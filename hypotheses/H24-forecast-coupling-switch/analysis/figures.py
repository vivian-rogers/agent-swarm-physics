"""H24 figures from the round-1 outputs (no agent text).

figures/summary.pdf        one-page overview (6 panels); also G21/figures/G21_panels.pdf
figures/summary_obs.pdf    the summary-page observables figure (4.3 x 2.6 in)
Usage: uv run python hypotheses/H24-forecast-coupling-switch/analysis/figures.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
from h24lib import CARD, H24  # noqa: E402

G = H24 / "G21"
BLUE, ORANGE, AQUA, VIOLET, GRAY, INK, MUTED = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#9a9893", "#0b0b0b", "#52514e"
QLAB = {"AGI2035": "AGI by 2035", "SI2050": "Superintelligence by 2050", "DOOM2100": "p(doom) by 2100"}
plt.rcParams.update({"font.size": 7.5, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False, "axes.titlesize": 8,
                     "axes.titleweight": "bold", "legend.frameon": False})


def load():
    ex = json.loads((G / "explore.json").read_text())
    syn = json.loads((G / "synthetic_validation.json").read_text())
    S = pl.read_parquet(G / "statements.parquet")
    sw = pl.read_parquet(G / "switch_on.parquet")
    hv = pl.read_parquet(G / "numeric_handverified.parquet")
    return ex, syn, S, sw, hv


def panel_raster(ax, S, sw):
    d1 = S.filter(pl.col("pt_date") == "2025-12-01")
    order = sw.filter(pl.col("role") != "late-joiner").sort("tau_offset_min", nulls_last=True)
    for y, r in enumerate(order.iter_rows(named=True)):
        m = d1.filter(pl.col("agent") == r["agent"])["min_from_open"].to_numpy()
        ax.plot(m, np.full_like(m, y), "|", color=GRAY, ms=5, mew=0.8)
        if r["role"] == "switched":
            ax.plot([r["tau_offset_min"]], [y], marker="v", color=BLUE, ms=6, zorder=3)
        lab = r["name"].replace("Claude ", "")
        ax.text(-6, y, lab + ("  (control)" if r["role"] != "switched" else ""), ha="right", va="center", fontsize=6.5, color=INK)
    tau_star = float(np.median(order.filter(pl.col("role") == "switched")["tau_offset_min"].to_numpy()))
    ax.axvline(tau_star, color=BLUE, lw=0.8, ls="--")
    ax.text(tau_star + 3, -0.9, f"τ* = {tau_star:.0f} min", color=BLUE, fontsize=6.5)
    ax.set_yticks([]); ax.set_xlim(0, 242); ax.set_xlabel("minutes after the window opened, 12-01")
    ax.set_title("a  Switch-on: first read of a teammate's forecast (▼)", loc="left")
    ax.spines["left"].set_visible(False)


def panel_levels(ax, ex):
    r = ex["O1"]["n32_ghat"]["a_all"]
    x = np.arange(2)
    for lab, col, off in (("raw", ORANGE, -0.08), ("res", BLUE, 0.08)):
        rr = r[lab]
        ax.plot(x + off, [rr["A_pre"], rr["A_post"]], "-o", color=col, ms=4, lw=1.5, label="raw" if lab == "raw" else "ĝ removed")
        ax.axhspan(0, rr["N3_rot"]["A_post_q95"], color=GRAY, alpha=0.15, lw=0)
    rd = ex["O1"]["n32_ghat"]["c_docs_all"]["res"]
    ax.plot(x + 0.2, [rd["A_pre"], rd["A_post"]], "-s", color=AQUA, ms=4, lw=1.5, label="documents, ĝ removed")
    ax.set_xticks(x); ax.set_xticklabels(["pre τ_i", "post τ_i (60 min)"]); ax.set_xlim(-0.4, 1.5)
    ax.set_ylabel("mean pairwise cosine A"); ax.set_ylim(0, 0.8)
    ax.text(1.45, 0.02, "rotation null (95%)", ha="right", fontsize=6, color=MUTED)
    ax.legend(fontsize=6, loc="upper right")
    ax.set_title("b  Alignment before vs after switch-on", loc="left")


def panel_placebo(ax, ex, compact=False):
    n2 = np.array([w["res"]["dA"] for w in ex["N2"]])
    r = ex["O1"]["n32_ghat"]["a_all"]["res"]
    n1 = np.array([p["dA"] for p in r["N1"]])
    rng = np.random.default_rng(0)
    ax.scatter(rng.uniform(-0.18, 0.18, len(n2)), n2, s=10, color=GRAY, label=f"other regime-I kickoff days (N2, n={len(n2)})", zorder=2)
    ax.scatter(1 + rng.uniform(-0.12, 0.12, len(n1)), n1, s=12, facecolor="white", edgecolor=ORANGE, lw=1, label="placebo switch times in #21 (N1)", zorder=2)
    for xx, q in ((0, np.quantile(n2, 0.9)), (1, r["N1_q90"])):
        ax.plot([xx - 0.25, xx + 0.25], [q, q], color=MUTED, lw=0.8, ls=":")
    ci = r["boot"]["dA_ci90"]
    ax.errorbar([2], [r["dA"]], yerr=[[r["dA"] - ci[0]], [ci[1] - r["dA"]]], fmt="o", color=BLUE, ms=6, capsize=2, lw=1.2, label="#21 at τ_i (90% CI)", zorder=3)
    rd = ex["O1"]["n32_ghat"]["c_docs_all"]["res"]
    cid = rd["boot"]["dA_ci90"]
    ax.errorbar([2.5], [rd["dA"]], yerr=[[rd["dA"] - cid[0]], [cid[1] - rd["dA"]]], fmt="s", color=AQUA, ms=5, capsize=2, lw=1.2, label="#21 documents", zorder=3)
    ax.axhline(0, color=MUTED, lw=0.5)
    ax.set_xticks([0, 1, 2.25]); ax.set_xticklabels(["N2", "N1", "#21"])
    ax.set_ylabel("ΔA (ĝ removed), post − pre"); ax.set_xlim(-0.5, 2.8)
    if compact:
        ax.set_xticks([0, 1, 2.25]); ax.set_xticklabels(["other\nweeks (N2)", "placebo\ntimes (N1)", "#21 at τ_i\n(● chat, ■ docs)"])
    else:
        ax.legend(fontsize=6, loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=2, handletextpad=0.3)
    ax.set_title("c  Step at switch-on vs placebos" if not compact else "No alignment step at switch-on", loc="left")


def panel_ramp(ax, ex):
    rp = ex["ramp"]
    x = [r["idx"] for r in rp]
    ax.plot(x, [r["A_raw"] for r in rp], "-o", color=ORANGE, ms=3, lw=1.2, label="raw")
    ax.plot(x, [r["A_res"] for r in rp], "-o", color=BLUE, ms=3, lw=1.5, label="ĝ removed")
    for k, d in enumerate(["12-01", "12-02", "12-03", "12-04", "12-05"]):
        ax.text(2 * k + 0.5, 0.05, d, ha="center", fontsize=6, color=MUTED)
    ax.axvline(6 - 0.5, color=MUTED, lw=0.6, ls="--"); ax.text(5.6, 0.62, "DeepSeek joins;\nshared tracker", fontsize=5.5, color=MUTED)
    ax.set_xticks(range(10)); ax.set_xticklabels([]); ax.set_ylim(0, 0.7)
    ax.set_xlabel("2-h blocks"); ax.set_ylabel("A per block (k = 4)")
    o3 = ex["O3"]
    ax.text(0.2, 0.62, f"G21b–c trend ρ = {o3['rho']:.2f} (p = {o3['p']:.2f})", fontsize=6, color=INK)
    ax.legend(fontsize=6, loc=(0.7, 0.15))
    ax.set_title("d  The coupling ramp over the week", loc="left")


def panel_numeric(ax, hv):
    xs = {"AGI2035": 0, "SI2050": 1, "DOOM2100": 2}
    for r in hv.iter_rows(named=True):
        x0 = xs[r["question"]]
        col = BLUE if r["seg_first"] == "pre" else (AQUA if r["t_first"].day == 1 else GRAY)
        ax.plot([x0 - 0.18, x0 + 0.18], [r["first"], r["last"]], "-o", color=col, ms=3, lw=1, alpha=0.9)
    ax.set_xticks([0, 1, 2]); ax.set_xticklabels(["AGI\nby 2035", "SI\nby 2050", "p(doom)\nby 2100"])
    ax.set_ylabel("stated probability (%)")
    ax.plot([], [], "-o", color=BLUE, ms=3, label="first value before τ_i")
    ax.plot([], [], "-o", color=AQUA, ms=3, label="first value on 12-01 after τ_i")
    ax.plot([], [], "-o", color=GRAY, ms=3, label="first stated 12-02 or later")
    ax.legend(fontsize=5.5, loc="lower left")
    ax.set_title("e  Anchor forecasts, first → last (hand-verified)", loc="left")


def panel_kappa(ax, ex, compact=False):
    num = ex["numeric"]
    rows = [("pre-registered\nextractor", num["prereg"]["self"]), ("amended\nextractor (A1)", num["A1"]["self"]),
            ("hand-\nverified", num["hand"]["all"]), ("hand-verified,\nfirst on 12-01", num["hand"]["day1_first"])]
    for i, (lab, r) in enumerate(rows):
        ax.bar(i, r["kappa"], width=0.55, color=BLUE if i < 2 else AQUA, zorder=2)
        ax.plot([i - 0.32, i + 0.32], [r["kappa_null_q90"]] * 2, color=INK, lw=1, ls=":", zorder=3)
        ax.text(i, r["kappa"] + 0.03, f"p={r['kappa_perm_p']:.3f}" if r["kappa_perm_p"] >= 0.001 else "p<0.001", ha="center", fontsize=5.5, color=INK)
    short = ["pre-reg.", "amended", "hand", "hand,\n12-01"]
    ax.set_xticks(range(4)); ax.set_xticklabels(short if compact else [r[0] for r in rows], fontsize=5.5 if compact else 6)
    ax.axhline(0, color=MUTED, lw=0.5); ax.set_ylim(0, 0.85)
    ax.set_ylabel("DeGroot pull κ")
    ax.text(-0.45, 0.8, "dotted: independent-updating null, 90th pct" if not compact else "dotted: null 90th pct", fontsize=5, color=MUTED, ha="left")
    ax.set_title("f  Numeric herding depends on extraction" if not compact else "Numeric herding is an extraction artifact", loc="left")


def panel_power(ax, syn):
    for h1, ls, lab in ((0.0, "-", "no kickoff transient"), (1.0, "--", "with kickoff transient")):
        cs = [c for c in syn["content"] if c["h1"] == h1]
        ax.plot([c["true_bJ_post"] for c in cs], [c["power_rule"] for c in cs], "o" + ls, color=VIOLET, ms=3, lw=1.2, label=lab)
    ax.axhline(0.5, color=MUTED, lw=0.5, ls=":")
    ax.set_xlabel("true βJ₀/n after switch-on (synthetic)"); ax.set_ylabel("detection rate (P1 rule)")
    ax.legend(fontsize=6, loc="lower right"); ax.set_ylim(0, 1.02)
    ax.set_title("g  Synthetic power at #21 sampling", loc="left")


def main():
    ex, syn, S, sw, hv = load()
    fig = plt.figure(figsize=(8.27, 11.0))
    gs = fig.add_gridspec(4, 2, height_ratios=[1.0, 1.0, 1.0, 1.0], hspace=0.55, wspace=0.3, top=0.875, bottom=0.05, left=0.17, right=0.97)
    panel_raster(fig.add_subplot(gs[0, :]), S, sw)
    panel_levels(fig.add_subplot(gs[1, 0]), ex)
    panel_placebo(fig.add_subplot(gs[1, 1]), ex)
    panel_ramp(fig.add_subplot(gs[2, 0]), ex)
    panel_numeric(fig.add_subplot(gs[2, 1]), hv)
    panel_kappa(fig.add_subplot(gs[3, 0]), ex)
    panel_power(fig.add_subplot(gs[3, 1]), syn)
    r = ex["O1"]["n32_ghat"]["a_all"]["res"]
    fig.text(0.04, 0.965, "H24 · Forecast week (#21): does comparing forecasts switch the coupling on?", fontsize=11, weight="bold", color=INK)
    fig.text(0.04, 0.935,
             f"The switch is on day 1 (median 50 min after the open), not mid-week. Residual alignment does not step up at it "
             f"(ΔA = {r['dA']:+.3f}; inside both placebo\ndistributions), but it is high from the first hour (A ≈ 0.33 vs rotation null ≈ 0.03) "
             "and ramps over the week. Numeric herding passes as pre-registered but\ndisappears after a hand audit of the extracted values. "
             "Exploratory, one week, N = 7–9.", fontsize=7, color=MUTED, va="top")
    (CARD / "figures").mkdir(exist_ok=True)
    fig.savefig(CARD / "figures/summary.pdf")
    (CARD / "G21/figures").mkdir(parents=True, exist_ok=True)
    fig.savefig(CARD / "G21/figures/G21_panels.pdf")
    plt.close(fig)

    fig, ax = plt.subplots(1, 2, figsize=(4.3, 2.6), gridspec_kw={"width_ratios": [1.05, 1]})
    panel_placebo(ax[0], ex, compact=True)
    panel_kappa(ax[1], ex, compact=True)
    ax[0].set_title("a  Alignment step at switch-on", loc="left", fontsize=7)
    ax[1].set_title("b  Numeric herding κ", loc="left", fontsize=7)
    ax[0].set_ylabel("ΔA, post − pre", fontsize=6.5); ax[1].set_ylabel("κ", fontsize=6.5)
    for a in ax:
        a.tick_params(labelsize=5.5)
    fig.tight_layout(pad=0.3)
    fig.savefig(CARD / "figures/summary_obs.pdf")
    print("figures written")


if __name__ == "__main__":
    main()
