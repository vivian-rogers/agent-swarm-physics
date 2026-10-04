"""H111 replication: per-unit collective Fano ratio and the sum-rule comparison (non-holdout units only).

Usage: uv run python hypotheses/H111-talk-fano-sum-rule/analysis/run_units.py [--units 27,41] [--workers 2]
Writes data/processed/H111-talk-fano-sum-rule/results/units.parquet (and units_<clock>.parquet for --clock wall).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import sys  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402
from pathlib import Path  # noqa: E402

import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h111lib as L  # noqa: E402

ROOT = L.ROOT
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import holdout_mask  # noqa: E402

H67 = ROOT / "data/processed/H67-lagged-criticality-dial/results/units.parquet"


def one(args):
    uid, g, g_se, g3, g_het, clock, exo = args
    L.CLOCK, L.EXO_RULE = clock, exo
    U = L.load_unit(uid)
    days = U.days["pt_date"].to_list()
    assert not any(holdout_mask(days, [None] * len(days))), f"holdout in {uid}"
    r = L.unit_stats(U, g=g, g_se=g_se, g3=g3, g_het=g_het, B=500, n_shift=49, seed=7)
    r["clock"], r["exo_rule"] = clock, exo
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", default="")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--clock", default=L.CLOCK)
    ap.add_argument("--exo", default=L.EXO_RULE)
    a = ap.parse_args()
    meta = pl.read_parquet(L.OUT / "unit_meta.parquet")
    g67 = pl.read_parquet(H67).select("unit_id", "g", "g_se", "g3", "g_het", "g_eq")
    m = meta.join(g67, on="unit_id", how="left")
    if a.units:
        m = m.filter(pl.col("unit_id").is_in(a.units.split(",")))
    jobs = [(r["unit_id"], r["g"], r["g_se"], r["g3"], r["g_het"], a.clock, a.exo) for r in m.iter_rows(named=True)]
    with ProcessPoolExecutor(max_workers=min(a.workers, 2)) as ex:
        res = list(ex.map(one, jobs))
    df = pl.DataFrame(res, infer_schema_length=None).join(
        m.select("unit_id", "goal_no", "regime", "n_days", "first_day", "last_day", "g_eq"), on="unit_id", how="left")
    out = L.OUT / "results"
    out.mkdir(parents=True, exist_ok=True)
    name = "units.parquet" if (a.clock == "percall" and not a.units) else f"units_{a.clock}{'_sub' if a.units else ''}.parquet"
    df.write_parquet(out / name)
    print("wrote", out / name, df.height)


if __name__ == "__main__":
    main()
