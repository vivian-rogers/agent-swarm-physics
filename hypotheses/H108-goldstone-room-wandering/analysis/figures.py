"""H108 figures: daily room-direction persistence P(1) per period with the G38 lag profile; synthetic recovery.
Usage: uv run python hypotheses/H108-goldstone-room-wandering/analysis/figures.py"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h108lib as L  # noqa: E402

FIG = HERE.parent / "figures"
BLUE, ORANGE, AQUA, INK, MUTED = "#2a78d6", "#eb6834", "#1baf7a", "#1f1f1e", "#8a8984"
plt.rcParams.update({"font.size": 7.5, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": INK,
                     "ytick.color": INK, "axes.spines.top": False, "axes.spines.right": False})
raw = json.loads((L.DATA / "results" / "raw_all.json").read_text())
num = lambda v: np.nan if v is None else (np.inf if v == "inf" else float(v))  # noqa: E731
ORDER = ["G36", "G37", "G39", "G41", "G42", "G38", "G44", "G35"]
COL = {p: BLUE for p in ORDER}; COL.update({"G38": ORANGE, "G44": ORANGE, "G35": AQUA})
fig, axes = plt.subplots(1, 2, figsize=(4.4, 2.3), gridspec_kw={"width_ratios": [1.7, 1]})
ax = axes[0]
for i, P in enumerate(ORDER):
    b = raw["bge_small/style_resid"]["periods"][P]; g = raw["gte_modernbert/style_resid"]["periods"][P]
    ci = b.get("P1_ci")
    if ci:
        ax.plot([i, i], ci, color=COL[P], lw=1.2, alpha=0.6)
    ax.plot(i - 0.12, num(b["P1"]), "o", ms=5, color=COL[P], mec="white", mew=1)
    ax.plot(i + 0.12, num(g["P1"]), "o", ms=5, mfc="white", mec=COL[P], mew=1.2)
gb = raw["bge_small/style_resid"]["groups"]
ax.axhline(gb["identical"]["P1"], xmin=0.02, xmax=0.62, color=BLUE, lw=0.8, ls=(0, (3, 2)))
ax.axhline(gb["fielded"]["P1"], xmin=0.64, xmax=0.86, color=ORANGE, lw=0.8, ls=(0, (3, 2)))
ax.set_xticks(range(len(ORDER))); ax.set_xticklabels([p.replace("G", "#") for p in ORDER])
ax.set_ylim(-0.1, 1.18); ax.set_title("day-to-day persistence $P(1)$", fontsize=8, color=INK)
ax.text(2, 0.06, "identical", color=BLUE, ha="center", fontsize=7); ax.text(5.5, 0.06, "room kickoffs", color=ORANGE, ha="center", fontsize=7)
ax.text(7, 0.18, "forks", color=AQUA, ha="center", fontsize=7)
ax.plot([], [], "o", color=INK, ms=4, label="bge (95% CI)"); ax.plot([], [], "o", mfc="white", mec=INK, ms=4, label="gte")
ax.legend(frameon=False, fontsize=6.5, loc="upper left", ncol=2)
ax = axes[1]
for key, mk, lab in (("bge_small/style_resid", "o", "bge"), ("gte_modernbert/style_resid", "s", "gte")):
    pl_ = raw[key]["periods"]["G38"]["P_lag"]
    ls = sorted(pl_, key=int)
    ax.plot([int(l) for l in ls], [num(pl_[l]) for l in ls], marker=mk, ms=4, lw=1.5, color=ORANGE,
            mfc=ORANGE if lab == "bge" else "white", label=lab)
ax.set_ylim(0, 1.05); ax.set_xlabel("lag ℓ (days)"); ax.set_title("#38 lag profile $P(\\ell)$", fontsize=8, color=INK)
ax.legend(frameon=False, fontsize=6.5, loc="lower left")
fig.tight_layout(); fig.savefig(FIG / "persistence_by_period.pdf"); fig.savefig(FIG / "persistence_by_period.png", dpi=200)

syn = json.loads((L.DATA / "synthetic" / "synthetic_summary.json").read_text())["single"]
planted = [("regen_c0.0_rho1.0", 0.0), ("gold_c0.3_rho1.0", 0.3), ("gold_c0.5_rho1.0", 0.5), ("gold_c0.6_rho1.0", 0.6),
           ("gold_c0.9_rho1.0", 0.9), ("pinned_cNone_rho1.0", 1.0)]
fig, ax = plt.subplots(figsize=(4.4, 1.9))
for key, col, lab in (("P1_med", BLUE, "relabel-excess P(1) (primary)"), ("Psh_med", ORANGE, "split-half $P_{sh}(1)$ (variant)")):
    y = [np.median([syn[k][P][key] for P in syn[k] if isinstance(syn[k][P], dict)]) for k, _ in planted]
    ax.plot([c for _, c in planted], y, "o-", color=col, lw=1.5, ms=4, label=lab)
ax.plot([0, 1], [0, 1], color=MUTED, lw=0.6, ls=(0, (3, 2)))
ax.set_xlabel("planted lag-1 cosine"); ax.set_ylabel("recovered (median of periods)"); ax.legend(frameon=False, fontsize=6.5)
fig.tight_layout(); fig.savefig(FIG / "synthetic_recovery.pdf"); fig.savefig(FIG / "synthetic_recovery.png", dpi=200)
print("ok")
