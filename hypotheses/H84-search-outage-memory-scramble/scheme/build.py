"""H84 scheme: the agent-day panel (outage DiD, NE18) and the per-search call frame (replication I_Q, G51 native).

Inputs: shared context_ledger_turns, work_commits, work_repos, artifact_mentions, artifacts, calendar, period_units,
roster; H84's own search_events.parquet (scheme/search_events.py). Codes and counts only; no text.

panel.parquet: one row per (agent, pt_date), regime-III non-holdout days 2026-03-24 -> 2026-05-29, all non-Claude-Code
agents with >= 1 ledger call that day. Columns:
  calls, search_calls (ledger kind == search), searches (raw SEARCH_HISTORY rows), failed (answer < 150 chars),
  ans_med (median answer chars), commits (DQ4 agent work), commits_pre (on repos whose first commit is before the
  day's window start), new_repos (first commit that day, first committer = the agent), dup_repos (new repos whose
  basename token set has Jaccard >= 0.5 with a repo existing before the day), ment (strict mentions of repo/site/file
  artifacts: how in url/output/bare; source action/chat/intention), ment_old (of those, artifacts first seen before
  the goal period's first day), rereads (action mentions resolving to a repo the agent committed to before the day),
  goal_no, unit_id, day_in_goal (1-based active-day index within the goal period).
search_calls.parquet: one row per raw search mapped to the agent's ledger call (t_first <= t <= t_log + 1 s):
  agent, pt_date, goal_no, unit_id, t, ans_chars, query_chars, S_Q (repo most named by the answer; -1 none),
  n_ans_rids, A_prev (repo of the last work commit before the call, <= 7 d), X_next (repo of the first work commit
  in the call and the next 19 calls, stopping at the next reset; -1 none), V (work commits in that window scaled to
  20 calls), V_pre (work commits in the 20 calls before), n_win, ctx_pos.

Usage: uv run python hypotheses/H84-search-outage-memory-scramble/scheme/build.py
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import datetime as dt  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
from collections import Counter  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit, holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H84-search-outage-memory-scramble"
D0, D1 = "2026-03-24", "2026-05-29"
WIN, PRE_V, MIN_WIN = 20, 20, 10
FAIL_CHARS = 150
TZ = "America/Los_Angeles"


def log(*a):
    print(f"[{dt.datetime.now():%H:%M:%S}]", *a, flush=True)


def tokens(name: str) -> frozenset:
    base = name.split("/")[-1].lower()
    return frozenset(t for t in re.split(r"[-_.]+", base) if len(t) >= 3)


def repo_tables():
    wr = pl.read_parquet(SH / "work_repos.parquet", columns=["repo", "artifacts", "first_commit_t"]).sort("repo")
    wr = wr.with_row_index("rid").with_columns(pl.col("rid").cast(pl.Int32))
    a2r = wr.select("rid", "artifacts").explode("artifacts").rename({"artifacts": "artifact"}).drop_nulls()
    art = pl.read_parquet(SH / "artifacts.parquet", columns=["artifact", "kind", "parent", "first_t"])
    child = (art.filter(pl.col("parent").is_not_null()).select("artifact", "parent")
             .join(a2r.rename({"artifact": "parent"}), on="parent", how="inner").select("artifact", "rid"))
    amap = pl.concat([a2r.select("artifact", "rid"), child]).unique("artifact", keep="first")
    return wr, amap, art


def load_calls(held_days: list[str] | None = None) -> pl.DataFrame:
    ros = pl.read_parquet(SH / "roster.parquet", columns=["agent", "claude_code"])
    cc = ros.filter(pl.col("claude_code"))["agent"].to_list()
    t = pl.read_parquet(SH / "context_ledger_turns.parquet",
                        columns=["turn_id", "agent", "pt_date", "goal_no", "regime", "holdout", "t_call", "t_first",
                                 "t_log", "kind", "ctx_mode", "reset_consol", "reset_forced", "reset_session",
                                 "first_of_day", "ctx_pos"])
    t = t.filter(pl.col("ctx_mode").is_in(["cu", "chat"]) & ~pl.col("agent").is_in(cc)
                 & (pl.col("regime").cast(pl.Utf8) == "III"))
    if held_days is not None:
        t = t.filter(pl.col("pt_date").is_in(held_days))
    else:
        hm = pl.Series(holdout_mask(t["pt_date"].to_list(), t["goal_no"].fill_null(-1).to_list()))
        t = t.filter(~hm & ~pl.col("holdout"))
        assert not t["holdout"].any()
    t = t.sort("agent", "t_first").with_columns(pl.int_range(pl.len()).over("agent", "pt_date").alias("seq"))
    rst = pl.col("reset_consol") | pl.col("reset_session") | pl.col("first_of_day") | (pl.col("seq") == 0)
    t = t.with_columns(rst.cast(pl.Int32).cum_sum().over("agent", "pt_date").alias("seg"))
    t = t.with_columns(pl.int_range(pl.len()).over("agent", "pt_date", "seg").alias("pos0"),
                       pl.len().over("agent", "pt_date", "seg").alias("seg_len"))
    return t.with_row_index("g").with_columns(pl.col("g").cast(pl.Int64))


def work_commits(wr: pl.DataFrame, held: bool) -> tuple[pl.DataFrame, pl.DataFrame]:
    wc = pl.read_parquet(SH / "work_commits.parquet",
                         columns=["repo", "t", "author_agent", "author_kind", "canonical", "imported", "automated",
                                  "holdout", "pt_date", "goal_no"])
    if not held:
        hm = pl.Series(holdout_mask(wc["pt_date"].to_list(), wc["goal_no"].fill_null(-1).to_list()))
        wc = wc.filter(~hm & ~pl.col("holdout"))
    wc = wc.with_columns(pl.col("repo").cast(pl.Utf8)).join(wr.select("rid", "repo"), on="repo", how="left")
    # first committer of every repo (any author kind): who created it
    first = (wc.filter(pl.col("author_agent").is_not_null()).sort("t").group_by("rid")
             .agg(pl.col("author_agent").first().alias("creator"), pl.col("t").first().alias("t_first_seen")))
    work = wc.filter(pl.col("canonical") & ~pl.col("imported") & (pl.col("author_kind") == "agent")
                     & ~pl.col("automated") & pl.col("author_agent").is_not_null())
    work = work.select("t", "pt_date", pl.col("author_agent").alias("agent"), pl.col("rid").fill_null(-2)).sort("t")
    return work, first


def build_panel(calls, wr, amap, art, work, first, srch, held: bool) -> pl.DataFrame:
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "goal_no", "win_start"])
    pu = pl.read_parquet(SH / "period_units.parquet", columns=["unit_id", "days"]).explode("days").rename(
        {"days": "pt_date"})
    gstart = (cal.filter(pl.col("goal_no").is_not_null()).group_by("goal_no")
              .agg(pl.col("win_start").min().alias("goal_start")))
    days = cal.filter((pl.col("pt_date") >= D0) & (pl.col("pt_date") <= D1)) if not held else cal
    days = days.join(gstart, on="goal_no", how="left")
    # day index within goal period (active days)
    din = (cal.filter(pl.col("goal_no").is_not_null()).sort("pt_date")
           .with_columns(pl.int_range(1, pl.len() + 1).over("goal_no").alias("day_in_goal"))
           .select("pt_date", "day_in_goal"))
    c = calls.filter(pl.col("pt_date").is_in(days["pt_date"].implode()))
    base = (c.group_by("agent", "pt_date").agg(pl.len().alias("calls"),
                                                (pl.col("kind") == "search").sum().alias("search_calls")))
    s = (srch.group_by("agent", "pt_date").agg(pl.len().alias("searches"),
                                                (pl.col("ans_chars") < FAIL_CHARS).sum().alias("failed"),
                                                pl.col("ans_chars").median().alias("ans_med")))
    base = base.join(s, on=["agent", "pt_date"], how="left").with_columns(
        pl.col("searches").fill_null(0), pl.col("failed").fill_null(0))
    base = base.join(days.select("pt_date", "goal_no", "win_start", "goal_start"), on="pt_date", how="left")
    # commits and continuity
    rfirst = wr.select("rid", "repo", "first_commit_t").join(first, on="rid", how="left").with_columns(
        pl.min_horizontal("first_commit_t", "t_first_seen").alias("t0"))
    wk = work.join(rfirst.select("rid", "t0"), on="rid", how="left").join(
        days.select("pt_date", "win_start"), on="pt_date", how="inner")
    wk = wk.with_columns((pl.col("t0") < pl.col("win_start")).fill_null(False).alias("pre"))
    cm = wk.group_by("agent", "pt_date").agg(pl.len().alias("commits"), pl.col("pre").sum().alias("commits_pre"))
    # new repos and duplicates
    rf = rfirst.filter(pl.col("t0").is_not_null()).with_columns(
        pl.col("t0").dt.convert_time_zone(TZ).dt.date().cast(pl.Utf8).alias("d0"))
    toks = {r: tokens(n) for r, n in zip(rf["rid"].to_list(), rf["repo"].to_list())}
    order = rf.sort("t0")
    t0s = order["t0"].to_list()
    rids = order["rid"].to_list()
    newr = rf.filter(pl.col("creator").is_not_null() & pl.col("d0").is_in(days["pt_date"].implode()))
    newr = newr.join(days.select(pl.col("pt_date").alias("d0"), "win_start"), on="d0", how="inner")
    dup = []
    import bisect
    for r, ws in zip(newr["rid"].to_list(), newr["win_start"].to_list()):
        k = bisect.bisect_left(t0s, ws)
        tk = toks[r]
        hit = False
        if tk:
            for j in range(k):
                o = toks[rids[j]]
                if o and len(tk & o) / len(tk | o) >= 0.5:
                    hit = True
                    break
        dup.append(hit)
    newr = newr.with_columns(pl.Series("dup", dup))
    nr = (newr.group_by(pl.col("creator").alias("agent"), pl.col("d0").alias("pt_date"))
          .agg(pl.len().alias("new_repos"), pl.col("dup").sum().alias("dup_repos")))
    # strict mentions, earlier-goal share, re-reads
    am = pl.read_parquet(SH / "artifact_mentions.parquet", columns=["artifact", "t", "agent", "source", "how"])
    am = am.filter(pl.col("agent").is_not_null() & pl.col("source").cast(pl.Utf8).is_in(["action", "chat", "intention"]))
    am = am.with_columns(pl.col("t").dt.convert_time_zone(TZ).dt.date().cast(pl.Utf8).alias("pt_date"))
    am = am.filter(pl.col("pt_date").is_in(days["pt_date"].implode()))
    strict = am.filter(pl.col("how").cast(pl.Utf8).is_in(["url", "output", "bare"])).join(
        art.filter(pl.col("kind").is_in(["repo", "site", "file"])).select("artifact", "first_t"), on="artifact",
        how="inner").join(days.select("pt_date", "goal_start"), on="pt_date", how="inner")
    mt = (strict.group_by("agent", "pt_date").agg(pl.len().alias("ment"),
                                                   (pl.col("first_t") < pl.col("goal_start")).sum().alias("ment_old")))
    # re-reads: action mentions (any how) of a repo the agent committed to before the day's window start
    act = am.filter(pl.col("source") == "action").join(amap, on="artifact", how="inner").join(
        days.select("pt_date", "win_start"), on="pt_date", how="inner")
    owned = work.group_by("agent", "rid").agg(pl.col("t").min().alias("t_own"))
    rr = (act.join(owned, on=["agent", "rid"], how="inner").filter(pl.col("t_own") < pl.col("win_start"))
          .group_by("agent", "pt_date").agg(pl.len().alias("rereads")))
    panel = (base.join(cm, on=["agent", "pt_date"], how="left").join(nr, on=["agent", "pt_date"], how="left")
             .join(mt, on=["agent", "pt_date"], how="left").join(rr, on=["agent", "pt_date"], how="left")
             .join(pu, on="pt_date", how="left").join(din, on="pt_date", how="left"))
    fill = ["commits", "commits_pre", "new_repos", "dup_repos", "ment", "ment_old", "rereads"]
    panel = panel.with_columns([pl.col(k).fill_null(0).cast(pl.Int32) for k in fill])
    return panel.drop("win_start", "goal_start").sort("agent", "pt_date")


def build_search_calls(calls, work, srch) -> pl.DataFrame:
    keys_first = calls.select("g", "agent", "t_first", "t_log").sort("t_first")
    s = srch.sort("t").join_asof(keys_first, left_on="t", right_on="t_first", by="agent", strategy="backward",
                                 check_sortedness=False)
    s = s.filter(pl.col("g").is_not_null() & (pl.col("t") <= pl.col("t_log") + pl.duration(seconds=1)))
    n = calls.height
    agent_arr = calls["agent"].to_numpy()
    keys_log = calls.select("g", "agent", "t_log").sort("t_log")
    wm = work.join_asof(keys_log, left_on="t", right_on="t_log", by="agent", strategy="forward", tolerance="10m",
                        check_sortedness=False).drop_nulls("g")
    n_work = np.zeros(n, dtype=np.int32)
    np.add.at(n_work, wm["g"].to_numpy(), 1)
    first_repo = np.full(n, -1, dtype=np.int32)
    fr = wm.sort("t").group_by("g").agg(pl.col("rid").first())
    first_repo[fr["g"].to_numpy()] = fr["rid"].to_numpy()
    cs = np.concatenate([[0], np.cumsum(n_work)])
    pos0 = calls["pos0"].to_numpy()
    segl = calls["seg_len"].to_numpy()
    rows = {k: [] for k in ("n_win", "V", "V_pre", "X_next")}
    for gi in s["g"].to_numpy():
        nw = int(min(WIN, segl[gi] - pos0[gi]))
        rows["n_win"].append(nw)
        rows["V"].append(float(cs[gi + nw] - cs[gi]) * WIN / nw if nw > 0 else np.nan)
        lo = gi - PRE_V
        while lo < gi and agent_arr[max(lo, 0)] != agent_arr[gi]:
            lo += 1
        rows["V_pre"].append(float(cs[gi] - cs[max(lo, 0)]))
        xn = -1
        for k in range(gi, gi + nw):
            if first_repo[k] != -1:
                xn = int(first_repo[k])
                break
        rows["X_next"].append(xn)
    s = s.with_columns(**{k: pl.Series(v) for k, v in rows.items()})
    s = s.join(calls.select("g", "ctx_pos"), on="g", how="left")
    s = s.sort("t").join_asof(work.select(pl.col("t").alias("t_c"), "agent", pl.col("rid").alias("A_prev")),
                              left_on="t", right_on="t_c", by="agent", strategy="backward", tolerance="7d",
                              check_sortedness=False)
    s = s.with_columns(
        pl.col("A_prev").fill_null(-1),
        pl.col("ans_rids").list.len().alias("n_ans_rids"),
        pl.col("ans_rids").list.eval(pl.element().mode().first()).list.first().fill_null(-1).alias("S_Q"))
    pu = pl.read_parquet(SH / "period_units.parquet", columns=["unit_id", "days"]).explode("days").rename(
        {"days": "pt_date"})
    s = s.join(pu, on="pt_date", how="left")
    return s.select("agent", "pt_date", "goal_no", "unit_id", "t", "g", "ans_chars", "query_chars", "S_Q",
                    "n_ans_rids", "A_prev", "X_next", "V", "V_pre", "n_win", "ctx_pos").filter(pl.col("n_win") >= 1)


def main(held_days: list[str] | None = None):
    held = held_days is not None
    wr, amap, art = repo_tables()
    calls = load_calls(held_days)
    log("calls", calls.height)
    work, first = work_commits(wr, held)
    srch = pl.read_parquet(OUT / ("search_events_confirm.parquet" if held else "search_events.parquet"))
    panel = build_panel(calls, wr, amap, art, work, first, srch, held)
    log("panel rows", panel.height)
    sc = build_search_calls(calls, work, srch)
    log("search calls mapped", sc.height, "of", srch.height)
    tag = "_confirm" if held else ""
    panel.write_parquet(OUT / f"panel{tag}.parquet", compression="zstd")
    sc.write_parquet(OUT / f"search_calls{tag}.parquet", compression="zstd")
    prov_path = OUT / "_provenance.json"
    prov = json.loads(prov_path.read_text()) if prov_path.exists() else {}
    prov.update({"built_by": "hypotheses/H84-search-outage-memory-scramble/scheme/build.py", "git_commit": git_commit(),
                 "inputs": [{"source": "ai-village", "revision": REVISION,
                             "tables": ["context_ledger_turns", "work_commits", "work_repos", "artifact_mentions",
                                        "artifacts", "calendar", "period_units", "roster", "H84 search_events"]}],
                 "params": {"days": [D0, D1], "regime": "III", "WIN": WIN, "PRE_V": PRE_V, "fail_chars": FAIL_CHARS,
                            "dup_rule": "basename tokens (>=3 chars) Jaccard >= 0.5 vs repos existing before the day",
                            "strict_mentions": "how in url/output/bare; kind repo/site/file",
                            "work_filter": "canonical & ~imported & author_kind==agent & ~automated",
                            "holdout": "CONFIRMATORY" if held else "masked (holdout_mask + ledger holdout flag)"},
                 "built_at": dt.datetime.now(dt.timezone.utc).isoformat()})
    prov_path.write_text(json.dumps(prov, indent=1, default=str))


if __name__ == "__main__":
    main()
