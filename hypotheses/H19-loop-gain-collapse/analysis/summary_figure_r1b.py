"""H19 round-1b page-2 figure (figures/summary_obs2.pdf): reads round-1b outputs only.

(a) E1 (equal-time activity gain) per period against x_att: raw (pre-registered, whole-day grid) and DQ8-trimmed,
    with each version's random-effects meta-regression line (r1b/results*/explore.json).
(b) NE14: regime II -> III change of the activity gain (Delta E +- 1.96 SE) on the old and fixed tables, raw vs
    day-edge-adjusted (r1b/NE14/result.json).
Usage: H19_DATA=r1b uv run python hypotheses/H19-loop-gain-collapse/analysis/summary_figure_r1b.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[2] / "data/processed/H19-loop-gain-collapse"
FIG = HERE.parent / "figures"
COL = {"raw": "#2a78d6", "trim": "#eb6834", "scaf": "#1baf7a"}   # reference slots 1-3 (all-pairs validated)
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
MARK = {"I": "o", "II": "s", "III": "^"}
XP = "x_att_village"
plt.rcParams.update({"font.size": 7, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "axes.titlesize": 7.2,
                     "axes.titleweight": "bold", "legend.frameon": False, "pdf.fonttype": 42})


def main():
    ctr = pl.read_parquet(DATA / "controls.parquet").select("goal_no", XP, "regime")
    est = pl.read_parquet(DATA / "r1b/estimates.parquet").join(ctr, on="goal_no")
    fig, (a, b) = plt.subplots(1, 2, figsize=(4.3, 2.05), gridspec_kw={"width_ratios": [1.2, 1]})
    hs = []
    for v, m, res in (("raw", "H19.geq_active", "results"), ("trim", "H19.geq_active_trim", "results_trim")):
        d = est.filter(pl.col("method") == m)
        for reg in ("I", "II", "III"):
            k = d["regime"].to_numpy() == reg
            a.errorbar(d[XP].to_numpy()[k], d["value"].to_numpy()[k], yerr=d["se"].to_numpy()[k], fmt=MARK[reg], ms=3,
                       color=COL[v], alpha=0.6, elinewidth=0.4, mec="white", mew=0.3, zorder=2)
        R = json.loads((DATA / f"r1b/{res}/explore.json").read_text())
        c = R["fits"]["H19.geq_active"]["x"]["coefs"]
        xs = np.linspace(d[XP].min(), d[XP].max(), 20)
        a.plot(xs, c[0]["b"] + c[1]["b"] * xs, color=COL[v], lw=1.8, zorder=3)
        s = R["P1"]["slopes"]["H19.geq_active"]
        hs.append(Line2D([], [], color=COL[v], lw=1.8, label=f"{'raw' if v == 'raw' else 'trimmed'}: slope {s['b']:+.2f} [{s['lo']:+.2f}, {s['hi']:+.2f}]"))
    a.axhline(0, color=INK2, lw=0.5)
    a.set_xlabel("x_att = (N_room − 1)/(1 + k̄)")
    a.set_ylabel("activity gain 1 − 1/VR")
    a.yaxis.grid(True, color=GRID, lw=0.5)
    a.set_axisbelow(True)
    a.set_title("a  Activity gain vs x_att", loc="left")
    a.set_ylim(-0.12, 0.78)
    hs += [Line2D([], [], ls="", marker=MARK[r], color=INK2, ms=3, label=f"regime {r}") for r in ("I", "III")]
    a.legend(handles=hs, loc="upper left", fontsize=5.4, handlelength=1.4, ncol=1)

    N = json.loads((DATA / "r1b/NE14/result.json").read_text())
    groups = [("old", "old tables"), ("fixed", "fixed tables")]
    vers = [("raw", "raw"), ("trim", "DQ8 trim"), ("scaf", "H38-conditioned")]
    w = 0.26
    for gi, (bins, glab) in enumerate(groups):
        for vi, (v, vlab) in enumerate(vers):
            r = N[bins]["delta"][f"active|{v}"]
            x = gi + (vi - 1) * w
            b.bar(x, r["dE"], width=w - 0.03, color=COL[v], label=vlab if gi == 0 else None, zorder=2)
            b.errorbar(x, r["dE"], yerr=1.96 * r["se"], color=INK, lw=0.6, capsize=1.5, zorder=3)
    b.axhline(0, color=INK2, lw=0.6)
    b.set_xticks([0, 1]); b.set_xticklabels([g[1] for g in groups])
    b.set_ylabel("ΔE, regime III − II")
    b.yaxis.grid(True, color=GRID, lw=0.5)
    b.set_axisbelow(True)
    b.set_title("b  NE14 (regime II → III)", loc="left")
    b.legend(loc="lower left", fontsize=5.6, handlelength=1.0)
    b.set_ylim(-0.5, 0.36)
    fig.tight_layout(pad=0.4, w_pad=1.0)
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / "summary_obs2.pdf")
    fig.savefig(FIG / "summary_obs2.png", dpi=200)


if __name__ == "__main__":
    main()
