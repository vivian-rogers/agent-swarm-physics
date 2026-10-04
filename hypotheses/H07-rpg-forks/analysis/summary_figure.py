"""Two-panel observables figure for the H07 one-page summary (no new analysis).

Reads data/processed/H07-rpg-forks/{curves_commit,horizontal_day}.parquet (exploratory, non-holdout) and writes
figures/summary_obs.pdf:
  (a) vertical inheritance: share of ancestor keys still identical vs. active hours since the split, for code
      (src/*.js files) and content (numeric parameters), in both forks;
  (b) horizontal copy information I_copy(best; rest) minus its shuffle null, relative to T0, per day: decay through
      #35, then a freeze (numbers move again in #37 when one fork grew).
Usage: uv run python hypotheses/H07-rpg-forks/analysis/summary_figure.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h07lib import P, T35_END  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "figures/summary_obs.pdf"
COL = {"best": "#2a78d6", "rest": "#eb6834"}
FCOL = {"files": "#52514e", "names": "#1baf7a", "numbers_data": "#4a3aa7"}
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({"font.size": 7, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5})


def main():
    fig, (a, b) = plt.subplots(1, 2, figsize=(4.3, 2.6))

    # (a) vertical copy fraction vs. active hours
    cc = pl.read_parquet(P / "curves_commit.parquet")
    end35 = cc.filter(pl.col("t") <= T35_END)["active_h"].max()
    for lin in ("best", "rest"):
        g = cc.filter(pl.col("lineage") == lin).sort("k")
        x = np.concatenate([[0], g["active_h"].to_numpy()])
        for f, ls in (("files_src", "-"), ("numbers_data", "--")):
            y = np.concatenate([[1], g[f"{f}_c"].to_numpy()])
            a.step(x, y, where="post", color=COL[lin], lw=1.4, ls=ls)
    a.axvline(end35, color=INK2, lw=0.7, ls=":")
    a.text(end35 + 1.5, 0.95, "end of #35", fontsize=5.8, color=INK2)
    a.set_xlim(0, 70)
    a.set_ylim(0.5, 1.02)
    a.set_xlabel("active hours since the split", fontsize=6.5)
    a.set_ylabel("share of ancestor keys identical", fontsize=6.5)
    a.text(66, 0.915, "numbers (dashed)", ha="right", fontsize=5.8, color=INK2)
    a.text(66, 0.613, "src files (solid)", ha="right", fontsize=5.8, color=INK2)
    a.plot([], [], color=COL["best"], lw=1.4, ls="-", label="#best (3 agents)")
    a.plot([], [], color=COL["rest"], lw=1.4, ls="-", label="#rest (10 agents)")
    a.legend(fontsize=5.8, frameon=False, loc="center left", bbox_to_anchor=(0.36, 0.5), handlelength=1.2)
    a.set_title("(a) Vertical: code drifts gradually,\ncontent jumps (in #best only)", fontsize=6.8, loc="left",
                color=INK)

    # (b) horizontal copy information, relative to T0
    hd = pl.read_parquet(P / "horizontal_day.parquet")
    t0 = hd.filter(pl.col("pt_date") == "T0")
    d = hd.filter(pl.col("pt_date") != "T0").filter(pl.col("pt_date") <= "2026-04-10")
    days = ["T0"] + d["pt_date"].to_list()
    x = np.arange(len(days))
    for f, lab in (("names", "names"), ("numbers_data", "numbers"), ("files", "files")):
        v0 = t0[f"{f}_I_copy_ex"][0]
        v = np.concatenate([[v0], d[f"{f}_I_copy_ex"].to_numpy()]) / v0
        b.plot(x, v, color=FCOL[f], lw=1.3, marker="o", ms=1.8)
        b.text(x[-1] + 0.6, v[-1], lab, fontsize=5.8, color=INK, va="center")
    b.axvline(5.5, color=INK2, lw=0.7, ls=":")
    i37 = days.index("2026-03-31") if "2026-03-31" in days else None
    if i37 is not None:
        b.annotate("#37: one agent\nreturns to #best", xy=(i37, 0.70), xytext=(i37 - 9, 0.58), fontsize=5.6,
                   color=INK2, arrowprops=dict(arrowstyle="-", color=INK2, lw=0.6))
    ticks = [0, 5] + ([i37] if i37 else [])
    b.set_xticks(ticks)
    b.set_xticklabels(["T0\n03-16", "03-20", "03-31"][:len(ticks)], fontsize=6)
    b.set_xlim(-0.5, len(days) + 4)
    b.set_ylim(0.45, 1.03)
    b.set_ylabel("I_copy(#best; #rest) − null, rel. to T0", fontsize=6.5)
    b.set_xlabel("calendar day (PT)", fontsize=6.5)
    b.set_title("(b) Horizontal: decays through #35,\nthen freezes (P4)", fontsize=6.8, loc="left", color=INK)

    for ax in (a, b):
        ax.tick_params(axis="both", length=2, labelsize=6)
    fig.tight_layout(pad=0.3, w_pad=0.8)
    OUT.parent.mkdir(exist_ok=True)
    fig.savefig(OUT)
    plt.close(fig)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
