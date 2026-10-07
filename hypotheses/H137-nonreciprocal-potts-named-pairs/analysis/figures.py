"""H137 figures: synthetic validation (summary_synth.pdf) and observed per-unit results (summary_obs.pdf).
Usage: uv run python hypotheses/H137-nonreciprocal-potts-named-pairs/analysis/figures.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h137lib as L  # noqa: E402

FIG = Path(__file__).resolve().parents[1] / "figures"
BLUE, ORANGE, GRAY, INK, MUTED = "#2a78d6", "#eb6834", "#8a8984", "#0b0b0b", "#52514e"
plt.rcParams.update({"font.size": 7, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False, "lines.linewidth": 1.2})
WORLD_LBL = {"W0": "W0 none", "W1h": "W1 J=0.5", "W1": "W1 J=1", "W1j2": "J=2", "W1j3": "J=3", "W1j5": "J=5",
             "W2": "W2 popul.", "W3": "W3 co-arr.", "W4": "W4 broadc."}


def synth():
    tabs = {}
    for tag in ("calls", "calls_all"):
        p = L.D / "results" / f"synthetic_table_{tag}.json"
        if p.exists():
            tabs[tag] = json.loads(p.read_text())
    t = tabs["calls"]
    order = [w for w in ("W0", "W2", "W3", "W4", "W1h", "W1", "W1j2", "W1j3", "W1j5") if w in t]
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.3))
    x = np.arange(len(order))
    for k, (key, col, lab) in enumerate((("P1_card", GRAY, "P1 card (pop+indeg)"), ("P1_A1", BLUE, "P1 A1 (+propensity)"),
                                         ("P4", ORANGE, "P4 read vs in-flight"))):
        v = [t[w][key][0] for w in order]
        ax[0].bar(x + (k - 1) * 0.27, v, 0.25, color=col, label=lab)
    ax[0].axhline(0.8, color=MUTED, lw=0.7, ls="--")
    ax[0].axhline(0.10, color=MUTED, lw=0.7, ls=":")
    ax[0].set_xticks(x, [WORLD_LBL[w] for w in order], rotation=40, ha="right")
    ax[0].set_ylabel("rejection rate (pooled, 11 units)")
    ax[0].set_ylim(0, 1)
    ax[0].legend(frameon=False, fontsize=6, loc="upper left")
    ax[0].set_title("(a) size and power", loc="left", fontsize=7)
    for k, (key, col, lab) in enumerate((("mean_theta", GRAY, r"$\theta$ card"), ("mean_theta_act", BLUE, r"$\theta$ A1"))):
        m = np.array([t[w][key][0] for w in order]); s = np.array([t[w][key][1] for w in order])
        ax[1].errorbar(x + (k - 0.5) * 0.25, m, yerr=s, fmt="o", ms=3.5, color=col, label=lab, capsize=0)
    ax[1].axhline(0, color=MUTED, lw=0.7)
    ax[1].set_xticks(x, [WORLD_LBL[w] for w in order], rotation=40, ha="right")
    ax[1].set_ylabel(r"$\theta_\mathrm{name}$ (mean $\pm$ sd over runs)")
    ax[1].legend(frameon=False, fontsize=6)
    ax[1].set_title(r"(b) bias of $\theta_\mathrm{name}$", loc="left", fontsize=7)
    fig.tight_layout()
    fig.savefig(FIG / "summary_synth.pdf")
    plt.close(fig)


def obs():
    U = pl.read_parquet(L.D / "results/units.parquet").filter(pl.col("testable"))
    R = json.loads((L.D / "results/round1.json").read_text())
    U = U.sort("goal_no", "unit")
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.5), gridspec_kw={"width_ratios": [3, 1.2]})
    y = np.arange(U.height)
    for key, col, off, lab in (("theta", GRAY, -0.18, r"card"), ("theta_act", BLUE, 0.18, r"A1")):
        m, lo, hi = U[key].to_numpy(), U[f"{key}_lo"].to_numpy(), U[f"{key}_hi"].to_numpy()
        ax[0].errorbar(y + off, m, yerr=[m - lo, hi - m], fmt="o", ms=2.5, color=col, lw=0.8, label=lab, capsize=0)
    p = R["pooled"]["theta_act"]
    ax[0].axhspan(p["lo"], p["hi"], color=BLUE, alpha=0.15, lw=0)
    ax[0].axhline(0, color=MUTED, lw=0.7)
    ax[0].set_xticks(y, U["unit"].to_list(), rotation=90, fontsize=5)
    ax[0].set_ylabel(r"$\theta_\mathrm{name}$ (95% pair-bootstrap CI)")
    ax[0].set_ylim(-3, 3)
    ax[0].legend(frameon=False, fontsize=6, loc="upper left", ncol=2)
    ax[0].set_title(r"(a) follow direction vs one-way naming, testable units (band: pooled A1)", loc="left", fontsize=7)
    o4 = R["pooled"]["o4"]
    vals = [o4["rate_read"] * 1e3, o4["rate_if"] * 1e3]
    ax[1].bar([0, 1], vals, 0.6, color=[BLUE, GRAY])
    ax[1].set_xticks([0, 1], ["read named", "in-flight named"])
    ax[1].set_ylabel("follow rate onto namer's project (per 1,000)")
    ax[1].set_title("(b) O4, pooled", loc="left", fontsize=7)
    for k, v in enumerate(vals):
        ax[1].text(k, v, f"{v:.2f}", ha="center", va="bottom", fontsize=6, color=INK)
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs.pdf")
    plt.close(fig)


if __name__ == "__main__":
    FIG.mkdir(parents=True, exist_ok=True)
    synth()
    if (L.D / "results/round1.json").exists():
        obs()
