"""Vectorized per-window state assembly for Jev behavior states v3 (design: infra/behavior_states/DESIGN.md).

Unit: one roster agent x one 5-minute window of a calendar day (w = minute // 5 of activity_bins; t0 = win_start + 5 w min).
Every timestamped row (action, command, event, chat message, exposure, intention) gets its window key (pt_date, agent, w)
once, then everything is grouped; nothing is filtered per window. The v2 per-window loop (label_windows.py) took ~1 s per
window; this assembles all ~295k grid cells in about a minute.

v3 fixes the state-assembly gaps reported by the blind labeler (stale intentions, recap/action desync, boot windows, looping):
  intention freshness  intention_age_min (t1 - time the current intention was written), intention_stale (> 60 min, i.e.
                       beyond the ~97th percentile of intention update intervals), intention_prev_day, intention_source
  desync context       previous window's actions, last commands and own-message count; next window's first actions and
                       first commands (own messages often recap work done in an earlier window)
  boot / startup       first_active_window (agent's first active window of the PT day), min_since_first_activity,
                       session_start (START_USING_COMPUTER in window), post_reset (context reset in the previous window)
  looping              longest_run (longest run of identical action+command, scaffold turns excluded), repeated_error_share
                       (errored actions repeating an earlier errored action+command of the window), noop_share ('none')
  self-repeat          self_repeat_share: share of own messages with cosine > 0.95 (bge-small, H12's rule) to an earlier
                       own message of the same PT day
  real failures        failures come from turn_outcomes (scan_turn_outcomes.py), NOT actions.error, which only means "stderr
                       was non-empty" (git and curl write normal progress there: 62% of git pushes are "errors")
  artifact changes     git commits / pushes printed by git, file writes, API/PR writes, deploys (turn_outcomes): the evidence
                       the execute_task tie-breaker needs
  command text         every bash turn's non-comment lines (turn_outcomes.cmd) plus the agent's own first comment line
                       (`# I'm committing ...`; regime-III commands almost always start with one), typed text for `type`
Scaffold artifacts (infra/README Known issues): the forced mouse_move after a context boundary is dropped from the action
counts and the looping statistics; mirror turns (pause / send_message_back_to_chat / search_history / move_to_room) stay in
the counts but are excluded from looping runs. Shell heads fall back to the head of turn_outcomes.cmd where bash_head is
null (regime III). Command verbs come from the artifact_commands_text sidecar.

Library:
  windows()               full grid (active and inactive cells) with counts and flags, no text
  features(keys=None)     per active window: numeric flags + text pieces (keys: optional DataFrame pt_date/agent/w)
  state_dict(row)         the JSON state sent to Jev for one feature row
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shared"))
from common import OUT  # noqa: E402

WIN_MIN = 5
WIN_S = WIN_MIN * 60
MIRROR = ["pause", "send_message_back_to_chat", "search_history", "move_to_room"]
STALE_MIN = 60
SELF_COS = 0.95
CHAT_BUDGET, CHAT_MIN, CHAT_MAX_MSGS = 1200, 160, 5   # characters of own chat per window; per message floor; messages
INTENT_CHARS, CMD_CHARS, N_CMD, N_CMD_CTX, CTX_CHARS = 300, 100, 4, 2, 80
TYPE_CHARS, N_TYPED, N_NOTES = 80, 2, 3
CHANGE = ["commit_ok", "push_ok", "file_write", "api_write", "deploy"]

TURN_OUTCOMES = OUT.parent / "behavior_states" / "turn_outcomes.parquet"  # scan_turn_outcomes.py (real failures, changes, text)
KEY = ["pt_date", "agent", "w"]
PT = "America/Los_Angeles"


def calendar() -> pl.DataFrame:
    return pl.read_parquet(OUT / "calendar.parquet", columns=["pt_date", "win_start", "holdout", "regime", "goal_no"])


def keyed(df: pl.DataFrame, cal: pl.DataFrame, tcol: str = "t") -> pl.DataFrame:
    """Add the window key (pt_date, w) exactly as activity_bins does (PT date of t; minute offset from win_start // 5)."""
    if "pt_date" in df.columns:
        df = df.drop("pt_date")
    return (df.with_columns(pl.col(tcol).dt.convert_time_zone(PT).dt.date().cast(pl.Utf8).alias("pt_date"))
            .join(cal.select("pt_date", "win_start"), on="pt_date")
            .with_columns(((pl.col(tcol) - pl.col("win_start")).dt.total_seconds() // WIN_S).cast(pl.Int32).alias("w"))
            .filter(pl.col("w") >= 0).drop("win_start"))


def windows() -> pl.DataFrame:
    """Every agent x 5-min window of the activity_bins grid (roster agents, calendar window), active or not."""
    cal = calendar()
    win = (pl.read_parquet(OUT / "activity_bins.parquet")
           .with_columns((pl.col("minute") // WIN_MIN).cast(pl.Int32).alias("w"))
           .group_by(KEY).agg(*[pl.col(c).sum().cast(pl.Int16) for c in ("talk", "turns", "idle", "paused", "consolidate", "other_event")]))
    win = win.with_columns(((pl.col("talk") + pl.col("turns") + pl.col("other_event") + pl.col("consolidate")) > 0).alias("active"))
    span = win.filter("active").group_by("pt_date", "agent").agg(pl.col("w").min().alias("w_first"), pl.col("w").max().alias("w_last"))
    win = (win.join(span, on=["pt_date", "agent"], how="left").join(cal, on="pt_date")
           .with_columns((pl.col("win_start") + pl.duration(minutes=pl.col("w") * WIN_MIN)).alias("t0"),
                         (pl.col("win_start") + pl.duration(minutes=(pl.col("w") + 1) * WIN_MIN)).alias("t1"),
                         ((pl.col("w") >= pl.col("w_first")) & (pl.col("w") <= pl.col("w_last"))).fill_null(False).alias("in_span"),
                         (pl.col("w") == pl.col("w_first")).fill_null(False).alias("first_active_window"),
                         ((pl.col("w") - pl.col("w_first")) * WIN_MIN).cast(pl.Int16).alias("min_since_first_activity"))
           .drop("win_start", "w_first", "w_last"))
    return win.sort(KEY)


def _counts(df: pl.DataFrame, col: str, name: str, top: int) -> pl.DataFrame:
    """'a×3, b×1' per window, most frequent first."""
    return (df.drop_nulls(col).group_by(KEY + [col]).len()
            .sort(KEY + ["len", col], descending=[False, False, False, True, False])
            .with_columns(pl.concat_str(pl.col(col).cast(pl.Utf8), pl.lit("×"), pl.col("len").cast(pl.Utf8)).alias("s"))
            .group_by(KEY, maintain_order=True).agg(pl.col("s").head(top).str.join(", ").alias(name)))


def _actions(cal: pl.DataFrame, keys: pl.DataFrame | None) -> pl.DataFrame:
    acts = pl.read_parquet(OUT / "actions.parquet", columns=["t", "agent", "action", "bash_head", "error"]).rename({"error": "stderr"})
    outc = pl.read_parquet(TURN_OUTCOMES, columns=["agent", "t", "failed", "commit_ok", "push_ok", "file_write", "api_write", "deploy", "note", "cmd"])
    verbs = (pl.read_parquet(OUT / "artifact_commands_text.parquet", columns=["agent", "t", "verbs"]).unique(["agent", "t"], keep="first"))
    acts = acts.join(outc, on=["agent", "t"], how="left").join(verbs, on=["agent", "t"], how="left").sort("agent", "t")
    acts = acts.with_columns(pl.col("failed").fill_null(False), *[pl.col(c).fill_null(False) for c in CHANGE])
    it = pl.read_parquet(OUT / "intentions.parquet", columns=["t", "agent"]).rename({"t": "t_int"}).sort("t_int")
    acts = acts.with_columns(pl.col("t").shift(1).over("agent").alias("prev_t"))
    acts = acts.join_asof(it, left_on="t", right_on="t_int", by="agent", strategy="backward")
    acts = keyed(acts, cal)
    if keys is not None:  # restrict to the requested windows and their neighbours (context)
        nb = pl.concat([keys.with_columns((pl.col("w") + d).cast(pl.Int32)) for d in (-1, 0, 1)]).unique()
        acts = acts.join(nb, on=KEY, how="semi")
    first_of_day = pl.col("pt_date") != pl.col("pt_date").shift(1).over("agent")
    acts = acts.sort("agent", "t").with_columns(
        ((pl.col("action") == "mouse_move")
         & ((pl.col("t_int").is_not_null() & (pl.col("prev_t").is_null() | (pl.col("t_int") > pl.col("prev_t")))) | first_of_day.fill_null(True)))
        .alias("forced"))
    derived = (pl.col("cmd").str.replace(r"^(cd \S+ ?(&&|;) ?)+", "").str.replace(r"^(\w+=\S* +)+", "")
               .str.extract(r"^([^\s;|&()]+)", 1).str.replace(r"^.*/", ""))
    is_bash = pl.col("action") == "bash"
    acts = acts.with_columns(
        pl.when(is_bash).then(pl.coalesce(pl.col("bash_head").cast(pl.Utf8), derived)).alias("head"),
        pl.when(is_bash).then(pl.when(pl.col("failed")).then(pl.lit("[failed] ")).otherwise(pl.lit("")) + pl.col("cmd").str.slice(0, CMD_CHARS)).alias("cmd_s"),
        pl.when(pl.col("action") == "type").then(pl.col("cmd").str.slice(0, TYPE_CHARS)).alias("typed"),
        pl.when(is_bash).then(pl.col("note")).alias("note"))
    acts = acts.with_columns(pl.concat_str(pl.col("action").cast(pl.Utf8), pl.lit("|"),
                                           pl.coalesce(pl.col("cmd").str.slice(0, 80), pl.col("head"), pl.lit(""))).alias("lkey"))
    a = acts.filter(~pl.col("forced"))
    # looping: runs of identical action+command, scaffold turns excluded
    loop = a.filter(~pl.col("action").cast(pl.Utf8).is_in(MIRROR)).sort("agent", "t")
    loop = loop.with_columns((pl.col("lkey") != pl.col("lkey").shift(1).over(KEY)).fill_null(True).cum_sum().over(KEY).alias("run"))
    runs = loop.group_by(KEY + ["run"]).len().group_by(KEY).agg(pl.col("len").max().cast(pl.Int16).alias("longest_run"))
    errs = (a.filter(pl.col("failed")).group_by(KEY)
            .agg(pl.len().alias("ne"), pl.col("lkey").n_unique().alias("nu"))
            .with_columns(((pl.col("ne") - pl.col("nu")) / pl.col("ne")).cast(pl.Float32).alias("repeated_error_share"))
            .select(KEY + ["repeated_error_share"]))
    base = a.sort("agent", "t").group_by(KEY, maintain_order=True).agg(
        pl.len().cast(pl.Int16).alias("n_actions"), pl.col("failed").sum().cast(pl.Int16).alias("n_errors"),
        pl.col("stderr").sum().cast(pl.Int16).alias("n_stderr"),
        *[pl.col(c).sum().cast(pl.Int16).alias(f"n_{c}") for c in CHANGE],
        (pl.col("action") == "none").mean().cast(pl.Float32).alias("noop_share"),
        pl.col("cmd_s").drop_nulls().unique(maintain_order=True).alias("cmds"),
        pl.col("note").drop_nulls().unique(maintain_order=True).alias("notes"),
        pl.col("typed").drop_nulls().unique(maintain_order=True).alias("typed"),
        pl.concat_str(pl.col("action").cast(pl.Utf8), pl.when(pl.col("head").is_not_null()).then(pl.lit(": ") + pl.col("head")).otherwise(pl.lit("")))
        .head(5).alias("first_actions"))
    forced = acts.group_by(KEY).agg(pl.col("forced").sum().cast(pl.Int16).alias("n_forced_mouse"))
    vb = a.select(KEY + ["verbs"]).explode("verbs").rename({"verbs": "verb"})
    out = (base.join(_counts(a, "action", "action_counts", 14), on=KEY, how="left")
           .join(_counts(a, "head", "head_counts", 10), on=KEY, how="left")
           .join(_counts(vb, "verb", "verb_counts", 10), on=KEY, how="left")
           .join(runs, on=KEY, how="left").join(errs, on=KEY, how="left").join(forced, on=KEY, how="full", coalesce=True))
    return out.with_columns(pl.col("longest_run").fill_null(0), pl.col("n_actions").fill_null(0), pl.col("n_errors").fill_null(0),
                            pl.col("n_forced_mouse").fill_null(0))


def _events(cal: pl.DataFrame) -> pl.DataFrame:
    ev = pl.read_parquet(OUT / "events_core.parquet", columns=["t", "agent", "actor_kind", "action_type", "pause_s"])
    ev = keyed(ev.filter((pl.col("actor_kind") == "agent") & pl.col("agent").is_not_null() & (pl.col("action_type") != "AGENT_TALK")), cal)
    agg = ev.group_by(KEY).agg((pl.col("action_type") == "START_USING_COMPUTER").any().alias("session_start"),
                               ((pl.col("action_type") == "START_USING_COMPUTER") | (pl.col("action_type") == "CONSOLIDATE")).any().alias("reset"),
                               pl.col("pause_s").filter(pl.col("action_type") == "PAUSE").sum().cast(pl.Int32).alias("pause_s"))
    return agg.join(_counts(ev, "action_type", "event_counts", 10), on=KEY, how="left")


def self_repeat(chat: pl.DataFrame) -> pl.DataFrame:
    """message_id -> self_repeat (cosine > 0.95 to an earlier own message of the same PT day; bge-small, normalized)."""
    E = np.load(OUT / "embeddings/chat_bge_small.npy", mmap_mode="r")
    idx = pl.read_parquet(OUT / "embeddings/chat_index.parquet").with_row_index("erow")
    c = (chat.select("message_id", "agent", "pt_date", "t").join(idx, on="message_id", how="inner")
         .sort("agent", "pt_date", "t"))  # every chat message has an embedding row
    rows = c["erow"].to_numpy().astype(np.int64)
    grp = (c["agent"].cast(pl.Utf8) + "|" + c["pt_date"]).to_numpy()
    flag = np.zeros(len(c), dtype=bool)
    starts = np.r_[0, np.flatnonzero(grp[1:] != grp[:-1]) + 1, len(c)]
    for s, e in zip(starts[:-1], starts[1:]):
        if e - s < 2:
            continue
        r = rows[s:e]
        V = np.asarray(E[np.sort(r)], dtype=np.float32)[np.argsort(np.argsort(r))]  # sorted reads from the memmap
        S = V @ V.T
        S[np.triu_indices(len(r))] = -1.0  # earlier messages only
        flag[s:e] = S.max(1) > SELF_COS
    return c.select("message_id").with_columns(pl.Series("self_repeat", flag))


def _chat(cal: pl.DataFrame) -> tuple[pl.DataFrame, pl.DataFrame]:
    core = pl.read_parquet(OUT / "chat_core.parquet", columns=["message_id", "t", "pt_date", "speaker_kind", "agent"])
    own = core.filter((pl.col("speaker_kind") == "agent") & pl.col("agent").is_not_null())
    own = own.join(self_repeat(own), on="message_id", how="left")
    own = keyed(own.join(pl.read_parquet(OUT / "chat_text.parquet", columns=["message_id", "text"]), on="message_id"), cal)
    own_w = own.sort("t").group_by(KEY, maintain_order=True).agg(
        pl.len().cast(pl.Int16).alias("n_own"), pl.col("self_repeat").sum().cast(pl.Int16).alias("n_self_repeat"),
        pl.col("text").alias("texts"))
    # exposure: messages posted in the window to a room the agent was in (exposure.msg = row of chat_core sorted by t)
    ment = pl.read_parquet(OUT / "chat_mentions_clean.parquet", columns=["message_id", "mentions_roster"])
    msgs = (core.sort("t", maintain_order=True).with_row_index("msg").join(ment, on="message_id", how="left")
            .select(pl.col("msg").cast(pl.UInt32), "t", "speaker_kind", pl.col("agent").alias("sender"), "mentions_roster"))
    exp = pl.read_parquet(OUT / "exposure.parquet", columns=["msg", "agent"]).join(msgs, on="msg")
    exp = keyed(exp, cal).with_columns(pl.col("mentions_roster").list.contains(pl.col("agent")).fill_null(False).alias("ment"))
    exp_w = exp.group_by(KEY).agg(pl.len().cast(pl.Int16).alias("n_seen"),
                                  (pl.col("speaker_kind") == "human").sum().cast(pl.Int16).alias("n_seen_human"),
                                  (pl.col("speaker_kind") == "automated").sum().cast(pl.Int16).alias("n_seen_automated"),
                                  pl.col("ment").sum().cast(pl.Int16).alias("n_seen_mentioning"))
    return own_w, exp_w


def _intentions(win: pl.DataFrame) -> pl.DataFrame:
    it = (pl.read_parquet(OUT / "intentions.parquet").join(pl.read_parquet(OUT / "intentions_text.parquet", columns=["event_index", "goal_text"]),
                                                           on="event_index")
          .select("agent", pl.col("t").alias("t_int"), "source", "goal_text").sort("t_int"))
    j = win.select(KEY + ["t1"]).sort("t1").join_asof(it, left_on="t1", right_on="t_int", by="agent", strategy="backward",
                                                       allow_exact_matches=False)
    return j.with_columns(
        ((pl.col("t1") - pl.col("t_int")).dt.total_seconds() / 60).round(0).cast(pl.Int32).alias("intention_age_min"),
        (pl.col("t_int").dt.convert_time_zone(PT).dt.date().cast(pl.Utf8) != pl.col("pt_date")).alias("intention_prev_day"),
    ).with_columns((pl.col("intention_age_min") > STALE_MIN).alias("intention_stale")).drop("t1", "t_int")


def features(keys: pl.DataFrame | None = None) -> pl.DataFrame:
    """One row per active window (or per requested key) with flags and text pieces for state_dict()."""
    cal = calendar()
    win = windows()
    act = win.filter("active")
    if keys is not None:
        act = act.join(keys.select(KEY).with_columns(pl.col("agent").cast(pl.Int8), pl.col("w").cast(pl.Int32)), on=KEY, how="semi")
    k3 = act.select(KEY)
    A = _actions(cal, k3 if keys is not None else None)
    own_w, exp_w = _chat(cal)
    ev = _events(cal)
    f = (act.join(A, on=KEY, how="left").join(own_w, on=KEY, how="left").join(exp_w, on=KEY, how="left")
         .join(ev, on=KEY, how="left").join(_intentions(act), on=KEY, how="left"))
    prev = (A.select(KEY + ["action_counts", "cmds"]).join(own_w.select(KEY + ["n_own"]), on=KEY, how="full", coalesce=True)
            .join(ev.select(KEY + ["reset"]), on=KEY, how="full", coalesce=True)
            .with_columns((pl.col("w") + 1).cast(pl.Int32))
            .rename({"action_counts": "prev_action_counts", "cmds": "prev_cmds", "n_own": "prev_n_own", "reset": "post_reset"}))
    nxt = (A.select(KEY + ["first_actions", "cmds"]).with_columns((pl.col("w") - 1).cast(pl.Int32))
           .rename({"first_actions": "next_first_actions", "cmds": "next_cmds"}))
    f = f.join(prev, on=KEY, how="left").join(nxt, on=KEY, how="left")
    f = f.with_columns(
        *[pl.col(c).fill_null(0) for c in ("n_actions", "n_errors", "n_stderr", "longest_run", "n_own", "n_self_repeat", "n_seen", "n_seen_human",
                                           "n_seen_automated", "n_seen_mentioning", "n_forced_mouse", "pause_s")
          + tuple(f"n_{c}" for c in CHANGE)],
        pl.col("session_start").fill_null(False), pl.col("post_reset").fill_null(False),
        pl.when(pl.col("n_errors") > 0).then(pl.col("repeated_error_share").fill_null(0)).alias("repeated_error_share"),
        pl.when(pl.col("n_own") > 0).then((pl.col("n_self_repeat") / pl.col("n_own")).cast(pl.Float32)).alias("self_repeat_share"),
        (pl.col("n_own") > 0).alias("has_chat"))
    return f.sort(KEY)


def _chat_list(texts: list[str] | None) -> list[str]:
    t = (texts or [])[:CHAT_MAX_MSGS]
    if not t:
        return []
    per = max(CHAT_MIN, CHAT_BUDGET // len(t))
    out = [WS.sub(" ", (m or "")).strip()[:per] for m in t]
    if len(texts) > len(t):
        out.append(f"(+{len(texts) - len(t)} more messages)")
    return out


def _spread(xs: list | None, k: int) -> list:
    """Up to k items spread over the window (first ... last)."""
    if not xs:
        return []
    if len(xs) <= k:
        return list(xs)
    ix = np.linspace(0, len(xs) - 1, k).round().astype(int)
    return [xs[i] for i in dict.fromkeys(ix)]


def _rle(xs: list | None) -> str:
    """['bash: curl', 'bash: curl', 'key'] -> 'bash: curl ×2, key'."""
    out = []
    for x in xs or []:
        if out and out[-1][0] == x:
            out[-1][1] += 1
        else:
            out.append([x, 1])
    return ", ".join(f"{x} ×{n}" if n > 1 else x for x, n in out)


SOURCE = {"CONSOLIDATE": "memory consolidation", "START_USING_COMPUTER": "session start"}
CHANGE_NAMES = {"commit_ok": "git commits", "push_ok": "git pushes", "file_write": "file writes", "api_write": "API/PR writes", "deploy": "deploys"}
WS = __import__("re").compile(r"\s+")


def state_dict(r: dict) -> dict:
    """The JSON state sent to Jev for one window (gated text: Jev only, never stored outside data/). Zero / false fields are
    omitted to save tokens; their absence means zero / false."""
    st = {}
    if r.get("event_counts"):
        st["events"] = r["event_counts"]
    st["actions"] = r.get("action_counts") or "none"
    if r.get("cmds"):
        st["commands"] = _spread(r["cmds"], N_CMD)
    if r.get("notes"):
        st["command_comments"] = [n[:100] for n in _spread(r["notes"], N_NOTES)]
    if r.get("verb_counts"):
        st["command_verbs"] = r["verb_counts"]
    elif r.get("head_counts"):
        st["shell_heads"] = r["head_counts"]
    if r.get("typed"):
        st["typed_text"] = _spread(r["typed"], N_TYPED)
    ch = ", ".join(f"{CHANGE_NAMES[c]}×{int(r.get('n_' + c) or 0)}" for c in CHANGE if r.get("n_" + c))
    if ch:
        st["artifact_changes"] = ch
    if r["n_errors"]:
        st["failed_actions"] = int(r["n_errors"])
        if r.get("repeated_error_share"):
            st["failures_repeating_earlier_failure_share"] = round(float(r["repeated_error_share"]), 2)
    if r["longest_run"] >= 3:
        st["longest_identical_action_run"] = int(r["longest_run"])
    if r.get("noop_share"):
        st["no_op_action_share"] = round(float(r["noop_share"]), 2)
    msgs = _chat_list(r.get("texts"))
    if msgs:
        st["own_messages"] = msgs
        if r["n_self_repeat"]:
            st["own_messages_repeating_own_earlier_text"] = int(r["n_self_repeat"])
    st["messages_seen"] = int(r["n_seen"])
    if r["n_seen_human"]:
        st["messages_seen_from_humans"] = int(r["n_seen_human"])
    if r["n_seen_mentioning"]:
        st["messages_seen_mentioning_agent"] = int(r["n_seen_mentioning"])
    st["intention"] = WS.sub(" ", (r.get("goal_text") or "")).strip()[:INTENT_CHARS] or "unknown"
    if r.get("goal_text"):
        st["intention_from"] = SOURCE.get(r.get("source"), "unknown")
        st["intention_age_min"] = r.get("intention_age_min")
        if r.get("intention_stale"):
            st["intention_stale"] = True
    if r["first_active_window"]:
        st["first_active_window_today"] = True
    else:
        st["min_since_first_activity_today"] = int(r["min_since_first_activity"] or 0)
    for k, name in (("session_start", "session_started"), ("post_reset", "context_reset_in_prev_window")):
        if r[k]:
            st[name] = True
    if r["consolidate"]:
        st["memory_consolidations"] = int(r["consolidate"])
    if r["pause_s"]:
        st["declared_pause_s"] = int(r["pause_s"])
    if r.get("prev_action_counts") or r.get("prev_n_own"):
        pw = {"actions": r.get("prev_action_counts") or "none"}
        if r.get("prev_cmds"):
            pw["last_commands"] = [c[:CTX_CHARS] for c in r["prev_cmds"][-N_CMD_CTX:]]
        if r.get("prev_n_own"):
            pw["own_messages"] = int(r["prev_n_own"])
        st["prev_window"] = pw
    else:
        st["prev_window"] = "no activity"
    if r.get("next_first_actions"):
        nw = {"first_actions": _rle(r["next_first_actions"])}
        if r.get("next_cmds"):
            nw["first_commands"] = [c[:CTX_CHARS] for c in r["next_cmds"][:N_CMD_CTX]]
        st["next_window"] = nw
    else:
        st["next_window"] = "no activity"
    return st


FLAG_COLS = ["n_actions", "n_errors", "n_stderr", "repeated_error_share", "longest_run", "noop_share", "n_forced_mouse",
             "n_commit_ok", "n_push_ok", "n_file_write", "n_api_write", "n_deploy", "n_own", "self_repeat_share",
             "n_seen", "n_seen_human", "n_seen_automated", "n_seen_mentioning", "intention_age_min", "intention_stale", "intention_prev_day",
             "source", "first_active_window", "min_since_first_activity", "session_start", "post_reset", "pause_s", "has_chat"]
