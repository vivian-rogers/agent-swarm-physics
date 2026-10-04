"""H41 writeup visual: novel items obey a logged read-out light cone inside a room; across rooms the cone is a cage.

    uv run python writeup/visuals/H41-readout-light-cone/make.py            # fig + animation
    uv run python writeup/visuals/H41-readout-light-cone/make.py --no-anim  # fig only

Reads only processed data: H41's G38/adoptions.parquet (item codes, adopters, cone entry calls; no text, the item
itself is a hash) and results/period_table.parquet, plus the shared ledger tables through H41's own read-only loader
(hypotheses/H41-readout-light-cone/scheme/h41core.py: load_skeleton, cone, RoomIndex), which drops held-out days.
The example item's cone is recomputed with h41core.cone and checked against H41's stored entry calls.
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
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch, Rectangle  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "writeup/visuals"))
sys.path.insert(0, str(ROOT / "hypotheses/H41-readout-light-cone/scheme"))
import vstyle as vs  # noqa: E402
import h41core as C  # noqa: E402  (read-only import of H41's loader)
from common import holdout_mask  # noqa: E402

D = ROOT / "data/processed/H41-readout-light-cone"
SH = ROOT / "data/processed/shared"
GOAL = 38
CONE = "#d6e6f2"           # light blue: inside the logged cone
OUTC = vs.INK              # adoption outside the cone (x marker)


def pick_item():
    """A G38 item adopted the same day by agents in both rooms, within ~75 min: the most cross-room adopters."""
    A = pl.read_parquet(D / f"G{GOAL}/adoptions.parquet").with_columns((pl.col("t_use") - pl.col("t0")).alias("dt"))
    g = (A.filter(pl.col("day_use") == pl.col("day0")).group_by("marker")
         .agg(pl.len().alias("n"), pl.col("cross").sum().alias("nc"), pl.col("dt").max().alias("span"))
         .filter((pl.col("span") < 4 * 3600) & (pl.col("n") >= 4)).sort(["nc", "n", "marker"], descending=[True, True, False]))
    mk = int(g["marker"][0])
    return A.filter(pl.col("marker") == mk).sort("t_use")


def build_example():
    ad = pick_item()
    r0 = ad.row(0, named=True)
    t0, src, day, room0 = float(r0["t0"]), int(r0["src"]), r0["day0"], int(r0["room0"])
    assert not holdout_mask([day], [GOAL])[0]
    sk = C.load_skeleton(GOAL)
    ri = C.RoomIndex(sk)
    t_end = t0 + 3 * 3600
    T, K, H = C.cone(sk, src, t0, t_end)
    # check: recomputed entry calls equal H41's stored K for every adopter
    for a, k in zip(ad["agent"].to_list(), ad["K"].to_list()):
        assert int(K[a]) == int(k), (a, K[a], k)
    names = dict(zip(*pl.read_parquet(SH / "roster.parquet", columns=["agent", "name"]).to_dict(as_series=False).values()))
    rname = dict(zip(*pl.read_parquet(SH / "rooms.parquet", columns=["room", "name"]).to_dict(as_series=False).values()))
    lanes = []
    for a in sk.agents:
        a = int(a)
        sl = sk.agent_calls[a]
        ct = sk.c_t[sl]
        sel = (ct > t0 - 600) & (ct < t0 + 2.2 * 3600)
        if not sel.any():
            continue
        rm = ri.at(a, t0)
        lanes.append(dict(agent=a, name=names.get(a, str(a)), room=rm, calls=(ct[sel] - t0) / 60,
                          T=(T[a] - t0) / 60 if np.isfinite(T[a]) else np.inf, H=int(H[a])))
    ad_rows = [dict(agent=int(x["agent"]), t=(x["t_use"] - t0) / 60, inside=bool(x["in_cone"]), cross=bool(x["cross"]))
               for x in ad.iter_rows(named=True)]
    # order: source room first, then the other room; within room by entry time
    def key(l):
        return (0 if l["room"] == room0 else 1, 0 if l["agent"] == src else 1, l["T"], l["name"])
    lanes.sort(key=key)
    return dict(lanes=lanes, adopt=ad_rows, src=src, room0=room0, rname=rname, day=day, cls=int(r0["cls"]))


CLS = {0: "artifact", 1: "number", 2: "name", 3: "rare word"}


def draw_cone(ax, ex, upto=None, x1=80, fs=6.3, show_names=True, room_x=-0.255):
    lanes = ex["lanes"]; n = len(lanes)
    ymap = {}
    for i, l in enumerate(lanes):
        y = n - 1 - i
        ymap[l["agent"]] = y
        if np.isfinite(l["T"]) and (upto is None or upto >= l["T"]):
            right = x1 if upto is None else min(upto, x1)
            ax.add_patch(Rectangle((l["T"], y - 0.42), right - l["T"], 0.84, color=CONE, lw=0, zorder=1))
        c = l["calls"]
        c = c[(c >= -5) & (c <= (x1 if upto is None else min(upto, x1)))]
        ax.vlines(c, y - 0.25, y + 0.25, color=vs.MUTED, lw=0.35, zorder=2)
        if np.isfinite(l["T"]) and (upto is None or upto >= l["T"]) and l["agent"] != ex["src"]:
            ax.plot([l["T"]], [y], marker="|", color=vs.COUPLING, ms=7 if fs < 7 else 10, mew=1.4, zorder=3)
        if show_names:
            nm = l["name"] + ("  (source)" if l["agent"] == ex["src"] else "")
            ax.text(-6, y, nm, ha="right", va="center", fontsize=fs, color=vs.INK)
    # room separator and labels
    nsrc = sum(1 for l in lanes if l["room"] == ex["room0"])
    ysep = n - nsrc - 0.5
    ax.axhline(ysep, color=vs.INK2, lw=0.6, ls="--", zorder=2)
    other = [l["room"] for l in lanes if l["room"] != ex["room0"]]
    if show_names:
        import matplotlib.transforms as mt
        tr = mt.blended_transform_factory(ax.transAxes, ax.transData)
        xr = room_x
        ax.text(xr, (ysep + n - 0.5) / 2, "#" + ex["rname"][ex["room0"]] + " (source)", rotation=90, ha="center",
                va="center", fontsize=fs, color=vs.INK2, transform=tr)
        ax.plot([xr + 0.012] * 2, [ysep + 0.15, n - 0.6], color=vs.INK2, lw=0.6, transform=tr, clip_on=False)
        if other:
            ax.text(xr, (ysep - 0.4) / 2, "#" + ex["rname"].get(other[0], "?"), rotation=90, ha="center",
                    va="center", fontsize=fs, color=vs.INK2, transform=tr)
            ax.plot([xr + 0.012] * 2, [-0.4, ysep - 0.15], color=vs.INK2, lw=0.6, transform=tr, clip_on=False)
    for r in ex["adopt"]:
        if upto is not None and upto < r["t"]:
            continue
        y = ymap[r["agent"]]
        if r["inside"]:
            ax.plot([r["t"]], [y], "o", color=vs.COUPLING, ms=5 if fs < 7 else 8, mec="white", mew=0.5, zorder=5)
        else:
            ax.plot([r["t"]], [y], "X", color=OUTC, ms=5.5 if fs < 7 else 9, mec="white", mew=0.4, zorder=5)
    ax.plot([0], [ymap[ex["src"]]], "*", color=vs.COUPLING, ms=8 if fs < 7 else 12, mec="white", mew=0.5, zorder=6)
    ax.axvline(0, color=vs.MUTED, lw=0.6, ls=":", zorder=1)
    ax.set_xlim(-5, x1); ax.set_ylim(-0.7, n - 0.3)
    ax.set_yticks([]); ax.spines["left"].set_visible(False); ax.grid(False)


def fig_static(ex):
    vs.use()
    P = pl.read_parquet(D / "results/period_table.parquet").sort("goal")
    fig = plt.figure(figsize=(vs.W["double"], 2.75))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.75, 1.0], wspace=0.25, left=0.155, right=0.99, bottom=0.25, top=0.9)
    ax = fig.add_subplot(gs[0])
    draw_cone(ax, ex, fs=5.8)
    ax.set_xlabel("minutes since the item first appeared (source's post)")
    ax.set_title("(a) one novel item (%s), %s %s: the logged light cone" % (CLS.get(ex["cls"], "item"), "G38", ex["day"]),
                 loc="left")
    h = [Patch(color=CONE), Line2D([], [], marker="|", ls="", color=vs.COUPLING, ms=7, mew=1.4),
         Line2D([], [], marker="o", ls="", color=vs.COUPLING, ms=5, mec="white"),
         Line2D([], [], marker="X", ls="", color=OUTC, ms=5.5, mec="white"),
         Line2D([], [], marker="|", ls="", color=vs.MUTED, ms=5)]
    ax.legend(h, ["inside the cone", "entry call (first read)", "adoption inside", "adoption outside", "model call"],
              loc="upper center", bbox_to_anchor=(0.45, -0.17), ncol=5, fontsize=5.8, handlelength=1.0,
              columnspacing=0.9)
    # (b) per period: share of adoptions outside the cone
    ax = fig.add_subplot(gs[1])
    x = np.arange(P.height)
    w = P["acaus_rob_within"].to_numpy()
    ax.plot(x, 100 * w, "o", color=vs.COUPLING, ms=3, label="adopter in the source's room")
    two = P.filter((pl.col("acaus_rob_cross_n") >= 1) | ((pl.col("share_cross") > 0) & pl.col("goal").is_in([35, 36, 37, 38, 39, 41, 42, 44, 51])))
    gx = [int(np.flatnonzero(P["goal"].to_numpy() == g)[0]) for g in two["goal"].to_list()]
    ax.plot(gx, 100 * two["acaus_rob_cross"].to_numpy(), "X", color=OUTC, ms=4.5, mec="white", mew=0.3,
            label="adopter in another room")
    for xx, g, v in zip(gx, two["goal"].to_list(), two["acaus_rob_cross"].to_numpy()):
        if g in (44, 51):
            ax.annotate(f"G{g}", (xx, 100 * v), xytext=(-3, 3), textcoords="offset points", fontsize=5.6,
                        color=vs.INK2, ha="right")
    ax.set_xticks([i for i, g in enumerate(P["goal"].to_list()) if g in (5, 13, 21, 30, 38, 51)])
    ax.set_xticklabels([f"G{g:02d}" for g in P["goal"].to_list() if g in (5, 13, 21, 30, 38, 51)], fontsize=6.3)
    ax.set_ylim(-4, 104)
    ax.set_ylabel("adoptions outside the cone (%)")
    ax.set_xlabel("goal period (32, non-holdout)")
    ax.set_title("(b) inside a room vs across rooms", loc="left")
    ax.legend(loc="center left", fontsize=5.9, handlelength=1.0, bbox_to_anchor=(0.0, 0.45))
    vs.save(fig, HERE / "fig")
    plt.close(fig)
    return P, two


def make_anim(ex):
    vs.use()
    fps, dur = 24, 18.0
    nf = int(fps * dur)
    x1 = 80.0
    t_in, t_sw, t_hold = 1.2, 13.0, 2.8
    fig = plt.figure(figsize=(1280 / 160, 720 / 160), dpi=160)
    ax = fig.add_axes([0.235, 0.16, 0.735, 0.67])
    fig.text(0.03, 0.94, "A light cone for ideas: an item can reach an agent only through a model call that read it",
             fontsize=10, weight="bold", color=vs.INK)
    fig.text(0.03, 0.885, "Real ledger reads, G38 (%s), two rooms. Blue = inside the logged cone (time-respecting read-out "
             "paths from the post); clock slowed for 10 min." % ex["day"], fontsize=7.6, color=vs.INK2)
    clock = fig.text(0.955, 0.94, "", ha="right", fontsize=9.5, family="monospace", color=vs.INK)
    note = fig.text(0.03, 0.035, "", fontsize=8.2, color=vs.INK)
    n_out = sum(1 for r in ex["adopt"] if not r["inside"])

    def frame(f):
        s = f / fps
        u = 0.0 if s < t_in else min(1.0, (s - t_in) / t_sw)
        tc = -5 + 10 * (u / 0.4) if u < 0.4 else 5 + (x1 - 5) * (u - 0.4) / 0.6   # slow first 10 min
        reset = s > t_in + t_sw + t_hold
        ax.clear()
        draw_cone(ax, ex, upto=-1e9 if reset else tc, x1=x1, fs=7.5, room_x=-0.235)
        if t_in <= s <= t_in + t_sw:
            ax.axvline(tc, color=vs.INK, lw=0.7, alpha=0.5)
        ax.set_xlabel("minutes since the item first appeared", fontsize=8)
        ax.tick_params(labelsize=7.5)
        if tc < 0 or reset:
            msg = "Star: an agent posts a new item. Ticks: each agent's model calls."
        elif tc < 30:
            msg = "The cone spreads one read per call: room-mates enter at their next call and can adopt (dots)."
        else:
            msg = ("The other room never enters the cone, yet %d adoptions appear there (x): an unlogged channel. "
                   "Within rooms: median 0.6%% outside." % n_out)
        note.set_text(msg)
        clock.set_text("t = %+5.1f min" % (tc if not reset else -5))
        return []

    anim = animation.FuncAnimation(fig, frame, frames=nf, interval=1000 / fps, blit=False)
    anim._save_count = nf
    vs.save_anim(anim, HERE / "anim", fps=fps, dpi=160, poster_frame=int(fps * (t_in + t_sw + 1.0)))
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-anim", action="store_true")
    a = ap.parse_args()
    ex = build_example()
    print("lanes", [(l["name"], l["room"], round(l["T"], 1), l["H"]) for l in ex["lanes"]])
    print("adopt", ex["adopt"])
    P, two = fig_static(ex)
    print(two.select("goal", "acaus_rob_cross", "acaus_rob_cross_n"))
    print("within median", float(P["acaus_rob_within"].median()), "max", float(P["acaus_rob_within"].max()))
    if not a.no_anim:
        make_anim(ex)


if __name__ == "__main__":
    main()
