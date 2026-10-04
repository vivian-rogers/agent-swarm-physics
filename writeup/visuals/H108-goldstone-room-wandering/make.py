"""H108 visual: the #best/#rest room direction persists from day to day inside a goal period, more so with
room-specific kickoffs (pinned) than with identical ones (Goldstone-like drift).

Static (fig.pdf/png, double column):
  (a) simulation: the angle of a room order parameter over 17 days, free (Goldstone diffusion, D_theta = 0.355/day,
      the identical-kickoff pooled value) vs pinned by a field (Ornstein-Uhlenbeck around h, D_theta = 0.075/day);
  (b) measured direction persistence P(l) per period (noise-corrected, joint-relabel excess), with the Goldstone decay
      exp(-D_theta l) for both pooled groups; lags with >= 2 day pairs only;
  (c) P(1) per period with agent-bootstrap 95% CIs against the regenerating synthetic world (gray, 10-90%) and the
      pooled group values with their CIs.
All measured numbers come from H108's results (raw_all.json, bge style_resid with constants; synthetic_summary.json);
nothing is recomputed.

Run: uv run python writeup/visuals/H108-goldstone-room-wandering/make.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import _rooms_common as rc  # noqa: E402
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.gridspec import GridSpec  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

import vstyle as vs  # noqa: E402

RAW = rc.load_json("H108-goldstone-room-wandering/results/raw_all.json")["bge_small/style_resid"]
SYN = rc.load_json("H108-goldstone-room-wandering/synthetic/synthetic_summary.json")["single"]["regen_c0.0_rho1.0"]
PER = RAW["periods"]; GRP = RAW["groups"]
FIELDED, IDENT = ["G38", "G44"], ["G36", "G37", "G39", "G41", "G42"]
D_ID, D_F = GRP["identical"]["D"], GRP["fielded"]["D"]
C_FORK = vs.C["green"]


def panel_sim(ax):
    rng = np.random.default_rng(3)
    days = np.arange(18)
    for rep in range(3):
        # Goldstone: angular random walk; per-day cos decay exp(-D) in 2-D needs var = 2 D per day
        th = np.cumsum(np.r_[0, rng.normal(0, np.sqrt(2 * D_ID), 17)])
        ax.plot(days, np.degrees(th), color=vs.COUPLING, lw=1.0, alpha=0.85)
        # pinned: OU around 0 with the fielded decorrelation
        k, s = 0.6, np.sqrt(2 * D_F)
        ph = [rng.normal(0, 8 / 57.3)]
        for _ in range(17):
            ph.append(ph[-1] * (1 - k) + rng.normal(0, s))
        ax.plot(days, np.degrees(ph), color=vs.FIELD, lw=1.0, alpha=0.9)
    ax.axhline(0, color=vs.FIELD, lw=0.6, ls=":")
    ax.set_xlabel("day in the goal period"); ax.set_ylabel("room direction angle (deg)")
    ax.set_ylim(-330, 330); ax.set_yticks([-270, -180, -90, 0, 90, 180, 270])
    h = [Line2D([], [], color=vs.COUPLING, lw=1.0, label="free: drifts (Goldstone)"),
         Line2D([], [], color=vs.FIELD, lw=1.0, label="pinned by a field $h$")]
    ax.legend(handles=h, loc="lower left", fontsize=6.0, handlelength=1.4, borderaxespad=0.2)
    ax.set_title("(a) simulation: free vs pinned direction", loc="left")


def panel_lag(ax):
    lmax = 6
    ls = np.linspace(0, lmax, 50)
    ax.plot(ls, np.exp(-D_ID * ls), color=vs.COUPLING, lw=0.9, ls="--")
    ax.plot(ls, np.exp(-D_F * ls), color=vs.FIELD, lw=0.9, ls="--")
    ax.axhline(0, color=vs.MUTED, lw=0.6, ls=":")
    for k, v in PER.items():
        lags = [int(l) for l, x in v["lags"].items() if x["n_pairs"] >= 2 and v["P_lag"][l] is not None]
        if not lags:
            continue
        y = [v["P_lag"][str(l)] for l in lags]
        x = [0] + lags; y = [1] + y
        if k in FIELDED:
            col, lw, mk = vs.FIELD, 1.5, "o"
        elif k == "G35":
            col, lw, mk = C_FORK, 1.2, "s"
        else:
            col, lw, mk = vs.COUPLING, 0.9, "^"
        ax.plot(x, y, color=col, lw=lw, marker=mk, ms=3, alpha=0.95 if k in FIELDED else 0.7)
    lab = {"G38": "#38 (17 days)", "G44": "#44", "G35": "#35 forks", "G41": "#41"}
    off = {"G38": 0.03, "G44": -0.07, "G35": 0, "G41": -0.03}
    for k, t in lab.items():
        v = PER[k]
        lags = [int(l) for l, x in v["lags"].items() if x["n_pairs"] >= 2 and v["P_lag"][l] is not None]
        col = vs.FIELD if k in FIELDED else C_FORK if k == "G35" else vs.COUPLING
        ax.text(lags[-1] + 0.12, v["P_lag"][str(lags[-1])] + off[k], t, fontsize=6.2, color=col, va="center")
    ax.text(5.9, np.exp(-D_ID * 5.9) + 0.06, f"$e^{{-{D_ID:.2f}\\,\\ell}}$", color=vs.COUPLING, fontsize=6.5,
            ha="right")
    ax.text(5.9, np.exp(-D_F * 5.9) - 0.1, f"$e^{{-{D_F:.3f}\\,\\ell}}$", color=vs.FIELD, fontsize=6.5, ha="right")
    ax.set_xlim(0, 7.4); ax.set_ylim(-0.25, 1.08)
    ax.set_xlabel("lag $\\ell$ (days)"); ax.set_ylabel("direction persistence $P(\\ell)$")
    ax.set_title("(b) measured persistence $P(\\ell)$", loc="left")
    h = [Line2D([], [], color=vs.FIELD, marker="o", ms=3, label="room-specific kickoffs"),
         Line2D([], [], color=vs.COUPLING, marker="^", ms=3, lw=0.9, label="identical kickoffs"),
         Line2D([], [], color=C_FORK, marker="s", ms=3, lw=1.2, label="fork week"),
         Line2D([], [], color=vs.INK2, ls="--", lw=0.9, label="$e^{-D_\\theta\\ell}$, pooled $D_\\theta$")]
    ax.legend(handles=h, loc="lower right", fontsize=6.0, handlelength=1.6, borderaxespad=0.2)


def panel_P1(ax):
    order = ["G35", "G36", "G37", "G39", "G41", "G42", "G38", "G44"]
    for i, k in enumerate(order):
        v = PER[k]; q = SYN[k[1:]]["P1_q10_q90"]
        ax.add_patch(plt.Rectangle((i - 0.3, q[0]), 0.6, q[1] - q[0], color=vs.NULL, alpha=0.6, lw=0))
        col = vs.FIELD if k in FIELDED else C_FORK if k == "G35" else vs.COUPLING
        lo, hi = v["P1_ci"]
        ax.errorbar(i, v["P1"], yerr=[[max(v["P1"] - lo, 0)], [max(hi - v["P1"], 0)]], fmt="o", color=col, ms=4,
                    lw=0.9, capsize=1.5)
        if lo > v["P1"] or hi < v["P1"]:
            ax.plot([i, i], [lo, hi], color=col, lw=0.9)
    gi = GRP["identical"]["P1"]; gf = GRP["fielded"]["P1"]
    ci_i, ci_f = GRP["P1_identical_ci"], GRP["P1_fielded_ci"]
    ax.fill_between([0.7, 5.3], ci_i[0], ci_i[1], color=vs.COUPLING, alpha=0.12, lw=0)
    ax.plot([0.7, 5.3], [gi, gi], color=vs.COUPLING, lw=1.0)
    ax.fill_between([5.7, 7.3], ci_f[0], ci_f[1], color=vs.FIELD, alpha=0.15, lw=0)
    ax.plot([5.7, 7.3], [gf, gf], color=vs.FIELD, lw=1.0)
    ax.text(3.5, 0.97, f"pooled identical {gi:.2f}", color=vs.COUPLING, fontsize=6.3, ha="center")
    ax.text(6.5, 0.45, f"pooled\nfielded {gf:.2f}", color=vs.FIELD, fontsize=6.3, ha="center")
    ax.text(0.98, 0.04, f"$R_D=D_\\mathrm{{id}}/D_\\mathrm{{f}}={GRP['R_D']:.1f}$ [{GRP['R_D_ci'][0]:.1f}, "
            f"{GRP['R_D_ci'][1]:.1f}]", transform=ax.transAxes, ha="right", fontsize=6.3)
    ax.axhline(0, color=vs.MUTED, lw=0.6, ls=":")
    ax.set_xticks(range(len(order)), [f"#{k[1:]}" for k in order], fontsize=6.6)
    for t, k in zip(ax.get_xticklabels(), order):
        t.set_color(vs.FIELD if k in FIELDED else C_FORK if k == "G35" else vs.INK2)
    ax.set_ylim(-0.45, 1.32); ax.set_ylabel("day-to-day persistence $P(1)$")
    ax.set_title("(c) $P(1)$ vs a regenerating room", loc="left")
    h = [plt.Rectangle((0, 0), 1, 1, color=vs.NULL, alpha=0.6, label="regenerating world\n(synthetic, 10–90%)")]
    ax.legend(handles=h, loc="upper left", fontsize=6.0, handlelength=1.2, borderaxespad=0.2)


def make_static():
    vs.use()
    fig = plt.figure(figsize=(vs.W["double"], 2.55))
    gs = GridSpec(1, 3, figure=fig, width_ratios=[1, 1.1, 1.15], wspace=0.36, left=0.065, right=0.99, top=0.88,
                  bottom=0.17)
    panel_sim(fig.add_subplot(gs[0]))
    panel_lag(fig.add_subplot(gs[1]))
    panel_P1(fig.add_subplot(gs[2]))
    vs.save(fig, HERE / "fig")
    plt.close(fig)


if __name__ == "__main__":
    make_static()
