"""H146 round 1 figures: r1_obs.pdf (per-pattern estimates against pseudo-patterns) and r1_synth.pdf (power)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
D = ROOT / "data" / "processed" / "H146-egregore-recruitment-behaviors-51"
FIG = HERE.parent / "figures"
BLUE, ORANGE, GRAY, INK = "#2a78d6", "#eb6834", "#9a9a94", "#333333"
plt.rcParams.update({"font.size": 7, "axes.edgecolor": "#888888", "axes.linewidth": 0.6, "xtick.color": INK,
                     "ytick.color": INK, "axes.labelcolor": INK, "axes.spines.top": False,
                     "axes.spines.right": False})


def load(name):
    p = D / "results" / name
    return json.loads(p.read_text()) if p.exists() else None


def rows(res, colour):
    out = []
    if not res:
        return out
    for k, r in res["patterns"].items():
        lab = r["meta"].get("label") or k
        out.append((k if res["set"] == "candidates" else f"{k}", lab, r, colour, res["set"]))
    return out


def ci_of(o, key):
    if not o or key not in o or o[key] is None:
        return None
    e, se = o[key]
    return e, e - 1.96 * se, e + 1.96 * se


def obs():
    R = rows(load("real_h145.json"), BLUE) + rows(load("real_candidates.json"), ORANGE)
    if not R:
        return
    fig, ax = plt.subplots(1, 3, figsize=(7.0, 2.6), sharey=True)
    y = np.arange(len(R))[::-1]
    for yi, (k, lab, r, c, s) in zip(y, R):
        st, ps = r["stats"], r["pseudo"]["values"]
        # P1b
        v = ci_of(st.get("P1b"), "delta")
        pv = [x for x in ps["P1b"] if x is not None]
        ax[0].scatter(pv, np.full(len(pv), yi), s=4, color=GRAY, lw=0, alpha=0.6)
        if v:
            ax[0].plot([v[1], v[2]], [yi, yi], color=c, lw=1.5)
            ax[0].scatter([v[0]], [yi], s=14, color=c, zorder=3)
        # P4 HR
        p4 = st.get("P4") or {}
        pv = [x for x in ps["P4_HR"] if x is not None]
        ax[1].scatter(pv, np.full(len(pv), yi), s=4, color=GRAY, lw=0, alpha=0.6)
        if p4.get("HR_F_vs_P") is not None:
            lo, hi = p4["ci"]
            if lo is not None:
                ax[1].plot([lo, hi], [yi, yi], color=c, lw=1.5)
            ax[1].scatter([p4["HR_F_vs_P"]], [yi], s=14, color=c, zorder=3)
        # P5 wipe RR
        w = (st.get("P5") or {}).get("wipe") or {}
        pv = [x for x in ps["P5_wipe"] if x is not None]
        ax[2].scatter(pv, np.full(len(pv), yi), s=4, color=GRAY, lw=0, alpha=0.6)
        if w.get("rr") is not None:
            lo, hi = w["ci"]
            if lo is not None:
                ax[2].plot([lo, hi], [yi, yi], color=c, lw=1.5)
            ax[2].scatter([w["rr"]], [yi], s=14, color=c, zorder=3)
    ax[0].set_yticks(y)
    ax[0].set_yticklabels([(k if s == "candidates" else k)[:22] + (" (post hoc)" if s == "candidates" else "")
                           for k, lab, r, c, s in R])
    ax[0].axvline(0, color="#bbbbbb", lw=0.6)
    ax[1].axvline(1, color="#bbbbbb", lw=0.6)
    ax[1].axvline(0.8, color="#bbbbbb", lw=0.6, ls=":")
    ax[1].axvline(0.5, color="#bbbbbb", lw=0.6, ls="--")
    ax[2].axvline(1, color="#bbbbbb", lw=0.6)
    ax[0].set_xlabel("P1b: read − in-flight log rate ratio")
    ax[1].set_xlabel("P4: re-expression HR, wipe vs placebo")
    ax[2].set_xlabel("P5: repair messages RR, wipe vs placebo")
    ax[2].scatter([], [], s=4, color=GRAY, label="pseudo-patterns")
    ax[2].scatter([], [], s=14, color=BLUE, label="H145 memeplex")
    ax[2].scatter([], [], s=14, color=ORANGE, label="candidate (post hoc)")
    ax[2].legend(frameon=False, fontsize=6, loc="lower right")
    fig.tight_layout()
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / "r1_obs.pdf")
    fig.savefig(FIG / "r1_obs.png", dpi=150)


def synth():
    s = json.loads((D / "synthetic" / "p1_synthetic.json").read_text())["worlds"]
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.4))
    for q0, ls in ((0.04, "-"), (0.12, "--")):
        for beta, c in ((0.3, BLUE), (0.6, ORANGE)):
            xs, ys = [], []
            for n in (500, 1500, 4000):
                k = f"expr_contagion_b{beta}_n{n}_q{q0}"
                if k in s:
                    xs.append(n)
                    ys.append(s[k]["rej_ci_above0"])
            ax[0].plot(xs, ys, ls=ls, color=c, lw=1.5, marker="o", ms=3,
                       label=f"β {beta}, q0 {q0}")
        xs = [n for n in (500, 1500, 4000)]
        ys = [max(s[f"expr_conv_slow_b0.0_n{n}_q{q0}"]["rej_ci_above0"],
                  s[f"expr_conv_fast_b0.0_n{n}_q{q0}"]["rej_ci_above0"]) for n in xs]
        ax[0].plot(xs, ys, ls=ls, color=GRAY, lw=1.2, label=f"convergence (max), q0 {q0}")
    ax[0].axhline(0.8, color="#bbbbbb", lw=0.6, ls=":")
    ax[0].set_xscale("log")
    ax[0].set_xticks([500, 1500, 4000])
    ax[0].set_xticklabels(["500", "1,500", "4,000"])
    ax[0].minorticks_off()
    ax[0].set_xlabel("events (expression design)")
    ax[0].set_ylabel("share z > 1.96")
    ax[0].legend(frameon=False, fontsize=5.5, ncol=1)
    pw = [load("power_h145.json"), load("power_candidates.json")]
    for res, c in zip(pw, (BLUE, ORANGE)):
        if not res:
            continue
        for k, v in res["patterns"].items():
            p = v.get("P1b_expr") or {}
            if "power" in p:
                ax[1].scatter([p.get("rows_read_exposed", 0)], [p["power"]], s=12, color=c)
                ax[1].annotate(k[:12], (p.get("rows_read_exposed", 0), p["power"]), fontsize=5, color=INK,
                               xytext=(2, 2), textcoords="offset points")
    ax[1].axhline(0.8, color="#bbbbbb", lw=0.6, ls=":")
    ax[1].set_xlabel("at-risk rows with a K item in the mirror window")
    ax[1].set_ylabel("P1b power at log-OR 0.3")
    ax[1].set_ylim(-0.03, 1.03)
    fig.tight_layout()
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / "r1_synth.pdf")
    fig.savefig(FIG / "r1_synth.png", dpi=150)


if __name__ == "__main__":
    synth()
    obs()
