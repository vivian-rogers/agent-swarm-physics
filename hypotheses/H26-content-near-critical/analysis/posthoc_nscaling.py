"""POST HOC (2026-10-04, prompted by H25's cross-hypothesis finding; not pre-registered): does the per-pair correlation
behind each channel's loop gain stay flat in room size (shared-field signature: rho const, g rises with N) or fall as
1/(N-1) (coupling normalized by N: g const)?

Fits log(rho) = c + alpha * log(N_r - 1) across H26 units, per channel and resolution, for
  (i)  within-room rho_w at L2 (all 15 units; includes any global drive; one-room units are upper bounds), and
  (ii) the room excess rho_ex at L3 (10 regime-III two-room units + #35; narrow N range, 6.5-9.6).
alpha ~ 0: shared field / constant per-pair correlation; alpha ~ -1: J0/N coupling; H18 found J ~ N^-0.6 for talk uptake.
Bootstrap over units for the CI. Cross-reference: H25's daily content g (dial_daily.parquet) on the same periods.

Usage: uv run python hypotheses/H26-content-near-critical/analysis/posthoc_nscaling.py
Writes data/processed/H26-content-near-critical/posthoc_nscaling.json
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
D = ROOT / "data/processed/H26-content-near-critical"


def fit(x, y, rng, B=2000):
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    if len(x) < 4:
        return None
    a = np.polyfit(x, y, 1)[0]
    bs = []
    for _ in range(B):
        i = rng.integers(0, len(x), len(x))
        if np.ptp(x[i]) > 0:
            bs.append(np.polyfit(x[i], y[i], 1)[0])
    return {"alpha": float(a), "ci": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))], "n": int(len(x))}


def main():
    rng = np.random.default_rng(20261004)
    R = json.loads((D / "summary_units.json").read_text())
    out = {"label": "POST HOC, cross-hypothesis (H25); not pre-registered"}
    for res in ("day", "w30"):
        for ch in ("c", "a", "k"):
            N = np.array([r.get(f"{ch}_{res}_Nr") or np.nan for r in R], float)
            rw = np.array([r.get(f"{ch}_{res}_rho_w") or np.nan for r in R], float)
            rw = np.where(rw > 0, rw, np.nan)
            out[f"{ch}_{res}_rho_w_L2_all_units"] = fit(np.log(N - 1), np.log(rw), rng)
            two = [r for r in R if r["two_room"]]
            N2 = np.array([r.get(f"{ch}_{res}_Nr") or np.nan for r in two], float)
            rex = np.array([r.get(f"{ch}_{res}_rho") if r.get(f"{ch}_{res}_rho") is not None else np.nan for r in two], float)
            rex = np.where(rex > 0, rex, np.nan)
            out[f"{ch}_{res}_rho_ex_L3_two_room"] = fit(np.log(N2 - 1), np.log(rex), rng)
            out[f"{ch}_{res}_table"] = [{"unit": r["unit"], "Nr": r.get(f"{ch}_{res}_Nr"), "rho_w": r.get(f"{ch}_{res}_rho_w"),
                                         "rho_L3_or_L2": r.get(f"{ch}_{res}_rho"), "g": r.get(f"{ch}_{res}_g")} for r in R]
    # cross-reference with H25's daily dial (content and activity), per goal period, non-holdout periods H26 used
    f = ROOT / "data/processed/H25-criticality-dial/dial_daily.parquet"
    if f.exists():
        d = pl.read_parquet(f)
        goals = sorted({r["goal_no"] for r in R})
        sub = d.filter(pl.col("goal_no").is_in(goals))
        cols = [c for c in ("channel", "variant") if c in sub.columns]
        agg = (sub.group_by(["goal_no"] + cols).agg(pl.col("g").median().alias("g_median"), pl.col("N").median().alias("N_median"),
                                                     pl.len().alias("n_days")).sort(["goal_no"] + cols))
        out["h25_dial_by_period"] = agg.to_dicts()
    (D / "posthoc_nscaling.json").write_text(json.dumps(out, indent=1, default=float))
    for k, v in out.items():
        if k.endswith("units") or k.endswith("two_room"):
            print(k, None if v is None else f"alpha {v['alpha']:+.2f} [{v['ci'][0]:+.2f}, {v['ci'][1]:+.2f}] n {v['n']}")


if __name__ == "__main__":
    main()
