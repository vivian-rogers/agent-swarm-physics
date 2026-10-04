"""Shared outages: joint silences (JS), village-off gaps and their causes, per minute and per run. Moved here from H38
(hypotheses/H38-platform-stalls/scheme/build_outages.py; consumed by H25, H26, H36). The rule is unchanged; the only
change is that H09's idle spells (data/processed/H09-swarm-thermodynamics/idle_runs.parquet: agent, regime,
t_prev_action, t_start, t_end) are recomputed here with H09's spell rule (`idle_spells`), so the shared pipeline does not
depend on a hypothesis folder. All days; holdout days are flagged, never dropped (measurements: exploratory users must
filter holdout == False).

Definitions (H38 card, "Data scheme"):
  day-present agents: roster agents (Claude Code excluded) with >= 1 active minute (activity_bins.state >= 3) that PT day
  K_t: day-present agents active in minute t; joint silence (JS): K_t <= 1 on a day with n_present >= 3
  village-off gap: >= 10 consecutive minutes with K_t = 0
  silence reason of a silent present agent-minute (first match): pre/post (before first / after last active minute
    of the day) > infra_err (gap adjacent to an infrastructure-error turn, cap 15 min) > consol (last turn ->
    CONSOLIDATE, cap 15 min) > pause (idle spell; regime I/II from the action before the WAIT, regime III from
    the PAUSE call) > none
  scheduled: minute outside the operator's resume -> pause messages of that day (or the period's median schedule
    +-5 min on days without both messages)
  explained JS ("stall"): scheduled, or >= half of the silent present agents have a reason
  primary cause: scheduled > argmax(edge, infra_error, pause, consolidation) [ties in that order] > unexplained
  idle spell (H09): consecutive WAIT/PAUSE events of one agent with no non-idle row in between (non-idle = any other
    agent event or any computer-use turn except the `pause` tool call; same-timestamp ties: non-idle first); ends at
    the next non-idle row the same PT day, else at the day's window end.

Outputs (data/processed/shared/):
  outages.parquet         one row per JS run: outage_id, pt_date, goal_no, regime, holdout, t_start, t_end, m_start,
                          m_end, dur_min, n_present, k_max, k0_min, village_off, k0_longest, at_day_edge, cause,
                          frac_<cause>, explained, frac_explained, infra_burst, n_infra_err_agents
  stall_minutes.parquet   one row per (day, window minute): K, js, scheduled, n_<reason>, explained, cause, outage_id, ...
  reasons.parquet         silent present agent-minutes with a reason: pt_date, minute, agent, reason (int8, REASONS)
Inputs: shared activity_bins, calendar, events_core, actions, chat_core, chat_text (automated rows only, regex, no
text kept), turn_errors (infra/shared/turn_errors.py).

Usage: uv run python infra/shared/outages.py            (build)
       uv run python infra/shared/outages.py --verify   (compare with H38's tables and H09's idle spells; read-only)
Library: main(out_dir) writes the three tables to another folder (for a shim in H38's scheme folder).
"""
from __future__ import annotations

import os

for _v, _n in (("POLARS_MAX_THREADS", "2"), ("OMP_NUM_THREADS", "2"), ("OPENBLAS_NUM_THREADS", "2"),
               ("MKL_NUM_THREADS", "2"), ("VECLIB_MAXIMUM_THREADS", "2")):
    os.environ.setdefault(_v, _n)

import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUT as SH, ROOT, holdout_mask, write_provenance  # noqa: E402

OUT = SH
TURN_ERRORS = SH / "turn_errors.parquet"

GAP_CAP_S = 15 * 60
OFF_MIN = 10
SCHED_TOL_MIN = 5
MIN_PRESENT = 3
INFRA = ["timeout", "vm", "resource", "network"]
REASONS = {"none": 0, "pre": 1, "post": 2, "infra_err": 3, "consol": 4, "pause": 5}
CAUSES = ["scheduled", "edge", "infra_error", "pause", "consolidation", "unexplained"]
PAUSE_RX = r"(?i)paus\w* the village"
RESUME_RX = r"(?i)resum\w* the village"


def idle_spells() -> pl.DataFrame:
    """H09's idle spells (hypotheses/H09-swarm-thermodynamics/analysis/build_observables.py, spell part only):
    agent, pt_date, regime, holdout, t_prev_action, t_start, t_last_idle, t_end, censored, idle_kind."""
    cal = pl.read_parquet(SH / "calendar.parquet").select("pt_date", pl.col("regime").cast(pl.Utf8).alias("regime"), "goal_no",
                                                           "holdout", "win_start", "win_end")
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
                 pl.col("kind").first().alias("kind_first"), pl.col("regime").first(), pl.col("holdout").first(),
                 pl.col("win_end").first())
            .sort("agent", "pt_date", "run")
            .with_columns(pl.col("t_start").shift(-1).over("agent", "pt_date").alias("t_esc"),
                          pl.col("t_last_idle").shift(1).over("agent", "pt_date").alias("t_prev_action")))
    idle = (runs.filter(pl.col("idle"))
            .with_columns(pl.col("t_esc").is_null().alias("censored"), pl.coalesce("t_esc", "win_end").alias("t_end"))
            .filter((pl.col("t_end") - pl.col("t_start")).dt.total_milliseconds() >= 0)
            .with_columns(pl.when(pl.col("kind_first") == "PAUSE").then(pl.lit("PAUSE")).otherwise(pl.lit("WAIT")).alias("idle_kind")))
    return idle.select("agent", "pt_date", "regime", "holdout", "t_prev_action", "t_start", "t_last_idle", "t_end", "censored",
                       "idle_kind").sort("t_start", "agent")


def calendar() -> pl.DataFrame:
    cal = pl.read_parquet(SH / "calendar.parquet").with_columns(pl.col("regime").cast(pl.String))
    assert cal["holdout"].to_list() == holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    return cal.with_columns((pl.col("window_s") // 60 + 1).cast(pl.Int32).alias("n_min"))


def to_minutes(df: pl.DataFrame, cal: pl.DataFrame, a: str, b: str) -> pl.DataFrame:
    """Interval rows (agent, a, b) -> (pt_date, minute, agent) for every window minute the interval overlaps.
    An interval is attached to the PT day of its start and, if different, of its end (each clipped to that window)."""
    w = cal.select("pt_date", "win_start", "n_min")
    parts = []
    for col in (a, b):
        x = (df.with_columns(pl.col(col).dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).alias("pt_date"))
             .join(w, on="pt_date"))
        parts.append(x)
    x = pl.concat(parts).unique(subset=["agent", a, b, "pt_date"])
    x = x.with_columns(((pl.col(a) - pl.col("win_start")).dt.total_seconds() / 60).alias("fa"),
                       ((pl.col(b) - pl.col("win_start")).dt.total_seconds() / 60).alias("fb"))
    x = x.with_columns(pl.col("fa").floor().clip(0, None).cast(pl.Int32).alias("m0"),
                       (pl.col("fb").ceil().cast(pl.Int32) - 1).alias("m1"))
    x = x.with_columns(pl.min_horizontal("m1", pl.col("n_min") - 1).alias("m1")).filter(pl.col("m1") >= pl.col("m0"))
    return (x.with_columns(pl.int_ranges("m0", pl.col("m1") + 1).alias("minute")).explode("minute")
            .select("pt_date", pl.col("minute").cast(pl.Int32), "agent").unique())


def activity_times() -> dict:
    """Per agent: sorted epoch seconds of every logged action (events_core agent events + actions turns)."""
    ev = pl.read_parquet(SH / "events_core.parquet", columns=["t", "agent", "actor_kind"]).filter(
        (pl.col("actor_kind") == "agent") & pl.col("agent").is_not_null()).select("t", "agent")
    ac = pl.read_parquet(SH / "actions.parquet", columns=["t", "agent"]).filter(pl.col("agent").is_not_null())
    allt = pl.concat([ev, ac]).with_columns((pl.col("t").dt.epoch("us") / 1e6).alias("s")).sort("agent", "s")
    return {a: g["s"].to_numpy() for (a,), g in allt.group_by("agent")}


def adjacent_gaps(targets: pl.DataFrame, T: dict, before=True, after=True) -> pl.DataFrame:
    """For target rows (agent, t): the gaps to the agent's previous / next logged action, capped at GAP_CAP_S."""
    rows = []
    for (a,), g in targets.group_by("agent"):
        arr = T.get(a)
        if arr is None or len(arr) == 0:
            continue
        s = g["t"].dt.epoch("us").to_numpy() / 1e6
        ip = np.searchsorted(arr, s - 0.5, side="left") - 1
        inx = np.searchsorted(arr, s + 0.5, side="right")
        prev = np.where(ip >= 0, arr[np.clip(ip, 0, None)], s - GAP_CAP_S)
        nxt = np.where(inx < len(arr), arr[np.clip(inx, None, len(arr) - 1)], s + GAP_CAP_S)
        prev = np.maximum(prev, s - GAP_CAP_S)
        nxt = np.minimum(nxt, s + GAP_CAP_S)
        if before:
            rows.append(pl.DataFrame({"agent": np.full(len(s), a, np.int8), "a": prev, "b": s}))
        if after:
            rows.append(pl.DataFrame({"agent": np.full(len(s), a, np.int8), "a": s, "b": nxt}))
    df = pl.concat(rows).filter(pl.col("b") > pl.col("a"))
    return df.with_columns(pl.from_epoch((pl.col("a") * 1e6).cast(pl.Int64), "us").dt.replace_time_zone("UTC").alias("a"),
                           pl.from_epoch((pl.col("b") * 1e6).cast(pl.Int64), "us").dt.replace_time_zone("UTC").alias("b"))


def operator_messages() -> pl.DataFrame:
    """Operator pause / resume messages (automated speaker, regex on text; no text kept): t, kind, pt_date."""
    c = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "speaker_kind"]).filter(
        pl.col("speaker_kind") == "automated")
    tx = pl.read_parquet(SH / "chat_text.parquet", columns=["message_id", "text"]).join(c.select("message_id"), on="message_id")
    m = (c.join(tx, on="message_id")
         .with_columns(pl.when(pl.col("text").str.contains(PAUSE_RX)).then(pl.lit("pause"))
                       .when(pl.col("text").str.contains(RESUME_RX)).then(pl.lit("resume")).alias("kind"))
         .drop("text").filter(pl.col("kind").is_not_null())
         .with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).alias("pt_date")))
    return m.select("t", "kind", "pt_date").sort("t")


def scheduled_flags(grid: pl.DataFrame, cal: pl.DataFrame) -> pl.DataFrame:
    """Per (pt_date, minute): scheduled = the village is operator-paused at the minute's midpoint.
    Days with >= 1 resume message: follow that day's pause/resume timeline (before the day's first message the state is
    'off' if that message is a resume). Days without a resume message: outside the period's median run (time of day of
    the resume / pause messages where present, else of the window) +-5 min."""
    m = operator_messages()
    tod = lambda c: (c.dt.convert_time_zone("America/Los_Angeles").dt.hour().cast(pl.Float64) * 60
                     + c.dt.convert_time_zone("America/Los_Angeles").dt.minute()
                     + c.dt.convert_time_zone("America/Los_Angeles").dt.second() / 60)
    msg_days = set(m.filter(pl.col("kind") == "resume")["pt_date"].to_list())
    g = grid.select("pt_date", "goal_no", "minute", "t").with_columns(
        (pl.col("t") + pl.duration(seconds=30)).alias("tm"), pl.col("pt_date").is_in(list(msg_days)).alias("msg_sched"))
    # timeline days: as-of join of each minute midpoint to the last operator message of the same day
    a = (g.filter("msg_sched").sort("tm")
         .join_asof(m.sort("t").rename({"pt_date": "mday"}), left_on="tm", right_on="t", strategy="backward", suffix="_m"))
    first = m.group_by("pt_date").agg(pl.col("kind").first().alias("first_kind"))
    a = a.join(first, on="pt_date", how="left").with_columns(
        pl.when(pl.col("mday") == pl.col("pt_date")).then(pl.col("kind") == "pause")
        .otherwise(pl.col("first_kind") == "resume").alias("scheduled"))
    # fallback days: period median run
    on_days = m.filter(pl.col("pt_date").is_in(list(msg_days)))
    r0 = on_days.filter(pl.col("kind") == "resume").group_by("pt_date").agg(pl.col("t").min().alias("r"))
    p1 = on_days.filter(pl.col("kind") == "pause").group_by("pt_date").agg(pl.col("t").max().alias("p"))
    d = cal.select("pt_date", "goal_no", "win_start", "win_end").join(r0, on="pt_date", how="left").join(p1, on="pt_date", how="left")
    d = d.with_columns(tod(pl.coalesce("r", "win_start")).alias("tod0"), tod(pl.coalesce("p", "win_end")).alias("tod1"))
    med = d.group_by("goal_no").agg(pl.col("tod0").median().alias("med0"), pl.col("tod1").median().alias("med1"))
    b = (g.filter(~pl.col("msg_sched")).join(med, on="goal_no", how="left")
         .with_columns(tod(pl.col("tm")).alias("x"))
         .with_columns(((pl.col("x") < pl.col("med0") - SCHED_TOL_MIN) | (pl.col("x") > pl.col("med1") + SCHED_TOL_MIN))
                       .fill_null(False).alias("scheduled")))
    return pl.concat([a.select("pt_date", "minute", "msg_sched", "scheduled"),
                      b.select("pt_date", "minute", "msg_sched", "scheduled")])


def main(out_dir: Path = OUT, turn_errors: Path = TURN_ERRORS, bins: Path | None = None):
    """`bins` overrides the activity_bins input (e.g. the DQ8 activity_bins_fixed sidecar)."""
    t0 = time.time()
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    cal = calendar()
    ab = pl.read_parquet(Path(bins) if bins else SH / "activity_bins.parquet",
                         columns=["pt_date", "minute", "agent", "state"]).with_columns(
        pl.col("minute").cast(pl.Int32))
    act = ab.filter(pl.col("state") >= 3)
    span = act.group_by("pt_date", "agent").agg(pl.col("minute").min().alias("first"), pl.col("minute").max().alias("last"))
    pres = span.select("pt_date", "agent")
    npres = pres.group_by("pt_date").agg(pl.len().cast(pl.Int8).alias("n_present"))
    print(f"loaded activity {time.time() - t0:.0f}s", flush=True)

    # ---- reason intervals -> agent-minutes
    T = activity_times()
    te = pl.read_parquet(turn_errors).filter(pl.col("err_cat").cast(pl.String).is_in(INFRA) & pl.col("agent").is_not_null())
    infra_m = to_minutes(adjacent_gaps(te.select("agent", "t"), T), cal, "a", "b").with_columns(pl.lit(REASONS["infra_err"]).alias("r"))
    ev = pl.read_parquet(SH / "events_core.parquet", columns=["t", "agent", "action_type"]).filter(pl.col("action_type") == "CONSOLIDATE")
    cons_m = to_minutes(adjacent_gaps(ev.select("agent", "t"), T, before=True, after=False), cal, "a", "b").with_columns(
        pl.lit(REASONS["consol"]).alias("r"))
    ir = idle_spells().select("agent", "regime", "t_prev_action", "t_start", "t_end")
    ir = ir.with_columns(pl.when(pl.col("regime") == "III").then(pl.col("t_start"))
                         .otherwise(pl.coalesce("t_prev_action", "t_start")).alias("a"), pl.col("t_end").alias("b")).filter(
        pl.col("b") > pl.col("a"))
    pause_m = to_minutes(ir.select("agent", "a", "b"), cal, "a", "b").with_columns(pl.lit(REASONS["pause"]).alias("r"))
    print(f"reason intervals {time.time() - t0:.0f}s", flush=True)

    # silent present agent-minutes with their first-match reason
    sil = (ab.filter(pl.col("state") <= 2).join(pres, on=["pt_date", "agent"], how="semi")
           .join(span, on=["pt_date", "agent"])
           .with_columns(pl.when(pl.col("minute") < pl.col("first")).then(REASONS["pre"])
                         .when(pl.col("minute") > pl.col("last")).then(REASONS["post"]).otherwise(0).alias("r0")))
    for tab in (infra_m, cons_m, pause_m):  # first match: infra > consol > pause
        sil = sil.join(tab.rename({"r": "rx"}), on=["pt_date", "minute", "agent"], how="left").with_columns(
            pl.when(pl.col("r0") == 0).then(pl.col("rx").fill_null(0)).otherwise(pl.col("r0")).alias("r0")).drop("rx")
    sil = sil.select("pt_date", "minute", "agent", pl.col("r0").cast(pl.Int8).alias("reason"))
    sil.filter(pl.col("reason") > 0).sort("pt_date", "minute", "agent").write_parquet(out_dir / "reasons.parquet", compression="zstd")

    # ---- per-minute table
    K = (act.join(pres, on=["pt_date", "agent"], how="semi").group_by("pt_date", "minute").agg(pl.len().cast(pl.Int8).alias("K")))
    grid = (cal.select("pt_date", "goal_no", "regime", "holdout", "win_start", "n_min")
            .with_columns(pl.int_ranges(0, pl.col("n_min")).alias("minute")).explode("minute")
            .with_columns(pl.col("minute").cast(pl.Int32),
                          (pl.col("win_start") + pl.duration(minutes=pl.col("minute"))).alias("t")))
    rc = (sil.group_by("pt_date", "minute").agg(*[(pl.col("reason") == v).sum().cast(pl.Int8).alias(f"n_{k}")
                                                   for k, v in REASONS.items()]))
    # infra burst: >= 2 distinct present agents with an infra-error turn in [t-5, t]
    tem = (te.with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).alias("pt_date"))
           .join(cal.select("pt_date", "win_start"), on="pt_date")
           .with_columns(((pl.col("t") - pl.col("win_start")).dt.total_seconds() // 60).cast(pl.Int32).alias("m"))
           .join(pres, on=["pt_date", "agent"], how="semi")
           .with_columns(pl.int_ranges("m", pl.col("m") + 6).alias("minute")).explode("minute")
           .group_by("pt_date", "minute").agg(pl.col("agent").n_unique().cast(pl.Int8).alias("n_infra_agents_5m")))
    sch = scheduled_flags(grid, cal)
    S = (grid.join(npres, on="pt_date", how="left").join(K, on=["pt_date", "minute"], how="left")
         .join(rc, on=["pt_date", "minute"], how="left").join(tem, on=["pt_date", "minute"], how="left")
         .join(sch, on=["pt_date", "minute"], how="left")
         .with_columns(pl.col("n_present").fill_null(0), pl.col("K").fill_null(0),
                       *[pl.col(f"n_{k}").fill_null(0) for k in REASONS], pl.col("n_infra_agents_5m").fill_null(0)))
    S = S.with_columns(((pl.col("K") <= 1) & (pl.col("n_present") >= MIN_PRESENT)).alias("js"),
                       pl.col("scheduled").fill_null(False),
                       (pl.col("n_infra_agents_5m") >= 2).alias("infra_burst"),
                       (pl.col("n_present").cast(pl.Int16) - pl.col("K")).alias("n_sil"))
    edge = pl.col("n_pre") + pl.col("n_post")
    nrec = edge + pl.col("n_infra_err") + pl.col("n_consol") + pl.col("n_pause")
    S = S.with_columns((pl.col("js") & (pl.col("scheduled") | (2 * nrec >= pl.col("n_sil")))).alias("explained"),
                       (pl.col("js") & (pl.col("scheduled") | (nrec >= pl.col("n_sil") - 1))).alias("explained_strict"))
    best = pl.max_horizontal(edge, pl.col("n_infra_err"), pl.col("n_pause"), pl.col("n_consol"))
    S = S.with_columns(
        pl.when(~pl.col("js")).then(None)
        .when(pl.col("scheduled")).then(pl.lit("scheduled"))
        .when(~pl.col("explained")).then(pl.lit("unexplained"))
        .when(edge == best).then(pl.lit("edge"))
        .when(pl.col("n_infra_err") == best).then(pl.lit("infra_error"))
        .when(pl.col("n_pause") == best).then(pl.lit("pause"))
        .otherwise(pl.lit("consolidation")).alias("cause"))
    # runs of JS minutes
    S = S.sort("pt_date", "minute").with_columns(
        ((pl.col("js") != pl.col("js").shift(1).over("pt_date")) | (pl.col("minute") == 0)).fill_null(True).cum_sum().alias("run"))
    runs = (S.filter("js").group_by("pt_date", "run").agg(
        pl.col("goal_no").first(), pl.col("regime").first(), pl.col("holdout").first(),
        pl.col("t").min().alias("t_start"), (pl.col("t").max() + pl.duration(minutes=1)).alias("t_end"),
        pl.col("minute").min().alias("m_start"), (pl.col("minute").max() + 1).alias("m_end"),
        pl.len().cast(pl.Int32).alias("dur_min"), pl.col("n_present").first(), pl.col("K").max().alias("k_max"),
        (pl.col("K") == 0).sum().cast(pl.Int32).alias("k0_min"), pl.col("n_min").first(),
        pl.col("explained").mean().alias("frac_explained"), pl.col("infra_burst").any().alias("infra_burst"),
        *[(pl.col("cause") == c).mean().cast(pl.Float32).alias(f"frac_{c}") for c in CAUSES],
        pl.col("cause").mode().sort().first().alias("cause_mode"),
        pl.col("K").cast(pl.Int8).alias("Kseq")))
    # longest K = 0 sub-run
    def longest_zero(seq):
        best = cur = 0
        for k in seq:
            cur = cur + 1 if k == 0 else 0
            best = max(best, cur)
        return best
    runs = runs.with_columns(pl.col("Kseq").map_elements(longest_zero, return_dtype=pl.Int32).alias("k0_longest"))
    # majority cause by minutes (mode ties broken by CAUSES order)
    fr = runs.select([f"frac_{c}" for c in CAUSES]).to_numpy()
    runs = runs.with_columns(pl.Series("cause", [CAUSES[i] for i in fr.argmax(1)]))
    # infra-error agents inside the run or 5 min before
    tem2 = (te.with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).alias("pt_date"))
            .join(cal.select("pt_date", "win_start"), on="pt_date")
            .with_columns(((pl.col("t") - pl.col("win_start")).dt.total_seconds() // 60).cast(pl.Int32).alias("m"))
            .join(pres, on=["pt_date", "agent"], how="semi").select("pt_date", "m", "agent"))
    ie = (runs.select("pt_date", "run", "m_start", "m_end").join(tem2, on="pt_date")
          .filter((pl.col("m") >= pl.col("m_start") - 5) & (pl.col("m") < pl.col("m_end")))
          .group_by("pt_date", "run").agg(pl.col("agent").n_unique().cast(pl.Int8).alias("n_infra_err_agents")))
    runs = (runs.join(ie, on=["pt_date", "run"], how="left").with_columns(pl.col("n_infra_err_agents").fill_null(0))
            .sort("t_start").with_row_index("outage_id").with_columns(pl.col("outage_id").cast(pl.Int32)))
    outages = runs.select(
        "outage_id", "pt_date", "goal_no", "regime", "holdout", "t_start", "t_end", "m_start", "m_end", "dur_min",
        "n_present", "k_max", "k0_min", (pl.col("k0_longest") >= OFF_MIN).alias("village_off"), "k0_longest",
        ((pl.col("m_start") == 0) | (pl.col("m_end") >= pl.col("n_min"))).alias("at_day_edge"), "cause",
        *[f"frac_{c}" for c in CAUSES], (pl.col("frac_explained") >= 0.5).alias("explained"),
        pl.col("frac_explained").cast(pl.Float32), "infra_burst", "n_infra_err_agents")
    outages.write_parquet(out_dir / "outages.parquet", compression="zstd")
    S = S.join(runs.select("pt_date", "run", "outage_id"), on=["pt_date", "run"], how="left")
    stall = S.select("pt_date", "goal_no", "regime", "holdout", "minute", "t", "n_present", "K", "js", "scheduled",
                     "msg_sched", *[f"n_{k}" for k in REASONS if k != "none"], "n_none", "explained", "explained_strict",
                     "cause", "infra_burst", "n_infra_agents_5m", "outage_id")
    stall.write_parquet(out_dir / "stall_minutes.parquet", compression="zstd")

    if out_dir == OUT:
        write_provenance("outages", ["activity_bins", "calendar", "events_core", "actions", "chat_core",
                                     "chat_text (automated rows, regex only)", "roster", "turn_errors",
                                     "idle spells (recomputed, H09 rule)"],
                         {"gap_cap_s": GAP_CAP_S, "village_off_min": OFF_MIN, "sched_tol_min_no_messages": SCHED_TOL_MIN,
                          "min_present": MIN_PRESENT, "infra_categories": INFRA, "reasons": REASONS, "causes": CAUSES,
                          "pause_regex": PAUSE_RX, "resume_regex": RESUME_RX, "js": "K <= 1 among day-present agents",
                          "explained": ">= half of silent present agents have a reason, or scheduled",
                          "holdout": "all days kept; flagged in `holdout`",
                          "source": "hypotheses/H38-platform-stalls/scheme/build_outages.py (rule unchanged; H09 idle spells recomputed)"})
    nh = stall.filter(~pl.col("holdout"))
    print(f"outages {outages.height:,} rows ({outages.filter(~pl.col('holdout')).height:,} non-holdout); "
          f"minutes {stall.height:,}; JS share (non-holdout) {nh['js'].mean():.3f}; {time.time() - t0:.0f}s")




def verify():
    """Shared tables vs H38's (exact on H38's columns) and the recomputed idle spells vs H09's idle_runs."""
    h38 = ROOT / "data/processed/H38-platform-stalls"
    res = {}
    for name in ("outages", "stall_minutes", "reasons"):
        a = pl.read_parquet(h38 / f"{name}.parquet")
        b = pl.read_parquet(OUT / f"{name}.parquet").select(a.columns)
        key = [c for c in ("pt_date", "minute", "agent", "outage_id") if c in a.columns]
        res[name] = {"h38_rows": a.height, "shared_rows": b.height, "equal": a.sort(key).equals(b.sort(key))}
        if not res[name]["equal"] and a.height == b.height:
            a2, b2 = a.sort(key), b.sort(key)
            res[name]["columns_differing"] = [c for c in a.columns if not a2[c].equals(b2[c])]
    h09 = ROOT / "data/processed/H09-swarm-thermodynamics/idle_runs.parquet"
    if h09.exists():
        cols = ["agent", "regime", "t_prev_action", "t_start", "t_end"]
        a = pl.read_parquet(h09, columns=cols).sort("agent", "t_start")
        b = idle_spells().select(cols).sort("agent", "t_start")
        res["idle_spells_vs_H09"] = {"h09_rows": a.height, "shared_rows": b.height, "equal": a.equals(b)}
    for k, v in res.items():
        print(k, v)
    return res


if __name__ == "__main__":
    if "--verify" in sys.argv:
        verify()
    elif "--fixed" in sys.argv:
        # outages from the corrected activity bins (DQ8), written to a sidecar folder until DQ7 rebuilds activity_bins
        fx = OUT / "outages_fixed"
        main(out_dir=fx, bins=OUT / "activity_bins_fixed.parquet")
        write_provenance("outages_fixed", ["activity_bins_fixed", "calendar", "events_core", "actions", "chat_core",
                                           "chat_text", "turn_errors"],
                         {"note": "outages/stall_minutes/reasons rebuilt from activity_bins_fixed (DQ8 join fix)",
                          "out_dir": str(fx.relative_to(ROOT))})
    else:
        main()
