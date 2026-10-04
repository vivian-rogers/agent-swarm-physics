"""H17 round 1b page-2 figure: (a) t2*_eq on Jev v3 macro states vs mean p_blocked per period; (b) NE41 relaxation
after forced erasures in G51 vs the MSM's t2*. Writes figures/r1b_summary.pdf."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
D = ROOT / "data/processed/H17-behavior-metastable-sets/r1b"
COL = {"I": "#2a78d6", "II": "#eda100", "III": "#eb6834"}
INK, MUTED = "#0b0b0b", "#52514e"

plt.rcParams.update({"font.family": "serif", "font.size": 6.5, "axes.linewidth": 0.5, "pdf.fonttype": 42,
                     "axes.edgecolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED, "axes.labelcolor": INK})
s = json.loads((D / "summary_r1b.json").read_text())
n = json.loads((D / "native_r1b.json").read_text())
fig, ax = plt.subplots(1, 2, figsize=(3.45, 1.75))
for reg in ("I", "II", "III"):
    P = [p for p in s["periods"] if p["regime"] == reg and p["t2_eq"] and p["t2_eq"] < 5000]
    ax[0].scatter([p["cov_p_blocked"] for p in P], [p["t2_eq"] for p in P], s=10, color=COL[reg], label=f"regime {reg}",
                  edgecolor="white", linewidth=0.4, zorder=3)
ax[0].set_yscale("log")
ax[0].set_xlabel("mean $p_{\\rm blocked}$ (period)")
ax[0].set_ylabel("$t_2^*$ (v3, equal-$n$; min)")
ax[0].legend(frameon=False, fontsize=4.6, loc="center", bbox_to_anchor=(0.5, 0.56), ncol=3, handletextpad=0.1, columnspacing=0.5)
ax[0].set_title("(a) slowest mode vs stuckness", fontsize=6.5, color=INK)
g = n["N1_G51"]
k = np.arange(len(g["forced"]["d"]))
for tag, c, lab in (("forced", "#eb6834", "after forced erasure"), ("control", "#2a78d6", "mid-segment control")):
    d = np.array(g[tag]["d"])
    lo, hi = np.array(g[tag]["d_ci"])
    ax[1].plot(k * 5, d, "o-", color=c, ms=3, lw=1.2, label=lab, zorder=3)
    ax[1].fill_between(k * 5, lo, hi, color=c, alpha=0.18, lw=0)
lam = np.exp(-5 / g["t2_bc"])
d1 = g["forced"]["d"][1]
ax[1].plot(k[1:] * 5, d1 * lam ** (k[1:] - 1), "--", color=MUTED, lw=0.9, label=f"MSM decay ($t_2^*$={g['t2_bc']:.0f} min)")
ax[1].set_xlabel("min after anchor window")
ax[1].set_ylabel("TV dist. to agent mean")
ax[1].legend(frameon=False, fontsize=4.6, loc="upper left")
ax[1].set_title("(b) NE41 relaxation, G51", fontsize=6.5, color=INK)
for a in ax:
    a.spines[["top", "right"]].set_visible(False)
    a.grid(alpha=0.25, lw=0.3)
fig.tight_layout(pad=0.3, w_pad=0.6)
out = HERE.parent / "figures/r1b_summary.pdf"
fig.savefig(out)
print(out)
