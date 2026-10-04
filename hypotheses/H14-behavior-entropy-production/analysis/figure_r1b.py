"""H14 round 1b page-2 figure: (a) share of test agents above the DB null per period for the four turn-level chains;
(b) pooled v3 soft EP per transition per period with the block-flip null's 95th percentile. Writes figures/r1b_summary.pdf."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
D = ROOT / "data/processed/H14-behavior-entropy-production/r1b"
INK, MUTED = "#0b0b0b", "#52514e"
plt.rcParams.update({"font.family": "serif", "font.size": 6.5, "axes.linewidth": 0.5, "pdf.fonttype": 42,
                     "axes.edgecolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED})
s = json.loads((D / "summary_r1b.json").read_text())["periods"]
per = ["G27", "G37", "G38", "G39", "G40", "G41", "G42", "G44", "G51"]
fig, ax = plt.subplots(1, 2, figsize=(3.45, 1.8), gridspec_kw={"width_ratios": [1.15, 1]})
series = [("coarse", "coarse", "#2a78d6", "o"), ("coarse_b3", "coarse, agent-only b3", "#1baf7a", "s"),
          ("act_sh", "fine + shell sub", "#eb6834", "^"), ("act_sh_b3", "fine, agent-only b3", "#eda100", "D")]
x = np.arange(len(per))
for j, (key, lab, c, m) in enumerate(series):
    y = [s[p].get(f"{key}_frac_above_null") for p in per]
    ax[0].plot(x + (j - 1.5) * 0.12, [np.nan if v is None else v for v in y], m, color=c, ms=3, label=lab,
               markeredgecolor="white", markeredgewidth=0.3, ls="none")
ax[0].axhline(0.8, color=MUTED, lw=0.5, ls=":")
ax[0].set_xticks(x)
ax[0].set_xticklabels([p[1:] for p in per], fontsize=5.5)
ax[0].set_ylim(-0.42, 1.05)
ax[0].set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
ax[0].set_ylabel("share of agents > DB null")
ax[0].legend(frameon=False, fontsize=4.4, loc="lower center", ncol=2, handletextpad=0.1, borderpad=0.1, columnspacing=0.4)
ax[0].set_title("(a) single-agent arrows", fontsize=6.5, color=INK)
v = [s[p]["pooled_v3s"]["newton"] for p in per]
nl = [s[p]["pooled_v3s"].get("flip_null_p95") for p in per]
cols = ["#2a78d6" if p == "G27" else "#eb6834" for p in per]
ax[1].bar(x, v, width=0.62, color=cols, edgecolor="white", linewidth=0.5)
ax[1].plot(x, nl, "_", color=INK, ms=7, mew=1.0, label="flip-null 95th pct")
ax[1].set_xticks(x)
ax[1].set_xticklabels([p[1:] for p in per], fontsize=5.5)
ax[1].set_ylabel("pooled v3 EP (nats/5 min)")
ax[1].legend(frameon=False, fontsize=4.6, loc="upper left")
ax[1].set_title("(b) Jev v3 states, pooled", fontsize=6.5, color=INK)
for a in ax:
    a.spines[["top", "right"]].set_visible(False)
    a.grid(axis="y", alpha=0.25, lw=0.3)
fig.tight_layout(pad=0.3, w_pad=0.6)
out = HERE.parent / "figures/r1b_summary.pdf"
fig.savefig(out)
print(out)
