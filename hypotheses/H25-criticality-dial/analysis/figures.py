"""H25 figures: synthetic recovery, the daily dial timeline, agreement with H19/H03, per-period dials, summary panels.

Usage: uv run python hypotheses/H25-criticality-dial/analysis/figures.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h25common as C  # noqa: E402
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

INK, INK2, MUTED, GRID, SURF = "#0b0b0b", "#52514e", "#85847e", "#e4e2dc", "#fcfcfb"
COL = {"activity": "#2a78d6", "talk": "#eb6834", "content": "#1baf7a"}
SHADE = {"I": "#f6f5f2", "II": "#eceae4", "III": "#f6f5f2"}
plt.rcParams.update({"font.size": 8, "axes.edgecolor": MUTED, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
                     "grid.linewidth": 0.6, "figure.facecolor": "white", "axes.facecolor": "white", "legend.frameon": False,
                     "savefig.dpi": 200})
SYN = C.OUT / "synthetic"
PRIM = {"activity": "auto", "talk": "auto", "content": "F2"}


def save(fig, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight")
    if path.suffix == ".png":
        fig.savefig(path.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def med_iqr(d, x, y):
    g = d.group_by(x).agg(pl.col(y).median().alias("m"), pl.col(y).quantile(0.25).alias("q1"), pl.col(y).quantile(0.75).alias("q3"),
                          pl.col("truth").median().alias("t")).sort(x)
    return g


def synthetic_panels(axes):
    b = pl.read_parquet(SYN / "binary.parquet").filter((pl.col("field") == "slow") & (pl.col("p_idle") == 0.3))
    h = pl.read_parquet(SYN / "hawkes.parquet")
    c = pl.read_parquet(SYN / "content.parquet")
    ax = axes[0]
    for mode, mk, lab in (("gibbs", "o", "Curie–Weiss (equilibrium)"), ("async", "s", "asynchronous Glauber"), ("delay", "^", "delayed reads (2–8 min)")):
        d = b.filter((pl.col("mode") == mode) & (pl.col("outages")) & (pl.col("variant") == "auto")).with_columns(pl.col("g_true").alias("truth"))
        g = med_iqr(d, "J", "g")
        ax.errorbar(g["t"], g["m"], yerr=[g["m"] - g["q1"], g["q3"] - g["m"]], fmt=mk + "-", color=COL["activity"] if mode != "delay" else MUTED,
                    ms=4, lw=1.2, capsize=0, label=lab, alpha=0.95 if mode != "async" else 0.6)
    d = b.filter((pl.col("mode") == "gibbs") & (pl.col("outages")) & (pl.col("variant") == "none")).with_columns(pl.col("g_true").alias("truth"))
    g = med_iqr(d, "J", "g")
    ax.plot(g["t"], g["m"], "x--", color="#e34948", ms=4, lw=1, label="stalls not masked")
    ax.plot([0, 0.6], [0, 0.6], color=INK2, lw=0.8, ls=":")
    ax.set_xlabel("true loop gain g"); ax.set_ylabel("daily dial (median, IQR)")
    ax.set_title("(a) activity, schedules + stalls", loc="left", fontsize=8, color=INK)
    ax.legend(fontsize=6, loc="upper left")
    ax = axes[1]
    for tau, mk in ((20.0, "o"), (180.0, "^")):
        d = h.filter((pl.col("tau") == tau) & (pl.col("variant") == "auto")).with_columns(pl.col("g_DC").alias("truth"))
        g = med_iqr(d, "n_x", "g")
        ax.errorbar(g["t"], g["m"], yerr=[g["m"] - g["q1"], g["q3"] - g["m"]], fmt=mk + "-", color=COL["talk"] if tau < 100 else MUTED, ms=4, lw=1.2,
                    label=f"Hawkes kernel τ = {int(tau)} s")
    ax.plot([0, 0.7], [0, 0.7], color=INK2, lw=0.8, ls=":")
    ax.set_xlabel("true DC cross gain n_x/(1−n_s)"); ax.set_title("(b) talk spins (Hawkes)", loc="left", fontsize=8, color=INK)
    ax.legend(fontsize=6, loc="upper left")
    ax = axes[2]
    for exo, var, ls, lab in ((0.0, "F2", "-", "no time-varying field"), (1.0, "F1", "--", "exogenous field, F1"), (1.0, "F2", "-", "exogenous field, F2")):
        d = c.filter((pl.col("exo") == exo) & (pl.col("variant") == var) & (pl.col("noise") == 1.2)).with_columns(pl.col("g_true").alias("truth"))
        g = med_iqr(d, "J", "g")
        ax.errorbar(g["t"], g["m"], yerr=[g["m"] - g["q1"], g["q3"] - g["m"]], fmt="o" + ls, color=COL["content"] if exo == 0 else ("#4a3aa7" if var == "F2" else MUTED),
                    ms=4, lw=1.2, label=lab)
    ax.plot([0, 0.75], [0, 0.75], color=INK2, lw=0.8, ls=":")
    ax.set_xlabel("true loop gain g = βJ₀/n"); ax.set_title("(c) content, O(32) soft spins", loc="left", fontsize=8, color=INK)
    ax.legend(fontsize=6, loc="upper left")
    for a in axes:
        a.set_ylim(-0.25, 0.85)


def fig_synthetic():
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.4), sharey=True)
    synthetic_panels(axes)
    fig.tight_layout()
    save(fig, C.FIG / "fig_synthetic.png")


def timeline(daily, cal, axes, chans=("activity", "talk", "content"), compact=False):
    days = cal.sort("pt_date")["pt_date"].to_list()
    idx = {d: i for i, d in enumerate(days)}
    for ax, ch in zip(axes, chans):
        d = daily.filter((pl.col("channel") == ch) & (pl.col("variant") == PRIM[ch]) & (pl.col("flag") == "ok")).sort("pt_date")
        x = np.array([idx[v] for v in d["pt_date"]])
        # regime bands
        regs = cal.sort("pt_date")["regime"].to_list()
        start = 0
        for i in range(1, len(regs) + 1):
            if i == len(regs) or regs[i] != regs[start]:
                ax.axvspan(start - 0.5, i - 0.5, color=SHADE.get(regs[start], "#f6f5f2"), lw=0, zorder=0)
                if not compact or ch == chans[0]:
                    ax.text((start + i) / 2, 1.02, f"regime {regs[start]}", transform=ax.get_xaxis_transform(), ha="center", fontsize=6, color=MUTED)
                start = i
        gs = cal.sort("pt_date")["goal_no"].to_list()
        for i in range(1, len(gs)):
            if gs[i] != gs[i - 1]:
                ax.axvline(i - 0.5, color=GRID, lw=0.5, zorder=1)
        lo, hi = d["lo"].to_numpy(), d["hi"].to_numpy()
        g = d["g"].to_numpy()
        ax.vlines(x, np.clip(lo, -0.6, 1), np.clip(hi, -0.6, 1), color=COL[ch], alpha=0.25, lw=0.8, zorder=2)
        ax.plot(x, g, "o", ms=2.2, color=COL[ch], zorder=3)
        # per-period random-effects mean as a step
        for gg in sorted(set(gs)):
            dd = d.filter(pl.col("goal_no") == gg)
            if dd.height:
                xi = [idx[v] for v in dd["pt_date"]]
                w = 1 / np.maximum(dd["se"].to_numpy(), 1e-3) ** 2
                ax.hlines(float((w * dd["g"].to_numpy()).sum() / w.sum()), min(xi) - 0.4, max(xi) + 0.4, color=INK, lw=1.2, zorder=4)
        ax.axhline(0, color=MUTED, lw=0.6)
        ax.axhline(0.8, color="#e34948", lw=0.6, ls="--")
        ax.set_ylim(-0.6, 1.02)
        ax.set_ylabel(f"{ch} g", color=INK2)
        ax.grid(False)
    lab = [(i, f"#{g}") for i, (g, gp) in enumerate(zip(cal.sort('pt_date')['goal_no'].to_list(), [None] + cal.sort('pt_date')['goal_no'].to_list()[:-1])) if g != gp]
    keep = [lab[k] for k in range(0, len(lab), 3)]
    axes[-1].set_xticks([k for k, _ in keep]); axes[-1].set_xticklabels([t for _, t in keep], fontsize=6)
    axes[-1].set_xlabel("non-holdout village days (goal period at its first day; vertical lines = goal changes)")


def fig_timeline(daily, cal):
    fig, axes = plt.subplots(3, 1, figsize=(7.2, 4.6), sharex=True)
    timeline(daily, cal, axes)
    axes[0].set_title("Daily dial g = 1 − 1/VR (dots, 90% intervals); period mean (black); red dashes g = 0.8", loc="left", fontsize=8, color=INK)
    fig.tight_layout()
    save(fig, C.FIG / "fig_timeline.png")


def fig_agreement(tab):
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.4))
    ax = axes[0]
    for ch, ref, mk in (("activity", "h19_active", "o"), ("talk", "h19_talk", "s")):
        ax.plot(tab[ref], tab[f"{ch}_none_fe"], mk, color=COL[ch], ms=4, label=ch)
    ax.plot([-0.1, 0.45], [-0.1, 0.45], color=INK2, lw=0.8, ls=":")
    ax.set_xlabel("H19 g_eq (5-day chunks)"); ax.set_ylabel("H25 daily dial, period mean (stalls kept)")
    ax.set_title("(a) same estimator, per day", loc="left", fontsize=8, color=INK); ax.legend(fontsize=6)
    ax = axes[1]
    ax.plot(tab["h03_n_talk"], tab["talk_auto_fe"], "s", color=COL["talk"], ms=4, label="talk")
    ax.plot(tab["h03_n_talk"], tab["activity_auto_fe"], "o", color=COL["activity"], ms=4, mfc="none", label="activity")
    ax.set_xlabel("H03 Hawkes n̂ (talk)"); ax.set_ylabel("H25 dial (stalls masked)")
    ax.set_title("(b) vs Hawkes branching ratio", loc="left", fontsize=8, color=INK); ax.legend(fontsize=6)
    ax = axes[2]
    nx, ns = tab["h03_nx_fast"].to_numpy(), tab["h03_ns_fast"].to_numpy()
    gm = 2 * 0.75 * nx / (1 + 1.5 * (nx + ns))
    ax.plot(gm, tab["talk_auto_fe"], "s", color=COL["talk"], ms=4)
    ax.plot([0, 0.35], [0, 0.35], color=INK2, lw=0.8, ls=":")
    ax.set_xlabel("ĝ_map from H03 fast n_x, n_s (w = 0.75)"); ax.set_ylabel("H25 talk dial")
    ax.set_title("(c) unfitted mapping", loc="left", fontsize=8, color=INK)
    fig.tight_layout()
    save(fig, C.FIG / "fig_agreement.png")


def fig_variants(daily):
    """Medians of daily dials by variant (sensitivity ladder)."""
    rows = []
    for ch, vs in (("activity", ["none", "auto", "lull", "h38_sched", "h38_exo", "b15", "b60", "sched"]),
                   ("talk", ["none", "auto", "lull", "h38_sched", "b15", "b60", "sched"]),
                   ("content", ["F1", "F2", "F3", "F2tod", "F2nodedup", "F2split"])):
        for v in vs:
            d = daily.filter((pl.col("channel") == ch) & (pl.col("variant") == v) & (pl.col("flag") == "ok"))["g"].drop_nulls()
            if len(d):
                rows.append((ch, v, float(d.median()), float(d.quantile(0.25)), float(d.quantile(0.75))))
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.2))
    for ax, ch in zip(axes, ("activity", "talk", "content")):
        r = [x for x in rows if x[0] == ch]
        y = np.arange(len(r))
        ax.hlines(y, [x[3] for x in r], [x[4] for x in r], color=COL[ch], lw=2, alpha=0.5)
        ax.plot([x[2] for x in r], y, "o", color=COL[ch], ms=4)
        ax.set_yticks(y); ax.set_yticklabels([x[1] for x in r], fontsize=6)
        ax.axvline(0, color=MUTED, lw=0.6)
        ax.set_title(ch, loc="left", fontsize=8, color=INK); ax.set_xlabel("daily g (median, IQR)")
    fig.tight_layout()
    save(fig, C.FIG / "fig_variants.png")


def fig_periods(daily, per, cal):
    for g in sorted(daily["goal_no"].unique().to_list()):
        d = daily.filter((pl.col("goal_no") == g) & (pl.col("flag") == "ok"))
        days = sorted(cal.filter(pl.col("goal_no") == g)["pt_date"].to_list())
        fig, ax = plt.subplots(figsize=(max(3.2, 0.32 * len(days) + 2.2), 2.4))
        x0 = {dd: i for i, dd in enumerate(days)}
        off = {"activity": -0.2, "talk": 0.0, "content": 0.2}
        for ch in ("activity", "talk", "content"):
            dc = d.filter((pl.col("channel") == ch) & (pl.col("variant") == PRIM[ch])).sort("pt_date")
            if not dc.height:
                continue
            x = np.array([x0[v] for v in dc["pt_date"]]) + off[ch]
            ax.vlines(x, np.clip(dc["lo"].to_numpy(), -0.8, 1.1), np.clip(dc["hi"].to_numpy(), -0.8, 1.1), color=COL[ch], lw=1.2, alpha=0.5)
            ax.plot(x, dc["g"], "o", ms=3.5, color=COL[ch], label=ch)
            ax.plot(x, dc["null_q95"], "_", ms=6, color=COL[ch], alpha=0.7)
        ax.axhline(0, color=MUTED, lw=0.6); ax.axhline(0.8, color="#e34948", lw=0.6, ls="--")
        step = max(1, len(days) // 12)
        ax.set_xticks(range(0, len(days), step)); ax.set_xticklabels([days[i][5:] for i in range(0, len(days), step)], fontsize=6, rotation=45)
        ax.set_ylim(-0.8, 1.1); ax.set_ylabel("daily dial g")
        ax.set_title(f"G{g:02d}: daily dial (dots, 90% CI); ticks = null 95th pct", loc="left", fontsize=7, color=INK)
        ax.legend(fontsize=6, ncol=3, loc="lower left")
        fig.tight_layout()
        out = C.HYP / f"goalperiod-subhypotheses/G{g:02d}/figures/G{g:02d}_dial.png"
        out.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out, bbox_inches="tight"); plt.close(fig)


def fig_summary(daily, cal, tab):
    """Page 1: (a) period-mean dial over time, three channels; (b) period dial vs N with mean-field size curves."""
    per = pl.read_parquet(C.OUT / "dial_period.parquet")
    post = json.loads((C.OUT / "results/posthoc.json").read_text())["PH1_size_scaling"]
    days = cal.sort("pt_date")
    idx = {d: i for i, d in enumerate(days["pt_date"].to_list())}
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(3.6, 1.85), gridspec_kw={"width_ratios": [1.45, 1]})
    regs = days["regime"].to_list(); start = 0
    for i in range(1, len(regs) + 1):
        if i == len(regs) or regs[i] != regs[start]:
            ax.axvspan(start - 0.5, i - 0.5, color=SHADE.get(regs[start], "#f6f5f2"), lw=0, zorder=0)
            ax.text((start + i) / 2, 0.97, f"{regs[start]}", transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=4.5, color=MUTED)
            start = i
    for ch in ("content", "talk", "activity"):
        d = daily.filter((pl.col("channel") == ch) & (pl.col("variant") == PRIM[ch]) & (pl.col("flag") == "ok"))
        ax.plot([idx[v] for v in d["pt_date"]], d["g"], "o", ms=0.8, color=COL[ch], alpha=0.35, zorder=2)
        p = per.filter((pl.col("channel") == ch) & (pl.col("variant") == PRIM[ch]))
        for r in p.iter_rows(named=True):
            xs = [idx[v] for v in days.filter(pl.col("goal_no") == r["goal_no"])["pt_date"]]
            ax.hlines(r["re"], min(xs) - 0.4, max(xs) + 0.4, color=COL[ch], lw=1.6, zorder=3)
        ax.text(1.01, float(p["re"].median()) + {"talk": 0.07, "activity": -0.05, "content": 0.0}[ch], ch, transform=ax.get_yaxis_transform(),
                fontsize=4.8, color=INK2, va="center")
    ax.axhline(0.8, color="#e34948", lw=0.7, ls="--"); ax.axhline(0, color=MUTED, lw=0.6)
    ax.set_ylim(-0.45, 1.0); ax.set_xlim(-1, len(idx)); ax.set_xticks([]); ax.grid(False)
    ax.set_xlabel("282 non-holdout days (regimes I–III)", fontsize=5)
    ax.set_ylabel("g = 1 − 1/VR", fontsize=5.5)
    ax.set_title("(a) days and period means", loc="left", fontsize=5.8, color=INK)
    Ns = np.linspace(2, 30, 200)
    for ch in ("activity", "talk", "content"):
        d = daily.filter((pl.col("channel") == ch) & (pl.col("variant") == PRIM[ch]) & (pl.col("flag") == "ok"))
        pm = d.group_by("goal_no").agg(pl.col("g").median(), pl.col("N").median())
        bx.plot(pm["N"], pm["g"], "o", ms=1.8, color=COL[ch], alpha=0.85)
        rho = post[ch]["median_rho"]
        bx.plot(Ns, (Ns - 1) * rho / (1 + (Ns - 1) * rho), color=COL[ch], lw=0.8, ls="--")
        bx.text(30.5, (29 * rho) / (1 + 29 * rho), f"ρ̄={rho:.2f}", fontsize=4.5, color=INK2, va="center")
    bx.axhline(0.8, color="#e34948", lw=0.7, ls="--")
    bx.set_xlim(1, 40); bx.set_ylim(-0.45, 1.0)
    bx.set_xlabel("agents per day N (period median)", fontsize=5)
    bx.set_title("(b) vs swarm size", loc="left", fontsize=5.8, color=INK)
    for a in (ax, bx):
        a.tick_params(labelsize=4.8, length=2, width=0.5)
        for sp in a.spines.values():
            sp.set_linewidth(0.5)
    fig.tight_layout(w_pad=0.6, pad=0.3)
    save(fig, C.FIG / "summary_obs.png")
    # page 2: synthetic recovery, column width
    fig, axes = plt.subplots(1, 3, figsize=(3.6, 1.5), sharey=True)
    synthetic_panels(axes)
    for a in axes:
        for ln in a.get_lines():
            ln.set_markersize(2.2); ln.set_linewidth(0.9)
    short = {"Curie–Weiss (equilibrium)": "CW equilibrium", "asynchronous Glauber": "async Glauber", "delayed reads (2–8 min)": "delayed reads",
             "stalls not masked": "stalls unmasked", "Hawkes kernel τ = 20 s": "τ = 20 s", "Hawkes kernel τ = 180 s": "τ = 180 s",
             "no time-varying field": "no field", "exogenous field, F1": "field, F1", "exogenous field, F2": "field, F2"}
    for a, t in zip(axes, ("(a) activity", "(b) talk (Hawkes)", "(c) content O(32)")):
        a.set_title(t, loc="left", fontsize=5.8, color=INK)
        h, l = a.get_legend_handles_labels()
        a.legend(h, [short.get(x, x) for x in l], fontsize=4.2, loc="upper left", handlelength=1.3, borderaxespad=0.2)
        a.tick_params(labelsize=4.8, length=2, width=0.5)
        a.xaxis.label.set_size(5); a.yaxis.label.set_size(5)
    axes[0].set_xlabel("true g"); axes[1].set_xlabel("true n_x/(1−n_s)"); axes[2].set_xlabel("true g = βJ₀/n")
    axes[0].set_ylabel("dial (median, IQR)")
    fig.tight_layout(w_pad=0.4, pad=0.3)
    save(fig, C.FIG / "summary_obs2.png")


def main():
    cal = C.calendar_nonholdout()
    fig_synthetic()
    if (C.OUT / "dial_daily.parquet").exists():
        daily = pl.read_parquet(C.OUT / "dial_daily.parquet")
        per = pl.read_parquet(C.OUT / "dial_period.parquet")
        tab = pl.read_parquet(C.OUT / "period_compare.parquet")
        fig_timeline(daily, cal)
        fig_agreement(tab)
        fig_variants(daily)
        fig_periods(daily, per, cal)
        fig_summary(daily, cal, tab)
    print("figures written")


if __name__ == "__main__":
    main()
