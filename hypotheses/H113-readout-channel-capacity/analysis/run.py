"""H113 round 1: per-period capacity exponent, information curve, placebo, recency and discrete check, both models;
pooled summaries (P1a-P8) and natives (G51 D2 wakes, NE03 #10a/#10b, NE42 #39/#40/#41).

Usage: uv run python hypotheses/H113-readout-channel-capacity/analysis/run.py [--period 38 ...] [--no-discrete]
Reads data/processed/H113-readout-channel-capacity/G<NN>/ (scheme/build.py). Writes results/{periods.json, pooled.json,
natives.json}.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "scheme"))
import h113lib as L  # noqa: E402
import h113scheme as S  # noqa: E402

D = S.ROOT / "data/processed/H113-readout-channel-capacity"
RES = D / "results"
MODELS = ("bge_small", "gte_modernbert")
NE03_DAYS = {"10a": ["2025-08-18", "2025-08-19"], "10b": ["2025-08-20", "2025-08-21", "2025-08-22"]}


def analyse(c: pl.DataFrame, it: pl.DataFrame, discrete: bool = True, seed: int = 0) -> dict:
    out = {"n_calls": len(c), "n_k1": int((c["k"] >= 1).sum()), "n_k8": int((c["k"] >= 8).sum())}
    out["testable"] = out["n_k1"] >= 300 and out["n_k8"] >= 30
    if out["n_k1"] < 30:
        return out
    out["fit"] = L.fit_b(c, seed=seed)                                   # primary (with the in-flight term)
    out["fit_noF"] = L.fit_b(c, with_F=False, seed=seed)
    out["fit_k1"] = L.fit_b(c.filter(pl.col("k1") >= 1), k_col="k1", ys="ys1", ss="s1s1", with_F=False, seed=seed) \
        if (c["k1"] >= 1).sum() >= 30 else {}
    out["binned"] = L.binned(c, seed=seed)
    out["info"] = L.info_curve(c, seed=seed)
    idb = [x for x in out["info"] if x["identified"]]
    out["a_I"] = L.slope_loglog([x["k_mean"] for x in idb], [x["I_bits"] for x in idb], [x["n"] for x in idb])["slope"] \
        if len(idb) >= 2 else None
    out["n_info_identified"] = len(idb)
    out["redundancy"] = L.redundancy(c)
    b = out["fit"].get("b"); r = out["redundancy"]["r"]
    out["a_I_pred"] = (1 - 2 * b + r) if b is not None and np.isfinite(r) else None
    out["placebo"] = L.placebo_contrast(c, it, seed=seed)
    out["recency"] = L.recency(c, it, seed=seed)
    pc = out["placebo"]; rr = out["redundancy"]["r"]
    out["identified"] = bool(pc.get("lo") is not None and pc["lo"] > 0 and np.isfinite(rr) and rr < 0.7)  # A1 rule
    f = out["fit"]
    if "a_U" in f:
        out["a_U_includes_0.34"] = bool(f["a_U_lo"] <= 0.34 <= f["a_U_hi"])
        out["a_U_includes_0.50"] = bool(f["a_U_lo"] <= 0.50 <= f["a_U_hi"])   # Note N1 (corrected H18 D2 value)
    out["low_snr"] = bool(all(x["R2"] < 0.05 for x in out["info"]))
    if discrete:
        try:
            out["discrete"] = L.discrete_check(c, it, seed=seed)
        except Exception as e:  # noqa: BLE001
            out["discrete"] = {"error": str(e)}
    return out


def load(g: int, model: str, prefix: str = ""):
    d = D / f"G{g:02d}"
    c = pl.read_parquet(d / f"{prefix}calls_{model}.parquet")
    it = pl.read_parquet(d / f"{prefix}items_{model}.parquet")
    return c, it


def verdict(o: dict) -> str:
    if not o.get("testable"):
        return "descriptive"
    if not any(o[m].get("identified") for m in MODELS if m in o):
        return "descriptive"   # A1: not identified against a field (placebo CI not > 0, or r >= 0.7)
    fits = [o[m]["fit"] for m in MODELS if m in o and "fit" in o[m] and "a_U" in o[m]["fit"]]
    if not fits:
        return "descriptive"
    inc = [f["a_U_lo"] <= 0.34 <= f["a_U_hi"] for f in fits]
    ex01 = [f["b_lo"] > 0 and f["b_hi"] < 1 for f in fits]
    if all(not x for x in inc):
        return "failed"
    if all(inc) and all(ex01):
        return "supported"
    return "mixed"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", type=int, action="append")
    ap.add_argument("--no-discrete", action="store_true")
    a = ap.parse_args()
    RES.mkdir(parents=True, exist_ok=True)
    periods = a.period or sorted(int(p.name[1:]) for p in D.glob("G*") if (p / "calls_bge_small.parquet").exists())
    pf = RES / "periods.json"
    per = json.loads(pf.read_text()) if pf.exists() and a.period else {}
    for g in periods:
        o = {"goal_no": g}
        for m in MODELS:
            c, it = load(g, m)
            o[m] = analyse(c, it, discrete=not a.no_discrete, seed=g)
            o["testable"] = o[m].get("testable", False)
            cF = pl.read_parquet(D / f"G{g:02d}/calls_{m}_F.parquet")
            o[m]["fit_F"] = L.fit_b(cF, seed=g)                          # A1 sensitivity: window-field projection
        o["verdict"] = verdict(o)
        per[str(g)] = o
        f = o["bge_small"].get("fit", {}); f2 = o["gte_modernbert"].get("fit", {})
        print(g, o["verdict"], "n", o["bge_small"].get("n_k1"), "b bge", f.get("b"), (f.get("b_lo"), f.get("b_hi")),
              "gte", f2.get("b"), (f2.get("b_lo"), f2.get("b_hi")), flush=True)
        pf.write_text(json.dumps(per, indent=1, default=float))
    pooled = {}
    for m in MODELS:
        T = [o[m]["fit"] for o in per.values() if o.get("testable") and o[m].get("identified") and "a_U" in o[m].get("fit", {})]
        Tall = [o[m]["fit"] for o in per.values() if o.get("testable") and "a_U" in o[m].get("fit", {})]
        pooled.setdefault("all_testable", {})[m] = {
            "a_U": L.dl_pool([t["a_U"] for t in Tall], [t["a_U_lo"] for t in Tall], [t["a_U_hi"] for t in Tall]), "k": len(Tall)}
        pooled[m] = {"a_U": L.dl_pool([t["a_U"] for t in T], [t["a_U_lo"] for t in T], [t["a_U_hi"] for t in T]),
                     "b": L.dl_pool([t["b"] for t in T], [t["b_lo"] for t in T], [t["b_hi"] for t in T]),
                     "k": len(T), "identified_periods": [int(g) for g, o in per.items() if o.get("testable") and o[m].get("identified")],
                     "P1a_point_in_band": int(sum(0.24 <= t["a_U"] <= 0.44 for t in T)),
                     "P2_b_gt0": int(sum(t["b_lo"] > 0 for t in T)), "P3_b_lt1": int(sum(t["b_hi"] < 1 for t in T)),
                     "edge": int(sum(t["boot_edge_share"] > 0.1 for t in T))}
        aI = [(o[m]["a_I"], o[m]["a_I_pred"]) for o in per.values() if o.get("testable") and o[m].get("a_I") is not None
              and o[m].get("a_I_pred") is not None]
        pooled[m]["a_I_values"] = aI
        pl_ = [o[m]["placebo"] for o in per.values() if o.get("testable") and o[m].get("placebo", {}).get("lo") is not None]
        pooled[m]["placebo"] = L.dl_pool([p["contrast"] for p in pl_], [p["lo"] for p in pl_], [p["hi"] for p in pl_])
        gF = [(o[m]["fit"]["gammaF"], o[m]["fit"]["gamma1"]) for o in per.values() if o.get("testable") and "gammaF" in o[m].get("fit", {})]
        pooled[m]["gammaF_over_gamma1"] = [float(x / y) if y else None for x, y in gF]
        rc = [o[m]["recency"] for o in per.values() if o.get("testable") and o[m].get("recency", {}).get("lo") is not None]
        pooled[m]["recency"] = L.dl_pool([r["diff"] for r in rc], [r["lo"] for r in rc], [r["hi"] for r in rc])
        dc = [o[m].get("discrete") for o in per.values() if o.get("testable") and isinstance(o[m].get("discrete"), list)]
        pooled[m]["P8_k1_identified"] = {"k": int(sum(any(x["bin"] == "1-1" and x["identified"] for x in d) for d in dc)), "n": len(dc)}
    tb = [(o["bge_small"]["fit"]["b"], o["gte_modernbert"]["fit"]["b"]) for o in per.values() if o.get("testable")
          and "b" in o["bge_small"].get("fit", {}) and "b" in o["gte_modernbert"].get("fit", {})]
    pooled["P6_models_within_0.2"] = {"k": int(sum(abs(x - y) <= 0.2 for x, y in tb)), "n": len(tb)}
    reg = pl.read_parquet(S.SHARED / "period_units.parquet").group_by("goal_no").agg(pl.col("regime").first())
    rmap = dict(reg.iter_rows())
    for m in MODELS:
        for R in ("I", "II", "III"):
            T = [o[m]["fit"] for g, o in per.items() if o.get("testable") and rmap.get(int(g)) == R and "b" in o[m].get("fit", {})]
            pooled[m][f"b_regime_{R}"] = L.dl_pool([t["b"] for t in T], [t["b_lo"] for t in T], [t["b_hi"] for t in T])
    (RES / "pooled.json").write_text(json.dumps(pooled, indent=1, default=float))
    print(json.dumps(pooled, indent=1, default=float)[:5000])


if __name__ == "__main__":
    main()
