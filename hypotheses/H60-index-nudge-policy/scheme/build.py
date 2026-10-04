"""H60 scheme: regime-III idle gates from the shared table, with trap-chain ids and the nudger-on flag.

Output: data/processed/H60-index-nudge-policy/gates.parquet (+ _provenance.json). Codes and numbers only.
  periods: G37-G44 (long-pause regime III, before NE44 on 06-11) and G51 (short pauses); holdout already excluded.
  chain    a trap chain = consecutive gates of one agent-day between active calls (k_any restarts at 1)
  nudged   the gate read >= 1 nudge whose leading @ is the agent (n_nudge_me > 0)
  nudger_on  day <= 2026-08-20 (NE43: the nudger's last nudge is on 08-20)
Usage: uv run python hypotheses/H60-index-nudge-policy/scheme/build.py
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit, holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H60-index-nudge-policy"
PERIODS = (37, 38, 39, 40, 41, 42, 44, 51)
NUDGER_LAST_DAY = "2026-08-20"


def main():
    g = (pl.read_parquet(SH / "idle_gates/idle_gates.parquet")
         .filter(pl.col("goal_no").is_in(PERIODS) & (pl.col("regime") == "III"))
         .sort("agent", "pt_date", "t_call"))
    hm = holdout_mask(g["pt_date"].to_list(), g["goal_no"].to_list())
    assert not any(hm), "holdout rows present"
    g = g.with_columns((pl.col("k_any") == 1).cast(pl.Int32).cum_sum().alias("chain"),
                       (pl.col("n_nudge_me") > 0).alias("nudged"),
                       (pl.col("pt_date") <= NUDGER_LAST_DAY).alias("nudger_on"))
    OUT.mkdir(parents=True, exist_ok=True)
    g.write_parquet(OUT / "gates.parquet", compression="zstd")
    prov = {"built_by": "hypotheses/H60-index-nudge-policy/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["idle_gates (infra/shared/idle_gates.py)"]}],
            "params": {"periods": PERIODS, "nudger_last_day": NUDGER_LAST_DAY}, "rows": g.height,
            "built_at": dt.datetime.now(dt.UTC).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print(g.group_by("goal_no").agg(pl.len(), pl.col("nudged").sum(), pl.col("chain").n_unique()).sort("goal_no"))


if __name__ == "__main__":
    main()
