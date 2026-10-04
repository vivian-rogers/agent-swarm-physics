"""H97 figures: figures/summary_obs.pdf (kickoff vs placebo memory; forgetting along k vs transverse) and
figures/synthetic_compact.pdf (P1 false-positive/power, beta vs rho; intercept test by scenario)."""
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
import h97lib as L  # noqa: E402

FIG = Path(__file__).resolve().parents[1] / "figures"
C = {"I": "#2a78d6", "II": "#eda100", "III": "#eb6834", "grey": "#85847e", "ink": "#0b0b0b", "aqua": "#1baf7a"}
plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#52514e",
                     "axes.labelcolor": "#0b0b0b", "xtick.color": "#52514e", "ytick.color": "#52514e"})


def obs():
    d = pl.read_parquet(L.DATA / "NE34/transitions_all_configs.parquet").filter(
        (pl.col("cfg") == "primary") & pl.col("same_regime") & (pl.col("N") >= 5) & (pl.col("n_placebo") > 0)).sort("p")
    fig, ax = plt.subplots(1, 2, figsize=(4.4, 2.0))
    x = np.arange(d.height)
    for i, r in enumerate(d.iter_rows(named=True)):
        ax[0].plot([i, i], [r["rho_full"], r["rho0_full"]], color="#c3c2b7", lw=1.2, zorder=1)
    ax[0].scatter(x, d["rho0_full"], s=14, facecolor="white", edgecolor=C["grey"], lw=1, zorder=2, label="placebo day")
    ax[0].scatter(x, d["rho_full"], s=14, c=[C[r] for r in d["regime"]], zorder=3, label="kickoff")
    ax[0].set_xticks(x); ax[0].set_xticklabels([str(p) for p in d["p"]], fontsize=5.5, rotation=90)
    ax[0].set_ylabel("memory ρ (cross-agent)"); ax[0].set_xlabel("kickoff of goal period #")
    ax[0].set_ylim(0, 1); ax[0].legend(frameon=False, fontsize=6, loc="lower left")
    ax[0].set_title("(a) kickoff erases position", fontsize=7.5, loc="left")
    ax[1].scatter(d["drho_perp"], d["drho_par"], s=14, c=[C[r] for r in d["regime"]], edgecolor="white", lw=0.5)
    lim = [-0.2, 1.1]
    ax[1].plot(lim, lim, color=C["grey"], lw=0.8, ls="--")
    ax[1].axhline(0, color="#e9e7e1", lw=0.8, zorder=0); ax[1].axvline(0, color="#e9e7e1", lw=0.8, zorder=0)
    ax[1].set_xlim(lim); ax[1].set_ylim(lim)
    ax[1].set_xlabel("extra forgetting ⊥ k̂  (Δρ⊥)"); ax[1].set_ylabel("extra forgetting ∥ k̂  (Δρ∥)")
    ax[1].set_title("(b) stronger along the kickoff", fontsize=7.5, loc="left")
    for reg in ("I", "II", "III"):
        ax[1].scatter([], [], c=C[reg], s=14, label=f"regime {reg}")
    ax[1].legend(frameon=False, fontsize=6, loc="lower right")
    fig.tight_layout(pad=0.3)
    fig.savefig(FIG / "summary_obs.pdf"); fig.savefig(FIG / "summary_obs.png", dpi=200)


def synth():
    s = json.loads((L.DATA / "synthetic/results_main.json").read_text())["scenarios"]
    sc = ["H", "Hn", "Hweak", "R0", "R1", "R2", "R4", "R5", "R6"]
    fig, ax = plt.subplots(1, 2, figsize=(4.4, 1.9))
    x = np.arange(len(sc)); w = 0.38
    ax[0].bar(x - w / 2, [s[f"{k}|white"]["p1"] for k in sc], w, color=C["grey"], label="slope β")
    ax[0].bar(x + w / 2, [s[f"{k}|white"]["p1_rho"] for k in sc], w, color=C["I"], label="correlation ρ")
    ax[0].set_xticks(x); ax[0].set_xticklabels(sc, fontsize=6, rotation=45)
    ax[0].set_ylabel("P1 pass rate"); ax[0].set_ylim(0, 1.35); ax[0].set_yticks([0, 0.5, 1]); ax[0].legend(frameon=False, fontsize=6, ncol=2, loc="upper center")
    ax[0].set_title("(a) P1: ρ is calibrated under R0", fontsize=7.5, loc="left")
    ax[1].bar(x, [s[f"{k}|center"]["p3_over"] for k in sc], 0.6, color=C["III"])
    ax[1].set_xticks(x); ax[1].set_xticklabels(sc, fontsize=6, rotation=45)
    ax[1].set_ylabel("intercept a > 0 flagged"); ax[1].set_ylim(0, 1)
    ax[1].set_title("(b) P3 intercept (centered)", fontsize=7.5, loc="left")
    fig.tight_layout(pad=0.3)
    fig.savefig(FIG / "synthetic_compact.pdf"); fig.savefig(FIG / "synthetic_compact.png", dpi=200)


if __name__ == "__main__":
    obs(); synth()
