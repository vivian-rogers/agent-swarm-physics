"""H44 round-2 R1: blind check of the call classifier and Theta_c on the checked labels.

Labels: analysis/r1_labels_blind.csv (my blind labels from tool names and arguments; codes only). Key and population
shares: data/processed/H44-erasure-reacquisition-thrash/r2/label_key.parquet, label_pop.parquet (scheme/build_r2.py).
Outputs: r2/r1_check.json
Usage: uv run python hypotheses/H44-erasure-reacquisition-thrash/analysis/r2_label.py [--B 300]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import h44lib as L  # noqa: E402
import r2lib as R  # noqa: E402
from h44lib import C  # noqa: E402

OUTD = C.OUT / "r2"
HERE = Path(__file__).resolve().parent
NC = len(C.CATS)
TOOL = {C.CAT[c] for c in ("look", "gui", "room_read", "talk", "idle")}
THREE = {**{c: "reacq" for c in C.REACQ}, **{c: "prod" for c in ("write", "run", "gui_type")},
         **{c: "other" for c in ("talk", "gui", "monitor", "setup", "idle", "other")}}
PERIODS = ["G36", "G37", "G38", "G39", "G40", "G41", "G42", "G44", "G51"]


def kappa(a, b, w, labels):
    idx = {l_: i for i, l_ in enumerate(labels)}
    M = np.zeros((len(labels), len(labels)))
    for x, y, ww in zip(a, b, w):
        M[idx[x], idx[y]] += ww
    M /= M.sum()
    po = np.trace(M)
    pe = (M.sum(1) * M.sum(0)).sum()
    return float(po), float((po - pe) / (1 - pe)) if pe < 1 else float("nan")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--B", type=int, default=300)
    a = ap.parse_args()
    rng = np.random.default_rng(4401)
    lab = pl.read_csv(HERE / "r1_labels_blind.csv", schema_overrides={"gui_split": pl.Utf8})
    key = pl.read_parquet(OUTD / "label_key.parquet")
    pop = pl.read_parquet(OUTD / "label_pop.parquet")
    d = key.join(lab, on="id", how="inner")
    assert d.height == 300, d.height
    d = d.with_columns(pl.col("cat").map_elements(lambda c: C.CATS[c], return_dtype=pl.Utf8).alias("clf"),
                       pl.when(pl.col("cat").is_in(list(TOOL))).then(pl.lit("tool")).otherwise(
                           pl.col("cat").cast(pl.Utf8)).alias("stratum"))
    pop = pop.with_columns(pl.when(pl.col("cat").is_in(list(TOOL))).then(pl.lit("tool")).otherwise(
        pl.col("cat").cast(pl.Utf8)).alias("stratum")).group_by("win", "stratum").agg(pl.col("len").sum().alias("N"))
    ns = d.group_by("win", "stratum").len().rename({"len": "n"})
    d = d.join(pop, on=["win", "stratum"], how="left").join(ns, on=["win", "stratum"])
    d = d.with_columns((pl.col("N") / pl.col("n")).alias("w"))
    out = {"n": d.height, "by_window": {}}
    for wname, g in [("all", d), *[(w_, g_) for (w_,), g_ in d.group_by("win")]]:
        w = g["w"].to_numpy().astype(float)
        clf, me = g["clf"].to_list(), g["label"].to_list()
        r = {"n": g.height}
        r["agree14_unweighted"] = float(np.mean([x == y for x, y in zip(clf, me)]))
        r["agree14"], r["kappa14"] = kappa(clf, me, w, C.CATS)
        c3 = [THREE[x] for x in clf]; m3 = [THREE[x] for x in me]
        r["agree3"], r["kappa3"] = kappa(c3, m3, w, ["reacq", "prod", "other"])
        r["agree3_unweighted"] = float(np.mean([x == y for x, y in zip(c3, m3)]))
        cb = ["R" if x in C.REACQ else "N" for x in clf]; mb = ["R" if x in C.REACQ else "N" for x in me]
        r["agree_reacq"], r["kappa_reacq"] = kappa(cb, mb, w, ["R", "N"])
        cbn, mbn = np.array(cb) == "R", np.array(mb) == "R"
        r["precision_reacq"] = float((w * (cbn & mbn)).sum() / max((w * cbn).sum(), 1e-12))
        r["recall_reacq"] = float((w * (cbn & mbn)).sum() / max((w * mbn).sum(), 1e-12))
        out["by_window"][wname] = r
    # confusion (unweighted counts), classifier rows x my labels
    conf = d.group_by("clf", "label").len().sort("clf", "label")
    out["confusion"] = [list(x) for x in conf.rows()]
    out["per_category"] = {}
    for (c_, w_), g in d.group_by("clf", "win"):
        out["per_category"][f"{c_}|{w_}"] = {"n": g.height, "agree": float((g["label"] == c_).mean()),
                                             "my_reacq": float(g["label"].is_in(C.REACQ).mean())}
    gt = d.filter(pl.col("label") == "gui_type")
    out["gui_type_split"] = {w_: {"n": g.height, "nav": float((g["gui_split"] == "nav").mean())}
                             for (w_,), g in gt.group_by("win")}
    out["gui_note"] = "clicks, scrolls, keys and mouse moves carry coordinates only: no navigation/production split"

    # q tables: P(my label in REACQ | classifier category, window); unsampled cells fall back to the classifier's rule
    def qtab(df, nav_as_reacq=False):
        q = {}
        for wname in ("post", "mid"):
            v = np.array([1.0 if C.CATS[i] in C.REACQ else 0.0 for i in range(NC)])
            g = df.filter(pl.col("win") == wname)
            for i in range(NC):
                gi = g.filter(pl.col("cat") == i)
                if gi.height:
                    hit = gi["label"].is_in(C.REACQ)
                    if nav_as_reacq:
                        hit = hit | ((gi["label"] == "gui_type") & (gi["gui_split"] == "nav"))
                    v[i] = float(hit.mean())
            q[wname] = v
        return q

    def boot_q(nav=False):
        qs_p, qs_m = [], []
        parts = {k_: g for k_, g in d.group_by("win", "stratum")}
        for b in range(a.B):
            res = pl.concat([g[rng.integers(0, g.height, g.height).tolist()] for g in parts.values()])
            q = qtab(res, nav)
            qs_p.append(q["post"]); qs_m.append(q["mid"])
        return np.array(qs_p), np.array(qs_m)

    q = qtab(d); qn = qtab(d, True)
    out["q_post"] = dict(zip(C.CATS, q["post"].round(3).tolist()))
    out["q_mid"] = dict(zip(C.CATS, q["mid"].round(3).tolist()))
    out["q_post_nav"] = dict(zip(C.CATS, qn["post"].round(3).tolist()))
    out["q_mid_nav"] = dict(zip(C.CATS, qn["mid"].round(3).tolist()))
    qbp, qbm = boot_q(False)
    qnbp, qnbm = boot_q(True)
    calls = pl.read_parquet(C.OUT / "calls.parquet")
    ev = pl.read_parquet(C.OUT / "events.parquet")
    C.refuse_holdout(calls["pt_date"].unique().to_list(), "calls")
    ind = np.array([1.0 if C.CATS[i] in C.REACQ else 0.0 for i in range(NC)])
    out["theta"] = {}
    for per in PERIODS:
        cp = calls.filter(pl.col("period") == per); ep = ev.filter(pl.col("period") == per)
        r1 = json.loads((C.OUT / per / "results.json").read_text())["stats"]["forced"]["contrasts"]["post5_vs_far"]["Theta_c"]
        chk_ind = R.theta_c_soft(cp, ep, ind, ind, B=50, seed=1)
        th = R.theta_c_soft(cp, ep, q["post"], q["mid"], qbp, qbm, B=a.B, seed=2)
        thn = R.theta_c_soft(cp, ep, qn["post"], qn["mid"], qnbp, qnbm, B=a.B, seed=3)
        # same q in both windows (mid-segment rates everywhere): isolates window-specific classifier error
        thm = R.theta_c_soft(cp, ep, q["mid"], q["mid"], qbm, qbm, B=a.B, seed=4)
        out["theta"][per] = {"round1": r1, "indicator_reproduces": chk_ind["theta_c"],
                             "checked": [th["theta_c"], *th["ci"]], "checked_nav": [thn["theta_c"], *thn["ci"]],
                             "checked_midq": [thm["theta_c"], *thm["ci"]], "n_events": th["n_events"]}
        C.log(per, out["theta"][per])
    for key_ in ("checked", "checked_nav", "checked_midq"):
        e = [v[key_][0] for v in out["theta"].values()]
        lo = [v[key_][1] for v in out["theta"].values()]
        hi = [v[key_][2] for v in out["theta"].values()]
        out[f"pooled_{key_}"] = L.dl_pool(e, lo, hi)
        out[f"n_periods_gt_floor_{key_}"] = int(sum(1 for v in out["theta"].values()
                                                   if v[key_][1] > 0 and v[key_][0] > L.THETA_FLOOR))
    (OUTD / "r1_check.json").write_text(json.dumps(out, indent=1, default=float))
    C.log("R1", {k_: v for k_, v in out.items() if k_ in ("by_window", "pooled_checked", "pooled_checked_nav")})


if __name__ == "__main__":
    main()
