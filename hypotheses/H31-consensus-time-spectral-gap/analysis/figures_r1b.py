"""H31 round-1b summary figure (figures/r1b_rounds_work.pdf; reads round-1b outputs only).

(a) #26 per election round (DQ6 ballots): cumulative ballots and cumulative first readers of the opening message
    (context ledger) against seconds since the round opened; consensus instant marked.
(b) Gradual consensus times per block, attention vs work labels, periods #30 onward (same blocks).

Usage: uv run python hypotheses/H31-consensus-time-spectral-gap/analysis/figures_r1b.py
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
R1B = ROOT / "data/processed/H31-consensus-time-spectral-gap/r1b"
FIG = HERE.parent / "figures"
C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
ROOMS = {0: "#general", 2: "#best", 3: "#rest", 4: "#univ"}
plt.rcParams.update({"font.size": 7, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "axes.titlesize": 7.2,
                     "axes.titleweight": "bold", "legend.frameon": False, "pdf.fonttype": 42})


def classify(ep):
    c = ep.filter(pl.col("consensus"))
    return c.with_columns(pl.when(~pl.col("frozen")).then(pl.lit("gradual"))
                          .when(pl.col("t0_h") > 0.75 + 1e-6).then(pl.lit("instant")).otherwise(pl.lit("frozen")).alias("kind"))


def main():
    ev = json.loads((R1B / "ev26.json").read_text())["rounds"]
    fig, (a, b) = plt.subplots(1, 2, figsize=(4.3, 2.05), gridspec_kw={"width_ratios": [1.1, 1]})
    for rnd, col in (("runoff", C2), ("confirmatory", C1)):
        x = ev[rnd]
        tb = np.array([p["t_s"] for p in x["trajectory"]])
        nb = np.array([p["n"] for p in x["trajectory"]])
        a.step(np.r_[0, tb, 120], np.r_[0, nb, nb[-1]], where="post", color=col, lw=1.6, label=f"{rnd} ballots")
        lr = np.array(x["readout"]["lags_s"])
        a.step(np.r_[0, lr, 120], np.r_[0, np.arange(1, len(lr) + 1), len(lr)], where="post", color=col, lw=0.8, ls=":")
        a.axvline(x["tau_V_s"], color=col, lw=0.6, ls="--")
    a.plot([], [], color=INK2, lw=0.8, ls=":", label="agents that read the opening")
    a.plot([], [], color=INK2, lw=0.6, ls="--", label="consensus (≥ 3 ballots, ≥ 50%)")
    a.set_xlim(0, 120)
    a.set_ylim(0, 13.5)
    a.set_yticks([0, 3, 6, 9])
    a.set_xticks([0, 30, 60, 90, 120])
    a.set_xlabel("seconds since the round opened")
    a.set_ylabel("count")
    a.set_title("a  #26 votes: read-out speed", loc="left")
    a.legend(loc="upper left", bbox_to_anchor=(0.0, 1.0), fontsize=4.6, handletextpad=0.3, borderaxespad=0.1)
    a.yaxis.grid(True, color=GRID, lw=0.5)
    a.set_axisbelow(True)
    a.text(118, 0.3, "λ₂ forecast: 1.1 h\n(80%: 0.2–5.2 h)", fontsize=5.0, color=INK2, va="bottom", ha="right")

    ea = classify(pl.read_parquet(R1B / "events_ep_w30.parquet")).filter((pl.col("goal_no") >= 30) & (pl.col("kind") == "gradual"))
    ew = classify(pl.read_parquet(R1B / "events_ep_w30_work.parquet")).filter((pl.col("goal_no") >= 30) & (pl.col("kind") == "gradual"))
    blocks = sorted(set(map(tuple, ea.select("goal_no", "room").rows())) | set(map(tuple, ew.select("goal_no", "room").rows())))
    for i, (g, r) in enumerate(blocks):
        ta = ea.filter((pl.col("goal_no") == g) & (pl.col("room") == r))["tau_h"].to_numpy()
        tw = ew.filter((pl.col("goal_no") == g) & (pl.col("room") == r))["tau_h"].to_numpy()
        b.scatter(ta, np.full(len(ta), i - 0.12), s=14, color=C2, lw=0, zorder=3)
        b.scatter(tw, np.full(len(tw), i + 0.12), s=14, color="white", edgecolor=C1, lw=1.0, zorder=3)
    b.set_xscale("log")
    b.set_xlim(0.2, 30)
    b.set_yticks(range(len(blocks)), [f"#{g} {ROOMS.get(r, r)}" for g, r in blocks], fontsize=5)
    b.invert_yaxis()
    b.axvline(float(np.median(ea["tau_h"])), color=C2, lw=0.6, ls="--")
    b.axvline(float(np.median(ew["tau_h"])), color=C1, lw=0.6, ls="--")
    b.set_xlabel("gradual consensus time (active h)")
    b.set_title("b  Attention vs work", loc="left")
    b.scatter([], [], s=14, color=C2, label="attention")
    b.scatter([], [], s=14, color="white", edgecolor=C1, lw=1.0, label="work (commits)")
    b.legend(loc="lower right", fontsize=5, handletextpad=0.2, borderaxespad=0.1)
    b.xaxis.grid(True, color=GRID, lw=0.5)
    b.set_axisbelow(True)
    fig.tight_layout(pad=0.3, w_pad=0.6)
    fig.savefig(FIG / "r1b_rounds_work.pdf")
    fig.savefig(FIG / "r1b_rounds_work.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    main()
