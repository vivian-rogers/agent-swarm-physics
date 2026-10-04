"""H25 round 1b: write the `**Verdict (1b):**` line and a "Round 1b" section into each replication period README,
from the round-1 tables (data/processed/H25-criticality-dial/{dial_period,dial_daily,period_verdicts}.parquet) and the
round-1b tables (r1b/...). Idempotent. Native sections (NE43, G51, G40) are written by hand.
Usage: uv run python hypotheses/H25-criticality-dial/analysis/r1b_periods.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HYP = Path(__file__).resolve().parents[1]
DATA = HYP.parents[1] / "data/processed/H25-criticality-dial"

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402


def fmt(x, nd=2):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "–"
    return f"{x:.{nd}f}"


def per_get(per, g, ch, v, col):
    x = per.filter((pl.col("goal_no") == g) & (pl.col("channel") == ch) & (pl.col("variant") == v))
    return x[col][0] if x.height else None


def above(daily, g, ch, v):
    d = daily.filter((pl.col("goal_no") == g) & (pl.col("channel") == ch) & (pl.col("variant") == v) & (pl.col("flag") == "ok")
                     & pl.col("null_q95").is_not_null())
    return f"{int((d['g'] > d['null_q95']).sum())}/{d.height}" if d.height else "–"


def main():
    po, pn = pl.read_parquet(DATA / "dial_period.parquet"), pl.read_parquet(DATA / "r1b/dial_period.parquet")
    do, dn = pl.read_parquet(DATA / "dial_daily.parquet"), pl.read_parquet(DATA / "r1b/dial_daily.parquet")
    vo = {r["goal_no"]: r for r in pl.read_parquet(DATA / "period_verdicts.parquet").to_dicts()}
    vn = {r["goal_no"]: r for r in pl.read_parquet(DATA / "r1b/period_verdicts.parquet").to_dicts()}
    rows = []
    for g in sorted(vn):
        f = HYP / "goalperiod-subhypotheses" / f"G{g:02d}" / "README.md"
        if not f.exists():
            continue
        o, n = vo.get(g, {}), vn[g]
        tab = ["| Quantity | Round 1 (old table) | Round 1b (fixed table) |", "| --- | --- | --- |",
               f"| activity dial, stalls masked (fixed-effect mean; median) | {fmt(per_get(po, g, 'activity', 'auto', 'fe'))}; {fmt(per_get(po, g, 'activity', 'auto', 'median'))} | {fmt(per_get(pn, g, 'activity', 'auto', 'fe'))}; {fmt(per_get(pn, g, 'activity', 'auto', 'median'))} |",
               f"| activity dial, stalls kept vs H19 g_eq | {fmt(o.get('act_none'))} vs {fmt(o.get('h19_active'))} | {fmt(n.get('act_none'))} vs {fmt(n.get('h19f_active'))} (H19 estimator on the fixed table) |",
               f"| talk dial, stalls masked (fixed-effect; random-effects) | {fmt(per_get(po, g, 'talk', 'auto', 'fe'))}; {fmt(per_get(po, g, 'talk', 'auto', 're'))} | {fmt(per_get(pn, g, 'talk', 'auto', 'fe'))}; {fmt(per_get(pn, g, 'talk', 'auto', 're'))} |",
               f"| talk dial, stalls kept vs H19 g_eq talk | {fmt(o.get('talk_none'))} vs {fmt(o.get('h19_talk'))} | {fmt(n.get('talk_none'))} vs {fmt(n.get('h19f_talk'))} |",
               f"| days above the block-shift null q95: activity (round-1 design → **DQ8 trim**) | {above(do, g, 'activity', 'auto')} | {above(dn, g, 'activity', 'auto')} → {above(dn, g, 'activity', 'trim')} |",
               f"| median activity dial with the DQ8 trim | – | {fmt(per_get(pn, g, 'activity', 'trim', 'median'))} |",
               f"| content dial F2 median (inputs unchanged) | {fmt(o.get('content_med'))} | {fmt(n.get('content_med'))} |",
               f"| per-period verdict (card rule) | {o.get('verdict', '–')} | {n['verdict']} |"]
        sec = ("## Round 1b (improved data, 2026-10-04)\n"
               "Same pipeline (`analysis/explore.py --data-version fixed`) on DQ8's `activity_bins_fixed` and the shared `outages_fixed` stall "
               "table (round 1's activity table dropped about half of all events). Predictions and verdict rule unchanged; check (ii) now compares "
               "with H19's estimator recomputed on the fixed table (round-1 H19 values are stale). The DQ8 row trims each day to the window in "
               "which all agents are between their first and last active minute before the block-shift null is drawn (whole-day block-shift "
               "nulls reject 28–34% of independent swarms).\n\n" + "\n".join(tab) +
               f"\n\nData: `data/processed/H25-criticality-dial/r1b/G{g:02d}/`.\n")
        t = f.read_text()
        line = f"**Verdict (1b):** {n['verdict']} (round 1: {o.get('verdict', '–')}; corrected table, same rule)"
        if "**Verdict (1b):**" in t:
            t = re.sub(r"\*\*Verdict \(1b\):\*\*.*", line, t, count=1)
        else:
            t = re.sub(r"(\*\*Verdict:\*\*.*\n)", r"\1" + line + "\n", t, count=1)
        if "## Round 1b (improved data" in t:
            t = re.sub(r"## Round 1b \(improved data.*?(?=\n## Notes)", sec.rstrip("\n") + "\n", t, flags=re.S)
        else:
            t = t.replace("\n## Notes", "\n" + sec + "\n## Notes", 1)
        f.write_text(t)
        rows.append({"goal_no": g, "v_r1": o.get("verdict"), "v_r1b": n["verdict"]})
    df = pl.DataFrame(rows)
    df.write_parquet(DATA / "r1b/verdict_changes.parquet")
    print(df.filter(pl.col("v_r1") != pl.col("v_r1b")))
    print(df.group_by("v_r1b").len())


if __name__ == "__main__":
    main()
