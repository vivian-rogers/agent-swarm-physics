"""H81 round 2 figure (no text): figures/summary_r2.pdf
(a) R1 record-carrier contrast C_R1 per regime and placebo, both models, goal-bootstrap 95% CI, S_ex 95th percentile
    (grey bar) and the planted record-carriage mean at lambda = 1 (tick).
(b) R4 regime I: binned H81 block similarity s(lag) and H82 boundary loadings gamma(|lag|) with the shared-tau OU fit.
Usage: uv run python hypotheses/H81-culture-beyond-composition/analysis/r2_figures.py
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
import r2lib as Q  # noqa: E402

FIG = Q.ROOT / "hypotheses/H81-culture-beyond-composition/figures"
C = {"bge_small": "#2a78d6", "gte_modernbert": "#eb6834"}
LAB = {"bge_small": "bge", "gte_modernbert": "gte"}
plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.6})


def binned(x, y, w, edges):
    out = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (x > lo) & (x <= hi) & np.isfinite(y)
        out.append(((lo + hi) / 2 if hi < 1e3 else lo * 1.3, (w[m] * y[m]).sum() / w[m].sum() if m.any() else np.nan))
    return np.array(out)


def main():
    res = json.loads((Q.R2 / "r2_results.json").read_text())
    fig, ax = plt.subplots(1, 2, figsize=(6.6, 2.5), gridspec_kw={"width_ratios": [1, 1.25]})
    keys = [("I/U_act", "I: used-\nbut-unposted"), ("III/U_ledger", "III: posted-\nbut-unread"), ("III/U_act", "III: used-\nbut-unposted")]
    for j, (k, lab) in enumerate(keys):
        for i, m in enumerate(Q.MODELS):
            o = res["r1"][m][k]; x = j + (i - 0.5) * 0.3
            sy = json.loads((Q.R2 / f"synthetic_r1_{m}.json").read_text())[k]
            ax[0].bar(x, o["S_ex_q95_C"], width=0.26, color="#d8d6cf", lw=0)
            ax[0].plot([x - 0.12, x + 0.12], [sy["S_rec_1.0"]["C_R1"]["mean"]] * 2, color="#555", lw=1)
            ax[0].errorbar(x, o["C_R1"], yerr=[[o["C_R1"] - o["C_R1_lo"]], [o["C_R1_hi"] - o["C_R1"]]], fmt="o", ms=4,
                           color=C[m], lw=1, label=LAB[m] if j == 0 else None)
    ax[0].axhline(0, color="#999", lw=0.5)
    ax[0].set_xticks(range(3)); ax[0].set_xticklabels([k[1] for k in keys], fontsize=7)
    ax[0].set_ylabel(r"$C_{R1}$ = cos(read) $-$ cos(placebo)")
    ax[0].set_title("(a) does the residual follow the record it read?", loc="left", fontsize=8)
    ax[0].legend(frameon=False, fontsize=7, loc="upper right")
    edges = (0, 7, 14, 28, 56, 112, 1e4)
    t = np.linspace(1, 160, 200)
    for m in Q.MODELS:
        T = pl.read_parquet(Q.R2 / f"pairs_clocks_{m}_I.parquet")
        G = pl.read_parquet(Q.R2 / f"r4_gammas_{m}_I.parquet").to_numpy()
        b81 = binned(T["dt"].to_numpy(), T["s"].to_numpy(), T["w"].to_numpy(), edges)
        b82 = binned(np.abs(G[:, 3]), G[:, 4], Q.h82_weights(G), edges)
        jf = res["r4"][m]["I"]["joint"]
        ax[1].plot(b81[:, 0], b81[:, 1], "s", color=C[m], ms=4, label=f"H81 blocks ({LAB[m]})")
        ax[1].plot(b82[:, 0], b82[:, 1], "o", mfc="white", color=C[m], ms=4, label=f"H82 boundaries ({LAB[m]})")
        ax[1].plot(t, jf["A81"] * np.exp(-t / jf["tau"]) + jf["c81"], "-", color=C[m], lw=1)
        ax[1].plot(t, jf["A82"] * np.exp(-t / jf["tau"]) + jf["c82"], "--", color=C[m], lw=1)
    ax[1].axhline(0, color="#999", lw=0.5)
    ax[1].set_xscale("log"); ax[1].set_xlabel("lag (days)"); ax[1].set_ylabel(r"$\bar s$ (H81) or $\gamma$ (H82)")
    ax[1].set_title("(b) regime I: block profile and boundary loadings", loc="left", fontsize=8)
    ax[1].legend(frameon=False, fontsize=6, ncol=1, loc="upper right")
    fig.tight_layout()
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / "summary_r2.pdf"); print("wrote", FIG / "summary_r2.pdf")


if __name__ == "__main__":
    main()
