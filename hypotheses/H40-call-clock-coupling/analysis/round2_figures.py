"""H40 round 2 summary figure: (a) R6 talk split, (b) R1 span split, (c) R5 collapse validity on synthetic worlds.

  uv run python hypotheses/H40-call-clock-coupling/analysis/round2_figures.py
"""
from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h40lib as L  # noqa: E402

INK, INK2, GRID = "#0b0b0b", "#52514e", "#d9d8d4"
C3 = ["#2a78d6", "#eb6834", "#1baf7a"]          # validated (dataviz validator, light surface)
MK = ["o", "s", "D"]
plt.rcParams.update({"font.size": 7.5, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.linewidth": 0.6, "font.family": "serif", "legend.frameon": False,
                     "axes.spines.top": False, "axes.spines.right": False})
R2 = L.OUT / "round2"


def panel_r6(ax):
    gs = [38, 44, 41, 40]
    specs = [("base", "total η"), ("D1_talk", "talk propensity"), ("D1_reptalk", "reply given talk")]
    for j, (sp, lab) in enumerate(specs):
        x, y, e = [], [], []
        for i, g in enumerate(gs):
            r = json.loads((R2 / f"r6_G{g}.json").read_text())[sp]
            x.append(i + (j - 1) * 0.22); y.append(r["coef"]["eta"]); e.append(1.96 * r["se"]["eta"])
        ax.errorbar(x, y, yerr=e, fmt=MK[j], ms=3.4, color=C3[j], ecolor=C3[j], elinewidth=0.9, capsize=0, label=lab,
                    markeredgecolor="white", markeredgewidth=0.5, zorder=3)
    ax.axhline(0, color=INK2, lw=0.8, ls="--", zorder=1)
    ax.set_xticks(range(4), ["G38", "G44", "G41", "G40"])
    ax.axvline(1.5, color=GRID, lw=0.6)
    ax.text(0.5, 0.33, "targets", ha="center", color=INK2, fontsize=6.5)
    ax.text(2.5, 0.33, "contrast", ha="center", color=INK2, fontsize=6.5)
    ax.set_ylim(-0.95, 0.42)
    ax.set_ylabel("span elasticity η")
    ax.grid(axis="y", color=GRID, lw=0.4)
    ax.legend(loc="lower right", fontsize=6.0, handletextpad=0.3, borderaxespad=0.1)
    ax.set_title("(a) R6: why η < 0 (regime III)", fontsize=7.5, loc="left", color=INK)


def panel_r1(ax):
    r = json.loads((R2 / "r1.json").read_text())
    gs = [g for g in r if g not in ("pooled", "24")]
    keys = [("base", "eta", "total η"), ("split", "eta_busy", "previous call busy"), ("split", "eta_wait", "scheduler wait")]
    for j, (sp, k, lab) in enumerate(keys):
        x = [i + (j - 1) * 0.22 for i in range(len(gs))]
        y = [r[g][sp]["coef"][k] for g in gs]
        e = [1.96 * r[g][sp]["se"][k] for g in gs]
        ax.errorbar(x, y, yerr=e, fmt=MK[j], ms=3.0, color=C3[j], ecolor=C3[j], elinewidth=0.7, capsize=0, alpha=0.55,
                    markeredgecolor="white", markeredgewidth=0.4, zorder=2)
        pk = {"eta": "eta", "eta_busy": "eta_busy", "eta_wait": "eta_wait"}[k]
        p = r["pooled"][pk]
        xp = len(gs) + 0.4 + (j - 1) * 0.22
        ax.errorbar([xp], [p["mean"]], yerr=[[p["mean"] - p["lo"]], [p["hi"] - p["mean"]]], fmt=MK[j], ms=4.2,
                    color=C3[j], ecolor=C3[j], elinewidth=1.3, capsize=0, label=lab, markeredgecolor="white",
                    markeredgewidth=0.5, zorder=3)
    ax.axhline(0, color=INK2, lw=0.8, ls="--", zorder=1)
    ax.axhline(0.84, color=INK2, lw=0.8, ls=":", zorder=1)
    ax.text(-0.45, 1.9, "dotted: wall-clock η_wait (synthetic)", color=INK2, fontsize=6.0)
    ax.set_xticks(list(range(len(gs))) + [len(gs) + 0.4], [f"G{g}" for g in gs] + ["pooled"])
    ax.set_ylim(-2.2, 2.4)
    ax.set_ylabel("elasticity")
    ax.grid(axis="y", color=GRID, lw=0.4)
    ax.legend(loc="lower left", fontsize=6.0, handletextpad=0.3, ncol=1)
    ax.set_title("(b) R1: regime-I span split (Gemini, logged)", fontsize=7.5, loc="left", color=INK)


def panel_r5(ax):
    d = pl.concat([pl.read_parquet(f) for f in sorted(glob.glob(str(R2 / "r5syn_*.parquet")))])
    s = d.group_by("goal", "clock").agg(pl.col("lab_call_better").mean(), pl.col("raw_call_better").mean()).sort("goal")
    gs = sorted(s["goal"].unique().to_list())
    for j, (clock, lab) in enumerate((("call", "call-clock worlds"), ("wall", "wall-clock worlds"))):
        v = [s.filter((pl.col("goal") == g) & (pl.col("clock") == clock))["lab_call_better"][0] for g in gs]
        ax.bar(np.arange(len(gs)) + (j - 0.5) * 0.36, v, width=0.34, color=C3[j], label=lab, zorder=3)
    ax.axhline(0.8, color=INK2, lw=0.8, ls="--", zorder=1)
    ax.text(2.0, 0.84, "validity bar 0.8", ha="center", color=INK2, fontsize=6.0)
    ax.set_xticks(range(len(gs)), [f"G{g}" + ("c" if g == 51 else "") for g in gs])
    ax.set_ylim(0, 1.45)
    ax.set_ylabel("share picking call clock")
    ax.grid(axis="y", color=GRID, lw=0.4)
    ax.legend(loc="upper center", fontsize=6.0, handletextpad=0.3, ncol=2, columnspacing=0.8)
    ax.set_title("(c) R5: collapse validity (synthetic)", fontsize=7.5, loc="left", color=INK)


def main():
    fig, axs = plt.subplots(1, 3, figsize=(7.0, 2.3), gridspec_kw=dict(width_ratios=[1.0, 1.15, 1.0]))
    panel_r6(axs[0]); panel_r1(axs[1]); panel_r5(axs[2])
    fig.tight_layout(pad=0.4, w_pad=0.8)
    for ext in ("pdf", "png"):
        fig.savefig(L.FIG / f"round2_summary.{ext}", dpi=200)
    print(L.FIG / "round2_summary.pdf")


if __name__ == "__main__":
    main()
