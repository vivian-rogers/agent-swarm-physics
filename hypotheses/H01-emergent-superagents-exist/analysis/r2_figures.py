"""H01 round 2 figures (static PDFs for the RevTeX summary and the card).

  figures/r2_summary_obs.pdf  (a) R4 composition excess per unit by coarse-graining; (b) R4d/R6b allocation
                              continuity across nights (leave-out), same coarse-grainings + singletons (substrate)
  figures/r2_synthetic.pdf    axis F: three tests by synthetic world, with the village's value as a dashed line
  figures/r2_kw.pdf           R5: KW stored value Delta V_st per unit with its Pinsker envelope; goal-change scramble
Palette: the validated categorical order (dataviz reference instance); categories are labelled on the axis.
Run: uv run python hypotheses/H01-emergent-superagents-exist/analysis/r2_figures.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r2lib as L  # noqa: E402,F401

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

R2 = L.ROOT / "data/processed/H01-emergent-superagents-exist/round2"
FIG = HERE.parent / "figures"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7"]
plt.rcParams.update({"font.size": 7.5, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "font.family": "serif"})


def strip(ax, cats, vals, colors, ylabel, hlines=(), med=True, jitter=0.12, seed=0):
    rng = np.random.default_rng(seed)
    for i, (v, c) in enumerate(zip(vals, colors)):
        v = np.asarray([x for x in v if x is not None and np.isfinite(x)], float)
        if not len(v):
            continue
        ax.scatter(i + rng.uniform(-jitter, jitter, len(v)), v, s=11, color=c, edgecolor="white", linewidth=0.5, zorder=3)
        if med:
            ax.plot([i - 0.28, i + 0.28], [np.median(v)] * 2, color=INK, lw=1.4, zorder=4, solid_capstyle="round")
    for y, ls in hlines:
        ax.axhline(y, color=INK2, lw=0.7, ls=ls, zorder=1)
    ax.set_xticks(range(len(cats)))
    ax.set_xticklabels(cats, rotation=35, ha="right", fontsize=6.8)
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", color=GRID, lw=0.5, zorder=0)


def fig_summary(r):
    per = r["r4"]["per_unit_summary"]
    cg = ["crew", "sync", "coalloc", "comm", "room", "lab"]
    lab = ["crew", "synchrony", "co-alloc.", "reply", "room", "lab"]
    fig, axs = plt.subplots(1, 2, figsize=(7.0, 2.5), gridspec_kw={"width_ratios": [1, 1.15]})
    strip(axs[0], lab, [[per[u][k]["median_z"] for u in per] for k in cg], CAT[:6],
          "individuality excess z\n(unit median, vs random groups)", hlines=((0, "-"), (1.64, ":")))
    axs[0].set_title("(a) R4: no coarse-graining is an individuality maximum", fontsize=7.5, color=INK, loc="left")
    d = r["r4d"]["per_unit"]
    cg2 = ["sub", "crew", "coalloc", "sync", "comm", "room", "lab"]
    lab2 = ["single agent", "crew", "co-alloc.", "synchrony", "reply", "room", "lab"]
    cols = [CAT[6]] + CAT[:6]
    cols = [CAT[6], CAT[0], CAT[2], CAT[1], CAT[3], CAT[4], CAT[5]]
    strip(axs[1], lab2, [[(d[u][k] or {}).get("dC") for u in d] for k in cg2], cols,
          r"continuity across nights $\Delta C$" + "\n(vs permutation null)", hlines=((0, "-"), (0.2, ":")))
    axs[1].set_title("(b) allocation persists overnight, most for single agents", fontsize=7.5, color=INK, loc="left")
    fig.tight_layout()
    fig.savefig(FIG / "r2_summary_obs.pdf")
    plt.close(fig)


def fig_synthetic(r, syn):
    S = syn["summary"]
    worlds = ["super", "supersync", "ind", "env"]
    wl = ["superagent", "super+sync", "individual", "environment"]
    tests = [("r4_crew_median_z", "R4c crews' individuality z", np.median([s["crew"]["median_z"] for s in r["r4"]["per_unit_summary"].values() if s["crew"]["median_z"] is not None])),
             ("r6b_dC_median", r"R6b night continuity $\Delta C$", r["r4d"]["R6b_leaveout"]["median_dC"]),
             ("r6c_ml_minus_base", "R6c continuity after memory loss\n(event $-$ base)", r["r6"]["memory_loss"]["unique_diff"])]
    fig, axs = plt.subplots(1, 3, figsize=(7.0, 2.1))
    for ax, (key, title, real) in zip(axs, tests):
        vals = [S.get(f"{w}/village", {}).get(key) for w in worlds]
        longv = [S.get(f"{w}/long", {}).get(key) for w in worlds]
        ax.scatter(range(4), vals, s=28, color=[CAT[0], CAT[0], CAT[1], CAT[2]], zorder=3, label="village-sized")
        ax.scatter(np.arange(4) + 0.18, longv, s=16, facecolor="white", edgecolor=[CAT[0], CAT[0], CAT[1], CAT[2]],
                   lw=1.0, zorder=3, label="#51-sized")
        ax.axhline(real, color=INK, lw=0.9, ls="--", zorder=2)
        ax.text(3.45, real, "village", color=INK, fontsize=6.5, va="bottom", ha="right")
        ax.axhline(0, color=INK2, lw=0.6)
        ax.set_xticks(range(4))
        ax.set_xticklabels(wl, rotation=25, ha="right")
        ax.set_title(title, fontsize=7.2, color=INK, loc="left")
        ax.grid(axis="y", color=GRID, lw=0.5, zorder=0)
    axs[0].legend(frameon=False, fontsize=6, loc="lower left")
    fig.tight_layout()
    fig.savefig(FIG / "r2_synthetic.pdf")
    plt.close(fig)


def fig_kw(r):
    v = r["r5"]["verdict"]["per_unit"]
    units = list(v)
    fig, axs = plt.subplots(1, 2, figsize=(7.0, 2.2), gridspec_kw={"width_ratios": [1.6, 1]})
    ax = axs[0]
    x = np.arange(len(units))
    pin = np.array([v[u]["pinsker"] for u in units])
    ax.bar(x, 2 * pin, bottom=-pin, width=0.8, color=GRID, zorder=0, label=r"Pinsker envelope $\pm\sqrt{I/2}$")
    dv = np.array([v[u]["dV_st"] for u in units])
    lo = np.array([v[u]["lo"] if v[u]["lo"] is not None else v[u]["dV_st"] for u in units])
    hi = np.array([v[u]["hi"] if v[u]["hi"] is not None else v[u]["dV_st"] for u in units])
    ax.errorbar(x, dv, yerr=[dv - lo, hi - dv], fmt="o", ms=3.5, color=CAT[0], ecolor=CAT[0], elinewidth=0.9, zorder=3,
                label=r"crews $\Delta V_{st}$ (95% CI)")
    ax.scatter(x, [v[u]["dV_obs"] for u in units], marker="s", s=9, color=CAT[1], zorder=3, label=r"$\Delta V_{obs}$")
    ax.axhline(0, color=INK2, lw=0.6)
    ax.set_ylim(-0.12, 0.12)
    ax.set_xticks(x)
    ax.set_xticklabels(units, rotation=60, fontsize=6)
    ax.set_ylabel(r"KW value (advancement, 2 h)")
    ax.set_title("(a) R5: no positive semantic information about the activity environment", fontsize=7.2, color=INK, loc="left")
    ax.legend(frameon=False, fontsize=6, loc="lower left", ncol=1)
    ax = axs[1]
    gc = r["r5"]["goal_change"]["boundaries"]
    names = list(gc)
    ax.errorbar(range(len(names)), [gc[n]["mean_dV"] for n in names], yerr=[1.96 * (gc[n]["se"] or 0) for n in names], fmt="o",
                ms=3.5, color=CAT[0], elinewidth=0.9)
    for i, n in enumerate(names):
        if gc[n]["kind"] == "continuation":
            ax.scatter(i, gc[n]["mean_dV"], s=60, facecolor="none", edgecolor=CAT[1], lw=1.2, zorder=4)
    m = r["r5"]["goal_change"]["meta_new"]
    ax.axhline(m["mu"], color=INK, ls="--", lw=0.9)
    ax.axhline(0, color=INK2, lw=0.6)
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels([n.replace("->", "→") for n in names], rotation=60, fontsize=6)
    ax.set_ylabel(r"$\Delta V_{adv}$, days 1–2 of next goal")
    ax.set_title("(b) goal change (relevance scramble)", fontsize=7.2, color=INK, loc="left")
    ax.text(len(names) - 0.5, m["mu"], f"meta {m['mu']:+.2f}", fontsize=6, ha="right", va="bottom", color=INK)
    fig.tight_layout()
    fig.savefig(FIG / "r2_kw.pdf")
    plt.close(fig)


def main():
    r = json.loads((R2 / "results.json").read_text())
    syn = json.loads((R2 / "synthetic.json").read_text())
    FIG.mkdir(exist_ok=True)
    fig_summary(r)
    fig_synthetic(r, syn)
    fig_kw(r)
    print("figures written")


if __name__ == "__main__":
    main()
