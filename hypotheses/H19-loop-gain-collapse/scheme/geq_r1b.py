"""H19 round 1b (improved data, 2026-10-04): H19's own equal-time gain g_eq on the corrected minute grid, with the DQ8
null design and H38's day-edge adjustment.

Per H02-rule chunk (5-day chunks, present population: a row on every day and >= 30 active bins) and spin (active,
talk with >= 30 talk bins), three versions of g = 1 - 1/VR (30-min blocks, H02/H19 estimator):
  raw     round-1 definition (whole-day grid)                                   -> method H19.geq_<spin>
  trim    DQ8: all-present window, then H38's explained joint silences removed  -> method H19.geq_<spin>_trim
          (`nulls.py` variant cw_gain_trim_h38mask; rows removed before the surrogates)
  scaf    H38 agent-state conditioning on the whole grid (`h38lib.gains`, variant mask_scaffold: operator-off minutes
          dropped, silent agent-minutes with a pre / post / infra-error / consolidation reason imputed)
                                                                                -> method H19.geq_<spin>_scaf
Each with a day-bootstrap SE (H19's cw_boot) and, for raw and trim, a joint N1 block-shift surrogate null (spins,
talk spins and reasons shifted together within (day, 30-min block) of the kept rows): E = g - mean(null), z.
"round-1 null" = N1 on the whole-day grid; "corrected null" = N1 after trim + stall mask (DQ8 size 0.02-0.04 on
independent swarms vs 0.28-0.34 untrimmed).

Inputs: activity_bins_fixed, outages_fixed/{reasons,stall_minutes} (or the round-1 tables with bins="old").
Masks and imputation: hypotheses/H02-couplings-are-real/analysis/r1b_common.py (frozen copies of H38's helpers).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h19common as C  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "h02_r1b_common_readonly", C.ROOT / "hypotheses/H02-couplings-are-real/analysis/r1b_common.py")
RB = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(RB)

CHUNK_DAYS, MIN_TAIL_DAYS, MIN_ACTIVE_BINS = 5, 3, 30
BLOCK_MIN, MIN_LAST_BLOCK, MIN_BLOCK_N = 30, 10, 5
N_SURR = 50
SCAF = RB.MASK_SETS["mask_scaffold"]


def block_ids(day, minute):
    blk = minute // BLOCK_MIN
    out = np.empty_like(blk)
    for d in np.unique(day):
        m = day == d
        b = blk[m].copy()
        last = b.max()
        if last > 0 and (b == last).sum() < MIN_LAST_BLOCK:
            b[b == last] = last - 1
        out[m] = b
    keys = day.astype(np.int64) * 1000 + out
    _, inv = np.unique(keys, return_inverse=True)
    return inv, keys // 1000


def suff(X, bid, bday):
    """Per block with >= MIN_BLOCK_N rows: n, n Var(M), n sum_i Var(s_i), n mean_i Var(s_i), day."""
    X = np.asarray(X, float)
    rows = []
    for b in np.unique(bid):
        m = bid == b
        n = int(m.sum())
        if n < MIN_BLOCK_N:
            continue
        Y = X[m]
        v = Y.var(0)
        rows.append((n, Y.sum(1).var() * n, v.sum() * n, v.mean() * n, bday[m][0]))
    return np.array(rows, float).reshape(-1, 5)


def cw(st):
    if st.shape[0] == 0 or st[:, 2].sum() <= 0:
        return {"g": np.nan, "VR": np.nan, "q": np.nan, "bJ0": np.nan}
    VR = st[:, 1].sum() / st[:, 2].sum()
    q = st[:, 3].sum() / st[:, 0].sum()
    return {"g": 1 - 1 / VR, "VR": VR, "q": q, "bJ0": (1 - 1 / VR) / q}


def boot_se(st, rng, nboot=300):
    days = np.unique(st[:, 4])
    if len(days) < 2:
        return np.nan, "none"
    idx = {d: np.flatnonzero(st[:, 4] == d) for d in days}
    gs = [cw(st[np.concatenate([idx[d] for d in rng.choice(days, len(days), replace=True)])])["g"] for _ in range(nboot)]
    return float(np.nanstd(gs) * np.sqrt(len(days) / (len(days) - 1))), "day_boot" if len(days) >= 4 else "day_boot_small"


def joint_shift(arrays, bid, rng):
    out = [np.empty_like(a) for a in arrays]
    N = arrays[0].shape[1]
    for b in np.unique(bid):
        idx = np.flatnonzero(bid == b)
        L = idx.size
        if L < 2:
            for a, o in zip(arrays, out):
                o[idx] = a[idx]
            continue
        sh = rng.integers(1, L, size=N)
        ar = (np.arange(L)[:, None] - sh[None, :]) % L
        for a, o in zip(arrays, out):
            o[idx] = a[idx][ar, np.arange(N)[None, :]]
    return out


def load_bins(days, bins="fixed"):
    path = C.SHARED / ("activity_bins_fixed.parquet" if bins == "fixed" else "activity_bins.parquet")
    ab = (pl.scan_parquet(path).filter(pl.col("pt_date").is_in(days)).select("pt_date", "minute", "agent", "state")
          .collect().with_columns(pl.col("minute").cast(pl.Int32)))
    if bins == "fixed":
        rs = pl.read_parquet(C.SHARED / "outages_fixed/reasons.parquet").filter(pl.col("pt_date").is_in(days))
        sm = pl.read_parquet(C.SHARED / "outages_fixed/stall_minutes.parquet", columns=["pt_date", "minute", "scheduled"])
    else:
        rs = pl.read_parquet(C.SHARED / "reasons.parquet").filter(pl.col("pt_date").is_in(days))
        sm = pl.read_parquet(C.SHARED / "stall_minutes.parquet", columns=["pt_date", "minute", "scheduled"])
    rs = rs.with_columns(pl.col("minute").cast(pl.Int32))
    sm = sm.filter(pl.col("pt_date").is_in(days)).with_columns(pl.col("minute").cast(pl.Int32))
    return ab.join(rs, on=["pt_date", "minute", "agent"], how="left").with_columns(pl.col("reason").fill_null(0)), sm


def matrices(ab, sm, ch, agents):
    d = ab.filter(pl.col("pt_date").is_in(ch) & pl.col("agent").is_in(agents)).with_columns(
        pl.col("pt_date").replace_strict({x: i for i, x in enumerate(ch)}, return_dtype=pl.Int16).alias("day"))
    cols = [str(a) for a in agents]
    st = d.pivot(on="agent", index=["day", "minute"], values="state").sort("day", "minute")
    state = np.nan_to_num(st.select(cols).to_numpy().astype(float), nan=1).astype(np.int8)
    rr = np.nan_to_num(d.pivot(on="agent", index=["day", "minute"], values="reason").sort("day", "minute")
                       .select(cols).to_numpy().astype(float), nan=0).astype(np.int8)
    day = st["day"].to_numpy().astype(np.int64)
    minute = st["minute"].to_numpy().astype(np.int64)
    S = np.where(state >= 3, 1, -1).astype(np.int8)
    Tk = np.where(state == 4, 1, -1).astype(np.int8)
    R = np.where(S > 0, 0, rr).astype(np.int8)
    key = pl.DataFrame({"pt_date": [ch[i] for i in day], "minute": minute.astype(np.int32)})
    sched = key.join(sm, on=["pt_date", "minute"], how="left")["scheduled"].fill_null(False).to_numpy()
    return S, Tk, R, day, minute, sched


def chunk_estimates(S, Tk, R, day, minute, sched, talk_ok, rng, n_surr=N_SURR):
    """Returns {spin: {variant: dict}} for spins active / talk (talk only if >= 3 talk agents)."""
    out = {}
    keep_trim = RB.keep_runs(day, RB.row_mask(S, R, sched, "trim_stall"))
    spins = {"active": (S, slice(None))}
    if talk_ok.sum() >= 3:
        spins["talk"] = (Tk, talk_ok)
    bid, bday = block_ids(day, minute)
    bid_t, bday_t = block_ids(day[keep_trim], minute[keep_trim]) if keep_trim.sum() else (None, None)
    ns = ~sched
    bid_s, bday_s = block_ids(day[ns], minute[ns])
    for spin, (X, cols) in spins.items():
        Xc = X[:, cols]
        Rc = R[:, cols]
        rec = {}
        # raw
        st = suff(Xc, bid, bday)
        rec["raw"] = {**cw(st), "st": st}
        # trim + stall mask
        if bid_t is not None:
            stt = suff(Xc[keep_trim], bid_t, bday_t)
            rec["trim"] = {**cw(stt), "st": stt, "kept_share": float(keep_trim.mean())}
        # H38 agent-state conditioning (mask_scaffold) on the whole grid
        Xi = RB.impute(Xc[ns], Rc[ns], bid_s, SCAF)
        sts = suff(Xi, bid_s, bday_s)
        rec["scaf"] = {**cw(sts), "st": sts}
        # surrogate nulls: round-1 design (whole grid) and corrected design (after trim + mask)
        for vn, (keep, b_) in (("raw", (np.ones(len(day), bool), bid)), ("trim", (keep_trim, bid_t))):
            if vn not in rec or b_ is None:
                continue
            Xk = Xc[keep]
            bd = bday if vn == "raw" else bday_t
            nul = np.array([cw(suff(joint_shift([Xk], b_, rng)[0], b_, bd))["g"] for _ in range(n_surr)])
            rec[vn].update({"null_mean": float(np.nanmean(nul)), "null_sd": float(np.nanstd(nul)),
                            "E": float(rec[vn]["g"] - np.nanmean(nul)),
                            "z": float((rec[vn]["g"] - np.nanmean(nul)) / max(np.nanstd(nul), 1e-12))})
        out[spin] = rec
    return out


def chunks_of(days):
    ch = [days[i:i + CHUNK_DAYS] for i in range(0, len(days), CHUNK_DAYS)]
    if len(ch) > 1 and len(ch[-1]) < MIN_TAIL_DAYS:
        ch = ch[:-1]
    return ch


def own_geq_r1b(cal: pl.DataFrame, rng: np.random.Generator, bins: str = "fixed") -> pl.DataFrame:
    days = cal["pt_date"].to_list()
    ab, sm = load_bins(days, bins)
    rows = []
    for g in sorted(cal["goal_no"].unique().to_list()):
        gdays = sorted(cal.filter(pl.col("goal_no") == g)["pt_date"].to_list())
        for k, ch in enumerate(chunks_of(gdays)):
            d = ab.filter(pl.col("pt_date").is_in(ch))
            pres = (d.group_by("agent").agg(pl.col("pt_date").n_unique().alias("nd"), (pl.col("state") >= 3).sum().alias("nact"),
                                            (pl.col("state") == 4).sum().alias("ntalk"))
                    .filter((pl.col("nd") == len(ch)) & (pl.col("nact") >= MIN_ACTIVE_BINS)).sort("agent"))
            if pres.height < 3:
                continue
            agents = pres["agent"].to_list()
            talk_ok = np.array([n >= MIN_ACTIVE_BINS for n in pres["ntalk"].to_list()])
            S, Tk, R, day, minute, sched = matrices(ab, sm, ch, agents)
            est = chunk_estimates(S, Tk, R, day, minute, sched, talk_ok, rng)
            for spin, rec in est.items():
                for vn, suffix in (("raw", ""), ("trim", "_trim"), ("scaf", "_scaf")):
                    if vn not in rec or not np.isfinite(rec[vn]["g"]):
                        continue
                    se, kind = boot_se(rec[vn]["st"], rng)
                    rows.append({"goal_no": g, "window": f"g{g:02d}c{k}", "method": f"H19.geq_{spin}{suffix}",
                                 "value": rec[vn]["g"], "se": se, "ci_kind": kind, "n_days": len(ch),
                                 "N": len(agents) if spin == "active" else int(talk_ok.sum()),
                                 "VR": rec[vn]["VR"], "q": rec[vn]["q"], "bJ0": rec[vn]["bJ0"],
                                 "occupancy": float((S > 0).mean()), "kept_share": rec[vn].get("kept_share", 1.0),
                                 "null_mean": rec[vn].get("null_mean"), "null_sd": rec[vn].get("null_sd"),
                                 "E": rec[vn].get("E"), "z": rec[vn].get("z")})
            print(f"  g_eq r1b {g:02d}c{k}: " + ", ".join(f"{s}:{v['raw']['g']:.3f}/{v.get('trim', {}).get('g', np.nan):.3f}/"
                                                            f"{v['scaf']['g']:.3f}" for s, v in est.items()), flush=True)
    return pl.DataFrame(rows)
