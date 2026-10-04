"""H18 round-1b scheme: pending sets from the DQ1 context ledger, responses from DQ2 reply labels (and mentions).

  uv run python hypotheses/H18-attention-dilution/scheme/build_ledger.py              # all H18 periods + G10 (NE03)
  uv run python hypotheses/H18-attention-dilution/scheme/build_ledger.py --period G38

Switch: this is the `--inputs ledger` path. The round-1 path (`scheme/build.py`, call start = previous logged record,
mention responses) is untouched and still runnable; its outputs stay in data/processed/H18-attention-dilution/G<NN>/.
Round-1b outputs go to data/processed/H18-attention-dilution/r1b/G<NN>/ with the same file names and columns, so
`analysis/fit_periods.py --dir .../r1b --resp <col>` runs unchanged on them.

Definitions (card, "Round 1b"):
- talk turn: a ledger call (`call_windows`) that produced >= 1 agent chat message (matched through the AGENT_TALK event:
  t_first <= t_event <= t_log, as DQ2 does); t_call = its context-assembly time;
- pending set P(tau): the `context_ledger_items` of the recipient's calls after its previous talk call, up to and
  including this one (= `context_ledger_turns.k_since_talk` at the talk call); first talk call of an agent-day excluded;
- rank: position from the newest message in P(tau) (1 = newest);
- responses (all on the same scored units, agent senders whose name the mention parser detects, as round 1):
    resp       mention: the talk's `mentions_roster` names the sender (round-1 measure, ledger visibility);
    resp_reply reply, message-specific: one of the sender's pending messages is the `reply_pairs.parent` of a message of
               this talk call (pair_set = cand, parent = True);
    resp_auth  reply, author-level: the talk's parent was written by the sender (any visible message);
    p_reply    soft: max p_reply over labelled cand pairs (talk message, pending message of the sender), else 0;
- invisible (placebo): messages by others in the recipient's room with t_call(tau) <= t_m < t(talk message); scored
  senders not pending; mention response; p_reply of a labelled `invisible` pair if any;
- D2 wake batches: calls that start at a timer-ended pause (gap_kind = pause, not wake_early); batch = that call's
  items (exogenous size); response = first talk call within the stint (before the next pause call), delay from the
  wake call's first record.
No text is read. Holdout days are dropped before anything is computed.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
from pathlib import Path

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
sys.path.insert(0, str(HERE.parent / "analysis"))
sys.path.insert(0, str(HERE))
from common import REVISION, git_commit, holdout_mask, mention_regexes  # noqa: E402
from periods import PERIODS, gname  # noqa: E402
from build import room_at, room_lookup  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H18-attention-dilution/r1b"
KIND = {"agent": 0, "human": 1, "nudge": 2, "pause_resume": 2, "automated_other": 2}
D2_WINDOW_S = 300.0
EXTRA = {10: dict(title="Complete as many games as you can", dates=("2025-08-18", "2025-08-25"), regime="I", mode="I",
                  N=7, rooms="#general", splits="NE03 chat fetch limit 2025-08-20", group="native NE03")}


def us(s: pl.Series) -> np.ndarray:
    return s.dt.epoch("us").to_numpy().astype(np.int64)


class Shared:
    def __init__(self):
        t0 = time.time()
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
        self.tl = room_lookup(_RT())
        rp = pl.read_parquet(SH / "reply_pairs.parquet", columns=["b_msg", "a_msg", "pair_set", "labelled", "p_reply", "parent",
                                                                  "a_agent", "holdout"]).filter(~pl.col("holdout"))
        self.rp_cand = rp.filter((pl.col("pair_set") == "cand") & pl.col("labelled")).select(
            "b_msg", "a_msg", "p_reply", "parent", "a_agent")
        self.rp_inv = rp.filter((pl.col("pair_set") == "invisible") & pl.col("labelled")).select("b_msg", "a_msg", "p_reply")
        ev = pl.read_parquet(SH / "events_core.parquet", columns=["t", "message_id", "action_type"]).filter(
            pl.col("action_type") == "AGENT_TALK").select("message_id", pl.col("t").alias("t_ev"))
        self.ev = ev
        print(f"shared loaded {time.time() - t0:.0f}s", flush=True)


class _RT:
    """Adapter so build.room_lookup can be reused (it expects an object with .rooms_tl)."""
    def __init__(self):
        self.rooms_tl = pl.read_parquet(SH / "rooms_timeline.parquet").sort("agent", "t_start")


def period_meta(g: int) -> dict:
    return PERIODS.get(g) or EXTRA[g]


def period_days(sh: Shared, g: int) -> list[str]:
    d0, d1 = period_meta(g)["dates"]
    cal = sh.cal.filter((pl.col("goal_no") == g) & (pl.col("pt_date") >= d0) & (pl.col("pt_date") < d1) & (pl.col("window_s") > 0))
    days = cal["pt_date"].to_list()
    hm = holdout_mask(days, [g] * len(days))
    hc = dict(zip(cal["pt_date"].to_list(), cal["holdout"].to_list()))
    return sorted(d for d, m in zip(days, hm) if not m and not hc[d])


def build_period(sh: Shared, g: int, verbose: bool = True) -> dict | None:
    t0 = time.time()
    days = period_days(sh, g)
    if not days:
        return None
    cw = (pl.scan_parquet(SH / "call_windows.parquet")
          .filter(pl.col("pt_date").is_in(days) & ~pl.col("holdout"))
          .select("turn_id", "agent", "pt_date", "talk", "ctx_mode", "gap_kind", "wake_early", "t_call", "t_first", "t_log",
                  "kind", "pause_s").collect().sort("turn_id"))
    lt = (pl.scan_parquet(SH / "context_ledger_turns.parquet").filter(pl.col("pt_date").is_in(days) & ~pl.col("holdout"))
          .select("turn_id", "k_since_talk", "room").collect())
    cw = cw.join(lt, on="turn_id", how="left")
    tids = cw["turn_id"]
    items = (pl.scan_parquet(SH / "context_ledger_items.parquet").filter(pl.col("turn_id").is_in(tids.implode()))
             .select("turn_id", "message_id", "sender", "kind", "rank").collect())
    chat = sh.chat
    items = items.join(chat.select("message_id", "msg", "t", "mentions_roster"), on="message_id", how="left")
    # talk messages -> calls (DQ2's rule)
    cd = chat.filter(pl.col("pt_date").is_in(days) & (pl.col("speaker_kind").cast(pl.Utf8) == "agent"))
    b = cd.select("msg", "message_id", "agent", "t", "mentions_roster").join(sh.ev, on="message_id", how="left").with_columns(
        pl.col("t_ev").fill_null(pl.col("t"))).sort("t_ev")
    cws = cw.select("turn_id", "agent", "t_first", "t_log").sort("t_first")
    b = b.join_asof(cws, left_on="t_ev", right_on="t_first", by="agent", strategy="backward")
    b = b.filter(pl.col("turn_id").is_not_null() & (pl.col("t_ev") <= pl.col("t_log")))
    # parents of talk messages
    par = b.select("msg", "turn_id").join(sh.rp_cand.rename({"b_msg": "msg"}), on="msg", how="inner")
    talkmsg = (b.group_by("turn_id").agg(pl.col("msg").sort_by("t").first().alias("msg0"), pl.col("t").min().alias("t_msg0"),
                                          pl.col("msg").alias("msgs"),
                                          pl.col("mentions_roster").flatten().drop_nulls().unique().alias("ment")))
    ros = sh.roster.filter(~pl.col("claude_code"))
    on_roster = {d: [int(r["agent"]) for r in ros.iter_rows(named=True)
                     if r["joined"] <= d and (r["left"] is None or d < r["left"])] for d in days}
    cal = sh.cal.filter(pl.col("pt_date").is_in(days))
    win = {r["pt_date"]: (int(r["win_start"].timestamp() * 1e6), int(r["win_end"].timestamp() * 1e6)) for r in cal.iter_rows(named=True)}
    det_set, cc = sh.detectable, sh.cc
    # lookups
    tm = dict(zip(talkmsg["turn_id"].to_list(), zip(talkmsg["msg0"].to_list(), us(talkmsg["t_msg0"]).tolist(),
                                                      talkmsg["msgs"].to_list(), talkmsg["ment"].to_list())))
    par_by_turn = {}
    for r in par.iter_rows(named=True):
        par_by_turn.setdefault(r["turn_id"], []).append((r["a_msg"], r["p_reply"], bool(r["parent"]), r["a_agent"]))
    inv_by_b = {}
    for r in sh.rp_inv.iter_rows(named=True):
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
            # invisible: arrivals in [t_call, t_b)
            src = inv_src.get(a)
            inv_senders = {}
            if src is not None:
                lo_, hi_ = np.searchsorted(src[0], tcall[j], "left"), np.searchsorted(src[0], t_b, "left")
                for q in range(lo_, hi_):
                    s_, k_ = int(src[3][q]), int(src[2][q])
                    if k_ == 0 and s_ in det_set and s_ not in cc and s_ != a:
                        pr = max((inv_by_b.get(int(bm), {}).get(int(src[1][q]), -1.0) for bm in msgs), default=-1.0)
                        inv_senders[s_] = max(inv_senders.get(s_, -1.0), pr)
            rooms_now = room_at(sh.tl, a, np.array([t_b]))[0]
            R = np.array([room_at(sh.tl, x, np.array([t_b]))[0] for x in rb])
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
        print(f"{gname(g)}: {len(days)} days, {talks.height} talks (k = k_since_talk in {n_k_match}/{n_k_tot}), "
              f"{pend.height} pending rows, {pend.filter(pl.col('scored')).height} scored, "
              f"resp mention {pend.filter(pl.col('scored'))['resp'].mean():.3f}, reply {pend.filter(pl.col('scored'))['resp_reply'].mean():.3f}, "
              f"{0 if wakes is None else wakes.height} wakes, {time.time() - t0:.0f}s", flush=True)
    return dict(talks=talks, pending=pend, invisible=inv, wakes=wakes, wake_pending=wpend, days=days,
                k_match=[n_k_match, n_k_tot])


def write_period(g: int, res: dict):
    d = OUT / gname(g)
    d.mkdir(parents=True, exist_ok=True)
    for k in ("talks", "pending", "invisible", "wakes", "wake_pending"):
        df = res.get(k)
        if df is None or df.is_empty():
            continue
        df.write_parquet(d / f"{k}.parquet", compression="zstd", compression_level=9)
    (d / "days.json").write_text(json.dumps({"days": res["days"], "k_equals_k_since_talk": res["k_match"]}))


def write_provenance(periods: list[int]):
    OUT.mkdir(parents=True, exist_ok=True)
    prov = {"built_by": "hypotheses/H18-attention-dilution/scheme/build_ledger.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["shared/call_windows", "shared/context_ledger_turns", "shared/context_ledger_items",
                                   "shared/reply_pairs", "shared/chat_core", "shared/chat_mentions_clean",
                                   "shared/events_core", "shared/roster", "shared/rooms_timeline", "shared/calendar"]}],
            "params": {"periods": [gname(g) for g in periods], "d2_window_s": D2_WINDOW_S,
                       "pending": "ledger items since the previous talk call (k_since_talk); first talk call of the day excluded",
                       "responses": "resp = mention; resp_reply = reply_pairs parent among the sender's pending messages; "
                                    "resp_auth = parent author; p_reply = soft",
                       "holdout": "excluded (calendar.holdout | holdout_mask | call_windows.holdout)"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", action="append")
    a = ap.parse_args()
    gs = [int(p.lstrip("G")) for p in a.period] if a.period else list(PERIODS) + [10]
    sh = Shared()
    done = []
    for g in gs:
        res = build_period(sh, g)
        if res is not None:
            write_period(g, res)
            done.append(g)
    write_provenance(done)


if __name__ == "__main__":
    main()
