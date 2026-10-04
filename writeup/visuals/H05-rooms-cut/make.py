"""H05 visual: rooms decouple chat only through what agents read; work (activity) is not room-bound.

Static (fig.pdf/png, double column):
  (a) schematic: two rooms as coupled blocks (kinetic Ising on 1-min talk spins): J_in inside a room, J_out ~ 0
      across; a room acts as a read filter;
  (b) within-room minus cross-room coupling (excess lagged correlation kappa_x over the cross-day surrogate) per
      two-room window, talk vs activity spins, with the room-label null (gray: +-1.96 null sd);
  (c) effects on talk coupling (kappa_x units): the 05-11 split (NE42 cut, a non-holdout cut) as a pair DiD against
      its assignment-permutation null (gray, 95%), the pooled co-location effect without and with ledger reads, the
      reads effect, and the activity-spin co-location effect.
NE12 itself separated no pair (all agents stayed in #general until 03-05/03-16), and NE15 (03-16) has a held-out pre
side, so the "before/after the cut" panel uses the non-holdout NE42 split (05-11); the card's holdout NE15 C1 result
is quoted in the caption only.
Numbers are read from H05's round-1b outputs (r1b/explore_bin1.json, r1b/r1b_reads.json); the DiD permutation null
is redrawn here from r1b/pair_day_bin1.parquet with H05's assignment rule (2,000 draws).

Run: uv run python writeup/visuals/H05-rooms-cut/make.py
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
from matplotlib.gridspec import GridSpec  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Circle  # noqa: E402

import vstyle as vs  # noqa: E402

R1B = rc.PROC / "H05-rooms-cut/r1b"
EX = rc.load_json("H05-rooms-cut/r1b/explore_bin1.json")
RD = rc.load_json("H05-rooms-cut/r1b/r1b_reads.json")
C_ACT = vs.C["green"]


def did_null(n_perm=2000, seed=511):
    """05-11 split, talk kappa_x: cut-arm DiD vs stay pairs and its assignment-permutation null (H05 rule)."""
    pdf = pl.read_parquet(R1B / "pair_day_bin1.parquet").filter(pl.col("spin") == "talk")
    ad = pl.read_parquet(R1B / "agent_day.parquet")
    pre = sorted(pdf.filter(pl.col("goal_no") == 40)["pt_date"].unique().to_list())
    post = sorted(pdf.filter(pl.col("goal_no") == 41)["pt_date"].unique().to_list())

    def mode(days):
        t = (ad.filter(pl.col("pt_date").is_in(days)).group_by("agent", "room_mode").len()
             .sort(["agent", "len"], descending=[False, True]))
        return dict(t.group_by("agent", maintain_order=True).agg(pl.col("room_mode").first()).iter_rows())
    mpre, mpost = mode(pre), mode(post)
    agents = np.array(sorted(set(mpre) & set(mpost)))
    traj = np.array([[mpre[a], mpost[a]] for a in agents])
    t = pdf.filter(pl.col("pt_date").is_in(pre + post) & pl.col("i").is_in(agents.tolist())
                   & pl.col("j").is_in(agents.tolist())).with_columns(pl.col("pt_date").is_in(post).alias("post"))
    g = t.group_by("i", "j", "post").agg(pl.col("coloc").mean(), pl.col("kappa_x").mean())
    piv = {}
    for i, j, p, c, k in g.iter_rows():
        piv.setdefault((i, j), {})[p] = (c, k)
    pairs = [p for p, v in piv.items() if True in v and False in v]
    cpre = np.array([piv[p][False][0] for p in pairs]); cpost = np.array([piv[p][True][0] for p in pairs])
    nz = lambda v: np.nan if v is None else v  # noqa: E731
    diff = np.array([nz(piv[p][True][1]) - nz(piv[p][False][1]) for p in pairs])
    cls = np.where((cpre >= 0.75) & (cpost >= 0.75), "stay", np.where((cpre >= 0.75) & (cpost <= 0.25), "cut",
                   "other"))
    obs = np.nanmean(diff[cls == "cut"]) - np.nanmean(diff[cls == "stay"])
    pa = np.array(pairs)
    ai, aj = np.searchsorted(agents, pa[:, 0]), np.searchsorted(agents, pa[:, 1])
    rng = np.random.default_rng(seed)
    null = []
    for _ in range(n_perm):
        tr = traj[rng.permutation(len(agents))]
        sp, so = tr[ai, 0] == tr[aj, 0], tr[ai, 1] == tr[aj, 1]
        cut, stay = sp & ~so, sp & so
        if cut.any() and stay.any():
            null.append(np.nanmean(diff[cut]) - np.nanmean(diff[stay]))
    null = np.array(null)
    p = (1 + np.sum(np.abs(null - null.mean()) >= abs(obs - null.mean()))) / (1 + len(null))
    return obs, null, p, int((cls == "cut").sum()), int((cls == "stay").sum())


def panel_schematic(ax):
    rng = np.random.default_rng(4)
    rooms = {"A": (0.25, 0.5, 4, vs.ROOM["#best"]), "B": (0.75, 0.5, 6, vs.ROOM["#rest"])}
    pos = {}
    for nm, (cx, cy, n, col) in rooms.items():
        ax.add_patch(Circle((cx, cy), 0.2, facecolor=col, alpha=0.08, edgecolor=col, lw=1.0))
        ang = np.linspace(0, 2 * np.pi, n, endpoint=False) + rng.uniform(0, 1)
        pos[nm] = np.column_stack([cx + 0.12 * np.cos(ang), cy + 0.12 * np.sin(ang)])
        for i in range(n):
            for j in range(i + 1, n):
                ax.plot(*pos[nm][[i, j]].T, color=vs.COUPLING, lw=0.9, alpha=0.75, zorder=1)
        ax.scatter(*pos[nm].T, s=26, color=col, edgecolor="white", lw=0.5, zorder=3,
                   marker="o" if nm == "A" else "s")
        ax.text(cx, cy - 0.27, "#best" if nm == "A" else "#rest", ha="center", fontsize=6.5, color=col)
    for (i, j) in ((0, 1), (2, 4), (3, 5)):
        p, q = pos["A"][i], pos["B"][j]
        ax.plot([p[0], q[0]], [p[1], q[1]], color=vs.NULL, lw=0.8, ls=(0, (2, 2)), zorder=0)
    ax.text(0.5, 0.5, "×", ha="center", va="center", fontsize=11, color=vs.INK2)
    ax.text(0.25, 0.86, "$J_\\mathrm{in}$: room-mates read\neach other", ha="center", fontsize=6.2,
            color=vs.COUPLING)
    ax.text(0.75, 0.86, "$J_\\mathrm{out}\\approx0$: no reads\nacross the cut", ha="center", fontsize=6.2,
            color=vs.INK2)
    ax.text(0.5, 0.04, "talk couples through reads; activity (work) does not", ha="center", fontsize=6.2,
            color=vs.INK)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1.02); ax.set_aspect("equal", adjustable="datalim"); ax.axis("off")
    ax.set_title("(a) schematic: rooms as coupled blocks", loc="left")


def panel_windows(ax):
    win = ["37", "38", "39", "41", "42", "44"]
    x = np.arange(len(win))
    for i, w in enumerate(win):
        sd = EX["X2"]["talk"][w]["kappa_x"]["null_sd"]
        ax.add_patch(plt.Rectangle((i - 0.32, -1.96 * sd), 0.3, 3.92 * sd, color=vs.NULL, alpha=0.6, lw=0))
        sda = EX["X2"]["active"][w]["kappa_x"]["null_sd"]
        ax.add_patch(plt.Rectangle((i + 0.02, -1.96 * sda), 0.3, 3.92 * sda, color=vs.NULL, alpha=0.6, lw=0))
    yt = [EX["X2"]["talk"][w]["kappa_x"]["diff"] for w in win]
    ya = [EX["X2"]["active"][w]["kappa_x"]["diff"] for w in win]
    ax.scatter(x - 0.17, yt, s=22, color=vs.COUPLING, marker="o", zorder=3)
    ax.scatter(x + 0.17, ya, s=22, facecolor="white", edgecolor=C_ACT, marker="s", lw=1.0, zorder=3)
    ax.axhline(0, color=vs.MUTED, lw=0.6)
    ax.set_xticks(x, [f"#{w}" for w in win])
    ax.set_ylabel("within − cross room coupling $\\Delta\\kappa_x$")
    ax.set_ylim(-0.035, 0.08)
    pt = EX["X2_pooled_III"]["talk"]["kappa_x"]; pa = EX["X2_pooled_III"]["active"]["kappa_x"]
    ax.set_title("(b) talk follows the room, activity does not", loc="left")
    h = [Line2D([], [], marker="o", ls="", color=vs.COUPLING, ms=4,
                label=f"talk spins: {pt['n_positive']}/6 above, Fisher $p$ = {pt['fisher_p']:.0e}".replace("e-0", "e-")),
         Line2D([], [], marker="s", ls="", mfc="white", mec=C_ACT, ms=4,
                label=f"activity spins: $p$ = {pa['fisher_p']:.2f}"),
         plt.Rectangle((0, 0), 1, 1, color=vs.NULL, alpha=0.6, label="room-label null, ±1.96 sd")]
    ax.legend(handles=h, loc="upper left", fontsize=6.0, handlelength=1.2, borderaxespad=0.2)


def panel_effects(ax, did):
    obs, null, _, n_cut, n_stay = did
    p = EX["X3"]["talk"]["split_0511"]["kappa_x"]["cut"]["p_assign_perm_2sided"]   # H05's own draw (card value)
    hh = RD["HH248_none"]["talk"]["all_III"]["kappa_x"]
    ha = RD["HH248_none"]["active"]["all_III"]["kappa_x"]
    rows = [
        ("05-11 split: cut pairs\nvs stay pairs (DiD)", obs, None, np.percentile(null, [2.5, 97.5]), vs.COUPLING),
        ("co-location", hh["M0_coloc"]["coloc"]["beta"], hh["M0_coloc"]["coloc"]["se"], None, vs.COUPLING),
        ("co-location | reads", hh["M1_coloc_plus_lreads"]["coloc"]["beta"],
         hh["M1_coloc_plus_lreads"]["coloc"]["se"], None, vs.COUPLING),
        ("reads | co-location\n(per e-fold)", hh["M1_coloc_plus_lreads"]["lreads"]["beta"],
         hh["M1_coloc_plus_lreads"]["lreads"]["se"], None, vs.COUPLING),
        ("co-location,\nactivity spins", ha["M0_coloc"]["coloc"]["beta"], ha["M0_coloc"]["coloc"]["se"], None, C_ACT),
    ]
    ys = np.arange(len(rows))[::-1]
    for y, (lab, b, se, nb, col) in zip(ys, rows):
        if nb is not None:
            ax.add_patch(plt.Rectangle((nb[0], y - 0.3), nb[1] - nb[0], 0.6, color=vs.NULL, alpha=0.6, lw=0))
            ax.scatter(b, y, s=24, color=col, marker="D", zorder=3)
            ax.text(b, y + 0.38, f"$p_\\mathrm{{perm}}$ = {p:.3f} ({n_cut} cut, {n_stay} stay pairs)", fontsize=5.9,
                    ha="center", va="bottom")
        else:
            mk = "s" if col == C_ACT else "o"
            ax.errorbar(b, y, xerr=1.96 * se, fmt=mk, color=col, ms=4, lw=0.9, capsize=1.5,
                        mfc="white" if col == C_ACT else col)
            ax.text(b + 1.96 * se + 0.0015, y, f"$z$ = {b / se:.1f}", fontsize=5.9, va="center")
    ax.axhline(3.5, color=vs.GRID, lw=0.8)
    ax.axvline(0, color=vs.MUTED, lw=0.6)
    ax.set_yticks(ys, [r[0] for r in rows], fontsize=6.3)
    ax.set_xlabel("effect on talk coupling $\\kappa_x$")
    ax.set_xlim(-0.06, 0.035); ax.set_ylim(-1.35, len(rows) - 0.25)
    ax.set_title("(c) a room acts only through reads", loc="left")
    ax.text(0.99, 0.02, "bars: 95% (pair-clustered, regime III)\ngray: assignment-permutation null 95%",
            transform=ax.transAxes, fontsize=5.6, color=vs.MUTED, ha="right", va="bottom")


def make_static():
    vs.use()
    did = did_null()
    print(f"05-11 split DiD {did[0]:.4f} (card -0.020), p_perm {did[2]:.3f} (card 0.027)")
    fig = plt.figure(figsize=(vs.W["double"], 2.7))
    gs = GridSpec(1, 3, figure=fig, width_ratios=[0.85, 1.05, 1.15], wspace=0.5, left=0.01, right=0.99, top=0.88,
                  bottom=0.17)
    panel_schematic(fig.add_subplot(gs[0]))
    panel_windows(fig.add_subplot(gs[1]))
    panel_effects(fig.add_subplot(gs[2]), did)
    vs.save(fig, HERE / "fig")
    plt.close(fig)


if __name__ == "__main__":
    make_static()
