"""H147 round 1 summary figure: per memeplex, the wipe value dV_K,F (A1 rate form, pseudo-pattern excess, bootstrap
CI) and the host relation on own-repo commits (A2, activity held, bootstrap CI), coloured by the host class.
Usage: uv run python hypotheses/H147-egregore-value-and-hosts-51/analysis/figures.py
Output: hypotheses/H147-egregore-value-and-hosts-51/figures/h147_obs.pdf
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import h147common as C  # noqa: E402

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

CLS = {"parasitic": "#c0392b", "neutral": "#8a8a8a", "mutualist": "#2e8b57"}
INK, MUTED = "#222222", "#777777"


def main():
    df = pl.read_parquet(C.OUT / "results" / "patterns.parquet").filter(pl.col("source") == "H145")
    df = df.sort("h_K")
    n = df.height
    y = np.arange(n)
    names = [f"{i} ({(lab or '')[:28]})" for i, lab in zip(df["id"], df["label"])]
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 0.32 * n + 1.3), sharey=True)
    for a in ax:
        a.axvline(0, color=MUTED, lw=0.8, zorder=0)
        a.spines[["top", "right"]].set_visible(False)
        a.tick_params(labelsize=7, colors=INK)
    col = [CLS.get(c, MUTED) for c in df["class"]]
    lo, hi, est = df["dV_lo"].to_numpy(), df["dV_hi"].to_numpy(), df["dV_rate"].to_numpy()
    ax[0].hlines(y, lo, hi, color=MUTED, lw=1.5)
    ax[0].scatter(est, y, s=22, color=INK, zorder=3)
    ax[0].axvspan(-0.05, 0.05, color="#dddddd", zorder=-1, lw=0)
    ax[0].axvline(-0.10, color=MUTED, lw=0.8, ls="--")
    ax[0].set_xlabel(r"wipe value $\Delta V_{K,F}$ (rate form, excess)", fontsize=7.5)
    ax[0].set_yticks(y, names, fontsize=6.5)
    for j, h in enumerate(df["h_K"].to_list()):
        ax[0].annotate(f"h={h:.2f}" if h is not None else "", (1.0, j), xycoords=("axes fraction", "data"),
                       fontsize=5.5, color=MUTED, ha="right", va="center")
    lo, hi, est = df["host_c_lo"].to_numpy(), df["host_c_hi"].to_numpy(), df["host_c"].to_numpy()
    ax[1].hlines(y, lo, hi, color=col, lw=1.5)
    ax[1].scatter(est, y, s=22, color=col, zorder=3)
    ax[1].axvline(-0.10, color=MUTED, lw=0.8, ls="--")
    ax[1].axvline(0.05, color=MUTED, lw=0.8, ls=":")
    ax[1].set_xlabel("hosting effect on own-repo commits (A2)", fontsize=7.5)
    for c, k in CLS.items():
        ax[1].scatter([], [], color=k, s=22, label=c)
    ax[1].legend(fontsize=6, frameon=False, loc="lower right")
    fig.tight_layout()
    out = C.HYP / "figures" / "h147_obs.pdf"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out)
    print(out)


if __name__ == "__main__":
    main()
