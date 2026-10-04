"""H89 writeup visual: village content changes by transmission; selection is undetectable.

Builds fig.pdf / fig.png from data/processed/H89-price-equation-culture/replication/periods.parquet:
  (a) the Price split in one picture (schematic): stayers change (transmission), influential stayers spread their
      trait (selection), leavers and entrants shift the mean (migration);
  (b) per eligible period: cross-fitted energy share of transmission in the day-to-day change of mean content (bge),
      agent-jackknife 95% CI;
  (c) the small terms: selection (with CI), migration, and the kickoff-field part (inside transmission);
  (d) migration share of style vs content per period (the style clause).
Usage: uv run python writeup/visuals/H89-price-equation/make.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "writeup/visuals"))
import vstyle as vs  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

P = ROOT / "data/processed/H89-price-equation-culture/replication/periods.parquet"
HELD = {1, 9, 14, 15, 22, 28, 29, 32, 34, 43, 45, 46, 47, 48, 49, 50}
C_TR, C_SEL, C_MIG, C_KICK = vs.C["green"], vs.C["pink"], vs.C["sky"], vs.FIELD


def schematic(ax):
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")
    ax.text(1.6, 9.6, "day $d$", ha="center", fontsize=7); ax.text(7.4, 9.6, "day $d'$", ha="center", fontsize=7)
    y0 = [7.6, 6.2, 5.0, 3.6]; y1 = [8.1, 6.9, 5.6, 4.2]
    w = [2.2, 1.0, 0.6, 0.9]          # fitness: influential stayer is big
    for a, b, ww in zip(y0, y1, w):
        ax.scatter(1.6, a, s=34 * ww, color=vs.INK2, zorder=3)
        ax.scatter(7.4, b, s=34, color=vs.INK2, zorder=3)
        ax.annotate("", xy=(7.15, b), xytext=(1.85, a), arrowprops=dict(arrowstyle="->", color=C_TR, lw=0.9))
    ax.scatter(1.6, 2.2, s=34, color=vs.MUTED, zorder=3); ax.text(2.1, 2.2, "leaves", fontsize=5.5, va="center",
                                                                    color=C_MIG)
    ax.scatter(7.4, 2.6, s=34, facecolor="white", edgecolor=vs.INK2, zorder=3)
    ax.text(7.0, 2.6, "joins", fontsize=5.5, va="center", ha="right", color=C_MIG)
    ax.text(4.5, 8.95, "transmission: stayers change", fontsize=5.8, color=C_TR, ha="center")
    ax.text(0.2, 0.85, "selection: big dots (adopted from,\nhigh fitness $w$) spread their trait", fontsize=5.5,
            color=C_SEL, va="bottom")
    ax.text(4.5, 0.0, r"$\Delta\bar z=\mathrm{Cov}(w,z)+E(w\,\Delta z)+\mathrm{migration}$", fontsize=6.5,
            ha="center", va="bottom")
    ax.text(9.9, 3.2, "schematic", fontsize=5, color=vs.MUTED, ha="right", va="center")


def main():
    vs.use()
    p = pl.read_parquet(P).filter(pl.col("eligible")).sort("goal")
    assert not set(p["goal"].to_list()) & HELD, "held-out period in the table"
    g = p["goal"].to_numpy(); x = np.arange(len(g))
    get = lambda c: p[c].to_numpy().astype(float)  # noqa: E731

    fig = plt.figure(figsize=(vs.W["double"], 3.6))
    gs = fig.add_gridspec(2, 3, width_ratios=[1.0, 2.15, 1.3], height_ratios=[1, 1], hspace=0.12, wspace=0.42)
    ax = fig.add_subplot(gs[:, 0]); schematic(ax); ax.set_title("(a) the Price split", loc="left")

    axt = fig.add_subplot(gs[0, 1]); axs = fig.add_subplot(gs[1, 1], sharex=axt)
    tr, trse = get("content_bge.s_trans"), get("content_bge.s_trans.se")
    axt.errorbar(x, tr, yerr=1.96 * trse, fmt="o", ms=3, color=C_TR, elinewidth=0.8, capsize=0, label="transmission")
    gt = get("content_gte.s_trans")
    axt.scatter(x, gt, marker="_", s=30, color=vs.INK2, lw=0.9, zorder=3, label="transmission, gte")
    axt.axhline(1, color=vs.INK2, lw=0.5); axt.axhline(0.5, color=vs.MUTED, lw=0.6, ls=":")
    axt.text(len(g) - 0.5, 0.52, "0.5 (P2 threshold)", fontsize=5.5, color=vs.MUTED, ha="right", va="bottom")
    axt.set_ylim(0.45, 1.22); axt.set_ylabel("energy share")
    axt.tick_params(labelbottom=False)
    axt.legend(loc="lower left", fontsize=6, ncol=2, bbox_to_anchor=(0.0, 0.08))
    axt.set_title(f"(b) content change is transmission: median {np.median(tr):.2f}, $\\geq$ 0.5 in "
                  f"{int((tr >= 0.5).sum())}/{len(g)} periods", loc="left")

    sel, selse = get("content_bge.s_sel"), get("content_bge.s_sel.se")
    mig, kick = get("content_bge.s_mig"), get("content_bge.s_kick")
    pp = get("content_bge.perm_p")
    axs.bar(x, kick, width=0.7, color=C_KICK, alpha=0.55, lw=0, label="kickoff field (in transmission)")
    axs.errorbar(x - 0.15, sel, yerr=1.96 * selse, fmt="o", ms=2.8, color=C_SEL, elinewidth=0.8, capsize=0,
                 label="selection")
    axs.scatter(x + 0.15, mig, marker="s", s=9, color=C_MIG, zorder=3, label="migration")
    sig = pp < 0.05
    axs.scatter(x[sig] - 0.15, sel[sig], s=55, facecolor="none", edgecolor=vs.INK, lw=0.7, zorder=4,
                label="selection, perm. p < 0.05")
    axs.axhline(0, color=vs.INK2, lw=0.5)
    axs.set_ylim(-0.17, 0.38); axs.set_ylabel("energy share")
    axs.set_xticks(x, [f"#{k}" for k in g], rotation=90, fontsize=5.3)
    axs.set_xlim(-0.7, len(g) - 0.3)
    axs.legend(loc="upper left", fontsize=5.3, ncol=2, bbox_to_anchor=(0.0, 1.03), columnspacing=0.6, handlelength=1.0,
               handletextpad=0.6, markerscale=0.8)
    axs.set_xlabel("goal period (content, bge; error bars: agent-jackknife 95% CI)")

    ax = fig.add_subplot(gs[:, 2])
    sm = get("style.s_mig")
    tie = (np.abs(sm) < 1e-12) & (np.abs(mig) < 1e-12)
    lim = (-0.06, 0.32)
    ax.plot(lim, lim, color=vs.INK2, lw=0.6, ls="--")
    ax.scatter(mig[~tie], sm[~tie], s=12, color=C_MIG, edgecolor="white", lw=0.3, zorder=3)
    ax.scatter([0], [0], s=30, facecolor="white", edgecolor=vs.INK2, zorder=4)
    ax.annotate(f"{int(tie.sum())} periods with no\nentries or exits", (0, 0), xytext=(0.09, -0.035), fontsize=5.5,
                arrowprops=dict(arrowstyle="-", lw=0.5, color=vs.INK2), va="center")
    for k, a, b in zip(g, mig, sm):
        if k in (51, 38, 40, 25):
            ax.annotate(f"#{k}", (a, b), xytext=(3, 2), textcoords="offset points", fontsize=5.5, color=vs.INK2)
    ab = int((sm[~tie] > mig[~tie]).sum())
    ax.text(0.31, 0.165, f"style above content\nin {ab}/{int((~tie).sum())} periods\nwith turnover", fontsize=6,
            va="top", ha="right")
    ax.set_xlim(*lim); ax.set_ylim(*lim); ax.set_aspect("equal")
    ax.set_xlabel("migration share, content"); ax.set_ylabel("migration share, style")
    ax.set_title("(c) style moves with the roster more", loc="left")
    vs.save(fig, HERE / "fig")
    plt.close(fig)
    print("median trans", np.median(tr), "median |sel|", np.median(np.abs(sel)), "median mig", np.median(mig),
          "perm p<.05", int(sig.sum()), "style>content", ab, "/", int((~tie).sum()))


if __name__ == "__main__":
    main()
