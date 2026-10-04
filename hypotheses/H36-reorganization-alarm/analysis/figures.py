"""H36 figures: event-locked profiles, operating curves, timeline, synthetic AUCs, and the summary-page panel.

Usage: uv run python hypotheses/H36-reorganization-alarm/analysis/figures.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h36lib as L  # noqa: E402

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

C = {"Z_phys": "#2a78d6", "Z_cont": "#eb6834", "Z_act": "#1baf7a", "R1": "#eda100", "R2": "#e87ba4"}
MK = {"Z_phys": "o", "Z_cont": "s", "Z_act": "^", "R1": "D", "R2": "v"}
LAB = {"Z_phys": "physics alarm $Z_{\\rm phys}$", "Z_cont": "content members $Z_{\\rm cont}$",
       "Z_act": "activity members $Z_{\\rm act}$", "R1": "rival R1: centroid shift", "R2": "rival R2: activity level"}
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"
plt.rcParams.update({"font.size": 8, "axes.edgecolor": "#c9c7c0", "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": "white"})


def panel_profile(ax, R):
    P = R["profiles_goal"]
    offs = list(range(-3, 4))
    pv = P["Z_phys"]["placebo"]
    ax.axhspan(-1, 1, color="#f0efec", lw=0, zorder=0)
    ax.axhline(0, color="#c9c7c0", lw=0.8, zorder=1)
    ax.axhline(L.THRESH, color="#85847e", lw=1.0, ls="--", zorder=2)
    ax.text(-3.3, L.THRESH + 0.12, "alarm threshold 2.0", fontsize=6.5, color=INK2, va="bottom")
    for j, k in enumerate(["R1", "Z_cont", "Z_phys", "Z_act"]):
        m = np.array([P[k][str(o)][0] if P[k][str(o)][0] is not None else np.nan for o in offs])
        se = np.array([P[k][str(o)][1] if P[k][str(o)][1] is not None else np.nan for o in offs])
        x = np.array(offs) + (j - 1.5) * 0.08
        ax.errorbar(x, m, yerr=se, color=C[k], marker=MK[k], ms=4.5, lw=2, elinewidth=1, capsize=0, zorder=3,
                    mec="white", mew=0.8, label=LAB[k])
    ax.set_xticks(offs)
    ax.set_xticklabels([f"{o:+d}" if o else "0\nkickoff" for o in offs])
    ax.set_xlabel("active days from goal kickoff")
    ax.set_ylabel("mean trailing z (± s.e.), 33 kickoffs")
    ax.text(-3.3, -0.85, "placebo days: mean 0, sd ≈ 0.8 (band ±1)", fontsize=6.5, color=INK2)
    ax.set_xlim(-3.4, 3.9)
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.legend(fontsize=6.3, frameon=False, loc="upper right", bbox_to_anchor=(1.0, 1.02))


def panel_roc(ax, R, PH):
    S = R["sweep_goal"]
    for k in ["R1", "Z_cont", "Z_phys", "Z_act"]:
        far = [x["far_win"] for x in S[k]]; hit = [x["hit"] for x in S[k]]
        ax.plot(far, hit, color=C[k], lw=2, zorder=2)
        p = next(x for x in S[k] if abs(x["thr"] - 2.0) < 1e-9)
        ax.plot(p["far_win"], p["hit"], marker=MK[k], color=C[k], ms=6, mec="white", mew=0.9, zorder=4, ls="none")
    rule = next(r for r in PH["PH4_rules_in_sample"] if r["rule"].startswith("R1 >= 3.0 or"))
    ax.plot(rule["far_win"], rule["hit"], marker="*", ms=11, color=INK, mec="white", mew=0.6, zorder=5, ls="none")
    ax.annotate("post hoc rule\nR1≥3 or $Z_{\\rm cont}$≥2", (rule["far_win"], rule["hit"]), xytext=(0.12, 0.80),
                fontsize=6.3, color=INK, arrowprops=dict(arrowstyle="-", color=INK2, lw=0.6))
    ax.plot([0, 1], [0, 1], color="#c9c7c0", lw=0.8, ls=(0, (2, 2)), zorder=1)
    ax.set_xlim(-0.02, 0.62); ax.set_ylim(0, 1.0)
    ax.set_xlabel("false-alarm rate (3-day placebo windows)")
    ax.set_ylabel("hit rate (goal kickoffs, days −1..+1)")
    ax.text(0.33, 0.06, "markers: threshold 2.0", fontsize=6.3, color=INK2)
    for k, (x, y) in {"R1": (0.40, 0.73), "Z_cont": (0.045, 0.505), "Z_phys": (0.27, 0.42), "Z_act": (0.47, 0.36)}.items():
        ax.text(x, y, {"R1": "R1", "Z_cont": "$Z_{\\rm cont}$", "Z_phys": "$Z_{\\rm phys}$", "Z_act": "$Z_{\\rm act}$"}[k],
                fontsize=7, color=INK)
    ax.grid(color=GRID, lw=0.6)


def fig_summary(R, PH):
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.55), gridspec_kw=dict(width_ratios=[1.25, 1]))
    panel_profile(axs[0], R); panel_roc(axs[1], R, PH)
    axs[0].set_title("a  event-locked alarm scores", loc="left", fontsize=8, color=INK)
    axs[1].set_title("b  operating curves (threshold sweep)", loc="left", fontsize=8, color=INK)
    fig.tight_layout(pad=0.4)
    fig.savefig(L.FIG / "summary_obs.pdf"); plt.close(fig)


def fig_event_locked(R):
    fig, ax = plt.subplots(figsize=(4.6, 3.0)); panel_profile(ax, R); fig.tight_layout(); fig.savefig(L.FIG / "event_locked.pdf"); plt.close(fig)


def fig_roc(R, PH):
    fig, ax = plt.subplots(figsize=(3.8, 3.0)); panel_roc(ax, R, PH); fig.tight_layout(); fig.savefig(L.FIG / "roc_goal.pdf"); plt.close(fig)


def fig_timeline():
    s = pl.read_parquet(L.OUT / "scores.parquet").sort("aday")
    ev = pl.read_parquet(L.OUT / "events.parquet").filter(~pl.col("holdout0"))
    fig, axs = plt.subplots(2, 1, figsize=(7.4, 3.6), sharex=True)
    x = s["aday"].to_numpy()
    for ax, k in zip(axs, ["Z_phys", "Z_cont"]):
        y = s[k].to_numpy().astype(float).copy()
        brk = np.r_[False, np.diff(x) > 1]  # break the line across held-out gaps
        xx = np.insert(x.astype(float), np.flatnonzero(brk), np.nan); y = np.insert(y, np.flatnonzero(brk), np.nan)
        ax.axhline(L.THRESH, color=INK2, lw=0.7, ls=(0, (3, 2)))
        ax.plot(xx, y, color=C[k], lw=0.9, marker=MK[k], ms=2.2)
        for cls, col_ in [("goal", "#85847e"), ("room", "#4a3aa7"), ("scaffold", "#e34948"), ("roster", "#008300")]:
            for a in ev.filter(pl.col("cls") == cls)["aday0"].drop_nulls().to_list():
                ax.axvline(a, color=col_, lw=0.6 if cls == "goal" else 1.0, alpha=0.6, zorder=0)
        ax.set_ylabel(LAB[k], fontsize=7)
        ax.grid(axis="y", color=GRID, lw=0.5)
        ax.set_ylim(-4, 9)
    axs[1].set_xlabel("calendar active-day index (held-out days absent)")
    axs[0].set_title("Daily alarm scores; vertical lines: goal kickoffs (gray), room (violet), scaffold (red), roster (green)",
                     fontsize=7, loc="left")
    fig.tight_layout(); fig.savefig(L.FIG / "timeline.pdf"); plt.close(fig)


def fig_synthetic():
    S = json.loads((L.OUT / "synthetic" / "summary.json").read_text())
    scen = ["S0", "S1", "S8", "S2", "S3", "S4", "S5", "S6", "S7"]
    names = ["nothing", "coupling\n↑ big", "coupling\n↑ moderate", "coupling\n↓", "field step\n(day edge)", "content goal\nswitch",
             "mid-day\nfield step", "content\ncoupling ↑", "stalls"]
    fig, ax = plt.subplots(figsize=(7.2, 2.6))
    ks = ["Z_phys", "Z_act", "Z_cont", "R1", "R2"]
    w = 0.16
    for j, k in enumerate(ks):
        v = [S[s_]["scores"][k]["auc"] for s_ in scen]
        ax.bar(np.arange(len(scen)) + (j - 2) * w, v, width=w * 0.88, color=C[k], label=LAB[k])
    ax.axhline(0.5, color=INK2, lw=0.7, ls=(0, (3, 2)))
    ax.set_xticks(np.arange(len(scen))); ax.set_xticklabels(names, fontsize=6.5)
    ax.set_ylabel("AUC (switch window vs placebo)"); ax.set_ylim(0.3, 1.14)
    ax.legend(fontsize=6, frameon=False, ncol=5, loc="upper left", bbox_to_anchor=(0, 1.02))
    ax.grid(axis="y", color=GRID, lw=0.5)
    fig.tight_layout(); fig.savefig(L.FIG / "synthetic.pdf"); plt.close(fig)


def fig_synthetic_col():
    """Column-width synthetic panel for the summary page 2."""
    S = json.loads((L.OUT / "synthetic" / "summary.json").read_text())
    scen = ["S0", "S1", "S8", "S3", "S4", "S5", "S6", "S7"]
    names = ["none", "J↑", "J↑ mod.", "h step", "goal\nswitch", "mid-day\nh step", "content\nJ↑", "stalls"]
    fig, ax = plt.subplots(figsize=(3.45, 1.95))
    ks = ["Z_phys", "Z_act", "Z_cont", "R1"]
    w = 0.2
    for j, k in enumerate(ks):
        v = [S[s_]["scores"][k]["auc"] for s_ in scen]
        ax.bar(np.arange(len(scen)) + (j - 1.5) * w, v, width=w * 0.86, color=C[k],
               label={"Z_phys": "$Z_{\\rm phys}$", "Z_act": "$Z_{\\rm act}$", "Z_cont": "$Z_{\\rm cont}$", "R1": "R1"}[k])
    ax.axhline(0.5, color=INK2, lw=0.7, ls="--")
    ax.set_xticks(np.arange(len(scen))); ax.set_xticklabels(names, fontsize=5.8)
    ax.set_ylabel("AUC", fontsize=7); ax.set_ylim(0.3, 1.16); ax.tick_params(labelsize=6)
    ax.legend(fontsize=5.8, frameon=False, ncol=4, loc="upper left", bbox_to_anchor=(0, 1.04), handlelength=1.2, columnspacing=0.8)
    ax.grid(axis="y", color=GRID, lw=0.5)
    fig.tight_layout(pad=0.3); fig.savefig(L.FIG / "synthetic_col.pdf"); plt.close(fig)


def main():
    L.FIG.mkdir(parents=True, exist_ok=True)
    R = json.loads((L.OUT / "results.json").read_text())
    PH = json.loads((L.OUT / "posthoc.json").read_text())
    fig_summary(R, PH); fig_event_locked(R); fig_roc(R, PH); fig_timeline(); fig_synthetic(); fig_synthetic_col()
    print("figures written to", L.FIG)


if __name__ == "__main__":
    main()
