"""H43 round 2 synthetic validation on the real skeletons (rows, agents, days, reads, covariates real; outcomes simulated).

  R2  G51 before 08-21, after-PAUSE timer wakes, simulated sequentially inside traps (stop at the first escape; later
      real wakes of that trap, and the nudges placed on them, drop out: re-firing on non-responders).
      W0 nudge +0.3, aging -0.4 per ln k, per-trap frailty SD 1, no facilitation; W1 W0 + facilitation +0.5 for re-fires;
      W2 nudge effect 0.6 - 0.2 ln k, no facilitation; W3 facilitation +0.5 only when no context reset lies between the
      two nudges (reset main effect +1.0).
  R3  G51 active-at-read receiving calls. W0 no dose effect; W1 saturating f = (0.8, 1.07, 1.15); W2 additive
      f = (0.8, 1.6, 2.4); W3 no dose effect, talk +0.5 per ln window; W4 W1 simulated on doses with 10% of directed
      items moved to the neighbouring call (start error), estimated on the ledger doses.
  R5  regime-III after-PAUSE wakes (G36-G44, G51). W0 beta_re = beta_fresh = 0.6; W1 beta_re = 0.3 beta_fresh;
      W2 W0 with agent-day responsiveness (baseline +/-0.5, directed effect x 0.3 / x 1.7).
  R6  G51 wakes in the NE43 before/after windows. W0 covariates shift only; W1 W0 + a step of -0.2 after 08-21.
Tests are Wald tests at 5% (analytic Newton covariance); a day-bootstrap check of the SE is run on 3 R2 replicates.

Output: data/processed/H43-kick-refractory-window/r2/synthetic/{r2,r3,r5,r6}.json
Usage:  uv run python hypotheses/H43-kick-refractory-window/analysis/synthetic_r2.py --only r2 [--reps 40]
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r2lib as R  # noqa: E402

SYN = R.OUT / "synthetic"


def sim_traps(lin: np.ndarray, trap: np.ndarray, rng) -> tuple[np.ndarray, np.ndarray]:
    """Draw y per row; keep rows of a trap up to and including the first simulated escape."""
    y = (rng.random(len(lin)) < R._sig(lin)).astype(float)
    # rows sorted by trap then time: escapes earlier in the same trap
    cs = np.cumsum(y)
    start = np.r_[0, np.flatnonzero(np.diff(trap)) + 1]
    lens = np.diff(np.r_[start, len(y)])
    offset = np.repeat(cs[start] - y[start], lens)
    keep = (cs - y - offset) == 0
    return y, keep


def agent_fx(agent: np.ndarray, rng, sd=0.5):
    lev = np.unique(agent)
    a = dict(zip(lev, rng.normal(0, sd, len(lev))))
    return np.array([a[x] for x in agent])


def wald(fit, names, name):
    b, s = R.coef(fit, names, name)
    return b, s, abs(b / s) > 1.96 if s > 0 else False


def contrast(fit, names, a, b):
    i, j = names.index(a), names.index(b)
    d = fit["beta"][i] - fit["beta"][j]
    v = fit["cov"][i, i] + fit["cov"][j, j] - 2 * fit["cov"][i, j]
    s = float(np.sqrt(max(v, 1e-12)))
    return float(d), s, abs(d / s) > 1.96


# ------------------------------------------------------------------------------------------------ R2
def run_r2(reps: int, rng) -> dict:
    w = R.add_nudge_history(R.load_wakes((51,), date_to=R.NE43)).sort("trap", "t_call")
    trap = w["trap"].to_numpy()
    agent = w["agent"].to_numpy()
    lk = np.log(w["k"].to_numpy())
    st = w["nprev_state"].to_numpy()
    N = w["N_now"].to_numpy().astype(float)
    rb = w["reset_between"].to_numpy().astype(float)
    ref = N * (st > 0)
    out = {"n_rows": w.height, "n_nudged": int(N.sum()), "n_refire": int(ref.sum()), "worlds": {}}
    worlds = {
        "W0": dict(fac=0.0, keff=False, resetfac=False),
        "W1": dict(fac=0.5, keff=False, resetfac=False),
        "W2": dict(fac=0.0, keff=True, resetfac=False),
        "W3": dict(fac=0.5, keff=False, resetfac=True),
    }
    for wn0, cfg in [(f"{k}_{m}", dict(v, mode=m)) for m in ("seq", "ind") for k, v in worlds.items()]:
        wn = wn0
        res = {"dF": [], "dF_rej": [], "dF_proxy": [], "dF_proxy_rej": [], "reset_int": [], "reset_rej": [], "n_kept": []}
        for r in range(reps):
            fr = rng.normal(0, 1.0, trap.max() + 1)[trap]
            beff = (0.6 - 0.2 * lk) if cfg["keff"] else 0.3
            fac = cfg["fac"] * ref * ((1 - rb) if cfg["resetfac"] else 1.0)
            lin = -0.1 + agent_fx(agent, rng) - 0.4 * lk + fr + beff * N + fac + (1.0 * rb if cfg["resetfac"] else 0.0)
            y, keep = sim_traps(lin, trap, rng)
            if cfg["mode"] == "ind":
                keep = np.ones(len(y), bool)
            wk = w.filter(pl.Series(keep))
            yk = y[keep]
            X, nm = R.r2_design(wk)
            f = R.fe_logit(X, yk, wk["agent"].to_numpy())
            d, s, rej = contrast(f, nm, "N_refire", "N_first")
            res["dF"].append(d); res["dF_rej"].append(rej)
            Xp, nmp = R.r2_design(wk, proxies=True)
            fp = R.fe_logit(Xp, yk, wk["agent"].to_numpy())
            d2, s2, rej2 = contrast(fp, nmp, "N_refire", "N_first")
            res["dF_proxy"].append(d2); res["dF_proxy_rej"].append(rej2)
            # reset partition: N_refire x reset_between, with reset_between main effect
            rbk = wk["reset_between"].to_numpy().astype(float)
            refk = (wk["N_now"].to_numpy() & (wk["nprev_state"].to_numpy() > 0)).astype(float)
            Xr = np.column_stack([X, rbk, refk * rbk])
            fr_ = R.fe_logit(Xr, yk, wk["agent"].to_numpy())
            b, sb, rr = wald(fr_, nm + ["reset_between", "N_refire_x_reset"], "N_refire_x_reset")
            res["reset_int"].append(b); res["reset_rej"].append(rr)
            res["n_kept"].append(int(keep.sum()))
        out["worlds"][wn] = {k: (float(np.mean(v)) if k.endswith("rej") else
                                 {"mean": float(np.mean(v)), "sd": float(np.std(v))}) for k, v in res.items()}
        print(f"R2 {wn}: dF {np.mean(res['dF']):+.3f} rej {np.mean(res['dF_rej']):.2f} | proxy {np.mean(res['dF_proxy']):+.3f} "
              f"rej {np.mean(res['dF_proxy_rej']):.2f} | reset int {np.mean(res['reset_int']):+.3f} rej {np.mean(res['reset_rej']):.2f}",
              flush=True)
    # bootstrap-vs-analytic SE check (W0)
    chk = []
    for r in range(3):
        fr = rng.normal(0, 1.0, trap.max() + 1)[trap]
        lin = -0.1 + agent_fx(agent, rng) - 0.4 * lk + fr + 0.3 * N
        y, keep = sim_traps(lin, trap, rng)
        wk = w.filter(pl.Series(keep))
        yk = y[keep]
        X, nm = R.r2_design(wk)
        ag = wk["agent"].to_numpy()
        f = R.fe_logit(X, yk, ag)
        d, s, _ = contrast(f, nm, "N_refire", "N_first")
        day = np.unique(wk["pt_date"].to_numpy(), return_inverse=True)[1]
        bd = []
        for idx in R.day_boot(day, rng, 100):
            fb = R.fe_logit(X[idx], yk[idx], ag[idx])
            bd.append(contrast(fb, nm, "N_refire", "N_first")[0])
        chk.append({"analytic_se": s, "boot_se": float(np.std(bd, ddof=1))})
    out["se_check"] = chk
    print("R2 SE check", chk, flush=True)
    return out


# ------------------------------------------------------------------------------------------------ R3
def move_items(d: pl.DataFrame, rng, share=0.1) -> np.ndarray:
    """Dose after moving each directed item, with probability share, to the previous or next call (same agent-day)."""
    dose = d["dose"].to_numpy().copy()
    aday = d["aday"].to_numpy()
    new = dose.copy()
    idx = np.flatnonzero(dose > 0)
    for i in idx:
        mv = rng.binomial(dose[i], share)
        for _ in range(mv):
            j = i + (1 if rng.random() < 0.5 else -1)
            if 0 <= j < len(dose) and aday[j] == aday[i]:
                new[i] -= 1
                new[j] += 1
    return new


def run_r3(reps: int, rng) -> dict:
    d = R.dose_table((51,), read_state="active")
    agent = d["agent"].to_numpy()
    lw = np.log(d["window_s"].to_numpy())
    lw_c = lw - np.median(lw)
    ua = np.log1p(d["n_und_agent"].to_numpy())
    dose = d["dose"].to_numpy()
    out = {"n_rows": d.height, "dose_counts": {str(k): int((np.minimum(dose, 3) == k).sum()) for k in range(4)}, "worlds": {}}
    F = {"W0": (0, 0, 0), "W1": (0.8, 1.07, 1.15), "W2": (0.8, 1.6, 2.4), "W3": (0, 0, 0), "W4": (0.8, 1.07, 1.15)}
    for wn, f in F.items():
        res = {"f1": [], "m2": [], "rho2": [], "f1_rej": [], "m2_rej": [], "f1_nowin": [], "f1_nowin_rej": []}
        for r in range(reps):
            dd = move_items(d, rng) if wn == "W4" else dose
            fd = np.select([dd == 1, dd == 2, dd >= 3], list(f), 0.0)
            lin = -2.0 + agent_fx(agent, rng) + fd + 0.1 * ua + (0.5 * lw_c if wn == "W3" else 0.0)
            y = (rng.random(len(lin)) < R._sig(lin)).astype(float)
            X, nm = R.dose_design(d)
            fit = R.fe_logit(X, y, agent)
            m = R.marginals(fit["beta"], nm)
            b1, s1, rj1 = wald(fit, nm, "f1")
            dm, sm, rjm = contrast(fit, nm, "f2", "f1")
            res["f1"].append(m["f1"]); res["m2"].append(m["m2"]); res["rho2"].append(m["rho2"])
            res["f1_rej"].append(rj1); res["m2_rej"].append(rjm)
            Xn, nmn = R.dose_design(d, window=False)
            fn = R.fe_logit(Xn, y, agent)
            bn, sn, rjn = wald(fn, nmn, "f1")
            res["f1_nowin"].append(bn); res["f1_nowin_rej"].append(rjn)
        out["worlds"][wn] = {k: (float(np.mean(v)) if k.endswith("rej") else
                                 {"mean": float(np.nanmean(v)), "sd": float(np.nanstd(v))}) for k, v in res.items()}
        out["worlds"][wn]["truth"] = {"f1": f[0], "m2": f[1] - f[0], "rho2": (f[1] - f[0]) / f[0] if f[0] else None}
        print(f"R3 {wn}: f1 {np.mean(res['f1']):+.3f} (rej {np.mean(res['f1_rej']):.2f}) m2 {np.mean(res['m2']):+.3f} "
              f"(rej {np.mean(res['m2_rej']):.2f}) rho2 {np.nanmean(res['rho2']):.3f} | no-window f1 {np.mean(res['f1_nowin']):+.3f} "
              f"rej {np.mean(res['f1_nowin_rej']):.2f}", flush=True)
    return out


# ------------------------------------------------------------------------------------------------ R5
def r5_fit_periods(w: pl.DataFrame, y: np.ndarray, min_rek: int = 5):
    per = {}
    for g in sorted(set(w["goal_no"].to_list())):
        m = (w["goal_no"] == g).to_numpy()
        wg = w.filter(pl.Series(m))
        n_rek = int((wg["D_now"] & (wg["dclass"] == 1)).sum())
        n_fr = int((wg["D_now"] & (wg["dclass"] == 0)).sum())
        if n_rek < min_rek or n_fr < min_rek:
            per[g] = {"n_rek": n_rek, "n_fresh": n_fr, "fit": False}
            continue
        X, nm = R.r5_design(wg)
        f = R.fe_logit(X, y[m], wg["agent"].to_numpy())
        bf, sf = R.coef(f, nm, "D_fresh")
        br, sr = R.coef(f, nm, "D_rekick")
        dd, sd, _ = contrast(f, nm, "D_rekick", "D_fresh")
        per[g] = {"n_rek": n_rek, "n_fresh": n_fr, "fit": True, "b_fresh": bf, "se_fresh": sf, "b_re": br, "se_re": sr,
                  "d": dd, "se_d": sd}
    fitted = [v for v in per.values() if v.get("fit")]
    pool = {k: R.dl_pool([v[f"{k}"] for v in fitted], [v[f"se_{k.split('_')[-1]}" if k != "d" else "se_d"] for v in fitted])
            for k in ("b_fresh", "b_re", "d")}
    return per, pool


def run_r5(reps: int, rng) -> dict:
    w = R.add_directed_history(R.load_wakes()).sort("goal_no", "trap", "t_call")
    trap = (w["goal_no"].cast(pl.Int64) * 10_000_000 + w["trap"]).to_numpy()
    trap = np.unique(trap, return_inverse=True)[1]
    agent = w["agent"].to_numpy()
    lk = np.log(w["k"].to_numpy())
    c = w["dclass"].to_numpy()
    D = w["D_now"].to_numpy().astype(float)
    aday = np.unique(w["aday"].to_numpy() + "|" + w["goal_no"].cast(pl.Utf8).to_numpy(), return_inverse=True)[1]
    out = {"n_rows": w.height, "worlds": {}}
    for wn0 in [f"{k}_{m}" for m in ("seq", "ind") for k in ("W0", "W1", "W2")]:
        wn, mode = wn0.split("_")
        res = {"pool_d": [], "pool_d_rej": [], "pool_R": [], "g51_d": [], "g51_rej": [], "k": []}
        for r in range(reps):
            fr = rng.normal(0, 1.0, trap.max() + 1)[trap]
            bre = 0.18 if wn == "W1" else 0.6
            if wn == "W2":
                z = rng.random(aday.max() + 1) < 0.5
                mult = np.where(z, 0.3, 1.7)[aday]
                base = np.where(z, -0.5, 0.5)[aday]
            else:
                mult, base = 1.0, 0.0
            eff = np.where(c == 1, bre, 0.6) * D * mult
            lin = -0.1 + agent_fx(agent, rng) - 0.4 * lk + fr + base + eff
            y, keep = sim_traps(lin, trap, rng)
            if mode == "ind":
                keep = np.ones(len(y), bool)
            wk = w.filter(pl.Series(keep))
            per, pool = r5_fit_periods(wk, y[keep])
            pdl = pool["d"]
            res["pool_d"].append(pdl.get("mu", np.nan))
            res["pool_d_rej"].append(bool(pdl.get("k", 0) and (pdl["ci"][0] > 0 or pdl["ci"][1] < 0)))
            pf, pr = pool["b_fresh"], pool["b_re"]
            res["pool_R"].append(pr["mu"] / pf["mu"] if pf.get("k") and pf["mu"] > 0.05 else np.nan)
            res["k"].append(pdl.get("k", 0))
            g = per.get(51, {})
            if g.get("fit"):
                res["g51_d"].append(g["d"]); res["g51_rej"].append(abs(g["d"] / g["se_d"]) > 1.96)
        out["worlds"][wn0] = {k: (float(np.mean(v)) if k.endswith("rej") else
                                  {"mean": float(np.nanmean(v)), "sd": float(np.nanstd(v))}) for k, v in res.items()}
        print(f"R5 {wn0}: pooled d {np.nanmean(res['pool_d']):+.3f} rej {np.mean(res['pool_d_rej']):.2f} R {np.nanmean(res['pool_R']):.2f} "
              f"k {np.mean(res['k']):.1f} | G51 d {np.nanmean(res['g51_d']):+.3f} rej {np.mean(res['g51_rej']):.2f}", flush=True)
    return out


# ------------------------------------------------------------------------------------------------ R6
def r6_design(w: pl.DataFrame, step_cols: list[str]):
    X0, nm = R.nuisance(w)
    cols = [X0, w["D_now"].to_numpy()[:, None], w["N_now"].to_numpy()[:, None], w["focus"].to_numpy()[:, None],
            np.log(w["n_present"].to_numpy().clip(1, None))[:, None], w["first_of_day"].to_numpy()[:, None]]
    nm = nm + ["D_now", "N_now", "focus", "ln_present", "first_of_day"]
    for s in step_cols:
        cols.append(w[s].to_numpy()[:, None]); nm.append(s)
    return np.hstack([np.asarray(x, float) for x in cols]), nm


def run_r6(reps: int, rng) -> dict:
    w = R.load_wakes((51,), date_from=R.PRE_WIN[0], date_to=R.POST_WIN[1]).with_columns(
        (pl.col("pt_date") >= R.NE43).alias("post"))
    agent = w["agent"].to_numpy()
    X, nm = r6_design(w, [])
    beta = np.zeros(len(nm))
    plant = {"ln_k": -0.4, "ln1p_peer_und": 0.1, "D_now": 0.6, "N_now": 0.3, "focus": -0.1, "ln_present": -0.3,
             "first_of_day": 0.3, "hday_1": 0.1, "hday_2": 0.0, "hday_3": -0.1, "hday_4": -0.2}
    for k, v in plant.items():
        beta[nm.index(k)] = v
    post = w["post"].to_numpy().astype(float)
    out = {"n_rows": w.height, "worlds": {}}
    Xs, nms = r6_design(w, ["post"])
    for wn, step in (("W0", 0.0), ("W1", -0.2)):
        est = []
        for r in range(reps):
            lin = -0.1 + agent_fx(agent, rng) + X @ beta + step * post
            y = (rng.random(len(lin)) < R._sig(lin)).astype(float)
            f = R.fe_logit(Xs, y, agent)
            est.append(R.coef(f, nms, "post")[0])
        out["worlds"][wn] = {"truth": step, "mean": float(np.mean(est)), "sd": float(np.std(est))}
        print(f"R6 {wn}: step truth {step} est {np.mean(est):+.3f} sd {np.std(est):.3f}", flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=["r2", "r3", "r5", "r6"], required=True)
    ap.add_argument("--reps", type=int, default=40)
    a = ap.parse_args()
    rng = np.random.default_rng(R.SEED + {"r2": 2, "r3": 3, "r5": 5, "r6": 6}[a.only])
    t0 = time.time()
    res = {"r2": run_r2, "r3": run_r3, "r5": run_r5, "r6": run_r6}[a.only](a.reps, rng)
    res["reps"] = a.reps
    res["secs"] = round(time.time() - t0, 1)
    res["built_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    R.jdump(res, SYN / f"{a.only}.json")
    print(f"done {a.only} in {res['secs']} s")


if __name__ == "__main__":
    main()
