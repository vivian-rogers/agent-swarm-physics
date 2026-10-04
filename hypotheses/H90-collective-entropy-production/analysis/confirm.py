"""H90 confirmatory tests on the LOCKED HOLDOUT. Written after exploratory round 1 (2026-10-04); NOT RUN.

Guard: the holdout is touched only with BOTH flags, a clean git state for H90's code, and a holdout-ledger check:
  uv run python hypotheses/H90-collective-entropy-production/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
Without the flags the script prints the frozen predictions and exits.

Targets (frozen in FROZEN below and on the card, "Confirmatory predictions"):
  C1  #51 tail (2026-09-07 -> 09-18; N up to 32, 10 days): talk address contrast Delta_addr > 0 against 100 block
      shifts (p < 0.05). Power at G51's effect size: between the 16-day (0.45-0.55) and 33-day (1.00) synthetic sizes.
  C2  #51 tail: sigma_un(talk) inside the shift null (p >= 0.05): no ungated talk coupling.
  C3  #51 tail: behavior and activity collective share small: rho_coll < 0.1, or sigma_coll(all) and Delta_addr both
      inside the shift null.
  C4  #45 and #47 (5 days, N 18): sigma_coll(all) inside the shift null in behavior and activity (the expected null;
      talk is reported, not scored: power at G51's effect size is <= 0.15 in 5-day periods).
Reuse: #45/#47 and the #51 tail are planned or used by many hypotheses (activity, talk, behavior EP: H02, H04, H14,
H41, H76 ...). H90's statistic (held-out AIK collective EP with naming partner sets) is new; the ledger check below
decides; disclose in both cards and LOG.md.
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
import h90lib as L  # noqa: E402
import build as B  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))

FROZEN = {  # frozen 2026-10-04 after exploratory round 1 (card, "Confirmatory predictions")
    "estimator": "held-out Newton, per-column ridge c=1 with block floor (A1+A2)", "R_shift_talk": 100, "R_shift": 50,
    "tail_window": ["2026-09-07", "2026-09-21"],
    "C1_addr_p_max": 0.05,           # round 1 G51: Delta_addr 0.0080 [0.0051, 0.0121], p 0.01
    "C2_un_p_min": 0.05,             # round 1 G51: sigma_un -0.0004
    "C3_rho_max": 0.1,               # round 1 G51 behavior rho 0.003
    "C4_goals": [45, 47],
}
FILES = ["hypotheses/H90-collective-entropy-production/analysis/confirm.py",
         "hypotheses/H90-collective-entropy-production/analysis/h90lib.py",
         "hypotheses/H90-collective-entropy-production/scheme/build.py"]


def git_clean() -> bool:
    out = subprocess.run(["git", "-C", str(L.ROOT), "status", "--porcelain", "--", *FILES], capture_output=True, text=True).stdout
    return out.strip() == ""


def channel(days, agents, ch, w, rng, R):
    n = len(agents)
    obs, stats, lay, folds = L.period_estimate(days, ch, n, w, per_agent=False)
    sh = L.null_dist(days, ch, n, w, "shift", R, rng, folds=folds)
    return {"obs": obs, **{f"p_{k}": L.pval(obs[k], [x[k] for x in sh]) for k in ("coll_all", "coll_named", "coll_unnamed", "addr")}}


def run():
    import holdout_ledger as HL
    for tgt in ("#51-tail", "G45", "G47"):
        chk = HL.check("H90", tgt, "behavior_states_v3+activity_bins_fixed+chat", "entropy_production")
        print(tgt, "allowed" if chk["allowed"] else "NOT ALLOWED", "disclosure needed" if chk["needs_disclosure"] else "")
        if not chk["allowed"]:
            raise SystemExit("holdout ledger refuses a same-family reuse: ask the coordinator")
    rng = np.random.default_rng(9090)
    lo, hi = FROZEN["tail_window"]
    res = {"tail": {}, "transfer": {}}
    for ch in ("talk", "behavior", "activity"):
        days, agents = (B.behavior_days(51, allow_holdout=True) if ch == "behavior" else B.spin_days(51, ch, allow_holdout=True))
        days = [d for d in days if lo <= d["date"] < hi]
        w = B.weights(51, agents, allow_holdout=True, days=[d["date"] for d in days])
        res["tail"][ch] = channel(days, agents, ch, w, rng, FROZEN["R_shift_talk"] if ch == "talk" else FROZEN["R_shift"])
    for g in FROZEN["C4_goals"]:
        res["transfer"][g] = {}
        for ch in ("talk", "behavior", "activity"):
            days, agents = (B.behavior_days(g, allow_holdout=True) if ch == "behavior" else B.spin_days(g, ch, allow_holdout=True))
            w = B.weights(g, agents, allow_holdout=True)
            res["transfer"][g][ch] = channel(days, agents, ch, w, rng, FROZEN["R_shift"])
    t = res["tail"]
    c1 = t["talk"]["obs"]["addr"] > 0 and t["talk"]["p_addr"] < FROZEN["C1_addr_p_max"]
    c2 = t["talk"]["p_coll_unnamed"] >= FROZEN["C2_un_p_min"]
    c3 = all((np.isfinite(t[c]["obs"]["rho_coll"]) and t[c]["obs"]["rho_coll"] < FROZEN["C3_rho_max"])
             or (t[c]["p_coll_all"] >= 0.05 and t[c]["p_addr"] >= 0.05) for c in ("behavior", "activity"))
    c4 = all(res["transfer"][g][c]["p_coll_all"] >= 0.05 for g in FROZEN["C4_goals"] for c in ("behavior", "activity"))
    out = res | {"C1": bool(c1), "C2": bool(c2), "C3": bool(c3), "C4": bool(c4)}
    L.write_json(L.OUTD / "confirm" / "confirm_results.json", out)
    print({k: out[k] for k in ("C1", "C2", "C3", "C4")})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", action="store_true", dest="ack")
    a = ap.parse_args()
    if not (a.confirm and a.ack):
        print("H90 confirm.py: frozen predictions (not run):")
        for k, v in FROZEN.items():
            print(f"  {k}: {v}")
        print("Pass --confirm --i-understand-this-uses-the-locked-holdout to run on the holdout.")
        return
    if not git_clean():
        raise SystemExit("commit H90's code first (predictions and script must be committed before a confirmatory run)")
    run()


if __name__ == "__main__":
    main()
