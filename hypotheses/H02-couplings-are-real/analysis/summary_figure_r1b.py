"""H02 round-1b page-2 figure (figures/summary_obs2.pdf): reads round-1b outputs only.

(a) Curie-Weiss beta*J0 z-score per chunk against the N1 surrogate null: corrected data on the whole-day grid (the
    round-1 null) vs the DQ8 corrected null (all-present window, explained joint silences removed before surrogates).
(b) Synthetic: pass rate of the frozen #45 rule (rank 1, z >= 2) for a planted leader of strength J_L, on clean
    spins and after the activity_bins bug's day-specific thinning (round-1b calibration).
Usage: uv run python hypotheses/H02-couplings-are-real/analysis/summary_figure_r1b.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[2] / "data/processed/H02-couplings-are-real/r1b"
FIG = HERE.parent / "figures"
C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({"font.size": 7, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "axes.titlesize": 7.2,
                     "axes.titleweight": "bold", "legend.frameon": False, "pdf.fonttype": 42})


def main():
    c = pl.read_parquet(DATA / "chunks_1b.parquet").sort("regime", "mode", "chunk")
    fig, (a, b) = plt.subplots(1, 2, figsize=(4.3, 2.05), gridspec_kw={"width_ratios": [1.35, 1]})
    x = np.arange(c.height)
    a.scatter(x - 0.15, c["z__r1b"], s=12, color=C1, label="whole-day grid (round-1 null)", zorder=3, edgecolor="white", lw=0.3)
    a.scatter(x + 0.15, c["z__r1b_trim_stall"], s=12, color=C2, label="corrected null (trim + stall mask)", zorder=3,
              edgecolor="white", lw=0.3)
    a.axhline(2, color=INK2, lw=0.6, ls="--")
    n1 = int((c["regime"] == "I").sum())
    a.axvline(n1 - 0.5, color=GRID, lw=0.8)
    a.text(n1 / 2 - 0.5, 10.6, "regime I", ha="center", color=INK2, fontsize=6)
    a.text(n1 + (c.height - n1) / 2 - 0.5, 10.6, "regime III", ha="center", color=INK2, fontsize=6)
    a.set_xticks(x)
    a.set_xticklabels([s[1:3] for s in c["chunk"].to_list()], fontsize=4.8, rotation=90)
    a.set_xlabel("chunk (goal period)")
    a.set_ylabel("z of βJ₀ vs N1 surrogates")
    a.set_ylim(-3, 15.5)
    a.yaxis.grid(True, color=GRID, lw=0.5)
    a.set_axisbelow(True)
    a.set_title("a  Collective coupling, two nulls", loc="left")
    a.legend(loc="upper left", fontsize=5.4, handletextpad=0.2, bbox_to_anchor=(0.0, 1.02))

    t = pl.read_parquet(DATA / "thinning.parquet").filter(pl.col("cal") == "r1b")
    g = t.group_by("JL").agg(pl.col("pass_clean").mean(), pl.col("pass_thin").mean(), pl.len()).sort("JL")
    for col, lab, cc, mk in (("pass_clean", "clean spins", C1, "o"), ("pass_thin", "after the bug's thinning", C3, "s")):
        p = g[col].to_numpy(); n = g["len"].to_numpy()
        se = np.sqrt(p * (1 - p) / n)
        b.errorbar(g["JL"], p, yerr=1.96 * se, color=cc, marker=mk, ms=4, lw=1.6, capsize=1.5, label=lab)
    b.set_xlabel("leader coupling J_L")
    b.set_ylabel("P(rank 1 and z ≥ 2)")
    b.set_ylim(0, 1.05)
    b.set_xticks([0.2, 0.3, 0.5])
    b.yaxis.grid(True, color=GRID, lw=0.5)
    b.set_axisbelow(True)
    b.set_title("b  #45 rule, synthetic", loc="left")
    b.legend(loc="lower right", fontsize=5.4)
    fig.tight_layout(pad=0.4, w_pad=1.0)
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / "summary_obs2.pdf")
    fig.savefig(FIG / "summary_obs2.png", dpi=200)


if __name__ == "__main__":
    main()
