"""H58 synthetic validation (axis F): worlds simulated on each unit's REAL schedule (card F10, prediction S0).

Only *which* artifact is simulated; *when* each agent commits is the real agent x bin activity mask, so timing carries
the real common drives and no planted signal. Worlds:
  own    agent + own artifact persistence only (stay 0.85 on own, 0.6 on shared; a switch goes to a shared artifact
         with prob 0.1, else to an own artifact)
  env    a common field F(b) over 3 shared artifacts (switch prob 0.15 / bin, half announced through y^h); every active
         agent follows it with prob 0.5, otherwise own persistence
  store  a planted group P (m = 3, or 4 in units with >= 15 agents) shares a persistent store Z(b) over 3 shared
         artifacts (switch 0.15 / bin, kept overnight); an active member follows Z with prob rho, else own persistence
Per replicate: g of the test group (P in `store`; the top-m writers of the most-written shared artifact otherwise) with
both nulls and the decision rule; H01's binary-state composition z and allocation-TE z on the same group (r2lib);
optionally the calibrated subset search and its recovery of P. Outputs data/processed/H58-coordinated-superagents/
results/synthetic*.json.
Run: uv run python hypotheses/H58-coordinated-superagents/analysis/synthetic.py [--reps 20] [--search-reps 5]
"""
from __future__ import annotations

import json
import os
import sys
import time
import zlib
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ[_v] = "1"

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h58data as HD  # noqa: E402
import h58lib as L  # noqa: E402

OUT = HD.D / "results"
SETTINGS = [("own", 0.0), ("env", 0.5), ("store", 0.2), ("store", 0.35), ("store", 0.5), ("store", 0.7)]
SEARCH_UNITS = ["31", "38a", "39", "40", "41", "44", "51a", "51c"]


def skeleton(name):
    U = HD.load_unit(name)
    act = U.N > 0
    own_n = []
    for a in range(U.nA):
        k = ((U.Wn[a] >= 0.5 * U.tot_k) & (U.tot_k >= 3)).sum()
        own_n.append(int(min(max(k, 1), 2)))
    return {"name": name, "regime": U.regime, "act": act, "yh": U.yh.copy(), "day_of_bin": U.day_of_bin.copy(),
            "own_n": own_n, "agents": list(U.agents)}


def simulate(sk, world, rho, rng, m=None, q=0.15, stay=0.85, shared_rate=0.1, stay_shared=0.6):
    act, dob = sk["act"], sk["day_of_bin"]
    nA, nB = act.shape
    shared = [0, 1, 2]
    own, nxt = [], 3
    for a in range(nA):
        own.append(list(range(nxt, nxt + sk["own_n"][a])))
        nxt += sk["own_n"][a]
    S = np.full((nA, nB), -1, np.int64)
    ell = [own[a][0] for a in range(nA)]
    m = m or (4 if nA >= 15 else 3)
    actn = act.sum(1)
    elig = np.flatnonzero(actn >= np.median(actn))
    P = sorted(rng.choice(elig, min(m, len(elig)), replace=False).tolist())
    Pset = set(P)
    Z, F = int(rng.integers(3)), int(rng.integers(3))
    yh = sk["yh"].copy() if world != "env" else np.zeros(nB, bool)
    for b in range(nB):
        if b > 0:
            if rng.random() < q:
                Z = int(rng.choice([s for s in shared if s != Z]))
            if rng.random() < q:
                F = int(rng.choice([s for s in shared if s != F]))
                if world == "env" and rng.random() < 0.5:
                    yh[b] = True
        for a in np.flatnonzero(act[:, b]):
            if world == "store" and a in Pset and rng.random() < rho:
                k = Z
            elif world == "env" and rng.random() < rho:
                k = F
            elif rng.random() < (stay_shared if ell[a] in shared else stay):
                k = ell[a]
            elif rng.random() < shared_rate:
                k = int(rng.choice(shared))
            else:
                k = int(rng.choice(own[a]))
            S[a, b] = k
            ell[a] = k
    U = L.Unit(sk["name"], sk["regime"], sk["agents"], list(range(nxt)), dob, S, act.astype(int), yh)
    return U, P


def test_group(U, world, P, m):
    if world == "store":
        return P
    if world == "env":
        # the top writers of the shared artifacts, enough of them to own them (>= 50% of their commits)
        order = np.argsort(-U.Wn[:, :3].sum(1))
        for n in range(2, U.nA):
            if np.isin(U.shared_artifacts(order[:n]), [0, 1, 2]).any():
                return sorted(order[:n].tolist())
        return sorted(order[:max(2, U.nA // 2)].tolist())
    # data-defined crew: top-m writers of the most-written shared artifact (0..2)
    k = int(np.argmax(U.Wn[:, :3].sum(0)))
    return sorted(np.argsort(-U.Wn[:, k])[:m].tolist())


def one_rep(args):
    name, world, rho, rep, do_search = args
    sk = SK[name]
    rng = np.random.default_rng(zlib.crc32(f"{name}|{world}|{rho}|{rep}".encode()))
    U, P = simulate(sk, world, rho, rng)
    m = len(P)
    G = test_group(U, world, P, m)
    cn = L.CompNull(U, n_draw=150, seed=rep)
    ev = L.evaluate(U, G, cn, n_shift=60, seed=rep)
    out = {"unit": name, "world": world, "rho": rho, "rep": rep, "nB": U.nB, "nA": U.nA, "m": m,
           "g": ev["g"], "z_comp": ev["z_comp"], "z_shift": ev["z_shift"], "qualifies": ev["qualifies"],
           "share_join": ev["share_join"], "n_trans": ev["n_trans"], "g_out": ev["g_out"],
           "specificity": ev["specificity"]}
    try:
        bh = L.binary_h01(U, G, n_draw=200, seed=rep)
        out.update(bh)
    except Exception as e:  # noqa: BLE001
        out["bin_err"] = str(e)[:80]
    ks = L.krakauer_shift(U, G, n_draw=30, seed=rep)
    out["iota_unit"] = ks.get("iota", np.nan) if ks.get("ok") else np.nan
    out["iota_shift_mu"] = ks.get("iota_shift_mu", np.nan)
    out["z_iota_shift"] = ks.get("z_iota_shift", np.nan)
    out["iota_members"] = L.member_iota(U, G)
    gn = L.coord_gain(U, G, night=True)
    out["g_night"] = gn
    if np.isfinite(gn):
        out["z_night_comp"] = L.CompNull(U, n_draw=100, seed=rep, night=True).z(G, gn)["z"]
    if do_search:
        t0 = time.time()
        sr = L.search_calibrated(U, n_surr=5, seed=rep, max_evals=1500)
        best = sr["members"]
        out["search_p"] = sr["p_search"]
        out["search_members"] = best
        if best:
            evb = L.evaluate(U, best, cn, n_shift=60, seed=rep + 1)
            out["search_beats_surr"] = sr["beats_all_surrogates"]
            out["search_final_qualifies"] = bool(evb["qualifies"])
            out["search_qualifies"] = bool(evb["qualifies"] and sr["beats_all_surrogates"])
            out["search_jaccard"] = len(set(best) & set(P)) / len(set(best) | set(P)) if world == "store" else np.nan
            out["search_g"] = evb["g"]
        out["search_s"] = time.time() - t0
    return out


SK = {}


def init(names):
    global SK
    for n in names:
        SK[n] = skeleton(n)


def main():
    reps = int(sys.argv[sys.argv.index("--reps") + 1]) if "--reps" in sys.argv else 20
    sreps = int(sys.argv[sys.argv.index("--search-reps") + 1]) if "--search-reps" in sys.argv else 5
    only = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None
    tag = sys.argv[sys.argv.index("--tag") + 1] if "--tag" in sys.argv else ""
    names = [x["unit"] for x in HD.units_meta()]
    if only:
        names = [n for n in names if n in only]
    jobs = []
    for n in names:
        for (w, rho) in SETTINGS:
            for r in range(reps):
                jobs.append((n, w, rho, r, False))
    for n in [u for u in SEARCH_UNITS if u in names]:
        for (w, rho) in [("own", 0.0), ("env", 0.5), ("store", 0.5)]:
            for r in range(sreps):
                jobs.append((n, w, rho, 1000 + r, True))
    t0 = time.time()
    res = []
    with ProcessPoolExecutor(2, initializer=init, initargs=(names,)) as ex:
        for i, r in enumerate(ex.map(one_rep, jobs, chunksize=4)):
            res.append(r)
            if i % 100 == 0:
                print(f"{i}/{len(jobs)} {time.time() - t0:.0f}s", flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"synthetic{tag}.json").write_text(json.dumps(res, default=float))
    print(f"done {len(res)} in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
