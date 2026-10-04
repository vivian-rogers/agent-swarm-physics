"""H61 figures: figures/summary_obs.pdf (real data) and figures/summary_obs2.pdf (synthetic + coefficients).

  uv run python hypotheses/H61-contagiousness-at-first-use/analysis/figures.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
HYP = HERE.parent
ROOT = HYP.parents[1]
DATA = ROOT / "data/processed/H61-contagiousness-at-first-use"
FIG = HYP / "figures"
REG = {"I": ("#2a78d6", "o"), "II": ("#eb6834", "s"), "III": ("#1baf7a", "^")}
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e9e7e1"
POWERED = 2500
plt.rcParams.update({"font.size": 7.5, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
                     "font.family": "serif"})


def fig1():
    rows = [r for r in json.loads((DATA / "results/periods.json").read_text()) if r.get("eligible")]
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.4), gridspec_kw=dict(width_ratios=[1.35, 1]))
    a = ax[0]
    for i, r in enumerate(rows):
        c, m = REG[r["regime"]]
        pw = r["n_test"] >= POWERED
        a.plot([i, i], [r["dll_F_B4_lo"], r["dll_F_B4_hi"]], color=c, lw=1.2)
        a.plot(i, r["dll_F_B4"], marker=m, ms=4.5, color=c if pw else "white", mec=c, mew=1.0, zorder=3)
    a.axhline(0, color=INK2, lw=0.8)
    a.set_xticks(range(len(rows)))
    a.set_xticklabels([f"{r['goal']}" for r in rows], fontsize=5.5, rotation=90)
    a.set_ylabel(r"$\Delta$LL(F $-$ B4), millinats / idea")
    a.set_xlabel("goal period (open: < 2,500 test ideas, underpowered)")
    for k, (c, m) in REG.items():
        a.plot([], [], marker=m, color=c, ls="", label=f"regime {k}")
    a.legend(frameon=False, fontsize=6, loc="upper left")
    a.grid(axis="y", color=GRID, lw=0.6)
    a.set_title("(a) held-out gain of seed features over the strongest baseline", fontsize=7.5, loc="left")
    b = ax[1]
    for r in rows:
        c, m = REG[r["regime"]]
        b.plot(r["auc_B4"], r["auc_F"], marker=m, ms=4.5, color=c, ls="", mec="white", mew=0.4)
        b.plot(r["auc_B1"], r["auc_F"], marker=m, ms=3.5, color="white", mec=c, mew=0.8, ls="")
    lo = min(min(r["auc_B1"] for r in rows), min(r["auc_F"] for r in rows)) - 0.02
    b.plot([lo, 1], [lo, 1], color=INK2, lw=0.8, ls="--")
    b.set_xlim(lo, 0.9); b.set_ylim(lo, 0.9)
    b.set_xlabel("baseline AUC (filled: B4; open: B1 class only)")
    b.set_ylabel("AUC of F (seed features)")
    b.grid(color=GRID, lw=0.6)
    b.set_title("(b) held-out AUC, reach ≥ 2 in 24 h", fontsize=7.5, loc="left")
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs.pdf")


def fig2():
    syn = json.loads((DATA / "synthetic/summary.json").read_text())
    sm = json.loads((DATA / "results/summary.json").read_text())
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.3), gridspec_kw=dict(width_ratios=[1, 1.2]))
    a = ax[0]
    ps = [k for k in syn["null"] if k != "all"]
    x = np.arange(len(ps))
    w = 0.26
    a.bar(x - w, [syn["null"][p]["rej_F_B3"] for p in ps], w, color="#86b6ef", label="null: F vs B3")
    a.bar(x, [syn["null"][p]["rej_F_B4"] for p in ps], w, color="#2a78d6", label="null: F vs B4 (A1)")
    a.bar(x + w, [syn["power"][p]["rej_F_B4"] for p in ps], w, color="#eb6834", label="power: F vs B4")
    a.axhline(0.05, color=INK2, lw=0.8, ls=":")
    a.axhline(0.8, color=INK2, lw=0.8, ls="--")
    a.set_xticks(x); a.set_xticklabels(ps, fontsize=6.5)
    a.set_ylabel("rejection rate (CI > 0)")
    a.legend(frameon=False, fontsize=5.8, loc="upper left", ncol=1, bbox_to_anchor=(0.0, 0.78))
    a.set_title("(a) synthetic size and power on real features", fontsize=7.5, loc="left")
    b = ax[1]
    names = {"lg_novel": "focus (log novel load)", "lg_len": "seed length", "spec": "specificity (goal distance)",
             "indeg": "poster reply in-degree", "f_rec": "receptive fraction", "addressed": "addressed (@)",
             "threaded": "threaded (DQ2 parent)", "kick": "kickoff day", "lg_npres": "room size"}
    fs = list(names)
    for i, f in enumerate(fs):
        c = sm[f"coef_{f}"]
        mu, se, _ = c["pooled"]
        b.plot([mu - 1.96 * se, mu + 1.96 * se], [i, i], color="#2a78d6", lw=1.4)
        b.plot(mu, i, "o", color="#2a78d6", ms=4)
        b.text(0.22, i, f"{c['n_ci_neg']}−/{c['n_ci_pos']}+", ha="right", va="center", fontsize=5.8, color=INK2)
    b.axvline(0, color=INK2, lw=0.8)
    b.set_xlim(-0.4, 0.23)
    b.set_yticks(range(len(fs))); b.set_yticklabels([names[f] for f in fs], fontsize=6.3)
    b.invert_yaxis()
    b.set_xlabel("pooled std. log-odds (text: periods CI<0 / CI>0)")
    b.grid(axis="x", color=GRID, lw=0.6)
    b.set_title("(b) which seed features carry fitness", fontsize=7.5, loc="left")
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs2.pdf")


if __name__ == "__main__":
    FIG.mkdir(exist_ok=True)
    fig1()
    fig2()
    print("figures written")
