"""H08 round 1b native test NE32: isolated newcomers, then merged (GPT-5.6 Sol/Terra/Luna on 2026-07-09; Grok 4.5 07-10).

  uv run python hypotheses/H08-context-is-the-coupling/analysis/ne32_newcomers.py

Prediction (written before this run): goalperiod-subhypotheses/NE32/README.md.
For each (newcomer n, old-timer j): t_rec = t_call of n's first ledger call that received an item from j; responses of n
to j = n's talk calls that name j (chat_mentions_clean) or whose reply parent (reply_pairs, pair_set = cand, parent) was
written by j. N32a: naming rate of old-timers during isolation; N32b: share of responding pairs whose first response
comes at or after t_rec; N32c: within the first 2 h after the move, per (talk call, j) response rate when an item from
j arrived at that call or one of the two before it, vs when none did. Non-holdout #51 days only; no text.
Writes data/processed/H08-context-is-the-coupling/r1b/NE32.json.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
from h08lib import *  # noqa: E402,F403

OUT1B = OUT / "r1b"
NEW = {35: "2026-07-09", 36: "2026-07-09", 37: "2026-07-09", 38: "2026-07-10"}
ONLY_MENTIONS = "--mentions-only" in sys.argv   # a reply parent must be a received message, so reply links satisfy
#                                                N32b by construction; the mention-only run is the informative one
HORIZON_DAYS = ["2026-07-09", "2026-07-10", "2026-07-13", "2026-07-14", "2026-07-15"]   # first non-holdout #51 days after joining


def main():
    days = [d for d in HORIZON_DAYS if not is_holdout(d, 51)]
    cal = calendar().filter(pl.col("pt_date").is_in(days))
    days = sorted(cal.filter(pl.col("window_s") > 0)["pt_date"].to_list())
    rt = pl.read_parquet(SH / "rooms_timeline.parquet")
    move = {}
    for a in NEW:
        r = rt.filter((pl.col("agent") == a) & (pl.col("room") != 0)).sort("t_start")
        move[a] = int(us(r["t_end"])[0]) if r.height else None
    ros = pl.read_parquet(SH / "roster.parquet").filter(~pl.col("claude_code"))
    cw = (pl.scan_parquet(SH / "call_windows.parquet").filter(pl.col("pt_date").is_in(days) & ~pl.col("holdout")
                                                             & pl.col("agent").is_in(list(NEW))
                                                             & (pl.col("ctx_mode").cast(pl.Utf8) != "summary"))
          .select("turn_id", "agent", "pt_date", "talk", "t_call", "t_first", "t_log").collect().sort("turn_id"))
    items = (pl.scan_parquet(SH / "context_ledger_items.parquet").filter(pl.col("turn_id").is_in(cw["turn_id"].implode()))
             .select("turn_id", "sender", "kind").collect())
    chat = chat_table()
    ev = (pl.read_parquet(SH / "events_core.parquet", columns=["t", "message_id", "action_type"])
          .filter(pl.col("action_type") == "AGENT_TALK").select("message_id", pl.col("t").alias("t_ev")))
    b = (chat.filter(pl.col("pt_date").is_in(days) & pl.col("agent").is_in(list(NEW)) & (pl.col("speaker_kind").cast(pl.Utf8) == "agent"))
         .select("msg", "message_id", "agent", "t", "mentions_roster").join(ev, on="message_id", how="left")
         .with_columns(pl.col("t_ev").fill_null(pl.col("t"))).sort("t_ev"))
    b = b.join_asof(cw.select("turn_id", "agent", "t_first", "t_log").sort("t_first"), left_on="t_ev", right_on="t_first",
                    by="agent", strategy="backward").filter(pl.col("turn_id").is_not_null() & (pl.col("t_ev") <= pl.col("t_log")))
    rp = (pl.read_parquet(SH / "reply_pairs.parquet", columns=["b_msg", "a_agent", "pair_set", "parent", "holdout"])
          .filter(~pl.col("holdout") & (pl.col("pair_set") == "cand") & pl.col("parent")).select(pl.col("b_msg").alias("msg"), "a_agent"))
    b = b.join(rp, on="msg", how="left")
    resp_by_turn, men_by_turn = {}, {}
    for r in b.iter_rows(named=True):
        s = resp_by_turn.setdefault(r["turn_id"], set())
        mm = set(int(x) for x in (r["mentions_roster"] or []))
        s |= mm
        men_by_turn.setdefault(r["turn_id"], set()).update(mm)
        if r["a_agent"] is not None and r["a_agent"] >= 0 and not ONLY_MENTIONS:
            s.add(int(r["a_agent"]))
    rec_by_turn = {}
    for r in items.filter(pl.col("kind").cast(pl.Utf8) == "agent").iter_rows(named=True):
        rec_by_turn.setdefault(r["turn_id"], set()).add(int(r["sender"]))
    out = {"newcomers": {}, "days": days}
    pairs = []
    c_rows = []
    for a in NEW:
        C = cw.filter(pl.col("agent") == a).sort("t_call")
        if not C.height:
            continue
        tid = C["turn_id"].to_list(); tc = us(C["t_call"])
        talk = [t in resp_by_turn or bool(x) for t, x in zip(tid, C["talk"].fill_null(False).to_list())]
        old = [int(r["agent"]) for r in ros.iter_rows(named=True) if r["joined"] <= NEW[a] and (r["left"] is None or NEW[a] < r["left"])
               and int(r["agent"]) not in NEW]
        mv = move[a]
        iso_talks = [i for i, t in enumerate(tid) if talk[i] and mv is not None and tc[i] < mv]
        iso_named = [i for i in iso_talks if resp_by_turn.get(tid[i], set()) & set(old)]
        first_rec, first_resp = {}, {}
        for i, t in enumerate(tid):
            for j in rec_by_turn.get(t, set()):
                first_rec.setdefault(j, (i, int(tc[i])))
            if talk[i]:
                for j in resp_by_turn.get(t, set()) & set(old):
                    first_resp.setdefault(j, (i, int(tc[i])))
        for j in old:
            r_, s_ = first_rec.get(j), first_resp.get(j)
            pairs.append({"newcomer": a, "oldtimer": j, "first_rec_call": r_[0] if r_ else None,
                          "first_resp_call": s_[0] if s_ else None,
                          "resp_after_rec": (s_ is not None and r_ is not None and s_[0] >= r_[0]),
                          "resp_without_rec": (s_ is not None and r_ is None),
                          "resp_before_rec": (s_ is not None and r_ is not None and s_[0] < r_[0]),
                          "resp_minutes_after_move": (s_[1] - mv) / 6e7 if (s_ and mv) else None})
        # N32c: first 2 h after the move
        if mv is not None:
            for i, t in enumerate(tid):
                if not talk[i] or not (mv <= tc[i] < mv + 2 * 3600 * US):
                    continue
                recent = set().union(*[rec_by_turn.get(tid[q], set()) for q in range(max(0, i - 2), i + 1)])
                rs = resp_by_turn.get(t, set())
                for j in old:
                    c_rows.append((a, j, j in recent, j in rs))
        out["newcomers"][str(a)] = {"move_utc_us": mv, "n_calls": len(tid), "n_talk_calls": int(sum(talk)),
                                    "isolation_talks": len(iso_talks), "isolation_talks_naming_oldtimer": len(iso_named),
                                    "n_oldtimers": len(old)}
    P = pl.DataFrame(pairs)
    resp = P.filter(pl.col("first_resp_call").is_not_null())
    out["N32a"] = {"isolation_talks": int(sum(v["isolation_talks"] for v in out["newcomers"].values())),
                   "naming_oldtimer": int(sum(v["isolation_talks_naming_oldtimer"] for v in out["newcomers"].values()))}
    out["N32b"] = {"n_pairs": P.height, "n_responding": resp.height,
                   "after_rec": int(resp["resp_after_rec"].sum()), "before_rec": int(resp["resp_before_rec"].sum()),
                   "without_rec": int(resp["resp_without_rec"].sum()),
                   "share_after": float(resp["resp_after_rec"].mean()) if resp.height else None,
                   "median_minutes_after_move": float(resp["resp_minutes_after_move"].drop_nulls().median() or np.nan) if resp.height else None}
    if c_rows:
        Cdf = pl.DataFrame(c_rows, schema=["n", "j", "recent", "y"], orient="row")
        g = Cdf.group_by("recent").agg(pl.col("y").mean().alias("rate"), pl.len().alias("n")).sort("recent")
        out["N32c"] = {str(r["recent"]): {"rate": float(r["rate"]), "n": int(r["n"])} for r in g.iter_rows(named=True)}
        # newcomer-stratified (Mantel-Haenszel style) risk difference
        rd, w = [], []
        for (nn,), sub in Cdf.group_by(["n"]):
            r1 = sub.filter(pl.col("recent")); r0 = sub.filter(~pl.col("recent"))
            if r1.height and r0.height:
                rd.append(r1["y"].mean() - r0["y"].mean()); w.append(r1.height * r0.height / sub.height)
        out["N32c"]["stratified_rd"] = float(np.average(rd, weights=w)) if rd else None
    out["pairs"] = pairs
    out["response"] = "mentions only" if ONLY_MENTIONS else "mentions or reply-parent author"
    jdump(out, OUT1B / ("NE32_mentions.json" if ONLY_MENTIONS else "NE32.json"))
    print({k: v for k, v in out.items() if k not in ("pairs",)}, flush=True)


if __name__ == "__main__":
    main()
