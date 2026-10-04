"""H120 figures from results/results.json and synthetic/summary.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h120lib as L  # noqa: E402

CARD = HERE.parent
BLUE, ORANGE, GREY, RED, GREEN = "#2a78d6", "#e8871e", "#85847e", "#c43a3a", "#2a9d5c"
ORDER = ["4c", "6b", "8", "13", "19a", "27", "38a", "51g", "G38", "51main"]
LABEL = {"4c": "4c", "6b": "6b", "8": "#8", "13": "#13", "19a": "19a", "27": "#27", "38a": "38a", "51g": "51g",
         "G38": "#38 all", "51main": "#51 main"}


def main():
    R = json.loads((L.DATA / "results" / "results.json").read_text())["windows"]
    S = json.loads((L.DATA / "synthetic" / "summary.json").read_text())
    (CARD / "figures").mkdir(exist_ok=True)
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.7))
    ws = [w for w in ORDER if w in R]
    for k, (ch, col, mk) in enumerate((("act", BLUE, "o"), ("talk", ORANGE, "s"))):
        for i, w in enumerate(ws):
            r = R[w][ch]
            x = i + (-0.12 if k == 0 else 0.12)
            ax[0].scatter(x, r["T1"]["R"], color=col, marker=mk, s=22, facecolor=col if r["T1"]["p"] < 0.05 else "white")
            ax[0].scatter(x, r["T2"]["R"], color=col, marker="^", s=18, facecolor=col if r["T2"]["p"] < 0.05 else "white")
            pw = S.get(f"{w}|{ch}|S2", {}).get("T1orT2", np.nan)
            ax[1].bar(x, pw, width=0.22, color=col, alpha=0.8)
    ax[0].axhline(1, color=GREY, lw=0.8)
    ax[0].set_yscale("log")
    ax[0].set_ylabel("drift ratio R")
    ax[0].set_title("drift beyond day-split placebo (filled: p < 0.05)", fontsize=8)
    ax[1].axhline(0.8, color=RED, ls="--", lw=0.8)
    ax[1].set_ylabel("synthetic power at the drift that matters")
    ax[1].set_title("power (T1 or T2), activity blue, talk orange", fontsize=8)
    for a_ in ax:
        a_.set_xticks(range(len(ws)))
        a_.set_xticklabels([LABEL[w] for w in ws], fontsize=6.5, rotation=45)
    fig.tight_layout()
    fig.savefig(CARD / "figures/drift_by_window.pdf")
    plt.close(fig)
    # boundary profile for G38 and 51main (activity)
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.4))
    for a_, w in zip(ax, ("G38", "51main")):
        if w not in R or "boundary_W_all" not in R[w]["act"]:
            continue
        d = R[w]["act"]["boundary_W_all"]
        days = list(d)
        a_.plot(range(len(days)), list(d.values()), color=BLUE, marker="o", ms=2, lw=1)
        from run import BOUNDARIES, PRIMARY_BOUNDARY
        for lab, day in BOUNDARIES[w].items():
            if day in days:
                a_.axvline(days.index(day), color=RED if lab in PRIMARY_BOUNDARY[w] else GREY, lw=0.8, ls="--")
        a_.set_xticks(range(0, len(days), max(1, len(days) // 8)))
        a_.set_xticklabels([days[i][5:] for i in range(0, len(days), max(1, len(days) // 8))], fontsize=6)
        a_.set_title(f"{LABEL[w]}: split score W at each day boundary (activity)", fontsize=8)
        a_.set_ylabel("W")
    fig.tight_layout()
    fig.savefig(CARD / "figures/boundary_profile.pdf")
    for g, w in (("G38", "G38"), ("G51", "51main")):
        p = CARD / f"goalperiod-subhypotheses/{g}/figures"
        p.mkdir(parents=True, exist_ok=True)
        fig.savefig(p / "boundary_profile.pdf")
    plt.close(fig)
    print("figures written")


if __name__ == "__main__":
    main()
