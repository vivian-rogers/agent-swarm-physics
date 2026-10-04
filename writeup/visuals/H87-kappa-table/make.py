"""H87 + H70 writeup visual: the kappa table (commits per bit, by channel).

Static figure (fig.pdf/png, double column), one row per channel (C context window, A own artifact, M memory note,
G chat reads, H human messages, Q history search, K kickoff):
  (a) allocation information I_c (bits beyond agent identity; permutation floor subtracted); gray band = below
      the identification floor (A1 rule: lower CI bound must exceed 0.02 bits)
  (b) value Delta V_c (work commits per 20 calls) at the channel's natural scramble; hollow marker for the
      "any chat item" own-scramble contrast of the G row
  (c) kappa_c = Delta V_c / I_c where identified; "n.i." elsewhere
  (d) return to the agent's own repo for the first commit after a forced erasure vs a pseudo-erasure,
      split by whether the agent re-read its artifact in calls 1-5 (H70)

Inputs (processed, non-holdout): data/processed/H87-kappa-channel-table/results/results.json.
Run: uv run python writeup/visuals/H87-kappa-table/make.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "writeup/visuals"))
import vstyle as vs  # noqa: E402

HERE = Path(__file__).resolve().parent
R = ROOT / "data/processed/H87-kappa-channel-table/results/results.json"
CTX = vs.C["green"]
ROWS = [("C", "context window"), ("A", "own artifact"), ("M", "memory note"), ("G", "chat reads"),
        ("H", "human messages"), ("Q", "history search"), ("K", "kickoff (day)")]
FLOOR = 0.02


def wilson(p, n, z=1.96):
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return c - h, c + h


def table(res):
    ne = res["NE41"]
    rows = {}
    for c in ("C", "A", "M", "G", "Q"):
        r = ne["rows"][c]
        rows[c] = dict(I=r["I"], I_ci=r["I_ci"], dV=r["dV"], dV_ci=r["dV_ci"],
                       k=r["kappa"] if ne["identified"][c] else None, k_ci=r["kappa_ci"] if ne["identified"][c] else None)
    h = ne["own_scramble"]["Hdose"]
    rows["H"] = dict(I=0.0, I_ci=None, dV=h["dV"], dV_ci=h["dV_ci"], k=None, k_ci=None)
    K = res["NE34_K"]
    rows["K"] = dict(I=K["I"], I_ci=K["I_ci"], dV=K["dV"], dV_ci=K["dV_ci"], k=None, k_ci=None)
    return rows, ne


def static():
    vs.use()
    res = json.loads(R.read_text())
    rows, ne = table(res)
    fig = plt.figure(figsize=(vs.W["double"], 2.75))
    gs = fig.add_gridspec(1, 4, width_ratios=[1.0, 1.0, 0.75, 0.95], wspace=0.16)
    axI, axV, axK = fig.add_subplot(gs[0]), fig.add_subplot(gs[1]), fig.add_subplot(gs[2])
    axR = fig.add_subplot(gs[3])
    ys = np.arange(len(ROWS))[::-1]

    for y, (c, name) in zip(ys, ROWS):
        r = rows[c]
        col = CTX if c == "C" else vs.INK2
        # (a) bits
        if r["I_ci"] is None:
            axI.plot(0, y, "x", ms=4, color=col)
            axI.text(0.03, y, "0 (no repo named)", fontsize=6.3, va="center", color=vs.MUTED)
        else:
            axI.plot(r["I_ci"], [y, y], color=col, lw=1.2)
            axI.plot(r["I"], y, "o", ms=3.5, color=col)
        # (b) value; K row's lower CI is clipped
        lo, hi = r["dV_ci"]
        lo_c = max(lo, -0.55)
        axV.plot([lo_c, hi], [y, y], color=col, lw=1.2)
        axV.plot(r["dV"], y, "s", ms=3.5, color=col)
        if lo < -0.55:
            axV.annotate("", xy=(-0.6, y), xytext=(-0.5, y), arrowprops=dict(arrowstyle="-|>", lw=0.8, color=col,
                                                                              mutation_scale=6))
        # (c) kappa
        if r["k"] is not None:
            klo, khi = r["k_ci"]
            axK.plot([klo, khi], [y, y], color=col, lw=1.2)
            axK.plot(r["k"], y, "D", ms=3.8, color=col)
        else:
            axK.text(3.0, y, "n.i.", fontsize=6.8, va="center", ha="center", color=vs.MUTED)

    g_any = ne["own_scramble"]["Gany"]
    yg = ys[[c for c, _ in ROWS].index("G")]
    axV.plot(g_any["dV_ci"], [yg - 0.3] * 2, color=vs.INK2, lw=0.8)
    axV.plot(g_any["dV"], yg - 0.3, "s", ms=3.5, mfc="white", mec=vs.INK2)
    axV.text(g_any["dV"], yg - 0.42, "any chat item", fontsize=6.0, va="top", ha="center", color=vs.INK2)

    axI.axvspan(-0.1, FLOOR, color=vs.NULL, alpha=0.45, lw=0)
    axI.text(0.025, ys[0] + 0.75, "not identified\nbelow 0.02 bits", fontsize=6, color=vs.MUTED, va="center")
    axI.set_xlim(-0.06, 0.8)
    axI.set_xlabel("$I_c$ (bits)")
    axI.set_yticks(ys)
    axI.set_yticklabels([n for _, n in ROWS])
    axI.get_yticklabels()[0].set_color(CTX)
    axI.set_title("(a) bits about where to work", loc="left")

    axV.axvline(0, color=vs.INK2, lw=0.6)
    axV.set_xlim(-0.62, 0.55)
    axV.set_xlabel(r"$\Delta V_c$ (commits / 20 calls)")
    axV.set_title("(b) output value", loc="left")
    axV.set_yticks(ys); axV.set_yticklabels([])

    axK.axvline(0, color=vs.INK2, lw=0.6)
    axK.set_xlim(-2.5, 9)
    axK.set_xlabel(r"$\kappa_c$ (per bit)")
    axK.set_title(r"(c) value per bit", loc="left")
    axK.set_yticks(ys); axK.set_yticklabels([])
    kC = rows["C"]
    axK.text(kC["k"], ys[0] + 0.42, f"{kC['k']:.1f}", fontsize=6.5, color=CTX, ha="center")
    for ax in (axI, axV, axK):
        ax.set_ylim(-0.7, ys[0] + 1.2)
        ax.grid(axis="y", visible=False)

    # (d) return to own repo (H70 frame, NE41)
    ret = ne["return"]
    groups = [("all", "all"), ("openA=True", "re-read\nartifact"), ("openA=False", "no\nre-read")]
    x = np.arange(len(groups))
    for kind, dx, col, mk, lab in (("P", -0.14, vs.MUTED, "o", "pseudo-erasure"), ("F", 0.14, vs.C["red"], "s",
                                                                                     "forced erasure")):
        for i, (key, _) in enumerate(groups):
            d = ret[kind] if key == "all" else ret[kind][key]
            p, n = (d["all"], d["n"]) if key == "all" else (d["p"], d["n"])
            lo, hi = wilson(p, n)
            axR.plot([i + dx] * 2, [lo * 100, hi * 100], color=vs.NULL if kind == "P" else col,
                     lw=2.2 if kind == "P" else 1.1, solid_capstyle="butt")
            axR.plot(i + dx, p * 100, mk, ms=3.5, color=col)
    axR.text(0.14, ret["F"]["all"] * 100 + 2.2, f"{ret['F']['all']*100:.0f}%", fontsize=6.5, ha="center",
             color=vs.C["red"])
    axR.set_xticks(x)
    axR.set_xticklabels([g for _, g in groups], fontsize=6.5)
    axR.set_ylim(70, 100)
    axR.set_xlim(-0.5, 2.5)
    axR.set_ylabel("first commit in own repo (%)")
    axR.yaxis.set_label_position("right"); axR.yaxis.tick_right()
    axR.spines["right"].set_visible(True); axR.spines["left"].set_visible(False)
    axR.set_title("(d) artifacts point home", loc="left")
    axR.legend(handles=[Line2D([], [], color=vs.C["red"], marker="s", ms=3, lw=1.1, label="forced erasure"),
                        Line2D([], [], color=vs.NULL, marker="o", mfc=vs.MUTED, mec=vs.MUTED, ms=3, lw=2.2,
                               label="pseudo-erasure")],
               loc="lower left", fontsize=6.3, handlelength=1.0, borderaxespad=0.2)
    axR.grid(axis="x", visible=False)
    vs.save(fig, HERE / "fig")
    plt.close(fig)


if __name__ == "__main__":
    static()
