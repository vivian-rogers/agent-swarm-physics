"""H118 figures from results/results.json: G35 hourly overlap and code overlap; M_late and q_late by period."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h118lib as L  # noqa: E402

CARD = HERE.parent
RES = L.DATA / "results" / "results.json"
BLUE, ORANGE, GREEN, GREY, RED = "#2a78d6", "#e8871e", "#2a9d5c", "#85847e", "#c43a3a"


def main():
    R = json.loads(RES.read_text())
    P = R["periods"]
    (CARD / "figures").mkdir(exist_ok=True)
    (CARD / "goalperiod-subhypotheses/G35/figures").mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.8))
    for m, col, mk in (("bge_small", BLUE, "o"), ("gte_modernbert", ORANGE, "s")):
        r = P[f"35|{m}|main"]
        t, q, w = map(np.array, (r["hourly"]["t"], r["hourly"]["q"], r["hourly"]["w"]))
        ax[0].scatter(t, q, s=8 + 30 * w / w.max(), color=col, marker=mk, alpha=0.7, label=m.split("_")[0])
        ft = r["tau"]
        tt = np.linspace(0, t.max() + 0.5, 200)
        a, c = ft["q_inf"], ft["q0"] - ft["q_inf"]
        ax[0].plot(tt, a + c * np.exp(-tt / ft["tau"]), color=col, lw=1)
        band = [P[f"{b}|{m}|main"]["q_late"] for b in L.BAND]
        ax[0].axhspan(min(band), max(band), color=col, alpha=0.08)
        rel = np.mean(list(r["q_rel_d"].values()))
        ax[0].axhline(rel, color=col, ls=":", lw=1)
    for d in range(1, 5):
        ax[0].axvline(4 * d, color=GREY, lw=0.5)
    ax[0].set_xlabel("active hours since the fork (4 h per day)")
    ax[0].set_ylabel("replica overlap $q_{eq}$")
    ax[0].set_title("G35 content: rooms' overlap by hour", fontsize=9)
    ax[0].legend(fontsize=7, frameon=False)
    code = R["code"]
    hrs = [c for c in code if c["kind"] == "hour"]
    x = np.arange(len(hrs)) + 1
    for fam, col in (("src", BLUE), ("functions", GREEN)):
        ax[1].plot(x, [c[f"{fam}_q"] for c in hrs], color=col, label=f"{fam}: identical in both forks")
        ax[1].plot(x, [c[f"{fam}_q_ind"] for c in hrs], color=col, ls="--", label=f"{fam}: independent replicas")
    ax[1].set_xlabel("active hours since the fork")
    ax[1].set_ylabel("share of ancestor keys")
    ax[1].set_title("G35 game state: code overlap", fontsize=9)
    ax[1].legend(fontsize=6, frameon=False)
    fig.tight_layout()
    fig.savefig(CARD / "goalperiod-subhypotheses/G35/figures/g35_overlap.pdf")
    fig.savefig(CARD / "figures/g35_overlap.pdf")
    plt.close(fig)
    # by period
    pers = ["35", "36", "37", "38", "39", "41", "42", "44"]
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.6))
    for k, (m, col, off) in enumerate((("bge_small", BLUE, -0.12), ("gte_modernbert", ORANGE, 0.12))):
        for i, p in enumerate(pers):
            r = P[f"{p}|{m}|main"]
            b = r["boot_agent_bin"]
            lo, hi = b["M_late_ci"]
            ax[0].errorbar(i + off, r["M_late"], yerr=[[r["M_late"] - lo], [hi - r["M_late"]]], fmt="o" if k == 0 else "s",
                           color=col, ms=4, lw=1, mfc=col if k == 0 else "white")
            lo, hi = b["q_late_ci"]
            ax[1].errorbar(i + off, r["q_late"], yerr=[[r["q_late"] - lo], [hi - r["q_late"]]], fmt="o" if k == 0 else "s",
                           color=col, ms=4, lw=1, mfc=col if k == 0 else "white")
    ax[0].axhline(0, color=GREY, lw=0.8)
    for a_ in ax:
        a_.set_xticks(range(len(pers)))
        a_.set_xticklabels([f"#{p}" for p in pers], fontsize=7)
    ax[0].set_ylabel("equal-time memory $M_{late}$")
    ax[1].set_ylabel("late overlap $q_\\infty^{late}$")
    ax[0].set_title("memory beyond the static overlap (days $\\geq$ 2)", fontsize=9)
    ax[1].set_title("late overlap (G35 green band = identical-kickoff periods)", fontsize=8)
    ax[1].axvspan(-0.4, 0.4, color=GREEN, alpha=0.08)
    fig.tight_layout()
    fig.savefig(CARD / "figures/by_period.pdf")
    plt.close(fig)
    print("figures written")


if __name__ == "__main__":
    main()
