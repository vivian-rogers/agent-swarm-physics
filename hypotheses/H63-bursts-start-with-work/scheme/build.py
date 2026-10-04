"""H63 scheme: per eligible non-holdout goal period (goal >= 30, >= 30 agent work commits), the strict touches, chat
links, work signals (deploy events, births, routine commits), active 5-min bins with rooms, all-present windows and
exogenous pulses. Codes and times only (no text).

    uv run python hypotheses/H63-bursts-start-with-work/scheme/build.py [--goals 31,39]

Output: data/processed/H63-bursts-start-with-work/G<NN>/{touches,links,signals,bins,days,kicks}.parquet, meta.parquet,
_provenance.json. Holdout asserted twice (calendar.holdout and common.holdout_mask). Times: float s since EPOCH.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import git_commit, holdout_mask  # noqa: E402
from project_states import project_map  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H63-bursts-start-with-work"
EPOCH = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc)
BIN = 300
MIN_CALLS_PRESENT = 20
DEPLOY_GAP = 3600.0        # a later deploy counts as a state change if >= 60 min after the project's previous deploy


def secs(col: str, alias: str | None = None) -> pl.Expr:
    return ((pl.col(col) - pl.lit(EPOCH)).dt.total_microseconds() / 1e6).alias(alias or col)


def work_filter() -> pl.Expr:
    return (pl.col("canonical") & ~pl.col("imported") & (pl.col("author_kind") == "agent") & ~pl.col("automated"))


def signals_all(pm: pl.DataFrame, am: pl.DataFrame, allow_holdout: bool = False) -> pl.DataFrame:
    """All (non-holdout unless allow_holdout) work signals: commits (deploy flag) and deploy commands, classified
    S / B / R / D."""
    wc = (pl.scan_parquet(SH / "work_commits.parquet").filter(work_filter() & (pl.lit(allow_holdout) | ~pl.col("holdout")))
          .select(pl.col("repo").cast(pl.String).alias("project"), "t", "author_agent", "pages_branch", "deploy_msg",
                  "goal_no", "pt_date").collect())
    wc = wc.with_columns(secs("t"), (pl.col("pages_branch") | pl.col("deploy_msg")).alias("deploy"),
                         pl.lit("commit").alias("src")).rename({"author_agent": "agent"})
    dep = (am.filter((pl.col("verb") == "deploy") & (pl.col("speaker_kind") == "agent"))
           .join(pm, on="artifact").select("project", "t", "agent", "goal_no", "pt_date")
           .with_columns(pl.lit(True).alias("deploy"), pl.lit("deploy_cmd").alias("src")))
    s = pl.concat([wc.select("project", "t", "agent", "deploy", "src", "goal_no", "pt_date"),
                   dep.select("project", "t", "agent", "deploy", "src", "goal_no", "pt_date")], how="vertical_relaxed")
    s = s.sort("project", "t")
    births = s.filter(pl.col("src") == "commit").group_by("project").agg(pl.col("t").min().alias("t_birth"))
    s = s.join(births, on="project", how="left")
    d = s.filter(pl.col("deploy")).with_columns(pl.col("t").shift(1).over("project").alias("t_prevdep"))
    d = d.with_columns((pl.col("t_prevdep").is_null() | (pl.col("t") - pl.col("t_prevdep") >= DEPLOY_GAP))
                       .alias("state_change"))
    s = s.join(d.select("project", "t", "src", "agent", "state_change").unique(["project", "t", "src", "agent"]),
               on=["project", "t", "src", "agent"], how="left")
    s = s.with_columns(
        pl.when(pl.col("state_change").fill_null(False)).then(pl.lit("S"))
        .when((pl.col("src") == "commit") & (pl.col("t") == pl.col("t_birth"))).then(pl.lit("B"))
        .when(pl.col("deploy")).then(pl.lit("D"))          # deploy within 60 min of a previous one (not a new state)
        .otherwise(pl.lit("R")).alias("cls"))
    return s.select("project", "t", "agent", "cls", "src", "goal_no", "pt_date")


def prepare(allow_holdout: bool = False):
    """Shared inputs. allow_holdout is only set by analysis/confirm.py (guarded)."""
    cal = pl.read_parquet(SH / "calendar.parquet").filter(pl.col("goal_no").is_not_null())
    pm = project_map()
    am = (pl.scan_parquet(SH / "artifact_mentions.parquet")
          .select("artifact", "t", "agent", "speaker_kind", "source", "how", "verb", "room", "message_id", "ref_index")
          .collect())
    calw = cal.select("pt_date", "goal_no", "win_start", "win_end", "holdout").sort("win_start")
    am = am.sort("t").join_asof(calw, left_on="t", right_on="win_start", strategy="backward")
    am = am.filter((pl.col("t") <= pl.col("win_end")) & (pl.lit(allow_holdout) | ~pl.col("holdout").fill_null(True)))
    am = am.with_columns(secs("t"))
    sig = signals_all(pm, am, allow_holdout)
    cw = (pl.scan_parquet(SH / "call_windows.parquet").filter(pl.lit(allow_holdout) | ~pl.col("holdout"))
          .select("turn_id", "agent", "pt_date", "goal_no", "t_call", "ctx_mode").collect())
    lt = pl.read_parquet(SH / "context_ledger_turns.parquet", columns=["turn_id", "room"])
    cw = cw.join(lt, on="turn_id", how="left").with_columns(secs("t_call"))
    kc = pl.read_parquet(SH / "kicks_classified.parquet").filter(pl.lit(allow_holdout) | ~pl.col("holdout").fill_null(False))
    return cal, am, sig, cw, kc


def build_goal(g, cal, am, sig, cw, kc, pm, out_root=OUT, allow_holdout=False, days_filter=None):
    """Write one period's tables to out_root/G<NN>. days_filter: optional list of PT dates to keep."""
    days = cal.filter((pl.col("goal_no") == g) & (pl.lit(allow_holdout) | ~pl.col("holdout"))).sort("pt_date")
    if days_filter is not None:
        days = days.filter(pl.col("pt_date").is_in(days_filter))
    dl = days["pt_date"].to_list()
    if not allow_holdout:
        assert not any(holdout_mask(dl, [g] * len(dl))), f"holdout day in G{g}"
    if not dl:
        return None
    dmap = {d: k for k, d in enumerate(dl)}
    od = out_root / f"G{g:02d}"
    od.mkdir(parents=True, exist_ok=True)
    dy = days.select("pt_date", secs("win_start"), secs("win_end")).with_columns(
        pl.col("pt_date").replace_strict(dmap, return_dtype=pl.Int16).alias("day"))
    # calls -> per-agent day spans, all-present windows, active 5-min bins with modal room
    c = cw.filter((pl.col("goal_no") == g) & pl.col("pt_date").is_in(dl)).with_columns(
        pl.col("pt_date").replace_strict(dmap, return_dtype=pl.Int16).alias("day"))
    span = c.group_by("day", "agent").agg(pl.len().alias("n_calls"), pl.col("t_call").min().alias("first_call"),
                                          pl.col("t_call").max().alias("last_call"))
    ap_ = (span.filter(pl.col("n_calls") >= MIN_CALLS_PRESENT).group_by("day")
           .agg(pl.col("first_call").max().alias("ap_lo"), pl.col("last_call").min().alias("ap_hi")))
    dy = dy.join(ap_, on="day", how="left")
    c = c.join(dy.select("day", "win_start"), on="day").with_columns(
        ((pl.col("t_call") - pl.col("win_start")) // BIN).cast(pl.Int32).alias("bin"))
    bins = (c.group_by("day", "bin", "agent").agg(pl.len().alias("n_calls"),
                                                  pl.col("room").drop_nulls().mode().first().alias("room")))
    # touches (strict, agent, action or chat) and links (chat url/bare) mapped to projects
    a_g = am.filter((pl.col("goal_no") == g) & pl.col("pt_date").is_in(dl)).join(pm, on="artifact")
    a_g = a_g.with_columns(pl.col("pt_date").replace_strict(dmap, return_dtype=pl.Int16).alias("day"))
    tch = (a_g.filter((pl.col("speaker_kind") == "agent") & pl.col("how").cast(pl.String).is_in(["url", "output", "bare"])
                      & pl.col("source").cast(pl.String).is_in(["action", "chat"]))
           .with_columns(pl.coalesce(pl.col("message_id"), pl.col("ref_index").cast(pl.String)).alias("ref"))
           .unique(["agent", "source", "ref", "project"])
           .select("t", "day", "agent", "project", pl.col("source").cast(pl.String), "room"))
    links = (a_g.filter(pl.col("source").cast(pl.String).eq("chat") & pl.col("how").cast(pl.String).is_in(["url", "bare"]))
             .unique(["message_id", "project"])
             .select("t", "day", "agent", pl.col("speaker_kind").cast(pl.String), "project", "room"))
    sg = sig.filter((pl.col("goal_no") == g) & pl.col("pt_date").is_in(dl)).with_columns(
        pl.col("pt_date").replace_strict(dmap, return_dtype=pl.Int16).alias("day")).drop("pt_date", "goal_no")
    k = kc.filter((pl.col("goal_no") == g) & pl.col("pt_date").is_in(dl)).with_columns(
        secs("t"), pl.col("pt_date").replace_strict(dmap, return_dtype=pl.Int16).alias("day"))
    kicks = k.select("t", "day", pl.col("kind").cast(pl.String), pl.col("subkind").cast(pl.String), "room",
                     pl.col("targets"))
    tch.write_parquet(od / "touches.parquet")
    links.write_parquet(od / "links.parquet")
    sg.write_parquet(od / "signals.parquet")
    bins.write_parquet(od / "bins.parquet")
    dy.join(span.group_by("day").agg(pl.len().alias("n_agents")), on="day", how="left").write_parquet(
        od / "days.parquet")
    span.write_parquet(od / "spans.parquet")
    kicks.write_parquet(od / "kicks.parquet")
    r = {"goal_no": g, "n_days": len(dl), "n_touches": tch.height, "n_links": links.height,
         "n_signals": sg.height, "n_S": sg.filter(pl.col("cls") == "S").height,
         "n_B": sg.filter(pl.col("cls") == "B").height, "n_R": sg.filter(pl.col("cls") == "R").height,
         "n_agents": span["agent"].n_unique(), "n_projects_touched": tch["project"].n_unique()}
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--goals", default="")
    a = ap.parse_args()
    cal, am, sig, cw, kc = prepare(False)
    pm = project_map()
    wc_counts = sig.filter(pl.col("src") == "commit").group_by("goal_no").len()
    goals = sorted(g for g, n in wc_counts.iter_rows() if g is not None and g >= 30 and n >= 30)
    if a.goals:
        goals = [g for g in goals if g in {int(x) for x in a.goals.split(",")}]
    meta = []
    for g in goals:
        r = build_goal(g, cal, am, sig, cw, kc, pm)
        if r:
            meta.append(r)
            print(r, flush=True)
    m = pl.DataFrame(meta)
    if a.goals and (OUT / "meta.parquet").exists():
        m = pl.concat([pl.read_parquet(OUT / "meta.parquet").filter(~pl.col("goal_no").is_in(m["goal_no"])), m])
    m.sort("goal_no").write_parquet(OUT / "meta.parquet")
    prov = {"built_by": "hypotheses/H63-bursts-start-with-work/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": "shared tables (DQ4 work ledger, artifacts, DQ1 ledger)",
                        "tables": ["work_commits", "artifact_mentions", "artifacts", "call_windows",
                                   "context_ledger_turns", "kicks_classified", "calendar"]}],
            "params": {"bin_s": BIN, "min_calls_present": MIN_CALLS_PRESENT, "deploy_gap_s": DEPLOY_GAP,
                       "work_filter": "canonical & ~imported & author_kind==agent & ~automated",
                       "holdout": "excluded, asserted twice", "epoch": EPOCH.isoformat()},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))


if __name__ == "__main__":
    main()
