"""H12 round 1b: write the `**Verdict (1b):**` line and a "Round 1b" section into each replication period README, from
round 1 (data/processed/H12-groupthink-dimensional-collapse/{unit_table,period_results,period_means}) and round 1b
(r1b/{unit_table,period_results}, r1b/dq5/prday_gte.parquet). Idempotent. Native sections (G12, G26) are by hand.
Usage: uv run python hypotheses/H12-groupthink-dimensional-collapse/analysis/r1b_periods.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HYP = Path(__file__).resolve().parents[1]
DATA = HYP.parents[1] / "data/processed/H12-groupthink-dimensional-collapse"

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402


def fmt(x, nd=2):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "–"
    return f"{x:.{nd}f}" if isinstance(x, float) else str(x)


def main():
    uo, un = pl.read_parquet(DATA / "unit_table.parquet"), pl.read_parquet(DATA / "r1b/unit_table.parquet")
    vo = json.loads((DATA / "period_results.json").read_text())
    vn = json.loads((DATA / "r1b/period_results.json").read_text())
    units = pl.read_parquet(DATA / "r1b/units.parquet").select("unit", "goal_no")
    pg = (pl.read_parquet(DATA / "r1b/dq5/prday_gte.parquet").join(units, on="unit")
          .group_by("goal_no").agg(pl.col("prday").drop_nans().mean().alias("prday_gte")))
    pm = pl.read_parquet(DATA / "period_means.parquet").select("goal_no", "prday_mean")
    rows = []
    for g in sorted(int(k) for k in vn):
        f = HYP / "goalperiod-subhypotheses" / f"G{g:02d}" / "README.md"
        if not f.exists():
            continue
        a, b = uo.filter(pl.col("goal_no") == g).sort("unit"), un.filter(pl.col("goal_no") == g).sort("unit")
        def col(df, c, nd=2):
            return ", ".join(fmt(v, nd) if isinstance(v, float) else fmt(v) for v in df[c].to_list()) if df.height else "–"
        p1 = pm.filter(pl.col("goal_no") == g)["prday_mean"]; p2 = pg.filter(pl.col("goal_no") == g)["prday_gte"]
        tab = ["| Quantity (per unit) | Round 1 (old table) | Round 1b (fixed table) |", "| --- | --- | --- |",
               f"| units | {col(a, 'unit')} | {col(b, 'unit')} |",
               f"| k activity (cross-day edge) | {col(a, 'k_cd')} | {col(b, 'k_cd')} |",
               f"| λ₁/edge activity (cross-day) | {col(a, 'l1_edge')} | {col(b, 'l1_edge')} |",
               f"| k after the lull filter (joint-lull share) | {col(a, 'k_lull')} ({col(a, 'lull_frac')}) | {col(b, 'k_lull')} ({col(b, 'lull_frac')}) |",
               f"| **DQ8 null:** k activity, trimmed + block-shift edge (λ₁/edge) | not computed | {col(b, 'k_trim')} ({col(b, 'l1_edge_trim')}) |",
               f"| DQ8: k activity, trimmed + H38 stall mask (replaces the lull filter) | not computed | {col(b, 'k_trim_stall')} |",
               f"| k talk (cross-day) → trimmed block-shift | {col(a, 'k_talk')} | {col(b, 'k_talk')} → {col(b, 'k_talk_trim')} |",
               f"| k content (inputs unchanged) | {col(a, 'k_content')} | {col(b, 'k_content')} |",
               f"| mean PRday: round-1 bge ruler → gte (shared 32-d, second model) | {fmt(float(p1[0])) if p1.len() else '–'} | {fmt(float(p2[0])) if p2.len() else '–'} (gte) |",
               f"| per-period verdict (card rule, Amendment 1 item 9) | {vo.get(str(g), {}).get('verdict', '–')} | {vn[str(g)]['verdict']} |"]
        sec = ("## Round 1b (improved data, 2026-10-04)\n"
               "Arm (a) spins rebuilt from DQ8's `activity_bins_fixed` (`scheme/build.py`, `run_units.py`, `evaluate.py --data-version fixed`); "
               "content and PR inputs do not depend on the activity table and are unchanged (re-checked with the second embedding model). "
               "Predictions and verdict rule unchanged. The DQ8 rows use the calibrated null for λ₁: each day trimmed to its all-present window "
               "*before* drawing block-shift surrogates (size 0.05; the cross-day edge has size 0.19 on trimmed and 0.62 on whole-day grids).\n\n"
               + "\n".join(tab) + f"\n\nData: `data/processed/H12-groupthink-dimensional-collapse/r1b/G{g:02d}/`.\n")
        t = f.read_text()
        v_old, v_new = vo.get(str(g), {}).get("verdict", "–"), vn[str(g)]["verdict"]
        line = f"**Verdict (1b):** {v_new} (round 1: {v_old}; corrected activity table, same rule)"
        if "**Verdict (1b):**" in t:
            t = re.sub(r"\*\*Verdict \(1b\):\*\*.*", line, t, count=1)
        else:
            t = re.sub(r"(\*\*Verdict:\*\*.*\n)", r"\1" + line + "\n", t, count=1)
        if "## Round 1b (improved data" in t:
            t = re.sub(r"## Round 1b \(improved data.*?(?=\n## Notes)", sec.rstrip("\n") + "\n", t, flags=re.S)
        elif "\n## Notes" in t:
            t = t.replace("\n## Notes", "\n" + sec + "\n## Notes", 1)
        else:
            t = t.rstrip("\n") + "\n\n" + sec
        f.write_text(t)
        rows.append({"goal_no": g, "v_r1": v_old, "v_r1b": v_new})
    df = pl.DataFrame(rows)
    df.write_parquet(DATA / "r1b/verdict_changes.parquet")
    print(df.filter(pl.col("v_r1") != pl.col("v_r1b")))
    print(df.group_by("v_r1b").len())


if __name__ == "__main__":
    main()
