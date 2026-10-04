"""DQ2 validation and compile steps for reply threading (called from reply_threading.py; design in
infra/data-quality/reply_threading.md).

val_sample(which)  writes a blind labelling sheet (message text, no Jev answers, no strata) to
                   data/processed/shared/reply_threading/validation/ (gitignored); the key goes to a separate file.
validate()         kappa, agreement by confidence, per-class precision, placebo checks, ground-truth checks, H37 agreement.
compile_tables()   reply_pairs.parquet and reply_graph.parquet in data/processed/shared/ (codes only) + provenance.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import OUT, ROOT, write_provenance  # noqa: E402
import reply_threading as rt  # noqa: E402

VAL = rt.VAL
STANCE_KEYS = list(rt.STANCES)                 # supports, opposes, asks, neutral
SIGN = {"supports": 1, "opposes": -1, "asks": 0, "neutral": 0}


# ---------------------------------------------------------------------------------------------------------------------
def labels_df() -> pl.DataFrame:
    """One row per labelled (b, a): first successful label."""
    df = rt.load_labels()
    df = df.filter(pl.col("p_reply").is_not_null())
    df = df.with_columns(pl.col("b").cast(pl.UInt32), pl.col("a").cast(pl.UInt32), pl.col("rank").cast(pl.Int16), pl.col("set").cast(pl.Utf8),
                         *[pl.col(c).cast(pl.Float32) for c in ["p_reply", "stance_conf"] + [f"p_{k}" for k in STANCE_KEYS]])
    return df.unique(["b", "a"], keep="first", maintain_order=True)


def _sheet(pairs: pl.DataFrame, name: str, strata: list[str]):
    pairs = pairs.with_columns(pl.Series("stratum", strata))
    pairs = pairs.sample(fraction=1.0, shuffle=True, seed=rt.SEED + len(name)).with_row_index("vid")
    st = rt.make_states(pairs.select("b", "a", "set", "rank"))
    VAL.mkdir(parents=True, exist_ok=True)
    with (VAL / f"sheet_{name}.jsonl").open("w") as f:      # gated text: data/processed only, never committed
        for vid, s in enumerate(st):
            f.write(json.dumps({"vid": vid, "A": s["state"]["message_A"], "B": s["state"]["message_B"]}) + "\n")
    pairs.select("vid", "b", "a", "stratum").write_parquet(VAL / f"key_{name}.parquet")
    print(f"wrote sheet_{name}.jsonl ({pairs.height} items); key kept separately", flush=True)


def val_sample(which: str = "random100"):
    cand = pl.read_parquet(rt.RT / "candidates.parquet").with_columns(pl.col("set").cast(pl.Utf8))
    meta = pl.read_parquet(rt.RT / "b_meta.parquet")
    smoke = set()
    for f in rt.LABELS.glob("smoke.jsonl"):
        smoke |= {json.loads(l)["b"] for l in f.open()}
    top1 = (cand.filter((pl.col("set") == "cand") & (pl.col("rank") == 1))
            .join(meta.filter(~pl.col("holdout")).select("b"), on="b", how="semi")
            .filter(~pl.col("b").is_in(list(smoke))))
    if which == "random100":       # drawn without any Jev output (top1 non-holdout pairs, random => regime-proportional)
        x = top1.sample(100, seed=rt.SEED)
        _sheet(x, which, ["random"] * x.height)
    elif which == "mixed75":       # 50 enriched by Jev's prediction + 25 random, shuffled; strata hidden in the key
        used = set(pl.read_parquet(VAL / "key_random100.parquet")["b"].to_list())
        lab = labels_df().filter((pl.col("set") == "cand") & (pl.col("rank") == 1))
        pool = top1.join(lab.select("b", "a", "stance", "p_reply"), on=["b", "a"]).filter(~pl.col("b").is_in(list(used)))
        opp = pool.filter(pl.col("stance") == "opposes").sample(17, seed=rt.SEED)
        ask = pool.filter(pl.col("stance") == "asks").sample(17, seed=rt.SEED)
        rest = pool.filter(~pl.col("b").is_in(opp["b"].to_list() + ask["b"].to_list()))
        mid = rest.filter(pl.col("p_reply").is_between(0.3, 0.7)).sample(16, seed=rt.SEED)
        rest = rest.filter(~pl.col("b").is_in(mid["b"].to_list()))
        rnd = rest.sample(25, seed=rt.SEED + 1)
        x = pl.concat([d.select(top1.columns) for d in (opp, ask, mid, rnd)])
        _sheet(x, which, ["opposes"] * 17 + ["asks"] * 17 + ["mid"] * 16 + ["random"] * 25)


# ---------------------------------------------------------------------------------------------------------------------
def kappa(y1, y2, w=None, cats=None) -> float:
    y1, y2 = np.asarray(y1), np.asarray(y2)
    w = np.ones(len(y1)) if w is None else np.asarray(w, float)
    cats = cats or sorted(set(y1) | set(y2))
    M = np.zeros((len(cats), len(cats)))
    for a, b, ww in zip(y1, y2, w):
        M[cats.index(a), cats.index(b)] += ww
    M /= M.sum()
    po, pe = np.trace(M), (M.sum(1) * M.sum(0)).sum()
    return float((po - pe) / (1 - pe)) if pe < 1 else float("nan")


def _strata_pop(lab_top1: pl.DataFrame) -> pl.DataFrame:
    """Population strata of non-holdout top-1 labels (same rule as the enriched draw)."""
    return lab_top1.with_columns(
        pl.when(pl.col("stance") == "opposes").then(pl.lit("opposes"))
        .when(pl.col("stance") == "asks").then(pl.lit("asks"))
        .when(pl.col("p_reply").is_between(0.3, 0.7)).then(pl.lit("mid"))
        .otherwise(pl.lit("rest")).alias("pstratum"))


def validate():
    res = {"computed_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    lab = labels_df()
    cand = pl.read_parquet(rt.RT / "candidates.parquet").with_columns(pl.col("set").cast(pl.Utf8))
    meta = pl.read_parquet(rt.RT / "b_meta.parquet")
    nh = meta.filter(~pl.col("holdout")).select("b", "regime", "goal_no", "b_agent", "pt_date", "room")
    feats = cand.select("b", "a", pl.col("set").alias("set_h18"), pl.col("rank").alias("rank_h18"), "cos", "b_names_a", "a_names_b",
                        "new", "pos", "lag_s", "a_kind", "a_agent")
    L = lab.join(feats, on=["b", "a"], how="left").join(nh, on="b", how="inner")   # non-holdout only
    L = ledger_status(L).with_columns((pl.col("p_supports") - pl.col("p_opposes")).alias("s_soft"))
    top1 = L.filter(pl.col("phase") == "top1")   # H18 top-1 (the population of the blind draw)
    res["n_labelled_nonholdout"] = {k: int(v) for k, v in L.group_by("phase").len().iter_rows()}

    # ---- descriptive distribution
    res["top1_distribution"] = {
        "n": top1.height, "mean_p_reply": float(top1["p_reply"].mean()),
        "share_p_reply_ge_0.5": float((top1["p_reply"] >= 0.5).mean()),
        "stance_shares": {k: float(v) for k, v in top1.group_by("stance").len().with_columns(pl.col("len") / top1.height).iter_rows()},
        "by_regime": {r: {"n": int(n), "mean_p_reply": float(m), "share_ge_0.5": float(s), "opposes_share": float(o)}
                      for r, n, m, s, o in top1.group_by("regime").agg(pl.len(), pl.col("p_reply").mean(), (pl.col("p_reply") >= 0.5).mean().alias("_r50"),
                                                                       (pl.col("stance") == "opposes").mean().alias("_o")).sort("regime").iter_rows()},
    }

    # ---- blind second labeler
    blind = []
    for name in ("random100", "mixed75"):
        kf, lf = VAL / f"key_{name}.parquet", VAL / f"claude_labels_{name}.json"
        if kf.exists() and lf.exists():
            key = pl.read_parquet(kf)
            raw = json.loads(lf.read_text())["labels"]
            cl = pl.DataFrame([{"vid": r["vid"], "c_reply": bool(r["reply"]), "c_stance": r["stance"],
                                "c_opp_type": r.get("opp_type") if r["stance"] == "opposes" else "none"} for r in raw],
                              schema={"vid": pl.UInt32, "c_reply": pl.Boolean, "c_stance": pl.Utf8, "c_opp_type": pl.Utf8})
            blind.append(key.with_columns(pl.lit(name).alias("sheet")).join(cl, on="vid"))
    if blind:
        V = pl.concat(blind).join(lab.select("b", "a", "p_reply", "stance", "stance_conf", *[f"p_{k}" for k in STANCE_KEYS]),
                                  on=["b", "a"], how="inner")
        V = V.with_columns((pl.col("p_reply") >= 0.5).alias("j_reply"))
        op = opp_df()
        if op.height:
            V = V.join(op.select("b", "a", pl.col("opp_type").alias("j_opp_type")), on=["b", "a"], how="left")
        else:
            V = V.with_columns(pl.lit(None, pl.Utf8).alias("j_opp_type"))
        res["blind"] = blind_stats(V, top1)
    # ---- ranking recall (audit)
    res["audit"] = audit_stats(L, meta)
    # ---- placebo
    res["placebo_h18_rule"] = placebo_stats(L)
    res["placebo_ledger"] = placebo_ledger(L)
    # ---- ground truth
    res["ground_truth_g12"] = g12_check(top1)
    res["g51_roles"] = g51_roles(top1)
    res["h37_agreement"] = h37_agreement(lab)
    (VAL / "results.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(res, indent=1, default=float)[:20000])


def blind_stats(V: pl.DataFrame, top1: pl.DataFrame) -> dict:
    out = {"n_total": V.height}
    rnd = V.filter(pl.col("stratum") == "random")

    def block(D, w=None):
        jr, cr = D["j_reply"].to_list(), D["c_reply"].to_list()
        js, cs = D["stance"].to_list(), D["c_stance"].to_list()
        jsg, csg = [SIGN[x] for x in js], [SIGN[x] for x in cs]
        ww = None if w is None else np.asarray(w)
        agree = lambda a, b: float(np.average(np.asarray(a) == np.asarray(b), weights=ww))
        return {"n": D.height,
                "kappa_reply": kappa(jr, cr, ww, [False, True]), "agree_reply": agree(jr, cr),
                "kappa_stance4": kappa(js, cs, ww, STANCE_KEYS), "agree_stance4": agree(js, cs),
                "kappa_sign": kappa(jsg, csg, ww, [-1, 0, 1]), "agree_sign": agree(jsg, csg),
                "claude_reply_share": float(np.average(np.asarray(cr, float), weights=ww)),
                "jev_reply_share": float(np.average(np.asarray(jr, float), weights=ww))}
    out["random"] = block(rnd)
    # reweight all items to population strata shares
    pop = _strata_pop(top1)
    shares = {k: v / pop.height for k, v in pop.group_by("pstratum").len().iter_rows()}
    Vs = V.join(pop.select("b", "a", "pstratum"), on=["b", "a"], how="left").with_columns(pl.col("pstratum").fill_null("rest"))
    cnt = dict(Vs.group_by("pstratum").len().iter_rows())
    w = [shares.get(s, 0) / cnt[s] for s in Vs["pstratum"].to_list()]
    out["all_reweighted"] = block(Vs, w)
    out["strata_population_shares"] = shares
    # agreement by Jev confidence
    conf = []
    for lo, hi in ((0, 0.5), (0.5, 0.8), (0.8, 1.01)):
        D = V.filter(pl.col("stance_conf").is_between(lo, hi, closed="left"))
        if D.height:
            conf.append({"stance_conf": [lo, min(hi, 1.0)], "n": D.height,
                         "agree_stance4": float((D["stance"] == D["c_stance"]).mean()),
                         "agree_sign": float((D["stance"].replace_strict(SIGN) == D["c_stance"].replace_strict(SIGN)).mean())})
    out["by_stance_conf"] = conf
    # label-noise floor of the raw opposes share: population share of (Jev opposes, Claude not opposes)
    wv = np.asarray(w)
    jo, co = (Vs["stance"] == "opposes").to_numpy(), (Vs["c_stance"] == "opposes").to_numpy()
    out["opposes_noise"] = {"jev_opposes_share_pop": float(np.average(jo, weights=wv)), "claude_opposes_share_pop": float(np.average(co, weights=wv)),
                            "false_oppose_share_pop (noise floor)": float(np.average(jo & ~co, weights=wv)),
                            "missed_oppose_share_pop": float(np.average(~jo & co, weights=wv)),
                            "h37_noise_floor_for_reference": 0.065}
    # opposition subtype on Jev-opposes items
    J = V.filter((pl.col("stance") == "opposes") & pl.col("j_opp_type").is_not_null())
    if J.height:
        out["opp_type"] = {"n_jev_opposes_with_subtype": J.height,
                           "agree_subtype (Claude non-opposes = none)": float((J["j_opp_type"] == J["c_opp_type"]).mean()),
                           "kappa_subtype": kappa(J["j_opp_type"].to_list(), J["c_opp_type"].to_list(), None, list(rt.OPP_TYPES)),
                           "jev_subtype_counts": dict(J.group_by("j_opp_type").len().iter_rows()),
                           "claude_subtype_counts": dict(J.group_by("c_opp_type").len().iter_rows()),
                           "precision_position (Claude opposes+position)": (float(((J["j_opp_type"] == "position") & (J["c_opp_type"] == "position")).sum()
                                                                                   / max(1, (J["j_opp_type"] == "position").sum()))),
                           "precision_any_oppose_when_subtype_not_none": float((J.filter(pl.col("j_opp_type") != "none")["c_stance"] == "opposes").mean())
                           if J.filter(pl.col("j_opp_type") != "none").height else None}
    rc = []
    V2 = V.with_columns(((pl.col("p_reply") - 0.5).abs() * 2).alias("rconf"))
    for lo, hi in ((0, 0.4), (0.4, 0.8), (0.8, 1.01)):
        D = V2.filter(pl.col("rconf").is_between(lo, hi, closed="left"))
        if D.height:
            rc.append({"reply_conf_|2p-1|": [lo, min(hi, 1.0)], "n": D.height, "agree_reply": float((D["j_reply"] == D["c_reply"]).mean())})
    out["by_reply_conf"] = rc
    # per-class precision (all items, unweighted: precision is conditional on Jev's class)
    out["precision_by_jev_stance"] = {k: {"n": int(D.height), "precision": float((D["c_stance"] == k).mean()),
                                          "claude_counts": dict(D.group_by("c_stance").len().iter_rows())}
                                      for k in STANCE_KEYS if (D := V.filter(pl.col("stance") == k)).height}
    out["precision_reply"] = {"jev_yes_n": int(V["j_reply"].sum()), "precision_yes": float(V.filter(pl.col("j_reply"))["c_reply"].mean()),
                              "jev_no_n": int((~V["j_reply"]).sum()), "npv_no": float((~V.filter(~pl.col("j_reply"))["c_reply"]).mean())}
    out["confusion_stance_rows_claude_cols_jev"] = {c: dict(V.filter(pl.col("c_stance") == c).group_by("stance").len().iter_rows())
                                                    for c in STANCE_KEYS}
    # calibration of p_reply against Claude's reply label
    cal = []
    for lo, hi in ((0, 0.2), (0.2, 0.5), (0.5, 0.8), (0.8, 1.01)):
        D = V.filter(pl.col("p_reply").is_between(lo, hi, closed="left"))
        if D.height:
            cal.append({"p_reply": [lo, min(hi, 1.0)], "n": D.height, "claude_reply_rate": float(D["c_reply"].mean())})
    out["reply_calibration"] = cal
    return out


def audit_stats(L: pl.DataFrame, meta: pl.DataFrame) -> dict:
    A = L.filter(pl.col("phase") == "audit")
    if A.is_empty():
        return {}
    # messages whose whole pool got labelled
    full = A.group_by("b").agg(pl.len().alias("n_lab")).join(meta.select("b", "n_pool"), on="b")
    full = full.filter(pl.col("n_lab") >= pl.col("n_pool"))
    A = A.join(full.select("b"), on="b", how="semi")
    out = {"n_messages": full.height, "n_pairs": A.height}
    best = A.sort("p_reply", "rank", descending=[True, False]).group_by("b").first()
    has = best.filter(pl.col("p_reply") >= 0.5)
    out["share_with_any_reply_ge_0.5"] = has.height / max(1, best.height)
    for k in (1, 2, 3, 5, 10):
        out[f"recall_at_{k}"] = float((has["rank"] <= k).mean()) if has.height else None
    out["n_replies_ge_0.5_per_message"] = float(A.filter(pl.col("p_reply") >= 0.5).height / max(1, full.height))
    out["mean_p_reply_by_rank"] = {int(r): float(m) for r, m in A.group_by("rank").agg(pl.col("p_reply").mean()).sort("rank").head(15).iter_rows()}
    # how often the reply mass above rank K is missed
    tot = A.filter(pl.col("p_reply") >= 0.5)
    out["share_of_reply_links_within_K"] = float((tot["rank"] <= rt.K).mean()) if tot.height else None
    # which single feature ranking would have done better? (diagnostic, post hoc)
    alt = {}
    for name, expr in (("recency", pl.col("pos")), ("cos", -pl.col("cos")), ("score", pl.col("rank"))):
        b2 = A.with_columns(expr.alias("_k")).sort("_k").group_by("b", maintain_order=True).first()
        b2 = b2.join(has.select("b", pl.col("a").alias("a_best")), on="b")
        alt[name] = float((b2["a"] == b2["a_best"]).mean()) if b2.height else None
    out["top1_hits_best_reply_by_ranker"] = alt
    return out


def ledger_status(df: pl.DataFrame) -> pl.DataFrame:
    """Visibility of A to B's call under the context ledger: vis_ledger in {visible, uncertain, invisible, after}."""
    ml = pl.read_parquet(rt.RT / "b_meta_ledger.parquet", columns=["b", "s_us", "s_lo_us", "s_hi_us", "s_fallback"])
    ct = (pl.read_parquet(OUT / "chat_core.parquet", columns=["t"]).with_row_index("msg")
          .select("msg", pl.col("t").dt.epoch("us").alias("t_us")))
    df = (df.join(ml, on="b", how="left").join(ct.select(pl.col("msg").alias("a"), pl.col("t_us").alias("t_a")), on="a", how="left")
          .join(ct.select(pl.col("msg").alias("b"), pl.col("t_us").alias("t_b")), on="b", how="left"))
    lo = pl.when(pl.col("s_fallback")).then(pl.col("s_us")).otherwise(pl.col("s_lo_us"))
    hi = pl.when(pl.col("s_fallback")).then(pl.col("s_us")).otherwise(pl.col("s_hi_us"))
    return df.with_columns(pl.when(pl.col("t_a") > pl.col("t_b")).then(pl.lit("after"))
                           .when(pl.col("t_a") < lo).then(pl.lit("visible"))
                           .when(pl.col("t_a") >= hi).then(pl.lit("invisible"))
                           .otherwise(pl.lit("uncertain")).alias("vis_ledger")).drop("s_lo_us", "s_hi_us", "t_a", "t_b")


def placebo_ledger(L: pl.DataFrame) -> dict:
    """Placebo with ledger visibility: every labelled pair classed by when A arrived relative to B's call."""
    out = {}
    vis_top = L.filter((pl.col("phase").is_in(["top1", "top1_ledger"])) & (pl.col("vis_ledger") == "visible"))
    out["by_vis_status_all_labelled"] = {v: {"n": int(n), "mean_p_reply": float(m), "share_ge_0.5": float(r)}
                                         for v, n, m, r in L.group_by("vis_ledger").agg(pl.len(), pl.col("p_reply").mean(),
                                                                                         (pl.col("p_reply") >= 0.5).mean().alias("_r50")).sort("vis_ledger").iter_rows()}
    P = L.filter(pl.col("phase") == "placebo")
    out["placebo_pairs_by_vis_status"] = {f"{s}|{v}": {"n": int(n), "mean_p_reply": float(m), "share_ge_0.5": float(r)}
                                          for s, v, n, m, r in P.group_by("set", "vis_ledger").agg(pl.len(), pl.col("p_reply").mean(),
                                                                                                   (pl.col("p_reply") >= 0.5).mean().alias("_r50")).sort("set", "vis_ledger").iter_rows()}
    out["placebo_pairs_by_regime_x_vis"] = {f"{r}|{v}": {"n": int(n), "mean_p_reply": float(m)}
                                            for r, v, n, m in P.filter(pl.col("set") == "invisible").group_by("regime", "vis_ledger")
                                            .agg(pl.len(), pl.col("p_reply").mean()).sort("regime", "vis_ledger").iter_rows()}
    # strict ledger-invisible vs visible, matched on b_names_a x cos decile (visible = every labelled ledger-visible pair)
    inv = L.filter(pl.col("vis_ledger") == "invisible")
    vis = L.filter(pl.col("vis_ledger") == "visible")
    if inv.height and vis.height:
        qs = np.quantile(vis["cos"].drop_nulls().to_numpy(), np.linspace(0, 1, 11)[1:-1])
        cut = lambda df: df.with_columns(pl.col("cos").cut(list(qs), labels=[str(i) for i in range(10)]).alias("cdec"))
        g = cut(inv).group_by("b_names_a", "cdec").agg(pl.len().alias("n_p"), pl.col("p_reply").mean().alias("m_p"),
                                                       (pl.col("p_reply") >= 0.5).mean().alias("r_p"))
        h = cut(vis).group_by("b_names_a", "cdec").agg(pl.len().alias("n_v"), pl.col("p_reply").mean().alias("m_v"),
                                                       (pl.col("p_reply") >= 0.5).mean().alias("r_v"))
        gh = g.join(h, on=["b_names_a", "cdec"], how="inner")
        w = gh["n_p"].to_numpy()
        out["strict_invisible_vs_visible_matched"] = {
            "n_invisible": int(w.sum()), "mean_p_invisible": float(np.average(gh["m_p"], weights=w)),
            "mean_p_visible_matched": float(np.average(gh["m_v"], weights=w)),
            "rate_ge_0.5_invisible": float(np.average(gh["r_p"], weights=w)),
            "rate_ge_0.5_visible_matched": float(np.average(gh["r_v"], weights=w))}
        for mb in (True, False):
            sub = gh.filter(pl.col("b_names_a") == mb)
            if sub.height:
                ww = sub["n_p"].to_numpy()
                out["strict_invisible_vs_visible_matched"][f"b_names_a={mb}"] = {
                    "n_invisible": int(ww.sum()), "mean_p_invisible": float(np.average(sub["m_p"], weights=ww)),
                    "mean_p_visible_matched": float(np.average(sub["m_v"], weights=ww)),
                    "rate_ge_0.5_invisible": float(np.average(sub["r_p"], weights=ww)),
                    "rate_ge_0.5_visible_matched": float(np.average(sub["r_v"], weights=ww))}
    out["visible_top1_mean_p_reply"] = float(vis_top["p_reply"].mean()) if vis_top.height else None
    rv = L.filter(pl.col("vis_ledger") == "after")
    out["reversed_after_B"] = {"n": rv.height, "mean_p_reply": float(rv["p_reply"].mean()) if rv.height else None,
                               "share_ge_0.5": float((rv["p_reply"] >= 0.5).mean()) if rv.height else None}
    return out


def placebo_stats(L: pl.DataFrame) -> dict:
    out = {}
    L = L.filter(pl.col("phase") != "top1_ledger")      # sets and ranks below are H18's
    top1 = L.filter((pl.col("set") == "cand") & (pl.col("rank") == 1))
    for s in ("invisible", "reversed"):
        P = L.filter(pl.col("set") == s)
        if P.is_empty():
            continue
        # paired with the same B's visible top-1
        pr = P.join(top1.select("b", pl.col("p_reply").alias("p_vis"), pl.col("cos").alias("cos_vis"),
                                pl.col("b_names_a").alias("mb_vis")), on="b", how="inner")
        d = {"n": P.height, "mean_p_reply": float(P["p_reply"].mean()), "share_ge_0.5": float((P["p_reply"] >= 0.5).mean()),
             "visible_top1_mean_p_reply": float(top1["p_reply"].mean()),
             "ratio_to_visible_top1": float(P["p_reply"].mean() / top1["p_reply"].mean()),
             "paired_same_B": {"n": pr.height, "mean_p_placebo": float(pr["p_reply"].mean()), "mean_p_visible_top1": float(pr["p_vis"].mean()),
                               "share_placebo_gt_visible": float((pr["p_reply"] > pr["p_vis"]).mean())}}
        # matched on b_names_a x cos decile, against ALL labelled visible candidates (any rank)
        vis = L.filter(pl.col("set") == "cand")
        qs = np.quantile(vis["cos"].drop_nulls().to_numpy(), np.linspace(0, 1, 11)[1:-1])
        cut = lambda df: df.with_columns(pl.col("cos").cut(list(qs), labels=[str(i) for i in range(10)]).alias("cdec"))
        Pv, Vv = cut(P), cut(vis)
        g = Pv.group_by("b_names_a", "cdec").agg(pl.len().alias("n_p"), pl.col("p_reply").mean().alias("m_p"),
                                                 (pl.col("p_reply") >= 0.5).mean().alias("r_p"))
        h = Vv.group_by("b_names_a", "cdec").agg(pl.len().alias("n_v"), pl.col("p_reply").mean().alias("m_v"),
                                                 (pl.col("p_reply") >= 0.5).mean().alias("r_v"))
        gh = g.join(h, on=["b_names_a", "cdec"], how="inner")
        w = gh["n_p"].to_numpy()
        d["matched_mention_x_cosdecile"] = {"n_cells": gh.height, "mean_p_placebo": float(np.average(gh["m_p"], weights=w)),
                                            "mean_p_visible_matched": float(np.average(gh["m_v"], weights=w)),
                                            "rate_ge_0.5_placebo": float(np.average(gh["r_p"], weights=w)),
                                            "rate_ge_0.5_visible_matched": float(np.average(gh["r_v"], weights=w))}
        for mb in (True, False):
            sub = gh.filter(pl.col("b_names_a") == mb)
            if sub.height:
                ww = sub["n_p"].to_numpy()
                d["matched_mention_x_cosdecile"][f"b_names_a={mb}"] = {
                    "n_placebo": int(ww.sum()), "mean_p_placebo": float(np.average(sub["m_p"], weights=ww)),
                    "mean_p_visible_matched": float(np.average(sub["m_v"], weights=ww))}
        d["by_regime"] = {r: {"n": int(n), "mean_p": float(m)} for r, n, m in
                          P.group_by("regime").agg(pl.len(), pl.col("p_reply").mean()).sort("regime").iter_rows()}
        out[s] = d
    # mentions are not replies
    mb = top1.filter(pl.col("b_names_a"))
    out["mention_pairs_top1"] = {"n": mb.height, "mean_p_reply": float(mb["p_reply"].mean()),
                                 "share_p_reply_lt_0.5": float((mb["p_reply"] < 0.5).mean()),
                                 "non_mention_mean_p_reply": float(top1.filter(~pl.col("b_names_a"))["p_reply"].mean())}
    return out


def _names():
    return {n: int(a) for a, n in pl.read_parquet(OUT / "roster.parquet", columns=["agent", "name"]).iter_rows()}


def g12_check(top1: pl.DataFrame) -> dict:
    p = ROOT / "hypotheses/H21-debate-antiferromagnet/scheme/labels/g12_debates.json"
    if not p.exists():
        return {}
    d = json.loads(p.read_text())
    nm = _names()
    chat = pl.read_parquet(OUT / "chat_core.parquet", columns=["t"]).with_row_index("msg")
    T = top1.filter(pl.col("goal_no") == 12).join(chat.select(pl.col("msg").alias("b"), pl.col("t").alias("t_b")), on="b")
    rows = []
    for e in d["debates"]:
        if not e.get("held"):
            continue
        t0, t1 = dt.datetime.fromisoformat(e["t_first_speech"]), dt.datetime.fromisoformat(e["t_verdict"])
        team = {nm[x]: "gov" for x in e["gov"] if x in nm} | {nm[x]: "opp" for x in e["opp"] if x in nm}
        sub = T.filter((pl.col("t_b") >= t0) & (pl.col("t_b") < t1) & (pl.col("a_kind") == 0))
        for r in sub.iter_rows(named=True):
            ta, tb = team.get(r["a_agent"]), team.get(r["b_agent"])
            if ta and tb:
                rows.append({"debate": e["debate"], "same": ta == tb, "p_reply": r["p_reply"], "stance": r["stance"],
                             "s_soft": r["s_soft"], "p_opposes": r["p_opposes"]})
    if not rows:
        return {"n": 0}
    D = pl.DataFrame(rows)
    out = {"n": D.height}
    for same in (True, False):
        S = D.filter(pl.col("same") == same)
        out["same_team" if same else "opposite_team"] = {
            "n": S.height, "opposes_share": float((S["stance"] == "opposes").mean()), "supports_share": float((S["stance"] == "supports").mean()),
            "mean_s_soft": float(S["s_soft"].mean()), "mean_p_reply": float(S["p_reply"].mean())}
    # permutation of the same/opposite label within debate
    rng = np.random.default_rng(12)
    obs = out["opposite_team"]["opposes_share"] - out["same_team"]["opposes_share"]
    deb, same, opp = D["debate"].to_numpy(), D["same"].to_numpy(), (D["stance"] == "opposes").to_numpy()
    null = []
    for _ in range(2000):
        s2 = same.copy()
        for k in np.unique(deb):
            ix = np.where(deb == k)[0]
            s2[ix] = rng.permutation(s2[ix])
        null.append(opp[~s2].mean() - opp[s2].mean())
    out["opposes_share_diff_opp_minus_same"] = obs
    out["perm_p_one_sided"] = float((np.sum(np.array(null) >= obs) + 1) / (len(null) + 1))
    return out


def g51_roles(top1: pl.DataFrame) -> dict:
    p = ROOT / "hypotheses/H22-private-goals-spin-glass/scheme/role_relations.py"
    if not p.exists():
        return {}
    sys.dont_write_bytecode = True          # read-only import: never write into hypotheses/
    sys.path.insert(0, str(p.parent))
    import role_relations as rr  # noqa: E402
    ros = pl.read_parquet(OUT / "roster.parquet", columns=["agent", "agent_id"])
    spells = rr.load_role_spells(dict(zip(ros["agent_id"].to_list(), [int(x) for x in ros["agent"].to_list()])))
    T = top1.filter((pl.col("goal_no") == 51) & (pl.col("a_kind") == 0))
    cls = []
    for r in T.select("a_agent", "b_agent", "pt_date").iter_rows():
        cls.append(rr.pair_class(rr.role_on(spells, int(r[0]), r[2]), rr.role_on(spells, int(r[1]), r[2])))
    T = T.with_columns(pl.Series("cls", cls).replace_strict(rr.CLASS_NAMES))
    return {c: {"n": int(n), "mean_p_reply": float(m), "opposes_share": float(o), "supports_share": float(s), "mean_s_soft": float(ss)}
            for c, n, m, o, s, ss in T.group_by("cls").agg(pl.len(), pl.col("p_reply").mean(), (pl.col("stance") == "opposes").mean().alias("_o"),
                                                           (pl.col("stance") == "supports").mean().alias("_s"), pl.col("s_soft").mean()).sort("cls").iter_rows()}


def h37_agreement(lab: pl.DataFrame) -> dict:
    d = ROOT / "data/processed/H37-stance-spins/labels"
    if not d.exists():
        return {}
    recs = []
    for f in d.glob("*.jsonl"):
        for line in f.open():
            j = json.loads(line)
            if j.get("stance") is not None:
                recs.append({k: j.get(k) for k in ("msg_a", "msg_b", "stance", "responds", "p_agree", "p_support", "p_oppose", "p_undermine")})
    if not recs:
        return {}
    H = pl.DataFrame(recs, infer_schema_length=None).unique(["msg_a", "msg_b"])
    idx = pl.read_parquet(rt.RT / "msg_index.parquet")
    M = lab.join(idx.select(pl.col("msg").alias("a"), pl.col("message_id").alias("msg_a")), on="a").join(
        idx.select(pl.col("msg").alias("b"), pl.col("message_id").alias("msg_b")), on="b")
    # visibility of H37's pairs under the call-start rule (H37 pairs are mention / adjacency based)
    meta = pl.read_parquet(rt.RT / "b_meta.parquet", columns=["b", "s_us"])
    ct = pl.read_parquet(OUT / "chat_core.parquet", columns=["t"]).with_row_index("msg").with_columns(pl.col("t").dt.epoch("us").alias("t_us"))
    Hv = (H.join(idx.select(pl.col("msg").alias("a"), pl.col("message_id").alias("msg_a")), on="msg_a")
          .join(idx.select(pl.col("msg").alias("b"), pl.col("message_id").alias("msg_b")), on="msg_b"))
    Hn = Hv.join(ct.select(pl.col("msg").alias("a"), pl.col("t_us").alias("t_a")), on="a").join(meta, on="b")
    Hl = ledger_status(Hv.select("b", "a"))
    vis = {"n_h37_pairs": Hv.height, "share_A_invisible_to_B_h18_rule": float((Hn["t_a"] >= Hn["s_us"]).mean()),
           "ledger_status_shares": {k: float(v) for k, v in Hl.group_by("vis_ledger").len().with_columns(pl.col("len") / Hl.height).iter_rows()}}
    J = M.join(H, on=["msg_a", "msg_b"], suffix="_h37")
    if J.is_empty():
        return {"n": 0, "visibility": vis}
    h_sign = J["stance_h37"].replace_strict({"agree": 1, "support": 1, "neutral": 0, "oppose": -1, "undermine": -1}).to_list()
    m_sign = J["stance"].replace_strict(SIGN).to_list()
    hs = (J["p_agree"] + J["p_support"] - J["p_oppose"] - J["p_undermine"]).to_numpy()
    ms = (J["p_supports"] - J["p_opposes"]).to_numpy()
    ok = np.isfinite(hs) & np.isfinite(ms)
    return {"n": J.height, "kappa_sign": kappa(h_sign, m_sign, None, [-1, 0, 1]),
            "agree_sign": float(np.mean(np.array(h_sign) == np.array(m_sign))),
            "corr_soft_sign": float(np.corrcoef(hs[ok], ms[ok])[0, 1]),
            "corr_responds_vs_p_reply": float(np.corrcoef(J["responds"].cast(pl.Float64).to_numpy(), J["p_reply"].cast(pl.Float64).to_numpy())[0, 1]),
            "neg_share_h37": float(np.mean(np.array(h_sign) == -1)), "neg_share_dq2": float(np.mean(np.array(m_sign) == -1)),
            "visibility": vis,
            "h37_responds_ge_0.5_share": float((J["responds"].cast(pl.Float64) >= 0.5).mean()),
            "dq2_p_reply_ge_0.5_share": float((J["p_reply"].cast(pl.Float64) >= 0.5).mean())}


# ---------------------------------------------------------------------------------------------------------------------
def opp_df() -> pl.DataFrame:
    recs = []
    for f in rt.LABELS.glob("opptype*.jsonl"):
        for line in f.open():
            j = json.loads(line)
            if j.get("opp_type") is not None:
                recs.append({"b": j["b"], "a": j["a"], "opp_type": j["opp_type"], **{f"p_opp_{k}": j.get(f"p_opp_{k}") for k in rt.OPP_TYPES}})
    if not recs:
        return pl.DataFrame()
    return pl.DataFrame(recs, infer_schema_length=None).with_columns(pl.col("b").cast(pl.UInt32), pl.col("a").cast(pl.UInt32)).unique(["b", "a"])


def h37_df() -> pl.DataFrame:
    d = ROOT / "data/processed/H37-stance-spins/labels"
    recs = []
    for f in d.glob("*.jsonl"):
        for line in f.open():
            j = json.loads(line)
            if j.get("stance") is not None:
                pa = [j.get(k) or 0.0 for k in ("p_agree", "p_support", "p_oppose", "p_undermine")]
                recs.append({"A_message_id": j["msg_a"], "B_message_id": j["msg_b"], "h37_stance": j["stance"],
                             "h37_s_soft": pa[0] + pa[1] - pa[2] - pa[3], "h37_responds": j.get("responds")})
    schema = {"A_message_id": pl.Utf8, "B_message_id": pl.Utf8, "h37_stance": pl.Utf8, "h37_s_soft": pl.Float32, "h37_responds": pl.Float32}
    return pl.DataFrame(recs, schema=schema).unique(["A_message_id", "B_message_id"])


def compile_tables(dest: Path | None = None):
    """reply_pairs + reply_graph from the ledger candidate pools (primary) and every label, joined on (B, A)."""
    dest = dest or OUT
    cl = pl.read_parquet(rt.RT / "candidates_ledger.parquet").with_columns(pl.col("set").cast(pl.Utf8))
    ch = pl.read_parquet(rt.RT / "candidates.parquet").with_columns(pl.col("set").cast(pl.Utf8))
    ml = pl.read_parquet(rt.RT / "b_meta_ledger.parquet")
    idx = pl.read_parquet(rt.RT / "msg_index.parquet")
    chat = pl.read_parquet(OUT / "chat_core.parquet", columns=["speaker_kind", "agent"]).with_row_index("msg")
    lab = labels_df().select("b", "a", "phase", "p_reply", *[f"p_{k}" for k in STANCE_KEYS], "stance", "stance_conf", "cost")
    h37k = rt.h37_pairs().unique()
    feat_cols = ["score", "cos", "b_names_a", "a_names_b", "new", "pos", "lag_s"]
    # universe: ledger top-K for every B, every labelled pair, and H37 pairs inside the kept ledger ranks
    U = pl.concat([cl.filter((pl.col("set") == "cand") & (pl.col("rank") <= rt.K)).select("b", "a"), lab.select("b", "a"),
                   cl.filter(pl.col("set") == "cand").join(h37k, on=["b", "a"], how="semi").select("b", "a")]).unique()
    fl = cl.select("b", "a", pl.when(pl.col("set") == "cand").then(pl.col("rank")).otherwise(None).alias("cand_rank"), *feat_cols)
    fh = ch.select("b", "a", pl.when(pl.col("set") == "cand").then(pl.col("rank")).otherwise(None).alias("rank_h18"),
                   *[pl.col(c).alias(c + "_h") for c in feat_cols])
    P = U.join(fl, on=["b", "a"], how="left").join(fh, on=["b", "a"], how="left")
    # features are pair properties except score/new/pos (cutoff-dependent): fill the pair features from the H18 build
    P = P.with_columns(*[pl.coalesce(c, c + "_h").alias(c) for c in ("cos", "b_names_a", "a_names_b", "lag_s")],
                       pl.coalesce("score", "score_h").alias("score"), pl.coalesce("new", "new_h").alias("new"),
                       pl.coalesce("pos", "pos_h").alias("pos")).drop([c + "_h" for c in feat_cols])
    P = ledger_status(P.join(lab, on=["b", "a"], how="left"))
    P = P.with_columns(pl.col("p_reply").is_not_null().alias("labelled"),
                       pl.col("vis_ledger").replace_strict({"visible": "cand", "uncertain": "cand", "invisible": "invisible", "after": "reversed"})
                       .alias("pair_set"), (pl.col("vis_ledger") == "uncertain").alias("vis_uncertain"))
    P = P.join(ml.select("b", "b_agent", "n_pool", "n_invisible", "s_fallback", "pt_date", "goal_no", "regime", "room", "holdout"), on="b", how="left")
    P = P.join(chat.select(pl.col("msg").alias("a"), pl.col("speaker_kind").cast(pl.Utf8).replace_strict(rt.KIND, default=3).cast(pl.Int8).alias("a_kind"),
                           pl.col("agent").alias("a_agent")), on="a", how="left")
    # graph set: labelled visible pairs that are B's ledger top-K or its H18 top-1 (the same designated pairs for every B)
    P = P.with_columns((pl.col("labelled") & (pl.col("pair_set") == "cand") & ((pl.col("cand_rank") <= rt.K) | (pl.col("rank_h18") == 1)))
                       .fill_null(False).alias("in_graph"))
    par = (P.filter(pl.col("in_graph")).sort(["p_reply", "cand_rank"], descending=[True, False], nulls_last=True)
           .group_by("b").first().filter(pl.col("p_reply") >= 0.5).select("b", "a", pl.lit(True).alias("parent")))
    P = P.join(par, on=["b", "a"], how="left").with_columns(pl.col("parent").fill_null(False))
    P = (P.join(idx.select(pl.col("msg").alias("b"), pl.col("message_id").alias("B_message_id")), on="b")
         .join(idx.select(pl.col("msg").alias("a"), pl.col("message_id").alias("A_message_id")), on="a"))
    op = opp_df()
    if op.height:
        P = P.join(op, on=["b", "a"], how="left")
    else:
        P = P.with_columns(pl.lit(None, pl.Utf8).alias("opp_type"), *[pl.lit(None, pl.Float32).alias(f"p_opp_{k}") for k in rt.OPP_TYPES])
    P = P.join(h37_df(), on=["A_message_id", "B_message_id"], how="left")
    P = P.with_columns(pl.when(pl.col("labelled") & pl.col("h37_stance").is_not_null()).then(pl.lit("dq2+h37"))
                       .when(pl.col("labelled")).then(pl.lit("dq2")).when(pl.col("h37_stance").is_not_null()).then(pl.lit("h37"))
                       .otherwise(pl.lit("none")).alias("label_source"))
    P = P.select(
        "B_message_id", "A_message_id", pl.col("b").alias("b_msg"), pl.col("a").alias("a_msg"),
        pl.col("pair_set").cast(pl.Categorical), "vis_uncertain", pl.col("cand_rank").cast(pl.Int16), pl.col("rank_h18").cast(pl.Int16),
        pl.col("score").cast(pl.Float32), pl.col("cos").cast(pl.Float32), "b_names_a", "a_names_b", "new", pl.col("pos").cast(pl.Int16),
        pl.col("lag_s").cast(pl.Float32), "n_pool", "n_invisible", "s_fallback",
        "b_agent", "a_kind", pl.col("a_agent").cast(pl.Int8), "room", "pt_date", "goal_no", "regime", "holdout",
        "labelled", pl.col("phase").cast(pl.Categorical), "p_reply", "p_supports", "p_opposes", "p_asks", "p_neutral",
        pl.col("stance").cast(pl.Categorical), "stance_conf",
        pl.col("opp_type").cast(pl.Categorical), *[pl.col(f"p_opp_{k}").cast(pl.Float32) for k in rt.OPP_TYPES],
        "in_graph", "parent", pl.col("cost").cast(pl.Float32), pl.col("label_source").cast(pl.Categorical),
        pl.col("h37_stance").cast(pl.Categorical), "h37_s_soft", "h37_responds"
    ).sort("b_msg", "pair_set", "cand_rank", nulls_last=True)
    P.write_parquet(dest / "reply_pairs.parquet", compression="zstd", compression_level=9)

    # ---- graph: replier (B's author) -> target (A's author; -1 human, -2 automated), over in_graph pairs
    G = P.filter(pl.col("in_graph")).with_columns(
        pl.when(pl.col("a_kind") == 0).then(pl.col("a_agent").cast(pl.Int16)).when(pl.col("a_kind") == 1).then(pl.lit(-1, pl.Int16))
        .otherwise(pl.lit(-2, pl.Int16)).alias("target"), pl.col("b_agent").cast(pl.Int16).alias("replier"))
    agg = [pl.len().cast(pl.Int32).alias("n_pairs_labelled"),
           (pl.col("cand_rank") == 1).sum().cast(pl.Int32).alias("n_top1"),
           pl.col("p_reply").sum().cast(pl.Float32).alias("reply_soft"),
           pl.col("parent").sum().cast(pl.Int32).alias("reply_hard"),
           *[(pl.col("p_reply") * pl.col(f"p_{k}")).sum().cast(pl.Float32).alias(f"{k}_soft") for k in STANCE_KEYS],
           *[(pl.col("parent") & (pl.col("stance") == k)).sum().cast(pl.Int32).alias(f"{k}_hard") for k in STANCE_KEYS],
           (pl.col("p_reply") * pl.col("p_opposes") * pl.col("p_opp_position").fill_null(0)).sum().cast(pl.Float32).alias("opp_position_soft"),
           (pl.col("parent") & (pl.col("stance") == "opposes") & (pl.col("opp_type") == "position")).sum().cast(pl.Int32).alias("opp_position_hard")]
    day = G.group_by("pt_date", "goal_no", "holdout", "replier", "target").agg(agg)
    per = G.group_by("goal_no", "holdout", "replier", "target").agg(agg)
    chm = pl.read_parquet(OUT / "chat_core.parquet", columns=["speaker_kind", "agent", "pt_date", "goal_no"]).with_row_index("b_msg")
    mc = pl.read_parquet(OUT / "chat_mentions_clean.parquet", columns=["mentions_roster"])
    chm = pl.concat([chm, mc], how="horizontal").filter(pl.col("speaker_kind") == "agent").join(
        ml.select(pl.col("b").alias("b_msg"), "holdout"), on="b_msg", how="left")
    men = (chm.explode("mentions_roster").drop_nulls("mentions_roster").filter(pl.col("mentions_roster") != pl.col("agent"))
           .select("pt_date", "goal_no", "holdout", pl.col("agent").cast(pl.Int16).alias("replier"),
                   pl.col("mentions_roster").cast(pl.Int16).alias("target")))
    keys_d, keys_p = ["pt_date", "goal_no", "holdout", "replier", "target"], ["goal_no", "holdout", "replier", "target"]
    day = day.join(men.group_by(keys_d).agg(pl.len().cast(pl.Int32).alias("n_mention_msgs")), on=keys_d, how="full", coalesce=True)
    per = per.join(men.group_by(keys_p).agg(pl.len().cast(pl.Int32).alias("n_mention_msgs")), on=keys_p, how="full", coalesce=True)
    cal = pl.read_parquet(OUT / "calendar.parquet", columns=["pt_date", "regime", "goal_no"])
    cols_num = [c for c in day.columns if c.endswith(("_soft", "_hard")) or c.startswith("n_")]
    day = day.join(cal.select("pt_date", "regime"), on="pt_date", how="left").with_columns(
        pl.lit("day").alias("scale"), *[pl.col(c).fill_null(0) for c in cols_num])
    per = per.join(cal.group_by("goal_no").agg(pl.col("regime").first()), on="goal_no", how="left").with_columns(
        pl.lit("period").alias("scale"), pl.lit(None, pl.Utf8).alias("pt_date"), *[pl.col(c).fill_null(0) for c in cols_num])
    order = ["scale", "pt_date", "goal_no", "regime", "holdout", "replier", "target"] + cols_num
    graph = pl.concat([day.select(order), per.select(order)], how="vertical_relaxed").with_columns(
        pl.col("scale").cast(pl.Categorical), pl.col("regime").cast(pl.Utf8).cast(pl.Categorical)
    ).sort("scale", "goal_no", "pt_date", "replier", "target", nulls_last=True)
    graph.write_parquet(dest / "reply_graph.parquet", compression="zstd", compression_level=9)
    if dest != OUT:
        return P, graph
    spent = rt.total_spent()
    write_provenance("reply_threading", ["shared/chat_core", "shared/chat_mentions_clean", "shared/chat_text (sent to Jev only)",
                                         "shared/exposure", "shared/actions", "shared/events_core", "shared/calendar", "shared/roster",
                                         "shared/call_windows (DQ1 ledger)", "shared/embeddings/chat_bge_small",
                                         "H37 labels (data/processed/H37-stance-spins/labels, read only)"],
                     {"outputs": ["reply_pairs.parquet", "reply_graph.parquet"], "visibility": "DQ1 context ledger t_call (H18 rule as fallback)",
                      "K": rt.K, "score": f"cos + {rt.W_MB}*b_names_a + {rt.W_MA}*a_names_b + {rt.W_NEW}*new - {rt.W_POS}*ln(pos)",
                      "lookback_s": rt.LOOKBACK_S, "max_pool": rt.MAX_POOL, "model": "typesafe/jev-1.13", "taxonomy": rt.TAXONOMY,
                      "a_chars": rt.A_CHARS, "b_chars": rt.B_CHARS, "n_pairs": P.height, "n_labelled": int(P["labelled"].sum()),
                      "spent_usd_all_runs": round(spent, 4), "cap_usd": 8.0, "design": "infra/data-quality/reply_threading.md"})
    print(f"reply_pairs {P.height} rows ({int(P['labelled'].sum())} labelled); reply_graph {graph.height} rows; spent ${spent:.4f}")
