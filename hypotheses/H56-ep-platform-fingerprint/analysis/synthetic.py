"""H56 synthetic validation (axis F, P0): Markov chains at village sampling with planted changes.

Village: 12 agents, 20 days, change at day 10; event statistic on pre = days 7-9, post = days 10-12 (the real O2).
Per-agent-day transitions ~ lognormal (median 600, q10 ~160, as regime III), clipped [100, 2500].
Each agent has its own chain (common template + heterogeneity) with true EP Sigma_i.

Scenarios (all agents unless stated):
  null            no change
  aff_up50 / aff_dn50 / aff_up25   drive strength re-solved so Sigma_i -> 1.5x / 0.5x / 1.25x (scaffold-like)
  occ             shared field on states (goal-like): U += delta, drive re-solved so Sigma_i is EXACTLY unchanged
  occ_mix         field plus shared conductance change (task mix), Sigma_i exactly unchanged
  count2 / count05  transitions per day x2 / x0.5 (hours, activity)
  roster          3 newcomers with 2x mean Sigma join at day 10 (absent before)
  single          one agent's Sigma x3
  scaffold        agent chain unchanged; a scaffold state is entered every 40 (pre) vs 20 (post) agent transitions
                  and forces a fixed next state; tested on the chain with the scaffold state and on the cut agent chain
Statistics: within-agent count-matched |t| (Newton, cfx, plug-in matched), plug-in unmatched (foil), and the
day-pooled swarm statistic (composition-sensitive). Threshold tau = 95th percentile of the null runs.
Run: OMP_NUM_THREADS=1 uv run python hypotheses/H56-ep-platform-fingerprint/analysis/synthetic.py [--fast]
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h56lib as L  # noqa: E402

OUT = L.DATA / "synthetic"
N_AG, N_DAY, D0, K = 12, 20, 10, 3
TEMPL = {"fine": dict(q=11, sigma=0.08), "coarse": dict(q=6, sigma=0.008)}


def agent_lengths(rng, n_days):
    mu = np.log(600) + rng.normal(0, 0.6)
    return np.clip(np.exp(mu + rng.normal(0, 0.6, n_days)), 100, 2500).astype(int)


def make_agents(templ, rng, n=N_AG, sigma_scale=1.0):
    q, sig = TEMPL[templ]["q"], TEMPL[templ]["sigma"]
    B0, F0, U0, st0 = L.random_template(q, rng)
    agents = []
    for _ in range(n):
        B = B0 * np.exp(rng.normal(0, 0.3, (q, q)))
        B = (B + B.T) / 2
        F = F0 + rng.normal(0, 0.2, (q, q))
        F = (F - F.T) / 2
        U = U0 + rng.normal(0, 0.3, q)
        st = np.clip(st0 + rng.normal(0, 0.05, q), 0.05, 0.9)
        target = sig * sigma_scale * np.exp(rng.normal(0, 0.3))
        s = L.solve_s(B, F, U, st, target)
        agents.append(dict(B=B, F=F, U=U, st=st, s=s, target=target))
    return agents, (B0, F0, U0, st0)


def changed(ag, scen, rng_shared):
    """Post-change parameters of one agent (shared draws in rng_shared state)."""
    B, F, U, st, s, tg = ag["B"], ag["F"], ag["U"], ag["st"], ag["s"], ag["target"]
    if scen in ("aff_up50", "aff_dn50", "aff_up25"):
        f = {"aff_up50": 1.5, "aff_dn50": 0.5, "aff_up25": 1.25}[scen]
        return B, F, U, st, L.solve_s(B, F, U, st, tg * f)
    if scen == "occ":
        U2 = U + rng_shared["dU"]
        return B, F, U2, st, L.solve_s(B, F, U2, st, L.true_ep(L.chain_from_params(B, F, U, s, st)))
    if scen == "occ_mix":
        U2 = U + rng_shared["dU"]
        B2 = B * rng_shared["dB"]
        return B2, F, U2, st, L.solve_s(B2, F, U2, st, L.true_ep(L.chain_from_params(B, F, U, s, st)))
    return B, F, U, st, s


def window_stat(Cpre_list, Cpost_list, rng, R=4):
    """Per-agent matched EP (pre, post) for newton/cfx/plugin plus unmatched plug-in. C*_list: per agent (days, q, q)."""
    res = {e: [] for e in ("newton", "cfx", "plugin", "plugin_raw")}
    lev = {e: [] for e in res}
    for Cpre, Cpost in zip(Cpre_list, Cpost_list):
        if Cpre.sum() < 100 or Cpost.sum() < 100:
            continue
        mp = L.matched_pair(Cpre, Cpost, rng, R=R, est=("newton", "cfx", "plugin"))
        for e in ("newton", "cfx", "plugin"):
            res[e].append(mp[e][1] - mp[e][0])
            lev[e].append(0.5 * (mp[e][0] + mp[e][1]))
        a, b = L.plugin_counts(Cpre.sum(0)), L.plugin_counts(Cpost.sum(0))
        res["plugin_raw"].append(b - a)
        lev["plugin_raw"].append(0.5 * (a + b))
    return {e: L.event_stats(res[e], np.mean(lev[e]) if lev[e] else None) for e in res}


def pooled_stat(Cpre_list, Cpost_list):
    """Day-pooled swarm EP (all present agents' counts summed per day; Newton, day folds), post - pre."""
    pre = np.sum([c for c in Cpre_list if c is not None], 0)
    post = np.sum([c for c in Cpost_list if c is not None], 0)
    return L.newton_counts(post) - L.newton_counts(pre)


def one_run(args):
    templ, scen, seed, detect = args
    rng = np.random.default_rng(seed)
    agents, (B0, F0, U0, st0) = make_agents(templ, rng)
    q = TEMPL[templ]["q"]
    shared = {"dU": rng.normal(0, 1.2, q), "dB": np.exp(rng.normal(0, 0.5, (q, q)))}
    shared["dB"] = (shared["dB"] + shared["dB"].T) / 2
    pre_days, post_days = list(range(D0 - K, D0)), list(range(D0, D0 + K))
    C_all, C_sc_all, C_sc_ag = [], [], []
    tv = []
    for i, ag in enumerate(agents):
        lens = agent_lengths(rng, N_DAY)
        P0 = L.chain_from_params(ag["B"], ag["F"], ag["U"], ag["s"], ag["st"])
        if scen == "scaffold":
            Cw0, Ca0 = L.insert_scaffold(P0, 40, 3 % q, rng, lens[:D0], blocks=1)
            Cw1, Ca1 = L.insert_scaffold(P0, 20, 3 % q, rng, lens[D0:], blocks=1)
            C_sc_all.append(np.concatenate([Cw0, Cw1])[:, 0])
            C_sc_ag.append(np.concatenate([Ca0, Ca1])[:, 0])
            continue
        if scen == "single" and i > 0:
            P1 = P0
        elif scen == "single":
            P1 = L.chain_from_params(ag["B"], ag["F"], ag["U"], L.solve_s(ag["B"], ag["F"], ag["U"], ag["st"], ag["target"] * 3), ag["st"])
        else:
            B, F, U, st, s = changed(ag, scen, shared)
            P1 = L.chain_from_params(B, F, U, s, st)
        if scen.startswith("occ"):
            tv.append(0.5 * np.abs(L.stationary(P0) - L.stationary(P1)).sum())
        l0, l1 = lens[:D0].copy(), lens[D0:].copy()
        if scen == "count2":
            l1 = np.minimum(l1 * 2, 5000)
        if scen == "count05":
            l1 = np.maximum(l1 // 2, 40)
        C0 = L.simulate_counts(P0, l0, rng, blocks=1)[:, 0]
        C1 = L.simulate_counts(P1, l1, rng, blocks=1)[:, 0]
        C_all.append(np.concatenate([C0, C1]))
    out = {"templ": templ, "scen": scen, "seed": seed}
    if scen == "scaffold":
        for nm, CC in (("with_scaffold", C_sc_all), ("agent_cut", C_sc_ag)):
            st_ = window_stat([c[pre_days] for c in CC], [c[post_days] for c in CC], rng)
            out[nm] = {e: st_[e]["t"] for e in st_}
            out[nm + "_dbar"] = st_["newton"]["dbar"]
        return out
    pre = [c[pre_days] for c in C_all]
    post = [c[post_days] for c in C_all]
    pooled_pre, pooled_post = list(pre), list(post)
    if scen == "roster":
        newcomers, _ = make_agents(templ, rng, n=3, sigma_scale=2.0)
        for ag in newcomers:
            P = L.chain_from_params(ag["B"], ag["F"], ag["U"], ag["s"], ag["st"])
            pooled_post.append(L.simulate_counts(P, agent_lengths(rng, K), rng, blocks=1)[:, 0])
    st_ = window_stat(pre, post, rng)
    out.update({e: st_[e]["t"] for e in st_})
    out["dbar_newton"] = st_["newton"]["dbar"]
    out["rel_newton"] = st_["newton"]["rel"]
    out["fpos_newton"] = st_["newton"]["fpos"]
    out["pooled"] = pooled_stat(pooled_pre, pooled_post)
    out["tv"] = float(np.mean(tv)) if tv else None
    if detect:
        ts = {}
        for d in range(K, N_DAY - K + 1):
            s2 = window_stat([c[d - K:d] for c in C_all], [c[d:d + K] for c in C_all], rng, R=2)
            ts[d] = s2["newton"]["t"]
        out["t_by_day"] = ts
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fast", action="store_true")
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    n_null, n_s = (60, 30) if a.fast else (300, 120)
    jobs = []
    seed = 1000
    for templ in ("fine", "coarse"):
        for _ in range(n_null):
            jobs.append((templ, "null", seed, templ == "fine" and _ < (30 if a.fast else 80)))
            seed += 1
        scens = ["aff_up50", "aff_dn50", "aff_up25", "occ", "occ_mix", "count2", "count05", "roster", "single", "scaffold"]
        if templ == "coarse":
            scens = ["aff_up50", "aff_dn50", "occ", "occ_mix", "count2", "roster"]
        for sc in scens:
            for _ in range(n_s):
                jobs.append((templ, sc, seed, templ == "fine" and sc == "aff_up50" and _ < (30 if a.fast else 80)))
                seed += 1
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        res = list(ex.map(one_run, jobs, chunksize=4))
    print(f"{len(res)} runs in {time.time() - t0:.0f} s")
    (OUT / "runs.json").write_text(json.dumps(res))
    summarize(res)


def summarize(res):
    ests = ["newton", "cfx", "plugin", "plugin_raw"]
    summ = {}
    for templ in ("fine", "coarse"):
        null = [r for r in res if r["templ"] == templ and r["scen"] == "null"]
        tau = {e: float(np.nanpercentile(np.abs([r[e] for r in null]), 95)) for e in ests}
        tau["pooled"] = float(np.nanpercentile(np.abs([r["pooled"] for r in null]), 95))
        summ[templ] = {"tau95": tau, "n_null": len(null),
                       "null_t_sd": {e: float(np.nanstd([r[e] for r in null])) for e in ests}, "scen": {}}
        for sc in sorted({r["scen"] for r in res if r["templ"] == templ}):
            rr = [r for r in res if r["templ"] == templ and r["scen"] == sc]
            if sc == "scaffold":
                tau_sc = tau
                summ[templ]["scen"][sc] = {
                    nm: {e: float(np.mean(np.abs([r[nm][e] for r in rr]) > tau_sc[e])) for e in ests}
                    for nm in ("with_scaffold", "agent_cut")}
                summ[templ]["scen"][sc]["dbar_with"] = float(np.mean([r["with_scaffold_dbar"] for r in rr]))
                summ[templ]["scen"][sc]["dbar_agent"] = float(np.mean([r["agent_cut_dbar"] for r in rr]))
                continue
            d = {e: float(np.mean(np.abs([r[e] for r in rr]) > tau[e])) for e in ests}
            d["pooled"] = float(np.mean(np.abs([r["pooled"] for r in rr]) > tau["pooled"]))
            d["mean_rel_newton"] = float(np.nanmean([r["rel_newton"] for r in rr]))
            d["mean_fpos"] = float(np.nanmean([r["fpos_newton"] for r in rr]))
            if rr[0].get("tv") is not None:
                d["mean_tv_occupancy"] = float(np.mean([r["tv"] for r in rr]))
            d["n"] = len(rr)
            summ[templ]["scen"][sc] = d
    # blind detector at tau95 (fine): hit = local max >= tau within +-1 day of day 10; false alarms per other day
    det = {}
    tau = summ["fine"]["tau95"]["newton"]
    for sc in ("null", "aff_up50"):
        rr = [r for r in res if r["templ"] == "fine" and r["scen"] == sc and "t_by_day" in r]
        hits, fa, nd = 0, 0, 0
        for r in rr:
            ts = {int(k): abs(v) if v == v else 0.0 for k, v in r["t_by_day"].items()}
            days = sorted(ts)
            cps = [d for d in days if ts[d] >= tau and all(ts[d] >= ts.get(e, -1) for e in range(d - 2, d + 3))]
            hits += any(abs(d - D0) <= 1 for d in cps)
            fa += sum(abs(d - D0) > 1 for d in cps)
            nd += sum(abs(d - D0) > 1 for d in days)
        det[sc] = {"runs": len(rr), "hit_rate": hits / max(len(rr), 1), "false_alarms_per_day": fa / max(nd, 1)}
    summ["detector_fine"] = det
    (OUT / "summary.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
