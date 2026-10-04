"""H24 scheme step 3: goal directions for the kickoff-matched placebo weeks (null N2).

Every non-holdout regime-I goal period except #21: its first active day's window open and its g-hat
(goal text + kickoff, the same rule as build.py), whitened in the regime-I basis. Holdout periods are
never touched (asserted). No text is stored.

Output: data/processed/H24-forecast-coupling-switch/placebo/placebo_weeks.parquet (+ placebo_ghat.npy)
Usage: uv run --offline --with sentence-transformers python hypotheses/H24-forecast-coupling-switch/scheme/build_placebo.py
"""
from __future__ import annotations

import datetime as dt
import re
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h24lib import H24, unit  # noqa: E402
from build import embed  # noqa: E402
from common import OUT, load_goals, load_holdout, load_whitener, holdout_mask  # noqa: E402

DEST = H24 / "placebo"


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    held = set(load_holdout()["goal_periods_held_out"])
    cal = pl.read_parquet(OUT / "calendar.parquet").with_columns(pl.col("regime").cast(pl.String))
    goals = {g["goal_no"]: g for g in load_goals()}
    ctext = pl.read_parquet(OUT / "chat_text.parquet", columns=["message_id", "text"])
    chat = pl.read_parquet(OUT / "chat_core.parquet", columns=["message_id", "t", "speaker_kind"]).filter(pl.col("speaker_kind") == "human")
    rows, texts = [], []
    for gno in sorted(cal.filter(pl.col("regime") == "I")["goal_no"].unique().to_list()):
        if gno in held or gno == 21 or gno == 0:
            continue
        days = cal.filter(pl.col("goal_no") == gno).sort("pt_date")
        if days.height == 0:
            continue
        d0 = days.row(0, named=True)
        assert not holdout_mask([d0["pt_date"]], [gno])[0]
        win0 = d0["win_start"]
        hum = chat.filter(pl.col("t") >= win0 - dt.timedelta(minutes=10), pl.col("t") <= win0 + dt.timedelta(minutes=45)).join(ctext, on="message_id")
        kick = [s for s in hum["text"].to_list() if len(s) >= 250]
        sents = [s for k in kick for s in re.split(r"(?<=[.!?])\s+", k)
                 if not re.search(r"(?i)(previous goal|last (two )?weeks?'? goal|to a close|archived|reflect on how it went)", s)]
        rows.append({"goal_no": gno, "pt_date": d0["pt_date"], "win_start": win0, "win_end": d0["win_end"],
                     "has_kickoff": bool(sents), "n_days": days.height})
        texts.append((goals[gno]["goal"], " ".join(sents) if sents else None))
    W = load_whitener("I", 64)
    flat = [t for pair in texts for t in pair if t]
    E = embed(flat)
    Wf = W(E)
    G, j = [], 0
    for goal, kick in texts:
        gv = unit(Wf[j]); j += 1
        if kick:
            kv = unit(Wf[j]); j += 1
            G.append(unit(gv + kv))
        else:
            G.append(gv)
    pl.DataFrame(rows).write_parquet(DEST / "placebo_weeks.parquet")
    np.save(DEST / "placebo_ghat.npy", np.array(G, dtype=np.float32))
    print(pl.DataFrame(rows))


if __name__ == "__main__":
    main()
