"""H42 cross-period figures from data/processed/H42-readout-hawkes-kernel/units.parquet.

  figures/summary_obs.pdf    (a) held-out cross gain per unit: read-out (world B) vs exponential (world A);
                             (b) n_cross by regime: world A's A, world B's B, world pr's B, with null levels
  figures/ncross_vs_N.pdf    per-pair weight and n_cross vs N (world B's B, world A's A)
  figures/kernels.pdf        B's call-index shape by regime; A's mean timescale vs read-out lag
  figures/activity.pdf       activity channel: visible vs invisible families, real vs shift null
Usage: uv run python hypotheses/H42-readout-hawkes-kernel/analysis/figures.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import h42lib as L  # noqa: E402

FIG = HERE.parent / "figures"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
REG = {"I": ("#2a78d6", "o"), "II": ("#eb6834", "s"), "III": ("#1baf7a", "^")}
FLOOR = 1e-3


def style(ax):
    ax.tick_params(labelsize=6.5, colors=INK2)
    ax.grid(color=GRID, lw=0.5)
    for s in ax.spines.values():
        s.set_color(GRID)


def summary_obs(df):
    cv = df.filter(pl.col("cv") == True)  # noqa: E712
    fig, axes = plt.subplots(1, 2, figsize=(4.8, 2.3), gridspec_kw={"width_ratios": [1, 1.2]})
    ax = axes[0]
    gA = (cv["A:A:cv"] - cv["A:S0:cv"]).to_numpy() * 1e3
    gB = (cv["B:B:cv"] - cv["B:S0:cv"]).to_numpy() * 1e3
    lim = [min(gA.min(), gB.min(), -1) * 1.1, max(gA.max(), gB.max(), 1) * 1.1]
    ax.axhline(0, color=INK2, lw=0.6); ax.axvline(0, color=INK2, lw=0.6)
    ax.plot(lim, lim, color=INK2, lw=0.6, ls=":")
    for g, (c, m) in REG.items():
        sel = cv["regime"].to_numpy() == g
        ax.scatter(gA[sel], gB[sel], s=16, marker=m, facecolor=c, edgecolor="white", lw=0.6, label=f"regime {g}", zorder=3)
    ax.set_xscale("symlog", linthresh=1); ax.set_yscale("symlog", linthresh=1)
    ax.set_xlabel("exponential cross gain, world A\n(mnats/event, held out)", fontsize=6.5, color=INK2)
    ax.set_ylabel("read-out cross gain, world B\n(mnats/event, held out)", fontsize=6.5, color=INK2)
    ax.set_title("(a) held-out gain over no-cross", fontsize=7, color=INK)
    ax.legend(fontsize=5.5, frameon=False, loc="lower right")
    style(ax)
    ax = axes[1]
    pm_path = L.DATA / "posthoc_mention.parquet"
    pm = pl.read_parquet(pm_path).select("unit_id", "per_named") if pm_path.exists() else None
    d2 = df.join(pm, on="unit_id", how="left") if pm is not None else df.with_columns(pl.lit(None).alias("per_named"))
    cols = [("A:A:nx", "A:A:shift_q95", "exponential\n(H03 world)"), ("B:B:nx", "B:B:shift_q95", "read-out\nall msgs"),
            ("per_named", None, "read-out\nnamed")]
    rng = np.random.default_rng(0)
    for k, (c, nq, lab) in enumerate(cols):
        for j, (g, (colr, m)) in enumerate(REG.items()):
            sub = d2.filter((pl.col("regime") == g) & pl.col(c).is_not_null())
            y = np.maximum(sub[c].to_numpy(), FLOOR)
            x = k + (j - 1) * 0.25 + rng.uniform(-0.06, 0.06, len(y))
            ax.scatter(x, y, s=9, marker=m, facecolor=colr, edgecolor="white", lw=0.4, zorder=3)
            if len(y):
                ax.plot([k + (j - 1) * 0.25 - 0.1, k + (j - 1) * 0.25 + 0.1], [np.median(y)] * 2, color=INK, lw=1.2, zorder=4)
                if nq is not None:
                    nqv = np.maximum(sub[nq].to_numpy(), FLOOR)
                    ax.plot([k + (j - 1) * 0.25 - 0.1, k + (j - 1) * 0.25 + 0.1], [np.median(nqv)] * 2, color=INK2,
                            lw=0.9, ls="--", zorder=4)
    ax.axhline(0.05, color="#e34948", lw=0.7, ls=":")
    ax.text(-0.45, 0.056, "field floor", fontsize=5.2, color=INK2, ha="left")
    ax.set_yscale("log")
    ax.set_xticks(range(len(cols))); ax.set_xticklabels([c[2] for c in cols], fontsize=5.6)
    ax.set_ylabel("extra talk per message", fontsize=6.5, color=INK2)
    ax.set_title("(b) cross-branching, regimes I/II/III", fontsize=7, color=INK)
    style(ax)
    fig.tight_layout(pad=0.3)
    fig.savefig(FIG / "summary_obs.pdf")
    plt.close(fig)


def ncross_vs_N(df):
    fig, axes = plt.subplots(1, 2, figsize=(5.2, 2.2))
    for ax, (c, lab) in zip(axes, [("B:B:nx", "world B, read-out B"), ("A:A:nx", "world A, exponential A")]):
        for g, (colr, m) in REG.items():
            sub = df.filter(pl.col("regime") == g)
            x = sub["n_agents"].to_numpy()
            y = np.maximum(sub[c].to_numpy(), FLOOR) / np.maximum(sub["rec_per_msg"].to_numpy(), 1)
            ax.scatter(x, y, s=12, marker=m, facecolor=colr, edgecolor="white", lw=0.5, label=f"regime {g}")
        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_xlabel("N (calling agents)", fontsize=6.5, color=INK2)
        ax.set_ylabel("per-pair weight", fontsize=6.5, color=INK2)
        ax.set_title(lab, fontsize=7)
        style(ax)
    axes[0].legend(fontsize=5.5, frameon=False)
    fig.tight_layout(pad=0.3)
    fig.savefig(FIG / "ncross_vs_N.pdf")
    plt.close(fig)


def kernels(df):
    fig, axes = plt.subplots(1, 2, figsize=(5.2, 2.2))
    ax = axes[0]
    for g, (colr, m) in REG.items():
        sub = df.filter((pl.col("regime") == g) & pl.col("B:B:B0").is_not_null() & (pl.col("B:B:nx") > 0.005))
        y = sub["B:B:B0"].to_numpy(); y1 = sub["B:B:B01"].to_numpy()
        ax.scatter(np.full(len(y), list(REG).index(g)) - 0.1, y, s=10, marker=m, facecolor=colr, edgecolor="white", lw=0.4)
        ax.scatter(np.full(len(y1), list(REG).index(g)) + 0.1, y1, s=10, marker=m, facecolor="white", edgecolor=colr, lw=0.8)
    ax.set_xticks(range(3)); ax.set_xticklabels([f"regime {g}" for g in REG], fontsize=6)
    ax.set_ylabel("share of B's cross mass", fontsize=6.5, color=INK2)
    ax.set_title("world B, units with $n_x$>0.005\nfilled: read-out call; open: calls 0-1", fontsize=6.5)
    style(ax)
    ax = axes[1]
    for g, (colr, m) in REG.items():
        sub = df.filter((pl.col("regime") == g) & pl.col("A:A:tau_A").is_not_null())
        ax.scatter(sub["lag_mean"].to_numpy(), sub["A:A:tau_A"].to_numpy(), s=12, marker=m, facecolor=colr,
                   edgecolor="white", lw=0.5, label=f"regime {g}")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.set_xlabel("mean read-out lag (s)", fontsize=6.5, color=INK2)
    ax.set_ylabel("A's mean timescale (s)", fontsize=6.5, color=INK2)
    ax.legend(fontsize=5.5, frameon=False)
    style(ax)
    fig.tight_layout(pad=0.3)
    fig.savefig(FIG / "kernels.pdf")
    plt.close(fig)


def activity(df):
    if "act:B:n_Bi" not in df.columns:
        return
    fig, ax = plt.subplots(figsize=(3.4, 2.3))
    fams = [("act:A:n_Av", "act:A:null_n_Av_max", "A visible"), ("act:A:n_Ai", "act:A:null_n_Ai_max", "A invisible"),
            ("act:B:n_Bv", "act:B:null_n_Bv_max", "B visible"), ("act:B:n_Bi", "act:B:null_n_Bi_max", "B invisible")]
    for k, (c, nc, lab) in enumerate(fams):
        y = np.maximum(df[c].to_numpy(), FLOOR); yn = np.maximum(df[nc].to_numpy(), FLOOR)
        ax.scatter(np.full(len(y), k) - 0.12, y, s=8, facecolor="#2a78d6", edgecolor="white", lw=0.4, label="real" if k == 0 else None)
        ax.scatter(np.full(len(yn), k) + 0.12, yn, s=8, facecolor="#eb6834", edgecolor="white", lw=0.4, label="shift null (max of 2)" if k == 0 else None)
    ax.set_yscale("log")
    ax.set_xticks(range(4)); ax.set_xticklabels([f[2] for f in fams], fontsize=6)
    ax.set_ylabel("activity $n_{cross}$ by source family", fontsize=6.5, color=INK2)
    ax.legend(fontsize=5.5, frameon=False)
    style(ax)
    fig.tight_layout(pad=0.3)
    fig.savefig(FIG / "activity.pdf")
    plt.close(fig)


def main():
    FIG.mkdir(exist_ok=True)
    df = pl.read_parquet(L.DATA / "units.parquet")
    summary_obs(df)
    ncross_vs_N(df)
    kernels(df)
    activity(df)
    print("figures written")


if __name__ == "__main__":
    main()
