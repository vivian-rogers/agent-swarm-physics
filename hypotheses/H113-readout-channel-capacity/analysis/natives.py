"""H113 natives: G51 D2 timer-wake batches (exogenous k), NE03 (#10a vs #10b chat fetch limit), NE42 (#39 -> #40 -> #41
room merge and split). Reads the scheme outputs and results/periods.json; writes results/natives.json.
Usage: uv run python hypotheses/H113-readout-channel-capacity/analysis/natives.py
"""
from __future__ import annotations

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
NE03 = {"10a": ["2025-08-18", "2025-08-19"], "10b": ["2025-08-20", "2025-08-21", "2025-08-22"]}


def slim(f: dict) -> dict:
    out = {k: f.get(k) for k in ("n", "b", "b_lo", "b_hi", "a_U", "a_U_lo", "a_U_hi", "gamma1", "gammaF", "k_mean", "boot_edge_share")}
    if f.get("a_U") is not None:
        out["incl_0.34"] = f["a_U_lo"] <= 0.34 <= f["a_U_hi"]; out["incl_0.50"] = f["a_U_lo"] <= 0.50 <= f["a_U_hi"]
    return out


def main():
    per = json.loads((RES / "periods.json").read_text())
    out = {"G51_D2": {}, "NE03": {}, "NE42": {}}
    for m in MODELS:
        # G51 D2 wakes
        wc = D / f"G51/wcalls_{m}.parquet"
        if wc.exists():
            c = pl.read_parquet(wc)
            f = L.fit_b(c, seed=51)
            bt = per["51"][m]["fit"]
            wi = pl.read_parquet(D / f"G51/witems_{m}.parquet")
            out["G51_D2"][m] = {"wake": slim(f), "placebo": L.placebo_contrast(c, wi, seed=51), "redundancy": L.redundancy(c), "talk_b": bt["b"], "diff": (f.get("b", np.nan) - bt["b"]) if f.get("b") is not None else None,
                                "pass_within_0.15": bool(f.get("b") is not None and abs(f["b"] - bt["b"]) <= 0.15),
                                "binned": L.binned(c, seed=51)}
        # NE03
        c10 = pl.read_parquet(D / f"G10/calls_{m}.parquet") if (D / f"G10/calls_{m}.parquet").exists() else None
        if c10 is not None:
            r = {}
            for side, days in NE03.items():
                cs = c10.filter(pl.col("pt_date").is_in(days))
                r[side] = {**slim(L.fit_b(cs, seed=10)), "n_k1": int((cs["k"] >= 1).sum()), "n_k8": int((cs["k"] >= 8).sum()),
                           "binned": L.binned(cs, seed=10)}
            bb = r["10b"].get("b"); ba = r["10a"].get("b")
            r["diff_b"] = (bb - ba) if bb is not None and ba is not None else None
            r["powered"] = all(r[s]["n_k1"] >= 300 and r[s]["n_k8"] >= 30 for s in NE03)
            out["NE03"][m] = r
        # NE42
        r = {}
        for g in (39, 40, 41):
            o = per.get(str(g), {}).get(m, {})
            f = o.get("fit", {})
            r[f"G{g}"] = {**slim(f), "testable": o.get("testable"), "n_k1": o.get("n_k1")}
        b = {g: r[f"G{g}"].get("b") for g in (39, 40, 41)}
        if all(v is not None for v in b.values()):
            r["d40_39"] = b[40] - b[39]; r["d40_41"] = b[40] - b[41]
            r["pass_invariance"] = abs(r["d40_39"]) < 0.2 and abs(r["d40_41"]) < 0.2
        km = {g: r[f"G{g}"].get("k_mean") for g in (39, 40, 41)}
        r["k_mean"] = km
        out["NE42"][m] = r
    (RES / "natives.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps({k: {m: (v.get(m, {}) if not isinstance(v.get(m), dict) else {kk: vv for kk, vv in v[m].items() if kk != "binned"})
                          for m in MODELS} for k, v in out.items()}, indent=1, default=float)[:6000])


if __name__ == "__main__":
    main()
