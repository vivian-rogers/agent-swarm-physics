"""H79 scheme: artifact reaction events (session x product repo) with executed catalysts, reversed catalysts and reads.
Ids only, no text.

uv run python hypotheses/H79-artifact-autocatalytic-set/scheme/build.py
Writes data/processed/H79-artifact-autocatalytic-set/{events,species,food}.parquet + _provenance.json
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit, holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
OUTD = ROOT / "data/processed/H79-artifact-autocatalytic-set"
PERIODS = [31, 33, 35, 36, 37, 38, 39, 40, 41, 42, 44, 51]   # non-holdout dense-git periods (#30+); NE29 follow-up
EXEC_HEADS = {"python3", "python", "node", "bash", "sh", "make", "pytest", "deno", "bun", "ruby", "perl", "php", "go",
              "cargo", "java", "tsx", "ts-node", "zsh"}
WRITE_VERBS = {"git push", "git commit", "deploy", "gh pr create", "glab mr create", "gh pr merge", "glab repo create",
               "gh repo create", "gh issue create", "gh issue comment", "gh pr comment", "git add", "git rm",
               "git init", "glab mr merge", "gh pr review", "gh pr close"}
CWD_WINDOW = dt.timedelta(minutes=30)


def calendar():
    c = pl.read_parquet(SH / "calendar.parquet").select("pt_date", "goal_no", "win_start", "win_end")
    return c.with_columns(pl.Series("ho", holdout_mask(c["pt_date"].to_list(), c["goal_no"].to_list())))


def sessions():
    return pl.read_parquet(SH / "sessions.parquet", columns=["session", "agent", "first_t", "last_t"]).sort("first_t")


def attach_session(df: pl.DataFrame, ses: pl.DataFrame, agent_col: str = "agent") -> pl.DataFrame:
    s = ses.with_columns(pl.col("agent").cast(df.schema[agent_col]))
    out = df.sort("t").join_asof(s, left_on="t", right_on="first_t", by_left=agent_col, by_right="agent",
                                 strategy="backward", check_sortedness=False)
    return out.filter(pl.col("session").is_not_null() & (pl.col("t") <= pl.col("last_t") + pl.duration(minutes=5)))


def repo_ids() -> tuple[dict, pl.DataFrame]:
    """Map every artifact id to its species id (repo; files -> parent repo; sites -> parent repo if known)."""
    a = pl.read_parquet(SH / "artifacts.parquet", columns=["artifact", "kind", "name", "parent", "first_t", "first_agent"])
    kind = dict(zip(a["artifact"].to_list(), a["kind"].cast(pl.Utf8).to_list()))
    par = dict(zip(a["artifact"].to_list(), a["parent"].to_list()))
    sp = {}
    for x, k in kind.items():
        if k == "domain":
            sp[x] = None                      # platform: food, never a species
        elif k == "file":
            p = par.get(x)
            sp[x] = p if p is not None else x
        elif k == "site":
            p = par.get(x)
            sp[x] = p if p is not None else x
        else:
            sp[x] = x
    return sp, a


def main(periods=None, allow_holdout: bool = False, outd: Path | None = None):
    """allow_holdout=True only from analysis/confirm.py behind its guard."""
    global OUTD
    periods = periods or PERIODS
    OUTD = outd or OUTD
    OUTD.mkdir(parents=True, exist_ok=True)
    cal = calendar()
    ses = sessions()
    sp, arts = repo_ids()
    wr = pl.read_parquet(SH / "work_repos.parquet", columns=["repo", "artifacts"])
    repo2art = {r: (a_[0] if a_ is not None and len(a_) else None) for r, a_ in wr.iter_rows()}
    keep_days = cal.filter(pl.col("goal_no").is_in(periods) & (pl.lit(allow_holdout) | ~pl.col("ho"))).select(
        "pt_date", "goal_no")

    # ---------------------------------------------------------------- commits -> events
    wc = pl.read_parquet(SH / "work_commits.parquet", columns=[
        "repo", "hash", "t", "pt_date", "goal_no", "author_agent", "author_kind", "imported", "canonical", "automated"])
    wc = wc.filter((pl.col("author_kind") == "agent") & ~pl.col("imported")).with_columns(pl.col("repo").cast(pl.Utf8))
    wc = wc.join(keep_days, on=["pt_date", "goal_no"], how="semi")
    wc = wc.with_columns(pl.col("repo").replace_strict(repo2art, default=None).alias("product"))
    am = pl.read_parquet(SH / "artifact_mentions.parquet").filter(pl.col("source") == "action")
    am = am.with_columns(pl.col("artifact").replace_strict(sp, default=None).alias("sp"))
    am = am.filter(pl.col("sp").is_not_null())
    am_s = attach_session(am.select("t", "agent", "sp", "how", "verb"), ses)
    pushes = am_s.filter(pl.col("verb") == "git push").select("session", pl.col("sp").alias("product")).unique()
    agentc = wc.filter(~pl.col("automated"))
    agentc = attach_session(agentc.rename({"author_agent": "agent"}), ses)
    canon = agentc.filter(pl.col("canonical"))
    forkc = agentc.filter(~pl.col("canonical")).join(pushes, on=["session", "product"], how="semi")   # DQ4 fork rows
    agentc = pl.concat([canon, forkc]).unique(["hash", "product"])
    ev = agentc.filter(pl.col("product").is_not_null()).group_by("goal_no", "session", "agent", "product").agg(
        pl.len().alias("n_commits"), pl.col("t").min().alias("t_first"), pl.col("t").max().alias("t_last"),
        pl.col("pt_date").min().alias("pt_date"))
    ev = ev.with_columns(pl.lit("agent").alias("kind"))

    # ---------------------------------------------------------------- executions with resolved cwd
    act = pl.scan_parquet(SH / "actions.parquet").select("t", "agent").with_row_index("row").collect()
    bh = pl.read_parquet(SH / "actions_bash_head_fixed.parquet", columns=["row", "bash_head_fixed"])
    act = act.join(bh.with_columns(pl.col("row").cast(pl.UInt32)), on="row").with_columns(
        pl.col("bash_head_fixed").cast(pl.Utf8).alias("h"))
    is_exec = pl.col("h").is_in(list(EXEC_HEADS)) | pl.col("h").str.starts_with("./") | \
        pl.col("h").str.ends_with(".sh") | pl.col("h").str.ends_with(".py")
    ex = act.filter(is_exec & pl.col("agent").is_not_null()).select("t", "agent")
    ex = attach_session(ex, ses)
    cwd = am_s.filter(pl.col("how").is_in(["cwd", "session_cwd"])).select(
        "t", "agent", "session", pl.col("sp").alias("cwd")).sort("t")
    ex = ex.sort("t").join_asof(cwd.rename({"t": "t_cwd"}).with_columns(pl.col("t_cwd").alias("t")), on="t",
                                by=["agent", "session"], strategy="backward", check_sortedness=False)
    ex = ex.filter(pl.col("cwd").is_not_null() & (pl.col("t") - pl.col("t_cwd") <= CWD_WINDOW))
    ex = ex.select("session", "agent", "t", "cwd")
    n_exec_all = act.filter(is_exec).height

    # catalysts: executions in the session before the event's last commit
    e_ids = ev.with_row_index("eid")
    cat = e_ids.select("eid", "session", "t_last").join(ex, on="session").filter(pl.col("t") <= pl.col("t_last")) \
        .group_by("eid").agg(pl.col("cwd").unique().alias("cat"))
    # reversed: executions after the last commit, same session or the agent's next session
    nxt = ses.sort("agent", "first_t").with_columns(pl.col("session").shift(-1).over("agent").alias("next_session"))
    e2 = e_ids.join(nxt.select("session", "next_session"), on="session", how="left")
    rev_same = e2.select("eid", "session", "t_last").join(ex, on="session").filter(pl.col("t") > pl.col("t_last"))
    rev_next = e2.select("eid", pl.col("next_session").alias("session")).drop_nulls().join(ex, on="session")
    rev = pl.concat([rev_same.select("eid", "cwd"), rev_next.select("eid", "cwd")]).group_by("eid").agg(
        pl.col("cwd").unique().alias("cat_rev"))
    # reads: strict mentions, non-write verbs, before the last commit
    rd = am_s.filter(pl.col("how").is_in(["url", "output", "bare"]) &
                     (pl.col("verb").is_null() | ~pl.col("verb").cast(pl.Utf8).is_in(list(WRITE_VERBS)))) \
        .select("session", "t", pl.col("sp").alias("read"))
    reads = e_ids.select("eid", "session", "t_last").join(rd, on="session").filter(pl.col("t") <= pl.col("t_last")) \
        .group_by("eid").agg(pl.col("read").unique().alias("reads"))
    ev = e_ids.join(cat, on="eid", how="left").join(rev, on="eid", how="left").join(reads, on="eid", how="left")

    # ---------------------------------------------------------------- automated self-reactions (stream-days)
    au = wc.filter(pl.col("automated") & pl.col("canonical") & pl.col("product").is_not_null()).group_by(
        "goal_no", "author_agent", "product", "pt_date").agg(pl.len().alias("n_commits"), pl.col("t").min().alias("t_first"),
                                                             pl.col("t").max().alias("t_last"))
    au = au.with_columns(pl.lit(None, pl.Int32).alias("session"), pl.col("author_agent").alias("agent"),
                         pl.lit("auto").alias("kind"), pl.concat_list([pl.col("product")]).alias("cat"),
                         pl.concat_list([pl.col("product")]).alias("cat_rev"), pl.lit(None, pl.List(pl.Int32)).alias("reads"))
    cols = ["goal_no", "kind", "session", "agent", "product", "n_commits", "t_first", "t_last", "pt_date", "cat",
            "cat_rev", "reads"]
    ev = pl.concat([ev.select(cols).with_columns(pl.col("session").cast(pl.Int32), pl.col("agent").cast(pl.Int8),
                                                 pl.col("product").cast(pl.Int32), pl.col("cat").cast(pl.List(pl.Int32)),
                                                 pl.col("cat_rev").cast(pl.List(pl.Int32)),
                                                 pl.col("reads").cast(pl.List(pl.Int32))),
                    au.select(cols).with_columns(pl.col("agent").cast(pl.Int8), pl.col("product").cast(pl.Int32),
                                                 pl.col("cat").cast(pl.List(pl.Int32)),
                                                 pl.col("cat_rev").cast(pl.List(pl.Int32)))], how="vertical_relaxed")
    ev = ev.sort("goal_no", "t_first").with_row_index("event_id")
    ev.write_parquet(OUTD / "events.parquet", compression="zstd")

    # ---------------------------------------------------------------- species and food per period
    starts = cal.group_by("goal_no").agg(pl.col("win_start").min().alias("start"), pl.col("win_end").max().alias("end"))
    sp_df = arts.with_columns(pl.col("artifact").replace_strict(sp, default=None).alias("sp")).filter(
        pl.col("sp").is_not_null()).group_by("sp").agg(pl.col("first_t").min(), pl.col("first_agent").sort_by(
            "first_t").first(), pl.col("kind").first().cast(pl.Utf8))
    sp_df.rename({"sp": "artifact"}).write_parquet(OUTD / "species.parquet", compression="zstd")
    chat = pl.read_parquet(SH / "artifact_mentions.parquet").filter(
        (pl.col("source") == "chat") & (pl.col("speaker_kind") != "agent")).with_columns(
        pl.col("artifact").replace_strict(sp, default=None).alias("sp")).filter(pl.col("sp").is_not_null())
    food = []
    for g in periods:
        st = starts.filter(pl.col("goal_no") == g)
        if st.height == 0:
            continue
        s0, s1 = st["start"][0], st["end"][0]
        pre = sp_df.filter(pl.col("first_t") < s0)["sp"].to_list()
        named = chat.filter((pl.col("t") >= s0) & (pl.col("t") <= s1))["sp"].unique().to_list()
        food += [(g, x, "pre") for x in pre] + [(g, x, "operator_named") for x in named]
    pl.DataFrame(food, schema={"goal_no": pl.Int8, "artifact": pl.Int32, "why": pl.Utf8}, orient="row").write_parquet(
        OUTD / "food.parquet", compression="zstd")

    (OUTD / "_provenance.json").write_text(json.dumps({
        "built_by": "hypotheses/H79-artifact-autocatalytic-set/scheme/build.py", "git_commit": git_commit(),
        "inputs": [{"source": "ai-village", "revision": REVISION,
                    "tables": ["work_commits (DQ4)", "work_repos", "sessions", "artifacts", "artifact_mentions",
                               "actions", "actions_bash_head_fixed", "calendar"]}],
        "params": {"periods": PERIODS, "exec_heads": sorted(EXEC_HEADS) + ["./*", "*.sh", "*.py"],
                   "cwd_window_min": 30, "write_verbs_excluded_from_reads": sorted(WRITE_VERBS),
                   "fork_rows": "non-canonical agent rows kept when the same agent pushed to that repo in the session",
                   "food": "pre-period artifacts (first_t < period start) + human/operator chat-named in period; "
                           "domains/platforms never species"},
        "stats": {"exec_actions_all": n_exec_all, "exec_with_cwd": ex.height, "events": ev.height},
        "built_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "note": "ids and counts only"}, indent=1))
    print(ev.group_by("goal_no", "kind").agg(pl.len(), pl.col("n_commits").sum()).sort("goal_no", "kind"))
    print("exec all", n_exec_all, "with cwd", ex.height)


if __name__ == "__main__":
    main()
