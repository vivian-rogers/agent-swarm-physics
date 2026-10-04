"""H93 confirmatory test on the locked holdout. FROZEN 2026-10-04 after exploratory round 1. NOT RUN.

Predictions (from the round-1 results; card section "Confirmatory design"):
  C1  Share coupling in shared-goal weeks: the validated estimator M4 gives betaJ-hat > 0 with 95% CI > 0 in work or
      attention in >= 1/2 of the testable scored period targets (#45, #46, #47, #50).
      (Round 1: 6 of 10 testable non-own replication periods, #31, #33, #36, #37, #38, #41.)
  C2  Subcritical: at the M4 fit, P_multi < 0.5 (fewer than half of 100 parametric draws give >= 2 stable
      Brock-Durlauf fixed points) in >= 90% of the identified unit-channel fits over all targets, the #51 tail included.
      (Round 1: 51/54.)
  C3  Private roles avoid occupied repos: in the #51 tail (unit 51m) betaJ-hat(M4, work) < 0 with CI < 0.
      (Round 1, #51 head: random-effects pool over 10 units -11.7 [-19.0, -4.4].)
  C4  Not a shared-prior artifact: in every target where C1's CI is > 0, the cross-lab share coefficient
      (SPLIT_lab) is > 0 (point estimate) in >= 2/3 of those target-channels.
  Reported, not scored: the kickoff-free placebo (M4_nonamed), the read split, R3 vs M4 log-likelihood.
Targets: #45, #46, #47, #50 (whole periods; units split at period_units, DL-pooled) and the #51 tail (51m).
#48 (one day) and #49 (one room, game-only) are reported, not scored.
Testable: >= 30 choice events with >= 2 options and >= 10 choices of an existing option (card rule).
Caveat fixed in advance: M4 cannot separate social coupling from fast common repo bursts (card A2), so C1 confirms the
share coefficient, not J.
Guard: needs --confirm --i-understand-this-uses-the-locked-holdout, a committed H93 folder, and holdout_ledger.check().
--dry-run runs the identical code on non-holdout stand-ins (#38, #41 for the periods; units 51h-51l for the tail).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import json  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
sys.path.insert(0, str(ROOT / "infra/shared"))
import build as B  # noqa: E402
import h93lib as L  # noqa: E402
import run as RUN  # noqa: E402

OUT = ROOT / "data/processed/H93-brock-durlauf-project-choice/confirm"
TARGETS = [45, 46, 47, 50]
REPORT_ONLY = [48, 49]
STANDIN = [38, 41]
TAIL_UNITS = ["51m"]
STANDIN_TAIL = ["51h", "51i", "51j", "51k", "51l"]
DRAWS = 100


def target_stats(g: int, allow_holdout: bool, units: list[str] | None = None) -> dict:
    d = B.build_period(g, allow_holdout=allow_holdout, write=False)
    res = {}
    for ch in ("work", "attention"):
        ev, lt, occ = d[ch]
        if lt is None:
            res[ch] = None
            continue
        if units:
            lt = lt.filter(pl.col("unit").is_in(units))
            ev = ev.filter(pl.col("unit").is_in(units))
            occ = occ.filter(pl.col("unit").is_in(units))
            if lt.height == 0:
                res[ch] = None
                continue
        lt = L.add_features(lt)
        r = RUN.channel(g, ch, DRAWS, lt=lt, ev=ev, occ=occ)
        pr = r.get("primary") if r else None
        lab = (r["fits"].get("SPLIT_lab") or {}).get("pool_s_cross") if r else None
        pm = [v.get("p_multi") for v in (r or {}).get("equilibria", {}).values() if isinstance(v, dict) and "p_multi" in v]
        fits = ((r or {}).get("fits") or {}).get("M4") or {}
        ufits = fits.get("units") or ({"period": fits.get("fit")} if fits.get("fit") else {})
        eq = (r or {}).get("equilibria") or {}
        pm_id = [eq[u]["p_multi"] for u, f in ufits.items()
                 if f and f.get("gamma_se") is not None and f["gamma_se"] <= 5 and u in eq and "p_multi" in eq[u]]
        res[ch] = {"testable": bool(r and (r["units_testable"] or r["testable"])), "events": r["events"] if r else 0,
                   "M4": pr, "cross_lab": lab, "p_multi_max": max(pm) if pm else None, "p_multi_all": pm_id,
                   "identified": bool(pr and pr.get("se") is not None and pr["se"] < 20)}
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.confirm == a.dry_run:
        sys.exit("choose exactly one of --confirm or --dry-run")
    real = a.confirm
    if real:
        if not a.ack:
            sys.exit("refusing: --confirm needs --i-understand-this-uses-the-locked-holdout")
        dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "hypotheses/H93-brock-durlauf-project-choice"],
                               capture_output=True, text=True).stdout.strip()
        if dirty:
            sys.exit("refusing: commit the H93 folder (predictions and this script) before the confirmatory run")
        import holdout_ledger as HL
        for t in [f"G{g}" for g in TARGETS] + ["#51-tail"]:
            c = HL.check("H93", t, "project choice (DQ4 work labels, project_states)", ["project_potts"])
            print(t, "allowed" if c["allowed"] else "BLOCKED", "disclosure needed" if c["needs_disclosure"] else "")
            if not c["allowed"]:
                sys.exit(f"refusing: {t} already used by the same estimator family")
    targets = TARGETS if real else STANDIN
    tail_units = TAIL_UNITS if real else STANDIN_TAIL
    res = {"mode": "confirm" if real else "dry-run", "targets": {}}
    for g in targets + (REPORT_ONLY if real else []):
        res["targets"][f"G{g}"] = target_stats(g, real)
    res["targets"]["51tail"] = target_stats(51, real, units=tail_units)
    scored = {k: v for k, v in res["targets"].items() if k in [f"G{g}" for g in targets]}
    # C1
    hits, tested = 0, 0
    for v in scored.values():
        chs = [c for c in (v.get("work"), v.get("attention")) if c and c["testable"] and c["identified"]]
        if not chs:
            continue
        tested += 1
        hits += any(c["M4"]["lo"] > 0 for c in chs)
    res["C1"] = tested > 0 and hits >= tested / 2
    # C2
    pms = [p for v in res["targets"].values() for c in (v.get("work"), v.get("attention"))
           if c and c["testable"] and c["identified"] for p in c["p_multi_all"]]
    res["C2"] = bool(pms) and sum(p < 0.5 for p in pms) >= 0.9 * len(pms)
    # C3
    tw = res["targets"]["51tail"].get("work")
    res["C3"] = bool(tw and tw["identified"] and tw["M4"]["hi"] < 0)
    # C4
    pos = [c for v in scored.values() for c in (v.get("work"), v.get("attention"))
           if c and c["testable"] and c["identified"] and c["M4"]["lo"] > 0]
    cl = [c["cross_lab"]["est"] > 0 for c in pos if c.get("cross_lab")]
    res["C4"] = bool(cl) and sum(cl) >= 2 / 3 * len(cl)
    res["counts"] = {"C1_tested": tested, "C1_hits": hits, "C2_n": len(pms), "C4_n": len(cl)}
    out = OUT if real else OUT.parent / "confirm_dryrun"  # the dashboard counts any data/processed/<H>/confirm* as a run
    out.mkdir(parents=True, exist_ok=True)
    name = "confirm.json" if real else "confirm_dryrun.json"
    (out / name).write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps({k: res[k] for k in ("C1", "C2", "C3", "C4", "counts")}, indent=1))


if __name__ == "__main__":
    main()
