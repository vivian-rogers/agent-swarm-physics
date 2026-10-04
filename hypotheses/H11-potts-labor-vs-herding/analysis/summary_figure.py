"""H11 summary-page figure (figures/summary_obs.pdf): reads round-1 outputs only, recomputes nothing.

(a) primary statistic beta*J_CW per tested period, grouped by the a-priori goal-mode class;
(b) the #26 runoff: the eventual winner's declared-vote share with the fitted logistic step.

Usage: uv run python hypotheses/H11-potts-labor-vs-herding/analysis/summary_figure.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = ROOT / "data/processed/H11-potts-labor-vs-herding"
FIG = HERE.parent / "figures"
C_AF, C_FM, C_NONE = "#2a78d6", "#eb6834", "#1baf7a"  # validated reference slots 1-3 (same as analysis/figures.py)
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
OWN = {39, 40, 42}  # weeks where the goal gave each agent its own artifact (card, Synthesis 1)
plt.rcParams.update({"font.size": 7, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "axes.titlesize": 7.2,
                     "axes.titleweight": "bold", "legend.frameon": False, "pdf.fonttype": 42})


def main():
    v = pl.read_parquet(DATA / "verdicts_round1.parquet").filter(pl.col("tested"))
    r26 = json.loads((DATA / "G26/round1.json").read_text())["votes"]
    fig, (a, b) = plt.subplots(1, 2, figsize=(4.3, 2.6), gridspec_kw={"width_ratios": [1.15, 1]})

    # (a) beta J_CW by predicted class
    groups = [("AF", "predicted\nAF (labor)", C_AF), ("FM", "predicted\nFM (herd)", C_FM), ("none", "no\nprediction", C_NONE)]
    lo_clip = -10.5
    a.axhspan(lo_clip, 0, color="#f3f2ee", lw=0, zorder=0)
    a.axhline(0, color=INK2, lw=0.7)
    a.text(2.45, -0.6, "spread", fontsize=6, color=INK2, ha="right", va="top")
    a.text(2.45, 0.5, "herding", fontsize=6, color=INK2, ha="right", va="bottom")
    for xi, (key, lab, col) in enumerate(groups):
        d = v.filter(pl.col("cls").str.starts_with(key) if key != "none" else pl.col("cls").str.starts_with("none")).sort("bj_cw")
        n = d.height
        xs = xi + np.linspace(-0.2, 0.2, n) if n > 1 else np.array([xi])
        for m, (x, r) in enumerate(zip(xs, d.iter_rows(named=True))):
            y = max(r["bj_cw"], lo_clip + 0.4)
            sig = abs(r["t_cw"]) > r["tcrit"]
            mk = "^" if r["goal"] in OWN else "o"
            a.scatter([x], [y], s=26, marker=mk, color=col if sig else "white", edgecolor=col, linewidth=1.1, zorder=3)
            txt = f"#{r['goal']}" + (f" ({r['bj_cw']:.0f})" if r["bj_cw"] < lo_clip else "")
            left = m % 2 == 1 and r["bj_cw"] > 0
            off = {25: (-3.5, -3.5), 38: (3.5, -2.5)}.get(r["goal"], (-3.5 if left else 3.5, -1))
            a.annotate(txt, (x, y), xytext=off, textcoords="offset points", fontsize=5, color=INK2,
                       va="center", ha="right" if off[0] < 0 else "left")
    a.set_xticks(range(3), [g[1] for g in groups], fontsize=6)
    a.set_xlim(-0.5, 2.55)
    a.set_ylim(lo_clip, 7.5)
    a.set_ylabel(r"$\beta J_{CW}$ (uniform Curie–Weiss Potts)")
    a.yaxis.grid(True, color=GRID, lw=0.5)
    a.set_axisbelow(True)
    a.set_title("a  Herding whatever the mode", loc="left")
    a.scatter([], [], marker="o", color=INK2, s=18, label="filled: |t| > t$_{crit}$")
    a.scatter([], [], marker="^", facecolor="white", edgecolor=INK2, s=18, label="own-artifact week")
    a.legend(loc="lower left", bbox_to_anchor=(0.0, 0.2), fontsize=5.2, handletextpad=0.2, borderaxespad=0.2)

    # (b) #26 declared votes
    s = r26["series"]
    t, k, n = map(np.asarray, (s["t"], s["k"], s["n"]))
    share = k / np.maximum(n, 1)
    j = r26["jump"]
    tt = np.linspace(t.min(), t.max(), 400)
    fit = j["lo"] + (j["hi"] - j["lo"]) / (1 + np.exp(-(tt - j["t0"]) / max(j["tau"], 1e-3)))
    b.scatter(t, share, s=np.clip(n * 2.2, 4, 26), color=INK2, alpha=0.65, lw=0, zorder=3, label="declared share (size = voters)")
    b.plot(tt, fit, color=C_FM, lw=1.6, zorder=2, label="logistic step fit")
    b.set_ylim(-0.03, 1.03)
    b.set_xlabel("30-min window (active time)")
    b.set_ylabel("winner's declared-vote share")
    b.yaxis.grid(True, color=GRID, lw=0.5)
    b.set_axisbelow(True)
    b.set_title("b  #26 runoff jump", loc="left")
    b.annotate(f"{j['lo']:.2f} → {j['hi']:.2f}\nΔBIC(step − linear) {j['dbic_step_vs_lin']:.0f}",
               (j["t0"], 0.5), xytext=(-62, 2), textcoords="offset points", fontsize=5.5, color=INK, va="center")
    b.legend(loc="upper left", fontsize=5.2, handletextpad=0.3, borderaxespad=0.2)
    fig.tight_layout(pad=0.3, w_pad=0.8)
    fig.savefig(FIG / "summary_obs.pdf")
    fig.savefig(FIG / "summary_obs.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    main()
