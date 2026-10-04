"""H94 confirmatory test on the locked holdout. FROZEN 2026-10-04 after exploratory round 1. NOT RUN.

Predictions (from the round-1 results; card section "Confirmatory design"). Units = period_units of each target;
testable = >= 100 work quanta, >= 3 agents, >= 3 repos (card rule). All KL in bits per work quantum.
  C1  Statistical equilibrium given the constraints: the residual after margins + ownership (+ room in two-room units),
      minus the run-preserving persistence floor, is <= 0.2 * D_1 in >= 2/3 of the testable target units.
      (Round 1: 23/24 units.)
  C2  Ownership price in private roles: in the #51 tail (51m) lambda_own >= 4 nats with the agent-bootstrap 2.5% bound
      >= 2. (Round 1, 51a-51l: 5.5-18.2.)
  C3  Ownership carries private-role work: ownership share (D_1 - D_2)/D_1 >= 0.5 in the #51 tail. (Round 1: 0.79-0.95.)
  C4  No planning beyond ownership: agent breadth over the run-preserving M2 null >= 0.8 in >= 2/3 of testable target
      units. (Round 1: 23/24.)
  C5  Ownership explains private projects: the M2 null predicts more singleton repos than the M1 null (closer to the
      observed count) in every testable target unit. (Round 1: 24/24.)
Targets: #45, #46, #47, #50 (all their units) and the #51 tail (51m). #48 and #49 are reported, not scored.
Guard: needs --confirm --i-understand-this-uses-the-locked-holdout, a committed H94 folder, and holdout_ledger.check().
--dry-run runs the identical code on non-holdout stand-ins (#38 and #41 for the periods; 51h-51l for the tail).
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
import h94lib as L  # noqa: E402

OUT = ROOT / "data/processed/H94-maxent-work-allocation/confirm"
TARGETS = [45, 46, 47, 50]
REPORT_ONLY = [48, 49]
STANDIN = [38, 41]
TAIL_UNITS = ["51m"]
STANDIN_TAIL = ["51h", "51i", "51j", "51k", "51l"]
DRAWS = 200


def testable(q: pl.DataFrame) -> bool:
    return q.height >= 100 and q["agent"].n_unique() >= 3 and q["repo"].n_unique() >= 3


def unit_stats(q: pl.DataFrame, labs: dict, seed: int) -> dict:
    two = q["room_mode"].drop_nulls().n_unique() > 1
    r = L.unit_analysis(q, two, draws=DRAWS, seed=seed, labs=labs)
    sg2, sg1 = r["sig_M2"], r["sig_M1"]
    return {"N": r["N"], "D1": r["D1"], "resid_frac": (min(r["D3"], r["D2"]) - r["pfloor3"]) / r["D1"],
            "own_share": r["own_share"], "lam_own": r["lam_own"], "lam_lo": r["lam_own_lo"], "lam_hi": r["lam_own_hi"],
            "breadth_persist": sg2.get("breadth_ratio_persist"), "single_obs": sg2["singletons_obs"],
            "single_M2": sg2.get("singletons_persist"), "single_M1": sg1.get("singletons_persist")}


def period_units(g: int, allow_holdout: bool, units: list[str] | None, labs: dict) -> dict:
    q = B.build_period(g, allow_holdout=allow_holdout, write=False)["quanta"]
    if units:
        q = q.filter(pl.col("unit").is_in(units))
    out = {}
    for (u,), qu in q.group_by(["unit"], maintain_order=True):
        out[str(u)] = unit_stats(qu, labs, sum(map(ord, str(u)))) if testable(qu) else {"testable": False, "N": qu.height}
    return out


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
        dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "hypotheses/H94-maxent-work-allocation"],
                               capture_output=True, text=True).stdout.strip()
        if dirty:
            sys.exit("refusing: commit the H94 folder (predictions and this script) before the confirmatory run")
        import holdout_ledger as HL
        for t in [f"G{g}" for g in TARGETS] + ["#51-tail"]:
            c = HL.check("H94", t, "work allocation (DQ4 work quanta)", ["artifact_lineage", "work_output"])
            print(t, "allowed" if c["allowed"] else "BLOCKED", "disclosure needed" if c["needs_disclosure"] else "")
            if not c["allowed"]:
                sys.exit(f"refusing: {t} already used by the same estimator family")
    labs = dict(pl.read_parquet(ROOT / "data/processed/shared/roster.parquet", columns=["agent", "lab"]).iter_rows())
    targets = TARGETS if real else STANDIN
    tail_units = TAIL_UNITS if real else STANDIN_TAIL
    res = {"mode": "confirm" if real else "dry-run", "targets": {}}
    for g in targets + (REPORT_ONLY if real else []):
        res["targets"][f"G{g}"] = period_units(g, real, None, labs)
    res["targets"]["51tail"] = period_units(51, real, tail_units, labs)
    scored = [v for k, t in res["targets"].items() if k in [f"G{g}" for g in targets] or k == "51tail"
              for v in t.values() if v.get("testable", True) and "D1" in v]
    tail = [v for v in res["targets"]["51tail"].values() if "D1" in v]
    res["C1"] = bool(scored) and sum(v["resid_frac"] <= 0.2 for v in scored) >= 2 / 3 * len(scored)
    res["C2"] = bool(tail) and all(v["lam_own"] >= 4 and (v["lam_lo"] or 0) >= 2 for v in tail)
    res["C3"] = bool(tail) and all(v["own_share"] >= 0.5 for v in tail)
    res["C4"] = bool(scored) and sum((v["breadth_persist"] or 0) >= 0.8 for v in scored) >= 2 / 3 * len(scored)
    res["C5"] = bool(scored) and all(abs(v["single_M2"] - v["single_obs"]) < abs(v["single_M1"] - v["single_obs"])
                                     for v in scored if v["single_obs"] > 0)
    res["counts"] = {"scored_units": len(scored), "tail_units": len(tail)}
    out = OUT if real else OUT.parent / "confirm_dryrun"  # the dashboard counts any data/processed/<H>/confirm* as a run
    out.mkdir(parents=True, exist_ok=True)
    name = "confirm.json" if real else "confirm_dryrun.json"
    (out / name).write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps({k: res[k] for k in ("C1", "C2", "C3", "C4", "C5", "counts")}, indent=1))


if __name__ == "__main__":
    main()
