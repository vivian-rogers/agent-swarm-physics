"""H37 label validation: Jev vs Claude's blind labels (O0; Amendment 1, point 2).

  --draw-enriched [--dump PATH]   draw the enriched blind set: 15 pairs each from Jev's negative / positive / neutral
                                  predictions (all labelled periods, excluding the random 60), shuffled; optional text
                                  dump to a scratch path OUTSIDE the repository (gated text never enters the project)
  --score                         kappa / agreement on both sets; P(obs | true) by reweighting the strata with the
                                  population shares of Jev's classes; writes validation/results.json and
                                  validation/confusion.json (the synthetic noise model)

Claude's labels are files validation/claude_labels_sample60.json and validation/claude_labels_enriched45.json, written
before their items' Jev answers were looked at.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "2")
import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h37data as D  # noqa: E402

V = D.DATA / "validation"
GOALS = [12, 26, 40, 51]
SGN = {"agree": 1, "support": 1, "neutral": 0, "oppose": -1, "undermine": -1}
SEED = 20261005


def all_labelled():
    parts = []
    for g in GOALS:
        P = D.load_pairs(g)
        parts.append(P.select("goal_no", "pair_id", "stance", "s_hard", "responds"))
    return pl.concat(parts)


def draw_enriched(dump=None):
    A = all_labelled()
    s60 = pl.read_parquet(V / "sample60.parquet").select("goal_no", "pair_id")
    A = A.join(s60, on=["goal_no", "pair_id"], how="anti")
    rng = np.random.default_rng(SEED)
    parts = []
    for sg, name in [(-1, "neg"), (1, "pos"), (0, "neu")]:
        pool = A.filter(pl.col("s_hard") == sg)
        ix = rng.choice(pool.height, 15, replace=False)
        parts.append(pool[np.sort(ix)].select("goal_no", "pair_id").with_columns(pl.lit(name).alias("jev_stratum")))
    S = pl.concat(parts)
    S = S[rng.permutation(S.height)].with_row_index("eid")
    S.write_parquet(V / "enriched45.parquet")
    print("enriched set drawn", S.height)
    if dump:
        path = Path(dump).resolve()
        assert D.ROOT not in path.parents, "refusing to write gated text inside the repository"
        sys.path.insert(0, str(D.H37 / "scheme"))
        from label_stance import window_around
        names = D.names()
        txt = pl.read_parquet(D.SHARED / "chat_text.parquet", columns=["message_id", "text"])
        lines = []
        for r in S.iter_rows(named=True):
            fn = "G12_debater.parquet" if r["pair_id"] >= 100000 else f"G{r['goal_no']:02d}.parquet"
            p = pl.read_parquet(D.DATA / "pairs" / fn).filter(pl.col("pair_id") == r["pair_id"]).row(0, named=True)
            ta = txt.filter(pl.col("message_id") == p["msg_a"])["text"][0]
            tb = txt.filter(pl.col("message_id") == p["msg_b"])["text"][0]
            na, nb = names[p["agent_a"]], names[p["agent_b"]]
            lines.append(f"=== E{r['eid']:02d} ===\nA ({na}): {window_around(ta, None, 800)}\nB ({nb}): {window_around(tb, na, 1000)}\n")
        path.write_text("\n".join(lines))  # no stratum or Jev answer in the dump


def kappa(a, b, cats):
    a = np.asarray(a); b = np.asarray(b)
    po = np.mean(a == b)
    pe = sum(np.mean(a == c) * np.mean(b == c) for c in cats)
    return float((po - pe) / (1 - pe)) if pe < 1 else np.nan, float(po)


def score():
    A = all_labelled()
    pop = A["s_hard"].value_counts().sort("s_hard")
    pop_share = {int(k): v / A.height for k, v in zip(pop["s_hard"], pop["count"])}
    out = {"population_jev_sign_shares": pop_share, "n_population": A.height}
    rows = []
    s60 = pl.read_parquet(V / "sample60.parquet")
    c60 = {x["vid"]: x for x in json.loads((V / "claude_labels_sample60.json").read_text())["labels"]}
    j60 = s60.join(A, on=["goal_no", "pair_id"], how="left")
    for r in j60.iter_rows(named=True):
        c = c60[r["vid"]]
        rows.append({"set": "random60", "stratum": r["stratum"], "jev": r["stance"], "claude": c["stance"],
                     "jev_resp": r["responds"], "claude_resp": c["responds"]})
    ef = V / "claude_labels_enriched45.json"
    if ef.exists():
        e45 = pl.read_parquet(V / "enriched45.parquet")
        ce = {x["eid"]: x for x in json.loads(ef.read_text())["labels"]}
        je = e45.join(A, on=["goal_no", "pair_id"], how="left")
        for r in je.iter_rows(named=True):
            c = ce[r["eid"]]
            rows.append({"set": "enriched45", "stratum": r["jev_stratum"], "jev": r["stance"], "claude": c["stance"],
                         "jev_resp": r["responds"], "claude_resp": c["responds"]})
    R = pl.DataFrame(rows)
    R = R.with_columns(pl.col("jev").replace_strict(SGN, return_dtype=pl.Int8).alias("js"),
                       pl.col("claude").replace_strict(SGN, return_dtype=pl.Int8).alias("cs"))
    for name in ("random60", "enriched45"):
        X = R.filter(pl.col("set") == name)
        if X.height == 0:
            continue
        k3, a3 = kappa(X["js"], X["cs"], [-1, 0, 1])
        k5, a5 = kappa(X["jev"], X["claude"], list(SGN))
        kr, ar = kappa((X["jev_resp"] >= 0.5).to_list(), X["claude_resp"].to_list(), [True, False])
        cm = {f"claude={c}": {f"jev={j}": int(((X["cs"] == c) & (X["js"] == j)).sum()) for j in (-1, 0, 1)} for c in (-1, 0, 1)}
        out[name] = {"n": X.height, "kappa_sign": k3, "agree_sign": a3, "kappa_5class": k5, "agree_5class": a5,
                     "kappa_responds": kr, "agree_responds": ar, "confusion_sign_counts": cm}
    # P(true | obs) from both sets pooled (each item blind), P(obs) from the population -> P(obs | true)
    ptrue_given_obs = {}
    for j in (-1, 0, 1):
        X = R.filter(pl.col("js") == j)
        n = X.height
        cnt = np.array([int((X["cs"] == c).sum()) for c in (-1, 0, 1)], float)
        ptrue_given_obs[j] = ((cnt + 0.5) / (n + 1.5)).tolist()  # Jeffreys-smoothed
        out.setdefault("precision_by_jev_class", {})[str(j)] = {"n": n, "claude_counts_neg_neu_pos": cnt.tolist(),
                                                                "precision": float(cnt[j + 1] / n) if n else None}
    joint = np.array([[pop_share.get(j, 0) * ptrue_given_obs[j][ci] for j in (-1, 0, 1)] for ci in range(3)])  # [true, obs]
    p_obs_given_true = joint / joint.sum(1, keepdims=True)
    recall = {str(c): float(p_obs_given_true[k, k]) for k, c in enumerate((-1, 0, 1))}
    # population-reweighted kappa from the joint
    po = np.trace(joint); pe = float(joint.sum(1) @ joint.sum(0))
    out["reweighted"] = {"P_obs_given_true_rows_true_neg_neu_pos": p_obs_given_true.tolist(), "recall": recall,
                         "true_shares": joint.sum(1).tolist(), "kappa_sign": float((po - pe) / (1 - pe)), "agree_sign": float(po)}
    (V / "results.json").write_text(json.dumps(out, indent=1))
    (V / "confusion.json").write_text(json.dumps({"P_obs_given_true": p_obs_given_true.tolist(), "rows": "true -,0,+", "cols": "obs -,0,+",
                                                  "source": "measured: random60 + enriched45 (blind Claude labels), reweighted by Jev class shares"}, indent=1))
    D.record("validation", "hypotheses/H37-stance-spins/analysis/validate.py", {"sets": ["random60", "enriched45"]})
    print(json.dumps(out, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draw-enriched", action="store_true")
    ap.add_argument("--dump")
    ap.add_argument("--score", action="store_true")
    a = ap.parse_args()
    if a.draw_enriched:
        draw_enriched(a.dump)
    if a.score:
        score()


if __name__ == "__main__":
    main()
