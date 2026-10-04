"""H123 O1 scheduler audit (runs FIRST, before any EP statistic). All units in data/processed/H123-.../steps.

Output: data/processed/H123-regime1-turn-sweep/results/audit.parquet (+ audit.json)
Usage: uv run python hypotheses/H123-regime1-turn-sweep/analysis/audit.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h123lib as L  # noqa: E402


def main():
    U = pl.read_parquet(L.OUT / "units.parquet")
    (L.OUT / "results").mkdir(exist_ok=True)
    rows = []
    for u in U.iter_rows(named=True):
        S = L.load_steps(u["unit"])
        rng = np.random.default_rng(123)
        ln = L.name_lift(S, rng=rng, n_null=50, boot_days=200 if u["n_days"] >= 2 else 0)
        for subset in ("all", "chat"):
            st = L.audit_unit(S, subset, n_shuffle=50, seed=1)
            if not st:
                continue
            cls = L.classify(st, ln if subset == "all" else None)
            row = {"unit": u["unit"], "goal_no": u["goal_no"], "regime": u["regime"], "subset": subset, "class": cls,
                   **{k: v for k, v in st.items() if not isinstance(v, list)},
                   **{f"{k}_lo": v[0] for k, v in st.items() if isinstance(v, list)},
                   **{f"{k}_hi": v[1] for k, v in st.items() if isinstance(v, list)}}
            if subset == "all":
                row.update({"L_name": ln.get("L_name"), "L_name_lo": (ln.get("ci") or [np.nan, np.nan])[0],
                            "L_name_hi": (ln.get("ci") or [np.nan, np.nan])[1], "L_name_null_q95": ln.get("null_q95"),
                            "L_name_p": ln.get("p")})
            rows.append(row)
            print(u["unit"], subset, cls, {k: round(v, 3) for k, v in row.items() if isinstance(v, float)}, flush=True)
    df = pl.DataFrame(rows)
    df.write_parquet(L.OUT / "results/audit.parquet")
    (L.OUT / "results/audit.json").write_text(json.dumps(rows, indent=1, default=float))


if __name__ == "__main__":
    main()
