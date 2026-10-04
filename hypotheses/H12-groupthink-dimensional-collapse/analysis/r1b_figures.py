"""H12 round 1b figure: (a) top-eigenvalue / edge per scored unit for activity (old table + cross-day edge; fixed table +
cross-day edge; fixed table + DQ8 trimmed block-shift edge) and talk (fixed, DQ8 edge); (b) #12 debates: PR while the
motion is on vs in the 20 min after the verdict, paired, two embedding models.
Output: hypotheses/H12-groupthink-dimensional-collapse/figures/r1b_modes_motion.{png,pdf}
Usage: uv run python hypotheses/H12-groupthink-dimensional-collapse/analysis/r1b_figures.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HYP = Path(__file__).resolve().parents[1]
DATA = HYP.parents[1] / "data/processed/H12-groupthink-dimensional-collapse"


def main():
    uo = pl.read_parquet(DATA / "unit_table.parquet").filter(pl.col("scored")).select("unit", "regime", pl.col("l1_edge").alias("old"))
    un = pl.read_parquet(DATA / "r1b/unit_table.parquet").filter(pl.col("scored")).select(
        "unit", pl.col("l1_edge").alias("fixed"), pl.col("l1_edge_trim").alias("trim"), pl.col("talk_l1_edge_trim").alias("talk_trim"))
    u = uo.join(un, on="unit").sort("regime", "unit")
    d12 = pl.read_parquet(DATA / "r1b/native/g12_debates.parquet")
    fig, ax = plt.subplots(1, 2, figsize=(7.6, 3.0), gridspec_kw={"width_ratios": [1.45, 1]})
    x = np.arange(u.height)
    for col, lab, c, m in (("old", "activity, old table, cross-day edge (round 1)", "#b0b0b0", "o"),
                           ("fixed", "activity, fixed table, cross-day edge", "#2a6fb0", "o"),
                           ("trim", "activity, fixed, trimmed + block-shift edge (DQ8)", "#e45756", "s"),
                           ("talk_trim", "talk, fixed, trimmed + block-shift edge (DQ8)", "#5aa469", "^")):
        ax[0].scatter(x, u[col].to_numpy(), s=14, color=c, marker=m, label=lab, zorder=3)
    ax[0].axhline(1, color="k", lw=0.7)
    ax[0].set_xticks(x, u["unit"].to_list(), fontsize=5.5, rotation=90)
    ax[0].set_ylabel("top eigenvalue / 95% surrogate edge", fontsize=8)
    ax[0].legend(fontsize=5.6, frameon=False, loc="upper left")
    ax[0].set_title("(a) collective mode per scored unit (> 1: above the edge)", fontsize=8)
    ax[0].tick_params(axis="y", labelsize=7)
    for k, (vk, c) in enumerate((("bge_h12", "#2a6fb0"), ("gte_shared", "#d08c2a"))):
        ok = d12.filter(pl.col(f"pr_on_{vk}").is_not_nan() & pl.col(f"pr_off_{vk}").is_not_nan())
        on, off = ok[f"pr_on_{vk}"].to_numpy(), ok[f"pr_off_{vk}"].to_numpy()
        for a, b in zip(off, on):
            ax[1].plot([2 * k, 2 * k + 1], [a, b], color=c, lw=0.8, alpha=0.7)
        ax[1].scatter([2 * k] * len(off), off, s=10, color=c); ax[1].scatter([2 * k + 1] * len(on), on, s=10, color=c)
    ax[1].set_xticks([0, 1, 2, 3], ["after\nverdict", "motion\non", "after\nverdict", "motion\non"], fontsize=7)
    ax[1].text(0.5, ax[1].get_ylim()[1], "bge (H12 ruler)", ha="center", va="bottom", fontsize=7, color="#2a6fb0")
    ax[1].text(2.5, ax[1].get_ylim()[1], "gte", ha="center", va="bottom", fontsize=7, color="#d08c2a")
    ax[1].set_ylabel("participation ratio (n = 12, cap 4)", fontsize=8)
    ax[1].set_title("(b) #12 debates: field on vs off", fontsize=8, pad=12)
    ax[1].tick_params(axis="y", labelsize=7)
    fig.tight_layout()
    fig.savefig(HYP / "figures/r1b_modes_motion.png", dpi=170); fig.savefig(HYP / "figures/r1b_modes_motion.pdf")
    print("written")


if __name__ == "__main__":
    main()
