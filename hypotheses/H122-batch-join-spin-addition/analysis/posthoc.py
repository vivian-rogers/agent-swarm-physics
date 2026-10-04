"""H122 POST HOC checks (labelled; written 2026-10-04 after the first real-data pass).
  PH1  NE32 without the #51 kickoff day in PRE (PRE = 07-07, 07-08): does the constant shift still win?
  PH2  every event: MC vs MJn (separate couplings for newcomer reads that name the incumbent and for the rest).
Output: data/processed/H122-batch-join-spin-addition/posthoc/posthoc.json
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h122lib as L  # noqa: E402

ROOT = HERE.parents[2]
D = ROOT / "data/processed/H122-batch-join-spin-addition"
SH = ROOT / "data/processed/shared"


def main():
    spec = importlib.util.spec_from_file_location("b", HERE.parent / "scheme" / "build.py")
    B = importlib.util.module_from_spec(spec); spec.loader.exec_module(B)
    ev = pl.read_parquet(D / "events.parquet")
    out = {"PH1": None, "PH2": []}
    e = ev.filter(pl.col("event") == "NE32").to_dicts()[0]
    e2 = dict(e, pre=[d for d in e["pre"] if d != "2026-07-06"], event="NE32_nokick")
    cal = pl.read_parquet(SH / "calendar.parquet")
    cw, lt, cc, cca = B.load_shared()
    meta = B.build_event(e2, cw, lt, cc, cca, cal, out_dir=D / "posthoc")
    df = L.prep(pl.read_parquet(D / "posthoc" / "calls" / "NE32_nokick.parquet"))
    N = {0: meta["N_pre"], 1: meta["N_p12"], 2: meta["N_f37"]}
    fit = L.fit_models(df, N)
    sc = L.scores(fit, B=2000, seed=1)
    out["PH1"] = {"pre": e2["pre"], "n_calls_pre": meta["n_calls_pre"], **{k: v for k, v in sc.items() if k.startswith("d_")},
                  "delta": fit["par"]["delta"], "J_N": fit["par"]["J_N"]}
    for r in ev.filter(pl.col("eligible_windows")).to_dicts():
        df = L.prep(pl.read_parquet(D / "calls" / f"{r['event']}.parquet"))
        N = {0: r["N_pre"], 1: r["N_p12"], 2: r["N_f37"]}
        fit = L.fit_models(df, N)
        y, Z, bl = fit["y"], fit["Z"], fit["blocks"]
        e_, lo, hi = L.paired_boot(L.logloss(y, Z["MC"]), L.logloss(y, Z["MJn"]), bl, 2000, 1)
        out["PH2"].append({"event": r["event"], "d_C_Jn": e_, "lo": lo, "hi": hi,
                           "J_named": fit["par"]["J_named"], "J_unnamed": fit["par"]["J_unnamed"]})
    (D / "posthoc" / "posthoc.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out, indent=1, default=lambda x: round(float(x), 3)))


if __name__ == "__main__":
    main()
