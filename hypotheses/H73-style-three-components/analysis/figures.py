"""H73 summary figures (static PDFs for the RevTeX page).

figures/summary_obs.pdf   (a) per-period variance shares of the non-day systematic style variance: agent constant,
                          context, rest (agent-day jitter); (b) attribution gain from the context model per period
                          against the synthetic null and planted-drift ranges.
figures/summary_obsb.pdf  (a) NE41 forced-erasure projection beta and style percentile T_s: real vs synthetic
                          scenarios; (b) #12 judge shifts: leave-agent-out cosine per judge vs permutation null.
Palette: reference categorical slots 1-3 (blue, orange, aqua), validated in the dataviz reference palette.
"""
from __future__ import annotations
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import h73lib as L  # noqa: E402

BLUE, ORANGE, AQUA, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({"font.size": 7.5, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
                     "legend.frameon": False, "pdf.fonttype": 42})


def main():
    rep = json.loads((L.DATA / "replication" / "replication.json").read_text())
    nat = json.loads((L.DATA / "natives" / "natives.json").read_text())
    syn = json.loads((L.DATA / "synthetic" / "synthetic.json").read_text())
    keys = [k for k in rep if not k.startswith("_")]
    F3 = np.array([rep[k]["dec"]["F3"] for k in keys])
    uA = np.array([rep[k]["dec"]["u_A"] for k in keys])
    uC = np.array([max(rep[k]["dec"]["u_C"], 0) for k in keys])
    reg = [rep[k]["regime"] for k in keys]
    dc = np.array([rep[k]["att"]["5"]["gain_agent"] for k in keys])
    x = np.arange(len(keys))

    fig, ax = plt.subplots(2, 1, figsize=(4.0, 3.6), gridspec_kw={"height_ratios": [1.25, 1]})
    a = ax[0]
    a.bar(x, uA, width=0.72, color=BLUE, label="agent constant $u_A$", edgecolor="white", linewidth=0.6)
    a.bar(x, uC, width=0.72, bottom=uA, color=ORANGE, label="context $u_C$", edgecolor="white", linewidth=0.6)
    a.plot(x, F3, "o", ms=3.2, color=INK, label="$F_3$ (all three)", zorder=3)
    a.axhline(0.57, color=MUTED, lw=0.8, ls="--")
    a.text(len(keys) - 0.3, 0.57, " 0.57", ha="left", va="center", fontsize=6, color=MUTED, clip_on=False)
    a.set_ylim(0, 1.15)
    a.set_ylabel("share of non-day\nsystematic variance")
    a.set_xticks(x, [k[1:] for k in keys], fontsize=5.5, rotation=90)
    a.set_xlim(-0.6, len(keys) - 0.4)
    for i, r in enumerate(reg):
        if i and reg[i - 1] != r:
            a.axvline(i - 0.5, color=GRID, lw=0.8)
    a.text(0, 1.12, "(a)  regime I", fontsize=7, color=INK, va="top")
    a.text(reg.index("II") - 0.3, 1.1, "II", fontsize=7, color=INK, va="top")
    a.text(reg.index("III") - 0.3, 1.1, "III", fontsize=7, color=INK, va="top")
    a.legend(loc="lower left", ncol=3, fontsize=6.2, bbox_to_anchor=(0.0, 1.0), borderaxespad=0.1)
    b = ax[1]
    s0 = [syn[g]["S0"]["gain_agent"] for g in ("G12", "G18", "G38", "G41", "G51")]
    s1 = [syn[g]["S1"]["gain_agent"] for g in ("G12", "G18", "G38", "G41", "G51")]
    b.axhspan(min(s0), max(s0), color=GRID, lw=0, label="synthetic null (S0)")
    b.axhspan(min(s1), max(s1), color=AQUA, alpha=0.18, lw=0, label="synthetic drift (S1)")
    b.axhline(0, color=MUTED, lw=0.6)
    b.plot(x, dc, "o", ms=3.2, color=ORANGE, label=r"real $\Delta_c$")
    b.set_xticks(x, [k[1:] for k in keys], fontsize=5.5, rotation=90)
    b.set_xlim(-0.6, len(keys) - 0.4)
    b.set_ylabel("attribution gain\n(balanced acc.)")
    b.set_xlabel("goal period")
    b.text(-0.3, 0.095, "(b)", fontsize=7, color=INK, va="top")
    b.set_ylim(-0.09, 0.1)
    b.legend(loc="lower left", fontsize=5.8, ncol=3, bbox_to_anchor=(0.0, 1.0), borderaxespad=0.1)
    fig.tight_layout(h_pad=0.4)
    fig.savefig(L.HYP / "figures" / "summary_obs.pdf")
    plt.close(fig)

    fig, ax = plt.subplots(1, 2, figsize=(4.0, 2.0), gridspec_kw={"width_ratios": [1.3, 1]})
    a = ax[0]
    ne = syn["NE41"]
    labels = ["S0 null", "S1 drift", "S2 excursion", "real"]
    beta = [ne["S0"]["beta_mean"], ne["S1"]["beta_mean"], ne["S2"]["beta_mean"], nat["NE41"]["pooled"]["forced"]["beta"]]
    T = [ne["S0"]["T_raw"], ne["S1"]["T_raw"], ne["S2"]["T_raw"], nat["NE41"]["pooled"]["forced"]["T_raw"]["T"]]
    cols = [MUTED, AQUA, BLUE, ORANGE]
    for i in range(4):
        a.scatter(beta[i], T[i], s=26, color=cols[i], zorder=3, edgecolor="white", linewidth=0.8)
        a.annotate(labels[i], (beta[i], T[i]), xytext=(4, 3 if i in (1, 3) else -9), textcoords="offset points",
                   fontsize=6.3, color=INK)
    F = nat["NE41"]["pooled"]["forced"]
    a.hlines(F["T_raw"]["T"], F["lo"], F["hi"], color=ORANGE, lw=1.0, zorder=2)
    a.vlines(F["beta"], F["T_raw"]["lo"], F["T_raw"]["hi"], color=ORANGE, lw=1.0, zorder=2)
    a.axhline(0.5, color=GRID, lw=0.8); a.axvline(0, color=GRID, lw=0.8)
    a.set_xlabel(r"drift projection $\beta$")
    a.set_ylabel(r"erasure style percentile $T_s$")
    a.set_xlim(-0.15, 1.15); a.set_ylim(0.49, 0.61)
    a.text(-0.12, 0.605, "(a) NE41", fontsize=7, va="top")
    b = ax[1]
    g = nat["G12"]
    cs = g["cos"]
    b.bar(np.arange(len(cs)), cs, width=0.6, color=BLUE)
    b.axhline(0, color=MUTED, lw=0.6)
    b.set_xticks(np.arange(len(cs)), [f"J{i + 1}" for i in range(len(cs))])
    b.set_ylim(-0.3, 1.0)
    b.set_ylabel("cosine to other\njudges' mean shift")
    b.text(-0.4, 0.98, f"(b) #12 judges, p = {g['p_coh']:.3f}", fontsize=6.5, va="top")
    fig.tight_layout()
    fig.savefig(L.HYP / "figures" / "summary_obsb.pdf")
    plt.close(fig)
    print("figures written")


if __name__ == "__main__":
    main()
