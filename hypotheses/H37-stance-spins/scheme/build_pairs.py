"""H37 scheme, step 1: reply pairs (A -> B) per goal period, codes only (no text).

A reply pair is (A, B): B is an agent chat message, A an earlier agent chat message by a different agent in the same
room. Two constructions (card, "Data scheme"):
  mention   B names agent i (chat_mentions_clean.mentions_roster, i != speaker(B)); A = i's latest message in B's room
            with 0 < t_B - t_A <= MENTION_WIN (30 min). Interaction (addressed) in DEFINITIONS.md, restricted to a
            time window: "interaction (addressed reply, 30 min)".
  adjacent  A = the latest message by any other agent in B's room with 0 < t_B - t_A <= ADJ_WIN (5 min).
            Interaction (reply) in DEFINITIONS.md with dt = 5 min: "interaction (adjacent reply, 5 min)".
A pair found by both constructions is kept once with kind = "both".

Also stored per pair: lag, topic cosine of A and B (bge-small, per-regime whitened n = 32, from the shared
embeddings), and whether B also mentions other agents. Holdout days are refused (holdout_mask).

Output: data/processed/H37-stance-spins/pairs/G<NN>.parquet + _provenance.json.
Usage: uv run python hypotheses/H37-stance-spins/scheme/build_pairs.py [--goals 12 26 51 40]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "2")
os.environ.setdefault("OMP_NUM_THREADS", "2")

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import OUT as SHARED, REVISION, git_commit, holdout_mask, load_whitener  # noqa: E402

DATA = ROOT / "data/processed/H37-stance-spins"
MENTION_WIN = 30 * 60
ADJ_WIN = 5 * 60


def load_chat(goals):
    c = pl.read_parquet(SHARED / "chat_core.parquet").with_row_index("row")
    m = pl.read_parquet(SHARED / "chat_mentions_clean.parquet", columns=["message_id", "mentions_roster"])
    assert c.height == m.height and (c["message_id"] == m["message_id"]).all()
    c = c.with_columns(m["mentions_roster"])
    c = c.filter(pl.col("goal_no").is_in(goals))
    c = c.with_columns(pl.Series("hold", holdout_mask(c["pt_date"].to_list(), c["goal_no"].to_list())))
    return c


def topic_cos(msg_a, msg_b, regime):
    idx = pl.read_parquet(SHARED / "embeddings/chat_index.parquet").with_row_index("erow")
    X = np.load(SHARED / "embeddings/chat_bge_small.npy", mmap_mode="r")
    pos = dict(zip(idx["message_id"].to_list(), idx["erow"].to_list()))
    W = load_whitener(regime, 32)
    ia = np.array([pos.get(x, -1) for x in msg_a]); ib = np.array([pos.get(x, -1) for x in msg_b])
    ok = (ia >= 0) & (ib >= 0)
    out = np.full(len(ia), np.nan, np.float32)
    if ok.any():
        A = W(np.asarray(X[ia[ok]], np.float32)); B = W(np.asarray(X[ib[ok]], np.float32))
        A /= np.linalg.norm(A, axis=1, keepdims=True); B /= np.linalg.norm(B, axis=1, keepdims=True)
        out[ok] = (A * B).sum(1)
    return out


def build_goal(c, g):
    x = c.filter((pl.col("goal_no") == g) & (pl.col("speaker_kind") == "agent")).sort("t")
    n_hold = int(x["hold"].sum())
    x = x.filter(~pl.col("hold"))
    assert not x["hold"].any()
    recs = {}
    for room, grp in x.group_by("room", maintain_order=True):
        rows = grp.select("message_id", "t", "agent", "mentions_roster", "pt_date").to_dicts()
        last_by_agent: dict[int, dict] = {}
        prev = []  # recent messages (any agent) for adjacency
        for r in rows:
            tb, sb = r["t"], r["agent"]
            ments = [a for a in (r["mentions_roster"] or []) if a != sb]
            for i in sorted(set(ments)):
                a = last_by_agent.get(i)
                if a is not None and 0 < (tb - a["t"]).total_seconds() <= MENTION_WIN:
                    key = (a["message_id"], r["message_id"])
                    recs[key] = dict(msg_a=a["message_id"], msg_b=r["message_id"], t_a=a["t"], t_b=tb, agent_a=i, agent_b=sb,
                                     room=room[0], pt_date=r["pt_date"], kind="mention", n_mentions_b=len(set(ments)))
            for a in reversed(prev):
                if a["agent"] != sb:
                    if 0 < (tb - a["t"]).total_seconds() <= ADJ_WIN:
                        key = (a["message_id"], r["message_id"])
                        if key in recs:
                            recs[key]["kind"] = "both"
                        else:
                            recs[key] = dict(msg_a=a["message_id"], msg_b=r["message_id"], t_a=a["t"], t_b=tb, agent_a=a["agent"],
                                             agent_b=sb, room=room[0], pt_date=r["pt_date"], kind="adjacent", n_mentions_b=len(set(ments)))
                    break
            last_by_agent[sb] = r
            prev.append(r)
            if len(prev) > 50:
                prev = prev[-50:]
    df = pl.DataFrame(list(recs.values()), schema_overrides={"agent_a": pl.Int8, "agent_b": pl.Int8, "room": pl.Int8,
                                                             "n_mentions_b": pl.Int16})
    df = df.with_columns(((pl.col("t_b") - pl.col("t_a")).dt.total_seconds()).cast(pl.Float32).alias("lag_s"),
                         pl.lit(g, pl.Int8).alias("goal_no"))
    regime = x["regime"].cast(pl.String).mode()[0]
    df = df.with_columns(pl.Series("topic_cos", topic_cos(df["msg_a"].to_list(), df["msg_b"].to_list(), regime)))
    df = df.sort("t_b").with_row_index("pair_id")
    return df, dict(goal=g, regime=regime, n_agent_msgs=x.height, n_holdout_msgs_refused=n_hold, n_pairs=df.height,
                    kinds=dict(zip(*[df.group_by("kind").len().sort("kind")[k].to_list() for k in ("kind", "len")])))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--goals", type=int, nargs="+", default=[12, 26, 51, 40])
    args = ap.parse_args()
    held = set(json.loads((ROOT / "hypotheses/holdout.json").read_text())["goal_periods_held_out"])
    bad = [g for g in args.goals if g in held]
    if bad:
        sys.exit(f"refusing held-out goal periods {bad} (exploration only; see hypotheses/holdout.md)")
    out = DATA / "pairs"
    out.mkdir(parents=True, exist_ok=True)
    c = load_chat(args.goals)
    meta = {}
    for g in args.goals:
        df, m = build_goal(c, g)
        df.write_parquet(out / f"G{g:02d}.parquet", compression="zstd")
        meta[f"G{g:02d}"] = m
        print(m, flush=True)
    prov_path = DATA / "_provenance.json"
    prov = json.loads(prov_path.read_text()) if prov_path.exists() else {}
    prov["pairs"] = {"built_by": "hypotheses/H37-stance-spins/scheme/build_pairs.py", "git_commit": git_commit(),
                     "inputs": [{"source": "ai-village", "revision": REVISION,
                                 "tables": ["shared/chat_core", "shared/chat_mentions_clean", "shared/embeddings/chat_bge_small",
                                            "shared/embeddings/whitening_*"]}],
                     "params": {"mention_win_s": MENTION_WIN, "adjacent_win_s": ADJ_WIN, "goals": args.goals, "meta": meta},
                     "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    prov_path.write_text(json.dumps(prov, indent=1, default=str))


if __name__ == "__main__":
    main()
