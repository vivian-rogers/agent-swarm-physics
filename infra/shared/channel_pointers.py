"""Scramble events and their channel pointers (semantic-information rows): the ledger-call frame, H70's events, H87's
added pointers and H84's per-search call frame.

Moved from H70 (`scheme/build.py`), H87 (`scheme/build.py`) and H84 (`scheme/build.py`: `load_calls`,
`build_search_calls`); round-3 consolidation, STANDARDS §8, 2026-10-04. The rules are unchanged (verified exactly);
the hypothesis copies stay in place. Search rows come from `infra/shared/search_events.py`.

Ledger-call frame (`load_calls`, H70's rule): context_ledger_turns with ctx_mode in {cu, chat}, the Claude Code agent
excluded, pt_date >= 2026-02-09 (#30: DQ4 work commits are dense from here on; H84 instead keeps regime III only),
sorted by (agent, t_first); seq = call index in the agent-day; resets = reset_consol | reset_session | first_of_day |
seq == 0; seg / pos0 / seg_len / day_len; g = global row index (the call id every pointer uses).

Events (`build_events`, H70): F forced erasure (first call after reset_forced; regime III, cu), P pseudo-erasure (call 21
of a segment with >= 40 calls; regime III, cu), N night (first call of the agent-day), PN mid-day placebo (the call
nearest the day's middle with >= 20 calls before and after it). Window = the event call and the next 19 calls (F/P stop
at the next reset, N/PN at the day end). Pointers (work_repos row ids; -1 none): A_prev (last agent work commit before
the event, <= 7 d), S_M (most recent intention naming a repo, <= 24 h), S_R (repo most named by chat items received
in calls 1-5), S_C (repo touched most in the agent's 10 previous calls); openA / openM / openR; outcomes X_next, V, V_pre.

Added pointers (`add_pointers`, H87): S_G / S_H (agent / human ledger items naming a repo in calls 1-5) with counts and
open flags; S_Q / openQ / n_search / n_search_named (the agent's history searches in calls 1-5); V40 / n_win40;
mem_chars (memory size at the event: memory_stats rows with lines_removed > 0, as-of <= 7 d); day_in_goal, newgoal,
continuation (#40, the #39 -> #40 continuation). `events.parquet` = H87's events_plus (H70's 23 columns first).

Per-search frame (`search_calls`, H84): each search mapped to its regime-III call (search_events.map_to_calls), with
S_Q (modal answer repo), A_prev, X_next, V, V_pre, n_win (call-scale window), ctx_pos, unit_id.

Holdout. Default: held-out calls are dropped (holdout_mask and the ledger flag) and every auxiliary table (work commits,
intentions, memory rows, search rows) keeps non-holdout rows only. `include_holdout=True` (CLI `--include-holdout`)
needs an explicit day list: calls of those days only, and auxiliary rows that are non-holdout or on a listed day. It is
for frozen confirm scripts behind their own guard; the CLI refuses it without
`--i-understand-this-uses-the-locked-holdout`, `--dates`, `--search` (a search_events.py confirm table) and an `--out`
folder outside data/processed/shared/. `aux="source"` reproduces the hypothesis copies' auxiliary rule instead
(H70/H87 default: intentions and memory rows unfiltered; held=True: commits unfiltered too). Units: a day listed in two
period units (2026-06-29: 50a/50b; 2025-06-18) gets the unit whose start is the latest <= the row's time (H70 and H84
join units on pt_date and would duplicate that day's rows).

Outputs (default build): data/processed/shared/channel_pointers/ events.parquet, repo_ids.parquet, search_calls.parquet

Usage: uv run python infra/shared/channel_pointers.py            (needs search_events.parquet; build_all step)
       uv run python infra/shared/channel_pointers.py --verify   (vs H70 events/repo_ids, H87 events_plus, H84
                                                                  search_calls; the include_holdout path on a stand-in)
       uv run python infra/shared/channel_pointers.py --include-holdout --i-understand-this-uses-the-locked-holdout \
              --dates 2026-06-01 2026-07-07 --search <confirm>/search_events.parquet --out <confirm folder> [--only-holdout]
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from collections import Counter  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import OUT as SH, REVISION, ROOT, git_commit, holdout_mask  # noqa: E402
import search_events as SE  # noqa: E402

OUT = SH / "channel_pointers"
ACK = "--i-understand-this-uses-the-locked-holdout"
WIN, EARLY, PRE_C, PRE_V, MIN_WIN, WIN40 = 20, 5, 10, 20, 10, 40
FIRST_DENSE = "2026-02-09"
TZ = "America/Los_Angeles"
H70_COLS = ["etype", "agent", "pt_date", "goal_no", "period", "unit_id", "regime", "t_call", "seq", "pos0", "seg_len",
            "n_win", "A_prev", "S_M", "S_R", "S_C", "openA", "openM", "openR", "n_items_named", "X_next", "V", "V_pre"]


def log(*a):
    print(f"[{dt.datetime.now():%H:%M:%S}]", *a, flush=True)


_KEEP_TIES = False   # verify only: keep the tied modal repos as list columns (__ties_<col>)


def _mode(lst: list) -> tuple[int, list]:
    """Modal repo id with a deterministic tie-break (smallest id) and the tied set. The hypothesis copies used
    Counter.most_common, whose ties follow the row order of an unordered join, so tied values varied between runs."""
    if not lst:
        return -1, []
    c = Counter(lst)
    m = max(c.values())
    t = sorted(k for k, v in c.items() if v == m)
    return t[0], t


# ---------------------------------------------------------------------------------------------- holdout helpers
def _hm(df: pl.DataFrame) -> pl.Series:
    """common.holdout_mask per row, computed once per distinct (pt_date, goal_no)."""
    key = df.select("pt_date", pl.col("goal_no").cast(pl.Int64).fill_null(-1).alias("__g"))
    u = key.unique()
    u = u.with_columns(pl.Series("__h", holdout_mask(u["pt_date"].to_list(), u["__g"].to_list()), dtype=pl.Boolean))
    return key.join(u, on=["pt_date", "__g"], how="left", maintain_order="left")["__h"]


def admit_aux(df: pl.DataFrame, include_holdout: bool, days: list[str] | None, t: str = "t") -> pl.DataFrame:
    """Auxiliary-row rule: non-holdout rows (holdout_mask on the row's PT day and goal, and the table's own `holdout`
    flag if it has one), plus, with include_holdout, every row on a listed day. Row order kept."""
    x = df
    if "pt_date" not in x.columns:
        x = x.with_columns(pl.col(t).dt.convert_time_zone(TZ).dt.date().cast(pl.Utf8).alias("pt_date"))
    if "goal_no" not in x.columns:
        cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "goal_no"])
        x = x.join(cal, on="pt_date", how="left", maintain_order="left")
    keep = ~_hm(x)
    if "holdout" in x.columns:
        keep = keep & ~x["holdout"].fill_null(False)
    if include_holdout:
        keep = keep | x["pt_date"].is_in(days)
    return df.filter(keep)


def unit_map(t_col: str = "t") -> pl.DataFrame:
    """(pt_date, unit_start, unit_id) for the as-of unit lookup."""
    pu = pl.read_parquet(SH / "period_units.parquet", columns=["unit_id", "start", "days"]).explode("days")
    return pu.rename({"days": "pt_date", "start": "unit_start"}).sort("pt_date", "unit_start")


def attach_unit(df: pl.DataFrame, t_col: str) -> pl.DataFrame:
    """unit_id by pt_date; a day in two units gets the latest unit starting <= t (else the first). Row order kept."""
    um = unit_map()
    multi = um.group_by("pt_date").len().filter(pl.col("len") > 1)["pt_date"].to_list()
    one = um.filter(~pl.col("pt_date").is_in(multi)).select("pt_date", "unit_id")
    x = df.with_row_index("__r").join(one, on="pt_date", how="left", maintain_order="left")
    sel = x.filter(pl.col("pt_date").is_in(multi))
    if sel.height:
        rows = []
        for r, ptd, t in zip(sel["__r"].to_list(), sel["pt_date"].to_list(), sel[t_col].to_list()):
            u = um.filter(pl.col("pt_date") == ptd)
            ok = u.filter(pl.col("unit_start") <= t)
            rows.append((r, (ok if ok.height else u)["unit_id"][-1 if ok.height else 0]))
        fix = pl.DataFrame(rows, schema={"__r": pl.UInt32, "__u": pl.Utf8}, orient="row")
        x = x.join(fix, on="__r", how="left", maintain_order="left").with_columns(pl.coalesce("__u", "unit_id").alias("unit_id")).drop("__u")
    return x.sort("__r").drop("__r")


# ---------------------------------------------------------------------------------------------- inputs
def repo_map() -> tuple[pl.DataFrame, pl.DataFrame]:
    """(repo name <-> int id), (artifact id -> repo id) for repos, their files and their sites (H70 repo_map)."""
    wr = pl.read_parquet(SH / "work_repos.parquet", columns=["repo", "artifacts"]).sort("repo")
    wr = wr.with_row_index("rid").with_columns(pl.col("rid").cast(pl.Int32))
    ids = wr.select("rid", "repo")
    a2r = wr.select("rid", "artifacts").explode("artifacts").rename({"artifacts": "artifact"}).drop_nulls()
    art = pl.read_parquet(SH / "artifacts.parquet", columns=["artifact", "kind", "parent"])
    child = (art.filter(pl.col("parent").is_not_null()).select("artifact", "parent")
             .join(a2r.rename({"artifact": "parent"}), on="parent", how="inner").select("artifact", "rid"))
    amap = pl.concat([a2r.select("artifact", "rid"), child]).unique("artifact", keep="first")
    return ids, amap


def load_calls(days: list[str] | None = None, include_holdout: bool = False, regime: str | None = None,
               first_day: str | None = FIRST_DENSE) -> pl.DataFrame:
    """H70's ledger-call frame (regime='III', first_day=None gives H84's)."""
    if include_holdout:
        assert days, "include_holdout needs an explicit day list"
    ros = pl.read_parquet(SH / "roster.parquet", columns=["agent", "claude_code"])
    cc = ros.filter(pl.col("claude_code"))["agent"].to_list()
    t = pl.read_parquet(SH / "context_ledger_turns.parquet",
                        columns=["turn_id", "agent", "pt_date", "goal_no", "regime", "holdout", "t_call", "t_first",
                                 "t_log", "kind", "ctx_mode", "reset_consol", "reset_forced", "reset_session",
                                 "first_of_day", "ctx_pos"])
    f = pl.col("ctx_mode").is_in(["cu", "chat"]) & ~pl.col("agent").is_in(cc)
    if first_day is not None:
        f = f & (pl.col("pt_date") >= first_day)
    if regime is not None:
        f = f & (pl.col("regime").cast(pl.Utf8) == regime)
    t = t.filter(f)
    if include_holdout:
        t = t.filter(pl.col("pt_date").is_in(days))
    else:
        t = t.filter(~_hm(t) & ~pl.col("holdout"))
        assert not t["holdout"].any()
        if days is not None:
            t = t.filter(pl.col("pt_date").is_in(days))
    t = t.with_columns(pl.col("regime").cast(pl.Utf8)).sort("agent", "t_first")
    t = t.with_columns(pl.int_range(pl.len()).over("agent", "pt_date").alias("seq"))
    rst = pl.col("reset_consol") | pl.col("reset_session") | pl.col("first_of_day") | (pl.col("seq") == 0)
    t = t.with_columns(rst.alias("is_reset"))
    t = t.with_columns(pl.col("is_reset").cast(pl.Int32).cum_sum().over("agent", "pt_date").alias("seg"))
    t = t.with_columns(pl.int_range(pl.len()).over("agent", "pt_date", "seg").alias("pos0"),
                       pl.len().over("agent", "pt_date", "seg").alias("seg_len"),
                       pl.len().over("agent", "pt_date").alias("day_len"))
    return t.with_row_index("g").with_columns(pl.col("g").cast(pl.Int64))


def work_commits(ids: pl.DataFrame, include_holdout: bool = False, days: list[str] | None = None,
                 aux: str = "admitted") -> pl.DataFrame:
    """DQ4 agent work commits (canonical, not imported, agent-authored, not automated): t, agent, rid (-2 = repo not in
    work_repos), pt_date; sorted by t."""
    wc = pl.read_parquet(SH / "work_commits.parquet",
                         columns=["repo", "t", "author_agent", "author_kind", "canonical", "imported", "automated",
                                  "holdout", "pt_date", "goal_no"])
    wc = wc.filter(pl.col("canonical") & ~pl.col("imported") & (pl.col("author_kind") == "agent")
                   & ~pl.col("automated") & pl.col("author_agent").is_not_null())
    if aux == "source":
        if not include_holdout:
            wc = wc.filter(~_hm(wc) & ~pl.col("holdout"))
    else:
        wc = admit_aux(wc, include_holdout, days)
    return (wc.with_columns(pl.col("repo").cast(pl.Utf8)).join(ids, on="repo", how="left")
            .select("t", pl.col("author_agent").alias("agent"), pl.col("rid").fill_null(-2).cast(pl.Int32), "pt_date")
            .sort("t"))


# ---------------------------------------------------------------------------------------------- H70 events
def build_events(calls: pl.DataFrame, ids: pl.DataFrame, amap: pl.DataFrame, wc: pl.DataFrame,
                 include_holdout: bool = False, days: list[str] | None = None, aux: str = "admitted") -> pl.DataFrame:
    """H70 scheme/build.py `build` (events part). Returns H70's 23 columns plus g, seg, day_len (sorted by g)."""
    keys_log = calls.select("g", "agent", "t_log").sort("t_log")
    keys_first = calls.select("g", "agent", "t_first", "t_log").sort("t_first")
    n = calls.height
    agent_arr = calls["agent"].to_numpy()
    wcs = wc.select("t", "agent", "rid")
    wm = wcs.join_asof(keys_log, left_on="t", right_on="t_log", by="agent", strategy="forward", tolerance="10m",
                       check_sortedness=False).drop_nulls("g")
    n_work = np.zeros(n, dtype=np.int32)
    np.add.at(n_work, wm["g"].to_numpy(), 1)
    first_repo = np.full(n, -1, dtype=np.int32)
    fr = wm.sort("t").group_by("g").agg(pl.col("rid").first())
    first_repo[fr["g"].to_numpy()] = fr["rid"].to_numpy()
    am = pl.read_parquet(SH / "artifact_mentions.parquet", columns=["artifact", "t", "agent", "source", "message_id"])
    act = (am.filter(pl.col("source") == "action").join(amap, on="artifact", how="inner")
           .select("t", "agent", "rid").sort("t"))
    act = act.join_asof(keys_first, left_on="t", right_on="t_first", by="agent", strategy="backward",
                        check_sortedness=False)
    act = act.filter(pl.col("g").is_not_null() & (pl.col("t") <= pl.col("t_log") + pl.duration(seconds=1)))
    touched: list[set] = [set() for _ in range(n)]
    for g, r in zip(act["g"].to_list(), act["rid"].to_list()):
        touched[g].add(r)
    ch = (am.filter((pl.col("source") == "chat") & pl.col("message_id").is_not_null())
          .join(amap, on="artifact", how="inner").select("message_id", "rid").unique())
    items = (pl.scan_parquet(SH / "context_ledger_items.parquet").select("turn_id", "message_id")
             .filter(pl.col("message_id").is_in(ch["message_id"].unique().implode())).collect())
    items = items.join(ch, on="message_id", how="inner").join(calls.select("turn_id", "g"), on="turn_id", how="inner")
    named: list[list] = [[] for _ in range(n)]
    for g, r in zip(items["g"].to_list(), items["rid"].to_list()):
        named[g].append(r)
    it = am.filter(pl.col("source") == "intention")
    if aux != "source":
        it = admit_aux(it, include_holdout, days)
    it = (it.join(amap, on="artifact", how="inner")
          .select(pl.col("t").alias("t_int"), "agent", pl.col("rid").alias("S_M"))
          .unique(["agent", "t_int"], keep="first", maintain_order=True).sort("t_int"))
    c = calls
    is_r3cu = (c["regime"] == "III") & (c["ctx_mode"] == "cu")
    F = c.filter(is_r3cu & c["reset_forced"]).select("g").with_columns(pl.lit("F").alias("etype"))
    P = c.filter(is_r3cu & (pl.col("pos0") == 20) & (pl.col("seg_len") >= 40)).select("g").with_columns(
        pl.lit("P").alias("etype"))
    N = c.filter(pl.col("seq") == 0).select("g").with_columns(pl.lit("N").alias("etype"))
    cand = c.filter((pl.col("seq") >= 20) & (pl.col("day_len") - pl.col("seq") >= 20))
    PN = (cand.with_columns((pl.col("seq") - pl.col("day_len") / 2).abs().alias("dmid"))
          .sort("dmid").group_by("agent", "pt_date").agg(pl.col("g").first()).select("g")
          .with_columns(pl.lit("PN").alias("etype")))
    ev = pl.concat([F, P, N, PN]).join(c.select("g", "agent", "pt_date", "goal_no", "regime", "t_call", "seg",
                                                "seg_len", "pos0", "day_len", "seq"), on="g")
    log("events", ev.group_by("etype").len().sort("etype").rows())
    ev = ev.sort("t_call").join_asof(wcs.rename({"t": "t_c", "rid": "A_prev"}), left_on="t_call", right_on="t_c",
                                     by="agent", strategy="backward", tolerance="7d", check_sortedness=False)
    ev = ev.join_asof(it, left_on="t_call", right_on="t_int", by="agent", strategy="backward", tolerance="24h",
                      check_sortedness=False)
    ev = ev.with_columns(pl.col("A_prev").fill_null(-1), pl.col("S_M").fill_null(-1)).sort("g")
    g_arr, pos0, segl = ev["g"].to_numpy(), ev["pos0"].to_numpy(), ev["seg_len"].to_numpy()
    dayscale = ev["etype"].is_in(["N", "PN"]).to_numpy()
    seqs, dlen, A = ev["seq"].to_numpy(), ev["day_len"].to_numpy(), ev["A_prev"].to_numpy()
    cs = np.concatenate([[0], np.cumsum(n_work)])
    rows = {k: [] for k in ("n_win", "V", "V_pre", "X_next", "openA", "S_R", "openR", "S_C", "n_items_named")}
    tie_rows = {"S_R": []}
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
        mo, ties = _mode(nm)
        rows["S_R"].append(mo)
        tie_rows["S_R"].append(ties)
        rows["openR"].append(bool(a >= 0 and a in nm))
        lo = max(gi - PRE_C, 0)
        cnt = Counter()
        for k in range(lo, gi):
            if agent_arr[k] == agent_arr[gi]:
                cnt.update(touched[k])
        rows["S_C"].append(cnt.most_common(1)[0][0] if cnt else -1)
    ev = ev.with_columns(**{k: pl.Series(v) for k, v in rows.items()})
    if _KEEP_TIES:
        ev = ev.with_columns(**{f"__ties_{k}": pl.Series(v, dtype=pl.List(pl.Int64)) for k, v in tie_rows.items()})
    ev = ev.with_columns((pl.col("S_M") == pl.col("A_prev")).and_(pl.col("A_prev") >= 0).alias("openM"),
                         pl.format("G{}", pl.col("goal_no").cast(pl.Utf8).str.zfill(2)).alias("period"))
    ev = attach_unit(ev, "t_call")
    return ev.select(*H70_COLS, "g", *([c for c in ev.columns if c.startswith("__ties_")]))


# ---------------------------------------------------------------------------------------------- H87 pointers
def add_pointers(ev: pl.DataFrame, calls: pl.DataFrame, amap: pl.DataFrame, wc: pl.DataFrame, se: pl.DataFrame,
                 include_holdout: bool = False, days: list[str] | None = None, aux: str = "admitted") -> pl.DataFrame:
    """H87 scheme/build.py `build` on an event frame with g (from build_events). Returns events_plus (sorted by g)."""
    n = calls.height
    chk = ev.join(calls.select("g", pl.col("t_call").alias("__tc")), on="g", how="left")
    assert chk["__tc"].is_null().sum() == 0 and (chk["__tc"] == chk["t_call"]).all(), "event -> call mapping failed"
    am = pl.read_parquet(SH / "artifact_mentions.parquet", columns=["artifact", "t", "agent", "source", "message_id"])
    ch = (am.filter((pl.col("source") == "chat") & pl.col("message_id").is_not_null())
          .join(amap, on="artifact", how="inner").select("message_id", "rid").unique())
    items = (pl.scan_parquet(SH / "context_ledger_items.parquet").select("turn_id", "message_id", "kind")
             .filter(pl.col("kind").is_in(["agent", "human"])).collect())
    items = items.join(calls.select("turn_id", "g"), on="turn_id", how="inner")
    cnt = {k: np.zeros(n, dtype=np.int32) for k in ("agent", "human")}
    for k in cnt:
        np.add.at(cnt[k], items.filter(pl.col("kind") == k)["g"].to_numpy(), 1)
    named = items.join(ch, on="message_id", how="inner")
    nm = {k: [[] for _ in range(n)] for k in ("agent", "human")}
    for g, r, k in zip(named["g"].to_list(), named["rid"].to_list(), named["kind"].cast(pl.Utf8).to_list()):
        nm[k][g].append(r)
    sm = SE.map_to_calls(se, calls)
    n_search = np.zeros(n, dtype=np.int32)
    np.add.at(n_search, sm["g"].to_numpy(), 1)
    srids: list[list] = [[] for _ in range(n)]
    for g, rs in zip(sm["g"].to_list(), sm["ans_rids"].to_list()):
        srids[g].extend(rs or [])
    log("searches mapped", sm.height, "of", se.height)
    keys_log = calls.select("g", "agent", "t_log").sort("t_log")
    wm = wc.select("t", "agent").join_asof(keys_log, left_on="t", right_on="t_log", by="agent", strategy="forward",
                                           tolerance="10m", check_sortedness=False).drop_nulls("g")
    n_work = np.zeros(n, dtype=np.int32)
    np.add.at(n_work, wm["g"].to_numpy(), 1)
    cs = np.concatenate([[0], np.cumsum(n_work)])
    rows = {k: [] for k in ("S_G", "openG", "n_agent_items", "n_agent_named", "S_H", "openH", "n_human_items",
                            "n_human_named", "S_Q", "openQ", "n_search", "n_search_named", "V40", "n_win40")}
    tie_rows = {"S_G": [], "S_H": [], "S_Q": []}
    dayscale = ev["etype"].is_in(["N", "PN"]).to_numpy()
    ag_arr, pd_arr = calls["agent"].to_numpy(), calls["pt_date"].to_numpy()
    for gi, nw, a, ds, sl, p0 in zip(ev["g"].to_numpy(), ev["n_win"].to_numpy(), ev["A_prev"].to_numpy(), dayscale,
                                     ev["seg_len"].to_numpy(), ev["pos0"].to_numpy()):
        e_end = gi + min(EARLY, nw)
        for kk, key in (("G", "agent"), ("H", "human")):
            lst = [r for k in range(gi, e_end) for r in nm[key][k]]
            mo, ties = _mode(lst)
            rows[f"S_{kk}"].append(mo)
            tie_rows[f"S_{kk}"].append(ties)
            rows[f"open{kk}"].append(bool(a >= 0 and a in lst))
            rows[f"n_{key}_items"].append(int(cnt[key][gi:e_end].sum()))
            rows[f"n_{key}_named"].append(len(lst))
        q = [r for k in range(gi, e_end) for r in srids[k]]
        mo, ties = _mode(q)
        rows["S_Q"].append(mo)
        tie_rows["S_Q"].append(ties)
        rows["openQ"].append(bool(a >= 0 and a in q))
        rows["n_search"].append(int(n_search[gi:e_end].sum()))
        rows["n_search_named"].append(len(q))
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
    if _KEEP_TIES:
        ev = ev.with_columns(**{f"__ties_{k}": pl.Series(v, dtype=pl.List(pl.Int64)) for k, v in tie_rows.items()})
    ms = pl.read_parquet(SH / "memory_stats.parquet", columns=["t", "agent", "n_chars", "lines_removed"])
    if aux != "source":
        ms = admit_aux(ms, include_holdout, days)
    ms = (ms.filter(pl.col("lines_removed") > 0)
          .select(pl.col("t").alias("t_mem"), "agent", pl.col("n_chars").alias("mem_chars")).sort("t_mem"))
    ev = ev.sort("t_call").join_asof(ms, left_on="t_call", right_on="t_mem", by="agent", strategy="backward",
                                     tolerance="7d", check_sortedness=False)
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "goal_no"])
    din = (cal.filter(pl.col("goal_no").is_not_null()).sort("pt_date")
           .with_columns(pl.int_range(1, pl.len() + 1).over("goal_no").alias("day_in_goal"))
           .select("pt_date", "day_in_goal"))
    ev = ev.join(din, on="pt_date", how="left").with_columns(
        ((pl.col("day_in_goal") == 1) & (pl.col("goal_no") != 40)).alias("newgoal"),
        ((pl.col("day_in_goal") == 1) & (pl.col("goal_no") == 40)).alias("continuation"))
    ev = ev.drop("t_mem").sort("g")
    return ev.select([c for c in ev.columns if not c.startswith("__ties_")] + [c for c in ev.columns if c.startswith("__ties_")])


# ---------------------------------------------------------------------------------------------- H84 per-search frame
def search_calls(calls: pl.DataFrame, work: pl.DataFrame, srch: pl.DataFrame) -> pl.DataFrame:
    """H84 scheme/build.py `build_search_calls` (calls = load_calls(regime='III', first_day=None))."""
    s = SE.map_to_calls(srch, calls)
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
    pos0, segl = calls["pos0"].to_numpy(), calls["seg_len"].to_numpy()
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
        pl.col("ans_rids").list.eval(pl.element().mode().min()).list.first().fill_null(-1).alias("S_Q"))
    if _KEEP_TIES:
        s = s.with_columns(pl.col("ans_rids").list.eval(pl.element().mode().sort()).cast(pl.List(pl.Int64))
                           .alias("__ties_S_Q"))
    s = attach_unit(s, "t")
    return s.select("agent", "pt_date", "goal_no", "unit_id", "t", "g", "ans_chars", "query_chars", "S_Q",
                    "n_ans_rids", "A_prev", "X_next", "V", "V_pre", "n_win", "ctx_pos",
                    *([c for c in s.columns if c.startswith("__ties_")])).filter(pl.col("n_win") >= 1)


# ---------------------------------------------------------------------------------------------- driver
def build_all(se: pl.DataFrame, days: list[str] | None = None, include_holdout: bool = False,
              aux: str = "admitted") -> dict:
    """events (H70 + H87 columns), repo_ids, search_calls. se = search rows (search_events.scan or a confirm table)."""
    if include_holdout:
        assert days, "include_holdout needs an explicit day list"
    if aux != "source":
        se = admit_aux(se, include_holdout, days)
    ids, amap = repo_map()
    calls = load_calls(days, include_holdout)
    log("calls", calls.height)
    wc = work_commits(ids, include_holdout, days, aux)
    ev = build_events(calls, ids, amap, wc, include_holdout, days, aux)
    ev = add_pointers(ev, calls, amap, wc, se, include_holdout, days, aux)
    calls3 = load_calls(days, include_holdout, regime="III", first_day=None)
    sc = search_calls(calls3, wc, se)
    log("events", ev.height, "search calls", sc.height, "of", se.height)
    return {"events": ev, "repo_ids": ids, "search_calls": sc}


def write(res: dict, out: Path, include_holdout: bool, extra: dict | None = None):
    out.mkdir(parents=True, exist_ok=True)
    for k, df in res.items():
        df.write_parquet(out / f"{k}.parquet", compression="zstd")
    prov = {"built_by": "infra/shared/channel_pointers.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["context_ledger_turns", "context_ledger_items", "work_commits", "work_repos",
                                   "artifact_mentions", "artifacts", "period_units", "roster", "memory_stats",
                                   "calendar", "search_events (infra/shared/search_events.py)"]}],
            "params": {"WIN": WIN, "EARLY": EARLY, "PRE_C": PRE_C, "PRE_V": PRE_V, "MIN_WIN": MIN_WIN, "WIN40": WIN40,
                       "first_day": FIRST_DENSE, "commit_to_call": "first call with t_log >= commit time, <= 10 min",
                       "work_filter": "canonical & ~imported & author_kind==agent & ~automated",
                       "holdout": ("INCLUDED for the listed days (confirm build)" if include_holdout else
                                   "excluded: calls (holdout_mask + ledger flag) and every auxiliary table"),
                       "source": "H70 scheme/build.py, H87 scheme/build.py, H84 scheme/build.py build_search_calls",
                       "rows": {k: v.height for k, v in res.items()}, **(extra or {})},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (out / "_provenance.json").write_text(json.dumps(prov, indent=1))


TIE_COLS = ("S_R", "S_G", "S_H", "S_Q")


def _cmp(a: pl.DataFrame, b: pl.DataFrame) -> str:
    """a = source table, b = shared rebuild (may carry __ties_<col>). Exact on every column of a, except the modal
    columns, where a differing value counts as a tie when it is one of b's tied modal repos."""
    ties = {c: b[f"__ties_{c}"] for c in TIE_COLS if f"__ties_{c}" in b.columns}
    b = b.select([c for c in b.columns if not c.startswith("__ties_")])
    if a.columns != b.columns:
        return f"columns differ: {sorted(set(a.columns) ^ set(b.columns))}"
    if a.schema != b.schema:
        return f"dtypes differ: {[(c, a.schema[c], b.schema[c]) for c in a.columns if a.schema[c] != b.schema[c]]}"
    if a.height != b.height:
        return f"rows {a.height} vs {b.height}"
    bad, tied = [], []
    for c in a.columns:
        if a[c].equals(b[c]):
            continue
        neq = (a[c].cast(pl.Utf8).fill_null("~") != b[c].cast(pl.Utf8).fill_null("~")).to_numpy()
        if c in ties:
            idx = np.flatnonzero(neq)
            av, tl = a[c].to_list(), ties[c].to_list()
            n_tie = sum(1 for i in idx if tl[i] is not None and av[i] in tl[i])
            tied.append(f"{c} {n_tie}")
            if n_tie < len(idx):
                bad.append(f"{c} ({len(idx) - n_tie} not ties)")
        else:
            bad.append(f"{c} ({int(neq.sum())})")
    if bad:
        return "differ: " + ", ".join(bad) + (f"; tie-breaks: {', '.join(tied)}" if tied else "")
    return "identical" + (f" up to tie-breaks ({', '.join(tied)} rows hold another tied modal repo)" if tied else "")


def verify() -> dict:
    """(1) Rebuild with the hypotheses' own auxiliary rule (aux='source') vs H70 events.parquet / repo_ids.parquet, H87
    events_plus.parquet and H84 search_calls.parquet (read-only): identical except where the source broke a modal tie
    differently. (2) The default build (auxiliary rows non-holdout only) vs the same tables: the remaining differences
    are values that came from held-out auxiliary rows. (3) The include_holdout path with every non-holdout day listed
    reproduces the default build exactly."""
    global _KEEP_TIES
    t0 = time.time()
    res, ok = {}, True
    se = SE.scan() if not SE.OUT.exists() else pl.read_parquet(SE.OUT)
    res["search_rows"] = f"{se.height} ({'shared table' if SE.OUT.exists() else 'fresh scan'})"
    _KEEP_TIES = True
    try:
        src_built = build_all(se, aux="source")
        built = build_all(se)
    finally:
        _KEEP_TIES = False
    srcs = {"H70_events": (ROOT / "data/processed/H70-artifact-store-semantic-info/events.parquet",
                           lambda r: r["events"].select(*H70_COLS, "__ties_S_R")),
            "H70_repo_ids": (ROOT / "data/processed/H70-artifact-store-semantic-info/repo_ids.parquet",
                             lambda r: r["repo_ids"]),
            "H87_events_plus": (ROOT / "data/processed/H87-kappa-channel-table/events_plus.parquet",
                                lambda r: r["events"]),
            "H84_search_calls": (ROOT / "data/processed/H84-search-outage-memory-scramble/search_calls.parquet",
                                 lambda r: r["search_calls"])}
    for name, (p, view) in srcs.items():
        if not p.exists():
            res[name] = "source table absent"
            continue
        src = pl.read_parquet(p)
        r = _cmp(src, view(src_built))
        res[name + " (aux=source)"] = r
        ok &= r.startswith("identical")
        res[name + " (default: holdout-free aux rows)"] = _cmp(src, view(built))
    ldays = load_calls()["pt_date"].unique().sort().to_list()
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "goal_no", "holdout"])
    c = cal.filter(pl.col("pt_date").is_in(ldays))
    assert not any(holdout_mask(c["pt_date"].to_list(), c["goal_no"].fill_null(-1).to_list())) and not c["holdout"].any()
    alt = build_all(se, days=ldays, include_holdout=True)
    plain = build_all(se)
    same = {k: ("identical" if plain[k].equals(alt[k]) else _cmp(plain[k], alt[k])) for k in plain}
    res["include_holdout_path_on_all_non_holdout_days"] = same
    ok &= all(v == "identical" for v in same.values())
    res["ok"] = bool(ok)
    res["seconds"] = round(time.time() - t0)
    print(json.dumps(res, indent=1), flush=True)
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--include-holdout", action="store_true", help="confirm scripts only (see docstring)")
    ap.add_argument(ACK, dest="ack", action="store_true")
    ap.add_argument("--dates", nargs=2, metavar=("START", "END_EXCL"))
    ap.add_argument("--only-holdout", action="store_true", help="with --include-holdout: list only held-out days")
    ap.add_argument("--search", help="search rows for --include-holdout (search_events.py confirm output)")
    ap.add_argument("--out")
    a = ap.parse_args()
    if a.verify:
        sys.exit(0 if verify()["ok"] else 1)
    if a.include_holdout:
        if not a.ack or not a.dates or not a.out or not a.search:
            sys.exit(f"refusing: --include-holdout needs {ACK}, --dates, --search and --out (confirm scripts only)")
        out = Path(a.out).resolve()
        if out == SH.resolve() or SH.resolve() in out.parents:
            sys.exit("refusing: held-out rows may not be written under data/processed/shared/")
        cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "goal_no", "holdout", "window_s"])
        cal = cal.filter(pl.col("pt_date").is_between(a.dates[0], a.dates[1], closed="left") & (pl.col("window_s") > 0))
        days = cal["pt_date"].to_list()
        if a.only_holdout:
            hm = holdout_mask(days, cal["goal_no"].fill_null(-1).to_list())
            days = [d for d, m, h in zip(days, hm, cal["holdout"].to_list()) if m or h]
        se = pl.read_parquet(a.search)
        res = build_all(se, days=days, include_holdout=True)
        write(res, out, True, {"dates": a.dates, "only_holdout": a.only_holdout, "days": days})
        print({k: v.height for k, v in res.items()}, "->", out)
        return
    if not SE.OUT.exists():
        sys.exit(f"missing {SE.OUT}: run infra/shared/search_events.py first")
    res = build_all(pl.read_parquet(SE.OUT))
    write(res, OUT, False)
    print({k: v.height for k, v in res.items()})


if __name__ == "__main__":
    main()
