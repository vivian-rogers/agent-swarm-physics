"""H126 summary figure. Left: kickoff rate changes (P3) with 90% agent-bootstrap CIs and the synthetic k_on-only /
k_off-only reference points. Right: per-unit held-out occupancy ratio rho_p (P2) and shape statistic (P1) by regime.
Usage: uv run python hypotheses/H126-telegraph-goal-occupancy/analysis/figures.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
D = ROOT / "data/processed/H126-telegraph-goal-occupancy"
F = Path(__file__).resolve().parents[1] / "figures"


def main():
    kick = [k for k in json.loads((D / "results/kick.json").read_text()) if k.get("eligible")]
    units = [u for u in json.loads((D / "results/units.json").read_text()) if u.get("eligible")]
    des = pl.read_parquet(D / "designs.parquet")
    reg = dict(zip(des["design"], des["regime"]))
    syn = pl.read_parquet(D / "synthetic/segments.parquet").filter(pl.col("design") != "NE38")
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.8))
    for w, c, lab in (("WK1", "#0ca30c", "synthetic k_on only"), ("WK2", "#7a5195", "synthetic k_off only"),
                      ("WK0", "#aaaaaa", "synthetic no change")):
        s = syn.filter(pl.col("world") == w)
        ax[0].scatter(s["dln_a"], s["dln_b"], s=6, color=c, alpha=0.35, label=lab)
    for k in kick:
        col = {"k_on": "#0ca30c", "k_off": "#d03b3b"}.get(k["P3"], "#333333")
        ax[0].errorbar(k["dln_a"], k["dln_b"], xerr=[[k["dln_a"] - k["a_lo"]], [k["a_hi"] - k["dln_a"]]],
                       yerr=[[k["dln_b"] - k["b_lo"]], [k["b_hi"] - k["dln_b"]]], fmt="o", ms=3.5, color=col, lw=0.6)
        ax[0].annotate(k["design"][1:], (k["dln_a"], k["dln_b"]), fontsize=5.5, xytext=(2, 2), textcoords="offset points")
    ax[0].axhline(0, color="k", lw=0.5)
    ax[0].axvline(0, color="k", lw=0.5)
    ax[0].set_xlabel("Δ ln k_on (kickoff)")
    ax[0].set_ylabel("Δ ln k_off (kickoff)")
    ax[0].set_title("Which rate does a kickoff move?", fontsize=8)
    ax[0].legend(fontsize=5.5, frameon=False, loc="lower left")
    ax[0].set_xlim(-4, 6)
    ax[0].set_ylim(-7, 4)
    for n, u in enumerate(sorted(units, key=lambda x: (reg[x["design"]], x["design"]))):
        r = reg[u["design"]]
        col = {"I": "#5598e7", "II": "#fab219", "III": "#c43a3a"}[r]
        ax[1].scatter(n, u["rho_p"], color=col, s=10)
    ax[1].axhspan(-np.log(1.2), np.log(1.2), color="#0ca30c", alpha=0.12, label="±20%")
    ax[1].axhline(np.log(1.3), color="#d03b3b", lw=0.6, ls="--", label="±30% (kill)")
    ax[1].axhline(-np.log(1.3), color="#d03b3b", lw=0.6, ls="--")
    ax[1].set_xlabel("unit (regime I blue, II amber, III red)")
    ax[1].set_ylabel("ρ_p = ln(obs / pred) occupancy")
    ax[1].set_title("Held-out-day occupancy from dwells (P2)", fontsize=8)
    ax[1].legend(fontsize=6, frameon=False)
    for a in ax:
        a.tick_params(labelsize=7)
        a.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    F.mkdir(exist_ok=True)
    fig.savefig(F / "h126_obs.pdf")
    fig.savefig(F / "h126_obs.png", dpi=150)


if __name__ == "__main__":
    main()
