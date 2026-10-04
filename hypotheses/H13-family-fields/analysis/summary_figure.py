"""H13 summary-page figure (figures/summary_obs.pdf): reads round-1 outputs only (explore.json), recomputes nothing.

(a) family-field statistic T_field per unit, raw vs style-residualized (S-a), with the random-effects summaries;
(b) two-room units: permutation z of the same-lab vs same-room pair coefficients for talk timing, content
    co-movement and the static content field.

Usage: uv run python hypotheses/H13-family-fields/analysis/summary_figure.py
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
DATA = ROOT / "data/processed/H13-family-fields"
FIG = HERE.parent / "figures"
C1, C2 = "#2a78d6", "#eb6834"  # validated reference slots 1-2 (same as analysis/figures.py)
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({"font.size": 7, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "axes.titlesize": 7.2,
                     "axes.titleweight": "bold", "legend.frameon": False, "pdf.fonttype": 42})


def main():
    ex = json.loads((DATA / "explore.json").read_text())
    U, M = ex["units"], ex["meta"]
    units = list(U)
    fig, (a, b) = plt.subplots(1, 2, figsize=(4.3, 2.6), gridspec_kw={"width_ratios": [1.35, 1]})

    # (a) T_field raw vs style-residualized
    x = np.arange(len(units))
    for off, key, col, mk, lab in ((-0.17, "a1", C1, "o", "raw"), (0.17, "a2", C2, "s", "style-residualized")):
        v = np.array([U[u][key]["obs"] for u in units])
        p = np.array([U[u][key]["p"] for u in units])
        a.scatter(x[p < 0.05] + off, v[p < 0.05], color=col, marker=mk, s=14, zorder=3, label=f"{lab} (filled: p < 0.05)")
        a.scatter(x[p >= 0.05] + off, v[p >= 0.05], facecolor="white", edgecolor=col, marker=mk, s=14, linewidth=0.9, zorder=3)
    xr = len(units) + 0.8
    for off, key, col, mk in ((-0.17, "T_field", C1, "o"), (0.17, "T_field_style", C2, "s")):
        m = M[key]
        a.errorbar([xr + off], [m["mu"]], yerr=[[m["mu"] - m["lo"]], [m["hi"] - m["mu"]]], fmt=mk, color=col, ms=4,
                   elinewidth=1.2, capsize=1.5, zorder=3)
    a.axvline(len(units) + 0.1, color=GRID, lw=0.8)
    a.axhline(0, color=INK2, lw=0.6)
    a.set_xticks(list(x) + [xr], units + ["RE"], rotation=90, fontsize=5.2)
    a.set_xlim(-0.7, xr + 0.7)
    a.set_ylabel("T_field: same-lab − cross-lab cos")
    a.yaxis.grid(True, color=GRID, lw=0.5)
    a.set_axisbelow(True)
    a.set_title("a  Family field = writing style", loc="left")
    a.legend(loc="upper right", fontsize=5.2, handletextpad=0.2, borderaxespad=0.1)
    a.set_ylim(-0.25, 0.55)

    # (b) family vs room in two-room units
    outs = [("y1_talk", "talk\ntiming"), ("y3_comove", "content\nco-movement"), ("y2_field", "content\nfield")]
    tr = [u for u in units if "c" in U[u]]
    for k, (y, nm) in enumerate(outs):
        zl = [U[u]["c"][y]["b_lab"] / U[u]["c"][y]["null_sd_lab"] for u in tr if y in U[u]["c"]]
        zr = [U[u]["c"][y]["b_room"] / U[u]["c"][y]["null_sd_room"] for u in tr if y in U[u]["c"]]
        jit = np.linspace(-0.09, 0.09, len(zl))
        b.scatter(k - 0.18 + jit, zl, color=C1, marker="o", s=9, label="same lab" if k == 0 else None, zorder=3)
        b.scatter(k + 0.18 + jit, zr, color=C2, marker="s", s=9, label="same room" if k == 0 else None, zorder=3)
    b.axhline(1.64, color=INK2, lw=0.6, ls="--")
    b.axhline(0, color=INK2, lw=0.5)
    b.text(-0.47, 1.45, "p = 0.05", fontsize=4.8, color=INK2, ha="left", va="top")
    b.set_xticks(range(len(outs)), [n for _, n in outs], fontsize=5.8)
    b.set_xlim(-0.5, 2.55)
    b.set_ylabel("permutation z (per two-room unit)")
    b.yaxis.grid(True, color=GRID, lw=0.5)
    b.set_axisbelow(True)
    b.set_title("b  Room beats lab", loc="left")
    b.legend(loc="upper left", fontsize=5.4, handletextpad=0.2, borderaxespad=0.1)
    fig.tight_layout(pad=0.3, w_pad=0.8)
    fig.savefig(FIG / "summary_obs.pdf")
    fig.savefig(FIG / "summary_obs.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    main()
