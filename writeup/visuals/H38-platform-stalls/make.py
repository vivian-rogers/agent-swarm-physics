"""H38 visual: in the always-on regime, most activity co-activation is the scheduler (agents start and stop together).

    uv run python writeup/visuals/H38-platform-stalls/make.py            # fig + anim
    uv run python writeup/visuals/H38-platform-stalls/make.py --fig
    uv run python writeup/visuals/H38-platform-stalls/make.py --anim

Inputs (read only; round 1b on the fixed activity table; non-holdout by construction, asserted):
  data/processed/H38-platform-stalls/r1b/period_table.parquet
    E_raw / z_raw (excess equal-time gain over the block-shift null, and its z), E_mask_scaffold (after scaffold
    conditioning: off-schedule minutes dropped, not-started / finished / consolidating agent-minutes imputed),
    E_trim (DQ8 all-present window), f_mask_scaffold, f_trim.
Panel (a) and the animation are simulations of the same estimator (30-min block demeaning, g = 1 - 1/VR).
Outputs: fig.pdf/png, writeup/animations/H38-platform-stalls.mp4 + H38-platform-stalls_poster.png.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from matplotlib import animation  # noqa: E402
from matplotlib.colors import ListedColormap  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "writeup/visuals"))
sys.path.insert(0, str(ROOT / "infra/shared"))
import vstyle as vs  # noqa: E402
from common import load_holdout  # noqa: E402

D = ROOT / "data/processed/H38-platform-stalls/r1b/period_table.parquet"


def load():
    held = set(load_holdout()["goal_periods_held_out"])
    p = pl.read_parquet(D).sort("goal_no")
    assert not set(p["goal_no"].to_list()) & held
    return p


# ----------------------------------------------------------------------------------------- simulation
def simulate(N=12, days=3, L=300, J=0.4, h=0.0, start_sd=4.0, seed=38):
    """Agents on a scheduled day of L minutes. Each agent starts a few minutes after the operator's
    resume and stops a few minutes before the pause (the scheduler field). Inside, a kinetic Ising
    update with a weak coupling J to the mean of the others. Returns spins (days, L+40, N) in {0, 1},
    plus start/stop minute per (day, agent)."""
    rng = np.random.default_rng(seed)
    pad = 20
    T = L + 2 * pad
    x = np.zeros((days, T, N), dtype=np.int8)
    st = np.zeros((days, N), dtype=int)
    en = np.zeros((days, N), dtype=int)
    for d in range(days):
        st[d] = pad + np.abs(rng.normal(0, start_sd, N)).astype(int)
        en[d] = pad + L - np.abs(rng.normal(0, start_sd, N)).astype(int)
        s = rng.integers(0, 2, N)
        for t in range(T):
            on = (t >= st[d]) & (t < en[d])
            m = (s.sum() - s) / (N - 1) - 0.5
            p = 1 / (1 + np.exp(-(h + J * 4 * m)))
            flip = rng.random(N) < 0.25                     # persistence: a quarter of agents update per minute
            s = np.where(flip, (rng.random(N) < p).astype(int), s)
            x[d, t] = np.where(on, s, 0)
    return x, st, en, pad


def gain(x_days, windows, block=30):
    """H25/H38 estimator: +-1 spins, each agent's mean removed in 30-min blocks within the window, g = 1 - 1/VR."""
    num = den = 0.0
    for x, (a, b) in zip(x_days, windows):
        if b - a < block:
            continue
        s = 2.0 * x[a:b] - 1
        nb = (b - a) // block
        s = s[: nb * block].reshape(nb, block, -1)
        s = s - s.mean(1, keepdims=True)
        s = s.reshape(-1, s.shape[-1])
        num += (s.sum(1) ** 2).sum()
        den += (s ** 2).sum()
    vr = num / den if den > 0 else 1.0
    return 1 - 1 / vr


def sim_gains(x, st, en, pad, upto=None):
    days, T, N = x.shape
    raw, trim = [], []
    for d in range(days):
        tmax = T if upto is None else min(T, max(0, upto - d * T))
        if tmax <= 0:
            continue
        raw.append((x[d], (0, tmax)))
        a, b = int(st[d].max()), int(en[d].min())
        trim.append((x[d], (a, min(b, tmax))))
    gr = gain([q[0] for q in raw], [q[1] for q in raw]) if raw else 0.0
    gt = gain([q[0] for q in trim], [q[1] for q in trim]) if trim else 0.0
    return gr, gt


# ----------------------------------------------------------------------------------------- static
def make_fig():
    vs.use()
    p = load()
    x, st, en, pad = simulate()
    gr, gt = sim_gains(x, st, en, pad)
    fig = plt.figure(figsize=(vs.W["double"], 3.0))
    gs = fig.add_gridspec(2, 2, width_ratios=[1, 1.55], height_ratios=[1, 0.5], hspace=0.12, wspace=0.22)
    ax = fig.add_subplot(gs[0, 0]); mx = fig.add_subplot(gs[1, 0], sharex=ax); bx = fig.add_subplot(gs[:, 1])

    # (a) simulation: one scheduled day, raster + active count
    d = 0
    T = x.shape[1]
    cmap = ListedColormap(["#f4f4f4", vs.INK2])
    ax.imshow(x[d].T, aspect="auto", cmap=cmap, interpolation="nearest", extent=(0, T, x.shape[2], 0))
    a, b = int(st[d].max()), int(en[d].min())
    for lo, hi in ((0, a), (b, T)):
        ax.axvspan(lo, hi, color=vs.FIELD, alpha=0.28, lw=0)
        mx.axvspan(lo, hi, color=vs.FIELD, alpha=0.28, lw=0)
    ax.set_yticks([0.5, 11.5]); ax.set_yticklabels(["1", "12"])
    ax.set_ylabel("agent")
    ax.grid(False)
    ax.tick_params(labelbottom=False)
    ax.set_title("(a) simulation: one scheduled day", loc="left")
    M = x[d].sum(1)
    mx.plot(np.arange(T), M, color=vs.INK, lw=0.7)
    mx.set_ylim(0, 12.5); mx.set_yticks([0, 6, 12])
    mx.set_ylabel("active")
    mx.set_xlabel("minute of the day")
    mx.text(2, 12.3, "start together", fontsize=5.6, color=vs.INK2, va="top")
    mx.text(T - 2, 12.3, "stop together", fontsize=5.6, color=vs.INK2, va="top", ha="right")
    mx.text(T / 2, 12.3, "orange: outside the all-present window", fontsize=5.6, color=vs.INK2, va="top", ha="center")
    ax.text(0.99, 0.04, f"3 days: g whole day {gr:.2f}\n          trimmed {gt:.2f}", transform=ax.transAxes,
            ha="right", va="bottom", fontsize=6.0, color=vs.INK,
            bbox=dict(fc="white", ec="none", alpha=0.85, pad=1.2))

    # (b) village: decomposition of the excess co-activation gain, all 35 periods in time order
    xi = np.arange(p.height)
    E = p["E_raw"].to_numpy()
    Es = p["E_mask_scaffold"].to_numpy()
    sd = np.abs(E / p["z_raw"].to_numpy())
    resid = Es
    field = np.clip(E - Es, 0, None)
    bx.bar(xi, 2 * 1.96 * sd, bottom=-1.96 * sd, width=0.85, color=vs.NULL, alpha=0.5, lw=0, zorder=1)
    bx.bar(xi, resid, width=0.62, color=vs.COUPLING, zorder=2)
    bx.bar(xi, field, bottom=np.maximum(resid, 0), width=0.62, color=vs.FIELD, zorder=2)
    over = Es > E
    bx.scatter(xi[over], E[over], marker="_", s=30, color=vs.INK, lw=1.2, zorder=3)
    bx.axhline(0, color=vs.INK2, lw=0.6)
    regs = p["regime"].to_list()
    cut = [i for i in range(1, len(regs)) if regs[i] != regs[i - 1]]
    for c in cut:
        bx.axvline(c - 0.5, color=vs.MUTED, ls=":", lw=0.7)
    s3 = [i for i, r in enumerate(regs) if r == "III"]
    s1 = [i for i, r in enumerate(regs) if r == "I"]
    f3 = float(np.nanmedian(p.filter(pl.col("regime") == "III")["f_mask_scaffold"]))
    ft3 = float(np.nanmedian(p.filter(pl.col("regime") == "III")["f_trim"]))
    sig1 = p.filter((pl.col("regime") == "I") & (pl.col("z_raw") > 2))  # card: significant raw gain (z > 2)
    f1 = float(np.nanmedian(sig1["f_mask_scaffold"]))
    bx.text(14.5, 0.315, f"scheduler share $f$ = {f1:.2f}\n(median, significant periods)", ha="center", fontsize=6.2,
            color=vs.INK, va="bottom")
    bx.text(np.mean(s3), 0.50, f"$f$ = {f3:.2f}\n(trimmed: {ft3:.2f})", ha="center", fontsize=6.2,
            color=vs.INK, va="bottom")
    starts = [0] + cut
    ends = cut + [len(regs)]
    for s0, e0 in zip(starts, ends):
        lab = regs[s0] if regs[s0] != "I" and regs[s0] != "III" else f"regime {regs[s0]}"
        if e0 - s0 < 3:
            continue
        bx.text((s0 + e0 - 1) / 2, 0.625, lab, ha="center", fontsize=6.0 if "/" in lab else 6.5, color=vs.INK2)
    bx.set_xticks(xi)
    bx.set_xticklabels([str(g) for g in p["goal_no"].to_list()], fontsize=5.3, rotation=90)
    bx.set_xlim(-0.8, p.height - 0.2)
    bx.set_ylim(-0.11, 0.66)
    bx.set_xlabel("goal period (time order)")
    bx.set_ylabel("excess co-activation gain over the null")
    bx.set_title("(b) village: how much co-activation is the scheduler?", loc="left")
    h = [plt.Rectangle((0, 0), 1, 1, color=vs.FIELD, label="scheduler field (removed by scaffold conditioning)"),
         plt.Rectangle((0, 0), 1, 1, color=vs.COUPLING, label="left after conditioning"),
         plt.Rectangle((0, 0), 1, 1, color=vs.NULL, alpha=0.5, label="block-shift null (95%)"),
         Line2D([], [], marker="_", ls="", color=vs.INK, ms=6, label="raw gain, where conditioning raised it")]
    bx.legend(handles=h, loc="upper left", bbox_to_anchor=(0.0, 0.95), fontsize=6.0, handlelength=1.2)
    fig.subplots_adjust(left=0.07, right=0.99, top=0.92, bottom=0.17)
    vs.save(fig, HERE / "fig")
    plt.close(fig)
    print(f"sim g raw {gr:.3f} trim {gt:.3f}; f regIII median {f3:.3f} trim {ft3:.3f}; f regI (sig) {f1:.3f}")


# ----------------------------------------------------------------------------------------- animation
def make_anim():
    vs.use()
    x, st, en, pad = simulate()
    days, T, N = x.shape
    total = days * T
    nfr = 480
    per = total / (nfr - 48)                      # minutes per frame; last 2 s hold then fade
    flat = x.reshape(-1, N)
    edge = np.zeros(total, bool)
    for d in range(days):
        a, b = int(st[d].max()), int(en[d].min())
        edge[d * T: d * T + a] = True
        edge[d * T + b: (d + 1) * T] = True
    W = 240
    fig = plt.figure(figsize=(1280 / 160, 720 / 160), dpi=160)
    fig.text(0.5, 0.95, "Do agents act together, or does the scheduler switch them on together?", ha="center",
             fontsize=10.5)
    fig.text(0.5, 0.912, "simulation: 12 agents, weak coupling, operator resume/pause each day; "
             "orange shading = minutes outside the all-present window", ha="center", fontsize=6.8, color=vs.INK2)
    ax = fig.add_axes([0.06, 0.47, 0.60, 0.38]); mx = fig.add_axes([0.06, 0.13, 0.60, 0.26])
    bx = fig.add_axes([0.76, 0.13, 0.20, 0.72])
    cmap = ListedColormap(["#f4f4f4", vs.INK2])
    im = ax.imshow(np.zeros((N, W)), aspect="auto", cmap=cmap, vmin=0, vmax=1, interpolation="nearest",
                   extent=(-W, 0, N, 0))
    ax.set_yticks([0.5, N - 0.5]); ax.set_yticklabels(["1", str(N)]); ax.set_ylabel("agent")
    ax.grid(False); ax.tick_params(labelbottom=False)
    shade_a = ax.imshow(np.zeros((1, W)), aspect="auto", cmap=ListedColormap([(1, 1, 1, 0), (*matplotlib.colors.to_rgb(vs.FIELD), 0.35)]),
                        vmin=0, vmax=1, extent=(-W, 0, N, 0), interpolation="nearest", zorder=3)
    line, = mx.plot([], [], color=vs.INK, lw=0.8)
    shade_m = mx.imshow(np.zeros((1, W)), aspect="auto", cmap=ListedColormap([(1, 1, 1, 0), (*matplotlib.colors.to_rgb(vs.FIELD), 0.35)]),
                        vmin=0, vmax=1, extent=(-W, 0, 0, N + 0.5), interpolation="nearest", zorder=0)
    mx.set_xlim(-W, 0); mx.set_ylim(0, N + 0.5); mx.set_ylabel("active agents")
    mx.set_xlabel("minutes ago")
    bars = bx.bar([0, 1], [0, 0], color=vs.COUPLING, width=0.6)
    top = bx.bar([0], [0], bottom=[0], color=vs.FIELD, width=0.6)[0]
    bx.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=vs.FIELD, label="start/stop synchrony"),
                       plt.Rectangle((0, 0), 1, 1, color=vs.COUPLING, label="co-activation inside\nthe all-present window")],
              loc="upper right", fontsize=6.2)
    bx.set_xticks([0, 1]); bx.set_xticklabels(["whole day", "all-present\nwindow"], fontsize=7)
    bx.set_ylim(-0.05, 0.55); bx.set_ylabel("co-activation gain $g$ (so far)")
    bx.axhline(0, color=vs.INK2, lw=0.6)
    vals = [bx.text(i, 0, "", ha="center", va="bottom", fontsize=8) for i in (0, 1)]
    note = fig.text(0.86, 0.885, "", ha="center", va="center", fontsize=7, color=vs.INK2)
    clock = fig.text(0.985, 0.02, "", ha="right", fontsize=7, color=vs.INK2)
    gr_f, gt_f = sim_gains(x, st, en, pad)

    def frame(f):
        t = min(total, int((f + 1) * per))
        lo = t - W
        idx = np.arange(lo, t)
        ok = idx >= 0
        img = np.zeros((N, W)); sh = np.zeros((1, W)); M = np.full(W, np.nan)
        img[:, ok] = flat[idx[ok]].T
        sh[0, ok] = edge[idx[ok]]
        M[ok] = flat[idx[ok]].sum(1)
        alpha = 1.0 if f < nfr - 24 else max(0.0, (nfr - 1 - f) / 24)
        im.set_data(img); im.set_alpha(alpha)
        shade_a.set_data(sh); shade_m.set_data(sh); shade_a.set_alpha(alpha); shade_m.set_alpha(alpha)
        line.set_data(np.arange(-W, 0), M); line.set_alpha(alpha)
        gr, gt = sim_gains(x, st, en, pad, upto=t)
        for b_ in bars:
            b_.set_height(gt); b_.set_alpha(alpha)
        top.set_y(max(gt, 0)); top.set_height(max(gr - max(gt, 0), 0)); top.set_alpha(alpha)
        for v_, tx in zip((gr, gt), vals):
            tx.set_position((tx.get_position()[0], max(v_, 0) + 0.008)); tx.set_text(f"{v_:.2f}"); tx.set_alpha(alpha)
        share = (gr - gt) / gr if gr > 0.02 else np.nan
        note.set_text(f"share from start/stop synchrony: {share:.0%}" if np.isfinite(share) else "")
        note.set_alpha(alpha)
        day = min(days, t // T + 1)
        clock.set_text(f"day {day} of {days}, minute {t % T if t < total else T:3d}")
        return []

    anim = animation.FuncAnimation(fig, frame, frames=nfr, blit=False)
    vs.save_anim(anim, HERE / "anim", fps=24, dpi=160, poster_frame=nfr - 30)
    plt.close(fig)
    print(f"anim final g raw {gr_f:.3f} trimmed {gt_f:.3f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--fig", action="store_true")
    ap.add_argument("--anim", action="store_true")
    a = ap.parse_args()
    both = not (a.fig or a.anim)
    if a.fig or both:
        make_fig()
    if a.anim or both:
        make_anim()
