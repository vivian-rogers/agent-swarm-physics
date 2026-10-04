"""H03 round-1b page-2 figure (figures/summary_obs2.pdf): reads round-1 and round-1b outputs only.

(a) Per-period n-hat (M1_B2) in round 1 vs round 1b (corrected exogenous drive, days split at operator-off gaps),
    TALK and ALL; labelled points moved by more than 0.1.
(b) NE43 inside #51 at a fixed roster: n-hat per side (bookends + nudges / nudges only / no drive) +- 2 day-bootstrap SD.
Usage: uv run python hypotheses/H03-self-excited-criticality/analysis/summary_figure_r1b.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[2] / "data/processed/H03-self-excited-criticality"
FIG = HERE.parent / "figures"
COL = {"TALK": "#2a78d6", "ALL": "#eb6834"}
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({"font.size": 7, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "axes.titlesize": 7.2,
                     "axes.titleweight": "bold", "legend.frameon": False, "pdf.fonttype": 42})


def main():
    t1 = pl.read_parquet(DATA / "period_table.parquet").select("goal_no", "set", "n")
    tb = pl.read_parquet(DATA / "r1b/period_table.parquet").select("goal_no", "set", pl.col("n").alias("nb"))
    d = t1.join(tb, on=["goal_no", "set"])
    fig, (a, b) = plt.subplots(1, 2, figsize=(4.3, 2.05), gridspec_kw={"width_ratios": [1, 1.1]})
    a.plot([0, 0.85], [0, 0.85], color=INK2, lw=0.6, ls="--", zorder=1)
    for s in ("TALK", "ALL"):
        x = d.filter(pl.col("set") == s)
        a.scatter(x["n"], x["nb"], s=11, color=COL[s], label=s, edgecolor="white", lw=0.3, zorder=3)
        for r in x.filter((pl.col("nb") - pl.col("n")).abs() > 0.1).iter_rows(named=True):
            a.annotate(f"#{r['goal_no']}", (r["n"], r["nb"]), xytext=(3, -6), textcoords="offset points", fontsize=5.5, color=INK2)
    a.set_xlabel("n̂ round 1")
    a.set_ylabel("n̂ round 1b")
    a.set_xlim(-0.02, 0.85); a.set_ylim(-0.02, 0.85)
    a.grid(True, color=GRID, lw=0.5)
    a.set_axisbelow(True)
    a.set_title("a  Corrected inputs, 35 periods", loc="left")
    a.legend(loc="upper left", fontsize=5.6)

    N = json.loads((DATA / "r1b/native.json").read_text())["NE43"]
    sides = [("A_bookends+nudges", "A: bookends\n+ nudges"), ("B_nudges_only", "B: nudges\nonly"), ("C_no_drive", "C: no drive")]
    for k, s in enumerate(("TALK", "ALL")):
        xs = np.arange(3) + (k - 0.5) * 0.22
        y = [N[f"{lab}|{s}"]["n"] for lab, _ in sides]
        e = [2 * N[f"{lab}|{s}"]["n_boot_sd"] for lab, _ in sides]
        b.errorbar(xs, y, yerr=e, fmt="o", ms=4, color=COL[s], capsize=1.5, lw=1.0, label=s)
    b.set_xticks(range(3)); b.set_xticklabels([l for _, l in sides], fontsize=5.8)
    b.set_ylabel("n̂ (± 2 SD)")
    b.set_ylim(0, 0.85)
    b.yaxis.grid(True, color=GRID, lw=0.5)
    b.set_axisbelow(True)
    b.set_title("b  NE43: drive withdrawn (#51)", loc="left")
    b.legend(loc="upper left", fontsize=5.6, ncol=2)
    fig.tight_layout(pad=0.4, w_pad=1.0)
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / "summary_obs2.pdf")
    fig.savefig(FIG / "summary_obs2.png", dpi=200)


if __name__ == "__main__":
    main()
