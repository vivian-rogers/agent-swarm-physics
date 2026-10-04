"""H19 exploratory round 1 on real, non-holdout data: P1-P5 and the control-parameter scan.

Reads data/processed/H19-loop-gain-collapse/{estimates,controls,h03_aux}.parquet (built by scheme/).
Writes results/explore.json, results/scan.parquet, results/per_period.parquet, G<NN>/residuals.parquet,
and results/frozen_model.json (the collapse model frozen for analysis/confirm.py).

Usage: uv run python hypotheses/H19-loop-gain-collapse/analysis/explore.py
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import h19common as C  # noqa: E402
import h19lib as L  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402

XP = "x_att_village"
PRIMARIES = ("H03.n_talk", "H19.geq_active")
Z90 = stats.norm.ppf(0.95)
SCAN = ["x_att_village", "x_att_llm", "N_roster", "log_N_roster", "N_room", "n_rooms", "m_turn_llm", "m_turn_village", "m_hour",
        "k_village", "k_llm", "log1p_k_village", "hours_emp", "human_share", "date_mid", "inv_m_turn_village"]


def jsonable(o):
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return None if not np.isfinite(o) else float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.ndarray):
        return jsonable(o.tolist())
    return o


def load():
    est = pl.read_parquet(C.OUT / "estimates.parquet").filter(~pl.col("validation_only"))
    # round 1b: the DQ8-trimmed / H38-conditioned versions of H19's own gains are not extra P1 methods; with
    # H19_E1=trim|scaf they replace E1 (geq_active) and E2 (geq_talk), otherwise they are dropped here.
    sfx = ("_trim", "_scaf")
    if C.E1_VARIANT != "raw":
        v = "_" + C.E1_VARIANT
        est = (est.filter(~pl.col("method").is_in(["H19.geq_active", "H19.geq_talk"]))
               .with_columns(pl.col("method").str.replace(v + "$", "")))
    est = est.filter(~pl.col("method").str.ends_with(sfx[0]) & ~pl.col("method").str.ends_with(sfx[1]))
    est = est.with_columns(pl.when(pl.col("method") == "H19.geq_active").then(True).otherwise(pl.col("primary")).alias("primary"))
    ctr = pl.read_parquet(C.CTRL / "controls.parquet").with_columns(
        pl.col("N_roster").log().alias("log_N_roster"), (1 + pl.col("k_village")).log().alias("log1p_k_village"),
        (1 / pl.col("m_turn_village")).alias("inv_m_turn_village"))
    C.assert_no_holdout(pl.read_parquet(C.CTRL / "controls_days.parquet")["pt_date"], pl.read_parquet(C.CTRL / "controls_days.parquet")["goal_no"])
    ctrd = {r["goal_no"]: r for r in ctr.iter_rows(named=True)}
    methods = {}
    for (m,), d in est.group_by(["method"], maintain_order=True):
        rows = [dict(ctrd[g], y=float(y), s=float(s)) for g, y, s in zip(d["goal_no"], d["value"], d["se"])]
        methods[m] = {"rows": rows, "family": d["family"][0]}
    return est, ctr, ctrd, methods


def fits_for(methods, xname, models=L.MODELS):
    return {m: L.method_fits(M["rows"], xname, models) for m, M in methods.items()}


def slope_of(fm, xname, model="x"):
    return [r for r in fm[model]["coefs"] if r["name"] == xname][0]


# ----------------------------------------------------------------------------- P1 and per-period results
def per_period(methods, per, ctrd):
    out = {}
    xs = np.array([ctrd[g][XP] for g in ctrd]); med_x = float(np.median(xs))
    med_y = {m: float(np.median([r["y"] for r in M["rows"]])) for m, M in methods.items()}
    rows_pq = []
    for g in sorted(ctrd):
        P = C.pname(g)
        rec = {"methods": {}, "predicted_side": "above" if ctrd[g][XP] > med_x else "below"}
        lpx = lpr = 0.0
        for m, M in methods.items():
            goals = [r["goal_no"] for r in M["rows"]]
            if g not in goals:
                continue
            i = goals.index(g)
            r = M["rows"][i]
            lx, lr = per[m]["x"]["lopo"], per[m]["regime"]["lopo"]
            f = per[m]["x"]["fit"]
            X, _ = L.design([r], "x", XP)
            mu_all = float(X[0] @ f["b"])
            lam = f["tau2"] / (f["tau2"] + r["s"] ** 2) if f["tau2"] > 0 else 0.0
            rr = {"y": r["y"], "s": r["s"], "shrunk": lam * r["y"] + (1 - lam) * mu_all, "fit_all": mu_all}
            if np.isfinite(lx["mu"][i]):
                sd = float(np.sqrt(lx["var"][i]))
                rr.update({"mu": float(lx["mu"][i]), "lo90": float(lx["mu"][i] - Z90 * sd), "hi90": float(lx["mu"][i] + Z90 * sd),
                           "z": float((r["y"] - lx["mu"][i]) / sd), "inside": bool(abs(r["y"] - lx["mu"][i]) <= Z90 * sd),
                           "lpd_x": float(lx["lpd"][i])})
            if np.isfinite(lr["mu"][i]):
                rr.update({"mu_regime": float(lr["mu"][i]), "lpd_regime": float(lr["lpd"][i])})
            if np.isfinite(lx["lpd"][i]) and np.isfinite(lr["lpd"][i]):
                lpx += lx["lpd"][i]; lpr += lr["lpd"][i]
            rec["methods"][m] = rr
            rows_pq.append({"goal_no": g, "period": P, "method": m, **{k: rr.get(k) for k in
                            ("y", "s", "mu", "lo90", "hi90", "z", "inside", "shrunk", "fit_all", "mu_regime", "lpd_x", "lpd_regime")}})
        prim = [rec["methods"][m] for m in PRIMARIES if m in rec["methods"] and "inside" in rec["methods"][m]]
        cond_i = bool(len(prim) > 0 and all(p["inside"] for p in prim))
        cond_ii = bool(lpx >= lpr)
        rec.update({"cond_i": cond_i, "cond_ii": cond_ii, "lpd_x": float(lpx), "lpd_regime": float(lpr),
                    "verdict": "supported" if cond_i and cond_ii else ("mixed" if cond_i or cond_ii else "failed"),
                    "observed_side": {m.split(".")[1]: ("above" if rec["methods"][m]["y"] > med_y[m] else "below")
                                      for m in PRIMARIES if m in rec["methods"]}})
        out[P] = rec
    return out, pl.DataFrame(rows_pq)


# ----------------------------------------------------------------------------- P2 concordance
def concordance(methods, residual_of=None):
    names = list(methods)
    val = {m: {r["goal_no"]: r["y"] for r in methods[m]["rows"]} for m in names}
    if residual_of is not None:
        val = residual_of
    mat = {}
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            gs = sorted(set(val[a]) & set(val[b]))
            r, p, n = L.spearman([val[a][g] for g in gs], [val[b][g] for g in gs])
            mat[f"{a}|{b}"] = {"rho": r, "p": p, "n": n, "same_family": methods[a]["family"] == methods[b]["family"]}
    return mat


def residuals_after(methods, per, model="x"):
    res = {}
    for m, M in methods.items():
        f = per[m][model]["fit"]
        X, names = L.design(M["rows"], model, XP)
        keep, _, _ = L.reduce_cols(X)
        mu = X[:, keep] @ f["b"]
        res[m] = {r["goal_no"]: (r["y"] - mu_i) / np.sqrt(r["s"] ** 2 + f["tau2"]) for r, mu_i in zip(M["rows"], mu)}
    return res


# ----------------------------------------------------------------------------- P3 mapping, P4 exponent, P5 mode
def p3_mapping(est, aux):
    talk = est.filter(pl.col("method") == "H19.geq_talk").select("goal_no", pl.col("value").alias("geq_talk"), pl.col("se").alias("se_geq"))
    d = talk.join(aux, on="goal_no", how="inner").filter(pl.col("n_cross_fast").is_not_null() & pl.col("n_self_fast").is_not_null())
    out = {"n": d.height}
    for w in (0.6, 0.75, 0.85):
        nx, ns = d["n_cross_fast"].to_numpy() * w, d["n_self_fast"].to_numpy() * w
        gmap = 2 * nx / (1 + 2 * nx + 2 * ns)
        out[f"w{w}"] = {"frac_geq_ge_map": float(np.mean(d["geq_talk"].to_numpy() >= gmap)), "median_map": float(np.median(gmap)),
                        "median_ratio": float(np.median(d["geq_talk"].to_numpy() / np.maximum(gmap, 1e-6)))}
    nx, ns = d["n_cross_fast"].to_numpy() * 0.75, d["n_self_fast"].to_numpy() * 0.75
    gmap = 2 * nx / (1 + 2 * nx + 2 * ns)
    r, p, n = L.spearman(d["geq_talk"], gmap)
    r2, p2, _ = L.spearman(d["geq_talk"], d["n_cross_fast"])
    out.update({"rho_geq_talk_vs_map": r, "p": p, "rho_geq_talk_vs_nx": r2, "p_nx": p2, "median_geq_talk": float(d["geq_talk"].median())})
    passed = (r > 0.3) and out["w0.6"]["frac_geq_ge_map"] >= 2 / 3
    failed = (r <= 0) or out["w0.85"]["frac_geq_ge_map"] < 0.5
    out["verdict"] = "supported" if passed else ("failed" if failed else "mixed")
    out["_points"] = {"goal_no": d["goal_no"].to_list(), "geq_talk": d["geq_talk"].to_list(), "gmap075": gmap.tolist(),
                      "nx": d["n_cross_fast"].to_list(), "ns": d["n_self_fast"].to_list()}
    return out


def powerlaw_fit(y, s, x, alphas=np.linspace(-1.0, 3.0, 401)):
    """y = A x^(-alpha) (x = 1+k or N-1); profile REML over alpha (A by GLS, tau2 by REML)."""
    best = None
    prof = []
    for a in alphas:
        X = (x ** (-a))[:, None]
        f = L.reml_fit(y, s, X)
        nll = L._neg_reml(np.log(max(f["tau2"], 1e-8)), y, X, s ** 2)
        prof.append(nll)
        if best is None or nll < best[0]:
            best = (nll, a, f)
    prof = np.array(prof)
    ok = prof - prof.min() <= 1.92  # 95% profile interval
    return {"alpha": float(best[1]), "lo": float(alphas[ok].min()), "hi": float(alphas[ok].max()), "A": float(best[2]["b"][0]),
            "tau2": best[2]["tau2"], "at_grid_edge": bool(ok[0] or ok[-1])}


def lopo_powerlaw(y, s, x, alphas=np.linspace(-1.0, 3.0, 81)):
    n = len(y); lpd = np.full(n, np.nan)
    for i in range(n):
        k = np.arange(n) != i
        f = powerlaw_fit(y[k], s[k], x[k], alphas)
        mu = f["A"] * x[i] ** (-f["alpha"])
        v = s[i] ** 2 + f["tau2"]
        lpd[i] = -0.5 * (np.log(2 * np.pi * v) + (y[i] - mu) ** 2 / v)
    return lpd


def p4_exponent(aux, ctr):
    d = aux.join(ctr.select("goal_no", "k_village", "N_active"), on="goal_no", how="inner", suffix="_c").filter(
        pl.col("n_c_pair_fast").is_not_null() & pl.col("n_cross_fast_boot_lo").is_not_null() & (pl.col("n_cross_fast") > 0))
    mbar1 = d["n_cross_fast"].to_numpy() / np.maximum(d["n_c_pair_fast"].to_numpy(), 1e-12)  # (m-bar - 1), H03's multiplier
    se_nx = np.maximum((d["n_cross_fast_boot_hi"].to_numpy() - d["n_cross_fast_boot_lo"].to_numpy()) / 3.92, 0.02)
    y = d["n_c_pair_fast"].to_numpy(); s = np.maximum(se_nx / mbar1, 1e-4)
    xk = 1 + d["k_village"].to_numpy(); xn = np.maximum(d["N_active"].to_numpy() - 1, 1.0)
    fk, fn = powerlaw_fit(y, s, xk), powerlaw_fit(y, s, xn)
    lk, ln = lopo_powerlaw(y, s, xk), lopo_powerlaw(y, s, xn)
    dd = L.elpd_diff(lk, ln)
    passed = (0.5 <= fk["alpha"] <= 1.5) and (fk["lo"] <= 1.0 <= fk["hi"]) and dd["delta"] > 0
    return {"n": d.height, "fit_k": fk, "fit_N": fn, "elpd_k_minus_N": dd, "verdict": "supported" if passed else "failed",
            "rho_pair_vs_k": L.spearman(y, xk)[0], "rho_pair_vs_N": L.spearman(y, xn)[0],
            "_points": {"goal_no": d["goal_no"].to_list(), "n_pair": y.tolist(), "se": s.tolist(), "one_plus_k": xk.tolist(), "N_minus_1": xn.tolist()}}


def p5_mode(methods):
    out = {}
    for m in PRIMARIES:
        f = L.method_fits(methods[m]["rows"], XP, models=("x", "x+modeC"))
        c = [r for r in f["x+modeC"]["coefs"] if r["name"] == "mode_C"][0]
        dd = L.elpd_diff(f["x+modeC"]["lopo"]["lpd"], f["x"]["lopo"]["lpd"])
        out[m] = {"mode_C": c, "elpd_mode_minus_x": dd}
    passed = all(v["elpd_mode_minus_x"]["delta"] <= 0 and v["mode_C"]["lo"] <= 0 <= v["mode_C"]["hi"] for v in out.values())
    out["verdict"] = "supported" if passed else "failed"
    return out


# ----------------------------------------------------------------------------- scan and method-specific best control
def scan(methods):
    rows = []
    const = {m: L.method_fits(M["rows"], None, models=("const",)) for m, M in methods.items()}
    for x in SCAN:
        per = {m: L.method_fits(M["rows"], x, models=("x",)) for m, M in methods.items()}
        for m in methods:
            c = slope_of(per[m], x)
            d = L.elpd_diff(per[m]["x"]["lopo"]["lpd"], const[m]["const"]["lopo"]["lpd"])
            r2 = L.r2_het(const[m]["const"]["fit"]["tau2"], per[m]["x"]["fit"]["tau2"])
            rows.append({"control": x, "method": m, "family": methods[m]["family"], "slope": c["b"], "slope_lo": c["lo"],
                         "slope_hi": c["hi"], "p": c["p"], "r2_het": r2, "delta_elpd_vs_const": d["delta"], "delta_se": d["se"]})
    df = pl.DataFrame(rows)
    # Holm over the slope tests of the primary methods across all scanned controls
    prim = df.filter(pl.col("method").is_in(list(PRIMARIES))).sort("p")
    m_tests = prim.height
    holm, running = [], 0.0
    for i, p in enumerate(prim["p"].to_list()):
        running = max(running, min(1.0, (m_tests - i) * p))
        holm.append(running)
    prim = prim.with_columns(pl.Series("p_holm", holm))
    df = df.join(prim.select("control", "method", "p_holm"), on=["control", "method"], how="left")
    return df


def nested_best_control(methods, cands=SCAN):
    """N4 rival: each method picks its own best control inside each LOPO training fold (inner LOPO)."""
    tot_sep, tot_common = 0.0, {x: 0.0 for x in cands}
    picks = {}
    for m, M in methods.items():
        rows = M["rows"]; n = len(rows)
        y = np.array([r["y"] for r in rows]); s = np.array([r["s"] for r in rows])
        Xs = {x: L.design(rows, "x", x)[0] for x in cands}
        lpd = np.full(n, np.nan); pk = []
        for i in range(n):
            k = np.arange(n) != i
            best, bx = -np.inf, None
            for x in cands:
                inner = L.lopo(y[k], s[k], Xs[x][k])["lpd"]
                sc = np.nansum(inner)
                if sc > best:
                    best, bx = sc, x
            f = L.reml_fit(y[k], s[k], Xs[bx][k])
            mu, v = L.predictive(f, Xs[bx][i:i + 1], s[i:i + 1])
            lpd[i] = -0.5 * (np.log(2 * np.pi * v[0]) + (y[i] - mu[0]) ** 2 / v[0]); pk.append(bx)
        tot_sep += float(np.nansum(lpd))
        vals, cnt = np.unique(pk, return_counts=True)
        picks[m] = {"modal": str(vals[np.argmax(cnt)]), "share": float(cnt.max() / n)}
    return {"elpd_method_specific": tot_sep, "picks": picks}


def regime_levels(rows, fm):
    """Regime-only rival frozen as per-level predictions (mean, parameter variance, tau2) for the levels seen."""
    f = fm["fit"]; qf = max(1.0, f["q"])
    out = {}
    for lvl in sorted({r["regime"] for r in rows}):
        X, names = L.design(rows + [dict(rows[0], regime=lvl)], "regime")
        keep, _, _ = L.reduce_cols(X[:-1])
        v = X[-1, keep]
        out[lvl] = {"mu": float(v @ f["b"]), "var_b": float(v @ (f["cov"] * qf) @ v), "tau2": f["tau2"]}
    return out


def main():
    est, ctr, ctrd, methods = load()
    aux = pl.read_parquet(C.OUT / "h03_aux.parquet")
    print("methods:", {m: len(M["rows"]) for m, M in methods.items()}, flush=True)
    per = fits_for(methods, XP)
    dec = L.p1_decision(per, PRIMARIES, XP)
    print("P1:", dec["verdict"], {k: dec[k] for k in ("a_sign", "b_r2", "c_rivals")}, flush=True)
    for m in methods:
        c = dec["slopes"][m]
        print(f"   {m:16s} slope {c['b']:+.3f} [{c['lo']:+.3f}, {c['hi']:+.3f}]  R2het {dec['r2_het'][m]:.2f}", flush=True)
    print("   ELPD totals:", {k: round(v, 1) for k, v in dec["elpd_total"].items()}, flush=True)

    pp, ppq = per_period(methods, per, ctrd)
    conc_raw = concordance(methods)
    conc_res = concordance(methods, residuals_after(methods, per))
    p2 = {}
    for fam in ("E", "T"):
        pairs = {k: v for k, v in conc_raw.items() if v["same_family"] and methods[k.split("|")[0]]["family"] == fam and v["n"] >= 8}
        rhos = [v["rho"] for v in pairs.values()]
        p2[fam] = {"pairs": pairs, "min_rho": float(min(rhos)) if rhos else None,
                   "verdict": ("supported" if rhos and min(rhos) >= 0.4 else ("failed" if rhos and min(rhos) <= 0 else "mixed"))}
    cross = {k: v for k, v in conc_raw.items() if not v["same_family"] and v["n"] >= 8}
    p3 = p3_mapping(est, aux)
    p4 = p4_exponent(aux, ctr)
    p5 = p5_mode(methods)
    print("P2:", {f: v["verdict"] for f, v in p2.items()}, "P3:", p3["verdict"], round(p3["rho_geq_talk_vs_map"], 2),
          "P4:", p4["verdict"], round(p4["fit_k"]["alpha"], 2), "P5:", p5["verdict"], flush=True)

    print("scan ...", flush=True)
    sc = scan(methods)
    joint = (sc.group_by("control").agg(pl.col("delta_elpd_vs_const").sum().alias("joint_delta_elpd"),
                                        (pl.col("slope") > 0).sum().alias("n_pos"), (pl.col("slope") < 0).sum().alias("n_neg"),
                                        ((pl.col("slope_lo") > 0) | (pl.col("slope_hi") < 0)).sum().alias("n_sig"))
             .sort("joint_delta_elpd", descending=True))
    print(joint, flush=True)
    print("nested method-specific best control ...", flush=True)
    sep = nested_best_control(methods)
    common_x = float(sum(np.nansum(per[m]["x"]["lopo"]["lpd"]) for m in methods))  # same periods as the nested rival
    rival_regime = float(dec["elpd_total"]["regime"])

    # robustness: drop G51 (the only 8 h period); drop periods < 4 days; LLM-step turns
    rob = {}
    for label, filt in (("no_G51", lambda r: r["goal_no"] != 51), ("min4days", lambda r: r["n_days"] >= 4)):
        mm = {m: {"rows": [r for r in M["rows"] if filt(r)], "family": M["family"]} for m, M in methods.items()}
        mm = {m: M for m, M in mm.items() if len(M["rows"]) >= 6}
        d2 = L.p1_decision(fits_for(mm, XP), PRIMARIES, XP)
        rob[label] = {"verdict": d2["verdict"], "slopes": {m: d2["slopes"][m] for m in mm}, "elpd_x_minus_rival": d2["elpd_x_minus_rival"]}
    d3 = L.p1_decision(fits_for(methods, "x_att_llm"), PRIMARIES, "x_att_llm")
    rob["x_att_llm"] = {"verdict": d3["verdict"], "slopes": d3["slopes"], "elpd_x_minus_rival": d3["elpd_x_minus_rival"]}

    # family-level regime contrasts (descriptive): regime III minus I per method from the regime model
    reg_contrast = {m: [r for r in per[m]["regime"]["coefs"] if r["name"] == "regime_III"] for m in methods}

    # frozen model for confirm.py
    frozen = {"x": XP, "primaries": PRIMARIES, "frozen_at": dt.datetime.now(dt.timezone.utc).isoformat(),
              "methods": {m: {"b": per[m]["x"]["fit"]["b"].tolist(), "names": per[m]["x"]["names"], "tau2": per[m]["x"]["fit"]["tau2"],
                              "cov": (per[m]["x"]["fit"]["cov"] * max(1.0, per[m]["x"]["fit"]["q"])).tolist(),
                              "regime_levels": regime_levels(methods[m]["rows"], per[m]["regime"]),
                              "median_se": float(np.median([r["s"] for r in methods[m]["rows"]]))} for m in methods},
              "exploratory_verdict_P1": dec["verdict"]}
    C.RES.mkdir(parents=True, exist_ok=True)
    (C.RES / "frozen_model.json").write_text(json.dumps(jsonable(frozen), indent=1))

    R = {"P1": {k: v for k, v in dec.items()}, "per_period": pp, "P2": p2, "cross_family_concordance": cross,
         "residual_concordance": conc_res, "P3": p3, "P4": p4, "P5": p5, "scan_joint": joint.to_dicts(),
         "method_specific_rival": {**sep, "elpd_common_x": common_x, "elpd_regime": rival_regime},
         "robustness": rob, "regime_III_contrast": reg_contrast,
         "fits": {m: {mod: {"coefs": per[m][mod]["coefs"], "tau2": per[m][mod]["fit"]["tau2"], "q": per[m][mod]["fit"]["q"],
                            "elpd": float(np.nansum(per[m][mod]["lopo"]["lpd"]))} for mod in L.MODELS} for m in methods},
         "n_periods": {m: len(M["rows"]) for m, M in methods.items()}}
    (C.RES / "explore.json").write_text(json.dumps(jsonable(R), indent=1))
    sc.write_parquet(C.RES / "scan.parquet")
    ppq.write_parquet(C.RES / "per_period.parquet")
    for (g,), d in ppq.group_by(["goal_no"]):
        (C.OUT / C.pname(g)).mkdir(parents=True, exist_ok=True)
        d.write_parquet(C.OUT / C.pname(g) / f"residuals{'' if C.E1_VARIANT == 'raw' else '_' + C.E1_VARIANT}.parquet")
    C.write_provenance("results", "hypotheses/H19-loop-gain-collapse/analysis/explore.py",
                       [{"source": "data/processed/H19-loop-gain-collapse", "tables": ["estimates.parquet", "controls.parquet", "h03_aux.parquet"]}],
                       {"x_primary": XP, "primaries": PRIMARIES, "scan": SCAN, "models": L.MODELS})
    print("method-specific rival ELPD", round(sep["elpd_method_specific"], 1), "vs common x", round(common_x, 1), "vs regime", round(rival_regime, 1))
    print("per-period verdicts:", {v: sum(1 for p in pp.values() if p["verdict"] == v) for v in ("supported", "mixed", "failed")})
    print("robustness:", {k: v["verdict"] for k, v in rob.items()})


if __name__ == "__main__":
    main()
