"""H94 scheme: agent x repo work-quantum tables per goal-period unit, with owner, room and kickoff-naming indicators.

  uv run python hypotheses/H94-maxent-work-allocation/scheme/build.py --all | --period 31 ...

Work quantum (H94): one (agent, 30-min window from the day's win_start, repo) with >= 1 agent work commit (DQ4 default
filter: canonical & ~imported & author_kind == agent & ~automated; Claude Code agent excluded).
Owner (H94): the agent with the earliest agent work commit to the repo in all of DQ4 (variant: earliest in the period).
Room: agent's room at the window midpoint (rooms_timeline; null t_end = open); room_ij = 1 if agent i's modal room in the
unit equals the owner's modal room in the unit (owner absent from the unit: owner's room at the unit's first quantum).
Writes data/processed/H94-maxent-work-allocation/G<NN>/quanta.parquet (repo names hashed), counts.json, _provenance.json.
Holdout days dropped (replicator_hosts.period_days + common.holdout_mask); --allow-holdout only via confirm.py imports.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import bisect  # noqa: E402
import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from functools import lru_cache  # noqa: E402
from pathlib import Path  # noqa: E402

import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
import replicator_hosts as R  # noqa: E402
from common import REVISION, git_commit, holdout_mask  # noqa: E402

OUT = ROOT / "data/processed/H94-maxent-work-allocation"
PERIODS = [30, 31, 33, 35, 36, 37, 38, 39, 40, 41, 42, 44, 51]
CLAUDE_CODE = 19
W = 30


@lru_cache(maxsize=1)
def owners_alltime() -> pl.DataFrame:
    wc = (pl.scan_parquet(R.SHARED / "work_commits.parquet")
          .filter(pl.col("canonical") & ~pl.col("imported") & (pl.col("author_kind").cast(pl.String) == "agent")
                  & ~pl.col("automated") & pl.col("author_agent").is_not_null() & (pl.col("author_agent") != CLAUDE_CODE))
          .select(pl.col("repo").cast(pl.String), pl.col("author_agent").alias("agent"), "t").collect())
    return (wc.sort("t", "agent").group_by("repo", maintain_order=True).first()
            .select("repo", pl.col("agent").alias("owner"), pl.col("t").alias("t_owner")))


def rooms_asof(rt: pl.DataFrame):
    far = dt.datetime(2100, 1, 1, tzinfo=dt.timezone.utc)
    by = {}
    for (a,), g in rt.sort("t_start").group_by(["agent"], maintain_order=True):
        by[int(a)] = ([x.timestamp() for x in g["t_start"].to_list()], g["room"].to_list(),
                      [(x or far).timestamp() for x in g["t_end"].to_list()])

    def room_of(a, t):
        v = by.get(int(a))
        if not v:
            return None
        k = bisect.bisect_right(v[0], t.timestamp()) - 1
        return v[1][k] if k >= 0 else None
    return room_of


def build_period(g: int, allow_holdout: bool = False, write: bool = True) -> dict:
    days = R.period_days(g, allow_holdout)
    if not allow_holdout:
        days = [d for d, h in zip(days, holdout_mask(days, [g] * len(days))) if not h]
    commits = R.load_commits(g, days)
    cal = R.calendar().filter(pl.col("pt_date").is_in(days)).select("pt_date", "win_start")
    c = commits.join(cal, on="pt_date", how="inner").with_columns(
        ((pl.col("t") - pl.col("win_start")).dt.total_seconds() // (W * 60)).clip(lower_bound=0).cast(pl.Int32).alias("win"))
    q = c.group_by("agent", "pt_date", "win", "repo").agg(pl.len().alias("n_commits"), pl.col("t").min().alias("t_first"),
                                                         pl.col("win_start").first())
    umap = R.unit_of_day(g)
    q = q.with_columns(pl.col("pt_date").replace_strict(umap, default=None).alias("unit"))
    own = owners_alltime()
    first_in = c.sort("t").group_by("repo", maintain_order=True).first().select("repo", pl.col("agent").alias("owner_period"))
    q = q.join(own, on="repo", how="left").join(first_in, on="repo", how="left")
    q = q.with_columns((pl.col("t_owner") < pl.col("win_start").min()).alias("carried"))
    named = R.kickoff_named(g, sorted(set(q["repo"].to_list())))
    q = q.with_columns(pl.col("repo").replace_strict(named, default=False, return_dtype=pl.Boolean).alias("named"))
    room_of = rooms_asof(pl.read_parquet(R.SHARED / "rooms_timeline.parquet"))
    mids = [(a, ws + dt.timedelta(minutes=W * w + W / 2)) for a, ws, w in q.select("agent", "win_start", "win").iter_rows()]
    q = q.with_columns(pl.Series("room", [room_of(a, t) for a, t in mids], dtype=pl.Int16))
    # modal room per (unit, agent); owner's room in the unit
    mr = (q.drop_nulls("room").group_by("unit", "agent", "room").len().sort("unit", "agent", "len", "room", descending=[False, False, True, False])
          .group_by("unit", "agent", maintain_order=True).first().select("unit", "agent", pl.col("room").alias("room_mode")))
    q = q.join(mr, on=["unit", "agent"], how="left")
    orm = mr.rename({"agent": "owner", "room_mode": "owner_room"})
    q = q.join(orm, on=["unit", "owner"], how="left")
    # owner absent from the unit: owner's room at the unit's first quantum
    u0 = q.group_by("unit").agg(pl.col("t_first").min().alias("u_t0"))
    q = q.join(u0, on="unit")
    fill = [room_of(o, t) if (o is not None and r is None) else r
            for o, r, t in q.select("owner", "owner_room", "u_t0").iter_rows()]
    q = q.with_columns(pl.Series("owner_room", fill, dtype=pl.Int16)).drop("u_t0")
    q = q.with_columns((pl.col("owner") == pl.col("agent")).fill_null(False).alias("own"),
                       (pl.col("owner_period") == pl.col("agent")).fill_null(False).alias("own_period"),
                       (pl.col("room_mode") == pl.col("owner_room")).fill_null(False).alias("same_room"))
    labs = dict(R.roster().select("agent", "lab").iter_rows())
    q = q.with_columns(pl.col("agent").replace_strict(labs, default=None, return_dtype=pl.String).alias("lab"),
                       pl.col("owner").replace_strict(labs, default=None, return_dtype=pl.String).alias("owner_lab"))
    q = q.with_columns((pl.col("lab") == pl.col("owner_lab")).fill_null(False).alias("same_lab")).drop("lab", "owner_lab")
    q = q.sort("unit", "agent", "pt_date", "win", "repo")
    counts = {"goal_no": g, "days": len(days), "quanta": q.height, "commits": int(q["n_commits"].sum()),
              "agents": q["agent"].n_unique(), "repos": q["repo"].n_unique(),
              "units": dict(q.group_by("unit").len().sort("unit").iter_rows())}
    if write:
        od = OUT / f"G{g:02d}"
        od.mkdir(parents=True, exist_ok=True)
        R.hashed(q, ("repo",)).write_parquet(od / "quanta.parquet", compression="zstd")
        (od / "counts.json").write_text(json.dumps(counts, indent=1))
    return {"quanta": q, "counts": counts, "named": named}


def provenance(periods):
    p = OUT / "_provenance.json"
    prov = json.loads(p.read_text()) if p.exists() else {}
    prov.update({"built_by": "hypotheses/H94-maxent-work-allocation/scheme/build.py", "git_commit": git_commit(),
                 "inputs": [{"source": "ai-village", "revision": REVISION,
                             "tables": ["work_commits", "calendar", "period_units", "rooms_timeline", "roster", "artifacts",
                                        "artifact_mentions", "chat_core", "chat_text (kickoff text, in memory only)",
                                        "village_goals (in memory only)"]}],
                 "params": {"quantum": "agent x 30-min window x repo with >= 1 agent work commit", "owner": "earliest agent "
                            "work commit, all DQ4", "named": "H54 rule via replicator_hosts.kickoff_named"},
                 "built_at": dt.datetime.now(dt.timezone.utc).isoformat()})
    prov["periods_built"] = sorted(set(prov.get("periods_built", [])) | set(periods))
    p.write_text(json.dumps(prov, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", type=int, action="append")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    periods = PERIODS if a.all else (a.period or [])
    OUT.mkdir(parents=True, exist_ok=True)
    for g in periods:
        print(json.dumps(build_period(g)["counts"]), flush=True)
    provenance(periods)


if __name__ == "__main__":
    main()
