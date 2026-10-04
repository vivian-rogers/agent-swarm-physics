"""H03 round 1b: per-period estimates into the shared table (infra/shared/estimates.py: write_estimates).
Rows: Hawkes branching ratio n-hat (M1_B2, TALK and ALL) and fast cross-agent triggering n_x per goal period on the
round-1b inputs (replication), and per-unit n-hat TALK for #51 under the shared period_units split (native N sweep).
Usage: uv run python hypotheses/H03-self-excited-criticality/analysis/r1b_estimates.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

D = ROOT / "data/processed/H03-self-excited-criticality/r1b"
NOTE = "round 1b (2026-10-04): exogenous drive from kicks_classified (bookends excluded), days split at operator-off gaps >= 60 min"
METHOD = "pooled univariate Hawkes M1_B2 (exp kernel, per-day level x 30-min shape + kickoff bump, human + nudge drive)"


def main():
    t = pl.read_parquet(D / "period_table.parquet")
    tn = pl.read_parquet(D / "trim_null.parquet")
    rows = []
    for r in t.iter_rows(named=True):
        boot = r.get("n_boot_lo") is not None
        lo, hi = (r["n_boot_lo"], r["n_boot_hi"]) if boot else (r["n_prof_lo"], r["n_prof_hi"])
        hi = None if hi is not None and hi == float("inf") else hi
        unit = E.map_unit(r["goal_no"])
        rows.append({"period_unit": unit, "goal_no": r["goal_no"], "statistic": "hawkes_branching_n", "channel": r["set"],
                     "estimate": r["n"], "ci_lo": lo, "ci_hi": hi, "ci_level": 0.95, "ci_kind": "percentile" if boot else "profile",
                     "n": r["n_days"], "n_kind": "days", "method": METHOD + ("; day bootstrap B = 50" if boot else "; profile likelihood"),
                     "null": "inhomogeneous Poisson with the same baseline", "role": "replication", "status": "ok",
                     "source": str((D / "period_table.parquet").relative_to(ROOT)), "notes": NOTE})
        z = tn.filter((pl.col("goal_no") == r["goal_no"]) & (pl.col("set") == r["set"]))
        zt = z.to_dicts()[0] if z.height else {}
        rows.append({"period_unit": unit, "goal_no": r["goal_no"], "statistic": "fast_cross_n_x", "channel": r["set"],
                     "estimate": r["n_cross_fast"], "ci_lo": r.get("n_cross_fast_boot_lo"), "ci_hi": r.get("n_cross_fast_boot_hi"),
                     "ci_level": 0.95, "ci_kind": "percentile" if r.get("n_cross_fast_boot_lo") is not None else "none",
                     "n": r["N_active"], "n_kind": "agents",
                     "method": "M3 self/cross Hawkes, fast (tau <= 300 s) cross-agent offspring per event; day bootstrap B = 25",
                     "null": "agent-shift (+-5-30 min per agent), 5 surrogates; corrected: drawn after trimming to the all-present window",
                     "role": "replication", "status": "ok", "source": str((D / "period_table.parquet").relative_to(ROOT)),
                     "notes": f"{NOTE}; shift null mean {r.get('shift_null_fast')}; trimmed: n_x {zt.get('nx_trim')} vs null {zt.get('shift_trim_mean')}"})
    seg = pl.read_parquet(D / "segments.parquet").filter((pl.col("rule") == "pu") & (pl.col("goal_no") == 51) &
                                                       (pl.col("model") == "M1_B2") & (pl.col("set") == "TALK"))
    for r in seg.iter_rows(named=True):
        hi = None if r["n_prof_hi"] == float("inf") else r["n_prof_hi"]
        rows.append({"period_unit": r["seg"], "goal_no": 51, "statistic": "hawkes_branching_n", "channel": "TALK", "estimate": r["n"],
                     "ci_lo": r["n_prof_lo"], "ci_hi": hi, "ci_level": 0.95, "ci_kind": "profile", "n": r["N_active"], "n_kind": "agents",
                     "method": METHOD + "; one fit per shared period unit; profile likelihood", "null": "inhomogeneous Poisson",
                     "role": "native", "status": "ok", "source": str((D / "segments.parquet").relative_to(ROOT)),
                     "notes": f"{NOTE}; #51 N sweep (N51-a supported: rho(n, N) = -0.70)"})
    out = E.write_estimates(rows, hypothesis="H03")
    print(out.height, "rows written")


if __name__ == "__main__":
    main()
