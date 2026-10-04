"""H95 confirmatory tests on the LOCKED HOLDOUT. Written after exploratory round 1 (2026-10-04); NOT RUN.

Guard: the holdout is touched only with BOTH flags, a clean git state for H95's code, and a holdout-ledger check:
  uv run python hypotheses/H95-slack-specificity-gauge/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
Without the flags the script prints the frozen predictions and exits.

Targets: the held-out regime-III kickoffs #45, #46, #47, #49 (whole-period units, W_null start, horizon min(20 h, period)).
#50 is excluded: its code hosting moved to GitLab (CHANGELOG I), so DQ4 commits may not cover it. #43 and #48 are 1-day.
  C1  (pre-registered gauge, expected underpowered) Spearman rho(S, x) <= -0.5 over the four units.
  C2  (post-hoc design code, amendment A2, frozen here) every held-out kickoff is coded d = 0 from its goal title
      (#45 follow your leader; #46 organise an event / surprise each other; #47 reduce global suffering / play games;
      #49 beat the hardest game you can): none assigns a concrete artifact to build. Prediction: S >= 2.5 or
      T_e >= 2 active h in >= 3 of the 4 units. Disclosure: the goal-periods.md setup lines (read 2026-10-04 while
      coding) say #47 #best had a Help Kit live within 11 minutes, which hints at a fast freeze in that room.
Reuse: #45-#47 and #49 are planned or used by H75 (same slack statistic; the ledger has no slack family yet, so "other" is passed), H02, H04, H30, H35, H40.
H75's confirm uses the same estimator on #45-#47: the ledger check below decides; the coordinator must order the runs.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h95lib as L  # noqa: E402
import build as B  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))

FROZEN = {  # frozen 2026-10-04 after exploratory round 1 (card, "Confirmatory predictions")
    "goals": [45, 46, 47, 49], "variant": "null", "horizon_cap_h": 20.0, "day1_h": 4.0,
    "C1_rho_max": -0.5,
    "C2_design_code": {45: 0, 46: 0, 47: 0, 49: 0}, "C2_S_min": 2.5, "C2_T_min_h": 2.0, "C2_min_units": 3,
}
FILES = ["hypotheses/H95-slack-specificity-gauge/analysis/confirm.py",
         "hypotheses/H95-slack-specificity-gauge/analysis/h95lib.py",
         "hypotheses/H95-slack-specificity-gauge/scheme/build.py"]


def git_clean() -> bool:
    out = subprocess.run(["git", "-C", str(L.ROOT), "status", "--porcelain", "--", *FILES], capture_output=True, text=True).stdout
    return out.strip() == ""


def run():
    import holdout_ledger as HL
    for g in FROZEN["goals"]:
        chk = HL.check("H95", f"G{g}", "work_commits", "other")   # no slack family in the ledger yet; H75 is unregistered
        print(g, "allowed" if chk["allowed"] else "NOT ALLOWED", "disclosure needed" if chk["needs_disclosure"] else "")
        if not chk["allowed"]:
            raise SystemExit("holdout ledger refuses a same-family reuse: ask the coordinator")
    res = {}
    for g in FROZEN["goals"]:
        clk = B.clock(g, allow_holdout=True)
        H = B.horizon(clk, FROZEN["horizon_cap_h"])
        E = B.ensemble(g, FROZEN["variant"], H, clk, allow_holdout=True)
        named = B.named_codes(g, B.repo_list(g, clk, allow_holdout=True))
        s = L.settle_stats(E)
        res[g] = {"N": len(E.agents), "H": H, "x": L.specificity(E, named, FROZEN["day1_h"]), "S_e": s["S_e"], "T_e": s["T_e"]}
    rho = L.spearman([res[g]["x"] for g in res], [res[g]["S_e"] for g in res])
    c1 = np.isfinite(rho) and rho <= FROZEN["C1_rho_max"]
    ok = [(res[g]["S_e"] >= FROZEN["C2_S_min"]) or (res[g]["T_e"] >= FROZEN["C2_T_min_h"]) for g in res
          if FROZEN["C2_design_code"][g] == 0 and np.isfinite(res[g]["S_e"])]
    c2 = sum(ok) >= FROZEN["C2_min_units"]
    out = {"units": res, "rho_S_x": rho, "C1": bool(c1), "C2": bool(c2), "C2_count": int(sum(ok))}
    L.write_json(L.OUTD / "confirm" / "confirm_results.json", out)
    print(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", action="store_true", dest="ack")
    a = ap.parse_args()
    if not (a.confirm and a.ack):
        print("H95 confirm.py: frozen predictions (not run):")
        for k, v in FROZEN.items():
            print(f"  {k}: {v}")
        print("Pass --confirm --i-understand-this-uses-the-locked-holdout to run on the holdout.")
        return
    if not git_clean():
        raise SystemExit("commit H95's code first (predictions and script must be committed before a confirmatory run)")
    run()


if __name__ == "__main__":
    main()
