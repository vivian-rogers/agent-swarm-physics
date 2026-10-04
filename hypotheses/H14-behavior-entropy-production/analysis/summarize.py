"""H14 cross-period synthesis (exploratory round 1): reads each period's results, scores the pre-registered
predictions, runs the cross-period family meta-test and the agent-trait invariance check, fills the G<NN>/README.md
result sections (goalperiod-subhypotheses/G<NN>/README.md), and draws the one-page summary (figures/summary_round1.pdf).

Usage: uv run python hypotheses/H14-behavior-entropy-production/analysis/summarize.py
Writes data/processed/H14-behavior-entropy-production/summary_round1.json.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h14lib as L  # noqa: E402,F401  (thread env)

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402

ROOT = HERE.parents[2]
DATA = ROOT / "data/processed/H14-behavior-entropy-production"
HYP = HERE.parent
FIG = HYP / "figures"
R3 = ["G37", "G38", "G39", "G40", "G41", "G42", "G44", "G51"]
ALL = ["G27"] + R3
MODE = {"G27": "K", "G37": "F", "G38": "C", "G39": "I", "G40": "C", "G41": "I", "G42": "I", "G44": "C", "G51": "I/K"}
P4_PRED = {"G27": True, "G37": False, "G38": True, "G39": False, "G40": True, "G41": False, "G42": False, "G44": False, "G51": True}
RNG = np.random.default_rng(20261003)


def load():
    res, ag = {}, {}
    for g in ALL:
        f = DATA / g / "results.json"
        if f.exists():
            res[g] = json.loads(f.read_text())
            ag[g] = pl.read_parquet(DATA / g / "agents.parquet")
    return res, ag


def holm(ps):
    ps = np.asarray(ps, float)
    order = np.argsort(ps)
    adj = np.empty_like(ps)
    m = len(ps)
    run = 0.0
    for r, i in enumerate(order):
        run = max(run, (m - r) * ps[i])
        adj[i] = min(1.0, run)
    return adj


# ============================================================================ cross-period tests
def family_meta(ag, periods, col="cfx_exc", nperm=10000):
    """Stratified permutation: lab labels permuted among agents within each period.
    T_diff = sum over periods of (mean Anthropic - mean OpenAI); T_eta = sum of eta^2."""
    blocks = []
    for g in periods:
        d = ag[g].filter(pl.col("eligible") & ~pl.col("lab").str.starts_with("Fine"))
        if col not in d.columns:
            continue
        d = d.filter(pl.col(col).is_not_nan())
        blocks.append((d[col].to_numpy(), np.array(d["lab"].to_list())))

    def stats(bl):
        td, te, k = 0.0, 0.0, 0
        for v, lab in bl:
            if (lab == "Anthropic").any() and (lab == "OpenAI").any():
                td += v[lab == "Anthropic"].mean() - v[lab == "OpenAI"].mean()
                k += 1
            te += L.eta2(v, lab)
        return td, te, k

    td, te, k = stats(blocks)
    nd, ne = np.empty(nperm), np.empty(nperm)
    for i in range(nperm):
        nd[i], ne[i], _ = stats([(v, RNG.permutation(lab)) for v, lab in blocks])
    per = []
    for v, lab in blocks:
        if (lab == "Anthropic").any() and (lab == "OpenAI").any():
            a, o = v[lab == "Anthropic"], v[lab == "OpenAI"]
            se = np.sqrt(a.var(ddof=1) / len(a) + o.var(ddof=1) / len(o)) if len(a) > 1 and len(o) > 1 else np.nan
            per.append((a.mean() - o.mean(), se))
    per = np.array(per)
    ok = np.isfinite(per[:, 1]) & (per[:, 1] > 0)
    w = 1 / per[ok, 1] ** 2
    mu = (w * per[ok, 0]).sum() / w.sum()
    Qc = (w * (per[ok, 0] - mu) ** 2).sum()
    I2 = max(0.0, (Qc - (ok.sum() - 1)) / Qc) if Qc > 0 else 0.0
    return {"col": col, "periods": periods, "k_periods_with_both": k, "sum_diff_anth_minus_openai": td,
            "p_two": float((1 + (np.abs(nd) >= abs(td)).sum()) / (nperm + 1)),
            "p_anth_gt_openai": float((1 + (nd >= td).sum()) / (nperm + 1)),
            "sum_eta2": te, "sum_eta2_null_mean": float(ne.mean()), "p_eta2": float((1 + (ne >= te).sum()) / (nperm + 1)),
            "ivw_diff": float(mu), "Q": float(Qc), "I2": float(I2), "per_period_diff": per[:, 0].tolist()}


def trait_stability(ag, periods, col="cfx_exc", min_periods=4, nperm=2000):
    """Agent-level invariance (CLAUDE.md exception (b)): within-period percentile ranks of an agent's excess EP,
    mean pairwise Spearman across period pairs (>= 5 common agents), vs. agent labels shuffled within periods."""
    tabs = {}
    for g in periods:
        d = ag[g].filter(pl.col("eligible") & pl.col(col).is_not_nan())
        v = d[col].to_numpy()
        r = (np.argsort(np.argsort(v)) + 0.5) / len(v)
        tabs[g] = dict(zip(d["agent"].to_list(), r))
    cnt = {}
    for g in tabs:
        for a in tabs[g]:
            cnt[a] = cnt.get(a, 0) + 1
    keep = {a for a, c in cnt.items() if c >= min_periods}

    def mean_rho(T):
        rs = []
        gs = list(T)
        for i in range(len(gs)):
            for j in range(i + 1, len(gs)):
                com = [a for a in T[gs[i]] if a in T[gs[j]] and a in keep]
                if len(com) >= 5:
                    rs.append(spearmanr([T[gs[i]][a] for a in com], [T[gs[j]][a] for a in com])[0])
        return float(np.mean(rs)) if rs else np.nan, len(rs)

    obs, npairs = mean_rho(tabs)
    null = []
    for _ in range(nperm):
        T2 = {}
        for g, dct in tabs.items():
            ks = list(dct)
            vs = RNG.permutation(list(dct.values()))
            T2[g] = dict(zip(ks, vs))
        null.append(mean_rho(T2)[0])
    null = np.array(null)
    # variance share of agent identity across periods (eta^2 of ranks by agent)
    vals, labs = [], []
    for g, dct in tabs.items():
        for a, r in dct.items():
            if a in keep:
                vals.append(r)
                labs.append(a)
    e_obs = L.eta2(np.array(vals), np.array(labs)) if vals else np.nan
    return {"col": col, "n_agents": len(keep), "n_period_pairs": npairs, "mean_spearman": obs,
            "null_mean": float(np.nanmean(null)), "p": float((1 + (null >= obs).sum()) / (len(null) + 1)) if np.isfinite(obs) else np.nan,
            "eta2_agent_of_ranks": e_obs}


# ============================================================================ verdicts
def evaluate(g, r):
    """Score the period's pre-registered items; returns dict of booleans and the verdict."""
    out = {}
    out["P2"] = bool(r.get("P2_frac_above_null_newton", np.nan) >= 0.8)
    cyc = r["P5_cycles"]
    if g == "G27":
        out["P5"] = bool((1 - cyc["work>chat>cons"]["frac_pos"]) >= 0.75 and r["P5_dominant_cycle"] == "work>chat>cons")
    else:
        out["P5"] = bool(cyc["work>chat>idle"]["frac_pos"] >= 0.75 and cyc["work>chat>cons"]["frac_pos"] >= 0.75
                         and r["P5_dominant_cycle"] in ("work>chat>idle", "work>chat>cons"))
    c = r.get("collective", {})
    if "delta_mf_p" in c:
        det = c["delta_mf_p"] < 0.05
        out["P4_detected"] = bool(det)
        out["P4_as_predicted"] = bool(det == P4_PRED[g])
    else:
        out["P4_as_predicted"] = None
    if g in ("G38", "G51"):
        f = r["family_newton_exc"]
        out["P3_period"] = bool(f.get("eta2", 0) >= 0.30 and f.get("eta2_p", 1) < 0.05)
    return out


def verdict(g, ev, p6=None):
    if not ev["P2"]:
        return "failed"
    items = [ev["P5"]]
    if g == "G27":
        items.append(bool(p6))
    elif g == "G37":
        pass
    else:
        if ev.get("P4_as_predicted") is not None:
            items.append(ev["P4_as_predicted"])
        if g == "G51":
            items.append(ev.get("P3_period", False))
    return "supported" if all(items) else "mixed"


# ============================================================================ README result sections
def fmt(x, nd=3):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "–"
    if isinstance(x, (int, np.integer)):
        return str(x)
    return f"{x:.{nd}f}" if abs(x) >= 10 ** (-nd) or x == 0 else f"{x:.1e}"


def period_section(g, r, a, ev, v, p6_info):
    el = a.filter(pl.col("eligible"))
    c = r.get("collective", {})
    cyc = r["P5_cycles"]
    f = r["family_newton_exc"]
    fc = r.get("family_cfx_exc", {})
    lines = ["## Result", f"*Run 2026-10-03 (exploratory, non-holdout). Primary single-agent estimator: H05's cross-fitted Newton bound "
             f"(the pre-registered switch rule did not fire); companion `cfx` = cross-fitted exact dual minus its DB-null mean. DB surrogates: {r['R_db']} per agent.*", "",
             "| Prediction | Observed | Null / reference | Verdict |", "| --- | --- | --- | --- |"]
    lines.append(f"| P2: ≥ 80% of agents (≥ 1,000 transitions) above the DB-surrogate 95th pct | "
                 f"{fmt(r['P2_frac_above_null_newton'], 2)} of {r['P2_n']} (cfx: {fmt(r['P2_frac_above_null_cfx'], 2)}); "
                 f"median Σ_i {fmt(r['median_newton'])} (Newton), excess {fmt(r['median_newton_exc'])}; cfx excess {fmt(r['median_cfx_exc'])} nats/transition | "
                 f"5% expected under the null | {'✓' if ev['P2'] else '✗'} |")
    lines.append(f"| P2 (minute grid): ≥ 60% above null; per-hour lower than on turns for ≥ 80% | "
                 f"{fmt(r.get('P2_frac_above_null_min'), 2)} of {r.get('P2_n_min')}; per-hour lower for "
                 f"{fmt(r.get('P2_frac_min_per_hour_below_turn'), 2)} | | "
                 f"{'✓' if (r.get('P2_frac_above_null_min', 0) >= 0.6 and r.get('P2_frac_min_per_hour_below_turn', 0) >= 0.8) else '✗'} |")
    if g == "G27":
        w = cyc["work>chat>cons"]
        lines.append(f"| P5: consolidate → chat → work → consolidate in ≥ 75%, dominant | reverse-orientation share "
                     f"{fmt(1 - w['frac_pos'], 2)}; dominant cycle: {r['P5_dominant_cycle']} | sign test p = {fmt(w['sign_test_p'])} | "
                     f"{'✓' if ev['P5'] else '✗'} |")
        lines.append(f"| P6: median ≥ 2× every regime-III median | {p6_info} | | {'✓' if p6_info.startswith('holds') else '✗'} |")
    else:
        a1, a2 = cyc["work>chat>idle"], cyc["work>chat>cons"]
        lines.append(f"| P5: work → chat → idle → work and work → chat → consolidate → work positive in ≥ 75%; one dominant | "
                     f"{fmt(a1['frac_pos'], 2)} and {fmt(a2['frac_pos'], 2)} positive; dominant: {r['P5_dominant_cycle']} | "
                     f"sign tests p = {fmt(a1['sign_test_p'])}, {fmt(a2['sign_test_p'])} | {'✓' if ev['P5'] else '✗'} |")
    if "delta_mf" in c:
        lines.append(f"| P4: ΔΣ_MF {'above' if P4_PRED[g] else 'within'} the cross-day null | excess {fmt(c['delta_mf_exc'], 4)} "
                     f"(observed {fmt(c['delta_mf'], 4)}), p = {fmt(c['delta_mf_p'])}; ΔΣ_PW excess {fmt(c['delta_pw_exc'], 4)}, p = {fmt(c['delta_pw_p'])} | "
                     f"null mean {fmt(c['delta_mf_null_mean'], 4)} ± {fmt(c['delta_mf_null_sd'], 4)} (MF), "
                     f"{fmt(c['delta_pw_null_mean'], 4)} ± {fmt(c['delta_pw_null_sd'], 4)} (PW); N = {c['N']}, {c['n_days']} days | "
                     f"{'✓' if ev.get('P4_as_predicted') else '✗'} |")
        lines.append(f"| HH67 strong form: ΔΣ > Σ_1 | ΔΣ_MF excess / Σ_1 = {fmt(c.get('ratio_delta_mf_exc_to_sigma1_cfx'), 3)}; "
                     f"ΔΣ_PW excess / Σ_1 = {fmt(c.get('ratio_delta_pw_exc_to_sigma1_cfx'), 3)} (Σ_1 = Σ_i cfx on the grid = {fmt(c['sigma1_cfx_sum'], 4)}) | | "
                     f"{'strong form fails' if max(c.get('ratio_delta_mf_exc_to_sigma1_cfx', 0), c.get('ratio_delta_pw_exc_to_sigma1_cfx', 0)) < 1 else 'strong form holds'} |")
    else:
        lines.append(f"| P4 | not estimable: {c.get('skipped', '')} | | – |")
    if "eta2" in f:
        lines.append(f"| P3 (family, descriptive here unless G38/G51) | η²_lab = {fmt(f['eta2'], 2)} (perm p = {fmt(f['eta2_p'])}, chance {fmt(f['eta2_null_mean'], 2)}); "
                     f"adjusted for shell share and log n: {fmt(f.get('eta2_adj'), 2)} (p = {fmt(f.get('eta2_adj_p'))}); "
                     f"Anthropic − OpenAI = {fmt(f.get('anth_minus_openai'), 4)} (two-sided p = {fmt(f.get('p_two'))}) | labs: "
                     f"{', '.join(f'{k} {n}' for k, n in f['labs'].items())}; cfx companion η² {fmt(fc.get('eta2'), 2)} (p {fmt(fc.get('eta2_p'))}) | "
                     f"{('✓' if ev.get('P3_period') else '✗') if g in ('G38', 'G51') else 'descriptive'} |")
    lines.append("")
    lines.append(f"**Verdict: {v}.** Other numbers: act-scheme share above null {fmt(r.get('act_frac_above_null'), 2)}; "
                 f"order 2 beats order 1 (held-out likelihood) for {fmt(r.get('P8_frac_order2_beats_order1'), 2)} of agents, "
                 f"order-2 bound > pair bound for {fmt(r.get('P8_frac_cfx3_gt_cfx'), 2)}; removing consolidate loses a median "
                 f"{fmt(r.get('P9_median_share_lost'), 2)} of the excess (the rest stays above null for {fmt(r.get('P9_frac_nocons_above_null'), 2)}); "
                 f"median plug-in EP share in consolidate transitions {fmt(r.get('median_plugin_share_consolidate'), 2)}.")
    if "split" in r:
        sp = r["split"]
        lines.append(f"Split at {sp['date']} (descriptive): median change in excess b − a = {fmt(sp['median_b_minus_a'], 4)} "
                     f"(Wilcoxon p = {fmt(sp['wilcoxon_p'])}, n = {sp['n']}).")
    if r.get("collective_weekly"):
        wk = r["collective_weekly"]
        lines.append("Weekly sub-blocks (collective, 20 surrogates each): " + "; ".join(
            f"{k}: ΔΣ_MF exc {fmt(w['delta_mf_exc'], 4)} (p {fmt(w['delta_mf_p'], 2)}), ΔΣ_PW exc {fmt(w['delta_pw_exc'], 4)} (p {fmt(w['delta_pw_p'], 2)})"
            for k, w in wk.items()) + ".")
    lines.append("")
    lines.append("Per-agent table (eligible agents; excess = estimate − DB-null mean, nats/transition; Newton primary, cfx companion):")
    lines.append("")
    lines.append("| Agent | Lab | Transitions | Σ_i Newton | p | cfx excess | p | Newton excess/h | Minute excess/h | work>chat>idle A | work>chat>cons A |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for row in el.sort("newton_exc", descending=True).iter_rows(named=True):
        lines.append(f"| {row['name']} | {row['lab']} | {row['n_trans']} | {fmt(row['newton'])} | {fmt(row['newton_p'])} | {fmt(row['cfx_exc'])} | {fmt(row['cfx_p'])} | "
                     f"{fmt(row.get('newton_exc_per_hour'), 2)} | {fmt(row.get('min_newton_exc_per_hour'), 2)} | "
                     f"{fmt(row['aff_work>chat>idle'], 2)} | {fmt(row['aff_work>chat>cons'], 2)} |")
    lines.append("")
    lines.append(f"Figures: [`figures/period_summary.pdf`](figures/period_summary.pdf). Data: `data/processed/H14-behavior-entropy-production/{g}/` "
                 "(`agents.parquet`, `results.json`). Code: `analysis/run_period.py --period " + g + "`.")
    lines.append("")
    lines.append("## Scorecard (period-specific axes)")
    lines.append(f"- **C (adequacy):** single-agent arrows beat the DB surrogate for {fmt(r['P2_frac_above_null_newton'], 2)} of test agents "
                 f"(held-out, day-blocked cross-fit). Collective term vs. cross-day null: "
                 f"{'p = ' + fmt(c.get('delta_mf_p')) + ' (MF), ' + fmt(c.get('delta_pw_p')) + ' (PW)' if 'delta_mf' in c else 'not estimable'}.")
    lines.append(f"- **D (unfitted):** cycle orientations (P5) are not fitted by the EP estimator: {'as predicted' if ev['P5'] else 'not as predicted'}.")
    lines.append("- **G (ground truth):** the consolidate-linked cycle is scaffold-imposed (consolidation cadence); see the card for how much EP it carries.")
    return "\n".join(lines) + "\n"


def write_readme(g, v, section):
    p = HYP / "goalperiod-subhypotheses" / g / "README.md"
    t = p.read_text()
    t = re.sub(r"^\*\*Verdict:\*\*.*$", f"**Verdict:** {v}", t, count=1, flags=re.M)
    head = t.split("## Result")[0]
    notes = t.split("## Notes", 1)[1] if "## Notes" in t else "\n"
    p.write_text(head + section + "\n## Notes" + notes)


# ============================================================================ figure
def summary_figure(res, ag, S):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "serif", "font.size": 6.5, "axes.linewidth": 0.5, "pdf.fonttype": 42})
    fig = plt.figure(figsize=(8.27, 11.0))
    gs = fig.add_gridspec(4, 2, height_ratios=[0.55, 1, 1, 1], hspace=0.55, wspace=0.3)
    ax0 = fig.add_subplot(gs[0, :]); ax0.axis("off")
    ax0.text(-0.05, 1, S["headline_text"], va="top", fontsize=6.2, family="serif")
    gs_ = [g for g in ALL if g in res]
    x = np.arange(len(gs_))
    modec = {"C": "#c2662d", "I": "#3f6fb5", "F": "#2a8a4a", "K": "#8a5ab5", "I/K": "#555555"}
    # A: per-period excess distribution
    ax = fig.add_subplot(gs[1, 0])
    for i, g in enumerate(gs_):
        v = ag[g].filter(pl.col("eligible"))["newton_exc"].drop_nans().to_numpy()
        ax.boxplot(v, positions=[i], widths=0.6, showfliers=False, patch_artist=True,
                   boxprops=dict(facecolor=modec[MODE[g]], alpha=0.5, lw=0.5), medianprops=dict(color="k", lw=0.8),
                   whiskerprops=dict(lw=0.5), capprops=dict(lw=0.5))
        ax.scatter(np.full(len(v), i) + RNG.uniform(-0.2, 0.2, len(v)), v, s=2, color="k", zorder=3)
    ax.set_xticks(x); ax.set_xticklabels([f"{g}\n{MODE[g]}" for g in gs_], fontsize=5.5)
    ax.set_ylabel("Σ_i (Newton) − DB-null mean (nats/transition)"); ax.set_title("A. Single-agent arrow of time per period (turns, coarse)", fontsize=7)
    # B: fraction above null
    ax = fig.add_subplot(gs[1, 1])
    ax.bar(x - 0.27, [res[g]["P2_frac_above_null_newton"] for g in gs_], 0.27, color="#3f6fb5", label="coarse 6 states, turns")
    ax.bar(x, [res[g].get("P2_frac_above_null_min", np.nan) for g in gs_], 0.27, color="#2a8a4a", label="coarse, minute grid")
    ax.bar(x + 0.27, [res[g].get("act_frac_above_null", np.nan) for g in gs_], 0.27, color="#c2662d", label="fine action classes, turns")
    ax.axhline(0.8, color="k", ls="--", lw=0.5); ax.axhline(0.05, color="r", ls=":", lw=0.5)
    ax.set_xticks(x); ax.set_xticklabels(gs_, fontsize=5.5); ax.set_ylim(0, 1.05)
    ax.set_ylabel("share of agents above DB null (p < 0.05)"); ax.set_title("B. Share of agents with an arrow (Newton vs DB null)", fontsize=7); ax.legend(frameon=False, fontsize=5.5, loc="lower right")
    # C: family means per period
    ax = fig.add_subplot(gs[2, 0])
    from run_period import LAB_COL
    labs = sorted({l for g in gs_ for l in ag[g].filter(pl.col("eligible"))["lab"].to_list() if not l.startswith("Fine")})
    for l in labs:
        ys = []
        for g in gs_:
            v = ag[g].filter(pl.col("eligible") & (pl.col("lab") == l))["newton_exc"].drop_nans().to_numpy()
            ys.append(v.mean() if len(v) else np.nan)
        ax.plot(x, ys, "-o", ms=2.5, lw=0.8, color=LAB_COL.get(l, "#999"), label=l)
    ax.set_xticks(x); ax.set_xticklabels(gs_, fontsize=5.5)
    ax.set_ylabel("lab mean excess (nats/transition)")
    fm = S["family_meta"]
    ax.set_title(f"C. P3 lab means; stratified η² p = {fm['p_eta2']:.2f}, Anth−OpenAI p = {fm['p_two']:.2f}", fontsize=7)
    ax.legend(frameon=False, fontsize=5, ncol=2)
    # D: collective
    ax = fig.add_subplot(gs[2, 1])
    for k, (key, colr) in enumerate((("delta_mf", "#2a8a4a"), ("delta_pw", "#3f6fb5"))):
        ys, es = [], []
        for g in gs_:
            c = res[g].get("collective", {})
            ys.append(c.get(f"{key}_exc", np.nan) / c["N"] if "N" in c else np.nan)
            es.append(1.645 * c.get(f"{key}_null_sd", np.nan) / c["N"] if "N" in c else np.nan)
        ax.errorbar(x + (k - 0.5) * 0.3, ys, yerr=es, fmt="o", ms=3, color=colr, lw=0.6, capsize=1.5, label=f"{key} excess (bar = 1.645 null SD)")
    ax.axhline(0, color="k", lw=0.5)
    ax.set_xticks(x); ax.set_xticklabels(gs_, fontsize=5.5)
    ax.set_ylabel("ΔΣ − cross-day null mean, per agent (nats/min)"); ax.set_title("D. P4 collective term (HH67) on the minute grid", fontsize=7)
    ax.legend(frameon=False, fontsize=5.5)
    # E: cycles
    ax = fig.add_subplot(gs[3, 0])
    from run_period import CYCLES
    for k, nm in enumerate(CYCLES):
        ax.plot(x, [res[g]["P5_cycles"][nm]["frac_pos"] for g in gs_], "-o", ms=2.5, lw=0.8, label=nm)
    ax.axhline(0.75, color="k", ls="--", lw=0.5); ax.axhline(0.25, color="k", ls="--", lw=0.5)
    ax.set_xticks(x); ax.set_xticklabels(gs_, fontsize=5.5); ax.set_ylim(0, 1.02)
    ax.set_ylabel("share of agents with positive affinity"); ax.set_title("E. P5 lump4 cycle orientation (HH56)", fontsize=7)
    ax.legend(frameon=False, fontsize=5.5)
    # F: synthetic
    ax = fig.add_subplot(gs[3, 1]); ax.axis("off")
    ax.text(-0.05, 1, S.get("synthetic_text", ""), va="top", fontsize=5.6, family="serif")
    ax.set_title("F. Synthetic validation (axis F)", fontsize=7, loc="left")
    fig.savefig(FIG / "summary_round1.pdf")
    plt.close(fig)


# ============================================================================ main
def main():
    res, ag = load()
    S = {"periods": list(res)}
    r3 = [g for g in R3 if g in res]
    S["family_meta"] = family_meta(ag, r3, "newton_exc")
    S["family_meta_cfx"] = family_meta(ag, r3, "cfx_exc")
    S["family_meta_per_hour"] = family_meta(ag, r3, "newton_exc_per_hour")
    S["family_meta_minute"] = family_meta(ag, r3, "min_newton_exc")
    S["family_meta_nocons"] = family_meta(ag, r3, "nocons_newton_exc")
    S["trait"] = trait_stability(ag, r3, "newton_exc")
    S["trait_cfx"] = trait_stability(ag, r3, "cfx_exc")
    S["trait_per_hour"] = trait_stability(ag, r3, "newton_exc_per_hour")
    S["trait_minute"] = trait_stability(ag, r3, "min_newton_exc")
    # P4 Holm across regime-III periods
    ps = [res[g]["collective"].get("delta_mf_p", np.nan) for g in r3]
    ok = [i for i, p in enumerate(ps) if np.isfinite(p)]
    adj = holm([ps[i] for i in ok]) if ok else []
    S["P4_holm_mf"] = {r3[i]: float(a) for i, a in zip(ok, adj)}
    pspw = [res[g]["collective"].get("delta_pw_p", np.nan) for g in r3]
    okp = [i for i, p in enumerate(pspw) if np.isfinite(p)]
    S["P4_holm_pw"] = {r3[i]: float(a) for i, a in zip(okp, holm([pspw[i] for i in okp]))} if okp else {}
    # P6
    med = {g: res[g]["median_newton"] for g in res}
    if "G27" in res:
        ratio = {g: med["G27"] / med[g] if med[g] > 0 else np.inf for g in r3}
        S["P6_ratio_G27_over_r3"] = ratio
        p6 = all(v >= 2 for v in ratio.values())
        p6_info = ("holds" if p6 else "fails") + f": G27 median {med['G27']:.4f} vs. regime-III medians " + ", ".join(f"{g} {med[g]:.4f}" for g in r3)
    else:
        p6, p6_info = None, "n/a"
    S["P6"] = p6
    # P7
    rank = sorted(r3, key=lambda g: med[g])
    S["P7_rank_low_to_high"] = rank
    S["P7_G37_lowest"] = bool(rank[0] == "G37") if "G37" in r3 else None
    mc = [med[g] for g in ("G38", "G40", "G44") if g in med]
    mi = [med[g] for g in ("G39", "G41", "G42") if g in med]
    S["P7_modeC_gt_modeI"] = bool(min(mc) > max(mi)) if mc and mi else None
    S["P7_modeC_mean_minus_modeI_mean"] = float(np.mean(mc) - np.mean(mi)) if mc and mi else None
    # verdicts + READMEs
    S["verdicts"] = {}
    for g in res:
        ev = evaluate(g, res[g])
        v = verdict(g, ev, p6 if g == "G27" else None)
        S["verdicts"][g] = {"verdict": v, **ev}
        write_readme(g, v, period_section(g, res[g], ag[g], ev, v, p6_info if g == "G27" else ""))
    # aggregate P2/P5/P8/P9 over regime III
    S["P2_periods_holding"] = [g for g in r3 if S["verdicts"][g]["P2"]]
    S["P5_periods_holding"] = [g for g in r3 if S["verdicts"][g]["P5"]]
    S["P4_periods_detected_mf"] = [g for g in r3 if S["verdicts"][g].get("P4_detected")]
    S["P8"] = {g: (res[g].get("P8_frac_order2_beats_order1"), res[g].get("P8_frac_cfx3_gt_cfx")) for g in res}
    S["P9"] = {g: res[g].get("P9_median_share_lost") for g in res}
    # synthetic text
    syn = DATA / "synthetic" / "synthetic_summary.json"
    S["synthetic_text"] = synthetic_text(json.loads(syn.read_text())) if syn.exists() else "synthetic summary missing"
    S["headline_text"] = headline_text(res, S)
    (DATA / "summary_round1.json").write_text(json.dumps(S, indent=1, default=float))
    summary_figure(res, ag, S)
    print(json.dumps({k: v for k, v in S.items() if k not in ("synthetic_text",)}, indent=1, default=float)[:8000])


def synthetic_text(sy):
    import textwrap
    s1 = sy.get("S1", [])

    def pick(st, n, lo, days=5):
        r = [x for x in s1 if x["sticky"] == st and x["n"] == n and x["days"] == days and abs(x["true_range"][0] - lo) < 1e-12]
        return r[0] if r else {}
    L_ = []
    for st in ("turn", "minute"):
        z, m, b = pick(st, 2000, 0), pick(st, 2000, 0.03), pick(st, 2000, 0.3)
        L_.append(f"S1 {st}-like chains, n=2,000 / 5 d: Σ=0 bias Newton {z.get('newton_mean', np.nan):+.4f}, plug-in {z.get('plugin_mean', np.nan):+.4f}; "
                  f"recovery at Σ≈{m.get('true_median', np.nan):.2f}: Newton {m.get('newton_recovery_median', np.nan):.2f}, cfx−null {m.get('cfx_bc_recovery_median', np.nan):.2f}; "
                  f"at Σ≈{b.get('true_median', np.nan):.1f}: Newton {b.get('newton_recovery_median', np.nan):.2f}, cfx−null {b.get('cfx_bc_recovery_median', np.nan):.2f}.")
    sz = [r for r in sy.get("S1n", []) if r["f"] == 0]
    if sz:
        L_.append(f"S1n DB-surrogate test size at Σ=0 (8 cells, cold and stationary starts): Newton {min(r['newton_reject'] for r in sz):.3f}–{max(r['newton_reject'] for r in sz):.3f}; "
                  f"power at Σ≈0.02 (n=2,000): {min(r['newton_reject'] for r in sy['S1n'] if r['f'] == 0.6 and r['n'] == 2000):.2f}–1.0.")
    c = sy.get("S2c", {})
    if c:
        L_.append(f"S2c family test (12 agents 6/4/2; equal true EP; n and stickiness differ): size Newton excess {c['size']['newton_excess']:.2f}, "
                  f"raw plug-in {c['size']['plugin']:.2f}, raw cfx {c['size']['cfx']:.2f}; power at 2×/3×: {c['power_x2']['newton_excess']:.2f}/{c['power_x3']['newton_excess']:.2f} "
                  f"(true values {c['power_x2']['true']:.2f}/{c['power_x3']['true']:.2f}: agent heterogeneity limits power).")
    s3 = sy.get("S3", {})
    if s3:
        L_.append("S3 kinetic Potts N=15, 5 d × 240 (cross-day null; reject rate MF / PW): " + "; ".join(
            f"{k} {v['delta_mf_reject']:.2f}/{v['delta_pw_reject']:.2f}" + (f" (true {v['true_collective_mean']:.2f})" if "true_collective_mean" in v else "")
            for k, v in s3.items()) + ".")
    return "\n".join(textwrap.fill(l, 78) for l in L_)


def headline_text(res, S):
    import textwrap
    r3 = [g for g in R3 if g in res]
    fm = S["family_meta"]
    t = S["trait"]
    lines = [
        "H14 round 1 (exploratory, non-holdout, 2026-10-03): entropy production of behavior-state sequences",
        f"P2 single-agent arrow: holds (≥80% of agents above the detailed-balance surrogate) in {len(S['P2_periods_holding'])}/{len(r3)} regime-III periods; "
        f"per-period medians of Σ_i (Newton) {min(res[g]['median_newton'] for g in r3):.3f}–{max(res[g]['median_newton'] for g in r3):.3f} nats/transition.",
        f"P3 per-family (HH19): stratified η² p = {fm['p_eta2']:.3f}; Anthropic − OpenAI summed over {fm['k_periods_with_both']} periods = {fm['sum_diff_anth_minus_openai']:+.4f} "
        f"(two-sided p = {fm['p_two']:.3f}, one-sided Anth>OpenAI p = {fm['p_anth_gt_openai']:.3f}; I² = {fm['I2']:.2f}). "
        f"Agent trait stability: mean pairwise Spearman {t['mean_spearman']:.2f} (null {t['null_mean']:.2f}, p = {t['p']:.3f}, {t['n_agents']} agents).",
        f"P4 collective (HH67): ΔΣ_MF above the cross-day null in {', '.join(S['P4_periods_detected_mf']) or 'no regime-III period'} (Holm-adjusted p: "
        + ", ".join(f"{g} {p:.2f}" for g, p in S["P4_holm_mf"].items()) + ").",
        f"P5 currents (HH56): holds in {len(S['P5_periods_holding'])}/{len(r3)} regime-III periods. P6 regime contrast: {S['P6']}. P7: G37 lowest = {S['P7_G37_lowest']}, mode C > mode I = {S['P7_modeC_gt_modeI']}.",
        "Verdicts: " + ", ".join(f"{g} {v['verdict']}" for g, v in S["verdicts"].items()),
    ]
    return "\n".join(textwrap.fill(l, 165) for l in lines)


if __name__ == "__main__":
    main()
