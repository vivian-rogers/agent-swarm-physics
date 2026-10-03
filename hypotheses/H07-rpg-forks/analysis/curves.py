"""H07 exploratory analysis (non-holdout only): divergence curves, clocks, decomposition, shared innovations.

Usage: uv run python hypotheses/H07-rpg-forks/analysis/curves.py
Outputs (data/processed/H07-rpg-forks/): curves_commit.parquet, curves_day.parquet, horizontal_day.parquet,
clock_fits.parquet, shared_innovations.parquet, results.json
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import polars as pl
from scipy.optimize import curve_fit

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h07lib import (ABSENT, F_REGIME, FEATURES, P, ROOT, SETS, SH, T0, T35_END, Features, horizontal, load_trees,
                    set_stats, transform_test, vertical)

sys.path.insert(0, str(ROOT / "infra/shared"))
from common import holdout_mask  # noqa: E402

REPO = {"origin": "rpg-game", "best": "rpg-game-best", "rest": "rpg-game-rest", "restweek": "rpg-game-rest-week"}
N_NULL = 100


def git(repo, *a):
    return subprocess.run(["git", "-C", str(ROOT / "data/raw/repos" / f"{repo}.git"), *a], capture_output=True,
                          text=True, check=True).stdout


def main():
    res: dict = {}
    snaps, trees = load_trees()
    feats = Features()
    commits = pl.read_parquet(P / "commits.parquet")
    cal = pl.read_parquet(SH / "calendar.parquet")
    held = dict(zip(cal["pt_date"].to_list(), cal["holdout"].to_list()))
    A = snaps.filter(pl.col("lineage") == "ancestor")["sha"][0]
    KA, SA = feats.of_tree(trees[A])
    res["ancestor"] = {"sha": A, "n_files": len(KA["files"]), **{f"n_{f}": len(KA[f]) for f in FEATURES},
                       **{f"n_{s}": len(SA[s]) for s in SETS}}
    # holdout guard: no commit of any lineage on a held-out PT day is analyzed
    cpt = commits.with_columns(pl.col("t_commit").dt.convert_time_zone("America/Los_Angeles").dt.date()
                               .cast(pl.Utf8).alias("pt_date"), pl.col("t_commit").alias("t"))
    gno = {d: g for d, g in zip(cal["pt_date"].to_list(), cal["goal_no"].to_list())}
    cpt = cpt.with_columns(pl.Series("held", holdout_mask(cpt["pt_date"].to_list(),
                                                          [gno.get(d, -1) for d in cpt["pt_date"].to_list()])))
    res["commits_on_holdout_days"] = int(cpt["held"].sum())
    held_shas = set(cpt.filter(pl.col("held"))["sha"].to_list())

    # cumulative file-touches (exact ancestry) per snapshot
    cf = pl.read_parquet(P / "commit_files.parquet").group_by("lineage", "sha").len()
    touches = {(l, s): n for l, s, n in cf.iter_rows()}
    rows = []
    feat_cache = {A: (KA, SA)}
    for lin, sha, k, t, ncom, ah in snaps.filter(pl.col("lineage") != "ancestor").iter_rows():
        if sha in held_shas:
            continue
        anc = git(REPO[lin], "rev-list", "--no-merges", f"{A}..{sha}").split()
        ntouch = sum(touches.get((lin, s), 0) for s in anc)
        if sha not in feat_cache:
            feat_cache[sha] = feats.of_tree(trees[sha])
        K, S = feat_cache[sha]
        rec = {"lineage": lin, "sha": sha, "k": k, "t": t, "n_commits": ncom, "n_touches": ntouch, "active_h": ah}
        for f in FEATURES:
            v = vertical(KA[f], K[f])
            rec.update({f"{f}_c": v["c"], f"{f}_kappa": v["kappa"], f"{f}_I": v["I"], f"{f}_Icopy": v["I_copy"],
                        f"{f}_H": v["H_x"], f"{f}_new": len(set(K[f]) - set(KA[f]))})
        for s in SETS:
            st = set_stats(SA[s], S[s])
            rec.update({f"{s}_survival": st["survival"], f"{s}_innov": st["innovations"], f"{s}_jaccard": st["jaccard"]})
        rows.append(rec)
    cc = pl.DataFrame(rows).sort("lineage", "k")
    cc.write_parquet(P / "curves_commit.parquet")

    # ---------------------------------------------------------------- day snapshots (vertical + horizontal, with nulls)
    ds = pl.read_parquet(P / "day_snapshots.parquet")
    ds = ds.with_columns(pl.col("pt_date").replace_strict(held, default=False).alias("holdout"))
    ds = ds.filter(~pl.col("holdout"))
    dec_cache: dict = {}
    drows = []
    for lin, d, sha, ah in ds.select("lineage", "pt_date", "sha", "active_h").iter_rows():
        if sha not in feat_cache:
            feat_cache[sha] = feats.of_tree(trees[sha]) if sha in trees else (KA, SA)
        K, S = feat_cache[sha]
        rec = {"lineage": lin, "pt_date": d, "sha": sha, "active_h": ah}
        for f in FEATURES:
            key = ("v", sha, f)
            if key not in dec_cache:
                dec_cache[key] = vertical(KA[f], K[f], n_null=N_NULL)
            for m in ("c", "kappa", "I", "I_copy", "I_transform", "I_ex", "I_copy_ex", "I_transform_ex",
                      "I_transform_null_sd", "H_x"):
                rec[f"{f}_{m}"] = dec_cache[key].get(m)
        for s in SETS:
            st = set_stats(SA[s], S[s])
            rec.update({f"{s}_survival": st["survival"], f"{s}_innov": st["innovations"]})
        if lin in ("best", "rest"):
            for f in ("numbers_data", "entities", "names", "functions"):
                key = ("t", sha, f)
                if key not in dec_cache:
                    dec_cache[key] = transform_test(KA[f], K[f], n_null=N_NULL)
                tt = dec_cache[key]
                rec[f"{f}_Itr_cx"] = tt.get("I_transform_cx")
                rec[f"{f}_Itr_z"] = tt.get("z")
                rec[f"{f}_rep_map"] = tt.get("repeated_mapping_frac")
        drows.append(rec)
    cd = pl.DataFrame(drows).sort("lineage", "pt_date")
    cd.write_parquet(P / "curves_day.parquet")

    # horizontal best(d) vs rest(d)
    b = dict(ds.filter(pl.col("lineage") == "best").select("pt_date", "sha").iter_rows())
    r = dict(ds.filter(pl.col("lineage") == "rest").select("pt_date", "sha").iter_rows())
    hrows = []
    t0rec = {"pt_date": "T0", "sha_best": A, "sha_rest": A}
    for f in FEATURES:
        h = horizontal(KA[f], KA[f], n_null=N_NULL)
        for m in ("n", "c", "kappa", "I", "I_copy", "I_transform", "I_ex", "I_copy_ex", "I_transform_ex", "H_x"):
            t0rec[f"{f}_{m}"] = h.get(m)
    hrows.append(t0rec)
    for d in sorted(set(b) | set(r)):
        sb, sr = b.get(d), r.get(d)
        if sb is None:  # best has stopped: carry its last state
            sb = b[max(x for x in b if x <= d)]
        if sr is None:
            sr = r[max(x for x in r if x <= d)]
        Kb, Sb = feat_cache[sb]
        Kr, Sr = feat_cache[sr]
        rec = {"pt_date": d, "sha_best": sb, "sha_rest": sr}
        for f in FEATURES:
            key = ("h", sb, sr, f)
            if key not in dec_cache:
                dec_cache[key] = horizontal(Kb[f], Kr[f], n_null=N_NULL)
            h = dec_cache[key]
            for m in ("n", "c", "kappa", "I", "I_copy", "I_transform", "I_ex", "I_copy_ex", "I_transform_ex", "H_x"):
                rec[f"{f}_{m}"] = h.get(m)
            # on ancestor keys: identity vs. both-unchanged (independent-lineage bound)
            keys = list(KA[f])
            xb = np.array([Kb[f].get(k, ABSENT) == KA[f][k] for k in keys])
            xr = np.array([Kr[f].get(k, ABSENT) == KA[f][k] for k in keys])
            same = np.array([Kb[f].get(k, ABSENT) == Kr[f].get(k, ABSENT) for k in keys])
            rec[f"{f}_anc_same"] = float(same.mean())
            rec[f"{f}_anc_both_unch"] = float((xb & xr).mean())
            rec[f"{f}_anc_prod"] = float(xb.mean() * xr.mean())
            rec[f"{f}_anc_both_changed_same"] = int((same & ~xb & ~xr).sum())
            rec[f"{f}_anc_both_changed"] = int((~xb & ~xr).sum())
        for s in SETS:
            rec[f"{s}_shared_new"] = len((Sb[s] & Sr[s]) - SA[s])
            rec[f"{s}_new_best"] = len(Sb[s] - SA[s])
            rec[f"{s}_new_rest"] = len(Sr[s] - SA[s])
        hrows.append(rec)
    hd = pl.DataFrame(hrows).sort("pt_date")
    hd.write_parquet(P / "horizontal_day.parquet")

    # ---------------------------------------------------------------- clocks (#35 window)
    fits = []
    w35 = cc.filter(pl.col("t") <= T35_END)

    def m1(x, mu):
        return np.exp(-mu * x)

    def m2(x, f, mu):
        return f + (1 - f) * np.exp(-mu * x)
    for lin in ("best", "rest"):
        g = w35.filter(pl.col("lineage") == lin)
        for f in ("files", "files_src", "functions", "numbers_data", "names"):
            y = np.concatenate([[1.0], g[f"{f}_c"].to_numpy()])
            for clock in ("n_commits", "n_touches", "active_h"):
                x = np.concatenate([[0.0], g[clock].to_numpy().astype(float)])
                n = len(x)
                p1, _ = curve_fit(m1, x, y, p0=[0.01], bounds=([0], [10]))
                rss1 = float(np.sum((y - m1(x, *p1)) ** 2))
                try:
                    p2, _ = curve_fit(m2, x, y, p0=[0.5, 0.05], bounds=([0, 0], [1, 10]))
                    rss2 = float(np.sum((y - m2(x, *p2)) ** 2))
                except RuntimeError:
                    p2, rss2 = [np.nan, np.nan], np.nan
                fits.append({"lineage": lin, "feature": f, "clock": clock, "n": n, "mu1": float(p1[0]), "rss1": rss1,
                             "bic1": n * np.log(rss1 / n) + 1 * np.log(n), "f2": float(p2[0]), "mu2": float(p2[1]),
                             "rss2": rss2, "bic2": n * np.log(rss2 / n) + 2 * np.log(n) if rss2 == rss2 else np.nan,
                             "x_end": float(x[-1]), "c_end": float(y[-1])})
    fits = pl.DataFrame(fits)
    fits.write_parquet(P / "clock_fits.parquet")

    # ---------------------------------------------------------------- P1: largest single first-parent step
    p1 = {}
    for lin in ("best", "rest"):
        g = w35.filter(pl.col("lineage") == lin).sort("k")
        dvec = 1 - np.concatenate([[1.0], g["files_c"].to_numpy()])
        steps = np.diff(dvec)
        i = int(np.argmax(steps))
        sha = g["sha"][i]
        cm = commits.filter((pl.col("lineage") == lin) & (pl.col("sha") == sha))
        p1[lin] = {"d_end": float(dvec[-1]), "max_step": float(steps[i]), "share": float(steps[i] / dvec[-1]),
                   "sha": sha, "is_merge": bool(cm["is_merge"][0]), "author": cm["author"][0],
                   "src_max_step_share": float(np.max(np.diff(1 - np.concatenate([[1.0], g["files_src_c"].to_numpy()])))
                                               / (1 - g["files_src_c"][-1]))}
    res["P1_steps"] = p1

    # ---------------------------------------------------------------- shared innovations (best & rest, end state and over time)
    first_seen = {}
    for lin in ("best", "rest"):
        g = cc.filter(pl.col("lineage") == lin).sort("k")
        for sha, t in g.select("sha", "t").iter_rows():
            K, S = feat_cache.get(sha) or feats.of_tree(trees[sha])
            for f in ("files", "functions", "names", "numbers_data"):
                for key, v in K[f].items():
                    if KA[f].get(key, ABSENT) != v:
                        first_seen.setdefault((lin, f, key, v), (t, sha))
            for s in SETS:
                for v in S[s] - SA[s]:
                    first_seen.setdefault((lin, s, None, v), (t, sha))
    sh = []
    keyset = {}
    for (lin, f, key, v), (t, sha) in first_seen.items():
        keyset.setdefault((f, key, v), {})[lin] = (t, sha)
    for (f, key, v), d in keyset.items():
        if "best" in d and "rest" in d:
            (tb, sb), (tr, sr) = d["best"], d["rest"]
            sh.append({"feature": f, "key": key, "value": str(v)[:120], "t_best": tb, "sha_best": sb, "t_rest": tr,
                       "sha_rest": sr, "first": "best" if tb < tr else "rest", "lag_h": abs((tr - tb).total_seconds()) / 3600})
    shdf = pl.DataFrame(sh, infer_schema_length=None) if sh else pl.DataFrame()
    if len(shdf):
        auth = commits.select("lineage", "sha", "author", "agent", "author_room_name")
        shdf = shdf.join(auth.filter(pl.col("lineage") == "best").select(pl.col("sha").alias("sha_best"),
                                                                         pl.col("author").alias("author_best")),
                         on="sha_best", how="left").join(
            auth.filter(pl.col("lineage") == "rest").select(pl.col("sha").alias("sha_rest"),
                                                            pl.col("author").alias("author_rest")),
            on="sha_rest", how="left")
        shdf.write_parquet(P / "shared_innovations.parquet")
    res["shared_innovations_by_feature"] = (shdf.group_by("feature").agg(pl.len().alias("n"),
                                            (pl.col("t_best") <= T35_END).sum().alias("by_best_in_35"))
                                            .to_dicts() if len(shdf) else [])
    # P4: horizontal drop during #35 vs. change afterwards (non-holdout days only)
    h0 = hd.filter(pl.col("pt_date") == "T0")
    hdd = hd.filter(pl.col("pt_date") != "T0")
    end35 = hdd.filter(pl.col("pt_date") <= "2026-03-22").sort("pt_date").tail(1)
    last = hdd.sort("pt_date").tail(1)
    p4 = {}
    for f in FEATURES:
        v0, v1, v2 = h0[f"{f}_I_copy_ex"][0], end35[f"{f}_I_copy_ex"][0], last[f"{f}_I_copy_ex"][0]
        seq = hdd.filter(pl.col("pt_date") <= "2026-03-20").sort("pt_date")[f"{f}_I_copy_ex"].to_list()
        p4[f] = {"T0": v0, "end35": v1, "last": v2, "drop35": v0 - v1, "post": v1 - v2,
                 "post_over_drop": (v1 - v2) / (v0 - v1) if v0 != v1 else None,
                 "monotone_daily_35": bool(all(a >= b for a, b in zip([v0] + seq, seq)))}
    res["P4_horizontal"] = p4
    # commit activity per active day: #35 vs later goal periods (non-holdout days)
    nm = cpt.filter(~pl.col("is_merge") & pl.col("lineage").is_in(["best", "rest"]))
    act = cal.filter((pl.col("pt_date") >= "2026-03-16") & (pl.col("pt_date") <= "2026-05-29") & ~pl.col("holdout")
                     & (pl.col("n_agent_events") > 0)).select("pt_date", "goal_no")
    per = nm.group_by("pt_date").len().join(act, on="pt_date", how="right").fill_null(0)
    res["commits_per_active_day"] = (per.with_columns(pl.when(pl.col("goal_no") == 35).then(pl.lit("35"))
                                                      .when(pl.col("goal_no") == 36).then(pl.lit("36"))
                                                      .when(pl.col("goal_no") == 37).then(pl.lit("37"))
                                                      .otherwise(pl.lit("38+")).alias("period"))
                                     .group_by("period").agg(pl.col("len").sum().alias("commits"),
                                                             pl.len().alias("active_days"))
                                     .with_columns((pl.col("commits") / pl.col("active_days")).alias("per_day"))
                                     .sort("period").to_dicts())
    (P / "results.json").write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
