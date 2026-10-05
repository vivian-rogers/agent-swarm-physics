"""H42 round 2: synthetic validation of the call-level R2/R1 estimators on the real call skeleton (before real data).

Worlds (8 replicates per unit; messages regenerated on the skeleton, see r2lib.gen_items):
  V0   fitted common field, no coupling: z = standardized log of the real room message rate (Gaussian sigma 300 s);
       strength a fitted per unit; talk x e^{a z}, pause x e^{-a z}, log gap - 0.2 a z, chat next x e^{0.5 a z},
       session start / stop x e^{-0.5 a z} (each normalized within cells).
  V0f  as V0 with sigma 60 s (fast field).
  VL   talk logit falls 0.5 per unit of centred log call duration; senders' messages follow this talk; pause, log gap
       and class outcomes are the real ones (no coupling: the synthetic messages never reach them).
  V1   V0 plus planted per-read effects (all reads at c): talk +0.08 named / +0.004 unnamed; log gap -0.05 named;
       session start -0.02 named; chat next +0.01 named. Pause (Amendment R2-A, before real data): each named read
       multiplies the pause probability by 0.7 (the additive -0.005 of the pre-registration was clipped at 0 in most
       cells, whose pause rate is ~0). The oracle truth per replicate is the realized per-read change in probability,
       sum(p1 - p0) / sum(reads) over the analysis rows (truth_named, truth_un).

Writes data/processed/H42-readout-hawkes-kernel/round2/synthetic/r2_synth.parquet.
Usage: uv run python hypotheses/H42-readout-hawkes-kernel/analysis/r2_synthetic.py [--reps 8]
"""
from __future__ import annotations

import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import r2lib as L  # noqa: E402

UNITS = ["27", "19a", "38b", "41", "51e"]
WORLDS = ["V0", "V0f", "VL", "V1"]
PLANT = {"talk": (0.08, 0.004), "pause": (-0.005, 0.0), "loggap": (-0.05, 0.0), "start": (-0.02, 0.0),
         "chatnext": (0.01, 0.0), "stop": (0.0, 0.0), "loggap_np": (0.0, 0.0)}
OUT = L.R2 / "synthetic"


def norm_mult(sk, x):
    e = np.exp(x)
    return e / L.cell_rates(sk, e)


def bern(rng, p):
    return (rng.uniform(size=len(p)) < np.clip(np.nan_to_num(p, nan=0.0), 0, 1)).astype(float)


def one(args):
    uid, world, rep = args
    t0 = time.time()
    u = L.load(uid)
    sk = L.skeleton(u)
    D0 = L.design(u, sk)                         # real-structure rows (only real talk is used, to fit a)
    rng = np.random.default_rng(abs(hash((uid, world, rep))) % (2 ** 31))
    shares = L.real_shares(u)
    sig = 60.0 if world == "V0f" else 300.0
    zc, _ = L.room_field(u, sk, sig)
    a = L.fitted_field_strength(D0, zc) if world != "VL" else 0.0
    p_talk = L.cell_rates(sk, sk.talk)
    if world == "VL":
        dur = np.log(np.maximum(np.nan_to_num(sk.te - sk.t, nan=10.0), 0.5))
        dc = dur - L.cell_rates(sk, dur)
        lp = np.log(np.clip(p_talk, 1e-4, 1 - 1e-4) / (1 - np.clip(p_talk, 1e-4, 1 - 1e-4))) - 0.5 * dc
        talk = bern(rng, 1 / (1 + np.exp(-lp)))
    else:
        talk = bern(rng, p_talk * norm_mult(sk, a * zc))
    it = L.gen_items(sk, talk, shares, rng)
    D = L.design(u, sk, it)
    Y = {}
    if world == "VL":
        Y = {"talk": talk, "pause": D["pause"], "loggap": D["loggap"], "loggap_np": D["loggap_np"],
             "chatnext": D["chatnext"], "start": D["start"], "stop": D["stop"]}
    else:
        Rn = D["Rall"][:, 0] + D["Rall"][:, 1]
        Ru = D["Rall"][:, 2]
        k = 1.0 if world == "V1" else 0.0
        pz = p_talk * norm_mult(sk, a * zc)
        Y["talk"] = bern(rng, pz + k * (PLANT["talk"][0] * Rn + PLANT["talk"][1] * Ru)) if world == "V1" else talk
        keep = D["keep"]
        truth = {}

        def oracle(o, p0, p1n, p1u=None):
            ok = keep & np.isfinite(p0)
            truth[o] = (float(np.sum((np.clip(p1n, 0, 1) - np.clip(p0, 0, 1))[ok]) / max(Rn[ok].sum(), 1)),
                        float(np.sum((np.clip(p1u, 0, 1) - np.clip(p0, 0, 1))[ok]) / max(Ru[ok].sum(), 1))
                        if p1u is not None else 0.0)
        oracle("talk", pz, pz + PLANT["talk"][0] * Rn, pz + PLANT["talk"][1] * Ru)
        q0 = L.cell_rates(sk, D["pause"]) * norm_mult(sk, -a * zc)
        q1 = q0 * (0.7 ** Rn) if world == "V1" else q0
        oracle("pause", q0, q0 * 0.7 ** Rn)
        Y["pause"] = bern(rng, q1)
        lg = D["loggap"]
        mu = L.cell_rates(sk, lg)
        res = lg - mu
        # resample residuals within cells
        perm = np.arange(len(lg))
        for c in np.unique(sk.cell):
            ix = np.flatnonzero((sk.cell == c) & np.isfinite(res))
            perm[ix] = rng.permutation(ix)
        Y["loggap"] = np.where(np.isfinite(lg), mu + res[perm] - 0.2 * a * zc + k * PLANT["loggap"][0] * Rn, np.nan)
        Y["loggap_np"] = np.where(sk.kind != "pause", Y["loggap"], np.nan)
        for o, sgn in (("chatnext", 0.5), ("start", -0.5), ("stop", -0.5)):
            base = D[o]
            p0 = L.cell_rates(sk, base) * norm_mult(sk, sgn * a * zc)
            oracle(o, np.where(np.isfinite(base), p0, np.nan), p0 + PLANT[o][0] * Rn)
            Y[o] = np.where(np.isfinite(base), bern(rng, p0 + k * PLANT[o][0] * Rn), np.nan)
        truth["loggap"] = truth["loggap_np"] = (PLANT["loggap"][0], 0.0)
    rows = []
    for o in L.OUTCOMES:
        for spec, field in (("r2", False), ("r2", True), ("r1", False)):
            if field and o not in ("talk", "pause"):
                continue
            if spec == "r1" and o != "talk":
                continue
            r = L.fit(D, o, spec=spec, field=field, B=200, seed=rep, y_override=Y[o])
            if "J_un" not in r and "J_cold" not in r:
                continue
            tn, tu = truth.get(o, (0.0, 0.0)) if world == "V1" else (0.0, 0.0)
            r.update({"unit_id": uid, "regime": u.regime, "world": world, "rep": rep, "a": a,
                      "plant_named": tn, "plant_un": tu})
            rows.append(r)
    print(uid, world, rep, f"a={a:.2f}", f"{time.time() - t0:.0f}s", flush=True)
    return rows


def main():
    reps = int(sys.argv[sys.argv.index("--reps") + 1]) if "--reps" in sys.argv else 8
    units = UNITS
    if "--units" in sys.argv:
        units = sys.argv[sys.argv.index("--units") + 1].split(",")
    jobs = [(u, w, r) for u in units for w in WORLDS for r in range(reps)]
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    with ProcessPoolExecutor(2) as ex:
        for rr in ex.map(one, jobs):
            rows += rr
            pl.DataFrame(rows, infer_schema_length=None).write_parquet(OUT / "r2_synth.parquet")


if __name__ == "__main__":
    main()
