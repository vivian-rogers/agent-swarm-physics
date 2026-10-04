"""H12 real-data figures (non-holdout): random-matrix arm, dimensionality arm, one-page summary, per-period figures."""
from __future__ import annotations

import json

import h12lib as L
import matplotlib.pyplot as plt
import numpy as np
import polars as pl
from matplotlib.backends.backend_pdf import PdfPages

from figures import C1, C2, C3, C4, GRID, INK, INK2, panel_label, preview, style
from write_period_folders import PERIODS

O = L.OUT


def load():
    ut = pl.read_parquet(O / "unit_table.parquet")
    pu = pl.read_parquet(O / "posthoc_units.parquet")
    h2 = pl.read_parquet(O / "h02_compare.parquet")
    kick = pl.read_parquet(O / "ne34_kickoffs.parquet"); plac = pl.read_parquet(O / "ne34_placebos.parquet")
    p7 = pl.read_parquet(O / "p7_day1.parquet"); pm = pl.read_parquet(O / "period_means.parquet")
    tmpl = pl.read_parquet(O / "posthoc_templating.parquet")
    outc = json.loads((O / "outcomes.json").read_text()); ph = json.loads((O / "posthoc.json").read_text())
    dd = json.loads((O / "posthoc_dedup.json").read_text())
    return ut, pu, h2, kick, plac, p7, pm, tmpl, outc, ph, dd


def ax_rmt(ax, ut):
    sc = ut.filter(pl.col("scored")).sort("goal_no", "unit")
    x = np.arange(sc.height)
    ax.axhline(1, color=INK2, lw=0.8, ls=":")
    ax.plot(x, sc["l1_edge"], "o", color=C1, label="activity")
    ax.plot(x, sc["l1_edge_lull"], "o", mfc="white", mec=C1, label="activity, lulls removed")
    ax.plot(x, sc["talk_l1_edge"], "s", color=C2, ms=3.5, label="talk")
    ax.plot(x, sc["content_l1_edge"], "^", color=C3, ms=4, label="content")
    ax.set_xticks(x, sc["unit"].to_list(), rotation=90, fontsize=5.5)
    ax.set_ylabel("λ₁ / cross-day edge")
    for b in [7, 9]:
        ax.axvline(b - 0.5, color=GRID, lw=0.8)
    ax.text(3, 2.75, "regime I", fontsize=6, color=INK2, ha="center"); ax.text(8, 2.75, "II", fontsize=6, color=INK2, ha="center")
    ax.text(16, 2.75, "regime III", fontsize=6, color=INK2, ha="center")
    ax.set_ylim(0.2, 2.9)
    ax.legend(loc="lower left", ncol=2, fontsize=5.8)


def fig_rmt(ut, pu, h2):
    fig, axs = plt.subplots(2, 2, figsize=(7.5, 5.4), gridspec_kw={"width_ratios": [1.6, 1]})
    ax = axs[0, 0]; ax_rmt(ax, ut); panel_label(ax, "a  One mode above the edge, per unit")
    ax = axs[0, 1]
    ax.plot(h2["VR_h02"], h2["l1_block"], "o", color=C1)
    lim = [0.9, max(h2["l1_block"].max(), h2["VR_h02"].max()) + 0.1]
    ax.plot(lim, lim, color=INK2, lw=0.8, ls=":")
    ax.set_xlabel("H02 variance ratio VR (Curie–Weiss)"); ax.set_ylabel("H12 top eigenvalue λ₁ (block-demeaned)")
    ax.text(lim[0] + 0.02, lim[1] - 0.12, "λ₁ = VR: uniform\n(Curie–Weiss) mode", fontsize=6, color=INK2)
    panel_label(ax, "b  Top mode vs H02 (21 chunks)")
    ax = axs[1, 0]
    ax.plot(pu["lull_frac"], pu["lull_drop"] * 100, "o", color=C1)
    for r in pu.filter(pl.col("lull_frac") > 0.25).iter_rows(named=True):
        ax.annotate(r["unit"], (r["lull_frac"], r["lull_drop"] * 100), xytext=(3, -3), textcoords="offset points", fontsize=6, color=INK2)
    ax.axhline(30, color=INK2, lw=0.8, ls=":"); ax.text(0.3, 32, "P2 threshold (30%)", fontsize=6, color=INK2)
    ax.set_xlabel("share of minutes with ≤ 1 active agent (joint lulls)"); ax.set_ylabel("drop in λ₁/edge after lull filter (%)")
    panel_label(ax, "c  The market mode is partly joint lulls")
    ax = axs[1, 1]
    sc = pu.sort("goal_no", "unit")
    ax.plot(sc["content_l1_edge"], sc["l1_edge_dc"], "^", color=C3)
    ax.plot([0.9, 2.8], [0.9, 2.8], color=INK2, lw=0.8, ls=":")
    ax.axhline(1, color=INK2, lw=0.6); ax.axvline(1, color=INK2, lw=0.6)
    ax.set_xlabel("content λ₁/edge (agent-centered)"); ax.set_ylabel("content λ₁/edge (agent-day centered)")
    panel_label(ax, "d  Content mode survives day-centering")
    fig.tight_layout(); fig.savefig(L.FIG / "rmt_arm.pdf"); preview(fig, "rmt_arm"); plt.close(fig)


def ax_kick(ax, kick, plac):
    rng = np.random.default_rng(1)
    yb = plac["rel"].to_numpy() * 100
    ax.boxplot([yb], positions=[0], widths=0.5, showfliers=False, medianprops=dict(color=INK), boxprops=dict(color=INK2),
               whiskerprops=dict(color=INK2), capprops=dict(color=INK2))
    ax.plot(rng.uniform(-0.18, 0.18, len(yb)), yb, ".", color=INK2, alpha=0.35, ms=3)
    for j, (reg, col) in enumerate([("I", C1), ("II", C4), ("III", C2)]):
        k = kick.filter(pl.col("regime") == reg)
        ax.plot(1 + rng.uniform(-0.15, 0.15, k.height), k["rel"] * 100, "o", color=col, label=f"regime {reg} (n = {k.height})")
    ax.axhline(0, color=INK2, lw=0.8, ls=":")
    ax.set_xticks([0, 1], ["placebo day pairs\n(n = %d)" % plac.height, "kickoffs (NE34)"])
    ax.set_ylabel("first-hour PR change (%)"); ax.legend(loc="upper left", fontsize=6)
    ax.text(1.25, -45, "predicted:\nbelow 0", fontsize=6, color=INK2)


def fig_dim(kick, plac, p7, pm, tmpl):
    fig, axs = plt.subplots(2, 2, figsize=(7.5, 5.4))
    ax = axs[0, 0]; ax_kick(ax, kick, plac); panel_label(ax, "a  Kickoffs do not collapse PR (P6)")
    ax = axs[0, 1]
    x = p7.filter(pl.col("prday_d1").is_not_nan() & pl.col("prday_later_med").is_not_nan() & (pl.col("N") >= 10)).sort("goal_no")
    for r in x.iter_rows(named=True):
        col = C2 if r["prday_d1"] > r["prday_later_med"] else C1
        ax.plot([0, 1], [r["prday_d1"], r["prday_later_med"]], "-", color=col, lw=1, alpha=0.8)
        ax.plot([0, 1], [r["prday_d1"], r["prday_later_med"]], "o", color=col, ms=3)
    ax.set_xticks([0, 1], ["day 1 (kickoff)", "median of later days"]); ax.set_xlim(-0.3, 1.3)
    ax.set_ylabel("PRday (6 agents × 15 chat statements)")
    n_hi = int((x["prday_d1"] > x["prday_later_med"]).sum())
    ax.text(0.5, x["prday_later_med"].min() - 0.5, f"day 1 higher in {n_hi}/{x.height} periods (orange)", ha="center", fontsize=6, color=INK2)
    panel_label(ax, "b  Day 1 is higher-dimensional (P7)")
    ax = axs[1, 0]
    groups = [("F", "free", C3), ("C", "shared objective", C1)]
    for xi, reg in enumerate(["I", "III"]):
        y = pm.filter((pl.col("regime") == reg) & pl.col("prday_mean").is_not_nan())
        if reg == "I":
            y = y.filter(pl.col("goal_no") >= 10)
        for m, lab, col in groups + [("other", "individual / competition / other", C4)]:
            yy = y.filter(pl.col("mode") == m) if m != "other" else y.filter(~pl.col("mode").is_in(["F", "C"]))
            off = {"F": -0.15, "C": 0.0, "other": 0.15}[m]
            ax.plot(np.full(yy.height, xi + off), yy["prday_mean"], "o", color=col, label=lab if xi == 0 else None)
            for r in yy.iter_rows(named=True):
                ax.annotate(f"#{r['goal_no']}", (xi + off, r["prday_mean"]), xytext=(4, -2), textcoords="offset points", fontsize=5, color=INK2)
    ax.set_xticks([0, 1], ["regime I (#10–#31)", "regime III"]); ax.set_xlim(-0.5, 1.6)
    ax.set_ylabel("period mean PRday"); ax.legend(loc="lower center", bbox_to_anchor=(0.5, 0.0), fontsize=6)
    panel_label(ax, "c  Free weeks are not higher (P9)")
    ax = axs[1, 1]
    for u, col in [("38", C2), ("39", C2), ("40", C2)]:
        pass
    low = tmpl.filter(pl.col("unit").is_in(["38a", "38b", "38c", "39", "40"]))
    oth = tmpl.filter(~pl.col("unit").is_in(["38a", "38b", "38c", "39", "40"]))
    ax.plot(oth["dup_within"] * 100, oth["prday"], "o", color=C1, ms=3.5, label="other regime-III days")
    ax.plot(low["dup_within"] * 100, low["prday"], "o", color=C2, ms=3.5, label="#38–#40")
    ax.set_xlabel("chat statements repeating the same agent's earlier text (%)"); ax.set_ylabel("PRday")
    ax.legend(loc="upper right", fontsize=6)
    panel_label(ax, "d  Low PR = agents looping, not echoing")
    fig.tight_layout(); fig.savefig(L.FIG / "dimensionality_arm.pdf"); preview(fig, "dimensionality_arm"); plt.close(fig)


OUTCOME_ROWS = None


def fig_summary(ut, pu, h2, kick, plac, p7, pm, tmpl, outc, ph, dd):
    fig = plt.figure(figsize=(8.27, 11.69))  # A4 portrait
    fig.text(0.06, 0.965, "H12 · Groupthink is dimensional collapse — exploratory round 1 (non-holdout)", fontsize=12, fontweight="bold", color=INK)
    fig.text(0.06, 0.948, "AI Village (AI Digest), goal periods split at step changes; 24 scored units (N ≥ 10), 20 kickoff transitions. 2026-10-03.",
             fontsize=7.5, color=INK2)
    head = ("Headline. The swarm has exactly one collective mode beyond random-matrix noise and the daily schedule — a uniform, "
            "Curie–Weiss-like 'market mode' — in activity (22/24 units), talk (20/24) and content (24/24). It is partly synchronized lulls. "
            "The dimensionality half fails in the predicted direction: kickoffs do not collapse the participation ratio; day 1 of a goal is "
            "higher-dimensional than later days (13/16, p = 0.02), and free weeks are not higher-dimensional than shared-objective weeks. "
            "The lowest-PR periods (#38–#40) are agents repeating themselves, not echoing each other.")
    import textwrap
    fig.text(0.06, 0.935, "\n".join(textwrap.wrap(head, 128)), fontsize=7.3, color=INK, va="top")
    ax1 = fig.add_axes([0.08, 0.60, 0.52, 0.25]); ax_rmt(ax1, ut); panel_label(ax1, "a  λ₁ / cross-day edge per unit")
    ax2 = fig.add_axes([0.70, 0.60, 0.26, 0.25])
    ax2.plot(h2["VR_h02"], h2["l1_block"], "o", color=C1, ms=3.5)
    lim = [0.9, max(h2["l1_block"].max(), h2["VR_h02"].max()) + 0.1]; ax2.plot(lim, lim, color=INK2, lw=0.8, ls=":")
    ax2.set_xlabel("H02 VR"); ax2.set_ylabel("λ₁ (block-demeaned)"); panel_label(ax2, "b  vs H02 Curie–Weiss")
    ax3 = fig.add_axes([0.08, 0.34, 0.40, 0.19]); ax_kick(ax3, kick, plac); panel_label(ax3, "c  Kickoffs (P6)")
    ax4 = fig.add_axes([0.58, 0.34, 0.38, 0.19])
    low = tmpl.filter(pl.col("unit").is_in(["38a", "38b", "38c", "39", "40"])); oth = tmpl.filter(~pl.col("unit").is_in(["38a", "38b", "38c", "39", "40"]))
    ax4.plot(oth["dup_within"] * 100, oth["prday"], "o", color=C1, ms=3, label="other regime-III days")
    ax4.plot(low["dup_within"] * 100, low["prday"], "o", color=C2, ms=3, label="#38–#40")
    ax4.set_xlabel("self-repeated chat statements (%)"); ax4.set_ylabel("PRday"); ax4.legend(fontsize=6)
    panel_label(ax4, "d  Low PR = looping (post hoc)")
    # outcome table
    rows = [("P1 few activity modes", "k_cd ∈ 1–3 in ≥ 2/3; MP inflated", f"k=1 in 22/24, k=0 in 2; MP inflated in 7/24", "core ✓, aux ✗"),
            ("P1′ beyond lulls", "same after lull filter", "k=1 in 14/24 (9/11 low-lull units)", "✗"),
            ("P2 Curie–Weiss market mode", "uniform; III > I; lull drop ≥ 30%", "uniform 22/22, VR/λ₁ 0.97; III > I; 11/24", "2 of 3 (✗)"),
            ("P3 talk + room mode", "k_talk ≤ k_act; room sep. ≥ 1/2", "22/24; 3/10 (8/10 sub-edge)", "✗"),
            ("P4 content modes", "k ≥ 1 in ≥ 1/2; C > I/F", "24/24; C > I/F in I only", "core ✓, aux ✗"),
            ("P5 family mode", "descriptive", "lab separation in 10/24", "–"),
            ("P6 kickoff collapse (NE34)", "median Δ < 0, ≥ 2/3 neg., p < .05", f"Δ +7%, {outc['P6']['frac_neg']:.0%} neg., p = {outc['P6']['p_mw']:.2f}", "✗"),
            ("P7 re-expansion", "day 1 < later in ≥ 2/3", "3/16 (reversed, p = .02)", "✗ (R4 wins)"),
            ("P8 consensus weeks decline", "slope < 0 in #19, #31, #40", "#31 only", "✗"),
            ("P9 free > shared", "regime I MW p ≤ .05", f"p = {outc['P9']['p_exact']:.2f}", "✗"),
            ("P10 arms agree", "ρ < 0 in I and III", f"ρ = {outc['P10']['by_regime']['I']['rho']:+.2f}, {outc['P10']['by_regime']['III']['rho']:+.2f}", "✗")]
    ax5 = fig.add_axes([0.06, 0.04, 0.9, 0.26]); ax5.axis("off")
    tb = ax5.table(cellText=[list(r) for r in rows], colLabels=["Prediction", "Rule", "Observed", "Verdict"], loc="upper left",
                   colWidths=[0.24, 0.33, 0.30, 0.13], cellLoc="left")
    tb.auto_set_font_size(False); tb.set_fontsize(6.6); tb.scale(1, 1.32)
    for (r, c), cell in tb.get_celld().items():
        cell.set_edgecolor(GRID); cell.set_linewidth(0.5)
        if r == 0:
            cell.set_text_props(fontweight="bold", color=INK)
    fig.text(0.06, 0.022, "Scorecard (card): random-matrix arm A1 B1 C1 D1 E0 F1 G0 H1 I0; dimensionality arm A1 B1 C0 D0 E0 F1 G0 H0 I0. "
             "Synthetic validation: figures/synthetic_validation.pdf.", fontsize=6.3, color=INK2)
    fig.text(0.06, 0.010, "Post hoc (no verdicts): lull stratification, agent-day-centered content, within-agent dedup (P6/P7/P9 unchanged), "
             "long-lull synthetic. Holdout untouched; confirm.py written, not run.", fontsize=6.3, color=INK2)
    fig.savefig(L.FIG / "H12_summary.pdf"); preview(fig, "H12_summary"); plt.close(fig)


def fig_periods(ut):
    rmt = {json.loads(f.read_text())["unit"]: json.loads(f.read_text()) for f in O.glob("G*/rmt_*.json")}
    for g in PERIODS:
        units = sorted(u for u, r in rmt.items() if r["goal_no"] == g)
        p30 = pl.concat([pl.read_parquet(f) for f in sorted(O.glob(f"G{g:02d}/pr30_*.parquet"))], how="diagonal_relaxed").sort("pt_date", "win30")
        pday = pl.concat([pl.read_parquet(f) for f in sorted(O.glob(f"G{g:02d}/prday_*.parquet"))], how="diagonal_relaxed").sort("pt_date")
        fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.6), gridspec_kw={"width_ratios": [1, 1.7]})
        ax = axs[0]
        for u in units:
            r = rmt[u]
            for key, col, mk in [("act", C1, "o"), ("talk", C2, "s"), ("content", C3, "^")]:
                b = r.get(key, {})
                if b.get("eig"):
                    e = np.array(b["eig"][:6]) / b["edge_cd"]
                    ax.plot(np.arange(1, len(e) + 1), e, mk + "-", color=col, ms=3, lw=0.8, alpha=0.9,
                            label={"act": "activity", "talk": "talk", "content": "content"}[key] if u == units[0] else None)
        ax.axhline(1, color=INK2, lw=0.8, ls=":")
        ax.set_xlabel("eigenvalue rank"); ax.set_ylabel("λ_k / cross-day edge")
        if units:
            ax.legend(fontsize=6)
        ax.set_title(f"G{g:02d} spectra ({', '.join(units) or 'no RMT unit'})", fontsize=7.5, loc="left")
        ax = axs[1]
        dates = p30["pt_date"].unique().sort().to_list()
        xs = []; off = 0
        for d in dates:
            x = p30.filter(pl.col("pt_date") == d)
            ax.plot(off + x["win30"].to_numpy(), x["pr"].to_numpy(), "-", color=C1, lw=1)
            pdv = pday.filter(pl.col("pt_date") == d)["prday"]
            if len(pdv) and pdv[0] == pdv[0]:
                ax.plot([off, off + x["win30"].max()], [pdv[0]] * 2, color=C2, lw=1.6)
            xs.append(off); off += int(x["win30"].max()) + 2
            ax.axvline(off - 1, color=GRID, lw=0.6)
        ax.set_xticks(xs, [d[5:] for d in dates], rotation=90, fontsize=5.5)
        ax.set_ylabel("PR (chat, d = 32)")
        ax.plot([], [], color=C1, label="PR30 (30-min windows)"); ax.plot([], [], color=C2, lw=1.6, label="PRday")
        ax.legend(fontsize=6, loc="lower right"); ax.set_title("dimensionality by window and day", fontsize=7.5, loc="left")
        fig.tight_layout()
        (L.HYP / f"G{g:02d}" / "figures").mkdir(parents=True, exist_ok=True)
        fig.savefig(L.HYP / f"G{g:02d}" / "figures" / f"G{g:02d}_summary.pdf"); plt.close(fig)
    print("period figures done")


def main(which="all"):
    style()
    ut, pu, h2, kick, plac, p7, pm, tmpl, outc, ph, dd = load()
    if which in ("real", "all"):
        fig_rmt(ut, pu, h2); fig_dim(kick, plac, p7, pm, tmpl); fig_periods(ut)
    if which in ("summary", "all", "real"):
        fig_summary(ut, pu, h2, kick, plac, p7, pm, tmpl, outc, ph, dd)
