"""H45 scheme: one row per model call with prompt tokens, context-segment structure, room content and engagement.

Builds data/processed/H45-context-homeostasis/calls.parquet (non-holdout days only) from the shared tables:
  call_windows + context_ledger_turns (DQ1; timing, new items by kind, ctx_pos, resets, the 200-event cap),
  actions / events_core (prompt tokens per call), chat_core (talk messages), context_ledger_items (who received what),
  reply_pairs (DQ2; pair_set = cand, parent = p_reply >= 0.5), roster, period_units.

No text is read or written. The holdout is masked with the calendar flag on the ledger (identical to
common.holdout_mask; asserted). The confirmatory script calls build(include_holdout=True) in memory only.

Prompt tokens (P): total input of the call. Anthropic reports uncached input + cache reads + cache writes separately
(summed, as in the ledger's token validation); Google's input count already includes cached tokens. Action rows carry
usage only for Anthropic and Google; agent events (talk, pause, consolidate, search, ...) carry `tokens_in` for every
lab, but Anthropic's event counts are uncached-only outside chat mode (dropped). P = max over the call's action rows,
else max over its event rows (`p_src` says which).

Room content (per call): the new chat items (k_new, chars_new) and the other room events counted by the ledger
(n_ev - k_new, events by others with no chat text). Converted to tokens later with per-lab coefficients fitted in
analysis/h45lib.py (calibrate_room_tokens), because those are part of the measurement rule, not of the data.

Segment: a maximal run of one agent's cu-mode receiving calls between context resets (ctx_pos restarts at 1).
Engagement: a talk call's message has a DQ2 reply parent among the items the agent received since its previous talk
call (`eng_pending`), any parent at all (`eng_any`); per receiving call, how many of its new items the recipient later
replies to (`n_items_replied`).

Usage: uv run python hypotheses/H45-context-homeostasis/scheme/build.py
"""
from __future__ import annotations

import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H45-context-homeostasis"


def log(*a):
    print(dt.datetime.now().strftime("%H:%M:%S"), *a, flush=True)


def _calls(include_holdout: bool) -> pl.DataFrame:
    cw = pl.scan_parquet(SH / "call_windows.parquet").select(
        "turn_id", "agent", "pt_date", "goal_no", "regime", "holdout", "kind", "talk", "src", "ctx_mode", "n_rec",
        "t_call", "start_conf", "t_first", "t_log", "t_end", "gap_kind", "after_pause", "first_of_day", "pause_s",
        "prev_busy_s")
    lt = pl.scan_parquet(SH / "context_ledger_turns.parquet").select(
        "turn_id", "t_prev_call", "room", "room_changed", "n_agent", "n_human", "n_nudge", "n_pause_resume",
        "n_automated_other", "n_ment", "n_nudge_me", "k_new", "k_since_talk", "k_ctx", "chars_new", "n_inflight",
        "n_uncertain", "n_ev", "cap_hit", "n_omitted", "reset_consol", "reset_forced", "reset_session", "ctx_pos",
        "prev_seg_len", "lookback_capped")
    c = cw.join(lt, on="turn_id", how="left")
    if not include_holdout:
        c = c.filter(~pl.col("holdout"))
    c = c.collect().sort("agent", "t_first")
    # the calendar flag must agree with the locked-holdout rule
    chk = c.select("pt_date", "goal_no", "holdout").unique()
    hm = holdout_mask(chk["pt_date"].to_list(), chk["goal_no"].fill_null(0).to_list())
    assert all(a == b for a, b in zip(hm, chk["holdout"].to_list())), "holdout flag disagrees with holdout_mask"
    return c


def _tokens(c: pl.DataFrame, lab: dict) -> pl.DataFrame:
    """Attach P (prompt tokens) per call from action rows (Anthropic/Google) or agent events (all labs)."""
    anth = [a for a, l in lab.items() if l == "Anthropic"]
    t0, t1 = c["t_first"].min(), c["t_log"].max()
    acts = (pl.scan_parquet(SH / "actions.parquet")
            .filter((pl.col("t") >= t0) & (pl.col("t") <= t1) & pl.col("tok_in").is_not_null())
            .select("t", "agent", pl.when(pl.col("agent").is_in(anth))
                    .then(pl.col("tok_in").fill_null(0) + pl.col("tok_cache_read").fill_null(0)
                          + pl.col("tok_cache_write").fill_null(0))
                    .otherwise(pl.col("tok_in")).cast(pl.Int32).alias("tok"))
            .collect())
    evs = (pl.scan_parquet(SH / "events_core.parquet")
           .filter((pl.col("actor_kind") == "agent") & (pl.col("t") >= t0) & (pl.col("t") <= t1)
                   & pl.col("tokens_in").is_not_null() & (pl.col("tokens_in") > 0))
           .select("t", "agent", pl.col("tokens_in").cast(pl.Int32).alias("tok")).collect())
    win = c.select("turn_id", "agent", "t_first", "t_log").sort("agent", "t_first")
    out = c
    for name, rows in (("p_act", acts), ("p_ev", evs)):
        j = (rows.sort("agent", "t").join_asof(win, left_on="t", right_on="t_first", by="agent", strategy="backward")
             .filter(pl.col("turn_id").is_not_null() & (pl.col("t") <= pl.col("t_log") + pl.duration(milliseconds=50)))
             .group_by("turn_id").agg(pl.col("tok").max().alias(name)))
        out = out.join(j, on="turn_id", how="left")
    # Anthropic events report uncached input only in computer-use mode (median 10 tokens in regime III vs ~48k on the
    # call's action rows; structural check 2026-10-04), so Anthropic event tokens are used only for chat-mode calls
    anth_bad = pl.col("agent").is_in(anth) & (pl.col("ctx_mode") != "chat")
    out = out.with_columns(pl.when(anth_bad).then(None).otherwise(pl.col("p_ev")).alias("p_ev"))
    return out.with_columns(
        pl.coalesce("p_act", "p_ev").alias("P"),
        pl.when(pl.col("p_act").is_not_null()).then(pl.lit("act")).when(pl.col("p_ev").is_not_null())
        .then(pl.lit("ev")).otherwise(None).alias("p_src"))


def _segments(c: pl.DataFrame) -> pl.DataFrame:
    """Segment id = cumulative count of ctx_pos == 1 among the agent's cu-mode receiving calls."""
    c = c.sort("agent", "t_first")
    cu = pl.col("ctx_mode") == "cu"
    c = c.with_columns(pl.when(cu).then((pl.col("ctx_pos") == 1).cast(pl.Int32)).otherwise(0).alias("_new"))
    c = c.with_columns(pl.col("_new").cum_sum().over("agent").alias("seg_local"))
    c = c.with_columns(pl.when(cu).then(pl.col("agent").cast(pl.Int64) * 1_000_000 + pl.col("seg_local"))
                       .otherwise(None).alias("seg"))
    # cumulative room content in the segment, inclusive of this call (what sits in this call's context)
    other_ev = (pl.col("n_ev") - pl.col("k_new")).clip(0, None)
    c = c.with_columns(other_ev.alias("n_oev"))
    c = c.with_columns(
        pl.when(cu).then(pl.col("k_new").cum_sum().over("seg")).alias("cum_k"),
        pl.when(cu).then(pl.col("chars_new").cum_sum().over("seg")).alias("cum_chars"),
        pl.when(cu).then(pl.col("n_oev").cum_sum().over("seg")).alias("cum_oev"))
    # segment summaries: length (receiving calls), how it ended (the next segment's opening flags)
    seg = (c.filter(cu).group_by("seg").agg(pl.len().alias("seg_len_calls"), pl.col("agent").first(),
                                            pl.col("t_first").min().alias("seg_t0"), pl.col("t_log").max().alias("seg_t1"))
           .sort("agent", "seg_t0"))
    first = (c.filter(cu & (pl.col("ctx_pos") == 1))
             .select("seg", "reset_forced", "reset_consol", "reset_session", "first_of_day", "prev_seg_len"))
    seg = seg.join(first.rename({"reset_forced": "open_forced", "reset_consol": "open_consol",
                                 "reset_session": "open_session", "first_of_day": "open_fod",
                                 "prev_seg_len": "open_prev_seg_len"}), on="seg", how="left")
    # end type of a segment = opening flags of the agent's next segment (same day)
    seg = seg.with_columns(
        pl.col("open_forced").shift(-1).over("agent").alias("end_forced"),
        pl.col("open_consol").shift(-1).over("agent").alias("end_consol"),
        pl.col("open_session").shift(-1).over("agent").alias("end_session"),
        pl.col("open_fod").shift(-1).over("agent").alias("end_nextday"))
    c = c.join(seg.select("seg", "seg_len_calls", "open_forced", "open_consol", "open_session", "open_fod",
                          "end_forced", "end_consol", "end_session", "end_nextday"), on="seg", how="left")
    return c.drop("_new", "seg_local")


def _engagement(c: pl.DataFrame) -> pl.DataFrame:
    """Talk-call reply engagement (DQ2 parents) and per-receiving-call count of items the recipient later replies to."""
    t0, t1 = c["t_first"].min(), c["t_log"].max()
    chat = (pl.scan_parquet(SH / "chat_core.parquet")
            .filter((pl.col("speaker_kind").cast(pl.Utf8) == "agent") & (pl.col("t") >= t0 - pl.duration(seconds=5))
                    & (pl.col("t") <= t1 + pl.duration(seconds=5)))
            .select("message_id", "t", "agent").collect().sort("agent", "t"))
    talks = c.filter(pl.col("talk")).select("turn_id", "agent", "t_first", "t_log").sort("agent", "t_first")
    # talk message -> its call: latest talk call starting <= t + 2 s, with t <= t_log + 2 s
    bm = (chat.with_columns((pl.col("t") + pl.duration(seconds=2)).alias("tq"))
          .join_asof(talks, left_on="tq", right_on="t_first", by="agent", strategy="backward")
          .filter(pl.col("turn_id").is_not_null() & (pl.col("t") <= pl.col("t_log") + pl.duration(seconds=2)))
          .select("message_id", "turn_id", "agent"))
    rp = (pl.scan_parquet(SH / "reply_pairs.parquet")
          .filter((pl.col("pair_set").cast(pl.Utf8) == "cand") & pl.col("parent"))
          .select("B_message_id", "A_message_id", "p_reply", "a_kind").collect())
    par = bm.join(rp, left_on="message_id", right_on="B_message_id", how="inner")
    # items -> the recipient's next talk call at or after the receiving call
    items = (pl.scan_parquet(SH / "context_ledger_items.parquet").select("turn_id", "message_id", "kind").collect()
             .join(c.select("turn_id", "agent"), on="turn_id", how="inner"))
    tk = c.filter(pl.col("talk")).select("agent", "turn_id").sort("agent", "turn_id")
    nxt = {}
    for (a,), sub in tk.group_by(["agent"]):
        nxt[int(a)] = np.sort(sub["turn_id"].to_numpy())
    it_ag = items["agent"].to_numpy()
    it_tid = items["turn_id"].to_numpy()
    nt = np.full(len(items), -1, dtype=np.int64)
    for a, arr in nxt.items():
        m = it_ag == a
        k = np.searchsorted(arr, it_tid[m], side="left")
        ok = k < len(arr)
        v = np.full(m.sum(), -1, dtype=np.int64)
        v[ok] = arr[k[ok]]
        nt[m] = v
    items = items.with_columns(pl.Series("next_talk", nt))
    # talk-level: does the parent sit in the pending set (items with next_talk == this talk)?
    par = par.join(items.select(pl.col("message_id").alias("A_message_id"), "agent", "next_talk",
                                pl.col("turn_id").alias("a_turn")), on=["A_message_id", "agent"], how="left")
    tl = (par.group_by("turn_id").agg(
        pl.len().alias("n_parents"),
        (pl.col("next_talk") == pl.col("turn_id")).any().alias("eng_pending"),
        pl.col("a_turn").is_not_null().any().alias("eng_item")))
    c = c.join(tl, on="turn_id", how="left")
    c = c.with_columns(pl.when(pl.col("talk")).then(pl.col("n_parents").fill_null(0) > 0).otherwise(None).alias("eng_any"),
                       pl.when(pl.col("talk")).then(pl.col("eng_pending").fill_null(False)).otherwise(None)
                       .alias("eng_pending")).drop("eng_item", "n_parents")
    # receiving-call level: items later replied to by the recipient
    replied = par.filter(pl.col("a_turn").is_not_null()).select(pl.col("A_message_id").alias("message_id"), "agent").unique()
    ir = (items.join(replied.with_columns(pl.lit(True).alias("rep")), on=["message_id", "agent"], how="left")
          .group_by("turn_id").agg(pl.col("rep").fill_null(False).sum().cast(pl.Int16).alias("n_items_replied"),
                                   (pl.col("kind").cast(pl.Utf8) == "agent").sum().cast(pl.Int16).alias("_nag")))
    c = c.join(ir.select("turn_id", "n_items_replied"), on="turn_id", how="left").with_columns(
        pl.col("n_items_replied").fill_null(0))
    return c


def build(include_holdout: bool = False) -> pl.DataFrame:
    ro = pl.read_parquet(SH / "roster.parquet")
    lab = dict(zip(ro["agent"].to_list(), ro["lab"].to_list()))
    log("calls")
    c = _calls(include_holdout)
    log(f"  {c.height:,} calls")
    c = _tokens(c, lab)
    log(f"  P present: {c['P'].is_not_null().mean():.3f}")
    c = _segments(c)
    c = _engagement(c)
    pu = pl.read_parquet(SH / "period_units.parquet").select("unit_id", "goal_no", "days").explode("days").rename(
        {"days": "pt_date"})
    c = c.join(pu.unique(subset=["pt_date"], keep="last").select("pt_date", "unit_id"), on="pt_date", how="left")
    c = c.with_columns(pl.col("agent").replace_strict(lab, default="Other").alias("lab"),
                       pl.col("regime").cast(pl.Utf8))
    keep = ["turn_id", "agent", "lab", "pt_date", "goal_no", "unit_id", "regime", "holdout", "kind", "talk", "src",
            "ctx_mode", "start_conf", "t_call", "t_first", "t_log", "gap_kind", "after_pause", "first_of_day",
            "pause_s", "room", "n_agent", "n_human", "n_nudge", "n_pause_resume", "n_ment", "k_new", "k_since_talk",
            "chars_new", "n_ev", "n_oev", "n_uncertain", "cap_hit", "n_omitted", "reset_consol", "reset_forced",
            "reset_session", "ctx_pos", "prev_seg_len", "seg", "seg_len_calls", "open_forced", "open_consol",
            "open_session", "open_fod", "end_forced", "end_consol", "end_session", "end_nextday", "cum_k",
            "cum_chars", "cum_oev", "P", "p_src", "p_act", "p_ev", "eng_any", "eng_pending", "n_items_replied"]
    c = c.select(keep).with_columns(
        pl.col("pause_s").cast(pl.Float32), pl.col("cum_k").cast(pl.Int32), pl.col("cum_chars").cast(pl.Int32),
        pl.col("cum_oev").cast(pl.Int32), pl.col("n_oev").cast(pl.Int32), pl.col("lab").cast(pl.Categorical),
        pl.col("regime").cast(pl.Categorical), pl.col("p_src").cast(pl.Categorical),
        pl.col("unit_id").cast(pl.Categorical))
    return c


def git_commit() -> str:
    r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "hypotheses/H45-context-homeostasis"],
                           capture_output=True, text=True).stdout
    return (r.stdout.strip() or "none") + ("+uncommitted" if dirty.strip() else "")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    c = build(include_holdout=False)
    assert not c["holdout"].any()
    c.write_parquet(OUT / "calls.parquet", compression="zstd", compression_level=9)
    log(f"wrote calls.parquet: {c.height:,} rows, {(OUT / 'calls.parquet').stat().st_size / 1e6:.1f} MB")
    prov = {"built_by": "hypotheses/H45-context-homeostasis/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["shared/call_windows", "shared/context_ledger_turns", "shared/context_ledger_items",
                                   "shared/actions", "shared/events_core", "shared/chat_core", "shared/reply_pairs",
                                   "shared/roster", "shared/period_units"]}],
            "params": {"holdout": "excluded (calendar flag == common.holdout_mask)",
                       "P": "Anthropic tok_in+cache_read+cache_write; Google tok_in; else events tokens_in",
                       "engagement": "reply_pairs pair_set=cand & parent (p_reply>=0.5)",
                       "not_used": "outage_s/outage_off (derive from the buggy activity_bins; DQ7)"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    p = OUT / "_provenance.json"
    old = json.loads(p.read_text()) if p.exists() else {}
    old["calls.parquet"] = prov
    p.write_text(json.dumps(old, indent=1))


if __name__ == "__main__":
    main()
