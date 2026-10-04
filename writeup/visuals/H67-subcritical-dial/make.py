"""H67 + H25 visual: the swarm sits far below the critical point of its talk loop.

    uv run python writeup/visuals/H67-subcritical-dial/make.py            # fig + anim
    uv run python writeup/visuals/H67-subcritical-dial/make.py --fig      # static only
    uv run python writeup/visuals/H67-subcritical-dial/make.py --anim     # animation only

Inputs (read only, non-holdout by construction; asserted again here):
  data/processed/H67-lagged-criticality-dial/results/periods.parquet   per-period g_lag (RE pool, 95% CI), g_eq
  data/processed/H67-lagged-criticality-dial/results/units.parquet     per-unit shift-null q95
  data/processed/H25-criticality-dial/r1b/dial_daily.parquet           H25 daily Curie-Weiss dial (round 1b)
Outputs: fig.pdf/png (writeup figure), anim.mp4 + anim_poster.png (simulation).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.transforms as mtrans  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from matplotlib import animation  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "writeup/visuals"))
sys.path.insert(0, str(ROOT / "infra/shared"))
import vstyle as vs  # noqa: E402
from common import holdout_mask, load_holdout  # noqa: E402

H67 = ROOT / "data/processed/H67-lagged-criticality-dial/results"
H25 = ROOT / "data/processed/H25-criticality-dial/r1b"
REG_C = {"I": vs.C["green"], "II": vs.C["pink"], "III": vs.C["blue"]}
REG_M = {"I": "s", "II": "D", "III": "o"}


def load():
    held = set(load_holdout()["goal_periods_held_out"])
    p = pl.read_parquet(H67 / "periods.parquet").sort("goal_no")
    assert not set(p["goal_no"].to_list()) & held, "held-out period in H67 periods"
    u = pl.read_parquet(H67 / "units.parquet").filter(pl.col("ok"))
    q = u.group_by("goal_no").agg(pl.col("shift_g_q95").median().alias("null_q95"))
    p = p.join(q, on="goal_no", how="left")
    d = pl.read_parquet(H25 / "dial_daily.parquet").filter(pl.col("variant") == "auto")
    mask = holdout_mask(d["pt_date"].cast(pl.Utf8).to_list(), d["goal_no"].to_list())
    assert not any(mask), "held-out day in H25 dial"
    return p, d


# ----------------------------------------------------------------------------------------- static figure
def make_fig():
    vs.use()
    p, d = load()
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(vs.W["double"], 2.75), gridspec_kw={"width_ratios": [1.0, 1.25]})

    # (a) the dial: amplification chi = 1/(1-g) against loop gain g
    g = np.linspace(0, 0.986, 400)
    ax.axvspan(1.0, 1.12, color=vs.GRID, lw=0, zorder=0)
    ax.text(1.06, 0.5, "runaway\n(supercritical)", rotation=90, ha="center", va="center", fontsize=6.5,
            color=vs.INK2, transform=mtrans.blended_transform_factory(ax.transData, ax.transAxes))
    ax.axvline(1.0, color=vs.INK2, ls="--", lw=1.0)
    ax.plot(g, 1 / (1 - g), color=vs.INK, lw=1.3, zorder=2)
    ax.text(0.86, 10, r"$\chi = 1/(1-g)$", fontsize=7.5, color=vs.INK, ha="right")
    # every period on the curve
    for r in ("I", "II", "III"):
        s = p.filter(pl.col("regime") == r)
        gg, lo, hi = s["g"].to_numpy(), s["g_lo"].to_numpy(), s["g_hi"].to_numpy()
        chi = 1 / (1 - gg)
        ax.errorbar(gg, chi, xerr=[gg - lo, hi - gg], fmt=REG_M[r], ms=3.2, mfc=REG_C[r], mec="white", mew=0.4,
                    ecolor=REG_C[r], elinewidth=0.7, capsize=0, alpha=0.9, zorder=3, label=f"regime {r}")
    # simulation gains used in the animation
    for gs in (0.13, 0.6, 0.95):
        ax.plot(gs, 1 / (1 - gs), "o", ms=4.5, mfc="none", mec=vs.MUTED, mew=0.9, zorder=4)
    gmax = p["g"].max()
    ax.annotate(f"35 periods: $g_{{lag}}\\leq${gmax:.2f}\n$\\chi\\leq${1/(1-gmax):.2f}", (0.24, 1.31),
                xytext=(0.45, 1.0), fontsize=6.5, color=vs.INK,
                arrowprops=dict(arrowstyle="-", color=vs.INK2, lw=0.6))
    # H25 daily equal-time dial (282 days per channel) as strips near the top
    tr = mtrans.blended_transform_factory(ax.transData, ax.transAxes)
    rng = np.random.default_rng(1)
    for k, (ch, y0) in enumerate((("activity", 0.90), ("talk", 0.80))):
        v = d.filter(pl.col("channel") == ch)
        gv = v["g"].to_numpy()
        gv = gv[np.isfinite(gv)]
        ax.scatter(gv, y0 + rng.uniform(-0.025, 0.025, len(gv)), s=1.2, color=vs.MUTED, alpha=0.6, lw=0,
                   transform=tr, zorder=2)
        med = np.median(gv)
        ax.plot([med, med], [y0 - 0.04, y0 + 0.04], color=vs.INK, lw=1.3, transform=tr, zorder=3)
        hi = v["hi"].max()
        ax.plot([hi], [y0], marker="|", ms=7, color=vs.INK2, mew=1.0, transform=tr, zorder=3)
        ax.text(-0.02, y0, f"H25 {ch}", transform=tr, ha="right", va="center", fontsize=6.0, color=vs.INK2)
    ax.text(0.50, 0.725, "| largest daily upper bound", transform=tr, fontsize=5.6, color=vs.INK2, va="center")
    ax.set_yscale("log")
    ax.set_ylim(0.93, 60)
    ax.set_xlim(-0.02, 1.12)
    ax.set_yticks([1, 1.31, 2, 5, 10, 20, 50])
    ax.set_yticklabels(["1", "1.31", "2", "5", "10", "20", "50"])
    ax.minorticks_off()
    ax.set_xlabel("loop gain $g$ (offspring per talk message)")
    ax.set_ylabel(r"amplification of a push $\chi$")
    ax.set_title("(a) distance to the critical point", loc="left")
    hr = [Line2D([], [], marker=REG_M[r], ls="", mfc=REG_C[r], mec="white", ms=4.5, label=f"regime {r}")
          for r in ("I", "II", "III")]
    hr.append(Line2D([], [], marker="o", ls="", mfc="none", mec=vs.MUTED, mew=0.9, ms=4.5,
                     label="simulated swarm\n(animation)"))
    ax.legend(handles=hr, loc="center left", bbox_to_anchor=(0.0, 0.47), handletextpad=0.2, borderaxespad=0.2)

    # (b) per-period read-out gain in time order, against the shift null and the equal-time dial
    x = np.arange(p.height)
    regs = p["regime"].to_list()
    nq = p["null_q95"].to_numpy()
    bx.bar(x, 2 * nq, bottom=-nq, width=0.8, color=vs.NULL, alpha=0.45, lw=0, zorder=1)
    bx.axhline(0, color=vs.INK2, lw=0.6, zorder=1)
    bx.scatter(x, p["g_eq"].to_numpy(), marker="D", s=9, facecolor="none", edgecolor=vs.FIELD, lw=0.8, zorder=2)
    for r in ("I", "II", "III"):
        m = np.array([q == r for q in regs])
        gg, lo, hi = p["g"].to_numpy()[m], p["g_lo"].to_numpy()[m], p["g_hi"].to_numpy()[m]
        bx.errorbar(x[m], gg, yerr=[gg - lo, hi - gg], fmt=REG_M[r], ms=3.2, mfc=REG_C[r], mec="white", mew=0.4,
                    ecolor=REG_C[r], elinewidth=0.8, capsize=0, zorder=3)
    # regime blocks
    edges = [i for i in range(1, len(regs)) if regs[i] != regs[i - 1]]
    for e in edges:
        bx.axvline(e - 0.5, color=vs.MUTED, ls=":", lw=0.7)
    starts = [0] + edges
    ends = edges + [len(regs)]
    for s0, e0 in zip(starts, ends):
        bx.text((s0 + e0 - 1) / 2, 0.47, f"regime {regs[s0]}", ha="center", fontsize=6.5, color=vs.INK2)
    s3 = starts[-1]
    uu = pl.read_parquet(H67 / "units.parquet").filter(pl.col("ok") & (pl.col("regime") == "III"))
    med3 = float(uu["g"].median())  # card: regime-III unit median 0.13
    bx.plot([s3 - 0.4, len(regs) - 0.6], [med3, med3], color=vs.COUPLING, ls="--", lw=0.8, zorder=2)
    bx.text(len(regs) - 0.5, 0.415, f"unit median {med3:.2f} (dashed)", ha="right", fontsize=6.0, color=vs.COUPLING)
    i40 = int(np.where(p["goal_no"].to_numpy() == 40)[0][0])
    bx.annotate("#40 merged room", (i40, p["g"][i40] - 0.115), xytext=(i40 - 0.4, -0.175), fontsize=5.8,
                color=vs.INK2, arrowprops=dict(arrowstyle="-", color=vs.MUTED, lw=0.6))
    bx.set_xticks(x)
    bx.set_xticklabels([f"{g}" for g in p["goal_no"].to_list()], fontsize=5.3, rotation=90)
    bx.set_xlim(-0.8, len(regs) - 0.2)
    bx.set_ylim(-0.27, 0.52)
    bx.set_xlabel("goal period (time order)")
    bx.set_ylabel(r"read-out loop gain $g_{lag}$")
    bx.set_title("(b) where the gain lives", loc="left")
    h = [Line2D([], [], marker="o", ls="", mfc=vs.COUPLING, mec="white", ms=4, label=r"$g_{lag}$ (95% CI)"),
         Line2D([], [], marker="D", ls="", mfc="none", mec=vs.FIELD, ms=3.5, label="equal-time dial $g_{eq}$"),
         plt.Rectangle((0, 0), 1, 1, color=vs.NULL, alpha=0.45, label="shift null (95%)")]
    bx.legend(handles=h, loc="lower left", bbox_to_anchor=(0.0, 0.0), ncol=3, handletextpad=0.3, columnspacing=0.8, handlelength=1.3, fontsize=6.3)
    fig.tight_layout(w_pad=1.2)
    vs.save(fig, HERE / "fig")
    plt.close(fig)
    print("fig: max period g", gmax, "chi", 1 / (1 - gmax), "regIII median", med3)


# ----------------------------------------------------------------------------------------- animation
def circular_branching(g, mu, T, N, rng):
    """Discrete-time branching swarm on a circular clock of T hops (so the movie loops exactly).
    Seeds (external pushes) arrive Poisson(mu) per hop at random agents; every talk event makes
    Poisson(g) offspring one hop later at other random agents. Returns per-hop lists of
    (agent, parent_agent or -1)."""
    ev = [[] for _ in range(T)]
    n_seed = rng.poisson(mu * T)
    for _ in range(n_seed):
        t = int(rng.integers(T))
        a = int(rng.integers(N))
        gen = [(a, -1)]
        tt = t
        while gen and len(gen) < 4000:
            for e in gen:
                ev[tt % T].append(e)
            nxt = []
            for a0, _ in gen:
                for _ in range(rng.poisson(g)):
                    b = int(rng.integers(N - 1))
                    b = b + (b >= a0)
                    nxt.append((b, a0))
            gen = nxt
            tt += 1
    return ev


def make_anim():
    vs.use()
    T, N, mu = 480, 24, 0.5
    gains = [(0.13, "g = 0.13  (village, regime III)"), (0.60, "g = 0.60"), (0.95, "g = 0.95  (near critical)")]
    rng = np.random.default_rng(67)
    sims = [circular_branching(gv, mu, T, N, rng) for gv, _ in gains]
    counts = [np.array([len(e) for e in s]) for s in sims]
    seeds = [np.array([sum(1 for _, par in e if par < 0) for e in s]) for s in sims]
    ang = np.linspace(0, 2 * np.pi, N, endpoint=False) + np.pi / 2
    xy = np.c_[np.cos(ang), np.sin(ang)]
    W = 120  # hops shown in the trace
    ymax = int(max(c.max() for c in counts) * 1.08) + 1

    fig = plt.figure(figsize=(1280 / 160, 720 / 160), dpi=160)
    fig.patch.set_facecolor("white")
    fig.text(0.5, 0.955, "Same pushes, three loop gains: how much does the swarm amplify?", ha="center",
             fontsize=10.5, color=vs.INK)
    fig.text(0.5, 0.915, "simulation: branching talk swarm, 24 agents; orange = external push, blue = reply caused by reading",
             ha="center", fontsize=7, color=vs.INK2)
    rings, traces, meas = [], [], []
    for k, (gv, lab) in enumerate(gains):
        axr = fig.add_axes([0.035 + k * 0.325, 0.40, 0.29, 0.46])
        axr.set_xlim(-1.35, 1.35); axr.set_ylim(-1.3, 1.3); axr.set_aspect("equal"); axr.axis("off")
        axr.scatter(xy[:, 0], xy[:, 1], s=26, color="#f2f2f2", edgecolor=vs.MUTED, lw=0.5, zorder=1)
        axr.set_title(lab, fontsize=8.5, color=vs.INK, pad=2)
        chi = 1 / (1 - gv)
        axr.text(0, 0.12, f"χ = {chi:.2f}", ha="center", va="center", fontsize=11, color=vs.INK, zorder=6,
                 bbox=dict(fc="white", ec="none", alpha=0.85, pad=1.5))
        axr.text(0, -0.18, "talk per push", ha="center", va="center", fontsize=6.5, color=vs.INK2, zorder=6,
                 bbox=dict(fc="white", ec="none", alpha=0.85, pad=1.0))
        flash = axr.scatter(xy[:, 0], xy[:, 1], s=np.zeros(N), color=vs.COUPLING, zorder=3, lw=0)
        seed = axr.scatter(xy[:, 0], xy[:, 1], s=np.zeros(N), color=vs.FIELD, zorder=4, lw=0)
        links = [axr.plot([], [], color=vs.COUPLING, lw=0.7, alpha=0.55, zorder=2)[0] for _ in range(40)]
        rings.append((flash, seed, links))
        axt = fig.add_axes([0.06 + k * 0.325, 0.15, 0.255, 0.20])
        axt.set_xlim(-W, 0); axt.set_ylim(0, ymax)
        axt.axhline(mu, color=vs.FIELD, lw=1.0, ls="--")
        axt.axhline(mu * chi, color=vs.COUPLING, lw=1.0, ls=":")
        axt.set_xlabel("hops ago (one hop = one read-out call)", fontsize=6.5)
        if k == 0:
            axt.set_ylabel("talk events per hop", fontsize=6.5)
        axt.tick_params(labelsize=6)
        line, = axt.plot([], [], color=vs.INK, lw=0.9)
        traces.append(line)
        meas.append(axr.text(0, -0.42, "", ha="center", va="center", fontsize=6.5, color=vs.INK2, zorder=6,
                             bbox=dict(fc="white", ec="none", alpha=0.85, pad=1.0)))
    fig.text(0.5, 0.018, "dashed: push rate   dotted: expected talk rate = push rate × χ", ha="center",
             fontsize=6.8, color=vs.INK2)
    clock = fig.text(0.985, 0.018, "", ha="right", fontsize=7, color=vs.INK2)
    decay = 0.78

    state = [np.zeros(N) for _ in gains]
    sstate = [np.zeros(N) for _ in gains]
    # warm the flash state so frame 0 matches the end of the loop
    for k in range(len(gains)):
        for t in range(T - 12, T):
            state[k] *= decay; sstate[k] *= decay
            for a, par in sims[k][t]:
                (sstate if par < 0 else state)[k][a] += 1

    def frame(t):
        for k in range(len(gains)):
            flash, seed, links = rings[k]
            state[k] *= decay; sstate[k] *= decay
            evs = sims[k][t % T]
            for a, par in evs:
                (sstate if par < 0 else state)[k][a] += 1
            flash.set_sizes(np.minimum(state[k], 5) * 60)
            seed.set_sizes(np.minimum(sstate[k], 4) * 70)
            kids = [(a, par) for a, par in evs if par >= 0][:len(links)]
            for j, ln in enumerate(links):
                if j < len(kids):
                    a, par = kids[j]
                    ln.set_data([xy[par, 0], xy[a, 0]], [xy[par, 1], xy[a, 1]])
                else:
                    ln.set_data([], [])
            idx = (np.arange(t - W + 1, t + 1)) % T
            traces[k].set_data(np.arange(-W + 1, 1), counts[k][idx])
            ns = seeds[k][:t + 1].sum(); ne = counts[k][:t + 1].sum()
            meas[k].set_text(f"so far: {ns} pushes $\\rightarrow$ {ne} talk events ($\\times${ne / max(ns, 1):.2f})")
        clock.set_text(f"hop {t + 1:3d} / {T}")
        return []

    anim = animation.FuncAnimation(fig, frame, frames=T, blit=False)
    vs.save_anim(anim, HERE / "anim", fps=24, dpi=160, poster_frame=T - 1)
    plt.close(fig)
    for k, (gv, _) in enumerate(gains):
        print(f"g={gv}: mean talk/hop {counts[k].mean():.2f} (expected {mu / (1 - gv):.2f}), max {counts[k].max()}")


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
