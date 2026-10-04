"""H12 round 1b, period-native tests (DQ9 cross-index). Predictions were written in the folders before this ran:
  G12  goalperiod-subhypotheses/G12/README.md   motion on (debate phase) vs off (20 min after the verdict), 10 debates
  G26  goalperiod-subhypotheses/G26/README.md   PR in the 30-min windows that open at the two vote instants vs all
                                               other 30-min windows of #26
Ground truth: shared ground_truth_labels (DQ6): #12 `phase` rows (deb, pre), #26 `phase` rows (approval_vote,
confirmatory_vote). Statements: H12's regime-whitened d = 32 bge vectors (primary) and the shared unit-normalized
32-d vectors of bge and gte (model check). Chat only. No text is read.
Output: data/processed/H12-groupthink-dimensional-collapse/r1b/native/{native.json, g12_debates.parquet, g26_windows.parquet}.
Usage: uv run python hypotheses/H12-groupthink-dimensional-collapse/analysis/r1b_native.py
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("H12_DATA_VERSION", "fixed")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import h12lib as L  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy.stats import wilcoxon  # noqa: E402

import r1b_dq5 as Q  # noqa: E402

OUT = L.OUTV / "native"
D = 32


def vectors():
    m = Q.stmt_map()
    V = {"bge_h12": np.load(L.OUT / "stmt_white_d64.npy", mmap_mode="r")[:, :D].astype(np.float64)}
    for k, f in Q.MODELS.items():
        V[f"{k}_shared"] = np.asarray(np.load(L.SH / "embeddings" / f, mmap_mode="r")[m["srow"].to_numpy()], np.float64)
    return m, V


def g12(m, V, rng) -> tuple[dict, pl.DataFrame]:
    gt = pl.read_parquet(L.SH / "ground_truth_labels.parquet").filter((pl.col("goal_no") == 12) & (pl.col("label_kind") == "phase"))
    deb = gt.filter(pl.col("value") == "deb").sort("t_valid_from")
    pre = gt.filter(pl.col("value") == "pre").sort("t_valid_from")
    ch = m.filter((pl.col("kind") == "chat") & (pl.col("goal_no") == 12))
    rows = []
    for r in deb.iter_rows(named=True):
        on0, on1 = r["t_valid_from"], r["t_valid_to"]
        nxt = pre.filter(pl.col("t_valid_from") > on1)["t_valid_from"]
        off1 = min(on1 + dt.timedelta(minutes=20), nxt[0]) if nxt.len() else on1 + dt.timedelta(minutes=20)
        x_on = ch.filter((pl.col("t") >= on0) & (pl.col("t") < on1))
        x_off = ch.filter((pl.col("t") >= on1) & (pl.col("t") < off1))
        row = {"debate": r["unit"], "n_on": x_on.height, "n_off": x_off.height, "on_min": (on1 - on0).total_seconds() / 60,
               "off_min": (off1 - on1).total_seconds() / 60}
        for vk, W in V.items():
            for side, x in (("on", x_on), ("off", x_off)):
                rr = L.pr_rarefied(W[x["row"].to_numpy()], x["agent"].to_numpy(), 12, 4, 100, rng, erank=False) if x.height else {"pr": np.nan, "tv": np.nan}
                row[f"pr_{side}_{vk}"] = rr["pr"]; row[f"tv_{side}_{vk}"] = rr["tv"]
        rows.append(row)
    df = pl.DataFrame(rows)
    res = {"n_debates": df.height}
    for vk in V:
        ok = df.filter(pl.col(f"pr_on_{vk}").is_not_nan() & pl.col(f"pr_off_{vk}").is_not_nan())
        d = (ok[f"pr_on_{vk}"] - ok[f"pr_off_{vk}"]).to_numpy()
        dtv = (ok[f"tv_on_{vk}"] - ok[f"tv_off_{vk}"]).to_numpy()
        res[vk] = {"n_usable": int(len(d)), "n_on_lower": int((d < 0).sum()), "median_diff": float(np.median(d)) if len(d) else None,
                   "median_rel": float(np.median(d / ok[f"pr_off_{vk}"].to_numpy())) if len(d) else None,
                   "wilcoxon_p_less": float(wilcoxon(d, alternative="less").pvalue) if len(d) >= 5 else None,
                   "n_tv_on_lower": int((dtv < 0).sum()), "median_tv_diff": float(np.median(dtv)) if len(d) else None}
    p = res["bge_h12"]
    n12a = p["n_usable"] > 0 and p["n_on_lower"] >= 7 and (p["wilcoxon_p_less"] or 1) < 0.05
    n12c = res["gte_shared"]["median_diff"] is not None and np.sign(res["gte_shared"]["median_diff"]) == np.sign(p["median_diff"])
    res["N12a"], res["N12b"] = bool(n12a), bool(p["n_tv_on_lower"] > p["n_usable"] / 2)
    res["N12c"] = bool(n12c)
    res["verdict"] = "supported" if (n12a and n12c) else ("failed" if (p["median_diff"] is None or p["median_diff"] >= 0) else "mixed")
    return res, df


def g26(m, V, rng) -> tuple[dict, pl.DataFrame]:
    gt = pl.read_parquet(L.SH / "ground_truth_labels.parquet").filter((pl.col("goal_no") == 26) & (pl.col("label_kind") == "phase"))
    t1 = gt.filter(pl.col("value") == "approval_vote")["t_valid_from"].min()
    t2 = gt.filter(pl.col("value") == "confirmatory_vote")["t_valid_from"].min()
    ev = {"E1": (t1, t1 + dt.timedelta(minutes=30)), "E2": (t2, t2 + dt.timedelta(minutes=30))}
    cal = pl.read_parquet(L.SH / "calendar.parquet").filter(pl.col("goal_no") == 26).select("pt_date", "win_start")
    ch = m.filter((pl.col("kind") == "chat") & (pl.col("goal_no") == 26)).join(cal, on="pt_date")
    ch = ch.with_columns((pl.col("win_start") + pl.duration(minutes=30 * pl.col("win30").cast(pl.Int64))).alias("w0"))
    # reference windows: H12's win30 grid, excluding windows that overlap an event window
    ref = ch.group_by("pt_date", "win30", "w0").agg(pl.len().alias("n"))
    ref = ref.with_columns((pl.col("w0") + pl.duration(minutes=30)).alias("w1"))
    for a, b in ev.values():
        ref = ref.filter(~((pl.col("w0") < b) & (pl.col("w1") > a)))
    res, rows = {"event_windows": {k: [str(a), str(b)] for k, (a, b) in ev.items()}}, []
    # n: 30 if both event windows have >= 30 capped statements, else 20
    def capped(x):
        _, c = np.unique(x["agent"].to_numpy(), return_counts=True)
        return int(np.minimum(c, 8).sum())
    xe = {k: ch.filter((pl.col("t") >= a) & (pl.col("t") < b)) for k, (a, b) in ev.items()}
    n = 30 if all(capped(x) >= 30 for x in xe.values()) else 20
    res["n_rarefied"] = n
    res["event_counts"] = {k: {"n_chat": x.height, "n_capped": capped(x), "n_agents": x["agent"].n_unique()} for k, x in xe.items()}
    for vk, W in V.items():
        refv = []
        for r in ref.iter_rows(named=True):
            x = ch.filter((pl.col("pt_date") == r["pt_date"]) & (pl.col("win30") == r["win30"]))
            rr = L.pr_rarefied(W[x["row"].to_numpy()], x["agent"].to_numpy(), n, 8, 20, rng, erank=False)
            refv.append((rr["pr"], rr["tv"]))
            rows.append({"model": vk, "kind": "ref", "pt_date": r["pt_date"], "win30": r["win30"], "pr": rr["pr"], "tv": rr["tv"]})
        rp = np.array([a for a, _ in refv if a == a]); rt = np.array([b for a, b in refv if a == a])
        out = {"n_ref": int(len(rp)), "ref_q25": float(np.quantile(rp, 0.25)), "ref_median": float(np.median(rp)),
               "ref_tv_median": float(np.median(rt))}
        for k, x in xe.items():
            rr = L.pr_rarefied(W[x["row"].to_numpy()], x["agent"].to_numpy(), n, 8, 20, rng, erank=False)
            out[k] = {"pr": rr["pr"], "tv": rr["tv"], "pct": float((rp < rr["pr"]).mean()) if rr["pr"] == rr["pr"] else None,
                      "tv_pct": float((rt < rr["tv"]).mean()) if rr["tv"] == rr["tv"] else None}
            rows.append({"model": vk, "kind": k, "pt_date": str(ev[k][0].date()), "win30": None, "pr": rr["pr"], "tv": rr["tv"]})
        res[vk] = out
    p = res["bge_h12"]
    n26a = all(p[k]["pr"] == p[k]["pr"] and p[k]["pr"] < p["ref_q25"] for k in ev)
    n26b = all(p[k]["tv"] == p[k]["tv"] and p[k]["tv"] < p["ref_tv_median"] for k in ev)
    n26c = all(res["gte_shared"][k]["pct"] is not None and res["gte_shared"][k]["pct"] < 0.5 for k in ev)
    both_above = all(p[k]["pct"] is not None and p[k]["pct"] >= 0.5 for k in ev)
    res["N26a"], res["N26b"], res["N26c"] = bool(n26a), bool(n26b), bool(n26c)
    res["verdict"] = "supported" if (n26a and n26c) else ("failed" if both_above else "mixed")
    return res, pl.DataFrame(rows, infer_schema_length=None)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    m, V = vectors()
    r12, d12 = g12(m, V, np.random.default_rng([L.SEED, 12, 1]))
    d12.write_parquet(OUT / "g12_debates.parquet")
    r26, d26 = g26(m, V, np.random.default_rng([L.SEED, 26, 1]))
    d26.write_parquet(OUT / "g26_windows.parquet")
    R = {"G12_motion": r12, "G26_votes": r26}
    (OUT / "native.json").write_text(json.dumps(R, indent=1, default=float))
    L.write_provenance("hypotheses/H12-groupthink-dimensional-collapse/analysis/r1b_native.py",
                       ["shared ground_truth_labels (phase), embeddings/statements, statements_white32_{bge_small,gte_modernbert}; H12 stmt_index, stmt_white_d64"],
                       {"G12": "PR n=12 cap 4, 100 draws; off = verdict -> +20 min (cut at next pre phase)",
                        "G26": "PR30 estimator (cap 8, n 30 or 20, 20 draws); events = 30 min from each vote start"},
                       path=L.OUTV / "_provenance.json")
    print(json.dumps(R, indent=1, default=float))


if __name__ == "__main__":
    main()
