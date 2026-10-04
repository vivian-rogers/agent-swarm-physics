"""H10 real data: the free -> assigned pair tests (P1-P4), per pair, then combined across pairs (meta-analysis only).

Primary pairs #11->#12a, #16->#17, #37->#38a; secondary #3->#4a, #5->#6a. Non-holdout only (h10data.guard).
Outputs: data/processed/H10-goals-are-legendre-pushes/NE34/pairs.json (+ robustness.json), figures in
hypotheses/H10-goals-are-legendre-pushes/NE34/figures/.

Usage: uv run python run_pairs.py [--boot 1000] [--skip-robust]
"""
from __future__ import annotations

import argparse
import time

import numpy as np

import h10data
from h10data import DATA, PAIRS, load_period, pair_segments, save_json, segment
from h10lib import (agent_cov, agent_stats, analyze_pair, pair_stats, stouffer, swarm_stats, verdict_P1, verdict_P2,
                    verdict_P3, verdict_P4, verdict_pair)

OUT = DATA / "NE34"
EPS_MAX = None  # set from synthetic_summary.json (Amendment 1); None = read at run time


def eps_max():
    import json
    s = json.loads((DATA / "synthetic_summary.json").read_text())
    return float(s.get("eps_max_P2", 1.0))


def placebo_covs(key, U, n=32):
    """Mean free-week covariance of the other regime-I free weeks (cross-week placebo for P4)."""
    if PAIRS[key]["regime"] != "I":
        return None, []
    own = PAIRS[key]["F"]
    covs, names = [], []
    for gno in (11, 16, 31):
        if gno == own:
            continue
        seg = segment(load_period(gno, n), U)
        a, m, C = agent_cov(seg)
        covs.append(C.mean(0)); names.append(gno)
    return covs, names


def run_one(key, n_boot, rng, n=32, variant="combined", include_day1=False, win_min=30, with_placebo=True, n_rot=2000):
    F, A, g = pair_segments(key, n=n, variant=variant, include_day1=include_day1, win_min=win_min)
    Cp, pn = placebo_covs(key, F.U, n) if with_placebo else (None, [])
    res = analyze_pair(F, A, rng, n_boot=n_boot, n_rot=n_rot, C_placebo=Cp)
    res["placebo_weeks"] = pn
    res["v1"] = verdict_P1(res["P1_r"], res["P1_p"], res["P1_mse_tilt"], res["P1_mse_trans"])
    em = eps_max()
    if np.isfinite(res["eps"]) and abs(res["eps"]) <= em:
        res["v2"] = verdict_P2(res["P2_rho"], res.get("P2_rho_ci90", [np.nan, np.nan]))
    else:
        res["v2"] = f"n/a (non-perturbative, eps = {res['eps']:.2f} > {em:.2f})"
    # Amendment 1: "would-be" P2 verdict (not counted) where the first-order tilt is unbiased in the synthetic (eps <= 1.2)
    res["v2_wouldbe"] = (verdict_P2(res["P2_rho"], res.get("P2_rho_ci90", [np.nan, np.nan]))
                         if np.isfinite(res["eps"]) and abs(res["eps"]) <= 1.2 else "n/a (eps > 1.2)")
    res["v3"] = verdict_P3(res.get("dg", np.nan), res.get("dg_ci90", [np.nan, np.nan]))
    res["v4"] = verdict_P4(res.get("P4_D", np.nan), res.get("P4_D_ci90", [np.nan, np.nan]), res.get("P4_cos_Cg", np.nan),
                           res.get("P4_rot_p95", np.nan))
    res["v"] = verdict_pair(res["v1"], res["v2"], res["v3"], res["v4"])
    res["n_win_F"] = int(len(np.unique(F.win))); res["n_win_A"] = int(len(np.unique(A.win)))
    res["days_F"] = F.meta["days"]; res["days_A"] = A.meta["days"]
    # descriptive extras: per-agent table, swarm deviations for the F(m) figure, mean-pairwise signal correlation
    sF, sA = agent_stats(F), agent_stats(A)
    wF, wA = swarm_stats(F, sF), swarm_stats(A, sA)
    if wF is not None and wA is not None:
        res["dm_F"] = wF["dm"].tolist(); res["dm_A"] = wA["dm"].tolist()
        nF, nA = len(sF.agents), len(sA.agents)
        res["rhobar_F"] = float((wF["R"][0] - 1) / max(nF - 1, 1)); res["rhobar_A"] = float((wA["R"][0] - 1) / max(nA - 1, 1))
    ps = pair_stats(sF, sA)
    res["agent_table"] = [{"agent": int(a), "muF": float(mf), "muA": float(ma), "D": float(d), "k2F": float(kf),
                           "k2A": float(ka), "k2pred": float(kp)}
                          for a, mf, ma, d, kf, ka, kp in zip(ps["agents"], ps["muF"], ps["muA"], ps["D"], ps["k2F"],
                                                              ps["k2A"], ps["k2pred"])]
    # standardized per-agent deviations (window means minus agent mean, over sqrt(k2 + noise)) for the F(m) figure
    for name, seg, st in (("F", F, sF), ("A", A, sA)):
        x = (seg.S1 @ seg.U[:, 0]) / seg.c
        idx = {a: i for i, a in enumerate(st.agents)}
        z = [(x[j] - st.mu[idx[a], 0]) for j, a in enumerate(seg.agent) if a in idx]
        res[f"dev_{name}"] = np.array(z).tolist()
    return res


def combined(results):
    """Amendment 1: combined verdicts over the three primary pairs; P3 and P4 are descriptive."""
    prim = [r for r in results.values() if r["primary"]]
    rpos = sum(r["P1_r"] > 0 for r in prim)
    pst = stouffer([r["P1_p"] for r in prim])
    v1 = "supported" if (rpos >= 2 and pst < 0.05) else ("failed" if (rpos <= 1 or np.mean([r["P1_r"] for r in prim]) <= 0) else "mixed")
    testable = [r["v2"] for r in prim if not r["v2"].startswith("n/a")]
    n_fail = sum(v.startswith("failed") for v in testable)
    same_dir = max(sum("R4" in v for v in testable), sum("R3" in v for v in testable)) if testable else 0
    if not testable:
        v2 = "n/a (no pair in the perturbative range)"
    elif testable and same_dir >= max(1, int(np.ceil(2 * len(testable) / 3))):
        v2 = "failed"
    elif any(v == "supported" for v in testable) and n_fail == 0:
        v2 = "supported"
    else:
        v2 = "inconclusive"
    v3 = f"descriptive ({sum(r['v3'] == 'supported' for r in prim)}/3 CIs contain 0)"
    v4 = f"descriptive ({sum(r['v4'] == 'supported' for r in prim)}/3 pass the original rule)"
    if v1 == "failed" or v2 == "failed":
        overall = "failed"
    elif v1 == "supported" and v2 == "supported":
        overall = "supported"
    else:
        overall = "mixed"
    return {"P1": v1, "P1_stouffer_p": pst, "P1_n_rpos": rpos, "P2": v2, "P2_testable_pairs": len(testable),
            "P3": v3, "P4": v4, "overall": overall}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--skip-robust", action="store_true")
    # round 1b (2026-10-04): corrected inputs; defaults reproduce round 1
    ap.add_argument("--emb", default="bge_small", choices=["bge_small", "gte_modernbert"])
    ap.add_argument("--goals", default="h10", choices=["h10", "shared"])
    ap.add_argument("--dedupe", default="none", choices=["none", "copies", "restate"])
    ap.add_argument("--style", action="store_true")
    args = ap.parse_args()
    h10data.configure(args.emb, args.goals, args.dedupe, args.style)
    global OUT
    OUT = h10data.out_root() / "NE34"
    print("config", h10data.cfg_tag(), "->", OUT, flush=True)
    rng = np.random.default_rng(20261003)
    t0 = time.time()
    results = {}
    for key, cfg in PAIRS.items():
        r = run_one(key, args.boot, rng)
        r["primary"] = cfg["primary"]
        results[key] = r
        print(key, f"N={r['N']} Dbar={r['Dbar']:.4f} eps={r['eps']:.2f} P1 r={r['P1_r']:.2f} p={r['P1_p']:.3f} "
                   f"mse t/u={r['P1_mse_tilt']:.2e}/{r['P1_mse_trans']:.2e} | rho={r['P2_rho']:.2f} {r.get('P2_rho_ci90')} "
                   f"perp={r['P2_rho_perp']:.2f} | gF={r.get('gF', np.nan):.2f} gA={r.get('gA', np.nan):.2f} "
                   f"dg CI {r.get('dg_ci90')} | D={r.get('P4_D', np.nan):.3f} {r.get('P4_D_ci90')} | "
                   f"{r['v1']} / {r['v2']} / {r['v3']} / {r['v4']} -> {r['v']}  {time.time() - t0:.0f}s", flush=True)
    comb = combined(results)
    print("combined", comb)
    save_json({"pairs": results, "combined": comb, "eps_max_P2": eps_max()}, OUT / "pairs.json")
    if args.skip_robust:
        return
    rob = {}
    variants = [("n16", dict(n=16)), ("n64", dict(n=64)), ("goal_only", dict(variant="goal")),
                ("kickoff_only", dict(variant="kickoff")), ("with_day1", dict(include_day1=True)), ("win60", dict(win_min=60))]
    zdim = h10data.statements()[1].shape[1]
    for key, cfg in PAIRS.items():
        if not cfg["primary"]:
            continue
        for vname, kw in variants:
            if kw.get("n", 32) > zdim:
                continue
            r = run_one(key, 200, rng, with_placebo=False, n_rot=500, **kw)
            rob[f"{key}:{vname}"] = {k: r.get(k) for k in ("N", "Dbar", "eps", "lam", "P1_r", "P1_p", "P1_mse_tilt",
                                                            "P1_mse_trans", "P2_rho", "P2_rho_ci90", "P2_rho_perp", "gF",
                                                            "gA", "dg", "dg_ci90", "P4_D", "P4_D_ci90", "v1", "v2", "v3",
                                                            "v4", "v")}
            print(key, vname, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in rob[f"{key}:{vname}"].items()
                               if k in ("N", "Dbar", "eps", "P1_r", "P1_p", "P2_rho", "dg", "P4_D", "v")}, flush=True)
    save_json(rob, OUT / "robustness.json")
    print(f"done {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
