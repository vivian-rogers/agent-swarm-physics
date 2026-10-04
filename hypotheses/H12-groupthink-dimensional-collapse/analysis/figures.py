"""H12 figures (matplotlib, PDF). Palette: reference categorical slots 1-3 (blue, orange, aqua), recessive grey axes.

Usage: uv run python hypotheses/H12-groupthink-dimensional-collapse/analysis/figures.py [synthetic|real|summary|all]
"""
from __future__ import annotations

import json
import sys

import h12lib as L
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

C1, C2, C3, C4 = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#d9d8d4"
SYN = L.OUT / "synthetic"


def style():
    plt.rcParams.update({
        "font.size": 7.5, "axes.titlesize": 8, "axes.labelsize": 7.5, "xtick.labelsize": 7, "ytick.labelsize": 7,
        "legend.fontsize": 6.5, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
        "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5,
        "lines.linewidth": 1.6, "lines.markersize": 4, "legend.frameon": False, "pdf.fonttype": 42, "figure.dpi": 150})


def preview(fig, name):
    import os
    d = os.environ.get("H12_PREVIEW")
    if d:
        fig.savefig(f"{d}/{name}.png", dpi=200)


def panel_label(ax, s):
    ax.set_title(s, loc="left", color=INK, fontweight="bold")


# ------------------------------------------------------------------------------------------ synthetic
def fig_synthetic():
    A = pl.read_parquet(SYN / "A_activity.parquet")
    B = pl.read_parquet(SYN / "B_content.parquet")
    C = pl.read_parquet(SYN / "C_pr.parquet")
    D = pl.read_parquet(SYN / "D_power.parquet")
    fig, axs = plt.subplots(2, 3, figsize=(7.5, 5.4))

    # (a) false positives at k = 0 by null and scenario
    ax = axs[0, 0]
    a3 = A.filter((pl.col("exp") == "A3") & (pl.col("k") == 0) & (pl.col("reg") == "III"))
    scen = [("shared", 0.0, "shared schedule"), ("hetero", 0.0, "heterogeneous daily profiles"), ("shared", 0.05, "platform stalls (5%)")]
    nulls = [("k_mp", "MP"), ("k_mpeff", "MP, T_eff"), ("k_circ", "circular shift"), ("k_cd", "cross-day"), ("k_cd_lull", "cross-day + lull filter")]
    y = np.arange(len(nulls))
    for j, (pr, lu, lab) in enumerate(scen):
        s = a3.filter((pl.col("profile") == pr) & (pl.col("lulls") == lu))
        v = [(s[c] > 0).mean() for c, _ in nulls]
        ax.barh(y + (j - 1) * 0.26, v, height=0.24, color=[C1, C2, C3][j], label=lab)
    ax.set_yticks(y, [n for _, n in nulls]); ax.invert_yaxis()
    ax.axvline(0.05, color=INK2, lw=0.8, ls=":")
    ax.set_xlabel("false-positive rate (k = 0, activity)"); ax.set_xlim(0, 1.02)
    ax.legend(loc="upper center", bbox_to_anchor=(0.45, -0.2), fontsize=5.8, ncol=1)
    panel_label(ax, "a  False modes, k = 0")

    # (b) activity recovery vs loading
    ax = axs[0, 1]
    a1 = A.filter(pl.col("exp") == "A1")
    for j, k in enumerate([1, 2, 3]):
        s = a1.filter(pl.col("k") == k).group_by("a").agg((pl.col("k_cd") >= pl.col("k")).mean().alias("p")).sort("a")
        ax.plot(s["a"], s["p"], "o-", color=[C1, C2, C3][j], label=f"{k} planted mode{'s' if k > 1 else ''}")
    ax.set_xlabel("latent loading a (N = 15, 5 days)"); ax.set_ylabel("P(k_cd ≥ k)"); ax.set_ylim(-0.03, 1.03)
    ax.legend(loc="center right")
    ax.annotate("3rd (family) mode\nnever recovered", xy=(0.5, 0.0), xytext=(0.33, 0.25), fontsize=6, color=INK2,
                arrowprops=dict(arrowstyle="-", color=INK2, lw=0.6))
    panel_label(ax, "b  Activity modes")

    # (c) content recovery vs loading and statement count
    ax = axs[0, 2]
    b1 = B.filter((pl.col("exp") == "B1") & (pl.col("k") == 1))
    for j, reg in enumerate(["I", "III"]):
        s = b1.filter(pl.col("reg") == reg).group_by("a").agg((pl.col("k_cd") >= 1).mean().alias("p")).sort("a")
        ax.plot(s["a"], s["p"], "o-", color=[C1, C2][j], label=f"regime {reg}, loading sweep")
    b2 = B.filter((pl.col("exp").is_in(["B1", "B2"])) & (pl.col("k") == 1) & (pl.col("a") == 0.3) & (pl.col("reg") == "III"))
    s = b2.with_columns(pl.col("mult").fill_null(1.0)).group_by("mult").agg((pl.col("k_cd") >= 1).mean().alias("p")).sort("mult")
    ax.text(0.205, 0.42, "III, a = 0.3, counts ×", fontsize=6, color=INK2)
    for i, (m, p) in enumerate(zip(s["mult"], s["p"])):
        ax.text(0.205, 0.32 - 0.08 * i, f"×{m:g}: P = {p:.2f}", fontsize=6, color=C2)
    ax.set_xlabel("window loading a (one mode)"); ax.set_ylabel("P(k_cd ≥ 1)"); ax.set_ylim(-0.03, 1.03)
    ax.legend(loc="lower right", bbox_to_anchor=(1.0, 0.45))
    panel_label(ax, "c  Content modes")

    # (d) PR estimator bias vs n
    ax = axs[1, 0]
    c1 = C.filter(pl.col("exp") == "C1")
    for j, (est, lab) in enumerate([("pr", "bias-corrected PR"), ("pr_naive", "naive PR"), ("erank", "effective rank")]):
        for spec, par, ls in [("flat", 16.0, "-"), ("power", 12.0, "--")]:
            s = c1.filter((pl.col("est") == est) & (pl.col("spec") == spec) & (pl.col("par") == par)).sort("n")
            ax.plot(s["n"], s["mean"] / s["pr_true"], ls, color=[C1, C2, C3][j], label=lab if spec == "flat" else None)
    ax.axhline(1, color=INK2, lw=0.8, ls=":")
    ax.set_xscale("log"); ax.set_xlabel("statements n (d = 32)"); ax.set_ylabel("estimate / true PR")
    ax.legend(loc="lower right"); ax.text(11, 1.55, "solid: flat PR = 16\ndashed: power law PR = 12", fontsize=6, color=INK2)
    panel_label(ax, "d  PR estimators")

    # (e) between-agent PR vs number of agents
    ax = axs[1, 1]
    c3 = C.filter((pl.col("exp") == "C3") & (pl.col("rb") == 5) & (pl.col("k") == 15)).group_by("Na").agg(
        pl.col("pr_finite").mean(), pl.col("naive").mean(), pl.col("noise_corr").mean(), pl.col("full_corr").mean()).sort("Na")
    ax.plot(c3["Na"], c3["naive"], "o-", color=C2, label="naive (agent means)")
    ax.plot(c3["Na"], c3["noise_corr"], "o-", color=C1, label="noise-corrected (split quarters)")
    ax.plot(c3["Na"], c3["full_corr"], "o-", color=C3, label="+ finite-N correction")
    ax.plot(c3["Na"], c3["pr_finite"], color=INK2, lw=0.8, ls=":", label="truth for these N agents")
    ax.axhline(5, color=INK, lw=0.8, ls="--"); ax.text(21, 5.25, "population PR = 5", fontsize=6, color=INK)
    ax.set_ylim(0, 7.5)
    ax.set_xlabel("agents N"); ax.set_ylabel("between-agent PR"); ax.legend(loc="lower right", fontsize=5.6)
    panel_label(ax, "e  Between-agent PR vs N")

    # (f) kickoff design power
    ax = axs[1, 2]
    d1 = D.group_by("s_day", "drop").agg(pl.col("pass").mean().alias("power")).sort("s_day", "drop")
    for j, sd in enumerate([0.05, 0.10, 0.20]):
        s = d1.filter(pl.col("s_day") == sd)
        ax.plot(s["drop"] * 100, s["power"], "o-", color=[C1, C2, C3][j], label=f"day-to-day sd {sd:.0%}")
    ax.set_xlabel("true kickoff PR drop (%)"); ax.set_ylabel("P(P6 passes)"); ax.set_ylim(-0.03, 1.03)
    ax.legend(loc="lower right"); ax.text(0, 0.9, "22 kickoffs vs 90 placebos", fontsize=6, color=INK2)
    panel_label(ax, "f  Kickoff test power")

    fig.tight_layout()
    fig.savefig(L.FIG / "synthetic_validation.pdf")
    preview(fig, "synthetic_validation")
    plt.close(fig)
    print("wrote", L.FIG / "synthetic_validation.pdf")


def main():
    style()
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    L.FIG.mkdir(parents=True, exist_ok=True)
    if which in ("synthetic", "all"):
        fig_synthetic()
    if which in ("real", "summary", "all"):
        import figures_real
        figures_real.main(which)


if __name__ == "__main__":
    main()
