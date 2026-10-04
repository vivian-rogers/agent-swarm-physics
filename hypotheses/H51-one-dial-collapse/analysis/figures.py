"""H51 figures: collapse panels (summary page 1), CV-R^2 by model (page 2), phase diagram, synthetic power.
Usage: uv run python hypotheses/H51-one-dial-collapse/analysis/figures.py
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
import h51lib as L  # noqa: E402

FIG = L.HYP / "figures"
COL = {"I": "#2c7fb8", "II": "#7f8c8d", "III": "#c0392b"}
MK = {"I": "o", "II": "s", "III": "^"}
plt.rcParams.update({"font.size": 7})


def main():
    FIG.mkdir(exist_ok=True)
    pts = pl.read_parquet(L.DATA / "results/phase_points.parquet")
    col = json.loads((L.DATA / "results/collapse.json").read_text())["primary"]
    syn = json.loads((L.DATA / "synthetic/summary.json").read_text())

    # 1. collapse panels
    fig, axs = plt.subplots(2, 2, figsize=(3.4, 3.0))
    for ax, j in zip(axs.flat, L.OBS):
        for reg in ("I", "II", "III"):
            s = pts.filter((pl.col("regime") == reg) & pl.col(j).is_not_null())
            ax.scatter(s["K"], s[j], s=9, color=COL[reg], marker=MK[reg], lw=0, label=f"regime {reg}")
        c = col[j]["cv_r2"]
        ax.set_title(f"{L.OBS_LABEL[j]}\nCV-$R^2$: $g_{{lag}}$ {c['K']:.2f} | regime {c['regime']:.2f} | log N {c['logN']:.2f}",
                     fontsize=5.6, pad=2)
        ax.tick_params(labelsize=5.5)
    for ax in axs[1]:
        ax.set_xlabel("read-out loop gain $g_{lag}$ (period)", fontsize=6)
    h, lab = axs[0, 0].get_legend_handles_labels()
    fig.legend(h, lab, frameon=False, fontsize=5.5, loc="lower center", ncol=3, handletextpad=0.1)
    fig.tight_layout(pad=0.4, h_pad=0.5, w_pad=0.5, rect=(0, 0.05, 1, 1))
    fig.savefig(FIG / "collapse_col.pdf")
    plt.close(fig)

    # 2. CV-R^2 by model
    models = [("regime", "regime labels"), ("logN", "log N"), ("field", "field (c$_\\times$, S$_{text}$)"),
              ("g_eq", "equal-time dial"), ("K", "$g_{lag}$ (D1)"), ("index", "single index (D2)")]
    cols = ["#bdbdbd", "#969696", "#74a9cf", "#fdae6b", "#c0392b", "#7b3294"]
    fig, ax = plt.subplots(figsize=(3.4, 1.95))
    x = np.arange(len(L.OBS))
    wbar = 0.13
    for k, ((m, lab), cc) in enumerate(zip(models, cols)):
        v = [max(col[j]["cv_r2"][m], -0.3) for j in L.OBS]
        ax.bar(x + (k - 2.5) * wbar, v, wbar, color=cc, label=lab)
    ax.axhline(0, color="k", lw=0.5)
    ax.axhline(L.MIN_R2, color="k", lw=0.5, ls=":")
    ax.set_xticks(x, ["settling", "herding", "branching", "loops"])
    ax.set_ylabel("LOPO CV-$R^2$")
    ax.set_ylim(-0.32, max(0.6, max(col[j]["cv_r2"][m] for j in L.OBS for m, _ in models) + 0.05))
    ax.legend(frameon=False, fontsize=5, ncol=3, loc="upper left")
    fig.tight_layout(pad=0.3)
    fig.savefig(FIG / "cvr2_col.pdf")
    plt.close(fig)

    # 3. phase diagram: (N, K) and (h, K)
    fig, axs = plt.subplots(1, 2, figsize=(6.8, 2.6), sharey=True)
    for ax, xc, xl in ((axs[0], "N_active", "active population N (H85)"),
                       (axs[1], "c_x_trim", "shared field $c_\\times$ (trimmed activity, H86)")):
        for reg in ("I", "II", "III"):
            s = pts.filter(pl.col("regime") == reg)
            ax.scatter(s[xc], s["K"], s=14, color=COL[reg], marker=MK[reg], alpha=0.85, lw=0, label=f"regime {reg}")
            for r in s.iter_rows(named=True):
                ax.annotate(str(r["goal_no"]), (r[xc], r["K"]), fontsize=4.5, xytext=(2, 1), textcoords="offset points")
        ax.axhline(0, color="k", lw=0.4)
        ax.set_xlabel(xl)
    axs[0].set_xscale("log")
    axs[1].set_xscale("symlog", linthresh=0.01)
    axs[0].set_ylabel("coupling $g_{lag}$ (H67)")
    axs[0].legend(frameon=False, fontsize=5.5, loc="upper left")
    fig.tight_layout()
    fig.savefig(FIG / "phase_diagram.pdf")
    plt.close(fig)

    # 4. synthetic power
    fig, ax = plt.subplots(figsize=(3.4, 1.8))
    worlds = ["W0", "W1_0.15", "W1_0.3", "W1_0.5", "W2", "W3"]
    labs = ["regime only", "dial $\\rho^2$ .15", "dial .30", "dial .50", "N only", "index"]
    a = [syn[w]["perm_reject_0.05"] for w in worlds]
    b = [syn[w]["hyp_K_3of4_and_p"] for w in worlds]
    c = [syn[w]["hyp_index_3of4"] for w in worlds]
    x = np.arange(len(worlds))
    ax.bar(x - 0.25, a, 0.25, color="#c0392b", label="permutation p<0.05")
    ax.bar(x, b, 0.25, color="#fdae6b", label="D1 collapses ≥3/4 & p<0.05")
    ax.bar(x + 0.25, c, 0.25, color="#7b3294", label="D2 collapses ≥3/4")
    ax.axhline(0.8, color="k", ls=":", lw=0.5)
    ax.axhline(0.1, color="k", ls="--", lw=0.5)
    ax.set_xticks(x, labs, fontsize=5.5)
    ax.set_ylabel("rate (100 runs)")
    ax.legend(frameon=False, fontsize=5, loc="upper left")
    fig.tight_layout(pad=0.3)
    fig.savefig(FIG / "synthetic_col.pdf")
    plt.close(fig)
    print("figures written")


if __name__ == "__main__":
    main()
