"""H71 axis F: the estimators on planted two-phase sawtooth dynamics at real cycle counts (before real outcomes).

Skeletons are the real non-holdout cycle tables (agent, period, time, appends per cycle, cycle type, wall-clock length);
only sizes are simulated. Noise levels are fixed (0.15 in log size per phase), not fitted to real outcomes.

Writes data/processed/H71-memory-homeostat/synthetic/synthetic.json.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h71lib as L  # noqa: E402

ROOT = HERE.parents[2]
OUT = ROOT / "data/processed/H71-memory-homeostat"
SKEL_PERIODS = ["G51", "G38", "G37", "G30", "G12a", "G36b"]
WORLDS = [("overshoot", -0.3, 0.0), ("deadbeat", 0.0, 0.0), ("first_order_weak", 0.3, 0.0),
          ("first_order", 0.6, 0.0), ("first_order_growthfb", 0.6, -0.3), ("near_rw", 0.9, 0.0),
          ("random_walk", 1.0, 0.0)]


def one(cyc_s, snaps_s, B=100):
    p = L.pairs(cyc_s)
    ph = L.phi_pooled(p)
    hpj = L.phi_hpj(p)
    _, lo, hi = L.boot_hpj(p, B=400)
    o = L.oos(cyc_s)
    share = float((o["mse_ar1"] < o["mse_rw"]).mean()) if o.height else float("nan")
    share_db = float((o["mse_ar1"] < o["mse_db"]).mean()) if o.height else float("nan")
    return {"phi": ph, "phi_hpj": hpj, "lo": lo, "hi": hi, "mixed": L.mixed_phi(snaps_s), "ar2": L.ar2(cyc_s),
            "oos_ar1_beats_rw": share, "oos_ar1_beats_db": share_db, "clock_slope": L.clock_stat(p),
            "dec": L.decomposition(p), "f_minus_v": L.phi_forced_minus_vol(p)}


def main(reps: int = 20):
    cyc = pl.read_parquet(OUT / "cycles.parquet")
    res = {}
    for per in SKEL_PERIODS:
        skel = cyc.filter(pl.col("period") == per).select("agent", "period", "regime", "t", "n_app", "ctype", "dt_s")
        res[per] = {"n_cycles": skel.height, "n_agents": skel["agent"].n_unique(), "worlds": {}}
        r = reps if skel.height < 5000 else max(6, reps // 3)
        for name, phi, c in WORLDS:
            out = []
            for k in range(r):
                rng = np.random.default_rng(1000 * k + hash(name) % 997)
                cs, ss = L.simulate_cycles(skel, phi, c, rng=rng)
                out.append(one(cs, ss, B=60 if skel.height > 5000 else 100))
            arr = {key: np.array([o[key] for o in out], dtype=float) for key in
                   ("phi", "phi_hpj", "lo", "hi", "mixed", "ar2", "oos_ar1_beats_rw", "oos_ar1_beats_db",
                    "clock_slope", "f_minus_v")}
            res[per]["worlds"][name] = {
                "planted_phi": phi, "planted_c": c, "reps": r,
                "phi_mean": float(np.nanmean(arr["phi"])), "phi_hpj_mean": float(np.nanmean(arr["phi_hpj"])),
                "bias_hpj": float(np.nanmean(arr["phi_hpj"]) - phi),
                "coverage": float(np.mean((arr["lo"] <= phi) & (arr["hi"] >= phi))),
                "ci_excl_0_and_1": float(np.mean((arr["lo"] > 0) & (arr["hi"] < 1))),
                "ci_below_0": float(np.mean(arr["hi"] < 0)), "ci_incl_1": float(np.mean(arr["hi"] >= 1)),
                "mixed_mean": float(np.nanmean(arr["mixed"])), "mixed_sd": float(np.nanstd(arr["mixed"])),
                "ar2_mean": float(np.nanmean(arr["ar2"])), "ar2_sd": float(np.nanstd(arr["ar2"])),
                "oos_ar1_beats_rw": float(np.nanmean(arr["oos_ar1_beats_rw"])),
                "oos_ar1_beats_db": float(np.nanmean(arr["oos_ar1_beats_db"])),
                "clock_slope_mean": float(np.nanmean(arr["clock_slope"])),
                "clock_slope_sd": float(np.nanstd(arr["clock_slope"])),
                "f_minus_v_mean": float(np.nanmean(arr["f_minus_v"])),
                "f_minus_v_sd": float(np.nanstd(arr["f_minus_v"])),
                "b_mean": float(np.nanmean([o["dec"]["b"] for o in out])),
                "c_mean": float(np.nanmean([o["dec"]["c"] for o in out])),
                "b1c_mean": float(np.nanmean([o["dec"]["b1c"] for o in out]))}
            w = res[per]["worlds"][name]
            print(per, name, f"phi {w['phi_hpj_mean']:+.3f} (planted {phi:+.2f}) cov {w['coverage']:.2f} "
                  f"mixed {w['mixed_mean']:+.3f} oos {w['oos_ar1_beats_rw']:.2f} clock {w['clock_slope_mean']:+.3f}",
                  flush=True)
        # wall-clock world: phi = exp(-k dt) with median-cycle phi = 0.5
        dtm = float(skel["dt_s"].drop_nulls().median())
        kk = np.log(2) / dtm
        sl = []
        for k in range(max(6, r // 2)):
            cs, ss = L.simulate_cycles(skel, 0.5, 0.0, rng=np.random.default_rng(77 + k), wall_k=kk)
            sl.append(L.clock_stat(L.pairs(cs)))
        res[per]["wallclock"] = {"k_per_s": kk, "slope_mean": float(np.nanmean(sl)), "slope_sd": float(np.nanstd(sl))}
        print(per, "wallclock slope", res[per]["wallclock"], flush=True)
    (OUT / "synthetic").mkdir(parents=True, exist_ok=True)
    (OUT / "synthetic/synthetic.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 20)
