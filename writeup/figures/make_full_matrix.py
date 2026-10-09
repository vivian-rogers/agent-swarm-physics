"""Full hypothesis x physics-model table (all scored hypotheses, 17 models) -> writeup/papers/thermodynamics/figs/full_matrix.pdf
(+ writeup/figures/full_matrix.png). Model assignments: meta.json `models` plus writeup/figures/model_overrides.py.

Usage: uv run python writeup/figures/make_full_matrix.py
"""
import sys
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
sys.path.insert(0, "writeup/visuals"); import vstyle as vs
sys.path.insert(0, "writeup/figures"); import model_overrides as mo
vs.use()
hs = mo.load_hypotheses()
cols, MN = mo.COLS, mo.SHORT
OUT = {"supported": "#0ca30c", "mixed": "#8c8c8c", "refuted": "#d03b3b"}
ROLE = {"primary": ("o", 22), "secondary": ("o", 8), "rival": ("D", 9), "null": ("s", 9), "tool": ("^", 9)}
half = (len(hs) + 1) // 2
fig, axes = plt.subplots(1, 2, figsize=(7.0, 9.4))
for ax, chunk in zip(axes, (hs[:half], hs[half:])):
    for i, h in enumerate(chunk):
        for m in sorted(h["models"], key=lambda m: m["role"] != "primary"):  # primaries underneath
            if m["model"] not in cols: continue
            j = cols.index(m["model"]); mk, sz = ROLE.get(m["role"], ("o", 6)); c = OUT.get(m.get("outcome"), "#cfcfcf")
            hol = m["role"] in ("null", "tool")
            ax.scatter(j, i, marker=mk, s=sz, facecolor="white" if hol else c, edgecolor=c, lw=0.7, zorder=3)
    ax.set_xlim(-0.6, len(cols) - 0.4); ax.set_ylim(len(chunk) - 0.4, -0.6)
    ax.set_yticks(range(len(chunk))); ax.set_yticklabels([f"{h['id']} {mo.clean_title(h['title'])[:30]}" for h in chunk], fontsize=4.3)
    ax.set_xticks(range(len(cols))); ax.set_xticklabels([f"{c} {n}" for c, n in zip(cols, MN)], fontsize=4.6, rotation=90)
    ax.xaxis.tick_top(); ax.tick_params(length=0); ax.grid(True, color=vs.GRID, lw=0.3)
    for s in ax.spines.values(): s.set_visible(False)
leg = [("primary", "o", 22, False), ("secondary", "o", 8, False), ("rival", "D", 9, False), ("null", "s", 9, True), ("tool", "^", 9, True)]
for k, (lab, mk, sz, hol) in enumerate(leg):
    fig.text(0.08 + 0.09 * k, 0.012, lab, fontsize=6, va="center")
    fig.add_artist(plt.Line2D([0.07 + 0.09 * k], [0.012], marker=mk, markersize=sz ** 0.5, color=vs.INK2, mfc="white" if hol else vs.INK2, transform=fig.transFigure, ls=""))
for k, (lab, c) in enumerate([("supported", OUT["supported"]), ("mixed", OUT["mixed"]), ("refuted", OUT["refuted"]), ("untested / n/a", "#cfcfcf")]):
    fig.patches.append(Rectangle((0.56 + 0.105 * k, 0.006), 0.012, 0.012, color=c, transform=fig.transFigure, figure=fig))
    fig.text(0.575 + 0.105 * k, 0.012, lab, fontsize=6, va="center")
fig.subplots_adjust(left=0.18, right=0.99, top=0.90, bottom=0.03, wspace=0.95)
fig.savefig("writeup/papers/thermodynamics/figs/full_matrix.pdf"); fig.savefig("writeup/figures/full_matrix.png", dpi=200)
print(len(hs), "hypotheses,", len(cols), "models; rows", hs[0]["id"], "-", hs[half - 1]["id"], "|", hs[half]["id"], "-", hs[-1]["id"])
