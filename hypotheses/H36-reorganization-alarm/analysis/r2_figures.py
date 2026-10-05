"""H36 round 2 figure (2026-10-05): figures/r2_summary.pdf, three panels.
(a) intraday: mean topic-shift z by 30-min window on kickoff days vs placebo days (bge; gte dashed);
(b) frozen C3 rule: hit vs window false-alarm rate in 6 embedding x dedupe variants, plus the seed spread;
(c) scaffold detection: AUC (window max vs placebo windows) per class for R5, schema diff S and H74's M.

Usage: uv run python hypotheses/H36-reorganization-alarm/analysis/r2_figures.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h36lib as L  # noqa: E402

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

R2 = L.OUT / "r2"
BLUE, ORANGE, AQUA, GRAY = "#2a78d6", "#eb6834", "#1baf7a", "#8a8984"
INK, INK2 = "#0b0b0b", "#52514e"
plt.rcParams.update({"font.size": 8, "axes.edgecolor": "#c9c7c0", "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": "white"})


def main():
    for layout in ("wide", "split"):
        draw(layout)


def draw(layout):
    """wide: figures/r2_summary.pdf (3 panels); split: figures/r2_obs.pdf (a, b) and figures/r2_scaffold_col.pdf (c)."""
    if layout == "wide":
        fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.4), constrained_layout=True)
    else:
        fig, ab = plt.subplots(1, 2, figsize=(4.6, 2.3), constrained_layout=True)
        fig2, c = plt.subplots(1, 1, figsize=(3.3, 2.0), constrained_layout=True)
        axs = [ab[0], ab[1], c]
    ax = axs[0]
    for tag, ls in (("bge", "-"), ("gte", "--")):
        o = json.loads((R2 / f"intraday_{tag}.json").read_text())
        W = range(0, 10)
        kz = [[k["z_by_win"].get(str(w)) for k in o["kickoffs"]] for w in W]
        km = [np.mean([x for x in col if x is not None]) if any(x is not None for x in col) else np.nan for col in kz]
        pz = [o["placebo_z_by_win"].get(str(w), np.nan) for w in W]
        ax.plot(list(W), km, ls, color=BLUE, lw=2, marker="o", ms=3, label=f"kickoff day ({tag})" if tag == "bge" else None)
        ax.plot(list(W), pz, ls, color=GRAY, lw=2, label="placebo day" if tag == "bge" else None)
    ax.axhline(3, color=INK2, lw=0.8, ls=":")
    ax.text(9, 3.2, "alarm z = 3", ha="right", va="bottom", fontsize=7, color=INK2)
    ax.set_xlabel("30-min window of the day"); ax.set_ylabel("mean intraday topic-shift z")
    ax.set_title("(a) R2: alarm in window 0", fontsize=8, loc="left")
    ax.legend(frameon=False, fontsize=7)

    ax = axs[1]
    rb = json.loads((R2 / "robust.json").read_text())
    for k, r in rb["variants"].items():
        m, dd = k.split("_")
        c = BLUE if m == "bge" else ORANGE
        mk = {"none": "o", "restate": "s", "copies": "^"}[dd]
        ax.scatter(r["C3"]["far_win_placebo"], r["C3"]["hit"], color=c, marker=mk, s=28, zorder=3, edgecolor="white", lw=0.8)
    for m, c in (("bge", BLUE), ("gte", ORANGE)):
        s = rb["seed_spread"][m]
        ax.scatter(s["C3_farwin"], s["C3_hit"], color=c, s=10, alpha=0.35, zorder=2)
    ax.axvline(0.15, color=INK2, lw=0.8, ls=":"); ax.axhline(0.45, color=INK2, lw=0.8, ls=":")
    ax.set_xlim(-0.01, 0.22); ax.set_ylim(0.4, 0.72)
    ax.set_xlabel("window false-alarm rate"); ax.set_ylabel("kickoff hit rate")
    ax.set_title("(b) frozen C3 rule", fontsize=8, loc="left")
    from matplotlib.lines import Line2D
    ax.legend(handles=[Line2D([], [], color=BLUE, marker="o", ls="", label="bge"), Line2D([], [], color=ORANGE, marker="o", ls="", label="gte"),
                       Line2D([], [], color=INK2, marker="o", ls="", label="no dedupe"), Line2D([], [], color=INK2, marker="s", ls="", label="restate"),
                       Line2D([], [], color=INK2, marker="^", ls="", label="copies")], frameon=False, fontsize=6, loc="lower right", ncol=2)

    ax = axs[2]
    sc = json.loads((R2 / "scaffold.json").read_text())["classes"]
    cls = ["scaffold_tool", "scaffold_prompt", "scaffold_family", "goal", "roster"]
    lab = ["tool", "prompt", "family", "goal", "roster"]
    x = np.arange(len(cls)); wdt = 0.26
    for i, (ch, c, nm) in enumerate((("R5", BLUE, "R5 action mix"), ("S", AQUA, "schema diff S"), ("M_h74", GRAY, "H74 mix M"))):
        a = [sc[k][ch]["auc"] for k in cls]
        lo = [sc[k][ch]["auc"] - sc[k][ch]["auc_ci"][0] for k in cls]; hi = [sc[k][ch]["auc_ci"][1] - sc[k][ch]["auc"] for k in cls]
        ax.bar(x + (i - 1) * wdt, a, wdt * 0.92, color=c, label=nm, yerr=[lo, hi], error_kw={"lw": 0.6, "ecolor": INK2})
    ax.axhline(0.5, color=INK2, lw=0.8, ls=":")
    ax.set_xticks(x); ax.set_xticklabels(lab, fontsize=7); ax.set_ylim(0.2, 1.0); ax.set_ylabel("AUC vs placebo windows")
    ax.set_title("(c) R5: scaffold changes stay hard", fontsize=8, loc="left")
    ax.legend(frameon=False, fontsize=6, loc="upper left", ncol=1)
    if layout == "wide":
        out = L.FIG / "r2_summary.pdf"
        fig.savefig(out); fig.savefig(str(out).replace(".pdf", ".png"), dpi=160)
    else:
        fig.savefig(L.FIG / "r2_obs.pdf"); fig2.savefig(L.FIG / "r2_scaffold_col.pdf")
        fig.savefig(L.FIG / "r2_obs.png", dpi=160); fig2.savefig(L.FIG / "r2_scaffold_col.png", dpi=160)
    plt.close("all")
    print(layout, "done")


if __name__ == "__main__":
    main()
