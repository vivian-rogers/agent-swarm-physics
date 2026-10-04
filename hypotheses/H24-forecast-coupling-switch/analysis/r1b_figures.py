"""H24 round 1b summary figure: figures/r1b_models.pdf.
(a) Residual-alignment step at switch-on per input configuration, with the within-week (N1) and kickoff-matched (N2)
    placebo q90 (blue bge, orange gte). (b) G41 native: within-room minus cross-room alignment by day, both models,
    with the room-permutation q95.
Usage: uv run python hypotheses/H24-forecast-coupling-switch/analysis/r1b_figures.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
D = HERE.parents[2] / "data/processed/H24-forecast-coupling-switch"
COL = {"bge_small": "#2a78d6", "gte_modernbert": "#eb6834"}
VARS = [("shared_1d", "base"), ("shared_multi", "multi-dir"), ("shared_1d_dd-restate", "deduped"),
        ("shared_1d_dd-echo", "no echo"), ("shared_1d_style", "style")]


def main():
    plt.rcParams.update({"font.size": 7, "axes.spines.top": False, "axes.spines.right": False})
    fig, ax = plt.subplots(1, 2, figsize=(3.45, 2.0), gridspec_kw={"width_ratios": [1.25, 1]})
    rep = {r["tag"]: r for r in json.loads((D / "G21" / "r1b" / "report.json").read_text())}
    for j, (m, c) in enumerate(COL.items()):
        for i, (v, lab) in enumerate(VARS):
            r = rep[f"{m}_{v}"]
            y = i + (0.17 if j else -0.17)
            ax[0].errorbar(r["dA_res"], y, xerr=[[r["dA_res"] - r["dA_ci90"][0]], [r["dA_ci90"][1] - r["dA_res"]]], fmt="o",
                           ms=3, color=c, lw=0.9, label=("bge" if j == 0 else "gte") if i == 0 else None)
            ax[0].plot([r["N1_q90"]], [y], "|", color=c, ms=5, mew=1)
            ax[0].plot([r["N2_q90"]], [y], "x", color=c, ms=3.5, mew=0.9)
    ax[0].axvline(0, color="#85847e", lw=0.6)
    ax[0].set_yticks(range(len(VARS)), [v[1] for v in VARS])
    ax[0].invert_yaxis()
    ax[0].set_xlabel("ΔA_res (| N1, × N2 q90)")
    ax[0].set_title("(a) #21 step at τᵢ", fontsize=7)
    for m, c in COL.items():
        w = json.loads((D / "G41" / "r1b" / f"native_{m}.json").read_text())
        xs = list(range(1, len(w["days"]) + 1))
        ax[1].plot(xs, [b["dW"] for b in w["days"]], "o-", color=c, ms=3, lw=1.2, label="bge" if m == "bge_small" else "gte")
        ax[1].plot(xs, [b["null_q95"] for b in w["days"]], ":", color=c, lw=0.9)
    ax[1].axhline(0, color="#85847e", lw=0.6)
    ax[1].set_xlabel("day of #41")
    ax[1].set_ylabel("within − cross room")
    ax[1].set_title("(b) #41 room gap", fontsize=7)
    ax[1].legend(fontsize=5.5, frameon=False, loc="upper left")
    fig.tight_layout(pad=0.3, w_pad=0.6)
    out = HERE.parent / "figures" / "r1b_models.pdf"
    fig.savefig(out)
    print(out)


if __name__ == "__main__":
    main()
