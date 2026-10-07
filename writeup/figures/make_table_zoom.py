"""Hypothesis x physics-model table (H01-H20 sample, 17 models) zooming into one cell's goal-period verdicts.

Panel (a): meta.json `models` plus writeup/figures/model_overrides.py (2026-10-07).
Panel (b): the latest per-period verdict in each period README of the zoomed card
(Verdict (r2) > Verdict (2) > Verdict (1c) > Verdict (1b) > Verdict).

Usage: uv run python writeup/figures/make_table_zoom.py
    -> writeup/figures/table_zoom.{pdf,png} and writeup/paper/figs/table_zoom.pdf
"""
import re, sys
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, ConnectionPatch
sys.path.insert(0, "writeup/visuals"); import vstyle as vs
sys.path.insert(0, "writeup/figures"); import model_overrides as mo
collect = mo.collect

vs.use()
ZOOM_H, ZOOM_M = "H08", "02"
hs = {h["id"]: h for h in mo.load_hypotheses()}
rows = [f"H{i:02d}" for i in range(1, 21)]
cols = mo.COLS
MNAME = mo.NAME
LATEST = ("Verdict (r2)", "Verdict (2)", "Verdict (1c)", "Verdict (1b)", "Verdict")


def latest_verdicts(h):
    """Per-period verdict from the latest round written in each period README."""
    out = {}
    for p in h["periods"]:
        t = (collect.ROOT / p["path"]).read_text(errors="replace")
        v = next((x for x in (collect.field(t, k) for k in LATEST) if x), "")
        out[p["period"]] = collect.verdict_key(v)
    return out
OUT = {"supported": "#0ca30c", "mixed": "#8c8c8c", "refuted": "#d03b3b"}
ROLE = {"primary": ("o", 46), "secondary": ("o", 18), "rival": ("D", 20), "null": ("s", 20), "tool": ("^", 20)}

fig = plt.figure(figsize=(7.0, 3.35))
ax = fig.add_axes([0.07, 0.17, 0.40, 0.70])
for i, hid in enumerate(rows):
    for m in sorted(hs.get(hid, {}).get("models") or [], key=lambda m: m["role"] != "primary"):
        if m["model"] not in cols:
            continue
        j = cols.index(m["model"])
        mk, sz = ROLE.get(m["role"], ("o", 10))
        c = OUT.get(m.get("outcome"), "#cfcfcf")
        hollow = m["role"] in ("null", "tool")
        ax.scatter(j, i, marker=mk, s=sz, facecolor="white" if hollow else c, edgecolor=c, lw=0.9, zorder=3)
ax.set_xlim(-0.6, len(cols) - 0.4); ax.set_ylim(len(rows) - 0.4, -0.6)
ax.set_xticks(range(len(cols))); ax.set_xticklabels(cols, fontsize=6)
ax.set_yticks(range(len(rows))); ax.set_yticklabels(rows, fontsize=6)
ax.tick_params(length=0); ax.grid(True, color=vs.GRID, lw=0.4)
ax.set_xlabel("physics model", fontsize=7); ax.set_title("(a) hypothesis × physics model (sample: H01–H20)", fontsize=7.5, loc="left")
for s in ax.spines.values(): s.set_visible(False)
zi, zj = rows.index(ZOOM_H), cols.index(ZOOM_M)
ax.add_patch(Rectangle((zj - 0.5, zi - 0.5), 1, 1, fill=False, ec=vs.INK, lw=1.4, zorder=4))
# legend: role glyphs and outcome colors
lx = ax.inset_axes([0.0, -0.30, 1.0, 0.12]); lx.axis("off"); lx.set_xlim(0, 10); lx.set_ylim(0, 1)
items = [("primary", "o", 30, False), ("secondary", "o", 12, False), ("rival", "D", 20, False), ("null", "s", 20, True), ("tool", "^", 20, True)]
for k, (lab, mk, sz, hol) in enumerate(items):
    lx.scatter(0.15 + 2.0 * k, 0.75, marker=mk, s=sz, facecolor="white" if hol else vs.INK2, edgecolor=vs.INK2, lw=0.9)
    lx.text(0.42 + 2.0 * k, 0.75, lab, fontsize=6, va="center")
for k, (lab, c) in enumerate([("supported", OUT["supported"]), ("mixed", OUT["mixed"]), ("refuted", OUT["refuted"]), ("untested", "#cfcfcf")]):
    lx.add_patch(Rectangle((0.15 + 2.0 * k, 0.0), 0.25, 0.3, color=c)); lx.text(0.5 + 2.0 * k, 0.15, lab, fontsize=6, va="center")

# (b) the zoomed cell: verdict per goal period
VC = {"supported": "#0ca30c", "failed": "#d03b3b", "mixed": "#8c8c8c", "descriptive": "#a9d8a9"}
h = hs[ZOOM_H]
verd = latest_verdicts(h)
bx = fig.add_axes([0.55, 0.22, 0.43, 0.58]); bx.axis("off")
ncol = 17
for g in range(1, 52):
    r, c = (g - 1) // ncol, (g - 1) % ncol
    v = verd.get(f"G{g:02d}")
    bx.add_patch(Rectangle((c, -r), 0.88, 0.88, color=VC.get(v, "#e3e3e3"), ec="white", lw=0.5))
    bx.text(c + 0.44, -r + 0.44, str(g), fontsize=4.6, ha="center", va="center", color="white" if v in VC else vs.MUTED)
bx.set_xlim(-0.2, ncol + 0.2); bx.set_ylim(-2.4, 1.05)
# regime bands under each period tile row: I = 1-32, II = 33-36, III = 37-51
for g in range(1, 52):
    r, c = (g - 1) // ncol, (g - 1) % ncol
    reg = "I" if g <= 32 else ("II" if g <= 36 else "III")
    bx.add_patch(Rectangle((c, -r - 0.10), 0.88, 0.06, color={"I": vs.C["sky"], "II": vs.MUTED, "III": vs.C["blue"]}[reg], lw=0))
nes = [p for p in h["periods"] if p["period"].startswith("NE")]
for k, p in enumerate(nes):
    bx.add_patch(Rectangle((k * 2.6, -3.55), 2.4, 0.7, color=VC.get(verd[p["period"]], "#e3e3e3"), ec="white"))
    bx.text(k * 2.6 + 1.2, -3.2, p["period"], fontsize=5, ha="center", va="center", color="white")
bx.set_ylim(-3.7, 1.05)
title = f"(b) one cell: {ZOOM_H} × {ZOOM_M} ({MNAME[ZOOM_M]}), verdict per goal period"
fig.text(0.55, 0.88, title, fontsize=7.5)
fig.text(0.55, 0.835, mo.clean_title(h["title"])[:78], fontsize=6.2, color=vs.INK2)
lg = [("supported", VC["supported"]), ("failed", VC["failed"]), ("mixed", VC["mixed"]), ("descriptive", VC["descriptive"]), ("not tested", "#e3e3e3")]
for k, (lab, c) in enumerate(lg):
    fig.patches.append(Rectangle((0.55 + 0.085 * k, 0.12), 0.012, 0.025, color=c, transform=fig.transFigure, figure=fig))
    fig.text(0.565 + 0.085 * k, 0.1325, lab, fontsize=5.8, va="center")
fig.text(0.55, 0.075, "bar under each tile: scaffold regime I (light) · II (gray) · III (dark);  chips: natural-experiment tests", fontsize=5.6, color=vs.INK2)
# the pointer from the cell to the zoom
con = ConnectionPatch(xyA=(zj + 0.5, zi), coordsA=ax.transData, xyB=(-0.25, 0.4), coordsB=bx.transData,
                      arrowstyle="-|>", color=vs.INK, lw=1.0, mutation_scale=8, connectionstyle="arc3,rad=-0.15")
fig.add_artist(con)
vs.save(fig, "writeup/figures/table_zoom")
fig.savefig("writeup/paper/figs/table_zoom.pdf")
print("ok", ZOOM_H, ZOOM_M, len(nes), "NE chips;", {k: v for k, v in sorted(verd.items())})
