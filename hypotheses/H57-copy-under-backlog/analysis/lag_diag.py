"""H57 post hoc diagnostic (exploratory, non-holdout): near-copy rate per pair against time lag, for read pairs
(A in R(B), A before B) and mutually invisible pairs (in-flight C, unread in both directions).

  uv run python hypotheses/H57-copy-under-backlog/analysis/lag_diag.py --periods 18,21,38,51

Writes results/lag_diag.parquet: goal_no, set (R / I), lag bin, pairs, near rate per model (raw cosine >= DQ5
threshold) and marker near-copy rate (Jaccard >= 0.5; statements with >= 3 markers).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "scheme"))
import h57core as C  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

BINS = [0, 15, 30, 60, 120, 240, 480, 960, 1920, 3840, 1e9]


def pair_table(g: int) -> pl.DataFrame:
    S = pl.read_parquet(C.OUT / "skeleton" / f"G{g:02d}_S.parquet")
    P = pl.read_parquet(C.OUT / "skeleton" / f"G{g:02d}_P.parquet").filter(pl.col("set").is_in([0, 2]))
    msgs = np.unique(np.r_[S["msg"].to_numpy(), P["msg"].to_numpy()]).astype(np.int64)
    content = C.load_real_content(msgs)
    pos = {int(m): i for i, m in enumerate(msgs)}
    b = np.array([pos[int(x)] for x in S["msg"].to_list()])
    ps, pl_ = P["sid"].to_numpy(), np.array([pos[int(x)] for x in P["msg"].to_list()])
    out = {"sid": ps, "set": P["set"].to_numpy()}
    for m in C.MODELS:
        R = content["raw"][m]
        out[f"cos_{m}"] = np.einsum("ij,ij->i", R[b[ps]], R[pl_])
    t = C.chat()["t"]
    tb = S["t"].to_numpy()[ps]
    ta = t.to_numpy()[P["msg"].to_numpy().astype(np.int64)]
    out["lag_s"] = np.abs((tb - ta).astype("timedelta64[ms]").astype(float) / 1000)
    df = pl.DataFrame(out).with_columns(pl.lit(g).alias("goal_no"))
    # marker Jaccard per pair
    mk = content["markers"].with_columns(pl.col("msg").cast(pl.Int64))
    pairs = df.with_row_index("pid").with_columns(pl.Series("bmsg", S["msg"].to_numpy()[ps].astype(np.int64)),
                                                  pl.Series("amsg", P["msg"].to_numpy().astype(np.int64)))
    nb = mk.group_by("msg").agg(pl.len().alias("n"))
    ja = (pairs.select("pid", "bmsg", "amsg").join(mk.rename({"msg": "bmsg"}), on="bmsg")
          .join(mk.rename({"msg": "amsg"}), on=["amsg", "marker"]).group_by("pid").agg(pl.len().alias("inter")))
    pairs = (pairs.join(ja, on="pid", how="left").join(nb.rename({"msg": "bmsg", "n": "nb"}), on="bmsg", how="left")
             .join(nb.rename({"msg": "amsg", "n": "na"}), on="amsg", how="left")
             .with_columns(pl.col("inter").fill_null(0), pl.col("nb").fill_null(0), pl.col("na").fill_null(0)))
    pairs = pairs.with_columns(pl.when(pl.col("nb") >= 3).then(
        (pl.col("inter") / (pl.col("nb") + pl.col("na") - pl.col("inter")) >= 0.5).cast(pl.Float64)).alias("mk_near"))
    return pairs.drop("bmsg", "amsg", "inter", "nb", "na", "pid")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--periods", default="18,21,38,51")
    a = ap.parse_args()
    rows = []
    for g in [int(x) for x in a.periods.split(",")]:
        df = pair_table(g).with_columns(pl.col("lag_s").cut(BINS[1:-1], labels=[str(int(x)) for x in BINS[:-1]]).alias("lag"))
        agg = df.group_by("goal_no", "set", "lag").agg(
            pl.len().alias("pairs"), (pl.col("cos_bge") >= C.THR["bge"]).mean().alias("near_bge"),
            (pl.col("cos_gte") >= C.THR["gte"]).mean().alias("near_gte"),
            ((pl.col("cos_bge") >= C.THR["bge"]) & (pl.col("cos_gte") >= C.THR["gte"])).mean().alias("near_both"),
            pl.col("mk_near").mean().alias("mk_near"), pl.col("cos_bge").mean().alias("mean_cos_bge"))
        rows.append(agg)
        print(f"G{g:02d}", df.group_by("set").agg(pl.len(), (pl.col("cos_bge") >= C.THR["bge"]).mean()).sort("set").rows())
    out = pl.concat(rows).sort("goal_no", "set", "lag")
    (C.OUT / "results").mkdir(exist_ok=True)
    f = C.OUT / "results" / "lag_diag.parquet"
    if f.exists():
        old = pl.read_parquet(f).filter(~pl.col("goal_no").is_in(out["goal_no"].unique().to_list()))
        out = pl.concat([old, out]).sort("goal_no", "set", "lag")
    out.write_parquet(f)
    with pl.Config(tbl_rows=200, tbl_width_chars=200, float_precision=4):
        print(out.filter(pl.col("goal_no").is_in([int(x) for x in a.periods.split(",")])))


if __name__ == "__main__":
    main()
