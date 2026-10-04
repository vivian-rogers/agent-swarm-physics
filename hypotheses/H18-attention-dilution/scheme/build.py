"""H18 scheme: pending sets at talk turns (D1), timer-wake batches (D2), and responses, per goal period.

  uv run python hypotheses/H18-attention-dilution/scheme/build.py            # all H18 periods, non-holdout days only
  uv run python hypotheses/H18-attention-dilution/scheme/build.py --period G38

Definitions are in the card (`../README.md`, "Operational definitions"). Summary:
- talk turn tau of agent i: an AGENT_TALK (chat_core row, speaker_kind = agent);
- call start s(tau): i's latest logged turn (actions minus `pause` mirrors, or any events_core event of i) before t - 1 s;
- pending set P(tau): messages by others in i's room (exposure rows of i) with s(tau_prev) <= t_m < s(tau), same PT day;
  first talk of each agent-day excluded;
- response: tau's mentions_roster contains the sender (chat_mentions_clean);
- D2: timer-ended PAUSEs; batch = messages in [s(pause call), min(expiry, wake)); response = first talk after the wake
  and before the next PAUSE.

Outputs (per period, in data/processed/H18-attention-dilution/G<NN>/): talks, pending, invisible, wakes, wake_pending
(zstd parquet, no text) and a _provenance.json at the folder root. Holdout days are dropped before anything is computed,
unless build_period(..., allow_holdout=True) is called by the confirmatory script.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "2")
os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
sys.path.insert(0, str(HERE.parent / "analysis"))
from common import REVISION, git_commit, holdout_mask, mention_regexes  # noqa: E402
from periods import PERIODS, gname  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H18-attention-dilution"
GUARD_S = 1.0          # the talk's own action mirror is logged ~0.06 s before AGENT_TALK
TIMER_TOL_S = 30.0     # a wake within 30 s of the declared expiry counts as timer-ended (H09)
KIND = {"agent": 0, "human": 1, "automated": 2}


def _ns(s: pl.Series) -> np.ndarray:
    return s.dt.epoch("us").to_numpy().astype(np.int64)


class Shared:
    """Loads the shared tables once."""

    def __init__(self):
        self.cal = pl.read_parquet(SH / "calendar.parquet")
        chat = pl.read_parquet(SH / "chat_core.parquet").with_row_index("msg")
        men = pl.read_parquet(SH / "chat_mentions_clean.parquet").select("mentions_roster")
        self.chat = pl.concat([chat, men], how="horizontal_extend")
        self.exposure = pl.read_parquet(SH / "exposure.parquet")
        self.ev = pl.read_parquet(SH / "events_core.parquet",
                                  columns=["t", "pt_date", "actor_kind", "agent", "action_type", "pause_s"]
                                  ).filter((pl.col("actor_kind") == "agent") & pl.col("agent").is_not_null())
        self.roster = pl.read_parquet(SH / "roster.parquet")
        self.rooms_tl = pl.read_parquet(SH / "rooms_timeline.parquet").sort("agent", "t_start")
        ros = self.roster.select(pl.col("agent").alias("id"), "name").to_dicts()
        self.detectable = set(mention_regexes(ros).keys())
        self.cc = set(self.roster.filter(pl.col("claude_code"))["agent"].to_list())
        # embeddings (secondary response): message_id -> row
        ci = pl.read_parquet(SH / "embeddings/chat_index.parquet").with_row_index("erow")
        self.erow = self.chat.select("msg", "message_id").join(ci, on="message_id", how="left").sort("msg")["erow"].to_numpy()
        self.emb = None

    def embeddings(self):
        if self.emb is None:
            self.emb = np.load(SH / "embeddings/chat_bge_small.npy", mmap_mode="r")
        return self.emb


def period_days(sh: Shared, g: int, allow_holdout: bool = False, dates: tuple[str, str] | None = None) -> list[str]:
    d0, d1 = dates or PERIODS[g]["dates"]
    cal = sh.cal.filter((pl.col("goal_no") == g) & (pl.col("pt_date") >= d0) & (pl.col("pt_date") < d1))
    days = cal["pt_date"].to_list()
    if not allow_holdout:
        mask = holdout_mask(days, [g] * len(days))
        days = [d for d, m in zip(days, mask) if not m and not cal.filter(pl.col("pt_date") == d)["holdout"][0]]
    return sorted(days)


def turn_times(sh: Shared, t0, t1) -> dict[int, np.ndarray]:
    """Per-agent sorted turn times (us since epoch): actions minus `pause` mirrors, plus events_core events."""
    acts = (pl.scan_parquet(SH / "actions.parquet").select("t", "agent", "action")
            .filter((pl.col("t") >= t0) & (pl.col("t") < t1) & pl.col("agent").is_not_null()
                    & (pl.col("action").cast(pl.Utf8) != "pause")).select("t", "agent").collect())
    ev = sh.ev.filter((pl.col("t") >= t0) & (pl.col("t") < t1)).select("t", "agent")
    allt = pl.concat([acts, ev]).sort("agent", "t")
    out = {}
    for (a,), sub in allt.group_by(["agent"], maintain_order=True):
        out[int(a)] = _ns(sub["t"])
    return out


def room_lookup(sh: Shared):
    tl = {}
    for (a,), sub in sh.rooms_tl.group_by(["agent"], maintain_order=True):
        sub = sub.sort("t_start")
        tl[int(a)] = (_ns(sub["t_start"]), sub["room"].to_numpy())
    return tl


def room_at(tl, a: int, t: np.ndarray) -> np.ndarray:
    if a not in tl:
        return np.full(len(t), -1, dtype=np.int16)
    ts, rm = tl[a]
    idx = np.searchsorted(ts, t, side="right") - 1
    out = np.where(idx >= 0, rm[np.clip(idx, 0, None)], -1)
    return out.astype(np.int16)


def build_period(sh: Shared, g: int, allow_holdout: bool = False, with_content: bool = True, verbose=True,
                 dates: tuple[str, str] | None = None, only_holdout: bool = False):
    days = period_days(sh, g, allow_holdout, dates)
    if only_holdout:   # confirmatory use: keep exactly the held-out days of this range
        hm = holdout_mask(days, [g] * len(days))
        days = [d for d, m in zip(days, hm) if m]
    if not days:
        return None
    cal = sh.cal.filter(pl.col("pt_date").is_in(days)).sort("pt_date")
    win = {r["pt_date"]: (int(_ns(pl.Series([r["win_start"]]))[0]), int(_ns(pl.Series([r["win_end"]]))[0]))
           for r in cal.iter_rows(named=True)}
    t0 = cal["win_start"].min() - dt.timedelta(hours=2)
    t1 = cal["win_end"].max() + dt.timedelta(hours=2)
    chat = sh.chat.filter(pl.col("pt_date").is_in(days))
    tl = room_lookup(sh)
    ros = sh.roster.filter(~pl.col("claude_code"))
    on_roster = {d: [int(r["agent"]) for r in ros.iter_rows(named=True)
                     if r["joined"] <= d and (r["left"] is None or d < r["left"])] for d in days}
    msgs = dict(t=_ns(chat["t"]), msg=chat["msg"].to_numpy(),
                kind=chat["speaker_kind"].cast(pl.Utf8).replace_strict(KIND, default=3).to_numpy().astype(np.int8),
                sender=chat["agent"].fill_null(-1).to_numpy().astype(np.int16),
                day=chat["pt_date"].to_numpy(), ment=[set(x or []) for x in chat["mentions_roster"].to_list()])
    pos = {int(x): i for i, x in enumerate(msgs["msg"])}
    expo = {}
    for (a,), ex in sh.exposure.filter(pl.col("msg").is_in(msgs["msg"])).group_by(["agent"], maintain_order=True):
        idx = np.array([pos[int(x)] for x in ex["msg"].to_numpy()], dtype=np.int64)
        expo[int(a)] = idx[np.argsort(msgs["t"][idx], kind="stable")]
    pz = sh.ev.filter((pl.col("action_type") == "PAUSE") & (pl.col("t") >= t0) & (pl.col("t") < t1)
                      & pl.col("pause_s").is_not_null())
    pauses = {}
    for (a,), sub in pz.sort("t").group_by(["agent"], maintain_order=True):
        pauses[int(a)] = (_ns(sub["t"]), sub["pause_s"].to_numpy().astype(float), sub["pt_date"].to_numpy())
    inp = dict(days=days, win=win, msgs=msgs, expo=expo, turns=turn_times(sh, t0, t1), pauses=pauses,
               room_at=lambda a, t: room_at(tl, a, t), on_roster=on_roster, detectable=sh.detectable, cc=sh.cc, goal=g)
    res = assemble(inp)
    if res is None:
        return None
    if with_content and res["pending"].height:
        res["pending"] = add_content(sh, res["talks"], res["pending"])
    if verbose:
        p, w = res["pending"], res["wakes"]
        print(f"{gname(g)}: {len(days)} days, {res['talks'].height} talks, {p.height} pending rows, "
              f"{p.filter(pl.col('scored')).height} scored, {w.height} wakes, {res['wake_pending'].height} wake rows",
              flush=True)
    res["days"] = days
    return res


def assemble(inp: dict) -> dict | None:
    """Core of the scheme, shared by real data and the synthetic generator (analysis/synthetic.py).

    inp: days; win {day: (start_us, end_us)}; msgs {t, msg, kind, sender, day, ment (list of sets)};
    expo {agent: message positions sorted by t}; turns {agent: sorted turn times, us}; pauses {agent: (t_us, dur_s, day)};
    room_at(agent, t_array) -> room codes; on_roster {day: [agents]}; detectable, cc (sets); goal.
    """
    days, win, M = inp["days"], inp["win"], inp["msgs"]
    m_t, m_msg, m_kind, m_sender, m_day, m_ment = M["t"], M["msg"], M["kind"], M["sender"], M["day"], M["ment"]
    det_set, cc, on_roster, ra = inp["detectable"], inp["cc"], inp["on_roster"], inp["room_at"]
    G_US = int(GUARD_S * 1e6)
    talks_rows, pend_rows, inv_rows, wake_rows, wpend_rows = [], [], [], [], []
    talk_id = wake_id = 0
    for a, idx in inp["expo"].items():
        if a in cc:
            continue
        tt = inp["turns"].get(a, np.zeros(0, dtype=np.int64))
        own = np.where((m_kind == 0) & (m_sender == a))[0]
        p_all = inp["pauses"].get(a)
        for d in days:
            if a not in on_roster[d]:
                continue
            ws_us, we_us = win[d]
            span_us = max(1.0, float(we_us - ws_us))
            own_d = own[m_day[own] == d]
            ex_d = idx[m_day[idx] == d]
            ex_t = m_t[ex_d]
            if p_all is not None:
                pm = p_all[2] == d
                p_t, p_s = p_all[0][pm], p_all[1][pm]
            else:
                p_t, p_s = np.zeros(0, dtype=np.int64), np.zeros(0)
            own_t = m_t[own_d]
            own_ment = [m_ment[q] for q in own_d]
            if len(own_d) > 1 and len(tt):
                j = np.searchsorted(tt, own_t - G_US, side="left") - 1
                s = np.where(j >= 0, tt[np.clip(j, 0, None)], -1)
                s = np.where(s >= ws_us - int(3600e6), s, -1)
                rooms_now = ra(a, own_t)
                rb = list(on_roster[d])
                R = np.stack([ra(b, own_t) for b in rb])
                same = R == rooms_now[None, :]
                nroom = same.sum(0).astype(np.int16)
                rb_ok = np.array([(b != a) and (b in det_set) for b in rb], dtype=bool)
                for n in range(1, len(own_d)):
                    sp, sc = s[n - 1], s[n]
                    if sp < 0 or sc < 0:
                        continue
                    lo, hi = np.searchsorted(ex_t, sp, "left"), np.searchsorted(ex_t, sc, "left")
                    P = ex_d[lo:hi]
                    ment = own_ment[n]
                    k = len(P)
                    kinds, senders = m_kind[P], m_sender[P]
                    agent_mask = kinds == 0
                    det = np.array([(int(x) in det_set) and (int(x) not in cc) and int(x) != a for x in senders],
                                   dtype=bool) & agent_mask
                    pend_senders = set(int(x) for x in senders[det])
                    ilo, ihi = hi, np.searchsorted(ex_t, own_t[n], "left")
                    Iv = ex_d[ilo:ihi]
                    inv_senders = set(int(x) for x, kk in zip(m_sender[Iv], m_kind[Iv])
                                      if kk == 0 and int(x) in det_set and int(x) not in cc and int(x) != a)
                    cand = [b for bi, b in enumerate(rb) if rb_ok[bi] and same[bi, n] and b not in pend_senders
                            and b not in inv_senders]
                    after_pause = bool(len(p_t) and np.any((p_t >= sp) & (p_t < sc)))
                    frac = (own_t[n] - ws_us) / span_us
                    talks_rows.append((talk_id, a, d, int(m_msg[own_d[n]]), int(own_t[n]), int(sc), int(sp),
                                       float((sc - sp) / 1e6), k, int(agent_mask.sum()), len(pend_senders),
                                       int(nroom[n]), int(rooms_now[n]), after_pause, len(ment),
                                       len(ment & pend_senders), len(cand), len(ment & set(cand)),
                                       int(min(3, max(0, np.floor(4 * frac))))))
                    for q, mrow in enumerate(P):
                        snd = int(m_sender[mrow])
                        pend_rows.append((talk_id, int(m_msg[mrow]), int(m_kind[mrow]), snd, int(k - q),
                                          a in m_ment[mrow], bool(det[q]), bool(det[q]) and (snd in ment)))
                    for snd in inv_senders - pend_senders:
                        inv_rows.append((talk_id, snd, snd in ment))
                    talk_id += 1
            # D2: timer wakes
            if len(p_t) and len(tt):
                for n in range(len(p_t)):
                    tp = p_t[n]
                    j = np.searchsorted(tt, tp - G_US, "left") - 1
                    if j < 0:
                        continue
                    s_p = tt[j]
                    jw = np.searchsorted(tt, tp + int(0.5e6), "left")
                    if jw >= len(tt):
                        continue
                    t_w = tt[jw]
                    expiry = tp + int(p_s[n] * 1e6)
                    if t_w < expiry - int(TIMER_TOL_S * 1e6) or (t_w - tp) > 4 * 3600e6 or t_w > we_us + int(1800e6):
                        continue  # not a timer-ended wake, or spans the night
                    if n + 1 < len(p_t) and p_t[n + 1] < t_w:
                        continue
                    end_b = min(expiry, t_w)
                    lo, hi = np.searchsorted(ex_t, s_p, "left"), np.searchsorted(ex_t, end_b, "left")
                    Bt = ex_d[lo:hi]
                    nxt_p = p_t[n + 1] if n + 1 < len(p_t) else np.iinfo(np.int64).max
                    cand_talk = np.where((own_t >= t_w - int(0.5e6)) & (own_t < nxt_p))[0]
                    talked = len(cand_talk) > 0
                    if talked:
                        q0 = cand_talk[0]
                        ment = own_ment[q0]
                        delay = (own_t[q0] - t_w) / 1e6
                        jt = np.searchsorted(tt, own_t[q0] - G_US, "left") - 1
                        s_talk = tt[jt] if jt >= 0 else end_b
                        k_extra = int(np.searchsorted(ex_t, s_talk, "left") - hi) if s_talk > end_b else 0
                    else:
                        ment, delay, k_extra = set(), np.nan, 0
                    kinds, senders = m_kind[Bt], m_sender[Bt]
                    det = np.array([(int(x) in det_set) and (int(x) not in cc) and int(x) != a for x in senders],
                                   dtype=bool) & (kinds == 0)
                    kk = len(Bt)
                    # backlog at the wake call: everything since the call start of i's last talk before the pause
                    prev_talks = np.where(own_t < tp)[0]
                    if len(prev_talks):
                        jl = np.searchsorted(tt, own_t[prev_talks[-1]] - G_US, "left") - 1
                        s_last = tt[jl] if jl >= 0 else ws_us
                    else:
                        s_last = ws_us
                    k_pend = int(hi - np.searchsorted(ex_t, min(s_last, s_p), "left"))
                    wake_rows.append((wake_id, a, d, int(tp), float(p_s[n]), int(t_w), kk, k_pend, int((kinds == 0).sum()),
                                      len(set(int(x) for x in senders[det])), talked, float(delay), k_extra, len(ment),
                                      int(min(3, max(0, np.floor(4 * (t_w - ws_us) / span_us))))))
                    for q, mrow in enumerate(Bt):
                        snd = int(m_sender[mrow])
                        resp = bool(det[q]) and (snd in ment)
                        wpend_rows.append((wake_id, int(m_msg[mrow]), int(m_kind[mrow]), snd, int(kk - q),
                                           a in m_ment[mrow], bool(det[q]), resp, bool(resp and delay <= 300)))
                    wake_id += 1
    if not talks_rows:
        return None
    g = inp.get("goal", 0)
    talks = pl.DataFrame(talks_rows, orient="row", schema={
        "talk_id": pl.Int32, "agent": pl.Int16, "pt_date": pl.Utf8, "msg": pl.UInt32, "t_us": pl.Int64, "s_us": pl.Int64,
        "s_prev_us": pl.Int64, "gap_s": pl.Float32, "k": pl.Int32, "k_agent": pl.Int32, "k_s": pl.Int16,
        "n_room": pl.Int16, "room": pl.Int16, "after_pause": pl.Boolean, "n_ment": pl.Int16, "n_ment_pending": pl.Int16,
        "n_cand_nonpend": pl.Int16, "n_ment_nonpend": pl.Int16, "block": pl.Int8}).with_columns(
        pl.lit(g, dtype=pl.Int16).alias("goal_no"))
    pend = pl.DataFrame(pend_rows, orient="row", schema={
        "talk_id": pl.Int32, "msg": pl.UInt32, "kind": pl.Int8, "sender": pl.Int16, "rank": pl.Int32,
        "ment_i": pl.Boolean, "scored": pl.Boolean, "resp": pl.Boolean})
    inv = pl.DataFrame(inv_rows, orient="row", schema={"talk_id": pl.Int32, "sender": pl.Int16, "resp": pl.Boolean})
    wakes = pl.DataFrame(wake_rows, orient="row", schema={
        "wake_id": pl.Int32, "agent": pl.Int16, "pt_date": pl.Utf8, "t_pause_us": pl.Int64, "pause_s": pl.Float32,
        "t_wake_us": pl.Int64, "k": pl.Int32, "k_pend": pl.Int32, "k_agent": pl.Int32, "k_s": pl.Int16, "talked": pl.Boolean,
        "delay_s": pl.Float32, "k_extra": pl.Int32, "n_ment": pl.Int16, "block": pl.Int8})
    wpend = pl.DataFrame(wpend_rows, orient="row", schema={
        "wake_id": pl.Int32, "msg": pl.UInt32, "kind": pl.Int8, "sender": pl.Int16, "rank": pl.Int32,
        "ment_i": pl.Boolean, "scored": pl.Boolean, "resp": pl.Boolean, "resp5": pl.Boolean})
    return dict(talks=talks, pending=pend, invisible=inv, wakes=wakes, wake_pending=wpend)


def add_content(sh: Shared, talks: pl.DataFrame, pend: pl.DataFrame, seed: int = 18) -> pl.DataFrame:
    """cos(e_tau, e_m) and a null cos(e_tau', e_m), tau' = a talk of the same agent on another day of the period."""
    E = sh.embeddings()
    rng = np.random.default_rng(seed)
    tk = talks.select("talk_id", "agent", "pt_date", "msg")
    tmsg = dict(zip(tk["talk_id"].to_list(), tk["msg"].to_list()))
    # null partner per talk
    by_agent = {}
    for r in tk.iter_rows(named=True):
        by_agent.setdefault(r["agent"], []).append((r["pt_date"], r["msg"]))
    null_msg = {}
    for r in tk.iter_rows(named=True):
        others = [m for d, m in by_agent[r["agent"]] if d != r["pt_date"]]
        null_msg[r["talk_id"]] = others[rng.integers(len(others))] if others else -1
    tid = pend["talk_id"].to_numpy()
    mm = pend["msg"].to_numpy().astype(np.int64)
    tm = np.array([tmsg[x] for x in tid], dtype=np.int64)
    nm = np.array([null_msg[x] for x in tid], dtype=np.int64)
    er = sh.erow
    cos = np.full(len(tid), np.nan, dtype=np.float32)
    cos0 = np.full(len(tid), np.nan, dtype=np.float32)
    ok = (er[tm] >= 0) & (er[mm] >= 0)
    ok0 = ok & (nm >= 0)
    for lo in range(0, len(tid), 200_000):
        sl = slice(lo, lo + 200_000)
        o = ok[sl]
        a = np.asarray(E[er[tm[sl][o]]], dtype=np.float32)
        b = np.asarray(E[er[mm[sl][o]]], dtype=np.float32)
        tmp = np.full(o.shape, np.nan, dtype=np.float32)
        tmp[o] = (a * b).sum(1)
        cos[sl] = tmp
        o0 = ok0[sl]
        a0 = np.asarray(E[er[np.where(o0, nm[sl], 0)][o0]], dtype=np.float32)
        b0 = np.asarray(E[er[mm[sl][o0]]], dtype=np.float32)
        tmp0 = np.full(o0.shape, np.nan, dtype=np.float32)
        tmp0[o0] = (a0 * b0).sum(1)
        cos0[sl] = tmp0
    return pend.with_columns(pl.Series("cos", cos).cast(pl.Float32), pl.Series("cos_null", cos0).cast(pl.Float32))


def write_period(g: int, res: dict, sub: str | None = None):
    d = OUT / (sub or gname(g))
    d.mkdir(parents=True, exist_ok=True)
    for k in ("talks", "pending", "invisible", "wakes", "wake_pending"):
        df = res[k]
        if df is None or df.is_empty():
            continue
        df.write_parquet(d / f"{k}.parquet", compression="zstd", compression_level=9)
    (d / "days.json").write_text(json.dumps(res["days"]))


def write_provenance(params: dict, periods: list[int]):
    OUT.mkdir(parents=True, exist_ok=True)
    prov = {"built_by": "hypotheses/H18-attention-dilution/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["shared/calendar", "shared/chat_core", "shared/chat_mentions_clean", "shared/exposure",
                                   "shared/events_core", "shared/actions", "shared/roster", "shared/rooms_timeline",
                                   "shared/embeddings/chat_bge_small", "shared/embeddings/chat_index"]}],
            "params": {**params, "periods": [gname(g) for g in periods], "holdout": "excluded (calendar.holdout | holdout_mask)"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    p = OUT / "_provenance.json"
    old = json.loads(p.read_text()) if p.exists() else {}
    old["scheme"] = prov
    p.write_text(json.dumps(old, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", default=None)
    ap.add_argument("--no-content", action="store_true")
    a = ap.parse_args()
    gs = [int(a.period.lstrip("G"))] if a.period else list(PERIODS)
    t = time.time()
    sh = Shared()
    print(f"loaded shared tables {time.time() - t:.0f}s", flush=True)
    for g in gs:
        res = build_period(sh, g, allow_holdout=False, with_content=not a.no_content)
        if res is not None:
            write_period(g, res)
    write_provenance({"guard_s": GUARD_S, "timer_tol_s": TIMER_TOL_S, "first_talk_of_day": "excluded",
                      "k": "all speaker kinds in the recipient's room", "response": "chat_mentions_clean.mentions_roster",
                      "content_null": "same agent, other day, same period (seed 18)"}, list(PERIODS))
    print(f"done {time.time() - t:.0f}s")


if __name__ == "__main__":
    main()
