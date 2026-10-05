"""H43 round 2 on real, non-reserved data (card "Round 2"; amendments A2-1..A2-4).

  --only r2   nudge facilitation vs nudger selection (G51 before 08-21, after-PAUSE timer wakes)
  --only r3   marginal value of the k-th directed kick in one read; provider / timing sensitivity; read-out unit check
  --only r5   pooled timer-wake test over regime-III periods (fresh vs re-kicked wakes)
  --only r6   decomposition of the NE43 drop in sustained escapes per idle minute

Output: data/processed/H43-kick-refractory-window/r2/results_<item>.json
Usage:  uv run python hypotheses/H43-kick-refractory-window/analysis/run_r2.py --only r2 [--B 200]
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r2lib as R  # noqa: E402

B_DEF = 200


def contrast_est(fit, nm, a, b):
    i, j = nm.index(a), nm.index(b)
    d = fit["beta"][i] - fit["beta"][j]
    v = fit["cov"][i, i] + fit["cov"][j, j] - 2 * fit["cov"][i, j]
    return float(d), float(np.sqrt(max(v, 1e-12)))


def boot_fit(X, y, g, day, rng, B, stats, ridge=1e-6):
    """Point fit and day-block bootstrap of named statistics. stats: dict name -> fn(fit) -> float."""
    f = R.fe_logit(X, y, g, ridge=ridge)
    pt = {k: fn(f) for k, fn in stats.items()}
    dr = {k: [] for k in stats}
    for idx in R.day_boot(day, rng, B):
        fb = R.fe_logit(X[idx], y[idx], g[idx], ridge=ridge)
        for k, fn in stats.items():
            try:
                dr[k].append(fn(fb))
            except Exception:
                dr[k].append(np.nan)
    return f, {k: R.summarize(pt[k], dr[k]) | {"se_analytic": None} for k in stats}


def b_of(name, nm):
    return lambda f: float(f["beta"][nm.index(name)])


def d_of(a, b, nm):
    return lambda f: float(f["beta"][nm.index(a)] - f["beta"][nm.index(b)])


def daycodes(w):
    return np.unique(w["pt_date"].to_numpy(), return_inverse=True)[1]


# =============================================================================================== R2
def run_r2(B, rng) -> dict:
    w = R.add_nudge_history(R.load_wakes((51,), date_to=R.NE43))
    y = w["y_sus"].to_numpy().astype(float)
    ya = w["y_any"].to_numpy().astype(float)
    ag = w["agent"].to_numpy()
    aday = w["aday"].to_numpy()
    day = daycodes(w)
    st = w["nprev_state"].to_numpy()
    N = w["N_now"].to_numpy()
    out = {"n_wakes": w.height, "n_days": int(day.max() + 1), "n_agents": int(len(np.unique(ag))),
           "counts": {"first": int((N & (st == 0)).sum()), "refire_same": int((N & (st == 1)).sum()),
                      "refire_new": int((N & (st == 2)).sum()),
                      "unnudged_by_state": {str(s): int((~N & (st == s)).sum()) for s in (0, 1, 2)},
                      "refire_reset_between": int((N & (st > 0) & w["reset_between"].to_numpy()).sum())}}
    # descriptive escape rates (y_sus) by state x nudged
    out["rates"] = {f"{s}|{int(n)}": float(y[(st == s) & (N == n)].mean()) for s in (0, 1, 2) for n in (0, 1)}
    models = {}
    for lab, kw, yy, grp in (("base", dict(), y, ag), ("proxy", dict(proxies=True), y, ag),
                             ("proxy_agentday", dict(proxies=True), y, aday),
                             ("glance_base", dict(), ya, ag), ("glance_proxy", dict(proxies=True), ya, ag)):
        X, nm = R.r2_design(w, **kw)
        stats = {"dF": d_of("N_refire", "N_first", nm), "g_first": b_of("N_first", nm), "g_refire": b_of("N_refire", nm),
                 "prior_same": b_of("prior_same", nm), "prior_new": b_of("prior_new", nm)}
        f, s = boot_fit(X, yy, grp, day, rng, B, stats)
        s["dF"]["se_analytic"] = contrast_est(f, nm, "N_refire", "N_first")[1]
        models[lab] = {"stats": s, "n_used": f["n"], "n_groups": f["n_groups"], "converged": f["converged"],
                       "coef": dict(zip(nm, f["beta"].tolist()))}
        print(f"R2 {lab}: dF {s['dF']['est']:+.3f} {np.round(s['dF']['ci'], 3)} | first {s['g_first']['est']:+.3f} "
              f"refire {s['g_refire']['est']:+.3f}", flush=True)
    # split re-fire classes (proxy model)
    X, nm = R.r2_design(w, proxies=True, split_refire=True)
    stats = {"d_same": d_of("N_ref_same", "N_first", nm), "d_new": d_of("N_ref_new", "N_first", nm),
             "g_first": b_of("N_first", nm), "g_same": b_of("N_ref_same", nm), "g_new": b_of("N_ref_new", nm)}
    f, s = boot_fit(X, y, ag, day, rng, B, stats)
    models["proxy_split"] = {"stats": s, "n_used": f["n"]}
    print(f"R2 split: same {s['d_same']['est']:+.3f} {np.round(s['d_same']['ci'], 3)} new {s['d_new']['est']:+.3f} "
          f"{np.round(s['d_new']['ci'], 3)}", flush=True)
    # reset partition (descriptive, A2-3)
    X, nm = R.r2_design(w, proxies=True)
    rb = w["reset_between"].to_numpy().astype(float)
    ref = (N & (st > 0)).astype(float)
    Xr = np.column_stack([X, rb, ref * rb])
    nmr = nm + ["reset_between", "N_refire_x_reset"]
    stats = {"refire_x_reset": b_of("N_refire_x_reset", nmr), "reset_main": b_of("reset_between", nmr)}
    f, s = boot_fit(Xr, y, ag, day, rng, B, stats)
    models["reset_partition"] = {"stats": s}
    print(f"R2 reset: interaction {s['refire_x_reset']['est']:+.3f} {np.round(s['refire_x_reset']['ci'], 3)}", flush=True)
    out["models"] = models
    return out


# =============================================================================================== R3
def unit_of(d: pl.DataFrame) -> np.ndarray:
    c = pl.read_parquet(R.ROOT / "data/processed/H43-kick-refractory-window/calls.parquet", columns=["turn_id", "unit_id"])
    u = d.select("turn_id").join(c, on="turn_id", how="left")["unit_id"].fill_null("na").to_numpy()
    return u


def dose_X(d: pl.DataFrame, dose_col="dose"):
    X, nm = R.dose_design(d, dose_col=dose_col)
    # day third and unit dummies (card model)
    t = d["t_call"].to_numpy()
    cal = pl.read_parquet(R.SH / "calendar.parquet").select("pt_date", R.ep("win_start"), R.ep("win_end"))
    cc = d.select("pt_date").join(cal, on="pt_date", how="left")
    ws, we = cc["win_start"].to_numpy(), cc["win_end"].to_numpy()
    third = np.clip(((t - ws) / np.maximum(we - ws, 60) * 3).astype(int), 0, 2)
    extra = [(third == 1).astype(float), (third == 2).astype(float)]
    names = ["third_1", "third_2"]
    u = unit_of(d)
    lev = sorted(set(u))
    for x in lev[1:]:
        extra.append((u == x).astype(float)); names.append(f"unit_{x}")
    return np.column_stack([X] + extra), nm + names


def r3_fit(d: pl.DataFrame, rng, B, dose_col="dose"):
    if d.height == 0:
        return None
    X, nm = dose_X(d, dose_col)
    y = d["talk"].to_numpy().astype(float)
    ag = d["agent"].to_numpy()
    day = daycodes(d)
    stats = {"f1": b_of("f1", nm), "f2": b_of("f2", nm), "f3p": b_of("f3p", nm), "m2": d_of("f2", "f1", nm),
             "m3": d_of("f3p", "f2", nm),
             "rho2": lambda f: float((f["beta"][nm.index("f2")] - f["beta"][nm.index("f1")]) / f["beta"][nm.index("f1")])
             if f["beta"][nm.index("f1")] > 0.05 else np.nan}
    f, s = boot_fit(X, y, ag, day, rng, B, stats)
    dose = d[dose_col].to_numpy()
    return {"stats": s, "n_calls": d.height, "n_used": f["n"], "dose_counts": {str(k): int((np.minimum(dose, 3) == k).sum()) for k in range(4)},
            "talk_rate_by_dose": {str(k): float(y[np.minimum(dose, 3) == k].mean()) if (np.minimum(dose, 3) == k).any() else None for k in range(4)},
            "n_days": int(day.max() + 1)}


def run_r3(B, rng) -> dict:
    out = {"periods": {}, "g51_sens": {}, "pooled": {}}
    calls = pl.read_parquet(R.ROOT / "data/processed/H43-kick-refractory-window/calls.parquet", columns=["goal_no"])
    goals = sorted(int(g) for g in calls["goal_no"].unique().to_list())
    for g in goals:
        t0 = time.time()
        d = R.dose_table((g,), read_state="active")
        n2 = int((d["dose"] >= 2).sum())
        if n2 < 30:
            out["periods"][f"G{g:02d}"] = {"skipped": f"{n2} calls at dose >= 2"}
            continue
        r = r3_fit(d, rng, B if g != 51 else B)
        r["regime"] = sorted(set(d["regime"].to_list()))
        out["periods"][f"G{g:02d}"] = r
        s = r["stats"]
        print(f"R3 G{g:02d} ({time.time() - t0:.0f}s): f1 {s['f1']['est']:+.3f} m2 {s['m2']['est']:+.3f} rho2 {s['rho2']['est']:.3f} "
              f"{np.round(s['rho2']['ci'], 3)} n2+ {n2}", flush=True)
        if g == 51:
            sens = {}
            sens["S2_gemini_logged"] = r3_fit(d.filter(pl.col("logged")), rng, B)
            sens["S2b_not_logged"] = r3_fit(d.filter(~pl.col("logged")), rng, B)
            sens["S3_no_uncertain"] = r3_fit(d.filter(~pl.col("unc_here") & ~pl.col("unc_prev")), rng, B)
            sens["S4_lo"] = r3_fit(d, rng, B, dose_col="dose_lo")
            sens["S4_hi"] = r3_fit(d, rng, B, dose_col="dose_hi")
            sens["no_window_term"] = None
            X, nm = dose_X(d)
            j = nm.index("ln_window")
            Xn = np.delete(X, j, axis=1)
            nmn = nm[:j] + nm[j + 1:]
            fn = R.fe_logit(Xn, d["talk"].to_numpy().astype(float), d["agent"].to_numpy())
            sens["no_window_term"] = R.marginals(fn["beta"], nmn)
            for k, v in sens.items():
                if v and "stats" in v:
                    print(f"   {k}: rho2 {v['stats']['rho2']['est']:.3f} {np.round(v['stats']['rho2']['ci'], 3)} f1 {v['stats']['f1']['est']:+.3f}",
                          flush=True)
            out["g51_sens"] = sens
            del d
    # random-effects pooling of f1 and m2 (all fitted periods; and without G51)
    fitted = {p: v for p, v in out["periods"].items() if "stats" in v}
    for lab, keys in (("all", list(fitted)), ("without_G51", [p for p in fitted if p != "G51"]),
                      ("regime_I", [p for p in fitted if fitted[p]["regime"] == ["I"]])):
        if not keys:
            continue
        pf = R.dl_pool([fitted[p]["stats"]["f1"]["est"] for p in keys], [fitted[p]["stats"]["f1"]["se"] for p in keys])
        pm = R.dl_pool([fitted[p]["stats"]["m2"]["est"] for p in keys], [fitted[p]["stats"]["m2"]["se"] for p in keys])
        dr = rng.normal(pm["mu"], pm["se"], 20000) / rng.normal(pf["mu"], pf["se"], 20000)
        out["pooled"][lab] = {"periods": keys, "f1": pf, "m2": pm, "rho2": {"est": pm["mu"] / pf["mu"],
                                                                          "ci": [float(np.percentile(dr, 2.5)), float(np.percentile(dr, 97.5))]}}
        print(f"R3 pooled {lab} (k={len(keys)}): f1 {pf['mu']:+.3f} m2 {pm['mu']:+.3f} I2(m2) {pm['I2']:.2f} rho2 {pm['mu'] / pf['mu']:.3f}",
              flush=True)
    # timer-wake version (regime III): dose of directed items read at the wake on y_sus
    tw = {}
    for g in (51, 38):
        w = R.load_wakes((g,))
        n = w["n_dir"].to_numpy()
        X0, nm0 = R.nuisance(w)
        X = np.column_stack([X0, (n == 1), (n == 2), (n >= 3)]).astype(float)
        nm = nm0 + ["f1", "f2", "f3p"]
        y = w["y_sus"].to_numpy().astype(float)
        stats = {"f1": b_of("f1", nm), "m2": d_of("f2", "f1", nm), "m3": d_of("f3p", "f2", nm),
                 "rho2": lambda f, nm=nm: float((f["beta"][nm.index("f2")] - f["beta"][nm.index("f1")]) / f["beta"][nm.index("f1")])
                 if f["beta"][nm.index("f1")] > 0.05 else np.nan}
        f, s = boot_fit(X, y, w["agent"].to_numpy(), daycodes(w), rng, B, stats)
        tw[f"G{g:02d}"] = {"stats": s, "n_wakes": w.height, "dose_counts": {str(k): int((np.minimum(n, 3) == k).sum()) for k in range(4)}}
        print(f"R3 wake G{g:02d}: f1 {s['f1']['est']:+.3f} m2 {s['m2']['est']:+.3f} rho2 {s['rho2']['est']:.3f} {np.round(s['rho2']['ci'], 3)}",
              flush=True)
    out["timer_wake"] = tw
    return out


def run_r3_readout(B, rng) -> dict:
    """R3-P5: round-1 estimator, mentions in G51, recipients with logged (Gemini) starts only vs all."""
    import h43lib as L
    calls, states, writes, cal = L.load_real(51)
    cw = (pl.scan_parquet(R.SH / "call_windows.parquet").filter((pl.col("goal_no") == 51) & ~pl.col("holdout"))
          .group_by("agent").agg((pl.col("start_src").cast(pl.Utf8) == "logged").mean().alias("logged")).collect())
    gem = cw.filter(pl.col("logged") > 0.5)["agent"].to_list()
    out = {"gemini_agents": [int(a) for a in gem]}
    for lab, c in (("gemini", calls.filter(pl.col("agent").is_in(gem))), ("non_gemini", calls.filter(~pl.col("agent").is_in(gem)))):
        P = L.Prep(c, states, writes, cal)
        draws = L.day_draws(len(P.days), B, rng)
        res = L.analyze_class(P, "A", rng, B=B, outcomes=("O2c", "O2"), draws=draws)
        keep = {}
        for o in ("O2c", "O2"):
            oo = res["outcomes"].get(o, {})
            keep[o] = {"E1": oo.get("E1"), "batched": oo.get("batched"),
                       "bins": {k: {"n": v.get("n"), "R": v.get("R")} for k, v in oo.get("E2_bins", {}).items()}}
        out[lab] = {"n_calls": c.height, "n_second": res.get("n_second"), "n_batched": res.get("n_batched"), "outcomes": keep}
        b = keep["O2c"]["bins"].get("0-2", {})
        print(f"R3-P5 {lab}: E1 {keep['O2c']['E1']['est'] if keep['O2c']['E1'] else None} R(0-2) {b.get('R')} n {b.get('n')}", flush=True)
    return out


# =============================================================================================== R5
def r5_period(wg: pl.DataFrame, rng, B, min_n=5):
    n_rek = int((wg["D_now"] & (wg["dclass"] == 1)).sum())
    n_fr = int((wg["D_now"] & (wg["dclass"] == 0)).sum())
    base = {"n_wakes": wg.height, "n_D_fresh": n_fr, "n_D_rekick": n_rek, "n_days": int(wg["pt_date"].n_unique())}
    if n_rek < min_n or n_fr < min_n:
        return base | {"fit": False}
    X, nm = R.r5_design(wg)
    y = wg["y_sus"].to_numpy().astype(float)
    stats = {"b_fresh": b_of("D_fresh", nm), "b_re": b_of("D_rekick", nm), "b_oth": b_of("D_oth", nm),
             "d": d_of("D_rekick", "D_fresh", nm),
             "R": lambda f: float(f["beta"][nm.index("D_rekick")] / f["beta"][nm.index("D_fresh")]) if f["beta"][nm.index("D_fresh")] > 0.05 else np.nan}
    f, s = boot_fit(X, y, wg["agent"].to_numpy(), daycodes(wg), rng, B, stats)
    # post hoc (separation in small periods): N(0, 2.5^2) prior on the three directed-read terms
    rv = np.full(len(nm), 1e-6)
    for k in ("D_fresh", "D_rekick", "D_oth"):
        rv[nm.index(k)] = 1 / 2.5 ** 2
    fp, sp = boot_fit(X, y, wg["agent"].to_numpy(), daycodes(wg), rng, B, stats, ridge=rv)
    rates = {f"{c}|{int(dn)}": float(y[(wg['dclass'].to_numpy() == c) & (wg['D_now'].to_numpy() == dn)].mean())
             for c in (0, 1) for dn in (0, 1) if ((wg['dclass'].to_numpy() == c) & (wg['D_now'].to_numpy() == dn)).any()}
    return base | {"fit": True, "stats": s, "stats_pen": sp, "n_used": f["n"], "rates": rates,
                   "n_by_cell": {f"{c}|{int(dn)}": int(((wg['dclass'].to_numpy() == c) & (wg['D_now'].to_numpy() == dn)).sum()) for c in (0, 1) for dn in (0, 1)}}


def run_r5(B, rng) -> dict:
    out = {}
    for lab, strict in (("strict", True), ("loose", False)):
        w = R.add_directed_history(R.load_wakes(), strict=strict)
        per = {}
        for g in sorted(set(w["goal_no"].to_list())):
            per[f"G{g:02d}"] = r5_period(w.filter(pl.col("goal_no") == g), rng, B)
        fitted = {p: v for p, v in per.items() if v.get("fit")}
        pools = {}
        for skey in ("stats", "stats_pen"):
            pool = {}
            for k in ("b_fresh", "b_re", "d"):
                pool[k] = R.dl_pool([v[skey][k]["est"] for v in fitted.values()], [v[skey][k]["se"] for v in fitted.values()])
                pool[k]["periods"] = list(fitted)
            pf, pr = pool["b_fresh"], pool["b_re"]
            dr = rng.normal(pr["mu"], pr["se"], 20000) / rng.normal(pf["mu"], pf["se"], 20000)
            pool["R"] = {"est": pr["mu"] / pf["mu"], "ci": [float(np.percentile(dr, 2.5)), float(np.percentile(dr, 97.5))]}
            pools[skey] = pool
        pool = pools["stats"]
        out[lab] = {"periods": per, "pooled": pools["stats"], "pooled_pen": pools["stats_pen"]}
        for p, v in per.items():
            if v.get("fit"):
                s = v["stats"]
                print(f"R5 {lab} {p}: fresh {s['b_fresh']['est']:+.3f} re {s['b_re']['est']:+.3f} d {s['d']['est']:+.3f} {np.round(s['d']['ci'], 3)} "
                      f"R {s['R']['est']:.2f} {np.round(s['R']['ci'], 2)}", flush=True)
            else:
                print(f"R5 {lab} {p}: not fitted (D fresh {v['n_D_fresh']}, D re-kicked {v['n_D_rekick']})", flush=True)
        print(f"R5 {lab} pooled: d {pool['d']['mu']:+.3f} {np.round(pool['d']['ci'], 3)} I2 {pool['d']['I2']:.2f} R {pool['R']['est']:.2f}", flush=True)
        pp = pools["stats_pen"]
        print(f"R5 {lab} pooled (penalized, post hoc): d {pp['d']['mu']:+.3f} {np.round(pp['d']['ci'], 3)} I2 {pp['d']['I2']:.2f} "
              f"R {pp['R']['est']:.2f} {np.round(pp['R']['ci'], 2)} fresh {pp['b_fresh']['mu']:+.3f} re {pp['b_re']['mu']:+.3f}", flush=True)
        for p, v in per.items():
            if v.get("fit"):
                sp = v["stats_pen"]
                print(f"   pen {p}: fresh {sp['b_fresh']['est']:+.3f} re {sp['b_re']['est']:+.3f} d {sp['d']['est']:+.3f} {np.round(sp['d']['ci'], 2)} "
                      f"cells {v['n_by_cell']} rates {({k: round(x, 2) for k, x in v['rates'].items()})}", flush=True)
    return out


# =============================================================================================== R6
def r6_design(w: pl.DataFrame, step_cols: list[str]):
    X0, nm = R.nuisance(w)
    cols = [X0, w["D_now"].to_numpy()[:, None], w["N_now"].to_numpy()[:, None], w["focus"].to_numpy()[:, None],
            np.log(w["n_present"].to_numpy().clip(1, None))[:, None], w["first_of_day"].to_numpy()[:, None]]
    nm = nm + ["D_now", "N_now", "focus", "ln_present", "first_of_day"]
    for s in step_cols:
        cols.append(w[s].to_numpy()[:, None]); nm.append(s)
    return np.hstack([np.asarray(x, float) for x in cols]), nm


GROUPS = {"nudger": ["N_now"], "room": ["focus", "ln1p_peer_und", "ln_present"],
          "day_edge": ["hday_1", "hday_2", "hday_3", "hday_4", "first_of_day"],
          "trap_state": ["ln_k", "ln_age_min", "no_sus", "ln_pause"], "activity": ["swarm_act10", "D_now"]}


def agentday_rates(P, states, days):
    """Per agent-day E (sustained starts at idle-at-read calls), G (idle-at-read calls), M (idle minutes)."""
    rs3 = np.isin(P.gt, P.rs3_key) & P.idle_at_read
    df = pl.DataFrame({"agent": P.agent, "pt_date": P.pt_date, "E": rs3.astype(np.int64), "G": P.idle_at_read.astype(np.int64)})
    df = df.group_by("agent", "pt_date").agg(pl.col("E").sum(), pl.col("G").sum())
    idle = (states.filter(pl.col("present") & pl.col("in_span") & (pl.col("lump4_min") == 2))
            .group_by("pt_date", "agent").len().rename({"len": "M"}).with_columns(pl.col("agent").cast(pl.Int64)))
    df = df.with_columns(pl.col("agent").cast(pl.Int64)).join(idle, on=["pt_date", "agent"], how="full", coalesce=True).fill_null(0)
    return df.filter(pl.col("pt_date").is_in(days))


def mech_split(df_pre, df_post):
    E0, G0, M0 = (df_pre[c].sum() for c in ("E", "G", "M"))
    E1, G1, M1 = (df_post[c].sum() for c in ("E", "G", "M"))
    return {"dlnR": np.log((E1 / M1) / (E0 / M0)), "dlnp": np.log((E1 / G1) / (E0 / G0)), "dlnGM": np.log((G1 / M1) / (G0 / M0)),
            "rel_change": (E1 / M1) / (E0 / M0) - 1, "R_pre": E0 / M0, "R_post": E1 / M1}


def shift_share(df_pre, df_post, min_days=3):
    a0 = df_pre.group_by("agent").agg(pl.col("E").sum(), pl.col("M").sum(), (pl.col("M") > 0).sum().alias("nd"))
    a1 = df_post.group_by("agent").agg(pl.col("E").sum(), pl.col("M").sum(), (pl.col("M") > 0).sum().alias("nd"))
    M0, M1 = a0["M"].sum(), a1["M"].sum()
    R0, R1 = a0["E"].sum() / M0, a1["E"].sum() / M1
    j = a0.join(a1, on="agent", how="full", suffix="_1", coalesce=True).fill_null(0)
    inc = j.filter((pl.col("nd") >= min_days) & (pl.col("nd_1") >= min_days) & (pl.col("M") > 0) & (pl.col("M_1") > 0))
    w0 = inc["M"].to_numpy() / M0
    w1 = inc["M_1"].to_numpy() / M1
    r0 = inc["E"].to_numpy() / inc["M"].to_numpy()
    r1 = inc["E_1"].to_numpy() / inc["M_1"].to_numpy()
    within = float(np.sum((w0 + w1) / 2 * (r1 - r0)))
    reweight = float(np.sum((r0 + r1) / 2 * (w1 - w0)))
    rest = (R1 - R0) - within - reweight          # newcomers, leavers and part-timers
    newcomers = j.filter((pl.col("nd") == 0) & (pl.col("nd_1") > 0))["agent"].to_list()
    return {"dR": R1 - R0, "within": within, "reweight": reweight, "newcomers_leavers": rest, "n_incumbents": inc.height,
            "newcomers": [int(a) for a in newcomers], "share_within": within / (R1 - R0), "share_reweight": reweight / (R1 - R0),
            "share_newcomers_leavers": rest / (R1 - R0)}


def oaxaca(w: pl.DataFrame, rng, B, incumbents: list | None = None) -> dict:
    if incumbents is not None:
        w = w.filter(pl.col("agent").is_in(incumbents))
    post = w["post"].to_numpy()
    X, nm = r6_design(w, ["post"])
    y = w["y_sus"].to_numpy().astype(float)
    ag = w["agent"].to_numpy()

    def comp(Xb, yb, agb, postb):
        f = R.fe_logit(Xb, yb, agb)
        keep = f["keep"]
        Xk, pk = Xb[keep], postb[keep]
        mu = f["mu"]
        dens = float(np.mean(mu * (1 - mu)))
        dx = Xk[pk].mean(0) - Xk[~pk].mean(0)
        res = {"obs_dp": float(yb[postb].mean() - yb[~postb].mean()), "dens": dens}
        for gname, cols in GROUPS.items():
            res[gname] = float(dens * sum(f["beta"][nm.index(c)] * dx[nm.index(c)] for c in cols))
        res["step_logit"] = float(f["beta"][nm.index("post")])
        eta_post = (Xk[pk] @ f["beta"]) + f["alpha"][f["gi"][pk]]
        res["step"] = float(np.mean(R._sig(eta_post) - R._sig(eta_post - f["beta"][nm.index("post")])))
        al = f["alpha"][f["gi"]]
        res["composition"] = float(dens * (al[pk].mean() - al[~pk].mean()))
        res["residual"] = res["obs_dp"] - sum(res[g] for g in GROUPS) - res["step"] - res["composition"]
        return res

    pt = comp(X, y, ag, post)
    pre_rows = np.flatnonzero(~post)
    post_rows = np.flatnonzero(post)
    d_pre, d_post = daycodes(w.filter(pl.Series(~post))), daycodes(w.filter(pl.Series(post)))
    rb0, rb1 = R.rows_by_day(d_pre), R.rows_by_day(d_post)
    dr = []
    for _ in range(B):
        i0 = np.concatenate([pre_rows[rb0[i]] for i in rng.integers(0, len(rb0), len(rb0))])
        i1 = np.concatenate([post_rows[rb1[i]] for i in rng.integers(0, len(rb1), len(rb1))])
        idx = np.r_[i0, i1]
        dr.append(comp(X[idx], y[idx], ag[idx], post[idx]))
    out = {}
    for k in pt:
        out[k] = R.summarize(pt[k], [d[k] for d in dr])
        if k not in ("obs_dp", "dens", "step_logit"):
            out[k]["share_of_obs"] = pt[k] / pt["obs_dp"] if pt["obs_dp"] else None
    out["n_wakes"] = w.height
    return out


def run_r6(B, rng) -> dict:
    import h43lib as L
    out = {}
    # ---- accountings 1 and 2: round-1 statistic (calls.parquet, states_min), G51 all non-reserved days
    calls, states, writes, cal = L.load_real(51)
    P = L.Prep(calls, states, writes, cal)
    days = P.days
    pre = [d for d in days if R.PRE_WIN[0] <= d < R.PRE_WIN[1]]
    post = [d for d in days if R.POST_WIN[0] <= d < R.POST_WIN[1]]
    ad = agentday_rates(P, states, days)
    dpre, dpost = ad.filter(pl.col("pt_date").is_in(pre)), ad.filter(pl.col("pt_date").is_in(post))
    ms = mech_split(dpre, dpost)
    ss = shift_share(dpre, dpost)
    dr_ms, dr_ss = [], []
    for _ in range(B):
        p0 = [pre[i] for i in rng.integers(0, len(pre), len(pre))]
        p1 = [post[i] for i in rng.integers(0, len(post), len(post))]
        b0 = pl.concat([dpre.filter(pl.col("pt_date") == d) for d in p0])
        b1 = pl.concat([dpost.filter(pl.col("pt_date") == d) for d in p1])
        dr_ms.append(mech_split(b0, b1))
        dr_ss.append(shift_share(b0, b1))
    out["mechanical"] = {k: R.summarize(v, [d[k] for d in dr_ms]) for k, v in ms.items()}
    out["mechanical"]["share_p"] = ms["dlnp"] / ms["dlnR"]
    out["mechanical"]["share_cadence"] = ms["dlnGM"] / ms["dlnR"]
    out["shift_share"] = {k: (R.summarize(v, [d[k] for d in dr_ss]) if isinstance(v, float) else v) for k, v in ss.items()}
    print(f"R6 mech: dlnR {ms['dlnR']:+.3f} dlnp {ms['dlnp']:+.3f} dlnGM {ms['dlnGM']:+.3f} (rel {ms['rel_change']:+.3f})", flush=True)
    print(f"R6 shift-share: dR {ss['dR']:+.4f} within {ss['within']:+.4f} reweight {ss['reweight']:+.4f} new/leave {ss['newcomers_leavers']:+.4f}",
          flush=True)
    # ---- date profile of the raw rate by segment (per-day rates)
    seg = {"S1_0821": ("2026-08-21", "2026-08-22"), "S2_0824_0827": ("2026-08-24", "2026-08-28"),
           "S3_0828_0902": ("2026-08-28", "2026-09-03"), "S4_0903_0904": ("2026-09-03", "2026-09-05")}
    R0 = dpre["E"].sum() / dpre["M"].sum()
    G0 = dpre["G"].sum() / dpre["M"].sum()
    p0 = dpre["E"].sum() / dpre["G"].sum()
    prof = {}
    inc = ss["n_incumbents"]
    for k, (a, b) in seg.items():
        s_ = ad.filter((pl.col("pt_date") >= a) & (pl.col("pt_date") < b))
        prof[k] = {"rel_R": float(s_["E"].sum() / s_["M"].sum() / R0 - 1), "rel_p": float(s_["E"].sum() / s_["G"].sum() / p0 - 1),
                   "rel_cadence": float(s_["G"].sum() / s_["M"].sum() / G0 - 1), "days": sorted(set(s_["pt_date"].to_list()))}
    out["segments_raw"] = prof
    print("R6 segments raw:", {k: round(v["rel_R"], 3) for k, v in prof.items()}, flush=True)
    # ---- bookend step (08-05), raw statistic, 11 vs 11 days, with placebo band over all 11|11 splits before 08-21
    allpre = [d for d in days if d < R.NE43]
    per_day = ad.group_by("pt_date").agg(pl.col("E").sum(), pl.col("M").sum()).sort("pt_date")
    pdm = {r["pt_date"]: (r["E"], r["M"]) for r in per_day.iter_rows(named=True)}

    def split_change(i, k=11, src=allpre):
        a_, b_ = src[i - k:i], src[i:i + k]
        e0, m0 = sum(pdm[d][0] for d in a_), sum(pdm[d][1] for d in a_)
        e1, m1 = sum(pdm[d][0] for d in b_), sum(pdm[d][1] for d in b_)
        return (e1 / m1) / (e0 / m0) - 1
    i05 = allpre.index(next(d for d in allpre if d >= "2026-08-05"))
    plac = [split_change(i) for i in range(11, len(allpre) - 11 + 1) if i != i05]
    out["bookend_step"] = {"split_day": allpre[i05], "rel_change": split_change(i05), "placebo_band": [float(np.percentile(plac, 2.5)),
                           float(np.percentile(plac, 97.5))], "n_placebo": len(plac), "placebo_all": plac}
    print(f"R6 bookend step {allpre[i05]}: {split_change(i05):+.3f} band {np.round(out['bookend_step']['placebo_band'], 3)}", flush=True)
    # ---- accounting 3 and 4: wake model (agent FE), joint over both windows
    w = R.load_wakes((51,), date_from=R.PRE_WIN[0], date_to=R.POST_WIN[1]).with_columns((pl.col("pt_date") >= R.NE43).alias("post"))
    out["oaxaca_all"] = oaxaca(w, rng, B)
    incs = [a for a in out["shift_share"]["newcomers"]]
    ag_pre = set(w.filter(~pl.col("post"))["agent"].to_list())
    incumbents = [a for a in set(w.filter(pl.col("post"))["agent"].to_list()) if a in ag_pre]
    out["oaxaca_incumbents"] = oaxaca(w, rng, B, incumbents=incumbents)
    o = out["oaxaca_all"]
    print("R6 oaxaca all: obs dp {:+.4f}; ".format(o["obs_dp"]["est"]) + " ".join(
        f"{k} {o[k]['est']:+.4f}" for k in list(GROUPS) + ["step", "composition", "residual"]), flush=True)
    # segment steps on wakes (agent FE)
    w2 = w.with_columns([((pl.col("pt_date") >= a) & (pl.col("pt_date") < b)).alias(k) for k, (a, b) in seg.items()])
    X, nm = r6_design(w2, list(seg))
    stats = {k: b_of(k, nm) for k in seg}
    f, s = boot_fit(X, w2["y_sus"].to_numpy().astype(float), w2["agent"].to_numpy(), daycodes(w2), rng, B, stats)
    out["segments_wake_logit"] = s
    print("R6 segment steps (logit):", {k: round(v["est"], 3) for k, v in s.items()}, flush=True)
    # placebo for the single step: 11|11 day splits before 08-21, same wake model
    wall = R.load_wakes((51,), date_to=R.NE43)
    dd = sorted(set(wall["pt_date"].to_list()))
    steps = []
    for i in range(11, len(dd) - 11 + 1):
        a_, b_ = dd[i - 11], dd[i + 10]
        wi = wall.filter((pl.col("pt_date") >= a_) & (pl.col("pt_date") <= b_)).with_columns((pl.col("pt_date") >= dd[i]).alias("post"))
        Xi, nmi = r6_design(wi, ["post"])
        fi = R.fe_logit(Xi, wi["y_sus"].to_numpy().astype(float), wi["agent"].to_numpy())
        steps.append({"split": dd[i], "step": float(fi["beta"][nmi.index("post")])})
    out["step_placebo"] = {"band": [float(np.percentile([s_["step"] for s_ in steps], 2.5)), float(np.percentile([s_["step"] for s_ in steps], 97.5))],
                           "all": steps}
    print(f"R6 step placebo band (logit): {np.round(out['step_placebo']['band'], 3)}; observed step {o['step_logit']['est']:+.3f}", flush=True)
    # cadence by segment with agent FE (OLS on per agent-day ln(G/M), weights M)
    a2 = ad.filter((pl.col("M") >= 10) & (pl.col("G") > 0) & (pl.col("pt_date") >= R.PRE_WIN[0]) & (pl.col("pt_date") < R.POST_WIN[1]))
    yv = np.log(a2["G"].to_numpy() / a2["M"].to_numpy())
    agv = a2["agent"].to_numpy()
    lev = np.unique(agv)
    Xc = np.column_stack([np.ones(len(yv))] + [((a2["pt_date"] >= a) & (a2["pt_date"] < b)).to_numpy().astype(float) for a, b in seg.values()]
                         + [(agv == x).astype(float) for x in lev[1:]])
    wts = a2["M"].to_numpy().astype(float)
    beta = np.linalg.lstsq(Xc * np.sqrt(wts)[:, None], yv * np.sqrt(wts), rcond=None)[0]
    out["segments_cadence_lnGM_agentFE"] = dict(zip(seg, beta[1:5].tolist()))
    print("R6 cadence segments (ln G/M, agent FE):", {k: round(v, 3) for k, v in out["segments_cadence_lnGM_agentFE"].items()}, flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=["r2", "r3", "r3p5", "r5", "r6"], required=True)
    ap.add_argument("--B", type=int, default=B_DEF)
    a = ap.parse_args()
    rng = np.random.default_rng(R.SEED + {"r2": 12, "r3": 13, "r3p5": 15, "r5": 25, "r6": 26}[a.only])
    t0 = time.time()
    fn = {"r2": run_r2, "r3": run_r3, "r3p5": run_r3_readout, "r5": run_r5, "r6": run_r6}[a.only]
    res = fn(a.B, rng)
    res["B"] = a.B
    res["secs"] = round(time.time() - t0, 1)
    res["built_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    import subprocess
    res["git_commit"] = subprocess.run(["git", "-C", str(R.ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    R.jdump(res, R.OUT / f"results_{a.only}.json")
    print(f"done {a.only} in {res['secs']} s")


if __name__ == "__main__":
    main()
