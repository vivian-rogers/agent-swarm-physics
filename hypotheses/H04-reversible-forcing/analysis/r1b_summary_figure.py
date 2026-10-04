"""H04 round-1b summary figures (plots existing round-1b results; no recomputation).

  uv run python hypotheses/H04-reversible-forcing/analysis/r1b_summary_figure.py

figures/r1b_summary_obs.pdf (page 1): (a) #51 nudge -> target kernel on the corrected design, aligned on the nudge (95%
  day-block band) and on the target's receiving call; (b) NE21 holdout n per hours segment (unchanged: C1 does not use
  activity_bins).
figures/r1b_summary_obs2.pdf (page 2): (a) #51 kernels by read-out delay bin; (b) NE43 Hawkes n per window.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from summary_figure import C1, C2, INK, INK2, FIGSIZE, plt, np  # noqa: E402
from h04lib import FIG, OUT, LAGS  # noqa: E402

R = OUT / "r1b"


def arr(x):
    return np.array([np.nan if v is None else v for v in x], float)


def main():
    d = json.loads((R / "G51.json").read_text())
    c = json.loads((OUT / "confirm_ne21_ne23.json").read_text())
    g, ra = d["G"]["nudge_target_all"], d["G"]["nudge_target_readout_aligned"]
    fig, ax = plt.subplots(1, 2, figsize=FIGSIZE, gridspec_kw={"width_ratios": [1.4, 1]})
    a = ax[0]
    m = (LAGS >= -10) & (LAGS <= 40)
    a.fill_between(LAGS[m], arr(g["G_lo"])[m], arr(g["G_hi"])[m], color=C2, alpha=0.18, lw=0)
    a.plot(LAGS[m], arr(g["G"])[m], color=C2, lw=0.8, label="from the nudge")
    a.plot(LAGS[m], arr(ra["G"])[m], color=C1, lw=0.8, label="from the receiving call")
    a.axhline(0, color=INK2, lw=0.7); a.axvline(0, color=INK, lw=0.7, ls=":")
    A30 = g["A30"]
    a.text(39, -0.11, f"A30 = {A30[0]:.2f} [{A30[1]:.2f}, {A30[2]:.2f}]", fontsize=4.9, color=INK, ha="right", va="bottom")
    a.set_xlim(-10, 40); a.set_ylim(-0.13, 0.42)
    a.set_xlabel("minutes"); a.set_ylabel(r"$G(\tau)$ = Δ P(active)")
    a.set_title(f"(a) #51 nudge → target ({g['n_cells']})", loc="left")
    a.legend(fontsize=4.6, frameon=False, loc="upper right")
    b = ax[1]
    segs = ["A1", "B1", "A2", "B2"]
    hrs = {"A1": 4, "B1": 8, "A2": 4, "B2": 8}
    x = np.arange(len(segs))
    for xi, s in zip(x, segs):
        n, lo, hi = c["segments"][s]["hawkes"]["n_ci"]
        b.errorbar(xi, n, yerr=[[n - lo], [hi - n]], fmt="o", color=C1 if hrs[s] == 4 else C2, ms=3.2, capsize=1.5, lw=0.8)
    nn = [c["segments"][s]["hawkes"]["n_ci"][0] for s in segs]
    b.plot(x, nn, color=INK2, lw=0.5, zorder=0)
    b.set_xticks(x); b.set_xticklabels([f"{s}\n{hrs[s]} h" for s in segs])
    b.set_ylim(0, 1.08); b.set_xlim(-0.5, 3.6)
    b.set_ylabel(r"branching ratio $n$")
    b.set_title("(b) NE21 holdout (C1)", loc="left")
    b.text(0.03, 0.985, "8 h higher at 3/3 switches\n(not affected by round 1b)", transform=b.transAxes, fontsize=4.9,
           color=INK, ha="left", va="top")
    b.grid(axis="x", visible=False)
    fig.tight_layout(pad=0.2, w_pad=0.6)
    fig.savefig(FIG / "r1b_summary_obs.pdf"); plt.close(fig)

    n43 = json.loads((R / "NE43.json").read_text())
    fig, ax = plt.subplots(1, 2, figsize=(3.4, 1.6), gridspec_kw={"width_ratios": [1.4, 1]})
    a = ax[0]
    cols = {"le1m": "#2a78d6", "1to3m": "#1baf7a", "3to10m": "#eda100", "gt10m": "#e34948"}
    lab = {"le1m": "read ≤ 1 min", "1to3m": "1–3 min", "3to10m": "3–10 min", "gt10m": "> 10 min"}
    m = (LAGS >= -5) & (LAGS <= 30)
    for k, v in d["by_readout"].items():
        if v.get("n_cells", 0) >= 20 and v.get("G"):
            a.plot(LAGS[m], np.cumsum(np.nan_to_num(arr(v["G"])[m]) * (LAGS[m] >= 1)), color=cols[k], lw=0.8,
                   label=f"{lab[k]} (n {v['n_cells']})")
    a.axhline(0, color=INK2, lw=0.6); a.axvline(0, color=INK, lw=0.6, ls=":")
    a.set_xlabel("minutes after the nudge"); a.set_ylabel("cumulative extra active min")
    a.set_title("(a) #51 by read-out delay", loc="left"); a.legend(fontsize=4.3, frameon=False, loc="lower left")
    b = ax[1]
    ws = ["pre", "on", "off"]
    for i, w in enumerate(ws):
        n, lo, hi = n43["windows"][w]["n_ci"]
        b.errorbar(i, n, yerr=[[n - lo], [hi - n]], fmt="o", color=[C1, C2, INK2][i], ms=3.2, capsize=1.5, lw=0.8)
    b.set_xticks(range(3)); b.set_xticklabels(["bookends\n+ nudges", "nudges\nonly", "neither"])
    b.set_ylim(0, 1.0); b.set_ylabel(r"Hawkes $n$")
    b.set_title("(b) NE43 (#51)", loc="left"); b.grid(axis="x", visible=False)
    fig.tight_layout(pad=0.2, w_pad=0.6)
    fig.savefig(FIG / "r1b_summary_obs2.pdf"); plt.close(fig)
    print("wrote r1b figures")


if __name__ == "__main__":
    main()
