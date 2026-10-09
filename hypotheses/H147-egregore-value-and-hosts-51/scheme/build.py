"""H147 scheme: event tables, cleaned own-repo commit panels and role-text alignment for #51 (07-06 -> 09-04).

Builds data/processed/H147-egregore-value-and-hosts-51/:
  commits_clean.parquet   kept #51 agent commits (memeplex.clean_commits since 4f6ab2e, plus a '-chat@' author check),
                          with repo slug, bin and H143 window; codes only
  own_repos.parquet       window x agent x slug: commits, share, own flag (own = >= 50% of the window's cleaned
                          commits on the repo are the agent's)
  stmt_align.parquet      one row per #51 statement (srow): agent, t, bin, role-text cosine in the regime-III whitened
                          32-d basis, bge and gte, raw (white) and style-residualized-within-period statement vectors
  panel.parquet           agent x 2-h bin (H145's bins and DQ8 presence): calls, non-pause calls, statements, chat
                          messages, talk share, cleaned commits (all / own repos), mean role alignment (4 variants)
  events_fp.parquet       forced erasures F (reset_forced) and placebo calls P (call 21 of a segment of >= 40 calls;
                          H70 rule) of #51 agents, with stratum (agent|unit), cluster (agent|pt_date), the event bin,
                          and own output in calls -20..-1 / 1..20 (work commits, statements, own-repo commits)
  scramble_events.json    the dated hub-loss and operator-action events (fixed in the card before any statistic)
  placebo_days.parquet    per event: placebo days (same weekday; >= 3 calendar days from every event day) and the
                          all-weekday variant
Commit rules (brief "data traps"; H145 card): `memeplex.clean_commits` (not automated; surprise-lab-mirror-proofs
dropped by repo name; busy single-file streams kept; no touching call on the repo that day; hash dedupe; before the
author's join date). A draft of this scheme (2026-10-09 early, never used for a statistic) had its own stream and
no-call rules; it was replaced by the shared function after the fix in 4f6ab2e.
Usage: uv run python hypotheses/H147-egregore-value-and-hosts-51/scheme/build.py
"""
from __future__ import annotations

import datetime as dt
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h147common as C  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import embed_models as EM  # noqa: E402  (infra/shared)

S = C.SHARED
T0 = time.time()


def log(*a):
    print(f"[{time.time() - T0:6.0f}s]", *a, flush=True)


def in_days(df: pl.DataFrame) -> pl.DataFrame:
    return df.filter(pl.col("pt_date").is_in(C.days()["pt_date"].implode()))


# ------------------------------------------------------------------------------------------------ commits
def chat_email_hashes(repos: list[str]) -> set[str]:
    out = set()
    for r in repos:
        p = C.ROOT / "data/raw/repos" / (r + ".git")
        if not p.exists():
            continue
        res = subprocess.run(["git", "-C", str(p), "log", "--all", "--since=2026-07-04", "--until=2026-09-06",
                              "--format=%H%x09%ae"], capture_output=True, text=True)
        for line in res.stdout.splitlines():
            h, _, e = line.partition("\t")
            if "-chat@" in e:
                out.add(h)
    return out


def build_commits():
    """Cleaned #51 commits: memeplex.clean_commits (shared rules since 4f6ab2e: not automated, the
    surprise-lab-mirror-proofs repo dropped by name, no touching call on the repo that day, hash dedupe, before the
    author's join date), then '-chat@agentvillage.org' authors (raw git emails; diagnostic, expected ~0 after the
    no-call rule) and the span 07-06 -> 09-04. Repos are keyed by `slug` (mirrors merged)."""
    import memeplex as MP
    rep = {}
    w = MP.clean_commits(C.GOAL, rep)
    w = in_days(w)
    rep["in_span"] = w.height
    chat_h = chat_email_hashes(sorted(w["repo"].unique().to_list()))
    n0 = w.height
    w = w.filter(~pl.col("hash").is_in(list(chat_h)))
    rep["drop_chat_email"] = n0 - w.height
    rep["kept_h147"] = w.height
    w = C.assign_bins(w.sort("t"))
    w = w.with_columns(pl.col("pt_date").map_elements(C.window_of, return_dtype=pl.String).alias("window"))
    log("commits:", rep)
    out = w.select("slug", "repo", "hash", "t", "pt_date", "window", "bin", "k", pl.col("author_agent").alias("agent"),
                   "n_files")
    out.write_parquet(C.OUT / "commits_clean.parquet", compression="zstd")
    tot = out.group_by("window", "slug").len().rename({"len": "n_repo"})
    own = (out.group_by("window", "agent", "slug").len().join(tot, on=["window", "slug"])
           .with_columns((pl.col("len") / pl.col("n_repo")).alias("share"))
           .with_columns((pl.col("share") >= 0.5).alias("own"))
           .rename({"len": "n"}))
    own.write_parquet(C.OUT / "own_repos.parquet")
    return out, own, rep


# ------------------------------------------------------------------------------------------------ statements
def role_rows() -> pl.DataFrame:
    """agent_goal rows of #51 with validity (UTC bounds from valid_from / valid_to PT dates; Opus 5's overwritten
    game-dev role 07-24 18:51 -> 07-29 16:50 UTC uses the identical game-dev text of Opus 4.7, agent 24)."""
    g = pl.read_parquet(C.ED / "goals.parquet").filter((pl.col("goal_no") == C.GOAL)
                                                       & (pl.col("kind").cast(pl.String) == "agent_goal"))
    g = g.filter(~pl.col("holdout")).select("gid", "agent", "valid_from", "valid_to")
    rows = []
    for r in g.iter_rows(named=True):
        lo = dt.datetime.fromisoformat(r["valid_from"]).replace(tzinfo=C.UTC)
        hi = (dt.datetime.fromisoformat(r["valid_to"]).replace(tzinfo=C.UTC) + dt.timedelta(days=1, hours=8)
              if r["valid_to"] else dt.datetime(2100, 1, 1, tzinfo=C.UTC))
        if r["agent"] == 40:
            lo = dt.datetime(2026, 7, 29, 16, 50, 1, tzinfo=C.UTC)
        rows.append((r["agent"], r["gid"], lo, hi))
    gd = g.filter(pl.col("agent") == 24)["gid"].to_list()
    rows.append((40, gd[0], dt.datetime(2026, 7, 24, 18, 51, 52, tzinfo=C.UTC),
                 dt.datetime(2026, 7, 29, 16, 50, 1, tzinfo=C.UTC)))
    return pl.DataFrame(rows, schema={"agent": pl.Int8, "gid": pl.Int32, "lo": pl.Datetime("us", "UTC"),
                                      "hi": pl.Datetime("us", "UTC")}, orient="row")


def build_statements():
    st = pl.read_parquet(C.ED / "statements.parquet").with_row_index("srow")
    st = in_days(st.filter((pl.col("goal_no") == C.GOAL) & ~pl.col("holdout") & (pl.col("agent") != C.CLAUDE_CODE)))
    st = C.assign_bins(st)
    rr = role_rows()
    # latest valid role row per statement (agent 42 has two rows on 09-01: the later valid_from wins via sort)
    j = st.select("srow", "agent", "t").join(rr, on="agent", how="left").filter(
        (pl.col("t") >= pl.col("lo")) & (pl.col("t") < pl.col("hi"))).sort("lo").group_by("srow").last()
    st = st.join(j.select("srow", "gid"), on="srow", how="left")
    srow = st["srow"].to_numpy()
    has = st["gid"].is_not_null().to_numpy()
    cols = {}
    full = pl.read_parquet(C.ED / "statements.parquet", columns=["kind", "src_row"])
    for model in ("bge_small", "gte_modernbert"):
        W = EM.load_whitener("III", 32, model)
        G = EM.goal_vectors(model).astype(np.float32)
        Gw = W(G)
        Gw /= np.linalg.norm(Gw, axis=1, keepdims=True)
        E = EM.statement_embeddings(model, full[srow], mmap=True)
        Z = W(E)
        Z /= np.linalg.norm(Z, axis=1, keepdims=True)
        SR = EM.statement_vectors(model, "style_resid_period32")[srow].astype(np.float32)
        SR /= np.maximum(np.linalg.norm(SR, axis=1, keepdims=True), 1e-9)
        a = np.full(len(srow), np.nan, np.float32)
        b = np.full(len(srow), np.nan, np.float32)
        gi = st["gid"].fill_null(0).to_numpy().astype(int)
        a[has] = np.einsum("ij,ij->i", Z[has], Gw[gi[has]])
        b[has] = np.einsum("ij,ij->i", SR[has], Gw[gi[has]])
        tag = "bge" if model == "bge_small" else "gte"
        cols[f"align_{tag}"] = a.astype(np.float16)
        cols[f"align_sr_{tag}"] = b.astype(np.float16)
        log(f"alignment {model}: n {has.sum()} mean {np.nanmean(a):.3f} sd {np.nanstd(a):.3f}")
    out = st.select("srow", "kind", "agent", "t", "pt_date", "bin", "k", "room", "gid").with_columns(
        *[pl.Series(k, v) for k, v in cols.items()])
    out.write_parquet(C.OUT / "stmt_align.parquet", compression="zstd")
    return out


# ------------------------------------------------------------------------------------------------ panel
def build_panel(commits: pl.DataFrame, own: pl.DataFrame, stm: pl.DataFrame) -> pl.DataFrame:
    lt = (pl.scan_parquet(S / "context_ledger_turns.parquet").filter(pl.col("goal_no") == C.GOAL)
          .select("agent", "pt_date", "t_call", "kind").collect())
    lt = in_days(lt).filter(pl.col("agent") != C.CLAUDE_CODE).rename({"t_call": "t"})
    lt = C.assign_bins(lt)
    calls = lt.group_by("agent", "bin").agg(pl.len().alias("n_calls"),
                                            (~pl.col("kind").cast(pl.String).is_in(["pause", "wait", "session_start",
                                                                                    "session_stop"])).sum()
                                            .alias("n_work_calls"))
    cc = (pl.scan_parquet(S / "chat_core.parquet").filter((pl.col("goal_no") == C.GOAL)
                                                         & (pl.col("speaker_kind").cast(pl.String) == "agent"))
          .select("agent", "t", "pt_date").collect())
    cc = C.assign_bins(in_days(cc).filter(pl.col("agent") != C.CLAUDE_CODE))
    chat = cc.group_by("agent", "bin").agg(pl.len().alias("n_chat"))
    tot = cc.group_by("bin").agg(pl.len().alias("n_chat_all"))
    stc = stm.group_by("agent", "bin").agg(
        pl.len().alias("n_stmt"),
        *[pl.col(c).cast(pl.Float32).fill_nan(None).mean().alias(c)
          for c in ("align_bge", "align_gte", "align_sr_bge", "align_sr_gte")],
        pl.col("align_bge").cast(pl.Float32).is_not_nan().sum().alias("n_align"))
    ownset = own.filter(pl.col("own")).select("window", "agent", "slug").with_columns(pl.lit(True).alias("_own"))
    kept = commits.join(ownset, on=["window", "agent", "slug"], how="left")
    com = kept.group_by("agent", "bin").agg(pl.len().alias("commits_all"),
                                            pl.col("_own").fill_null(False).sum().alias("commits_own"))
    b = C.bins()
    mb = C.mbins()
    agents = list(mb.agents)
    grid = b.join(pl.DataFrame({"agent": agents}, schema={"agent": pl.Int8}), how="cross")
    p = (grid.join(calls, on=["agent", "bin"], how="left").join(chat, on=["agent", "bin"], how="left")
         .join(tot, on="bin", how="left").join(stc, on=["agent", "bin"], how="left")
         .join(com, on=["agent", "bin"], how="left"))
    cnt_cols = ("n_calls", "n_work_calls", "n_chat", "n_chat_all", "n_stmt", "n_align", "commits_all", "commits_own")
    p = p.with_columns(*[pl.col(c).fill_null(0) for c in cnt_cols])
    # presence: H145's DQ8 per-agent trim (first-to-last non-pause call span covers >= half the bin)
    pres = pl.DataFrame({"agent": np.repeat(np.asarray(agents), mb.nB).astype(np.int8),
                         "bin": np.tile(np.arange(mb.nB), len(agents)).astype(np.int32),
                         "present": mb.present.ravel()})
    p = p.join(pres, on=["agent", "bin"], how="left").with_columns(pl.col("present").fill_null(False))
    p = p.with_columns((pl.col("n_chat") / pl.col("n_chat_all")).fill_nan(None).alias("talk_share"))
    p = p.with_columns(*[pl.col(c).cast(pl.Int16) for c in cnt_cols])
    p.write_parquet(C.OUT / "panel.parquet", compression="zstd")
    log("panel:", p.height, "agent-bins;", int(p["present"].sum()), "present;", len(agents), "agents")
    return p


# ------------------------------------------------------------------------------------------------ F / P events
def build_events(commits: pl.DataFrame, own: pl.DataFrame, stm: pl.DataFrame) -> pl.DataFrame:
    c = (pl.scan_parquet(S / "calls.parquet").filter(pl.col("goal_no") == C.GOAL)
         .select("turn_id", "agent", "pt_date", "t_call", "kind", "reset_forced", "n_work", "seq", "seg", "pos",
                 "seg_len", "holdout").collect())
    c = in_days(c).filter(~pl.col("holdout") & (pl.col("agent") != C.CLAUDE_CODE)).sort("agent", "pt_date", "seq")
    c = c.with_columns(pl.int_range(pl.len()).over("agent", "pt_date").alias("i"),
                       pl.len().over("agent", "pt_date").alias("day_len"))
    # statements and own-repo commits per call: map each statement / commit to the agent's latest call at or before it
    ownset = own.filter(pl.col("own")).select("window", "agent", "slug").with_columns(pl.lit(True).alias("_own"))
    kept = commits.join(ownset, on=["window", "agent", "slug"], how="left").with_columns(pl.col("_own").fill_null(False))
    cs = c.select("agent", "pt_date", "t_call", "i").sort("t_call")

    def per_call(df: pl.DataFrame, val: str | None) -> pl.DataFrame:
        d = df.select("agent", "pt_date", "t", *( [val] if val else [])).sort("t")
        m = d.join_asof(cs, left_on="t", right_on="t_call", by=["agent", "pt_date"], strategy="backward")
        m = m.filter(pl.col("i").is_not_null())
        return m.group_by("agent", "pt_date", "i").agg(
            (pl.col(val).sum() if val else pl.len()).alias("v"))

    stc = per_call(stm, None).rename({"v": "stmt"})
    owc = per_call(kept.rename({"_own": "own"}), "own").rename({"v": "own"})
    c = (c.join(stc, on=["agent", "pt_date", "i"], how="left").join(owc, on=["agent", "pt_date", "i"], how="left")
         .with_columns(pl.col("stmt").fill_null(0), pl.col("own").fill_null(0)))
    ev = c.filter(pl.col("reset_forced") | ((pl.col("pos") - 1 == 20) & (pl.col("seg_len") >= 40)))
    ev = ev.with_columns(pl.when(pl.col("reset_forced")).then(pl.lit("F")).otherwise(pl.lit("P")).alias("etype"))
    # windows of 20 calls after (event call + 19) and before (-20..-1) within the agent-day
    out = []
    arr = {k: c[k].to_numpy() for k in ("n_work", "stmt", "own")}
    pos_in = c["i"].to_numpy()
    g0 = np.arange(c.height) - pos_in
    glen = c["day_len"].to_numpy()
    cum = {k: np.r_[0, np.cumsum(v)] for k, v in arr.items()}
    idx = np.flatnonzero((c["reset_forced"].to_numpy()) | ((c["pos"].to_numpy() - 1 == 20) & (c["seg_len"].to_numpy() >= 40)))
    lo_post, hi_post = idx, np.minimum(idx + 20, g0[idx] + glen[idx])
    lo_pre, hi_pre = np.maximum(idx - 20, g0[idx]), idx
    for k in arr:
        out.append((f"{k}_post20", cum[k][hi_post] - cum[k][lo_post]))
        out.append((f"{k}_pre20", cum[k][hi_pre] - cum[k][lo_pre]))
    tc = c["t_call"].dt.epoch("us").to_numpy()
    last = g0[idx] + glen[idx] - 1
    # window bounds (UTC us): pre = [t_call(e-20), t_call(e)), post = [t_call(e), t_call(e+20)) (or last call + 60 s)
    t_post_end = np.where(hi_post <= last, tc[np.minimum(hi_post, len(tc) - 1)], tc[last] + 60 * 10**6)
    t_pre_start = tc[lo_pre]
    out.append(("n_post20", hi_post - lo_post))
    out.append(("n_pre20", hi_pre - lo_pre))
    ev = c[idx].with_columns(pl.when(pl.col("reset_forced")).then(pl.lit("F")).otherwise(pl.lit("P")).alias("etype"),
                             *[pl.Series(n, v.astype(np.int32)) for n, v in out],
                             pl.Series("day_pos", pos_in[idx].astype(np.int32)),
                             pl.Series("t_post_end", t_post_end.astype(np.int64)),
                             pl.Series("t_pre_start", t_pre_start.astype(np.int64)))
    ev = C.assign_bins(ev.rename({"t_call": "t"}))
    ev = ev.join(C.days().select("pt_date", "unit_id", "window"), on="pt_date", how="left")
    # 2-h statement windows (event-centred; truncated at the day window)
    st_t = stm.select("agent", "t").sort("agent", "t")
    ag = st_t["agent"].to_numpy()
    tt = st_t["t"].dt.epoch("us").to_numpy()
    e_ag = ev["agent"].to_numpy()
    e_t = ev["t"].dt.epoch("us").to_numpy()
    H = 2 * 3600 * 10**6
    post = np.zeros(len(ev), np.int32)
    pre = np.zeros(len(ev), np.int32)
    for a in np.unique(e_ag):
        m = ag == a
        ta = tt[m]
        me = e_ag == a
        post[me] = np.searchsorted(ta, e_t[me] + H, "right") - np.searchsorted(ta, e_t[me], "right")
        pre[me] = np.searchsorted(ta, e_t[me], "left") - np.searchsorted(ta, e_t[me] - H, "left")
    ev = ev.with_columns(pl.Series("stmt_post2h", post), pl.Series("stmt_pre2h", pre),
                         (pl.col("agent").cast(pl.String) + "|" + pl.col("unit_id")).alias("stratum"),
                         (pl.col("agent").cast(pl.String) + "|" + pl.col("pt_date")).alias("cluster"))
    ev = ev.select("etype", "turn_id", "agent", "pt_date", "t", "bin", "k", "unit_id", "window", "seg", "pos", "seg_len",
                   "day_pos", "day_len", "stratum", "cluster", "n_work_post20", "n_work_pre20", "stmt_post20",
                   "stmt_pre20", "own_post20", "own_pre20", "n_post20", "n_pre20", "stmt_post2h", "stmt_pre2h",
                   "t_pre_start", "t_post_end")
    ev.write_parquet(C.OUT / "events_fp.parquet", compression="zstd")
    log("events:", dict(zip(*ev["etype"].value_counts().sort("etype").to_dict(as_series=False).values())))
    return ev


# ------------------------------------------------------------------------------------------------ dated events
EVENTS = [
    # id, kind, agent (code), label, t_start (UTC), t_end (UTC, None = point event), note
    ("HL1", "hub_loss", 40, "NE38: Claude Opus 5 reassigned (game dev -> mathematician)", "2026-07-29T16:50:01",
     None, "operator message (kicks_classified human_message, target 40)"),
    ("HL2", "hub_loss", 6, "Gemini 2.5 Pro tool losses, week W3 (08-10 -> 08-14 PT)", "2026-08-10T16:00:00",
     "2026-08-15T00:10:00", "story part 2 (W3: 0 commits by Gemini); window event, before = W2 (same active length)"),
    ("HL3", "hub_loss", 6, "Gemini 2.5 Pro bash broken (09-02 afternoon -> fixed 09-04 17:14 UTC)", "2026-09-02T20:00:00",
     "2026-09-04T17:14:37", "story part 3; fix = human message 09-04 17:14:37 UTC (kicks_classified)"),
    ("HL4", "hub_loss", 33, "DeepSeek-V4-Pro tool loss (09-02 -> 09-04, card dates)", "2026-09-02T16:00:00",
     "2026-09-05T00:10:00", "card; story part 3 dates the bash failure to 09-03 (variant HL4b)"),
    ("HL4b", "hub_loss", 33, "DeepSeek-V4-Pro tool loss, story date (09-03 -> 09-04)", "2026-09-03T16:00:00",
     "2026-09-05T00:10:00", "variant of HL4 (story part 3)"),
    ("OP1", "operator", 17, "08-05 rebuke of DeepSeek-V3.2's flooding", "2026-08-05T16:38:53", None,
     "kicks_classified human_message target 17; same day: bookends stop, #focus opens (16:36)"),
    ("OP2", "operator", 17, "08-24 withdrawal of approval for DeepSeek-V3.2's outreach", "2026-08-24T17:59:01", None,
     "kicks_classified human_message target 17 (reminder 19:07:46)"),
    ("OP3", "operator", None, "08-20 nudger stop and pause shares (NE43 step 2)", "2026-08-20T16:45:33",
     "2026-08-20T17:51:20", "operator in #general 16:45 -> 17:51 UTC; last nudge 17:42:38; point event with a gap: "
     "before ends at 16:45:33, after starts at 17:51:20 (the switch-off)"),
]
PLACEBO_GAP_DAYS = 3
SPAN_ACTIVE_DAYS = 2.0        # before / after windows of point events, in active days (one active day = mean window)


def build_scramble_events():
    d = C.days()
    day_s = float(d["win_s"].mean())
    evs = []
    for eid, kind, agent, label, t0, t1, note in EVENTS:
        a0 = float(C.active_time(np.array([int(C.ts(t0).timestamp() * 1e6)]))[0])
        if t1 is None or eid == "OP3":
            L = SPAN_ACTIVE_DAYS * day_s
            a_after = a0 if t1 is None else float(C.active_time(np.array([int(C.ts(t1).timestamp() * 1e6)]))[0])
            a1 = a_after + L
        else:
            a_after = a0
            a1 = float(C.active_time(np.array([int(C.ts(t1).timestamp() * 1e6)]))[0])
            L = a1 - a0
        evs.append({"id": eid, "kind": kind, "agent": agent, "label": label, "t_start": t0, "t_end": t1,
                    "a_start": a0, "a_after": a_after, "a_end": a1, "a_before": a0 - L, "len_active_s": L,
                    "gap_s": a_after - a0, "note": note, "start_date": t0[:10]})
    a_max = float(d["a0"].max() + d["win_s"].to_numpy()[-1])
    ev_days = set()
    for e in evs:
        if e["id"] in ("HL4b",):
            continue
        s = dt.date.fromisoformat(e["start_date"])
        last = dt.date.fromisoformat((e["t_end"] or e["t_start"])[:10])
        while s <= last:
            ev_days.add(s)
            s += dt.timedelta(days=1)
    rows = []
    for e in evs:
        ed = dt.date.fromisoformat(e["start_date"])
        tod = C.ts(e["t_start"]) - d.filter(pl.col("pt_date") == e["start_date"])["win_start"][0]
        for r in d.iter_rows(named=True):
            pdd = dt.date.fromisoformat(r["pt_date"])
            if pdd == ed:
                continue
            gap = min(abs((pdd - x).days) for x in ev_days)
            t0p = r["win_start"] + tod
            a0 = float(C.active_time(np.array([int(t0p.timestamp() * 1e6)]))[0])
            fits = (a0 - e["len_active_s"] >= 0) and (a0 + e["gap_s"] + e["len_active_s"] <= a_max)
            if gap < PLACEBO_GAP_DAYS or not fits:
                continue
            rows.append({"id": e["id"], "placebo_date": r["pt_date"], "same_weekday": r["weekday"] == ed.isoweekday(),
                         "a_start": a0, "a_after": a0 + e["gap_s"], "a_end": a0 + e["gap_s"] + e["len_active_s"],
                         "a_before": a0 - e["len_active_s"],
                         "gap_days": gap})
    pdays = pl.DataFrame(rows)
    (C.OUT / "scramble_events.json").write_text(json.dumps(
        {"events": evs, "placebo_rule": f"same weekday as the event start (variant: any weekday); >= {PLACEBO_GAP_DAYS} "
                                        "calendar days from every event day; same time of day; windows inside #51 "
                                        "non-reserved active time", "event_days": sorted(str(x) for x in ev_days),
         "span_active_days_point_events": SPAN_ACTIVE_DAYS, "active_day_s": day_s}, indent=1))
    pdays.write_parquet(C.OUT / "placebo_days.parquet")
    log("placebo days (same weekday):", pdays.filter(pl.col("same_weekday")).group_by("id").len().sort("id").rows())
    return evs, pdays


def main():
    C.OUT.mkdir(parents=True, exist_ok=True)
    commits, own, ccounts = build_commits()
    stm = build_statements()
    panel = build_panel(commits, own, stm)
    ev = build_events(commits, own, stm)
    evs, pdays = build_scramble_events()
    C.provenance("scheme", "hypotheses/H147-egregore-value-and-hosts-51/scheme/build.py",
                 ["work_commits (memeplex.clean_commits, 4f6ab2e)", "project_calls", "project_call_touches", "roster", "calendar", "period_units", "call_windows (DQ8 presence)",
                  "embeddings/statements", "embeddings/goals", "goal_vectors (bge, gte)", "chat/intentions embeddings",
                  "statements_style_resid_period32 (bge, gte)", "context_ledger_turns", "chat_core", "calls",
                  "kicks_classified (event times)", "raw git emails of the bare clones (-chat filter)"],
                 params={"bin_s": C.BIN_S, "span": [C.FIRST, C.LAST], "own_share": 0.5, "P_rule": "pos0 == 20 & seg_len >= 40",
                         "placebo_gap_days": PLACEBO_GAP_DAYS},
                 extra={"commit_cleaning": ccounts,
                        "n_events": ev["etype"].value_counts().rows(), "panel_rows": panel.height,
                        "reserved": "51m masked (holdout_mask); asserted absent"})
    log("done")


if __name__ == "__main__":
    main()
