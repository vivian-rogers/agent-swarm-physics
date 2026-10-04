"""H106 scheme: block tables with active population N_b and active-day index a_b (no text; holdout masked).

Inputs (shared): data/processed/shared/culture_vectors/ (agentdays, blocks; built by infra/shared/culture_vectors.py,
non-holdout), activity_bins_fixed (active population), calendar (run days), roster (Claude Code flag).
  N_d   active population (H85 rule, whole day): agents with >= 1 record (turn, talk, idle, consolidate, other event)
        on PT day d, Claude Code agents excluded; computed on NON-holdout days only (holdout_mask asserted)
  a(d)  active-day index: rank of d among village run days (calendar rows); only the existence of a run day is used
  N_b   mean N_d over the block's eligible days; n_members = eligible members (culture_vectors blocks.n_agents)
  a_b   mean a(d) over the block's eligible days
Output: data/processed/H106-slow-mode-finite-size/{nday.parquet, blocks_I.parquet, blocks_III.parquet,
        aday.parquet, _provenance.json}
Usage: uv run python hypotheses/H106-slow-mode-finite-size/scheme/build.py
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit, holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
CV = SH / "culture_vectors"
OUT = ROOT / "data/processed/H106-slow-mode-finite-size"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ad = pl.read_parquet(CV / "agentdays.parquet")
    blocks = pl.read_parquet(CV / "blocks.parquet")
    assert not ad["holdout"].any()
    # active-day index over all run days (existence of a run day only)
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "goal_no"]).sort("pt_date")
    aday = cal.select("pt_date").unique().sort("pt_date").with_row_index("a").with_columns(pl.col("a").cast(pl.Float64))
    # active population on non-holdout days
    days = sorted(set(ad["pt_date"].to_list()))
    gmap = dict(zip(cal["pt_date"].to_list(), cal["goal_no"].to_list()))
    hm = holdout_mask(days, [gmap.get(d) for d in days])
    days = [d for d, h in zip(days, hm) if not h]
    cc = set(pl.read_parquet(SH / "roster.parquet").filter(pl.col("claude_code"))["agent"].to_list())
    act = (pl.scan_parquet(SH / "activity_bins_fixed.parquet")
           .filter(pl.col("pt_date").is_in(days) & ~pl.col("agent").is_in(list(cc)))
           .filter((pl.col("turns") + pl.col("talk") + pl.col("idle") + pl.col("consolidate") + pl.col("other_event")) > 0)
           .group_by("pt_date").agg(pl.col("agent").n_unique().alias("N_d")).collect())
    nday = pl.DataFrame({"pt_date": days}).join(act, on="pt_date", how="left").join(aday, on="pt_date", how="left")
    assert nday["a"].null_count() == 0
    nday.write_parquet(OUT / "nday.parquet")
    aday.write_parquet(OUT / "aday.parquet")
    for regime in ("I", "III"):
        a2 = ad.filter(pl.col("regime") == regime).join(nday, on="pt_date", how="left")
        bt = (a2.group_by("block").agg(pl.col("pt_date").unique().alias("days"))
              .with_columns(pl.col("days").list.len().alias("n_days_elig")))
        rows = []
        nd = dict(zip(nday["pt_date"].to_list(), nday["N_d"].to_list()))
        ai = dict(zip(nday["pt_date"].to_list(), nday["a"].to_list()))
        for b, ds in zip(bt["block"].to_list(), bt["days"].to_list()):
            rows.append({"block": b, "N_b": float(np.mean([nd[d] for d in ds if nd[d] is not None])),
                         "a_b": float(np.mean([ai[d] for d in ds]))})
        bl = blocks.filter(pl.col("regime") == regime).join(pl.DataFrame(rows), on="block", how="left") \
            .rename({"n_agents": "n_members"}).sort("a_b")
        bl.write_parquet(OUT / f"blocks_{regime}.parquet")
        pl.Config.set_tbl_rows(100); print(regime, bl.select("block", "goal_no", "n_days", "n_members", "N_b", "a_b"))
    prov = {"built_by": "hypotheses/H106-slow-mode-finite-size/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["shared/culture_vectors (agentdays, blocks)", "activity_bins_fixed", "calendar",
                                   "roster"]}],
            "params": {"N_d": "agents with >=1 record (turn/talk/idle/consolidate/other) on the PT day, Claude Code "
                              "excluded, non-holdout days only", "a": "rank among calendar run days",
                       "holdout": "masked (culture_vectors default build + holdout_mask on days)"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))


if __name__ == "__main__":
    main()
