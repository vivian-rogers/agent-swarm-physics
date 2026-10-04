"""H95 figures: summary_obs.pdf (slack vs pre-registered x; slack and settling time by the post-hoc design code) and
synthetic_compact.pdf (gauge curve; rho under the churn null vs a true gauge).
  uv run python hypotheses/H95-slack-specificity-gauge/analysis/figures.py
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h95lib as L  # noqa: E402

FIG = L.ROOT / "hypotheses/H95-slack-specificity-gauge/figures"
C1, C2, C3, GREY = "#2a78d6", "#eb6834", "#1baf7a", "#8a8984"
plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.6,
                     "legend.frameon": False})
D = {"G37": 0, "G38": 0, "G39": 1, "G40": 1, "G41": 0, "G42": 1, "G44best": 1, "G44rest": 0, "G51": 1}


def obs():
    a = json.load(open(L.OUTD / "results/across.json"))
    pu = a["per_unit"]
    fig, ax = plt.subplots(1, 2, figsize=(6.8, 2.5))
    for n, r in pu.items():
        c, m = (C1, "o") if D[n] else (C2, "s")
        ax[0].plot([r["x"]] * 2, r["S_ci"], color=c, lw=0.8, alpha=0.6)
        ax[0].plot(r["x"], r["S_e"], m, color=c, ms=5)
        ax[0].annotate(n.replace("G44", "G44 "), (r["x"], r["S_e"]), xytext=(4, 2), textcoords="offset points", fontsize=6)
    ax[0].set_yscale("log")
    ax[0].axhline(1, color=GREY, lw=0.6)
    ax[0].set_xlabel("x: day-1 share of work on H54-named repos")
    ax[0].set_ylabel("slack S = ĀT/W (log)")
    rho, p, _ = a["rho_S_x"]
    ax[0].set_title(f"(a) pre-registered gauge: ρ = {rho:+.2f}, p = {p:.2f}", fontsize=8, loc="left")
    names = list(pu)
    order = sorted(names, key=lambda n: (D[n], pu[n]["S_e"]))
    xx = np.arange(len(order))
    for k, n in enumerate(order):
        c = C1 if D[n] else C2
        ax[1].bar(k, pu[n]["T_e"], width=0.6, color=c)
    ax[1].set_xticks(xx, [n.replace("G44best", "G44b").replace("G44rest", "G44r") for n in order], fontsize=6.5)
    ax[1].set_ylabel("settling time T_e (active h)")
    ax[1].bar([0], [0], color=C2, label="goal open or objective only")
    ax[1].bar([0], [0], color=C1, label="goal assigns an artifact")
    ax[1].legend(fontsize=6.5, loc="upper right")
    ax[1].set_title("(b) T_e by goal type (post hoc, p = 0.008)", fontsize=8, loc="left")
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs.pdf")
    fig.savefig(FIG / "summary_obs.png", dpi=150)


def syn():
    g = pl.read_parquet(L.OUTD / "synthetic/gauge.parquet")
    fig, ax = plt.subplots(1, 2, figsize=(6.8, 2.1))
    for tg, c, m in (("shared", C1, "o"), ("own", C3, "^")):
        d = g.filter((pl.col("target") == tg) & (pl.col("N") == 15)).group_by("q").agg(
            pl.col("S_e").median().alias("m"), pl.col("S_e").quantile(0.1).alias("lo"),
            pl.col("S_e").quantile(0.9).alias("hi")).sort("q")
        ax[0].fill_between(d["q"], d["lo"], d["hi"], color=c, alpha=0.15, lw=0)
        ax[0].plot(d["q"], d["m"], marker=m, color=c, lw=1.5, ms=3.5, label=f"{tg} named target")
    ax[0].set_xlabel("captured fraction q (planted)")
    ax[0].set_ylabel("slack S (N = 15)")
    ax[0].legend(fontsize=6.5)
    ax[0].set_title("(a) gauge curve: monotone in q", fontsize=8, loc="left")
    nul = pl.read_parquet(L.OUTD / "synthetic/churn_null.parquet")["rho_S_x"].to_numpy()
    pw = pl.read_parquet(L.OUTD / "synthetic/power.parquet")["rho_S_x"].to_numpy()
    bins = np.linspace(-1, 1, 21)
    ax[1].hist(nul, bins=bins, color=GREY, alpha=0.7, label="churn only (q fixed)")
    ax[1].hist(pw, bins=bins, histtype="step", color=C1, lw=1.5, label="true gauge (q varies)")
    ax[1].axvline(-0.583, color=C2, lw=1, ls="--", label="ρ_crit (n = 9)")
    ax[1].set_xlabel("ρ(S, x) over nine kickoffs")
    ax[1].set_ylabel("draws")
    ax[1].legend(fontsize=6.5, loc="upper right")
    ax[1].set_title("(b) power 0.29 at n = 9", fontsize=8, loc="left")
    fig.tight_layout()
    fig.savefig(FIG / "synthetic_compact.pdf")
    fig.savefig(FIG / "synthetic_compact.png", dpi=150)


if __name__ == "__main__":
    FIG.mkdir(exist_ok=True)
    obs()
    syn()
