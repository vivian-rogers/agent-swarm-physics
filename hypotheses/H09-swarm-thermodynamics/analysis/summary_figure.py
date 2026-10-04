"""Two-panel observables figure for the H09 one-page summary (no new analysis).

Reads data/processed/H09-swarm-thermodynamics/explore_e6_idle_traps.json (E6, exploratory, non-holdout) and writes
figures/summary_obs.pdf:
  (a) escape hazard ratio of idle spells: minutes with a kick in the prior 60 s vs. minutes without (Mantel-Haenszel,
      stratified by elapsed dwell and time of day), by kick type and regime, with the day-swap null's 95th percentile;
  (b) escape rate per idle minute vs. kick rate (agent-day deciles): Kramers-like rise in regime I, none in III.
Usage: uv run python hypotheses/H09-swarm-thermodynamics/analysis/summary_figure.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data/processed/H09-swarm-thermodynamics/explore_e6_idle_traps.json"
OUT = Path(__file__).resolve().parents[1] / "figures/summary_obs.pdf"
COL = {"I": "#2a78d6", "III": "#eb6834"}
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({"font.size": 7, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False})
KICKS = [("any", "any room msg"), ("mention", "@-mention"), ("nudger_msg", "nudger"), ("human_msg", "human")]


def main():
    d = json.loads(DATA.read_text())["E6c_kicks"]
    fig, (a, b) = plt.subplots(1, 2, figsize=(4.3, 2.6), gridspec_kw={"width_ratios": [1.15, 1]})

    # (a) hazard ratios, log scale
    for i, (k, lab) in enumerate(KICKS):
        for reg, off in (("I", 0.17), ("III", -0.17)):
            q = d[reg][k]
            y = len(KICKS) - 1 - i + off
            hr = q["tau60"]["rr_mh"]
            ci = q.get("ci95_bootstrap_agentday")
            if ci:
                a.plot(ci, [y, y], color=COL[reg], lw=1.5, solid_capstyle="butt")
            a.plot(hr, y, "o", color=COL[reg], ms=4.5, mec="white", mew=0.7, zorder=3,
                   label=f"regime {reg}" if i == 0 else None)
            p95 = q["null_dayswap_tau60"]["p95"]
            a.plot([p95, p95], [y - 0.12, y + 0.12], color=INK2, lw=1.0)
    a.axvline(1, color=INK2, lw=0.6, ls=":")
    a.set_xscale("log")
    a.set_xticks([0.8, 1, 1.5, 2, 3])
    a.set_xticklabels(["0.8", "1", "1.5", "2", "3"])
    a.minorticks_off()
    a.set_xlim(0.75, 3.8)
    a.set_yticks(range(len(KICKS)))
    a.set_yticklabels([lab for _, lab in KICKS][::-1], fontsize=6.3)
    a.set_xlabel("escape hazard ratio (kick in prior 60 s)", fontsize=6.5)
    a.legend(fontsize=5.8, frameon=False, loc="lower right", handlelength=0.8)
    a.text(0.98, 0.985, "| = day-swap null p95", transform=a.transAxes, ha="right", va="top", fontsize=5.6,
           color=INK2)
    a.set_title("(a) Kicks end idling in regime I;\nin III only @-mentions do", fontsize=6.8, loc="left", color=INK)

    # (b) escape rate vs kick rate, agent-day deciles
    for reg in ("I", "III"):
        k = d[reg]["kramers_agentday"]
        r = np.array([c["r_mid"] for c in k["curve"]])
        e = np.array([c["k"] for c in k["curve"]])
        b.plot(r, e, "o-", color=COL[reg], ms=3.2, lw=1.2, mec="white", mew=0.5)
        xx = np.linspace(r.min(), r.max(), 20)
        b.plot(xx, k["k0_per_min"] + k["c_per_kick"] * xx, color=COL[reg], lw=0.8, ls="--")
        b.text(r[-1] + 0.1, e[-1], f"{reg}\nρ={k['spearman_r_k']:+.2f}", fontsize=5.8, color=INK, va="center")
    b.set_xlim(0, 5.4)
    b.set_ylim(0, 1.0)
    b.set_xlabel("room messages per idle minute", fontsize=6.5)
    b.set_ylabel("escapes per idle minute", fontsize=6.5)
    b.set_title("(b) Kramers-like k = k₀ + c·r:\nrises in I, not in III", fontsize=6.8, loc="left", color=INK)
    for ax in (a, b):
        ax.tick_params(axis="both", length=2, labelsize=6)
    fig.tight_layout(pad=0.3, w_pad=0.8)
    fig.savefig(OUT)
    plt.close(fig)
    print("wrote", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
