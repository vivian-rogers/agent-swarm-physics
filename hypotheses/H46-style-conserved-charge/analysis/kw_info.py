"""H46 Kolchinsky-Wolpert angle (O3): information that style vs content carry about the agent's next-day output.

V = log(1 + commits + API content writes + API MR/PR writes), DQ4 work_daily agent level (agent work: canonical,
not imported, agent-authored, not automated); periods #30 onward (dense ledger). Target: V on the agent's next
eligible day in the same unit. Predictors: agent-day means, two-way demeaned within the period. Ridge (GCV),
leave-one-day-out CV, I = -1/2 log2(1 - R2) bits; within-agent scramble null (200 permutations).
Identity channel: agent-mean predictors vs agent-mean V, leave-one-agent-out ridge R2, label permutation (500).
Output: data/processed/H46-style-conserved-charge/kw_info.json
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h46lib as L  # noqa: E402

PERIODS = [30, 31, 33, 35, 36, 37, 38, 39, 40, 41, 42, 44, 51]


def identity_channel(X, y, n_perm=500, seed=0):
    n = len(y)
    if n < 6:
        return {"n_agents": n}
    a = L.ridge_gcv(X - X.mean(0), y - y.mean())
    folds = np.arange(n)
    r2 = L.cv_r2(X, y, folds, a)
    rng = np.random.default_rng(seed)
    null = np.array([L.cv_r2(X, rng.permutation(y), folds, a) for _ in range(n_perm)])
    return {"n_agents": n, "r2_cv": r2, "p": float((1 + (null >= r2).sum()) / (1 + n_perm))}


def main():
    m = L.load_messages().filter(pl.col("goal_no") >= 30)
    mats = {"style": L.style_matrix(m, "tc"), "style_raw": L.style_matrix(m, "raw"), "content": L.content_matrix(m, "resid")}
    dt_ = L.day_table(m, mats)
    k = dt_.keys
    w = (pl.read_parquet(L.SH / "work_daily.parquet").filter((pl.col("level") == "agent") & ~pl.col("holdout"))
         .select("agent", "pt_date", (pl.col("commits").fill_null(0) + pl.col("api_content_writes").fill_null(0)
                                      + pl.col("api_mr_pr_writes").fill_null(0)).alias("out")))
    k = k.join(w, on=["agent", "pt_date"], how="left").with_columns(pl.col("out").fill_null(0))
    k = k.with_columns(pl.col("out").log1p().alias("V")).sort("row")
    k = k.with_columns(pl.col("V").shift(-1).over("agent", "unit2", order_by="pt_date").alias("V_next"))
    res = {"periods": {}}
    for g in PERIODS:
        kk = k.filter((pl.col("goal_no") == g) & pl.col("V_next").is_not_null())
        if kk.height < 20:
            continue
        rows = kk["row"].to_numpy()
        a = kk["agent"].to_numpy()
        d = kk["pt_date"].to_numpy()
        y = kk["V_next"].to_numpy()
        r = {"n": int(kk.height), "n_agents": int(len(np.unique(a))), "mean_out": float(kk["out"].mean()),
             "share_days_with_output": float((kk["out"] > 0).mean())}
        for ch in ("style", "style_raw", "content"):
            r[ch] = L.info_within(dt_.M[ch][rows], y, a, d, n_perm=200, seed=g)
        # identity channel: agent means over all the agent's eligible days in the period (V same day)
        ka = k.filter(pl.col("goal_no") == g)
        ag = np.unique(ka["agent"].to_numpy())
        if len(ag) >= 6:
            for ch in ("style", "content"):
                Xa = np.stack([dt_.M[ch][ka.filter(pl.col("agent") == x)["row"].to_numpy()].mean(0) for x in ag])
                ya = np.array([ka.filter(pl.col("agent") == x)["V"].mean() for x in ag])
                r[f"identity_{ch}"] = identity_channel(Xa, ya, seed=g)
        res["periods"][f"G{g:02d}"] = r
        print(g, r["n"], {ch: (round(r[ch].get("r2_cv", np.nan), 4), r[ch].get("p")) for ch in ("style", "style_raw", "content")},
              {c: (round(r.get(f"identity_{c}", {}).get("r2_cv", np.nan), 3), r.get(f"identity_{c}", {}).get("p"))
               for c in ("style", "content")}, flush=True)
    pooled = {}
    for ch in ("style", "style_raw", "content"):
        ps = [v[ch]["p"] for v in res["periods"].values() if "p" in v[ch]]
        ns = [v[ch]["n"] for v in res["periods"].values() if "p" in v[ch]]
        bs = [v[ch]["bits"] for v in res["periods"].values() if "p" in v[ch]]
        z = stats.norm.isf(np.clip(ps, 1e-6, 1 - 1e-6))
        pooled[ch] = {"n_periods": len(ps), "n_sig": int(sum(p < 0.05 for p in ps)),
                      "stouffer_p": float(stats.norm.sf(z.sum() / np.sqrt(len(z)))),
                      "bits_weighted": float(np.average(bs, weights=ns)), "bits_median": float(np.median(bs))}
    for ch in ("style", "content"):
        vals = [v[f"identity_{ch}"] for v in res["periods"].values() if f"identity_{ch}" in v and "p" in v[f"identity_{ch}"]]
        pooled[f"identity_{ch}"] = {"n_periods": len(vals), "n_r2_pos": int(sum(x["r2_cv"] > 0 for x in vals)),
                                    "n_sig": int(sum(x["p"] < 0.05 for x in vals)),
                                    "median_r2": float(np.median([x["r2_cv"] for x in vals])) if vals else None}
    res["pooled"] = pooled
    print(json.dumps(pooled, indent=1))
    (L.DATA / "kw_info.json").write_text(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
