"""H90 exploratory round 1: replication (G37-G42, G44, G51 head; behavior, talk, activity) and natives
(N1 G38 rooms; N2 G51 full pairwise talk; N3 NE43 nudger off).

  uv run python hypotheses/H90-collective-entropy-production/analysis/run.py [--period G38] [--natives-only]
Reads data/processed/H90-collective-entropy-production/<G..>/grid_*.npz (scheme/build.py), writes <G..>/results.json,
results/summary.json, per-period estimates (infra/shared/estimates.py) and figures/.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h90lib as L  # noqa: E402
import build as B  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
import estimates as EST  # noqa: E402

GOALS = B.GOALS
CHANNELS = ("behavior", "talk", "activity")
SETS = L.DEFAULT_SETS
R_SHIFT = {"behavior": 50, "talk": 100, "activity": 50}
R_FLIP = 20
NBOOT = 200
# H50 per-period talk J1 (card table, "Results by goal period"; read-only)
H50_J1 = {37: 0.097, 38: 0.009, 39: 0.026, 40: 0.010, 41: 0.024, 42: 0.022, 44: 0.025, 51: 0.016}
SIZE_CLASS = {37: "S40", 38: "S38", 39: "S40", 40: "S40", 41: "S40", 42: "S40", 44: "S40", 51: "S51"}
KEYS = ("Sigma1", "sum_sigma_i", "Sigma1_all", "coll_all", "coll_named", "coll_unnamed", "addr", "rho_coll")


def synthetic_power() -> dict:
    f = L.OUTD / "synthetic/summary.parquet"
    if not f.exists():
        return {}
    s = pl.read_parquet(f)
    out = {}
    for r in s.iter_rows(named=True):
        out[(r["size"], r["channel"], r["scen"])] = r
    f2 = L.OUTD / "synthetic/effect_power.parquet"          # A3 (post hoc): power at the G51 effect size, J = 0.25
    if f2.exists():
        e = pl.read_parquet(f2).filter(pl.col("J") == 0.25).group_by("size").agg((pl.col("addr_p_shift") < 0.05).mean().alias("P"))
        for r in e.iter_rows(named=True):
            out[(r["size"], "talk", "G51effect")] = {"P_addr_shift": r["P"]}
    return out


def channel_result(goal: int, ch: str, rng, sizematch: bool = True) -> dict:
    days, agents = B.load_period(goal, ch)
    n = len(agents)
    if len(days) < 3:
        return {"channel": ch, "n_days": len(days), "status": "n/a (< 3 trimmed days)"}
    w = B.weights(goal, agents)
    t0 = time.time()
    obs, stats, lay, folds = L.period_estimate(days, ch, n, w, SETS, per_agent=True)
    _, Gs = L.build_stats(days, ch, n, w, SETS, keep_G=True)
    exact = {nm: L.exact_dual_cf(Gs, cols, folds, block=lay["block"]) for nm, cols in
             (("single", lay["single"]), ("single+all", np.r_[lay["single"], lay["all"]]),
              ("single+named", np.r_[lay["single"], lay["named"]]), ("single+unnamed", np.r_[lay["single"], lay["unnamed"]]))}
    exact["coll_all"] = exact["single+all"] - exact["single"]
    exact["coll_named"] = exact["single+named"] - exact["single"]
    exact["coll_unnamed"] = exact["single+unnamed"] - exact["single"]
    del Gs
    boot = L.bootstrap(stats, lay, folds, n, SETS, NBOOT, rng, per_agent=False)
    sh = L.null_dist(days, ch, n, w, "shift", R_SHIFT[ch], rng, folds=folds)
    fl = L.null_dist(days, ch, n, w, "flip", R_FLIP, rng, folds=folds)
    nbar = float(np.mean([len(d["agents"]) for d in days]))
    steps = int(sum(d["X"].shape[1] for d in days))
    res = {"channel": ch, "n_days": len(days), "n_agents": n, "nbar": nbar, "steps": steps, "obs": obs, "ci": boot,
           "exact_dual": exact, "n_named_pairs": int((w > 0).sum()), "n_msgs_naming": float(w.sum()),
           "per_agent_hour": {k: L.per_agent_hour(obs[k], ch, nbar) for k in ("Sigma1", "coll_all", "coll_named", "coll_unnamed")}}
    for k in ("coll_all", "coll_named", "coll_unnamed", "addr", "Sigma1"):
        v = [x[k] for x in sh]
        res[f"shift_{k}"] = {"p": L.pval(obs[k], v), "q95": float(np.nanpercentile(v, 95)), "mean": float(np.nanmean(v))}
        v = [x[k] for x in fl]
        res[f"flip_{k}"] = {"p": L.pval(obs[k], v), "q95": float(np.nanpercentile(v, 95)), "mean": float(np.nanmean(v)),
                            "sd": float(np.nanstd(v))}
    # sensitivity: drop the period's first active day (kickoff day)
    if len(days) >= 4:
        o2, *_ = L.period_estimate(days[1:], ch, n, w, SETS, per_agent=False)
        res["no_kickoff_day"] = {k: o2[k] for k in ("coll_all", "coll_named", "coll_unnamed", "Sigma1")}
    # size-matched: random subsets of 12 agents (agents present on >= half the days)
    if sizematch and n > 12:
        cnt = np.bincount(np.concatenate([d["agents"] for d in days]), minlength=n)
        elig = np.nonzero(cnt >= len(days) / 2)[0]
        vals = []
        for _ in range(20):
            sub = np.sort(rng.choice(elig, min(12, len(elig)), replace=False))
            mp = {g: k for k, g in enumerate(sub)}
            dd = []
            for d in days:
                keep = np.isin(d["agents"], sub)
                if keep.sum() >= 2:
                    dd.append({**d, "agents": np.array([mp[g] for g in d["agents"][keep]]), "X": d["X"][keep]})
            o, *_ = L.period_estimate(dd, ch, len(sub), w[np.ix_(sub, sub)], SETS, per_agent=False)
            vals.append({k: o[k] for k in ("coll_all", "coll_named", "Sigma1")})
        res["size12"] = {k: float(np.nanmedian([v[k] for v in vals])) for k in vals[0]}
    res["secs"] = time.time() - t0
    return res


def verdict(per_ch: dict, power: dict, goal: int) -> tuple[str, str]:
    """Amendment A1: the coupling test is the address contrast (talk) against the block-shift null; sigma_coll over the
    shift null only shows cross-agent lead-lag (a lagged field passes it)."""
    talk = per_ch.get("talk", {})
    if "obs" not in talk:
        return "n/a", "fewer than 3 trimmed days"
    p_addr = talk["shift_addr"]["p"]
    part1 = p_addr < 0.05 and talk["obs"]["addr"] > 0
    ok2 = []
    for ch in ("behavior", "activity"):
        r = per_ch.get(ch, {})
        if "obs" not in r:
            continue
        rho = r["obs"]["rho_coll"]
        at_null = r["shift_coll_all"]["p"] >= 0.05 and r["shift_addr"]["p"] >= 0.05
        ok2.append(at_null or (np.isfinite(rho) and rho < 0.1))
    part2 = all(ok2) if ok2 else False
    pw1 = power.get((SIZE_CLASS[goal], "talk", "C1"), {}).get("P_addr_shift", np.nan)
    pw = power.get((SIZE_CLASS[goal], "talk", "G51effect"), {}).get("P_addr_shift", pw1)   # A3: power at the G51 effect
    any_ll = any(per_ch[c]["shift_coll_all"]["p"] < 0.05 or per_ch[c]["shift_coll_named"]["p"] < 0.05
                 for c in CHANNELS if "obs" in per_ch.get(c, {}))
    if part1 and part2:
        return "supported", f"talk address contrast over the shift null (p {p_addr:.3f}); small collective share elsewhere"
    if not part1 and not any_ll:
        if np.isfinite(pw) and pw >= 0.8:
            return "failed", f"no address contrast and no lead-lag over the shift null; talk power at the G51 effect {pw:.2f}"
        return "mixed", (f"underpowered: nothing over the shift null; talk power at the G51 effect size {pw:.2f} "
                         f"(at J = 1: {pw1:.2f}; 'failed' under the A1 rule)")
    return "mixed", (f"address contrast {'holds' if part1 else 'fails'} (p {p_addr:.3f}); lead-lag over shift null "
                     f"{'in some channel' if any_ll else 'nowhere'}; small-share part {'holds' if part2 else 'fails'}")


# ------------------------------------------------------------------------------------------------ natives
def native_g38_rooms(rng) -> dict:
    out = {}
    for ch in ("talk", "behavior"):
        days, agents = B.load_period(38, ch)
        rbd = B.rooms_by_day(38, agents, days)
        for d in days:
            d["room"] = rbd[d["date"]]
        n = len(agents)
        w = B.weights(38, agents)
        sets = ("same", "cross")
        obs, stats, lay, folds = L.period_estimate(days, ch, n, w, sets, per_agent=False)
        o = {"same": obs["coll_same"], "cross": obs["coll_cross"]}
        sh = L.null_dist(days, ch, n, w, "shift", R_SHIFT[ch], rng, sets, folds=folds)
        o["p_same"] = L.pval(obs["coll_same"], [x["coll_same"] for x in sh])
        o["p_cross"] = L.pval(obs["coll_cross"], [x["coll_cross"] for x in sh])
        o["q95_same"] = float(np.nanpercentile([x["coll_same"] for x in sh], 95))
        o["q95_cross"] = float(np.nanpercentile([x["coll_cross"] for x in sh], 95))
        ci = L.bootstrap(stats, lay, folds, n, sets, NBOOT, rng)
        o["ci_same"], o["ci_cross"] = ci["coll_same"], ci["coll_cross"]
        o["rooms_per_day"] = {d["date"]: sorted(set(int(x) for x in d["room"][d["agents"]])) for d in days}
        out[ch] = o
    t = out["talk"]
    v = "supported" if (t["same"] > t["cross"] and t["p_cross"] >= 0.05) else (
        "failed" if t["same"] <= t["cross"] else "mixed")
    out["verdict"] = v
    return out


def native_g51_pairwise(rng) -> dict:
    days, agents = B.load_period(51, "talk")
    n = len(agents)
    w = B.weights(51, agents)
    cnt = np.bincount(np.concatenate([d["agents"] for d in days]), minlength=n)
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n) if cnt[i] >= 5 and cnt[j] >= 5]
    lay = L.layout("talk", n, [], len(pairs))
    stats, Gs = L.build_stats(days, "talk", n, w, (), pairs=pairs, keep_G=True)
    folds = L.fold_ids(len(days))
    sub = {"single": lay["single"], "single+pairs": np.r_[lay["single"], lay["pairs"]]}
    obs = L.newton_from_stats(stats, sub, folds, block=lay["block"])
    coll = obs["single+pairs"] - obs["single"]
    G = np.concatenate(Gs).astype(np.float64)
    del Gs
    cols = np.r_[lay["single"], lay["pairs"]]
    K = np.cov(G[:, cols], rowvar=False)
    blk = lay["block"][cols]
    dK = np.clip(np.diag(K), 0, None)
    K = K + L.RIDGE_HO * np.diag(dK + np.array([dK[blk == b].mean() for b in blk]))
    th = 2 * np.linalg.solve(K, G[:, cols].mean(0))[len(lay["single"]):]
    # theta_ij > 0: i follows j (g_ij = s_i' s_j - s_i s_j'); naming j -> i predicts i follows j
    dirw = np.array([w[j, i] - w[i, j] for i, j in pairs])
    tot = np.array([w[j, i] + w[i, j] for i, j in pairs])
    m = np.abs(dirw) >= 3
    agree = float((np.sign(th[m]) == np.sign(dirw[m])).mean()) if m.any() else np.nan
    from scipy.stats import spearmanr
    rs = float(spearmanr(np.abs(th), tot).statistic)
    null_ag, null_rs, null_coll = [], [], []
    for _ in range(20):
        dd = L.block_shift(days, L.BLOCK["talk"], rng)
        st2, G2 = L.build_stats(dd, "talk", n, w, (), pairs=pairs, keep_G=True)
        o2 = L.newton_from_stats(st2, sub, folds, block=lay["block"])
        null_coll.append(o2["single+pairs"] - o2["single"])
        G2 = np.concatenate(G2).astype(np.float64)
        K2 = np.cov(G2[:, cols], rowvar=False)
        d2 = np.clip(np.diag(K2), 0, None)
        K2 = K2 + L.RIDGE_HO * np.diag(d2 + np.array([d2[blk == b].mean() for b in blk]))
        t2 = 2 * np.linalg.solve(K2, G2[:, cols].mean(0))[len(lay["single"]):]
        null_ag.append(float((np.sign(t2[m]) == np.sign(dirw[m])).mean()) if m.any() else np.nan)
        null_rs.append(float(spearmanr(np.abs(t2), tot).statistic))
    out = {"n_pairs": len(pairs), "n_directed_pairs": int(m.sum()), "coll_pairs": coll, "Sigma1": obs["single"],
           "coll_pairs_p_shift": L.pval(coll, null_coll), "coll_pairs_q95": float(np.nanpercentile(null_coll, 95)),
           "sign_agree": agree, "sign_agree_null_q95": float(np.nanpercentile(null_ag, 95)),
           "sign_agree_null_mean": float(np.nanmean(null_ag)), "spearman_abs_theta_w": rs,
           "spearman_null_q95": float(np.nanpercentile(null_rs, 95))}
    ok1 = np.isfinite(agree) and agree >= 0.6 and agree > out["sign_agree_null_q95"]
    ok2 = rs > 0.1
    out["verdict"] = "supported" if (ok1 and ok2) else ("failed" if not (ok1 or ok2) else "mixed")
    return out


def native_ne43(rng) -> dict:
    days, agents = B.load_period(51, "talk")
    n = len(agents)
    w = B.weights(51, agents)
    dates = [d["date"] for d in days]

    def ratio(bnd: str):
        before = [d for d in days if d["date"] < bnd][-10:]
        after = [d for d in days if d["date"] >= bnd][:10]
        k = min(len(before), len(after))
        if k < 4:
            return None
        before, after = before[-k:], after[:k]
        ob, *_ = L.period_estimate(before, "talk", n, w, SETS, per_agent=False)
        oa, *_ = L.period_estimate(after, "talk", n, w, SETS, per_agent=False)
        nb = np.mean([len(d["agents"]) for d in before])
        na = np.mean([len(d["agents"]) for d in after])
        out = {"k_days": k}
        for key in ("coll_all", "coll_named"):
            b_, a_ = L.per_agent_hour(ob[key], "talk", nb), L.per_agent_hour(oa[key], "talk", na)
            out[key] = {"before": b_, "after": a_, "ratio": a_ / b_ if b_ > 0 and a_ > -np.inf else np.nan,
                        "diff": a_ - b_}
        return out
    main = ratio("2026-08-21")
    plac = {b: ratio(b) for b in ("2026-07-20", "2026-07-27", "2026-08-04", "2026-08-28")}
    plac = {b: v for b, v in plac.items() if v is not None}
    res = {"boundary": "2026-08-21", "main": main, "placebos": plac, "dates_used": [dates[0], dates[-1]]}
    if main is not None and plac:
        d = [v["coll_named"]["diff"] for v in plac.values()]
        res["placebo_diff_range"] = [float(min(d)), float(max(d))]
        md = main["coll_named"]["diff"]
        res["verdict"] = "supported" if min(d) <= md <= max(d) else ("failed" if md < min(d) else "mixed")
    else:
        res["verdict"] = "n/a"
    return res


# ------------------------------------------------------------------------------------------------ estimates
def estimate_rows(goal: int, per_ch: dict) -> list:
    rows = []
    unit = str(goal) if goal not in (38, 44, 51) else f"G{goal:02d}"
    for ch, r in per_ch.items():
        if "obs" not in r:
            continue
        for stat, key in (("coll_ep_sigma_coll_all", "coll_all"), ("coll_ep_sigma_coll_named", "coll_named"),
                          ("coll_ep_sigma_coll_unnamed", "coll_unnamed"), ("coll_ep_address_contrast", "addr"),
                          ("coll_ep_sigma1_single", "Sigma1")):
            lo, hi = r["ci"][key]
            rows.append({"period_unit": unit, "goal_no": goal, "statistic": stat, "channel": ch,
                         "estimate": float(r["obs"][key]), "ci_lo": lo, "ci_hi": hi, "ci_level": 0.95,
                         "ci_kind": "percentile", "n": float(r["n_days"]), "n_kind": "days",
                         "method": "held-out Newton AIK bound (per-column ridge c=1), day folds; nats per system step; "
                                   "day bootstrap B=200",
                         "null": f"per-agent 30-min block shift in the DQ8 trimmed window (p={r.get('shift_' + key, {}).get('p', float('nan')):.3f})",
                         "role": "replication", "status": "ok",
                         "source": f"data/processed/H90-collective-entropy-production/G{goal:02d}/results.json"})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", default=None)
    ap.add_argument("--natives-only", action="store_true")
    ap.add_argument("--no-natives", action="store_true")
    a = ap.parse_args()
    rng = np.random.default_rng(20261004)
    power = synthetic_power()
    goals = [int(a.period[1:])] if a.period else GOALS
    summary = {}
    allrows = []
    if not a.natives_only:
        for g in goals:
            per_ch = {}
            for ch in CHANNELS:
                per_ch[ch] = channel_result(g, ch, rng)
                r = per_ch[ch]
                if "obs" in r:
                    print(g, ch, "days", r["n_days"], "N", r["n_agents"], {k: round(r["obs"][k], 5) for k in KEYS},
                          "p_shift all/named", round(r["shift_coll_all"]["p"], 3), round(r["shift_coll_named"]["p"], 3),
                          f"{r['secs']:.0f}s", flush=True)
            v, why = verdict(per_ch, power, g)
            res = {"goal": g, "channels": per_ch, "verdict": v, "why": why, "h50_J1": H50_J1.get(g)}
            L.write_json(L.OUTD / f"G{g:02d}" / "results.json", res)
            summary[g] = res
            allrows += estimate_rows(g, per_ch)
        if allrows:
            EST.write_estimates(allrows, hypothesis="H90")
    if not a.no_natives and not a.period:
        nat = {"N1_G38_rooms": native_g38_rooms(rng)}
        print("N1", nat["N1_G38_rooms"], flush=True)
        nat["N2_G51_pairwise"] = native_g51_pairwise(rng)
        print("N2", nat["N2_G51_pairwise"], flush=True)
        nat["N3_NE43"] = native_ne43(rng)
        print("N3", nat["N3_NE43"], flush=True)
        L.write_json(L.OUTD / "results" / "natives.json", nat)
        nrows = []
        t = nat["N1_G38_rooms"]["talk"]
        for key in ("same", "cross"):
            nrows.append({"period_unit": "G38", "goal_no": 38, "statistic": f"coll_ep_sigma_coll_{key}_room", "channel": "talk",
                          "estimate": float(t[key]), "ci_lo": t[f"ci_{key}"][0], "ci_hi": t[f"ci_{key}"][1], "ci_level": 0.95,
                          "ci_kind": "percentile", "n": 16.0, "n_kind": "days",
                          "method": "held-out Newton AIK bound, partner field restricted to same/other room; day bootstrap",
                          "null": f"block shift p={t['p_' + key]:.3f}", "role": "native", "status": "ok",
                          "source": "data/processed/H90-collective-entropy-production/results/natives.json"})
        p2 = nat["N2_G51_pairwise"]
        nrows.append({"period_unit": "G51", "goal_no": 51, "statistic": "coll_ep_theta_sign_agreement_naming", "channel": "talk",
                      "estimate": float(p2["sign_agree"]), "ci_lo": None, "ci_hi": None, "ci_kind": "none",
                      "n": float(p2["n_directed_pairs"]), "n_kind": "pairs",
                      "method": "full pairwise AIK theta (ridge), sign vs naming direction over pairs with |w_ji - w_ij| >= 3",
                      "null": f"block shift q95={p2['sign_agree_null_q95']:.3f}", "role": "native", "status": "ok",
                      "source": "data/processed/H90-collective-entropy-production/results/natives.json"})
        EST.write_estimates(nrows, hypothesis="H90")
    if summary:
        from scipy.stats import spearmanr
        gs = [g for g in summary if "obs" in summary[g]["channels"].get("talk", {})]
        v_nam = [summary[g]["channels"]["talk"]["per_agent_hour"]["coll_named"] for g in gs]
        v_all = [summary[g]["channels"]["talk"]["per_agent_hour"]["coll_all"] for g in gs]
        j1 = [H50_J1[g] for g in gs]
        summary["across"] = {"goals": gs, "spearman_named_pah_vs_H50_J1": float(spearmanr(v_nam, j1).statistic),
                             "spearman_all_pah_vs_H50_J1": float(spearmanr(v_all, j1).statistic),
                             "n_supported": sum(summary[g]["verdict"] == "supported" for g in gs)}
        print("ACROSS", summary["across"], flush=True)
        L.write_json(L.OUTD / "results" / "summary.json", summary)


if __name__ == "__main__":
    main()
