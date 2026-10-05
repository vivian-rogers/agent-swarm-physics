"""H42 round 2: score the R2/R1 synthetic validation (S-R2a, S-R2b, S-R2c), per regime where each outcome is used.

Reads round2/synthetic/r2_synth.parquet; writes round2/synthetic/r2_synth_summary.json and prints tables.
Outcomes by regime: III -> talk, pause, loggap, loggap_np; I -> talk, chatnext, start, stop, loggap.
Unit level: median J over unit x replicate, share of CIs excluding 0 (false positives in V0/V0f/VL), coverage (V1).
Pooled level: per replicate, a DerSimonian-Laird pool over the regime's units, as the real-data statistic is pooled.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import r2lib as L  # noqa: E402

TOL = {"talk": 0.01, "pause": 0.002, "loggap": 0.01, "loggap_np": 0.01, "chatnext": 0.003, "start": 0.003,
       "stop": 0.003}
USE = {"III": ["talk", "pause", "loggap", "loggap_np"], "I": ["talk", "chatnext", "start", "stop", "loggap"]}


def long(d):
    rows = []
    for X in ("named", "un", "cold", "thrn"):
        if f"J_{X}" not in d.columns:
            continue
        x = d.filter(pl.col(f"J_{X}").is_not_null() & (pl.col(f"se_{X}") > 0))
        truth = pl.col("plant_un") if X == "un" else pl.col("plant_named")
        rows.append(x.select("world", "regime", "outcome", "spec", "field", "unit_id", "rep",
                             pl.lit(X).alias("X"), pl.col(f"J_{X}").alias("J"), pl.col(f"lo_{X}").alias("lo"),
                             pl.col(f"hi_{X}").alias("hi"), pl.col(f"se_{X}").alias("se"), truth.alias("truth")))
    return pl.concat(rows)


def main():
    d = pl.read_parquet(L.R2 / "synthetic" / "r2_synth.parquet")
    z = long(d)
    z = z.with_columns(((pl.col("lo") > 0) | (pl.col("hi") < 0)).alias("sig"),
                       ((pl.col("lo") <= pl.col("truth")) & (pl.col("hi") >= pl.col("truth"))).alias("cov"))
    keep = pl.lit(False)
    for reg, outs in USE.items():
        keep = keep | ((pl.col("regime") == reg) & pl.col("outcome").is_in(outs))
    z = z.filter(keep)
    unit = (z.group_by("regime", "outcome", "spec", "field", "X", "world")
            .agg(pl.col("J").median().alias("medJ"), pl.col("truth").median().alias("truth"),
                 pl.col("sig").mean().alias("fp_or_power"), pl.col("cov").mean().alias("cov"),
                 pl.col("se").median().alias("se"), pl.len().alias("n"))
            .sort("regime", "outcome", "spec", "field", "X", "world"))
    # pooled per replicate
    prow = []
    for (reg, o, sp, fd, X, w, rep), g in z.group_by("regime", "outcome", "spec", "field", "X", "world", "rep"):
        p = L.dl_pool(g["J"].to_numpy(), g["se"].to_numpy())
        if p["k"] == 0:
            continue
        prow.append({"regime": reg, "outcome": o, "spec": sp, "field": fd, "X": X, "world": w, "rep": rep,
                     "J": p["re"], "lo": p["re_lo"], "hi": p["re_hi"], "truth": float(g["truth"].mean())})
    P = pl.DataFrame(prow).with_columns(((pl.col("lo") > 0) | (pl.col("hi") < 0)).alias("sig"),
                                        ((pl.col("lo") <= pl.col("truth")) & (pl.col("hi") >= pl.col("truth"))).alias("cov"))
    pooled = (P.group_by("regime", "outcome", "spec", "field", "X", "world")
              .agg(pl.col("J").median().alias("medJ_pool"), pl.col("truth").median().alias("truth"),
                   pl.col("sig").mean().alias("sig_pool"), pl.col("cov").mean().alias("cov_pool"), pl.len().alias("reps"))
              .sort("regime", "outcome", "spec", "field", "X", "world"))
    tab = unit.join(pooled, on=["regime", "outcome", "spec", "field", "X", "world"], how="left")
    # criteria
    verdict = {}
    for (reg, o, sp, fd, X), g in tab.group_by("regime", "outcome", "spec", "field", "X"):
        key = f"{reg}|{o}|{sp}|{'field' if fd else 'nofield'}|{X}"
        nulls = g.filter(pl.col("world").is_in(["V0", "V0f", "VL"]))
        a_unit = bool((nulls["medJ"].abs() <= TOL[o]).all() and (nulls["fp_or_power"] <= 0.15).all())
        a_pool = bool((nulls["medJ_pool"].abs() <= TOL[o]).all() and (nulls["sig_pool"] <= 0.15).all())
        v1 = g.filter(pl.col("world") == "V1")
        b = None
        if len(v1) and abs(v1["truth"][0]) > 1e-9:
            rel = (v1["medJ"][0] - v1["truth"][0]) / v1["truth"][0]
            b = {"rel_err": float(rel), "cov_unit": float(v1["cov"][0]), "cov_pool": float(v1["cov_pool"][0]),
                 "power_pool": float(v1["sig_pool"][0]),
                 "pass": bool(abs(rel) <= 0.30 and v1["cov"][0] >= 0.8)}
        worst = {w: {"medJ": float(r["medJ"]), "fp": float(r["fp_or_power"]), "medJ_pool": r["medJ_pool"],
                     "fp_pool": r["sig_pool"]} for w, r in zip(nulls["world"], nulls.iter_rows(named=True))}
        verdict[key] = {"S_R2a_unit": a_unit, "S_R2a_pool": a_pool, "S_R2b": b, "nulls": worst}
    pl.Config.set_tbl_rows(300); pl.Config.set_tbl_width_chars(250); pl.Config.set_tbl_cols(20)
    print(tab.with_columns(pl.col(pl.Float64).round(4)))
    for k, v in sorted(verdict.items()):
        print(k, "S-R2a unit", v["S_R2a_unit"], "pool", v["S_R2a_pool"], "S-R2b", v["S_R2b"])
    (L.R2 / "synthetic" / "r2_synth_summary.json").write_text(json.dumps(
        {"table": tab.to_dicts(), "verdict": verdict}, indent=1, default=float))


if __name__ == "__main__":
    main()
