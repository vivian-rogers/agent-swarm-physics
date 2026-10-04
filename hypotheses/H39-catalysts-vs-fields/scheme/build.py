"""H39 scheme: behavior states, lever events and erasure events for non-holdout days.

Outputs (data/processed/H39-catalysts-vs-fields/):
  states_b6.parquet   agent x minute of each non-holdout day (H14's builder, imported): pt_date, minute, agent,
                      coarse_min (0 browse, 1 type, 2 shell, 3 chat, 4 idle, 5 consolidate), n_rec, present
  kicks.parquet       one row per (message, recipient agent) for directed/human kicks on non-holdout days:
                      agent, t, pt_date, cls (N_tgt / H_men / H_und / A_men), msg (chat_core row), emb (row in
                      chat_bge_small, -1 if missing). Same class rules as H16's load_kicks (checked equal).
  erasures.parquet    consolidation events from H15 (kind CF forced at the 41-turn cap, CV voluntary, other)
  _provenance.json

Holdout days are never read (calendar.holdout == False, asserted against holdout.json).
Usage: uv run python hypotheses/H39-catalysts-vs-fields/scheme/build.py
"""
from __future__ import annotations

import os

os.environ.setdefault("POLARS_MAX_THREADS", "2")

import datetime as dt
import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
sys.path.insert(0, str(ROOT / "hypotheses/H14-behavior-entropy-production/scheme"))
sys.path.insert(0, str(ROOT / "hypotheses/H16-metastable-traps-kramers/analysis"))
from common import REVISION, git_commit, holdout_mask  # noqa: E402
import build_states as H14  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H39-catalysts-vs-fields"


def nonholdout_days() -> list[str]:
    cal = pl.read_parquet(SH / "calendar.parquet")
    m = holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    assert list(m) == cal["holdout"].to_list(), "calendar.holdout disagrees with holdout.json"
    return cal.filter(~pl.col("holdout") & (pl.col("window_s") > 0))["pt_date"].to_list()


def load_kick_table(days: list[str], allow_holdout: bool = False) -> pl.DataFrame:
    """Directed/human kicks with message rows. Mirrors h16lib.load_kicks (exposure recipients,
    chat_mentions_clean.mentions_roster); automated messages without a valid mention (bookends) dropped."""
    if not allow_holdout:
        cal = pl.read_parquet(SH / "calendar.parquet").filter(pl.col("pt_date").is_in(days))
        assert not cal["holdout"].any(), "holdout day requested"
    chat = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "pt_date", "speaker_kind"]).with_row_index("msg")
    men = pl.read_parquet(SH / "chat_mentions_clean.parquet", columns=["message_id", "mentions_roster"])
    assert chat.height == men.height and (chat["message_id"] == men["message_id"]).all(), "chat_mentions_clean misaligned"
    chat = chat.with_columns(men["mentions_roster"].alias("men")).filter(pl.col("pt_date").is_in(days))
    emb = pl.read_parquet(SH / "embeddings/chat_index.parquet").with_row_index("emb")
    chat = chat.join(emb.select("message_id", pl.col("emb").cast(pl.Int64)), on="message_id", how="left")
    ex = pl.read_parquet(SH / "exposure.parquet", columns=["msg", "agent"]).join(chat, on="msg", how="inner")
    sk = pl.col("speaker_kind").cast(pl.Utf8)
    directed = pl.col("men").list.contains(pl.col("agent")).fill_null(False)
    ex = ex.with_columns(
        pl.when((sk == "agent") & directed).then(pl.lit("A_men"))
        .when((sk == "human") & directed).then(pl.lit("H_men"))
        .when(sk == "human").then(pl.lit("H_und"))
        .when((sk == "automated") & directed).then(pl.lit("N_tgt"))
        .otherwise(pl.lit("drop")).alias("cls"))
    return (ex.filter(pl.col("cls") != "drop")
            .select(pl.col("agent").cast(pl.Int8), "t", "pt_date", pl.col("cls").cast(pl.Categorical),
                    pl.col("msg").cast(pl.UInt32), pl.col("emb").fill_null(-1).cast(pl.Int32))
            .sort("agent", "t"))


def leading_targets(message_ids) -> dict:
    """message_id -> agent code of a nudge's leading @ (H35's rule; infra/README.md Known issue: 29% of nudges name
    other agents too). Text is read in memory only and never written."""
    from common import mention_regexes
    ids = list(message_ids)
    chat = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "pt_date"]).filter(pl.col("message_id").is_in(ids))
    txt = pl.read_parquet(SH / "chat_text.parquet", columns=["message_id", "text"]).filter(pl.col("message_id").is_in(ids))
    chat = chat.join(txt, on="message_id", how="left")
    ros = pl.read_parquet(SH / "roster.parquet").filter(~pl.col("claude_code"))
    pats = mention_regexes([{"id": int(a), "name": n} for a, n in ros.select("agent", "name").iter_rows()])
    span = {int(a): (j, l) for a, j, l in ros.select("agent", "joined", "left").iter_rows()}
    out = {}
    for mid, d, text in chat.select("message_id", "pt_date", "text").iter_rows():
        best, blen = None, 0
        if text and text.startswith("@"):
            for a, pat in pats.items():
                j, l = span[a]
                if not (j <= d and (l is None or d < l)):
                    continue
                mt = pat.match(text, 1)
                if mt and (mt.end() - mt.start()) > blen:
                    best, blen = a, mt.end() - mt.start()
        out[mid] = best
    return out


def load_kick_table_r1b(days: list[str]) -> pl.DataFrame:
    """Round 1b kicks (2026-10-04): as load_kick_table, but a nudge's target is its leading @ only (N_tgt); agents
    named second in a nudge become N_oth (they mark the control/quiet windows as busy but are not episodes). Adds
    t_rc, the receiving call's t_call from the DQ1 context ledger (null when the pair has no receiving call), for the
    receiving-call timing sensitivity."""
    k = load_kick_table(days)
    chat = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id"]).with_row_index("msg")
    k = k.join(chat.with_columns(pl.col("msg").cast(pl.UInt32)), on="msg", how="left")
    nid = k.filter(pl.col("cls").cast(pl.Utf8) == "N_tgt")["message_id"].unique().to_list()
    lt = leading_targets(nid)
    k = k.with_columns(pl.col("message_id").replace_strict(lt, default=None, return_dtype=pl.Int64).alias("lead"))
    k = k.with_columns(pl.when((pl.col("cls").cast(pl.Utf8) == "N_tgt") & (pl.col("agent").cast(pl.Int64) != pl.col("lead").fill_null(-1)))
                       .then(pl.lit("N_oth")).otherwise(pl.col("cls").cast(pl.Utf8)).cast(pl.Categorical).alias("cls"))
    it = (pl.scan_parquet(SH / "context_ledger_items.parquet").filter(pl.col("message_id").is_in(k["message_id"].unique().implode()))
          .select("turn_id", "message_id").collect())
    cw = (pl.scan_parquet(SH / "call_windows.parquet").filter(pl.col("turn_id").is_in(it["turn_id"].implode()))
          .select("turn_id", pl.col("agent").cast(pl.Int8), pl.col("t_call").alias("t_rc"), pl.col("pt_date").alias("rc_date")).collect())
    it = it.join(cw, on="turn_id", how="inner").drop("turn_id")
    k = k.join(it, on=["message_id", "agent"], how="left")
    k = k.with_columns(pl.when(pl.col("rc_date") == pl.col("pt_date")).then(pl.col("t_rc")).otherwise(None).alias("t_rc"))
    return k.select("agent", "t", "pt_date", "cls", "msg", "emb", "t_rc").sort("agent", "t")


def check_against_h16(kicks: pl.DataFrame, days: list[str]) -> dict:
    import h16lib
    K = h16lib.load_kicks(days)
    kicks = kicks.filter(pl.col("pt_date").is_in(days))
    bad = 0
    tot = 0
    for c in ("N_tgt", "H_men", "H_und", "A_men"):
        for a, d in K.items():
            ref = np.sort(d.get(c, np.zeros(0)))
            mine = np.sort((kicks.filter((pl.col("agent") == a) & (pl.col("cls").cast(pl.Utf8) == c))["t"]
                            .dt.epoch("us").to_numpy() / 1e6))
            tot += len(ref)
            if len(ref) != len(mine) or (len(ref) and np.max(np.abs(ref - mine)) > 1e-3):
                bad += 1
    return dict(n_ref=int(tot), mismatched_agent_class=int(bad))


def write_provenance(params: dict):
    prov = {"built_by": "hypotheses/H39-catalysts-vs-fields/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["calendar", "roster", "actions", "events_core", "chat_core", "chat_mentions_clean",
                                   "exposure", "embeddings/chat_index"]},
                       {"source": "derived", "path": "data/processed/H15-semantic-information-scrambles/consolidations.parquet",
                        "built_by": "hypotheses/H15-semantic-information-scrambles/scheme/build.py"}],
            "imports": ["hypotheses/H14-behavior-entropy-production/scheme/build_states.py: build(days)",
                        "hypotheses/H16-metastable-traps-kramers/analysis/h16lib.py: load_kicks (equality check)"],
            "params": params, "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))


def main_r1b():
    """Round 1b kick table only (states and erasures are unchanged: H14's minute grid never used activity_bins)."""
    t0 = time.time()
    days = nonholdout_days()
    k = load_kick_table_r1b(days)
    (OUT / "r1b").mkdir(parents=True, exist_ok=True)
    k.write_parquet(OUT / "r1b" / "kicks_r1b.parquet", compression="zstd")
    n_old = k.filter(pl.col("cls").cast(pl.Utf8).is_in(["N_tgt", "N_oth"])).height
    print("kicks_r1b", k.height, k.group_by("cls").len().sort("cls").rows(), "nudge exposures", n_old,
          "with receiving call", int(k["t_rc"].is_not_null().sum()), f"{time.time() - t0:.0f}s", flush=True)
    prov = {"built_by": "hypotheses/H39-catalysts-vs-fields/scheme/build.py --r1b", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["calendar", "chat_core", "chat_text (leading @ only, in memory)", "chat_mentions_clean",
                                   "exposure", "roster", "embeddings/chat_index", "context_ledger_items", "call_windows"]}],
            "params": {"days": len(days), "nudge_target": "leading @ (H35)", "other_named": "N_oth (busy only)"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "r1b" / "_provenance.json").write_text(json.dumps(prov, indent=1))


def main():
    if "--r1b" in sys.argv:
        return main_r1b()
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    days = nonholdout_days()
    audit = {}
    _, states_min = H14.build(days, audit)
    states_min.write_parquet(OUT / "states_b6.parquet", compression="zstd")
    print(f"states {states_min.height} rows, {time.time() - t0:.0f}s", flush=True)
    kicks = load_kick_table(days)
    kicks.write_parquet(OUT / "kicks.parquet", compression="zstd")
    chk_days = [d for d in days if "2026-04-02" <= d <= "2026-04-24"] + [d for d in days if "2025-09-08" <= d <= "2025-09-19"]
    chk = check_against_h16(kicks, chk_days)
    print("kicks", kicks.height, kicks.group_by("cls").len().sort("cls").rows(), "check vs H16:", chk, flush=True)
    er = pl.read_parquet(ROOT / "data/processed/H15-semantic-information-scrambles/consolidations.parquet",
                         columns=["agent", "t", "pt_date", "goal_no", "kind", "seg_len_pre"])
    er = er.filter(pl.col("pt_date").is_in(days))
    er.write_parquet(OUT / "erasures.parquet", compression="zstd")
    write_provenance(dict(days=len(days), first=days[0], last=days[-1], kick_check_vs_h16=chk,
                          h14_audit_minute_mix=audit.get("minute_mix")))
    print(f"done {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
