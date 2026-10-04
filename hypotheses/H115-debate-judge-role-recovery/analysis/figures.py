"""H115 figures: figures/summary_obs.pdf (judge and leader sink ranks) and figures/synthetic.pdf (power).

  uv run python hypotheses/H115-debate-judge-role-recovery/analysis/figures.py
"""
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
import h115lib as L  # noqa: E402

FIG = HERE.parent / "figures"
BLUE, RED, GREY = "#2a78d6", "#d03b3b", "#85847e"


def main():
    FIG.mkdir(exist_ok=True)
    r12 = json.loads((L.DATA / "G12" / "results.json").read_text())
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.6), gridspec_kw={"width_ratios": [1.25, 1]})
    a = ax[0]
    rs = np.array(r12["P1"]["judge_ranks"])
    rp = np.array(r12["P1c"]["judge_ranks_inflight"])
    x = np.arange(1, len(rs) + 1)
    a.axhspan(3.5, 7.5, color="#ecebe6", zorder=0)
    a.plot(x - 0.12, rs, "o", color=BLUE, label="read-gated $S^R$")
    a.plot(x + 0.12, rp, "s", color=GREY, mfc="none", label="in-flight $S^P$")
    a.axhline(np.median(rs), color=BLUE, lw=1, ls="--")
    a.set_ylim(7.5, 0.5)
    a.set_yticks(range(1, 8))
    a.set_xticks(x)
    a.set_xlabel("debate (#12)")
    a.set_ylabel("judge's sink rank (1 = top)")
    a.set_title("G12: blind judge rank", fontsize=9)
    a.legend(fontsize=7, loc="lower right", frameon=False)
    a = ax[1]
    pos = 0
    ticks, labs = [], []
    for g, col in (("G26", RED), ("G35", "#fab219"), ("G44", "#5598e7")):
        p = L.DATA / g / "replication.json"
        if not p.exists():
            continue
        rep = json.loads(p.read_text())
        us = [v["u"] for v in rep["windows"].values() if v is not None]
        nul = [rep["skeleton"][w]["mean_u_null"] for w, v in rep["windows"].items() if v is not None]
        xs = pos + np.arange(len(us))
        a.bar(xs, us, color=col, width=0.7)
        a.plot(xs, nul, "_", color="k", ms=10, mew=1.5)
        ticks.append(xs.mean())
        labs.append(g)
        pos += len(us) + 1
    us_j = (rs - 1) / 6
    a.axhline(0.5, color=GREY, lw=0.8)
    a.axhline(us_j.mean(), color=BLUE, lw=1, ls="--")
    a.text(0.2, us_j.mean() - 0.07, "judges (G12) mean", color=BLUE, fontsize=7)
    a.set_xticks(ticks)
    a.set_xticklabels(labs)
    a.set_ylim(0, 1.05)
    a.set_ylabel("leader's normalized rank $u_L$\n(0 = top sink, 1 = top source)", fontsize=8)
    a.set_title("leaders by role window (– skeleton null)", fontsize=9)
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs.pdf")
    # synthetic
    syn = json.loads((L.DATA / "synthetic" / "synthetic.json").read_text())
    raw = json.loads((L.DATA / "synthetic" / "synthetic_raw.json").read_text())
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.2))
    a = ax[0]
    A = [0.0, 0.15, 0.3, 0.6, 1.0]
    rows = {r["a"]: r for r in syn["grid"] if r["kind"] == "sink" and r["b"] == 0.0}
    a.plot(A, [rows[x]["lam4.0"]["p_rank1"] for x in A], "o-", color=BLUE, label="P(judge rank 1)")
    a.plot(A, [rows[x]["lam4.0"]["support_rate"] for x in A], "s-", color="#0ca30c", label="P1 support rule")
    a.plot(A, [rows[x]["lam4.0"]["kill_rate"] for x in A], "^-", color=RED, label="P1 kill rule")
    a.axhline(1 / 7, color=GREY, lw=0.8, ls=":")
    a.set_xlabel("planted judge sink $a$ (Ising units)")
    a.set_ylabel("rate (100 worlds)")
    a.legend(fontsize=6.5, frameon=False)
    a = ax[1]
    for x, col in zip(A, ["#cde2fb", "#9ec5f4", "#6da7ec", "#2a78d6", "#184f95"]):
        rr = [r for r in raw if r["kind"] == "sink" and r["a"] == x and r["b"] == 0.0]
        u = [np.nanmean((np.array(r["rank"]["4.0"], float) - 1) / 6) for r in rr]
        a.hist(u, bins=np.linspace(0, 0.8, 25), histtype="step", color=col, lw=1.5, label=f"a = {x}")
    a.axvline(us_j.mean(), color=RED, lw=1.5)
    a.text(us_j.mean() + 0.01, a.get_ylim()[1] * 0.85, "observed", color=RED, fontsize=7)
    a.set_xlabel("judges' mean normalized rank $\\bar u$")
    a.set_ylabel("worlds")
    a.legend(fontsize=6, frameon=False, ncol=1)
    fig.tight_layout()
    fig.savefig(FIG / "synthetic.pdf")
    # per-period figure for G12
    pf = HERE.parent / "goalperiod-subhypotheses" / "G12" / "figures"
    pf.mkdir(parents=True, exist_ok=True)
    fig, a = plt.subplots(figsize=(3.4, 2.4))
    co = r12["P2"]["coef"]
    se = r12["P2"]["se_coef"]
    keys = ["R_ST_all", "R_OT_all", "R_JD_all", "R_DJ_all", "P_ST_all", "P_OT_all", "P_JD_all", "P_DJ_all"]
    labs = ["ST", "OT", "JD", "DJ", "ST$^P$", "OT$^P$", "JD$^P$", "DJ$^P$"]
    a.errorbar(range(len(keys)), [co[k] for k in keys], yerr=[1.96 * se[k] for k in keys], fmt="o",
               color=BLUE, ecolor=GREY)
    a.axhline(0, color=GREY, lw=0.8)
    a.set_xticks(range(len(keys)))
    a.set_xticklabels(labs, fontsize=7)
    a.set_ylabel("coupling J (Ising units)")
    a.set_title("pair-type couplings, 10 debates", fontsize=9)
    fig.tight_layout()
    fig.savefig(pf / "pairtype.pdf")


if __name__ == "__main__":
    main()
