"""H54 visuals: the kickoff text is the quench target.

fig.pdf/png  (a) genericness-corrected target score of every day-1 content centroid (rows) against every eligible
             kickoff (columns), 33 x 33, bge; the diagonal is the own kickoff. (b) rank of the own kickoff among the
             33 candidates, per period, against the kickoff-swap null (uniform rank, gray band). (c) #51 private goals:
             weekly role-swap accuracy of each agent's content on its own goal text vs a swapped agent's goal.

Inputs (read-only): data/processed/H54-kickoff-quench-target/NE34/{S_kick.npy, periods.parquet, results.json},
G51/native.json; shared period_affordances (mode F = free week).
Usage: uv run python writeup/visuals/H54-kickoff-quench-target/make.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VIS = HERE.parent
ROOT = VIS.parents[1]
sys.path.insert(0, str(VIS))

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import TwoSlopeNorm  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

import vstyle as vs  # noqa: E402

D = ROOT / "data/processed/H54-kickoff-quench-target"


def corrected(S):
    """H54's genericness correction: S_pq minus mean_{p' != q} S_{p'q} (a kickoff that resembles every centroid gets
    no credit)."""
    n = S.shape[0]
    cm = np.array([[np.mean([S[pp, q] for pp in range(n) if pp != q]) for q in range(n)]])
    return S - cm


def main():
    vs.use()
    S = np.load(D / "NE34/S_kick.npy")
    per = pl.read_parquet(D / "NE34/periods.parquet")
    res = json.load(open(D / "NE34/results.json"))["P1"]
    g51 = json.load(open(D / "G51/native.json"))
    modes = pl.read_parquet(ROOT / "data/processed/shared/period_affordances.parquet").select("goal_no", "mode") \
        .unique("goal_no")
    mode = dict(zip(modes["goal_no"].to_list(), modes["mode"].to_list()))
    goals = per["goal_no"].to_list()
    n = len(goals)
    Sh = corrected(S)
    rank = np.array([1 + (np.delete(Sh[i], i) > Sh[i, i]).sum() for i in range(n)])
    assert rank.tolist() == per["rank"].to_list(), "rank mismatch with the card table"
    top1 = int((rank == 1).sum())

    fig = plt.figure(figsize=(vs.W["double"], 2.55))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.05, 1.35, 0.85], wspace=0.5)
    a0, a1, a2 = (fig.add_subplot(gs[0, i]) for i in range(3))

    # (a) score matrix
    v = np.nanpercentile(np.abs(Sh), 98)
    im = a0.imshow(Sh, cmap=vs.DIV, norm=TwoSlopeNorm(0, -v, v), interpolation="nearest")
    for i in range(n):
        a0.add_patch(Rectangle((i - 0.5, i - 0.5), 1, 1, fill=False, ec=vs.INK, lw=0.25))
    tk = [i for i, g in enumerate(goals) if g in (3, 10, 20, 30, 40, 51)]
    a0.set_xticks(tk); a0.set_xticklabels([f"#{goals[i]}" for i in tk], fontsize=6)
    a0.set_yticks(tk); a0.set_yticklabels([f"#{goals[i]}" for i in tk], fontsize=6)
    a0.set_xlabel("candidate kickoff text"); a0.set_ylabel("day-1 content centroid")
    a0.grid(False)
    cb = fig.colorbar(im, ax=a0, fraction=0.046, pad=0.03)
    cb.ax.tick_params(labelsize=5.5); cb.ax.set_xlabel("score", fontsize=6, labelpad=2)
    a0.set_title("(a) day 1 vs every kickoff (bge)", loc="left")

    # (b) rank of the own kickoff
    x = np.arange(n)
    lo, hi = 0.05 * n, 0.95 * n
    a1.axhspan(lo, hi, color=vs.NULL, alpha=0.35, lw=0, label="swap null (90% band, median)")
    a1.axhline((n + 1) / 2, color=vs.MUTED, lw=0.8, ls="--")
    free = np.array([mode.get(g) == "F" or g in (44, 51) for g in goals])
    a1.vlines(x, rank, n + 1, color=vs.GRID, lw=0.6, zorder=1)
    a1.scatter(x[~free], rank[~free], s=16, color=vs.FIELD, edgecolor=vs.INK, lw=0.5, zorder=3,
               label="named shared target")
    a1.scatter(x[free], rank[free], s=16, marker="s", facecolor="white", edgecolor=vs.INK, lw=0.7, zorder=3,
               label="free week; #44 half-free; #51 private")
    a1.set_yscale("log")
    a1.set_ylim(n + 2, 0.8)
    a1.set_yticks([1, 2, 5, 10, 20, 33]); a1.set_yticklabels(["1", "2", "5", "10", "20", "33"])
    a1.set_xticks(x[::3]); a1.set_xticklabels([f"#{goals[i]}" for i in x[::3]], fontsize=6, rotation=0)
    a1.set_xlim(-0.8, n - 0.2)
    a1.set_xlabel("goal period")
    a1.set_ylabel("rank of the own kickoff (of 33)")
    a1.legend(loc="lower left", bbox_to_anchor=(0.02, 0.1), fontsize=5.8, borderaxespad=0.2, handletextpad=0.3,
              frameon=True, facecolor="white", edgecolor="none", framealpha=0.85)
    a1.text(0.98, 0.47, f"top-1 in {top1}/{n}\nmedian percentile {res['median_pi']:.1f}\n"
            f"p = {res['p_wilcoxon']:.0e}".replace("e-0", "e−"), transform=a1.transAxes, ha="right", va="top",
            fontsize=6.3, color=vs.INK)
    a1.grid(axis="x", visible=False)
    a1.set_title("(b) the own kickoff ranks first", loc="left")

    # (c) #51 private goals, weekly
    wk = g51["weekly"]
    w = np.array([r["week"] for r in wk]) + 1
    acc = np.array([r["swap_accuracy"] for r in wk]); npairs = np.array([r["n_pairs"] for r in wk])
    se = np.sqrt(acc * (1 - acc) / npairs)
    a2.axhline(0.5, color=vs.MUTED, lw=0.8, ls="--")
    a2.text(w[-1], 0.515, "chance (swap null)", fontsize=5.8, color=vs.INK2, ha="right", va="bottom")
    a2.errorbar(w, acc, yerr=1.645 * se, fmt="o-", color=vs.FIELD, mec=vs.INK, mew=0.5, ms=3.5, capsize=1.2, lw=1.2)
    a2.set_ylim(0.38, 1.02); a2.set_xlim(0.5, w[-1] + 0.5)
    a2.set_xticks(w)
    a2.set_xlabel("week of #51")
    a2.set_ylabel("own goal beats a swapped goal")
    a2.text(0.5 + 0.2, 0.79, f"all weeks {g51['swap_accuracy']:.2f}\n(p = {g51['p_perm']:.4f})", fontsize=6.3,
            color=vs.INK, va="top")
    a2.set_title("(c) #51: each agent on its own goal", loc="left")

    vs.save(fig, HERE / "fig")
    plt.close(fig)
    print("top1", top1, "of", n, "median pi", res["median_pi"], "p", res["p_wilcoxon"])
    print("weekly", np.round(acc, 3).tolist(), "overall", g51["swap_accuracy"])
    print("free ranks", {g: int(r) for g, r, f in zip(goals, rank, free) if f})


if __name__ == "__main__":
    main()
