"""H10 figures from the JSON outputs: per-pair panels (NE34/figures/pair_<key>.pdf), the synthetic validation
figure (figures/synthetic.pdf) and the one-page summary (figures/summary.pdf). No statement text anywhere.

Usage: uv run python figures.py
"""
from __future__ import annotations

import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from h10data import DATA, HERE  # noqa: E402

HYP = HERE.parent
C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"   # reference palette slots 1-3 (all-pairs safe)
INK, INK2, GRID = "#0b0b0b", "#52514e", "#d9d8d4"
plt.rcParams.update({"font.size": 7, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "lines.linewidth": 1.5,
                     "axes.titlesize": 7.5, "legend.frameon": False, "legend.fontsize": 6})
PAIR_LABEL = {"11-12": "#11 → #12a (F → M)", "16-17": "#16 → #17 (F → I)", "37-38": "#37 → #38a (F → C)",
              "3-4": "#3 → #4a (F → C)", "5-6": "#5 → #6a (F → K)"}
SHORT = {"11-12": "11→12a", "16-17": "16→17", "37-38": "37→38a", "3-4": "3→4a*", "5-6": "5→6a*"}


def load(name):
    p = DATA / name
    return json.loads(p.read_text()) if p.exists() else None


def p1_panel(ax, r, title=True):
    t = r["agent_table"]
    k2 = np.array([a["k2F"] for a in t]); D = np.array([a["D"] for a in t])
    ax.scatter(k2, D, s=18, color=C1, zorder=3, edgecolor="white", linewidth=0.6)
    xs = np.linspace(min(0, k2.min()), k2.max() * 1.1, 50)
    ax.plot(xs, r["lam"] * xs, color=C2, lw=1.2, label=f"tilt Δ = λκ₂ (λ = {r['lam']:.1f})")
    ax.axhline(r["Dbar"], color=INK2, lw=1, ls="--", label="uniform translation (R1)")
    ax.axhline(0, color=GRID, lw=0.6)
    ax.set_xlabel("free-week signal variance κ₂ along ĝ")
    ax.set_ylabel("push Δᵢ = μᵢ(A) − μᵢ(F)")
    if title:
        ax.set_title(f"{PAIR_LABEL.get(r.get('key', ''), '')}  r = {r['P1_r']:.2f}, p = {r['P1_p']:.2f}, N = {r['N']}")
    ax.legend(loc="best")


def pair_figure(key, r):
    r["key"] = key
    fig, ax = plt.subplots(2, 2, figsize=(7.0, 5.2))
    # (a) shape: per-agent deviations in F and A
    dF, dA = np.array(r["dev_F"]), np.array(r["dev_A"])
    bins = np.linspace(min(dF.min(), dA.min()), max(dF.max(), dA.max()), 30)
    ax[0, 0].hist(dF, bins=bins, density=True, histtype="step", color=C1, lw=1.5, label="free week F")
    ax[0, 0].hist(dA, bins=bins, density=True, histtype="step", color=C2, lw=1.5, label="assigned week A")
    t = r["agent_table"]
    sF = np.sqrt(np.mean(dF ** 2)); sP = np.sqrt(max(np.mean(dF ** 2) + np.mean([a["k2pred"] - a["k2F"] for a in t]), 1e-12))
    xs = np.linspace(bins[0], bins[-1], 200)
    ax[0, 0].plot(xs, np.exp(-xs ** 2 / (2 * sP ** 2)) / np.sqrt(2 * np.pi) / sP, color=INK2, lw=1, ls="--",
                  label="tilt prediction for A (Gaussian)")
    ax[0, 0].set_xlabel("agent-window alignment minus agent mean (x − μᵢ)")
    ax[0, 0].set_ylabel("density"); ax[0, 0].legend(loc="upper right")
    ax[0, 0].set_title(f"(a) shape; push ε = {r['eps']:.2f} free-week SDs")
    # (b) P1
    p1_panel(ax[0, 1], r, title=False)
    ax[0, 1].set_title(f"(b) P1: r = {r['P1_r']:.2f}, p = {r['P1_p']:.2f}; MSE tilt/transl. = "
                       f"{r['P1_mse_tilt'] / r['P1_mse_trans']:.2f}")
    # (c) per-agent variance observed vs predicted
    k2A = np.array([a["k2A"] for a in t]); k2p = np.array([a["k2pred"] for a in t]); k2F = np.array([a["k2F"] for a in t])
    lim = [min(k2A.min(), k2p.min(), 0), max(k2A.max(), k2p.max()) * 1.1]
    ax[1, 0].plot(lim, lim, color=GRID, lw=1)
    ax[1, 0].scatter(k2p, k2A, s=18, color=C1, edgecolor="white", linewidth=0.6, zorder=3, label="tilt prediction")
    ax[1, 0].scatter(k2F, k2A, s=10, color=C3, marker="s", zorder=2, label="free-week κ₂ (no change)")
    ci = r.get("P2_rho_ci90", [np.nan, np.nan])
    ax[1, 0].set_xlabel("predicted κ₂ under the field"); ax[1, 0].set_ylabel("observed κ₂ in A")
    ax[1, 0].set_title(f"(c) P2: ρ = {r['P2_rho']:.2f} [{ci[0]:.2f}, {ci[1]:.2f}]; transverse ρ⊥ = {r['P2_rho_perp']:.2f}")
    ax[1, 0].legend(loc="lower right")
    # (d) P4
    labels = ["ĝ", "Ĉĝ (own free week)"] + [f"Ĉĝ (#{w} placebo)" for w in r.get("placebo_weeks", [])]
    vals = [r["P4_cos_g"], r["P4_cos_Cg"]] + list(r.get("P4_cos_Cplacebo", []) or [])
    cols = [INK2, C2] + [C1] * (len(vals) - 2)
    ax[1, 1].barh(range(len(vals)), vals, color=cols, height=0.5)
    ax[1, 1].axvline(r["P4_rot_p95"], color=INK, lw=1, ls=":", label="rotation null, 95th pct")
    ax[1, 1].set_yticks(range(len(vals))); ax[1, 1].set_yticklabels(labels)
    ax[1, 1].set_xlabel("cosine with the observed 32-d response Δμ")
    ci4 = r.get("P4_D_ci90", [np.nan, np.nan])
    ax[1, 1].set_title(f"(d) P4: D = {r['P4_D']:.3f} [{ci4[0]:.3f}, {ci4[1]:.3f}]")
    ax[1, 1].legend(loc="lower right")
    fig.suptitle(f"H10 · {PAIR_LABEL.get(key, key)} · P1 {r['v1']} · P2 {r['v2'].split(',')[0]}"
                 f"{')' if ',' in r['v2'] else ''} · P3/P4 descriptive · pair: {r['v']}", fontsize=7.5)
    fig.tight_layout()
    out = HYP / "goalperiod-subhypotheses" / "NE34" / "figures" / f"pair_{key}.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    plt.close(fig)


def synthetic_figure(S):
    rows = S["per_design"]
    fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.5))
    for d, col in zip(("11-12", "16-17", "37-38"), (C1, C2, C3)):
        for scen, mk in (("H", "o"), ("Hgibbs", "s")):
            rr = sorted([r for r in rows if r["design"] == d and r["scen"] == scen and r["het"] is None], key=lambda r: r["eps_med"])
            if not rr:
                continue
            e = [r["eps_med"] for r in rr]
            ax[0].plot(e, [r["P1_supported"] for r in rr], marker=mk, color=col, lw=1, ms=4,
                       label=f"{d} {'drive' if scen == 'H' else 'exact'}")
            ax[1].plot(e, [r["P2_rho_med"] for r in rr], marker=mk, color=col, lw=1, ms=4)
            ax[2].plot(e, [r["P2_cover0"] for r in rr], marker=mk, color=col, lw=1, ms=4)
    ax[0].set_xlabel("push ε (free-week SDs)"); ax[0].set_ylabel("P(P1 supported per pair)")
    ax[0].legend(fontsize=5)
    ax[1].axhline(0, color=GRID); ax[1].axhspan(-0.15, 0.15, color=GRID, alpha=0.4)
    ax[1].axvline(S.get("eps_max_P2", np.nan), color=INK, ls=":", lw=1)
    ax[1].set_xlabel("push ε"); ax[1].set_ylabel("median ρ (first-order tilt) under H")
    ax[2].axhline(0.9, color=GRID); ax[2].axhline(0.8, color=INK2, ls="--", lw=0.8)
    ax[2].set_xlabel("push ε"); ax[2].set_ylabel("90% CI covers ρ = 0 under H")
    fig.suptitle(f"Synthetic validation (mean-field O(32), village sampling); P2 testable for ε ≤ {S.get('eps_max_P2', np.nan):.2f}",
                 fontsize=7.5)
    fig.tight_layout()
    fig.savefig(HYP / "figures" / "synthetic.pdf")
    plt.close(fig)


def summary_figure(P, S, K, PS):
    fig = plt.figure(figsize=(8.5, 11))
    gs = fig.add_gridspec(5, 3, height_ratios=[0.55, 1, 1, 1, 0.9], hspace=0.75, wspace=0.38,
                          left=0.08, right=0.97, top=0.97, bottom=0.04)
    ax0 = fig.add_subplot(gs[0, :]); ax0.axis("off")
    comb = P["combined"]
    txt = ("H10 · Goals are Legendre pushes · exploratory round 1 (2026-10-03)\n"
           "Claim: P_assigned(state) ∝ P_free(state)·exp(λ·Σ y), with y = statement alignment with the assigned goal ĝ. "
           "One λ per pair is fitted to the mean push;\n"
           "everything else is predicted: who moves (P1), the variance (P2), the loop gain (P3) and the 32-d response direction (P4).\n"
           f"Combined verdicts: P1 {comb['P1']} (Stouffer p = {comb['P1_stouffer_p']:.3f}) · P2 {comb['P2']} · P3 {comb['P3']} · "
           f"P4 {comb['P4']} · overall {comb['overall'].upper()}")
    ax0.text(0, 1, txt, va="top", ha="left", fontsize=7.5, color=INK, wrap=True)
    prim = [k for k in ("11-12", "16-17", "37-38") if k in P["pairs"]]
    for j, k in enumerate(prim):
        ax = fig.add_subplot(gs[1, j])
        r = dict(P["pairs"][k]); r["key"] = k
        p1_panel(ax, r)
        if j:
            ax.get_legend().remove()
    # forest plots P2, P3, P4 across all pairs
    keys = list(P["pairs"].keys())
    for j, (stat, ci, lab, ref) in enumerate((("P2_rho", "P2_rho_ci90", "P2: ρ = ln(obs/pred variance along ĝ)", 0),
                                              ("dg", "dg_ci90", "P3: Δg = g_A − g_F (loop gain along ĝ)", 0),
                                              ("P4_D", "P4_D_ci90", "P4: D = cos(Δμ, Ĉĝ) − cos(Δμ, ĝ)", 0))):
        ax = fig.add_subplot(gs[2, j])
        for i, k in enumerate(keys):
            r = P["pairs"][k]
            v = r.get(stat, np.nan); c = r.get(ci, [np.nan, np.nan])
            col = C1 if r["primary"] else INK2
            lo, hi = np.clip(c[0], -3, 3), np.clip(c[1], -3, 3)
            ax.plot([lo, hi], [i, i], color=col, lw=1.5)
            ax.plot([np.clip(v, -3, 3)], [i], "o", color=col, ms=4)
            if stat == "P2_rho":
                ax.plot([np.clip(r.get("P2_rho_perp", np.nan), -3, 3)], [i], "s", color=C3, ms=3,
                        label="ρ⊥ transverse (unchanged pred.)" if i == 0 else None)
                ax.plot([np.clip(r.get("P2_rho_gauss", np.nan), -3, 3)], [i], "D", color=C2, ms=3,
                        label="ρ vs 'variance unchanged'" if i == 0 else None)
        ax.axvline(ref, color=INK, lw=0.6)
        if stat == "P2_rho":
            ax.axvspan(-np.log(1.5), np.log(1.5), color=GRID, alpha=0.4)
        ax.set_yticks(range(len(keys))); ax.set_yticklabels([SHORT.get(k, k) for k in keys], fontsize=6)
        ax.invert_yaxis(); ax.set_title(lab, fontsize=7)
        if stat == "P2_rho":
            ax.plot([], [], "o", color=C1, ms=4, label="ρ vs first-order tilt (90% CI)")
            ax.legend(loc="upper left", bbox_to_anchor=(-0.25, -0.12), fontsize=5, ncol=1)
            ax.text(1.0, -0.12, "* secondary (N = 4)\nshaded: |ρ| < ln 1.5", transform=ax.transAxes, ha="right", va="top", fontsize=5,
                    color=INK2)
        if j:
            ax.set_yticklabels([])
    # kickoffs
    ax = fig.add_subplot(gs[3, 0:2])
    if K:
        tr = K["transitions"]
        for reg, col in (("I", C1), ("II", C2), ("III", C3)):
            xs = [t["v"] for t in tr if t["regime"] == reg]; ys = [t["Dm"] for t in tr if t["regime"] == reg]
            ax.scatter(xs, ys, s=14, color=col, label=f"regime {reg}", edgecolor="white", linewidth=0.5)
            for t in tr:
                if t["regime"] == reg:
                    ax.annotate(f"{t['old']}→{t['new']}", (t["v"], t["Dm"]), fontsize=4.5, color=INK2)
        ax.axhline(0, color=GRID)
        sI = K.get("spearman_I", {})
        ax.set_title(f"P5 kickoffs: jump vs pre-period fluctuation along ĝ_new; Δm > 0 in "
                     f"{K.get('frac_positive_into_assigned', np.nan):.0%} of {K.get('n_into_assigned', 0)} transitions into assigned "
                     f"goals; Spearman (I) = {sI.get('rho', np.nan):.2f}", fontsize=6.5)
        ax.set_xlabel("pre-period κ₂ along ĝ_new"); ax.set_ylabel("Δm (first new − last old day)")
        ax.legend()
    # synthetic power box
    ax = fig.add_subplot(gs[3, 2]); ax.axis("off")
    lines = ["Synthetic validation (60 reps/cell)", f"P2 testable for ε ≤ {S.get('eps_max_P2', np.nan):.2f}", ""]
    for c in S["combined"]:
        if c["het"] is None and c["scen"] in ("H", "Hgibbs", "R1", "R3", "R4", "R5up", "R6", "Haniso"):
            lines.append(f"{c['scen']:<7} λ={c['lam']:<5g} P1 {c['P1_combined_supported']:.2f}  "
                         f"P4 {c['P4_combined_supported']:.2f}  H10✓ {c['H10_supported']:.2f}")
    ax.text(0, 1, "\n".join(lines), va="top", ha="left", fontsize=5.6, family="monospace", color=INK)
    # per-period descriptive table
    ax = fig.add_subplot(gs[4, :]); ax.axis("off")
    if PS:
        rows = []
        for k, v in PS.items():
            if "A_segment" in v:
                a = v["A_segment"]
                rows.append(f"{k:<9} assigned: all A days above free mean {v['A1_all_days_above']}; day1 − rest = "
                            f"{v['A2_day1_minus_rest']:+.3f}; g_A = {a.get('g', np.nan):.2f}; trend slope CI "
                            f"{np.round(a.get('slope_ci90', [np.nan, np.nan]), 3).tolist()}")
            else:
                rows.append(f"{k:<9} free: γ = {v.get('gamma', np.nan):+.2f}, unimodal {v.get('F1_unimodal')}, g = "
                            f"{v.get('g', np.nan):.2f} {np.round(v.get('g_ci90', [np.nan, np.nan]), 2).tolist()}, "
                            f"g⊥ = {v.get('g_perp_median', np.nan):.2f}; slope CI {np.round(v.get('slope_ci90', [np.nan, np.nan]), 3).tolist()}")
        ax.text(0, 1, "Per-period descriptives (G folders)\n" + "\n".join(rows), va="top", ha="left", fontsize=6,
                family="monospace", color=INK)
    fig.savefig(HYP / "figures" / "summary.pdf")
    plt.close(fig)


def summary_obs_figure(P, S):
    """Two panels for the one-page hypothesis summary (about 4.3 x 2.6 in)."""
    fig, ax = plt.subplots(1, 2, figsize=(4.3, 2.6), gridspec_kw={"width_ratios": [1.15, 1]})
    prim = [("11-12", C1, "o"), ("16-17", C2, "s"), ("37-38", C3, "^")]
    for k, col, mk in prim:
        r = P["pairs"][k]; t = r["agent_table"]
        k2 = np.array([a["k2F"] for a in t]); D = np.array([a["D"] for a in t])
        ax[0].scatter(k2 / k2.mean(), D / D.mean(), s=14, color=col, marker=mk, edgecolor="white", linewidth=0.4,
                      label=f"{SHORT[k]} (r = {r['P1_r']:+.2f})", zorder=3)
    xs = np.linspace(-0.6, 3.0, 10)
    ax[0].plot(xs, xs, color=INK, lw=1, label="tilt: Δᵢ ∝ κ₂ᵢ")
    ax[0].axhline(1, color=INK2, lw=0.8, ls="--", label="uniform translation")
    ax[0].set_xlabel("free-week fluctuation κ₂ᵢ / mean", fontsize=6)
    ax[0].set_ylabel("push Δᵢ / mean push", fontsize=6)
    ax[0].set_title("(a) who moves toward the goal", fontsize=6.5)
    ax[0].set_ylim(-1.4, 4.3)
    ax[0].legend(fontsize=4.4, loc="upper left", ncol=2, columnspacing=0.8, handletextpad=0.3)
    ax[0].tick_params(labelsize=5.5)
    # (b) variance change along g vs transverse, with the synthetic-H expectation at matched push
    rows = S["per_design"]
    for i, (k, col, mk) in enumerate(prim):
        r = P["pairs"][k]
        cand = [x for x in rows if x["design"] == k and x["scen"] == "H" and x["het"] is None]
        best = min(cand, key=lambda x: abs(x["eps_med"] - r["eps"]))
        ax[1].plot([r["P2_rho_gauss"]], [i], marker=mk, color=col, ms=5, ls="none")
        ax[1].plot([r["P2_rho_perp"]], [i - 0.22], marker="|", color=INK2, ms=7, mew=1.2, ls="none")
        ax[1].plot([best["P2_rho_gauss_med"]], [i + 0.22], marker="x", color=INK, ms=4, ls="none")
        ax[1].text(2.25, i, f"ε={r['eps']:.1f}", fontsize=4.8, va="center", color=INK2)
    ax[1].axvline(0, color=GRID, lw=0.8)
    ax[1].set_yticks(range(3)); ax[1].set_yticklabels([SHORT[k] for k, _, _ in prim], fontsize=5.5)
    ax[1].set_ylim(3.2, -0.5)
    ax[1].set_xlim(-1.9, 2.6)
    ax[1].set_xlabel("ln(var assigned / var free)", fontsize=6)
    ax[1].set_title("(b) variance along ĝ", fontsize=6.5)
    ax[1].plot([], [], "o", color=INK2, ms=4, label="observed along ĝ")
    ax[1].plot([], [], "|", color=INK2, ms=6, label="observed transverse")
    ax[1].plot([], [], "x", color=INK, ms=4, label="tilt (synthetic, same ε)")
    ax[1].legend(fontsize=4.6, loc="lower left")
    ax[1].tick_params(labelsize=5.5)
    fig.tight_layout(pad=0.4)
    fig.savefig(HYP / "figures" / "summary_obs.pdf")
    plt.close(fig)


def main():
    P, S, K, PS = load("NE34/pairs.json"), load("synthetic_summary.json"), load("NE34/kickoffs.json"), load("periods_summary.json")
    if S:
        synthetic_figure(S)
    if P:
        for k, r in P["pairs"].items():
            pair_figure(k, r)
        summary_figure(P, S, K, PS)
        summary_obs_figure(P, S)


if __name__ == "__main__":
    main()
