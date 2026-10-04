"""H35 writeup visual (with H60 as companion): the auto-nudger is an inefficient Maxwell demon.

Builds fig.pdf / fig.png from
  data/processed/H35-nudger-maxwell-demon/G51/results.json        (round 1: information-work plane, trap-age response)
  data/processed/H35-nudger-maxwell-demon/G51/r1b/results_r1b*.json (round 1b: efficiency for glances and commits)
  data/processed/H60-index-nudge-policy/G51/results.json           (H60: policy values at idle gates)
Panels: (a) G51 information-work plane in trap-age space: frontier V*(R), Donsker-Varadhan ceiling, random nudging,
the logged nudger, nudge only at k = 2-3, nudge only deep traps; (b) response per first nudge and share of nudges by
trap age; (c) Sagawa-Ueda efficiency by outcome (round 1b); (d) H60: policy value per nudge at idle gates.
Usage: uv run python writeup/visuals/H35-nudger-demon/make.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "writeup/visuals"))
sys.path.insert(0, str(ROOT / "hypotheses/H35-nudger-maxwell-demon/analysis"))
import vstyle as vs  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

D35 = ROOT / "data/processed/H35-nudger-maxwell-demon/G51"
D60 = ROOT / "data/processed/H60-index-nudge-policy/G51/results.json"
LN2 = np.log(2)
C_LOG, C_ONCE, C_DEEP = vs.C["red"], vs.C["green"], vs.C["pink"]


def policy_info(p, pi):
    """I(X;M) in nats (same formula as h35lib.policy_info)."""
    r = float(np.sum(p * pi))
    with np.errstate(divide="ignore", invalid="ignore"):
        t1 = np.where(pi > 0, pi * np.log(pi / r), 0.0)
        t0 = np.where(pi < 1, (1 - pi) * np.log((1 - pi) / (1 - r)), 0.0)
    return float(np.sum(p * (t1 + t0)))


def policy_value(p, pi, g):
    r = np.sum(p * pi)
    return float(np.sum(p * pi * g) - r * np.sum(p * g))


def only_bin(e, j):
    p = np.array(e["p"]); g = np.array(e["g_shrunk"]); r = e["r"]
    pi = np.zeros_like(p); pi[j] = min(1.0, r / p[j]); rr = float(np.sum(p * pi))
    return policy_info(p, pi) / LN2 / rr, policy_value(p, pi, g) / rr


def main():
    vs.use()
    R = json.loads((D35 / "results.json").read_text())
    e = R["minute_k_eff"]
    r1b = json.loads((D35 / "r1b/results_r1b.json").read_text())["k_eff"]
    did = json.loads((D35 / "r1b/results_r1b_did.json").read_text())
    h60 = json.loads(D60.read_text())["calls30"]

    fig = plt.figure(figsize=(vs.W["double"], 4.6))
    gs = fig.add_gridspec(2, 2, hspace=0.55, wspace=0.32)

    # (a) information-work plane
    ax = fig.add_subplot(gs[0, 0])
    fb, fv = np.array(e["frontier_bits_per_nudge"]), np.array(e["frontier_value_per_nudge"])
    m = fb <= 4.2
    bb = np.linspace(0, 4.2, 200)
    ceil = e["half_range_g"] * np.sqrt(2 * bb * LN2)
    ax.fill_between(bb, ceil, 3.0, color=vs.NULL, alpha=0.25, lw=0)
    ax.plot(bb, ceil, color=vs.INK2, ls=":", lw=1.0)
    ax.text(0.55, 2.62, "forbidden: above the\nDonsker–Varadhan ceiling", fontsize=5.5, color=vs.INK2)
    ax.plot(fb[m], fv[m], color=vs.INK, lw=1.5)
    ax.text(2.3, 1.45, r"frontier $V^*(R)$", fontsize=6, color=vs.INK)
    ax.axhline(0, color=vs.INK2, lw=0.5)
    ax.scatter([0], [0], s=22, color=vs.MUTED, zorder=4); ax.text(0.08, -0.22, "random nudging", fontsize=5.8, color=vs.INK2)
    lo, hi = e["boot"]["dV_per_nudge"]
    xb, yb = e["bits_per_nudge"], e["dV_per_nudge"]
    ax.errorbar([xb], [yb], yerr=[[yb - lo], [hi - yb]], fmt="D", ms=5, color=C_LOG, capsize=0, elinewidth=0.9, zorder=5)
    vstar = e["Vstar_at_I_per_nudge"]
    ax.annotate("", xy=(xb, vstar), xytext=(xb, yb + 0.06), arrowprops=dict(arrowstyle="->", color=C_LOG, lw=0.7, ls="--"))
    ax.text(xb + 0.1, yb + 0.02, f"logged nudger\n$\\eta_{{SU}}$ = {e['eta_SU']:.2f}", fontsize=6, color=C_LOG, va="center")
    for j, col, mk, txt, dy in ((2, C_ONCE, "o", "nudge only at k = 2–3", 0.28), (4, C_DEEP, "v", "only deep traps (k ≥ 10)", -0.3)):
        x_, y_ = only_bin(e, j)
        ax.scatter([x_], [y_], marker=mk, s=28, color=col, zorder=5)
        ax.text(x_ + 0.05, y_ + dy, txt.replace("≥", r"$\geq$"), fontsize=5.8, color=col, va="center", ha="right")
    ax.set_xlim(0, 4.2); ax.set_ylim(-0.7, 2.9)
    ax.set_xlabel("state information used (bits per nudge)")
    ax.set_ylabel("work beyond random\n(extra active min per nudge)")
    ax.set_title("(a) #51: the demon sits far below its frontier", loc="left")

    # (b) response and share by trap age (two stacked axes, one y-axis each)
    sub = gs[0, 1].subgridspec(2, 1, height_ratios=[1.5, 1], hspace=0.12)
    ax1 = fig.add_subplot(sub[0]); ax2 = fig.add_subplot(sub[1], sharex=ax1)
    x = np.arange(5); labels = e["labels"]
    g_raw, g_se, g_sh = np.array(e["g_raw"]), np.array(e["g_se"]), np.array(e["g_shrunk"])
    ax1.errorbar(x, g_raw, yerr=1.96 * g_se, fmt="o", ms=3.5, color=vs.INK, elinewidth=0.8, capsize=0,
                 label="first-nudge response, 95% CI")
    ax1.plot(x, g_sh, color=vs.INK2, lw=0.9, ls="--", label="shrunk")
    ax1.axhline(0, color=vs.INK2, lw=0.5)
    ax1.set_ylabel("extra active min\nper nudge")
    ax1.tick_params(labelbottom=False)
    ax1.set_ylim(-1.8, 8.2)
    ax1.legend(loc="upper left", fontsize=5.5, ncol=2)
    ax1.set_title("(b) where nudges go vs where they work", loc="left")
    sh = np.array(e["share_of_nudges"])
    ax2.bar(x, sh, color=[vs.MUTED, C_ONCE, C_ONCE, vs.MUTED, C_DEEP], width=0.6)
    for xi, s in zip(x, sh):
        ax2.text(xi, s + 0.02, f"{s:.0%}", ha="center", fontsize=5.5)
    ax2.set_ylim(0, 0.52); ax2.set_ylabel("share of\nnudges")
    ax2.set_xticks(x, ["0 (no chain)", "1", "2–3", "4–9", r"$\geq$10"])
    ax2.set_xlabel("trap age k (re-pauses in the current chain)")

    # (c) efficiency by outcome (round 1b)
    ax = fig.add_subplot(gs[1, 0])
    rows = [("active minutes (round 1)", e["eta_SU"], e["boot"]["eta_SU"]),
            ("glance (any action in 30 min)", r1b["y_glance30"]["eta_SU"], r1b["y_glance30"]["boot"]["eta_SU"]),
            ("work commits (DiD, post hoc)", did["work_did_h"]["k_eff"]["eta_SU"], did["work_did_h"]["k_eff"]["boot"]["eta_SU"])]
    ax.axvspan(-0.03, 0.03, color=vs.NULL, alpha=0.7, lw=0)
    ax.axvline(1, color=vs.INK2, lw=0.6); ax.axvline(0.7, color=vs.MUTED, lw=0.6, ls=":")
    for i, (name, v, (l, h)) in enumerate(rows):
        lcl = max(l, -0.55)
        ax.plot([lcl, h], [i, i], color=C_LOG, lw=1.1)
        if l < -0.55:
            ax.annotate("", xy=(-0.58, i), xytext=(-0.45, i), arrowprops=dict(arrowstyle="->", color=C_LOG, lw=1.1))
            ax.text(-0.5, i - 0.28, f"to {l:.1f}".replace("-", "\u2212"), fontsize=5.3, color=C_LOG, ha="left")
        ax.scatter([v], [i], marker="D", s=20, color=C_LOG, zorder=3)
        ax.text(h + 0.03, i, f"{v:.2f}", fontsize=6, va="center")
    ax.text(-0.57, 3.2, "sustained runs: flat response, $\\eta$ undefined", fontsize=5.5, color=vs.INK2, va="center")
    ax.set_yticks(range(3), [r[0] for r in rows], fontsize=6)
    ax.set_ylim(3.6, -0.6); ax.set_xlim(-0.6, 1.12)
    ax.text(0.0, -0.45, "random", fontsize=5.5, color=vs.INK2, ha="center")
    ax.text(1.0, -0.45, "reversible", fontsize=5.5, color=vs.INK2, ha="center")
    ax.text(0.7, -0.45, "R1 bar", fontsize=5.5, color=vs.MUTED, ha="center")
    ax.set_xlabel(r"Sagawa–Ueda efficiency $\eta_{SU}$ (bootstrap 95% CI)")
    ax.set_title("(c) bits buy glances, not committed work", loc="left")

    # (d) H60 policy values
    ax = fig.add_subplot(gs[1, 1])
    pol = [("logged nudger", "logged", C_LOG), ("random gates", "random", vs.MUTED), ("once-early (k = 2)", "once_early", C_ONCE),
           ("index, myopic", "index", vs.C["sky"]), ("index, once per trap", "index_once", vs.C["sky"])]
    for i, (name, k, col) in enumerate(pol):
        v = h60["values"][k]; l, h = h60["values_ci"][k]
        ax.barh(i, v, color=col, height=0.6, alpha=0.85)
        ax.plot([l, h], [i, i], color=vs.INK, lw=0.9)
        rat = v / h60["values"]["logged"]
        ax.text(31.5, i, f"×{rat:.2f}", fontsize=6, va="center", ha="right")
    ax.set_yticks(range(len(pol)), [p[0] for p in pol], fontsize=6)
    ax.set_ylim(len(pol) - 0.4, -0.6)
    ax.set_xlim(-3, 32)
    ax.axvline(0, color=vs.INK2, lw=0.5)
    ax.set_xlabel("extra active calls in 30 min per nudge (95% CI)")
    ax.text(31.5, -0.55, "vs logged", fontsize=5.5, ha="right", color=vs.INK2)
    ax.set_title("(d) H60: once-early beats it; an index adds nothing", loc="left")
    vs.save(fig, HERE / "fig")
    plt.close(fig)
    print({p[1]: (round(h60['values'][p[1]], 2), [round(c, 2) for c in h60['values_ci'][p[1]]]) for p in pol})
    print("once-early k=2-3 point", only_bin(e, 2), "deep", only_bin(e, 4))


if __name__ == "__main__":
    main()
