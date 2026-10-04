"""H131 summary figure: #12 rival/teammate flag rates by phase and read status (left); synthetic pass rates (right).
Usage: uv run python hypotheses/H131-antagonism-off-one-readout/analysis/figures.py
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
D = ROOT / "data/processed/H131-antagonism-off-one-readout"
F = Path(__file__).resolve().parents[1] / "figures"


def wilson(k, n, z=1.96):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (c - h, c + h)


def main():
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import h131lib as L
    rep = pl.read_parquet(D / "replies.parquet")
    g = L.G12(rep, pl.read_parquet(D / "reads.parquet"), "y", "12")
    cells = [("riv.\npre", (g.R == 1) & (g.phase == "pre")), ("riv.\ndeb", (g.R == 1) & (g.phase == "deb")),
             ("riv. 1st\npost-read", g.first), ("riv. later\npost", (g.R == 1) & (g.phase == "post") & ~g.first),
             ("mate\nopen", (g.R == 0) & (g.phase != "post")), ("mate\npost", (g.R == 0) & (g.phase == "post"))]
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.6), gridspec_kw=dict(width_ratios=[1.3, 1]))
    for n, (lab, m) in enumerate(cells):
        k, N = int(g.y[m].sum()), int(m.sum())
        lo, hi = wilson(k, N)
        col = "#c43a3a" if lab.startswith("riv") else "#5598e7"
        ax[0].bar(n, k / N, color=col, alpha=0.85)
        ax[0].errorbar(n, k / N, yerr=[[k / N - lo], [hi - k / N]], color="k", lw=0.8, capsize=2)
        ax[0].text(n, hi + 0.02, f"{k}/{N}", ha="center", fontsize=7)
    ax[0].set_xticks(range(len(cells)))
    ax[0].set_xticklabels([c[0] for c in cells], fontsize=6.5)
    ax[0].set_ylabel("validated disagreement flag rate")
    ax[0].set_title("#12 debates: flags by relation, phase, read", fontsize=8)
    ax[0].set_ylim(0, 0.75)
    s = json.loads((D / "synthetic/summary.json").read_text())
    rows = {r["world"]: r for r in s["g12"]}
    ws = ["W0", "W1", "W3_120", "W4_3", "W5_300", "W6"]
    lab = ["none", "H131", "clock\n+2 m", "reman.\nκ=3", "decay\n5 m", "relat."]
    x = np.arange(len(ws))
    ax[1].bar(x - 0.2, [rows[w]["P1"] for w in ws], 0.4, label="P1 DiD", color="#888")
    ax[1].bar(x + 0.2, [rows[w]["N2"] for w in ws], 0.4, label="N2 first reply", color="#c43a3a")
    ax[1].set_xticks(x)
    ax[1].set_xticklabels(lab, fontsize=6)
    ax[1].set_ylabel("pass rate (synthetic)")
    ax[1].set_title("Synthetic worlds on the real skeleton", fontsize=8)
    ax[1].legend(fontsize=6, frameon=False)
    ax[1].set_ylim(0, 1)
    for a in ax:
        a.tick_params(labelsize=7)
        a.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    F.mkdir(exist_ok=True)
    fig.savefig(F / "h131_obs.pdf")
    fig.savefig(F / "h131_obs.png", dpi=150)


if __name__ == "__main__":
    main()
