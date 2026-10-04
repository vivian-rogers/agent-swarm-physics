"""#51 segment check for the unit-of-analysis exception (card): human premium (content, reply) per H29 segment of
#51 next to the whole-period estimate, with random-effects partial pooling. Writes native/g51_segments.json.
Usage: uv run python hypotheses/H52-humans-loud-agents/analysis/segments.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h52lib as L  # noqa: E402
import estimate as E  # noqa: E402

import polars as pl  # noqa: E402

SEG = {"51a": ("2026-07-06", "2026-07-08"), "51b": ("2026-07-09", "2026-08-04"), "51c": ("2026-08-05", "2026-08-24"),
       "51d": ("2026-08-25", "2026-09-02"), "51e": ("2026-09-03", "2026-09-04")}


def main(B: int = 500):
    R = pl.read_parquet(L.OUT / "G51" / "rows.parquet")
    out = {}
    for s, (a, b) in SEG.items():
        sub = R.filter((pl.col("pt_date") >= a) & (pl.col("pt_date") <= b))
        d = E.prepare(sub, con_col="chi_dd")
        res = E.analyze(d, B=B, placebo_draws=0, regression=False, classes=(1,), outcomes=("con", "rep"))
        out[s] = {oc: res[oc].get("human", {}).get("all", {}) for oc in ("con", "rep")}
        out[s]["human_msgs"] = int(sub.filter((pl.col("cls") == 1) & ~pl.col("kickoff"))["msg"].n_unique())
    for oc in ("con", "rep"):
        e = [out[s][oc].get("att") for s in SEG if out[s][oc].get("att") is not None]
        se = [out[s][oc].get("se") for s in SEG if out[s][oc].get("att") is not None]
        out[f"pooled_{oc}"] = L.re_pool(e, se)
    L.jdump(out, L.OUT / "native" / "g51_segments.json")
    for s in SEG:
        print(s, out[s]["human_msgs"], {oc: (round(out[s][oc].get("att", float("nan")) or float("nan"), 4), out[s][oc].get("ci")) for oc in ("con", "rep")})
    print({k: (round(v["pooled"], 4), v["ci"]) for k, v in out.items() if k.startswith("pooled")})


if __name__ == "__main__":
    main()
