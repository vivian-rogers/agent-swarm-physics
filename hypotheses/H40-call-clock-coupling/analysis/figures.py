"""H40 figures (print, RevTeX column width).

  figures/summary_obs.pdf        (a) eta per goal period with 95% CI (0 = call clock, 1 = wall clock), by regime;
                                 (b) G51 reply curves of slow / fast cadence tertiles in call count and in wall time
  figures/synthetic_compact.pdf  synthetic recovery of eta (S1-S5) and of the between-agent slope (S1 vs S4)
  figures/eta_by_gap.pdf         pooled eta by gap kind and regime (card)

  uv run python hypotheses/H40-call-clock-coupling/analysis/figures.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h40lib as L  # noqa: E402

RES = L.OUT / "results"
# validated categorical slots 1-3 (light mode): blue, orange, aqua; text in ink tokens
REG_COL = {"I": "#2a78d6", "II": "#eb6834", "III": "#1baf7a"}
INK, INK2, GRID = "#0b0b0b", "#52514e", "#d9d8d4"
plt.rcParams.update({"font.size": 7.5, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.linewidth": 0.6, "font.family": "serif", "legend.frameon": False,
                     "axes.spines.top": False, "axes.spines.right": False})


def panel_eta(ax, df: pl.DataFrame, col="eta", se="eta_se", title=None):
    ax.axhline(0, color=INK2, lw=0.8, ls="--", zorder=1)
    ax.axhline(1, color=INK2, lw=0.8, ls=":", zorder=1)
    for reg, c in REG_COL.items():
        d = df.filter((pl.col("regime") == reg) & pl.col(se).is_not_null() & (pl.col(se) < 1))
        if not d.height:
            continue
        g = d["goal"].to_numpy(); e = d[col].to_numpy(); s = d[se].to_numpy()
        ax.errorbar(g, e, yerr=1.96 * s, fmt="o", ms=3.2, color=c, ecolor=c, elinewidth=0.9, capsize=0, label=f"regime {reg}",
                    zorder=3, markeredgecolor="white", markeredgewidth=0.5)
    ax.text(1.5, 0.04, "call clock", color=INK2, fontsize=6.5, va="bottom")
    ax.text(1.5, 1.04, "wall clock", color=INK2, fontsize=6.5, va="bottom")
    ax.set_xlabel("goal period")
    ax.set_ylabel(r"$\eta$ (exposure-time elasticity)")
    ax.set_ylim(-1.1, 1.8)
    ax.set_xlim(0, 53)
    ax.grid(axis="y", color=GRID, lw=0.4)
    ax.legend(loc="upper right", fontsize=6.5, handletextpad=0.2, borderaxespad=0.1)
    if title:
        ax.set_title(title, fontsize=7.5, loc="left", color=INK)


def panel_collapse(ax, goal=51, which="call"):
    r = json.loads((RES / f"G{goal:02d}.json").read_text())
    c = r["modelfree"]["collapse"]
    F = np.array(c["F_call"] if which == "call" else c["F_wall"])
    x = np.array(c["grid_calls"]) if which == "call" else np.array(c["grid_wall_s"]) / 60
    names = ["slow", "middle", "fast"]
    cols = ["#2a78d6", "#a8a7a2", "#eb6834"]
    for k in (0, 2, 1):
        ax.plot(x, F[k], "-o", ms=2.8, lw=1.4, color=cols[k], label=f"{names[k]} ({c['tertile_rates'][k]:.0f}/h)",
                markeredgecolor="white", markeredgewidth=0.4)
    ax.set_xscale("log")
    ax.set_xlabel("calls since read-out" if which == "call" else "minutes since message")
    ax.set_ylabel("share replied")
    ax.grid(axis="y", color=GRID, lw=0.4)
    D = c["D_call"] if which == "call" else c["D_wall"]
    ax.set_title(f"G{goal}: {'call count' if which == 'call' else 'wall time'} (D = {D:.2f})", fontsize=7, loc="left")


def panel_heavy(ax, goal=51):
    """Per agent-unit: model-based per-call coupling (alpha) and per-hour coupling (alpha + log r), vs call rate."""
    r = json.loads((RES / f"G{goal:02d}.json").read_text())
    a = pl.DataFrame(r["au_table"]).filter((pl.col("replies") >= 5) & pl.col("rate").is_finite())
    x = np.log(a["rate"].to_numpy())
    al = a["fe"].to_numpy()
    u = a["unit"].to_numpy()
    # remove unit means (the estimand is within unit), then centre
    def dm(v):
        v = v.copy()
        for uu in np.unique(u):
            m = u == uu
            v[m] -= v[m].mean()
        return v
    xc, yc, yh = x, dm(al), dm(al + x)
    xr = np.exp(xc)
    c_call, c_hour = "#2a78d6", "#eb6834"
    ax.scatter(xr, yh, s=7, color=c_hour, alpha=0.75, linewidths=0.3, edgecolors="white", label="per hour", zorder=3)
    ax.scatter(xr, yc, s=7, color=c_call, alpha=0.75, linewidths=0.3, edgecolors="white", label="per call", zorder=3)
    b = r["between"]
    grid = np.linspace(x.min(), x.max(), 20)
    xm = np.average(x)
    ax.plot(np.exp(grid), b["s"] * (grid - xm), color=c_call, lw=1.6, zorder=4)
    ax.plot(np.exp(grid), (1 + b["s"]) * (grid - xm), color=c_hour, lw=1.6, zorder=4)
    ax.set_xscale("log")
    ax.set_xlabel("recipient call rate (calls / h)")
    ax.set_ylabel("log coupling (unit-centred)")
    ax.grid(axis="y", color=GRID, lw=0.4)
    ax.text(0.98, 0.05, f"per call: slope {b['s']:+.2f} [{b['s_lo']:+.2f}, {b['s_hi']:+.2f}]", transform=ax.transAxes,
            ha="right", va="bottom", fontsize=6, color=INK)
    ax.text(0.02, 0.95, f"per hour: slope {1 + b['s']:+.2f}", transform=ax.transAxes, ha="left", va="top", fontsize=6, color=INK)
    ax.legend(fontsize=6, loc="lower left", bbox_to_anchor=(0.0, 0.62), handletextpad=0.1, markerscale=1.5)
    ax.set_title(f"(b) G{goal}: {len(x)} agent-units (32 agents x 12 units), 'heavy spins'", fontsize=7, loc="left")


def fig_summary():
    df = pl.read_parquet(RES / "replication_table.parquet")
    fig, (ax, a2) = plt.subplots(2, 1, figsize=(4.2, 4.0), gridspec_kw=dict(height_ratios=[1, 1.05], hspace=0.55))
    panel_eta(ax, df, title="(a) does a call that spans more wall time carry more reply hazard? 95% CI")
    panel_heavy(a2, 51)
    fig.savefig(L.FIG / "summary_obs.pdf", bbox_inches="tight")
    fig.savefig(L.FIG / "summary_obs.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig_synthetic():
    syn = pl.read_parquet(RES / "synthetic_summary.parquet")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(4.2, 1.9), gridspec_kw=dict(width_ratios=[1.6, 1], wspace=0.4))
    scen = ["S1", "S2", "S3", "S4", "S5"]
    tags = syn.select("goal", "unit").unique().sort("goal").rows()
    marks = ["o", "s", "^", "D"]
    for j, (g, u) in enumerate(tags):
        d = syn.filter((pl.col("goal") == g) & (pl.col("unit") == u))
        for i, s in enumerate(scen):
            r = d.filter(pl.col("scenario") == s)
            if not r.height:
                continue
            x = i + (j - 1.5) * 0.14
            a1.errorbar(x, r["eta_mean"][0], yerr=r["eta_sd"][0] * 1.96, fmt=marks[j % 4], ms=3, color=REG_COL["I" if g < 33 else "III"],
                        elinewidth=0.8, capsize=0, markeredgecolor="white", markeredgewidth=0.4,
                        label=(f"G{g}" + ("" if u == "all" else f" ({u})")) if i == 0 else None)
    for i, s in enumerate(scen):
        tv = {"S1": 0, "S2": 1, "S3": 0.5, "S4": 0, "S5": 0}[s]
        a1.plot([i - 0.32, i + 0.32], [tv, tv], color=INK, lw=1.0)
    a1.set_xticks(range(5)); a1.set_xticklabels(["S1\ncall", "S2\nwall", "S3\nmix", "S4\nconf.", "S5\ndet."], fontsize=6)
    a1.set_ylabel(r"$\hat\eta$ (mean $\pm$ 1.96 SD)")
    a1.grid(axis="y", color=GRID, lw=0.4)
    a1.legend(fontsize=5.5, loc="upper right", ncol=1, handletextpad=0.1)
    for j, (g, u) in enumerate(tags):
        d = syn.filter((pl.col("goal") == g) & (pl.col("unit") == u))
        for k, s in enumerate(["S1", "S4"]):
            r = d.filter(pl.col("scenario") == s)
            if r.height:
                a2.errorbar(k + (j - 1.5) * 0.1, r["s_mean"][0], yerr=1.96 * r["s_sd"][0], fmt=marks[j % 4], ms=3,
                            color=REG_COL["I" if g < 33 else "III"], elinewidth=0.8, capsize=0, markeredgecolor="white",
                            markeredgewidth=0.4)
    a2.plot([-0.3, 0.3], [0, 0], color=INK, lw=1.0); a2.plot([0.7, 1.3], [0.5, 0.5], color=INK, lw=1.0)
    a2.set_xticks([0, 1]); a2.set_xticklabels(["S1", "S4"], fontsize=6)
    a2.set_ylabel(r"between-agent slope $\hat s$")
    a2.grid(axis="y", color=GRID, lw=0.4)
    fig.savefig(L.FIG / "synthetic_compact.pdf", bbox_inches="tight")
    fig.savefig(L.FIG / "synthetic_compact.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig_eta_by_gap():
    S = json.loads((RES / "summary.json").read_text())
    rows = [("all calls", "RE_eta"), ("busy (chained)", "RE_eta_busy"), ("long previous call", "RE_eta_longprev"),
            ("pause wake", "RE_eta_pause"), ("after forced consol.", "RE_eta_forced"), ("chat mode (reg. I/II)", "RE_eta_chat"),
            ("read-out wait $\\eta_1$", "RE_eta1")]
    fig, ax = plt.subplots(figsize=(3.4, 2.0))
    for i, (lab, key) in enumerate(rows):
        for k, (reg, c) in enumerate((("I", REG_COL["I"]), ("III", REG_COL["III"]))):
            v = S.get(key, {}).get(reg)
            if not v or not np.isfinite(v.get("mean", np.nan)):
                continue
            ax.errorbar(v["mean"], i + (k - 0.5) * 0.25, xerr=[[v["mean"] - v["lo"]], [v["hi"] - v["mean"]]], fmt="o", ms=3,
                        color=c, elinewidth=0.9, capsize=0, label=f"regime {reg}" if i == 0 else None,
                        markeredgecolor="white", markeredgewidth=0.4)
    ax.axvline(0, color=INK2, lw=0.8, ls="--"); ax.axvline(1, color=INK2, lw=0.8, ls=":")
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows], fontsize=6.5)
    ax.invert_yaxis()
    ax.set_xlabel(r"pooled $\eta$ (random-effects mean, 95% CI)")
    ax.grid(axis="x", color=GRID, lw=0.4)
    ax.legend(fontsize=6, loc="lower right")
    fig.savefig(L.FIG / "eta_by_gap.pdf", bbox_inches="tight")
    fig.savefig(L.FIG / "eta_by_gap.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def main():
    L.FIG.mkdir(parents=True, exist_ok=True)
    if (RES / "replication_table.parquet").exists() and (RES / "G51.json").exists():
        fig_summary()
    if (RES / "synthetic_summary.parquet").exists():
        fig_synthetic()
    if (RES / "summary.json").exists():
        fig_eta_by_gap()


if __name__ == "__main__":
    main()
