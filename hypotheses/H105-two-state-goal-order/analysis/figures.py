"""H105 figures: figures/summary_obs.pdf (variance growth observed vs tilt-predicted across kickoff transitions;
G51 own-goal vs shared loop gain) and figures/synthetic_compact.pdf (identifiability of P1 and P2)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h105lib as L  # noqa: E402

FIG = Path(__file__).resolve().parents[1] / "figures"
C = {"blue": "#2a78d6", "orange": "#eb6834", "aqua": "#1baf7a", "grey": "#85847e"}
plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#52514e",
                     "xtick.color": "#52514e", "ytick.color": "#52514e"})


def obs():
    k = pl.read_parquet(L.DATA / "NE34/kickoffs.parquet").filter(pl.col("testable") & pl.col("growth_obs").is_finite()
                                                                 & pl.col("growth_pred").is_finite())
    pairs = {"K12", "K17", "K38"}
    fig, ax = plt.subplots(1, 2, figsize=(4.4, 2.0))
    for r in k.iter_rows(named=True):
        c = C["orange"] if r["design"] in pairs else C["blue"]
        ax[0].scatter(r["growth_pred"], r["growth_obs"], s=16, c=c, edgecolor="white", lw=0.5, zorder=3)
        if r["design"] in pairs:
            ax[0].annotate("#" + r["design"][1:], (r["growth_pred"], r["growth_obs"]), fontsize=6, xytext=(3, -6),
                           textcoords="offset points")
    lim = [-2.2, 5.6]
    ax[0].plot(lim, lim, color=C["grey"], lw=0.8, ls="--")
    ax[0].fill_between(lim, [v - np.log(1.5) for v in lim], [v + np.log(1.5) for v in lim], color="#e9e7e1", zorder=0)
    ax[0].set_xlim(lim); ax[0].set_ylim(lim)
    ax[0].set_xlabel("tilt-predicted ln(V_A / V_F)"); ax[0].set_ylabel("observed ln(V_A / V_F)")
    ax[0].scatter([], [], c=C["orange"], s=16, label="free → assigned"); ax[0].scatter([], [], c=C["blue"], s=16, label="other kickoffs")
    ax[0].legend(frameon=False, fontsize=6, loc="upper left")
    ax[0].set_title("(a) variance grows with p(1−p)", fontsize=7.5, loc="left")
    g = json.loads((L.DATA / "natives/G51.json").read_text())
    for j, (m, c) in enumerate((("bge_small", C["blue"]), ("gte_modernbert", C["aqua"]))):
        u = g[m]["units"]
        xs = np.arange(len(u)) + (j - 0.5) * 0.25
        ax[1].scatter(xs, [v["g_own"] for v in u], s=12, c=c, label=f"own ({m.split('_')[0]})", zorder=3)
        ax[1].scatter(xs, [v["g_shared"] for v in u], s=12, facecolor="white", edgecolor=c, lw=0.8, zorder=2)
    ax[1].axhline(0, color=C["grey"], lw=0.8)
    ax[1].set_xticks(np.arange(len(g["bge_small"]["units"])))
    ax[1].set_xticklabels([v["unit"] for v in g["bge_small"]["units"]], fontsize=5.5, rotation=90)
    ax[1].set_ylabel("two-state loop gain g₂"); ax[1].scatter([], [], facecolor="white", edgecolor=C["grey"], s=12, label="shared #51")
    ax[1].set_ylim(-0.6, 1.05); ax[1].legend(frameon=False, fontsize=5, loc="upper center", ncol=2, handletextpad=0.2, columnspacing=0.6)
    ax[1].set_title("(b) #51: private fields, g₂ ≈ 0", fontsize=7.5, loc="left")
    fig.tight_layout(pad=0.3)
    fig.savefig(FIG / "summary_obs.pdf"); fig.savefig(FIG / "summary_obs.png", dpi=200)


def synth():
    s = json.loads((L.DATA / "synthetic/results.json").read_text())["scenarios"]
    sc = ["H", "Hs", "R5", "R5s", "R2", "R6"]
    fig, ax = plt.subplots(1, 2, figsize=(4.4, 1.8))
    x = np.arange(len(sc))
    for i, k in enumerate(sc):
        ax[0].plot([i, i], [s[k]["rho_q10"], s[k]["rho_q90"]], color=C["blue"], lw=3, solid_capstyle="round")
        ax[0].scatter(i, s[k]["rho_median"], c="white", edgecolor=C["blue"], s=14, zorder=3)
    ax[0].axhspan(-np.log(1.5), np.log(1.5), color="#e9e7e1", zorder=0)
    ax[0].set_xticks(x); ax[0].set_xticklabels(sc, fontsize=6.5); ax[0].set_ylabel("ρ_V (10–90%)")
    ax[0].set_title("(a) P1 cannot tell H from R5", fontsize=7.5, loc="left")
    ax[1].bar(x, [s[k]["s_median"] for k in sc], 0.6, color=C["orange"])
    ax[1].axhline(1, color=C["grey"], ls="--", lw=0.8)
    ax[1].set_xticks(x); ax[1].set_xticklabels(sc, fontsize=6.5); ax[1].set_ylabel("median logit slope s")
    ax[1].set_title("(b) P2 slope: biased, but R2 ≈ 0", fontsize=7.5, loc="left")
    fig.tight_layout(pad=0.3)
    fig.savefig(FIG / "synthetic_compact.pdf"); fig.savefig(FIG / "synthetic_compact.png", dpi=200)


if __name__ == "__main__":
    obs(); synth()
