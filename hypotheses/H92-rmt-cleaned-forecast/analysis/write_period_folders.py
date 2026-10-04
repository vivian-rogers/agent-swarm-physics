"""H92: per-goal-period replication folders (templated from the card's replication rule) and per-period rows in the
shared per_period_estimates table. G38 and G51 are native folders (their replication numbers are in data/processed and
quoted in the native READMEs).
Run after evaluate.py: uv run python hypotheses/H92-rmt-cleaned-forecast/analysis/write_period_folders.py
"""
from __future__ import annotations

import re
import sys

import numpy as np
import polars as pl

import h92lib as L

sys.path.insert(0, str(L.ROOT / "infra/shared"))
import estimates as E  # noqa: E402

HYPD = L.ROOT / "hypotheses/H92-rmt-cleaned-forecast/goalperiod-subhypotheses"
NATIVE = {38, 51}
METHOD = ("H92 round 1: next-day forecast of the agent correlation matrix (expanding training window within the unit); "
          "relative gain r = 1 - MSE(RMT clip, calibrated edge) / MSE(rival) on off-diagonal entries of the realized day")
LAB = {"E2_raw": "raw", "E3_lwi": "Ledoit-Wolf identity", "E4_lwcc": "Ledoit-Wolf constant correlation", "E1_mean": "mean field"}


def titles() -> dict:
    t = {}
    for line in (L.ROOT / "hypotheses/hypohypotheses/goal-periods.md").read_text().splitlines():
        m = re.match(r"^### (\d+) · (.+)$", line)
        if m:
            t[int(m.group(1))] = m.group(2).strip()
    return t


def fmt(x, nd=3):
    return "–" if x is None or (isinstance(x, float) and not np.isfinite(x)) else f"{x:+.{nd}f}"


def main():
    pt = pl.read_parquet(L.OUT / "periods.parquet")
    ttl = titles()
    rows = []
    cal = L.DM.calendar()
    for g in sorted(pt["goal_no"].unique().to_list()):
        x = pt.filter(pl.col("goal_no") == g)
        unit = E.map_unit(int(g))
        for r in x.iter_rows(named=True):
            base = {"period_unit": unit, "goal_no": int(g), "method": METHOD, "role": "replication",
                    "first_day": r["first_day"], "last_day": r["last_day"], "post_hoc": False,
                    "source": "data/processed/H92-rmt-cleaned-forecast/periods.parquet",
                    "null": "rival estimators; calibrated edge from within-day surrogates (content) / DQ8 trimmed block shift (spins)"}
            for k, lab in LAB.items():
                rows.append({**base, "statistic": f"clip_gain_vs_{k.split('_', 1)[1]}", "channel": r["channel"],
                             "estimate": r[f"r_{k}"], "ci_lo": r[f"r_{k}_lo"], "ci_hi": r[f"r_{k}_hi"],
                             "ci_kind": "percentile" if r[f"r_{k}_lo"] is not None else "none", "ci_level": 0.95,
                             "n": r["n_targets"], "n_kind": "target days",
                             "notes": f"mean over target days of 1 - MSE_clip / MSE_{lab}; positive = clipping forecasts better"})
        if g in NATIVE:
            continue
        v = x["verdict"][0]
        c = {r["channel"]: r for r in x.iter_rows(named=True)}
        lines = []
        for ch in ("content_bge", "content_gte", "content_bge_style_resid_period", "content_gte_style_resid_period", "talk", "act"):
            if ch in c:
                r = c[ch]
                lines.append(f"| {ch} | {r['n_targets']} | {r['N_med']:.0f} | {fmt(r['r_E2_raw'])} | {fmt(r['r_E3_lwi'])} | "
                             f"{fmt(r['r_E4_lwcc'])} | {fmt(r['r_E1_mean'])} | {r['best']} |")
        reg = cal.filter(pl.col("goal_no") == g)["regime"][0]
        folder = HYPD / f"G{int(g):02d}"
        (folder / "figures").mkdir(parents=True, exist_ok=True)
        text = f"""# H92 × G{int(g):02d}: {ttl.get(int(g), 'goal period ' + str(g))} ({x['first_day'].min()} → {x['last_day'].max()}, forecast target days)

**Verdict:** {v}
**Role:** replication (exploratory)
**Period:** regime {reg} · forecasts within `period_units` units only (no forecast crosses a step change).

## Why this period
A replication point for the common estimator (layer 1). Every eligible goal period gets the same forecast comparison, so periods are comparable points, not independent tests.

## Prediction
*Templated from the card's replication rule, written 2026-10-04 ~20:15 UTC before any real-data forecast.*
- RMT clipping at the calibrated edge (E5) has the lowest mean next-day MSE among raw (E2), Ledoit–Wolf identity (E3), Ledoit–Wolf constant correlation (E4) and E5, in the content channel with both embedding models.
- *Supported* if that holds in both models; *failed* if E5's mean MSE exceeds raw's in both; *mixed* otherwise; *descriptive* with < 2 target days.

## Result
Relative gain of E5 over each rival, r = 1 − MSE_E5/MSE_rival, mean over target days (positive = clipping forecasts better). Expanding training window.

| Channel | target days | median N | vs raw | vs LW identity | vs LW const. corr. | vs mean field | best estimator |
| --- | --- | --- | --- | --- | --- | --- | --- |
{chr(10).join(lines)}

Data: `data/processed/H92-rmt-cleaned-forecast/periods.parquet`, `forecasts.parquet`. CIs are in the shared estimates table.

## Scorecard (period-specific axes)
- C (adequacy): the forecast comparison against the strongest rival on this period, as tabulated.
- H (comparative): E5 vs E3/E4 here.

## Notes
- Templated folder (replication layer), written by `analysis/write_period_folders.py`.
"""
        (folder / "README.md").write_text(text)
    E.write_estimates(rows, hypothesis="H92")
    print(f"{len(rows)} estimate rows")


if __name__ == "__main__":
    main()
