"""H16 round 1b page-2 figure: (a) error-loop aging slope per period, stderr (round 1) vs real failures (1b), and
the v3 blocked-spell slope; (b) NE44: TS2r gate escape by chain depth, with and without a directed kick, before
(G37-G44) and after (G51 07-06 -> 08-20) the pause-default change. Writes figures/r1b_summary.pdf."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import native_r1b as N  # noqa: E402

ROOT = HERE.parents[2]
D = ROOT / "data/processed/H16-metastable-traps-kramers/r1b"
INK, MUTED = "#0b0b0b", "#52514e"
plt.rcParams.update({"font.family": "serif", "font.size": 6.5, "axes.linewidth": 0.5, "pdf.fonttype": 42,
                     "axes.edgecolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED})
s = json.loads((D / "summary_r1b.json").read_text())["periods"]
per = [p for p in ["G27", "G30", "G31", "G37", "G38", "G39", "G40", "G41", "G42", "G44", "G51"] if p in s]
fig, ax = plt.subplots(1, 2, figsize=(3.45, 1.8), gridspec_kw={"width_ratios": [1.2, 1]})
x = np.arange(len(per))
for j, (key, src, lab, c, m) in enumerate((("ts3", "round1", "error loops, stderr (r1)", "#2a78d6", "o"),
                                           ("ts3", "r1b", "error loops, real fail. (1b)", "#eb6834", "s"),
                                           ("ts5", "r1b", "v3 blocked spells (1b)", "#1baf7a", "^"))):
    b = np.array([s[p][src][f"{key}_beta"] if s[p][src] else np.nan for p in per], float)
    w = np.array([s[p][src][f"{key}_wald"] if s[p][src] else [np.nan, np.nan] for p in per], float)
    ok = np.isfinite(b) & (np.abs(b) < 4)
    xx = x + (j - 1) * 0.22
    ax[0].errorbar(xx[ok], b[ok], yerr=[(b - w[:, 0])[ok], (w[:, 1] - b)[ok]], fmt=m, color=c, ms=2.6, lw=0.6,
                   capsize=0, label=lab, markeredgecolor="white", markeredgewidth=0.3)
ax[0].axhspan(-0.3, 0.3, color=MUTED, alpha=0.12, lw=0)
ax[0].axhline(0, color=MUTED, lw=0.4)
ax[0].set_ylim(-4.7, 3.3)
ax[0].set_yticks([-2, -1, 0, 1, 2, 3])
ax[0].set_xticks(x)
ax[0].set_xticklabels([p[1:] for p in per], fontsize=5.3)
ax[0].set_ylabel("slope of break hazard on ln k")
ax[0].legend(frameon=False, fontsize=4.2, loc="lower center", ncol=2, handletextpad=0.1, borderpad=0.1, columnspacing=0.3)
ax[0].set_title("(a) loop aging (band: memoryless)", fontsize=6.5, color=INK)
pre = pl.concat([N.gates(p) for p in N.PRE], how="diagonal_relaxed")
post = N.gates("G51", d1="2026-08-20")
for g, ls, tag in ((pre, "--", "before NE44"), (post, "-", "after NE44")):
    g = g.filter((pl.col("outcome") != "censored") & (pl.col("declared_s") > 0))
    y = (g["outcome"] != "repause").to_numpy()
    k = np.minimum(g["k"].to_numpy(), 5)
    Dk = np.sum([g[c].to_numpy() for c in N.DIRECTED], axis=0) > 0
    for dflag, c, nm in ((True, "#eb6834", "kick"), (False, "#2a78d6", "no kick")):
        pk = [y[(k == kk) & (Dk == dflag)].mean() if ((k == kk) & (Dk == dflag)).sum() >= 15 else np.nan for kk in range(1, 6)]
        ax[1].plot(range(1, 6), pk, ls, color=c, marker="o", ms=2.5, lw=1.0, label=f"{nm}, {tag}")
ax[1].set_xticks(range(1, 6))
ax[1].set_xticklabels(["1", "2", "3", "4", "5+"])
ax[1].set_xlabel("pause-chain depth k")
ax[1].set_ylabel("P(escape at gate)")
ax[1].set_ylim(0, 1)
ax[1].legend(frameon=False, fontsize=4.2, loc="upper right", handletextpad=0.2)
ax[1].set_title("(b) NE44 gate model", fontsize=6.5, color=INK)
for a in ax:
    a.spines[["top", "right"]].set_visible(False)
    a.grid(axis="y", alpha=0.25, lw=0.3)
fig.tight_layout(pad=0.3, w_pad=0.6)
out = HERE.parent / "figures/r1b_summary.pdf"
fig.savefig(out)
print(out)
