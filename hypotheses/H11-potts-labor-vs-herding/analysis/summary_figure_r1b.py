"""H11 round-1b summary figures (read round-1b outputs only; recompute nothing).

figures/summary_obs_r1b.pdf   page 1: (a) beta*J_CW per tested week on shared labels, by a-priori class;
                              (b) #26 per election round from DQ6 ballots (winner's ballot share vs seconds since opening)
figures/r1b_work_vs_attention.pdf  page 2: (a) coupling beyond agent fields (z vs circular shift) in attention vs work,
                              per goal period / #51 unit; (b) share of agent-windows whose work repo equals the attention project

Usage: uv run python hypotheses/H11-potts-labor-vs-herding/analysis/summary_figure_r1b.py
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
R1B = ROOT / "data/processed/H11-potts-labor-vs-herding/r1b"
FIG = HERE.parent / "figures"
C_AF, C_FM, C_NONE = "#2a78d6", "#eb6834", "#1baf7a"   # project reference slots 1-3 (analysis/figures.py)
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
OWN = {39, 40, 42}
plt.rcParams.update({"font.size": 7, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "axes.titlesize": 7.2,
                     "axes.titleweight": "bold", "legend.frameon": False, "pdf.fonttype": 42})


def page1():
    v = pl.read_parquet(R1B / "verdicts_round1b.parquet").filter(pl.col("tested"))
    g26 = json.loads((R1B / "g26_rounds_r1b.json").read_text())
    fig, (a, b) = plt.subplots(1, 2, figsize=(4.3, 2.6), gridspec_kw={"width_ratios": [1.15, 1]})
    groups = [("AF", "predicted\nAF (labor)", C_AF), ("FM", "predicted\nFM (herd)", C_FM), ("none", "no\nprediction", C_NONE)]
    lo_clip = -10.5
    a.axhspan(lo_clip, 0, color="#f3f2ee", lw=0, zorder=0)
    a.axhline(0, color=INK2, lw=0.7)
    a.text(2.45, -0.6, "spread", fontsize=6, color=INK2, ha="right", va="top")
    a.text(2.45, 0.5, "herding", fontsize=6, color=INK2, ha="right", va="bottom")
    for xi, (key, lab, col) in enumerate(groups):
        d = v.filter(pl.col("cls").str.starts_with(key)).sort("bj_cw")
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
    a.set_ylabel(r"$\beta J_{CW}$ (shared labels, round 1b)")
    a.yaxis.grid(True, color=GRID, lw=0.5)
    a.set_axisbelow(True)
    a.set_title("a  Herding whatever the mode", loc="left")
    a.scatter([], [], marker="o", color=INK2, s=18, label="filled: |t| > t$_{crit}$")
    a.scatter([], [], marker="^", facecolor="white", edgecolor=INK2, s=18, label="own-artifact week")
    a.legend(loc="lower left", bbox_to_anchor=(0.0, 0.2), fontsize=5.2, handletextpad=0.2, borderaxespad=0.2)

    for rnd, col, lab in (("runoff", C_FM, "01-05 runoff"), ("confirmatory", C_AF, "01-09 confirmatory")):
        tr = g26[rnd]["trajectory"]
        t = np.array([x["t_s"] for x in tr])
        n = np.array([x["n"] for x in tr])
        k = np.round(np.array([x["share"] for x in tr]) * n)
        b.step(np.r_[0, t, 120], np.r_[0, n, n[-1]], where="post", color=col, lw=0.9, ls="--")
        b.step(np.r_[0, t, 120], np.r_[0, k, k[-1]], where="post", color=col, lw=1.8, label=lab)
    b.plot([], [], color=INK2, lw=0.9, ls="--", label="all ballots cast")
    b.plot([], [], color=INK2, lw=1.8, label="ballots for the winner")
    b.set_ylim(0, 9.8)
    b.set_xlim(0, 120)
    b.set_xticks([0, 30, 60, 90, 120])
    b.set_xlabel("seconds since the round opened")
    b.set_ylabel("ballots")
    b.yaxis.grid(True, color=GRID, lw=0.5)
    b.set_axisbelow(True)
    b.set_title("b  #26 per round (DQ6)", loc="left")
    b.text(118, 0.4, "approval round before:\n9–9–9 tie among 3", fontsize=5.2, color=INK2, ha="right", va="bottom")
    b.legend(loc="upper left", fontsize=5.0, handletextpad=0.3, borderaxespad=0.2)
    fig.tight_layout(pad=0.3, w_pad=0.8)
    fig.savefig(FIG / "summary_obs_r1b.pdf")
    fig.savefig(FIG / "summary_obs_r1b.png", dpi=200)
    plt.close(fig)


def page2():
    wv = pl.read_parquet(R1B / "work_vs_attention_r1b.parquet")
    a_ = wv.filter(pl.col("space") == "attention")
    w_ = wv.filter(pl.col("space") == "work")
    j = a_.join(w_, on=["unit", "goal"], suffix="_w").sort("goal", "unit")
    jp = j.filter(pl.col("goal") < 51)
    fig, (a, b) = plt.subplots(1, 2, figsize=(4.3, 2.05), gridspec_kw={"width_ratios": [1, 1.25]})
    lab = lambda u: u.replace("G", "#") if u.startswith("G") else u
    for i, r in enumerate(jp.iter_rows(named=True)):
        za, zw = r["z_N2"], r["z_N2_w"]
        own = r["goal"] in OWN or (r["own_w"] is not None and r["own_w"] >= 0.5)
        if za == za and zw == zw:
            a.plot([i, i], [za, zw], color=GRID, lw=1.2, zorder=1)
        if za == za:
            a.scatter([i], [min(za, 15)], s=16, color=C_FM, marker="^" if own else "o", zorder=3, lw=0)
        if zw == zw and r["tested_w"]:
            a.scatter([i], [min(zw, 15)], s=16, color="white", edgecolor=C_AF, marker="^" if own else "o", zorder=3, lw=1.1)
        elif r["goal"] == 39:
            a.text(i, -2.3, "all\nprivate", fontsize=4.3, color=C_AF, ha="center", va="top")
        elif not r["tested_w"]:
            a.text(i, -3.1, "too\nsparse", fontsize=4.3, color=INK2, ha="center", va="top")
    a.axhline(2, color=INK2, lw=0.6, ls="--")
    a.axhline(0, color=INK2, lw=0.5)
    a.set_xticks(np.arange(jp.height), [lab(u) for u in jp["unit"].to_list()], rotation=90, fontsize=5)
    a.set_ylim(-4.5, 15.5)
    a.set_ylabel("z, coupling beyond agent\nfields vs circular shift", fontsize=6)
    a.set_title("a  Herding: attention vs work", loc="left")
    a.scatter([], [], s=14, color=C_FM, label="attention")
    a.scatter([], [], s=14, color="white", edgecolor=C_AF, lw=1.1, label="work (commits)")
    a.scatter([], [], s=14, color=INK2, marker="^", label="own-artifact")
    a.legend(loc="upper right", fontsize=4.8, handletextpad=0.2, borderaxespad=0.1)
    a.yaxis.grid(True, color=GRID, lw=0.5)
    a.set_axisbelow(True)
    ys = np.arange(j.height)
    for y, r in zip(ys, j.iter_rows(named=True)):
        b.plot([r["cowork_w"], r["cowork"]], [y, y], color=GRID, lw=1.4, zorder=1)
        b.scatter([r["cowork"]], [y], s=14, color=C_FM, zorder=3, lw=0)
        b.scatter([r["cowork_w"]], [y], s=14, color="white", edgecolor=C_AF, lw=1.1, zorder=3)
    b.set_yticks(ys, [lab(u) for u in j["unit"].to_list()], fontsize=5)
    b.invert_yaxis()
    b.set_xlim(-0.02, 1.02)
    b.set_xlabel("share of labelled agents sharing their\nrepo with a room-mate (same 30 min)", fontsize=6)
    b.set_title("b  Co-location", loc="left")
    b.xaxis.grid(True, color=GRID, lw=0.5)
    b.set_axisbelow(True)
    fig.tight_layout(pad=0.3, w_pad=0.6)
    fig.savefig(FIG / "r1b_work_vs_attention.pdf")
    fig.savefig(FIG / "r1b_work_vs_attention.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    page1()
    page2()
