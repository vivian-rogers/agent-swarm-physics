"""H57 figures (summary and period folders). Numbers only; no text.

  uv run python hypotheses/H57-copy-under-backlog/analysis/figures.py
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
HDIR = HERE.parent
ROOT = HDIR.parents[1]
OUT = ROOT / "data/processed/H57-copy-under-backlog"
RES = OUT / "results"
FIG = HDIR / "figures"
GP = HDIR / "goalperiod-subhypotheses"
BLUE, ORANGE, AQUA, YELLOW, GRAY, INK = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#8a8984", "#0b0b0b"
plt.rcParams.update({"font.size": 7, "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.6,
                     "axes.edgecolor": "#52514e", "axes.labelcolor": INK, "xtick.color": "#52514e",
                     "ytick.color": "#52514e", "legend.frameon": False, "axes.grid": True, "grid.color": "#ecebe6",
                     "grid.linewidth": 0.5, "lines.linewidth": 1.5})
LAGS = ["0", "15", "30", "60", "120", "240", "480", "960", "1920", "3840"]
LAGX = [7, 22, 45, 90, 180, 360, 720, 1440, 2880, 5000]


def slope(r, key, c="logk"):
    v = (r["slopes"].get(key, {}) or {}).get(c) or {}
    return v.get("b", np.nan), v.get("se", np.nan)


def fig_summary_obs():
    lg = pl.read_parquet(RES / "lag_diag.parquet")
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.0, 2.5), gridspec_kw={"width_ratios": [1, 1.5]})
    for s, col, lab, mk in ((0, BLUE, "read (in the read set)", "o"), (2, ORANGE, "unread (mutually invisible)", "s")):
        x = lg.filter(pl.col("set") == s).with_columns((pl.col("near_both") * pl.col("pairs")).alias("h"))
        agg = x.group_by("lag").agg(pl.col("h").sum(), pl.col("pairs").sum())
        agg = agg.with_columns(pl.col("lag").cast(pl.Utf8)).filter(pl.col("pairs") >= 200)
        xs, ys = [], []
        for lb, xx in zip(LAGS, LAGX):
            row = agg.filter(pl.col("lag") == lb)
            if row.height and row["h"][0] > 0:
                xs.append(xx); ys.append(row["h"][0] / row["pairs"][0])
        a.plot(xs, ys, color=col, marker=mk, ms=4, label=lab)
    a.set_xscale("log"); a.set_yscale("log")
    a.set_xlabel("time lag between the two messages (s)")
    a.set_ylabel("near-copy rate per pair (both models)")
    a.set_title("(a) near-copy rate by time lag, read vs unread pairs", fontsize=7, loc="left")
    a.legend(fontsize=6, loc="lower left")
    rows = [json.loads(f.read_text()) for f in sorted(RES.glob("G*.json"))]
    gs = [r["goal_no"] for r in rows]
    xpos = np.arange(len(gs))
    for off, key, col, lab, mk in ((-0.25, "e_bge|agent", ORANGE, "pre-registered (chance-corrected)", "s"),
                                   (0.0, "elc_bge|agent", AQUA, "post hoc (lag-matched count)", "D"),
                                   (0.25, "er_bge|agent", BLUE, "raw read-set echo (upper bound)", "o")):
        bb = np.array([slope(r, key)[0] for r in rows]); se = np.array([slope(r, key)[1] for r in rows])
        b.errorbar(xpos + off, bb, yerr=1.96 * se, fmt=mk, ms=2.5, color=col, elinewidth=0.6, label=lab)
    b.axhline(0, color=INK, lw=0.6)
    b.axhline(0.03, color=GRAY, lw=0.8, ls="--")
    b.text(len(gs) - 0.5, 0.032, "synthetic H57 world plants +0.03", ha="right", va="bottom", fontsize=6, color="#52514e")
    b.set_xticks(xpos); b.set_xticklabels([f"{g}" for g in gs], fontsize=5, rotation=90)
    b.set_ylim(-0.12, 0.08)
    b.set_ylabel("slope per doubling of backlog k (bge)")
    b.set_xlabel("goal period")
    b.set_title("(b) within-agent echo slope vs backlog, per period", fontsize=7, loc="left")
    b.legend(fontsize=5.5, loc="lower left", ncol=1)
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs.pdf"); fig.savefig(FIG / "summary_obs.png", dpi=160)
    plt.close(fig)


def fig_synth():
    d = pl.concat([pl.read_parquet(f) for f in sorted((OUT / "synthetic").glob("synth_*.parquet"))], how="diagonal_relaxed")
    d = d.filter(pl.col("skeleton").str.contains("G40|G51"))
    worlds = (("no convergence", ~pl.col("skeleton").str.contains("conv")), ("contemporaneous convergence",
                                                                          pl.col("skeleton").str.contains("conv")))
    est = [("e_bge|agent|b", "pre-reg.\nchance-corr."), ("em_bge|agent|b", "mirrored\nplacebo"),
           ("er_bge|agent|b", "raw read-set\necho"), ("elc_bge|agent|b", "post hoc\nlag-matched")]
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.1), sharey=True)
    for ax, (wn, cond) in zip(axes, worlds):
        w = d.filter(cond)
        for j, (col, lab) in enumerate(est):
            for off, sc, c, mk in ((-0.15, "const", GRAY, "o"), (0.15, "load", BLUE, "s")):
                x = w.filter(pl.col("scenario") == sc)
                if col not in x.columns:
                    continue
                v = x[col].drop_nulls().drop_nans().to_numpy()
                if len(v) == 0:
                    continue
                ax.errorbar(j + off, v.mean(), yerr=v.std(), fmt=mk, color=c, ms=3.5, elinewidth=0.8,
                            label=("constant copy prob." if sc == "const" else "load-dependent (H57)") if j == 0 else None)
        tc = w.filter(pl.col("scenario") == "load")["true_copy|agent|b"].mean()
        ax.axhline(tc, color=BLUE, lw=0.6, ls="--")
        ax.axhline(0, color=INK, lw=0.6)
        ax.set_xticks(range(len(est))); ax.set_xticklabels([e[1] for e in est], fontsize=6)
        ax.set_title(f"synthetic worlds, {wn}", fontsize=7, loc="left")
    axes[0].set_ylabel("slope per doubling of k")
    axes[0].legend(fontsize=6, loc="lower left")
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs2.pdf"); fig.savefig(FIG / "synthetic_validation.png", dpi=160)
    plt.close(fig)


def fig_phase():
    s = pl.read_parquet(RES / "summary.parquet").sort("goal_no")
    fig, ax = plt.subplots(figsize=(3.4, 2.4))
    for reg, col, mk in (("I", BLUE, "o"), ("II", ORANGE, "s"), ("III", AQUA, "D")):
        x = s.filter(pl.col("regime") == reg)
        ax.errorbar(x["k_med"], x["er_bge_b"], yerr=1.96 * x["er_bge_se"], fmt=mk, color=col, ms=3, elinewidth=0.5,
                    label=f"regime {reg}")
    ax.axhline(0, color=INK, lw=0.6)
    ax.set_xlabel("median backlog k in the period")
    ax.set_ylabel("raw read-set echo slope (bge)")
    ax.legend(fontsize=6)
    fig.tight_layout(); fig.savefig(FIG / "phase_diagram_er_slope.pdf"); plt.close(fig)


def fig_natives():
    n = json.loads((RES / "native_NE42.json").read_text())
    fig, ax = plt.subplots(figsize=(3.4, 2.2))
    for y, col, mk, lab in (("er_bge", BLUE, "o", "raw echo (bge)"), ("elc_bge", AQUA, "D", "lag-matched (bge)"),
                            ("e_gte", ORANGE, "s", "pre-reg. (gte)")):
        pm = n[y]["phase_means"]
        ax.plot([0, 1, 2], [pm["39"], pm["40"], pm["41"]], marker=mk, color=col, label=lab)
    ax2y = n["dlogk"]["phase_means"]
    ax.set_xticks([0, 1, 2]); ax.set_xticklabels([f"#39 (k {2**ax2y['39'] - 1:.1f})", f"#40 merged (k {2**ax2y['40'] - 1:.1f})",
                                                  f"#41 (k {2**ax2y['41'] - 1:.1f})"], fontsize=6)
    ax.axhline(0, color=INK, lw=0.6); ax.set_ylabel("agent-mean outcome"); ax.legend(fontsize=6)
    fig.tight_layout(); (GP / "NE42/figures").mkdir(parents=True, exist_ok=True)
    fig.savefig(GP / "NE42/figures/ne42_phases.pdf"); plt.close(fig)
    n = json.loads((RES / "native_NE41.json").read_text())
    fig, ax = plt.subplots(figsize=(3.4, 2.2))
    ps = list(n["periods"])
    for off, y, col, mk in ((-0.15, "elc_bge", AQUA, "D"), (0.15, "er_bge", BLUE, "o")):
        b = [((n["periods"][p]["forced"].get(y) or {}).get("b_after") or np.nan) for p in ps]
        se = [((n["periods"][p]["forced"].get(y) or {}).get("se") or np.nan) for p in ps]
        ax.errorbar(np.arange(len(ps)) + off, b, yerr=1.96 * np.array(se, float), fmt=mk, color=col, ms=3, elinewidth=0.5,
                    label={"elc_bge": "lag-matched (bge)", "er_bge": "raw echo (bge)"}[y])
    ax.axhline(0, color=INK, lw=0.6); ax.set_xticks(range(len(ps))); ax.set_xticklabels(ps, fontsize=6)
    ax.set_ylabel("after - before forced erasure"); ax.legend(fontsize=6)
    fig.tight_layout(); (GP / "NE41/figures").mkdir(parents=True, exist_ok=True)
    fig.savefig(GP / "NE41/figures/ne41_after_before.pdf"); plt.close(fig)
    n = json.loads((RES / "native_G51.json").read_text())
    u = pl.DataFrame(n["units"])
    fig, (a, b) = plt.subplots(1, 2, figsize=(5.2, 2.2))
    for y, col, mk, lab in (("er_bge", BLUE, "o", "raw echo (bge)"), ("er_gte", ORANGE, "s", "raw echo (gte)")):
        a.scatter(u["logk_med"], u[y], color=col, marker=mk, s=12, label=lab)
    a.set_xlabel("unit median log2(1+k)"); a.set_ylabel("unit mean raw echo"); a.legend(fontsize=6)
    for y, col, mk in (("er_bge", BLUE, "o"), ("elc_bge", AQUA, "D")):
        bm = n.get(f"{y}|bin_means", [])
        b.plot([r["kbin"] for r in bm], [r[y] for r in bm], marker=mk, color=col,
               label={"er_bge": "raw echo", "elc_bge": "lag-matched"}[y])
    b.set_xticks([0, 1, 2, 3]); b.set_xticklabels(["k<=3", "4-10", "11-29", ">=30"], fontsize=6)
    b.axhline(0, color=INK, lw=0.6); b.legend(fontsize=6); b.set_ylabel("mean (bge)")
    fig.tight_layout(); (GP / "G51/figures").mkdir(parents=True, exist_ok=True)
    fig.savefig(GP / "G51/figures/g51_sweep.pdf"); plt.close(fig)


if __name__ == "__main__":
    FIG.mkdir(exist_ok=True)
    fig_summary_obs(); fig_synth(); fig_phase(); fig_natives()
    print("figures written")
