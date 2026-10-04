"""H58 scheme: allocation panels, coordination layers and erasure features for coordinated superagents.

Card: hypotheses/H58-coordinated-superagents/README.md, "Formal setup" F1-F9. Builds
data/processed/H58-coordinated-superagents/ from the shared tables, non-holdout days only (asserted on every table):

  units.json         H01 round-2 units of analysis (19), with days, regime, window starts
  commits.parquet    DQ4 agent work commits: unit, day (index), m (minutes since the day's window start), agent, repo
                     (int id; repos.parquet), hash (for the file-level native test), bulk
  repos.parquet      repo id -> canonical name (work_commits.repo)
  presence.parquet   model calls per agent x day x 5-min slot (call_windows.t_call)
  exog.parquet       nudges, human messages, goal kickoffs (kicks_classified): unit, day, m, kind
  content.parquet    content cluster (k-means k=6 per regime, style_resid_period bge win30 vectors) per agent x day x win30
  rooms.parquet      room of each agent at each 30-min bin midpoint (rooms_timeline)
  layers.parquet     per unit and agent pair: synchrony, co-adoption, reply, co-artifact weights (card F7)
  erasures.parquet   regime III: forced / voluntary context erasures and placebo calls with re-acquisition features (F9)
  files40.parquet    #40 shared-repo commits -> file groups (read-only git log on the bare clone; native test N1)
No message text is read or stored. Run: uv run python hypotheses/H58-coordinated-superagents/scheme/build.py
"""
from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import sys
import time
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "POLARS_MAX_THREADS",
           "NUMEXPR_NUM_THREADS"):
    os.environ[_v] = "2"

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H58-coordinated-superagents"
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import holdout_mask, git_commit  # noqa: E402

REVISION = "838b4150303ca8228e8edb432d8b8ccae353d258"
CLAUDE_CODE = 19
TZ = "America/Los_Angeles"
WORK_BEHAVIORS = ["execute_task", "debug_recover", "verify_report"]
WRITE_VERBS = ["git push", "git commit", "deploy", "gh pr create", "gh pr merge", "gh repo create", "glab mr create",
               "glab mr merge", "glab repo create", "glab project create"]
# H01 round-2 units: goal periods split at catalogued steps (#36 at 03-24; #38 at 04-14, 04-20; #51 at 07-09, 08-05,
# 08-25, 09-03); 36a (one day) is not eligible. Days come from the calendar (non-holdout only).
UNIT_SPEC = [("30", 30, None, None), ("31", 31, None, None), ("33", 33, None, None), ("35", 35, None, None),
             ("36b", 36, "2026-03-24", None), ("37", 37, None, None), ("38a", 38, None, "2026-04-14"),
             ("38b", 38, "2026-04-14", "2026-04-20"), ("38c", 38, "2026-04-20", None), ("39", 39, None, None),
             ("40", 40, None, None), ("41", 41, None, None), ("42", 42, None, None), ("44", 44, None, None),
             ("51a", 51, None, "2026-07-09"), ("51b", 51, "2026-07-09", "2026-08-05"),
             ("51c", 51, "2026-08-05", "2026-08-25"), ("51d", 51, "2026-08-25", "2026-09-03"),
             ("51e", 51, "2026-09-03", None)]


INCLUDE_HOLDOUT = False   # set only by analysis/confirm.py behind its two flags (confirmatory panels)


def _nh():
    """Row filter: non-holdout rows (exploration); all rows only for the confirmatory build."""
    return pl.lit(True) if INCLUDE_HOLDOUT else ~pl.col("holdout")


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def guard(df: pl.DataFrame, name: str, date_col="pt_date", goal_col="goal_no"):
    if df.height == 0:
        return df
    if goal_col in df.columns:
        m = holdout_mask(df[date_col].to_list(), df[goal_col].to_list())
    else:
        cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "goal_no"])
        g = df.select(date_col).join(cal, left_on=date_col, right_on="pt_date", how="left")
        m = holdout_mask(g[date_col].to_list(), g["goal_no"].to_list())
    assert not any(m), f"holdout rows in {name}"
    return df


def units():
    cal = pl.read_parquet(SH / "calendar.parquet").filter(_nh()).sort("pt_date")
    out = []
    for (u, g, lo, hi) in UNIT_SPEC:
        c = cal.filter(pl.col("goal_no") == g)
        if lo:
            c = c.filter(pl.col("pt_date") >= lo)
        if hi:
            c = c.filter(pl.col("pt_date") < hi)
        days = c["pt_date"].to_list()
        assert not any(holdout_mask(days, [g] * len(days)))
        out.append({"unit": u, "goal_no": g, "regime": str(c["regime"][0]), "days": days, "n_days": len(days),
                    "win_start": [t.isoformat() for t in c["win_start"].to_list()],
                    "win_end": [t.isoformat() for t in c["win_end"].to_list()]})
    # check against H01 round 2 (read-only)
    h01 = ROOT / "data/processed/H01-emergent-superagents-exist/round2/units.json"
    if h01.exists():
        ref = {x["unit"]: x["days"] for x in json.loads(h01.read_text()) if x.get("eligible")}
        for x in out:
            assert ref.get(x["unit"]) == x["days"], f"unit {x['unit']} differs from H01 round 2"
    return out


def day_frame(U):
    rows = []
    for x in U:
        for d, (day, ws, we) in enumerate(zip(x["days"], x["win_start"], x["win_end"])):
            rows.append({"unit": x["unit"], "goal_no": x["goal_no"], "day": d, "pt_date": day,
                         "win_start": dt.datetime.fromisoformat(ws), "win_end": dt.datetime.fromisoformat(we)})
    return pl.DataFrame(rows).with_columns(pl.col("day").cast(pl.Int16), pl.col("goal_no").cast(pl.Int8))


def with_m(df: pl.DataFrame, days: pl.DataFrame, tcol="t"):
    """Attach unit, day and minutes since the day's window start (rows outside the window are dropped)."""
    df = df.join(days.select("unit", "day", "pt_date", "win_start", "win_end"), on="pt_date", how="inner")
    df = df.filter((pl.col(tcol) >= pl.col("win_start")) & (pl.col(tcol) < pl.col("win_end")))
    return df.with_columns(((pl.col(tcol) - pl.col("win_start")).dt.total_microseconds() / 6e7).cast(pl.Float32)
                           .alias("m")).drop("win_start", "win_end")


def build_commits(days):
    w = pl.read_parquet(SH / "work_commits.parquet",
                        columns=["repo", "hash", "t", "pt_date", "goal_no", "holdout", "author_agent", "author_kind",
                                 "automated", "canonical", "imported", "bulk"])
    w = w.filter(pl.col("canonical") & ~pl.col("imported") & (pl.col("author_kind") == "agent") & ~pl.col("automated")
                 & _nh() & pl.col("pt_date").is_in(days["pt_date"].to_list())
                 & (pl.col("author_agent") != CLAUDE_CODE))
    w = w.with_columns(pl.col("repo").cast(pl.Utf8))
    repos = w.select("repo").unique().sort("repo").with_row_index("repo_id").with_columns(pl.col("repo_id").cast(pl.Int32))
    w = w.join(repos, on="repo").rename({"author_agent": "agent"})
    w = guard(w, "commits")
    w = with_m(w, days)
    return w.select("unit", "day", "pt_date", "m", "agent", "repo_id", "hash", "bulk", "t").sort("unit", "day", "m"), repos


def build_presence(days):
    c = pl.scan_parquet(SH / "call_windows.parquet").filter(_nh()).select("agent", "pt_date", "t_call") \
        .filter(pl.col("pt_date").is_in(days["pt_date"].to_list())).collect()
    c = with_m(c, days, "t_call").filter(pl.col("agent") != CLAUDE_CODE)
    c = c.with_columns((pl.col("m") // 5).cast(pl.Int16).alias("slot5"))
    return guard(c.group_by("unit", "day", "pt_date", "agent", "slot5").agg(pl.len().alias("n_calls")).sort(
        "unit", "day", "agent", "slot5"), "presence")


def build_exog(days):
    k = pl.read_parquet(SH / "kicks_classified.parquet", columns=["t", "kind", "pt_date", "holdout"])
    k = k.filter(_nh() & pl.col("kind").is_in(["nudge", "human_message", "goal_kickoff"]))
    k = with_m(k, days)
    return guard(k.select("unit", "day", "pt_date", "m", "kind"), "exog")


def build_content(days, U):
    """k-means (k=6) per regime on the style-residualized (per goal period) bge win30 vectors of non-holdout windows."""
    idx = pl.read_parquet(SH / "embeddings/agent_win30.parquet").with_row_index("row")
    V = np.load(SH / "embeddings/agent_win30_style_resid_period_bge_small.npy", mmap_mode="r")
    idx = idx.filter(_nh())
    out = []
    rng = np.random.default_rng(58)
    for reg in ("I", "II", "III"):
        sub = idx.filter(pl.col("regime") == reg)
        X = np.asarray(V[sub["row"].to_numpy()], dtype=np.float64)
        ok = np.isfinite(X).all(1) & (np.linalg.norm(X, axis=1) > 0)
        sub, X = sub.filter(pl.Series(ok)), X[ok]
        X = X / np.linalg.norm(X, axis=1, keepdims=True)
        lab = kmeans(X, 6, rng)
        out.append(sub.with_columns(pl.Series("cluster", lab.astype(np.int8))))
    c = pl.concat(out).select("agent", "pt_date", "win30", "cluster", "n_chat", "n_intent")
    c = c.join(days.select("unit", "day", "pt_date"), on="pt_date", how="inner")
    return guard(c.select("unit", "day", "pt_date", "agent", "win30", "cluster", "n_chat", "n_intent"), "content")


def kmeans(X, k, rng, n_init=5, iters=60):
    best, best_in = None, np.inf
    for _ in range(n_init):
        C = X[rng.choice(len(X), k, replace=False)]
        for _ in range(iters):
            d = ((X[:, None, :] - C[None]) ** 2).sum(-1) if len(X) < 20000 else _dist_chunk(X, C)
            lab = d.argmin(1)
            C2 = np.stack([X[lab == j].mean(0) if (lab == j).any() else C[j] for j in range(k)])
            if np.allclose(C2, C):
                break
            C = C2
        d = _dist_chunk(X, C)
        inertia = d.min(1).sum()
        if inertia < best_in:
            best_in, best = inertia, d.argmin(1)
    return best


def _dist_chunk(X, C, ch=20000):
    out = np.empty((len(X), len(C)))
    for s in range(0, len(X), ch):
        Y = X[s:s + ch]
        out[s:s + ch] = (Y ** 2).sum(1)[:, None] - 2 * Y @ C.T + (C ** 2).sum(1)[None]
    return out


def build_rooms(days):
    rt = pl.read_parquet(SH / "rooms_timeline.parquet")
    rows = []
    for (u, d, day, ws, we) in days.select("unit", "day", "pt_date", "win_start", "win_end").iter_rows():
        nb = int(np.ceil((we - ws).total_seconds() / 1800))
        mids = [ws + dt.timedelta(minutes=30 * b + 15) for b in range(nb)]
        for (a, room, t0, t1) in rt.select("agent", "room", "t_start", pl.col("t_end").fill_null(pl.col("t_last"))).iter_rows():
            for b, tm in enumerate(mids):
                if t0 <= tm < (t1 or dt.datetime.max.replace(tzinfo=dt.timezone.utc)):
                    rows.append((u, d, day, a, b, room))
    r = pl.DataFrame(rows, schema=["unit", "day", "pt_date", "agent", "bin30", "room"], orient="row")
    return guard(r.unique(["unit", "day", "agent", "bin30"], keep="last"), "rooms")


def build_layers(days, commits, U):
    """Card F7: four coordination layers per unit and agent pair."""
    unit_days = {x["unit"]: x["days"] for x in U}
    # --- synchrony: behavior_states_v3 5-min working indicators, cross-agent mean removed, pairwise in-span slots
    bs = pl.scan_parquet(SH / "behavior_states_v3.parquet").filter(_nh()) \
        .select("pt_date", "agent", "w", "behavior", "in_span", "active").collect()
    bs = bs.filter(pl.col("agent") != CLAUDE_CODE)
    bs = bs.with_columns(pl.col("behavior").cast(pl.Utf8).is_in(WORK_BEHAVIORS).fill_null(False).alias("work"))
    # --- co-adoption: H34 idea markers (read-only)
    chat = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "pt_date", "speaker_kind", "agent"]) \
        .sort("t").with_row_index("msg")
    uses = pl.read_parquet(ROOT / "data/processed/H34-idea-cascades/markers/uses.parquet")
    uses = uses.join(chat.select(pl.col("msg").cast(pl.UInt32), "pt_date", "speaker_kind", "agent"), on="msg", how="inner") \
        .filter((pl.col("speaker_kind") == "agent") & (pl.col("agent") != CLAUDE_CODE))
    # --- reply threads (DQ2): candidate pairs only
    rp = pl.read_parquet(SH / "reply_pairs.parquet", columns=["pair_set", "b_agent", "a_kind", "a_agent", "pt_date",
                                                               "holdout", "p_reply"])
    rp = rp.filter((pl.col("pair_set").cast(pl.Utf8) == "cand") & _nh() & pl.col("a_agent").is_not_null()
                   & pl.col("p_reply").is_not_null())
    nmsg = chat.filter(pl.col("speaker_kind") == "agent").group_by("pt_date", "agent").agg(pl.len().alias("n"))
    rows = []
    for x in U:
        u, dl = x["unit"], x["days"]
        cm = commits.filter(pl.col("unit") == u)
        agents = sorted(cm["agent"].unique().to_list())
        n = len(agents)
        pos = {a: i for i, a in enumerate(agents)}
        W = {k: np.zeros((n, n)) for k in ("sync", "coad", "reply", "coart")}
        # sync
        b = bs.filter(pl.col("pt_date").is_in(dl) & pl.col("agent").is_in(agents))
        acc_xy = np.zeros((n, n)); acc_xx = np.zeros((n, n)); acc_yy = np.zeros((n, n)); acc_n = np.zeros((n, n))
        for day in dl:
            bd = b.filter(pl.col("pt_date") == day)
            if bd.height == 0:
                continue
            nw = int(bd["w"].max()) + 1
            M = np.zeros((n, nw))
            S = np.zeros((n, nw), bool)
            for (a, w, wk, sp) in bd.select("agent", "w", "work", "in_span").iter_rows():
                M[pos[a], w] = float(wk)
                S[pos[a], w] = bool(sp)
            cnt = S.sum(0)
            mean = np.where(cnt > 0, (M * S).sum(0) / np.maximum(cnt, 1), 0.0)
            R = (M - mean[None]) * S
            Sf = S.astype(float)
            acc_xy += R @ R.T
            acc_xx += (R ** 2) @ Sf.T
            acc_yy += Sf @ (R ** 2).T
            acc_n += Sf @ Sf.T
        with np.errstate(invalid="ignore", divide="ignore"):
            C = acc_xy / np.sqrt(acc_xx * acc_yy)
        C[~np.isfinite(C) | (acc_n < 24)] = 0.0
        np.fill_diagonal(C, 0)
        W["sync"] = np.clip(C, 0, None)
        # co-adoption
        us = uses.filter(pl.col("pt_date").is_in(dl) & pl.col("agent").is_in(agents)).unique(["marker", "agent"])
        cnt_m = us.group_by("marker").agg(pl.len().alias("k"))
        us = us.join(cnt_m, on="marker").filter((pl.col("k") >= 2) & (pl.col("k") <= max(2, n // 2)))
        nm = np.zeros(n)
        for (a, ln) in us.group_by("agent").agg(pl.len()).iter_rows():
            nm[pos[a]] = ln
        for grp in us.group_by("marker").agg(pl.col("agent")).iter_rows():
            ids = [pos[a] for a in grp[1]]
            for i in ids:
                for j in ids:
                    if i != j:
                        W["coad"][i, j] += 1
        with np.errstate(invalid="ignore", divide="ignore"):
            W["coad"] = np.nan_to_num(W["coad"] / np.sqrt(np.outer(nm, nm)))
        # reply
        r = rp.filter(pl.col("pt_date").is_in(dl) & pl.col("b_agent").is_in(agents) & pl.col("a_agent").is_in(agents)
                      & (pl.col("b_agent") != pl.col("a_agent")))
        for (bi, ai, s) in r.group_by("b_agent", "a_agent").agg(pl.col("p_reply").sum()).iter_rows():
            W["reply"][pos[bi], pos[ai]] += s
            W["reply"][pos[ai], pos[bi]] += s
        mm = np.zeros(n)
        for (a, s) in nmsg.filter(pl.col("pt_date").is_in(dl) & pl.col("agent").is_in(agents)).group_by("agent") \
                .agg(pl.col("n").sum()).iter_rows():
            mm[pos[a]] = s
        with np.errstate(invalid="ignore", divide="ignore"):
            W["reply"] = np.nan_to_num(W["reply"] / np.sqrt(np.outer(mm, mm)))
        # co-artifact: Jaccard of (repo, day) sets
        sets = {a: set() for a in agents}
        for (a, rid, d) in cm.select("agent", "repo_id", "day").unique().iter_rows():
            sets[a].add((rid, d))
        for i, a in enumerate(agents):
            for j, c in enumerate(agents):
                if i < j and (sets[a] or sets[c]):
                    jac = len(sets[a] & sets[c]) / len(sets[a] | sets[c])
                    W["coart"][i, j] = W["coart"][j, i] = jac
        for i in range(n):
            for j in range(i + 1, n):
                rows.append((u, agents[i], agents[j], *(float(W[k][i, j]) for k in ("sync", "coad", "reply", "coart"))))
    return pl.DataFrame(rows, schema=["unit", "i", "j", "w_sync", "w_coad", "w_reply", "w_coart"], orient="row")


def repo_of_artifact(repos: pl.DataFrame) -> pl.DataFrame:
    """artifact id -> repo id (work_repos.artifacts, plus files/sites through artifacts.parent)."""
    wr = pl.read_parquet(SH / "work_repos.parquet", columns=["repo", "artifacts"]).explode("artifacts") \
        .rename({"artifacts": "artifact"}).drop_nulls()
    wr = wr.join(repos, on="repo", how="inner").select("artifact", "repo_id")
    art = pl.read_parquet(SH / "artifacts.parquet", columns=["artifact", "kind", "parent"])
    child = art.filter(pl.col("parent").is_not_null()).join(wr.rename({"artifact": "parent"}), on="parent", how="inner") \
        .select("artifact", "repo_id")
    return pl.concat([wr, child]).unique("artifact")


def build_erasures(days, commits, repos, U):
    """Card F9: forced / voluntary erasures and placebo calls (regime III units) with re-acquisition features."""
    r3 = [x for x in U if x["regime"] == "III"]
    dl = [d for x in r3 for d in x["days"]]
    tu = pl.scan_parquet(SH / "context_ledger_turns.parquet").filter(_nh() & pl.col("pt_date").is_in(dl)) \
        .select("turn_id", "agent", "pt_date", "t_call", "ctx_mode", "reset_forced", "reset_consol", "reset_session",
                "first_of_day", "ctx_pos", "prev_seg_len").collect()
    tu = tu.filter((pl.col("ctx_mode").cast(pl.Utf8) != "summary") & (pl.col("agent") != CLAUDE_CODE)).sort("agent", "t_call")
    tu = with_m(tu, days, "t_call")
    a2r = repo_of_artifact(repos)
    am = pl.read_parquet(SH / "artifact_mentions.parquet", columns=["artifact", "t", "agent", "speaker_kind", "source",
                                                                     "how", "verb", "message_id", "ref_index"])
    am = am.filter(pl.col("speaker_kind") == "agent").join(a2r, on="artifact", how="inner")
    am = am.with_columns(pl.col("t").dt.convert_time_zone(TZ).dt.date().cast(pl.Utf8).alias("pt_date")) \
        .filter(pl.col("pt_date").is_in(dl))
    reads = am.filter((pl.col("source").cast(pl.Utf8) == "action")
                      & ~pl.col("verb").cast(pl.Utf8).fill_null("").is_in(WRITE_VERBS)).select("agent", "t", "repo_id")
    chat_named = am.filter(pl.col("source").cast(pl.Utf8) == "chat").select("message_id", "repo_id").unique()
    intents = pl.read_parquet(SH / "intentions.parquet").filter(pl.col("source").cast(pl.Utf8) == "CONSOLIDATE") \
        .select("event_index", "t", "agent").sort("agent", "t")
    int_named = am.filter(pl.col("source").cast(pl.Utf8) == "intention").select(pl.col("ref_index").alias("event_index"),
                                                                                  "repo_id").unique()
    int_rep = intents.join(int_named.group_by("event_index").agg(pl.col("repo_id").alias("int_repos")), on="event_index",
                           how="left")
    items = pl.scan_parquet(SH / "context_ledger_items.parquet").select("turn_id", "message_id", "sender", "kind").collect()
    items = items.join(tu.select("turn_id"), on="turn_id", how="semi")
    items = items.join(chat_named.group_by("message_id").agg(pl.col("repo_id").alias("named")), on="message_id", how="left")
    # events: forced and voluntary erasures = first receiving call after the consolidation; placebo = mid-segment calls
    ev = tu.with_columns(pl.when(pl.col("reset_forced")).then(pl.lit("forced"))
                         .when(pl.col("reset_consol")).then(pl.lit("voluntary"))
                         .when(pl.col("ctx_pos") == 20).then(pl.lit("placebo")).otherwise(None).alias("etype"))
    ev = ev.filter(pl.col("etype").is_not_null() & ~pl.col("first_of_day"))
    # placebo: mid-segment call (ctx_pos 20) with no reset among this agent's next 10 calls (so the 10-call outcome
    # window is reset-free for placebos as for erasures, which open a ~41-call segment)
    tu = tu.with_columns((pl.col("reset_consol") | pl.col("reset_session")).cast(pl.Int32).alias("_r"))
    tu = tu.with_columns(pl.col("_r").reverse().rolling_sum(10, min_samples=1).reverse().shift(-1).over("agent")
                         .fill_null(0).alias("_r_next10"))
    ev = ev.join(tu.select("turn_id", "_r_next10"), on="turn_id", how="left")
    ev = ev.filter((pl.col("etype") != "placebo") | (pl.col("_r_next10") == 0))
    # per-event features
    cm = commits.select("agent", "t", "repo_id").sort("agent", "t")
    calls = tu.select("agent", "turn_id", "t_call").sort("agent", "t_call")
    out = []
    by_agent_calls = {a: g for (a,), g in calls.partition_by("agent", as_dict=True).items()}
    by_agent_commits = {a: g for (a,), g in cm.partition_by("agent", as_dict=True).items()}
    by_agent_reads = {a: g.sort("t") for (a,), g in reads.partition_by("agent", as_dict=True).items()}
    by_agent_int = {a: g for (a,), g in int_rep.partition_by("agent", as_dict=True).items()}
    items_by_turn = items.group_by("turn_id").agg(pl.col("sender"), pl.col("kind").cast(pl.Utf8), pl.col("named"))
    ibt = {r[0]: r[1:] for r in items_by_turn.iter_rows()}
    for (tid, a, day, t, et, unit, d, m, pos) in ev.select("turn_id", "agent", "pt_date", "t_call", "etype", "unit", "day",
                                                           "m", "ctx_pos").iter_rows():
        C = by_agent_commits.get(a)
        # last commit before t (<= 60 min) and first commit after t (<= 60 min)
        k_pre = t_pre = k_post = t_post = None
        tt = np.datetime64(t.replace(tzinfo=None), "us")
        if C is not None and C.height:
            tarr = C["t"].to_numpy()
            rarr = C["repo_id"].to_numpy()
            tt = np.datetime64(t.replace(tzinfo=None), "us")
            i = np.searchsorted(tarr, tt, "left")
            if i > 0 and (tt - tarr[i - 1]) <= np.timedelta64(60, "m"):
                k_pre, t_pre = int(rarr[i - 1]), float((tt - tarr[i - 1]) / np.timedelta64(1, "s")) / 60
            if i < len(tarr) and (tarr[i] - tt) <= np.timedelta64(60, "m"):
                k_post, t_post = int(rarr[i]), float((tarr[i] - tt) / np.timedelta64(1, "s")) / 60
        # outcome window: the event call and the agent's next 9 calls (10 calls), capped at 30 min
        Ca = by_agent_calls[a]
        tc = Ca["t_call"].to_numpy()
        j0 = int(np.searchsorted(tc, np.datetime64(t.replace(tzinfo=None), "us"), "left"))
        t_end = t + dt.timedelta(minutes=30)
        if j0 + 10 < len(tc):
            t_end = min(t_end, Ca["t_call"][j0 + 10])
        k10 = t10 = None
        if C is not None and C.height:
            i2 = np.searchsorted(tarr, tt, "left")
            if i2 < len(tarr) and tarr[i2] < np.datetime64(t_end.replace(tzinfo=None), "us"):
                k10, t10 = int(rarr[i2]), float((tarr[i2] - tt) / np.timedelta64(1, "s")) / 60
        tlim = t_end if t10 is None else t + dt.timedelta(minutes=t10)
        win = Ca[j0:j0 + 10].filter(pl.col("t_call") <= tlim)
        senders, kinds, named = [], [], []
        for tt_ in win["turn_id"].to_list():
            if tt_ in ibt:
                s_, k_, n_ = ibt[tt_]
                senders += [int(v) if v is not None else -1 for v in s_]
                kinds += list(k_)
                for nn in n_:
                    if nn is not None:
                        named += list(nn)
        R = by_agent_reads.get(a)
        rd, t_read = [], None
        if R is not None:
            rr = R.filter((pl.col("t") >= t) & (pl.col("t") <= tlim))
            rd = rr["repo_id"].unique().to_list()
            if rr.height:
                t_read = (rr["t"].min() - t).total_seconds() / 60
        Ii = by_agent_int.get(a)
        irep = []
        if Ii is not None:
            ii = Ii.filter(pl.col("t") <= t + dt.timedelta(seconds=5))
            if ii.height:
                last = ii.tail(1)
                v = last["int_repos"][0]
                irep = list(v) if v is not None else []
        out.append({"turn_id": tid, "agent": a, "unit": unit, "day": d, "pt_date": day, "m": m, "etype": et,
                    "ctx_pos": pos, "k_pre": k_pre, "t_pre": t_pre, "k_post": k_post, "t_post": t_post,
                    "k10": k10, "t10": t10, "win_min": (t_end - t).total_seconds() / 60,
                    "reads": rd, "t_first_read": t_read, "peer_senders": senders, "peer_kinds": kinds,
                    "peer_named": sorted(set(named)), "intent_repos": irep, "n_win_calls": win.height})
    return guard(pl.DataFrame(out, infer_schema_length=None), "erasures")


def build_files40(commits, repos):
    """#40 shared repo: commit -> file groups (path depth <= 2), read-only git log on the bare clone."""
    rid = repos.filter(pl.col("repo") == "github.com/ai-village-agents/the-universe")["repo_id"]
    if rid.is_empty():
        return None
    rid = int(rid[0])
    c = commits.filter((pl.col("unit") == "40") & (pl.col("repo_id") == rid))
    path = ROOT / "data/raw/repos/github.com/ai-village-agents/the-universe.git"
    env = dict(os.environ, GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1", GIT_TERMINAL_PROMPT="0")
    txt = subprocess.run(["git", "-C", str(path), "log", "--all", "--name-only", "--format=C %H"], capture_output=True,
                         text=True, env=env).stdout
    fmap, cur = {}, None
    for line in txt.splitlines():
        if line.startswith("C "):
            cur = line[2:].strip()
            fmap[cur] = []
        elif line.strip() and cur:
            parts = line.strip().split("/")
            fmap[cur].append("/".join(parts[:2]))
    rows = []
    for (h, a, d, m) in c.select("hash", "agent", "day", "m").iter_rows():
        for f in sorted(set(fmap.get(h, []))):
            rows.append((h, a, d, m, f))
    return pl.DataFrame(rows, schema=["hash", "agent", "day", "m", "file"], orient="row")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    only = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None
    U = units()
    (OUT / "units.json").write_text(json.dumps(U, indent=1))
    days = day_frame(U)
    log(f"{len(U)} units, {days.height} days")
    commits, repos = build_commits(days)
    commits.drop("t").write_parquet(OUT / "commits.parquet", compression="zstd")
    repos.write_parquet(OUT / "repos.parquet", compression="zstd")
    log(f"commits {commits.height}, repos {repos.height}")
    if only is None or "presence" in only:
        build_presence(days).write_parquet(OUT / "presence.parquet", compression="zstd")
    log("presence")
    if only is None or "exog" in only:
        build_exog(days).write_parquet(OUT / "exog.parquet", compression="zstd")
    log("exog")
    if only is None or "content" in only:
        build_content(days, U).write_parquet(OUT / "content.parquet", compression="zstd")
    log("content")
    if only is None or "rooms" in only:
        build_rooms(days).write_parquet(OUT / "rooms.parquet", compression="zstd")
    log("rooms")
    if only is None or "layers" in only:
        build_layers(days, commits, U).write_parquet(OUT / "layers.parquet", compression="zstd")
    log("layers")
    if only is None or "erasures" in only:
        build_erasures(days, commits, repos, U).write_parquet(OUT / "erasures.parquet", compression="zstd")
    log("erasures")
    f40 = build_files40(commits, repos) if (only is None or "files40" in only) else None
    if f40 is not None:
        f40.write_parquet(OUT / "files40.parquet", compression="zstd")
    log("files40")
    prov = {"built_by": "hypotheses/H58-coordinated-superagents/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["work_commits (DQ4, agent work only)", "work_repos", "artifacts", "artifact_mentions",
                                   "intentions", "calendar", "call_windows", "context_ledger_turns",
                                   "context_ledger_items", "kicks_classified", "rooms_timeline", "behavior_states_v3",
                                   "reply_pairs (pair_set == cand)", "chat_core (ids only)",
                                   "embeddings/agent_win30 + agent_win30_style_resid_period_bge_small",
                                   "H34 markers/uses.parquet (read-only)",
                                   "data/raw/repos the-universe.git (read-only git log --name-only)"]}],
            "params": {"units": "H01 round-2 units (19, non-holdout)", "content_k": 6,
                       "work_behaviors": WORK_BEHAVIORS, "placebo_ctx_pos": 20, "placebo_rule": "no reset among the next 10 calls",
                       "reacq_window_calls": 10, "reacq_window_cap_min": 30, "commit_window_min": 60,
                       "not_used": "activity_bins, outages (activity_bins join bug, 2026-10-04)"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))
    log("done")


if __name__ == "__main__":
    main()
