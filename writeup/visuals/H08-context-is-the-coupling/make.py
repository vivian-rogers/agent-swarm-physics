"""H08 writeup visual: coupling acts at the recipient's receiving call (context ledger, round 1b).

    uv run python writeup/visuals/H08-context-is-the-coupling/make.py            # fig + animation
    uv run python writeup/visuals/H08-context-is-the-coupling/make.py --no-anim  # fig only

Writes fig.pdf (double column, a|b|c) and the single-column fig_a.pdf, fig_bc.pdf used by writeup/papers/thermodynamics.

Reads only processed outputs: data/processed/H08-context-is-the-coupling/r1b/ (c9.json per period, G38 readout and
turns), plus the shared chat_core (message time, room, sender; no text) and roster (names). Non-holdout only; the
example day is checked against the locked holdout.
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
from matplotlib.patches import FancyArrowPatch, Rectangle  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "writeup/visuals"))
sys.path.insert(0, str(ROOT / "infra/shared"))
import vstyle as vs  # noqa: E402
from common import holdout_mask  # noqa: E402

D = ROOT / "data/processed/H08-context-is-the-coupling/r1b"
SH = ROOT / "data/processed/shared"
PERIODS = ["G24", "G25", "G26", "G27", "G30", "G31", "G33", "G35", "G36", "G37", "G38", "G39", "G40", "G41", "G42",
           "G44", "G51"]
EX_PERIOD = "G38"
US = 1_000_000
INFL = "#5f5f5f"          # in-flight call (darker gray)
CALL = "#cfcfcf"          # ordinary call


# ------------------------------------------------------------------------------------------- data
def load_c9():
    out = {}
    for g in PERIODS:
        out[g] = json.loads((D / g / "c9.json").read_text())
    return out


def regime_of(g):
    s = json.loads((D / "summary_r1b.json").read_text())
    return {p["period"]: p["regime"] for p in s["periods"]}[g]


def pick_example():
    """A G38 agent message read by several room-mates, most of them mid-call when it arrived, with replies to the
    sender at the receiving call and none at the in-flight call."""
    R = pl.read_parquet(D / EX_PERIOD / "readout.parquet").filter(~pl.col("placebo") & (pl.col("sender") >= 0))
    R = R.with_columns((pl.col("yauth").cast(pl.Int32) // 8 % 2).alias("a1"),
                       (pl.col("yauth").cast(pl.Int32) // 4 % 2).alias("a0"))
    g = R.group_by("msg").agg(pl.len().alias("n"), pl.col("a1").sum().alias("rep1"), pl.col("a0").sum().alias("rep0"),
                              pl.col("inflight").sum().alias("infl"), pl.col("W_s").max().alias("Wmax"))
    c = g.filter((pl.col("rep1") >= 2) & (pl.col("infl") >= 3) & (pl.col("rep0") == 0) & (pl.col("Wmax") < 200)
                 & (pl.col("n") >= 5) & (pl.col("n") <= 8)).sort(["rep1", "n", "msg"], descending=[True, True, False])
    msg = int(c["msg"][0])
    rows = R.filter(pl.col("msg") == msg)
    chat = pl.read_parquet(SH / "chat_core.parquet", columns=["t", "pt_date", "goal_no", "room", "agent"])
    m = chat.row(msg, named=True)
    assert not holdout_mask([m["pt_date"]], [int(m["goal_no"])])[0], "example day is in the holdout"
    t_m = int(m["t"].timestamp() * US)
    sender = int(m["agent"])
    rec = rows.sort("W_s")["agent"].to_list()
    T = pl.read_parquet(D / EX_PERIOD / "turns.parquet").filter(
        (pl.col("pt_date") == m["pt_date"]) & pl.col("agent").is_in([sender] + rec)).sort("agent", "s_us")
    names = dict(zip(*pl.read_parquet(SH / "roster.parquet", columns=["agent", "name"]).to_dict(as_series=False).values()))
    lanes = []
    for a in [sender] + rec:
        sub = T.filter(pl.col("agent") == a)
        s = sub["s_us"].to_numpy(); t = sub["t_us"].to_numpy()
        talk = sub["talk"].fill_null(False).to_numpy()
        pa = sub["par_auth"].to_numpy().astype(np.uint64)
        ln = dict(agent=a, name=names[a], s=(s - t_m) / US, t=(t - t_m) / US, talk=talk,
                  reply=talk & (((pa >> np.uint64(sender)) & np.uint64(1)) == 1))
        if a != sender:
            k = int(np.searchsorted(s, t_m, side="right"))          # receiving call (first t_call > t_m)
            ln["recv"] = k
            ln["infl"] = k - 1 if (k > 0 and t[k - 1] > t_m) else None
            ln["W"] = (s[k] - t_m) / US
            ln["replied"] = bool(ln["reply"][k])
            wd = float(rows.filter(pl.col("agent") == a)["Wc_s"][0])
            assert abs(wd - ln["W"]) < 1e-3, (a, wd, ln["W"])  # same receiving call as the H08 table
        lanes.append(ln)
    return dict(msg=msg, room=int(m["room"]), day=m["pt_date"], lanes=lanes)


# ------------------------------------------------------------------------------------------- drawing
def draw_raster(ax, ex, x0=-35, x1=None, upto=None, show_reply=True, fs=7):
    lanes = ex["lanes"]
    x1 = x1 or max(l["W"] for l in lanes[1:]) + 35
    n = len(lanes)
    for i, l in enumerate(lanes):
        y = n - 1 - i
        for j, (s, t) in enumerate(zip(l["s"], l["t"])):
            if t < x0 or s > x1:
                continue
            col, lw = CALL, 0
            if i > 0 and j == l.get("infl"):
                col = INFL
            if i > 0 and j == l.get("recv") and (upto is None or upto >= s):
                col = vs.COUPLING
            ax.add_patch(Rectangle((s, y - 0.17), max(t - s, 1.2), 0.34, color=col, lw=lw, zorder=2))
        lab = l["name"] + ("  (sender)" if i == 0 else "")
        ax.text(x0 - 3, y, lab, ha="right", va="center", fontsize=fs, color=vs.INK)
        if i > 0:
            k = l["recv"]
            show = upto is None or upto >= 0
            if show:
                end = l["s"][k] if upto is None else min(l["s"][k], upto)
                ax.plot([0, end], [y, y], color=vs.COUPLING, lw=1.0, ls=(0, (1.5, 1.5)), zorder=3)
            if show_reply and l["replied"] and (upto is None or upto >= l["t"][k]):
                ax.plot([l["t"][k]], [y], marker="v", color=vs.COUPLING, ms=5, zorder=5, mec="white", mew=0.5)
    if upto is None or upto >= 0:
        ax.plot([0], [n - 1], marker="*", color=vs.COUPLING, ms=9, zorder=6, mec="white", mew=0.5)
    ax.axvline(0, color=vs.MUTED, lw=0.6, ls="--", zorder=1)
    ax.set_xlim(x0, x1); ax.set_ylim(-0.7, n - 0.4)
    ax.set_yticks([]); ax.spines["left"].set_visible(False); ax.grid(False)
    return x1


def panel_a(ax, ex, fs=6.5, ncol=4):
    """(a) one real message: calls, in-flight call, receiving call, replies."""
    from matplotlib.lines import Line2D
    draw_raster(ax, ex, fs=fs)
    ax.set_xlabel("time since the message (s)")
    ax.set_title("(a) one message, %s %s" % (EX_PERIOD, ex["day"]), loc="left")
    h = [Rectangle((0, 0), 1, 1, color=CALL), Rectangle((0, 0), 1, 1, color=INFL),
         Rectangle((0, 0), 1, 1, color=vs.COUPLING),
         Line2D([], [], marker="v", ls="", color=vs.COUPLING, ms=5)]
    ax.set_ylim(-1.75 if ncol == 4 else -2.6, len(ex["lanes"]) - 0.4)
    ax.legend(h, ["model call", "in flight at the post", "receiving call", "reply to sender"], loc="lower center",
              fontsize=6, handlelength=1.2, borderaxespad=0.1, ncol=ncol, columnspacing=0.9)


def panel_b(ax, c9, title="(b) %s, 17 days" % EX_PERIOD):
    """(b) G38 offset profile: own room vs other-room placebo (mentions, the pre-registered response)."""
    d = c9[EX_PERIOD]
    o = np.arange(-2, 4)
    for key, col, lab, mk in (("other_room", vs.NULL, "other-room placebo", "s"), ("primary", vs.COUPLING, "own room", "o")):
        G = np.array([d[key]["addr"]["G"][str(k)] for k in o]) * 100
        ax.fill_between(o, G[:, 1], G[:, 2], color=col, alpha=0.25 if key == "primary" else 0.5, lw=0)
        ax.plot(o, G[:, 0], "-", marker=mk, color=col if key == "primary" else vs.INK2, ms=3.2, lw=1.2, label=lab,
                mfc=col if key == "primary" else "white")
    ax.axhline(0, color=vs.INK2, lw=0.5)
    ax.axvspan(-0.5, 0.5, color=INFL, alpha=0.10, lw=0)
    ax.axvspan(0.5, 1.5, color=vs.COUPLING, alpha=0.08, lw=0)
    ax.set_xticks(o)
    ax.set_xticklabels(["−2", "−1", "0", "1", "2", "3"])
    ax.text(0, -0.15, "in\nflight", ha="center", va="center", fontsize=5.5, color=vs.INK2, linespacing=0.9)
    ax.text(1, -0.15, "recv.\ncall", ha="center", va="center", fontsize=5.5, color=vs.COUPLING, linespacing=0.9)
    ax.set_ylim(-0.26, 1.75)
    ax.set_xlabel("recipient's call offset $o$")
    ax.set_ylabel("addresses sender: excess (pp)")
    ax.set_title(title, loc="left")
    ax.legend(loc="upper left", fontsize=6, handlelength=1.4)
    ax.set_xlim(-2.4, 3.4)


def panel_c(ax, c9, title="(c) all 17 periods"):
    """(c) jump D per period, with the other-room null."""
    from matplotlib.lines import Line2D
    y = np.arange(len(PERIODS))[::-1]
    for yi, g in zip(y, PERIODS):
        dd = c9[g]
        Da = np.array(dd["primary"]["auth"]["D"]) * 100
        Dm = np.array(dd["primary"]["addr"]["D"]) * 100
        ax.plot(Da[1:], [yi + 0.14] * 2, color=vs.COUPLING, lw=1.1)
        ax.plot(Da[0], yi + 0.14, "o", color=vs.COUPLING, ms=3.2)
        ax.plot(Dm[1:], [yi - 0.14] * 2, color=vs.COUPLING, lw=0.8, alpha=0.7)
        ax.plot(Dm[0], yi - 0.14, "o", mfc="white", mec=vs.COUPLING, ms=3.0, mew=0.8)
        orr = dd.get("other_room")
        if orr and dd["n_pairs_other"] > 0:
            Dp = np.array(orr["addr"]["D"]) * 100
            ax.plot(Dp[1:], [yi - 0.38] * 2, color=vs.MUTED, lw=0.8)
            ax.plot(Dp[0], yi - 0.38, "s", color=vs.NULL, mec=vs.INK2, mew=0.4, ms=2.6)
    ax.axvline(0, color=vs.INK2, lw=0.5)
    ax.set_xlim(-0.7, 5.6)
    ax.set_yticks(y)
    ax.set_yticklabels([f"{g} {regime_of(g)}" for g in PERIODS], fontsize=5.6)
    ax.set_ylim(-0.8, len(PERIODS) - 0.4)
    ax.set_xlabel("jump $D=G(1)-G(0)$ (pp)")
    ax.set_title(title, loc="left")
    h = [Line2D([], [], marker="o", color=vs.COUPLING, ms=3.2, lw=1.1),
         Line2D([], [], marker="o", mfc="white", mec=vs.COUPLING, color=vs.COUPLING, ms=3, lw=0.8),
         Line2D([], [], marker="s", color=vs.MUTED, mfc=vs.NULL, mec=vs.INK2, ms=2.6, lw=0.8)]
    ax.legend(h, ["reply to sender", "names sender", "other room (null)"], loc="upper right", fontsize=5.6,
              handlelength=1.3, borderaxespad=0.1)
    ax.grid(axis="y", visible=False)


def fig_static(c9, ex):
    """Double-column figure: (a) | (b) | (c)."""
    vs.use()
    fig = plt.figure(figsize=(vs.W["double"], 2.55))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.55, 1.0, 1.0], wspace=0.42, left=0.13, right=0.99, bottom=0.17, top=0.88)
    panel_a(fig.add_subplot(gs[0]), ex)
    panel_b(fig.add_subplot(gs[1]), c9)
    panel_c(fig.add_subplot(gs[2]), c9)
    vs.save(fig, HERE / "fig")
    plt.close(fig)


def fig_cols(c9, ex):
    """Single-column figures for the paper: fig_a (the example alone) and fig_bc (profile and per-period jumps)."""
    vs.use()
    fig = plt.figure(figsize=(vs.W["single"], 2.35))
    ax = fig.add_axes([0.26, 0.17, 0.72, 0.74])
    panel_a(ax, ex, fs=6.5, ncol=2)
    ax.set_title("one message, %s %s" % (EX_PERIOD, ex["day"]), loc="left")
    vs.save(fig, HERE / "fig_a")
    plt.close(fig)
    fig = plt.figure(figsize=(vs.W["single"], 2.45))
    gs = fig.add_gridspec(1, 2, width_ratios=[0.85, 1.0], wspace=0.55, left=0.14, right=0.99, bottom=0.18, top=0.9)
    panel_b(fig.add_subplot(gs[0]), c9, title="(a) %s, 17 days" % EX_PERIOD)
    panel_c(fig.add_subplot(gs[1]), c9, title="(b) all 17 periods")
    vs.save(fig, HERE / "fig_bc")
    plt.close(fig)


# ------------------------------------------------------------------------------------------- animation
def make_anim(ex, c9):
    vs.use()
    lanes = ex["lanes"]
    n = len(lanes)
    x0 = -35
    x1 = max(l["W"] for l in lanes[1:]) + 35
    fps, dur = 24, 18.0
    nf = int(fps * dur)
    t_intro, t_sweep, t_hold = 1.5, 12.5, 2.5          # seconds; the rest fades back to the start state
    fig = plt.figure(figsize=(1280 / 160, 720 / 160), dpi=160)
    ax = fig.add_axes([0.22, 0.17, 0.75, 0.66])
    title = fig.text(0.03, 0.94, "Context is the coupling: a message acts only at the recipient's next model call",
                     fontsize=10.5, color=vs.INK, weight="bold")
    sub = fig.text(0.03, 0.885, "Real calls, %s (%s), one room. Bars = model calls (context assembled at the left edge); gaps = tool time or pauses."
                   % (EX_PERIOD, ex["day"]), fontsize=8, color=vs.INK2)
    clock = fig.text(0.955, 0.94, "", ha="right", fontsize=9.5, color=vs.INK, family="monospace")
    note = fig.text(0.03, 0.04, "", fontsize=8.5, color=vs.INK)
    D38 = np.array(c9[EX_PERIOD]["primary"]["auth"]["D"]) * 100

    def tnow(f):
        s = f / fps
        if s < t_intro:
            return x0
        if s < t_intro + t_sweep:
            return x0 + (x1 - x0) * (s - t_intro) / t_sweep
        return x1

    def frame(f):
        ax.clear()
        s = f / fps
        tc = tnow(f)
        fade = 1.0
        if s > t_intro + t_sweep + t_hold:
            fade = max(0.0, 1 - (s - t_intro - t_sweep - t_hold) / (dur - t_intro - t_sweep - t_hold))
        upto = tc if fade > 0 else x0 - 1
        draw_raster(ax, ex, x0=x0, x1=x1, upto=upto if fade > 0.02 else -1e9, fs=8)
        ax.set_xlabel("time since the message (s)", fontsize=8.5)
        ax.tick_params(labelsize=8)
        # cursor
        if t_intro <= s <= t_intro + t_sweep:
            ax.axvline(tc, color=vs.INK, lw=0.8, alpha=0.6)
        # pending markers and read-out flashes
        if tc >= 0 and fade > 0.02:
            for i, l in enumerate(lanes[1:], start=1):
                y = n - 1 - i
                sr = l["s"][l["recv"]]
                if tc < sr:   # waiting, unread
                    ax.plot([tc], [y], "o", mfc="white", mec=vs.COUPLING, ms=6.5, mew=1.2, zorder=7, alpha=fade)
                else:
                    age = tc - sr
                    if age < 12:
                        r = 5 + 2.2 * age
                        ax.plot([sr], [y], "o", mfc="none", mec=vs.COUPLING, ms=r, mew=1.6 * (1 - age / 12),
                                zorder=7, alpha=fade)
                    if l["replied"] and tc >= l["t"][l["recv"]]:
                        a = FancyArrowPatch((l["t"][l["recv"]], y + 0.2), (l["t"][l["recv"]] - 4, n - 1 - 0.2),
                                            connectionstyle="arc3,rad=-0.25", arrowstyle="-|>", mutation_scale=7,
                                            color=vs.COUPLING, lw=0.9, alpha=0.55 * fade, zorder=4)
                        ax.add_patch(a)
            # message broadcast flash
            if tc < 10:
                ax.plot([0], [n - 1], "o", mfc="none", mec=vs.COUPLING, ms=6 + 3 * tc, mew=1.5 * (1 - tc / 10))
        # labels
        if tc < 0:
            msg = "A model call reads the room once, when its context is assembled."
        elif any(tc < l["s"][l["recv"]] for l in lanes[1:]):
            msg = "Posted. Calls already running (dark) cannot see it: the message waits, unread."
        else:
            msg = ("Each recipient reads it at its next call (blue); replies (triangles) come only from that call. "
                   "%s, all 17 days: reply jump %+.2f pp [%+.2f, %+.2f]." % (EX_PERIOD, D38[0], D38[1], D38[2]))
        note.set_text(msg)
        note.set_alpha(fade if s > t_intro + t_sweep + t_hold else 1)
        clock.set_text("t = %+5.0f s" % tc if tc >= x0 + 0.5 else "t = %+5.0f s" % x0)
        return []

    anim = animation.FuncAnimation(fig, frame, frames=nf, interval=1000 / fps, blit=False)
    anim._save_count = nf
    poster = int(fps * (t_intro + t_sweep + 1.0))
    vs.save_anim(anim, HERE / "anim", fps=fps, dpi=160, poster_frame=poster)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-anim", action="store_true")
    a = ap.parse_args()
    c9 = load_c9()
    ex = pick_example()
    print("example msg", ex["msg"], ex["day"], [(l["name"], round(l.get("W", 0), 1), l.get("infl"), l.get("replied"))
                                                for l in ex["lanes"]])
    fig_static(c9, ex)
    fig_cols(c9, ex)
    if not a.no_anim:
        make_anim(ex, c9)


if __name__ == "__main__":
    main()
