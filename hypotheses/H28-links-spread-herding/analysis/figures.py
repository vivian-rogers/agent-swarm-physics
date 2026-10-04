"""H28 figures: synthetic validation, per-period forest, kernel/dose, counterfactual, NE09 latency, one-page summary,
and the observables figure for the summary page.

  uv run python hypotheses/H28-links-spread-herding/analysis/figures.py
"""
from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scheme"))
from h28lib import ALL_PERIODS, FIG, OUT, POST_NE09, PRE_NE09, gname  # noqa: E402

BLUE, ORANGE, AQUA, GRAY = "#2a78d6", "#eb6834", "#1baf7a", "#8a8984"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e6e5e0"
plt.rcParams.update({"font.size": 8, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
                     "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True, "legend.frameon": False,
                     "pdf.fonttype": 42})
ROLE_LAB = {"candidate": "named", "herding": "herding", "contrast": "own-artifact"}
SCEN_LAB = {"S0_null": "S0 null", "S1_contagion": "S1 contagion", "S2_drive": "S2 drive", "S3_occupancy": "S3 occupancy",
            "S4_contagion+drive": "S4 contagion+drive", "S5_revisits": "S5 revisits", "S6_complex": "S6 complex",
            "S7_drive_2rooms": "S7 drive, 2 rooms", "S8_contagion_2rooms": "S8 contagion, 2 rooms",
            "S9_drive_long": "S9 long drive", "S10_announce": "S10 announce links", "S11_announce_2rooms": "S11 announce, 2 rooms"}
TRUE_LINK = {"S1_contagion", "S4_contagion+drive", "S6_complex", "S8_contagion_2rooms"}


def load_real():
    import polars as pl
    df = pl.read_parquet(OUT / "results_round1.parquet")
    rs = {g: json.loads((OUT / gname(g) / "round1.json").read_text()) for g in ALL_PERIODS if (OUT / gname(g) / "round1.json").exists()}
    return df, rs


def fig_synthetic():
    rec = json.loads((OUT / "synthetic/recovery.json").read_text())
    cf = json.loads((OUT / "synthetic/counterfactual.json").read_text())
    by = collections.defaultdict(list)
    for r in rec:
        by[r["scen"]].append(r)
    scen = [s for s in SCEN_LAB if s in by]
    fig, ax = plt.subplots(2, 2, figsize=(7.2, 5.6))
    # (a) P1 rate and P1 + lead-contrast rate
    y = np.arange(len(scen))[::-1]
    p1 = [np.mean([(r["kappa"] > 0) and (r["z_shift"] >= 2) and (r["p"] < 0.05) for r in by[s]]) for s in scen]
    p12 = [np.mean([(r["kappa"] > 0) and (r["z_shift"] >= 2) and (r["p"] < 0.05) and (r["diff_lead"] > 0) and (r["p_diff_lead"] < 0.05)
                    for r in by[s]]) for s in scen]
    a = ax[0, 0]
    a.barh(y + 0.18, p1, height=0.34, color=BLUE, label="P1 (κ>0, p<.05, z_shift≥2)")
    a.barh(y - 0.18, p12, height=0.34, color=ORANGE, label="P1 and lead contrast (P2a)")
    a.set_yticks(y, [SCEN_LAB[s] + (" *" if s in TRUE_LINK else "") for s in scen])
    a.axvline(0.05, color=GRAY, lw=0.8, ls="--")
    a.set_xlim(0, 1)
    a.set_xlabel("share of runs called 'link contagion'")
    a.set_title("(a) calls by scenario (* = true link effect)", loc="left", fontsize=8)
    a.legend(loc="lower right", fontsize=6.5)
    # (b) kappa-hat by scenario
    a = ax[0, 1]
    for yy, s in zip(y, scen):
        k = np.array([r["kappa"] for r in by[s]])
        a.scatter(k, np.full(len(k), yy) + np.random.default_rng(0).uniform(-0.2, 0.2, len(k)), s=6,
                  color=BLUE if s in TRUE_LINK else GRAY, alpha=0.7, lw=0)
    a.axvline(0, color=INK2, lw=0.8)
    a.axvline(np.log(3), color=ORANGE, lw=0.8, ls="--")
    a.text(np.log(3), y.max() + 0.6, "true κ = ln 3", color=INK2, fontsize=6.5, ha="center")
    a.set_yticks(y, ["" for _ in scen])
    a.set_xlabel("κ̂ (primary)")
    a.set_title("(b) κ̂ per run", loc="left", fontsize=8)
    # (c) lambda recovery
    a = ax[1, 0]
    for s in scen:
        lt = [r["truth"]["lam"] for r in by[s]]
        lh = [r["lam"] for r in by[s]]
        a.scatter(lt, lh, s=7, color=BLUE if s in TRUE_LINK else GRAY, alpha=0.6, lw=0)
    mx = max(0.12, max(r["truth"]["lam"] for r in rec))
    a.plot([0, mx], [0, mx], color=INK2, lw=0.8, ls="--")
    a.set_xlabel("true λ (extra arrivals per exposure)")
    a.set_ylabel("estimated λ")
    a.set_title("(c) infection rate per exposure", loc="left", fontsize=8)
    # (d) counterfactual
    a = ax[1, 1]
    cols = {"S1_contagion": BLUE, "S2_drive": GRAY, "S4_contagion+drive": ORANGE}
    for s, c in cols.items():
        L = [x for x in cf if x["scen"] == s]
        if L:
            a.scatter([x["true"]["peak_occ"] for x in L], [x["est"]["peak_occ"] for x in L], s=14, color=c, label=SCEN_LAB[s], lw=0)
    a.plot([0.5, 1.1], [0.5, 1.1], color=INK2, lw=0.8, ls="--")
    a.set_xlabel("true peak-occupancy ratio, links off / on")
    a.set_ylabel("simulated ratio (fitted model)")
    a.set_title("(d) counterfactual: removing links", loc="left", fontsize=8)
    a.legend(fontsize=6.5, loc="upper left")
    fig.tight_layout()
    fig.savefig(FIG / "synthetic_validation.pdf")
    plt.close(fig)


def forest(a, df, show_null=True, label=True):
    import polars as pl
    d = df.sort(["role", "goal"], descending=[False, False])
    order = [r for role in ("candidate", "herding", "contrast") for r in d.filter(pl.col("role") == role).iter_rows(named=True)]
    y = np.arange(len(order))[::-1]
    for yy, r in zip(y, order):
        if show_null:
            a.plot([r["null_mean"] - 2 * (r["kappa"] - r["null_mean"]) / r["z_shift"] if r["z_shift"] else r["null_mean"],
                    r["null_mean"] + 2 * (r["kappa"] - r["null_mean"]) / r["z_shift"] if r["z_shift"] else r["null_mean"]],
                   [yy, yy], color=GRID, lw=6, solid_capstyle="butt")
        c = BLUE if r["verdict"] == "supported" else ORANGE if r["verdict"] == "weak" else GRAY
        a.plot([r["kappa"] - 1.96 * r["se"], r["kappa"] + 1.96 * r["se"]], [yy, yy], color=c, lw=1.4)
        a.scatter([r["kappa"]], [yy], s=18, color=c, zorder=3, edgecolor="white", lw=0.8)
    a.axvline(0, color=INK2, lw=0.8)
    a.set_yticks(y, [f"#{r['goal']} ({ROLE_LAB[r['role']]})" if label else f"#{r['goal']}" for r in order])
    return order


def fig_forest(df):
    fig, a = plt.subplots(figsize=(4.2, 4.2))
    forest(a, df)
    a.set_xlabel("κ̂: log hazard ratio of switching to X, ≥1 visible link to X in last 60 min")
    a.set_title("Link exposure vs switch hazard (gray band: link time-shift null ±2 sd)", loc="left", fontsize=7.5)
    fig.tight_layout()
    fig.savefig(FIG / "periods_forest.pdf")
    plt.close(fig)


def fig_kernel_dose(cross):
    fig, ax = plt.subplots(1, 2, figsize=(6.4, 2.6))
    k = cross["kernel"]
    labs = ["0–15 min", "15–60 min", "60–240 min"]
    vals = [k["k015"], k["k1560"], k["k60240"]]
    a = ax[0]
    for i, v in enumerate(vals):
        a.errorbar(i, v["b"], yerr=1.96 * v["se"], fmt="o", color=BLUE, ms=4, capsize=2)
    a.axhline(0, color=INK2, lw=0.8)
    a.set_xticks(range(3), labs)
    a.set_ylabel("pooled coefficient on log(1+links)")
    a.set_title("(a) kernel: when do visible links act?", loc="left", fontsize=8)
    d = cross["P4"]
    a = ax[1]
    labs = ["1 link,\n1 sender", "2 links,\n1 sender", "3+ links,\n1 sender", "≥2\nsenders"]
    for i, kk in enumerate(("d11", "d12", "d13", "dS2")):
        v = d[kk]
        a.errorbar(i, np.exp(v["b"]), yerr=[[np.exp(v["b"]) - np.exp(v["b"] - 1.96 * v["se"])], [np.exp(v["b"] + 1.96 * v["se"]) - np.exp(v["b"])]],
                   fmt="o", color=BLUE if kk != "dS2" else ORANGE, ms=4, capsize=2)
    a.axhline(1, color=INK2, lw=0.8)
    a.set_xticks(range(4), labs)
    a.set_ylabel("pooled hazard ratio vs no link")
    a.set_title("(b) dose: simple vs complex contagion", loc="left", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "kernel_dose.pdf")
    plt.close(fig)


def cf_panel(a, df):
    import polars as pl
    d = df.filter(pl.col("tested") & pl.col("cf_f0").is_not_null()).sort("goal")
    x = np.arange(d.height)
    a.bar(x - 0.27, d["cf_f05"], width=0.26, color=AQUA, label="half the links")
    a.bar(x, d["cf_cap"], width=0.26, color=BLUE, label="≤1 link/project/room/2 h")
    a.bar(x + 0.27, d["cf_f0"], width=0.26, color=ORANGE, label="no links")
    a.axhline(1, color=INK2, lw=0.8)
    a.set_xticks(x, [f"#{g}" for g in d["goal"]], rotation=0, fontsize=6.5)
    lo = max(0.0, float(np.nanmin(d["cf_f0"])) - 0.1)
    a.set_ylim(lo, 1.08)
    a.set_ylabel("simulated peak occupancy\n(relative to links as observed)")
    return d


def fig_counterfactual(df):
    fig, a = plt.subplots(figsize=(6.4, 2.6))
    cf_panel(a, df)
    a.legend(fontsize=6.5, ncol=3, loc="lower left")
    a.set_title("Counterfactual link throttling: peak number of agents on one project", loc="left", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "counterfactual.pdf")
    plt.close(fig)


def fig_latency(rs):
    fig, a = plt.subplots(figsize=(4.2, 2.6))
    lags = np.arange(2.5, 240, 5)
    for grp, col, lab in ((PRE_NE09, ORANGE, "pre-NE09 (#18, #19)"), (POST_NE09, BLUE, "post-NE09 (#24–#31)")):
        h = sum(np.array(rs[g]["latency"]["h_obs"]) - np.array(rs[g]["latency"]["h_null"]) for g in grp if g in rs)
        n = sum(rs[g]["latency"]["n_pairs"] for g in grp if g in rs)
        a.plot(lags, 1000 * np.asarray(h) / max(n, 1), color=col, lw=1.5, label=lab)
    a.axhline(0, color=INK2, lw=0.8)
    a.set_xlim(0, 120)
    a.set_xlabel("minutes since the link was posted")
    a.set_ylabel("excess arrivals per 1000\nexposed recipients per 5 min")
    a.legend(fontsize=6.5)
    a.set_title("NE09: latency of link-induced arrivals", loc="left", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "latency_ne09.pdf")
    plt.close(fig)


def fig_summary(df, rs, cross):
    """One-page round-1 summary (letter)."""
    import polars as pl
    fig = plt.figure(figsize=(8.5, 11))
    gs = fig.add_gridspec(4, 2, height_ratios=[0.25, 1.15, 1, 1], hspace=0.55, wspace=0.5, left=0.15, right=0.97, top=0.97, bottom=0.05)
    t = fig.add_subplot(gs[0, :])
    t.axis("off")
    P1 = cross["P1_counts"]
    pooled = cross["P1_pooled"]
    t.text(0, 0.95, "H28 round 1: are links the contagion vector of herding?", fontsize=12, weight="bold", va="top", color=INK)
    t.text(0, 0.45, (f"P1 (κ>0, p<.05, z_shift≥2): supported {P1['supported']}, weak {P1['weak']}, failed {P1['failed']} of {cross['P1_tested']} tested herding periods; "
                     f"pooled κ {pooled['b']:+.2f} ± {pooled['se']:.2f} (e^κ {np.exp(pooled['b']):.2f}).\n"
                     f"Median λ {cross['P5']['lam_all_median']:.3f} extra arrivals per link exposure; median R_link {cross['P6']['R_median']:.2f}; "
                     f"removing all links: median simulated peak occupancy ×{cross.get('P7', {}).get('f0_median', float('nan')):.2f}."),
           fontsize=7.5, va="top", color=INK2)
    a = fig.add_subplot(gs[1, 0])
    forest(a, df)
    a.set_xlabel("κ̂ (log hazard ratio, visible link in last 60 min)")
    a.set_title("(a) per-period κ̂ (gray: shift null ±2 sd)", loc="left", fontsize=8)
    a = fig.add_subplot(gs[1, 1])
    d = df.filter(pl.col("tested")).sort("goal")
    yy = np.arange(d.height)[::-1]
    a.scatter(d["kappa_wlead"], yy + 0.15, s=18, color=BLUE, label="κ: link seen in last 60 min", zorder=3)
    a.scatter(d["lead"], yy - 0.15, s=18, color=ORANGE, marker="D", label="κ_lead: link arrives in next 60 min", zorder=3)
    for y0, k0, l0 in zip(yy, d["kappa_wlead"], d["lead"]):
        a.plot([k0, l0], [y0 + 0.15, y0 - 0.15], color=GRID, lw=1, zorder=1)
    a.axvline(0, color=INK2, lw=0.8)
    a.set_yticks(yy, [f"#{g}" for g in d["goal"]])
    a.legend(fontsize=6.5, loc="lower right")
    a.set_xlabel("coefficient (joint lag + lead model)")
    a.set_title("(b) lead placebo: future links predict as well", loc="left", fontsize=8)
    a = fig.add_subplot(gs[2, 0])
    k = cross["kernel"]
    for i, v in enumerate([k["k015"], k["k1560"], k["k60240"]]):
        a.errorbar(i, v["b"], yerr=1.96 * v["se"], fmt="o", color=BLUE, ms=4, capsize=2)
    dd = cross["P4"]
    for i, kk in enumerate(("d11", "d12", "d13", "dS2")):
        v = dd[kk]
        a.errorbar(4 + i, v["b"], yerr=1.96 * v["se"], fmt="o", color=ORANGE if kk == "dS2" else AQUA, ms=4, capsize=2)
    a.axhline(0, color=INK2, lw=0.8)
    a.axvline(3, color=GRID, lw=1)
    a.set_xticks([0, 1, 2, 4, 5, 6, 7], ["0–15'", "15–60'", "60–240'", "1 link", "2 links", "3+ links", "≥2 senders"], fontsize=6.2)
    a.set_ylim(-2.5, 2)
    a.set_title("(c) pooled kernel (blue) and dose (green/orange)", loc="left", fontsize=8)
    a.set_ylabel("pooled coefficient")
    a = fig.add_subplot(gs[2, 1])
    lags = np.arange(2.5, 240, 5)
    for grp, col, lab in ((PRE_NE09, ORANGE, "pre-NE09"), (POST_NE09, BLUE, "post-NE09")):
        h = sum(np.array(rs[g]["latency"]["h_obs"]) - np.array(rs[g]["latency"]["h_null"]) for g in grp if g in rs)
        n = sum(rs[g]["latency"]["n_pairs"] for g in grp if g in rs)
        a.plot(lags, 1000 * np.asarray(h) / max(n, 1), color=col, lw=1.4, label=lab)
    a.axhline(0, color=INK2, lw=0.8)
    a.set_xlim(0, 120)
    a.set_xlabel("minutes since link posted")
    a.set_ylabel("excess arrivals /1000 exposed /5 min")
    a.legend(fontsize=6.5)
    a.set_title("(d) NE09 latency", loc="left", fontsize=8)
    a = fig.add_subplot(gs[3, :])
    cf_panel(a, df)
    a.legend(fontsize=6.5, ncol=3, loc="lower left")
    a.set_title("(e) counterfactual: simulated peak single-project occupancy under link throttling", loc="left", fontsize=8)
    fig.savefig(FIG / "H28_round1_summary.pdf")
    plt.close(fig)


def fig_summary_obs(df, cross):
    """Observables figure for the one-page summary (two panels, ~4.6 in wide)."""
    import polars as pl
    fig, ax = plt.subplots(1, 2, figsize=(4.6, 2.35), gridspec_kw=dict(width_ratios=[1.1, 1], wspace=0.45))
    d = df.filter(pl.col("tested")).sort("goal")
    yy = np.arange(d.height)[::-1]
    a = ax[0]
    for y0, k0, l0 in zip(yy, d["kappa_wlead"], d["lead"]):
        a.plot([k0, l0], [y0, y0], color=GRID, lw=1.2, zorder=1)
    a.scatter(d["kappa_wlead"], yy, s=12, color=BLUE, label="link seen, last 60 min", zorder=3)
    a.scatter(d["lead"], yy, s=12, color=ORANGE, marker="D", label="link arrives, next 60 min", zorder=3)
    a.axvline(0, color=INK2, lw=0.8)
    a.set_yticks(yy, [f"#{g}" for g in d["goal"]], fontsize=6)
    a.tick_params(labelsize=6)
    a.set_xlabel("log hazard ratio of switching to X", fontsize=6.5)
    a.legend(fontsize=5.3, loc="lower right", handletextpad=0.2, borderaxespad=0.1)
    a.set_title("(a) past vs future links", loc="left", fontsize=7)
    c = df.filter(pl.col("tested") & pl.col("cf_f0").is_not_null()).sort("goal")
    yc = np.arange(c.height)[::-1]
    b = ax[1]
    b.scatter(c["cf_f05"], yc, s=12, color=AQUA, label="half the links", zorder=3)
    b.scatter(c["cf_f0"], yc, s=12, color=ORANGE, marker="D", label="no links", zorder=3)
    b.axvline(1, color=INK2, lw=0.8)
    b.set_yticks(yc, [f"#{g}" for g in c["goal"]], fontsize=6)
    b.tick_params(labelsize=6)
    b.set_xlabel("peak occupancy vs. as observed", fontsize=6.5)
    b.legend(fontsize=5.3, loc="upper left", handletextpad=0.2, borderaxespad=0.1)
    b.set_title("(b) simulated throttling", loc="left", fontsize=7)
    fig.savefig(FIG / "summary_obs.pdf", bbox_inches="tight")
    plt.close(fig)


def fig_synthetic_compact():
    """Compact synthetic-validation figure for summary page 2 (column width, <= 2.1 in tall)."""
    rec = json.loads((OUT / "synthetic/recovery.json").read_text())
    by = collections.defaultdict(list)
    for r in rec:
        by[r["scen"]].append(r)
    scen = [s for s in SCEN_LAB if s in by]
    fig, a = plt.subplots(figsize=(3.4, 2.05))
    y = np.arange(len(scen))[::-1]
    p1 = [np.mean([(r["kappa"] > 0) and (r["z_shift"] >= 2) and (r["p"] < 0.05) for r in by[s]]) for s in scen]
    lead = [np.mean([r["kappa_lead"] > r["kappa_withlead"] for r in by[s]]) for s in scen]
    a.barh(y + 0.2, p1, height=0.38, color=BLUE, label="P1 call (κ>0, p<.05, z≥2)")
    a.barh(y - 0.2, lead, height=0.38, color=ORANGE, label="lead > lag (as in real herding weeks)")
    a.set_yticks(y, [SCEN_LAB[s] + (" *" if s in TRUE_LINK else "") for s in scen], fontsize=5.5)
    a.tick_params(axis="x", labelsize=5.5)
    a.set_xlim(0, 1)
    a.set_xlabel("share of 25 synthetic runs (* = true link effect)", fontsize=6)
    a.legend(fontsize=5, loc="lower center", bbox_to_anchor=(0.4, 1.0), ncol=2, handlelength=1, borderaxespad=0.2)
    fig.savefig(FIG / "synthetic_compact.pdf", bbox_inches="tight")
    plt.close(fig)


def main():
    FIG.mkdir(exist_ok=True)
    if (OUT / "synthetic/recovery.json").exists():
        fig_synthetic()
        fig_synthetic_compact()
    if (OUT / "results_round1.parquet").exists():
        df, rs = load_real()
        cross = json.loads((OUT / "cross_period_round1.json").read_text())
        fig_forest(df)
        fig_kernel_dose(cross)
        fig_counterfactual(df)
        fig_latency(rs)
        fig_summary(df, rs, cross)
        fig_summary_obs(df, cross)
    print("figures written to", FIG)


if __name__ == "__main__":
    main()
