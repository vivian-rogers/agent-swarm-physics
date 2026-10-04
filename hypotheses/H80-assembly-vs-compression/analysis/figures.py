"""H80 figures: summary_obs.pdf (AUC by feature family per unit; motif spread vs assembly index)."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
D = ROOT / "data/processed/H80-assembly-vs-compression"
FIG = HERE.parent / "figures"


def style(ax):
    ax.tick_params(labelsize=7)
    ax.spines[["top", "right"]].set_visible(False)


def obs():
    cls = json.loads((D / "results/classifier.json").read_text())
    units = [("G51", "day"), ("G31", "day"), ("G41", "window"), ("G51+post", "repo")]
    lab = ["G51\n(1 stream)", "G31\n(1 stream)", "G41\n(1 stream)", "G51+post\n(28 streams)"]
    sets = [("T", "#85847e", "timing (scheduler)"), ("C", "#86b6ef", "compression"), ("C+A", "#2a78d6", "compression + assembly")]
    fig, ax = plt.subplots(1, 2, figsize=(6.6, 2.5), gridspec_kw={"width_ratios": [1.6, 1]})
    for i, (u, b) in enumerate(units):
        r = next(x for x in cls if x["unit"] == u and x["block"] == b)
        for j, (s, c, l) in enumerate(sets):
            v = r["auc"][s]
            lo, hi = r["auc_ci"][s]
            ax[0].bar(i + (j - 1) * 0.26, v, 0.25, color=c, label=l if i == 0 else None)
            ax[0].errorbar(i + (j - 1) * 0.26, v, yerr=[[max(v - lo, 0)], [max(hi - v, 0)]], color="#0b0b0b", lw=0.7,
                           capsize=1.5)
    ax[0].axhline(0.5, color="#85847e", lw=0.6, ls=":")
    ax[0].axhline(0.9, color="#85847e", lw=0.6, ls="--")
    ax[0].set_xticks(range(4), lab, fontsize=6.5)
    ax[0].set_ylabel("AUC, automated vs agent windows", fontsize=7)
    ax[0].set_ylim(0, 1.3)
    ax[0].legend(fontsize=5.5, frameon=False, loc="upper center", ncol=3)
    style(ax[0])
    m = pl.read_parquet(D / "motifs.parquet")
    g = m.group_by("a").agg(pl.col("n_agents").median().alias("med"), pl.col("n_agents").quantile(0.25).alias("q1"),
                            pl.col("n_agents").quantile(0.75).alias("q3"), pl.len()).sort("a")
    a = g["a"].to_numpy()
    ax[1].errorbar(a, g["med"], yerr=[g["med"] - g["q1"], g["q3"] - g["med"]], fmt="o-", color="#2a78d6", ms=3,
                   capsize=2)
    for ai, n in zip(a, g["len"].to_list()):
        ax[1].text(ai, 0.3, str(n), fontsize=5.5, ha="center", color="#85847e")
    ax[1].set_xlabel("assembly index $a$ of the command motif", fontsize=7)
    ax[1].set_ylabel("agents using it (median, IQR)", fontsize=7)
    ax[1].set_ylim(0, 12)
    style(ax[1])
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs.pdf")


if __name__ == "__main__":
    obs()
