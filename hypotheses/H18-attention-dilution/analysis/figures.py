"""H18 figures.

  uv run python hypotheses/H18-attention-dilution/analysis/figures.py

- figures/summary.pdf: one-page summary (6 panels + headline text)
- figures/synthetic.pdf: synthetic validation (A: recovery on village skeletons; B: timing / D1 vs D2)
- G<NN>/figures/curves.pdf: per-period P(r|k), O/E under M_const, S(k)
- NE42/figures/merge.pdf, NE15/figures/rooms.pdf
Colors: the first three categorical slots of the dataviz reference palette (blue, orange, aqua) = regime I contrast,
two-room era, #51. No dual axes.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from periods import PERIODS, REGIME_I, gname  # noqa: E402

ROOT = HERE.parents[2]
HYP = HERE.parent
DATA = ROOT / "data/processed/H18-attention-dilution"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#d9d8d4"
C_I, C_2R, C_51 = "#2a78d6", "#eb6834", "#1baf7a"
plt.rcParams.update({"font.size": 7.5, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5,
                     "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
                     "lines.linewidth": 1.2, "pdf.fonttype": 42})


def color(g):
    return C_I if g in REGIME_I else (C_51 if g == 51 else C_2R)


def load():
    F = {}
    for g in PERIODS:
        f = DATA / gname(g) / "fits.json"
        if f.exists():
            F[g] = json.loads(f.read_text())
    S = json.loads((DATA / "summary.json").read_text()) if (DATA / "summary.json").exists() else None
    return F, S


def legend_groups(ax, loc="best"):
    from matplotlib.lines import Line2D
    h = [Line2D([], [], color=C_I, lw=1.5, label="regime I (#24–#31)"),
         Line2D([], [], color=C_2R, lw=1.5, label="two-room era (#35–#44)"),
         Line2D([], [], color=C_51, lw=1.5, label="#51 (non-holdout)")]
    ax.legend(handles=h, loc=loc, fontsize=6.5)


def panel_oe(ax, F):
    for g, f in F.items():
        cv = [c for c in f["curves"] if c["n"] >= 30 and c["oe"] > 0]
        x = [c["kmean"] for c in cv]
        y = [c["oe"] for c in cv]
        ax.plot(x, y, "-o", color=color(g), ms=2.5, lw=0.9, alpha=0.85)
    xs = np.array([1, 100])
    ax.plot(xs, 2.0 * xs ** -1.0, ls="--", color=INK2, lw=0.8)
    ax.plot(xs, 1.2 * xs ** 0.0, ls=":", color=INK2, lw=0.8)
    ax.text(40, 2.0 / 40 * 1.15, "slope −1 (fixed budget)", fontsize=6, color=INK2, ha="center")
    ax.text(40, 1.32, "slope 0 (no budget)", fontsize=6, color=INK2, ha="center")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("k (messages pending at the talk turn)")
    ax.set_ylabel("observed / expected under M_const\n(agent×day propensities)")
    ax.set_title("a  Within-agent-day dilution of addressing", loc="left", fontsize=8, color=INK)
    legend_groups(ax, "lower left")


def panel_forest(ax, F, S):
    order = [g for g in PERIODS if g in F]
    y = np.arange(len(order))[::-1]
    for yi, g in zip(y, order):
        d1 = F[g]["D1"]
        b = d1["boot"]["beta"]
        ax.plot([b["lo"], b["hi"]], [yi, yi], color=color(g), lw=1.2)
        ax.plot(d1["beta"], yi, "o", color=color(g), ms=4)
        d2 = F[g].get("D2") or {}
        if "beta" in d2 and d2.get("boot") and d2["boot"].get("beta"):
            bb = d2["boot"]["beta"]
            ax.plot([bb["lo"], bb["hi"]], [yi - 0.3, yi - 0.3], color=INK2, lw=0.8)
            ax.plot(d2["beta"], yi - 0.3, "s", mfc="white", mec=INK2, ms=3.2)
    ax.axvline(0, color=INK2, lw=0.7); ax.axvline(1, color=INK2, lw=0.7, ls="--")
    ax.set_yticks(y); ax.set_yticklabels([gname(g) for g in order], fontsize=6)
    ax.set_xlabel("β̂  (uptake ∝ k^−β; 0 = no budget, 1 = fixed budget)")
    ax.set_title("b  β̂ per period: D1 (●) and timer-wake D2 (□)", loc="left", fontsize=8, color=INK)
    ax.set_xlim(-1.0, 2.0)
    if S:
        for lab, key, yy in (("pooled regime I", "pooled_regI", -1.3), ("pooled regime III", "pooled_regIII", -2.0)):
            p = S["P1"].get(key)
            if p:
                ax.plot([p["mean"] - 1.96 * p["se"], p["mean"] + 1.96 * p["se"]], [yy, yy], color=INK, lw=1.2)
                ax.plot(p["mean"], yy, "D", color=INK, ms=3.5)
                ax.text(1.95, yy, lab, fontsize=5.8, color=INK2, ha="right", va="center")
        ax.set_ylim(-2.6, len(order) - 0.4)


def panel_cv(ax, F):
    order = [g for g in PERIODS if g in F and F[g]["D1"].get("cv_block")]
    x = np.arange(len(order))
    for xi, g in zip(x, order):
        comp = F[g]["D1"]["cv_block"]["comp"]
        for off, key, mk in ((-0.18, "inv_vs_const", "o"), (0.18, "inv_vs_rec", "^")):
            m, lo, hi, _ = comp[key]
            ax.plot([xi + off, xi + off], [1000 * lo, 1000 * hi], color=color(g), lw=1.0)
            ax.plot(xi + off, 1000 * m, mk, color=color(g), ms=3.5, mfc=color(g) if mk == "o" else "white")
    ax.axhline(0, color=INK2, lw=0.7)
    ax.set_xticks(x); ax.set_xticklabels([gname(g) for g in order], rotation=90, fontsize=6)
    ax.set_ylabel("held-out Δℓ per unit ×10³\n(within-day blocks)")
    ax.set_title("c  1/k vs. constant (●) and vs. recency-only (△)", loc="left", fontsize=8, color=INK)


def panel_S(ax, F):
    for g, f in F.items():
        cv = [c for c in f["curves"] if c["n_talks"] >= 30 and c["S"] == c["S"]]
        ax.plot([c["kmean"] for c in cv], [c["S"] for c in cv], "-o", color=color(g), ms=2.5, lw=0.9, alpha=0.85)
    ax.set_xscale("log")
    ax.set_xlabel("k (messages pending at the talk turn)")
    ax.set_ylabel("pending senders addressed per talk turn (S)")
    ax.set_title("d  Total response per turn vs. k (flat = conserved budget)", loc="left", fontsize=8, color=INK)


def panel_N(ax, F, S, which):
    for g, f in F.items():
        v = f["p_bar"] if which == "p" else f["B_hat"]
        ax.plot(f["n_room_mean"], v, "o", color=color(g), ms=4)
        ax.annotate(gname(g)[1:], (f["n_room_mean"], v), fontsize=5, color=INK2, xytext=(2, 2), textcoords="offset points")
    seg = (F.get(51) or {}).get("segment_S") or []
    if seg:
        ax.plot([s["n_room"] for s in seg], [s["p_bar"] if which == "p" else s["B_hat"] for s in seg], "x", color=C_51,
                ms=3.5, label="#51 segments")
        ax.legend(fontsize=6, loc="best")
    ax.set_xlabel("mean room size N_room")
    if which == "p":
        ax.set_ylabel("per-pair addressing rate p̄")
        t = "e  Per-pair uptake vs. room size"
        if S:
            t += f" (ρ = {S['P9']['rho_p_N']:.2f})"
    else:
        ax.set_ylabel("senders addressed per talk turn B̂")
        t = "f  Budget per turn vs. room size"
        if S:
            t += f" (ρ = {S['P9']['rho_B_N']:.2f})"
    ax.set_title(t, loc="left", fontsize=8, color=INK)


def summary(F, S):
    fig = plt.figure(figsize=(11, 8.5))
    gs = fig.add_gridspec(3, 3, height_ratios=[1, 1, 0.42], hspace=0.62, wspace=0.38, left=0.07, right=0.98, top=0.92, bottom=0.04)
    panel_oe(fig.add_subplot(gs[0, 0]), F)
    panel_forest(fig.add_subplot(gs[0, 1]), F, S)
    panel_cv(fig.add_subplot(gs[0, 2]), F)
    panel_S(fig.add_subplot(gs[1, 0]), F)
    panel_N(fig.add_subplot(gs[1, 1]), F, S, "p")
    panel_N(fig.add_subplot(gs[1, 2]), F, S, "B")
    fig.suptitle("H18 · Attention dilution in the AI Village: exploratory round 1 (non-holdout, 16 goal periods)",
                 x=0.07, ha="left", fontsize=11, color=INK)
    tx = fig.add_subplot(gs[2, :]); tx.axis("off")
    if S:
        P = S
        lines = [
            f"P1 dilution: β̂ CI excludes 0 in {P['P1']['n_ci_excl0']}/{P['P1']['n_eligible']} periods; median β̂ {P['P1']['median_beta']:.2f}; "
            f"pooled regime I {P['P1']['pooled_regI']['mean']:.2f} ± {P['P1']['pooled_regI']['se']:.2f}, regime III {P['P1']['pooled_regIII']['mean']:.2f} ± {P['P1']['pooled_regIII']['se']:.2f} (I² {P['P1']['pooled']['I2']:.2f}).",
            f"P2 shape: near-literal budget (M_inv or M_sat with k₀ < 3) wins CV in {P['P2']['budget_like']}/{P['P2']['n']}; saturating (k₀ ≈ 3–8) {P['P2']['saturating']}; recency-only {P['P2']['rec']}; constant 0. "
            f"1/k beats recency-only in {P['P2']['inv_beats_rec_ci']}/{P['P2']['n']} (recency beats 1/k, CI: {P['P2']['rec_beats_inv_ci']}).",
            f"P3 Σ: pooled ε_S {P['P3']['pooled']['mean']:.2f} ± {P['P3']['pooled']['se']:.2f}.   P4 mentions: pooled e^γ {P['P4']['pooled_egamma']:.1f}; β_M − β_other {P['P4']['pooled_betaM_minus_beta']['mean']:.2f} ± {P['P4']['pooled_betaM_minus_beta']['se']:.2f}." if P['P4']['pooled_betaM_minus_beta'] else "",
            (f"P5 timer wakes (exogenous k): pooled β̂_D2 {P['P5']['pooled_D2']['mean']:.2f} ± {P['P5']['pooled_D2']['se']:.2f} vs D1 regime III {P['P5']['pooled_D1_regIII']['mean']:.2f}."
             if P["P5"]["pooled_D2"] else "P5: D2 underpowered."),
            "Post hoc: k adds held-out value at fixed recency rank in 5/16 periods (regime I; #51 with ρ̂ = 1.00, k₀ ≈ 7); engagement (i addressed j last turn) does not absorb β̂.",
            "Placebo fails 16/16: senders of messages the agent could not yet see are mentioned far above baseline (mentions partly mark ongoing exchanges).",
            f"Synthetic (axis F): β̂ recovered (1/k → 1.00 ± 0.03; const → 0.00 ± 0.04); reactive-timing constant agents fake β̂_D1 ≈ 0.78 with recency winning, D2 ≈ 0.",
        ]
        tx.text(0, 1, "\n".join(l for l in lines if l), va="top", fontsize=7.2, color=INK, family="DejaVu Sans")
    fig.savefig(HYP / "figures/summary.pdf")
    plt.close(fig)


def synthetic_fig():
    A = DATA / "synthetic/A.parquet"
    B = DATA / "synthetic/B.parquet"
    if not (A.exists() and B.exists()):
        return
    a = pl.read_parquet(A)
    b = pl.read_parquet(B)
    fig, axs = plt.subplots(1, 2, figsize=(9, 3.4))
    truth = {"const": 0, "pow0.5": 0.5, "sat3": None, "rec0.5": None, "inv": 1}
    rules = ["const", "pow0.5", "sat3", "rec0.5", "inv"]
    for i, r in enumerate(rules):
        sub = a.filter(pl.col("rule") == r)
        for j, p in enumerate(["G25", "G38", "G41", "G51"]):
            v = sub.filter(pl.col("period") == p)["beta"].to_numpy()
            axs[0].plot(np.full(len(v), i + (j - 1.5) * 0.12), v, "o", ms=2.5, color=[C_I, C_2R, C_2R, C_51][j], alpha=0.7)
        if truth[r] is not None:
            axs[0].plot([i - 0.3, i + 0.3], [truth[r]] * 2, color=INK, lw=1)
    axs[0].set_xticks(range(len(rules)))
    axs[0].set_xticklabels(["constant", "k^−0.5", "saturating\nk₀=3", "recency\nρ=0.5", "1/k"])
    axs[0].set_ylabel("β̂ (M_pow)")
    axs[0].set_title("A  Known rules on real skeletons (G25, G38, G41, G51)", loc="left", fontsize=8)
    sc = ["exo_const", "exo_inv", "exo_sat3", "exo_rec", "react_const", "react_inv"]
    labels = ["exo\nconst", "exo\n1/k", "exo\nsat", "exo\nrecency", "reactive\nconst", "reactive\n1/k"]
    m = b.filter(pl.col("variant") == "main")
    for i, s in enumerate(sc):
        sub = m.filter(pl.col("scenario") == s)
        for off, col, mk, fc in ((-0.15, "beta_D1", "o", C_2R), (0.15, "beta_D2w300", "s", "white")):
            v = sub[col].drop_nans().drop_nulls().to_numpy()
            axs[1].plot(np.full(len(v), i + off), v, mk, ms=3, mec=C_2R if mk == "o" else INK2,
                        mfc=fc if mk == "s" else C_2R, alpha=0.8)
    axs[1].axhline(0, color=INK2, lw=0.7); axs[1].axhline(1, color=INK2, lw=0.7, ls="--")
    axs[1].set_xticks(range(len(sc))); axs[1].set_xticklabels(labels)
    axs[1].set_ylabel("β̂")
    axs[1].set_title("B  Generative agents: D1 backlog (●) vs. D2 timer wakes, 300 s (□)", loc="left", fontsize=8)
    fig.tight_layout()
    fig.savefig(HYP / "figures/synthetic.pdf")
    plt.close(fig)


def period_figs(F):
    for g, f in F.items():
        fig, axs = plt.subplots(1, 3, figsize=(9, 2.8))
        cv = [c for c in f["curves"] if c["n"] >= 20 and c["oe"] > 0]
        x = [c["kmean"] for c in cv]

        def errs(key):
            v = np.array([c[key] for c in cv], float)
            lo = np.array([c[key + "_lo"] if c[key + "_lo"] is not None else np.nan for c in cv], float)
            hi = np.array([c[key + "_hi"] if c[key + "_hi"] is not None else np.nan for c in cv], float)
            return v, np.vstack([np.maximum(v - lo, 0), np.maximum(hi - v, 0)])

        for ax, key, yl in ((axs[0], "rate1", "P(addressed), senders with 1 pending msg"),
                            (axs[1], "oe", "obs / exp under M_const (agent×day)"),
                            (axs[2], "S", "pending senders addressed per talk")):
            v, e = errs(key)
            ok = ~np.isnan(v)
            ax.errorbar(np.array(x)[ok], v[ok], yerr=e[:, ok], fmt="-o", color=color(g), ms=3, lw=1, capsize=1.5)
            ax.set_xscale("log")
            ax.set_xlabel("k pending")
            ax.set_ylabel(yl, fontsize=6.5)
        b = f["D1"]["boot"]["beta"]
        axs[0].set_title(f"{gname(g)}: β̂ = {f['D1']['beta']:.2f} [{b['lo']:.2f}, {b['hi']:.2f}]", loc="left", fontsize=8)
        axs[1].set_yscale("log")
        fig.tight_layout()
        d = HYP / gname(g) / "figures"
        d.mkdir(parents=True, exist_ok=True)
        fig.savefig(d / "curves.pdf")
        plt.close(fig)


def spanning_figs(F):
    sp = DATA / "spanning.json"
    if not sp.exists():
        return
    S = json.loads(sp.read_text())
    m = S["merge"]["sides"]
    fig, axs = plt.subplots(1, 3, figsize=(8, 2.6))
    sides = ["G39", "G40", "G41"]
    for ax, key, yl in ((axs[0], "kbar", "mean k per talk turn"), (axs[1], "pbar", "per-pair addressing rate"),
                        (axs[2], "Sbar", "senders addressed per talk")):
        ax.plot(range(3), [m[s][key] for s in sides], "-o", color=C_2R, ms=4)
        ax.set_xticks(range(3)); ax.set_xticklabels(["#39\n2 rooms", "#40\nmerged", "#41\n2 rooms"])
        ax.set_ylabel(yl)
        ax.set_ylim(0, None)
    axs[0].set_title("Merged agents across the 05-04 merge / 05-11 split", loc="left", fontsize=8)
    fig.tight_layout()
    fig.savefig(HYP / "NE42/figures/merge.pdf")
    plt.close(fig)
    ne = S["ne15"]
    if ne:
        fig, axs = plt.subplots(1, 2, figsize=(7.5, 2.8))
        gs_ = list(ne)
        y = np.arange(len(gs_))[::-1]
        for yi, gp in zip(y, gs_):
            r = ne[gp]
            for off, key, mk in ((0.12, "effect_const", "o"), (-0.12, "effect_pow", "s")):
                ci_ = r.get(key + "_ci") or {}
                if ci_:
                    axs[0].plot([ci_["lo"], ci_["hi"]], [yi + off] * 2, color=C_2R if mk == "o" else INK2, lw=1)
                axs[0].plot(r[key], yi + off, mk, color=C_2R if mk == "o" else INK2, mfc="white" if mk == "s" else C_2R, ms=3.5)
            axs[1].plot(r["median_k_ratio"], r["median_p_ratio"], "o", color=C_2R, ms=4)
            axs[1].annotate(gp, (r["median_k_ratio"], r["median_p_ratio"]), fontsize=5.5, xytext=(2, 2), textcoords="offset points")
        axs[0].axvline(0, color=INK2, lw=0.7)
        axs[0].set_yticks(y); axs[0].set_yticklabels(gs_)
        axs[0].set_xlabel("small-room log uptake effect\nwithout k (●) / with k^−β (□)")
        lim = max(2, max(max(r["median_k_ratio"], r["median_p_ratio"]) for r in ne.values()) * 1.1)
        axs[1].plot([0, lim], [0, lim], ls="--", color=INK2, lw=0.8)
        axs[1].axhline(1, color=INK2, lw=0.6, ls=":")
        axs[1].set_xlabel("k̄ ratio (large / small room)")
        axs[1].set_ylabel("p̄ ratio (small / large room)")
        axs[0].set_title("Same-day room-size contrast (NE15 side and replications)", loc="left", fontsize=8)
        fig.tight_layout()
        fig.savefig(HYP / "NE15/figures/rooms.pdf")
        plt.close(fig)


if __name__ == "__main__":
    F, S = load()
    synthetic_fig()
    period_figs(F)
    spanning_figs(F)
    if S:
        summary(F, S)
    print("figures written")


def summary_obs(F, S):
    """figures/summary_obs.pdf (~4.3 x 2.6 in) for the one-page hypothesis summary."""
    fig, axs = plt.subplots(1, 2, figsize=(4.3, 2.6), gridspec_kw=dict(wspace=0.45, left=0.13, right=0.98, bottom=0.18, top=0.86))
    ax = axs[0]
    for g, f in F.items():
        cv = [c for c in f["curves"] if c["n"] >= 30 and c["oe"] > 0]
        ax.plot([c["kmean"] for c in cv], [c["oe"] for c in cv], "-", color=color(g), lw=0.8, alpha=0.85)
    xs = np.array([1, 100])
    ax.plot(xs, 2.0 * xs ** -1.0, ls="--", color=INK2, lw=0.7)
    ax.plot(xs, 1.3 * xs ** 0.0, ls=":", color=INK2, lw=0.7)
    ax.text(45, 0.06, "1/k", fontsize=5.5, color=INK2)
    ax.text(30, 1.45, "no budget", fontsize=5.5, color=INK2, ha="center")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("k pending at the talk turn", fontsize=6.5)
    ax.set_ylabel("observed / expected (no budget)", fontsize=6.5)
    ax.set_title("a  within agent-days", loc="left", fontsize=7)
    ax.tick_params(labelsize=5.5)
    ax = axs[1]
    for g, f in F.items():
        ax.plot(f["n_room_mean"], f["p_bar"], "o", color=color(g), ms=3)
    seg = (F.get(51) or {}).get("segment_S") or []
    ax.plot([s["n_room"] for s in seg], [s["p_bar"] for s in seg], "x", color=C_51, ms=3)
    ax.set_xlabel("mean room size", fontsize=6.5)
    ax.set_ylabel("per-pair addressing rate", fontsize=6.5)
    ax.set_title(f"b  across periods (ρ = {S['P9']['rho_p_N']:.2f})", loc="left", fontsize=7)
    ax.tick_params(labelsize=5.5)
    from matplotlib.lines import Line2D
    h = [Line2D([], [], color=C_I, lw=1.2, label="regime I"), Line2D([], [], color=C_2R, lw=1.2, label="two-room era"),
         Line2D([], [], color=C_51, lw=1.2, label="#51"), Line2D([], [], color=C_51, marker="x", lw=0, ms=3, label="#51 segments")]
    ax.legend(handles=h, fontsize=5, loc="upper right")
    fig.savefig(HYP / "figures/summary_obs.pdf")
    plt.close(fig)


if __name__ == "__main__":
    F, S = load()
    summary_obs(F, S)
