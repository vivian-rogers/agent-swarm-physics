"""H64 synthetic validation (axis F), run before any real-data outcome. Real reply structures (who replies to whom,
when, in which conversation block), synthetic labels from the card's generative model.

    uv run python hypotheses/H64-conflict-scarce-prize/analysis/synthetic.py [s1|s2|all]

S1: size of the antagonistic-pair count (naive vs cluster-robust) against the calibrated agent-field null, under agent
    fields plus thread (block) shocks.
S2: the prize-gated DiD at the G12, G26, G23 structures: power for gated antagonism, false 'gated' calls under the
    heat and relation rivals.
Writes data/processed/H64-conflict-scarce-prize/synthetic/{s1,s2}.json.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
           "POLARS_MAX_THREADS"):
    os.environ.setdefault(_v, "1")

import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from multiprocessing import Pool  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h64lib as L  # noqa: E402

DATA = L.ROOT / "data/processed/H64-conflict-scarce-prize"
OUT = DATA / "synthetic"
SHOCKS = [(0.0, 0.0), (0.5, 0.0), (1.0, 0.0), (0.0, 1.0), (0.5, 1.0)]
S1_UNITS = [("G13", 13, None), ("G26", 26, None), ("G38", 38, None), ("G41", 41, None), ("51g", 51, "51g")]


def s1_job(args):
    name, goal, unit, (sd_u, sd_pb), rep = args
    rp = pl.read_parquet(DATA / "replies.parquet").filter(pl.col("goal_no") == goal)
    if unit:
        rp = rp.filter(pl.col("unit_id") == unit)
    spk, tgt, N, _ = L.reindex(rp["b_agent"].to_numpy(), rp["a_agent"].to_numpy())
    block = rp["block"].to_numpy()
    rng = np.random.default_rng(1000 * rep + int(10 * sd_u) + 100 * int(10 * sd_pb) + goal)
    y = L.simulate_labels(spk, tgt, block, N, rng, sd_u=sd_u, sd_pb=sd_pb)
    r = L.excess(spk, tgt, y, block, N, R=100, rng=rng)
    return {"unit": name, "sd_u": sd_u, "sd_pb": sd_pb, "rep": rep, "n": int(len(y)), "N": int(N),
            "fp_robust": r["n_neg_robust"] > r["null_p95_robust"], "fp_naive": r["n_neg_naive"] > r["null_p95_naive"],
            "E_robust": r["E_robust"], "E_naive": r["E_naive"], "p_robust": r["p_af_robust"], "p_naive": r["p_af_naive"]}


def s1(workers=4, reps=30):
    jobs = [(n, g, u, s, k) for (n, g, u) in S1_UNITS for s in SHOCKS for k in range(reps)]
    t0 = time.time()
    with Pool(workers) as p:
        res = p.map(s1_job, jobs, chunksize=2)
    df = pl.DataFrame(res)
    summ = df.group_by("unit", "sd_u", "sd_pb").agg(pl.len().alias("reps"), pl.col("n").first(), pl.col("N").first(),
                                           pl.col("fp_robust").mean().alias("size_robust"),
                                           pl.col("fp_naive").mean().alias("size_naive"),
                                           pl.col("E_robust").mean(), pl.col("E_naive").mean()).sort("unit", "sd_u", "sd_pb")
    with pl.Config(tbl_rows=40, tbl_width_chars=200):
        print(summ)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "s1.json").write_text(json.dumps({"summary": summ.to_dicts(), "runtime_s": time.time() - t0}, indent=1))


def native_frame(name):
    if name == "G12":
        d = pl.read_parquet(DATA / "g12_rel.parquet")
        return d, d["wblock"].to_numpy(), d["debate"].to_numpy(), d["debate"].to_numpy(), d["O"].to_numpy()
    if name == "G26":
        d = pl.read_parquet(DATA / "g26_rel.parquet").filter(pl.col("window") != "confirmatory")
        return d, d["window"].to_numpy(), d["block"].to_numpy(), None, d["O"].to_numpy()
    d = pl.read_parquet(DATA / "g23_rel.parquet")
    return d, d["pt_date"].to_numpy(), d["block"].to_numpy(), None, d["any_open"].to_numpy()


SCEN = {"null": {}, "gated_0.5": {"gate": -0.5}, "gated_1": {"gate": -1.0}, "gated_2": {"gate": -2.0},
        "heat_1": {"heat": -1.0}, "relation_1": {"rel": -1.0}, "relation_gated": {"rel": -1.0, "gate": -1.0}}


def s2_job(args):
    name, scen, rep = args
    d, win, clus, hu, O_any = native_frame(name)
    spk, tgt, N, _ = L.reindex(d["b_agent"].to_numpy(), d["a_agent"].to_numpy())
    R = d["R"].to_numpy().astype(float)
    O = d["O"].to_numpy().astype(float)
    p = SCEN[scen]
    extra = p.get("gate", 0) * R * O + p.get("heat", 0) * O_any + p.get("rel", 0) * R
    rng = np.random.default_rng(7919 * rep + hash(scen) % 1000 + len(name))
    y = L.simulate_labels(spk, tgt, d["block"].to_numpy(), N, rng, sd_u=0.5, extra=extra)
    res = L.did(y, spk, tgt, win, R, O, clus, B=200, rng=rng, heat_unit=hu)
    dec = L.decision(res)
    return {"native": name, "scen": scen, "rep": rep, **dec, "g_open": res["est"]["g_open"],
            "g_set": res["est"]["g_set"], "delta": res["est"]["delta"]}


def s2(workers=4, reps=100):
    jobs = [(n, s, k) for n in ("G12", "G26", "G23") for s in SCEN for k in range(reps)]
    t0 = time.time()
    with Pool(workers) as p:
        res = p.map(s2_job, jobs, chunksize=4)
    df = pl.DataFrame(res)
    summ = df.group_by("native", "scen").agg(
        pl.len().alias("reps"), pl.col("open_neg").mean(), pl.col("set_equiv").mean(), pl.col("delta_neg").mean(),
        pl.col("gated").mean(), pl.col("g_open").mean(), pl.col("g_set").mean(), pl.col("delta").mean()).sort("native",
                                                                                                               "scen")
    with pl.Config(tbl_rows=40, tbl_width_chars=200):
        print(summ)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "s2.json").write_text(json.dumps({"summary": summ.to_dicts(), "runtime_s": time.time() - t0}, indent=1))


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("s1", "all"):
        s1()
    if what in ("s2", "all"):
        s2()
