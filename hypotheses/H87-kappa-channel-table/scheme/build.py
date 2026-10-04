"""H87 scheme: H70's scramble events plus the pointers of the remaining channels (agent chat, human messages, history
search), memory size at the event, 40-call viability and the new-goal flag for nights.

Data reuse, not code reuse: reads data/processed/H70-artifact-store-semantic-info/events.parquet (and repo_ids) and
data/processed/H84-search-outage-memory-scramble/search_events.parquet. Ledger calls are reloaded here with H70's
documented rule (cu/chat calls, Claude Code agent excluded, pt_date >= 2026-02-09, holdout masked, sorted by agent
and t_first, seq per agent-day, segments split at consolidation / session / first-of-day resets) and each event is
joined to its call on (agent, pt_date, seq); t_call is checked.

Added columns (repo ids are work_repos row ids, the same ids H70 uses; -1 = none):
  S_G, openG, n_agent_items, n_agent_named   agent-kind ledger items received in calls 1-5 of the window
  S_H, openH, n_human_items, n_human_named   human-kind items received in calls 1-5
  S_Q, openQ, n_search, n_search_named        the agent's history searches in calls 1-5 (answer repo ids)
  mem_chars                                   memory size at the event (memory_stats as-of, rows with lines_removed > 0)
  V40, n_win40                                work commits in calls 1-40 (stopping where H70's 20-call window stops:
                                              next reset for F/P, day end for N/PN), scaled to 20 calls
  day_in_goal, newgoal, continuation          nights: first active day of a goal period (newgoal; #40, the #39 -> #40
                                              continuation, is flagged separately)
Usage: uv run python hypotheses/H87-kappa-channel-table/scheme/build.py
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from collections import Counter  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit, holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
H70 = ROOT / "data/processed/H70-artifact-store-semantic-info"
H84 = ROOT / "data/processed/H84-search-outage-memory-scramble"
OUT = ROOT / "data/processed/H87-kappa-channel-table"
EARLY, WIN40 = 5, 40
FIRST_DENSE = "2026-02-09"


def log(*a):
    print(f"[{dt.datetime.now():%H:%M:%S}]", *a, flush=True)


def amap_table() -> pl.DataFrame:
    wr = pl.read_parquet(SH / "work_repos.parquet", columns=["repo", "artifacts"]).sort("repo")
    wr = wr.with_row_index("rid").with_columns(pl.col("rid").cast(pl.Int32))
    ids70 = pl.read_parquet(H70 / "repo_ids.parquet")
    assert ids70.height == wr.height and (ids70["repo"] == wr["repo"]).all(), "repo ids differ from H70's"
    a2r = wr.select("rid", "artifacts").explode("artifacts").rename({"artifacts": "artifact"}).drop_nulls()
    art = pl.read_parquet(SH / "artifacts.parquet", columns=["artifact", "parent"])
    child = (art.filter(pl.col("parent").is_not_null()).select("artifact", "parent")
             .join(a2r.rename({"artifact": "parent"}), on="parent", how="inner").select("artifact", "rid"))
    return pl.concat([a2r.select("artifact", "rid"), child]).unique("artifact", keep="first")


def load_calls(held_days: list[str] | None) -> pl.DataFrame:
    ros = pl.read_parquet(SH / "roster.parquet", columns=["agent", "claude_code"])
    cc = ros.filter(pl.col("claude_code"))["agent"].to_list()
    t = pl.read_parquet(SH / "context_ledger_turns.parquet",
                        columns=["turn_id", "agent", "pt_date", "goal_no", "regime", "holdout", "t_call", "t_first",
                                 "t_log", "ctx_mode", "reset_consol", "reset_forced", "reset_session", "first_of_day"])
    t = t.filter(pl.col("ctx_mode").is_in(["cu", "chat"]) & ~pl.col("agent").is_in(cc)
                 & (pl.col("pt_date") >= FIRST_DENSE))
    if held_days is not None:
        t = t.filter(pl.col("pt_date").is_in(held_days))
    else:
        hm = pl.Series(holdout_mask(t["pt_date"].to_list(), t["goal_no"].fill_null(-1).to_list()))
        t = t.filter(~hm & ~pl.col("holdout"))
        assert not t["holdout"].any()
    t = t.sort("agent", "t_first").with_columns(pl.int_range(pl.len()).over("agent", "pt_date").alias("seq"))
    return t.with_row_index("g").with_columns(pl.col("g").cast(pl.Int64))


def build(events_path: Path = H70 / "events.parquet", search_path: Path = H84 / "search_events.parquet",
          held_days: list[str] | None = None, out_name: str = "events_plus.parquet") -> dict:
    ev = pl.read_parquet(events_path)
    calls = load_calls(held_days)
    n = calls.height
    log("events", ev.height, "calls", n)
    ev = ev.join(calls.select("agent", "pt_date", "seq", "g", pl.col("t_call").alias("t_call_led")),
                 on=["agent", "pt_date", "seq"], how="left")
    miss = ev["g"].is_null().sum()
    bad = ev.filter(pl.col("g").is_not_null() & (pl.col("t_call") != pl.col("t_call_led"))).height
    log("unmatched", miss, "t_call mismatches", bad)
    assert miss == 0 and bad == 0, "event -> call mapping failed"
    amap = amap_table()
    # --- chat items naming repos, by kind
    am = pl.read_parquet(SH / "artifact_mentions.parquet", columns=["artifact", "t", "agent", "source", "message_id"])
    ch = (am.filter((pl.col("source") == "chat") & pl.col("message_id").is_not_null())
          .join(amap, on="artifact", how="inner").select("message_id", "rid").unique())
    items = (pl.scan_parquet(SH / "context_ledger_items.parquet").select("turn_id", "message_id", "kind")
             .filter(pl.col("kind").is_in(["agent", "human"])).collect())
    items = items.join(calls.select("turn_id", "g"), on="turn_id", how="inner")
    cnt = {k: np.zeros(n, dtype=np.int32) for k in ("agent", "human")}
    for k in cnt:
        gk = items.filter(pl.col("kind") == k)["g"].to_numpy()
        np.add.at(cnt[k], gk, 1)
    named = items.join(ch, on="message_id", how="inner")
    nm = {k: [[] for _ in range(n)] for k in ("agent", "human")}
    for g, r, k in zip(named["g"].to_list(), named["rid"].to_list(), named["kind"].cast(pl.Utf8).to_list()):
        nm[k][g].append(r)
    log("named items", named.group_by("kind").len().rows())
    # --- searches -> calls
    se = pl.read_parquet(search_path).sort("t")
    keys_first = calls.select("g", "agent", "t_first", "t_log").sort("t_first")
    sm = se.join_asof(keys_first, left_on="t", right_on="t_first", by="agent", strategy="backward",
                      check_sortedness=False)
    sm = sm.filter(pl.col("g").is_not_null() & (pl.col("t") <= pl.col("t_log") + pl.duration(seconds=1)))
    n_search = np.zeros(n, dtype=np.int32)
    np.add.at(n_search, sm["g"].to_numpy(), 1)
    srids: list[list] = [[] for _ in range(n)]
    for g, rs in zip(sm["g"].to_list(), sm["ans_rids"].to_list()):
        srids[g].extend(rs or [])
    log("searches mapped", sm.height, "of", se.height)
    # --- work commits per call (for V40)
    wc = pl.read_parquet(SH / "work_commits.parquet",
                         columns=["t", "author_agent", "author_kind", "canonical", "imported", "automated", "holdout",
                                  "pt_date", "goal_no"])
    wc = wc.filter(pl.col("canonical") & ~pl.col("imported") & (pl.col("author_kind") == "agent")
                   & ~pl.col("automated") & pl.col("author_agent").is_not_null())
    if held_days is None:
        hm = pl.Series(holdout_mask(wc["pt_date"].to_list(), wc["goal_no"].fill_null(-1).to_list()))
        wc = wc.filter(~hm & ~pl.col("holdout"))
    wc = wc.select("t", pl.col("author_agent").alias("agent")).sort("t")
    keys_log = calls.select("g", "agent", "t_log").sort("t_log")
    wm = wc.join_asof(keys_log, left_on="t", right_on="t_log", by="agent", strategy="forward", tolerance="10m",
                      check_sortedness=False).drop_nulls("g")
    n_work = np.zeros(n, dtype=np.int32)
    np.add.at(n_work, wm["g"].to_numpy(), 1)
    cs = np.concatenate([[0], np.cumsum(n_work)])
    # --- per event
    rows = {k: [] for k in ("S_G", "openG", "n_agent_items", "n_agent_named", "S_H", "openH", "n_human_items",
                            "n_human_named", "S_Q", "openQ", "n_search", "n_search_named", "V40", "n_win40")}
    dayscale = ev["etype"].is_in(["N", "PN"]).to_numpy()
    ag_arr, pd_arr = calls["agent"].to_numpy(), calls["pt_date"].to_numpy()
    for gi, nw, a, ds, sl, p0, sq in zip(ev["g"].to_numpy(), ev["n_win"].to_numpy(), ev["A_prev"].to_numpy(), dayscale,
                                         ev["seg_len"].to_numpy(), ev["pos0"].to_numpy(), ev["seq"].to_numpy()):
        e_end = gi + min(EARLY, nw)
        for kk, key in (("G", "agent"), ("H", "human")):
            lst = [r for k in range(gi, e_end) for r in nm[key][k]]
            rows[f"S_{kk}"].append(Counter(lst).most_common(1)[0][0] if lst else -1)
            rows[f"open{kk}"].append(bool(a >= 0 and a in lst))
            rows[f"n_{key}_items"].append(int(cnt[key][gi:e_end].sum()))
            rows[f"n_{key}_named"].append(len(lst))
        q = [r for k in range(gi, e_end) for r in srids[k]]
        rows["S_Q"].append(Counter(q).most_common(1)[0][0] if q else -1)
        rows["openQ"].append(bool(a >= 0 and a in q))
        rows["n_search"].append(int(n_search[gi:e_end].sum()))
        rows["n_search_named"].append(len(q))
        # 40-call window: same stopping rule as H70's (segment end for F/P; for N/PN the day end, found below)
        if ds:
            lim = gi
            while lim + 1 < n and ag_arr[lim + 1] == ag_arr[gi] and pd_arr[lim + 1] == pd_arr[gi] \
                    and lim + 1 - gi < WIN40:
                lim += 1
            n40 = lim - gi + 1
        else:
            n40 = int(min(WIN40, sl - p0))
        rows["n_win40"].append(n40)
        rows["V40"].append(float(cs[gi + n40] - cs[gi]) * 20 / n40 if n40 > 0 else np.nan)
    ev = ev.with_columns(**{k: pl.Series(v) for k, v in rows.items()})
    # --- memory size at the event
    ms = (pl.read_parquet(SH / "memory_stats.parquet", columns=["t", "agent", "n_chars", "lines_removed"])
          .filter(pl.col("lines_removed") > 0).select(pl.col("t").alias("t_mem"), "agent",
                                                      pl.col("n_chars").alias("mem_chars")).sort("t_mem"))
    ev = ev.sort("t_call").join_asof(ms, left_on="t_call", right_on="t_mem", by="agent", strategy="backward",
                                     tolerance="7d", check_sortedness=False)
    # --- goal-day index for nights
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "goal_no"])
    din = (cal.filter(pl.col("goal_no").is_not_null()).sort("pt_date")
           .with_columns(pl.int_range(1, pl.len() + 1).over("goal_no").alias("day_in_goal"))
           .select("pt_date", "day_in_goal"))
    ev = ev.join(din, on="pt_date", how="left").with_columns(
        ((pl.col("day_in_goal") == 1) & (pl.col("goal_no") != 40)).alias("newgoal"),
        ((pl.col("day_in_goal") == 1) & (pl.col("goal_no") == 40)).alias("continuation"))
    ev = ev.drop("t_call_led", "t_mem").sort("g")
    OUT.mkdir(parents=True, exist_ok=True)
    ev.write_parquet(OUT / out_name, compression="zstd")
    prov = {"built_by": "hypotheses/H87-kappa-channel-table/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["context_ledger_turns", "context_ledger_items", "artifact_mentions", "artifacts",
                                   "work_repos", "work_commits", "memory_stats", "calendar", "roster",
                                   "H70 events.parquet + repo_ids.parquet (data)", "H84 search_events.parquet (data)"]}],
            "params": {"EARLY": EARLY, "WIN40": WIN40, "first_day": FIRST_DENSE,
                       "memory_rows": "lines_removed > 0 (one row per regime-III consolidation)",
                       "holdout": "CONFIRMATORY" if held_days else "masked (holdout_mask + ledger holdout flag)"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    pp = OUT / "_provenance.json"
    old = json.loads(pp.read_text()) if pp.exists() else {}
    if held_days:
        old["confirm"] = prov
    else:
        old.update(prov)
    pp.write_text(json.dumps(old, indent=1))
    return {"events": ev.height}


if __name__ == "__main__":
    print(build())
