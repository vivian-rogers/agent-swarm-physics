"""H22 exploratory round 1 on non-holdout units (card: Observables O1-O6, Amendment 1). One process.

Reads data/processed/H22-private-goals-spin-glass/G<NN>/<unit>/ (scheme/build.py); writes results.json and
matrices.npz per unit there. `run_unit` is shared with confirm_tail.py so both use identical code paths.

Usage: uv run python hypotheses/H22-private-goals-spin-glass/analysis/explore.py [unit ...]

Round 1b (2026-10-04; the call above is the unchanged round-1 path):
  ... explore.py --base data/processed/H22-private-goals-spin-glass/r1b/<variant> [--units 51b,pu51e,...]
reads and writes under <base> (built by scheme/build.py --r1b); shared #51 units (pu51*) are known as well.
"""
from __future__ import annotations

import json
import os
import sys
import time
import zlib
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
sys.path.insert(0, str(ROOT / "hypotheses/H05-rooms-cut/analysis"))
import h22lib as L  # noqa: E402
import role_relations as RR  # noqa: E402
from build import UNITS, shared_units_51  # noqa: E402
from mf_blocks import block_J  # noqa: E402  (H05's block mean field, reused by import)

DATA = ROOT / "data/processed/H22-private-goals-spin-glass"
COUNTED_51 = ("51b", "51c", "51d")
CONTRAST = ("38a", "38b", "38c", "40", "44")
FOCUS_AGENTS = (6, 29)  # #focus room in 51c (excluded from couplings, as in H13)
SEED = 20261004
BASE = (ROOT / sys.argv[sys.argv.index("--base") + 1]) if "--base" in sys.argv else DATA
ALL_UNITS = {**UNITS, **shared_units_51()} if "--base" in sys.argv else UNITS


def load_unit(period, name):
    p = BASE / period / name
    meta = json.loads((p / "meta.json").read_text())
    ag = pl.read_parquet(p / "agents.parquet")
    wi = pl.read_parquet(p / "win_index.parquet"); wv = np.load(p / "win_vec.npy").astype(np.float64)
    di = pl.read_parquet(p / "day_index.parquet"); dv = np.load(p / "day_vec.npy").astype(np.float64)
    tk = np.load(p / "talk.npz")
    return meta, ag, wi, wv, di, dv, tk


def eligible(meta, ag, wi, di, exclude=()):
    """Population rule (card + Amendment 1): >= min(20, 0.4 D W_med) windows with >= 2 statements, present (>= 3
    statements) on >= half the unit's days."""
    D = len(meta["days"])
    thr_w = min(20, 0.4 * D * float(np.median(meta["wins_per_day"])))
    nw = wi.filter(pl.col("n") >= 2).group_by("a").len()
    nd = di.filter(pl.col("n") >= 3).group_by("a").len()
    nw = dict(nw.iter_rows()); nd = dict(nd.iter_rows())
    code = dict(zip(ag["idx"].to_list(), ag["agent"].to_list()))
    keep = [a for a in ag["idx"].to_list() if nw.get(a, 0) >= thr_w and nd.get(a, 0) * 2 >= D and code[a] not in exclude]
    return np.array(sorted(keep)), thr_w


def window_tensor(meta, wi, wv, agents):
    D = len(meta["days"])
    Wmax = max(int(wi["w"].max()) + 1, max(meta["wins_per_day"])) if wi.height else 1
    pos = {a: k for k, a in enumerate(agents)}
    X = np.zeros((D, len(agents), Wmax, wv.shape[1])); O = np.zeros((D, len(agents), Wmax), bool)
    for r, (a, d, w, n) in enumerate(wi.iter_rows()):
        if a in pos and n >= 2:
            X[d, pos[a], w] = wv[r]; O[d, pos[a], w] = True
    return X, O


def day_tensor(meta, di, dv, agents):
    D = len(meta["days"])
    pos = {a: k for k, a in enumerate(agents)}
    Hf = np.zeros((D, len(agents), dv.shape[2])); H1 = np.zeros_like(Hf); H2 = np.zeros_like(Hf)
    P = np.zeros((D, len(agents)), bool)
    for r, (a, d, n) in enumerate(di.iter_rows()):
        if a in pos and n >= 3:
            Hf[d, pos[a]] = dv[r, 0]; H1[d, pos[a]] = dv[r, 1]; H2[d, pos[a]] = dv[r, 2]; P[d, pos[a]] = True
    return Hf, H1, H2, P


def strip(m):
    return {k: v for k, v in m.items() if k not in ("J_full", "JA", "JB")}


def coupling_block(stats, D, labs, rng, roles=None, lookup=None, role_names=None, nboot=500, nnull=300):
    m = L.unit_moments(stats, D, nboot=nboot, nnull=nnull, rng=rng)
    res = {"moments": strip(m)}
    if m.get("N", 0) < 4 or "J_full" not in m:
        return res, m
    k = np.array(m["agents"])
    res["frustration"] = L.frustration_block(m, rng, nperm=2000, gs=True)
    labs_k = np.asarray(labs)[k]
    Jr = L.family_block_residual(m["J_full"], labs_k)
    fr = L.sign_shuffle_null(Jr, 2000, rng)
    # family-block residual tau3 on cross-fitted folds
    f3 = L.folds(D, 3)
    Js = [np.nan_to_num(stats.J(f)[np.ix_(k, k)]) for f in f3]
    t3r = L.tau3_from(*[L.family_block_residual(J, labs_k) for J in Js])[0]
    t3r_dc = L.tau3_from(*[L.double_center(L.family_block_residual(J, labs_k)) for J in Js])[0]
    res["family_residual"] = {"tau3": t3r, "tau3_dc": t3r_dc, "F": fr.get("F"), "F_null_mean": fr.get("F_null_mean"),
                              "p_F_low": fr.get("p_F_low")}
    if roles is not None:
        codes = {"SR": 1, "OP": 2, "K": [1, 2], "SY": 3, "NC": 4}
        # complete-matrix version (first run; same agent set as tau3 / F)
        ridx = np.array([role_names.index(roles[x]) if roles[x] is not None else -1 for x in k])
        res["treatment_complete"] = L.treatment_test(m["J_full"], ridx, lookup, codes, labs=labs_k, nperm=5000, rng=rng)
        res["treatment_complete"]["n_role_holders"] = int((ridx >= 0).sum())
        # card pair rule (primary for P4): every eligible pair with >= min_shared windows, no completeness requirement
        Jp = stats.J(np.ones(D, bool))
        ridx_all = np.array([role_names.index(roles[x]) if roles[x] is not None else -1 for x in range(len(labs))])
        res["treatment"] = L.treatment_test(Jp, ridx_all, lookup, codes, labs=np.asarray(labs), nperm=5000, rng=rng)
        res["treatment"]["n_role_holders"] = int((ridx_all >= 0).sum())
        res["treatment"]["n_pairs"] = int(np.isfinite(L.triu_vals(Jp)).sum())
    return res, m


def static_role_alignment(Hf, P, agents_roles, lookup, role_names, rng, nperm=5000):
    """Manipulation check: cos(H_i, H_j) of day-field-removed agent means, SR vs U, role permutation."""
    D, N, n = Hf.shape
    Pm = P[..., None].astype(float)
    m = (Hf * Pm).sum(1) / np.maximum(Pm.sum(1), 1)
    Dl = (Hf - m[:, None]) * Pm
    cnt = P.sum(0)
    ok = cnt >= 2
    H = Dl.sum(0)[ok] / cnt[ok][:, None]
    C = L.unit(H) @ L.unit(H).T
    ridx = np.array([role_names.index(r) if r is not None else -1 for r in np.asarray(agents_roles, dtype=object)[ok]])
    t = L.treatment_test(C, ridx, lookup, {"SR": 1, "SY": 3, "NC": 4}, labs=None, nperm=nperm, rng=rng)
    return t["raw"]


def mf_role_blocks(Jt, k_agents, roles, talk_rate):
    """H05 block_J with role labels (singletons unique): J_in = same-role pairs, J_out = all other pairs."""
    labs = []
    seen = {}
    for x in k_agents:
        r = roles[x]
        key = r if r is not None else f"_none{x}"
        labs.append(seen.setdefault(key, len(seen)))
    labs = np.array(labs)
    i, j = np.triu_indices(len(k_agents), 1)
    v = 4 * talk_rate * (1 - talk_rate)
    sv = np.sqrt(v[i] * v[j])
    r = Jt[i, j]
    try:
        out = block_J(i, j, r, sv, labs)
        return {k: out[k] for k in ("J_in", "J_out", "J_in_minus_out", "loop_gain")}
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)}


def run_unit(name, units=None, nboot=500, nnull=300, quick=False):
    units = units or ALL_UNITS
    period, a, b = units[name]
    rng = np.random.default_rng(SEED + zlib.crc32(name.encode()) % 1000)
    meta, ag, wi, wv, di, dv, tk = load_unit(period, name)
    D = len(meta["days"])
    excl = FOCUS_AGENTS if name in ("51c", "pu51g") else ()
    keep, thr_w = eligible(meta, ag, wi, di, exclude=excl)
    code = ag["agent"].to_numpy(); labs_all = ag["lab"].fill_null("?").to_numpy()
    roles_all = ag["role"].to_list()
    out = {"unit": name, "period": period, "days": meta["days"], "D": D, "N_eligible": int(len(keep)),
           "eligible_agents": code[keep].tolist(), "window_threshold": thr_w, "excluded": list(excl)}
    is51 = period == "G51"
    role_names = sorted({r for r in roles_all if r is not None}) if is51 else None
    lookup = RR.lookup_table(role_names) if is51 else None
    roles_k = [roles_all[x] for x in keep] if is51 else None
    # ---- content couplings
    X, O = window_tensor(meta, wi, wv, keep)
    Dp = D
    if D < 7:
        X, O = L.to_pseudo_days(X, O, 3, meta["wins_per_day"])
        Dp = 3 * D
    out["pseudo_days"] = Dp != D
    st = L.ContentStats(X, O)
    res_c, mc = coupling_block(st, Dp, labs_all[keep], rng, roles=dict(enumerate(roles_k)) if is51 else None,
                               lookup=lookup, role_names=role_names, nboot=nboot, nnull=nnull)
    out["content"] = res_c
    if "agents" in mc:
        out["content"]["agents"] = code[keep][mc["agents"]].tolist()
    # ---- talk couplings
    c, cs = (tk["c"], tk["cs"]) if D >= 7 else (tk["c3"], tk["cs3"])
    tstats = L.TalkStats(c[:, keep][:, :, keep], cs[:, :, keep][:, :, :, keep])
    res_t, mt = coupling_block(tstats, c.shape[0], labs_all[keep], rng, roles=dict(enumerate(roles_k)) if is51 else None,
                               lookup=lookup, role_names=role_names, nboot=nboot, nnull=nnull)
    out["talk"] = res_t
    if is51 and "J_full" in mt and "talk_rate" in ag.columns:
        kk = np.array(mt["agents"])
        tr = ag["talk_rate"].to_numpy()[keep][kk]
        out["talk"]["mf_role_blocks"] = mf_role_blocks(mt["J_full"], list(range(len(kk))), {x: roles_k[kk[x]] for x in range(len(kk))}, tr)
    # ---- static role alignment (manipulation check) and overlaps
    Hf, H1, H2, P = day_tensor(meta, di, dv, keep)
    if is51:
        out["static_role_alignment"] = static_role_alignment(Hf, P, roles_k, lookup, role_names, rng)
    keepA = P.sum(0) * 2 >= D
    if D >= 4 and keepA.sum() >= 4:
        h1, h2, hf = L.day_field_remove(Hf[:, keepA], H1[:, keepA], H2[:, keepA], P[:, keepA])
        o = L.overlap_stats(h1, h2, P[:, keepA], nshift=500 if quick else 2000, rng=rng)
        out["overlap"] = {k: v for k, v in o.items() if k != "q"}
        out["overlap"]["N"] = int(keepA.sum()); out["overlap"]["counted"] = D >= 7
        qmat = o["q"]
        if period != "G51":  # post-hoc (added after the first run): per-room day fields for two-room periods
            rooms = ag["room_mode"].fill_null(-1).to_numpy()[keep][keepA]
            g1, g2, gf = L.day_field_remove_groups(Hf[:, keepA], H1[:, keepA], H2[:, keepA], P[:, keepA], rooms)
            o2 = L.overlap_stats(g1, g2, P[:, keepA], nshift=500 if quick else 2000, rng=rng)
            out["overlap_room_field"] = {k: v for k, v in o2.items() if k != "q"}
    else:
        qmat = None
    # ---- variants
    variants = {}
    if name == "51c":  # keep the #focus agents
        keep2, _ = eligible(meta, ag, wi, di)
        X2, O2 = window_tensor(meta, wi, wv, keep2)
        m2 = L.unit_moments(L.ContentStats(X2, O2), D, nboot=0, nnull=100, rng=rng)
        variants["with_focus_agents"] = strip(m2)
    if period != "G51":  # largest room only (room rival)
        rooms = ag["room_mode"].to_numpy(); pur = ag["purity"].to_numpy()
        kr = np.array([x for x in keep if pur[x] is not None and pur[x] >= 0.9])
        if len(kr):
            vals, cnt = np.unique(rooms[kr], return_counts=True)
            big = vals[np.argmax(cnt)]
            kr = np.array([x for x in kr if rooms[x] == big])
            if len(kr) >= 5:
                X3, O3 = window_tensor(meta, wi, wv, kr)
                if D < 7:
                    X3, O3 = L.to_pseudo_days(X3, O3, 3, meta["wins_per_day"])
                m3 = L.unit_moments(L.ContentStats(X3, O3), X3.shape[0], nboot=200, nnull=100, rng=rng)
                variants["largest_room"] = strip(m3)
                variants["largest_room"]["room"] = int(big)
                if "J_full" in m3:
                    variants["largest_room"]["frustration"] = L.frustration_block(m3, rng, nperm=1000, gs=False)["shuffle"]
    out["variants"] = variants
    # save
    p = BASE / period / name
    mats = {}
    mats["Jc_pair"] = st.J(np.ones(Dp, bool)); mats["Jc_pair_agents"] = code[keep]
    if "J_full" in mc:
        mats["Jc"] = mc["J_full"]; mats["Jc_agents"] = code[keep][mc["agents"]]
    if "J_full" in mt:
        mats["Jt"] = mt["J_full"]; mats["Jt_agents"] = code[keep][mt["agents"]]
    if qmat is not None:
        mats["q"] = qmat
    np.savez_compressed(p / "matrices.npz", **mats)
    (p / "results.json").write_text(json.dumps(out, indent=1, default=_js))
    return out


def _js(x):
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating,)):
        return float(x)
    if isinstance(x, np.ndarray):
        return x.tolist()
    return str(x)


def main():
    if "--base" in sys.argv:
        names = sys.argv[sys.argv.index("--units") + 1].split(",") if "--units" in sys.argv else list(ALL_UNITS)
    else:
        names = sys.argv[1:] or list(UNITS)
    t0 = time.time()
    for n in names:
        r = run_unit(n)
        c = r["content"].get("moments", {})
        print(f"{n}: N={r['N_eligible']} content tau3={c.get('tau3')} tau3_dc={c.get('tau3_dc')} kappa={c.get('kappa')} "
              f"p_rho={c.get('p_rho')} ({time.time() - t0:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
