"""H34 scheme, step 2: adoption cascades per goal period (non-holdout days only).

  uv run python hypotheses/H34-idea-cascades/scheme/build.py               # all analyzed periods
  uv run python hypotheses/H34-idea-cascades/scheme/build.py --period 42   # one period

Needs markers/ from build_markers.py. Writes data/processed/H34-idea-cascades/G<NN>/:
  first_uses.parquet, trees.parquet, atrisk.parquet, jitter.parquet, roomx.parquet, meta.json
Analyzed periods: non-holdout goal periods with >= 10,000 earlier non-holdout chat messages (#5 onward), see README.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "1")
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "infra/shared"))
import h34core as C  # noqa: E402
from common import REVISION, git_commit  # noqa: E402

N_WORKERS = 2
MIN_PRIOR_MSGS = 10_000
ATRISK_CAP = 4000
_SH = None


def analyzed_periods(sh: C.Shared) -> list[int]:
    """Non-holdout goal periods with >= MIN_PRIOR_MSGS earlier non-holdout chat messages (the novelty baseline)."""
    from build_markers import non_holdout_chat
    nonh = non_holdout_chat()
    out = []
    for g in sorted(nonh["goal_no"].unique().to_list()):
        if g < 1 or not sh.period_days(g):
            continue
        first_row = nonh.filter(pl.col("goal_no") == g)["msg"].min()
        if nonh.filter(pl.col("msg") < first_row).height >= MIN_PRIOR_MSGS:
            out.append(int(g))
    return out


def room_size(inp: dict) -> int:
    am = inp["kind"] == 0
    E = inp["E"][am]
    snd = inp["sender"][am].astype(np.int64)
    inc = E[np.arange(len(snd)), snd]
    n = E.sum(1) + (~inc).astype(int)
    return int(np.median(n))


def _init():
    global _SH
    _SH = C.Shared()


def build_one(g: int, days: list[str] | None = None, out_dir: Path | None = None, tag: str = "") -> dict:
    t0 = time.time()
    sh = _SH or C.Shared()
    inp = C.period_inputs(sh, g, days=days)
    if inp is None:
        return {"goal": g, "skipped": True}
    res = C.assemble(inp, atrisk_cap=ATRISK_CAP, seed=g)
    od = out_dir or (C.OUT / f"G{g:02d}")
    od.mkdir(parents=True, exist_ok=True)
    for k in ("first_uses", "trees", "atrisk", "jitter", "roomx"):
        res[k].write_parquet(od / f"{k}.parquet", compression="zstd")
    meta = dict(res["meta"])
    meta.update(goal=g, days=inp["days"], N_room=room_size(inp), N_roster_active=meta["n_agents"],
                sender_in_exposure=float(np.mean(inp["E"][inp["kind"] == 0][np.arange(int((inp["kind"] == 0).sum())),
                                                                       inp["sender"][inp["kind"] == 0].astype(np.int64)])),
                n_uses=int(len(inp["use_pos"])), secs=round(time.time() - t0, 1), tag=tag)
    (od / "meta.json").write_text(json.dumps(meta, indent=1))
    print(f"G{g:02d}{tag}: {meta['n_days']} days, {meta['n_agent_msgs']} agent msgs, {meta['n_ideas']} ideas, "
          f"{res['first_uses'].height} first uses, {res['trees'].height} trees, N_room {meta['N_room']}, "
          f"{meta['secs']}s", flush=True)
    return meta


def write_provenance(periods, params):
    p = C.OUT / "_provenance.json"
    prov = json.loads(p.read_text()) if p.exists() else {}
    prov["cascades"] = {"built_by": "hypotheses/H34-idea-cascades/scheme/build.py", "git_commit": git_commit(),
                        "inputs": [{"source": "ai-village", "revision": REVISION,
                                    "tables": ["H34 markers/", "shared/chat_core", "shared/exposure", "shared/events_core",
                                               "shared/actions (via H18 turn_times)", "shared/roster", "shared/calendar"]}],
                        "params": params, "periods": periods, "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    p.write_text(json.dumps(prov, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", type=int, action="append")
    a = ap.parse_args()
    sh = C.Shared()
    periods = a.period or analyzed_periods(sh)
    del sh
    print("periods:", periods, flush=True)
    order = sorted(periods, key=lambda g: -1 if g == 51 else g)   # the big one first
    with Pool(N_WORKERS, initializer=_init) as pool:
        metas = pool.map(build_one, order, chunksize=1)
    write_provenance(sorted(periods), {"min_prior_msgs": MIN_PRIOR_MSGS, "atrisk_cap_per_class": ATRISK_CAP,
                                       "H_turns": C.H_TURNS, "mem_turns": C.MEM_TURNS, "jitter_deltas_s": C.DELTAS_S,
                                       "stale_s": C.STALE_US / 1e6, "guard_s": C.GUARD_US / 1e6})
    pl.DataFrame([{k: v for k, v in m.items() if k != "days"} for m in metas]).write_parquet(C.OUT / "periods_meta.parquet")


if __name__ == "__main__":
    main()
