"""Figures for H03 (small PDFs in hypotheses/H03-self-excited-criticality/figures/).
Run after summarize.py: uv run python hypotheses/H03-self-excited-criticality/analysis/figures.py
"""
from __future__ import annotations

import datetime as dt

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

from common import (DATA, FIG, GRID, INK, INK2, MODE_COLORS, MODE_MARKERS, MODE_NAMES, hc)  # noqa: E402

plt.rcParams.update({"font.size": 7.5, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5,
                     "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
                     "lines.linewidth": 1.5, "pdf.fonttype": 42, "axes.titlesize": 8, "axes.titleweight": "bold"})
SET_COLORS = {"TALK": "#2a78d6", "ALL": "#eb6834"}
MODES = ["F", "I", "K", "M", "C", "P"]


def mode_legend(ax, loc="upper left", modes=MODES):
    hs = [plt.Line2D([], [], ls="", marker=MODE_MARKERS[m], color=MODE_COLORS[m], mec="white", mew=0.5, ms=6,
                     label=MODE_NAMES[m]) for m in modes]
    ax.legend(handles=hs, loc=loc, fontsize=6.5, handletextpad=0.3, borderaxespad=0.2)


def err(r, lo, hi):
    a, b = r.get(lo), r.get(hi)
    if a is None or b is None or not np.isfinite(a):
        return None
    b = b if np.isfinite(b) else r["n"] + 1.0
    return [[max(r["n"] - a, 0)], [max(b - r["n"], 0)]]


def fig_phase(tab, roll, rboot):
    fig, axs = plt.subplots(2, 2, figsize=(7.2, 6.0))
    for j, s in enumerate(("TALK", "ALL")):
        ax = axs[0, j]
        t = tab.filter(pl.col("set") == s)
        for r in t.iter_rows(named=True):
            m = r["mode"]
            lo, hi = ("n_boot_lo", "n_boot_hi") if r.get("n_boot_lo") is not None else ("n_prof_lo", "n_prof_hi")
            e = err(r, lo, hi)
            ax.errorbar(r["N_active"], r["n"], yerr=e, fmt="none", ecolor=MODE_COLORS[m], alpha=0.45, lw=0.8)
            ax.scatter(r["N_active"], r["n"], marker=MODE_MARKERS[m], c=MODE_COLORS[m], s=10 + 9 * r["hours"],
                       edgecolors="white", linewidths=0.5, zorder=3)
            ax.annotate(str(r["goal_no"]), (r["N_active"], r["n"]), xytext=(3, 2), textcoords="offset points",
                        fontsize=5.5, color=INK2)
        if roll is not None:
            b = roll.filter((pl.col("kind") == "block") & (pl.col("set") == s) & (pl.col("model") == "M1_B2")).sort("w0")
            jit = np.linspace(-0.6, 0.6, b.height)
            for k, r in enumerate(b.iter_rows(named=True)):
                xx = r["N_active"] + jit[k] * 0.5
                if rboot is not None:
                    bb = rboot.filter((pl.col("set") == s) & (pl.col("w0") == r["w0"]) & (pl.col("model") == "M1_B2"))["n"].to_numpy()
                    if len(bb):
                        ax.plot([xx] * 2, np.quantile(bb, [0.025, 0.975]), color=MODE_COLORS["P"], lw=0.6, alpha=0.5)
                ax.scatter([xx], [r["n"]], marker="*", s=14, color=MODE_COLORS["P"], alpha=0.7, zorder=2,
                           edgecolors="none")
        ax.axhline(1.0, color=INK2, lw=0.6, ls=":")
        ax.axhline(0.5, color=INK2, lw=0.6, ls="--")
        ax.set_xscale("log"); ax.set_xticks([4, 7, 10, 15, 20, 30]); ax.set_xticklabels([4, 7, 10, 15, 20, 30])
        ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        ax.set_ylim(-0.05, 1.15)
        ax.set_xlabel("mean active agents per day, N"); ax.set_ylabel("branching ratio n (M1, B2)")
        ax.set_title(f"{s}: n̂ vs N (size = h/day; ★ = #51 blocks)")
    # bottom: N x hours plane coloured by n (sequential, one hue), marker = mode
    cmap = plt.get_cmap("Blues")
    rng = np.random.default_rng(0)
    for j, s in enumerate(("TALK", "ALL")):
        ax = axs[1, j]
        t = tab.filter(pl.col("set") == s)
        for r in t.iter_rows(named=True):
            jx = np.exp(rng.normal(0, 0.04)); jy = rng.normal(0, 0.12)
            ax.scatter(r["N_active"] * jx, r["hours"] + jy, marker=MODE_MARKERS[r["mode"]], c=[cmap(0.15 + 0.85 * min(r["n"], 1))],
                       s=55, edgecolors=MODE_COLORS[r["mode"]], linewidths=1.0, zorder=3)
            ax.annotate(f"{r['goal_no']}", (r["N_active"] * jx, r["hours"] + jy), xytext=(4, -2), textcoords="offset points",
                        fontsize=5.5, color=INK2)
        ax.set_xscale("log"); ax.set_xticks([4, 7, 10, 15, 20, 30]); ax.set_xticklabels([4, 7, 10, 15, 20, 30])
        ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        ax.set_xlabel("mean active agents per day, N"); ax.set_ylabel("hours per day (jittered)")
        ax.set_title(f"{s}: N × hours plane, fill = n̂")
        sm = plt.cm.ScalarMappable(cmap=matplotlib.colors.LinearSegmentedColormap.from_list("b", [cmap(0.15), cmap(1.0)]),
                                   norm=plt.Normalize(0, 1))
        cb = fig.colorbar(sm, ax=ax, fraction=0.04, pad=0.02); cb.set_label("n", fontsize=7); cb.outline.set_visible(False)
    hs = [plt.Line2D([], [], ls="", marker=MODE_MARKERS[m], color=MODE_COLORS[m], mec="white", mew=0.5, ms=6,
                     label=MODE_NAMES[m]) for m in MODES]
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.legend(handles=hs, loc="lower center", ncol=6, fontsize=6.5, handletextpad=0.3, columnspacing=1.0)
    fig.savefig(FIG / "phase_diagram.pdf"); plt.close(fig)


def fig_ladder(tab, guard):
    rungs = [("n_B0", "B0 const"), ("n_B1", "B1 day"), ("n", "B2 day×shape"), ("n_t30", "B2, τ≤30m"),
             ("n_B3_2h", "B3 2-h cells"), ("n_B3", "B3 30-min cells")]
    fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.7), gridspec_kw={"width_ratios": [1, 1, 1.25]})
    x = np.arange(len(rungs))
    for j, s in enumerate(("TALK", "ALL")):
        ax = axs[j]
        t = tab.filter(pl.col("set") == s)
        for r in t.iter_rows(named=True):
            y = [min(r[c], 1.2) if r[c] is not None else np.nan for c, _ in rungs]
            ax.plot(x, y, color=MODE_COLORS[r["mode"]], lw=0.6, alpha=0.5)
        med = [float(t[c].median()) for c, _ in rungs]
        ax.plot(x, med, color=INK, lw=2.0, marker="o", ms=4, label="median")
        ax.set_xticks(x); ax.set_xticklabels([l for _, l in rungs], rotation=40, ha="right", fontsize=6.5)
        ax.set_ylim(-0.05, 1.22); ax.set_ylabel("n̂ (real data)"); ax.set_title(f"{s}: baseline ladder")
        ax.legend(loc="upper right", fontsize=6.5)
    ax = axs[2]
    if guard is not None:
        mm = [("M1_B0", "B0"), ("M1_B2", "B2"), ("M1_B2_t30", "B2 τ≤30m"), ("M1_B3_2h", "B3 2h"), ("M1_B3", "B3 30m")]
        scen = [("n0", 0.0, "#52514e"), ("n0_fine", 0.0, "#eb6834"), ("n06", 0.6, "#2a78d6"), ("n09", 0.9, "#4a3aa7")]
        lbl = {"n0": "n=0, B2-type baseline", "n0_fine": "n=0, real 10-min rate", "n06": "n=0.6", "n09": "n=0.9"}
        for k, (sc, nt, colr) in enumerate(scen):
            for i, (m, _) in enumerate(mm):
                v = guard.filter((pl.col("scenario") == sc) & (pl.col("model") == m))["n_hat"].to_numpy()
                if len(v) == 0:
                    continue
                xi = i + (k - 1.5) * 0.17
                ax.plot([xi, xi], np.quantile(v, [0.1, 0.9]), color=colr, lw=1.0)
                ax.scatter([xi], [np.median(v)], color=colr, s=12, zorder=3, label=lbl[sc] if i == 1 else None)
            ax.axhline(nt, color=colr, lw=0.6, ls=":")
        ax.set_xticks(range(len(mm))); ax.set_xticklabels([l for _, l in mm], rotation=40, ha="right", fontsize=6.5)
        ax.set_ylabel("n̂ on synthetic data (median, 10–90%)"); ax.set_title("synthetic guard (TALK+ALL)")
        ax.legend(fontsize=6, loc="upper left")
        ax.set_ylim(-0.05, 1.22)
    fig.tight_layout(); fig.savefig(FIG / "baseline_ladder_and_guard.pdf"); plt.close(fig)


def fig_rolling(roll, rboot):
    fig, axs = plt.subplots(3, 1, figsize=(6.0, 5.6), sharex=True, gridspec_kw={"height_ratios": [1.5, 1.2, 0.8]})
    d = lambda col: [dt.date.fromisoformat(v) + dt.timedelta(days=2) for v in col]
    for s in ("TALK", "ALL"):
        r = roll.filter((pl.col("kind") == "rolling") & (pl.col("set") == s))
        m1 = r.filter(pl.col("model") == "M1_B2").sort("w0")
        lo = np.where(np.isfinite(m1["n_prof_lo"].to_numpy()), m1["n_prof_lo"].to_numpy(), np.nan)
        hi = np.where(np.isfinite(m1["n_prof_hi"].to_numpy()), m1["n_prof_hi"].to_numpy(), np.nan)
        x = d(m1["first_date"].to_list())
        axs[0].fill_between(x, lo, hi, color=SET_COLORS[s], alpha=0.15, lw=0)
        axs[0].plot(x, m1["n"], color=SET_COLORS[s], label=f"{s} n̂ (B2), profile 95%")
        t30 = r.filter(pl.col("model") == "M1_B2_t30") if "M1_B2_t30" in r["model"].to_list() else None
        b0 = r.filter(pl.col("model") == "M1_B0").sort("w0")
        axs[0].plot(d(b0["first_date"].to_list()), b0["n"], color=SET_COLORS[s], ls=":", lw=1.0, label=f"{s} n̂ (B0, naive)")
        if rboot is not None:
            blk = roll.filter((pl.col("kind") == "block") & (pl.col("set") == s) & (pl.col("model") == "M1_B2")).sort("w0")
            for row in blk.iter_rows(named=True):
                bb = rboot.filter((pl.col("set") == s) & (pl.col("w0") == row["w0"]) & (pl.col("model") == "M1_B2"))["n"].to_numpy()
                xx = dt.date.fromisoformat(row["first_date"]) + dt.timedelta(days=2)
                if len(bb):
                    axs[0].plot([xx, xx], np.quantile(bb, [0.025, 0.975]), color=SET_COLORS[s], lw=2.5, alpha=0.5)
        m3 = r.filter(pl.col("model") == "M3_sc").sort("w0").with_columns(
            sf=pl.col("self_10") + pl.col("self_30") + pl.col("self_100") + pl.col("self_300"),
            xf=(pl.col("cross_10") + pl.col("cross_30") + pl.col("cross_100") + pl.col("cross_300")) * (pl.col("m_bar") - 1))
        axs[1].plot(d(m3["first_date"].to_list()), m3["sf"], color=SET_COLORS[s], label=f"{s} n_self (τ≤300 s)")
        axs[1].plot(d(m3["first_date"].to_list()), m3["xf"], color=SET_COLORS[s], ls="--", label=f"{s} n_cross (τ≤300 s)")
    nn = roll.filter((pl.col("kind") == "rolling") & (pl.col("set") == "ALL") & (pl.col("model") == "M1_B2")).sort("w0")
    axs[2].plot(d(nn["first_date"].to_list()), nn["N_active"], color=INK)
    axs[0].axhline(1, color=INK2, lw=0.6, ls=":"); axs[0].set_ylim(0, 1.1)
    axs[0].set_ylabel("branching ratio n"); axs[0].legend(fontsize=6, ncol=2, loc="lower left")
    axs[0].set_title("#51 private-role era, 5-day windows (centre date); thick bars = block bootstrap 95%")
    axs[1].set_ylabel("M3 fast self / cross"); axs[1].legend(fontsize=6, ncol=2)
    axs[2].set_ylabel("active agents N"); axs[2].set_xlabel("window centre (PT date); tail from 09-07 held out")
    fig.autofmt_xdate(); fig.tight_layout(); fig.savefig(FIG / "rolling51.pdf"); plt.close(fig)


def fig_selfcross(tab):
    fig, axs = plt.subplots(1, 2, figsize=(7.0, 3.0))
    for j, s in enumerate(("TALK", "ALL")):
        ax = axs[j]
        t = tab.filter(pl.col("set") == s)
        for r in t.iter_rows(named=True):
            ax.scatter(r["n_self_fast"], r["n_cross_fast"], marker=MODE_MARKERS[r["mode"]], c=MODE_COLORS[r["mode"]], s=28,
                       edgecolors="white", linewidths=0.5, zorder=3)
            if r.get("n_cross_fast_boot_lo") is not None:
                ax.plot([r["n_self_fast"]] * 2, [r["n_cross_fast_boot_lo"], r["n_cross_fast_boot_hi"]],
                        color=MODE_COLORS[r["mode"]], lw=0.6, alpha=0.5)
            ax.annotate(str(r["goal_no"]), (r["n_self_fast"], r["n_cross_fast"]), xytext=(3, 2), textcoords="offset points", fontsize=5.5, color=INK2)
        lim = [0, max(0.9, float(t["n_self_fast"].max()) * 1.05)]
        ax.plot(lim, lim, color=INK2, lw=0.6, ls=":")
        ax.set_xlabel("own-loop excitation n_self, τ ≤ 300 s (M3)"); ax.set_ylabel("social excitation n_cross = (m̄−1)·n_c, τ ≤ 300 s")
        ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        ax.set_title(f"{s}: who triggers whom")
        if j == 0:
            mode_legend(ax)
    fig.tight_layout(); fig.savefig(FIG / "self_vs_cross.pdf"); plt.close(fig)


def fig_kernels(fits):
    taus = hc.GRID_TAUS
    fig, axs = plt.subplots(1, 2, figsize=(7.0, 2.8), sharey=True)
    for j, s in enumerate(("TALK", "ALL")):
        ax = axs[j]
        g = fits.filter((pl.col("model") == "M2_grid") & (pl.col("set") == s))
        for m in ("F", "I", "K", "M", "C", "P"):
            sub = g.filter(pl.col("mode") == m)
            if sub.height == 0:
                continue
            W = np.column_stack([sub[f"ker_{int(t)}"].to_numpy() for t in taus])
            ax.plot(taus, np.median(W, 0), color=MODE_COLORS[m], marker=MODE_MARKERS[m], ms=4, label=f"{m} (k={sub.height})")
        ax.set_xscale("log"); ax.set_xlabel("kernel component timescale τ_m (s)"); ax.set_ylabel("median weight α_m")
        ax.set_title(f"{s}: sum-of-exponentials kernel (M2)")
        ax.legend(fontsize=6)
    fig.tight_layout(); fig.savefig(FIG / "kernels.pdf"); plt.close(fig)


def fig_cascades(tab):
    p = DATA / "cascades.parquet"
    if not p.exists():
        return
    c = pl.read_parquet(p)
    fig, axs = plt.subplots(1, 3, figsize=(7.4, 2.7))
    rec = c.filter((pl.col("source") == "reconstructed") & (pl.col("set") == "TALK")).join(
        tab.filter(pl.col("set") == "TALK").select("goal_no", "n"), on="goal_no")
    ax = axs[0]
    for (lo, hi, colr, lab) in [(0, 0.5, "#1baf7a", "n̂<0.5"), (0.5, 0.65, "#2a78d6", "0.5≤n̂<0.65"), (0.65, 2, "#4a3aa7", "n̂≥0.65")]:
        sub = rec.filter((pl.col("n") >= lo) & (pl.col("n") < hi))
        if sub.height == 0:
            continue
        sizes = np.repeat(sub["size"].to_numpy(), sub["count"].to_numpy())
        v = np.sort(np.unique(sizes))
        ccdf = np.array([(sizes >= k).mean() for k in v])
        ax.loglog(v, ccdf, color=colr, label=f"{lab}", marker=".", ms=2, lw=1)
        nbar = float(np.average(sub["n"].to_numpy(), weights=sub["count"].to_numpy()))
        ss = np.arange(1, 400)
        pm = hc.borel_pmf(ss, nbar); cc = 1 - np.concatenate([[0], np.cumsum(pm)[:-1]])
        ax.loglog(ss, cc, color=colr, ls=":", lw=0.8)
    ss = np.arange(1, 300)
    ax.loglog(ss, ss ** -0.5, color=INK2, ls="--", lw=0.8, label="s^(−1/2) CCDF (critical)")
    ax.set_ylim(1e-5, 1.2); ax.set_xlabel("reconstructed cascade size s"); ax.set_ylabel("P(S ≥ s)")
    ax.set_title("TALK: cascades (dots: Borel(n̄))"); ax.legend(fontsize=5.5)
    for j, s in enumerate(("TALK", "ALL")):
        ax = axs[1 + j]
        b = c.filter((pl.col("set") == s) & (pl.col("gap") == 60.0))
        for src, colr, lab in [("data", INK, "data"), ("sim_hawkes", "#2a78d6", "Hawkes sim (M1 B2)"),
                               ("sim_poisson", "#eb6834", "Poisson sim (P B2)")]:
            x = b.filter(pl.col("source") == src)
            sizes = np.repeat(x["size"].to_numpy(), x["count"].to_numpy())
            v = np.sort(np.unique(sizes)); ccdf = np.array([(sizes >= k).mean() for k in v])
            ax.loglog(v, ccdf, color=colr, label=lab, lw=1.2 if src == "data" else 1.0)
        ax.set_xlabel("burst size (gap ≤ 60 s)"); ax.set_ylabel("P(S ≥ s)"); ax.set_title(f"{s}: bursts (pooled periods)")
        ax.legend(fontsize=6); ax.set_ylim(1e-5, 1.2)
    fig.tight_layout(); fig.savefig(FIG / "cascades.pdf"); plt.close(fig)


def fig_diag(tab):
    fig, axs = plt.subplots(1, 2, figsize=(7.0, 2.9))
    ax = axs[0]
    for s in ("TALK", "ALL"):
        t = tab.filter(pl.col("set") == s)
        ax.scatter(t["ks_D_P"], t["ks_D"], s=14, color=SET_COLORS[s], label=s, edgecolors="white", linewidths=0.4)
    lim = [0, float(max(tab["ks_D_P"].max(), tab["ks_D"].max())) * 1.05]
    ax.plot(lim, lim, color=INK2, lw=0.6, ls=":")
    ax.set_xlabel("KS D, inhomogeneous Poisson (P B2)"); ax.set_ylabel("KS D, Hawkes (M1 B2)")
    ax.set_title("time-rescaling KS distance per period"); ax.legend(fontsize=6.5)
    ax = axs[1]
    cols = [("cv_B2", "Hawkes−Poisson, B2"), ("cv_B3_2h", "…, B3 2h"), ("cv_B3", "…, B3 30m"), ("cv_cross", "M3 cross−self")]
    for i, (c, lab) in enumerate(cols):
        for k, s in enumerate(("TALK", "ALL")):
            v = tab.filter(pl.col("set") == s)[c].drop_nulls().to_numpy()
            xx = i + (k - 0.5) * 0.3 + np.random.default_rng(i).normal(0, 0.03, len(v))
            ax.scatter(xx, v, s=6, color=SET_COLORS[s], alpha=0.7, label=s if i == 0 else None)
            ax.plot([i + (k - 0.5) * 0.3 - 0.1, i + (k - 0.5) * 0.3 + 0.1], [np.median(v)] * 2, color=INK, lw=1.5)
    ax.axhline(0, color=INK2, lw=0.6)
    ax.set_xticks(range(len(cols))); ax.set_xticklabels([l for _, l in cols], fontsize=6.5)
    ax.set_ylabel("held-out Δ log-lik per event (nats)"); ax.set_title("day-blocked CV (5 folds)")
    ax.set_yscale("symlog", linthresh=0.01); ax.legend(fontsize=6.5)
    fig.tight_layout(); fig.savefig(FIG / "diagnostics.pdf"); plt.close(fig)


def fig_segments():
    p = DATA / "segment_table.parquet"
    if not p.exists():
        return
    t = pl.read_parquet(p)
    fig, axs = plt.subplots(1, 3, figsize=(7.4, 2.9), gridspec_kw={"width_ratios": [1.2, 1.2, 1]})
    for j, s in enumerate(("TALK", "ALL")):
        ax = axs[j]
        x = t.filter(pl.col("set") == s)
        for r in x.iter_rows(named=True):
            m = r["mode"]; xx = r["N_active"]
            if r["se"] is not None and np.isfinite(r["se"]):
                ax.plot([xx, xx], [r["n"] - 1.96 * r["se"], r["n"] + 1.96 * r["se"]], color=MODE_COLORS[m], lw=0.5, alpha=0.4)
            ax.scatter([xx], [r["n"]], marker=MODE_MARKERS[m], facecolors="none", edgecolors=MODE_COLORS[m], s=18, lw=0.8, zorder=3)
            sh = r.get("n_shrunk")
            if sh is not None and np.isfinite(sh):
                ax.plot([xx, xx], [r["n"], sh], color=MODE_COLORS[m], lw=0.6, ls=":")
                ax.scatter([xx], [sh], marker=MODE_MARKERS[m], color=MODE_COLORS[m], s=9, zorder=4, edgecolors="none")
        ax.set_xscale("log"); ax.set_xticks([4, 7, 10, 15, 20, 30]); ax.set_xticklabels([4, 7, 10, 15, 20, 30])
        ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        ax.set_ylim(-0.1, 1.2); ax.axhline(1, color=INK2, lw=0.6, ls=":")
        ax.set_xlabel("active agents N (segment mean)"); ax.set_ylabel("n̂ per segment (M1, B2)")
        ax.set_title(f"{s}: segments (open), pooled (filled)", fontsize=7)
    ax = axs[2]
    for s in ("TALK", "ALL"):
        x = t.filter((pl.col("set") == s) & (pl.col("goal_no") == 51)).sort("seg")
        se = x["se"].fill_null(np.nan).to_numpy()
        ax.errorbar(x["N_active"], x["n"], yerr=1.96 * se, fmt="o", ms=3, color=SET_COLORS[s], lw=0.8, label=s, capsize=0)
        if "n_shrunk" in x.columns:
            ax.plot(x["N_active"], x["n_shrunk"], color=SET_COLORS[s], lw=0.8, ls="--")
    ax.axhline(1, color=INK2, lw=0.6, ls=":"); ax.set_ylim(-0.1, 1.2)
    ax.set_xlabel("active agents N"); ax.set_ylabel("n̂"); ax.set_title("#51 segments (roster steps)", fontsize=7)
    ax.legend(fontsize=6.5)
    hs = [plt.Line2D([], [], ls="", marker=MODE_MARKERS[m], color=MODE_COLORS[m], ms=5, label=MODE_NAMES[m]) for m in MODES]
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    fig.legend(handles=hs, loc="lower center", ncol=6, fontsize=6, handletextpad=0.3, columnspacing=0.8)
    fig.savefig(FIG / "segments_phase.pdf"); plt.close(fig)


def main():
    FIG.mkdir(exist_ok=True)
    tab = pl.read_parquet(DATA / "period_table.parquet")
    fits = pl.read_parquet(DATA / "period_fits.parquet")
    roll = pl.read_parquet(DATA / "rolling51.parquet") if (DATA / "rolling51.parquet").exists() else None
    rboot = pl.read_parquet(DATA / "rolling51_boot.parquet") if (DATA / "rolling51_boot.parquet").exists() else None
    guard = pl.read_parquet(DATA / "synthetic_guard.parquet") if (DATA / "synthetic_guard.parquet").exists() else None
    fig_phase(tab, roll, rboot)
    fig_ladder(tab, guard)
    if roll is not None:
        fig_rolling(roll, rboot)
    fig_selfcross(tab)
    fig_kernels(fits)
    fig_cascades(tab)
    fig_diag(tab)
    fig_segments()
    print("figures written to", FIG)


if __name__ == "__main__":
    main()
