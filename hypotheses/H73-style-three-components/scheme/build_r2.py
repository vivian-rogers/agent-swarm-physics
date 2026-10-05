"""H73 round 2 scheme: conversation state per message, context segments (all regimes) and read vs in-flight source pairs.

Reads round 1's messages.parquet (non-reserved, asserted) and shared tables only; no text is read or written; round-1
outputs are untouched (round-2 outputs go to data/processed/H73-style-three-components/r2/).

Outputs (r2/):
  messages_r2.parquet  round-1 message keys + conversation state at the producing talk call:
                       t_call (producing call), k_since_talk, k_new, pend_ment (items naming the agent received since its
                       previous talk call, through the producing call), pend_nudge, thread_depth (DQ2 parent chain, 0 = no
                       parent), parent_kind, seg (context segment: cumulative resets on cu-mode calls), seg_k (eligible
                       message index in the segment, cu mode only), n_reset_prev / reset_kind_prev (resets between the
                       agent's previous eligible cu message and this one), t_prev (agent's previous eligible message, same
                       PT day), main/copy flags.
  src_pairs.parquet    for each eligible message B with a previous same-day message: every eligible agent message A by
                       another agent that B's author received with A.t in (t_prev, t_B) and lag <= 300 s:
                       cls = read (A posted before the producing call's t_call, so received at a call <= it) or inflight
                       (posted after t_call, before B), lag_s, before_age_s, density (agent items received with A.t in
                       (t_B - 120 s, t_B)), named (ledger ment), uncertain (ledger), parentAB (A is B's DQ2 parent).
Usage: uv run python hypotheses/H73-style-three-components/scheme/build_r2.py
"""
from __future__ import annotations
import os
for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "2"
import datetime as dt  # noqa: E402
import json  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra" / "shared"))
from common import holdout_mask, REVISION  # noqa: E402

SH = ROOT / "data/processed/shared"
DATA = ROOT / "data/processed/H73-style-three-components"
OUT = DATA / "r2"
MAX_LAG = 300.0
DENS_WIN = 120.0


def git_commit() -> str:
    r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    return r.stdout.strip() or "none"


def turns() -> pl.DataFrame:
    ct = (pl.scan_parquet(SH / "context_ledger_turns.parquet").filter(~pl.col("holdout"))
          .select("turn_id", "agent", "t_call", "ctx_mode", "talk", "reset_forced", "reset_consol", "reset_session",
                  "n_ment", "n_nudge_me", "k_since_talk", "k_new").collect()
          .sort("agent", "t_call", "turn_id"))
    cu = pl.col("ctx_mode") == "cu"
    rs = pl.col("reset_forced") | pl.col("reset_consol") | pl.col("reset_session")
    ct = ct.with_columns(
        (rs & cu).cast(pl.Int32).cum_sum().over("agent").alias("seg"),
        (pl.col("reset_forced") & cu).cast(pl.Int32).cum_sum().over("agent").alias("cf"),
        (pl.col("reset_consol") & ~pl.col("reset_forced") & cu).cast(pl.Int32).cum_sum().over("agent").alias("cv"),
        (pl.col("reset_session") & ~pl.col("reset_consol") & cu).cast(pl.Int32).cum_sum().over("agent").alias("cs"),
        pl.col("n_ment").cast(pl.Int32).cum_sum().over("agent").alias("cum_ment"),
        pl.col("n_nudge_me").cast(pl.Int32).cum_sum().over("agent").alias("cum_nudge"),
    )
    # cumulative mentions at the previous talk call (exclusive of the current call)
    ct = ct.with_columns(
        pl.when(pl.col("talk")).then(pl.col("cum_ment")).otherwise(None).shift(1).forward_fill().over("agent")
        .fill_null(0).alias("ment_at_prev_talk"),
        pl.when(pl.col("talk")).then(pl.col("cum_nudge")).otherwise(None).shift(1).forward_fill().over("agent")
        .fill_null(0).alias("nudge_at_prev_talk"))
    return ct.with_columns((pl.col("cum_ment") - pl.col("ment_at_prev_talk")).alias("pend_ment"),
                           (pl.col("cum_nudge") - pl.col("nudge_at_prev_talk")).alias("pend_nudge"))


def thread_depth(msgs: pl.DataFrame) -> pl.DataFrame:
    rp = (pl.scan_parquet(SH / "reply_pairs.parquet").filter((pl.col("pair_set") == "cand") & pl.col("parent")
                                                              & ~pl.col("holdout"))
          .select("b_msg", "a_msg", "a_kind").collect().unique("b_msg", keep="first"))
    par = dict(zip(rp["b_msg"].to_list(), rp["a_msg"].to_list()))
    kind = dict(zip(rp["b_msg"].to_list(), rp["a_kind"].to_list()))
    cc = pl.read_parquet(SH / "chat_core.parquet", columns=["t"]).with_row_index("msg")
    order = np.argsort(cc["t"].dt.epoch("us").to_numpy(), kind="stable")
    depth = {}
    for mi in order.tolist():          # chat_core is sorted by t; msg is the row index
        p = par.get(mi)
        if p is not None:
            depth[mi] = min(1 + depth.get(p, 0), 5)
    d = np.array([depth.get(int(x), 0) for x in msgs["msg"].to_list()], dtype=np.int8)
    k = np.array([kind.get(int(x), -1) for x in msgs["msg"].to_list()], dtype=np.int8)
    return msgs.with_columns(pl.Series("thread_depth", d), pl.Series("parent_kind", k))


def build_messages() -> pl.DataFrame:
    m = pl.read_parquet(DATA / "messages.parquet")
    assert not m["holdout"].any()
    assert not any(holdout_mask(m["pt_date"].to_list(), m["goal_no"].to_list()))
    ct = turns()
    m = m.join(ct.select("turn_id", "t_call", "seg", "cf", "cv", "cs", "pend_ment", "pend_nudge", "k_since_talk",
                         "k_new"), on="turn_id", how="left")
    m = thread_depth(m)
    m = m.sort("agent", "t")
    # previous eligible message of the agent on the same PT day (eligible = main & ~copy), any mode
    el = pl.col("main") & ~pl.col("copy")
    m = m.with_columns(pl.when(el).then(pl.col("t")).otherwise(None).alias("_te"))
    m = m.with_columns(pl.col("_te").shift(1).forward_fill().over("agent", "pt_date").alias("t_prev")).drop("_te")
    # segment position (eligible cu messages) and resets since the previous eligible cu message
    cu = m.filter(el & (pl.col("ctx_mode") == "cu")).select("message_id", "agent", "pt_date", "seg", "cf", "cv", "cs", "t")
    cu = cu.sort("agent", "t").with_columns(
        pl.int_range(1, pl.len() + 1).over("agent", "seg").alias("seg_k"),
        (pl.col("seg") - pl.col("seg").shift(1).over("agent", "pt_date")).alias("n_reset_prev"),
        (pl.col("cf") - pl.col("cf").shift(1).over("agent", "pt_date")).alias("_df"),
        (pl.col("cv") - pl.col("cv").shift(1).over("agent", "pt_date")).alias("_dv"),
        (pl.col("cs") - pl.col("cs").shift(1).over("agent", "pt_date")).alias("_ds"))
    cu = cu.with_columns(
        pl.when(pl.col("n_reset_prev").is_null()).then(pl.lit("first"))
        .when(pl.col("n_reset_prev") == 0).then(pl.lit("within"))
        .when((pl.col("n_reset_prev") == 1) & (pl.col("_df") == 1)).then(pl.lit("forced"))
        .when((pl.col("n_reset_prev") == 1) & (pl.col("_dv") == 1)).then(pl.lit("voluntary"))
        .when((pl.col("n_reset_prev") == 1) & (pl.col("_ds") == 1)).then(pl.lit("session"))
        .otherwise(pl.lit("multi")).alias("reset_kind_prev"))
    m = m.join(cu.select("message_id", "seg_k", "n_reset_prev", "reset_kind_prev"), on="message_id", how="left")
    keep = ["message_id", "msg", "agent", "t", "pt_date", "goal_no", "unit_id", "regime", "room", "main", "copy",
            "restate", "turn_id", "t_call", "ctx_mode", "ctx_pos", "k_ctx", "k_since_talk", "k_new", "pend_ment",
            "pend_nudge", "thread_depth", "parent_kind", "is_reply", "has_mention", "seg", "seg_k", "n_reset_prev",
            "reset_kind_prev", "t_prev"]
    return m.select(keep)


def build_pairs(m: pl.DataFrame) -> pl.DataFrame:
    el = m.filter(pl.col("main") & ~pl.col("copy"))
    B = el.filter(pl.col("t_prev").is_not_null() & pl.col("t_call").is_not_null())
    srcA = el.select(pl.col("message_id").alias("A_id"), pl.col("msg").alias("A_msg"), pl.col("agent").alias("A_agent"),
                     pl.col("t").alias("A_t"))
    it = (pl.scan_parquet(SH / "context_ledger_items.parquet").filter(pl.col("kind") == "agent")
          .select("turn_id", pl.col("message_id").alias("A_id"), "ment", "uncertain").collect())
    ctr = pl.scan_parquet(SH / "context_ledger_turns.parquet").filter(~pl.col("holdout")).select(
        "turn_id", pl.col("agent").alias("rec"), pl.col("t_call").alias("recv_t")).collect()
    it = it.join(ctr, on="turn_id", how="inner").join(srcA, on="A_id", how="inner").filter(pl.col("rec") != pl.col("A_agent"))
    it = it.sort("rec", "A_t")
    rp = (pl.scan_parquet(SH / "reply_pairs.parquet").filter((pl.col("pair_set") == "cand") & pl.col("parent"))
          .select(pl.col("b_msg").alias("B_msg"), pl.col("a_msg").alias("A_msg")).collect()
          .with_columns(pl.lit(True).alias("parentAB")))
    out = []
    for rec, grp in B.group_by("agent"):
        rec = rec[0]
        items = it.filter(pl.col("rec") == rec)
        if items.height == 0:
            continue
        at = items["A_t"].dt.epoch("us").to_numpy()
        rt = items["recv_t"].dt.epoch("us").to_numpy()
        tb = grp["t"].dt.epoch("us").to_numpy()
        tp = grp["t_prev"].dt.epoch("us").to_numpy()
        tc = grp["t_call"].dt.epoch("us").to_numpy()
        lo = np.searchsorted(at, np.maximum(tp, tb - int(MAX_LAG * 1e6)), side="right")
        hi = np.searchsorted(at, tb, side="left")
        dlo = np.searchsorted(at, tb - int(DENS_WIN * 1e6), side="right")
        bi, ai = [], []
        for k in range(len(tb)):
            if hi[k] > lo[k]:
                bi.append(np.full(hi[k] - lo[k], k)); ai.append(np.arange(lo[k], hi[k]))
        if not bi:
            continue
        bi, ai = np.concatenate(bi), np.concatenate(ai)
        dens = (hi - dlo)[bi]
        df = pl.DataFrame({
            "B_id": grp["message_id"].to_numpy()[bi], "B_msg": grp["msg"].to_numpy()[bi], "B_agent": np.full(len(bi), rec, np.int8),
            "A_id": items["A_id"].to_numpy()[ai], "A_msg": items["A_msg"].to_numpy()[ai],
            "A_agent": items["A_agent"].to_numpy()[ai],
            "cls": np.where((at[ai] < tc[bi]) & (rt[ai] <= tc[bi]), "read",
                            np.where((at[ai] >= tc[bi]) & (rt[ai] > tc[bi]), "inflight", "mismatch")),
            "lag_s": ((tb[bi] - at[ai]) / 1e6).astype(np.float32),
            "before_age_s": ((tb[bi] - tp[bi]) / 1e6).astype(np.float32),
            "call_age_s": ((tb[bi] - tc[bi]) / 1e6).astype(np.float32),
            "density": dens.astype(np.int16),
            "named": items["ment"].to_numpy()[ai], "uncertain": items["uncertain"].to_numpy()[ai],
            "unit_id": grp["unit_id"].to_numpy()[bi], "regime": grp["regime"].to_numpy()[bi],
            "pt_date": grp["pt_date"].to_numpy()[bi], "goal_no": grp["goal_no"].to_numpy()[bi],
            "hour": grp["t"].dt.hour().to_numpy()[bi].astype(np.int8),
        })
        out.append(df)
    P = pl.concat(out)
    # a message posted after the producing call's t_call cannot have been received at a call <= it; check the
    # ledger agrees for the read class: the A item was received at a call with t_call <= B's producing t_call
    P = P.join(rp, on=["B_msg", "A_msg"], how="left").with_columns(pl.col("parentAB").fill_null(False))
    return P


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    m = build_messages()
    m.write_parquet(OUT / "messages_r2.parquet", compression="zstd")
    P = build_pairs(m)
    P.write_parquet(OUT / "src_pairs.parquet", compression="zstd")
    el = m.filter(pl.col("main") & ~pl.col("copy"))
    print(f"messages_r2: {m.height:,} rows ({el.height:,} eligible)")
    print(el.group_by("regime", "ctx_mode").agg(pl.len(), (pl.col("pend_ment") > 0).mean().alias("pend_ment>0"),
                                                (pl.col("thread_depth") > 0).mean().alias("depth>0"),
                                                pl.col("k_since_talk").median().alias("k_med")).sort("regime", "ctx_mode"))
    print(el.filter(pl.col("ctx_mode") == "cu").group_by("regime", "reset_kind_prev").len().sort("regime", "reset_kind_prev"))
    print(f"src_pairs: {P.height:,}")
    print(P.group_by("regime", "cls").agg(pl.len(), pl.col("B_id").n_unique().alias("nB"),
                                          (pl.col("lag_s") <= 60).sum().alias("lag<=60"),
                                          pl.col("named").mean().alias("named"), pl.col("uncertain").mean().alias("unc"))
          .sort("regime", "cls"))
    prov = {"built_by": "hypotheses/H73-style-three-components/scheme/build_r2.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["H73 messages.parquet (round 1)", "shared/context_ledger_turns",
                                   "shared/context_ledger_items", "shared/reply_pairs", "shared/chat_core"]}],
            "params": {"segments": "cumulative reset_forced|reset_consol|reset_session on cu-mode calls, per agent",
                       "pend_ment": "sum of ledger n_ment from the call after the previous talk call through the producing call",
                       "thread_depth": "DQ2 parent chain (pair_set cand & parent), capped at 5",
                       "pairs": f"ledger agent items received by B's author with A.t in (t_prev, t_B), lag <= {MAX_LAG} s; "
                                "read if A.t < producing t_call else inflight",
                       "density": f"agent items received with A.t in (t_B - {DENS_WIN} s, t_B)",
                       "holdout": "inherits round 1 (asserted)"},
            "built_at": dt.datetime.now(dt.UTC).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))


if __name__ == "__main__":
    main()
