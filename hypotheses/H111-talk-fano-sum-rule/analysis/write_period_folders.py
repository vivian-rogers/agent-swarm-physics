"""Write H111 goal-period folders. --pre: predictions only (before the real-data run). --post: fill results.

Usage: uv run python hypotheses/H111-talk-fano-sum-rule/analysis/write_period_folders.py --pre|--post
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import sys
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h111lib as L  # noqa: E402

CARD = L.ROOT / "hypotheses/H111-talk-fano-sum-rule"
GP = CARD / "goalperiod-subhypotheses"
H67 = L.ROOT / "data/processed/H67-lagged-criticality-dial/results/units.parquet"
NATIVE = {"39": "NE42", "40": "NE42", "41": "NE42", "36": "NE14"}


def f(x, d=2):
    return "–" if x is None or (isinstance(x, float) and not math.isfinite(x)) else f"{x:.{d}f}"


def pre():
    meta = pl.read_parquet(L.OUT / "unit_meta.parquet")
    g67 = pl.read_parquet(H67).select("unit_id", "g", "g_lo", "g_hi")
    m = meta.join(g67, on="unit_id", how="left")
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    for gno, grp in m.group_by("goal_no"):
        gno = int(gno[0])
        rows = grp.sort("unit_id")
        reg = rows["regime"][0]
        d = GP / f"G{gno:02d}"
        (d / "figures").mkdir(parents=True, exist_ok=True)
        units = ", ".join(rows["unit_id"].to_list())
        ndays = int(rows["n_days"].sum())
        npres = rows["n_present_mean"].mean()
        lines = [f"| {r['unit_id']} | {f(r['g'], 3)} [{f(r['g_lo'], 3)}, {f(r['g_hi'], 3)}] | "
                 f"{f(1 / (1 - r['g']) ** 2 if r['g'] is not None and r['g'] < 1 else None)} |"
                 for r in rows.iter_rows(named=True)]
        role = "replication" + (f" (+ {NATIVE[str(gno)]} native, separate folder)" if str(gno) in NATIVE else "")
        if gno == 51:
            role = "replication (+ NE43 native on 51f/51g/51h, separate folder)"
        exp = ("g_lag ≈ 0 in regime I, so the sum rule predicts Φ ≈ 1; the card expects an excess (P4: Φ(10) > 1.2, "
               "a field)." if reg == "I" else
               "g_lag ≈ 0 in regime II (H67), so the sum rule predicts Φ ≈ 1." if reg == "II" else
               "Regime III: the sum rule predicts Φ ≈ 1/(1 − g_lag)² (table). The card gives the HH's ±20% band "
               "credence 0.20 and the kill (Φ ≥ 2 Φ_pred) credence 0.35.")
        txt = f"""# H111 × G{gno:02d}: goal period #{gno}

**Verdict:** pending
**Role:** {role} (exploratory)
**Period:** goal #{gno} · regime {reg} · mean present N {npres:.1f} · units {units} · {ndays} non-holdout days.

## Why this period
Eligible for the replication layer: H67 measured a read-out loop gain g_lag for every unit of this period, so the sum rule gives a parameter-free prediction here.

## Prediction
*Written {stamp}, before running on this period (after Amendment A1). No H111 statistic seen.*
The card's per-period rule on the random-effects pooled r_F = Φ_obs(10)/Φ_pred(g_lag): supported if r_F ∈ [0.8, 1.2]; failed if r_F ≥ 2 or ≤ 0.5; mixed otherwise; descriptive with fewer than 40 usable windows or a Φ CI wider than 1.0. {exp}

| Unit | H67 g_lag [95%] | ≈ 1/(1 − g_lag)² (room-adjusted value computed in the run) |
| --- | --- | --- |
""" + "\n".join(lines) + """

## Result
(pending)

## Scorecard (period-specific axes)
C (Φ vs the block-shift null), D (the sum rule is unfitted).

## Notes
"""
        (d / "README.md").write_text(txt)
    print("wrote", m["goal_no"].n_unique(), "period folders")


if __name__ == "__main__" and "--pre" in sys.argv:
    pre()


def post():
    """Fill Verdict and Result from results/units.parquet and periods.parquet (keeps the dated prediction)."""
    import re
    U = pl.read_parquet(L.OUT / "results/units.parquet")
    W = pl.read_parquet(L.OUT / "results/units_wall.parquet").select("unit_id", pl.col("phi_10").alias("phi_wall"))
    U = U.join(W, on="unit_id", how="left")
    P = pl.read_parquet(L.OUT / "results/periods.parquet")
    for r in P.iter_rows(named=True):
        g = r["goal_no"]
        f = GP / f"G{g:02d}" / "README.md"
        txt = f.read_text()
        txt = re.sub(r"\*\*Verdict:\*\* .*", f"**Verdict:** {r['verdict']}", txt, count=1)
        rows = U.filter(pl.col("goal_no") == g).sort("unit_id")
        tab = ["| Unit | windows (10 min) | Φ(10) [95%] per-call | Φ(10) wall | Φ_pred(g_lag) | r_F [95%] | Φ(5) → Φ(30) | Φ untrimmed |",
               "| --- | --- | --- | --- | --- | --- | --- | --- |"]
        for u in rows.iter_rows(named=True):
            tab.append(f"| {u['unit_id']} | {u['nwin_10']} | {f_(u['phi_10'])} [{f_(u['phi_10_lo'])}, {f_(u['phi_10_hi'])}] | "
                       f"{f_(u['phi_wall'])} | {f_(u.get('phi_pred'))} | {f_(u.get('r_F'))} [{f_(u.get('r_F_lo'))}, {f_(u.get('r_F_hi'))}] | "
                       f"{f_(u['phi_5'])} → {f_(u['phi_30'])} | {f_(u['phi_untrim'])} |")
        res = (f"*Run 2026-10-04 ~21:45 UTC (non-holdout units; per-call clock, Amendment A1).* Period pool (random effects over units): "
               f"**Φ(10) = {f_(r['phi'])} [{f_(r['phi_lo'])}, {f_(r['phi_hi'])}]**, Φ_pred = {f_(r['phi_pred'])}, "
               f"**r_F = {f_(r['r_F'])} [{f_(r['r_F_lo'])}, {f_(r['r_F_hi'])}]**; {r['nwin']} usable 10-min windows. "
               f"Verdict by the card's rule: **{r['verdict']}**.\n\n" + "\n".join(tab) +
               "\n\nData: `data/processed/H111-talk-fano-sum-rule/results/units.parquet`, `units_wall.parquet`, `periods.parquet`.")
        txt = re.sub(r"## Result\n.*?\n## Scorecard", "## Result\n" + res + "\n\n## Scorecard", txt, count=1, flags=re.S)
        f.write_text(txt)
    print("filled", P.height)


def f_(x, d=2):
    try:
        return "–" if x is None or not math.isfinite(float(x)) else f"{float(x):.{d}f}"
    except (TypeError, ValueError):
        return "–"


if __name__ == "__main__" and "--post" in sys.argv:
    post()
