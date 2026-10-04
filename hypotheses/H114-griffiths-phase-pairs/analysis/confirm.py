"""H114 confirmatory run on the LOCKED HOLDOUT. Written and frozen 2026-10-04 after round 1; NOT RUN.

Guard: runs on held-out data only with BOTH `--confirm` and H114_CONFIRM=1, and only if `holdout_ledger.check` allows
every target. Otherwise it refuses. `--dry-run` runs the identical pipeline on non-holdout stand-in units, rebuilt
from the shared tables into a scratch directory, so the code path is tested without touching the holdout.

Targets (period units of): #28 (regime I), #43 (regime III) and the #51 tail (regime III).

Frozen estimator (round 1 primary): DQ2 parents (pair_set cand, p_reply >= 0.5), cross-day links cut, depth counted
for messages in the DQ8 all-present window; h_tail over d >= 4 (d <= 30); day blocks (> 5 days) or (day, hour) blocks;
B = 500; strong pair = R_ij >= 10 and Garwood lower bound of L_ij/R_ij > 0.5; 200 matched random cuts.

Frozen predictions (round 1 pattern; the HH's Griffiths mechanism is predicted to FAIL):
  C1  Heavier than geometric: in each target period the random-effects pooled dh = h_tail - g_rep is > 0 with a 95% CI
      excluding 0.  (Round 1: CI > 0 in 33/54 units; point > 0 in 52/54.)
  C2  First-order thread momentum: h(1) > g_rep in every usable target unit (round 1: 54/54), and the pooled Griffiths
      rise delta_h = h_tail - h(1) over all target units is < 0.08 or has a CI including 0 (round 1: rise significant
      in 10/54; regime medians 0.08 (I) and 0.02 (III)).
  C3  Strong pairs do not carry the tail: among target units with >= 1 strong pair, the strong-pair cut brings dh'
      within CI of 0 and below the 5th percentile of matched random cuts in fewer than half (round 1: 1/16).
  C4  Agent heterogeneity does not explain the tail: the observed h_tail's 95% lower bound exceeds the rank-1 M1
      prediction in >= half of the usable target units (round 1: 31/54).
Reading: C1 + C2 + C4 confirm "reply chains are heavier than uniform subcritical branching because of first-order
thread momentum"; C3 confirms that rare strong pairs do not carry it (the HH's Griffiths phase refuted).

Reuse policy (hypotheses/holdout.md): planned users of #28, #43 and the #51 tail include H63 and H28 (link family on
reply-adjacent data), H34/H61/H62 (cascade trees), H37/H64 (stance on DQ2 pairs) and H67/H99/H101 (activity and talk).
H114's statistic (DQ2 reply-depth hazard) is new; disclose to H62/H63 if they run first. Disclose in the card and
LOG.md before running.

Usage:
  uv run python hypotheses/H114-griffiths-phase-pairs/analysis/confirm.py --dry-run
  H114_CONFIRM=1 uv run python hypotheses/H114-griffiths-phase-pairs/analysis/confirm.py --confirm
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import build as B  # noqa: E402
import h114lib as L  # noqa: E402

ROOT = HERE.parents[2]
SH = ROOT / "data/processed/shared"
sys.path.insert(0, str(ROOT / "infra/shared"))
OUT = ROOT / "data/processed/H114-griffiths-phase-pairs/confirm"
SCRATCH = Path(os.environ.get("TMPDIR", "/tmp")) / "h114_confirm_dryrun"
TARGET_GOALS = {28: "I", 43: "III", 51: "III"}
STANDINS = {"27": "I", "41": "III", "51h": "III"}
FROZEN = dict(B=500, n_rand=200, C2_rise=0.08, min_links=100, min_tail=30)


def se_ci(lo, hi):
    return (np.asarray(hi, float) - np.asarray(lo, float)) / 3.92


def score(rows: list, period_of: dict) -> dict:
    df = pl.DataFrame(rows).with_columns(pl.col("unit").replace_strict(period_of, default=None).alias("period"))
    us = df.filter((pl.col("n_links") >= FROZEN["min_links"]) & (pl.col("n_tail") >= FROZEN["min_tail"])
                   & pl.col("dh").is_finite())
    out = {"C1_detail": {}}
    c1 = []
    for p in sorted(set(us["period"].to_list())):
        x = us.filter(pl.col("period") == p)
        m, lo, hi, _ = L.re_pool(x["dh"].to_numpy(), se_ci(x["dh_lo"], x["dh_hi"]))
        out["C1_detail"][str(p)] = {"dh": m, "lo": lo, "hi": hi}
        c1.append(lo > 0)
    out["C1"] = bool(c1 and all(c1))
    m, lo, hi, _ = L.re_pool(us["delta_h"].to_numpy(), se_ci(us["delta_h_lo"], us["delta_h_hi"]))
    out["C2"] = bool((us["h_1"] > us["g_rep"]).all() and (m < FROZEN["C2_rise"] or lo <= 0))
    out["C2_detail"] = {"delta_h": m, "lo": lo, "hi": hi, "h1_gt_grep": int((us["h_1"] > us["g_rep"]).sum()),
                        "n": us.height}
    ws = us.filter(pl.col("n_strong") > 0)
    carry = ((ws["dh_cut_lo"] <= 0) & (ws["dh_cut_hi"] >= 0) & (ws["dh_cut"] < ws["dh_rand_q05"])).sum() if ws.height else 0
    out["C3"] = bool(ws.height == 0 or carry < ws.height / 2)
    out["C3_detail"] = {"units_with_strong": ws.height, "carry": int(carry)}
    out["C4"] = bool((us["h_tail_lo"] > us["h_tail_M1"]).sum() >= us.height / 2) if us.height else False
    out["C4_detail"] = {"above_M1": int((us["h_tail_lo"] > us["h_tail_M1"]).sum()), "n": us.height}
    out["units"] = df.to_dicts()
    return out


def run(base: Path, units: dict) -> list:
    rows = []
    for uid, nd in units.items():
        m, R = L.load_unit(uid, base)
        st = L.unit_stats(m, R, nd, B=FROZEN["B"], n_rand=FROZEN["n_rand"], seed=11)
        st.pop("_pairs")
        rows.append({"unit": uid, **{k: st.get(k) for k in ("n_links", "n_tail", "g_rep", "h_1", "h_tail", "h_tail_lo",
                                                           "dh", "dh_lo", "dh_hi", "delta_h", "delta_h_lo",
                                                           "delta_h_hi", "h_tail_M1", "h_tail_M2", "n_strong",
                                                           "dh_cut", "dh_cut_lo", "dh_cut_hi", "dh_rand_q05")}})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    pu = pl.read_parquet(SH / "period_units.parquet")
    if a.dry_run:
        SCRATCH.mkdir(parents=True, exist_ok=True)
        cc, rp, cw, pdr, cal = B.load_shared(allow_holdout=False)
        units, period_of = {}, {}
        for u in pu.filter(pl.col("unit_id").is_in(list(STANDINS))).to_dicts():
            r = B.build_unit(u, cc, rp, cw, pdr, cal, out=SCRATCH, allow_holdout=False)
            if r:
                units[u["unit_id"]] = len(u["days"])
                period_of[u["unit_id"]] = u["goal_no"]
        out = score(run(SCRATCH, units), period_of)
        (SCRATCH / "confirm_dryrun.json").write_text(json.dumps({"sha256": sha, "dry_run": True, **out}, indent=1,
                                                                default=float))
        print(json.dumps({k: v for k, v in out.items() if k != "units"}, indent=1, default=float))
        return
    if not (a.confirm and os.environ.get("H114_CONFIRM") == "1"):
        sys.exit("refusing: confirmatory run needs --confirm and H114_CONFIRM=1 (Vivian's sign-off)")
    import holdout_ledger as HL
    for g in TARGET_GOALS:
        tgt = "#51-tail" if g == 51 else f"G{g}"
        chk = HL.check("H114", tgt, "reply", ["reply_tree_tail"])
        if not chk["allowed"]:
            sys.exit(f"refusing: holdout ledger blocks {tgt}: {chk['prior_runs_same_family']}")
    held = pu.filter(pl.col("holdout") & pl.col("goal_no").is_in(list(TARGET_GOALS)))
    cc, rp, cw, pdr, cal = B.load_shared(allow_holdout=True)
    units, period_of = {}, {}
    for u in held.to_dicts():
        r = B.build_unit(u, cc, rp, cw, pdr, cal, out=OUT, allow_holdout=True)
        if r:
            units[u["unit_id"]] = len(u["days"])
            period_of[u["unit_id"]] = u["goal_no"]
    out = score(run(OUT, units), period_of)
    (OUT / "confirm_result.json").write_text(json.dumps({"sha256": sha, **out}, indent=1, default=float))
    print(json.dumps({k: v for k, v in out.items() if k != "units"}, indent=1, default=float))


if __name__ == "__main__":
    main()
