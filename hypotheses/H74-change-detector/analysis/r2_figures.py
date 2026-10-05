"""H74 round 2 summary figure: (a, b) operating points, out-of-sample P2 per-day FAR vs hit on the pooled platform/drive/
undocumented events and on goal kickoffs; (c) the D3 counter channel over all non-reserved days with its LOPO threshold.
Run after r2_monitor.py (both catalogs): uv run python hypotheses/H74-change-detector/analysis/r2_figures.py
Output: hypotheses/H74-change-detector/figures/r2_summary.pdf
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data/processed/H74-change-detector/r2"
FIG = ROOT / "hypotheses/H74-change-detector/figures"
BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN, VIOLET, RED = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4",
                                                          "#008300", "#4a3aa7", "#e34948")
INK, INK2 = "#0b0b0b", "#52514e"


def main():
    mj = json.loads((OUT / "monitor.json").read_text())
    mx = json.loads((OUT / "monitor_ext.json").read_text())
    pts = [("round-1 fused, z ≥ 4", mj["round1_fused"], INK2, "s"),
           ("round-1 fused, LOPO", mj["round1_fused_lopo"], INK2, "x"),
           ("C3 alone", mj["channels"]["C3"], AQUA, "o"),
           ("S alone", mj["channels"]["S"], BLUE, "o"),
           ("D3 alone", mj["channels"]["D3"], ORANGE, "o"),
           ("monitor S∪D3∪C3", mj["monitor"], VIOLET, "D"),
           ("monitor, + provider dates*", mx["monitor"], VIOLET, "d"),
           ("monitor, C3 LOPO, + provider dates*", mx["monitor_C3_lopo"], MAGENTA, "d")]
    fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.6), gridspec_kw={"width_ratios": [1, 1, 1.35]})
    for k, (key, title) in enumerate((("pool", "platform + drive + undocumented (45)"), ("goal", "goal kickoffs (35)"))):
        a = ax[k]
        for lab, s, c, m in pts:
            far = s["far"]["P2"]["per_day"]
            h = s["pooled_platform"]["hit"] if key == "pool" else s["classes"]["goal"]["hit"]
            a.plot(far, h, m, color=c, ms=6, mec="white" if m not in "x" else c, mew=0.8, label=lab)
        a.axvline(0.02, color=INK2, lw=0.6, ls=":")
        a.axvline(0.05, color=INK2, lw=0.6, ls="--")
        a.set_xlim(-0.01, 0.23); a.set_ylim(-0.03, 0.9)
        a.set_xlabel("out-of-sample FAR per placebo day (P2)", fontsize=6.5)
        a.set_ylabel("hit (alarm on day −1..+1)", fontsize=6.5)
        a.set_title(f"({'ab'[k]}) {title}", fontsize=7)
        a.tick_params(labelsize=6)
        for sp in ("top", "right"):
            a.spines[sp].set_visible(False)
    ax[1].legend(fontsize=4.8, loc="lower right", frameon=False, bbox_to_anchor=(1.04, 0.1))
    md = pl.read_parquet(OUT / "monitor_days.parquet")
    x = np.arange(md.height)
    d3 = md["D3"].fill_nan(None).fill_null(0).to_numpy()
    a = ax[2]
    a.plot(x, np.clip(d3, 0, 12), color=ORANGE, lw=0.8, label="D3 score (clipped at 12)")
    a.plot(x, md["th_D3"].to_numpy(), color=INK2, lw=0.8, ls="--", label="LOPO threshold")
    p2 = md["P2"].to_numpy()
    a.plot(x[p2], np.full(p2.sum(), -0.6), "|", color=BLUE, ms=4, label="P2 placebo day")
    dl = md["pt_date"].to_list()
    for d, lab in (("2025-07-02", "NE39"), ("2026-08-06", "NE43a"), ("2026-08-21", "NE43b"), ("2026-04-29", "P2 false\nalarm")):
        if d in dl:
            i = dl.index(d)
            a.annotate(lab, (i, min(d3[i], 12)), xytext=(0, 6), textcoords="offset points", fontsize=5.5, ha="center", color=INK)
    ticks = [i for i, d in enumerate(dl) if d.endswith("-01")][::2]
    a.set_xticks(ticks, [dl[i][2:7] for i in ticks], fontsize=5.5, rotation=45)
    a.set_ylim(-1.2, 13.5)
    a.set_ylabel("operator-counter score", fontsize=6.5)
    a.set_title("(c) D3: bookends, nudges, human messages", fontsize=7)
    a.legend(fontsize=5, frameon=False, loc="upper left")
    a.tick_params(labelsize=6)
    for sp in ("top", "right"):
        a.spines[sp].set_visible(False)
    fig.text(0.01, 0.005, "* post hoc: round-1 provider format dates added to the catalog. Dotted / dashed lines: FAR 0.02 / 0.05.",
             fontsize=5, color=INK2)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / "r2_summary.pdf")


if __name__ == "__main__":
    main()
