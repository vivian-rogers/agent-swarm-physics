"""H07 scheme, step 1: lineages of the RPG forks from the fork instant onward (trees only, no file contents).

Inputs: bare partial clones (--filter=blob:none) in data/raw/repos/<repo>.git (see data/raw/repos/_source.md);
shared tables roster, calendar, rooms_timeline.

Holdout (#34): the only pre-T0 information used is the identity of the common ancestor commit A (the newest commit
of rpg-game/main reachable from every fork's main) and its tree. No pre-T0 commit metadata is read: every log /
rev-list call is restricted to A..main, and any commit in A..main with a committer time before T0 is dropped (and
counted in the provenance).

Outputs (data/processed/H07-rpg-forks/):
  commits.parquet    lineage, sha, author agent, times, merge flag, first-parent flag, files touched (A/M/D counts),
                     room of the author at commit time, cross_room flag
  commit_files.parquet  lineage, sha, path, status (A/M/D) for non-merge commits
  fp_trees.parquet   the tree (path -> blob) at A and at every first-parent commit of each lineage's main, with the
                     cumulative non-merge commit count since A (the commit clock) and active hours since T0
  day_snapshots.parquet  lineage, pt_date, sha of the main state at the end of that PT day (all calendar days from
                     2026-03-16 to the lineage's last commit), active hours since T0 at that day's end
"""
from __future__ import annotations

import datetime as dt
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import PT, UTC, git_commit  # noqa: E402

REPOS = ROOT / "data/raw/repos"
SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H07-rpg-forks"
T0 = dt.datetime(2026, 3, 16, 16, 20, 5, 640000, tzinfo=UTC)  # #35 kickoff (village_goals start_time)
LINEAGES = {"best": "rpg-game-best", "rest": "rpg-game-rest", "restweek": "rpg-game-rest-week", "origin": "rpg-game"}
ROOM_CODE = {0: "general", 2: "best", 3: "rest"}


def git(repo: str, *args: str) -> str:
    return subprocess.run(["git", "-C", str(REPOS / f"{repo}.git"), *args], capture_output=True, text=True,
                          check=True).stdout


def find_ancestor() -> str:
    """Newest commit of rpg-game/main that every fork's main contains (sets of SHAs only; no metadata)."""
    origin = set(git("rpg-game", "rev-list", "main").split())
    common = None
    for lin, repo in LINEAGES.items():
        if lin == "origin":
            continue
        s = set(git(repo, "rev-list", "main").split()) & origin
        common = s if common is None else common & s
    order = git("rpg-game", "rev-list", "--topo-order", "main").split()
    return next(c for c in order if c in common)


def agent_map():
    ro = pl.read_parquet(SH / "roster.parquet")
    m = {}
    for code, name in zip(ro["agent"].to_list(), ro["name"].to_list()):
        key = name.lower().replace("(", "").replace(")", "").replace(" ", "-")
        if key.startswith("claude-code"):
            continue
        m[key] = code
    return m


def room_at(rt: pl.DataFrame):
    by = defaultdict(list)
    for a, room, ts, te in rt.select("agent", "room", "t_start", "t_end").iter_rows():
        by[a].append((ts, te, room))

    def f(agent, t):
        for ts, te, room in by.get(agent, []):
            if ts <= t < te:
                return room
        return None
    return f


def active_hours_fn(cal: pl.DataFrame):
    """Active hours since T0 at UTC time t: sum of empirical active windows (calendar) clipped to [T0, t]."""
    wins = [(s, e) for s, e in cal.select("win_start", "win_end").iter_rows() if s is not None and e is not None]

    def f(t):
        h = 0.0
        for s, e in wins:
            lo, hi = max(s, T0), min(e, t)
            if hi > lo:
                h += (hi - lo).total_seconds() / 3600
        return h
    return f


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    A = find_ancestor()
    amap = agent_map()
    rt = pl.read_parquet(SH / "rooms_timeline.parquet")
    room = room_at(rt)
    cal = pl.read_parquet(SH / "calendar.parquet")
    ah = active_hours_fn(cal)
    sep = "\x1f"
    commits, cfiles, trees, days = [], [], [], []
    dropped_pre_t0 = {}
    # ancestor tree
    for line in git("rpg-game", "ls-tree", "-r", A).splitlines():
        meta, path = line.split("\t", 1)
        trees.append(("ancestor", A, 0, None, 0, 0.0, path, meta.split()[2]))
    for lin, repo in LINEAGES.items():
        fmt = sep.join(["%H", "%P", "%ae", "%aI", "%cI"])
        log = git(repo, "log", "--no-renames", "--name-status", f"--format=@@{fmt}", f"{A}..main")
        fp = set(git(repo, "rev-list", "--first-parent", f"{A}..main").split())
        cur = None
        recs = []
        for line in log.splitlines():
            if line.startswith("@@"):
                h, parents, email, ta, tc = line[2:].split(sep)
                cur = {"sha": h, "parents": parents.split(), "email": email, "t_author": dt.datetime.fromisoformat(ta)
                       .astimezone(UTC), "t_commit": dt.datetime.fromisoformat(tc).astimezone(UTC), "files": []}
                recs.append(cur)
            elif line.strip() and cur is not None:
                st, path = line.split("\t", 1)
                cur["files"].append((st[0], path))
        pre = [r for r in recs if r["t_commit"] < T0]
        dropped_pre_t0[lin] = len(pre)
        recs = [r for r in recs if r["t_commit"] >= T0]
        for r in recs:
            ag = amap.get(r["email"].split("@")[0].lower())  # emails are <agent-name-slug>@agentvillage.org
            rm = room(ag, r["t_commit"]) if ag is not None else None
            n = defaultdict(int)
            for st, _ in r["files"]:
                n[st] += 1
            is_merge = len(r["parents"]) > 1
            commits.append((lin, r["sha"], r["email"].split("@")[0], ag, r["t_author"], r["t_commit"], is_merge,
                            r["sha"] in fp, len(r["files"]), n["A"], n["M"], n["D"], rm, ah(r["t_commit"])))
            if not is_merge:
                for st, path in r["files"]:
                    cfiles.append((lin, r["sha"], path, st))
        # first-parent chain trees, oldest first
        chain = git(repo, "rev-list", "--first-parent", "--reverse", f"{A}..main").split()
        tmap = {r["sha"]: r["t_commit"] for r in recs}
        for k, sha in enumerate(chain, 1):
            if sha not in tmap:
                continue
            ncum = int(git(repo, "rev-list", "--count", "--no-merges", f"{A}..{sha}").strip())
            for line in git(repo, "ls-tree", "-r", sha).splitlines():
                meta, path = line.split("\t", 1)
                trees.append((lin, sha, k, tmap[sha], ncum, ah(tmap[sha]), path, meta.split()[2]))
        # day snapshots: main state at the end of each PT day
        chain_t = [(tmap[s], s) for s in chain if s in tmap]
        if not chain_t:
            continue
        last = max(t for t, _ in chain_t)
        d = T0.astimezone(PT).date()
        while d <= last.astimezone(PT).date() + dt.timedelta(days=1):
            end = dt.datetime.combine(d + dt.timedelta(days=1), dt.time(), tzinfo=PT).astimezone(UTC)
            sha = A
            for t, s in chain_t:
                if t <= end:
                    sha = s
            days.append((lin, d.isoformat(), sha, ah(end)))
            d += dt.timedelta(days=1)
    pl.DataFrame(commits, schema=["lineage", "sha", "author", "agent", "t_author", "t_commit", "is_merge",
                                  "first_parent", "n_files", "n_added", "n_modified", "n_deleted", "author_room",
                                  "active_h"], orient="row", infer_schema_length=None).with_columns(
        pl.col("agent").cast(pl.Int8), pl.col("author_room").cast(pl.Int8),
        (pl.col("author_room").replace_strict({2: "best", 3: "rest", 0: "general"}, default=None)
         .alias("author_room_name"))).with_columns(
        pl.when(pl.col("lineage").is_in(["rest", "restweek"])).then(pl.lit("rest"))
        .when(pl.col("lineage") == "best").then(pl.lit("best")).otherwise(None).alias("home_room")
    ).write_parquet(OUT / "commits.parquet")
    pl.DataFrame(cfiles, schema=["lineage", "sha", "path", "status"], orient="row").write_parquet(
        OUT / "commit_files.parquet")
    pl.DataFrame(trees, schema=["lineage", "sha", "k", "t_commit", "n_commits", "active_h", "path", "blob"],
                 orient="row", infer_schema_length=None).write_parquet(OUT / "fp_trees.parquet")
    pl.DataFrame(days, schema=["lineage", "pt_date", "sha", "active_h"], orient="row").write_parquet(
        OUT / "day_snapshots.parquet")
    prov = {"built_by": "hypotheses/H07-rpg-forks/scheme/build_lineages.py", "git_commit": git_commit(),
            "inputs": [{"source": "github.com/ai-village-agents/" + r, "head": git(r, "rev-parse", "main").strip()}
                       for r in LINEAGES.values()] +
                      [{"source": "ai-village (shared tables)", "tables": ["roster", "calendar", "rooms_timeline"]}],
            "params": {"T0": T0.isoformat(), "ancestor": A, "dropped_pre_t0_commits": dropped_pre_t0},
            "built_at": dt.datetime.now(UTC).isoformat()}
    p = OUT / "_provenance.json"
    old = json.loads(p.read_text()) if p.exists() else {}
    old["build_lineages"] = prov
    p.write_text(json.dumps(old, indent=1))
    print("ancestor", A, "dropped pre-T0", dropped_pre_t0, "commits", len(commits), "tree rows", len(trees))


if __name__ == "__main__":
    main()
