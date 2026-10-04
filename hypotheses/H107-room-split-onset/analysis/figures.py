"""H107 figures: onset ratio and projection per period (both models); synthetic operating characteristics.
Usage: uv run python hypotheses/H107-room-split-onset/analysis/figures.py"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h107lib as L  # noqa: E402

FIG = HERE.parent / "figures"
BLUE, ORANGE, AQUA, INK, MUTED = "#2a78d6", "#eb6834", "#1baf7a", "#1f1f1e", "#8a8984"
plt.rcParams.update({"font.size": 7.5, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": INK,
                     "ytick.color": INK, "axes.spines.top": False, "axes.spines.right": False})
raw = json.loads((L.DATA / "results" / "raw_all.json").read_text())
ORDER = ["G37", "G39", "G41", "G42", "G38", "G44", "G35"]
COL = {"G37": BLUE, "G39": BLUE, "G41": BLUE, "G42": BLUE, "G38": ORANGE, "G44": ORANGE, "G35": AQUA}

fig, axes = plt.subplots(1, 2, figsize=(4.4, 2.3), sharey=False)
for ax, stat, ttl, thr in ((axes[0], "r1", "onset ratio $r_1=E(1)/E_F$", (0.3, 0.8)),
                           (axes[1], "pi1", r"onset projection $\pi_1$", (0.6,))):
    for i, P in enumerate(ORDER):
        b = raw["bge_small/style_resid"]["periods"][P]; g = raw["gte_modernbert/style_resid"]["periods"][P]
        ci = (b.get("ci") or {}).get(stat)
        if ci:
            ax.plot([i, i], ci, color=COL[P], lw=1.2, alpha=0.6, solid_capstyle="round")
        ax.plot(i - 0.12, b[stat], "o", ms=5, color=COL[P], mec="white", mew=1)
        ax.plot(i + 0.12, g[stat], "o", ms=5, mfc="white", mec=COL[P], mew=1.2)
    for t in thr:
        ax.axhline(t, color=MUTED, lw=0.6, ls=(0, (3, 2)))
    ax.axhline(0, color=MUTED, lw=0.5)
    ax.set_xticks(range(len(ORDER))); ax.set_xticklabels([p.replace("G", "#") for p in ORDER], rotation=0)
    ax.set_title(ttl, fontsize=8, color=INK)
    ax.set_ylim(-0.7, 2.1)
axes[0].text(1.5, 2.0, "identical", color=BLUE, ha="center", fontsize=7)
axes[0].text(4.5, 2.0, "kickoffs", color=ORANGE, ha="center", fontsize=7)
axes[0].text(6, 1.75, "forks", color=AQUA, ha="center", fontsize=7)
axes[1].plot([], [], "o", color=INK, ms=4, label="bge (95% CI)"); axes[1].plot([], [], "o", mfc="white", mec=INK, ms=4, label="gte")
axes[1].legend(frameon=False, fontsize=6.5, loc="upper left")
fig.tight_layout()
fig.savefig(FIG / "onset_by_period.pdf"); fig.savefig(FIG / "onset_by_period.png", dpi=200)

syn = json.loads((L.DATA / "synthetic" / "synthetic_summary.json").read_text())["worlds"]
W = [("null_rho0.0", "null"), ("step_rho0.3", "step\nρ 0.3"), ("step_rho1.0", "step\nρ 1"),
     ("slow_rho1.0_tau1.0", "slow\n1 d"), ("slow_rho1.0_tau2.0", "slow\n2 d"), ("fast_rho1.0_tau0.25", "fast\n1 h")]
fig, ax = plt.subplots(figsize=(4.4, 1.9))
x = np.arange(len(W)); w = 0.26
for k, (key, lab, col) in enumerate((("kill", "kill (r₁≥0.8, c₁≥0.7)", ORANGE), ("ssb", "SSB (r₁≤0.3)", BLUE),
                                     ("pi1_ge06", "π₁≥0.6", AQUA))):
    vals = [syn[wk]["all"][key] if not (wk.startswith("null") and key == "pi1_ge06") else 0 for wk, _ in W]
    ax.bar(x + (k - 1) * w, vals, w - 0.03, color=col, label=lab)
ax.set_xticks(x); ax.set_xticklabels([l for _, l in W]); ax.set_ylabel("share of period runs"); ax.set_ylim(0, 1.05)
ax.legend(frameon=False, fontsize=6.5, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.22))
fig.tight_layout()
fig.savefig(FIG / "synthetic_rules.pdf"); fig.savefig(FIG / "synthetic_rules.png", dpi=200)
print("ok")
