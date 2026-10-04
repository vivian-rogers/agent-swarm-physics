"""Shared visibility helpers on the DQ1 context ledger: "seen iff posted before the producing call's t_call".

Consolidates the round-1b copies in
  H28  hypotheses/H28-links-spread-herding/scheme/build_r1b.py (receipts -> exposures.t_vis; receiving-call list)
       hypotheses/H28-links-spread-herding/analysis/h28core.py: visibility (first receiving call with t_call > t_post)
  H32  hypotheses/H32-information-current-leaders/analysis/ic_core.py: ledger_calls, call_start_of
  H34  hypotheses/H34-idea-cascades/scheme/h34core.py: ledger_arrays (TS receipts, cs producing call)
The rule is unchanged; only the code moved.

Definitions (t_call = the call's context-assembly time in `call_windows`):
  receiving call of (message m, recipient a)  the one ledger call of a whose new items include m
                                              (`context_ledger_items`; windows tile time, so it is unique)
  producing call of an agent message m         the sender's latest call with t_call < t_m (strict); if none within
                                              `stale_s` (6 h) the fallback is t_m - `guard_s` (1 s), flagged
  seen                                         x is seen by the call that produced m iff x's receiving call (for m's
                                              author) has t_call <= the producing call's t_call (H34); on the posting
                                              clock, iff x was posted in the author's room before that t_call (H32)
  in flight / unread                           posted in the author's room but not yet seen by the producing call

Table (data/processed/shared/, zstd parquet, no text, ALL days, `holdout` flags locked-holdout days; exploratory users
filter `~holdout`):
  producing_calls.parquet  one row per agent chat message: msg (chat_core row), message_id, agent, t, pt_date,
                           goal_no, holdout, turn_id_prod, t_call_prod, prod_kind, prod_talk (the call's talk flag:
                           99.6-100%; kind is the call's other action, e.g. wait in regime I), prod_age_s (t - t_call_prod),
                           prod_fallback (no call within 6 h: t_call_prod = t - 1 s, turn_id_prod null)
Functions: load_calls, receipts, producing_call, first_call_after, seen_by_receipt, seen_by_time.

Usage: uv run python infra/shared/visibility.py            (build producing_calls.parquet)
       uv run python infra/shared/visibility.py --verify   (H28 exposures/calls on disk; H34 ledger_arrays and H32
                                                            call_start_of in memory; read-only imports)
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
           "RAYON_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import datetime as dt  # noqa: E402
import importlib.util  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUT, ROOT, holdout_mask, write_provenance  # noqa: E402

SH = OUT
US = 1_000_000
STALE_S = 6 * 3600          # H32 / H34: no call within 6 h before a message -> fallback
GUARD_S = 1.0               # H32 min_gap_s / H34 GUARD_US: fallback producing time = t_msg - 1 s


def log(*a):
    print(*a, flush=True)


def _us(s: pl.Series) -> np.ndarray:
    return s.dt.epoch("us").to_numpy().astype(np.int64)


def _to_dt(x):
    if x is None or isinstance(x, dt.datetime):
        return x
    return dt.datetime.fromtimestamp(float(x), dt.timezone.utc)


def holdout_flags(df: pl.DataFrame, date_col: str = "pt_date", goal_col: str = "goal_no") -> pl.Series:
    """Locked-holdout flag per row (common.holdout_mask over the distinct (date, goal) pairs)."""
    u = df.select(date_col, goal_col).unique()
    hm = holdout_mask(u[date_col].to_list(), u[goal_col].to_list())
    u = u.with_columns(pl.Series("_h", hm))
    return df.select(date_col, goal_col).join(u, on=[date_col, goal_col], how="left", maintain_order="left")["_h"]


# ----------------------------------------------------------------------------------------------- loaders
def calls_frame(agents=None, t0=None, t1=None, *, receiving_only: bool = False, exclude_holdout: bool = False,
                goal_nos=None) -> pl.DataFrame:
    """call_windows rows (turn_id, agent, t_call, pt_date, goal_no, holdout, kind, talk, ctx_mode), sorted by agent,
    t_call. receiving_only drops summary calls (consolidation / session stop), which receive no items (H28's list)."""
    cw = pl.scan_parquet(SH / "call_windows.parquet").select("turn_id", "agent", "t_call", "pt_date", "goal_no", "holdout",
                                                             "kind", "talk", "ctx_mode")
    if agents is not None:
        cw = cw.filter(pl.col("agent").is_in([int(a) for a in agents]))
    if t0 is not None:
        cw = cw.filter(pl.col("t_call") >= _to_dt(t0))
    if t1 is not None:
        cw = cw.filter(pl.col("t_call") <= _to_dt(t1))
    if receiving_only:
        cw = cw.filter(pl.col("ctx_mode").cast(pl.String) != "summary")
    if exclude_holdout:
        cw = cw.filter(~pl.col("holdout"))
    if goal_nos is not None:
        cw = cw.filter(pl.col("goal_no").is_in(list(goal_nos)))
    return cw.collect().sort("agent", "t_call", "turn_id")


def load_calls(agents=None, t0=None, t1=None, *, receiving_only: bool = False, exclude_holdout: bool = False,
               goal_nos=None, with_turn_id: bool = False) -> dict:
    """agent -> sorted t_call (epoch us, int64) [, turn_id aligned]. t0 / t1: datetime or epoch seconds (inclusive)."""
    cw = calls_frame(agents, t0, t1, receiving_only=receiving_only, exclude_holdout=exclude_holdout, goal_nos=goal_nos)
    out = {}
    for (a,), g in cw.group_by(["agent"], maintain_order=True):
        t = _us(g["t_call"])
        out[int(a)] = (t, g["turn_id"].to_numpy()) if with_turn_id else t
    return out


def receipts(message_ids=None, *, agents=None, t0=None, t1=None, goal_nos=None, exclude_holdout: bool = False,
             item_cols=()) -> pl.DataFrame:
    """One row per (message, recipient): the receiving call. Columns: message_id, recipient, turn_id, t_call,
    rc_date (the call's pt_date), rc_goal, rc_holdout, plus `item_cols` from context_ledger_items (e.g. age_s, ment,
    uncertain, kind, sender). The filters restrict the receiving CALL (window, goal, holdout), as H28 / H34 (t window)
    and H06 (goal) did; a pair whose receiving call falls outside them has no row."""
    it = pl.scan_parquet(SH / "context_ledger_items.parquet").select("turn_id", "message_id", *item_cols)
    if message_ids is not None:
        ids = pl.Series("message_id", list(message_ids), dtype=pl.String)
        it = it.filter(pl.col("message_id").is_in(ids.implode()))
    cw = pl.scan_parquet(SH / "call_windows.parquet").select("turn_id", pl.col("agent").alias("recipient"), "t_call",
                                                             pl.col("pt_date").alias("rc_date"),
                                                             pl.col("goal_no").alias("rc_goal"),
                                                             pl.col("holdout").alias("rc_holdout"))
    if agents is not None:
        cw = cw.filter(pl.col("recipient").is_in([int(a) for a in agents]))
    if t0 is not None:
        cw = cw.filter(pl.col("t_call") >= _to_dt(t0))
    if t1 is not None:
        cw = cw.filter(pl.col("t_call") <= _to_dt(t1))
    if goal_nos is not None:
        cw = cw.filter(pl.col("rc_goal").is_in(list(goal_nos)))
    if exclude_holdout:
        cw = cw.filter(~pl.col("rc_holdout"))
    r = it.join(cw, on="turn_id", how="inner").collect()
    return r.select("message_id", "recipient", "turn_id", "t_call", "rc_date", "rc_goal", "rc_holdout", *item_cols)


# ----------------------------------------------------------------------------------------------- the rule
def producing_call(t_us: np.ndarray, sender: np.ndarray, calls: dict, stale_s: float = STALE_S, guard_s: float = GUARD_S,
                   turn_ids: bool = False):
    """t_call (us) of the call that produced each message: the sender's latest call with t_call < t (strict).
    No call within stale_s -> t - guard_s and fallback=True. `calls`: load_calls(...) (with_turn_id=True if turn_ids).
    Rows with sender < 0 (humans, automated) get the fallback. Returns (t_prod, fallback[, turn_id_prod (-1 = none)])."""
    t_us = np.asarray(t_us, dtype=np.int64)
    sender = np.asarray(sender)
    out = t_us - int(round(guard_s * US))
    fb = np.ones(len(t_us), dtype=bool)
    tid = np.full(len(t_us), -1, dtype=np.int64)
    stale = int(round(stale_s * US))
    for a in np.unique(sender):
        if a < 0:
            continue
        v = calls.get(int(a))
        if v is None:
            continue
        ca, ta = v if isinstance(v, tuple) else (v, None)
        if len(ca) == 0:
            continue
        idx = np.flatnonzero(sender == a)
        k = np.searchsorted(ca, t_us[idx], side="left") - 1
        ok = k >= 0
        ok &= (t_us[idx] - ca[np.clip(k, 0, None)]) <= stale
        out[idx[ok]] = ca[k[ok]]
        fb[idx[ok]] = False
        if ta is not None:
            tid[idx[ok]] = ta[k[ok]]
    return (out, fb, tid) if turn_ids else (out, fb)


def first_call_after(t_post_us: np.ndarray, recipient: np.ndarray, calls: dict) -> np.ndarray:
    """H28's visibility on the posting clock: the recipient's first call with t_call > t_post (us); -1 if none.
    Pass receiving calls (load_calls(..., receiving_only=True))."""
    t_post_us = np.asarray(t_post_us, dtype=np.int64)
    recipient = np.asarray(recipient)
    out = np.full(len(t_post_us), -1, np.int64)
    for a in np.unique(recipient):
        v = calls.get(int(a))
        if v is None:
            continue
        tv = v[0] if isinstance(v, tuple) else v
        if len(tv) == 0:
            continue
        m = np.flatnonzero(recipient == a)
        j = np.searchsorted(tv, t_post_us[m], "right")
        ok = j < len(tv)
        out[m[ok]] = tv[j[ok]]
    return out


def seen_by_receipt(t_recv_us, t_prod_us):
    """H34: source x is seen by the producing call iff x's receiving call (for that author) has t_call <= t_prod.
    Use a large sentinel (e.g. INF) for t_recv when the author never received x."""
    return np.asarray(t_recv_us) <= np.asarray(t_prod_us)


def seen_by_time(t_src_us, t_prod_us):
    """H32: same-room source x is seen by the producing call iff it was posted before that call's t_call."""
    return np.asarray(t_src_us) < np.asarray(t_prod_us)


# ----------------------------------------------------------------------------------------------- table
def build_producing_calls() -> pl.DataFrame:
    chat = (pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "pt_date", "goal_no", "speaker_kind", "agent"])
            .with_row_index("msg")
            .filter((pl.col("speaker_kind").cast(pl.String) == "agent") & pl.col("agent").is_not_null()))
    cw = calls_frame()
    calls = {}
    for (a,), g in cw.group_by(["agent"], maintain_order=True):
        calls[int(a)] = (_us(g["t_call"]), g["turn_id"].to_numpy())
    tp, fb, tid = producing_call(_us(chat["t"]), chat["agent"].to_numpy(), calls, turn_ids=True)
    kinds = cw.select("turn_id", pl.col("kind").alias("prod_kind"), pl.col("talk").alias("prod_talk"))
    out = chat.with_columns(pl.Series("turn_id_prod", tid, dtype=pl.Int64),
                            pl.Series("t_call_prod", tp).cast(pl.Datetime("us", "UTC")),
                            pl.Series("prod_fallback", fb))
    out = out.with_columns(pl.when(pl.col("turn_id_prod") >= 0).then(pl.col("turn_id_prod")).otherwise(None)
                           .cast(pl.Int32).alias("turn_id_prod"))
    out = out.join(kinds, left_on="turn_id_prod", right_on="turn_id", how="left", maintain_order="left")
    out = out.with_columns(((pl.col("t") - pl.col("t_call_prod")).dt.total_microseconds() / 1e6).cast(pl.Float32)
                           .alias("prod_age_s"))
    out = out.with_columns(holdout_flags(out).alias("holdout"))
    return out.select(pl.col("msg").cast(pl.UInt32), "message_id", pl.col("agent").cast(pl.Int8), "t", "pt_date",
                      "goal_no", "holdout", "turn_id_prod", "t_call_prod", "prod_kind", "prod_talk", "prod_age_s",
                      "prod_fallback")


def main():
    t0 = time.time()
    pc = build_producing_calls()
    p = SH / "producing_calls.parquet"
    pc.write_parquet(p, compression="zstd", compression_level=9)
    nh = pc.filter(~pl.col("holdout"))
    summ = {"rows": pc.height, "fallback_share_nonholdout": float(nh["prod_fallback"].mean()),
            "prod_talk_share_nonholdout": float(nh.filter(~pl.col("prod_fallback"))["prod_talk"].mean()),
            "prod_age_s_median_nonholdout": float(nh.filter(~pl.col("prod_fallback"))["prod_age_s"].median())}
    write_provenance("visibility", ["chat_core", "call_windows"],
                     {"rule": "producing call = sender's latest call with t_call < t_msg (strict); none within stale_s "
                              "-> t_msg - guard_s, flagged", "stale_s": STALE_S, "guard_s": GUARD_S,
                      "calls": "all call_windows rows (any ctx_mode, holdout included; rows flagged by message day)",
                      "holdout": "all days, flagged", "sources": "H28 build_r1b / h28core.visibility; H32 ic_core."
                      "ledger_calls / call_start_of; H34 h34core.ledger_arrays (rule unchanged)", "summary": summ})
    log(f"producing_calls.parquet: {pc.height} rows, {p.stat().st_size / 1e6:.1f} MB, {time.time() - t0:.0f}s")
    log(json.dumps(summ))


# ----------------------------------------------------------------------------------------------- verification
def load_ro(name: str, path: Path):
    """Import a hypothesis module read-only (no bytecode written into the hypothesis folder)."""
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _verify_h28() -> dict:
    """Recompute H28's round-1b exposures (receipts of its link messages) and receiving-call lists; compare to disk."""
    base = ROOT / "data/processed/H28-links-spread-herding"
    roster = pl.read_parquet(SH / "roster.parquet")
    cc = set(roster.filter(pl.col("claude_code"))["agent"].to_list())
    chat_ids = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id"]).with_row_index("msg").with_columns(
        pl.col("msg").cast(pl.UInt32))
    res = {}
    for d in sorted((base / "r1b").glob("G*")):
        if not (d / "exposures.parquet").exists():
            continue
        meta = json.loads((base / d.name / "meta.json").read_text())
        days = meta["days"]
        t0 = days[0]["ws_ms"] / 1000 - 7200
        t1 = days[-1]["we_ms"] / 1000 + 26 * 3600
        links = pl.read_parquet(base / d.name / "links.parquet").select("msg", "sender").unique("msg")
        lm = links.join(chat_ids, on="msg", how="left")
        r = receipts(lm["message_id"].to_list(), t0=t0, t1=t1)
        assert not r["rc_holdout"].any()
        r = (r.join(lm, on="message_id").filter((pl.col("recipient").cast(pl.Int16) != pl.col("sender"))
                                                 & ~pl.col("recipient").is_in(list(cc)))
             .select(pl.col("msg").cast(pl.UInt32), pl.col("recipient").cast(pl.Int8),
                     pl.col("t_call").dt.epoch("ms").alias("t_vis_ms")).sort("msg", "recipient"))
        old = pl.read_parquet(d / "exposures.parquet").sort("msg", "recipient")
        same_exp = old.equals(r)
        cl = load_calls(t0=t0, t1=t1, receiving_only=True)
        mine = pl.DataFrame({"agent": np.concatenate([np.full(len(v), a) for a, v in cl.items()]).astype(np.int8),
                             "t_ms": np.concatenate(list(cl.values())) // 1000}).sort("agent", "t_ms")
        oc = pl.read_parquet(d / "calls.parquet").sort("agent", "t_ms")
        same_calls = oc.equals(mine)
        res[d.name] = {"exposures": old.height, "identical": bool(same_exp),
                       "calls": oc.height, "calls_identical": bool(same_calls)}
        if not same_exp:
            j = old.join(r, on=["msg", "recipient"], how="full", coalesce=True, suffix="_s")
            res[d.name]["mismatch"] = {"only_h28": int(j["t_vis_ms_s"].is_null().sum()),
                                       "only_shared": int(j["t_vis_ms"].is_null().sum()),
                                       "t_diff": int((j["t_vis_ms"] != j["t_vis_ms_s"]).sum())}
    return res


def _period_chat(g: int) -> tuple[pl.DataFrame, list]:
    cal = pl.read_parquet(SH / "calendar.parquet").filter(pl.col("goal_no") == g)
    days = cal["pt_date"].to_list()
    hm = holdout_mask(days, [g] * len(days))
    days = sorted(d for d, h, f in zip(days, hm, cal["holdout"].fill_null(False).to_list()) if not (h or f))
    chat = (pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "pt_date", "goal_no", "room", "speaker_kind",
                                                               "agent"])
            .with_row_index("msg").filter((pl.col("goal_no") == g) & pl.col("pt_date").is_in(days)).sort("msg"))
    return chat, days


def _verify_h34(goals) -> dict:
    """H34 ledger_arrays (in memory): TS = receiving-call t_call per (message, agent); cs = producing call."""
    h34 = load_ro("h34core_ro", ROOT / "hypotheses/H34-idea-cascades/scheme/h34core.py")
    n_agents = int(pl.read_parquet(SH / "roster.parquet")["agent"].max()) + 1
    res = {}
    for g in goals:
        chat, _days = _period_chat(g)
        if chat.height == 0:
            continue
        kind = chat["speaker_kind"].cast(pl.Utf8).replace_strict(h34.KIND, default=3).to_numpy().astype(np.int8)
        sender = chat["agent"].fill_null(-1).to_numpy().astype(np.int16)
        t = _us(chat["t"])
        t0 = chat["t"].min() - dt.timedelta(hours=8)
        t1 = chat["t"].max() + dt.timedelta(hours=1)
        ref = h34.ledger_arrays(chat, t, kind, sender, n_agents, t0, t1)
        # shared
        cl = load_calls(t0=t0, t1=t1)
        snd = np.where(kind == 0, sender, -1)
        cs, fb = producing_call(t, snd, cl)
        cs = np.where(kind == 0, cs, t - int(GUARD_S * US))
        fb = np.where(kind == 0, fb, True)
        r = receipts(chat["message_id"].to_list(), t0=t0, t1=t1)
        pos = dict(zip(chat["message_id"].to_list(), range(chat.height)))
        TS = np.full((chat.height, n_agents), h34.INF_US, dtype=np.int64)
        if r.height:
            TS[np.array([pos[m] for m in r["message_id"].to_list()]), r["recipient"].to_numpy().astype(np.int64)] = _us(r["t_call"])
        res[f"G{g:02d}"] = {"messages": chat.height, "receipts": int(r.height),
                            "TS_identical": bool(np.array_equal(TS, ref["TS"])),
                            "cs_identical": bool(np.array_equal(cs, ref["cs"])),
                            "cs_fallback_identical": bool(np.array_equal(fb, ref["cs_fb"])),
                            "n_cs_diff": int((cs != ref["cs"]).sum())}
    return res


def _verify_h32(goals) -> dict:
    """H32 call_start_of (in memory) on agent messages: shared producing_call vs its non-holdout ledger_calls."""
    ic = load_ro("ic_core_ro", ROOT / "hypotheses/H32-information-current-leaders/analysis/ic_core.py")
    from types import SimpleNamespace
    res = {}
    for g in goals:
        chat, _days = _period_chat(g)
        chat = chat.filter(pl.col("speaker_kind").cast(pl.Utf8) == "agent")
        if chat.height == 0:
            continue
        ts = chat["t"].dt.epoch("us").to_numpy() / 1e6
        agents = sorted(set(chat["agent"].to_list()))
        t0, t1 = ts.min() - 8 * 3600, ts.max() + 30 * 3600
        calls_s = ic.ledger_calls(agents, t0, t1)
        sk = SimpleNamespace(t=ts, spk=chat["agent"].to_numpy(), meta={"calls": calls_s})
        ref = ic.call_start_of(sk, np.arange(chat.height))
        cl = load_calls(agents, t0, t1, exclude_holdout=True)
        cs, _fb = producing_call(_us(chat["t"]), chat["agent"].to_numpy(), cl)
        d = np.abs(cs / 1e6 - ref)
        res[f"G{g:02d}"] = {"messages": chat.height, "max_abs_diff_s": float(d.max()), "n_diff_gt_1ms": int((d > 1e-3).sum())}
    return res


def verify():
    t0 = time.time()
    out = {"H28": _verify_h28()}
    log("H28", json.dumps(out["H28"]))
    out["H34"] = _verify_h34([5, 18, 38])
    log("H34", json.dumps(out["H34"]))
    out["H32"] = _verify_h32([18, 38])
    log("H32", json.dumps(out["H32"]))
    # the table itself agrees with the in-memory rule
    pc = pl.read_parquet(SH / "producing_calls.parquet")
    chat, _ = _period_chat(38)
    a = chat.filter(pl.col("speaker_kind").cast(pl.Utf8) == "agent")
    cs, _fb = producing_call(_us(a["t"]), a["agent"].to_numpy(), load_calls())
    sub = pc.filter(pl.col("message_id").is_in(a["message_id"].implode())).sort("msg")
    out["table_vs_function_G38"] = bool(np.array_equal(_us(sub["t_call_prod"]), cs))
    log("table_vs_function_G38", out["table_vs_function_G38"], f"{time.time() - t0:.0f}s")
    return out


if __name__ == "__main__":
    if "--verify" in sys.argv:
        verify()
    else:
        main()
