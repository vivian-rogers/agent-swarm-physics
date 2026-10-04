"""Synthetic validation (axis F): mean-field O(n) swarms at village sampling, analyzed with the real pipeline.

World (per replicate):
- N agents, unit spins s_i in n = 32 dims; quenched agent directions mu_i (uniform) with concentrations
  kappa_i = kbar * lognormal(sigma_het); goal direction g (uniform, independent of mu_i).
- Gibbs (heat-bath) dynamics, one sweep per 30-min window, each agent updating with probability p_upd from
  vMF(kappa_i mu_i + J sum_{j != i} s_j + lam_i g). Stationary law = Gibbs, so under H the assigned week is the exact
  exponential tilt of the free week.
- Statements: z = unit(a s + sqrt(1 - a^2) xi), xi uniform; counts per agent-window resampled from the real period's
  count distribution (calibration.json), so sampling noise matches the village.
- Free week: lam = 0. Assigned week: day 1 is the transient and is discarded, as in the real design.

Scenarios: H (pure field, several lam), R1 (uniform translation, no field), R3 (cooling: kappa x2 in A), R4 (dispersal:
kappa x0.5 in A), R5 (J x1.6 / x0.4 in A), R6 (agent-specific lam_i = lam * lognormal(0.7)).

Usage:
  uv run python synthetic.py tune            # check calibration targets of the free-week world
  uv run python synthetic.py run [--reps 100] [--boot 60] [--workers 2]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from h10data import DATA, save_json
from h10lib import (aggregate, agent_stats, analyze_pair, random_transverse, stouffer, swarm_stats, verdict_P1,
                    verdict_P2, verdict_P3, verdict_P4, verdict_pair)

N_DIM = 32
CAL = json.loads((DATA / "calibration.json").read_text())

# designs mirror the three primary pairs: free-week and assigned-week (days 2+) shapes and statement counts
DESIGNS = {
    "11-12": {"N": 7, "F": (5, 6, "11"), "A": (3, 6, "12"), "reg": "I"},
    "16-17": {"N": 7, "F": (5, 6, "16"), "A": (4, 6, "17"), "reg": "I"},
    "37-38": {"N": 12, "F": (3, 9, "37"), "A": (8, 9, "38"), "reg": "III"},
}
WORLD = {  # tuned against calibration.json (non-test periods, random directions): r_sig, mu spread, R, a2, trC cv
    "I": {"kbar": 150.0, "sigma_het": 0.9, "J": 3.0, "p_upd": 0.6, "a": 0.69, "drive": 26.0, "phi": 0.5},
    "III": {"kbar": 180.0, "sigma_het": 1.0, "J": 1.5, "p_upd": 0.6, "a": 0.73, "drive": 6.0, "phi": 0.5},
}
WORLD_GIBBS = {  # no exogenous drive: the assigned week is the exact tilt (collective enhancement R ~ 2 only)
    "I": {"kbar": 30.0, "sigma_het": 0.9, "J": 5.0, "p_upd": 0.6, "a": 0.69, "drive": 0.0},
    "III": {"kbar": 60.0, "sigma_het": 1.0, "J": 2.0, "p_upd": 0.6, "a": 0.73, "drive": 0.0},
}


def vmf(theta: np.ndarray, rng) -> np.ndarray:
    """Wood (1994) sampler, vectorized over rows of theta (natural parameters, shape (m, p))."""
    m, p = theta.shape
    kap = np.linalg.norm(theta, axis=1)
    mu = theta / np.where(kap > 0, kap, 1)[:, None]
    w = np.empty(m)
    todo = np.arange(m)
    b = (-2 * kap + np.sqrt(4 * kap ** 2 + (p - 1) ** 2)) / (p - 1)
    x0 = (1 - b) / (1 + b)
    c = kap * x0 + (p - 1) * np.log(1 - x0 ** 2)
    while len(todo):
        Z = rng.beta((p - 1) / 2, (p - 1) / 2, len(todo))
        bb = b[todo]
        W = (1 - (1 + bb) * Z) / (1 - (1 - bb) * Z)
        ok = kap[todo] * W + (p - 1) * np.log(1 - x0[todo] * W) - c[todo] >= np.log(rng.random(len(todo)))
        w[todo[ok]] = W[ok]
        todo = todo[~ok]
    v = rng.standard_normal((m, p))
    v -= (v * mu).sum(1, keepdims=True) * mu
    v /= np.linalg.norm(v, axis=1, keepdims=True)
    s = w[:, None] * mu + np.sqrt(np.clip(1 - w ** 2, 0, None))[:, None] * v
    uni = kap < 1e-9
    if uni.any():
        u = rng.standard_normal((uni.sum(), p))
        s[uni] = u / np.linalg.norm(u, axis=1, keepdims=True)
    return s


def simulate(world, N, mu, kap, g, s0, lam, ndays, wpd, counts, rng, translate=0.0, J=None):
    """Run ndays x wpd windows; return statements (Z, agent, day, win) and the final state.
    world["drive"] > 0 adds an exogenous common drive psi(t) (isotropic AR(1) across windows, coefficient world["phi"],
    stationary per-component sd world["drive"]) to every agent's natural parameter. It is unchanged by the field, so with
    drive > 0 the assigned week is only approximately the tilt of the free week (a realistic perturbation)."""
    J = world["J"] if J is None else J
    a = world["a"]
    s = s0.copy()
    lam = np.broadcast_to(np.asarray(lam, float), (N,))
    sd, phi = world.get("drive", 0.0), world.get("phi", 0.5)
    psi = sd * rng.standard_normal(N_DIM)
    Zs, ags, days, wins = [], [], [], []
    for d in range(ndays):
        for t in range(wpd):
            psi = phi * psi + np.sqrt(1 - phi ** 2) * sd * rng.standard_normal(N_DIM)
            for i in rng.permutation(N):
                if rng.random() < world["p_upd"]:
                    th = kap[i] * mu[i] + J * (s.sum(0) - s[i]) + lam[i] * g + psi
                    s[i] = vmf(th[None], rng)[0]
            c = rng.choice(counts, size=N)
            for i in range(N):
                if c[i] <= 0:
                    continue
                xi = rng.standard_normal((c[i], N_DIM))
                xi /= np.linalg.norm(xi, axis=1, keepdims=True)
                z = a * s[i] + np.sqrt(1 - a ** 2) * xi + translate * g
                Zs.append(z / np.linalg.norm(z, axis=1, keepdims=True))
                ags += [i] * c[i]; days += [d] * c[i]; wins += [d * 1000 + t] * c[i]
    if not Zs:
        return np.zeros((0, N_DIM)), np.array([], int), np.array([], int), np.array([], int), s
    return np.vstack(Zs), np.array(ags), np.array(days), np.array(wins), s


def counts_for(period: str):
    c = np.array(CAL["counts"][period]["c"])
    n_ag, n_win = CAL["counts"][period]["n_agents"], CAL["counts"][period]["n_win"]
    cover = len(c) / (n_ag * n_win)
    # agent-windows with no statements appear as zeros with probability 1 - coverage
    n0 = int(round(len(c) * (1 - cover) / max(cover, 1e-9)))
    return np.r_[c, np.zeros(n0, int)]


def make_world(design, rng, het=None, gibbs=False, aniso=False):
    """aniso: agents' quenched directions cluster around a shared topic mu0 and the goal overlaps it (cos 0.6), so the
    swarm's susceptibility is anisotropic (stiff along mu0) and the tilt bends the response away from mu0 (P4 signal)."""
    w = (WORLD_GIBBS if gibbs else WORLD)[DESIGNS[design]["reg"]]
    N = DESIGNS[design]["N"]
    if aniso:
        mu0 = rng.standard_normal(N_DIM); mu0 /= np.linalg.norm(mu0)
        mu = mu0 + 0.35 * rng.standard_normal((N, N_DIM))
        mu /= np.linalg.norm(mu, axis=1, keepdims=True)
        v = rng.standard_normal(N_DIM); v -= (v @ mu0) * mu0; v /= np.linalg.norm(v)
        g = 0.6 * mu0 + 0.8 * v
    else:
        mu = rng.standard_normal((N, N_DIM)); mu /= np.linalg.norm(mu, axis=1, keepdims=True)
        g = rng.standard_normal(N_DIM); g /= np.linalg.norm(g)
    sig = w["sigma_het"] if het is None else het
    kap = w["kbar"] * np.exp(sig * rng.standard_normal(N) - sig ** 2 / 2)
    return w, N, mu, kap, g


def run_pair(design, scen, lam, seed, n_boot=60, K=20, het=None):
    rng = np.random.default_rng(seed)
    w, N, mu, kap, g = make_world(design, rng, het, gibbs=(scen in ("Hgibbs", "HgibbsAniso")),
                                  aniso=(scen in ("Haniso", "HgibbsAniso")))
    h_true = g
    if scen == "Hmis":  # true field direction only partly along the text direction (cos 0.5)
        v = rng.standard_normal(N_DIM); v -= (v @ g) * g; v /= np.linalg.norm(v)
        h_true = 0.5 * g + np.sqrt(0.75) * v
    D = DESIGNS[design]
    cF, cA = counts_for(D["F"][2]), counts_for(D["A"][2])
    s0 = vmf(kap[:, None] * mu, rng)
    _, _, _, _, s0 = simulate(w, N, mu, kap, g, s0, 0.0, 2, D["F"][1], np.array([0]), rng)  # burn-in
    ZF, aF, dF, wF, s1 = simulate(w, N, mu, kap, g, s0, 0.0, D["F"][0], D["F"][1], cF, rng)
    lamA, kapA, JA, tr = lam, kap, w["J"], 0.0
    if scen == "R1":
        lamA, tr = 0.0, lam  # here `lam` is the translation amplitude b
    elif scen == "R3":
        kapA = kap * 2.0
    elif scen == "R4":
        kapA = kap * 0.5
    elif scen == "R5up":
        JA = w["J"] * 1.6
    elif scen == "R5down":
        JA = w["J"] * 0.4
    elif scen == "R6":
        lamA = lam * np.exp(0.7 * rng.standard_normal(N) - 0.245)
    _, _, _, _, s2 = simulate(w, N, mu, kapA, h_true, s1, lamA, 1, D["A"][1], cA, rng, translate=tr, J=JA)  # day 1 dropped
    ZA, aA, dA, wA, _ = simulate(w, N, mu, kapA, h_true, s2, lamA, D["A"][0], D["A"][1], cA, rng, translate=tr, J=JA)
    U = random_transverse(g, K, rng)
    F, A = aggregate(ZF, aF, dF, wF, U), aggregate(ZA, aA, dA, wA, U)
    res = analyze_pair(F, A, rng, n_boot=n_boot, n_rot=300)
    res["v1"] = verdict_P1(res["P1_r"], res["P1_p"], res["P1_mse_tilt"], res["P1_mse_trans"])
    res["v2"] = verdict_P2(res["P2_rho"], res.get("P2_rho_ci90", [np.nan, np.nan]))
    res["v3"] = verdict_P3(res.get("dg", np.nan), res.get("dg_ci90", [np.nan, np.nan]))
    res["v4"] = verdict_P4(res.get("P4_D", np.nan), res.get("P4_D_ci90", [np.nan, np.nan]), res.get("P4_cos_Cg", np.nan),
                           res.get("P4_rot_p95", np.nan))
    res["v"] = verdict_pair(res["v1"], res["v2"], res["v3"], res["v4"])
    keep = ("N", "Dbar", "lam", "eps", "P1_r", "P1_p", "P1_mse_tilt", "P1_mse_trans", "P2_rho", "P2_rho_ci90",
            "P2_rho_gauss", "P2_rho_perp", "P2_rho_perp_ci90", "gF", "gA", "dg", "dg_ci90", "P4_D", "P4_D_ci90",
            "P4_cos_Cg", "P4_cos_g", "P4_rot_p95", "P2swarm_rho", "R2_slope_muF", "gammaF", "v1", "v2", "v3", "v4", "v")
    out = {k: res.get(k) for k in keep}
    out.update({"design": design, "scen": scen, "lam_in": lam, "seed": seed, "het": het})
    return out


def _job(args):
    try:
        return run_pair(*args)
    except Exception as e:  # keep the batch alive; record the failure
        return {"design": args[0], "scen": args[1], "lam_in": args[2], "seed": args[3], "error": repr(e)}


def tune():
    """Free-week calibration statistics of the synthetic world vs calibration.json (random directions)."""
    from h10lib import agent_cov
    for design in DESIGNS:
        reg = DESIGNS[design]["reg"]
        stats = []
        for rep in range(6):
            rng = np.random.default_rng(100 + rep)
            w, N, mu, kap, g = make_world(design, rng)
            s0 = vmf(kap[:, None] * mu, rng)
            _, _, _, _, s0 = simulate(w, N, mu, kap, g, s0, 0.0, 2, 8, np.array([0]), rng)
            Z, ag, dy, wn, _ = simulate(w, N, mu, kap, g, s0, 0.0, 10, 8, counts_for(DESIGNS[design]["F"][2]), rng)
            U = random_transverse(rng.standard_normal(N_DIM), 19, rng)
            seg = aggregate(Z, ag, dy, wn, U)
            st = agent_stats(seg); sw = swarm_stats(seg, st)
            var_stmt = (Z @ U).var(0).mean()
            xm = seg.S1 / seg.c[:, None]
            A_ = 1 - 1 / seg.c
            a2 = ((((xm ** 2).sum(1)) - 1 / seg.c) * A_).sum() / (A_ ** 2).sum()
            _, _, C = agent_cov(seg)
            trC = np.array([np.trace(c) for c in C])
            stats.append({"r_sig": np.mean(st.k2) / var_stmt, "mu_between_rel": np.var(st.mu, axis=0).mean() / var_stmt,
                          "R_median": np.nanmedian(sw["R"]), "a2_window": a2, "trC_cv": trC.std() / trC.mean(),
                          "var_stmt": var_stmt})
        avg = {k: float(np.mean([s[k] for s in stats])) for k in stats[0]}
        tgt = CAL[f"summary_{reg}"]
        print(design, {k: (round(avg[k], 3), round(tgt.get(k, np.nan), 3)) for k in avg}, flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["tune", "run", "summarize"])
    ap.add_argument("--reps", type=int, default=100)
    ap.add_argument("--boot", type=int, default=60)
    ap.add_argument("--workers", type=int, default=2)
    args = ap.parse_args()
    if args.mode == "tune":
        tune()
        return
    out_path = DATA / "synthetic_runs.json"
    if args.mode == "run":
        jobs = []
        for design in DESIGNS:
            for lam in (10.0, 20.0, 60.0, 150.0):                      # drive world: eps ~ 0.5, 1, 2, 4
                jobs += [(design, "H", lam, 10_000 * len(jobs) + r, args.boot) for r in range(args.reps)]
            for lam in (2.0, 6.0, 15.0):                               # exact-tilt world
                jobs += [(design, "Hgibbs", lam, 10_000 * len(jobs) + r, args.boot) for r in range(args.reps)]
            for scen, lam in (("Haniso", 20.0), ("HgibbsAniso", 6.0), ("Hmis", 20.0)):
                jobs += [(design, scen, lam, 10_000 * len(jobs) + r, args.boot) for r in range(args.reps)]
            for scen in ("R3", "R4", "R5up", "R5down", "R6"):
                jobs += [(design, scen, 20.0, 10_000 * len(jobs) + r, args.boot) for r in range(args.reps)]
            jobs += [(design, "R1", 0.10, 10_000 * len(jobs) + r, args.boot) for r in range(args.reps)]
            for het in (0.3, 1.5):
                jobs += [(design, "H", 20.0, 10_000 * len(jobs) + r, args.boot, 20, het) for r in range(args.reps // 2)]
        t0 = time.time()
        print(f"{len(jobs)} jobs on {args.workers} workers", flush=True)
        res = []
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            for k, r in enumerate(ex.map(_job, jobs, chunksize=4)):
                res.append(r)
                if (k + 1) % 100 == 0:
                    print(f"{k + 1}/{len(jobs)} {time.time() - t0:.0f}s", flush=True)
                    save_json(res, out_path)
        save_json(res, out_path)
    summarize(out_path)


def summarize(path):
    res = [r for r in json.loads(path.read_text()) if "error" not in r]
    errs = [r for r in json.loads(path.read_text()) if "error" in r]
    import collections
    groups = collections.defaultdict(list)
    for r in res:
        groups[(r["design"], r["scen"], r["lam_in"], r.get("het"))].append(r)
    table = []
    for key, rs in sorted(groups.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2], str(kv[0][3]))):
        f = lambda k: np.array([x[k] if x.get(k) is not None else np.nan for x in rs], float)
        row = {"design": key[0], "scen": key[1], "lam": key[2], "het": key[3], "n": len(rs),
               "eps_med": float(np.nanmedian(f("eps"))), "Dbar_med": float(np.nanmedian(f("Dbar"))),
               "P1_r_med": float(np.nanmedian(f("P1_r"))),
               "P1_supported": float(np.mean([x["v1"] == "supported" for x in rs])),
               "P1_p05": float(np.nanmean(f("P1_p") < 0.05)),
               "P2_rho_med": float(np.nanmedian(f("P2_rho"))), "P2_rho_gauss_med": float(np.nanmedian(f("P2_rho_gauss"))),
               "P2_cover0": float(np.mean([(x["P2_rho_ci90"][0] <= 0 <= x["P2_rho_ci90"][1]) for x in rs if x.get("P2_rho_ci90") and np.all(np.isfinite(x["P2_rho_ci90"]))])),
               "P2_supported": float(np.mean([x["v2"] == "supported" for x in rs])),
               "P2_failed": float(np.mean([str(x["v2"]).startswith("failed") for x in rs])),
               "P2_perp_med": float(np.nanmedian(f("P2_rho_perp"))),
               "gF_med": float(np.nanmedian(f("gF"))), "dg_med": float(np.nanmedian(f("dg"))),
               "P3_supported": float(np.mean([x["v3"] == "supported" for x in rs])),
               "P3_failed": float(np.mean([x["v3"] == "failed" for x in rs])),
               "P4_D_med": float(np.nanmedian(f("P4_D"))), "P4_supported": float(np.mean([x["v4"] == "supported" for x in rs])),
               "P4_failed": float(np.mean([x["v4"] == "failed" for x in rs])),
               "pair_supported": float(np.mean([x["v"] == "supported" for x in rs])),
               "pair_failed": float(np.mean([x["v"] == "failed" for x in rs])),
               "R2_slope_med": float(np.nanmedian(f("R2_slope_muF")))}
        table.append(row)
    # Amendment 1 rule (fixed before reading these results): P2 is testable only up to eps_max = the largest median eps
    # among the H / Hgibbs cells (all designs, sorted by eps) before the first cell where the first-order tilt is biased
    # (|median rho| >= 0.15) or the 90% CI covers 0 in < 80% of replicates.
    cells = sorted([r for r in table if r["scen"] in ("H", "Hgibbs") and r["het"] is None], key=lambda r: r["eps_med"])
    eps_max = 0.0
    for r in cells:
        if abs(r["P2_rho_med"]) < 0.15 and r["P2_cover0"] >= 0.8:
            eps_max = r["eps_med"]
        else:
            break
    # per-pair verdict under the amended rule (P1 and eps-gated P2 only)
    for row in table:
        rs = groups[(row["design"], row["scen"], row["lam"], row["het"])]
        vv = [verdict_pair(x["v1"], x["v2"] if (x.get("eps") is not None and abs(x["eps"]) <= eps_max) else "n/a")
              for x in rs]
        row["pair_supported_amended"] = float(np.mean([v == "supported" for v in vv]))
        row["pair_failed_amended"] = float(np.mean([v == "failed" for v in vv]))
    # combined (three designs, one replicate each, matched by index) for each scenario
    comb = []
    scen_keys = sorted({(k[1], k[2], k[3]) for k in groups}, key=lambda t: (t[0], t[1], -1 if t[2] is None else t[2]))
    for sk in scen_keys:
        per = [groups.get((d, *sk), []) for d in DESIGNS]
        n = min(len(p) for p in per)
        if n == 0:
            continue
        c1 = c1f = c2s = c2f = c2na = c3 = c4 = cs = cf = 0
        for i in range(n):
            trip = [dict(p[i]) for p in per]
            for t in trip:  # Amendment 1: P2 only in the perturbative range
                if not (t.get("eps") is not None and abs(t["eps"]) <= eps_max):
                    t["v2"] = "n/a"
            rpos = sum((t["P1_r"] or 0) > 0 for t in trip)
            pst = stouffer([t["P1_p"] for t in trip])
            v1 = ("supported" if (rpos >= 2 and pst < 0.05) else
                  "failed" if (rpos <= 1 or np.mean([t["P1_r"] or 0 for t in trip]) <= 0) else "mixed")
            v2s = [t["v2"] for t in trip]
            tv = [v for v in v2s if v != "n/a"]
            nR4 = sum("R4" in str(v) for v in tv); nR3 = sum("R3" in str(v) for v in tv)
            if not tv:
                v2 = "n/a"
            elif max(nR4, nR3) >= max(1, int(np.ceil(2 * len(tv) / 3))):
                v2 = "failed"
            elif any(v == "supported" for v in tv) and not any(str(v).startswith("failed") for v in tv):
                v2 = "supported"
            else:
                v2 = "inconclusive"
            v3 = "supported" if sum(t["v3"] == "supported" for t in trip) >= 2 else "other"
            v4 = "supported" if sum(t["v4"] == "supported" for t in trip) >= 2 else ("failed" if sum(t["v4"] == "failed" for t in trip) >= 2 else "other")
            c1f += v1 == "failed"; c2na += v2 == "n/a"
            c1 += v1 == "supported"; c2s += v2 == "supported"; c2f += v2 == "failed"; c3 += v3 == "supported"; c4 += v4 == "supported"
            overall_s = v1 == "supported" and v2 == "supported"
            overall_f = v1 == "failed" or v2 == "failed"
            cs += overall_s; cf += overall_f
        comb.append({"scen": sk[0], "lam": sk[1], "het": sk[2], "n": n, "P1_combined_supported": c1 / n,
                     "P1_combined_failed": c1f / n, "P2_combined_na": c2na / n,
                     "P2_combined_supported": c2s / n, "P2_combined_failed": c2f / n, "P3_combined_supported": c3 / n,
                     "P4_combined_supported": c4 / n, "H10_supported": cs / n, "H10_failed": cf / n})
    save_json({"per_design": table, "combined": comb, "n_errors": len(errs), "errors": errs[:5], "eps_max_P2": eps_max,
               "eps_max_rule": "largest median eps (H, Hgibbs cells sorted by eps) before the first cell with "
                               "|median rho| >= 0.15 or CI coverage of 0 < 0.8"},
              DATA / "synthetic_summary.json")
    print("eps_max_P2", eps_max)
    for r in table:
        print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})
    print("--- combined")
    for r in comb:
        print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})
    print("errors", len(errs))


if __name__ == "__main__":
    sys.exit(main())
