"""H55 correction-marker validation against blind labels (codes only).

Precision per sensor from all items it flags (random + enriched strata are both draws from the flagged population for
the enriched sensor; the random stratum is a draw from all addressed messages). Recall and base rate are reweighted
to population shares: each stratum's items get weight = (population size of the stratum) / (items drawn).
  uv run python hypotheses/H55-norm-enforcer-immunity/analysis/validate.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import h55common as H  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (float(c - h), float(c + h))


def kappa(a, b):
    a, b = np.asarray(a), np.asarray(b)
    po = (a == b).mean()
    pe = sum((a == k).mean() * (b == k).mean() for k in np.unique(np.r_[a, b]))
    return float((po - pe) / (1 - pe)) if pe < 1 else float("nan")


def main():
    vd = H.OUT / "validation"
    key = pl.read_parquet(vd / "sample_key.parquet")
    lab = json.load(open(vd / "blind_labels.json"))["labels"]
    key = key.with_columns(pl.Series("truth", [lab[str(i)] for i in key["item"]]))
    key = key.with_columns((pl.col("truth") != "none").alias("C"))
    m = pl.read_parquet(H.OUT / "messages.parquet").filter((pl.col("speaker_kind") == "agent") & pl.col("addressed"))
    N_all, N_lex, N_jev = m.height, m["corr_lex"].sum(), m["corr_jev"].sum()
    # population weights: random stratum represents all addressed messages; lex stratum the lex-positive not in random;
    # jev stratum the jev-positive not in random/lex. Use a Horvitz-Thompson style weight per item.
    n_r = key.filter(pl.col("stratum") == "random").height
    n_l = key.filter(pl.col("stratum") == "lex").height
    n_j = key.filter(pl.col("stratum") == "jev").height
    res = {"n_items": key.height, "n_random": n_r, "n_lex": n_l, "n_jev": n_j,
           "population": {"addressed_agent_msgs": N_all, "lex_pos": int(N_lex), "jev_pos": int(N_jev)}}
    # precision: all flagged items (random flagged + enriched)
    for sens in ("corr_lex", "corr_jev", "lex_corr", "lex_norm", "lex_decl"):
        f = key.filter(pl.col(sens) & (pl.col("addressed") if "addressed" in key.columns else True)) if False else key.filter(pl.col(sens))
        k = int(f["C"].sum())
        res[f"precision_{sens}"] = {"k": k, "n": f.height, "p": k / f.height if f.height else None, "ci": wilson(k, f.height)}
    # subtype-specific precision (truth subtype matches family)
    for fam, t in (("lex_corr", "corr"), ("lex_norm", "norm"), ("lex_decl", "decl")):
        f = key.filter(pl.col(fam))
        res[f"precision_{fam}_same_subtype"] = {"k": int((f["truth"] == t).sum()), "n": f.height}
    # random stratum: base rate, recall (unweighted from random only) + reweighted
    r = key.filter(pl.col("stratum") == "random")
    res["random_base_rate_C"] = {"k": int(r["C"].sum()), "n": r.height, "ci": wilson(int(r["C"].sum()), r.height)}
    res["random_lex_rate"] = float(r["corr_lex"].mean())
    for sens in ("corr_lex", "corr_jev"):
        rc = r.filter(pl.col("C"))
        res[f"recall_random_{sens}"] = {"k": int(rc[sens].sum()), "n": rc.height}
        res[f"kappa_random_{sens}"] = kappa(r[sens].cast(int).to_numpy(), r["C"].cast(int).to_numpy())
    # combined sensor (lex OR jev)
    key = key.with_columns((pl.col("corr_lex") | pl.col("corr_jev")).alias("either"), (pl.col("corr_lex") & pl.col("corr_jev")).alias("both"))
    for sens in ("either", "both"):
        f = key.filter(pl.col(sens))
        res[f"precision_{sens}"] = {"k": int(f["C"].sum()), "n": f.height, "ci": wilson(int(f["C"].sum()), f.height)}
    # reweighted population estimates (HT): P(C), recall of lex
    # strata: random (all), lex (lex-pos minus random), jev (jev-pos & ~lex minus random)
    w = []
    for s, lx, jv in key.select("stratum", "corr_lex", "corr_jev").iter_rows():
        if s == "random":
            w.append(N_all / n_r)
        else:
            w.append(0.0)  # enriched items are used for precision only; recall uses random + lex-split estimator below
    key = key.with_columns(pl.Series("w", w))
    # precision-weighted recall estimator: recall_lex = P(lex & C) / P(C); P(lex & C) = P(lex) * prec_lex
    p_lex = N_lex / N_all
    prec = res["precision_corr_lex"]["p"]
    pc_r = r["C"].mean()
    # P(C & ~lex) from random stratum items that are not lex
    rn = r.filter(~pl.col("corr_lex"))
    p_c_notlex = float(rn["C"].mean()) * (1 - p_lex) if rn.height else float("nan")
    p_c_lex = p_lex * prec
    res["population_estimates"] = {"P_lex": p_lex, "P_C_given_lex": prec, "P_C_given_notlex": float(rn["C"].mean()),
                                   "P_C": p_c_lex + p_c_notlex, "recall_lex": p_c_lex / (p_c_lex + p_c_notlex),
                                   "P_C_random_direct": float(pc_r)}
    res["confusion_lex_by_truth"] = key.group_by("corr_lex", "truth").len().sort("corr_lex", "truth").to_dicts()
    res["by_regime_precision_lex"] = key.filter(pl.col("corr_lex")).group_by("regime").agg(pl.col("C").mean(), pl.len()).sort("regime").to_dicts()
    json.dump(res, open(vd / "results.json", "w"), indent=1, default=str)
    print(json.dumps({k: v for k, v in res.items() if k != "confusion_lex_by_truth"}, indent=1, default=str))


if __name__ == "__main__":
    main()
