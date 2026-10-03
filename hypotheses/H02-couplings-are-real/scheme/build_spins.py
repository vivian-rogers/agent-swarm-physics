"""H02 scheme: binary activity spins per goal-period chunk (non-holdout only).

Builds data/processed/H02-couplings-are-real/spins.parquet:
  chunk (str "g<goal>c<k>"), goal_no, mode, regime, pt_date, day (0-based within chunk), minute, agent, state (1..4)
Spin s = +1 if state >= 3 (act or talk) else -1 (derived at analysis time).

Rules (card, "Data scheme"):
  - drop every holdout day (calendar.holdout), and assert via infra holdout_mask as well;
  - periods with > 5 active days are split into consecutive 5-day chunks; a trailing chunk is kept if >= 3 days;
  - present population per chunk: an activity_bins row on every day of the chunk AND >= 30 active bins.

Usage: uv run python hypotheses/H02-couplings-are-real/scheme/build_spins.py
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import git_commit, holdout_mask, REVISION  # noqa: E402

SHARED = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H02-couplings-are-real"

MODE_I = [10, 17, 20, 39, 41, 42]
MODE_C = [13, 18, 19, 24, 25, 26, 38, 40, 44]
CHUNK_DAYS, MIN_TAIL_DAYS, MIN_ACTIVE_BINS = 5, 3, 30


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cal = pl.read_parquet(SHARED / "calendar.parquet").select("pt_date", "goal_no", "regime", "holdout")
    goals = MODE_I + MODE_C
    cal = cal.filter(pl.col("goal_no").is_in(goals) & ~pl.col("holdout")).sort("pt_date")
    # belt and braces: the infra mask must agree that nothing here is held out
    hm = holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    assert not any(hm), "holdout day leaked into the H02 exploratory selection"

    rows = []
    for g in goals:
        days = cal.filter(pl.col("goal_no") == g)["pt_date"].to_list()
        reg = cal.filter(pl.col("goal_no") == g)["regime"].cast(pl.Utf8)[0]
        chunks = [days[i:i + CHUNK_DAYS] for i in range(0, len(days), CHUNK_DAYS)]
        if len(chunks) > 1 and len(chunks[-1]) < MIN_TAIL_DAYS:
            chunks = chunks[:-1]
        for k, ch in enumerate(chunks):
            for di, d in enumerate(ch):
                rows.append({"chunk": f"g{g:02d}c{k}", "goal_no": g, "mode": "I" if g in MODE_I else "C",
                             "regime": reg, "pt_date": d, "day": di})
    sel = pl.DataFrame(rows)
    ab = (pl.scan_parquet(SHARED / "activity_bins.parquet")
          .filter(pl.col("pt_date").is_in(sel["pt_date"].to_list()))
          .select("pt_date", "minute", "agent", "state").collect())
    df = sel.join(ab, on="pt_date", how="inner")

    # present population per chunk
    ndays = sel.group_by("chunk").agg(pl.len().alias("ndays"))
    pres = (df.group_by("chunk", "agent")
            .agg(pl.col("pt_date").n_unique().alias("nd"), (pl.col("state") >= 3).sum().alias("nact"))
            .join(ndays, on="chunk")
            .filter((pl.col("nd") == pl.col("ndays")) & (pl.col("nact") >= MIN_ACTIVE_BINS)))
    df = df.join(pres.select("chunk", "agent"), on=["chunk", "agent"], how="semi")
    df = df.with_columns(pl.col("day").cast(pl.Int8), pl.col("minute").cast(pl.Int16), pl.col("goal_no").cast(pl.Int8))
    df = df.sort("chunk", "day", "minute", "agent")
    df.write_parquet(OUT / "spins.parquet", compression="zstd")

    summ = (df.group_by("chunk", "goal_no", "mode", "regime")
            .agg(pl.col("pt_date").n_unique().alias("days"), pl.col("agent").n_unique().alias("N"),
                 (pl.col("state") >= 3).mean().round(3).alias("active_frac"))
            .sort("chunk"))
    dropped = (sel.join(ab, on="pt_date").group_by("chunk").agg(pl.col("agent").n_unique().alias("N_roster"))
               .join(summ.select("chunk", "N"), on="chunk"))
    with pl.Config(tbl_rows=50):
        print(summ.join(dropped.select("chunk", "N_roster"), on="chunk"))

    prov_path = OUT / "_provenance.json"
    prov = json.loads(prov_path.read_text()) if prov_path.exists() else {}
    prov["spins"] = {"built_by": "hypotheses/H02-couplings-are-real/scheme/build_spins.py", "git_commit": git_commit(),
                     "inputs": [{"source": "ai-village", "revision": REVISION,
                                 "tables": ["data/processed/shared/activity_bins.parquet",
                                            "data/processed/shared/calendar.parquet"]}],
                     "params": {"mode_I": MODE_I, "mode_C": MODE_C, "chunk_days": CHUNK_DAYS,
                                "min_tail_days": MIN_TAIL_DAYS, "min_active_bins": MIN_ACTIVE_BINS,
                                "spin": "+1 if state>=3 else -1", "holdout": "excluded (calendar.holdout + holdout_mask)"},
                     "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    prov_path.write_text(json.dumps(prov, indent=1))


if __name__ == "__main__":
    main()
