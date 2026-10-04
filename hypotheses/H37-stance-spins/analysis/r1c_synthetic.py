"""H37 round 1c synthetic validation (pre-registered; run before r1c.py on real flags).

On the real reply structures of the v2 population (flags never read):
  #12  debate-phase debater pairs: worlds null (fields sd 0.5 / 1.0), null + differential false positives (x2, x4),
       antiferromagnets Delta = 0.7, 1.5, 2.5 log-odds (true teammate rate 4%). Tests: gamma_f team permutation,
       noise-aware agent-field null, stress null; bias and CI coverage of the true-scale beta-hat.
  #51  role holders: worlds null, SR +1 / +2, OP +1 / +2 log-odds (true base rate 1.2%). Tests: role permutation of
       the FE linear-probability class coefficients; bias of the noise-aware true-scale betas; excess-pair count.
  #26  voters: +1 / +2 / +4 log-odds per unit of ballot dissimilarity; Mantel power.
Expected observed flag rates per world are reported. Label noise: labelnoise.draws (precision ~ 0.64, recall ~ 0.60).
Usage: uv run python hypotheses/H37-stance-spins/analysis/r1c_synthetic.py [--fast]
Writes data/processed/H37-stance-spins/r1c/synthetic.json.
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
sys.path.insert(0, str(HERE))
import labelnoise as N  # noqa: E402
import r1c as R1  # noqa: E402

FAST = "--fast" in sys.argv
SMOKE = "--smoke" in sys.argv
R12 = 3 if SMOKE else (30 if FAST else 100)
R51 = 2 if SMOKE else (10 if FAST else 30)
R26 = 3 if SMOKE else (50 if FAST else 200)


def sig(x):
    return 1 / (1 + np.exp(-x))


def world12(S, delta, sd, ratio, rng):
    mu = np.log(0.04 / 0.96)
    a = rng.normal(0, sd, S.NA); b = rng.normal(0, sd, S.NA)
    d = rng.random(len(S.opp)) < sig(mu + a[S.spk] + b[S.tgt] + delta * S.opp)
    _, R, phi = N.draws(1, rng)[0]
    grp = S.opp.astype(int)
    phv = N.stress_phi(phi, grp, np.array([1.0, ratio]))
    f = N.observe(d, R, phv, rng)
    g = S.gamma(f)
    PX = S.perm_x(1000, rng); PXr = PX - (PX @ S.Q) @ S.Q.T
    gp = (PXr @ R1.resid(S.Q, f)) / (PXr * PXr).sum(1)
    naf, nst = [], []
    for _, Rk, phk in N.draws(6, rng):
        par = N.fit(f, S.spk, S.tgt, None, S.NA, Rk, phk)
        phs = N.stress_phi(phk, grp, np.array([1.0, ratio]))
        pars = N.fit(f, S.spk, S.tgt, None, S.NA, Rk, phs)
        for _ in range(25):
            naf.append(S.gamma(N.simulate(S.spk, S.tgt, None, par, Rk, phk, rng)))
            nst.append(S.gamma(N.simulate(S.spk, S.tgt, None, pars, Rk, phs, rng)))
    X = S.opp.astype(float)[:, None]
    dr = N.draws(60, rng)
    bh = np.mean([N.fit(f, S.spk, S.tgt, X, S.NA, Rk, phk)["beta"][0] for _, Rk, phk in dr[:6]])
    bs = []
    for k in range(60):
        ix = np.concatenate([np.flatnonzero(S.deb == x) for x in rng.choice(S.debs, len(S.debs))])
        if X[ix, 0].min() == X[ix, 0].max():
            continue
        bs.append(N.fit(f[ix], S.spk[ix], S.tgt[ix], X[ix], S.NA, dr[k, 1], dr[k, 2])["beta"][0])
    lo, hi = np.quantile(bs, [0.025, 0.975])
    return {"obs_same": f[~S.opp].mean(), "obs_opp": f[S.opp].mean(), "true_same": d[~S.opp].mean(), "true_opp": d[S.opp].mean(),
            "gamma": g, "p_perm": R1.pv(g, gp), "p_af": R1.pv(g, naf), "p_stress": R1.pv(g, nst), "bh": bh, "lo": lo, "hi": hi}


def world51(S, cls, beta_sr, beta_op, rng, nperm):
    mu = np.log(0.012 / 0.988)
    a = rng.normal(0, 0.7, S.NA); b = rng.normal(0, 0.7, S.NA)
    eta = mu + a[S.spk] + b[S.tgt] + beta_sr * (cls == 1) + beta_op * (cls == 2)
    d = rng.random(len(cls)) < sig(eta)
    _, R, phi = N.draws(1, rng)[0]
    f = N.observe(d, R, phi, rng)
    bo = S.betas(f)
    bp = S.perm(f, nperm, rng)
    X = np.column_stack([(cls == k).astype(float) for k in (1, 2, 3, 4)] + [S.lab])
    bt = N.fit(f, S.spk, S.tgt, X, S.NA, N.R_MEAN, N.phi_from(N.Q_POP, N.PPV_MEAN, N.R_MEAN))["beta"][:2]
    return {"obs_U": f[cls == 0].mean(), "obs_SR": f[cls == 1].mean(), "obs_OP": f[cls == 2].mean(),
            "true_U": d[cls == 0].mean(), "true_SR": d[cls == 1].mean(), "true_OP": d[cls == 2].mean(),
            "p_SR": R1.pv(bo[0], bp[:, 0]), "p_OP": R1.pv(bo[1], bp[:, 1]), "bt_SR": bt[0], "bt_OP": bt[1], "flags": f.sum()}


def main():
    t0 = time.time()
    rng = np.random.default_rng(20261006)
    out = {"reps": {"g12": R12, "g51": R51, "g26": R26}}
    # ---------------------------------------------------------------- #12
    df, debs = R1.g12_frame()
    deb = df.filter((pl.col("phase") == "deb") & pl.col("rel").is_not_null()).with_columns(pl.lit(0.0).alias("f"))
    S = R1.G12(deb, debs)
    out["g12_structure"] = {"n": deb.height, "n_opp": int(S.opp.sum()), "n_same": int((~S.opp).sum()), "agents": S.NA, "debates": len(S.debs)}
    out["g12"] = {}
    for name, delta, sd, ratio in [("null_sd0.5", 0, 0.5, 1), ("null_sd1.0", 0, 1.0, 1), ("diffFP_x2", 0, 0.5, 2), ("diffFP_x4", 0, 0.5, 4),
                                   ("af_0.7", 0.7, 0.5, 1), ("af_1.5", 1.5, 0.5, 1), ("af_2.5", 2.5, 0.5, 1)]:
        rows = [world12(S, delta, sd, ratio, rng) for _ in range(R12)]
        A = {k: np.array([r[k] for r in rows], float) for k in rows[0]}
        w = {k: float(np.nanmean(A[k])) for k in ("obs_same", "obs_opp", "true_same", "true_opp", "gamma")}
        for t in ("p_perm", "p_af", "p_stress"):
            w[f"rate_{t}_lt05"] = float(np.mean(A[t] < 0.05)); w[f"rate_{t}_lt01"] = float(np.mean(A[t] < 0.01))
        w["bh_median"] = float(np.median(A["bh"])); w["bh_coverage95"] = float(np.mean((A["lo"] <= delta) & (delta <= A["hi"])))
        w["bh_ci_excludes0"] = float(np.mean(A["lo"] > 0))
        out["g12"][name] = w
        print("g12", name, json.dumps(w), flush=True)
    # ---------------------------------------------------------------- #51
    d51, maj = R1.g51_frame()
    S51 = R1.G51(d51.with_columns(pl.lit(0.0).alias("f")), maj)
    cls = S51.classes()
    out["g51_structure"] = {"n": d51.height, "agents": S51.NA, "class_rows": {R1.CLASS_NAMES[k]: int((cls == k).sum()) for k in range(5)}}
    out["g51"] = {}
    for name, bsr, bop in [("null", 0, 0), ("SR+1", 1, 0), ("SR+2", 2, 0), ("OP+1", 0, 1), ("OP+2", 0, 2), ("OP+3", 0, 3)]:
        rows = [world51(S51, cls, bsr, bop, rng, 300 if not FAST else 150) for _ in range(R51)]
        A = {k: np.array([r[k] for r in rows], float) for k in rows[0]}
        w = {k: float(np.nanmean(A[k])) for k in ("obs_U", "obs_SR", "obs_OP", "true_U", "true_SR", "true_OP", "flags")}
        w["power_SR_05"] = float(np.mean(A["p_SR"] < 0.05)); w["power_OP_05"] = float(np.mean(A["p_OP"] < 0.05))
        w["bt_SR_median"] = float(np.median(A["bt_SR"])); w["bt_OP_median"] = float(np.median(A["bt_OP"]))
        out["g51"][name] = w
        print("g51", name, json.dumps(w), flush=True)
    # ---------------------------------------------------------------- #26
    rv, voters, Dm, spk, tgt = R1.g26_struct()
    n = len(voters)
    out["g26_structure"] = {"n_replies": rv.height, "voters": n}
    out["g26"] = {}
    for bb in (0, 1, 2, 4):
        ps = []
        for _ in range(R26):
            a = rng.normal(0, 0.5, n); b = rng.normal(0, 0.5, n)
            mu = np.log(0.01 / 0.99)
            d = rng.random(len(spk)) < sig(mu + a[spk] + b[tgt] + bb * Dm[spk, tgt])
            _, R, phi = N.draws(1, rng)[0]
            f = N.observe(d, R, phi, rng)
            r_, p_ = R1.g26_mantel(R1.g26_pairmat(spk, tgt, f, n), Dm, 300, rng)
            ps.append(p_ if np.isfinite(p_) else 1.0)
        out["g26"][f"beta_{bb}"] = {"power_05": float(np.mean(np.array(ps) < 0.05)), "testable_rate": float(np.mean(np.array(ps) < 1.0))}
        print("g26", bb, out["g26"][f"beta_{bb}"], flush=True)
    out["seconds"] = round(time.time() - t0, 1)
    R1.OUT.mkdir(parents=True, exist_ok=True)
    (R1.OUT / ("synthetic_smoke.json" if SMOKE else "synthetic_fast.json" if FAST else "synthetic.json")).write_text(R1.jdump(out))
    print("done", out["seconds"])


if __name__ == "__main__":
    main()
