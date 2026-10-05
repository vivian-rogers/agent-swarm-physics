"""H74 round 2: shared loaders (day frame, catalog, D features, search-answer marker table). Non-reserved days only."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import polars as pl

import r2lib as R

ROOT = Path(__file__).resolve().parents[3]
OUT1 = ROOT / "data/processed/H74-change-detector"
OUT = OUT1 / "r2"
SH = ROOT / "data/processed/shared"
H36 = ROOT / "data/processed/H36-reorganization-alarm/r2"
MARKERS = ["h1", "h2", "h3", "bold", "b_star3", "b_star", "b_dash", "b_dot", "b_num", "emdash", "endash", "nonascii",
           "open0", "open1", "open2", "open3"]
CLASSES = ["scaffold_tool", "scaffold_prompt", "scaffold_family", "drive", "goal", "goal_prompt", "roster", "room",
           "undocumented"]
LABEL_MAP = {"drive": ["operator", "operator_schedule"]}
PLATFORM_POOL = ["scaffold_tool", "scaffold_family", "operator", "operator_schedule", "undocumented"]


def load_days():
    days = pl.read_parquet(OUT1 / "days.parquet")
    cal = pl.read_parquet(SH / "calendar.parquet").filter(pl.col("n_agent_events") > 0).sort("pt_date")
    cal_days = cal["pt_date"].to_list()
    held = dict(zip(cal_days, cal["holdout"].to_list()))
    prev_held = {d: (i > 0 and held[cal_days[i - 1]]) for i, d in enumerate(cal_days)}
    days = days.with_columns(pl.col("pt_date").replace_strict(prev_held, return_dtype=pl.Boolean).alias("gap_return"),
                             (pl.col("idx") >= 10).alias("has_baseline"))
    assert not any(held[d] for d in days["pt_date"].to_list()), "reserved day in the scored set"
    return days, cal_days


def load_frame() -> R.Frame:
    days, cal_days = load_days()
    ev = pl.read_parquet(OUT1 / "events.parquet")
    return R.Frame(days, cal_days, ev)


def d_raw(fr: R.Frame) -> dict[str, np.ndarray]:
    df = pl.DataFrame({"pt_date": fr.dl}).join(pl.read_parquet(OUT1 / "day_features.parquet"), on="pt_date", how="left")
    return {f: df[f].cast(pl.Float64).fill_null(np.nan).to_numpy() for f in R.D2_FEATURES}


def marker_day_table(fr: R.Frame | None = None):
    """Per H74 scored day: answers n, distinct searching agents, and per marker the answers / agents with it."""
    fr = fr or load_frame()
    sf = pl.read_parquet(OUT1 / "search_format.parquet").filter(pl.col("pt_date").is_in(fr.dl))
    pres = sf.select("pt_date", "agent",
                     *[(pl.col(f"f_{m}") > 0).alias(m) for m in MARKERS if not m.startswith("open")],
                     *[(pl.col("f_open") == int(m[-1])).alias(m) for m in MARKERS if m.startswith("open")])
    g = pres.group_by("pt_date").agg(pl.len().alias("n"), pl.col("agent").n_unique().alias("nag"),
                                     *[pl.col(m).sum().alias(m) for m in MARKERS],
                                     *[pl.col("agent").filter(pl.col(m)).n_unique().alias(f"ag_{m}") for m in MARKERS])
    full = pl.DataFrame({"pt_date": fr.dl}).join(g, on="pt_date", how="left").fill_null(0)
    tab = {m: full[m].to_numpy().astype(int) for m in MARKERS}
    tag = {m: full[f"ag_{m}"].to_numpy().astype(int) for m in MARKERS}
    return tab, full["n"].to_numpy().astype(int), full["nag"].to_numpy().astype(int), tag
