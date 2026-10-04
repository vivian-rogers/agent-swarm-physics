"""H65 round 1: replication layer (every eligible period) and the four natives (G26, G35, G44, G12). The same
functions run on synthetic designs (analysis/synthetic.py).

    uv run python hypotheses/H65-leaders-are-routers/analysis/run.py replication [--model bge_small|gte_modernbert|style]
    uv run python hypotheses/H65-leaders-are-routers/analysis/run.py natives [--model ...]
Writes data/processed/H65-leaders-are-routers/{replication,natives}/<model>/*.json and per-agent parquet.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
           "POLARS_MAX_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from multiprocessing import Pool  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h65lib as L  # noqa: E402

UTC = dt.timezone.utc
MIN_AGENTS = 4
G26_TERM = (dt.datetime(2026, 1, 5, 19, 35, 22, 589746, tzinfo=UTC), dt.datetime(2026, 1, 9, 19, 0, 43, 77738, tzinfo=UTC))
G44_START = dt.datetime(2026, 5, 26, 19, 15, 47, 698593, tzinfo=UTC)
G44_BEST_ROOM = 2
ROOMS35 = {"rest": 3, "best": 2}


# ------------------------------------------------------------------------------------------------ helpers
def gt() -> pl.DataFrame:
    return pl.read_parquet(L.SH / "ground_truth_labels.parquet").filter(pl.col("preferred") & ~pl.col("holdout"))


def g12_windows() -> pl.DataFrame:
    g = gt().filter(pl.col("goal_no") == 12)
    ph = g.filter(pl.col("label_kind") == "phase").group_by("unit").agg(pl.col("t_valid_from").min().alias("a"),
                                                                        pl.col("t_valid_to").max().alias("b"))
    return ph.sort("a")


def load_period(goal: int, model: str, unit: str | None = None, g12_blocks: bool = False):
    d = L.DATA / f"G{goal:02d}"
    tg = pl.read_parquet(d / "targets.parquet").filter(pl.col("t_call").is_not_null())
    rd = pl.read_parquet(d / "reads.parquet")
    if unit is not None:
        tg = tg.filter(pl.col("unit_id") == unit)
        rd = rd.join(tg.select("tgt"), on="tgt", how="semi")
    Zs, pos, Hm, hpos, regime = L.load_vectors(goal, model, tg, rd)
    block = None
    if g12_blocks:
        w = g12_windows()
        t = tg.sort("tgt")["t"]
        tt = t.dt.epoch("us").to_numpy() / 1e6
        room = tg.sort("tgt")["room"].to_numpy().astype(np.int64)
        block = room * 10_000_000 + (tt // L.BLOCK_S).astype(np.int64)
        for k, (u, a, b) in enumerate(w.iter_rows()):
            m = (t >= a) & (t < b)
            block[m.to_numpy()] = 9_000_000_000 + k
    return tg, rd, Zs, pos, Hm, hpos, regime, block


def sp(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < 4 or np.std(a[m]) == 0 or np.std(b[m]) == 0:
        return np.nan
    return float(spearmanr(a[m], b[m]).statistic)


def partial_sp(x, y, z):
    """Spearman partial correlation of x and y given z (ranks, linear residuals)."""
    from scipy.stats import rankdata
    x, y, z = (np.asarray(v, float) for v in (x, y, z))
    m = np.isfinite(x) & np.isfinite(y) & np.isfinite(z)
    if m.sum() < 5:
        return np.nan
    rx, ry, rz = (rankdata(v[m]) for v in (x, y, z))
    A = np.c_[np.ones(m.sum()), rz]
    ex = rx - A @ np.linalg.lstsq(A, rx, rcond=None)[0]
    ey = ry - A @ np.linalg.lstsq(A, ry, rcond=None)[0]
    if ex.std() == 0 or ey.std() == 0:
        return np.nan
    return float(np.corrcoef(ex, ey)[0, 1])


def period_stats(E: pl.DataFrame, min_n: int = 30) -> dict:
    e = E.filter(pl.col("n") >= min_n)
    chi, kap, ro, ri, n = (e[c].to_numpy() for c in ("chi", "kappa", "RO", "RI", "n"))
    ln = np.log(n)
    d1 = partial_sp(ri, chi, ln)
    d2 = partial_sp(ri, kap, ln)
    lam = e["lam"].to_numpy()
    ratio = lam / chi
    ok = np.isfinite(ratio) & (chi > 0)
    return {"n_agents": int(e.height), "rho_RO_chi": sp(ro, chi), "pr_RI_chi": d1, "pr_RI_kappa": d2,
            "D": (d1 - d2) if np.isfinite(d1) and np.isfinite(d2) else np.nan, "rho_chi_kappa": sp(chi, kap),
            "lam_over_chi_median": float(np.median(ratio[ok])) if ok.any() else np.nan,
            "chi_median": float(np.nanmedian(chi)) if len(chi) else np.nan,
            "kappa_median": float(np.nanmedian(kap)) if len(kap) else np.nan,
            "chi_pos_share": float(np.mean(chi[np.isfinite(chi)] > 0)) if np.isfinite(chi).any() else np.nan}


# ------------------------------------------------------------------------------------------------ replication
def eligible_units() -> list:
    out = []
    pa = pl.read_parquet(L.SH / "period_affordances.parquet").filter(~pl.col("holdout"))
    for g in sorted(set(pa["goal_no"].to_list())):
        p = L.DATA / f"G{g:02d}/targets.parquet"
        if not p.exists():
            continue
        tg = pl.read_parquet(p).filter(pl.col("t_call").is_not_null())
        if g == 51:
            for u in sorted(tg["unit_id"].unique().to_list()):
                c = tg.filter(pl.col("unit_id") == u).group_by("agent").len()
                if (c["len"] >= 30).sum() >= MIN_AGENTS:
                    out.append((g, u))
        else:
            c = tg.group_by("agent").len()
            if (c["len"] >= 30).sum() >= MIN_AGENTS:
                out.append((g, None))
    return out


def h32_inout(goal: int) -> dict:
    p = L.ROOT / f"data/processed/H32-information-current-leaders/r1b/bge/G{goal:02d}/result.json"
    if not p.exists():
        return {}
    r = json.loads(p.read_text())
    return {int(a): (o, o - n) for a, o, n in zip(r["nodes"], r["out"], r["net"])}


def replication_job(args):
    goal, unit, model, B = args
    t0 = time.time()
    tg, rd, Zs, pos, Hm, hpos, regime, block = load_period(goal, model, unit)
    D = L.build_design(tg, rd, Zs, pos, Hm, hpos)
    Gr = L.build_grams(D)
    w = np.ones(len(Gr.blocks))
    E = L.estimate(Gr, w)
    st = period_stats(E)
    boots = L.bootstrap(Gr, w, B=B, rng=np.random.default_rng(goal))
    bs = [period_stats(b) for b in boots]
    for k in ("D", "rho_RO_chi", "rho_chi_kappa", "pr_RI_chi", "pr_RI_kappa"):
        v = np.array([b[k] for b in bs], float)
        v = v[np.isfinite(v)]
        st[k + "_ci"] = [float(np.quantile(v, 0.025)), float(np.quantile(v, 0.975))] if len(v) > 20 else [None, None]
    # per-agent bootstrap SEs
    for c in ("chi", "kappa"):
        M = np.stack([b.sort("agent")[c].to_numpy() for b in boots])
        E = E.sort("agent").with_columns(pl.Series(c + "_se", np.nanstd(M, 0)))
    if model == "bge_small" and unit is None:
        h = h32_inout(goal)
        if h:
            a = E.filter(pl.col("n") >= 30)
            o32 = np.array([h.get(int(x), (np.nan, np.nan))[0] for x in a["agent"]], float)
            i32 = np.array([h.get(int(x), (np.nan, np.nan))[1] for x in a["agent"]], float)
            st["rho_kappa_H32out"] = sp(a["kappa"].to_numpy(), o32)
            st["rho_chi_H32in"] = sp(a["chi"].to_numpy(), i32)
    st.update({"goal": goal, "unit": unit or f"{goal}", "model": model, "regime": regime, "n_blocks": len(Gr.blocks),
               "n_targets": int(tg.height), "runtime_s": time.time() - t0})
    E = E.with_columns(pl.lit(goal).alias("goal"), pl.lit(unit or f"{goal}").alias("unit"))
    return st, E


def replication(model: str, workers: int = 4, B: int = 100):
    units = eligible_units()
    jobs = [(g, u, model, B) for g, u in units]
    jobs.sort(key=lambda j: -(j[0] == 51))
    out = L.DATA / "replication" / model
    out.mkdir(parents=True, exist_ok=True)
    with Pool(workers) as p:
        res = p.map(replication_job, jobs, chunksize=1)
    stats = [r[0] for r in res]
    pl.concat([r[1] for r in res], how="diagonal").write_parquet(out / "agents.parquet", compression="zstd")
    (out / "periods.json").write_text(json.dumps(stats, indent=1, default=float))
    print(f"{model}: {len(stats)} units")


# ------------------------------------------------------------------------------------------------ natives
def window_weights(Gr, t0=None, t1=None, room=None):
    m = np.ones(len(Gr.blocks), bool)
    tt = Gr.bmeta["t0"].to_numpy()
    if t0 is not None:
        m &= tt >= t0.timestamp()
    if t1 is not None:
        m &= tt < t1.timestamp()
    if room is not None:
        m &= Gr.bmeta["room"].to_numpy() == room
    return m.astype(float)


def leader_pct(Gr, w, leader, B=100, rng=None, min_n=30, min_exp=30):
    E = L.estimate(Gr, w, min_n=min_n, min_exp=min_exp).sort("agent")
    ag = E["agent"].to_numpy()

    def calls(E):
        out = {}
        for c in ("chi", "kappa", "BO", "RI", "RO"):
            v = E[c].to_numpy()
            p = L.pct(np.where(E["n"].to_numpy() >= min_n, v, np.nan))
            k = np.flatnonzero(E["agent"].to_numpy() == leader)
            out["pct_" + c] = float(p[k[0]]) if len(k) else np.nan
        out["router_index"] = out["pct_chi"] - out["pct_kappa"]
        out["router_call"] = bool(out["pct_chi"] >= 0.6 and out["pct_kappa"] <= 0.5)
        return out
    point = calls(E)
    boots = L.bootstrap(Gr, w, B=B, rng=rng or np.random.default_rng(5), min_n=min_n, min_exp=min_exp)
    bc = [calls(b.sort("agent")) for b in boots]
    for k in ("pct_chi", "pct_kappa", "router_index"):
        v = np.array([b[k] for b in bc], float)
        v = v[np.isfinite(v)]
        point[k + "_ci"] = [float(np.quantile(v, 0.025)), float(np.quantile(v, 0.975))] if len(v) > 20 else [None, None]
    point["router_call_boot_share"] = float(np.mean([b["router_call"] for b in bc]))
    point["n_agents"] = int((E["n"].to_numpy() >= min_n).sum())
    point["leader_n"] = float(E.filter(pl.col("agent") == leader)["n"][0]) if leader in ag else 0.0
    point["agents"] = E.to_dicts()
    return point


def fe_contrast(df: pl.DataFrame, metric: str, role: str, unit_col: str, R: int = 5000, rng=None):
    """metric ~ agent FE + unit FE + beta * role; permutation of the role label among each unit's agents."""
    d = df.filter(pl.col(metric).is_finite())
    multi = d.group_by("agent").len().filter(pl.col("len") >= 2)["agent"]
    d = d.filter(pl.col("agent").is_in(multi))
    if d.height < 6 or d[role].sum() == 0:
        return {"beta": np.nan, "p_greater": np.nan, "p_less": np.nan, "n": d.height}
    y = d[metric].to_numpy()
    a = d["agent"].to_numpy()
    u = d[unit_col].to_numpy()
    rl = d[role].to_numpy().astype(float)

    def dm(codes):
        uu, inv = np.unique(codes, return_inverse=True)
        M = np.zeros((len(codes), max(len(uu) - 1, 0)))
        if len(uu) > 1:
            M[np.flatnonzero(inv > 0), inv[inv > 0] - 1] = 1
        return M
    X0 = np.hstack([np.ones((len(y), 1)), dm(a), dm(u)])

    def beta(r):
        X = np.hstack([X0, r[:, None]])
        return float(np.linalg.lstsq(X, y, rcond=None)[0][-1])
    b = beta(rl)
    rng = rng or np.random.default_rng(11)
    groups = [np.flatnonzero(u == k) for k in np.unique(u)]
    null = np.empty(R)
    for k in range(R):
        rp = rl.copy()
        for g in groups:
            rp[g] = rng.permutation(rl[g])
        null[k] = beta(rp)
    return {"beta": b, "p_greater": float((1 + (null >= b).sum()) / (R + 1)),
            "p_less": float((1 + (null <= b).sum()) / (R + 1)), "n": int(d.height), "n_role": int(rl.sum())}


def per_window(Gr, windows: list, min_n=10, min_exp=10) -> pl.DataFrame:
    """windows: list of (key dict, weight vector). Returns per-agent rows with the key columns."""
    rows = []
    for key, w in windows:
        if w.sum() == 0:
            continue
        E = L.estimate(Gr, w, min_n=min_n, min_exp=min_exp).filter(pl.col("n") >= min_n)
        for r in E.to_dicts():
            rows.append({**key, **r})
    return pl.DataFrame(rows)


def calibrate(name: str, r: dict) -> dict:
    """Amendment A1: router call against the skeleton null (synthetic null replicates of this native)."""
    fs = [L.DATA / "synthetic/natives_reps.parquet", L.DATA / "synthetic/null_extra_reps.parquet"]
    fs = [f for f in fs if f.exists()]
    if not fs:
        return r
    nl = pl.concat([pl.read_parquet(f).filter((pl.col("native") == name) & (pl.col("scen") == "null"))
                    .select("router_index", "pct_chi", "pct_kappa") for f in fs])
    ri = nl["router_index"].drop_nans().drop_nulls().to_numpy()
    r["null_n"] = int(len(ri))
    r["null_ri_q90"] = float(np.quantile(ri, 0.9))
    r["null_mean_pct_chi"] = float(nl["pct_chi"].mean())
    r["null_mean_pct_kappa"] = float(nl["pct_kappa"].mean())
    r["p_syn"] = float((1 + (ri >= r["router_index"]).sum()) / (len(ri) + 1)) if np.isfinite(r["router_index"]) else np.nan
    r["router_call_raw"] = r["router_call"]
    r["router_call"] = bool(np.isfinite(r["p_syn"]) and r["p_syn"] < 0.10 and r["pct_kappa"] <= 0.5)
    return r


def native_g26(Gr, B=100, rng=None, calibrated=False):
    w = window_weights(Gr, *G26_TERM)
    r = leader_pct(Gr, w, 17, B=B, rng=rng)
    return calibrate("G26", r) if calibrated else r


def native_g44(Gr, B=100, rng=None, calibrated=False):
    # pre-data amendment (card, 2026-10-04 ~20:10 UTC): thresholds 15/15 for this native (leader has 27 statements)
    w = window_weights(Gr, G44_START, None, G44_BEST_ROOM)
    r = leader_pct(Gr, w, 28, B=B, rng=rng, min_n=15, min_exp=15)
    return calibrate("G44", r) if calibrated else r


def native_g35(Gr, R=5000, rng=None):
    lead = gt().filter((pl.col("goal_no") == 35) & (pl.col("label_kind") == "leader"))
    L35 = {}
    for u, a, det in lead.select("unit", "agent", "detail").iter_rows():
        room = ROOMS35["rest" if "room=rest" in det else "best"]
        L35[(u.replace("day_", ""), room)] = a
    windows = []
    days = sorted(set(Gr.bmeta["day"].to_list()))
    for d in days:
        for room in (2, 3):
            w = ((Gr.bmeta["day"].to_numpy() == d) & (Gr.bmeta["room"].to_numpy() == room)).astype(float)
            windows.append(({"day": d, "room": room, "rd": f"{d}|{room}"}, w))
    df = per_window(Gr, windows)
    if df.height == 0:
        return {"note": "no estimable agent-room-days"}
    df = df.with_columns(leader=pl.struct("day", "room", "agent").map_elements(
        lambda s: int(L35.get((s["day"], s["room"])) == s["agent"]), return_dtype=pl.Int8))
    out = {"n_rows": df.height, "n_leader_rows": int(df["leader"].sum()),
           "leader_rows": df.filter(pl.col("leader") == 1).select("rd", "agent", "n").to_dicts()}
    for m in ("chi", "kappa", "RO", "BO", "RI"):
        out[m] = fe_contrast(df, m, "leader", "rd", R=R, rng=rng)
    out["router_call"] = bool(np.isfinite(out["chi"]["beta"]) and out["chi"]["beta"] > 0
                              and (not np.isfinite(out["kappa"]["beta"]) or out["kappa"]["beta"] <= 0)
                              and out["chi"]["p_greater"] < 0.10)
    out["table"] = df.to_dicts()
    return out


def native_g12(Gr, R=5000, rng=None):
    g = gt().filter(pl.col("goal_no") == 12)
    judge = dict(g.filter(pl.col("label_kind") == "judge").select("unit", "agent").iter_rows())
    teams = g.filter(pl.col("label_kind") == "team").group_by("unit").agg(pl.col("agent"))
    part = {u: set(a) | {judge[u]} for u, a in teams.iter_rows()}
    w12 = g12_windows()
    windows = []
    blocks = Gr.blocks
    for k, (u, a, b) in enumerate(w12.iter_rows()):
        w = (blocks == 9_000_000_000 + k).astype(float)
        windows.append(({"debate": u}, w))
    df = per_window(Gr, windows, min_n=5, min_exp=5)
    if df.height == 0:
        return {"note": "no estimable agent-debates"}
    df = df.filter(pl.struct("debate", "agent").map_elements(lambda s: s["agent"] in part[s["debate"]],
                                                             return_dtype=pl.Boolean))
    df = df.with_columns(judge=pl.struct("debate", "agent").map_elements(
        lambda s: int(judge[s["debate"]] == s["agent"]), return_dtype=pl.Int8))
    out = {"n_rows": df.height, "n_judge_rows": int(df["judge"].sum())}
    for m in ("chi", "kappa", "RO", "BO", "RI"):
        out[m] = fe_contrast(df, m, "judge", "debate", R=R, rng=rng)
    out["router_call"] = bool(np.isfinite(out["chi"]["beta"]) and out["chi"]["beta"] > 0
                              and (not np.isfinite(out["kappa"]["beta"]) or out["kappa"]["beta"] <= 0)
                              and out["chi"]["p_greater"] < 0.10)
    out["table"] = df.to_dicts()
    return out


def native_job(args):
    name, model = args
    goal = int(name[1:])
    tg, rd, Zs, pos, Hm, hpos, regime, block = load_period(goal, model, g12_blocks=(name == "G12"))
    D = L.build_design(tg, rd, Zs, pos, Hm, hpos, block=block)
    Gr = L.build_grams(D)
    if name in ("G26", "G44"):
        f = native_g26 if name == "G26" else native_g44
        return name, f(Gr, calibrated=True)
    f = {"G35": native_g35, "G12": native_g12}[name]
    return name, f(Gr)


def natives(model: str, workers: int = 2):
    out = L.DATA / "natives" / model
    out.mkdir(parents=True, exist_ok=True)
    with Pool(workers) as p:
        res = p.map(native_job, [(n, model) for n in ("G35", "G12", "G26", "G44")], chunksize=1)
    for name, r in res:
        (out / f"{name}.json").write_text(json.dumps(r, indent=1, default=float))
        print(name, {k: v for k, v in r.items() if k not in ("agents", "table", "leader_rows")})


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["replication", "natives"])
    ap.add_argument("--model", default="bge_small")
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    if a.what == "replication":
        replication(a.model, a.workers)
    else:
        natives(a.model, a.workers)
