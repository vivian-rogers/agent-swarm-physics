"""H87 round 2 event frame: finer allocation X (DQ3 behavior state), chat item kinds after an erasure, an in-flight
arm at matched lag, and graded-scramble events (context size k in forced-opened segments).

Round-1 inputs are unchanged (scheme/build.py, events_plus.parquet). This builder reads only shared tables and shared
code (`infra/shared/channel_pointers.py`: load_calls, repo_map, work_commits, admit_aux; `channel_pointers/events.parquet`
for mem_chars and a cross-check). No code or data from another hypothesis folder.

Events (regime III, computer-use calls; reserved data excluded by load_calls and admit_aux):
  F   forced erasure (first call after reset_forced), P pseudo-erasure (call 21 of a no-reset segment >= 40 calls):
      channel_pointers' rules, rebuilt here so every new column is computed on one call frame.
  Fk  graded-scramble events: the call at position k (k = 2, 5, 10, 20) of a segment opened by a forced erasure
      (k = 0 is F itself). At Fk the context holds the last k calls only.
Per event (window = the event call and the next 19, stopped at the next reset; n_win >= 10 is applied in analysis):
  V, V_pre, X_next, A_prev, openA as channel_pointers (V = agent work commits in the window, rate x 20 if truncated).
  S_C (repo touched most in calls -10..-1; ties -> smallest repo id; deterministic).
  X_beh  DQ3 behavior state (argmax of the 11 probabilities, existing labels only) of the agent's first labelled 5-min
         window starting at or after the end of call min(5, n_win) (<= 15 min later); -1 = none.
  S_Cb   behavior state of the agent's last labelled window ending at or before the end of call -1 (<= 15 min); -1 none.
  Chat (agent items from other agents received at the agent's ledger receiving calls 1..5):
         n_ag, n_backlog (received at call 1), n_fresh (calls 2..5), any_ment (item mentions the recipient, ledger flag),
         any_ques (question mark, not a mention), any_stat (neither), any_rel (sender's last work commit repo, <= 7 d
         before posting, equals the recipient's A_prev), n_hum, hum_ment.
  Room rate  n_pre = agent items received in calls -20..-1 (same agent-day).  Before-age  age_before = seconds from the
         latest agent item posted before call 1 started (received at calls <= 1) to the start of call 1 (null = none).
  In-flight arm (matched lag): span S = [start of call 1, start of call 1 + DELTA). R_S = >= 1 agent item posted in S
         and received by call 5; IF_S = items posted in S, none received by call 5 (all in flight at call 5);
         lag_S = lag of the first item posted in S; kind_S = its kind (0 status, 1 question, 2 mention).
  t15 = seconds from the start of call 1 to the start of call 5 (call speed; for the synthetic and a sensitivity).
Search: n_search (calls 1..5) and S_Q from channel_pointers events (joined on g for F and P).

Output: data/processed/H87-kappa-channel-table/r2/events_r2.parquet (codes, ids, counts; no text), _provenance.json.
Usage: uv run python hypotheses/H87-kappa-channel-table/scheme/build_r2.py [--counts]
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
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
from common import OUT as SH, REVISION, git_commit, holdout_mask  # noqa: E402

OUTD = ROOT / "data/processed/H87-kappa-channel-table/r2"
WIN, EARLY, PRE_C, PRE_V = 20, 5, 10, 20
KS = (2, 5, 10, 20)
DELTA_S = 60.0           # in-flight span (s): the median start(call 1) -> start(call 5) is 51-59 s (counts run, before outcomes)
BEH_TOL = dt.timedelta(minutes=15)
STATES = ["plan_coordinate", "execute_task", "research_browse", "communicate_external", "debug_recover",
          "verify_report", "monitor_wait", "self_maintenance", "social", "meta", "idle"]


def log(*a):
    print(f"[{dt.datetime.now():%H:%M:%S}]", *a, flush=True)


def mode_min(cnt: Counter) -> int:
    if not cnt:
        return -1
    m = max(cnt.values())
    return min(k for k, v in cnt.items() if v == m)


def behavior_windows() -> pl.DataFrame:
    b = pl.read_parquet(SH / "behavior_states_v3.parquet",
                        columns=["pt_date", "agent", "t0", "t1", "goal_no", "holdout", "labeled"] + [f"p_{s}" for s in STATES])
    b = b.filter(pl.col("labeled") & ~pl.col("holdout"))
    b = b.filter(~pl.Series(holdout_mask(b["pt_date"].to_list(), b["goal_no"].cast(pl.Int64).fill_null(-1).to_list())))
    P = b.select([f"p_{s}" for s in STATES]).to_numpy()
    code = np.argmax(np.nan_to_num(P, nan=-1.0), axis=1).astype(np.int8)   # ties -> first in STATES order
    return b.select("agent", "t0", "t1").with_columns(pl.Series("beh", code))


def build(counts_only: bool = False) -> pl.DataFrame:
    ids, amap = CP.repo_map()
    calls = CP.load_calls()
    log("calls", calls.height)
    n = calls.height
    wc = CP.work_commits(ids)
    agent_arr = calls["agent"].to_numpy()
    tf = calls["t_first"].dt.epoch("us").to_numpy() / 1e6
    tl = calls["t_log"].dt.epoch("us").to_numpy() / 1e6
    pos0, segl = calls["pos0"].to_numpy(), calls["seg_len"].to_numpy()
    pdate = calls["pt_date"].to_numpy()

    # --- work commits per call (H70 rule: author's first call with t_log >= commit time, <= 10 min)
    keys_log = calls.select("g", "agent", "t_log").sort("t_log")
    wm = wc.select("t", "agent", "rid").join_asof(keys_log, left_on="t", right_on="t_log", by="agent",
                                                   strategy="forward", tolerance="10m",
                                                   check_sortedness=False).drop_nulls("g")
    n_work = np.zeros(n, dtype=np.int32)
    np.add.at(n_work, wm["g"].to_numpy(), 1)
    first_repo = np.full(n, -1, dtype=np.int32)
    fr = wm.sort("t", "rid").group_by("g").agg(pl.col("rid").first())
    first_repo[fr["g"].to_numpy()] = fr["rid"].to_numpy()
    cs = np.concatenate([[0], np.cumsum(n_work)])

    # --- repos touched per call (artifact_mentions, action source)
    keys_first = calls.select("g", "agent", "t_first", "t_log").sort("t_first")
    am = pl.read_parquet(SH / "artifact_mentions.parquet", columns=["artifact", "t", "agent", "source"])
    act = (am.filter(pl.col("source") == "action").join(amap, on="artifact", how="inner")
           .select("t", "agent", "rid").sort("t"))
    act = act.join_asof(keys_first, left_on="t", right_on="t_first", by="agent", strategy="backward",
                        check_sortedness=False)
    act = act.filter(pl.col("g").is_not_null() & (pl.col("t") <= pl.col("t_log") + pl.duration(seconds=1)))
    touched: list[set] = [set() for _ in range(n)]
    for g, r in zip(act["g"].to_list(), act["rid"].to_list()):
        touched[g].add(r)

    # --- events
    c = calls
    r3 = (c["regime"] == "III") & (c["ctx_mode"] == "cu")
    F = c.filter(r3 & c["reset_forced"]).select("g").with_columns(pl.lit("F").alias("etype"), pl.lit(0).alias("k"))
    P = c.filter(r3 & (pl.col("pos0") == 20) & (pl.col("seg_len") >= 40)).select("g").with_columns(
        pl.lit("P").alias("etype"), pl.lit(-1).alias("k"))
    fpos = F["g"].to_numpy()
    assert (pos0[fpos] == 0).all(), "a forced erasure is not the first call of its segment"
    Fk = []
    for k in KS:
        gk = fpos + k
        ok = (gk < n) & (segl[fpos] >= k + 10)
        gk, f0 = gk[ok], fpos[ok]
        ok2 = (agent_arr[gk] == agent_arr[f0]) & (pos0[gk] == k)
        Fk.append(pl.DataFrame({"g": gk[ok2].astype(np.int64)}).with_columns(pl.lit(f"F{k}").alias("etype"),
                                                                             pl.lit(k).alias("k")))
    ev = pl.concat([F.with_columns(pl.col("g").cast(pl.Int64)), P.with_columns(pl.col("g").cast(pl.Int64))] +
                   [f.with_columns(pl.col("k").cast(pl.Int32)) for f in Fk], how="vertical_relaxed")
    ev = ev.join(c.select("g", "agent", "pt_date", "goal_no", "t_call", "seq", "pos0", "seg_len"), on="g").sort("g")
    log("events", ev.group_by("etype").len().sort("etype").rows())
    n_ev = ev.height
    g_arr = ev["g"].to_numpy()
    nwin = np.minimum(WIN, segl[g_arr] - pos0[g_arr]).astype(int)
    t15 = np.array([tf[gi + min(4, nw - 1)] - tf[gi] for gi, nw in zip(g_arr, nwin)])
    if counts_only:
        e2 = ev.with_columns(pl.Series("n_win", nwin), pl.Series("t15", t15))
        e2 = e2.filter(pl.col("n_win") >= 10)
        print(e2.group_by("etype").agg(pl.len(), pl.col("t15").median().alias("t15_med")).sort("etype"))
        return e2

    # A_prev (last work commit before the event call, <= 7 d)
    ev = ev.sort("t_call").join_asof(wc.select(pl.col("t").alias("t_c"), "agent", pl.col("rid").alias("A_prev")),
                                     left_on="t_call", right_on="t_c", by="agent", strategy="backward",
                                     tolerance="7d", check_sortedness=False).drop("t_c")
    ev = ev.with_columns(pl.col("A_prev").fill_null(-1)).sort("g", "etype")
    g_arr = ev["g"].to_numpy()
    A = ev["A_prev"].to_numpy()
    nwin = np.minimum(WIN, segl[g_arr] - pos0[g_arr]).astype(int)
    rows = {k: [] for k in ("n_win", "V", "V_pre", "X_next", "openA", "S_C", "t15", "t_end5", "t_endm1")}
    for gi, nw, a in zip(g_arr, nwin, A):
        rows["n_win"].append(int(nw))
        rows["V"].append(float(cs[gi + nw] - cs[gi]) * WIN / nw if nw > 0 else np.nan)
        lo = gi - PRE_V
        while lo < gi and agent_arr[max(lo, 0)] != agent_arr[gi]:
            lo += 1
        rows["V_pre"].append(float(cs[gi] - cs[max(lo, 0)]))
        xn = -1
        for kk in range(gi, gi + nw):
            if first_repo[kk] != -1:
                xn = int(first_repo[kk])
                break
        rows["X_next"].append(xn)
        e_end = gi + min(EARLY, nw)
        tset = set().union(*touched[gi:e_end]) if e_end > gi else set()
        rows["openA"].append(bool(a >= 0 and a in tset))
        cnt = Counter()
        for kk in range(max(gi - PRE_C, 0), gi):
            if agent_arr[kk] == agent_arr[gi]:
                cnt.update(touched[kk])
        rows["S_C"].append(mode_min(cnt))
        rows["t15"].append(float(tf[gi + min(4, nw - 1)] - tf[gi]) if nw > 0 else np.nan)
        rows["t_end5"].append(float(tl[gi + min(EARLY, nw) - 1]) if nw > 0 else np.nan)
        rows["t_endm1"].append(float(tl[gi - 1]) if gi > 0 and agent_arr[gi - 1] == agent_arr[gi] else np.nan)
    ev = ev.with_columns(**{k: pl.Series(v) for k, v in rows.items()})

    # --- behavior states
    bw = behavior_windows()
    log("labelled behavior windows (non-reserved)", bw.height)
    us = lambda col: pl.from_epoch((pl.col(col) * 1e6).cast(pl.Int64), time_unit="us").dt.replace_time_zone("UTC")
    e5 = ev.select("g", "agent", us("t_end5").alias("tq")).unique("g").drop_nulls("tq").sort("tq")
    xb = e5.join_asof(bw.select("agent", pl.col("t0").alias("tw"), "beh").sort("tw"), left_on="tq", right_on="tw",
                      by="agent", strategy="forward", tolerance=BEH_TOL, check_sortedness=False)
    em = ev.select("g", "agent", us("t_endm1").alias("tq")).unique("g").drop_nulls("tq").sort("tq")
    sb = em.join_asof(bw.select("agent", pl.col("t1").alias("tw"), "beh").sort("tw"), left_on="tq", right_on="tw",
                      by="agent", strategy="backward", tolerance=BEH_TOL, check_sortedness=False)
    ev = (ev.join(xb.select("g", pl.col("beh").alias("X_beh")), on="g", how="left")
          .join(sb.select("g", pl.col("beh").alias("S_Cb")), on="g", how="left")
          .with_columns(pl.col("X_beh").fill_null(-1).cast(pl.Int16), pl.col("S_Cb").fill_null(-1).cast(pl.Int16))
          .sort("g"))

    # --- ledger items (agent and human), post time, question flag, sender's repo
    it = (pl.scan_parquet(SH / "context_ledger_items.parquet")
          .select("turn_id", "message_id", "sender", "kind", "ment")
          .filter(pl.col("kind").is_in(["agent", "human"])).collect())
    it = it.join(calls.select("turn_id", "g", pl.col("agent").alias("recv")), on="turn_id", how="inner")
    it = it.filter(pl.col("sender").is_null() | (pl.col("sender") != pl.col("recv")))
    cc = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t"])
    tq = pl.read_parquet(SH / "text_features.parquet", columns=["message_id", "f_ques"])
    it = (it.join(cc, on="message_id", how="left").join(tq, on="message_id", how="left")
          .with_columns((pl.col("f_ques").fill_null(0) > 0).alias("ques"), pl.col("kind").cast(pl.Utf8)))
    ag = it.filter((pl.col("kind") == "agent") & pl.col("t").is_not_null()).sort("t")
    ag = ag.join_asof(wc.select(pl.col("t").alias("t_c"), pl.col("agent").cast(pl.Int8).alias("sender"),
                                pl.col("rid").alias("srepo")).sort("t_c"),
                      left_on="t", right_on="t_c", by="sender", strategy="backward", tolerance="7d",
                      check_sortedness=False).with_columns(pl.col("srepo").fill_null(-1))
    log("agent items", ag.height, "human items", it.filter(pl.col("kind") == "human").height)
    # per-call lists
    per = {k: [[] for _ in range(n)] for k in ("tp", "kd", "rp")}
    for g, t, m, q, r in zip(ag["g"].to_list(), (ag["t"].dt.epoch("us") / 1e6).to_list(), ag["ment"].to_list(),
                             ag["ques"].to_list(), ag["srepo"].to_list()):
        per["tp"][g].append(t)
        per["kd"][g].append(2 if m else (1 if q else 0))
        per["rp"][g].append(r)
    hu = it.filter(pl.col("kind") == "human")
    n_h = np.zeros(n, dtype=np.int32)
    np.add.at(n_h, hu["g"].to_numpy(), 1)
    h_m = np.zeros(n, dtype=np.int32)
    np.add.at(h_m, hu.filter(pl.col("ment"))["g"].to_numpy(), 1)
    n_ag = np.array([len(x) for x in per["tp"]], dtype=np.int32)

    g_arr, A, nwin = ev["g"].to_numpy(), ev["A_prev"].to_numpy(), ev["n_win"].to_numpy()
    cols = {k: [] for k in ("n_ag", "n_backlog", "n_fresh", "any_ment", "any_ques", "any_stat", "any_rel", "n_hum",
                            "hum_ment", "n_pre", "age_before", "R_S", "IF_S", "lag_S", "kind_S", "n_S")}
    for gi, a, nw in zip(g_arr, A, nwin):
        e_end = gi + min(EARLY, nw)
        kd = [x for kk in range(gi, e_end) for x in per["kd"][kk]]
        rp = [x for kk in range(gi, e_end) for x in per["rp"][kk]]
        cols["n_ag"].append(int(n_ag[gi:e_end].sum()))
        cols["n_backlog"].append(int(n_ag[gi]))
        cols["n_fresh"].append(int(n_ag[gi + 1:e_end].sum()))
        cols["any_ment"].append(2 in kd)
        cols["any_ques"].append(1 in kd)
        cols["any_stat"].append(0 in kd)
        cols["any_rel"].append(bool(a >= 0 and a in rp))
        cols["n_hum"].append(int(n_h[gi:e_end].sum()))
        cols["hum_ment"].append(int(h_m[gi:e_end].sum()) > 0)
        lo = gi - PRE_V
        while lo < gi and not (agent_arr[max(lo, 0)] == agent_arr[gi] and pdate[max(lo, 0)] == pdate[gi]):
            lo += 1
        cols["n_pre"].append(int(n_ag[max(lo, 0):gi].sum()))
        t0 = tf[gi]
        before = [t for kk in range(max(lo, 0), gi + 1) for t in per["tp"][kk] if t < t0]
        cols["age_before"].append(float(t0 - max(before)) if before else None)
        # in-flight span S: items posted in [t0, t0 + DELTA), received at calls 1..min(30, segment end)
        hi = min(gi + 30, gi + int(segl[gi] - pos0[gi]))
        inS = [(t, kk - gi, kdv) for kk in range(gi, hi) for t, kdv in zip(per["tp"][kk], per["kd"][kk])
               if t0 <= t < t0 + DELTA_S]
        if inS:
            read = [x for x in inS if x[1] <= 4]
            first = min(inS)
            cols["R_S"].append(bool(read))
            cols["IF_S"].append(not read)
            cols["lag_S"].append(float(first[0] - t0))
            cols["kind_S"].append(int(first[2]))
            cols["n_S"].append(len(inS))
        else:
            cols["R_S"].append(False)
            cols["IF_S"].append(False)
            cols["lag_S"].append(None)
            cols["kind_S"].append(-1)
            cols["n_S"].append(0)
    ev = ev.with_columns(**{k: pl.Series(k, v) for k, v in cols.items()})

    # --- search pointer, memory size, unit from the shared events (F and P only)
    sh = pl.read_parquet(SH / "channel_pointers/events.parquet",
                         columns=["g", "etype", "S_Q", "openQ", "n_search", "mem_chars", "V", "X_next", "A_prev",
                                  "V_pre", "S_M", "openM", "unit_id", "period"])
    sh = sh.filter(pl.col("etype").is_in(["F", "P"]))
    ev = ev.join(sh.select("g", "S_Q", "openQ", "n_search", "mem_chars", "S_M", "openM", "unit_id", "period",
                           pl.col("V").alias("__V"), pl.col("X_next").alias("__X"), pl.col("A_prev").alias("__A"),
                           pl.col("V_pre").alias("__Vp")), on="g", how="left")
    assert ev.height == n_ev, "row count changed in a join"
    fp = ev.filter(pl.col("etype").is_in(["F", "P"]))
    chk = {c0: float(((fp[c0] == fp[f"__{c1}"]) | (fp[c0].is_nan() & fp[f"__{c1}"].is_nan()) if c0 == "V"
                      else (fp[c0] == fp[f"__{c1}"])).mean())
           for c0, c1 in (("V", "V"), ("X_next", "X"), ("A_prev", "A"), ("V_pre", "Vp"))}
    log("agreement with channel_pointers events (F, P):", chk)
    assert min(chk.values()) > 0.999, chk
    ev = ev.drop("__V", "__X", "__A", "__Vp")
    ev = ev.with_columns(pl.format("G{}", pl.col("goal_no").cast(pl.Utf8).str.zfill(2)).alias("period2"))
    ev = ev.with_columns(pl.coalesce("period", "period2").alias("period")).drop("period2")
    ev = CP.attach_unit(ev.drop("unit_id"), "t_call")
    # reserved-data guard
    hm = holdout_mask(ev["pt_date"].to_list(), ev["goal_no"].cast(pl.Int64).to_list())
    assert not any(hm), "reserved day in the round-2 frame"
    return ev.drop("t_end5", "t_endm1")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--counts", action="store_true")
    a = ap.parse_args()
    ev = build(counts_only=a.counts)
    if a.counts:
        return
    OUTD.mkdir(parents=True, exist_ok=True)
    ev.write_parquet(OUTD / "events_r2.parquet", compression="zstd")
    prov = {"built_by": "hypotheses/H87-kappa-channel-table/scheme/build_r2.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["context_ledger_turns", "context_ledger_items", "work_commits", "work_repos",
                                   "artifact_mentions", "artifacts", "behavior_states_v3", "chat_core",
                                   "text_features", "period_units", "roster",
                                   "channel_pointers/events (infra/shared/channel_pointers.py)"]}],
            "params": {"WIN": WIN, "EARLY": EARLY, "PRE_C": PRE_C, "PRE_V": PRE_V, "KS": KS, "DELTA_S": DELTA_S,
                       "behavior": "argmax of 11 DQ3 v3.1 probabilities; ties -> first in STATES", "states": STATES,
                       "beh_tolerance_min": 15, "reserved": "excluded (load_calls, holdout_mask on windows)",
                       "rows": ev.height},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUTD / "_provenance.json").write_text(json.dumps(prov, indent=1))
    log("wrote", OUTD / "events_r2.parquet", ev.height)


if __name__ == "__main__":
    main()
