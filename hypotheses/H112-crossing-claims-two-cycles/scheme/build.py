"""Build data/processed/H112-crossing-claims-two-cycles/G<NN>/ (switches, pairs, solo, work pairs; codes only).

Usage: uv run python hypotheses/H112-crossing-claims-two-cycles/scheme/build.py [--period 38 --period 51 | --all]
Holdout days are dropped (h112scheme.period_days). Project names are hashed on output.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
from pathlib import Path

import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h112scheme as S  # noqa: E402
from common import REVISION, git_commit  # noqa: E402

OUT = S.ROOT / "data/processed/H112-crossing-claims-two-cycles"
# non-holdout periods with action touches (feasibility count, card)
ALL = [4, 11, 12, 13, 17, 18, 19, 20, 21, 23, 24, 25, 26, 27, 30, 31, 33, 35, 36, 37, 38, 39, 40, 41, 42, 44, 51]


def build(g: int) -> dict:
    t0 = time.time()
    r = S.build_period(g)
    d = OUT / f"G{g:02d}"
    d.mkdir(parents=True, exist_ok=True)
    S.hashed(r["switches"]).write_parquet(d / "switches.parquet", compression="zstd")
    S.hashed(r["pairs"]).write_parquet(d / "pairs.parquet", compression="zstd")
    S.hashed(r["solo"]).write_parquet(d / "solo.parquet", compression="zstd")
    if "work_pairs" in r:
        S.hashed(r["work_pairs"]).write_parquet(d / "work_pairs.parquet", compression="zstd")
    p = r["pairs"]
    cnt = {"goal_no": g, "days": len(r["days"]), "touches": r["n_touches"], "claims": r["n_claims"], "calls": r["n_calls"],
           "switch_ins": len(r["switches"]), "pairs": len(p), "solo": len(r["solo"]), "median_lag_s": r["median_lag"],
           "classes": {k: int(v) for k, v in (p.group_by("cls").len().iter_rows() if len(p) else [])},
           "work_commits": r.get("n_work"), "work_pairs": len(r.get("work_pairs", [])), "build_s": round(time.time() - t0, 1)}
    (d / "counts.json").write_text(json.dumps(cnt, indent=1))
    return cnt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", type=int, action="append")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    periods = ALL if a.all or not a.period else a.period
    OUT.mkdir(parents=True, exist_ok=True)
    allc = {}
    for g in periods:
        c = build(g)
        allc[g] = c
        print(json.dumps(c), flush=True)
    prov = {"built_by": "hypotheses/H112-crossing-claims-two-cycles/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["artifact_mentions", "artifacts", "project_mentions_chat", "call_windows",
                                   "context_ledger_items", "work_commits", "calendar", "roster", "goal texts (kickoff_naming, in memory)"]}],
            "params": {"W_PAIR_s": S.W_PAIR, "W_CLAIM_s": S.W_CLAIM, "REVISIT_s": S.REVISIT, "Ks": list(S.KS),
                       "lag_bins_s": list(S.LAG_BINS), "work_horizon_s": S.WORK_HORIZON, "periods": periods},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    pp = OUT / "_provenance.json"
    old = json.loads(pp.read_text()) if pp.exists() else {}
    old["scheme"] = prov
    pp.write_text(json.dumps(old, indent=1))


if __name__ == "__main__":
    main()
