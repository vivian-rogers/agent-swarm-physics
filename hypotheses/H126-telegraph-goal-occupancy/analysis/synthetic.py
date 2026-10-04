"""H126 synthetic validation (axis F), run BEFORE any real-data statistic. Planted truths on the real statement
skeletons (agents, statement call indices, days, windows) of six units and four segment designs; the real labels are
never read here (only the skeleton columns of stmts.parquet).

Unit worlds (6 units x R replicates):
  W1 telegraph: per-agent p_i ~ U(0.15, 0.45), tau_on ~ logU(3, 30) calls; emissions q0 = 0.05, q1 = 0.6
  W2 heavy-tailed: 4-state, dwell CV ~ 3 in both states (ra = rb = 0.04, w = 0.85), same mean dwells as W1
  W4 drift: W1 with k_on ramping x4 across the unit (by call index), k_off fixed
  W5 wall clock: switching in wall minutes (tau_on ~ logU(10, 120) min), same p_i
  W6 raw-run bias check = W1 (raw runs vs latent dwells)
Segment worlds (designs K12, K17, K38, NE38; N12_12a): rates per segment, shared emissions:
  WK1 k_on only (a x 8 at the boundary), WK2 k_off only (b / 8), WK3 symmetric (a x sqrt 8, b / sqrt 8), WK0 none.
Outputs: data/processed/H126-telegraph-goal-occupancy/synthetic/{units,segments}.parquet, summary.json
Usage: uv run --with numba python hypotheses/H126-telegraph-goal-occupancy/analysis/synthetic.py [--R 12] [--workers 2]
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h126lib as L  # noqa: E402

ROOT = HERE.parents[2]
D = ROOT / "data/processed/H126-telegraph-goal-occupancy"
OUT = D / "synthetic"
UNITS = ["U12a", "U17", "U25", "U35", "U38a", "U41"]
SEGS = ["K12", "K17", "K38", "NE38", "N12_12a"]
SKEL_COLS = ["design", "agent", "t", "pt_date", "win30", "c", "seg", "dup"]


def skeleton(design):
    df = pl.read_parquet(D / "stmts.parquet", columns=SKEL_COLS).filter(pl.col("design") == design)
    return df.with_columns(pl.lit(0, dtype=pl.Int8).alias("b_bge"))  # placeholder: real labels never loaded


def draw_rates(G, rng, wall=False):
    p = rng.uniform(0.15, 0.45, G)
    tau = np.exp(rng.uniform(np.log(10), np.log(120), G)) if wall else np.exp(rng.uniform(np.log(3), np.log(30), G))
    b = 1 / tau
    a = b * p / (1 - p)
    return a, b


def unit_job(args):
    try:
        return _unit_job(args)
    except Exception as e:  # keep the grid alive; failures are counted in the summary
        return [dict(design=args[0], world=args[1], rep=args[2], eligible=False, error=repr(e)[:200])]


def _unit_job(args):
    design, world, rep = args
    rng = np.random.default_rng(hash((design, world, rep)) % (2 ** 32))
    df = skeleton(design)
    S, meta = L.design_seq(df)
    G = S.n_rg
    truth = {}
    if world in ("W1", "W4"):
        a, b = draw_rates(G, rng)
        if world == "W4":
            # ramp k_on x4 over the unit: piecewise-constant in 4 call-index quarters, via rate groups agent x quarter
            q = np.minimum((np.argsort(np.argsort(meta["c"])) * 4) // S.n, 3)
            rg = meta["ai"] * 4 + q
            aa = np.concatenate([a[i] * np.array([0.5, 0.85, 1.35, 2.0]) for i in range(G)])
            bb = np.repeat(b, 4)
            Sx = L.make_seq(S.obs, S.step, rg, meta["seq_key"], G * 4)
            o, lat = L.simulate2(Sx, aa, bb, 0.05, 0.6, rng)
        else:
            o, lat = L.simulate2(S, a, b, 0.05, 0.6, rng)
        truth = dict(tau_on_true=float(np.median(1 / b)), p_true=float(np.mean(a / (a + b))))
    elif world == "W2":
        a, b = draw_rates(G, rng)
        ra = rb = 0.04
        w = 0.85
        # match mean dwell: mean = w/af + (1-w)/(af*ra) = 1/a  ->  af = a * (w + (1-w)/ra)
        af = np.clip(a * (w + (1 - w) / ra), 1e-5, 0.95)
        bf = np.clip(b * (w + (1 - w) / rb), 1e-5, 0.95)
        o, lat = L.simulate4(S, af, bf, ra, rb, w, w, 0.05, 0.6, rng)
        truth = dict(tau_on_true=float(np.median(1 / b)), cv_true=L.dwell_cv(float(np.median(bf)), rb, w))
    elif world == "W5":
        a, b = draw_rates(G, rng, wall=True)
        Sw = L.make_seq(S.obs, np.r_[0.0, np.diff(meta["tmin"])] * (~np.r_[True, meta["seq_key"][1:] != meta["seq_key"][:-1]]),
                        S.rg, meta["seq_key"], G)
        o, lat = L.simulate2(Sw, a, b, 0.05, 0.6, rng, wall=True)
        truth = dict(p_true=float(np.mean(a / (a + b))))
    S.obs[:] = o
    rows = []
    for qmode in ("fixed", "free"):
        r = L.evaluate_unit(S, meta, np.random.default_rng(rep), n_sim=60, qmode=qmode)
        if not r.get("eligible"):
            return [dict(design=design, world=world, rep=rep, eligible=False)]
        r.pop("_fit2"); r.pop("_S"); r.pop("_meta")
        rows.append(dict(design=design, world=world, rep=rep, qmode=qmode,
                         **{k: v for k, v in r.items() if not isinstance(v, list)}, **truth))
    return rows


def seg_build(fr, world_seg=None):
    S, meta = L.design_seq(fr, rg_mode="seg", seg_split=True, min_seg=20)
    return S


def seg_job(args):
    try:
        return _seg_job(args)
    except Exception as e:
        return dict(design=args[0], world=args[1], rep=args[2], eligible=False, error=repr(e)[:200])


def _seg_job(args):
    design, world, rep = args
    rng = np.random.default_rng(hash((design, world, rep, "s")) % (2 ** 32))
    df = skeleton(design)
    min_seg = 20 if design != "NE38" else 10
    S, meta = L.design_seq(df, rg_mode="seg", seg_split=True, min_seg=min_seg)
    if S is None:
        return dict(design=design, world=world, rep=rep, eligible=False)
    segs = meta["segs"]  # sorted: ['A','F'] or ['D','O']
    # baseline segment = F (kickoff) or O (outside debate); field segment = A or D
    base = segs.index("F") if "F" in segs else segs.index("O")
    fld = 1 - base
    b0 = 1 / 15.0
    if design == "NE38":
        pF, pA = 0.03, 0.85
    else:
        pF, pA = 0.05, 0.3
    a0 = b0 * pF / (1 - pF)
    k = {"WK0": (1, 1), "WK1": None, "WK2": None, "WK3": None}
    # choose multipliers so that p_A is reached: WK1 a only; WK2 b only; WK3 split evenly in log odds
    odds = (pA / (1 - pA)) / (pF / (1 - pF))
    mult = {"WK0": (1.0, 1.0), "WK1": (odds, 1.0), "WK2": (1.0, 1 / odds), "WK3": (math.sqrt(odds), 1 / math.sqrt(odds))}
    ma, mb = mult[world]
    a = np.zeros(2)
    b = np.zeros(2)
    a[base], b[base] = a0, b0
    a[fld], b[fld] = min(a0 * ma, 0.6), min(b0 * mb, 0.6)
    o, _ = L.simulate2(S, a, b, 0.05, 0.6, rng)
    S.obs[:] = o
    f = L.fit2(S)
    dla = math.log(f["a"][fld] / f["a"][base])
    dlb = math.log(f["b"][fld] / f["b"][base])
    fr = meta["frame"].with_columns(pl.Series("b_bge", o))
    sw = "F" if "F" in segs else "O"

    def build(x):
        Sx, mx = L.design_seq(x, rg_mode="seg", seg_split=True, min_seg=min_seg)
        if Sx is None:
            return None
        # make rg 0 = baseline, 1 = field
        if mx["segs"].index(sw) != 0:
            Sx.rg[:] = 1 - Sx.rg
        return Sx
    if design == "NE38":
        # one agent: parametric bootstrap from the fitted model
        bs = []
        for _ in range(40):
            ob, _ = L.simulate2(S, f["a"], f["b"], f["q0"], f["q1"], rng)
            Sx = L.Seq(ob, S.step, S.rg, S.ptr, S.n_rg)
            fx = L.fit2(Sx)
            bs.append((math.log(fx["a"][fld] / fx["a"][base]), math.log(fx["b"][fld] / fx["b"][base])))
        bs = np.array(bs)
    else:
        bs = L.seg_bootstrap(fr, build, rng, B=40)
    lo = np.percentile(bs, 5, axis=0)
    hi = np.percentile(bs, 95, axis=0)
    a_up = lo[0] > 0
    b_null = lo[1] <= 0 <= hi[1]
    verdict = ("k_on" if (a_up and b_null) else
               ("k_off" if ((hi[1] < 0 or lo[1] > 0) and abs(dlb) >= dla) else "inconclusive"))
    return dict(design=design, world=world, rep=rep, eligible=True, dln_a=dla, dln_b=dlb, a_lo=lo[0], a_hi=hi[0],
                b_lo=lo[1], b_hi=hi[1], verdict=verdict, true_dla=math.log(ma), true_dlb=math.log(mb))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--R", type=int, default=12)
    ap.add_argument("--Rs", type=int, default=10)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = [(u, w, r) for u in UNITS for w in ("W1", "W2", "W4", "W5") for r in range(a.R)]
    sjobs = [(d, w, r) for d in SEGS for w in ("WK0", "WK1", "WK2", "WK3") for r in range(a.Rs)]
    with Pool(a.workers) as pool:
        if a.only in ("", "units"):
            rows = [x for rr in pool.map(unit_job, jobs, chunksize=1) for x in rr]
            pl.DataFrame([r for r in rows if r.get("eligible")]).write_parquet(OUT / "units.parquet")
            print("unit errors:", sum(1 for r in rows if r.get("error")))
        if a.only in ("", "segs"):
            srows = pool.map(seg_job, sjobs, chunksize=1)
            pl.DataFrame([r for r in srows if r.get("eligible")]).write_parquet(OUT / "segments.parquet")
            print("seg errors:", sum(1 for r in srows if r.get("error")))
    print("done")


if __name__ == "__main__":
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    main()
