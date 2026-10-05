"""H13 round 2 figures: figures/r2_obs.pdf (style ladder; read-out family contrast) and figures/r2_obsb.pdf
(newcomer lab alignment and room outsiderness by day; read-out pull by receiver lab).

Usage: uv run python hypotheses/H13-family-fields/analysis/r2_figures.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
R2 = ROOT / "data/processed/H13-family-fields/r2"
FIG = HERE.parent / "figures"
BLUE, ORANGE, AQUA, VIOLET = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7"
INK, INK2, GRID, NULL = "#0b0b0b", "#52514e", "#e4e3df", "#9b9a95"
plt.rcParams.update({"font.size": 7, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
                     "grid.linewidth": 0.5, "legend.frameon": False, "pdf.fonttype": 42, "axes.titlesize": 7.5})


def fig1():
    lad = json.loads((R2 / "ladder.json").read_text())["summary"]
    syn = json.loads((R2 / "synthetic_A.json").read_text())["worlds"]["S0"]
    ro = json.loads((R2 / "readout.json").read_text())["pooled"]
    ph = json.loads((R2 / "posthoc.json").read_text())["PH1"]
    lv = ["L0", "W1", "W2", "W3", "Wf", "S-a'", "P1", "P2", "P3", "S-a", "PG"]
    lab = ["raw", "W core", "W +S20", "W +FW", "W FW", "S-a′", "P core", "P +S20", "P +FW", "S-a", "P genre"]
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.8, 2.2), gridspec_kw={"width_ratios": [1.55, 1]})
    x = np.arange(len(lv))
    for k, (m, col, mk) in enumerate((("bge", BLUE, "o"), ("gte", ORANGE, "s"))):
        S = lad[m]
        mu = np.array([S[l]["mu"] for l in lv]); lo = np.array([S[l]["lo"] for l in lv]); hi = np.array([S[l]["hi"] for l in lv])
        off = (k - 0.5) * 0.24
        a.errorbar(x + off, mu, yerr=[mu - lo, hi - mu], fmt=mk, ms=3.5, color=col, lw=0.9, capsize=0, label=m)
    a.scatter(x, [syn[l]["re_mu_mean"] for l in lv], marker="_", s=90, color=INK2, lw=1.4, zorder=4,
              label="style-only synthetic (S0)")
    a.axhline(0, color=INK2, lw=0.6)
    a.axvline(5.5, color=GRID, lw=1.0)
    a.text(2.5, 0.145, "within-agent map (W)", ha="center", fontsize=6, color=INK2)
    a.text(8.5, 0.145, "pooled map (P)", ha="center", fontsize=6, color=INK2)
    a.set_xticks(x, lab, rotation=55, ha="right")
    a.set_ylim(-0.1, 0.16)
    a.set_ylabel("RE family field T (15 units)")
    a.set_title("(a) graded style rival: family field left after each control", loc="left")
    a.legend(loc="lower left", fontsize=5.8, ncol=3, handletextpad=0.2, columnspacing=0.8)
    keys = [("same_nm", "same\nnamed"), ("cross_nm", "cross\nnamed"), ("same_un", "same\nunnam."),
            ("cross_un", "cross\nunnam.")]
    xx = np.arange(len(keys))
    for k, (ch, col) in enumerate((("bge_white32", BLUE), ("gte_white32", ORANGE))):
        v = [ro[f"III|{ch}|{q}"] for q, _ in keys]
        mu = np.array([t["est"] for t in v]); lo = np.array([t["lo"] for t in v]); hi = np.array([t["hi"] for t in v])
        b.bar(xx + (k - 0.5) * 0.36, mu, 0.34, color=col, edgecolor="white", lw=0.5, label=ch.split("_")[0])
        b.errorbar(xx + (k - 0.5) * 0.36, mu, yerr=[mu - lo, hi - mu], fmt="none", ecolor=INK2, lw=0.7)
    d = [("Δ\npre-reg", ro["III|bge_white32|delta_adj"]), ("Δ|recv\npost hoc", ph["recv"]["pooled"]),
         ("Δ|send\npost hoc", ph["send"]["pooled"])]
    x2 = len(keys) + np.arange(len(d)) + 0.3
    for xi, (nm, t) in zip(x2, d):
        b.errorbar([xi], [t["est"]], yerr=[[t["est"] - t["lo"]], [t["hi"] - t["est"]]], fmt="D", ms=3.5, color=VIOLET, lw=0.9)
    b.axhline(0, color=INK2, lw=0.6)
    b.set_xticks(list(xx) + list(x2), [k[1] for k in keys] + [n for n, _ in d], fontsize=5.5)
    b.set_ylabel("read-out jump J^c_1 (cos)")
    b.set_title("(b) read-out pull by lab pair (regime III)", loc="left")
    b.legend(loc="upper right", fontsize=6)
    fig.tight_layout(pad=0.4)
    fig.savefig(FIG / "r2_obs.pdf")


def fig2():
    enc = json.loads((R2 / "encult.json").read_text())
    ro = json.loads((R2 / "readout.json").read_text())["pooled"]
    rng = np.random.default_rng(0)
    fig, (a, b, c) = plt.subplots(1, 3, figsize=(6.8, 2.0), gridspec_kw={"width_ratios": [1.2, 1.2, 1]})

    def by_day(P, key, sel):
        m, lo, hi = [], [], []
        for k in range(5):
            v = np.array([p[key][k] for p in P if sel(p) and len(p[key]) > k and p[key][k] is not None], float)
            v = v[np.isfinite(v)]
            if len(v) < 3:
                m.append(np.nan); lo.append(np.nan); hi.append(np.nan); continue
            bs = v[rng.integers(len(v), size=(2000, len(v)))].mean(1)
            m.append(v.mean()); lo.append(np.percentile(bs, 2.5)); hi.append(np.percentile(bs, 97.5))
        return np.array(m), np.array(lo), np.array(hi)
    d = np.arange(1, 6)
    for key_, col, lab_ in (("bge_white32", BLUE, "raw content"), ("bge_srp", AQUA, "style-free (DQ5)")):
        P = enc[key_]["per_joiner"]
        m, lo, hi = by_day(P, "a", lambda p: True)
        a.plot(d, m, "-o", color=col, ms=3, lw=1.2, label=lab_)
        a.fill_between(d, lo, hi, color=col, alpha=0.15, lw=0)
    P = enc["bge_white32"]["per_joiner"]
    m, _, _ = by_day(P, "a", lambda p: p["goal_no"] == 51)
    a.plot(d, m, ":", color=INK2, lw=1.0, label="#51 joiners (post hoc)")
    a.axhline(0, color=INK2, lw=0.6)
    a.set_xlabel("joiner's day d"); a.set_ylabel("lab alignment a(d)")
    a.set_title("(a) newcomers start at their lab, then drift", loc="left")
    a.legend(fontsize=5.5, loc="upper right")
    for key_, col, lab_ in (("bge_white32", BLUE, "bge"), ("gte_white32", ORANGE, "gte")):
        m, lo, hi = by_day(enc[key_]["per_joiner"], "r", lambda p: True)
        b.plot(d, m, "-o", color=col, ms=3, lw=1.2, label=lab_)
        b.fill_between(d, lo, hi, color=col, alpha=0.15, lw=0)
    b.axhline(0, color=INK2, lw=0.6)
    b.set_xlabel("joiner's day d"); b.set_ylabel("room outsiderness r(d)")
    b.set_title("(b) newcomers sit near the room centroid", loc="left")
    b.legend(fontsize=6)
    M = np.array(ro["kxk_III"], float); N = np.array(ro["kxk_III_n"], float)
    g = ["Anthropic", "OpenAI", "Google", "other"]
    recv = [np.nansum(M[:, k] * N[:, k]) / N[:, k].sum() for k in range(4)]
    send = [np.nansum(M[k] * N[k]) / N[k].sum() for k in range(4)]
    x = np.arange(4)
    c.bar(x - 0.19, recv, 0.36, color=VIOLET, edgecolor="white", lw=0.5, label="as receiver")
    c.bar(x + 0.19, send, 0.36, color=NULL, edgecolor="white", lw=0.5, label="as sender")
    c.set_xticks(x, g, rotation=30)
    c.set_ylabel("read-out jump J^c_1")
    c.set_title("(c) who listens (descriptive)", loc="left")
    c.set_ylim(0, 0.08)
    c.legend(fontsize=5.5, loc="upper left", ncol=2)
    fig.tight_layout(pad=0.4)
    fig.savefig(FIG / "r2_obsb.pdf")


if __name__ == "__main__":
    fig1()
    fig2()
    print("wrote figures/r2_obs.pdf, figures/r2_obsb.pdf")
