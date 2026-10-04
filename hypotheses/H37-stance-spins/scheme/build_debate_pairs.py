"""H37 scheme, Amendment 1 (2026-10-04, before any outcome): debater-adjacent reply pairs for #12.

Reading the blind validation sample showed that in #12 the adjacent reply of a speech is usually the judge's
"floor is yours" call, not the previous speech. So for each message B inside a debate window [pre_start, post_end)
written by one of that debate's debaters, A = the latest message by a *different debater of the same debate*
(judge and bench excluded) within the window and at most 10 min before B. The rule does not look at teams.

Pairs that already exist in pairs/G12.parquet get flagged there via a join at analysis time; new ones are written to
pairs/G12_debater.parquet with pair_id offset 100000 (so G12 pair ids stay stable). Codes only.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "2")
import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "infra/shared"))
from build_pairs import load_chat, topic_cos, DATA  # noqa: E402
from select_samples import debate_windows  # noqa: E402
from common import REVISION, git_commit  # noqa: E402

OFFSET = 100000
WIN = 10 * 60


def debater_adjacent():
    """All debater-adjacent (A, B) pairs of #12 under the Amendment-1 rule, as dicts (codes only)."""
    names = dict(pl.read_parquet(ROOT / "data/processed/shared/roster.parquet", columns=["name", "agent"]).iter_rows())
    c = load_chat([12]).filter((pl.col("speaker_kind") == "agent") & ~pl.col("hold")).sort("t")
    rows = c.select("message_id", "t", "agent", "pt_date", "room").to_dicts()
    out, n_b = [], 0
    for w in debate_windows():
        deb = {names[x] for x in w["gov"] + w["opp"]}
        inw = [r for r in rows if w["pre_start"] <= r["t"] < w["post_end"]]
        for k, b in enumerate(inw):
            if b["agent"] not in deb:
                continue
            n_b += 1
            for a in reversed(inw[:k]):
                if a["agent"] in deb and a["agent"] != b["agent"]:
                    if 0 < (b["t"] - a["t"]).total_seconds() <= WIN:
                        out.append(dict(msg_a=a["message_id"], msg_b=b["message_id"], t_a=a["t"], t_b=b["t"], agent_a=a["agent"],
                                        agent_b=b["agent"], room=b["room"], pt_date=b["pt_date"], kind="debater", n_mentions_b=-1))
                    break
    return out, n_b


def main():
    old = pl.read_parquet(DATA / "pairs/G12.parquet")
    have = set(zip(old["msg_a"].to_list(), old["msg_b"].to_list()))
    allp, n_b = debater_adjacent()
    recs = [r for r in allp if (r["msg_a"], r["msg_b"]) not in have]
    n_exist = len(allp) - len(recs)
    df = pl.DataFrame(recs, schema_overrides={"agent_a": pl.Int8, "agent_b": pl.Int8, "room": pl.Int8, "n_mentions_b": pl.Int16})
    df = df.with_columns(((pl.col("t_b") - pl.col("t_a")).dt.total_seconds()).cast(pl.Float32).alias("lag_s"), pl.lit(12, pl.Int8).alias("goal_no"))
    df = df.with_columns(pl.Series("topic_cos", topic_cos(df["msg_a"].to_list(), df["msg_b"].to_list(), "I")))
    df = df.sort("t_b").with_row_index("pair_id", offset=OFFSET)
    df = df.select(old.columns)
    df.write_parquet(DATA / "pairs/G12_debater.parquet", compression="zstd")
    print(f"debater B messages {n_b}; debater-adjacent pairs already in G12: {n_exist}; new: {df.height}")
    prov_path = DATA / "_provenance.json"
    prov = json.loads(prov_path.read_text())
    prov["pairs_debater"] = {"built_by": "hypotheses/H37-stance-spins/scheme/build_debate_pairs.py", "git_commit": git_commit(),
                             "inputs": [{"source": "ai-village", "revision": REVISION, "tables": ["shared/chat_core", "H21 g12_debates.json"]}],
                             "params": {"win_s": WIN, "offset": OFFSET, "n_new": df.height, "n_existing": n_exist},
                             "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    prov_path.write_text(json.dumps(prov, indent=1, default=str))


if __name__ == "__main__":
    main()
