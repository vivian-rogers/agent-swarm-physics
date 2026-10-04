"""H07 round-1b page-2 figure: (a) cross-team chat reads per day (ledger), (b) independent-lineage bound: identity on
ancestor keys vs P(both unchanged) for the RPG forks (end of #35, files) and the agent-papers copy pairs.
Usage: uv run python hypotheses/H07-rpg-forks/analysis/summary_figure_r1b.py"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
P = ROOT / "data/processed/H07-rpg-forks"
r = json.loads((P / "r1b/results_r1b.json").read_text())
fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.2))
d = {}
for x in r["ledger"]["cross_by_day"]:
    d.setdefault(x["pt_date"][5:], {})[x["r_team"]] = x["cross_items"]
days = sorted(d)
import numpy as np  # noqa: E402
xi = np.arange(len(days))
ax[0].bar(xi - 0.2, [d[k].get("best", 0) for k in days], 0.4, color="#2a78d6", label="read by #best")
ax[0].bar(xi + 0.2, [d[k].get("rest", 0) for k in days], 0.4, color="#eb6e3d", label="read by #rest")
ax[0].set_xticks(xi, days, fontsize=6, rotation=45)
ax[0].set_ylabel("cross-team items read", fontsize=7)
ax[0].tick_params(labelsize=6)
ax[0].legend(fontsize=6, frameon=False)
ax[0].set_title("(a) the light cone (ledger)", fontsize=8)
hd = pl.read_parquet(P / "horizontal_day.parquet").filter(pl.col("pt_date") == "2026-03-20")
pts = [("RPG best~rest", hd["files_anc_both_unch"][0], hd["files_anc_same"][0], "#0b0b0b")]
for k, v in r["papers"]["pairs"].items():
    pts.append((v["rooms"], v["anc_both_unch"], v["anc_same"], "#2a78d6" if v["excess"] > 0.02 else "#85847e"))
ax[1].plot([0.5, 1.02], [0.5, 1.02], color="#cccccc", lw=0.8)
for lab, xx, yy, c in pts:
    ax[1].scatter(xx, yy, s=18, color=c, zorder=3)
ax[1].annotate("RPG forks (no channel)", (pts[0][1], pts[0][2]), fontsize=6, xytext=(4, -9), textcoords="offset points")
ax[1].annotate("agent-papers rest~org\n(upstream syncs)", (0.667, 0.967), fontsize=6, xytext=(4, -14), textcoords="offset points")
ax[1].set_xlabel("P(both unchanged), ancestor files", fontsize=7)
ax[1].set_ylabel("P(same file), ancestor files", fontsize=7)
ax[1].tick_params(labelsize=6)
ax[1].set_title("(b) independent-lineage bound", fontsize=8)
fig.tight_layout()
fig.savefig(ROOT / "hypotheses/H07-rpg-forks/figures/summary_r1b.pdf")
