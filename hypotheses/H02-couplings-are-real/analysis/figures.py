"""H02 figures (small PDFs in ../figures/).

fig1_recovery.pdf  synthetic: P(leader ranked #1) and coupling AUC vs days, KI-1 vs EQ-PL, by leader strength
fig2_nulls.pdf     real (exploratory): fraction of significant couplings per chunk for the null hierarchy, mode I vs C
fig3_heldout.pdf   real: calibrated held-out z (M2 and M3 over M1 vs N1 surrogates) per chunk, mode I vs C
fig4_g26.pdf       real: net outgoing influence z-scores in #26 (elected leader DeepSeek-V3.2 marked)
fig5_meanfield.pdf H02-MF: Curie-Weiss beta*J0 per chunk vs N1 null; forward P(K) for #39
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data/processed/H02-couplings-are-real"
FIG = Path(__file__).resolve().parents[1] / "figures"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
BLUE_SEQ = {0.1: "#86b6ef", 0.2: "#3987e5", 0.3: "#1c5cab", 0.5: "#0d366b"}
MODE = {"I": "#2a78d6", "C": "#eb6834"}
plt.rcParams.update({"font.size": 8, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "lines.linewidth": 2,
                     "legend.frameon": False, "pdf.fonttype": 42})


def fig1():
    A = pl.read_parquet(DATA / "harness_A.parquet").filter(~pl.col("low_leader"))
    s = A.group_by("JL", "D").agg((pl.col("ki_rank") == 1).mean().alias("ki"), (pl.col("eq_rank") == 1).mean().alias("eq"),
                                  pl.col("ki_auc").mean().alias("kiauc"), pl.col("eq_auc").mean().alias("eqauc")).sort("JL", "D")
    fig, ax = plt.subplots(1, 2, figsize=(6.6, 2.6))
    for JL, c in BLUE_SEQ.items():
        d = s.filter(pl.col("JL") == JL)
        ax[0].plot(d["D"], d["ki"], "-o", color=c, ms=4, label=f"$J_L$={JL}")
        ax[0].plot(d["D"], d["eq"], "--", color=c, lw=1.2)
    ax[0].axvline(5, color=INK2, lw=0.8, ls=":"); ax[0].text(5, 1.05, "#45", color=INK2, fontsize=7, ha="center")
    ax[0].set_xscale("log"); ax[0].set_xticks([1, 2, 3, 5, 10, 20]); ax[0].set_xticklabels([1, 2, 3, 5, 10, 20])
    ax[0].set_ylim(0, 1.03); ax[0].set_xlabel("days of data (241 one-min bins/day, N = 18)")
    ax[0].set_ylabel("P(planted leader ranked #1)")
    ax[0].set_title("Leader ranked #1: KI-1 (solid) vs EQ-PL (dashed)", fontsize=8, color=INK, loc="left", pad=12)
    ax[0].legend(fontsize=6.5, loc="center right", bbox_to_anchor=(1.0, 0.45), ncol=2, columnspacing=0.8)
    d = s.filter(pl.col("JL") == 0.3)
    ax[1].plot(d["D"], d["kiauc"], "-o", color=MODE["I"], ms=4, label="KI-1 (directed)")
    ax[1].plot(d["D"], d["eqauc"], "-s", color=MODE["C"], ms=4, label="EQ-PL (undirected)")
    ax[1].axhline(0.5, color=INK2, lw=0.8, ls=":")
    ax[1].set_xscale("log"); ax[1].set_xticks([1, 2, 3, 5, 10, 20]); ax[1].set_xticklabels([1, 2, 3, 5, 10, 20])
    ax[1].set_ylim(0.45, 1.0); ax[1].set_xlabel("days of data"); ax[1].set_ylabel("AUC, coupling exists")
    ax[1].set_title("Edge recovery ($J_L$ = 0.3)", fontsize=8, color=INK, loc="left", pad=12); ax[1].legend(fontsize=7)
    fig.tight_layout(); fig.savefig(FIG / "fig1_recovery.pdf"); plt.close(fig)


def fig2():
    R = pl.read_parquet(DATA / "real_chunks.parquet")
    combos = [("naive_N0", "naive\nvs N0"), ("naive_N1", "naive\nvs N1"), ("block_N1", "KI-1 block\nvs N1"),
              ("box5_N1", "KI-5 block\nvs N1"), ("eq_N1", "EQ-PL block\nvs N1")]
    fig, axs = plt.subplots(1, 2, figsize=(6.6, 2.6), sharey=True)
    rng = np.random.default_rng(0)
    for ax, reg in zip(axs, ["I", "III"]):
        for k, (col, lab) in enumerate(combos):
            for m, dx in [("I", -0.15), ("C", 0.15)]:
                v = R.filter((pl.col("regime") == reg) & (pl.col("mode") == m))[f"{col}_frac_sig"].to_numpy()
                ax.scatter(k + dx + rng.uniform(-0.05, 0.05, v.size), v, s=14, color=MODE[m], edgecolor="white",
                           linewidth=0.5, label=f"mode {m}" if k == 0 else None, zorder=3)
                if v.size:
                    ax.hlines(np.median(v), k + dx - 0.1, k + dx + 0.1, color=INK, lw=1.2, zorder=4)
        ax.axhline(0.05, color=INK2, lw=0.8, ls=":")
        ax.set_xticks(range(len(combos))); ax.set_xticklabels([c[1] for c in combos], fontsize=6.5)
        ax.set_title(f"Regime {reg}", fontsize=8, color=INK, loc="left")
    axs[0].set_ylabel("fraction of couplings |z| > 1.96"); axs[0].legend(fontsize=7, loc="upper right")
    axs[0].text(4.45, 0.055, "5%", color=INK2, fontsize=6.5)
    fig.tight_layout(); fig.savefig(FIG / "fig2_nulls.pdf"); plt.close(fig)


def fig3():
    R = pl.read_parquet(DATA / "heldout_null.parquet").sort("regime", "mode", "chunk")
    R10 = pl.read_parquet(DATA / "heldout_null_b10_rIII.parquet").select("chunk", pl.col("z21").alias("z21_b10"))
    R = R.join(R10, on="chunk", how="left")
    fig, ax = plt.subplots(figsize=(6.6, 2.5))
    x = np.arange(R.height)
    cols = [MODE[m] for m in R["mode"]]
    ax.scatter(x - 0.12, R["z21"], s=26, marker="o", color=cols, edgecolor="white", linewidth=0.5, zorder=3,
               label="M2 (family + global mean field), 30-min null")
    ax.scatter(x + 0.12, R["z31"], s=26, marker="s", facecolor="white", edgecolor=cols, linewidth=1.2, zorder=3,
               label="M3 (pairwise J), 30-min null")
    m = R["z21_b10"].is_not_null().to_numpy()
    ax.scatter(x[m] - 0.12, R["z21_b10"].to_numpy()[m], s=22, marker="v", color=INK2, zorder=4,
               label="M2, 10-min null (regime III)")
    ax.axhline(0, color=INK2, lw=0.8); ax.axhline(2, color=INK2, lw=0.8, ls=":")
    split = int((R["regime"] == "I").sum()) - 0.5
    ax.axvline(split, color=GRID, lw=1.5)
    ax.text(split - 0.3, 8.3, "regime I", ha="right", color=INK2, fontsize=7)
    ax.text(split + 0.3, 8.3, "regime III", ha="left", color=INK2, fontsize=7)
    ax.set_xticks(x); ax.set_xticklabels([f"{c[1:3]}.{c[-1]}\n{m}" for c, m in zip(R["chunk"], R["mode"])], fontsize=6)
    ax.set_ylabel("z of held-out Δ log-lik\nvs block-shift surrogates")
    ax.set_xlabel("goal.chunk and mode (blue I = individual objectives, orange C = shared objective)", fontsize=7)
    ax.legend(fontsize=6.5, loc="upper left", ncol=1)
    ax.set_ylim(-3.5, 9.2)
    fig.tight_layout(); fig.savefig(FIG / "fig3_heldout.pdf"); plt.close(fig)


def fig4():
    I = pl.read_parquet(DATA / "real_influence.parquet").filter(pl.col("chunk") == "g26c0")
    roster = pl.read_parquet(ROOT / "data/processed/shared/roster.parquet").select("agent", "name")
    fig, axs = plt.subplots(1, 2, figsize=(6.6, 2.6), sharey=False)
    for ax, est, lab in zip(axs, ["block", "box5"], ["KI-1 block", "KI-5 block"]):
        d = I.filter(pl.col("est") == est).join(roster, on="agent").sort("zI")
        cols = [MODE["C"] if a == 17 else "#9ec5f4" for a in d["agent"]]
        ax.barh(np.arange(d.height), d["zI"], color=cols, height=0.7)
        ax.set_yticks(np.arange(d.height)); ax.set_yticklabels(d["name"], fontsize=6.5)
        ax.axvline(0, color=INK2, lw=0.8); ax.axvline(2, color=INK2, lw=0.6, ls=":"); ax.axvline(-2, color=INK2, lw=0.6, ls=":")
        ax.set_xlabel("z of net outgoing influence vs N1")
        ax.set_title(f"#26, {lab} (orange: DeepSeek-V3.2)", fontsize=7.5, color=INK, loc="left")
    fig.tight_layout(); fig.savefig(FIG / "fig4_g26.pdf"); plt.close(fig)


def fig5():
    C = pl.read_parquet(DATA / "mf_cw.parquet").sort("regime", "mode", "chunk")
    PK = pl.read_parquet(DATA / "mf_pk.parquet")
    fig, ax = plt.subplots(1, 2, figsize=(6.6, 2.6), gridspec_kw={"width_ratios": [1.6, 1]})
    x = np.arange(C.height)
    lo = C["bJ0_null_mean"] - 2 * C["bJ0_null_sd"]; hi = C["bJ0_null_mean"] + 2 * C["bJ0_null_sd"]
    ax[0].vlines(x, lo, hi, color=GRID, lw=5, label="N1 null ±2 sd")
    ax[0].scatter(x, C["bJ0"], s=24, color=[MODE[m] for m in C["mode"]], edgecolor="white", linewidth=0.5, zorder=3)
    split = int((C["regime"] == "I").sum()) - 0.5
    ax[0].axvline(split, color=GRID, lw=1.5); ax[0].axhline(0, color=INK2, lw=0.8)
    ax[0].text(split - 0.3, 0.6, "regime I", ha="right", color=INK2, fontsize=7)
    ax[0].text(split + 0.3, 0.6, "regime III", ha="left", color=INK2, fontsize=7)
    ax[0].set_xticks(x); ax[0].set_xticklabels([f"{c[1:3]}.{c[-1]}\n{m}" for c, m in zip(C["chunk"], C["mode"])], fontsize=5.5)
    ax[0].set_ylabel(r"Curie–Weiss $\beta J_0$ (within 30-min blocks)"); ax[0].set_ylim(-0.2, 0.68)
    ax[0].set_title("HH80: uniform equal-time coupling (blue I, orange C)", fontsize=8, color=INK, loc="left")
    ax[0].legend(fontsize=6.5, loc="upper left")
    ch = "g39c0"
    d = PK.filter(pl.col("chunk") == ch).sort("K")
    ax[1].bar(d["K"], d["obs"], color="#cde2fb", width=0.8, label="observed")
    ax[1].plot(d["K"], d["ind"], "-", color=INK2, lw=1.5, label="independent")
    ax[1].plot(d["K"], d["cw"], "--", color=MODE["C"], lw=1.5, label="Curie–Weiss")
    ax[1].set_yscale("log"); ax[1].set_ylim(1e-4, 0.3)
    ax[1].set_xlabel("K = active agents per minute"); ax[1].set_ylabel("P(K)")
    ax[1].set_title(f"Forward P(K), #39 (N = 15)", fontsize=8, color=INK, loc="left")
    ax[1].legend(fontsize=6.5, loc="upper left")
    fig.tight_layout(); fig.savefig(FIG / "fig5_meanfield.pdf"); plt.close(fig)


if __name__ == "__main__":
    import sys
    FIG.mkdir(exist_ok=True)
    for f in (sys.argv[1:] or ["fig1", "fig2", "fig3", "fig4", "fig5"]):
        globals()[f]()
        print("wrote", f)
