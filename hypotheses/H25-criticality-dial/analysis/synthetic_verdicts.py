"""Score the card's synthetic predictions S1-S4 from synthetic.py's outputs (with and without the x1.5 interval widening).

Usage: uv run python hypotheses/H25-criticality-dial/analysis/synthetic_verdicts.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h25common as C  # noqa: E402
import polars as pl  # noqa: E402

import dial as D  # noqa: E402

SYN = C.OUT / "synthetic"


def cov(d, truth, f):
    lo = d["g"] - f * (d["g"] - d["lo"]); hi = (d["g"] + f * (d["hi"] - d["g"])).clip(upper_bound=1.0)
    return float(((lo <= d[truth]) & (hi >= d[truth])).mean())


def main():
    b = pl.read_parquet(SYN / "binary.parquet")
    h = pl.read_parquet(SYN / "hawkes.parquet")
    c = pl.read_parquet(SYN / "content.parquet")
    bs = b.filter((pl.col("field") == "slow") & (pl.col("p_idle") == 0.3))
    out = {}
    eq = bs.filter(pl.col("mode").is_in(["gibbs", "async"]) & (pl.col("variant") == "auto"))
    s1 = []
    for (mode, J), d in eq.group_by(["mode", "J"]):
        s1.append({"mode": mode, "J": J, "truth": float(d["g_true"].median()), "bias": float((d["g"] - d["g_true"]).median()),
                   "cov_raw": cov(d, "g_true", 1.0), "cov_x1.5": cov(d, "g_true", D.SE_INFLATE),
                   "fp_lo_gt0": float((d["lo"] > 0).mean()) if J == 0 else None})
    s1 = sorted(s1, key=lambda r: (r["mode"], r["J"]))
    out["S1"] = {"cells": s1, "max_abs_bias_g_le_0.4": max(abs(r["bias"]) for r in s1 if r["truth"] <= 0.4),
                 "max_abs_bias_all": max(abs(r["bias"]) for r in s1), "verdict": "mixed (bias <= 0.04 for g <= 0.4; -0.06 to -0.08 near g = 0.5; coverage needs the x1.5 widening)"}
    st = {}
    for var in ("none", "auto", "lull", "oracle"):
        d = bs.filter((pl.col("variant") == var) & pl.col("mode").is_in(["gibbs", "async"]) & (pl.col("J") <= 0.2))
        st[var] = {"bias_with_outages": float((d.filter(pl.col("outages"))["g"] - d.filter(pl.col("outages"))["g_true"]).median()),
                   "bias_no_outages": float((d.filter(~pl.col("outages"))["g"] - d.filter(~pl.col("outages"))["g_true"]).median())}
    a = b.filter((pl.col("variant") == "auto") & pl.col("outages"))
    small = bs.filter((pl.col("N") <= 6) & pl.col("mode").is_in(["gibbs", "async"]) & (pl.col("J") == 0) & ~pl.col("outages"))
    out["S2"] = {"by_variant_low_g": st, "outage_minutes_caught": float(a["auto_hit"].sum() / a["out_min"].sum()),
                 "false_stall_minute_share": float(b.filter((pl.col("variant") == "auto") & ~pl.col("outages")).select((pl.col("auto_masked") / pl.col("T")).mean()).item()),
                 "lull_bias_N_le_6_g0": float(small.filter(pl.col("variant") == "lull")["g"].median()), "verdict": "supported"}
    dl = bs.filter((pl.col("mode") == "delay") & (pl.col("variant") == "auto")).group_by("J").agg(pl.col("g_true").median(), pl.col("g").median()).sort("J")
    hk = h.filter(pl.col("variant") == "auto").group_by("tau", "n_x").agg(pl.col("g_DC").first(), pl.col("g").median(), pl.col("g_map").first()).sort("tau", "n_x")
    out["S3"] = {"delay_CW": dl.to_dicts(), "hawkes": hk.to_dicts(), "hawkes_fast_cov_x1.5": cov(h.filter((pl.col("tau") == 20) & (pl.col("variant") == "auto")), "g_DC", D.SE_INFLATE),
                 "verdict": "failed (delayed reads: dial ~0 at every coupling; slow Hawkes: factor 0.2-0.3; fast Hawkes: factor ~1)"}
    cc = c.filter(pl.col("variant").is_in(["F1", "F2", "noSH"])).group_by("exo", "noise", "variant", "J").agg(pl.col("g_true").median(), pl.col("g").median()).sort("exo", "noise", "variant", "J")
    out["S4"] = {"cells": cc.to_dicts(), "content_cov_x1.5_exo0": cov(c.filter((pl.col("variant") == "F2") & (pl.col("exo") == 0)), "g_true", D.SE_INFLATE),
                 "verdict": "failed (F2 leaves 0.20-0.26 of a 0.26-0.30 leak; noise correction recovers g within ~0.09)"}
    (C.OUT / "results").mkdir(parents=True, exist_ok=True)
    (C.OUT / "results/synthetic_verdicts.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps({k: v["verdict"] for k, v in out.items()}, indent=1))
    print(json.dumps(out["S2"], indent=1, default=float))


if __name__ == "__main__":
    main()
