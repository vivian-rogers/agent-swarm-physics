"""H48 settling times per goal period (the outcome), both embedding models.

  S1  kickoff remanence at active-hour resolution (primary tau_settle): kickoff excess over decoy kickoffs in 1-h bins,
      plateau fit (card Observables). Variants: S1_dq5 (templated / self_repeat_both removed), S1_chat (chat only),
      S1_room (per-room kickoff vectors).
  S2  H20's MQ kickoff transient tau_q recomputed from the shared white32 statements with h20lib (days -> hours).
  S3  H54's day-level tau_K (bge), imported read-only (days -> hours).
  S5  within-room pairwise-alignment relaxation (agent_win30 white32), plateau fit in active hours (descriptive).

  uv run python hypotheses/H48-settling-mixing-time/analysis/settling.py [--periods 38] [--workers 2]
Writes data/processed/H48-settling-mixing-time/settling_period.parquet and G<NN>/s1_series_<model>.parquet.
"""
from __future__ import annotations

import argparse
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h48lib as L  # noqa: E402
from h48lib import hc  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(hc.ROOT / "infra/shared"))
import embed_models as EM  # noqa: E402

MODELS = ["bge_small", "gte_modernbert"]
H54_EXCLUDE = {23}


@lru_cache(maxsize=1)
def goals() -> pl.DataFrame:
    return pl.read_parquet(hc.ED / "goals.parquet").with_columns(pl.col("kind").cast(pl.String))


@lru_cache(maxsize=2)
def goal_raw(model: str) -> np.ndarray:
    return np.load(hc.ED / f"goal_vectors{EM.MODELS[model]['vec_suffix']}.npy").astype(np.float32)


@lru_cache(maxsize=8)
def whitener(regime: str, model: str):
    return EM.load_whitener(regime, 32, model)


def gvec(g: int, regime: str, model: str, kind: str = "kickoff", room: int | None = None):
    q = goals().filter((pl.col("goal_no") == g) & (pl.col("kind") == kind))
    if room is not None:
        q = q.filter(pl.col("room") == room)
    if q.height == 0:
        return None
    return L.unit(whitener(regime, model)(goal_raw(model)[int(q["gid"][0])][None]))[0]


@lru_cache(maxsize=1)
def eligible_kickoffs() -> list[int]:
    q = goals().filter((pl.col("kind") == "kickoff") & ~pl.col("holdout"))
    return sorted(set(q["goal_no"].to_list()) - H54_EXCLUDE)


def decoys(g: int, regime: str, model: str) -> np.ndarray:
    return np.vstack([gvec(q, regime, model) for q in eligible_kickoffs() if q != g])


@lru_cache(maxsize=2)
def stmt_vectors(model: str) -> np.ndarray:
    return np.load(hc.ED / f"statements_white32_{EM.MODELS[model]['suffix']}.npy", mmap_mode="r")


@lru_cache(maxsize=1)
def flags() -> pl.DataFrame:
    return pl.read_parquet(hc.SH / "statement_flags.parquet", columns=["srow", "templated", "self_repeat_both"])


def h20_tau_q(st: pl.DataFrame, Z: np.ndarray, g: int) -> dict:
    """H20's estimator: agent-day means (n >= 8), C(d, d') ratio of sums, entries t_w >= 2, tau <= (T-1)//2, MQ fit."""
    H = L.h20lib()
    days = hc.period_days(g)
    dix = {d: k for k, d in enumerate(days["pt_date"].to_list())}
    wk = (days["gap_before_s"].to_numpy() > 36 * 3600)
    k_idx = np.array([dix[d] for d in st["pt_date"].to_list()])
    agents = sorted(set(st["agent"].to_list()))
    apos = {a: n for n, a in enumerate(agents)}
    a_idx = np.array([apos[a] for a in st["agent"].to_list()])
    T = int(k_idx.max()) + 1
    xbar, v, n, valid = H.agent_day_stats(Z, a_idx, k_idx, len(agents), T)
    C, npair = H.two_time(xbar, v, valid)
    E = H.entries(C, npair, wk[:T], tw_min=2, tau_max=H.tau_max_for(T))
    if len(E["c"]) < 6:
        return {"tau_q_days": np.nan, "b2": np.nan, "detected": False, "n_entries": len(E["c"])}
    p, wsse = H.fit_model("MQ", E)
    tq, b2 = float(np.exp(p[4])), float(np.exp(p[3]))
    lo, hi = np.exp(np.log(0.2)), np.exp(np.log(100))
    det = bool(b2 >= 0.1 and tq > lo * 1.05 and tq < min(hi * 0.95, T))
    lag1 = [float(C[k, k + 1]) for k in range(T - 1)]
    return {"tau_q_days": tq, "b2": b2, "kap": float(p[5]), "detected": det, "n_entries": int(len(E["c"])), "T": T,
            "lag1": lag1}


def s5_alignment(g: int, model: str, roster: pl.DataFrame, a_max: float) -> dict | None:
    aw = pl.read_parquet(hc.ED / "agent_win30.parquet").with_row_index("r")
    aw = aw.filter((pl.col("goal_no") == g) & (pl.col("agent") != hc.CLAUDE_CODE))
    days = hc.period_days(g)
    aw = aw.join(days.select("pt_date"), on="pt_date", how="semi")
    if aw.height == 0:
        return None
    V = np.load(hc.ED / f"agent_win30_white32_{EM.MODELS[model]['suffix']}.npy", mmap_mode="r")
    X = L.unit(np.asarray(V[aw["r"].to_numpy()], dtype=np.float64))
    m = {d: (ws, w, off) for d, ws, w, off in zip(days["pt_date"], days["win_start"], days["window_s"],
                                                   days["active_offset_s"])}
    t0 = hc.kickoff_t0(g)
    ws0, w0, off0 = m[days["pt_date"][0]]
    a0 = off0 + min(max((t0 - ws0).total_seconds(), 0.0), w0)
    a = np.array([(m[d][2] + min((k + 0.5) * 1800.0, m[d][1]) - a0) / 3600.0
                  for d, k in zip(aw["pt_date"].to_list(), aw["win30"].to_list())])
    room = dict(zip(roster["agent"].to_list(), roster["room0"].to_list()))
    rr = np.array([room.get(x, -1) if room.get(x) is not None else -1 for x in aw["agent"].to_list()])
    key = aw.select("pt_date", "win30").with_columns(pl.Series("rr", rr))
    t_, y_, w_ = [], [], []
    for pd_, k, r_, idx in key.with_row_index("i").group_by(["pt_date", "win30", "rr"]).agg(pl.col("i")).iter_rows():
        if r_ < 0:
            continue
        ix = np.asarray(idx)
        if len(ix) < 3 or not (0 <= a[ix[0]] <= a_max):
            continue
        G = X[ix] @ X[ix].T
        n = len(ix)
        t_.append(a[ix[0]]); y_.append((G.sum() - n) / (n * (n - 1))); w_.append(n * (n - 1) / 2)
    if len(t_) < 6:
        return None
    return L.exp_plateau_fit(np.array(t_), np.array(y_), np.array(w_))


def period_job(g: int) -> list[dict]:
    t_start = time.time()
    P = L.load_period(g)
    reg = P["meta"]["regime"]
    de = L.day_ends(g)
    a_max = float(de[min(hc.MAX_FIT_DAYS, len(de)) - 1])
    hpd = float(P["meta"]["hours_per_day"])
    st_all = P["stmts"].filter(~pl.col("pre_kick") & (pl.col("a") >= 0))
    srow = pl.read_parquet(hc.ED / "statements.parquet", columns=["pt_date"]).with_row_index("srow")
    st_all = st_all.join(srow, on="srow", how="left").join(flags(), on="srow", how="left")
    st = st_all.filter(pl.col("a") <= a_max)
    rows = []
    out = hc.OUT / f"G{g:02d}"
    out.mkdir(parents=True, exist_ok=True)
    for model in MODELS:
        Zall = stmt_vectors(model)
        k = gvec(g, reg, model)
        if k is None:
            rows.append(dict(goal_no=g, model=model, estimator="S1", note="no kickoff vector"))
            continue
        Dq = decoys(g, reg, model)
        Z = np.asarray(Zall[st["srow"].to_numpy()], dtype=np.float64)
        a = st["a"].to_numpy().astype(float)
        ag = st["agent"].to_numpy()
        variants = {"S1": np.ones(len(a), bool),
                    "S1_dq5": ~(st["templated"].fill_null(False).to_numpy() | st["self_repeat_both"].fill_null(False).to_numpy()),
                    "S1_chat": (st["kind"] == "chat").to_numpy()}
        for name, msk in variants.items():
            f, (mids, ex, na) = L.s1_fit(a[msk], ag[msk], Z[msk], k, Dq, a_max)
            if name == "S1":
                pl.DataFrame({"a": mids, "excess": ex, "n_agents": na}).write_parquet(out / f"s1_series_{model}.parquet")
            rows.append(dict(goal_no=g, model=model, estimator=name, **(_flat(f) if f else {"note": "too few bins"})))
        # per-room kickoff vectors (multi-room periods): agents' excess vs their own room's kickoff
        blocks = L.blocks_of(P["roster"])
        if len(blocks) >= 2:
            room0 = dict(zip(P["roster"]["agent"].to_list(), P["roster"]["room0"].to_list()))
            kr = {b: gvec(g, reg, model, "kickoff_room", b) for b in blocks}
            if all(v is not None for v in kr.values()):
                rows += _room_variant(g, model, a, ag, Z, kr, room0, Dq, a_max)
        # S2: H20's MQ on the whole period (as H20 ran it)
        Zw = np.asarray(Zall[st_all["srow"].to_numpy()], dtype=np.float64)
        try:
            s2 = h20_tau_q(st_all, Zw, g)
        except Exception as e:  # noqa: BLE001
            s2 = {"tau_q_days": np.nan, "detected": False, "note": str(e)[:80]}
        lag1 = s2.pop("lag1", None)
        rows.append(dict(goal_no=g, model=model, estimator="S2_H20", tau=s2["tau_q_days"] * hpd
                         if np.isfinite(s2.get("tau_q_days", np.nan)) else np.nan, detected=s2["detected"],
                         tau_days=s2.get("tau_q_days"), b2=s2.get("b2"), lag1=str([round(x, 3) for x in lag1])
                         if lag1 else None))
        f5 = s5_alignment(g, model, P["roster"], a_max)
        rows.append(dict(goal_no=g, model=model, estimator="S5_pair", **(_flat(f5) if f5 else {"note": "too few"})))
    # S3: H54 day-level tau_K (bge), read-only
    try:
        r54 = hc.load_json(hc.H54 / f"G{g:02d}" / "results.json")["remanence"]["kick"]
        rows.append(dict(goal_no=g, model="bge_small", estimator="S3_H54day", tau=r54["tau"] * hpd, tau_days=r54["tau"],
                         A_0=r54["A_1"], A_inf=r54["A_inf"], dbic=r54["bic_const"] - r54["bic_exp"],
                         detected=bool(r54["bic_const"] - r54["bic_exp"] >= 2 and r54["A_1"] > r54["A_inf"])))
    except Exception:
        pass
    # H20 published MQ (bge), read-only, for validation
    try:
        r20 = hc.load_json(hc.H20 / f"G{g:02d}" / "result_aniso.json")["fits"]["MQ"]["params"]
        rows.append(dict(goal_no=g, model="bge_small", estimator="S2_H20_published", tau_days=float(np.exp(r20[4])),
                         b2=float(np.exp(r20[3])), tau=float(np.exp(r20[4])) * hpd))
    except Exception:
        pass
    print(f"#{g}: done ({time.time() - t_start:.0f}s)", flush=True)
    return rows


def _flat(f: dict) -> dict:
    return {k: f[k] for k in ("tau", "A_0", "A_inf", "dbic", "detected", "n", "span", "at_top", "at_bottom")}


def _room_variant(g, model, a, ag, Z, kr, room0, Dq, a_max) -> list[dict]:
    """S1 with each agent scored against its own room's kickoff; decoys unchanged."""
    mids, bins = L.bin_vectors(a, ag, Z, 1.0, a_max, 2)
    ex, na = np.full(len(mids), np.nan), np.zeros(len(mids))
    for b, (ags, V) in enumerate(bins):
        keep = [n for n, x in enumerate(ags) if room0.get(int(x)) in kr]
        if len(keep) < 3:
            continue
        Kv = np.vstack([kr[room0[int(ags[n])]] for n in keep])
        ex[b] = float((V[keep] * Kv).sum(1).mean() - (V[keep] @ Dq.T).mean())
        na[b] = len(keep)
    f = L.exp_plateau_fit(mids, ex, na)
    return [dict(goal_no=g, model=model, estimator="S1_room", **(_flat(f) if f else {"note": "too few bins"}))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--periods", default=None)
    ap.add_argument("--workers", type=int, default=2)
    x = ap.parse_args()
    periods = [int(p) for p in x.periods.split(",")] if x.periods else hc.REPLICATION
    rows = []
    with ProcessPoolExecutor(max_workers=min(x.workers, 2)) as ex:
        for r in ex.map(period_job, sorted(periods, key=lambda g: -1 if g == 51 else g)):
            rows += r
    df = pl.DataFrame(rows, infer_schema_length=None)
    path = hc.OUT / "settling_period.parquet"
    if x.periods and path.exists():
        df = pl.concat([pl.read_parquet(path).filter(~pl.col("goal_no").is_in(periods)), df], how="diagonal_relaxed")
    df.sort("goal_no", "model", "estimator").write_parquet(path)
    pp = hc.OUT / "_provenance.json"
    prov = hc.load_json(pp)
    prov.setdefault("derived", {})["settling"] = {"built_by": "hypotheses/H48-settling-mixing-time/analysis/settling.py",
                                                  "git_commit": hc.common.git_commit(), "models": MODELS,
                                                  "inputs": ["shared/embeddings/statements_white32_*",
                                                             "shared/embeddings/goals + goal_vectors*",
                                                             "shared/embeddings/agent_win30_white32_*",
                                                             "shared/statement_flags", "H20 h20lib + G*/result_aniso.json (read-only)",
                                                             "H54 G*/results.json (read-only)"]}
    hc.save_json(pp, prov)


if __name__ == "__main__":
    main()
