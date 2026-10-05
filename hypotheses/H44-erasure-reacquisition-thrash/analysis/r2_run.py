"""H44 round-2 real-data run (exploratory, non-reserved data only): R2 sawtooth and cap, reference sensitivity, R3 re-open
share, R4 loop lever, the regime I/II long-session arm, pooled values and estimates rows. R1 runs in r2_label.py.

Outputs: data/processed/H44-erasure-reacquisition-thrash/r2/{G<NN>/r2_results.json, long_arm.json, pooled.json,
         per_period_estimates_H44_r2.parquet}; rows also go to the shared table through write_estimates (--estimates).
Usage:   uv run python hypotheses/H44-erasure-reacquisition-thrash/analysis/r2_run.py [--periods G38,G51] [--B 200]
         [--estimates]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import h44lib as L  # noqa: E402
import r2lib as R  # noqa: E402
from h44lib import C  # noqa: E402

OUTD = C.OUT / "r2"
PERIODS = ["G36", "G37", "G38", "G39", "G40", "G41", "G42", "G44", "G51"]
MIN_SAW_LAB = 300


def j(x):
    return json.loads(json.dumps(x, default=lambda o: o.tolist() if hasattr(o, "tolist") else float(o)))


def r2_block(saw: pl.DataFrame, B: int, rng, full: bool = True) -> dict:
    """Curves, fits, parameter CIs and cap statistics for one set of sawtooth calls."""
    saw = saw.with_columns(pl.col("cat").is_in(C.REACQ_IDX).alias("reacq"))
    out = {"n_segments": int(saw.select("agent", "pt_date", "seg").n_unique()), "n_calls": saw.height}
    num, den, cl = R.curve_sums(saw, "any_write")
    Bw = L.boot_weights(num.shape[0], B, rng)
    out["W_fit"] = R.fit_compare(num, den, True, Bw)
    out["W_par"] = R.param_boot(num, den, Bw, "M2", True, 12.0)
    out["cap"] = R.cap_stats(num, den, Bw, 1.0)
    out["cap_c0"] = R.cap_stats(num, den, Bw, 0.0)
    W_emp = num.sum(0) / np.clip(den.sum(0), 1e-12, None)
    fg = out["W_fit"]["fits"]["M2g"]; fl = out["W_fit"]["fits"]["M2"]
    out["extrap"] = R.extrapolate(fg, fl, W_emp, 1.0)
    nr, dr, _ = R.curve_sums(saw, "reacq", cl_codes=cl)
    out["R_fit"] = R.fit_compare(nr, dr, True, Bw)
    out["R_par"] = R.param_boot(nr, dr, Bw, "M2", True, 12.0)
    nk, dk, _ = R.curve_sums(saw, "n_work", cl_codes=cl)
    out["work_curve"] = (nk.sum(0) / np.clip(dk.sum(0), 1e-12, None)).tolist()
    out["work_cap"] = R.cap_stats(nk, dk, Bw, 1.0)
    nl, dl, _ = R.curve_sums(saw, "in_loop", cl_codes=cl)
    out["loop_curve"] = (nl.sum(0) / np.clip(dl.sum(0), 1e-12, None)).tolist()
    # loop share slope over k 11..40 (bootstrap)
    kk = np.arange(11, 41)
    def slope(nu, de):
        y = nu[10:] / np.clip(de[10:], 1e-12, None)
        return float(np.polyfit(kk, y, 1)[0])
    out["loop_slope"] = [slope(nl.sum(0), dl.sum(0)), *L._ci(np.array([slope(Bw[b] @ nl, Bw[b] @ dl)
                                                                         for b in range(Bw.shape[0])]))]
    # per-minute cap curve (wall clock per call from t_first gaps; the gap after k = 40 holds the consolidation)
    if full and "t_first" in saw.columns:
        s2 = saw.sort("agent", "t_first").with_columns(
            (pl.col("t_first").shift(-1).over("agent", "pt_date") - pl.col("t_first")).dt.total_seconds().alias("dt"))
        s2 = s2.with_columns(pl.col("dt").clip(0, 900).fill_null(np.nan))
        ok = s2.filter(pl.col("dt").is_not_nan())
        dn, dd, _ = R.curve_sums(ok.with_columns(pl.col("dt").cast(pl.Float64)), "dt", cl_codes=cl)
        dt_k = dn.sum(0) / np.clip(dd.sum(0), 1e-12, None)
        dt_reset = float(dt_k[-1] - np.median(dt_k[10:39]))
        dt_k2 = dt_k.copy(); dt_k2[-1] = np.median(dt_k[10:39])
        dn2 = dn.copy(); dn2[:, -1] = dd[:, -1] * dt_k2[-1]
        out["cap_minute"] = R.cap_stats(num, den, Bw, 0.0, dt_num=dn2, dt_den=dd, dt_reset=max(dt_reset, 0.0))
        out["dt_per_call"] = dt_k.tolist()
        out["dt_reset_s"] = dt_reset
    return out


def voluntary_lengths(calls: pl.DataFrame, W_forced: np.ndarray) -> dict:
    """Observed writes per call in voluntary-closed segments (opened by any consolidation) by length bin vs Y(L)
    predicted from the forced complete-sawtooth curve (c0 = 1)."""
    seg = (calls.filter(pl.col("seg_kind").is_in(["forced", "voluntary"]) & (pl.col("seg_end_kind") == "voluntary"))
           .group_by("agent", "pt_date", "seg").agg(pl.col("any_write").sum().alias("w"), pl.len().alias("Lseg"),
                                                     pl.col("n_work").sum().alias("wk")))
    Yp = R.cap_curve(W_forced, 1.0)
    out = {}
    for lo, hi in ((10, 19), (20, 29), (30, 39)):
        s = seg.filter(pl.col("Lseg").is_between(lo, hi))
        if s.height < 30:
            continue
        obs = float(s["w"].sum() / (s["Lseg"].sum() + s.height))
        pred = float(np.mean([Yp[int(l_) - 1] for l_ in s["Lseg"].to_list()]))
        out[f"{lo}-{hi}"] = {"n": s.height, "obs_Y": obs, "pred_Y": pred, "ratio": obs / pred if pred > 0 else None}
    return out


def r3_block(calls, ev, obj, B, seed) -> dict:
    out = {}
    for col in ("paths", "arts", "arts_cwd"):
        p = R.object_panel(calls, ev, obj, col)
        out[col] = R.reopen_stats(p, B=B, seed=seed)
        fr = R.recency_frac(calls, ev, obj, col, p["ev_id"].unique().to_list())
        out[col]["recency_adjusted"] = R.recency_adjusted(p, fr, out[col], B=B, seed=seed)
        if col == "paths":
            nf = R.new_object_flags(calls, obj, col)
            q = p.filter(pl.col("k").is_between(1, 10) & pl.col("cat").is_in(R.READ_IDX) & pl.col("obj").is_not_null()
                         & (pl.col("obj").list.len() > 0)).join(nf, on="turn_id", how="left")
            out["paths"]["all_new_share"] = {k_: float(g["all_new"].fill_null(False).mean())
                                             for (k_,), g in q.group_by("ev_kind")}
            out["paths"]["coverage_read_calls_with_objects"] = float(
                p.filter(pl.col("k").is_between(1, 10) & pl.col("cat").is_in(R.READ_IDX))
                .select((pl.col("obj").is_not_null() & (pl.col("obj").list.len() > 0)).mean()).item())
    return out


def r4_block(calls, ev, B, seed) -> dict:
    out = {}
    g = R.loop_strata(calls, ev)
    out["writes"] = R.lever_stats(g, B=B, seed=seed, outcome="w")
    out["work"] = R.lever_stats(g, B=B, seed=seed, outcome="k")
    gn = R.loop_strata(calls, ev, lcol="in_loop_norm")
    out["writes_normhash"] = R.lever_stats(gn, B=B, seed=seed, outcome="w")
    gv = R.loop_strata(calls, ev, kinds=("voluntary", "pseudo31")).with_columns(
        pl.col("ev_kind").replace({"voluntary": "forced"}))
    out["writes_voluntary"] = R.lever_stats(gv, B=B, seed=seed, outcome="w")
    # post hoc (labelled): "stuck" loops = >= 3 in-loop calls and no write in -10..-1; "productive" = >= 3 and >= 1 write
    gs = g.with_columns(pl.when((pl.col("nl") >= 3) & (pl.col("w_pre") == 0)).then(pl.lit("loop"))
                        .when(pl.col("nl") == 0).then(pl.lit("free")).otherwise(pl.lit("other")).alias("stratum"))
    out["posthoc_stuck_writes"] = R.lever_stats(gs, B=B, seed=seed, outcome="w")
    gp = g.with_columns(pl.when((pl.col("nl") >= 3) & (pl.col("w_pre") > 0)).then(pl.lit("loop"))
                        .when(pl.col("nl") == 0).then(pl.lit("free")).otherwise(pl.lit("other")).alias("stratum"))
    out["posthoc_productive_writes"] = R.lever_stats(gp, B=B, seed=seed, outcome="w")
    # operator number: net write calls per reset for a looping agent over +1..+10 = 10 * E_loop
    out["net_writes_per_reset_loop"] = [10 * x for x in out["writes"]["E_loop"]]
    out["net_work_per_reset_loop"] = [10 * x for x in out["work"]["E_loop"]]
    return out


def long_arm(B: int, rng) -> dict:
    cl_ = pl.read_parquet(OUTD / "calls_long.parquet")
    C.refuse_holdout(cl_["pt_date"].unique().to_list(), "long calls")
    cl_ = cl_.with_columns((pl.col("agent").cast(pl.Utf8) + "_" + pl.col("pt_date")).alias("cl"))
    out = {}
    for (per,), g in sorted(cl_.group_by("period"), key=lambda t: t[0]):
        g = g.filter(pl.col("k").is_between(1, 60))
        long_s = g.filter(pl.col("sess_len") >= 41)
        n_long = long_s.select("agent", "sess").n_unique()
        res = {"n_sessions": int(g.select("agent", "sess").n_unique()), "n_sessions_gt40": int(n_long),
               "regime": g["regime"][0]}
        num, den, clc = R.curve_sums(g, "any_write", kmax=60)
        res["W_curve_all"] = (num.sum(0) / np.clip(den.sum(0), 1e-12, None)).tolist()
        res["n_curve_all"] = den.sum(0).tolist()
        if n_long >= 30:
            nL, dL, _ = R.curve_sums(long_s, "any_write", kmax=60)
            W = L.boot_weights(nL.shape[0], B, rng)
            def d(nu, de):
                a = nu[..., 40:60].sum(-1) / np.clip(de[..., 40:60].sum(-1), 1e-12, None)
                b = nu[..., 30:40].sum(-1) / np.clip(de[..., 30:40].sum(-1), 1e-12, None)
                return a - b, a, b
            dd, a, b = d(nL.sum(0), dL.sum(0))
            bd = d(W @ nL, W @ dL)[0]
            res["W41_60_minus_W31_40"] = [float(dd), *L._ci(bd)]
            res["W41_60"] = float(a); res["W31_40"] = float(b)
            res["W_curve_long"] = (nL.sum(0) / np.clip(dL.sum(0), 1e-12, None)).tolist()
            nw, dw, _ = R.curve_sums(long_s, "n_work", kmax=60)
            dk = d(nw.sum(0), dw.sum(0)); bk = d(W @ nw, W @ dw)[0]
            res["work41_60_minus_work31_40"] = [float(dk[0]), *L._ci(bk)]
            # post hoc (labelled): drop the last 10 calls of every session (a voluntary stop follows a write burst)
            trim = long_s.filter(pl.col("k") <= pl.col("sess_len") - 10)
            nT, dT, _ = R.curve_sums(trim, "any_write", kmax=60, cl_codes=np.unique(long_s["cl"].to_numpy()))
            okT = dT[:, 40:60].sum() > 0
            if okT:
                dT_, aT, bT = d(nT.sum(0), dT.sum(0))
                res["posthoc_trim10_W41_60_minus_W31_40"] = [float(dT_), *L._ci(d(W @ nT, W @ dT)[0])]
                res["posthoc_trim10_n_calls_41_60"] = int(dT[:, 40:60].sum())
            # first-10 dip in these sessions (session start = context reset)
            e10 = nL[:, :10].sum() / max(dL[:, :10].sum(), 1); m = nL[:, 10:40].sum() / max(dL[:, 10:40].sum(), 1)
            res["W1_10_over_W11_40"] = float(e10 / m) if m > 0 else None
        out[per] = res
        C.log("long", per, {k_: v for k_, v in res.items() if not k_.startswith(("W_curve", "n_curve"))})
    return out


def run_period(per, calls_all, ev_all, obj, B) -> dict:
    t0 = time.time()
    rng = np.random.default_rng(int(per[1:]) + 1000)
    calls = calls_all.filter(pl.col("period") == per)
    ev = ev_all.filter(pl.col("period") == per)
    roster = pl.read_parquet(C.SH / "roster.parquet").select("agent", "lab", "model_string")
    res = {"period": per}
    saw = R.sawtooth_calls(calls)
    res["r2"] = r2_block(saw, B, rng)
    W_forced = np.array(res["r2"]["W_fit"]["y"])
    res["r2"]["voluntary_lengths"] = voluntary_lengths(calls, W_forced)
    res["r2_all_forced_opened"] = r2_block(R.sawtooth_calls(calls, ("forced",), ("forced", "voluntary", "session",
                                                                                  "day_end"), full=False), B, rng, False)
    res["r2_voluntary_opened"] = r2_block(R.sawtooth_calls(calls, ("voluntary",), ("forced",), full=True), B, rng, False)
    # labs and models
    sl = saw.join(roster, on="agent")
    res["r2_labs"] = {}
    for (lab,), g in sorted(sl.group_by("lab"), key=lambda t: t[0]):
        nseg = g.select("agent", "pt_date", "seg").n_unique()
        if nseg >= MIN_SAW_LAB:
            res["r2_labs"][lab] = r2_block(g, B, rng, False)
    if per == "G51":
        res["r2_models"] = {}
        for (m,), g in sorted(sl.group_by("model_string"), key=lambda t: t[0]):
            nseg = g.select("agent", "pt_date", "seg").n_unique()
            if nseg >= MIN_SAW_LAB:
                res["r2_models"][m] = r2_block(g, B, rng, False)
    res["refs"] = R.reference_table(calls, ev, B=B, seed=int(per[1:]))
    res["r3"] = r3_block(calls, ev, obj, B, int(per[1:]))
    res["r4"] = r4_block(calls, ev, B, int(per[1:]))
    C.log(per, f"{time.time() - t0:.0f}s")
    return j(res)


def pooled(results: dict) -> dict:
    def pool(getter, min_ok=lambda r: True):
        e, lo, hi, used = [], [], [], []
        for per, r in results.items():
            if not min_ok(r):
                continue
            try:
                v = getter(r)
            except (KeyError, TypeError, IndexError):
                continue
            if v and all(np.isfinite(v[:3])):
                e.append(v[0]); lo.append(v[1]); hi.append(v[2]); used.append(per)
        d = L.dl_pool(e, lo, hi)
        d["periods"] = used
        return d
    out = {
        "W_beta": pool(lambda r: r["r2"]["W_par"]["beta"]),
        "R_beta": pool(lambda r: r["r2"]["R_par"]["beta"]),
        "W_l2": pool(lambda r: r["r2"]["W_par"]["l2"]),
        "R_l1": pool(lambda r: r["r2"]["R_par"]["l1"]), "R_l2": pool(lambda r: r["r2"]["R_par"]["l2"]),
        "loop_slope": pool(lambda r: r["r2"]["loop_slope"]),
        "r3_dFP_paths": pool(lambda r: r["r3"]["paths"]["d_forced_pseudo31"], lambda r: r["r3"]["paths"]["forced"].get("n_events", 0) >= 200),
        "r3_dFV_paths": pool(lambda r: r["r3"]["paths"]["d_forced_voluntary"], lambda r: r["r3"]["paths"]["forced"].get("n_events", 0) >= 200),
        "r3_excess_FP_paths": pool(lambda r: r["r3"]["paths"]["recency_adjusted"]["excess_FP"], lambda r: r["r3"]["paths"]["forced"].get("n_events", 0) >= 200),
        "r3_excess_FV_paths": pool(lambda r: r["r3"]["paths"]["recency_adjusted"]["excess_FV"], lambda r: r["r3"]["paths"]["forced"].get("n_events", 0) >= 200),
        "r3_excess_FP_arts": pool(lambda r: r["r3"]["arts"]["recency_adjusted"]["excess_FP"], lambda r: r["r3"]["arts"]["forced"].get("n_events", 0) >= 200),
        "r3_excess_FV_arts": pool(lambda r: r["r3"]["arts"]["recency_adjusted"]["excess_FV"], lambda r: r["r3"]["arts"]["forced"].get("n_events", 0) >= 200),
        "r3_rho_forced_paths": pool(lambda r: r["r3"]["paths"]["forced"]["rho"]),
        "r3_rho_pseudo_paths": pool(lambda r: r["r3"]["paths"]["pseudo31"]["rho"]),
        "r2_Y20_over_Y40": pool(lambda r: r["r2"]["cap"]["Y20_over_Y40"]),
        "r2_Y30_over_Y40": pool(lambda r: r["r2"]["cap"]["Y30_over_Y40"]),
        "r4_logDDD": pool(lambda r: r["r4"]["writes"]["logDDD"], lambda r: r["r4"]["writes"]["n"]["forced_loop"] >= 30),
        "r4_posthoc_E_stuck": pool(lambda r: r["r4"]["posthoc_stuck_writes"]["E_loop"], lambda r: r["r4"]["posthoc_stuck_writes"]["n"]["forced_loop"] >= 30),
        "r4_posthoc_E_productive": pool(lambda r: r["r4"]["posthoc_productive_writes"]["E_loop"], lambda r: r["r4"]["posthoc_productive_writes"]["n"]["forced_loop"] >= 30),
        "r3_dFP_arts": pool(lambda r: r["r3"]["arts"]["d_forced_pseudo31"], lambda r: r["r3"]["arts"]["forced"].get("n_events", 0) >= 200),
        "r4_E_loop": pool(lambda r: r["r4"]["writes"]["E_loop"], lambda r: r["r4"]["writes"]["n"]["forced_loop"] >= 30),
        "r4_E_free": pool(lambda r: r["r4"]["writes"]["E_free"], lambda r: r["r4"]["writes"]["n"]["forced_loop"] >= 30),
        "r4_DDD": pool(lambda r: r["r4"]["writes"]["DDD"], lambda r: r["r4"]["writes"]["n"]["forced_loop"] >= 30),
        "r4_E_loop_work": pool(lambda r: r["r4"]["work"]["E_loop"], lambda r: r["r4"]["writes"]["n"]["forced_loop"] >= 30),
        "r4_DDD_work": pool(lambda r: r["r4"]["work"]["DDD"], lambda r: r["r4"]["writes"]["n"]["forced_loop"] >= 30),
    }
    for ref in ("far", "near", "whole", "steady", "sawtooth"):
        out[f"Omega_{ref}"] = pool(lambda r, ref=ref: r["refs"]["refs"][ref]["Omega"])
        out[f"dV_{ref}"] = pool(lambda r, ref=ref: r["refs"]["refs"][ref]["dV"])
    return j(out)


def estimate_rows(results: dict) -> list[dict]:
    rows = []
    for per, r in results.items():
        g = int(per[1:])
        role = "native" if per in ("G51", "G38") else "replication"
        src = f"data/processed/H44-erasure-reacquisition-thrash/r2/{per}/r2_results.json"
        nsaw = r["r2"]["n_segments"]

        def add(stat, ch, v, n, nk, method, null, post_hoc=False, rl=None):
            if v is None or not np.all(np.isfinite(v[:3])):
                return
            rows.append({"period_unit": str(g), "goal_no": g, "statistic": stat, "channel": ch, "estimate": float(v[0]),
                         "ci_lo": float(v[1]), "ci_hi": float(v[2]), "n": float(n), "method": method, "null": null,
                         "role": rl or role, "ci_level": 0.95, "ci_kind": "percentile", "n_kind": nk,
                         "confirmatory": False, "post_hoc": post_hoc, "status": "exploratory", "source": src,
                         "notes": "H44 round 2 (2026-10-05)"})
        m_saw = "complete forced sawtooths (40 calls), M2 fit with l2 <= 12; agent-day cluster bootstrap"
        add("r2_W_beta", "writes", r["r2"]["W_par"]["beta"], nsaw, "segments", m_saw, "flat plateau (beta = 0)")
        add("r2_W_l1", "writes", r["r2"]["W_par"]["l1"], nsaw, "segments", m_saw, "none")
        add("r2_W_l2", "writes", r["r2"]["W_par"]["l2"], nsaw, "segments", m_saw, "none")
        add("r2_R_l1", "reacq", r["r2"]["R_par"]["l1"], nsaw, "segments", m_saw, "none")
        add("r2_R_l2", "reacq", r["r2"]["R_par"]["l2"], nsaw, "segments", m_saw, "none")
        add("r2_R_beta", "reacq", r["r2"]["R_par"]["beta"], nsaw, "segments", m_saw, "flat plateau (beta = 0)")
        add("r2_Lstar", "writes", [r["r2"]["cap"]["L_star"], *r["r2"]["cap"]["L_star_ci"]], nsaw, "segments",
            "argmax_L sum_{k<=L} W(k)/(L+1) on [5, 40]; agent-day cluster bootstrap", "edge rule P(L*=40) >= 0.8")
        add("r2_Y20_over_Y40", "writes", r["r2"]["cap"]["Y20_over_Y40"], nsaw, "segments",
            "output per call at cap 20 / cap 40 (c0 = 1)", "ratio 1")
        add("r2_loop_slope", "in_loop", r["r2"]["loop_slope"], nsaw, "segments",
            "OLS slope of in-loop share over k 11..40, complete sawtooths", "slope 0")
        for ref in ("far", "near", "whole", "steady", "sawtooth"):
            v = r["refs"]["refs"].get(ref)
            if v:
                add(f"r2_Omega_ref_{ref}", "writes", v["Omega"], r["refs"]["n_events"], "events",
                    f"forced write dip +1..+10 vs reference '{ref}'", "Omega 0")
        for col in ("paths", "arts"):
            x = r["r3"][col]
            n_ev = x["forced"].get("n_events", 0)
            add("r3_reopen_rho", f"forced:{col}", x["forced"].get("rho"), n_ev, "events",
                "share of post-reset read calls (+1..+10) touching an object of the pre window (-20..-1)", "pseudo31")
            add("r3_reopen_rho", f"pseudo31:{col}", x["pseudo31"].get("rho"), x["pseudo31"].get("n_events", 0),
                "events", "share of post-boundary read calls touching a pre-window object", "none")
            add("r3_d_forced_pseudo", col, x.get("d_forced_pseudo31"), n_ev, "events",
                "re-open share forced minus pseudo31; agent-day cluster bootstrap", "recency null (synthetic)")
            add("r3_d_forced_voluntary", col, x.get("d_forced_voluntary"), n_ev, "events",
                "re-open share forced minus voluntary; agent-day cluster bootstrap", "0")
        w4 = r["r4"]["writes"]
        nl = w4["n"]["forced_loop"]
        add("r4_E_loop", "writes", w4["E_loop"], nl, "events",
            "dW(+1..+10 minus -10..-1) forced minus pseudo31, looping pre window (>= 3 in-loop calls)", "0")
        add("r4_E_free", "writes", w4["E_free"], w4["n"]["forced_free"], "events",
            "dW forced minus pseudo31, loop-free pre window", "0")
        add("r4_DDD", "writes", w4["DDD"], nl, "events", "E_loop - E_free (absolute)", "multiplicative-dip null q95")
        add("r4_E_loop", "work", r["r4"]["work"]["E_loop"], nl, "events",
            "work commits per call, forced minus pseudo31, looping pre window", "0")
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--periods", default=",".join(PERIODS))
    ap.add_argument("--B", type=int, default=200)
    ap.add_argument("--estimates", action="store_true")
    ap.add_argument("--skip-long", action="store_true")
    a = ap.parse_args()
    calls = pl.read_parquet(C.OUT / "calls.parquet")
    ev = pl.read_parquet(C.OUT / "events.parquet")
    obj = pl.read_parquet(OUTD / "objects.parquet")
    for df, nm in ((calls, "calls"), (ev, "events")):
        C.refuse_holdout(df["pt_date"].unique().to_list(), nm)
    results = {}
    for per in a.periods.split(","):
        r = run_period(per, calls, ev, obj, a.B)
        (OUTD / per).mkdir(parents=True, exist_ok=True)
        (OUTD / per / "r2_results.json").write_text(json.dumps(r, indent=1))
        results[per] = r
    if not a.skip_long:
        la = long_arm(a.B, np.random.default_rng(3044))
        (OUTD / "long_arm.json").write_text(json.dumps(j(la), indent=1))
    if len(results) == len(PERIODS):
        (OUTD / "pooled.json").write_text(json.dumps(pooled(results), indent=1))
        rows = estimate_rows(results)
        pl.DataFrame(rows).write_parquet(OUTD / "per_period_estimates_H44_r2.parquet")
        if a.estimates:
            sys.path.insert(0, str(C.ROOT / "infra/shared"))
            import estimates as E
            E.write_estimates(rows, hypothesis="H44")
            C.log("estimates rows written", len(rows))
    C.log("done")


if __name__ == "__main__":
    main()
