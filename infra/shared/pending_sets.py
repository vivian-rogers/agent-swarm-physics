"""Pending sets on the DQ1 context ledger ("ledger k"): per talk call, the chat items the recipient received since its
previous talk call, with mention and DQ2 reply responses; plus timer-wake batches (D2) and in-flight placebo senders.

Moved from H18 (hypotheses/H18-attention-dilution/scheme/build_ledger.py, round 1b; STANDARDS §8, 2026-10-04). The
rules are unchanged; H18's copy stays in place. Users: H18 (dilution exponent), H68 (per-agent dilution mixture) and
their confirm scripts; any attention-budget design on ledger k.

Definitions (H18 card, "Round 1b"):
- talk call: a ledger call (`call_windows`) that produced >= 1 agent chat message (AGENT_TALK event inside
  [t_first, t_log], as DQ2); t_call = its context-assembly time;
- pending set P(tau): the `context_ledger_items` of the recipient's calls after its previous talk call, up to and
  including this one (= `context_ledger_turns.k_since_talk` at the talk call); the first talk call of an agent-day is
  excluded; rank = position from the newest item (1 = newest);
- responses (scored units: agent senders the mention parser can detect, Claude Code agent and self excluded):
    resp       mention: the talk's `mentions_roster` names the sender;
    resp_reply one of the sender's pending messages is the DQ2 `reply_pairs.parent` of a message of this talk call;
    resp_auth  the talk's parent was written by the sender (any visible message);
    p_reply    soft: max p_reply over labelled cand pairs (talk message, pending message), else 0;
- invisible (placebo): messages by others in the recipient's room with t_call(tau) <= t_m < t(talk message), from
  scored senders not pending; mention response; p_reply of a labelled `invisible` pair if any;
- D2 wake batches: calls that start at a timer-ended pause (gap_kind = pause, not wake_early); batch = that call's items;
  response = first talk call before the next pause call; delay from the wake call's first record.
No text is read.

Holdout. Default: held-out days are dropped before anything is computed (calendar.holdout, common.holdout_mask and the
ledger tables' own flags), exactly as H18. `include_holdout=True` (CLI `--include-holdout`) admits the held-out rows of
the explicitly listed days only. It is for frozen confirm scripts behind their own guard (holdout_ledger.check, Vivian's
sign-off): the CLI refuses it without `--i-understand-this-uses-the-locked-holdout`, explicit `--goal` and `--dates`,
and an `--out` folder outside data/processed/shared/. This replaces H18 confirm_r1b's "shared-folder view" mechanism.

Output (default build): data/processed/shared/pending_sets/G<NN>/ for every goal period with non-holdout active days:
  talks.parquet        one row per scored talk call (talk_id, agent, pt_date, msg, t_us, s_us = t_call, s_prev_us, gap_s,
                       k, k_agent, k_s, n_room, room, after_pause, n_ment, n_ment_pending, n_cand_nonpend,
                       n_ment_nonpend, block (day quarter), k_since_talk, has_parent, parent_pending, goal_no)
  pending.parquet      one row per pending item (talk_id, msg, kind 0 agent / 1 human / 2 nudge+bookend, sender, rank,
                       ment_i (item names the recipient), scored, resp, resp_reply, resp_auth, p_reply)
  invisible.parquet    placebo senders per talk (talk_id, sender, resp, p_reply_inv)
  wakes.parquet        D2 timer wakes; wake_pending.parquet: their batch items (resp5 / resp_reply5: within 300 s)
  days.json            the days used and the k == k_since_talk agreement count
Same file names and columns as H18's r1b folders, so H18's fit scripts and H68's scheme run unchanged on them.

Usage: uv run python infra/shared/pending_sets.py                     (all goal periods; non-holdout)
       uv run python infra/shared/pending_sets.py --period G38 --period G51
       uv run python infra/shared/pending_sets.py --verify            (compare with H18's r1b tables, every period;
                                                                       plus the include_holdout path on a stand-in)
       uv run python infra/shared/pending_sets.py --include-holdout --i-understand-this-uses-the-locked-holdout \
              --goal 45 --dates 2026-06-01 2026-06-08 --out <confirm folder>          (confirm scripts only)
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
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUT as SH, REVISION, ROOT, git_commit, holdout_mask, mention_regexes  # noqa: E402

OUT = SH / "pending_sets"
H18 = ROOT / "data/processed/H18-attention-dilution/r1b"
KIND = {"agent": 0, "human": 1, "nudge": 2, "pause_resume": 2, "automated_other": 2}
D2_WINDOW_S = 300.0
TABLES = ("talks", "pending", "invisible", "wakes", "wake_pending")
ACK = "--i-understand-this-uses-the-locked-holdout"


def gname(g: int) -> str:
    return f"G{g:02d}"


def us(s: pl.Series) -> np.ndarray:
    return s.dt.epoch("us").to_numpy().astype(np.int64)


def room_lookup(rooms_tl: pl.DataFrame) -> dict:
    """agent -> (sorted t_start in us, room codes); H18 scheme/build.py room_lookup (uses t_start only)."""
    tl = {}
    for (a,), sub in rooms_tl.group_by(["agent"], maintain_order=True):
        sub = sub.sort("t_start")
        tl[int(a)] = (us(sub["t_start"]), sub["room"].to_numpy())
    return tl


def room_at(tl: dict, a: int, t: np.ndarray) -> np.ndarray:
    if a not in tl:
        return np.full(len(t), -1, dtype=np.int16)
    ts, rm = tl[a]
    idx = np.searchsorted(ts, t, side="right") - 1
    return np.where(idx >= 0, rm[np.clip(idx, 0, None)], -1).astype(np.int16)


class Inputs:
    """Shared tables loaded once (H18 build_ledger.Shared). include_holdout keeps held-out reply pairs."""

    def __init__(self, include_holdout: bool = False):
        t0 = time.time()
        self.include_holdout = include_holdout
        self.cal = pl.read_parquet(SH / "calendar.parquet")
        chat = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "pt_date", "room", "speaker_kind", "agent"]
                               ).with_row_index("msg")
        men = pl.read_parquet(SH / "chat_mentions_clean.parquet", columns=["message_id", "mentions_roster"])
        assert (chat["message_id"] == men["message_id"]).all()
        self.chat = chat.with_columns(men["mentions_roster"])
        self.roster = pl.read_parquet(SH / "roster.parquet")
        ros = self.roster.select(pl.col("agent").alias("id"), "name").to_dicts()
        self.detectable = set(mention_regexes(ros).keys())
        self.cc = set(self.roster.filter(pl.col("claude_code"))["agent"].to_list())
        self.tl = room_lookup(pl.read_parquet(SH / "rooms_timeline.parquet").sort("agent", "t_start"))
        rp = pl.read_parquet(SH / "reply_pairs.parquet", columns=["b_msg", "a_msg", "pair_set", "labelled", "p_reply", "parent",
                                                                  "a_agent", "holdout"])
        if not include_holdout:
            rp = rp.filter(~pl.col("holdout"))
        self.rp_cand = rp.filter((pl.col("pair_set") == "cand") & pl.col("labelled")).select(
            "b_msg", "a_msg", "p_reply", "parent", "a_agent")
        self.rp_inv = rp.filter((pl.col("pair_set") == "invisible") & pl.col("labelled")).select("b_msg", "a_msg", "p_reply")
        self.ev = pl.read_parquet(SH / "events_core.parquet", columns=["t", "message_id", "action_type"]).filter(
            pl.col("action_type") == "AGENT_TALK").select("message_id", pl.col("t").alias("t_ev"))
        print(f"inputs loaded {time.time() - t0:.0f}s", flush=True)


def period_days(cal: pl.DataFrame, g: int, dates: tuple[str, str] | None = None, include_holdout: bool = False) -> list[str]:
    """Active days of goal g (optionally restricted to [dates[0], dates[1])). Held-out days are dropped unless
    include_holdout, in which case ALL active days in range are returned (the caller picks the held-out ones)."""
    c = cal.filter((pl.col("goal_no") == g) & (pl.col("window_s") > 0))
    if dates is not None:
        c = c.filter((pl.col("pt_date") >= dates[0]) & (pl.col("pt_date") < dates[1]))
    days = c["pt_date"].to_list()
    if include_holdout:
        return sorted(days)
    hm = holdout_mask(days, [g] * len(days))
    hc = dict(zip(c["pt_date"].to_list(), c["holdout"].to_list()))
    return sorted(d for d, m in zip(days, hm) if not m and not hc[d])


def build_period(inp: Inputs, g: int, days: list[str] | None = None, include_holdout: bool = False,
                 verbose: bool = True) -> dict | None:
    """H18 build_ledger.build_period. days=None -> period_days(non-holdout). include_holdout=True requires explicit days
    and an Inputs built with include_holdout=True; it admits held-out ledger rows of those days only."""
    t0 = time.time()
    if include_holdout:
        assert days is not None, "include_holdout needs an explicit day list"
        assert inp.include_holdout, "include_holdout needs Inputs(include_holdout=True)"
    else:
        days = period_days(inp.cal, g) if days is None else list(days)
        hm = holdout_mask(days, [g] * len(days))
        hc = dict(zip(inp.cal["pt_date"].to_list(), inp.cal["holdout"].to_list()))
        assert not any(hm) and not any(hc.get(d, False) for d in days), "held-out day requested without include_holdout"
    if not days:
        return None
    keep_h = pl.lit(True) if include_holdout else ~pl.col("holdout")
    cw = (pl.scan_parquet(SH / "call_windows.parquet")
          .filter(pl.col("pt_date").is_in(days) & keep_h)
          .select("turn_id", "agent", "pt_date", "talk", "ctx_mode", "gap_kind", "wake_early", "t_call", "t_first", "t_log",
                  "kind", "pause_s").collect().sort("turn_id"))
    lt = (pl.scan_parquet(SH / "context_ledger_turns.parquet").filter(pl.col("pt_date").is_in(days) & keep_h)
          .select("turn_id", "k_since_talk", "room").collect())
    cw = cw.join(lt, on="turn_id", how="left")
    tids = cw["turn_id"]
    items = (pl.scan_parquet(SH / "context_ledger_items.parquet").filter(pl.col("turn_id").is_in(tids.implode()))
             .select("turn_id", "message_id", "sender", "kind", "rank").collect())
    chat = inp.chat
    items = items.join(chat.select("message_id", "msg", "t", "mentions_roster"), on="message_id", how="left")
    # talk messages -> calls (DQ2's rule)
    cd = chat.filter(pl.col("pt_date").is_in(days) & (pl.col("speaker_kind").cast(pl.Utf8) == "agent"))
    b = cd.select("msg", "message_id", "agent", "t", "mentions_roster").join(inp.ev, on="message_id", how="left").with_columns(
        pl.col("t_ev").fill_null(pl.col("t"))).sort("t_ev")
    cws = cw.select("turn_id", "agent", "t_first", "t_log").sort("t_first")
    b = b.join_asof(cws, left_on="t_ev", right_on="t_first", by="agent", strategy="backward")
    b = b.filter(pl.col("turn_id").is_not_null() & (pl.col("t_ev") <= pl.col("t_log")))
    par = b.select("msg", "turn_id").join(inp.rp_cand.rename({"b_msg": "msg"}), on="msg", how="inner")
    talkmsg = (b.group_by("turn_id").agg(pl.col("msg").sort_by("t").first().alias("msg0"), pl.col("t").min().alias("t_msg0"),
                                          pl.col("msg").alias("msgs"),
                                          pl.col("mentions_roster").flatten().drop_nulls().unique().alias("ment")))
    ros = inp.roster.filter(~pl.col("claude_code"))
    on_roster = {d: [int(r["agent"]) for r in ros.iter_rows(named=True)
                     if r["joined"] <= d and (r["left"] is None or d < r["left"])] for d in days}
    cal = inp.cal.filter(pl.col("pt_date").is_in(days))
    win = {r["pt_date"]: (int(r["win_start"].timestamp() * 1e6), int(r["win_end"].timestamp() * 1e6)) for r in cal.iter_rows(named=True)}
    det_set, cc = inp.detectable, inp.cc
    tm = dict(zip(talkmsg["turn_id"].to_list(), zip(talkmsg["msg0"].to_list(), us(talkmsg["t_msg0"]).tolist(),
                                                      talkmsg["msgs"].to_list(), talkmsg["ment"].to_list())))
    par_by_turn = {}
    for r in par.iter_rows(named=True):
        par_by_turn.setdefault(r["turn_id"], []).append((r["a_msg"], r["p_reply"], bool(r["parent"]), r["a_agent"]))
    inv_by_b = {}
    for r in inp.rp_inv.iter_rows(named=True):
        inv_by_b.setdefault(r["b_msg"], {})[r["a_msg"]] = r["p_reply"]
    talks_rows, pend_rows, inv_rows, wake_rows, wpend_rows = [], [], [], [], []
    talk_id = wake_id = 0
    n_k_match = n_k_tot = 0
    items = items.with_columns(pl.col("kind").cast(pl.Utf8).replace_strict(KIND, default=2).cast(pl.Int8).alias("k8"),
                               pl.col("sender").fill_null(-1).cast(pl.Int16),
                               pl.col("t").dt.epoch("us").alias("t_us")).sort("turn_id", "t_us")
    I_tid = items["turn_id"].to_numpy(); I_msg = items["msg"].to_numpy().astype(np.int64)
    I_k8 = items["k8"].to_numpy(); I_snd = items["sender"].to_numpy(); I_t = items["t_us"].to_numpy()
    I_men = [set(x or []) for x in items["mentions_roster"].to_list()]
    agent_of_turn = dict(zip(cw["turn_id"].to_list(), cw["agent"].to_list()))
    rc = np.array([agent_of_turn.get(int(x), -1) for x in I_tid])
    inv_src = {}
    for a_ in np.unique(rc):
        ix = np.where(rc == a_)[0]
        ix = ix[np.argsort(I_t[ix], kind="stable")]
        inv_src[int(a_)] = (I_t[ix], I_msg[ix], I_k8[ix], I_snd[ix])

    def slice_items(t_lo, t_hi):
        """item indices with turn_id in (t_lo, t_hi] (turn ids are time-ordered within an agent)."""
        return np.arange(np.searchsorted(I_tid, t_lo, "right"), np.searchsorted(I_tid, t_hi, "right"))

    for (a, d), calls in cw.group_by(["agent", "pt_date"], maintain_order=True):
        a = int(a)
        if a in cc or a not in on_roster.get(d, []):
            continue
        calls = calls.sort("turn_id")
        rec = calls.filter(pl.col("ctx_mode").cast(pl.Utf8) != "summary")
        if rec.height == 0:
            continue
        tid = rec["turn_id"].to_numpy()
        tcall = us(rec["t_call"]); tfirst = us(rec["t_first"])
        is_talk = np.array([int(x) in tm for x in tid])
        gap = rec["gap_kind"].cast(pl.Utf8).to_list()
        wake_e = rec["wake_early"].fill_null(False).to_numpy()
        kind = rec["kind"].cast(pl.Utf8).to_list()
        kst = rec["k_since_talk"].fill_null(-1).to_numpy()
        pause_sv = rec["pause_s"].fill_null(np.nan).to_numpy().astype(float)
        ws, we = win[d]
        span = max(1.0, float(we - ws))
        rb = list(on_roster[d])
        rb_ok = np.array([(x != a) and (x in det_set) for x in rb], bool)
        talk_ix = np.where(is_talk)[0]

        for n_, j in enumerate(talk_ix):
            if n_ == 0:
                continue   # first talk call of the agent-day (window spans the night / morning)
            jp = talk_ix[n_ - 1]
            P = slice_items(int(tid[jp]), int(tid[j]))
            msg0, t_b, msgs, ment = tm[int(tid[j])]
            ment = set(int(x) for x in (ment or []))
            prs = par_by_turn.get(int(tid[j]), [])
            parent_msgs = {int(m) for m, p, isp, aa in prs if isp}
            parent_auth = {int(aa) for m, p, isp, aa in prs if isp and aa is not None and aa >= 0}
            soft = {}
            for m, p, isp, aa in prs:
                soft[int(m)] = max(soft.get(int(m), 0.0), float(p) if p is not None else 0.0)
            pm, pk, ps = I_msg[P], I_k8[P], I_snd[P]
            pmen = [I_men[x] for x in P]
            k = len(pm)
            n_k_tot += 1
            n_k_match += int(kst[j] == k)
            det = np.array([(int(x) in det_set) and (int(x) not in cc) and int(x) != a for x in ps], bool) & (pk == 0)
            pend_senders = set(int(x) for x in ps[det])
            src = inv_src.get(a)
            inv_senders = {}
            if src is not None:
                lo_, hi_ = np.searchsorted(src[0], tcall[j], "left"), np.searchsorted(src[0], t_b, "left")
                for q in range(lo_, hi_):
                    s_, k_ = int(src[3][q]), int(src[2][q])
                    if k_ == 0 and s_ in det_set and s_ not in cc and s_ != a:
                        pr = max((inv_by_b.get(int(bm), {}).get(int(src[1][q]), -1.0) for bm in msgs), default=-1.0)
                        inv_senders[s_] = max(inv_senders.get(s_, -1.0), pr)
            rooms_now = room_at(inp.tl, a, np.array([t_b]))[0]
            R = np.array([room_at(inp.tl, x, np.array([t_b]))[0] for x in rb])
            nroom = int((R == rooms_now).sum())
            cand = [x for xi, x in enumerate(rb) if rb_ok[xi] and R[xi] == rooms_now and x not in pend_senders
                    and x not in inv_senders]
            after_pause = any(gap[q] in ("pause", "pause_early") for q in range(jp + 1, j + 1))
            frac = (t_b - ws) / span
            talks_rows.append((talk_id, a, d, int(msg0), int(t_b), int(tcall[j]), int(tcall[jp]), float((tcall[j] - tcall[jp]) / 1e6),
                               k, int((pk == 0).sum()), len(pend_senders), nroom, int(rooms_now), after_pause, len(ment),
                               len(ment & pend_senders), len(cand), len(ment & set(cand)),
                               int(min(3, max(0, np.floor(4 * frac)))), int(kst[j]), len(parent_msgs) > 0,
                               len(parent_msgs & set(int(x) for x in pm)) > 0))
            for q in range(k):
                snd = int(ps[q]); m = int(pm[q])
                sc = bool(det[q])
                pend_rows.append((talk_id, m, int(pk[q]), snd, int(k - q), a in pmen[q], sc, sc and (snd in ment),
                                  sc and (m in parent_msgs), sc and (snd in parent_auth), float(soft.get(m, 0.0)) if sc else 0.0))
            for snd, pr in inv_senders.items():
                if snd in pend_senders:
                    continue
                inv_rows.append((talk_id, snd, snd in ment, float(pr)))
            talk_id += 1
        # D2: timer-ended pause wakes
        pause_ix = [q for q in range(len(tid)) if kind[q] == "pause"]
        for q in range(1, len(tid)):
            if gap[q] != "pause" or wake_e[q]:
                continue
            P = slice_items(int(tid[q]) - 1, int(tid[q]))
            if len(P) == 0:
                continue
            nxt_p = next((p for p in pause_ix if p >= q), None)   # the stint ends at the next pause call (inclusive)
            hi_ix = nxt_p if nxt_p is not None else len(tid) - 1
            tj = [x for x in talk_ix if q <= x <= hi_ix]
            talked = len(tj) > 0
            if talked:
                x = tj[0]
                msg0, t_b, msgs, ment = tm[int(tid[x])]
                ment = set(int(y) for y in (ment or []))
                delay = (t_b - tfirst[q]) / 1e6
                prs = par_by_turn.get(int(tid[x]), [])
                parent_msgs = {int(m) for m, p, isp, aa in prs if isp}
                k_extra = int(len(slice_items(int(tid[q]), int(tid[x]))))
            else:
                ment, delay, parent_msgs, k_extra = set(), np.nan, set(), 0
            pm, pk, ps = I_msg[P], I_k8[P], I_snd[P]
            pmen = [I_men[y] for y in P]
            det = np.array([(int(y) in det_set) and (int(y) not in cc) and int(y) != a for y in ps], bool) & (pk == 0)
            kk = len(pm)
            t_p = int(tfirst[q - 1])
            p_s = float(pause_sv[q - 1]) if np.isfinite(pause_sv[q - 1]) else np.nan
            wake_rows.append((wake_id, a, d, t_p, p_s, int(tfirst[q]), kk, int(kst[q]), int((pk == 0).sum()),
                              len(set(int(y) for y in ps[det])), talked, float(delay), k_extra, len(ment),
                              int(min(3, max(0, np.floor(4 * (tfirst[q] - ws) / span))))))
            for r_ in range(kk):
                snd = int(ps[r_]); m = int(pm[r_])
                sc = bool(det[r_])
                resp = sc and (snd in ment)
                rr = sc and (m in parent_msgs)
                ok5 = bool(talked and delay <= D2_WINDOW_S)
                wpend_rows.append((wake_id, m, int(pk[r_]), snd, int(kk - r_), a in pmen[r_], sc, resp, resp and ok5, rr, rr and ok5))
            wake_id += 1
    if not talks_rows:
        return None
    talks = pl.DataFrame(talks_rows, orient="row", schema={
        "talk_id": pl.Int32, "agent": pl.Int16, "pt_date": pl.Utf8, "msg": pl.UInt32, "t_us": pl.Int64, "s_us": pl.Int64,
        "s_prev_us": pl.Int64, "gap_s": pl.Float32, "k": pl.Int32, "k_agent": pl.Int32, "k_s": pl.Int16,
        "n_room": pl.Int16, "room": pl.Int16, "after_pause": pl.Boolean, "n_ment": pl.Int16, "n_ment_pending": pl.Int16,
        "n_cand_nonpend": pl.Int16, "n_ment_nonpend": pl.Int16, "block": pl.Int8, "k_since_talk": pl.Int32,
        "has_parent": pl.Boolean, "parent_pending": pl.Boolean}).with_columns(pl.lit(g, dtype=pl.Int16).alias("goal_no"))
    pend = pl.DataFrame(pend_rows, orient="row", schema={
        "talk_id": pl.Int32, "msg": pl.UInt32, "kind": pl.Int8, "sender": pl.Int16, "rank": pl.Int32, "ment_i": pl.Boolean,
        "scored": pl.Boolean, "resp": pl.Boolean, "resp_reply": pl.Boolean, "resp_auth": pl.Boolean, "p_reply": pl.Float32})
    inv = pl.DataFrame(inv_rows, orient="row", schema={"talk_id": pl.Int32, "sender": pl.Int16, "resp": pl.Boolean,
                                                       "p_reply_inv": pl.Float32})
    wakes = pl.DataFrame(wake_rows, orient="row", schema={
        "wake_id": pl.Int32, "agent": pl.Int16, "pt_date": pl.Utf8, "t_pause_us": pl.Int64, "pause_s": pl.Float32,
        "t_wake_us": pl.Int64, "k": pl.Int32, "k_pend": pl.Int32, "k_agent": pl.Int32, "k_s": pl.Int16, "talked": pl.Boolean,
        "delay_s": pl.Float32, "k_extra": pl.Int32, "n_ment": pl.Int16, "block": pl.Int8}) if wake_rows else None
    wpend = pl.DataFrame(wpend_rows, orient="row", schema={
        "wake_id": pl.Int32, "msg": pl.UInt32, "kind": pl.Int8, "sender": pl.Int16, "rank": pl.Int32, "ment_i": pl.Boolean,
        "scored": pl.Boolean, "resp": pl.Boolean, "resp5": pl.Boolean, "resp_reply": pl.Boolean, "resp_reply5": pl.Boolean}) if wpend_rows else None
    if verbose:
        sc = pend.filter(pl.col("scored"))
        print(f"{gname(g)}: {len(days)} days, {talks.height} talks (k = k_since_talk in {n_k_match}/{n_k_tot}), "
              f"{pend.height} pending rows, {sc.height} scored, "
              f"{0 if wakes is None else wakes.height} wakes, {time.time() - t0:.0f}s", flush=True)
    return dict(talks=talks, pending=pend, invisible=inv, wakes=wakes, wake_pending=wpend, days=days,
                k_match=[n_k_match, n_k_tot])


def write_period(out_dir: Path, res: dict):
    out_dir.mkdir(parents=True, exist_ok=True)
    for k in TABLES:
        df = res.get(k)
        if df is None or df.is_empty():
            continue
        df.write_parquet(out_dir / f"{k}.parquet", compression="zstd", compression_level=9)
    (out_dir / "days.json").write_text(json.dumps({"days": res["days"], "k_equals_k_since_talk": res["k_match"]}))


def write_provenance(out: Path, periods: list[str], include_holdout: bool, extra: dict | None = None):
    out.mkdir(parents=True, exist_ok=True)
    prov = {"built_by": "infra/shared/pending_sets.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["shared/call_windows", "shared/context_ledger_turns", "shared/context_ledger_items",
                                   "shared/reply_pairs", "shared/chat_core", "shared/chat_mentions_clean",
                                   "shared/events_core", "shared/roster", "shared/rooms_timeline", "shared/calendar"]}],
            "params": {"periods": periods, "d2_window_s": D2_WINDOW_S,
                       "pending": "ledger items since the previous talk call (k_since_talk); first talk call of the day excluded",
                       "responses": "resp = mention; resp_reply = reply_pairs parent among the sender's pending messages; "
                                    "resp_auth = parent author; p_reply = soft",
                       "holdout": ("INCLUDED for the listed days (confirm build)" if include_holdout else
                                   "excluded (calendar.holdout | holdout_mask | ledger holdout flags)"),
                       "source": "hypotheses/H18-attention-dilution/scheme/build_ledger.py (rules unchanged)",
                       **(extra or {})},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (out / "_provenance.json").write_text(json.dumps(prov, indent=1))


def all_goals(cal: pl.DataFrame) -> list[int]:
    c = cal.filter((pl.col("window_s") > 0) & ~pl.col("holdout") & pl.col("goal_no").is_not_null())
    gs = sorted(set(c["goal_no"].to_list()))
    return [g for g in gs if period_days(cal, g)]


def _cmp(a: pl.DataFrame | None, b: pl.DataFrame | None) -> str:
    if a is None and b is None:
        return "both absent"
    if a is None or b is None:
        return "one absent"
    if a.columns != b.columns:
        return f"columns differ: {set(a.columns) ^ set(b.columns)}"
    if a.equals(b):
        return "identical"
    if a.height != b.height:
        return f"rows {a.height} vs {b.height}"
    diff = [c for c in a.columns if not a[c].equals(b[c])]
    return f"same rows; columns differ: {diff}"


def verify(standin: str = "G41") -> dict:
    """(1) Shared tables on disk vs H18's r1b tables, every H18 period (read-only). (2) The include_holdout path on a
    non-holdout stand-in (explicit days, include_holdout=True) reproduces the default build exactly."""
    res, ok = {"periods": {}}, True
    for d in sorted(H18.glob("G*")):
        if not (d / "talks.parquet").exists():
            continue
        s = OUT / d.name
        row = {}
        for k in TABLES:
            a = pl.read_parquet(d / f"{k}.parquet") if (d / f"{k}.parquet").exists() else None
            b = pl.read_parquet(s / f"{k}.parquet") if (s / f"{k}.parquet").exists() else None
            row[k] = _cmp(a, b)
        dj = json.loads((d / "days.json").read_text()) if (d / "days.json").exists() else None
        sj = json.loads((s / "days.json").read_text()) if (s / "days.json").exists() else None
        row["days"] = "identical" if dj == sj else "differ"
        ok &= all(v in ("identical", "both absent") for v in row.values())
        res["periods"][d.name] = row
    inp_h = Inputs(include_holdout=True)
    g = int(standin[1:])
    days = period_days(inp_h.cal, g)
    r1 = build_period(inp_h, g, days=days, include_holdout=True, verbose=False)
    same = {k: _cmp(pl.read_parquet(OUT / standin / f"{k}.parquet") if (OUT / standin / f"{k}.parquet").exists() else None,
                    r1.get(k)) for k in TABLES}
    res["include_holdout_path_on_" + standin] = same
    ok &= all(v in ("identical", "both absent") for v in same.values())
    res["ok"] = bool(ok)
    print(json.dumps(res, indent=1), flush=True)
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--period", action="append", help="G<NN> (repeatable); default: every goal period")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--include-holdout", action="store_true", help="confirm scripts only (see docstring)")
    ap.add_argument(ACK, dest="ack", action="store_true")
    ap.add_argument("--goal", type=int)
    ap.add_argument("--dates", nargs=2, metavar=("START", "END_EXCL"))
    ap.add_argument("--only-holdout", action="store_true", help="with --include-holdout: keep only the held-out days")
    ap.add_argument("--out")
    a = ap.parse_args()
    if a.verify:
        sys.exit(0 if verify()["ok"] else 1)
    if a.include_holdout:
        if not a.ack or a.goal is None or not a.dates or not a.out:
            sys.exit(f"refusing: --include-holdout needs {ACK}, --goal, --dates and --out (confirm scripts only)")
        out = Path(a.out).resolve()
        if out == OUT.resolve() or SH.resolve() in out.parents or out == SH.resolve():
            sys.exit("refusing: held-out rows may not be written under data/processed/shared/")
        inp = Inputs(include_holdout=True)
        days = period_days(inp.cal, a.goal, tuple(a.dates), include_holdout=True)
        if a.only_holdout:
            hm = holdout_mask(days, [a.goal] * len(days))
            hc = dict(zip(inp.cal["pt_date"].to_list(), inp.cal["holdout"].to_list()))
            days = [d for d, m in zip(days, hm) if m or hc[d]]
        res = build_period(inp, a.goal, days=days, include_holdout=True)
        if res is not None:
            write_period(out / gname(a.goal), res)
        write_provenance(out, [gname(a.goal)], True, {"dates": a.dates, "only_holdout": a.only_holdout})
        return
    inp = Inputs()
    gs = [int(p.lstrip("G")) for p in a.period] if a.period else all_goals(inp.cal)
    done = []
    for g in gs:
        res = build_period(inp, g)
        if res is not None:
            write_period(OUT / gname(g), res)
            done.append(gname(g))
    if not a.period:
        write_provenance(OUT, done, False)
    else:
        p = OUT / "_provenance.json"
        prev = json.loads(p.read_text())["params"]["periods"] if p.exists() else []
        write_provenance(OUT, sorted(set(prev) | set(done)), False)


if __name__ == "__main__":
    main()
