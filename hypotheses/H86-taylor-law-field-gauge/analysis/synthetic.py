"""H86 synthetic validation on the real presence grid (spans and windows) of four units, one or two per regime.

Design facts only (spans.parquet, calendar windows, bins15 cell layout); no count is read.
Per agent-day minute inside its span: Poisson(lambda_i * xi * zeta); zero outside the span (the scheduler).
lambda_i lognormal (median 2/min in regime III, 0.7/min otherwise; SD 0.5).
  S0  Poisson + scheduler only
  S1  + private burstiness zeta (gamma per agent-bin, CV^2 s = 1)          (R1)
  S2  S1 + shared within-day field xi per bin (lognormal, CV^2 c = 0.1)
  S3  S1 + shared day-level field xi per day (CV^2 c = 0.1)
Reported per unit and scenario: b, c_T, c_x, c_xw, phi on raw and trimmed grids; size (S1, S3) and power (S2) of the
within-day shift null for c_xw on the trimmed grid; day-bootstrap CI coverage of c_x (S2, trimmed).
Output: data/processed/H86-taylor-law-field-gauge/synthetic/synthetic.json
Usage: uv run python hypotheses/H86-taylor-law-field-gauge/analysis/synthetic.py [--reps 20]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h86lib as L  # noqa: E402

ROOT = L.ROOT
UNITS = ["13", "35", "38a", "51c"]
SCEN = {"S0": (0.0, 0.0, None), "S1": (1.0, 0.0, None), "S2": (1.0, 0.1, "bin"), "S3": (1.0, 0.1, "day")}


def layout(unit):
    b = pl.read_parquet(L.DATA / "bins15.parquet", columns=["unit_id", "pt_date", "bin", "agent", "trim"]).filter(
        pl.col("unit_id") == unit)
    sp = pl.read_parquet(L.DATA / "spans.parquet").filter(pl.col("pt_date").is_in(b["pt_date"].unique().to_list()))
    days = sorted(b["pt_date"].unique().to_list())
    agents = sorted(b["agent"].unique().to_list())
    cells = b.select("pt_date", "bin", "trim").unique().sort("pt_date", "bin")
    return days, agents, cells, sp


def simulate(unit, regime, s, c, kind, rng, lay):
    days, agents, cells, sp = lay
    med = 2.0 if regime == "III" else 0.7
    lam = np.exp(np.log(med) + rng.normal(0, 0.5, len(agents)))
    cd = cells["pt_date"].to_numpy(); cb = cells["bin"].to_numpy()
    Y = np.full((len(cd), len(agents)), np.nan)
    spd = {(r["pt_date"], r["agent"]): (r["m0"], r["m1"]) for r in sp.iter_rows(named=True)}
    sig2 = np.log(1 + c) if c > 0 else 0.0
    xi_day = {d: np.exp(rng.normal(-sig2 / 2, np.sqrt(sig2))) if kind == "day" else 1.0 for d in days}
    xi_bin = np.exp(rng.normal(-sig2 / 2, np.sqrt(sig2), len(cd))) if kind == "bin" else np.ones(len(cd))
    for k, a in enumerate(agents):
        for i in range(len(cd)):
            m = spd.get((cd[i], a))
            if m is None:
                continue
            lo, hi = cb[i] * 15, cb[i] * 15 + 14
            mins = max(0, min(hi, m[1]) - max(lo, m[0]) + 1)
            z = rng.gamma(1 / s, s) if s > 0 else 1.0
            Y[i, k] = rng.poisson(lam[k] * mins * z * xi_day[cd[i]] * xi_bin[i]) if mins > 0 else 0.0
    return Y, cd, cells["trim"].to_numpy()


def run(reps, n_surr):
    rng = np.random.default_rng(20261004)
    pu = pl.read_parquet(ROOT / "data/processed/shared/period_units.parquet").select("unit_id", "regime")
    reg = dict(zip(pu["unit_id"], pu["regime"]))
    out = {}
    for unit in UNITS:
        lay = layout(unit)
        res = {}
        for name, (s, c, kind) in SCEN.items():
            acc = {f"{g}_{k}": [] for g in ("raw", "trim") for k in ("b", "c_T", "c_x", "c_xw", "phi")}
            rej, cover = [], []
            for r in range(reps):
                Y, days, trim = simulate(unit, reg[unit], s, c, kind, rng, lay)
                for g, mask in (("raw", np.ones(len(days), bool)), ("trim", trim)):
                    st = L.taylor(Y[mask], days[mask])
                    for k in ("b", "c_T", "c_x", "c_xw", "phi"):
                        acc[f"{g}_{k}"].append(st.get(k, np.nan))
                if name in ("S1", "S2", "S3") and r < max(reps // 2, 5):
                    Yt, dt_ = Y[trim], days[trim]
                    obs = L.c_cross_within(Yt, dt_)
                    nul = L.shift_null(Yt, dt_, rng, n_surr)
                    rej.append(float((1 + (nul >= obs).sum()) / (n_surr + 1) < 0.05))
                    if name == "S2" and r < 10:
                        ci = L.boot(Yt, dt_, rng, B=100, keys=("c_x",))["c_x"]
                        cover.append(float(ci[0] <= c <= ci[1]))
            res[name] = {k: float(np.nanmedian(v)) for k, v in acc.items()}
            if rej:
                res[name]["shift_null_reject"] = float(np.mean(rej))
            if cover:
                res[name]["cx_trim_ci_cover"] = float(np.mean(cover))
            res[name]["planted"] = {"s": s, "c": c, "kind": kind}
        out[unit] = {"regime": reg[unit], "n_days": len(lay[0]), "n_agents": len(lay[1]),
                     "trim_share": float(lay[2]["trim"].mean()), "scenarios": res}
        print(unit, json.dumps(out[unit]["scenarios"], indent=0)[:2000])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=20)
    ap.add_argument("--surr", type=int, default=39)
    a = ap.parse_args()
    res = run(a.reps, a.surr)
    o = L.DATA / "synthetic"
    o.mkdir(parents=True, exist_ok=True)
    (o / "synthetic.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
