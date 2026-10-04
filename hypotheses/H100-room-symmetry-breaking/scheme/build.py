"""H100 scheme: agent-day content vectors with the agent's room of the day, plus room field directions.

Output: data/processed/H100-room-symmetry-breaking/
  agent_days.parquet          row, gid, agent, pt_date, goal_no, unit, regime, n_stat, room (room of the day: majority of
                              the agent's statements that day), room_share, n_rooms
  x_<variant>_<model>.npy     float16 (rows aligned with agent_days), variant in {style_resid, white32},
                              model in {bge_small, gte_modernbert}; plain means of unit 32-d regime-whitened statement
                              vectors (DQ5), not re-normalized
  fields.parquet + fields_<model>.npy   per (goal_no, room, kind): whitened, unit-normalized room kickoff vectors
                              (kind kickoff_room) and the mean of whitened unit operator-message vectors per room
                              (kind operator; human speakers only; >= 3 messages)
Non-holdout rows only (holdout_mask); the Claude Code agent is excluded. No text is read.

Usage: uv run python hypotheses/H100-room-symmetry-breaking/scheme/build.py
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit, holdout_mask  # noqa: E402
from embed_models import load_whitener  # noqa: E402

SH = ROOT / "data/processed/shared"
ED = SH / "embeddings"
OUT = ROOT / "data/processed/H100-room-symmetry-breaking"
GOALS = list(range(33, 52))
MODELS = ["bge_small", "gte_modernbert"]
SUFFIX = {"bge_small": "", "gte_modernbert": "_gte_modernbert"}
CHAT = {"bge_small": "chat_bge_small.npy", "gte_modernbert": "chat_gte_modernbert.npy"}
FAR = dt.datetime(2100, 1, 1, tzinfo=dt.timezone.utc)


def rooms_timeline() -> pl.DataFrame:
    """rooms_timeline with null t_end filled by +inf (infra Known issues: open rooms have a null t_end)."""
    return (pl.read_parquet(SH / "rooms_timeline.parquet")
            .with_columns(pl.col("t_end").fill_null(pl.lit(FAR).cast(pl.Datetime("us", "UTC"))))
            .sort("agent", "t_start"))


def statement_rooms(st: pl.DataFrame) -> pl.DataFrame:
    """Room of every statement: chat = message room; intentions = as-of rooms_timeline (t_start <= t < t_end)."""
    rt = rooms_timeline().select("agent", pl.col("t_start").alias("t"), pl.col("room").alias("room_rt"),
                                 pl.col("t_end"))
    s = st.with_row_index("srow").sort("agent", "t")
    j = s.join_asof(rt, on="t", by="agent", strategy="backward")
    j = j.with_columns(pl.when(pl.col("t") < pl.col("t_end")).then(pl.col("room_rt")).otherwise(None).alias("room_rt"))
    j = j.with_columns(pl.when(pl.col("kind") == "chat").then(pl.col("room")).otherwise(pl.col("room_rt"))
                       .alias("room_at"))
    return j.sort("srow").drop("srow", "room_rt", "t_end")


def main(goals=None, allow_holdout_goals=(), write=True):
    """write=False returns (table, {(variant, model): X}, fields table, {model: F}) in memory. allow_holdout_goals is
    used only by analysis/confirm.py (guarded); exploration always runs with the default ()."""
    GOALS_ = goals or GOALS
    allow = set(allow_holdout_goals)
    if write:
        assert not allow, "held-out rows are never written to disk"
        OUT.mkdir(parents=True, exist_ok=True)
    roster = pl.read_parquet(SH / "roster.parquet")
    cc_agents = roster.filter(pl.col("claude_code"))["agent"].to_list()
    units = pl.read_parquet(SH / "period_units.parquet").select("unit_id", "goal_no", "days").explode("days") \
        .rename({"days": "pt_date"})

    ad = pl.read_parquet(ED / "agent_day.parquet").with_row_index("src")
    ad = ad.filter(pl.col("goal_no").is_in(GOALS_) & ~pl.col("agent").is_in(cc_agents))
    hm = np.array(holdout_mask(ad["pt_date"].to_list(), ad["goal_no"].to_list()))
    ok = ~hm | ad["goal_no"].is_in(list(allow)).to_numpy()
    ad = ad.filter(pl.Series(ok))
    if not allow:
        assert not any(holdout_mask(ad["pt_date"].to_list(), ad["goal_no"].to_list()))

    st = pl.read_parquet(ED / "statements.parquet", columns=["kind", "agent", "t", "pt_date", "room", "goal_no",
                                                             "holdout"])
    st = st.filter(pl.col("goal_no").is_in(GOALS_) & ~pl.col("agent").is_in(cc_agents))
    st = st.filter(~pl.col("holdout") | pl.col("goal_no").is_in(list(allow)))
    st = statement_rooms(st)
    rd = (st.drop_nulls("room_at").group_by("agent", "pt_date", "room_at").len()
          .sort(["agent", "pt_date", "len", "room_at"], descending=[False, False, True, False]))
    room_day = rd.group_by("agent", "pt_date", maintain_order=True).agg(
        pl.col("room_at").first().alias("room"), (pl.col("len").first() / pl.col("len").sum()).alias("room_share"),
        pl.len().alias("n_rooms"), pl.col("len").sum().alias("n_stat_room"))
    tab = (ad.join(room_day, on=["agent", "pt_date"], how="left")
           .join(units, on=["goal_no", "pt_date"], how="left").rename({"unit_id": "unit"})
           .with_columns((pl.col("n_chat") + pl.col("n_intent")).alias("n_stat"))
           .sort("pt_date", "agent").with_row_index("row"))
    tab_out = tab.select("row", "gid", "agent", "pt_date", "goal_no", "unit", "regime", "n_stat", "n_chat", "room",
                         "room_share", "n_rooms")
    if write:
        tab_out.write_parquet(OUT / "agent_days.parquet", compression="zstd")
    src = tab["src"].to_numpy()
    Xs = {}
    for model in MODELS:
        for variant in ("style_resid", "white32"):
            a = np.load(ED / f"agent_day_{variant}_{model}.npy", mmap_mode="r")
            Xs[(variant, model)] = np.asarray(a[src], dtype=np.float16)
            if write:
                np.save(OUT / f"x_{variant}_{model}.npy", Xs[(variant, model)])

    # ---- field directions
    g = pl.read_parquet(ED / "goals.parquet").with_columns(pl.col("kind").cast(pl.String))
    kr = g.filter((pl.col("kind") == "kickoff_room") & pl.col("goal_no").is_in(GOALS_)
                  & (~pl.col("holdout") | pl.col("goal_no").is_in(list(allow))))
    cc = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "pt_date", "goal_no", "room",
                                                             "speaker_kind"])
    ci = pl.read_parquet(ED / "chat_index.parquet").with_row_index("crow")
    hum = (cc.filter((pl.col("speaker_kind") == "human") & pl.col("goal_no").is_in(GOALS_))
           .join(ci, on="message_id", how="inner"))
    hm = np.array(holdout_mask(hum["pt_date"].to_list(), hum["goal_no"].to_list())) if hum.height else np.array([])
    hum = hum.filter(pl.Series(~hm | hum["goal_no"].is_in(list(allow)).to_numpy()))
    hg = hum.group_by("goal_no", "room").agg(pl.col("crow"), pl.len().alias("n")).filter(pl.col("n") >= 3) \
        .sort("goal_no", "room")
    rows, vecs = [], {m: [] for m in MODELS}
    reg = lambda gno: "II" if gno <= 35 else "III"  # noqa: E731  (#36a is regime II; fields of #36 use regime III)
    for m in MODELS:
        gv = np.load(ED / f"goal_vectors{SUFFIX[m]}.npy").astype(np.float32)
        cv = np.load(ED / CHAT[m], mmap_mode="r")
        for r in kr.sort("goal_no", "room").to_dicts():
            W = load_whitener(reg(r["goal_no"]), 32, m)
            v = W(gv[r["gid"]][None])[0]
            vecs[m].append(v / np.linalg.norm(v))
            if m == MODELS[0]:
                rows.append({"goal_no": r["goal_no"], "room": r["room"], "kind": "kickoff_room", "n": r["n_msgs"]})
        for r in hg.to_dicts():
            W = load_whitener(reg(r["goal_no"]), 32, m)
            u = W(np.asarray(cv[np.array(r["crow"])], dtype=np.float32))
            u /= np.linalg.norm(u, axis=1, keepdims=True)
            vecs[m].append(u.mean(0))
            if m == MODELS[0]:
                rows.append({"goal_no": r["goal_no"], "room": r["room"], "kind": "operator", "n": r["n"]})
    ftab = pl.DataFrame(rows).with_row_index("frow")
    Fs = {m: np.array(vecs[m], dtype=np.float32) for m in MODELS}
    if not write:
        return tab_out, Xs, ftab, Fs
    ftab.write_parquet(OUT / "fields.parquet")
    for m in MODELS:
        np.save(OUT / f"fields_{m}.npy", Fs[m])

    prov = {"built_by": "hypotheses/H100-room-symmetry-breaking/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["shared/embeddings/agent_day(+style_resid, white32 arrays, both models)",
                                   "shared/embeddings/statements", "shared/rooms_timeline", "shared/roster",
                                   "shared/period_units", "shared/embeddings/goals + goal_vectors",
                                   "shared/chat_core", "shared/embeddings/chat_index + chat arrays",
                                   "shared/embeddings/whitening_*"]}],
            "params": {"goals": [GOALS[0], GOALS[-1]], "holdout": "excluded (holdout_mask)",
                       "rooms_timeline_null_t_end": "+inf", "room_of_day": "majority room of the agent's statements",
                       "operator_min_msgs": 3, "claude_code_excluded": cc_agents},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print(f"agent-days {tab.height}; fields {len(rows)}; out {OUT}")


if __name__ == "__main__":
    main()
