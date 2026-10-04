"""H78 confirmatory test on the locked holdout. FROZEN 2026-10-04 after exploratory round 1. NOT RUN.

Predictions (from the round-1 results; see the card, "Confirmatory design"):
  C1  #51 tail (unit 51m): the between-repo growth order (primary estimator, E = 100) has a 95% CI above 1.
      (Round 1, #51 head: 1.94 [1.22, 2.67]; read as first-order copying plus repo fitness spread, not conformism.)
  C2  #51 tail: the primary p-hat lies inside the fitness-spread null band: between the 2.5th percentile of the
      sigma_A = 0.5 world and the 97.5th percentile of the sigma_A = 1.0 world (p = 1), simulated on the tail's schedule.
  C3  Formation dominates arrivals: formation share (births + kickoff-named + blind) >= 0.6 in >= 2/3 of testable targets
      (>= 20 arrivals). Round 1: 0.76-1.00 in 7/7.
  C4  The H28 blind window is negligible at commit level: touch-based blind recruitments <= 5% of recruitments, pooled.
      Round 1: 4 of 585 (0.7%).
  C5  Returns dominate #51 recruitments: touch class "return" >= 40% of the tail's recruitments (round 1 head: 72%).
  C6  (A0) A step in the share of hosts on kickoff-named repos beyond the AR(1) surrogate null (p < 0.05) in >= 1/2 of
      testable targets (>= 20 bins with >= 2 hosts and >= 1 named repo). Round 1: 4/8.
Targets: #46, #47, #50 (whole periods, holdout NE21+NE23 / NE24 windows) and the #51 tail. #45, #48, #49 are reported,
not scored (leader week; one day; UI-only games).
Guard: needs --confirm --i-understand-this-uses-the-locked-holdout, a committed H78 folder, and holdout_ledger.check().
--dry-run runs the identical code on non-holdout stand-ins (#38 for the periods; units 51h-51l for the #51 tail).
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

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import replicator_fit as F  # noqa: E402
import replicator_hosts as R  # noqa: E402
import replicator_sim as S  # noqa: E402

OUT = ROOT / "data/processed/H78-replicator-growth-order/confirm"
TARGETS = [46, 47, 50]
REPORT_ONLY = [45, 48, 49]
STANDIN = [38]
TAIL_UNITS = ["51m"]
STANDIN_TAIL = ["51h", "51i", "51j", "51k", "51l"]


def active_h(bins: pl.DataFrame) -> dict:
    """bin -> active hours since the first bin (calendar active_offset_s), as in the round-1 tables."""
    cal = pl.read_parquet(R.SHARED / "calendar.parquet", columns=["pt_date", "win_start", "active_offset_s"])
    b = bins.select("bin", "t0").unique().with_columns(
        pl.col("t0").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).alias("pt_date"))
    b = b.join(cal, on="pt_date", how="left").with_columns(
        ((pl.col("active_offset_s") + (pl.col("t0") - pl.col("win_start")).dt.total_seconds().clip(lower_bound=0)) / 3600).alias("h"))
    h0 = b["h"].min()
    return {bb: hh - h0 for bb, hh in zip(b["bin"].to_list(), b["h"].to_list())}


def period_stats(d: dict, units: list[str] | None = None) -> dict:
    bins, ev = d["bins"], d["events"]
    if units:
        bins = bins.filter(pl.col("unit").is_in(units))
        ev = ev.filter(pl.col("t") >= bins["t0"].min())
    named = {r for r, v in d["named"].items() if v}
    po = F.period_order(bins, R="R_ff", exclude=named)
    arr = ev.filter(pl.col("kind").is_in(["recruit", "birth"]))
    form = arr.filter((pl.col("kind") == "birth") | pl.col("named") | (pl.col("cls") == "blind")).height
    rec = arr.filter(pl.col("kind") == "recruit")
    a0 = F.mathis_step(bins, named, active_h(bins)) if bins.height else None
    return {"p": po["pooled"], "p_testable": po["testable"], "n_ff": po["n_events"], "arrivals": arr.height,
            "formation_share": form / max(arr.height, 1), "recruits": rec.height,
            "blind_touch": rec.filter(pl.col("cls_touch") == "blind").height,
            "return_touch": rec.filter(pl.col("cls_touch") == "return").height,
            "A0_p": a0["p_surrogate"] if a0 else None, "A0_testable": a0 is not None and bool(named)}


def fitness_band(g: int, allow_holdout: bool, units: list[str], reps: int = 20) -> dict:
    days = R.period_days(g, allow_holdout)
    um = R.unit_of_day(g)
    days = [x for x in days if um.get(x) in units]
    calls = R.load_calls(g, days)
    labs = dict(R.roster().select("agent", "lab").iter_rows())
    import importlib.util
    spec = importlib.util.spec_from_file_location("h78_synthetic", Path(__file__).resolve().parent / "synthetic.py")
    SY = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(SY)
    ctx = (calls, um, labs, days, g)
    d = R.build_period(g, allow_holdout=allow_holdout)
    ev = d["events"].filter(pl.col("t") >= calls["t_call"].min())
    k = dict(ev.group_by("kind").len().iter_rows())
    tgt = {"R": k.get("recruit", 0), "B": k.get("birth", 0), "X": k.get("expire", 0) + k.get("leave", 0),
           "pi_c": 0.05, "calls": calls.height}
    out = {}
    for w in ("fitness05", "fitness10"):
        prm = SY.calibrate(ctx, SY.WORLDS[w], tgt)
        ps = []
        for r in range(reps):
            e2, bt, _ = SY.one_run(ctx, prm, 500 + r, true_too=False)
            if e2 is None:
                continue
            po = F.period_order(bt)
            if po["pooled"]:
                ps.append(po["pooled"]["est"])
        out[w] = ps
    lo = float(np.quantile(out["fitness05"], 0.025)) if out["fitness05"] else None
    hi = float(np.quantile(out["fitness10"], 0.975)) if out["fitness10"] else None
    return {"lo": lo, "hi": hi, "n": {w: len(v) for w, v in out.items()}}


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
        dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "hypotheses/H78-replicator-growth-order"],
                               capture_output=True, text=True).stdout.strip()
        if dirty:
            sys.exit("refusing: commit the H78 folder (predictions and this script) before the confirmatory run")
        import holdout_ledger as HL
        for t in [f"G{g}" for g in TARGETS] + ["#51-tail"]:
            c = HL.check("H78", t, "work commits (DQ4)", ["project_potts", "artifact_lineage"])
            print(t, "allowed" if c["allowed"] else "BLOCKED", "disclosure needed" if c["needs_disclosure"] else "")
            if not c["allowed"]:
                sys.exit(f"refusing: {t} already used by the same estimator family")
    targets = TARGETS if real else STANDIN
    tail_units = TAIL_UNITS if real else STANDIN_TAIL
    res = {"mode": "confirm" if real else "dry-run", "targets": {}}
    for g in targets + (REPORT_ONLY if real else []):
        d = R.build_period(g, allow_holdout=real)
        res["targets"][f"G{g}"] = period_stats(d)
    d51 = R.build_period(51, allow_holdout=real)
    tail = period_stats(d51, units=tail_units)
    res["targets"]["51tail"] = tail
    band = fitness_band(51, real, tail_units)
    res["fitness_band_51tail"] = band
    scored = {k: v for k, v in res["targets"].items() if k in [f"G{g}" for g in targets] or k == "51tail"}
    p = tail["p"]
    res["C1"] = bool(p and p["lo"] > 1)
    res["C2"] = bool(p and band["lo"] is not None and band["lo"] <= p["est"] <= band["hi"])
    fs = [v["formation_share"] >= 0.6 for v in scored.values() if v["arrivals"] >= 20]
    res["C3"] = bool(fs) and sum(fs) >= 2 / 3 * len(fs)
    rec = sum(v["recruits"] for v in scored.values())
    res["C4"] = rec > 0 and sum(v["blind_touch"] for v in scored.values()) / rec <= 0.05
    res["C5"] = tail["recruits"] > 0 and tail["return_touch"] / tail["recruits"] >= 0.4
    a0 = [v["A0_p"] < 0.05 for v in scored.values() if v["A0_testable"] and v["A0_p"] is not None]
    res["C6"] = bool(a0) and sum(a0) >= len(a0) / 2
    OUT.mkdir(parents=True, exist_ok=True)
    name = "confirm.json" if real else "confirm_dryrun.json"
    (OUT / name).write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps({k: res[k] for k in ("C1", "C2", "C3", "C4", "C5", "C6")}, indent=1))


if __name__ == "__main__":
    main()
