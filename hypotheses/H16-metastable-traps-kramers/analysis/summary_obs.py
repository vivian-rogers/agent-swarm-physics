"""Focused two-panel figure for the one-page hypothesis summary: figures/summary_obs.pdf (~4.3 x 2.6 in).

Left: escape hazard vs time in the trap (TS1r, G51 and G38) against a flat (memoryless, Kramers) reference.
Right: kick dose response in G51 (TS1 undirected and directed; TS2r directed at the pause gate) against the Kramers
exponential extrapolation from dose 1 (ln HR_n = n ln HR_1).
Usage: uv run python hypotheses/H16-metastable-traps-kramers/analysis/summary_obs.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h16lib as L  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

plt.rcParams.update({"font.family": "serif", "font.size": 7, "axes.linewidth": 0.5, "pdf.fonttype": 42})
R51 = json.loads((L.OUT / "G51" / "results.json").read_text())
R38 = json.loads((L.OUT / "G38" / "results.json").read_text())
fig, ax = plt.subplots(1, 2, figsize=(4.3, 2.6))
for R, lab, c in ((R51, "G51 (8 h, 29 agents)", "C0"), (R38, "G38 (4 h, 14 agents)", "C1")):
    hc = R["a"]["TS1r"]["hazard_curve_per_30s"]
    x = np.array([np.sqrt(h["lo"] * h["hi"]) / 60 for h in hc]); y = np.array([h["h"] for h in hc]) * 2  # per minute
    ax[0].loglog(x, y, "o-", c=c, ms=3, lw=1, label=lab)
    b = R["a"]["TS1r"]["deep"]["beta_agentFE"]
    ax[0].text(x[-2] * 0.9, y[-2] * (1.8 if c == "C0" else 0.45), f"β = {b:.2f}", fontsize=6, color=c, va="center", ha="right")
ref = np.array([10, 160])
ax[0].loglog(ref, [R51["a"]["TS1r"]["hazard_curve_per_30s"][2]["h"] * 2] * 2, "k--", lw=0.7, label="memoryless (Kramers)")
ax[0].axvspan(3, 10, color="grey", alpha=0.12, lw=0)
ax[0].set_xlabel("time in inactive spell (min)"); ax[0].set_ylabel("escape hazard (per min)")
ax[0].set_title("(a) traps age", fontsize=7.5); ax[0].legend(fontsize=5.2, loc="lower left", frameon=False)
ax[0].set_xlim(2.5, 250)
d = np.array([1, 2, 3])
c1 = R51["c"]["TS1"]
for key, lab, col, mk in (("dose_undirected", "room msg → escape (TS1)", "C2", "o"), ("dose_directed", "mention/nudge → escape (TS1)", "C3", "s")):
    lhr = np.array(c1[key]["lhr"]); se = np.array(c1[key]["se"])
    ax[1].errorbar(d, np.exp(lhr), yerr=[np.exp(lhr) - np.exp(lhr - 1.96 * se), np.exp(lhr + 1.96 * se) - np.exp(lhr)], fmt=mk + "-", c=col, ms=3, lw=1, label=lab)
    ax[1].plot(d, np.exp(d * lhr[0]), ":", c=col, lw=0.9)
g = R51["c"]["TS2r"]["dose_directed"]
lo = np.array(g["lnOR"]); se = np.array(g["se"])
ax[1].errorbar(d, np.exp(lo), yerr=[np.exp(lo) - np.exp(lo - 1.96 * se), np.exp(lo + 1.96 * se) - np.exp(lo)], fmt="^-", c="C4", ms=3, lw=1, label="mention/nudge in pause → act at gate (OR)")
ax[1].plot(d, np.exp(d * lo[0]), ":", c="C4", lw=0.9)
ax[1].axhline(1, c="k", lw=0.4)
ax[1].set_xticks(d); ax[1].set_xticklabels(["1", "2", "3+"])
ax[1].set_xlabel("kicks (prior 2 min / during pause)"); ax[1].set_ylabel("hazard (odds) ratio vs no kick")
ax[1].set_title("(c) one kick is what matters (G51)", fontsize=7.5)
ax[1].legend(fontsize=4.8, loc="upper left", frameon=False)
ax[1].text(3.05, 0.97, "dotted: Kramers\n(exponential in dose)", fontsize=5, va="bottom", ha="right")
ax[1].set_ylim(0.9, max(ax[1].get_ylim()[1], 3.2))
fig.tight_layout(pad=0.4)
fig.savefig(L.HDIR / "figures" / "summary_obs.pdf")
print("ok")
