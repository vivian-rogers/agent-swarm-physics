"""H44 figures: per-period event-study curves, cross-period summary (Theta_c / Omega / sigma forest), the summary-page
observable, and the synthetic validation.

Usage: uv run python hypotheses/H44-erasure-reacquisition-thrash/analysis/figures.py
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
COL = {"forced": "#2a78d6", "voluntary": "#e08a1e", "pseudo21": "#85847e", "pseudo31": "#85847e"}
plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.6,
                     "xtick.major.width": 0.6, "ytick.major.width": 0.6, "legend.frameon": False})


def load(per):
    return json.loads((C.OUT / per / "results.json").read_text())


def per_period_curves(per: str, r: dict):
    d = C.HYP / "goalperiod-subhypotheses" / per / "figures"
    d.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(1, 4, figsize=(9, 2.3))
    for kind in ("forced", "voluntary", "pseudo21"):
        cv = r["curves"].get(kind)
        if not cv:
            continue
        k = np.array(cv["k"])
        for i, (name, lab) in enumerate((("R_nw", "re-acquisition share (non-write)"), ("W", "write share"),
                                         ("work", "work commits / call"), ("talk", "talk share"))):
            y = np.array(cv[name]["est"]); lo = np.array(cv[name]["lo"]); hi = np.array(cv[name]["hi"])
            ax[i].plot(k, y, color=COL[kind], lw=1, label=kind if i == 0 else None)
            ax[i].fill_between(k, lo, hi, color=COL[kind], alpha=0.15, lw=0)
            ax[i].set_title(lab, fontsize=8)
            ax[i].axvline(0, color="k", lw=0.5, ls=":")
            ax[i].set_xlabel("calls from reset")
    ax[0].legend(fontsize=6)
    fig.suptitle(f"H44 x {per}: event study around resets (pseudo21 = no reset, boundary at call 21)", fontsize=8)
    fig.tight_layout()
    fig.savefig(d / "event_study.pdf")
    plt.close(fig)


def forest(results: dict, ne: dict):
    fig, ax = plt.subplots(1, 4, figsize=(9, 2.8), sharey=True)
    ys = np.arange(len(PERIODS))[::-1]
    for i, (stat, tag, lab) in enumerate((("Theta_c", "post5_vs_far", r"$\Theta_c$ (re-acq. | agent, prev)"),
                                          ("dR", "post5_vs_far", r"$\Delta R$ (raw re-acq.)"),
                                          ("Omega", "post10_vs_far", r"$\Omega$ (write dip)"),
                                          ("d_sigma", "post5_vs_far", r"$\Delta\sigma$ (switching)"))):
        for j, (kind, off) in enumerate((("forced", 0.15), ("voluntary", -0.05), ("pseudo31", -0.25))):
            for y, per in zip(ys, PERIODS):
                c = results[per]["stats"].get(kind, {}).get("contrasts", {}).get(tag, {}).get(stat)
                if not c:
                    continue
                ax[i].errorbar(c[0], y + off, xerr=[[c[0] - c[1]], [c[2] - c[0]]], fmt="o", ms=2.5, color=COL[kind],
                               lw=0.8, label=kind if (y == ys[0] and i == 0) else None)
            pk = ne["pooled"].get(f"{kind}:{tag}:{stat}")
            if pk and np.isfinite(pk["est"]):
                ax[i].errorbar(pk["est"], -1.2 + off, xerr=[[pk["est"] - pk["lo"]], [pk["hi"] - pk["est"]]], fmt="D",
                               ms=3, color=COL[kind], lw=1)
        ax[i].axvline(0, color="k", lw=0.5)
        ax[i].set_title(lab, fontsize=8)
    ax[0].set_yticks(list(ys) + [-1.2]); ax[0].set_yticklabels(PERIODS + ["pooled (RE)"])
    ax[0].legend(fontsize=6, loc="lower left")
    fig.tight_layout()
    fig.savefig(C.FIG / "forest.pdf")
    plt.close(fig)


def summary_obs(results: dict, ne: dict):
    """Summary page figure: (a) G51 curves of the re-acquisition share among non-write calls and the write share,
    forced vs voluntary vs no reset; (b) per-period Theta_c vs Omega (forced, voluntary, pseudo)."""
    r = results["G51"]
    fig, ax = plt.subplots(1, 2, figsize=(4.4, 2.0), gridspec_kw={"width_ratios": [1.3, 1]})
    a2 = ax[0].twinx()
    for kind in ("forced", "voluntary", "pseudo21"):
        cv = r["curves"][kind]
        k = np.array(cv["k"])
        ax[0].plot(k, cv["R_nw"]["est"], color=COL[kind], lw=1, label={"forced": "forced", "voluntary": "voluntary",
                                                                        "pseudo21": "no reset"}[kind])
        a2.plot(k, cv["W"]["est"], color=COL[kind], lw=0.8, ls="--")
    ax[0].axvline(0, color="k", lw=0.5, ls=":")
    ax[0].set_xlabel("calls from reset (G51)", fontsize=7)
    ax[0].set_ylabel("re-acquisition share\n(non-write calls), solid", fontsize=6.5)
    a2.set_ylabel("write share, dashed", fontsize=6.5)
    a2.spines["right"].set_visible(True)
    ax[0].legend(fontsize=5.5, loc="upper right")
    ax[0].set_title("(a)", fontsize=7, loc="left")
    for kind, mk in (("forced", "o"), ("voluntary", "s"), ("pseudo31", "x")):
        xs, ys = [], []
        for per in PERIODS:
            st = results[per]["stats"].get(kind)
            if not st:
                continue
            xs.append(st["contrasts"]["post5_vs_far"]["Theta_c"][0]); ys.append(st["contrasts"]["post10_vs_far"]["Omega"][0])
        ax[1].scatter(xs, ys, s=10, marker=mk, color=COL[kind], label={"pseudo31": "no reset"}.get(kind, kind), lw=0.8)
    ax[1].axhline(0, color="k", lw=0.5); ax[1].axvline(0, color="k", lw=0.5)
    ax[1].set_xlabel(r"$\Theta_c$ (re-acquisition rise)", fontsize=7)
    ax[1].set_ylabel(r"$\Omega$ (write dip)", fontsize=7)
    ax[1].legend(fontsize=5.5)
    ax[1].set_title("(b) 9 periods", fontsize=7, loc="left")
    for a in (ax[0], a2, ax[1]):
        a.tick_params(labelsize=6)
    fig.tight_layout(pad=0.3)
    fig.savefig(C.FIG / "summary_obs.pdf")
    plt.close(fig)


def synthetic_fig():
    s = json.loads((C.OUT / "synthetic" / "synthetic.json").read_text())
    fig, ax = plt.subplots(1, 2, figsize=(4.4, 1.9))
    col = {"thrash": "#2a78d6", "dip": "#d03b3b", "none": "#85847e"}
    for i, per in enumerate(("G51", "G37")):
        P = s["periods"].get(per)
        if not P:
            continue
        for w, v in P["worlds"].items():
            th = [x["forced"]["Theta_c"][0] for x in v["reps"]]
            om = [x["forced"]["Omega"][0] for x in v["reps"]]
            ax[i].scatter(th, om, s=7, color=col[w], label=f"{w} ({100 * v['accuracy']:.0f}%)", lw=0)
        ax[i].axvline(0.01, color="k", lw=0.5, ls=":")
        ax[i].axhline(0, color="k", lw=0.5)
        ax[i].set_title(f"{per}: {P['n_forced']} forced resets", fontsize=7)
        ax[i].set_xlabel(r"$\Theta_c$", fontsize=7)
        ax[i].tick_params(labelsize=6)
        ax[i].legend(fontsize=5.5, title="planted (accuracy)", title_fontsize=5.5)
    ax[0].set_ylabel(r"$\Omega$", fontsize=7)
    fig.tight_layout(pad=0.3)
    fig.savefig(C.FIG / "synthetic_validation.pdf")
    plt.close(fig)


def main():
    results = {p: load(p) for p in PERIODS}
    ne = json.loads((C.OUT / "NE41" / "results.json").read_text())
    for p, r in results.items():
        per_period_curves(p, r)
    forest(results, ne)
    summary_obs(results, ne)
    synthetic_fig()
    print("figures written")


if __name__ == "__main__":
    main()
