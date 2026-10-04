"""DQ10: fresh blind reference for Jev behavior states v3.1 (pre-registration: DESIGN.md, "Fresh blind reference on v3 states").

  uv run python infra/behavior_states/blind_reference_v3.py sample    # 200 non-holdout windows; two blind sheets (gated) + key
  uv run python infra/behavior_states/blind_reference_v3.py compare   # kappa, confusion, confidence bins vs behavior_states_v3

No Jev calls. Sheets hold the exact v3 state Jev saw (assemble_v3.state_dict), with no Jev output and no stratum; they live
under data/processed/behavior_states/blind_ref_v31/ (gitignored). The key (window ids, strata, weights) is a separate file.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "shared"))
import assemble_v3 as A  # noqa: E402
from common import OUT, holdout_mask  # noqa: E402
from label_v3 import BEHAVIORS  # noqa: E402

BR = OUT.parent / "behavior_states" / "blind_ref_v31"
SEED = 20261004
N = 200
STATES = list(BEHAVIORS)


def sample():
    b = pl.read_parquet(OUT / "behavior_states_v3.parquet",
                        columns=["pt_date", "agent", "w", "goal_no", "regime", "holdout", "active", "labeled", "state_chars"])
    b = b.filter(pl.col("active") & pl.col("labeled") & ~pl.col("holdout").fill_null(True))
    b = b.filter(~pl.Series(holdout_mask(b["pt_date"].cast(pl.Utf8).to_list(), b["goal_no"].to_list())))
    old = pl.read_ndjson(OUT.parent / "behavior_states" / "blind_draft.jsonl").select("pt_date", pl.col("agent").cast(pl.Int8), pl.col("w").cast(pl.Int16))
    b = b.join(old, on=["pt_date", "agent", "w"], how="anti")
    lab = pl.read_parquet(OUT / "roster.parquet", columns=["agent", "lab"])
    b = b.join(lab, on="agent", how="left").with_columns(
        pl.concat_str(pl.col("regime").cast(pl.Utf8), pl.lit("|"), pl.col("lab").fill_null("?")).alias("stratum"))
    Nst = dict(b.group_by("stratum").len().iter_rows())
    strata = sorted(Nst)
    k = N // len(strata)
    rng = np.random.default_rng(SEED)
    parts = []
    for s in strata:                                   # equal allocation (as the DQ3 draft); polars sampling by explicit index
        sub = b.filter(pl.col("stratum") == s).sort("pt_date", "agent", "w")
        ix = rng.choice(sub.height, size=min(k, sub.height), replace=False)
        parts.append(sub[np.sort(ix)])
    x = pl.concat(parts)
    rest = b.join(x.select("pt_date", "agent", "w"), on=["pt_date", "agent", "w"], how="anti").sort("pt_date", "agent", "w")
    if x.height < N:                                   # fill to N at random from the rest
        ix = rng.choice(rest.height, size=N - x.height, replace=False)
        x = pl.concat([x, rest[np.sort(ix)]])
    x = x.with_columns(pl.Series("_u", rng.random(x.height))).sort("_u").drop("_u").with_row_index("vid")
    x = x.with_columns(pl.when(pl.col("vid") % 2 == 0).then(pl.lit("A")).otherwise(pl.lit("B")).alias("sheet"))
    # the weight of a window = stratum population / stratum sample count
    ns = dict(x.group_by("stratum").len().iter_rows())
    x = x.with_columns((pl.col("stratum").replace_strict(Nst, return_dtype=pl.Float64)
                        / pl.col("stratum").replace_strict(ns, return_dtype=pl.Float64)).alias("w_pop"))
    f = A.features(x.select("pt_date", "agent", "w"))
    states = {(r["pt_date"], r["agent"], r["w"]): A.state_dict(r) for r in f.iter_rows(named=True)}
    BR.mkdir(parents=True, exist_ok=True)
    mism = 0
    files = {s: (BR / f"sheet_{s}.jsonl").open("w") for s in ("A", "B")}
    for r in x.iter_rows(named=True):
        st = states[(r["pt_date"], r["agent"], int(r["w"]))]
        mism += len(json.dumps(st, ensure_ascii=False)) != r["state_chars"]
        files[r["sheet"]].write(json.dumps({"vid": r["vid"], "state": st}, ensure_ascii=False) + "\n")
    for fh in files.values():
        fh.close()
    x.select("vid", "sheet", "pt_date", "agent", "w", "goal_no", "regime", "lab", "stratum", "w_pop").write_parquet(BR / "key.parquet")
    print(f"wrote 2 sheets ({x.height} windows, {len(strata)} strata, k={k}); state length differs from the labelled state in {mism} windows")


def kappa(a, b, w=None, cats=None) -> float:
    a, b = list(a), list(b)
    w = np.ones(len(a)) if w is None else np.asarray(w, float)
    cats = cats or sorted(set(a) | set(b))
    M = np.zeros((len(cats), len(cats)))
    for x, y, ww in zip(a, b, w):
        M[cats.index(x), cats.index(y)] += ww
    M /= M.sum()
    po, pe = np.trace(M), (M.sum(1) * M.sum(0)).sum()
    return float((po - pe) / (1 - pe)) if pe < 1 else float("nan")


def spearman(x, y) -> float:
    from scipy.stats import spearmanr
    return float(spearmanr(x, y).statistic)


def boot_kappa(V: pl.DataFrame, B: int = 2000, weighted: bool = False) -> list:
    rng = np.random.default_rng(SEED)
    vals = []
    j, c, w = V["j"].to_list(), V["c"].to_list(), V["w_pop"].to_numpy()
    n = len(j)
    for _ in range(B):
        ix = rng.integers(0, n, n)
        vals.append(kappa([j[i] for i in ix], [c[i] for i in ix], w[ix] if weighted else None))
    return [float(np.nanquantile(vals, 0.025)), float(np.nanquantile(vals, 0.975))]


def compare():
    key = pl.read_parquet(BR / "key.parquet")
    raw = []
    for s in ("A", "B"):
        raw += json.loads((BR / f"ref_labels_{s}.json").read_text())["labels"]
    cl = pl.DataFrame([{"vid": int(r["vid"]), "c": r["behavior"], "c2": r.get("second_choice"), "c_blocked": bool(r["blocked"]),
                        "c_others": bool(r["others_work"]), "c_progress": int(r["progress"]),
                        "c_addr": r.get("addresses_participant"), "c_amb": bool(r.get("ambiguous", False))} for r in raw],
                      schema={"vid": pl.UInt32, "c": pl.Utf8, "c2": pl.Utf8, "c_blocked": pl.Boolean, "c_others": pl.Boolean,
                              "c_progress": pl.Int8, "c_addr": pl.Boolean, "c_amb": pl.Boolean})
    bad = set(cl["c"].to_list()) - set(STATES)
    assert not bad, bad
    jv = pl.read_parquet(OUT / "behavior_states_v3.parquet").select(
        "pt_date", "agent", "w", pl.col("behavior").cast(pl.Utf8).alias("j"), "behavior_conf", *[f"p_{s}" for s in STATES],
        "p_blocked", "p_others_work", "p_addresses_participant", "progress_score", "has_chat")
    V = key.join(cl, on="vid").join(jv, on=["pt_date", "agent", "w"], how="left")
    P = V.select([f"p_{s}" for s in STATES]).to_numpy()
    top2 = [{STATES[i] for i in np.argsort(-row)[:2]} for row in P]
    V = V.with_columns(pl.Series("top2_hit", [c in t for c, t in zip(V["c"].to_list(), top2)]),
                       pl.Series("ref2_hit", [(j == c) or (j == c2) for j, c, c2 in zip(V["j"].to_list(), V["c"].to_list(), V["c2"].to_list())]))
    res = {"computed_at": dt.datetime.now(dt.timezone.utc).isoformat(), "n": V.height, "n_ambiguous": int(V["c_amb"].sum())}
    w = V["w_pop"].to_list()
    res["behavior"] = {"kappa_raw": kappa(V["j"], V["c"]), "kappa_raw_ci": boot_kappa(V),
                       "kappa_reweighted": kappa(V["j"], V["c"], w), "kappa_reweighted_ci": boot_kappa(V, weighted=True),
                       "agree_raw": float((V["j"] == V["c"]).mean()),
                       "agree_reweighted": float(V.filter(pl.col("j") == pl.col("c"))["w_pop"].sum() / V["w_pop"].sum()),
                       "jev_top2_contains_ref": float(V["top2_hit"].mean()),
                       "ref_top2_contains_jev": float(V["ref2_hit"].mean())}
    U = V.filter(~pl.col("c_amb"))
    res["behavior"]["unambiguous"] = {"n": U.height, "kappa": kappa(U["j"], U["c"]), "agree": float((U["j"] == U["c"]).mean())}
    res["by_conf"] = {}
    for lo, hi in ((0.8, 1.01), (0.5, 0.8), (0.0, 0.5)):
        d = V.filter(pl.col("behavior_conf").is_between(lo, hi, closed="left"))
        res["by_conf"][f"{lo}-{hi}"] = {"n": d.height, "agree": float((d["j"] == d["c"]).mean()) if d.height else None,
                                        "kappa": kappa(d["j"], d["c"]) if d.height > 5 else None}
    res["by_regime"] = {r: {"n": d.height, "kappa": kappa(d["j"], d["c"]), "agree": float((d["j"] == d["c"]).mean())}
                        for (r,), d in V.group_by(["regime"]) for r in [str(r)]}
    res["by_labeler"] = {s: {"n": d.height, "kappa": kappa(d["j"], d["c"]), "agree": float((d["j"] == d["c"]).mean())}
                         for (s,), d in V.group_by(["sheet"])}
    res["per_class"] = {s: {"jev_n": int((V["j"] == s).sum()), "ref_n": int((V["c"] == s).sum()),
                            "precision": (float(((V["j"] == s) & (V["c"] == s)).sum() / (V["j"] == s).sum()) if (V["j"] == s).sum() else None),
                            "recall": (float(((V["j"] == s) & (V["c"] == s)).sum() / (V["c"] == s).sum()) if (V["c"] == s).sum() else None)}
                        for s in STATES}
    res["confusion_jev_rows_ref_cols"] = {a: {b: int(((V["j"] == a) & (V["c"] == b)).sum()) for b in STATES} for a in STATES}
    res["blocked"] = {"kappa": kappa((V["p_blocked"] >= 0.5).to_list(), V["c_blocked"].to_list()),
                      "agree": float(((V["p_blocked"] >= 0.5) == V["c_blocked"]).mean()),
                      "ref_rate": float(V["c_blocked"].mean()), "jev_rate": float((V["p_blocked"] >= 0.5).mean())}
    res["others_work"] = {"kappa": kappa((V["p_others_work"] >= 0.5).to_list(), V["c_others"].to_list()),
                          "agree": float(((V["p_others_work"] >= 0.5) == V["c_others"]).mean()),
                          "ref_rate": float(V["c_others"].mean()), "jev_rate": float((V["p_others_work"] >= 0.5).mean())}
    ch = V.filter(pl.col("p_addresses_participant").is_not_null() & pl.col("c_addr").is_not_null())
    res["addresses_participant"] = {"n": ch.height, "kappa": kappa((ch["p_addresses_participant"] >= 0.5).to_list(), ch["c_addr"].to_list()) if ch.height else None}
    res["progress"] = {"spearman": spearman(V["progress_score"].to_numpy(), V["c_progress"].to_numpy()),
                       "mean_jev": float(V["progress_score"].mean()), "mean_ref": float(V["c_progress"].mean())}
    # second, independent blind run of the same sheets (an earlier labeler launch whose output was kept): inter-rater ceiling
    r2 = []
    for s in ("A", "B"):
        f = BR / f"ref2_labels_{s}_original.json"
        if f.exists():
            r2 += json.loads(f.read_text())["labels"]
    if r2:
        c2 = pl.DataFrame([{"vid": int(r["vid"]), "c_alt": r["behavior"], "c_alt_blocked": bool(r["blocked"])} for r in r2],
                          schema={"vid": pl.UInt32, "c_alt": pl.Utf8, "c_alt_blocked": pl.Boolean})
        W = V.join(c2, on="vid")
        res["inter_rater"] = {"n": W.height, "ref_vs_ref2_kappa": kappa(W["c"], W["c_alt"]),
                              "ref_vs_ref2_agree": float((W["c"] == W["c_alt"]).mean()),
                              "jev_vs_ref2_kappa": kappa(W["j"], W["c_alt"]), "jev_vs_ref_kappa_same_items": kappa(W["j"], W["c"]),
                              "ref_vs_ref2_blocked_kappa": kappa(W["c_blocked"].to_list(), W["c_alt_blocked"].to_list()),
                              "jev_vs_either_ref": float(((W["j"] == W["c"]) | (W["j"] == W["c_alt"])).mean()),
                              "jev_vs_ref_when_refs_agree": {"n": int((W["c"] == W["c_alt"]).sum()),
                                                             "agree": float((W.filter(pl.col("c") == pl.col("c_alt"))["j"] == W.filter(pl.col("c") == pl.col("c_alt"))["c"]).mean())}}
    k = res["behavior"]["kappa_raw"]
    a8 = res["by_conf"]["0.8-1.01"]["agree"] or 0
    res["reading"] = "confirmed" if (k >= 0.5 and a8 >= 0.8) else ("weak" if k >= 0.4 else "fails")
    res["distribution"] = {"jev": {s: int((V["j"] == s).sum()) for s in STATES}, "ref": {s: int((V["c"] == s).sum()) for s in STATES}}
    (BR / "results.json").write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps(res, indent=1, default=str))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["sample", "compare"])
    a = ap.parse_args()
    sample() if a.cmd == "sample" else compare()


if __name__ == "__main__":
    main()
