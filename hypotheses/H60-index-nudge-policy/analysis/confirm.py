"""H60 confirmatory test on the LOCKED HOLDOUT. Written and frozen 2026-10-04 after exploratory round 1; NOT RUN.

Refuses to touch held-out data unless called with BOTH flags
    --confirm --i-understand-this-uses-the-locked-holdout
and refuses if hypotheses/H60-index-nudge-policy/ or infra/shared/idle_gates.py has uncommitted changes. It prints the
holdout-ledger reuse check for each target. Without the flags it runs a DRY RUN on non-holdout stand-ins and writes
data/processed/H60-index-nudge-policy/confirm_dryrun/confirm_results.json.

HH252 asked for "the #51 tail before 08-20"; that window does not exist (the held-out tail starts 09-07, after the
nudger stopped on 08-20). The short-pause, nudger-on held-out periods are #47-#50 (inside NE21+NE23; the nudger was
off 06-13 -> 06-15, NE23, and those days carry no nudges). #45 is long-pause (before NE44).

Frozen predictions (same estimator as analysis/run_period.py: cross-fitted direct method on day halves, agent-FE
outcome model, logged budget; per period, never pooled):
  C1  #47-#50, active calls in 30 min: once-early (k_sus = 2) beats the logged nudger, ratio point > 1, in >= 3 of the
      eligible periods (eligible: >= 30 nudged gates); n/a if < 2 eligible.                                [primary]
  C2  #47-#50, active calls: random gate choice is at least as good as the logged nudger, ratio point >= 1, in >= 3 of
      the eligible periods.                                                                                   [primary]
  C3  #47-#50, active calls: the index does not beat once-early: V(index)/V(once-early) point <= 1.25 in every
      eligible period.                                                                                         [primary]
  C4  #47-#50, sustained escape: V(index)/V(logged) point > 1 in >= 3 eligible periods (possibly selection).  [secondary]
  C5  #45, active calls: the nudge effect at the mean nudged state theta_0 > 0 (bootstrap CI above 0).         [secondary]
Overall: "an index does not beat once-early; the logged nudger is no better than random" is confirmed if no primary C
fails and >= 1 passes.

Reuse: #45 (H02, H35 planned), #46-#50 (H04 run; H35, H43 planned) - the H35 plan (C3 "once at k* = 2 beats the
logged nudger") overlaps C1 in substance: coordinate with H35's run (one test, not two) and disclose in LOG.md.
Stand-ins (dry run): #47..#50 -> G51 weeks 07-06..07-10, 07-13..07-17, 07-20..07-24, 07-27..07-31; #45 -> G38.
Usage:  uv run python hypotheses/H60-index-nudge-policy/analysis/confirm.py                  (dry run)
        uv run python hypotheses/H60-index-nudge-policy/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h60lib as L  # noqa: E402

ROOT = L.ROOT
sys.path.insert(0, str(ROOT / "infra/shared"))
TARGETS = {"short": [{"goals": [g]} for g in (47, 48, 49, 50)], "long": {"goals": [45]}}
STANDINS = {"short": [{"goals": [51], "from": a, "to": b} for a, b in
                      (("2026-07-06", "2026-07-10"), ("2026-07-13", "2026-07-17"), ("2026-07-20", "2026-07-24"),
                       ("2026-07-27", "2026-07-31"))], "long": {"goals": [38]}}
MIN_NUDGED = 30


def frames(spec, holdout):
    if holdout:
        import idle_gates as IG
        from common import holdout_mask
        g = IG.build(include_holdout=True, goal_nos=spec["goals"])
        g = g.filter(pl.Series(holdout_mask(g["pt_date"].to_list(), g["goal_no"].to_list())))
        g = g.sort("agent", "pt_date", "t_call").with_columns((pl.col("n_nudge_me") > 0).alias("nudged"))
    else:
        g = pl.read_parquet(L.OUT / "gates.parquet").filter(pl.col("goal_no").is_in(spec["goals"]) & pl.col("nudger_on"))
    if spec.get("from"):
        g = g.filter(pl.col("pt_date").is_between(pl.lit(spec["from"]), pl.lit(spec["to"])))
    return g.filter(pl.col("regime") == "III")


def policy(df, oc, B):
    P = L.prep(df, oc)
    r = {"n": P["n"], "nudged": int(P["M"].sum())}
    if r["nudged"] < MIN_NUDGED:
        r["eligible"] = False
        return r
    cf = L.crossfit(P)
    r.update({"eligible": True, "values": {p: float(cf[p]) for p in L.POL}, "ratios": L.ratios(cf)})
    return r


def run(holdout, B):
    S = TARGETS if holdout else STANDINS
    res = {"mode": "CONFIRM" if holdout else "dry run (stand-ins, not evidence)", "short": []}
    for spec in S["short"]:
        df = frames(spec, holdout)
        res["short"].append({"spec": spec, "calls30": policy(df, "calls30", B), "sus": policy(df, "sus", B)})
    el = [x for x in res["short"] if x["calls30"].get("eligible")]
    if len(el) < 2:
        res["C1"] = res["C2"] = res["C3"] = res["C4"] = "n/a"
    else:
        need = min(3, len(el))
        res["C1"] = "pass" if sum(x["calls30"]["ratios"]["once_early/logged"] > 1 for x in el) >= need else "fail"
        res["C2"] = "pass" if sum(x["calls30"]["ratios"]["random/logged"] >= 1 for x in el) >= need else "fail"
        res["C3"] = "pass" if all(x["calls30"]["ratios"]["index/once_early"] <= 1.25 for x in el) else "fail"
        els = [x for x in el if x["sus"].get("eligible")]
        res["C4"] = "n/a" if len(els) < 2 else (
            "pass" if sum(x["sus"]["ratios"]["index/logged"] > 1 for x in els) >= min(3, len(els)) else "fail")
    P = L.prep(frames(S["long"], holdout), "calls30")
    if P["M"].sum() >= 15:
        h = L.heterogeneity(P, B=B, seed=45)
        res["long"] = {"theta0": h["theta"]["M"], "ci": h["theta_ci"]["M"], "nudged": int(P["M"].sum())}
        res["C5"] = "pass" if h["theta_ci"]["M"][0] > 0 else "fail"
    else:
        res["C5"] = "n/a"
    prim = [res["C1"], res["C2"], res["C3"]]
    res["overall"] = "confirmed" if ("fail" not in prim and "pass" in prim) else ("not confirmed" if "fail" in prim else "n/a")
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    a = ap.parse_args()
    if a.confirm or a.ack:
        if not (a.confirm and a.ack):
            sys.exit("both --confirm and --i-understand-this-uses-the-locked-holdout are required")
        dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "--", "hypotheses/H60-index-nudge-policy",
                                "infra/shared/idle_gates.py"], capture_output=True, text=True).stdout.strip()
        if dirty:
            sys.exit("refusing: uncommitted changes in the H60 folder or idle_gates.py\n" + dirty)
        import holdout_ledger as HL
        for tgt in ("G45", "G47", "G48", "G49", "G50"):
            print(tgt, HL.check("H60", tgt, "activity", ["kick_response"]))
        res, od = run(True, 200), L.OUT / "confirm"
    else:
        res, od = run(False, 50), L.OUT / "confirm_dryrun"
    od.mkdir(parents=True, exist_ok=True)
    (od / "confirm_results.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps({k: v for k, v in res.items() if k.startswith("C") or k in ("mode", "overall")}))


if __name__ == "__main__":
    main()
