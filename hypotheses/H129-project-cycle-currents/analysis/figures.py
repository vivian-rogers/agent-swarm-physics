"""H129 figures: summary_obs.pdf (A_3 and A_cyc per unit-channel against the reversal null and the age walker W1*)
and summary_synth.pdf (rejection rates by synthetic world). Okabe-Ito colors (writeup/visuals/STYLE.md).
Usage: uv run python hypotheses/H129-project-cycle-currents/analysis/figures.py
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
import h129lib as L  # noqa: E402

BLUE, ORANGE, GREEN, INK, MUTED, GRID, NULL = "#0072B2", "#E69F00", "#009E73", "#1a1a1a", "#8c8c8c", "#e6e6e6", "#b3b3b3"
FIG = HERE.parent / "figures"
plt.rcParams.update({"font.size": 8, "axes.edgecolor": MUTED, "axes.spines.top": False, "axes.spines.right": False})


def obs():
    u = json.loads((L.D / "results/units.json").read_text())
    rows = [(k, r) for k, r in u.items() if r.get("testable_tri") and "boot" in r]
    rows.sort(key=lambda kr: (kr[1]["channel"], kr[1]["goal_no"], kr[1]["unit"]))
    fig, ax = plt.subplots(1, 2, figsize=(7.0, max(2.6, 0.13 * len(rows) + 0.8)), sharey=True)
    for j, (key, title) in enumerate((("A3", "(a) age-signed triple affinity $A_3$"),
                                      ("Acyc", "(b) rotation-summed cycle affinity $\\mathcal{A}_{cyc}$"))):
        a = ax[j]
        for i, (k, r) in enumerate(rows):
            col = BLUE if r["channel"] == "work" else ORANGE
            lo, hi, _ = r["boot"][key]
            a.plot([lo, hi], [i, i], color=col, lw=1.0, alpha=0.8)
            mk = "o" if r.get("shared") else "s"
            sig = r["p_flip"][key] < 0.05
            a.scatter(r[key], i, color=col if sig else "white", edgecolor=col, s=14, marker=mk, zorder=3, lw=0.8)
            if "W1star" in r:
                a.scatter(r["W1star"][f"q95_{key}"], i, marker="|", color=INK, s=22, zorder=4)
        a.axvline(0, color=NULL, lw=0.8)
        a.set_title(title, fontsize=8, loc="left"); a.grid(axis="x", color=GRID, lw=0.5)
        a.set_xlabel("nats (agent-bootstrap 95% CI)")
    ax[0].set_yticks(range(len(rows)))
    ax[0].set_yticklabels([f"{r['unit']} {r['channel'][:4]}" for _, r in rows], fontsize=5.2)
    ax[1].scatter([], [], color=BLUE, s=12, label="work (filled: reversal p<0.05)")
    ax[1].scatter([], [], color=ORANGE, s=12, label="attention")
    ax[1].scatter([], [], marker="|", color=INK, s=22, label="age walker W1* 95th pct")
    ax[1].legend(frameon=False, fontsize=5.5, loc="lower right")
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs.pdf"); plt.close(fig)


def synth():
    s = json.loads((L.D / "synthetic/summary.json").read_text())
    worlds = ["W0", "W0h", "W1", "W2", "W3", "W3s"]
    lab = {"W0": "W0 fixed\nMarkov", "W0h": "W0h fixed\n+habit", "W1": "W1 age", "W2": "W2 age\n+recency",
           "W3": "W3 cycle\nκ=1", "W3s": "W3s cycle\nκ=2"}
    stats = [("rej_flip_A3", "$A_3$ vs reversal null", ORANGE), ("rej_both_Acyc", "$\\mathcal{A}_{cyc}$ vs reversal and W1*", BLUE),
             ("rej_db_C2", "$C_2$ vs detailed-balance null", GREEN)]
    fig, ax = plt.subplots(1, 1, figsize=(7.0, 2.3))
    for k, (key, name, col) in enumerate(stats):
        for i, w in enumerate(worlds):
            v = np.array([s[sk][w][key] for sk in s])
            x = i + (k - 1) * 0.25
            ax.scatter(np.full(len(v), x), v, s=9, color=col, edgecolor="white", lw=0.4, zorder=3)
            ax.plot([x - 0.1, x + 0.1], [np.median(v)] * 2, color=INK, lw=1.0)
        ax.scatter([], [], color=col, s=10, label=name)
    ax.axhline(0.10, color=NULL, ls="--", lw=0.8); ax.axhline(0.5, color=NULL, ls=":", lw=0.8)
    ax.set_xticks(range(len(worlds))); ax.set_xticklabels([lab[w] for w in worlds], fontsize=6)
    ax.set_ylabel("rejection rate (p<0.05)"); ax.set_ylim(-0.03, 1.03); ax.grid(axis="y", color=GRID, lw=0.5)
    ax.legend(frameon=False, fontsize=6, loc="upper left")
    fig.tight_layout()
    fig.savefig(FIG / "summary_synth.pdf"); plt.close(fig)


if __name__ == "__main__":
    FIG.mkdir(exist_ok=True)
    synth()
    if (L.D / "results/units.json").exists():
        obs()
    print("figures written")
