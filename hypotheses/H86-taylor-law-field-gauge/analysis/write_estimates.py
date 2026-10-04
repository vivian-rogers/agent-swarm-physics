"""Write H86 per-unit gauge rows to the shared per_period_estimates table (infra/shared/estimates.py).

Replication rows per non-holdout unit and channel_grid (activity, calls, msg: 15-min bins; commit: 60-min bins):
  taylor_c_shared       c_x = sum_{i<j} Cov_ij / sum_{i<j} mu_i mu_j  (the field gauge; day-bootstrap percentile CI)
  taylor_phi_shared     shared share of super-Poisson variance
  taylor_c_T            quadratic Taylor coefficient across agents (V = a mu + c_T mu^2), the HH's c
  taylor_b              Taylor exponent across agents (slope of ln V on ln mu)
  taylor_c_shared_within_day  (trimmed grids) within-day part with the within-day circular-shift null
Recommended join for other hypotheses: statistic = taylor_c_shared, channel = activity_trim (and activity_raw).
NE14 and NE43 are transition contrasts and are not written.
Usage: uv run python hypotheses/H86-taylor-law-field-gauge/analysis/write_estimates.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h86lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra" / "shared"))
import estimates as E  # noqa: E402

SRC = "data/processed/H86-taylor-law-field-gauge/replication/gauge.parquet"


def nz(x):
    return None if x is None or (isinstance(x, float) and not np.isfinite(x)) else float(x)


def main():
    g = pl.read_parquet(L.ROOT / SRC)
    pu = pl.read_parquet(L.ROOT / "data/processed/shared/period_units.parquet").select("unit_id", "first_day", "last_day")
    g = g.join(pu, on="unit_id")
    rows = []
    for r in g.iter_rows(named=True):
        ch, gr = r["channel"], r["grid"]
        if not np.isfinite(r["c_x"] if r["c_x"] is not None else np.nan):
            continue
        base = {"period_unit": r["unit_id"], "goal_no": r["goal_no"], "role": "replication", "source": SRC,
                "first_day": r["first_day"], "last_day": r["last_day"], "channel": f"{ch}_{gr}",
                "n": r["n_agents"], "n_kind": "agents"}
        binw = f"{r['bin_min']}-min bins"
        gdesc = "raw window grid (zeros outside agent spans)" if gr == "raw" else "DQ8 all-present trimmed grid"
        stats = [("taylor_c_shared", "c_x", "pair covariance / product of means over common cells", "independent agents: 0"),
                 ("taylor_phi_shared", "phi", "c_x * sum mu^2 / sum (V - mu)", None),
                 ("taylor_c_T", "c_T", "OLS of Fano factor on mean across agents (V = a mu + c_T mu^2)", "Poisson: 0"),
                 ("taylor_b", "b", "OLS slope of ln V on ln mu across agents", "Poisson: 1")]
        if ch in ("calls", "commit"):
            stats = [s for s in stats if s[0] in ("taylor_c_shared", "taylor_b")]
        for stat, key, meth, null in stats:
            lo, hi = r.get(f"{key}_lo"), r.get(f"{key}_hi")
            has = lo is not None and hi is not None and np.isfinite(lo) and np.isfinite(hi)
            rows.append({**base, "statistic": stat, "estimate": nz(r[key]), "ci_lo": nz(lo) if has else None,
                         "ci_hi": nz(hi) if has else None, "ci_level": 0.95 if has else None,
                         "ci_kind": "percentile" if has else "none", "method": f"{meth}; {binw}; {gdesc}; "
                         f"day bootstrap (>= 3 days) else 1-h blocks", "null": null,
                         "notes": "bootstrap CIs under-cover (synthetic 0.7-0.8); see H86 card A2" if has else None})
        if gr == "trim" and r.get("c_xw") is not None and np.isfinite(r["c_xw"]):
            rows.append({**base, "statistic": "taylor_c_shared_within_day", "estimate": nz(r["c_xw"]), "ci_lo": nz(r.get("c_xw_lo")),
                         "ci_hi": nz(r.get("c_xw_hi")), "ci_level": 0.95, "ci_kind": "percentile",
                         "method": f"c_x on counts demeaned within agent-day; {binw}; trimmed grid",
                         "null": f"within-day circular shift (49): p = {r.get('c_xw_p')}, null mean {r.get('c_xw_null_mean')}"})
    rows = [x for x in rows if x["estimate"] is not None]
    for x in rows:
        if x["ci_lo"] is None or x["ci_hi"] is None or x["ci_lo"] > x["ci_hi"]:
            x["ci_lo"] = x["ci_hi"] = None
            x["ci_kind"], x["ci_level"] = "none", None
    out = E.write_estimates(rows, hypothesis="H86")
    print(f"wrote {out.height} rows")


if __name__ == "__main__":
    main()
