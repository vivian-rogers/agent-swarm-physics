"""H46 round 2: write per-unit rows to the shared per_period_estimates table (non-reserved units only).

  NE41 forced-erasure percentile per regime-III unit (native): style gp, function words, content bge (scaled, A5).
  Context-held state per regime-III goal period (replication): dC(1) within minus across forced erasures (gp, gap-matched)
  and the self-pull contrast rho_within - rho_forced.
Usage: uv run python hypotheses/H46-style-conserved-charge/analysis/r2_estimates.py
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h46lib as L  # noqa: E402
import r2lib as R  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
import estimates as E  # noqa: E402


def main():
    r1 = json.loads((R.R2 / "r1.json").read_text())
    r2 = json.loads((R.R2 / "r2.json").read_text())
    r3 = json.loads((R.R2 / "r3.json").read_text())
    m = R.load()
    span = {u: (g["pt_date"].min(), g["pt_date"].max(), int(g["goal_no"][0]))
            for (u,), g in m.group_by(["unit2"])}
    pu = set(pl.read_parquet(L.SH / "period_units.parquet")["unit_id"].to_list())
    rows = []
    src1 = "data/processed/H46-style-conserved-charge/r2/r1.json"
    src3 = "data/processed/H46-style-conserved-charge/r2/r3.json"
    for ch, block, src in (("style_gp", r1["NE41"]["gp"], src1), ("function_words", r3["NE41"]["fw"], src3),
                           ("content_bge", r1["NE41"]["content_bge"], src1)):
        for u, v in block["forced"]["per_unit"].items():
            f, l_, g = span[u]
            rows.append({"period_unit": u if u in pu else f"local:{u}", "unit_local": None if u in pu else u,
                         "goal_no": g, "statistic": "erasure_pair_percentile_T_forced", "channel": ch,
                         "estimate": v["T"], "ci_lo": None, "ci_hi": None, "ci_kind": "none", "n": v["n"],
                         "n_kind": "message pairs", "method": "NE41 gap-matched percentile, agent-unit scaled (R2-A5)",
                         "null": "same-agent within-context pairs at matched gap; 0.5", "role": "native",
                         "first_day": f, "last_day": l_, "post_hoc": False, "source": src,
                         "notes": "round 2; forced erasures; message pairs with >= 30 per unit"})
    src2 = "data/processed/H46-style-conserved-charge/r2/r2.json"
    multi = {36, 38, 42, 44, 51}
    for g, v in r2["gp"]["periods"].items():
        g = int(g)
        unit = f"G{g:02d}" if g in multi else str(g)
        c1 = v["cross"]["lags"]["1"]
        rows.append({"period_unit": unit, "goal_no": g, "statistic": "style_context_state_dC1", "channel": "style_gp",
                     "estimate": c1["dC"], "ci_lo": c1["dC_ci"][0], "ci_hi": c1["dC_ci"][1], "ci_level": 0.95,
                     "ci_kind": "percentile", "n": c1["n_across"], "n_kind": "lag-1 pairs across forced erasures",
                     "method": "cross-product within minus across a forced erasure, gap-reweighted; agent bootstrap",
                     "null": "0 (no context-held state)", "role": "replication", "post_hoc": False, "source": src2,
                     "notes": "round 2 R2-P2; clipped unit-centred 17-d style (R2-A1)"})
        p = v["pull"]
        rows.append({"period_unit": unit, "goal_no": g, "statistic": "style_selfpull_within_minus_erased",
                     "channel": "style_gp", "estimate": p["diff"], "ci_lo": p["diff_ci"][0], "ci_hi": p["diff_ci"][1],
                     "ci_level": 0.95, "ci_kind": "percentile", "n": p["n"]["forced"],
                     "n_kind": "messages after forced erasures", "method": "pull coefficient rho, gap x n_ref matched (R2-A4)",
                     "null": "0 (pull not held by the context)", "role": "replication", "post_hoc": False,
                     "source": src2, "notes": "round 2 R2-P3"})
    out = E.write_estimates(rows, hypothesis="H46")
    print(out.height, "rows written")


if __name__ == "__main__":
    main()
