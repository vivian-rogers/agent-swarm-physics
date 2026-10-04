"""H79 figures: summary_obs.pdf (catalyst classes and time arrow per period), summary_synthetic.pdf."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
D = ROOT / "data/processed/H79-artifact-autocatalytic-set"
FIG = HERE.parent / "figures"
PER = ["G31", "G38", "G40", "G41", "G51"]
C = {"self": "#2a78d6", "food": "#86b6ef", "new": "#e34948", "none": "#ecebe6"}


def style(ax):
    ax.tick_params(labelsize=7)
    ax.spines[["top", "right"]].set_visible(False)


def obs():
    R = {p: json.loads((D / f"results/{p}.json").read_text()) for p in PER}
    fig, ax = plt.subplots(1, 2, figsize=(6.6, 2.5), gridspec_kw={"width_ratios": [1.5, 1]})
    x = np.arange(len(PER))
    s = np.array([R[p]["real"]["self_share_work"] for p in PER])
    f = np.array([R[p]["real"]["food_tool_share_work"] for p in PER])
    n = np.array([R[p]["real"]["inperiod_tool_share_work"] for p in PER])
    cov = np.array([R[p]["real"]["coverage"] for p in PER])
    ax[0].bar(x, s, color=C["self"], label="self (classes overlap)")
    ax[0].bar(x, f, bottom=s, color=C["food"], label="pre-period tool")
    ax[0].bar(x, n, bottom=s + f, color=C["new"], label="in-period tool (artifact layer)")
    ax[0].scatter(x, cov, marker="_", s=200, color="#0b0b0b", label="maxRAF coverage", zorder=3)
    ax[0].axhline(0.2, color="#85847e", ls="--", lw=0.8)
    ax[0].text(-0.45, 0.205, "P1 bound", fontsize=6, color="#85847e", ha="left", va="bottom")
    ax[0].set_xticks(x, PER)
    ax[0].set_ylabel("share of agent work commits", fontsize=7)
    ax[0].legend(fontsize=5.5, frameon=False, loc="upper right")
    ax[0].set_ylim(0, 0.62)
    style(ax[0])
    r = np.array([R[p]["time_arrow"]["ratio"] for p in PER])
    lo = np.array([R[p]["time_arrow"]["ratio_ci"][0] for p in PER])
    hi = np.array([R[p]["time_arrow"]["ratio_ci"][1] for p in PER])
    ax[1].errorbar(x, r, yerr=[r - lo, hi - r], fmt="o", color="#2a78d6", ms=4, capsize=2)
    ax[1].axhline(1, color="#85847e", lw=0.8)
    ax[1].set_xticks(x, PER)
    ax[1].set_ylabel("executions before / after write", fontsize=7)
    ax[1].set_ylim(0.4, 1.2)
    ax[1].text(0, 1.04, "P4 predicts > 1", fontsize=6, color="#85847e")
    style(ax[1])
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs.pdf")


def synth():
    d = json.loads((D / "synthetic.json").read_text())
    ks = [0, 1, 3, 5]
    u = [d["S1b_unweighted_first_run"][f"k{k}"]["detect_rate"] for k in ks]
    s = [d["S1b_planted_3cycles"][f"k{k}"]["detect_rate(S3 & p<0.05)"] for k in ks]
    fig, ax = plt.subplots(figsize=(3.3, 2.0))
    ax.plot(ks, u, "o-", color="#e34948", ms=3, label="all cross edges")
    ax.plot(ks, s, "s-", color="#2a78d6", ms=3, label="edges with $\\geq$3 events (A2)")
    ax.set_xlabel("events per planted edge (0 = nothing planted)", fontsize=7)
    ax.set_ylabel("detection rate", fontsize=7)
    ax.set_ylim(-0.05, 1.05)
    ax.legend(fontsize=6, frameon=False)
    style(ax)
    fig.tight_layout()
    fig.savefig(FIG / "summary_synthetic.pdf")


if __name__ == "__main__":
    obs()
    synth()
