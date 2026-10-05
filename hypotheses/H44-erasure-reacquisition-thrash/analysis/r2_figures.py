"""H44 round-2 figures: figures/summary_r2.pdf (sawtooth, cap curve, reference sensitivity, R1/R3/R4 forest) and
per-period goalperiod-subhypotheses/G<NN>/figures/r2_sawtooth.pdf.

Usage: uv run python hypotheses/H44-erasure-reacquisition-thrash/analysis/r2_figures.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from h44lib import C  # noqa: E402

PERIODS = ["G36", "G37", "G38", "G39", "G40", "G41", "G42", "G44", "G51"]
BLUE, ORANGE, GREY, GOOD, BAD = "#2a78d6", "#e08a1e", "#85847e", "#0ca30c", "#d03b3b"
plt.rcParams.update({"font.size": 7.5, "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.6,
                     "xtick.major.width": 0.6, "ytick.major.width": 0.6, "legend.frameon": False})
R2D = C.OUT / "r2"


def model_curve(par, kmax=40):
    x = np.arange(kmax, dtype=float)
    g = lambda k_: par[k_][0] if isinstance(par.get(k_), list) else (par.get(k_) or 0.0)
    return g("c") + g("beta") * x + g("A1") * np.exp(-x / g("l1")) + g("A2") * np.exp(-x / max(g("l2"), 1e-6))


def per_period(per, r):
    d = C.HYP / "goalperiod-subhypotheses" / per / "figures"
    d.mkdir(parents=True, exist_ok=True)
    a = r["r2"]
    k = np.arange(1, 41)
    fig, ax = plt.subplots(1, 4, figsize=(9, 2.2))
    for i, (ykey, par, lab) in enumerate((("W_fit", "W_par", "write share W(k)"), ("R_fit", "R_par", "re-acquisition share R(k)"))):
        y = np.array(a[ykey]["y"])
        ax[i].plot(k, y, "o", ms=2, color=BLUE)
        ax[i].plot(k, model_curve(a[par]), color="k", lw=0.8)
        ax[i].set_title(lab, fontsize=7.5); ax[i].set_xlabel("call k in a 40-call segment")
    ax[2].plot(k, a["loop_curve"], color=GREY); ax[2].set_title("in-loop share", fontsize=7.5); ax[2].set_xlabel("k")
    Y = np.array(a["cap"]["Y"]); ax[3].plot(k[4:], Y[4:] / Y[-1], color=BLUE)
    ax[3].axhline(1, color=GREY, lw=0.5, ls=":"); ax[3].set_title("output per call at cap L / cap 40", fontsize=7.5)
    ax[3].set_xlabel("cap L (calls)")
    fig.suptitle(f"H44 x {per}, round 2: complete forced sawtooths (n = {a['n_segments']}); line = two-timescale fit",
                 fontsize=7.5)
    fig.tight_layout(); fig.savefig(d / "r2_sawtooth.pdf"); plt.close(fig)


def summary(results, pooled, r1):
    fig, ax = plt.subplots(2, 2, figsize=(7.0, 4.6))
    a = results["G51"]["r2"]
    k = np.arange(1, 41)
    # (a) G51 sawtooth: W and R with fits
    ax0 = ax[0, 0]
    yW = np.array(a["W_fit"]["y"]); yR = np.array(a["R_fit"]["y"])
    ax0.plot(k, yR, "o", ms=2, color=ORANGE, label="re-acquisition R(k)")
    ax0.plot(k, model_curve(a["R_par"]), color=ORANGE, lw=0.8)
    ax0.plot(k, yW, "o", ms=2, color=BLUE, label="writes W(k)")
    ax0.plot(k, model_curve(a["W_par"]), color=BLUE, lw=0.8)
    ax0.set_xlabel("call k after a forced reset (40-call segment)"); ax0.set_ylabel("share of calls")
    ax0.set_title("(a) G51 sawtooth, 8,842 complete segments", fontsize=7.5, loc="left")
    ax0.legend(fontsize=6.5, loc="center right")
    # (b) cap curves
    ax1 = ax[0, 1]
    for per in PERIODS:
        Y = np.array(results[per]["r2"]["cap"]["Y"])
        ax1.plot(k[4:], Y[4:] / Y[-1], color=BLUE if per == "G51" else GREY, lw=1.2 if per == "G51" else 0.6,
                 alpha=1 if per == "G51" else 0.7)
    ax1.axhline(1, color="k", lw=0.5, ls=":")
    p = pooled["r2_Y20_over_Y40"]
    ax1.errorbar([20], [p["est"]], yerr=[[p["est"] - p["lo"]], [p["hi"] - p["est"]]], fmt="D", ms=3, color="k")
    ax1.set_xlabel("cap L (calls per segment)"); ax1.set_ylabel("output per call, relative to cap 40")
    ax1.set_title("(b) shorter caps lose output (G51 blue)", fontsize=7.5, loc="left")
    # (c) reference sensitivity
    ax2 = ax[1, 0]
    refs = ["far", "near", "whole", "steady", "sawtooth"]
    labs = ["-20..-11", "-10..-1", "-40..-1", "steady\n(pos 11-30)", "cycle\nmean"]
    for i, ref in enumerate(refs):
        vals = [results[per]["refs"]["refs"][ref]["Omega"][0] for per in PERIODS]
        ax2.plot(np.full(len(vals), i) + np.linspace(-0.15, 0.15, len(vals)), vals, "o", ms=2, color=GREY)
        q = pooled[f"Omega_{ref}"]
        ax2.errorbar([i + 0.28], [q["est"]], yerr=[[q["est"] - q["lo"]], [q["hi"] - q["est"]]], fmt="D", ms=3, color="k")
    ax2.axhline(0, color="k", lw=0.5, ls=":")
    ax2.set_xticks(range(len(refs))); ax2.set_xticklabels(labs, fontsize=6.5)
    ax2.set_ylabel(r"write dip $\Omega$ (+1..+10)")
    ax2.set_title("(c) the dip depends on the reference window", fontsize=7.5, loc="left")
    # (d) forest: R1, R3, R4 pooled
    ax3 = ax[1, 1]
    rows = [(r"$\Theta_c$ checked labels", r1["pooled_checked"], GOOD),
            (r"$\Theta_c$ checked, mid-segment rates", r1["pooled_checked_midq"], GOOD),
            ("R3 re-open excess vs no reset", pooled["r3_excess_FP_paths"], GREY),
            ("R3 re-open excess vs voluntary", pooled["r3_excess_FV_paths"], GOOD),
            ("R4 reset effect, looping (writes/call)", pooled["r4_E_loop"], BAD),
            ("R4 reset effect, loop-free", pooled["r4_E_free"], BAD),
            ("R4 looping minus loop-free", pooled["r4_DDD"], GREY)]
    for i, (lab, q, col) in enumerate(rows[::-1]):
        ax3.errorbar([q["est"]], [i], xerr=[[q["est"] - q["lo"]], [q["hi"] - q["est"]]], fmt="o", ms=3, color=col)
    ax3.axvline(0, color="k", lw=0.5, ls=":")
    ax3.set_yticks(range(len(rows))); ax3.set_yticklabels([r_[0] for r_ in rows[::-1]], fontsize=6.3)
    ax3.set_xlim(-0.17, 0.14)
    ax3.set_xlabel("pooled estimate (random effects, 95% CI)")
    ax3.set_title("(d) classifier check, re-reading, loop lever", fontsize=7.5, loc="left")
    fig.tight_layout()
    fig.savefig(C.FIG / "summary_r2.pdf"); plt.close(fig)


def main():
    results = {per: json.loads((R2D / per / "r2_results.json").read_text()) for per in PERIODS}
    pooled = json.loads((R2D / "pooled.json").read_text())
    r1 = json.loads((R2D / "r1_check.json").read_text())
    for per, r in results.items():
        per_period(per, r)
    summary(results, pooled, r1)
    C.log("figures done")


if __name__ == "__main__":
    main()
