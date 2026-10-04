"""H01 figures from the exploratory JSONs (no data text): synthetic validation, P1-P3, P5-P7, P8, P9, robustness,
a one-page summary, and per-goal-period panels for the G## folders.

Usage: uv run python hypotheses/H01-emergent-superagents-exist/analysis/figures.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
from h01common import OUT, FIG, HYP  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402

C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"     # reference categorical slots 1-3
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({"font.size": 8, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
                     "axes.spines.right": False, "lines.linewidth": 1.5, "axes.titlesize": 9, "axes.titleweight": "bold",
                     "legend.frameon": False, "pdf.fonttype": 42})


def J(name):
    p = OUT / name
    return json.loads(p.read_text()) if p.exists() else None


def unit_order(u):
    import re
    m = re.match(r"(\d+)([a-z]?)", u)
    return (int(m.group(1)), m.group(2))


# ============================================================================ synthetic
def fig_synthetic(sv):
    v1 = sv["V1_decomposition"]; v2 = sv["V2_P1"]; v3 = sv["V3_MF"]
    fig, ax = plt.subplots(2, 2, figsize=(7.2, 5.6))
    Js = [0, 0.05, 0.1, 0.2, 0.4]; keys = ["J0", "J0.05", "J0.1", "J0.2", "J0.4"]
    a = ax[0, 0]
    a.plot(Js, [v1[k]["rare"]["re_mu"] for k in keys], "o-", color=C1, label="exposure slope, rarefied (primary)")
    a.plot(Js, [v1[k]["full"]["re_mu"] for k in keys], "s--", color=C2, label="exposure slope, full vectors + log n")
    a.plot(Js, [v1[k]["room_diff"] / 10 for k in keys], "^:", color=C3, label="within − cross residual (÷10)")
    for xj, k in zip(Js, keys):
        a.text(xj, -0.012, f"P6 pass\n{v1[k]['rare']['P6_pass']*100:.0f}%", ha="center", va="top", fontsize=5.5, color=INK2)
    a.set_ylim(-0.03, 0.075)
    a.set_xlabel("planted exposure coupling J"); a.set_ylabel("RE summary (residual cos per e-fold)")
    a.set_title("V1 · P6 recovers weak coupling, saturates at strong"); a.legend(fontsize=6, loc="upper right")
    a = ax[0, 1]
    names = ["J0", "J0_noroom", "J0.1", "J0.2", "nofield_J0"]
    lbl = ["J=0\nroom field", "J=0\nno room", "J=0.1", "J=0.2", "no fields\nJ=0"]
    x = np.arange(len(names))
    a.bar(x - 0.25, [v1[k]["r2"] for k in names], 0.25, color=C1, label="R², estimated fields")
    a.bar(x, [v1[k]["r2_oracle"] for k in names], 0.25, color=C3, label="R², true fields (oracle)")
    a.bar(x + 0.25, [v1[k]["r2_rot"] for k in names], 0.25, color=INK2, alpha=0.5, label="R², rotation null")
    a.axhline(0.6, color=C2, lw=1, ls="--"); a.text(4.4, 0.62, "P5 threshold", color=C2, fontsize=6, ha="right")
    a.set_xticks(x); a.set_xticklabels(lbl, fontsize=6); a.set_ylabel("R² of a_ij on field terms")
    a.set_title("V1 · P5 R² has a large mechanical floor"); a.legend(fontsize=6, loc="upper right")
    a = ax[1, 0]
    order = ["null", "room_field_0.15", "room_field_0.3", "coupling_0.1", "coupling_0.2"]
    x = np.arange(len(order))
    a.bar(x - 0.2, [v2[k]["frac_dH_neg"] for k in order], 0.4, color=C1, label="share of days ΔH < 0")
    a.bar(x + 0.2, [v2[k]["P1_pass"] for k in order], 0.4, color=C2, label="P1 pass rate (both criteria)")
    for i, k in enumerate(order):
        a.text(i, max(v2[k]["frac_dH_neg"], v2[k]["P1_pass"]) + 0.03, f"med ΔH\n{v2[k]['median_dH']:.3f}", ha="center", fontsize=5.5, color=INK2)
    a.set_xticks(x); a.set_xticklabels(["null", "room\nfield .15", "room\nfield .3", "coupling\n.1", "coupling\n.2"], fontsize=6)
    a.set_ylim(0, 1.25); a.set_title("V2 · P1 size and power (30 days)"); a.legend(fontsize=6, loc="upper left")
    a = ax[1, 1]
    for NT, col, mk in (("N13_T5", C1, "o"), ("N20_T15", C2, "s")):
        for bh, ls in ((2.0, "-"), (8.0, "--")):
            ks = [k for k in v3 if k.startswith(NT) and f"bh{bh}_df0.0" in k]
            ks = sorted(ks, key=lambda k: v3[k]["bJn_true"])
            xt = [v3[k]["bJn_true"] for k in ks]; yh = [v3[k]["bJn_hat_median"] for k in ks]
            lo = [v3[k]["bJn_hat_q10"] for k in ks]; hi = [v3[k]["bJn_hat_q90"] for k in ks]
            a.errorbar(np.array(xt) + (0.01 if bh == 8 else -0.01), yh, yerr=[np.array(yh) - lo, np.array(hi) - yh], fmt=mk + ls,
                       color=col, ms=4, capsize=2, label=f"{NT.replace('_', ', ')} · βh={bh:g}")
    a.plot([0, 0.8], [0, 0.8], color=INK2, lw=0.8, ls=":")
    a.axhline(0.5, color=C3, lw=1, ls="--")
    a.set_xlabel("true βJ₀/n"); a.set_ylabel("estimated βJ₀/n (median, 10–90%)")
    a.set_title("V3 · P9 mean-field fit roughly recoverable"); a.legend(fontsize=5.5)
    fig.tight_layout(); fig.savefig(FIG / "synthetic_validation.pdf"); plt.close(fig)


# ============================================================================ P1 / P2 / P3
def fig_p1(ex):
    days = [d for d in ex["p1"]["days"] if "room" in d]
    units = sorted({d["unit"] for d in days}, key=unit_order)
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.0), gridspec_kw={"width_ratios": [2.2, 1]})
    a = ax[0]
    for i, u in enumerate(units):
        dd = [d for d in days if d["unit"] == u]
        for d in dd:
            col = C1 if d["room"]["p"] < 0.05 else INK2
            a.plot(i + (d["day_idx"] - 2) * 0.06, d["room"]["dH"], "o", color=col, ms=4 if d["day_idx"] else 6,
                   mfc=col if d["day_idx"] else "white")
    a.axhline(0, color=INK2, lw=0.8); a.axhline(-0.1, color=C2, lw=1, ls="--")
    a.text(len(units) - 0.5, -0.095, "P1 size threshold (−0.1)", color=C2, fontsize=6, ha="right", va="bottom")
    a.set_xticks(range(len(units))); a.set_xticklabels(["#" + u + ("*" if u in ("36b", "37") else "") for u in units], fontsize=7)
    a.set_ylabel("ΔH = H(rooms) − H(random), nats"); a.set_title("P1 · rooms are more ordered than random groups on 96% of days")
    a.text(0.01, 0.02, "filled blue: day p < 0.05 · open marker: day 1 · * secondary units", transform=a.transAxes, fontsize=6, color=INK2)
    a = ax[1]
    P2 = ex["p1"]["P2"]
    vals = [P2["room_raw"]["median_dH"], P2["room_field_removed"]["median_dH"], P2["lab_raw"]["median_dH"], P2["lab_field_removed"]["median_dH"]]
    a.bar([0, 1, 3, 4], vals, color=[C1, C1, C3, C3], alpha=1)
    for xx, v, t in zip([0, 1, 3, 4], vals, ["raw", "h removed", "raw", "h removed"]):
        a.text(xx, v - 0.004, f"{v:.3f}", ha="center", va="top", fontsize=6, color=INK)
        a.text(xx, 0.003, t, ha="center", va="bottom", fontsize=6, color=INK2)
    a.set_xticks([0.5, 3.5]); a.set_xticklabels(["rooms", "labs"])
    a.set_ylabel("median ΔH (days 2+)"); a.set_title(f"P2 · removing h_i: rooms −{P2['room_shrink']*100:.0f}%, labs −{P2['lab_shrink']*100:.0f}%")
    fig.tight_layout(); fig.savefig(FIG / "p1_p2_rooms_labs.pdf"); plt.close(fig)


# ============================================================================ P5 / P6 / P7
def fig_p56(ex, exh):
    per = ex["p56"]["per_unit"]; units = sorted([u for u in per if "slope" in per[u]], key=unit_order)
    fig, ax = plt.subplots(1, 3, figsize=(7.4, 3.3), gridspec_kw={"width_ratios": [1.3, 1.1, 1]})
    a = ax[0]
    y = np.arange(len(units))[::-1]
    for yy, u in zip(y, units):
        b, se = per[u]["slope"], per[u]["slope_se"]
        a.errorbar(b, yy, xerr=1.96 * se, fmt="o", color=C1, ms=3.5, capsize=0, lw=1)
        if exh and u in exh["p56"]["per_unit"] and "slope" in exh["p56"]["per_unit"][u]:
            a.plot(exh["p56"]["per_unit"][u]["slope"], yy - 0.3, "|", color=C2, ms=6)
    re = ex["p56"]["P6"]["re_slope"]
    a.errorbar(re["mu"], -1.2, xerr=1.96 * re["se"], fmt="D", color=INK, ms=5, capsize=2)
    a.axvline(0, color=INK2, lw=0.8)
    a.set_yticks(list(y) + [-1.2]); a.set_yticklabels(["#" + u for u in units] + ["RE"], fontsize=6.5)
    a.set_xlabel("residual cos per e-fold of exposure"); a.set_title("P6 · exposure slope per unit")
    a.text(0.98, 0.99, f"RE {re['mu']:+.3f} ± {re['se']:.3f}\np = {re['p_two']:.3f}\n| = cross-fitted h", transform=a.transAxes,
           fontsize=6, color=INK2, ha="right", va="top")
    a = ax[1]
    r2 = ex["p56"]["P5"]["r2"]; uu = sorted(r2, key=unit_order)
    x = np.arange(len(uu))
    a.plot(x, [r2[u] for u in uu], "o", color=C1, ms=4, label="R² (first-day h, primary)")
    a.plot(x, [per[u]["r2_rot_mean"] for u in uu], "_", color=INK2, ms=9, mew=1.5, label="rotation null")
    if exh:
        a.plot(x, [exh["p56"]["P5"]["r2"].get(u, np.nan) for u in uu], "s", color=C2, ms=3, label="R² (cross-fitted h)")
        a.plot(x, [exh["p56"]["per_unit"][u]["r2_rot_mean"] for u in uu], "_", color=C2, ms=7, mew=1, alpha=0.6)
    a.axhline(0.6, color=C3, ls="--", lw=1)
    a.set_xticks(x); a.set_xticklabels(uu, rotation=90, fontsize=6); a.set_ylim(0, 1)
    a.set_title("P5 · field R² vs rotation null"); a.legend(fontsize=5, loc="lower right")
    a = ax[2]
    tw = ex["p56"]["P6"]["two_room"]; tu = sorted(tw, key=unit_order)
    y = np.arange(len(tu))[::-1]
    a.barh(y, [tw[u]["within_minus_cross"] for u in tu], color=[C1 if tw[u]["p_agent_room_perm"] < 0.05 else INK2 for u in tu], height=0.6)
    if ex.get("p9_rooms"):
        pr = ex["p9_rooms"]
        a.plot([pr[u]["rho_within"] - pr[u]["rho_cross"] if pr.get(u) and pr[u]["rho_within"] is not None and pr[u]["rho_cross"] is not None else np.nan
                for u in tu], y, "o", color=C2, ms=3.5, label="ρ_within − ρ_cross (day-to-day)")
        a.legend(fontsize=5.5, loc="lower right")
    a.set_yticks(y); a.set_yticklabels(["#" + u for u in tu], fontsize=6.5)
    a.set_xlabel("within − cross"); a.set_title("P6 · rooms (blue: p < .05)")
    fig.tight_layout(); fig.savefig(FIG / "p5_p6_coupling.pdf"); plt.close(fig)


def fig_p7_p8(ex):
    P7 = ex["p56"]["P7"]; P8 = ex.get("p8")
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.8))
    a = ax[0]
    for g, col, lab in (("stay", INK2, "stay (co-located both weeks)"), ("new", C1, "new (best × rest → merged)"), ("g5_cut", C2, "GPT-5 × #rest (cut)")):
        m = P7["means"]
        a.plot([0, 1], [m[f"{g}_pre"], m[f"{g}_post"]], "o-", color=col, label=lab)
    a.set_xticks([0, 1]); a.set_xticklabels(["#39 (pre)", "#40 merged (post)"]); a.set_xlim(-0.3, 1.3)
    a.set_ylabel("mean residual cos"); a.legend(fontsize=6)
    a.set_title(f"P7 · merge DiD {P7['new']['did']:+.2f} (perm p = {P7['new']['p_perm_one_sided']:.3f})")
    a = ax[1]
    if P8:
        rb = P8["resid_by_day"]; dd = list(rb)
        x = np.arange(len(dd))
        a.plot(x, [rb[d]["r_triplet_incumbent"] for d in dd], "o-", color=C1, label="triplet × incumbents")
        a.plot(x, [rb[d]["r_incumbent_incumbent"] for d in dd], "s-", color=INK2, label="incumbent × incumbent")
        a.plot(x, [rb[d]["r_triplet_triplet"] for d in dd], "^:", color=C2, label="within triplet")
        a.set_xticks(x); a.set_xticklabels([d[5:] for d in dd], fontsize=6.5)
        a.set_ylabel("mean residual cos"); a.legend(fontsize=6)
        a.set_title("P8 · NE32 GPT-5.6 triplet (no isolated statements)")
    fig.tight_layout(); fig.savefig(FIG / "p7_p8_events.pdf"); plt.close(fig)


def fig_p9(ex):
    u9 = ex["p9"]["units"]; uu = sorted(u9, key=unit_order)
    fig, ax = plt.subplots(figsize=(7.2, 2.8))
    x = np.arange(len(uu))
    cols = {"I": C1, "II": C3, "III": C2}
    for i, u in enumerate(uu):
        v = u9[u]; se = v.get("bJn_jk_se") or 0
        ax.errorbar(i, v["bJ_over_n"], yerr=1.96 * se, fmt="o", color=cols[v["regime"]], ms=3.5, lw=0.8)
    ax.axhline(0.5, color=INK, ls="--", lw=1); ax.text(len(uu) - 0.5, 0.52, "P9: predicted below 0.5", fontsize=6, ha="right", color=INK)
    ax.axhline(1.0, color=INK2, ls=":", lw=0.8); ax.text(len(uu) - 0.5, 1.02, "mean-field critical point", fontsize=6, ha="right", color=INK2)
    ax.set_xticks(x); ax.set_xticklabels(uu, rotation=90, fontsize=6)
    ax.set_ylabel("βJ₀ / n  (upper bound; ±1.96 jackknife SE)")
    for R, c in cols.items():
        ax.plot([], [], "o", color=c, label=f"regime {R}")
    ax.legend(fontsize=6, loc="upper left", ncol=3)
    ax.set_title("P9 · mean-field O(32) βJ₀/n per unit: 34/41 units ≥ 0.5 (day-shuffle null R ≈ 1)")
    fig.tight_layout(); fig.savefig(FIG / "p9_meanfield.pdf"); plt.close(fig)


def fig_robust(rob):
    fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.6))
    names = [n for n in rob if not n.startswith("_") and "P1_median_dH" in rob[n]]
    a = ax[0]
    y = np.arange(len(names))[::-1]
    a.barh(y, [rob[n]["P1_median_dH"] for n in names], color=[C1 if rob[n]["P1_median_dH"] <= -0.1 else INK2 for n in names], height=0.6)
    a.axvline(-0.1, color=C2, ls="--", lw=1)
    a.set_yticks(y); a.set_yticklabels(names, fontsize=6.5); a.set_xlabel("P1 median ΔH"); a.set_title("P1 across instruments")
    a = ax[1]
    nn = [n for n in names if rob[n].get("P6_mu") is not None]; y2 = np.arange(len(nn))[::-1]
    a.errorbar([rob[n]["P6_mu"] for n in nn], y2, xerr=[1.96 * rob[n]["P6_se"] for n in nn], fmt="o", color=C1, ms=3.5)
    a.axvline(0, color=INK2, lw=0.8); a.set_yticks(y2); a.set_yticklabels(nn, fontsize=6.5)
    a.set_xlabel("P6 RE slope"); a.set_title("P6 slope across instruments")
    a = ax[2]
    nn = [n for n in names if rob[n].get("P9_median") is not None]; y3 = np.arange(len(nn))[::-1]
    a.barh(y3, [rob[n]["P9_median"] for n in nn], color=C3, height=0.6); a.axvline(0.5, color=INK, ls="--", lw=1)
    a.set_yticks(y3); a.set_yticklabels(nn, fontsize=6.5); a.set_xlabel("median βJ₀/n"); a.set_title("P9 across instruments")
    fig.tight_layout(); fig.savefig(FIG / "robustness.pdf"); plt.close(fig)


# ============================================================================ summary page
def fig_summary(ex, rows, rob):
    with PdfPages(FIG / "summary.pdf") as pdf:
        fig = plt.figure(figsize=(8.27, 11.69))
        import textwrap
        fig.text(0.05, 0.968, "H01 · ideological order (D3.1.a) and coupling vs field (D3.2)", fontsize=12, weight="bold", color=INK)
        fig.text(0.05, 0.952, "Exploratory round 1, non-holdout only (holdout untouched). AI Village data (AI Digest). Unit = goal period split at",
                 fontsize=7, color=INK2)
        fig.text(0.05, 0.941, "step changes; bge-small statements, per-regime whitening n = 32, k = 40 meaning clusters.", fontsize=7, color=INK2)
        tab = fig.add_axes([0.05, 0.585, 0.9, 0.345]); tab.axis("off")
        wr = lambda x, w: "\n".join(textwrap.wrap(x, w))  # noqa: E731
        cell = [[r[0], wr(r[1], 44), wr(r[2], 52), wr(r[3], 18)] for r in rows]
        t = tab.table(cellText=cell, colLabels=["", "prediction (locked)", "outcome", "verdict"], colWidths=[0.05, 0.37, 0.43, 0.15],
                      loc="upper left", cellLoc="left")
        t.auto_set_font_size(False); t.set_fontsize(6.0)
        for (rr, cc), c in t.get_celld().items():
            n_lines = max(len(str(cell[rr - 1][k]).split("\n")) for k in range(4)) if rr > 0 else 1
            c.set_height(0.028 * n_lines + 0.012)
        for (rr, cc), c in t.get_celld().items():
            c.set_edgecolor(GRID); c.get_text().set_wrap(True)
            if rr == 0:
                c.get_text().set_weight("bold")
        heads = ["Headline: rooms are reliably MORE ordered than random groups (96% of days), but the effect is just under the",
                 "pre-registered size; it is largest where rooms got different instructions (#38, #44: a room field). Coupling evidence:",
                 "small positive exposure slope (+0.013/e-fold, p = 0.02; instrument-sensitive), a strong merge DiD (+0.18), and day-to-day",
                 "co-fluctuation that lives inside rooms. The mean-field coupling bound is large (P9 failed), so 'order is mostly field' is not supported."]
        for k, h in enumerate(heads):
            fig.text(0.05, 0.565 - 0.0135 * k, h, fontsize=7.4, color=INK, weight="bold" if k == 0 else "normal")
        # panels
        days = [d for d in ex["p1"]["days"] if "room" in d]
        a = fig.add_axes([0.07, 0.36, 0.40, 0.19])
        a.hist([d["room"]["dH"] for d in days if d["primary"]], bins=20, color=C1)
        a.axvline(0, color=INK2, lw=0.8); a.axvline(-0.1, color=C2, ls="--", lw=1)
        a.set_xlabel("ΔH rooms − random (nats), 54 days"); a.set_title("P1: rooms below random on 96% of days", fontsize=8)
        per = ex["p56"]["per_unit"]; units = sorted([u for u in per if "slope" in per[u]], key=unit_order)
        a = fig.add_axes([0.57, 0.36, 0.38, 0.19])
        a.errorbar(range(len(units)), [per[u]["slope"] for u in units], yerr=[1.96 * per[u]["slope_se"] for u in units], fmt="o", color=C1, ms=3)
        a.axhline(0, color=INK2, lw=0.8); re = ex["p56"]["P6"]["re_slope"]
        a.axhspan(re["mu"] - 1.96 * re["se"], re["mu"] + 1.96 * re["se"], color=C2, alpha=0.15)
        a.set_xticks(range(len(units))); a.set_xticklabels(units, rotation=90, fontsize=6)
        a.set_title(f"P6: exposure slope, RE {re['mu']:+.3f} (p = {re['p_two']:.3f})", fontsize=8)
        u9 = ex["p9"]["units"]; uu = sorted(u9, key=unit_order)
        a = fig.add_axes([0.07, 0.10, 0.40, 0.19])
        a.plot(range(len(uu)), [u9[u]["bJ_over_n"] for u in uu], "o", color=C3, ms=3)
        a.axhline(0.5, color=INK, ls="--", lw=1)
        a.set_xticks(range(0, len(uu), 3)); a.set_xticklabels(uu[::3], fontsize=6, rotation=90)
        a.set_title("P9: mean-field βJ₀/n per unit (upper bound)", fontsize=8)
        a = fig.add_axes([0.57, 0.10, 0.38, 0.19])
        pr = ex.get("p9_rooms", {})
        ks = sorted([k for k in pr if pr[k]["rho_cross"] is not None], key=unit_order)
        a.plot(range(len(ks)), [pr[k]["rho_within"] for k in ks], "o-", color=C1, ms=3, label="same room")
        a.plot(range(len(ks)), [pr[k]["rho_cross"] for k in ks], "s-", color=C2, ms=3, label="different rooms")
        a.set_xticks(range(len(ks))); a.set_xticklabels(ks, fontsize=6, rotation=90); a.legend(fontsize=6)
        a.set_title("Day-to-day co-fluctuation lives inside rooms", fontsize=8)
        fig.text(0.05, 0.045, "Scorecard: A1 B1 C1 D1 E1 F1 G1 H0 I1 (see card). Level: hypothesis (not descriptive: C < 2).", fontsize=7, color=INK2)
        fig.text(0.05, 0.032, "Other figures: synthetic_validation, p1_p2_rooms_labs, p5_p6_coupling, p7_p8_events, p9_meanfield, robustness.",
                 fontsize=7, color=INK2)
        pdf.savefig(fig); plt.close(fig)


# ============================================================================ per-period panels
def fig_periods(ex):
    gmap = {}
    for u in ex["p9"]["units"]:
        g = "".join(ch for ch in u if ch.isdigit())
        gmap.setdefault(g, []).append(u)
    for g, units in gmap.items():
        gdir = HYP / f"G{int(g):02d}"
        if not gdir.exists():
            continue
        (gdir / "figures").mkdir(exist_ok=True)
        fig, ax = plt.subplots(1, 2, figsize=(6.4, 2.4))
        a = ax[0]
        days = [d for d in ex["p1"]["days"] if "room" in d and d["unit"] in units]
        if days:
            a.plot(range(len(days)), [d["room"]["dH"] for d in days], "o-", color=C1, label="rooms")
            a.plot(range(len(days)), [d["lab"]["dH"] if "lab" in d else np.nan for d in days], "s--", color=C3, label="labs")
            a.axhline(0, color=INK2, lw=0.8); a.axhline(-0.1, color=C2, ls="--", lw=1)
            a.set_xticks(range(len(days))); a.set_xticklabels([d["day"][5:] for d in days], rotation=90, fontsize=6)
            a.set_title("P1/P2 ΔH vs random partitions"); a.legend(fontsize=6)
        else:
            pol = ex["p4"]["units"]
            for u in units:
                if u in pol:
                    a.plot(range(len(pol[u]["pol_g_daily"])), pol[u]["pol_g_daily"], "o-", color=C1, label=f"#{u}")
            a.axhline(0, color=INK2, lw=0.8); a.set_title("P4 polarization along ĝ (daily)"); a.legend(fontsize=6)
        a = ax[1]
        per = ex["p56"]["per_unit"]
        shown = False
        for u, col in zip(units, (C1, C2, C3, INK2, "#e87ba4")):
            if u in per and per[u].get("mean_r_by_day"):
                a.plot(per[u]["mean_r_by_day"], "o-", color=col, label=f"#{u}"); shown = True
        if shown:
            a.set_title("mean residual cos by day (rarefied)"); a.set_xlabel("day index in unit"); a.legend(fontsize=6)
        else:
            u9 = ex["p9"]["units"]
            a.bar(range(len(units)), [u9[u]["bJ_over_n"] for u in units], color=C3)
            a.axhline(0.5, color=INK, ls="--", lw=1)
            a.set_xticks(range(len(units))); a.set_xticklabels(units); a.set_title("P9 βJ₀/n (upper bound)")
        fig.tight_layout(); fig.savefig(gdir / "figures" / f"G{int(g):02d}_panels.pdf"); plt.close(fig)


def main():
    ex = J("explore.json"); exh = J("explore_hcross.json"); sv = J("synthetic_validation.json")
    FIG.mkdir(exist_ok=True)
    fig_synthetic(sv)
    fig_p1(ex); fig_p56(ex, exh); fig_p7_p8(ex); fig_p9(ex)
    rob = json.loads((OUT / "robustness_summary.json").read_text()) if (OUT / "robustness_summary.json").exists() else None
    if rob:
        fig_robust(rob)
    rows = json.loads((OUT / "outcome_rows.json").read_text()) if (OUT / "outcome_rows.json").exists() else []
    fig_summary(ex, rows, rob)
    fig_periods(ex)
    print("figures written to", FIG)


if __name__ == "__main__":
    main()
