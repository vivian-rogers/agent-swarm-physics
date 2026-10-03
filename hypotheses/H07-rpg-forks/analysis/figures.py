"""H07 figures (exploratory). Palette: dataviz reference categorical slots 1-2 (light mode).

NE15/figures/fig_vertical.pdf    copy fraction vs. active hours since the split, per feature type (small multiples)
G35/figures/fig_clocks.pdf       src-file copy fraction during #35 against three clocks, with single-exponential fits
NE15/figures/fig_horizontal.pdf  best-vs-rest copy information (shuffle-corrected, relative to T0) per day; commits/day
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

H07 = Path(__file__).resolve().parents[1]
FIG_NE15, FIG_G35 = H07 / "NE15" / "figures", H07 / "G35" / "figures"
COL = {"best": "#2a78d6", "rest": "#eb6834"}
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
plt.rcParams.update({"font.size": 8, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
                     "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": SURF,
                     "axes.facecolor": SURF, "legend.frameon": False, "lines.linewidth": 2})
LABEL = {"files": "all files (blob identical)", "files_src": "src/*.js files", "functions": "function bodies",
         "numbers_data": "numeric parameters", "names": "content names (keyed)", "entities": "entity id → name"}


def fig_vertical():
    cc = pl.read_parquet(P / "curves_commit.parquet")
    end35 = {lin: cc.filter((pl.col("lineage") == lin) & (pl.col("t") <= T35_END))["active_h"].max()
             for lin in ("best", "rest")}
    feats = list(LABEL)
    fig, axes = plt.subplots(2, 3, figsize=(7.2, 4.4), sharex=True)
    for ax, f in zip(axes.flat, feats):
        for lin in ("best", "rest"):
            g = cc.filter(pl.col("lineage") == lin).sort("k")
            x = np.concatenate([[0], g["active_h"].to_numpy()])
            y = np.concatenate([[1], g[f"{f}_c"].to_numpy()])
            ax.step(x, y, where="post", color=COL[lin], lw=1.6, label=f"#{lin}")
        ax.axvline(max(end35.values()), color=INK2, lw=0.8, ls=":")
        ax.set_title(LABEL[f], fontsize=8, color=INK, loc="left")
        ax.set_xlim(0, 70)
    for ax in axes[1]:
        ax.set_xlabel("active hours since the split (T0)")
    for ax in axes[:, 0]:
        ax.set_ylabel("copy fraction vs. ancestor")
    axes[1, 1].legend(loc="center left", bbox_to_anchor=(0.02, 0.45))
    axes[0, 0].text(max(end35.values()) + 1, 0.98, "end of #35", color=INK2, fontsize=7, va="top")
    fig.suptitle("Vertical inheritance: share of ancestor keys still identical", fontsize=9, color=INK, x=0.01,
                 ha="left")
    fig.text(0.01, 0.005, "Rest continues to 227 active h with 18 more commits (not shown; curve flat). "
             "Exploratory, non-holdout.", fontsize=6.5, color=INK2)
    fig.tight_layout(rect=(0, 0.02, 1, 0.97))
    fig.savefig(FIG_NE15 / "fig_vertical.pdf")
    plt.close(fig)


def fig_clocks():
    cc = pl.read_parquet(P / "curves_commit.parquet").filter(pl.col("t") <= T35_END)
    fits = pl.read_parquet(P / "clock_fits.parquet").filter(pl.col("feature") == "files_src")
    clocks = [("n_commits", "cumulative non-merge commits"), ("n_touches", "cumulative file-touches"),
              ("active_h", "active hours")]
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.6), sharey=True)
    for ax, (ck, lab) in zip(axes, clocks):
        txt = []
        for lin in ("best", "rest"):
            g = cc.filter(pl.col("lineage") == lin).sort("k")
            x = np.concatenate([[0], g[ck].to_numpy().astype(float)])
            y = np.concatenate([[1], g["files_src_c"].to_numpy()])
            ax.plot(x, y, color=COL[lin], lw=1.6, label=f"#{lin}")
            mu = fits.filter((pl.col("lineage") == lin) & (pl.col("clock") == ck))["mu1"][0]
            xx = np.linspace(0, x.max(), 100)
            ax.plot(xx, np.exp(-mu * xx), color=COL[lin], lw=0.9, ls="--")
            txt.append(mu)
        ax.set_xlabel(lab)
        ax.set_title(f"μ ratio best/rest = {txt[0] / txt[1]:.2f}", fontsize=8, color=INK, loc="left")
    axes[0].set_ylabel("src-file copy fraction (#35)")
    axes[0].legend(loc="lower left")
    fig.suptitle("Which clock collapses the two forks? (dashed: single-exponential fit)", fontsize=9, color=INK,
                 x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(FIG_G35 / "fig_clocks.pdf")
    plt.close(fig)


def fig_horizontal():
    hd = pl.read_parquet(P / "horizontal_day.parquet")
    t0 = hd.filter(pl.col("pt_date") == "T0")
    d = hd.filter(pl.col("pt_date") != "T0").filter(pl.col("pt_date") <= "2026-04-10")
    days = ["T0"] + d["pt_date"].to_list()
    x = np.arange(len(days))
    fig, axes = plt.subplots(2, 1, figsize=(7.2, 4.6), sharex=True, gridspec_kw={"height_ratios": [2, 1]})
    ax = axes[0]
    shades = ["#0b0b0b", "#52514e", "#2a78d6", "#1baf7a", "#eda100", "#4a3aa7"]
    for (f, lab), col in zip(LABEL.items(), shades):
        v = np.concatenate([[t0[f"{f}_I_copy_ex"][0]], d[f"{f}_I_copy_ex"].to_numpy()]) / t0[f"{f}_I_copy_ex"][0]
        ax.plot(x, v, color=col, lw=1.4, marker="o", ms=2.5)
        ax.text(x[-1] + 0.3, v[-1], lab, color=INK, fontsize=6.5, va="center")
    ax.set_ylabel("I_copy(best; rest) − shuffle null\n(relative to T0)")
    ax.set_title("Horizontal copy information between the forks", fontsize=9, color=INK, loc="left")
    ax.set_xlim(-0.5, len(days) + 6)
    cm = pl.read_parquet(P / "commits.parquet").filter(~pl.col("is_merge")).with_columns(
        pl.col("t_commit").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.Utf8).alias("pt_date"))
    ax2 = axes[1]
    w = 0.38
    for i, lin in enumerate(("best", "rest")):
        n = dict(cm.filter(pl.col("lineage") == lin).group_by("pt_date").len().iter_rows())
        ax2.bar(x + (i - 0.5) * w, [n.get(dd, 0) for dd in days], width=w - 0.04, color=COL[lin], label=f"#{lin}")
    ax2.set_ylabel("non-merge commits / day")
    ax2.legend(loc="upper right")
    lab = [dd if dd == "T0" else dd[5:] for dd in days]
    ax2.set_xticks(x[::2], lab[::2], rotation=60, fontsize=6.5)
    for a in axes:
        a.axvline(5.5, color=INK2, lw=0.8, ls=":")
    axes[0].text(5.6, 1.0, "end of #35", color=INK2, fontsize=7, va="top")
    fig.tight_layout()
    fig.savefig(FIG_NE15 / "fig_horizontal.pdf")
    plt.close(fig)


if __name__ == "__main__":
    FIG_NE15.mkdir(parents=True, exist_ok=True)
    FIG_G35.mkdir(parents=True, exist_ok=True)
    fig_vertical()
    fig_clocks()
    fig_horizontal()
    print("figures written to", FIG_NE15, "and", FIG_G35)
