"""H78 figures: summary_obs.pdf (p per period vs the prediction bands) and summary_synth.pdf (synthetic recovery).
Also writes per-period figures into goalperiod-subhypotheses/G<NN>/figures/.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
HYP = ROOT / "hypotheses/H78-replicator-growth-order"
DATA = ROOT / "data/processed/H78-replicator-growth-order"
HERD = [31, 33, 41]
OWN = [39, 42, 51]
plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False, "pdf.fonttype": 42})
C_HERD, C_OWN, C_NAT = "#2166ac", "#b2182b", "#5a5a5a"


def res(name):
    p = DATA / "results" / f"{name}.json"
    return json.loads(p.read_text()) if p.exists() else None


def fig_obs(tag=""):
    a2p = DATA / "synthetic/summary_A2.json"
    a2 = json.loads(a2p.read_text()) if a2p.exists() else {}
    fig, ax = plt.subplots(figsize=(3.4, 2.3))
    ax.axhspan(1.2, 1.5, color=C_HERD, alpha=0.12, lw=0)
    ax.axhspan(-0.5, 0.7, color=C_OWN, alpha=0.08, lw=0)
    ax.axhline(1, color="k", lw=0.6, ls=":")
    labels = []
    x = 0
    for grp, col in ((HERD, C_HERD), (OWN, C_OWN)):
        for g in grp:
            r = res(f"G{g:02d}")
            labels.append(f"#{g}")
            for w in ("fitness05", "fitness10"):
                v = a2.get(f"G{g:02d}/{w}")
                if v and v["p_pooled"]["median"] is not None:
                    ax.plot([x - 0.3, x + 0.3], [v["p_pooled"]["median"]] * 2, color="#e08214", lw=1.0, alpha=0.8)
            if r and r["primary"]["pooled"] and r["primary"]["testable"]:
                p = r["primary"]["pooled"]
                ax.errorbar(x, p["est"], yerr=[[p["est"] - p["lo"]], [p["hi"] - p["est"]]], fmt="o", color=col, ms=4, capsize=2)
                c = r.get("p_corrected")
                if c is not None:
                    ax.plot(x + 0.22, c, marker="D", ms=3, color=col, mfc="white")
            else:
                ax.text(x, 0.0, "n/a", ha="center", fontsize=6, color=col)
            x += 1
    for g, lab in ((40, "#40 named"), (40, "#40")):
        pass
    r = res("G40")
    if r and r.get("named_stratum"):
        p = r["named_stratum"]
        ax.errorbar(x, p["est"], yerr=[[p["est"] - p["lo"]], [p["hi"] - p["est"]]], fmt="s", color=C_NAT, ms=4, capsize=2)
    labels.append("#40\nnamed")
    ax.set_xticks(range(len(labels)), labels)
    ax.set_ylabel("growth order $\\hat p$")
    ax.set_ylim(-0.6, 3.2)
    ax.text(0.01, 0.97, "herding band", transform=ax.transAxes, color=C_HERD, fontsize=6, va="top")
    ax.text(0.99, 0.03, "parabolic band; orange: $p$=1 with fitness spread", transform=ax.transAxes, color=C_OWN, fontsize=5.5, ha="right")
    fig.tight_layout()
    fig.savefig(HYP / "figures/summary_obs.pdf")
    plt.close(fig)


def fig_synth():
    s = json.loads((DATA / "synthetic/summary.json").read_text())
    worlds = [("field", 0.0), ("parabolic", 0.5), ("neutral", 1.0), ("conformist", 1.4)]
    fig, ax = plt.subplots(figsize=(3.4, 2.1))
    periods = sorted({k.split("/")[0] for k in s})
    for i, (w, pt) in enumerate(worlds):
        for j, g in enumerate(periods):
            v = s.get(f"{g}/{w}")
            if not v or v["p_pooled"]["median"] is None:
                continue
            ax.plot(pt + (j - len(periods) / 2) * 0.03, v["p_pooled"]["median"], "o", ms=3, color=plt.cm.viridis(j / max(len(periods) - 1, 1)),
                    label=g if i == 0 else None)
    a2p = DATA / "synthetic/summary_A2.json"
    if a2p.exists():
        a2 = json.loads(a2p.read_text())
        for k, (w, dx) in enumerate((("fitness05", 0.08), ("fitness10", 0.16), ("fitness15", 0.24))):
            vals = [v["p_pooled"]["median"] for kk, v in a2.items() if kk.endswith("/" + w) and v["p_pooled"]["median"] is not None]
            ax.plot([1 + dx] * len(vals), vals, "x", ms=3.5, color="#e08214", label=("fitness spread $\\sigma_A$=0.5/1/1.5, $p$=1" if k == 0 else None))
    ax.plot([-0.1, 1.6], [-0.1, 1.6], "k:", lw=0.7)
    ax.set_xlabel("planted $p$")
    ax.set_ylabel("median $\\hat p$ (primary)")
    ax.legend(fontsize=5, ncol=2, frameon=False, loc="upper left")
    fig.tight_layout()
    fig.savefig(HYP / "figures/summary_synth.pdf")
    plt.close(fig)


if __name__ == "__main__":
    fig_obs()
    fig_synth()
