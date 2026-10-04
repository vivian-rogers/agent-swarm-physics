"""Two-panel observables figure for the H01 one-page summary (plots existing results only; no recomputation).

(a) P1: per-day room-vs-random semantic-entropy gap dH, by unit, with the locked -0.1 nats threshold.
(b) P6: per-unit exposure slope of the residual alignment, sorted, with the random-effects summary (needed p < 0.01).

Reads data/processed/H01-emergent-superagents-exist/explore.json (written by analysis/explore.py).
Usage: uv run python hypotheses/H01-emergent-superagents-exist/analysis/summary_figure.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
from h01common import OUT, FIG  # noqa: E402

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


def unit_order(u):
    m = re.match(r"(\d+)([a-z]?)", u)
    return (int(m.group(1)), m.group(2))


def main():
    ex = json.loads((OUT / "explore.json").read_text())
    fig, ax = plt.subplots(1, 2, figsize=FIGSIZE, gridspec_kw={"width_ratios": [1.5, 1]})

    # (a) P1 per-day dH by unit (primary units only; the card counts these)
    days = [d for d in ex["p1"]["days"] if "room" in d and d.get("primary")]
    units = sorted({d["unit"] for d in days}, key=unit_order)
    a = ax[0]
    for i, u in enumerate(units):
        dd = [d for d in days if d["unit"] == u]
        xs = i + np.linspace(-0.22, 0.22, len(dd)) if len(dd) > 1 else [i]
        for x, d in zip(xs, dd):
            sig = d["room"]["p"] < 0.05
            a.plot(x, d["room"]["dH"], "o", ms=1.9, color=C1 if sig else "#9a9993", mec="none", zorder=3)
        med = np.median([d["room"]["dH"] for d in dd])
        a.plot([i - 0.32, i + 0.32], [med, med], color=INK, lw=1.0, zorder=4)
    P1 = ex["p1"]["P1"]
    a.axhline(0, color=INK2, lw=0.6)
    a.axhline(-0.1, color=C2, lw=0.9, ls="--", zorder=2)
    a.text(-0.5, -0.108, "locked threshold", color=C2, fontsize=5, ha="left", va="top")
    a.text(0.02, 0.985, f"median {P1['median_dH']:.3f} nats; {P1['frac_dH_neg']*100:.0f}% of days < 0\n"
                        "dot = day (blue: p < 0.05), bar = median".replace("-0", "−0"), transform=a.transAxes, fontsize=4.9, color=INK2, va="top")
    a.set_xticks(range(len(units)))
    a.set_xticklabels(["#" + u for u in units], rotation=60, fontsize=5)
    a.set_xlim(-0.6, len(units) - 0.4)
    a.set_ylabel(r"$\Delta H$ rooms − random (nats)")
    a.set_title("(a) P1: room order", loc="left")
    a.set_ylim(-0.5, 0.16)

    # (b) P6: per-unit exposure slopes, sorted (caterpillar), with the random-effects summary
    per = ex["p56"]["per_unit"]
    us = sorted([u for u in per if "slope" in per[u]], key=lambda u: per[u]["slope"])
    b = ax[1]
    re_ = ex["p56"]["P6"]["re_slope"]
    b.axhspan(re_["mu"] - 1.96 * re_["se"], re_["mu"] + 1.96 * re_["se"], color=INK, alpha=0.12, lw=0)
    b.axhline(re_["mu"], color=INK, lw=0.9)
    b.axhline(0, color=INK2, lw=0.6)
    for i, u in enumerate(us):
        s_, se = per[u]["slope"], per[u]["slope_se"]
        b.errorbar(i, s_, yerr=1.96 * se, fmt="o", ms=1.9, color=C1, lw=0.6, capsize=0)
    b.set_xticks([]); b.set_xlim(-0.8, len(us) - 0.2)
    b.set_ylim(-0.22, 0.3)
    b.set_xlabel(f"{len(us)} units, sorted")
    b.set_ylabel("slope (residual cos per e-fold)")
    b.set_title("(b) P6: coupling", loc="left")
    b.text(0.03, 0.985, f"RE {re_['mu']:+.3f}, p = {re_['p_two']:.3f}\n(needed p < 0.01)", transform=b.transAxes,
           fontsize=4.9, color=INK, ha="left", va="top")
    b.grid(axis="x", visible=False)

    fig.tight_layout(pad=0.2, w_pad=0.6)
    fig.savefig(FIG / "summary_obs.pdf")
    plt.close(fig)
    print("wrote", FIG / "summary_obs.pdf")


if __name__ == "__main__":
    main()
