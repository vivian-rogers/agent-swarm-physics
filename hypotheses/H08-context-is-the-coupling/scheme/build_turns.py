"""H08 scheme for C2, C3, C8-C10: turns with pause-aware call starts and the read-out of every room message.

  uv run python hypotheses/H08-context-is-the-coupling/scheme/build_turns.py              # all H08 periods
  uv run python hypotheses/H08-context-is-the-coupling/scheme/build_turns.py --period 38

Outputs per goal period in data/processed/H08-context-is-the-coupling/G<NN>/ (zstd parquet, no text):
- turns.parquet: agent, pt_date, t_us, s_us, talk, pause, pause_s, cons, ment (uint64 bitmask of addressed agents),
  msg (chat row of the talk), unc / ctx (provider-aware tokens), n_new (room messages by others first visible at this call);
- readout.parquet: one row per (message, recipient): msg, agent, sender (-1 human / -2 automated), placebo (other room),
  W_s (read-out delay), inflight, wake (read-out call starts at a pause expiry), ytalk / yaddr / yvalid bit fields over
  turn offsets o = -2..3 (bit o+2), and the same for the pseudo-message (t' = t_m +- U(20, 60) min): Wp_s, inflp,
  ytalkp, yaddrp, yvalidp.
Holdout days are dropped before anything is computed (h08lib.period_days asserts it).
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h08lib import *  # noqa: E402,F403

OFFS = np.arange(-2, 4)          # turn offsets; bit = o + 2
KIND = {"agent": 0, "human": 1, "automated": 2}
SEED = 20261004


def room_lookup():
    tl = {}
    rt = pl.read_parquet(SH / "rooms_timeline.parquet").sort("agent", "t_start")
    for (a,), sub in rt.group_by(["agent"], maintain_order=True):
        tl[int(a)] = (us(sub["t_start"]), sub["room"].to_numpy())
    return tl


def room_at(tl, a, t):
    if a not in tl:
        return np.full(len(t), -1, dtype=np.int16)
    ts, rm = tl[a]
    idx = np.searchsorted(ts, t, side="right") - 1
    return np.where(idx >= 0, rm[np.clip(idx, 0, None)], -1).astype(np.int16)


def offset_bits(tr: Turns, idx: np.ndarray, sender: np.ndarray):
    """Bit fields (uint8) of talk, addressing-the-sender and validity at offsets o = -2..3 around read-out index idx."""
    n = len(tr.t)
    yt = np.zeros(len(idx), np.uint8); ya = np.zeros(len(idx), np.uint8); yv = np.zeros(len(idx), np.uint8)
    sh = np.where(sender >= 0, sender, 63).astype(np.uint64)
    for o in OFFS:
        j = idx + o - 1
        ok = (j >= 0) & (j < n)
        jj = np.clip(j, 0, max(n - 1, 0))
        talk = ok & tr.talk[jj]
        addr = talk & (sender >= 0) & (((tr.ment[jj] >> sh) & np.uint64(1)) == 1)
        b = np.uint8(1 << int(o + 2))
        yv |= np.where(ok, b, 0).astype(np.uint8)
        yt |= np.where(talk, b, 0).astype(np.uint8)
        ya |= np.where(addr, b, 0).astype(np.uint8)
    return yt, ya, yv


def pair_rows(tr: Turns, t_m: np.ndarray, sender: np.ndarray):
    idx = readout_idx(tr, t_m)
    n = len(tr.t)
    has = idx < n
    ii = np.clip(idx, 0, max(n - 1, 0))
    W = np.where(has, (tr.t[ii] - t_m) / US, np.nan).astype(np.float32)
    prev = np.clip(idx - 1, 0, max(n - 1, 0))
    infl = (idx > 0) & has & (tr.t[prev] > t_m)
    wake = has & (idx > 0) & tr.pause[prev]
    yt, ya, yv = offset_bits(tr, idx, sender)
    gap = np.where(infl, (t_m - tr.s[prev]) / US, np.nan).astype(np.float32)   # time since the in-flight call started
    return idx, W, infl, wake, yt, ya, yv, gap


def build_period(g: int, chat: pl.DataFrame, expo: pl.DataFrame, tl, verbose=True, days=None, out_dir=None):
    days = days if days is not None else period_days(g)
    if not days:
        return None
    t0 = time.time()
    T = build_turns(days, chat)
    win = windows(days)
    rng = np.random.default_rng(SEED + g)
    ch = chat.filter(pl.col("pt_date").is_in(days)).select(
        "msg", "t", "pt_date", "room", pl.col("speaker_kind").cast(pl.Utf8).alias("sk"), "agent")
    ch = ch.with_columns(pl.col("sk").replace_strict(KIND, default=3).cast(pl.Int8).alias("kind"),
                         pl.col("agent").fill_null(-1).cast(pl.Int16).alias("spk"))
    mt = dict(zip(ch["msg"].to_list(), us(ch["t"]).tolist()))
    ex = expo.filter(pl.col("msg").is_in(ch["msg"].implode())).join(
        ch.select("msg", "pt_date", "kind", "spk", "room"), on="msg", how="inner")
    ex = ex.filter((pl.col("agent") != pl.col("spk")) & (pl.col("agent") != CC_AGENT))
    rows = []
    nnew = {k: np.zeros(len(v.t), np.int32) for k, v in T.items()}
    two_room = g in TWO_ROOM
    ros = pl.read_parquet(SH / "roster.parquet").filter(~pl.col("claude_code"))
    for (a, d), sub in ex.group_by(["agent", "pt_date"], maintain_order=True):
        key = (int(a), d)
        if key not in T:
            continue
        tr = T[key]
        msgs = sub["msg"].to_numpy()
        t_m = np.array([mt[int(x)] for x in msgs], dtype=np.int64)
        kind = sub["kind"].to_numpy(); spk = sub["spk"].to_numpy()
        sender = np.where(kind == 0, spk, np.where(kind == 1, -1, -2)).astype(np.int16)
        idx, W, infl, wake, yt, ya, yv, gap = pair_rows(tr, t_m, sender)
        np.add.at(nnew[key], idx[idx < len(tr.t)], 1)
        ws, we = win[d]
        off = rng.uniform(20, 60, len(t_m)) * 60 * US * rng.choice([-1, 1], len(t_m))
        tp = (t_m + off).astype(np.int64)
        okp = (tp >= ws) & (tp <= we)
        _, Wp, inflp, _, ytp, yap, yvp, gapp = pair_rows(tr, tp, sender)
        rows.append(pl.DataFrame({
            "msg": msgs.astype(np.uint32), "agent": np.full(len(msgs), a, np.int8), "sender": sender,
            "placebo": np.zeros(len(msgs), bool), "W_s": W, "inflight": infl, "wake": wake, "gap_s": gap,
            "ytalk": yt, "yaddr": ya, "yvalid": yv,
            "Wp_s": np.where(okp, Wp, np.nan).astype(np.float32), "inflp": inflp & okp,
            "gapp_s": np.where(okp, gapp, np.nan).astype(np.float32),
            "ytalkp": np.where(okp, ytp, 0).astype(np.uint8), "yaddrp": np.where(okp, yap, 0).astype(np.uint8),
            "yvalidp": np.where(okp, yvp, 0).astype(np.uint8)}))
    # other-room placebo (two-room era): agents on that day's roster whose room at t_m differs from the message room
    if two_room:
        for d in days:
            cd = ch.filter(pl.col("pt_date") == d)
            if not cd.height:
                continue
            on = [int(r["agent"]) for r in ros.iter_rows(named=True)
                  if r["joined"] <= d and (r["left"] is None or d < r["left"])]
            tm_all = us(cd["t"]); room = cd["room"].to_numpy(); kind = cd["kind"].to_numpy(); spk = cd["spk"].to_numpy()
            msgs_all = cd["msg"].to_numpy()
            for a in on:
                key = (a, d)
                if key not in T:
                    continue
                ra = room_at(tl, a, tm_all)
                sel = (ra >= 0) & (ra != room) & (spk != a)
                if not sel.any():
                    continue
                tr = T[key]
                t_m = tm_all[sel]
                sender = np.where(kind[sel] == 0, spk[sel], np.where(kind[sel] == 1, -1, -2)).astype(np.int16)
                idx, W, infl, wake, yt, ya, yv, gap = pair_rows(tr, t_m, sender)
                ws, we = win[d]
                off = rng.uniform(20, 60, len(t_m)) * 60 * US * rng.choice([-1, 1], len(t_m))
                tp = (t_m + off).astype(np.int64)
                okp = (tp >= ws) & (tp <= we)
                _, Wp, inflp, _, ytp, yap, yvp, gapp = pair_rows(tr, tp, sender)
                rows.append(pl.DataFrame({
                    "msg": msgs_all[sel].astype(np.uint32), "agent": np.full(sel.sum(), a, np.int8), "sender": sender,
                    "placebo": np.ones(sel.sum(), bool), "W_s": W, "inflight": infl, "wake": wake, "gap_s": gap,
                    "ytalk": yt, "yaddr": ya, "yvalid": yv,
                    "Wp_s": np.where(okp, Wp, np.nan).astype(np.float32), "inflp": inflp & okp,
            "gapp_s": np.where(okp, gapp, np.nan).astype(np.float32),
                    "ytalkp": np.where(okp, ytp, 0).astype(np.uint8), "yaddrp": np.where(okp, yap, 0).astype(np.uint8),
                    "yvalidp": np.where(okp, yvp, 0).astype(np.uint8)}))
    ro = pl.concat(rows) if rows else None
    tf = []
    for (a, d), tr in T.items():
        tf.append(pl.DataFrame({"agent": np.full(len(tr.t), a, np.int8), "pt_date": [d] * len(tr.t), "t_us": tr.t,
                                "s_us": tr.s, "talk": tr.talk, "pause": tr.pause, "pause_s": tr.pause_s, "cons": tr.cons,
                                "ment": tr.ment, "msg": tr.msg, "unc": tr.unc.astype(np.float32),
                                "ctx": tr.ctx.astype(np.float32), "n_new": nnew[(a, d)],
                                "act": tr.act.tolist() if tr.act is not None else [""] * len(tr.t)}))
    turns = pl.concat(tf).sort("agent", "t_us")
    od = out_dir or (OUT / gname(g))
    od.mkdir(parents=True, exist_ok=True)
    turns.write_parquet(od / "turns.parquet", compression="zstd")
    if ro is not None:
        ro.write_parquet(od / "readout.parquet", compression="zstd")
    if verbose:
        print(f"{gname(g)}: {len(days)} days, {turns.height} turns, {0 if ro is None else ro.height} read-out pairs "
              f"({0 if ro is None else int(ro['placebo'].sum())} other-room), {time.time() - t0:.0f}s", flush=True)
    return {"days": days, "n_turns": turns.height, "n_pairs": 0 if ro is None else ro.height}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", type=int, action="append")
    a = ap.parse_args()
    gs = a.period or sorted(PERIODS)
    chat = chat_table()
    expo = pl.read_parquet(SH / "exposure.parquet", columns=["msg", "agent"])
    tl = room_lookup()
    info = {}
    for g in gs:
        info[gname(g)] = build_period(g, chat, expo, tl)
        write_provenance(f"{gname(g)}/turns+readout", "hypotheses/H08-context-is-the-coupling/scheme/build_turns.py",
                         ["actions", "events_core", "chat_core", "chat_mentions_clean", "exposure (membership)",
                          "rooms_timeline", "roster", "calendar"],
                         {"merge_s": 1, "wake_guard_s": 1, "offsets": OFFS.tolist(), "pseudo_shift_min": [20, 60],
                          "seed": SEED + g, "holdout": "dropped before computation",
                          "days": info[gname(g)]["days"] if info[gname(g)] else []})


if __name__ == "__main__":
    main()
