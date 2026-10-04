"""Credence vs value for every v2-scored claim (writeup/figures/scoring_scatter.pdf)."""
import json, glob, sys
import numpy as np
sys.path.insert(0, "writeup/visuals"); import vstyle as vs
import matplotlib.pyplot as plt
vs.use()
rows = []
for f in sorted(glob.glob("hypotheses/H*/summary/meta.json")):
    v = json.load(open(f)).get("v2")
    if v: rows.append((f.split("/")[1].split("-")[0], v["credence"], v["value_if_true"], v.get("mechanism_level", "M0"), v.get("fragile", False)))
fig, ax = plt.subplots(figsize=(4.6, 3.3))
V = np.linspace(0.05, 3.95, 200)
for eu in (0.5, 1.0, 1.5, 2.0, 2.5):
    p = eu / V; m = p <= 1
    ax.plot(V[m], p[m], color=vs.GRID, lw=0.8, zorder=0)
    ax.text(3.97, eu / 3.95, f"EU {eu:g}", fontsize=6, color=vs.MUTED, va="center")
style = {"M0": (vs.C["sky"], "o"), "M1": (vs.C["blue"], "s"), "M2": (vs.C["red"], "D")}
rng = np.random.default_rng(0)
for lvl, (c, mk) in style.items():
    pts = [r for r in rows if r[3] == lvl]
    x = np.array([r[2] for r in pts]) + rng.uniform(-0.06, 0.06, len(pts))
    y = np.array([r[1] for r in pts])
    fr = np.array([r[4] for r in pts])
    ax.scatter(x[~fr], y[~fr], s=16, color=c, marker=mk, edgecolor="white", lw=0.4, label=f"{lvl} ({len(pts)})", zorder=3)
    if fr.any(): ax.scatter(x[fr], y[fr], s=16, facecolor="white", edgecolor=c, marker=mk, lw=0.9, zorder=3)
POS = {"H02": (2.2, 1.0), "H54": (2.62, 1.0), "H08": (3.02, 1.0), "H38": (3.42, 1.0), "H44": (4.25, 0.92),
       "H50": (4.25, 0.84), "H15": (4.25, 0.77), "H40": (4.25, 0.70), "H46": (3.1, 0.82), "H69": (2.45, 0.90)}
for h, p, v, *_ in rows:
    if h in POS:
        ax.annotate(h, (v, p), xytext=POS[h], textcoords="data", fontsize=6, color=vs.INK2, ha="center", va="center",
                    arrowprops=dict(arrowstyle="-", color=vs.MUTED, lw=0.5, shrinkA=1, shrinkB=3))
ax.axhline(0.95, color=vs.NULL, lw=0.8, ls="--"); ax.text(0.08, 0.94, "credence cap (0.95)", fontsize=6, color=vs.MUTED, va="top")
ax.set_xlim(0, 4.45); ax.set_ylim(0, 1.04); ax.set_xticks([0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5])
ax.set_xlabel("value if true, $V$"); ax.set_ylabel("credence $p$")
ax.scatter([], [], s=16, facecolor="white", edgecolor=vs.INK2, label="fragile (open marker)")
ax.legend(loc="lower right", fontsize=6.5, handletextpad=0.3)
ax.set_title(f"{len(rows)} scored claims (median $p$ = {np.median([r[1] for r in rows]):.2f})", fontsize=8)
vs.save(fig, "writeup/figures/scoring_scatter")
print(len(rows))
