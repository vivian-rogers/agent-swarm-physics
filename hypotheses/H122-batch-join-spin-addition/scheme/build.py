"""H122 scheme: join events (single or batch) and, per eligible non-holdout event, the incumbents' receiving calls in
the PRE / P12 / F37 windows with reads split by sender class (newcomer vs incumbent-class), matched-lag split,
in-flight placebo counts, exogenous items and call class. Codes only (no text).

Output: data/processed/H122-batch-join-spin-addition/events.parquet (all events, eligibility), calls/<event>.parquet,
_provenance.json.

    uv run python hypotheses/H122-batch-join-spin-addition/scheme/build.py

Holdout: windows use non-holdout calendar days only; every day used is asserted twice (calendar.holdout and
common.holdout_mask). NE33's days 1-2 (2026-09-03/04) are refused in exploration (confirmation-only; see the card).
`build_event(..., allow_holdout=True)` is called only by analysis/confirm.py (guarded).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import git_commit, holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H122-batch-join-spin-addition"
MIN_CALLS = 30
PRE_MAX, PRE_LOOK, RECENT_JOIN = 5, 10, 7
NE33_P12 = {"2026-09-03", "2026-09-04"}
WAKE = {"pause", "pause_early", "first_of_day", "after_summary", "session_start", "marker"}


def events_table(cal: pl.DataFrame, roster: pl.DataFrame) -> pl.DataFrame:
    """Join events from roster join dates and calendar active days (metadata only; no call data)."""
    cal = cal.sort("pt_date").with_row_index("ix")
    days = cal["pt_date"].to_list()
    hold = dict(zip(days, cal["holdout"].to_list()))
    reg = dict(zip(days, cal["regime"].cast(pl.String).to_list()))
    goal = dict(zip(days, cal["goal_no"].to_list()))
    j = (roster.filter(~pl.col("claude_code") & pl.col("joined").is_not_null()
                       & (pl.col("joined") > days[0])).select("agent", "name", "joined").sort("joined"))
    ix_of = []
    for d in j["joined"].to_list():
        k = int(np.searchsorted(np.array(days), d))
        ix_of.append(k if k < len(days) else None)
    j = j.with_columns(pl.Series("ix1", ix_of, dtype=pl.Int32)).filter(pl.col("ix1").is_not_null()).sort("ix1")
    ev, cur = [], None
    for r in j.to_dicts():
        if cur is not None and r["ix1"] - cur["last_ix"] <= 1:
            cur["agents"].append(r["agent"]); cur["names"].append(r["name"]); cur["last_ix"] = r["ix1"]
        else:
            cur = {"ix1": r["ix1"], "last_ix": r["ix1"], "agents": [r["agent"]], "names": [r["name"]]}
            ev.append(cur)
    rows = []
    for n, e in enumerate(ev):
        i1 = e["ix1"]
        nxt = ev[n + 1]["ix1"] if n + 1 < len(ev) else len(days)
        d1 = days[i1]
        r1 = reg[d1]
        pre = [days[i] for i in range(max(0, i1 - PRE_LOOK), i1) if not hold[days[i]] and reg[days[i]] == r1][-PRE_MAX:]
        p12 = [days[i] for i in (i1, i1 + 1) if i < len(days)]
        f37_all = [days[i] for i in range(i1 + 2, min(i1 + 7, len(days)))]
        f37_cut = [days[i] for i in range(i1 + 2, min(i1 + 7, nxt, len(days)))]
        f37 = [d for d in f37_cut if not hold[d] and reg[d] == r1]
        p12_ok = len(p12) == 2 and not any(hold[d] for d in p12) and all(reg[d] == r1 for d in p12)
        why = []
        if len(pre) < 2: why.append("pre<2")
        if not p12_ok: why.append("p12 held out or regime change")
        if len(f37) < 3: why.append("f37<3")
        if any(hold[d] for d in f37_cut): why.append("f37 window touches holdout")
        if set(p12) & NE33_P12: why.append("NE33 confirmation-only")
        label = {"2025-08-18": "NE27", "2026-07-09": "NE32", "2026-09-03": "NE33"}.get(d1, f"J{d1}")
        rows.append({"event": label, "day1": d1, "goal_no": goal[d1], "regime": r1, "newcomers": e["agents"],
                     "names": e["names"], "n_new": len(e["agents"]), "pre": pre, "p12": p12, "f37": f37,
                     "f37_cut_at_next": nxt < i1 + 7, "eligible_windows": not [w for w in why if w != "f37 window touches holdout"],
                     "why_not": "; ".join(why), "ix1": i1})
    return pl.DataFrame(rows)


def load_shared(allow_holdout: bool = False):
    cc_agents = pl.read_parquet(SH / "roster.parquet").filter(pl.col("claude_code"))["agent"].to_list()
    cw = (pl.scan_parquet(SH / "call_windows.parquet")
          .filter((pl.lit(allow_holdout) | ~pl.col("holdout")) & (pl.col("ctx_mode") != "summary"))
          .select("turn_id", "agent", "pt_date", "holdout", "talk", "ctx_mode", "t_call", "t_first", "gap_kind")
          .collect())
    lt = (pl.scan_parquet(SH / "context_ledger_turns.parquet")
          .filter(pl.lit(allow_holdout) | ~pl.col("holdout"))
          .select("turn_id", "room", "n_human", "n_nudge", "n_nudge_me").collect())
    cc = (pl.scan_parquet(SH / "chat_core.parquet").filter(pl.col("speaker_kind") == "agent")
          .select("message_id", "t", "pt_date", "room", "agent").collect()
          .join(pl.read_parquet(SH / "chat_mentions_clean.parquet", columns=["message_id", "mentions_roster"]),
                on="message_id", how="left"))
    return cw, lt, cc, cc_agents


def build_event(e: dict, cw, lt, cc, cc_agents, cal, out_dir: Path | None = None, allow_holdout: bool = False):
    days = list(e["pre"]) + list(e["p12"]) + list(e["f37"])
    if not allow_holdout:
        gmap = dict(zip(cal["pt_date"].to_list(), cal["goal_no"].to_list()))
        assert not any(holdout_mask(days, [gmap[d] for d in days])), "holdout day"
        assert not cal.filter(pl.col("pt_date").is_in(days) & pl.col("holdout")).height, "calendar holdout"
        assert not (set(e["p12"]) & NE33_P12), "NE33 days 1-2 are confirmation-only"
    win = {**{d: 0 for d in e["pre"]}, **{d: 1 for d in e["p12"]}, **{d: 2 for d in e["f37"]}}
    newc = set(e["newcomers"])
    c = (cw.filter(pl.col("pt_date").is_in(days)).join(lt, on="turn_id", how="left")
         .sort("agent", "pt_date", "t_call", "turn_id"))
    nad = c.group_by("agent", "pt_date").agg(pl.len().alias("n"))
    act = nad.filter(pl.col("n") >= MIN_CALLS)
    Nwin = (act.with_columns(pl.col("pt_date").replace_strict(win, return_dtype=pl.Int8).alias("win"))
            .group_by("win", "pt_date").agg(pl.len().alias("N")).group_by("win").agg(pl.col("N").mean()).sort("win"))
    recent = set(e.get("recent_joiners", []))
    pre_set = set(act.filter(pl.col("pt_date").is_in(e["pre"]))["agent"].to_list())
    p12_set = set(act.filter(pl.col("pt_date").is_in(e["p12"]))["agent"].to_list())
    inc = sorted((pre_set & p12_set) - newc - recent - set(cc_agents))
    c = c.filter(pl.col("agent").is_in(inc))
    if not allow_holdout:
        assert not c["holdout"].any()
    us = lambda col: (pl.col(col).dt.epoch("us") / 1e6)  # noqa: E731
    c = c.with_columns(us("t_call").alias("tc"), us("t_first").alias("tf"),
                       pl.col("pt_date").replace_strict(win, return_dtype=pl.Int8).alias("win"),
                       pl.int_range(pl.len()).over("agent", "pt_date").cast(pl.Int32).alias("k"),
                       pl.col("talk").cast(pl.Int8).alias("Y"),
                       pl.col("talk").shift(1).over("agent", "pt_date").cast(pl.Int8).fill_null(0).alias("Yprev"),
                       ((pl.col("ctx_mode") == "chat").cast(pl.Int8) * 2
                        + pl.col("gap_kind").cast(pl.String).is_in(list(WAKE)).cast(pl.Int8)).alias("cls"))
    c = c.with_columns((pl.col("tf") - pl.col("tc")).clip(1.0, 120.0).fill_null(1.0).alias("dc"),
                       pl.col("tc").min().over("pt_date").alias("t_day0"))
    c = c.with_columns(((pl.col("tc") - pl.col("t_day0")) // 3600).cast(pl.Int16).alias("hour"))
    # reads from ledger items (kind agent) at these calls
    it = (pl.scan_parquet(SH / "context_ledger_items.parquet").filter(pl.col("kind") == "agent")
          .filter(pl.col("turn_id").is_in(c["turn_id"].implode()))
          .select("turn_id", "sender", "age_s", "ment").collect())
    it = it.join(c.select("turn_id", "dc"), on="turn_id", how="left").with_columns(
        pl.col("sender").is_in(list(newc)).alias("isN"), (pl.col("age_s") < pl.col("dc")).alias("isM"))
    agg = it.group_by("turn_id").agg(
        (~pl.col("isN") & pl.col("isM")).sum().alias("Rm_I"), (~pl.col("isN") & ~pl.col("isM")).sum().alias("Ro_I"),
        (pl.col("isN") & pl.col("isM")).sum().alias("Rm_N"), (pl.col("isN") & ~pl.col("isM")).sum().alias("Ro_N"),
        (pl.col("isN") & pl.col("ment")).sum().alias("RN_named"), (pl.col("isN") & ~pl.col("ment")).sum().alias("RN_unnamed"),
        (~pl.col("isN") & pl.col("ment")).sum().alias("RI_named"))
    c = c.join(agg, on="turn_id", how="left").with_columns(
        [pl.col(x).fill_null(0).cast(pl.Int16) for x in ("Rm_I", "Ro_I", "Rm_N", "Ro_N", "RN_named", "RN_unnamed", "RI_named")])
    # in-flight placebo: other agents' messages posted in the recipient's room in (t_call, t_call + d_c]
    m = cc.filter(pl.col("pt_date").is_in(days)).with_columns(us("t").alias("tm")).sort("tm")
    room_c = c["room"].fill_null(0).to_numpy()
    tc, dc, ag = c["tc"].to_numpy(), c["dc"].to_numpy(), c["agent"].to_numpy()
    P_I = np.zeros(c.height, np.int16); P_N = np.zeros(c.height, np.int16); PN_named = np.zeros(c.height, np.int16)
    mroom = m["room"].fill_null(0).to_numpy(); mt = m["tm"].to_numpy(); ma = m["agent"].to_numpy()
    mment = m["mentions_roster"].to_list()
    for rm in np.unique(room_c):
        sel = np.where(mroom == rm)[0]
        if not len(sel):
            continue
        t_r = mt[sel]
        rows = np.where(room_c == rm)[0]
        lo = np.searchsorted(t_r, tc[rows], side="right")
        hi = np.searchsorted(t_r, tc[rows] + dc[rows], side="right")
        for jj, r in enumerate(rows):
            for q in range(lo[jj], hi[jj]):
                s = sel[q]
                if ma[s] == ag[r]:
                    continue
                if ma[s] in newc:
                    P_N[r] += 1
                    if mment[s] is not None and int(ag[r]) in mment[s]:
                        PN_named[r] += 1
                else:
                    P_I[r] += 1
    c = c.with_columns(pl.Series("P_I", P_I), pl.Series("P_N", P_N), pl.Series("PN_named", PN_named),
                       pl.col("n_human").fill_null(0).cast(pl.Int16).alias("E_h"),
                       pl.col("n_nudge").fill_null(0).cast(pl.Int16).alias("E_n"),
                       pl.col("n_nudge_me").fill_null(0).cast(pl.Int16).alias("E_nme"))
    out = c.select("agent", "pt_date", "win", "hour", "k", "cls", "Y", "Yprev", "Rm_I", "Ro_I", "P_I", "Rm_N", "Ro_N",
                   "P_N", "RN_named", "RN_unnamed", "PN_named", "RI_named", "E_h", "E_n", "E_nme", "dc")
    base = out_dir or OUT
    (base / "calls").mkdir(parents=True, exist_ok=True)
    out.write_parquet(base / "calls" / f"{e['event']}.parquet", compression="zstd")
    Nd = dict(zip(Nwin["win"].to_list(), Nwin["N"].to_list()))
    return {"event": e["event"], "n_incumbents": len(inc), "incumbents": inc, "N_pre": Nd.get(0), "N_p12": Nd.get(1),
            "N_f37": Nd.get(2), "n_calls_pre": int((out["win"] == 0).sum()), "n_calls_p12": int((out["win"] == 1).sum()),
            "n_calls_f37": int((out["win"] == 2).sum())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--events-only", action="store_true")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    cal = pl.read_parquet(SH / "calendar.parquet")
    ros = pl.read_parquet(SH / "roster.parquet")
    ev = events_table(cal, ros)
    # recent joiners (joined in the 7 active days before day 1) are neither incumbents nor newcomers
    rec = []
    for r in ev.to_dicts():
        rj = [a2 for e2 in ev.to_dicts() if r["ix1"] - RECENT_JOIN <= e2["ix1"] < r["ix1"] for a2 in e2["newcomers"]]
        rec.append(rj)
    ev = ev.with_columns(pl.Series("recent_joiners", rec, dtype=pl.List(pl.Int8)))
    meta = []
    if not a.events_only:
        cw, lt, cc, cca = load_shared()
        for e in ev.filter(pl.col("eligible_windows")).to_dicts():
            r = build_event(e, cw, lt, cc, cca, cal)
            meta.append(r)
            print(r["event"], r["n_incumbents"], r["n_calls_pre"], r["n_calls_p12"], r["n_calls_f37"], flush=True)
    if meta:
        ev = ev.join(pl.DataFrame(meta), on="event", how="left")
    ev.write_parquet(OUT / "events.parquet")
    prov = {"built_by": "hypotheses/H122-batch-join-spin-addition/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": "shared tables (DQ1 context ledger)",
                        "tables": ["call_windows", "context_ledger_turns", "context_ledger_items", "chat_core",
                                   "chat_mentions_clean", "calendar", "roster"]}],
            "params": {"min_calls": MIN_CALLS, "pre_max": PRE_MAX, "pre_look": PRE_LOOK, "recent_join": RECENT_JOIN,
                       "ne33_refused": sorted(NE33_P12), "holdout": "excluded, asserted twice"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))


if __name__ == "__main__":
    main()
