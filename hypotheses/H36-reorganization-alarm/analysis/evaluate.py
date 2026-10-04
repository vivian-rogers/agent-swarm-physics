"""H36 evaluation on non-holdout days: trailing z-scores, the pre-registered alarm, hit rates per transition class,
false-alarm rates on placebo days and windows, AUC, timing, random-date null, Monday placebos, stall null, rivals,
robustness variants, per-period and per-NE results.

Usage: uv run python hypotheses/H36-reorganization-alarm/analysis/evaluate.py
Outputs: data/processed/H36-reorganization-alarm/{scores.parquet, event_table.parquet, results.json}
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h36lib as L  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

OFFS = list(range(-3, 4))
CLASSES = ["goal", "room", "scaffold", "roster", "operator"]
MAIN_SCORES = ["Z_phys", "Z_I", "Z_chi", "Z_C", "Z_act", "Z_cont", "Z_chan", "Z_or", "Z_phys_2s",
               "R1", "R2", "R3", "Z_phys_none", "Z_phys_lull", "Z_phys_b5", "R1_or_Zphys"]
THR = {k: (L.OR_THRESH if k == "Z_or" else L.THRESH) for k in MAIN_SCORES}


def compute_scores(d: pl.DataFrame) -> dict[str, np.ndarray]:
    def zs(suffix=""):
        out = {}
        for s in L.ACT_STATS:
            col = s + suffix
            out[s] = L.trailing_z(d[col].to_numpy().astype(float)) if col in d.columns else np.full(d.height, np.nan)
        for s in L.CONT_STATS:
            out[s] = L.trailing_z(d[s].to_numpy().astype(float))
        return out
    Z = zs("")
    A = L.alarm_scores(Z)
    sc = {k: A[k] for k in ["Z_phys", "Z_I", "Z_chi", "Z_C", "Z_act", "Z_cont", "Z_chan", "Z_or"]}
    sc.update({"z_" + k: v for k, v in Z.items()})
    sc["Z_phys_2s"] = np.abs(A["Z_phys"])
    for suf in ["_none", "_lull", "_b5"]:
        sc["Z_phys" + suf] = L.alarm_scores(zs(suf))["Z_phys"]
    sc["R1"] = L.trailing_z(d["R1_shift"].to_numpy().astype(float))
    sc["R2"] = L.trailing_z(d["R2_level"].to_numpy().astype(float), two_sided=True)
    sc["R3"] = L.trailing_z(d["R3_polar"].to_numpy().astype(float), two_sided=True)
    # union rule R1 or Z_phys: encoded as the max of the two (alarm iff either >= 2.0)
    sc["R1_or_Zphys"] = np.fmax(sc["R1"], sc["Z_phys"])
    return sc


def main():
    rng = np.random.default_rng(L.SEED)
    d = pl.read_parquet(L.OUT / "day_stats.parquet").sort("aday")
    ev = pl.read_parquet(L.OUT / "events.parquet")
    allev = pl.read_parquet(L.OUT / "allevents.parquet")
    sc = compute_scores(d)
    aday = d["aday"].to_numpy()
    pos = {int(a): i for i, a in enumerate(aday)}
    reg = d["regime"].to_numpy()
    ev_days = np.unique(allev["aday0"].drop_nulls().to_numpy())
    dist = np.array([np.min(np.abs(ev_days - a)) for a in aday])
    ok = np.isfinite(sc["Z_phys"])
    placebo = (dist >= L.PLACEBO_DIST) & ok
    monday = d["monday"].to_numpy() & placebo
    # scores table
    st = d.select("aday", "pt_date", "goal_no", "regime", "monday", "n_present", "T", "stall_min", "lull_min",
                  "consol_per_agent").with_columns(
        [pl.Series(k, v) for k, v in sc.items()] + [pl.Series("placebo", placebo), pl.Series("dist_event", dist)])
    st.write_parquet(L.OUT / "scores.parquet", compression="zstd")

    def val(k, a):
        i = pos.get(int(a))
        return np.nan if i is None else float(sc[k][i])

    def window(k, c, offs=L.HIT_WINDOW):
        vals = [val(k, c + o) for o in offs]
        fin = [v for v in vals if np.isfinite(v)]
        hit = any(v >= THR[k] for v in fin)
        first = next((o for o, v in zip(offs, vals) if np.isfinite(v) and v >= THR[k]), None)
        return hit, first, len(fin), (max(fin) if fin else np.nan)

    # ---- event table
    rows = []
    for r in ev.filter(~pl.col("holdout0")).iter_rows(named=True):
        c = r["aday0"]
        row = {k: r[k] for k in ["event_id", "cls", "ref", "label", "pt_date0", "aday0", "goal0", "regime0", "confounded",
                                 "all_refs_same_day"]}
        for k in MAIN_SCORES:
            h, f, n, mx = window(k, c)
            row[k + "_hit"] = h if n else None
            row[k + "_first"] = f
            row[k + "_wmax"] = mx
            row[k + "_d0"] = val(k, c)
        row["n_scored"] = window("Z_phys", c)[2]
        prof = [val("Z_phys", c + o) for o in OFFS]
        row["peak_off"] = OFFS[int(np.nanargmax(prof))] if np.isfinite(prof).any() else None
        for o in OFFS:
            for k in ["Z_phys", "Z_act", "Z_cont", "R1", "Z_I", "Z_chi", "Z_C"]:
                row[f"{k}_o{o}"] = val(k, c + o)
        rows.append(row)
    et = pl.DataFrame(rows, infer_schema_length=None)
    et.write_parquet(L.OUT / "event_table.parquet", compression="zstd")

    # ---- placebo windows
    pidx = np.flatnonzero(placebo)
    pcent = aday[pidx]

    def pw_max(k):
        return np.array([window(k, c)[3] for c in pcent])

    def pw_hit(k):
        return np.array([window(k, c)[0] for c in pcent])

    res = {"n_days": int(d.height), "n_placebo": int(placebo.sum()), "n_monday_placebo": int(monday.sum()),
           "classes": {}, "thresholds": THR}
    metrics = {}
    for cls in CLASSES + ["goal_unconfounded", "all_primary"]:
        if cls == "goal_unconfounded":
            sub = et.filter((pl.col("cls") == "goal") & ~pl.col("confounded"))
        elif cls == "all_primary":
            sub = et.filter(pl.col("cls").is_in(["goal", "room", "scaffold", "roster"]))
        else:
            sub = et.filter(pl.col("cls") == cls)
        sub = sub.filter(pl.col("n_scored") > 0)
        m = {"n_events": sub.height}
        for k in MAIN_SCORES:
            hits = sub[k + "_hit"].drop_nulls().to_numpy().astype(float)
            d0 = sub[k + "_d0"].to_numpy().astype(float)
            wm = sub[k + "_wmax"].to_numpy().astype(float)
            pday = sc[k][placebo]
            mk = {"hit": float(hits.mean()) if hits.size else None, "n": int(hits.size),
                  "far_day": float(np.mean(pday[np.isfinite(pday)] >= THR[k])),
                  "far_win": float(np.mean(pw_hit(k))),
                  "auc_d0": L.auc(d0, pday), "auc_d0_ci": L.auc_ci(d0, pday, rng, 1000),
                  "auc_win": L.auc(wm, pw_max(k)), "auc_win_ci": L.auc_ci(wm, pw_max(k), rng, 1000),
                  "far_day_monday": float(np.mean(sc[k][monday] >= THR[k])) if monday.any() else None,
                  "auc_d0_vs_monday": L.auc(d0, sc[k][monday]) if monday.any() else None}
            m[k] = mk
        metrics[cls] = m
    res["classes"] = metrics

    # ---- random-date null (goal class, primary score) and Monday placebo windows
    def rand_null(cls_sub, k, n_draw=2000):
        evs = cls_sub.filter(pl.col("n_scored") > 0)
        obs = float(np.mean(evs[k + "_hit"].drop_nulls().to_numpy().astype(float)))
        elig = {rg: aday[ok & (reg == rg)] for rg in np.unique(reg)}
        regs = evs["regime0"].to_list()
        draws = np.empty(n_draw)
        for b in range(n_draw):
            hs = []
            for rg in regs:
                c = int(rng.choice(elig[rg]))
                hs.append(window(k, c)[0])
            draws[b] = np.mean(hs)
        return {"observed": obs, "null_mean": float(draws.mean()), "null_q95": float(np.quantile(draws, 0.95)),
                "p": float((np.sum(draws >= obs) + 1) / (n_draw + 1))}
    goal = et.filter(pl.col("cls") == "goal")
    res["random_date"] = {k: rand_null(goal, k) for k in ["Z_phys", "Z_cont", "Z_act", "R1", "R2", "R1_or_Zphys"]}
    res["random_date_all_primary"] = rand_null(et.filter(pl.col("cls").is_in(["goal", "room", "scaffold", "roster"])), "Z_phys")
    mcent = aday[monday]
    res["monday_window_far"] = {k: float(np.mean([window(k, c)[0] for c in mcent])) for k in ["Z_phys", "R1", "Z_cont", "Z_act"]}
    res["nonmonday_placebo_far_day"] = {k: float(np.mean(sc[k][placebo & ~monday] >= THR[k])) for k in ["Z_phys", "R1", "Z_cont", "Z_act"]}

    # ---- stall null
    share = (d["stall_min"].to_numpy() / d["T"].to_numpy())
    js = d["lull_min"].to_numpy() / d["T"].to_numpy()
    top = placebo & (js >= np.quantile(js[placebo], 0.9))
    res["stall"] = {
        "top_decile_js_share_threshold": float(np.quantile(js[placebo], 0.9)),
        "n_top": int(top.sum()),
        "far_top_masked": float(np.mean(sc["Z_phys"][top] >= THR["Z_phys"])),
        "far_top_nomask": float(np.mean(sc["Z_phys_none"][top] >= THR["Z_phys"])),
        "far_rest_masked": float(np.mean(sc["Z_phys"][placebo & ~top] >= THR["Z_phys"])),
        "far_rest_nomask": float(np.nanmean(sc["Z_phys_none"][placebo & ~top] >= THR["Z_phys"])),
        "share_nomask_fa_on_top": float(np.sum((sc["Z_phys_none"] >= 2) & top) / max(1, np.sum((sc["Z_phys_none"] >= 2) & placebo))),
        "share_masked_fa_on_top": float(np.sum((sc["Z_phys"] >= 2) & top) / max(1, np.sum((sc["Z_phys"] >= 2) & placebo))),
        "mean_mask_share": float(np.mean(share)), "mean_js_share": float(np.mean(js)),
        "spearman_js_vs_Zphys_none_placebo": spearman(js[placebo], sc["Z_phys_none"][placebo]),
        "spearman_js_vs_Zphys_placebo": spearman(js[placebo], sc["Z_phys"][placebo]),
    }

    # ---- rivals: paired bootstrap AUC difference on goal day 0
    g = goal.filter(pl.col("n_scored") > 0)
    a0 = g["Z_phys_d0"].to_numpy().astype(float); b0 = g["R1_d0"].to_numpy().astype(float)
    both = np.isfinite(a0) & np.isfinite(b0)
    pa, pb = sc["Z_phys"][placebo], sc["R1"][placebo]
    pboth = np.isfinite(pa) & np.isfinite(pb)
    diffs = []
    ia, ip = np.flatnonzero(both), np.flatnonzero(pboth)
    for _ in range(2000):
        e_ = rng.choice(ia, ia.size); p_ = rng.choice(ip, ip.size)
        diffs.append(L.auc(a0[e_], pa[p_]) - L.auc(b0[e_], pb[p_]))
    res["rival_auc_diff_Zphys_minus_R1"] = {"n_events": int(both.sum()), "diff": float(L.auc(a0[both], pa[pboth]) - L.auc(b0[both], pb[pboth])),
                                            "ci": [float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))]}
    # ---- threshold sweep (goal class): hit vs window FAR
    sweep = {}
    for k in ["Z_phys", "Z_cont", "Z_act", "R1", "R2", "Z_phys_2s"]:
        out = []
        for th in np.arange(0.5, 4.01, 0.25):
            wm = g[k + "_wmax"].to_numpy().astype(float)
            out.append({"thr": float(th), "hit": float(np.mean(np.nan_to_num(wm, nan=-9) >= th)),
                        "far_win": float(np.mean(np.nan_to_num(pw_max(k), nan=-9) >= th)),
                        "far_day": float(np.mean(np.nan_to_num(sc[k][placebo], nan=-9) >= th))})
        sweep[k] = out
    res["sweep_goal"] = sweep
    # ---- event-locked profiles (goal) vs placebo
    prof = {}
    for k in ["Z_phys", "Z_act", "Z_cont", "R1", "Z_I", "Z_chi", "Z_C"]:
        prof[k] = {}
        for o in OFFS:
            v = g[f"{k}_o{o}"].to_numpy().astype(float); v = v[np.isfinite(v)]
            prof[k][o] = [float(v.mean()) if v.size else None, float(v.std(ddof=1) / np.sqrt(v.size)) if v.size > 1 else None, int(v.size)]
        pv = sc[k][placebo]; pv = pv[np.isfinite(pv)]
        prof[k]["placebo"] = [float(pv.mean()), float(pv.std(ddof=1)), int(pv.size)]
    res["profiles_goal"] = prof
    # ---- timing (goal hits)
    gh = g.filter(pl.col("Z_phys_hit") == True)  # noqa: E712
    res["timing_goal"] = {"first_offsets": gh["Z_phys_first"].to_list(), "peak_offsets": g["peak_off"].to_list()}
    # ---- NE41 nuisance
    r3 = placebo & (reg == "III")
    res["ne41"] = {"n": int(r3.sum()), "spearman_consol_vs_Zphys": spearman(d["consol_per_agent"].to_numpy()[r3], sc["Z_phys"][r3]),
                   "spearman_consol_vs_Zact": spearman(d["consol_per_agent"].to_numpy()[r3], sc["Z_act"][r3])}
    # ---- regime-specific placebo FAR
    res["far_by_regime"] = {rg: {"n": int((placebo & (reg == rg)).sum()),
                                 "Z_phys": float(np.mean(sc["Z_phys"][placebo & (reg == rg)] >= 2)) if (placebo & (reg == rg)).any() else None}
                            for rg in ["I", "II", "III"]}
    res["periods"], res["ne"] = period_results(d, st, et, sc, placebo, pos, val), ne_results(et, res, val)
    (L.OUT / "results.json").write_text(json.dumps(res, indent=1, default=lambda o: None if o is None or (isinstance(o, float) and not np.isfinite(o)) else (float(o) if isinstance(o, (np.floating,)) else int(o) if isinstance(o, np.integer) else bool(o) if isinstance(o, np.bool_) else str(o))))
    L.write_provenance("hypotheses/H36-reorganization-alarm/analysis/evaluate.py", ["(H36 day_stats, events)"],
                       {"thresh": L.THRESH, "base_days": L.BASE_DAYS, "placebo_dist": L.PLACEBO_DIST})
    report(res)


def spearman(x, y):
    m = np.isfinite(x) & np.isfinite(y)
    if m.sum() < 5:
        return None
    from scipy.stats import spearmanr
    r = spearmanr(x[m], y[m])
    return {"rho": float(r.statistic), "p": float(r.pvalue), "n": int(m.sum())}


def fmt(v, nd=2):
    return "–" if v is None or (isinstance(v, float) and not np.isfinite(v)) else f"{v:.{nd}f}"


def period_results(d, st, et, sc, placebo, pos, val):
    out = {}
    for (g,), sub in d.group_by(["goal_no"]):
        g = int(g)
        idx = [pos[int(a)] for a in sub["aday"].to_list()]
        pl_ = [i for i in idx if placebo[i]]
        fa = int(sum(sc["Z_phys"][i] >= 2 for i in pl_))
        far = fa / len(pl_) if pl_ else None
        k = et.filter((pl.col("cls") == "goal") & (pl.col("ref") == f"#{g}"))
        lines = []
        verdict = "n/a"
        if k.height and k["n_scored"][0] > 0 and g > 3:
            r = k.row(0, named=True)
            hit = bool(r["Z_phys_hit"])
            verdict = ("supported" if far is None or far <= 0.10 else "mixed") if hit else "failed"
            lines.append(f"**Kickoff** (day 0 = {r['pt_date0']}{'; same day as ' + r['all_refs_same_day'] if r['confounded'] else ''}): "
                         f"alarm {'**fired**' if hit else 'did not fire'} on days −1..+1"
                         + (f" (first on day {r['Z_phys_first']:+d})" if hit else "") + f"; R1 {'fired' if r['R1_hit'] else 'did not fire'}.")
            lines += ["", "| Score | day −1 | day 0 | day +1 | day +2 |", "| --- | --- | --- | --- | --- |"]
            for kk, lab in [("Z_phys", "Z_phys (alarm)"), ("Z_I", "Z_I"), ("Z_chi", "Z_χ"), ("Z_C", "Z_C"), ("Z_act", "Z_act"),
                            ("Z_cont", "Z_cont"), ("R1", "R1 centroid shift")]:
                lines.append(f"| {lab} | " + " | ".join(fmt(r[f'{kk}_o{o}']) for o in (-1, 0, 1, 2)) + " |")
        else:
            lines.append("**Kickoff:** not scored (day 0 held out, or fewer than 5 baseline days).")
        lines += ["", f"**Placebo days in this period:** {len(pl_)}; alarms {fa}" + (f" (rate {far:.2f})" if pl_ else "") + ".",
                  f"Non-holdout days scored: {int(np.isfinite(sc['Z_phys'][idx]).sum())} of {len(idx)}; "
                  f"mean Z_phys {fmt(float(np.nanmean(sc['Z_phys'][idx])) if np.isfinite(sc['Z_phys'][idx]).any() else None)}.",
                  "", f"Data: `data/processed/H36-reorganization-alarm/G{g:02d}/day_stats.parquet`, `scores.parquet`."]
        out[f"G{g:02d}"] = {"verdict": verdict, "body": "\n".join(lines), "placebo_n": len(pl_), "placebo_fa": fa}
    return out


def ne_results(et, res, val):
    out = {}
    c = res["classes"]["goal"]["Z_phys"]; rd = res["random_date"]["Z_phys"]
    auc_ok = c["auc_d0"] is not None and c["auc_d0"] >= 0.70 and c["auc_d0_ci"][0] > 0.5
    sup = (c["hit"] or 0) >= 0.6 and c["far_win"] <= 0.25 and auc_ok and rd["p"] < 0.05 and (res["monday_window_far"]["Z_phys"] <= 0.25)
    fail = (c["auc_d0"] is not None and c["auc_d0"] <= 0.60) or rd["p"] > 0.10
    v = "supported" if sup else ("failed" if fail else "mixed")
    r1 = res["classes"]["goal"]["R1"]
    body = [f"| Score | hit rate (n) | window FAR | per-day FAR | AUC day 0 [95% CI] | AUC window max | random-date p |",
            "| --- | --- | --- | --- | --- | --- | --- |"]
    for k in ["Z_phys", "Z_I", "Z_chi", "Z_C", "Z_act", "Z_cont", "R1", "R2", "R1_or_Zphys"]:
        m = res["classes"]["goal"][k]
        p = res["random_date"].get(k, {}).get("p")
        body.append(f"| {k} | {fmt(m['hit'])} ({m['n']}) | {fmt(m['far_win'])} | {fmt(m['far_day'], 3)} | {fmt(m['auc_d0'])} "
                    f"[{fmt(m['auc_d0_ci'][0])}, {fmt(m['auc_d0_ci'][1])}] | {fmt(m['auc_win'])} | {fmt(p, 3) if p is not None else '–'} |")
    body += ["", f"Monday-placebo window FAR (Z_phys): {fmt(res['monday_window_far']['Z_phys'])}; AUC(day 0 vs Monday placebos) "
                 f"{fmt(c['auc_d0_vs_monday'])}. Rival AUC difference (Z_phys − R1, day 0): "
                 f"{fmt(res['rival_auc_diff_Zphys_minus_R1']['diff'])} [{fmt(res['rival_auc_diff_Zphys_minus_R1']['ci'][0])}, "
                 f"{fmt(res['rival_auc_diff_Zphys_minus_R1']['ci'][1])}].",
             f"Unconfounded goal changes only (n = {res['classes']['goal_unconfounded']['n_events']}): Z_phys hit "
             f"{fmt(res['classes']['goal_unconfounded']['Z_phys']['hit'])}, AUC {fmt(res['classes']['goal_unconfounded']['Z_phys']['auc_d0'])}.",
             "", "Per-event table: `data/processed/H36-reorganization-alarm/event_table.parquet`; figure `figures/event_locked.pdf`."]
    out["NE34"] = {"verdict": v, "body": "\n".join(body)}

    def one(refs, rule):
        rows = et.filter(pl.col("ref").is_in(refs))
        lines = ["| Event | day 0 | Z_phys −1 / 0 / +1 / +2 / +3 | Z_I d0 | Z_χ d0 | Z_C d0 | Z_act d0 | Z_cont d0 | R1 d0 | alarm |",
                 "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        hits = []
        for r in rows.iter_rows(named=True):
            hits.append(bool(r["Z_phys_hit"]) if r["Z_phys_hit"] is not None else None)
            lines.append(f"| {r['ref']} ({r['label']}) | {r['pt_date0']} | " + " / ".join(fmt(r[f'Z_phys_o{o}']) for o in (-1, 0, 1, 2, 3))
                         + f" | {fmt(r['Z_I_o0'])} | {fmt(r['Z_chi_o0'])} | {fmt(r['Z_C_o0'])} | {fmt(r['Z_act_o0'])} | {fmt(r['Z_cont_o0'])} | "
                         f"{fmt(r['R1_o0'])} | {'yes' if r['Z_phys_hit'] else 'no' if r['Z_phys_hit'] is not None else 'not scored'} |")
        if rule == "descriptive":
            verdict = "descriptive"
        else:
            verdict = "supported" if hits and all(h for h in hits if h is not None) and any(h is not None for h in hits) else \
                      ("failed" if any(h is False for h in hits) else "n/a")
        return verdict, "\n".join(lines)
    for ne, refs, rule in [("NE15", ["NE15"], "descriptive"), ("NE42", ["NE42a", "NE42b"], "descriptive"),
                           ("NE14", ["NE14b"], "alarm"), ("NE17", ["NE17"], "alarm"), ("NE18", ["NE18"], "alarm")]:
        v_, b_ = one(refs, rule)
        out[ne] = {"verdict": v_, "body": b_}
    n41 = res["ne41"]
    s = n41["spearman_consol_vs_Zphys"]
    out["NE41"] = {"verdict": "n/a", "body": f"Regime-III placebo days (n = {n41['n']}): Spearman ρ(consolidations per present agent, Z_phys) = "
                   f"{fmt(s['rho']) if s else '–'} (p {fmt(s['p'], 3) if s else '–'}); with Z_act: "
                   f"{fmt(n41['spearman_consol_vs_Zact']['rho']) if n41['spearman_consol_vs_Zact'] else '–'}. "
                   f"Nuisance check {'passes' if s and (abs(s['rho']) < 0.2 or s['p'] > 0.05) else 'fails'} (rule: |ρ| < 0.2 or p > 0.05)."}
    return out


def report(res):
    print(f"days {res['n_days']}, placebo {res['n_placebo']} (Monday {res['n_monday_placebo']})")
    for cls in CLASSES + ["goal_unconfounded", "all_primary"]:
        m = res["classes"][cls]
        print(f"\n[{cls}] n = {m['n_events']}")
        for k in MAIN_SCORES:
            x = m[k]
            print(f"  {k:12s} hit {fmt(x['hit'])} (n {x['n']})  FARwin {fmt(x['far_win'])}  FARday {fmt(x['far_day'], 3)}  "
                  f"AUC0 {fmt(x['auc_d0'])} [{fmt(x['auc_d0_ci'][0])},{fmt(x['auc_d0_ci'][1])}]  AUCwin {fmt(x['auc_win'])}  "
                  f"Mon FARday {fmt(x['far_day_monday'], 3)}  AUC0 vs Mon {fmt(x['auc_d0_vs_monday'])}")
    print("\nrandom-date", json.dumps(res["random_date"], indent=None))
    print("random-date all primary", res["random_date_all_primary"])
    print("monday window FAR", res["monday_window_far"], "non-Monday day FAR", res["nonmonday_placebo_far_day"])
    print("stall", json.dumps(res["stall"], indent=None))
    print("rival diff", res["rival_auc_diff_Zphys_minus_R1"])
    print("timing", res["timing_goal"])
    print("ne41", res["ne41"]); print("far by regime", res["far_by_regime"])
    print("verdicts NE", {k: v["verdict"] for k, v in res["ne"].items()})
    print("verdicts G", {k: v["verdict"] for k, v in sorted(res["periods"].items())})


if __name__ == "__main__":
    main()
