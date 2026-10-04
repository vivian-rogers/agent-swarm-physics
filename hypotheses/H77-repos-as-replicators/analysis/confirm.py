"""H77 confirmatory test on the locked holdout. FROZEN 2026-10-04 after exploratory round 1. NOT RUN.

Predictions (round-1 pattern; see the card, "Confirmatory design"):
  C1  sigma* is a loss-convention quantity: sigma*(E = 50) - sigma*(E = 300) >= 1 nat in >= 1/2 of the targets where both
      have J+ + J- >= 8. Round 1: 2.3, 3.1, 3.7, 0.7, 2.0 nats in #31, #33, #41, #42, #40.
  C2  The observed sigma* (E = 100) lies at or below the 95th percentile of the neutral world (p = 1, no fitness spread)
      simulated on the target's own call schedule, in >= 2/3 of testable targets. Round 1: 5/5 testable.
  C3  The top repo is kickoff-named (H54 rule) in >= 2/3 of the targets that have a top repo. Round 1: 7/8.
  C4  #51 tail: the switch-out (uncopying) order q has a 95% CI above 1 (round 1, #51 head: 1.46 [1.22, 1.70]).
Targets: #46, #47, #50 and the #51 tail (unit 51m); #45, #48, #49 reported, not scored.
Guard: --confirm --i-understand-this-uses-the-locked-holdout, a committed H77 folder, holdout_ledger.check().
--dry-run runs the identical code on non-holdout stand-ins (#38; units 51h-51l for the tail).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import importlib.util  # noqa: E402
import json  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
import replicator_fit as F  # noqa: E402
import replicator_hosts as R  # noqa: E402

OUT = ROOT / "data/processed/H77-repos-as-replicators/confirm"
TARGETS = [46, 47, 50]
REPORT_ONLY = [45, 48, 49]
STANDIN = [38]
TAIL_UNITS = ["51m"]
STANDIN_TAIL = ["51h", "51i", "51j", "51k", "51l"]


def synth_module():
    spec = importlib.util.spec_from_file_location("h78_synthetic", ROOT / "hypotheses/H78-replicator-growth-order/analysis/synthetic.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def restrict(d, units):
    if not units:
        return d["bins"], d["events"]
    b = d["bins"].filter(pl.col("unit").is_in(units))
    return b, d["events"].filter(pl.col("t") >= b["t0"].min())


def sig(bins):
    ab = sorted(bins["bin"].unique().to_list())
    return F.sigma_star(bins, ab) if ab else None


def neutral_q95(g, allow, units, reps=20):
    SY = synth_module()
    days = R.period_days(g, allow)
    um = R.unit_of_day(g)
    if units:
        days = [x for x in days if um.get(x) in units]
    calls = R.load_calls(g, days)
    labs = dict(R.roster().select("agent", "lab").iter_rows())
    ctx = (calls, um, labs, days, g)
    d = R.build_period(g, allow_holdout=allow)
    ev = d["events"].filter(pl.col("t") >= calls["t_call"].min())
    k = dict(ev.group_by("kind").len().iter_rows())
    tgt = {"R": k.get("recruit", 0), "B": k.get("birth", 0), "X": k.get("expire", 0) + k.get("leave", 0), "pi_c": 0.05,
           "calls": calls.height}
    prm = SY.calibrate(ctx, SY.WORLDS["neutral"], tgt)
    s = []
    for r in range(reps):
        e2, bt, _ = SY.one_run(ctx, prm, 700 + r, true_too=False)
        if e2 is not None and bt.height:
            x = sig(bt)
            if x:
                s.append(x["est"])
    return float(np.quantile(s, 0.95)) if s else None


def target_stats(g, allow, units=None):
    d = R.build_period(g, allow_holdout=allow)
    nm = d["named"]
    out = {}
    for lab, E in (("E100", 100), ("E50", 50), ("E300", 300)):
        dd = d if E == 100 else R.build_period(g, allow_holdout=allow, E=E, named=nm)
        b, _ = restrict(dd, units)
        s = sig(b)
        out[lab] = {k: s[k] for k in ("est", "se", "J_plus", "J_minus", "testable", "top")} if s else None
    b, ev = restrict(d, units)
    top = out["E100"]["top"] if out["E100"] else None
    out["top_named"] = bool(nm.get(top, False)) if top else None
    q = F.depart_order(b)
    out["q"] = q
    for k in ("E100", "E50", "E300"):
        if out[k]:
            out[k].pop("top", None)
    out["neutral_q95"] = neutral_q95(g, allow, units) if out["E100"] and out["E100"]["testable"] else None
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
        dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "hypotheses/H77-repos-as-replicators"],
                               capture_output=True, text=True).stdout.strip()
        if dirty:
            sys.exit("refusing: commit the H77 folder (predictions and this script) before the confirmatory run")
        import holdout_ledger as HL
        for t in [f"G{g}" for g in TARGETS] + ["#51-tail"]:
            c = HL.check("H77", t, "work commits (DQ4)", ["project_potts", "artifact_lineage"])
            print(t, "allowed" if c["allowed"] else "BLOCKED", "disclosure needed" if c["needs_disclosure"] else "")
            if not c["allowed"]:
                sys.exit(f"refusing: {t} already used by the same estimator family")
    targets = TARGETS if real else STANDIN
    res = {"mode": "confirm" if real else "dry-run", "targets": {}}
    for g in targets + (REPORT_ONLY if real else []):
        res["targets"][f"G{g}"] = target_stats(g, real)
    res["targets"]["51tail"] = target_stats(51, real, TAIL_UNITS if real else STANDIN_TAIL)
    sc = {k: v for k, v in res["targets"].items() if k in [f"G{g}" for g in targets] or k == "51tail"}
    c1 = [(v["E50"]["est"] - v["E300"]["est"]) >= 1 for v in sc.values()
          if v["E50"] and v["E300"] and v["E50"]["testable"] and v["E300"]["testable"]]
    res["C1"] = bool(c1) and sum(c1) >= len(c1) / 2
    c2 = [v["E100"]["est"] <= v["neutral_q95"] for v in sc.values() if v["E100"] and v["E100"]["testable"] and v["neutral_q95"] is not None]
    res["C2"] = bool(c2) and sum(c2) >= 2 / 3 * len(c2)
    c3 = [v["top_named"] for v in sc.values() if v["top_named"] is not None]
    res["C3"] = bool(c3) and sum(c3) >= 2 / 3 * len(c3)
    q = sc["51tail"]["q"]
    res["C4"] = bool(q and q["lo"] > 1)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / ("confirm.json" if real else "confirm_dryrun.json")).write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps({k: res[k] for k in ("C1", "C2", "C3", "C4")}, indent=1))


if __name__ == "__main__":
    main()
