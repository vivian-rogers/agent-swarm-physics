"""H93 summary figures.
  figures/summary_obs.pdf    share coupling betaJ-hat per period (validated M4; naive M0 for contrast) and the coupling
                             gamma_c at which the period's fitted fields would first support two stable equilibria
  figures/summary_synth.pdf  synthetic identification: rate of 'betaJ > 0' calls by M2 and M4 in worlds without coupling
                             (static fitness spread, fast and slow repo bursts) and power at betaJ = 3
"""
from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
DATA = ROOT / "data/processed/H93-brock-durlauf-project-choice"
FIG = HERE.parent / "figures"
PERIODS = [30, 31, 33, 35, 36, 37, 38, 39, 40, 41, 42, 44, 51]
W_C, A_C, N_C = "#3a6ea5", "#d1495b", "#999999"


def pool(r, ch, m):
    c = r.get(ch) or {}
    x = (c.get("fits") or {}).get(m) or {}
    p = x.get("pool")
    if not p or p.get("se") is None or p["se"] > 5:
        return None
    return p


def fig_obs():
    ph = json.loads((DATA / "results" / "phase.json").read_text()) if (DATA / "results" / "phase.json").exists() else {}
    fig, ax = plt.subplots(figsize=(4.2, 2.4))
    for i, g in enumerate(PERIODS):
        p = DATA / "results" / f"G{g:02d}.json"
        if not p.exists():
            continue
        r = json.loads(p.read_text())
        for ch, dx, col, mk in (("work", -0.15, W_C, "o"), ("attention", 0.15, A_C, "s")):
            m4 = pool(r, ch, "M4")
            if m4:
                lo, hi = max(m4["lo"], -13.5), min(m4["hi"], 12)
                ax.plot([i + dx, i + dx], [lo, hi], color=col, lw=0.9)
                ax.plot(i + dx, np.clip(m4["est"], -13.5, 12), mk, ms=3.2, color=col, mfc=col if ch == "work" else "white")
            m0 = pool(r, ch, "M0")
            if m0:
                ax.plot(i + dx, np.clip(m0["est"], -13.5, 12), "_", ms=5, color=N_C, mew=1.0)
            q = ph.get(f"G{g}_{ch}") or {}
            if q.get("gamma_c"):
                ax.plot(i + dx, min(q["gamma_c"], 12), "v", ms=3.0, color="k", mfc="none", mew=0.6)
    ax.axhline(0, color="k", lw=0.5)
    ax.set_xticks(range(len(PERIODS)))
    ax.set_xticklabels([f"#{g}" for g in PERIODS], fontsize=6, rotation=0)
    ax.set_ylabel(r"$\beta J$ (share coupling)", fontsize=7)
    ax.set_ylim(-14, 12.5)
    ax.tick_params(axis="y", labelsize=6)
    from matplotlib.lines import Line2D
    ax.legend(handles=[Line2D([], [], marker="o", color=W_C, ls="", ms=3, label="work (M4)"),
                       Line2D([], [], marker="s", color=A_C, mfc="white", ls="", ms=3, label="attention (M4)"),
                       Line2D([], [], marker="_", color=N_C, ls="", ms=5, label="naive M0"),
                       Line2D([], [], marker="v", color="k", mfc="none", ls="", ms=3, label=r"$\gamma_c$ (2 equilibria)")],
              fontsize=5.5, frameon=False, ncol=2, loc="upper left")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs.pdf")


def fig_synth():
    import synthetic as SY
    d = pl.concat([pl.read_parquet(p) for p in glob.glob(str(DATA / "synthetic" / "G*.parquet"))], how="diagonal_relaxed")
    s = SY.summarize(d)
    worlds = [("W1", "fitness\n" + r"$\sigma_A$=0.5"), ("W2", "fitness\n" + r"$\sigma_A$=1"), ("W8", "slow\nbursts"),
              ("W6", "fast bursts\n" + r"$\sigma$=1"), ("W7", "fast bursts\n" + r"$\sigma$=2"), ("W3", "power\n" + r"$\beta J$=3")]
    fig, ax = plt.subplots(figsize=(4.2, 2.0))
    for k, (m, col) in enumerate((("M2", N_C), ("M4", W_C))):
        vals, lo, hi = [], [], []
        for w, _ in worlds:
            x = s.filter((pl.col("world") == w) & (pl.col("model") == m))["pos_rate"].to_numpy()
            vals.append(np.median(x) if len(x) else np.nan)
            lo.append(np.min(x) if len(x) else np.nan)
            hi.append(np.max(x) if len(x) else np.nan)
        xs = np.arange(len(worlds)) + (k - 0.5) * 0.36
        ax.bar(xs, vals, width=0.34, color=col, label=m + (" (validated)" if m == "M4" else ""))
        ax.errorbar(xs, vals, yerr=[np.array(vals) - np.array(lo), np.array(hi) - np.array(vals)], fmt="none",
                    ecolor="k", elinewidth=0.5, capsize=1.2)
    ax.axhline(0.1, color="k", lw=0.5, ls=":")
    ax.axvline(4.5, color="k", lw=0.5)
    ax.text(2.0, 1.04, "no coupling: false positives", fontsize=5.5, ha="center")
    ax.text(5.0, 1.04, "coupling", fontsize=5.5, ha="center")
    ax.set_ylim(0, 1.12)
    ax.set_xticks(range(len(worlds)))
    ax.set_xticklabels([lab for _, lab in worlds], fontsize=5.5)
    ax.set_ylabel(r"share of runs with CI$>0$", fontsize=6.5)
    ax.tick_params(axis="y", labelsize=6)
    ax.legend(fontsize=5.5, frameon=False, loc="upper left")
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG / "summary_synth.pdf")


if __name__ == "__main__":
    FIG.mkdir(exist_ok=True)
    fig_obs()
    fig_synth()
    print("ok")
