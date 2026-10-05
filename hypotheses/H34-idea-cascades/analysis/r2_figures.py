"""H34 round 2 figures: figures/r2_obs.pdf (R1 tails, R2 room changes) and figures/r2_obsb.pdf (R4 semantic ideas).

  uv run python hypotheses/H34-idea-cascades/analysis/r2_figures.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "scheme"))
import h34stats as S  # noqa: E402
import h34core as C  # noqa: E402
import r2_mixture as M  # noqa: E402

FIG = HERE.parent / "figures"
R1B, R2 = C.OUT / "r1b", C.OUT / "r2"
C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#dcdad3"
plt.rcParams.update({"font.size": 8, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5, "lines.linewidth": 1.6,
                     "font.family": "DejaVu Sans"})
MK = ["o", "s", "^"]


def fig_obs():
    pt = pl.read_parquet(R1B / "results" / "period_table.parquet").filter(pl.col("cls") == "ALL")
    mx = pl.read_parquet(R2 / "mixture" / "periods_r1b.parquet")
    fig, axs = plt.subplots(1, 2, figsize=(7.0, 2.7))
    ax = axs[0]
    for i, (g, col) in enumerate(zip((20, 42, 51), (C1, C2, C3))):
        tr = pl.read_parquet(R1B / f"G{g:02d}" / "trees.parquet")
        r = pt.filter(pl.col("goal") == g).row(0, named=True)
        m = mx.filter(pl.col("goal") == g).row(0, named=True)
        N = int(m["N_fit"])
        sz = np.minimum(tr["size"].to_numpy(), N)
        s = np.arange(1, sz.max() + 1)
        ccdf = np.array([(sz >= x).mean() for x in s])
        ax.plot(s, ccdf, color=col, marker=MK[i], ms=3.5, lw=0, label=f"#{g}", zorder=3)
        p_fn, _ = S.fngw_pmf(r["R"], r["k"], N, seed=1)
        pg = M.marginal(m["mu"], m["alpha"], N)
        xs = np.arange(1, N + 1)
        ax.plot(xs, np.cumsum(p_fn[::-1])[::-1], color=col, ls="--", lw=0.9, zorder=2)
        ax.plot(xs, np.cumsum(pg[::-1])[::-1], color=col, ls="-", lw=1.1, zorder=2)
    ax.plot([], [], color=INK2, ls="--", lw=0.9, label="one R (FN-GW)")
    ax.plot([], [], color=INK2, ls="-", lw=1.1, label="gamma-mixed R")
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_ylim(1e-5, 1.2)
    ax.set_xlabel("tree size s (agents)"); ax.set_ylabel("P(size ≥ s)")
    ax.set_title("(a) idea trees: one R vs gamma-mixed R", fontsize=8, loc="left")
    ax.legend(fontsize=6.5, loc="lower left")
    # (b) room changes
    ax = axs[1]
    g = pl.read_parquet(R2 / "ne" / "groups.parquet").filter(pl.col("used"))
    summ = json.loads((R2 / "ne" / "summary.json").read_text())
    multi = g.group_by("boundary").len().filter(pl.col("len") >= 2)["boundary"].to_list()
    g = g.filter(pl.col("boundary").is_in(multi))
    g = g.with_columns((pl.col("d_pred") - pl.col("d_pred").mean().over("boundary")).alias("xp"),
                       (pl.col("d_obs") - pl.col("d_obs").mean().over("boundary")).alias("yo"),
                       (pl.col("d_lo") - pl.col("d_obs")).alias("elo"), (pl.col("d_hi") - pl.col("d_obs")).alias("ehi"))
    ne = g["boundary"].is_in(["39->40", "40->41"]).to_numpy()
    for msk, col, lab in ((~ne, INK2, "other boundaries"), (ne, C2, "NE42 merge / split")):
        sub = g.filter(pl.Series(msk))
        ax.errorbar(sub["xp"], sub["yo"], yerr=[-sub["elo"].to_numpy(), sub["ehi"].to_numpy()], fmt="o", ms=4, color=col,
                    ecolor=col, elinewidth=0.7, capsize=0, label=lab, zorder=3, mec="white", mew=0.5)
    xx = np.linspace(-0.5, 0.5, 10)
    for b, ls, lab in ((1.0, "-", "dilution law (β = 1)"), (1.7, "--", "skeleton, constant per read (β ≈ 1.7)"),
                       (2.5, ":", "skeleton, field only (β ≈ 2.5)")):
        ax.plot(xx, b * xx, color=C1, ls=ls, lw=1.0, label=lab, zorder=2)
    ax.set_xlabel("predicted Δ ln R_src (boundary-demeaned)"); ax.set_ylabel("observed Δ ln R_src (boundary-demeaned)")
    ax.set_title(f"(b) room changes: β̂ = {summ['beta']:.2f} [{summ['beta_ci'][0]:.2f}, {summ['beta_ci'][1]:.2f}]", fontsize=8, loc="left")
    ax.legend(fontsize=6, loc="upper left")
    fig.tight_layout()
    fig.savefig(FIG / "r2_obs.pdf"); fig.savefig(FIG / "r2_obs.png", dpi=180)


def fig_obsb():
    mk = pl.read_parquet(R1B / "results" / "period_table.parquet").filter(pl.col("cls") == "ALL").select(
        "goal", pl.col("R").alias("Rm"), (pl.col("hr_unread5") / pl.col("hr_seen5")).alias("um"))
    fig, axs = plt.subplots(1, 2, figsize=(7.0, 2.6))
    ax = axs[0]
    for tag, col, m, lab in (("sem_bge_small", C1, "o", "bge-small"), ("sem_gte_modernbert", C2, "s", "gte-modernbert")):
        pt = pl.read_parquet(R2 / tag / "results" / "period_table.parquet").join(mk, on="goal")
        ax.scatter(pt["Rm"], pt["R"], s=16, color=col, marker=m, edgecolor="white", linewidth=0.5, label=lab, zorder=3)
    ax.plot([0, 0.45], [0, 0.45], color=INK2, ls=":", lw=0.8)
    ax.text(0.33, 0.36, "equal", fontsize=6.5, color=INK2)
    ax.set_xlabel("marker-idea R̂ (round 1b)"); ax.set_ylabel("semantic-idea R̂")
    ax.set_title("(a) paraphrase ideas branch about half as much", fontsize=8, loc="left")
    ax.legend(fontsize=6.5, loc="upper left")
    ax = axs[1]
    pt = pl.read_parquet(R2 / "sem_gte_modernbert" / "results" / "period_table.parquet").join(mk, on="goal")
    pb = pl.read_parquet(R2 / "sem_bge_small" / "results" / "period_table.parquet").select("goal", (pl.col("hr_unread5") / pl.col("hr_seen5")).alias("ub"))
    pt = pt.join(pb, on="goal").with_columns((pl.col("hr_unread5") / pl.col("hr_seen5")).alias("ug")).sort("goal")
    x = np.arange(pt.height)
    lo_c, hi_c = 0.1, 10.0
    pt = pt.with_columns([pl.col(c).clip(lo_c, hi_c) for c in ("um", "ub", "ug")])
    ax.scatter(x, pt["um"], s=14, color=INK2, marker="o", label="marker ideas", zorder=3)
    ax.scatter(x, pt["ub"], s=14, color=C1, marker="o", edgecolor="white", linewidth=0.4, label="semantic, bge", zorder=3)
    ax.scatter(x, pt["ug"], s=14, color=C2, marker="s", edgecolor="white", linewidth=0.4, label="semantic, gte", zorder=3)
    ax.axhline(1, color=INK2, lw=0.8, ls=":")
    ax.set_yscale("log"); ax.set_ylim(0.03, 14)
    ax.set_xticks(x[::3]); ax.set_xticklabels([f"#{g}" for g in pt["goal"].to_list()[::3]], fontsize=6)
    ax.set_ylabel("HR unread / HR read (5 min)")
    ax.set_title("(b) unread vs read uses (clipped to [0.1, 10])", fontsize=8, loc="left")
    ax.legend(fontsize=6.5, loc="lower left", ncol=3, handletextpad=0.2, columnspacing=0.8)
    fig.tight_layout()
    fig.savefig(FIG / "r2_obsb.pdf"); fig.savefig(FIG / "r2_obsb.png", dpi=180)


if __name__ == "__main__":
    fig_obs()
    fig_obsb()
