"""Two-panel observables figure for the H02 one-page summary (plots existing results only; no recomputation).

(a) Synthetic: pass rate of the locked #45 rule (leader rank 1 and z >= 2 vs N1) at village sampling (N = 18, 5 days),
    by planted leader strength (results_summary.json, harness_C).
(b) #45 locked holdout: z of net outgoing influence I_k vs the N1 surrogates for all 18 agents, Fine-Tuned Leader marked
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
plt.rcParams.update({"font.size": 7, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.titlesize": 7.5, "axes.titleweight": "bold", "pdf.fonttype": 42,
                     "xtick.labelsize": 6.5, "ytick.labelsize": 6.5, "axes.labelsize": 7})


def main():
    summ = json.loads((DATA / "results_summary.json").read_text())
    conf = json.loads((DATA / "confirm_45.json").read_text())
    roster = pl.read_parquet(ROOT / "data/processed/shared/roster.parquet").select("agent", "name")
    name = dict(zip(roster["agent"].to_list(), roster["name"].to_list()))

    fig, ax = plt.subplots(1, 2, figsize=(4.3, 2.6), gridspec_kw={"width_ratios": [0.85, 1.5]})

    # (a) synthetic power of the confirmatory rule
    rows = [r for r in summ["harness_C"] if r["background"] and r["JL"] > 0]
    rows = sorted(rows, key=lambda r: r["JL"])
    a = ax[0]
    x = np.arange(len(rows))
    vals = [r["pass_rate"] for r in rows]
    a.bar(x, vals, 0.6, color=C1)
    for xx, v in zip(x, vals):
        a.text(xx, v + 0.02, f"{v:.2f}", ha="center", va="bottom", fontsize=6, color=INK)
    a.set_xticks(x)
    a.set_xticklabels([f"{5 * r['JL']:g}" for r in rows])
    a.set_xlabel("planted leader's total outgoing J", fontsize=6.3)
    a.set_ylabel("P(locked rule passes)")
    a.set_ylim(0, 1.12)
    a.set_title("(a) synthetic, 5 days", loc="left")
    a.grid(axis="x", visible=False)

    # (b) #45 holdout ranking
    rk = conf["primary"]["ranking"]
    leader = conf["leader"]
    b = ax[1]
    y = np.arange(len(rk))[::-1]
    for yy, r in zip(y, rk):
        b.barh(yy, r["z"], 0.72, color=C2 if r["agent"] == leader else "#a9c9f0")
    b.axvline(2, color=INK, lw=0.9, ls="--")
    b.axvline(0, color=INK2, lw=0.6)
    b.text(2.05, y.max() - 0.3, "rule:\nz ≥ 2\nand\nrank 1", fontsize=5.6, color=INK, va="top", ha="left")
    b.set_yticks(y)
    b.set_yticklabels([name.get(r["agent"], str(r["agent"])) for r in rk], fontsize=5.7)
    for t, r in zip(b.get_yticklabels(), rk):
        if r["agent"] == leader:
            t.set_color(C2); t.set_fontweight("bold")
    b.set_xlim(-2.3, 3.0)
    b.set_xlabel(r"z of net outgoing influence $I_k$ vs N1", fontsize=6.3)
    pr = conf["primary"]
    b.set_title("(b) #45 locked holdout", loc="left")
    b.text(0.12, 3.0, f"leader:\nrank {pr['leader_rank']}/{pr['N']}\nz = {pr['leader_z']:.2f}\nFAIL", fontsize=6, color=C2,
           ha="left", va="center", fontweight="bold")
    b.grid(axis="y", visible=False)

    fig.tight_layout(pad=0.3, w_pad=0.6)
    fig.savefig(FIG / "summary_obs.pdf")
    plt.close(fig)
    print("wrote", FIG / "summary_obs.pdf")


if __name__ == "__main__":
    main()
