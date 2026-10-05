"""H41 round 2 scheme: write and read events on artifacts (R2), hashed, no text stored.

  uv run python hypotheses/H41-readout-light-cone/scheme/build_r2.py files       # DQ4 file-level commit history
  uv run python hypotheses/H41-readout-light-cone/scheme/build_r2.py reads       # read events (artifact_mentions)
  uv run python hypotheses/H41-readout-light-cone/scheme/build_r2.py local       # local file reads (command text, in memory)
  uv run python hypotheses/H41-readout-light-cone/scheme/build_r2.py all

Outputs in data/processed/H41-readout-light-cone/r2/tables/:
  commit_files.parquet   repo (artifact id), hash, t (epoch s), author_agent, path_hash, base_hash, base_ok
                         agent work commits (author_kind agent, not automated, not reserved) since 2026-02-25
  writes_push.parquet    agent, t, artifact, kind   (source action mentions with verb git push / deploy)
  reads.parquet          agent, t, artifact, kind, verb, chan, repo (repo of the artifact), path_hash (file URLs)
  local_reads.parquet    agent, t, repo, path_hash, match (path / base): command rows in a repo's working directory
                         naming a path that some agent committed to that repo
Definitions: README "Round 2", R2 (written 2026-10-05 03:50 UTC before any round-2 statistic).
Reserved days are removed (holdout_mask + calendar.holdout) before any text is read. Paths and command text are hashed
in memory; nothing textual is written.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "2")
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
sys.path.insert(0, str(HERE))
from common import REVISION, git_commit, holdout_mask  # noqa: E402
import h41core as C  # noqa: E402

SH = C.SH
OUT = C.OUT / "r2" / "tables"
REPOS = ROOT / "data/raw/repos"
T_START = dt.datetime(2026, 2, 25, tzinfo=dt.timezone.utc)
READ_VERBS = ["git pull", "git fetch", "git clone", "gh repo clone", "glab repo clone", "fetch", "git show", "git log",
              "gh pr view", "gh pr diff", "gh issue view", "glab mr view", "glab issue view", "gh api", "gh api repos",
              "glab api", "glab api projects"]
CHAN = {"git pull": "pull", "git fetch": "pull", "git clone": "pull", "gh repo clone": "pull", "glab repo clone": "pull",
        "fetch": "page", "git show": "pull", "git log": "pull", "gh pr view": "api", "gh pr diff": "api",
        "gh issue view": "api", "glab mr view": "api", "glab issue view": "api", "gh api": "api", "gh api repos": "api",
        "glab api": "api", "glab api projects": "api"}
STOP_BASE = {"readme.md", "index.html", "package.json", "styles.css", "style.css", "script.js", "main.js", "app.js",
             "index.js", "license", "license.md", ".gitignore", "config.json", "data.json", "makefile", "index.md",
             "changelog.md", "requirements.txt", "package-lock.json", "contributing.md", "readme.txt", "notes.md"}
REF_PREFIX = re.compile(r"^(?:(?:refs/)?heads|blob|tree|raw|-/blob|-/raw|-/tree)/[^/]+/")
TOKEN = re.compile(r"[A-Za-z0-9_.\-/]{3,200}")


def h64(s: str) -> int:
    return int.from_bytes(hashlib.blake2b(s.encode("utf-8", "replace"), digest_size=8).digest(), "little", signed=True)


def norm_path(p: str) -> str:
    p = p.strip().strip("'\"`").lstrip("./")
    return REF_PREFIX.sub("", p)


def base_of(p: str) -> str:
    return p.rsplit("/", 1)[-1].lower()


def hold_days() -> set:
    cal = C.calendar()
    return set(cal.filter(pl.col("hold"))["pt_date"].to_list())


def pt_date(col: str = "t") -> pl.Expr:
    return pl.col(col).dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.Utf8)


def repo_ids() -> dict:
    a = pl.read_parquet(SH / "artifacts.parquet", columns=["artifact", "kind", "name"])
    r = a.filter(pl.col("kind").cast(pl.Utf8) == "repo")
    return dict(zip(r["name"].to_list(), r["artifact"].to_list()))


# ============================================================================================ files
def build_files():
    t_a = time.time()
    hd = hold_days()
    wc = (pl.read_parquet(SH / "work_commits.parquet",
                          columns=["repo", "hash", "t", "pt_date", "author_agent", "author_kind", "automated", "holdout"])
          .with_columns(pl.col("repo").cast(pl.Utf8))
          .filter((pl.col("t") >= T_START) & (pl.col("author_kind").cast(pl.Utf8) == "agent") & ~pl.col("automated")
                  & ~pl.col("holdout") & ~pl.col("pt_date").is_in(list(hd))))
    rid = repo_ids()
    repos = sorted(wc["repo"].unique().to_list())
    want = {(r, h) for r, h in zip(wc["repo"].to_list(), wc["hash"].to_list())}
    rows = []
    n_nofile = 0
    env = dict(os.environ, GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1", GIT_TERMINAL_PROMPT="0", GIT_NO_LAZY_FETCH="1")
    for r in repos:
        gd = REPOS / f"{r}.git"
        if not gd.exists():
            continue
        cmd = ["git", f"--git-dir={gd}", "log", "--all", "--no-renames", "--name-only", "--format=C\t%H",
               "--since=2026-02-24", "--until=2026-09-08"]
        p = subprocess.run(cmd, capture_output=True, text=True, env=env, errors="replace")
        cur = None
        for line in p.stdout.splitlines():
            if line.startswith("C\t"):
                h = line[2:].strip()
                cur = h if (r, h) in want else None
                continue
            if cur is None or not line.strip():
                continue
            path = norm_path(line)
            b = base_of(path)
            rows.append((rid[r], cur, h64(path), h64(b), len(b) >= 8 and b not in STOP_BASE))
        if p.returncode != 0:
            n_nofile += 1
    cf = pl.DataFrame(rows, schema={"repo": pl.Int32, "hash": pl.Utf8, "path_hash": pl.Int64, "base_hash": pl.Int64,
                                    "base_ok": pl.Boolean}, orient="row").unique()
    meta = wc.select(pl.col("repo").replace_strict(rid, return_dtype=pl.Int32).alias("repo"), "hash", C.ts("t").alias("t"),
                     pl.col("author_agent").cast(pl.Int16).alias("author_agent")).unique(["repo", "hash"])
    cf = cf.join(meta, on=["repo", "hash"], how="inner")
    # commits with no file list (commits-only clone or merge without diff) still count at repo level
    nof = meta.join(cf.select("repo", "hash").unique(), on=["repo", "hash"], how="anti").with_columns(
        pl.lit(None, pl.Int64).alias("path_hash"), pl.lit(None, pl.Int64).alias("base_hash"),
        pl.lit(False).alias("base_ok"))
    cf = pl.concat([cf, nof.select(cf.columns)]).sort("t")
    OUT.mkdir(parents=True, exist_ok=True)
    cf.write_parquet(OUT / "commit_files.parquet", compression="zstd")
    # pushes / deploys (source writes that are not commits)
    am = load_mentions(hd)
    wp = am.filter(pl.col("verb").is_in(["git push", "deploy"]) & pl.col("kind").is_in(["repo", "site", "file"])) \
        .select("agent", "t", "artifact", "kind")
    wp.write_parquet(OUT / "writes_push.parquet", compression="zstd")
    print(f"files: {len(repos)} repos, {meta.height} commits, {cf.height} rows ({nof.height} without file list), "
          f"{wp.height} push/deploy rows, git errors {n_nofile}, {time.time() - t_a:.0f}s", flush=True)
    prov("files", ["shared/work_commits", "raw/repos (git log --name-only)", "shared/artifact_mentions", "shared/artifacts"],
         {"since": "2026-02-25", "paths": "blake2b-64 hashed", "stop_basenames": sorted(STOP_BASE)})


def load_mentions(hd: set) -> pl.DataFrame:
    art = pl.read_parquet(SH / "artifacts.parquet", columns=["artifact", "kind", "name", "parent"]).with_columns(
        pl.col("kind").cast(pl.Utf8))
    am = (pl.scan_parquet(SH / "artifact_mentions.parquet")
          .filter((pl.col("t") >= T_START) & (pl.col("source").cast(pl.Utf8) == "action") & pl.col("agent").is_not_null())
          .select("artifact", "t", "agent", pl.col("how").cast(pl.Utf8).alias("how"),
                  pl.col("verb").cast(pl.Utf8).alias("verb"), "ref_index")
          .collect())
    am = am.with_columns(pt_date("t").alias("pt")).filter(~pl.col("pt").is_in(list(hd)))
    am = am.join(art, on="artifact", how="left")
    return am.with_columns(C.ts("t").alias("t"))


# ============================================================================================ reads
def build_reads():
    t_a = time.time()
    hd = hold_days()
    am = load_mentions(hd)
    rid = repo_ids()
    rd = am.filter(pl.col("how").is_in(["url", "output", "bare", "cwd"])
                   & (pl.col("verb").is_in(READ_VERBS) | (pl.col("verb").is_null() & (pl.col("how") == "url")))
                   & pl.col("kind").is_in(["repo", "site", "file"]))
    rd = rd.filter(~((pl.col("how") == "cwd") & ~pl.col("verb").is_in(["git pull", "git fetch", "git log", "git show"])))
    # repo of the artifact: repo itself; site/file -> parent; github/gitlab file names "<repo>:<path>"
    names = rd["name"].to_list()
    kinds = rd["kind"].to_list()
    parents = rd["parent"].to_list()
    arts = rd["artifact"].to_list()
    repo, ph = [], []
    for n, k, p, a in zip(names, kinds, parents, arts):
        if k == "repo":
            repo.append(a)
            ph.append(None)
        elif k == "file":
            if n and ":" in n and (n.startswith("github.com/") or n.startswith("gitlab.com/")):
                rn, path = n.split(":", 1)
                repo.append(rid.get(rn, p))
                ph.append(h64(norm_path(path)))
            else:
                repo.append(p)
                ph.append(None)
        else:
            repo.append(p)
            ph.append(None)
    rd = rd.with_columns(pl.Series("repo", repo, dtype=pl.Int32), pl.Series("path_hash", ph, dtype=pl.Int64),
                         pl.when(pl.col("verb").is_null()).then(pl.lit("page"))
                         .otherwise(pl.col("verb").replace_strict(CHAN, default="api")).alias("chan"))
    rd = rd.with_columns(pl.when((pl.col("kind") == "file") & (pl.col("chan") == "page")).then(pl.lit("file"))
                         .otherwise(pl.col("chan")).alias("chan"))
    rd = rd.select(pl.col("agent").cast(pl.Int16), "t", "artifact", "kind", "verb", "how", "chan", "repo", "path_hash",
                   "ref_index").sort("agent", "t")
    OUT.mkdir(parents=True, exist_ok=True)
    rd.write_parquet(OUT / "reads.parquet", compression="zstd")
    print(f"reads: {rd.height} rows; by channel {dict(rd.group_by('chan').len().iter_rows())}, {time.time() - t_a:.0f}s",
          flush=True)
    prov("reads", ["shared/artifact_mentions", "shared/artifacts", "shared/calendar"],
         {"read_verbs": READ_VERBS, "how": ["url", "output", "bare", "cwd (git pull/fetch/log/show only)"],
          "page_visit": "null verb with how=url", "kinds": ["repo", "site", "file"]})


# ============================================================================================ local reads
def build_local():
    t_a = time.time()
    hd = hold_days()
    cf = pl.read_parquet(OUT / "commit_files.parquet").filter(pl.col("path_hash").is_not_null())
    pset = set(zip(cf["repo"].to_list(), cf["path_hash"].to_list()))
    bset = set(zip(cf.filter(pl.col("base_ok"))["repo"].to_list(), cf.filter(pl.col("base_ok"))["base_hash"].to_list()))
    repos_with_files = set(cf["repo"].unique().to_list())
    # working-directory repo of each command row
    cw = (pl.scan_parquet(SH / "artifact_mentions.parquet")
          .filter((pl.col("t") >= T_START) & (pl.col("source").cast(pl.Utf8) == "action")
                  & (pl.col("how").cast(pl.Utf8) == "cwd"))
          .select(pl.col("ref_index").alias("row"), "artifact").collect())
    art = pl.read_parquet(SH / "artifacts.parquet", columns=["artifact", "kind", "parent"]).with_columns(
        pl.col("kind").cast(pl.Utf8))
    cw = cw.join(art, on="artifact", how="left").with_columns(
        pl.when(pl.col("kind") == "repo").then(pl.col("artifact")).otherwise(pl.col("parent")).alias("repo"))
    cw = cw.filter(pl.col("repo").is_in(list(repos_with_files))).select(pl.col("row").cast(pl.UInt32), "repo").unique("row")
    cmd = (pl.scan_parquet(SH / "artifact_commands_text.parquet")
           .filter((pl.col("t") >= T_START) & pl.col("cmd").is_not_null())
           .select("row", "t", "agent", "cmd").collect())
    cmd = cmd.with_columns(pt_date("t").alias("pt")).filter(~pl.col("pt").is_in(list(hd)))
    cmd = cmd.join(cw, on="row", how="inner")
    out = []
    for row, t, a, c, r in zip(cmd["row"].to_list(), cmd["t"].to_list(), cmd["agent"].to_list(), cmd["cmd"].to_list(),
                               cmd["repo"].to_list()):
        seen = set()
        for tok in TOKEN.findall(c):
            p = norm_path(tok)
            if not p or p in seen:
                continue
            seen.add(p)
            hp = h64(p)
            if (r, hp) in pset:
                out.append((a, t, r, hp, "path"))
                continue
            b = base_of(p)
            if len(b) >= 8 and b not in STOP_BASE:
                hb = h64(b)
                if (r, hb) in bset:
                    out.append((a, t, r, hb, "base"))
    del cmd
    lr = pl.DataFrame(out, schema={"agent": pl.Int16, "t": pl.Datetime("us", "UTC"), "repo": pl.Int32,
                                   "path_hash": pl.Int64, "match": pl.Utf8}, orient="row")
    lr = lr.with_columns(C.ts("t").alias("t")).sort("agent", "t")
    lr.write_parquet(OUT / "local_reads.parquet", compression="zstd")
    print(f"local reads: {lr.height} rows ({int((lr['match'] == 'path').sum())} full path), {time.time() - t_a:.0f}s",
          flush=True)
    prov("local", ["shared/artifact_commands_text (in memory)", "shared/artifact_mentions (cwd)", "r2/tables/commit_files"],
         {"token": TOKEN.pattern, "basename_min_len": 8, "stop_basenames": sorted(STOP_BASE)})


def prov(name, tables, params):
    p = C.OUT / "_provenance.json"
    pr = json.loads(p.read_text()) if p.exists() else {}
    pr[f"r2_{name}"] = {"built_by": f"hypotheses/H41-readout-light-cone/scheme/build_r2.py {name}", "git_commit": git_commit(),
                        "inputs": [{"source": "ai-village", "revision": REVISION, "tables": tables}], "params": params,
                        "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    p.write_text(json.dumps(pr, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["files", "reads", "local", "all"])
    a = ap.parse_args()
    if a.step in ("files", "all"):
        build_files()
    if a.step in ("reads", "all"):
        build_reads()
    if a.step in ("local", "all"):
        build_local()


if __name__ == "__main__":
    main()
