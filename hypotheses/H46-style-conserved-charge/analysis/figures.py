"""H46 figures: summary_obs (conservation map), summary_obsb (fingerprint + KW), per-period/NE figures."""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h46lib as L  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

FIG = L.ROOT / "hypotheses/H46-style-conserved-charge/figures"
PDIR = L.ROOT / "hypotheses/H46-style-conserved-charge/goalperiod-subhypotheses"
COL = {"goal": "#1f77b4", "rooms": "#d62728", "nudger": "#9467bd", "roster": "#2ca02c", "scaffold": "#ff7f0e",
       "goal_skip": "#7f7f7f", "NE41": "#000000"}
NAME = {"goal": "goal switch (NE34)", "rooms": "rooms (NE42)", "nudger": "nudger off (NE43)", "roster": "roster",
        "scaffold": "scaffold", "NE41": "erasure (NE41)"}


def conservation_map(ax, rows, cons, ne41):
    for c in ("goal", "rooms", "nudger", "roster", "scaffold"):
        sub = rows.filter(pl.col("cls") == c).group_by("label").agg(pl.col("r_style").mean(), pl.col("r_content").mean())
        ax.scatter(sub["r_content"], sub["r_style"], s=10, color=COL[c], alpha=0.45, lw=0)
        t = cons["tests"][c]
        ax.errorbar(t["content"]["T"], t["style"]["T"], xerr=[[t["content"]["T"] - t["content"]["lo"]], [t["content"]["hi"] - t["content"]["T"]]],
                    yerr=[[t["style"]["T"] - t["style"]["lo"]], [t["style"]["hi"] - t["style"]["T"]]], fmt="o", ms=5,
                    color=COL[c], mec="k", mew=0.5, capsize=1.5, lw=0.8, label=NAME[c])
    for k, mk in (("forced", "s"), ("voluntary", "^")):
        tc, ts = ne41["dedup"]["content"][k], ne41["dedup"]["style"][k]
        ax.errorbar(tc["T"], ts["T"], xerr=[[tc["T"] - tc["lo"]], [tc["hi"] - tc["T"]]], yerr=[[ts["T"] - ts["lo"]], [ts["hi"] - ts["T"]]],
                    fmt=mk, ms=5, color="k", mfc="w", capsize=1.5, lw=0.8, label=f"erasure, {k} (NE41)")
    ax.axhspan(0.4, 0.6, color="0.85", zorder=0)
    ax.axhline(0.5, color="0.5", lw=0.6)
    ax.axvline(0.5, color="0.5", lw=0.6)
    ax.plot([0, 1], [0, 1], ls=":", color="0.4", lw=0.7)
    ax.set_xlim(0.2, 1.0)
    ax.set_ylim(0.2, 1.0)
    ax.set_xlabel("content: boundary percentile vs own day-to-day", fontsize=7)
    ax.set_ylabel("style (type-controlled) percentile", fontsize=7)
    ax.tick_params(labelsize=6)
    ax.legend(fontsize=5, frameon=False, loc="upper left")


def fingerprint_panel(ax, fp):
    f = fp.filter((pl.col("family") == "all") & pl.col("cls").is_in(["goal", "rooms", "roster", "scaffold", "nudger"]))
    piv = f.pivot(values="cross", index=["label", "cls", "chance"], on="variant")
    for c in ("goal", "rooms", "nudger", "roster", "scaffold"):
        sub = piv.filter(pl.col("cls") == c)
        ax.scatter(sub["content"], sub["style"], s=12, color=COL[c], alpha=0.8, lw=0, label=NAME[c])
    ax.plot([0, 1], [0, 1], ls=":", color="0.4", lw=0.7)
    ch = float(piv["chance"].mean())
    ax.axhline(ch, color="0.6", lw=0.6)
    ax.axvline(ch, color="0.6", lw=0.6)
    ax.text(ch + 0.01, 0.02, "mean chance", fontsize=5, color="0.4")
    ax.set_xlim(0, 1.02)
    ax.set_ylim(0, 1.02)
    ax.set_xlabel("content: balanced accuracy, train before / test after", fontsize=7)
    ax.set_ylabel("style: balanced accuracy", fontsize=7)
    ax.tick_params(labelsize=6)
    ax.legend(fontsize=5, frameon=False, loc="lower right")


def obsb():
    ph = json.loads((L.DATA / "posthoc.json").read_text())
    g51 = json.loads((L.DATA / "G51/native.json").read_text())
    g12 = json.loads((L.DATA / "G12/native.json").read_text())
    roster = pl.read_parquet(L.SH / "roster.parquet")
    lab = dict(zip(roster["agent"].to_list(), roster["lab"].to_list()))
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.4))
    bins = ["1", "2", "3", "4-6", "7+"]
    for key, col, nm, sc in (("style", "#1f77b4", "style (sq. distance)", 1.0), ("content", "#d62728", "content (1-cos) x 100", 100.0)):
        w = ph["PH3"][key]["within_long_segments"]
        y = [w[b]["mean_excess"] * sc for b in bins]
        e = [1.96 * w[b]["se"] * sc for b in bins]
        ax[0].errorbar(np.arange(5) + (0.08 if key == "content" else 0), y, yerr=e, marker="o", ms=3.5, color=col, lw=1, capsize=2, label=nm)
    ax[0].axhline(0, color="0.5", lw=0.6)
    ax[0].set_xticks(np.arange(5), bins)
    ax[0].set_xlabel("message position since the last context reset", fontsize=7)
    ax[0].set_ylabel("excess distance to agent's own mean", fontsize=7)
    ax[0].set_title("(a) style drifts in context, resets at erasure", fontsize=8)
    ax[0].legend(fontsize=5.5, frameon=False)
    ax[0].tick_params(labelsize=6)
    A = g51["agents"]
    items = sorted(A.items(), key=lambda kv: kv[1]["pct_style"])
    xs = np.arange(len(items))
    cols = ["#d62728" if v["group"] == "prankster" else ("#ff7f0e" if v["group"] == "media" else "#7f7f7f") for _, v in items]
    mk = ["o" if lab[int(a)] == "Anthropic" else "s" for a, _ in items]
    for x_, (a, v), c_, m_ in zip(xs, items, cols, mk):
        ax[1].scatter(x_, v["pct_style"], color=c_, marker=m_, s=16, zorder=3)
    jx = len(items) + 1.0
    js = list(g12["onetime_judges_style"].values())
    jc = list(g12["onetime_judges_content"].values())
    ax[1].scatter([jx] * len(js), [v["pct"] for v in js], color="#9467bd", marker="D", s=14, zorder=3)
    ax[1].scatter([jx + 1] * len(jc), [v["pct"] for v in jc], color="#9467bd", marker="D", s=14, facecolor="w", zorder=3)
    ax[1].axhline(0.9, color="0.4", lw=0.6, ls=":")
    ax[1].axhline(0.5, color="0.6", lw=0.6)
    ax[1].set_xticks(list(xs) + [jx, jx + 1], [""] * len(xs) + ["judges:\nstyle", "judges:\ncontent"], fontsize=5)
    ax[1].set_ylabel("percentile vs own placebo", fontsize=7)
    ax[1].set_title("(b) #51 incumbents into roles; #12 judges", fontsize=8)
    ax[1].tick_params(labelsize=6)
    from matplotlib.lines import Line2D
    h = [Line2D([], [], color="#d62728", marker="o", ls="", ms=4, label="Prankster"),
         Line2D([], [], color="#ff7f0e", marker="o", ls="", ms=4, label="media roles"),
         Line2D([], [], color="#7f7f7f", marker="o", ls="", ms=4, label="other roles"),
         Line2D([], [], color="k", marker="o", ls="", ms=4, mfc="w", label="circle Anthropic, square other lab")]
    ax[1].legend(handles=h, fontsize=5, frameon=False, loc="upper left")
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"summary_obsb.{ext}", dpi=200)
    plt.close(fig)


def main():
    rows = pl.read_parquet(L.DATA / "conservation_rows.parquet")
    cons = json.loads((L.DATA / "conservation.json").read_text())
    ne41 = json.loads((L.DATA / "NE41/ne41.json").read_text())
    fp = pl.read_parquet(L.DATA / "fingerprint.parquet")
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 3.0))
    conservation_map(ax[0], rows, cons, ne41)
    ax[0].set_title("(a) conservation map: one dot per boundary", fontsize=8)
    fingerprint_panel(ax[1], fp)
    ax[1].set_title("(b) identity across boundaries (one dot each)", fontsize=8)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"summary_obs.{ext}", dpi=200)
    plt.close(fig)
    obsb()


if __name__ == "__main__":
    main()
