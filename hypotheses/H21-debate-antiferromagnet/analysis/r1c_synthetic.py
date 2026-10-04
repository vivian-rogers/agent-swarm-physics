"""H21 round 1c synthetic validation (pre-registered; run before r1c.py on real flags).

On the real #12 reply structure (v2 population, debater-to-debater pairs: debate phase and post window; speakers,
targets, debates, drafted teams), plant true disagreement d from logit pi = mu + a_spk + b_tgt + Delta*1[opposite],
pass it through the validated label noise (labelnoise.draws: precision ~ 0.64, recall ~ 0.60), and run r1c's tests.
The observed flags of the real data are never read here (only the reply structure).

Worlds: null (fields sd 0.5 / 1.0), null + differential false positives (phi_opp/phi_same = 2, 4), antiferromagnets
Delta = 0.7, 1.5, 2.5 (true teammate rate 4%). Reports per world: expected observed flag rates, size or power of the
team-permutation test, the noise-aware agent-field null and the stress null (alpha 0.05 and 0.01), bias and coverage
of Delta-hat, team recovery from the flag graph, and the power of the post-window test if the contrast persisted.
Usage: uv run python hypotheses/H21-debate-antiferromagnet/analysis/r1c_synthetic.py [--fast]
Writes data/processed/H21-debate-antiferromagnet/r1c/synthetic.json.
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
import afmlib as L  # noqa: E402
import labelnoise as N  # noqa: E402
import r1c as R1  # noqa: E402

FAST = "--fast" in sys.argv
REPS = (3 if "--smoke" in sys.argv else 30) if FAST else 100
WORLDS = [("null_sd0.5", 0.0, 0.5, 1.0), ("null_sd1.0", 0.0, 1.0, 1.0), ("diffFP_x2", 0.0, 0.5, 2.0), ("diffFP_x4", 0.0, 0.5, 4.0),
          ("af_0.7", 0.7, 0.5, 1.0), ("af_1.5", 1.5, 0.5, 1.0), ("af_2.5", 2.5, 0.5, 1.0)]
BASE = 0.04


def one(D, Dp, delta, sd, ratio, rng, debates):
    mu = np.log(BASE / (1 - BASE))
    a = rng.normal(0, sd, D.NA); b = rng.normal(0, sd, D.NA)
    opp = ~D.same_true
    d = rng.random(D.n) < 1 / (1 + np.exp(-(mu + a[D.spk] + b[D.tgt] + delta * opp)))
    ppv, Rr, phi = N.draws(1, rng)[0]
    grp = opp.astype(int)
    phv = N.stress_phi(phi, grp, np.array([1.0, ratio]))
    f = N.observe(d, Rr, phv, rng)
    o = D.stat(f)
    p_perm = L.p_upper(o, D.perm_null(f, 1000, rng)) if np.isfinite(o) else 1.0
    nl = R1.noise_null(D, f, D.stat, rng, K=6, M=25)
    ns = R1.noise_null(D, f, D.stat, rng, stress=(grp, np.array([1.0, ratio])), K=6, M=25)
    X = opp.astype(float)[:, None]
    dr = N.draws(60, rng)
    pt = np.mean([N.fit(f, D.spk, D.tgt, X, D.NA, r_, p_)["beta"][0] for _, r_, p_ in dr[:6]])
    bs = []
    for k in range(60):
        ix = np.concatenate([D.idx[x] for x in rng.choice(D.debs, len(D.debs))])
        if X[ix, 0].min() == X[ix, 0].max():
            continue
        bs.append(N.fit(f[ix], D.spk[ix], D.tgt[ix], X[ix], D.NA, dr[k, 1], dr[k, 2])["beta"][0])
    lo, hi = np.quantile(bs, [0.025, 0.975])
    rec = R1.recovery(D, f, debates, rng, sign=-1.0)["recovered"]
    # post window, same true model (contrast persists)
    ap = a; bp = b
    pos = {x: k for k, x in enumerate(D.agents)}
    sp = np.array([pos.get(x, -1) for x in Dp.b]); tp = np.array([pos.get(x, -1) for x in Dp.a])
    okp = (sp >= 0) & (tp >= 0)
    etap = mu + np.where(okp, ap[np.maximum(sp, 0)] + bp[np.maximum(tp, 0)], 0) + delta * (~Dp.same_true)
    dp = rng.random(Dp.n) < 1 / (1 + np.exp(-etap))
    fp = N.observe(dp, Rr, phi, rng)
    op = Dp.stat(fp)
    p_post = L.p_upper(op, Dp.perm_null(fp, 500, rng)) if np.isfinite(op) and fp.sum() > 0 else 1.0
    return {"obs_rate_same": f[~opp].mean(), "obs_rate_opp": f[opp].mean(), "true_rate_same": d[~opp].mean(), "true_rate_opp": d[opp].mean(),
            "delta_f": o, "p_perm": p_perm, "p_af": N.pval(o, nl), "p_stress": N.pval(o, ns), "dhat": pt, "lo": lo, "hi": hi,
            "recovered": rec, "p_post": p_post, "n_flags": f.sum()}


def main():
    t0 = time.time()
    rng = np.random.default_rng(20261005)
    st_pl, debates, tz = R1.load_debates()
    df = R1.g12_frame(st_pl, debates, tz).drop("f", "s2_soft", "p_disagree", "dq2_opp")   # structure only
    df = df.with_columns(pl.lit(0.0).alias("f"))
    D = R1.Design(df.filter(pl.col("debaters") & (pl.col("phase") == "deb")), debates)
    Dp = R1.Design(df.filter(pl.col("debaters") & (pl.col("phase") == "post")), debates)
    out = {"structure": {"n_deb": D.n, "n_same": int(D.same_true.sum()), "n_opp": int((~D.same_true).sum()), "n_post": Dp.n,
                         "n_debates": len(D.debs), "agents": D.NA}, "reps": REPS, "base_true_rate": BASE, "worlds": {}}
    for name, delta, sd, ratio in WORLDS:
        rows = [one(D, Dp, delta, sd, ratio, rng, debates) for _ in range(REPS)]
        A = {k: np.array([r[k] for r in rows], float) for k in rows[0]}
        w = {"delta": delta, "field_sd": sd, "phi_ratio": ratio,
             "obs_rate_same": float(A["obs_rate_same"].mean()), "obs_rate_opp": float(A["obs_rate_opp"].mean()),
             "true_rate_same": float(A["true_rate_same"].mean()), "true_rate_opp": float(A["true_rate_opp"].mean()),
             "delta_f_mean": float(np.nanmean(A["delta_f"])), "flags_mean": float(A["n_flags"].mean())}
        for t in ("p_perm", "p_af", "p_stress", "p_post"):
            w[f"rate_{t}_lt05"] = float(np.mean(A[t] < 0.05)); w[f"rate_{t}_lt01"] = float(np.mean(A[t] < 0.01))
        w["dhat_mean"] = float(np.mean(A["dhat"])); w["dhat_median"] = float(np.median(A["dhat"]))
        w["dhat_coverage95"] = float(np.mean((A["lo"] <= delta) & (delta <= A["hi"])))
        w["dhat_ci_excludes0"] = float(np.mean(A["lo"] > 0))
        w["recovered_mean"] = float(A["recovered"].mean()); w["rate_recovered_ge4"] = float(np.mean(A["recovered"] >= 4))
        out["worlds"][name] = w
        print(name, json.dumps(w), flush=True)
    out["seconds"] = round(time.time() - t0, 1)
    R1.OUT.mkdir(parents=True, exist_ok=True)
    (R1.OUT / ("synthetic_fast.json" if FAST else "synthetic.json")).write_text(R1.jdump(out))
    print("done", out["seconds"])


if __name__ == "__main__":
    main()
