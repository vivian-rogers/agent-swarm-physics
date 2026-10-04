"""H64 figures: figures/h64_obs.pdf (phase diagram of position-opposition by prize class; the G12 settlement
switch-off and the G26/G23 natives) and figures/h64_synth.pdf (synthetic power of the DiD)."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data/processed/H64-conflict-scarce-prize"
FIG = Path(__file__).resolve().parents[1] / "figures"
C = {"blue": "#2a78d6", "orange": "#eb6834", "aqua": "#1baf7a", "yellow": "#eda100", "violet": "#4a3aa7",
     "gray": "#8a8984", "ink": "#0b0b0b", "ink2": "#52514e"}
plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": C["ink2"], "axes.labelcolor": C["ink"], "xtick.color": C["ink2"],
                     "ytick.color": C["ink2"], "font.family": "sans-serif"})


def obs():
    u = json.loads((DATA / "replication/units.json").read_text())
    s = json.loads((DATA / "replication/summary.json").read_text())
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.6), gridspec_kw={"width_ratios": [1.15, 1]})
    a = ax[0]
    classes = [("prize_free", "prize-free", C["gray"]), ("rivalry_no_prize", "#51 units\n(no prize)", C["violet"]),
               ("competition", "competition", C["orange"]), ("assigned", "debates", C["blue"])]
    rng = np.random.default_rng(0)
    for k, (cl, lab, col) in enumerate(classes):
        rr = [r for r in u if r["prize_class"] == cl]
        y = np.array([r["r_pos"][0] for r in rr]) * 100
        x = k + rng.uniform(-0.18, 0.18, len(y))
        a.scatter(x, y, s=14, color=col, edgecolor="white", linewidth=0.5, zorder=3)
        if cl in ("competition", "assigned"):
            for xi, r in zip(x, rr):
                a.text(xi + 0.08, r["r_pos"][0] * 100, f"#{r['goal']}", fontsize=6.5, color=C["ink2"], va="center")
    a.axhline(s["P1"]["prize_free_median"] * 100, color=C["gray"], lw=1, ls="--", zorder=1)
    a.text(2.55, s["P1"]["prize_free_median"] * 100 - 0.25, "prize-free median", fontsize=6.5, color=C["ink2"])
    a.set_xticks(range(4), [c[1] for c in classes], fontsize=6.5)
    a.set_ylabel("confident position-opposition (% of replies)")
    a.set_title("(a) one point per period unit", fontsize=8, loc="left")
    b = ax[1]
    for name, lab, col in (("G12", "#12 debates", C["blue"]), ("G23", "#23 chess", C["orange"]),
                           ("G26", "#26 election", C["aqua"])):
        n = json.loads((DATA / f"natives/{name}.json").read_text())["soft"]
        off = {"G12": -0.15, "G23": 0.0, "G26": 0.15}[name]
        for j, k in enumerate(("g_open", "g_set")):
            e = n["est"][k]
            lo, hi = n["ci"][k]
            b.errorbar(j + off, e, yerr=[[e - lo], [hi - e]], fmt="o", color=col, ms=4, lw=1.2, capsize=0,
                       label=lab if j == 0 else None)
        b.plot([off, 1 + off], [n["est"]["g_open"], n["est"]["g_set"]], color=col, lw=0.8, alpha=0.6)
    b.axhline(0, color=C["ink2"], lw=0.6)
    b.set_xticks([0, 1], ["prize open", "prize settled"])
    b.set_xlim(-0.5, 1.5)
    b.set_ylabel("rival − other reply stance (soft)")
    b.set_title("(b) rival contrast before / after settlement", fontsize=8, loc="left")
    b.legend(frameon=False, fontsize=6.5, loc="lower right")
    fig.tight_layout()
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / "h64_obs.pdf")
    fig.savefig(FIG / "h64_obs.png", dpi=150)


def synth():
    s2 = json.loads((DATA / "synthetic/s2.json").read_text())["summary"]
    fig, ax = plt.subplots(figsize=(3.6, 1.9))
    xs = [0, 0.5, 1, 2]
    for name, col in (("G12", C["blue"]), ("G23", C["orange"]), ("G26", C["aqua"])):
        d = {r["scen"]: r for r in s2 if r["native"] == name}
        y = [d["null"]["open_neg"], d["gated_0.5"]["open_neg"], d["gated_1"]["open_neg"], d["gated_2"]["open_neg"]]
        ax.plot(xs, y, "-o", color=col, ms=3.5, lw=1.5, label=name)
        ax.plot([2.25], [d["relation_1"]["open_neg"]], "s", color=col, ms=3.5, mfc="white")
        ax.plot([2.45], [d["heat_1"]["open_neg"]], "^", color=col, ms=3.5, mfc="white")
    ax.set_xticks([0, 0.5, 1, 2, 2.25, 2.45], ["0", "0.5", "1", "2", "rel", "heat"], fontsize=6.5)
    ax.set_xlabel("planted gated antagonism |Δ| (logit); rivals at 1 logit")
    ax.set_ylabel("P(γ_open CI < 0)")
    ax.set_ylim(0, 1)
    ax.legend(frameon=False, fontsize=6.5, loc="upper left")
    fig.tight_layout()
    fig.savefig(FIG / "h64_synth.pdf")
    fig.savefig(FIG / "h64_synth.png", dpi=150)


if __name__ == "__main__":
    obs()
    synth()
