"""H96 figures: figures/summary_obs.pdf (old-state persistence at switches vs ordinary nights; order vs switching
time) and figures/summary_synthetic.pdf (why tau_old fails the order test and tau_sw does not)."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
H = HERE.parent
DATA = H.parents[1] / "data/processed/H96-goal-switch-hysteresis"
FIG = H / "figures"
C = {"I": "#2a78d6", "III": "#1baf7a", "gte": "#eb6834", "ink": "#3d3d3a", "grid": "#d9d8d2", "band": "#ecebe6"}
plt.rcParams.update({"font.size": 7.5, "axes.edgecolor": C["ink"], "axes.labelcolor": C["ink"],
                     "xtick.color": C["ink"], "ytick.color": C["ink"], "axes.spines.top": False,
                     "axes.spines.right": False, "legend.frameon": False})


def main():
    FIG.mkdir(exist_ok=True)
    tb = json.loads((DATA / "results/transitions_bge_small_style_resid32.json").read_text())
    tg = {o["P"]: o for o in json.loads((DATA / "results/transitions_gte_modernbert_style_resid32.json").read_text())}
    ps = json.loads((DATA / "results/pseudo_bge_small_style_resid32.json").read_text())["reference"]
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.0, 2.4), gridspec_kw={"width_ratios": [2.0, 1]})
    for reg, x0, x1 in (("I", -0.5, 17.5), ("III", 17.5, 23.5)):
        a.fill_between([x0, x1], ps[reg]["p10"], ps[reg]["p90"], color=C["band"], zorder=0, lw=0)
        a.plot([x0, x1], [ps[reg]["median"]] * 2, color=C["ink"], lw=0.8, ls="--", zorder=1)
    for i, o in enumerate(tb):
        s = o["state"]
        a.plot([i - 0.12] * 2, [s["R1"]["lo"], s["R1"]["hi"]], color=C[o["regime"]], lw=1.1)
        a.plot(i - 0.12, s["R1"]["est"], "o", ms=3, color=C[o["regime"]])
        g = tg[o["P"]]["state"]
        a.plot(i + 0.12, g["R1"]["est"], "D", ms=2.6, mfc="white", mec=C["gte"], mew=0.9)
    a.axhline(0, color=C["grid"], lw=0.8, zorder=0)
    a.set_xticks(range(len(tb)))
    a.set_xticklabels([f"{o['P']}" for o in tb], fontsize=6)
    a.set_xlabel("new period P (transition P−1 → P)")
    a.set_ylabel("R₁ = old-state excess day 1 / pre day")
    a.set_ylim(-0.6, 1.6)
    a.text(0.01, 0.97, "(a)  dots: bge (CI); diamonds: gte; band: ordinary nights p10–p90", transform=a.transAxes,
           va="top", fontsize=6.5)
    for o in tb:
        s = o["state"]
        if s["M_pre"]["lo"] > 0 and np.isfinite(s["tau_sw"]["est"]) and s["tau_sw"]["est"] < 500:
            b.plot(s["q"], s["tau_sw"]["est"], "o", ms=3.5, color=C[o["regime"]])
    b.set_yscale("log")
    b.set_xlabel("old-state order q")
    b.set_ylabel("switching time τ_sw (active h)")
    card = json.loads((DATA / "results/card.json").read_text())["bge_small_style_resid32"]
    b.text(0.03, 0.97, f"(b)  ρ = {card['rho_q_logtau_sw']:+.2f} (n {card['n_sw_identified']})\nnull p95 {card['rho_sw_null_p95']:+.2f}",
           transform=b.transAxes, va="top", fontsize=6.5)
    b.plot([], [], "o", color=C["I"], label="regime I"); b.plot([], [], "o", color=C["III"], label="regime III")
    b.legend(loc="lower left", fontsize=6)
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs.pdf")

    syn = json.loads((DATA / "synthetic/synthetic.json").read_text())
    fig, (a, b) = plt.subplots(1, 2, figsize=(3.4, 1.9), sharey=True)
    for ax, key, title in ((a, "rho_q_logtau", "τ_old (cosine)"), (b, "rho_q_logtau_sw", "τ_sw (ratio, A1)")):
        for k, col, lab in (("S1_lag", C["ink"], "no order dep."), ("S2_hysteresis", C["gte"], "hysteresis")):
            v = [r[key] for r in syn[k]["reps"] if np.isfinite(r[key])]
            ax.hist(v, bins=np.linspace(-1, 1, 21), color=col, alpha=0.55, label=lab)
        ax.axvline(0, color=C["grid"], lw=0.8)
        ax.set_title(title, fontsize=7)
        ax.set_xlabel("ρ(q, ln τ)")
    b.axvline(card["rho_q_logtau_sw"], color=C["I"], lw=1.2)
    a.set_ylabel("replicates")
    a.legend(fontsize=5.5, loc="upper left")
    fig.tight_layout()
    fig.savefig(FIG / "summary_synthetic.pdf")


if __name__ == "__main__":
    main()
