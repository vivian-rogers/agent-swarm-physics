"""Write H114 goal-period folders before the real-data run (predictions only). G51 is written by hand (native).

Usage: uv run python hypotheses/H114-griffiths-phase-pairs/analysis/write_period_folders.py --pre
"""
from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data/processed/H114-griffiths-phase-pairs"
GP = ROOT / "hypotheses/H114-griffiths-phase-pairs/goalperiod-subhypotheses"
NATIVE = {39: "NE42", 40: "NE42", 41: "NE42"}


def pre():
    m = pl.read_parquet(OUT / "unit_meta.parquet").filter(pl.col("eligible"))
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    n = 0
    for (g,), grp in m.group_by(["goal_no"]):
        g = int(g)
        if g == 51:
            continue
        d = GP / f"G{g:02d}"
        (d / "figures").mkdir(parents=True, exist_ok=True)
        role = "replication" + (f" (+ {NATIVE[g]} native, separate folder)" if g in NATIVE else "")
        reg = grp["regime"][0]
        txt = f"""# H114 × G{g:02d}: goal period #{g}

**Verdict:** pending
**Role:** {role} (exploratory)
**Period:** goal #{g} · regime {reg} · units {", ".join(sorted(grp["unit_id"].to_list()))} · {int(grp["n_days"].sum())} non-holdout days · {int(grp["n_agents"].max())} authors.

## Why this period
Eligible for the replication layer (≥ 300 agent messages and ≥ 100 DQ2 agent-to-agent parent links in at least one unit).

## Prediction
*Written {stamp}, before running on this period (after Amendment A1). No H114 statistic seen.*
The card's per-period rule on the random-effects pool of its units: supported if Δh > 0 (CI excluding 0), the period has ≥ 1 strong pair (lower bound of g_ij > 0.5, R_ij ≥ 10) and the strong-pair cut brings Δh′ within CI of 0 and below the 5th percentile of matched random cuts; failed if Δh's CI includes 0 or lies below 0 (tail not heavier than geometric), or if Δh > 0 with no strong pair (the HH's kill); mixed if strong pairs exist but do not carry the excess; descriptive with fewer than 100 links or fewer than 30 messages at depth ≥ 4. The card expects Δh > 0 (credence 0.75) and strong pairs in only about a third of units (0.35); A1: a missing strong pair rules out only pairs with g ≳ 0.7.

## Result
(pending)

## Scorecard (period-specific axes)
C (Δh against M0 and M1), H (M1 vs M2 vs thread momentum).

## Notes
"""
        (d / "README.md").write_text(txt)
        n += 1
    print("wrote", n)


if __name__ == "__main__" and "--pre" in __import__("sys").argv:
    pre()


def f_(x, d=3):
    import math
    try:
        return "–" if x is None or not math.isfinite(float(x)) else f"{float(x):.{d}f}"
    except (TypeError, ValueError):
        return "–"


def post():
    import re
    U = pl.read_parquet(OUT / "results/units.parquet")
    P = pl.read_parquet(OUT / "results/periods.parquet")
    for r in P.iter_rows(named=True):
        g = r["goal_no"]
        f = GP / f"G{g:02d}" / "README.md"
        if not f.exists():
            continue
        txt = f.read_text()
        txt = re.sub(r"\*\*Verdict:\*\* .*", f"**Verdict:** {r['verdict']}", txt, count=1)
        rows = U.filter(pl.col("goal_no") == g).sort("unit_id")
        tab = ["| Unit | msgs in window | g_rep | h(1) | h_tail (d ≥ 4) | Δh [95%] | δh [95%] | h_tail M1 / M2 | strong pairs | strong-link share | Δh′ after cut (random-cut 5th pct) |",
               "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for u in rows.iter_rows(named=True):
            tab.append(f"| {u['unit_id']} | {u['n_msgs_win']} | {f_(u['g_rep'])} | {f_(u['h_1'])} | {f_(u['h_tail'])} | "
                       f"{f_(u['dh'])} [{f_(u['dh_lo'])}, {f_(u['dh_hi'])}] | {f_(u['delta_h'])} [{f_(u['delta_h_lo'])}, {f_(u['delta_h_hi'])}] | "
                       f"{f_(u['h_tail_M1'])} / {f_(u['h_tail_M2'])} | {u['n_strong']} | {f_(u['strong_link_share'])} | "
                       f"{f_(u.get('dh_cut'))} ({f_(u.get('dh_rand_q05'))}) |")
        res = (f"*Run 2026-10-04 ~21:55 UTC (non-holdout units).* Period pool (random effects over usable units): "
               f"**Δh = {f_(r['dh'])} [{f_(r['dh_lo'])}, {f_(r['dh_hi'])}]**, δh = {f_(r['delta_h'])} "
               f"[{f_(r['delta_h_lo'])}, {f_(r['delta_h_hi'])}], {r['n_strong']} strong directed pairs in "
               f"{r['n_units_strong']} unit(s), the cut carries the excess in {r['n_units_carry']}. "
               f"Verdict by the card's rule: **{r['verdict']}**.\n\n" + "\n".join(tab) +
               "\n\nData: `data/processed/H114-griffiths-phase-pairs/results/units.parquet`, `pairs.parquet`, `periods.parquet`.")
        txt = re.sub(r"## Result\n.*?\n## Scorecard", "## Result\n" + res + "\n\n## Scorecard", txt, count=1, flags=re.S)
        f.write_text(txt)
    print("filled", P.height)


if __name__ == "__main__" and "--post" in __import__("sys").argv:
    post()
