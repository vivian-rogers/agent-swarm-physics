"""H50 writeup visual: activity co-movement is the scheduler's field; talk spreads by a coupling gated at one read-out call.

    uv run python writeup/visuals/H50-field-vs-coupling-transfer-lag/make.py            # fig + animation
    uv run python writeup/visuals/H50-field-vs-coupling-transfer-lag/make.py --no-anim  # fig only

Reads only H50's processed outputs (data/processed/H50-field-vs-coupling-transfer-lag/): units/<unit>.npz (ledger calls,
peer messages, receiving calls; no text) for G38's five units, unit_table.parquet and the per-unit JSON results (hop
kernels, placebo jumps). Non-holdout only (units are built from non-holdout days; checked again here). Panel (a) and the
animation are a labelled simulation on a synthetic call schedule.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from matplotlib import animation  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import FancyArrowPatch  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "writeup/visuals"))
sys.path.insert(0, str(ROOT / "infra/shared"))
import vstyle as vs  # noqa: E402
from common import holdout_mask  # noqa: E402

D = ROOT / "data/processed/H50-field-vs-coupling-transfer-lag"
FIELD, COUP = vs.FIELD, vs.COUPLING


# ------------------------------------------------------------------------------------------- data
def ivw(est, se):
    est, se = np.asarray(est, float), np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    w = 1 / se[ok] ** 2
    m = (w * est[ok]).sum() / w.sum()
    s = 1 / np.sqrt(w.sum())
    return m, m - 1.96 * s, m + 1.96 * s


def g38_lags():
    """Field: each agent's first call of the day relative to that day's median first call. Coupling: peer message ->
    the recipient's receiving call (ledger), as H50's readout_delay."""
    on, rd = [], []
    for f in sorted((D / "units").glob("38*.npz")):
        z = np.load(f)
        days = [str(x) for x in z["days"]]
        assert not any(holdout_mask(days, [38] * len(days)))
        tc, ag, dy = z["calls__tc"], z["calls__agent"], z["calls__day"]
        for d in np.unique(dy):
            sel = dy == d
            firsts = np.array([tc[sel & (ag == a)].min() for a in np.unique(ag[sel])])
            on += list(firsts - np.median(firsts))
        rd += list(tc[z["mpairs__turn_pos"]] - z["msgs__t"][z["mpairs__msg"]])
    return np.array(on), np.array(rd)


def kernels():
    T = pl.read_parquet(D / "unit_table.parquet").filter(~pl.col("ne43"))
    R = {}
    for p in D.glob("G*/*.json"):
        if p.name != "native.json":
            r = json.loads(p.read_text())
            R[r["unit"]] = r
    out = {}
    for reg in ("I", "III"):
        us = T.filter(pl.col("regime") == reg)["unit"].to_list()
        K = np.array([R[u]["gate_talk"]["kernel"] for u in us], float)
        SE = np.array([R[u]["gate_talk"]["k_se"] for u in us], float)
        pts = [ivw(K[:, k], SE[:, k]) for k in range(K.shape[1])]
        pl_ = ivw([R[u]["gate_k1"]["talk"]["J_pl"] for u in us], [R[u]["gate_k1"]["talk"]["J_pl_se"] for u in us])
        out[reg] = dict(m=np.r_[0, [p[0] for p in pts]], lo=np.r_[0, [p[1] for p in pts]],
                        hi=np.r_[0, [p[2] for p in pts]], n=len(us), placebo=pl_)
    jpos = int((T["J1_lo"] > 0).sum()); jneg = int((T["J1_hi"] < 0).sum())
    return out, jpos, jneg, T.height


def native38():
    return json.loads((D / "G38" / "native.json").read_text())


# ------------------------------------------------------------------------------------------- simulation (schematic)
def sim_world(seed=7, n=7, T=120.0):
    """Synthetic call schedules (lognormal intervals, median ~13 s, as regime III) for the schematic."""
    rng = np.random.default_rng(seed)
    calls = []
    for i in range(n):
        t = -rng.uniform(0, 15) - 20
        cs = []
        while t < T:
            cs.append(t)
            t += rng.lognormal(np.log(13), 0.35)
        calls.append(np.array(cs))
    return calls


def next_call(c, t):
    return float(c[np.searchsorted(c, t, side="right")])


def sim_field(calls, t_in=10.0):
    return [next_call(c, t_in) for c in calls]


def sim_coupling(calls, t0=10.0, src=0):
    """A cascade: the source posts at t0; each agent responds at its first call after the message it reads (posting at
    the end of that call, +4 s), and its post is read by the next agents. Order fixed for clarity."""
    tree = {src: (None, t0, 0)}            # agent -> (parent, post time, hop)
    order = [(0, [1, 2]), (1, [3]), (2, [4]), (3, [5]), (4, [6])]
    for par, kids in order:
        tp = tree[par][1]
        for k in kids:
            r = next_call(calls[k], tp)
            tree[k] = (par, r + 4.0, tree[par][2] + 1, r)
    return tree


def draw_sim(ax, calls, kind, upto=None, fs=7, title=None):
    n = len(calls)
    x0, x1 = -5, 60
    for i, c in enumerate(calls):
        y = n - 1 - i
        cc = c[(c > x0) & (c < x1)]
        ax.vlines(cc, y - 0.22, y + 0.22, color=vs.MUTED, lw=0.8)
    if kind == "field":
        t_in = 10.0
        if upto is None or upto >= t_in:
            ax.axvline(t_in, color=FIELD, lw=1.4, alpha=0.8)
        for i, r in enumerate(sim_field(calls, t_in)):
            if upto is None or upto >= r:
                ax.plot([r], [n - 1 - i], "o", color=FIELD, ms=5 if fs > 7 else 3.6, mec="white", mew=0.4, zorder=5)
    else:
        tree = sim_coupling(calls)
        for a, v in tree.items():
            y = n - 1 - a
            if v[0] is None:
                if upto is None or upto >= v[1]:
                    ax.plot([v[1]], [y], "*", color=COUP, ms=8 if fs > 7 else 6, mec="white", mew=0.4, zorder=6)
                continue
            par, tpost, hop, r = v
            tp = tree[par][1]
            if upto is None or upto >= r:
                yp = n - 1 - par
                ax.add_patch(FancyArrowPatch((tp, yp), (r, y), arrowstyle="-|>", mutation_scale=6 if fs <= 7 else 9,
                                             color=COUP, lw=0.8 if fs <= 7 else 1.2, alpha=0.8,
                                             connectionstyle="arc3,rad=0.15", zorder=4))
                ax.plot([r], [y], "o", color=COUP, ms=5 if fs > 7 else 3.6, mec="white", mew=0.4, zorder=5)
                ax.text(r + 1.2, y + 0.25, f"hop {hop}" if fs > 7 else str(hop), fontsize=fs - 1, color=COUP,
                        va="bottom")
            elif upto >= tp:   # waiting for the next call
                ax.plot([upto], [y], "o", mfc="white", mec=COUP, ms=5 if fs > 7 else 3.6, mew=1.0, zorder=5)
    ax.set_xlim(x0, x1); ax.set_ylim(-0.7, n - 0.3)
    ax.set_yticks([]); ax.grid(False); ax.spines["left"].set_visible(False)
    if title:
        ax.set_title(title, loc="left", fontsize=fs + 0.5)


# ------------------------------------------------------------------------------------------- static figure
def symlog_hist(ax, x, color, label, bins, fill_alpha=0.25, ls="-"):
    h, e = np.histogram(x, bins=bins)
    h = h / h.sum()
    xs = np.repeat(e, 2)[1:-1]
    ys = np.repeat(h, 2)
    ax.fill_between(xs, ys, color=color, alpha=fill_alpha, lw=0, step=None)
    ax.plot(xs, ys, color=color, lw=1.2, ls=ls, label=label)


def fig_static():
    vs.use()
    calls = sim_world()
    on, rd = g38_lags()
    K, jpos, jneg, nunits = kernels()
    nat = native38()
    fig = plt.figure(figsize=(vs.W["double"], 2.5))
    gs = fig.add_gridspec(2, 3, width_ratios=[1.0, 1.25, 1.0], height_ratios=[1, 1.55], hspace=0.55, wspace=0.38,
                          left=0.03, right=0.99, bottom=0.17, top=0.88)
    axf = fig.add_subplot(gs[0, 0]); axc = fig.add_subplot(gs[1, 0])
    draw_sim(axf, calls, "field", fs=6.5, title="(a) simulation: field")
    draw_sim(axc, calls, "coupling", fs=6.5, title="coupling (hop by hop)")
    axf.set_xticks([]); axf.spines["bottom"].set_visible(False)
    axc.set_xlabel("time (s); ticks = model calls")
    # (b) lag distributions, G38
    ax = fig.add_subplot(gs[:, 1])
    lin = 10.0
    def f(x):
        return np.sign(x) * np.log10(1 + np.abs(x) / lin)
    edges_t = np.r_[-np.logspace(np.log10(300), 0, 12), 0, np.logspace(0, np.log10(3000), 17)]
    bins = np.unique(f(edges_t))
    symlog_hist(ax, f(on), FIELD, "field: day-start onsets,\nrelative to the day median", bins)
    symlog_hist(ax, f(rd), COUP, "coupling: peer message to\nrecipient's receiving call", bins)
    tick_s = [-100, -10, 0, 10, 100, 1000]
    ax.set_xticks(f(np.array(tick_s, float))); ax.set_xticklabels([str(t) for t in tick_s])
    ax.set_xlim(f(-300.0), f(3000.0))
    ax.axvline(0, color=vs.INK2, lw=0.5)
    ax.set_xlabel("lag (s; symmetric log scale)")
    ax.set_ylabel("share per bin")
    ax.set_title("(b) G38: transfer lags", loc="left")
    q_on = np.percentile(on, [25, 75]); q_rd = np.median(rd)
    ax.set_ylim(0, ax.get_ylim()[1] * 1.55)
    lg = ax.legend(loc="upper left", fontsize=6, handlelength=1.4, ncol=2, columnspacing=0.8, frameon=True,
                   facecolor="white", edgecolor="none", framealpha=1.0)
    lg.set_zorder(10)
    ax.text(f(-280.0), ax.get_ylim()[1] * 0.70, "onset IQR %.0f s\n(per-day median %.0f s)\n%.0f%% start before\nany peer message" % (
        q_on[1] - q_on[0], nat["resume"]["onset_iqr_s_median"], 100 * nat["resume"]["share_first_before_peer"]),
        fontsize=5.8, color=vs.INK2, va="top")
    ax.text(f(2900.0), ax.get_ylim()[1] * 0.70, "median %.0f s\n(one call $\\approx$ 13 s)" % q_rd, fontsize=5.8,
            color=vs.INK2, va="top", ha="right")
    # (c) hop kernel
    ax = fig.add_subplot(gs[:, 2])
    pls = []
    for reg, mk, dx, ls in (("I", "s", -0.08, "--"), ("III", "o", 0.08, "-")):
        k = K[reg]
        h = np.arange(len(k["m"])) + dx
        ax.fill_between(h, k["lo"], k["hi"], color=COUP, alpha=0.18 if reg == "III" else 0.10, lw=0)
        ax.plot(h, k["m"], ls=ls, marker=mk, color=COUP, ms=3, lw=1.1, mfc=COUP if reg == "III" else "white",
                label=f"regime {reg} ({k['n']} units)")
        pls.append(k["placebo"])
    plo = min(p[1] for p in pls); phi = max(p[2] for p in pls)
    ax.axhspan(plo, phi, color=vs.NULL, alpha=0.6, lw=0, zorder=0, label="shifted-time placebo")
    ax.axhline(0, color=vs.INK2, lw=0.5)
    ax.set_xticks(range(7))
    ax.set_xlabel("hop (recipient's calls after the message)")
    ax.set_ylabel("extra P(read-out call is talk)")
    ax.set_title("(c) the coupling is gated", loc="left")
    ax.legend(loc="center right", bbox_to_anchor=(1.0, 0.42), fontsize=6, handlelength=1.5)
    ax.text(3.0, 0.0062, "hop 0 = the call in flight at the post", fontsize=5.8, color=vs.INK2, ha="center")
    vs.save(fig, HERE / "fig")
    plt.close(fig)
    return dict(onset_iqr=q_on[1] - q_on[0], rd_med=q_rd, jpos=jpos, jneg=jneg, nunits=nunits,
                kIII=K["III"]["m"][1:3], kI=K["I"]["m"][1:3], pl=pls)


# ------------------------------------------------------------------------------------------- animation
def make_anim():
    vs.use()
    calls = sim_world(seed=11, n=8)
    fps, dur = 24, 18.0
    nf = int(fps * dur)
    t_start, t_end = -5.0, 60.0
    t_sweep0, t_sweep1, t_hold = 1.0, 13.0, 3.0
    fig = plt.figure(figsize=(1280 / 160, 720 / 160), dpi=160)
    axl = fig.add_axes([0.04, 0.24, 0.42, 0.55])
    axr = fig.add_axes([0.54, 0.24, 0.43, 0.55])
    fig.text(0.03, 0.94, "Field or coupling? Count the lag in model calls", fontsize=11, weight="bold", color=vs.INK)
    fig.text(0.03, 0.885, "Simulation on a synthetic call schedule (ticks = model calls, ~13 s apart as in regime III).",
             fontsize=8, color=vs.INK2)
    clock = fig.text(0.955, 0.94, "", ha="right", fontsize=9.5, family="monospace", color=vs.INK)
    fig.text(0.04, 0.82, "FIELD: one input hits everyone", fontsize=9, color=FIELD, weight="bold")
    fig.text(0.54, 0.82, "COUPLING: agents read each other", fontsize=9, color=COUP, weight="bold")
    capl = fig.text(0.04, 0.045, "", fontsize=8, color=vs.INK)
    capr = fig.text(0.54, 0.045, "", fontsize=8, color=vs.INK)
    tree = sim_coupling(calls)
    t_last = max(v[3] for v in tree.values() if v[0] is not None)

    def tnow(f):
        s = f / fps
        if s < t_sweep0:
            return t_start
        return min(t_end, t_start + (t_end - t_start) * (s - t_sweep0) / (t_sweep1 - t_sweep0))

    def frame(f):
        s = f / fps
        tc = tnow(f)
        fade = 1.0
        if s > t_sweep1 + t_hold:
            fade = max(0.0, 1 - (s - t_sweep1 - t_hold) / (dur - t_sweep1 - t_hold))
        u = tc if fade > 0.02 else -1e9
        for ax, kind in ((axl, "field"), (axr, "coupling")):
            ax.clear()
            draw_sim(ax, calls, kind, upto=u, fs=9)
            ax.set_xlim(t_start, t_end)
            if tc > t_start and fade > 0.02:
                ax.axvline(min(tc, ax.get_xlim()[1]), color=vs.INK, lw=0.7, alpha=0.5)
            ax.set_xlabel("time (s)", fontsize=8)
            ax.tick_params(labelsize=7.5)
        # field pending markers: agents still waiting for their next call
        if 10 <= tc and fade > 0.02:
            n = len(calls)
            for i, c in enumerate(calls):
                if tc < next_call(c, 10.0):
                    axl.plot([tc], [n - 1 - i], "o", mfc="white", mec=FIELD, ms=5, mew=1.0, zorder=6)
        capl.set_text("" if tc < 10 else "Everyone responds at its next call: all within ~1 call.\n"
                      "Village (G38): agents start the day within 9 s (IQR).")
        capr.set_text("" if tc < 10 else ("Each reader responds at its next call; lags add hop by hop.\n"
                                          "Village: $J_1>0$ at hop 1 in 45/71 units, none negative."))
        capl.set_alpha(fade); capr.set_alpha(fade)
        clock.set_text("t = %+5.0f s" % tc)
        return []

    anim = animation.FuncAnimation(fig, frame, frames=nf, interval=1000 / fps, blit=False)
    anim._save_count = nf
    vs.save_anim(anim, HERE / "anim", fps=fps, dpi=160, poster_frame=int(fps * (t_sweep1 + 1.0)))
    plt.close(fig)
    return t_last


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-anim", action="store_true")
    a = ap.parse_args()
    st = fig_static()
    print({k: (np.round(v, 4) if isinstance(v, (float, np.ndarray)) else v) for k, v in st.items()})
    if not a.no_anim:
        make_anim()


if __name__ == "__main__":
    main()
