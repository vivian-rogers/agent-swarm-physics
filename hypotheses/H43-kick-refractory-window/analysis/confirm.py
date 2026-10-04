"""H43 confirmatory test on the LOCKED HOLDOUT. Written 2026-10-04 after exploratory round 1; NOT RUN.

Refuses to touch held-out data unless called with BOTH flags:
    --confirm --i-understand-this-uses-the-locked-holdout
and refuses if hypotheses/H43-kick-refractory-window/ has uncommitted changes (reuse policy, condition 1: predictions and
this script committed before the run). Without the flags it runs a DRY RUN on non-holdout stand-ins and writes
data/processed/H43-kick-refractory-window/confirm_dryrun/confirm_results.json.

Frozen predictions (the round-1 findings, stated as confirmable claims; card, "Confirmatory plan"):
  C1  mentions, #51 tail (2026-09-07 -> 09-21), busy recipients, O2c (the receiving call replies):
      E1 > 0 (95% CI above 0); 0.3 < R(0,15] lower CI and R(0,15] point in [0.5, 1.1] (a shallow dip, not a window);
      R(60,240] >= 0.7; delta_half < 2 min in >= 80% of bootstrap draws.
  C2  mentions, #51 tail: a second mention read in the SAME call adds little: batched R (O2c) <= 0.5.
  C3  mentions, #51 tail, O2: no episode lock: R_in >= 0.4 (episode-lock signature in the synthetic: ~0.2).
  C4  nudges, held-out regime-III goal periods #45-#50 (stratified by unit; per period and pooled): first nudge after a
      30-min quiet spell: E1(O1a, any activity) > 0 and E1(O1, sustained run) < 0.3; re-fires keep the effect:
      R(15,60] on O1a >= 0.7. n/a if < 50 pooled idle primers.
  C5  human messages, held-out regime-I periods #1, #9, #14, #15 (5-min quiet rule, units as strata): E1(O2c) > 0 and
      R(0,2] (O2c) >= 0.7. n/a if < 50 pooled busy primers.
Scoring: each C is pass / fail / n/a. Overall: "no refractory window beyond the read-out" is confirmed if C1, C2 and at
least one of C4/C5 pass and none of the scored ones fails.

Reuse of held-out periods (hypotheses/holdout.md, default policy): #45 was used by H02's confirmatory run (activity
couplings) and #46-#50 sit in NE21+NE23, used by H04's confirmatory run (branching ratio, kernels, FD; its superposition
test was exploratory and non-holdout). H43's statistic (second-kick marginal effect vs read-out spacing at the receiving
call) differs from both and has not been examined on these periods. Disclose the reuse in this card, the H02 and H04
cards and LOG.md before running.

Stand-ins for the dry run (non-holdout): C1-C3 -> #51 days 2026-08-24 .. 09-04 (after NE43, like the tail);
C4 -> G38, G41, G42, G44 (regime-III nudge periods); C5 -> G04 (4a, 4c), G05, G06 (regime-I human periods).
Usage:  uv run python hypotheses/H43-kick-refractory-window/analysis/confirm.py                    (dry run)
        uv run python hypotheses/H43-kick-refractory-window/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import h43lib as L  # noqa: E402

TARGETS = {
    "tail": {"goals": [51], "date_from": "2026-09-07", "date_to": "2026-09-21"},
    "nudge": {"goals": [45, 46, 47, 48, 49, 50]},
    "human": {"goals": [1, 9, 14, 15]},
}
STANDINS = {
    "tail": {"goals": [51], "date_from": "2026-08-24", "date_to": "2026-09-05"},
    "nudge": {"goals": [38, 41, 42, 44]},
    "human": {"goals": [4, 5, 6], "units": ["4a", "4c", "5", "6a", "6b"]},
}


def load_frames(spec: dict, holdout: bool):
    """Calls / states / writes / calendar for a target or stand-in. Held-out rows only when holdout=True."""
    if holdout:
        import build as B
        calls, _ = B.calls_frame(include_holdout=True, goal_nos=spec["goals"])
        writes = B.writes_frame(include_holdout=True)
    else:
        calls = pl.read_parquet(L.OUT / "calls.parquet").filter(pl.col("goal_no").is_in(spec["goals"]))
        writes = pl.read_parquet(L.OUT / "writes.parquet")
    if spec.get("date_from"):
        calls = calls.filter(pl.col("pt_date") >= spec["date_from"])
    if spec.get("date_to"):
        calls = calls.filter(pl.col("pt_date") < spec["date_to"])
    if spec.get("units"):
        calls = calls.filter(pl.col("unit_id").is_in(spec["units"]) | ~pl.col("goal_no").is_in([4, 5, 6]))
    days = sorted(calls["pt_date"].unique().to_list())
    if not holdout:
        assert not any(L.is_holdout(d, g) for d, g in calls.select("pt_date", "goal_no").unique().iter_rows()), \
            "dry run touched a held-out day"
    hcol = pl.col("holdout") if holdout else ~pl.col("holdout")
    states = (pl.scan_parquet(L.SH / "states_min.parquet").filter(pl.col("pt_date").is_in(days) & hcol)
              .select("pt_date", "minute", "agent", "lump4_min", "in_span", "present").collect())
    writes = writes.filter(pl.col("pt_date").is_in(days)).select("agent", "t")
    cal = (pl.read_parquet(L.SH / "calendar.parquet").filter(pl.col("pt_date").is_in(days))
           .select("pt_date", (pl.col("win_start").dt.epoch("us") / 1e6).alias("win_start"),
                   (pl.col("win_end").dt.epoch("us") / 1e6).alias("win_end")))
    return calls, states, writes, cal


def get(od, *path):
    for p in path:
        if od is None:
            return None
        od = od.get(p) if isinstance(od, dict) else None
    return od


def score_tail(P, rng, B):
    res = L.analyze_class(P, "A", rng, B=B, outcomes=("O2", "O2c"))
    oc, o2 = res["outcomes"].get("O2c", {}), res["outcomes"].get("O2", {})
    out = {"n_primers": get(oc, "E1", "n"), "E1_O2c": oc.get("E1"), "R_pool_O2c": oc.get("R_pool"),
           "batched_O2c": oc.get("batched"), "fit_O2c": oc.get("fit"), "in_O2": get(o2, "by_status", "in")}
    e1 = oc.get("E1") or {}
    r15 = get(oc, "R_pool", "0-15", "R") or {}
    r60 = get(oc, "R_pool", "60-240", "R") or {}
    db = get(oc, "fit", "draw_bins") or {}
    tot = sum(db.values())
    share = (db.get("none", 0) + db.get("0-2", 0)) / tot if tot else None
    c1 = None
    if e1.get("lo") is not None and r15.get("est") is not None:
        c1 = bool(e1["lo"] > 0 and 0.5 <= r15["est"] <= 1.1 and (r15.get("lo") or -9) > 0.3
                  and (r60.get("est") is None or r60["est"] >= 0.7) and (share is None or share >= 0.8))
    bt = get(oc, "batched", "R", "est")
    c2 = None if bt is None else bool(bt <= 0.5)
    rin = get(o2, "by_status", "in", "R", "est")
    c3 = None if rin is None else bool(rin >= 0.4)
    out.update({"share_window_lt_2min": share, "C1": c1, "C2": c2, "C3": c3})
    return out


def score_nudge(P, rng, B):
    res = L.analyze_class(P, "N", rng, B=B, outcomes=("O1", "O1a"))
    o1, o1a = res["outcomes"].get("O1", {}), res["outcomes"].get("O1a", {})
    n = get(o1a, "E1", "n") or 0
    out = {"n_idle_primers": n, "E1_O1": o1.get("E1"), "E1_O1a": o1a.get("E1"), "R_pool_O1a": o1a.get("R_pool")}
    if n < 50:
        out["C4"] = None
        out["why"] = "fewer than 50 idle nudge primers"
        return out
    r = get(o1a, "R_pool", "15-60", "R", "est")
    out["C4"] = bool((get(o1a, "E1", "lo") or -9) > 0 and (get(o1, "E1", "est") or 9) < 0.3 and r is not None and r >= 0.7)
    return out


def score_human(P, rng, B):
    D = L.build_design(P, "H", quiet_s=300)
    out = {"n_primers": int(len(D.get("primer", [])))}
    if not len(D.get("primer", [])):
        out["C5"] = None
        return out
    C = L.day_draws(len(P.days), B, rng)
    e1 = L.e1_table(P, D, "O2c", C)
    out["E1_O2c"] = e1["summary"]
    if e1["summary"]["n"] < 50 or "sec" not in D:
        out["C5"] = None
        out["why"] = "fewer than 50 busy human primers"
        return out
    r, _ = L.ratio_for(P, D, "O2c", (D["d_t"] > 0) & (D["d_t"] <= 2), e1, C)
    out["R_0_2_O2c"] = r
    out["C5"] = bool(e1["summary"]["lo"] > 0 and get(r, "R", "est") is not None and r["R"]["est"] >= 0.7)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    ap.add_argument("--B", type=int, default=L.B_BOOT)
    a = ap.parse_args()
    holdout = bool(a.confirm and a.ack)
    if (a.confirm or a.ack) and not holdout:
        sys.exit("refusing: the confirmatory run needs BOTH --confirm and --i-understand-this-uses-the-locked-holdout")
    if holdout:
        dirty = subprocess.run(["git", "-C", str(L.ROOT), "status", "--porcelain", "hypotheses/H43-kick-refractory-window"],
                               capture_output=True, text=True).stdout.strip()
        if dirty:
            sys.exit("refusing: commit the H43 card and scripts before the confirmatory run (holdout reuse policy, "
                     "condition 1). Uncommitted:\n" + dirty)
        print("CONFIRMATORY RUN on the locked holdout. Reuse disclosure: #45 (H02), #46-#50 in NE21+NE23 (H04); "
              "H43's statistic differs and was not examined there.")
    specs = TARGETS if holdout else STANDINS
    rng = np.random.default_rng(L.SEED + 9999)
    t0 = time.time()
    out = {"mode": "confirm" if holdout else "dry_run (non-holdout stand-ins)", "specs": specs,
           "git_commit": L.git_commit(), "built_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    calls, states, writes, cal = load_frames(specs["tail"], holdout)
    out["tail"] = score_tail(L.Prep(calls, states, writes, cal), rng, a.B)
    calls, states, writes, cal = load_frames(specs["nudge"], holdout)
    out["nudge_pooled"] = score_nudge(L.Prep(calls, states, writes, cal), rng, a.B)
    out["nudge_per_period"] = {}
    for g in specs["nudge"]["goals"]:
        sub = calls.filter(pl.col("goal_no") == g)
        if sub.height == 0:
            continue
        d = sub["pt_date"].unique().to_list()
        out["nudge_per_period"][f"G{g:02d}"] = score_nudge(
            L.Prep(sub, states.filter(pl.col("pt_date").is_in(d)), writes, cal.filter(pl.col("pt_date").is_in(d))), rng, a.B)
    calls, states, writes, cal = load_frames(specs["human"], holdout)
    out["human_pooled"] = score_human(L.Prep(calls, states, writes, cal), rng, a.B)
    sc = {"C1": out["tail"]["C1"], "C2": out["tail"]["C2"], "C3": out["tail"]["C3"],
          "C4": out["nudge_pooled"]["C4"], "C5": out["human_pooled"]["C5"]}
    scored = {k: v for k, v in sc.items() if v is not None}
    overall = bool(sc["C1"] and sc["C2"] and (sc["C4"] or sc["C5"]) and all(scored.values()))
    out["scores"] = {k: ("n/a" if v is None else ("pass" if v else "fail")) for k, v in sc.items()}
    out["overall_no_window_confirmed"] = overall
    out["secs"] = round(time.time() - t0, 1)
    dest = L.OUT / ("confirm" if holdout else "confirm_dryrun") / "confirm_results.json"
    L.jdump(out, dest)
    print(out["mode"], out["scores"], "overall:", overall, f"({out['secs']} s) ->", dest)


if __name__ == "__main__":
    main()
