"""H17 scheme: freeze categorical state tables (via H14's builder) and add 5-min windows and covariates.

States come from H14's `scheme/build_states.py: build(days)` (imported, not copied; see the H17 card). This script
writes H17's own copies so that a rebuild by H14 cannot change H17's inputs mid-round.

Outputs (data/processed/H17-behavior-metastable-sets/), non-holdout days only:
  states_min.parquet    pt_date, goal_no, regime, agent, minute, coarse_min, n_rec, present
  states_turn.parquet   pt_date, goal_no, regime, agent, t, act, coarse          (records; coarse = -1 removed)
  states_win5.parquet   pt_date, goal_no, agent, w (= minute // 5), n_min, hard, p_0..p_5 (fractions of minutes)
  covariates.parquet    pt_date, goal_no, agent, n_turns, n_error, n_output, present_min
  _provenance.json

Holdout days are never read here. The confirmatory script builds its days in memory with `build_for_days`.

Usage: uv run python hypotheses/H17-behavior-metastable-sets/scheme/build.py
"""
from __future__ import annotations

import os

os.environ.setdefault("POLARS_MAX_THREADS", "2")

import datetime as dt
import importlib.util
import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H17-behavior-metastable-sets"
H14_BUILDER = ROOT / "hypotheses/H14-behavior-entropy-production/scheme/build_states.py"
COARSE = ["browse", "type", "shell", "chat", "idle", "consolidate"]
TIE_PRIORITY = {3: 6, 5: 5, 2: 4, 1: 3, 0: 2, 4: 1}  # chat > consolidate > shell > type > browse > idle
OUTPUT_VERBS = ["git commit", "git push", "deploy"]


def h14():
    spec = importlib.util.spec_from_file_location("h14_build_states", H14_BUILDER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def builder_sha256() -> str:
    import hashlib
    return hashlib.sha256(H14_BUILDER.read_bytes()).hexdigest()


def win5(states_min: pl.DataFrame) -> pl.DataFrame:
    q = len(COARSE)
    sm = states_min.filter(pl.col("present")).with_columns((pl.col("minute") // 5).cast(pl.Int16).alias("w"))
    agg = sm.group_by("pt_date", "goal_no", "agent", "w").agg(
        [pl.len().cast(pl.Int8).alias("n_min")] + [(pl.col("coarse_min") == k).sum().cast(pl.Int8).alias(f"c_{k}") for k in range(q)])
    C = agg.select([f"c_{k}" for k in range(q)]).to_numpy().astype(np.float64)
    pri = np.array([TIE_PRIORITY[k] for k in range(q)]) * 1e-3
    hard = (C + pri[None, :]).argmax(1)
    P = C / np.clip(C.sum(1, keepdims=True), 1, None)
    out = agg.select("pt_date", "goal_no", "agent", "w", "n_min").with_columns(
        [pl.Series("hard", hard.astype(np.int8))] + [pl.Series(f"p_{k}", P[:, k].astype(np.float32)) for k in range(q)])
    return out.sort("pt_date", "agent", "w")


def covariates(days: list[str], states_min: pl.DataFrame) -> pl.DataFrame:
    dset = set(days)
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "goal_no"]).filter(pl.col("pt_date").is_in(dset))
    ptd = pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.Utf8).alias("pt_date")
    acts = (pl.scan_parquet(SH / "actions.parquet").select("t", "agent", "error").with_columns(ptd)
            .filter(pl.col("pt_date").is_in(dset))
            .group_by("pt_date", "agent").agg(pl.len().alias("n_turns"), pl.col("error").sum().alias("n_error")).collect())
    out_ev = (pl.scan_parquet(SH / "artifact_mentions.parquet").select("t", "agent", "source", "verb", "ref_index")
              .filter((pl.col("source") == "action") & pl.col("verb").cast(pl.Utf8).is_in(OUTPUT_VERBS) & pl.col("agent").is_not_null())
              .with_columns(ptd).filter(pl.col("pt_date").is_in(dset))
              .group_by("pt_date", "agent").agg(pl.col("ref_index").n_unique().alias("n_output")).collect())
    pres = (states_min.filter(pl.col("present")).group_by("pt_date", "agent").agg(pl.len().alias("present_min")))
    cov = (pres.join(acts.with_columns(pl.col("agent").cast(pl.Int8)), on=["pt_date", "agent"], how="left")
           .join(out_ev.with_columns(pl.col("agent").cast(pl.Int8)), on=["pt_date", "agent"], how="left")
           .join(cal, on="pt_date", how="left")
           .with_columns(pl.col("n_turns").fill_null(0), pl.col("n_error").fill_null(0), pl.col("n_output").fill_null(0)))
    return cov.select("pt_date", "goal_no", "agent", "n_turns", "n_error", "n_output", "present_min").sort("pt_date", "agent")


def build_for_days(days: list[str]):
    """In-memory build for any list of PT days (used by the confirmatory script for holdout days)."""
    mod = h14()
    audit: dict = {}
    st, sm = mod.build(days, audit)
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "goal_no", "regime"]).with_columns(pl.col("regime").cast(pl.Utf8))
    sm = sm.join(cal, on="pt_date", how="left").select("pt_date", "goal_no", "regime", "agent", "minute", "coarse_min", "n_rec", "present")
    st = st.select("pt_date", "goal_no", "regime", "agent", "t", "act", "coarse")
    return st, sm, audit


def main():
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    mod = h14()
    days = mod.nonholdout_days()
    st, sm, audit = build_for_days(days)
    w5 = win5(sm)
    cov = covariates(days, sm)
    st.write_parquet(OUT / "states_turn.parquet", compression="zstd")
    sm.write_parquet(OUT / "states_min.parquet", compression="zstd")
    w5.write_parquet(OUT / "states_win5.parquet", compression="zstd")
    cov.write_parquet(OUT / "covariates.parquet", compression="zstd")
    prov_path = OUT / "_provenance.json"
    prov = json.loads(prov_path.read_text()) if prov_path.exists() else {}
    prov["states"] = {
        "built_by": "hypotheses/H17-behavior-metastable-sets/scheme/build.py (states via hypotheses/H14-behavior-entropy-production/scheme/build_states.py: build)",
        "git_commit": git_commit(),
        "inputs": [{"source": "ai-village", "revision": REVISION,
                    "tables": ["shared/actions", "shared/events_core", "shared/calendar", "shared/roster", "shared/artifact_mentions"]}],
        "params": {"days": "calendar.holdout == False", "coarse": COARSE, "win5": "w = minute // 5; hard = majority, ties chat>consolidate>shell>type>browse>idle; present agent-days only",
                   "output_verbs": OUTPUT_VERBS, "h14_builder_sha256": builder_sha256(), "h14_audit_rows": {"states_turn": st.height, "states_min": sm.height}},
        "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    prov_path.write_text(json.dumps(prov, indent=1))
    print({"days": len(days), "states_turn": st.height, "states_min": sm.height, "win5": w5.height, "cov": cov.height,
           "secs": round(time.time() - t0, 1)})


if __name__ == "__main__":
    main()
