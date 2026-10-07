"""H139 round 1 summary: predictions vs results (after Amendment A1), estimates rows, figures.

    uv run python hypotheses/H139-two-rate-variance-split/analysis/summarize.py [--no-estimates]
Output: data/processed/H139-two-rate-variance-split/results/summary.json; figures/summary_obs_col.pdf,
figures/synthetic_col.pdf; per_period_estimates rows (hypothesis H139; roles replication / native).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import glob  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h139lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
RES = L.DATA / "results"
FIG = HERE.parent / "figures"
PRIMARY = ("bge_small", "style_resid_period")
ODD = ["51a", "51c", "51e", "51g", "51i", "51k"]
EVEN = ["51b", "51d", "51f", "51h", "51j", "51l"]
BLUE, ORANGE, GRAY = "#2a78d6", "#eb6834", "#8a8a85"


def j(x):
    return json.loads(x) if isinstance(x, str) else x


def load():
    U = pl.concat([pl.read_parquet(f) for f in sorted(glob.glob(str(RES / "units_G*.parquet")))], how="diagonal_relaxed")
    A = pl.concat([pl.read_parquet(f) for f in sorted(glob.glob(str(RES / "agents_G*.parquet")))], how="diagonal_relaxed")
    I = {}
    for f in sorted(glob.glob(str(RES / "inputs_G*.json"))):
        I.update(json.loads(Path(f).read_text()))
    syn = json.loads((L.DATA / "synthetic/summary.json").read_text())["units"]
    return U, A, I, syn


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-estimates", action="store_true")
    a = ap.parse_args()
    U, A, I, syn = load()
    out = {"units": {}}
    prim = U.filter((pl.col("model") == PRIMARY[0]) & (pl.col("variant") == PRIMARY[1]) & (pl.col("mode") == "corrected"))
    testable = [u for u in prim["unit"].to_list() if u in syn]
    # ---------------------------------------------------------------- per unit
    for r in U.iter_rows(named=True):
        key = f"{r['unit']}|{r['model']}|{r['variant']}|{r['mode']}"
        ci_ak = j(r.get("ci_A_k")) or [np.nan, np.nan]
        inp = I.get(f"{r['unit']}|{r['model']}|{r['variant']}", {})
        sy = syn.get(r["unit"], {})
        amin = sy.get("A_min95", np.nan)
        amin = amin if np.isfinite(amin) else (3.0 if sy else np.nan)    # not reached on the ladder: > 3
        resolved = bool(ci_ak[0] > 0)
        d = {"unit": r["unit"], "period": r["period"], "n_days": r["n_days"], "model": r["model"],
             "variant": r["variant"], "mode": r["mode"], "testable_S1": r["unit"] in syn,
             "A_k": r.get("A_k"), "ci_A_k": ci_ak, "se_A_k": r.get("se_A_k"), "A_pred": r.get("A_pred"),
             "Q_k": r.get("Q_k"), "Q_k_upper": ci_ak[1] / r["A_pred"] if r.get("A_pred") else np.nan,
             "resolved": resolved, "Q_k_lower_if_resolved": (amin / r["A_pred"]) if resolved else np.nan,
             "A_s": r.get("A_s"), "B": r.get("B"), "g_s": r.get("g_s"), "ci_g_s": j(r.get("ci_g_s")),
             "f_k": r.get("f_k"), "f_s": r.get("f_s"), "ci_f_s": j(r.get("ci_f_s")), "g_1": r.get("g_1"),
             "two_beats_one": r.get("two_beats_one"), "oof_two": r.get("oof_two"), "oof_one": r.get("oof_one"),
             "free_A_k": r.get("free_A_k"), "free_g_k": r.get("free_g_k"), "ci_free_g_k": j(r.get("ci_free_g_k")),
             "R_fast": r.get("R_fast"), "ci_R_fast": j(r.get("ci_R_fast")), "R_slow": r.get("R_slow"),
             "ci_R_slow": j(r.get("ci_R_slow")), "R_fast_n": r.get("R_fast_n"), "rbar": r.get("rbar"),
             "rbar_talk": r.get("rbar_talk"), "J_in": r.get("J_in"), "g_k": r.get("g_k"),
             "J_K_shared": inp.get("J") if "H139" in str(inp.get("source", "")) else None,
             "ci_J_K_shared": inp.get("ci_J"), "J_star": sy.get("J_star"), "A_min95": sy.get("A_min95"),
             "C": j(r.get("C")), "N": j(r.get("N")), "n_pairs": r.get("n_pairs"), "n_ad": r.get("n_ad")}
        out["units"][key] = d
    P = {k: v for k, v in out["units"].items() if k.endswith("|bge_small|style_resid_period|corrected")}
    T = {v["unit"]: v for v in P.values() if v["testable_S1"]}
    # ---------------------------------------------------------------- S1 in shared weeks with re-estimated J_K
    s1 = {}
    for u, v in T.items():
        jk = v["J_K_shared"] if v["J_K_shared"] is not None else v["J_in"]
        jstar = v["J_star"] if v["J_star"] and np.isfinite(v["J_star"]) else float(
            np.sqrt(3.0 / (2 * v["rbar"] * L.kick_memory(0.15))))
        ci_hi = (v["ci_J_K_shared"] or [np.nan, np.nan])[1] if v["J_K_shared"] is not None else jk
        s1[u] = {"J_K": jk, "J_K_ci_hi": ci_hi, "J_star": jstar, "S1_holds": bool(not (ci_hi >= jstar))}
    out["S1_real_inputs"] = s1
    # post hoc: A_min on the real noise scale = (synthetic A_min / synthetic SE) x real SE of A_k
    ph = {}
    for u, v in T.items():
        sy = syn[u]
        se_syn = sy["worlds"]["W1"]["se_A_k_med"]
        k = (sy["A_min95"] / se_syn) if np.isfinite(sy["A_min95"]) else 3.4
        a_real = k * v["se_A_k"]
        ph[u] = {"A_min_real": a_real, "ratio": a_real / v["A_pred"] if v["A_pred"] > 0 else np.inf,
                 "S1_holds": bool(a_real > 2 * v["A_pred"]), "dyn_var": v["A_s"] + v["B"],
                 "f_k_pred": v["A_pred"] / (v["A_s"] + v["B"])}
    out["S1_posthoc_real_scale"] = ph
    # ---------------------------------------------------------------- P1 bounds (pool of A_k over testable units)
    ak = np.array([T[u]["A_k"] for u in T])
    se = np.array([T[u]["se_A_k"] for u in T])
    mu, se_mu, tau2, I2 = L.dl_pool(ak, se)
    apred_med = float(np.median([T[u]["A_pred"] for u in T]))
    out["P1"] = {"pooled_A_k": mu, "pooled_ci95": [mu - 1.96 * se_mu, mu + 1.96 * se_mu],
                 "pooled_ci90": [mu - 1.645 * se_mu, mu + 1.645 * se_mu], "I2": I2, "tau2": tau2,
                 "A_pred_median": apred_med, "Q_k_pooled_upper95": (mu + 1.96 * se_mu) / apred_med,
                 "n_units": len(T), "n_resolved": int(sum(T[u]["resolved"] for u in T)),
                 "resolved_units": [u for u in T if T[u]["resolved"]],
                 "units_upper_A_k": {u: T[u]["ci_A_k"][1] for u in T}}
    # #51 pool separately (G51 folder, N2)
    t51 = [u for u in T if u.startswith("51")]
    m51 = L.dl_pool(np.array([T[u]["A_k"] for u in t51]), np.array([T[u]["se_A_k"] for u in t51]))
    out["P1_G51"] = {"pooled_A_k": m51[0], "ci95": [m51[0] - 1.96 * m51[1], m51[0] + 1.96 * m51[1]], "I2": m51[3],
                     "A_pred_median": float(np.median([T[u]["A_pred"] for u in t51])), "units": t51}
    # variants of the pool
    out["P1_variants"] = {}
    for (model, variant, mode) in [("bge_small", "white32", "corrected"), ("gte_modernbert", "style_resid_period", "corrected"),
                                   ("bge_small", "style_resid_period", "raw"), ("bge_small", "style_resid_period", "roomhour")]:
        vv = [out["units"].get(f"{u}|{model}|{variant}|{mode}") for u in T]
        vv = [x for x in vv if x and x["A_k"] is not None and np.isfinite(x["A_k"])]
        m = L.dl_pool(np.array([x["A_k"] for x in vv]), np.array([x["se_A_k"] for x in vv]))
        out["P1_variants"][f"{model}|{variant}|{mode}"] = {"pooled_A_k": m[0], "ci95": [m[0] - 1.96 * m[1], m[0] + 1.96 * m[1]],
                                                           "n_resolved": int(sum(x["resolved"] for x in vv)), "n": len(vv)}
    # ---------------------------------------------------------------- P3, P5
    fs = {u: T[u]["f_s"] for u in T}
    out["P3"] = {"f_s": fs, "n_ge_08": int(sum(v >= 0.8 for v in fs.values())), "n": len(fs),
                 "pass": bool(sum(v >= 0.8 for v in fs.values()) >= 2 / 3 * len(fs)), "label": "non-diagnostic (A1.5)"}
    tb = {u: T[u]["two_beats_one"] for u in T}
    out["P5"] = {"two_beats_one": tb, "n_two": int(sum(bool(v) for v in tb.values())), "n": len(tb),
                 "pass": bool(sum(bool(v) for v in tb.values()) >= len(tb) / 2), "label": "non-diagnostic (A1.5)"}
    # ---------------------------------------------------------------- P4 split-unit Spearman (#51)
    ag = A.filter(pl.col("ok") & pl.col("unit").str.starts_with("51") & pl.col("f_s").is_finite())
    o = ag.filter(pl.col("unit").is_in(ODD)).group_by("agent").agg(pl.col("f_s").mean().alias("o"))
    e = ag.filter(pl.col("unit").is_in(EVEN)).group_by("agent").agg(pl.col("f_s").mean().alias("e"))
    oe = o.join(e, on="agent", how="inner").sort("agent")
    rho = float(spearmanr(oe["o"], oe["e"]).statistic) if oe.height >= 4 else np.nan
    rng = np.random.default_rng(20261007)
    perm = np.array([spearmanr(oe["o"].to_numpy(), rng.permutation(oe["e"].to_numpy())).statistic for _ in range(2000)])
    p = float((np.sum(perm >= rho) + 1) / (len(perm) + 1)) if np.isfinite(rho) else np.nan
    # bootstrap CI of rho over agents
    bs = []
    for _ in range(2000):
        k = rng.integers(0, oe.height, oe.height)
        bs.append(spearmanr(oe["o"].to_numpy()[k], oe["e"].to_numpy()[k]).statistic)
    out["P4"] = {"rho": rho, "ci95": L.ci(bs), "perm_p": p, "n_agents": oe.height,
                 "pass": bool(rho >= 0.3 and p < 0.05), "f_s_agent_median": float(ag["f_s"].median()),
                 "f_s_agent_iqr": [float(ag["f_s"].quantile(0.25)), float(ag["f_s"].quantile(0.75))],
                 "n_agent_units": ag.height}
    # ---------------------------------------------------------------- N1 descriptive
    rf = {u: (T[u]["R_fast"], T[u]["ci_R_fast"]) for u in T}
    rs = {u: (T[u]["R_slow"], T[u]["ci_R_slow"]) for u in T}
    def pool_ratio(dct):
        est = np.array([v[0] for v in dct.values()], float)
        sei = np.array([(v[1][1] - v[1][0]) / 3.92 if v[1] else np.nan for v in dct.values()], float)
        m = L.dl_pool(est, sei)
        return {"pooled": m[0], "ci95": [m[0] - 1.96 * m[1], m[0] + 1.96 * m[1]], "I2": m[3],
                "per_unit": {u: v[0] for u, v in dct.items()}}
    out["N1"] = {"R_fast": pool_ratio(rf), "R_slow": pool_ratio(rs), "label": "untestable (S1) and descriptive (S3)"}
    # ---------------------------------------------------------------- slow amplitudes (descriptive)
    out["slow"] = {u: {"A_s": T[u]["A_s"], "B": T[u]["B"], "g_s": T[u]["g_s"], "ci_g_s": T[u]["ci_g_s"],
                       "g_1": T[u]["g_1"]} for u in T}
    gs = np.array([T[u]["g_s"] for u in t51])
    out["slow_G51_g_s_median"] = float(np.median(gs))
    out["verdict"] = "inconclusive (below resolution)"
    (RES / "summary.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps({k: v for k, v in out.items() if k not in ("units", "slow")}, indent=1, default=float))
    for u in T:
        v = T[u]
        print(f"{u:4s} d{v['n_days']:2d} rbar {v['rbar']:.2f} A_pred {v['A_pred']:.4f} A_k {v['A_k']:+.3f} "
              f"[{v['ci_A_k'][0]:+.3f}, {v['ci_A_k'][1]:+.3f}] Qup {v['Q_k_upper']:.0f} f_s {v['f_s']:.3f} "
              f"g_s {v['g_s']:.4f} 2>1 {v['two_beats_one']} Rf {v['R_fast']:+.2f} Rs {v['R_slow']:.2f} "
              f"gkfree {v['free_g_k']:.3f} JK {v['J_K_shared']}")
    figures(T, syn, out["S1_posthoc_real_scale"])
    if not a.no_estimates:
        estimates(out, T)


def figures(T, syn, ph):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    FIG.mkdir(exist_ok=True)
    plt.rcParams.update({"font.size": 7, "axes.spines.top": False, "axes.spines.right": False})
    units = sorted(T, key=lambda u: (not u.startswith("51"), u))
    # observed: A_k with 95% CI per unit, A_pred and A_min markers
    fig, ax = plt.subplots(figsize=(3.4, 2.3))
    x = np.arange(len(units))
    ak = np.array([T[u]["A_k"] for u in units])
    lo = np.array([T[u]["ci_A_k"][0] for u in units])
    hi = np.array([T[u]["ci_A_k"][1] for u in units])
    ax.axhline(0, color=GRAY, lw=0.6)
    ax.vlines(x, lo, hi, color=BLUE, lw=1.2)
    ax.plot(x, ak, "o", color=BLUE, ms=3.5, label=r"$\hat A_k$ (95% CI)")
    amin = [syn[u]["A_min95"] if np.isfinite(syn[u]["A_min95"]) else 3.0 for u in units]
    ax.plot(x, amin, "_", color=GRAY, ms=8, mew=1.5, label=r"$A_{\min}$ (synthetic scale)")
    ax.plot(x, [ph[u]["A_min_real"] for u in units], "v", color=GRAY, ms=3.5, mfc="none",
            label=r"$A_{\min}$ (real noise scale, post hoc)")
    ax.plot(x, [T[u]["A_pred"] for u in units], "s", color=ORANGE, ms=3, label=r"$A_k^{\rm pred}$")
    ax.set_xticks(x)
    ax.set_xticklabels(units, rotation=90)
    ax.set_ylabel(r"fast amplitude ($|x|^2$ units)")
    ax.legend(frameon=False, fontsize=6, loc="upper left")
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs_col.pdf")
    fig.savefig(FIG / "summary_obs_col.png", dpi=200)
    plt.close(fig)
    # synthetic: detection rate vs planted amplitude
    fig, ax = plt.subplots(figsize=(3.4, 2.3))
    lad = [0.1, 0.3, 0.5, 1.0, 2.0, 3.0]
    for u, U in syn.items():
        W = U["worlds"]
        det = [W[f"L{a:g}"]["det95"] for a in lad]
        c = BLUE if u.startswith("51") else ORANGE
        ax.plot(lad, det, "-", color=c, lw=1, alpha=0.8)
    ax.axhline(0.8, color=GRAY, lw=0.6, ls="--")
    ap = [U["A_pred"] for U in syn.values()]
    ax.axvspan(min(ap), max(ap), color=GRAY, alpha=0.3)
    ax.text(max(ap) * 1.1, 0.9, r"$A_k^{\rm pred}$", fontsize=6, color="#555")
    ax.set_xscale("log")
    ax.set_xlim(1e-3, 4)
    ax.set_xlabel(r"planted fast amplitude $A_k$")
    ax.set_ylabel(r"share with $\hat A_k$ CI $>0$")
    ax.plot([], [], color=BLUE, label="#51 units")
    ax.plot([], [], color=ORANGE, label="#37-#42 units")
    ax.legend(frameon=False, fontsize=6, loc="center left")
    fig.tight_layout()
    fig.savefig(FIG / "synthetic_col.pdf")
    fig.savefig(FIG / "synthetic_col.png", dpi=200)
    plt.close(fig)


def estimates(out, T):
    import estimates as E
    rows = []
    for key, v in out["units"].items():
        if v["mode"] != "corrected" or v["A_k"] is None or not np.isfinite(v["A_k"]):
            continue
        goal = int(v["period"][1:])
        ch = f"content:{v['model']}:{v['variant']}"
        base = {"period_unit": v["unit"], "goal_no": goal, "channel": ch, "role": "replication", "ci_level": 0.95,
                "n_kind": "agent-days", "n": float(v["n_ad"]), "unit_local": v["unit"], "source": "results/summary.json",
                "status": "ok" if v["testable_S1"] else "underpowered"}
        meth = ("drive-corrected own autocovariance on the call clock, 14 lag bins; WLS of A_k(1-g_k)^tau + "
                "A_s(1-g_s)^tau + B with g_k fixed (H130 unit/pooled); agent-day bootstrap (200)")
        note = "S1 fired (synthetic): fast part below resolution; A1" if v["testable_S1"] else "unit < 3 days: descriptive"
        civ = v["ci_A_k"]
        rows += [
            {**base, "statistic": "h139_fast_amp", "estimate": v["A_k"], "ci_lo": civ[0], "ci_hi": civ[1],
             "ci_kind": "percentile", "method": meth, "null": "N0 one-rate OU (A_k = 0)", "notes": note},
            {**base, "statistic": "h139_fast_amp_pred", "estimate": v["A_pred"], "ci_lo": None, "ci_hi": None,
             "ci_kind": "none", "method": "r_bar J_K^2 / [1-(1-g_k)^2] (Campbell); J_K, g_k from H130 or H139 read jump",
             "null": None, "notes": note},
            {**base, "statistic": "h139_fast_ratio_Qk", "estimate": v["Q_k"], "ci_lo": None,
             "ci_hi": v["Q_k_upper"], "ci_kind": "percentile",
             "method": "A_k / A_k^pred; upper = 97.5th percentile of A_k / A_k^pred", "null": "Q_k = 1",
             "notes": note + "; only the upper bound is meaningful"},
            {**base, "statistic": "h139_fast_share", "estimate": v["f_k"], "ci_lo": None, "ci_hi": None,
             "ci_kind": "none", "method": "A_k / (A_k + A_s + B)", "null": None, "notes": note},
            {**base, "statistic": "h139_slow_share", "estimate": v["f_s"], "ci_lo": (v["ci_f_s"] or [None, None])[0],
             "ci_hi": (v["ci_f_s"] or [None, None])[1], "ci_kind": "percentile",
             "method": "(A_s + B) / (A_k + A_s + B); bootstrap", "null": None,
             "notes": "non-diagnostic at this resolution (A1.5)"},
            {**base, "statistic": "h139_read_rate", "estimate": v["rbar"], "ci_lo": None, "ci_hi": None,
             "ci_kind": "none", "channel": "ledger:agent_reads", "method": "mean agent items from other agents newly in context per call (DQ1)",
             "null": None, "notes": f"talk calls only: {v['rbar_talk']:.3f}"},
        ]
        if v["R_fast"] is not None and np.isfinite(v["R_fast"]) and v["model"] == "bge_small" and v["variant"] == "style_resid_period":
            rows.append({**base, "role": "native", "statistic": "h139_erasure_fast_ratio", "estimate": v["R_fast"],
                         "ci_lo": (v["ci_R_fast"] or [None, None])[0], "ci_hi": (v["ci_R_fast"] or [None, None])[1],
                         "ci_kind": "percentile", "method": "lag 1-7 covariance above the slow fit, crossed vs within a forced reset, matched per agent-day and bin",
                         "null": "R_fast = 1 (not context-held)", "notes": "NE41; untestable (S1) and descriptive (S3)"})
    for r in rows:
        r["ci_level"] = 0.95 if r.get("ci_lo") is not None or r.get("ci_hi") is not None else None
    E.write_estimates(rows, hypothesis="H139")
    print("estimates rows:", len(rows))


if __name__ == "__main__":
    main()
