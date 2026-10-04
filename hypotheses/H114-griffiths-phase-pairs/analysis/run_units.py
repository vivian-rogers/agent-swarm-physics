"""H114 replication: per-unit reply-depth tail, model ladder, pair gains and strong-pair cuts (non-holdout units).

Usage: uv run python hypotheses/H114-griffiths-phase-pairs/analysis/run_units.py [--variant primary|untrim|p08]
Writes data/processed/H114-griffiths-phase-pairs/results/units[_<variant>].parquet and pairs[_<variant>].parquet.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h114lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
from common import holdout_mask  # noqa: E402


def variant_msgs(m: pl.DataFrame, variant: str) -> pl.DataFrame:
    if variant == "p08":       # p_reply >= 0.8 parents only (93% blind precision)
        par = np.where((m["par"].to_numpy() >= 0) & (m["p_reply"].fill_null(0).to_numpy() >= 0.8), m["par"].to_numpy(), -1)
        return m.with_columns(pl.Series("par", par), pl.Series("depth", L.depth_pass(par)))
    if variant == "nohuman":   # drop messages whose chain root replies to a human or the automated speaker
        par = m["par"].to_numpy()
        rk = m["root_kind"].to_numpy()
        root = np.arange(len(par))
        for k in range(len(par)):
            if par[k] >= 0:
                root[k] = root[par[k]]
        keep = ~np.isin(rk[root], ["human", "automated"])
        return m.with_columns((pl.col("in_win") & pl.Series(keep)).alias("in_win"))
    return m


def one(args):
    uid, n_days, variant = args
    m, R = L.load_unit(uid)
    m = variant_msgs(m, variant)
    st = L.unit_stats(m, R, n_days, B=500, n_rand=200, seed=11, trim=(variant != "untrim"))
    P = st.pop("_pairs").with_columns(pl.lit(uid).alias("unit_id"))
    st["unit_id"] = uid
    for k in ("hazard", "S", "S_M1", "S_M2", "strong_pairs"):
        st[k] = json.dumps(st[k])
    return st, P


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", default="primary")
    a = ap.parse_args()
    meta = pl.read_parquet(L.OUT / "unit_meta.parquet").filter(pl.col("eligible"))
    for r in meta.iter_rows(named=True):
        days = pl.read_parquet(L.ROOT / "data/processed/shared/period_units.parquet").filter(
            pl.col("unit_id") == r["unit_id"])["days"][0].to_list()
        assert not any(holdout_mask(days, [r["goal_no"]] * len(days))), r["unit_id"]
    jobs = [(r["unit_id"], r["n_days"], a.variant) for r in meta.iter_rows(named=True)]
    with ProcessPoolExecutor(max_workers=2) as ex:
        res = list(ex.map(one, jobs))
    U = pl.DataFrame([x[0] for x in res], infer_schema_length=None).join(
        meta.select("unit_id", "goal_no", "regime", "n_days", "first_day", "last_day", "n_agents"), on="unit_id")
    P = pl.concat([x[1] for x in res], how="diagonal_relaxed")
    out = L.OUT / "results"
    out.mkdir(parents=True, exist_ok=True)
    tag = "" if a.variant == "primary" else f"_{a.variant}"
    U.write_parquet(out / f"units{tag}.parquet")
    P.write_parquet(out / f"pairs{tag}.parquet")
    print("wrote", U.height, "units")


if __name__ == "__main__":
    main()
