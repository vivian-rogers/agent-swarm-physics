"""H128 analysis: curve statistics per unit, per-period verdicts, P1-P5, natives N1-N3, estimates rows.

Primary observable (Amendment A1): the domain-wall fraction dw(t) = (N_p - 1)/(N_h - 1). HH-literal secondary: N_p(t).
Uncertainty: leave-one-agent-out jackknife (z interval) for t_f, A_u and alpha; 500-draw 2-h block bootstrap for alpha.
Writes data/processed/H128-coarsening-vs-freeze/results/{units.json, score.json} and estimates rows (write_estimates).

Usage: uv run python hypotheses/H128-coarsening-vs-freeze/analysis/run.py [--no-estimates]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl
from scipy.stats import mannwhitneyu

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h128lib as L  # noqa: E402

UNITS = {f"G{g:02d}": g for g in L.REPL}
NATIVE = {"G44best": 44, "G44rest": 44, "G37best": 37, "G37rest": 37, "NE42_merge": 40, "NE42_split": 41}
CODE = {**{f"G{g:02d}": ("named" if g in L.NAMED else "free") for g in L.REPL},
        "G44best": "named", "G44rest": "free", "G37best": "free", "G37rest": "free",
        "NE42_merge": "named", "NE42_split": "free"}
SYN_NAME = {"G44best": "44best", "G44rest": "44rest", "G37best": "37best", "G37rest": "37rest",
            "NE42_merge": "G40", "NE42_split": "G41"}


def load(name):
    o = L.D / name
    return pl.read_parquet(o / "curve.parquet"), pl.read_parquet(o / "deaths.parquet"), json.loads((o / "meta.json").read_text())


def jackknife(name, col, meta):
    """Leave-one-agent-out curves from the hashed event table (names are hashed consistently, so the replay is exact)."""
    g = meta.get("goal_no")
    if g is None:
        return {}
    ev = pl.read_parquet(L.D / f"G{g:02d}" / "events.parquet")
    days = meta["days"]
    clock = L.ActiveClock(days)
    if g == 51:
        ev = ev.filter(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).is_in(days))
    agents = set(meta["room_agents"]) if meta.get("room_agents") else set(ev["agent"].cast(pl.Int64).unique().to_list())
    vals = {"t_f": [], "A_u": [], "alpha": []}
    for a in sorted(agents):
        cur, de = L.curve_from_events(ev, clock, agents=agents - {a})
        s = L.curve_stats(cur, de, col=col)
        if s.get("class") is None:
            continue
        vals["t_f"].append(s["H"] if s["t_f_censored"] else s["t_f"])
        vals["A_u"].append(s["A_u"])
        vals["alpha"].append(s["alpha"] if s.get("alpha") is not None else np.nan)
    out = {}
    for k, v in vals.items():
        v = np.array(v, dtype=float)
        v = v[np.isfinite(v)]
        n = len(v)
        if n >= 3:
            se = float(np.sqrt((n - 1) / n * np.sum((v - v.mean()) ** 2)))
            out[k] = {"se": se, "n": n}
    return out


def drift(cur, s):
    from scipy.stats import kendalltau
    if s.get("class") is None:
        return None
    c = cur.filter(pl.col("dw").is_not_nan() & (pl.col("t") >= s["t_pk"]))
    t, y = c["t"].to_numpy(), c["dw"].to_numpy()
    if len(t) < 8:
        return None
    b = np.polyfit(t, y, 1)[0]
    tau = kendalltau(t, y)
    return {"dw_mean": float(y.mean()), "dw_slope_per_h": float(b), "kendall_tau": float(tau.statistic),
            "kendall_p": float(tau.pvalue), "dw_first2h": float(y[t <= s["t_pk"] + 2].mean()), "dw_last4h": float(y[t >= t[-1] - 4].mean())}


def alpha_ok(s, valid):
    if not valid.get("alpha_identified") or s.get("alpha_ci") is None or not s.get("alpha_fit_ok"):
        return None
    lo, hi = s["alpha_ci"]
    if lo is None or not np.isfinite(lo):
        return None
    return bool(lo <= 0.5 and hi >= 0.3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-estimates", action="store_true")
    a = ap.parse_args()
    syn = json.loads((L.D / "synthetic/summary.json").read_text())["rule"]
    rng = np.random.default_rng(128)
    res = {}
    for name in list(UNITS) + list(NATIVE):
        cur, de, meta = load(name)
        r = {"code": CODE[name], "meta": {k: meta.get(k) for k in ("H", "n_agents", "events_dropped_by_clock", "days",
                                                                      "boundary_day", "pre_dw_median", "pre_N_p_median")}}
        r["valid"] = syn.get(SYN_NAME.get(name, name), {})
        r["dw"] = L.curve_stats(cur, de, col="dw", boot=500, rng=rng)
        r["N_p"] = L.curve_stats(cur, de, col="N_p", boot=200, rng=rng)
        r["N_p_m"] = L.curve_stats(cur, None, col="N_p_m")
        cur2 = cur.with_columns(((pl.col("K_eff") - 1) / (pl.col("N_h") - 1)).alias("keff_dw"))
        cur2 = cur2.with_columns(pl.when(pl.col("N_h") >= 2).then(pl.col("keff_dw")).otherwise(None).alias("keff_dw"))
        r["keff_dw"] = {k: v for k, v in L.curve_stats(cur2.rename({"keff_dw": "dwk"}).with_columns(pl.col("dwk").alias("dw")), None,
                                                       col="dw").items() if k in ("class", "t_f", "A_u", "selected")}
        if not name.startswith("NE42"):
            r["jack_dw"] = jackknife(name, "dw", meta)
        mer = de.filter(pl.col("kind") == "merge")
        r["merge_read_share"] = (float(mer.filter(pl.col("cls_touch") == "read").height / mer.height)
                                 if mer.height and "cls_touch" in mer.columns and mer["cls_touch"].null_count() < mer.height else None)
        r["post_hoc"] = drift(cur, r["dw"])   # A2 (post hoc, disclosed): signed drift of dw after the peak
        ok = alpha_ok(r["dw"], r["valid"])
        r["alpha_in_band"] = ok
        r["verdict"] = (L.verdict_named(r["dw"]) if r["code"] == "named" else L.verdict_free(r["dw"], ok))
        res[name] = r
        print(name, r["code"], r["dw"].get("class"), r["dw"].get("selected"), r["dw"].get("t_f"), r["verdict"], flush=True)
    score = score_all(res)
    out = L.D / "results"
    out.mkdir(parents=True, exist_ok=True)
    (out / "units.json").write_text(json.dumps(res, indent=1, default=lambda o: o.item() if isinstance(o, np.generic) else str(o)))
    (out / "score.json").write_text(json.dumps(score, indent=1, default=lambda o: o.item() if isinstance(o, np.generic) else str(o)))
    print(json.dumps(score, indent=1, default=str))
    if not a.no_estimates:
        write_rows(res)


def tf_eff(s):
    if s.get("class") is None:
        return None
    return s["H"] if s["t_f_censored"] else s["t_f"]


def score_all(res):
    rep = {k: v for k, v in res.items() if k in UNITS}
    free = [k for k, v in rep.items() if v["code"] == "free" and v["dw"].get("testable")]
    named = [k for k, v in rep.items() if v["code"] == "named" and v["dw"].get("testable")]
    sc = {"free_testable": free, "named_testable": named}
    sup = [k for k in free if res[k]["verdict"] == "supported"]
    sc["P1"] = {"supported_units": sup, "frac": len(sup) / len(free) if free else None,
                "pass": bool(free) and len(sup) >= 2 / 3 * len(free),
                "slow_units": [k for k in free if res[k]["dw"]["class"] == "slow"],
                "power_selected": [k for k in free if res[k]["dw"]["selected"] == "power"]}
    fr = [k for k in named if res[k]["dw"]["class"] == "freeze"]
    sc["P2"] = {"freeze_units": fr, "frac": len(fr) / len(named) if named else None,
                "pass": bool(named) and len(fr) >= 2 / 3 * len(named)}
    tf_f = [tf_eff(res[k]["dw"]) for k in free]
    tf_n = [tf_eff(res[k]["dw"]) for k in named]
    au_f = [res[k]["dw"]["A_u"] for k in free]
    au_n = [res[k]["dw"]["A_u"] for k in named]
    p_tf = float(mannwhitneyu(tf_f, tf_n, alternative="greater", method="exact").pvalue) if free and named else None
    p_au = float(mannwhitneyu(au_f, au_n, alternative="greater", method="exact").pvalue) if free and named else None
    sc["P3"] = {"t_f_free": tf_f, "t_f_named": tf_n, "A_u_free": au_f, "A_u_named": au_n, "p_tf": p_tf, "p_Au": p_au,
                "pass": bool(p_tf is not None and p_tf < 0.05 and p_au < 0.05)}
    # HH-literal N_p version of P3 (reported)
    tf_fN = [tf_eff(res[k]["N_p"]) for k in free if res[k]["N_p"].get("class")]
    tf_nN = [tf_eff(res[k]["N_p"]) for k in named if res[k]["N_p"].get("class")]
    sc["P3_Np"] = {"p_tf": float(mannwhitneyu(tf_fN, tf_nN, alternative="greater", method="exact").pvalue)
                   if tf_fN and tf_nN else None}
    dec = [k for k in free if (res[k]["N_p"].get("R_d") or 0) >= 1.5]
    p4 = [k for k in dec if (res[k]["N_p"].get("c_m") or 0) >= 0.5 and res[k]["N_p_m"].get("selected") != "constant"]
    sc["P4"] = {"declining_free": dec, "merge_driven": p4, "c_m": {k: res[k]["N_p"].get("c_m") for k in free},
                "deaths": {k: res[k]["N_p"].get("deaths") for k in free},
                "pass": bool(dec) and len(p4) == len(dec)}
    d5 = {k: res[k]["dw"].get("dBIC_exp_minus_pow") for k in free}
    w5 = [k for k, v in d5.items() if v is not None and v >= 2]
    sc["P5"] = {"dBIC_exp_minus_pow": d5, "power_beats_exp": w5, "pass": bool(free) and len(w5) >= 0.5 * len(free)}
    sc["kill"] = {"met": not sc["P3"]["pass"]}
    nat = {}
    b, r_ = res["G44best"]["dw"], res["G44rest"]["dw"]
    nat["N1"] = {"tf_best": tf_eff(b), "tf_rest": tf_eff(r_), "Au_best": b["A_u"], "Au_rest": r_["A_u"],
                 "class_best": b["class"], "class_rest": r_["class"],
                 "pass": bool(tf_eff(r_) > L.FREEZE_H >= tf_eff(b) and r_["A_u"] > b["A_u"])}
    m, s = res["NE42_merge"]["dw"], res["NE42_split"]["dw"]
    nat["N2"] = {"tf_merge": tf_eff(m), "tf_split": tf_eff(s), "class_merge": m["class"], "class_split": s["class"],
                 "pass": bool(tf_eff(m) <= L.FREEZE_H < tf_eff(s))}
    x, y = res["G37best"]["dw"], res["G37rest"]["dw"]
    same = (x.get("class") == "freeze") == (y.get("class") == "freeze")
    if x.get("class") is None or y.get("class") is None:
        nat["N3"] = {"class_best": x.get("class"), "class_rest": y.get("class"), "pass": None, "note": "descriptive (A1)"}
    else:
      nat["N3"] = {"class_best": x["class"], "class_rest": y["class"], "tf_best": tf_eff(x), "tf_rest": tf_eff(y),
                   "pass": bool(same and abs(tf_eff(x) - tf_eff(y)) <= 3.0)}
    sc["natives"] = nat
    return sc


def write_rows(res):
    sys.path.insert(0, str(L.ROOT / "infra/shared"))
    import estimates as E
    rows = []
    for name, r in res.items():
        if name.startswith("NE42"):
            g, unit, role, local = (40 if "merge" in name else 41), None, "native", name
        elif name in NATIVE:
            g, unit, role, local = NATIVE[name], f"G{NATIVE[name]:02d}", "native", name
        else:
            g, unit, role, local = UNITS[name], None, "replication", None
        if unit is None:
            unit = "51a" if g == 51 else E.map_unit(g) or f"G{g:02d}"
        s = r["dw"]
        if s.get("class") is None:
            continue
        jk = r.get("jack_dw", {})
        base = dict(period_unit=unit, goal_no=g, channel="work_host_labels", role=role, unit_local=local,
                    source="data/processed/H128-coarsening-vs-freeze/results/units.json", post_hoc=False,
                    n=r["meta"].get("n_agents"), n_kind="agents", notes=f"code={r['code']}; verdict={r['verdict']}")

        def ci(est, key):
            se = jk.get(key, {}).get("se")
            if se is None or est is None:
                return dict(ci_lo=None, ci_hi=None, ci_kind="none", se=None)
            lo, hi = E.ci_from_se(est, se)
            return dict(ci_lo=lo, ci_hi=hi, ci_kind="jackknife_z", se=se)
        tf = tf_eff(s)
        rows.append({**base, "statistic": "h128_freeze_time_dw", "estimate": tf, **ci(tf, "t_f"),
                     "method": "dw=(N_p-1)/(N_h-1) on 15-min active grid; t_f = first time within one domain of the final level (A1); censored -> H",
                     "null": "freeze baseline t_f <= 3 h; free vs named Mann-Whitney"})
        rows.append({**base, "statistic": "h128_excess_area_dw", "estimate": s["A_u"], **ci(s["A_u"], "A_u"),
                     "method": "normalized excess area of dw over [t_pk, t_pk+8h], active hours",
                     "null": "0 for an instant freeze"})
        if s.get("alpha") is not None and s.get("alpha_ci") and s.get("alpha_fit_ok"):
            lo, hi = s["alpha_ci"]
            rows.append({**base, "statistic": "h128_coarsening_alpha_dw", "estimate": s["alpha"], "ci_lo": lo, "ci_hi": hi,
                         "ci_kind": "percentile", "method": "power-law fit A(t-t_pk+0.25)^-alpha to dw; 2-h block residual bootstrap",
                         "null": "HH band 0.3-0.5; synthetic Q0 spread"})
        cm = r["N_p"].get("c_m")
        if cm is not None and np.isfinite(cm):
            nd = sum((r["N_p"].get("deaths") or {}).values())
            rows.append({**base, "statistic": "h128_merge_share", "estimate": cm, "ci_lo": None, "ci_hi": None, "ci_kind": "none",
                         "n": nd, "n_kind": "project deaths after t_pk",
                         "method": "share of project deaths by merge (last host departs to an occupied repo)",
                         "null": "exogenous finish: c_m ~ 0 (synthetic Q3)"})
    rows = [x for x in rows if x["estimate"] is not None and np.isfinite(x["estimate"])]
    E.write_estimates(rows, hypothesis="H128")
    print(f"wrote {len(rows)} estimates rows")


if __name__ == "__main__":
    main()
