"""H23 round 1b page-2 figure: O3a d (corpus vs Kimi-field proximity) by group, in bge and gte."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
ROOT = Path(__file__).resolve().parents[3]
R = json.loads((ROOT / "data/processed/H23-leader-distillation-copy/G44/r1b/r1b.json").read_text())["C_embedding_two_models"]
plt.rcParams.update({"font.family": "serif", "font.size": 7, "axes.linewidth": 0.5, "pdf.fonttype": 42})
fig, ax = plt.subplots(figsize=(3.3, 2.1))
gs = ["leader", "K_same", "V_same"]
for k, (mdl, c) in enumerate((("bge_small", "#3f6fb5"), ("gte_modernbert", "#c2662d"))):
    ax.bar([i + 0.38 * k for i in range(3)], [R[mdl]["d_mean"][g] for g in gs], 0.36, color=c, label=mdl)
ax.set_xticks([i + 0.19 for i in range(3)]); ax.set_xticklabels(["leader (16)", "Kimi same window (6)", "other agents (39)"], fontsize=6)
ax.axhline(0, color="k", lw=0.5); ax.set_ylabel(r"$d=\cos(z,C)-\cos(z,K)$"); ax.legend(frameon=False, fontsize=6)
fig.tight_layout(); fig.savefig(ROOT / "hypotheses/H23-leader-distillation-copy/figures/r1b_summary_obs2.pdf")
