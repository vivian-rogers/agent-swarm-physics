"""H38 P9 (NE14, transition exception c): the regime II -> III boundary (2026-03-24: perma computer use, consolidation,
pause tool). Raw and stall-adjusted equal-time gains on the last regime-II days (#35, #36a = 03-23) vs the first
regime-III days (#36b = 03-24..03-27, #37). Each side is one window with its own present population (H02 rule: a row on
every day of the side and >= 30 active bins). N1 joint surrogates (200) for E and z; day bootstrap (500) for the
uncertainty of Delta = E_III - E_II.

Output: data/processed/H38-platform-stalls/NE14/result.json; the card's NE14 folder is written by summarize.py.
Usage: uv run python hypotheses/H38-platform-stalls/analysis/ne14.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import h38lib as L  # noqa: E402
import run_period as RP  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

VARS = ["raw", "lull", "stall", "field", "mask_edge", "mask_infra", "mask_scaffold", "mask_all"]
N_SURR, N_BOOT = 200, 500


def side_days():
    cal = pl.read_parquet(L.SH / "calendar.parquet").filter(~pl.col("holdout")).sort("pt_date")
    d35 = cal.filter(pl.col("goal_no") == 35)["pt_date"].to_list()
    d36 = cal.filter(pl.col("goal_no") == 36)["pt_date"].to_list()
    d37 = cal.filter(pl.col("goal_no") == 37)["pt_date"].to_list()
    ii = d35 + [d for d in d36 if d < "2026-03-24"]
    iii = [d for d in d36 if d >= "2026-03-24"] + d37
    for side in (ii, iii):
        assert not any(L.h12.holdout_mask(side, [0] * len(side)))
    return ii, iii


def window(days, rng):
    ab, sm = RP.load(days)
    pres = (ab.group_by("agent").agg(pl.col("pt_date").n_unique().alias("nd"), (pl.col("state") >= 3).sum().alias("nact"))
            .filter((pl.col("nd") == len(days)) & (pl.col("nact") >= RP.MIN_ACTIVE_BINS)).sort("agent"))
    agents = pres["agent"].to_list()
    S, Tk, R, day, minute, sched = RP.matrices(ab, sm, days, agents)
    bid, segs = L.block_segments(day, minute)
    res, f = L.gains(S, R, sched, bid)
    out = {"days": days, "N": len(agents), "js_share": float(f["js"].mean()), "stall_share": float(f["explained"].mean())}
    nulls = {v: [] for v in VARS}
    for _ in range(N_SURR):
        Sx, Rx = L.joint_shift([S, R], segs, rng)
        rx, _ = L.gains(Sx, Rx, sched, bid)
        for v in VARS:
            nulls[v].append(L.cw(rx[v][0])["g"])
    # day bootstrap of the observed g per variant (block suffstats carry their day)
    bday = np.array([day[bid == b][0] for b in range(bid.max() + 1)])
    for v in VARS:
        nv = np.array(nulls[v])
        go = L.cw(res[v][0])["g"]
        out[v] = {"g": go, "null_mean": float(nv.mean()), "null_sd": float(nv.std()), "E": go - float(nv.mean()),
                  "z": (go - nv.mean()) / nv.std()}
    # bootstrap: recompute suffstats per day once, then resample days
    per_day = {}
    for d in np.unique(day):
        m = day == d
        rr, _ = L.gains(S[m], R[m], sched[m], L.h02.block_ids(day[m], minute[m]))
        per_day[d] = {v: rr[v][0] for v in VARS}
    dd = list(per_day)
    boots = {v: [] for v in VARS}
    for _ in range(N_BOOT):
        pick = rng.choice(dd, size=len(dd), replace=True)
        for v in VARS:
            boots[v].append(L.cw(np.vstack([per_day[x][v] for x in pick]))["g"])
    for v in VARS:
        out[v]["boot_sd"] = float(np.nanstd(boots[v]))
    _ = bday
    return out


def main():
    rng = np.random.default_rng([L.SEED, 14])
    ii, iii = side_days()
    A, B = window(ii, rng), window(iii, rng)
    # sensitivity (post hoc, disclosed): drop 2026-03-31, whose window contains a 513-min operator-scheduled gap
    B2 = window([d for d in iii if d != "2026-03-31"], rng)
    res = {"II": A, "III": B, "III_no0331": B2, "delta": {}, "delta_no0331": {}}
    for key, BB in (("delta", B), ("delta_no0331", B2)):
        for v in VARS:
            dE = BB[v]["E"] - A[v]["E"]
            se = float(np.hypot(A[v]["boot_sd"], BB[v]["boot_sd"]))
            res[key][v] = {"dE": dE, "se": se, "lo": dE - 1.96 * se, "hi": dE + 1.96 * se}
    out = L.DATA / "NE14"
    out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(res, indent=1, default=float))
    for v in VARS:
        print(f"{v:14s} II E={A[v]['E']:.3f} (z {A[v]['z']:.1f})  III E={B[v]['E']:.3f} (z {B[v]['z']:.1f})  "
              f"dE={res['delta'][v]['dE']:+.3f} ± {1.96 * res['delta'][v]['se']:.3f}")
    print("N", A["N"], B["N"], "stall share", round(A["stall_share"], 3), round(B["stall_share"], 3))
    for v in VARS:
        print(f"  no 03-31: {v:14s} III E={B2[v]['E']:.3f} (z {B2[v]['z']:.1f})  dE={res['delta_no0331'][v]['dE']:+.3f} ± "
              f"{1.96 * res['delta_no0331'][v]['se']:.3f}")
    print("  no 03-31 stall share", round(B2["stall_share"], 3), "N", B2["N"])


if __name__ == "__main__":
    main()
