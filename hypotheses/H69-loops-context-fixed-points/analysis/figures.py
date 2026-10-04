"""H69 figures: figures/summary_obs.pdf (effects forest) and figures/summary_obs2.pdf (synthetic size and power)."""
from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
D = ROOT / "data/processed/H69-loops-context-fixed-points"
FIG = HERE.parent / "figures"
COL = {"G38": "#2a78d6", "G40": "#e3a21a", "G41": "#0ca30c", "G51": "#c43a3a"}

ROWS = [  # label, per-period getter (result key, b key, se key), pooled key
    ("onset: own statements in context", ("onset", "b_O", "se_O"), "b_O"),
    ("onset: room items in context", ("onset", "b_K", "se_K"), "b_K"),
    ("onset after a forced erasure", ("onset_forced", "b", "se"), "onset_forced"),
    ("exit: forced erasure", ("exit", "b_forced_between", "se_forced_between"), "exit_forced"),
    ("exit: voluntary erasure", ("exit", "b_vol_between", "se_vol_between"), "exit_vol"),
    ("exit: novel items read", ("exit", "b_nov_read", "se_nov_read"), "exit_nov_read"),
    ("exit: novel items in flight (placebo)", ("exit", "b_nov_infl", "se_nov_infl"), "exit_nov_infl"),
    ("exit: next-call items (placebo)", ("exit", "b_nov_read_next", "se_nov_read_next"), "exit_nov_next"),
    ("source in context vs erased (MH)", ("enrich", "log_or", "se"), "enrich"),
    ("pseudo-erasure (same vs other half)", ("pseudo", "log_or", "se"), "pseudo"),
]


def main():
    FIG.mkdir(exist_ok=True)
    r = json.loads((D / "results.json").read_text())
    per, po = r["periods"], r["pooled"]
    fig, ax = plt.subplots(figsize=(4.6, 3.3))
    y0 = np.arange(len(ROWS))[::-1]
    for yi, (lab, (k, bk, sk), pk) in zip(y0, ROWS):
        for j, p in enumerate(COL):
            d = per[p].get(k) or {}
            b, s = d.get(bk), d.get(sk)
            if b is None or s is None or not (math.isfinite(b) and math.isfinite(s)):
                continue
            yy = yi + 0.12 * (j - 1.5)
            ax.plot([b - 1.96 * s, b + 1.96 * s], [yy, yy], color=COL[p], lw=0.8, alpha=0.7)
            ax.plot(b, yy, "o", ms=2.5, color=COL[p])
        q = po[pk]
        if q.get("k"):
            ax.plot([q["lo"], q["hi"]], [yi - 0.38, yi - 0.38], color="black", lw=1.6)
            ax.plot(q["mean"], yi - 0.38, "D", ms=4, color="black")
    ax.axvline(0, color="gray", lw=0.6)
    ax.axvline(math.log(2), color="gray", lw=0.6, ls=":")
    ax.set_yticks(y0)
    ax.set_yticklabels([x[0] for x in ROWS], fontsize=6.5)
    ax.set_xlabel("log odds ratio (per unit, or per log count)", fontsize=7)
    ax.tick_params(axis="x", labelsize=7)
    for p, c in COL.items():
        ax.plot([], [], "o", color=c, ms=3, label=p)
    ax.plot([], [], "D", color="black", ms=3, label="pooled (RE)")
    ax.legend(fontsize=5.5, loc="lower right", frameon=False)
    ax.set_xlim(-2.5, 3.5)
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs.pdf")
    plt.close(fig)

    w = pl.read_parquet(D / "synthetic/worlds.parquet").filter(pl.col("period").is_in(list(COL)))
    stats = [("P1 b_s>0", "z_s", 1), ("P1 b_K<0", "z_K", -1), ("P3 forced", "z_forced_between", 1),
             ("P5 novel read", "z_nov_read", 1)]
    fig, ax = plt.subplots(figsize=(4.6, 1.9))
    xs = np.arange(len(stats) + 1)
    for j, (wd, c) in enumerate((("Z0", "#9aa0a6"), ("Z1", "#2a78d6"), ("Z2", "#e3a21a"))):
        sub = w.filter(pl.col("world") == wd)
        vals = []
        for _, col, sgn in stats:
            z = sub[col].to_numpy().astype(float)
            z = z[np.isfinite(z)]
            vals.append(float(np.mean(z * sgn > 1.96)) if len(z) else np.nan)
        lo = sub["lor_lo"].to_numpy().astype(float)
        lo = lo[np.isfinite(lo)]
        vals.append(float(np.mean(lo > 0)) if len(lo) else np.nan)
        ax.bar(xs + 0.27 * (j - 1), vals, 0.26, color=c, label={"Z0": "Z0 recency null", "Z1": "Z1 H69",
                                                                  "Z2": "Z2 starvation"}[wd])
    ax.axhline(0.05, color="black", lw=0.6, ls=":")
    ax.axhline(0.8, color="black", lw=0.6, ls="--")
    ax.set_xticks(xs)
    ax.set_xticklabels([s[0] for s in stats] + ["P4 enrichment"], fontsize=6.5)
    ax.set_ylabel("rejection rate", fontsize=7)
    ax.tick_params(axis="y", labelsize=7)
    ax.legend(fontsize=6, frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.22))
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs2.pdf")
    plt.close(fig)


if __name__ == "__main__":
    main()
