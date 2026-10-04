"""H16 synthetic validation (axis F). Runs the SAME estimators as the real-data pipeline (h16lib) on simulated agents.

S1  Overdamped Langevin agents in a double well U(x) = dU (x^2-1)^2 + c x (left well = idle, right = active), noise T,
    observed only through event times (Poisson readout: 3/min in the active well, 0.01/min in the idle well), with
    4-h days, cold start in the active well each day (the village scheduler), right-censoring at the day end.
    S1a dwell law: hazard slope on ln(elapsed) for TS1 spells; exponential truth vs a deepening trap; agent frailty.
    S1b censoring: naive vs KM / exponential-MLE dwell estimators vs truth, as a function of mean dwell / day length.
    S1c landscape: Boltzmann barrier on the EWMA coordinate vs true dU/T; observed first-passage rate vs the
        parameter-free 1D MFPT (occupancy + Kramers-Moyal diffusion), Kramers saddle formula and the 1-min MSM.
    S1d kicks: barrier lowering (force f for 2 min per kick; hazard exponential in dose) vs independent triggers
        (each kick resets to the active well with prob q; additive); dose-law selection at high and village kick rates.
S2  Gate model (regime-III pause chains): per-gate escape logit = theta_agent + theta_age ln k + theta_m n_mentions,
    with agent frailty; recovery of theta_age and theta_m with and without agent fixed effects.
S3  Swarm: Glauber agents with a daily field and mean-field coupling betaJ0 in {0, 0.3, 0.6, 1.3, 1.8}; bimodality of
    m(t) vs the day-swap null, betaJ0 recovery; plus a common-stall scenario (betaJ0 = 0, everyone silent in blocks).

Usage: uv run python hypotheses/H16-metastable-traps-kramers/analysis/synthetic.py [--quick]
Outputs: data/processed/H16-metastable-traps-kramers/synthetic/synthetic_results.json, figures/synthetic_validation.pdf
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h16lib as L  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import optimize, special  # noqa: E402

QUICK = "--quick" in sys.argv
RNG = np.random.default_rng(L.SEED)
OUTD = L.OUT / "synthetic"
FIG = L.HDIR / "figures"
DAY_MIN = 240
R: dict = {}
T0 = time.time()


def log(*a):
    print(f"[{time.time() - T0:6.1f}s]", *a, flush=True)


# ============================================================================ S1 simulator
# Natural units: U(x) = (x^2 - 1)^2 + c x (barrier 1 at c = 0), temperature T = 1/b (b = barrier / T at c = 0),
# mobility mu = 1 / (8 tau_relax) so the intra-well relaxation time is tau_relax minutes whatever the barrier.
# Euler-Maruyama with dt = 0.01 min (mu U'' dt = dt / tau_relax = 0.05 at tau_relax = 0.2 min).

def kramers_true(b, c, tau=0.2):
    """Kramers rate (per min) out of the left well, and the left barrier in units of T."""
    mu, T = 1 / (8 * tau), 1 / b
    U = lambda x: (x ** 2 - 1) ** 2 + c * x
    U2 = lambda x: 12 * x ** 2 - 4
    roots = np.roots([4, 0, -4, c])
    roots = np.sort(roots[np.abs(roots.imag) < 1e-9].real)
    if len(roots) < 3:
        return np.nan, np.nan
    a, s_ = roots[0], roots[1]
    bar = U(s_) - U(a)
    return float(mu * np.sqrt(U2(a) * abs(U2(s_))) / (2 * np.pi) * np.exp(-bar / T)), float(bar / T)


def sim_langevin(par: list[dict], n_days: int, rng, dt=0.01, n_min=DAY_MIN):
    """Simulate agents (one parameter dict each) for n_days; returns rows, W, K (kicks as class A_men), latent dwells.

    par keys: b (barrier/T), c (tilt), tau (relaxation, min), kick_rate (/min), f (force per active kick; lowers the
    left barrier by ~f, i.e. ln HR ~ f b), kick_dur (min), q (trigger probability per kick), gamma (trap deepening:
    barrier += gamma T ln(1 + s/5) while x < 0, s = minutes since entering), lam_act / lam_idle (readout rates /min)."""
    nA = len(par)
    nAD = nA * n_days
    dflt = dict(b=3.0, c=0.0, tau=0.2, kick_rate=0.0, f=0.0, kick_dur=2.0, q=0.0, gamma=0.0, lam_act=3.0, lam_idle=0.01)
    P = {k: np.repeat(np.array([p.get(k, v) for p in par], float), n_days) for k, v in dflt.items()}
    T = 1 / P["b"]; mu = 1 / (8 * P["tau"])
    steps = int(round(n_min / dt))
    kick_times = []
    kc = np.zeros((nAD, steps + 1), np.int16)
    trig = np.zeros((nAD, steps), bool)
    for i in range(nAD):
        n = rng.poisson(P["kick_rate"][i] * n_min)
        ts = np.sort(rng.uniform(0, n_min, n))
        kick_times.append(ts)
        s0 = np.minimum((ts / dt).astype(int), steps - 1)
        s1 = np.minimum(((ts + P["kick_dur"][i]) / dt).astype(int), steps)
        np.add.at(kc[i], s0, 1)
        np.add.at(kc[i], s1, -1)
        trig[i, s0] = True
    kc = np.cumsum(kc[:, :steps], axis=1)
    x = np.ones(nAD)
    s_idle = np.zeros(nAD)
    state = np.ones(nAD, int)
    entry = np.zeros(nAD)
    lat_d, lat_c, lat_a = [], [], []
    ev_i, ev_t = [], []
    sq = np.sqrt(2 * mu * T * dt)
    use_q = (P["q"] > 0).any(); use_g = (P["gamma"] > 0).any()
    for st in range(steps):
        t = st * dt
        if use_g:
            scale = np.where(x < 0, 1 + P["gamma"] * T * np.log1p(s_idle / 5.0), 1.0)
        else:
            scale = 1.0
        force = -(4 * scale * x * (x * x - 1) + P["c"]) + P["f"] * kc[:, st]
        x = x + mu * force * dt + sq * rng.standard_normal(nAD)
        if use_q:
            hit = trig[:, st] & (rng.random(nAD) < P["q"])
            x[hit] = 1.0
        s_idle = np.where(x < 0, s_idle + dt, 0.0)
        to_idle = (state == 1) & (x < -0.5)
        to_act = (state == -1) & (x > 0.5)
        if to_act.any():
            idx = np.nonzero(to_act)[0]
            lat_d.extend(t - entry[idx]); lat_c.extend([False] * len(idx)); lat_a.extend(idx // n_days)
        entry[to_idle] = t
        state[to_idle] = -1
        state[to_act] = 1
        lam = np.where(x > 0, P["lam_act"], P["lam_idle"])
        e = rng.random(nAD) < lam * dt
        if e.any():
            idx = np.nonzero(e)[0]
            ev_i.append(idx); ev_t.append(t + rng.uniform(0, dt, len(idx)))
    idx = np.nonzero(state == -1)[0]
    lat_d.extend(n_min - entry[idx]); lat_c.extend([True] * len(idx)); lat_a.extend(idx // n_days)
    ev_i = np.concatenate(ev_i) if ev_i else np.zeros(0, int)
    ev_t = np.concatenate(ev_t) if ev_t else np.zeros(0)
    rows, W, K = {}, {}, {}
    for d in range(n_days):
        W[f"d{d:03d}"] = {"t0": d * 86400.0, "t1": d * 86400.0 + n_min * 60.0}
    o = np.argsort(ev_t, kind="stable")
    ev_i, ev_t = ev_i[o], ev_t[o]
    order = np.argsort(ev_i, kind="stable")
    ev_i_s, ev_t_s = ev_i[order], ev_t[order]
    bounds = np.searchsorted(ev_i_s, np.arange(nAD + 1))
    for i in range(nAD):
        a, d = i // n_days, i % n_days
        dk = f"d{d:03d}"
        tt = np.sort(ev_t_s[bounds[i]:bounds[i + 1]]) * 60.0 + W[dk]["t0"]
        rows[(a, dk)] = {"act": tt, "pause_t": np.zeros(0), "pause_s": np.zeros(0), "wait_t": np.zeros(0)}
        K.setdefault(a, {}).setdefault("A_men", [])
        K[a]["A_men"].append(kick_times[i] * 60.0 + W[dk]["t0"])
    for a in K:
        K[a]["A_men"] = np.sort(np.concatenate(K[a]["A_men"]))
    lat = {"d": np.array(lat_d), "c": np.array(lat_c), "agent": np.array(lat_a)}
    return rows, W, K, lat


def latent_slope(lat, fe=True):
    """Same hazard-slope estimator applied to the latent (true) idle dwells, as the apples-to-apples truth."""
    df = pl.DataFrame({"agent": lat["agent"].astype(np.int16), "pt_date": [f"x{i}" for i in range(len(lat["d"]))],
                       "t0": np.zeros(len(lat["d"])), "t1": lat["d"] * 60.0, "censored": lat["c"],
                       "tod": np.zeros(len(lat["d"]), np.float32)})
    H = L.ts1_hazard_rows(df, None)
    f = L.glm_fe(H["y"], np.log(H["elapsed"] / 60.0)[:, None], H["agent"] if fe else None, "cloglog")
    return float(f["beta"][0]), float(f["se"][0])


def ts1_slope(rows, W, K=None, fe="agent", extra=None, bin_s=L.BIN_S, look=L.LOOK_FAST_S, robust=False, el_min=None,
              el_max=None):
    ts1 = L.build_ts1(rows, W, K, robust=robust)
    ts1 = ts1.filter(pl.col("first_act_s") >= 0)
    H = L.ts1_hazard_rows(ts1, K, bin_s=bin_s, look_fast=look)
    if el_min is not None or el_max is not None:
        m = (H["elapsed"] >= (el_min or 0)) & (H["elapsed"] < (el_max or 1e12))
        H = {k: v[m] for k, v in H.items()}
    X = [np.log(H["elapsed"] / 60.0)]
    if extra == "dose":
        X += list(L.dose_dummies(H["f_A_men"]).T)
    X = np.stack(X, 1)
    g = None if fe is None else H[fe]
    return L.glm_fe(H["y"], X, g, "cloglog"), ts1, H


# ============================================================================ S1a dwell law
log("S1a dwell law")
nd = 10 if QUICK else 20
s1a = {}
for name, extra, hetero in [("exponential", {}, False), ("deepening_gamma1", {"gamma": 1.0}, False),
                            ("deepening_gamma2", {"gamma": 2.0}, False), ("frailty_exponential", {}, True),
                            ("exponential_sparse_readout", {"lam_act": 0.8}, False)]:
    par = []
    for a in range(12):
        p = dict(b=3.0, **extra)
        if hetero:
            p["b"] = float(np.clip(RNG.normal(3.0, 0.8), 1.8, 4.5))
        par.append(p)
    rows, W, K, lat = sim_langevin(par, nd, RNG)
    res = {}
    for fe in (None, "agent", "agentday"):
        f, ts1, H = ts1_slope(rows, W, None, fe)
        res[str(fe)] = {"beta": float(f["beta"][0]), "se": float(f["se"][0]), "n_events": f["n_events"]}
    for robust in (False, True):
        for lo, hi, tag in ((180, 600, "3-10min"), (600, 4 * 3600, ">=10min")):
            f, _, _ = ts1_slope(rows, W, None, "agent", robust=robust, el_min=lo, el_max=hi)
            res[f"{'TS1r' if robust else 'TS1'}|agent|{tag}"] = {"beta": float(f["beta"][0]), "se": float(f["se"][0]),
                                                                  "n_events": f["n_events"]}
    res["latent_truth_agentFE"] = dict(zip(("beta", "se"), latent_slope(lat, True)))
    res["latent_truth_pooled"] = dict(zip(("beta", "se"), latent_slope(lat, False)))
    res["n_spells"] = int(ts1.height)
    res["censored_frac"] = float(ts1["censored"].mean())
    s1a[name] = res
    log(name, {k: (round(v["beta"], 3), round(v["se"], 3)) for k, v in res.items() if isinstance(v, dict) and "beta" in v})
R["S1a_dwell_law"] = s1a

# ============================================================================ S1b censoring
log("S1b censoring")
s1b = []
for bb in (2.0, 3.0, 4.0, 5.0, 6.0):
    par = [dict(b=bb) for _ in range(10)]
    rows, W, K, lat = sim_langevin(par, 10 if QUICK else 16, RNG)
    k_true, _ = kramers_true(bb, 0.0)
    ts1 = L.build_ts1(rows, W, robust=True).filter(pl.col("first_act_s") >= 0)
    d = ts1["dwell_s"].to_numpy() / 60.0; c = ts1["censored"].to_numpy()
    s1b.append({"b": bb, "true_mean_min": 1 / k_true, "latent_exp_mle": float(lat["d"].sum() / max((~lat["c"]).sum(), 1)),
                "latent_naive_completed": float(lat["d"][~lat["c"]].mean()) if (~lat["c"]).any() else np.nan,
                "naive_completed_mean": float(d[~c].mean()) if (~c).any() else np.nan,
                "naive_all_as_events": float(d.mean()), "exp_mle": float(d.sum() / max((~c).sum(), 1)),
                "km_median": L.km_median(d, c), "censored_frac": float(c.mean()), "n": int(len(d)),
                "latent_censored_frac": float(lat["c"].mean())})
    log({k: round(v, 3) if isinstance(v, float) else v for k, v in s1b[-1].items()})
R["S1b_censoring"] = s1b

# ============================================================================ S1c landscape / Kramers
log("S1c landscape")
grid = []
for lam_act in (3.0, 0.8):
    for bb in (2.0, 3.0, 4.0, 5.0):
        for c in (-0.2, 0.0, 0.2):
            for tau in (0.2, 0.5):
                grid.append(dict(b=bb, c=c, tau=tau, lam_act=lam_act))
if QUICK:
    grid = grid[::3]
rows, W, K, lat = sim_langevin(grid, 12 if QUICK else 20, RNG)
MA = L.minute_activity(rows, W)
series, acts = {}, {}
for d, (ag, A) in MA.items():
    X = L.ewma(A.astype(float))
    for r, a in enumerate(ag):
        series.setdefault(int(a), []).append(X[r])
        acts.setdefault(int(a), []).append(A[r])
cells = []
for a, p in enumerate(grid):
    if a not in series:
        continue
    cell = L.rc_cell(series[a], acts=acts[a])
    k_true, bar_true = kramers_true(p["b"], p["c"], p["tau"])
    m = lat["agent"] == a
    lat_rate = (~lat["c"][m]).sum() / max(lat["d"][m].sum(), 1e-9)
    rec = {"b": p["b"], "tau": p["tau"], "lam_act": p["lam_act"], "c": p["c"], "bar_true_over_T": bar_true, "k_kramers_true": k_true,
           "k_latent_obs": float(lat_rate), "double_well": bool(cell.get("landscape", {}).get("double_well", False))}
    if cell.get("ok") and rec["double_well"]:
        rec.update({"dG": cell["landscape"]["dG"], "xa": cell["landscape"]["xa"], "xb": cell["landscape"]["xb"],
                    "k_obs": cell["obs"]["k"], "n_pass": cell["obs"]["n_events"], "mfpt_1d": cell["mfpt_1d"],
                    "mfpt_kramers": cell["mfpt_kramers"], "mfpt_msm": cell["mfpt_msm"], "mfpt_msm2": cell["mfpt_msm2"],
                    "dU_over_T_drift": cell["dU_over_T_drift"], "T_eff": cell["T_eff_well"]})
    rows_a = {k: v for k, v in rows.items() if k[0] == a}
    t1r = L.build_ts1(rows_a, W, robust=True).filter(pl.col("first_act_s") >= 0)
    if t1r.height:
        k_, ev_, _ = L.deep_rate(t1r)
        if ev_ >= 5:
            rec["k_ts1r"] = k_
    cells.append(rec)
C = pl.DataFrame(cells)
s1c = {"n_cells": len(cells), "frac_double_well": float(C["double_well"].mean())}
ok = C.filter(pl.col("double_well") & pl.col("k_obs").is_not_null() & (pl.col("n_pass") >= 15))


def loglin(xv, yv):
    m = np.isfinite(xv) & np.isfinite(yv)
    if m.sum() < 4:
        return {"n": int(m.sum())}
    b, a = np.polyfit(xv[m], yv[m], 1)
    r = np.corrcoef(xv[m], yv[m])[0, 1]
    return {"n": int(m.sum()), "slope": float(b), "intercept": float(a), "r": float(r),
            "median_abs_log_ratio": float(np.median(np.abs(yv[m] - xv[m])))}


if ok.height:
    lk = np.log(ok["k_obs"].to_numpy())
    s1c["obs_vs_1d"] = loglin(np.log(1 / ok["mfpt_1d"].to_numpy()), lk)
    s1c["obs_vs_kramers_saddle"] = loglin(np.log(1 / ok["mfpt_kramers"].to_numpy()), lk)
    s1c["obs_vs_msm"] = loglin(np.log(1 / ok["mfpt_msm"].to_numpy()), lk)
    s1c["obs_vs_msm2"] = loglin(np.log(1 / ok["mfpt_msm2"].to_numpy()), lk)
    s1c["latent_obs_vs_latent_true_kramers"] = loglin(np.log(ok["k_kramers_true"].to_numpy()), np.log(ok["k_latent_obs"].to_numpy()))
    s1c["obs_vs_latent_true_kramers"] = loglin(np.log(ok["k_kramers_true"].to_numpy()), lk)
    s1c["dG_vs_true_barrier"] = loglin(ok["bar_true_over_T"].to_numpy(), ok["dG"].to_numpy())
    s1c["dG_vs_drift_barrier"] = loglin(ok["dU_over_T_drift"].to_numpy(), ok["dG"].to_numpy())
    s1c["arrhenius_lnk_on_dG"] = loglin(ok["dG"].to_numpy(), lk)
    okr = ok.filter(pl.col("k_ts1r").is_not_null()) if "k_ts1r" in ok.columns else ok.head(0)
    if okr.height:
        s1c["arrhenius_ln_kts1r_deep_on_dG"] = loglin(okr["dG"].to_numpy(), np.log(okr["k_ts1r"].to_numpy()))
        s1c["ln_kts1r_deep_vs_ln_latent"] = loglin(np.log(okr["k_latent_obs"].to_numpy()), np.log(okr["k_ts1r"].to_numpy()))
    s1c["arrhenius_lnk_on_true_barrier"] = loglin(ok["bar_true_over_T"].to_numpy(), np.log(ok["k_latent_obs"].to_numpy()))
log("S1c", {k: v for k, v in s1c.items() if not isinstance(v, dict)}, s1c.get("obs_vs_1d"), s1c.get("obs_vs_msm"))
R["S1c_landscape"] = s1c
R["S1c_cells"] = cells
# single-well false positive rate (no barrier: monostable potentials)
log("S1c single-well false-positive check")
sw_par = [dict(b=bb, c=1.5, lam_act=la) for bb in (2.0, 4.0) for la in (3.0, 0.8)] + \
         [dict(b=0.5, c=0.0, lam_act=la) for la in (3.0, 0.8)]   # c = 1.5: no left minimum; b = 0.5: barrier << T
rows_sw, W_sw, _, _ = sim_langevin(sw_par, 12 if QUICK else 20, RNG)
MA_sw = L.minute_activity(rows_sw, W_sw)
ser_sw = {}
for d, (ag, A) in MA_sw.items():
    X = L.ewma(A.astype(float))
    for r, a in enumerate(ag):
        ser_sw.setdefault(int(a), []).append(X[r])
fp = [bool(L.rc_cell(s_).get("landscape", {}).get("double_well", False)) for s_ in ser_sw.values()]
R["S1c_single_well_false_double_well"] = {"n": len(fp), "frac": float(np.mean(fp)) if fp else np.nan, "flags": fp,
                                         "note": "latent potentials without a left well (c=1.5) or with barrier << T (b=0.5)"}
log("single-well FP", R["S1c_single_well_false_double_well"])

# ============================================================================ S1d kicks: dose law
log("S1d kicks")
s1d = {}
for name, kp in [("barrier_high_rate", dict(kick_rate=0.25, f=0.25, kick_dur=2.0)),
                 ("trigger_high_rate", dict(kick_rate=0.25, q=0.3, kick_dur=2.0)),
                 ("barrier_village_rate", dict(kick_rate=0.04, f=0.25, kick_dur=2.0)),
                 ("trigger_village_rate", dict(kick_rate=0.04, q=0.3, kick_dur=2.0)),
                 ("no_kick_effect", dict(kick_rate=0.25, f=0.0, kick_dur=2.0)),
                 ("fast_trigger_village_rate", dict(kick_rate=0.08, q=0.5, kick_dur=0.3))]:
    par = [dict(b=3.5, **kp) for _ in range(12)]
    rows, W, K, lat = sim_langevin(par, 10 if QUICK else 20, RNG)
    for bin_s in (30.0, 10.0):
        f, ts1, H = ts1_slope(rows, W, K, "agent", extra="dose", bin_s=bin_s)
        lhr = f["beta"][1:4]; cov = f["cov"][1:, 1:]
        n3 = H["f_A_men"][H["f_A_men"] >= 3]
        dl = L.dose_law(lhr, cov, [1, 2, float(n3.mean()) if len(n3) else 3.0])
        key = f"{name}|bin{int(bin_s)}"
        s1d[key] = {"lhr": [float(v) for v in lhr], "se": [float(v) for v in f["se"][1:4]],
                    "n_dose": [int((np.minimum(H["f_A_men"], 3) == k).sum()) for k in range(4)],
                    "events_dose": [int(H["y"][np.minimum(H["f_A_men"], 3) == k].sum()) for k in range(4)],
                    "best": dl.get("best_aic"), "aic": dl.get("aic"), "kappa": dl.get("kappa"),
                    "kramers_b": dl.get("kramers", {}).get("b"),
                    "expected_ln_hr_per_kick": (kp.get("f", 0) * 3.5) if "barrier" in name or "no_kick" in name else None}
        log(key, np.round(s1d[key]["lhr"], 3), s1d[key]["best"], s1d[key]["n_dose"], s1d[key]["events_dose"])
    # A2 exact-time estimator (counting process), same data
    ts1k = L.build_ts1(rows, W, K).filter(pl.col("first_act_s") >= 0)
    Kd = {a: {"A_men": v["A_men"]} for a, v in K.items()}
    I = L.ts1_interval_rows(ts1k, Kd)
    el = np.log(np.maximum(I["elapsed"], 1.0) / 60.0)
    Xd = np.stack([el] + list(L.dose_dummies(I["directed"]).T), 1)
    fd = L.glm_fe(I["y"], Xd, I["agent"], "cloglog", offset=np.log(I["dt"] / 60.0))
    lhr = fd["beta"][1:4].copy()
    for k_ in range(3):
        if I["y"][np.minimum(I["directed"], 3) == k_ + 1].sum() < 5:
            lhr[k_] = np.nan
    n3 = I["directed"][I["directed"] >= 3]
    dl = L.dose_law(lhr, fd["cov"][1:, 1:], [1, 2, float(n3.mean()) if len(n3) else 3.0])
    s1d[f"{name}|exact_time"] = {"lhr": [float(v) for v in lhr], "se": [float(v) for v in fd["se"][1:4]],
                                 "events_dose": [int(I["y"][np.minimum(I["directed"], 3) == k].sum()) for k in range(4)],
                                 "best": dl.get("best_aic"), "kappa": dl.get("kappa"),
                                 "expected_ln_hr_per_kick": (kp.get("f", 0) * 3.5) if "barrier" in name or "no_kick" in name else None}
    log(f"{name}|exact_time", np.round(lhr, 3), dl.get("best_aic"), s1d[f"{name}|exact_time"]["events_dose"])
R["S1d_kicks"] = s1d

# ============================================================================ S2 gate model
log("S2 gates")


def sim_gates(nA, n_days, th_age, th_m, r_m, rng, frail_sd=1.0, chains_per_day=12):
    recs = []
    th_a = rng.normal(-0.3, frail_sd, nA)
    for a in range(nA):
        for d in range(n_days):
            starts = np.sort(rng.uniform(0, DAY_MIN, chains_per_day))
            for c, s in enumerate(starts):
                t, k = s, 1
                while True:
                    dur = rng.choice([1, 2, 3, 5, 10], p=[0.15, 0.2, 0.2, 0.35, 0.1])
                    if t + dur > DAY_MIN:
                        recs.append((a, d, c, k, 0, -1, 0)); break
                    n = rng.poisson(r_m * dur)
                    p = special.expit(th_a[a] + th_age * np.log(k) + th_m * n)
                    y = rng.random() < p
                    recs.append((a, d, c, k, n, int(y), dur))
                    t += dur
                    if y:
                        break
                    k += 1
    g = np.array(recs)
    g = g[g[:, 5] >= 0]
    return g


s2 = {}
for th_age in (0.0, -0.5):
    g = sim_gates(15, 10 if QUICK else 20, th_age, 0.5, 0.08, RNG)
    X = np.stack([np.log(g[:, 3]), np.minimum(g[:, 4], 3)], 1).astype(float)
    pooled = L.glm_fe(g[:, 5], X, None, "logit")
    fe = L.glm_fe(g[:, 5], X, g[:, 0], "logit")
    s2[f"theta_age={th_age}"] = {"pooled": {"age": float(pooled["beta"][0]), "se": float(pooled["se"][0]), "m": float(pooled["beta"][1])},
                                 "agent_fe": {"age": float(fe["beta"][0]), "se": float(fe["se"][0]), "m": float(fe["beta"][1]),
                                              "m_se": float(fe["se"][1])},
                                 "true": {"age": th_age, "m": 0.5}, "n_gates": int(len(g))}
    log(th_age, s2[f"theta_age={th_age}"])
R["S2_gates"] = s2

# ============================================================================ S3 swarm
log("S3 swarm")


def sim_glauber(N, n_days, n_min, bj, rng, rho=0.4, stall_frac=0.0):
    MA = {}
    h0 = rng.normal(-0.15, 0.35, N)
    for d in range(n_days):
        t = np.arange(n_min)
        sched = 0.35 * np.sin(np.pi * t / n_min) - 0.1
        s = np.where(rng.random(N) < 0.5, 1, -1)
        A = np.zeros((N, n_min), np.int8)
        stall = np.zeros(n_min, bool)
        if stall_frac > 0:
            nblk = rng.poisson(stall_frac * n_min / 8)
            for st in rng.integers(0, n_min, nblk):
                stall[st:st + 8] = True
        for m in range(n_min):
            M = (s.sum() - s) / (N - 1)
            p = special.expit(2 * (bj * M + h0 + sched[m]))
            up = rng.random(N) < rho
            s = np.where(up, np.where(rng.random(N) < p, 1, -1), s)
            A[:, m] = (s > 0) & ~stall[m]
        MA[f"d{d:03d}"] = (np.arange(N, dtype=np.int16), A)
    return MA


s3 = {}
for N, nd_, nm, tag in [(15, 5, 240, "village_4h_N15_5d"), (25, 20, 480, "village_8h_N25_20d")]:
    if QUICK and tag.startswith("village_8h"):
        continue
    for bj in (0.0, 0.3, 0.6, 1.3, 1.8):
        MA = sim_glauber(N, nd_, nm, bj, RNG)
        sa = L.swarm_analysis(MA, RNG, n_sur=60 if QUICK else 150)
        s3[f"{tag}|bj={bj}"] = {k: sa[k] for k in ("VR_cond", "VR_null_p95", "VR_null_median", "phi", "betaJ0_raw", "betaJ0", "p_bc", "p_valley", "p_n_modes", "acf_obs",
                                                   "acf_null_mean", "acf_null_p95", "stall_frac")} | {"obs": sa["obs"]}
        log(tag, bj, {k: round(v, 3) for k, v in s3[f"{tag}|bj={bj}"].items() if isinstance(v, float)})
    MA = sim_glauber(N, nd_, nm, 0.0, RNG, stall_frac=0.04)
    for ex in (False, True):
        sa = L.swarm_analysis(MA, RNG, n_sur=60 if QUICK else 150, exclude_stalls=ex)
        s3[f"{tag}|stalls|exclude={ex}"] = {k: sa[k] for k in ("VR_cond", "VR_null_p95", "betaJ0", "p_bc", "p_valley", "p_n_modes",
                                                               "acf_obs", "acf_null_mean", "stall_frac")} | {"obs": sa["obs"]}
        log(tag, "stalls", ex, {k: round(v, 3) for k, v in s3[f"{tag}|stalls|exclude={ex}"].items() if isinstance(v, float)})
R["S3_swarm"] = s3

L.jdump(R, OUTD / "synthetic_results.json")
L.write_provenance(OUTD, "hypotheses/H16-metastable-traps-kramers/analysis/synthetic.py", [], {"quick": QUICK, "seed": L.SEED})

# ============================================================================ figure
plt.rcParams.update({"font.family": "serif", "font.size": 7, "axes.linewidth": 0.5, "pdf.fonttype": 42})
fig, ax = plt.subplots(2, 3, figsize=(7.2, 4.6))
# S1a
names = list(s1a)
for j, fe in enumerate(("None", "agent", "agentday")):
    ax[0, 0].errorbar(np.arange(len(names)) + (j - 1) * 0.2, [s1a[n][fe]["beta"] for n in names],
                      yerr=[1.96 * s1a[n][fe]["se"] for n in names], fmt="o", ms=3, label=f"FE={fe}")
ax[0, 0].scatter(np.arange(len(names)), [s1a[n]["latent_truth_agentFE"]["beta"] for n in names], marker="_", s=200, c="k", label="latent truth (agent FE)")
ax[0, 0].set_xticks(range(len(names))); ax[0, 0].set_xticklabels([n.replace("_", "\n") for n in names], fontsize=5)
ax[0, 0].axhline(0, lw=0.4, c="grey"); ax[0, 0].set_ylabel("hazard slope on ln elapsed"); ax[0, 0].legend(fontsize=5)
ax[0, 0].set_title("S1a dwell law (TS1)")
# S1b
b = pl.DataFrame(s1b)
x = b["true_mean_min"].to_numpy()
for col, lab in [("naive_completed_mean", "TS1r naive (completed only)"), ("exp_mle", "TS1r exp. MLE (censoring-aware)"),
                 ("latent_naive_completed", "latent naive (completed)"), ("latent_exp_mle", "latent exp. MLE")]:
    ax[0, 1].plot(x, b[col].to_numpy() / x, "o-", ms=3, label=lab)
ax[0, 1].set_xscale("log"); ax[0, 1].axhline(1, lw=0.4, c="grey"); ax[0, 1].set_xlabel("true mean dwell (min); day = 240 min")
ax[0, 1].set_ylabel("estimate / truth"); ax[0, 1].legend(fontsize=5); ax[0, 1].set_title("S1b day-boundary censoring")
# S1c
if ok.height:
    kk = ok["k_obs"].to_numpy()
    ax[0, 2].loglog(1 / ok["mfpt_1d"].to_numpy(), kk, "o", ms=3, label="1D MFPT (occupancy + D)")
    ax[0, 2].loglog(1 / ok["mfpt_msm"].to_numpy(), kk, "s", ms=3, mfc="none", label="MSM on x")
    ax[0, 2].loglog(1 / ok["mfpt_msm2"].to_numpy(), kk, "^", ms=3, label="MSM on (x, a)")
    lim = [kk.min() / 3, kk.max() * 3]
    ax[0, 2].plot(lim, lim, "k-", lw=0.4)
    ax[0, 2].set_xlabel("predicted escape rate (/min)"); ax[0, 2].set_ylabel("observed (/min)"); ax[0, 2].legend(fontsize=5)
ax[0, 2].set_title("S1c Kramers from the landscape")
if ok.height:
    ax[1, 0].plot(ok["bar_true_over_T"].to_numpy(), ok["dG"].to_numpy(), "o", ms=3)
    ax[1, 0].set_xlabel("true barrier dU/T (latent)"); ax[1, 0].set_ylabel("Boltzmann dG on EWMA coordinate")
ax[1, 0].set_title("S1c barrier recovery")
# S1d
for j, n in enumerate([k for k in s1d if k.endswith("bin10")]):
    ax[1, 1].errorbar(np.array([1, 2, 3]) + 0.06 * j, s1d[n]["lhr"], yerr=1.96 * np.array(s1d[n]["se"]), fmt="o-", ms=3,
                      label=f"{n} -> {s1d[n]['best']}")
ax[1, 1].set_xlabel("kick dose (in 2 min)"); ax[1, 1].set_ylabel("ln HR vs dose 0"); ax[1, 1].legend(fontsize=4.5)
ax[1, 1].set_title("S1d kick dose law")
# S3
for tag in ("village_4h_N15_5d", "village_8h_N25_20d"):
    ks = [k for k in s3 if k.startswith(tag + "|bj=")]
    if not ks:
        continue
    bjs = [float(k.split("=")[1]) for k in ks]
    ax[1, 2].plot(bjs, [s3[k]["betaJ0"] for k in ks], "o-", ms=3, label=f"{tag}: est. betaJ0")
    ax[1, 2].plot(bjs, [-np.log10(s3[k]["p_valley"]) for k in ks], "s--", ms=3, label=f"{tag}: -log10 p(valley)")
ax[1, 2].plot([0, 1.8], [0, 1.8], "k-", lw=0.3); ax[1, 2].axvline(1, lw=0.4, c="grey")
ax[1, 2].set_xlabel("true betaJ0"); ax[1, 2].legend(fontsize=4.5); ax[1, 2].set_title("S3 swarm bistability")
fig.tight_layout()
fig.savefig(FIG / "synthetic_validation.pdf")
log("done")
