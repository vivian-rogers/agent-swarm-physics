"""H40 writeup visual: in the computer-use scaffold agents couple per model call, not per minute.

    uv run python writeup/visuals/H40-call-clock-coupling/make.py

Reads only H40's processed outputs (data/processed/H40-call-clock-coupling/results/): replication_table.parquet
(eta per period), summary.json (random-effects pooled eta by regime) and G51.json (per agent-unit call rates and
per-call coupling intercepts, between-agent slope). Non-holdout only (H40 built every table from non-holdout days).
Panel (a) is an analytic illustration, labelled as such. No animation: the still carries it.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "writeup/visuals"))
import vstyle as vs  # noqa: E402

D = ROOT / "data/processed/H40-call-clock-coupling/results"
MIN_REPLIES_AU = 5          # as H40 replication.between_agent
MK = {"I": "s", "II": "D", "III": "o"}


def demean(y, x, unit, w):
    y, x = y.copy(), x.copy()
    for u in np.unique(unit):
        m = unit == u
        ww = w[m] / w[m].sum()
        y[m] -= (ww * y[m]).sum(); x[m] -= (ww * x[m]).sum()
    return y, x


def heavy_spins():
    r = json.loads((D / "G51.json").read_text())
    t = r["au_table"]; b = r["between"]
    fe, se, rate = (np.array(t[k], float) for k in ("fe", "fe_se", "rate"))
    rep = np.array(t["replies"], float); unit = np.array(t["unit"])
    ok = (rep >= MIN_REPLIES_AU) & np.isfinite(fe) & np.isfinite(rate) & (rate > 0) & np.isfinite(se) & (se > 0)
    assert ok.sum() == b["n_au"], (ok.sum(), b["n_au"])
    w = 1 / (se[ok] ** 2 + b["tau"] ** 2)
    x = np.log(rate[ok])
    yc, xc = demean(fe[ok], x, unit[ok], w)
    yh, _ = demean(fe[ok] + x, x, unit[ok], w)
    xm = (w * x).sum() / w.sum()
    return dict(x=xc + xm, ycall=yc, yhour=yh, w=w, b=b, xm=xm, rate=rate[ok])


def panel_sim(ax_c, ax_w):
    """Call clock, analytic: hazard h per call after read-out, two agents with 40 s and 8 s between calls."""
    h = 0.08
    n = np.arange(0, 121)
    for dt, ls, lab in ((8.0, "-", "fast (8 s / call)"), (40.0, "--", "slow (40 s / call)")):
        P = 1 - (1 - h) ** n
        ax_c.plot(n, P, ls=ls, color=vs.COUPLING, lw=1.3, label=lab)
        ax_w.plot(n * dt / 60, P, ls=ls, color=vs.COUPLING, lw=1.3)
    ax_c.set_xlabel("calls since read-out", labelpad=1)
    ax_c.set_xlim(0, 30)
    ax_w.set_xlabel("minutes since read-out", labelpad=1)
    ax_w.set_xlim(0, 10)
    for a in (ax_c, ax_w):
        a.set_ylim(0, 1); a.set_yticks([0, 0.5, 1])
        a.set_ylabel("P(replied)", labelpad=1)
    ax_c.set_title("(a) call clock, analytic", loc="left")
    ax_c.text(14, 0.12, "curves coincide", fontsize=6.5, color=vs.INK2)
    ax_w.text(5.6, 0.18, "smear", fontsize=6.5, color=vs.INK2)
    ax_c.legend(loc="upper left", fontsize=5.6, handlelength=1.8, borderaxespad=0.1)


def panel_eta(ax):
    T = pl.read_parquet(D / "replication_table.parquet").sort("goal")
    S = json.loads((D / "summary.json").read_text())["RE_eta"]
    x = np.arange(T.height)
    for reg in ("I", "II", "III"):
        m = (T["regime"] == reg).to_numpy()
        ax.errorbar(x[m], T["eta"].to_numpy()[m], yerr=[T["eta"].to_numpy()[m] - T["eta_lo"].to_numpy()[m],
                                                        T["eta_hi"].to_numpy()[m] - T["eta"].to_numpy()[m]],
                    fmt=MK[reg], ms=3, color=vs.COUPLING, mfc="white" if reg == "I" else vs.COUPLING, elinewidth=0.6,
                    capsize=0, mew=0.8, label=f"regime {reg}")
        r = S[reg]
        xs = x[m]
        ax.fill_between([xs.min() - 0.4, xs.max() + 0.4], r["lo"], r["hi"], color=vs.COUPLING, alpha=0.12, lw=0)
        ax.plot([xs.min() - 0.4, xs.max() + 0.4], [r["mean"]] * 2, color=vs.COUPLING, lw=1.0)
    ax.axhline(0, color=vs.COUPLING, lw=0.8, ls=":")
    ax.axhline(1, color=vs.MUTED, lw=1.0, ls="--")
    ax.text(0.3, 1.04, "wall clock ($\\eta=1$)", fontsize=6, color=vs.INK2, va="bottom")
    ax.text(0.3, -0.05, "call clock ($\\eta=0$)", fontsize=6, color=vs.COUPLING, ha="left", va="top")
    g = T["goal"].to_list()
    lab_at = [i for i, gg in enumerate(g) if gg in (2, 13, 24, 33, 38, 51)]
    ax.set_xticks(lab_at); ax.set_xticklabels([f"G{g[i]:02d}" for i in lab_at], fontsize=6.3)
    ax.set_xlim(-0.8, T.height - 0.2)
    ax.set_ylim(-1.0, 1.45)
    ax.set_ylabel("exposure-time elasticity $\\eta$")
    ax.set_title("(b) which clock, 33 periods", loc="left")
    ax.legend(loc="lower left", fontsize=5.8, ncol=3, handlelength=1.0, columnspacing=0.8, borderaxespad=0.1)
    return S


def panel_spins(ax, H, which):
    b = H["b"]
    y = H["ycall"] if which == "call" else H["yhour"]
    sz = 2 + 30 * H["w"] / H["w"].max()
    ax.scatter(H["x"], y, s=sz, color=vs.COUPLING, alpha=0.45, lw=0)
    xs = np.linspace(H["x"].min(), H["x"].max(), 50)
    s = b["s"] if which == "call" else b["hour_slope"]
    ax.plot(xs, s * (xs - H["xm"]), color=vs.COUPLING, lw=1.5)
    # rival: wall clock at the agent level (s = -1: same per-hour coupling for all)
    rival = -1.0 if which == "call" else 0.0
    ax.plot(xs, rival * (xs - H["xm"]), color=vs.MUTED, lw=1.0, ls="--")
    ticks = [25, 50, 100, 200]
    ax.set_xticks(np.log(ticks)); ax.set_xticklabels([str(t) for t in ticks])
    ax.set_xlabel("call rate (calls / h)")
    ax.set_ylim(-4.2, 4.2)
    if which == "call":
        ax.set_ylabel("coupling (log, within unit)")
        ax.set_title("(c) G51: per call", loc="left")
        ax.text(0.03, 0.96, "$s=%+.2f$ [%+.2f, %+.2f]" % (b["s"], b["s_lo"], b["s_hi"]), transform=ax.transAxes,
                fontsize=6.2, color=vs.COUPLING, va="top")
        ax.text(0.97, 0.04, "wall-clock rival\n$s=-1$", transform=ax.transAxes, fontsize=5.8, color=vs.INK2,
                ha="right", va="bottom")
    else:
        ax.set_title("(d) G51: per hour", loc="left")
        ax.text(0.03, 0.96, "slope %.2f [%.2f, %.2f]" % (b["hour_slope"], 1 + b["s_lo"], 1 + b["s_hi"]),
                transform=ax.transAxes, fontsize=6.2, color=vs.COUPLING, va="top")
        ax.text(0.97, 0.04, "wall-clock rival: flat", transform=ax.transAxes, fontsize=5.8, color=vs.INK2,
                ha="right", va="bottom")
        plt.setp(ax.get_yticklabels(), visible=False)


def main():
    vs.use()
    fig = plt.figure(figsize=(vs.W["double"], 2.45))
    gs = fig.add_gridspec(2, 4, width_ratios=[0.8, 1.35, 0.95, 0.95], hspace=0.95, wspace=0.42,
                          left=0.055, right=0.99, bottom=0.17, top=0.9)
    panel_sim(fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[1, 0]))
    S = panel_eta(fig.add_subplot(gs[:, 1]))
    H = heavy_spins()
    ax3 = fig.add_subplot(gs[:, 2]); panel_spins(ax3, H, "call")
    ax4 = fig.add_subplot(gs[:, 3], sharey=ax3); panel_spins(ax4, H, "hour")
    vs.save(fig, HERE / "fig")
    plt.close(fig)
    print({k: (round(v["mean"], 3), round(v["lo"], 3), round(v["hi"], 3)) for k, v in S.items()})
    print({k: H["b"][k] for k in ("n_au", "s", "s_lo", "s_hi", "hour_slope")})


if __name__ == "__main__":
    main()
