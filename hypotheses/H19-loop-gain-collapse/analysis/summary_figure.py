"""H19 summary-page figure (figures/summary_obs.pdf): reads round-1 outputs only, recomputes nothing.

(a) P1: the two primary loop gains (E1 equal-time active-spin gain, T1 Hawkes talk branching ratio) per period against
    x_att, with each method's random-effects meta-regression line from results/explore.json;
(b) P3: measured equal-time talk gain vs the gain mapped from H03's fast Hawkes kernels (w = 0.75).

Usage: uv run python hypotheses/H19-loop-gain-collapse/analysis/summary_figure.py
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
ROOT = HERE.parents[2]
DATA = ROOT / "data/processed/H19-loop-gain-collapse"
FIG = HERE.parent / "figures"
FAM = {"E": "#2a78d6", "T": "#eb6834"}  # validated reference slots 1-2 (same as analysis/figures.py)
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
MARK = {"I": "o", "II": "s", "III": "^"}
XP = "x_att_village"
plt.rcParams.update({"font.size": 7, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "axes.titlesize": 7.2,
                     "axes.titleweight": "bold", "legend.frameon": False, "pdf.fonttype": 42})


def main():
    R = json.loads((DATA / "results/explore.json").read_text())
    ctr = pl.read_parquet(DATA / "controls.parquet").select("goal_no", XP, "regime")
    est = pl.read_parquet(DATA / "estimates.parquet").filter(~pl.col("validation_only")).join(ctr, on="goal_no")
    fig, (a, b) = plt.subplots(1, 2, figsize=(4.3, 2.6), gridspec_kw={"width_ratios": [1.15, 1]})

    # (a) the two primaries vs x_att
    hm = []
    for m, fam, lab in (("H03.n_talk", "T", "T1 Hawkes n̂, talk"), ("H19.geq_active", "E", "E1 1−1/VR, active")):
        d = est.filter(pl.col("method") == m)
        for reg in ("I", "II", "III"):
            k = d["regime"].to_numpy() == reg
            a.errorbar(d[XP].to_numpy()[k], d["value"].to_numpy()[k], yerr=d["se"].to_numpy()[k], fmt=MARK[reg], ms=3,
                       color=FAM[fam], alpha=0.55, elinewidth=0.4, mec="white", mew=0.3, zorder=2)
        c = R["fits"][m]["x"]["coefs"]
        xs = np.linspace(d[XP].min(), d[XP].max(), 20)
        a.plot(xs, c[0]["b"] + c[1]["b"] * xs, color=FAM[fam], lw=1.8, zorder=3)
        s = R["P1"]["slopes"][m]
        hm.append(Line2D([], [], color=FAM[fam], lw=1.8, label=f"{lab}: slope {s['b']:+.2f} [{s['lo']:+.2f}, {s['hi']:+.2f}]"))
    a.set_xlabel("x_att = (N_room − 1)/(1 + k̄)")
    a.set_ylabel("loop gain")
    a.set_xlim(0.7, 2.35)
    a.yaxis.grid(True, color=GRID, lw=0.5)
    a.set_axisbelow(True)
    a.set_title("a  No common curve (P1)", loc="left")
    h = [Line2D([], [], ls="", marker=MARK[r], color=INK2, ms=3.5, label=f"regime {r}") for r in ("I", "II", "III")]
    lg = a.legend(handles=hm, loc="upper right", fontsize=4.9, handlelength=1.4, handletextpad=0.3, borderaxespad=0.0, frameon=True, facecolor="white", edgecolor="none", framealpha=0.9, borderpad=0.2)
    a.add_artist(lg)
    a.legend(handles=h, loc="upper right", bbox_to_anchor=(1.0, 0.86), ncol=3, fontsize=5.0, handletextpad=0.1,
             columnspacing=0.6, borderaxespad=0.0)
    a.set_ylim(-0.12, 1.08)

    # (b) P3 mapping
    p3 = pl.DataFrame(R["P3"]["_points"]).join(ctr, on="goal_no")
    for reg in ("I", "II", "III"):
        d = p3.filter(pl.col("regime") == reg)
        b.scatter(d["gmap075"], d["geq_talk"], marker=MARK[reg], s=14, color=FAM["E"], edgecolor="white", linewidth=0.4, zorder=3)
    lim = 0.42
    b.plot([0, lim], [0, lim], color=INK2, lw=0.8, ls="--")
    b.text(0.3, 0.27, "measured = mapped", fontsize=5, color=INK2, rotation=40, ha="center")
    b.set_xlim(-0.01, lim)
    b.set_ylim(-0.09, lim)
    b.set_xlabel("ĝ_map from Hawkes n_x, n_s")
    b.set_ylabel("measured 1−1/VR, talk spins")
    b.yaxis.grid(True, color=GRID, lw=0.5)
    b.set_axisbelow(True)
    b.set_title("b  Mapping holds (P3)", loc="left")
    b.text(0.97, 0.04, f"ρ = {R['P3']['rho_geq_talk_vs_map']:.2f}, p = {R['P3']['p']:.3f}\n"
                       f"above line: {R['P3']['w0.6']['frac_geq_ge_map']:.0%} (w = 0.6)",
           transform=b.transAxes, ha="right", va="bottom", fontsize=5.4, color=INK)
    fig.tight_layout(pad=0.3, w_pad=0.8)
    fig.savefig(FIG / "summary_obs.pdf")
    fig.savefig(FIG / "summary_obs.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    main()
