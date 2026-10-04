"""H97 visuals: a kickoff is a restoring force (anisotropic, with a day-1 overshoot).

fig.pdf/png  (a) content plane of one real kickoff (#38 -> #39, bge): agents' day means before and after an ordinary
             night (gray) and across the kickoff (orange); (b) cross-agent memory rho on consecutive-day boundaries
             around 18 kickoffs (event study) against the placebo band of ordinary nights; (c) extra forgetting
             along / across the kickoff and the overshoot intercept (card meta-analysis).
anim.mp4     the same kickoff in the content plane, frame by frame (active time only): before, snap, overshoot, settle.

Inputs (read-only): data/processed/H97-quench-restoring-force/ (stmt, transitions, vectors, G<NN>/results.json,
NE34/summary.json, NE34/transitions_all_configs.parquet, NE34/placebo_gaps.parquet), shared DQ5 statement vectors.
Usage: uv run python writeup/visuals/H97-quench-restoring-force/make.py [--no-anim] [--anim-only]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VIS = HERE.parent
ROOT = VIS.parents[1]
sys.path.insert(0, str(VIS))
sys.path.insert(0, str(ROOT / "hypotheses/H97-quench-restoring-force/analysis"))

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.animation import FuncAnimation  # noqa: E402

import vstyle as vs  # noqa: E402
import _quench_common as qc  # noqa: E402
import h97lib as L  # noqa: E402

DATA = qc.H97
DESIGN = "T39"          # #38 -> #39: regime III, 13 agents on both sides, the largest extra forgetting
PLAT = (1, 2, 3, 4)     # days 2-5 of P (rel 1..4): H97's settled level


# ============================================================================== event study (cheap: day means only)
def event_study():
    """rho_full on consecutive active-day boundaries at offsets -4..+3 around each of the 18 primary kickoffs.
    Offset 0 is the stored kickoff rho (G<NN>/results.json); the others use the same estimator (h97lib.memory_corr,
    split halves of both days, 20 splits)."""
    tac = pl.read_parquet(DATA / "NE34/transitions_all_configs.parquet")
    prim = tac.filter((pl.col("cfg") == "primary") & pl.col("same_regime") & (pl.col("N") >= L.MIN_N_TRANSITION)
                      & (pl.col("n_placebo") > 0) & pl.col("drho_full").is_finite())
    rows = []
    for tr in prim.iter_rows(named=True):
        design, p = tr["design"], tr["p"]
        stmt, trow = L.load_design(design)
        stmt = stmt.filter(pl.col("agent") != qc.CC_AGENT)
        k = L.vectors(design, "k", "bge_small")
        days = stmt.select("goal_no", "pt_date", "day_idx").unique().sort("pt_date").to_dicts()
        prevd = [d for d in days if d["goal_no"] == trow["prev"]]
        newd = [d for d in days if d["goal_no"] == p and d["day_idx"] <= 5]
        segs = []
        for j in range(1, 5):      # offsets -1..-4 inside P-1
            if len(prevd) > j:
                segs.append((-j, prevd[-1 - j], prevd[-j], False))
        for j in range(1, 4):      # offsets +1..+3 inside P (day1 -> day2 uses the post-kickoff day-1 rows)
            if len(newd) > j:
                segs.append((j, newd[j - 1], newd[j], j == 1))
        for off, d0, d1, d0_is_day1 in segs:
            m0 = (pl.col("seg") == "day1") if d0_is_day1 else ((pl.col("goal_no") == d0["goal_no"]) & (pl.col("pt_date") == d0["pt_date"]))
            m1 = (pl.col("goal_no") == d1["goal_no"]) & (pl.col("pt_date") == d1["pt_date"])
            bd = L.boundary(L.seg_vectors(stmt, m0), L.seg_vectors(stmt, m1))
            if len(bd) < L.MIN_N_TRANSITION:
                continue
            XA, XB, Y, ag, YA, YB = L.split_arrays(bd, n_splits=20, seed=1000 + p * 10 + off + 5, with_y_halves=True)
            rows.append(dict(design=design, p=p, off=off, rho=float(L.memory_corr(XA, XB, Y, YA, YB, k, "full")), N=len(bd)))
        rows.append(dict(design=design, p=p, off=0, rho=float(tr["rho_full"]), N=int(tr["N"])))
    return pl.DataFrame(rows), prim


def boot_median(v, B=4000, seed=0):
    v = np.asarray(v, float); v = v[np.isfinite(v)]
    rng = np.random.default_rng(seed)
    bs = np.median(rng.choice(v, (B, len(v))), axis=1)
    return float(np.median(v)), float(np.percentile(bs, 5)), float(np.percentile(bs, 95)), len(v)


# ============================================================================== static figure
def panel_plane(ax, T):
    """Agent day means in the content plane: ordinary night (day -2 -> -1, gray) and kickoff (day -1 -> day 1)."""
    m2 = qc.seg_means(T, qc.day_mask(T, -2)); m1 = qc.seg_means(T, qc.day_mask(T, -1))
    d1 = qc.seg_means(T, pl.col("seg") == "day1")
    plat = qc.seg_means(T, pl.col("seg") == "plateau")
    v2 = np.array([m2[a][:2] for a in sorted(set(m2) & set(m1))])
    ax.scatter(v2[:, 0], v2[:, 1], s=5, color=vs.NULL, zorder=2)
    for a in sorted(set(m2) & set(m1)):
        ax.annotate("", xy=m1[a][:2], xytext=m2[a][:2],
                    arrowprops=dict(arrowstyle="-|>", color=vs.NULL, lw=0.8, shrinkA=0, shrinkB=1.5, mutation_scale=6))
    for a in sorted(set(m1) & set(d1)):
        ax.annotate("", xy=d1[a][:2], xytext=m1[a][:2],
                    arrowprops=dict(arrowstyle="-|>", color=vs.FIELD, lw=0.9, alpha=0.9, shrinkA=1.5, shrinkB=1.5,
                                    mutation_scale=6))
    v1 = np.array([m1[a][:2] for a in m1]); vd = np.array([d1[a][:2] for a in d1])
    ax.scatter(v1[:, 0], v1[:, 1], s=14, facecolor="white", edgecolor=vs.INK2, lw=0.8, zorder=3,
               label="#38, last day")
    ax.scatter(vd[:, 0], vd[:, 1], s=14, color=vs.FIELD, edgecolor=vs.INK, lw=0.4, zorder=3, label="#39, day 1")
    xs = np.mean([v[0] for v in plat.values()])
    ax.axvline(xs, color=vs.INK2, lw=0.8, ls="--", zorder=1)
    ax.text(xs, 0.98, " settled\n level", transform=ax.get_xaxis_transform(), fontsize=6, color=vs.INK2,
            va="top", ha="left")
    ax.scatter([vd[:, 0].mean()], [vd[:, 1].mean()], marker="D", s=26, color=vs.FIELD, edgecolor=vs.INK, lw=0.8,
               zorder=4)
    ax.annotate("day-1 mean,\nbeyond the\nsettled level", (vd[:, 0].mean(), vd[:, 1].mean()), xytext=(0.215, 0.36),
                textcoords="data", fontsize=6, color=vs.INK, ha="left",
                arrowprops=dict(arrowstyle="-", lw=0.5, color=vs.INK2, shrinkB=4))
    ax.plot([], [], color=vs.NULL, lw=0.9, label="ordinary night")
    ax.plot([], [], color=vs.FIELD, lw=0.9, label="kickoff")
    ax.set_xlabel(r"goal axis $\langle z,\hat k_{39}\rangle$")
    ax.set_ylabel(r"old-state axis $\langle z,\hat e_{38}\rangle$")
    ax.legend(loc="lower left", fontsize=5.6, handlelength=1.2, borderaxespad=0.1, labelspacing=0.2)
    ax.set_title(r"(a) one kickoff, #38 $\rightarrow$ #39 (bge)", loc="left")


def panel_event(ax, es, gaps, summ):
    pl0 = gaps["rho0"].to_numpy()
    lo, q25, q75, hi = np.percentile(pl0, [5, 25, 75, 95])
    offs = sorted(es["off"].unique().to_list())
    ax.axhspan(lo, hi, color=vs.NULL, alpha=0.25, lw=0)
    ax.axhspan(q25, q75, color=vs.NULL, alpha=0.45, lw=0)
    ax.text(offs[0] - 0.35, hi + 0.012, "ordinary nights (placebo, 161)", fontsize=6, color=vs.INK2, va="bottom")
    for d, g in es.group_by("design"):
        g = g.sort("off")
        ax.plot(g["off"], g["rho"], color=vs.INK, lw=0.35, alpha=0.16, zorder=1)
    med = []
    for o in offs:
        m, a, b, n = boot_median(es.filter(pl.col("off") == o)["rho"].to_numpy(), seed=o + 10)
        med.append((o, m, a, b, n))
    med = np.array(med)
    ax.errorbar(med[:, 0], med[:, 1], yerr=[med[:, 1] - med[:, 2], med[:, 3] - med[:, 1]], fmt="o-", color=vs.INK,
                ms=3.2, lw=1.2, capsize=1.5, zorder=3, label="median of 18 kickoffs (90% CI)")
    k0 = med[med[:, 0] == 0][0]
    ax.errorbar([0], [k0[1]], yerr=[[k0[1] - k0[2]], [k0[3] - k0[1]]], fmt="o", color=vs.FIELD, mec=vs.INK, ms=5,
                capsize=1.8, zorder=4)
    ax.annotate(f"kickoff\nρ = {summ['rho_kick_median']:.2f}", (0, k0[1]), xytext=(8, -14), textcoords="offset points",
                fontsize=6.3, color=vs.INK)
    ax.axvline(0, color=vs.FIELD, lw=0.6, ls=":", zorder=0)
    ax.set_xticks(offs)
    ax.set_xticklabels([("K" if o == 0 else f"{o:+d}".replace("-", "−")) for o in offs])
    ax.set_xlabel("day boundary relative to the kickoff (K)")
    ax.set_ylabel(r"memory $\rho$ of agents' positions")
    ax.set_ylim(-0.05, 1.12)
    ax.legend(loc="lower left", fontsize=5.8, borderaxespad=0.2)
    ax.set_title("(b) memory across each night", loc="left")
    return med


def panel_aniso(ax, summ):
    p = summ["meta"]["primary"]
    items = [("full space", p["drho"]), (r"across $\hat k$", p["drho_perp"]), (r"along $\hat k$", p["drho_par"])]
    for i, (lab, d) in enumerate(items):
        m, se = d["mean"], d["se"]
        col = vs.FIELD if "along" in lab else (vs.C["sky"] if "across" in lab else vs.INK)
        ax.errorbar([m], [i], xerr=[[1.645 * se], [1.645 * se]], fmt="o", color=col, mec=vs.INK, mew=0.5, ms=4.5,
                    capsize=1.8, lw=1.2)
        ax.text(m, i + 0.2, f"{m:+.2f} ± {se:.2f}", ha="center", va="bottom", fontsize=6.2, color=vs.INK)
    ax.axvline(0, color=vs.INK2, lw=0.6)
    ax.set_yticks(range(3)); ax.set_yticklabels([t for t, _ in items])
    ax.set_ylim(-0.6, 2.75)
    ax.set_xlim(-0.12, 1.15)
    ax.set_xlabel(r"extra forgetting $\Delta\rho=\rho_0-\rho_{\rm kick}$")
    ax.grid(axis="y", visible=False)
    a = summ["meta"]["center"]["shape_a"]
    ax.text(0.98, 0.04, f"day-1 overshoot\na = {a['mean']:+.2f} ± {a['se']:.2f}\n(agent-centered)",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=5.8, color=vs.INK2)
    ax.set_title(r"(c) the well is stiffer along $\hat k$", loc="left")


def static(es):
    T = qc.load_transition(DESIGN)
    summ = json.load(open(DATA / "NE34/summary.json"))["meta"]["primary"]
    summ_all = json.load(open(DATA / "NE34/summary.json"))
    gaps = pl.read_parquet(DATA / "NE34/placebo_gaps.parquet")
    fig = plt.figure(figsize=(vs.W["double"], 2.45))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.15, 0.95], wspace=0.42)
    a0, a1, a2 = (fig.add_subplot(gs[0, i]) for i in range(3))
    panel_plane(a0, T)
    med = panel_event(a1, es, gaps, summ)
    panel_aniso(a2, summ_all)
    vs.save(fig, HERE / "fig")
    plt.close(fig)
    return med, summ


# ============================================================================== animation
def animate():
    T = qc.load_transition(DESIGN)
    rels = [-2, -1, 0, 1, 2, 3, 4]
    tj = qc.kernel_trajectories(T, rels, step_min=4.0, tau_min=40.0, window_min=120.0, min_weight=2.0)
    pos, fresh, frames = tj["pos"], tj["fresh"], tj["frames"]
    nm = T["names"]
    plat = qc.seg_means(T, pl.col("seg") == "plateau")
    x_set = float(np.mean([v[0] for v in plat.values()]))
    r39 = json.load(open(DATA / "G39/results.json"))
    summ = json.load(open(DATA / "NE34/summary.json"))["meta"]["primary"]
    # frame schedule: active-time frames + night holds (fade) + an end fade for the loop
    NIGHT, END, START = 12, 20, 8
    sched = [("start", 0, i) for i in range(START)]
    t0m_ = T["t0"].timestamp() / 60.0
    for i in range(len(frames)):
        if i in tj["day_starts"][1:]:
            sched += [("night", i, j) for j in range(NIGHT)]
        sched.append(("f", i, 0))
        if frames[i][0] == 0 and frames[i][1] - t0m_ < 90:   # the snap in 2x slow motion
            sched.append(("f", i, 1))
    sched += [("end", len(frames) - 1, j) for j in range(END)]
    cen = np.nanmean(pos, axis=1)
    allp = pos.reshape(-1, 2)
    allp = allp[np.isfinite(allp).all(1)]
    xl = np.percentile(allp[:, 0], [0.5, 99.5]) + np.array([-0.06, 0.06])
    yl = np.percentile(allp[:, 1], [0.5, 99.5]) + np.array([-0.06, 0.06])
    rel_of = np.array([f[0] for f in frames])
    # stage per frame
    t0m = T["t0"].timestamp() / 60.0

    def stage(i):
        r, g = frames[i]
        if r < 0:
            return "before (#38)", vs.INK2
        if r == 0 and g - t0m < 75:
            return "kickoff snap (2× slow)", vs.FIELD
        if r <= 1:
            return "overshoot", vs.FIELD
        return "settle", vs.C["blue"]

    plt.rcParams.update({"font.size": 11, "axes.titlesize": 12, "axes.labelsize": 11, "xtick.labelsize": 9.5,
                         "ytick.labelsize": 9.5, "legend.fontsize": 9})
    fig = plt.figure(figsize=(8.0, 4.5), dpi=160)
    ax = fig.add_axes([0.075, 0.12, 0.455, 0.73])
    axt = fig.add_axes([0.635, 0.545, 0.34, 0.29])
    axx = fig.add_axes([0.71, 0.225, 0.265, 0.14])
    fig.text(0.075, 0.955, "H97 · A kickoff is a restoring force", fontsize=14.5, color=vs.INK, va="top")
    fig.text(0.075, 0.905, r"AI Village #38 $\rightarrow$ #39, agents in the content plane (bge, active time only)", fontsize=9.5,
             color=vs.INK2, va="top")
    clock = fig.text(0.975, 0.955, "", ha="right", va="top", fontsize=11, color=vs.INK, family="monospace")
    stg = ax.text(0.02, 0.98, "", transform=ax.transAxes, ha="left", va="top", fontsize=12, zorder=7)
    ax.set_xlim(*xl); ax.set_ylim(*yl)
    ax.set_xlabel(r"goal axis $\langle z,\hat k_{39}\rangle$ (toward the new kickoff)")
    ax.set_ylabel(r"old-state axis $\langle z,\hat e_{38}\rangle$")
    ax.axvline(x_set, color=vs.INK2, lw=1.0, ls="--")
    ax.text(x_set, yl[1] - 0.005, " settled level\n (days 2–5)", fontsize=8.5, color=vs.INK2, va="top", ha="left")
    ax.annotate("", xy=(xl[1] - 0.01, yl[0] + 0.03), xytext=(xl[1] - 0.16, yl[0] + 0.03),
                arrowprops=dict(arrowstyle="-|>", color=vs.FIELD, lw=2.0, mutation_scale=12))
    ax.text(xl[1] - 0.015, yl[0] + 0.045, "kickoff field", color=vs.FIELD, ha="right", va="bottom", fontsize=9)
    ghosts = ax.scatter([], [], s=34, facecolor="none", edgecolor=vs.MUTED, lw=0.9, zorder=2)
    trails = [ax.plot([], [], color=vs.INK2, lw=0.7, alpha=0.35, zorder=2)[0] for _ in tj["agents"]]
    dots = ax.scatter([], [], s=34, color=vs.INK, edgecolor="white", lw=0.6, zorder=4)
    cpath, = ax.plot([], [], color=vs.FIELD, lw=1.4, alpha=0.9, zorder=3)
    cdot = ax.scatter([], [], marker="D", s=70, color=vs.FIELD, edgecolor=vs.INK, lw=1.0, zorder=5)
    ax.scatter([], [], s=34, color=vs.INK, edgecolor="white", label="agent (2-h kernel mean)")
    ax.scatter([], [], marker="D", s=50, color=vs.FIELD, edgecolor=vs.INK, label="swarm mean + path")
    ax.scatter([], [], s=34, facecolor="none", edgecolor=vs.MUTED, label="position before the kickoff")
    ax.legend(loc="lower left", fontsize=8, handletextpad=0.3, borderaxespad=0.3)
    night_txt = ax.text(0.5, 0.5, "", transform=ax.transAxes, ha="center", va="center", fontsize=15, color=vs.INK2,
                        alpha=0.0, weight="bold", zorder=6)
    # time series: swarm-mean goal-axis and old-state coordinates
    idx = np.arange(len(frames))
    gapx = np.zeros(len(frames))
    for s in tj["day_starts"][1:]:
        gapx[s:] += 6
    tx = idx + gapx
    axt.set_xlim(tx[0] - 2, tx[-1] + 60)
    yy = np.r_[cen[:, 0], cen[:, 1]]
    axt.set_ylim(np.nanmin(yy) - 0.04, np.nanmax(yy) + 0.06)
    for s in tj["day_starts"][1:]:
        axt.axvspan(tx[s] - 6, tx[s] - 0.5, color=vs.GRID, lw=0)
    k0 = tj["day_starts"][rels.index(0)]
    axt.axvline(tx[k0] - 0.5, color=vs.FIELD, lw=1.0, ls=":")
    axt.text(tx[k0], axt.get_ylim()[1], "kickoff", color=vs.FIELD, fontsize=8.5, va="top", ha="left")
    axt.axhline(x_set, color=vs.INK2, lw=0.8, ls="--")
    lx, = axt.plot([], [], color=vs.FIELD, lw=1.6)
    ly, = axt.plot([], [], color=vs.C["sky"], lw=1.6)
    tlx = axt.text(0, 0, "", color=vs.INK, fontsize=8.5, va="center")
    tly = axt.text(0, 0, "", color=vs.INK, fontsize=8.5, va="center")
    axt.set_xticks([tx[s] + (tj["day_starts"][j + 1] - s if j + 1 < len(rels) else len(frames) - s) / 2
                    for j, s in enumerate(tj["day_starts"])])
    axt.set_xticklabels(["−2", "−1", "1", "2", "3", "4", "5"])
    axt.set_xlabel("day (nights shaded; #38 | #39)")
    axt.set_ylabel("swarm mean")
    axt.set_title("goal axis vs old-state axis", loc="left", fontsize=10.5)
    # numbers panel: memory bars (this swarm) + the 18-kickoff summary
    rho0, rho = r39["rho0_full"], r39["rho_full"]
    axx.set_title("memory of who was where (ρ)", loc="left", fontsize=10.5)
    bars = [("ordinary night", rho0, vs.NULL), ("this kickoff", rho, vs.FIELD)]
    barts = []
    for i, (lab, v, col) in enumerate(bars):
        bb = axx.barh([1 - i], [v], color=col, edgecolor=vs.INK, lw=0.6, height=0.6)
        tt = axx.text(v + 0.02, 1 - i, f"{v:.2f}", va="center", fontsize=10)
        barts.append((bb, tt))
    axx.set_yticks([1, 0]); axx.set_yticklabels([b_[0] for b_ in bars], fontsize=9)
    axx.set_xlim(0, 1.0); axx.set_ylim(-0.5, 1.5); axx.set_xticks([0, 0.5, 1.0])
    axx.tick_params(axis="x", labelsize=8.5)
    axx.grid(axis="y", visible=False)
    axx.text(-0.29, -0.55, f"all 18 kickoffs: ρ {summ['rho0_median']:.2f} $\\rightarrow$ {summ['rho_kick_median']:.2f}"
             f"  (Δρ = +{summ['drho']['mean']:.2f} ± {summ['drho']['se']:.2f})\n"
             f"forgetting along $\\hat k$ {summ['drho_par']['mean']:.2f}, across {summ['drho_perp']['mean']:.2f}",
             transform=axx.transAxes, fontsize=8.5, color=vs.INK2, va="top")

    def draw_frame(si):
        kind, i, j = sched[si]
        P = pos[i]
        ok = np.isfinite(P).all(1)
        alpha = 1.0
        if kind == "start":
            alpha = (j + 1) / START
        if kind == "end":
            alpha = max(0.0, 1 - (j + 1) / END)
        dots.set_offsets(P[ok]); dots.set_alpha(alpha)
        fr = fresh[i][ok]
        dots.set_sizes(np.where(fr, 34, 18))
        lo = max(0, i - 10)
        for a, ln in enumerate(trails):
            seg = pos[lo:i + 1, a]
            seg = seg[np.isfinite(seg).all(1)]
            ln.set_data(seg[:, 0], seg[:, 1]); ln.set_alpha(0.35 * alpha)
        cpath.set_data(cen[:i + 1, 0], cen[:i + 1, 1]); cpath.set_alpha(0.9 * alpha)
        cdot.set_offsets(cen[i:i + 1]); cdot.set_alpha(alpha)
        if rel_of[i] >= 0:
            G = pos[k0 - 1]; okg = np.isfinite(G).all(1)
            ghosts.set_offsets(G[okg]); ghosts.set_alpha(alpha)
        else:
            ghosts.set_offsets(np.empty((0, 2)))
        lx.set_data(tx[:i + 1], cen[:i + 1, 0]); ly.set_data(tx[:i + 1], cen[:i + 1, 1])
        tlx.set_position((tx[i] + 1.5, cen[i, 0])); tlx.set_text("goal")
        tly.set_position((tx[i] + 1.5, cen[i, 1])); tly.set_text("old state")
        r, g = frames[i]
        hh = int(g // 60) % 24; mm = int(g % 60)
        dlab = f"#38 day {r:+d}".replace("-", "−") if r < 0 else f"#39 day {r + 1}"
        clock.set_text(f"{dlab} · {hh:02d}:{mm:02d} UTC")
        s, c = stage(i)
        stg.set_text(s); stg.set_color(c)
        if kind == "night":
            nxt = i
            lab = "weekend · new goal" if rel_of[nxt] == 0 else "night"
            night_txt.set_text(lab)
            night_txt.set_alpha(np.sin(np.pi * (j + 0.5) / NIGHT) * 0.85)
        else:
            night_txt.set_alpha(0.0)
        show = bool(rel_of[i] >= 0 or kind == "end")
        barts[1][0].patches[0].set_visible(show); barts[1][1].set_visible(show)
        return []

    anim = FuncAnimation(fig, draw_frame, frames=len(sched), interval=1000 / 24, blit=False)
    poster = [si for si, s in enumerate(sched) if s[0] == "f" and rel_of[s[1]] == 0][60]
    vs.save_anim(anim, HERE / "anim", fps=24, dpi=160, poster_frame=poster)
    plt.close(fig)
    return len(sched)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-anim", action="store_true")
    ap.add_argument("--anim-only", action="store_true")
    a = ap.parse_args()
    vs.use()
    if not a.anim_only:
        es, prim = event_study()
        med, summ = static(es)
        print("event study medians (off, median, lo, hi, n):")
        for r in med:
            print("  %+d  %.3f [%.3f, %.3f]  n=%d" % tuple(r))
        print("kickoffs:", es.filter(pl.col("off") == 0).height)
    if not a.no_anim:
        n = animate()
        print("anim frames", n, "duration %.1f s" % (n / 24))


if __name__ == "__main__":
    main()
