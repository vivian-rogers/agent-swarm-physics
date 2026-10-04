"""H63 scheduler-impostor variant (pre-registered "untrimmed variant"): the arrival-hazard lead-lag model without the
all-present / first-30-min trim (first touches of the day count as arrivals). Writes results/untrim_hazard.parquet."""
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import polars as pl

import h63lib as L


def run(g):
    P = L.load(g)
    D, uni = L.risk_panel(P, trim=False)
    if D is None:
        return {"goal_no": g}
    h = L.hazard(D, B=20, seed=g)
    return {"goal_no": g, **{f"u_{k}": v for k, v in h.items() if k != "regs"}}


if __name__ == "__main__":
    goals = pl.read_parquet(L.OUT / "meta.parquet")["goal_no"].to_list()
    with ProcessPoolExecutor(2) as ex:
        res = list(ex.map(run, goals))
    df = pl.DataFrame(res, infer_schema_length=None)
    df.write_parquet(L.OUT / "results" / "untrim_hazard.parquet")
    H = df.filter(pl.col("u_n_events") >= 50)
    for k in ("dS", "dL"):
        print(k, L.re_pool(H[f"u_{k}"].to_numpy(), H[f"u_{k}_se"].to_numpy()))
    print(df.select("goal_no", "u_n_events", "u_dS", "u_dL", "u_dL_lo", "u_dL_hi", "u_L", "u_L_lead"))
