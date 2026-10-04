"""H23 scheme step 4: the message table for a goal period (G44 here; confirm_g45.py reuses `build(goal)`).

Rows: every chat message in #best during the goal period (all speakers, for contexts), plus Kimi K2.6's messages
in the base-field periods (non-holdout regime III: #38-#42, #44) and a background sample of all agents' messages
in #38-#42 (log-odds prior, invariance baseline). No text is stored; text is joined from shared chat_text when needed.

Columns: message_id, t, goal_no, room, agent, speaker_kind, set (period | field | background), group
(leader | kimi | village | human | automated), checkpoint (leader only), live (inside the v7-aug window), primary
plan act + act flags, ctx_ids (3 previous messages in the room by other speakers), prev_act (primary act of the most
recent of those), emb_row (row in chat_bge_small.npy).
Vectors: <out>/vectors.npz with z (whitened regime-III, 32-d) for rows and z_ctx (mean of the 3 context messages).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
sys.path.insert(0, str(ROOT / "hypotheses/H23-leader-distillation-copy/analysis"))
from common import holdout_mask, load_whitener, git_commit, REVISION  # noqa: E402
import h23lib as L  # noqa: E402

SH = ROOT / "data/processed/shared"
VILLAGE_BEST44 = {24, 26, 27, 29}


def build(goal: int, out: Path, allow_holdout: bool = False, live_start=None, live_end=None, leader_ids=None):
    leader_ids = leader_ids or L.LEADER_AGENTS
    cc = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "pt_date", "goal_no", "room",
                                                            "speaker_kind", "agent"])
    idx = pl.read_parquet(SH / "embeddings/chat_index.parquet").with_row_index("emb_row")
    cc = cc.join(idx, on="message_id", how="left").with_columns(pl.col("speaker_kind").cast(pl.String))
    period = cc.filter((pl.col("goal_no") == goal) & (pl.col("room") == L.BEST_ROOM)).with_columns(
        pl.lit("period").alias("set"))
    field = cc.filter((pl.col("agent") == L.KIMI) & pl.col("goal_no").is_in(L.BASE_FIELD_GOALS)
                      & (pl.col("speaker_kind") == "agent")).with_columns(pl.lit("field").alias("set"))
    if live_start is not None:
        field = field.filter(~((pl.col("t") >= live_start) & (pl.col("t") < live_end)))
    bg = cc.filter(pl.col("goal_no").is_in([38, 39, 40, 41, 42]) & (pl.col("speaker_kind") == "agent")
                   & ~pl.col("agent").is_in(list(leader_ids)))
    bg = bg.sample(n=min(12000, bg.height), seed=20261003, shuffle=True)
    bg = bg.with_columns(pl.lit("background").alias("set"))
    D = pl.concat([period, field, bg]).unique(["message_id", "set"], keep="first").sort("t")
    # holdout guard
    held = holdout_mask(D["pt_date"].to_list(), D["goal_no"].to_list())
    if any(held) and not allow_holdout:
        raise SystemExit(f"refusing: {sum(held)} rows fall in the locked holdout")
    text = pl.read_parquet(SH / "chat_text.parquet", columns=["message_id", "text"])
    D = D.join(text, on="message_id", how="left")

    def grp(kind, a):
        if kind == "agent" and a in leader_ids:
            return "leader"
        if kind == "agent" and a == L.KIMI:
            return "kimi"
        if kind == "agent":
            return "village"
        return kind
    D = D.with_columns(pl.struct(["speaker_kind", "agent"]).map_elements(
        lambda s: grp(s["speaker_kind"], s["agent"]), return_dtype=pl.String).alias("group"))
    D = D.with_columns(
        pl.struct(["group", "t"]).map_elements(lambda s: L.checkpoint_of(s["t"]) if s["group"] == "leader" else None,
                                               return_dtype=pl.String).alias("checkpoint"))
    if live_start is not None:
        D = D.with_columns(((pl.col("t") >= live_start) & (pl.col("t") < live_end) & (pl.col("set") == "period"))
                           .alias("live"))
    else:
        D = D.with_columns((pl.col("set") == "period").alias("live"))
    acts = [L.plan_acts(s or "") for s in D["text"].to_list()]
    D = D.with_columns(pl.Series("primary", [a["primary"] for a in acts]),
                       *[pl.Series(f"act_{k}", [a[k] for a in acts]) for k in L.ACTS[:-1]],
                       pl.Series("n_tokens", [len(L.tokens(s or "")) for s in D["text"].to_list()]))
    # contexts inside the room (period set only): 3 previous messages by other speakers
    per = D.filter(pl.col("set") == "period").sort("t")
    rows = per.select("message_id", "agent", "speaker_kind", "human", "primary").to_dicts() if "human" in per.columns \
        else per.select("message_id", "agent", "speaker_kind", "primary").to_dicts()
    ctx_ids, prev_act = {}, {}
    for i, r in enumerate(rows):
        me = (r["speaker_kind"], r["agent"])
        prev = []
        j = i - 1
        while j >= 0 and len(prev) < 3:
            o = rows[j]
            if not (o["speaker_kind"] == "agent" and (o["speaker_kind"], o["agent"]) == me):
                prev.append(o)
            j -= 1
        ctx_ids[r["message_id"]] = [o["message_id"] for o in prev]
        prev_act[r["message_id"]] = prev[0]["primary"] if prev else None
    D = D.with_columns(
        pl.col("message_id").map_elements(lambda m: ctx_ids.get(m), return_dtype=pl.List(pl.String)).alias("ctx_ids"),
        pl.col("message_id").map_elements(lambda m: prev_act.get(m), return_dtype=pl.String).alias("prev_act"))
    # vectors
    E = np.load(SH / "embeddings/chat_bge_small.npy", mmap_mode="r")
    W = load_whitener("III", 32)
    er = D["emb_row"].to_numpy()
    Z = W(np.asarray(E[er], dtype=np.float32))
    pos = {m: i for i, m in enumerate(D["message_id"].to_list())}
    Zc = np.full_like(Z, np.nan)
    rowmap = dict(zip(D["message_id"].to_list(), er))
    for i, m in enumerate(D["message_id"].to_list()):
        ids = ctx_ids.get(m) or []
        if ids:
            raw = np.asarray(E[[rowmap[x] for x in ids]], dtype=np.float32).mean(0, keepdims=True)
            Zc[i] = W(raw)[0]
    out.mkdir(parents=True, exist_ok=True)
    core = D.drop("text")
    core.write_parquet(out / "messages.parquet", compression="zstd")
    np.savez_compressed(out / "vectors.npz", z=Z.astype(np.float32), z_ctx=Zc.astype(np.float32),
                        message_id=np.array(D["message_id"].to_list()), set=np.array(D["set"].to_list()))
    prov = {"built_by": "hypotheses/H23-leader-distillation-copy/scheme/build_messages.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["chat_core", "chat_text", "embeddings/chat_bge_small", "whitening_III",
                                   "computer_use_turns", "computer_use_sessions"]}],
            "params": {"goal": goal, "room": "best", "base_field_goals": L.BASE_FIELD_GOALS, "context_k": 3,
                       "whitening": "III, 32-d", "background_n": 12000, "seed": 20261003},
            "built_at": __import__("datetime").datetime.now(L.UTC).isoformat()}
    (out / "_provenance.json").write_text(json.dumps(prov, indent=1))
    return core


if __name__ == "__main__":
    core = build(44, L.OUT / "G44", live_start=L.LIVE_START, live_end=L.LIVE_END)
    print(core.group_by("set", "group", "live").len().sort("set", "group"))
    print(core.filter(pl.col("group") == "leader").group_by("checkpoint").len())
