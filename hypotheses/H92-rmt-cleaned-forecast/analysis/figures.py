"""H92 figures: figures/summary_obs.pdf (page 1) and figures/summary_obsb.pdf (page 2).
Usage: uv run python hypotheses/H92-rmt-cleaned-forecast/analysis/figures.py
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import h92lib as L  # noqa: E402

FIG = L.ROOT / "hypotheses/H92-rmt-cleaned-forecast/figures"
BLUE, ORANGE, AQUA, YELLOW, GRAY, INK = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#9a988f", "#2b2b29"
plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#85847e",
                     "axes.labelcolor": INK, "xtick.color": "#5d5c57", "ytick.color": "#5d5c57", "axes.grid": True,
                     "grid.color": "#ecebe6", "grid.linewidth": 0.6})


def main():
    FIG.mkdir(exist_ok=True)
    pt = pl.read_parquet(L.OUT / "periods.parquet").filter(pl.col("n_targets") >= 2)
    f = pl.read_parquet(L.OUT / "forecasts.parquet").filter(pl.col("variant") == "expand").with_columns(
        (1 - pl.col("mse_E5_clip") / pl.col("mse_E2_raw")).alias("r_raw"))
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.6), gridspec_kw={"width_ratios": [1.5, 1]})
    # (a) per-period gain of E5 over raw, LW-CC, mean field (content, gte), periods ordered by goal number
    x = pt.filter(pl.col("channel") == "content_gte").sort("goal_no")
    i = np.arange(x.height)
    for col, lab, c, mk in (("r_E2_raw", "vs raw", BLUE, "o"), ("r_E4_lwcc", "vs Ledoit–Wolf const. corr.", ORANGE, "s"),
                            ("r_E1_mean", "vs mean field", AQUA, "^")):
        ax[0].scatter(i, np.clip(x[col].to_numpy(), -0.6, 0.6), s=14, marker=mk, color=c, label=lab, lw=0, zorder=3)
    ax[0].axhline(0, color="#85847e", lw=0.8)
    ax[0].set_xticks(i[::3], [f"#{g}" for g in x["goal_no"].to_list()][::3], fontsize=6.5)
    ax[0].set_ylabel("gain of RMT clip, $1-{\\rm MSE}_{E5}/{\\rm MSE}_{\\rm rival}$")
    ax[0].set_xlabel("goal period (content, gte)")
    ax[0].set_title("(a) next-day forecast gain per period", fontsize=8, loc="left")
    ax[0].legend(fontsize=6.5, frameon=False, loc="lower right", ncol=1)
    ax[0].set_ylim(-0.65, 0.65)
    # (b) RMT signature: gain over raw vs q = N/T, per channel
    for ch, c, lab in (("content_gte", BLUE, "content"), ("talk", ORANGE, "talk"), ("act", GRAY, "activity")):
        y = f.filter(pl.col("channel") == ch)
        ax[1].scatter(y["q"].to_numpy(), np.clip(y["r_raw"].to_numpy(), -1, 1), s=6, color=c, alpha=0.65, lw=0, label=lab)
    ax[1].set_xscale("log"); ax[1].axhline(0, color="#85847e", lw=0.8)
    ax[1].set_xlabel("$q = N/T$ of the training window"); ax[1].set_ylabel("gain over raw")
    ax[1].set_title("(b) gain grows with $q$", fontsize=8, loc="left")
    ax[1].legend(fontsize=6.5, frameon=False, loc="lower right", markerscale=2)
    fig.tight_layout(); fig.savefig(FIG / "summary_obs.pdf"); plt.close(fig)
    # page 2: G51 gain vs training length; G38 room contrast (talk vs content)
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.1))
    g = f.filter((pl.col("goal_no") == 51) & pl.col("unit_id").is_in(["51c", "51d", "51g"]))
    for ch, c, lab in (("content_bge", BLUE, "content bge"), ("content_gte", AQUA, "content gte")):
        y = g.filter(pl.col("channel") == ch).group_by("n_train_days").agg(pl.col("r_raw").mean()).sort("n_train_days")
        ax[0].plot(y["n_train_days"], y["r_raw"], marker="o", ms=4, lw=1.6, color=c, label=lab)
    ax[0].axhline(0, color="#85847e", lw=0.8)
    ax[0].set_xlabel("training days (51c, 51d, 51g)"); ax[0].set_ylabel("gain over raw")
    ax[0].set_title("(a) #51: the cleaning gain falls as T grows", fontsize=7.5, loc="left"); ax[0].legend(fontsize=6.5, frameon=False)
    h = f.filter((pl.col("goal_no") == 38) & pl.col("cont_real").is_not_null() & pl.col("cont_E2_raw").is_not_null())
    labs, reals, raws, clips, lwcc = [], [], [], [], []
    for ch, lab in (("talk", "talk"), ("content_bge", "content bge"), ("content_gte", "content gte")):
        y = h.filter(pl.col("channel") == ch)
        labs.append(lab); reals.append(y["cont_real"].mean()); raws.append(y["cont_E2_raw"].mean())
        clips.append(y["cont_E5_clip"].mean()); lwcc.append(y["cont_E4_lwcc"].mean())
    xx = np.arange(3); w = 0.2
    for k, (vals, c, lab) in enumerate(((reals, INK, "realized"), (raws, BLUE, "raw forecast"), (clips, ORANGE, "RMT clip"),
                                         (lwcc, AQUA, "LW const. corr."))):
        ax[1].bar(xx + (k - 1.5) * w, vals, width=w * 0.9, color=c, label=lab)
    ax[1].set_xticks(xx, labs); ax[1].set_ylabel("room contrast (within − between)")
    ax[1].set_title("(b) #38: next-day room contrast", fontsize=7.5, loc="left")
    ax[1].legend(fontsize=6, frameon=False, ncol=2, loc="upper left")
    fig.tight_layout(); fig.savefig(FIG / "summary_obsb.pdf"); plt.close(fig)
    print("figures written")


if __name__ == "__main__":
    main()
