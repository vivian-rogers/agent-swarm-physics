"""H54 round-2 summary figure: (a) per-agent read-out pull vs lag (R3) with the in-flight arm; (b) own-kickoff
percentile per period, bge-small vs gte-modernbert (R5). Writes figures/round2.pdf/.png.
Usage: uv run python figures_r2.py
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import h54lib as L  # noqa: E402

C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e6e5e0"
plt.rcParams.update({"font.size": 8, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "legend.frameon": False})
R2 = L.OUT_BASE / "r2"
BINS = [(0, 30), (30, 120), (120, 600), (600, 1800), (1800, 3600)]


def main():
    fig, axs = plt.subplots(1, 2, figsize=(3.45, 1.75), gridspec_kw={"width_ratios": [1.2, 1]})
    ax = axs[0]
    for model, col, mk, lab in (("bge_small", C1, "o", "read, bge"), ("gte_modernbert", C3, "s", "read, gte")):
        D = pl.read_parquet(R2 / f"r3_deltas_{model}.parquet").filter(pl.col("delta").is_not_nan())
        rd = D.filter(pl.col("arm") == "read")
        x, y, e = [], [], []
        for lo, hi in BINS:
            s = rd.filter((pl.col("lag_s") >= lo) & (pl.col("lag_s") < hi))
            x.append(np.sqrt(lo * hi) if lo else 15.0); y.append(s["delta"].mean()); e.append(s["delta"].std() / np.sqrt(s.height))
        ax.errorbar(x, y, yerr=e, color=col, marker=mk, ms=3.2, lw=1.4, capsize=0, label=lab)
        inf = D.filter((pl.col("arm") == "inflight") & (pl.col("lag_s") < 30))
        ax.errorbar([float(inf["lag_s"].median())], [inf["delta"].mean()], yerr=[inf["delta"].std() / np.sqrt(inf.height)],
                    color=C2, marker="D" if model == "bge_small" else "v", ms=3.6, lw=0, elinewidth=1.2,
                    label="in flight (unread), " + ("bge" if model == "bge_small" else "gte"))
    ax.axhline(0, color=INK2, lw=0.7)
    ax.set_xscale("log")
    ax.set_xlabel("lag of first message after m (s)", fontsize=7)
    ax.set_ylabel("pull toward m, Δ", fontsize=7)
    ax.legend(fontsize=5.2, loc="upper right", handlelength=1.2)
    ax.text(-0.02, 1.08, "(a)", transform=ax.transAxes, fontsize=7.5, va="top")
    ax = axs[1]
    a = pl.read_parquet(L.OUT_BASE / "NE34" / "periods.parquet").select("goal_no", "pi")
    b = pl.read_parquet(L.OUT_BASE / "r2_gte" / "NE34" / "periods.parquet").select("goal_no", pl.col("pi").alias("pg"))
    d = a.join(b, on="goal_no")
    rng = np.random.default_rng(0)
    jx, jy = rng.uniform(-0.012, 0.012, d.height), rng.uniform(-0.012, 0.012, d.height)
    ax.plot([0, 1], [0, 1], color=INK2, lw=0.7, ls=":")
    ax.scatter(d["pi"].to_numpy() + jx, d["pg"].to_numpy() + jy, s=12, color=C1, edgecolor="white", lw=0.4, zorder=3)
    for g, x, y in zip(d["goal_no"].to_list(), d["pi"].to_list(), d["pg"].to_list()):
        if x < 0.75 or y < 0.75:
            ax.annotate(f"#{g}", (x, y), xytext=(3, 1), textcoords="offset points", fontsize=5.6, color=INK2)
    ax.set_xlabel("own-kickoff π, bge", fontsize=7)
    ax.set_ylabel("π, gte", fontsize=7)
    ax.set_xlim(-0.05, 1.08); ax.set_ylim(-0.05, 1.08)
    ax.text(-0.02, 1.08, "(b)", transform=ax.transAxes, fontsize=7.5, va="top")
    fig.tight_layout(pad=0.3, w_pad=0.8)
    out = L.HYP / "figures"
    fig.savefig(out / "round2.pdf", bbox_inches="tight")
    fig.savefig(out / "round2.png", dpi=180, bbox_inches="tight")


if __name__ == "__main__":
    main()
