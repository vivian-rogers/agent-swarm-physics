"""H72 round 2 figure: figures/r2_summary.pdf.
(a) G51: held-out gain of each mechanism and the share of the aging clocks' information it explains (eps), with the
    proxy band from the synthetic worlds; (b) chatter-hold slope beta_C per period (full model); (c) transfer of G51's
    slopes to the other regime-III periods. Reads r2/results_r2.json and r2/synthetic/main.json only.
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
import r2lib as R  # noqa: E402

FIG = Path(__file__).resolve().parents[1] / "figures"
COL = {"S": "#2a78d6", "C": "#d0632b", "F": "#1a9e77", "A": "#7f7f7f"}
NAME = {"S": "starvation", "C": "chatter", "F": "self-share", "A": "clocks"}
INK, MUTED = "#222222", "#888888"


def main():
    d = json.loads((R.R2 / "results_r2.json").read_text())
    cv = d["reconcile"]["G51"]["cv"]
    fig, ax = plt.subplots(1, 3, figsize=(7.4, 2.8), gridspec_kw={"width_ratios": [1.0, 1.3, 1.0]})
    # (a) eps per mechanism
    a = ax[0]
    ms = ["S", "C", "F"]
    for i, m in enumerate(ms):
        e, lo, hi = cv[f"eps_{m}"]
        a.errorbar(i, e, yerr=[[e - lo], [hi - e]], fmt="o", color=COL[m], ms=6, lw=1.5, capsize=0)
        g = cv[f"gain_{m}"][0]
        a.text(i, hi + 0.05, f"G {g:+.1f}", ha="center", va="bottom", fontsize=7, color=INK)
    a.axhspan(-0.05, 0.22, color="#dddddd", zorder=0)
    a.text(2.45, 0.11, "proxy\nworlds", fontsize=6.5, color=MUTED, ha="right", va="center")
    a.axhline(0, color=MUTED, lw=0.6)
    a.set_xticks(range(3), [NAME[m] for m in ms], fontsize=7.5)
    a.set_ylim(-0.1, 0.9)
    a.set_ylabel(r"aging share explained $\varepsilon$ (held out)", fontsize=7.5)
    a.set_title("(a) G51: what carries aging", fontsize=8, loc="left")
    # (b) beta_C per period
    b = ax[1]
    rows = [(g, r) for g, r in d["r1"].items() if "bC_full" in r]
    for i, (g, r) in enumerate(rows):
        e = r["bC_full"]["est"]; lo, hi = r["bC_full"]["ci"]
        col = INK if g == "G51" else MUTED
        b.errorbar(i, np.clip(e, -1.5, 1.5), yerr=[[np.clip(e - lo, 0, 2)], [np.clip(hi - e, 0, 2)]], fmt="o",
                   color=col, ms=3.5 if g != "G51" else 5, lw=1.0, capsize=0)
    b.axhline(0, color=MUTED, lw=0.6)
    b.set_xticks(range(len(rows)), [g[1:] for g, _ in rows], fontsize=6, rotation=90)
    b.set_ylim(-1.6, 1.6)
    b.set_ylabel(r"$\beta_C$ per ln(1 + undirected items)", fontsize=7.5)
    b.set_title("(b) chatter hold by period (full model)", fontsize=8, loc="left")
    b.text(len(rows) - 1, -0.45, "G51\n−0.09", fontsize=6.5, ha="center", va="top", color=INK)
    # (c) transfer
    c = ax[2]
    tg = ["G37", "G38", "G40", "G41", "G44"]
    for j, m in enumerate(["S", "C", "F"]):
        for i, t in enumerate(tg):
            e, lo, hi = d["transfer"][t][m]
            c.errorbar(i + (j - 1) * 0.22, np.clip(e, -30, 60), yerr=[[np.clip(e - lo, 0, 90)], [np.clip(hi - e, 0, 90)]],
                       fmt="o", color=COL[m], ms=3.5, lw=1.0, capsize=0, label=NAME[m] if i == 0 else None)
    c.axhline(0, color=MUTED, lw=0.6)
    c.set_xticks(range(len(tg)), tg, fontsize=7)
    c.set_ylim(-30, 60)
    c.set_ylabel("held-out gain, G51 slopes (nats / 1,000)", fontsize=7.5)
    c.set_title("(c) transfer from G51", fontsize=8, loc="left")
    c.legend(fontsize=6.5, frameon=False, loc="upper right")
    for x in ax:
        x.tick_params(labelsize=7)
        for s in ("top", "right"):
            x.spines[s].set_visible(False)
    fig.tight_layout()
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / "r2_summary.pdf")
    fig.savefig(R.R2 / "r2_summary.png", dpi=110)
    print("written", FIG / "r2_summary.pdf")


if __name__ == "__main__":
    main()
