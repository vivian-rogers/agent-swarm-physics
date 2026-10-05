"""Slide figure (16:9 PNG) for Motivation II: information dynamics and Kolchinsky-Wolpert value per bit."""
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch

plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
                     "mathtext.fontset": "dejavusans", "font.size": 15, "axes.spines.top": False, "axes.spines.right": False})
INK, INK2, MUTED = "#1a1a1a", "#555555", "#9a9a9a"
BLUE, GREEN, GRAY = "#2f6db5", "#0ca30c", "#b5b5b5"

fig = plt.figure(figsize=(13.33, 7.5), dpi=200)
fig.patch.set_facecolor("white")

# ---------- left: storage, transfer, synergy
ax = fig.add_axes([0.03, 0.10, 0.47, 0.78]); ax.set_xlim(0, 12); ax.set_ylim(0, 9); ax.set_aspect("equal"); ax.axis("off")
fig.text(0.04, 0.92, "Where is information kept and moved?", fontsize=20, weight="bold", color=INK)

def agent(x, y, lab, c=BLUE, r=0.62):
    ax.add_patch(Circle((x, y), r, fc=c, ec="white", lw=2.5, zorder=3))
    ax.text(x, y, lab, color="white", ha="center", va="center", fontsize=17, weight="bold", zorder=4)

def arrow(p, q, rad=0.0, lw=2.6, ms=20):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=ms, color=INK2, lw=lw,
                                 connectionstyle=f"arc3,rad={rad}", zorder=2))

y0 = 6.0
# storage
agent(1.6, y0, "X"); arrow((1.15, y0 + 0.5), (2.05, y0 + 0.5), rad=-2.3, lw=2.4, ms=18)
ax.text(1.6, 3.95, "Storage", ha="center", fontsize=17, weight="bold", color=INK)
ax.text(1.6, 3.4, "its own past\npredicts its next state", ha="center", va="top", fontsize=13, color=INK2)
# transfer
agent(4.75, y0, "Y"); agent(6.85, y0, "X"); arrow((5.42, y0), (6.18, y0), lw=3.2)
ax.text(5.8, 3.95, "Transfer", ha="center", fontsize=17, weight="bold", color=INK)
ax.text(5.8, 3.4, "another agent adds\nwhat X's past cannot", ha="center", va="top", fontsize=13, color=INK2)
# synergy
agent(9.35, y0 + 0.72, "S₁", r=0.55); agent(9.35, y0 - 0.72, "S₂", r=0.55); agent(11.0, y0, "T", c=GREEN)
arrow((9.9, y0 + 0.5), (10.42, y0 + 0.22)); arrow((9.9, y0 - 0.5), (10.42, y0 - 0.22))
ax.text(10.15, 3.95, "Synergy", ha="center", fontsize=17, weight="bold", color=INK)
ax.text(10.15, 3.4, "only the joint state\nholds the information", ha="center", va="top", fontsize=13, color=INK2)
# egregore test box
ax.add_patch(FancyBboxPatch((0.3, 0.25), 11.4, 1.75, boxstyle="round,pad=0.12,rounding_size=0.25", fc="#f3f3f3", ec="#d8d8d8", lw=1.2))
ax.text(0.65, 1.55, r"Egregore test:  $\Psi>0$?", fontsize=15, weight="bold", color=INK, va="center")
ax.text(0.65, 0.78, r"Does the whole swarm predict its future better than its parts?",
        fontsize=13.5, color=INK2, va="center")

# ---------- right: value per bit (horizontal bars)
bx = fig.add_axes([0.62, 0.17, 0.35, 0.62])
fig.text(0.58, 0.92, "What is one bit worth?", fontsize=20, weight="bold", color=INK)
fig.text(0.58, 0.865, "Scramble one channel; Kolchinsky–Wolpert value per bit  " + r"$\kappa=\Delta V/I$", fontsize=13.5, color=INK2)
ch = ["context window", "own artifacts", "memory notes", "chat reads", "history search"]
kap = [5.2, -0.6, None, None, None]; lo = [3.8, -1.6, None, None, None]; hi = [7.9, 0.3, None, None, None]
ys = list(range(len(ch)))[::-1]
for y, k, l, h in zip(ys, kap, lo, hi):
    if k is None:
        bx.plot([0], [y], marker="o", ms=9, mfc="white", mec=GRAY, mew=2, zorder=3)
        bx.text(0.35, y, "too little information to measure", va="center", fontsize=12.5, color=MUTED)
        continue
    c = GREEN if l > 0 else GRAY
    bx.barh(y, k, height=0.55, color=c, zorder=3)
    bx.errorbar(k, y, xerr=[[k - l], [h - k]], color=INK, capsize=6, lw=1.8, zorder=4)
bx.axvline(0, color=INK2, lw=1.2)
bx.set_yticks(ys); bx.set_yticklabels(ch, fontsize=15)
bx.tick_params(axis="y", length=0); bx.spines["left"].set_visible(False)
bx.set_xlim(-2.2, 8.6); bx.set_xlabel("commits per 20 calls per bit", fontsize=14, color=INK2)
bx.grid(axis="x", color="#ececec", lw=0.8); bx.set_axisbelow(True)
bx.text(0.25, ys[0] - 0.5, "forced wipe: −40% output for ≈10 calls", va="center", fontsize=12.5, style="italic", color=INK2)

fig.savefig("writeup/figures/slide_motivation2.png", dpi=200, facecolor="white")
fig.savefig("writeup/figures/slide_motivation2.pdf", facecolor="white")
print("ok")
