"""H86 summary figures: figures/summary_obs.pdf (a Taylor plot across agents; c_x raw vs trimmed per unit) and
figures/summary_obsb.pdf (NE14 daily c_x; shared share phi for talk vs activity).
Usage: uv run python hypotheses/H86-taylor-law-field-gauge/analysis/figures.py
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
import h86lib as L  # noqa: E402

INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
COL = {"I": "#2a78d6", "II": "#1baf7a", "III": "#eb6834"}
plt.rcParams.update({"font.size": 7.5, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False})
FIG = L.ROOT / "hypotheses/H86-taylor-law-field-gauge/figures"


def obs():
    b15 = pl.read_parquet(L.DATA / "bins15.parquet")
    g = pl.read_parquet(L.DATA / "replication/gauge.parquet")
    fig, ax = plt.subplots(1, 2, figsize=(4.2, 2.0))
    a = ax[0]
    for unit, col, lab in (("38a", "#eb6834", "38a activity"), ("51c", "#2a78d6", "51c activity")):
        Y, days, _ = L.matrix(b15.filter((pl.col("unit_id") == unit) & pl.col("trim")), "activity")
        mu, V = np.nanmean(Y, 0), np.nanvar(Y, 0, ddof=1)
        a.scatter(mu, V, s=10, color=col, edgecolor="white", linewidth=0.4, label=lab, zorder=3)
    xs = np.array([4, 120])
    m0 = 30.0
    v0 = 150.0
    a.plot(xs, v0 * (xs / m0), color=MUTED, lw=0.8, ls="--", label="$b=1$")
    a.plot(xs, v0 * (xs / m0) ** 2, color=MUTED, lw=0.8, ls=":", label="$b=2$")
    a.set_xscale("log"); a.set_yscale("log")
    a.set_xlabel("agent mean $\\mu_i$ (records / 15 min)"); a.set_ylabel("variance $V_i$")
    a.legend(fontsize=5.8, loc="upper left", handletextpad=0.2)
    a.set_title("(a) trimmed, per agent", fontsize=7, loc="left")
    a.grid(color=GRID, lw=0.5, which="both"); a.set_axisbelow(True)
    b = ax[1]
    w = g.filter(pl.col("channel") == "activity").pivot(on="grid", index=["unit_id", "regime"], values="c_x").drop_nulls()
    for r in ("I", "II", "III"):
        s = w.filter(pl.col("regime") == r)
        b.scatter(np.clip(s["raw"], 1e-4, None), np.clip(s["trim"], 1e-4, None), s=10, color=COL[r], edgecolor="white",
                  linewidth=0.4, label=f"regime {r}", zorder=3)
    lim = [1e-4, 3]
    b.plot(lim, lim, color=MUTED, lw=0.6)
    b.plot(lim, [x * 0.25 for x in lim], color=MUTED, lw=0.6, ls="--")
    b.text(0.9, 0.12, "75%\nremoved", fontsize=5.8, color=MUTED, va="center", ha="center")
    b.set_xscale("log"); b.set_yscale("log"); b.set_xlim(lim); b.set_ylim(lim)
    b.set_xlabel("$c_\\times$ raw grid"); b.set_ylabel("$c_\\times$ trimmed grid")
    b.legend(fontsize=5.8, loc="upper left", handletextpad=0.2)
    b.set_title("(b) shared-field coefficient per unit", fontsize=7, loc="left")
    fig.tight_layout(pad=0.3)
    fig.savefig(FIG / "summary_obs.pdf")


def obsb():
    d = pl.read_parquet(L.DATA / "replication/daily.parquet").filter(
        (pl.col("channel") == "activity") & pl.col("unit_id").is_in(["35", "36a", "36b", "36c", "37"]))
    w = d.pivot(on="grid", index=["unit_id", "pt_date"], values="c_x").sort("pt_date")
    g = pl.read_parquet(L.DATA / "replication/gauge.parquet").filter(pl.col("grid") == "trim")
    fig, ax = plt.subplots(1, 2, figsize=(4.2, 2.0))
    a = ax[0]
    x = np.arange(w.height)
    a.plot(x, np.clip(w["raw"], 1e-4, None), "o-", color="#2a78d6", ms=3, lw=1, label="raw")
    a.plot(x, np.clip(w["trim"], 1e-4, None), "s-", color="#eb6834", ms=3, lw=1, label="trimmed")
    a.axvline(list(w["unit_id"]).index("36b") - 0.5, color=MUTED, lw=0.8, ls="--")
    a.text(list(w["unit_id"]).index("36b") - 0.4, 1.5, "NE14", fontsize=6, color=MUTED)
    a.set_yscale("log"); a.set_ylim(1e-4, 5)
    a.set_xticks(x); a.set_xticklabels([s[5:] for s in w["pt_date"]], rotation=90, fontsize=5.5)
    a.set_ylabel("daily $c_\\times$ (activity)")
    a.legend(fontsize=6, loc="upper left", handletextpad=0.2)
    a.set_title("(a) regime II $\\to$ III", fontsize=7, loc="left")
    b = ax[1]
    p = g.pivot(on="channel", index=["unit_id", "regime"], values="phi").drop_nulls(["activity", "msg"])
    for r in ("I", "II", "III"):
        s = p.filter(pl.col("regime") == r)
        b.scatter(s["activity"], s["msg"], s=10, color=COL[r], edgecolor="white", linewidth=0.4, label=f"regime {r}", zorder=3)
    b.plot([-0.2, 1], [-0.2, 1], color=MUTED, lw=0.6)
    b.set_xlim(-0.2, 0.8); b.set_ylim(-0.2, 1.0)
    b.set_xlabel("$\\varphi$ activity (trimmed)"); b.set_ylabel("$\\varphi$ messages (trimmed)")
    b.legend(fontsize=5.8, loc="upper left", handletextpad=0.2)
    b.set_title("(b) shared share $\\varphi$", fontsize=7, loc="left")
    fig.tight_layout(pad=0.3)
    fig.savefig(FIG / "summary_obsb.pdf")


if __name__ == "__main__":
    FIG.mkdir(parents=True, exist_ok=True)
    obs(); obsb()
