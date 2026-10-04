"""H10 round 1b summary figure: figures/r1b_models.pdf.
(a) P1 r(Delta_i, kappa2_i^F) per primary pair under every round-1b input configuration (blue bge, orange gte; marker =
    variant). (b) G44 native: each room's push along its own room kickoff (and #rest along #best's), both models.
Usage: uv run python hypotheses/H10-goals-are-legendre-pushes/analysis/r1b_figures.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[2] / "data/processed/H10-goals-are-legendre-pushes"
COL = {"bge_small": "#2a78d6", "gte_modernbert": "#eb6834"}
VAR = {"shared": ("o", "base"), "shared_dd-restate": ("s", "deduped"), "shared_style": ("^", "style-resid")}


def main():
    plt.rcParams.update({"font.size": 7, "axes.spines.top": False, "axes.spines.right": False})
    fig, ax = plt.subplots(1, 2, figsize=(3.45, 2.0), gridspec_kw={"width_ratios": [1.15, 1]})
    pairs = ["11-12", "16-17", "37-38"]
    for m, c in COL.items():
        for v, (mk, lab) in VAR.items():
            f = DATA / "r1b" / f"{m}_{v}" / "NE34" / "pairs.json"
            if not f.exists():
                continue
            P = json.loads(f.read_text())["pairs"]
            off = (0.12 if m == "gte_modernbert" else -0.12) + {"o": -0.05, "s": 0.0, "^": 0.05}[mk]
            ax[0].scatter([i + off for i in range(3)], [P[k]["P1_r"] for k in pairs], s=14, marker=mk,
                          facecolor=c if mk == "o" else "white", edgecolor=c, lw=0.9, zorder=3,
                          label=f"{'bge' if m == 'bge_small' else 'gte'} {lab}")
    ax[0].axhline(0, color="#85847e", lw=0.6)
    ax[0].set_xticks(range(3), ["11→12", "16→17", "37→38"], fontsize=6)
    ax[0].set_ylabel("P1: r(Δᵢ, κ2ᵢ^F)")
    ax[0].set_ylim(-1, 1.45)
    ax[0].set_title("(a) P1: who moves", fontsize=7)
    ax[0].legend(fontsize=4.6, frameon=False, loc="upper left", ncol=2, handletextpad=0.1, columnspacing=0.4, borderaxespad=0.1)
    rows = [("best_along_best", "#best, own"), ("rest_along_rest", "#rest, own"), ("rest_along_best", "#rest, #best's")]
    for j, m in enumerate(COL):
        f = DATA / "r1b" / f"{m}_shared" / "natives.json"
        G = json.loads(f.read_text())["G44"]["kickoff_room"]
        for i, (k, _) in enumerate(rows):
            x = G[k]
            y = i + (0.15 if j else -0.15)
            ax[1].errorbar(x["Dbar"], y, xerr=[[x["Dbar"] - x["Dbar_ci90"][0]], [x["Dbar_ci90"][1] - x["Dbar"]]],
                           fmt="o", ms=3.5, color=COL[m], lw=1, capsize=0, label=("bge" if j == 0 else "gte") if i == 0 else None)
    ax[1].axvline(0, color="#85847e", lw=0.6)
    ax[1].set_yticks(range(3), [r[1] for r in rows])
    ax[1].invert_yaxis()
    ax[1].set_xlabel("push Δ̄ along kickoff")
    ax[1].set_title("(b) #44 rooms", fontsize=7)
    ax[1].legend(fontsize=5.5, frameon=False, loc="center right")
    fig.tight_layout(pad=0.3, w_pad=0.6)
    out = HERE.parent / "figures" / "r1b_models.pdf"
    fig.savefig(out)
    print(out)


if __name__ == "__main__":
    main()
