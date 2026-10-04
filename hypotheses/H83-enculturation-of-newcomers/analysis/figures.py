"""H83 summary figures: figures/summary_obs.pdf and figures/summary_obsb.pdf."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h83lib as L  # noqa: E402

FIG = L.ROOT / "hypotheses/H83-enculturation-of-newcomers/figures"
C1, C2, C3, INK, MUTED = "#2a78d6", "#eb6834", "#1baf7a", "#2b2b2b", "#8a8a85"
plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK})
rep = json.loads((L.DATA / "replication" / "replication.json").read_text())
syn = json.loads((L.DATA / "synthetic" / "synthetic.json").read_text())
nat = json.loads((L.DATA / "natives" / "natives.json").read_text())
newc = L.newcomers(); name = dict(zip(newc["agent"].to_list(), newc["name"].to_list()))
J = rep["joins"]
order = sorted(J, key=lambda a: J[a]["join_day"])

fig, ax = plt.subplots(1, 2, figsize=(6.6, 2.5), gridspec_kw={"width_ratios": [1.6, 1]})
x = np.arange(len(order))
gb = [J[a]["G"]["delta"] for a in order]; gg = [J[a].get("G_gte", {}).get("delta", np.nan) for a in order]
ax[0].axhspan(-0.032, 0.032, color="#ecebe6", zorder=0, label="synthetic null 95% (mean of 19)")
ax[0].axhline(0, color=MUTED, lw=0.8)
ax[0].scatter(x - 0.12, gb, s=14, color=C1, label="bge", zorder=3)
ax[0].scatter(x + 0.12, gg, s=14, color=C2, marker="s", label="gte", zorder=3)
c = rep["card"]["G"]; cg = rep["variants"]["gte"]["G"]
ax[0].errorbar([len(order) + 0.8], [c["mean"]], yerr=[[c["mean"] - c["lo"]], [c["hi"] - c["mean"]]], fmt="o", color=C1, ms=5)
ax[0].errorbar([len(order) + 1.3], [cg["mean"]], yerr=[[cg["mean"] - cg["lo"]], [cg["hi"] - cg["mean"]]], fmt="s", color=C2, ms=5)
ax[0].set_xticks(list(x) + [len(order) + 1.05])
ax[0].set_xticklabels([name[int(a)].replace("Claude ", "").replace("GPT-5.6 ", "") for a in order] + ["mean"], rotation=70, fontsize=6)
ax[0].set_ylabel("enculturation index ΔG")
ax[0].set_title("(a) newcomers' move toward the veterans, by join", fontsize=8, loc="left")
ax[0].legend(fontsize=6, frameon=False, loc="upper left")
ks = [(J[a]["K"]["gap_E"], J[a]["K"]["gap_L"]) for a in order if J[a].get("K")]
for e, l_ in ks:
    ax[1].plot([0, 1], [e, l_], color=C3, lw=0.8, alpha=0.7)
ke = rep["card"]["K_E"]; kd = rep["card"]["K"]
ax[1].errorbar([-0.1], [ke["mean"]], yerr=[[ke["mean"] - ke["lo"]], [ke["hi"] - ke["mean"]]], fmt="o", color=INK, ms=4)
ax[1].axhline(0, color=MUTED, lw=0.8)
ax[1].set_xticks([0, 1]); ax[1].set_xticklabels(["days 2–4", "days 8–14"])
ax[1].set_ylabel("family signature K")
ax[1].set_title(f"(b) family signature fades: ΔK {kd['mean']:+.3f}", fontsize=8, loc="left")
fig.tight_layout(); fig.savefig(FIG / "summary_obs.pdf"); plt.close(fig)

fig, ax = plt.subplots(1, 2, figsize=(6.6, 2.1))
sc = syn["scenarios"]
labs = [("S0_lam0.0", "null S0"), ("S0b_lam0.0", "null S0b"), ("S1_lam0.5", "dose, closure 0.5"), ("S1_lam1.0", "dose, closure 1"),
        ("S2_lam0.5", "time, closure 0.5"), ("S2_lam1.0", "time, closure 1")]
vals = [sc[k]["G"]["reject_pos"] for k, _ in labs]
ax[0].barh(range(len(labs)), vals, color=[MUTED, MUTED, C1, C1, C3, C3], height=0.6)
ax[0].axvline(0.8, color=C2, lw=1, ls="--"); ax[0].text(0.81, 4.7, "0.8", color=C2, fontsize=6)
ax[0].set_yticks(range(len(labs))); ax[0].set_yticklabels([l for _, l in labs], fontsize=6)
ax[0].set_xlim(0, 1); ax[0].set_xlabel("P1 rejection rate (40 replicates)")
ax[0].set_title("(a) synthetic power of the pooled ΔG test", fontsize=8, loc="left")
g = nat["bge"]["G38"]; gg = nat["gte"]["G38"]
for i, (v, lab, col) in enumerate([(g, "bge", C1), (gg, "gte", C2)]):
    ax[1].errorbar([i - 0.1], [v["R_new"]], yerr=[[v["R_new"] - v["R_new_ci"][0]], [v["R_new_ci"][1] - v["R_new"]]],
                   fmt="o", color=col, ms=5, label=f"newcomers ({lab})")
    ax[1].scatter([i + 0.1], [v["R_vet"]], marker="D", color=INK, s=14, label="veterans" if i == 0 else None)
ax[1].axhline(0, color=MUTED, lw=0.8)
ax[1].set_xticks([0, 1]); ax[1].set_xticklabels(["bge", "gte"]); ax[1].set_ylabel("own room − other room")
ax[1].set_title("(b) #38: own-room alignment", fontsize=8, loc="left")
ax[1].legend(fontsize=6, frameon=False, loc="lower right")
fig.tight_layout(); fig.savefig(FIG / "summary_obsb.pdf"); plt.close(fig)
print("figures written")
