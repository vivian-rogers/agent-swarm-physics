"""H79 CONFIRMATORY test on the LOCKED HOLDOUT. Written 2026-10-04 after exploratory round 1. NOT RUN.

Refuses to read any holdout day unless BOTH flags are given:
    --confirm --i-understand-this-uses-the-locked-holdout
`--dry-run` computes the identical statistics on non-holdout stand-ins (G41, G51); no holdout day is read.

Frozen criteria (machine-readable in PREDICTIONS; the claims that stand after round 1):
  Units: #46, #47, #48, #49, #50 (NE21+NE23 window, automation-dense) and the #51 tail (2026-09-07 -> 09-18).
  Eligible: >= 1,000 agent work commits (C1, C4, C5) or >= 1 automated stream-day (C2).
  C1  No collective catalytic set: in every eligible unit, the number of simple catalytic cycles of length >= 3 among
      reactions backed by >= 3 events is not above the rewired null (p_high >= 0.05, 100 draws, cross edges only).
  C2  First-order catalysis: self-catalysed reactions carry >= 80% of maxRAF commits (automated included) in every
      eligible unit. (Round 1: 0.85-0.99.)
  C3  Execution follows writes: executions-before / executions-after catalysed-coverage ratio < 1 (point estimate) in
      >= 2/3 of eligible units. (Round 1: 0.74-0.89, 5/5.)
  C4  No artifact layer: in-period tools catalysing other repos carry <= 5% of agent work commits in >= 2/3 of
      eligible units. (Round 1: 3/4 replication periods; G31 0.21.)
  C5  Topology adds nothing to coverage: |maxRAF coverage - rewired-null mean coverage| <= 0.01 in every eligible unit.
  Supported if C1, C2 and C5 hold and at least one of C3/C4; failed if C1 fails in any unit (a collective set).

Holdout reuse: #46-#50 and the #51 tail are targeted by many scripts (activity, content, kicks, H58's work-ledger
allocation state). This script uses work ledger x executed-artifact catalysis graphs, a statistic no run has computed.
holdout_ledger.check() is called before reading; disclose in the card and LOG.md and commit the script first.

Run:   uv run python hypotheses/H79-artifact-autocatalytic-set/analysis/confirm.py --dry-run
Real:  ... --confirm --i-understand-this-uses-the-locked-holdout     (only after Vivian signs off)
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ[_v] = "2"

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "infra/shared"))
import raflib as RL  # noqa: E402

D = ROOT / "data/processed/H79-artifact-autocatalytic-set"
CONF = D / "confirm"
PREDICTIONS = {
    "C1": "support>=3 cycles of length>=3 not above rewired null (p_high >= 0.05) in every eligible unit",
    "C2": "self-catalysed share of maxRAF commits (automated included) >= 0.80 in every eligible unit",
    "C3": "exec-before / exec-after catalysed coverage ratio < 1 in >= 2/3 of eligible units",
    "C4": "in-period tool share of agent work commits <= 0.05 in >= 2/3 of eligible units",
    "C5": "|maxRAF coverage - rewired-null mean coverage| <= 0.01 in every eligible unit",
}
HOLDOUT_UNITS = [("G46", 46, None), ("G47", 47, None), ("G48", 48, None), ("G49", 49, None), ("G50", 50, None),
                 ("51-tail", 51, "2026-09-07")]
STANDINS = [("G41", 41, None), ("G51", 51, None)]
N_NULL = 100


def unit_events(path: Path, goal: int, since: str | None):
    ev = pl.read_parquet(path / "events.parquet").filter(pl.col("goal_no") == goal)
    if since:
        ev = ev.filter(pl.col("pt_date") >= since)
    events = [{"eid": r["event_id"], "product": r["product"], "cat": r["cat"] or [], "cat_rev": r["cat_rev"] or [],
               "reads": r["reads"] or [], "n_commits": r["n_commits"], "t_first": r["t_first"].timestamp(),
               "kind": r["kind"], "day": r["pt_date"]} for r in ev.iter_rows(named=True)]
    if since:     # food = artifacts first seen before the unit's first day (+ operator-named, as in the scheme)
        sp = pl.read_parquet(path / "species.parquet")
        t0 = dt.datetime.fromisoformat(since).replace(tzinfo=dt.timezone.utc)
        food = set(sp.filter(pl.col("first_t") < t0)["artifact"].to_list())
        food |= set(pl.read_parquet(path / "food.parquet").filter(
            (pl.col("goal_no") == goal) & (pl.col("why") == "operator_named"))["artifact"].to_list())
    else:
        food = set(pl.read_parquet(path / "food.parquet").filter(pl.col("goal_no") == goal)["artifact"].to_list())
    return events, food


def n3(c):
    return sum(v for k, v in c["by_len"].items() if k >= 3)


def stats(events, food, seed=0):
    rng = np.random.default_rng(seed)
    s = RL.summarize(events, food)
    null_n3, null_cov = [], []
    for _ in range(N_NULL):
        z = RL.summarize(RL.rewire(events, rng), food)
        null_n3.append(n3(z["cycles_support3"]))
        null_cov.append(z["coverage"])
    ag = [e for e in events if e["kind"] != "auto"]
    before = sum(e["n_commits"] for e in ag if e["cat"])
    after = sum(e["n_commits"] for e in ag if e["cat_rev"])
    return {"work_commits": s["work_commits"], "auto_commits": s["auto_commits"],
            "n3_support3": n3(s["cycles_support3"]),
            "p_high": (1 + sum(x >= n3(s["cycles_support3"]) for x in null_n3)) / (1 + N_NULL),
            "self_share_all": s["self_share_of_raf_commits_all"], "time_ratio": before / after if after else float("nan"),
            "inperiod_tool_share": s["inperiod_tool_share_work"], "coverage": s["coverage"],
            "null_coverage": float(np.mean(null_cov))}


def evaluate(res: dict) -> dict:
    el = {u: r for u, r in res.items() if r["work_commits"] >= 1000}
    el2 = {u: r for u, r in res.items() if r["auto_commits"] > 0 or r["work_commits"] >= 1000}
    c = {"C1": all(r["p_high"] >= 0.05 for r in el.values()),
         "C2": all((r["self_share_all"] or 0) >= 0.80 for r in el2.values()),
         "C3": np.mean([r["time_ratio"] < 1 for r in el.values()]) >= 2 / 3 if el else None,
         "C4": np.mean([r["inperiod_tool_share"] <= 0.05 for r in el.values()]) >= 2 / 3 if el else None,
         "C5": all(abs(r["coverage"] - r["null_coverage"]) <= 0.01 for r in el.values())}
    c = {k: (None if v is None else bool(v)) for k, v in c.items()}
    c["eligible_units"] = sorted(el)
    c["verdict"] = ("failed" if c["C1"] is False else
                    "supported" if (c["C1"] and c["C2"] and c["C5"] and (c["C3"] or c["C4"])) else "mixed")
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    a = ap.parse_args()
    if a.dry_run:
        res = {u: stats(*unit_events(D, g, s)) for u, g, s in STANDINS}
        print(json.dumps({"DRY_RUN_on_non_holdout_standins": res, "criteria": evaluate(res)}, indent=1, default=float))
        return
    if not (a.confirm and a.ack):
        sys.exit("Refusing: this script reads the locked holdout. Pass --dry-run, or both --confirm and "
                 "--i-understand-this-uses-the-locked-holdout after sign-off.")
    import holdout_ledger as HL
    for u, _g, _s in HOLDOUT_UNITS:
        tgt = "#51-tail" if u == "51-tail" else u
        print(u, HL.check("H79", tgt, "work ledger x executed-artifact catalysis", None))
    sys.path.insert(0, str(HERE.parent / "scheme"))
    import build as B   # the round-1 scheme, unchanged, with the guarded holdout switch
    B.main(periods=[46, 47, 48, 49, 50, 51], allow_holdout=True, outd=CONF)
    res = {u: stats(*unit_events(CONF, g, s)) for u, g, s in HOLDOUT_UNITS}
    out = {"run_at": dt.datetime.now(dt.timezone.utc).isoformat(), "predictions": PREDICTIONS, "units": res,
           "criteria": evaluate(res)}
    (CONF / "confirm_result.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
