"""H11 writeup visual: agents herd onto shared projects, in attention and in work commits.

Builds from data/processed/H11-potts-labor-vs-herding/r1b/ (round 1b, shared deterministic labels):
  fig.pdf / fig.png   (a) Potts cartoon; (b) #31: agents on the busiest project per 30-min window vs the
                      circular-shift null band; (c) co-location share vs its N2 null per unit (attention, work);
                      (d) coupling beyond agent fields z_N2 per period (attention, work), null band |z| < 2.
  writeup/animations/H11-herding-shared-projects.mp4 + H11-herding-shared-projects_poster.png   #31 week: agents (dots) move between project wells; well depth follows occupancy.

Usage: uv run python writeup/visuals/H11-herding-shared-projects/make.py [--no-anim]
Non-holdout only (#31 and every unit shown are non-holdout; asserted with holdout_mask). No text is read.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "writeup/visuals"))
sys.path.insert(0, str(ROOT / "infra/shared"))
import vstyle as vs  # noqa: E402
from common import holdout_mask  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import animation  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

D = ROOT / "data/processed/H11-potts-labor-vs-herding/r1b"
GOAL = 31
SEED = 20261004
N_NULL = 400


# ------------------------------------------------------------------------------------------------ data
def load_week(space="project"):
    lab = pl.read_parquet(D / f"G{GOAL}/labels_{space}_w30.parquet")
    assert not any(holdout_mask(lab["pt_date"].to_list(), lab["goal_no"].to_list())), "held-out rows"
    proj = pl.read_parquet(D / f"G{GOAL}/projects_{'work_' if space == 'work' else ''}w30.parquet")
    return lab, proj


def pile_series(lab: pl.DataFrame, n_win: int):
    """Agents on the most-occupied single project per window (raw project, not merged)."""
    t = (lab["day"] * n_win + lab["win"]).to_numpy()
    out = np.zeros(lab["day"].max() * n_win + n_win, int)
    for k in np.unique(t):
        _, c = np.unique(lab["project"].to_numpy()[t == k], return_counts=True)
        out[k] = c.max()
    return out


def pile_null(lab: pl.DataFrame, n_win: int, rng, n=N_NULL):
    """N2 circular shift: each agent's within-day window sequence (label + presence) rolled by a random offset."""
    days = int(lab["day"].max()) + 1
    agents = sorted(lab["agent"].unique().to_list())
    projs = {p: i for i, p in enumerate(sorted(lab["project"].unique().to_list()))}
    S = -np.ones((len(agents), days, n_win), int)
    ai = {a: i for i, a in enumerate(agents)}
    for a, d, w, p in lab.select("agent", "day", "win", "project").iter_rows():
        S[ai[a], d, w] = projs[p]
    res = np.zeros((n, days * n_win), int)
    for r in range(n):
        Z = S.copy()
        for i in range(len(agents)):
            for d in range(days):
                Z[i, d] = np.roll(S[i, d], rng.integers(n_win))
        for d in range(days):
            for w in range(n_win):
                v = Z[:, d, w]; v = v[v >= 0]
                res[r, d * n_win + w] = np.bincount(v).max() if len(v) else 0
    return res


def short(p: str) -> str:
    return p.rstrip("/").split("/")[-1]


def wrap(name: str, width: int = 11) -> str:
    """Break a repo name at hyphens into lines of at most ~width characters."""
    lines, cur = [], ""
    for part in name.split("-"):
        piece = part if not cur else cur + "-" + part
        if cur and len(piece) > width:
            lines.append(cur + "-"); cur = part
        else:
            cur = piece
    lines.append(cur)
    return "\n".join(lines)


def units_table():
    w = pl.read_parquet(D / "work_vs_attention_r1b.parquet")
    v = pl.read_parquet(D / "verdicts_round1b.parquet").filter(pl.col("tested"))
    return w, v


# ------------------------------------------------------------------------------------------------ figure
def cartoon(ax):
    """(a) Potts picture: wells = projects; balls = agents. Left: spread (fields / division of labor). Right: herding."""
    ax.set_xlim(0, 10); ax.set_ylim(-0.35, 3.75); ax.axis("off")
    rng = np.random.default_rng(3)
    def wells(x0, depths, occ, color):
        xs = x0 + np.arange(len(depths)) * 1.35
        for x, dep, n in zip(xs, depths, occ):
            u = np.linspace(-0.55, 0.55, 40)
            ax.plot(x + u, 1.25 - dep * (1 - (u / 0.55) ** 2), color=vs.INK2, lw=0.9)
            for k in range(n):
                ax.scatter(x + (k % 3 - 1) * 0.27, 1.32 - dep + 0.13 + (k // 3) * 0.3, s=13, color=color,
                           edgecolor="white", lw=0.4, zorder=3)
        return xs
    ax.text(0.15, 3.7, r"$\beta J<0$: spread", fontsize=7, color=vs.INK, va="top")
    ax.text(0.15, 3.2, "own project each", fontsize=6, color=vs.INK2, va="top")
    wells(0.75, [0.5, 0.5, 0.5], [2, 2, 2], vs.MUTED)
    ax.text(5.35, 3.7, r"$\beta J>0$: herding", fontsize=7, color=vs.INK, va="top")
    ax.text(5.35, 3.2, "full wells attract", fontsize=6, color=vs.INK2, va="top")
    wells(5.95, [0.25, 1.05, 0.25], [0, 6, 0], vs.COUPLING)
    ax.annotate("", xy=(7.0, 2.05), xytext=(6.1, 2.6), arrowprops=dict(arrowstyle="->", color=vs.COUPLING, lw=0.8))
    ax.annotate("", xy=(7.6, 2.05), xytext=(8.5, 2.6), arrowprops=dict(arrowstyle="->", color=vs.COUPLING, lw=0.8))
    ax.text(5.0, -0.3, "cartoon; wells = projects, dots = agents", fontsize=5.5, color=vs.MUTED, ha="center")


def make_fig():
    rng = np.random.default_rng(SEED)
    lab, proj = load_week("project")
    labw, _ = load_week("work")
    n_win = int(lab["win"].max()) + 1
    obs = pile_series(lab, n_win); obsw = pile_series(labw, n_win)
    nul = pile_null(lab, n_win, rng)
    lo, hi = np.quantile(nul, [0.025, 0.975], axis=0); mu = nul.mean(0)
    w, v = units_table()

    fig = plt.figure(figsize=(vs.W["double"], 4.7))
    gs = fig.add_gridspec(2, 2, width_ratios=[1, 1.55], height_ratios=[1, 1.08], hspace=0.62, wspace=0.22)
    ax_a = fig.add_subplot(gs[0, 0]); cartoon(ax_a)
    ax_a.set_title("(a) Potts picture", loc="left")

    # (b) #31 week
    ax = fig.add_subplot(gs[0, 1])
    x = np.arange(len(obs))
    ax.fill_between(x, lo, hi, step="mid", color=vs.NULL, alpha=0.55, lw=0, label="circular-shift null, 95%")
    ax.step(x, mu, where="mid", color=vs.MUTED, lw=0.8, ls="--")
    ax.step(x, obs, where="mid", color=vs.COUPLING, lw=1.5, label="attention (mentions)")
    ax.step(x, obsw, where="mid", color=vs.C["red"], lw=1.0, ls=(0, (3, 1.2)), label="work (commits)")
    for d in range(1, len(obs) // n_win):
        ax.axvline(d * n_win - 0.5, color=vs.GRID, lw=0.8, zorder=0)
    days = lab.select("day", "pt_date").unique().sort("day")["pt_date"].to_list()
    ax.set_xticks([d * n_win + n_win / 2 - 0.5 for d in range(len(days))], [d[5:] for d in days])
    ax.set_xlim(-0.5, len(obs) - 0.5); ax.set_ylim(0, 15.5)
    ax.set_ylabel("agents on the\nbusiest project")
    ax.set_xlabel("#31 (free week, Feb 2026), 30-min windows by day")
    k = int(np.argmax(obs))
    ax.annotate(f"{obs[k]} agents on one repo", (k, obs[k]), xytext=(k + 3.0, 12.2), fontsize=6.5,
                arrowprops=dict(arrowstyle="-", color=vs.INK2, lw=0.5), va="center")
    ax.legend(loc="upper left", fontsize=6, ncol=3, bbox_to_anchor=(0.0, 1.03), handlelength=1.6, columnspacing=1.0)
    ax.set_title("(b) one real week: piles beyond the null", loc="left")

    # order of units by ownership (attention)
    wa = w.filter(pl.col("space") == "attention").sort("own")
    order = wa["unit"].to_list()
    lbl = [u.replace("G", "#") if u.startswith("G") else "#" + u for u in order]
    own = dict(zip(wa["unit"], wa["own"]))
    xs = np.arange(len(order))

    # (c) co-location share vs N2 null
    ax = fig.add_subplot(gs[1, 0])
    for j, (space, mk, col, dx) in enumerate((("attention", "o", vs.COUPLING, -0.17), ("work", "s", vs.C["red"], 0.17))):
        t = w.filter(pl.col("space") == space)
        dd = {r["unit"]: r for r in t.iter_rows(named=True)}
        for i, u in enumerate(order):
            r = dd.get(u)
            if r is None or r["cowork"] is None:
                continue
            exc = r["cowork"] - r["cowork_N2"]
            sd = abs(exc / r["cowork_z"]) if r["cowork_z"] not in (None, 0) and np.isfinite(r["cowork_z"]) else np.nan
            if np.isfinite(sd):
                ax.add_patch(Rectangle((i + dx - 0.15, -1.96 * sd), 0.3, 3.92 * sd, color=vs.NULL, alpha=0.7, lw=0))
            ax.scatter(i + dx, exc, marker=mk, s=12, color=col, zorder=3, edgecolor="white", lw=0.3,
                       label=space if i == 0 else None)
    ax.axhline(0, color=vs.INK2, lw=0.6)
    ax.set_xticks(xs, lbl, rotation=90, fontsize=5.5)
    ax.set_xlim(-0.7, len(order) - 0.3)
    ax.set_ylabel("co-location share\nminus null mean")
    io = [i for i, u in enumerate(order) if own[u] >= 0.5]
    ax.axvspan(min(io) - 0.5, len(order) - 0.3, color=vs.C["orange"], alpha=0.08, lw=0)
    ax.text(min(io) - 0.3, 0.165, "own-artifact units", fontsize=5.5, color=vs.INK2)
    ax.text(0.0, 0.165, "shared-artifact", fontsize=5.5, color=vs.INK2)
    ax.set_ylim(-0.04, 0.18)
    h = [plt.Line2D([], [], marker="s", ls="", ms=5, color=vs.NULL)]
    ax.legend(h, ["N2 null, ±1.96 SD"], loc="upper right", fontsize=5.5, bbox_to_anchor=(1.0, 0.9))
    ax.set_title("(c) same-project co-location vs null", loc="left")

    # (d) coupling beyond agent fields: z_N2 per period, attention (all 14 tested) and work (#30+)
    ax = fig.add_subplot(gs[1, 1])
    ww = w.filter((pl.col("space") == "work") & pl.col("unit").str.starts_with("G"))
    wz = {int(r["goal"]): (r["z_N2"], r["tested"]) for r in ww.iter_rows(named=True)}
    wa_ = w.filter((pl.col("space") == "attention") & pl.col("unit").str.starts_with("G"))
    # attention: regime-I periods from the replication run; #30 onward from the work run (same run as the work z)
    rows = [(int(r["goal"]), r["z_N2"], r["own"]) for r in v.iter_rows(named=True) if r["goal"] < 30]
    rows += [(int(r["goal"]), r["z_N2"], r["own"]) for r in wa_.iter_rows(named=True)]
    rows.sort(key=lambda t: t[2])
    vv = pl.DataFrame(rows, schema=["goal", "z_N2", "own"], orient="row")
    goals = vv["goal"].to_list()
    xs = np.arange(len(goals))
    ax.axhspan(-2, 2, color=vs.NULL, alpha=0.45, lw=0, label="null, |z| < 2")
    ax.axhline(0, color=vs.INK2, lw=0.6)
    za = vv["z_N2"].to_numpy()
    ax.scatter(xs - 0.12, za, marker="o", s=16, color=vs.COUPLING, zorder=3, edgecolor="white", lw=0.3,
               label="attention")
    for i, g in enumerate(goals):
        if g in wz and wz[g][0] is not None and np.isfinite(wz[g][0]):
            tested = wz[g][1]
            ax.scatter(i + 0.12, wz[g][0], marker="s", s=14, zorder=3,
                       facecolor=vs.C["red"] if tested else "white",
                       edgecolor="white" if tested else vs.C["red"], linewidth=0.3 if tested else 0.8,
                       label="work (commits)" if g == 31 else None)
    ownv = vv["own"].to_numpy()
    io = np.flatnonzero(ownv >= 0.5)
    ax.axvspan(io.min() - 0.5, len(goals) - 0.5, color=vs.C["orange"], alpha=0.08, lw=0)
    ax.text(io.min() - 0.4, 11.8, "own artifacts", fontsize=5.5, color=vs.INK2)
    ax.set_xticks(xs, [f"#{g}" for g in goals], fontsize=6)
    ax.set_xlim(-0.6, len(goals) - 0.4)
    ax.set_ylim(-4, 23.5)
    ax.set_ylabel(r"$z_{N2}$: coupling beyond" "\n" "agent fields")
    ax.set_xlabel("goal period, sorted by artifact ownership index")
    i35 = goals.index(35) if 35 in goals else None
    if i35 is not None:
        ax.annotate(f"#35: {za[i35]:+.1f}".replace("-", "\u2212"), (i35 - 0.12, za[i35]), xytext=(i35 + 0.8, -3.3), fontsize=5.5,
                    arrowprops=dict(arrowstyle="-", lw=0.5, color=vs.INK2), va="center")
    ax.legend(loc="upper left", fontsize=6, ncol=3, bbox_to_anchor=(0.17, 1.02), columnspacing=0.8, handletextpad=0.3)
    ax.set_title("(d) herding per period, attention and work", loc="left")
    vs.save(fig, HERE / "fig")
    plt.close(fig)
    return obs, obsw, lo, hi


# ------------------------------------------------------------------------------------------------ animation
def make_anim(fps=24, sec_per_win=0.42, hold=1.2, preview=None):
    rng = np.random.default_rng(SEED)
    lab, proj = load_week("project")
    n_win = int(lab["win"].max()) + 1
    days = int(lab["day"].max()) + 1
    T = days * n_win
    top = proj.filter(pl.col("label") > 0).sort("label")["project"].to_list()
    wells = top + ["other"]
    K = len(wells)
    agents = sorted(lab["agent"].unique().to_list())
    names = dict(pl.read_parquet(ROOT / "data/processed/shared/roster.parquet").select("agent", "name").iter_rows())
    state = -np.ones((len(agents), T), int)          # -1 = no strict mention this window (off record)
    ai = {a: i for i, a in enumerate(agents)}
    for a, d, w_, p in lab.select("agent", "day", "win", "project").iter_rows():
        state[ai[a], d * n_win + w_] = wells.index(p) if p in top else K - 1
    occ = np.stack([(state == k).sum(0) for k in range(K)])          # K x T
    obs = pile_series(lab, n_win)
    nul = pile_null(lab, n_win, rng)
    lo, hi = np.quantile(nul, [0.025, 0.975], axis=0)
    wdates = pl.read_parquet(D / f"G{GOAL}/windows_w30.parquet").sort("day", "win")
    tmid = {(d, w_): t for d, w_, t in wdates.select("day", "win", "t_mid").iter_rows()}

    OFF_Y = -0.05
    wx = np.linspace(0.06, 0.94, K)
    width = 0.88 / K * 0.92

    def slot_pos(k, j):
        """Position of the j-th agent in well k (stacked from the well bottom); off-record row for k = -1."""
        if k < 0:
            return None
        return wx[k] + ((j % 4) - 1.5) * width * 0.2, 0.0 + (j // 4) * 0.07

    pos = np.zeros((len(agents), T, 2)); vis = np.zeros((len(agents), T))
    for t in range(T):
        cnt = np.zeros(K, int); off = 0
        for i in range(len(agents)):
            k = state[i, t]
            if k >= 0:
                x, y = slot_pos(k, cnt[k]); cnt[k] += 1; vis[i, t] = 1
            else:
                x, y = 0.04 + off * 0.06, OFF_Y; off += 1
            pos[i, t] = (x, y)
    # resolve final (x, y) per window with the bowl shape at that window's occupancy
    def bowl_y(k, px, depk):
        u = np.clip((px - wx[k]) / (width / 2), -1, 1)
        return 0.78 - (0.06 + 0.055 * depk) * (1 - u ** 2)
    XY = pos.copy()
    for t in range(T):
        for i in range(len(agents)):
            k = state[i, t]
            if k >= 0:
                XY[i, t, 1] = bowl_y(k, pos[i, t, 0], occ[k, t]) + 0.04 + pos[i, t, 1]

    fpw = int(round(sec_per_win * fps))
    n_frames = T * fpw + int(hold * fps)
    plt.rcParams.update({"font.size": 11})
    fig = plt.figure(figsize=(8, 4.5), dpi=160)
    axw = fig.add_axes([0.04, 0.33, 0.92, 0.50]); axw.axis("off")
    axw.set_xlim(0, 1); axw.set_ylim(-0.12, 1.0)
    axt = fig.add_axes([0.08, 0.08, 0.88, 0.2])
    fig.text(0.04, 0.95, "Agents herd onto shared projects (H11, goal period #31, real data)", fontsize=13,
             color=vs.INK, va="top")
    fig.text(0.04, 0.905, "each dot = one agent's project in a 30-min window; well depth = how many agents are in it",
             fontsize=8.5, color=vs.INK2, va="top")
    clock = fig.text(0.96, 0.95, "", fontsize=11, ha="right", va="top", color=vs.INK, family="monospace")
    for k, nm in enumerate(wells):
        axw.text(wx[k], 0.83, wrap(short(nm)) if nm != "other" else "other\nrepos", fontsize=6.6,
                 ha="center", va="bottom", color=vs.INK2, linespacing=1.0)
    axw.text(0.0, 0.0, "no project mention this window", fontsize=7, color=vs.MUTED, va="bottom")
    curves = [axw.plot([], [], color=vs.INK2, lw=1.2)[0] for _ in range(K)]
    fills = [None] * K
    dots = axw.scatter(pos[:, 0, 0], pos[:, 0, 1], s=46, color=vs.INK, edgecolor="white", lw=0.6, zorder=4)
    # bottom: pile vs null
    x = np.arange(T)
    axt.fill_between(x, lo, hi, step="mid", color=vs.NULL, alpha=0.6, lw=0)
    for d in range(1, days):
        axt.axvline(d * n_win - 0.5, color=vs.GRID, lw=0.8, zorder=0)
    line, = axt.step([], [], where="mid", color=vs.COUPLING, lw=1.8)
    cur = axt.axvline(0, color=vs.INK2, lw=0.6)
    axt.set_xlim(-0.5, T - 0.5); axt.set_ylim(0, 12.5)
    axt.set_xticks([d * n_win + n_win / 2 - 0.5 for d in range(days)],
                   [tmid[(d, 0)].strftime("%a %m-%d") for d in range(days)], fontsize=8)
    axt.set_ylabel("busiest\nproject", fontsize=8)
    axt.tick_params(labelsize=8)
    axt.text(T - 0.7, 11.6, "gray: circular-shift null (95%)   blue: observed", fontsize=7.5, ha="right",
             color=vs.INK2, va="center")

    def depth_at(tf):
        t0 = min(int(tf), T - 1); t1 = min(t0 + 1, T - 1); a = tf - int(tf)
        return (1 - a) * occ[:, t0] + a * occ[:, t1]

    def frame(f):
        tf = min(f / fpw, T - 1)
        t0 = min(int(tf), T - 1); t1 = min(t0 + 1, T - 1)
        a = tf - int(tf); a = a * a * (3 - 2 * a)          # smoothstep between windows
        P = (1 - a) * XY[:, t0] + a * XY[:, t1]
        moved = (state[:, t0] != state[:, t1])
        P[:, 1] = P[:, 1] + moved * 0.10 * np.sin(np.pi * a)     # small hop between wells
        dep = depth_at(tf)
        u = np.linspace(-1, 1, 30)
        for k in range(K):
            dk = 0.06 + 0.055 * dep[k]
            yy = 0.78 - dk * (1 - u ** 2) - 0.0
            curves[k].set_data(wx[k] + u * width / 2, yy)
            if fills[k] is not None:
                fills[k].remove()
            big = k < K - 1 and dep[k] >= max(dep[:-1].max() - 1e-9, 2)
            fills[k] = axw.fill_between(wx[k] + u * width / 2, yy, 0.78, color=vs.COUPLING if big else vs.NULL,
                                        alpha=0.35 if big else 0.25, lw=0)
        dots.set_offsets(P)
        tt = int(round(tf))
        line.set_data(x[: tt + 1], obs[: tt + 1]); cur.set_xdata([tt, tt])
        d, w_ = divmod(min(tt, T - 1), n_win)
        clock.set_text(tmid[(d, w_)].strftime("%Y-%m-%d %H:%M UTC"))
        return []

    if preview is not None:
        frame(preview); fig.savefig(HERE.parent / ".preview_H11.png"); plt.close(fig); return 0, names
    anim = animation.FuncAnimation(fig, frame, frames=n_frames, interval=1000 / fps, blit=False)
    anim._save_count = n_frames
    k_peak = int(np.argmax(obs))
    vs.save_anim(anim, HERE / "anim", fps=fps, dpi=160, poster_frame=k_peak * fpw)
    plt.close(fig)
    return n_frames / fps, names


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--no-anim", action="store_true")
    ap.add_argument("--preview", type=int, default=None); a = ap.parse_args()
    vs.use()
    if a.preview is not None:
        make_anim(preview=a.preview); sys.exit()
    obs, obsw, lo, hi = make_fig()
    print("peak attention pile", obs.max(), "peak work pile", obsw.max(), "windows above null 97.5%:",
          int((obs > hi).sum()), "of", len(obs))
    if not a.no_anim:
        vs.use()
        dur, _ = make_anim()
        print(f"anim {dur:.1f} s")
