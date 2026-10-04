"""H45 figures. Usage: uv run python hypotheses/H45-context-homeostasis/analysis/figures.py [synthetic|summary|all]"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import h45lib as L  # noqa: E402

FIG = L.ROOT / "hypotheses/H45-context-homeostasis/figures"
BLUE, ORANGE, AQUA, GRAY, INK, MUTED = "#2a78d6", "#eb6834", "#1baf7a", "#8a8984", "#0b0b0b", "#52514e"
CLS_COL = {"controller": BLUE, "passive": GRAY, "scaffold": ORANGE, "competition": AQUA}
REG_COL = {"I": GRAY, "II": AQUA, "III": BLUE}
plt.rcParams.update({"font.size": 7, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED, "axes.linewidth": 0.6,
                     "xtick.major.width": 0.6, "ytick.major.width": 0.6, "legend.frameon": False})


def fig_synthetic():
    runs = json.loads((L.DATA / "synthetic" / "synthetic_runs.json").read_text())["runs"]
    cvc = json.loads((L.DATA / "synthetic" / "synthetic_cvcheck.json").read_text())
    classes = ["controller", "passive", "scaffold", "competition"]
    stats = [("RI", "regulation index RI", None), ("overshoot", "talk overshoot\nafter forced reset", 1.0),
             ("g_W", r"$\gamma_W$ (own content)", 0.0), ("pgrowth", "P growth\n(j30–35 / j8–12)", 1.0)]
    fig, axes = plt.subplots(1, 4, figsize=(6.8, 1.9))
    rng = np.random.default_rng(0)
    for ax, (k, lab, ref) in zip(axes, stats):
        for i, cl in enumerate(classes):
            v = np.array([r[k] for r in runs if r["cls"] == cl and r.get(k) is not None], float)
            v = v[np.isfinite(v)]
            ax.scatter(i + rng.uniform(-0.18, 0.18, len(v)), v, s=4, color=CLS_COL[cl], alpha=0.45, lw=0)
            ax.plot([i - 0.28, i + 0.28], [np.median(v)] * 2, color=INK, lw=1.2)
        if ref is not None:
            ax.axhline(ref, color=GRAY, lw=0.6, ls="--", zorder=0)
        if k == "RI":
            ax.axhline(0, color=GRAY, lw=0.6, ls="--", zorder=0)
        ax.set_xticks(range(4), ["contr.", "passive", "scaff.", "comp."], rotation=0)
        ax.set_title(lab, fontsize=7, color=INK)
    fig.tight_layout(w_pad=0.8)
    fig.savefig(FIG / "synthetic.pdf")
    plt.close(fig)


def load_rep() -> dict:
    return json.loads((L.DATA / "replication.json").read_text())


def fig_summary_obs():
    """Page-1 figure (column width, <= 1.7 in tall): (a) RI per period with CI vs passive (0), the synthetic controller
    and the P1 threshold; (b) NE41: k-adjusted talk propensity and reply share after forced resets."""
    rep = load_rep()
    syn = json.loads((L.DATA / "synthetic" / "synthetic_runs.json").read_text())["runs"]
    ctrl = float(np.median([r["RI"] for r in syn if r["cls"] == "controller"]))
    ne41 = json.loads((L.DATA / "NE41" / "native.json").read_text())
    fig, (a, b) = plt.subplots(1, 2, figsize=(3.45, 1.65), gridspec_kw={"width_ratios": [1.45, 1]})
    ps = sorted(rep.values(), key=lambda r: r["goal_no"])
    for i, r in enumerate(ps):
        reg = r["regulation"]
        rg = "III" if "III" in r["regime"] else ("II" if "II" in r["regime"].split(",") else "I")
        a.plot([i, i], reg["RI_ci"], color=REG_COL[rg], lw=0.8)
        a.scatter([i], [reg["RI"]], s=5, color=REG_COL[rg], zorder=3, lw=0)
    a.axhline(0, color=GRAY, lw=0.6, ls="--")
    a.axhline(ctrl, color=BLUE, lw=0.6, ls=":")
    a.axhline(0.5, color=MUTED, lw=0.5, alpha=0.5)
    a.text(0, ctrl + 0.03, "synthetic controller", color=BLUE, fontsize=5)
    a.text(0, 0.53, "P1 threshold", color=MUTED, fontsize=5)
    a.text(0, -0.17, "passive = 0", color=GRAY, fontsize=5)
    ticks = [i for i, r in enumerate(ps) if r["goal_no"] in (4, 13, 21, 27, 33, 38, 51)]
    a.set_xticks(ticks, [f"#{ps[i]['goal_no']}" for i in ticks], fontsize=5)
    a.set_ylim(-0.2, 0.65)
    a.set_ylabel("regulation index RI", fontsize=6)
    a.set_title("(a) room share vs inflow, 32 periods", fontsize=6, loc="left")
    a.tick_params(labelsize=5)
    for key, col, lab in (("forced_talk", BLUE, "talk"), ("forced_E1", ORANGE, "reply share")):
        r = ne41[key]
        d = np.array(r["delta"])
        b.plot(np.arange(1, len(d) + 1), (r["baseline"] + d) / r["baseline"], color=col, lw=1.2, label=lab)
    b.axhline(1, color=GRAY, lw=0.6, ls="--")
    b.set_xlabel("calls after a forced erasure", fontsize=6)
    b.set_ylabel("ratio to j 20–40", fontsize=6)
    b.set_title("(b) NE41, k-adjusted", fontsize=6, loc="left")
    b.legend(fontsize=5, loc="upper right", handlelength=1.2)
    b.tick_params(labelsize=5)
    fig.tight_layout(pad=0.3, w_pad=0.6)
    fig.savefig(FIG / "summary_obs.pdf")
    plt.close(fig)


def fig_summary_obs2():
    """Page-2 figure (column width, <= 2.1 in tall): synthetic classes on real schedules with the real-data value overlaid:
    (a) RI (real: the 32 period estimates), (b) k-adjusted talk ratio after forced resets (real: NE41 pooled + periods)."""
    syn = json.loads((L.DATA / "synthetic" / "synthetic_runs.json").read_text())["runs"]
    rep = load_rep()
    ne41 = json.loads((L.DATA / "NE41" / "native.json").read_text())
    classes = ["controller", "passive", "scaffold", "competition"]
    labels = ["contr.", "passive", "scaff.", "comp.", "village"]
    fig, axes = plt.subplots(1, 2, figsize=(3.45, 1.95))
    rng = np.random.default_rng(0)
    real = {"RI": [r["regulation"]["RI"] for r in rep.values()],
            "overshoot": [v["overshoot"] for v in ne41["per_period"].values()]}
    pooled = {"RI": None, "overshoot": ne41["forced_talk"]["overshoot"]}
    for ax, (k, ttl, ref) in zip(axes, (("RI", "(a) regulation index", 0.0), ("overshoot", "(b) talk after forced reset", 1.0))):
        for i, cl in enumerate(classes):
            v = np.array([r[k] for r in syn if r["cls"] == cl and r.get(k) is not None], float)
            v = v[np.isfinite(v)]
            ax.scatter(i + rng.uniform(-0.2, 0.2, len(v)), v, s=3, color=CLS_COL[cl], alpha=0.4, lw=0)
            ax.plot([i - 0.3, i + 0.3], [np.median(v)] * 2, color=INK, lw=1.0)
        rv = np.array(real[k], float)
        ax.scatter(4 + rng.uniform(-0.2, 0.2, len(rv)), rv, s=7, color=INK, marker="D", lw=0, alpha=0.8)
        if pooled[k] is not None:
            ax.plot([3.7, 4.3], [pooled[k]] * 2, color=ORANGE, lw=1.4)
        ax.axhline(ref, color=GRAY, lw=0.6, ls="--", zorder=0)
        ax.set_xticks(range(5), labels, fontsize=5)
        ax.tick_params(labelsize=5)
        ax.set_title(ttl, fontsize=6, loc="left")
    axes[0].set_ylabel("synthetic (20 reps × 6 units) and real", fontsize=5)
    fig.tight_layout(pad=0.3, w_pad=0.6)
    fig.savefig(FIG / "summary_obs2.pdf")
    plt.close(fig)


def fig_setpoints():
    """Cross-period: agent-period set point s* vs inflow per call lambda (log-log), regime colors; NE42 and G51 inset
    numbers in the card."""
    rep = load_rep()
    fig, ax = plt.subplots(figsize=(3.4, 2.4))
    for r in rep.values():
        rg = "III" if "III" in r["regime"] else ("II" if "II" in r["regime"].split(",") else "I")
        for a in r["set_points"]["by_agent"]:
            if a["s_star"] and a["lam_med"] and a["s_star"] > 0 and a["lam_med"] > 0:
                ax.scatter(a["lam_med"], a["s_star"], s=4, color=REG_COL[rg], alpha=0.5, lw=0)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel(r"inflow per call $\lambda$ (room tokens)")
    ax.set_ylabel(r"set point $s^*$ (median share, j 15–35)")
    fig.tight_layout()
    fig.savefig(FIG / "setpoints.pdf")
    plt.close(fig)


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    FIG.mkdir(exist_ok=True)
    if what in ("synthetic", "all"):
        fig_synthetic()
    if what in ("summary", "all"):
        fig_summary_obs()
        fig_summary_obs2()
        fig_setpoints()
