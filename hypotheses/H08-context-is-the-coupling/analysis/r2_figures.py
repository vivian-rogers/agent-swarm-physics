"""H08 round-2 summary figure (reads only round-2 JSON outputs).

  uv run python hypotheses/H08-context-is-the-coupling/analysis/r2_figures.py

figures/r2_summary.pdf: (a) R2 read-minus-in-flight content contrast at matched lag, all statements vs statements that
neither name nor reply to the sender (bge); (b) R5 the Claude Code agent's fetched events: share stale (> 24 h old) per
day; (c) R4 forced erasure x memory dose (CF x z) per period with the pooled estimate.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figures import AQUA, BLUE, GRID, INK, INK2, MUTED, ORANGE, style  # noqa: E402
from figures import plt, np, OUT, FIG, PERIODS, gname  # noqa: E402

R2 = OUT / "r2"


def main():
    plt.rcParams.update({"font.size": 6})
    fig = plt.figure(figsize=(3.45, 3.1), dpi=200)
    gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.0])
    axs = [fig.add_subplot(gs[0, :]), fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1])]
    # (a) R2
    ax = axs[0]
    S = json.loads((R2 / "r2_summary.json").read_text())["rows"]
    x = np.arange(len(S))
    for off, key, col, lab in ((-0.17, "bge_all", BLUE, "all statements"), (0.17, "bge_delta", ORANGE, "no name, no reply")):
        v = np.array([r[key] for r in S]) * 100
        ax.errorbar(x + off, v[:, 0], yerr=[v[:, 0] - v[:, 1], v[:, 2] - v[:, 0]], fmt="o", ms=2.5, lw=0.7, color=col, label=lab)
    ax.axhline(0, color=MUTED, lw=0.6)
    ax.set_ylim(-6, 6)   # G37's interval (40 in-flight statements) runs off the axis
    ax.set_xticks(x); ax.set_xticklabels([r["period"][1:] for r in S], fontsize=5)
    ax.axvline(7.5, color=GRID, lw=0.6, ls=":"); ax.text(3.5, ax.get_ylim()[1] * 0.92, "regime I/II", ha="center", color=INK2, fontsize=5)
    ax.text(12, ax.get_ylim()[1] * 0.92, "regime III", ha="center", color=INK2, fontsize=5)
    ax.set_ylabel("read − in flight, cos ×100"); ax.set_xlabel("goal period")
    ax.set_title("(a) content contrast at matched lag", loc="left", fontsize=6)
    ax.legend(frameon=False, fontsize=5, loc="lower left")
    style(ax)
    # (b) R5
    ax = axs[1]
    A = json.loads((R2 / "r5_audit.json").read_text())["fetch_audit"]["per_day"]
    days = [r["pt_date"] for r in A]; st = [100 * r["stale_share"] for r in A]
    cols = [ORANGE if d >= "2026-03-17" else BLUE for d in days]
    ax.bar(np.arange(len(days)), st, color=cols, width=0.8)
    ticks = [i for i, d in enumerate(days) if i % 4 == 0]
    ax.set_xticks(ticks); ax.set_xticklabels([days[i][5:] for i in ticks], fontsize=5, rotation=45)
    ax.set_ylabel("fetches stale (%)"); ax.set_ylim(0, 105)
    ax.set_title("(b) Claude Code feed", loc="left", fontsize=6)
    ax.text(0.03, 0.9, "replay\nfrom 03-17", transform=ax.transAxes, color=INK2, fontsize=5)
    style(ax)
    # (c) R4
    ax = axs[2]
    P = json.loads((R2 / "r4_pooled.json").read_text())
    names = list(P["periods"])
    v = np.array([P["periods"][g]["auth"]["beta"]["CFz"] for g in names]) * 100
    y = np.arange(len(names))
    ax.errorbar(v[:, 0], y, xerr=[v[:, 0] - v[:, 1], v[:, 2] - v[:, 0]], fmt="o", ms=2.5, lw=0.7, color=AQUA)
    pm = P["pooled"]["auth"]["CFz"]
    ax.errorbar([100 * pm["mu"]], [len(names)], xerr=[[196 * pm["se"]], [196 * pm["se"]]], fmt="D", ms=3, lw=1, color=INK)
    ax.axvline(0, color=MUTED, lw=0.6)
    ax.set_yticks(list(y) + [len(names)]); ax.set_yticklabels([g[1:] for g in names] + ["pooled"], fontsize=5)
    ax.set_xlabel("CF × dose on replies (pp)")
    ax.set_title("(c) memory dose, NE41", loc="left", fontsize=6)
    style(ax)
    fig.tight_layout(w_pad=0.8, h_pad=0.8)
    fig.savefig(FIG / "r2_summary.pdf", bbox_inches="tight")
    print("wrote", FIG / "r2_summary.pdf")


if __name__ == "__main__":
    main()
