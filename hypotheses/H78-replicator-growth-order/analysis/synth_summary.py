"""Summarize the synthetic runs (H78 order recovery; H77 sigma* recovery and resolution-test size).
Writes data/processed/H78-replicator-growth-order/synthetic/summary.json and .../H77-repos-as-replicators/synthetic/summary.json.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
S78 = ROOT / "data/processed/H78-replicator-growth-order/synthetic"
S77 = ROOT / "data/processed/H77-repos-as-replicators/synthetic"


def q(x, f):
    x = np.asarray([v for v in x if v is not None and np.isfinite(v)])
    return float(f(x)) if len(x) else None


def main(tag: str = ""):
    import re
    files = [p for p in sorted(S78.glob(f"runs_G*{tag}.parquet")) if re.fullmatch(rf"runs_G\d\d{tag}\.parquet", p.name)]
    runs = pl.concat([pl.read_parquet(p) for p in files], how="diagonal_relaxed")
    out78, out77 = {}, {}
    for (g, w), d in runs.group_by(["period", "world"], maintain_order=True):
        pt = d["p_true"][0]
        key = f"G{g:02d}/{w}"
        dt = d.filter(pl.col("p_testable") & pl.col("p_pooled").is_not_null())
        r = {"runs": d.height, "testable": float(d["p_testable"].mean()), "n_rec_median": q(d["n_rec"].to_list(), np.median)}
        for est in ("p_pooled", "p_whole", "p_fe", "p_clogit"):
            v = dt[est].to_list()
            r[est] = {"median": q(v, np.median), "bias": q([x - pt for x in v if x is not None], np.median),
                      "rmse": q([(x - pt) ** 2 for x in v if x is not None], lambda a: np.sqrt(a.mean()))}
            se = dt[est + "_se"].to_list()
            cov = [abs(x - pt) <= 1.96 * s for x, s in zip(v, se) if x is not None and s is not None and np.isfinite(s)]
            r[est]["coverage"] = float(np.mean(cov)) if cov else None
        out78[key] = r
        s = d.filter(pl.col("sigma").is_not_null() & pl.col("sigma_true").is_not_null())
        st = s.filter(pl.col("sigma_testable"))
        diff = (st["sigma"] - st["sigma_true"]).to_list()
        cov = [abs(a - b) <= 1.96 * c for a, b, c in zip(st["sigma"].to_list(), st["sigma_true"].to_list(), st["sigma_se"].to_list())]
        rf = d.filter(pl.col("res_frac").is_not_null()) if "res_frac" in d.columns else d.head(0)
        out77[key] = {"runs": d.height, "sigma_testable": float(s["sigma_testable"].mean()) if s.height else None,
                      "sigma_true_median": q(st["sigma_true"].to_list(), np.median),
                      "sigma_meas_median": q(st["sigma"].to_list(), np.median),
                      "sigma_bias_median": q(diff, np.median), "sigma_mae": q([abs(x) for x in diff], np.mean),
                      "sigma_coverage": float(np.mean(cov)) if cov else None,
                      "sigma_q95": q(s["sigma"].to_list(), lambda a: np.quantile(a, 0.95)),
                      "res_testable": rf.height / max(d.height, 1),
                      "res_frac_median": q(rf["res_frac"].to_list(), np.median) if rf.height else None,
                      "res_size_p05": float((rf["res_p"] < 0.05).mean()) if rf.height else None,
                      "res_frac_ge09": float((rf["res_frac"] >= 0.9).mean()) if rf.height else None,
                      "q_median": q(d["q"].to_list(), np.median),
                      "frustrated_mean": q(d["n_frustrated"].to_list(), np.mean) if "n_frustrated" in d.columns else None}
    (S78 / f"summary{tag}.json").write_text(json.dumps(out78, indent=1))
    S77.mkdir(parents=True, exist_ok=True)
    (S77 / f"summary{tag}.json").write_text(json.dumps(out77, indent=1))
    for k, v in out78.items():
        p = v["p_pooled"]
        print(f"{k:24s} test {v['testable']:.2f} nrec {v['n_rec_median']} pooled med {p['median']} bias {p['bias']} cov {p['coverage']}"
              f" | fe {v['p_fe']['median']} | clogit {v['p_clogit']['median']}")
    for k, v in out77.items():
        print(f"{k:24s} sig_true {v['sigma_true_median']} meas {v['sigma_meas_median']} bias {v['sigma_bias_median']} cov {v['sigma_coverage']}"
              f" q95 {v['sigma_q95']} res_frac {v['res_frac_median']} size {v['res_size_p05']} ge09 {v['res_frac_ge09']} q {v['q_median']}")


if __name__ == "__main__":
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else "")
