"""H29 round 1b figure (figures/h29_r1b.pdf): (a) like-for-like named vs unnamed visibility jumps per unit, round 1
vs round 1b (ledger visibility; bge and gte); (b) held-out validation of the content-pull vs reply-graph driver score."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
B = ROOT / "data/processed/H29-driver-nodes"
U = ["G38", "G39", "G40", "G41", "G42", "G44", "G51b", "G51c", "G51d"]
fig, ax = plt.subplots(1, 2, figsize=(7.4, 3.0))
cols = {"r1": "#a0aec0", "r1b": "#2b6cb0", "r1b_gte": "#c05621"}
labs = {"r1": "round 1 (H18 rule)", "r1b": "1b bge (ledger)", "r1b_gte": "1b gte (ledger)"}
for k, root in enumerate(("r1", "r1b", "r1b_gte")):
    rr = B if root == "r1" else B / root
    for j, key in enumerate(("rd_named_ll", "rd_unnamed_ll")):
        xs, ys, lo, hi = [], [], [], []
        for i, u in enumerate(U):
            d = json.loads((rr / u / "results_posthoc.json").read_text())[key]
            if d.get("jump") is None or d.get("ci") is None:
                continue
            xs.append(i + (k - 1) * 0.22); ys.append(d["jump"]); lo.append(d["ci"][0]); hi.append(d["ci"][1])
        ys, lo, hi = np.array(ys), np.array(lo), np.array(hi)
        ax[0].errorbar(np.array(xs) + (0.0 if j == 0 else 0.06), ys, yerr=[ys - lo, hi - ys], fmt="o" if j == 0 else "s", ms=3,
                       lw=0.7, color=cols[root], mfc=cols[root] if j == 0 else "white",
                       label=f"{labs[root]}, {'named' if j == 0 else 'unnamed'}")
ax[0].axhline(0, color="0.5", lw=0.6); ax[0].set_xticks(range(len(U))); ax[0].set_xticklabels(U, fontsize=7, rotation=45)
ax[0].set_ylabel("visibility jump per message"); ax[0].set_ylim(-0.2, 0.25)
ax[0].set_title("(a) named (filled) vs unnamed (open), like-for-like", fontsize=8); ax[0].legend(fontsize=5, frameon=False, ncol=2)
for k, (root, lab) in enumerate((("r1b", "bge"), ("r1b_gte", "gte"))):
    E = json.loads((B / root / "r1b_extra.json").read_text())
    cont = [json.loads((B / root / u / "results_posthoc.json").read_text())["V"]["V2_D"] for u in U]
    rep = [E["units"][u]["V"]["V2_Drep"] for u in U]
    vol = [E["units"][u]["V"]["V2_vol"] for u in U]
    x = np.arange(len(U)) + (k - 0.5) * 0.3
    ax[1].scatter(x, cont, marker="x", color="#718096", s=14, label="content-pull D" if k == 0 else None)
    ax[1].scatter(x, vol, marker="+", color="#a0aec0", s=18, label="volume" if k == 0 else None)
    ax[1].scatter(x, rep, marker="o", color=cols[root], s=14, label=f"reply-graph D ({lab})")
ax[1].axhline(0, color="0.5", lw=0.6); ax[1].set_xticks(range(len(U))); ax[1].set_xticklabels(U, fontsize=7, rotation=45)
ax[1].set_ylabel("held-out ρ with 2-h swarm spread")
ax[1].set_title("(b) driver score validation (pooled: reply 0.23 / 0.12)", fontsize=8); ax[1].legend(fontsize=5.5, frameon=False)
fig.tight_layout(); fig.savefig(ROOT / "hypotheses/H29-driver-nodes/figures/h29_r1b.pdf"); plt.close(fig)
print("ok")
