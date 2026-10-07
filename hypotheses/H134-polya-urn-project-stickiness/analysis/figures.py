"""H134 round 1 summary figure: (a) urn slope beta_F per unit (model b) vs the urn's 1; (b) observed dwell slope gamma vs
the O3-pp band from the fitted per-call rule; (c) forced-reset leave step per unit, pooled, vs the urn's prediction.
Output: figures/round1_summary.pdf (+ .png)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h134lib as L  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

FIG = L.ROOT / "hypotheses/H134-polya-urn-project-stickiness/figures"
RED, GRAY, GREEN, INK = "#b2443a", "#8a8a8a", "#3f7f4f", "#222222"


def main():
    S = json.loads((L.OUT / "results" / "summary.json").read_text())
    ph = json.loads((L.OUT / "results" / "posthoc.json").read_text())
    us = S["units"]
    pu = S["per_unit"]
    x = np.arange(len(us))
    fig, ax = plt.subplots(3, 1, figsize=(7.2, 7.6), sharex=True)
    b = np.array([pu[u]["bF_b"] for u in us]); lo = np.array([pu[u]["bF_b_ci"][0] for u in us]); hi = np.array([pu[u]["bF_b_ci"][1] for u in us])
    col = [GREEN if l > 0 else (RED if h < 0 else GRAY) for l, h in zip(lo, hi)]
    ax[0].vlines(x, lo, hi, color=col, lw=1.6); ax[0].scatter(x, b, color=col, s=14, zorder=3)
    ax[0].axhline(1, color=INK, ls="--", lw=0.8); ax[0].axhline(0, color=GRAY, lw=0.6)
    ax[0].text(len(us) - 0.5, 1.05, "urn: β_F = 1", ha="right", va="bottom", fontsize=8)
    ax[0].set_ylabel("β_F (model b)")
    ax[0].set_title("(a) Leave odds vs ln(1 − f_proj): 3/25 units > 0, RE mean 0.07 [−0.05, 0.19]", fontsize=9, loc="left")
    go = np.array([pu[u]["O3pp"]["gamma"]["obs"] for u in us])
    bl = np.array([pu[u]["O3pp"]["gamma"]["band"][0] for u in us]); bh = np.array([pu[u]["O3pp"]["gamma"]["band"][1] for u in us])
    ax[1].fill_between(x, bl, bh, color=GRAY, alpha=0.35, step="mid", label="95% band, fitted rule without ln d")
    ax[1].scatter(x, go, color=RED, s=16, zorder=3, label="observed γ")
    ax[1].set_ylabel("dwell slope γ"); ax[1].legend(fontsize=7, loc="lower left", frameon=False)
    ax[1].set_title("(b) Dwell aging: observed γ outside the band in 25/25 units", fontsize=9, loc="left")
    lor = np.array([pu[u]["O4"]["lor"] if pu[u]["O4"]["lor"] is not None else np.nan for u in us], float)
    se = np.array([pu[u]["O4"]["se"] if pu[u]["O4"]["se"] is not None else np.nan for u in us], float)
    pr = np.array([pu[u]["O4"]["pred"] if pu[u]["O4"]["pred"] is not None else np.nan for u in us], float)
    ax[2].vlines(x, lor - 1.96 * se, lor + 1.96 * se, color=GRAY, lw=1.4); ax[2].scatter(x, lor, color=INK, s=14, zorder=3, label="observed Δ_reset")
    ax[2].scatter(x, pr, color=RED, marker="_", s=80, zorder=4, label="urn prediction −β_F ln(1 − f_pre)")
    ax[2].axhline(0, color=GRAY, lw=0.6)
    n1 = S["N1_G51"]
    ax[2].set_ylabel("leave log OR at reset"); ax[2].legend(fontsize=7, loc="upper left", frameon=False)
    ax[2].set_title(f"(c) Forced reset: G51 pooled +{n1['lor']:.2f} [{n1['ci'][0]:+.2f}, {n1['ci'][1]:+.2f}] vs urn +{n1['pred']:.3f}; "
                    f"sustained leaves +{ph['G51_sustained_lor'][0]:.2f}", fontsize=9, loc="left")
    ax[2].set_ylim(-1.5, 3.5)
    ax[2].set_xticks(x); ax[2].set_xticklabels(us, rotation=90, fontsize=7)
    fig.tight_layout()
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / "round1_summary.pdf"); fig.savefig(FIG / "round1_summary.png", dpi=150)
    print("ok")


if __name__ == "__main__":
    main()
