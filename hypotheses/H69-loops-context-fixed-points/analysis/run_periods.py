"""H69 round 1 on real data: onset, exit, in-context enrichment, natives (NE41, G38, G51).

  uv run python hypotheses/H69-loops-context-fixed-points/analysis/run_periods.py [--B 300]

Reads data/processed/H69-loops-context-fixed-points/G<NN>/{statements,items,pairs}.parquet (non-holdout; asserted)
and synthetic/summary.json (scorable rule). Writes G<NN>/results.json, results.json and per_period_estimates rows.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import argparse  # noqa: E402
import json  # noqa: E402
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


def thresholds():
    m = json.loads((SH / "statement_flags_meta.json").read_text())
    return m["thr_bge"], m["thr_gte_rate_matched"]


def load(p):
    st = pl.read_parquet(D / p / "statements.parquet")
    assert not any(holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list())), f"{p}: held-out statements"
    it = pl.read_parquet(D / p / "items.parquet")
    pr = pl.read_parquet(D / p / "pairs.parquet")
    tb, tg = thresholds()
    pr = pr.with_columns((pl.col("cos_bge") > tb).alias("y_bge"), (pl.col("cos_gte") > tg).alias("y_gte")).with_columns(
        (pl.col("y_bge") | pl.col("y_gte")).alias("y"), (pl.col("y_bge") & pl.col("y_gte")).alias("y_both"))
    return st, it, pr


def run_period(args):
    p, B = args
    t0 = time.time()
    st, it, pr = load(p)
    res = dict(period=p)
    s, thr = L.prepare(st, it, resp="r_either", nov="nov_bge")
    res["nov_thr_bge"] = thr
    res["episodes"] = {r: L.episodes(L.prepare(st, None, resp=r)[0], r) for r in ("r_either", "r_bge", "r_gte", "r_both")}
    res["onset"] = L.onset(s, "r_either")
    res["onset_chars"] = L.onset(s, "r_either", share="s_chars")
    res["onset_copy"] = L.onset(L.prepare(st, it, resp="r_both")[0], "r_both")
    # onset with an erasure indicator (NE41: first statement after a forced erasure)
    d0 = s.filter(pl.col("r_prev") == 0)
    if d0.height >= 50 and d0["r_either"].sum() >= 10:
        y = d0["r_either"].to_numpy().astype(float)
        ag = np.unique(d0["agent"].to_numpy(), return_inverse=True)[1]
        X = L._X(d0, ["forced_between", "log1p:n_prev_day", "log:lag_prev_s", "log:calls_prev", "log1p:n_read"])
        if X[:, 0].std() > 0:
            r = L.fit_logit(y, X, ag, clusters=d0["aday"].to_list())
            res["onset_forced"] = dict(b=float(r["b"][0]), se=float(r["se_cl"][0]), n=int(len(y)),
                                       n_forced=int(X[:, 0].sum()))
    res["exit"] = L.exit_model(s, "r_either")
    res["exit_s"] = L.exit_model(s, "r_either", include_s=True)
    sg, _ = L.prepare(st, it, resp="r_either", nov="nov_gte")
    res["exit_gte_nov"] = L.exit_model(sg, "r_either")
    if p == "G51":
        res["exit_kicks"] = L.exit_model(s, "r_either", extra=("read_nudge", "read_human", "infl_nudge", "infl_human",
                                                                "nov_read"))
    nt = st.filter(~pl.col("templated").fill_null(False) & ~pl.col("cross_echo").fill_null(False))
    snt, _ = L.prepare(nt, it, resp="r_either")
    res["onset_notempl"] = L.onset(snt, "r_either")
    res["exit_notempl"] = L.exit_model(snt, "r_either")
    res["enrich"] = L.enrichment(pr, s, "y", B=B, seed=1)
    res["enrich_bge"] = L.enrichment(pr, s, "y_bge", B=B, seed=2)
    res["enrich_gte"] = L.enrichment(pr, s, "y_gte", B=B, seed=3)
    res["enrich_both"] = L.enrichment(pr, s, "y_both", B=B, seed=4)
    res["enrich_forced"] = L.enrichment(pr, s, "y", B=B, seed=5, restrict=pl.col("in_seg") | pl.col("forced_between"))
    res["pseudo"] = L.enrichment(pr, s, "y", B=B, seed=6, exposure="same_half", restrict=pl.col("in_seg"))
    res["secs"] = round(time.time() - t0, 1)
    (D / p / "results.json").write_text(json.dumps(res, indent=1, default=float))
    print(p, "done", res["secs"], flush=True)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--B", type=int, default=300)
    ap.add_argument("--procs", type=int, default=2)
    a = ap.parse_args()
    with ProcessPoolExecutor(a.procs) as ex:
        outs = list(ex.map(run_period, [(p, a.B) for p in PERIODS]))
    per = {o["period"]: o for o in outs}
    syn = json.loads((D / "synthetic/summary.json").read_text())
    pw = {(r["period"], r["world"]): r for r in syn}
    pooled = {}
    for p, o in per.items():
        z1 = pw.get((p, "Z1"), {})
        o["scorable"] = dict(
            episodes=o["episodes"]["r_either"]["n_episodes"] >= 30,
            P1=(z1.get("P1_bs_pos") or 0) >= 0.8, P3=(z1.get("P3_forced") or 0) >= 0.8,
            P4=(z1.get("P4_lor_pos") or 0) >= 0.8, P5=(z1.get("P5_read") or 0) >= 0.8)

    def pool(key, bkey, sekey, cond):
        est, se, ps = [], [], []
        for p, o in per.items():
            r = o.get(key)
            if r and cond(o) and np.isfinite(r.get(bkey, np.nan)) and np.isfinite(r.get(sekey, np.nan)):
                est.append(r[bkey])
                se.append(r[sekey])
                ps.append(p)
        out = L.dl_pool(est, se)
        out["periods"] = ps
        return out
    ok = lambda o: o["scorable"]["episodes"]  # noqa: E731
    pooled["b_s"] = pool("onset", "b_s", "se_s", ok)
    pooled["b_O"] = pool("onset", "b_O", "se_O", ok)
    pooled["b_K"] = pool("onset", "b_K", "se_K", ok)
    pooled["b_s_chars"] = pool("onset_chars", "b_s", "se_s", ok)
    pooled["exit_forced"] = pool("exit", "b_forced_between", "se_forced_between", ok)
    pooled["exit_vol"] = pool("exit", "b_vol_between", "se_vol_between", ok)
    pooled["exit_nov_read"] = pool("exit", "b_nov_read", "se_nov_read", ok)
    pooled["exit_nov_infl"] = pool("exit", "b_nov_infl", "se_nov_infl", ok)
    pooled["exit_nov_next"] = pool("exit", "b_nov_read_next", "se_nov_read_next", ok)
    pooled["exit_s_forced"] = pool("exit_s", "b_forced_between", "se_forced_between", ok)
    pooled["onset_forced"] = pool("onset_forced", "b", "se", ok)
    for k in ("enrich", "enrich_bge", "enrich_gte", "enrich_both", "enrich_forced", "pseudo"):
        pooled[k] = pool(k, "log_or", "se", ok)
    dAIC = {p: (o["onset"] or {}).get("dAIC_hinge") for p, o in per.items()}
    sstar = {p: (o["onset"] or {}).get("s_star") for p, o in per.items()}
    res = dict(periods=per, pooled=pooled, dAIC_hinge=dAIC, s_star=sstar,
               dAIC_hinge_sum=float(np.nansum([v for p, v in dAIC.items() if v is not None and ok(per[p])])))
    (D / "results.json").write_text(json.dumps(res, indent=1, default=float))
    for k, v in pooled.items():
        print(k, {kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in v.items()})
    print("dAIC hinge", dAIC, "s*", sstar)


if __name__ == "__main__":
    main()
