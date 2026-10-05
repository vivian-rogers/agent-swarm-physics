"""H42 round 2, real data (non-reserved): R2 call-level outcomes and R1 named-message check, with the call-skeleton null.

Per unit (round-1 eligible units; reserved days asserted absent): design on the real call skeleton and real ledger
items; OLS within agent x day x class cells; 1-h block bootstrap (200). Fits:
  r2 (named / unnamed) for every outcome; talk and pause also with room x day x 10-min fixed effects (field);
  r1 (cold / thread-named / unnamed) for talk, with and without the field; h67 (H67-like window + lagged reads) for talk.
Call-skeleton null: 8 synthetic message streams (r2lib.skeleton_null), the same fits on the REAL outcomes.

Writes data/processed/H42-readout-hawkes-kernel/round2/r2_units.parquet.
Usage: uv run python hypotheses/H42-readout-hawkes-kernel/analysis/r2_run.py [--units 38b,41]
"""
from __future__ import annotations

import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import r2lib as L  # noqa: E402

ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import holdout_mask  # noqa: E402

N_NULL = 8
FITS = [(o, "r2", False) for o in L.OUTCOMES] + [("talk", "r2", True), ("pause", "r2", True), ("talk", "r1", False),
                                                  ("talk", "r1", True), ("talk", "h67", False)]


def units():
    pa = pl.read_parquet(ROOT / "data/processed/H42-readout-hawkes-kernel/units.parquet")
    return pa.with_columns(((pl.col("n_agents") >= 3) & (pl.col("n_talk") >= 50)).alias("eligible"))


def run(uid):
    t0 = time.time()
    u = L.load(uid)
    pu = pl.read_parquet(ROOT / "data/processed/shared/period_units.parquet").filter(pl.col("unit_id") == uid)
    days = pu.explode("days")["days"].to_list()
    assert not any(holdout_mask(days, [u.goal] * len(days))), "reserved day"
    sk = L.skeleton(u)
    D = L.design(u, sk)
    rows = []
    real = {}
    for o, spec, field in FITS:
        r = L.fit(D, o, spec=spec, field=field, B=200, seed=1)
        real[(o, spec, field)] = r
    nulls = {k: [] for k in real}
    rng = np.random.default_rng(abs(hash(uid)) % (2 ** 31))
    for rep in range(N_NULL):
        it, _ = L.skeleton_null(u, sk, rng)
        Dn = L.design(u, sk, it)
        for o, spec, field in FITS:
            nulls[(o, spec, field)].append(L.fit(Dn, o, spec=spec, field=field, B=0))
    for k, r in real.items():
        r = dict(r)
        for X in ("named", "un", "cold", "thrn"):
            v = [x.get(f"J_{X}", np.nan) for x in nulls[k]]
            v = np.array([x for x in v if x is not None and np.isfinite(x)])
            if len(v):
                r[f"null_mean_{X}"] = float(v.mean()); r[f"null_sd_{X}"] = float(v.std(ddof=1)) if len(v) > 1 else 0.0
        r.update({"unit_id": uid, "goal_no": u.goal, "regime": u.regime, "n_days": int(len(np.unique(sk.day)))})
        rows.append(r)
    print(uid, u.regime, f"rows={real[('talk', 'r2', False)].get('n')}",
          f"Jtalk_named={real[('talk', 'r2', False)].get('J_named', np.nan):.4f}",
          f"Jpause_named={real[('pause', 'r2', False)].get('J_named', np.nan):.4f}", f"{time.time() - t0:.0f}s", flush=True)
    return rows


def main():
    ids = units().filter(pl.col("eligible"))["unit_id"].to_list() if "--units" not in sys.argv else \
        sys.argv[sys.argv.index("--units") + 1].split(",")
    out = L.R2 / "r2_units.parquet"
    rows = []
    with ProcessPoolExecutor(2) as ex:
        for rr in ex.map(run, ids):
            rows += rr
            pl.DataFrame(rows, infer_schema_length=None).write_parquet(out)


if __name__ == "__main__":
    main()
