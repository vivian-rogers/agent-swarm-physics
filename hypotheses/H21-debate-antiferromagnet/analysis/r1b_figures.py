"""H21 round 1b page-2 figure: staggered order per debate in the stance channel (DQ2) vs the content channel (masked
text, two embedding models), and the re-drafting within-pair contrast.

Usage: uv run python hypotheses/H21-debate-antiferromagnet/analysis/r1b_figures.py -> figures/r1b_stance_vs_content.pdf
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
R1B = ROOT / "data/processed/H21-debate-antiferromagnet/r1b"
FIG = HERE.parent / "figures"
BLUE, ORANGE, AQUA, VIOLET = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7"
INK, INK2, GRID, NULL = "#0b0b0b", "#52514e", "#e4e3df", "#9b9a95"
plt.rcParams.update({"font.size": 7, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
                     "grid.linewidth": 0.5, "legend.frameon": False, "pdf.fonttype": 42, "axes.titlesize": 7.5})


def main():
    r = json.loads((R1B / "r1b.json").read_text())
    stance = {int(k): v for k, v in r["stance"]["S1_delta_soft"]["per_debate"].items()}
    cont = {}
    for m in ("bge_small", "gte_modernbert"):
        c = json.loads((R1B / f"content_{m}_masked_none.json").read_text())
        cont[m] = {int(d["debate"]): d["delta"] for d in c["static"]["per_debate"]}
    debs = sorted(set(stance) | set(cont["bge_small"]))
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.8, 2.05), gridspec_kw={"width_ratios": [1.7, 1]})
    x = np.arange(len(debs))
    for k, (lab, col, mk, d) in enumerate([("content, bge (masked)", NULL, "o", cont["bge_small"]),
                                            ("content, gte (masked)", VIOLET, "s", cont["gte_modernbert"]),
                                            ("stance (DQ2 replies)", ORANGE, "D", stance)]):
        y = np.array([d.get(q, np.nan) for q in debs])
        a.scatter(x + (k - 1) * 0.22, y, s=16, color=col, marker=mk, edgecolor="white", linewidth=0.6, zorder=3, label=lab)
    a.axhline(0, color=INK2, lw=0.6)
    a.set_xticks(x, [f"#{q}" for q in debs])
    a.set_xlabel("debate")
    a.set_ylabel("teammates − opponents")
    a.set_title("(a) staggered order per debate", loc="left")
    a.set_ylim(top=1.55)
    a.legend(loc="upper left", fontsize=5.8, handletextpad=0.2, ncol=3, columnspacing=0.8)
    pp = r["native_G12"]["stance_soft"]["per_pair"]
    cvals = np.array(list(pp.values()))
    b.hist(cvals, bins=np.linspace(-1.6, 1.0, 14), color=ORANGE, edgecolor="white", linewidth=0.6, label="stance")
    b.axvline(0, color=INK2, lw=0.6)
    b.axvline(np.mean(cvals), color=INK, lw=1.0, ls="--")
    b.text(np.mean(cvals), b.get_ylim()[1] * 0.92, f" mean {np.mean(cvals):+.2f}", fontsize=6, color=INK, ha="left")
    cb = r["native_G12"]["content_bge_small"]["mean_c"]
    b.set_xlabel("stance: opponents − teammates")
    b.set_ylabel("agent pairs")
    b.set_title("(b) same pair across re-drafts", loc="left")
    fig.tight_layout(pad=0.4)
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / "r1b_stance_vs_content.pdf")
    print("wrote", FIG / "r1b_stance_vs_content.pdf")


if __name__ == "__main__":
    main()
