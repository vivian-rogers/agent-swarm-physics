"""H28 synthetic validation (axis F): village-like swarms with known link contagion, common drive, occupancy coupling,
own-history homophily or complex contagion, sampled like the village; run through the real-data estimator.

  uv run python hypotheses/H28-links-spread-herding/analysis/synthetic.py [--runs 30] [--shifts 29] [--workers 2]

Generator (1-min steps; 5 days x 4 h; N agents; K projects; 1 or 2 rooms):
  * activity: alternating active (Exp mean 45 min) / paused (Exp mean 12 min) spells; one logged turn per active minute;
  * an active agent off project x arrives at x with per-minute rate
      exp(base + a_i + h_x + g_xd + drive_x(t) + J log(1 + occ_-i,x) + kappa 1[visible link to x, last 60 min]
          + kappa2 1[>= 2 distinct senders visible, last 60 min] + rho 1[i visited x before])
  * on arrival: a spell (Exp mean 25 min) with touches every ~6 min; a link to x is posted at the arrival with prob p0 and
    at each later touch with prob p1 (chat touches); recipients = the poster's room; visible at the recipient's next turn;
  * common drive: `pulses` per day, each raising one project's rate by `delta` for 45 min for everyone (both rooms);
    half of the pulses come with a human message (observed kick), the rest are invisible to the analyst.
Ground truth: expected extra arrivals due to link exposure (lambda_true per exposure; R_true = share of arrivals).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h28core as hc  # noqa: E402

MIN = 60_000
DAY = 86_400_000

SCEN = {
    # name: generator kwargs
    "S0_null": dict(),
    "S1_contagion": dict(kappa=np.log(3)),
    "S2_drive": dict(pulses=4, delta=2.0),
    "S3_occupancy": dict(J=0.8),
    "S4_contagion+drive": dict(kappa=np.log(3), pulses=4, delta=2.0),
    "S5_revisits": dict(rho=1.5),
    "S6_complex": dict(kappa2=np.log(5)),
    "S7_drive_2rooms": dict(pulses=4, delta=2.0, rooms=2, N=14),
    "S8_contagion_2rooms": dict(kappa=np.log(3), rooms=2, N=14),
    "S9_drive_long": dict(pulses=2, delta=1.5, pulse_len=120),
    "S10_announce": dict(pulses=4, delta=2.0, announce=True),
    "S11_announce_2rooms": dict(pulses=4, delta=2.0, announce=True, rooms=2, N=14),
}


def generate(seed, N=12, K=15, D=5, M=240, rooms=1, base=-7.0, kappa=0.0, kappa2=0.0, J=0.0, rho=0.0, pulses=0,
             delta=2.0, p0=0.35, p1=0.15, spell_mean=25.0, touch_gap=6.0, links_on=True, field_seed=None,
             pulse_len=45, announce=False):
    rng = np.random.default_rng(seed)
    frng = np.random.default_rng(seed if field_seed is None else field_seed)
    a = frng.normal(0, 0.3, N)
    h = frng.normal(0, 0.8, K)
    g = frng.normal(0, 0.7, (K, D))
    room_of = np.zeros(N, np.int64) if rooms == 1 else np.where(np.arange(N) < N // 2, 2, 3)
    # pulses (common drive): fixed by the field seed so counterfactual replays share them
    pul = []
    for d in range(D):
        for _ in range(pulses):
            st = int(frng.integers(0, M - min(pulse_len, M // 2)))
            x = int(frng.choice(K, p=np.exp(h) / np.exp(h).sum()))
            pul.append((d, st, x, bool(frng.random() < 0.5)))
    # activity and turns (exogenous)
    active = np.zeros((N, D, M), bool)
    turn_t = {i: [] for i in range(N)}
    for i in range(N):
        for d in range(D):
            m, act = 0, frng.random() < 0.8
            while m < M:
                L = max(1, int(frng.exponential(45 if act else 12)))
                if act:
                    active[i, d, m:m + L] = True
                m += L
                act = not act
            for m in np.nonzero(active[i, d])[0]:
                turn_t[i].append(d * DAY + m * MIN + int(frng.integers(0, MIN)))
    turns = {i: np.array(sorted(v), np.int64) for i, v in turn_t.items()}
    # dynamics
    on_until = np.full((N, K), -1, np.int64)
    visited = np.zeros((N, K), bool)
    lastvis = np.full((N, K, N + 1), -10 ** 15, np.int64)   # per sender (index N = human)
    pending = []                                             # (t_vis, ri, x, sender, lid)
    touches, links, expo = [], [], []
    attr_true, nexp_true, n_arr = 0.0, 0, 0
    for d in range(D):
        for m in range(M):
            t = d * DAY + m * MIN
            # visibility events up to t
            if pending:
                pending.sort()
                k = 0
                while k < len(pending) and pending[k][0] < t:
                    tv, ri, x, s, lid = pending[k]
                    lastvis[ri, x, s] = max(lastvis[ri, x, s], tv)
                    if on_until[ri, x] <= tv:
                        nexp_true += 1
                    k += 1
                pending = pending[k:]
            on = on_until > t
            occ = on.sum(0)
            drive = np.zeros(K)
            for (pd, st, x, _) in pul:
                if pd == d and st <= m < st + pulse_len:
                    drive[x] += delta
                if announce and links_on and pd == d and st == m:   # an announcement link marks the drive onset
                    i = int(rng.integers(N))
                    tk = t + int(rng.integers(0, MIN))
                    touches.append((i, x, tk, 1))
                    on_until[i, x] = max(on_until[i, x], tk + 60 * MIN)
                    lid = len(links)
                    links.append((tk, i, int(room_of[i]), x))
                    for j in range(N):
                        if j != i and room_of[j] == room_of[i]:
                            tv_arr = turns[j]
                            q = np.searchsorted(tv_arr, tk, "left")
                            if q < len(tv_arr) and tv_arr[q] // DAY == d:
                                expo.append((lid, j, int(tv_arr[q])))
                                pending.append((int(tv_arr[q]), j, x, i, lid))
            recent = (t - lastvis) < 60 * MIN                 # (N, K, N+1)
            E = recent.any(2)
            S2 = recent.sum(2) >= 2
            lin = (base + a[:, None] + h[None, :] + g[:, d][None, :] + drive[None, :]
                   + J * np.log1p(occ[None, :] - on) + rho * visited)
            r0 = np.exp(lin)
            r = np.exp(lin + kappa * E + kappa2 * S2)
            risk = active[:, d, m][:, None] & ~on
            attr_true += float(((r - r0) * risk).sum())
            hit = risk & (rng.random((N, K)) < 1 - np.exp(-r))
            for i, x in zip(*np.nonzero(hit)):
                n_arr += 1
                visited[i, x] = True
                t0 = t + int(rng.integers(0, MIN))
                dur = rng.exponential(spell_mean) * MIN
                tt = [t0]
                while True:
                    nxt = tt[-1] + rng.exponential(touch_gap) * MIN
                    if nxt > t0 + dur:
                        break
                    tt.append(int(nxt))
                tt = [min(x_, d * DAY + M * MIN - 1) for x_ in tt]
                on_until[i, x] = tt[-1] + 60 * MIN
                for k_, tk in enumerate(tt):
                    is_link = links_on and (rng.random() < (p0 if k_ == 0 else p1))
                    touches.append((i, x, tk, 1 if is_link else 0))
                    if is_link:
                        lid = len(links)
                        links.append((tk, i, int(room_of[i]), x))
                        for j in range(N):
                            if j == i or room_of[j] != room_of[i]:
                                continue
                            tv_arr = turns[j]
                            q = np.searchsorted(tv_arr, tk, "left")
                            if q < len(tv_arr) and tv_arr[q] // DAY == d:
                                expo.append((lid, j, int(tv_arr[q])))
                                pending.append((int(tv_arr[q]), j, x, i, lid))
    # assemble P in the load_period format
    days = [dict(ws_ms=d * DAY, we_ms=d * DAY + M * MIN - 1, nb=int(np.ceil(M * MIN / hc.BIN_MS)), pt_date=f"d{d}") for d in range(D)]
    tch = np.array(touches, np.int64).reshape(-1, 4)
    lk = np.array(links, np.int64).reshape(-1, 4)
    ex = np.array(expo, np.int64).reshape(-1, 3)
    act_ai, act_b, act_room = [], [], []
    for i in range(N):
        tb = np.unique((turns[i] // DAY) * days[0]["nb"] + (turns[i] % DAY) // hc.BIN_MS)
        act_ai += [i] * len(tb)
        act_b += list(tb)
        act_room += [int(room_of[i])] * len(tb)
    hum_t, hum_r = [], []
    for (pd, st, x, vis) in pul:
        if vis:
            for rr in sorted(set(room_of.tolist())):
                hum_t.append(pd * DAY + st * MIN)
                hum_r.append(rr)
    P = dict(goal=-1, days=days, agents=list(range(N)), K=K, projects=[f"p{x}" for x in range(K)],
             touches=dict(ai=tch[:, 0], x=tch[:, 1], t=tch[:, 2], src=tch[:, 3]),
             links=dict(lid=np.arange(len(lk)), msg=np.arange(len(lk)), t=lk[:, 0], sender=lk[:, 1], room=lk[:, 2],
                        x=lk[:, 3], addressed=[set() for _ in range(len(lk))]),
             expo=dict(lid=ex[:, 0], ri=ex[:, 1], t_vis=ex[:, 2]),
             turns=turns, ev_turns=turns, pre_ne09=False,
             active=dict(ai=np.array(act_ai, np.int64), b=np.array(act_b, np.int64), room=np.array(act_room, np.int64)),
             roster={d: set(range(N)) for d in range(D)},
             plans=dict(ai=np.zeros(0, np.int64), t=np.zeros(0, np.int64), pid=np.zeros(0, np.int64), proj=set()),
             kicks=dict(human=(np.array(hum_t, np.int64), np.array(hum_r, np.int64)),
                        auto=(np.zeros(0, np.int64), np.zeros(0, np.int64)),
                        kickoff=np.array([d * DAY for d in range(D)], np.int64)))
    truth = dict(attr=attr_true, nexp=nexp_true, arrivals=n_arr, lam=attr_true / max(nexp_true, 1),
                 R=attr_true / max(n_arr, 1), links=len(lk))
    return P, truth


def analyse(P, shifts=29, seed=0, full=True):
    """The real-data pipeline on one period: primary fit, shift null, rivals, dose-response, lambda, R_link."""
    rng = np.random.default_rng(seed)
    R, B, G = hc.build_rows(P)
    F = hc.link_features(P, R)
    out = {"rows": int(len(R["y"])), "arrivals": int(R["y"].sum()), "links": int((P["links"]["x"] >= 0).sum())}
    res = hc.fit(R, F, "primary")
    k, se = hc.coef(res, "E60")
    out.update(kappa=k, se=se, p=_p(k, se), J=hc.coef(res, "log_occ")[0])
    null = []
    for _ in range(shifts):
        lt, tv = hc.shift_links(P, rng)
        Fs = hc.link_features(P, R, link_t=lt, t_vis=tv)
        null.append(hc.coef(hc.fit(R, Fs, "primary"), "E60")[0])
    null = np.array([v for v in null if np.isfinite(v)])
    out["null_mean"], out["null_sd"] = float(null.mean()), float(null.std(ddof=1))
    out["z_shift"] = (k - out["null_mean"]) / out["null_sd"] if out["null_sd"] > 0 else np.nan
    nexp = hc.count_exposures(P)
    att = hc.attributable(res, R, F, nexp, draws=0)
    out.update(lam=att["lam"], R_link=att["R_link"], nexp=nexp)
    if not full:
        return out
    rl = hc.fit(R, F, "lead")
    out["kappa_lead"], out["se_lead"] = hc.coef(rl, "lead60")
    out["kappa_withlead"], _ = hc.coef(rl, "E60")
    out["diff_lead"], out["p_diff_lead"] = _diff(rl, "E60", "lead60")
    rs = hc.fit(R, F, "momentum")
    out["kappa_strict"], out["se_strict"] = hc.coef(rs, "E60")
    out["b_mom"] = hc.coef(rs, "mom30")[0]
    rpd = hc.fit(R, F, "primary", fe="pd")
    out["kappa_pd"], out["se_pd"] = hc.coef(rpd, "E60")
    out["J_pd"] = hc.coef(rpd, "log_occ")[0]
    naive = R["own_ever"] == 0
    rn = hc.fit(R, F, [n for n in hc.SPECS["primary"] if n not in ("own_ever", "log_own")], rows=naive)
    out["kappa_naive"], out["se_naive"] = hc.coef(rn, "E60")
    if len(set(P["active"]["room"].tolist())) > 1:
        rr = hc.fit(R, F, "room")
        out["kappa_other"], out["se_other"] = hc.coef(rr, "other60")
        out["kappa_same"], _ = hc.coef(rr, "E60")
    rd = hc.fit(R, F, "dose")
    for nme in ("d11", "d12", "d13", "dS2"):
        out[f"b_{nme}"], out[f"se_{nme}"] = hc.coef(rd, nme)
    cv = hc.cv_quarters(R, F, specs=("fields", "occ_only", "primary", "simple", "complex"))
    out["cv"] = cv
    rf = hc.fit(R, F, "fields")
    es = hc.event_study(P, R, F, rf)
    out["es_pre"], out["es_post"] = es["pre"], es["post"]
    return out


def _p(b, se):
    from scipy.stats import norm
    return float(2 * norm.sf(abs(b / se))) if se and np.isfinite(se) and se > 0 else np.nan


def _diff(res, a, b):
    from scipy.stats import norm
    if res is None or a not in res["names"] or b not in res["names"]:
        return np.nan, np.nan
    i, j = res["names"].index(a), res["names"].index(b)
    d = res["beta"][i] - res["beta"][j]
    v = res["V"][i, i] + res["V"][j, j] - 2 * res["V"][i, j]
    return float(d), float(norm.sf(d / np.sqrt(v))) if v > 0 else np.nan


def one(args):
    scen, r, shifts = args
    kw = dict(SCEN[scen])
    P, truth = generate(1000 * (list(SCEN).index(scen) + 1) + r, **kw)
    t = time.time()
    out = analyse(P, shifts=shifts, seed=r)
    out.update(scen=scen, run=r, truth=truth, secs=time.time() - t)
    return out


def counterfactual_check(args):
    """True vs estimated effect of removing links on pile-ons (peak occupancy, 60-min burst)."""
    scen, r, nsim = args
    kw = dict(SCEN[scen])
    seed = 50_000 + 1000 * (list(SCEN).index(scen) + 1) + r
    P, truth = generate(seed, **kw)
    R, B, G = hc.build_rows(P)
    F = hc.link_features(P, R)
    res = hc.fit(R, F, "primary")
    if res is None:
        return None
    sim = hc.Simulator(P, R, B, G, res, F)
    rng = np.random.default_rng(seed)
    est = {f: [sim.run(rng, f=f) for _ in range(nsim)] for f in (1.0, 0.0)}
    # truth: replay the generator with the same fields/pulses/activity, links on vs off
    tru = {}
    for f, on in ((1.0, True), (0.0, False)):
        vals = []
        for rep in range(nsim):
            Pp, _ = generate(seed * 7 + rep + (0 if on else 999), field_seed=seed, links_on=on, **kw)
            Bp = hc.bins(Pp)
            Gp = hc.grids(Pp, Bp)
            vals.append(hc.observed_pileups(Pp, Bp, Gp))
        tru[f] = vals
    obs = hc.observed_pileups(P, B, G)

    def med(lst, k):
        return float(np.mean([v[k] for v in lst]))
    return dict(scen=scen, run=r, obs=obs,
                est={k: med(est[0.0], k) / max(med(est[1.0], k), 1e-9) for k in ("peak_occ", "burst60", "arrivals")},
                true={k: med(tru[0.0], k) / max(med(tru[1.0], k), 1e-9) for k in ("peak_occ", "burst60")},
                est_f1={k: med(est[1.0], k) for k in ("peak_occ", "burst60", "arrivals")},
                true_f1={k: med(tru[1.0], k) for k in ("peak_occ", "burst60")})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=30)
    ap.add_argument("--shifts", type=int, default=29)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--cf-runs", type=int, default=8)
    ap.add_argument("--cf-sims", type=int, default=20)
    ap.add_argument("--only", nargs="*", default=None)
    a = ap.parse_args()
    out_dir = hc.Path(__file__).resolve().parents[3] / "data/processed/H28-links-spread-herding/synthetic"
    out_dir.mkdir(parents=True, exist_ok=True)
    scens = a.only or list(SCEN)
    jobs = [(s, r, a.shifts) for s in scens for r in range(a.runs)]
    t = time.time()
    with Pool(a.workers) as pool:
        res = pool.map(one, jobs, chunksize=1)
        print(f"recovery runs done in {time.time() - t:.0f}s", flush=True)
        cf_jobs = [(s, r, a.cf_sims) for s in ("S1_contagion", "S2_drive", "S4_contagion+drive") if s in scens
                   for r in range(a.cf_runs)]
        cf = [c for c in pool.map(counterfactual_check, cf_jobs, chunksize=1) if c is not None] if a.cf_runs else []
    print(f"all done in {time.time() - t:.0f}s", flush=True)
    (out_dir / "recovery.json").write_text(json.dumps(res, default=float, indent=0))
    (out_dir / "counterfactual.json").write_text(json.dumps(cf, default=float, indent=0))
    summarize(res, cf, out_dir)


def summarize(res, cf, out_dir):
    import collections
    by = collections.defaultdict(list)
    for r in res:
        by[r["scen"]].append(r)
    rows = {}
    for s, L in by.items():
        def arr(k):
            return np.array([x.get(k, np.nan) for x in L], float)
        k, z, p = arr("kappa"), arr("z_shift"), arr("p")
        sup = (k > 0) & (z >= 2) & (p < 0.05)
        lt = np.array([x["truth"]["lam"] for x in L])
        Rt = np.array([x["truth"]["R"] for x in L])
        row = dict(n=len(L), arrivals=float(np.median(arr("arrivals"))), links=float(np.median(arr("links"))),
                   kappa_med=float(np.nanmedian(k)), P1_supported=float(np.mean(sup)),
                   z_med=float(np.nanmedian(z)),
                   lead_med=float(np.nanmedian(arr("kappa_lead"))), diff_lead_sig=float(np.nanmean(arr("p_diff_lead") < 0.05)),
                   strict_ratio_med=float(np.nanmedian(arr("kappa_strict") / k)),
                   strict_sig=float(np.nanmean((arr("kappa_strict") / arr("se_strict")) > 1.96)),
                   p_sig=float(np.nanmean((k / arr("se")) > 1.96)), z2=float(np.nanmean(z >= 2)),
                   J_med=float(np.nanmedian(arr("J"))), J_pd_med=float(np.nanmedian(arr("J_pd"))),
                   naive_med=float(np.nanmedian(arr("kappa_naive"))),
                   lam_hat_med=float(np.nanmedian(arr("lam"))), lam_true_med=float(np.median(lt)),
                   R_hat_med=float(np.nanmedian(arr("R_link"))), R_true_med=float(np.median(Rt)),
                   d11_med=float(np.nanmedian(arr("b_d11"))), dS2_med=float(np.nanmedian(arr("b_dS2"))),
                   complex_wins=float(np.mean([x["cv"]["complex"] > x["cv"]["simple"] for x in L])),
                   primary_beats_fields=float(np.mean([x["cv"]["primary"] > x["cv"]["occ_only"] for x in L])),
                   es_pre=float(np.nansum([x["es_pre"]["O"] for x in L]) / max(np.nansum([x["es_pre"]["E"] for x in L]), 1e-9)),
                   es_post=float(np.nansum([x["es_post"]["O"] for x in L]) / max(np.nansum([x["es_post"]["E"] for x in L]), 1e-9)))
        if "kappa_other" in L[0]:
            row["other_med"] = float(np.nanmedian(arr("kappa_other")))
            row["other_sig"] = float(np.nanmean(np.abs(arr("kappa_other") / arr("se_other")) > 1.96))
            row["same_med"] = float(np.nanmedian(arr("kappa_same")))
        rows[s] = row
    cfs = collections.defaultdict(list)
    for c in cf:
        cfs[c["scen"]].append(c)
    cfsum = {s: dict(est_peak=float(np.median([c["est"]["peak_occ"] for c in L])),
                     true_peak=float(np.median([c["true"]["peak_occ"] for c in L])),
                     est_burst=float(np.median([c["est"]["burst60"] for c in L])),
                     true_burst=float(np.median([c["true"]["burst60"] for c in L])),
                     calib_peak=float(np.median([c["est_f1"]["peak_occ"] / max(c["true_f1"]["peak_occ"], 1e-9) for c in L])))
             for s, L in cfs.items()}
    summ = dict(scenarios=rows, counterfactual=cfsum)
    (out_dir / "summary.json").write_text(json.dumps(summ, indent=1))
    for s, r in rows.items():
        print(s, json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()}))
    for s, r in cfsum.items():
        print("CF", s, json.dumps({k: round(v, 3) for k, v in r.items()}))


if __name__ == "__main__":
    main()
