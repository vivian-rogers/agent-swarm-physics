"""Two-panel observables figure for the H04 one-page summary (plots existing results only; no recomputation).

(a) Exploratory (non-holdout, regime III): matched Green's function G(tau) of a nudge on the named target's activity,
    with the 95% day-block bootstrap band (explore_kernels.json, III / nudge_target_iso).
(b) Confirmatory (locked holdout, NE21): Hawkes branching ratio n per hours segment A1 (4 h), B1 (8 h), A2 (4 h),
    B2 (8 h), with day-bootstrap CIs, against the pre-registered direction (confirm_ne21_ne23.json).

Usage: uv run python hypotheses/H04-reversible-forcing/analysis/summary_figure.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h04lib import FIG, OUT, LAGS  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

C1, C2, INK, INK2, GRID = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#e4e3df"
FIGSIZE = (3.4, 1.7)  # one RevTeX column, printed 1:1 (the page caps the figure at 1.7 in tall)
plt.rcParams.update({"font.size": 5.8, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.4, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.titlesize": 6.3, "axes.titleweight": "bold", "pdf.fonttype": 42,
                     "xtick.labelsize": 5.4, "ytick.labelsize": 5.4, "axes.labelsize": 5.8, "axes.linewidth": 0.6,
                     "xtick.major.size": 2, "ytick.major.size": 2, "xtick.major.pad": 1.5, "ytick.major.pad": 1.5,
                     "axes.titlepad": 3, "axes.labelpad": 1.5})


def main():
    k = json.loads((OUT / "explore_kernels.json").read_text())
    c = json.loads((OUT / "confirm_ne21_ne23.json").read_text())
    g = k["III"]["G"]["nudge_target_iso"]
    G, lo, hi = (np.array(g[x], dtype=float) for x in ("G", "G_lo", "G_hi"))
    assert len(G) == len(LAGS)

    fig, ax = plt.subplots(1, 2, figsize=FIGSIZE, gridspec_kw={"width_ratios": [1.4, 1]})

    # (a) nudge -> target kernel
    a = ax[0]
    a.fill_between(LAGS, lo, hi, color=C2, alpha=0.18, lw=0)
    a.plot(LAGS, G, color=C2, lw=0.8)
    a.axhline(0, color=INK2, lw=0.7)
    a.axvline(0, color=INK, lw=0.7, ls=":")
    a.axvspan(1, 4, color="#9a9993", alpha=0.15, lw=0)
    a.text(2.5, 0.145, "1–4 min:\nno response", fontsize=4.9, color=INK2, ha="left", va="top")
    A30 = g["A30"]
    a.text(59, -0.085, f"A30 = {A30[0]:.2f} [{A30[1]:.2f}, {A30[2]:.2f}]\nextra active min per nudge",
           fontsize=4.9, color=INK, ha="right", va="bottom")
    a.set_xlim(-30, 60); a.set_ylim(-0.1, 0.16)
    a.set_xticks([-30, 0, 15, 30, 45, 60])
    a.set_xlabel("minutes after nudge")
    a.set_ylabel(r"$G(\tau)$ = Δ P(active)")
    a.set_title(f"(a) nudge → target ({g['n_kicks']} nudges)", loc="left")

    # (b) NE21 segment n
    b = ax[1]
    segs = ["A1", "B1", "A2", "B2"]
    hrs = {"A1": 4, "B1": 8, "A2": 4, "B2": 8}
    x = np.arange(len(segs))
    for xi, s in zip(x, segs):
        n, l, h = c["segments"][s]["hawkes"]["n_ci"]
        col = C1 if hrs[s] == 4 else C2
        b.errorbar(xi, n, yerr=[[n - l], [h - n]], fmt="o", color=col, ms=3.2, capsize=1.5, lw=0.8)
    nn = [c["segments"][s]["hawkes"]["n_ci"][0] for s in segs]
    b.plot(x, nn, color=INK2, lw=0.5, zorder=0)
    # predicted direction at each switch: 8 h below the neighbouring 4 h
    for xi in (1, 3):
        b.annotate("", xy=(xi + 0.18, nn[xi - 1] - 0.16), xytext=(xi + 0.18, nn[xi - 1]),
                   arrowprops=dict(arrowstyle="->", color=INK2, lw=0.7, ls="--"))
    b.text(1.28, nn[0] - 0.13, "predicted", fontsize=4.9, color=INK2, ha="left", va="center")
    b.set_xticks(x); b.set_xticklabels([f"{s}\n{hrs[s]} h" for s in segs])
    b.set_ylim(0, 1.08); b.set_xlim(-0.5, 3.6)
    b.set_ylabel(r"branching ratio $n$")
    D = c["verdicts"]["C1_reversal_of_n"]["ABAB_contrast"]; P = c["verdicts"]["C1_reversal_of_n"]["placebo_abs_p95"]
    b.set_title("(b) NE21 holdout", loc="left")
    b.text(0.03, 0.985, f"8 h higher at 3/3 switches\nABAB {D[0]:+.2f}; noise |p95| {P:.2f}".replace("-", "−"),
           transform=b.transAxes, fontsize=4.9, color=INK, ha="left", va="top")
    b.grid(axis="x", visible=False)

    fig.tight_layout(pad=0.2, w_pad=0.6)
    fig.subplots_adjust(left=fig.subplotpars.left + 0.02)
    fig.savefig(FIG / "summary_obs.pdf")
    plt.close(fig)
    print("wrote", FIG / "summary_obs.pdf")


if __name__ == "__main__":
    main()
