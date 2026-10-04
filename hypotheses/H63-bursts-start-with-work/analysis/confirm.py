"""H63 confirmatory run on the LOCKED HOLDOUT. Written and frozen 2026-10-04 after round 1; NOT RUN.

Guard: runs on held-out data only with BOTH `--confirm` and H63_CONFIRM=1, and only if `holdout_ledger.check` allows
every target. `--dry-run` runs the identical pipeline on non-holdout stand-in periods (#38, #41, #44) and writes to a
scratch directory.

Targets: #43 (regime III), the #51 tail (2026-09-07 -> 09-21), #45 (regime III, two rooms).

Frozen predictions (round-1 estimators and thresholds; trimmed window; 60-min windows; Haldane 0.5):
  C1  Original claim: pooled Mantel-Haenszel OR_S (a deploy-type state change in the 60 min before the follower onset,
      herding bursts vs 1-2-agent clusters) >= 2 with 95% CI excluding 1. Round 1 predicts this FAILS (claim refuted).
  C2  Links precede bursts: pooled OR_L > 3 with 95% CI lower bound > 1.
  C3  No work lead: random-effects pooled h_S - h_S' (arrival hazard, agent + project + day fields) has a 95% CI
      including 0.
  C4  (post hoc pattern from round 1, flagged) In the trimmed window links lead arrivals: pooled kappa - kappa' > 0.
  C5  At most 10% of herding bursts have a state change in the 60 min before the follower onset.
Reading: C1 failing with C2, C3 and C5 holding confirms "herding bursts are not started by artifact state changes;
links come first".

Reuse policy (hypotheses/holdout.md): planned users of #43 / #51 tail / #45 for project or artifact statistics include
H01, H15, H27, H34, H37 (#51 tail) and H11, H28 (#45 project labels); H02 and H04 ran activity statistics on #45.
H63's statistics (burst precedence of DQ4 work signals, arrival hazard lead-lag with work terms) are different
statistics. H28's #45 link hazard overlaps C2/C4 in family (link_contagion): if H28 runs first, disclose C2/C4 as
second uses. Disclose in the card and LOG.md before running.

Usage:
  uv run python hypotheses/H63-bursts-start-with-work/analysis/confirm.py --dry-run
  H63_CONFIRM=1 uv run python hypotheses/H63-bursts-start-with-work/analysis/confirm.py --confirm
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
import h63lib as L  # noqa: E402

ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
OUT = ROOT / "data/processed/H63-bursts-start-with-work/confirm"
SCRATCH = Path(os.environ.get("TMPDIR", "/tmp")) / "h63_confirm_dryrun"
TARGETS = {43: None, 51: ("2026-09-07", "2026-09-21"), 45: None}
STANDINS = [38, 41, 44]
FROZEN = dict(C1=dict(OR=2.0), C2=dict(OR=3.0), C5=dict(share=0.10))


def period_stats(g, root):
    P = L.load(g, root)
    aa = L.arrivals(P, trim=False)
    cl = L.clusters(aa.filter(pl.col("trim")), aa)
    pre = L.precedence(P, cl)
    out = {"goal_no": g, "tab_S": L.table(pre, "S_pre"), "tab_L": L.table(pre, "L_pre")}
    D, _ = L.risk_panel(P, trim=True)
    if D is not None:
        h = L.hazard(D, B=50, seed=g)
        out.update({k: h.get(k) for k in ("dS", "dS_se", "dL", "dL_se", "n_events")})
    return out


def score(res):
    o = {}
    s = L.mh_or([r["tab_S"] for r in res])
    lk = L.mh_or([r["tab_L"] for r in res])
    o["C1"] = bool(s["or"] >= FROZEN["C1"]["OR"] and s["lo"] > 1)
    o["C1_detail"] = s
    o["C2"] = bool(lk["or"] > FROZEN["C2"]["OR"] and lk["lo"] > 1)
    o["C2_detail"] = lk
    hs = [r for r in res if r.get("dS_se")]
    pS = L.re_pool([r["dS"] for r in hs], [r["dS_se"] for r in hs])
    pL = L.re_pool([r["dL"] for r in hs], [r["dL_se"] for r in hs])
    o["C3"] = bool(pS["lo"] <= 0 <= pS["hi"]) if pS["k"] else None
    o["C3_detail"] = pS
    o["C4"] = bool(pL["mean"] > 0) if pL["k"] else None
    o["C4_detail"] = pL
    nb = sum(sum(r["tab_S"][0]) for r in res)
    o["C5_share"] = sum(r["tab_S"][0][0] for r in res) / max(nb, 1)
    o["C5"] = bool(o["C5_share"] <= FROZEN["C5"]["share"])
    o["n_bursts"] = nb
    return o


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    if a.dry_run:
        out = score([period_stats(g, L.OUT) for g in STANDINS])
        SCRATCH.mkdir(parents=True, exist_ok=True)
        (SCRATCH / "dryrun.json").write_text(json.dumps({"sha256": sha, **out}, indent=1, default=float))
        print(json.dumps(out, indent=1, default=float))
        return
    if not (a.confirm and os.environ.get("H63_CONFIRM") == "1"):
        sys.exit("refusing: confirmatory run needs --confirm and H63_CONFIRM=1 (Vivian's sign-off)")
    import holdout_ledger as HL
    from project_states import project_map
    for g in TARGETS:
        tgt = "#51-tail" if g == 51 else f"G{g}"
        chk = HL.check("H63", tgt, "project", ["project_potts", "artifact_lineage"])
        if not chk["allowed"]:
            sys.exit(f"refusing: holdout ledger blocks {tgt}: {chk['prior_runs_same_family']}")
    cal, am, sig, cw, kc = B.prepare(allow_holdout=True)
    pm = project_map()
    res = []
    for g, win in TARGETS.items():
        days = None
        if win:
            days = cal.filter((pl.col("goal_no") == g) & (pl.col("pt_date") >= win[0]) & (pl.col("pt_date") < win[1]))[
                "pt_date"].to_list()
        if B.build_goal(g, cal, am, sig, cw, kc, pm, out_root=OUT, allow_holdout=True, days_filter=days):
            res.append(period_stats(g, OUT))
    out = score(res)
    (OUT / "confirm_result.json").write_text(json.dumps({"sha256": sha, **out, "periods": res}, indent=1, default=float))
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
