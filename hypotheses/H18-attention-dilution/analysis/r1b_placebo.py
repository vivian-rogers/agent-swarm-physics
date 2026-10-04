"""H18 round 1b, P10 (invisible-message placebo) on reply labels.

  uv run python hypotheses/H18-attention-dilution/analysis/r1b_placebo.py

DQ2 labelled 2,000 invisible pairs (A arrived during B's own model call) and 1,000 reversed pairs (A after B) as a
placebo. Here, with ledger visibility (`reply_pairs`, pair_set and vis_uncertain), per regime and per H18 period:
mean p_reply of strictly invisible pairs vs visible top-1 candidates reweighted to the invisible pairs' cells of
(B names A's author) x cos decile, and the reversed-pair floor. P10's reply version: invisible <= 1/2 matched visible.
Bootstrap over B messages. Writes data/processed/H18-attention-dilution/r1b/placebo_reply.json.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import json
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H18-attention-dilution/r1b"
H18_GOALS = [24, 25, 26, 27, 30, 31, 35, 36, 37, 38, 39, 40, 41, 42, 44, 51]


def matched(inv: pl.DataFrame, vis: pl.DataFrame, rng, B=1000):
    edges = np.nanquantile(vis["cos"].to_numpy(), np.linspace(0, 1, 11)[1:-1])
    cell = lambda df: df.with_columns((pl.col("b_names_a").cast(pl.Int8) * 10 + pl.col("cos").fill_null(0).map_batches(
        lambda s: pl.Series(np.digitize(s.to_numpy(), edges)), return_dtype=pl.Int64)).alias("cell"))
    inv, vis = cell(inv), cell(vis)
    w = inv.group_by("cell").len().rename({"len": "w"})
    vm = vis.group_by("cell").agg(pl.col("p_reply").mean().alias("pv"), pl.len().alias("nv")).join(w, on="cell")
    pv = float((vm["pv"] * vm["w"]).sum() / vm["w"].sum()) if vm.height else float("nan")
    pi = float(inv["p_reply"].mean())
    x = inv["p_reply"].to_numpy()
    bs = []
    for _ in range(B):
        bs.append(x[rng.integers(len(x), size=len(x))].mean() / pv if pv else np.nan)
    return {"n_invisible": inv.height, "p_invisible": pi, "p_visible_matched": pv, "ratio": pi / pv if pv else None,
            "ratio_ci": [float(np.nanpercentile(bs, 2.5)), float(np.nanpercentile(bs, 97.5))],
            "share_ge05_invisible": float((inv["p_reply"] >= 0.5).mean())}


def main():
    rng = np.random.default_rng(18)
    rp = pl.read_parquet(SH / "reply_pairs.parquet", columns=["b_msg", "pair_set", "labelled", "p_reply", "cand_rank", "cos",
                                                              "b_names_a", "vis_uncertain", "holdout", "regime", "goal_no"]
                         ).filter(pl.col("labelled") & ~pl.col("holdout"))
    inv = rp.filter((pl.col("pair_set") == "invisible") & ~pl.col("vis_uncertain").fill_null(False))
    vis = rp.filter((pl.col("pair_set") == "cand") & (pl.col("cand_rank") == 1))
    rev = rp.filter(pl.col("pair_set") == "reversed")
    out = {"all": matched(inv, vis, rng), "reversed_mean": float(rev["p_reply"].mean()), "n_reversed": rev.height,
           "by_regime": {}, "by_period": {}}
    for reg in ("I", "II", "III"):
        a, b = inv.filter(pl.col("regime").cast(pl.Utf8) == reg), vis.filter(pl.col("regime").cast(pl.Utf8) == reg)
        if a.height >= 20:
            out["by_regime"][reg] = matched(a, b, rng)
    for g in H18_GOALS:
        a, b = inv.filter(pl.col("goal_no") == g), vis.filter(pl.col("goal_no") == g)
        if a.height >= 30:
            out["by_period"][f"G{g:02d}"] = matched(a, b, rng)
        else:
            out["by_period"][f"G{g:02d}"] = {"n_invisible": a.height, "note": "too few labelled strictly invisible pairs"}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "placebo_reply.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in out.items() if k != "by_period"}, indent=1))
    print({k: (v.get("ratio"), v.get("n_invisible")) for k, v in out["by_period"].items()})


if __name__ == "__main__":
    main()
