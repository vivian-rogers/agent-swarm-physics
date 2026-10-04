"""H130 synthetic figure (figures/synthetic_col.pdf). Run from the repo root."""
import json, numpy as np, polars as pl, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
# H130 synthetic figure
d = pl.read_parquet("data/processed/H130-ou-private-wells-51/synthetic/runs.parquet")
ws = ["W0_null","W1_kick","W1_kick_strong","W1_fastdrive","W1_slowdrive","W1s_slow","W2_context","W3_drive"]
lab = ["null","kick","kick×2","5-min drive","3-h drive","slow well","context kick","drive only"]
fig, ax = plt.subplots(1,2,figsize=(7,2.6))
for k,w in enumerate(ws):
    x = d.filter(pl.col("world")==w)
    ax[0].scatter(np.full(x.height,k)-0.12, x["g_auto"], s=8, color="#2a78d6", label="γ_auto" if k==0 else None)
    ax[0].scatter(np.full(x.height,k)+0.12, np.clip(x["g_kick"].to_numpy(),1e-4,None), s=8, color="#d03b3b", label="γ_kick" if k==0 else None)
    ax[0].scatter(np.full(x.height,k), x["g_auto_raw"], s=6, marker="x", color="#86b6ef", label="γ_auto raw" if k==0 else None)
ax[0].axhline(0.01, color="k", lw=0.5, ls=":"); ax[0].set_yscale("log"); ax[0].set_xticks(range(len(ws))); ax[0].set_xticklabels(lab, rotation=50, fontsize=6)
ax[0].set_ylabel("rate per call"); ax[0].legend(fontsize=6, frameon=False); ax[0].set_title("recovery (planted 0.01; slow well 0.003; context kick 0.05)", fontsize=7)
for k,w in enumerate(ws):
    x = d.filter(pl.col("world")==w)
    ax[1].scatter(np.full(x.height,k), x["J"], s=8, color="#5598e7")
ax[1].axhline(0, color="k", lw=0.5); ax[1].set_xticks(range(len(ws))); ax[1].set_xticklabels(lab, rotation=50, fontsize=6)
ax[1].set_ylabel("read jump J_K (per unit)"); ax[1].set_title("in-flight contrast per unit (3 units × 3 reps)", fontsize=7)
fig.tight_layout(); fig.savefig("hypotheses/H130-ou-private-wells-51/figures/synthetic_col.pdf"); fig.savefig("hypotheses/H130-ou-private-wells-51/figures/synthetic_col.png", dpi=150)
