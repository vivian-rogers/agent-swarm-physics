"""H142 summary figures: figures/summary_synth.pdf (synthetic decision rates) and figures/summary_obs.pdf (step curves
and out-of-fold ΔLL per period). Per-period step-curve figures go to goalperiod-subhypotheses/G<NN>/figures/.
Usage: uv run python hypotheses/H142-langevin-torque-saturation/analysis/figures.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
CARD = HERE.parent
ROOT = HERE.parents[2]
DATA = ROOT / "data/processed/H142-langevin-torque-saturation"
RED, GRAY, GREEN = "#d03b3b", "#8a8a8a", "#0ca30c"
XS = {"n1": 1, "n2": 2, "n3": 3, "n4_5": 4.5, "n6p": 7}
plt.rcParams.update({"font.size": 7, "axes.spines.top": False, "axes.spines.right": False})


def lang(x):
    x = np.asarray(x, float)
    return np.where(np.abs(x) < 1e-3, x / 3, 1 / np.tanh(np.maximum(x, 1e-9)) - 1 / np.maximum(x, 1e-9))


def synth_fig():
    s = json.loads((DATA / "synthetic/summary_main.json").read_text())
    worlds = ["W0", "W-lin", "W-sel", "W-recent", "W-pow", "W-field1", "W-field", "W-L1", "W-L3"]
    labs = ["none", "linear", "select", "newest", "power", "field 1x", "field 4x", "L, n_sat 1", "L, n_sat 3"]
    fig, axes = plt.subplots(1, 2, figsize=(4.2, 1.9))
    for ax, key, title in ((axes[0], "prefer_L_over_lin", "Langevin beats line\n(ΔLL CI > 0)"),
                           (axes[1], "pooled_prefer_L_over_lin", "same, card's pooled\namplitude (pre-A1)")):
        for j, g in enumerate((13, 38, 51)):
            v = [s.get(f"G{g}|bge_small|{w}", {}).get(key) or 0 for w in worlds]
            cols = [GREEN if w.startswith("W-L") else RED for w in worlds]
            ax.scatter(np.arange(len(worlds)) + (j - 1) * 0.22, v, s=9, c=cols, marker="osD"[j], edgecolors="none",
                       label=f"#{g}")
        ax.axhline(0.8, color=GREEN, lw=0.6, ls=":"); ax.axhline(0.1, color=RED, lw=0.6, ls=":")
        ax.set_xticks(range(len(worlds))); ax.set_xticklabels(labs, rotation=60, ha="right", fontsize=5.5)
        ax.set_ylim(-0.05, 1.05); ax.set_title(title, fontsize=6.5)
    axes[0].set_ylabel("share of 100 runs"); axes[0].legend(fontsize=5, frameon=False, loc="center left")
    fig.tight_layout()
    fig.savefig(CARD / "figures/summary_synth.pdf"); plt.close(fig)


def curve_panel(ax, r, color, label, offset=0.0):
    f = r["dummies"]["f"]
    xs = [XS[k] + offset for k in f]; ys = [f[k]["est"] for k in f]
    lo = [f[k]["lo"] for k in f]; hi = [f[k]["hi"] for k in f]
    ax.errorbar(xs, ys, yerr=[np.subtract(ys, lo), np.subtract(hi, ys)], fmt="o", ms=2.5, lw=0.7, color=color, label=label)


def obs_fig():
    per = json.loads((DATA / "results/periods.json").read_text())
    fig, axes = plt.subplots(1, 2, figsize=(4.4, 1.9))
    ax = axes[0]
    show = [k for k in per if per[k].get("bge_small", {}).get("scored")]
    if not show:
        show = [k for k in per if per[k].get("bge_small", {}).get("identified_H113")][:3]
    cmap = plt.get_cmap("viridis")
    for i, k in enumerate(show):
        curve_panel(ax, per[k]["bge_small"], cmap(i / max(len(show) - 1, 1) * 0.85), f"#{k[1:]}", offset=(i - len(show) / 2) * 0.12)
    ax.axhline(0, color=GRAY, lw=0.5)
    ax.set_xticks(list(XS.values())); ax.set_xticklabels(["1", "2", "3", "4–5", "6+"])
    ax.set_xlabel("aligned reads n in the batch"); ax.set_ylabel("step toward u (f̂)")
    ax.legend(fontsize=5, frameon=False)
    ax = axes[1]
    ks = sorted(per, key=lambda k: int(k[1:]))
    for j, m in enumerate(("bge_small", "gte_modernbert")):
        for i, k in enumerate(ks):
            r = per[k].get(m)
            if not r:
                continue
            d = r["dll_langevin_linear"]
            n = max(d["n_rows"], 1)
            y, lo, hi = d["dll"] / n * 1e3, d["lo"] / n * 1e3, d["hi"] / n * 1e3
            col = GREEN if lo > 0 else (RED if hi < 0 else GRAY)
            alpha = 1.0 if r.get("scored") else 0.35
            ax.errorbar(i + (j - 0.5) * 0.3, y, yerr=[[y - lo], [hi - y]], fmt="os"[j], ms=2.2, lw=0.6, color=col, alpha=alpha)
    ax.axhline(0, color=GRAY, lw=0.5)
    ax.set_xticks(range(len(ks))); ax.set_xticklabels([k[1:] for k in ks], rotation=90, fontsize=4.5)
    ax.set_ylabel("ΔLL(Langevin − line)\nper 1000 rows"); ax.set_xlabel("goal period (dark = scored)")
    fig.tight_layout()
    fig.savefig(CARD / "figures/summary_obs.pdf"); plt.close(fig)


def period_figs():
    per = json.loads((DATA / "results/periods.json").read_text())
    for k, p in per.items():
        d = CARD / "goalperiod-subhypotheses" / f"G{int(k[1:]):02d}"
        if not d.exists():
            continue
        fig, ax = plt.subplots(figsize=(2.6, 1.8))
        for j, (m, col) in enumerate((("bge_small", "#1f4e79"), ("gte_modernbert", "#c07a00"))):
            if m in p:
                curve_panel(ax, p[m], col, m.split("_")[0], offset=(j - 0.5) * 0.15)
        ax.axhline(0, color=GRAY, lw=0.5)
        ax.set_xticks(list(XS.values())); ax.set_xticklabels(["1", "2", "3", "4–5", "6+"])
        ax.set_xlabel("aligned reads n"); ax.set_ylabel("step f̂(n)"); ax.legend(fontsize=5, frameon=False)
        fig.tight_layout(); (d / "figures").mkdir(exist_ok=True)
        fig.savefig(d / "figures/step_curve.pdf"); plt.close(fig)


if __name__ == "__main__":
    synth_fig()
    if (DATA / "results/periods.json").exists():
        obs_fig(); period_figs()
