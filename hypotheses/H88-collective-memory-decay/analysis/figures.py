"""H88 summary figures: figures/summary_obs.pdf and figures/summary_obsb.pdf."""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h88lib as H  # noqa: E402

FIG = H.ROOT / "hypotheses/H88-collective-memory-decay/figures"
FIG.mkdir(exist_ok=True)
C = {"M1": "#2a78d6", "M2": "#eb6834", "M1c": "#1baf7a", "MP": "#eda100"}
INK, MUTED = "#2b2b2b", "#8a8a85"
plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": MUTED})
rep = json.loads((H.DATA / "replication" / "replication.json").read_text())
syn = json.loads((H.DATA / "synthetic" / "synthetic.json").read_text())
nat = json.loads((H.DATA / "natives" / "natives.json").read_text())
daily = H.load_daily()

fig, ax = plt.subplots(1, 2, figsize=(6.6, 2.5), gridspec_kw={"width_ratios": [1.4, 1]})
# (a) pooled term shares relative to the k 1-3 share, per period, with the median M1c fit
cur = []
for P, v in rep["periods"].items():
    r = v.get("term")
    if not r:
        continue
    k, y, O = H.series(daily, int(P), "term", "vet")
    e = (k <= 3)
    if y[e].sum() == 0:
        continue
    s0 = y[e].sum() / O[e].sum()
    bins = [(1, 1), (2, 2), (3, 3), (4, 5), (6, 8), (9, 13), (14, 21), (22, 34), (35, 55), (56, 89), (90, 120)]
    pts = []
    for lo, hi in bins:
        m = (k >= lo) & (k <= hi)
        if O[m].sum() > 0:
            pts.append((np.sqrt(lo * hi), y[m].sum() / O[m].sum() / s0))
    cur.append(pts)
    xs, ys = zip(*pts)
    ax[0].plot(xs, np.maximum(ys, 1e-3), color=MUTED, lw=0.6, alpha=0.6)
kk = np.logspace(0, np.log10(120), 100)
ct = rep["card"]["term"]
fc = np.exp(-kk / ct["M1c_tau_median"]) + ct["M1c_floor_ratio_median"]
ax[0].plot(kk, fc / fc[0], color=C["M1c"], lw=2, label=f"exp + floor: τ {ct['M1c_tau_median']:.1f} d, floor {ct['M1c_floor_ratio_median']:.3f}")
ax[0].plot(kk, np.exp(-(kk - 1) / ct["M1_tau_median"]), color=C["M1"], lw=1.2, ls="--", label=f"single exp: τ {ct['M1_tau_median']:.0f} d")
ax[0].set_xscale("log"); ax[0].set_yscale("log"); ax[0].set_ylim(1e-3, 3)
ax[0].set_xlabel("village days since the period ended"); ax[0].set_ylabel("share / share at days 1–3")
ax[0].set_title("(a) attention to a period's coined terms (20 periods)", fontsize=8, loc="left")
ax[0].legend(fontsize=6, frameon=False, loc="lower left")
# (b) best-model counts, real vs synthetic biexponential truth
groups = [("real terms", Counter(rep["card"]["term"]["best_counts"]), rep["card"]["term"]["n_periods"]),
          ("real artifacts", Counter(rep["card"]["art"]["best_counts"]), rep["card"]["art"]["n_periods"]),
          ("synthetic biexp\n(terms, NB2)", {m: v for m, v in syn["selection"]["term/S1_biexp/nb2"]["best_rate"].items()}, 1),
          ("synthetic biexp\n(artifacts, NB2)", {m: v for m, v in syn["selection"]["art/S1_biexp/nb2"]["best_rate"].items()}, 1)]
for i, (lab, cnt, n) in enumerate(groups):
    left = 0
    for m in ("M1", "M2", "M1c", "MP"):
        w = cnt.get(m, 0) / n
        ax[1].barh(i, w, left=left, color=C[m], height=0.6, edgecolor="white", lw=1, label=m if i == 0 else None)
        left += w
ax[1].set_yticks(range(len(groups))); ax[1].set_yticklabels([g[0] for g in groups], fontsize=6)
ax[1].set_xlabel("share of periods (best QAIC)"); ax[1].set_xlim(0, 1)
ax[1].set_title("(b) which decay law wins", fontsize=8, loc="left")
ax[1].legend(fontsize=6, frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.32))
fig.tight_layout(); fig.savefig(FIG / "summary_obs.pdf"); plt.close(fig)

fig, ax = plt.subplots(1, 2, figsize=(6.6, 2.1))
for j, (kind, col) in enumerate((("term", "#2a78d6"), ("art", "#eb6834"))):
    R = rep["card"][kind]["newcomer"]["R"]
    b = list(R)
    ax[0].plot(range(len(b)), [R[x] for x in b], "o-", color=col, label={"term": "terms", "art": "artifacts"}[kind])
ax[0].axhline(1, color=MUTED, lw=0.8)
ax[0].set_xticks(range(3)); ax[0].set_xticklabels(["1–10", "11–40", "41–120"])
ax[0].set_xlabel("village days since the period ended"); ax[0].set_ylabel("newcomers / veterans")
ax[0].set_title("(a) newcomers are not slower", fontsize=8, loc="left"); ax[0].legend(fontsize=6, frameon=False)
pe = nat["NE28"]["per_exit"]
names = [k for k in pe if k != "pooled"]
for i, k in enumerate(names):
    v = pe[k]
    ax[1].barh(i, v["carried_post_others"] / max(v["carried_pre_others"], 1), color="#2a78d6", height=0.6)
    ax[1].text(0.02, i, f"{v['carried_pre_others']} → {v['carried_post_others']}", va="center", fontsize=6, color="white" if
               v["carried_post_others"] / max(v["carried_pre_others"], 1) > 0.05 else INK)
ax[1].set_yticks(range(len(names))); ax[1].set_yticklabels(names, fontsize=6)
ax[1].set_xlabel("others' uses after / before (carried items)")
ax[1].set_title("(b) retirees' items: others' use", fontsize=8, loc="left")
fig.tight_layout(); fig.savefig(FIG / "summary_obsb.pdf"); plt.close(fig)
print("figures written")
