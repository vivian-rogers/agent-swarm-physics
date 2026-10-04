"""H91 figures: figures/summary_obs.pdf (page 1) and figures/summary_obsb.pdf (page 2 synthetic).
Usage: uv run python hypotheses/H91-eigenvector-rotation-signal/analysis/figures.py
"""
from __future__ import annotations

import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import h91lib as L  # noqa: E402

FIG = L.ROOT / "hypotheses/H91-eigenvector-rotation-signal/figures"
BLUE, ORANGE, AQUA, YELLOW, GRAY, INK = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#9a988f", "#2b2b29"
plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#85847e",
                     "axes.labelcolor": INK, "xtick.color": "#5d5c57", "ytick.color": "#5d5c57", "axes.grid": True,
                     "grid.color": "#ecebe6", "grid.linewidth": 0.6})


def main():
    FIG.mkdir(exist_ok=True)
    d = pl.read_parquet(L.OUT / "days_scored.parquet")
    ev = pl.read_parquet(L.ROOT / "data/processed/H36-reorganization-alarm/r1b/fixed_bge_none/events.parquet").filter(
        ~pl.col("holdout0"))
    res = json.loads((L.OUT / "eval/results.json").read_text())
    goal_days = set(ev.filter(pl.col("cls") == "goal")["pt_date0"].to_list())
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.6), gridspec_kw={"width_ratios": [1, 1.6]})
    # (a) kickoff vs placebo for A_C and R1
    rng = np.random.default_rng(0)
    for i, (col, lab, c) in enumerate((("A_C", "rotation alarm $A_C$", BLUE), ("R1m", "topic shift R1 (H36)", ORANGE))):
        pe = d.filter(pl.col("pt_date").is_in(list(goal_days)))[col].drop_nulls().drop_nans().to_numpy()
        pn = d.filter(pl.col("placebo"))[col].drop_nulls().drop_nans().to_numpy()
        pe, pn = np.clip(pe, -4, 12), np.clip(pn, -4, 12)
        x0 = i * 2.4
        ax[0].scatter(x0 + rng.uniform(-0.25, 0.25, len(pn)), pn, s=9, color=GRAY, alpha=0.7, lw=0)
        ax[0].scatter(x0 + 1 + rng.uniform(-0.25, 0.25, len(pe)), pe, s=11, color=c, lw=0)
        a = res["goal"][col]
        ax[0].text(x0 + 0.5, 12.6, f"AUC {a['auc']:.2f}\n[{a['auc_lo']:.2f}, {a['auc_hi']:.2f}]", ha="center", fontsize=7, color=INK)
    ax[0].axhline(2, color="#85847e", lw=0.8, ls="--")
    ax[0].set_xticks([0, 1, 2.4, 3.4], ["placebo", "kickoff\nrotation", "placebo", "kickoff\nR1"])
    ax[0].set_ylim(-4.5, 14.5); ax[0].set_ylabel("trailing z (day 0)")
    ax[0].set_title("(a) goal kickoffs vs placebo days", fontsize=8, loc="left")
    # (b) z_boot over time (content, model mean) with the stationary synthetic band
    dd = d.filter(pl.col("z_C").is_not_null() & pl.col("z_C").is_not_nan()).with_row_index("i")
    ax[1].axhspan(0.1, 0.75, color="#ecebe6", lw=0, label="stationary synthetic (0.1–0.75)")
    ax[1].plot(dd["i"].to_numpy(), dd["z_C"].to_numpy(), lw=1.0, color=BLUE, label="content $z_{\\rm boot}$ (bge+gte)")
    kk = dd.filter(pl.col("pt_date").is_in(list(goal_days)))
    ax[1].scatter(kk["i"].to_numpy(), kk["z_C"].to_numpy(), s=14, color=ORANGE, zorder=3, label="goal kickoff pair", lw=0)
    for t, lab in (("2026-05-04", "NE42 merge"), ("2026-05-11", "split"), ("2026-08-05", "#focus")):
        r = dd.filter(pl.col("pt_date") == t)
        if r.height:
            ax[1].annotate(lab, (r["i"][0], r["z_C"][0]), xytext=(0, 14), textcoords="offset points", ha="center", fontsize=6.5,
                           arrowprops={"arrowstyle": "-", "color": "#85847e", "lw": 0.6})
    ax[1].axhline(np.median(dd["z_C"].to_numpy()), color=INK, lw=0.6, ls=":")
    ax[1].set_xlabel("scored day pair (time order, 2025-05 → 2026-09)"); ax[1].set_ylabel("rotation excess $z_{\\rm boot}$ (k = 2)")
    ax[1].set_title("(b) day-to-day eigenvector rotation", fontsize=8, loc="left")
    ax[1].legend(fontsize=6.5, frameon=False, loc="lower left", ncol=2)
    ax[1].set_ylim(-2.2, 3.6)
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs.pdf"); plt.close(fig)
    # synthetic: AUC S1 vs S0 by N, W (strong rooms, rho 0.5), boot vs split
    s = pl.read_parquet(L.OUT / "synthetic/summary.parquet").filter((pl.col("channel") == "content") & (pl.col("b_room") == 0.4)
                                                                    & (pl.col("rho") == 0.5))
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.25))
    cols = {4: YELLOW, 8: AQUA, 16: BLUE}
    for W, c in cols.items():
        x = s.filter(pl.col("W") == W).sort("N")
        ax[0].plot(x["N"], x["auc_S1_boot_k2"], marker="o", ms=4, lw=1.6, color=c, label=f"W = {W}, boot null")
        ax[0].plot(x["N"], x["auc_S1_split_k2"], marker="o", ms=3, lw=1.0, ls="--", color=c, alpha=0.7)
        ax[1].plot(x["N"], x["hit_boot_k2"], marker="o", ms=4, lw=1.6, color=c, label=f"W = {W}")
        ax[1].plot(x["N"], x["far_boot_k2"], marker="s", ms=3, lw=0.8, ls=":", color=c)
    ax[0].axhline(0.5, color="#85847e", lw=0.6)
    ax[0].set_xscale("log", base=2); ax[1].set_xscale("log", base=2)
    for a_ in ax:
        a_.set_xticks([4, 8, 16, 32], ["4", "8", "16", "32"]); a_.set_xlabel("agents N")
        a_.axvline(10, color=ORANGE, lw=0.8, ls="--")
    ax[0].text(10.5, 0.27, "real median N 10, W 8", fontsize=6.5, color=ORANGE)
    ax[0].set_ylabel("AUC, regrouping vs stationary"); ax[0].set_ylim(0.2, 1.05)
    ax[0].set_title("(a) solid: boot null; dashed: pooled split", fontsize=7.5, loc="left")
    ax[1].set_ylabel("alarm rate"); ax[1].set_ylim(-0.03, 1.03)
    ax[1].set_title("(b) alarm hit at a regrouping (solid), FAR (dotted)", fontsize=7.5, loc="left")
    h, l = ax[1].get_legend_handles_labels()
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.legend(h, l, loc="upper center", ncol=3, fontsize=6.5, frameon=False, bbox_to_anchor=(0.5, 1.0))
    fig.savefig(FIG / "summary_obsb.pdf"); plt.close(fig)
    print("figures written")


if __name__ == "__main__":
    main()
