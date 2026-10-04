"""H29 scheme: per-unit exposure rows for the content-pull influence network (no text, no vectors).

  uv run python hypotheses/H29-driver-nodes/scheme/build.py               # all exploratory units (non-holdout)
  uv run python hypotheses/H29-driver-nodes/scheme/build.py --unit G38

Definitions (card, "Observables"; H18's visibility rule, imported unmodified from
hypotheses/H18-attention-dilution/scheme/build.py):
- talk turn tau_n of recipient j: j's n-th chat message of the PT day (chat_core, speaker_kind = agent);
- call start s(tau): j's latest logged turn (actions minus `pause` mirrors, or events_core) before t_tau - 1 s;
- visible set V(tau_n): messages by others that reached j (`exposure`) with s(tau_{n-1}) <= t_m < s(tau_n);
  these are new to tau_n and were not available to tau_{n-1};
- invisible set I(tau_n): messages that reached j with s(tau_n) <= t_m < t_tau_n (posted during tau_n's own model
  call; tau_n cannot have read them). Placebo for the common-topic / conversation-state component (H18's P10 design);
- first talk of each agent-day has no tau_{n-1} and contributes no rows.

Outputs (per unit, in data/processed/H29-driver-nodes/<unit>/):
  turns.parquet  talk_id, agent, pt_date, day_idx, msg (chat_core row of tau_n), prev_msg (row of tau_{n-1}),
                 t_us, s_us, s_prev_us, room, n_room
  rows.parquet   talk_id, msg, kind (0 agent, 1 human, 2 automated), sender, vis (True = V, False = I), ment_j
                 (the message names the recipient)
  msgs.parquet   every chat message on the unit's days: msg, t_us, pt_date, kind, sender, room, mentions (roster)
  meta.json      days, agents, room sizes
Embedding vectors are NOT copied; analysis maps msg -> embedding row through chat_index (storage rule).
Holdout days are dropped before anything is computed unless build_unit(..., allow_holdout=True) is called by
analysis/confirm.py with its flags.
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "2")
os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit, holdout_mask  # noqa: E402

OUT = ROOT / "data/processed/H29-driver-nodes"
LSH = ROOT / "data/processed/shared"
GUARD_S = 1.0
KIND = {"agent": 0, "human": 1, "automated": 2}

# H18's loaders, imported by path under a unique module name (never modified).
_H18 = ROOT / "hypotheses/H18-attention-dilution"
sys.path.insert(0, str(_H18 / "analysis"))
_spec = importlib.util.spec_from_file_location("h18_scheme_build", _H18 / "scheme/build.py")
h18 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(h18)

# Units: goal period split at step changes, same split dates as H01/H12/H22 so results line up.
UNITS = {
    "G37": dict(goal=37, dates=("2026-03-30", "2026-04-02"), role="exploratory (short)", rooms="#best / #rest"),
    "G38": dict(goal=38, dates=("2026-04-02", "2026-04-27"), role="exploratory", rooms="#best / #rest"),
    "G39": dict(goal=39, dates=("2026-04-27", "2026-05-04"), role="exploratory", rooms="#best / #rest (reshuffled)"),
    "G40": dict(goal=40, dates=("2026-05-04", "2026-05-11"), role="exploratory", rooms="merged #universe-coordination"),
    "G41": dict(goal=41, dates=("2026-05-11", "2026-05-18"), role="exploratory", rooms="#best / #rest"),
    "G42": dict(goal=42, dates=("2026-05-18", "2026-05-25"), role="exploratory", rooms="#best / #rest"),
    "G44": dict(goal=44, dates=("2026-05-26", "2026-06-01"), role="exploratory", rooms="#best / #rest"),
    "G51a": dict(goal=51, dates=("2026-07-06", "2026-07-09"), role="exploratory (short)", rooms="#general"),
    "G51b": dict(goal=51, dates=("2026-07-09", "2026-08-05"), role="exploratory", rooms="#general (+isolated 07-09/10)"),
    "G51c": dict(goal=51, dates=("2026-08-05", "2026-08-25"), role="exploratory", rooms="#general + #focus"),
    "G51d": dict(goal=51, dates=("2026-08-25", "2026-09-03"), role="exploratory", rooms="#general"),
    "G51e": dict(goal=51, dates=("2026-09-03", "2026-09-07"), role="exploratory (short)", rooms="#general"),
}
# Round-1b native units (ledger visibility only; analysis/r1b_extra.py): designated / elected leaders.
NATIVE_UNITS = {
    "G26": dict(goal=26, dates=("2026-01-05", "2026-01-10"), role="native (elected leader)", rooms="#general"),
    "G35": dict(goal=35, dates=("2026-03-16", "2026-03-21"), role="native (designated daily leaders)", rooms="#best / #rest"),
}
# Confirmation units (locked holdout; only analysis/confirm.py may build them, with its flags).
HOLDOUT_UNITS = {
    "G47": dict(goal=47, dates=("2026-06-15", "2026-06-22"), role="confirmatory", rooms="see rooms_timeline"),
    "G51tail": dict(goal=51, dates=("2026-09-07", "2026-09-21"), role="confirmatory", rooms="#general"),
    "G45": dict(goal=45, dates=("2026-06-01", "2026-06-08"), role="confirmatory (reuse; disclosure needed)",
                rooms="#best / #rest"),
}


def unit_days(sh, u: dict, allow_holdout: bool = False, only_holdout: bool = False) -> list[str]:
    d0, d1 = u["dates"]
    cal = sh.cal.filter((pl.col("goal_no") == u["goal"]) & (pl.col("pt_date") >= d0) & (pl.col("pt_date") < d1))
    days = sorted(cal["pt_date"].to_list())
    hm = holdout_mask(days, [u["goal"]] * len(days))
    calh = dict(zip(cal["pt_date"].to_list(), cal["holdout"].to_list()))
    held = [m or bool(calh[d]) for d, m in zip(days, hm)]
    if only_holdout:
        return [d for d, h in zip(days, held) if h]
    if allow_holdout:
        return days
    return [d for d, h in zip(days, held) if not h]


def build_unit(sh, name: str, u: dict, allow_holdout: bool = False, only_holdout: bool = False, verbose=True):
    days = unit_days(sh, u, allow_holdout, only_holdout)
    if not days:
        return None
    cal = sh.cal.filter(pl.col("pt_date").is_in(days)).sort("pt_date")
    win = {r["pt_date"]: (int(h18._ns(pl.Series([r["win_start"]]))[0]), int(h18._ns(pl.Series([r["win_end"]]))[0]))
           for r in cal.iter_rows(named=True)}
    t0 = cal["win_start"].min() - dt.timedelta(hours=2)
    t1 = cal["win_end"].max() + dt.timedelta(hours=2)
    chat = sh.chat.filter(pl.col("pt_date").is_in(days))
    tl = h18.room_lookup(sh)
    ros = sh.roster.filter(~pl.col("claude_code"))
    on_roster = {d: [int(r["agent"]) for r in ros.iter_rows(named=True)
                     if r["joined"] <= d and (r["left"] is None or d < r["left"])] for d in days}
    m_t = h18._ns(chat["t"])
    m_msg = chat["msg"].to_numpy()
    m_kind = chat["speaker_kind"].cast(pl.Utf8).replace_strict(KIND, default=3).to_numpy().astype(np.int8)
    m_sender = chat["agent"].fill_null(-1).to_numpy().astype(np.int16)
    m_day = chat["pt_date"].to_numpy()
    m_ment = [set(x or []) for x in chat["mentions_roster"].to_list()]
    m_room = chat["room"].fill_null(-1).to_numpy().astype(np.int16)
    pos = {int(x): i for i, x in enumerate(m_msg)}
    expo = {}
    for (a,), ex in sh.exposure.filter(pl.col("msg").is_in(m_msg)).group_by(["agent"], maintain_order=True):
        idx = np.array([pos[int(x)] for x in ex["msg"].to_numpy()], dtype=np.int64)
        expo[int(a)] = idx[np.argsort(m_t[idx], kind="stable")]
    turns = h18.turn_times(sh, t0, t1)
    g_us = int(GUARD_S * 1e6)
    day_idx = {d: i for i, d in enumerate(days)}
    trows, rrows = [], []
    tid = 0
    for a, idx in expo.items():
        if a in sh.cc:
            continue
        tt = turns.get(a, np.zeros(0, dtype=np.int64))
        own = np.where((m_kind == 0) & (m_sender == a))[0]
        for d in days:
            if a not in on_roster[d] or not len(tt):
                continue
            ws_us, _ = win[d]
            own_d = own[m_day[own] == d]
            if len(own_d) < 2:
                continue
            ex_d = idx[(m_day[idx] == d) & (m_sender[idx] != a)]
            ex_t = m_t[ex_d]
            own_t = m_t[own_d]
            j = np.searchsorted(tt, own_t - g_us, side="left") - 1
            s = np.where(j >= 0, tt[np.clip(j, 0, None)], -1)
            s = np.where(s >= ws_us - int(3600e6), s, -1)
            rooms_now = h18.room_at(tl, a, own_t)
            R = np.stack([h18.room_at(tl, b, own_t) for b in on_roster[d]])
            nroom = (R == rooms_now[None, :]).sum(0).astype(np.int16)
            for n in range(1, len(own_d)):
                sp, sc = s[n - 1], s[n]
                if sp < 0 or sc < 0 or sc < sp:
                    continue
                lo, hi = np.searchsorted(ex_t, sp, "left"), np.searchsorted(ex_t, sc, "left")
                ihi = np.searchsorted(ex_t, own_t[n], "left")
                trows.append((tid, a, d, day_idx[d], int(m_msg[own_d[n]]), int(m_msg[own_d[n - 1]]), int(own_t[n]),
                              int(sc), int(sp), int(rooms_now[n]), int(nroom[n])))
                for q in ex_d[lo:hi]:
                    rrows.append((tid, int(m_msg[q]), int(m_kind[q]), int(m_sender[q]), True, a in m_ment[q]))
                for q in ex_d[hi:ihi]:
                    rrows.append((tid, int(m_msg[q]), int(m_kind[q]), int(m_sender[q]), False, a in m_ment[q]))
                tid += 1
    if not trows:
        return None
    turns_df = pl.DataFrame(trows, orient="row", schema={
        "talk_id": pl.Int32, "agent": pl.Int16, "pt_date": pl.Utf8, "day_idx": pl.Int16, "msg": pl.UInt32,
        "prev_msg": pl.UInt32, "t_us": pl.Int64, "s_us": pl.Int64, "s_prev_us": pl.Int64, "room": pl.Int16,
        "n_room": pl.Int16})
    rows_df = pl.DataFrame(rrows, orient="row", schema={
        "talk_id": pl.Int32, "msg": pl.UInt32, "kind": pl.Int8, "sender": pl.Int16, "vis": pl.Boolean,
        "ment_j": pl.Boolean})
    msgs_df = pl.DataFrame({"msg": m_msg.astype(np.uint32), "t_us": m_t, "pt_date": m_day, "kind": m_kind,
                            "sender": m_sender, "room": m_room}).with_columns(
        pl.Series("mentions", [sorted(x) for x in m_ment], dtype=pl.List(pl.Int16)))
    agents = sorted(set(turns_df["agent"].to_list()))
    meta = dict(unit=name, goal=u["goal"], days=days, n_days=len(days), agents=agents, n_agents=len(agents),
                roster_size={d: len(on_roster[d]) for d in days},
                median_n_room=float(turns_df["n_room"].median()), rooms=u["rooms"], role=u["role"])
    if verbose:
        nv = rows_df.filter(pl.col("vis")).height
        ni = rows_df.filter(~pl.col("vis")).height
        print(f"{name}: {len(days)} days, {len(agents)} recipients, {turns_df.height} turns, {nv} visible rows, "
              f"{ni} invisible rows, median n_room {meta['median_n_room']:.0f}", flush=True)
    return dict(turns=turns_df, rows=rows_df, msgs=msgs_df, meta=meta)


def build_unit_ledger(sh, name: str, u: dict, allow_holdout: bool = False, only_holdout: bool = False, verbose=True):
    """Round 1b (2026-10-04): the same turns / rows / msgs tables with the DQ1 context ledger's visibility rule
    instead of H18's call-start rule (which mislabels 65-70% of "invisible" messages: PAUSE windows, long tool calls,
    first calls of the day).

    - talk turn tau_n of recipient j: j's n-th chat message of the PT day, matched to the model call that produced it
      (AGENT_TALK event time between the call's t_first and t_log; DQ2's `ledger_call_starts` rule); s(tau) = that
      call's context-assembly time `call_windows.t_call`;
    - visible set V(tau_n): the ledger items (message, recipient j) whose receiving call lies after tau_{n-1}'s call
      and up to and including tau_n's call, i.e. messages posted in j's room in [t_call(c_{n-1}), t_call(c_n));
    - invisible set I(tau_n): items of the call right after c_n that were posted before tau_n itself (during tau_n's
      own generation). Under the ledger these are all strictly invisible (no 30-s call-window filter is needed);
    - turns whose call equals the previous talk's call contribute no rows."""
    days = unit_days(sh, u, allow_holdout, only_holdout)
    if not days:
        return None
    chat = sh.chat.filter(pl.col("pt_date").is_in(days))
    tl = h18.room_lookup(sh)
    ros = sh.roster.filter(~pl.col("claude_code"))
    on_roster = {d: [int(r["agent"]) for r in ros.iter_rows(named=True)
                     if r["joined"] <= d and (r["left"] is None or d < r["left"])] for d in days}
    m_t = h18._ns(chat["t"])
    m_msg = chat["msg"].to_numpy()
    m_kind = chat["speaker_kind"].cast(pl.Utf8).replace_strict(KIND, default=3).to_numpy().astype(np.int8)
    m_sender = chat["agent"].fill_null(-1).to_numpy().astype(np.int16)
    m_day = chat["pt_date"].to_numpy()
    m_ment = [set(x or []) for x in chat["mentions_roster"].to_list()]
    m_room = chat["room"].fill_null(-1).to_numpy().astype(np.int16)
    pos_by_id = {mid: i for i, mid in enumerate(chat["message_id"].to_list())}
    # calls of the unit's days
    cw = (pl.scan_parquet(LSH / "call_windows.parquet").filter(pl.col("pt_date").is_in(days))
          .select("turn_id", "agent", "pt_date", "t_call", "t_first", "t_log").collect().sort("agent", "t_call"))
    if not allow_holdout and cw.height:
        hm = holdout_mask(cw["pt_date"].unique().to_list(), [u["goal"]] * cw["pt_date"].n_unique())
        assert not any(hm), "holdout day in ledger calls"
    # talk turn -> its call (DQ2 rule)
    ev = (sh.ev.filter(pl.col("pt_date").is_in(days) & (pl.col("action_type") == "AGENT_TALK")).select("t", "agent"))
    evt = pl.read_parquet(LSH / "events_core.parquet", columns=["t", "message_id", "action_type"]).filter(
        pl.col("action_type") == "AGENT_TALK").select("message_id", pl.col("t").alias("t_ev"))
    talks = (chat.filter(pl.col("speaker_kind").cast(pl.Utf8) == "agent").select("msg", "message_id", "agent", "t", "pt_date")
             .join(evt, on="message_id", how="left").with_columns(pl.col("t_ev").fill_null(pl.col("t"))).sort("t_ev"))
    j = talks.join_asof(cw.sort("t_first").select("agent", "turn_id", "t_call", "t_first", "t_log"), left_on="t_ev",
                        right_on="t_first", by="agent", strategy="backward")
    j = j.with_columns(pl.when(pl.col("t_ev") <= pl.col("t_log")).then(pl.col("turn_id")).otherwise(None).alias("turn_id"))
    n_unmatched = int(j["turn_id"].is_null().sum())
    j = j.filter(pl.col("turn_id").is_not_null())
    # call order per agent
    cw = cw.with_columns(pl.int_range(pl.len()).over("agent").alias("cpos"))
    cpos = dict(zip(cw["turn_id"].to_list(), cw["cpos"].to_list()))
    ctime = dict(zip(cw["turn_id"].to_list(), h18._ns(cw["t_call"]).tolist()))
    calls_by_agent = {int(a): g["turn_id"].to_numpy() for (a,), g in cw.group_by(["agent"], maintain_order=True)}
    # ledger items of these calls
    it = (pl.scan_parquet(LSH / "context_ledger_items.parquet").filter(pl.col("turn_id").is_in(cw["turn_id"].implode()))
          .select("turn_id", "message_id", "uncertain").collect())
    items = {}
    for tid, g in it.group_by(["turn_id"]):
        idx = [pos_by_id[x] for x in g["message_id"].to_list() if x in pos_by_id]
        items[int(tid[0])] = (np.array(idx, np.int64), g["uncertain"].to_numpy()[[k for k, x in enumerate(g["message_id"].to_list()) if x in pos_by_id]])
    day_idx = {d: i for i, d in enumerate(days)}
    trows, rrows = [], []
    tid_out = 0
    n_same_call = 0
    for (a, d), g in j.sort("t_ev").group_by(["agent", "pt_date"], maintain_order=True):
        a = int(a)
        if a in sh.cc or a not in on_roster.get(d, []):
            continue
        g = g.sort("t_ev")
        if g.height < 2:
            continue
        tids = g["turn_id"].to_numpy()
        tmsg = g["msg"].to_numpy()
        tt = h18._ns(g["t"])
        rooms_now = h18.room_at(tl, a, tt)
        R = np.stack([h18.room_at(tl, b, tt) for b in on_roster[d]])
        nroom = (R == rooms_now[None, :]).sum(0).astype(np.int16)
        calls = calls_by_agent[a]
        for n in range(1, len(tids)):
            cp, cn = cpos[int(tids[n - 1])], cpos[int(tids[n])]
            if cn <= cp:
                n_same_call += 1
                continue
            trows.append((tid_out, a, d, day_idx[d], int(tmsg[n]), int(tmsg[n - 1]), int(tt[n]), int(ctime[int(tids[n])]),
                          int(ctime[int(tids[n - 1])]), int(rooms_now[n]), int(nroom[n])))
            for c in calls[cp + 1: cn + 1]:
                ix, unc = items.get(int(c), (np.zeros(0, np.int64), np.zeros(0, bool)))
                for q, uu in zip(ix, unc):
                    if m_sender[q] == a:
                        continue
                    rrows.append((tid_out, int(m_msg[q]), int(m_kind[q]), int(m_sender[q]), True, a in m_ment[q], bool(uu)))
            if cn + 1 < len(calls):
                ix, unc = items.get(int(calls[cn + 1]), (np.zeros(0, np.int64), np.zeros(0, bool)))
                for q, uu in zip(ix, unc):
                    if m_sender[q] == a or m_t[q] >= tt[n]:
                        continue
                    rrows.append((tid_out, int(m_msg[q]), int(m_kind[q]), int(m_sender[q]), False, a in m_ment[q], bool(uu)))
            tid_out += 1
    if not trows:
        return None
    turns_df = pl.DataFrame(trows, orient="row", schema={
        "talk_id": pl.Int32, "agent": pl.Int16, "pt_date": pl.Utf8, "day_idx": pl.Int16, "msg": pl.UInt32,
        "prev_msg": pl.UInt32, "t_us": pl.Int64, "s_us": pl.Int64, "s_prev_us": pl.Int64, "room": pl.Int16,
        "n_room": pl.Int16})
    rows_df = pl.DataFrame(rrows, orient="row", schema={
        "talk_id": pl.Int32, "msg": pl.UInt32, "kind": pl.Int8, "sender": pl.Int16, "vis": pl.Boolean,
        "ment_j": pl.Boolean, "uncertain": pl.Boolean})
    msgs_df = pl.DataFrame({"msg": m_msg.astype(np.uint32), "t_us": m_t, "pt_date": m_day, "kind": m_kind,
                            "sender": m_sender, "room": m_room}).with_columns(
        pl.Series("mentions", [sorted(x) for x in m_ment], dtype=pl.List(pl.Int16)))
    agents = sorted(set(turns_df["agent"].to_list()))
    meta = dict(unit=name, goal=u["goal"], days=days, n_days=len(days), agents=agents, n_agents=len(agents),
                roster_size={d: len(on_roster[d]) for d in days}, median_n_room=float(turns_df["n_room"].median()),
                rooms=u["rooms"], role=u["role"], visibility="context ledger (DQ1)", talk_unmatched_to_call=n_unmatched,
                turns_same_call_as_previous=n_same_call)
    if verbose:
        nv = rows_df.filter(pl.col("vis")).height
        ni = rows_df.filter(~pl.col("vis")).height
        print(f"{name} [ledger]: {len(days)} days, {len(agents)} recipients, {turns_df.height} turns, {nv} visible rows, "
              f"{ni} invisible rows, unmatched talks {n_unmatched}, same-call turns {n_same_call}", flush=True)
    return dict(turns=turns_df, rows=rows_df, msgs=msgs_df, meta=meta)


def write_unit(name: str, res: dict, root: Path = OUT):
    d = root / name
    d.mkdir(parents=True, exist_ok=True)
    for k in ("turns", "rows", "msgs"):
        res[k].write_parquet(d / f"{k}.parquet", compression="zstd", compression_level=9)
    (d / "meta.json").write_text(json.dumps(res["meta"], indent=1))


def write_provenance(units: list[str], root: Path = OUT, extra: dict | None = None):
    root.mkdir(parents=True, exist_ok=True)
    prov = {"built_by": "hypotheses/H29-driver-nodes/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["shared/calendar", "shared/chat_core", "shared/chat_mentions_clean",
                                   "shared/exposure", "shared/events_core", "shared/actions", "shared/roster",
                                   "shared/rooms_timeline"]}],
            "code_imported": ["hypotheses/H18-attention-dilution/scheme/build.py (Shared, turn_times, room_lookup, "
                              "room_at; unmodified)"],
            "params": {"guard_s": GUARD_S, "units": units, "holdout": "excluded (calendar.holdout | holdout_mask)",
                       **(extra or {})},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (root / "_provenance.json").write_text(json.dumps(prov, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--unit", default=None)
    ap.add_argument("--data", default="r1", choices=["r1", "r1b"],
                    help="r1: H18 call-start visibility (round 1); r1b: DQ1 context-ledger visibility -> OUT/r1b/")
    a = ap.parse_args()
    allu = {**UNITS, **(NATIVE_UNITS if a.data == "r1b" else {})}
    names = [a.unit] if a.unit else list(allu)
    for n in names:
        if n not in allu:
            raise SystemExit(f"{n} is not an exploratory unit (holdout units are built only by analysis/confirm.py)")
    t = time.time()
    sh = h18.Shared()
    print(f"loaded shared tables {time.time() - t:.0f}s", flush=True)
    root = OUT if a.data == "r1" else OUT / "r1b"
    for n in names:
        res = (build_unit if a.data == "r1" else build_unit_ledger)(sh, n, allu[n])
        if res is not None:
            write_unit(n, res, root=root)
    write_provenance(list(UNITS), root=root,
                     extra=None if a.data == "r1" else {"visibility": "DQ1 context ledger (call_windows, context_ledger_items)"})
    print(f"done {time.time() - t:.0f}s")


if __name__ == "__main__":
    main()
