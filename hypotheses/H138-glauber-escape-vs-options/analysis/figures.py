"""H138 round-1 figures from results/results.json and synthetic/summary.json.

figures/h138_round1.png        per-unit option elasticity (work, attention) with DL pools; O4 cross-unit points
figures/h138_synthetic.png     synthetic recovery: pooled eps_q by world and channel
goalperiod-subhypotheses/G38/figures/n1_terciles.png, G44/figures/n2_rooms.png
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h138lib as L  # noqa: E402

CARD = HERE.parent
GRAY, RED, GREEN, BLUE = "#777777", "#b2182b", "#1a7837", "#2166ac"


def main():
    R = json.loads((L.D / "results" / "results.json").read_text())
    S = json.loads((L.D / "synthetic" / "summary.json").read_text())
    fig, ax = plt.subplots(1, 3, figsize=(13, 5.2), gridspec_kw={"width_ratios": [1, 1.4, 1]})
    for k, ch in enumerate(("work", "attention")):
        U = [u for u in R[ch]["units"].values() if u["testable"] and u.get("eps_q") is not None]
        y = np.arange(len(U))
        for i, u in enumerate(U):
            c = GREEN if u["eps_lo"] > 0 else (RED if u["eps_hi"] < 0 else GRAY)
            ax[k].plot([u["eps_lo"], u["eps_hi"]], [i, i], color=c, lw=1.5)
            ax[k].plot(u["eps_q"], i, "o", color=c, ms=4)
        p = R[ch]["score"]["pool_eps_q"]
        ax[k].plot([p["lo"], p["hi"]], [-1.5, -1.5], color="k", lw=3)
        ax[k].plot(p["est"], -1.5, "D", color="k")
        ax[k].set_yticks(list(y) + [-1.5], [u["unit"] for u in U] + ["pool"], fontsize=7)
        ax[k].axvline(0, color=GRAY, lw=0.8)
        ax[k].axvline(1, color=BLUE, lw=0.8, ls="--")
        ax[k].set_xlabel("option elasticity ε_q")
        ax[k].set_title(f"{ch}: ε_q per unit (95% CI)", fontsize=10)
        ax[k].set_xlim(-4, 4)
    o4 = R["work"]["O4"]
    U = [u for u in R["work"]["units"].values() if u["unit"] in o4.get("units", [])]
    x = np.log([u["O6_qbar"] for u in U])
    yv = [u["O6_ln_r"] for u in U]
    cols = [RED if u["own_role"] else BLUE for u in U]
    ax[2].scatter(x, yv, c=cols, s=18)
    for u, xi, yi in zip(U, x, yv):
        ax[2].annotate(u["unit"], (xi, yi), fontsize=6)
    ax[2].set_xlabel("ln mean q_live (open options)")
    ax[2].set_ylabel("ln leaves per 100 own calls (reference)")
    ax[2].set_title(f"O4 across units: b_q = {o4['b_q']:.2f} [{o4['lo']:.2f}, {o4['hi']:.2f}]", fontsize=10)
    fig.tight_layout()
    (CARD / "figures").mkdir(exist_ok=True)
    fig.savefig(CARD / "figures" / "h138_round1.png", dpi=130)
    plt.close(fig)

    fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
    for k, ch in enumerate(("work", "attention")):
        ws = [w for w in ("W0", "W1h", "W1", "W2", "W3", "W4") if w in S[ch]]
        for i, w in enumerate(ws):
            p = S[ch][w]["pooled_all"]
            ax[k].bar(i, p["mean"], color=GRAY if S[ch][w]["eps_true"] == 0 else BLUE)
            ax[k].plot([i - 0.4, i + 0.4], [S[ch][w]["eps_true"]] * 2, color="k", lw=1)
            ax[k].text(i, max(p["mean"], 0) + 0.05, f"rej {p['reject']:.2f}", ha="center", fontsize=7)
        ax[k].set_xticks(range(len(ws)), ws)
        ax[k].set_ylabel("pooled ε̂_q (mean over replicates)")
        ax[k].set_title(f"{ch}: synthetic worlds (line = truth)", fontsize=10)
    fig.tight_layout()
    fig.savefig(CARD / "figures" / "h138_synthetic.png", dpi=130)
    plt.close(fig)

    n1 = R["natives"]["N1_G38"]
    fig, ax = plt.subplots(figsize=(4, 3.2))
    ax.bar([0, 1], [n1["h_bot_per100"], n1["h_top_per100"]], color=[GRAY, BLUE])
    ax.set_xticks([0, 1], [f"bottom q (mean {n1['q_bot']:.1f})", f"top q (mean {n1['q_top']:.1f})"], fontsize=7)
    ax.set_ylabel("leaves per 100 own calls")
    ax.set_title(f"G38 N1: obs/pred = {n1['obs_over_pred']:.2f}" if n1.get("obs_over_pred") else "G38 N1", fontsize=9)
    fig.tight_layout()
    fig.savefig(CARD / "goalperiod-subhypotheses" / "G38" / "figures" / "n1_terciles.png", dpi=130)
    plt.close(fig)

    n2 = R["natives"]["N2_G44"]
    fig, ax = plt.subplots(figsize=(4, 3.2))
    ax.bar([0, 1], [n2["raw_rate_best_per100"], n2["raw_rate_rest_per100"]], color=[GRAY, BLUE])
    ax.set_xticks([0, 1], [f"#best (q_room {n2['qroom_best']:.1f})", f"#rest (q_room {n2['qroom_rest']:.1f})"], fontsize=7)
    ax.set_ylabel("raw leaves per 100 own calls")
    ax.set_title(f"G44 N2: HR {n2['hr_rest_over_best']:.2f}, pred {n2['pred_ratio']:.2f}", fontsize=9)
    fig.tight_layout()
    fig.savefig(CARD / "goalperiod-subhypotheses" / "G44" / "figures" / "n2_rooms.png", dpi=130)
    plt.close(fig)
    print("figures written")


if __name__ == "__main__":
    main()
