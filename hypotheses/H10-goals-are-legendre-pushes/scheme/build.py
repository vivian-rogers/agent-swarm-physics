"""H10 scheme: whitened statement coordinates and goal-field vectors. NON-HOLDOUT ONLY; goal period #23 excluded.

Statements = each agent's own chat messages and self-written intentions (shared `embeddings/statements.parquet`,
bge-small-en-v1.5). The Claude Code agent is excluded (separate scaffolding). #23 is not held out in holdout.json
but is kept untouched in round 1 so the confirmatory #22 -> #23 pair stays blind on both sides.

Outputs (data/processed/H10-goals-are-legendre-pushes/):
  statements.parquet   row, kind, agent, t, pt_date, room, goal_no, regime, win30   (no text)
  stmt_w64.npy         (n, 64) float16 whitened coordinates in the statement's regime basis (common.load_whitener);
                       the first 32 columns are the primary n = 32 basis (PCA whitening is nested). NOT normalized:
                       analyses unit-normalize the first n columns.
  goals.parquet        goal_no, first_day, regime, n_kick_msgs, kick_chars, kick_rooms   (lengths only, no text)
  goal_vecs.npz        goal_no, goal_raw (G, 384), kick_raw (G, 384; NaN when no kickoff) - raw bge embeddings;
                       whiten downstream with load_whitener(regime)
  _provenance.json

Goal and kickoff texts (held in memory only, never stored): the village_goals text, and the kickoff = human
messages >= 250 chars within [window start - 10 min, + 45 min] of the period's first active day (fallback: that
day's longest human message >= 250 chars), all rooms combined, sentences about the previous goal stripped. This is
the rule of H01's scheme (hypotheses/H01-emergent-superagents-exist/scheme/build.py: goal_texts); duplicated here
because infra/ is outside this hypothesis's edit scope - proposed move: infra/shared/goal_fields.py.

Usage:  UV_OFFLINE=1 HF_HUB_OFFLINE=1 uv run --with sentence-transformers python \
            hypotheses/H10-goals-are-legendre-pushes/scheme/build.py
"""
from __future__ import annotations

import datetime as dt
import json
import re
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit, holdout_mask, load_goals, load_holdout, load_whitener  # noqa: E402

SH = ROOT / "data/processed/shared"
EMB = SH / "embeddings"
OUT = ROOT / "data/processed/H10-goals-are-legendre-pushes"
MODEL = "BAAI/bge-small-en-v1.5"
EXCLUDED_GOALS = {0, 23}
D_MAX = 64

BOILER = re.compile(r"wrap(s|ped)?\s+up|to a close|your memory|previous goal|last week|last two weeks|that goal is", re.I)


def strip_boilerplate(text: str) -> str:
    sents = re.split(r"(?<=[.!?])\s+|\n+", text)
    return " ".join(s for s in sents if s.strip() and not BOILER.search(s)).strip()


def chunks(text: str, n: int = 700) -> list[str]:
    sents = re.split(r"(?<=[.!?])\s+", text)
    out, cur = [], ""
    for s in sents:
        if len(cur) + len(s) > n and cur:
            out.append(cur)
            cur = s
        else:
            cur = (cur + " " + s).strip()
    if cur:
        out.append(cur)
    return [c[:2000] for c in out if len(c) > 20]


def held_goals() -> set[int]:
    return set(load_holdout()["goal_periods_held_out"])


def load_statements() -> pl.DataFrame:
    st = pl.read_parquet(EMB / "statements.parquet").with_row_index("emb_row")
    roster = pl.read_parquet(SH / "roster.parquet")
    cc = roster.filter(pl.col("claude_code"))["agent"].to_list()
    st = st.filter(~pl.col("holdout") & pl.col("goal_no").is_not_null() & ~pl.col("goal_no").is_in(list(EXCLUDED_GOALS))
                   & ~pl.col("agent").is_in(cc))
    hm = np.array(holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list()))
    st = st.filter(pl.Series(~hm))
    assert not set(st["goal_no"].unique().to_list()) & held_goals(), "holdout goal leaked"
    return st


def whitened(st: pl.DataFrame) -> np.ndarray:
    Ec = np.load(EMB / "chat_bge_small.npy", mmap_mode="r")
    Ei = np.load(EMB / "intentions_bge_small.npy", mmap_mode="r")
    kind = st["kind"].to_numpy()
    src = st["src_row"].to_numpy()
    reg = st["regime"].to_numpy()
    Z = np.zeros((st.height, D_MAX), dtype=np.float16)
    for r in sorted(set(reg)):
        W = load_whitener(r, D_MAX)
        for k, E in (("chat", Ec), ("intent", Ei)):
            sel = np.flatnonzero((reg == r) & (kind == k))
            if len(sel):
                Z[sel] = W(np.asarray(E[np.sort(src[sel])], dtype=np.float32)[np.argsort(np.argsort(src[sel]))]).astype(np.float16)
    return Z


def goal_texts(goal_nos: list[int]) -> tuple[list[dict], list[str], list[list[str]]]:
    goals = {g["goal_no"]: g for g in load_goals()}
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "win_start", "goal_no", "regime", "holdout"])
    cc = (pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "pt_date", "room", "speaker_kind", "length"])
          .filter(pl.col("speaker_kind") == "human"))
    ct = pl.read_parquet(SH / "chat_text.parquet", columns=["message_id", "text"])
    meta, gtext, ktext = [], [], []
    for g in goal_nos:
        c = cal.filter((pl.col("goal_no") == g) & ~pl.col("holdout")).sort("pt_date")
        if c.height == 0:
            continue
        d0, ws, reg = c["pt_date"][0], c["win_start"][0], str(c["regime"][0])
        k = cc.filter((pl.col("pt_date") == d0) & (pl.col("length") >= 250) & (pl.col("t") >= ws - dt.timedelta(minutes=10))
                      & (pl.col("t") <= ws + dt.timedelta(minutes=45)))
        if k.height == 0:
            k = cc.filter((pl.col("pt_date") == d0) & (pl.col("length") >= 250)).sort("length", descending=True).head(1)
        k = k.join(ct, on="message_id").sort("t")
        body = " ".join(strip_boilerplate(x) for x in k["text"].to_list())
        meta.append({"goal_no": g, "first_day": d0, "regime": reg, "n_kick_msgs": k.height,
                     "kick_chars": len(body), "kick_rooms": k["room"].n_unique() if k.height else 0})
        gtext.append(goals[g]["goal"])
        ktext.append(chunks(body))
    return meta, gtext, ktext


def embed(gtext: list[str], ktext: list[list[str]]) -> tuple[np.ndarray, np.ndarray]:
    import torch
    from sentence_transformers import SentenceTransformer
    torch.set_num_threads(2)
    dev = "mps" if torch.backends.mps.is_available() else "cpu"
    m = SentenceTransformer(MODEL, device=dev)
    m.max_seq_length = 256  # as in infra/shared/build_embeddings.py
    G = np.full((len(gtext), 384), np.nan, dtype=np.float32)
    K = np.full((len(gtext), 384), np.nan, dtype=np.float32)
    for i, (gt, kt) in enumerate(zip(gtext, ktext)):
        G[i] = m.encode(chunks(gt) or [gt], normalize_embeddings=True, convert_to_numpy=True).mean(0)
        if kt:
            K[i] = m.encode(kt, batch_size=16, normalize_embeddings=True, convert_to_numpy=True).mean(0)
    return G, K


def main():
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    st = load_statements()
    print(f"statements {st.height}  goals {sorted(st['goal_no'].unique().to_list())}", flush=True)
    Z = whitened(st)
    st.select(pl.int_range(pl.len(), dtype=pl.UInt32).alias("row"), "kind", "agent", "t", "pt_date", "room", "goal_no",
              "regime", "win30").write_parquet(OUT / "statements.parquet", compression="zstd")
    np.save(OUT / "stmt_w64.npy", Z)
    print(f"whitened {Z.shape} {time.time() - t0:.0f}s", flush=True)

    goal_nos = sorted(set(st["goal_no"].unique().to_list()) - EXCLUDED_GOALS)
    meta, gtext, ktext = goal_texts(goal_nos)
    G, K = embed(gtext, ktext)
    del gtext, ktext
    pl.DataFrame(meta).write_parquet(OUT / "goals.parquet")
    np.savez(OUT / "goal_vecs.npz", goal_no=np.array([m["goal_no"] for m in meta]), goal_raw=G, kick_raw=K)
    print(f"goal vectors {len(meta)}; no kickoff for {[m['goal_no'] for m in meta if m['n_kick_msgs'] == 0]}", flush=True)

    prov = {"built_by": "hypotheses/H10-goals-are-legendre-pushes/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["shared/embeddings/statements", "shared/embeddings/chat_bge_small",
                                   "shared/embeddings/intentions_bge_small", "shared/embeddings/whitening_*",
                                   "shared/calendar", "shared/roster", "shared/chat_core",
                                   "shared/chat_text (kickoff texts, in memory only)", "raw village_goals"]}],
            "params": {"model": MODEL, "max_seq_length": 256, "whiten_dim_stored": D_MAX, "primary_dim": 32,
                       "excluded_goals": sorted(EXCLUDED_GOALS), "holdout": "excluded (holdout.json + holdout_mask)",
                       "claude_code_agent": "excluded",
                       "kickoff_rule": "human msgs >= 250 chars within [win_start-10m, win_start+45m] of the goal's first "
                                       "non-holdout active day, all rooms; previous-goal boilerplate stripped; chunks <= 700 "
                                       "chars, mean of unit chunk embeddings"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print(f"done {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
