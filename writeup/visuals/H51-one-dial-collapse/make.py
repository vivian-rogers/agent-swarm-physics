"""H51 visual: one dial fails. The phase diagram (N, regime, g_lag) and why g_lag cannot collapse the observables.

    uv run python writeup/visuals/H51-one-dial-collapse/make.py

Inputs (read only; non-holdout by construction, asserted):
  data/processed/H51-one-dial-collapse/results/phase_points.parquet   per period: N_active, K = g_lag (H67 pool) + SE,
                                                                       Y1 ln tau_settle, Y2 herding share, Y3 logit R-hat,
                                                                       Y4 logit loop rate
  data/processed/H51-one-dial-collapse/results/collapse.json          leave-one-period-out CV-R^2 per dial (primary)
Output: fig.pdf / fig.png (no animation: the claim is a static comparison of periods).
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
from matplotlib.lines import Line2D  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "writeup/visuals"))
sys.path.insert(0, str(ROOT / "infra/shared"))
import vstyle as vs  # noqa: E402
from common import load_holdout  # noqa: E402

D = ROOT / "data/processed/H51-one-dial-collapse/results"
REG_C = {"I": vs.C["green"], "II": vs.C["pink"], "III": vs.C["blue"]}
REG_M = {"I": "s", "II": "D", "III": "o"}
OBS = [("Y1_settle", r"settling $\ln\tau$", "log"),
       ("Y2_herd", "herding share", "lin"),
       ("Y3_branch", r"branching logit $\hat R$", "log"),
       ("Y4_loop", "loop rate (logit)", "log")]


def main():
    vs.use()
    held = set(load_holdout()["goal_periods_held_out"])
    p = pl.read_parquet(D / "phase_points.parquet").sort("goal_no")
    assert not set(p["goal_no"].to_list()) & held
    cv = json.loads((D / "collapse.json").read_text())["primary"]

    fig = plt.figure(figsize=(vs.W["double"], 3.7))
    gs = fig.add_gridspec(2, 5, width_ratios=[1.9, 1, 1, 1, 1], hspace=0.42, wspace=0.42,
                          left=0.07, right=0.99, top=0.86, bottom=0.12)
    ax = fig.add_subplot(gs[:, 0])

    # (a) phase diagram: N (log) x g_lag, marker = regime
    for r in ("I", "II", "III"):
        v = p.filter(pl.col("regime") == r)
        x, k, se = v["N_active"].to_numpy(), v["K"].to_numpy(), v["g_lag_se"].to_numpy()
        ax.errorbar(x, k, yerr=1.96 * se, fmt=REG_M[r], ms=3.8, mfc=REG_C[r], mec="white", mew=0.4,
                    ecolor=REG_C[r], elinewidth=0.7, capsize=0, alpha=0.9, zorder=3, label=f"regime {r}")
    for g in (40, 51, 44, 37):
        v = p.filter(pl.col("goal_no") == g).to_dicts()[0]
        dx, dy = {40: (4, -10), 51: (-4, 9), 44: (5, 3), 37: (-16, 4)}[g]
        ax.annotate(f"#{g}", (v["N_active"], v["K"]), xytext=(dx, dy), textcoords="offset points", fontsize=6,
                    color=vs.INK2)
    ax.axhline(0, color=vs.INK2, lw=0.6)
    ax.set_xscale("log")
    ax.set_xticks([4, 6, 10, 15, 25]); ax.set_xticklabels(["4", "6", "10", "15", "25"]); ax.minorticks_off()
    ax.set_xlim(3.5, 32)
    ax.set_ylim(-0.2, 0.42)
    ax.set_xlabel("active agents $N$ (log scale)")
    ax.set_ylabel(r"coupling coordinate $g_{lag}$ (95% CI)")
    ax.set_title("(a) phase diagram of 33 periods", loc="left", y=1.035)
    gmax = float(p["K"].max())
    ax.text(3.7, 0.395, f"critical $g = 1$ is far off-scale:\nmax $\\chi = 1/(1-g)$ = {1/(1-gmax):.2f}",
            fontsize=6.2, color=vs.INK, va="top")
    ax.legend(loc="lower left", handletextpad=0.2, fontsize=6.5)

    # (b) small multiples: each observable vs g_lag (top) and vs log N (bottom)
    g0 = np.linspace(0, 0.25, 50)
    axes = []
    for j, (col, lab, kind) in enumerate(OBS):
        for row, (xcol, xl, key) in enumerate((("K", r"$g_{lag}$", "K"), ("N_active", "$N$", "logN"))):
            a = fig.add_subplot(gs[row, j + 1])
            axes.append(a)
            v = p.filter(pl.col(col).is_not_null())
            if row == 0:
                base = v.filter(pl.col("K").abs() < 0.05)[col].median()
                # gray band: the most a mean-field amplification chi = 1/(1 - g) can move the observable
                up = base + np.log(1 / (1 - g0)) if kind == "log" else base / (1 - g0)
                dn = base - np.log(1 / (1 - g0)) if kind == "log" else base * (1 - g0)
                a.fill_between(g0, dn, up, color=vs.NULL, alpha=0.55, lw=0, zorder=0)
            for r in ("I", "II", "III"):
                w = v.filter(pl.col("regime") == r)
                a.scatter(w[xcol].to_numpy(), w[col].to_numpy(), marker=REG_M[r], s=7, color=REG_C[r],
                          edgecolor="white", lw=0.25, zorder=2)
            if row == 1:
                a.set_xscale("log"); a.set_xticks([4, 10, 25]); a.set_xticklabels(["4", "10", "25"]); a.minorticks_off()
            else:
                a.set_xlim(-0.08, 0.27); a.set_xticks([0, 0.1, 0.2])
            a.tick_params(labelsize=5.5, pad=1)
            r2 = cv[col]["cv_r2"][key]
            if row == 0:
                a.set_title(lab, fontsize=6.6, pad=2)
            a.set_xlabel(f"{xl}   (CV-$R^2$ {r2:+.2f})", fontsize=6.2, labelpad=1)
            if j == 0:
                a.set_ylabel("vs coupling" if row == 0 else "vs size", fontsize=6.5)
    fig.text(0.355, 0.955, "(b) four unfitted observables against coupling (top) and size (bottom); "
             "gray: the most $\\chi\\leq1.31$ could move them", fontsize=7.6, ha="left")
    fig.savefig  # noqa: B018
    vs.save(fig, HERE / "fig")
    plt.close(fig)
    for col, *_ in OBS:
        c = cv[col]["cv_r2"]
        print(col, "K", round(c["K"], 3), "logN", round(c["logN"], 3), "regime", round(c["regime"], 3))


if __name__ == "__main__":
    main()
