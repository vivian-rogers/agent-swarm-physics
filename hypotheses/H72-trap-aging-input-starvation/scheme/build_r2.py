"""H72 round 2 scheme: wake rows with chatter dose, context composition, trap kind at start and reset flags.

Round 1 outputs are not touched (scheme/build.py). Output (codes and numbers only, no text):
  data/processed/H72-trap-aging-input-starvation/r2/wakes_r2.parquet
    the round-1 eligible wakes (gates.parquet: idle-gate rows of the 18 periods with >= 200 wakes) plus
    dose     U<N> = undirected novel items read at the N calls before the wake (N = 3, 5, 10; the wake's own reads are
             excluded; same agent-day); D<N> the same for directed items; Upeer5 = undirected agent + human items;
             win<N>_s = t_call(wake) - t_call(first call of the window) [s]; nwin<N> = calls in the window (< N early in
             the day).
    composition (regime III only; copied from H16 analysis/r2lib.py: composition, U-call / U-entry / U-rec rulers; the
             token ruler U-tok is not rebuilt because it needs H45 data): n_rep, n_act, kc, f_call, f_entry, f_rec,
             seg, ctx_pos, reset_at_wake, forced, vol (H16 rule: segment changes between the idle call and the wake).
    trap kind at start: trap_id (agent-day run of wakes with k_sus counting from 1), consol_start (a summary call starts
             within [-30 s, +60 s] of the end of the last sustained run: the trap begins with a consolidation's
             latency; H16 round-2 rule transferred to the call clock), trap_kind (after_fail / after_talk / after_work:
             the last call of the last sustained run failed (shared calls.fail), talked, or neither), gap_kind (from
             call_windows: pause = timer wake, after_summary, busy, pause_early).
    r16 (bool): row inside H16's round-2 G51 window (pt_date < 2026-09-03, NE33 batch join excluded); true elsewhere.
Reserved data: the shared gate table and call loaders exclude common.holdout_mask days; re-asserted here.
Usage: uv run python hypotheses/H72-trap-aging-input-starvation/scheme/build_r2.py
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import datetime as dt
import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

HYP = Path(__file__).resolve().parents[1]
ROOT = HYP.parents[1]
sys.path.insert(0, str(ROOT / "infra/shared"))
sys.path.insert(0, str(HYP / "analysis"))
from common import REVISION, git_commit, holdout_mask  # noqa: E402
import idle_gates as IG  # noqa: E402
import r2lib as R  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H72-trap-aging-input-starvation"
R2 = OUT / "r2"
NS = (3, 5, 10)
G51_END = "2026-09-03"


def log(t0, *a):
    print(f"[{time.time() - t0:6.1f}s]", *a, flush=True)


def dose_table(goals) -> pl.DataFrame:
    """Per non-summary call of the eligible periods: rolling undirected / directed reads over the previous N calls."""
    cw = IG.load_calls(goal_nos=goals)
    ic = IG.item_counts(cw)
    cw = cw.join(ic, on="turn_id", how="left").with_columns(
        [pl.col(c).fill_null(0) for c in ("n_novel", "n_dir", "n_peer", "n_ment_agent", "n_human_named")])
    cw = cw.with_columns(
        n_undir=(pl.col("n_novel").cast(pl.Int32) - pl.col("n_dir").cast(pl.Int32)).clip(0, None),
        n_undir_peer=(pl.col("n_peer").cast(pl.Int32) - pl.col("n_ment_agent").cast(pl.Int32)
                      - pl.col("n_human_named").cast(pl.Int32)).clip(0, None),
        n_dirc=pl.col("n_dir").cast(pl.Int32))
    cw = cw.sort("agent", "pt_date", "t_call", "turn_id")
    ad = ["agent", "pt_date"]
    cw = cw.with_columns(pos=pl.int_range(pl.len()).over(ad))
    ex = []
    for N in NS:
        ex += [pl.col("n_undir").shift(1).rolling_sum(N, min_samples=1).over(ad).fill_null(0).alias(f"U{N}"),
               pl.col("n_dirc").shift(1).rolling_sum(N, min_samples=1).over(ad).fill_null(0).alias(f"D{N}"),
               pl.min_horizontal(pl.col("pos"), pl.lit(N)).alias(f"nwin{N}"),
               ((pl.col("t_call") - pl.col("t_call").shift(N).over(ad)).dt.total_microseconds() / 1e6).alias(f"win{N}_s")]
    ex.append(pl.col("n_undir_peer").shift(1).rolling_sum(5, min_samples=1).over(ad).fill_null(0).alias("Upeer5"))
    cw = cw.with_columns(ex)
    # windows shorter than N (early in the day): measure from the first call of the day
    tfirst = pl.col("t_call").first().over(ad)
    cw = cw.with_columns([pl.when(pl.col(f"win{N}_s").is_null() & (pl.col("pos") > 0))
                          .then((pl.col("t_call") - tfirst).dt.total_microseconds() / 1e6)
                          .otherwise(pl.col(f"win{N}_s")).alias(f"win{N}_s") for N in NS])
    # last call of the last sustained run (idle_gates rule): its turn_id, talk and failure
    cw = cw.with_columns(idle=(pl.col("kind").cast(pl.Utf8).is_in(IG.IDLE_KINDS) & ~pl.col("talk")))
    cw = cw.with_columns((pl.col("idle") != pl.col("idle").shift(1).over(ad)).fill_null(True).cast(pl.Int32)
                         .cum_sum().over(ad).alias("run"))
    cw = cw.with_columns(run_len=pl.len().over(ad + ["run"]),
                         run_last=(pl.int_range(pl.len()).over(ad + ["run"]) == pl.len().over(ad + ["run"]) - 1))
    cw = cw.with_columns(end_sus=(~pl.col("idle") & pl.col("run_last") & (pl.col("run_len") >= IG.SUS_LEN)))
    fl = pl.read_parquet(SH / "calls.parquet", columns=["turn_id", "fail"])
    cw = cw.join(fl, on="turn_id", how="left")
    cw = cw.with_columns(
        pl.when(pl.col("end_sus")).then(pl.col("turn_id")).shift(1).forward_fill().over(ad).alias("sus_tid"),
        pl.when(pl.col("end_sus")).then(pl.col("talk")).shift(1).forward_fill().over(ad).alias("sus_talk"),
        pl.when(pl.col("end_sus")).then(pl.col("fail").fill_null(0) > 0).shift(1).forward_fill().over(ad).alias("sus_fail"),
        pl.when(pl.col("end_sus")).then(pl.col("t_end")).shift(1).forward_fill().over(ad).alias("t_sus_end"))
    keep = ["turn_id", *[f"{p}{N}" for N in NS for p in ("U", "D", "nwin")], *[f"win{N}_s" for N in NS], "Upeer5",
            "sus_tid", "sus_talk", "sus_fail", "t_sus_end"]
    return cw.select(keep)


def comp_table() -> pl.DataFrame:
    t = pl.read_parquet(SH / "context_ledger_turns.parquet",
                        columns=["turn_id", "agent", "pt_date", "goal_no", "regime", "holdout", "t_call", "kind", "talk",
                                 "ctx_mode", "k_new", "ctx_pos", "reset_consol", "reset_forced", "reset_session"])
    t = t.filter((pl.col("regime").cast(pl.Utf8) == "III") & ~pl.col("holdout") & (pl.col("ctx_mode").cast(pl.Utf8) == "cu"))
    hm = np.array(holdout_mask(t["pt_date"].to_list(), t["goal_no"].to_list()))
    t = t.filter(pl.Series(~hm))
    ros = pl.read_parquet(SH / "roster.parquet").filter(~pl.col("claude_code")).select("agent")
    t = t.join(ros, on="agent", how="inner")
    c = R.composition(t)
    cc = c.sort("agent", "t_call", "turn_id")
    prev = cc.select("turn_id", pl.col("seg").shift(1).over("agent").alias("seg_prev"))
    c = c.join(prev, on="turn_id", how="left")
    c = c.with_columns(reset_at_wake=(pl.col("seg") != pl.col("seg_prev")).fill_null(False))
    c = c.with_columns(forced=(pl.col("reset_at_wake") & pl.col("reset_forced").fill_null(False)),
                       vol=(pl.col("reset_at_wake") & ~pl.col("reset_forced").fill_null(False)))
    return c.select("turn_id", "seg", "ctx_pos", "n_rep", "n_act", "kc", "f_call", "f_entry", "f_rec", "reset_at_wake",
                    "forced", "vol")


def consol_flags(w: pl.DataFrame) -> pl.DataFrame:
    """consol_start per wake: a summary call starts within [-30 s, +60 s] of the end of the trap's last sustained run."""
    sm = (pl.scan_parquet(SH / "call_windows.parquet").filter(pl.col("ctx_mode") == "summary")
          .select("agent", "pt_date", "goal_no", "t_call").collect())
    sm = sm.filter(pl.Series(~np.array(holdout_mask(sm["pt_date"].to_list(), sm["goal_no"].to_list()))))
    sm = sm.select("agent", pl.col("t_call").alias("t_sum")).sort("t_sum")
    x = w.select("turn_id", "agent", "t_sus_end").filter(pl.col("t_sus_end").is_not_null())
    x = x.with_columns(t_lo=pl.col("t_sus_end") - pl.duration(seconds=30)).sort("t_lo")
    x = x.join_asof(sm, left_on="t_lo", right_on="t_sum", by="agent", strategy="forward")
    x = x.with_columns(consol_start=(pl.col("t_sum").is_not_null()
                                     & (pl.col("t_sum") <= pl.col("t_sus_end") + pl.duration(seconds=60))))
    return x.select("turn_id", "consol_start")


def main():
    t0 = time.time()
    R2.mkdir(parents=True, exist_ok=True)
    g = pl.read_parquet(OUT / "gates.parquet")
    hm = holdout_mask(g["pt_date"].to_list(), g["goal_no"].to_list())
    assert not any(hm), "reserved rows in gates.parquet"
    goals = sorted(g["goal_no"].unique().to_list())
    d = dose_table(goals)
    log(t0, "dose table", d.height)
    w = g.join(d, on="turn_id", how="left")
    c = comp_table()
    log(t0, "composition", c.height)
    w = w.join(c, on="turn_id", how="left")
    gk = pl.read_parquet(SH / "call_windows.parquet", columns=["turn_id", "gap_kind"])
    w = w.join(gk, on="turn_id", how="left").with_columns(pl.col("gap_kind").cast(pl.Utf8))
    w = w.join(consol_flags(w), on="turn_id", how="left").with_columns(pl.col("consol_start").fill_null(False))
    w = w.sort("agent", "pt_date", "t_call", "turn_id")
    w = w.with_columns(trap_id=(pl.col("k_sus") == 1).cast(pl.Int32).cum_sum().over("agent", "pt_date"))
    # trap kind at start is fixed per trap (the same last sustained run for every wake of the trap)
    w = w.with_columns(
        trap_kind=pl.when(pl.col("sus_fail").fill_null(False)).then(pl.lit("after_fail"))
        .when(pl.col("sus_talk").fill_null(False)).then(pl.lit("after_talk")).otherwise(pl.lit("after_work")),
        consol_start=pl.col("consol_start").first().over("agent", "pt_date", "trap_id"),
        r16=(pl.col("goal_no") != 51) | (pl.col("pt_date") < G51_END))
    w = w.drop("t_sus_end", "sus_tid")
    w.write_parquet(R2 / "wakes_r2.parquet", compression="zstd")
    prov = {"built_by": "hypotheses/H72-trap-aging-input-starvation/scheme/build_r2.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["H72 gates.parquet (shared idle_gates)", "call_windows", "context_ledger_items",
                                   "context_ledger_turns", "calls (fail)", "roster", "statement_flags",
                                   "chat_core/chat_text (nudge leading @, in memory only)"]}],
            "params": {"dose_windows_calls": NS, "consol_window_s": [-30, 60], "g51_h16_end": G51_END,
                       "composition": "copied from H16 analysis/r2lib.py (U-call, U-entry, U-rec)"},
            "rows": w.height, "built_at": dt.datetime.now(dt.UTC).isoformat()}
    (R2 / "_provenance.json").write_text(json.dumps(prov, indent=1))
    log(t0, "wakes", w.height)


if __name__ == "__main__":
    main()
