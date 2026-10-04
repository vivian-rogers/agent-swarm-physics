"""H56 post hoc layer (after the pre-registered replication run; labelled as such in the card).

Amendment 3 (procedural repair): the pre-registered N1 placebo rule leaves 35 placebo days (the changelog makes the
catalog dense), so the smallest attainable per-event p was 0.11 and per-event "hits" were impossible. Per-event p-values
are recomputed against N2 pools (eligible days of the regime > 2 days from every event of the same class, weekday-
matched when >= 20 such days).
Post hoc statistics (not pre-registered): M = median_i |Delta_i| / median level (direction-free magnitude) and
S = |f+ - 0.5| (sign synchrony), with the same class-level random-date null; a weekday profile of |t|; the real
null spread vs the synthetic stationary null; Holm over the six pre-specified primaries.
Run: OMP_NUM_THREADS=2 uv run python hypotheses/H56-ep-platform-fingerprint/analysis/posthoc.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import event_study as ES  # noqa: E402
import h56lib as L  # noqa: E402

REP = L.OUTROOT / "replication"


def magnitude_table():
    ta = pl.read_parquet(REP / "tday_agent.parquet").with_columns(
        (pl.col("post") - pl.col("pre")).abs().alias("ad"), ((pl.col("post") + pl.col("pre")) / 2).alias("lev"))
    m = ta.group_by("nidx", "variant").agg((pl.col("ad").median() / pl.col("lev").median().clip(1e-4)).alias("M"))
    return m


def class_null(es, tday, col, v, cls, rng, n_draw=5000, absval=True):
    ee = es.filter((pl.col("variant") == v) & (pl.col("cls") == cls) & pl.col(col).is_not_nan())
    if ee.height == 0:
        return None
    f = (lambda x: np.abs(x)) if absval else (lambda x: x)
    obs = float(np.mean(f(ee[col].to_numpy())))
    cls_days = es.filter(pl.col("cls") == cls)["nidx"].to_list()
    tv = tday.filter((pl.col("variant") == v) & pl.col(col).is_not_nan())
    pools = [f(tv.filter((pl.col("regime") == r) & ~pl.col("nidx").is_in(cls_days))[col].to_numpy()) for r in ee["regime"].to_list()]
    draws = np.array([np.mean([p[rng.integers(len(p))] for p in pools]) for _ in range(n_draw)])
    return {"n": ee.height, "mean": obs, "null_mean": float(draws.mean()), "p": float((1 + (draws >= obs).sum()) / (1 + n_draw))}


def main():
    rng = np.random.default_rng(20261006)
    es = pl.read_parquet(REP / "events.parquet")
    tday = pl.read_parquet(REP / "tday.parquet")
    M = magnitude_table()
    tday = tday.join(M, on=["nidx", "variant"], how="left").with_columns((pl.col("newton_fpos") - 0.5).abs().alias("S"))
    es = es.join(M, on=["nidx", "variant"], how="left").with_columns((pl.col("newton_fpos") - 0.5).abs().alias("S"))
    # Amendment 3 per-event p-values
    p3, kinds, npool = [], [], []
    for r in es.iter_rows(named=True):
        t = r.get("newton_t")
        if r["cls"] == "scaffold_family" or t is None or not np.isfinite(t):
            p3.append(r.get("p_placebo")); kinds.append(r.get("null_kind")); npool.append(r.get("n_placebo"))
            continue
        excl = es.filter(pl.col("cls") == r["cls"])["nidx"].unique().to_list()
        pool, kind = ES.n2_pool(tday, r["variant"], r["regime"], r["weekday"], excl)
        p3.append(float((1 + (pool >= abs(t)).sum()) / (1 + len(pool))) if len(pool) else np.nan)
        kinds.append(kind); npool.append(len(pool))
    es = es.with_columns(pl.Series("p_n2", p3, dtype=pl.Float64), pl.Series("null_n2", kinds, dtype=pl.Utf8),
                         pl.Series("n_n2", npool, dtype=pl.Int64))
    es.write_parquet(REP / "events_posthoc.parquet", compression="zstd")
    out = {"amendment3_hits": {}, "magnitude": {}, "sign": {}, "weekday_abs_t": {}, "null_spread": {}}
    for v in L.VARIANTS:
        out["amendment3_hits"][v] = {}
        for cls in ES.TESTED:
            ee = es.filter((pl.col("variant") == v) & (pl.col("cls") == cls) & pl.col("p_n2").is_not_nan())
            if ee.height:
                out["amendment3_hits"][v][cls] = {"n": ee.height, "hit_rate": float((ee["p_n2"] < 0.05).mean()),
                                                  "hits": ee.filter(pl.col("p_n2") < 0.05)["refs"].to_list(),
                                                  "median_pool": float(np.median(ee["n_n2"].to_numpy()))}
        out["magnitude"][v] = {c: class_null(es, tday, "M", v, c, rng) for c in ES.TESTED if c != "scaffold_family"}
        out["sign"][v] = {c: class_null(es, tday, "S", v, c, rng) for c in ES.TESTED if c != "scaffold_family"}
        tv = tday.filter((pl.col("variant") == v) & pl.col("newton_t").is_not_nan())
        out["weekday_abs_t"][v] = {int(w): {"n": int(n), "mean_abs_t": float(m)} for w, n, m in
                                   tv.group_by("weekday").agg(pl.len(), pl.col("newton_t").abs().mean()).sort("weekday").iter_rows()}
        out["null_spread"][v] = {"sd_t_all_days": float(tv["newton_t"].std()), "q95_abs_t": float(np.percentile(np.abs(tv["newton_t"].to_numpy()), 95)),
                                 "share_abs_t_gt_2.25": float((tv["newton_t"].abs() > 2.25).mean())}
    syn_path = L.OUTROOT / "synthetic/summary.json"
    if not syn_path.exists() and L.EP == "xprod":   # verify runs: the round-1 synthetic is the legacy one
        syn_path = L.DATA / "synthetic/summary.json"
    syn = json.loads(syn_path.read_text())
    out["null_spread"]["synthetic_fine_null_sd_t"] = syn["fine"]["null_t_sd"]["newton"]
    out["null_spread"]["synthetic_fine_tau95"] = syn["fine"]["tau95"]["newton"]
    # NE14b and NE18/NE40 magnitude percentiles
    for ref in ("NE14b", "CL:2026-04-20"):
        for v in ("act_all", "act_agent_b3", "coarse_all"):
            r = es.filter((pl.col("ref") == ref) & (pl.col("variant") == v))
            if r.height:
                reg = r["regime"][0]
                pool = tday.filter((pl.col("variant") == v) & (pl.col("regime") == reg))["M"].drop_nulls().to_numpy()
                out.setdefault("event_magnitude", {})[f"{ref}:{v}"] = {
                    "M": float(r["M"][0]) if r["M"][0] is not None else None,
                    "pct_in_regime": float((pool < r["M"][0]).mean()) if r["M"][0] is not None else None,
                    "t": float(r["newton_t"][0]), "fpos": float(r["newton_fpos"][0]), "p_n2": r["p_n2"][0]}
    # Holm over the six pre-specified primaries (p for the effect H56 predicts; absence claims noted)
    res = json.loads((REP / "results.json").read_text())
    nat = {k: json.loads((L.OUTROOT / f"native/{k}.json").read_text()) for k in ("NE14", "NE43")}
    prim = {"P1 scaffold_tool V1 (N2 class)": res["class_tests"]["act_all"]["scaffold_tool:all"]["p_random_date"],
            "P2 goal V1 jump (N2 class; H56 predicts none)": res["class_tests"]["act_all"]["goal:all"]["p_random_date"],
            "P4 scaffold enrichment V1": res["blind"]["act_all"]["classes"]["scaffold_tool"]["p"],
            "P6b family on V5 (H56 predicts p > 0.05)": res["families"]["act_agent_b3"]["p_stratified"],
            "P7 NE43 V1 k3 jump (H56 predicts none)": nat["NE43"]["designs"]["k3"]["act_all"]["p_friday_placebo"],
            "P8 NE14b V1 (Tuesday N2)": nat["NE14"]["variants"]["act_all"]["p_tuesday_placebo"]}
    ks = sorted(prim, key=lambda k: prim[k])
    holm, run = {}, 0.0
    for i, k in enumerate(ks):
        run = max(run, min(1.0, (len(ks) - i) * prim[k]))
        holm[k] = {"p": prim[k], "holm": run}
    out["holm_primaries"] = holm
    (REP / "posthoc.json").write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps(out, indent=1, default=str)[:6000])


if __name__ == "__main__":
    main()
