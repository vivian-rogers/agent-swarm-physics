"""Idle gates: one row per model call that follows an idle call (a "gate"), with two trap clocks, input reads and
escape outcomes. Shared by H72 (trap aging vs input starvation) and H60 (index nudge policy).

Definitions (call clock; DQ1 context ledger):
  sequence      an agent-day's non-summary calls (`call_windows.ctx_mode != "summary"`), sorted by `t_call`;
                Claude Code agent and held-out days (common.holdout_mask) excluded.
  idle call     kind in {pause, wait} and not talking. Every other call in the sequence is active (H43, H59 rule).
  gate          a call whose previous call (same agent-day) is idle. The agent decides at the gate whether to act.
  current reads ledger items (`context_ledger_items`, not omitted) that enter the context at the gate itself.
  novel item    an item of kind agent, human or nudge (pause/resume bookends are not input).
                Variants: peer (agent + human), content (novel minus agent items that DQ5 flags as a restatement:
                self_repeat or cross_echo under either embedding model), directed (an item that names the recipient,
                or a nudge whose leading @ is the recipient).
  nudge target  the leading @ of a nudge (H35 rule; Known issue "a nudge's target is its leading @"): the text starts
                with '@' and the longest roster-name match at position 1, among agents on the roster that day.
                Text is read in memory only and never written.
  trap clocks   a_any  = t_call(gate) - t_end(last active call before the gate)            [s]
                a_sus  = t_call(gate) - t_end(last call of the last sustained active run)   [s]
                         (sustained run = >= 3 consecutive active calls; H43 / H16 TS1r spirit)
                k_any, k_sus = gate index inside the trap (1 = first gate after the trap starts)
  starvation    s_<v>  = t_call(gate) - t_call(latest EARLIER call of the same agent-day that read >= 1 item of
                variant v) [s]; null when no such call today (then `s_<v>_none` is true and s is measured from the
                agent's first call of the day, `s_<v>_lc`).
  outcomes      y_any  = the gate call is active (a glance counts).
                y_sus  = the gate call and the next two calls are active (null when the day ends first).
                y_calls30 = active calls in [t_call, t_call + 30 min) (null when that window passes the calendar
                window end).
  covariates    prev_pause_s (declared duration of the previous pause), h_day (hours since the calendar window start),
                swarm_act10 (share of other present agents with an active call in the previous 10 min), room (ledger),
                last_run_len (calls in the last active run before the trap), in-flight placebo counts (messages by
                others posted in the gate's room in (t_call, t_call + 60 s] and during the gate call's model latency
                (t_call, t_call + latency_s, capped at 60 s], which the gate cannot have read).

Output: data/processed/shared/idle_gates/idle_gates.parquet (+ _provenance.json). Codes and numbers only, no text.
Usage:  uv run python infra/shared/idle_gates.py            build
        uv run python infra/shared/idle_gates.py --verify   brute-force recount on 40 random agent-days
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "4")

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import REVISION, git_commit, holdout_mask, mention_regexes  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SH = ROOT / "data/processed/shared"
OUT = SH / "idle_gates"
IDLE_KINDS = ("pause", "wait")
NOVEL_KINDS = ("agent", "human", "nudge")
SUS_LEN = 3
W30 = 30 * 60
INFLIGHT_S = 60


def leading_targets(message_ids: list[str]) -> dict:
    """message_id -> agent code of the nudge's leading @ (None if none)."""
    if not message_ids:
        return {}
    ids = pl.Series(message_ids)
    chat = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "pt_date"]).filter(pl.col("message_id").is_in(ids))
    txt = pl.read_parquet(SH / "chat_text.parquet", columns=["message_id", "text"]).filter(pl.col("message_id").is_in(ids))
    chat = chat.join(txt, on="message_id", how="left")
    ros = pl.read_parquet(SH / "roster.parquet").filter(~pl.col("claude_code"))
    pats = mention_regexes([{"id": int(a), "name": n} for a, n in ros.select("agent", "name").iter_rows()])
    span = {int(a): (j, l) for a, j, l in ros.select("agent", "joined", "left").iter_rows()}
    out = {}
    for mid, d, text in chat.select("message_id", "pt_date", "text").iter_rows():
        best, blen = None, 0
        if text and text.startswith("@"):
            for a, pat in pats.items():
                j, l = span[a]
                if not (j <= d and (l is None or d < l)):
                    continue
                mt = pat.match(text, 1)
                if mt and (mt.end() - mt.start()) > blen:
                    best, blen = a, mt.end() - mt.start()
        out[mid] = best
    return out


def load_calls(include_holdout: bool = False, goal_nos=None) -> pl.DataFrame:
    """Non-summary calls; held-out days only when include_holdout (confirmatory scripts, behind their own guard)."""
    ros = pl.read_parquet(SH / "roster.parquet").select("agent", "claude_code", "lab")
    cw = (pl.scan_parquet(SH / "call_windows.parquet")
          .filter(pl.col("ctx_mode") != "summary")
          .select("turn_id", "agent", "pt_date", "goal_no", "regime", "kind", "talk", "t_call", "t_end", "pause_s",
                  "gap_kind", "first_of_day", "latency_s", "dur_api_s")
          .collect())
    cw = cw.join(ros, on="agent", how="left").filter(~pl.col("claude_code").fill_null(False)).drop("claude_code")
    keys = cw.select("pt_date", "goal_no").unique()
    hm = holdout_mask(keys["pt_date"].to_list(), keys["goal_no"].to_list())
    keep = keys if include_holdout else keys.filter(~pl.Series(hm))
    if goal_nos is not None:
        keep = keep.filter(pl.col("goal_no").is_in(list(goal_nos)))
    cw = cw.join(keep, on=["pt_date", "goal_no"], how="inner")
    return cw.sort("agent", "pt_date", "t_call", "turn_id")


def item_counts(cw: pl.DataFrame) -> pl.DataFrame:
    """Per call: counts of current reads by class."""
    it = (pl.scan_parquet(SH / "context_ledger_items.parquet")
          .filter(~pl.col("omitted"))
          .select("turn_id", "message_id", "sender", pl.col("kind").cast(pl.Utf8), "ment")
          .collect()
          .join(cw.select("turn_id", "agent"), on="turn_id", how="inner"))
    # nudge leading targets
    nids = it.filter(pl.col("kind") == "nudge")["message_id"].unique().to_list()
    lt = leading_targets(nids)
    lead = pl.DataFrame({"message_id": list(lt.keys()), "lead": [v if v is not None else -1 for v in lt.values()]},
                        schema={"message_id": pl.Utf8, "lead": pl.Int16})
    it = it.join(lead, on="message_id", how="left")
    # DQ5 restatement flags for agent chat (either model)
    sf = (pl.read_parquet(SH / "statement_flags.parquet",
                          columns=["kind", "src_row", "self_repeat_bge", "self_repeat_gte", "cross_echo_bge", "cross_echo_gte"])
          .filter(pl.col("kind") == "chat"))
    ci = pl.read_parquet(SH / "embeddings/chat_index.parquet").with_row_index("src_row")
    sf = (sf.join(ci, on="src_row", how="inner")
          .select("message_id", (pl.col("self_repeat_bge") | pl.col("self_repeat_gte") | pl.col("cross_echo_bge")
                                 | pl.col("cross_echo_gte")).fill_null(False).alias("restated")))
    it = it.join(sf, on="message_id", how="left")
    novel = pl.col("kind").is_in(NOVEL_KINDS)
    lead_me = (pl.col("kind") == "nudge") & (pl.col("lead") == pl.col("agent").cast(pl.Int16))
    directed = (novel & pl.col("ment") & (pl.col("kind") != "nudge")) | lead_me
    agg = it.group_by("turn_id").agg(
        novel.sum().cast(pl.Int16).alias("n_novel"),
        pl.col("kind").is_in(["agent", "human"]).sum().cast(pl.Int16).alias("n_peer"),
        (novel & ~((pl.col("kind") == "agent") & pl.col("restated").fill_null(False))).sum().cast(pl.Int16).alias("n_content"),
        directed.sum().cast(pl.Int16).alias("n_dir"),
        lead_me.sum().cast(pl.Int16).alias("n_nudge_me"),
        ((pl.col("kind") == "nudge") & ~lead_me).sum().cast(pl.Int16).alias("n_nudge_other"),
        ((pl.col("kind") == "agent") & pl.col("ment")).sum().cast(pl.Int16).alias("n_ment_agent"),
        (pl.col("kind") == "human").sum().cast(pl.Int16).alias("n_human"),
        ((pl.col("kind") == "human") & pl.col("ment")).sum().cast(pl.Int16).alias("n_human_named"),
        (pl.col("kind") == "pause_resume").sum().cast(pl.Int16).alias("n_bookend"),
    )
    return agg


def swarm_activity(cw: pl.DataFrame) -> pl.DataFrame:
    """swarm_act10 per call: share of OTHER agents present that day with an active call in [t-10 min, t)."""
    out = []
    for (d,), g in cw.select("turn_id", "agent", "pt_date", "t_call", "active").group_by(["pt_date"]):
        t = g["t_call"].dt.epoch("s").to_numpy().astype(np.float64)
        ag = g["agent"].to_numpy()
        act = g["active"].to_numpy()
        agents = np.unique(ag)
        n_pres = len(agents)
        res = np.zeros(len(t))
        if n_pres > 1:
            cnt = np.zeros(len(t))
            for a in agents:
                ta = np.sort(t[(ag == a) & act])
                if len(ta) == 0:
                    continue
                hi = np.searchsorted(ta, t, side="left")
                lo = np.searchsorted(ta, t - 600, side="left")
                has = (hi - lo) > 0
                cnt += has & (ag != a)
            res = cnt / (n_pres - 1)
        out.append(pl.DataFrame({"turn_id": g["turn_id"], "swarm_act10": res.astype(np.float32),
                                 "n_present": np.full(len(t), n_pres, dtype=np.int16)}))
    return pl.concat(out)


def inflight(gates: pl.DataFrame) -> pl.DataFrame:
    """Messages by others (agents, humans) posted in the gate's room in (t_call, t_call + 60 s] (n_inflight60) and
    during the gate call's model latency, (t_call, t_call + latency] (n_inflight_call): the gate's context cannot hold
    them, and they cannot answer the gate's own output, which does not exist before the latency has elapsed."""
    ch = (pl.scan_parquet(SH / "chat_core.parquet")
          .filter(pl.col("speaker_kind").cast(pl.Utf8).is_in(["agent", "human"]))
          .select("t", "room", "agent").collect())
    res = np.zeros(gates.height, dtype=np.int16)
    res_c = np.zeros(gates.height, dtype=np.int16)
    t_g = gates["t_call"].dt.epoch("us").to_numpy()
    # placebo window end: the gate call's model latency (its output cannot exist earlier). NOT t_end: for a pause
    # call t_end includes the timer, which would make the window outcome-dependent (bug found 2026-10-04, H72).
    lat = gates["latency_s"].fill_null(gates["dur_api_s"]).fill_null(10.0).to_numpy().astype(float)
    t_e = t_g + (np.clip(lat, 1.0, 60.0) * 1_000_000).astype(np.int64)
    room_g = gates["room"].fill_null(-99).to_numpy()
    ag_g = gates["agent"].to_numpy()
    for (r,), c in ch.group_by(["room"]):
        idx = np.where(room_g == r)[0]
        if len(idx) == 0:
            continue
        tc = c["t"].dt.epoch("us").to_numpy()
        o = np.argsort(tc)
        tc = tc[o]
        ac = c["agent"].fill_null(-1).to_numpy()[o]
        lo = np.searchsorted(tc, t_g[idx], side="right")
        hi = np.searchsorted(tc, t_g[idx] + INFLIGHT_S * 1_000_000, side="right")
        he = np.searchsorted(tc, np.maximum(t_e[idx], t_g[idx]), side="right")
        for j, (a, b, e) in enumerate(zip(lo, hi, he)):
            if b > a:
                res[idx[j]] = int(np.sum(ac[a:b] != ag_g[idx[j]]))
            if e > a:
                res_c[idx[j]] = int(np.sum(ac[a:e] != ag_g[idx[j]]))
    return gates.with_columns(pl.Series("n_inflight60", res), pl.Series("n_inflight_call", res_c))


def build(include_holdout: bool = False, goal_nos=None) -> pl.DataFrame:
    cw = load_calls(include_holdout, goal_nos)
    cw = cw.with_columns((pl.col("kind").cast(pl.Utf8).is_in(IDLE_KINDS) & ~pl.col("talk")).alias("idle"))
    cw = cw.with_columns((~pl.col("idle")).alias("active"))
    ic = item_counts(cw)
    cw = cw.join(ic, on="turn_id", how="left").with_columns(
        [pl.col(c).fill_null(0) for c in ic.columns if c != "turn_id"])
    room = pl.scan_parquet(SH / "context_ledger_turns.parquet").select("turn_id", "room").collect()
    cw = cw.join(room, on="turn_id", how="left")
    cw = cw.join(swarm_activity(cw), on="turn_id", how="left")
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "win_start", "win_end"])
    cw = cw.join(cal, on="pt_date", how="left").sort("agent", "pt_date", "t_call", "turn_id")
    ad = ["agent", "pt_date"]
    # runs of equal state
    cw = cw.with_columns((pl.col("idle") != pl.col("idle").shift(1).over(ad)).fill_null(True).cast(pl.Int32)
                         .cum_sum().over(ad).alias("run"))
    cw = cw.with_columns(pl.len().over(ad + ["run"]).alias("run_len"),
                         (pl.int_range(pl.len()).over(ad + ["run"]) == pl.len().over(ad + ["run"]) - 1).alias("run_last"))
    cw = cw.with_columns(
        (pl.col("active") & pl.col("run_last")).alias("end_any"),
        (pl.col("active") & pl.col("run_last") & (pl.col("run_len") >= SUS_LEN)).alias("end_sus"),
        pl.col("idle").shift(1).over(ad).fill_null(False).alias("gate"),
        pl.col("active").shift(-1).over(ad).alias("act_n1"),
        pl.col("active").shift(-2).over(ad).alias("act_n2"),
        pl.col("pause_s").shift(1).over(ad).alias("prev_pause_s"),
        pl.col("kind").cast(pl.Utf8).shift(1).over(ad).alias("prev_kind"),
        pl.col("t_call").first().over(ad).alias("t_first_call"),
    )
    # last end times before each call (strictly earlier calls)
    cw = cw.with_columns(
        pl.when(pl.col("end_any")).then(pl.col("t_end")).shift(1).forward_fill().over(ad).alias("t_end_any"),
        pl.when(pl.col("end_sus")).then(pl.col("t_end")).shift(1).forward_fill().over(ad).alias("t_end_sus"),
        pl.when(pl.col("end_any")).then(pl.col("run_len")).shift(1).forward_fill().over(ad).alias("last_run_len"),
    )
    # epochs for gate index
    cw = cw.with_columns(
        pl.col("end_any").shift(1).fill_null(False).cast(pl.Int32).cum_sum().over(ad).alias("ep_any"),
        pl.col("end_sus").shift(1).fill_null(False).cast(pl.Int32).cum_sum().over(ad).alias("ep_sus"),
    )
    cw = cw.with_columns(
        pl.col("gate").cast(pl.Int32).cum_sum().over(ad + ["ep_any"]).alias("k_any"),
        pl.col("gate").cast(pl.Int32).cum_sum().over(ad + ["ep_sus"]).alias("k_sus"),
    )
    # starvation clocks: latest earlier call with reads of each variant
    for v, col in (("novel", "n_novel"), ("peer", "n_peer"), ("content", "n_content"), ("dir", "n_dir"),
                   ("nudge", "n_nudge_me")):
        cw = cw.with_columns(
            pl.when(pl.col(col) > 0).then(pl.col("t_call")).shift(1).forward_fill().over(ad).alias(f"t_last_{v}"))
    # outcome: active calls in [t, t+30 min)
    cw = cw.with_columns(pl.col("active").cast(pl.Int32).cum_sum().over(ad).alias("cum_act"),
                         (pl.col("t_call") + pl.duration(seconds=W30)).alias("t_plus30"))
    right = cw.select("agent", "pt_date", pl.col("t_call").alias("t_r"), pl.col("cum_act").alias("cum_r")).sort("t_r")
    g = cw.filter(pl.col("gate")).sort("t_plus30")
    g = g.join_asof(right, left_on="t_plus30", right_on="t_r", by=["agent", "pt_date"], strategy="backward",
                    allow_exact_matches=False)
    g = g.with_columns((pl.col("cum_r") - pl.col("cum_act") + pl.col("active").cast(pl.Int32)).alias("y_calls30"))
    g = g.with_columns(pl.when(pl.col("t_plus30") <= pl.col("win_end")).then(pl.col("y_calls30")).otherwise(None)
                       .cast(pl.Int16).alias("y_calls30"))
    sec = lambda a, b: (pl.col(a) - pl.col(b)).dt.total_microseconds().cast(pl.Float64) / 1e6  # noqa: E731
    y_sus = (pl.when(~pl.col("active")).then(False)
             .when(pl.col("act_n1").is_null()).then(None)
             .when(~pl.col("act_n1")).then(False)
             .when(pl.col("act_n2").is_null()).then(None)
             .otherwise(pl.col("act_n2")))
    g = g.with_columns(
        pl.col("active").alias("y_any"), y_sus.alias("y_sus"),
        sec("t_call", "t_end_any").alias("a_any"), sec("t_call", "t_end_sus").alias("a_sus"),
        ((pl.col("t_call") - pl.col("win_start")).dt.total_seconds() / 3600).cast(pl.Float32).alias("h_day"),
        *[sec("t_call", f"t_last_{v}").alias(f"s_{v}") for v in ("novel", "peer", "content", "dir", "nudge")],
        *[pl.col(f"t_last_{v}").is_null().alias(f"s_{v}_none") for v in ("novel", "peer", "content", "dir", "nudge")],
        sec("t_call", "t_first_call").alias("s_lc"),
    )
    pu = pl.read_parquet(SH / "period_units.parquet", columns=["unit_id", "goal_no", "days"]).explode("days") \
        .rename({"days": "pt_date"})
    g = g.join(pu, on=["goal_no", "pt_date"], how="left")
    g = inflight(g.sort("agent", "pt_date", "t_call"))
    keep = ["turn_id", "agent", "lab", "pt_date", "goal_no", "unit_id", "regime", "kind", "prev_kind", "room", "t_call",
            "y_any", "y_sus", "y_calls30", "a_any", "a_sus", "k_any", "k_sus", "last_run_len",
            "s_novel", "s_peer", "s_content", "s_dir", "s_nudge", "s_novel_none", "s_peer_none", "s_content_none",
            "s_dir_none", "s_nudge_none", "s_lc",
            "n_novel", "n_peer", "n_content", "n_dir", "n_nudge_me", "n_nudge_other", "n_ment_agent", "n_human",
            "n_human_named", "n_bookend", "prev_pause_s", "h_day", "swarm_act10", "n_present", "first_of_day",
            "n_inflight60", "n_inflight_call", "t_end", "latency_s"]
    g = g.select(keep).with_columns(
        pl.col("regime").cast(pl.Utf8), pl.col("k_any").cast(pl.Int16), pl.col("k_sus").cast(pl.Int16),
        pl.col("last_run_len").cast(pl.Int32),
        *[pl.col(c).cast(pl.Float32) for c in ("a_any", "a_sus", "s_novel", "s_peer", "s_content", "s_dir", "s_nudge",
                                                 "s_lc")])
    return g.sort("agent", "pt_date", "t_call")


def verify(g: pl.DataFrame, n: int = 40, seed: int = 0) -> dict:
    """Recount a_any, a_sus, k_any, y_any, y_sus, s_novel for random agent-days with a plain Python loop."""
    cw = load_calls()
    cw = cw.with_columns((pl.col("kind").cast(pl.Utf8).is_in(IDLE_KINDS) & ~pl.col("talk")).alias("idle"))
    ic = item_counts(cw)
    cw = cw.join(ic, on="turn_id", how="left").with_columns(pl.col("n_novel").fill_null(0))
    rng = np.random.default_rng(seed)
    ad = g.select("agent", "pt_date").unique().sort("agent", "pt_date")
    pick = ad[rng.choice(ad.height, size=min(n, ad.height), replace=False)]
    bad = 0
    checked = 0
    for a, d in pick.iter_rows():
        c = cw.filter((pl.col("agent") == a) & (pl.col("pt_date") == d)).sort("t_call", "turn_id")
        rows = c.select("turn_id", "idle", "t_call", "t_end", "n_novel").rows()
        gg = {r[0]: r for r in g.filter((pl.col("agent") == a) & (pl.col("pt_date") == d))
              .select("turn_id", "a_any", "a_sus", "k_any", "y_any", "y_sus", "s_novel").rows()}
        last_end_any = last_end_sus = last_novel = None
        run_len = 0
        k = 0
        for i, (tid, idle, tc, te, nn) in enumerate(rows):
            if i > 0 and rows[i - 1][1]:
                exp_a = None if last_end_any is None else (tc - last_end_any).total_seconds()
                exp_as = None if last_end_sus is None else (tc - last_end_sus).total_seconds()
                k += 1
                y_any = not idle
                if idle:
                    y_sus = False
                elif i + 1 >= len(rows):
                    y_sus = None
                elif rows[i + 1][1]:
                    y_sus = False
                elif i + 2 >= len(rows):
                    y_sus = None
                else:
                    y_sus = not rows[i + 2][1]
                exp_s = None if last_novel is None else (tc - last_novel).total_seconds()
                got = gg.get(tid)
                checked += 1
                ok = got is not None
                if ok:
                    def close(x, y):
                        return (x is None and y is None) or (x is not None and y is not None and abs(x - y) < 1e-2)
                    ok = (close(exp_a, got[1]) and close(exp_as, got[2]) and got[3] == k and got[4] == y_any
                          and got[5] == y_sus and close(exp_s, got[6]))
                bad += not ok
            # update state after call i
            if not idle:
                run_len += 1
                nxt_idle = rows[i + 1][1] if i + 1 < len(rows) else True
                if nxt_idle or i + 1 >= len(rows):
                    last_end_any = te
                    k = 0
                    if run_len >= SUS_LEN:
                        last_end_sus = te
            else:
                run_len = 0
            if nn > 0:
                last_novel = tc
    return {"agent_days": pick.height, "gates_checked": checked, "mismatches": bad}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    if args.verify:
        g = pl.read_parquet(OUT / "idle_gates.parquet")
        r = verify(g)
        print(json.dumps(r))
        (OUT / "verify.json").write_text(json.dumps(r, indent=1))
        return
    g = build()
    OUT.mkdir(parents=True, exist_ok=True)
    g.write_parquet(OUT / "idle_gates.parquet", compression="zstd")
    prov = {"built_by": "infra/shared/idle_gates.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["call_windows", "context_ledger_items", "context_ledger_turns", "chat_core",
                                   "chat_text (nudge leading @, in memory)", "statement_flags",
                                   "embeddings/chat_index", "calendar", "period_units", "roster"]}],
            "params": {"idle_kinds": IDLE_KINDS, "novel_kinds": NOVEL_KINDS, "sustained_len": SUS_LEN,
                       "calls_window_s": W30, "inflight_s": INFLIGHT_S, "holdout": "excluded (common.holdout_mask)"},
            "rows": g.height, "built_at": dt.datetime.now(dt.UTC).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print(g.height, "gates")


if __name__ == "__main__":
    main()
