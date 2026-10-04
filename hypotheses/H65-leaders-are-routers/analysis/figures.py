"""H65 figures: figures/h65_obs.pdf (leader natives and the replication layer) and figures/h65_synth.pdf."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
import numpy as np
import polars as pl

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data/processed/H65-leaders-are-routers"
FIG = Path(__file__).resolve().parents[1] / "figures"
C = {"blue": "#2a78d6", "orange": "#eb6834", "aqua": "#1baf7a", "yellow": "#eda100", "violet": "#4a3aa7",
     "gray": "#8a8984", "ink": "#0b0b0b", "ink2": "#52514e"}
plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": C["ink2"], "xtick.color": C["ink2"], "ytick.color": C["ink2"]})
MODELS = [("bge_small", "o", "bge"), ("gte_modernbert", "s", "gte"), ("style", "^", "style")]


def obs():
    fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.5), gridspec_kw={"width_ratios": [1, 1.25, 1]})
    a = ax[0]
    for k, name in enumerate(("G26", "G44")):
        for j, (m, mk, lab) in enumerate(MODELS):
            r = json.loads((DATA / f"natives/{m}/{name}.json").read_text())
            a.scatter(k * 2 + j * 0.15, r["pct_chi"], marker=mk, color=C["blue"], s=18, label="inflow χ" if k == j == 0 else None)
            a.scatter(k * 2 + 0.9 + j * 0.15, r["pct_kappa"], marker=mk, color=C["orange"], s=18,
                      label="outflow κ" if k == j == 0 else None)
        a.hlines(r["null_mean_pct_chi"], k * 2 - 0.1, k * 2 + 0.4, color=C["blue"], lw=1, ls=":")
        a.hlines(r["null_mean_pct_kappa"], k * 2 + 0.8, k * 2 + 1.3, color=C["orange"], lw=1, ls=":")
    a.set_xticks([0.6, 2.6], ["#26 elected", "#44 installed"])
    a.set_ylim(-0.05, 1.05)
    a.set_ylabel("leader's rank percentile")
    a.set_title("(a) single leaders (dotted: null)", fontsize=8, loc="left")
    a.legend(frameon=False, fontsize=6.5, loc="upper center", bbox_to_anchor=(0.62, 0.92))
    b = ax[1]
    ms = [("chi", "Δχ inflow", C["blue"]), ("kappa", "Δκ outflow", C["orange"]), ("BO", "Δ reply breadth", C["aqua"]),
          ("RI", "Δ replies received", C["violet"])]
    for k, name in enumerate(("G35", "G12")):
        r = json.loads((DATA / f"natives/bge_small/{name}.json").read_text())
        for j, (m, lab, col) in enumerate(ms):
            x = k * 1.2 + j * 0.22
            v = r[m]["beta"]
            sig = min(r[m]["p_greater"], r[m]["p_less"]) < 0.05
            b.bar(x, v, width=0.18, color=col if sig else "white", edgecolor=col, lw=1.2,
                  label=lab if k == 0 else None)
    b.axhline(0, color=C["ink2"], lw=0.6)
    b.set_xticks([0.33, 1.53], ["#35 lead designers", "#12 judges"])
    b.set_ylabel("role − same agent off-role")
    b.set_title("(b) role contrasts (filled: p<0.05)", fontsize=8, loc="left")
    b.legend(frameon=False, fontsize=6, loc="upper left")
    c = ax[2]
    u = json.loads((DATA / "replication/bge_small/periods.json").read_text())
    for j, (k, lab, col) in enumerate((("rho_RO_chi", "ρ(reply-out, χ)", C["blue"]), ("D", "D_p attention\nalignment", C["orange"]))):
        v = np.array([r[k] for r in u], float)
        v = v[np.isfinite(v)]
        x = j + np.random.default_rng(j).uniform(-0.15, 0.15, len(v))
        c.scatter(x, v, s=9, color=col, edgecolor="white", lw=0.4)
        c.hlines(np.median(v), j - 0.25, j + 0.25, color=C["ink"], lw=1.5)
    c.axhline(0, color=C["ink2"], lw=0.6)
    c.set_xticks([0, 1], ["ρ(RO, χ)", "D_p"])
    c.set_title("(c) replication, 46 units", fontsize=8, loc="left")
    fig.tight_layout()
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / "h65_obs.pdf")
    fig.savefig(FIG / "h65_obs.png", dpi=150)


def synth():
    d = pl.concat([pl.read_parquet(DATA / "synthetic/natives_reps.parquet"),
                   pl.read_parquet(DATA / "synthetic/null_extra_reps.parquet")], how="diagonal")
    s = d.group_by("native", "scen").agg(pl.col("router_call").mean()).sort("native", "scen")
    fig, ax = plt.subplots(figsize=(3.6, 1.9))
    scen = [("null", C["gray"]), ("router_weak", C["aqua"]), ("router", C["blue"]), ("source", C["orange"])]
    for k, nat in enumerate(("G35", "G12", "G26", "G44")):
        for j, (sc, col) in enumerate(scen):
            v = s.filter((pl.col("native") == nat) & (pl.col("scen") == sc))["router_call"]
            ax.bar(k + j * 0.2 - 0.3, v[0] if len(v) else 0, width=0.18, color=col, label=sc if k == 0 else None)
    ax.set_xticks(range(4), ["G35", "G12", "G26 (raw)", "G44 (raw)"])
    ax.set_ylabel("router-call rate")
    ax.legend(frameon=False, fontsize=6, ncol=4, loc="upper center", bbox_to_anchor=(0.5, 1.22))
    fig.tight_layout()
    fig.savefig(FIG / "h65_synth.pdf")
    fig.savefig(FIG / "h65_synth.png", dpi=150)


if __name__ == "__main__":
    obs()
    synth()
