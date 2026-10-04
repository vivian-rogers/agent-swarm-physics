"""H20 real-data pipeline, one goal period at a time (non-holdout data only).

For each period: agent-day states (O1), C / C_m / V-g / V-c (O2-O4), aging statistics (O5) with the parametric
stationary null, model fits and leave-one-day-out CV (O6), mu-hat CI, design power at the fitted nuisance parameters,
robustness variants and the secondary observables (O7). Writes data/processed/H20-content-aging/G<NN>/result.json,
matrices.npz, and per-period figures in hypotheses/H20-content-aging/G<NN>/figures/.

Usage: uv run python hypotheses/H20-content-aging/analysis/run_periods.py --periods 38      (or --role long / --all)
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h20lib as L  # noqa: E402
from h20lib import hc  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy.stats import wilcoxon  # noqa: E402

B_MAIN, B_VAR, B_MU, B_POW = 500, 200, 200, 300
import os  # noqa: E402
DEBUG_DIR = Path(os.environ["H20_DEBUG_DIR"]) if os.environ.get("H20_DEBUG_DIR") else None
NULL_KIND = "iso"   # "iso" = pre-registered isotropic null; "aniso" = Amendment 2 (estimated latent shapes)


def null_test(xbar, v, n, valid, wk, T, rng, B, stable=None, with_derived=True, ndim=32, two_scale=False, clock=None):
    C, npair = L.two_time(xbar, v, valid)
    Cx, cnt = L.cross_agent_C(xbar, v, valid)
    nm = L.fit_null_model(C, npair, Cx, cnt, wk, T, two_scale=two_scale)
    if NULL_KIND == "aniso":   # Amendment 2: latent shapes estimated from the same states
        Rs, Rp, _, _ = L.estimate_shapes(xbar, v, valid)
        nm = dataclasses.replace(nm, Rs=Rs, Rp=Rp)
    design = L.design_from_states(xbar, v, valid, n, ndim)
    obs = L.stats_bundle(xbar, v, valid, wk, T, stable=stable, with_derived=with_derived)
    null = L.null_distribution(nm, design, wk, T, B, rng, ndim=ndim, stable=stable, with_derived=with_derived)
    pv = {}
    for k in obs:
        if k in ("n_entries",):
            continue
        pv[k] = dict(obs=obs[k], p_upper=L.p_upper(obs[k], null[k]), p_lower=L.p_lower(obs[k], null[k]),
                     null_mean=float(np.nanmean(null[k])), null_sd=float(np.nanstd(null[k])))
    return dict(stats=pv, null_model=L.model_meta(nm), n_entries=obs["n_entries"]), nm, design, null, C, npair


def agent_slopes(xbar, v, valid, wk, T, min_days=6):
    out = []
    for i in range(xbar.shape[0]):
        if valid[i].sum() < min_days:
            continue
        C, npair = L.two_time(xbar[i:i + 1], v[i:i + 1], valid[i:i + 1])
        A, _, ne = L.aging_slope(L.entries(C, npair, wk, tw_min=2, tau_max=L.tau_max_for(T)))
        if np.isfinite(A):
            out.append((i, A, int(valid[i].sum()), int(np.argmax(valid[i])) + 1))
    return out


def mu_bootstrap(fitM1, nm, design, wk, T, rng, B, steps_k=None):
    """Simulate the fitted M1 (Box-Cox clock) with the null model's shares; refit M1 -> mu* distribution.
    Also returns the rejuvenation statistic under M1 (for the step-change test)."""
    q, a, lt, mu = fitM1
    q = float(np.clip(q, 0, 0.98)); a = float(np.clip(a, 0, 0.99 - q))
    m = dataclasses.replace(nm, q=q, r=(a,), tau=(float(np.exp(lt)),), mu=float(mu))
    mus, rej = [], []
    for _ in range(B):
        xb, vv, ok = L.simulate_states(m, design, rng)
        C, npair = L.two_time(xb, vv, ok)
        E = L.entries(C, npair, wk, tw_min=2)
        p, _ = L.fit_model("M1", E, x0=fitM1, quick=True)
        mus.append(p[3])
        if steps_k:
            rej.append(step_residual(E, p, steps_k))
    return np.array(mus), np.array(rej) if steps_k else None


def step_residual(E, pM1, steps_k):
    """Mean M1 residual of pairs straddling a step minus that of non-straddling pairs at the same lags."""
    res = E["c"] - L.predict("M1", pM1, E)
    strad = np.zeros(res.size, bool)
    for k in steps_k:
        strad |= (E["d1"] < k) & (E["d2"] >= k)
    vals = []
    for lag in np.unique(E["lag"][strad]):
        s = E["lag"] == lag
        a, b = res[s & strad], res[s & ~strad]
        if a.size and b.size:
            vals.append((a.mean() - b.mean(), a.size))
    if not vals:
        return np.nan
    return float(np.average([x for x, _ in vals], weights=[w for _, w in vals]))


def memory_slope(P: L.Period):
    """Agent-day mean memory jaccard_prev vs log d, agent fixed effects (non-holdout days of the period)."""
    ms = pl.read_parquet(hc.SH / "memory_stats.parquet", columns=["t", "agent", "jaccard_prev"])
    ms = ms.with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).alias("pt_date"))
    dmap = {d: k + 1 for k, d in enumerate(P.pt_dates)}
    ms = ms.filter(pl.col("pt_date").is_in(list(dmap)) & pl.col("agent").is_in(P.agents.tolist())
                   & pl.col("jaccard_prev").is_not_null())
    if ms.height < 20:
        return None
    hc.assert_not_holdout([P.g] * ms.height, ms["pt_date"].to_list())
    g = ms.group_by("agent", "pt_date").agg(pl.col("jaccard_prev").mean())
    d = np.array([dmap[x] for x in g["pt_date"].to_list()], float)
    y = g["jaccard_prev"].to_numpy().astype(float)
    ag = g["agent"].to_numpy()
    X = [np.log(d)] + [(ag == a).astype(float) for a in np.unique(ag)]
    X = np.column_stack(X)
    beta, res, rk, _ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    dof = max(1, y.size - X.shape[1])
    cov = np.linalg.pinv(X.T @ X) * (resid @ resid) / dof
    return dict(slope=float(beta[0]), se=float(np.sqrt(cov[0, 0])), n_agent_days=int(y.size), mean=float(y.mean()))


def analyze(g: int, rng, fast=False):
    t0 = time.time()
    f = 0.2 if fast else 1.0
    P = L.load_period(g)
    if DEBUG_DIR is not None:   # code test only: real counts, random embeddings, no real statistic computed
        r0 = np.random.default_rng(0)
        lat = r0.standard_normal((len(P.agents), P.T, 64)) * 0.5 + r0.standard_normal((len(P.agents), 1, 64)) * 0.6
        P.Z = (lat[P.a_idx, P.k_idx] + r0.standard_normal(P.Z.shape)).astype(np.float32)
    T = P.T
    wk = P.wk_gap
    res = dict(goal_no=g, role=hc.role(g), regime=P.regime, T=T, n_agents=int(len(P.agents)))
    xbar, v, n, valid = L.states(P, "raw", 32)
    res["n_agent_days_valid"] = int(valid.sum())
    res["median_stmts"] = float(np.median(n[valid])) if valid.any() else None
    res["mean_S"] = float(np.mean(((xbar ** 2).sum(-1) - v)[valid]))
    stable = L.stable_subset(valid)
    res["n_stable"] = int(stable.sum())

    # primary: raw, with derived (V-c, swarm mean)
    main, nm, design, null, C, npair = null_test(xbar, v, n, valid, wk, T, rng, int(B_MAIN * f), stable=stable)
    res["raw"] = main
    # null with two OU timescales (robustness of the null form)
    if T >= 8:
        alt2, *_ = null_test(xbar, v, n, valid, wk, T, rng, int(B_VAR * f), stable=stable, with_derived=False, two_scale=True)
        res["raw_null2"] = alt2
    # V-g
    xg, vg, ng, okg = L.states(P, "g", 32)
    res["g"], *_ = null_test(xg, vg, ng, okg, wk, T, rng, int(B_MAIN * f), stable=L.stable_subset(okg), with_derived=True)
    Cg, npg = L.two_time(xg, vg, okg)
    # robustness variants
    rob = {}
    variants = {"chat": (*L.states(P, "chat", 32), 32)}
    if not L.CFG["style"]:          # style-residualized vectors are 32-d only (round 1b)
        variants["n16"] = (*L.states(P, "raw", 16), 16)
        variants["n64"] = (*L.states(P, "raw", 64), 64)
    for name, (xx, vv, nn, oo, nd) in variants.items():
        if oo.sum() < 4:
            continue
        r, *_ = null_test(xx, vv, nn, oo, wk, T, rng, int(B_VAR * f), with_derived=False, ndim=nd)
        rob[name] = r
    # rarefied (10 draws): average C, A from the average; null from the raw-fitted model with rarefied counts
    Cs = []
    for k in range(10):
        xr, vr, nr, okr = L.rarefied_states(P, 32, 8, rng=np.random.default_rng(hc.SEED + k))
        Cr, npr = L.two_time(xr, vr, okr)
        Cs.append(Cr)
    Crare = np.nanmean(Cs, 0)
    rob["rare"] = dict(A=L.slope_set(Crare, npr, wk, T)["A"])
    # calendar clock: A with calendar lags (no weekend covariate), M1 CV on the calendar clock
    Ecal = L.entries(C, npair, wk, clock=P.d_cal, tw_min=2)
    Ecal_A = {k: vv for k, vv in Ecal.items()}
    Ecal_A["lag"] = Ecal["tau"].astype(int)
    tm = L.tau_max_for(int(P.d_cal.max()))
    selc = Ecal_A["lag"] <= tm
    Acal, _, _ = L.aging_slope({k: vv[selc] for k, vv in Ecal_A.items()}, use_wk=False)
    rob["calendar_clock"] = dict(A=Acal)
    res["robust"] = rob

    # swarm-common removed and swarm-mean matrices (for figures)
    xc, vc, okc = L.common_removed(xbar, v, valid)
    Cc, npc = L.two_time(xc, vc, okc)
    m, vm, okm = L.swarm_mean(xbar, v, valid)
    Cm, npm = L.two_time(m, vm, okm)

    # per-agent slopes
    sl = agent_slopes(xbar, v, valid, wk, T)
    Ai = np.array([x[1] for x in sl])
    res["agents"] = dict(n=int(Ai.size), median=float(np.median(Ai)) if Ai.size else None,
                         frac_pos=float((Ai > 0).mean()) if Ai.size else None,
                         wilcoxon_p_greater=float(wilcoxon(Ai, alternative="greater").pvalue) if Ai.size >= 5 else None,
                         per_agent=[dict(agent=int(P.agents[i]), A=float(a), days=int(dv), first_day=int(fd)) for i, a, dv, fd in sl])

    # model fits + LODO CV (raw), and on V-g
    fits_out = {}
    if T >= 6:
        E = L.entries(C, npair, wk, tw_min=2)
        fits = {}
        for mname in ("M0", "M0b", "MQ", "M1"):
            p, sse = L.fit_model(mname, E)
            fits[mname] = p
            fits_out[mname] = dict(params=[float(x) for x in p], wsse=sse)
        cv = L.lodo_cv(E, full_fits=fits)
        fits_out["cv"] = cv
        fits_out["cv_winner"] = min(cv, key=cv.get)
        # calendar clock CV for M1 vs active-day clock
        Ecal2 = {k: vv for k, vv in Ecal.items()}
        Ecal2["lag"] = Ecal["tau"].astype(int)
        cvc = L.lodo_cv(Ecal2, models=("M1", "M0", "MT"))
        fits_out["cv_calendar_clock"] = cvc
        # mu CI and rejuvenation test
        steps_k = None
        if g in hc.STEPS:
            steps_k = [P.pt_dates.index(s) for s in hc.STEPS[g] if s in P.pt_dates]
        mus, rejn = mu_bootstrap(fits["M1"], nm, design, wk, T, rng, int(B_MU * f), steps_k)
        mus = mus[np.isfinite(mus)]
        fits_out["mu_hat"] = float(fits["M1"][3])
        fits_out["mu_ci90"] = [float(np.quantile(mus, 0.05)), float(np.quantile(mus, 0.95))]
        fits_out["mu_boot_mean"] = float(mus.mean())
        if steps_k:
            obs_r = step_residual(E, fits["M1"], steps_k)
            rejn = rejn[np.isfinite(rejn)]
            fits_out["rejuvenation"] = dict(steps=[hc.STEPS[g][i] for i in range(len(hc.STEPS[g])) if hc.STEPS[g][i] in P.pt_dates],
                                            obs=obs_r, null_mean=float(rejn.mean()), null_sd=float(rejn.std()),
                                            p_lower=L.p_lower(obs_r, rejn))
        # V-g fits
        Eg = L.entries(Cg, npg, wk, tw_min=2)
        fg = {mname: L.fit_model(mname, Eg)[0] for mname in ("M0", "M0b", "MQ", "M1")}
        fits_out["g_cv"] = L.lodo_cv(Eg, full_fits=fg)
        fits_out["g_mu_hat"] = float(fg["M1"][3])
    res["fits"] = fits_out

    # design power at the fitted nuisance parameters
    pw = {}
    keys = ("A", "A_early", "A_late", "A_c")
    crit = {k: np.nanquantile(null[k], 0.95) for k in keys}
    crit25 = {k: np.nanquantile(null[k], 0.975) for k in ("A", "A_c")}
    for mu in (0.5, 1.0):
        alt = L.null_distribution(L.alt_model(nm, mu, T), design, wk, T, int(B_POW * f), rng, stable=stable, with_derived=True)
        for k in keys:
            pw[f"{k}|mu={mu}"] = float(np.nanmean(alt[k] > crit[k]))
            pw[f"{k}_alt_mean|mu={mu}"] = float(np.nanmean(alt[k]))
            a = alt[k][np.isfinite(alt[k])]
            # Amendment 1: is aging of this size rejected? P(A_alt <= A_obs)
            pw[f"{k}_p_alt|mu={mu}"] = float((1 + (a <= main["stats"][k]["obs"]).sum()) / (1 + a.size)) if a.size else None
        pw[f"coprimary|mu={mu}"] = float(np.nanmean((alt["A"] > crit25["A"]) | (alt["A_c"] > crit25["A_c"])))
    res["power"] = pw

    # joiner clock (#51): A_i on own clock vs kickoff clock
    if g == 51:
        jo = []
        for i, a, dv, fd in sl:
            if fd <= 2:
                continue
            ks = np.flatnonzero(valid[i])
            sub = slice(ks[0], T)
            C1, np1 = L.two_time(xbar[i:i + 1, sub], v[i:i + 1, sub], valid[i:i + 1, sub])
            Aown, _, _ = L.aging_slope(L.entries(C1, np1, wk[sub], tw_min=2, tau_max=L.tau_max_for(T - ks[0])))
            jo.append(dict(agent=int(P.agents[i]), first_day=int(fd), days=int(dv), A_kickoff_clock=float(a), A_own_clock=float(Aown)))
        res["joiners"] = jo

    res["memory"] = memory_slope(P) if DEBUG_DIR is None else None

    # verdict ingredients (card rule; applied in summarize.py)
    out_dir = (hc.OUT if DEBUG_DIR is None else DEBUG_DIR) / f"G{g:02d}"
    tag = L.cfg_tag()
    if tag != "r1":                 # round 1b configurations: G<NN>/r1b/*_<tag>.*
        out_dir = out_dir / "r1b"
    out_dir.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out_dir / ("matrices.npz" if tag == "r1" else f"matrices_{tag}.npz"), C=C, npair=npair, Cg=Cg,
                        npg=npg, Cc=Cc, npc=npc, Cm=Cm, npm=npm, Crare=Crare, d_cal=P.d_cal, wk=wk)
    res["runtime_s"] = round(time.time() - t0, 1)
    res["null_kind"] = NULL_KIND
    res["config"] = dict(L.CFG)
    fn = "result.json" if NULL_KIND == "iso" else "result_aniso.json"
    if tag != "r1":
        fn = fn.replace(".json", f"_{tag}.json")
    (out_dir / fn).write_text(json.dumps(res, indent=1, default=float))
    print(f"G{g:02d}: T={T} A={main['stats']['A']['obs']:+.4f} p={main['stats']['A']['p_upper']:.3f} "
          f"A_g={res['g']['stats']['A']['obs']:+.4f} p={res['g']['stats']['A']['p_upper']:.3f} "
          f"mu={fits_out.get('mu_hat', np.nan):+.2f} {fits_out.get('mu_ci90')} cv={fits_out.get('cv_winner')} "
          f"pow={pw['A|mu=0.5']:.2f} ({res['runtime_s']}s)", flush=True)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--periods", default=None, help="comma-separated goal numbers")
    ap.add_argument("--role", default=None, choices=["long", "medium", "short"])
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--fast", action="store_true", help="fewer bootstrap draws (debugging only)")
    ap.add_argument("--null", default="iso", choices=["iso", "aniso"])
    # round 1b (2026-10-04): any of these switches to the corrected inputs (shared goal fields; scheme/build_r1b.py)
    ap.add_argument("--r1b", action="store_true", help="corrected inputs with the defaults below")
    ap.add_argument("--emb", default=None, choices=["bge_small", "gte_modernbert"])
    ap.add_argument("--dedupe", default="none", choices=["none", "copies", "restate"])
    ap.add_argument("--style", action="store_true")
    args = ap.parse_args()
    if args.r1b or args.emb or args.dedupe != "none" or args.style:
        L.configure(args.emb or "bge_small", args.dedupe, args.style)
    print("config", L.cfg_tag(), flush=True)
    global NULL_KIND
    NULL_KIND = args.null
    if args.all:
        pers = hc.ALL_PERIODS
    elif args.role:
        pers = {"long": hc.LONG, "medium": hc.MEDIUM, "short": hc.SHORT}[args.role]
    else:
        pers = [int(x) for x in args.periods.split(",")]
    held = hc.held_out_goals()
    for g in pers:
        if g in held:
            raise RuntimeError(f"#{g} is in the locked holdout")
        rng = np.random.default_rng(hc.SEED + g)
        analyze(g, rng, fast=args.fast)
    if DEBUG_DIR is not None:
        return
    if L.cfg_tag() != "r1":
        return                      # round-1b runs record their config inside each result file
    hc.write_provenance({"null": NULL_KIND, "B_main": B_MAIN, "B_var": B_VAR, "B_mu": B_MU, "B_pow": B_POW, "n_dim": 32,
                         "min_stmts": hc.MIN_STMTS, "periods": pers},
                        ["H20/statements.parquet", "H20/stmt_w64.npy", "H20/days.parquet", "H20/goal_dirs",
                         "shared/memory_stats"], "hypotheses/H20-content-aging/analysis/run_periods.py")


if __name__ == "__main__":
    main()
