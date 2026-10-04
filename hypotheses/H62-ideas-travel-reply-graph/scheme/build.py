"""H62 scheme: channel-resolved contagion tables per goal period (no text).

  uv run python hypotheses/H62-ideas-travel-reply-graph/scheme/build.py [--goals 38,51]

Inputs: infra/shared/idea_ledger.py (chat timeline, DQ1 ledger reads, H34 markers, DQ2 parents); held-out days never
enter. Output per period in data/processed/H62-ideas-travel-reply-graph/G<NN>/:
  cells.parquet     idea x indicator pattern: talk calls at risk, adoptions (Models A, B and the guard)
  events.parquet    (idea, agent) first exposed call: channel (1 reply, 2 room-only), guard channel, adoption in 3 calls
  adopters.parquet  every agent first use: status (0 seed, 1 unexposed, 2 exposed) and the latest read use's channel
  meta.json
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from multiprocessing import Pool  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
sys.path.insert(0, str(HERE))
import idea_ledger as IL  # noqa: E402
import h62core as C  # noqa: E402
from common import REVISION, git_commit  # noqa: E402

OUT = ROOT / "data/processed/H62-ideas-travel-reply-graph"
GOALS = [5, 6, 7, 8, 10, 11, 12, 13, 16, 17, 18, 19, 20, 21, 23, 24, 25, 26, 27, 30, 31, 33, 35, 36, 37, 38, 39, 40,
         41, 42, 44, 51]
_BASE = None


def room_size(P: dict) -> float:
    """Median over (room, day) of agents posting there (H34's N_room analogue)."""
    k = (P["kind"] == 0) & (P["sender"] >= 0)
    df = pl.DataFrame({"room": P["room"][k], "day": P["day"][k], "a": P["sender"][k]})
    return float(df.group_by("room", "day").agg(pl.col("a").n_unique()).filter(pl.col("a") >= 2)["a"].median() or 0)


def one(g: int):
    global _BASE
    if _BASE is None:
        _BASE = IL.Base()
    t0 = time.time()
    P = IL.load_period(_BASE, g)
    if P is None:
        return g, None
    r = C.assemble(P)
    d = OUT / f"G{g:02d}"
    d.mkdir(parents=True, exist_ok=True)
    for k in ("cells", "events", "adopters"):
        r[k].write_parquet(d / f"{k}.parquet", compression="zstd")
    regime = _BASE.cal.filter(pl.col("pt_date").is_in(P["days"]))["regime"].mode()[0]
    meta = dict(r["meta"], goal=g, n_days=len(P["days"]), N_room=room_size(P), regime=regime,
                n_rooms=int(len(np.unique(P["room"][P["kind"] == 0]))), secs=round(time.time() - t0, 1),
                first_day=P["days"][0], last_day=P["days"][-1])
    (d / "meta.json").write_text(json.dumps(meta, indent=1))
    return g, meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--goals", default="")
    ap.add_argument("--procs", type=int, default=4)
    a = ap.parse_args()
    goals = [int(x) for x in a.goals.split(",")] if a.goals else GOALS
    goals = sorted(goals, key=lambda g: -1 if g == 51 else g)
    with Pool(a.procs) as pool:
        for g, m in pool.imap_unordered(one, goals):
            print(f"G{g:02d}: {m}" if m else f"G{g:02d}: none", flush=True)
    prov = {"built_by": "hypotheses/H62-ideas-travel-reply-graph/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["shared/chat_core", "shared/calendar", "shared/roster", "shared/call_windows",
                                   "shared/context_ledger_items", "shared/reply_pairs (cand, parent)",
                                   "H34-idea-cascades/markers (data, hashes)"]}],
            "params": {"tie_window_h": 2, "lag5_s": 300, "mem_turns": C.MEM_TURNS, "h_turns": C.H_TURNS,
                       "t_calls": C.T_CALLS, "cap_ideas_per_class": 4000, "holdout": "excluded (holdout_mask)",
                       "loader": "infra/shared/idea_ledger.py"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))


if __name__ == "__main__":
    main()
