"""Distribute the cross-period output tables into per-period folders data/processed/H03-.../G<NN>/
(folder convention 2026-10-03). The cross-period tables stay at the top level for the phase diagram and
heterogeneity summaries. Run: uv run python hypotheses/H03-self-excited-criticality/analysis/split_by_period.py
"""
from __future__ import annotations

import datetime as dt
import json

import polars as pl

from common import DATA, gdir

TABLES = ["period_fits", "period_cv", "period_boot", "synthetic_guard", "cascades", "jitter_test", "segments",
          "segments_boot", "attribution", "period_table", "segment_table", "jitter_table"]


def main():
    written = {}
    for name in TABLES:
        p = DATA / f"{name}.parquet"
        if not p.exists():
            continue
        df = pl.read_parquet(p)
        for (g,), sub in df.partition_by("goal_no", as_dict=True).items():
            gdir(int(g)).mkdir(parents=True, exist_ok=True)
            sub.write_parquet(gdir(int(g)) / f"{name}.parquet", compression="zstd")
            written.setdefault(int(g), []).append(name)
    for name in ("rolling51", "rolling51_boot"):
        p = DATA / f"{name}.parquet"
        if p.exists():
            pl.read_parquet(p).write_parquet(gdir(51) / f"{name}.parquet", compression="zstd")
            written.setdefault(51, []).append(name)
    for g, names in written.items():
        prov = {"built_by": "hypotheses/H03-self-excited-criticality/analysis/split_by_period.py",
                "inputs": [f"data/processed/H03-self-excited-criticality/{n}.parquet" for n in names],
                "params": {"goal_no": g, "fits": "fits/<SET>_<MODEL>.npy written by analysis/fit_periods.py"},
                "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
        (gdir(g) / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print("periods:", len(written))


if __name__ == "__main__":
    main()
