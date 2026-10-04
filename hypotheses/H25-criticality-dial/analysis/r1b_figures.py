"""H25 round 1b figure: (a) period dials, round 1 (old table) vs round 1b (fixed table), activity and talk, plus the
activity dial with the DQ8 trim; (b) NE42 A-B-A (#39 two rooms, #40 one room, #41 two rooms): period random-effects
dials for activity and talk with 90% intervals.
Output: hypotheses/H25-criticality-dial/figures/r1b_dial.{png,pdf}
Usage: uv run python hypotheses/H25-criticality-dial/analysis/r1b_figures.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import polars as pl  # noqa: E402

HYP = Path(__file__).resolve().parents[1]
DATA = HYP.parents[1] / "data/processed/H25-criticality-dial"


def pcol(per, ch, v, col="fe"):
    return per.filter((pl.col("channel") == ch) & (pl.col("variant") == v)).select("goal_no", pl.col(col).alias(f"{ch}_{v}"))


def main():
    po, pn = pl.read_parquet(DATA / "dial_period.parquet"), pl.read_parquet(DATA / "r1b/dial_period.parquet")
    a = (pcol(po, "activity", "auto").rename({"activity_auto": "act_old"}).join(pcol(pn, "activity", "auto"), on="goal_no")
         .join(pcol(pn, "activity", "trim", "median"), on="goal_no", how="left")
         .join(pcol(po, "talk", "auto").rename({"talk_auto": "talk_old"}), on="goal_no", how="left").join(pcol(pn, "talk", "auto"), on="goal_no", how="left"))
    nat = json.loads((DATA / "r1b/native/native.json").read_text())["NE42"]
    fig, ax = plt.subplots(1, 2, figsize=(7.4, 3.0), gridspec_kw={"width_ratios": [1.1, 1]})
    ax[0].scatter(a["act_old"], a["activity_auto"], s=16, color="#2a6fb0", label="activity (stalls masked)")
    ax[0].scatter(a["act_old"], a["activity_trim"], s=16, color="#e45756", marker="s", label="activity, DQ8 trim (median)")
    ax[0].scatter(a["talk_old"], a["talk_auto"], s=16, color="#d08c2a", marker="^", label="talk (stalls masked)")
    lim = [-0.15, 0.5]
    ax[0].plot(lim, lim, "k-", lw=0.6); ax[0].axhline(0, color="k", lw=0.4); ax[0].axvline(0, color="k", lw=0.4)
    ax[0].set_xlim(lim); ax[0].set_ylim(lim)
    ax[0].set_xlabel("period dial, round 1 (old table)", fontsize=8); ax[0].set_ylabel("period dial, round 1b (fixed table)", fontsize=8)
    ax[0].legend(fontsize=6.3, frameon=False, loc="upper left"); ax[0].tick_params(labelsize=7)
    ax[0].set_title("(a) 35 periods: restored events raise the dial", fontsize=8)
    for k, (ch, c, dx) in enumerate((("activity", "#2a6fb0", -0.08), ("talk", "#d08c2a", 0.08))):
        ps = nat[ch]["periods"]
        xs = [0, 1, 2]
        ys = [ps[str(g)]["re"] for g in (39, 40, 41)]
        es = [1.645 * ps[str(g)]["se_re"] for g in (39, 40, 41)]
        ax[1].errorbar([x + dx for x in xs], ys, yerr=es, fmt="o-", color=c, ms=4, lw=1, capsize=2, label=ch)
    ax[1].axhline(0, color="k", lw=0.4)
    ax[1].set_xticks([0, 1, 2], ["#39\ntwo rooms", "#40\none room", "#41\ntwo rooms"], fontsize=7)
    ax[1].set_ylabel("period dial g (random effects, 90%)", fontsize=8); ax[1].tick_params(labelsize=7)
    ax[1].legend(fontsize=7, frameon=False, loc="upper right")
    ax[1].set_title("(b) NE42 merge and split, 15 agents", fontsize=8)
    fig.tight_layout()
    fig.savefig(HYP / "figures/r1b_dial.png", dpi=170); fig.savefig(HYP / "figures/r1b_dial.pdf")
    print("written")


if __name__ == "__main__":
    main()
