"""H128 figures: summary_obs.pdf (dw curves by kickoff code; freeze time and drift per unit) and summary_synth.pdf
(synthetic class rates by world for dw and N_p). Colors: Okabe-Ito (writeup/visuals/STYLE.md): named blue, free orange.
Usage: uv run python hypotheses/H128-coarsening-vs-freeze/analysis/figures.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h128lib as L  # noqa: E402

BLUE, ORANGE, INK, MUTED, GRID, NULL = "#0072B2", "#E69F00", "#1a1a1a", "#8c8c8c", "#e6e6e6", "#b3b3b3"
FIG = HERE.parent / "figures"
plt.rcParams.update({"font.size": 8, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": INK2 if False else INK,
                     "ytick.color": INK, "axes.spines.top": False, "axes.spines.right": False})


def obs():
    u = json.loads((L.D / "results/units.json").read_text())
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.6), gridspec_kw={"width_ratios": [1.35, 1]})
    a = ax[0]
    for name in [f"G{g:02d}" for g in L.REPL]:
        c = pl.read_parquet(L.D / name / "curve.parquet").filter(pl.col("dw").is_not_nan())
        col = BLUE if u[name]["code"] == "named" else ORANGE
        a.plot(c["t"], c["dw"].rolling_mean(4, min_samples=1), color=col, lw=1.0, alpha=0.75)
        a.text(c["t"][-1] + 0.2, c["dw"].tail(4).mean(), name[1:], color=col, fontsize=5.5, va="center")
    a.plot([], [], color=BLUE, label="named kickoff"); a.plot([], [], color=ORANGE, label="free kickoff")
    a.set_xlabel("active hours from kickoff"); a.set_ylabel("domain-wall fraction dw (1-h mean)")
    a.set_xlim(0, 21.5); a.set_ylim(-0.03, 1.05); a.grid(color=GRID, lw=0.5); a.legend(frameon=False, fontsize=6, loc="lower left")
    a.set_title("(a) dw = (N_p-1)/(N_h-1) after each kickoff", fontsize=8, loc="left")
    b = ax[1]
    names = [f"G{g:02d}" for g in L.REPL] + ["G44best", "G44rest", "NE42_merge", "NE42_split"]
    names = [n for n in names if u[n].get("post_hoc")]
    order = sorted(names, key=lambda n: (u[n]["code"], u[n]["post_hoc"]["dw_slope_per_h"]))
    for i, n in enumerate(order):
        r = u[n]
        col = BLUE if r["code"] == "named" else ORANGE
        tf = r["dw"]["H"] if r["dw"]["t_f_censored"] else r["dw"]["t_f"]
        b.scatter(tf, i, color=col, s=16, zorder=3, edgecolor="white", lw=0.5,
                  marker="o" if not r["dw"]["t_f_censored"] else ">")
        b.text(21.2, i, f"{r['post_hoc']['dw_slope_per_h']:+.3f}", fontsize=5.5, va="center", color=INK)
    b.axvline(L.FREEZE_H, color=NULL, ls="--", lw=0.8)
    b.text(L.FREEZE_H + 0.2, len(order) - 0.3, "freeze (3 h)", fontsize=5.5, color=MUTED)
    b.set_yticks(range(len(order))); b.set_yticklabels([n.replace("_", " ") for n in order], fontsize=5.5)
    b.set_xlim(0, 24); b.set_xlabel("freeze time t_f on dw (h; > censored)")
    b.text(21.0, len(order) - 0.2, "slope/h", fontsize=5.5, color=MUTED)
    b.set_title("(b) freeze time and post hoc dw drift", fontsize=8, loc="left"); b.grid(axis="x", color=GRID, lw=0.5)
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs.pdf"); plt.close(fig)


def synth():
    s = json.loads((L.D / "synthetic/summary.json").read_text())["by_skeleton"]
    sks = [f"G{g:02d}" for g in L.REPL]
    worlds = ["Q0", "Q0w", "Q1", "Q2", "Q3"]
    lab = {"Q0": "Q0 coarsen\nβJ=4", "Q0w": "Q0w coarsen\nβJ=2", "Q1": "Q1 shared\nfield", "Q2": "Q2 own\nfields",
           "Q3": "Q3 finish\n(no merge)"}
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.3))
    for k, (obsn, title) in enumerate((("dw", "(a) primary dw: share classified freeze"),
                                       ("np", "(b) HH-literal N_p: share classified freeze"))):
        a = ax[k]
        for i, w in enumerate(worlds):
            v = np.array([s[x][w][f"{obsn}_freeze"] for x in sks])
            a.scatter(np.full(len(v), i) + np.linspace(-0.2, 0.2, len(v)), v, s=9, color=BLUE if w in ("Q1", "Q2", "Q3") else ORANGE,
                      edgecolor="white", lw=0.4, zorder=3)
            a.plot([i - 0.28, i + 0.28], [np.median(v)] * 2, color=INK, lw=1.2)
        a.axhline(0.8, color=NULL, ls="--", lw=0.8); a.axhline(0.3, color=NULL, ls=":", lw=0.8)
        a.set_xticks(range(len(worlds))); a.set_xticklabels([lab[w] for w in worlds], fontsize=5.8)
        a.set_ylim(-0.05, 1.05); a.set_ylabel("share of 60 runs"); a.set_title(title, fontsize=8, loc="left")
        a.grid(axis="y", color=GRID, lw=0.5)
    fig.tight_layout()
    fig.savefig(FIG / "summary_synth.pdf"); plt.close(fig)


if __name__ == "__main__":
    FIG.mkdir(exist_ok=True)
    obs(); synth()
    print("figures written")
