"""H47 visual: rooms bound content coherence, sharply where they do different things, and the boundary moves with
the channel (NE42 merge/split).

Static (fig.pdf/png, double column):
  (a) simulation: agent-agent content correlations in a 5 + 10 two-room soft-spin world with room-specific drives
      ("different work") vs one shared drive ("same task"); the room contrast C_B is the cross/within ratio;
  (b) C_B per period (30-min windows, day-bootstrap 95% CI) against the between-room topic separation F (post hoc
      axis), with the room-relabel null (C_B medians of random partitions, gray band) and the C_B = 0.3 rule line;
  (c) NE42 A-B-A: cross-partition / within-partition correlation r_X in #39 (two rooms), #40 (merged), #41 (split
      again), with the partition-permutation null medians (gray) and the DiD.
All measured numbers are read from H47's results (summary.json, coherence.json, separation.json, ne42.json).

Run: uv run python writeup/visuals/H47-room-coherence-length/make.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import _rooms_common as rc  # noqa: E402
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

import vstyle as vs  # noqa: E402

R = "H47-room-coherence-length/results/"
SUM = rc.load_json(R + "summary.json")["periods"]
COH = rc.load_json(R + "coherence.json")
SEP = rc.load_json(R + "separation.json")
NE = rc.load_json(R + "ne42.json")
FIELDED = ("G38", "G44")
C_FORK = vs.C["green"]


def sim_corr(room_drive: float, global_drive: float, seed: int = 1):
    """Two rooms (5 + 10 agents), 400 windows: x_i = room drive + global drive + agent noise; correlation matrix."""
    rng = np.random.default_rng(seed)
    T, rooms = 400, np.r_[np.zeros(5, int), np.ones(10, int)]
    hr = rng.normal(0, 1, (T, 2)); hg = rng.normal(0, 1, T)
    X = room_drive * hr[:, rooms] + global_drive * hg[:, None] + rng.normal(0, 1, (T, 15))
    C = np.corrcoef(X.T)
    np.fill_diagonal(C, np.nan)
    w = C[rooms[:, None] == rooms[None, :]]; c = C[rooms[:, None] != rooms[None, :]]
    return C, np.nanmean(c) / np.nanmean(w)


def panel_sim(fig, spec):
    sub = GridSpecFromSubplotSpec(1, 2, subplot_spec=spec, wspace=0.12)
    axes = []
    for j, (rd, gd, t) in enumerate(((1.1, 0.25, "different work"), (0.6, 1.0, "same task"))):
        ax = fig.add_subplot(sub[j]); axes.append(ax)
        C, cb = sim_corr(rd, gd)
        im = ax.imshow(C, cmap=vs.DIV, vmin=-0.7, vmax=0.7, interpolation="nearest")
        ax.axhline(4.5, color=vs.INK, lw=0.6); ax.axvline(4.5, color=vs.INK, lw=0.6)
        ax.set_xticks([2, 9.5], ["A", "B"], fontsize=6.5)
        ax.set_yticks([2, 9.5], ["A", "B"] if j == 0 else [], fontsize=6.5)
        ax.tick_params(length=0); ax.grid(False)
        ax.set_title(f"{t}\n$C_B={cb:.2f}$", fontsize=7)
    axes[0].text(0.0, 1.38, "(a) simulation: agent–agent correlation", transform=axes[0].transAxes, fontsize=8.5,
                 ha="left", va="bottom")
    cax = fig.add_axes([axes[1].get_position().x1 + 0.004, axes[1].get_position().y0, 0.005,
                        axes[1].get_position().height])
    cb = fig.colorbar(im, cax=cax); cb.ax.tick_params(labelsize=5.5, length=1.5); cb.outline.set_visible(False)
    return axes, cax


def panel_CB(ax):
    per = ["G35", "G36", "G37", "G38", "G39", "G41", "G42", "G44"]
    nulls = [COH[k]["w30"]["null_CB_med"] for k in per]
    ax.axhspan(min(nulls), max(nulls), color=vs.NULL, alpha=0.6, lw=0)
    ax.text(8.7, max(nulls) + 0.02, "random rooms\n(relabel median)", fontsize=6, color=vs.INK2, ha="right",
            va="bottom")
    ax.axhline(0.3, color=vs.MUTED, lw=0.7, ls="--")
    ax.text(5.6, 0.32, "rule: $C_B\\leq0.3$", fontsize=6, color=vs.MUTED, ha="center", va="bottom")
    for k in per:
        v = SUM[k]; F = SEP[k]["median_F"]; lo, hi = v["C_B_ci"]
        col = vs.FIELD if k in FIELDED else C_FORK if k == "G35" else vs.COUPLING if k == "G41" else vs.INK2
        mk = "o" if k in FIELDED else "s" if k == "G35" else "D" if k == "G41" else "^"
        ax.errorbar(F, v["C_B"], yerr=[[v["C_B"] - lo], [hi - v["C_B"]]], fmt=mk, color=col, ms=4, lw=0.8,
                    capsize=1.5, zorder=3)
        dx, dy, ha = 0.15, 0.0, "left"
        if k == "G42":
            dx, ha = -0.15, "right"
        if k == "G41":
            dx, dy, ha = -0.15, 0.1, "right"
        ax.text(F + dx, v["C_B"] + dy, f"#{k[1:]}", fontsize=6.2, color=col, ha=ha, va="center")
    ax.set_xlim(1, 8.8); ax.set_ylim(-0.75, 1.45)
    ax.set_xlabel("between-room topic separation $F$ (median day)")
    ax.set_ylabel("room contrast $C_B=\\rho_c/\\rho_w$")
    ax.set_title("(b) sharp boundary where work differs", loc="left")
    h = [Line2D([], [], marker="o", ls="", color=vs.FIELD, ms=4, label="room-specific kickoffs"),
         Line2D([], [], marker="D", ls="", color=vs.COUPLING, ms=4, label="#41: same kickoff, split work"),
         Line2D([], [], marker="^", ls="", color=vs.INK2, ms=4, label="identical kickoffs"),
         Line2D([], [], marker="s", ls="", color=C_FORK, ms=4, label="#35 fork week")]
    ax.legend(handles=h, loc="lower center", bbox_to_anchor=(0.47, 0.0), fontsize=5.9, handlelength=1.0,
              borderaxespad=0.2, ncol=2, columnspacing=0.6)
    ax.text(1.15, -0.2, "post hoc: Spearman $-0.83$ ($p$ 0.014)", fontsize=6, color=vs.MUTED,
            va="center")


def panel_NE42(ax):
    o = NE["obs"]; ph = ["39", "40", "41"]
    x = np.arange(3)
    for i, nm in enumerate(NE["null_rX_median"]):
        ax.add_patch(plt.Rectangle((i - 0.28, 0), 0.56, nm, color=vs.NULL, alpha=0.6, lw=0))
    y = [o[p]["r_X"] for p in ph]
    ax.plot(x, y, color=vs.COUPLING, lw=1.5, marker="D", ms=5, zorder=3)
    for i, p in enumerate(ph):
        ax.text(i + 0.12, y[i] + 0.05, f"{y[i]:.2f}", fontsize=6.5, color=vs.COUPLING, va="bottom")
    ax.set_xticks(x, ["#39\ntwo rooms", "#40\nmerged", "#41\nsplit again"], fontsize=6.6)
    ax.set_xlim(-0.5, 2.6); ax.set_ylim(0, 1.9)
    ax.set_ylabel("cross / within partition $r_X$")
    lo, hi = NE["DiD_ci"]
    ax.text(0.5, 0.96, f"DiD = {NE['DiD']:.2f} [{lo:.2f}, {hi:.2f}], $p$ = {NE['p_DiD']:.3f}", transform=ax.transAxes,
            ha="center", va="top", fontsize=6.4)
    ax.set_title("(c) NE42: it follows the channel", loc="left")
    ax.text(0.5, 0.88, "gray: random partition (median)", transform=ax.transAxes, ha="center", va="top", fontsize=6,
            color=vs.INK2)


def make_static():
    vs.use()
    fig = plt.figure(figsize=(vs.W["double"], 2.75))
    gs = GridSpec(1, 3, figure=fig, width_ratios=[0.95, 1.25, 0.9], wspace=0.55, left=0.02, right=0.99, top=0.83,
                  bottom=0.2)
    panel_sim(fig, gs[0])
    panel_CB(fig.add_subplot(gs[1]))
    panel_NE42(fig.add_subplot(gs[2]))
    vs.save(fig, HERE / "fig")
    plt.close(fig)


if __name__ == "__main__":
    make_static()
