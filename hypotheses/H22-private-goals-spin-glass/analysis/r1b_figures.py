"""H22 round 1b page-2 figure: the rival contrast T_SR per unit in content (two models, style-residualized) and stance,
and the NE38 before/after for Claude Opus 5 and its former game-dev rivals.

Usage: uv run python hypotheses/H22-private-goals-spin-glass/analysis/r1b_figures.py -> figures/r1b_rivals_channels.pdf
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
R1B = ROOT / "data/processed/H22-private-goals-spin-glass/r1b"
FIG = HERE.parent / "figures"
BLUE, ORANGE, AQUA, VIOLET = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7"
INK, INK2, GRID, NULL = "#0b0b0b", "#52514e", "#e4e3df", "#9b9a95"
plt.rcParams.update({"font.size": 7, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
                     "grid.linewidth": 0.5, "legend.frameon": False, "pdf.fonttype": 42, "axes.titlesize": 7.5})
UNITS = ["51b", "51c", "51d", "pu51c", "pu51d", "pu51e", "pu51f", "pu51g", "pu51h"]


def main():
    S = json.loads((R1B / "summary.json").read_text())
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.8, 2.1), gridspec_kw={"width_ratios": [2.0, 1]})
    x = np.arange(len(UNITS))
    chans = [("content bge", NULL, "o", lambda u: S["r1b"]["bge_small_white32_none"].get(u)),
             ("content gte", VIOLET, "s", lambda u: S["r1b"]["gte_modernbert_white32_none"].get(u)),
             ("content bge, style-resid.", BLUE, "^", lambda u: S["r1b"]["bge_small_styp_none"].get(u)),
             ("stance (DQ2)", ORANGE, "D", lambda u: S["stance"].get(u))]
    for k, (lab, col, mk, get) in enumerate(chans):
        y, e = [], []
        for u in UNITS:
            d = get(u) or {}
            y.append(d.get("T_SR") if d.get("T_SR") is not None else np.nan)
            e.append(d.get("SR_null_sd") or np.nan)
        y, e = np.array(y, float), np.array(e, float)
        xx = x + (k - 1.5) * 0.18
        a.errorbar(xx, y, yerr=e, fmt="none", ecolor=col, elinewidth=0.6, alpha=0.6)
        a.scatter(xx, y, s=15, color=col, marker=mk, edgecolor="white", linewidth=0.5, zorder=3, label=lab)
    a.axhline(0, color=INK2, lw=0.6)
    a.axvline(2.5, color=GRID, lw=1.0)
    a.set_xticks(x, ["51b", "51c", "51d", "c", "d", "e*", "f", "g", "h"])
    a.text(1, a.get_ylim()[1] * 0.92, "H22 units", ha="center", fontsize=6, color=INK2)
    a.text(5.5, a.get_ylim()[1] * 0.92, "shared splits pu51· (* Opus 5 a game dev)", ha="center", fontsize=6, color=INK2)
    a.set_ylabel("T_SR = J(rivals) − J(unrelated)")
    a.set_title("(a) same-role rivals vs unrelated pairs (bars: role-permutation sd)", loc="left")
    a.legend(loc="lower left", fontsize=5.8, ncol=2, handletextpad=0.2, columnspacing=0.6)
    ne = S.get("native_NE38_min2", {}).get("bge_small", {})
    sa = ne.get("static_alignment", {})
    labels = ["alignment\nwith rivals", "coupling\nwith GPT-5.5"]
    pre = [sa.get("cos_rivals_pre", np.nan), ne.get("J_pre_rivals", {}).get("26", np.nan)]
    post = [sa.get("cos_rivals_post", np.nan), ne.get("J_post_rivals", {}).get("26", np.nan)]
    xb = np.arange(2)
    b.bar(xb - 0.2, pre, 0.38, color=ORANGE, label="as game dev", edgecolor="white", linewidth=0.5)
    b.bar(xb + 0.2, post, 0.38, color=BLUE, label="as mathematician", edgecolor="white", linewidth=0.5)
    b.axhline(0, color=INK2, lw=0.6)
    b.set_xticks(xb, labels)
    b.set_title("(b) NE38: Opus 5, rival vs not (bge)", loc="left")
    b.legend(loc="upper right", fontsize=5.8)
    fig.tight_layout(pad=0.4)
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / "r1b_rivals_channels.pdf")
    print("wrote", FIG / "r1b_rivals_channels.pdf")


if __name__ == "__main__":
    main()
