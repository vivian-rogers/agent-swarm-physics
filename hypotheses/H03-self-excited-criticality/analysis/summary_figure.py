"""Two-panel observables figure for the H03 one-page summary (plots existing results only; no recomputation).

(a) Primary branching ratio n-hat (TALK, M1 with baseline B2 + exogenous drive) per non-holdout goal period vs mean
    active agents N, by coupling mode, with the day-bootstrap CI (profile CI for periods under 3 days).
(b) Fast (tau <= 300 s) cross-agent excitation n_cross from M3, real vs the mean of the 5 agent-shift surrogates.

Reads data/processed/H03-self-excited-criticality/{period_table,jitter_table}.parquet and summary.json.
Usage: uv run python hypotheses/H03-self-excited-criticality/analysis/summary_figure.py
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
DATA = ROOT / "data/processed/H03-self-excited-criticality"
FIG = Path(__file__).resolve().parents[1] / "figures"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
MODE = {"C": ("#eb6834", "o", "shared objective (C)"), "F": ("#2a78d6", "s", "free / holiday (F)"),
        "other": ("#9a9993", "^", "other (I, K, M)"), "P": ("#0b0b0b", "*", "#51 private roles")}
FIGSIZE = (3.4, 1.7)  # one RevTeX column, printed 1:1 (the page caps the figure at 1.7 in tall)
plt.rcParams.update({"font.size": 5.8, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.4, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.titlesize": 6.3, "axes.titleweight": "bold", "pdf.fonttype": 42,
                     "xtick.labelsize": 5.4, "ytick.labelsize": 5.4, "axes.labelsize": 5.8, "axes.linewidth": 0.6,
                     "xtick.major.size": 2, "ytick.major.size": 2, "xtick.major.pad": 1.5, "ytick.major.pad": 1.5,
                     "axes.titlepad": 3, "axes.labelpad": 1.5})


def mkey(m):
    return m if m in ("C", "F", "P") else "other"


def main():
    t = pl.read_parquet(DATA / "period_table.parquet").filter(pl.col("set") == "TALK")
    j = pl.read_parquet(DATA / "jitter_table.parquet").filter(pl.col("set") == "TALK")
    s = json.loads((DATA / "summary.json").read_text())
    rho = s["primary_M1_B2"]["TALK"]["spearman_n_logN"]
    rho = rho[0] if isinstance(rho, (list, tuple)) else rho
    sh = s["jitter"]["TALK"]["n_cross_fast300_shift"]

    fig, ax = plt.subplots(1, 2, figsize=FIGSIZE, gridspec_kw={"width_ratios": [1.3, 1]})

    # (a) n-hat vs N
    a = ax[0]
    for r in t.iter_rows(named=True):
        k = mkey(r["mode"]); col, mk, _ = MODE[k]
        lo, hi = (r["n_boot_lo"], r["n_boot_hi"]) if r["n_boot_lo"] is not None else (r["n_prof_lo"], r["n_prof_hi"])
        hi = min(hi, 1.1) if np.isfinite(hi) else 1.1
        a.plot([r["N_active"]] * 2, [lo, hi], color=col, lw=0.45, alpha=0.5, zorder=2)
        a.plot(r["N_active"], r["n"], mk, color=col, ms=4.5 if k == "P" else 2.6, mec="white", mew=0.25, zorder=3)
    a.axhline(1.0, color=INK, lw=0.8, ls="--")
    a.text(30, 1.02, "critical, n = 1", fontsize=5, ha="right", va="bottom", color=INK)
    a.axhline(0.7, color=MODE["C"][0], lw=0.8, ls=":")
    a.text(30, 0.67, "predicted C median ≥ 0.7", fontsize=4.9, ha="right", va="top", color=MODE["C"][0])
    a.set_xscale("log")
    a.set_xticks([4, 7, 10, 15, 25]); a.set_xticklabels(["4", "7", "10", "15", "25"])
    a.minorticks_off()
    a.set_xlim(3.1, 32); a.set_ylim(-0.03, 1.15)
    a.set_xlabel("mean active agents per day, N")
    a.set_ylabel(r"branching ratio $\hat n$ (talk, B2)")
    a.set_title("(a) branching ratio vs size", loc="left")
    a.text(0.03, 0.80, f"Spearman ρ(n̂, log N) = {rho:.2f}".replace("-", "−"), transform=a.transAxes, fontsize=4.9, color=INK2, ha="left")
    hs = [plt.Line2D([], [], marker=MODE[k][1], color=MODE[k][0], ls="", ms=3 if k != "P" else 4.5, label=MODE[k][2])
          for k in ("C", "F", "other", "P")]
    fig.legend(handles=hs, fontsize=5, loc="lower center", ncol=4, frameon=False, handletextpad=0.1,
               columnspacing=0.8, borderaxespad=0.05)

    # (b) fast n_cross real vs agent-shift null
    b = ax[1]
    m = dict(zip(t["goal_no"].to_list(), t["mode"].to_list()))
    for r in j.iter_rows(named=True):
        k = mkey(m.get(r["goal_no"], "")); col, mk, _ = MODE[k]
        b.plot(r["n_cross_fast300_shift_mean"], r["n_cross_fast300_real"], mk, color=col, ms=4.5 if k == "P" else 2.6,
               mec="white", mew=0.25)
    b.plot([0, 0.22], [0, 0.22], color=INK2, lw=0.7, ls="--")
    b.text(0.215, 0.14, "real = null", fontsize=4.9, color=INK2, ha="right", va="top")
    b.set_xlim(-0.005, 0.22); b.set_ylim(-0.005, 0.22)
    b.set_xticks([0, 0.1, 0.2]); b.set_yticks([0, 0.1, 0.2])
    b.set_xlabel("agent-shift null")
    b.set_ylabel(r"fast cross-agent $n_{\times}$")
    b.set_title("(b) fast cross-triggering", loc="left")
    b.text(0.97, 0.03, f"real > all shifts in {sh['frac_real_gt_all_surrogates']*100:.0f}%\n"
                        f"Wilcoxon p = {sh['wilcoxon_p_greater']:.0e}".replace("e-0", "e-"),
           transform=b.transAxes, fontsize=4.9, color=INK, ha="right", va="bottom")

    fig.tight_layout(pad=0.2, w_pad=0.6, rect=(0, 0.075, 1, 1))
    fig.savefig(FIG / "summary_obs.pdf")
    plt.close(fig)
    print("wrote", FIG / "summary_obs.pdf")


if __name__ == "__main__":
    main()
