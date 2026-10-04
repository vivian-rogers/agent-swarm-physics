"""H89 summary figures: figures/summary_obs.pdf (migration shares, persistence C) and figures/summary_obsb.pdf
(synthetic calibration: migration share vs day-field fraction).

  uv run python hypotheses/H89-price-equation-culture/analysis/figures.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
HYP = HERE.parent
DATA = HYP.parents[1] / "data/processed/H89-price-equation-culture"
FIG = HYP / "figures"
BLUE, ORANGE, AQUA, YELLOW, MAGENTA = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"
INK, MUTED, GRID = "#1a1a19", "#6b6a63", "#e4e3dc"
plt.rcParams.update({"font.size": 7.5, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
                     "font.family": "serif"})


def obs():
    rep = json.loads((DATA / "replication/replication.json").read_text())["periods"]
    E = [r for r in rep.values() if r["eligible"] and r["verdict"] != "n/a"]
    E.sort(key=lambda r: r["goal"])
    x = np.arange(len(E))
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.4), gridspec_kw=dict(width_ratios=[1.35, 1]))
    a = ax[0]
    s = np.array([r["style.s_mig"] for r in E]); c = np.array([r["content_bge.s_mig"] for r in E])
    for i in range(len(E)):
        a.plot([x[i], x[i]], [c[i], s[i]], color=GRID, lw=1.2, zorder=1)
    a.scatter(x, s, s=14, color=BLUE, label="style", zorder=3, edgecolor="white", linewidth=0.6)
    a.scatter(x, c, s=14, color=ORANGE, label="content (bge)", zorder=3, edgecolor="white", linewidth=0.6)
    a.axhline(0, color=MUTED, lw=0.6)
    a.set_xticks(x); a.set_xticklabels([f"{r['goal']}" for r in E], rotation=90, fontsize=5.5)
    a.set_xlabel("goal period"); a.set_ylabel("migration share $s_{\\rm Mig}$ (energy)")
    a.set_title("(a) style moves by migration more than content (21/33)", fontsize=7.5, loc="left", color=INK)
    a.legend(frameon=False, loc="upper left", fontsize=6.5)
    a.grid(axis="y", color=GRID, lw=0.5)
    b = ax[1]
    C = np.array([r["content_bge.C"] for r in E]); se = np.array([r["content_bge.C.se"] for r in E])
    o = np.argsort(C)
    b.errorbar(np.arange(len(E)), C[o], yerr=1.96 * se[o], fmt="o", ms=3, color=BLUE, ecolor=GRID, elinewidth=1.0)
    b.axhline(-0.5, color=ORANGE, lw=1.0, ls="--")
    b.text(len(E) - 1, -0.47, "iid day topics", ha="right", va="bottom", fontsize=6, color=INK)
    b.axhline(0, color=MUTED, lw=0.8)
    b.text(0, 0.03, "random walk; > 0 = directed drift", ha="left", va="bottom", fontsize=6, color=INK)
    b.set_ylim(-1.0, 0.9)
    b.set_xticks([]); b.set_xlabel("periods, sorted by $C$")
    b.set_ylabel("persistence $C$ (content)")
    b.set_title("(b) no attractor: $C>0$ in 0/29", fontsize=7.5, loc="left", color=INK)
    b.grid(axis="y", color=GRID, lw=0.5)
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs.pdf")
    plt.close(fig)


def obsb():
    rep = json.loads((DATA / "replication/replication.json").read_text())["periods"]
    syn = json.loads((DATA / "synthetic/synthetic.json").read_text())
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.1))
    a = ax[0]
    cols = [BLUE, ORANGE, AQUA, YELLOW, MAGENTA]
    for col, g in zip(cols, ["20", "31", "38", "51"]):
        cur = rep[g]["calib_curve"]
        ph = [float(k) for k in cur if float(k) > 0]
        a.plot(ph, [cur[str(p) if str(p) in cur else p] for p in ph], "-o", ms=3, lw=1.5, color=col, label=f"G{g}")
        sm, cm = rep[g]["style.s_mig"], rep[g]["content_bge.s_mig"]
        a.axhline(sm, color=col, lw=0.6, ls=":")
    a.set_xscale("log"); a.set_xlabel("day-field fraction $\\varphi$ of the agent-day signal")
    a.set_ylabel("true $s_{\\rm Mig}$ (noise-free)")
    a.set_title("(a) migration share gauges the day field", fontsize=7.5, loc="left", color=INK)
    a.legend(frameon=False, fontsize=6, ncol=2)
    a.grid(color=GRID, lw=0.5)
    b = ax[1]
    labels, xfb, nvb = [], [], []
    for sc, lab in (("F99", "1%"), ("F97", "3%"), ("S1w", "10%"), ("S1", "50%")):
        v1 = [syn[g]["content"][sc]["trans"]["xf_bias"] for g in ("20", "31", "38", "51")]
        v2 = [syn[g]["content"][sc]["trans"]["naive_bias"] for g in ("20", "31", "38", "51")]
        labels.append(lab); xfb.append(np.median(v1)); nvb.append(np.median(v2))
    xx = np.arange(len(labels))
    b.bar(xx - 0.18, nvb, 0.34, color=ORANGE, label="naive (whole sample)")
    b.bar(xx + 0.18, xfb, 0.34, color=BLUE, label="cross-fitted halves")
    b.axhline(0, color=MUTED, lw=0.6)
    b.set_xticks(xx); b.set_xticklabels(labels); b.set_xlabel("planted day-field fraction")
    b.set_ylabel("bias of $s_{\\rm Trans}$ (median)")
    b.set_title("(b) noise bias where $\\rho_\\Delta\\geq0.3$", fontsize=7.5, loc="left", color=INK)
    b.legend(frameon=False, fontsize=6)
    b.grid(axis="y", color=GRID, lw=0.5)
    fig.tight_layout()
    fig.savefig(FIG / "summary_obsb.pdf")
    plt.close(fig)


if __name__ == "__main__":
    FIG.mkdir(exist_ok=True)
    obs()
    obsb()
    print("figures written")
