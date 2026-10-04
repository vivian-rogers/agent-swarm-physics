"""H70 scheme: scramble events (forced erasures, nights) and matched placebos with channel pointers and outcomes.

Usage:
    uv run python hypotheses/H70-artifact-store-semantic-info/scheme/build.py      # exploratory (holdout masked)
The confirmatory script calls build(days=..., held=True) on held-out days explicitly; nothing else may.

Event types (per agent, ledger calls ordered by t_first):
  F  forced erasure: first call after reset_forced (regime III, cu mode)
  P  pseudo-erasure: call at position 21 of a segment with >= 40 calls (regime III, cu mode; H44)
  N  night: first call of the agent's PT day (all regimes)
  PN mid-day placebo: one call per agent-day nearest the day's middle with >= 20 calls before and after it that day
Window W = the event call and the next 19 calls; F/P windows stop at the next reset, N/PN windows at the day end
(regime I/II sessions are short); >= 10 calls kept.
Channel pointers (repo ids; -1 = none):
  A_prev  repo of the agent's last agent work commit before the event call (<= 7 days)
  S_M     repo named by the most recent intention before the event (<= 24 h)
  S_R     repo named most often by chat items the agent receives in calls 1-5 of W (ledger receiving calls)
  S_C     repo touched most in the agent's 10 calls before the event (executed commands)
Open flags: openA = A_prev touched in calls 1-5; openM = S_M == A_prev; openR = a received item names A_prev.
Outcomes (columns only; never used to select events): X_next = repo of the first work commit in W (-1 none);
V = work commits in W scaled to 20 calls; V_pre = work commits in the 20 calls before the event.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

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
OUT = ROOT / "data/processed/H70-artifact-store-semantic-info"
WIN, EARLY, PRE_C, PRE_V, MIN_WIN = 20, 5, 10, 20, 10
FIRST_DENSE = "2026-02-09"  # #30: DQ4 work commits are dense from here on


def log(*a):
    print(f"[{dt.datetime.now():%H:%M:%S}]", *a, flush=True)


def repo_map() -> tuple[pl.DataFrame, pl.DataFrame]:
    """(repo name <-> int id), (artifact id -> repo id) for repos, their files and their sites."""
    wr = pl.read_parquet(SH / "work_repos.parquet", columns=["repo", "artifacts"]).sort("repo")
    wr = wr.with_row_index("rid").with_columns(pl.col("rid").cast(pl.Int32))
    ids = wr.select("rid", "repo")
    a2r = wr.select("rid", "artifacts").explode("artifacts").rename({"artifacts": "artifact"}).drop_nulls()
    art = pl.read_parquet(SH / "artifacts.parquet", columns=["artifact", "kind", "parent"])
    child = (art.filter(pl.col("parent").is_not_null()).select("artifact", "parent")
             .join(a2r.rename({"artifact": "parent"}), on="parent", how="inner").select("artifact", "rid"))
    amap = pl.concat([a2r.select("artifact", "rid"), child]).unique("artifact", keep="first")
    return ids, amap


def load_calls(days: list[str] | None, held: bool) -> pl.DataFrame:
    ros = pl.read_parquet(SH / "roster.parquet", columns=["agent", "claude_code"])
    cc = ros.filter(pl.col("claude_code"))["agent"].to_list()
    t = pl.read_parquet(SH / "context_ledger_turns.parquet",
                        columns=["turn_id", "agent", "pt_date", "goal_no", "regime", "holdout", "t_call", "t_first",
                                 "t_log", "kind", "ctx_mode", "reset_consol", "reset_forced", "reset_session",
                                 "first_of_day", "ctx_pos"])
    t = t.filter(pl.col("ctx_mode").is_in(["cu", "chat"]) & ~pl.col("agent").is_in(cc)
                 & (pl.col("pt_date") >= FIRST_DENSE))
    if held:
        t = t.filter(pl.col("pt_date").is_in(days))
    else:
        hm = pl.Series(holdout_mask(t["pt_date"].to_list(), t["goal_no"].fill_null(-1).to_list()))
        t = t.filter(~hm & ~pl.col("holdout"))
        assert not t["holdout"].any()
    t = t.with_columns(pl.col("regime").cast(pl.Utf8)).sort("agent", "t_first")
    t = t.with_columns(pl.int_range(pl.len()).over("agent", "pt_date").alias("seq"))
    rst = pl.col("reset_consol") | pl.col("reset_session") | pl.col("first_of_day") | (pl.col("seq") == 0)
    t = t.with_columns(rst.alias("is_reset"))
    t = t.with_columns(pl.col("is_reset").cast(pl.Int32).cum_sum().over("agent", "pt_date").alias("seg"))
    t = t.with_columns(pl.int_range(pl.len()).over("agent", "pt_date", "seg").alias("pos0"),
                       pl.len().over("agent", "pt_date", "seg").alias("seg_len"),
                       pl.len().over("agent", "pt_date").alias("day_len"))
    return t.with_row_index("g").with_columns(pl.col("g").cast(pl.Int64))


def build(days: list[str] | None = None, held: bool = False, out: Path = OUT) -> dict:
    assert (days is None) != held or (held and days), "held-out builds need explicit days"
    ids, amap = repo_map()
    calls = load_calls(days, held)
    log("calls", calls.height)
    keys_log = calls.select("g", "agent", "t_log").sort("t_log")
    keys_first = calls.select("g", "agent", "t_first", "t_log").sort("t_first")
    n = calls.height
    agent_arr = calls["agent"].to_numpy()
    # --- work commits -> calls
    wc = pl.read_parquet(SH / "work_commits.parquet",
                         columns=["repo", "t", "author_agent", "author_kind", "canonical", "imported", "automated",
                                  "holdout", "pt_date", "goal_no"])
    wc = wc.filter(pl.col("canonical") & ~pl.col("imported") & (pl.col("author_kind") == "agent")
                   & ~pl.col("automated") & pl.col("author_agent").is_not_null())
    if not held:
        hm = pl.Series(holdout_mask(wc["pt_date"].to_list(), wc["goal_no"].fill_null(-1).to_list()))
        wc = wc.filter(~hm & ~pl.col("holdout"))
    wc = (wc.with_columns(pl.col("repo").cast(pl.Utf8)).join(ids, on="repo", how="left")
          .select("t", pl.col("author_agent").alias("agent"), pl.col("rid").fill_null(-2).cast(pl.Int32))
          .sort("t"))
    wm = wc.join_asof(keys_log, left_on="t", right_on="t_log", by="agent", strategy="forward", tolerance="10m",
                      check_sortedness=False).drop_nulls("g")
    log("work commits", wc.height, "mapped", wm.height)
    n_work = np.zeros(n, dtype=np.int32)
    gw = wm["g"].to_numpy()
    np.add.at(n_work, gw, 1)
    first_repo = np.full(n, -1, dtype=np.int32)
    fr = wm.sort("t").group_by("g").agg(pl.col("rid").first())
    first_repo[fr["g"].to_numpy()] = fr["rid"].to_numpy()
    # --- action mentions -> calls (touched repos)
    am = pl.read_parquet(SH / "artifact_mentions.parquet", columns=["artifact", "t", "agent", "source", "message_id"])
    act = (am.filter(pl.col("source") == "action").join(amap, on="artifact", how="inner")
           .select("t", "agent", "rid").sort("t"))
    act = act.join_asof(keys_first, left_on="t", right_on="t_first", by="agent", strategy="backward",
                        check_sortedness=False)
    act = act.filter(pl.col("g").is_not_null() & (pl.col("t") <= pl.col("t_log") + pl.duration(seconds=1)))
    touched: list[set] = [set() for _ in range(n)]
    for g, r in zip(act["g"].to_list(), act["rid"].to_list()):
        touched[g].add(r)
    log("action repo mentions mapped", act.height)
    # --- chat mentions -> receiving calls
    ch = (am.filter((pl.col("source") == "chat") & pl.col("message_id").is_not_null())
          .join(amap, on="artifact", how="inner").select("message_id", "rid").unique())
    items = (pl.scan_parquet(SH / "context_ledger_items.parquet").select("turn_id", "message_id")
             .filter(pl.col("message_id").is_in(ch["message_id"].unique().implode())).collect())
    items = items.join(ch, on="message_id", how="inner").join(calls.select("turn_id", "g"), on="turn_id", how="inner")
    named: list[list] = [[] for _ in range(n)]
    for g, r in zip(items["g"].to_list(), items["rid"].to_list()):
        named[g].append(r)
    log("received repo-naming items", items.height)
    # --- intentions (memory note pointer)
    it = (am.filter(pl.col("source") == "intention").join(amap, on="artifact", how="inner")
          .select(pl.col("t").alias("t_int"), "agent", pl.col("rid").alias("S_M"))
          .unique(["agent", "t_int"], keep="first", maintain_order=True).sort("t_int"))
    # --- events
    c = calls
    is_r3cu = (c["regime"] == "III") & (c["ctx_mode"] == "cu")
    F = c.filter(is_r3cu & c["reset_forced"]).select("g").with_columns(pl.lit("F").alias("etype"))
    P = c.filter(is_r3cu & (pl.col("pos0") == 20) & (pl.col("seg_len") >= 40)).select("g").with_columns(
        pl.lit("P").alias("etype"))
    N = c.filter(pl.col("seq") == 0).select("g").with_columns(pl.lit("N").alias("etype"))
    # day-scale placebo: a mid-day call with >= 20 calls before and after it in the day (resets allowed, as for N)
    cand = c.filter((pl.col("seq") >= 20) & (pl.col("day_len") - pl.col("seq") >= 20))
    PN = (cand.with_columns((pl.col("seq") - pl.col("day_len") / 2).abs().alias("dmid"))
          .sort("dmid").group_by("agent", "pt_date").agg(pl.col("g").first()).select("g")
          .with_columns(pl.lit("PN").alias("etype")))
    ev = pl.concat([F, P, N, PN]).join(c.select("g", "agent", "pt_date", "goal_no", "regime", "t_call", "seg",
                                                "seg_len", "pos0", "day_len", "seq"), on="g")
    log("events", ev.group_by("etype").len().sort("etype").rows())
    # A_prev: last work commit before the event call (<= 7 days)
    ev = ev.sort("t_call").join_asof(wc.rename({"t": "t_c", "rid": "A_prev"}), left_on="t_call", right_on="t_c",
                                     by="agent", strategy="backward", tolerance="7d", check_sortedness=False)
    ev = ev.join_asof(it, left_on="t_call", right_on="t_int", by="agent", strategy="backward", tolerance="24h",
                      check_sortedness=False)
    ev = ev.with_columns(pl.col("A_prev").fill_null(-1), pl.col("S_M").fill_null(-1)).sort("g")
    # per-event window aggregates
    g_arr = ev["g"].to_numpy()
    pos0 = ev["pos0"].to_numpy()
    segl = ev["seg_len"].to_numpy()
    # day scale (N, PN): the window runs WIN calls within the day, across session resets (regime I/II sessions are
    # short); call scale (F, P): the window stops at the next reset
    dayscale = ev["etype"].is_in(["N", "PN"]).to_numpy()
    seqs = ev["seq"].to_numpy()
    dlen = ev["day_len"].to_numpy()
    A = ev["A_prev"].to_numpy()
    cs = np.concatenate([[0], np.cumsum(n_work)])
    rows = {k: [] for k in ("n_win", "V", "V_pre", "X_next", "openA", "S_R", "openR", "S_C", "n_items_named")}
    for gi, p0, sl, a, ds, sq, dl in zip(g_arr, pos0, segl, A, dayscale, seqs, dlen):
        nw = int(min(WIN, (dl - sq) if ds else (sl - p0)))
        rows["n_win"].append(nw)
        rows["V"].append(float(cs[gi + nw] - cs[gi]) * WIN / nw if nw > 0 else np.nan)
        lo = gi - PRE_V
        while lo < gi and agent_arr[lo] != agent_arr[gi]:
            lo += 1
        rows["V_pre"].append(float(cs[gi] - cs[max(lo, 0)]))
        xn = -1
        for k in range(gi, gi + nw):
            if first_repo[k] != -1:
                xn = int(first_repo[k])
                break
        rows["X_next"].append(xn)
        e_end = gi + min(EARLY, nw)
        tset = set().union(*touched[gi:e_end]) if e_end > gi else set()
        rows["openA"].append(bool(a >= 0 and a in tset))
        nm = [r for k in range(gi, e_end) for r in named[k]]
        rows["n_items_named"].append(len(nm))
        rows["S_R"].append(Counter(nm).most_common(1)[0][0] if nm else -1)
        rows["openR"].append(bool(a >= 0 and a in nm))
        lo = max(gi - PRE_C, 0)
        cnt = Counter()
        for k in range(lo, gi):
            if agent_arr[k] == agent_arr[gi]:
                cnt.update(touched[k])
        rows["S_C"].append(cnt.most_common(1)[0][0] if cnt else -1)
    ev = ev.with_columns(**{k: pl.Series(v) for k, v in rows.items()})
    ev = ev.with_columns((pl.col("S_M") == pl.col("A_prev")).and_(pl.col("A_prev") >= 0).alias("openM"),
                         pl.format("G{}", pl.col("goal_no").cast(pl.Utf8).str.zfill(2)).alias("period"))
    pu = pl.read_parquet(SH / "period_units.parquet", columns=["unit_id", "days"]).explode("days").rename(
        {"days": "pt_date"})
    ev = ev.join(pu, on="pt_date", how="left")
    ev = ev.select("etype", "agent", "pt_date", "goal_no", "period", "unit_id", "regime", "t_call", "seq", "pos0",
                   "seg_len", "n_win", "A_prev", "S_M", "S_R", "S_C", "openA", "openM", "openR", "n_items_named",
                   "X_next", "V", "V_pre")
    out.mkdir(parents=True, exist_ok=True)
    tag = "" if not held else "_confirm"
    ev.write_parquet(out / f"events{tag}.parquet", compression="zstd")
    ids.write_parquet(out / "repo_ids.parquet", compression="zstd")
    prov = {"built_by": "hypotheses/H70-artifact-store-semantic-info/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["context_ledger_turns", "context_ledger_items", "work_commits", "work_repos",
                                   "artifact_mentions", "artifacts", "period_units", "roster"]}],
            "params": {"WIN": WIN, "EARLY": EARLY, "PRE_C": PRE_C, "PRE_V": PRE_V, "MIN_WIN": MIN_WIN,
                       "first_day": FIRST_DENSE, "commit_to_call": "first call with t_log >= commit time, <= 10 min",
                       "work_filter": "canonical & ~imported & author_kind==agent & ~automated",
                       "holdout": "masked (holdout_mask + ledger holdout flag)" if not held else "CONFIRMATORY"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (out / ("_provenance.json" if not held else "_provenance_confirm.json")).write_text(json.dumps(prov, indent=1))
    return {"events": ev.height}


if __name__ == "__main__":
    print(build())
