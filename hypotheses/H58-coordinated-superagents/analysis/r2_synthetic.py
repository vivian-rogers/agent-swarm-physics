"""H58 round-2 synthetic validation (axis F) for R1 (attraction rule, territorial rule, village level) and R2 (file level).

R1: worlds simulated on each unit's REAL activity mask (only *which* artifact is simulated, as round 1):
  own    agent + own artifact persistence (round 1's W_own)
  env    common field over 3 shared artifacts, every active agent follows it with prob 0.5 (round 1's W_env)
  store  planted group P shares a store Z over 3 shared artifacts, followed with prob rho (round 1's W_store)
  terr   planted group P shares a pool of 3 artifacts (works there with prob 0.7, stays with prob 0.6); a choice that
         lands on an artifact another P member holds in that bin is redrawn among free pool artifacts with prob theta
Round 1's g rule is also run on terr (theta 0.9) to measure its avoidance leak (h58lib, with H01's r2lib stubbed out:
the g rule does not use it).
R2: file-level worlds on each eligible shared repo's REAL writer x bin mask (scheme r2/files.parquet):
  fown   each writer persists on its own 1-2 files (stay 0.85), visits a hub file with prob 0.1
  fstore writers follow a store over 3 shared files with prob 0.5 (else as fown)
  fterr  writers work on 3 shared files with prob 0.6 and redraw a file another writer holds in that bin with prob 0.9
Output: data/processed/H58-coordinated-superagents/r2/synthetic_r1.json, synthetic_r2.json
Run: uv run python hypotheses/H58-coordinated-superagents/analysis/r2_synthetic.py [--r1] [--r2] [--reps 20]
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ[_v] = "1"

import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
import types  # noqa: E402
import zlib  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r2lib58 as R  # noqa: E402

SETTINGS = [("own", 0.0), ("env", 0.5), ("store", 0.35), ("store", 0.5), ("store", 0.7), ("terr", 0.5), ("terr", 0.9)]
UNITS = R.REPL + R.NATIVE


def skeleton(name):
    P = R.load_panel(name)
    act = P.S >= 0
    W = np.zeros((P.nA, P.K))
    a_, b_ = np.nonzero(act)
    np.add.at(W, (a_, P.S[a_, b_]), 1)
    tot = W.sum(0)
    own_n = [int(min(max(((W[a] >= 0.5 * tot) & (tot >= 3)).sum(), 1), 2)) for a in range(P.nA)]
    return {"name": name, "act": act, "day": P.day.copy(), "own_n": own_n, "agents": list(P.agents)}


def simulate(sk, world, par, rng, q=0.15, stay=0.85, shared_rate=0.1, stay_shared=0.6):
    act, day = sk["act"], sk["day"]
    nA, nB = act.shape
    pool = [0, 1, 2]
    own, nxt = [], 3
    for a in range(nA):
        own.append(list(range(nxt, nxt + sk["own_n"][a])))
        nxt += sk["own_n"][a]
    S = np.full((nA, nB), -1, np.int64)
    ell = [own[a][0] for a in range(nA)]
    m = 4 if nA >= 15 else 3
    actn = act.sum(1)
    elig = np.flatnonzero(actn >= np.median(actn))
    P = sorted(rng.choice(elig, min(m, len(elig)), replace=False).tolist())
    Pset = set(P)
    Z, F = int(rng.integers(3)), int(rng.integers(3))
    for b in range(nB):
        if b > 0:
            if rng.random() < q:
                Z = int(rng.choice([s for s in pool if s != Z]))
            if rng.random() < q:
                F = int(rng.choice([s for s in pool if s != F]))
        held = set()
        order = rng.permutation(np.flatnonzero(act[:, b]))
        for a in order:
            if world == "store" and a in Pset and rng.random() < par:
                k = Z
            elif world == "env" and rng.random() < par:
                k = F
            elif world == "terr" and a in Pset and rng.random() < 0.7:
                k = ell[a] if (ell[a] in pool and rng.random() < 0.6) else int(rng.choice(pool))
                if k in held and rng.random() < par:
                    free = [s for s in pool if s not in held]
                    if free:
                        k = int(rng.choice(free))
                held.add(k)
            elif rng.random() < (stay_shared if ell[a] in pool else stay):
                k = ell[a]
            elif rng.random() < shared_rate:
                k = int(rng.choice(pool))
            else:
                k = int(rng.choice(own[a]))
            S[a, b] = k
            ell[a] = k
    Pn = R.Panel(sk["name"], sk["agents"], nxt, S, day, (S >= 0).sum(1).astype(float))
    return Pn, P


def test_group(Pn, world, P, m):
    if world in ("store", "terr"):
        return P
    W = np.zeros((Pn.nA, Pn.K))
    a_, b_ = np.nonzero(Pn.S >= 0)
    np.add.at(W, (a_, Pn.S[a_, b_]), 1)
    if world == "env":
        order = np.argsort(-W[:, :3].sum(1))
        return sorted(order[:max(2, min(m + 2, Pn.nA // 2))].tolist())
    k = int(np.argmax(W[:, :3].sum(0)))
    return sorted(np.argsort(-W[:, k])[:m].tolist())


def g_rule(Pn, G, rep):
    """Round 1's decision rule on a simulated panel (h58lib; H01's r2lib is stubbed: not used by the g rule)."""
    sys.modules.setdefault("r2lib", types.ModuleType("r2lib"))
    import h58lib as L
    U = L.Unit(Pn.name, "III", list(Pn.agents), list(range(Pn.K)), Pn.day, Pn.S, (Pn.S >= 0).astype(int),
               np.zeros(Pn.nB, bool))
    cn = L.CompNull(U, n_draw=150, seed=rep)
    ev = L.evaluate(U, G, cn, n_shift=60, seed=rep)
    return {"g": ev["g"], "g_qualifies": ev["qualifies"], "g_z_shift": ev["z_shift"], "g_z_spec": ev["z_comp"]}


def one_rep(args):
    name, world, par, rep, do_g = args
    sk = SK[name]
    rng = np.random.default_rng(zlib.crc32(f"r2|{name}|{world}|{par}|{rep}".encode()))
    Pn, P = simulate(sk, world, par, rng)
    m = len(P)
    G = test_group(Pn, world, P, m)
    Dr = R.make_draws(Pn, R=100, seed=rep)
    a = R.a_rule(Dr, G, seed=rep)
    t = R.t_rule(Dr, G, seed=rep)
    v = R.village(Dr)
    out = {"unit": name, "world": world, "par": par, "rep": rep, "nA": Pn.nA, "nB": Pn.nB, "m": m,
           "a_lam": a["lam"], "a_z_shift": a["z_shift"], "a_z_out": a["z_out"], "a_testable": a["testable"],
           "a_spec": a["specificity"], "a_n_ctx": a["n_ctx"], "a_qual": a["qualifies"],
           "t_T": t["T"], "t_Tref": t["T_part_mu"], "t_z_rot": t["z_rot"], "t_z_part": t["z_part"], "t_n_part": t["n_part"],
           "t_pairbins": t["pairbins"], "t_qual": t["qualifies"],
           "v_lam_ratio": v["lam_V_ratio"], "v_z_lam": v["z_lam"], "v_T": v["T_V"], "v_z_T": v["z_T"]}
    if do_g:
        try:
            out.update(g_rule(Pn, G, rep))
        except Exception as e:  # noqa: BLE001
            out["g_err"] = str(e)[:100]
    return out


SK = {}


def init(names):
    global SK
    for n in names:
        SK[n] = skeleton(n)


def run_r1(reps, g_reps):
    names = UNITS
    jobs = [(n, w, p, r, False) for n in names for (w, p) in SETTINGS for r in range(reps)]
    jobs += [(n, "terr", 0.9, 500 + r, True) for n in names for r in range(g_reps)]
    t0 = time.time()
    res = []
    with ProcessPoolExecutor(2, initializer=init, initargs=(names,)) as ex:
        for i, r in enumerate(ex.map(one_rep, jobs, chunksize=4)):
            res.append(r)
            if i % 200 == 0:
                print(f"r1 {i}/{len(jobs)} {time.time() - t0:.0f}s", flush=True)
    R.R2.mkdir(parents=True, exist_ok=True)
    (R.R2 / "synthetic_r1.json").write_text(json.dumps(R.jsonable(res)))
    print(f"r1 done {len(res)} in {time.time() - t0:.0f}s", flush=True)


# ============================================================================ R2 (file level)
FILE_WORLDS = [("fown", 0.0), ("fstore", 0.5), ("fterr", 0.9)]


def file_skeletons():
    import r2_run as RR
    return {key: {"act": Pn.S >= 0, "day": Pn.day, "agents": Pn.agents, "name": key}
            for key, Pn in RR.file_panels().items()}


def simulate_file(sk, world, par, rng, q=0.15, stay=0.85, hub_rate=0.1):
    act, day = sk["act"], sk["day"]
    nA, nB = act.shape
    shared = [0, 1, 2]
    hub = 3
    own, nxt = [], 4
    for a in range(nA):
        n_own = 1 + int(rng.random() < 0.5)
        own.append(list(range(nxt, nxt + n_own)))
        nxt += n_own
    S = np.full((nA, nB), -1, np.int64)
    ell = [own[a][0] for a in range(nA)]
    Z = int(rng.integers(3))
    for b in range(nB):
        if b > 0 and rng.random() < q:
            Z = int(rng.choice([s for s in shared if s != Z]))
        held = set()
        for a in rng.permutation(np.flatnonzero(act[:, b])):
            if world == "fstore" and rng.random() < par:
                k = Z
            elif world == "fterr" and rng.random() < 0.6:
                k = ell[a] if (ell[a] in shared and rng.random() < 0.6) else int(rng.choice(shared))
                if k in held and rng.random() < par:
                    free = [s for s in shared if s not in held]
                    if free:
                        k = int(rng.choice(free))
                held.add(k)
            elif ell[a] in own[a] and rng.random() < stay:
                k = ell[a]
            elif rng.random() < hub_rate:
                k = hub
            else:
                k = int(rng.choice(own[a]))
            S[a, b] = k
            ell[a] = k
    return R.Panel(sk["name"], sk["agents"], nxt, S, day, (S >= 0).sum(1).astype(float))


def one_file_rep(args):
    key, world, par, rep = args
    sk = FSK[key]
    rng = np.random.default_rng(zlib.crc32(f"r2f|{key}|{world}|{par}|{rep}".encode()))
    Pn = simulate_file(sk, world, par, rng)
    Dr = R.make_draws(Pn, R=100, seed=rep)
    v = R.village(Dr)
    sp = R.static_partition(Pn, n_draw=100, seed=rep, min_act=3)
    return {"repo": key, "world": world, "par": par, "rep": rep, "nA": Pn.nA,
            "lam_ratio": v["lam_V_ratio"], "z_lam": v["z_lam"], "n_ctx": v["n_ctx"], "T": v["T_V"], "z_T": v["z_T"],
            "pairbins": v["pairbins"], "z_excl": sp.get("z_excl"), "excl": sp.get("excl")}


FSK = {}


def init_files():
    global FSK
    FSK = file_skeletons()


def run_r2(reps):
    init_files()
    keys = sorted(FSK)
    jobs = [(k, w, p, r) for k in keys for (w, p) in FILE_WORLDS for r in range(reps)]
    t0 = time.time()
    res = []
    with ProcessPoolExecutor(2, initializer=init_files) as ex:
        for i, r in enumerate(ex.map(one_file_rep, jobs, chunksize=8)):
            res.append(r)
            if i % 500 == 0:
                print(f"r2 {i}/{len(jobs)} {time.time() - t0:.0f}s", flush=True)
    (R.R2 / "synthetic_r2.json").write_text(json.dumps(R.jsonable(res)))
    print(f"r2 done {len(res)} in {time.time() - t0:.0f}s", flush=True)


def main():
    reps = int(sys.argv[sys.argv.index("--reps") + 1]) if "--reps" in sys.argv else 20
    g_reps = int(sys.argv[sys.argv.index("--g-reps") + 1]) if "--g-reps" in sys.argv else 10
    if "--r1" in sys.argv:
        run_r1(reps, g_reps)
    if "--r2" in sys.argv:
        run_r2(reps)


if __name__ == "__main__":
    main()
