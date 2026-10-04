"""Shared per-call outcomes for regime-III computer-use calls: action rows, real failures, write evidence, agent work
commits, and context-segment positions.

Merges two copies of one builder:
  H44  hypotheses/H44-erasure-reacquisition-thrash/scheme/build.py: build_calls (load_calls_raw, action_rows)
  H15  hypotheses/H15-semantic-information-scrambles/scheme/build.py: r1b_calls
Both map `actions` rows to DQ1 ledger calls the same way and differ only in the failure rule, which is kept twice:
  n_fail  H44: action rows of the call with turn_outcomes.failed (DQ3 real failures; rows without an outcome count 0)
  fail    H15: any action row that failed, where a row without a turn_outcomes match falls back to a platform error
          class (actions_bash_head_fixed.error_class in timeout / vm / resource / network / tool_use)
H44's command categories, command hashes and loop flags stay in H44 (they classify command text).

Rules (unchanged):
  calls      context_ledger_turns rows with regime == III and ctx_mode == cu (summary calls excluded)
  rows       actions rows from 2026-03-24 07:00 UTC, joined to turn_outcomes on (agent, t) (first match) and to
             actions_bash_head_fixed on row; a row belongs to the agent's latest call with t_first <= t, if
             t <= that call's t_log + 1 s
  write ev.  commit_ok | push_ok | file_write | api_write | deploy (turn_outcomes)
  n_work     DQ4 agent work commits (canonical & ~imported & author_kind == agent & ~automated, author known, from
             2026-03-24) mapped forward to the author's first call with t_log >= commit time, within 10 min
  segments   per agent-day in (t_first, turn_id) order: seq (0-based); a reset (is_reset) opens a segment at a
             voluntary or forced consolidation, a session reset, the first call of the day or seq 0; seg = cumulative
             reset count (1-based); pos = position in the segment (1-based; H15's 0-based pos = pos - 1); seg_len;
             seg_kind = forced / voluntary / session / day_start

Output (data/processed/shared/calls.parquet, zstd, codes only, ALL regime-III days; `holdout` flags locked-holdout
days, exploratory users filter `~holdout`):
  turn_id, agent, pt_date, goal_no, holdout, t_call, kind, talk, ctx_pos, reset_consol, reset_forced, reset_session,
  first_of_day, prev_seg_len, n_rows, n_fail, fail, any_write, commit_ok, push_ok, n_work, seq, is_reset, seg,
  seg_start, pos, seg_len, seg_kind. Join context_ledger_turns on turn_id for t_first, t_log and item counts.
  t_call is not a unique key within an agent: about 800 pairs of consecutive calls share one logged start.

Usage: uv run python infra/shared/calls.py            (build)
       uv run python infra/shared/calls.py --verify   (compare with H44's calls.parquet and H15's r1b/calls.parquet on
                                                       their non-holdout rows; read-only)
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
           "RAYON_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUT, ROOT, write_provenance  # noqa: E402

SH = OUT
BS = ROOT / "data/processed/behavior_states"
REGIME3_START = "2026-03-24"
T0_ACTIONS = dt.datetime(2026, 3, 24, 7, tzinfo=dt.timezone.utc)
PLATFORM_ERR = ["timeout", "vm", "resource", "network", "tool_use"]   # H15: error classes that are real failures
WRITE_FLAGS = ("commit_ok", "push_ok", "file_write", "api_write", "deploy")
TOL_LOG_S = 1
WORK_TOL = "10m"


def ledger_calls() -> pl.DataFrame:
    return (pl.scan_parquet(SH / "context_ledger_turns.parquet")
            .filter((pl.col("regime") == "III") & (pl.col("ctx_mode") == "cu"))
            .select("turn_id", "agent", "pt_date", "goal_no", "holdout", "t_call", "t_first", "t_log", "kind", "talk",
                    "ctx_pos", "reset_consol", "reset_forced", "reset_session", "first_of_day", "prev_seg_len")
            .collect())


def action_rows() -> pl.DataFrame:
    """Regime-III action rows with real-failure and write-evidence flags (no command text)."""
    a = (pl.scan_parquet(SH / "actions.parquet").select("t", "agent", "action").with_row_index("row")
         .filter(pl.col("t") >= T0_ACTIONS).collect())
    ec = pl.read_parquet(SH / "actions_bash_head_fixed.parquet", columns=["row", "error_class"])
    to = (pl.read_parquet(BS / "turn_outcomes.parquet", columns=["t", "agent", "failed", *WRITE_FLAGS])
          .filter(pl.col("t") >= T0_ACTIONS).unique(["agent", "t"], keep="first"))
    a = a.join(ec, on="row", how="left").join(to, on=["agent", "t"], how="left")
    wev = pl.lit(False)
    for f in WRITE_FLAGS:
        wev = wev | pl.col(f).fill_null(False)
    return a.select("t", "agent",
                    pl.col("failed").fill_null(False).alias("failed_h44"),
                    pl.when(pl.col("failed").is_not_null()).then(pl.col("failed"))
                    .otherwise(pl.col("error_class").cast(pl.Utf8).is_in(PLATFORM_ERR)).alias("failed_h15"),
                    wev.alias("wev"), pl.col("commit_ok").fill_null(False), pl.col("push_ok").fill_null(False))


def work_commits() -> pl.DataFrame:
    return (pl.scan_parquet(SH / "work_commits.parquet")
            .filter(pl.col("canonical") & ~pl.col("imported") & (pl.col("author_kind") == "agent") & ~pl.col("automated")
                    & pl.col("author_agent").is_not_null() & (pl.col("pt_date") >= REGIME3_START))
            .select("t", pl.col("author_agent").alias("agent"), "holdout").collect().sort("t"))


def build() -> pl.DataFrame:
    t0 = time.time()
    calls = ledger_calls()
    a = action_rows()
    keys = calls.select("turn_id", "agent", "t_first", "t_log").sort("t_first")
    m = (a.sort("t").join_asof(keys, left_on="t", right_on="t_first", by="agent", strategy="backward")
         .filter(pl.col("turn_id").is_not_null() & (pl.col("t") <= pl.col("t_log") + pl.duration(seconds=TOL_LOG_S))))
    print(f"calls {calls.height}; action rows {a.height}, mapped {m.height} ({time.time() - t0:.0f}s)", flush=True)
    agg = m.group_by("turn_id").agg(pl.len().cast(pl.Int16).alias("n_rows"),
                                    pl.col("failed_h44").sum().cast(pl.Int16).alias("n_fail"),
                                    pl.col("failed_h15").any().cast(pl.Int8).alias("fail"),
                                    pl.col("wev").any().alias("any_write"), pl.col("commit_ok").any(),
                                    pl.col("push_ok").any())
    calls = calls.join(agg, on="turn_id", how="left").with_columns(
        pl.col("n_rows").fill_null(0), pl.col("n_fail").fill_null(0), pl.col("fail").fill_null(0),
        pl.col("any_write").fill_null(False), pl.col("commit_ok").fill_null(False), pl.col("push_ok").fill_null(False))
    wc = work_commits()
    wm = wc.join_asof(calls.select("turn_id", "agent", "t_log").sort("t_log"), left_on="t", right_on="t_log", by="agent",
                      strategy="forward", tolerance=WORK_TOL)
    wcnt = wm.drop_nulls("turn_id").group_by("turn_id").agg(pl.len().cast(pl.Int16).alias("n_work"))
    calls = calls.join(wcnt, on="turn_id", how="left").with_columns(pl.col("n_work").fill_null(0))
    print(f"work commits {wc.height}, mapped {int(wm['turn_id'].is_not_null().sum())}", flush=True)
    calls = calls.sort("agent", "pt_date", "t_first", "turn_id").with_columns(
        pl.int_range(pl.len()).over("agent", "pt_date").cast(pl.Int32).alias("seq"))
    calls = calls.with_columns((pl.col("reset_consol") | pl.col("reset_session") | pl.col("first_of_day")
                                | (pl.col("seq") == 0)).alias("is_reset"))
    calls = calls.with_columns(pl.col("is_reset").cast(pl.Int32).cum_sum().over("agent", "pt_date").cast(pl.Int16).alias("seg"))
    sk = (pl.when(pl.col("reset_forced")).then(pl.lit("forced")).when(pl.col("reset_consol")).then(pl.lit("voluntary"))
          .when(pl.col("reset_session")).then(pl.lit("session")).otherwise(pl.lit("day_start")))
    seginfo = calls.filter(pl.col("is_reset")).select("agent", "pt_date", "seg", sk.alias("seg_kind"),
                                                      pl.col("seq").alias("seg_start"))
    calls = calls.join(seginfo, on=["agent", "pt_date", "seg"], how="left").with_columns(
        (pl.col("seq") - pl.col("seg_start") + 1).cast(pl.Int16).alias("pos"),
        pl.len().over("agent", "pt_date", "seg").cast(pl.Int16).alias("seg_len"))
    return calls.select("turn_id", "agent", "pt_date", "goal_no", "holdout", "t_call", "kind", "talk",
                        "ctx_pos", "reset_consol", "reset_forced", "reset_session", "first_of_day", "prev_seg_len",
                        "n_rows", "n_fail", "fail", "any_write", "commit_ok", "push_ok", "n_work", "seq", "is_reset", "seg",
                        "seg_start", "pos", "seg_len", pl.col("seg_kind").cast(pl.Categorical)).sort("agent", "pt_date", "seq")


def main():
    t0 = time.time()
    c = build()
    p = SH / "calls.parquet"
    c.write_parquet(p, compression="zstd", compression_level=9)
    nh = c.filter(~pl.col("holdout"))
    summ = {"rows": c.height, "rows_nonholdout": nh.height, "fail_share": float(nh["fail"].mean()),
            "n_fail_share": float((nh["n_fail"] > 0).mean()), "any_write_share": float(nh["any_write"].mean()),
            "work_commits_mapped_nonholdout": int(nh["n_work"].sum())}
    write_provenance("calls", ["context_ledger_turns", "actions", "actions_bash_head_fixed",
                               "behavior_states/turn_outcomes (flags only)", "work_commits"],
                     {"calls": "context_ledger_turns regime III, ctx_mode cu", "rows_from": str(T0_ACTIONS),
                      "row_to_call": "latest call with t_first <= t, t <= t_log + 1 s",
                      "n_fail": "sum of turn_outcomes.failed (H44)", "fail": "any failed, else error_class in "
                      f"{PLATFORM_ERR} when no outcome (H15)", "write_evidence": list(WRITE_FLAGS),
                      "n_work": "agent work commits -> first call with t_log >= t within 10 min",
                      "holdout": "all days, flagged", "sources": "H44 scheme/build.py build_calls; H15 scheme/build.py "
                      "r1b_calls (rules unchanged)", "summary": summ})
    print(f"calls.parquet: {c.height} rows, {p.stat().st_size / 1e6:.1f} MB, {time.time() - t0:.0f}s", flush=True)
    print(json.dumps(summ), flush=True)


def verify() -> dict:
    c = pl.read_parquet(SH / "calls.parquet")
    res = {}
    # H44
    h = pl.read_parquet(ROOT / "data/processed/H44-erasure-reacquisition-thrash/calls.parquet")
    cols = ["any_write", "commit_ok", "push_ok", "n_fail", "n_work", "n_rows", "seq", "is_reset", "seg", "seg_start", "pos",
            "seg_len", "seg_kind"]
    j = h.select("turn_id", *cols).join(c.select("turn_id", "holdout", *cols), on="turn_id", how="left", suffix="_s")
    r = {"h44_rows": h.height, "missing_in_shared": int(j["holdout"].is_null().sum()),
         "holdout_rows": int(j["holdout"].fill_null(False).sum()),
         "shared_nonholdout_rows_not_in_h44": c.filter(~pl.col("holdout")).join(h.select("turn_id"), on="turn_id",
                                                                               how="anti").height}
    for k in cols:
        a, b = j[k], j[f"{k}_s"]
        if k == "seg_kind":
            a, b = a.cast(pl.Utf8), b.cast(pl.Utf8)
        r[f"{k}_diff"] = int((~a.cast(b.dtype).eq_missing(b)).sum())
    res["H44"] = r
    # H15 (no turn_id: key agent, pt_date, t_call; pos 0-based). Some consecutive calls share one logged t_call
    # (Known issue "duplicate logged call starts"), so those keys are ambiguous: compare on unique keys, count the rest.
    h = pl.read_parquet(ROOT / "data/processed/H15-semantic-information-scrambles/r1b/calls.parquet")
    k = ["agent", "pt_date", "t_call"]
    dupk = c.group_by(k).len().filter(pl.col("len") > 1).select(k)
    cu = c.join(dupk, on=k, how="anti")
    j = h.join(cu.select(*k, "holdout", "seq", "seg", (pl.col("pos") - 1).alias("pos0"), "seg_len", "is_reset", "n_work", "fail",
                         pl.col("any_write").cast(pl.Int8).alias("wev_s")), on=k, how="inner")
    r = {"h15_rows": h.height, "ambiguous_h15_rows_on_duplicate_keys": h.join(dupk, on=k, how="semi").height,
         "compared_rows": j.height, "missing_in_shared": h.join(c.select(k), on=k, how="anti").height,
         "holdout_rows": int(j["holdout"].sum())}
    for a, b in (("w", "n_work"), ("fail", "fail_right" if "fail_right" in j.columns else None), ("wev", "wev_s"),
                 ("seq", "seq_right"), ("seg", "seg_right"), ("pos", "pos0"), ("seg_len", "seg_len_right"),
                 ("is_reset", "is_reset_right")):
        if b is None or b not in j.columns:
            continue
        r[f"{a}_diff"] = int((~j[a].cast(pl.Int64).eq_missing(j[b].cast(pl.Int64))).sum())
    res["H15"] = r
    print(json.dumps(res, indent=1), flush=True)
    return res


if __name__ == "__main__":
    if "--verify" in sys.argv:
        verify()
    else:
        main()
