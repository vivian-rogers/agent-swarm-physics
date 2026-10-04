"""H43 replication layer: the common estimator on one non-holdout goal period (units of period_units are strata).

Classes N (nudge), H (human message), A (@-mention); outcomes O1 (idle-at-read escape, 15 min), O2 (busy recipient
talks within 5 min), O2c (the receiving call talks), O3 (busy recipient writes within 30 min; regime III).
Templated verdict (card, "Replication layer"): every powered class (>= 20 primers and >= 20 second kicks in the primary
read state) with E1 > 0 has R(short) < R(long) and delta_half within a factor 2 of the launched-episode median L.

Usage:  uv run python hypotheses/H43-kick-refractory-window/analysis/run_period.py --period G38 [--B 300]
        uv run python hypotheses/H43-kick-refractory-window/analysis/run_period.py --all
Output: data/processed/H43-kick-refractory-window/G<NN>/results.json
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h43lib as L  # noqa: E402

OUTCOMES = ("O1", "O2", "O2c", "O3", "O1a")


def class_test(res: dict, cl: str) -> dict:
    """Templated replication test for one class in one period (primary outcome)."""
    o = res.get("outcomes", {}).get(L.PRIMARY[cl])
    if not o or "skipped" in o:
        return {"testable": False, "why": "no primers in the primary read state"}
    n_prim = o["E1"]["n"]
    n_sec = sum(v.get("n", 0) for v in o.get("E2_bins", {}).values())
    out = {"n_primers": n_prim, "n_second": n_sec, "E1": o["E1"]["est"], "E1_lo": o["E1"]["lo"],
           "E1_hi": o["E1"]["hi"], "E1_positive": o["E1_positive"], "L_median": res.get("L_median")}
    if n_prim < 20 or n_sec < 20:
        return {**out, "testable": False, "why": "underpowered (< 20 primers or < 20 second kicks)"}
    if not o["E1_positive"]:
        return {**out, "testable": False, "why": "no first-kick effect (E1 CI includes 0)"}
    rs, rl, fit = o.get("R_short"), o.get("R_long"), o.get("fit")
    rising = bool(rs and rl and rs["bin"] != rl["bin"] and np.isfinite(rs["est"]) and np.isfinite(rl["est"])
                  and rs["est"] < rl["est"])
    Lm = res.get("L_median")
    dh = fit["delta_half"] if fit else np.nan
    win = bool(fit and np.isfinite(Lm) and np.isfinite(dh) and dh > 0 and Lm / 2 <= dh <= 2 * Lm)
    p1 = bool(rs and rl and np.isfinite(rs["est"]) and rs["est"] <= 0.5 and np.isfinite(rs["hi"]) and rs["hi"] < 1
              and np.isfinite(rl["est"]) and rl["est"] >= 0.7)
    return {**out, "testable": True, "R_short": rs, "R_long": rl, "rising": rising, "delta_half": dh,
            "delta_half_ci": [fit["delta_half_lo"], fit["delta_half_hi"]] if fit else None,
            "window_tracks_episode": win, "P1_window_exists": p1, "pass": rising and win}


def verdict(tests: dict) -> str:
    t = [v for v in tests.values() if v.get("testable")]
    if not t:
        return "descriptive"
    n = sum(v["pass"] for v in t)
    return "supported" if n == len(t) else ("failed" if n == 0 else "mixed")


def run(goal_no: int, B: int, label: str | None = None, **kw) -> dict:
    t0 = time.time()
    calls, states, writes, cal = L.load_real(goal_no, **kw)
    if calls.height == 0:
        return {}
    P = L.Prep(calls, states, writes, cal)
    rng = np.random.default_rng(L.SEED + goal_no)
    draws = L.day_draws(len(P.days), B, rng)
    res = {"period": label or f"G{goal_no:02d}", "goal_no": goal_no, "days": P.days, "n_days": len(P.days),
           "units": P.units, "n_calls": P.n, "n_agents": int(len(np.unique(P.agent))),
           "regime": sorted(calls["regime"].unique().to_list()), "writes_per_agentday": P.writes_per_agentday,
           "idle_at_read_share": float(P.idle_at_read.mean()), "B": B, "classes": {}}
    for cl in L.CLASSES:
        res["classes"][cl] = L.analyze_class(P, cl, rng, B=B, outcomes=OUTCOMES, draws=draws)
    res["tests"] = {cl: class_test(res["classes"][cl], cl) for cl in L.CLASSES}
    res["verdict_templated"] = verdict(res["tests"])
    res["secs"] = round(time.time() - t0, 1)
    res["git_commit"] = L.git_commit()
    res["built_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    return res


def eligible_periods() -> list[int]:
    c = pl.read_parquet(L.OUT / "calls.parquet", columns=["goal_no"])
    return sorted(int(g) for g in c["goal_no"].unique().to_list())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", default=None)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--B", type=int, default=L.B_BOOT)
    ap.add_argument("--skip-existing", action="store_true")
    a = ap.parse_args()
    gs = eligible_periods() if a.all else [int(a.period.lstrip("G"))]
    for g in gs:
        out = L.OUT / f"G{g:02d}" / "results.json"
        if a.skip_existing and out.exists():
            continue
        res = run(g, a.B)
        if not res:
            continue
        L.jdump(res, out)
        t = res["tests"]
        print(f"G{g:02d} {res['secs']}s calls {res['n_calls']} verdict {res['verdict_templated']} | " +
              " ".join(f"{cl}:{'T' if v.get('testable') else '-'}" for cl, v in t.items()), flush=True)


if __name__ == "__main__":
    main()
