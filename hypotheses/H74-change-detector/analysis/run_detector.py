"""H74 real-data run: channel scores on every non-holdout active day, the fused alarm, class evaluation, blind
change-points, rival comparison (fused vs content R1 alone). Non-holdout only.
Run: uv run python hypotheses/H74-change-detector/analysis/run_detector.py
Outputs: data/processed/H74-change-detector/{scores.parquet, replication/results.json, replication/changepoints.parquet}
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h74lib as L  # noqa: E402

ROOT = HERE.parents[2]
OUT = ROOT / "data/processed/H74-change-detector"
SH = ROOT / "data/processed/shared"
DOC_CLASSES = ["scaffold_tool", "scaffold_prompt", "scaffold_family", "operator", "operator_schedule", "goal",
               "goal_prompt", "roster", "room"]
DQ9 = {"2026-04-27": "#best membership reshuffle at #39 (DQ9 candidate)", "2026-05-26": "per-room goal override (DQ9 candidate)",
       "2026-08-24": "#focus empties / #51 single room (DQ9 candidate)"}


def load():
    days = pl.read_parquet(OUT / "days.parquet")
    cal = pl.read_parquet(SH / "calendar.parquet").filter(pl.col("n_agent_events") > 0).sort("pt_date")
    cal_days = cal["pt_date"].to_list()
    held = dict(zip(cal_days, cal["holdout"].to_list()))
    prev_held = {d: (i > 0 and held[cal_days[i - 1]]) for i, d in enumerate(cal_days)}
    days = days.with_columns(pl.col("pt_date").replace_strict(prev_held, return_dtype=pl.Boolean).alias("gap_return"),
                             (pl.col("idx") >= 10).alias("has_baseline"))
    assert not any(held[d] for d in days["pt_date"].to_list())
    return days, cal_days


def scores_for(days):
    dl = days["pt_date"].to_list()
    agd = pl.read_parquet(OUT / "agent_day_features.parquet")
    dfeat = pl.read_parquet(OUT / "day_features.parquet")
    sd = pl.read_parquet(OUT / "search_daily.parquet")
    sigs = pl.read_parquet(OUT / "signatures_daily.parquet")
    first = agd.group_by("agent").agg(pl.col("pt_date").sort().head(3).alias("f3"))
    newcomer = {(a, d): True for a, f3 in first.iter_rows() for d in f3}
    zS, sinfo = L.score_S(sigs, dl, newcomer)
    zM, minfo = L.score_M(agd, dl)
    zO, oinfo = L.score_series(sd, dl, L.O_FEATURES, min_count_col="n_search", min_count=3)
    zD, dinfo = L.score_series(dfeat, dl, L.D_FEATURES)
    zC, cinfo = L.score_C(dfeat, dl)
    sc = {"S": zS.astype(float), "M": zM, "O": zO, "D": zD, "C": zC}
    F, top = L.fused(sc)
    sc["F"] = F
    sdict = dict(pl.read_parquet(OUT / "signature_dict.parquet").select("sig", "fields").iter_rows())
    tab = days.select("pt_date", "goal_no", "regime", "weekday", "gap_return").with_columns(
        *[pl.Series(f"z_{k}", v) for k, v in sc.items()], pl.Series("top", top),
        pl.Series("feat_M", minfo["feature"]), pl.Series("feat_O", oinfo["feature"]), pl.Series("feat_D", dinfo["feature"]),
        pl.Series("s_new", sinfo["new"]), pl.Series("s_gone", sinfo["gone"]),
        pl.Series("s_detail", [";".join(f"{k}:{sdict.get(s, s)[:90]}" for k, s in d) for d in sinfo["detail"]]))
    return sc, tab


def paired_auc_diff(sc_a, sc_b, ev_cent, plc, cal_days, day_pos, rng, n=1000):
    wa, wb = L.window_array(sc_a, cal_days, day_pos), L.window_array(sc_b, cal_days, day_pos)
    ea, eb, pa, pb = wa[ev_cent], wb[ev_cent], wa[plc], wb[plc]
    ok_e = np.isfinite(ea) & np.isfinite(eb); ok_p = np.isfinite(pa) & np.isfinite(pb)
    ea, eb, pa, pb = ea[ok_e], eb[ok_e], pa[ok_p], pb[ok_p]
    if not ea.size:
        return None
    d0 = L.auc(ea, pa) - L.auc(eb, pb)
    bs = []
    for _ in range(n):
        i = rng.integers(0, ea.size, ea.size); j = rng.integers(0, pa.size, pa.size)
        bs.append(L.auc(ea[i], pa[j]) - L.auc(eb[i], pb[j]))
    return {"diff": float(d0), "ci": [float(np.nanpercentile(bs, 2.5)), float(np.nanpercentile(bs, 97.5))], "n": int(ea.size)}


def holm(ps):
    order = np.argsort(ps)
    adj = np.empty(len(ps))
    m = len(ps)
    run = 0.0
    for r, k in enumerate(order):
        run = max(run, min(1.0, (m - r) * ps[k]))
        adj[k] = run
    return adj


def main():
    rng = np.random.default_rng(20261004)
    days, cal_days = load()
    sc, tab = scores_for(days)
    tab.write_parquet(OUT / "scores.parquet")
    events = pl.read_parquet(OUT / "events.parquet")
    doc = events.filter(pl.col("cls") != "undocumented")
    und = events.filter(pl.col("cls") == "undocumented")
    res = L.evaluate(sc, days, doc, cal_days, DOC_CLASSES, rng, n_rand=2000, n_boot=1000, exclude_from_placebo=und)
    res_u = L.evaluate(sc, days, und, cal_days, ["undocumented"], rng, n_rand=2000, n_boot=1000, exclude_from_placebo=doc)
    res["classes"]["undocumented"] = res_u["classes"].get("undocumented", {})
    # rival: fused vs content alone, per class
    dl = days["pt_date"].to_list(); day_pos = {d: i for i, d in enumerate(dl)}; cal_pos = {d: i for i, d in enumerate(cal_days)}
    plc = np.array([cal_pos[d] for d in res["placebo_days"]], int)
    riv = {}
    for cls in DOC_CLASSES + ["undocumented"]:
        e = events.filter((pl.col("cls") == cls) & ~pl.col("held0") & pl.col("day0").is_in(dl))
        if e.height:
            riv[cls] = paired_auc_diff(sc["F"], sc["C"], np.array([cal_pos[d] for d in e["day0"].to_list()]), plc, cal_days, day_pos, rng)
    res["rival_F_minus_C"] = riv
    # Holm over class tests (fused, random-date hit p)
    cls_p = {c: v["F"]["p_rand_hit"] for c, v in res["classes"].items() if "F" in v}
    adj = holm(np.array(list(cls_p.values())))
    res["holm_F"] = dict(zip(cls_p, [float(x) for x in adj]))
    # blind change-points: alarm days, explained by a documented event within +-1 calendar active day?
    doc_c = {}
    for d0, cls, lab in doc.select("day0", "cls", "label").iter_rows():
        if d0 in cal_pos:
            doc_c.setdefault(cal_pos[d0], []).append(f"{cls}: {lab[:60]}")
    und_c = {cal_pos[d0]: ev for d0, ev in und.select("day0", "event").iter_rows() if d0 in cal_pos}
    rows = []
    for r in tab.filter(pl.col("z_F") >= L.TAU).iter_rows(named=True):
        c = cal_pos[r["pt_date"]]
        near = [x for o in (-1, 0, 1) for x in doc_c.get(c + o, [])]
        nu = [und_c[c + o] for o in (-1, 0, 1) if c + o in und_c]
        rows.append({"pt_date": r["pt_date"], "goal_no": r["goal_no"], "Z": r["z_F"], "channel": r["top"],
                     "feature": {"M": r["feat_M"], "O": r["feat_O"], "D": r["feat_D"]}.get(r["top"]),
                     "s_detail": r["s_detail"] if r["top"] == "S" else None, "gap_return": r["gap_return"],
                     "explained_by": " | ".join(near) if near else None, "undocumented": ",".join(nu) if nu else None,
                     "dq9": DQ9.get(r["pt_date"])})
    cp = pl.DataFrame(rows, infer_schema_length=None)
    (OUT / "replication").mkdir(exist_ok=True)
    cp.write_parquet(OUT / "replication" / "changepoints.parquet")
    res["changepoints"] = {"n_alarm_days": cp.height, "n_explained": int(cp["explained_by"].is_not_null().sum()),
                           "n_unexplained": int(cp["explained_by"].is_null().sum()),
                           "n_unexplained_gap_return": int((cp["explained_by"].is_null() & cp["gap_return"]).sum()),
                           "undocumented_hits": cp.filter(pl.col("undocumented").is_not_null())["undocumented"].to_list()}
    res["n_days"] = len(dl)
    (OUT / "replication" / "results.json").write_text(json.dumps(res, indent=1, default=float))
    # print a compact summary
    print("days", len(dl), "placebo", res["n_placebo"])
    print("FAR", {k: (round(v["per_day"], 3), round(v["window"], 3)) for k, v in res["far"].items()})
    for c, v in res["classes"].items():
        print(c, {k: (x["n"], round(x["hit"], 2), round(x["auc"], 2) if x["auc"] == x["auc"] else None, round(x["p_rand_hit"], 3)) for k, x in v.items()})
    print("rival", {k: (round(v["diff"], 2), [round(x, 2) for x in v["ci"]]) for k, v in riv.items() if v})
    print(res["changepoints"])


if __name__ == "__main__":
    main()
