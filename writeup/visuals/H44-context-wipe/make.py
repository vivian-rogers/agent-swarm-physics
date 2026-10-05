"""H44 + H15 writeup visual: a forced context wipe and what it costs.

Static figure (fig.pdf/png, double column):
  (a) schematic: context fill over calls, wiped at the 40-call cap (simulation, not data)
  (b) G51 write share around forced wipes vs no-reset pseudo-erasures (gray band)
  (c) G51 work commits per call, same alignment
  (d) G51 re-acquisition share (reads, screenshots, history search), same alignment
  (e) per-period work-commit dip over calls +1..+10 (forced) vs pseudo-erasures (gray)
  (f) command-loop recurrence after a forced wipe vs a no-reset boundary, per period

Animation (writeup/animations/H44-context-wipe.mp4): one agent's context window filling block by block (block colors sampled from the
measured G51 call-category shares at each call offset), a forced wipe at the cap, re-reading, the measured
write-share meter dipping and recovering, and one command loop broken by a wipe (loop is schematic).

Inputs (processed, non-holdout): data/processed/H44-erasure-reacquisition-thrash/{G*,NE41}/results.json.
Run: uv run python writeup/visuals/H44-context-wipe/make.py [--no-anim]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation
from matplotlib.patches import Rectangle, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "writeup/visuals"))
import vstyle as vs  # noqa: E402

HERE = Path(__file__).resolve().parent
D44 = ROOT / "data/processed/H44-erasure-reacquisition-thrash"
PERIODS = ["G36", "G37", "G38", "G39", "G40", "G41", "G42", "G44", "G51"]
WIPE = vs.C["red"]          # forced erasure (not a field, not a coupling)
CATS = ["write", "talk", "room_read", "notes_read", "local_read", "remote_read", "run", "look", "gui_type", "gui",
        "monitor", "setup", "idle", "other"]   # H44 call categories (scheme/h44common.py)
REACQ = {"room_read", "notes_read", "local_read", "remote_read", "look"}


def load(p):
    return json.loads((D44 / p / "results.json").read_text())


def curve(r, kind, q):
    c = r["curves"][kind]
    return np.array(c["k"]), np.array(c[q]["est"]), np.array(c[q]["lo"]), np.array(c[q]["hi"])


from matplotlib.lines import Line2D  # noqa: E402
HANDLES = [Line2D([], [], color=WIPE, marker="s", ms=3, lw=1.1, label="forced wipe"),
           Line2D([], [], color=vs.NULL, marker="o", mfc=vs.MUTED, mec=vs.MUTED, ms=3, lw=2.2, label="no reset")]


def wilson(k, n, z=1.96):
    if n == 0:
        return np.nan, np.nan
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return c - h, c + h


# ------------------------------------------------------------------------------------------------ static
def panel_schematic(ax):
    calls = np.arange(0, 121)
    fill = calls % 40
    ax.fill_between(calls, 0, fill, step="post", color=vs.C["sky"], alpha=0.35, lw=0)
    ax.step(calls, fill, where="post", color=vs.INK2, lw=1.0)
    for w in (40, 80):
        ax.axvline(w, color=WIPE, lw=1.2, ls="--")
        ax.axvspan(w, w + 5, color=vs.C["sky"], alpha=0.5, lw=0)
    ax.text(42, 41, "wipe at\ncap", color=WIPE, fontsize=6.5, va="bottom")
    ax.annotate("re-read", xy=(84, 3), xytext=(96, 6), fontsize=6.5, color=vs.INK2,
                arrowprops=dict(arrowstyle="-", lw=0.6, color=vs.INK2))
    ax.set_xlim(0, 120)
    ax.set_ylim(0, 55)
    ax.set_xlabel("model call")
    ax.set_ylabel("calls held in context")
    ax.set_title("(a) context window", loc="left")
    ax.text(2, 51, "schematic", fontsize=6.5, color=vs.MUTED, va="top")


def event_panel(ax, r, q, title, ylab, scale=1.0, note=None):
    k, y, lo, hi = curve(r, "pseudo21", q)
    ax.fill_between(k, lo * scale, hi * scale, color=vs.NULL, alpha=0.6, lw=0, label="no reset (pseudo)")
    ax.plot(k, y * scale, color=vs.MUTED, lw=0.8)
    k, y, lo, hi = curve(r, "forced", q)
    for side in (k < 0, k > 0):
        ax.fill_between(k[side], lo[side] * scale, hi[side] * scale, color=WIPE, alpha=0.25, lw=0)
        ax.plot(k[side], y[side] * scale, color=WIPE, lw=1.5, label="forced wipe" if side[0] else None)
    ax.axvline(0, color=vs.INK2, lw=0.6, ls=":")
    ax.set_xlim(-20.5, 20.5)
    ax.set_xticks([-20, -10, 0, 10, 20])
    ax.set_xlabel("calls from boundary")
    ax.set_ylabel(ylab)
    ax.set_title(title, loc="left")
    if note:
        ax.text(0.97, 0.05, note, transform=ax.transAxes, ha="right", va="bottom", fontsize=6.5, color=vs.INK2)


def panel_forest(ax, res, pooled):
    ys = np.arange(len(PERIODS))[::-1]
    for y, p in zip(ys, PERIODS):
        c = res[p]["stats"]["forced"]["contrasts"]["post10_vs_far"]["work_rel"]
        ps = res[p]["stats"]["pseudo31"]["contrasts"]["post10_vs_far"]["work_rel"]
        ax.plot([ps[1] * 100, ps[2] * 100], [y - 0.18] * 2, color=vs.NULL, lw=2.2, solid_capstyle="butt")
        ax.plot(ps[0] * 100, y - 0.18, "o", ms=2.6, color=vs.MUTED)
        ax.plot([c[1] * 100, c[2] * 100], [y + 0.12] * 2, color=WIPE, lw=1.1)
        ax.plot(c[0] * 100, y + 0.12, "s", ms=3, color=WIPE)
    pf = pooled["forced:post10_vs_far:work_rel"]
    pp = pooled["pseudo31:post10_vs_far:work_rel"]
    y0 = -1.3
    ax.fill_betweenx([y0 - 0.35, y0 + 0.35], pf["lo"] * 100, pf["hi"] * 100, color=WIPE, alpha=0.35, lw=0)
    ax.plot(pf["est"] * 100, y0, "D", ms=4, color=WIPE)
    ax.fill_betweenx([y0 - 0.35, y0 + 0.35], pp["lo"] * 100, pp["hi"] * 100, color=vs.NULL, alpha=0.8, lw=0)
    ax.plot(pp["est"] * 100, y0, "D", ms=3.5, color=vs.MUTED)
    ax.axvline(0, color=vs.INK2, lw=0.6)
    ax.set_yticks(list(ys) + [y0])
    ax.set_yticklabels(PERIODS + ["pooled"])
    ax.set_xlim(-75, 110)
    ax.set_xlabel("work commits, calls +1…+10 (%)")
    ax.set_title("(e) dip by period", loc="left")
    ax.text(pf["lo"] * 100 - 4, y0, f"$-${abs(pf['est'])*100:.0f}%", color=WIPE, fontsize=6.5, ha="right", va="center")
    ax.legend(handles=HANDLES, loc="upper center", ncol=2, fontsize=6.5, handlelength=1.0, columnspacing=1.0,
              borderaxespad=0.1)
    ax.set_ylim(y0 - 1.3, ys[0] + 1.7)
    ax.grid(axis="y", visible=False)


def panel_loops(ax, res):
    rows = [p for p in PERIODS if res[p]["loops"]["forced"]["n_loop_events"] >= 30]
    x = np.arange(len(rows))
    for i, p in enumerate(rows):
        L = res[p]["loops"]
        for kind, dx, col, mk in (("pseudo31", -0.16, vs.MUTED, "o"), ("forced", 0.16, WIPE, "s")):
            n = L[kind]["n_loop_events"]
            pr = L[kind]["recur"]
            lo, hi = wilson(round(pr * n), n)
            ax.plot([i + dx] * 2, [lo * 100, hi * 100], color=col if kind == "forced" else vs.NULL,
                    lw=1.1 if kind == "forced" else 2.2, solid_capstyle="butt")
            ax.plot(i + dx, pr * 100, mk, ms=3.2, color=col)
    ax.set_xticks(x)
    ax.set_xticklabels(rows, fontsize=6.5)
    ax.set_ylim(0, 112)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_xlim(-0.6, len(rows) - 0.4)
    ax.set_ylabel("loop recurs, next 10 calls (%)")
    ax.set_title("(f) command loops", loc="left")
    ax.legend(handles=HANDLES, loc="upper center", ncol=2, fontsize=6.5, handlelength=1.0, columnspacing=1.0,
              borderaxespad=0.1)
    ax.grid(axis="x", visible=False)


def static():
    vs.use()
    res = {p: load(p) for p in PERIODS}
    ne = json.loads((D44 / "NE41/results.json").read_text())
    r = res["G51"]
    fig, axs = plt.subplots(2, 3, figsize=(vs.W["double"], 4.35))
    panel_schematic(axs[0, 0])
    event_panel(axs[0, 1], r, "W", "(b) write share (G51)", "share of calls that write")
    axs[0, 1].legend(loc="lower right", fontsize=6.5, handlelength=1.4)
    event_panel(axs[0, 2], r, "work", "(c) work commits (G51)", "commits per call")
    event_panel(axs[1, 0], r, "R", "(d) re-reading (G51)", "re-acquisition share")
    axs[1, 0].annotate(r"0.22 $\rightarrow$ 0.47", xy=(1, 0.473), xytext=(5, 0.43), fontsize=6.5, color=WIPE,
                       arrowprops=dict(arrowstyle="-", lw=0.6, color=WIPE))
    panel_forest(axs[1, 1], res, ne["pooled"])
    panel_loops(axs[1, 2], res)
    fig.tight_layout(h_pad=1.0, w_pad=0.8)
    vs.save(fig, HERE / "fig")
    plt.close(fig)


# ------------------------------------------------------------------------------------------------ animation
CAT_COLOR = {"write": vs.C["green"], "reacq": vs.C["sky"], "talk": vs.C["pink"], "other": "#d9d9d9",
             "loop": WIPE}


def cat_group(name):
    if name == "write":
        return "write"
    if name in REACQ:
        return "reacq"
    if name == "talk":
        return "talk"
    return "other"


def build_story(r, seed=7):
    """Three 40-call segments; categories sampled from the measured G51 shares at each segment position."""
    cf = r["curves"]["forced"]
    k = np.array(cf["k"])
    shares = np.array(cf["shares"])          # rows: k, cols: CATS
    W = np.array(cf["W"]["est"])
    pos_share, pos_W = {}, {}
    for pos in range(1, 41):                 # pos 1..20 = k +1..+20; pos 21..40 = k -20..-1
        kk = pos if pos <= 20 else pos - 41
        i = int(np.where(k == kk)[0][0])
        pos_share[pos] = shares[i] / shares[i].sum()
        pos_W[pos] = W[i]
    rng = np.random.default_rng(seed)
    story = []
    for seg in range(3):
        for pos in range(1, 41):
            c = CATS[rng.choice(len(CATS), p=pos_share[pos])]
            story.append({"seg": seg, "pos": pos, "grp": cat_group(c), "W": pos_W[pos]})
    # schematic command loop: segment 2 positions 24..40 repeat one command; it does not recur after the wipe
    for s in story:
        if s["seg"] == 1 and s["pos"] >= 24 and s["pos"] % 2 == 0:
            s["grp"] = "loop"
    return story, pos_W


def anim():
    vs.use()
    r = load("G51")
    story, pos_W = build_story(r)
    k, pW, pW_lo, pW_hi = curve(r, "pseudo21", "W")
    null_level = float(np.mean(pW[k > 0]))
    null_lo, null_hi = float(np.mean(pW_lo[k > 0])), float(np.mean(pW_hi[k > 0]))
    n_calls = len(story)
    FPC = 3                      # frames per call
    HOLD = 10                    # extra frames at each wipe
    frames = []
    for i in range(n_calls):
        hold = HOLD if story[i]["pos"] == 1 and i > 0 else 0
        frames += [(i, "wipe")] * hold + [(i, "call")] * FPC
    frames += [(n_calls - 1, "call")] * 24

    fig = plt.figure(figsize=(1280 / 160, 720 / 160), dpi=160)
    fig.patch.set_facecolor("white")
    axT = fig.add_axes([0.05, 0.86, 0.9, 0.12]); axT.axis("off")
    axC = fig.add_axes([0.06, 0.52, 0.88, 0.30]); axC.axis("off")
    axM = fig.add_axes([0.08, 0.10, 0.86, 0.34])
    axT.text(0, 0.75, "A forced context wipe: re-read, then rebuild output", fontsize=13, color=vs.INK, va="center")
    axT.text(0, 0.15, "one agent's context window (block colors sampled from measured G51 call shares; loop schematic)",
             fontsize=7.5, color=vs.INK2, va="center")
    counter = axT.text(1, 0.75, "", fontsize=10, ha="right", va="center", color=vs.INK2, family="monospace")

    # context bar
    axC.set_xlim(-1, 41); axC.set_ylim(-1.6, 2.2)
    axC.add_patch(FancyBboxPatch((-0.3, -0.25), 40.6, 1.5, boxstyle="round,pad=0.05", fc="none", ec=vs.INK2, lw=1.0))
    axC.text(-0.3, 1.55, "context window", fontsize=8.5, color=vs.INK, va="bottom")
    cap = axC.text(40.3, 1.55, "", fontsize=8.5, color=vs.INK2, ha="right", va="bottom")
    blocks = [Rectangle((j + 0.08, 0.0), 0.84, 1.0, fc="white", ec="none") for j in range(40)]
    for b in blocks:
        axC.add_patch(b)
    legend_items = [("write", "write"), ("reacq", "re-read (files, screen, history)"), ("talk", "talk"),
                    ("other", "run / GUI / other"), ("loop", "repeated command (loop)")]
    for x0, (g, lab) in zip([0, 4.5, 17.5, 21.5, 30.5], legend_items):
        axC.add_patch(Rectangle((x0, -1.25), 0.8, 0.55, fc=CAT_COLOR[g], ec="none"))
        axC.text(x0 + 1.1, -0.97, lab, fontsize=7, va="center", color=vs.INK2)
    flash = axC.text(20, 0.5, "", fontsize=16, ha="center", va="center", color=WIPE, weight="bold")

    # output meter
    xs = np.arange(n_calls) + 1
    axM.axhspan(null_lo, null_hi, color=vs.NULL, alpha=0.6, lw=0)
    axM.text(n_calls + 1, null_level, "no-reset\nlevel", fontsize=7, va="center", color=vs.MUTED)
    for w in (40, 80):
        axM.axvline(w + 0.5, color=WIPE, lw=0.8, ls="--")
    line, = axM.plot([], [], color=vs.C["green"], lw=1.8)
    dot, = axM.plot([], [], "o", color=vs.C["green"], ms=5)
    axM.set_xlim(0, n_calls + 12)
    axM.set_ylim(0.0, 0.2)
    axM.set_xlabel("model call", fontsize=8)
    axM.set_ylabel("write share\n(measured, G51)", fontsize=8)
    axM.tick_params(labelsize=7)
    dip = axM.text(0, 0, "", fontsize=8, color=WIPE)
    Wseries = np.array([s["W"] for s in story])

    def draw(fi):
        i, mode = frames[fi]
        s = story[i]
        seg_start = i - (s["pos"] - 1)
        if mode == "wipe":
            for b in blocks:
                b.set_facecolor("white")
            flash.set_text("WIPE: 41-record cap")
            cap.set_text("fill 0 / 40")
            line.set_data(xs[:i], Wseries[:i]); dot.set_data([], [])
        else:
            flash.set_text("")
            for j in range(40):
                idx = seg_start + j
                blocks[j].set_facecolor(CAT_COLOR[story[idx]["grp"]] if j < s["pos"] else "white")
            cap.set_text(f"fill {s['pos']:2d} / 40")
            line.set_data(xs[: i + 1], Wseries[: i + 1]); dot.set_data([xs[i]], [Wseries[i]])
        if s["seg"] >= 1 and s["pos"] <= 6:
            dip.set_position((seg_start + 1.5, 0.035))
            dip.set_text("re-reading: writes dip, recover in ~3 calls")
        elif s["seg"] == 2 and 1 <= s["pos"] <= 14:
            dip.set_text("")
        else:
            dip.set_text("")
        if s["seg"] == 1 and s["pos"] >= 26:
            flash.set_text("")
            axC.set_title("")
        counter.set_text(f"call {i + 1:3d}   since wipe {s['pos']:2d}")
        return blocks + [line, dot, flash, cap, counter, dip]

    loop_note = axC.text(20, 1.55, "", fontsize=8, ha="center", va="bottom", color=WIPE)

    def draw2(fi):
        out = draw(fi)
        i, _ = frames[fi]
        s = story[i]
        if s["seg"] == 1 and s["pos"] >= 26:
            loop_note.set_text("loop: same command repeats")
        elif s["seg"] == 2 and s["pos"] <= 12:
            loop_note.set_text("wipe broke the loop: loops recur 16% after a wipe vs 72% without (G38)")
        else:
            loop_note.set_text("")
        return out + [loop_note]

    a = animation.FuncAnimation(fig, draw2, frames=len(frames), interval=1000 / 24, blit=False)
    a._save_count = len(frames)
    vs.save_anim(a, HERE / "anim", fps=24, dpi=160, poster_frame=frames.index((84, "call")))
    plt.close(fig)
    print("frames", len(frames), "duration s", len(frames) / 24)


if __name__ == "__main__":
    static()
    if "--no-anim" not in sys.argv:
        anim()
