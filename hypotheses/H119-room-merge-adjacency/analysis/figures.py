"""H119 summary figures: NE42 block couplings (E1 class model, full J, daily) and E2 read vs in-flight; synthetic."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
D = ROOT / "data/processed/H119-room-merge-adjacency"
FIG = ROOT / "hypotheses/H119-room-merge-adjacency/figures"
B, O, INK = "#2a78d6", "#eb6834", "#52514e"
plt.rcParams.update({"font.size": 7, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": INK,
                     "xtick.color": INK, "ytick.color": INK})
Z = 1.959964


def obs():
    w = json.loads((D / "ne42_weeks.json").read_text())["contrasts"]
    dd = pl.read_parquet(D / "ne42_days.parquet")
    e2 = pl.read_parquet(D / "e2_ne42.parquet")
    fig, ax = plt.subplots(1, 3, figsize=(7.0, 2.3))
    x = np.arange(3); weeks = ["39", "40", "41"]
    for off, cls, c, nm in ((-0.08, "within", B, "within (always co-located)"), (0.08, "cross", O, "cross (co-located in #40 only)")):
        k = "Jw" if cls == "within" else "Jx"
        v = [w[f"{k}_{wk}"] for wk in weeks]; se = [w[f"se_{cls}_{wk}"] for wk in weeks]
        ax[0].errorbar(x + off, v, yerr=Z * np.array(se), fmt="o", ms=4, color=c, lw=1, capsize=0, label=nm)
    ax[0].axvspan(0.6, 1.4, color="#ecebe6", zorder=0); ax[0].axhline(0, color=INK, lw=0.6)
    ax[0].set_xticks(x); ax[0].set_xticklabels(["#39", "#40 merged", "#41"]); ax[0].set_ylabel("per-pair J (logistic units)")
    ax[0].legend(frameon=False, fontsize=5.5, loc="upper left"); ax[0].set_title("(a) E1 class model by week", fontsize=7, loc="left")
    dd = dd.with_columns(pl.int_range(pl.len()).alias("i"))
    for col, c, nm in (("Jw", B, "within"), ("Jx", O, "cross")):
        ax[1].plot(dd["i"], dd[col], "-o", ms=3, lw=1.2, color=c, label=nm)
    ax[1].axvspan(4.5, 9.5, color="#ecebe6", zorder=0); ax[1].axhline(0, color=INK, lw=0.6)
    ax[1].set_xticks([2, 7, 12]); ax[1].set_xticklabels(["#39", "#40", "#41"]); ax[1].set_xlabel("day")
    ax[1].legend(frameon=False, fontsize=5.5); ax[1].set_title("(b) daily J (no step at 05-04 or 05-11)", fontsize=7, loc="left")
    for off, cls, c in ((-0.08, "within", B), (0.08, "cross", O)):
        v, lo, hi = [], [], []
        for wk in weeks:
            r = e2.filter(pl.col("week") == wk).to_dicts()[0]
            v.append(r[f"CRU_{cls}"]); lo.append(r[f"CRU_{cls}_lo"]); hi.append(r[f"CRU_{cls}_hi"])
        v, lo, hi = map(lambda a: np.array(a, float), (v, lo, hi))
        ax[2].errorbar(x + off, v, yerr=[v - lo, hi - v], fmt="o", ms=4, color=c, lw=1, capsize=0)
    ax[2].axvspan(0.6, 1.4, color="#ecebe6", zorder=0); ax[2].axhline(0, color=INK, lw=0.6)
    ax[2].set_xticks(x); ax[2].set_xticklabels(["#39", "#40 merged", "#41"]); ax[2].set_ylabel("J$^R$ − J$^U$ (per call)")
    ax[2].set_title("(c) E2 read minus in-flight", fontsize=7, loc="left")
    fig.tight_layout(); fig.savefig(FIG / "summary_obs.pdf"); plt.close(fig)


def syn():
    s = json.loads((D / "synthetic/p0_summary.json").read_text())
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 1.9))
    arms = [("coupling_0.3", "coupling J 0.3"), ("coupling_0.6", "coupling J 0.6"), ("roomdrive_0.0", "room drive only"),
            ("remanence_0.6", "coupling + remanence")]
    st = [("M_detect", "M > 0"), ("MD_detect", "M_D > 0"), ("Rm_detect", "Rm > 0")]
    for k, (key, nm) in enumerate(st):
        ax[0].bar(np.arange(4) + (k - 1) * 0.27, [s["e1"][a][key] for a, _ in arms], 0.25,
                  color=[B, O, INK][k], label=nm)
    ax[0].set_xticks(range(4)); ax[0].set_xticklabels([n for _, n in arms], fontsize=5.5)
    ax[0].set_ylabel("detection rate"); ax[0].legend(frameon=False, fontsize=5.5, ncol=3, loc="upper center")
    ax[0].set_ylim(0, 1.25); ax[0].set_title("(a) E1 on the NE42 skeleton", fontsize=7, loc="left")
    arms2 = [("read_J_0.3", "read J 0.3"), ("read_J_0.6", "read J 0.6"), ("drive_0.0", "room drive only")]
    for k, (key, nm) in enumerate((("CRU_x_detect", "J$^R$−J$^U$ > 0"), ("JUx_detect", "J$^U$ > 0"))):
        ax[1].bar(np.arange(3) + (k - 0.5) * 0.35, [s["e2"][a][key] for a, _ in arms2], 0.33, color=[B, INK][k], label=nm)
    ax[1].set_xticks(range(3)); ax[1].set_xticklabels([n for _, n in arms2], fontsize=6)
    ax[1].legend(frameon=False, fontsize=5.5); ax[1].set_ylim(0, 1.25)
    ax[1].set_title("(b) E2 cross class, real #40 call skeleton", fontsize=7, loc="left")
    fig.tight_layout(); fig.savefig(FIG / "summary_synthetic.pdf"); plt.close(fig)


if __name__ == "__main__":
    FIG.mkdir(exist_ok=True)
    obs(); syn()
