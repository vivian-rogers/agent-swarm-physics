"""H16 round 2 summary figure -> figures/r2_summary.pdf (also used by the 2-page summary)."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
D = ROOT / "data/processed/H16-metastable-traps-kramers/r2"
FIG = ROOT / "hypotheses/H16-metastable-traps-kramers/figures/r2_summary.pdf"
OBS, PRED, NULL, GREY = "#1f4e79", "#c05a28", "#8a8a8a", "#bbbbbb"


def main():
    res = json.loads((D / "results_r2.json").read_text())
    ph = json.loads((D / "posthoc_r2.json").read_text())
    g = res["gates"]["G51"]
    t = res["ts1r"]
    fig, ax = plt.subplots(2, 2, figsize=(7.2, 5.6))
    # (a) gate aging: observed vs urn-predicted, per ruler
    a = ax[0, 0]
    names = ["f_tok", "f_call", "f_entry", "f_rec"]
    lab = ["U-tok", "U-call", "U-entry", "U-rec"]
    x = np.arange(len(names))
    bo = g["stats"]["beta_a0"]
    a.axhspan(bo["ci"][0], bo["ci"][1], color=OBS, alpha=0.15, lw=0)
    a.axhline(bo["est"], color=OBS, lw=1.5, label="observed (G51 gates)")
    for i, n in enumerate(names):
        u = g["urn_vs_obs"][n]
        a.errorbar(i, u["beta_pred"], yerr=[[u["beta_pred"] - u["band"][0]], [u["band"][1] - u["beta_pred"]]], fmt="o", color=PRED, capsize=3,
                   label="urn prediction" if i == 0 else None)
    a.set_xticks(x, lab)
    a.axhline(0, color=GREY, lw=0.8)
    a.set_ylabel("aging slope (per ln trap age)")
    a.set_title("(a) urn exponent from composition", fontsize=9, loc="left")
    a.legend(fontsize=7, frameon=False, loc="lower left")
    # (b) escape after a forced reset vs no reset, by gate index
    b = ax[0, 1]
    r = ph["P5_reset_by_k"]["rates"]
    ks = ["k1", "k2_4", "k5p"]
    xl = ["1", "2–4", "≥5"]
    b.plot(range(3), [r[k]["noreset"] for k in ks], "o-", color=OBS, label="no reset")
    b.plot(range(3), [r[k]["forced"] for k in ks], "s-", color=PRED, label="first gate after a forced reset")
    b.set_xticks(range(3), xl)
    b.set_xlabel("gate index k in the trap")
    b.set_ylabel("P(sustained escape)")
    b.set_ylim(0, 1)
    b.set_title("(b) a forced erasure ends most traps", fontsize=9, loc="left")
    b.legend(fontsize=7, frameon=False, loc="lower left")
    # (c) TS1r deep slope within kinds, with the mixture null
    c = ax[1, 0]
    rows = []
    for per in ("G51", "G38"):
        o = t[per]
        rows += [(f"{per} pooled", o["pooled"]), (f"{per} pause", o["by_kind"]["pause"]), (f"{per} within cell", o["within_cell"])]
    for i, (nm, o) in enumerate(rows):
        c.errorbar(o["beta"], i, xerr=[[o["beta"] - o["ci"][0]], [o["ci"][1] - o["beta"]]], fmt="o", color=OBS, capsize=3)
    for per, i0 in (("G51", 0), ("G38", 3)):
        q = t[per]["mixture_null"]["q"]
        c.fill_betweenx([i0 - 0.4, i0 + 0.4], q[0], q[1], color=NULL, alpha=0.4, lw=0, label="pure-mixture null" if per == "G51" else None)
        qd = t[per]["mixture_null_day"]["q"]
        c.fill_betweenx([i0 - 0.4, i0 + 0.4], qd[0], qd[1], color=PRED, alpha=0.25, lw=0, label="day-cell null (post hoc)" if per == "G51" else None)
    c.set_yticks(range(len(rows)), [r_[0] for r_ in rows], fontsize=7)
    c.axvline(0, color=GREY, lw=0.8)
    c.axvspan(-0.3, 0.3, color=GREY, alpha=0.15, lw=0)
    c.set_xlabel("deep TS1r slope (per ln elapsed)")
    c.set_title("(c) aging within spell kinds", fontsize=9, loc="left")
    c.legend(fontsize=6.5, frameon=False, loc="upper left", bbox_to_anchor=(0.0, 0.62))
    # (d) kicks: observed vs urn-implied
    d = ax[1, 1]
    st = g["stats"]
    obs = [st["kick.dir"]["est"], st["kick.undir"]["est"]]
    err = [[st["kick.dir"]["est"] - st["kick.dir"]["ci"][0], st["kick.undir"]["est"] - st["kick.undir"]["ci"][0]],
           [st["kick.dir"]["ci"][1] - st["kick.dir"]["est"], st["kick.undir"]["ci"][1] - st["kick.undir"]["est"]]]
    urn = [ph["P3_urn_implied"]["kick.dir"]["mean"], ph["P3_urn_implied"]["kick.undir"]["mean"]]
    d.bar(np.arange(2) - 0.18, obs, 0.34, yerr=err, color=OBS, label="observed", capsize=3)
    d.bar(np.arange(2) + 0.18, urn, 0.34, color=PRED, label="urn-implied")
    d.set_xticks(range(2), ["directed read", "undirected only"])
    d.set_ylabel("log OR of sustained escape at the gate")
    d.axhline(0, color=GREY, lw=0.8)
    d.set_title("(d) a message works by address, not dilution", fontsize=9, loc="left")
    d.legend(fontsize=7, frameon=False)
    for axx in ax.flat:
        axx.tick_params(labelsize=7)
        for s in ("top", "right"):
            axx.spines[s].set_visible(False)
    fig.tight_layout()
    FIG.parent.mkdir(exist_ok=True)
    fig.savefig(FIG)
    print("wrote", FIG)


if __name__ == "__main__":
    main()
