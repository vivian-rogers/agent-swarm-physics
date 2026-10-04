"""H117 confirmatory script (LOCKED HOLDOUT). Written 2026-10-04 after exploratory round 1. NOT RUN.

Frozen predictions (thresholds fixed from the round-1 non-holdout placebo pools, before any holdout data is loaded):
  C1 NE35 (#32; before 2026-02-23, 02-24 | after 02-26, 02-27; the step day 02-25 is skipped): the E1 KI-5 block
     coupling-shift Q over fixed pairs is <= the frozen regime-I placebo 95th percentile (J invariant). Kill if above.
     First stage: F above the frozen regime-I placebo 90th percentile (else "no field step": mixed).            [0.6]
     Structural assertion: every eligible pair is co-located on both sides (one room); otherwise the run stops.
  C2 NE44 (#46; before 06-09, 06-10 | after 06-11, 06-12): the same rule against the frozen regime-III pool.  [0.6]
Power (Amendment 1): a pass rules out rewiring of +-1.2 logistic units on half the pairs (power 0.85-0.88 in
#38-type and regime-I skeletons); smaller changes are not ruled out.

Reuse disclosure (hypotheses/holdout.md; holdout_ledger.check): #32/NE12 were used by H05 (curie_weiss_gain,
entropy_production; talk and activity); #46 by H04 (hawkes, kick response; NE21+NE23). Different estimator family
(kinetic_ising_couplings), same talk-timing modality: disclose in the card and LOG.md before running.

Safeguards: refuses without --confirm --i-understand-this-uses-the-locked-holdout; refuses unless this file, the card,
scheme/ki_talk.py and analysis/run.py are tracked and unmodified; calls holdout_ledger.check() per target;
--dry-run uses non-holdout stand-ins (NE07 windows for C1, NE17 windows for C2) with ALLOW_HOLDOUT left False, so a
held-out day would raise.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scheme"))
sys.path.insert(0, str(HERE))
import ki_talk as K  # noqa: E402
import run as RUN  # noqa: E402

ROOT = K.ROOT
FILES = [f"hypotheses/H117-coupling-invariant-rule-reset/{f}" for f in
         ("analysis/confirm.py", "README.md", "scheme/ki_talk.py", "analysis/run.py")]

# Frozen from round 1 (data/processed/H117-coupling-invariant-rule-reset/splits.parquet, placebo rows, k = 2).
FROZEN = {
    "Q95": {"I": 1.4253, "III": 0.9532},   # linear quantiles; pools of 83 (I) and 26 (III) placebo splits
    "F90": {"I": 6.5926, "III": 5.5455},
}
TARGETS = {
    "C1": {"name": "NE35", "before": ["2026-02-23", "2026-02-24"], "after": ["2026-02-26", "2026-02-27"],
           "pool": "I", "ledger": "G32", "standin": ("NE07", ["2025-12-02", "2025-12-03"], ["2025-12-04", "2025-12-05"])},
    "C2": {"name": "NE44", "before": ["2026-06-09", "2026-06-10"], "after": ["2026-06-11", "2026-06-12"],
           "pool": "III", "ledger": "G46", "standin": ("NE17", ["2026-04-10", "2026-04-13"], ["2026-04-14", "2026-04-15"])},
}


def git_clean() -> bool:
    for f in FILES:
        tracked = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--error-unmatch", f], capture_output=True).returncode == 0
        dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", f], capture_output=True, text=True).stdout.strip()
        if not tracked or dirty:
            print(f"refusing: {f} is untracked or modified", file=sys.stderr)
            return False
    return True


def evaluate(tag: str, spec: dict, before, after, name) -> dict:
    sp = {"name": name, "before": before, "after": after, "regime": spec["pool"], "kind": "confirm", "k": 2}
    row = RUN.run_split(sp, do_e2=False, save_J=False)
    row.pop("_rowq", None)
    if row.get("skip"):
        return {"target": tag, "verdict": "void", "row": row}
    if spec["name"] == "NE35" and row["n_pairs"] < row["n_agents"] * (row["n_agents"] - 1) / 2:
        raise RuntimeError("NE35: not all eligible pairs are co-located on both sides; the frozen design assumes one room")
    q95, f90 = FROZEN["Q95"][spec["pool"]], FROZEN["F90"][spec["pool"]]
    if row["Q"] > q95:
        verdict = "failed (J moved more than placebo splits)"
    elif row["F"] > f90:
        verdict = "supported"
    else:
        verdict = "mixed (no field step)"
    return {"target": tag, "name": name, "Q": row["Q"], "Q95": q95, "F": row["F"], "F90": f90,
            "n_agents": row["n_agents"], "n_pairs": row["n_pairs"], "verdict": verdict}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    a = ap.parse_args()
    assert all(v is not None for d in FROZEN.values() for v in d.values()), "frozen thresholds missing"
    if a.dry_run:
        assert not K.ALLOW_HOLDOUT
        out = []
        for tag, spec in TARGETS.items():
            nm, b, af = spec["standin"]
            out.append(evaluate(tag, spec, b, af, f"standin_{nm}"))
        print(json.dumps(out, indent=1, default=float))
        print("dry run OK (non-holdout stand-ins; no held-out row loaded)")
        return
    if not (a.confirm and a.ack):
        sys.exit("refusing: needs --confirm --i-understand-this-uses-the-locked-holdout (Vivian's sign-off)")
    if not git_clean():
        sys.exit(1)
    sys.path.insert(0, str(ROOT / "infra/shared"))
    import holdout_ledger as HL
    for tag, spec in TARGETS.items():
        chk = HL.check("H117", spec["ledger"], "talk", "kinetic_ising_couplings")
        if not chk["allowed"]:
            sys.exit(f"refusing: ledger blocks {spec['ledger']}: {chk['prior_runs_same_family']}")
        if chk["needs_disclosure"]:
            print(f"disclosure required for {spec['ledger']}: {[u['hypothesis'] for u in chk['prior_runs']]}")
    K.ALLOW_HOLDOUT = True
    res = [evaluate(tag, spec, spec["before"], spec["after"], spec["name"]) for tag, spec in TARGETS.items()]
    od = ROOT / "data/processed/H117-coupling-invariant-rule-reset/confirm"
    od.mkdir(parents=True, exist_ok=True)
    (od / "confirm_results.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
