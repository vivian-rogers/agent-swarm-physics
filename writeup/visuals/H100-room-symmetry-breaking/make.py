"""H100 visuals: rooms break the #best/#rest symmetry anew at each goal (no remanence).

Static (fig.pdf/png, double column):
  (a) simulation: explicit symmetry breaking (room split pinned along a field h) vs spontaneous (a new direction at
      each goal), two-block soft-spin cartoon;
  (b) relabel excess Q and Q_spont per period with the room-relabel null (gray: null 95th percentile);
  (c) shares of the room separation: composition / field direction / spontaneous, per regime-III period;
  (d) remanence R between consecutive periods against the joint-relabel null (gray: mean +- 2 sd).
  All numbers in (b)-(d) are read from H100's results (raw_bge_small_style_resid.json), not recomputed.

Animation (anim.mp4, 1280x720): #39 -> #40 (NE42 merge) -> #41, agents as points in a 2-D content plane spanned by
the #39 and #41 room differences (bge style-residualized statement vectors, day-centred, H100's leave-period-out agent
constants removed, H100's field directions projected out). Built by writeup/visuals/_rooms_common.py; the in-plane
angle reproduces H100's R(#39, #41) = -0.13.

Run: uv run python writeup/visuals/H100-room-symmetry-breaking/make.py [--static] [--anim]
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import _rooms_common as rc  # noqa: E402  (sets thread caps first)
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from matplotlib import animation  # noqa: E402
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import FancyArrowPatch  # noqa: E402

import vstyle as vs  # noqa: E402

H100 = rc.PROC / "H100-room-symmetry-breaking"
RAW = rc.load_json("H100-room-symmetry-breaking/results/raw_bge_small_style_resid.json")
BEST, REST = rc.BEST, rc.REST
C_BEST, C_REST = vs.ROOM["#best"], vs.ROOM["#rest"]
C_COMP = vs.C["green"]
MERGED = vs.INK2          # one merged room (#universe-coordination): no extra hue
MK = {BEST: "o", REST: "s"}


# ============================================================================ static figure
def panel_sim(fig, spec):
    """Two rows x three goals: explicit (field-pinned) vs spontaneous (random direction each goal). Simulation."""
    rng = np.random.default_rng(7)
    sub = GridSpecFromSubplotSpec(2, 3, subplot_spec=spec, wspace=0.08, hspace=0.25)
    h = np.array([1.0, 0.25]); h /= np.linalg.norm(h)
    thetas = [0.6, 2.6, 4.4]
    axes = []
    for row in range(2):
        for g in range(3):
            ax = fig.add_subplot(sub[row, g]); axes.append(ax)
            if row == 0:
                ang = np.arctan2(h[1], h[0]) + rng.normal(0, 0.12)
            else:
                ang = thetas[g]
            d = 0.9 * np.array([np.cos(ang), np.sin(ang)])
            for r, sgn in ((BEST, 0.5), (REST, -0.5)):
                pts = sgn * d + rng.normal(0, 0.28, (7, 2))
                ax.scatter(pts[:, 0], pts[:, 1], s=9, marker=MK[r], color=C_BEST if r == BEST else C_REST,
                           edgecolor="white", linewidth=0.3, zorder=3)
            ax.add_patch(FancyArrowPatch(-0.5 * d, 0.5 * d, arrowstyle="-|>", mutation_scale=6, color=vs.INK,
                                         lw=0.9, zorder=4))
            if row == 0:
                ax.add_patch(FancyArrowPatch(-1.25 * h - [0, 0.95], 1.25 * h - [0, 0.95], arrowstyle="-|>",
                                             mutation_scale=6, color=vs.FIELD, lw=1.2, zorder=2))
            ax.set_xlim(-1.5, 1.5); ax.set_ylim(-1.5, 1.5); ax.set_aspect("equal")
            ax.set_xticks([]); ax.set_yticks([]); ax.grid(False)
            for s in ax.spines.values():
                s.set_visible(True); s.set_color(vs.GRID)
            if row == 0:
                ax.set_title(f"goal {g + 1}", fontsize=7, pad=2)
    axes[0].set_ylabel("explicit\n(field $h$)", fontsize=7, color=vs.INK)
    axes[3].set_ylabel("spontaneous\n(no field)", fontsize=7, color=vs.INK)
    axes[0].text(-0.08, 1.32, "(a) simulation: room split $\\Delta$ (arrow) at three goals", transform=axes[0].transAxes,
                 fontsize=8, ha="left", va="bottom")
    axes[0].text(0.05, 0.95, "field $h$", color=vs.FIELD, transform=axes[0].transAxes, ha="left", va="top",
                 fontsize=6.3)
    return axes


def panel_Q(ax):
    per = ["G35", "G36", "G37", "G38", "G39", "G41", "G42", "G44"]
    x = np.arange(len(per))
    for i, k in enumerate(per):
        v = RAW["periods"][k]
        hi = 1 + 1.645 * v["S_null_sd"] / v["S_null_mean"]
        ax.add_patch(plt.Rectangle((i - 0.32, 0), 0.28, hi, color=vs.NULL, alpha=0.55, lw=0, zorder=1))
        ax.scatter(i - 0.18, v["Q"], s=16, color=vs.INK, marker="o", zorder=3)
        if v.get("Q_spont") is not None:
            his = 1 + 1.645 * v["S_null_sd_spont"] / v["S_null_mean_spont"]
            ax.add_patch(plt.Rectangle((i + 0.04, 0), 0.28, his, color=vs.NULL, alpha=0.55, lw=0, zorder=1))
            ax.scatter(i + 0.18, v["Q_spont"], s=16, color=vs.COUPLING, marker="D", zorder=3)
    ax.axhline(1, color=vs.MUTED, lw=0.6, ls=":", zorder=2)
    ax.set_xticks(x, [f"#{k[1:]}" for k in per])
    for t, k in zip(ax.get_xticklabels(), per):
        if k in ("G38", "G44"):
            t.set_color(vs.FIELD); t.set_fontweight("bold")
    ax.set_ylabel("relabel excess $Q$")
    ax.set_ylim(0, 9.6)
    ax.set_title("(b) rooms differ beyond random groupings", loc="left")
    h = [Line2D([], [], marker="o", ls="", color=vs.INK, ms=4, label="$Q$ (all)"),
         Line2D([], [], marker="D", ls="", color=vs.COUPLING, ms=4,
                label="$Q_\\mathrm{spont}$ (comp. + field removed)"),
         plt.Rectangle((0, 0), 1, 1, color=vs.NULL, alpha=0.55, label="relabel null, 95th pct.")]
    ax.legend(handles=h, loc="upper left", fontsize=6.3, handlelength=1.2, borderaxespad=0.2)
    ax.text(0.99, 0.98, "orange labels:\nroom-specific kickoffs", transform=ax.transAxes, ha="right", va="top",
            fontsize=6.3, color=vs.FIELD)


def panel_shares(ax):
    per = ["G36", "G37", "G38", "G39", "G41", "G42", "G44"]
    x = np.arange(len(per))
    for i, k in enumerate(per):
        v = RAW["periods"][k]
        sig = v["p"] < 0.05
        a = 1.0 if sig else 0.38
        fc, ff = max(v["f_comp"], 0), max(v["f_field"], 0)
        fs = 1 - fc - ff
        ax.bar(i, fc, color=C_COMP, alpha=a, width=0.62, lw=0)
        ax.bar(i, ff, bottom=fc, color=vs.FIELD, alpha=a, width=0.62, lw=0)
        ax.bar(i, fs, bottom=fc + ff, color=vs.COUPLING, alpha=a, width=0.62, lw=0)
        lo, hi = v["f_comp_ci"]
        ax.errorbar(i - 0.2, fc, yerr=[[fc - max(lo, 0)], [hi - fc]], color=vs.INK, lw=0.7, capsize=1.5)
        if not sig:
            ax.text(i, 1.03, "n.s.", ha="center", va="bottom", fontsize=6, color=vs.MUTED)
    ax.set_xticks(x, [f"#{k[1:]}" for k in per])
    for t, k in zip(ax.get_xticklabels(), per):
        if k in ("G38", "G44"):
            t.set_color(vs.FIELD); t.set_fontweight("bold")
    ax.set_ylim(0, 1.13); ax.set_ylabel("share of room separation $S$")
    ax.set_title("(c) the split is endogenous, not composition", loc="left")
    # direct labels on the last bar
    v = RAW["periods"]["G44"]
    xl = len(per) - 1 + 0.36
    ax.text(xl, 0.5 * max(v["f_comp"], 0), "composition", fontsize=6.3, va="center", ha="left", color=C_COMP)
    ax.text(xl, max(v["f_comp"], 0) + 0.5 * v["f_field"] + 0.01, "field dir.", fontsize=6.3, va="center", ha="left",
            color=vs.FIELD)
    ax.text(xl, 0.6, "spontaneous", fontsize=6.3, va="center", ha="left", color=vs.COUPLING)
    ax.set_xlim(-0.6, len(per) + 0.9)
    ax.text(0.0, -0.2, "faded: $Q$ not significant (shares not read)", transform=ax.transAxes, fontsize=6.2,
            color=vs.MUTED)


def panel_R(ax):
    rem = RAW["remanence"]
    keys = list(rem)
    x = np.arange(len(keys))
    for i, k in enumerate(keys):
        r = rem[k]
        mu = r["R"] - r["z"] * r["null_sd"]
        ax.add_patch(plt.Rectangle((i - 0.3, mu - 2 * r["null_sd"]), 0.6, 4 * r["null_sd"], color=vs.NULL, alpha=0.55,
                                   lw=0))
        ax.plot([i - 0.3, i + 0.3], [mu, mu], color=vs.MUTED, lw=0.8)
        ax.scatter(i, r["R"], s=18, color=vs.COUPLING, zorder=3, marker="D")
    ax.axhline(0, color=vs.MUTED, lw=0.6, ls=":")
    ax.set_xticks(x, [f"#{k.split('-')[0]}$\\to$#{k.split('-')[1]}" for k in keys], fontsize=6.3)
    ax.set_ylim(-1, 1); ax.set_ylabel("remanence $R=\\cos(\\Delta_P,\\Delta_{P'})$")
    ax.set_title("(d) the split direction does not survive the goal", loc="left")
    i = keys.index("39-41")
    ax.annotate("across the NE42 merge:\n$R=-0.13$ ($z=-1.6$)", (i, rem["39-41"]["R"]), xytext=(i - 0.2, -0.85),
                fontsize=6.3, ha="center", arrowprops=dict(arrowstyle="-", color=vs.MUTED, lw=0.6))
    h = [Line2D([], [], marker="D", ls="", color=vs.COUPLING, ms=4, label="observed $R$ (spontaneous part)"),
         plt.Rectangle((0, 0), 1, 1, color=vs.NULL, alpha=0.55, label="joint-relabel null, mean $\\pm$ 2 sd")]
    ax.legend(handles=h, loc="upper left", fontsize=6.3, handlelength=1.2, borderaxespad=0.2)


def make_static():
    vs.use()
    fig = plt.figure(figsize=(vs.W["double"], 4.7))
    gs = GridSpec(2, 2, figure=fig, width_ratios=[1, 1.08], hspace=0.55, wspace=0.28, left=0.07, right=0.985,
                  top=0.93, bottom=0.11)
    panel_sim(fig, gs[0, 0])
    panel_Q(fig.add_subplot(gs[0, 1]))
    panel_shares(fig.add_subplot(gs[1, 0]))
    panel_R(fig.add_subplot(gs[1, 1]))
    vs.save(fig, HERE / "fig")
    plt.close(fig)


# ============================================================================ animation data
def constants(exclude):
    """H100's leave-period-out agent constants (h100lib.constants rule) from H100's processed agent-day table."""
    tab = pl.read_parquet(H100 / "agent_days.parquet")
    XA = np.load(H100 / "x_style_resid_bge_small.npy").astype(np.float64)
    key = (tab["goal_no"].cast(pl.String) + "|" + tab["pt_date"]).to_numpy()
    for k in np.unique(key):
        m = key == k
        XA[m] -= XA[m].mean(0)
    ag, g, reg = tab["agent"].to_numpy(), tab["goal_no"].to_numpy(), tab["regime"].to_numpy()
    acc = {}
    for P in (36, 37, 38, 39, 40, 41, 42, 44, 51):
        if P in exclude:
            continue
        m = (g == P) & (reg == "III")
        for a in np.unique(ag[m]):
            acc.setdefault(int(a), []).append(XA[m & (ag == a)].mean(0))
    return {a: np.mean(v, 0) for a, v in acc.items()}


def field_basis(P):
    """H100's field directions for period P (room kickoff if the rooms' kickoffs differ; operator messages)."""
    fields = pl.read_parquet(H100 / "fields.parquet")
    F = np.load(H100 / "fields_bge_small.npy").astype(np.float64)
    dirs = []
    for kind in ("kickoff_room", "operator"):
        f = fields.filter((pl.col("goal_no") == P) & (pl.col("kind") == kind))
        rb, rr = f.filter(pl.col("room") == BEST), f.filter(pl.col("room") == REST)
        if rb.height and rr.height:
            vb, vr = F[rb["frow"][0]], F[rr["frow"][0]]
            c = vb @ vr / np.linalg.norm(vb) / np.linalg.norm(vr)
            if kind == "operator" or c < 0.95:
                d = vb - vr; dirs.append(d / np.linalg.norm(d))
    if not dirs:
        return np.zeros((0, 32))
    Q, _ = np.linalg.qr(np.array(dirs).T)
    return Q.T


def anim_data():
    st, X = rc.load_statements(goals=[39, 40, 41])
    Xc = rc.day_center(st, X)
    tab, V = rc.agent_day_means(st, Xc, min_n=1)
    A = constants({39, 41})
    ag, g = tab["agent"].to_numpy(), tab["goal_no"].to_numpy()
    W = V - np.array([A.get(int(a), np.zeros(32)) for a in ag])
    for P in (39, 41):
        E = field_basis(P); m = g == P
        if E.shape[0]:
            W[m] = W[m] - (W[m] @ E.T) @ E
    # partition: agents in one room (#best or #rest) on all their days of #39 and of #41, the same in both
    part = {}
    for a in np.unique(ag):
        r39 = set(tab.filter((pl.col("agent") == a) & (pl.col("goal_no") == 39))["room_day"].to_list())
        r41 = set(tab.filter((pl.col("agent") == a) & (pl.col("goal_no") == 41))["room_day"].to_list())
        if len(r39) == 1 and r39 == r41 and r39 <= {BEST, REST}:
            part[int(a)] = r39.pop()
    keep = np.isin(ag, list(part))
    tab, W = tab.filter(pl.Series(keep)), W[keep]
    ag, g = tab["agent"].to_numpy(), tab["goal_no"].to_numpy()

    def pdiff(P):
        means = {a: W[(g == P) & (ag == a)].mean(0) for a in part if ((g == P) & (ag == a)).any()}
        return (np.mean([v for a, v in means.items() if part[a] == BEST], 0)
                - np.mean([v for a, v in means.items() if part[a] == REST], 0))
    d39, d41 = pdiff(39), pdiff(41)
    R = float(d39 @ d41 / np.linalg.norm(d39) / np.linalg.norm(d41))
    B = rc.plane(d39, d41)
    days = sorted(tab["pt_date"].unique().to_list())
    split = rc.daily_room_split(tab, W, part, days, n_null=2000, seed=39)
    return dict(tab=tab, W=W, P2=W @ B.T, part=part, days=days, R=R, split=split, d39=B @ d39, d41=B @ d41)


# ============================================================================ animation
def make_anim():
    D = anim_data()
    print(f"in-plane R(#39,#41) = {D['R']:.3f} (card: -0.13)")
    tab, P2, part, days = D["tab"], D["P2"], D["part"], D["days"]
    agents = sorted(part)
    goal_of = dict(zip(tab["pt_date"].to_list(), tab["goal_no"].to_list()))
    # daily smoothed positions: within-period exponential average over days (tau 1.5 days), reset at each goal
    pos = {a: [] for a in agents}; room = {a: [] for a in agents}; present = {a: [] for a in agents}
    ag_col, d_col, r_col = tab["agent"].to_numpy(), tab["pt_date"].to_numpy(), tab["room_day"].to_numpy()
    for a in agents:
        acc, w, last_goal, last_room = None, 0.0, None, part[a]
        for d in days:
            if goal_of[d] != last_goal:
                acc, w, last_goal = None, 0.0, goal_of[d]
            m = (ag_col == a) & (d_col == d)
            if m.any():
                x = P2[m][0]
                acc = x if acc is None else acc * np.exp(-1 / 1.5) + x
                w = 1.0 if w == 0 else w * np.exp(-1 / 1.5) + 1.0
                last_room = int(r_col[m][0]); present[a].append(True)
            else:
                present[a].append(False)
            pos[a].append(acc / w if acc is not None else np.array([np.nan, np.nan]))
            room[a].append(last_room)
    pos = {a: np.array(v) for a, v in pos.items()}

    # frame schedule
    FPD, TR, GAP, FADE = 30, 18, 14, 12
    frames = []          # (day index, interpolation weight, kind)
    for k in range(len(days)):
        if k > 0 and goal_of[days[k]] != goal_of[days[k - 1]]:
            frames += [(k - 1, 1.0, "gap")] * GAP
        frames += [(k, min(1.0, f / TR), "day") for f in range(FPD)]
    frames = [(0, 0.0, "fadein")] * FADE + frames + [(len(days) - 1, 1.0, "hold")] * 30 + \
             [(len(days) - 1, 1.0, "fadeout")] * FADE
    n_frames = len(frames)

    split = D["split"]
    q05, q95 = np.nanpercentile(split["E_null"], [5, 95], axis=0)
    q50 = np.nanmedian(split["E_null"], axis=0)

    vs.use()
    rc_ctx = {"font.size": 12, "axes.titlesize": 12.5, "axes.labelsize": 11.5, "xtick.labelsize": 10,
              "ytick.labelsize": 10, "legend.fontsize": 10}
    plt.rcParams.update(rc_ctx)
    plt.rcParams["savefig.bbox"] = "standard"
    fig = plt.figure(figsize=(8, 4.5), dpi=160)
    gs = GridSpec(2, 2, figure=fig, width_ratios=[1.55, 1], height_ratios=[1, 1], left=0.07, right=0.975,
                  top=0.79, bottom=0.14, wspace=0.22, hspace=0.62)
    ax = fig.add_subplot(gs[:, 0]); axd = fig.add_subplot(gs[0, 1], projection="polar"); axs = fig.add_subplot(gs[1, 1])
    allp = np.concatenate([v[~np.isnan(v[:, 0])] for v in pos.values()])
    lim = np.abs(allp).max() * 1.12
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_aspect("equal")
    ax.set_xlabel("axis 1: #39 room difference")
    ax.set_ylabel("axis 2: #41 room difference ($\\perp$)")
    ax.tick_params(labelsize=8)
    fig.text(0.07, 0.955, "Rooms break the symmetry anew at each goal", fontsize=15, ha="left", va="center",
             color=vs.INK, fontweight="bold")
    sub = fig.text(0.07, 0.905, "", fontsize=11, ha="left", va="center", color=vs.INK2)
    clock = fig.text(0.975, 0.955, "", fontsize=12, ha="right", va="center", color=vs.INK, family="monospace")
    fig.text(0.015, 0.022, "H100 · bge style-resid. statement vectors, day-centred; agent constants and field directions "
             "removed; axes = observed #39 and #41 room differences (in-sample)",
             fontsize=7.5, ha="left", va="center", color=vs.MUTED)

    scat = {a: ax.scatter([], [], s=70, marker=MK[part[a]], edgecolor="white", linewidth=0.8, zorder=4)
            for a in agents}
    cent = {r: ax.scatter([], [], s=260, marker=MK[r], facecolor="none", linewidth=2.0, zorder=5)
            for r in (BEST, REST)}
    arrow = FancyArrowPatch((0, 0), (0, 0), arrowstyle="-|>", mutation_scale=16, color=vs.INK, lw=2.0, zorder=6)
    ax.add_patch(arrow)
    gpt5 = ax.text(0, 0, "", fontsize=8.5, color=C_REST, zorder=7, ha="right")
    leg = [Line2D([], [], marker="o", ls="", color=C_BEST, ms=8, label="#best"),
           Line2D([], [], marker="s", ls="", color=C_REST, ms=8, label="#rest"),
           Line2D([], [], marker="o", ls="", color=MERGED, ms=8, label="merged room (#40)"),
           Line2D([], [], color=vs.INK, lw=2, marker=">", ms=6, label="room split Δ")]
    ax.legend(handles=leg, loc="lower left", fontsize=8.5, handletextpad=0.3, borderaxespad=0.3, ncol=2,
              columnspacing=0.8)
    ax.text(0.99, 0.99, "shape = room in #39/#41", transform=ax.transAxes, ha="right", va="top", fontsize=8,
            color=vs.MUTED)

    # dial: direction of the split in the plane
    axd.set_theta_zero_location("E"); axd.set_rticks([]); axd.set_ylim(0, 1.05)
    axd.set_xticks(np.deg2rad([0, 90, 180, 270]), ["axis 1", "axis 2", "", ""], fontsize=8.5)
    axd.grid(color=vs.GRID, lw=0.6)
    axd.text(0.5, -0.13, "direction of the split", transform=axd.transAxes, ha="center", va="top", fontsize=11)
    dial_hist = axd.scatter([], [], s=12, zorder=3)
    dial_line, = axd.plot([], [], color=vs.INK, lw=2.2, zorder=4)

    # strip: daily split size vs joint-relabel null
    xs = np.arange(len(days))
    axs.fill_between(xs, q05, q95, color=vs.NULL, alpha=0.6, lw=0, step="mid", label="relabel null 5–95%")
    axs.plot(xs, q50, color=vs.MUTED, lw=0.8, drawstyle="steps-mid")
    line_obs, = axs.plot([], [], color=vs.COUPLING, lw=1.8, marker="o", ms=3.5, label="observed")
    axs.set_xlim(-0.5, len(days) - 0.5)
    ymax = np.nanmax(np.concatenate([split["E_obs"], q95])) * 1.15
    axs.set_ylim(0, ymax)
    axs.set_ylabel("split size |Δ(d)|²", fontsize=10)
    bounds = [k for k in range(1, len(days)) if goal_of[days[k]] != goal_of[days[k - 1]]]
    for b in bounds:
        axs.axvline(b - 0.5, color=vs.MUTED, lw=0.8, ls="--")
    seg = [0] + bounds + [len(days)]
    axs.set_xticks([(seg[i] + seg[i + 1] - 1) / 2 for i in range(3)], ["#39", "#40 merged", "#41"], fontsize=9.5)
    axs.tick_params(axis="y", labelsize=8)
    axs.legend(loc="upper left", fontsize=7.5, handlelength=1.2, borderaxespad=0.1, ncol=2, columnspacing=0.6)
    axs.set_title("daily split vs random groupings", fontsize=11, pad=4)

    SUB = {39: "#39: two rooms, identical kickoffs: the rooms split along axis 1",
           40: "#40 (NE42): rooms merged into one; GPT-5 left alone in #rest",
           41: f"#41: same members split again, along a new direction (R = −0.13, z = −1.6)"}
    angles_hist = []

    def state(fi):
        k, wgt, kind = frames[fi]
        s = 3 * wgt ** 2 - 2 * wgt ** 3
        P = {}
        for a in agents:
            cur = pos[a][k]
            prev = pos[a][k - 1] if k > 0 else cur
            if np.isnan(prev[0]):
                prev = cur
            P[a] = cur if kind != "day" else (1 - s) * prev + s * cur
        return k, P, kind

    def draw(fi):
        k, P, kind = state(fi)
        alpha = 1.0
        if kind == "fadein":
            alpha = fi / FADE
        elif kind == "fadeout":
            alpha = 1 - (fi - (n_frames - FADE)) / FADE
        G = goal_of[days[k]] if kind != "gap" else goal_of[days[min(k + 1, len(days) - 1)]]
        cpos = {BEST: [], REST: []}
        for a in agents:
            p = P[a]
            if np.isnan(p[0]):
                scat[a].set_offsets(np.empty((0, 2))); continue
            r = room[a][k]
            col = C_BEST if r == BEST else C_REST if r == REST else MERGED
            scat[a].set_offsets([p]); scat[a].set_facecolor(col)
            scat[a].set_alpha(alpha * (1.0 if present[a][k] else 0.45))
            cpos[part[a]].append(p)
        cb, cr = np.mean(cpos[BEST], 0), np.mean(cpos[REST], 0)
        cent[BEST].set_offsets([cb]); cent[REST].set_offsets([cr])
        merged = goal_of[days[k]] == 40
        cent[BEST].set_edgecolor(MERGED if merged else C_BEST); cent[REST].set_edgecolor(MERGED if merged else C_REST)
        for c in cent.values():
            c.set_alpha(alpha)
        arrow.set_positions(tuple(cr), tuple(cb)); arrow.set_alpha(alpha)
        g5 = P.get(10)
        if goal_of[days[k]] == 40 and g5 is not None and not np.isnan(g5[0]) and room[10][k] == REST:
            gpt5.set_position((g5[0] - 0.012, g5[1] + 0.022)); gpt5.set_text("GPT-5"); gpt5.set_alpha(alpha)
        else:
            gpt5.set_text("")
        dvec = cb - cr; th = np.arctan2(dvec[1], dvec[0]); mag = np.linalg.norm(dvec)
        if kind == "day" and frames[fi][1] >= 1.0 and (not angles_hist or angles_hist[-1][2] != k):
            angles_hist.append((th, min(1.0, mag / 0.45), k))
        if kind == "fadein":
            angles_hist.clear()
        hist = [(t, m) for t, m, kk in angles_hist]
        if hist:
            dial_hist.set_offsets(np.array(hist))
            dial_hist.set_facecolor([vs.COUPLING if goal_of[days[kk]] != 40 else MERGED for _, _, kk in angles_hist])
            dial_hist.set_alpha(0.5 * alpha)
        dial_line.set_data([th, th], [0, min(1.0, mag / 0.45)]); dial_line.set_alpha(alpha)
        n_show = k + (1 if kind in ("day", "hold", "fadeout") and frames[fi][1] >= 1.0 else 0)
        n_show = max(n_show, 0) if kind != "fadein" else 0
        line_obs.set_data(xs[:n_show], split["E_obs"][:n_show]); line_obs.set_alpha(alpha)
        gd = [d for d in days if goal_of[d] == goal_of[days[k]]]
        clock.set_text(f"#{goal_of[days[k]]} · day {gd.index(days[k]) + 1}/{len(gd)} · {days[k]}"
                       if kind != "gap" else "next goal …")
        sub.set_text(SUB[G])
        return []

    anim = animation.FuncAnimation(fig, draw, frames=n_frames, interval=1000 / 24, blit=False)
    out = HERE / "anim.mp4"
    w = animation.FFMpegWriter(fps=24, codec="h264", bitrate=2400,
                               extra_args=["-pix_fmt", "yuv420p", "-movflags", "+faststart"])
    if "--poster-only" not in sys.argv:
        anim.save(out, writer=w, dpi=160)
    # poster: the last fully drawn #41 frame (redraw from scratch so the dial history is complete)
    angles_hist.clear()
    for fi in range(n_frames - FADE - 1):
        draw(fi)
    fig.savefig(HERE / "anim_poster.png", dpi=160, bbox_inches=None)
    plt.close(fig)
    print(f"frames {n_frames} = {n_frames / 24:.1f} s")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or "--static" in args:
        make_static()
    if not args or "--anim" in args:
        make_anim()
