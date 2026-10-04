"""H13 round 1b page-2 figure: family field per unit in three channels (raw words, style-free words, behavior) and the
room-adjusted family term in behavior vs style-free words (two-room units).

Usage: uv run python hypotheses/H13-family-fields/analysis/r1b_figures.py  ->  figures/r1b_behavior_vs_words.pdf
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
R1B = ROOT / "data/processed/H13-family-fields/r1b"
FIG = HERE.parent / "figures"
BLUE, ORANGE, AQUA, VIOLET = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7"
INK, INK2, GRID, NULL = "#0b0b0b", "#52514e", "#e4e3df", "#9b9a95"
plt.rcParams.update({"font.size": 7, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
                     "grid.linewidth": 0.5, "legend.frameon": False, "pdf.fonttype": 42, "axes.titlesize": 7.5})
UNITS = ["35", "36b", "37", "38a", "38b", "38c", "39", "40", "41", "42", "44", "51a", "51b", "51c", "51d"]
TWO = ["35", "36b", "37", "38a", "38b", "38c", "39", "41", "42", "44"]


def main():
    beh = json.loads((R1B / "behavior.json").read_text())
    raw = {u: json.loads((R1B / "bge_small_none" / g / f"results_u{u}.json").read_text())
           for u, g in [(u, "G" + u[:2]) for u in UNITS]}
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.8, 2.05), gridspec_kw={"width_ratios": [2.1, 1]})
    x = np.arange(len(UNITS))
    series = [("words (raw, bge)", NULL, "o", lambda u: (raw[u]["a1"]["obs"], raw[u]["a1"]["p"])),
              ("style-free words (DQ5, bge)", BLUE, "s", lambda u: (beh["units"][u]["B"]["field_styp_bge"]["obs"], beh["units"][u]["B"]["field_styp_bge"]["p"])),
              ("behavior (Jev v3 + rates)", ORANGE, "D", lambda u: (beh["units"][u]["B"]["field"]["obs"], beh["units"][u]["B"]["field"]["p"]))]
    for k, (lab, col, mk, f) in enumerate(series):
        v = np.array([f(u) for u in UNITS], float)
        off = (k - 1) * 0.22
        sig = v[:, 1] < 0.05
        a.scatter(x[sig] + off, v[sig, 0], s=16, color=col, marker=mk, edgecolor="white", linewidth=0.6, zorder=3, label=lab)
        a.scatter(x[~sig] + off, v[~sig, 0], s=16, facecolor="white", edgecolor=col, marker=mk, linewidth=0.9, zorder=3)
    a.axhline(0, color=INK2, lw=0.6)
    a.set_xticks(x, UNITS, rotation=60)
    a.set_ylabel("family field T (within − across cos)")
    a.set_title("(a) family field per unit (filled: lab-permutation p < 0.05)", loc="left")
    a.legend(loc="upper right", fontsize=6, handletextpad=0.2)
    yb = np.array([beh["units"][u]["B"]["famroom"]["b_lab"] for u in TWO])
    pb = np.array([beh["units"][u]["B"]["famroom"]["p_lab"] for u in TWO])
    yw = np.array([beh["units"][u]["B"].get("famroom_styp_bge", {}).get("b_lab", np.nan) for u in TWO])
    pw = np.array([beh["units"][u]["B"].get("famroom_styp_bge", {}).get("p_lab", 1) for u in TWO])
    xx = np.arange(len(TWO))
    b.bar(xx - 0.2, yw, 0.38, color=BLUE, label="style-free words", edgecolor="white", linewidth=0.5)
    b.bar(xx + 0.2, yb, 0.38, color=ORANGE, label="behavior", edgecolor="white", linewidth=0.5)
    for xi, (vb, p_) in enumerate(zip(yb, pb)):
        if p_ < 0.05:
            b.text(xi + 0.2, vb + 0.01 * np.sign(vb if vb != 0 else 1), "*", ha="center", va="bottom", fontsize=8, color=INK)
    for xi, (vw, p_) in enumerate(zip(yw, pw)):
        if p_ < 0.05:
            b.text(xi - 0.2, vw + 0.01, "*", ha="center", va="bottom", fontsize=8, color=INK)
    b.axhline(0, color=INK2, lw=0.6)
    b.set_xticks(xx, TWO, rotation=60)
    b.set_ylabel("same-lab coefficient b_lab")
    b.set_title("(b) family term with room held fixed", loc="left")
    b.legend(loc="upper left", fontsize=6)
    fig.tight_layout(pad=0.4)
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / "r1b_behavior_vs_words.pdf")
    print("wrote", FIG / "r1b_behavior_vs_words.pdf")


if __name__ == "__main__":
    main()
