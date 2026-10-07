"""Summarise the H135 synthetic runs: size and power of each statistic per skeleton, world and co-alive rule.

  uv run python hypotheses/H135-detailed-balance-potts-walker/analysis/synth_summary.py
Writes data/processed/H135-detailed-balance-potts-walker/synthetic/summary.json and prints a compact table.
Band = 2.5-97.5% of W0 runs 0-99; the size in W0 is read on W0 runs 100-199 (split half); other worlds use all runs.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h135lib as L  # noqa: E402

STATS = ("m_pi", "m2co", "beta", "theta")


def beyond(x, lo, hi):
    x = np.asarray(x, float)
    ok = np.isfinite(x)
    return float(np.mean((x[ok] < lo) | (x[ok] > hi))) if ok.any() else np.nan


def main():
    out = {}
    for f in sorted((L.D / "synthetic").glob("*.parquet")):
        df = pl.read_parquet(f)
        key = f.stem
        out[key] = {}
        for pre in ("", "v80_"):
            rule = "primary" if pre == "" else "v80"
            w0 = df.filter(pl.col("world") == "W0")
            cal = w0.filter(pl.col("run") < 100)
            test0 = w0.filter(pl.col("run") >= 100)
            bands = {}
            for s in STATS:
                x = cal[pre + s].to_numpy().astype(float)
                x = x[np.isfinite(x)]
                bands[s] = [float(np.quantile(x, .025)), float(np.quantile(x, .975))] if len(x) > 10 else [np.nan, np.nan]
            res = {"band_W0": bands}
            for w in ("W0", "W0M", "W1", "W2", "W3", "W4"):
                d = test0 if w == "W0" else df.filter(pl.col("world") == w)
                r = {"n": d.height, "co_hops": float(np.nanmean(d[pre + "n_co_hops"].to_numpy().astype(float))),
                     "pairs4": float(np.nanmean(d[pre + "n_pairs4"].to_numpy().astype(float))),
                     "o1_pass": float(np.nanmean(d[pre + "o1_pass"].to_numpy().astype(float))),
                     "slope_med": float(np.nanmedian(d[pre + "slope"].to_numpy().astype(float))) if d[pre + "slope"].drop_nulls().len() else None}
                for s in STATS:
                    v = d[pre + s].to_numpy().astype(float)
                    r[f"{s}_mean"] = float(np.nanmean(v)) if np.isfinite(v).any() else None
                    r[f"{s}_beyond"] = beyond(v, *bands[s])
                r["flip_mpi_rej"] = float(np.nanmean(d[pre + "p_flip_mpi"].to_numpy().astype(float) < 0.05))
                r["flip_m2_rej"] = float(np.nanmean(d[pre + "p_flip_m2"].to_numpy().astype(float) < 0.05))
                dd = w0 if w == "W0" else d          # O4 and LR were run on W0 runs 0-49 / 0-29: use all W0 runs
                if pre + "psi" in dd.columns:
                    ok = dd[pre + "psi"].is_not_null() & dd[pre + "psi"].is_not_nan()
                    ps = dd.filter(ok)[pre + "psi"].to_numpy()
                    if len(ps):
                        rh = dd.filter(ok)[pre + "rho"].to_numpy()
                        sp = dd.filter(ok)[pre + "se_psi"].to_numpy()
                        r["psi_mean"], r["psi_sd"], r["rho_mean"] = float(np.mean(ps)), float(np.std(ps)), float(np.mean(rh))
                        r["psi_cover1"] = float(np.mean(np.abs(ps - 1) <= 1.96 * sp)) if len(sp) == len(ps) else None
                lpc = dd[pre + "lr_p"].drop_nulls().drop_nans() if pre + "lr_p" in dd.columns else None
                if lpc is not None and lpc.len():
                    lp = lpc.to_numpy()
                    r["lr_rej"] = float(np.mean(lp < 0.05))
                    r["lr_n"] = int(len(lp))
                if "hub_flux_early" in d.columns:
                    r["hub_mean"] = float(np.nanmean(d["hub_flux_early"].to_numpy().astype(float)))
                res[w] = r
            # pass rules (card): O1 test if pass >= 0.8 in W0 and <= 0.2 in W1-W3; O2/O3 if size <= 0.10 in W0 and W0M
            # and power >= 0.8 in W1 or W2
            o1_ok = res["W0"]["o1_pass"] >= 0.8 and max(res[w]["o1_pass"] for w in ("W1", "W2", "W3")) <= 0.2
            rules = {"O1_valid": bool(o1_ok)}
            for s, name in (("m_pi", "O2"), ("m2co", "O3")):
                size = max(res["W0"][f"{s}_beyond"], res["W0M"][f"{s}_beyond"])
                power = max(res["W1"][f"{s}_beyond"], res["W2"][f"{s}_beyond"])
                rules[f"{name}_size"] = size
                rules[f"{name}_power_W1_W2"] = power
                rules[f"{name}_valid"] = bool(size <= 0.10 and power >= 0.8)
            res["rules"] = rules
            out[key][rule] = res
    (L.D / "synthetic" / "summary.json").write_text(json.dumps(out, indent=1, default=lambda x: None))
    for k, v in out.items():
        for rule, r in v.items():
            rr = r["rules"]
            print(f"{k:18s} {rule:7s} co_hops W0 {r['W0']['co_hops']:6.1f} pairs4 {r['W0']['pairs4']:4.1f} | O1 pass W0 {r['W0']['o1_pass']:.2f} "
                  f"W1 {r['W1']['o1_pass']:.2f} W2 {r['W2']['o1_pass']:.2f} W3 {r['W3']['o1_pass']:.2f} | "
                  f"m_pi beyond W0 {r['W0']['m_pi_beyond']:.2f} W0M {r['W0M']['m_pi_beyond']:.2f} W1 {r['W1']['m_pi_beyond']:.2f} "
                  f"W2 {r['W2']['m_pi_beyond']:.2f} W3 {r['W3']['m_pi_beyond']:.2f} | m2co W0 {r['W0']['m2co_beyond']:.2f} "
                  f"W0M {r['W0M']['m2co_beyond']:.2f} W1 {r['W1']['m2co_beyond']:.2f} W2 {r['W2']['m2co_beyond']:.2f} W3 {r['W3']['m2co_beyond']:.2f} "
                  f"| flip size {r['W0']['flip_mpi_rej']:.2f}/{r['W0']['flip_m2_rej']:.2f}")
            for w in ("W0", "W0M", "W1", "W4"):
                if "psi_mean" in r[w]:
                    print(f"    {w} psi {r[w]['psi_mean']:.2f}±{r[w]['psi_sd']:.2f} cover1 {r[w].get('psi_cover1')} rho {r[w]['rho_mean']:.2f} "
                          f"lr_rej {r[w].get('lr_rej')} (n {r[w].get('lr_n')})")
            if "hub_mean" in r["W0"]:
                print(f"    hub_flux W0 mean {r['W0']['hub_mean']:.3f}")


if __name__ == "__main__":
    main()
