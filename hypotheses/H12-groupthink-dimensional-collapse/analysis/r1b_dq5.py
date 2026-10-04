"""H12 round 1b: the dimensionality and content arms on DQ5's embedding robustness pack (second model, statement flags).
None of the PR or content inputs depend on activity_bins, so these are robustness re-runs of round-1 statistics, not
corrections of them.

A. Self-repetition (DQ5: "mostly restatement"). Regime-III days with a valid PRday: share of chat statements flagged
   as exact self-repeats, bge self-repeats, gte self-repeats, copies (`self_repeat_both`), restatements (either model),
   and cross-agent echoes; Spearman with PRday (round-1 bge PRday and the gte PRday of B).
B. Second embedding model for the PR arm: PR30 / PRday per unit recomputed with the shared regime-whitened, unit-
   normalized 32-d vectors of bge (`statements_white32_bge_small`, same normalization as gte) and gte
   (`statements_white32_gte_modernbert`); P6 (kickoff first-hour change vs placebos), P7 (day 1 vs later days), P9
   (regime-I free vs shared weeks) and the regime-III loop periods re-scored under both; dedup variants that drop
   copies (`self_repeat_both`) or restatements (either model's flag).
C. Content modes (P4) with gte vectors (d = 32, kind-centered 30-min windows, cross-day edge), scored units.
Output: data/processed/H12-groupthink-dimensional-collapse/r1b/dq5/{dq5.json, prday_<model>[_<dedup>].parquet,
pr30_<model>[_<dedup>].parquet, selfrep_III.parquet, content_gte.parquet}.
Usage: uv run python hypotheses/H12-groupthink-dimensional-collapse/analysis/r1b_dq5.py [--workers 2]
"""
from __future__ import annotations

import json
import os
import sys
from multiprocessing import Pool
from pathlib import Path

os.environ.setdefault("H12_DATA_VERSION", "fixed")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import h12lib as L  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy.stats import binomtest, mannwhitneyu, spearmanr  # noqa: E402

import evaluate as EV  # noqa: E402
import run_units as R  # noqa: E402
from write_period_folders import FREE, SHARED  # noqa: E402

OUT = L.OUTV / "dq5"
MODELS = {"bge": "statements_white32_bge_small.npy", "gte": "statements_white32_gte_modernbert.npy"}
_G: dict = {}


def stmt_map() -> pl.DataFrame:
    """H12 stmt_index rows -> shared statements.parquet rows (srow) via (kind, agent, t, pt_date); asserts 1:1."""
    idx = pl.read_parquet(L.OUT / "stmt_index.parquet")
    st = (pl.read_parquet(L.SH / "embeddings/statements.parquet", columns=["kind", "agent", "t", "pt_date", "holdout"])
          .with_row_index("srow").filter(~pl.col("holdout")))
    m = idx.join(st.select("srow", "kind", "agent", "t", "pt_date"), on=["kind", "agent", "t", "pt_date"], how="left")
    dup = m.group_by("row").len().filter(pl.col("len") > 1)
    if dup.height:  # same agent, same timestamp, same kind: keep the first srow per row (ties are identical texts' rows)
        m = m.sort("row", "srow").unique("row", keep="first")
    assert m.height == idx.height and m["srow"].null_count() == 0, (m.height, idx.height, m["srow"].null_count())
    return m.sort("row")


def init(d):
    _G.update(d)


def pr_job(args):
    unit, model, dedup = args
    idx = _G["idx"].filter(pl.col("unit") == unit)
    if dedup == "copies":
        idx = idx.filter(~((pl.col("kind") == "chat") & pl.col("self_repeat_both")))
    elif dedup == "restatements":
        idx = idx.filter(~((pl.col("kind") == "chat") & pl.col("self_repeat_either")))
    Wv = np.load(L.SH / "embeddings" / MODELS[model], mmap_mode="r")
    rows = idx.with_columns(pl.col("srow").alias("row"))  # pr_unit reads Wv[row]; here row = shared statement row
    rng = np.random.default_rng([L.SEED, L.stable_seed([unit, "r1b", model, dedup])])
    a, b = R.pr_unit(unit, rows, Wv, rng)
    return unit, model, dedup, a, b


def content_job(args):
    unit, model = args
    ur = R.unit_row(unit)
    cal = pl.read_parquet(L.SH / "calendar.parquet").filter(pl.col("pt_date").is_in(ur["days"]))
    idx = _G["idx"].filter(pl.col("unit") == unit).with_columns(pl.col("srow").alias("row"))
    Wv = np.load(L.SH / "embeddings" / MODELS[model], mmap_mode="r")
    rng = np.random.default_rng([L.SEED, L.stable_seed([unit, "r1b-content", model])])
    r = R.rmt_content(unit, idx, Wv, cal, rng)
    return {"unit": unit, "model": model, "N": r.get("N"), "k_cd": r.get("k_cd"),
            "l1_edge": (r["eig"][0] / r["edge_cd"]) if r.get("eig") else None,
            "sign_share": r["modes"][0]["sign_share"] if r.get("eig") else None}


def score(p30, pday, units) -> dict:
    p30 = p30.join(units.select("unit", "goal_no", "regime", "mode"), on="unit")
    pday = pday.join(units.select("unit", "goal_no", "regime", "mode"), on="unit")
    kick, plac = EV.ne34(p30, units)
    out = {"P6": {"n": kick.height, "median_rel": float(kick["rel"].median()), "frac_neg": float((kick["d_pr"] < 0).mean()),
                  "p_mw_less": float(mannwhitneyu(kick["d_pr"], plac["d_pr"], alternative="less").pvalue),
                  "regIII_median_rel": float(kick.filter(pl.col("regime") == "III")["rel"].median())}}
    hi = lo = 0
    for g in sorted(set(units.filter(pl.col("N_catalog") >= 10)["goal_no"].to_list())):
        days_all = [d for dd in units.filter(pl.col("goal_no") == g).sort("unit")["days"].to_list() for d in dd]
        if len(days_all) < 3:
            continue
        x = pday.filter(pl.col("goal_no") == g)
        d1 = x.filter(pl.col("pt_date") == days_all[0])["prday"]
        later = x.filter(pl.col("pt_date") != days_all[0])["prday"].drop_nans()
        if len(d1) and d1[0] == d1[0] and len(later):
            hi += int(d1[0] > later.median()); lo += int(d1[0] < later.median())
    out["P7"] = {"day1_higher": hi, "day1_lower": lo, "p_two_sided": float(binomtest(hi, hi + lo, 0.5).pvalue) if hi + lo else None}
    pm = pday.group_by("goal_no").agg(pl.col("prday").drop_nans().mean())
    get = lambda g: pm.filter(pl.col("goal_no") == g)["prday"][0]  # noqa: E731
    fI = [get(g) for g in FREE["I"]]; sI = [get(g) for g in SHARED["I"]]
    out["P9"] = {"free_I": fI, "shared_I_median": float(np.median(sI)),
                 "p_exact": float(mannwhitneyu(fI, sI, alternative="greater", method="exact").pvalue)}
    r3 = {g: get(g) for g in (36, 37, 38, 39, 40, 41, 42, 44, 51)}
    loops = [r3[g] for g in (38, 39, 40) if r3[g] is not None and np.isfinite(r3[g])]
    others = [r3[g] for g in (37, 41, 42, 44, 51) if r3[g] is not None and np.isfinite(r3[g])]
    out["III_prday"] = {**{str(k): v for k, v in r3.items()}, "loops_max": float(max(loops)) if loops else None,
                        "others_min": float(min(others)) if others else None,
                        "loops_below_all_others": bool(loops and others and max(loops) < min(others)), "n_loop_periods_valid": len(loops)}
    return out


def main():
    workers = 2
    if "--workers" in sys.argv:
        workers = min(2, int(sys.argv[sys.argv.index("--workers") + 1]))
    OUT.mkdir(parents=True, exist_ok=True)
    m = stmt_map()
    fl = pl.read_parquet(L.SH / "statement_flags.parquet").select(
        "srow", "exact_self_repeat", "self_repeat_bge", "self_repeat_gte", "self_repeat_both", "cross_echo_bge", "cross_echo_gte",
        "cross_echo_both").with_columns(pl.col("srow").cast(pl.UInt32))
    idx = (m.join(fl, on="srow", how="left")
           .with_columns((pl.col("self_repeat_bge") | pl.col("self_repeat_gte")).alias("self_repeat_either"),
                         (pl.col("cross_echo_bge") | pl.col("cross_echo_gte")).alias("cross_echo_either")))
    units = pl.read_parquet(L.OUTV / "units.parquet")
    combos = [(mdl, dd) for mdl in MODELS for dd in ("none", "copies", "restatements")]
    tagof = lambda mdl, dd: mdl if dd == "none" else f"{mdl}_{dd}"  # noqa: E731
    todo = [c for c in combos if not (OUT / f"prday_{tagof(*c)}.parquet").exists()]  # cache: rerun only missing combos
    jobs = [(u, mdl, dd) for u in units["unit"].to_list() for (mdl, dd) in todo]
    res: dict = {}
    with Pool(workers, initializer=init, initargs=({"idx": idx},)) as pool:
        for unit, mdl, dd, a, b in pool.imap_unordered(pr_job, jobs):
            res.setdefault((mdl, dd), ([], []))
            res[(mdl, dd)][0].append(a); res[(mdl, dd)][1].append(b)
        for (mdl, dd), (a, b) in res.items():  # persist before scoring
            pl.concat(a, how="diagonal_relaxed").write_parquet(OUT / f"pr30_{tagof(mdl, dd)}.parquet")
            pl.concat(b, how="diagonal_relaxed").write_parquet(OUT / f"prday_{tagof(mdl, dd)}.parquet")
        sc = units.filter(pl.col("scored") & (pl.col("N_present") >= 6))["unit"].to_list()
        content = list(pool.imap_unordered(content_job, [(u, "gte") for u in sc]))
    D = {}
    pdays = {}
    for (mdl, dd) in combos:
        tag = tagof(mdl, dd)
        p30 = pl.read_parquet(OUT / f"pr30_{tag}.parquet"); pday = pl.read_parquet(OUT / f"prday_{tag}.parquet")
        D[tag] = score(p30, pday, units)
        pdays[tag] = pday.select("pt_date", pl.col("prday").alias(f"prday_{tag}"))
    # A. self-repetition vs PRday, regime-III days
    r1 = pl.concat([pl.read_parquet(f) for f in sorted(L.OUT.glob("G*/prday_*.parquet"))], how="diagonal_relaxed")
    r1 = r1.join(units.select("unit", "regime"), on="unit").filter(pl.col("regime") == "III").select("pt_date", pl.col("prday").alias("prday_r1"))
    ch = idx.filter(pl.col("kind") == "chat")
    share = ch.group_by("pt_date").agg(pl.len().alias("n_chat"),
                                       *[pl.col(c).cast(pl.Float64).mean().alias(c) for c in
                                         ("exact_self_repeat", "self_repeat_bge", "self_repeat_gte", "self_repeat_both", "self_repeat_either",
                                          "cross_echo_bge", "cross_echo_gte", "cross_echo_both", "cross_echo_either")])
    j = r1.join(share, on="pt_date").join(pdays["gte"], on="pt_date", how="left").join(pdays["bge"], on="pt_date", how="left")
    j = j.filter(pl.col("prday_r1").is_not_nan())
    j.write_parquet(OUT / "selfrep_III.parquet")
    A = {"n_days": j.height}
    for c in ("exact_self_repeat", "self_repeat_bge", "self_repeat_gte", "self_repeat_both", "self_repeat_either", "cross_echo_either"):
        A[c] = {"median_share": float(j[c].median()), "spearman_vs_prday_r1": float(spearmanr(j[c], j["prday_r1"]).statistic),
                "spearman_vs_prday_gte": float(spearmanr(j[c], j["prday_gte"], nan_policy="omit").statistic)}
    loops = ch.join(units.select("unit", "goal_no"), on="unit").filter(pl.col("goal_no").is_in([38, 39, 40]))
    A["loop_periods_share"] = (loops.group_by("goal_no").agg(*[pl.col(c).cast(pl.Float64).mean() for c in
                                                             ("exact_self_repeat", "self_repeat_bge", "self_repeat_gte",
                                                              "self_repeat_both", "self_repeat_either")]).sort("goal_no").to_dicts())
    # model agreement of PRday across days
    ag = pdays["bge"].join(pdays["gte"], on="pt_date").join(
        pl.concat([pl.read_parquet(f) for f in sorted(L.OUT.glob("G*/prday_*.parquet"))], how="diagonal_relaxed")
        .select("pt_date", pl.col("prday").alias("prday_r1")), on="pt_date")
    ag = ag.filter(pl.col("prday_bge").is_not_nan() & pl.col("prday_gte").is_not_nan() & pl.col("prday_r1").is_not_nan())
    B = {"n_days": ag.height, "spearman_bge_gte": float(spearmanr(ag["prday_bge"], ag["prday_gte"]).statistic),
         "spearman_r1_bge_shared": float(spearmanr(ag["prday_r1"], ag["prday_bge"]).statistic),
         "spearman_r1_gte": float(spearmanr(ag["prday_r1"], ag["prday_gte"]).statistic)}
    cg = pl.DataFrame(content)
    cg.write_parquet(OUT / "content_gte.parquet")
    r1c = pl.read_parquet(L.OUT / "unit_table.parquet").filter(pl.col("scored")).select("unit", "k_content", "content_l1_edge")
    cj = cg.join(r1c, on="unit", how="left")
    C = {"n_units": cg.height, "k_gte_dist": cg["k_cd"].value_counts().sort("k_cd").to_dicts(),
         "frac_k_ge1": float((cg["k_cd"] >= 1).mean()), "median_l1_edge_gte": float(cg["l1_edge"].median()),
         "median_l1_edge_bge_r1": float(cj["content_l1_edge"].median()),
         "spearman_l1edge_bge_gte": float(spearmanr(cj["l1_edge"], cj["content_l1_edge"], nan_policy="omit").statistic)}
    out = {"A_selfrep_III": A, "B_model_agreement_prday": B, "B_scores": D, "C_content_gte": C}
    (OUT / "dq5.json").write_text(json.dumps(out, indent=1, default=float))
    L.write_provenance("hypotheses/H12-groupthink-dimensional-collapse/analysis/r1b_dq5.py",
                       ["shared embeddings/statements.parquet, statements_white32_{bge_small,gte_modernbert}.npy, statement_flags.parquet; "
                        "H12 stmt_index, units, round-1 prday/unit_table"],
                       {"pr30": "chat, cap 8, n 30, 20 draws", "prday": "6 agents x 15 chat, 50 draws", "dedup": ["copies: self_repeat_both",
                                                                                                               "restatements: bge or gte flag"]},
                       path=L.OUTV / "_provenance.json")
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
