"""H56 ep_newton recheck (2026-10-04, post hoc; non-holdout only; no confirm script run).

Trigger: infra/README "Known issues" (H90). H56 copied the legacy cross-product Newton count form (`newton_counts`)
and applies it at d/n up to ~0.46 (55 fine-class indicator columns, n0 = 120 transitions per agent-day, 4 quarter
folds), where the legacy form can return a spurious positive bound. The corrected held-out estimator is
`infra/shared/ep_newton.py: newton_counts_heldout`, reached through the H56_EP=heldout switch in h56lib. Its values
are ridge-shrunk (about 0.5-0.96 of their long-run value), so only excess-over-null and null tests are comparable
with round 1, never raw magnitudes.

Steps (each writes into data/processed/H56-ep-platform-fingerprint/recheck_epfix/):
  --verify DIR   compare a default-mode (H56_EP=xprod) rerun written to DIR with the stored round-1 outputs. Round 1
                 ran the natives as `native.py --test NE40,NE14,NE43` then `--test G51` (one RNG stream per call;
                 file times 23:05:42/44/49 and 23:07:50), so reproduce them in that order.
  --synthetic    level layout at H56's real d/T (not covered by infra ep_newton_synthetic.py, which tests nested
                 pairwise sets): one Markov chain per agent on 11 states; (i) daily O1 (n0 = 120, 4 quarter folds):
                 raw bias on reversible chains and recovery on driven chains, legacy vs corrected; (ii) per-agent
                 period level with the block-flip null: size on reversible chains and power on driven chains
  --levels       real data: is per-agent fine-action EP above a reversible null with the SAME estimator? Per
                 non-holdout goal period, agents with >= 300 transitions on >= 2 days; observed Newton bound (day
                 folds) vs a block-flip null (each (day, quarter) count block transposed with probability 1/2, R
                 draws); both estimators. Scaffold share on excess: 1 - exc(V5)/exc(V1).
  --compare      old (round 1) vs new (recheck run) table of every EP number the card quotes -> compare.json
  --estimates    per_period_estimates rows (legacy round-1 rows + recheck rows tagged post hoc in `method`)
Run (one process, 2 threads):
  H56_EP=heldout uv run python hypotheses/H56-ep-platform-fingerprint/analysis/recheck_epfix.py --levels
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h56lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
import ep_newton as EPN  # noqa: E402
from common import holdout_mask  # noqa: E402

RE = L.DATA / "recheck_epfix"
OLD = L.DATA
EST = {"legacy": EPN.newton_counts_xprod, "heldout": EPN.newton_counts_heldout}
V1, V5, V3, V6 = 0, 4, 2, 5
VN = {V1: "act_all", V5: "act_agent_b3", V3: "coarse_all", V6: "coarse_agent_b3"}


def jdump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, default=lambda o: None if o is None else (
        float(o) if isinstance(o, (np.floating, np.integer)) else str(o))))


def finite(x):
    return x is not None and isinstance(x, (int, float)) and math.isfinite(x)


# ============================================================================ 1. verify the default reproduces round 1
def verify(d):
    d = Path(d)
    rows, ok = [], True
    for sub in ("replication", "native"):
        for f in sorted((OLD / sub).iterdir()):
            g = d / sub / f.name
            if not g.exists():
                rows.append((f"{sub}/{f.name}", "missing in rerun"))
                if f.name not in ("period_summary.json",):   # written by write_period_folders.py, not rerun
                    ok = False
                continue
            if f.suffix == ".parquet":
                a, b = pl.read_parquet(f), pl.read_parquet(g)
                same = a.shape == b.shape and a.columns == b.columns and a.equals(b, null_equal=True)
            else:
                ja, jb = json.loads(f.read_text()), json.loads(g.read_text())
                if f.name == "NE40.json":   # `schema` comes from an unordered group_by: compare it as a set of rows
                    for j in (ja, jb):
                        j["schema"] = sorted(j["schema"], key=lambda r: str(r["first"]))
                same = ja == jb
                if not same:   # NaN != NaN in Python; compare the canonical text
                    same = json.dumps(ja, sort_keys=True) == json.dumps(jb, sort_keys=True)
            rows.append((f"{sub}/{f.name}", "identical" if same else "DIFFERENT"))
            ok &= bool(same)
    for r in rows:
        print(f"  {r[0]:<40s} {r[1]}")
    print("verify (default H56_EP=xprod reproduces round 1):", "OK" if ok else "FAILED")
    jdump(RE / "verify_default.json", {"rerun_dir": str(d), "files": dict(rows), "ok": ok,
                                       "checked_at": dt.datetime.now(dt.timezone.utc).isoformat()})
    return ok


# ============================================================================ 2. level synthetic at H56's d/T
def _flip_null(Cb, day_of_block, n_days, R, rng, est):
    """Block-flip null: each block's counts transposed with probability 1/2, regrouped by day (fold labels)."""
    CbT = Cb.transpose(0, 2, 1)
    out = np.empty(R)
    for r in range(R):
        f = rng.random(len(Cb)) < 0.5
        Cs = np.where(f[:, None, None], CbT, Cb)
        Dd = np.zeros((n_days,) + Cb.shape[1:])
        np.add.at(Dd, day_of_block, Cs)
        out[r] = est(Dd[Dd.sum((1, 2)) > 0])
    return out


def synthetic(reps_daily=300, reps_level=100, R=50):
    rng = np.random.default_rng(20261004)
    q = 11
    res = {"daily_n0_120": {}, "agent_period": {}}
    # (i) daily O1: one agent-day, n0 = 120 transitions in 4 quarter blocks (folds = quarters); d = 55
    for sig in (0.0, 0.04, 0.08, 0.16):
        vals = {k: [] for k in EST}
        truth = []
        for _ in range(reps_daily):
            B, F, U, st = L.random_template(q, rng)
            s = 0.0 if sig == 0 else L.solve_s(B, F, U, st, sig)
            P = L.chain_from_params(B, F, U, s, st)
            truth.append(L.true_ep(P))
            C = L.simulate_counts(P, [120], rng, blocks=4)[0]
            for k, f in EST.items():
                vals[k].append(f(C))
        res["daily_n0_120"][f"sigma={sig}"] = {
            "true_mean": float(np.mean(truth)), "reps": reps_daily, "d_max": q * (q - 1) // 2, "n": 120,
            **{f"{k}_mean": float(np.nanmean(v)) for k, v in vals.items()},
            **{f"{k}_sd": float(np.nanstd(v)) for k, v in vals.items()},
            **{f"{k}_frac_pos": float(np.mean(np.asarray(v) > 0)) for k, v in vals.items()}}
        print("daily", sig, {k: round(float(np.nanmean(v)), 4) for k, v in vals.items()}, flush=True)
    # (ii) agent-period level: days x transitions/day (4 quarter blocks per day), day folds; block-flip null
    for size, (nd, per_day) in {"3d_x_160": (3, 160), "5d_x_600": (5, 600), "16d_x_450": (16, 450)}.items():
        for sig in (0.0, 0.02, 0.08):
            obs = {k: [] for k in EST}
            pv = {k: [] for k in EST}
            exc = {k: [] for k in EST}
            truth = []
            for _ in range(reps_level):
                B, F, U, st = L.random_template(q, rng)
                s = 0.0 if sig == 0 else L.solve_s(B, F, U, st, sig)
                P = L.chain_from_params(B, F, U, s, st)
                truth.append(L.true_ep(P))
                Cdb = L.simulate_counts(P, np.full(nd, per_day), rng, blocks=4)      # (days, 4, q, q)
                Cday = Cdb.sum(1)
                Cb = Cdb.reshape(-1, q, q).astype(np.float64)
                dob = np.repeat(np.arange(nd), 4)
                for k, f in EST.items():
                    o = f(Cday)
                    nl = _flip_null(Cb, dob, nd, R, rng, f)
                    obs[k].append(o)
                    pv[k].append((1 + np.sum(nl >= o)) / (R + 1))
                    exc[k].append(o - np.nanmean(nl))
            res["agent_period"][f"{size}:sigma={sig}"] = {
                "days": nd, "per_day": per_day, "true_mean": float(np.mean(truth)), "reps": reps_level, "R": R,
                **{f"{k}_mean": float(np.nanmean(v)) for k, v in obs.items()},
                **{f"{k}_excess_mean": float(np.nanmean(v)) for k, v in exc.items()},
                **{f"{k}_reject05": float(np.mean(np.asarray(v) <= 0.05)) for k, v in pv.items()}}
            print("level", size, sig, {k: (round(float(np.nanmean(obs[k])), 4), round(float(np.mean(np.asarray(pv[k]) <= 0.05)), 2))
                                        for k in EST}, flush=True)
    jdump(RE / "synthetic_levels.json", res)
    return res


# ============================================================================ 3. real-data levels vs block-flip null
def levels(R=100):
    import event_study as ES
    D = ES.Data()
    hm = holdout_mask(D.nh_dates, D.nh_goal)
    assert not any(hm), "held-out days in the H56 day list"
    rng = np.random.default_rng(20261007)
    out = []
    for g in sorted(set(D.nh_goal)):
        didx = [i for i, gg in enumerate(D.nh_goal) if gg == g]
        if len(didx) < 2:
            continue
        rec = {"goal_no": g, "regime": D.nh_regime[didx[0]], "first_day": D.nh_dates[didx[0]],
               "last_day": D.nh_dates[didx[-1]], "variants": {}}
        agents_v1 = None
        for vi in (V1, V5, V3, V6):
            nt = D.ntr[vi][:, didx]
            ag = [a for a in range(D.n_agents) if nt[a].sum() >= 300 and (nt[a] > 0).sum() >= 2]
            if vi == V1:
                agents_v1 = ag
            if len(ag) < 3:
                continue
            per = {}
            for a in ag:
                dd = [i for i in didx if D.ntr[vi][a, i] > 0]
                Cday = D.Cday[vi][a, dd].astype(np.float64)
                Cb = D.C[vi][a, dd].reshape((-1,) + Cday.shape[1:]).astype(np.float64)
                dob = np.repeat(np.arange(len(dd)), 4)
                keepb = Cb.sum((1, 2)) > 0
                Cb, dob = Cb[keepb], dob[keepb]
                r = {"n": int(Cday.sum())}
                for k, f in EST.items():
                    o = f(Cday)
                    nl = _flip_null(Cb, dob, len(dd), R, rng, f)
                    r[k] = {"obs": float(o), "null_mean": float(np.nanmean(nl)), "null_p95": float(np.nanpercentile(nl, 95)),
                            "p": float((1 + np.sum(nl >= o)) / (R + 1))}
                per[int(a)] = r
            summ = {"n_agents": len(per)}
            for k in EST:
                o = np.array([x[k]["obs"] for x in per.values()])
                e = np.array([x[k]["obs"] - x[k]["null_mean"] for x in per.values()])
                p = np.array([x[k]["p"] for x in per.values()])
                summ[k] = {"median_obs": float(np.nanmedian(o)), "median_excess": float(np.nanmedian(e)),
                           "median_null_mean": float(np.nanmedian([x[k]["null_mean"] for x in per.values()])),
                           "frac_above_null": float(np.mean(p <= 0.05)),
                           "frac_obs_positive": float(np.mean(o > 0))}
            rec["variants"][VN[vi]] = {"summary": summ, "agents": per}
        # scaffold share on excess, per agent present in V1 and V5 with a positive V1 excess
        if "act_all" in rec["variants"] and "act_agent_b3" in rec["variants"]:
            a1, a5 = rec["variants"]["act_all"]["agents"], rec["variants"]["act_agent_b3"]["agents"]
            for k in EST:
                sh = []
                for a in a1:
                    if a in a5:
                        e1 = a1[a][k]["obs"] - a1[a][k]["null_mean"]
                        e5 = a5[a][k]["obs"] - a5[a][k]["null_mean"]
                        if e1 > 0.01:
                            sh.append(1 - e5 / e1)
                rec[f"scaffold_share_excess_{k}"] = float(np.median(sh)) if sh else None
                shr = [1 - a5[a][k]["obs"] / a1[a][k]["obs"] for a in a1 if a in a5 and a1[a][k]["obs"] > 0.01]
                rec[f"scaffold_share_raw_{k}"] = float(np.median(shr)) if shr else None
        if rec["variants"]:
            out.append(rec)
        s1 = rec["variants"].get("act_all", {}).get("summary", {})
        print(g, rec["regime"], {k: (round(s1[k]["median_obs"], 3), round(s1[k]["median_excess"], 3), round(s1[k]["frac_above_null"], 2))
                                 for k in EST if k in s1}, flush=True)
    jdump(RE / "levels_flipnull.json", {"R": R, "periods": out})
    return out


# ============================================================================ 4. old vs new comparison
def _rd(p):
    return json.loads(p.read_text()) if p.exists() else None


def compare():
    o_res, n_res = _rd(OLD / "replication/results.json"), _rd(RE / "replication/results.json")
    o_ph, n_ph = _rd(OLD / "replication/posthoc.json"), _rd(RE / "replication/posthoc.json")
    o_nat = {k: _rd(OLD / f"native/{k}.json") for k in ("NE14", "NE43", "NE40", "G51")}
    n_nat = {k: _rd(RE / f"native/{k}.json") for k in ("NE14", "NE43", "NE40", "G51")}
    o_syn, n_syn = _rd(OLD / "synthetic/summary.json"), _rd(RE / "synthetic/summary.json")
    lev = _rd(RE / "levels_flipnull.json")
    o_pts, n_pts = _rd(OLD / "replication/period_points.json"), _rd(RE / "replication/period_points.json")
    C = {}

    def both(name, f):
        try:
            a = f(o_res, o_ph, o_nat, o_syn, o_pts)
        except Exception as e:  # noqa: BLE001
            a = f"ERR {e}"
        try:
            b = f(n_res, n_ph, n_nat, n_syn, n_pts)
        except Exception as e:  # noqa: BLE001
            b = f"ERR {e}"
        C[name] = {"old": a, "new": b}

    for v in ("act_all", "act_agent_b3", "act_agent"):
        for cls in ("scaffold_tool:all", "scaffold_tool:no_NE14b", "scaffold_prompt:all", "goal:all", "roster:all", "room:all",
                    "operator:all"):
            both(f"class {cls} {v}", lambda r, *_a, v=v, cls=cls: {k: r["class_tests"][v][cls].get(k) for k in
                                                                     ("n", "mean_abs_t", "p_random_date", "p_placebo_class")}
                 if cls in r["class_tests"][v] else None)
        both(f"P3 tool-goal {v}", lambda r, *_a, v=v: r["class_tests"][v].get("P3_tool_minus_goal"))
        both(f"A3 hits {v}", lambda r, ph, *_a, v=v: {c: (x["hits"], x["n"]) for c, x in ph["amendment3_hits"][v].items()})
        both(f"blind {v}", lambda r, *_a, v=v: {"scaffold_tool": r["blind"][v]["classes"].get("scaffold_tool"),
                                                 "goal": r["blind"][v]["classes"].get("goal"),
                                                 "n_cp": len(r["blind"][v]["change_points"]),
                                                 "n_unexplained": r["blind"][v]["n_unexplained"],
                                                 "unexplained_dates": [c["pt_date"] for c in r["blind"][v]["change_points"] if c["unexplained"]],
                                                 "max_fpos_dev_unexplained": max([abs(c["fpos"] - 0.5) for c in r["blind"][v]["change_points"] if c["unexplained"]] or [None])})
        both(f"sign S {v}", lambda r, ph, *_a, v=v: ph["sign"][v].get("scaffold_tool"))
        both(f"magnitude M {v}", lambda r, ph, *_a, v=v: ph["magnitude"][v].get("scaffold_tool"))
        both(f"null spread {v}", lambda r, ph, *_a, v=v: ph["null_spread"][v])
    for v in ("act_all", "act_agent_b3", "act_agent", "coarse_all", "coarse_agent_b3"):
        both(f"families {v}", lambda r, *_a, v=v: {k: r["families"][v][k] for k in ("mean_eta2", "p_stratified")} | {
            "n_periods": len(r["families"][v]["periods"]), "n_p05": sum(p["p"] < 0.05 for p in r["families"][v]["periods"])})
    both("holm", lambda r, ph, *_a: ph["holm_primaries"])
    both("synthetic null sd / tau", lambda r, ph, n, s, *_a: {"null_t_sd": s["fine"]["null_t_sd"]["newton"],
                                                               "tau95": s["fine"]["tau95"]["newton"]} if s else None)
    for tmpl in ("fine", "coarse"):
        both(f"synthetic {tmpl}", lambda r, ph, n, s, *_a, t=tmpl: {sc: (x["newton"] if "newton" in x else
                                                                          {kk: x[kk]["newton"] for kk in ("with_scaffold", "agent_cut")})
                                                                     for sc, x in s[t]["scen"].items()} if s else None)
    both("synthetic detector", lambda r, ph, n, s, *_a: s["detector_fine"] if s else None)
    # natives
    for v in ("act_all", "coarse_all", "act_agent_b3", "coarse_agent", "coarse_agent_b3", "act_agent"):
        both(f"NE14 {v}", lambda r, ph, n, *_a, v=v: {k: n["NE14"]["variants"][v][k] for k in ("n", "dbar", "t", "fpos", "rel", "p_tuesday_placebo", "n_placebo")})
    both("NE14 carriage", lambda r, ph, n, *_a: {k: n["NE14"][k] for k in n["NE14"] if k.startswith("carriage")})
    for d_ in ("k3", "fri_only", "k5"):
        for v in ("act_all", "act_agent_b3"):
            both(f"NE43 {d_} {v}", lambda r, ph, n, *_a, d_=d_, v=v: {
                "t": n["NE43"]["designs"][d_][v]["t"], "rel": n["NE43"]["designs"][d_][v]["rel"],
                "p": n["NE43"]["designs"][d_][v]["p_friday_placebo"],
                "idle_rel": n["NE43"]["designs"][d_][v]["idle_sector"]["rel"],
                "idle_p": n["NE43"]["designs"][d_][v]["idle_sector"]["p_friday_placebo"]})
    both("NE40 EP at D40", lambda r, ph, n, *_a: {k: n["NE40"]["ep_at_D40_act_all"][k] for k in ("n", "t", "rel", "p_placebo")})
    both("NE40 search sector", lambda r, ph, n, *_a: {k: n["NE40"]["search_sector_at_D40"][k] for k in ("n", "t", "p_placebo")})
    for v in ("act_all", "act_agent_b3"):
        both(f"G51 {v}", lambda r, ph, n, *_a, v=v: {k: n["G51"]["variants"][v][k] for k in ("hits", "enrichment", "p_shift", "trend_spearman", "trend_p")} | {
            "unexplained": [(c["pt_date"], round(c["fpos"], 2), c["all_providers_same_sign"]) for c in n["G51"]["variants"][v]["change_points"] if c["unexplained"]]})
    # period points
    for v in ("act_all", "act_agent_b3"):
        both(f"period median EP {v}", lambda r, ph, n, s, p, v=v: {pp["goal_no"]: round(pp["median_ep"], 4) for pp in p if pp["variant"] == v})
    # per-period kickoff and scaffold verdict ingredients (event p against the Amendment-3 null)
    for path, key in ((OLD, "old"), (RE, "new")):
        f = path / "replication/events_posthoc.parquet"
        if f.exists():
            es = pl.read_parquet(f)
            k = es.filter(pl.col("variant").is_in(["act_all", "act_agent_b3"])).select(
                "goal_no", "variant", "refs", "cls", "day0", "newton_t", "p_n2")
            C.setdefault("events_posthoc", {})[key] = k.to_dicts()
    if lev:
        C["levels_flipnull"] = [{"goal_no": p["goal_no"], "regime": p["regime"],
                                 **{f"{v}:{k}": p["variants"][v]["summary"][k] for v in p["variants"] for k in EST},
                                 **{kk: p.get(kk) for kk in p if kk.startswith("scaffold_share")}} for p in lev["periods"]]
    jdump(RE / "compare.json", C)
    for k, v in C.items():
        if k in ("events_posthoc", "levels_flipnull") or k.startswith("period median"):
            continue
        print(f"{k}\n   old {v['old']}\n   new {v['new']}")
    return C


# ============================================================================ 5. per-period verdicts (replication rule)
def period_verdicts():
    """Re-apply write_period_folders.py's verdict rule to both event tables (V1, Amendment-3 null)."""
    out = {}
    for path, key in ((OLD, "old"), (RE, "new")):
        es = pl.read_parquet(path / "replication/events_posthoc.parquet").filter(pl.col("variant") == "act_all")
        for g in sorted(es["goal_no"].unique().to_list()):
            ev = es.filter(pl.col("goal_no") == g)
            kick = ev.filter(pl.col("cls") == "goal")
            scaf = ev.filter(pl.col("cls").is_in(["scaffold_tool", "scaffold_prompt", "scaffold_family"]) & pl.col("newton_t").is_not_nan())
            kick_hit = bool(kick.height and kick["p_n2"][0] is not None and kick["p_n2"][0] < 0.05)
            hits = int((scaf["p_n2"] < 0.05).sum()) if scaf.height else 0
            if scaf.height == 0 and kick.height == 0:
                vd = "n/a"
            elif scaf.height:
                vd = "supported" if (hits == scaf.height and not kick_hit) else ("mixed" if hits else "failed")
            else:
                vd = "failed" if kick_hit else "descriptive"
            out.setdefault(int(g), {})[key] = {"verdict": vd, "kick_t": kick["newton_t"][0] if kick.height else None,
                                               "kick_p": kick["p_n2"][0] if kick.height else None,
                                               "n_scaf": scaf.height, "scaf_hits": hits}
    ch = {g: v for g, v in out.items() if v.get("old", {}).get("verdict") != v.get("new", {}).get("verdict")}
    print("period verdict changes (replication rule):", {g: (v.get("old", {}).get("verdict"), v.get("new", {}).get("verdict")) for g, v in ch.items()})
    jdump(RE / "period_verdicts.json", {"all": out, "changed": ch})
    return out, ch


# ============================================================================ 6. per_period_estimates rows
def estimates():
    import estimates as E
    lev = _rd(RE / "levels_flipnull.json")
    o_pts, n_pts = _rd(OLD / "replication/period_points.json"), _rd(RE / "replication/period_points.json")
    pv = _rd(RE / "period_verdicts.json")["all"]
    o_fam, n_fam = _rd(OLD / "replication/results.json")["families"], _rd(RE / "replication/results.json")["families"]
    days = pl.read_parquet(L.DATA / "days.parquet").filter(~pl.col("holdout"))
    span = {g: (min(d), max(d)) for g, d in days.group_by("goal_no").agg(pl.col("pt_date")).iter_rows()}
    TAG = " [held-out Newton, per-column ridge; post hoc ep_newton recheck 2026-10-04]"
    LEG = " [legacy cross-product Newton, round 1]"
    CH = {"act_all": "fine actions, all records (V1)", "act_agent_b3": "fine actions, agent-only + burn-in 3 (V5)",
          "coarse_all": "coarse states, all records (V3)", "coarse_agent_b3": "coarse states, agent-only + burn-in 3 (V6)"}
    rows = []

    def base(g, src):
        f, l_ = span[g]
        u = E.map_unit(g, f, l_) or f"G{g:02d}"
        return dict(period_unit=u, goal_no=g, role="replication", first_day=f, last_day=l_, source=src)

    for pts, tag, ph, src in ((o_pts, LEG, False, "data/processed/H56-ep-platform-fingerprint/replication/period_points.json"),
                              (n_pts, TAG, True, "data/processed/H56-ep-platform-fingerprint/recheck_epfix/replication/period_points.json")):
        for p in pts:
            if p["variant"] not in CH:
                continue
            vals = np.array([x for x in p["agents"].values() if finite(x)])
            rows.append(base(p["goal_no"], src) | dict(
                statistic="ep_rate_median_agent", channel=CH[p["variant"]], estimate=p["median_ep"],
                ci_lo=float(np.percentile(vals, 25)) if len(vals) else None, ci_hi=float(np.percentile(vals, 75)) if len(vals) else None,
                ci_kind="percentile", ci_level=0.5, n=p["n_agents"], n_kind="agents (>= 300 transitions, >= 2 days)",
                unit_local="nats/transition", method="median over agents of the Newton bound on antisymmetrized transition indicators, day folds" + tag,
                null="none (raw bound; interquartile range over agents)", post_hoc=ph,
                notes="raw magnitudes are not comparable between the two estimators (the held-out bound is ridge-shrunk)"))
    for p in lev["periods"]:
        g = p["goal_no"]
        for v, x in p["variants"].items():
            if v not in CH:
                continue
            for k, tag in (("legacy", LEG.replace("round 1", "post hoc recompute 2026-10-04")), ("heldout", TAG)):
                s = x["summary"][k]
                b = base(g, "data/processed/H56-ep-platform-fingerprint/recheck_epfix/levels_flipnull.json")
                rows.append(b | dict(statistic="ep_excess_over_flip_null_median_agent", channel=CH[v], estimate=s["median_excess"],
                                     ci_kind="none", n=x["summary"]["n_agents"], n_kind="agents", unit_local="nats/transition",
                                     method="median over agents of Newton EP minus the block-flip null mean, day folds" + tag,
                                     null=f"block-flip, (day, quarter) blocks, R={lev['R']}", post_hoc=True))
                rows.append(b | dict(statistic="frac_agents_ep_above_null", channel=CH[v], estimate=s["frac_above_null"],
                                     ci_kind="none", n=x["summary"]["n_agents"], n_kind="agents",
                                     method="share of agents with Newton EP above the block-flip null p95 (p <= 0.05)" + tag,
                                     null=f"block-flip, (day, quarter) blocks, R={lev['R']}", post_hoc=True))
        for k, tag in (("legacy", LEG.replace("round 1", "post hoc recompute 2026-10-04")), ("heldout", TAG)):
            if p.get(f"scaffold_share_excess_{k}") is not None:
                rows.append(base(g, "data/processed/H56-ep-platform-fingerprint/recheck_epfix/levels_flipnull.json") | dict(
                    statistic="ep_scaffold_share", channel="fine actions (V1 vs V5)", estimate=p[f"scaffold_share_excess_{k}"],
                    ci_kind="none", n=p["variants"]["act_all"]["summary"]["n_agents"], n_kind="agents",
                    method="median over agents of 1 - excess(V5)/excess(V1), excess over the block-flip null" + tag,
                    null="block-flip", post_hoc=True))
    for fam, tag, ph, src in ((o_fam, LEG, False, "data/processed/H56-ep-platform-fingerprint/replication/results.json"),
                              (n_fam, TAG, True, "data/processed/H56-ep-platform-fingerprint/recheck_epfix/replication/results.json")):
        for v in ("act_all", "act_agent_b3"):
            for p in fam[v]["periods"]:
                rows.append(base(p["goal_no"], src) | dict(
                    statistic="family_eta2_ep", channel=CH[v], estimate=p["eta2"], ci_kind="none", n=p["n"],
                    n_kind="agents in labs with >= 2 agents", method="eta^2 of count-matched per-agent Newton EP by lab" + tag,
                    null=f"within-period lab permutation (2,000); p {p['p']:.4f}, null mean {p['null_mean']:.3f}", post_hoc=ph))
    for g, v in pv.items():
        g = int(g)
        for key, tag, ph, src in (("old", LEG, False, "data/processed/H56-ep-platform-fingerprint/replication/events_posthoc.parquet"),
                                  ("new", TAG, True, "data/processed/H56-ep-platform-fingerprint/recheck_epfix/replication/events_posthoc.parquet")):
            x = v.get(key)
            if not x or x["kick_t"] is None or g not in span:
                continue
            rows.append(base(g, src) | dict(
                statistic="kickoff_ep_event_t", channel=CH["act_all"], estimate=x["kick_t"], ci_kind="none",
                method="within-agent count-matched Newton EP change, 3 + 3 non-holdout days, t over agents" + tag,
                null=f"Amendment-3 same-regime day pool; p {x['kick_p']:.3f}" if finite(x["kick_p"]) else "Amendment-3 pool",
                post_hoc=ph))
    rows = [r for r in rows if r["goal_no"] in span]
    out = E.write_estimates(rows, hypothesis="H56")
    print(out.height, "rows written")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify")
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--levels", action="store_true")
    ap.add_argument("--compare", action="store_true")
    ap.add_argument("--verdicts", action="store_true")
    ap.add_argument("--estimates", action="store_true")
    a = ap.parse_args()
    RE.mkdir(parents=True, exist_ok=True)
    if a.verify:
        sys.exit(0 if verify(a.verify) else 1)
    if a.synthetic:
        synthetic()
    if a.levels:
        levels()
    if a.compare:
        compare()
    if a.verdicts:
        period_verdicts()
    if a.estimates:
        estimates()
