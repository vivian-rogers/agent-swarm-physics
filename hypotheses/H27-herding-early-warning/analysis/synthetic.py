"""H27 synthetic validation (axis F): kinetic mean-field Potts swarms at village sampling.

Model (card, "Model"): N agents, states 0 (neutral, uncoupled) and 1..q (projects). Each agent reconsiders at rate
gamma and picks a with prob ∝ exp(h_a(t) + K k_a^(-i)/(N-1)) (a >= 1), ∝ 1 for a = 0. K = βJ.

Sampling (village-like): W = 15-min windows, 16 per day, 5 days; each agent observed per window with prob p_obs at its
state at a uniform random time in the window; a fraction eps of observed labels replaced by a uniform random label.

Scenarios (Amendment 1, 2026-10-04, after a 10-rep pilot and before any real data: the pilot's fold used
K = 4.5 with competitor fields -1, and at N = 12 the four competitor projects ordered spontaneously, swamping the fold;
it is kept as SF_compete. The amended fold uses K = 6 with competitor fields -3.5, where competitors cannot order;
MF fold at h_A = -2.46, pre-fold share 0.19 jumping to 0.96, bistable range -3.28..-2.46):
  S0          stationary null, K = 2, all fields -1                                  (calibrates tau*)
  S0drift     K = 2, each field an OU process (sd 0.5, time scale 1 active day)      (generic false alarms)
  SF_slow     fold: K = 6, others -3.5, h_A ramps -4 -> -2 over 4 days               (saddle-node; CSD expected)
  SF_fast     fold: same ramp compressed into day 3
  SN          noise-induced flips: K = 6, others -3.5, h_A = -2.75 fixed (inside the bistable range)
  SS          field step: K = 2, h_A jumps -1 -> +1.5 at a random time in days 1.5-4
  SF_compete  pilot fold: K = 4.5, others -1, h_A ramps -2.5 -> -0.5 over 4 days (competitors order at N = 12)
  SF_clean12  SF_slow at N = 12 with perfect sampling (p_obs = 1, eps = 0): separates N from sampling
  SF_big      SF_slow at N = 200 with perfect sampling: positive control

The same onset rule, indicators, placebo segments and operator scoring as the real data (ews_core) are applied.
tau* for the operator alarm is calibrated on S0 (5% alarm rate per watchable (project, window)) and frozen.

Usage: uv run python hypotheses/H27-herding-early-warning/analysis/synthetic.py [--reps 200] [--workers 2]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import warnings
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ews_core as E  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data/processed/H27-herding-early-warning/synthetic"
W_MIN, WPD, DAYS, Q = 15, 16, 5, 5
GAMMA = 1 / 30.0  # per minute: an agent reconsiders every 30 min on average
LEADS = (1, 2, 4, 8)

FOLD = dict(ho=-3.5, h_from=-4.0, h_to=-2.0, h_fold=-2.46, h_noise=-2.75)
COMPETE = dict(ho=-1.0, h_from=-2.5, h_to=-0.5, h_fold=-0.92, h_noise=-1.05)
SCEN = {
    "S0": dict(N=12, K=2.0, kind="const", p_obs=0.75, eps=0.1),
    "S0drift": dict(N=12, K=2.0, kind="drift", p_obs=0.75, eps=0.1),
    "SF_slow": dict(N=12, K=6.0, kind="ramp_slow", p_obs=0.75, eps=0.1, **FOLD),
    "SF_fast": dict(N=12, K=6.0, kind="ramp_fast", p_obs=0.75, eps=0.1, **FOLD),
    "SN": dict(N=12, K=6.0, kind="noise", p_obs=0.75, eps=0.1, **FOLD),
    "SS": dict(N=12, K=2.0, kind="step", p_obs=0.75, eps=0.1),
    "SF_compete": dict(N=12, K=4.5, kind="ramp_slow", p_obs=0.75, eps=0.1, **COMPETE),
    "SF_clean12": dict(N=12, K=6.0, kind="ramp_slow", p_obs=1.0, eps=0.0, **FOLD),
    "SF_big": dict(N=200, K=6.0, kind="ramp_slow", p_obs=1.0, eps=0.0, **FOLD),
}
RULES = {"O1": E.P0, "O1slow": E.P_SLOW}


def field_fn(cfg, rng, Tm):
    kind = cfg["kind"]
    base = np.full(Q, cfg.get("ho", -1.0))
    if kind == "const":
        return lambda t: base, None
    if kind == "drift":
        grid = np.arange(-120, Tm + 1)
        tau, sd = 240.0, 0.5
        a = np.exp(-1 / tau)
        z = np.zeros((len(grid), Q))
        z[0] = rng.normal(0, sd, Q)
        for i in range(1, len(grid)):
            z[i] = a * z[i - 1] + np.sqrt(1 - a * a) * sd * rng.normal(size=Q)
        return (lambda t: base + z[int(np.clip(round(t) + 120, 0, len(grid) - 1))]), None
    if kind in ("ramp_slow", "ramp_fast"):
        t0, t1 = (0.0, 4 * 240.0) if kind == "ramp_slow" else (2 * 240.0, 3 * 240.0)

        a0, a1 = cfg["h_from"], cfg["h_to"]

        def f(t):
            h = base.copy()
            u = np.clip((t - t0) / (t1 - t0), 0, 1)
            h[0] = a0 + (a1 - a0) * u
            return h
        tf = t0 + (t1 - t0) * (cfg["h_fold"] - a0) / (a1 - a0)  # MF fold crossing
        return f, tf
    if kind == "noise":
        h = base.copy()
        h[0] = cfg["h_noise"]
        return (lambda t: h), None
    if kind == "step":
        ts = rng.uniform(1.5 * 240, 4 * 240)

        def f(t):
            h = base.copy()
            if t >= ts:
                h[0] = 1.5
            return h
        return f, ts
    raise ValueError(kind)


def simulate(rng, cfg):
    N, K, p_obs, eps = cfg["N"], cfg["K"], cfg["p_obs"], cfg["eps"]
    T = DAYS * WPD
    Tm = T * W_MIN
    hf, t_event = field_fn(cfg, rng, Tm)
    B = 120.0  # burn-in (min) at the initial fields
    n_ev = rng.poisson(N * GAMMA * (Tm + B))
    times = np.sort(rng.uniform(-B, Tm, n_ev))
    who = rng.integers(N, size=n_ev)
    u = rng.random(n_ev)
    state = np.zeros(N, np.int8)
    counts = np.bincount(state, minlength=Q + 1).astype(float)
    states = np.empty((n_ev + 1, N), np.int8)
    states[0] = state
    for e in range(n_ev):
        i = who[e]
        counts[state[i]] -= 1
        h = hf(max(times[e], 0.0))
        lg = np.empty(Q + 1)
        lg[0] = 0.0
        lg[1:] = h + K * counts[1:] / (N - 1)
        pr = np.exp(lg - lg.max())
        c = np.cumsum(pr)
        new = int(np.searchsorted(c, u[e] * c[-1]))
        state[i] = new
        counts[new] += 1
        states[e + 1] = state
    # sampling
    k = np.zeros((T, Q), int)
    n = np.zeros(T, int)
    for w in range(T):
        obs = rng.random(N) < p_obs
        tt = rng.uniform(w * W_MIN, (w + 1) * W_MIN, N)
        idx = np.searchsorted(times, tt, side="right")
        lab = states[idx, np.arange(N)].astype(int)
        if eps > 0:
            flip = rng.random(N) < eps
            lab = np.where(flip, rng.integers(0, Q + 1, N), lab)
        lab = lab[obs]
        n[w] = len(lab)
        bc = np.bincount(lab, minlength=Q + 1)
        k[w] = bc[1:]
    # hidden true share of project A per window (window-mean of the full state), for reference
    mid = (np.arange(T) + 0.5) * W_MIN
    true_xA = (states[np.searchsorted(times, mid, side="right")] == 1).mean(1)
    return k, n, t_event, true_xA


def run_one(args):
    name, rep, seed = args
    warnings.simplefilter("ignore")
    cfg = SCEN[name]
    rng = np.random.default_rng(seed)
    k, n, t_event, true_xA = simulate(rng, cfg)
    win = np.tile(np.arange(WPD), DAYS)
    day = np.repeat(np.arange(DAYS), WPD)
    ind = E.all_window_indicators(k, n, E.P0)  # indicators do not depend on the onset rule
    keep = {kk: ind[kk] for kk in ("tau_ar1", "tau_sd", "valid", "matched", "x")}
    var = {}
    for rname, p in RULES.items():
        on = E.find_onsets(k, n, win, day, p)
        seg, drops = {}, {}
        for lead in (LEADS if rname == "O1" else (4,)):
            rows, dr = E.onset_and_placebo_segments(k, n, on, lead, p)
            seg[lead] = rows
            drops[lead] = dr
        conc = E.concentration_segments(k, n, on, 4, p)
        var[rname] = dict(onsets=on, seg=seg, drops=drops, conc=conc)
    return dict(name=name, rep=rep, var=var, ind=keep, k=k, n=n, t_event=t_event, true_xA=true_xA)


KEYS = ("composite", "tau_ar1", "tau_sd", "tau_skew", "tau_flick", "flick_level", "tau_sd_binom", "mean_last4")


def summarize_rule(R, rname, tau_star, rng, name, n_boot=400):
    n_on = [len(r["var"][rname]["onsets"]) for r in R]
    S = dict(reps=len(R), onsets_total=int(sum(n_on)), onsets_per_run=float(np.mean(n_on)),
             frac_runs_with_onset=float(np.mean([x > 0 for x in n_on])))
    if name not in ("S0", "S0drift"):
        dA, nA = [], 0
        for r in R:
            oa = [o["w0"] for o in r["var"][rname]["onsets"] if o["project"] == 0]
            nA += bool(oa)
            if oa and r["t_event"] is not None:
                dA.append(oa[0] - r["t_event"] / W_MIN)
        S["frac_runs_with_A_onset"] = nA / max(len(R), 1)
        S["first_A_onset_minus_event_windows_median"] = float(np.median(dA)) if dA else None
    S["auc"] = {}
    for lead in R[0]["var"][rname]["seg"]:
        groups = {}
        for r in R:
            rows = r["var"][rname]["seg"][lead]
            pos = {kk: np.array([x[kk] for x in rows if x["kind"] == "onset"]) for kk in KEYS}
            neg = {kk: np.array([x[kk] for x in rows if x["kind"] == "placebo"]) for kk in KEYS}
            groups[r["rep"]] = (pos, neg)
        A = {}
        for kk in KEYS:
            est, ci = E.cluster_bootstrap_auc({g: (v[0][kk], v[1][kk]) for g, v in groups.items()}, kk, rng, n_boot=n_boot)
            A[kk] = dict(auc=est, ci=ci)
        A["n_onset_segments"] = int(sum(len(g[0]["composite"]) for g in groups.values()))
        A["n_placebo_segments"] = int(sum(len(g[1]["composite"]) for g in groups.values()))
        S["auc"][lead] = A
    S["onsets_dropped_lead4"] = {kk: int(sum(r["var"][rname]["drops"][4][kk] for r in R)) for kk in R[0]["var"][rname]["drops"][4]}
    cg = {r["rep"]: (np.array([x["composite"] for x in r["var"][rname]["conc"] if x["kind"] == "onset"]),
                     np.array([x["composite"] for x in r["var"][rname]["conc"] if x["kind"] == "placebo"])) for r in R}
    est, ci = E.cluster_bootstrap_auc(cg, "composite", rng, n_boot=n_boot)
    S["auc_concentration_lead4"] = dict(auc=est, ci=ci)
    ops = {}
    for rule in ("ews", "level", "momentum"):
        tot = dict(n_onsets=0, warnable=0, hits=0, leads=[], false_alarms=0, negatives=0, n_alarms=0, true_alarms=0)
        for r in R:
            al, watch = E.alarms(r["ind"], r["k"], rule, tau_star)
            sc = E.score_alarms(al, watch, r["var"][rname]["onsets"])
            for kk in tot:
                tot[kk] = tot[kk] + ([int(x) for x in sc[kk]] if kk == "leads" else sc[kk])
        ops[rule] = dict(hit_rate=tot["hits"] / max(tot["n_onsets"], 1),
                         hit_rate_warnable=tot["hits"] / max(tot["warnable"], 1),
                         far=tot["false_alarms"] / max(tot["negatives"], 1),
                         ppv=tot["true_alarms"] / max(tot["n_alarms"], 1),
                         false_alarms_per_day=tot["false_alarms"] / max(len(R) * DAYS, 1),
                         median_lead_h=float(np.median(tot["leads"]) * W_MIN / 60) if tot["leads"] else None,
                         n_onsets=tot["n_onsets"], warnable=tot["warnable"], hits=tot["hits"])
    S["operator"] = ops
    return S


def summarize(results, tau_star, rng):
    out = {}
    for name in SCEN:
        R = [r for r in results if r["name"] == name]
        out[name] = {rname: summarize_rule(R, rname, tau_star, rng, name) for rname in RULES}
    return out


def calibrate_tau(results):
    vals = []
    for r in results:
        if r["name"] != "S0":
            continue
        ind = r["ind"]
        w = ind["valid"] & ind["matched"]
        vals.append(np.minimum(ind["tau_ar1"], ind["tau_sd"])[w])
    v = np.concatenate(vals)
    return float(np.quantile(v, 0.95)), int(len(v))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=200)
    ap.add_argument("--reps-big", type=int, default=100)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--cache", default=None, help="optional pickle path for raw runs (use a scratch path)")
    ap.add_argument("--from-cache", action="store_true")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = []
    for si, name in enumerate(SCEN):
        nr = a.reps_big if name == "SF_big" else a.reps
        for rep in range(nr):
            jobs.append((name, rep, 20261004 + 1000 * si + rep))
    if a.from_cache:
        import pickle
        with open(a.cache, "rb") as fh:
            results = pickle.load(fh)
    elif a.workers > 1:
        from multiprocessing import get_context
        with get_context("spawn").Pool(min(a.workers, 2)) as pool:
            results = pool.map(run_one, jobs, chunksize=8)
    else:
        results = [run_one(j) for j in jobs]
    if a.cache and not a.from_cache:  # optional raw per-run cache (scratch, not the data folder)
        import pickle
        with open(a.cache, "wb") as fh:
            pickle.dump(results, fh, protocol=pickle.HIGHEST_PROTOCOL)
    tau_star, n_cal = calibrate_tau(results)
    rng = np.random.default_rng(7)
    summ = summarize(results, tau_star, rng)
    meta = dict(built_by="hypotheses/H27-herding-early-warning/analysis/synthetic.py", built_at=dt.datetime.now(dt.timezone.utc).isoformat(),
                tau_star=tau_star, tau_star_n_calibration=n_cal, gamma_per_min=GAMMA, W_min=W_MIN, windows_per_day=WPD, days=DAYS, q=Q,
                params={k: v.__dict__ for k, v in RULES.items()}, scenarios=SCEN, reps=a.reps, reps_big=a.reps_big)
    (OUT / "synthetic_summary.json").write_text(json.dumps(dict(meta=meta, summary=summ), indent=1, default=float))
    # compact traces for the figure: a few example runs per scenario
    ex = {}
    for name in SCEN:
        R = [r for r in results if r["name"] == name][:3]
        ex[name] = [dict(k=r["k"].tolist(), n=r["n"].tolist(), onsets=r["var"]["O1"]["onsets"],
                         onsets_slow=r["var"]["O1slow"]["onsets"], true_xA=r["true_xA"].tolist(), t_event=r["t_event"]) for r in R]
    (OUT / "synthetic_examples.json").write_text(json.dumps(ex, default=float))
    # per-segment rows for lead 4 (for figures)
    import polars as pl
    rows = []
    for r in results:
        for rname in RULES:
            for x in r["var"][rname]["seg"][4]:
                rows.append(dict(scenario=r["name"], rule=rname, rep=r["rep"], **x))
    pl.DataFrame(rows).write_parquet(OUT / "segments_lead4.parquet", compression="zstd")
    print(f"tau* = {tau_star:.3f} (n = {n_cal})")
    for name, SS_ in summ.items():
      for rname, S in SS_.items():
        a4 = S["auc"][4]
        op = S["operator"]["ews"]
        print(f"{name:11s} {rname:6s} A-onset {S.get('frac_runs_with_A_onset', float('nan')):.2f} onsets/run {S['onsets_per_run']:.2f}  AUC4 comp {a4['composite']['auc']:.2f} "
              f"ar1 {a4['tau_ar1']['auc']:.2f} sd {a4['tau_sd']['auc']:.2f} sdb {a4['tau_sd_binom']['auc']:.2f} "
              f"skew {a4['tau_skew']['auc']:.2f} flk {a4['tau_flick']['auc']:.2f} flkL {a4['flick_level']['auc']:.2f} "
              f"last4 {a4['mean_last4']['auc']:.2f} (n+ {a4['n_onset_segments']}, n- {a4['n_placebo_segments']}) | "
              f"EWS hit {op['hit_rate']:.2f} FAR {op['far']:.3f} PPV {op['ppv']:.2f} lead {op['median_lead_h']} | "
              f"level hit {S['operator']['level']['hit_rate']:.2f} FAR {S['operator']['level']['far']:.3f} lead {S['operator']['level']['median_lead_h']}")


if __name__ == "__main__":
    main()
