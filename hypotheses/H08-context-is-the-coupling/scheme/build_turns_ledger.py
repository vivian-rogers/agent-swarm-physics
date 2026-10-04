"""H08 round-1b scheme: turns and read-out from the DQ1 context ledger (`call_windows`, `context_ledger_items`).

  uv run python hypotheses/H08-context-is-the-coupling/scheme/build_turns_ledger.py              # all H08 periods + G10
  uv run python hypotheses/H08-context-is-the-coupling/scheme/build_turns_ledger.py --period 38

Switch: this is the ledger path. The round-1 path (`scheme/build_turns.py`: turn-merged records, pause-aware call starts
from H08's own rule, `exposure` membership) is untouched; its outputs stay in data/processed/H08-context-is-the-coupling/
G<NN>/. Round-1b outputs go to .../r1b/G<NN>/ with the round-1 columns plus new ones, so the round-1 C9 code reads them.

Turns = ledger calls with ctx_mode != summary (memory/session-summary calls receive no items and never talk), sorted by
t_call; t_us = t_first (first logged record), s_us = t_call (context assembly). The read-out call of a message is the call
that received it (`context_ledger_items`), i.e. the first call with t_call > t_m, so o = 1 is exact by construction.
New columns:
- turns: turn_id, gap_kind, ctx_mode, reset_forced, reset_consol, par_auth (bitmask of the talk's reply-parent authors),
  k_new;
- readout: Wc_s (t_call of the read-out call - t_m: the visibility lag, = ledger age_s), rank (position in the receiving
  batch, 1 = newest), yrep (bits: the talk at offset o has this message as its reply parent), yauth (bits: its parent's
  author is the sender), cos_m2..cos_p3 / cosp_m2..cosp_p3 (float16: cosine of the bge-small embeddings of the talk at
  offset o and the message; NaN when that call does not talk), for the real and the pseudo message.
Pseudo-message null and other-room placebo as round 1. No text is read. Holdout days are dropped before computation.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h08lib import *  # noqa: E402,F403
from build_turns import room_lookup, room_at  # noqa: E402

OFFS = np.arange(-2, 4)
KIND = {"agent": 0, "human": 1, "automated": 2}
SEED = 20261004
OUT1B = OUT / "r1b"
EXTRA_PERIODS = {10: dict(title="Complete as many games as you can", regime="I", mode="I", N=7, rooms="#general")}


def chat_full() -> pl.DataFrame:
    chat = chat_table()
    ci = pl.read_parquet(SH / "embeddings/chat_index.parquet").with_row_index("erow")
    return chat.join(ci, on="message_id", how="left").sort("msg")


def period_days_any(g: int) -> list[str]:
    if g in PERIODS:
        return period_days(g)
    cal = calendar().filter((pl.col("goal_no") == g) & (pl.col("window_s") > 0))
    days = cal["pt_date"].to_list()
    m = holdout_mask(days, [g] * len(days))
    hc = dict(zip(cal["pt_date"].to_list(), cal["holdout"].to_list()))
    days = [d for d, x in zip(days, m) if not x and not hc[d]]
    assert not any(is_holdout(d, g) for d in days)
    return sorted(days)


def load_calls(days, chat):
    cw = (pl.scan_parquet(SH / "call_windows.parquet").filter(pl.col("pt_date").is_in(days) & ~pl.col("holdout")
                                                             & (pl.col("ctx_mode").cast(pl.Utf8) != "summary"))
          .select("turn_id", "agent", "pt_date", "talk", "kind", "ctx_mode", "gap_kind", "t_call", "t_first", "t_log", "pause_s")
          .collect())
    lt = (pl.scan_parquet(SH / "context_ledger_turns.parquet").filter(pl.col("pt_date").is_in(days) & ~pl.col("holdout"))
          .select("turn_id", "reset_forced", "reset_consol", "k_new").collect())
    cw = cw.join(lt, on="turn_id", how="left").sort("turn_id")
    ev = (pl.read_parquet(SH / "events_core.parquet", columns=["t", "message_id", "action_type"])
          .filter(pl.col("action_type") == "AGENT_TALK").select("message_id", pl.col("t").alias("t_ev")))
    b = (chat.filter(pl.col("pt_date").is_in(days) & (pl.col("speaker_kind").cast(pl.Utf8) == "agent"))
         .select("msg", "message_id", "agent", "t", "mentions_roster", "erow").join(ev, on="message_id", how="left")
         .with_columns(pl.col("t_ev").fill_null(pl.col("t"))).sort("t_ev"))
    b = b.join_asof(cw.select("turn_id", "agent", "t_first", "t_log").sort("t_first"), left_on="t_ev", right_on="t_first",
                    by="agent", strategy="backward")
    b = b.filter(pl.col("turn_id").is_not_null() & (pl.col("t_ev") <= pl.col("t_log")))
    rp = (pl.read_parquet(SH / "reply_pairs.parquet", columns=["b_msg", "a_msg", "pair_set", "parent", "a_agent", "holdout"])
          .filter(~pl.col("holdout") & (pl.col("pair_set") == "cand") & pl.col("parent")).select(
              pl.col("b_msg").alias("msg"), "a_msg", "a_agent"))
    b = b.join(rp, on="msg", how="left")
    tm = (b.sort("t").group_by("turn_id").agg(pl.col("msg").first().alias("msg0"), pl.col("erow").first().alias("erow0"),
                                              pl.col("mentions_roster").flatten().drop_nulls().unique().alias("ment"),
                                              pl.col("a_msg").drop_nulls().unique().alias("par_msgs"),
                                              pl.col("a_agent").drop_nulls().unique().alias("par_auth")))
    cw = cw.join(tm, on="turn_id", how="left")
    return cw


def build_period(g: int, chat: pl.DataFrame, tl, E: np.ndarray, verbose=True):
    days = period_days_any(g)
    if not days:
        return None
    t0 = time.time()
    rng = np.random.default_rng(SEED + g)
    win = windows(days)
    cw = load_calls(days, chat)
    items = (pl.scan_parquet(SH / "context_ledger_items.parquet").filter(pl.col("turn_id").is_in(cw["turn_id"].implode()))
             .select("turn_id", "message_id", "rank").collect())
    items = items.join(chat.select("message_id", "msg", "t", "room", pl.col("speaker_kind").cast(pl.Utf8).alias("sk"), "agent",
                                   "erow"), on="message_id", how="left")
    items = items.with_columns(pl.col("sk").replace_strict(KIND, default=3).cast(pl.Int8).alias("kind"),
                               pl.col("agent").fill_null(-1).cast(pl.Int16).alias("spk"))
    agent_of = dict(zip(cw["turn_id"].to_list(), cw["agent"].to_list()))
    items = items.with_columns(pl.col("turn_id").replace_strict(agent_of, default=-1).cast(pl.Int16).alias("rcpt"))
    T = {}
    turn_frames = []
    for (a, d), sub in cw.group_by(["agent", "pt_date"], maintain_order=True):
        sub = sub.sort("t_call")
        t = us(sub["t_first"]); s = us(sub["t_call"])
        ment = np.array([mask_of(x) for x in sub["ment"].to_list()], dtype=np.uint64)
        pa = np.array([mask_of(x) for x in sub["par_auth"].to_list()], dtype=np.uint64)
        pm = [set(int(y) for y in (x or [])) for x in sub["par_msgs"].to_list()]
        T[(int(a), d)] = dict(t=t, s=s, talk=sub["talk"].fill_null(False).to_numpy() & sub["msg0"].is_not_null().to_numpy(),
                              pause=(sub["kind"].cast(pl.Utf8) == "pause").to_numpy(),
                              wake=(sub["gap_kind"].cast(pl.Utf8) == "pause").to_numpy(),
                              ment=ment, pa=pa, pm=pm, erow=sub["erow0"].fill_null(-1).to_numpy().astype(np.int64))
        turn_frames.append(sub.select("turn_id", "agent", "pt_date", pl.col("t_first").dt.epoch("us").alias("t_us"),
                                      pl.col("t_call").dt.epoch("us").alias("s_us"), "talk", "kind", "gap_kind", "ctx_mode",
                                      "pause_s", "reset_forced", "reset_consol", "k_new",
                                      pl.col("msg0").alias("msg")).with_columns(pl.Series("ment", ment), pl.Series("par_auth", pa)))

    def cosines(tr, idx, erow_m):
        out = np.full((len(idx), len(OFFS)), np.nan, np.float32)
        n = len(tr["t"])
        em = erow_m >= 0
        for j, o in enumerate(OFFS):
            k = idx + o - 1
            ok = (k >= 0) & (k < n)
            kk = np.clip(k, 0, max(n - 1, 0))
            er = np.where(ok & tr["talk"][kk], tr["erow"][kk], -1)
            v = (er >= 0) & em
            if v.any():
                out[v, j] = (np.asarray(E[er[v]], np.float32) * np.asarray(E[erow_m[v]], np.float32)).sum(1)
        return out

    def bits(tr, idx, sender, msgs):
        n = len(tr["t"])
        yt = np.zeros(len(idx), np.uint8); ya = np.zeros(len(idx), np.uint8); yv = np.zeros(len(idx), np.uint8)
        yr = np.zeros(len(idx), np.uint8); yu = np.zeros(len(idx), np.uint8)
        sh = np.where(sender >= 0, sender, 63).astype(np.uint64)
        for o in OFFS:
            k = idx + o - 1
            ok = (k >= 0) & (k < n)
            kk = np.clip(k, 0, max(n - 1, 0))
            talk = ok & tr["talk"][kk]
            addr = talk & (sender >= 0) & (((tr["ment"][kk] >> sh) & np.uint64(1)) == 1)
            auth = talk & (sender >= 0) & (((tr["pa"][kk] >> sh) & np.uint64(1)) == 1)
            rep = np.array([bool(tk) and (int(m) in tr["pm"][int(q)]) for tk, m, q in zip(talk, msgs, kk)], bool)
            b = np.uint8(1 << int(o + 2))
            yv |= np.where(ok, b, 0).astype(np.uint8); yt |= np.where(talk, b, 0).astype(np.uint8)
            ya |= np.where(addr, b, 0).astype(np.uint8); yr |= np.where(rep, b, 0).astype(np.uint8)
            yu |= np.where(auth, b, 0).astype(np.uint8)
        return yt, ya, yv, yr, yu

    def pair_block(tr, t_m, sender, msgs, erow_m, ws, we, placebo):
        idx = np.searchsorted(tr["s"], t_m, side="right")
        n = len(tr["t"])
        has = idx < n
        ii = np.clip(idx, 0, max(n - 1, 0))
        W = np.where(has, (tr["t"][ii] - t_m) / US, np.nan).astype(np.float32)
        Wc = np.where(has, (tr["s"][ii] - t_m) / US, np.nan).astype(np.float32)
        prev = np.clip(idx - 1, 0, max(n - 1, 0))
        infl = (idx > 0) & has & (tr["t"][prev] > t_m)
        wake = has & tr["wake"][ii]
        gap = np.where(infl, (t_m - tr["s"][prev]) / US, np.nan).astype(np.float32)
        yt, ya, yv, yr, yu = bits(tr, idx, sender, msgs)
        cs = cosines(tr, idx, erow_m)
        off = rng.uniform(20, 60, len(t_m)) * 60 * US * rng.choice([-1, 1], len(t_m))
        tp = (t_m + off).astype(np.int64)
        okp = (tp >= ws) & (tp <= we)
        idp = np.searchsorted(tr["s"], tp, side="right")
        hp = idp < n
        iip = np.clip(idp, 0, max(n - 1, 0))
        prp = np.clip(idp - 1, 0, max(n - 1, 0))
        inflp = (idp > 0) & hp & (tr["t"][prp] > tp) & okp
        Wp = np.where(hp & okp, (tr["t"][iip] - tp) / US, np.nan).astype(np.float32)
        gapp = np.where(inflp, (tp - tr["s"][prp]) / US, np.nan).astype(np.float32)
        ytp, yap, yvp, yrp, yup = bits(tr, idp, sender, msgs)
        csp = cosines(tr, idp, erow_m)
        z = lambda x: np.where(okp, x, 0).astype(np.uint8)
        cols = {"msg": msgs.astype(np.uint32), "sender": sender, "placebo": np.full(len(msgs), placebo),
                "W_s": W, "Wc_s": Wc, "inflight": infl, "wake": wake, "gap_s": gap,
                "ytalk": yt, "yaddr": ya, "yvalid": yv, "yrep": yr, "yauth": yu,
                "Wp_s": Wp, "inflp": inflp, "gapp_s": gapp, "ytalkp": z(ytp), "yaddrp": z(yap), "yvalidp": z(yvp),
                "yrepp": z(yrp), "yauthp": z(yup)}
        for j, o in enumerate(OFFS):
            nm = f"m{-o}" if o < 0 else f"p{o}"
            cols[f"cos_{nm}"] = cs[:, j].astype(np.float16)
            cols[f"cosp_{nm}"] = np.where(okp, csp[:, j], np.nan).astype(np.float16)
        return pl.DataFrame(cols)

    rows = []
    it = items.filter(pl.col("spk") != pl.col("rcpt"))
    it = it.with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.Utf8).alias("pdate"))
    for (a, d), sub in it.group_by(["rcpt", "pdate"], maintain_order=True):
        key = (int(a), d)
        if key not in T or d not in win:
            continue
        tr = T[key]
        t_m = us(sub["t"]); kind = sub["kind"].to_numpy(); spk = sub["spk"].to_numpy()
        sender = np.where(kind == 0, spk, np.where(kind == 1, -1, -2)).astype(np.int16)
        df = pair_block(tr, t_m, sender, sub["msg"].to_numpy().astype(np.int64), sub["erow"].fill_null(-1).to_numpy().astype(np.int64),
                        *win[d], False)
        rows.append(df.with_columns(pl.lit(int(a), pl.Int8).alias("agent"), pl.Series("rank", sub["rank"].to_numpy())))
    if g in TWO_ROOM:
        ros = pl.read_parquet(SH / "roster.parquet").filter(~pl.col("claude_code"))
        ch = chat.filter(pl.col("pt_date").is_in(days))
        for d in days:
            cd = ch.filter(pl.col("pt_date") == d)
            if not cd.height:
                continue
            on = [int(r["agent"]) for r in ros.iter_rows(named=True) if r["joined"] <= d and (r["left"] is None or d < r["left"])]
            tm_all = us(cd["t"]); room = cd["room"].to_numpy()
            kind = cd["speaker_kind"].cast(pl.Utf8).replace_strict(KIND, default=3).to_numpy()
            spk = cd["agent"].fill_null(-1).to_numpy()
            msgs_all = cd["msg"].to_numpy().astype(np.int64); er_all = cd["erow"].fill_null(-1).to_numpy().astype(np.int64)
            for a in on:
                if (a, d) not in T:
                    continue
                ra = room_at(tl, a, tm_all)
                sel = (ra >= 0) & (ra != room) & (spk != a)
                if not sel.any():
                    continue
                sender = np.where(kind[sel] == 0, spk[sel], np.where(kind[sel] == 1, -1, -2)).astype(np.int16)
                df = pair_block(T[(a, d)], tm_all[sel], sender, msgs_all[sel], er_all[sel], *win[d], True)
                rows.append(df.with_columns(pl.lit(a, pl.Int8).alias("agent"), pl.lit(None, pl.Int16).alias("rank")))
    ro = pl.concat(rows, how="diagonal_relaxed") if rows else None
    turns = pl.concat(turn_frames).sort("agent", "s_us")
    od = OUT1B / gname(g)
    od.mkdir(parents=True, exist_ok=True)
    turns.write_parquet(od / "turns.parquet", compression="zstd")
    if ro is not None:
        ro.write_parquet(od / "readout.parquet", compression="zstd")
    if verbose:
        print(f"{gname(g)}: {len(days)} days, {turns.height} calls, {0 if ro is None else ro.height} read-out pairs "
              f"({0 if ro is None else int(ro['placebo'].sum())} other-room), {time.time() - t0:.0f}s", flush=True)
    return {"days": days, "n_turns": turns.height, "n_pairs": 0 if ro is None else ro.height}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", type=int, action="append")
    a = ap.parse_args()
    gs = a.period or (sorted(PERIODS) + [10])
    chat = chat_full()
    tl = room_lookup()
    E = np.load(SH / "embeddings/chat_bge_small.npy", mmap_mode="r")
    for g in gs:
        info = build_period(g, chat, tl, E)
        write_provenance(f"r1b/{gname(g)}/turns+readout", "hypotheses/H08-context-is-the-coupling/scheme/build_turns_ledger.py",
                         ["call_windows", "context_ledger_turns", "context_ledger_items", "reply_pairs", "chat_core",
                          "chat_mentions_clean", "events_core", "embeddings/chat_bge_small", "rooms_timeline", "roster",
                          "calendar"],
                         {"offsets": OFFS.tolist(), "pseudo_shift_min": [20, 60], "seed": SEED + g,
                          "turns": "ledger calls, ctx_mode != summary; t = t_first, s = t_call",
                          "holdout": "dropped before computation", "days": info["days"] if info else []},
                         folder=OUT1B)


if __name__ == "__main__":
    main()
