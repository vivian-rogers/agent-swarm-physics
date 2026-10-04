"""H34 figures (no text from the data; derived statistics only).

  uv run python hypotheses/H34-idea-cascades/analysis/figures.py
Writes hypotheses/H34-idea-cascades/figures/*.pdf (+ .png previews).
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

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h34stats as S  # noqa: E402
import h34core as C  # noqa: E402

FIG = HERE.parent / "figures"
RES = C.OUT / "results"
SYN = C.OUT / "synthetic"
# validated categorical slots 1-3 (dataviz reference palette, light surface); gray for references/nulls
C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#dcdad3"
MK = ["o", "s", "^"]
plt.rcParams.update({"font.size": 8, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5, "lines.linewidth": 1.6,
                     "pdf.fonttype": 42})
REG = {}


def regimes():
    cal = pl.read_parquet(C.SH / "calendar.parquet").group_by("goal_no").agg(pl.col("regime").cast(pl.Utf8).mode().first())
    return {int(r["goal_no"]): r["regime"] for r in cal.iter_rows(named=True)}


def save(fig, name):
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(FIG / f"{name}.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def ccdf(sizes, smax):
    s = np.arange(1, smax + 1)
    return s, np.array([(sizes >= x).mean() for x in s])


def panel_ccdf(ax, pt):
    for i, (g, col) in enumerate(((20, C1), (42, C2), (51, C3))):
        tr = pl.read_parquet(C.OUT / f"G{g:02d}/trees.parquet")
        sizes = tr["size"].to_numpy()
        r = pt.filter((pl.col("goal") == g) & (pl.col("cls") == "ALL")).to_dicts()[0]
        N = max(int(r["N_room"]), int(sizes.max()))
        s, c = ccdf(sizes, int(sizes.max()))
        ax.plot(s, c, color=col, marker=MK[i], ms=4, lw=1.4, label=f"#{g}  R̂={r['R']:.2f}", zorder=3)
        p = S.nb_gw_pmf_trunc(r["R"], r["k"], N)
        cp = np.cumsum(p[::-1])[::-1]
        ax.plot(np.arange(1, N + 1), cp, color=col, ls="--", lw=1.0, alpha=0.9, zorder=2)
    x = np.arange(1, 27)
    ax.plot(x, x ** -0.5, color=INK2, ls=":", lw=1.0, label="critical $s^{-3/2}$")
    ax.plot([], [], color=INK2, ls="--", lw=1.0, label="GW-NB from R̂, k̂")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_ylim(1e-5, 1.3)
    ax.set_xlabel("cascade size s (agents in an exposure tree)")
    ax.set_ylabel("P(S ≥ s)")
    ax.legend(loc="lower left", fontsize=7)


def panel_rn(ax, pt):
    a = pt.filter(pl.col("cls") == "ALL").sort("goal").to_dicts()
    reg = REG
    for i, (rg, col) in enumerate((("I", C1), ("II", C2), ("III", C3))):
        sub = [r for r in a if reg.get(r["goal"]) == rg and r.get("n03") is not None]
        ax.scatter([r["n03"] for r in sub], [r["R"] for r in sub], s=22, color=col, marker=MK[i], edgecolor="white",
                   linewidth=0.6, label=f"regime {rg}", zorder=3)
    for r in a:
        if r["goal"] in (20, 42, 51):
            ax.annotate(f"#{r['goal']}", (r["n03"], r["R"]), xytext=(3, 3), textcoords="offset points", fontsize=6.5, color=INK2)
    ax.plot([0, 0.8], [0, 0.8], color=INK2, lw=0.8, ls=":")
    ax.text(0.445, 0.40, "R̂ = n̂", fontsize=6.5, color=INK2)
    ax.set_xlim(-0.02, 0.82)
    ax.set_ylim(0, 0.5)
    ax.set_xlabel("activity loop gain n̂ (H03, talk)")
    ax.set_ylabel("idea branching ratio R̂")
    ax.legend(loc="upper left", fontsize=7)
    s = json.loads((RES / "summary.json").read_text())["P4"]["primary"]["R~n03"]
    ax.text(0.98, 0.04, f"Spearman ρ = {s['rho']:.2f} (n = {s['n']})", transform=ax.transAxes, ha="right", fontsize=7, color=INK2)


def summary_obs(pt):
    fig, axs = plt.subplots(1, 2, figsize=(6.4, 2.5))
    panel_ccdf(axs[0], pt)
    panel_rn(axs[1], pt)
    axs[0].set_title("(a) cascade sizes vs branching law", fontsize=8, loc="left", color=INK)
    axs[1].set_title("(b) idea spread vs activity criticality", fontsize=8, loc="left", color=INK)
    fig.tight_layout(w_pad=1.5)
    save(fig, "summary_obs")


def fig_hr10(pt):
    a = pt.filter(pl.col("cls") == "ALL").sort("goal").to_dicts()
    fig, ax = plt.subplots(figsize=(6.4, 2.3))
    for i, (rg, col) in enumerate((("I", C1), ("II", C2), ("III", C3))):
        sub = [(j, r) for j, r in enumerate(a) if REG.get(r["goal"]) == rg]
        x = [j for j, _ in sub]
        y = [r["hr10"] for _, r in sub]
        lo = [r["hr10"] - r["hr10_lo"] for _, r in sub]
        hi = [min(r["hr10_hi"], 500) - r["hr10"] for _, r in sub]
        ax.errorbar(x, y, yerr=[lo, hi], fmt=MK[i], color=col, ms=4, elinewidth=1, capsize=0, label=f"regime {rg}")
    ax.axhline(1, color=INK2, lw=0.8, ls=":")
    ax.set_yscale("log")
    ax.set_xticks(range(len(a)))
    ax.set_xticklabels([str(r["goal"]) for r in a], fontsize=6)
    ax.set_xlabel("goal period")
    ax.set_ylabel("HR₁₀ (recent visible source vs none)")
    ax.legend(fontsize=7, loc="upper left", ncol=3)
    fig.tight_layout()
    save(fig, "hr10_by_period")


def fig_rpair(pt):
    a = pt.filter(pl.col("cls") == "ALL").to_dicts()
    fig, ax = plt.subplots(figsize=(3.2, 2.5))
    for i, (rg, col) in enumerate((("I", C1), ("II", C2), ("III", C3))):
        sub = [r for r in a if REG.get(r["goal"]) == rg]
        ax.scatter([r["N_room"] - 1 for r in sub], [r["R"] / (r["N_room"] - 1) for r in sub], s=20, color=col, marker=MK[i],
                   edgecolor="white", linewidth=0.6, label=f"regime {rg}")
    x = np.array([r["N_room"] - 1 for r in a], float)
    y = np.array([r["R"] / (r["N_room"] - 1) for r in a])
    b = np.polyfit(np.log(x), np.log(y), 1)
    xx = np.linspace(x.min(), x.max(), 50)
    ax.plot(xx, np.exp(b[1]) * xx ** b[0], color=INK2, lw=1, ls="--")
    ax.text(0.97, 0.92, f"slope {b[0]:.2f}", transform=ax.transAxes, ha="right", fontsize=7, color=INK2)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("N_room − 1")
    ax.set_ylabel("per-pair branching R̂/(N−1)")
    ax.legend(fontsize=7, loc="lower left")
    fig.tight_layout()
    save(fig, "rpair_vs_N")


def fig_forecast():
    pre = pl.read_parquet(RES / "forecast_days.parquet")
    post = pl.read_parquet(RES / "forecast_posthoc_days.parquet").filter(pl.col("variant") == "V3")
    fig, axs = plt.subplots(1, 2, figsize=(6.4, 2.5), sharey=True)
    for ax, df, title in ((axs[0], pre, "pre-registered (FN-GW, all prior days)"), (axs[1], post, "post hoc V3 (GW-NB, last 2 days + drift)")):
        ax.scatter(df["pred_p2"], df["obs_p2"], s=8, color=C1, alpha=0.7, edgecolor="none", label="P(s ≥ 2)")
        ax.scatter(df["pred_p3"], df["obs_p3"], s=8, color=C2, marker="s", alpha=0.7, edgecolor="none", label="P(s ≥ 3)")
        ax.plot([0, 0.45], [0, 0.45], color=INK2, lw=0.8, ls=":")
        c2, c3 = df["cover2"].mean(), df["cover3"].mean()
        ax.set_title(title, fontsize=7.5, loc="left")
        ax.text(0.97, 0.05, f"90% PI coverage: {c2:.0%} / {c3:.0%}", transform=ax.transAxes, ha="right", fontsize=7, color=INK2)
        ax.set_xlabel("forecast for the next day")
    axs[0].set_ylabel("observed that day")
    axs[0].legend(fontsize=7, loc="upper left")
    fig.tight_layout()
    save(fig, "forecast_calibration")


def fig_synthetic():
    s1 = pl.read_parquet(SYN / "s1.parquet")
    s2 = pl.read_parquet(SYN / "s2.parquet")
    fig, axs = plt.subplots(1, 3, figsize=(7.0, 2.4))
    ax = axs[0]
    for i, (N, col) in enumerate(((8, C1), (15, C2), (25, C3))):
        d = s1.filter((pl.col("model") == "gwnb") & (pl.col("N") == N) & (pl.col("n_trees") == 3000)).group_by("R").agg(pl.col("tau_app").mean()).sort("R")
        ax.plot(d["R"], d["tau_app"], color=col, marker=MK[i], ms=3.5, label=f"N = {N}")
    ax.axhline(1.5, color=INK2, lw=0.8, ls=":")
    ax.set_xlabel("true R (GW-NB, k = 0.5)")
    ax.set_ylabel("apparent exponent τ_app")
    ax.set_title("(a) τ_app reads R, not universality", fontsize=7.5, loc="left")
    ax.legend(fontsize=6.5)
    ax = axs[1]
    for i, (N, col) in enumerate(((8, C1), (15, C2), (25, C3))):
        d = s1.filter((pl.col("model") == "reedfrost") & (pl.col("N") == N) & (pl.col("n_trees") == 3000)).group_by("R").agg(pl.col("R_off").mean(), pl.col("fn_R0").mean()).sort("R")
        ax.plot(d["R"], d["R_off"], color=col, marker=MK[i], ms=3.5, ls="--", lw=1)
        ax.plot(d["R"], d["fn_R0"], color=col, marker=MK[i], ms=3.5, label=f"N = {N}")
    ax.plot([0, 1], [0, 1], color=INK2, lw=0.8, ls=":")
    ax.set_xlabel("true R0 (Reed–Frost)")
    ax.set_ylabel("estimate")
    ax.set_title("(b) realized R̂ (dashed) vs FN-GW R0", fontsize=7.5, loc="left")
    ax.legend(fontsize=6.5)
    ax = axs[2]
    d = s2.filter(pl.col("mode") == "simple")
    for i, (g, col) in enumerate(((20, C1), (42, C2), (51, C3))):
        e = d.filter(pl.col("goal") == g)
        ax.scatter(e["R_true"], e["R_hat"], s=12, facecolor="none", edgecolor=col, marker=MK[i], linewidth=0.8)
        ax.scatter(e["R_true"], e["R_c"], s=12, color=col, marker=MK[i], edgecolor="white", linewidth=0.4, label=f"#{g}")
    ax.plot([0, 1], [0, 1], color=INK2, lw=0.8, ls=":")
    ax.set_xlabel("true contagion R (S2)")
    ax.set_ylabel("R̂ (open) / R_c (filled)")
    ax.set_title("(c) the field inflates R̂; R_c corrects", fontsize=7.5, loc="left")
    ax.legend(fontsize=6.5, loc="lower right")
    fig.tight_layout()
    save(fig, "synthetic_validation")


def summary_obsb():
    s2 = pl.read_parquet(SYN / "s2.parquet").filter(pl.col("mode") == "simple")
    post = pl.read_parquet(RES / "forecast_posthoc_days.parquet").filter(pl.col("variant") == "V3")
    fig, axs = plt.subplots(1, 2, figsize=(3.5, 1.95))
    ax = axs[0]
    ax.scatter(s2["R_true"], s2["R_hat"], s=9, facecolor="none", edgecolor=C2, marker="s", linewidth=0.7, label="R̂")
    ax.scatter(s2["R_true"], s2["R_c"], s=9, color=C1, edgecolor="white", linewidth=0.3, label="R_c")
    ax.plot([0, 1], [0, 1], color=INK2, lw=0.7, ls=":")
    ax.set_xlabel("true contagion R", fontsize=6.5)
    ax.set_ylabel("estimate", fontsize=6.5)
    ax.set_title("(a) synthetic (S2)", fontsize=6.5, loc="left")
    ax.legend(fontsize=5.5, loc="upper left", handletextpad=0.2)
    ax.tick_params(labelsize=5.5)
    ax = axs[1]
    ax.scatter(post["pred_p2"], post["obs_p2"], s=4, color=C1, alpha=0.7, edgecolor="none", label="P(s≥2)")
    ax.scatter(post["pred_p3"], post["obs_p3"], s=4, color=C2, marker="s", alpha=0.7, edgecolor="none", label="P(s≥3)")
    ax.plot([0, 0.45], [0, 0.45], color=INK2, lw=0.7, ls=":")
    ax.set_xlabel("next-day forecast (V3)", fontsize=6.5)
    ax.set_ylabel("observed", fontsize=6.5)
    ax.set_title(f"(b) coverage {post['cover2'].mean():.0%} / {post['cover3'].mean():.0%}", fontsize=6.5, loc="left")
    ax.legend(fontsize=5.5, loc="upper left", handletextpad=0.2)
    ax.tick_params(labelsize=5.5)
    fig.tight_layout(w_pad=0.6)
    save(fig, "summary_obsb")


def main():
    global REG
    REG = regimes()
    pt = pl.read_parquet(RES / "period_table.parquet")
    summary_obs(pt)
    fig_hr10(pt)
    fig_rpair(pt)
    fig_forecast()
    fig_synthetic()
    summary_obsb()
    print("figures written to", FIG)


if __name__ == "__main__":
    main()
