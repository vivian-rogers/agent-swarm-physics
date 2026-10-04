"""H22 round 1c, RIF: read vs in-flight content response by pair class (closes the open convergence impostor of the
content clause P4; card "Round 1c", pre-registered 2026-10-04 22:10 UTC).

  uv run python hypotheses/H22-private-goals-spin-glass/analysis/r1c_readflight.py [--model bge_small]

Model (pooled over target agents within a unit; isotropic scalar coefficients on the stacked 32 coordinates):
  z_B = a zP + a' e + b f + h H + lam_conf U_conf + lam_oth U_oth + chi_conf R_conf + chi_oth R_oth + xi
  z_B: target statement (whitened, goal / kickoff / period-mean field projected out; infra/shared/read_response.py);
  zP, e, f, H: read_response nuisance (own previous statement, own EWMA, room-day leave-out field, human reads);
  R_c: read agent statements from senders whose pair class with the target (DQ6 roles on that day) is c, weights
       exp(-age/900 s), R_c = sum_c w z / (1 + sum_all w)  (so R_conf + R_oth = read_response's R);
  U_c: in-flight statements (posted during the target's call, unread) from class c, same form.
  conflict = SR or OP (scheme/role_relations.py); other = every other pair (incl. agents without a role).
Gamma = (chi_conf - lam_conf) - (chi_oth - lam_oth). Inference: room x 1-h block bootstrap (1,000); placebo pair sets
(the same number of pseudo-conflict pairs drawn among pairs that read each other) as a descriptive size check.
Inputs: H65's G51 targets/reads (holdout masked by H65's builder; holdout_mask re-applied here), H22 unit days.
Writes data/processed/H22-private-goals-spin-glass/r1c/readflight_<model>.json.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
sys.path.insert(0, str(ROOT / "infra/shared"))
import role_relations as RR  # noqa: E402
import read_response as RRS  # noqa: E402
from common import holdout_mask  # noqa: E402
from r1c_stance import jdump  # noqa: E402
import stance_noise as SN  # noqa: E402

H65 = ROOT / "data/processed/H65-leaders-are-routers"
R1B = ROOT / "data/processed/H22-private-goals-spin-glass/r1b/bge_small_white32_none"
OUT = ROOT / "data/processed/H22-private-goals-spin-glass/r1c"
COUNTED = ["51b", "51c", "51d"]
TAU = 900.0
B = 1000
NPLAC = 200
SEED = 20261004
COLS = ["zP", "e", "f", "H", "U_conf", "U_oth", "R_conf", "R_oth"]


def unit_design(u, model, tg_all, rd_all, Zs, pos, Hm, hpos, spells):
    meta = json.loads((R1B / "G51" / u / "meta.json").read_text())
    days = meta["days"]
    assert not any(holdout_mask(days, [51] * len(days)))
    tg = tg_all.filter(pl.col("pt_date").is_in(days))
    rd = rd_all.join(tg.select("tgt"), on="tgt", how="semi")
    D = RRS.build_design(tg, rd, Zs, pos, Hm, hpos)
    tgs = D.tg  # sorted by tgt
    n = tgs.height
    agent = tgs["agent"].to_numpy()
    day = tgs["pt_date"].to_list()
    tgt_ids = tgs["tgt"].to_numpy()
    idx = {int(x): k for k, x in enumerate(tgt_ids)}
    role_cache = {}

    def role(a, d):
        key = (int(a), d)
        if key not in role_cache:
            role_cache[key] = RR.role_on(spells, int(a), d)
        return role_cache[key]

    # per target, per sender: read sums (from D.S) and in-flight sums (from reads, kind 2)
    inflight = {}
    tk = rd["tgt"].to_numpy(); kind = rd["src_kind"].to_numpy(); snd = rd["sender"].to_numpy(); vr = rd["vrow"].to_numpy()
    w = np.exp(-np.maximum(rd["age_s"].to_numpy().astype(float), 0) / TAU)
    Wu = np.zeros(n)
    for r in np.flatnonzero(kind == 2):
        k = idx.get(int(tk[r]))
        p = pos.get(int(vr[r]))
        if k is None or p is None:
            continue
        dd = inflight.setdefault(k, {})
        if snd[r] in dd:
            dd[snd[r]][0] += w[r] * Zs[p]
            dd[snd[r]][1] += w[r]
        else:
            dd[snd[r]] = [w[r] * Zs[p], w[r]]
        Wu[k] += w[r]
    pair_cls = {}
    for k in range(n):
        for i in list(D.S.get(k, {}).keys()) + list(inflight.get(k, {}).keys()):
            pair_cls[(k, int(i))] = RR.pair_class(role(agent[k], day[k]), role(i, day[k]))
    return {"D": D, "inflight": inflight, "Wu": Wu, "pair_cls": pair_cls, "agent": agent, "day": day, "n": n}


def split_regressors(U, conf_pairs=None):
    """R_conf, R_oth, U_conf, U_oth. conf_pairs: set of unordered agent pairs treated as 'conflict' (placebo), else
    the real pair classes (SR, OP)."""
    D = U["D"]
    n, dim = D.z.shape
    Rc = np.zeros((n, dim)); Ro = np.zeros((n, dim)); Uc = np.zeros((n, dim)); Uo = np.zeros((n, dim))
    for k in range(n):
        j = int(U["agent"][k])
        for src, Wtot, (A, Bm) in ((D.S.get(k, {}), 1 + D.W[k], (Rc, Ro)), (U["inflight"].get(k, {}), 1 + U["Wu"][k], (Uc, Uo))):
            for i, (v, _ww) in src.items():
                i = int(i)
                if conf_pairs is None:
                    isc = U["pair_cls"].get((k, i), 0) in (1, 2)
                else:
                    isc = (min(i, j), max(i, j)) in conf_pairs
                (A if isc else Bm)[k] += v / Wtot
    return Rc, Ro, Uc, Uo


def block_grams(U, Rc, Ro, Uc, Uo, block_s=3600):
    D = U["D"]
    t = D.tg["t"].dt.epoch("s").to_numpy()
    room = D.tg["room"].to_numpy().astype(np.int64)
    blk = room * 10_000_000 + t // block_s
    ub, binv = np.unique(blk, return_inverse=True)
    M = np.stack([D.X["zP"], D.X["e"], D.X["f"], D.X["H"], Uc, Uo, Rc, Ro], 1)  # n x 8 x 32
    G = np.einsum("npd,nqd->npq", M, M)
    c = np.einsum("npd,nd->np", M, D.z)
    nb = len(ub)
    Gb = np.zeros((nb, 8, 8)); cb = np.zeros((nb, 8))
    for p in range(8):
        cb[:, p] = np.bincount(binv, c[:, p], nb)
        for q in range(8):
            Gb[:, p, q] = np.bincount(binv, G[:, p, q], nb)
    exp_c = np.array([(np.linalg.norm(Rc, axis=1) > 0).sum(), (np.linalg.norm(Uc, axis=1) > 0).sum(),
                      (np.linalg.norm(Ro, axis=1) > 0).sum(), (np.linalg.norm(Uo, axis=1) > 0).sum()])
    return Gb, cb, exp_c


def solve(Gb, cb, w):
    G = np.tensordot(w, Gb, 1); c = w @ cb
    tr = np.trace(G) / 8
    beta = np.linalg.solve(G + 1e-8 * tr * np.eye(8), c)
    return dict(zip(COLS, beta))


def gamma(b):
    return (b["R_conf"] - b["U_conf"]) - (b["R_oth"] - b["U_oth"])


def run_unit(u, model, tg_all, rd_all, Zs, pos, Hm, hpos, spells, rng):
    t0 = time.time()
    U = unit_design(u, model, tg_all, rd_all, Zs, pos, Hm, hpos, spells)
    Rc, Ro, Uc, Uo = split_regressors(U)
    Gb, cb, expc = block_grams(U, Rc, Ro, Uc, Uo)
    nb = len(cb)
    est = solve(Gb, cb, np.ones(nb))
    g0 = gamma(est)
    boots = []
    for _ in range(B):
        wv = np.bincount(rng.integers(0, nb, nb), None, nb).astype(float)
        try:
            bb = solve(Gb, cb, wv)
            boots.append([gamma(bb), bb["R_conf"] - bb["U_conf"], bb["R_oth"] - bb["U_oth"], bb["R_conf"], bb["U_conf"]])
        except np.linalg.LinAlgError:
            continue
    boots = np.array(boots)
    q = lambda col: [float(np.quantile(boots[:, col], 0.025)), float(np.quantile(boots[:, col], 0.975))]
    # placebo pair sets: as many pseudo-conflict pairs as real conflict pairs that read each other in the unit
    real_conf = {(min(int(U["agent"][k]), i), max(int(U["agent"][k]), i)) for (k, i), c in U["pair_cls"].items() if c in (1, 2)}
    allp = sorted({(min(int(U["agent"][k]), i), max(int(U["agent"][k]), i)) for (k, i) in U["pair_cls"]} - {(a, a) for a in range(200)})
    plac = []
    for _ in range(NPLAC):
        pick = rng.choice(len(allp), min(len(real_conf), len(allp)), replace=False)
        S = {allp[i] for i in pick}
        r_ = split_regressors(U, S)
        Gp, cp, _ = block_grams(U, *r_)
        plac.append(gamma(solve(Gp, cp, np.ones(len(cp)))))
    plac = np.array(plac)
    out = {"unit": u, "model": model, "n_targets": U["n"], "n_blocks": nb, "n_conflict_pairs": len(real_conf),
           "targets_exposed": {"R_conf": int(expc[0]), "U_conf": int(expc[1]), "R_oth": int(expc[2]), "U_oth": int(expc[3])},
           "coef": est, "Gamma": g0, "Gamma_ci": q(0), "Gamma_se": float(boots[:, 0].std()),
           "read_minus_inflight_conf": est["R_conf"] - est["U_conf"], "rmi_conf_ci": q(1),
           "read_minus_inflight_oth": est["R_oth"] - est["U_oth"], "rmi_oth_ci": q(2),
           "chi_conf_ci": q(3), "lam_conf_ci": q(4),
           "placebo_pct": float(np.mean(plac <= g0)), "placebo_sd": float(plac.std()), "placebo_mean": float(plac.mean()),
           "seconds": round(time.time() - t0, 1)}
    print(jdump({k: v for k, v in out.items() if k != "coef"}).replace("\n", " "), flush=True)
    return out


def main():
    model = sys.argv[sys.argv.index("--model") + 1] if "--model" in sys.argv else "bge_small"
    rng = np.random.default_rng(SEED + 7)
    tg, rd, Zs, pos, Hm, hpos, regime = RRS.load_unit(H65, 51, model)
    hm = holdout_mask(tg["pt_date"].to_list(), [51] * tg.height)
    assert not any(hm), "held-out targets in H65's G51 table"
    spells = RR.load_role_spells_gt()
    res = {"units": {}}
    for u in COUNTED:
        res["units"][u] = run_unit(u, model, tg, rd, Zs, pos, Hm, hpos, spells, rng)
    est = [res["units"][u]["Gamma"] for u in COUNTED]
    se = [res["units"][u]["Gamma_se"] for u in COUNTED]
    res["RE_Gamma"] = SN.dl_random_effects(est, se)
    est2 = [res["units"][u]["read_minus_inflight_conf"] for u in COUNTED]
    se2 = [(res["units"][u]["rmi_conf_ci"][1] - res["units"][u]["rmi_conf_ci"][0]) / 3.92 for u in COUNTED]
    res["RE_read_minus_inflight_conf"] = SN.dl_random_effects(est2, se2)
    est3 = [res["units"][u]["read_minus_inflight_oth"] for u in COUNTED]
    se3 = [(res["units"][u]["rmi_oth_ci"][1] - res["units"][u]["rmi_oth_ci"][0]) / 3.92 for u in COUNTED]
    res["RE_read_minus_inflight_oth"] = SN.dl_random_effects(est3, se3)
    res["settings"] = {"B": B, "block_s": 3600, "tau_s": TAU, "n_placebo": NPLAC, "label": "round 1c, stance v2.1 (content arm)"}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"readflight_{model}.json").write_text(jdump(res))
    print(jdump({k: v for k, v in res.items() if k != "units"}))


if __name__ == "__main__":
    main()
