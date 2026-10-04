"""H81 replication (non-holdout; regimes I and III; both embedding models).

O1  equal-time collective share kappa per goal period (sign-flip null)
O2  slow mode across goal boundaries: D_adjg (P2), profile s(dt), permutation null, tau_u (descriptive)
O3  overlap-adjusted D_adj (P3), turnover-disjoint D_near_perp, far-epoch similarity
O4  scaled jumps of the day residual at roster events vs placebo within-goal day boundaries
O5  robustness: white32 / style_resid_period variants, without Gemini 2.5 Pro, size-matched (m = 4), n_stat weights,
    literal HH null (METHOD = "mean"); each configuration has its own S0 calibration on its own panel.

Output: data/processed/H81-culture-beyond-composition/replication/ (replication.json, kappa.parquet, pairs_<model>.parquet,
day_jumps.parquet)
Usage: uv run python hypotheses/H81-culture-beyond-composition/analysis/replication.py [--s0 100]
"""
from __future__ import annotations

import argparse
import json
import sys
import zlib
from pathlib import Path

import numpy as np
import polars as pl
from scipy.optimize import curve_fit

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h81lib as L  # noqa: E402

MODELS = ["bge_small", "gte_modernbert"]
KEYS = ("D_adjg", "D_adj", "D_near", "D_near_perp", "D_adjg_perp", "far90", "far90_perp")


def stats_for(pan, X, kick, subset=None, draws=1, rng=None, weights=None):
    A, B, R = L.agent_block_residuals(pan, X, weights)
    if subset:
        acc = [L.slow_stats(L.pair_table(pan, A, B, R, kick, subset_size=subset, rng=rng)) for _ in range(draws)]
        return {k: float(np.nanmean([a[k] for a in acc])) for k in KEYS}, (A, B, R)
    T = L.pair_table(pan, A, B, R, kick)
    return {k: L.slow_stats(T)[k] for k in KEYS}, (A, B, R, T)


def calibrate(pan, X, kick, reps, seed, subset=None, draws=1, weights=None):
    sc = L.variance_scales(pan, X)
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(reps):
        Xs = L.simulate(pan, sc, rng)
        st, _ = stats_for(pan, Xs, kick, subset, draws, rng, weights)
        out.append(st)
    df = pl.DataFrame(out)
    return {k: {"q95": float(np.nanquantile(df[k].to_numpy(), 0.95)), "mean": float(np.nanmean(df[k].to_numpy())),
                "sd": float(np.nanstd(df[k].to_numpy()))} for k in KEYS}


def panel(model, variant, regime, drop=frozenset(), use_human=True):
    ad, X, blocks = L.load(model, variant, regime, drop)
    P = L.projectors(model, regime, ad, use_human)
    pan = L.Panel(ad, blocks, P)
    kick = L.goal_kickoff(model, regime, np.unique(pan.goal))
    return ad, X, pan, kick


def tau_fit(T):
    m = ~np.isnan(T[:, 5])
    x, y, w = T[m, 2], T[m, 5], T[m, 7]
    try:
        p, cov = curve_fit(lambda t, A, tau, c: A * np.exp(-t / tau) + c, x, y, p0=(0.1, 30, 0), sigma=1 / np.sqrt(w),
                           bounds=([-1, 1, -1], [1, 400, 1]), maxfev=20000)
        return {"A": float(p[0]), "tau_days": float(p[1]), "s_inf": float(p[2]),
                "tau_se": float(np.sqrt(cov[1, 1])) if np.isfinite(cov[1, 1]) else None}
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--s0", type=int, default=100)
    a = ap.parse_args()
    out = L.OUT / "replication"; out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(81)
    res = {"primary": {}, "robustness": {}, "kappa": {}, "roster": {}}
    kap_rows, jump_rows = [], []
    for model in MODELS:
        syn = json.loads((L.OUT / "synthetic" / f"synthetic_{model}.json").read_text())
        for regime in ("I", "III"):
            ad, X, pan, kick = panel(model, "style_resid", regime)
            st, (A, B, R, T) = stats_for(pan, X, kick)
            thr = syn["scenarios"][regime]["S0_q95"]
            perm = L.permute_time(pan, A, B, R, kick, rng, n=1000)
            prof = L.profile(T); prof_perp = L.profile(T, col=6)
            res["primary"][f"{model}/{regime}"] = {
                **st, "S0_q95": thr, "S0_mean": syn["scenarios"][regime]["S0_mean"],
                "S0_far90_mean": syn["scenarios"][regime]["S0_far90_mean"],
                "S0_far90_q95": syn["scenarios"][regime]["S0_far90_q95"],
                "pass_P2": bool(st["D_adjg"] > thr["D_adjg"]), "pass_P3_Dadj": bool(st["D_adj"] > thr["D_adj"]),
                "pass_P3_perp": bool(st["D_near_perp"] > thr["D_near_perp"]),
                "perm_p_Dadj": float((np.sum(perm >= st["D_adj"]) + 1) / (len(perm) + 1)),
                "n_pairs": int(len(T)), "n_blocks": int(len(set(T[:, 0]) | set(T[:, 1]))),
                "n_goals": int(len(np.unique(pan.block_goal))), "n_agentdays": int(len(X)),
                "profile": prof, "profile_perp": prof_perp, "tau_fit": tau_fit(T)}
            pl.DataFrame(T, schema=["b", "c", "dt", "J", "goal_sim", "s", "s_perp", "w"], orient="row") \
                .with_columns(pl.lit(regime).alias("regime")).write_parquet(out / f"pairs_{model}_{regime}.parquet")
            print(model, regime, {k: round(v, 3) for k, v in st.items()}, flush=True)
            # O1 kappa per goal period
            kb, nulls, ns = L.kappa_blocks(A, B, R, pan.nb, rng, n_null=1000)
            for g in np.unique(pan.block_goal):
                bs = np.flatnonzero((pan.block_goal == g) & ~np.isnan(kb))
                if len(bs) == 0:
                    continue
                w = ns[bs] / ns[bs].sum()
                k_g = float((kb[bs] * w).sum()); null_g = (nulls[bs] * w[:, None]).sum(0)
                # excess variance ratio X = |u|^2 / floor
                xs = []
                for b in bs:
                    m = B == b; Rb = R[m]
                    xs.append(float(np.linalg.norm(Rb.mean(0)) ** 2 / ((Rb ** 2).sum() / len(Rb) ** 2)))
                # agent jackknife SE of kappa_G
                gm = np.isin(B, bs); ag_g = np.unique(A[gm]); jk = []
                for x in ag_g:
                    keep = ~(gm & (A == x))
                    kb2, _, ns2 = L.kappa_blocks(A[keep], B[keep], R[keep], pan.nb)
                    ok2 = [b for b in bs if np.isfinite(kb2[b])]
                    if ok2:
                        w2 = ns2[ok2] / ns2[ok2].sum(); jk.append(float((kb2[ok2] * w2).sum()))
                jk = np.array(jk); nj = len(jk)
                se_jk = float(np.sqrt((nj - 1) / nj * ((jk - jk.mean()) ** 2).sum())) if nj > 2 else np.nan
                kap_rows.append({"model": model, "regime": regime, "goal_no": int(g), "kappa": k_g, "kappa_se": se_jk,
                                 "n_agents_goal": int(len(ag_g)),
                                 "null_lo": float(np.quantile(null_g, 0.025)), "null_hi": float(np.quantile(null_g, 0.975)),
                                 "p_upper": float((np.sum(null_g >= k_g) + 1) / (len(null_g) + 1)),
                                 "excess_ratio": float(np.mean(xs)), "n_agents_med": float(np.median(ns[bs])),
                                 "n_blocks": int(len(bs)),
                                 "first_day": str(min(ad.filter(pl.col("goal_no") == g)["pt_date"])),
                                 "last_day": str(max(ad.filter(pl.col("goal_no") == g)["pt_date"]))})
            # O4 roster jumps (day residuals)
            Rd = L.day_residuals(pan, X)
            for d0, d1, g, ev, J, Js, n1 in L.day_jumps(pan, Rd, L.roster_event_days()):
                jump_rows.append({"model": model, "regime": regime, "d0": d0, "d1": d1, "goal_no": int(g), "roster": ev,
                                  "J": float(J), "J_stayers": float(Js), "n": int(n1)})
            # O5 robustness
            seed = zlib.crc32(f"{model}|{regime}".encode())
            configs = {
                "white32": dict(variant="white32"), "style_resid_period": dict(variant="style_resid_period"),
                "no_gemini25": dict(drop=frozenset({L.GEMINI_25})), "no_human_dir": dict(use_human=False),
                "size_matched_m4": dict(subset=4), "nstat_weights": dict(weights=True), "literal_mean_null": dict(method="mean")}
            for name, cfg in configs.items():
                ad2, X2, pan2, kick2 = panel(model, cfg.get("variant", "style_resid"), regime, cfg.get("drop", frozenset()),
                                             cfg.get("use_human", True))
                wts = pan2.n_stat if cfg.get("weights") else None
                old = L.METHOD
                if cfg.get("method"):
                    L.METHOD = cfg["method"]
                sub = cfg.get("subset"); draws = 20 if sub else 1
                st2, _ = stats_for(pan2, X2, kick2, sub, draws, rng, wts)
                cal = calibrate(pan2, X2, kick2, a.s0 if not sub else max(a.s0 // 2, 30), seed + len(name), sub, draws, wts)
                L.METHOD = old
                res["robustness"][f"{model}/{regime}/{name}"] = {
                    **st2, "S0": cal, "pass_P2": bool(st2["D_adjg"] > cal["D_adjg"]["q95"]),
                    "pass_P3": bool(st2["D_adj"] > cal["D_adj"]["q95"]),
                    "ratio_Dadjg_to_primary": float(st2["D_adjg"] / st["D_adjg"]) if st["D_adjg"] else None}
                print("  ", name, {k: round(st2[k], 3) for k in ("D_adjg", "D_adj", "D_near_perp")},
                      "q95", round(cal["D_adjg"]["q95"], 3), round(cal["D_adj"]["q95"], 3), flush=True)
    kap = pl.DataFrame(kap_rows); kap.write_parquet(out / "kappa.parquet")
    jumps = pl.DataFrame(jump_rows); jumps.write_parquet(out / "day_jumps.parquet")
    for model in MODELS:
        k = kap.filter(pl.col("model") == model)
        res["kappa"][model] = {"n_periods": k.height, "frac_above_band": float((k["kappa"] > k["null_hi"]).mean()),
                               "median_kappa": float(k["kappa"].median()),
                               "median_excess_ratio": float(k["excess_ratio"].median()),
                               "by_regime": {r: float(k.filter(pl.col("regime") == r)["kappa"].median()) for r in ("I", "III")}}
        for scope in ("I", "III", "all"):
            j = jumps.filter(pl.col("model") == model)
            if scope != "all":
                j = j.filter(pl.col("regime") == scope)
            ev, pc = j.filter(pl.col("roster")), j.filter(~pl.col("roster"))
            if ev.height == 0:
                continue
            for col in ("J", "J_stayers"):
                e = ev[col].drop_nans().to_numpy(); p = pc[col].drop_nans().to_numpy()
                if len(e) == 0 or len(p) < 5:
                    continue
                draws = np.array([np.median(rng.choice(p, len(e), replace=False)) for _ in range(2000)])
                res["roster"][f"{model}/{scope}/{col}"] = {
                    "n_events": int(len(e)), "n_placebo": int(len(p)), "median_event": float(np.median(e)),
                    "median_placebo": float(np.median(p)), "rho": float(np.median(e) / np.median(p)),
                    "percentile": float((draws < np.median(e)).mean())}
    (out / "replication.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps({k: res[k] for k in ("kappa", "roster")}, indent=1))


if __name__ == "__main__":
    main()
