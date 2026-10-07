"""H133 scheme: per-call risk sets, reads about projects, in-flight placebo counts and project activity, per period unit.

Inputs (shared, read-only): project_calls / project_call_touches (infra/shared/project_calls.py; E = 100 carry, hops),
call_windows (gap_kind, wake_early, kind), context_ledger_turns (room), context_ledger_items (turn_id, message_id,
sender, kind, ment, omitted), project_mentions_chat (agent chat x strictly linked project), chat_mentions_clean
(mentions_roster), calendar (active windows), period_units, roster (lab). No message text.

Per unit (non-reserved units only; reserved rows are dropped with common.holdout_mask and the ledger flag is asserted):
  calls.parquet    risk-set calls: a present agent's call whose carried label at the previous call is known (prev_label).
                   unit, turn_id, agent, t_call, a (active seconds since the unit start), h (active hour index), span_s,
                   hod (UTC hour), prev_kind, timer_wake, cur (current project hash), hop, dst (hash or null), d (own-call
                   dwell on cur), first4h (in the first 4 active hours of the goal period), any_read_other (any read at c
                   about a project other than cur)
  reads.parquet    (turn_id, p) with n_nam, n_un (reads at c: agent senders, not omitted, sender != reader, message links
                   p), n_if (named in-flight placebo: messages naming the reader that link p, posted in the reader's room
                   in (t_call, t_call + d_c], d_c = t_first - t_call clipped to [1, 120] s), n_nam_l1, n_un_l1 (reads at the
                   agent's previous call), n_nam_same, n_nam_cross (named reads by same-lab / other-lab senders)
  touches.parquet  (unit, p, a, agent): every strict project touch in the unit (call t_first on the active clock), for the
                   option sets (projects touched by anyone in the last 4 active hours)
  held.parquet     (turn_id, p): projects the agent had as its label earlier in the unit (rho term), and the share
                   s_b(c) is computed in analysis from `labels.parquet` (agent, t_call, label hash) of all unit calls.
Project names are hashed (sha1, 10 hex). Writes data/processed/H133-readout-glauber-potts/<unit>/ and _provenance.json.

Usage: uv run python hypotheses/H133-readout-glauber-potts/scheme/build.py [--units 38a,51c] [--counts]
       --counts prints the structural precondition counts only (hops; named reads about a non-current project).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import datetime as dt  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit, holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H133-readout-glauber-potts"
D_LO, D_HI = 1.0, 120.0
KICK_H = 4 * 3600


def hsh(s: str) -> str:
    return hashlib.sha1(s.encode()).hexdigest()[:10]


def units() -> pl.DataFrame:
    pu = pl.read_parquet(SH / "period_units.parquet").filter(~pl.col("holdout"))
    return pu.select("unit_id", "goal_no", "start", "end", "days", "regime", "n_agents").sort("start")


def active_clock(days: list[str], goal_days: list[str]) -> pl.DataFrame:
    """pt_date -> win_start, offset (active seconds before this day in the unit), goff (same within the goal period)."""
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "win_start", "win_end", "window_s", "goal_no"])
    c = cal.filter(pl.col("pt_date").is_in(goal_days)).sort("pt_date").with_columns(
        pl.col("window_s").fill_null(0).cum_sum().shift(1).fill_null(0).alias("goff"))
    cu = c.filter(pl.col("pt_date").is_in(days)).with_columns(
        pl.col("window_s").fill_null(0).cum_sum().shift(1).fill_null(0).alias("offset"))
    return cu.select("pt_date", "win_start", "window_s", "offset", "goff")


def to_active(df: pl.DataFrame, tcol: str, clock: pl.DataFrame, name: str = "a") -> pl.DataFrame:
    df = df.with_columns(pl.col(tcol).dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).alias("_d"))
    df = df.join(clock.rename({"pt_date": "_d"}), on="_d", how="left")
    within = ((pl.col(tcol) - pl.col("win_start")).dt.total_milliseconds() / 1000).clip(0, pl.col("window_s"))
    return df.with_columns((pl.col("offset") + within).alias(name), (pl.col("goff") + within).alias(f"g{name}")).drop(
        "_d", "win_start", "window_s", "offset", "goff")


def build_unit(u: dict, counts_only: bool = False, allow_reserved: bool = False, out_root: Path = OUT) -> dict:
    """allow_reserved is used only by analysis/confirm.py (guarded); exploration never sets it."""
    uid, g = u["unit_id"], u["goal_no"]
    days = list(u["days"])
    if not allow_reserved:
        assert not any(holdout_mask(days, [g] * len(days))), f"reserved day in unit {uid}"
    pc = pl.read_parquet(SH / "project_calls.parquet").filter(pl.col("unit_id") == uid)
    if not allow_reserved:
        pc = pc.filter(~pl.col("holdout"))
    pc = pc.filter(pl.col("pt_date").is_in(days))
    if not allow_reserved:
        assert not pc["holdout"].any()
    cw = pl.read_parquet(SH / "call_windows.parquet", columns=["turn_id", "gap_kind", "wake_early", "holdout"]).filter(
        pl.col("turn_id").is_in(pc["turn_id"].implode()))
    if not allow_reserved:
        assert not cw["holdout"].any()
    tr = pl.read_parquet(SH / "context_ledger_turns.parquet", columns=["turn_id", "room"]).filter(
        pl.col("turn_id").is_in(pc["turn_id"].implode()))
    pc = pc.join(cw.drop("holdout"), on="turn_id", how="left").join(tr, on="turn_id", how="left")
    goal_days = pl.read_parquet(SH / "calendar.parquet").filter(pl.col("goal_no") == g)["pt_date"].to_list()
    clock = active_clock(days, goal_days)
    pc = to_active(pc.sort("agent", "t_first", "turn_id"), "t_call", clock)
    blk = ["agent", "goal_no", "holdout"]
    pc = pc.with_columns(
        pl.col("kind").shift(1).over(blk).cast(pl.String).alias("prev_kind"),
        pl.when(pl.col("hop") | pl.col("arrive")).then(pl.col("idx")).forward_fill().shift(1).over(blk).alias("_arr"))
    pc = pc.with_columns((pl.col("idx") - pl.col("_arr")).alias("d")).drop("_arr")
    # reads at c (ledger), linked to projects
    pm = pl.read_parquet(SH / "project_mentions_chat.parquet", columns=["message_id", "project", "t", "room", "agent"])
    it = (pl.scan_parquet(SH / "context_ledger_items.parquet")
          .filter(pl.col("turn_id").is_in(pc["turn_id"].implode()) & (pl.col("kind").cast(pl.String) == "agent")
                  & ~pl.col("omitted"))
          .select("turn_id", "message_id", "sender", "ment").collect())
    it = it.join(pc.select("turn_id", "agent"), on="turn_id").filter(pl.col("sender") != pl.col("agent"))
    lab = dict(pl.read_parquet(SH / "roster.parquet").select("agent", "lab").iter_rows())
    it = it.join(pm.select("message_id", "project").unique(), on="message_id", how="inner").with_columns(
        (pl.col("sender").replace_strict(lab, default=None) == pl.col("agent").replace_strict(lab, default=None)).alias("same"))
    rd = it.group_by("turn_id", "project").agg(
        pl.col("ment").sum().cast(pl.Int16).alias("n_nam"), (~pl.col("ment")).sum().cast(pl.Int16).alias("n_un"),
        (pl.col("ment") & pl.col("same")).sum().cast(pl.Int16).alias("n_nam_same"),
        (pl.col("ment") & ~pl.col("same").fill_null(False)).sum().cast(pl.Int16).alias("n_nam_cross"))
    # named in-flight placebo
    men = pl.read_parquet(SH / "chat_mentions_clean.parquet", columns=["message_id", "mentions_roster"])
    fl = (pm.join(men, on="message_id", how="inner").explode("mentions_roster")
          .rename({"mentions_roster": "reader", "agent": "sender", "room": "mroom"})
          .filter(pl.col("reader").is_not_null() & (pl.col("reader") != pl.col("sender"))))
    keys = pc.select("turn_id", pl.col("agent").alias("reader"), "t_call", "t_first", "room").sort("t_call")
    fl = fl.filter(pl.col("reader").is_in(pc["agent"].unique().implode())).sort("t")
    fl = fl.join_asof(keys, left_on="t", right_on="t_call", by="reader", strategy="backward", allow_exact_matches=False)
    dc = ((pl.col("t_first") - pl.col("t_call")).dt.total_milliseconds() / 1000).clip(D_LO, D_HI)
    fl = fl.filter(pl.col("turn_id").is_not_null() & (pl.col("mroom") == pl.col("room"))
                   & (((pl.col("t") - pl.col("t_call")).dt.total_milliseconds() / 1000) <= dc))
    nif = fl.group_by("turn_id", "project").agg(pl.len().cast(pl.Int16).alias("n_if"))
    rd = rd.join(nif, on=["turn_id", "project"], how="full", coalesce=True)
    # lag-1 reads (the agent's previous call in its block)
    prev = pc.select("turn_id", pl.col("turn_id").shift(1).over(blk).alias("prev_turn"))
    l1 = (it.group_by("turn_id", "project").agg(pl.col("ment").sum().cast(pl.Int16).alias("n_nam_l1"),
                                               (~pl.col("ment")).sum().cast(pl.Int16).alias("n_un_l1"))
          .rename({"turn_id": "prev_turn"}).join(prev, on="prev_turn").drop("prev_turn"))
    rd = rd.join(l1, on=["turn_id", "project"], how="full", coalesce=True)
    rd = rd.with_columns([pl.col(c).fill_null(0) for c in ("n_nam", "n_un", "n_if", "n_nam_l1", "n_un_l1", "n_nam_same",
                                                           "n_nam_cross")])
    # risk set
    risk = pc.filter(pl.col("prev_label").is_not_null())
    other = (rd.join(risk.select("turn_id", "prev_label"), on="turn_id")
             .filter((pl.col("project") != pl.col("prev_label")) & ((pl.col("n_nam") + pl.col("n_un")) > 0))
             .group_by("turn_id").agg(pl.col("n_nam").sum().alias("nam_other"), pl.col("n_un").sum().alias("un_other")))
    risk = risk.join(other, on="turn_id", how="left").with_columns(pl.col("nam_other").fill_null(0), pl.col("un_other").fill_null(0))
    n_hops = int(risk["hop"].sum())
    n_named_other = int(risk["nam_other"].sum())
    res = {"unit": uid, "goal_no": g, "regime": u["regime"], "risk_calls": risk.height, "hops": n_hops,
           "named_reads_other": n_named_other, "testable": bool(n_hops >= 30 and n_named_other >= 20)}
    if counts_only:
        return res
    o = out_root / uid
    o.mkdir(parents=True, exist_ok=True)
    rc = risk.select(
        pl.lit(uid).alias("unit"), "turn_id", "agent", "pt_date", "t_call", "a", "ga", (pl.col("a") // 3600).cast(pl.Int32).alias("h"),
        "span_s", pl.col("t_call").dt.hour().cast(pl.Int8).alias("hod"), "prev_kind",
        ((pl.col("gap_kind").cast(pl.String) == "pause") & ~pl.col("wake_early").fill_null(False)).alias("timer_wake"),
        pl.col("prev_label").map_elements(hsh, return_dtype=pl.String).alias("cur"), "hop",
        pl.when(pl.col("hop")).then(pl.col("proj")).map_elements(hsh, return_dtype=pl.String).alias("dst"),
        pl.col("d").cast(pl.Int32), (pl.col("ga") < KICK_H).alias("first4h"),
        ((pl.col("nam_other") + pl.col("un_other")) > 0).alias("any_read_other"), "ctx_mode", "kind")
    rc.write_parquet(o / "calls.parquet", compression="zstd")
    rd.filter(pl.col("turn_id").is_in(risk["turn_id"].implode())).with_columns(
        pl.col("project").map_elements(hsh, return_dtype=pl.String).alias("p")).drop("project").write_parquet(
        o / "reads.parquet", compression="zstd")
    tc = pl.read_parquet(SH / "project_call_touches.parquet").filter(pl.col("turn_id").is_in(pc["turn_id"].implode()))
    tc = tc.join(pc.select("turn_id", "t_first"), on="turn_id")
    tc = to_active(tc, "t_first", clock)
    tc.select(pl.lit(uid).alias("unit"), pl.col("project").map_elements(hsh, return_dtype=pl.String).alias("p"), "a", "agent").write_parquet(
        o / "touches.parquet", compression="zstd")
    pc.select("agent", "turn_id", "t_call", "a", pl.col("label").map_elements(hsh, return_dtype=pl.String).alias("label"),
              "pt_date").write_parquet(o / "labels.parquet", compression="zstd")
    # kickoff-named projects (H54 rule) of the goal period, hashed
    try:
        import replicator_hosts as RH
        projs = sorted(set(pc["proj"].drop_nulls().to_list()))
        kn = RH.kickoff_named(g, projs)
        res["kickoff_named"] = sorted(hsh(p) for p, v in kn.items() if v)
    except Exception as e:  # noqa: BLE001
        res["kickoff_named_error"] = repr(e)[:200]
    (o / "meta.json").write_text(json.dumps(res, indent=1))
    return res


def main():
    t0 = time.time()
    counts_only = "--counts" in sys.argv
    sel = None
    if "--units" in sys.argv:
        sel = sys.argv[sys.argv.index("--units") + 1].split(",")
    us = units()
    if sel:
        us = us.filter(pl.col("unit_id").is_in(sel))
    rows = []
    for u in us.iter_rows(named=True):
        r = build_unit(u, counts_only=counts_only)
        rows.append(r)
        print(json.dumps({k: r[k] for k in ("unit", "regime", "risk_calls", "hops", "named_reads_other", "testable")}),
              f"{time.time() - t0:.0f}s", flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    tag = "counts" if counts_only else "build"
    old = {}
    p = OUT / f"structural_{tag}.json"
    if p.exists():
        old = {r["unit"]: r for r in json.loads(p.read_text())}
    for r in rows:
        old[r["unit"]] = r
    p.write_text(json.dumps(sorted(old.values(), key=lambda r: r["unit"]), indent=1, default=str))
    if not counts_only:
        prov = {"built_by": "hypotheses/H133-readout-glauber-potts/scheme/build.py", "git_commit": git_commit(),
                "inputs": [{"source": "ai-village", "revision": REVISION,
                            "tables": ["project_calls", "project_call_touches", "call_windows", "context_ledger_turns",
                                       "context_ledger_items", "project_mentions_chat", "chat_mentions_clean", "calendar",
                                       "period_units", "roster"]}],
                "params": {"expiry_E": 100, "inflight_d_clip_s": [D_LO, D_HI], "kickoff_variant_active_s": KICK_H,
                           "reads": "ledger items, agent senders != reader, not omitted", "hash": "sha1[:10]",
                           "reserved": "non-reserved units only; ledger holdout flag asserted false"},
                "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
        (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print(f"done {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
