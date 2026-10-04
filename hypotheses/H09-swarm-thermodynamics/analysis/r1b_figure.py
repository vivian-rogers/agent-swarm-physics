"""H09 round 1b page-2 figure: (a) P(act) at the regime-III timer gate by what newly entered the call; (b) AR(1) of ln V."""
import json
from pathlib import Path
import numpy as np
import polars as pl
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
ROOT = Path(__file__).resolve().parents[3]
D = ROOT / "data/processed/H09-swarm-thermodynamics/r1b"
g = pl.read_parquet(D / "gate_calls.parquet")
plt.rcParams.update({"font.family": "serif", "font.size": 7, "axes.linewidth": 0.5, "pdf.fonttype": 42})
cats = {"no new item": g["no_new"], "agent msgs only": g["agent_msg"] & ~g["ment"] & ~g["nudge_me"] & ~g["human"],
        "@-mention": g["ment"], "nudge": g["nudge_me"], "human": g["human"]}
fig, ax = plt.subplots(1, 2, figsize=(6.6, 2.2))
p = [float(g.filter(m)["act"].mean()) for m in cats.values()]; n = [int(m.sum()) for m in cats.values()]
ax[0].bar(range(len(p)), p, color=["0.6", "#c2662d", "#3f6fb5", "#3a7d6b", "#7a4b9c"])
for i, (pp, nn) in enumerate(zip(p, n)):
    ax[0].text(i, pp + 0.01, f"n={nn}", ha="center", fontsize=5)
ax[0].set_xticks(range(len(p))); ax[0].set_xticklabels(list(cats), fontsize=6); ax[0].set_ylim(0, 1); ax[0].set_ylabel("P(act at post-pause call)")
m = json.loads((D / "r1b_memory.json").read_text())["N3_homeostat"]
phis = [a["phi"] for a in m["per_agent"]]
ax[1].hist(phis, bins=15, color="#3f6fb5")
for k, c in (("phi_after_forced", "#c2662d"), ("phi_after_voluntary", "0.3")):
    ax[1].axvline(m[k]["phi"], color=c, lw=1, label=k.replace("phi_after_", "pooled, after "))
ax[1].axvline(0, color="k", lw=0.5); ax[1].set_xlabel(r"AR(1) $\phi$ of $\ln V$ toward the agent mean"); ax[1].set_ylabel("agents"); ax[1].legend(frameon=False, fontsize=5)
fig.tight_layout(); fig.savefig(ROOT / "hypotheses/H09-swarm-thermodynamics/figures/r1b_summary_obs2.pdf")
