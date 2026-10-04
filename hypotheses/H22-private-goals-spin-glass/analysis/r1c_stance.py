"""H22 round 1c: the stance channel re-tested with the validated v2.1 conflict flag (card "Round 1c", pre-registered
2026-10-04 22:10 UTC).

  uv run python hypotheses/H22-private-goals-spin-glass/analysis/r1c_stance.py synth   # synthetic validation first
  uv run python hypotheses/H22-private-goals-spin-glass/analysis/r1c_stance.py real    # P4v2, P4v2-s, P3v2, G23v2

Inputs: shared reply_stance_v2 (non-holdout; holdout_mask re-applied), chat_core (B time for conversation blocks), H22's
round-1b unit folders (agents, DQ6 roles, days). Writes data/processed/H22-private-goals-spin-glass/r1c/{synth,stance}.json.
Pair classes: scheme/role_relations.py (U 0, SR 1, OP 2, SY 3, NC 4). Statistic T^D_K: mean two-way (speaker, target)
residual of D = disagree_validated_agent over replies in class K minus that over U (percentage points of replies).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from multiprocessing import Pool  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import role_relations as RR  # noqa: E402
import stance_noise as SN  # noqa: E402

SH = ROOT / "data/processed/shared"
R1B = ROOT / "data/processed/H22-private-goals-spin-glass/r1b/bge_small_white32_none"
OUT = ROOT / "data/processed/H22-private-goals-spin-glass/r1c"
SEED = 20261004
UNITS = ["51a", "51b", "51c", "51d", "51e"]
COUNTED = ["51b", "51c", "51d"]
CLASSES = {"SR": [1], "OP": [2], "K": [1, 2], "SY": [3]}
SIDE = {"SR": "greater", "OP": "greater", "K": "greater", "SY": "less"}
R_NULL = 2000
BLOCK_S = 1800


def jdump(o):
    def d(x):
        if isinstance(x, dict):
            return {str(k): d(v) for k, v in x.items()}
        if isinstance(x, (list, tuple)):
            return [d(v) for v in x]
        if isinstance(x, np.ndarray):
            return d(x.tolist())
        if isinstance(x, (np.floating, float)):
            return None if not np.isfinite(x) else float(x)
        if isinstance(x, np.integer):
            return int(x)
        if isinstance(x, np.bool_):
            return bool(x)
        return x
    return json.dumps(d(o), indent=1)


_V2 = None


def v2_51():
    global _V2
    if _V2 is None:
        d = SN.load_v2().filter((pl.col("goal_no") == 51) & (pl.col("a_kind") == 0) & (pl.col("b_agent") != pl.col("a_agent")))
        cc = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t"]).rename({"message_id": "B_message_id"})
        _V2 = d.join(cc, on="B_message_id", how="left")
    return _V2


def unit_frame(u: str):
    """Replies among the unit's agents on its days, with pair class, block, fp profile."""
    p = R1B / "G51" / u
    meta = json.loads((p / "meta.json").read_text())
    ag = pl.read_parquet(p / "agents.parquet")
    agents = ag["agent"].to_list()
    roles = dict(zip(agents, ag["role"].to_list()))
    d = v2_51().filter(pl.col("pt_date").is_in(meta["days"]) & pl.col("b_agent").is_in(agents) & pl.col("a_agent").is_in(agents))
    cls = np.array([RR.pair_class(roles[b], roles[a]) for b, a in zip(d["b_agent"].to_list(), d["a_agent"].to_list())])
    codes = {a: k for k, a in enumerate(agents)}
    spk = np.array([codes[x] for x in d["b_agent"].to_list()])
    tgt = np.array([codes[x] for x in d["a_agent"].to_list()])
    tsec = d["t"].dt.epoch("s").to_numpy()
    block = d["room"].cast(pl.Int64).to_numpy() * 10_000_000 + tsec // BLOCK_S
    return {"unit": u, "days": meta["days"], "d": d, "cls": cls, "spk": spk, "tgt": tgt, "N": len(agents), "block": block,
            "D": d["disagree_validated_agent"].cast(pl.Float64).to_numpy(), "s": d["s2_soft"].cast(pl.Float64).to_numpy(),
            "g": SN.fp_profile(d), "agents": agents, "roles": roles}


def contrasts(y, U):
    r = SN.twoway_resid(U["spk"], U["tgt"], y, U["N"])
    base = r[U["cls"] == 0].mean() if (U["cls"] == 0).any() else np.nan
    out = {}
    for k, codes in CLASSES.items():
        m = np.isin(U["cls"], codes)
        out[k] = float(r[m].mean() - base) if m.any() else np.nan
    return out


def null_stats(U, ng, rng, R, beta=0.0, x=None):
    arr = np.full((R, len(CLASSES)), np.nan)
    for i in range(R):
        y = ng.draw(rng, beta=beta, x=x)
        c = contrasts(y, U)
        arr[i] = [c[k] for k in CLASSES]
    return arr


# ================================================================================================ synthetic
def synth_job(args):
    u, orv, reps, M, seed = args
    rng = np.random.default_rng(seed)
    U = unit_frame(u)
    x_sr = (U["cls"] == 1).astype(float)
    ng_true = SN.NoiseNull([U["spk"], U["tgt"]], U["D"], U["g"], U["block"])
    out = []
    for _ in range(reps):
        y = ng_true.draw(rng, beta=np.log(orv), x=x_sr)
        c = contrasts(y, U)
        ng = SN.NoiseNull([U["spk"], U["tgt"]], y, U["g"], U["block"])   # re-fitted on the synthetic flags
        nul = null_stats(U, ng, rng, M)
        out.append({"T": [c[k] for k in CLASSES], "null_mean": np.nanmean(nul, 0).tolist(), "null_sd": np.nanstd(nul, 0).tolist(),
                    "p": [SN.p_greater(c[k], nul[:, j]) if SIDE[k] == "greater" else SN.p_less(c[k], nul[:, j])
                          for j, k in enumerate(CLASSES)], "null_SR": nul[:, 0].tolist()})
    return u, orv, out


def synth():
    t0 = time.time()
    ORS = [1.0, 2.0, 3.0, 5.0]
    REPS, M = 150, 150
    jobs = [(u, o, REPS, M, SEED + 17 * i + int(10 * o)) for i, u in enumerate(COUNTED) for o in ORS]
    with Pool(2) as p:
        res = p.map(synth_job, jobs, chunksize=1)
    by = {(u, o): r for u, o, r in res}
    summ = {"ORs": ORS, "reps": REPS, "null_draws": M, "units": {}}
    for u in COUNTED:
        U = unit_frame(u)
        summ["units"][u] = {"n_replies": int(len(U["D"])), "n_SR": int((U["cls"] == 1).sum()), "n_OP": int((U["cls"] == 2).sum()),
                            "power_SR": {str(o): float(np.mean([r["p"][0] < 0.05 for r in by[(u, o)]])) for o in ORS},
                            "mean_T_SR": {str(o): float(np.mean([r["T"][0] for r in by[(u, o)]])) for o in ORS},
                            "size_K": float(np.mean([r["p"][2] < 0.05 for r in by[(u, 1.0)]])),
                            "size_SY": float(np.mean([r["p"][3] < 0.05 for r in by[(u, 1.0)]]))}
    # pooled precision-weighted test over 51b-51d (weights 1/null var), null from the same replicates' null draws
    pooled = {}
    for o in ORS:
        hits = []
        for k in range(REPS):
            Ts, ws, nulls = [], [], []
            for u in COUNTED:
                r = by[(u, o)][k]
                sd = r["null_sd"][0]
                if not np.isfinite(r["T"][0]) or not np.isfinite(sd) or sd <= 0:
                    continue
                Ts.append(r["T"][0] - r["null_mean"][0]); ws.append(1 / sd ** 2)
                nulls.append(np.asarray(r["null_SR"]) - r["null_mean"][0])
            if not Ts:
                continue
            ws = np.array(ws) / np.sum(ws)
            stat = float(np.dot(ws, Ts))
            L = min(len(n) for n in nulls)
            nd = sum(w * n[:L] for w, n in zip(ws, nulls))
            hits.append(SN.p_greater(stat, nd) < 0.05)
        pooled[str(o)] = float(np.mean(hits)) if hits else None
    summ["pooled_power_SR"] = pooled
    summ["seconds"] = round(time.time() - t0, 1)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "synth.json").write_text(jdump(summ))
    print(jdump(summ))


# ================================================================================================ real
def real_unit(u, rng):
    U = unit_frame(u)
    n = len(U["D"])
    out = {"unit": u, "n_replies": n, "n_flags": int(U["D"].sum()), "flag_rate": float(U["D"].mean()) if n else None,
           "n_by_class": {RR.CLASS_NAMES[c]: int((U["cls"] == c).sum()) for c in range(5)},
           "flags_by_class": {RR.CLASS_NAMES[c]: int(U["D"][U["cls"] == c].sum()) for c in range(5)}}
    if n < 100 or U["D"].sum() < 3:
        out["scorable"] = False
        return out, None
    out["scorable"] = True
    T = contrasts(U["D"], U)
    Ts = contrasts(U["s"], U)
    ng = SN.NoiseNull([U["spk"], U["tgt"]], U["D"], U["g"], U["block"])
    nul = null_stats(U, ng, rng, R_NULL)
    fexp, fbar = ng.f_expected()
    Tf = contrasts(fexp, U)
    out["T_D"], out["T_s"], out["T_f"] = T, Ts, Tf
    out["null_mean"] = {k: float(np.nanmean(nul[:, j])) for j, k in enumerate(CLASSES)}
    out["null_sd"] = {k: float(np.nanstd(nul[:, j])) for j, k in enumerate(CLASSES)}
    out["p_NG"] = {k: (SN.p_greater(T[k], nul[:, j]) if SIDE[k] == "greater" else SN.p_less(T[k], nul[:, j]))
                   for j, k in enumerate(CLASSES)}
    out["T_corrected"] = {k: (T[k] - Tf[k]) / (SN.R_POINT - fbar) if np.isfinite(T[k]) else None for k in CLASSES}
    out["fbar"] = fbar
    # raw class rates (descriptive)
    out["rate_by_class"] = {RR.CLASS_NAMES[c]: float(U["D"][U["cls"] == c].mean()) if (U["cls"] == c).any() else None for c in range(5)}
    out["sr_pairs_flags"] = sorted({(int(min(b, a)), int(max(b, a))) for b, a, c in zip(U["d"]["b_agent"].to_list(), U["d"]["a_agent"].to_list(), U["cls"]) if c == 1})
    # P3v2: tau3 / tau3(dc) of J^s from s2 (round-1b code, three day folds, day bootstrap)
    import r1b_stance_native as R1
    rr = U["d"].with_columns(pl.col("s2_soft").cast(pl.Float64).alias("s"))
    out["balance_s2"] = R1.tau3_folds(rr, U["days"], U["agents"], rng, nboot=200)
    return out, nul


def pooled51(rng):
    """All non-holdout #51 days, roles by GT majority over present days (as round 1b's 51all; descriptive)."""
    pu = pl.read_parquet(SH / "period_units.parquet").filter((pl.col("goal_no") == 51) & ~pl.col("holdout"))
    days = sorted({d for ds in pu["days"].to_list() for d in ds})
    d = v2_51().filter(pl.col("pt_date").is_in(days))
    agents = sorted(set(d["b_agent"].to_list()) | set(d["a_agent"].to_list()))
    spells = RR.load_role_spells_gt()
    present = {a: sorted(set(d.filter(pl.col("b_agent") == a)["pt_date"].to_list())) or days for a in agents}
    roles = RR.unit_roles(spells, agents, days, present)
    codes = {a: k for k, a in enumerate(agents)}
    U = {"spk": np.array([codes[x] for x in d["b_agent"].to_list()]), "tgt": np.array([codes[x] for x in d["a_agent"].to_list()]),
         "N": len(agents), "cls": np.array([RR.pair_class(roles[b], roles[a]) for b, a in zip(d["b_agent"].to_list(), d["a_agent"].to_list())]),
         "D": d["disagree_validated_agent"].cast(pl.Float64).to_numpy(), "s": d["s2_soft"].cast(pl.Float64).to_numpy(), "g": SN.fp_profile(d)}
    block = d["room"].cast(pl.Int64).to_numpy() * 10_000_000 + d["t"].dt.epoch("s").to_numpy() // BLOCK_S
    T = contrasts(U["D"], U)
    ng = SN.NoiseNull([U["spk"], U["tgt"]], U["D"], U["g"], block)
    nul = null_stats(U, ng, rng, R_NULL)
    fexp, fbar = ng.f_expected()
    Tf = contrasts(fexp, U)
    return {"n_replies": len(U["D"]), "n_flags": int(U["D"].sum()), "n_by_class": {RR.CLASS_NAMES[c]: int((U["cls"] == c).sum()) for c in range(5)},
            "flags_by_class": {RR.CLASS_NAMES[c]: int(U["D"][U["cls"] == c].sum()) for c in range(5)},
            "T_D": T, "T_s": contrasts(U["s"], U), "T_f": Tf,
            "p_NG": {k: (SN.p_greater(T[k], nul[:, j]) if SIDE[k] == "greater" else SN.p_less(T[k], nul[:, j])) for j, k in enumerate(CLASSES)},
            "null_sd": {k: float(np.nanstd(nul[:, j])) for j, k in enumerate(CLASSES)},
            "T_corrected": {k: (T[k] - Tf[k]) / (SN.R_POINT - fbar) for k in CLASSES}}


def g23v2(rng):
    """Chess opponents (round-1b's 21 opponent pairs) vs other pairs: reply-level residual contrast of D."""
    prev = json.loads((ROOT / "data/processed/H22-private-goals-spin-glass/r1b/stance_native.json").read_text())
    opp = {tuple(sorted(p)) for p in prev["native_G23"]["pairs"]}
    cal = pl.read_parquet(SH / "calendar.parquet").filter(pl.col("goal_no") == 23)
    d = SN.load_v2().filter((pl.col("goal_no") == 23) & (pl.col("a_kind") == 0) & (pl.col("b_agent") != pl.col("a_agent"))
                            & pl.col("pt_date").is_in(cal["pt_date"].to_list()))
    cc = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t"]).rename({"message_id": "B_message_id"})
    d = d.join(cc, on="B_message_id", how="left")
    agents = sorted(set(d["b_agent"].to_list()) | set(d["a_agent"].to_list()))
    codes = {a: k for k, a in enumerate(agents)}
    b, a = d["b_agent"].to_numpy(), d["a_agent"].to_numpy()
    spk, tgt = np.array([codes[x] for x in b]), np.array([codes[x] for x in a])
    D = d["disagree_validated_agent"].cast(pl.Float64).to_numpy()
    g = SN.fp_profile(d)
    block = d["room"].cast(pl.Int64).to_numpy() * 10_000_000 + d["t"].dt.epoch("s").to_numpy() // BLOCK_S

    def T(y, perm=None):
        r = SN.twoway_resid(spk, tgt, y, len(agents))
        pm = perm or {x: x for x in agents}
        isopp = np.array([tuple(sorted((pm[x], pm[z]))) in opp for x, z in zip(b, a)])
        return float(r[isopp].mean() - r[~isopp].mean()) if isopp.any() and (~isopp).any() else np.nan, int(isopp.sum())
    obs, nopp = T(D)
    perm = np.array([T(D, dict(zip(agents, rng.permutation(agents))))[0] for _ in range(5000)])
    ng = SN.NoiseNull([spk, tgt], D, g, block)
    nn = np.array([T(ng.draw(rng))[0] for _ in range(R_NULL)])
    fexp, fbar = ng.f_expected()
    Tf = T(fexp)[0]
    s = d["s2_soft"].cast(pl.Float64).to_numpy()
    return {"n_replies": len(D), "n_flags": int(D.sum()), "n_opp_replies": nopp, "T_D": obs, "p_perm_greater": SN.p_greater(obs, perm),
            "p_NG_greater": SN.p_greater(obs, nn), "T_f": Tf, "T_corrected": (obs - Tf) / (SN.R_POINT - fbar),
            "T_s": T(s)[0], "flag_rate": float(D.mean())}


def real():
    t0 = time.time()
    rng = np.random.default_rng(SEED + 1)
    out = {"units": {}}
    nulls = {}
    for u in UNITS:
        r, nul = real_unit(u, rng)
        out["units"][u] = r
        nulls[u] = nul
        print(u, {k: r.get(k) for k in ("n_replies", "n_flags", "T_D", "p_NG", "T_corrected")}, flush=True)
    # random-effects and pooled precision-weighted test over the counted units
    pool = {}
    for j, k in enumerate(CLASSES):
        est = [out["units"][u]["T_D"][k] for u in COUNTED if out["units"][u].get("scorable")]
        se = [out["units"][u]["null_sd"][k] for u in COUNTED if out["units"][u].get("scorable")]
        re = SN.dl_random_effects(est, se)
        okU = [u for u in COUNTED if out["units"][u].get("scorable") and np.isfinite(out["units"][u]["T_D"][k])]
        if okU:
            w = np.array([1 / out["units"][u]["null_sd"][k] ** 2 for u in okU])
            w = w / w.sum()
            stat = float(sum(wi * (out["units"][u]["T_D"][k] - out["units"][u]["null_mean"][k]) for wi, u in zip(w, okU)))
            nd = sum(wi * (nulls[u][:, j] - np.nanmean(nulls[u][:, j])) for wi, u in zip(w, okU))
            re["pooled_stat"] = stat
            re["p_NG_pooled"] = SN.p_greater(stat, nd) if SIDE[k] == "greater" else SN.p_less(stat, nd)
            re["T_corrected_mean"] = float(np.average([out["units"][u]["T_corrected"][k] for u in okU], weights=w))
            re["units"] = okU
            re["n_same_sign_positive"] = int(sum(out["units"][u]["T_D"][k] > 0 for u in okU))
        pool[k] = re
    out["pooled_counted"] = pool
    out["pooled51"] = pooled51(rng)
    out["G23v2"] = g23v2(rng)
    out["settings"] = {"R_null": R_NULL, "pi_range": SN.PI_RANGE, "r_range": SN.R_RANGE, "sigma_u": SN.SIGMA_U, "phi": SN.phi(),
                       "sensor": "disagree_validated_agent", "label": "round 1c, stance v2.1"}
    out["seconds"] = round(time.time() - t0, 1)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "stance.json").write_text(jdump(out))
    print(jdump({"pooled_counted": pool, "pooled51": out["pooled51"], "G23v2": out["G23v2"]}))


if __name__ == "__main__":
    {"synth": synth, "real": real}[sys.argv[1]]()
