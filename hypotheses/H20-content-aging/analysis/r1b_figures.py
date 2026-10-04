"""H20 round 1b summary figure: figures/r1b_models.pdf.
(a) Aging slope A per long / medium period, bge vs gte (Amendment-2 null; marker = base vs style-residualized).
(b) #38 lag-1 two-time correlation C(t_w, t_w + 1) by t_w, both models (base and style-residualized).
Usage: uv run python hypotheses/H20-content-aging/analysis/r1b_figures.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[2] / "data/processed/H20-content-aging"
COL = {"bge_small": "#2a78d6", "gte_modernbert": "#eb6834"}
LM = [4, 8, 38, 51, 6, 13, 18, 19, 20, 27]


def main():
    plt.rcParams.update({"font.size": 7, "axes.spines.top": False, "axes.spines.right": False})
    fig, ax = plt.subplots(1, 2, figsize=(3.45, 2.0), gridspec_kw={"width_ratios": [1.2, 1]})
    for m, c in COL.items():
        for sfx, mk in (("", "o"), ("_style", "^")):
            S = json.loads((DATA / "r1b" / f"summary_{m}{sfx}.json").read_text())["aniso"]
            rows = {r["g"]: r for r in S["rows"]}
            off = (0.15 if m == "gte_modernbert" else -0.15) + (0.06 if sfx else -0.06)
            ax[0].scatter([i + off for i in range(len(LM))], [rows[g]["A"] for g in LM], s=12, marker=mk,
                          facecolor=c if not sfx else "white", edgecolor=c, lw=0.9, zorder=3,
                          label=f"{'bge' if m == 'bge_small' else 'gte'}{' style-resid' if sfx else ''}")
    ax[0].axhline(0, color="#85847e", lw=0.6)
    ax[0].set_xticks(range(len(LM)), [f"#{g}" for g in LM], rotation=90)
    ax[0].set_ylabel("A (C per e-fold of t_w)")
    ax[0].set_ylim(-0.25, 0.22)
    ax[0].set_title("(a) aging slope", fontsize=7)
    ax[0].legend(fontsize=4.6, frameon=False, loc="upper right", ncol=2, handletextpad=0.1, columnspacing=0.4, borderaxespad=0.1)
    for m, c in COL.items():
        for sfx, ls in (("", "-"), ("_style", "--")):
            C = np.load(DATA / "G38" / "r1b" / f"matrices_{m}{sfx}.npz")["C"]
            T = C.shape[0]
            ax[1].plot(range(1, T), [C[k, k + 1] for k in range(T - 1)], ls, color=c, lw=1.2 if not sfx else 0.9,
                       marker="o" if not sfx else None, ms=2.5)
    ax[1].axvspan(1, 5, color="#ecebe6", zorder=0)
    ax[1].set_xlabel("t_w (active day)")
    ax[1].set_ylabel("C(t_w, t_w + 1)")
    ax[1].set_title("(b) #38 lag-1 C", fontsize=7)
    fig.tight_layout(pad=0.3, w_pad=0.6)
    out = HERE.parent / "figures" / "r1b_models.pdf"
    fig.savefig(out)
    print(out)


if __name__ == "__main__":
    main()
