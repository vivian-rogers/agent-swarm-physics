"""H146 round 1 on exploration data (#51, 07-06 -> 09-04; 51m and #45-#50 never read).

Stage 1 (--stage power): per pattern K, its real skeleton (item coding, exposures, at-risk rows, event counts, wipe and
placebo events, challenge and lapse rows) with planted outcomes -> power and size per test (power146.py). Writes
results/power_<set>.json. No estimate of K is computed in this stage.
Stage 2 (--stage estimate): per pattern K, the pre-registered statistics with CIs (P1 adoption, P1b expression
response, P2 named vs unnamed, P3 newcomers, P4 wipes, P5 repair, P6 specialization and O-information), and the same
statistics (point estimates) on frequency-matched pseudo-patterns drawn from H145's element pool. Writes
results/real_<set>.json.

Sets: `h145` (H145's memeplexes.json; primary) and `candidates` (the qualitative candidates fixed in
scheme/candidates_story.json; POST HOC, labelled). Pseudo-patterns for both come from H145's element table: each
element of K is replaced by a pool element with agent-bin count within +-25% and agent count within +-1 (widened in
steps if none is free; the widening is recorded).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h146lib as L  # noqa: E402
import power146 as PW  # noqa: E402
import tests146 as T  # noqa: E402

OUTR = L.ROOT / "data" / "processed" / "H146-egregore-recruitment-behaviors-51" / "results"
H145 = L.ROOT / "data" / "processed" / "H145-ideology-egregores-51"
FABLE = 31   # Claude Fable 5: relays outside human input (A1.4: its items are exogenous in a robustness fit)


def jsonable(o):
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return None if not np.isfinite(o) else float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.ndarray):
        return jsonable(o.tolist())
    return o


# ------------------------------------------------------------------------------------------------- sets and pool
def load_memeplexes(cod):
    mp = json.loads((H145 / "memeplexes.json").read_text())
    items = mp.get("memeplexes", mp) if isinstance(mp, dict) else mp
    if isinstance(items, dict):
        items = [dict(v, id=k) for k, v in items.items()]
    K, meta = {}, {}
    for i, m in enumerate(items):
        if m.get("qualifies") is False:
            continue
        name = str(m.get("id", m.get("name", f"K{i}")))
        els = np.array(sorted(int(e) for e in m["elements"]), np.int64)
        K[name] = els
        meta[name] = {k: m.get(k) for k in ("label", "n_elements", "n_hosts", "labs", "lifetime_days", "h_K",
                                            "candidate", "candidates", "maps_to", "field_seeded") if k in m}
    return K, meta, {k: v for k, v in mp.items() if k != "memeplexes"} if isinstance(mp, dict) else {}


def profiles(cod):
    B = cod.M_ab.tocoo()
    n_ab = np.bincount(B.col, minlength=len(cod.names)).astype(float)
    k = np.unique(B.col.astype(np.int64) * 1000 + cod.ab_agent[B.row].astype(np.int64))
    n_ag = np.bincount(k // 1000, minlength=len(cod.names)).astype(float)
    return n_ab, n_ag


def pseudo_sets(prof_K, prof_pool, exclude, n, rng):
    """prof_K: (n_ab, n_ag) arrays for K's elements; returns n pseudo element sets (pool indices) and widening log."""
    pab, pag = prof_pool
    ok_pool = pab > 0
    ok_pool[list(exclude)] = False
    steps = [(0.25, 1), (0.5, 2), (1.0, 4), (np.inf, np.inf)]
    cand = []
    widen = [0] * len(steps)
    for x, y in zip(*prof_K):
        for si, (rt, at) in enumerate(steps):
            c = np.flatnonzero(ok_pool & (np.abs(pab - x) <= rt * max(x, 1)) & (np.abs(pag - y) <= at))
            if len(c) >= 3 or si == len(steps) - 1:
                cand.append(c)
                widen[si] += 1
                break
    sets = []
    for _ in range(n):
        used = set()
        S = []
        for c in cand:
            free = [j for j in rng.permutation(c)[:50] if j not in used]
            if not free:
                free = [j for j in rng.permutation(np.flatnonzero(ok_pool)) if j not in used][:1]
            used.add(free[0])
            S.append(free[0])
        sets.append(np.array(sorted(S), np.int64))
    return sets, {"steps": [list(s) for s in steps], "elements_per_step": widen}


def k_profile_in(cod, K):
    n_ab, n_ag = profiles(cod)
    return n_ab[K], n_ag[K]


# --------------------------------------------------------------------------------------------- per-pattern work
def practice_slugs(cod, K):
    return [cod.practice_slugs[j] for j in K if j in cod.practice_slugs]


def designs(ev, cod, pn):
    at, y, info = L.adoption_rows(ev, cod, pn)
    nh = T.nonhost_rows(ev, cod, pn)
    ye = pn.row_own > 0
    return at, y, info, nh, ye


def newcomer_rows(ev, days=2):
    a = ev.a
    act = L.agent_days(ev)
    rows = np.zeros(a["n_rows"], bool)
    for n in ev.newcomers:
        ad = act.get(int(n["agent"]), np.array([], dtype=int))[:days]
        rows |= (a["row_agent"] == n["agent"]) & np.isin(a["row_day"], ad)
    return rows


def stage_power(ev, cod, K, ctrl, seed):
    pn = L.panel(ev, cod, K)
    at, y, info, nh, ye = designs(ev, cod, pn)
    Xd = L.exposures(ev, pn, host_only=True)
    nc = newcomer_rows(ev)
    out = {"n_elements": int(len(K)), "host_agentbins": int(pn.host_ab.sum()),
           "hosts": int(len(np.unique(cod.ab_agent[pn.host_ab]))),
           "items_carrying_share": float((pn.carries > 0).mean()),
           "items_from_hosts_share": float(pn.carries_host.mean()), "adoption_counts": info,
           "n_nonhost_rows": int(nh.sum()), "n_nonhost_events": int((ye & nh).sum()),
           "n_newcomer_rows": int(nc.sum()), "n_newcomer_events": int((ye & nc).sum())}
    out["P1_adopt"] = PW.p1_power(ev, Xd, at, int(y[at].sum()), ctrl, beta=0.3, seed=seed)
    out["P1_adopt_b0.6"] = PW.p1_power(ev, Xd, at, int(y[at].sum()), ctrl, beta=0.6, reps=30, seed=seed + 1)
    out["P1b_expr"] = PW.p1_power(ev, Xd, nh, int((ye & nh).sum()), ctrl, beta=0.3, seed=seed + 2)
    out["P1b_expr_b0.6"] = PW.p1_power(ev, Xd, nh, int((ye & nh).sum()), ctrl, beta=0.6, reps=30, seed=seed + 7)
    out["P3_newcomers"] = PW.p1_power(ev, Xd, nc, int((ye & nc).sum()), ctrl, beta=0.3, seed=seed + 3)
    out["P3_newcomers_b0.6"] = PW.p1_power(ev, Xd, nc, int((ye & nc).sum()), ctrl, beta=0.6, reps=30,
                                           seed=seed + 4)
    E4 = L.p4_events(ev, cod, pn, K, practice_slugs(cod, K))
    out["P4"] = PW.p4_power(E4, seed=seed + 5)
    sk = T.p5_repair(ev, cod, pn, E4, skel_only=True)
    out["P5"] = {lab: PW.p5_power(m, ag, s, cl, c, seed=seed + 10 + i) for i, (lab, (m, ag, s, cl, c))
                 in enumerate(sk.items())}
    return out


def stage_estimate(ev, cod, K, ctrl, rng, full=True):
    pn = L.panel(ev, cod, K)
    at, y, info, nh, ye = designs(ev, cod, pn)
    Xd = L.exposures(ev, pn, host_only=True)
    out = {"adoption_counts": info}
    if y[at].sum() >= 5:
        out["P1_adopt"] = L.p1_fit(ev, Xd, at, y, ctrl=ctrl)
        out["P2_adopt"] = L.p1_fit(ev, Xd, at, y, split_named=True, ctrl=ctrl)
    out["P1b"] = L.p1_fit(ev, Xd, nh, ye, ctrl=ctrl)
    out["P2b"] = L.p1_fit(ev, Xd, nh, ye, split_named=True, ctrl=ctrl)
    if full:
        out["P1b_nohub"] = L.p1_fit(ev, L.exposures(ev, pn, host_only=True, nohub=True), nh, ye, ctrl=ctrl)
        pn_nf = L.Panel(pn.K, pn.nK_ab, pn.host_ab, pn.carries, pn.carries_host & (ev.a["msg_agent"] != FABLE),
                        pn.row_own, pn.m)
        out["P1b_nofable"] = L.p1_fit(ev, L.exposures(ev, pn_nf, host_only=True), nh, ye, ctrl=ctrl)
        out["P1b_anysender"] = L.p1_fit(ev, L.exposures(ev, pn, host_only=False), nh, ye, ctrl=ctrl)
        out["P3"] = T.p3_newcomers(ev, cod, pn, ctrl)
    E4 = L.p4_events(ev, cod, pn, K, practice_slugs(cod, K))
    out["P4"] = L.p4_stats(E4, B=300 if full else 0, seed=int(rng.integers(1e9)))
    out["P5"] = T.p5_repair(ev, cod, pn, E4, B=300 if full else 0, seed=int(rng.integers(1e9)))
    out["P6_spec"] = T.p6_spec(cod, pn, K, rng, n_perm=200 if full else 60)
    out["P6_omega"] = T.p6_omega(ev, cod, pn, rng, n_surr=100 if full else 0)
    return out


def point(o, path):
    cur = o
    for p in path:
        if cur is None:
            return None
        cur = cur.get(p) if isinstance(cur, dict) else None
    if isinstance(cur, (list, tuple)):
        cur = cur[0]
    return None if cur is None or (isinstance(cur, float) and not np.isfinite(cur)) else float(cur)


PSEUDO_KEYS = {"P1_adopt": ("P1_adopt", "delta"), "P1b": ("P1b", "delta"),
               "P2b_named_minus_unnamed": ("P2b", "delta_named_minus_unnamed"),
               "P4_HR": ("P4", "HR_F_vs_P"), "P5_wipe": ("P5", "wipe", "rr"),
               "P5_challenge_val": ("P5", "challenge_val", "rr"), "P5_challenge_dq2": ("P5", "challenge_dq2", "rr"),
               "P5_lapse": ("P5", "lapse", "rr"), "P6_spec_z": ("P6_spec", "z"),
               "P6_omega": ("P6_omega", "omega_per")}


# ---------------------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", choices=["h145", "candidates"], required=True)
    ap.add_argument("--stage", choices=["power", "estimate"], required=True)
    ap.add_argument("--n-pseudo", type=int, default=30)
    ap.add_argument("--only", default=None)
    A = ap.parse_args()
    import coding_h145 as CH
    t0 = time.time()
    ev = L.load()
    ctrl = L.controls(ev)
    pool = CH.build(ev)
    if A.set == "h145":
        cod = pool
        Ks, meta, mp_info = load_memeplexes(cod)
        src = "H145 memeplexes.json"
    else:
        cod, Ks = L.coding_candidates(ev)
        meta = {k: {"label": "post hoc qualitative candidate"} for k in Ks}
        mp_info = {}
        src = "scheme/candidates_story.json (post hoc)"
    if A.only:
        Ks = {k: v for k, v in Ks.items() if k in A.only.split(",")}
    print(f"[{time.time() - t0:.0f}s] {A.set}: {len(Ks)} patterns", flush=True)
    OUTR.mkdir(parents=True, exist_ok=True)
    seed = 20261009
    if A.stage == "power":
        res = {"set": A.set, "source": src, "coding": cod.source, "patterns": {}}
        for i, (k, K) in enumerate(Ks.items()):
            res["patterns"][k] = dict(meta.get(k, {}), **stage_power(ev, cod, K, ctrl, seed + 100 * i))
            print(f"[{time.time() - t0:.0f}s] power {k}: " + json.dumps(jsonable(res["patterns"][k]))[:600],
                  flush=True)
            (OUTR / f"power_{A.set}.json").write_text(json.dumps(jsonable(res), indent=1))
        return
    rng = np.random.default_rng(seed)
    res_path = OUTR / f"real_{A.set}.json"
    res = json.loads(res_path.read_text()) if res_path.exists() and A.only else \
        {"set": A.set, "source": src, "coding": cod.source, "patterns": {}, "memeplex_info": mp_info}
    prof_pool = profiles(pool)
    for k, K in Ks.items():
        tk = time.time()
        r = {"meta": meta.get(k, {}), "elements": K.tolist() if A.set == "h145" else
             [cod.names[j] for j in K]}
        r["stats"] = stage_estimate(ev, cod, K, ctrl, rng, full=True)
        print(f"[{time.time() - t0:.0f}s] {k} real done ({time.time() - tk:.0f}s)", flush=True)
        prof_K = k_profile_in(cod, K)
        excl = set(K.tolist()) if A.set == "h145" else set()
        sets, wl = pseudo_sets(prof_K, prof_pool, excl, A.n_pseudo, rng)
        ps = {key: [] for key in PSEUDO_KEYS}
        for j, S in enumerate(sets):
            o = stage_estimate(ev, pool, S, ctrl, rng, full=False)
            for key, path in PSEUDO_KEYS.items():
                ps[key].append(point(o, path))
        r["pseudo"] = {"n": len(sets), "widening": wl, "values": ps}
        res["patterns"][k] = r
        print(f"[{time.time() - t0:.0f}s] {k} pseudo done ({time.time() - tk:.0f}s)", flush=True)
        res_path.write_text(json.dumps(jsonable(res), indent=1))


if __name__ == "__main__":
    main()
