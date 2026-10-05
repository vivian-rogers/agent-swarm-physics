"""H102 visuals: rooms with different work are two content domains, but the wall between them is empty; hoppers switch
sides with the room they speak in.

Static (fig.pdf/png, double column):
  (a) schematic: the coupling model's wall (hoppers sit inside it, s ~ kappa p) vs the observed sharp wall (a hopper's
      content follows the room of the statement);
  (b) bimodality D per unit against the room-relabel null (gray: null 95th percentile), from H102's results;
  (c) unit 51g (#general vs #focus): wall-coordinate distribution of statements (stayers in #general, residents in
      #focus; shared pipeline), stayers' leave-one-out positions (rug) and the hoppers' positions by room of statement;
  (d) dose-response: hopper-day s(home) vs hopping read-outs, with H102's fitted kappa_R and the powered coupling
      alternative kappa = 0.1.
Animation (writeup/animations/H102-room-domain-walls.mp4): the three #general hoppers with #focus statements in 51g (Claude Fable 5, Gemini 3.5 Flash,
  GLM-5.2) as tokens on the wall axis over 08-05..08-21; each token is the running mean of the agent's statements in its
  current room stay; dots below are the individual statements, coloured by room.

Wall axis: H102's rule (day-centred bge style-residualized statement vectors; centroids of the core stayers' home-room
statements, full data; s = 0 at the #general centroid, 1 at the #focus centroid). Reproduces H102's hopper s(all) and
s(#focus) exactly (Fable 5: 0.063, 0.154).

Run: uv run python writeup/visuals/H102-room-domain-walls/make.py [--static] [--anim]
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
import polars as pl  # noqa: E402
from matplotlib import animation  # noqa: E402
from matplotlib.gridspec import GridSpec  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import FancyArrowPatch  # noqa: E402

import vstyle as vs  # noqa: E402

D102 = rc.PROC / "H102-room-domain-walls"
RAW = rc.load_json("H102-room-domain-walls/results/raw_bge_small_style_resid.json")
C_GEN, C_FOC = vs.ROOM["#general"], vs.ROOM["#focus"]
HOPPERS = [31, 27, 34]                     # #general hoppers with >= 5 statements in #focus (H102 Amendment 0)
HMARK = {31: "o", 27: "^", 34: "D"}


def wall_data():
    """51g statements on the wall axis (H102 rule, shared pipeline)."""
    s102 = pl.read_parquet(D102 / "statements.parquet").filter(pl.col("unit") == "51g")
    dom = pl.read_parquet(D102 / "domains.parquet").filter(pl.col("unit") == "51g")
    st, X = rc.load_statements(date_range=(s102["pt_date"].min(), s102["pt_date"].max()))
    keep = st["srow"].is_in(s102["srow"].implode()).to_numpy()
    st, X = st.filter(pl.Series(keep)), X[keep]
    assert st.height == s102.height
    Xc = rc.day_center(st, X)
    st = st.join(dom.select(pl.col("agent").cast(pl.Int8), "home", "role"), on="agent", how="left")
    ag, room, home = st["agent"].to_numpy(), st["room_at"].to_numpy(), st["home"].to_numpy()
    core = [a for a, r in zip(dom["agent"], dom["role"]) if r in ("stayer", "core")]
    hm = dict(zip(dom["agent"], dom["home"]))
    full = {a: Xc[(ag == a) & (room == home)].mean(0) for a in core}
    cG = np.mean([full[a] for a in core if hm[a] == rc.GENERAL], 0)
    cF = np.mean([full[a] for a in core if hm[a] == rc.FOCUS], 0)
    u = cF - cG
    s = (Xc - cG) @ u / (u @ u)
    return st.with_columns(pl.Series("s", s)), dom


# ============================================================================ static
def hills(ax, y0, labelled=False):
    x = np.linspace(-0.6, 1.6, 300)
    g = np.exp(-x ** 2 / (2 * 0.16 ** 2)); f = np.exp(-(x - 1) ** 2 / (2 * 0.16 ** 2))
    ax.fill_between(x, y0, y0 + 0.55 * g, color=C_GEN, alpha=0.35, lw=0)
    ax.fill_between(x, y0, y0 + 0.55 * f, color=C_FOC, alpha=0.35, lw=0)
    ax.plot([-0.6, 1.6], [y0, y0], color=vs.INK2, lw=0.6)
    if labelled:
        ax.text(0, y0 + 0.6, "#general\ndomain", ha="center", va="bottom", fontsize=6.3, color=C_GEN)
        ax.text(1, y0 + 0.6, "#focus\ndomain", ha="center", va="bottom", fontsize=6.3, color=C_FOC)


def panel_schematic(ax):
    hills(ax, 1.25, labelled=True); hills(ax, 0.0)
    ax.add_patch(plt.Rectangle((0.25, 1.25), 0.5, 0.55, color=vs.NULL, alpha=0.35, lw=0))
    ax.scatter([0.45], [1.36], marker="o", s=26, color=vs.INK, zorder=4)
    ax.text(0.5, 1.88 + 0.33, "coupling model: hopper inside the wall,\n$s\\approx\\kappa\\,p$ (read share $p$)",
            ha="center", va="bottom", fontsize=6.3)
    ax.text(0.5, 1.76, "wall interior", ha="center", va="top", fontsize=5.8, color=vs.MUTED)
    ax.scatter([0.06], [0.11], marker="o", s=26, color=C_GEN, edgecolor=vs.INK, lw=0.5, zorder=4)
    ax.scatter([0.33], [0.11], marker="o", s=26, color=C_FOC, edgecolor=vs.INK, lw=0.5, zorder=4)
    ax.add_patch(FancyArrowPatch((0.1, 0.24), (0.3, 0.24), connectionstyle="arc3,rad=-0.5", arrowstyle="<|-|>",
                                 mutation_scale=6, color=vs.INK2, lw=0.7))
    ax.text(0.5, 0.75, "observed: content follows the room it is\nsaid in; home talk stays in its domain",
            ha="center", va="bottom", fontsize=6.3)
    ax.text(-0.04, -0.08, "in #general", ha="center", va="top", fontsize=5.8, color=C_GEN)
    ax.text(0.46, -0.08, "in #focus", ha="center", va="top", fontsize=5.8, color=C_FOC)
    ax.set_xlim(-0.6, 1.6); ax.set_ylim(-0.3, 2.75)
    ax.set_xticks([0, 1], ["0", "1"]); ax.set_yticks([])
    ax.spines["left"].set_visible(False); ax.grid(False)
    ax.set_xlabel("wall coordinate $s$")
    ax.set_title("(a) schematic: domains and the wall", loc="left")


def panel_D(ax):
    units = ["G35", "G36", "G37", "G38", "G39", "G41", "G42", "G44", "51g"]
    for i, k in enumerate(units):
        b = RAW["units"][k]["bimodality"]
        ax.add_patch(plt.Rectangle((i - 0.3, 0), 0.6, b["D_null_p95"], color=vs.NULL, alpha=0.6, lw=0))
        split = k in ("G38", "G41", "G44", "51g")
        ax.scatter(i, b["D"], s=20, color=vs.COUPLING if split else vs.INK2, marker="D" if split else "o", zorder=3)
    ax.axhline(2, color=vs.MUTED, lw=0.7, ls="--")
    ax.text(-0.45, 2.1, "$D=2$: two modes", fontsize=6, color=vs.MUTED, ha="left", va="bottom")
    ax.set_xticks(range(len(units)), [f"#{k[1:]}" if k[0] == "G" else "#51g" for k in units], fontsize=6.5)
    for t, k in zip(ax.get_xticklabels(), units):
        if k in ("G38", "G44"):
            t.set_color(vs.FIELD)
    ax.set_ylim(0, 8.6); ax.set_ylabel("bimodality $D$ (stayers)")
    ax.set_title("(b) two domains where rooms do different work", loc="left")
    h = [Line2D([], [], marker="D", ls="", color=vs.COUPLING, ms=4, label="different work"),
         Line2D([], [], marker="o", ls="", color=vs.INK2, ms=4, label="identical kickoffs / forks"),
         plt.Rectangle((0, 0), 1, 1, color=vs.NULL, alpha=0.6, label="relabel null, 95th pct.")]
    ax.legend(handles=h, loc="upper left", fontsize=6.2, handlelength=1.2, borderaxespad=0.2)


def panel_wall(ax, st):
    g = RAW["units"]["51g"]; hp = g["hoppers"]
    s, ag, room, role = st["s"].to_numpy(), st["agent"].to_numpy(), st["room_at"].to_numpy(), st["role"].to_numpy()
    bins = np.linspace(-1.0, 2.0, 61)
    mG = (role == "stayer") & (room == rc.GENERAL)
    mF = (role == "core") & (room == rc.FOCUS)
    for m, col, lab in ((mG, C_GEN, f"#general stayers' statements ({mG.sum():,})"),
                        (mF, C_FOC, f"#focus residents' statements ({mF.sum():,})")):
        hgt, _ = np.histogram(s[m], bins=bins, density=True)
        ax.stairs(hgt, bins, fill=True, color=col, alpha=0.35, lw=0)
        ax.stairs(hgt, bins, color=col, lw=0.8, label=lab)
    ax.axvspan(0.25, 0.75, color=vs.NULL, alpha=0.25, lw=0)
    ax.text(0.5, 2.55, "wall\ninterior", ha="center", va="top", fontsize=6, color=vs.MUTED)
    # stayers' leave-one-out agent positions (N2 null distribution) as a rug; residents at 1 - s(home)
    st_s = [v for a, v in hp["stayers"].items() if int(a) not in (6, 29)]
    ax.plot(st_s, np.full(len(st_s), -0.12), "|", color=C_GEN, ms=6, mew=0.8)
    ax.plot([1 - hp["stayers"]["6"], 1 - hp["stayers"]["29"]], [-0.12, -0.12], "|", color=C_FOC, ms=6, mew=0.8)
    ax.axvline(hp["home_stayers_p95"], color=vs.INK2, lw=0.7, ls=":")
    ax.text(hp["home_stayers_p95"] + 0.03, -0.36, "#general stayers' 95th pct.", fontsize=5.8, color=vs.INK2,
            va="center")
    names = rc.roster()
    ys = {31: 3.35, 27: 3.0, 34: 2.65}
    for a in HOPPERS:
        r = hp["hoppers"][str(a)]
        y = ys[a]
        ax.plot([r["s_home"], r["s_other"]], [y, y], color=vs.INK2, lw=0.7)
        ax.scatter(r["s_home"], y, marker=HMARK[a], s=24, color=C_GEN, edgecolor=vs.INK, lw=0.5, zorder=4)
        ax.scatter(r["s_other"], y, marker=HMARK[a], s=24, color=C_FOC, edgecolor=vs.INK, lw=0.5, zorder=4)
        ax.text(max(r["s_other"], r["s_home"]) + 0.07, y, f"{names[a]} ({r['n_other']} in #focus)", fontsize=6,
                va="center")
    ax.set_xlim(-1.0, 2.0); ax.set_ylim(-0.48, 3.6)
    ax.set_yticks([0, 1, 2])
    ax.set_xlabel("wall coordinate $s$  (0 = #general, 1 = #focus centroid)")
    ax.set_ylabel("statement density")
    ax.set_title("(c) #51g: hoppers switch sides, the wall stays empty", loc="left")
    h = [Line2D([], [], color=C_GEN, lw=4, alpha=0.5, label="#general stayers (statements)"),
         Line2D([], [], color=C_FOC, lw=4, alpha=0.5, label="#focus residents (statements)"),
         Line2D([], [], marker="o", ls="", color=C_GEN, mec=vs.INK, ms=4, label="hopper, said in #general"),
         Line2D([], [], marker="o", ls="", color=C_FOC, mec=vs.INK, ms=4, label="hopper, said in #focus")]
    ax.legend(handles=h, loc="center right", bbox_to_anchor=(1.0, 0.56), fontsize=5.9, handlelength=1.3,
              borderaxespad=0.2)


def panel_dose(ax):
    g = RAW["units"]["51g"]; hp = g["hoppers"]["hoppers"]; dose = g["dose"]
    rd = pl.read_parquet(D102 / "reads_day.parquet").filter(pl.col("unit") == "51g")
    rdd = {(str(x["agent"]), x["pt_date"]): x for x in rd.to_dicts()}
    rows = []
    for k, rec in hp.items():
        for d, v in rec["days"].items():
            if v["s_home"] is None or v["n_home"] < 3 or (k, d) not in rdd:
                continue
            rows.append((k, v["s_home"], v["n_home"], np.log1p(rdd[(k, d)]["R_hop"])))
    k_, y, w, R = map(np.array, zip(*rows))
    yd, Rd = y.copy(), R.copy()
    for a in np.unique(k_):
        m = k_ == a
        yd[m] -= np.average(y[m], weights=w[m]); Rd[m] -= np.average(R[m], weights=w[m])
    Rm = np.average(R, weights=w)
    xs = np.linspace(-1.2, 2.2, 50)
    kap, (lo, hi) = dose["kappa_R"], dose["kappa_R_ci_day"]
    ax.fill_between(xs + Rm, lo * xs, hi * xs, color=vs.COUPLING, alpha=0.18, lw=0)
    ax.plot(xs + Rm, kap * xs, color=vs.COUPLING, lw=1.5)
    ax.plot(xs + Rm, 0.1 * xs, color=vs.INK2, lw=1.0, ls="--")
    for a in np.unique(k_):
        m = k_ == a
        mk = HMARK.get(int(a), "s")
        ax.scatter(Rd[m] + Rm, yd[m], s=6 + 0.25 * w[m], marker=mk, facecolor="none", edgecolor=vs.INK2, lw=0.6,
                   zorder=3)
    ax.text(2.2 + Rm, 0.1 * 2.2, "coupling $\\kappa=0.1$\n(synthetic power $\\geq$ 0.93)", fontsize=6, ha="right",
            va="bottom", color=vs.INK2)
    ax.text(0.03, 0.04, f"fit $\\kappa_R={kap:.3f}$ [{lo:.3f}, {hi:.3f}] per e-fold", transform=ax.transAxes,
            fontsize=6.3, color=vs.COUPLING)
    ax.text(0.97, 0.04, "shapes as in (c); squares: other hoppers", transform=ax.transAxes, fontsize=5.8,
            color=vs.MUTED, ha="right")
    ax.set_xlabel("hopping read-outs that day, $\\ln(1+R)$")
    ax.set_ylabel("hopper-day $s$(#general talk), within-hopper")
    ax.set_ylim(-0.45, 0.45)
    ax.set_title("(d) no dose-response on reading the other room", loc="left")


def make_static():
    vs.use()
    st, _ = wall_data()
    fig = plt.figure(figsize=(vs.W["double"], 4.9))
    gs = GridSpec(2, 2, figure=fig, width_ratios=[1, 1.35], hspace=0.55, wspace=0.25, left=0.075, right=0.985,
                  top=0.94, bottom=0.10)
    panel_schematic(fig.add_subplot(gs[0, 0]))
    panel_D(fig.add_subplot(gs[1, 0]))
    panel_wall(fig.add_subplot(gs[0, 1]), st)
    panel_dose(fig.add_subplot(gs[1, 1]))
    vs.save(fig, HERE / "fig")
    plt.close(fig)


# ============================================================================ animation
def make_anim():
    st, dom = wall_data()
    days = sorted(st["pt_date"].unique().to_list())
    # compressed active clock: each day spans [k, k+1] from its first to last statement in the unit
    t = st["t"].dt.epoch("us").to_numpy() / 3.6e9
    dk = {d: k for k, d in enumerate(days)}
    clock = np.empty(len(t))
    dcol = st["pt_date"].to_numpy()
    for d in days:
        m = dcol == d
        t0, t1 = t[m].min(), t[m].max()
        clock[m] = dk[d] + (t[m] - t0) / (t1 - t0)
    st = st.with_columns(pl.Series("clock", clock))
    s_all, room_all, role = st["s"].to_numpy(), st["room_at"].to_numpy(), st["role"].to_numpy()
    mG = (role == "stayer") & (room_all == rc.GENERAL); mF = (role == "core") & (room_all == rc.FOCUS)
    names = rc.roster()
    H = {}
    for a in HOPPERS:
        sub = st.filter(pl.col("agent") == a).sort("clock")
        H[a] = dict(c=sub["clock"].to_numpy(), s=sub["s"].to_numpy(), r=sub["room_at"].to_numpy())
        # token: running mean within the current room stay (last 15 statements)
        tok = np.empty(len(sub)); start = 0
        for i in range(len(sub)):
            if i > 0 and H[a]["r"][i] != H[a]["r"][i - 1]:
                start = i
            tok[i] = H[a]["s"][max(start, i - 14):i + 1].mean()
        H[a]["tok"] = tok
    raw = RAW["units"]["51g"]["hoppers"]["hoppers"]

    vs.use()
    plt.rcParams.update({"font.size": 12, "axes.titlesize": 12.5, "axes.labelsize": 11.5, "xtick.labelsize": 10,
                         "ytick.labelsize": 10, "legend.fontsize": 10, "savefig.bbox": "standard"})
    fig = plt.figure(figsize=(8, 4.5), dpi=160)
    gs = GridSpec(4, 1, figure=fig, height_ratios=[2.0, 1, 1, 1], left=0.17, right=0.80, top=0.84, bottom=0.145,
                  hspace=0.18)
    axl = fig.add_subplot(gs[0])
    axr = [fig.add_subplot(gs[i + 1], sharex=axl) for i in range(3)]
    fig.text(0.02, 0.955, "Domains without a wall: a hopper's talk follows its room", fontsize=15, fontweight="bold",
             ha="left", va="center")
    fig.text(0.02, 0.905, "#51g: #general vs the agent-made #focus room · tokens = mean of a hopper's recent statements "
             "in its current room", fontsize=9.5, ha="left", va="center", color=vs.INK2)
    clk = fig.text(0.98, 0.955, "", fontsize=12, ha="right", va="center", family="monospace")
    fig.text(0.02, 0.022, "H102 · bge style-resid. statement vectors, day-centred; axis between the core stayers' "
             "centroids (s = 0 #general, 1 #focus)", fontsize=7.5, ha="left", va="center", color=vs.MUTED)
    bins = np.linspace(-1.0, 2.0, 61)
    for m, col in ((mG, C_GEN), (mF, C_FOC)):
        hgt, _ = np.histogram(s_all[m], bins=bins, density=True)
        axl.stairs(hgt, bins, fill=True, color=col, alpha=0.3, lw=0); axl.stairs(hgt, bins, color=col, lw=0.8)
    axl.axvspan(0.25, 0.75, color=vs.NULL, alpha=0.25, lw=0)
    axl.text(-0.75, 3.0, "#general domain", ha="left", va="top", fontsize=10, color=C_GEN)
    axl.text(1.75, 3.0, "#focus domain", ha="right", va="top", fontsize=10, color=C_FOC)
    axl.text(0.5, 3.0, "wall", ha="center", va="top", fontsize=9, color=vs.MUTED)
    axl.set_ylim(0, 3.2); axl.set_yticks([]); axl.set_xlim(-0.8, 1.8)
    axl.tick_params(labelbottom=False)
    tokens = {a: axl.scatter([], [], s=150, marker=HMARK[a], edgecolor=vs.INK, lw=1.0, zorder=5) for a in HOPPERS}
    toklab = {a: axl.text(0, 0, "", fontsize=8.5, ha="left", va="center", zorder=6) for a in HOPPERS}
    tok_y = {31: 2.15, 27: 1.4, 34: 0.65}
    dots, runtxt = {}, {}
    for i, a in enumerate(HOPPERS):
        ax = axr[i]
        ax.axvspan(0.25, 0.75, color=vs.NULL, alpha=0.25, lw=0)
        ax.axvline(0, color=C_GEN, lw=0.8, alpha=0.6); ax.axvline(1, color=C_FOC, lw=0.8, alpha=0.6)
        ax.set_ylim(-0.5, 0.5); ax.set_yticks([])
        ax.set_ylabel(names[a], rotation=0, ha="right", va="center", fontsize=10)
        dots[a] = ax.scatter([], [], s=10, zorder=3)
        runtxt[a] = ax.text(1.02, 0.5, "", transform=ax.transAxes, fontsize=8.5, va="center", ha="left")
        if i < 2:
            ax.tick_params(labelbottom=False)
    axr[-1].set_xlabel("wall coordinate s")
    fig.legend(handles=[Line2D([], [], marker="o", ls="", color=C_GEN, ms=5, label="said in #general"),
                        Line2D([], [], marker="o", ls="", color=C_FOC, mec=vs.INK, ms=6, label="said in #focus")],
               loc="upper left", bbox_to_anchor=(0.805, 0.85), fontsize=8.5, handletextpad=0.2,
               title="one dot = one statement\nmean s by room (n):", title_fontsize=8.5, alignment="left")
    rng = np.random.default_rng(0)
    jit = {a: rng.uniform(-0.38, 0.38, len(H[a]["s"])) for a in HOPPERS}
    for a in HOPPERS:
        tokens[a].set_offsets(np.empty((0, 2)))

    FADE, HOLD = 12, 36
    n_main = 456
    T = np.concatenate([np.zeros(FADE), np.linspace(0, len(days), n_main), np.full(HOLD + FADE, len(days))])
    n_frames = len(T)

    def draw(fi):
        tc = T[fi]
        alpha = min(1.0, fi / FADE) if fi < FADE else (1 - (fi - (n_frames - FADE)) / FADE if fi >= n_frames - FADE
                                                       else 1.0)
        k = min(int(tc), len(days) - 1)
        clk.set_text(f"{days[k]}  (day {k + 1}/{len(days)})")
        for a in HOPPERS:
            h = H[a]
            n = int(np.searchsorted(h["c"], tc, side="right")) if fi >= FADE else 0
            if n == 0:
                dots[a].set_offsets(np.empty((0, 2))); tokens[a].set_offsets(np.empty((0, 2))); toklab[a].set_text("")
                runtxt[a].set_text(""); continue
            age = tc - h["c"][:n]
            al = np.clip(1 - age / 3.0, 0.12, 1.0)
            cols = np.array([matplotlib.colors.to_rgba(C_FOC if r == rc.FOCUS else C_GEN) for r in h["r"][:n]])
            cols[:, 3] = al * alpha
            isF = h["r"][:n] == rc.FOCUS
            cols[isF, 3] = alpha
            dots[a].set_offsets(np.column_stack([h["s"][:n], jit[a][:n]])); dots[a].set_facecolor(cols)
            dots[a].set_sizes(np.where(isF, 34, 9))
            dots[a].set_edgecolor(np.where(isF[:, None], np.array([matplotlib.colors.to_rgba(vs.INK)]),
                                           np.array([[0, 0, 0, 0]])))
            r_now = h["r"][n - 1]
            tokens[a].set_offsets([[h["tok"][n - 1], tok_y[a]]])
            tokens[a].set_facecolor(C_FOC if r_now == rc.FOCUS else C_GEN); tokens[a].set_alpha(alpha)
            toklab[a].set_position((h["tok"][n - 1] + 0.07, tok_y[a]))
            toklab[a].set_text(names[a].replace("Claude ", "").replace("Gemini ", "Gemini "))
            toklab[a].set_alpha(alpha)
            sg = h["s"][:n][~isF]; sf = h["s"][:n][isF]
            txt = f"#general: {sg.mean():+.2f} ({len(sg)})"
            txt += f"\n#focus: {sf.mean():+.2f} ({len(sf)})" if len(sf) else "\n#focus: –"
            runtxt[a].set_text(txt); runtxt[a].set_alpha(alpha)
        return []

    anim = animation.FuncAnimation(fig, draw, frames=n_frames, interval=1000 / 24, blit=False)
    w = animation.FFMpegWriter(fps=24, codec="h264", bitrate=2400,
                               extra_args=["-pix_fmt", "yuv420p", "-movflags", "+faststart"])
    if "--poster-only" not in sys.argv:
        anim.save(HERE.parent.parent / "animations" / (HERE.name + ".mp4"), writer=w, dpi=160)
    draw(n_frames - FADE - 1)
    fig.savefig(HERE.parent.parent / "animations" / (HERE.name + "_poster.png"), dpi=160)
    plt.close(fig)
    # the final running means must equal H102's s(home) and s(#focus) for these hoppers
    for a in HOPPERS:
        h = H[a]; isF = h["r"] == rc.FOCUS
        print(names[a], round(h["s"][~isF].mean(), 3), round(h["s"][isF].mean(), 3), "| H102:",
              round(raw[str(a)]["s_home"], 3), round(raw[str(a)]["s_other"], 3))
    print(f"frames {n_frames} = {n_frames / 24:.1f} s")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or "--static" in args:
        make_static()
    if not args or "--anim" in args:
        make_anim()
