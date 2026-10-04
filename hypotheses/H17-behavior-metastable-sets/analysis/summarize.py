"""H17 cross-period synthesis: tests of the card's predictions, tables, figures and the one-page summary PDF.

Reads data/processed/H17-behavior-metastable-sets/G<NN>/result.json and synthetic/synthetic_rows.json.
Writes summary.json (same folder), figures in hypotheses/H17-behavior-metastable-sets/figures/, and per-period
scorecard/extra lines back into each result.json (for write_period_folders.py --results).

Usage: uv run python hypotheses/H17-behavior-metastable-sets/analysis/summarize.py
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("POLARS_MAX_THREADS", "2")

import collections
import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
CARD = HERE.parent
ROOT = CARD.parents[1]
sys.path.insert(0, str(HERE))
import h17lib as L  # noqa: E402
import run_period as RP  # noqa: E402
from periods import PERIODS, REGIME1, REGIME2, REGIME3, TAU_C  # noqa: E402

DATA = ROOT / "data/processed/H17-behavior-metastable-sets"
FIG = CARD / "figures"
REG_COLOR = {"I": "#4f8fc0", "II": "#9b9b9b", "III": "#c0504d"}


def load():
    res = {}
    for g in PERIODS:
        f = DATA / f"G{g:02d}" / "result.json"
        if f.exists():
            res[g] = json.loads(f.read_text())
    return res


def holm(ps):
    ps = np.asarray(ps, float)
    o = np.argsort(ps)
    m = len(ps)
    adj = np.empty(m)
    run = 0
    for r, i in enumerate(o):
        run = max(run, (m - r) * ps[i])
        adj[i] = min(1.0, run)
    return adj


def extra_n2(goal, nnull=400, seed=7):
    """More N2 surrogates (t2 only) for regime-III periods, so Holm across 8 periods is possible."""
    rng = np.random.default_rng(seed + goal)
    sm = RP.load_min(goal)
    S = RP.seq_from_min(sm)
    t2 = L.its_from_C(L.counts(S["x"], S["seg"], 6, TAU_C), TAU_C)[0]
    nn = np.array([L.its_from_C(L.counts(L.null_sojourn(S["x"], S["seg"], rng)[0], S["seg"], 6, TAU_C), TAU_C)[0] for _ in range(nnull)])
    return {"t2": float(t2), "n2_med": float(np.median(nn)), "n2_p95": float(np.percentile(nn, 95)),
            "p_emp": float((1 + np.sum(nn >= t2)) / (1 + nnull)),
            "z": float((t2 - nn.mean()) / nn.std()) if nn.std() > 0 else None}


def _extra(g):
    return extra_n2(g, nnull=200 if g == 51 else 400)


def its_rise(p):
    a, b = p["its"].get("15"), p["its"].get("1")
    return a[0] / b[0] if a and b and b[0] else None


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    R = load()
    rows = []
    for g, r in sorted(R.items()):
        p = r["primary"]
        v = r["verdict"]
        rows.append({"goal": g, "regime": r["regime"], "agents": p["n_agents"], "days": p["n_days"], "agent_days": p["n_segments"],
                     "t2": p["t2"], "t2_lo": p["t2_ci"][0], "t2_hi": p["t2_ci"][1], "ln_se": p["ln_t2_se"],
                     "n1_p95": p["n1_p95"], "n2_med": p["n2_med"], "n2_p95": p["n2_p95"], "n2_ratio": p["t2"] / p["n2_med"],
                     "n3_med": p.get("n3_med"), "t2_R1": p["t2_R1"], "m": p["m"], "sets_m2": p["sets_m2"], "sets_m": p["sets_m"],
                     "crisp": p["crispness"], "sep": p["sep"], "ck_max": p["ck_max"], "ck_sig_fail": p["ck_sig_fail"],
                     "plateau": p["plateau_tau"], "its_rise": its_rise(p), "I2": p.get("I2"), "n_agents_I2": len(p["per_agent"]),
                     "dll_R1": p["ll_tauc"]["M1"] - p["ll_tauc"]["R1"], "dll_M0": p["ll_tauc"]["M1"] - p["ll_tauc"]["M0"],
                     "dll_o2": p["dll_o2"], "delta_max": p.get("delta_max"), "delta_sig": p.get("delta_sig"),
                     "delta_state": p.get("delta_max_state"), "cores": p.get("cores"),
                     "ep": p["ep"], "ep_n2_p95": p.get("ep_n2_p95"), "ep_macro_share": p.get("ep_macro_share"),
                     "err": p["err_share"], "out": p["out_rate"], "idle": p["idle_share"],
                     "idle_bnd": p.get("idle_boundary_frac"), "t2_trim": p.get("t2_trim_boundary_idle"),
                     "trim_n2_med": p.get("trim_n2_med"), "trim_n2_p95": p.get("trim_n2_p95"), "trim_sets_m2": p.get("trim_sets_m2"),
                     "half1": p["t2_half1"], "half2": p["t2_half2"], "w5_hard": p.get("w5_hard"), "w5_soft": p.get("w5_soft"),
                     "w5_shift": p.get("w5_shift"), "rec_t2_min": p.get("rec_t2_min"), "act_sets": p.get("act_sets"),
                     "t_mix": p.get("t_mix"), "mfpt_AB": p.get("mfpt_AB"), "mfpt_BA": p.get("mfpt_BA"),
                     "rate_AB": p.get("rate_AB_per_min"), "complex_period": p.get("complex_period_min"),
                     "lab_eta2": p.get("lab_eta2"), "lab_eta2_p": p.get("lab_eta2_p"),
                     "cov": p.get("covariates", {}), "verdict": v["verdict"], "v": v, "extra": p.get("extra", {}),
                     "frac_agent_beats": p.get("frac_agent_beats")})
    by = {r["goal"]: r for r in rows}
    r3 = [by[g] for g in REGIME3 if g in by]
    r1 = [by[g] for g in REGIME1 if g in by]
    r2 = [by[g] for g in REGIME2 if g in by]
    S = {"n_periods": len(rows)}

    # ---- P3b with more surrogates (regime III), Holm
    cache = DATA / "extra_n2.json"
    ex = {int(k): v for k, v in json.loads(cache.read_text()).items()} if cache.exists() else {}
    todo = [r["goal"] for r in r3 if r["goal"] not in ex]
    if todo:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=2) as pool:
            for g, e in zip(todo, pool.map(_extra, todo)):
                ex[g] = e
                cache.write_text(json.dumps(ex))
    ps = [ex[r["goal"]]["p_emp"] for r in r3]
    adj = holm(ps)
    p3b_rows = []
    for r, pa in zip(r3, adj):
        e = ex[r["goal"]]
        ok = bool(pa < 0.05 and e["t2"] / e["n2_med"] >= 1.25)
        p3b_rows.append({"goal": r["goal"], "t2": e["t2"], "n2_med": e["n2_med"], "ratio": e["t2"] / e["n2_med"], "p_emp": e["p_emp"],
                         "p_holm": float(pa), "z": e["z"], "pass": ok})
    S["P3b"] = {"rows": p3b_rows, "n_pass": sum(x["pass"] for x in p3b_rows), "n": len(p3b_rows),
                "holds": sum(x["pass"] for x in p3b_rows) >= len(p3b_rows) / 2}

    # ---- P2
    S["P2"] = {"plateau_frac_r3": float(np.mean([r["plateau"] is not None for r in r3])),
               "ck_pass_frac_all": float(np.mean([r["v"]["ck_pass"] for r in rows])),
               "ck_pass_frac_r3": float(np.mean([r["v"]["ck_pass"] for r in r3])),
               "ck_sig_fail_frac_all": float(np.mean([bool(r["ck_sig_fail"]) for r in rows])),
               "order2_better_frac": float(np.mean([(r["dll_o2"] or 0) > 0 for r in rows])),
               "its_rise_median_r3": float(np.median([r["its_rise"] for r in r3])),
               "its_rise_median_r1": float(np.median([r["its_rise"] for r in r1])) if r1 else None,
               "its_rise_range_all": [float(min(r["its_rise"] for r in rows)), float(max(r["its_rise"] for r in rows))]}
    # ---- P3 a, c, d, e
    S["P3a_frac"] = float(np.mean([r["t2"] > r["n1_p95"] for r in rows]))
    S["P3c"] = {"m23_frac": float(np.mean([r["m"] in (2, 3) for r in rows])),
                "crisp_ge075_frac": float(np.mean([(r["crisp"] or 0) >= 0.75 for r in rows])),
                "sep_ge2_frac": float(np.mean([(r["sep"] or 0) >= 2 for r in rows])),
                "all_three_frac": float(np.mean([r["v"]["p3c"] for r in rows]))}
    S["P3d_frac_r3"] = float(np.mean([r["v"]["p3d"] for r in r3]))
    S["P3d_frac_r1"] = float(np.mean([r["v"]["p3d"] for r in r1])) if r1 else None
    S["P3e_r3_in_5_60"] = float(np.mean([5 <= r["t2"] <= 60 for r in r3]))
    S["m2_split_counts"] = collections.Counter(" | ".join(sorted("+".join(s) for s in r["sets_m2"])) for r in rows).most_common()
    # ---- P4a heterogeneity across regime-III periods; #51 weeks
    y = np.log([r["t2"] for r in r3])
    se = np.array([r["ln_se"] for r in r3])
    I2p, Qp = L.i_squared(y, se)
    cv_between = float(np.std([r["t2"] for r in r3], ddof=1) / np.mean([r["t2"] for r in r3]))
    weeks = by.get(51, {}).get("extra", {}).get("weeks", [])
    cv_weeks = float(np.std([w["t2"] for w in weeks], ddof=1) / np.mean([w["t2"] for w in weeks])) if len(weeks) > 2 else None
    S["P4a"] = {"I2_r3": I2p, "Q": Qp, "cv_between_r3": cv_between, "cv_weeks_51": cv_weeks, "n_weeks": len(weeks),
                "weeks": [{"week": w["week"], "t2": w["t2"], "ci": w["t2_ci"], "sets_m2": w["sets_m2"]} for w in weeks],
                "holds": bool(I2p >= 0.75 and cv_weeks is not None and cv_between > cv_weeks)}
    # trimmed (post hoc) heterogeneity
    yt = np.log([r["t2_trim"] for r in r3 if r["t2_trim"]])
    S["P4a_trimmed_cv_between_r3"] = float(np.std(np.exp(yt), ddof=1) / np.mean(np.exp(yt)))
    # ---- P4b stuckness covariates
    def sp(a, b):
        rr, pp = stats.spearmanr(a, b)
        return float(rr), float(pp)
    S["P4b"] = {"across_r3": {"rho_err": sp([r["t2"] for r in r3], [r["err"] for r in r3]),
                              "rho_out": sp([r["t2"] for r in r3], [r["out"] for r in r3]),
                              "rho_idle": sp([r["t2"] for r in r3], [r["idle"] for r in r3]),
                              "rho_err_trim": sp([r["t2_trim"] for r in r3], [r["err"] for r in r3]),
                              "rho_out_trim": sp([r["t2_trim"] for r in r3], [r["out"] for r in r3])},
                "across_r1": {"rho_err": sp([r["t2"] for r in r1], [r["err"] for r in r1]),
                              "rho_out": sp([r["t2"] for r in r1], [r["out"] for r in r1])} if len(r1) > 4 else None}

    def meta(rs, key):
        zs, ws = [], []
        for r in rs:
            c = r["cov"]
            if c.get(key) is None or c.get(key) != c.get(key) or c.get("n_agents_cov", 0) < 5:
                continue
            n = c["n_agents_cov"]
            zs.append(np.arctanh(np.clip(c[key], -0.999, 0.999)))
            ws.append(n - 3)
        if not zs:
            return None
        zs, ws = np.array(zs), np.array(ws, float)
        zbar = np.sum(ws * zs) / ws.sum()
        se_ = 1 / np.sqrt(ws.sum())
        z = zbar / se_
        return {"rho": float(np.tanh(zbar)), "z": float(z), "p": float(2 * stats.norm.sf(abs(z))), "k": len(zs), "n_total": int(ws.sum() + 3 * len(zs)),
                "Q_het_p": float(stats.chi2.sf(np.sum(ws * (zs - zbar) ** 2), len(zs) - 1)) if len(zs) > 1 else None}
    S["P4b"]["within_meta_r3"] = {"err": meta(r3, "rho_t2_err"), "out": meta(r3, "rho_t2_out"), "idle": meta(r3, "rho_t2_idle")}
    S["P4b"]["within_meta_all"] = {"err": meta(rows, "rho_t2_err"), "out": meta(rows, "rho_t2_out"), "idle": meta(rows, "rho_t2_idle")}
    # ---- P4c regime contrast
    S["P4c"] = {"median_r1": float(np.median([r["t2"] for r in r1])), "median_r3": float(np.median([r["t2"] for r in r3])),
                "median_r2": float(np.median([r["t2"] for r in r2])) if r2 else None,
                "mw_p_greater": float(stats.mannwhitneyu([r["t2"] for r in r1], [r["t2"] for r in r3], alternative="greater").pvalue),
                "mw_p_two": float(stats.mannwhitneyu([r["t2"] for r in r1], [r["t2"] for r in r3]).pvalue),
                "trim_median_r1": float(np.median([r["t2_trim"] for r in r1])), "trim_median_r3": float(np.median([r["t2_trim"] for r in r3])),
                "trim_mw_p_two": float(stats.mannwhitneyu([r["t2_trim"] for r in r1], [r["t2_trim"] for r in r3]).pvalue)}
    # ---- P4d free periods
    def rank_fast(g, rs):
        vals = sorted(r["t2"] for r in rs)
        return vals.index(by[g]["t2"]) + 1 if g in by else None
    S["P4d"] = {"31_rank_from_fastest_in_r1": rank_fast(31, r1), "n_r1": len(r1), "37_rank_from_fastest_in_r3": rank_fast(37, r3), "n_r3": len(r3)}
    # ---- P5
    i2s = [r["I2"] for r in rows if r["I2"] is not None]
    S["P5"] = {"frac_I2_ge05": float(np.mean([v >= 0.5 for v in i2s])), "median_I2": float(np.median(i2s)), "n": len(i2s),
               "frac_agent_beats_median": float(np.nanmedian([r["frac_agent_beats"] for r in rows if r["frac_agent_beats"] is not None])),
               "lab_eta2_sig": [r["goal"] for r in rows if r["lab_eta2_p"] is not None and r["lab_eta2_p"] < 0.05]}
    # ---- P6, P7, P8
    S["P6_frac_r3"] = float(np.mean([r["v"]["p6"] for r in r3]))
    S["P6_delta_max_r3"] = [(r["goal"], r["delta_max"], r["delta_sig"], r["delta_state"], r["cores"]) for r in r3]
    S["P7"] = {"ep_gt_n2_frac_r3": float(np.mean([r["ep"] > (r["ep_n2_p95"] or np.inf) for r in r3])),
               "macro_share_lt05_frac_r3": float(np.mean([(r["ep_macro_share"] or 1) < 0.5 for r in r3])),
               "both_frac_r3": float(np.mean([r["v"]["p7"] for r in r3])),
               "ep_gt_n2_frac_all": float(np.mean([r["ep"] > (r["ep_n2_p95"] or np.inf) for r in rows]))}
    S["P8_frac_all"] = float(np.mean([r["v"]["p8"] for r in rows]))
    S["P8_dll_R1_median"] = float(np.median([r["dll_R1"] for r in rows]))
    # ---- P10 NE splits
    S["P10"] = {g: by[g]["extra"].get("ne_split") for g in (21, 30, 38) if g in by}
    # ---- R3, robustness
    S["R3_half_ratio_median"] = float(np.median([r["half1"] / r["half2"] for r in rows if r["half2"]]))
    S["idle_boundary_frac_median_r3"] = float(np.median([r["idle_bnd"] for r in r3]))
    S["idle_boundary_frac_median_r1"] = float(np.median([r["idle_bnd"] for r in r1]))
    S["trim"] = {"t2_trim_median_r3": float(np.median([r["t2_trim"] for r in r3])),
                 "trim_exceeds_n2_r3": [(r["goal"], r["t2_trim"], r["trim_n2_p95"], r["t2_trim"] / r["trim_n2_med"]) for r in r3],
                 "trim_frac_ratio_ge125_all": float(np.mean([r["t2_trim"] / r["trim_n2_med"] >= 1.25 and r["t2_trim"] > r["trim_n2_p95"] for r in rows])),
                 "trim_sets": collections.Counter(" | ".join(sorted("+".join(s) for s in r["trim_sets_m2"])) for r in rows).most_common()}
    S["verdicts"] = collections.Counter(r["verdict"].split(" ")[0] for r in rows)
    S["table"] = [{k: v for k, v in r.items() if k not in ("cov", "v", "extra")} for r in rows]
    (DATA / "summary.json").write_text(json.dumps(L.jsonable(S), indent=1))

    # ---- per-period scorecard lines back into result.json
    p3b_by = {x["goal"]: x for x in p3b_rows}
    for r in rows:
        f = DATA / f"G{r['goal']:02d}" / "result.json"
        j = json.loads(f.read_text())
        v = r["v"]
        if r["goal"] in p3b_by:  # regime III: definitive P3b = 400 surrogates (200 for #51) + Holm across the 8 periods
            x = p3b_by[r["goal"]]
            v["p3b"] = x["pass"]
            j["primary"]["n2_med_400"], j["primary"]["n2_p_holm"] = x["n2_med"], x["p_holm"]
            reasons = ([] if v["ck_pass"] else ["CK fails"]) + ([] if v["p3b"] else ["t2* not beyond the sojourn null"]) + ([] if v["p8"] else ["MSM does not beat R1/M0"])
            base = "supported" if (v["ck_pass"] and v["p3b"] and v["p8"]) else ("failed" if (not v["ck_pass"] and not v["p3b"]) else "mixed")
            v["verdict"] = base + (f" ({'; '.join(reasons)})" if reasons else "")
            r["verdict"] = v["verdict"]
        j["verdict"] = v
        sc = ["| Axis | Evidence | Score |", "| --- | --- | --- |",
              f"| B assumptions | CK max \\|Δ\\| {r['ck_max']:.3f} ({'pass' if v['ck_pass'] else 'fail'}); ITS rise t2(15)/t2(1) = {r['its_rise']:.1f}; "
              f"plateau: {r['plateau'] if r['plateau'] is not None else 'none'}; order 2 better by {r['dll_o2']:.3f} nats; halves {r['half1']:.0f}/{r['half2']:.0f} min | "
              f"{1 if v['ck_pass'] else 0} |",
              f"| C adequacy | MSM vs R1 ΔLL/pair {r['dll_R1']:+.4f}, vs M0 {r['dll_M0']:+.3f} (day-blocked) | {2 if (v['p8'] and v['p3b']) else (1 if v['p8'] or r['dll_R1'] > 0 else 0)} |",
              f"| D unfitted | t2\\*/N2 = {r['n2_ratio']:.2f} (sets beyond sticky states: {'yes' if v['p3b'] else 'no'}); trimmed t2\\*/N2 = "
              f"{(r['t2_trim'] / r['trim_n2_med']) if r['trim_n2_med'] else float('nan'):.2f} | {1 if v['p3b'] else 0} |",
              f"| G ground truth | slow set = {r['sets_m2']}; {r['idle_bnd']:.0%} of idle minutes are boundary runs (scaffold/schedule) | 1 |"]
        j["scorecard_lines"] = sc
        extra = []
        if r["goal"] == 51 and weeks:
            extra.append("**Weekly blocks (O10):** " + "; ".join(f"{w['week']}: {w['t2']:.1f} min" for w in weeks)
                         + f". Between-week CV {cv_weeks:.2f} vs between-period CV (regime III) {cv_between:.2f}.")
        ne = r["extra"].get("ne_split")
        if ne:
            extra.append(f"**{ne['ne']} split at {ne['date']}:** t2\\* before {ne['before']['t2']:.1f} min "
                         f"[{ne['before']['ci'][0]:.1f}, {ne['before']['ci'][1]:.1f}] ({ne['before']['agent_days']} agent-days) vs after "
                         f"{ne['after']['t2']:.1f} [{ne['after']['ci'][0]:.1f}, {ne['after']['ci'][1]:.1f}] ({ne['after']['agent_days']}); "
                         f"difference {ne['diff']:+.1f} min, 95% CI [{ne['diff_ci'][0]:+.1f}, {ne['diff_ci'][1]:+.1f}]; idle share "
                         f"{ne['before']['idle_share']:.2f} → {ne['after']['idle_share']:.2f}.")
        extra.append(f"**Post hoc (boundary idle):** {r['idle_bnd']:.0%} of idle minutes lie in the leading/trailing idle run of an "
                     f"agent-day; without them t2\\* = {r['t2_trim']:.1f} min (N2 median {r['trim_n2_med']:.1f}), m = 2 split {r['trim_sets_m2']}.")
        extra.append(f"**Per-agent t2 (τ_c):** " + ", ".join(f"{a['agent']}: {a['t2']:.0f}" for a in sorted(j['primary']['per_agent'], key=lambda z: z['t2']))
                     + f" min (agent codes from `roster.parquet`); lab η² = {r['lab_eta2'] if r['lab_eta2'] is not None else float('nan'):.2f} "
                     f"(perm p = {r['lab_eta2_p'] if r['lab_eta2_p'] is not None else float('nan'):.2f}).")
        c = r["cov"]
        if c.get("rho_t2_err") is not None:
            f2 = lambda v: "n/a" if v is None or v != v else f"{v:+.2f}"
            extra.append(f"**Within-period stuckness (per agent, n = {c['n_agents_cov']}):** ρ(t2, error share) = {f2(c.get('rho_t2_err'))}; "
                         f"ρ(t2, output rate) = {f2(c.get('rho_t2_out'))}; ρ(t2, idle share) = {f2(c.get('rho_t2_idle'))}.")
        j["extra_lines"] = extra
        f.write_text(json.dumps(j))
    figures(rows, S, by, r1, r2, r3, weeks)
    print(json.dumps({k: S[k] for k in S if k not in ("table",)}, indent=1, default=str)[:6000])


def figures(rows, S, by, r1, r2, r3, weeks):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False})

    def order_param(ax):
        xs = np.arange(len(rows))
        for i, r in enumerate(rows):
            c = REG_COLOR[r["regime"]]
            ax.errorbar(i, r["t2"], yerr=[[r["t2"] - r["t2_lo"]], [r["t2_hi"] - r["t2"]]], fmt="o", color=c, ms=4, lw=1)
            ax.plot(i, r["n2_med"], "_", color="k", ms=8, mew=1.2)
            ax.plot(i, r["t2_trim"], "s", mfc="none", color=c, ms=4)
        ax.set_xticks(xs)
        ax.set_xticklabels([f"{r['goal']}" for r in rows], rotation=90, fontsize=6)
        ax.set_yscale("log")
        ax.set_ylabel("t2* (active min, τc = 5)")
        ax.set_xlabel("goal period (blue I, grey II, red III)")
        ax.set_title("Order parameter t2*: ● pooled MSM, — N2 sojourn null median, □ boundary idle trimmed (post hoc)", fontsize=7.5)

    def its_overlay(ax):
        for r in rows:
            p = json.loads((DATA / f"G{r['goal']:02d}" / "result.json").read_text())["primary"]
            taus = np.array(p["taus"])
            ax.plot(taus, [p["its"][str(t)][0] for t in p["taus"]], "-", color=REG_COLOR[r["regime"]], lw=0.8, alpha=0.7)
        ax.plot([1, 30], [1, 30], "k:", lw=0.7)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("lag τ (min)")
        ax.set_ylabel("t2(τ) (min)")
        ax.set_title(f"ITS keep rising (median t2(15)/t2(1): III {S['P2']['its_rise_median_r3']:.1f}, I {S['P2']['its_rise_median_r1']:.1f})", fontsize=7.5)

    def hetero(ax):
        for i, r in enumerate(rows):
            p = json.loads((DATA / f"G{r['goal']:02d}" / "result.json").read_text())["primary"]
            ys = [a["t2"] for a in p["per_agent"] if a["t2"] > 0]
            ax.scatter(np.full(len(ys), i) + np.random.default_rng(i).uniform(-0.2, 0.2, len(ys)), ys, s=5, color=REG_COLOR[r["regime"]], alpha=0.6)
            ax.plot(i, r["t2"], "k_", ms=7)
        ax.set_yscale("log")
        ax.set_xticks(range(len(rows)))
        ax.set_xticklabels([str(r["goal"]) for r in rows], rotation=90, fontsize=6)
        ax.set_ylabel("per-agent t2 (min)")
        ax.set_title(f"Agents differ: I² ≥ 0.5 in {S['P5']['frac_I2_ge05']:.0%} of periods (median {S['P5']['median_I2']:.2f})", fontsize=7.5)

    def covs(ax):
        for r in r3 + r1 + r2:
            ax.scatter(r["err"], r["t2"], color=REG_COLOR[r["regime"]], s=14)
            ax.annotate(str(r["goal"]), (r["err"], r["t2"]), fontsize=5, xytext=(2, 2), textcoords="offset points")
        ax.set_yscale("log")
        ax.set_xlabel("error share of computer-use turns")
        ax.set_ylabel("t2* (min)")
        m = S["P4b"]["within_meta_r3"]["err"]
        a = S["P4b"]["across_r3"]["rho_err"]
        ax.set_title(f"t2* vs errors: III ρ = {a[0]:+.2f}; within-period ρ = {m['rho']:+.2f}", fontsize=7.5)

    def idle_bnd(ax):
        for r in rows:
            ax.scatter(r["idle_bnd"], r["t2"] / r["t2_trim"], color=REG_COLOR[r["regime"]], s=14)
            ax.annotate(str(r["goal"]), (r["idle_bnd"], r["t2"] / r["t2_trim"]), fontsize=5, xytext=(2, 2), textcoords="offset points")
        ax.set_xlabel("share of idle minutes in boundary runs")
        ax.set_ylabel("t2* / t2* (boundary idle trimmed)")
        ax.set_title("Boundary idling inflates t2* only in #37 (post hoc)", fontsize=7.5)

    def weekly(ax):
        if not weeks:
            return
        ax.errorbar(range(len(weeks)), [w["t2"] for w in weeks], yerr=[[w["t2"] - w["t2_ci"][0] for w in weeks], [w["t2_ci"][1] - w["t2"] for w in weeks]],
                    fmt="o-", color=REG_COLOR["III"], ms=3, lw=1)
        ax.set_xticks(range(len(weeks)))
        ax.set_xticklabels([w["week"][5:] for w in weeks], rotation=90, fontsize=6)
        ax.set_ylabel("t2* (min)")
        ax.set_title(f"#51 by week: CV {S['P4a']['cv_weeks_51']:.2f} vs between-period CV {S['P4a']['cv_between_r3']:.2f}", fontsize=7.5)

    def synth(ax):
        f = DATA / "synthetic" / "synthetic_rows.json"
        if not f.exists():
            return
        sr = json.loads(f.read_text())
        A = sr["A"]
        cr = np.array([x["crossings"] for x in A])
        ra = np.array([x["ratio"] for x in A])
        ax.scatter(cr, ra, s=3, color="#666", alpha=0.4, label="planted sets: t2 ratio")
        E = sr["E"]
        for key, c in (("argmax_1", "#c0504d"), ("softcount_1", "#e8a33d"), ("shifted_1", "#1f4e79")):
            ax.scatter(np.full(len(E), 3e4) * np.exp(np.random.default_rng(1).normal(0, 0.15, len(E))) * {"argmax_1": 1, "softcount_1": 3, "shifted_1": 9}[key],
                       [x[key] for x in E], s=6, color=c, label=f"soft states: {key.replace('_1', '')}")
        ax.axhline(1, color="k", lw=0.6)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("inter-set crossings (planted); soft-state runs at right")
        ax.set_ylabel("t2 estimate / truth")
        ax.legend(fontsize=5, frameon=False, loc="lower left")
        ax.set_title("Synthetic: hard t2 unbiased; Jev-like argmax biased low", fontsize=7.5)

    for name, fn, size in (("order_parameter", order_param, (8, 3)), ("its_all_periods", its_overlay, (4, 3)), ("agent_heterogeneity", hetero, (8, 3)),
                           ("stuckness_covariates", covs, (4.5, 3.2)), ("boundary_idle", idle_bnd, (4.5, 3.2)), ("g51_weekly", weekly, (5, 3)),
                           ("synthetic_validation", synth, (5.5, 3.5))):
        fig, ax = plt.subplots(figsize=size)
        fn(ax)
        fig.tight_layout()
        fig.savefig(FIG / f"{name}.pdf")
        plt.close(fig)

    # ---- one-page summary
    fig = plt.figure(figsize=(8.5, 11))
    gs = fig.add_gridspec(5, 2, height_ratios=[0.9, 1.1, 1, 1, 1], hspace=0.75, wspace=0.3)
    axT = fig.add_subplot(gs[0, :])
    axT.axis("off")
    p3b = S["P3b"]
    vc = collections.Counter(json.loads((DATA / f"G{r['goal']:02d}" / "result.json").read_text())["verdict"]["verdict"].split(" ")[0] for r in rows)
    S["verdicts"] = dict(vc)
    (DATA / "summary.json").write_text(json.dumps(L.jsonable(S), indent=1))
    txt = (f"H17 · Behavior MSM with metastable sets; t2* as a per-period order parameter (exploratory round 1, 2026-10-03)\n"
           f"States: H14 coarse 6-state minute grid (action classes); pooled non-reversible MSM per goal period, τc = 5 min; {S['n_periods']} non-holdout periods.\n\n"
           f"• Slowest process = tool mode: GUI work (browse+type) vs. shell/chat/idle in most periods (idle alone only in #37, #51).\n"
           f"• t2* = {S['P4c']['median_r3']:.1f} min (median, regime III) vs {S['P4c']['median_r1']:.1f} min (regime I): regime III is SLOWER (predicted the reverse).\n"
           f"• Sets beyond sticky states (P3b, Holm): {p3b['n_pass']}/{p3b['n']} regime-III periods; the sojourn null reproduces ~80% of t2*.\n"
           f"• Not Markov at minute scale: ITS rise ×{S['P2']['its_rise_median_r3']:.1f} from τ = 1 to 15 min; CK fails in all 27 periods.\n"
           f"• t2* does not track error share or output (within-period meta ρ = {S['P4b']['within_meta_r3']['err']['rho']:+.2f}); agents differ (I² ≥ 0.5 in {S['P5']['frac_I2_ge05']:.0%}).\n"
           f"• Verdicts: {dict(vc)}. Jev-like noisy labels would bias t2 low 4–14× unless the shifted estimator is used."
           )
    axT.text(0, 1, txt, va="top", ha="left", fontsize=7.6, family="DejaVu Sans", wrap=True)
    order_param(fig.add_subplot(gs[1, :]))
    its_overlay(fig.add_subplot(gs[2, 0]))
    idle_bnd(fig.add_subplot(gs[2, 1]))
    hetero(fig.add_subplot(gs[3, :]))
    covs(fig.add_subplot(gs[4, 0]))
    synth(fig.add_subplot(gs[4, 1]))
    fig.savefig(FIG / "summary.pdf")
    plt.close(fig)


if __name__ == "__main__":
    main()
