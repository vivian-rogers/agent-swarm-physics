"""H91 scheme: per-day content and spin matrices for the eigenvector-rotation statistic.

Builds data/processed/<HYP>/ from shared tables only (no text, non-holdout days only; see daymat.py):
  content_<model>.npz                  per-day agent x window x 32 content deviations (kind- and agent-day-centered)
  content_<model>_style_resid_period.npz   the same from style-residualized vectors (shared-priors variant)
  content_<model>_restate.npz          the same without restatements (either model's self-repeat flag)
  spins.npz                            per-day activity spins and talk spins in the all-present window (DQ8 trim)
  rooms.parquet                        each agent's modal room per day (statements.room)
  days.parquet                         calendar facts per non-holdout day + eligibility per channel
  _provenance.json

Usage: uv run python hypotheses/H91-eigenvector-rotation-signal/scheme/build.py
(H92's scheme/build.py runs the identical daymat builder into its own folder.)
"""
from __future__ import annotations

import datetime as dt
import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import daymat as DM  # noqa: E402
from common import REVISION, git_commit  # noqa: E402  (infra/shared on sys.path via daymat)

HYP = HERE.parent.name
OUT = DM.ROOT / "data/processed" / HYP


def build(out: Path, built_by: str, with_activity_note: bool = False):
    t0 = time.time()
    out.mkdir(parents=True, exist_ok=True)
    cal = DM.calendar()
    elig = {}
    variants = [("white32", "none", ""), ("style_resid_period", "none", "_style_resid_period"), ("white32", "restate", "_restate")]
    for m in DM.MODELS:
        for var, ded, suf in variants:
            days = DM.build_content(m, var, ded)
            DM.save_days(out / f"content_{m}{suf}.npz", days, ("agents", "Z"))
            elig[f"content_{m}{suf}"] = {d: len(r["agents"]) for d, r in days.items()}
            print(f"content {m}{suf}: {len(days)} days ({time.time() - t0:.0f}s)", flush=True)
    sp = DM.build_spins()
    DM.save_days(out / "spins.npz", sp, ("agents", "act", "talk", "talk_ok", "act_ok", "minutes"))
    elig["talk"] = {d: int(r["talk_ok"].sum()) for d, r in sp.items()}
    elig["act"] = {d: int(r["act_ok"].sum()) for d, r in sp.items()}
    print(f"spins: {len(sp)} days ({time.time() - t0:.0f}s)", flush=True)
    DM.modal_rooms().write_parquet(out / "rooms.parquet", compression="zstd")
    dd = cal
    for k, v in elig.items():
        dd = dd.join(pl.DataFrame({"pt_date": list(v), f"n_{k}": list(v.values())}, schema={"pt_date": pl.String, f"n_{k}": pl.Int32}),
                     on="pt_date", how="left")
    dd.write_parquet(out / "days.parquet", compression="zstd")
    prov = {"built_by": built_by, "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["shared/calendar", "shared/roster", "shared/period_units", "shared/activity_bins_fixed",
                                   "shared/statement_flags", "shared/embeddings/statements",
                                   "shared/embeddings/statements_white32_{bge_small,gte_modernbert}",
                                   "shared/embeddings/statements_style_resid_period32_{bge_small,gte_modernbert}"]}],
            "params": {"d": DM.D, "window_s": 1800, "min_windows": "max(2, ceil(W/4))", "min_W": 4,
                       "min_agents": DM.MIN_AGENTS, "min_talk_minutes": DM.MIN_TALK, "min_kept_minutes": DM.MIN_KEPT,
                       "trim": "all-present window of the activity population (DQ8)", "claude_code": "excluded",
                       "holdout": "dropped (holdout_mask + calendar.holdout assertion)", "text_stored": False},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (out / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print(f"done in {time.time() - t0:.0f}s -> {out}")


if __name__ == "__main__":
    build(OUT, f"hypotheses/{HYP}/scheme/build.py")
