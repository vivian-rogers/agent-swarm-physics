"""H142 post hoc diagnostics (2026-10-07, after the round-1 run; labelled post hoc in the card).
Why is the aligned-count curve flat on the scored periods? Variants on bge (and gte for #51):
  raw   P_c without the window field (H113 A1's raw projection), same centroids and FE;
  day   direction x room x day cells instead of direction x room x hour;
  raw+day both.
Usage: uv run python hypotheses/H142-langevin-torque-saturation/analysis/posthoc.py
Output: data/processed/H142-langevin-torque-saturation/results/posthoc.json
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h142lib as L  # noqa: E402

DATA = HERE.parents[2] / "data/processed/H142-langevin-torque-saturation"


def one(rows: pl.DataFrame, seed: int) -> dict:
    D = L.Design(rows)
    st = D.y_stats(rows["y"].to_numpy().astype(float))
    ll = L.oof_loglik(D, st)
    fd = L.fit_dummies(D, st, B=300, seed=seed)
    d = L.dll_summary(ll, "langevin", "linear", B=1000, seed=seed)
    return {"f": {k: [v["est"], v["lo"], v["hi"]] for k, v in fd["f"].items()},
            "newest": [fd["nuis"]["newest"][x] for x in ("est", "lo", "hi")],
            "nname": [fd["nuis"]["nname"][x] for x in ("est", "lo", "hi")] if "nname" in fd["nuis"] else None,
            "dll_L_lin": [d["dll"], d["lo"], d["hi"]],
            "contrast1": [fd["inflight"][x] for x in ("contrast", "contrast_lo", "contrast_hi")] if fd.get("inflight") else None}


def main():
    out = {}
    for g, models in ((13, ["bge_small"]), (38, ["bge_small"]), (51, ["bge_small", "gte_modernbert"])):
        d = DATA / f"G{g:02d}"
        for m in models:
            base = pl.read_parquet(d / f"rows_{m}.parquet")
            raw = pl.read_parquet(d / f"rows_{m}_raw.parquet")
            dayc = lambda r: r.with_columns(pl.col("pt_date").str.replace_all("-", "").cast(pl.Int32).alias("hour"))  # noqa: E731
            for name, r in (("card", base), ("raw", raw), ("day", dayc(base)), ("raw+day", dayc(raw))):
                out[f"G{g}|{m}|{name}"] = one(r, seed=g)
                x = out[f"G{g}|{m}|{name}"]
                print(g, m, name, {k: round(v[0], 4) for k, v in x["f"].items()}, "newest", [round(v, 4) for v in x["newest"]],
                      "dll", [round(v, 1) for v in x["dll_L_lin"]], flush=True)
            (DATA / "results/posthoc.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
