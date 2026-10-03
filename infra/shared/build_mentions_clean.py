"""Corrected @-mentions, recomputed from chat text with the fixed name regexes.

chat_core.mentions (scan_tables.py before 2026-10-03) has a bug: `o1`'s alias set was empty, and the empty
regex matched almost every message (175k of 183k carry a spurious `o1`). This sidecar recomputes mentions
with the fixed `common.mention_regexes` (o1 and o3 matched case-sensitively; agents with no alias skipped),
without rewriting chat_core under analyses that are running. Rebuild chat_core with scan_tables.py later.

Output: data/processed/shared/chat_mentions_clean.parquet, in chat_core row order:
  message_id, mentions_clean (all roster agents, minus the speaker), mentions_roster (also restricted to agents
  on the roster that day: joined <= pt_date < left)
Usage: uv run python infra/shared/build_mentions_clean.py
"""
from __future__ import annotations

import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUT, mention_regexes, rows, write_provenance  # noqa: E402
from scan_tables import agent_codes  # noqa: E402

_PATS = None


def _init():
    global _PATS
    A = agent_codes()
    _PATS = {A[k]: v for k, v in mention_regexes(list(rows("agents"))).items() if k in A}


def _chunk(items):
    return [[c for c, p in _PATS.items() if c != spk and p.search(txt or "")] for spk, txt in items]


def main():
    core = pl.read_parquet(OUT / "chat_core.parquet", columns=["message_id", "pt_date", "agent"])
    text = pl.read_parquet(OUT / "chat_text.parquet", columns=["message_id", "text"])
    df = core.join(text, on="message_id", how="left", maintain_order="left")
    items = list(zip(df["agent"].to_list(), df["text"].to_list()))
    chunks = [items[i:i + 5000] for i in range(0, len(items), 5000)]
    with ProcessPoolExecutor(4, initializer=_init) as ex:
        ments = [m for part in ex.map(_chunk, chunks) for m in part]
    roster = {r["agent"]: (r["joined"], r["left"]) for r in pl.read_parquet(OUT / "roster.parquet").iter_rows(named=True)}
    on = [[c for c in m if (roster.get(c, (None, None))[0] or "") <= d and (roster.get(c, (None, None))[1] is None or d < roster[c][1])]
          for m, d in zip(ments, df["pt_date"].to_list())]
    out = pl.DataFrame({"message_id": df["message_id"], "mentions_clean": ments, "mentions_roster": on},
                       schema_overrides={"mentions_clean": pl.List(pl.Int8), "mentions_roster": pl.List(pl.Int8)})
    out.write_parquet(OUT / "chat_mentions_clean.parquet", compression="zstd")
    old = core.join(pl.read_parquet(OUT / "chat_core.parquet", columns=["message_id", "mentions"]), on="message_id")
    n_old = int(old["mentions"].list.len().sum()); n_new = int(out["mentions_clean"].list.len().sum())
    print(f"{out.height} messages; mentions old {n_old:,} → clean {n_new:,} (roster-restricted {int(out['mentions_roster'].list.len().sum()):,})")
    write_provenance("build_mentions_clean", ["chat_core", "chat_text", "agents", "roster"],
                     {"fix": "o1 empty-alias regex; o1/o3 case-sensitive", "roster_rule": "joined <= pt_date < left"})


if __name__ == "__main__":
    main()
