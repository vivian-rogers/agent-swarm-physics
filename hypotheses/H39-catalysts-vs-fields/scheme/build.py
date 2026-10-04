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


def main():
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
