"""H96 visuals: a goal switch is a quench, not a hysteresis loop.

fig.pdf/png  (a) illustration in the shared content plane (bge white32, #38 -> #39): each agent's old-state coordinate
             before and after an ordinary night and before and after the kickoff; (b) H96's field-orthogonal old-state
             remanence M(t)/M_pre against active hours since the kickoff (24 transitions, bge style_resid32) with the
             ordinary-night band; (c) day-1 persistence R1 per transition (bge filled, gte open, 90% CIs) against the
             ordinary-night reference (146 pseudo-switches, 10-90% band and median, by regime).

Inputs (read-only): data/processed/H96-goal-switch-hysteresis/results/{card.json, transitions_*_style_resid32.json};
H97's design T39 via writeup/visuals/_quench_common.py (panel a only).
Usage: uv run python writeup/visuals/H96-goal-switch-hysteresis/make.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VIS = HERE.parent
ROOT = VIS.parents[1]
sys.path.insert(0, str(VIS))

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import vstyle as vs  # noqa: E402
import _quench_common as qc  # noqa: E402

D = ROOT / "data/processed/H96-goal-switch-hysteresis/results"
BINS = [0, 0.5, 1, 2, 4, 8, 16, 32]   # h96lib.BINS (active hours since t0)
YCLIP = (-1.6, 2.2)


def load(model):
    return json.load(open(D / f"transitions_{model}_style_resid32.json"))


def panel_slope(ax):
    T = qc.load_transition("T39")
    m2 = qc.seg_means(T, qc.day_mask(T, -2)); m1 = qc.seg_means(T, qc.day_mask(T, -1))
    d1 = qc.seg_means(T, pl.col("seg") == "day1")
    xs = [0, 1, 2]
    for a in sorted(set(m2) & set(m1)):
        ax.plot(xs[:2], [m2[a][1], m1[a][1]], color=vs.NULL, lw=0.8, marker="o", ms=2.2, zorder=2)
    for a in sorted(set(m1) & set(d1)):
        ax.plot(xs[1:], [m1[a][1], d1[a][1]], color=vs.FIELD, lw=0.8, marker="o", ms=2.2, alpha=0.9, zorder=2)
    mm = [np.mean([v[1] for v in m.values()]) for m in (m2, m1, d1)]
    ax.plot(xs, mm, color=vs.INK, lw=1.6, marker="D", ms=4, zorder=3)
    r_n = mm[1] / mm[0]; r_k = mm[2] / mm[1]
    ax.text(0.5, 0.03, f"night\n×{r_n:.2f}", ha="center", fontsize=6.3, color=vs.INK2, transform=ax.get_xaxis_transform())
    ax.text(1.5, 0.03, f"kickoff\n×{r_k:.2f}", ha="center", fontsize=6.3, color=vs.FIELD,
            transform=ax.get_xaxis_transform())
    ax.axhline(0, color=vs.INK2, lw=0.5)
    ax.set_xticks(xs); ax.set_xticklabels(["#38\nday −2", "#38\nlast day", "#39\nday 1"], fontsize=6.3)
    ax.set_xlim(-0.25, 2.25)
    ax.set_ylabel(r"old-state coordinate $\langle z,\hat e_{38}\rangle$")
    ax.grid(axis="x", visible=False)
    ax.set_title("(a) one switch", loc="left")
    return r_n, r_k


def panel_time(ax, tb, ref):
    hc = np.sqrt(np.array(BINS[:-1]) * np.array(BINS[1:])); hc[0] = 0.25
    xpre = 0.08
    curves = []
    for t in tb:
        s = t["state"]
        mpre = s["M_pre"]["est"]
        if not (np.isfinite(mpre) and s["M_pre"]["lo"] > 0):
            continue
        ser = np.array([np.nan if v is None else v for v in s["M_series"]], float)
        y = np.r_[1.0, ser[2:] / mpre]
        curves.append(y)
        ax.plot(np.r_[xpre, hc], y, color=vs.MUTED, lw=0.4, alpha=0.45, zorder=1)
    C = np.array(curves)
    med = np.nanmedian(C, 0)
    q1, q3 = np.nanpercentile(C, [25, 75], axis=0)
    xx = np.r_[xpre, hc]
    ax.fill_between(xx, q1, q3, color=vs.FIELD, alpha=0.18, lw=0)
    ax.plot(xx, med, color=vs.FIELD, lw=1.6, marker="o", ms=3, mec=vs.INK, mew=0.4, zorder=3,
            label=f"switch, median of {len(C)} (IQR)")
    r = ref["I"]
    ax.axhspan(r["p10"], r["p90"], color=vs.NULL, alpha=0.35, lw=0, label="ordinary night, day 1 (10–90%)")
    ax.axhline(r["median"], color=vs.MUTED, lw=0.9, ls="--")
    ax.axhline(0, color=vs.INK2, lw=0.5)
    ax.set_xscale("log")
    ax.set_xticks([xpre, 0.25, 1, 4, 16]); ax.set_xticklabels(["pre", "0.25", "1", "4", "16"])
    ax.set_xlim(0.06, 30)
    ax.set_ylim(-0.9, 1.6)
    ax.set_xlabel("active hours since the kickoff")
    ax.set_ylabel(r"old-state remanence $M(t)/M_{\rm pre}$")
    ax.legend(loc="upper right", fontsize=5.8, borderaxespad=0.2)
    ax.set_title("(b) gone in the first hour", loc="left")
    return len(C)


def panel_r1(ax, tb, tg, card):
    P = [t["P"] for t in tb]
    reg = {t["P"]: t["regime"] for t in tb}
    gmap = {t["P"]: t for t in tg}
    x = np.arange(len(P))
    refs = card["bge_small_style_resid32"]["pseudo_reference"]
    for rg in ("I", "III"):
        ix = [i for i, p in enumerate(P) if reg[p] == rg]
        if not ix:
            continue
        r = refs[rg]
        ax.fill_between([min(ix) - 0.45, max(ix) + 0.45], r["p10"], r["p90"], color=vs.NULL, alpha=0.35, lw=0)
        ax.plot([min(ix) - 0.45, max(ix) + 0.45], [r["median"]] * 2, color=vs.MUTED, lw=0.9, ls="--")
        ax.text((min(ix) + max(ix)) / 2, r["p90"] + 0.06, f"ordinary nights ({rg})", ha="center", fontsize=5.8,
                color=vs.INK2)
    for off, src, filled in ((-0.17, tb, True), (0.17, [gmap.get(p) for p in P], False)):
        for i, t in enumerate(src):
            if t is None:
                continue
            r = t["state"]["R1"]
            e, lo, hi = r["est"], r["lo"], r["hi"]
            if not np.isfinite(e):
                continue
            ec, lc, hc_ = np.clip([e, lo, hi], *YCLIP)
            ax.plot([i + off] * 2, [lc, hc_], color=vs.FIELD if filled else vs.INK2, lw=0.8, zorder=2)
            ax.scatter([i + off], [ec], s=12, zorder=3, color=vs.FIELD if filled else "white",
                       edgecolor=vs.INK, lw=0.5, marker="o" if filled else "s")
            if e > YCLIP[1] or e < YCLIP[0]:
                ax.annotate("", (i + off, ec), xytext=(i + off, ec - 0.25 * np.sign(e)),
                            arrowprops=dict(arrowstyle="-|>", lw=0.6, color=vs.INK2, mutation_scale=5))
    ax.scatter([], [], s=12, color=vs.FIELD, edgecolor=vs.INK, lw=0.5, label="bge")
    ax.scatter([], [], s=12, color="white", edgecolor=vs.INK, lw=0.5, marker="s", label="gte")
    ax.axhline(0, color=vs.INK2, lw=0.5)
    ax.set_ylim(*YCLIP)
    ax.set_xticks(x[::2]); ax.set_xticklabels([f"#{p}" for p in P[::2]], fontsize=6)
    ax.set_xlim(-0.8, len(P) - 0.2)
    ax.set_xlabel(r"new goal period P (transition P$-$1 $\rightarrow$ P)")
    ax.set_ylabel(r"day-1 persistence $R_1$")
    ax.legend(loc="upper left", fontsize=5.8, borderaxespad=0.2, ncol=2, handletextpad=0.2, columnspacing=0.8)
    ax.grid(axis="x", visible=False)
    ax.set_title("(c) every transition vs an ordinary night", loc="left")


def main():
    vs.use()
    card = json.load(open(D / "card.json"))
    tb, tg = load("bge_small"), load("gte_modernbert")
    fig = plt.figure(figsize=(vs.W["double"], 2.5))
    gs = fig.add_gridspec(1, 3, width_ratios=[0.62, 0.95, 1.6], wspace=0.45)
    a0, a1, a2 = (fig.add_subplot(gs[0, i]) for i in range(3))
    r_n, r_k = panel_slope(a0)
    n = panel_time(a1, tb, card["bge_small_style_resid32"]["pseudo_reference"])
    panel_r1(a2, tb, tg, card)
    vs.save(fig, HERE / "fig")
    plt.close(fig)
    R1b = np.nanmedian([t["state"]["R1"]["est"] for t in tb]); R1g = np.nanmedian([t["state"]["R1"]["est"] for t in tg])
    print(f"illustration ratios night {r_n:.2f} kickoff {r_k:.2f}; time-course curves {n}")
    print(f"R1 median bge {R1b:.2f} gte {R1g:.2f}")
    print({k: card[k]["dR1_RE"] for k in card if "dR1_RE" in card[k]})


if __name__ == "__main__":
    main()
