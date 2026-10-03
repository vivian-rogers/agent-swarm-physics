"""H09 reusable observable tables (round 2). Built for ALL days with a `holdout` flag; exploratory
analyses must filter holdout == False (confirmation work uses the flagged rows later).

Outputs (data/processed/H09-swarm-thermodynamics/):
  idle_runs.parquet            one row per idle spell (maximal run of one agent's WAIT/PAUSE events)
  consolidation_inflow.parquet one row per memory snapshot (memory_stats) with inflow since the previous one
Schema notes are in the H09 card (Results, "Observable tables").

Definitions
  idle spell: consecutive idle events (WAIT/PAUSE) of one agent with no non-idle row in between.
    Non-idle row = any other events_core agent event, or any `actions` turn except the `pause` tool call
    (it mirrors the PAUSE event ~0.1 s earlier). Ties at the same timestamp: non-idle first (a regime-I
    turn logs AGENT_TALK and WAIT with one timestamp; the wait starts after the talk).
    Ends at the next non-idle row on the same PT day, else right-censored at the day's window end.
  kicks: chat messages by others in the agent's room (`exposure`); typed agent / human / automated
    (nudger) and @-mention of the agent.
  escape_cause (proximate label, NOT causal; see base rates in explore_e6_idle_traps.json):
    censored > timer (PAUSE spell ending >= last declared expiry - 30 s) > mention > nudge > human >
    room_msg (any kick in the 60 s before escape) > none.
  inflow per snapshot (t_prev, t]: exposed messages; uncached input tokens summed over the agent's turns.
    Token accounting differs by provider: 'exclusive' (Anthropic; tok_in excludes cache reads):
    uncached = tok_in + tok_cache_write, context = tok_in + tok_cache_read + tok_cache_write;
    'inclusive' (Gemini; tok_in includes cache reads): uncached = tok_in - tok_cache_read, context = tok_in.
    Other providers report no tokens (null).

Usage: uv run python hypotheses/H09-swarm-thermodynamics/analysis/build_observables.py
"""
from __future__ import annotations

import datetime as dt
import json
import subprocess
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
SH = ROOT / "data/processed/shared"
OUTD = ROOT / "data/processed/H09-swarm-thermodynamics"
OUTD.mkdir(parents=True, exist_ok=True)
US = 1_000_000

cal = pl.read_parquet(SH / "calendar.parquet").select("pt_date", pl.col("regime").cast(pl.Utf8).alias("regime"), "goal_no",
                                                       "holdout", "win_start", "win_end")
roster = pl.read_parquet(SH / "roster.parquet")


def to_us(s: pl.Series) -> np.ndarray:
    return s.dt.epoch("us").to_numpy()


# ------------------------------------------------------------------ kicks per agent (all days)
chat = pl.read_parquet(SH / "chat_core.parquet", columns=["t", "speaker_kind", "mentions"]).with_row_index("msg")
kk = (pl.read_parquet(SH / "exposure.parquet", columns=["msg", "agent"]).join(chat, on="msg")
      .with_columns(pl.col("mentions").list.contains(pl.col("agent")).fill_null(False).alias("mention"),
                    pl.col("speaker_kind").cast(pl.Utf8).alias("sk"))
      .select("agent", "t", "sk", "mention").sort("agent", "t"))
KT = {"msgs": pl.lit(True), "agent_msgs": pl.col("sk") == "agent", "human_msgs": pl.col("sk") == "human",
      "nudges": pl.col("sk") == "automated", "mentions": pl.col("mention")}
KICKS = {}
for (a,), g in kk.group_by("agent"):
    KICKS[a] = {n: np.sort(to_us(g.filter(c)["t"])) for n, c in KT.items()}


def count_in(a, name, lo, hi, left_closed=True):
    """Number of kicks of type `name` for agent a in [lo, hi) (or (lo, hi] if left_closed=False)."""
    arr = KICKS.get(a, {}).get(name)
    if arr is None or len(arr) == 0:
        return np.zeros(len(lo), np.int32)
    side = "left" if left_closed else "right"
    return (np.searchsorted(arr, hi, side=side) - np.searchsorted(arr, lo, side=side)).astype(np.int32)


# ------------------------------------------------------------------ idle runs
ev = (pl.read_parquet(SH / "events_core.parquet", columns=["t", "pt_date", "actor_kind", "agent", "action_type", "pause_s"])
      .filter((pl.col("actor_kind") == "agent") & pl.col("agent").is_not_null())
      .select("agent", "t", "pt_date", pl.col("action_type").cast(pl.Utf8).alias("kind"), "pause_s"))
acts = (pl.read_parquet(SH / "actions.parquet", columns=["t", "agent", "action"])
        .filter(pl.col("agent").is_not_null() & (pl.col("action") != "pause"))
        .with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.Utf8).alias("pt_date"))
        .select("agent", "t", "pt_date", (pl.lit("turn:") + pl.col("action").cast(pl.Utf8)).alias("kind"),
                pl.lit(None, dtype=pl.Float32).alias("pause_s")))
tl = (pl.concat([ev, acts]).with_columns(pl.col("kind").is_in(["WAIT", "PAUSE"]).alias("idle"))
      .join(cal, on="pt_date").sort("agent", "t", "idle"))
tl = tl.with_columns((pl.col("idle") != pl.col("idle").shift(1).over("agent", "pt_date")).fill_null(True)
                     .cum_sum().over("agent", "pt_date").alias("run"))
runs = (tl.group_by("agent", "pt_date", "run")
        .agg(pl.col("idle").first(), pl.col("t").first().alias("t_start"), pl.col("t").last().alias("t_last_idle"),
             pl.len().alias("n_idle_events"), pl.col("kind").first().alias("kind_first"),
             pl.col("pause_s").first().alias("declared_first_s"), pl.col("pause_s").last().alias("declared_last_s"),
             pl.col("regime").first(), pl.col("goal_no").first(), pl.col("holdout").first(), pl.col("win_end").first())
        .sort("agent", "pt_date", "run")
        .with_columns(pl.col("t_start").shift(-1).over("agent", "pt_date").alias("t_esc"),
                      pl.col("kind_first").shift(-1).over("agent", "pt_date").alias("escape_kind"),
                      pl.col("t_last_idle").shift(1).over("agent", "pt_date").alias("t_prev_action")))
idle = (runs.filter(pl.col("idle"))
        .with_columns(pl.col("t_esc").is_null().alias("censored"), pl.coalesce("t_esc", "win_end").alias("t_end"))
        .with_columns(((pl.col("t_end") - pl.col("t_start")).dt.total_milliseconds() / 1000).cast(pl.Float32).alias("dwell_s"),
                      ((pl.col("t_end") - pl.col("t_prev_action")).dt.total_milliseconds() / 1000).cast(pl.Float32).alias("gap_dwell_s"),
                      pl.when(pl.col("kind_first") == "PAUSE").then(pl.lit("PAUSE")).otherwise(pl.lit("WAIT")).alias("idle_kind"))
        .filter(pl.col("dwell_s") >= 0)
        .sort("agent", "t_start"))
parts = []
for (a,), g in idle.group_by("agent"):
    t0, t1 = to_us(g["t_start"]), to_us(g["t_end"])
    cols = {f"n_{n}_during": count_in(a, n, t0, t1) for n in KT}
    for n in ("msgs", "mentions", "nudges", "human_msgs"):
        cols[f"kick_{n}_60s"] = count_in(a, n, t1 - 60 * US, t1, left_closed=False) > 0
    parts.append(g.with_columns(**{k: pl.Series(v) for k, v in cols.items()}))
idle = pl.concat(parts)
cens = pl.col("censored")
idle = idle.with_columns(
    (pl.col("idle_kind") == "PAUSE")
    .and_(pl.col("t_end") >= pl.col("t_last_idle") + pl.duration(milliseconds=(pl.col("declared_last_s").fill_null(1e9) * 1000 - 30_000).cast(pl.Int64)))
    .alias("timer_expired"))
idle = idle.with_columns(
    pl.when(cens).then(pl.lit("censored"))
    .when(pl.col("timer_expired")).then(pl.lit("timer"))
    .when(pl.col("kick_mentions_60s")).then(pl.lit("mention"))
    .when(pl.col("kick_nudges_60s")).then(pl.lit("nudge"))
    .when(pl.col("kick_human_msgs_60s")).then(pl.lit("human"))
    .when(pl.col("kick_msgs_60s")).then(pl.lit("room_msg"))
    .otherwise(pl.lit("none")).alias("escape_cause"))
for c in ("kick_msgs_60s", "kick_mentions_60s", "kick_nudges_60s", "kick_human_msgs_60s"):
    idle = idle.with_columns(pl.when(cens).then(None).otherwise(pl.col(c)).alias(c))
idle = (idle.select("agent", "pt_date", "regime", "goal_no", "holdout", "idle_kind", "t_prev_action", "t_start", "t_last_idle", "t_end",
                    "censored", "dwell_s", "gap_dwell_s", "n_idle_events", "declared_first_s", "declared_last_s", "timer_expired",
                    "escape_kind", "escape_cause", "n_msgs_during", "n_agent_msgs_during", "n_human_msgs_during",
                    "n_nudges_during", "n_mentions_during", "kick_msgs_60s", "kick_mentions_60s", "kick_nudges_60s",
                    "kick_human_msgs_60s")
        .with_columns(pl.col("goal_no").cast(pl.Int8), pl.col("n_idle_events").cast(pl.Int32))
        .sort("t_start", "agent"))
idle.write_parquet(OUTD / "idle_runs.parquet", compression="zstd")
print("idle_runs", idle.height, flush=True)

# ------------------------------------------------------------------ consolidation inflow
ms = (pl.read_parquet(SH / "memory_stats.parquet")
      .with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.Utf8).alias("pt_date"))
      .join(cal.select("pt_date", "regime", "goal_no", "holdout"), on="pt_date", how="left")
      .sort("agent", "t")
      .with_columns(pl.col("t").shift(1).over("agent").alias("t_prev"),
                    pl.col("pt_date").shift(1).over("agent").alias("pt_prev"),
                    pl.col("n_chars").shift(1).over("agent").alias("n_chars_prev"),
                    pl.col("n_lines").shift(1).over("agent").alias("n_lines_prev"))
      .with_columns(((pl.col("t") - pl.col("t_prev")).dt.total_milliseconds() / 1000).cast(pl.Float32).alias("dt_s"),
                    (pl.col("pt_prev") == pl.col("pt_date")).fill_null(False).alias("same_day_prev"),
                    (pl.col("n_chars") - pl.col("n_chars_prev")).alias("d_chars"),
                    (pl.col("n_lines") - pl.col("n_lines_prev")).alias("d_lines")))
# token accounting per agent
tok = pl.read_parquet(SH / "actions.parquet", columns=["t", "agent", "tok_in", "tok_cache_read", "tok_cache_write", "tok_out"])
acct = (tok.drop_nulls("tok_in").group_by("agent")
        .agg((pl.col("tok_in") >= pl.col("tok_cache_read").fill_null(0)).mean().alias("ge"))
        .with_columns(pl.when(pl.col("ge") > 0.99).then(pl.lit("inclusive")).otherwise(pl.lit("exclusive")).alias("tok_acct")))
ACCT = dict(zip(acct["agent"].to_list(), acct["tok_acct"].to_list()))
tok = (tok.with_columns(pl.col("agent").replace_strict(ACCT, default=None).alias("acct"))
       .with_columns(
           pl.when(pl.col("acct") == "exclusive").then(pl.col("tok_in") + pl.col("tok_cache_write").fill_null(0))
           .when(pl.col("acct") == "inclusive").then(pl.col("tok_in") - pl.col("tok_cache_read").fill_null(0))
           .otherwise(None).cast(pl.Float64).alias("unc"),
           pl.when(pl.col("acct") == "exclusive").then(pl.col("tok_in") + pl.col("tok_cache_read").fill_null(0) + pl.col("tok_cache_write").fill_null(0))
           .when(pl.col("acct") == "inclusive").then(pl.col("tok_in"))
           .otherwise(None).cast(pl.Float64).alias("ctx"))
       .sort("agent", "t"))
cons_ev = (pl.read_parquet(SH / "events_core.parquet", columns=["t", "agent", "action_type"])
           .filter(pl.col("action_type") == "CONSOLIDATE").sort("agent", "t"))
parts = []
for (a,), g in ms.group_by("agent"):
    g = g.sort("t")
    t1 = to_us(g["t"]); tp = g["t_prev"].dt.epoch("us").fill_null(0).to_numpy()
    cols = {f"n_{n}": count_in(a, n, tp, t1, left_closed=False) for n in KT}
    ta = tok.filter(pl.col("agent") == a)
    tt = to_us(ta["t"])
    i0, i1 = np.searchsorted(tt, tp, side="right"), np.searchsorted(tt, t1, side="right")
    cols["n_turns"] = (i1 - i0).astype(np.int32)
    has = ta["unc"].is_not_null().to_numpy()
    cum_has = np.r_[0, np.cumsum(has)]
    unc = np.r_[0, np.cumsum(np.nan_to_num(ta["unc"].to_numpy().astype(float)))]
    out_ = np.r_[0, np.cumsum(np.nan_to_num(ta["tok_out"].to_numpy().astype(float)))]
    ntok = cum_has[i1] - cum_has[i0]
    cols["n_turns_tok"] = ntok.astype(np.int32)
    cols["tok_uncached"] = np.where(ntok > 0, unc[i1] - unc[i0], np.nan)
    cols["tok_out"] = np.where(ntok > 0, out_[i1] - out_[i0], np.nan)
    ctx = ta["ctx"].to_numpy().astype(float)
    last = i1 - 1
    cols["tok_context_last"] = np.where((i1 > i0) & (last >= 0), ctx[np.clip(last, 0, max(len(ctx) - 1, 0))] if len(ctx) else np.nan, np.nan)
    ce = to_us(cons_ev.filter(pl.col("agent") == a)["t"])
    j = np.searchsorted(ce, t1)
    near = np.full(len(t1), np.inf)
    if len(ce):
        near = np.minimum(np.abs(ce[np.clip(j, 0, len(ce) - 1)] - t1), np.abs(ce[np.clip(j - 1, 0, len(ce) - 1)] - t1))
    cols["consolidate_event_120s"] = near <= 120 * US
    parts.append(g.with_columns(**{k: (pl.Series(k, v).fill_nan(None) if np.asarray(v).dtype.kind == "f" else pl.Series(k, v)) for k, v in cols.items()}))
ci = (pl.concat(parts)
      .with_columns(pl.col("agent").replace_strict(ACCT, default=None).alias("tok_acct"),
                    pl.when(pl.col("t_prev").is_null()).then(None).otherwise(pl.col("tok_uncached")).alias("tok_uncached"))
      .select("agent", "t", "pt_date", "regime", "goal_no", "holdout", "t_prev", "dt_s", "same_day_prev",
              "n_chars", "n_lines", "n_headers", "lines_kept", "lines_added", "lines_removed", "jaccard_prev",
              "d_chars", "d_lines", pl.col("n_msgs").alias("n_exposed"), pl.col("n_agent_msgs").alias("n_exposed_agent"),
              pl.col("n_human_msgs").alias("n_exposed_human"), pl.col("n_nudges").alias("n_exposed_nudge"),
              pl.col("n_mentions").alias("n_exposed_mention"), "n_turns", "n_turns_tok", "tok_acct",
              pl.col("tok_uncached").cast(pl.Float32), pl.col("tok_out").cast(pl.Float32),
              pl.col("tok_context_last").cast(pl.Float32), "consolidate_event_120s")
      .with_columns(pl.col("goal_no").cast(pl.Int8))
      .sort("t", "agent"))
ci.write_parquet(OUTD / "consolidation_inflow.parquet", compression="zstd")
print("consolidation_inflow", ci.height, flush=True)

# ------------------------------------------------------------------ provenance
try:
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip() or None
except Exception:
    commit = None
shared_prov = json.loads((SH / "_provenance.json").read_text())
prov = {
    "built_by": ["hypotheses/H09-swarm-thermodynamics/analysis/build_observables.py",
                 "hypotheses/H09-swarm-thermodynamics/analysis/explore_e1_e5.py",
                 "hypotheses/H09-swarm-thermodynamics/analysis/explore_e6_idle_traps.py",
                 "hypotheses/H09-swarm-thermodynamics/analysis/explore_e7_e8.py"],
    "git_commit": commit,
    "inputs": [{"source": "data/processed/shared", "revision": shared_prov.get("inputs", [{}])[0].get("revision") if isinstance(shared_prov.get("inputs"), list) else None,
                "tables": ["events_core", "actions", "exposure", "chat_core", "memory_stats", "calendar", "roster", "activity_bins", "kicks"]}],
    "outputs": {"idle_runs.parquet": "per idle spell; all days, holdout flag",
                "consolidation_inflow.parquet": "per memory snapshot with inflow since previous; all days, holdout flag",
                "explore_*.json": "exploratory numbers, non-holdout days only"},
    "params": {"pause_action_mirror_dropped": True, "tie_order": "non-idle before idle at equal t", "kick_lookback_s": 60,
               "timer_tolerance_s": 30, "token_accounting": {str(k): v for k, v in ACCT.items()}},
    "built_at": dt.datetime.now(dt.timezone.utc).isoformat(),
}
(OUTD / "_provenance.json").write_text(json.dumps(prov, indent=1))
