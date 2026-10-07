"""H141 figures: synthetic recovery and the real-data summary (per-unit anisotropy ratio against the random-plane band,
subspace autocorrelation profiles, day-scale persistence).

    uv run python hypotheses/H141-easy-plane-anisotropy/analysis/figures.py [--synthetic-only]
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import json  # noqa: E402
import pickle  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h141lib as L  # noqa: E402

FIG = HERE.parent / "figures"
BLUE, RED, GRAY = "#2a78d6", "#d03b3b", "#8a8a8a"
plt.rcParams.update({"font.size": 7, "axes.titlesize": 7, "axes.labelsize": 7, "legend.fontsize": 6})


def synthetic():
    d = pl.read_parquet(L.DATA / "synthetic/runs.parquet")
    worlds = ["W-iso", "W-easy", "W-hard", "W-modes", "W-drive"]
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.5))
    for k, w in enumerate(worlds):
        q = d.filter(pl.col("world") == w)
        lr = np.log(q["rho"].to_numpy())
        ax[0].scatter(np.full(len(lr), k) + np.random.default_rng(k).uniform(-0.25, 0.25, len(lr)), lr, s=2,
                      color=BLUE, alpha=0.4)
        ax[0].hlines(q["truth"][0], k - 0.35, k + 0.35, color=RED, lw=1.2)
        pdiff = q["vg_P_diff"].to_numpy()
        ax[1].scatter(np.full(len(pdiff), k) + np.random.default_rng(k).uniform(-0.25, 0.25, len(pdiff)), pdiff, s=2,
                      color=BLUE, alpha=0.4)
    for a_ in ax:
        a_.set_xticks(range(len(worlds)))
        a_.set_xticklabels(worlds)
        a_.axhline(0, color="k", lw=0.5)
    ax[0].axhspan(np.log(1 / 3), np.log(3), color=GRAY, alpha=0.15, lw=0)
    ax[0].set_ylabel("ln ρ_A (call clock)")
    ax[0].set_title("(a) anisotropy ratio; red = planted", loc="left")
    ax[1].set_ylim(-1.5, 1.5)
    ax[1].set_ylabel("P_∥(1) − P_⊥(1) (clipped ±1.5)")
    ax[1].set_title("(b) day-scale variogram contrast (A1)", loc="left")
    fig.tight_layout()
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / "synthetic.pdf")
    fig.savefig(FIG / "synthetic.png", dpi=150)


def real():
    full = pickle.loads((L.DATA / "results/units.pkl").read_bytes())
    rows = sorted([r for k, r in full.items() if k.startswith("bge_small|style_resid_period|")],
                  key=lambda r: (r["goal"], r["unit"]))
    fig, ax = plt.subplots(1, 3, figsize=(7.0, 2.6), gridspec_kw={"width_ratios": [1.0, 1.6, 1.2]})
    # (a) profiles for the largest shared-goal unit and the largest #51 unit
    for u, col in (("38a", BLUE), ("51g", RED)):
        r = next((x for x in rows if x["unit"] == u), None)
        if r is None:
            continue
        t = np.array(r["C_tau"])
        cp, cq = np.array(r["C_par"]), np.array(r["C_perp"])
        ax[0].plot(t, cp / cp[0], "o-", color=col, ms=2.5, lw=0.8, label=f"{u} along E")
        ax[0].plot(t, cq / cq[0], "s--", color=col, ms=2.5, lw=0.8, label=f"{u} across E")
    ax[0].set_xscale("log")
    ax[0].axhline(0, color="k", lw=0.5)
    ax[0].set_xlabel("lag (own calls)")
    ax[0].set_ylabel("C_P(τ) / C_P(1–3)")
    ax[0].set_title("(a) subspace autocorrelation", loc="left")
    ax[0].legend(frameon=False)
    # (b) per-unit ln rho with 90% CI and the random-plane 5-95% band
    x = np.arange(len(rows))
    for k, r in enumerate(rows):
        q = r["rand_rho_q"]
        ax[1].vlines(k, np.log(q[0]), np.log(q[3]), color=GRAY, lw=4, alpha=0.4)
        lr = np.log(r["rho"]) if r["rho"] > 0 else np.nan
        ci = r.get("ci90", [np.nan, np.nan])
        col = BLUE if r["testable"] else GRAY
        ax[1].errorbar(k, lr, yerr=[[lr - np.log(max(ci[0], 1e-3))], [np.log(max(ci[1], 1e-3)) - lr]], fmt="o",
                       color=col, ms=3, lw=0.8)
    ax[1].axhspan(np.log(1 / 3), np.log(3), color=GRAY, alpha=0.12, lw=0)
    ax[1].axhline(np.log(10), color=RED, lw=0.6, ls=":")
    ax[1].set_xticks(x)
    ax[1].set_xticklabels([r["unit"] for r in rows], rotation=90)
    ax[1].set_ylabel("ln ρ_A (text plane)")
    ax[1].set_title("(b) ρ_A per unit; gray bar = random planes 5–95%", loc="left")
    # (c) day-scale persistence along vs across
    for r in rows:
        if r.get("vg_P_par") is None or not r["testable"]:
            continue
        ax[2].plot(r["vg_P_perp"], r["vg_P_par"], "o", color=RED if r["goal"] == 51 else BLUE, ms=3)
        ax[2].annotate(r["unit"], (r["vg_P_perp"], r["vg_P_par"]), fontsize=5, xytext=(2, 2), textcoords="offset points")
    lim = [-0.1, 0.8]
    ax[2].plot(lim, lim, color="k", lw=0.5)
    ax[2].set_xlabel("P_⊥(1) across E")
    ax[2].set_ylabel("P_∥(1) along E")
    ax[2].set_title("(c) day persistence (variogram, A1)", loc="left")
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs.pdf")
    fig.savefig(FIG / "summary_obs.png", dpi=150)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--synthetic-only", action="store_true")
    a = ap.parse_args()
    synthetic()
    if not a.synthetic_only:
        real()


if __name__ == "__main__":
    main()
