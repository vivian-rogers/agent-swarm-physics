"""H81 writeup visual: a collective slow mode in regime-I village content, carried across member turnover.

Builds fig.pdf / fig.png from data/processed/H81-culture-beyond-composition/:
  (a) top: the model, an Ornstein-Uhlenbeck culture direction with tau = 25 d (simulation);
      bottom: real regime-I membership of the weekly blocks (who carries the content), showing turnover;
  (b) cross-goal block similarity s(dt) vs lag (bge and gte) against the S0 composition-null band, with the OU fit;
  (c) the same for the turnover-disjoint similarity s_perp (only agents absent from the other block);
  (d) the card's contrasts vs their S0 95th percentiles (both models).
The S0 band per lag bin is recomputed here with H81's own synthetic (h81lib.simulate, the card's S0 world on the real
regime-I panel, 200 replicates per model; ~1 min). Real profiles are read from replication/pairs_<model>_I.parquet.
Usage: uv run python writeup/visuals/H81-culture-slow-mode/make.py
"""
from __future__ import annotations

import json
import os
import sys
import zlib
from pathlib import Path

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "writeup/visuals"))
sys.path.insert(0, str(ROOT / "hypotheses/H81-culture-beyond-composition/analysis"))
import vstyle as vs  # noqa: E402
import h81lib as L  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

D = ROOT / "data/processed/H81-culture-beyond-composition"
MODELS = {"bge_small": ("bge", "o", vs.C["blue"]), "gte_modernbert": ("gte", "s", vs.C["sky"])}
EDGES = (0, 14, 28, 56, 112, 1e9)
N_S0 = 200
COLS = ["b", "c", "dt", "J", "goal_sim", "s", "s_perp", "w"]


def real_pairs(model):
    return pl.read_parquet(D / f"replication/pairs_{model}_I.parquet").select(COLS).to_numpy()


def bin_x(T):
    """Weighted-mean lag of the pairs in each bin (x position of the bin)."""
    out = []
    for lo, hi in zip(EDGES[:-1], EDGES[1:]):
        m = (T[:, 2] > lo - (1e-9 if lo == 0 else 0)) & (T[:, 2] <= hi)
        out.append(float(np.average(T[m, 2], weights=T[m, 7])))
    return np.array(out)


def s0_profiles(model):
    ad, X, blocks = L.load(model, "style_resid", "I")
    P = L.projectors(model, "I", ad)
    pan = L.Panel(ad, blocks, P)
    sc = L.variance_scales(pan, X)
    kick = L.goal_kickoff(model, "I", np.unique(pan.goal))
    rng = np.random.default_rng(zlib.crc32(f"{model}|I|S0|visual".encode()))
    prof, profp = [], []
    for _ in range(N_S0):
        Xs = L.simulate(pan, sc, rng)
        A, B, R = L.agent_block_residuals(pan, Xs)
        T = L.pair_table(pan, A, B, R, kick)
        prof.append([p[2] for p in L.profile(T, 5, EDGES)])
        profp.append([p[2] for p in L.profile(T, 6, EDGES)])
    return np.array(prof), np.array(profp)


def membership():
    b = pl.read_parquet(D / "blocks.parquet").filter(pl.col("regime") == "I").sort("mid_day")
    return b


def panel_a(fig, sub):
    g = sub.subgridspec(2, 1, height_ratios=[0.7, 1.6], hspace=0.08)
    ax = fig.add_subplot(g[0])
    b = membership()
    t0, t1 = b["mid_day"].min() - 4, b["mid_day"].max() + 4
    rng = np.random.default_rng(7)
    t = np.arange(t0, t1, 1.0)
    u = np.zeros((len(t), 2)); tau = 25.0
    for k in range(1, len(t)):
        u[k] = u[k - 1] * np.exp(-1 / tau) + np.sqrt(1 - np.exp(-2 / tau)) * rng.standard_normal(2)
    ax.plot(t, u[:, 0], color=vs.INK, lw=1.0)
    ax.plot(t, u[:, 1], color=vs.MUTED, lw=0.8)
    ax.set_xlim(t0, t1); ax.set_yticks([]); ax.set_xticks([]); ax.grid(False)
    ax.set_ylim(u.min() - 0.3, u.max() + 2.2)
    ax.spines["left"].set_visible(False)
    ax.set_title("(a) slow mode, changing carriers", loc="left")
    ax.text(0.01, 0.97, r"model: OU culture direction, $\tau=25$ d (simulation)", transform=ax.transAxes,
            fontsize=5.5, color=vs.INK2, va="top")
    ax2 = fig.add_subplot(g[1])
    agents = sorted({a for m in b["members"].to_list() for a in m})
    first = {a: min(md for md, m in zip(b["mid_day"], b["members"]) if a in m) for a in agents}
    agents.sort(key=lambda a: first[a])
    for i, a in enumerate(agents):
        for md, m, nd in zip(b["mid_day"], b["members"], b["n_days"]):
            if a in m:
                ax2.add_patch(plt.Rectangle((md - 3, i - 0.4), 6, 0.8, color=vs.INK2, lw=0))
    ax2.set_xlim(t0, t1); ax2.set_ylim(len(agents) - 0.5, -0.5)
    ax2.set_yticks([]); ax2.grid(False)
    ticks = [np.datetime64(d) for d in ("2025-06-01", "2025-09-01", "2025-12-01")]
    tx = [(d - L.T0).astype(float) for d in ticks]
    ax2.set_xticks(tx, ["Jun 2025", "Sep 2025", "Dec 2025"], fontsize=6.5)
    ax2.set_ylabel(f"members ({len(agents)} agents)", fontsize=6)
    ax2.text(0.02, 0.03, "real: who is in each weekly block (regime I)", transform=ax2.transAxes, fontsize=5.5,
             color=vs.INK2, ha="left", va="bottom")


def main():
    vs.use()
    rep = json.loads((D / "replication/replication.json").read_text())
    r2 = json.loads((D / "round2/r2_results.json").read_text())
    fig = plt.figure(figsize=(vs.W["double"], 4.6))
    gs = fig.add_gridspec(2, 2, width_ratios=[1, 1], hspace=0.55, wspace=0.42)
    panel_a(fig, gs[0, 0])
    axb = fig.add_subplot(gs[0, 1]); axc = fig.add_subplot(gs[1, 0])
    for model, (short, mk, col) in MODELS.items():
        T = real_pairs(model)
        x = bin_x(T)
        pr = np.array([p[2] for p in L.profile(T, 5, EDGES)])
        prp = np.array([p[2] for p in L.profile(T, 6, EDGES)]); npp = np.array([p[3] for p in L.profile(T, 6, EDGES)])
        prim = rep["primary"][f"{model}/I"]
        assert np.allclose(pr, [p[2] for p in prim["profile"]]), "profile does not reproduce the card"
        S, Sp = s0_profiles(model)
        dx = 1.06 if short == "gte" else 0.94
        for ax, y, SS in ((axb, pr, S), (axc, prp, Sp)):
            lo, hi = np.nanquantile(SS, [0.025, 0.975], axis=0)
            if short == "bge":
                ax.fill_between(x, lo, hi, color=vs.NULL, alpha=0.6, lw=0, label="S0 composition null, 95%")
            else:
                ax.fill_between(x, lo, hi, color=vs.NULL, alpha=0.35, lw=0)
        tf = prim["tau_fit"]
        xx = np.linspace(1, 400, 300)
        axb.plot(xx, tf["A"] * np.exp(-xx / tf["tau_days"]) + tf["s_inf"], color=col, lw=0.9, ls="--", alpha=0.9)
        axb.scatter(x * dx, pr, marker=mk, s=16, color=col, zorder=3, edgecolor="white", lw=0.3,
                    label=f"{short}: τ = {tf['tau_days']:.0f} ± {tf['tau_se']:.0f} d")
        small = npp < 15
        axc.scatter((x * dx)[~small], prp[~small], marker=mk, s=16, color=col, zorder=3, edgecolor="white", lw=0.3,
                    label=short)
        axc.scatter((x * dx)[small], prp[small], marker=mk, s=16, facecolor="white", edgecolor=col, lw=0.8, zorder=3)
    for ax in (axb, axc):
        ax.set_xscale("log"); ax.set_xlim(4, 400)
        ax.set_xticks([7, 14, 28, 56, 112, 224], ["7", "14", "28", "56", "112", "224"])
        ax.minorticks_off()
        ax.axhline(0, color=vs.INK2, lw=0.5)
        ax.set_xlabel("lag between blocks (days)")
        ax.set_ylim(-0.32, 0.42)
    axb.set_ylabel("cosine similarity of\nblock culture residuals")
    axc.set_ylabel("cosine similarity\n(disjoint members only)")
    axb.legend(loc="upper right", fontsize=5.5, handlelength=1.2)
    axb.set_title("(b) similarity decays over weeks", loc="left")
    axc.legend(loc="upper right", fontsize=5.5, handlelength=1.2)
    axc.text(0.03, 0.03, "open: < 15 pairs in the bin", transform=axc.transAxes, fontsize=5.5, color=vs.INK2)
    axc.set_title("(c) turnover-disjoint members", loc="left")

    # (d) contrasts vs S0 q95
    ax = fig.add_subplot(gs[1, 1])
    rows = [("goal-adjusted $D$", "D_adjg", "primary"), ("+ overlap-adjusted", "D_adj", "primary"),
            ("turnover-disjoint", "D_near_perp", "primary"), ("disjoint, size-matched", "D_near_perp", "size"),
            ("operator dirs removed", None, "r2a")]
    for i, (name, key, src) in enumerate(rows):
        for j, (model, (short, mk, col)) in enumerate(MODELS.items()):
            if src == "primary":
                pm = rep["primary"][f"{model}/I"]; val, q = pm[key], pm["S0_q95"][key]
            elif src == "size":
                pm = rep["robustness"][f"{model}/I/size_matched_m4"]; val, q = pm[key], pm["S0"][key]["q95"]
            else:
                pm = r2["r2a"][model]["I"]; val, q = pm["D_adjg_operator_removed"], pm["S0_q95_operator_removed"]
            y = i + (j - 0.5) * 0.32
            ax.barh(y, q, height=0.26, color=vs.NULL, lw=0, label="S0 null, 0 to 95th pct" if i == 0 and j == 0 else None)
            ax.scatter(val, y, marker=mk, s=16, color=col, zorder=3, edgecolor="white", lw=0.3,
                       label=short if i == 0 else None)
    ax.set_yticks(range(len(rows)), [r[0] for r in rows], fontsize=6)
    ax.set_ylim(len(rows) - 0.5, -1.25)
    ax.axvline(0, color=vs.INK2, lw=0.5)
    ax.set_xlim(0, 0.32)
    ax.set_xlabel(r"near ($\leq$14 d) minus far contrast")
    ax.legend(loc="upper left", fontsize=5.5, ncol=3, handlelength=1.0, columnspacing=0.8, bbox_to_anchor=(0.0, 1.02))
    ax.set_title("(d) contrasts vs the null", loc="left")
    vs.save(fig, HERE / "fig")
    plt.close(fig)


if __name__ == "__main__":
    main()
