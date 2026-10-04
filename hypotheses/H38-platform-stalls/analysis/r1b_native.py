"""H38 round 1b, period-native tests (DQ9 cross-index), on the corrected tables (activity_bins_fixed + outages_fixed).
Predictions are in the folders, written before this script was run:
  NE43  goalperiod-subhypotheses/NE43/README.md  bookends stop 08-05 vs nudger stop 08-21 inside #51 (day-edge mechanism)
  G04   goalperiod-subhypotheses/G04/README.md   the 2025-06-18 stop-and-restart (#4d)
NE14 / #36 (the third native test) is computed by ne14.py --data-version fixed.

Per day d (day-present population: agents with >= 30 active minutes that day):
  E_v(d) = g_v(d) - mean_null g_v(d), N1 block-shift surrogates (200, joint with reasons) for the round-1 variants
  (raw, stall, mask_edge, mask_scaffold) and the DQ8 trimmed variants (trim, trim_stall, trim_scaffold; rows removed
  before the surrogates); D_edge = E_raw - E_mask_edge; start / end spread = SD across agents of the first / last
  active minute of the day.
Output: data/processed/H38-platform-stalls/r1b/native/{ne43_days.parquet, g04_days.parquet, native.json}.
Usage: uv run python hypotheses/H38-platform-stalls/analysis/r1b_native.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

os.environ["H38_DATA_VERSION"] = "fixed"
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import h38lib as L  # noqa: E402
import run_period as RP  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

N_SURR = 200
N_PERM = 10000
MIN_ACT_DAY = 30
VARS = ["raw", "stall", "mask_edge", "mask_scaffold"]
OUT = L.RES / "native"


def day_stats(ab, sm, d, rng) -> dict | None:
    a = ab.filter(pl.col("pt_date") == d)
    pres = (a.group_by("agent").agg((pl.col("state") >= 3).sum().alias("n")).filter(pl.col("n") >= MIN_ACT_DAY)
            .sort("agent")["agent"].to_list())
    if len(pres) < 3:
        return None
    S, Tk, R, day, minute, sched = RP.matrices(ab, sm, [d], pres)
    bid, segs = L.block_segments(day, minute)
    res, f = L.gains(S, R, sched, bid)
    nul = {v: [] for v in VARS}
    for _ in range(N_SURR):
        Sx, Rx = L.joint_shift([S, R], segs, rng)
        rx, _ = L.gains(Sx, Rx, sched, bid)
        for v in VARS:
            nul[v].append(L.cw(rx[v][0])["g"])
    tob, tnu = L.trim_gains(S, R, sched, day, minute, f["explained"], rng, N_SURR)
    out = {"pt_date": d, "N": len(pres), "T": int(len(minute)), "js_share": float(f["js"].mean()),
           "stall_share": float(f["explained"].mean()), "trim_share": float(L.trim_mask(R).mean()),
           "sched_share": float(sched.mean())}
    for v in VARS:
        g = L.cw(res[v][0])["g"]; nv = np.array(nul[v]); nv = nv[np.isfinite(nv)]
        out[f"g_{v}"] = g; out[f"E_{v}"] = g - nv.mean() if nv.size else np.nan
        out[f"z_{v}"] = (g - nv.mean()) / nv.std() if nv.size and nv.std() > 0 else np.nan
    for v in ("trim", "trim_stall", "trim_scaffold"):
        if v not in tob:
            out[f"g_{v}"] = out[f"E_{v}"] = out[f"z_{v}"] = np.nan
            continue
        g = L.cw(tob[v][0])["g"]; nv = np.array([L.cw(x[0])["g"] for x in tnu[v]]); nv = nv[np.isfinite(nv)]
        out[f"g_{v}"] = g; out[f"E_{v}"] = g - nv.mean() if nv.size else np.nan
        out[f"z_{v}"] = (g - nv.mean()) / nv.std() if nv.size and nv.std() > 0 else np.nan
    out["D_edge"] = out["E_raw"] - out["E_mask_edge"]
    act = S > 0
    first = np.array([minute[act[:, j]].min() for j in range(act.shape[1]) if act[:, j].any()])
    last = np.array([minute[act[:, j]].max() for j in range(act.shape[1]) if act[:, j].any()])
    out["start_sd"] = float(first.std()); out["end_sd"] = float(last.std())
    out["start_med"] = float(np.median(first)); out["end_med"] = float(np.median(minute.max() - last))
    return out


def perm_test(x, y, rng, side="less"):
    """Difference of means mean(y) - mean(x); one-sided p for 'less' (y < x) or 'greater' (y > x), two-sided 'two'."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    x, y = x[np.isfinite(x)], y[np.isfinite(y)]
    obs = y.mean() - x.mean()
    z = np.r_[x, y]
    nx = len(x)
    null = np.empty(N_PERM)
    for k in range(N_PERM):
        p = rng.permutation(z)
        null[k] = p[nx:].mean() - p[:nx].mean()
    if side == "less":
        pv = (1 + (null <= obs).sum()) / (N_PERM + 1)
    elif side == "greater":
        pv = (1 + (null >= obs).sum()) / (N_PERM + 1)
    else:
        pv = (1 + (np.abs(null) >= abs(obs)).sum()) / (N_PERM + 1)
    return {"diff": float(obs), "p": float(pv), "n_x": int(nx), "n_y": int(len(y))}


def ne43(rng) -> tuple[pl.DataFrame, dict]:
    days = RP.nonholdout_days(51)
    ab, sm = RP.load(days)
    rows = [r for d in days if (r := day_stats(ab, sm, d, rng)) is not None]
    df = pl.DataFrame(rows).with_columns(
        pl.when(pl.col("pt_date") < "2026-08-05").then(pl.lit("A")).when(pl.col("pt_date") < "2026-08-21")
        .then(pl.lit("B")).otherwise(pl.lit("C")).alias("window"))
    W = {w: df.filter(pl.col("window") == w) for w in "ABC"}
    res = {"n_days": {w: W[w].height for w in "ABC"},
           "means": {w: {c: float(W[w][c].mean()) for c in ("D_edge", "E_raw", "E_mask_edge", "E_mask_scaffold", "E_trim",
                                                         "E_trim_stall", "start_sd", "end_sd", "sched_share", "js_share", "N")}
                     for w in "ABC"}}
    res["N1a_Dedge_B_lt_A"] = perm_test(W["A"]["D_edge"], W["B"]["D_edge"], rng, "less")
    res["N1a_start_sd_B_gt_A"] = perm_test(W["A"]["start_sd"], W["B"]["start_sd"], rng, "greater")
    res["end_sd_B_gt_A"] = perm_test(W["A"]["end_sd"], W["B"]["end_sd"], rng, "greater")
    res["N1b_Dedge_C_vs_B"] = perm_test(W["B"]["D_edge"], W["C"]["D_edge"], rng, "two")
    res["start_sd_C_vs_B"] = perm_test(W["B"]["start_sd"], W["C"]["start_sd"], rng, "two")
    for c in ("E_raw", "E_trim", "E_trim_stall", "E_mask_scaffold"):
        res[f"{c}_B_vs_A"] = perm_test(W["A"][c], W["B"][c], rng, "two")
        res[f"{c}_C_vs_B"] = perm_test(W["B"][c], W["C"][c], rng, "two")
    n1a = res["N1a_Dedge_B_lt_A"]["p"] < 0.05 and res["N1a_start_sd_B_gt_A"]["p"] < 0.05
    n1b = (abs(res["N1b_Dedge_C_vs_B"]["diff"]) < abs(res["N1a_Dedge_B_lt_A"]["diff"])) and res["N1b_Dedge_C_vs_B"]["p"] >= 0.05
    moved = res["N1a_Dedge_B_lt_A"]["p"] < 0.05 or res["N1a_start_sd_B_gt_A"]["p"] < 0.05
    res["N1a"] = bool(n1a); res["N1b"] = bool(n1b)
    res["verdict"] = "supported" if (n1a and n1b) else ("failed" if not moved else "mixed")
    return df, res


def g04(rng) -> tuple[pl.DataFrame, dict]:
    days = RP.nonholdout_days(4)
    ab, sm = RP.load(days)
    rows = [r for d in days if (r := day_stats(ab, sm, d, rng)) is not None]
    df = pl.DataFrame(rows)
    D = "2025-06-18"
    o = pl.read_parquet(L.STALLS / "outages.parquet").filter(pl.col("pt_date") == D)
    off = o.filter(pl.col("village_off")).sort("k0_longest", descending=True)
    res = {"outage_runs_0618": o.height,
           "longest_off_min": int(off["k0_longest"][0]) if off.height else 0,
           "longest_off_frac_scheduled": float(off["frac_scheduled"][0]) if off.height else None,
           "longest_off_cause": off["cause"][0] if off.height else None}
    res["N2a"] = bool(res["longest_off_min"] >= 240 and (res["longest_off_frac_scheduled"] or 0) >= 0.8)
    x = df.filter(pl.col("pt_date") == D)
    oth = df.filter(pl.col("pt_date") != D)
    if x.height:
        m = {c: float(oth[c].median()) for c in ("E_raw", "E_stall", "E_trim_stall", "E_trim")}
        v = {c: float(x[c][0]) for c in m}
        res.update({"day": v, "others_median": m, "others_n": oth.height,
                    "rank_E_raw": int((oth["E_raw"] < v["E_raw"]).sum()) + 1})
        res["N2b"] = bool(v["E_raw"] > m["E_raw"])
        res["N2c_stall"] = bool(abs(v["E_stall"] - m["E_stall"]) < abs(v["E_raw"] - m["E_raw"]))
        res["N2c_trim"] = bool(abs(v["E_trim_stall"] - m["E_trim_stall"]) < abs(v["E_raw"] - m["E_raw"]))
        # restart spread: first active minute of each present agent after the longest K = 0 run
        if off.height:
            a = ab.filter(pl.col("pt_date") == D)
            m_end = int(off["m_end"][0])
            fa = (a.filter((pl.col("state") >= 3) & (pl.col("minute") >= m_end)).group_by("agent")
                  .agg(pl.col("minute").min().alias("m")))
            res["restart_first_minutes"] = sorted(int(z - m_end) for z in fa["m"].to_list())
            res["restart_sd"] = float(np.std(fa["m"].to_numpy())) if fa.height else None
            res["N2d"] = bool(fa.height and (fa["m"].max() - fa["m"].min()) <= 10 and res["restart_sd"] <= 5)
        res["verdict"] = ("supported" if res["N2a"] and res["N2b"] and res["N2c_stall"] and res["N2c_trim"] else
                          "failed" if (not res["N2b"]) or (not res["N2c_stall"] and not res["N2c_trim"]) else "mixed")
    else:
        res["verdict"] = "n/a"
    return df, res


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng([L.SEED, 43])
    d43, r43 = ne43(rng)
    d43.write_parquet(OUT / "ne43_days.parquet")
    d04, r04 = g04(np.random.default_rng([L.SEED, 4]))
    d04.write_parquet(OUT / "g04_days.parquet")
    R = {"NE43": r43, "G04_0618": r04, "data_version": L.DATA_VERSION, "n_surr": N_SURR, "n_perm": N_PERM}
    (OUT / "native.json").write_text(json.dumps(R, indent=1, default=float))
    print(json.dumps(R, indent=1, default=float))


if __name__ == "__main__":
    main()
