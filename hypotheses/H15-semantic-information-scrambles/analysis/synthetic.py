"""H15 synthetic validation (axis F), run before any real-data outcome.

Toy agents with known load-bearing information are simulated on the REAL village skeleton: which agents are present
on which non-holdout days, the unit (goal-period) boundaries, and the real positions and doses of the catalogued
scramble events (ML, MN, CC). Only the outcome V is synthetic.

Generator (agent a, day d of its unit sequence):
  V = alpha_a + gamma_d + h_ad + eps_ad + scramble effects
  h: AR(1) latent "health" (rho_h, stationary sd 0.6); eps: day noise (sd 0.7); gamma: shared day field (sd 0.5).
  ML (memory loss, dose delta): deficit -c * g(delta) * (1 - lam)^(k-1) on post day k >= 1 (load-bearing info is
     rebuilt at rate lam); g = hockey stick max(0, delta - delta*)/(1 - delta*) or linear delta.
  MN (newcomer, delta = 1): deficit -c_new * (1 - lam_new)^(k-1) from tenure day 1, plus optional novelty boost.
  CC (chat cut): effect c_chat on cut days (negative value of information if c_chat > 0).
  Selection (main pitfall): event days re-drawn within the agent's unit with P ∝ exp(-beta * h_{d-1})
     ("resets happen when the agent is already failing"); or a transient unobserved slump around the event.

Turn-level context erasure (CF/CV): agent-days of turns with write probability p; a forced consolidation every 41
turns unless the agent consolidates voluntarily first, with a voluntary hazard that jumps right after a write
(task completion); after a consolidation the write probability drops by Delta for 10 turns
(Delta_CF > Delta_CV; Delta_CF shrinks with the stored-transfer dose).

Outputs: data/processed/H15-semantic-information-scrambles/synthetic.json, figures/F1_synthetic.pdf
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h15lib import (METHODS, Panel, autocov_params, dl_meta, event_delta, agent_mu, hockey_vs_linear,  # noqa: E402
                    period_test, placebo_deltas, residual_panel, spearman, cluster_boot_diff, unit_placebo_pool)
from h15common import FIG, OUT, SEED, write_provenance  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

T0 = time.time()
R = int(sys.argv[sys.argv.index("--reps") + 1]) if "--reps" in sys.argv else 150


def log(m):
    print(f"[{time.time() - T0:6.1f}s] {m}", flush=True)


ad = pl.read_parquet(OUT / "agent_day.parquet")
cat = pl.read_parquet(OUT / "scramble_catalog.parquet")
skel = ad.select("pt_date", "agent", "unit", "regime", "tenure_d").sort("unit", "pt_date")
unit_days = {u: sorted(g["pt_date"].unique().to_list()) for (u,), g in skel.group_by(["unit"])}
units = sorted(unit_days)
regime_of = {u: skel.filter(pl.col("unit") == u)["regime"][0] for u in units}
pres = {(int(a), u): set(g["pt_date"].to_list()) for (a, u), g in skel.group_by(["agent", "unit"])}
EV = {t: cat.filter(pl.col("type") == t).select("agent", "pt_date", "unit", "dose", "run_len").rows(named=True)
      for t in ("ML", "MN", "CC")}
# the agent's own sequence across units (for MN), in time order
agent_seq = {int(a): g.sort("pt_date")[["pt_date", "unit"]].rows() for (a,), g in skel.group_by(["agent"])}


def simulate(rng, rho_h=0.6, c_ml=0.0, lam=0.5, dstar=None, beta=0.0, slump=0.0, c_new=0.0, lam_new=0.4,
             novelty=0.0, c_cc=0.0):
    """Returns the synthetic agent_day frame (columns pt_date, agent, unit, regime, V) and the event lists used."""
    alpha = {a: rng.normal(0, 0.5) for a in agent_seq}
    gamma = {d: rng.normal(0, 0.5) for u in units for d in unit_days[u]}
    sd_h = 0.6
    vals = {}
    hval = {}
    for (a, u), ds in pres.items():
        days = unit_days[u]
        h = np.zeros(len(days))
        h[0] = rng.normal(0, sd_h)
        for i in range(1, len(days)):
            h[i] = rho_h * h[i - 1] + rng.normal(0, sd_h * np.sqrt(1 - rho_h ** 2))
        hval[(a, u)] = h
        for i, d in enumerate(days):
            if d in ds:
                vals[(a, d)] = alpha[a] + gamma[d] + h[i] + rng.normal(0, 0.7)
    # ML: real positions, or re-drawn under selection
    ml = []
    for e in EV["ML"]:
        a, u, d = int(e["agent"]), e["unit"], e["pt_date"]
        days = unit_days[u]
        if beta > 0:
            cand = [i for i in range(1, len(days)) if days[i] in pres[(a, u)]]
            w = np.exp(-beta * hval[(a, u)][[i - 1 for i in cand]] / sd_h)
            i0 = int(rng.choice(cand, p=w / w.sum()))
            d = days[i0]
        ml.append({"agent": a, "unit": u, "pt_date": d, "dose": e["dose"]})
    for e in ml:
        a, u, d = e["agent"], e["unit"], e["pt_date"]
        days = unit_days[u]
        i0 = days.index(d)
        g = (max(0.0, e["dose"] - dstar) / (1 - dstar)) if dstar is not None else e["dose"]
        for k in range(1, len(days) - i0):
            dd = days[i0 + k]
            if (a, dd) in vals:
                vals[(a, dd)] += -c_ml * g * (1 - lam) ** (k - 1)
        if slump:
            for k in range(-2, 3):
                if 0 <= i0 + k < len(days) and (a, days[i0 + k]) in vals:
                    vals[(a, days[i0 + k])] -= slump
    # MN: tenure-day deficit along the agent's own sequence
    for e in EV["MN"]:
        a = int(e["agent"])
        seq = [d for d, _ in agent_seq[a] if d >= e["pt_date"]]
        for k, d in enumerate(seq[:15]):
            vals[(a, d)] += -c_new * (1 - lam_new) ** k + (novelty if k < 3 else 0.0)
    # CC: cut days (<= run_len)
    for e in EV["CC"]:
        a, u = int(e["agent"]), e["unit"]
        days = unit_days[u]
        i0 = days.index(e["pt_date"])
        for k in range(min(int(e["run_len"]), len(days) - i0)):
            if (a, days[i0 + k]) in vals:
                vals[(a, days[i0 + k])] += c_cc
    df = (skel.with_columns(pl.Series("V", [vals.get((int(a), d), np.nan) for a, d in
                                            zip(skel["agent"].to_list(), skel["pt_date"].to_list())])))
    return df, ml


def estimate_events(df, events, kind, post_offsets_fn, methods=METHODS, rng=None, pool="unit"):
    """Per-unit period tests + DL meta for each method. Returns dict method -> meta, plus per-event table."""
    rp = residual_panel(df, "V")
    panel = Panel(rp, unit_days)
    by_agent_unit = {}
    for e in events:
        by_agent_unit.setdefault((int(e["agent"]), e["unit"]), []).append(unit_days[e["unit"]].index(e["pt_date"]))
    prm = {}
    for reg in ("I", "II", "III"):
        us = [u for u in units if regime_of[u] == reg]
        if us:
            prm[reg] = autocov_params(panel, us, exclude=by_agent_unit)
    rows = []
    cache = {}
    for e in events:
        a, u = int(e["agent"]), e["unit"]
        x = panel.get(a, u)
        if x is None:
            continue
        i0 = unit_days[u].index(e["pt_date"])
        evs = by_agent_unit[(a, u)]
        offs = post_offsets_fn(e)
        mu = agent_mu(x, evs)
        p = prm[regime_of[u]]
        r = event_delta(x, i0, offs, mu, p)
        if r is None:
            continue
        if pool == "unit":
            null = unit_placebo_pool(panel, u, by_agent_unit, offs, p, cache)
        else:
            null = placebo_deltas(x, evs, offs, p)
        rows.append({"unit": u, "agent": a, **r, "null": null, "dose": e.get("dose")})
    out = {}
    for m in list(methods) + ["pretrend"]:
        per_unit = {}
        for u in sorted({r["unit"] for r in rows}):
            rr = [r for r in rows if r["unit"] == u]
            t = period_test([r[m] for r in rr], [[n[m] for n in r["null"]] for r in rr], ndraw=600, rng=rng)
            if t:
                per_unit[u] = t
        meta = dl_meta([t["effect"] for t in per_unit.values()], [t["null_sd"] for t in per_unit.values()])
        out[m] = {"meta": meta, "units": per_unit}
    return out, rows


def mn_estimate(df, rng):
    """Newcomer deficit: mean u over tenure active days 1-3 minus days 6-12; placebo = incumbents at pseudo-joins."""
    rp = residual_panel(df, "V")
    useq = {}
    for (a,), g in rp.sort("pt_date").group_by(["agent"]):
        useq[int(a)] = dict(zip(g["pt_date"].to_list(), g["u"].to_list()))
    per_unit = {}
    newcomers = {int(e["agent"]) for e in EV["MN"]}
    for e in EV["MN"]:
        a = int(e["agent"])
        seq = [d for d, _ in agent_seq[a] if d >= e["pt_date"]]
        xs = np.array([useq.get(a, {}).get(d, np.nan) for d in seq[:12]], float)
        if np.isfinite(xs[:3]).sum() < 1 or np.isfinite(xs[5:12]).sum() < 3:
            continue
        val = np.nanmean(xs[:3]) - np.nanmean(xs[5:12])
        null = []
        udays = unit_days[e["unit"]]
        for b, s in useq.items():
            if b in newcomers or b == a:
                continue
            bseq = [d for d, _ in agent_seq[b]]
            for d0 in udays:
                if d0 not in bseq:
                    continue
                j = bseq.index(d0)
                ys = np.array([s.get(d, np.nan) for d in bseq[j:j + 12]], float)
                if len(ys) == 12 and np.isfinite(ys[:3]).sum() >= 1 and np.isfinite(ys[5:12]).sum() >= 3:
                    null.append(np.nanmean(ys[:3]) - np.nanmean(ys[5:12]))
        per_unit.setdefault(e["unit"], []).append((val, null))
    tests = {}
    for u, lst in per_unit.items():
        t = period_test([v for v, _ in lst], [n for _, n in lst], ndraw=600, rng=rng)
        if t:
            tests[u] = t
    return dl_meta([t["effect"] for t in tests.values()], [t["null_sd"] for t in tests.values()]), tests


def summarize(metas, truth):
    """metas: list over reps of meta dicts. Returns bias, rmse, coverage, rejection rates."""
    mus = np.array([m["mu"] if m else np.nan for m in metas])
    los = np.array([m["lo"] if m else np.nan for m in metas])
    his = np.array([m["hi"] if m else np.nan for m in metas])
    zs = np.array([m["z"] if m else np.nan for m in metas])
    ok = np.isfinite(mus)
    return {"truth": truth, "mean_est": float(np.nanmean(mus)), "bias": float(np.nanmean(mus) - truth),
            "rmse": float(np.sqrt(np.nanmean((mus - truth) ** 2))),
            "coverage": float(np.mean((los[ok] <= truth) & (his[ok] >= truth))),
            "reject_neg": float(np.mean(zs[ok] <= -2)), "reject_two_sided": float(np.mean(np.abs(zs[ok]) >= 2)),
            "n_reps": int(ok.sum())}


SCALE = 1.0
ML_POST = lambda e: [1, 2]  # noqa: E731
CC_POST = lambda e: list(range(0, min(int(e["run_len"]), 5)))  # noqa: E731


def true_ml_effect(c_ml, lam, dstar):
    """Mean deficit over post days 1-2 averaged over the real ML doses."""
    ds = np.array([e["dose"] for e in EV["ML"]])
    g = np.maximum(0, ds - dstar) / (1 - dstar) if dstar is not None else ds
    return float(-c_ml * np.mean(g) * (1 + (1 - lam)) / 2)


def run_ml_scenarios(rng):
    res = {}
    scen = {
        "null_rho0.6": dict(rho_h=0.6),
        "effect_rho0.6": dict(rho_h=0.6, c_ml=1.0),
        "select_beta1.5_rho0.6": dict(rho_h=0.6, beta=1.5),
        "select_beta1.5_rho0.6_effect": dict(rho_h=0.6, beta=1.5, c_ml=1.0),
        "select_beta1.5_rho0.3": dict(rho_h=0.3, beta=1.5),
        "slump0.5_rho0.6": dict(rho_h=0.6, slump=0.5),
        "effect_small_rho0.6": dict(rho_h=0.6, c_ml=0.5),
    }
    for name, kw in scen.items():
        metas = {m: [] for m in list(METHODS) + ["pretrend"]}
        per_event = {m: [] for m in METHODS}
        for r in range(R):
            df, ml = simulate(rng, **kw)
            out, rows = estimate_events(df, ml, "ML", ML_POST, rng=rng)
            for m in metas:
                metas[m].append(out[m]["meta"])
            for m in METHODS:
                per_event[m] += [row[m] for row in rows]
        truth = true_ml_effect(kw.get("c_ml", 0.0), kw.get("lam", 0.5), kw.get("dstar"))
        # estimates are in units of the unit's residual SD of u_raw; truth is converted with SCALE
        res[name] = {"kw": kw, "truth_rawV": truth, "truth_u": truth / SCALE,
                     **{m: summarize(metas[m], truth / SCALE if m != "pretrend" else 0.0) for m in metas}}
        log(f"ML {name}: " + ", ".join(f"{m} {res[name][m]['mean_est']:+.3f} rej- {res[name][m]['reject_neg']:.2f}"
                                       for m in METHODS))
    return res


def calibrate_scale(rng, n=20):
    """SD of u_raw in raw V units (so true effects in V units map to u units)."""
    sds = []
    for _ in range(n):
        df, _ = simulate(rng, rho_h=0.6)
        d = df.filter(pl.col("V").is_finite())
        d = d.with_columns(pl.col("V").sum().over("pt_date").alias("_s"), pl.len().over("pt_date").alias("_n"))
        d = d.filter(pl.col("_n") >= 3).with_columns(
            (pl.col("V") - (pl.col("_s") - pl.col("V")) / (pl.col("_n") - 1)).alias("ur"))
        sds.append(float(d.group_by("unit").agg(pl.col("ur").std())["ur"].mean()))
    return float(np.mean(sds))


def run_dose(rng, n_rep=R):
    """Power of AIC (hockey vs linear) and recovery of delta* with the real ML doses (truncated at 0.5)."""
    out = {}
    for name, dstar in (("hockey_dstar0.6", 0.6), ("linear", None)):
        prefs, dst, slopes = [], [], []
        for _ in range(n_rep):
            df, ml = simulate(rng, rho_h=0.6, c_ml=1.5, dstar=dstar)
            _, rows = estimate_events(df, ml, "ML", ML_POST, methods=("kal",), rng=rng)
            hv = hockey_vs_linear(np.array([r["dose"] for r in rows]), np.array([r["kal"] for r in rows]))
            if hv and "dAIC_lin_minus_hockey" in hv:
                prefs.append(hv["dAIC_lin_minus_hockey"] >= 2)
                dst.append(hv["dstar"])
                slopes.append(hv["slope_lin"])
        out[name] = {"p_hockey_preferred": float(np.mean(prefs)), "dstar_median": float(np.median(dst)),
                     "dstar_iqr": [float(np.percentile(dst, 25)), float(np.percentile(dst, 75))],
                     "p_slope_negative": float(np.mean(np.array(slopes) < 0)), "n": len(prefs)}
        log(f"dose {name}: {out[name]}")
    return out


def run_mn(rng):
    out = {}
    for name, kw in (("null", {}), ("deficit0.6", {"c_new": 0.6}), ("deficit0.6_novelty0.4", {"c_new": 0.6, "novelty": 0.4})):
        metas = []
        for _ in range(R):
            df, _ = simulate(rng, rho_h=0.6, **kw)
            m, _ = mn_estimate(df, rng)
            metas.append(m)
        truth = -kw.get("c_new", 0) * np.mean([(1 - 0.4) ** k for k in range(3)]) + kw.get("novelty", 0) \
            + kw.get("c_new", 0) * np.mean([(1 - 0.4) ** k for k in range(5, 12)])
        out[name] = {"kw": kw, "truth_rawV": float(truth), "truth_u": float(truth / SCALE),
                     **summarize(metas, truth / SCALE)}
        log(f"MN {name}: est {out[name]['mean_est']:+.3f} rej- {out[name]['reject_neg']:.2f} truth(V) {truth:+.3f}")
    return out


def run_cc(rng):
    out = {}
    for name, kw in (("null", {}), ("cost0.5", {"c_cc": -0.5}), ("negvalue0.5", {"c_cc": 0.5})):
        metas = {m: [] for m in METHODS}
        for _ in range(R):
            df, _ = simulate(rng, rho_h=0.6, **kw)
            o, _ = estimate_events(df, EV["CC"], "CC", CC_POST, rng=rng)
            for m in METHODS:
                metas[m].append(o[m]["meta"])
        truth = kw.get("c_cc", 0.0)
        out[name] = {"kw": kw, "truth_rawV": truth, "truth_u": truth / SCALE,
                     **{m: summarize(metas[m], truth / SCALE) for m in METHODS}}
        log(f"CC {name}: " + ", ".join(f"{m} {out[name][m]['mean_est']:+.3f} rej2 {out[name][m]['reject_two_sided']:.2f}"
                                       for m in METHODS))
    return out


def run_turns(rng, n_agentdays=1500):
    """Context erasure at consolidation; voluntary consolidations are selected right after a write."""
    out = {}
    for name, (dcf, dcv, theta) in {"null": (0.0, 0.0, 0.0), "cf_cost": (0.5, 0.1, 0.0),
                                    "cf_cost_dose": (0.5, 0.1, 0.8)}.items():
        recs = []
        for ad_i in range(n_agentdays):
            p = rng.uniform(0.02, 0.08)
            T = 400
            w = np.zeros(T, int)
            seg_start, last_cons, kind, sdose = 0, -999, None, 0.0
            info = []
            pen_until, pen = -1, 0.0
            t = 0
            seg_len = 0
            while t < T:
                pw = p * (1 - pen) if t < pen_until else p
                w[t] = rng.random() < pw
                seg_len += 1
                vol_h = 0.01 + (0.15 if (w[t] or (t > 0 and w[t - 1])) else 0.0)
                if seg_len >= 41 or (seg_len >= 10 and rng.random() < vol_h):
                    k = "CF" if seg_len >= 41 else "CV"
                    sdose = rng.uniform(0, 1)
                    d = dcf * (1 - theta * sdose) if k == "CF" else dcv
                    info.append((t + 1, k, sdose, seg_len))
                    pen_until, pen = t + 11, d
                    seg_len = 0
                t += 1
            base = w.mean()
            for (t0, k, sd, sl) in info:
                if t0 - 10 < 0 or t0 + 10 > T:
                    continue
                recs.append((ad_i, k, w[t0 - 10:t0].mean(), w[t0:t0 + 10].mean(), base, sd, p))
        a = np.array([(r[0], r[2], r[3], r[4], r[5], r[6]) for r in recs], float)
        kinds = np.array([r[1] for r in recs])
        dip_pre = a[:, 2] - a[:, 1]
        dip_base = a[:, 2] - a[:, 3]
        cf, cv = kinds == "CF", kinds == "CV"
        res = {}
        for lab, dip in (("pre", dip_pre), ("base", dip_base)):
            b = cluster_boot_diff(dip[cf], a[cf, 0], dip[cv], a[cv, 0], nboot=200, rng=rng)
            res[lab] = b
        # truth in write-rate units: -p*(dcf*(1-theta*E[dose]) - dcv) averaged
        pm = a[:, 5].mean()
        res["truth"] = float(-pm * (dcf * (1 - theta * 0.5) - dcv))
        rho, n = spearman(a[cf, 4], dip_base[cf])
        res["spearman_dose_dip_CF"] = rho
        res["n_CF"], res["n_CV"] = int(cf.sum()), int(cv.sum())
        out[name] = res
        log(f"turns {name}: pre {res['pre']['est']:+.4f} base {res['base']['est']:+.4f} truth {res['truth']:+.4f} "
            f"rho {rho:+.3f}")
    return out


if __name__ == "__main__":
    rng = np.random.default_rng(SEED)
    SCALE = calibrate_scale(rng)
    log(f"u_raw SD (V units) = {SCALE:.3f}; R = {R}")
    results = {"reps": R, "u_scale_V": SCALE, "n_events": {k: len(v) for k, v in EV.items()}}
    results["turns"] = run_turns(rng)
    results["ML"] = run_ml_scenarios(rng)
    results["MN"] = run_mn(rng)
    results["CC"] = run_cc(rng)
    results["dose"] = run_dose(rng, n_rep=max(60, R // 2))
    # primary-counterfactual rule (fixed in the card before this run)
    sel = results["ML"]["select_beta1.5_rho0.6"]
    nul = results["ML"]["null_rho0.6"]
    elig = [m for m in METHODS if nul[m]["coverage"] >= 0.90]
    best = min(elig or METHODS, key=lambda m: (abs(sel[m]["bias"]), m != "ar1"))
    results["primary_counterfactual"] = {"chosen": best, "eligible": elig,
                                         "abs_bias_under_selection": {m: abs(sel[m]["bias"]) for m in METHODS},
                                         "null_coverage": {m: nul[m]["coverage"] for m in METHODS}}
    tb = results["turns"]["cf_cost"]
    results["primary_turn_contrast"] = {"chosen": min(("base", "pre"),
                                                      key=lambda k: abs(tb[k]["est"] - tb["truth"])),
                                        "bias": {k: tb[k]["est"] - tb["truth"] for k in ("pre", "base")}}
    log(f"primary counterfactual: {results['primary_counterfactual']}")
    log(f"primary turn contrast: {results['primary_turn_contrast']}")
    (OUT / "synthetic.json").write_text(json.dumps(results, indent=1, default=float))
    write_provenance("synthetic", ["H15 agent_day (skeleton only)", "scramble_catalog (positions, doses)"],
                     {"reps": R, "seed": SEED}, built_by="hypotheses/H15-semantic-information-scrambles/analysis/synthetic.py")
    log("wrote synthetic.json")
