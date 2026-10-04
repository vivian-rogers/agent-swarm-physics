"""H100 round 1 (exploratory, non-holdout): decomposition per period, movers, remanence, swap-carry, both models.

Writes data/processed/H100-room-symmetry-breaking/results/{raw_<model>_<variant>.json, results.json}.
Usage: uv run python hypotheses/H100-room-symmetry-breaking/analysis/run.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h100lib as L  # noqa: E402

RES = L.DATA / "results"
VARIANTS = [("bge_small", "style_resid"), ("gte_modernbert", "style_resid"), ("bge_small", "white32"),
            ("gte_modernbert", "white32")]
PAIRS = [(36, 37), (37, 38), (38, 39), (39, 41), (41, 42), (42, 44)]
NAMES = {20: "Claude Opus 4.6", 21: "Claude Sonnet 4.6", 22: "Gemini 3.1 Pro", 23: "GPT-5.4"}


def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items() if not str(k).startswith("_")}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    return o


def one(model, variant, full=True):
    tab, X = L.load(model, variant)
    Xc = L.day_center(tab, X)
    fields = pl.read_parquet(L.DATA / "fields.parquet")
    F = np.load(L.DATA / f"fields_{model}.npy")
    out = {"model": model, "variant": variant}
    out["invariance"] = L.constants_invariance(tab, Xc)
    out["periods"] = {}
    for P in L.MULTI:
        r = L.decompose(tab, Xc, fields, F, P, n_null=2000 if full else 500, n_boot=500 if full else 0, seed=P)
        out["periods"][f"G{P}"] = r
    out["movers"] = {b: L.mover_index(tab, Xc, b, n_boot=500 if full else 0, seed=7) for b in L.MOVES}
    out["remanence"] = {f"{a}-{b}": L.remanence(tab, Xc, fields, F, a, b, n_null=2000, seed=a) for a, b in PAIRS}
    out["remanence_raw"] = {f"{a}-{b}": L.remanence(tab, Xc, fields, F, a, b, n_null=2000, seed=a, spont=False)
                            for a, b in PAIRS}
    out["swap_carry"] = L.swap_carry(tab, Xc, 38, 39)
    return clean(out)


def main():
    RES.mkdir(parents=True, exist_ok=True)
    allr = {}
    for model, variant in VARIANTS:
        full = variant == "style_resid"
        r = one(model, variant, full=full)
        allr[f"{model}/{variant}"] = r
        (RES / f"raw_{model}_{variant}.json").write_text(json.dumps(r, indent=1))
        print("done", model, variant, flush=True)
    (RES / "raw_all.json").write_text(json.dumps(allr, indent=1))


def movers_only():
    """Recompute only the mover block (C_pre significance added 2026-10-04 after the first run) into raw files."""
    allr = json.loads((RES / "raw_all.json").read_text())
    for model, variant in VARIANTS:
        tab, X = L.load(model, variant)
        Xc = L.day_center(tab, X)
        full = variant == "style_resid"
        allr[f"{model}/{variant}"]["movers"] = clean({b: L.mover_index(tab, Xc, b, n_boot=500 if full else 0, seed=7)
                                                     for b in L.MOVES})
        (RES / f"raw_{model}_{variant}.json").write_text(json.dumps(allr[f"{model}/{variant}"], indent=1))
    (RES / "raw_all.json").write_text(json.dumps(allr, indent=1))


if __name__ == "__main__":
    if "--movers-only" in sys.argv:
        movers_only()
    else:
        main()
