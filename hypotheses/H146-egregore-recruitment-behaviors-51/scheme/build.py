"""H146 scheme: event tables for read-gated recruitment, wipes, repair and newcomers in #51 (07-06 -> 09-04).

Builds data/processed/H146-egregore-recruitment-behaviors-51/events/ from shared tables only. No text is stored:
message ids, integer indices, times and flags. Reserved days (51m) are masked with `common.holdout_mask` and asserted.

Tables (all times int64 microseconds UTC):
  msgs.parquet       #51 chat messages: msg (index), message_id, t, pt_date, room, agent (-1 if not an agent),
                     skind (0 agent, 1 human, 2 automated/nudge), srow (row in embeddings/statements.parquet), mentions
  calls.parquet      agent calls (no summary-mode, no Claude Code): turn_id, agent, pt_date, unit, t_call, t_first,
                     kind, talk, room, ctx_pos, reset flags, seq (order within agent-day), d_s (matched lag, s)
  stmts.parquet      statements (chat + consolidation intents): srow, kind, agent, t, turn_id (producing call), msg
  talkrows.parquet   one row per talk call with >= 1 chat message: row, turn_id, agent, pt_date, unit, t_call,
                     t_first, d_s, room, before_age_s, dens10, msgs (its own chat messages)
  window_items.parquet  (row, msg, w, named): other agents' agent-kind messages in the caller's room posted in the
                     mirror window (t_c - d_c, t_c) [w = 0, read] or in flight (t_c, t_c + d_c] [w = 1] (H67 rule)
  reads.parquet      ledger read-out items (agent-kind senders, not self): agent, turn_id, t_recv (= t_call of the
                     receiving call), msg, ment (names the reader), uncertain
  erasures.parquet   forced erasures F (reset_forced, not first of day) and placebo calls P (ctx_pos 20, no reset in
                     the next 10 calls) (H58 R3 rule): turn_id, agent, unit, pt_date, t_call, etype, t10, t20, projs10
  touches.parquet    project touches (`project_calls.proj`, mapped to slugs; never `label`): agent, turn_id, t, slug
  challenges.parquet DQ2 parent replies B -> A between different agents: a_msg, b_msg, t_b, a_agent, b_agent,
                     opposes (DQ2), disagree_val (DQ10 `disagree_validated_agent`), stance2
  newcomers.json     arrival dates of agents that join during #51
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra" / "shared"))
from common import holdout_mask, git_commit  # noqa: E402

SH = ROOT / "data" / "processed" / "shared"
OUT = ROOT / "data" / "processed" / "H146-egregore-recruitment-behaviors-51" / "events"
GOAL = 51
D0, D1 = "2026-07-06", "2026-09-04"
CLAUDE_CODE = 19
US = 1_000_000
REVISION = "see data/raw/ai-village/_source.md"


def _keep(df: pl.DataFrame, dcol="pt_date") -> pl.DataFrame:
    df = df.filter((pl.col(dcol) >= D0) & (pl.col(dcol) <= D1))
    m = np.array(holdout_mask(df[dcol].to_list(), [GOAL] * df.height), dtype=bool)
    df = df.filter(pl.Series(~m))
    assert df.height == 0 or (df[dcol].max() <= D1), "reserved rows leaked"
    return df


def units() -> pl.DataFrame:
    pu = pl.read_parquet(SH / "period_units.parquet").filter((pl.col("goal_no") == GOAL) & ~pl.col("holdout"))
    return pu.select("unit_id", "days").explode("days").rename({"days": "pt_date"})


def build_msgs(U):
    ch = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "pt_date", "goal_no", "room",
                                                             "speaker_kind", "agent"])
    ch = _keep(ch.filter(pl.col("goal_no") == GOAL)).sort("t", "message_id")
    mc = pl.read_parquet(SH / "chat_mentions_clean.parquet", columns=["message_id", "mentions_clean"])
    ch = ch.join(mc, on="message_id", how="left")
    st = pl.read_parquet(SH / "embeddings" / "statements.parquet").with_row_index("srow")
    ci = pl.read_parquet(SH / "embeddings" / "chat_index.parquet").with_row_index("crow")
    sm = st.filter(pl.col("kind") == "chat").join(ci, left_on="src_row", right_on="crow").select("message_id", "srow")
    ch = ch.join(sm, on="message_id", how="left")
    sk = pl.when(pl.col("speaker_kind").cast(pl.Utf8) == "agent").then(0).when(
        pl.col("speaker_kind").cast(pl.Utf8) == "human").then(1).otherwise(2).cast(pl.Int8)
    ch = ch.with_row_index("msg").with_columns(
        pl.col("msg").cast(pl.Int32), sk.alias("skind"),
        pl.when(pl.col("speaker_kind").cast(pl.Utf8) == "agent").then(pl.col("agent")).otherwise(-1).cast(pl.Int8)
        .alias("agent"),
        pl.col("t").dt.epoch("us").alias("t"), pl.col("mentions_clean").fill_null([]).alias("mentions"))
    ch = ch.join(U, on="pt_date", how="left")
    return ch.select("msg", "message_id", "t", "pt_date", "unit_id", "room", "agent", "skind", "srow", "mentions")


def build_calls(U):
    tu = pl.scan_parquet(SH / "context_ledger_turns.parquet").filter(pl.col("goal_no") == GOAL).select(
        "turn_id", "agent", "pt_date", "t_call", "t_first", "kind", "talk", "ctx_mode", "room", "ctx_pos",
        "reset_forced", "reset_consol", "reset_session", "first_of_day").collect()
    tu = _keep(tu).filter((pl.col("agent") != CLAUDE_CODE)).sort("agent", "t_call", "turn_id")
    tu = tu.with_columns(pl.col("t_call").dt.epoch("us"), pl.col("t_first").dt.epoch("us"),
                         pl.col("kind").cast(pl.Utf8), pl.col("ctx_mode").cast(pl.Utf8))
    d = ((pl.col("t_first") - pl.col("t_call")) / US).clip(1.0, 120.0).fill_null(1.0)
    tu = tu.with_columns(d.cast(pl.Float32).alias("d_s"),
                         pl.int_range(pl.len()).over("agent", "pt_date").cast(pl.Int32).alias("seq"))
    return tu.join(U, on="pt_date", how="left")


def build_stmts(msgs, calls):
    st = pl.read_parquet(SH / "embeddings" / "statements.parquet").with_row_index("srow")
    st = _keep(st.filter(pl.col("goal_no") == GOAL)).with_columns(pl.col("t").dt.epoch("us"))
    pc = pl.read_parquet(SH / "producing_calls.parquet", columns=["message_id", "turn_id_prod"])
    chat = msgs.filter(pl.col("skind") == 0).join(pc, on="message_id", how="left").select(
        "srow", "msg", pl.col("turn_id_prod").alias("turn_id"))
    out_c = st.filter(pl.col("kind") == "chat").join(chat, on="srow", how="left")
    # intents: the agent's latest consolidate call at or before t
    cons = calls.filter(pl.col("kind") == "consolidate").select("agent", "t_call", "turn_id").sort("t_call")
    it = st.filter(pl.col("kind") == "intent").sort("t")
    it = it.join_asof(cons, left_on="t", right_on="t_call", by="agent", strategy="backward").drop("t_call")
    it = it.with_columns(pl.lit(None, dtype=pl.Int32).alias("msg"))
    cols = ["srow", "kind", "agent", "t", "pt_date", "turn_id", "msg"]
    return pl.concat([out_c.select(cols), it.select(cols)]).sort("t")


def build_talkrows(msgs, calls, stmts):
    am = msgs.filter(pl.col("skind") == 0)
    prod = stmts.filter(pl.col("kind") == "chat").group_by("turn_id").agg(pl.col("msg").sort())
    tr = calls.filter(pl.col("talk")).join(prod, on="turn_id", how="inner").rename({"msg": "msgs"}).sort("t_call")
    # before-age: time since the agent's previous chat message (any day; inf if none) at t_call
    prev = am.select(pl.col("agent"), pl.col("t").alias("t_prev")).sort("t_prev")
    tr = tr.with_columns((pl.col("t_call") - 1).alias("_tq")).sort("_tq")
    tr = tr.join_asof(prev, left_on="_tq", right_on="t_prev", by="agent", strategy="backward")
    tr = tr.with_columns(((pl.col("t_call") - pl.col("t_prev")) / US).fill_null(1e9).cast(pl.Float32)
                         .alias("before_age_s")).drop("_tq", "t_prev")
    tr = tr.sort("t_call").with_row_index("row").with_columns(pl.col("row").cast(pl.Int32))
    # room message stream (agent-kind), window items and density
    W, dens = [], np.zeros(tr.height, dtype=np.int16)
    ag_m = am.select("msg", "t", "room", "agent", "mentions")
    for (room,), g in ag_m.partition_by("room", as_dict=True).items():
        g = g.sort("t")
        tm = g["t"].to_numpy(); mid = g["msg"].to_numpy(); snd = g["agent"].to_numpy()
        men = g["mentions"].to_list()
        sub = tr.filter(pl.col("room") == room)
        if sub.height == 0:
            continue
        rows = sub["row"].to_numpy(); tc = sub["t_call"].to_numpy(); ag = sub["agent"].to_numpy()
        dc = (sub["d_s"].to_numpy().astype(np.float64) * US).astype(np.int64)
        lo = np.searchsorted(tm, tc - dc, side="right")      # posted > t_c - d_c
        mid_ = np.searchsorted(tm, tc, side="left")          # posted < t_c
        hi = np.searchsorted(tm, tc + dc, side="right")      # posted <= t_c + d_c
        d10 = np.searchsorted(tm, tc - 600 * US, side="left")
        dens[rows] = np.minimum(mid_ - d10, 32000)
        for r, a, l0, m0, h0 in zip(rows, ag, lo, mid_, hi):
            for j in range(l0, h0):
                if snd[j] == a:
                    continue
                W.append((r, mid[j], 0 if j < m0 else 1, a in men[j]))
    wi = pl.DataFrame(W, schema={"row": pl.Int32, "msg": pl.Int32, "w": pl.Int8, "named": pl.Boolean}, orient="row")
    tr = tr.with_columns(pl.Series("dens10", dens))
    keep = ["row", "turn_id", "agent", "pt_date", "unit_id", "t_call", "t_first", "d_s", "room", "before_age_s",
            "dens10", "msgs"]
    return tr.select(keep), wi


def build_reads(msgs, calls):
    it = pl.scan_parquet(SH / "context_ledger_items.parquet").select(
        "turn_id", "message_id", "sender", "kind", "ment", "uncertain").filter(pl.col("kind") == "agent").collect()
    cl = calls.select("turn_id", "agent", "t_call")
    it = it.join(cl, on="turn_id", how="inner").filter(pl.col("sender") != pl.col("agent"))
    it = it.join(msgs.select("message_id", "msg"), on="message_id", how="inner")
    return it.select("agent", "turn_id", pl.col("t_call").alias("t_recv"), "msg", "ment", "uncertain") \
        .sort("agent", "t_recv")


def slug(s: str | None) -> str | None:
    if s is None:
        return None
    s = s.rstrip("/")
    return s.split("/")[-1].lower() if s else None


def build_touches(calls):
    pc = pl.scan_parquet(SH / "project_calls.parquet").filter((pl.col("goal_no") == GOAL) & pl.col("proj")
                                                            .is_not_null()).select("turn_id", "agent", "pt_date",
                                                                                   "t_call", "proj").collect()
    pc = _keep(pc).join(calls.select("turn_id"), on="turn_id", how="semi")
    pc = pc.with_columns(pl.col("t_call").dt.epoch("us").alias("t"),
                         pl.col("proj").map_elements(slug, return_dtype=pl.Utf8).alias("slug"))
    return pc.select("agent", "turn_id", "t", "slug").sort("agent", "t")


def build_erasures(calls, touches):
    tu = calls.filter(pl.col("ctx_mode") != "summary").sort("agent", "t_call", "turn_id")
    tu = tu.with_columns((pl.col("reset_consol") | pl.col("reset_session") | pl.col("reset_forced"))
                         .cast(pl.Int32).alias("_r"))
    tu = tu.with_columns(pl.col("_r").reverse().rolling_sum(10, min_samples=1).reverse().shift(-1)
                         .over("agent").fill_null(0).alias("_r_next10"))
    et = pl.when(pl.col("reset_forced")).then(pl.lit("F")).when(pl.col("ctx_pos") == 20).then(pl.lit("P")) \
        .otherwise(None)
    tu = tu.with_columns(et.alias("etype"))
    ev = tu.filter(pl.col("etype").is_not_null() & ~pl.col("first_of_day"))
    ev = ev.filter((pl.col("etype") == "F") | (pl.col("_r_next10") == 0))
    # calls 1-10 / 1-20: the event call and the next 9 / 19 calls of the agent-day, truncated at the next reset
    out = []
    by = {a: g for (a,), g in tu.select("agent", "pt_date", "t_call", "_r", "turn_id").partition_by(
        "agent", as_dict=True).items()}
    tby = {a: g for (a,), g in touches.partition_by("agent", as_dict=True).items()}
    for a, g in ev.partition_by("agent", as_dict=True).items():
        a = a[0]
        G = by[a]; tg = G["t_call"].to_numpy(); dg = G["pt_date"].to_numpy(); rg = G["_r"].to_numpy()
        pos = {t: i for i, t in enumerate(G["turn_id"].to_list())}
        T = tby.get(a)
        tt = T["t"].to_numpy() if T is not None else np.array([], dtype=np.int64)
        ts = T["slug"].to_list() if T is not None else []
        for r in g.iter_rows(named=True):
            i = pos[r["turn_id"]]
            j10 = j20 = i
            for k in range(1, 20):
                if i + k >= len(tg) or dg[i + k] != dg[i] or rg[i + k]:
                    break
                if k < 10:
                    j10 = i + k
                j20 = i + k
            t10 = int(tg[j10]); t20 = int(tg[j20])
            lo, hi = np.searchsorted(tt, r["t_call"], "left"), np.searchsorted(tt, t10, "right")
            out.append({"turn_id": r["turn_id"], "agent": a, "unit_id": r["unit_id"], "pt_date": r["pt_date"],
                        "t_call": r["t_call"], "etype": r["etype"], "t10": t10, "t20": t20,
                        "n10": j10 - i + 1, "projs10": sorted({s for s in ts[lo:hi] if s})})
    return pl.DataFrame(out).sort("agent", "t_call")


def build_challenges(msgs):
    rs = pl.read_parquet(SH / "reply_stance_v2.parquet", columns=[
        "B_message_id", "A_message_id", "b_agent", "a_kind", "a_agent", "pt_date", "goal_no", "parent",
        "dq2_stance", "stance2", "disagree_validated_agent", "holdout"])
    rs = _keep(rs.filter((pl.col("goal_no") == GOAL) & pl.col("parent") & ~pl.col("holdout")))
    rs = rs.filter(pl.col("a_agent").is_not_null() & (pl.col("a_agent") != pl.col("b_agent")))
    m = msgs.select("message_id", "msg", "t", "skind")
    rs = rs.join(m.rename({"message_id": "A_message_id", "msg": "a_msg", "t": "t_a", "skind": "a_sk"}),
                 on="A_message_id", how="inner")
    rs = rs.join(m.rename({"message_id": "B_message_id", "msg": "b_msg", "t": "t_b", "skind": "b_sk"}),
                 on="B_message_id", how="inner")
    rs = rs.filter((pl.col("a_sk") == 0) & (pl.col("b_sk") == 0))
    return rs.select("a_msg", "b_msg", "t_a", "t_b", "a_agent", "b_agent",
                     (pl.col("dq2_stance").cast(pl.Utf8) == "opposes").alias("opposes"),
                     pl.col("disagree_validated_agent").fill_null(False).alias("disagree_val"),
                     pl.col("stance2").cast(pl.Utf8)).sort("t_b")


def build_newcomers(calls):
    ro = pl.read_parquet(SH / "roster.parquet").select("agent", "name", "lab", "joined")
    first = calls.group_by("agent").agg(pl.col("t_call").min().alias("t_first_call"),
                                        pl.col("pt_date").min().alias("first_day"))
    nc = ro.join(first, on="agent").filter(pl.col("joined") >= D0).sort("joined")
    return [{"agent": r["agent"], "lab": r["lab"], "joined": r["joined"], "first_day": r["first_day"],
             "t_first_call": r["t_first_call"], "ne33": r["joined"] >= "2026-09-03"} for r in nc.iter_rows(named=True)]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    U = units()
    msgs = build_msgs(U); print("msgs", msgs.height, flush=True)
    calls = build_calls(U); print("calls", calls.height, flush=True)
    stmts = build_stmts(msgs, calls); print("stmts", stmts.height, stmts["turn_id"].null_count(), flush=True)
    tr, wi = build_talkrows(msgs, calls, stmts); print("talkrows", tr.height, "window items", wi.height, flush=True)
    reads = build_reads(msgs, calls); print("reads", reads.height, flush=True)
    touches = build_touches(calls); print("touches", touches.height, flush=True)
    er = build_erasures(calls, touches); print("erasures", er.group_by("etype").len().rows(), flush=True)
    chg = build_challenges(msgs); print("challenges", chg.height, chg["disagree_val"].sum(), chg["opposes"].sum())
    nc = build_newcomers(calls)
    for name, df in [("msgs", msgs), ("calls", calls.drop("ctx_mode")), ("stmts", stmts), ("talkrows", tr),
                     ("window_items", wi), ("reads", reads), ("touches", touches), ("erasures", er),
                     ("challenges", chg)]:
        assert df.height > 0, name
        if "pt_date" in df.columns:
            assert df["pt_date"].max() <= D1 and df["pt_date"].min() >= D0, name
        df.write_parquet(OUT / f"{name}.parquet", compression="zstd")
    (OUT / "newcomers.json").write_text(json.dumps(nc, indent=1))
    prov = {"built_by": "hypotheses/H146-egregore-recruitment-behaviors-51/scheme/build.py",
            "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["chat_core", "chat_mentions_clean", "context_ledger_turns", "context_ledger_items",
                                   "producing_calls", "embeddings/statements", "embeddings/chat_index",
                                   "project_calls (proj)", "reply_stance_v2", "roster", "period_units"]}],
            "params": {"goal": GOAL, "span": [D0, D1], "matched_lag_clip_s": [1, 120],
                       "placebo": "ctx_pos 20, no reset in next 10 calls", "reserved": "masked (holdout_mask)"},
            "built_at": __import__("datetime").datetime.now(__import__("datetime").UTC).isoformat()}
    pp = OUT.parent / "_provenance.json"
    P = json.loads(pp.read_text()) if pp.exists() else {}
    P["events"] = prov
    pp.write_text(json.dumps(P, indent=1))
    print("done")


if __name__ == "__main__":
    main()
