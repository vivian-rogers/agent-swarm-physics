"""H112 confirmatory test on the locked holdout. FROZEN 2026-10-04 after exploratory round 1. NOT RUN.

Predictions (from round 1; card section "Confirmatory design"):
  C1  HH343's 2x effect is absent: pooled RR_U (>= 1 of a co-switch pair departs within 5 calls; unaware vs read;
      Mantel-Haenszel over target x lag bin x kickoff-named) has its 95% upper bound < 2.
      (Round 1: 1.15 [1.08, 1.22], 9 testable periods.)
  C2  No update-order effect once chat engagement is matched: among pairs where a partner claim exists before or
      around the switch (claim_i or claim_j), RR_U's 95% CI includes 1 and its point estimate lies in [0.8, 1.25].
      (Round 1: 1.02 [0.92, 1.13], 577 pairs.)
  C3  The raw excess is engagement selection: over all pairs RR_U > 1 with 95% CI > 1 (round 1: 1.15 [1.08, 1.22]),
      and the no-claim pairs depart at least as often as the claimed unaware pairs.
  C4  No read-out onset of departures in the #51 tail: the post-read departure ratio (3 calls after / 3 before the
      first read of the partner's claim) is <= 1.5 (point). (Round 1, #51 head: 0.79 [0.37, 1.64].)
Targets: #45, #46, #47, #50 (whole periods) and the #51 tail (unit 51m days). #48 and #49 reported, not scored.
Guard: --confirm --i-understand-this-uses-the-locked-holdout, a committed H112 folder (git), holdout_ledger.check()
(family "update_order_departure"). --dry-run runs the identical code on non-holdout stand-ins (#38, #41, #44 for the
periods; units 51h-51l for the tail) and writes to confirm_dryrun/.
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

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "scheme")); sys.path.insert(0, str(ROOT / "infra/shared"))
import h112lib as L  # noqa: E402
import h112scheme as S  # noqa: E402
import natives as N  # noqa: E402

OUT = ROOT / "data/processed/H112-crossing-claims-two-cycles"
TARGETS = [45, 46, 47, 50]
REPORT_ONLY = [48, 49]
STANDIN = [38, 41, 44]
TAIL_UNITS = ["51m"]
STANDIN_TAIL = ["51h", "51i", "51j", "51k", "51l"]
FAMILY = "update_order_departure"


def unit_days(units: list[str]) -> list[str]:
    pu = pl.read_parquet(S.SHARED / "period_units.parquet").filter(pl.col("unit_id").is_in(units))
    return sorted(d for ds in pu["days"].to_list() for d in ds)


def target_frame(g: int, allow_holdout: bool, days: list[str] | None, label: str) -> tuple[pl.DataFrame, dict]:
    r = S.build_period(g, allow_holdout=allow_holdout, with_work=False, days=days)
    d = r["days"]
    claims = S.load_claims(g, d)
    p = N.claimed_flags(r["pairs"], claims) if len(r["pairs"]) else r["pairs"]
    pf = L.pair_frame(p, unit=label)
    extra = {}
    if g == 51:
        extra["post_read"] = N.post_read_onset(r, claims, S.load_touches(g, d), S.load_calls_period(g, d), d)
    return pf, extra


def evaluate(frames: list[pl.DataFrame], tail_extra: dict) -> dict:
    allp = pl.concat([f for f in frames if len(f)], how="diagonal_relaxed")
    st = L.strata_of(allp)
    r_all = L.mh_rr(allp["any"].to_numpy(), allp["unaware"].to_numpy(), st)
    cl = allp.filter(pl.col("claim_i") | pl.col("claim_j"))
    r_cl = L.mh_rr(cl["any"].to_numpy(), cl["unaware"].to_numpy(), L.strata_of(cl)) if len(cl) else {"rr": np.nan}
    nocl = allp.filter(~pl.col("claim_i") & ~pl.col("claim_j"))
    p_nocl = float(nocl["any"].mean()) if len(nocl) else np.nan
    cu = cl.filter(pl.col("unaware"))
    p_cu = float(cu["any"].mean()) if len(cu) else np.nan
    pr = tail_extra.get("post_read", {})
    res = {"n_pairs": len(allp), "n_read": int(allp["read"].sum()), "rr_u_all": r_all, "rr_u_claim": r_cl,
           "p_any_noclaim": p_nocl, "p_any_claimed_unaware": p_cu, "post_read_tail": pr}
    res["C1"] = bool(np.isfinite(r_all.get("hi", np.nan)) and r_all["hi"] < 2)
    res["C2"] = bool(np.isfinite(r_cl.get("lo", np.nan)) and r_cl["lo"] <= 1 <= r_cl["hi"] and 0.8 <= r_cl["rr"] <= 1.25)
    res["C3"] = bool(np.isfinite(r_all.get("lo", np.nan)) and r_all["lo"] > 1 and (p_nocl >= p_cu))
    res["C4"] = bool(pr.get("ratio") is not None and pr["ratio"] <= 1.5)
    return res


def guard(args):
    if not (args.confirm and args.i_understand_this_uses_the_locked_holdout):
        sys.exit("refusing: confirmatory run needs --confirm --i-understand-this-uses-the-locked-holdout (Vivian's sign-off)")
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", str(HERE.parent)], capture_output=True, text=True).stdout
    if dirty.strip():
        sys.exit("refusing: commit the H112 folder (card, predictions, this script) before the confirmatory run")
    import holdout_ledger as HL
    for t in [f"G{g}" for g in TARGETS] + ["#51-tail"]:
        c = HL.check("H112", t, "co-switch departures (action touches x ledger reads)", FAMILY)
        if not c["allowed"]:
            sys.exit(f"refusing: holdout ledger forbids reuse of {t}: {c['prior_runs_same_family']}")
        if c["needs_disclosure"]:
            print(f"disclosure needed for {t}: {len(c['prior_runs'])} prior runs, {len(c['competing_planned'])} planned")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", action="store_true")
    args = ap.parse_args()
    if args.dry_run == args.confirm:
        sys.exit("choose exactly one of --dry-run / --confirm")
    if args.confirm:
        guard(args)
        allow, periods, tail, out = True, TARGETS, TAIL_UNITS, OUT / "confirm"
    else:
        allow, periods, tail, out = False, STANDIN, STANDIN_TAIL, OUT / "confirm_dryrun"
    out.mkdir(parents=True, exist_ok=True)
    frames = []
    for g in periods:
        pf, _ = target_frame(g, allow, None, f"G{g}")
        frames.append(pf)
    pf, extra = target_frame(51, allow, unit_days(tail), "51tail")
    frames.append(pf)
    res = evaluate(frames, extra)
    res.update(mode="confirm" if args.confirm else "dry-run (non-holdout stand-ins; a pipeline check, not evidence)",
               periods=periods, tail_units=tail)
    if args.confirm:
        rep = {}
        for g in REPORT_ONLY:
            f, _ = target_frame(g, allow, None, f"G{g}")
            rep[g] = {"n_pairs": len(f)}
        res["report_only"] = rep
    (out / ("confirm.json" if args.confirm else "dry_run.json")).write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps({k: res[k] for k in ("C1", "C2", "C3", "C4", "n_pairs", "n_read")}, indent=1))


if __name__ == "__main__":
    main()
