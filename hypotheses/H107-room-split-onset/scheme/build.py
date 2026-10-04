"""Room-split scheme (H107; byte-identical copy in H108 except OUT and WITH_REPOS): statement rows with rooms and time
bins, repo mentions mapped to statements, agent work per repo and goal, and room field vectors.

Output (OUT):
  statements.parquet     srow (row in the shared embeddings/statements_* arrays), kind, agent, t, pt_date, goal_no, unit,
                         regime, win30, half (0 = win30 0-3: the first two active hours; 1 = later), room_at (room of the
                         statement), room_day (majority room of the agent's statements that day), parity (0/1: odd/even
                         statement of the agent-day by time, for split halves)
  repo_mentions.parquet  (WITH_REPOS) strict agent artifact mentions (chat / intention; how in url, output, bare) mapped
                         to statement rows; files and sites mapped to their parent repo: repo, t, srow
  agent_repo_period.parquet (WITH_REPOS) DQ4 agent work per (goal_no, agent, repo): distinct commit hashes
                         (author_kind agent, not automated, not imported; canonical filter not applied: infra Known issues)
  fields.parquet + fields_<model>.npy  whitened unit room-kickoff vectors (kind kickoff_room) and per-room means of
                         whitened unit operator-message vectors (kind operator; human speakers; >= 3 messages). H100's rule.
Non-holdout rows only (holdout_mask, asserted); the Claude Code agent is excluded. No text is read; no vectors copied.
Room of a statement: H100/H102 rule (copied; candidate for infra/shared/: now four users): chat = message room;
intentions = as-of rooms_timeline (t_start <= t < t_end; null t_end -> +inf, infra Known issues).

Usage: uv run python hypotheses/H107-room-split-onset/scheme/build.py
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
OUT = ROOT / "data/processed/H107-room-split-onset"
WITH_REPOS = True
GOALS = list(range(33, 52))
MODELS = ["bge_small", "gte_modernbert"]
SUFFIX = {"bge_small": "", "gte_modernbert": "_gte_modernbert"}
CHAT = {"bge_small": "chat_bge_small.npy", "gte_modernbert": "chat_gte_modernbert.npy"}
FAR = dt.datetime(2100, 1, 1, tzinfo=dt.timezone.utc)
STRICT = ["url", "output", "bare"]


def rooms_timeline() -> pl.DataFrame:
    return (pl.read_parquet(SH / "rooms_timeline.parquet")
            .with_columns(pl.col("t_end").fill_null(pl.lit(FAR).cast(pl.Datetime("us", "UTC"))))
            .sort("agent", "t_start"))


def statement_rooms(st: pl.DataFrame) -> pl.DataFrame:
    """Room of every statement (H100 scheme/build.py rule, copied verbatim in logic)."""
    rt = rooms_timeline().select("agent", pl.col("t_start").alias("t"), pl.col("room").alias("room_rt"),
                                 pl.col("t_end"))
    s = st.with_row_index("_o").sort("agent", "t")
    j = s.join_asof(rt, on="t", by="agent", strategy="backward")
    j = j.with_columns(pl.when(pl.col("t") < pl.col("t_end")).then(pl.col("room_rt")).otherwise(None).alias("room_rt"))
    j = j.with_columns(pl.when(pl.col("kind") == "chat").then(pl.col("room")).otherwise(pl.col("room_rt"))
                       .alias("room_at"))
    return j.sort("_o").drop("_o", "room_rt", "t_end")


def build_statements(cc_agents, allow_holdout_goals=(), goals=None) -> pl.DataFrame:
    """allow_holdout_goals: used only in memory by analysis/confirm.py (guarded); main() never passes it."""
    allow = list(allow_holdout_goals)
    G = list(goals or GOALS) + [g for g in allow if g not in (goals or GOALS)]
    st = pl.read_parquet(ED / "statements.parquet").with_row_index("srow")
    st = st.filter(pl.col("goal_no").is_in(G) & ~pl.col("agent").is_in(cc_agents)
                   & (~pl.col("holdout") | pl.col("goal_no").is_in(allow)))
    hm = np.array(holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list()))
    st = st.filter(pl.Series(~hm | st["goal_no"].is_in(allow).to_numpy()))
    if not allow:
        assert not any(holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list()))
    st = statement_rooms(st)
    rd = (st.drop_nulls("room_at").group_by("agent", "pt_date", "room_at").len()
          .sort(["agent", "pt_date", "len", "room_at"], descending=[False, False, True, False])
          .group_by("agent", "pt_date", maintain_order=True).agg(pl.col("room_at").first().alias("room_day")))
    units = (pl.read_parquet(SH / "period_units.parquet").select("unit_id", "goal_no", "days").explode("days")
             .rename({"days": "pt_date", "unit_id": "unit"}))
    st = (st.join(rd, on=["agent", "pt_date"], how="left").join(units, on=["goal_no", "pt_date"], how="left")
          .sort("agent", "pt_date", "t", "srow")
          .with_columns((pl.col("t").rank("ordinal").over("agent", "pt_date") % 2).cast(pl.Int8).alias("parity"),
                        (pl.col("win30") >= 4).cast(pl.Int8).alias("half"))
          .sort("srow"))
    return st.select("srow", "kind", "agent", "t", "pt_date", "goal_no", "unit", "regime", "win30", "half",
                     "room_at", "room_day", "parity")


def build_repo_mentions(st: pl.DataFrame) -> pl.DataFrame:
    ar = pl.read_parquet(SH / "artifacts.parquet", columns=["artifact", "kind", "name", "parent"])
    ar = ar.with_columns(pl.col("kind").cast(pl.String))
    repos = ar.filter(pl.col("kind") == "repo").select("artifact", pl.col("name").alias("repo"))
    par = (ar.filter(pl.col("kind") != "repo").drop_nulls("parent")
           .join(repos.rename({"artifact": "parent", "repo": "repo"}), on="parent", how="inner")
           .select("artifact", "repo"))
    amap = pl.concat([repos, par])
    am = pl.read_parquet(SH / "artifact_mentions.parquet",
                         columns=["artifact", "t", "agent", "speaker_kind", "source", "how", "message_id", "ref_index"])
    am = am.with_columns(pl.col("speaker_kind").cast(pl.String), pl.col("source").cast(pl.String),
                         pl.col("how").cast(pl.String))
    am = am.filter((pl.col("speaker_kind") == "agent") & pl.col("source").is_in(["chat", "intention"])
                   & pl.col("how").is_in(STRICT)).join(amap, on="artifact", how="inner")
    ci = pl.read_parquet(ED / "chat_index.parquet").with_row_index("src_row")
    ii = pl.read_parquet(ED / "intentions_index.parquet").with_row_index("src_row")
    sall = pl.read_parquet(ED / "statements.parquet", columns=["kind", "src_row"]).with_row_index("srow")
    c = (am.filter(pl.col("source") == "chat").join(ci, on="message_id", how="inner")
         .join(sall.filter(pl.col("kind") == "chat").drop("kind"), on="src_row", how="inner"))
    i = (am.filter(pl.col("source") == "intention").join(ii.rename({"event_index": "ref_index"}), on="ref_index",
                                                           how="inner")
         .join(sall.filter(pl.col("kind") == "intent").drop("kind"), on="src_row", how="inner"))
    out = pl.concat([c.select("repo", "t", "srow"), i.select("repo", "t", "srow")]).unique(["repo", "srow"])
    return out.join(st.select("srow"), on="srow", how="semi").sort("srow", "repo")


def build_agent_repo(allow_holdout_goals=()) -> pl.DataFrame:
    allow = list(allow_holdout_goals)
    wc = pl.read_parquet(SH / "work_commits.parquet",
                         columns=["repo", "hash", "author_agent", "author_kind", "automated", "imported", "goal_no",
                                  "holdout", "pt_date"])
    wc = wc.filter((pl.col("author_kind") == "agent") & ~pl.col("automated") & ~pl.col("imported")
                   & (~pl.col("holdout") | pl.col("goal_no").is_in(allow))
                   & pl.col("goal_no").is_in(GOALS + allow)).drop_nulls("author_agent")
    hm = np.array(holdout_mask(wc["pt_date"].to_list(), wc["goal_no"].to_list()))
    wc = wc.filter(pl.Series(~hm | wc["goal_no"].is_in(allow).to_numpy()))
    return (wc.group_by("goal_no", "author_agent", "repo").agg(pl.col("hash").n_unique().alias("n_commits"))
            .rename({"author_agent": "agent"}).sort("goal_no", "agent", "repo"))


def build_fields():
    g = pl.read_parquet(ED / "goals.parquet").with_columns(pl.col("kind").cast(pl.String))
    kr = g.filter((pl.col("kind") == "kickoff_room") & pl.col("goal_no").is_in(GOALS) & ~pl.col("holdout"))
    cc = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "pt_date", "goal_no", "room", "speaker_kind"])
    ci = pl.read_parquet(ED / "chat_index.parquet").with_row_index("crow")
    hum = (cc.filter((pl.col("speaker_kind") == "human") & pl.col("goal_no").is_in(GOALS))
           .join(ci, on="message_id", how="inner"))
    hm = np.array(holdout_mask(hum["pt_date"].to_list(), hum["goal_no"].to_list()))
    hum = hum.filter(pl.Series(~hm))
    hg = hum.group_by("goal_no", "room").agg(pl.col("crow"), pl.len().alias("n")).filter(pl.col("n") >= 3) \
        .sort("goal_no", "room")
    rows, vecs = [], {m: [] for m in MODELS}
    reg = lambda gno: "II" if gno <= 35 else "III"  # noqa: E731
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
    return pl.DataFrame(rows).with_row_index("frow"), {m: np.array(vecs[m], dtype=np.float32) for m in MODELS}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    roster = pl.read_parquet(SH / "roster.parquet")
    cc_agents = roster.filter(pl.col("claude_code"))["agent"].to_list()
    st = build_statements(cc_agents)
    st.write_parquet(OUT / "statements.parquet", compression="zstd")
    info = {"statements": st.height}
    if WITH_REPOS:
        rm = build_repo_mentions(st)
        rm.write_parquet(OUT / "repo_mentions.parquet", compression="zstd")
        ar = build_agent_repo()
        ar.write_parquet(OUT / "agent_repo_period.parquet", compression="zstd")
        info.update(repo_mentions=rm.height, agent_repo_rows=ar.height)
    ft, F = build_fields()
    ft.write_parquet(OUT / "fields.parquet")
    for m in MODELS:
        np.save(OUT / f"fields_{m}.npy", F[m])
    info["fields"] = ft.height
    prov = {"built_by": str(Path(__file__).resolve().relative_to(ROOT)), "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["shared/embeddings/statements (+ statements_* arrays read at analysis time)",
                                   "shared/rooms_timeline", "shared/roster", "shared/period_units",
                                   "shared/artifacts", "shared/artifact_mentions", "shared/embeddings/chat_index",
                                   "shared/embeddings/intentions_index", "shared/work_commits",
                                   "shared/embeddings/goals + goal_vectors", "shared/chat_core",
                                   "shared/embeddings/chat arrays", "shared/embeddings/whitening_*"]}],
            "params": {"goals": [GOALS[0], GOALS[-1]], "holdout": "excluded (holdout_mask, asserted)",
                       "rooms_timeline_null_t_end": "+inf", "half": "win30 < 4 -> 0", "strict_mentions": STRICT,
                       "work": "author_kind agent, ~automated, ~imported, distinct hashes", "with_repos": WITH_REPOS,
                       "claude_code_excluded": cc_agents},
            "counts": info, "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print(json.dumps(info), "->", OUT)


if __name__ == "__main__":
    main()
