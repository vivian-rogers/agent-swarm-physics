"""H43 operator rule (deliverable): minimum kick spacing per kick type, with measured reliability.

For each kick type, in its best-powered non-holdout setting:
  mention  (A)  G51, busy recipients, O2c (the receiving call replies) and O2 (talks within 5 min)
  nudge    (N)  G51 before 08-21, idle recipients, O1a (any activity; post hoc) and O1 (sustained escape)
  human    (H)  G04 units 4a+4c, 5-min quiet rule, O2c and O2
Reported: R for spacings (0, 15], (15, 60], (60, 240] min and for a second kick read in the same call (batched);
the bootstrap share of draws with delta_half < 2 min (no window beyond one read-out); split-half (odd vs even days)
estimates of the same quantities. The rule is: minimum spacing = upper 80% bootstrap bound of delta_half, or "one
receiving call" when that bound is below the shortest populated spacing bin.
Usage:  uv run python hypotheses/H43-kick-refractory-window/analysis/rule.py
Output: data/processed/H43-kick-refractory-window/rule.json
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h43lib as L  # noqa: E402

SETTINGS = {
    "A": dict(goal=51, kw={}, outcomes=("O2c", "O2"), quiet=L.QUIET_S),
    "N": dict(goal=51, kw={"date_to": "2026-08-21"}, outcomes=("O1a", "O1"), quiet=L.QUIET_S),
    "H": dict(goal=4, kw={"units": ["4a", "4c"]}, outcomes=("O2c", "O2"), quiet=300.0),
}


def extract(res: dict, o: str) -> dict:
    od = res.get("outcomes", {}).get(o, {})
    if "E1" not in od:
        return {}
    fit = od.get("fit") or {}
    db = fit.get("draw_bins", {})
    tot = sum(db.values()) if db else 0
    return {"E1": od["E1"], "E1_positive": od.get("E1_positive"),
            "R_pool": {k: {"R": v["R"], "n": v["n"]} for k, v in od.get("R_pool", {}).items()},
            "batched": od.get("batched"),
            "delta_half": fit.get("delta_half"), "delta_half_p80": fit.get("delta_half_p80"),
            "share_draws_window_lt_2min": (db.get("none", 0) + db.get("0-2", 0)) / tot if tot else None,
            "bins": {k: {"R": v.get("R"), "n": v.get("n")} for k, v in od.get("E2_bins", {}).items() if v.get("n")}}


def run_subset(cl, st, days, rng, B):
    calls, states, writes, cal = L.load_real(st["goal"], **st["kw"])
    calls = calls.filter(pl.col("pt_date").is_in(days))
    states = states.filter(pl.col("pt_date").is_in(days))
    cal = cal.filter(pl.col("pt_date").is_in(days))
    P = L.Prep(calls, states, writes, cal)
    return L.analyze_class(P, cl, rng, B=B, outcomes=st["outcomes"], quiet_s=st["quiet"])


def main(B: int = 300):
    t0 = time.time()
    out = {"built_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "git_commit": L.git_commit(), "classes": {}}
    for cl, st in SETTINGS.items():
        rng = np.random.default_rng(L.SEED + 777)
        calls, states, writes, cal = L.load_real(st["goal"], **st["kw"])
        days = sorted(calls["pt_date"].unique().to_list())
        full = run_subset(cl, st, days, rng, B)
        halves = {h: run_subset(cl, st, days[i::2], rng, B) for h, i in (("odd", 0), ("even", 1))}
        rec = {"setting": {"goal": st["goal"], **st["kw"], "quiet_min": st["quiet"] / 60}, "n_days": len(days)}
        for o in st["outcomes"]:
            rec[o] = {"full": extract(full, o), **{h: extract(r, o) for h, r in halves.items()}}
            # split-half agreement on R(0-15] (or the shortest populated range) and on "no window beyond one call"
            f = rec[o]["full"]
            if f:
                rng_lab = next((k for k in ("0-15", "15-60", "60-240") if k in f["R_pool"]), None)
                ag = {}
                for h in ("odd", "even"):
                    hh = rec[o][h]
                    ag[h] = hh.get("R_pool", {}).get(rng_lab, {}).get("R", {}).get("est") if hh else None
                rec[o]["split_half"] = {"range": rng_lab, **ag,
                                        "both_ge_0p5": all(v is not None and v >= 0.5 for v in ag.values())}
        out["classes"][cl] = rec
        print(cl, "done", round(time.time() - t0, 1), flush=True)
    L.jdump(out, L.OUT / "rule.json")


if __name__ == "__main__":
    main()
