"""H15 real-data run (non-holdout only), per unit (goal period), then cross-period meta-analysis.

Reads agent_day, scramble_catalog, consolidations (scheme/build.py), v_choice.json (choose_v.py) and synthetic.json
(primary counterfactual and turn contrast). Writes results.json and per-unit JSONs in G<NN>/ data folders.

Estimators (h15lib): same-day-differenced residual u; counterfactuals kal / ar1 / did; naive = did on undifferenced
z(V); unit-pooled placebo null (amendment A1) with the same-agent-only null as a robustness column.
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h15lib import (METHODS, Panel, agent_mu, autocov_params, cluster_boot_diff, dl_meta, event_delta,  # noqa: E402
                    hockey_vs_linear, period_test, placebo_deltas, residual_panel, spearman, unit_placebo_pool)
from h15common import OUT, SEED, SH, V_CANDIDATES, calendar_nonholdout, refuse_holdout, write_provenance  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

T0 = time.time()
rng = np.random.default_rng(SEED)


def log(m):
    print(f"[{time.time() - T0:6.1f}s] {m}", flush=True)


ad = pl.read_parquet(OUT / "agent_day.parquet")
cat = pl.read_parquet(OUT / "scramble_catalog.parquet")
ce = pl.read_parquet(OUT / "consolidations.parquet")
vch = json.loads((OUT / "v_choice.json").read_text())
syn = json.loads((OUT / "synthetic.json").read_text())
refuse_holdout(ad["pt_date"].unique().to_list(), "agent_day")
refuse_holdout(cat["pt_date"].to_list(), "catalog")
refuse_holdout(ce["pt_date"].unique().to_list(), "consolidations")
PRIMARY = syn["primary_counterfactual"]["chosen"]
TURN_PRIMARY = syn["primary_turn_contrast"]["chosen"]
V_STAR = {"I": vch["I"]["chosen"], "II": vch["regime_II_uses"], "III": vch["III"]["chosen"]}
cal = calendar_nonholdout().sort("pt_date")
unit_days = {u: sorted(g["pt_date"].to_list()) for (u,), g in cal.group_by(["unit"])}
units = sorted(unit_days, key=lambda u: (int(re.match(r"\d+", u).group()), u))
regime_of = {u: str(cal.filter(pl.col("unit") == u)["regime"][0]) for u in units}
agent_seq = {int(a): g.sort("pt_date")["pt_date"].to_list() for (a,), g in ad.group_by(["agent"])}
EVTYPES = ("ML", "MG", "MR", "CC")
events = {t: cat.filter(pl.col("type") == t).rows(named=True) for t in ("ML", "MG", "MR", "CC", "MN")}


def post_offsets(e):
    if e["type"] == "CC":
        return list(range(0, min(int(e["run_len"]), 5)))
    return [1, 2]


def all_event_index(panel):
    """(agent, unit) -> indices of every catalogued day-level event (guards for mu and placebo days)."""
    d = {}
    for t in ("ML", "MG", "MR", "CC", "MN"):
        for e in events[t]:
            u = e["unit"]
            if e["pt_date"] in unit_days.get(u, []):
                d.setdefault((int(e["agent"]), u), []).append(unit_days[u].index(e["pt_date"]))
    return d


def run_event_types(V):
    rp = residual_panel(ad, V)
    panel = Panel(rp, unit_days, "u")
    zpanel = Panel(rp, unit_days, "zV")
    evidx = all_event_index(panel)
    prm = {r: autocov_params(panel, [u for u in units if regime_of[u] == r], exclude=evidx) for r in ("I", "II", "III")}
    prm_z = {r: autocov_params(zpanel, [u for u in units if regime_of[u] == r], exclude=evidx) for r in ("I", "II", "III")}
    out = {"prm": prm, "types": {}}
    cache, cache_z = {}, {}
    for t in EVTYPES:
        rows = []
        for e in events[t]:
            a, u = int(e["agent"]), e["unit"]
            x = panel.get(a, u)
            if x is None or e["pt_date"] not in unit_days[u]:
                continue
            i0 = unit_days[u].index(e["pt_date"])
            offs = post_offsets(e)
            evs = evidx.get((a, u), [])
            p = prm[regime_of[u]]
            r = event_delta(x, i0, offs, agent_mu(x, evs), p)
            if r is None:
                continue
            xz = zpanel.get(a, u)
            rz = event_delta(xz, i0, offs, agent_mu(xz, evs), prm_z[regime_of[u]]) if xz is not None else None
            pool = unit_placebo_pool(panel, u, evidx, offs, p, cache)
            own = placebo_deltas(x, evs, offs, p)
            poolz = unit_placebo_pool(zpanel, u, evidx, offs, prm_z[regime_of[u]], cache_z) if rz else []
            rows.append({"unit": u, "agent": a, "pt_date": e["pt_date"], "dose": e["dose"], **r,
                         "naive": rz["did"] if rz else float("nan"), "pool": pool, "own": own, "poolz": poolz,
                         "rel_u": [float(x[i0 + k]) if 0 <= i0 + k < len(x) else float("nan") for k in range(-5, 6)]})
        per_unit = {}
        for u in sorted({r["unit"] for r in rows}):
            rr = [r for r in rows if r["unit"] == u]
            res = {}
            for m in list(METHODS) + ["pretrend"]:
                res[m] = period_test([r[m] for r in rr], [[n[m] for n in r["pool"]] for r in rr], rng=rng)
            res["naive"] = period_test([r["naive"] for r in rr], [[n["did"] for n in r["poolz"]] for r in rr], rng=rng)
            res["own_null"] = period_test([r[PRIMARY] for r in rr], [[n[PRIMARY] for n in r["own"]] for r in rr], rng=rng)
            res["events"] = [{"agent": r["agent"], "pt_date": r["pt_date"], "dose": r["dose"],
                              **{m: r[m] for m in METHODS}, "naive": r["naive"], "pretrend": r["pretrend"],
                              "z_pool": (r[PRIMARY] - np.mean([n[PRIMARY] for n in r["pool"]])) /
                              (np.std([n[PRIMARY] for n in r["pool"]]) + 1e-9) if len(r["pool"]) >= 3 else None}
                             for r in rr]
            per_unit[u] = res
        metas = {}
        for m in list(METHODS) + ["pretrend", "naive"]:
            ts = [per_unit[u][m] for u in per_unit if per_unit[u][m]]
            metas[m] = dl_meta([x["effect"] for x in ts], [x["null_sd"] for x in ts])
        # event-study curve (mean u by relative day) and dose response (primary method)
        curve = np.nanmean(np.array([r["rel_u"] for r in rows]), axis=0).tolist() if rows else []
        hv = hockey_vs_linear(np.array([r["dose"] for r in rows]), np.array([r[PRIMARY] for r in rows])) if t == "ML" else None
        out["types"][t] = {"per_unit": per_unit, "meta": metas, "n_events": len(rows), "curve": curve, "dose": hv,
                           "kappa": (float(np.mean([r[PRIMARY] for r in rows]) / np.mean([r["dose"] for r in rows]))
                                     if rows else None),
                           "mean_dose": float(np.mean([r["dose"] for r in rows])) if rows else None}
    out["MN"] = run_mn(rp, V)
    out["SPILL"] = run_spill(rp)
    return out


def run_mn(rp, V):
    useq = {int(a): dict(zip(g["pt_date"].to_list(), g["u"].to_list())) for (a,), g in rp.group_by(["agent"])}
    newcomers = {int(e["agent"]) for e in events["MN"]}
    per = {}
    curves = []
    for e in events["MN"]:
        a = int(e["agent"])
        seq = [d for d in agent_seq.get(a, []) if d >= e["pt_date"]]
        xs = np.array([useq.get(a, {}).get(d, np.nan) for d in seq[:12]], float)
        if len(xs) < 12 or np.isfinite(xs[:3]).sum() < 1 or np.isfinite(xs[5:12]).sum() < 3:
            continue
        val = float(np.nanmean(xs[:3]) - np.nanmean(xs[5:12]))
        curves.append(xs.tolist())
        null = []
        udays = unit_days[e["unit"]]
        for b, s in useq.items():
            if b in newcomers or b == a:
                continue
            bseq = agent_seq[b]
            pos = {d: i for i, d in enumerate(bseq)}
            for d0 in udays:
                j = pos.get(d0)
                if j is None:
                    continue
                ys = np.array([s.get(d, np.nan) for d in bseq[j:j + 12]], float)
                if len(ys) == 12 and np.isfinite(ys[:3]).sum() >= 1 and np.isfinite(ys[5:12]).sum() >= 3:
                    null.append(float(np.nanmean(ys[:3]) - np.nanmean(ys[5:12])))
        per.setdefault(e["unit"], []).append({"agent": a, "pt_date": e["pt_date"], "deficit": val, "null": null})
    per_unit = {}
    for u, lst in per.items():
        t = period_test([x["deficit"] for x in lst], [x["null"] for x in lst], rng=rng)
        per_unit[u] = {"deficit": t, "events": [{k: v for k, v in x.items() if k != "null"} for x in lst]}
    ts = [v["deficit"] for v in per_unit.values() if v["deficit"]]
    meta = dl_meta([x["effect"] for x in ts], [x["null_sd"] for x in ts])
    curve = np.nanmean(np.array(curves), axis=0).tolist() if curves else []
    return {"per_unit": per_unit, "meta": meta, "curve": curve, "n_events": sum(len(v) for v in per.values())}


def run_spill(rp):
    """O8: incumbents' undifferenced zV, days 0..+2 after a join minus days -3..-1, vs. random days in the unit."""
    zd = {(int(a), d): z for a, d, z in rp.select("agent", "pt_date", "zV").rows() if z is not None}
    newcomers = {int(e["agent"]) for e in events["MN"]}
    per = {}
    for e in events["MN"]:
        u = e["unit"]
        days = unit_days[u]
        if e["pt_date"] not in days:
            continue

        def contrast(i0):
            vals = []
            for b in {a for (a, d) in zd if d in days} - newcomers:
                pre = [zd.get((b, days[i])) for i in range(i0 - 3, i0) if 0 <= i < len(days)]
                post = [zd.get((b, days[i])) for i in range(i0, i0 + 3) if 0 <= i < len(days)]
                pre, post = [x for x in pre if x is not None], [x for x in post if x is not None]
                if pre and post:
                    vals.append(np.mean(post) - np.mean(pre))
            return float(np.mean(vals)) if vals else float("nan")

        i0 = days.index(e["pt_date"])
        val = contrast(i0)
        null = [contrast(j) for j in range(3, len(days) - 2) if abs(j - i0) > 3]
        null = [x for x in null if np.isfinite(x)]
        per.setdefault(u, []).append((val, null))
    per_unit = {u: period_test([v for v, _ in lst], [n for _, n in lst], rng=rng) for u, lst in per.items()}
    ts = [t for t in per_unit.values() if t]
    return {"per_unit": per_unit, "meta": dl_meta([t["effect"] for t in ts], [t["null_sd"] for t in ts])}


def run_ctx():
    """Context erasure: dip after forced vs voluntary consolidations, per unit, writes and errors."""
    base = ad.select("agent", "pt_date", (pl.col("n_writes") / pl.col("n_turns")).alias("w_base"),
                     (1 - pl.col("V_rel")).alias("e_base"))
    c = ce.join(base, on=["agent", "pt_date"], how="left").filter(pl.col("kind").is_in(["CF", "CV"]))
    c = c.with_columns((pl.col("agent").cast(pl.Utf8) + "_" + pl.col("pt_date")).alias("cl"))
    out = {}
    for u in sorted(c["unit"].unique().to_list(), key=lambda u: (int(re.match(r"\d+", u).group()), u)):
        g = c.filter(pl.col("unit") == u)
        res = {}
        for o, post, pre, b in (("write", "w_post", "w_pre", "w_base"), ("error", "e_post", "e_pre", "e_base")):
            gg = g.filter(pl.col(b).is_not_null())
            cf, cv = gg.filter(pl.col("kind") == "CF"), gg.filter(pl.col("kind") == "CV")
            if cf.height < 20 or cv.height < 20:
                continue
            dbf = (cf[post] - cf[b]).to_numpy()
            dbv = (cv[post] - cv[b]).to_numpy()
            dpf = (cf[post] - cf[pre]).to_numpy()
            dpv = (cv[post] - cv[pre]).to_numpy()
            rho, n = spearman(cf["stored_dose"].to_numpy(), dbf if TURN_PRIMARY == "base" else dpf)
            res[o] = {"dip_cf": float(np.nanmean(dbf if TURN_PRIMARY == "base" else dpf)),
                      "dip_cv": float(np.nanmean(dbv if TURN_PRIMARY == "base" else dpv)),
                      "diff_base": cluster_boot_diff(dbf, cf["cl"].to_numpy(), dbv, cv["cl"].to_numpy(), 500, rng),
                      "diff_pre": cluster_boot_diff(dpf, cf["cl"].to_numpy(), dpv, cv["cl"].to_numpy(), 500, rng),
                      "rho_dose_dip": rho, "n_rho": n, "n_cf": cf.height, "n_cv": cv.height,
                      "rate_base": float(np.nanmean(gg[b].to_numpy()))}
        # POST-HOC (added after seeing the P5 result; labelled exploratory): exogenous-timing RD for forced
        # consolidations. Relative dip = mean writes in turns +1..+10 / mean writes in turns -20..-11 (far from the
        # cap) - 1, ratio of sums with an agent-day cluster bootstrap; the same for voluntary ones with >= 20 turns.
        ph = {}
        for kind in ("CF", "CV"):
            gg = g.filter((pl.col("kind") == kind) & (pl.col("n_far") >= 10) & (pl.col("n_post") >= 10))
            if gg.height < 20:
                continue
            cl = gg["cl"].to_numpy()
            post_w, far_w = gg["w_post"].to_numpy(), gg["w_far"].to_numpy()
            uu, inv = np.unique(cl, return_inverse=True)
            sp = np.bincount(inv, weights=post_w)
            sf = np.bincount(inv, weights=far_w)
            est = sp.sum() / max(sf.sum(), 1e-12) - 1
            bs = []
            for _ in range(500):
                ii = rng.integers(0, len(uu), len(uu))
                bs.append(sp[ii].sum() / max(sf[ii].sum(), 1e-12) - 1)
            ph[kind] = {"rel_dip": float(est), "lo": float(np.percentile(bs, 2.5)), "hi": float(np.percentile(bs, 97.5)),
                        "n": gg.height, "w_far": float(far_w.mean()), "w_post": float(post_w.mean()),
                        "abs_dip": float(post_w.mean() - far_w.mean())}
        res["posthoc_rd"] = ph
        out[u] = res
    return out


def run_ne18():
    """Within #38: per-agent change in u (04-20..04-24 minus 04-02..04-17) vs pre-period search rate."""
    ev = pl.read_parquet(SH / "events_core.parquet", columns=["pt_date", "agent", "action_type", "goal_no"])
    pre_days = [d for d in unit_days["38"] if d < "2026-04-20"]
    post_days = [d for d in unit_days["38"] if d >= "2026-04-20"]
    srch = (ev.filter((pl.col("action_type") == "SEARCH_HISTORY") & pl.col("pt_date").is_in(pre_days))
            .group_by("agent").agg(pl.len().alias("n_search")))
    hours = (ad.filter(pl.col("pt_date").is_in(pre_days)).group_by("agent").agg(pl.col("win_h").sum().alias("h"),
                                                                                   pl.len().alias("nd")))
    dose = hours.join(srch, on="agent", how="left").with_columns(
        (pl.col("n_search").fill_null(0) / pl.col("h")).alias("rate")).filter(pl.col("nd") >= 5)
    out = {}
    for V in V_CANDIDATES:
        rp = residual_panel(ad, V).filter(pl.col("unit") == "38")
        dd = (rp.group_by("agent").agg(pl.col("u").filter(pl.col("pt_date").is_in(post_days)).mean().alias("post"),
                                       pl.col("u").filter(pl.col("pt_date").is_in(pre_days)).mean().alias("pre"))
              .with_columns((pl.col("post") - pl.col("pre")).alias("du")).join(dose, on="agent", how="inner")
              .filter(pl.col("du").is_finite()))
        if dd.height < 5:
            out[V] = {"n": dd.height, "slope": float("nan"), "p": float("nan")}
            continue
        x, y = dd["rate"].to_numpy(), dd["du"].to_numpy()
        slope = float(np.polyfit(x, y, 1)[0])
        perm = np.array([np.polyfit(rng.permutation(x), y, 1)[0] for _ in range(4000)])
        out[V] = {"n": dd.height, "slope": slope, "p": float((np.abs(perm) >= abs(slope)).mean()),
                  "rate_range": [float(x.min()), float(x.max())]}
    return out


def verdict(ur, reg):
    """Per-period verdict from the pre-registered rule (V* only)."""
    vs = V_STAR[reg]
    signs = []  # (name, ok_sign, opposite_sig)
    for t, want in (("ML", -1), ("MN", -1), ("CC", None)):
        r = (ur.get(t) or {}).get(vs)
        if not r:
            continue
        pr = r.get(PRIMARY) if t != "MN" else r.get("deficit")
        if not pr:
            continue
        if want is None:  # CC on V*: P6 depends on V*; V_eng -> negative predicted; V_out/V_rel -> |ΔV| < 0.3
            if vs == "V_eng":
                signs.append(("CC", pr["effect"] < 0, pr["z"] >= 2))
            else:
                signs.append(("CC", abs(pr["effect"]) < 0.3, pr["effect"] <= -0.3 and pr["z"] <= -2))
        else:
            signs.append((t, pr["effect"] * want > 0, pr["z"] * want <= -2))
    mr = (ur.get("MR") or {}).get(vs)
    if mr and mr.get(PRIMARY):
        signs.append(("MR", abs(mr[PRIMARY]["z"]) < 2, abs(mr[PRIMARY]["z"]) >= 2))
    ctx = (ur.get("CTX") or {}).get("write")
    if ctx and ctx.get("diff_base" if TURN_PRIMARY == "base" else "diff_pre"):
        b = ctx["diff_base" if TURN_PRIMARY == "base" else "diff_pre"]
        signs.append(("CTX", b["est"] < 0, b["lo"] > 0))
    prim = [s for s in signs if s[0] != "MR"]
    if not prim and signs:
        v = "descriptive"
    elif not signs:
        v = "n/a"
    elif any(s[2] for s in signs):
        v = "failed"
    elif all(s[1] for s in signs):
        v = "supported"
    else:
        v = "mixed"
    reason = "; ".join(f"{n}: {'sign as predicted' if ok else 'sign not as predicted'}"
                       f"{', significantly opposite' if opp else ''}" for n, ok, opp in signs)
    return v, reason


if __name__ == "__main__":
    results = {"primary": PRIMARY, "turn_primary": TURN_PRIMARY, "V_star": V_STAR, "by_V": {}}
    for V in V_CANDIDATES:
        results["by_V"][V] = run_event_types(V)
        m = results["by_V"][V]["types"]["ML"]["meta"][PRIMARY]
        log(f"{V}: ML meta {m['mu'] if m else None}")
    results["CTX"] = run_ctx()
    log("ctx done")
    results["NE18"] = run_ne18()
    log("ne18 done")
    # reshape per unit
    per_unit = {}
    for u in units:
        reg = regime_of[u]
        ur = {"V_star": V_STAR[reg], "regime": reg}
        for t in EVTYPES:
            d = {V: results["by_V"][V]["types"][t]["per_unit"].get(u) for V in V_CANDIDATES}
            if any(d.values()):
                ur[t] = d
        d = {V: results["by_V"][V]["MN"]["per_unit"].get(u) for V in V_CANDIDATES}
        if any(d.values()):
            ur["MN"] = d
        d = {V: ({"deficit": results["by_V"][V]["SPILL"]["per_unit"].get(u)}
                 if results["by_V"][V]["SPILL"]["per_unit"].get(u) else None) for V in V_CANDIDATES}
        if any(d.values()):
            ur["SPILL"] = d
        if u in results["CTX"] and results["CTX"][u]:
            ur["CTX"] = results["CTX"][u]
        if u == "38":
            ur["NE18"] = results["NE18"]
        if len(ur) > 2:
            ur["verdict"], ur["verdict_reason"] = verdict(ur, reg)
            per_unit[u] = ur
    results["per_unit"] = per_unit
    # pre-registered primary: V* chosen per regime (I/II: regime I choice; III: regime III choice)
    vm = {}
    for t in EVTYPES + ("MN", "SPILL", "pretrend_ML"):
        ts = []
        for u in units:
            vs = V_STAR[regime_of[u]]
            if t in EVTYPES:
                x = results["by_V"][vs]["types"][t]["per_unit"].get(u)
                x = x.get(PRIMARY) if x else None
            elif t == "pretrend_ML":
                x = results["by_V"][vs]["types"]["ML"]["per_unit"].get(u)
                x = x.get("pretrend") if x else None
            elif t == "MN":
                x = results["by_V"][vs]["MN"]["per_unit"].get(u)
                x = x.get("deficit") if x else None
            else:
                x = results["by_V"][vs]["SPILL"]["per_unit"].get(u)
            if x:
                ts.append((u, x["effect"], x["null_sd"], x["n"]))
        vm[t] = {"meta": dl_meta([a for _, a, _, _ in ts], [b for _, _, b, _ in ts]),
                 "units": {u: {"effect": a, "se": b, "n": n} for u, a, b, n in ts}}
    results["vstar_meta"] = vm
    # cross-period CTX meta (writes): DL over units of the primary contrast
    k = "diff_base" if TURN_PRIMARY == "base" else "diff_pre"
    for o in ("write", "error"):
        ts = [(r[o][k]["est"], r[o][k]["se"]) for r in results["CTX"].values() if o in r and r[o][k]]
        results.setdefault("CTX_meta", {})[o] = dl_meta([a for a, _ in ts], [b for _, b in ts])
        rhos = [(r[o]["rho_dose_dip"], r[o]["n_rho"]) for r in results["CTX"].values() if o in r]
        results["CTX_meta"][o + "_rho_weighted"] = float(np.nansum([a * n for a, n in rhos]) / max(1, sum(n for _, n in rhos)))

    def clean(o):
        if isinstance(o, dict):
            return {str(k): clean(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [clean(v) for v in o]
        if isinstance(o, (np.floating, float)):
            return None if not np.isfinite(o) else float(o)
        if isinstance(o, np.integer):
            return int(o)
        return o

    (OUT / "results.json").write_text(json.dumps(clean(results), indent=1))
    for u, ur in per_unit.items():
        d = OUT / f"G{int(re.match(r'(\d+)', u).group(1)):02d}{re.match(r'\d+([ab]?)', u).group(1)}"
        d.mkdir(exist_ok=True)
        (d / "result.json").write_text(json.dumps(clean(ur), indent=1))
    write_provenance("run_scrambles", ["H15 agent_day", "scramble_catalog", "consolidations", "events_core"],
                     {"primary": PRIMARY, "turn_primary": TURN_PRIMARY, "V_star": V_STAR, "null": "unit-pooled placebo (A1)"},
                     built_by="hypotheses/H15-semantic-information-scrambles/analysis/run_scrambles.py")
    log("wrote results.json")
