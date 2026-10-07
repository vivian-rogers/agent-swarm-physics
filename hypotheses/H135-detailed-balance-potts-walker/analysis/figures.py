"""H135 summary figure: observed psi, m_pi and m_2^co per variant-testable unit against the synthetic world bands.

  uv run python hypotheses/H135-detailed-balance-potts-walker/analysis/figures.py
Writes figures/summary_obs.pdf.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
CARD = HERE.parent
ROOT = HERE.parents[2]
D = ROOT / "data/processed/H135-detailed-balance-potts-walker"
INK, MUTED, GRID = "#1f1f1e", "#6b6a64", "#d9d8d2"
W0C, W0MC, W1C = "#b5b4ad", "#2a78d6", "#eb6834"


def main():
    r = json.load(open(D / "results/results.json"))
    us = [u for k, u in r["units"].items() if u["rule"] == "coalive80"]
    us.sort(key=lambda u: u["unit"])
    names = [u["unit"] for u in us]
    fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.5))
    panels = [("psi", "destination slope $\\psi$", [("W0", W0C, "W0 heat-bath"), ("W0M", W0MC, "W0M Metropolis"), ("W1", W1C, "W1 age+habit")]),
              ("m_pi", "net max-ent flux $m_\\pi$", [("W0", W0C, "W0 heat-bath")]),
              ("m2co", "co-alive age flux $m_2^{co}$", [("W0", W0C, "W0 heat-bath"), ("W1", W1C, "W1 age+habit")])]
    for ax, (s, lab, bands) in zip(axs, panels):
        for i, u in enumerate(us):
            for j, (w, c, _) in enumerate(bands):
                b = u[f"band_{w}"][s]
                off = (j - (len(bands) - 1) / 2) * 0.22
                ax.fill_between([i + off - 0.1, i + off + 0.1], b[0], b[1], color=c, alpha=0.55, lw=0)
            if s == "psi":
                est, lo, hi = u["o4"]["psi"], *u["o4"]["psi_ci"]
            else:
                est, (lo, hi) = u[s], u[f"{s}_ci"]
            ax.plot([i, i], [lo, hi], color=INK, lw=1.2)
            ax.plot(i, est, "o", color=INK, ms=4)
        ax.axhline(1.0 if s == "psi" else 0.0, color=MUTED, lw=0.8, ls="--")
        ax.set_xticks(range(len(us)), names, fontsize=7)
        ax.set_title(lab, fontsize=8, color=INK)
        ax.tick_params(labelsize=7, colors=MUTED)
        ax.grid(axis="y", color=GRID, lw=0.5)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        if s != "m_pi":
            for w, c, name in bands:
                ax.plot([], [], "s", color=c, alpha=0.55, label=name)
            ax.legend(fontsize=6, frameon=False, loc="best")
    fig.text(0.5, 0.005, "#51 attention units testable under the 80% co-alive variant; dots = observed (95% CI); boxes = 2.5-97.5% of 200 synthetic runs",
             ha="center", fontsize=6.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    (CARD / "figures").mkdir(exist_ok=True)
    fig.savefig(CARD / "figures/summary_obs.pdf")
    fig.savefig(D / "results/summary_obs.png", dpi=130)


def synth():
    sm = json.load(open(D / "synthetic/summary.json"))
    keys = ["51a_attention", "51c_attention", "51f_attention", "51g_attention", "51h_attention"]
    worlds = ["W0", "W0M", "W1", "W2", "W3"]
    stats = [("o1_pass", "O1 passes", "#2a78d6"), ("m_pi_beyond", "$m_\\pi$ beyond W0 band", "#eb6834"),
             ("m2co_beyond", "$m_2^{co}$ beyond W0 band", "#1baf7a")]
    fig, ax = plt.subplots(figsize=(3.5, 2.4))
    for j, (k, lab, c) in enumerate(stats):
        for i, w in enumerate(worlds):
            v = [sm[u]["v80"][w][k] for u in keys]
            x = i + (j - 1) * 0.22
            ax.plot([x, x], [min(v), max(v)], color=c, lw=1.5)
            ax.plot(x, sum(v) / len(v), "o", color=c, ms=4, label=lab if i == 0 else None)
    ax.axhline(0.8, color=MUTED, lw=0.7, ls="--")
    ax.axhline(0.1, color=MUTED, lw=0.7, ls=":")
    ax.set_xticks(range(len(worlds)), ["W0\nheat-bath", "W0M\nMetropolis", "W1\nage+habit", "W2\nsink", "W3\ncycle"], fontsize=6.5)
    ax.set_ylabel("share of runs", fontsize=7, color=MUTED)
    ax.tick_params(labelsize=7, colors=MUTED)
    ax.set_ylim(-0.02, 1.02)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.legend(fontsize=6, frameon=False, loc="upper left", bbox_to_anchor=(0.22, 1.0))
    fig.tight_layout()
    fig.savefig(CARD / "figures/summary_synth.pdf")
    fig.savefig(D / "results/summary_synth.png", dpi=130)


if __name__ == "__main__":
    main()
    synth()
