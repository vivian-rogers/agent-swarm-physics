"""H70 round 2 frames (non-reserved data only): nights for the kickoff row (R2-K), regime-III calls around the
2026-03-31/04-01 history-search outage for the search row (R2-Q), and #51 forced erasures with private roles (R4).

Round-1 files are untouched. Writes data/processed/H70-artifact-store-semantic-info/r2/{nights, qcalls, g51_events,
roles}.parquet and r2/_provenance.json (codes and repo ids only; no text).

Shared code used (infra/shared, never another hypothesis folder): channel_pointers (repo_map, work_commits, admit_aux,
attach-free helpers), search_events (map_to_calls), common (holdout_mask, paths).

Deterministic rules (the round-1 sources had unstable tie-breaks; infra/README Known issues):
  calls are sorted by (agent, t_first, turn_id) (t_first is not unique within an agent);
  commits are de-duplicated per (agent, t) to the smallest repo id before the last-commit lookup (A_prev);
  a call's first commit (X_next) is the earliest mapped commit, ties to the smallest repo id;
  commit -> call mapping uses call keys sorted by (t_log, g);
  modal answer repo of a call's searches: the most frequent id, ties to the smallest id.
Reserved data: calls drop held-out days (holdout_mask and the ledger flag; asserted); every auxiliary table (work commits,
search rows) keeps non-reserved rows only (channel_pointers' default `admit_aux`).

Usage: uv run python hypotheses/H70-artifact-store-semantic-info/scheme/build_r2.py [--counts]
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
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
import channel_pointers as CP  # noqa: E402
import search_events as SE  # noqa: E402
from common import OUT as SH, REVISION, git_commit, holdout_mask, parse_ts, rows  # noqa: E402

OUT = ROOT / "data/processed/H70-artifact-store-semantic-info/r2"
WIN, PRE_V, MIN_WIN = 20, 20, 10
FIRST_DENSE = "2026-02-09"
Q_DAYS = ("2026-03-24", "2026-04-14")            # regime-III panel around the outage (inclusive)
OUTAGE = ("2026-03-31", "2026-04-01")
RECOVERY = ("2026-04-02", "2026-04-03")
G51_LAST = "2026-09-06"                          # #51 non-reserved head ends before the 09-07 reserved window
FAILED_CHARS = 150                               # H84's failed-answer rule


def log(*a):
    print(f"[{dt.datetime.now():%H:%M:%S}]", *a, flush=True)


# ---------------------------------------------------------------------------------------------- calls
def load_calls() -> pl.DataFrame:
    """channel_pointers.load_calls' rule (cu/chat, Claude Code excluded, from 2026-02-09, reserved days dropped) with a
    deterministic sort (agent, t_first, turn_id)."""
    ros = pl.read_parquet(SH / "roster.parquet", columns=["agent", "claude_code"])
    cc = ros.filter(pl.col("claude_code"))["agent"].to_list()
    t = pl.read_parquet(SH / "context_ledger_turns.parquet",
                        columns=["turn_id", "agent", "pt_date", "goal_no", "regime", "holdout", "t_call", "t_first",
                                 "t_log", "kind", "ctx_mode", "reset_consol", "reset_forced", "reset_session",
                                 "first_of_day", "ctx_pos"])
    t = t.filter(pl.col("ctx_mode").is_in(["cu", "chat"]) & ~pl.col("agent").is_in(cc) & (pl.col("pt_date") >= FIRST_DENSE))
    t = t.filter(~CP._hm(t) & ~pl.col("holdout"))
    assert not t["holdout"].any()
    assert not any(holdout_mask(t["pt_date"].unique().to_list(), [None] * t["pt_date"].n_unique())), "reserved NE day"
    t = t.with_columns(pl.col("regime").cast(pl.Utf8)).sort("agent", "t_first", "turn_id")
    t = t.with_columns(pl.int_range(pl.len()).over("agent", "pt_date").alias("seq"))
    rst = pl.col("reset_consol") | pl.col("reset_session") | pl.col("first_of_day") | (pl.col("seq") == 0)
    t = t.with_columns(rst.alias("is_reset"))
    t = t.with_columns(pl.col("is_reset").cast(pl.Int32).cum_sum().over("agent", "pt_date").alias("seg"))
    t = t.with_columns(pl.int_range(pl.len()).over("agent", "pt_date", "seg").alias("pos0"),
                       pl.len().over("agent", "pt_date", "seg").alias("seg_len"),
                       pl.len().over("agent", "pt_date").alias("day_len"))
    return t.with_row_index("g").with_columns(pl.col("g").cast(pl.Int64))


def commit_arrays(calls: pl.DataFrame, wc: pl.DataFrame):
    """n_work per call and the first commit's repo per call (ties at equal t -> smallest repo id)."""
    n = calls.height
    keys_log = calls.select("g", "agent", "t_log").sort("t_log", "g")
    wm = wc.select("t", "agent", "rid").sort("t", "rid").join_asof(
        keys_log, left_on="t", right_on="t_log", by="agent", strategy="forward", tolerance="10m",
        check_sortedness=False).drop_nulls("g")
    n_work = np.zeros(n, dtype=np.int32)
    np.add.at(n_work, wm["g"].to_numpy(), 1)
    first_repo = np.full(n, -1, dtype=np.int32)
    fr = wm.group_by("g").agg(pl.col("rid").sort_by("t", "rid").first())
    first_repo[fr["g"].to_numpy()] = fr["rid"].to_numpy()
    return n_work, first_repo


def a_prev(ev: pl.DataFrame, wc: pl.DataFrame) -> pl.DataFrame:
    """A_prev = repo of the agent's last work commit at or before t_call (<= 7 d); ties at equal t -> smallest id."""
    wd = wc.group_by("agent", "t").agg(pl.col("rid").min().alias("A_prev")).sort("t").rename({"t": "t_c"})
    out = ev.sort("t_call").join_asof(wd, left_on="t_call", right_on="t_c", by="agent", strategy="backward",
                                      tolerance="7d", check_sortedness=False)
    return out.with_columns(pl.col("A_prev").fill_null(-1)).drop("t_c")


def outcomes(calls: pl.DataFrame, g_idx: np.ndarray, nwin: np.ndarray, n_work, first_repo) -> dict:
    """V (commits in the window, scaled to 20 calls), V_pre (commits in the agent's previous 20 calls), X_next."""
    agent_arr = calls["agent"].to_numpy()
    cs = np.concatenate([[0], np.cumsum(n_work)])
    V, Vp, X = [], [], []
    for gi, nw in zip(g_idx, nwin):
        V.append(float(cs[gi + nw] - cs[gi]) * WIN / nw if nw > 0 else np.nan)
        lo = gi - PRE_V
        while lo < gi and agent_arr[max(lo, 0)] != agent_arr[gi]:
            lo += 1
        Vp.append(float(cs[gi] - cs[max(lo, 0)]))
        xn = -1
        for k in range(gi, gi + nw):
            if first_repo[k] != -1:
                xn = int(first_repo[k])
                break
        X.append(xn)
    return {"V": V, "V_pre": Vp, "X_next": X}


# ---------------------------------------------------------------------------------------------- R2-K: nights
def build_nights(calls, wc, n_work, first_repo) -> pl.DataFrame:
    """First call of every agent-day (#30 on, all regimes); window = 20 calls within the day. Adds the previous night
    of the same agent (goal, date), the boundary label and the kind (within / new_goal / continuation)."""
    N = calls.filter(pl.col("seq") == 0).select("g", "agent", "pt_date", "goal_no", "regime", "t_call", "day_len")
    nw = np.minimum(WIN, N["day_len"].to_numpy())
    o = outcomes(calls, N["g"].to_numpy(), nw, n_work, first_repo)
    N = N.with_columns(pl.Series("n_win", nw), **{k: pl.Series(v) for k, v in o.items()})
    N = a_prev(N, wc).sort("agent", "pt_date")
    N = N.with_columns(pl.col("goal_no").shift(1).over("agent").alias("goal_prev"),
                       pl.col("pt_date").shift(1).over("agent").alias("date_prev"))
    N = N.with_columns((pl.col("pt_date").str.to_date() - pl.col("date_prev").str.to_date()).dt.total_days()
                       .alias("gap_d"))
    N = N.with_columns(
        pl.when(pl.col("goal_prev").is_null() | (pl.col("gap_d") > 7)).then(pl.lit("none"))
        .when(pl.col("goal_prev") == pl.col("goal_no")).then(pl.lit("within"))
        .when((pl.col("goal_prev") == 39) & (pl.col("goal_no") == 40)).then(pl.lit("continuation"))
        .otherwise(pl.lit("new_goal")).alias("kind"),
        pl.format("{}->{}", pl.col("goal_prev"), pl.col("goal_no")).alias("boundary"))
    return N.select("agent", "pt_date", "goal_no", "regime", "t_call", "n_win", "A_prev", "X_next", "V", "V_pre",
                    "goal_prev", "date_prev", "gap_d", "kind", "boundary").sort("agent", "pt_date")


# ---------------------------------------------------------------------------------------------- R2-Q: search outage
def build_qcalls(calls, wc, n_work, first_repo, se: pl.DataFrame) -> pl.DataFrame:
    """Every regime-III call on the panel days with >= 10 window calls (window = 20 calls, truncated at the next
    reset), flagged for history searches mapped to it (search_events.map_to_calls), with the modal answer repo S_Q."""
    sm = SE.map_to_calls(se, calls)
    per = {}
    for g, rids, ch in zip(sm["g"].to_list(), sm["ans_rids"].to_list(), sm["ans_chars"].to_list()):
        d = per.setdefault(g, {"r": [], "c": []})
        d["r"].extend(rids or [])
        d["c"].append(ch)
    C = calls.filter((pl.col("regime") == "III") & (pl.col("pt_date") >= Q_DAYS[0]) & (pl.col("pt_date") <= Q_DAYS[1]))
    nw = np.minimum(WIN, (C["seg_len"] - C["pos0"]).to_numpy())
    C = C.with_columns(pl.Series("n_win", nw)).filter(pl.col("n_win") >= MIN_WIN)
    g_idx = C["g"].to_numpy()
    o = outcomes(calls, g_idx, C["n_win"].to_numpy(), n_work, first_repo)
    n_s, SQ, fail, med = [], [], [], []
    for g in g_idx:
        d = per.get(int(g))
        if d is None:
            n_s.append(0); SQ.append(-1); fail.append(False); med.append(None)
            continue
        n_s.append(len(d["c"]))
        if d["r"]:
            c = Counter(d["r"])
            m = max(c.values())
            SQ.append(min(k for k, v in c.items() if v == m))
        else:
            SQ.append(-1)
        fail.append(all((x or 0) < FAILED_CHARS for x in d["c"]))
        med.append(float(np.median([x or 0 for x in d["c"]])))
    C = C.with_columns(pl.Series("n_search", n_s, dtype=pl.Int32), pl.Series("S_Q", SQ, dtype=pl.Int32),
                       pl.Series("failed", fail), pl.Series("ans_chars_med", med, dtype=pl.Float64),
                       **{k: pl.Series(v) for k, v in o.items()})
    C = C.with_columns(
        pl.when(pl.col("pt_date").is_in(list(OUTAGE))).then(pl.lit("outage"))
        .when(pl.col("pt_date").is_in(list(RECOVERY))).then(pl.lit("recovery"))
        .otherwise(pl.lit("placebo")).alias("day_class"))
    C = a_prev(C, wc)
    C = C.with_columns((pl.col("n_search") > 0).alias("is_search"),
                       ((pl.col("S_Q") == pl.col("A_prev")) & (pl.col("A_prev") >= 0)).alias("openQ"))
    return C.select("g", "agent", "pt_date", "goal_no", "t_call", "pos0", "n_win", "day_class", "is_search", "n_search",
                    "S_Q", "openQ", "failed", "ans_chars_med", "A_prev", "X_next", "V", "V_pre").sort("g")


# ---------------------------------------------------------------------------------------------- R4: #51 roles
def load_roles() -> pl.DataFrame:
    """Raw agent_goals -> (agent code, role code, start UTC). Role code = rank of the role's short name among the sorted
    distinct short names (two agents with the same role share a code). Codes only."""
    ros = pl.read_parquet(SH / "roster.parquet", columns=["agent", "agent_id"])
    a2c = dict(zip(ros["agent_id"].to_list(), ros["agent"].to_list()))
    recs = [(a2c.get(r["agent_id"]), (r.get("short_name") or r.get("name") or "").strip().lower(),
             parse_ts(r.get("start_time"))) for r in rows("agent_goals")]
    names = sorted({n for _, n, _ in recs})
    code = {n: i for i, n in enumerate(names)}
    df = pl.DataFrame([(a, code[n], t) for a, n, t in recs if a is not None],
                      schema={"agent": pl.Int8, "role": pl.Int16, "t_role": pl.Datetime("us", "UTC")}, orient="row")
    return df.sort("t_role")


def build_g51(calls, wc, n_work, first_repo, roles: pl.DataFrame) -> pl.DataFrame:
    """#51 non-reserved forced erasures (F, first call after reset_forced) and pseudo-erasures (P, call 21 of a no-reset
    segment of >= 40 calls), regime III cu; window 20 calls truncated at the next reset (>= 10 calls)."""
    c = calls.filter((pl.col("goal_no") == 51) & (pl.col("pt_date") <= G51_LAST) & (pl.col("regime") == "III")
                     & (pl.col("ctx_mode") == "cu"))
    F = c.filter(pl.col("reset_forced")).with_columns(pl.lit("F").alias("etype"))
    P = c.filter((pl.col("pos0") == 20) & (pl.col("seg_len") >= 40)).with_columns(pl.lit("P").alias("etype"))
    E = pl.concat([F, P]).sort("g")
    nw = np.minimum(WIN, (E["seg_len"] - E["pos0"]).to_numpy())
    E = E.with_columns(pl.Series("n_win", nw)).filter(pl.col("n_win") >= MIN_WIN)
    o = outcomes(calls, E["g"].to_numpy(), E["n_win"].to_numpy(), n_work, first_repo)
    E = E.with_columns(**{k: pl.Series(v) for k, v in o.items()})
    E = a_prev(E, wc)
    E = E.sort("t_call").join_asof(roles.with_columns(pl.col("agent").cast(E["agent"].dtype)), left_on="t_call",
                                   right_on="t_role", by="agent", strategy="backward", check_sortedness=False)
    E = E.with_columns(pl.col("role").fill_null(-1))
    return E.select("g", "etype", "agent", "pt_date", "t_call", "pos0", "n_win", "role", "A_prev", "X_next", "V",
                    "V_pre").sort("g")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ids, amap = CP.repo_map()
    calls = load_calls()
    log("calls", calls.height)
    wc = CP.work_commits(ids)            # non-reserved auxiliary rows only (admit_aux)
    n_work, first_repo = commit_arrays(calls, wc)
    se = CP.admit_aux(pl.read_parquet(SH / "search_events.parquet"), False, None)
    assert not se["holdout"].any()
    nights = build_nights(calls, wc, n_work, first_repo)
    q = build_qcalls(calls, wc, n_work, first_repo, se)
    roles = load_roles()
    g51 = build_g51(calls, wc, n_work, first_repo, roles)
    for name, df in (("nights", nights), ("qcalls", q), ("g51_events", g51), ("roles", roles)):
        df.write_parquet(OUT / f"{name}.parquet", compression="zstd")
        log(name, df.height)
    prov = {"built_by": "hypotheses/H70-artifact-store-semantic-info/scheme/build_r2.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["context_ledger_turns", "work_commits", "work_repos", "artifacts", "roster",
                                   "search_events (infra/shared/search_events.py)", "raw agent_goals (codes only)"]}],
            "params": {"WIN": WIN, "PRE_V": PRE_V, "MIN_WIN": MIN_WIN, "first_day": FIRST_DENSE, "Q_DAYS": Q_DAYS,
                       "OUTAGE": OUTAGE, "RECOVERY": RECOVERY, "G51_LAST": G51_LAST, "FAILED_CHARS": FAILED_CHARS,
                       "reserved": "excluded: calls (holdout_mask + ledger flag) and every auxiliary table",
                       "tie_breaks": "calls (agent, t_first, turn_id); A_prev and X_next ties -> smallest repo id; "
                                     "modal answer repo ties -> smallest id",
                       "rows": {"nights": nights.height, "qcalls": q.height, "g51_events": g51.height}},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))
    if "--counts" in sys.argv:
        counts(nights, q, g51)


def counts(nights, q, g51):
    """Structure counts only (no outcome statistic): used to write the round-2 predictions."""
    k = nights.filter(pl.col("A_prev") >= 0)
    print("nights with A_prev by kind:", k.group_by("kind").len().sort("kind").rows())
    print("new-goal boundaries:", k.filter(pl.col("kind") == "new_goal").group_by("boundary").len().sort("boundary").rows())
    print("qcalls by day class:", q.group_by("day_class").agg(pl.len(), pl.col("is_search").sum(),
                                                             pl.col("agent").n_unique()).sort("day_class").rows())
    s = q.filter(pl.col("is_search"))
    print("search calls by day class and agent:",
          s.group_by("day_class", "agent").len().sort("day_class", "agent").rows())
    print("search calls naming a repo (S_Q >= 0) by day class:",
          s.group_by("day_class").agg((pl.col("S_Q") >= 0).sum()).sort("day_class").rows())
    e = g51.filter(pl.col("A_prev") >= 0)
    print("g51 events with A_prev:", e.group_by("etype").len().sort("etype").rows(),
          "agents", e["agent"].n_unique(), "roles", e.filter(pl.col("role") >= 0)["role"].n_unique(),
          "events without a role", e.filter(pl.col("role") < 0).height)
    ra = e.filter(pl.col("role") >= 0).group_by("role").agg(pl.col("agent").n_unique().alias("na"))
    print("roles by number of agents (F/P events with A_prev):", ra.group_by("na").len().sort("na").rows())


if __name__ == "__main__":
    main()
