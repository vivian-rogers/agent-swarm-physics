"""H69 writeup visual: restatement loops copy what is still in the context window.

Static figure (fig.pdf/png, double column):
  (a) schematic: an agent's statements on a call timeline; a wipe removes the older ones from context;
      a new statement near-copies an in-context statement more often than an erased one at the same lag
  (b) in-context enrichment (Mantel-Haenszel OR, in-context vs erased source at matched lag and call distance)
      per period, with the pseudo-erasure OR (fake boundary mid-segment) as the gray null
  (c) loop exit odds when a forced erasure falls between two statements, per scorable period, plus the pool,
      and the onset odds after a forced erasure

Inputs (processed, non-holdout): data/processed/H69-loops-context-fixed-points/results.json (segment-cut recheck).
Animation (anim.mp4, schematic): colored blocks for one agent's statements; copies of in-context statements build a
loop until a forced wipe empties the context.

Run: uv run python writeup/visuals/H69-restatement-loops/make.py [--no-anim]
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
from matplotlib.patches import FancyArrowPatch, Rectangle

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "writeup/visuals"))
import vstyle as vs  # noqa: E402

HERE = Path(__file__).resolve().parent
D = ROOT / "data/processed/H69-loops-context-fixed-points"
PERIODS = ["G36", "G37", "G38", "G39", "G40", "G41", "G42", "G44", "G51"]
SCORABLE = ["G38", "G40", "G41", "G51"]          # >= 30 loop episodes (card)
CTX = vs.C["green"]                               # in-context source
WIPE = vs.C["red"]


def ci_exp(b, se):
    return np.exp(b), np.exp(b - 1.96 * se), np.exp(b + 1.96 * se)


def panel_schematic(ax):
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.2)
    ax.axis("off")
    cols = [vs.C["pink"], vs.C["sky"], vs.C["green"], vs.C["sky"], vs.C["pink"], vs.C["green"]]
    xs = [0.4, 1.6, 2.8, 5.0, 6.2, 7.4]
    yb = 2.5
    for i, (x, c) in enumerate(zip(xs, cols)):
        ax.add_patch(Rectangle((x, yb), 0.9, 0.9, fc=c, ec="none", alpha=0.3 if i < 3 else 1.0))
    ax.add_patch(Rectangle((8.8, yb), 0.9, 0.9, fc=vs.C["sky"], ec=vs.INK, lw=0.8))
    ax.text(9.25, yb + 1.05, "new", ha="center", fontsize=6.5, color=vs.INK)
    ax.plot([4.3, 4.3], [1.9, 4.0], color=WIPE, ls="--", lw=1.2)
    ax.text(4.3, 4.1, "wipe", color=WIPE, ha="center", va="bottom", fontsize=6.5)
    ax.text(1.85, yb + 1.05, "erased", ha="center", fontsize=6.5, color=vs.MUTED)
    ax.text(6.65, yb + 1.05, "in context", ha="center", fontsize=6.5, color=vs.INK2)
    ax.add_patch(FancyArrowPatch((9.25, yb + 1.45), (5.45, yb + 1.45), connectionstyle="arc3,rad=0.5",
                                 arrowstyle="-|>", mutation_scale=7, lw=1.3, color=CTX))
    ax.text(7.35, 5.0, "near-copy odds 3.4×", fontsize=6.8, color=CTX, ha="center")
    ax.add_patch(FancyArrowPatch((9.25, yb - 0.05), (2.05, yb - 0.05), connectionstyle="arc3,rad=-0.22",
                                 arrowstyle="-|>", mutation_scale=7, lw=0.9, ls=":", color=vs.MUTED))
    ax.text(5.6, 0.35, "same lag, erased source: 1×", fontsize=6.5, color=vs.MUTED, ha="center")
    ax.text(0.0, 6.1, "own statements on the call clock (schematic)", fontsize=6.5, color=vs.MUTED, va="top")
    ax.set_title("(a) restatement copies context", loc="left")


def panel_enrich(ax, res, pooled):
    ys = np.arange(len(PERIODS))[::-1]
    for y, p in zip(ys, PERIODS):
        r = res[p]
        e, ps = r.get("enrich"), r.get("pseudo")
        strong = p in SCORABLE
        if ps and np.isfinite(ps["log_or"]):
            ax.plot(np.exp([ps["lo"], ps["hi"]]), [y - 0.17] * 2, color=vs.NULL, lw=2.2, solid_capstyle="butt")
            ax.plot(np.exp(ps["log_or"]), y - 0.17, "o", ms=2.6, color=vs.MUTED)
        if e and np.isfinite(e["log_or"]):
            a = 1.0 if strong else 0.35
            ax.plot(np.exp([e["lo"], e["hi"]]), [y + 0.12] * 2, color=CTX, lw=1.1, alpha=a)
            ax.plot(np.exp(e["log_or"]), y + 0.12, "s", ms=3, color=CTX, alpha=a)
    y0 = -1.3
    pe, pp = pooled["enrich"], pooled["pseudo"]
    ax.fill_betweenx([y0 - 0.32, y0 + 0.32], np.exp(pe["lo"]), np.exp(pe["hi"]), color=CTX, alpha=0.35, lw=0)
    ax.plot(np.exp(pe["mean"]), y0, "D", ms=4, color=CTX)
    ax.fill_betweenx([y0 - 0.32, y0 + 0.32], np.exp(pp["lo"]), np.exp(pp["hi"]), color=vs.NULL, alpha=0.9, lw=0)
    ax.plot(np.exp(pp["mean"]), y0, "D", ms=3.5, color=vs.MUTED)
    ax.text(np.exp(pe["hi"]) * 1.12, y0, f"{np.exp(pe['mean']):.2f}", color=CTX, fontsize=6.5, va="center")
    ax.axvline(1, color=vs.INK2, lw=0.6)
    ax.set_xscale("log")
    ax.set_xlim(0.15, 45)
    ax.set_xticks([0.2, 0.5, 1, 2, 5, 10, 20])
    ax.set_xticklabels(["0.2", "0.5", "1", "2", "5", "10", "20"])
    ax.set_yticks(list(ys) + [y0])
    ax.set_yticklabels(PERIODS + ["pooled (4)"])
    for t, p in zip(ax.get_yticklabels(), PERIODS + ["pooled"]):
        if p not in SCORABLE and p != "pooled":
            t.set_color(vs.MUTED)
    ax.set_ylim(y0 - 0.9, ys[0] + 1.7)
    ax.set_xlabel("odds of near-copying a source (in context / erased)")
    ax.set_title("(b) in-context enrichment", loc="left")
    ax.legend(handles=[Line2D([], [], color=CTX, marker="s", ms=3, lw=1.1, label="real boundary"),
                       Line2D([], [], color=vs.NULL, marker="o", mfc=vs.MUTED, mec=vs.MUTED, ms=3, lw=2.2,
                              label="pseudo-boundary")],
              loc="upper center", ncol=2, fontsize=6.5, handlelength=1.0, columnspacing=1.0, borderaxespad=0.1)
    ax.grid(axis="y", visible=False)


def panel_exit(ax, res, pooled):
    rows = SCORABLE
    ys = np.arange(len(rows))[::-1] + 2.2
    for y, p in zip(ys, rows):
        ex = res[p]["exit"]
        m, lo, hi = ci_exp(ex["b_forced_between"], ex["se_forced_between"])
        ax.plot([lo, hi], [y] * 2, color=WIPE, lw=1.1)
        ax.plot(m, y, "s", ms=3, color=WIPE)
    pe = pooled["exit_forced"]
    yp = 1.0
    ax.fill_betweenx([yp - 0.3, yp + 0.3], np.exp(pe["lo"]), np.exp(pe["hi"]), color=WIPE, alpha=0.35, lw=0)
    ax.plot(np.exp(pe["mean"]), yp, "D", ms=4, color=WIPE)
    ax.text(np.exp(pe["hi"]) * 1.12, yp, f"exit {np.exp(pe['mean']):.1f}×", color=WIPE, fontsize=6.5, va="center")
    po = pooled["onset_forced"]
    yo = -0.2
    ax.fill_betweenx([yo - 0.3, yo + 0.3], np.exp(po["lo"]), np.exp(po["hi"]), color=vs.C["sky"], alpha=0.45, lw=0)
    ax.plot(np.exp(po["mean"]), yo, "D", ms=4, color=vs.C["sky"])
    ax.text(np.exp(po["hi"]) * 1.25, yo, f"onset {np.exp(po['mean']):.2f}×", color=vs.INK2, fontsize=6.5,
            va="center")
    ax.axvline(1, color=vs.INK2, lw=0.6)
    ax.set_xscale("log")
    ax.set_xlim(0.2, 40)
    ax.set_xticks([0.25, 0.5, 1, 2, 5, 10, 20])
    ax.set_xticklabels(["0.25", "0.5", "1", "2", "5", "10", "20"])
    ax.set_yticks(list(ys) + [yp, yo])
    ax.set_yticklabels(rows + ["pooled exit", "pooled onset"])
    ax.set_ylim(-1.0, ys[0] + 0.8)
    ax.set_xlabel("odds ratio, forced erasure in between")
    ax.set_title("(c) an erasure breaks loops", loc="left")
    ax.grid(axis="y", visible=False)


def static():
    vs.use()
    res = json.loads((D / "results.json").read_text())
    fig, axs = plt.subplots(1, 3, figsize=(vs.W["double"], 2.55), gridspec_kw={"width_ratios": [1.05, 1.1, 1.0]})
    panel_schematic(axs[0])
    panel_enrich(axs[1], res["periods"], res["pooled"])
    panel_exit(axs[2], res["periods"], res["pooled"])
    fig.tight_layout(w_pad=0.6)
    vs.save(fig, HERE / "fig")
    plt.close(fig)


# ------------------------------------------------------------------------------------------------ animation
TOPIC = [vs.C["green"], vs.C["pink"], vs.C["sky"], vs.INK2, "#bfbfbf"]


def story(seed=11, n_seg=3, seg_len=12):
    """Schematic: each new statement copies an in-context own statement with a probability that grows with the
    number of own statements in the segment (the card's own-count trigger); otherwise it says something new."""
    rng = np.random.default_rng(seed)
    out = []
    for seg in range(n_seg):
        ctx = []
        for j in range(seg_len):
            p_copy = min(0.85, 0.08 + 0.09 * len(ctx)) if ctx else 0.0
            if ctx and rng.random() < p_copy:
                src = len(ctx) - 1 if rng.random() < 0.7 else int(rng.integers(len(ctx)))
                c, copy = ctx[src], src
            else:
                c, copy = int(rng.integers(len(TOPIC))), None
                while ctx and c == ctx[-1]:
                    c = int(rng.integers(len(TOPIC)))
            ctx.append(c)
            out.append({"seg": seg, "j": j, "c": c, "copy": copy})
    return out, seg_len


def anim():
    from matplotlib import animation
    vs.use()
    st, L = story()
    FPS, FPS_ST, HOLD = 24, 8, 14
    frames = []
    for i, s in enumerate(st):
        if s["j"] == 0 and i > 0:
            frames += [(i - 1, "wipe")] * HOLD
        frames += [(i, "st")] * FPS_ST
    frames += [(len(st) - 1, "st")] * 20
    fig = plt.figure(figsize=(8, 4.5), dpi=160)
    axT = fig.add_axes([0.05, 0.86, 0.9, 0.12]); axT.axis("off")
    ax = fig.add_axes([0.04, 0.08, 0.92, 0.74]); ax.axis("off")
    ax.set_xlim(-0.5, L + 0.5); ax.set_ylim(-4.2, 3.2)
    axT.text(0, 0.7, "A restatement loop copies its own context; a wipe breaks it", fontsize=13, va="center")
    axT.text(0, 0.1, "schematic: colored blocks stand for one agent's statements (no text); copying odds grow with "
             "own statements in context", fontsize=7.5, va="center", color=vs.INK2)
    counter = axT.text(1, 0.7, "", fontsize=10, ha="right", va="center", color=vs.INK2, family="monospace")
    ax.text(-0.3, 2.35, "context window (own statements since the last wipe)", fontsize=8.5, color=vs.INK)
    box = Rectangle((-0.3, 0.35), L + 0.6, 1.5, fc="none", ec=vs.INK2, lw=1.0)
    ax.add_patch(box)
    slots = [Rectangle((j + 0.1, 0.55), 0.8, 1.1, fc="white", ec="none") for j in range(L)]
    for r in slots:
        ax.add_patch(r)
    ax.text(-0.3, -0.75, "all statements so far", fontsize=8.5, color=vs.INK)
    n = len(st)
    w = (L + 0.6) / n
    hist = [Rectangle((-0.3 + i * w + 0.03, -2.1), w - 0.06, 1.0, fc="white", ec="none") for i in range(n)]
    for r in hist:
        ax.add_patch(r)
    for k in range(1, 3):
        ax.plot([-0.3 + k * L * w] * 2, [-2.3, -0.9], color=WIPE, ls="--", lw=1.0)
    marks = [ax.text(-0.3 + (i + 0.5) * w, -2.45, "", ha="center", va="top", fontsize=9, color=CTX) for i in range(n)]
    arrow = ax.annotate("", xy=(0, 0), xytext=(0, 0),
                        arrowprops=dict(arrowstyle="-|>", lw=1.6, color=CTX, connectionstyle="arc3,rad=0.5"))
    msg = ax.text(L / 2, 2.85, "", ha="center", fontsize=10, color=WIPE)
    note = ax.text(-0.3, -3.55, "", fontsize=8.5, color=vs.INK2)

    def draw(f):
        i, mode = frames[f]
        s = st[i]
        base = i - s["j"]
        if mode == "wipe":
            for r in slots:
                r.set_facecolor("white")
            arrow.set_visible(False)
            msg.set_text("WIPE: context emptied, the loop's source is gone")
        else:
            msg.set_text("")
            for j in range(L):
                slots[j].set_facecolor(TOPIC[st[base + j]["c"]] if j <= s["j"] else "white")
            if s["copy"] is not None:
                arrow.set_visible(True)
                arrow.xy = (s["copy"] + 0.5, 1.9); arrow.set_position((s["j"] + 0.5, 1.9))
            else:
                arrow.set_visible(False)
        for k in range(n):
            hist[k].set_facecolor(TOPIC[st[k]["c"]] if k <= i else "white")
            marks[k].set_text("c" if (k <= i and st[k]["copy"] is not None) else "")
        cp = sum(1 for k in range(base, i + 1) if st[k]["copy"] is not None)
        note.set_text(f"copies (c) in this segment: {cp} of {s['j'] + 1}    measured: a source still in context is "
                      "near-copied 3.4x as often; a forced wipe raises loop exit 2.4x")
        counter.set_text(f"statement {i + 1:2d}")
        return slots + hist + marks + [arrow, msg, note, counter]

    a = animation.FuncAnimation(fig, draw, frames=len(frames), interval=1000 / FPS)
    a._save_count = len(frames)
    vs.save_anim(a, HERE / "anim", fps=FPS, dpi=160, poster_frame=frames.index((L + 10, "st")))
    plt.close(fig)
    print("anim frames", len(frames), "duration", len(frames) / FPS)


if __name__ == "__main__":
    static()
    if "--no-anim" not in sys.argv:
        anim()
