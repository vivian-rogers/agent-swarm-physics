"""H59 scheme: call-level transition table with kick exposures aligned on the receiving call.

Builds data/processed/H59-one-lever-model/ from shared tables and H43's per-call table (read only):
  transitions.parquet  one row per consecutive pair of model calls (same agent, same PT day) in the chosen goal periods:
                       from-state s_prev, to-state s (I idle / W work / T talk), previous-previous state, run length of
                       s_prev, time-of-day bin, nuisance context counts at the current call, and for every kick class a
                       lag bitmask (bit b set if a receiving call of that class sits at lag bin b before this call).
  readout.parquet      one row per (kick item, recipient) at its receiving call: class, age at read (read-out delay).
  _provenance.json

States per call (H43 `calls.parquet`, summary calls already dropped):
  T talk  = the call posts chat (talk flag);
  I idle  = kind in {pause, wait} and not talking;
  W work  = every other call (computer-use action, search, room move, request, session start).
Kick classes, at the receiving call (DQ1 `context_ledger_items`, omitted items dropped):
  N  nudge whose leading @ is the recipient (H35 rule; H30's `h30lib.leading_targets`, imported read-only)
  Hu human message not naming the recipient;  Hm human message naming the recipient;  A agent message naming it.
Lag bins (calls after the receiving call; the receiving call itself is lag 0):
  bit 0 = lag -1 (the call just before the receiving call: a pre-read placebo / sender-selection term)
  bit 1 = 0, bit 2 = 1, bit 3 = 2, bit 4 = 3-5, bit 5 = 6-10, bit 6 = 11-30.
Holdout: H43's table excludes held-out rows; holdout_mask is re-checked here.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import importlib.util  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit, holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H59-one-lever-model"
H43_CALLS = ROOT / "data/processed/H43-kick-refractory-window/calls.parquet"
KINDS = ["cu_action", "talk", "pause", "wait", "consolidate", "session_start", "session_stop", "search", "room_move",
         "request"]
IDLE_KINDS = {KINDS.index("pause"), KINDS.index("wait")}
CLASSES = ["N", "Hu", "Hm", "A"]
LAG_EDGES = [(-1, -1), (0, 0), (1, 1), (2, 2), (3, 5), (6, 10), (11, 30)]   # bit b <-> LAG_EDGES[b]
MAXLAG = 30
PERIODS_DEFAULT = [4, 5, 38, 51]


def _h30lib():
    spec = importlib.util.spec_from_file_location("h30lib_ro", ROOT / "hypotheses/H30-operator-susceptibility/analysis/h30lib.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["h30lib_ro"] = mod
    spec.loader.exec_module(mod)
    return mod


def load_calls(goals: list[int]) -> pl.DataFrame:
    c = pl.read_parquet(H43_CALLS).filter(pl.col("goal_no").is_in(goals))
    hm = holdout_mask(c["pt_date"].to_list(), c["goal_no"].to_list())
    assert not any(hm), "holdout rows in H43 calls"
    return c.sort("agent", "pt_date", "t_call", "turn_id")


def kick_items(calls: pl.DataFrame) -> pl.DataFrame:
    """(turn_id, class, age_s, message_id) for every kick item read at a call of these periods."""
    it = (pl.scan_parquet(SH / "context_ledger_items.parquet")
          .filter(~pl.col("omitted"))
          .select("turn_id", "message_id", pl.col("kind").cast(pl.Utf8), "age_s", "ment")
          .join(calls.lazy().select("turn_id", "agent", "goal_no", "pt_date"), on="turn_id", how="inner")
          .collect())
    nud = it.filter(pl.col("kind") == "nudge")
    lt = _h30lib().leading_targets(nud["message_id"].unique().to_list())
    lt_df = pl.DataFrame({"message_id": list(lt.keys()), "lead": [v if v is not None else -1 for v in lt.values()]},
                         schema={"message_id": pl.Utf8, "lead": pl.Int32})
    it = it.join(lt_df, on="message_id", how="left")
    cls = (pl.when((pl.col("kind") == "nudge") & (pl.col("lead") == pl.col("agent").cast(pl.Int32))).then(pl.lit("N"))
           .when((pl.col("kind") == "human") & ~pl.col("ment")).then(pl.lit("Hu"))
           .when((pl.col("kind") == "human") & pl.col("ment")).then(pl.lit("Hm"))
           .when((pl.col("kind") == "agent") & pl.col("ment")).then(pl.lit("A"))
           .when(pl.col("kind") == "agent").then(pl.lit("chat"))
           .when(pl.col("kind") == "pause_resume").then(pl.lit("bookend"))
           .otherwise(pl.lit("other")))
    return it.with_columns(cls.alias("cls")).select("turn_id", "agent", "goal_no", "pt_date", "message_id", "cls", "age_s")


def build(goals: list[int], calls: pl.DataFrame | None = None) -> tuple[pl.DataFrame, pl.DataFrame]:
    """calls=None loads H43's non-holdout table; analysis/confirm.py passes its own (held-out) calls frame."""
    calls = load_calls(goals) if calls is None else calls.sort("agent", "pt_date", "t_call", "turn_id")
    items = kick_items(calls)
    per = (items.group_by("turn_id").agg([(pl.col("cls") == c).sum().cast(pl.Int16).alias(f"n_{c}") for c in
                                          CLASSES + ["chat", "bookend"]]
                                         + [pl.col("age_s").filter(pl.col("cls") == c).min().alias(f"age_{c}")
                                            for c in CLASSES]))
    calls = calls.join(per, on="turn_id", how="left").with_columns(
        [pl.col(f"n_{c}").fill_null(0) for c in CLASSES + ["chat", "bookend"]])
    s = np.where(calls["talk"].to_numpy(), 2, np.where(np.isin(calls["kind_c"].to_numpy(), list(IDLE_KINDS)), 0, 1))
    calls = calls.with_columns(pl.Series("s", s.astype(np.int8)))
    # sequence index within agent-day
    key = (calls["agent"].cast(pl.Int32) * 100000 + calls["pt_date"].rank("dense").cast(pl.Int32)).to_numpy()
    n = calls.height
    newseq = np.r_[True, key[1:] != key[:-1]]
    seq_start = np.maximum.accumulate(np.where(newseq, np.arange(n), 0))
    pos = np.arange(n) - seq_start
    # lag bitmasks per class: for call j, bit b set if call j-k is a receiving call of the class for k in bin b,
    # bit 0 (lag -1) if call j+1 is a receiving call.
    masks = {}
    for c in CLASSES:
        rec = calls[f"n_{c}"].to_numpy() > 0
        m = np.zeros(n, np.uint8)
        for b, (lo, hi) in enumerate(LAG_EDGES):
            for k in range(lo, hi + 1):
                if k == -1:
                    nb = np.zeros(n, bool)
                    ok = np.r_[~newseq[1:], False]          # j+1 exists in the same agent-day
                    nb[:-1] = rec[1:]
                    hit = nb & ok
                else:
                    hit = np.zeros(n, bool)
                    if k == 0:
                        hit = rec.copy()
                    else:
                        hit[k:] = rec[:-k]
                        hit &= pos >= k
                m |= (hit.astype(np.uint8) << b)
        masks[f"m_{c}"] = m
    # previous states, run length of s_prev
    sp = np.r_[-1, s[:-1]].astype(np.int8)
    sp[newseq] = -1
    sp2 = np.r_[-1, -1, s[:-2]].astype(np.int8)
    sp2[pos < 2] = -1
    run = np.zeros(n, np.int32)   # run length of s at call j (in calls, ending at j)
    for j in range(n):
        run[j] = 1 if (newseq[j] or s[j] != s[j - 1]) else run[j - 1] + 1
    runprev = np.r_[0, run[:-1]]
    runprev[newseq] = 0
    t = calls["t_call"].to_numpy()
    t0 = t[seq_start]
    tod = np.digitize((t - t0) / 3600.0, [1, 3, 6]).astype(np.int8)
    dtprev = np.r_[np.nan, t[1:] - calls["t_end"].to_numpy()[:-1]]
    dtprev[newseq] = np.nan
    tr = calls.select("turn_id", "agent", "pt_date", "goal_no", "unit_id", "regime", "t_call", "low_conf",
                      "n_N", "n_Hu", "n_Hm", "n_A", "n_chat", "n_bookend", "age_N", "age_Hu", "age_Hm", "age_A").with_columns(
        pl.Series("s", s.astype(np.int8)), pl.Series("s_prev", sp), pl.Series("s_prev2", sp2),
        pl.Series("run_prev", runprev.astype(np.int32)), pl.Series("tod", tod), pl.Series("pos", pos.astype(np.int32)),
        pl.Series("gap_prev_s", dtprev.astype(np.float32)),
        *[pl.Series(k, v) for k, v in masks.items()])
    # a transition needs a previous call in the same agent-day; drop gaps > 60 min (village-off / outage)
    tr = tr.filter((pl.col("s_prev") >= 0) & (pl.col("gap_prev_s").fill_nan(1e9) <= 3600))
    readout = items.filter(pl.col("cls").is_in(CLASSES)).select("goal_no", "pt_date", "agent", "turn_id", "cls", "age_s")
    return tr, readout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--goals", default=",".join(map(str, PERIODS_DEFAULT)))
    a = ap.parse_args()
    goals = [int(x) for x in a.goals.split(",")]
    OUT.mkdir(parents=True, exist_ok=True)
    tr, ro = build(goals)
    tr.write_parquet(OUT / "transitions.parquet", compression="zstd")
    ro.write_parquet(OUT / "readout.parquet", compression="zstd")
    prov = {"built_by": "hypotheses/H59-one-lever-model/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["shared/context_ledger_items", "shared/chat_core", "shared/chat_text (leading @ only, in memory)",
                                   "shared/roster", "H43-kick-refractory-window/calls.parquet (from shared/call_windows)"]}],
            "params": {"goals": goals, "states": {"T": "talk flag", "I": "pause/wait, not talking", "W": "other"},
                       "classes": {"N": "nudge, leading @ = recipient", "Hu": "human, not naming", "Hm": "human, naming",
                                   "A": "agent, naming"},
                       "lag_bins": LAG_EDGES, "max_gap_s": 3600, "holdout": "excluded (H43 table + holdout_mask)"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print(tr.group_by("goal_no").agg(pl.len(), *[(pl.col(f"n_{c}") > 0).sum().alias(c) for c in CLASSES]).sort("goal_no"))


if __name__ == "__main__":
    main()
