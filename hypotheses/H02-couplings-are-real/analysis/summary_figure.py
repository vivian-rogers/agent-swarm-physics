"""Two-panel observables figure for the H02 one-page summary (plots existing results only; no recomputation).

(a) Synthetic: pass rate of the locked #45 rule (leader rank 1 and z >= 2 vs N1) at village sampling (N = 18, 5 days),
    by planted leader strength (results_summary.json, harness_C).
(b) #45 locked holdout: z of net outgoing influence I_k vs the N1 surrogates for all 18 agents in rank order, Fine-Tuned Leader marked
    (confirm_45.json, primary KI-1 block estimator).

Usage: uv run python hypotheses/H02-couplings-are-real/analysis/summary_figure.py
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
DATA = ROOT / "data/processed/H02-couplings-are-real"
FIG = Path(__file__).resolve().parents[1] / "figures"
C1, C2, INK, INK2, GRID = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#e4e3df"
FIGSIZE = (3.4, 1.7)  # one RevTeX column, printed 1:1 (the page caps the figure at 1.7 in tall)
plt.rcParams.update({"font.size": 5.8, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.4, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.titlesize": 6.3, "axes.titleweight": "bold", "pdf.fonttype": 42,
                     "xtick.labelsize": 5.4, "ytick.labelsize": 5.4, "axes.labelsize": 5.8, "axes.linewidth": 0.6,
                     "xtick.major.size": 2, "ytick.major.size": 2, "xtick.major.pad": 1.5, "ytick.major.pad": 1.5,
                     "axes.titlepad": 3, "axes.labelpad": 1.5})


def main():
    summ = json.loads((DATA / "results_summary.json").read_text())
    conf = json.loads((DATA / "confirm_45.json").read_text())
    roster = pl.read_parquet(ROOT / "data/processed/shared/roster.parquet").select("agent", "name")
    name = dict(zip(roster["agent"].to_list(), roster["name"].to_list()))

    fig, ax = plt.subplots(1, 2, figsize=FIGSIZE, gridspec_kw={"width_ratios": [0.8, 1.55]})

    # (a) synthetic power of the confirmatory rule
    rows = sorted([r for r in summ["harness_C"] if r["background"] and r["JL"] > 0], key=lambda r: r["JL"])
    a = ax[0]
    x = np.arange(len(rows))
    vals = [r["pass_rate"] for r in rows]
    a.bar(x, vals, 0.6, color=C1)
    for xx, v in zip(x, vals):
        a.text(xx, v + 0.02, f"{v:.2f}", ha="center", va="bottom", fontsize=5.2, color=INK)
    a.set_xticks(x)
    a.set_xticklabels([f"{5 * r['JL']:g}" for r in rows])
    a.set_xlabel("leader's total outgoing J")
    a.set_ylabel("P(locked rule passes)")
    a.set_ylim(0, 1.15)
    a.set_title("(a) synthetic, 5 d", loc="left")
    a.grid(axis="x", visible=False)

    # (b) #45 holdout: z(I_k) for every agent, in rank order
    rk = conf["primary"]["ranking"]
    leader = conf["leader"]
    pr = conf["primary"]
    b = ax[1]
    xr = np.arange(1, len(rk) + 1)
    b.bar(xr, [r["z"] for r in rk], 0.75, color=[C2 if r["agent"] == leader else "#a9c9f0" for r in rk])
    b.axhline(2, color=INK, lw=0.8, ls="--")
    b.axhline(0, color=INK2, lw=0.5)
    b.text(len(rk) + 0.4, 2.08, "rule: rank 1 and z ≥ 2", fontsize=5, color=INK, ha="right", va="bottom")
    li = [i for i, r in enumerate(rk) if r["agent"] == leader][0]
    b.annotate(f"{name.get(leader, 'leader')}\nrank {pr['leader_rank']}/{pr['N']}, z = {pr['leader_z']:.2f}",
               xy=(li + 1, rk[li]["z"] + 0.05), xytext=(li + 3.2, 1.25), fontsize=5.2, color=C2, fontweight="bold",
               ha="left", va="center", arrowprops=dict(arrowstyle="->", color=C2, lw=0.7))
    b.set_xticks([1, 5, 10, 15, 18]); b.set_xlim(0.3, len(rk) + 0.7)
    b.set_ylim(-2.3, 2.6)
    b.set_xlabel("agent rank by net outgoing influence")
    b.set_ylabel(r"z of $I_k$ vs N1 null")
    b.set_title("(b) #45 locked holdout: FAIL", loc="left")
    b.grid(axis="x", visible=False)

    fig.tight_layout(pad=0.2, w_pad=0.6)
    fig.savefig(FIG / "summary_obs.pdf")
    plt.close(fig)
    print("wrote", FIG / "summary_obs.pdf")


if __name__ == "__main__":
    main()
