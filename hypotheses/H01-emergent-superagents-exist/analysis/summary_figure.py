"""Two-panel observables figure for the H01 one-page summary (plots existing results only; no recomputation).

(a) P1: per-day room-vs-random semantic-entropy gap dH, by unit, with the locked -0.1 nats threshold.
(b) P6: per-unit exposure slope of the residual alignment with the random-effects summary (needed p < 0.01).

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
plt.rcParams.update({"font.size": 7, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.titlesize": 7.5, "axes.titleweight": "bold", "pdf.fonttype": 42,
                     "xtick.labelsize": 6.5, "ytick.labelsize": 6.5, "axes.labelsize": 7})


def unit_order(u):
    m = re.match(r"(\d+)([a-z]?)", u)
    return (int(m.group(1)), m.group(2))


def main():
    ex = json.loads((OUT / "explore.json").read_text())
    fig, ax = plt.subplots(1, 2, figsize=(4.3, 2.6), gridspec_kw={"width_ratios": [1.45, 1]})

    # (a) P1 per-day dH by unit (primary units only; the card counts these)
    days = [d for d in ex["p1"]["days"] if "room" in d and d.get("primary")]
    units = sorted({d["unit"] for d in days}, key=unit_order)
    a = ax[0]
    for i, u in enumerate(units):
        dd = [d for d in days if d["unit"] == u]
        xs = i + np.linspace(-0.22, 0.22, len(dd)) if len(dd) > 1 else [i]
        for x, d in zip(xs, dd):
            sig = d["room"]["p"] < 0.05
            a.plot(x, d["room"]["dH"], "o", ms=2.6, color=C1 if sig else "#9a9993", mec="none", zorder=3)
        med = np.median([d["room"]["dH"] for d in dd])
        a.plot([i - 0.32, i + 0.32], [med, med], color=INK, lw=1.2, zorder=4)
    P1 = ex["p1"]["P1"]
    a.axhline(0, color=INK2, lw=0.7)
    a.axhline(-0.1, color=C2, lw=1, ls="--", zorder=2)
    a.text(-0.5, -0.106, "locked threshold", color=C2, fontsize=5.8, ha="left", va="top")
    a.text(0.02, 0.985, f"all days: median {P1['median_dH']:.3f}, {P1['frac_dH_neg']*100:.0f}% below 0\n"
                        "dot = day (blue: p < 0.05); bar = unit median", transform=a.transAxes, fontsize=5.6, color=INK2, va="top")
    a.set_xticks(range(len(units)))
    a.set_xticklabels(["#" + u for u in units], rotation=60, fontsize=6)
    a.set_xlim(-0.6, len(units) - 0.4)
    a.set_ylabel(r"$\Delta H$ = H(rooms) − H(random), nats")
    a.set_title("(a) P1: room order", loc="left")
    a.set_ylim(-0.5, 0.13)

    # (b) P6 forest
    per = ex["p56"]["per_unit"]
    us = sorted([u for u in per if "slope" in per[u]], key=unit_order)
    b = ax[1]
    y = np.arange(len(us))[::-1] + 1.4
    for yy, u in zip(y, us):
        s, se = per[u]["slope"], per[u]["slope_se"]
        b.errorbar(s, yy, xerr=1.96 * se, fmt="o", ms=2.4, color=C1, lw=0.8, capsize=0)
    re_ = ex["p56"]["P6"]["re_slope"]
    b.errorbar(re_["mu"], 0, xerr=1.96 * re_["se"], fmt="D", ms=4, color=INK, lw=1.2, capsize=2)
    b.axvline(0, color=INK2, lw=0.7)
    b.set_yticks(list(y) + [0])
    b.set_yticklabels(["#" + u for u in us] + ["RE"], fontsize=5.6)
    b.set_xlim(-0.22, 0.3)
    b.set_ylim(-0.9, y.max() + 0.7)
    b.set_xlabel("residual cos per e-fold of exposure", fontsize=6.3)
    b.set_title("(b) P6: exposure slope", loc="left")
    b.text(0.06, 0, f"p = {re_['p_two']:.3f}\n(needed < 0.01)", fontsize=5.6, color=INK, ha="left", va="center")
    b.grid(axis="y", visible=False)

    fig.tight_layout(pad=0.3, w_pad=0.8)
    for ext in ("pdf",):
        fig.savefig(FIG / f"summary_obs.{ext}")
    plt.close(fig)
    print("wrote", FIG / "summary_obs.pdf")


if __name__ == "__main__":
    main()
