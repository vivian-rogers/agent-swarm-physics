"""Focused observable figure for the H17 one-page summary (figures/summary_obs.pdf, ~4.3 x 2.6 in).

t2* per goal period (pooled MSM, tau_c = 5 min) with its agent-day 95% CI, the N2 sojourn-null median, and the
median per-agent t2 (free of agent-mixture inflation). Reads summary.json and G<NN>/result.json.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
import matplotlib.ticker

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
CARD = HERE.parent
ROOT = CARD.parents[1]
DATA = ROOT / "data/processed/H17-behavior-metastable-sets"
REG = {"I": "#4f8fc0", "II": "#9b9b9b", "III": "#c0504d"}


def main():
    S = json.loads((DATA / "summary.json").read_text())
    rows = S["table"]
    plt.rcParams.update({"font.size": 7, "axes.spines.top": False, "axes.spines.right": False})
    fig, ax = plt.subplots(figsize=(4.3, 1.9))
    for i, r in enumerate(rows):
        pa = json.loads((DATA / f"G{r['goal']:02d}" / "result.json").read_text())["primary"]["per_agent"]
        med = np.median([a["t2"] for a in pa if a["t2"] > 0])
        c = REG[r["regime"]]
        ax.errorbar(i, r["t2"], yerr=[[r["t2"] - r["t2_lo"]], [r["t2_hi"] - r["t2"]]], fmt="o", color=c, ms=3.2, lw=0.9,
                    label="pooled t2* (95% CI)" if i == 0 else None)
        ax.plot(i, r["n2_med"], "_", color="k", ms=6, mew=1.1, label="sojourn null N2 (median)" if i == 0 else None)
        ax.plot(i, med, "o", mfc="white", mec=c, ms=3.2, mew=0.8, label="median per-agent t2" if i == 0 else None)
    ax.set_yscale("log")
    ax.set_yticks([3, 5, 10, 20])
    ax.set_yticklabels(["3", "5", "10", "20"])
    ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.set_xticks(range(len(rows)))
    ax.set_xticklabels([str(r["goal"]) for r in rows], rotation=90, fontsize=5.5)
    ax.set_xlabel("goal period", fontsize=6, labelpad=1)
    ax.set_ylabel("t2 (active min)")
    ax.legend(fontsize=5.5, frameon=False, loc="upper left")
    fig.tight_layout(pad=0.3)
    fig.savefig(CARD / "figures" / "summary_obs.pdf")
    print("ok")


if __name__ == "__main__":
    main()
