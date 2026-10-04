"""H14 one-page-summary figure (figures/summary_obs.pdf, ~4.3 x 2.6 in), from the round-1 period results.

(a) Share of agents with a detectable arrow of time (Newton bound above the detailed-balance surrogate, p < 0.05),
    fine action classes vs. the 6 coarse states, per goal period (G27 = regime I).
(b) Median excess irreversibility per transition (log scale): fine classes, coarse states, coarse states with the
    consolidation boundary removed.
Palette: reference categorical slots 1-3 (validated all-pairs; aqua has a contrast WARN, so every series also has its
own marker and a direct label).

Usage: uv run python hypotheses/H14-behavior-entropy-production/analysis/summary_figure.py
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
DATA = ROOT / "data/processed/H14-behavior-entropy-production"
OUT = HERE.parent / "figures" / "summary_obs.pdf"
PERIODS = ["G27", "G37", "G38", "G39", "G40", "G41", "G42", "G44", "G51"]
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"


def main():
    R = {g: json.loads((DATA / g / "results.json").read_text()) for g in PERIODS}
    x = np.array([0] + list(range(2, 2 + len(PERIODS) - 1)))      # gap between regime I and regime III
    plt.rcParams.update({"font.family": "serif", "font.size": 6.5, "axes.linewidth": 0.5, "pdf.fonttype": 42,
                         "axes.edgecolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "axes.labelcolor": INK})
    fig, (a, b) = plt.subplots(1, 2, figsize=(4.3, 2.6), gridspec_kw={"wspace": 0.42})
    labels = [g + ("\nreg I" if g == "G27" else "") for g in PERIODS]

    fine = [R[g]["act_frac_above_null"] for g in PERIODS]
    coarse = [R[g]["P2_frac_above_null_newton"] for g in PERIODS]
    a.axhspan(0, 0.05, color=GRID, lw=0)
    a.axhline(0.8, color=INK2, lw=0.5, ls=(0, (3, 2)))
    a.text(10.3, 0.81, "predicted", fontsize=5, color=INK2, ha="right", va="bottom")
    a.text(10.3, 0.055, "chance", fontsize=5, color=INK2, ha="right", va="bottom")
    for xs, ys, st, col, ms, dx in ((x, fine, "o", BLUE, 4, -0.22), (x, coarse, "s", ORANGE, 3.6, 0.22)):
        a.plot(xs[:1] + dx, ys[:1], st, color=col, ms=ms, mec="white", mew=0.6)       # regime I: no line across the gap
        a.plot(xs[1:], ys[1:], "-" + st, color=col, lw=1.2, ms=ms, mec="white", mew=0.6)
    a.text(x[-1] + 0.25, fine[-1], "fine", color=INK, fontsize=5.5, va="center")
    a.text(x[-1] + 0.25, coarse[-1] - 0.06, "coarse", color=INK, fontsize=5.5, va="center")
    a.set_xticks(x); a.set_xticklabels(labels, fontsize=5.2, rotation=90)
    a.set_ylim(0, 1.04); a.set_xlim(-0.6, x[-1] + 1.6)
    a.set_ylabel("share of agents with an arrow\n(above detailed-balance null)")
    a.set_title("(a) who has an arrow of time", fontsize=6.8, loc="left", color=INK)
    a.grid(axis="y", color=GRID, lw=0.4); a.set_axisbelow(True)
    for s in ("top", "right"):
        a.spines[s].set_visible(False)

    f2 = [R[g]["median_act_newton_exc"] for g in PERIODS]
    c2 = [R[g]["median_newton_exc"] for g in PERIODS]
    n2 = [max(R[g]["median_nocons_newton_exc"], 1e-5) for g in PERIODS]
    for ys, st, col, ms, lab in ((f2, "o", BLUE, 4, "fine action classes"), (c2, "s", ORANGE, 3.6, "6 coarse states"),
                                 (n2, "^", AQUA, 4, "coarse, consolidate removed")):
        b.plot(x[:1], ys[:1], st, color=col, ms=ms, mec="white", mew=0.6)
        b.plot(x[1:], ys[1:], "-" + st, color=col, lw=1.2, ms=ms, mec="white", mew=0.6, label=lab)
    b.set_yscale("log"); b.set_ylim(2e-5, 0.4)
    b.text(x[-1] + 0.25, f2[-1], "fine", color=INK, fontsize=5.5, va="center")
    b.text(x[-1] + 0.25, c2[-1] * 1.3, "coarse", color=INK, fontsize=5.5, va="center")
    b.text(x[-1] + 0.25, n2[-1] * 0.6, "no\nconsol.", color=INK, fontsize=5.5, va="center")
    b.set_xticks(x); b.set_xticklabels(labels, fontsize=5.2, rotation=90)
    b.set_xlim(-0.6, x[-1] + 1.9)
    b.set_ylabel("median excess Σ$_i$ (nats per transition)")
    b.set_title("(b) how strong, and whose", fontsize=6.8, loc="left", color=INK)
    b.grid(axis="y", color=GRID, lw=0.4, which="major"); b.set_axisbelow(True)
    for s in ("top", "right"):
        b.spines[s].set_visible(False)
    b.legend(frameon=False, fontsize=5, loc="lower left", handlelength=1.6, borderaxespad=0.2)
    fig.subplots_adjust(left=0.12, right=0.98, bottom=0.2, top=0.9)
    fig.savefig(OUT)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
