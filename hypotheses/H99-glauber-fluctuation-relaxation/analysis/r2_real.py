"""H99 round 2 on real data (non-holdout units only): per unit, the W0 reference world (independent talk at the real
calls, 8 replicates), the call-grid removal stack with the room partition, the round-1-grid removal stack (check), the
call-clock kernel (R1), and for regime II/III units the R2 indirect-inference curve (hop-1 coupling g1 in
{0.1, 0.2, 0.3, 0.45}, 3 replicates each; g1 = 0 is the W0 world).

Output: data/processed/H99-glauber-fluctuation-relaxation/r2/results/{units.parquet, curves.parquet}
Usage: uv run python .../r2_real.py [--units 38a,51g]
"""
from __future__ import annotations

import argparse
import sys
import zlib
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r2lib as R  # noqa: E402
import r2run as RR  # noqa: E402

OUT = RR.R2 / "results"
N_W0 = 8
G_GRID = (0.1, 0.2, 0.3, 0.45)
N_CURVE = 3
VARS = ("V0", "V1", "V2", "V3", "V4", "V5", "V3s", "V5s")


def point_stats(V):
    out = {}
    for k, (Xs, oks, rooms) in V.items():
        e = R.est_X(R.sums_X(Xs, oks).sum(0)) if len(Xs) else {}
        out.update({f"{k}_{s}": e.get(s, np.nan) for s in ("g_chi", "drho1", "rho_c1", "rho_p1")})
        if k in ("V0", "V5"):
            ps = R.pair_sums(Xs, oks, rooms)
            if len(ps) and ps[:, 1].sum() > 0 and ps[:, 3].sum() > 0:
                out.update({f"{k}_pair_{s}": v for s, v in R.pair_est(ps).items()})
    return out


def one(uid):
    meta, calls, msgs, exo, ws = RR.load_unit(uid)
    if calls.filter(pl.col("trim")).height < 500:
        return None, []
    rng = np.random.default_rng(zlib.crc32(f"real|{uid}".encode()))
    row = {"unit": uid, "goal_no": meta["goal_no"], "regime": meta["regime"], "r_bar": meta["r_bar"],
           "n_calls_trim": meta["n_calls_trim"], "n_agents": meta["n_agents_trim"], "rooms": meta["rooms_trim"]}
    sk = R.skeleton(calls, msgs)
    # W0 reference
    w0 = []
    for r in range(N_W0):
        srng = np.random.default_rng(zlib.crc32(f"W0|{uid}|{r}".encode()))
        Cs, Ms = R.simulate(sk, srng, r_bar=meta["r_bar"])
        p = point_stats(RR.call_grid_variants(Cs, exo, ws))
        D = R.call_design(Cs, Ms)
        rs = R.rho_self(D)
        p["rho_s"] = rs[:, 0].sum() / rs[:, 1].sum() if len(rs) and rs[:, 1].sum() > 0 else np.nan
        w0.append(p)
    W = pl.DataFrame(w0, infer_schema_length=None)
    for c in W.columns:
        v = W[c].cast(pl.Float64).to_numpy()
        row[f"w0_{c}"] = float(np.nanmean(v)) if np.isfinite(v).any() else np.nan
        row[f"w0sd_{c}"] = float(np.nanstd(v, ddof=1)) if np.isfinite(v).sum() > 1 else np.nan
    # real: call grid
    V = RR.call_grid_variants(calls, exo, ws)
    row.update({f"cg_{k}": v for k, v in RR.minute_stats(V, rng, B=400).items()})
    # real: round-1 grid (check)
    if (RR.BASE / "grids" / f"{uid}.npz").exists():
        try:
            V1 = RR.round1_grid_variants(uid, meta, calls, exo, ws)
            row.update({f"r1g_{k}": v for k, v in RR.minute_stats(V1, rng, B=400).items()})
        except KeyError:
            pass
    # R1 kernel
    k1, _ = RR.r1_stats(calls, msgs, meta, rng, B=200)
    row.update({f"k_{k}": v for k, v in k1.items()})
    # R2 curve
    curve = []
    if meta["regime"] in ("II", "III"):
        for g in G_GRID:
            for r in range(N_CURVE):
                srng = np.random.default_rng(zlib.crc32(f"curve|{uid}|{g}|{r}".encode()))
                Cs, Ms = R.simulate(sk, srng, g1=g, r_bar=meta["r_bar"])
                p = point_stats(RR.call_grid_variants(Cs, exo, ws))
                curve.append({"unit": uid, "g1": g, "rep": r, "V0_drho1": p["V0_drho1"], "V5_drho1": p["V5_drho1"],
                              "V0_g_chi": p["V0_g_chi"]})
        for r, p in enumerate(w0):
            curve.append({"unit": uid, "g1": 0.0, "rep": r, "V0_drho1": p["V0_drho1"], "V5_drho1": p["V5_drho1"],
                          "V0_g_chi": p["V0_g_chi"]})
    row = {k: (float(v) if isinstance(v, (int, float, np.floating, np.integer)) and not isinstance(v, bool) else v)
           for k, v in row.items()}
    return row, curve


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", default="")
    a = ap.parse_args()
    meta = pl.read_parquet(RR.R2 / "unit_meta.parquet")
    units = a.units.split(",") if a.units else meta.filter(pl.col("n_calls_trim") >= 500)["unit_id"].to_list()
    # heavy units first so the two workers finish together
    order = meta.filter(pl.col("unit_id").is_in(units)).sort("n_calls_trim", descending=True)["unit_id"].to_list()
    OUT.mkdir(parents=True, exist_ok=True)
    rows, curves = [], []
    with ProcessPoolExecutor(2) as ex:
        for row, cv in ex.map(one, order):
            if row is None:
                continue
            rows.append(row)
            curves += cv
            print(row["unit"], "done", flush=True)
    df = pl.DataFrame(rows, infer_schema_length=None)
    cf = pl.DataFrame(curves) if curves else None
    if a.units and (OUT / "units.parquet").exists():
        old = pl.read_parquet(OUT / "units.parquet").filter(~pl.col("unit").is_in(df["unit"]))
        df = pl.concat([old, df], how="diagonal_relaxed")
        if cf is not None and (OUT / "curves.parquet").exists():
            oc = pl.read_parquet(OUT / "curves.parquet").filter(~pl.col("unit").is_in(cf["unit"]))
            cf = pl.concat([oc, cf], how="diagonal_relaxed")
    df.write_parquet(OUT / "units.parquet")
    if cf is not None:
        cf.write_parquet(OUT / "curves.parquet")


if __name__ == "__main__":
    main()
