"""H113 confirmatory test on the locked holdout. FROZEN 2026-10-04 after exploratory round 1. NOT RUN.

Predictions (from round 1; card section "Confirmatory design"):
  C1  Exogenous-k design (D2 timer-wake batches, #51 tail): total-uptake exponent a_U = 1 - b has a 95% CI inside
      (0, 0.50): a bottleneck that is neither a one-message capacity (0) nor H18's corrected 0.50, nor linear (1).
      (Round 1, #51 head: bge 0.31 [0.25, 0.37], gte 0.29 [0.24, 0.34].)
  C2  Talk calls: the DerSimonian-Laird pool of a_U over the testable targets (bge) has its 95% CI inside (0, 0.50).
      (Round 1, 34 testable periods: 0.28 [0.25, 0.31].)
  C3  Read-out, not only a field: the pooled matched-age read - in-flight contrast (bge) is > 0 with CI > 0.
      (Round 1: 0.014 [0.006, 0.022].)
  C4  Both embedding models: |b(bge) - b(gte)| <= 0.2 in >= 2/3 of testable targets. (Round 1: 34/34.)
  C5  Recency: the pooled newest-minus-older item slope (bge) is > 0 with CI > 0. (Round 1: 0.034 [0.025, 0.043].)
Targets: talk calls of #43, #45, #46, #47, #48, #49, #50 (held-out days only) and the #51 tail (unit 51m days; talk
calls and D2 wakes). Testable: >= 300 calls with k >= 1 and >= 30 with k >= 8 (card rule).
Fixed caveat: a time-local topic field alone gives b ~ 0.8 (a_U ~ 0.2) on synthetic skeletons; C3 is the guard.
Guard: --confirm --i-understand-this-uses-the-locked-holdout, a committed H113 folder, holdout_ledger.check() (family
"readout_capacity"). --dry-run runs the identical code on non-holdout stand-ins (#38, #41, #44; tail = units 51h-51l)
and writes to confirm_dryrun/. Pending sets for held-out days are built in memory and written only to a folder outside
data/processed/shared/ (pending_sets.build_period with include_holdout=True).
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
import h113lib as L  # noqa: E402
import h113scheme as S  # noqa: E402

OUT = ROOT / "data/processed/H113-readout-channel-capacity"
TARGETS = [43, 45, 46, 47, 48, 49, 50]
STANDIN = [38, 41, 44]
TAIL_UNITS = ["51m"]
STANDIN_TAIL = ["51h", "51i", "51j", "51k", "51l"]
FAMILY = "readout_capacity"
MODELS = ("bge_small", "gte_modernbert")


def days_of(g: int, units: list[str] | None, allow_holdout: bool) -> list[str]:
    pu = pl.read_parquet(S.SHARED / "period_units.parquet").filter(pl.col("goal_no") == g)
    if units:
        pu = pu.filter(pl.col("unit_id").is_in(units))
    if not allow_holdout:
        pu = pu.filter(~pl.col("holdout"))
    return sorted(d for ds in pu["days"].to_list() for d in ds)


def build(g: int, days: list[str], allow_holdout: bool, tmp: Path, inp) -> Path | None:
    import pending_sets as PS
    res = PS.build_period(inp, g, days=days, include_holdout=allow_holdout, verbose=False)
    if res is None:
        return None
    d = tmp / f"G{g:02d}_{days[0]}"
    PS.write_period(d, res)
    return d


def target(g: int, days: list[str], allow_holdout: bool, tmp: Path, inp, wakes: bool = False) -> dict:
    d = build(g, days, allow_holdout, tmp, inp)
    if d is None:
        return {"n": 0}
    cr = S.chat_rows()
    calls, items = S.build_frames_talks(g, d)
    items = S.at_call_items(calls, items, cr)
    out = {}
    for m in MODELS:
        c, it, _, _ = S.compute(g, calls, items, m, allow_holdout=allow_holdout, field=False)
        o = {"n_k1": int((c["k"] >= 1).sum()) if len(c) else 0, "n_k8": int((c["k"] >= 8).sum()) if len(c) else 0}
        o["testable"] = o["n_k1"] >= 300 and o["n_k8"] >= 30
        if o["n_k1"] >= 30:
            o["fit"] = L.fit_b(c, seed=g); o["placebo"] = L.placebo_contrast(c, it, seed=g); o["recency"] = L.recency(c, it, seed=g)
        if wakes and (d / "wakes.parquet").exists():
            wc, wi = S.build_frames_wakes(g, d, cr)
            wi = wi.with_columns(pl.lit(False).alias("at_call"))
            cw, iw, _, _ = S.compute(g, wc, wi, m, allow_holdout=allow_holdout, field=False)
            o["wake_fit"] = L.fit_b(cw, seed=g) if len(cw) else {}
        out[m] = o
    return out


def evaluate(res: dict, tail: dict) -> dict:
    T = [r for r in res.values() if r.get("bge_small", {}).get("testable")]
    fits = [r["bge_small"]["fit"] for r in T if "a_U" in r["bge_small"].get("fit", {})]
    pool = L.dl_pool([f["a_U"] for f in fits], [f["a_U_lo"] for f in fits], [f["a_U_hi"] for f in fits])
    pcs = [r["bge_small"]["placebo"] for r in T if r["bge_small"].get("placebo", {}).get("lo") is not None]
    pc = L.dl_pool([p["contrast"] for p in pcs], [p["lo"] for p in pcs], [p["hi"] for p in pcs])
    rcs = [r["bge_small"]["recency"] for r in T if r["bge_small"].get("recency", {}).get("lo") is not None]
    rc = L.dl_pool([p["diff"] for p in rcs], [p["lo"] for p in rcs], [p["hi"] for p in rcs])
    agree = [abs(r["bge_small"]["fit"]["b"] - r["gte_modernbert"]["fit"]["b"]) <= 0.2 for r in T
             if "b" in r["bge_small"].get("fit", {}) and "b" in r["gte_modernbert"].get("fit", {})]
    wf = tail.get("bge_small", {}).get("wake_fit", {})
    out = {"n_testable": len(T), "pool_a_U": pool, "pool_placebo": pc, "pool_recency": rc, "agree": [int(sum(agree)), len(agree)],
           "tail_wake_bge": wf, "tail_wake_gte": tail.get("gte_modernbert", {}).get("wake_fit", {})}
    out["C1"] = bool(wf.get("a_U") is not None and wf["a_U_lo"] > 0 and wf["a_U_hi"] < 0.50)
    out["C2"] = bool(np.isfinite(pool["est"]) and pool["lo"] > 0 and pool["hi"] < 0.50)
    out["C3"] = bool(np.isfinite(pc["est"]) and pc["lo"] > 0)
    out["C4"] = bool(agree and sum(agree) >= 2 / 3 * len(agree))
    out["C5"] = bool(np.isfinite(rc["est"]) and rc["lo"] > 0)
    return out


def guard(args):
    if not (args.confirm and args.i_understand_this_uses_the_locked_holdout):
        sys.exit("refusing: confirmatory run needs --confirm --i-understand-this-uses-the-locked-holdout (Vivian's sign-off)")
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", str(HERE.parent)], capture_output=True, text=True).stdout
    if dirty.strip():
        sys.exit("refusing: commit the H113 folder (card, predictions, this script) before the confirmatory run")
    import holdout_ledger as HL
    for t in [f"G{g}" for g in TARGETS] + ["#51-tail"]:
        c = HL.check("H113", t, "read-out content uptake (ledger pending sets x DQ5 vectors)", FAMILY)
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
    import pending_sets as PS
    if args.confirm:
        guard(args)
        allow, periods, tail_units, out = True, TARGETS, TAIL_UNITS, OUT / "confirm"
    else:
        allow, periods, tail_units, out = False, STANDIN, STANDIN_TAIL, OUT / "confirm_dryrun"
    out.mkdir(parents=True, exist_ok=True)
    tmp = out / "pending_sets_tmp"
    inp = PS.Inputs(include_holdout=allow)
    res = {}
    for g in periods:
        dd = days_of(g, None, allow)
        res[g] = target(g, dd, allow, tmp, inp) if dd else {"n": 0}
    tail = target(51, days_of(51, tail_units, allow), allow, tmp, inp, wakes=True)
    ev = evaluate(res, tail)
    ev.update(mode="confirm" if args.confirm else "dry-run (non-holdout stand-ins; a pipeline check, not evidence)",
              periods=periods, tail_units=tail_units)
    (out / ("confirm.json" if args.confirm else "dry_run.json")).write_text(json.dumps(ev, indent=1, default=float))
    print(json.dumps({k: ev[k] for k in ("C1", "C2", "C3", "C4", "C5", "n_testable")}, indent=1))


if __name__ == "__main__":
    main()
