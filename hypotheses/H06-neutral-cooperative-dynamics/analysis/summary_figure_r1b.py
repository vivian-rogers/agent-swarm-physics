"""H06 round-1b page-2 figure. (a) singleton fraction per period: stated goals (round 1 bge km24, round 1b gte_sr km24)
and work labels (DQ4), with #35 (known universe) as control. (b) copying channel: switch probability per candidate
by exposure (V read, U posted-unread, N none), attention and work, pooled.
Usage: H06_DATA=r1b uv run python hypotheses/H06-neutral-cooperative-dynamics/analysis/summary_figure_r1b.py"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
R = ROOT / "data/processed/H06-neutral-cooperative-dynamics/r1b"
L = json.loads((R / "light_r1b.json").read_text())
cp = json.loads((R / "copying_r1b.json").read_text())
order = ["G11", "G16", "G31", "G37", "G44", "G19", "G25", "G30", "G38", "G51a", "G51b", "G51c", "G35"]
fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.3), gridspec_kw={"width_ratios": [1.6, 1]})
x = np.arange(len(order))
r1 = [L[s].get("round1", {}).get("km24", {}).get("single", np.nan) for s in order]
r1b = [L[s]["sets"]["km24"]["single"] for s in order]
wk = [L[s]["sets"].get("work", {}).get("single", np.nan) if L[s]["sets"].get("work", {}).get("per_win", 0) >= 3 else np.nan
      for s in order]
ax[0].scatter(x - 0.15, r1, s=14, color="#85847e", label="stated goals, round 1 (bge)")
ax[0].scatter(x, r1b, s=14, color="#2a78d6", label="stated goals, 1b (gte, style removed)")
ax[0].scatter(x + 0.15, wk, s=18, color="#eb6e3d", marker="s", label="work (DQ4 commits)")
ax[0].axvspan(-0.5, 4.5, color="#f2f1ec", zorder=0)
ax[0].axvline(11.5, color="#cccccc", lw=0.8)
ax[0].set_xticks(x, [s.replace("G", "#") for s in order], fontsize=6, rotation=45)
ax[0].set_ylabel("singleton fraction", fontsize=7)
ax[0].set_ylim(0, 1.02)
ax[0].tick_params(labelsize=6)
ax[0].legend(fontsize=5.5, frameon=False, loc="lower left")
ax[0].set_title("(a) projects held by one agent", fontsize=8)
cls = ["V", "U", "N"]
for i, (nm, col) in enumerate((("art", "#2a78d6"), ("work", "#eb6e3d"))):
    ps = cp["pooled"][nm]
    rate = [ps["n_switches"][c] / ps["n_candidates"][c] for c in cls]
    ax[1].bar(np.arange(3) + (i - 0.5) * 0.38, rate, 0.38, color=col, label="attention" if nm == "art" else "work")
ax[1].set_xticks(np.arange(3), ["read\n(V)", "posted,\nunread (U)", "not\nmentioned (N)"], fontsize=6)
ax[1].set_ylabel("P(switch to project)", fontsize=7)
ax[1].tick_params(labelsize=6)
ax[1].legend(fontsize=6, frameon=False)
ax[1].set_title("(b) copying needs reading", fontsize=8)
fig.tight_layout()
fig.savefig(ROOT / "hypotheses/H06-neutral-cooperative-dynamics/figures/summary_r1b.pdf")
