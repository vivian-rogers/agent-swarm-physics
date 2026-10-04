"""H12 summary-page figure (figures/summary_obs.pdf): reads round-1 outputs only, recomputes nothing.

(a) P7: agent-balanced participation ratio PRday on the kickoff day vs the median of later days (periods with N >= 10);
(b) post hoc: regime-III day PRday against the share of chat statements that near-copy (cos > 0.95) the same agent's
    earlier text vs another agent's text.

Usage: uv run python hypotheses/H12-groupthink-dimensional-collapse/analysis/summary_figure.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = ROOT / "data/processed/H12-groupthink-dimensional-collapse"
FIG = HERE.parent / "figures"
C1, C2 = "#2a78d6", "#eb6834"  # validated reference slots 1-2
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({"font.size": 7, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "axes.titlesize": 7.2,
                     "axes.titleweight": "bold", "legend.frameon": False, "pdf.fonttype": 42})


def main():
    p7 = pl.read_parquet(DATA / "p7_day1.parquet").filter(
        pl.col("prday_d1").is_not_nan() & pl.col("prday_later_med").is_not_nan() & (pl.col("N") >= 10)).sort("goal_no")
    tm = pl.read_parquet(DATA / "posthoc_templating.parquet").filter(pl.col("prday").is_not_nan())
    fig, (a, b) = plt.subplots(1, 2, figsize=(4.3, 2.6), gridspec_kw={"width_ratios": [0.85, 1.15]})

    # (a) day 1 vs later days
    n_hi = 0
    for r in p7.iter_rows(named=True):
        hi = r["prday_d1"] > r["prday_later_med"]
        n_hi += hi
        col = C2 if hi else C1
        a.plot([0, 1], [r["prday_d1"], r["prday_later_med"]], "-", color=col, lw=0.9, alpha=0.85)
        a.plot([0, 1], [r["prday_d1"], r["prday_later_med"]], "o", color=col, ms=2.8)
        if r["prday_later_med"] < 11:
            a.annotate(f"#{r['goal_no']}", (1, r["prday_later_med"]), xytext=(3, 3 if r["goal_no"] == 40 else -3), textcoords="offset points",
                       fontsize=5, color=INK2, va="center")
    a.set_xticks([0, 1], ["day 1\n(kickoff)", "median of\nlater days"], fontsize=6)
    a.set_xlim(-0.25, 1.3)
    a.set_ylabel("PRday (6 agents × 15 chat statements)")
    a.yaxis.grid(True, color=GRID, lw=0.5)
    a.set_axisbelow(True)
    a.set_title("a  Kickoff day is more diverse", loc="left")
    a.text(0.5, 0.03, f"day 1 higher in {n_hi}/{p7.height}", transform=a.transAxes, ha="center", fontsize=5.8, color=INK)

    # (b) loops vs echoes
    xw, xc, y = tm["dup_within"].to_numpy() * 100, tm["dup_cross"].to_numpy() * 100, tm["prday"].to_numpy()
    rw, rc = spearmanr(xw, y)[0], spearmanr(xc, y)[0]
    b.scatter(xc, y, s=12, marker="D", facecolor="white", edgecolor=C1, linewidth=0.8, zorder=3,
              label=f"copies another agent (ρ = {rc:+.2f})")
    b.scatter(xw, y, s=12, marker="o", color=C2, edgecolor="white", linewidth=0.3, zorder=4,
              label=f"repeats itself (ρ = {rw:+.2f})")
    for r in tm.filter(pl.col("dup_within") > 0.45).iter_rows(named=True):
        b.annotate(f"#{r['unit']}", (r["dup_within"] * 100, r["prday"]), xytext=(-2, 5), textcoords="offset points",
                   fontsize=5, color=INK2, ha="center")
    b.set_xlabel("near-copy chat statements (%)")
    b.set_ylabel("PRday (regime-III days)")
    b.yaxis.grid(True, color=GRID, lw=0.5)
    b.set_axisbelow(True)
    b.set_title("b  Loops, not echo", loc="left")
    b.legend(loc="upper right", fontsize=5.4, handletextpad=0.2, borderaxespad=0.1)
    ylo = min(np.nanmin(y), p7["prday_later_med"].min()) - 0.8
    yhi = max(np.nanmax(y), p7["prday_d1"].max()) + 0.8
    a.set_ylim(ylo, yhi)
    b.set_ylim(ylo, yhi + 2.5)
    fig.tight_layout(pad=0.3, w_pad=0.8)
    fig.savefig(FIG / "summary_obs.pdf")
    fig.savefig(FIG / "summary_obs.png", dpi=200)
    plt.close(fig)
    print(f"day1 higher {n_hi}/{p7.height}; spearman within {rw:.2f}, cross {rc:.2f}; cross max {np.nanmax(xc):.1f}%")


if __name__ == "__main__":
    main()
