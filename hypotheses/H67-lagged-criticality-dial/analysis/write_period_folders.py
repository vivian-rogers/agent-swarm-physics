"""Write/refresh the H67 per-period READMEs (replication rows) from results/periods.parquet and units.parquet."""
import json
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[3]
H = ROOT / "hypotheses/H67-lagged-criticality-dial/goalperiod-subhypotheses"
R = ROOT / "data/processed/H67-lagged-criticality-dial/results"
P = pl.read_parquet(R / "periods.parquet")
U = pl.read_parquet(R / "units.parquet").filter(pl.col("ok").fill_null(False))
f = lambda x: "n/a" if x is None or x != x else f"{x:.3f}"  # noqa: E731
for r in P.iter_rows(named=True):
    g = r["goal_no"]
    d = H / f"G{g:02d}"
    (d / "figures").mkdir(parents=True, exist_ok=True)
    us = U.filter(pl.col("goal_no") == g).sort("unit_id")
    lines = "\n".join(
        f"| {u['unit_id']} | {u['N']} | {u['n_rows_trim']} | {f(u['g'])} [{f(u['g_lo'])}, {f(u['g_hi'])}] | "
        f"{f(u['J1'])} [{f(u['J1_lo'])}, {f(u['J1_hi'])}] | {f(u['rbar'])} | {f(u['g_eq'])} | {f(u['g_named'])} | "
        f"{f(u['shift_excl0_share'])} |" for u in us.iter_rows(named=True))
    body = f"""**Verdict:** {r['verdict']}
**Role:** replication (exploratory)
**Period:** goal #{g} · regime {r['regime']} · mean N {r['N']:.1f} · units {', '.join(r['units'])} · {r['n_rows']} receiving calls in the all-present window.

## Why this period
Eligible for the replication layer (≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls).

## Prediction
*The card's per-period rule, written 2026-10-04 19:15 UTC before any real-data statistic; this folder was written after the run and copies it.* Supported if the pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; failed if J₁* is not above 0 and g_lag ≤ g_eq, or any unit's lower bound ≥ 1; mixed otherwise.

## Result
Period pool (random effects over units): **g_lag = {f(r['g'])} [{f(r['g_lo'])}, {f(r['g_hi'])}]**, J₁* = {f(r['J1'])} [{f(r['J1_lo'])}, {f(r['J1_hi'])}], g_eq (same data) = {f(r['g_eq'])}, H25 trimmed talk dial = {f(r['g_h25_trim'])}, H42 world-B n_x = {f(r['nxB_w'])}; named-message part of g_lag = {f(r['g_named'])}.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
{lines}

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).
"""
    p = d / "README.md"
    title = f"# H67 × G{g:02d}: goal period #{g}\n\n"
    if p.exists() and "native" in p.read_text().split("\n")[3]:
        txt = p.read_text()
        if "## Replication layer" not in txt:
            p.write_text(txt.rstrip() + "\n\n## Replication layer\n" + body.split("## Result", 1)[1].replace("\n## Scorecard", "\n### Scorecard"))
        continue
    p.write_text(title + body)
print("done")
