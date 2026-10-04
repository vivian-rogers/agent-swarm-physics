"""H81: write goalperiod-subhypotheses/G<NN>/README.md for every replication period (κ and the period's place in the
cross-goal slow-mode pairs). G51 is a native folder; its replication numbers are appended there by hand.
Usage: uv run python hypotheses/H81-culture-beyond-composition/analysis/write_period_cards.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h81lib as L  # noqa: E402

HYP = L.ROOT / "hypotheses/H81-culture-beyond-composition/goalperiod-subhypotheses"


def neigh(model, regime, goal):
    T = pl.read_parquet(L.OUT / f"replication/pairs_{model}_{regime}.parquet")
    bl = pl.read_parquet(L.OUT / "blocks.parquet").filter(pl.col("regime") == regime).with_row_index("k")
    ks = set(bl.filter(pl.col("goal_no") == goal)["k"].to_list())
    t = T.filter(pl.col("b").cast(pl.Int64).is_in(list(ks)) | pl.col("c").cast(pl.Int64).is_in(list(ks)))
    near = t.filter(pl.col("dt") <= 14); far = t.filter(pl.col("dt") >= 42)
    f = lambda d: float(np.average(d["s"].to_numpy(), weights=d["w"].to_numpy())) if d.height else float("nan")  # noqa: E731
    return f(near), near.height, f(far), far.height


def main():
    kap = pl.read_parquet(L.OUT / "replication/kappa.parquet")
    pu = pl.read_parquet(L.ROOT / "data/processed/shared/period_units.parquet")
    for g in sorted(set(kap["goal_no"].to_list())):
        k = {m: kap.filter((pl.col("goal_no") == g) & (pl.col("model") == m)).row(0, named=True)
             for m in ("bge_small", "gte_modernbert")}
        reg = k["bge_small"]["regime"]
        u = pu.filter((pl.col("goal_no") == g) & ~pl.col("holdout"))
        splits = ", ".join(f"{r['unit_id']} ({r['reason']})" for r in u.iter_rows(named=True) if r["seq"] > 0) or "none"
        nb = {m: neigh(m, reg, g) for m in k}
        above = all(k[m]["kappa"] > k[m]["null_hi"] for m in k)
        lines = [f"# H81 × G{g:02d}: goal period #{g} ({k['bge_small']['first_day']} → {k['bge_small']['last_day']}, non-holdout days)", "",
                 "**Verdict:** descriptive", "**Role:** replication",
                 f"**Period:** regime {reg} · {k['bge_small']['n_agents_goal']} eligible agents · {k['bge_small']['n_blocks']} calendar-week block(s). Splits inside the period: {splits}.",
                 "", "## Why this period",
                 "Every non-holdout goal period of regimes I and III is a replication point for the equal-time collective share κ "
                 "and a node of the regime-level cross-goal slow-mode analysis (the card's exception (c)).",
                 "", "## Prediction",
                 "*Written 2026-10-04 20:05 UTC in the card (P1), before any real-data statistic; this folder was generated after the run.*",
                 "- P1 (descriptive): κ above its sign-flip band (field leakage and contemporaneous convergence make it positive). Not a culture claim.",
                 "- The slow-mode predictions (P2, P3) are regime-level; this period's neighbour similarities are listed for reference.",
                 "", "## Result", "| Quantity | bge | gte |", "| --- | --- | --- |"]
        f = lambda x: f"{x:+.3f}" if x == x else "n/a"  # noqa: E731
        lines.append(f"| κ (equal time) [95% jackknife] | {f(k['bge_small']['kappa'])} ± {1.96 * (k['bge_small']['kappa_se'] or 0):.3f} | {f(k['gte_modernbert']['kappa'])} ± {1.96 * (k['gte_modernbert']['kappa_se'] or 0):.3f} |")
        lines.append(f"| sign-flip null band | [{k['bge_small']['null_lo']:.3f}, {k['bge_small']['null_hi']:.3f}] | [{k['gte_modernbert']['null_lo']:.3f}, {k['gte_modernbert']['null_hi']:.3f}] |")
        lines.append(f"| excess variance ratio ‖u‖² / floor | {k['bge_small']['excess_ratio']:.2f} | {k['gte_modernbert']['excess_ratio']:.2f} |")
        lines.append(f"| mean similarity to blocks of other goals ≤ 14 d away (pairs) | {f(nb['bge_small'][0])} ({nb['bge_small'][1]}) | {f(nb['gte_modernbert'][0])} ({nb['gte_modernbert'][1]}) |")
        lines.append(f"| mean similarity to blocks of other goals ≥ 42 d away (pairs) | {f(nb['bge_small'][2])} ({nb['bge_small'][3]}) | {f(nb['gte_modernbert'][2])} ({nb['gte_modernbert'][3]}) |")
        lines += ["", f"P1 here: κ {'above' if above else 'not above'} the band in both models. "
                  "Data: `data/processed/H81-culture-beyond-composition/replication/` (`kappa.parquet`, `pairs_<model>_<regime>.parquet`).",
                  "", "## Scorecard (period-specific axes)",
                  "- C: κ against the sign-flip null (equal time only). The period's role in D (slow mode) is through the regime-level pairs.",
                  "", "## Notes", "- κ includes field leakage beyond the projected directions and contemporaneous convergence; it is an upper bound on equal-time collective order."]
        d = HYP / f"G{g:02d}"
        if g == 51:
            continue
        (d / "figures").mkdir(parents=True, exist_ok=True)
        (d / "README.md").write_text("\n".join(lines) + "\n")
    print("ok")


if __name__ == "__main__":
    main()
