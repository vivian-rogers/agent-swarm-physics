"""H87 summary figures (static PDFs for the RevTeX page).

figures/summary_obs.pdf   the kappa table (NE41 call scale + NE34 kickoff + G37 search own scramble):
                          (a) information I_c (bits) per channel; (b) value dV_c (commits per 20 calls) per channel.
figures/summary_obsb.pdf  (a) per-period replication: the context cost share and kappa_C per period;
                          (b) synthetic: recovered vs planted dV_rel for rows A, M, G in worlds W1 and W0.
Palette: reference categorical slots 1-3 (blue, orange, aqua), validated in the dataviz reference palette.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h87lib as L  # noqa: E402

BLUE, ORANGE, AQUA, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({"font.size": 7.5, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
                     "legend.frameon": False, "pdf.fonttype": 42})
FIG = L.ROOT / "hypotheses/H87-kappa-channel-table/figures"
LAB = {"C": "context", "A": "own artifact", "M": "memory note", "G": "chat reads", "Q": "search", "K": "kickoff"}


def err(ax, y, est, c, col, marker="o"):
    if est is None or not np.isfinite(est):
        return
    lo, hi = (c if c and c[0] is not None else (est, est))
    ax.errorbar(est, y, xerr=[[est - lo], [hi - est]], fmt=marker, color=col, ms=4, lw=1.1, capsize=0)


def main():
    res = json.loads((L.DATA / "results/results.json").read_text())
    syn = json.loads((L.DATA / "synthetic/synthetic.json").read_text())
    FIG.mkdir(parents=True, exist_ok=True)
    rows = res["NE41"]["rows"]
    K = res["NE34_K"]
    Q = res["G37_Q"]
    order = ["C", "A", "M", "G", "Q", "K"]
    fig, ax = plt.subplots(1, 2, figsize=(4.2, 2.1), sharey=True)
    for i, c in enumerate(order):
        y = len(order) - 1 - i
        if c == "K":
            err(ax[0], y, K["I"], K["I_ci"], AQUA, "s")
            err(ax[1], y, K["dV"], K["dV_ci"], AQUA, "s")
            continue
        r = rows[c]
        col = ORANGE if c == "C" else BLUE
        err(ax[0], y, r["I"], r["I_ci"], col)
        err(ax[1], y, r["dV"], r["dV_ci"], col)
        if c == "Q":
            err(ax[1], y - 0.3, Q["dV"], Q["dV_ci"], MUTED, "D")
        k = r["kappa"] if res["NE41"]["identified"][c] else None
        txt = f"κ {k:.1f}" if k is not None and np.isfinite(k) else "κ n.i."
        ax[1].text(1.02, y, txt, transform=ax[1].get_yaxis_transform(), fontsize=6.3, color=INK, va="center")
    kk = K["kappa"]
    ax[1].text(1.02, 0, f"κ {kk:.1f}" if np.isfinite(kk) and K["I_ci"][0] and K["I_ci"][0] > L.MIN_I else "κ n.i.",
               transform=ax[1].get_yaxis_transform(), fontsize=6.3, color=INK, va="center")
    for a in ax:
        a.axvline(0, color=MUTED, lw=0.6)
    ax[0].set_yticks(range(len(order)), [LAB[c] for c in reversed(order)])
    ax[0].set_xlabel("$I_c$ (bits)")
    ax[1].set_xlabel(r"$\Delta V_c$ (commits / 20 calls)")
    ax[0].set_title("(a) information", fontsize=7.5, loc="left")
    ax[1].set_title("(b) value", fontsize=7.5, loc="left")
    fig.tight_layout(pad=0.4, rect=(0, 0, 0.92, 1))
    fig.savefig(FIG / "summary_obs.pdf")
    plt.close(fig)

    fig, ax = plt.subplots(1, 2, figsize=(4.2, 1.85))
    a = ax[0]
    rep = res["replication"]
    ps = list(rep)
    for i, p in enumerate(ps):
        r = rep[p]["rows"]
        err(a, i, r["C"]["dV_rel"], r["C"]["dV_rel_ci"], ORANGE)
        err(a, i + 0.25, r["A"]["dV_rel"], r["A"]["dV_rel_ci"], BLUE)
    a.axvline(0, color=MUTED, lw=0.6)
    a.set_yticks(range(len(ps)), ps)
    a.set_xlabel(r"$\Delta V_{\rm rel}$")
    a.set_xlim(-1.0, 2.6)
    a.plot([], [], "o", color=ORANGE, label="context")
    a.plot([], [], "o", color=BLUE, label="artifact")
    a.legend(fontsize=5.4, loc="upper right", handletextpad=0.1, borderaxespad=0.1, markerscale=0.7)
    a.set_title("(a) per period", fontsize=7.5, loc="left")
    a = ax[1]
    for j, (w, col) in enumerate((("W1", BLUE), ("W0", MUTED))):
        s = syn["worlds"][w]["summary"]
        for i, c in enumerate(("A", "M", "G")):
            a.scatter(s[c]["truth_rel"], s[c]["mean_rel"], color=col, s=18, marker="os^"[i],
                      label=f"{w} {c}" if True else None, zorder=3)
    a.plot([-0.05, 0.6], [-0.05, 0.6], color=MUTED, lw=0.6, ls="--")
    a.set_xlabel(r"planted $\Delta V_{\rm rel}$")
    a.set_ylabel("recovered (mean)")
    a.legend(fontsize=5.4, loc="upper left", ncol=2, handletextpad=0.1, columnspacing=0.5)
    a.set_title("(b) synthetic", fontsize=7.5, loc="left")
    fig.tight_layout(pad=0.4)
    fig.savefig(FIG / "summary_obsb.pdf")
    plt.close(fig)


if __name__ == "__main__":
    main()
