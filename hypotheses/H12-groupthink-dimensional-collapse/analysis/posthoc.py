"""H12 post hoc diagnostics (run AFTER evaluate.py; none of these enter a verdict). Non-holdout only.

1. Content overlap with per-agent-DAY centering: is the content mode window-level co-movement (survives) or day-level
   topic drift shared by all agents (vanishes)?
2. Lull stratification: k after the lull filter vs the unit's joint-lull fraction (the filter loses power when lulls
   are long and frequent; synthetic A5).
3. Direction test for P7 (two-sided sign test of PRday day 1 vs later days) and the NE34 contrast by regime.
4. Message templating check for low-PR periods: share of near-duplicate chat statements per day (cosine > 0.95 in raw
   embedding space to another statement of the same day), vs PRday.

Writes posthoc.json and posthoc_units.parquet.
Usage: uv run python hypotheses/H12-groupthink-dimensional-collapse/analysis/posthoc.py
"""
from __future__ import annotations

import json

import h12lib as L
import numpy as np
import polars as pl
from scipy.stats import binomtest, spearmanr

import run_units as R


def content_day_centered(unit, rng):
    ur = R.unit_row(unit)
    cal = pl.read_parquet(L.SH / "calendar.parquet").filter(pl.col("pt_date").is_in(ur["days"]))
    idx = pl.read_parquet(L.OUT / "stmt_index.parquet").filter(pl.col("unit") == unit)
    Wv = np.load(L.OUT / "stmt_white_d64.npy", mmap_mode="r")
    days, agents = R.content_days(unit, idx, Wv, cal)
    out = []
    for A in days:  # subtract each agent's mean over its present windows of the day
        pres = np.abs(A).sum(2) > 0
        mu = A.sum(1) / np.maximum(pres.sum(1), 1)[:, None]
        out.append(np.where(pres[:, :, None], A - mu[:, None, :], 0.0))
    cd = L.spectrum_test(out, 200, rng, "content", "crossday")
    return {"k_dc": cd["k"], "l1_edge_dc": float(cd["eig"][0] / cd["edge"])}


def near_dup_share(pday_dates):
    idx = pl.read_parquet(L.OUT / "stmt_index.parquet").filter((pl.col("kind") == "chat") & pl.col("pt_date").is_in(pday_dates))
    E = np.load(L.SH / "embeddings/chat_bge_small.npy", mmap_mode="r")
    st = pl.read_parquet(L.SH / "embeddings/statements.parquet").with_row_index("srow")
    # stmt_index rows follow statements.parquet filtered to non-holdout; recover src_row via the join on (kind, agent, t)
    key = st.filter(pl.col("kind") == "chat").select("agent", "t", "src_row")
    idx = idx.join(key, on=["agent", "t"], how="left").unique(["row"])
    res = []
    for d in pday_dates:
        x = idx.filter(pl.col("pt_date") == d)
        if x.height < 20:
            continue
        V = np.asarray(E[x["src_row"].to_numpy()], dtype=np.float32)
        S = V @ V.T
        np.fill_diagonal(S, 0)
        a = x["agent"].to_numpy(); same = a[:, None] == a[None, :]
        res.append({"pt_date": d, "n": x.height, "dup_share": float((S.max(1) > 0.95).mean()),
                    "dup_within": float((np.where(same, S, 0).max(1) > 0.95).mean()),
                    "dup_cross": float((np.where(~same, S, 0).max(1) > 0.95).mean())})
    return pl.DataFrame(res)


def main():
    ut = pl.read_parquet(L.OUT / "unit_table.parquet")
    sc = ut.filter(pl.col("scored"))
    rows = []
    for u in sc["unit"].to_list():
        rng = np.random.default_rng([L.SEED, L.stable_seed([u, "posthoc"])])
        rows.append({"unit": u, **content_day_centered(u, rng)})
    dc = pl.DataFrame(rows)
    pu = sc.join(dc, on="unit")
    P = {}
    P["content_day_centered"] = {"k_dc_dist": pu["k_dc"].value_counts().sort("k_dc").to_dicts(),
                                 "median_l1_edge_dc": float(pu["l1_edge_dc"].median()),
                                 "median_l1_edge_raw": float(pu["content_l1_edge"].median())}
    lo = pu.filter((pl.col("lull_frac") <= 0.10) & (pl.col("k_cd") >= 1))
    hi = pu.filter((pl.col("lull_frac") > 0.10) & (pl.col("k_cd") >= 1))
    P["lull_strata"] = {"low_lull_units": lo.height, "low_lull_k_lull_ge1": lo.filter(pl.col("k_lull") >= 1).height,
                        "high_lull_units": hi.height, "high_lull_k_lull_ge1": hi.filter(pl.col("k_lull") >= 1).height,
                        "spearman_lullfrac_vs_lulldrop": float(spearmanr(pu["lull_frac"], pu["lull_drop"]).statistic)}
    p7 = pl.read_parquet(L.OUT / "p7_day1.parquet").filter((pl.col("N") >= 10) & pl.col("prday_d1").is_not_nan() & pl.col("prday_later_med").is_not_nan())
    nh = int((~p7["d1_lower"]).sum())
    P["P7_direction"] = {"n": p7.height, "day1_higher": nh, "p_two_sided": float(binomtest(nh, p7.height, 0.5).pvalue)}
    p7a = pl.read_parquet(L.OUT / "p7_day1.parquet").filter(pl.col("prday_d1").is_not_nan() & pl.col("prday_later_med").is_not_nan())
    nha = int((~p7a["d1_lower"]).sum())
    P["P7_direction_all_N"] = {"n": p7a.height, "day1_higher": nha, "p_two_sided": float(binomtest(nha, p7a.height, 0.5).pvalue)}
    k = pl.read_parquet(L.OUT / "ne34_kickoffs.parquet")
    P["NE34_by_regime"] = k.group_by("regime").agg(pl.len(), pl.col("rel").median(), (pl.col("d_pr") > 0).sum().alias("n_up")).sort("regime").to_dicts()
    # templating check on regime-III scored units
    pday = pl.concat([pl.read_parquet(f) for f in sorted(L.OUT.glob("G*/prday_*.parquet"))], how="diagonal_relaxed")
    r3 = pday.join(pl.read_parquet(L.OUT / "units.parquet").select("unit", "regime"), on="unit").filter(pl.col("regime") == "III")
    nd = near_dup_share(r3["pt_date"].to_list())
    j = r3.join(nd, on="pt_date").filter(pl.col("prday").is_not_nan())
    P["templating_III"] = {"n_days": j.height, "spearman_dup_vs_prday": float(spearmanr(j["dup_share"], j["prday"]).statistic),
                           "spearman_within_vs_prday": float(spearmanr(j["dup_within"], j["prday"]).statistic),
                           "spearman_cross_vs_prday": float(spearmanr(j["dup_cross"], j["prday"]).statistic),
                           "median_dup_share": float(j["dup_share"].median()), "median_within": float(j["dup_within"].median()),
                           "median_cross": float(j["dup_cross"].median())}
    j.write_parquet(L.OUT / "posthoc_templating.parquet")
    pu.write_parquet(L.OUT / "posthoc_units.parquet")
    (L.OUT / "posthoc.json").write_text(json.dumps(P, indent=1, default=float))
    L.write_provenance("hypotheses/H12-groupthink-dimensional-collapse/analysis/posthoc.py",
                       ["H12 unit_table, p7_day1, ne34_kickoffs, prday_*; shared embeddings/chat_bge_small.npy, statements"],
                       {"post_hoc": True, "near_dup_cos": 0.95, "outputs": "posthoc.json, posthoc_units, posthoc_templating, posthoc_dedup.json, G*/pr*dedup_*"})
    print(json.dumps(P, indent=1, default=float))


if __name__ == "__main__" and __import__("sys").argv[1:] != ["dedup"]:
    main()


# ------------------------------------------------------------------------------------------------ dedup variant
def dedup_rows(idx_unit: pl.DataFrame) -> pl.DataFrame:
    """Drop chat statements whose raw-embedding cosine to an EARLIER chat statement by the same agent on the same day
    exceeds 0.95 (self-repetition / loops). Intentions are kept unchanged."""
    E = np.load(L.SH / "embeddings/chat_bge_small.npy", mmap_mode="r")
    key = pl.read_parquet(L.SH / "embeddings/statements.parquet").filter(pl.col("kind") == "chat").select("agent", "t", "src_row")
    ch = idx_unit.filter(pl.col("kind") == "chat").join(key, on=["agent", "t"], how="left").sort("t")
    drop = []
    for (a, d), g in ch.group_by(["agent", "pt_date"]):
        V = np.asarray(E[g["src_row"].to_numpy()], dtype=np.float32)
        S = np.tril(V @ V.T, -1)
        drop += g["row"].filter(pl.Series(S.max(1) > 0.95)).to_list() if len(g) > 1 else []
    return idx_unit.filter(~pl.col("row").is_in(drop))


def dedup_main():
    import evaluate as EV
    from scipy.stats import mannwhitneyu
    units = pl.read_parquet(L.OUT / "units.parquet")
    Wv = np.load(L.OUT / "stmt_white_d64.npy", mmap_mode="r")
    p30s, pdays, nd = [], [], []
    for u in units["unit"].to_list():
        idx = pl.read_parquet(L.OUT / "stmt_index.parquet").filter(pl.col("unit") == u)
        idd = dedup_rows(idx)
        nd.append({"unit": u, "n_chat": idx.filter(pl.col("kind") == "chat").height, "n_chat_dedup": idd.filter(pl.col("kind") == "chat").height})
        rng = np.random.default_rng([L.SEED, L.stable_seed([u, "dedup"])])
        a, b = R.pr_unit(u, idd, Wv, rng)
        g = int(u.rstrip("abcdefgh"))
        a.write_parquet(L.OUT / f"G{g:02d}" / f"pr30dedup_{u}.parquet"); b.write_parquet(L.OUT / f"G{g:02d}" / f"prdaydedup_{u}.parquet")
        p30s.append(a); pdays.append(b)
    p30 = pl.concat(p30s, how="diagonal_relaxed").join(units.select("unit", "goal_no", "regime", "mode"), on="unit")
    pday = pl.concat(pdays, how="diagonal_relaxed").join(units.select("unit", "goal_no", "regime", "mode"), on="unit")
    kick, plac = EV.ne34(p30, units)
    out = {"dedup_counts": pl.DataFrame(nd).select(pl.col("n_chat").sum(), pl.col("n_chat_dedup").sum()).to_dicts()[0]}
    out["P6_dedup"] = {"n": kick.height, "median_rel": float(kick["rel"].median()), "frac_neg": float((kick["d_pr"] < 0).mean()),
                       "p_mw": float(mannwhitneyu(kick["d_pr"], plac["d_pr"], alternative="less").pvalue),
                       "by_regime": kick.group_by("regime").agg(pl.len(), pl.col("rel").median()).sort("regime").to_dicts()}
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
    out["P7_dedup"] = {"day1_higher": hi, "day1_lower": lo, "p_two_sided": float(binomtest(hi, hi + lo, 0.5).pvalue)}
    pm = pday.group_by("goal_no").agg(pl.col("prday").drop_nans().mean())
    get = lambda g: pm.filter(pl.col("goal_no") == g)["prday"][0]  # noqa: E731
    fI = [get(g) for g in [11, 16, 31]]; sI = [get(g) for g in [13, 18, 19, 24, 25, 26, 30]]
    out["P9_dedup"] = {"free_I": fI, "shared_I_median": float(np.median(sI)),
                       "p_exact": float(mannwhitneyu(fI, sI, alternative="greater", method="exact").pvalue),
                       "III": {"37": get(37), "38": get(38), "40": get(40), "44": get(44), "39": get(39)}}
    (L.OUT / "posthoc_dedup.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__" and __import__("sys").argv[1:] == ["dedup"]:
    dedup_main()
