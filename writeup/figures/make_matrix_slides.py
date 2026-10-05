"""Hypothesis x physics-model table for slides: 3 landscape pages of 44 rows (2 panels of 22).

Usage: uv run python writeup/figures/make_matrix_slides.py  -> writeup/figures/matrix_slide_{1,2,3}.pdf
"""
import re, sys
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
sys.path.insert(0, "writeup/visuals"); import vstyle as vs
sys.path.insert(0, "dashboard"); import collect
vs.use()
hs = []
for d in sorted(collect.HYP.iterdir(), key=lambda d: int(re.match(r"^H(\d+)", d.name).group(1)) if re.match(r"^H\d+-", d.name) else 0):
    if d.is_dir() and re.match(r"^H\d{2,}-", d.name):
        hs.append(collect.hypothesis(d))
cols = [f"{i:02d}" for i in range(1, 16)]
MN = ["inv. Ising", "kin. Ising", "contagion", "sem. info", "replicators", "neutral", "fluct. env.", "copying",
      "Hawkes", "Potts", "vector spins", "info dyn.", "conventions", "scaling", "stoch. thermo"]
OUT = {"supported": "#0ca30c", "mixed": "#8c8c8c", "refuted": "#d03b3b"}
ROLE = {"primary": ("o", 60), "secondary": ("o", 20), "rival": ("D", 22), "null": ("s", 22), "tool": ("^", 24)}


def clean(t):
    return t.replace("gating", "coupling").replace("gated", "filtered").replace("Holdout", "Reserved").replace("holdout", "reserved")


per, rows = 44, 22
for page in range((len(hs) + per - 1) // per):
    block = hs[page * per:(page + 1) * per]
    fig, axes = plt.subplots(1, 2, figsize=(13.33, 6.3))
    for ax, chunk in zip(axes, (block[:rows], block[rows:])):
        for i, h in enumerate(chunk):
            for m in (h.get("models") or []):
                if m["model"] not in cols: continue
                j = cols.index(m["model"]); mk, sz = ROLE.get(m["role"], ("o", 16)); c = OUT.get(m.get("outcome"), "#cfcfcf")
                hol = m["role"] in ("null", "tool")
                ax.scatter(j, i, marker=mk, s=sz, facecolor="white" if hol else c, edgecolor=c, lw=1.0, zorder=3)
        ax.set_xlim(-0.6, 14.6); ax.set_ylim(rows - 0.4, -0.6)
        ax.set_yticks(range(len(chunk)))
        ax.set_yticklabels([f"{h['id']}  {clean(h['title'])[:42]}" for h in chunk], fontsize=7.5)
        ax.set_xticks(range(15)); ax.set_xticklabels([f"{c} {n}" for c, n in zip(cols, MN)], fontsize=7.5, rotation=60, ha="left")
        ax.xaxis.tick_top(); ax.tick_params(length=0); ax.grid(True, color=vs.GRID, lw=0.4)
        for s in ax.spines.values(): s.set_visible(False)
    for k, (lab, mk, sz, hol) in enumerate([("primary", "o", 60, False), ("secondary", "o", 20, False), ("rival", "D", 22, False), ("null", "s", 22, True), ("tool", "^", 24, True)]):
        fig.add_artist(Line2D([0.03 + 0.075 * k], [0.025], marker=mk, markersize=sz ** 0.5, color=vs.INK2, mfc="white" if hol else vs.INK2, transform=fig.transFigure, ls=""))
        fig.text(0.04 + 0.075 * k, 0.025, lab, fontsize=8.5, va="center")
    for k, (lab, c) in enumerate([("supported", OUT["supported"]), ("mixed", OUT["mixed"]), ("refuted", OUT["refuted"]), ("untested / n/a", "#cfcfcf")]):
        fig.patches.append(Rectangle((0.55 + 0.09 * k, 0.017), 0.011, 0.018, color=c, transform=fig.transFigure, figure=fig))
        fig.text(0.565 + 0.09 * k, 0.025, lab, fontsize=8.5, va="center")
    fig.subplots_adjust(left=0.215, right=0.99, top=0.80, bottom=0.07, wspace=1.05)
    fig.savefig(f"writeup/figures/matrix_slide_{page + 1}.pdf")
print(len(hs), "hypotheses")
