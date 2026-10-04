"""H27 round-1b summary figure (figures/r1b_auc_hub.pdf; reads round-1b outputs only).

(a) AUC of each early-warning trend (onset vs placebo, lead 1 h, W = 15): round 1 vs round 1b (shared labels),
    with period-cluster bootstrap CIs.
(b) #40 at the minute clock: cumulative share of the room's agents with a first strict mention of the hub, and with a
    first work commit to it, against minutes since the kickoff; the first chat link marked.

Usage: uv run python hypotheses/H27-herding-early-warning/analysis/figures_r1b.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OLD = ROOT / "data/processed/H27-herding-early-warning"
R1B = OLD / "r1b"
FIG = HERE.parent / "figures"
C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({"font.size": 7, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "axes.titlesize": 7.2,
                     "axes.titleweight": "bold", "legend.frameon": False, "pdf.fonttype": 42})
KEYS = [("composite", "composite"), ("tau_ar1", "τ AR1"), ("tau_sd", "τ SD"), ("tau_sd_binom", "τ SD binom."),
        ("tau_flick", "τ flicker"), ("mean_last4", "share level")]


def main():
    o = json.loads((OLD / "results_round1.json").read_text())["W15"]["auc"]["4"]
    n = json.loads((R1B / "results_round1.json").read_text())["W15"]["auc"]["4"]
    g = json.loads((R1B / "compare_r1b.json").read_text())["g40"]
    fig, (a, b) = plt.subplots(1, 2, figsize=(4.3, 2.05), gridspec_kw={"width_ratios": [1.1, 1]})
    ys = np.arange(len(KEYS))
    for off, d, col, lab in ((-0.15, o, C2, "round 1 (H11 labels)"), (0.15, n, C1, "round 1b (shared labels)")):
        for y, (k, _) in zip(ys, KEYS):
            a.plot(d[k]["ci"], [y + off, y + off], color=col, lw=1.0, alpha=0.6)
            a.scatter([d[k]["auc"]], [y + off], s=14, color=col, zorder=3, lw=0)
        a.scatter([], [], s=14, color=col, label=lab)
    a.axvline(0.5, color=INK2, lw=0.6, ls="--")
    a.axvline(0.7, color=INK2, lw=0.6, ls=":")
    a.set_yticks(ys, [lab for _, lab in KEYS], fontsize=5.5)
    a.invert_yaxis()
    a.set_xlim(0.2, 1.0)
    a.set_xlabel("AUC, onset vs placebo (8 onsets, 1 h lead)")
    a.set_title("a  No slowing-down signal", loc="left")
    a.legend(loc="center left", fontsize=4.8, handletextpad=0.2, borderaxespad=0.1)
    a.xaxis.grid(True, color=GRID, lw=0.5)
    a.set_axisbelow(True)

    nr = g["n_room_agents"]
    lm = np.array(g["mention_lags_from_kickoff_min"])
    lw = np.array(g["work_lags_from_kickoff_min"])
    T = 40
    for lags, col, lab in ((lm, C2, "first mention of the hub"), (lw, C1, "first commit to the hub")):
        x = np.sort(lags[lags <= T])
        b.step(np.r_[0, x, T], np.r_[0, np.arange(1, len(x) + 1), len(x)] / nr, where="post", color=col, lw=1.6, label=lab)
    b.axvline(g["link_after_kickoff_min"], color=INK2, lw=0.6, ls="--")
    b.text(g["link_after_kickoff_min"] + 0.6, 0.97, "first chat link", fontsize=5, color=INK2, va="top")
    b.axhline(0.5, color=INK2, lw=0.5, ls=":")
    b.axvspan(0, 15, color="#f3f2ee", lw=0, zorder=0)
    b.text(14.5, 0.05, "one 15-min\nwindow", fontsize=5, color=INK2, ha="right", va="bottom")
    b.set_xlim(0, T)
    b.set_ylim(0, 1.02)
    b.set_xlabel("minutes since the #40 kickoff")
    b.set_ylabel("share of the room's 14 agents")
    b.set_title("b  #40 hub, minute clock", loc="left")
    b.legend(loc="center right", bbox_to_anchor=(1.0, 0.25), fontsize=4.8, handletextpad=0.3, borderaxespad=0.1)
    b.yaxis.grid(True, color=GRID, lw=0.5)
    b.set_axisbelow(True)
    fig.tight_layout(pad=0.3, w_pad=0.6)
    fig.savefig(FIG / "r1b_auc_hub.pdf")
    fig.savefig(FIG / "r1b_auc_hub.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    main()
