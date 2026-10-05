"""H69 round 2 on real data: R1 own tokens, R2 erasure dose and cap hits, R3 memory containment.

  uv run python hypotheses/H69-loops-context-fixed-points/analysis/run_r2.py [--B 300] [--procs 2]

Reads G<NN>/{statements,items,pairs,r2_tokens,r2_memory}.parquet (non-reserved; asserted) and synthetic/r2_worlds.parquet
(power). Writes G<NN>/results_r2.json and results_r2.json. Round-1 files are not touched.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import argparse  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "infra/shared"))
import h69lib as L  # noqa: E402
from common import holdout_mask  # noqa: E402

D = ROOT / "data/processed/H69-loops-context-fixed-points"
SH = ROOT / "data/processed/shared"
PERIODS = ["G36", "G37", "G38", "G39", "G40", "G41", "G42", "G44", "G51"]


def load(p):
    st = pl.read_parquet(D / p / "statements.parquet")
    assert not any(holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list())), f"{p}: reserved rows"
    it = pl.read_parquet(D / p / "items.parquet")
    m = json.loads((SH / "statement_flags_meta.json").read_text())
    tb, tg = m["thr_bge"], m["thr_gte_rate_matched"]
    pr = pl.read_parquet(D / p / "pairs.parquet").with_columns(
        (pl.col("cos_bge") > tb).alias("y_bge"), (pl.col("cos_gte") > tg).alias("y_gte")).with_columns(
        (pl.col("y_bge") | pl.col("y_gte")).alias("y"))
    tok = pl.read_parquet(D / p / "r2_tokens.parquet")
    mem = pl.read_parquet(D / p / "r2_memory.parquet")
    s, _ = L.prepare(st, it)
    s = L.attach_r2(s, tok)
    return s, pr, mem


def terms(o, *names):
    if not o:
        return None
    return {k: dict(b=o["terms"][k][0], se=o["terms"][k][1]) for k in names if k in o["terms"]} | dict(
        n=o["n"], n_y=o["n_y"])


def run_period(args):
    p, B = args
    t0 = time.time()
    s, pr, mem = load(p)
    res = dict(period=p)
    dense = s.filter(pl.col("dense").fill_null(False) & (pl.col("base_pos") == 0))
    allx = s.filter(pl.col("base_pos") <= 2)
    res["episodes_dense"] = L.episodes(dense, "r_either")
    res["episodes_all"] = L.episodes(allx, "r_either")
    ctl = ("o_ctx", "U_k", "k_ctx", "ctx_pos", "P")
    for name, d in (("dense", dense), ("all", allx)):
        res[f"r1_{name}"] = terms(L.r1_onset(d), *ctl)
        res[f"r1_{name}_noU"] = terms(L.r1_onset(d, with_U=False), *ctl)
        res[f"r1_{name}_logP"] = terms(L.r1_onset(d, fill="P"), *ctl)
    ex = L.r2_exit_dose(s)
    res["r2_exit_dose"] = (terms(ex, "forced_between", "vol_between", "dose_c")
                           | dict(n_erasure=ex["n_erasure"], dose_mean=ex["dose_mean"], dose_sd=ex["dose_sd"])) \
        if ex else None
    on = L.r2_onset_dose(s)
    res["r2_onset_dose"] = (terms(on, "erased", "dose_c") | dict(n_erasure=on["n_erasure"])) if on else None
    res["r2_cap"] = L.r2_cap_exit(s)
    if "terms" in res["r2_cap"]:
        res["r2_cap"]["terms"] = {k: dict(b=v[0], se=v[1]) for k, v in res["r2_cap"]["terms"].items()}
    q = L.r3_frame(pr, mem, s)
    e = q.filter(~pl.col("in_seg"))
    res["r3"] = L.r3_stats(e, "y", B=B, seed=11)
    res["r3_bge"] = L.r3_stats(e, "y_bge", B=B, seed=12)
    res["r3_gte"] = L.r3_stats(e, "y_gte", B=B, seed=13)
    res["r3_thr03"] = L.r3_stats(e, "y", thr=0.3, B=B, seed=14)
    res["r3_thr07"] = L.r3_stats(e, "y", thr=0.7, B=B, seed=15)
    res["r3_P3"] = L.r3_lowerbound(q, "y", B=B, seed=16)
    # descriptive memory dose: lines added between u and t (append rows), copies vs not, erased pairs
    ee = e.filter(pl.col("lines_added_between").is_not_null())
    if ee.height:
        res["r3_lines_added"] = dict(
            median_copy=float(ee.filter(pl.col("y"))["lines_added_between"].median() or float("nan")),
            median_nocopy=float(ee.filter(~pl.col("y"))["lines_added_between"].median() or float("nan")))
    res["secs"] = round(time.time() - t0, 1)
    (D / p / "results_r2.json").write_text(json.dumps(res, indent=1, default=float))
    print(p, "done", res["secs"], flush=True)
    return res


def get(o, path):
    for k in path:
        if o is None:
            return None
        o = o.get(k) if isinstance(o, dict) else None
    return o


def pool(per, scor, path_b, path_se=None, kind="se"):
    est, se, used = [], [], []
    for p in scor:
        o = per[p]
        if kind == "se":
            b, s_ = get(o, path_b + ["b"]), get(o, path_b + ["se"])
        else:  # bootstrap interval for a log OR
            b, s_ = get(o, path_b + ["log_or"]), get(o, path_b + ["se"])
        if b is not None and s_ is not None and np.isfinite(b) and np.isfinite(s_) and s_ > 0:
            est.append(b)
            se.append(s_)
            used.append(p)
    r = L.dl_pool(est, se)
    r["periods"] = used
    return r


def composition(p, thr=0.5):
    m = json.loads((SH / "statement_flags_meta.json").read_text())
    pr = pl.read_parquet(D / p / "pairs.parquet").filter(~pl.col("in_seg")).with_columns(
        ((pl.col("cos_bge") > m["thr_bge"]) | (pl.col("cos_gte") > m["thr_gte_rate_matched"])).alias("y"))
    e = pr.join(pl.read_parquet(D / p / "r2_memory.parquet"), on=["sid", "sid_u"]).filter(pl.col("c_t").is_not_nan())
    e = e.with_columns((pl.col("c_t") >= thr).alias("inm"), (pl.col("c_u").fill_nan(0) >= thr).alias("old"))
    out = {}
    for name, d in (("copies", e.filter(pl.col("y"))), ("pairs", e)):
        n = d.height
        out[name] = dict(n=n, in_mem=float(d["inm"].mean()) if n else None,
                         old_mem=float((d["inm"] & d["old"]).mean()) if n else None,
                         new_mem=float((d["inm"] & ~d["old"]).mean()) if n else None)
    return out


def _num(v, default):
    return default if v is None or not np.isfinite(v) else float(v)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--B", type=int, default=300)
    ap.add_argument("--procs", type=int, default=2)
    ap.add_argument("--pool-only", action="store_true", help="re-pool from existing G<NN>/results_r2.json")
    a = ap.parse_args()
    if a.pool_only:
        outs = [json.loads((D / p / "results_r2.json").read_text()) for p in PERIODS]
    else:
        with ProcessPoolExecutor(min(a.procs, 2)) as ex:
            outs = list(ex.map(run_period, [(p, a.B) for p in PERIODS]))
    per = {o["period"]: o for o in outs}
    syn = json.loads((D / "synthetic/r2_summary.json").read_text())
    pw = {(r["period"], r["world"]): r for r in syn}
    for p, o in per.items():
        o["scorable"] = dict(
            R1_dense=o["episodes_dense"]["n_episodes"] >= 30,
            R1_all=o["episodes_all"]["n_episodes"] >= 30,
            R1_power_dense=pw.get((p, "WU"), {}).get("R1_bU_dense"),
            R1_power_all=pw.get((p, "WU"), {}).get("R1_bU_all"),
            R2_power=pw.get((p, "WD"), {}).get("R2_exit_dose"),
            R3=((get(o, ["r3", "n_copies"]) or 0) >= 100) and (_num(pw.get((p, "M0"), {}).get("R3_P1"), 1.0) <= 0.10),
            R3_size=pw.get((p, "M0"), {}).get("R3_P1"),
            R3_power=pw.get((p, "M1"), {}).get("R3_P1"))
        (D / p / "results_r2.json").write_text(json.dumps(o, indent=1, default=float))
    r1d = [p for p in PERIODS if per[p]["scorable"]["R1_dense"]]
    r1a = [p for p in PERIODS if per[p]["scorable"]["R1_all"]]
    r1 = ["G38", "G40", "G41", "G51"]  # round-1 scorable set, for the exit-dose pool
    r3 = [p for p in PERIODS if per[p]["scorable"]["R3"]]
    pooled = dict(
        sets=dict(R1_dense=r1d, R1_all=r1a, R2=r1, R3=r3),
        R1_dense_bU=pool(per, r1d, ["r1_dense", "U_k"]), R1_dense_bO=pool(per, r1d, ["r1_dense", "o_ctx"]),
        R1_dense_fill=pool(per, r1d, ["r1_dense", "ctx_pos"]),
        R1_dense_noU_bO=pool(per, r1d, ["r1_dense_noU", "o_ctx"]),
        R1_dense_noU_fill=pool(per, r1d, ["r1_dense_noU", "ctx_pos"]),
        R1_dense_logP_bU=pool(per, r1d, ["r1_dense_logP", "U_k"]), R1_dense_logP_P=pool(per, r1d, ["r1_dense_logP", "P"]),
        R1_all_bU=pool(per, r1a, ["r1_all", "U_k"]), R1_all_bO=pool(per, r1a, ["r1_all", "o_ctx"]),
        R1_all_fill=pool(per, r1a, ["r1_all", "ctx_pos"]),
        R1_all_noU_bO=pool(per, r1a, ["r1_all_noU", "o_ctx"]), R1_all_noU_fill=pool(per, r1a, ["r1_all_noU", "ctx_pos"]),
        R1_all_logP_bU=pool(per, r1a, ["r1_all_logP", "U_k"]), R1_all_logP_P=pool(per, r1a, ["r1_all_logP", "P"]),
        R2_exit_dose=pool(per, r1, ["r2_exit_dose", "dose_c"]),
        R2_exit_forced=pool(per, r1, ["r2_exit_dose", "forced_between"]),
        R2_onset_dose=pool(per, r1, ["r2_onset_dose", "dose_c"]),
        R3_P1=pool(per, r3, ["r3", "P1"], kind="or"), R3_P2_new=pool(per, r3, ["r3", "P2_new"], kind="or"),
        R3_P2_strat=pool(per, r3, ["r3", "P2_strat"], kind="or"),
        R3_within_u=pool(per, r3, ["r3", "within_u"], kind="or"),
        R3_P1_bge=pool(per, r3, ["r3_bge", "P1"], kind="or"), R3_P1_gte=pool(per, r3, ["r3_gte", "P1"], kind="or"),
        R3_P1_thr03=pool(per, r3, ["r3_thr03", "P1"], kind="or"),
        R3_P1_thr07=pool(per, r3, ["r3_thr07", "P1"], kind="or"),
    )
    # P3: pooled difference of log ORs
    est, se, used = [], [], []
    for p in r3:
        o = per[p]["r3_P3"]
        if o and np.isfinite(o["diff"]) and np.isfinite(o["se"]) and o["se"] > 0:
            est.append(o["diff"])
            se.append(o["se"])
            used.append(p)
    pooled["R3_P3_diff"] = L.dl_pool(est, se) | dict(periods=used)
    for p in PERIODS:  # descriptive: where the erased sources of cross-erasure near-copies sit (memory before/after u)
        per[p]["r3_composition"] = composition(p)
        if p in ("G38", "G39", "G40", "G41", "G51"):  # POST HOC (labelled): erasure exit by memory status
            s_, _, mem_ = load(p)
            o = L.posthoc_exit_mem(s_, mem_)
            if "terms" in o:
                o["terms"] = {k: dict(b=v[0], se=v[1]) for k, v in o["terms"].items()}
            per[p]["posthoc_exit_mem"] = o
            (D / p / "results_r2.json").write_text(json.dumps(per[p], indent=1, default=float))
    pooled["POSTHOC_exit_erased"] = pool(per, r3, ["posthoc_exit_mem", "terms", "erased"])
    pooled["POSTHOC_exit_erased_inmem"] = pool(per, r3, ["posthoc_exit_mem", "terms", "erased_inmem"])
    out = dict(periods=per, pooled=pooled)
    (D / "results_r2.json").write_text(json.dumps(out, indent=1, default=float))
    for k, v in pooled.items():
        if k != "sets":
            print(k, {kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in v.items()
                      if kk in ("mean", "lo", "hi", "I2", "k", "periods")})
    print(pooled["sets"])


if __name__ == "__main__":
    main()
