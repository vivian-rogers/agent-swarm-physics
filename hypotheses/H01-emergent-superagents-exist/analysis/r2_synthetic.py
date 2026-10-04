"""H01 round 2, axis F: a toy 'superagent on a substrate' world and two rivals, at village sampling.

Worlds (card F8), simulated at 5-min ticks and aggregated to 30-min bins exactly like the real scheme:
  W_super  members have no usable memory; every ~14 min (forced consolidation) and every night their context is
           erased and they re-acquire a project from the shared store: artifact momentum z_k (open work visible in the
           repo), the channel (crew-mates currently on k) and the repo's log of their own past commits. Crews sense a
           hidden environment state e(t) through their channel and write more when it is favourable; writes made when
           e = 1 land (confirmed) and raise z_k, writes when e = 0 fail (unconfirmed) and break the artifact, which
           crew-mates on k then repair (write rate x3 until a landing write). Group-level semantic information.
  W_ind    each agent returns to its own personal project from memory (p = 0.9 after an erasure); nothing is shared;
           memory losses redraw the personal project. No artifact state, no repair, no sensing beyond chance.
  W_env    agents carry no state; each tick they pick a project by fixed goal popularity and write with a probability
           set by the exogenous drive. No memory, no artifact state.
Common to all: human-message indicator y^h is a noisy readout of e(t) plus an exogenous presence process; agents are
absent on some days; departures (2-day absences) and memory-loss events are planted with known times; room and lab
labels are random decoys (no effect), so rooms/labs are rival coarse-grainings with no true individuality.

Estimators run (r2lib): R4 composition excess per coarse-graining + crews' shift excess; R5 KW stored/observed
semantic information (kernel model) for crews and singletons; R6 night continuity, memory-loss continuity, and the
spillover of a member's forced consolidation onto the others; R7 departure effect vs the member's share; R8 others'
write response after an unconfirmed vs a confirmed push. Size = rival worlds, power = W_super.

Run: uv run python hypotheses/H01-emergent-superagents-exist/analysis/r2_synthetic.py [--reps 40]
Output: data/processed/H01-emergent-superagents-exist/round2/synthetic.json, figures/r2_synthetic.pdf
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r2lib as L  # noqa: E402  (sets thread caps)

import numpy as np  # noqa: E402

OUT = L.ROOT / "data/processed/H01-emergent-superagents-exist/round2"
TICK = 5.0  # minutes


def simulate(world: str, N=13, K=10, D=5, ticks_per_day=48, seed=0, p_depart=0.15, p_ml=0.06, sense=0.6,
             lam=0.5, mu=30.0, repair=4.0, feedback=1.0, sync=0.0):
    """Calibrated to generic ledger statistics of regime III (median 15 writes per agent-day, bursty; median 2 of 8
    occupied bins per project-day; 4-16 crews of 2-4 writers per period)."""
    rng = np.random.default_rng(seed)
    T = D * ticks_per_day
    q_erase = TICK / 14.0
    active = rng.random((N, D)) < 0.9
    depart = []
    for a in range(N):
        if rng.random() < p_depart and D >= 4:
            d = int(rng.integers(1, D - 2))
            if active[a, d - 1]:
                active[a, d:d + 2] = False
                depart.append((a, d))
    ml = [(a, d) for a in range(N) for d in range(1, D) if rng.random() < p_ml]
    ml_set = set(ml)
    pop = rng.dirichlet(np.ones(K) * 0.7)
    personal = rng.integers(0, K, N)
    e = np.zeros(T, int)
    hpres = np.zeros(T, int)
    e[0] = 1
    for t in range(1, T):
        e[t] = 1 - e[t - 1] if rng.random() < 0.04 else e[t - 1]
        hpres[t] = (rng.random() < 0.08) if hpres[t - 1] == 0 else (rng.random() < 0.8)
    msg = (rng.random(T) < np.where(e == 1, 0.35, 0.05)) | (hpres.astype(bool) & (rng.random(T) < 0.3))
    drive = 1.0 + 0.6 * hpres
    z = np.zeros(K)
    logt = np.zeros((N, K))
    broken = np.zeros(K, bool)
    ctx = -np.ones(N, int)
    work = rng.random(N) < 0.25
    home = rng.integers(0, K, N)          # the repo each agent touched at kickoff (in the repo log, i.e. shared)
    logt[np.arange(N), home] = 3.0
    writes, cons = [], []
    for t in range(T):
        d, tt = divmod(t, ticks_per_day)
        tmin = d * 1440.0 + tt * TICK
        if tt == 0:  # night: every context erased; artifact momentum and log persist (with decay)
            ctx[:] = -1
            z *= 0.7
            logt *= 0.5
            if world == "ind":
                for a in range(N):
                    if (a, d) in ml_set:
                        personal[a] = rng.integers(0, K)
        on_k = np.bincount(ctx[ctx >= 0], minlength=K)
        for a in rng.permutation(N):
            if not active[a, d]:
                continue
            # work phase: own persistence (super, ind) or exogenous (env)
            if world == "env":
                work[a] = rng.random() < 0.12 + 0.35 * hpres[t]
            else:
                # sync > 0: channel activation in timing (start working when crew-mates on the same project work)
                n_mates = int(((ctx == ctx[a]) & work & (np.arange(N) != a)).sum()) if (sync > 0 and ctx[a] >= 0) else 0
                work[a] = (rng.random() > 0.18 / (1 + sync * n_mates)) if work[a] else (rng.random() < 0.06 * (1 + sync * n_mates))
            restart = False
            if ctx[a] >= 0 and rng.random() < q_erase:
                cons.append((tmin + rng.uniform(0, TICK), a))
                ctx[a] = -1
                restart = True            # restart overhead: no write in this tick (the ~10-turn dip)
            if ctx[a] < 0 and not restart:
                if world == "super":
                    w = (0.01 + 0.2 * z / (z + 5.0)) * (1 + lam * np.minimum(on_k, 3)) * (1 + mu * logt[a])
                    ctx[a] = rng.choice(K, p=w / w.sum())
                elif world == "ind":
                    ctx[a] = personal[a] if rng.random() < 0.9 else rng.integers(0, K)
                else:
                    ctx[a] = rng.choice(K, p=pop)
                on_k = np.bincount(ctx[ctx >= 0], minlength=K)
            if restart or ctx[a] < 0:
                continue
            k = ctx[a]
            p = (0.35 if work[a] else 0.01) * drive[t]
            if world == "super":
                if on_k[k] >= 2:                     # channel-informed crews sense e(t)
                    p *= (1 + sense * (2 * e[t] - 1))
                if broken[k] and on_k[k] >= 2:
                    p *= repair
            if rng.random() < min(p, 0.95):
                conf = bool(e[t] == 1)
                for _ in range(1 + rng.poisson(1.5)):   # pushes come in bursts
                    writes.append((tmin + rng.uniform(0, TICK), a, k, conf))
                if world == "super":
                    if conf:
                        z[k] += 1.0 + feedback * msg[t]
                        broken[k] = False
                    else:
                        broken[k] = True
                    logt[a, k] += 1.0
        z *= 0.985
    writes = np.array(writes, dtype=float).reshape(-1, 4)
    cons = np.array(cons, dtype=float).reshape(-1, 2)
    return {"writes": writes, "cons": cons, "active": active, "msg": msg, "D": D, "tpd": ticks_per_day, "N": N,
            "K": K, "depart": depart, "ml": ml, "e": e}


def to_period(sim, name="syn", bin_min=30.0):
    D, tpd = sim["D"], sim["tpd"]
    day_len = tpd * TICK
    bpd = int(day_len // bin_min)
    nB = D * bpd
    day_of_bin = np.repeat(np.arange(D), bpd)
    pos_of_bin = np.tile(np.arange(bpd), D)
    W = sim["writes"]
    agents = list(range(sim["N"]))
    projects = list(range(sim["K"]))
    b = (W[:, 0] // 1440).astype(int) * bpd + ((W[:, 0] % 1440) // bin_min).astype(int)
    vec, Wn = {}, np.zeros((sim["N"], sim["K"]))
    any_w = np.zeros((sim["N"], nB), bool)
    for (bb, a, k) in zip(b, W[:, 1].astype(int), W[:, 2].astype(int)):
        vec.setdefault((a, k), np.zeros(nB, bool))[bb] = True
        Wn[a, k] += 1
        any_w[a, bb] = True
    tick_bin = (np.arange(D * tpd) // tpd) * bpd + ((np.arange(D * tpd) % tpd) * TICK // bin_min).astype(int)
    yh = np.zeros(nB, bool)
    np.logical_or.at(yh, tick_bin, sim["msg"].astype(bool))
    return L.Period(name, "III", day_of_bin, pos_of_bin, agents, projects, vec, Wn, any_w, yh, sim["active"],
                    days=list(range(D)))


def wrote_day(sim):
    W = sim["writes"]
    out = np.zeros((sim["N"], sim["K"], sim["D"]), bool)
    out[W[:, 1].astype(int), W[:, 2].astype(int), (W[:, 0] // 1440).astype(int)] = True
    return out


def r4(P, rng_seed, decoy_rooms, decoy_labs, nc=None):
    nc = nc or L.NullCache(P, n_draw=600, seed=rng_seed)
    res = {}
    cr = L.crews(P, min_writes=max(10, int(P.Wn.sum() / 60)))
    groups = {"crew": [c["members"] for c in cr],
              "room": [list(np.flatnonzero(decoy_rooms == r)) for r in np.unique(decoy_rooms)],
              "lab": [list(np.flatnonzero(decoy_labs == r)) for r in np.unique(decoy_labs)]}
    for kname, gl in groups.items():
        zs, isl = [], []
        for g in gl:
            g = [a for a in g if P.act_a[a] > 0]
            if len(g) < 2:
                continue
            r = L.composition_excess(P, g, nc)
            zs.append(r["z"])
        res[kname] = {"z": [float(v) for v in zs if np.isfinite(v)]}
    shifts, az, ash = [], [], []
    nca = L.NullCacheAlloc(P, n_draw=300, seed=rng_seed)
    for g in groups["crew"][:6]:
        if len(g) >= P.nA - 1:
            continue
        s = L.shift_excess(P, g, n_draw=60, seed=rng_seed)
        shifts.append(s["z"])
        r = L.alloc_individuality(P, g)
        az.append(nca.z(len(g), P.act_a[np.asarray(g)].sum(), r["iota_alloc"])[0])
        ash.append(L.alloc_shift(P, g, n_draw=40, seed=rng_seed)["z"])
    res["crew_shift_z"] = [float(v) for v in shifts if np.isfinite(v)]
    res["crew_alloc_z"] = [float(v) for v in az if np.isfinite(v)]
    res["crew_alloc_shift_z"] = [float(v) for v in ash if np.isfinite(v)]
    return res, cr


def member_xy(P, members):
    """A1.2: each crew member as the system: x = s_i (its writes on the crew's R_G), y = (anyone else wrote, message)."""
    S, R = P.member_series(members)
    out = []
    for j, a in enumerate(members):
        others = np.ones(P.nA, bool)
        others[a] = False
        yw = P.any_w[others].any(0)
        out.append((S[j], (yw.astype(np.int8) * 2 + P.yh.astype(np.int8)).astype(np.int8), P.day_of_bin))
    return out


def r5(P, cr, tau=4, n_boot=60):
    out = {}
    units = {"crew": [c["members"] for c in cr], "singleton": [c["members"] for c in cr]}
    for kname, gl in units.items():
        xy = []
        for g in gl:
            if kname == "crew":
                x, y, _, _ = P.unit_xy(g)
                xy.append((x, y, P.day_of_bin))
            else:
                xy += member_xy(P, g)
        r = L.kw_semantic(xy, P.trans, tau=tau, n_boot=n_boot)
        out[kname] = {k: (float(v) if isinstance(v, (int, float, np.floating)) else None)
                      for k, v in r.items() if k not in ("curve", "pairs")}
    return out


def r6_r7_r8(sim, P, cr):
    res = {}
    wd = wrote_day(sim)
    clist = []
    for c in cr:
        clist.append({"members": c["members"], "R": P.shared_artifacts(c["members"])})
    nc_ = L.night_continuity(P, clist, wd, n_perm=200)
    res["night"] = {k: nc_[k] for k in ("C", "C_null", "dC", "n") if k in nc_} if nc_.get("ok") else None
    # memory-loss continuity: agents with ML on day d who wrote crew R on d-1: do they write it on d?
    W = sim["writes"]
    ev, base = [], []
    for c in clist:
        R = c["R"]
        for a in c["members"]:
            for d in range(1, sim["D"]):
                if not (sim["active"][a, d] and sim["active"][a, d - 1] and wd[a, R, d - 1].any()):
                    continue
                hit = wd[a, R, d].any()
                (ev if (a, d) in set(sim["ml"]) else base).append(hit)
    res["ml_cont"] = {"event": float(np.mean(ev)) if ev else None, "base": float(np.mean(base)) if base else None,
                      "n_ev": len(ev)}
    # spillover of forced consolidations
    events = []
    bounds = [(d * 1440.0, d * 1440.0 + sim["tpd"] * TICK) for d in range(sim["D"])]
    for c in clist:
        R = set(int(k) for k in c["R"])
        mR = np.isin(W[:, 2].astype(int), list(R))
        for a in c["members"]:
            tc = sim["cons"][sim["cons"][:, 1] == a, 0]
            ws = W[mR & (W[:, 1] == a), 0]
            wo = W[mR & (W[:, 1] != a) & np.isin(W[:, 1].astype(int), c["members"]), 0]
            events.append({"t_cons": tc, "w_self": ws, "w_other": wo, "day_bounds": bounds})
    sp = L.spillover(events, n_rot=60)
    res["spill"] = {k: sp[k] for k in ("self", "other", "n_events")} if sp.get("ok") else None
    # departures: crew V_adv on the 2 absent days relative to the 2 days before, vs the member's prior share
    dep = []
    for (a, d0) in sim["depart"]:
        for c in clist:
            if a not in c["members"] or d0 < 2 or d0 + 2 > sim["D"]:
                continue
            R = c["R"]
            x, _, S, _ = P.unit_xy(c["members"])
            Vd = np.array([x[P.day_of_bin == d].mean() for d in range(sim["D"])])
            ia = c["members"].index(a)
            share = S[ia][(P.day_of_bin >= d0 - 2) & (P.day_of_bin < d0)].sum() / max(
                S[:, (P.day_of_bin >= d0 - 2) & (P.day_of_bin < d0)].sum(), 1)
            pre = Vd[d0 - 2:d0].mean()
            post = Vd[d0:d0 + 2].mean()
            dep.append({"dV": float(post - pre), "pre": float(pre), "share": float(share)})
    res["depart"] = dep
    # R8: others' writes on R within 30 min after a member's unconfirmed vs confirmed push
    ratios = {"attempt": [0, 0, 0, 0], "confirmed": [0, 0, 0, 0]}
    for c in clist:
        R = set(int(k) for k in c["R"])
        mR = np.isin(W[:, 2].astype(int), list(R)) & np.isin(W[:, 1].astype(int), c["members"])
        Wc = W[mR]
        for i in range(len(Wc)):
            t, a, conf = Wc[i, 0], Wc[i, 1], Wc[i, 3]
            oth = Wc[(Wc[:, 1] != a) & (Wc[:, 0] > t) & (Wc[:, 0] <= t + 30)]
            for key, sel in (("attempt", oth), ("confirmed", oth[oth[:, 3] == 1])):
                j = 0 if conf == 0 else 2
                ratios[key][j] += float(len(sel) > 0)
                ratios[key][j + 1] += 1
    res["r8"] = {k: ((v[0] / v[1]) / (v[2] / v[3]) if v[1] and v[3] and v[2] else None) for k, v in ratios.items()}
    res["r8_n_unconf"] = ratios["attempt"][1]
    return res


def run_world(world, setting, seed):
    w, kw = (("super", {"sync": 5.0}) if world == "supersync" else (world, {}))
    if setting == "village":
        sim = simulate(w, N=13, K=10, D=5, ticks_per_day=48, seed=seed, **kw)
    else:
        sim = simulate(w, N=20, K=16, D=20, ticks_per_day=96, seed=seed, **kw)
    P = to_period(sim)
    rng = np.random.default_rng(seed + 7)
    rooms = rng.integers(0, 2, P.nA)
    labs = rng.integers(0, 4, P.nA)
    out = {"world": world, "setting": setting, "seed": seed, "n_writes": int(len(sim["writes"]))}
    out["r4"], cr = r4(P, seed, rooms, labs)
    out["n_crews"] = len(cr)
    out["r5"] = r5(P, cr) if cr else None
    out.update(r6_r7_r8(sim, P, cr) if cr else {})
    return out


def truth_r5(world, seed=999):
    """Large-sample reference for the coarse-grained KW quantities (long run, same parameters)."""
    sim = simulate(world, N=13, K=10, D=80, ticks_per_day=48, seed=seed)
    P = to_period(sim)
    cr = L.crews(P, min_writes=max(10, int(P.Wn.sum() / 60)))
    return r5(P, cr, n_boot=0) if cr else None


def kernel_recovery(n_rep=100, seed=7):
    """KW estimator recovery on a known factorized kernel with a planted x * y interaction (human messages sustain only
    active units) and a correlated start distribution; plus an additive (no-interaction) kernel for size."""
    rng = np.random.default_rng(seed)
    res = {}
    for name, inter in (("interaction", True), ("additive", False)):
        Kx = np.zeros((2, 4, 2))
        for x in range(2):
            for y in range(4):
                yh = y % 2
                p1 = (0.85 if yh else 0.45) if (x == 1 and inter) else (0.65 if x == 1 else 0.2)
                if not inter:
                    p1 = 0.2 + 0.45 * x + 0.1 * yh
                Kx[x, y] = (1 - p1, p1)
        Ky = np.zeros((4, 2, 4))
        for y in range(4):
            for x in range(2):
                yw, yh = divmod(y, 2)
                pw = 0.7 if yw else 0.3
                ph = 0.75 if yh else 0.15
                for y2 in range(4):
                    w2, h2 = divmod(y2, 2)
                    Ky[y, x, y2] = (pw if w2 else 1 - pw) * (ph if h2 else 1 - ph)
        K = L.Kernel(Kx, Ky, np.full((2, 4), 99.0))
        p0 = np.array([[0.20, 0.06, 0.20, 0.06], [0.08, 0.16, 0.08, 0.16]])
        p0 /= p0.sum()
        tau = 4
        for setting, (nu, nd, nb) in {"village": (6, 5, 8), "long": (6, 20, 16)}.items():
            # estimand: the start-of-horizon mixture p_bar = mean over start bins b of p0 K^b (what kw_from estimates)
            ps, p = [], p0.copy()
            for b in range(nb - tau):
                ps.append(p.copy())
                p = np.einsum("xy,xyu,yxv->uv", p, K.Kx, K.Ky)
            pbar = np.mean(ps, 0)
            V = L.propagate(pbar, K, tau)
            Vf = L.propagate(np.outer(pbar.sum(1), pbar.sum(0)), K, tau)
            Vo = L.propagate(pbar, K, tau, observed_scramble=True)
            truth = {"dV_st": V - Vf, "dV_obs": V - Vo, "I": L._mi_joint(pbar)}
            est = []
            for _ in range(n_rep):
                units = L.simulate_kernel_chain(K, p0, nu, nd, nb, rng)
                trans_list = [(u[0], u[1], u[2]) for u in units]
                # each unit has its own day array; pass per-unit transition masks
                Tl, Sl = [], []
                for (x, y, day) in trans_list:
                    tr = np.r_[day[1:] == day[:-1], False]
                    T1, S1 = L.transitions_from_units([(x, y, day)], tr, tau)
                    Tl.append(T1)
                    Sl.append(S1)
                r = L.kw_from(np.concatenate(Tl), np.concatenate(Sl), tau)
                if r.get("ok"):
                    est.append((r["dV_st"], r["dV_obs"], r["I"]))
            e = np.array(est)
            res[f"{name}/{setting}"] = {"truth": truth, "dV_st_mean": float(e[:, 0].mean()), "dV_st_sd": float(e[:, 0].std()),
                                        "dV_obs_mean": float(e[:, 1].mean()), "dV_obs_sd": float(e[:, 1].std()),
                                        "I_mean": float(e[:, 2].mean()),
                                        "frac_dV_st_ge_0.01": float((e[:, 0] >= 0.01).mean()),
                                        "frac_dV_st_gt_2sd": float((e[:, 0] > 2 * e[:, 0].std()).mean())}
    return res


def summarize(rows):
    S = {}
    for setting in ("village", "long"):
        for world in ("super", "supersync", "ind", "env"):
            rs = [r for r in rows if r["world"] == world and r["setting"] == setting]
            if not rs:
                continue
            s = {"n_reps": len(rs)}
            for k in ("crew", "room", "lab"):
                meds = [np.median(r["r4"][k]["z"]) for r in rs if r["r4"][k]["z"]]
                s[f"r4_{k}_median_z"] = float(np.median(meds)) if meds else None
                s[f"r4_{k}_frac_rep_median_z_gt_1.64"] = float(np.mean([m > 1.64 for m in meds])) if meds else None
            wins = [np.median(r["r4"]["crew"]["z"]) > max(np.median(r["r4"]["room"]["z"] or [-9]),
                                                         np.median(r["r4"]["lab"]["z"] or [-9]))
                    for r in rs if r["r4"]["crew"]["z"]]
            s["r4a_crew_ranks_first"] = float(np.mean(wins)) if wins else None
            s["r4a_note"] = "rooms and labs are random decoys; ranking first by chance is ~1/3"
            stz = [L.stouffer(r["r4"]["crew"]["z"])[1] for r in rs if r["r4"]["crew"]["z"]]
            s["r4c_power_p<0.01"] = float(np.mean([p < 0.01 for p in stz])) if stz else None
            for key in ("crew_alloc_z", "crew_alloc_shift_z", "crew_shift_z"):
                allz = [z for r in rs for z in r["r4"].get(key, [])]
                s[f"r4_{key}_median"] = float(np.median(allz)) if allz else None
                s[f"r4_{key}_frac_gt_1.64"] = float(np.mean([z > 1.64 for z in allz])) if allz else None
                stz = [L.stouffer(r["r4"].get(key, []))[1] for r in rs if r["r4"].get(key)]
                s[f"r4_{key}_rep_stouffer_p<0.01"] = float(np.mean([p < 0.01 for p in stz])) if stz else None
            allc = [z for r in rs for z in r["r4"]["crew"]["z"]]
            s["r4_crew_z_frac_gt_1.64"] = float(np.mean([z > 1.64 for z in allc])) if allc else None
            sh = [np.median(r["r4"]["crew_shift_z"]) for r in rs if r["r4"]["crew_shift_z"]]
            s["r6d_shift_median_z"] = float(np.median(sh)) if sh else None
            s["r6d_frac_shift_z_gt_0"] = float(np.mean([v > 0 for v in sh])) if sh else None
            for unit in ("crew", "singleton"):
                dv = [r["r5"][unit] for r in rs if r.get("r5") and r["r5"][unit].get("ok")]
                if dv:
                    s[f"r5_{unit}_dV_st_median"] = float(np.median([v["dV_st"] for v in dv]))
                    s[f"r5_{unit}_dV_st_CI>0"] = float(np.mean([(v.get("dV_st_lo") or -1) > 0 for v in dv]))
                    s[f"r5_{unit}_dV_obs_median"] = float(np.median([v["dV_obs"] for v in dv]))
                    s[f"r5_{unit}_dV_obs_CI>0"] = float(np.mean([(v.get("dV_obs_lo") or -1) > 0 for v in dv]))
                    s[f"r5_{unit}_I_median"] = float(np.median([v["I"] for v in dv]))
                    s[f"r5_{unit}_ck_err"] = float(np.nanmedian([v["ck_err"] or np.nan for v in dv]))
                    s[f"r5_{unit}_Vmodel_minus_emp"] = float(np.nanmedian([(v["V"] - v["V_emp"]) for v in dv]))
            gt = [r["r5"]["crew"]["dV_st"] > r["r5"]["singleton"]["dV_st"] for r in rs
                  if r.get("r5") and r["r5"]["crew"].get("ok") and r["r5"]["singleton"].get("ok")]
            s["r5a_crew_gt_singleton"] = float(np.mean(gt)) if gt else None
            ni = [r["night"] for r in rs if r.get("night")]
            if ni:
                s["r6b_dC_median"] = float(np.median([v["dC"] for v in ni]))
                s["r6b_frac_dC>=0.2"] = float(np.mean([v["dC"] >= 0.2 for v in ni]))
            ml = [r["ml_cont"] for r in rs if r.get("ml_cont") and r["ml_cont"]["event"] is not None]
            if ml:
                s["r6c_ml_minus_base"] = float(np.mean([v["event"] - v["base"] for v in ml]))
                s["r6c_n_ev"] = int(sum(v["n_ev"] for v in ml))
            sp = [r["spill"] for r in rs if r.get("spill")]
            if sp:
                s["r6a_self_rel"] = float(np.median([v["self"]["rel"] for v in sp]))
                s["r6a_other_rel"] = float(np.median([v["other"]["rel"] for v in sp]))
                s["r6a_other_p<0.05"] = float(np.mean([v["other"]["p_two"] < 0.05 for v in sp]))
                s["r6a_self_p<0.05"] = float(np.mean([v["self"]["p_two"] < 0.05 for v in sp]))
            dp = [d for r in rs for d in r.get("depart", [])]
            if dp:
                s["r7a_dV_plus_share_x_pre_mean"] = float(np.mean([d["dV"] + d["share"] * d["pre"] for d in dp]))
                s["r7a_n"] = len(dp)
            for key in ("attempt", "confirmed"):
                v = [r["r8"][key] for r in rs if r.get("r8") and r["r8"][key] is not None]
                s[f"r8a_ratio_{key}_median"] = float(np.median(v)) if v else None
                s[f"r8a_frac_ratio_{key}>=1.2"] = float(np.mean([x >= 1.2 for x in v])) if v else None
            S[f"{world}/{setting}"] = s
    return S


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=30)
    ap.add_argument("--long-reps", type=int, default=10)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    rows = []
    for world in ("super", "supersync", "ind", "env"):
        for i in range(a.reps):
            rows.append(run_world(world, "village", 1000 + i))
        for i in range(a.long_reps):
            rows.append(run_world(world, "long", 5000 + i))
        print(world, f"{time.time() - t0:.0f}s", flush=True)
    truth = {w: truth_r5(w) for w in ("super", "ind", "env")}
    S = summarize(rows)
    S["truth_r5_long_run"] = truth
    S["kernel_recovery"] = kernel_recovery()
    S["runtime_s"] = time.time() - t0

    def clean(o):
        if isinstance(o, dict):
            return {k: clean(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [clean(v) for v in o]
        if isinstance(o, (np.floating, float)):
            return None if not np.isfinite(o) else float(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        return o
    (OUT / "synthetic.json").write_text(json.dumps(clean({"summary": S, "rows": rows}), indent=1))
    print(json.dumps(clean(S), indent=1))


if __name__ == "__main__":
    main()
