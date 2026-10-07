"""H133 frozen confirmation script (written 2026-10-07 after round 1; NOT RUN). Runs only with Vivian's sign-off.

Targets (reserved): goal periods #45, #46, #47 and the #51 tail units of `period_units` (holdout == True). Reuse
disclosure: family `project_potts` (H93, H129, H77/H78, H104 plan the same periods); check the holdout ledger first.

Frozen tests (from the H133 card, round 1, after Amendments A1-A2):
  C1 (P4, per-call background): the random-effects mean of eta_sw over the target units (cloglog on background calls;
     the A2 model with ln(1 + n options); agent-cluster sandwich SEs; DerSimonian-Laird) has a 95% CI that includes 0
     and excludes 1. Kill B fires if the CI includes 1 and excludes 0.
  C2 (descriptive only, A1): the post hoc observed / expected count of hops onto projects named in a read message
     (score form at the fit without read terms) is reported with its within-project-hour permutation band. It is
     not a test: the round-1 synthetic gave power 0.64 at gamma_nam = 1 even for the whole regime-II/III stack.
Outputs go to data/processed/H133-readout-glauber-potts/confirm/ (never to the exploration folders).

Usage:
  uv run python hypotheses/H133-readout-glauber-potts/analysis/confirm.py --dry-run
        builds and runs the frozen pipeline on a NON-reserved stand-in unit (44a) into a scratch folder; reads no
        reserved row.
  uv run python hypotheses/H133-readout-glauber-potts/analysis/confirm.py --run --i-understand-this-uses-the-reserved-periods
        the confirmatory run (requires sign-off and a holdout-ledger check()).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402
from pathlib import Path  # noqa: E402

import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import build as SB  # noqa: E402
import h133lib as L  # noqa: E402

TARGET_GOALS = (45, 46, 47)
STAND_IN = ("44a",)


def targets(dry: bool) -> pl.DataFrame:
    pu = pl.read_parquet(SB.SH / "period_units.parquet")
    if dry:
        return pu.filter(pl.col("unit_id").is_in(list(STAND_IN)) & ~pl.col("holdout"))
    return pu.filter(pl.col("holdout") & (pl.col("goal_no").is_in(list(TARGET_GOALS)) | (pl.col("goal_no") == 51)))


def run(dry: bool):
    out = Path(tempfile.mkdtemp(prefix="h133_confirm_dry_")) if dry else L.D / "confirm"
    out.mkdir(parents=True, exist_ok=True)
    res = {}
    for u in targets(dry).iter_rows(named=True):
        meta = SB.build_unit(u, allow_reserved=not dry, out_root=out)
        if not meta.get("testable"):
            res[u["unit_id"]] = {"testable": False, **{k: meta[k] for k in ("hops", "named_reads_other")}}
            continue
        sk = L.load_skeleton(u["unit_id"], root=out)
        c1 = L.fit_cloglog(sk, sk.hop_any, sk.bg, extra=L.n_options(sk))
        res[u["unit_id"]] = {"testable": True, "eta_sw": c1}
    est = [r["eta_sw"]["eta"] for r in res.values() if r.get("testable") and r["eta_sw"].get("ok")]
    se = [r["eta_sw"]["se"] for r in res.values() if r.get("testable") and r["eta_sw"].get("ok")]
    pooled = L.dersimonian_laird(est, se)
    lo, hi = pooled["ci"]
    verdict = None if pooled["k"] == 0 else ("C1 holds" if lo <= 0 <= hi and hi < 1 else
                                             "Kill B" if lo <= 1 <= hi and lo > 0 else "C1 fails")
    summ = {"dry_run": dry, "units": res, "C1_pooled": pooled, "C1_verdict": verdict, "out": str(out)}
    (out / "confirm_summary.json").write_text(json.dumps(summ, indent=1, default=float))
    print(json.dumps({k: v for k, v in summ.items() if k != "units"}, indent=1, default=float))


def main():
    if "--dry-run" in sys.argv:
        run(dry=True)
        return
    if "--run" in sys.argv and "--i-understand-this-uses-the-reserved-periods" in sys.argv:
        sys.path.insert(0, str(SB.ROOT / "infra/shared"))
        import holdout_ledger as HL  # noqa: E402
        chk = [HL.check("H133", t, "project hops per call", "project_potts") for t in ("G45", "G46", "G47", "#51-tail")]
        print(json.dumps(chk, indent=1, default=str))
        if not all(c["allowed"] for c in chk):
            sys.exit("holdout ledger: a prior run of the same family used a target; stop (policy item 2)")
        run(dry=False)
        return
    print(__doc__)
    sys.exit(2)


if __name__ == "__main__":
    main()
