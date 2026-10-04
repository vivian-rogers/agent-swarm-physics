"""H109 round-1 real-data run (non-holdout). Writes data/processed/H109-erasure-demagnetizing-pulse/results/.

Per model (bge_small primary, gte_modernbert) and dedupe variant (restate primary; none; copy):
  per period: delta_F (agent-day cluster bootstrap 1000; agent-cluster robustness 500), regression companion, delta_V,
  delta_K (kickoff alignment), R-fast split (primary only), first-statement window (k = 1)
  pooled: DerSimonian-Laird random-effects means over periods (NE41 native)
  recovery slopes (event fixed effects), pooled and per period
Variants (bge, restate): no agent constant; white32 vectors.
Usage: uv run python hypotheses/H109-erasure-demagnetizing-pulse/analysis/run.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h109lib as L  # noqa: E402

OUT = L.D / "results"


def first_only(b: pl.DataFrame) -> pl.DataFrame:
    return b.with_columns(pl.col("pre").list.tail(1), pl.col("post").list.head(1))


def period_block(b, st, a, bk, variant, reads, seed=0, rfast=False):
    ev = L.event_table(b, st, a, variant)
    evK = L.event_table(b, st, bk, variant)
    out = {}
    for P in L.PERIODS:
        e = ev.filter(pl.col("period") == P)
        eK = evK.filter(pl.col("period") == P)
        o = {"F": L.delta(e, "F", 1000, seed), "F_agent": L.delta(e, "F", 500, seed, cluster="agent"),
             "V": L.delta(e, "V", 500, seed), "K": L.delta(eK, "F", 500, seed), "reg": L.delta_reg(e),
             "n_events": {lab: int((e["label"] == lab).sum()) for lab in ("F", "V", "W", "O")}}
        out[P] = o
    if rfast:
        rr = reads.filter(pl.col("variant") == variant)
        R = np.full(st.height, np.nan)
        R[rr["sid"].to_numpy()] = rr["R"].to_numpy()
        for name, mask in (("R0", R == 0), ("Rpos", R > 0)):
            evm = L.event_table(b, st, a, variant, post_mask=mask)
            # W boundaries are unaffected by the mask only if their post statements pass it; keep W from the full table
            evm = pl.concat([evm.filter(pl.col("label") == "F"), ev.filter(pl.col("label") == "W")])
            for P in L.PERIODS:
                out[P][f"F_{name}"] = L.delta(evm.filter(pl.col("period") == P), "F", 300, seed)
            out.setdefault("pooled_rfast", {})[name] = L.delta(evm, "F", 300, seed)
    for key in ("F", "V", "K"):
        out[f"re_{key}"] = L.re_meta([out[P][key].get("delta", np.nan) for P in L.PERIODS],
                                     [out[P][key].get("delta_se", np.nan) for P in L.PERIODS])
    out["pooled_direct_F"] = L.delta(ev, "F", 1000, seed)
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    st, b, r = L.load_tables()
    res = {"info": {}, "models": {}}
    t0 = time.time()
    for model in L.MODELS:
        X = L.load_X(st, model)
        Xc = L.day_center(st, X)
        A = L.agent_constants(st, Xc)
        F = L.field_dirs(model)
        a, bk, info = L.axes_and_alignment(st, Xc, X, A, F)
        res["info"][model] = info
        mres = {}
        for variant in ("restate", "none", "copy"):
            mres[variant] = period_block(b, st, a, bk, variant, r, rfast=(variant == "restate"))
            print(model, variant, f"{time.time() - t0:.0f}s", flush=True)
        mres["restate_k1"] = period_block(first_only(b), st, a, bk, "restate", r)
        mres["recovery"] = {"pooled": L.recovery(b, r, st, a, "restate", nboot=1000)}
        for P in L.PERIODS:
            mres["recovery"][P] = L.recovery(b, r, st, a, "restate", periods=[P], nboot=500)
        mres["recovery_V"] = L.recovery(b.with_columns(pl.when(pl.col("label") == "V").then(pl.lit("F"))
                                                       .when(pl.col("label") == "F").then(pl.lit("x"))
                                                       .otherwise(pl.col("label")).alias("label")),
                                        r, st, a, "restate", nboot=500)
        # level of alignment overall (descriptive)
        sc = st["scoped"].to_numpy()
        gl = st["goal_no"].to_numpy()
        mres["level"] = {P: {"mean_a": float(np.nanmean(a[sc & (gl == P)])), "mean_b": float(np.nanmean(bk[sc & (gl == P)])),
                             "n": int(np.isfinite(a[sc & (gl == P)]).sum())} for P in L.PERIODS}
        if model == "bge_small":
            a0, _, _ = L.axes_and_alignment(st, Xc, X, A, F, use_const=False)
            mres["noconst"] = period_block(b, st, a0, bk, "restate", r)
            Xw = L.load_X(st, model, "white32")
            Xwc = L.day_center(st, Xw)
            Aw = L.agent_constants(st, Xwc)
            aw, bw, _ = L.axes_and_alignment(st, Xwc, Xw, Aw, F)
            mres["white32"] = period_block(b, st, aw, bw, "restate", r)
        res["models"][model] = mres
        print(model, "done", f"{time.time() - t0:.0f}s", flush=True)
    (OUT / "results.json").write_text(json.dumps(res, indent=1, default=lambda o: o if not isinstance(o, np.generic) else o.item()))
    for model in L.MODELS:
        m = res["models"][model]["restate"]
        print(model, "RE delta_F", m["re_F"], "RE delta_K", m["re_K"], "RE delta_V", m["re_V"])
        for P in L.PERIODS:
            f = m[P]["F"]
            print("  ", P, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in f.items()
                            if k in ("n", "delta", "delta_ci", "A_pre", "A_pre_ci", "coverage")})


if __name__ == "__main__":
    main()
