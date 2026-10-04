"""H27 exploratory round 1 on non-holdout goal periods (card: Observables O1-O8, Prediction P0-P6).

Reads data/processed/H27-herding-early-warning/G<NN>/series_w{15,30}.parquet (scheme/build.py) and the frozen
tau* from synthetic/synthetic_summary.json. Writes results_round1.json, segments_round1.parquet,
onsets_round1.parquet and G<NN>/round1.json into the same data folder.

Usage: uv run python hypotheses/H27-herding-early-warning/analysis/explore.py
"""
from __future__ import annotations

import json
import os
import sys
import warnings
from dataclasses import replace
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "2")
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ews_core as E  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data/processed/H27-herding-early-warning"
sys.path.insert(0, str(ROOT))
from infra.shared import common as C  # noqa: E402

LEADS = (1, 2, 4, 8)
KEYS = ("composite", "tau_ar1", "tau_sd", "tau_skew", "tau_flick", "flick_level", "tau_sd_binom", "mean_last4")
COVER_MIN = 0.5
CANDIDATES = (18, 31, 37, 41)
SEED = 20261004


def load_tau_star() -> float:
    return float(json.loads((DATA / "synthetic/synthetic_summary.json").read_text())["meta"]["tau_star"])


def load_series(g: int, W: int, base: Path = DATA):
    s = pl.read_parquet(base / f"G{g:02d}" / f"series_w{W}.parquet").sort("gwin")
    # exploration guard: no held-out day may be present
    if base == DATA and any(C.holdout_mask(s["pt_date"].to_list(), [g] * s.height)):
        raise SystemExit(f"G{g}: holdout rows present")
    q = json.loads((base / "coverage.json").read_text())[str(g)][f"w{W}"]["q"]
    k = s.select([f"k{a}" for a in range(1, q + 1)]).to_numpy().astype(int) if q else np.zeros((s.height, 0), int)
    return k, s["n"].to_numpy().astype(int), s["win"].to_numpy(), s["day"].to_numpy(), s


def period_set(W: int, base: Path = DATA, goals=None):
    cov = json.loads((base / "coverage.json").read_text())
    out = []
    for g, c in cov.items():
        if goals is not None and int(g) not in goals:
            continue
        if f"w{W}" in c and c[f"w{W}"]["frac_n_ge3"] >= COVER_MIN and c[f"w{W}"]["q"] > 0:
            out.append(int(g))
    return sorted(out)


def analyze_period(g, W, p, tau_star, rng, base=DATA, leads=LEADS, n_shift=500, robust=True):
    warnings.simplefilter("ignore")
    k, n, win, day, s = load_series(g, W, base)
    T, q = k.shape
    R = dict(goal=g, W=W, T=T, q=q, days=int(len(np.unique(day))), frac_obs=float((n >= p.n_obs).mean()))
    on = E.find_onsets(k, n, win, day, p)
    on_slow = E.find_onsets(k, n, win, day, replace(p, base_skip=4))
    R["onsets"] = on
    R["onsets_slow"] = on_slow
    seg, drops = {}, {}
    for lead in leads:
        rows, dr = E.onset_and_placebo_segments(k, n, on, lead, p)
        seg[lead], drops[lead] = rows, dr
    R["drops"] = drops
    rows_slow, drops_slow = E.onset_and_placebo_segments(k, n, on_slow, 4, p)
    R["drops_slow"] = drops_slow
    conc = E.concentration_segments(k, n, on, 4, p)
    # operator
    ind = E.all_window_indicators(k, n, p)
    ops = {}
    for rule in ("ews", "level", "momentum"):
        al, watch = E.alarms(ind, k, rule, tau_star, p)
        sc = E.score_alarms(al, watch, on, p)
        sw = E.swarm_score(al, watch, on, p)
        sc["swarm"] = sw
        if rule == "ews" and n_shift:
            sc["shift_hits"] = E.shifted_hits(al, watch, on, rng, n_shift, p).tolist()
        ops[rule] = sc
    R["operator"] = ops
    # O1-slow operator (secondary)
    al, watch = E.alarms(ind, k, "ews", tau_star, p)
    R["operator_slow"] = E.score_alarms(al, watch, on_slow, p)
    # alarm/day bookkeeping
    R["watch_windows"] = int(watch.sum())
    R["active_days_evaluated"] = int(len(np.unique(day[watch.any(1)]))) if watch.any() else 0
    # robustness (lead 4): S/L and sigma
    rob = {}
    if robust:
        for nm, pp in (("S16L8", replace(p, S=16, L=8)), ("S32L16", replace(p, S=32, L=16)),
                       ("sigma2", replace(p, sigma=2.0)), ("sigma8", replace(p, sigma=8.0))):
            rr, _ = E.onset_and_placebo_segments(k, n, on, 4, pp)
            rob[nm] = rr
    return R, seg, rows_slow, conc, rob


def groups_from(per_period_rows, key):
    G = {}
    for g, rows in per_period_rows.items():
        pos = np.array([r[key] for r in rows if r["kind"] == "onset"])
        neg = np.array([r[key] for r in rows if r["kind"] == "placebo"])
        G[g] = (pos, neg)
    return G


def auc_table(per_period_rows, rng, n_boot=2000):
    out = {}
    for kk in KEYS:
        G = groups_from(per_period_rows, kk)
        est, ci = E.cluster_bootstrap_auc(G, kk, rng, n_boot)
        out[kk] = dict(auc=est, ci=ci)
    out["n_onset_segments"] = int(sum(1 for rows in per_period_rows.values() for r in rows if r["kind"] == "onset"))
    out["n_placebo_segments"] = int(sum(1 for rows in per_period_rows.values() for r in rows if r["kind"] == "placebo"))
    out["n_periods_with_onsets"] = int(sum(1 for rows in per_period_rows.values() if any(r["kind"] == "onset" for r in rows)))
    return out


def pool_operator(results, rule, key="operator"):
    tot = dict(n_onsets=0, warnable=0, hits=0, leads=[], false_alarms=0, negatives=0, n_alarms=0, true_alarms=0)
    days = 0
    for R in results:
        sc = R[key][rule] if key == "operator" else R[key]
        for kk in tot:
            tot[kk] = tot[kk] + ([int(x) for x in sc[kk]] if kk == "leads" else sc[kk])
        days += R["active_days_evaluated"]
    W = results[0]["W"] if results else 15
    out = dict(n_onsets=tot["n_onsets"], warnable=tot["warnable"], hits=tot["hits"],
               hit_rate=tot["hits"] / max(tot["n_onsets"], 1), hit_rate_warnable=tot["hits"] / max(tot["warnable"], 1),
               far=tot["false_alarms"] / max(tot["negatives"], 1), false_alarms=tot["false_alarms"],
               false_alarms_per_day=tot["false_alarms"] / max(days, 1), ppv=tot["true_alarms"] / max(tot["n_alarms"], 1),
               n_alarms=tot["n_alarms"], median_lead_h=float(np.median(tot["leads"]) * W / 60) if tot["leads"] else None,
               leads_h=[x * W / 60 for x in tot["leads"]], days=days)
    if key == "operator":
        sw = [R["operator"][rule]["swarm"] for R in results]
        out["swarm"] = dict(n_onsets=sum(x["n_onsets"] for x in sw), hits=sum(x["hits"] for x in sw),
                            far=sum(x["false_alarms"] for x in sw) / max(sum(x["negatives"] for x in sw), 1),
                            false_alarms_per_day=sum(x["false_alarms"] for x in sw) / max(days, 1),
                            median_lead_h=float(np.median([l for x in sw for l in x["leads"]]) * W / 60)
                            if any(x["leads"] for x in sw) else None)
        if rule == "ews":
            sh = np.array([R["operator"]["ews"]["shift_hits"] for R in results if "shift_hits" in R["operator"]["ews"]])
            if sh.size:
                tot_sh = sh.sum(0)
                out["N2_null_mean_hits"] = float(tot_sh.mean())
                out["N2_p"] = float((1 + (tot_sh >= tot["hits"]).sum()) / (1 + len(tot_sh)))
    return out


def run_arm(W, p, tau_star, goals=None, base=DATA, robust=True, n_shift=500, tag=""):
    rng = np.random.default_rng(SEED + W)
    periods = period_set(W, base, goals)
    results, segs, segs_slow, concs, robs = [], {}, {}, {}, {}
    for g in periods:
        R, seg, rows_slow, conc, rob = analyze_period(g, W, p, tau_star, rng, base, n_shift=n_shift, robust=robust)
        results.append(R)
        segs[g], segs_slow[g], concs[g], robs[g] = seg, rows_slow, conc, rob
        print(f"W{W} G{g}: T={R['T']} q={R['q']} onsets={len(R['onsets'])} (slow {len(R['onsets_slow'])}) "
              f"eval@4={sum(1 for r in seg[4] if r['kind'] == 'onset')} placebo@4={sum(1 for r in seg[4] if r['kind'] == 'placebo')}")
    leads = sorted(next(iter(segs.values())).keys()) if segs else []
    A = {lead: auc_table({g: segs[g][lead] for g in periods}, rng) for lead in leads}
    A_slow = auc_table(segs_slow, rng)
    A_conc = auc_table(concs, rng)
    A_rob = {}
    if robust and periods:
        for nm in next(iter(robs.values())).keys():
            A_rob[nm] = auc_table({g: robs[g][nm] for g in periods}, rng, n_boot=1000)
    # per-period AUC (lead 4)
    per = {}
    for g in periods:
        rows = segs[g][4]
        pos = [r["composite"] for r in rows if r["kind"] == "onset"]
        neg = [r["composite"] for r in rows if r["kind"] == "placebo"]
        per[g] = dict(n_eval=len(pos), n_placebo=len(neg), auc_composite=E.auc(pos, neg) if pos and neg else None,
                      percentiles=[float((np.array(neg) < v).mean() + 0.5 * (np.array(neg) == v).mean()) for v in pos] if neg else [],
                      **{f"auc_{kk}": (E.auc([r[kk] for r in rows if r["kind"] == "onset"], [r[kk] for r in rows if r["kind"] == "placebo"])
                                        if pos and neg else None) for kk in ("tau_ar1", "tau_sd", "tau_sd_binom", "tau_flick", "flick_level", "mean_last4")})
    ops = {rule: pool_operator(results, rule) for rule in ("ews", "level", "momentum")}
    ops["ews_O1slow"] = pool_operator(results, None, key="operator_slow")
    return dict(W=W, periods=periods, auc=A, auc_O1slow=A_slow, auc_concentration=A_conc, auc_robust=A_rob,
                per_period=per, operator=ops, results=results, segs=segs)


def verdicts(arm):
    A4 = arm["auc"][4]["composite"]
    auc4, ci = A4["auc"], A4["ci"]
    per = [v for v in arm["per_period"].values() if v["n_eval"] >= 2 and v["auc_composite"] is not None]
    frac_pos = (sum(v["auc_composite"] > 0.5 for v in per) / len(per)) if per else None
    if auc4 is None or not np.isfinite(auc4):
        p1 = "untestable (no evaluable onsets)"
    elif auc4 >= 0.70 and ci[0] > 0.5 and (frac_pos is None or frac_pos >= 2 / 3):
        p1 = "supported"
    elif ci[0] <= 0.5 or auc4 < 0.6:
        p1 = "failed"
    else:
        p1 = "mixed"
    op = arm["operator"]["ews"]
    lv = arm["operator"]["level"]
    useful = (op["far"] <= 0.05 and op["hit_rate"] >= 0.5 and (op["median_lead_h"] or 0) >= 1.0
              and op.get("N2_p", 1) < 0.05 and (op["median_lead_h"] or 0) - (lv["median_lead_h"] or 0) >= 0.5)
    return dict(P1=p1, P1_auc=auc4, P1_ci=ci, P1_frac_periods_pos=frac_pos, P1_n_periods_2plus=len(per), P3_useful=bool(useful))


def main():
    tau_star = load_tau_star()
    print(f"tau* (frozen from synthetic S0) = {tau_star:.3f}")
    arm15 = run_arm(15, E.P0, tau_star)
    arm30 = run_arm(30, E.P_W30, tau_star, robust=False, n_shift=200)
    out = {}
    for nm, arm in (("W15", arm15), ("W30", arm30)):
        out[nm] = {kk: v for kk, v in arm.items() if kk not in ("results", "segs")}
        out[nm]["verdicts"] = verdicts(arm)
        out[nm]["period_summaries"] = [
            dict(goal=R["goal"], T=R["T"], q=R["q"], days=R["days"], frac_obs=R["frac_obs"], n_onsets=len(R["onsets"]),
                 n_onsets_slow=len(R["onsets_slow"]), drops=R["drops"], onsets=R["onsets"],
                 operator={rule: {kk: R["operator"][rule][kk] for kk in ("n_onsets", "warnable", "hits", "leads", "false_alarms",
                                                                           "negatives", "n_alarms", "true_alarms", "per_onset")}
                           for rule in ("ews", "level", "momentum")},
                 active_days_evaluated=R["active_days_evaluated"], watch_windows=R["watch_windows"])
            for R in arm["results"]]
    out["tau_star"] = tau_star
    (DATA / "results_round1.json").write_text(json.dumps(out, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    # tables
    rows, orow = [], []
    for nm, arm in (("W15", arm15), ("W30", arm30)):
        for g, seg in arm["segs"].items():
            for lead, rr in seg.items():
                for r in rr:
                    rows.append(dict(arm=nm, goal=g, **r))
        for R in arm["results"]:
            for o in R["onsets"]:
                orow.append(dict(arm=nm, goal=R["goal"], rule="O1", **o))
            for o in R["onsets_slow"]:
                orow.append(dict(arm=nm, goal=R["goal"], rule="O1slow", **o))
            f = DATA / f"G{R['goal']:02d}"
            (f / f"round1_w{R['W']}.json").write_text(json.dumps(
                dict(goal=R["goal"], W=R["W"], T=R["T"], q=R["q"], onsets=R["onsets"], onsets_slow=R["onsets_slow"], drops=R["drops"],
                     per_period=arm["per_period"].get(R["goal"]),
                     operator={rule: {kk: v for kk, v in R["operator"][rule].items() if kk != "shift_hits"} for rule in R["operator"]}),
                indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    pl.DataFrame(rows).write_parquet(DATA / "segments_round1.parquet", compression="zstd")
    pl.DataFrame(orow).write_parquet(DATA / "onsets_round1.parquet", compression="zstd")
    for nm in ("W15", "W30"):
        v = out[nm]["verdicts"]
        print(nm, v)
        for lead, A in out[nm]["auc"].items():
            print(f"  lead {lead}: n+ {A['n_onset_segments']} n- {A['n_placebo_segments']} | " +
                  " ".join(f"{kk} {A[kk]['auc']:.2f}[{A[kk]['ci'][0]:.2f},{A[kk]['ci'][1]:.2f}]" for kk in KEYS if A[kk]['auc'] == A[kk]['auc']))
        for rule, op in out[nm]["operator"].items():
            print(f"  {rule}: " + json.dumps({k: op[k] for k in op if k != "leads_h"}, default=str))


if __name__ == "__main__":
    main()
