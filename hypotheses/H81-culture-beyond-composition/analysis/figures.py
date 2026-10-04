"""H81 figures (no text): summary_obs.pdf (pair similarity vs lag, regime I, real vs S0 band; D_adjg real vs null and
planted), summary_obsb.pdf (synthetic power by scenario; equal-time kappa per period).
Usage: uv run python hypotheses/H81-culture-beyond-composition/analysis/figures.py
"""
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
import h81lib as L  # noqa: E402

FIG = L.ROOT / "hypotheses/H81-culture-beyond-composition/figures"
C = {"bge_small": "#2a78d6", "gte_modernbert": "#eb6834"}
LAB = {"bge_small": "bge", "gte_modernbert": "gte"}
EDGES = (0, 14, 28, 56, 112, 300)
plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.6})


def profile_band(model, regime, reps=60):
    ad, X, blocks = L.load(model, "style_resid", regime)
    P = L.projectors(model, regime, ad); pan = L.Panel(ad, blocks, P)
    kick = L.goal_kickoff(model, regime, np.unique(pan.goal))
    A, B, R = L.agent_block_residuals(pan, X)
    real = [p[2] for p in L.profile(L.pair_table(pan, A, B, R, kick), edges=EDGES)]
    sc = L.variance_scales(pan, X); rng = np.random.default_rng(7)
    sims = []
    for _ in range(reps):
        Xs = L.simulate(pan, sc, rng)
        A2, B2, R2 = L.agent_block_residuals(pan, Xs)
        sims.append([p[2] for p in L.profile(L.pair_table(pan, A2, B2, R2, kick, disjoint=False), edges=EDGES)])
    sims = np.array(sims)
    return np.array(real), np.nanquantile(sims, 0.05, 0), np.nanquantile(sims, 0.95, 0)


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    rep = json.loads((L.OUT / "replication/replication.json").read_text())
    x = np.array([7, 21, 42, 84, 200])
    fig, ax = plt.subplots(1, 2, figsize=(6.6, 2.6), gridspec_kw={"width_ratios": [1.3, 1]})
    for k, m in enumerate(("bge_small", "gte_modernbert")):
        real, lo, hi = profile_band(m, "I")
        off = (k - 0.5) * 0.06
        ax[0].fill_between(x * np.exp(off), lo, hi, color=C[m], alpha=0.15, lw=0)
        ax[0].plot(x * np.exp(off), real, "-o", color=C[m], ms=4, lw=1.5, label=f"{LAB[m]} (band: S0 90%)")
    ax[0].axhline(0, color="#999", lw=0.5)
    ax[0].set_xscale("log"); ax[0].set_xticks(x); ax[0].set_xticklabels(["0–14", "14–28", "28–56", "56–112", ">112"])
    ax[0].set_xlabel("lag between blocks (days)"); ax[0].set_ylabel("cos of culture residuals")
    ax[0].set_title("(a) regime I, cross-goal block pairs", loc="left", fontsize=8)
    ax[0].legend(frameon=False, fontsize=7)
    # (b) D_adjg real vs S0 q95 and planted means
    labels, rv, q95, s1 = [], [], [], []
    for m in ("bge_small", "gte_modernbert"):
        syn = pl.read_parquet(L.OUT / f"synthetic/replicates_{m}.parquet")
        for r in ("I", "III"):
            p = rep["primary"][f"{m}/{r}"]
            labels.append(f"{LAB[m]} {r}"); rv.append(p["D_adjg"]); q95.append(p["S0_q95"]["D_adjg"])
            s1.append(float(syn.filter((pl.col("regime") == r) & (pl.col("scenario") == "S1_0.5"))["D_adjg"].mean()))
    yy = np.arange(len(labels))
    ax[1].barh(yy, q95, color="#cfcfcf", height=0.55, label="S0 95th pct")
    ax[1].scatter(s1, yy, marker="|", s=120, color="#555", label="planted s = 0.5 (mean)")
    ax[1].scatter(rv, yy, color=[C["bge_small"]] * 2 + [C["gte_modernbert"]] * 2, s=30, zorder=3, label="real")
    ax[1].set_yticks(yy); ax[1].set_yticklabels(labels); ax[1].invert_yaxis()
    ax[1].set_xlabel("slow-mode contrast D_adjg"); ax[1].set_title("(b) real vs null", loc="left", fontsize=8)
    ax[1].legend(frameon=False, fontsize=6.5, loc="upper center", bbox_to_anchor=(0.5, -0.32), ncol=3)
    fig.tight_layout(); fig.savefig(FIG / "summary_obs.pdf"); plt.close(fig)

    # obsb: (a) power of D_adjg and D_adj under S1/S2 (regime I, bge) with real; (b) kappa per period
    fig, ax = plt.subplots(1, 2, figsize=(6.6, 2.1))
    syn = pl.read_parquet(L.OUT / "synthetic/replicates_bge_small.parquet").filter(pl.col("regime") == "I")
    sc = ["S0", "S1_0.1", "S1_0.25", "S1_0.5", "S2_0.25", "S2_0.5"]
    q = {k: float(np.quantile(syn.filter(pl.col("scenario") == "S0")[k].to_numpy(), 0.95)) for k in ("D_adjg", "D_adj")}
    w = 0.38
    for j, (k, col) in enumerate((("D_adjg", "#2a78d6"), ("D_adj", "#1baf7a"))):
        pw = [float((syn.filter(pl.col("scenario") == s)[k].to_numpy() > q[k]).mean()) for s in sc]
        ax[0].bar(np.arange(len(sc)) + (j - 0.5) * w, pw, width=w - 0.04, color=col,
                  label={"D_adjg": "goal-adjusted (P2)", "D_adj": "goal + overlap (P3)"}[k])
    ax[0].axhline(0.8, color="#999", lw=0.5, ls="--")
    ax[0].set_xticks(range(len(sc))); ax[0].set_xticklabels(["S0", "S1\n.1", "S1\n.25", "S1\n.5", "S2\n.25", "S2\n.5"])
    ax[0].set_ylabel("pass rate (bge, regime I)"); ax[0].legend(frameon=False, fontsize=6.5)
    ax[0].set_title("(a) synthetic: culture (S1) vs drift (S2)", loc="left", fontsize=8)
    kap = pl.read_parquet(L.OUT / "replication/kappa.parquet").filter(pl.col("model") == "bge_small").sort("goal_no")
    for r, col in (("I", "#2a78d6"), ("III", "#eb6834")):
        d = kap.filter(pl.col("regime") == r)
        ax[1].errorbar(d["goal_no"], d["kappa"], yerr=1.96 * d["kappa_se"].fill_nan(0).to_numpy(), fmt="o", ms=3,
                       color=col, lw=0.8, label=f"regime {r}")
        ax[1].vlines(d["goal_no"], d["null_lo"], d["null_hi"], color="#bbb", lw=3, zorder=0)
    ax[1].axhline(0, color="#999", lw=0.5)
    ax[1].set_xlabel("goal period"); ax[1].set_ylabel("collective share κ (equal time)")
    ax[1].set_title("(b) κ per period (grey: sign-flip null)", loc="left", fontsize=8); ax[1].legend(frameon=False, fontsize=6.5)
    fig.tight_layout(); fig.savefig(FIG / "summary_obsb.pdf"); plt.close(fig)


if __name__ == "__main__":
    main()
