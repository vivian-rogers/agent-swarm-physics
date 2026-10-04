"""H38 pipeline, one goal period at a time (non-holdout only; asserts it).

O1 prevalence      JS share (day-present population) vs the per-block Poisson-binomial independent expectation;
                   village-off gaps (outages.parquet)
O2 causes          shares of JS minutes by primary cause; explained share (half rule, strict) vs its N1 surrogate level
O3 marker check    odds ratio of JS at t given an infra burst in [t-10, t-1] (>= 2 agents with infrastructure-error
                   turns); null = burst series circularly shifted within (day, 30-min block)
O4 gains           Curie-Weiss g (H02/H19 estimator, chunks and present population as H19) for every stall variant,
                   active and talk spins, vs joint N1 surrogates; per-cause drops; O6 consistency formula
O5 lambda_1        H12 units inside the period: top eigenvalue raw / lull / stall / mask_scaffold vs joint cross-day
                   surrogate edges (95% quantile)
Output: data/processed/H38-platform-stalls/G<NN>/result.json

Round 1b (2026-10-04): --data-version fixed reads DQ8's activity_bins_fixed and the shared outages_fixed sidecar and
writes to data/processed/H38-platform-stalls/r1b/G<NN>/result.json (round-1 outputs untouched). Both versions also
report the DQ8-calibrated variants (O4 `trim*`: rows outside the all-present window removed before block-shift
surrogates; O5 `trim_bs`: lambda_1 on trimmed rows vs a block-shift edge).

Usage: uv run python hypotheses/H38-platform-stalls/analysis/run_period.py --period G38 [--n-surr 200] [--data-version fixed]
       uv run python hypotheses/H38-platform-stalls/analysis/run_period.py --all [--workers 2] [--data-version fixed]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

sys.dont_write_bytecode = True
if "--data-version" in sys.argv:  # must be set before h38lib is imported (and inherited by spawned workers)
    os.environ["H38_DATA_VERSION"] = sys.argv[sys.argv.index("--data-version") + 1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import h38lib as L  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

CHUNK_DAYS, MIN_TAIL_DAYS, MIN_ACTIVE_BINS = 5, 3, 30  # H02 / H19 rules
VARS = ["raw", "lull", "stall", "stall_strict", "field", "exo", "mask_edge", "mask_infra", "mask_scaffold", "mask_all"] + \
       [f"drop_{c}" for c in L.CAUSES]
ALLV = VARS + L.TRIM_VARS
INFRA = ["timeout", "vm", "resource", "network"]


def nonholdout_days(g: int) -> list[str]:
    cal = pl.read_parquet(L.SH / "calendar.parquet")
    d = cal.filter((pl.col("goal_no") == g) & ~pl.col("holdout")).sort("pt_date")
    days = d["pt_date"].to_list()
    assert not any(L.h12.holdout_mask(days, [g] * len(days))), "holdout day in exploratory selection"
    assert not cal.filter(pl.col("pt_date").is_in(days))["holdout"].any()
    return days


def chunks_of(days):
    ch = [days[i:i + CHUNK_DAYS] for i in range(0, len(days), CHUNK_DAYS)]
    if len(ch) > 1 and len(ch[-1]) < MIN_TAIL_DAYS:
        ch = ch[:-1]
    return ch


def load(days):
    ab = (pl.scan_parquet(L.AB).filter(pl.col("pt_date").is_in(days))
          .select("pt_date", pl.col("minute").cast(pl.Int32), "agent", "state").collect())
    rs = pl.scan_parquet(L.STALLS / "reasons.parquet").filter(pl.col("pt_date").is_in(days)).collect()
    sm = pl.scan_parquet(L.STALLS / "stall_minutes.parquet").filter(pl.col("pt_date").is_in(days)).collect()
    ab = ab.join(rs, on=["pt_date", "minute", "agent"], how="left").with_columns(pl.col("reason").fill_null(0))
    return ab, sm


def matrices(ab: pl.DataFrame, sm: pl.DataFrame, days: list[str], agents: list[int]):
    """Dense (T, N) spins (active), talk spins, reasons; plus day index, minute, scheduled flag, in (day, minute) order."""
    d = ab.filter(pl.col("pt_date").is_in(days) & pl.col("agent").is_in(agents))
    dmap = {x: i for i, x in enumerate(days)}
    d = d.with_columns(pl.col("pt_date").replace_strict(dmap, return_dtype=pl.Int16).alias("day"))
    piv = lambda col: (d.pivot(on="agent", index=["day", "minute"], values=col).sort("day", "minute"))
    st = piv("state")
    cols = [str(a) for a in agents]
    state = st.select(cols).to_numpy()
    state = np.nan_to_num(state.astype(float), nan=1).astype(np.int8)
    rr = piv("reason").select(cols).to_numpy()
    rr = np.nan_to_num(rr.astype(float), nan=0).astype(np.int8)
    day = st["day"].to_numpy(); minute = st["minute"].to_numpy()
    S = np.where(state >= 3, 1, -1).astype(np.int8)
    Tk = np.where(state == 4, 1, -1).astype(np.int8)
    R = np.where(S > 0, 0, rr).astype(np.int8)
    sch = (sm.filter(pl.col("pt_date").is_in(days)).with_columns(pl.col("pt_date").replace_strict(dmap, return_dtype=pl.Int16).alias("day"))
           .select("day", "minute", "scheduled"))
    key = pl.DataFrame({"day": day.astype(np.int16), "minute": minute.astype(np.int32)})
    sched = key.join(sch, on=["day", "minute"], how="left")["scheduled"].fill_null(False).to_numpy()
    return S, Tk, R, day, minute, sched


# ------------------------------------------------------------------------------------------------ O4
def o4_gains(ab, sm, days, rng, n_surr):
    obs = {v: [] for v in ALLV}; obs_t = {v: [] for v in ALLV}
    nul = {v: [[] for _ in range(n_surr)] for v in ALLV}; nul_t = {v: [[] for _ in range(n_surr)] for v in ALLV}
    o6n = o6d = 0.0
    chunks = []
    for k, ch in enumerate(chunks_of(days)):
        d = ab.filter(pl.col("pt_date").is_in(ch))
        pres = (d.group_by("agent").agg(pl.col("pt_date").n_unique().alias("nd"), (pl.col("state") >= 3).sum().alias("nact"),
                                        (pl.col("state") == 4).sum().alias("ntalk"))
                .filter((pl.col("nd") == len(ch)) & (pl.col("nact") >= MIN_ACTIVE_BINS)).sort("agent"))
        if pres.height < 3:
            continue
        agents = pres["agent"].to_list()
        talk_ok = np.array([n >= MIN_ACTIVE_BINS for n in pres["ntalk"].to_list()])
        S, Tk, R, day, minute, sched = matrices(ab, sm, ch, agents)
        bid, segs = L.block_segments(day, minute)
        use_talk = talk_ok.sum() >= 3
        res, f = L.gains(S, R, sched, bid, talk=Tk[:, talk_ok] if use_talk else None, talk_cols=talk_ok)
        for v in VARS:
            obs[v].append(res[v][0])
            if use_talk:
                obs_t[v].append(res[v][1])
        o6 = L.o6_predict(S, bid, f["explained"])
        o6n += o6["num"]; o6d += o6["den"]
        for s in range(n_surr):
            Sx, Rx, Tx = L.joint_shift([S, R, Tk], segs, rng)
            rx, _ = L.gains(Sx, Rx, sched, bid, talk=Tx[:, talk_ok] if use_talk else None, talk_cols=talk_ok)
            for v in VARS:
                nul[v][s].append(rx[v][0])
                if use_talk:
                    nul_t[v][s].append(rx[v][1])
        # round 1b: DQ8 design (rows removed before block-shift surrogates)
        tob, tnu = L.trim_gains(S, R, sched, day, minute, f["explained"], rng, n_surr,
                                talk=Tk if use_talk else None, talk_cols=talk_ok if use_talk else None)
        for v in L.TRIM_VARS:
            if v in tob and len(tnu[v]) == n_surr:
                obs[v].append(tob[v][0])
                if use_talk:
                    obs_t[v].append(tob[v][1])
                for s in range(n_surr):
                    nul[v][s].append(tnu[v][s][0])
                    if use_talk:
                        nul_t[v][s].append(tnu[v][s][1])
        chunks.append({"chunk": f"c{k}", "days": len(ch), "N": len(agents), "N_talk": int(talk_ok.sum()),
                       "js_share": float(f["js"].mean()), "stall_share": float(f["explained"].mean()),
                       "trim_share": float(L.trim_mask(R).mean()),
                       "g_raw_chunk": L.cw(res["raw"][0])["g"], "bJ0_raw_chunk": L.cw(res["raw"][0])["bJ0"]})
    if not chunks:
        return None
    for ci, c in enumerate(chunks):  # chunk-level z (H02's 21 chunks are scored on these)
        for v in ("raw", "lull", "stall", "field", "mask_scaffold", "mask_all", "trim", "trim_stall", "trim_scaffold"):
            if len(obs[v]) != len(chunks):
                continue
            go = L.cw(obs[v][ci])["g"]
            gn = np.array([L.cw(nul[v][s][ci])["g"] for s in range(n_surr)])
            gn = gn[np.isfinite(gn)]
            c[f"g_{v}"] = go
            c[f"E_{v}"] = go - gn.mean() if gn.size else np.nan
            c[f"z_{v}"] = (go - gn.mean()) / gn.std() if gn.size and gn.std() > 0 else np.nan

    def summarize(o, n):
        out = {}
        for v in ALLV:
            if not o[v] or any(len(n[v][s]) != len(o[v]) for s in range(n_surr)):
                continue
            go = L.cw(np.vstack(o[v]))
            gn = np.array([L.cw(np.vstack(n[v][s]))["g"] for s in range(n_surr)])
            gn = gn[np.isfinite(gn)]
            mu, sd = (float(gn.mean()), float(gn.std())) if gn.size else (np.nan, np.nan)
            out[v] = {"g": go["g"], "bJ0": go["bJ0"], "q": go["q"], "VR": go["VR"], "n_min": go["n"], "null_mean": mu,
                      "null_sd": sd, "E": go["g"] - mu, "z": (go["g"] - mu) / sd if sd and sd > 0 else np.nan}
        return out
    A = summarize(obs, nul)
    Tt = summarize(obs_t, nul_t) if any(obs_t[v] for v in ALLV) else {}
    o6g = 1 - o6d / o6n if o6n > 0 else np.nan
    return {"active": A, "talk": Tt, "chunks": chunks, "o6_g_pred": o6g}


# ------------------------------------------------------------------------------------------------ O1-O3 (day-present)
def poisson_binomial_le1(p: np.ndarray) -> float:
    P0 = np.prod(1 - p)
    P1 = sum(p[i] * np.prod(np.delete(1 - p, i)) for i in range(len(p)))
    return float(P0 + P1)


def o123(ab, sm, days, rng, n_surr):
    te = pl.read_parquet(L.DATA / "turn_errors.parquet").filter(pl.col("err_cat").cast(pl.String).is_in(INFRA))  # = shared turn_errors
    cal = pl.read_parquet(L.SH / "calendar.parquet").filter(pl.col("pt_date").is_in(days)).select("pt_date", "win_start")
    tem = (te.with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).alias("pt_date"))
           .join(cal, on="pt_date").with_columns(((pl.col("t") - pl.col("win_start")).dt.total_seconds() // 60).cast(pl.Int32).alias("m")))
    exp_js = []; obs_js = []; js_all = []; burst_all = []; blk_all = []
    expl_obs = []; expl_obs_s = []; n_js = 0
    sur_expl = np.zeros(n_surr); sur_js = np.zeros(n_surr)
    for di, d in enumerate(days):
        a = ab.filter(pl.col("pt_date") == d)
        pres = a.filter(pl.col("state") >= 3)["agent"].unique().sort().to_list()
        if len(pres) < 3:
            continue
        S, Tk, R, day, minute, sched = matrices(ab, sm, [d], pres)
        bid, segs = L.block_segments(day, minute)
        f = L.stall_flags(S, R, sched); fs = L.stall_flags(S, R, sched, strict=True)
        js_all.append(f["js"]); n_js += int(f["js"].sum())
        expl_obs.append(f["explained"]); expl_obs_s.append(fs["explained"])
        # independent expectation per block
        X = (S > 0).astype(float)
        for b in np.unique(bid):
            m = bid == b
            p = X[m].mean(0)
            exp_js.append((m.sum(), poisson_binomial_le1(p)))
        # bursts in [t-10, t-1] among day-present agents
        e = tem.filter((pl.col("pt_date") == d) & pl.col("agent").is_in(pres))
        cnt = np.zeros(len(minute), dtype=np.int16)
        if e.height:
            em = e.select("m", "agent").unique()
            per_min = {}
            for m_, ag in em.iter_rows():
                for t in range(m_ + 1, m_ + 11):
                    per_min.setdefault(t, set()).add(ag)
            idx = {int(mm): i for i, mm in enumerate(minute)}
            for t, ags in per_min.items():
                if t in idx:
                    cnt[idx[t]] = len(ags)
        burst_all.append(cnt >= 2); blk_all.append(bid + di * 10000)
        for s in range(n_surr):
            Sx, Rx = L.joint_shift([S, R], segs, rng)
            fx = L.stall_flags(Sx, Rx, sched)
            sur_expl[s] += fx["explained"].sum(); sur_js[s] += fx["js"].sum()
    if not js_all:
        return None
    js = np.concatenate(js_all); ex = np.concatenate(expl_obs); exs = np.concatenate(expl_obs_s)
    w = np.array([x[0] for x in exp_js]); pe = np.array([x[1] for x in exp_js])
    out = {"js_share": float(js.mean()), "js_expected_indep": float((w * pe).sum() / w.sum()),
           "n_js_min": int(js.sum()), "n_min": int(len(js)),
           "explained_share": float(ex.sum() / max(js.sum(), 1)), "explained_share_strict": float(exs.sum() / max(js.sum(), 1)),
           "explained_share_surr": float(np.mean(sur_expl / np.maximum(sur_js, 1))),
           "explained_share_surr_q95": float(np.quantile(sur_expl / np.maximum(sur_js, 1), 0.95)),
           "js_share_surr": float(np.mean(sur_js) / len(js))}
    burst = np.concatenate(burst_all); blk = np.concatenate(blk_all)

    def odds(jj, bb):
        a_ = (jj & bb).sum() + 0.5; b_ = (~jj & bb).sum() + 0.5; c_ = (jj & ~bb).sum() + 0.5; d_ = (~jj & ~bb).sum() + 0.5
        return float(np.log(a_ * d_ / (b_ * c_)))
    out["n_burst_min"] = int(burst.sum())
    if burst.sum() >= 1:
        lor = odds(js, burst)
        order = np.argsort(blk, kind="stable"); cuts = np.flatnonzero(np.diff(blk[order])) + 1
        segs = np.split(order, cuts)
        nullv = []
        for _ in range(500):
            bx = np.empty_like(burst)
            for idx in segs:
                Lg = idx.size
                bx[idx] = np.roll(burst[idx], rng.integers(0, Lg)) if Lg > 1 else burst[idx]
            nullv.append(odds(js, bx))
        nullv = np.array(nullv)
        out.update({"burst_logOR": lor, "burst_logOR_null_mean": float(nullv.mean()),
                    "burst_p_greater": float((1 + (nullv >= lor).sum()) / (len(nullv) + 1)),
                    "burst_p_less": float((1 + (nullv <= lor).sum()) / (len(nullv) + 1))})
    # cause shares (day-present, from the shared table)
    s = sm.filter(pl.col("js"))
    tot = max(s.height, 1)
    out["cause_shares"] = {c: float((s["cause"] == c).sum() / tot) for c in L.CAUSES}
    o = pl.read_parquet(L.STALLS / "outages.parquet").filter(pl.col("pt_date").is_in(days))
    off = o.filter(pl.col("village_off"))
    out["village_off"] = {"n": off.height, "minutes": int(off["k0_longest"].sum()) if off.height else 0,
                          "share_scheduled_minutes": float((off["frac_scheduled"] * off["dur_min"]).sum() / off["dur_min"].sum()) if off.height else None,
                          "causes": off["cause"].to_list()}
    out["n_outages"] = o.height
    out["outage_dur_median"] = float(o["dur_min"].median()) if o.height else None
    return out


# ------------------------------------------------------------------------------------------------ O5
def o5_lambda(ab, sm, days, g, rng, n_surr):
    units = {}
    for d in days:
        units.setdefault(L.h12.unit_of(g, d), []).append(d)
    out = {}
    for u, ud in units.items():
        if len(ud) < 2:
            continue
        a = ab.filter(pl.col("pt_date").is_in(ud))
        pres = (a.group_by("agent").agg(pl.col("pt_date").n_unique().alias("nd"), (pl.col("state") >= 3).sum().alias("nact"))
                .filter((pl.col("nd") == len(ud)) & (pl.col("nact") >= MIN_ACTIVE_BINS)).sort("agent"))
        if pres.height < 3:
            continue
        agents = pres["agent"].to_list()
        Sd, Rd, Bd, Cd = [], [], [], []
        for d in ud:
            S, Tk, R, day, minute, sched = matrices(ab, sm, [d], agents)
            Sd.append(S.T); Rd.append(R.T); Cd.append(sched)
            Bd.append(L.h02.block_ids(day, minute))
        Lens = np.array([x.shape[1] for x in Sd])
        X = np.concatenate(Sd, 1); Rr = np.concatenate(Rd, 1); sched = np.concatenate(Cd)
        bid = np.concatenate([b + 1000 * i for i, b in enumerate(Bd)])
        _, bid = np.unique(bid, return_inverse=True)
        obs = L.l1_variants(X, Rr, sched, bid)
        tbs = L.l1_trim_blockshift(Sd, Rd, Cd, Bd, rng, n_surr)  # round 1b: DQ8 design
        PS, _ = L.h12._pad_days(Sd); PR, _ = L.h12._pad_days(Rd)
        nulls = {k: [] for k in obs}
        for _ in range(n_surr):
            Xs, Rs = L.crossday_joint([PS, PR], Lens, rng)
            r = L.l1_variants(Xs, Rs, sched, bid)
            for k in obs:
                nulls[k].append(r[k])
        fl = L.stall_flags(X.T, Rr.T, sched)
        res = {"days": len(ud), "N": len(agents), "js_share": float(fl["js"].mean()), "stall_share": float(fl["explained"].mean())}
        for k in obs:
            nv = np.array(nulls[k]); nv = nv[np.isfinite(nv)]
            edge = float(np.quantile(nv, 0.95)) if nv.size else np.nan
            res[k] = {"l1": obs[k], "edge": edge, "ratio": obs[k] / edge if edge else np.nan, "above": bool(obs[k] > edge)}
        for k, v in tbs.items():
            res[f"{k}_bs"] = v
        out[u] = res
    return out


def run(period: str, n_surr: int = 200) -> dict:
    g = int(period[1:3])
    t0 = time.time()
    rng = np.random.default_rng([L.SEED, g])
    days = nonholdout_days(g)
    ab, sm = load(days)
    cal = pl.read_parquet(L.SH / "calendar.parquet").filter(pl.col("pt_date").is_in(days))
    res = {"period": period, "goal_no": g, "days": len(days), "regime": sorted(set(cal["regime"].cast(pl.String).to_list())),
           "n_surr": n_surr}
    res["o123"] = o123(ab, sm, days, rng, min(n_surr, 100))
    res["o4"] = o4_gains(ab, sm, days, rng, n_surr)
    res["o5"] = o5_lambda(ab, sm, days, g, rng, n_surr)
    res["runtime_s"] = round(time.time() - t0, 1)
    res["data_version"] = L.DATA_VERSION
    out = L.RES / period
    out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(res, indent=1, default=lambda x: float(x) if isinstance(x, np.floating) else
                                                (int(x) if isinstance(x, np.integer) else str(x))))
    a = (res["o4"] or {}).get("active", {})
    print(f"{period}: {len(days)} d, JS {res['o123']['js_share'] if res['o123'] else float('nan'):.3f}, "
          f"g raw {a.get('raw', {}).get('g', float('nan')):.3f} (z {a.get('raw', {}).get('z', float('nan')):.1f}), "
          f"stall {a.get('stall', {}).get('g', float('nan')):.3f}, mask_scaffold {a.get('mask_scaffold', {}).get('g', float('nan')):.3f}; "
          f"{res['runtime_s']} s", flush=True)
    return res


def periods_all():
    cal = pl.read_parquet(L.SH / "calendar.parquet").filter(~pl.col("holdout") & (pl.col("goal_no") > 0))
    return [f"G{g:02d}" for g in sorted(cal["goal_no"].unique().to_list())]


def _run(args):
    return run(*args)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period"); ap.add_argument("--all", action="store_true")
    ap.add_argument("--n-surr", type=int, default=200); ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--data-version", choices=["r1", "fixed"], default="r1")
    a = ap.parse_args()
    if a.all:
        ps = periods_all()
        ps = sorted(ps, key=lambda p: p != "G51")  # longest first
        with Pool(min(a.workers, 2)) as pool:
            pool.map(_run, [(p, a.n_surr) for p in ps], chunksize=1)
    else:
        run(a.period, a.n_surr)


if __name__ == "__main__":
    main()
