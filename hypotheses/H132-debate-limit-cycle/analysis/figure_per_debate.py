"""H132 per-debate figure (figures/per_debate_col.pdf). Run from the repo root."""
import json, numpy as np, polars as pl, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
# H132 per-debate figure
R = json.load(open("data/processed/H132-debate-limit-cycle/results/results.json"))
fig, ax = plt.subplots(1,1,figsize=(3.4,2.4))
for k,(key,col) in enumerate((("bge_small|masked","#2a78d6"),("gte_modernbert|masked","#d03b3b"))):
    pdb = R[key]["per_debate"]
    ax.plot([p["debate"]+(k-0.5)*0.2 for p in pdb], [p["rho1"] for p in pdb], "o", color=col, ms=4, label=key.split("|")[0].split("_")[0]+" masked ρ₁")
ax.axhline(0, color="k", lw=0.5); ax.set_xlabel("debate"); ax.set_ylabel("lag-1 turn correlation")
ax.legend(fontsize=6, frameon=False); ax.set_title("per debate: ρ₁ mostly > 0 (cycle predicts < 0)", fontsize=7)
fig.tight_layout(); fig.savefig("hypotheses/H132-debate-limit-cycle/figures/per_debate_col.pdf"); fig.savefig("hypotheses/H132-debate-limit-cycle/figures/per_debate_col.png", dpi=150)
