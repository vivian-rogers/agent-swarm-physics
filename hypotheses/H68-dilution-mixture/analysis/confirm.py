"""H68 confirmatory script (LOCKED HOLDOUT). Written 2026-10-04 after exploratory round 1. NOT RUN.

Frozen predictions (thresholds fixed from round 1, before any holdout data is loaded). Targets: #28, #29 (regime I),
#45, #46, #47, #49, #50 (regime III) and the #51 tail (2026-09-07 -> 09-21). A target is scored when >= 6 agents are
eligible (>= 150 units, >= 15 mention responses, within-agent-day SD of log k >= 0.3). Estimator: round 1's per-agent
cloglog k^-beta_i with agent-day propensities and the per-unit mention factor (primary), mixture test B = 200.
  C1 one exponent family: tau-hat's profile 95% upper bound < 0.35 in >= 75% of scored targets
     (round 1: 7/9 powered periods; tau-hat 0.09-0.20).                                                              [0.75]
  C2 no two-strategy mixture: the P1 rule (bootstrap p < 0.05, modes in [0.7, 1.3] and [-0.3, 0.3], >= 2 agents each)
     fails in every scored target (round 1: 0/17).                                                                     [0.9]
  C3 no thread followers: fewer than 5% of scored agent-periods have beta_i + 1.96 se_i < 0.3 (round 1: 0/170 point
     estimates below 0.19).                                                                                            [0.85]
  C4 no family weights: lab permutation p > 0.05 on the pooled held-out agent-periods (round 1: p 0.37).            [0.7]

Inputs. H68 reads H18's round-1b ledger pending tables, which exclude the holdout by construction. A confirmatory run
therefore needs the pending-set builder run on the held-out days: data/processed/H68-dilution-mixture/confirm_inputs/
G<NN>/units.parquet with the columns of scheme/build.py. That builder (H18's scheme/build_ledger.py, proposed for
infra/shared/ with an --include-holdout switch) is not run here; this script refuses until the inputs exist and the
builder is committed. Re-freeze this script if the builder's definitions change.

Reuse disclosure (hypotheses/holdout.md policy): #45 was used by H02 (activity couplings); #46-#50 by H04 (Hawkes,
hours); H18's own confirm_holdout.py targets the same periods with the population exponent (a different statistic:
H68 tests the between-agent distribution). Disclose in this card, H18's card and LOG.md before running.

Safeguards: refuses without --confirm --i-understand-this-uses-the-locked-holdout; refuses unless this script, the
card, h68lib.py, run_periods.py and scheme/build.py are tracked and unmodified, and holdout_ledger.check() allows every
target. --dry-run scores non-holdout stand-ins (G38, G41, G44, G51 units) through the same code and checks that tau-hat
reproduces run_periods within 0.01.

Usage: uv run python hypotheses/H68-dilution-mixture/analysis/confirm.py --dry-run
       uv run python hypotheses/H68-dilution-mixture/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "infra/shared"))
import h68lib as L  # noqa: E402

D = ROOT / "data/processed/H68-dilution-mixture"
TARGETS = {"G28": "G28", "G29": "G29", "G45": "G45", "G46": "G46", "G47": "G47", "G49": "G49", "G50": "G50",
           "G51tail": "#51-tail"}
STANDINS = ["G38", "G41", "G44", "G51"]
FILES = ["hypotheses/H68-dilution-mixture/analysis/confirm.py", "hypotheses/H68-dilution-mixture/README.md",
         "hypotheses/H68-dilution-mixture/analysis/h68lib.py", "hypotheses/H68-dilution-mixture/analysis/run_periods.py",
         "hypotheses/H68-dilution-mixture/scheme/build.py"]


def git_clean() -> bool:
    for f in FILES:
        tracked = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--error-unmatch", f], capture_output=True).returncode == 0
        dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", f], capture_output=True, text=True).stdout.strip()
        if not tracked or dirty:
            print(f"refusing: {f} is untracked or modified", file=sys.stderr)
            return False
    return True


def score_units(u: pl.DataFrame, seed: int) -> dict:
    rows = []
    for (a,), g in u.group_by(["agent"], maintain_order=True):
        if L.eligible(g, "resp"):
            f = L.agent_fit(g, "resp")
            rows.append(dict(agent=int(a), lab=g["lab"][0], beta=f["beta"], se=f["se"]))
    out = dict(n_eligible=len(rows), agents=rows, scored=len(rows) >= 6)
    if len(rows) >= 4:
        b = np.array([r["beta"] for r in rows])
        s = np.array([r["se"] for r in rows])
        mt = L.mixture_test(b, s, B=200, seed=seed)
        lo, hi = L.tau_profile_ci(b, s)
        out.update(tau=mt["U"]["tau"], tau_ci=[lo, hi], p1=L.p1_pass(mt), lr_p=mt["p"],
                   n_thread=int(np.sum(b + 1.96 * s < 0.3)))
    return out


def verdicts(per: dict) -> dict:
    sc = {k: v for k, v in per.items() if v["scored"]}
    ag = [dict(r, period=k) for k, v in sc.items() for r in v["agents"]]
    c = dict(n_scored=len(sc),
             C1=len(sc) > 0 and np.mean([v["tau_ci"][1] < 0.35 for v in sc.values()]) >= 0.75,
             C2=len(sc) > 0 and not any(v["p1"] for v in sc.values()),
             C3=len(ag) > 0 and np.mean([r["beta"] + 1.96 * r["se"] < 0.3 for r in ag]) < 0.05)
    if len(ag) >= 6:
        c["C4_lab"] = L.lab_share(pl.DataFrame(ag).select("agent", "period", "lab", "beta", "se"), n_perm=2000, seed=1)
        c["C4"] = c["C4_lab"]["p"] > 0.05
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    a = ap.parse_args()
    if a.dry_run:
        from common import holdout_mask
        per = {}
        for i, p in enumerate(STANDINS):
            u = pl.read_parquet(D / p / "units.parquet")
            assert not any(holdout_mask(u["pt_date"].to_list(), [int(p[1:])] * u.height)), "holdout day in dry run"
            per[p] = score_units(u, seed=int(p[1:]))
            ref = json.loads((D / p / "period.json").read_text())
            d = abs(per[p]["tau"] - ref["tau"])
            print(p, "tau", round(per[p]["tau"], 3), "round-1", round(ref["tau"], 3), "|d|", round(d, 4))
            assert d < 0.01, "dry run does not reproduce round 1"
        print(json.dumps({k: v for k, v in verdicts(per).items() if k != "C4_lab"}, default=bool))
        print("dry run OK (non-holdout stand-ins only)")
        return
    if not (a.confirm and a.ack):
        sys.exit("refusing: confirmatory run needs --confirm --i-understand-this-uses-the-locked-holdout")
    if not git_clean():
        sys.exit(1)
    import holdout_ledger as HL
    for k, t in TARGETS.items():
        if not HL.check("H68", t, "chat addressing", ["dilution_exponent"])["allowed"]:
            sys.exit(f"refusing: holdout ledger blocks {t}")
    src = D / "confirm_inputs"
    missing = [k for k in TARGETS if not (src / k / "units.parquet").exists()]
    if missing:
        sys.exit(f"refusing: holdout pending-set inputs missing for {missing} (see docstring)")
    per = {k: score_units(pl.read_parquet(src / k / "units.parquet"), seed=i) for i, k in enumerate(TARGETS)}
    res = dict(periods=per, verdicts=verdicts(per))
    (src / "confirm_results.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps({k: v for k, v in res["verdicts"].items() if k != "C4_lab"}, indent=1, default=bool))


if __name__ == "__main__":
    main()
