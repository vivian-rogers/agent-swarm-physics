"""H36 round 1b native tests (2026-10-04): blind detection of the corrected / undocumented step changes.

Targets (predictions in goalperiod-subhypotheses/{NE39,NE40,NE43,NE45}/README.md, written before this ran):
  NE39  2025-07-01 public chat closed (#6)          NE40  2026-04-20 search answerer swap (with NE18; #38)
  NE43a 2026-08-05 bookends stop (+ #focus opens)    NE43b 2026-08-21 nudger off (#51)
  NE45  2026-07-29 search tool schema (+ NE38; #51)
For each target and score (Z_phys, Z_act, Z_act_trim, Z_cont, R1, C3):
  - hit: score >= 2.0 on day -1, 0 or +1 (C3 is encoded so that >= 2.0 <=> R1 >= 3 or Z_cont >= 2);
  - blind dating: candidate days = the goal period's scored days, minus days within +-1 of every OTHER catalogued
    event (goal kickoffs, rooms, scaffold, roster, operator, other r1b targets); the day with the largest score among
    candidates plus the target window: is it inside -1..+1? and the percentile of the target-window max among the
    candidates' daily scores.
Reads data/processed/H36-reorganization-alarm/r1b/<TAG>/{scores,events}.parquet; writes native.json there.

Usage: uv run python hypotheses/H36-reorganization-alarm/analysis/r1b_native.py --r1b fixed_bge_restate
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h36lib as L  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

TARGETS = {"NE39": ["NE39"], "NE40": ["NE40", "NE18"], "NE43a": ["NE43a", "NE-focus"], "NE43b": ["NE43b"],
           "NE45": ["NE45", "NE38"]}
SCORES = ["Z_phys", "Z_act", "Z_act_trim", "Z_cont", "R1", "C3"]
PRIMARY = ["goal", "room", "scaffold", "roster", "operator", "r1b"]


def run(tag: str) -> dict:
    d = L.OUT / "r1b" / tag
    sc = pl.read_parquet(d / "scores.parquet").sort("aday")
    ev = pl.read_parquet(d / "events.parquet").filter(pl.col("cls").is_in(PRIMARY))
    adays = sc["aday"].to_numpy()
    goal = dict(zip(sc["aday"].to_list(), sc["goal_no"].to_list()))
    out = {}
    for tgt, same in TARGETS.items():
        r = ev.filter(pl.col("ref") == tgt)
        if r.height == 0 or r["holdout0"][0]:
            out[tgt] = {"note": "not scored (held out or missing)"}
            continue
        a0 = int(r["aday0"][0]); g = goal.get(a0)
        if g is None:   # day 0 not scored (fewer than 3 present agents): use the nearest scored day's goal
            g = goal.get(min(goal, key=lambda x: abs(x - a0)))
        others = ev.filter(~pl.col("ref").is_in(same) & (pl.col("aday0") != a0))["aday0"].drop_nulls().to_numpy()
        inper = np.array([goal.get(int(x)) == g for x in adays])
        near_other = np.array([np.any(np.abs(others - x) <= 1) for x in adays]) if others.size else np.zeros(adays.size, bool)
        win = np.isin(adays, [a0 - 1, a0, a0 + 1])
        cand = inper & ~near_other & ~win
        rec = {"day0": r["pt_date0"][0], "goal_no": int(g), "same_day_refs": r["all_refs_same_day_r1b"][0]
               if "all_refs_same_day_r1b" in r.columns else None, "n_candidates": int(cand.sum())}
        for k in SCORES:
            v = sc[k].to_numpy().astype(float)
            wv = {o: (float(v[adays == a0 + o][0]) if np.any(adays == a0 + o) and np.isfinite(v[adays == a0 + o][0]) else None)
                  for o in (-1, 0, 1)}
            fin = [x for x in wv.values() if x is not None]
            wmax = max(fin) if fin else None
            cv = v[cand]; cv = cv[np.isfinite(cv)]
            pool = np.r_[cv, [wmax]] if wmax is not None else cv
            rec[k] = {"d-1": wv[-1], "d0": wv[0], "d+1": wv[1], "hit": (wmax is not None and wmax >= L.THRESH),
                      "top_in_window": bool(wmax is not None and cv.size and wmax >= np.max(pool)),
                      "pct_vs_candidates": float(np.mean(cv < wmax)) if (wmax is not None and cv.size) else None,
                      "n_cand_scored": int(cv.size)}
        out[tgt] = rec
    (d / "native.json").write_text(json.dumps(out, indent=1))
    return out


def fmt(x):
    return "–" if x is None else f"{x:.2f}"


def main():
    tag = sys.argv[sys.argv.index("--r1b") + 1]
    out = run(tag)
    for t, rec in out.items():
        if "note" in rec:
            print(t, rec["note"]); continue
        print(f"\n{t} day0 {rec['day0']} (#{rec['goal_no']}; same day {rec['same_day_refs']}; candidates {rec['n_candidates']})")
        for k in SCORES:
            x = rec[k]
            print(f"  {k:11s} {fmt(x['d-1'])} / {fmt(x['d0'])} / {fmt(x['d+1'])}  hit {x['hit']}  top {x['top_in_window']}  "
                  f"pct {fmt(x['pct_vs_candidates'])} (n {x['n_cand_scored']})")


if __name__ == "__main__":
    main()
