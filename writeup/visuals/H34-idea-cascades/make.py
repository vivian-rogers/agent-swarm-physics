"""H34 visual: idea cascades are strongly subcritical (R ~ 0.2) and heavier-tailed than one branching law.

    uv run python writeup/visuals/H34-idea-cascades/make.py            # fig + anim
    uv run python writeup/visuals/H34-idea-cascades/make.py --fig
    uv run python writeup/visuals/H34-idea-cascades/make.py --anim

Inputs (read only; round 1b = context-ledger visibility; non-holdout by construction, asserted):
  data/processed/H34-idea-cascades/r1b/results/period_table.parquet   R-hat, CI, k-hat, N_room per period (cls ALL)
  data/processed/H34-idea-cascades/r1b/G<NN>/trees.parquet            exposure-tree sizes (hashed ideas; no text)
  data/processed/H67-lagged-criticality-dial/results/periods.parquet  regime label per goal period
The GW-NB size law is H34's own (hypotheses/H34-idea-cascades/analysis/h34stats.py, imported read-only).
Outputs: fig.pdf/png (double column), fig_col.pdf (single column, a over b, for writeup/papers/thermodynamics), writeup/animations/H34-idea-cascades.mp4 + H34-idea-cascades_poster.png (simulation).
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
from matplotlib.collections import LineCollection  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "writeup/visuals"))
sys.path.insert(0, str(ROOT / "infra/shared"))
sys.path.insert(0, str(ROOT / "hypotheses/H34-idea-cascades/analysis"))
import vstyle as vs  # noqa: E402
import h34stats as S  # noqa: E402
from common import load_holdout  # noqa: E402

D = ROOT / "data/processed/H34-idea-cascades/r1b"
REG_C = {"I": vs.C["green"], "II": vs.C["pink"], "III": vs.C["blue"]}
REG_M = {"I": "s", "II": "D", "III": "o"}


def load():
    held = set(load_holdout()["goal_periods_held_out"])
    p = pl.read_parquet(D / "results/period_table.parquet").filter(pl.col("cls") == "ALL").sort("goal")
    assert not set(p["goal"].to_list()) & held
    reg = pl.read_parquet(ROOT / "data/processed/H67-lagged-criticality-dial/results/periods.parquet")
    reg = dict(zip(reg["goal_no"].to_list(), reg["regime"].to_list()))
    p = p.with_columns(pl.col("goal").replace_strict(reg, default="I").alias("regime"))
    return p


def ccdf(sizes, smax):
    s = np.arange(1, smax + 1)
    n = len(sizes)
    c = np.array([(sizes >= x).sum() for x in s])
    return s, c / n, c, n


def wilson(k, n, z=1.96):
    p = k / n
    den = 1 + z * z / n
    mid = (p + z * z / (2 * n)) / den
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return mid - half, mid + half


# ----------------------------------------------------------------------------------------- static
def panel_a(ax, p):
    """(a) cascade-size CCDF, #51 against the homogeneous branching law and the critical law."""
    for g in p["goal"].to_list():
        if g == 51:
            continue
        sz = pl.read_parquet(D / f"G{g:02d}/trees.parquet")["size"].to_numpy()
        s, c, _, _ = ccdf(sz, int(sz.max()))
        ax.plot(s, c, color=vs.C["sky"], lw=0.5, alpha=0.45, zorder=1)
    r = p.filter(pl.col("goal") == 51).to_dicts()[0]
    sz = pl.read_parquet(D / "G51/trees.parquet")["size"].to_numpy()
    N = max(int(r["N_room"]), int(sz.max()))
    pm = S.nb_gw_pmf_trunc(r["R"], r["k"], N)
    rng = np.random.default_rng(34)
    sims = rng.multinomial(len(sz), pm, size=2000)
    cc = np.cumsum(sims[:, ::-1], axis=1)[:, ::-1] / len(sz)
    lo, hi = np.percentile(cc, [2.5, 97.5], axis=0)
    xs = np.arange(1, N + 1)
    lo = np.where(lo > 0, lo, np.nan)
    ax.fill_between(xs, np.nan_to_num(lo, nan=1e-7), hi, color=vs.NULL, alpha=0.6, lw=0, zorder=2, step=None)
    ax.plot(xs, np.cumsum(pm[::-1])[::-1], color=vs.INK2, lw=0.8, ls="--", zorder=3)
    s, c, k, n = ccdf(sz, int(sz.max()))
    wl, wh = wilson(k, n)
    ok = c > 0
    ax.errorbar(s[ok], c[ok], yerr=[np.clip(c[ok] - wl[ok], 0, None), np.clip(wh[ok] - c[ok], 0, None)], fmt="o", ms=3, color=vs.COUPLING, mec="white",
                mew=0.3, elinewidth=0.8, capsize=0, zorder=4)
    x = np.arange(1, 30)
    ax.plot(x, x ** -0.5, color=vs.INK, ls=":", lw=1.1, zorder=3)
    ax.text(5, 5 ** -0.5 * 0.7, r"critical law $P(s)\propto s^{-3/2}$ ($R=1$)", fontsize=6.3, va="top", ha="center", color=vs.INK)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(0.9, 32); ax.set_ylim(1.2e-5, 1.6)
    ax.set_xticks([1, 2, 5, 10, 20]); ax.set_xticklabels(["1", "2", "5", "10", "20"]); ax.minorticks_off()
    ax.set_xlabel("cascade size $s$ (agents in one exposure tree)")
    ax.set_ylabel(r"$P(S \geq s)$")
    ax.set_title("(a) cascade sizes, #51 (25-agent room)", loc="left")
    h = [Line2D([], [], marker="o", ls="", color=vs.COUPLING, mec="white", ms=4,
                label=f"#51 observed ({len(sz):,} trees), $\\hat R$ = {r['R']:.2f}"),
         (plt.Rectangle((0, 0), 1, 1, color=vs.NULL, alpha=0.6), Line2D([], [], color=vs.INK2, ls="--", lw=0.8)),
         Line2D([], [], color=vs.C["sky"], lw=0.6, label="31 other periods")]
    ax.legend(h, [h[0].get_label(), f"one branching law, GW-NB($\\hat R$, $\\hat k$={r['k']:.1f}), 95%",
                  "31 other periods"], loc="lower left", handlelength=1.6)
    return r, sz, pm, N


def panel_b(bx, p):
    """(b) branching ratio of every period against the critical point."""
    for rg in ("I", "II", "III"):
        v = p.filter(pl.col("regime") == rg)
        xN = v["N_room"].to_numpy() * np.exp(np.random.default_rng(7).uniform(-0.04, 0.04, v.height))
        R, Rl, Rh = v["R"].to_numpy(), v["R_lo"].to_numpy(), v["R_hi"].to_numpy()
        bx.errorbar(xN, R, yerr=[R - Rl, Rh - R], fmt=REG_M[rg], ms=3.4, mfc=REG_C[rg], mec="white", mew=0.4,
                    ecolor=REG_C[rg], elinewidth=0.8, capsize=0, zorder=3, label=f"regime {rg}")
    bx.axhspan(1.0, 1.2, color=vs.GRID, lw=0, zorder=0)
    bx.axhline(1.0, color=vs.INK2, ls="--", lw=1.0)
    bx.text(3.6, 1.04, "critical $R = 1$: ideas spread without limit", fontsize=6.3, color=vs.INK2, va="bottom")
    med = float(p["R"].median())
    bx.axhline(med, color=vs.COUPLING, lw=0.7, ls=":")
    bx.text(29, med + 0.025, f"median {med:.2f}", ha="right", fontsize=6.3, color=vs.COUPLING)
    bx.text(3.6, 0.72, f"32/32 periods: upper 95% bound < 1\n$\\hat R$ {p['R'].min():.2f}–{p['R'].max():.2f}; "
            f"mean tree $1/(1-\\hat R)\\approx${1/(1-med):.2f} agents", fontsize=6.3, color=vs.INK, va="center")
    bx.set_xscale("log")
    bx.set_xticks([4, 6, 10, 15, 25]); bx.set_xticklabels(["4", "6", "10", "15", "25"])
    bx.minorticks_off()
    bx.set_xlim(3.4, 30); bx.set_ylim(0, 1.15)
    bx.set_xlabel("room size $N$ (agents)")
    bx.set_ylabel(r"idea branching ratio $\hat R$ (95% CI)")
    bx.set_title("(b) every period far below $R = 1$", loc="left")
    bx.legend(loc="center left", bbox_to_anchor=(0.0, 0.38), handletextpad=0.2)
    return med


def make_fig():
    vs.use()
    p = load()
    # double column: a | b
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(vs.W["double"], 2.8), gridspec_kw={"width_ratios": [1.15, 1]})
    r, sz, pm, N = panel_a(ax, p)
    med = panel_b(bx, p)
    fig.tight_layout(w_pad=1.4)
    vs.save(fig, HERE / "fig")
    plt.close(fig)
    # single column: a over b
    fig, (ax, bx) = plt.subplots(2, 1, figsize=(vs.W["single"], 4.9))
    panel_a(ax, p)
    panel_b(bx, p)
    fig.tight_layout(h_pad=1.2)
    vs.save(fig, HERE / "fig_col")
    plt.close(fig)
    p5_obs = (sz >= 5).mean(); p5_gw = pm[4:].sum()
    print(f"#51 R {r['R']:.3f} k {r['k']:.2f} N {N}; P(s>=5) obs {p5_obs:.4f} vs GW-NB {p5_gw:.4f}; median R {med:.3f}")


# ----------------------------------------------------------------------------------------- animation
def grow_tree(R, k, cap, rng):
    """GW tree with NB(mean R, dispersion k) offspring, capped at `cap` agents (one room).
    Returns list of generations, each a list of parent indices into the previous generation."""
    gens = [[-1]]
    total = 1
    while total < cap:
        prev = gens[-1]
        kids = []
        for i in range(len(prev)):
            o = rng.negative_binomial(k, k / (k + R))
            for _ in range(o):
                if total + len(kids) >= cap:
                    break
                kids.append(i)
        if not kids:
            break
        gens.append(kids)
        total += len(kids)
    return gens


def layout(gens, w, top, dy):
    """x, y per node and parent index (flat)."""
    xs, ys, par = [], [], []
    prev_idx = []
    for gi, g in enumerate(gens):
        n = len(g)
        order = sorted(range(n), key=lambda j: g[j])
        cur = [0] * n
        for rank, j in enumerate(order):
            x = (rank + 0.5) / n * w - w / 2
            cur[j] = len(xs)
            xs.append(x); ys.append(top - gi * dy)
            par.append(prev_idx[g[j]] if gi > 0 else -1)
        prev_idx = cur
    return np.array(xs), np.array(ys), np.array(par)


def make_anim():
    vs.use()
    p = load()
    r51 = p.filter(pl.col("goal") == 51).to_dicts()[0]
    k, cap = 1.3, 25
    Rs = [(0.2, "R = 0.2   (the village: $\\hat R$ 0.09–0.40)"), (1.0, "R = 1   (critical)")]
    rng = np.random.default_rng(3434)
    rows, cols = 3, 8
    nslot = rows * cols
    T, gen_frames = 480, 7
    start = np.sort(rng.uniform(0, 230, nslot)).astype(int)  # seed times (frames)
    forests = []
    for R, _ in Rs:
        trees = [grow_tree(R, k, cap, rng) for _ in range(nslot)]
        forests.append(trees)

    fig = plt.figure(figsize=(1280 / 160, 720 / 160), dpi=160)
    fig.text(0.5, 0.955, "Idea cascades: who picks up a new idea after reading it?", ha="center", fontsize=10.5)
    fig.text(0.5, 0.918, f"simulation: branching trees, offspring NB(mean R, k = {k}), capped at a {cap}-agent room;"
             " orange = inventor, blue = adopter after reading", ha="center", fontsize=6.8, color=vs.INK2)
    panels = []
    for pi, (R, lab) in enumerate(Rs):
        axp = fig.add_axes([0.03 + pi * 0.49, 0.30, 0.45, 0.57])
        axp.set_xlim(0, cols); axp.set_ylim(0, rows); axp.axis("off")
        axp.set_title(lab, fontsize=8.5, pad=2)
        lc = LineCollection([], colors=vs.COUPLING, linewidths=0.6, alpha=0.8)
        axp.add_collection(lc)
        sc_root = axp.scatter([], [], s=14, color=vs.FIELD, zorder=3, lw=0)
        sc = axp.scatter([], [], s=6, color=vs.COUPLING, zorder=3, lw=0)
        lay = []
        for j, tr in enumerate(forests[pi]):
            cx, cy = j % cols + 0.5, rows - (j // cols) - 0.12
            x, y, par = layout(tr, 0.88, cy, 0.85 / max(len(tr), 6))
            gen = np.concatenate([[gi] * len(g) for gi, g in enumerate(tr)])
            lay.append((x + cx, y, par, gen))
        cnt = axp.text(cols / 2, -0.12, "", ha="center", fontsize=7, color=vs.INK2)
        panels.append((lc, sc_root, sc, lay, cnt))
    # bottom: CCDF of the real #51 trees vs the two laws
    axc = fig.add_axes([0.30, 0.075, 0.40, 0.17])
    sz = pl.read_parquet(D / "G51/trees.parquet")["size"].to_numpy()
    s, c, _, _ = ccdf(sz, int(sz.max()))
    for R, ls, lab in ((0.2, "-", "R = 0.2"), (1.0, "--", "R = 1")):
        pm = S.nb_gw_pmf_trunc(R, k, cap)
        axc.plot(np.arange(1, cap + 1), np.cumsum(pm[::-1])[::-1], color=vs.INK2, ls=ls, lw=1.0, label=lab)
    axc.plot(s, c, "o", ms=2.5, color=vs.COUPLING, label=f"village #51 ({len(sz):,} trees)")
    axc.set_xscale("log"); axc.set_yscale("log"); axc.set_ylim(1e-5, 1.5); axc.set_xlim(0.9, 30)
    axc.tick_params(labelsize=5.5)
    axc.set_xticks([1, 2, 5, 10, 20]); axc.set_xticklabels(["1", "2", "5", "10", "20"]); axc.minorticks_off()
    fig.add_artist(Line2D([0.505, 0.505], [0.31, 0.88], color=vs.GRID, lw=1.0))
    axc.set_xlabel("cascade size $s$", fontsize=6.5, labelpad=1)
    axc.set_ylabel(r"$P(S\geq s)$", fontsize=6.5)
    axc.legend(fontsize=5.5, loc="center left", bbox_to_anchor=(1.02, 0.5))
    clock = fig.text(0.985, 0.02, "", ha="right", fontsize=7, color=vs.INK2)
    fade0 = T - 48

    def frame(t):
        alpha = 1.0 if t < fade0 else max(0.0, 1 - (t - fade0) / 40)
        for pi, (lc, sc_root, sc, lay, cnt) in enumerate(panels):
            segs, pts, roots, sizes_done, alive = [], [], [], [], 0
            for j, (x, y, par, gen) in enumerate(lay):
                if t < start[j]:
                    continue
                gshown = (t - start[j]) // gen_frames
                vis = gen <= gshown
                for i in np.where(vis)[0]:
                    if par[i] < 0:
                        roots.append((x[i], y[i]))
                    else:
                        pts.append((x[i], y[i]))
                        segs.append([(x[par[i]], y[par[i]]), (x[i], y[i])])
                if gshown >= gen.max():
                    sizes_done.append(len(gen))
                else:
                    alive += 1
            lc.set_segments(segs); lc.set_alpha(0.8 * alpha)
            sc.set_offsets(np.array(pts) if pts else np.empty((0, 2))); sc.set_alpha(alpha)
            sc_root.set_offsets(np.array(roots) if roots else np.empty((0, 2))); sc_root.set_alpha(alpha)
            if sizes_done:
                sd = np.array(sizes_done)
                cnt.set_text(f"{len(sd)} ideas finished: {np.mean(sd == 1):.0%} never left the inventor, "
                             f"largest reached {sd.max()} agents")
            else:
                cnt.set_text("")
            cnt.set_alpha(alpha)
        clock.set_text(f"t = {t / 24:4.1f} s   (one generation = one read-and-reuse step)")
        return []

    anim = animation.FuncAnimation(fig, frame, frames=T, blit=False)
    vs.save_anim(anim, HERE / "anim", fps=24, dpi=160, poster_frame=fade0 - 1)
    plt.close(fig)
    for pi, (R, _) in enumerate(Rs):
        sizes = [sum(len(g) for g in tr) for tr in forests[pi]]
        print(f"R={R}: sizes {sorted(sizes)}")


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
