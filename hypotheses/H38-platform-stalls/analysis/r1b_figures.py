"""H38 round 1b figure: (a) excess gain per period, round-1 null on the whole-day grid vs the DQ8 null after trimming
to the all-present window (fixed tables); (b) NE43 inside #51: per-day day-edge component D_edge and start spread by
window (bookends + nudges / nudges only / neither).
Output: hypotheses/H38-platform-stalls/figures/r1b_null_ne43.{png,pdf}
Usage: uv run python hypotheses/H38-platform-stalls/analysis/r1b_figures.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HYP = Path(__file__).resolve().parents[1]
DATA = HYP.parents[1] / "data/processed/H38-platform-stalls/r1b"
REGC = {"I": "#4c78a8", "II": "#9c6ade", "III": "#e45756"}


def main():
    d = pl.read_parquet(DATA / "period_table.parquet")
    n43 = pl.read_parquet(DATA / "native/ne43_days.parquet")
    fig, ax = plt.subplots(1, 2, figsize=(7.6, 3.1), gridspec_kw={"width_ratios": [1.1, 1]})
    for r in d.iter_rows(named=True):
        reg = "III" if r["regime"].endswith("III") else r["regime"]
        sig = (r["z_trim"] or 0) > 2
        ax[0].scatter(r["E_raw"], r["E_trim"], s=22, color=REGC[reg], alpha=0.85, edgecolor="k" if sig else "none", lw=0.7)
    lim = [-0.15, 0.55]
    ax[0].plot(lim, lim, "k-", lw=0.6); ax[0].plot(lim, [x / 2 for x in lim], "k--", lw=0.6)
    ax[0].axhline(0, color="k", lw=0.4); ax[0].axvline(0, color="k", lw=0.4)
    ax[0].set_xlim(lim); ax[0].set_ylim(lim)
    ax[0].set_xlabel("excess gain, whole-day grid (round-1 null)", fontsize=8)
    ax[0].set_ylabel("excess gain, trimmed before surrogates (DQ8)", fontsize=8)
    for reg, col in REGC.items():
        ax[0].scatter([], [], color=col, s=18, label=f"regime {reg}")
    ax[0].legend(fontsize=6.5, frameon=False, loc="upper left")
    ax[0].set_title("(a) fixed tables, 35 periods (black edge: trimmed z > 2)", fontsize=8)
    ax[0].tick_params(labelsize=7)
    wins = ["A", "B", "C"]
    lab = {"A": "bookends\n+ nudges", "B": "nudges\nonly", "C": "neither"}
    rng = np.random.default_rng(0)
    for k, w in enumerate(wins):
        x = n43.filter(pl.col("window") == w)
        jit = k + rng.uniform(-0.12, 0.12, x.height)
        ax[1].scatter(jit - 0.18, x["D_edge"].to_numpy(), s=10, color="#2a6fb0", alpha=0.7)
        ax[1].plot([k - 0.32, k - 0.04], [x["D_edge"].mean()] * 2, color="#2a6fb0", lw=2)
    ax[1].set_ylabel("day-edge component D_edge (blue)", fontsize=8, color="#2a6fb0")
    ax2 = ax[1].twinx()
    for k, w in enumerate(wins):
        x = n43.filter(pl.col("window") == w)
        jit = k + rng.uniform(-0.12, 0.12, x.height)
        ax2.scatter(jit + 0.18, x["start_sd"].to_numpy(), s=10, color="#d08c2a", alpha=0.7, marker="s")
        ax2.plot([k + 0.04, k + 0.32], [float(x["start_sd"].median())] * 2, color="#d08c2a", lw=2)
    ax2.set_yscale("symlog", linthresh=5)
    ax2.set_ylabel("start spread, min (orange; bar = median)", fontsize=8, color="#d08c2a")
    ax[1].set_xticks(range(3), [lab[w] for w in wins], fontsize=7)
    ax[1].axvline(0.5, color="k", ls=":", lw=0.8); ax[1].axvline(1.5, color="k", ls=":", lw=0.8)
    ax[1].text(0.5, ax[1].get_ylim()[1], "08-05", fontsize=6.5, ha="center", va="bottom")
    ax[1].text(1.5, ax[1].get_ylim()[1], "08-21", fontsize=6.5, ha="center", va="bottom")
    ax[1].set_title("(b) NE43 inside #51 (one point per day)", fontsize=8, pad=10)
    ax[1].tick_params(labelsize=7); ax2.tick_params(labelsize=7)
    fig.tight_layout()
    fig.savefig(HYP / "figures/r1b_null_ne43.png", dpi=170); fig.savefig(HYP / "figures/r1b_null_ne43.pdf")
    print("written")


if __name__ == "__main__":
    main()
