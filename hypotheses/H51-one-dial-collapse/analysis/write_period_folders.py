"""Write one replication README per goal period (G<NN>/) from results/phase_points.parquet and collapse.json.
G51 is native + replication and is written by hand (its replication point is appended from the same numbers).
Usage: uv run python hypotheses/H51-one-dial-collapse/analysis/write_period_folders.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h51lib as L  # noqa: E402

GP = L.HYP / "goalperiod-subhypotheses"
NATIVE_LINK = {36: "NE14", 39: "NE42", 40: "NE42", 41: "NE42"}


def fmt(x, n=3):
    return "–" if x is None or (isinstance(x, float) and not np.isfinite(x)) else f"{x:.{n}f}"


def verdict(r, card_collapse: bool) -> tuple[str, int]:
    zs = [r[f"{j}_zK"] for j in L.OBS if r[f"{j}_zK"] is not None and np.isfinite(r[f"{j}_zK"])]
    if len(zs) < 2:
        return "descriptive", len(zs)
    inside = sum(abs(z) <= 1.28 for z in zs)
    if card_collapse and inside >= 0.75 * len(zs):
        return "supported", len(zs)
    if not card_collapse:
        return "failed", len(zs)
    return "mixed", len(zs)


def main():
    pts = pl.read_parquet(L.DATA / "results/phase_points.parquet")
    col = json.loads((L.DATA / "results/collapse.json").read_text())["primary"]
    perm = json.loads((L.DATA / "results/perm.json").read_text())
    card_collapse = sum(col[j]["collapse_K"] for j in L.OBS) >= 3 and perm["K"]["p"] < 0.05
    ap = pl.read_parquet(L.DATA / "axes_periods.parquet")
    table = []
    for r in pts.iter_rows(named=True):
        g = r["goal_no"]
        v, nobs = verdict(r, card_collapse)
        units = ap.filter(pl.col("goal_no") == g)["units"][0].to_list()
        key = (f"regime {r['regime']}, N {r['N_active']:.1f}: g_lag {fmt(r['K'])} · c_× {fmt(r['c_x_trim'], 4)} · "
               f"S_text {fmt(r['kick'], 2)} · z(D1) " + " / ".join(fmt(r[f'{j}_zK'], 1) for j in L.OBS))
        table.append((g, v, key))
        if g == 51:
            continue
        lines = [f"# H51 × G{g:02d}: goal period #{g}", "", f"**Verdict:** {v}", "**Role:** replication (exploratory)"
                 + (f"; native test in [{NATIVE_LINK[g]}](../{NATIVE_LINK[g]}/README.md)" if g in NATIVE_LINK else ""),
                 f"**Period:** goal #{g} · regime {r['regime']} · active N {r['N_active']:.1f} · units {', '.join(units)}.", "",
                 "## Why this period",
                 "A non-holdout goal period with the three phase-diagram axes (H67 g_lag, H86 c_×, H85 N) and at least one "
                 "observable; one point of the replication layer.", "",
                 "## Prediction",
                 "*The card's per-period rule, written 2026-10-04 20:40 UTC before any collapse statistic; this folder was "
                 "written after the run and copies it.* Supported if the period's D1 (g_lag) leave-one-period-out residual "
                 "lies inside the 80% band (|z| ≤ 1.28) for ≥ 3/4 of its observables and the card-level collapse holds; "
                 "failed if the card-level collapse does not hold and the period has ≥ 2 observables; descriptive if it "
                 "has < 2 observables.", "",
                 "## Result",
                 f"Card-level D1 collapse: **{'holds' if card_collapse else 'does not hold'}** "
                 f"({sum(col[j]['collapse_K'] for j in L.OBS)}/4 observables; within-regime permutation p = {perm['K']['p']:.3f}).",
                 "", "| Axis | Value |", "| --- | --- |",
                 f"| K = g_lag (H67 pool) | {fmt(r['K'])} ± {fmt(r['g_lag_se'])} |",
                 f"| equal-time dial g_eq | {fmt(r['g_eq'])} |",
                 f"| h = c_× trimmed (H86) | {fmt(r['c_x_trim'], 4)} (φ {fmt(r['phi_trim'], 3)}) |",
                 f"| kickoff S_text (H54) | {fmt(r['kick'], 2)} |",
                 f"| N active (H85) | {r['N_active']:.1f} |",
                 f"| f_sched (H38) | {fmt(r['f_sched'], 2)} |", "",
                 "| Observable | Observed | D1 prediction (LOPO) | z | regime-only prediction |",
                 "| --- | --- | --- | --- | --- |"]
        for j in L.OBS:
            lines.append(f"| {L.OBS_LABEL[j]} | {fmt(r[j])} | {fmt(r[f'{j}_predK'])} | {fmt(r[f'{j}_zK'], 2)} | "
                         f"{fmt(r[f'{j}_predReg'])} |")
        lines += ["", "Transformed scales: settling log active hours; herding share excess; branching and loop rate in logits. "
                  "Data: `data/processed/H51-one-dial-collapse/results/phase_points.parquet`.", "",
                  "## Scorecard (period-specific axes)",
                  "D (unfitted observables placed against the dial), H (D1 vs regime-only prediction above).", ""]
        p = GP / f"G{g:02d}"
        (p / "figures").mkdir(parents=True, exist_ok=True)
        (p / "README.md").write_text("\n".join(lines))
    L.jdump([{"goal_no": g, "verdict": v, "key": k} for g, v, k in table], L.DATA / "results/period_verdicts.json")
    print({v: sum(1 for _, x, _ in table if x == v) for v in ("supported", "failed", "mixed", "descriptive")})


if __name__ == "__main__":
    main()
