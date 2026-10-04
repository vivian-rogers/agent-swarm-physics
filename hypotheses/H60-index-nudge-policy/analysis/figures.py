"""H60 figures: figures/summary_obs.pdf (policy values and ratios) and figures/synthetic_validation.pdf."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h60lib as L  # noqa: E402

FIG = Path(__file__).resolve().parents[1] / "figures"
POLS = ["random", "logged", "once_early", "index_ak", "index", "index_once"]
LAB = {"random": "random", "logged": "logged", "once_early": "once-early\n(k=2)", "index_ak": "index\n(a,k)",
       "index": "index\n(a,k,r)", "index_once": "Gittins\n1/trap"}
COL = {"G51": "#2a78d6", "G38": "#d0632b"}


def summary_obs():
    fig, ax = plt.subplots(1, 3, figsize=(7.4, 3.0))
    for j, oc in enumerate(("calls30", "sus", "any")):
        for k, per in enumerate(("G51", "G38")):
            p = L.OUT / per / "results.json"
            if not p.exists():
                continue
            r = json.loads(p.read_text())[oc]
            x = np.arange(len(POLS)) + (k - 0.5) * 0.3
            v = np.array([r["values"][q] for q in POLS])
            lo = np.array([r["values_ci"][q][0] for q in POLS])
            hi = np.array([r["values_ci"][q][1] for q in POLS])
            ax[j].errorbar(x, v, yerr=[np.clip(v - lo, 0, None), np.clip(hi - v, 0, None)], fmt="o", ms=3, lw=0.8,
                           color=COL[per], label=per if j == 0 else None)
        ax[j].axhline(0, color="k", lw=0.5)
        ax[j].set_xticks(range(len(POLS)), [LAB[q] for q in POLS], fontsize=5, rotation=60)
        ax[j].tick_params(labelsize=6)
        ax[j].set_title({"calls30": "(a) active calls in 30 min", "sus": "(b) sustained escape (prob.)",
                         "any": "(c) glance (prob.)"}[oc], fontsize=7.5)
    ax[0].set_ylabel("value per nudge (cross-fitted)", fontsize=7)
    ax[0].legend(fontsize=6, frameon=False)
    fig.tight_layout()
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / "summary_obs.pdf")


def synthetic():
    s = json.loads((L.OUT / "synthetic/synthetic_results.json").read_text())
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.5))
    for i, sc in enumerate(("S1", "S2", "S3")):
        rows = s[sc]["rows"]
        est = [r["est_ratio"] for r in rows]
        tru = [r["true_ratio"] for r in rows]
        ax[0].scatter(np.full(len(est), i) - 0.1, est, s=8, color="#2a78d6", label="estimated" if i == 0 else None)
        ax[0].scatter(np.full(len(tru), i) + 0.1, tru, s=8, color="#7f7f7f", label="true" if i == 0 else None)
        ax[1].bar(i, s[sc]["rate_ci_above_1"], color="#2a78d6")
    ax[0].axhline(1, color="k", lw=0.5)
    ax[0].axhline(2.3, color="#d0632b", lw=0.6, ls="--")
    ax[0].set_xticks(range(3), ["S1 hetero.", "S2 flat", "S3 selection"], fontsize=7)
    ax[0].set_ylabel("index / logged", fontsize=7)
    ax[0].legend(fontsize=6, frameon=False)
    ax[0].set_title("(a) policy ratio, G51 design", fontsize=7.5)
    ax[1].set_xticks(range(3), ["S1", "S2", "S3"], fontsize=7)
    ax[1].set_ylabel("share with CI lower > 1", fontsize=7)
    ax[1].set_title("(b) rejection rate of index = logged", fontsize=7.5)
    for a in ax:
        a.tick_params(labelsize=6.5)
    fig.tight_layout()
    fig.savefig(FIG / "synthetic_validation.pdf")


if __name__ == "__main__":
    summary_obs()
    synthetic()
