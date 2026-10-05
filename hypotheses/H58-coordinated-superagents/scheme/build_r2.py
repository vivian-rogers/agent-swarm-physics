"""H58 round-2 scheme: file-level commit lists (R2) and the erasure re-acquisition file codes (R3).

Card: hypotheses/H58-coordinated-superagents/README.md, "Round 2 design" (R2, R3). Reads round 1's panels
(data/processed/H58-coordinated-superagents/: units.json, commits.parquet, repos.parquet, erasures.parquet), the bare
clones (read-only `git log --all --name-only`), `calls`, `turn_outcomes` (command text parsed in memory; only codes and
hashed file keys are stored). Non-reserved days only (asserted). Writes data/processed/H58-coordinated-superagents/r2/:

  file_map.parquet    file_id -> (repo_id, path)                       [paths of repository files, not agent text]
  file_commits.parquet  repo_id, hash, t_git (commit time), file_id      [every commit in the clone's history]
  files_shared.parquet  R2 panels: unit, repo_id, agent, day, m, hash, file_id (agent work commits on eligible shared
                      repos; commits touching > 20 files dropped)
  r3_events.parquet   R3: one row per erasure / placebo event with k_pre: etype, agent, unit, day, t_call, S (first
                      re-read file code), first_read_call, X (outcome code), V, V_pre, open_own, open_oth, open_goal,
                      r1_read, X_is_r1, has_commit, plus X coded against a time-shifted artifact state (X_shift)
Codes: 0 r1, 1 r2, 2 r3, 3 r45, 4 own-old, 5 oth (a file of A the agent never committed), 6 xrepo, 7 none.
Run: uv run python hypotheses/H58-coordinated-superagents/scheme/build_r2.py
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ[_v] = "2"

import datetime as dt  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
SH = ROOT / "data/processed/shared"
D = ROOT / "data/processed/H58-coordinated-superagents"
OUT = D / "r2"
REPOS = ROOT / "data/raw/repos"
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import git_commit, holdout_mask  # noqa: E402

REVISION = "838b4150303ca8228e8edb432d8b8ccae353d258"
R2_UNITS = ["38a", "38b", "38c", "51a", "51b", "51c", "51d", "51e", "39", "40", "41", "44"]
BULK_FILES = 20
MIN_WRITER_COMMITS, MIN_REPO_COMMITS = 3, 30
READ_VERBS = {"cat", "head", "tail", "less", "more", "sed", "grep", "rg", "egrep", "fgrep", "wc", "diff", "ls", "find",
              "nl", "awk", "stat", "file", "tree", "jq", "view", "bat"}
GIT_READ = {"show", "diff", "log", "blame", "grep", "ls-files", "cat-file"}
GOAL_RX = re.compile(r"(readme|todo|task|plan|roadmap|status|handoff|goal|agenda|backlog|contributing|coordination|"
                     r"claim|assign)", re.I)
TOKEN_RX = re.compile(r"(?<![\w@:])((?:[\w.\-~]+/)*[\w.\-]+\.[A-Za-z][A-Za-z0-9]{0,6}|(?:[\w.\-]+/)+[\w.\-]+)")
CODES = ["r1", "r2", "r3", "r45", "own_old", "oth", "xrepo", "none"]
C_XREPO, C_NONE, C_OTH = 6, 7, 5
ENV = dict(os.environ, GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1", GIT_TERMINAL_PROMPT="0")


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def guard_days(days):
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "goal_no"])
    g = pl.DataFrame({"pt_date": list(days)}).join(cal, on="pt_date", how="left")
    assert not any(holdout_mask(g["pt_date"].to_list(), g["goal_no"].to_list())), "reserved days present"


def git_files(repo: str):
    """hash -> (commit time UTC seconds, [paths]) for the clone's whole history (read-only)."""
    p = REPOS / f"{repo}.git"
    if not p.is_dir():
        return {}
    txt = subprocess.run(["git", "-C", str(p), "log", "--all", "--name-only", "--format=C %H %ct"],
                         capture_output=True, text=True, env=ENV, errors="replace").stdout
    out, cur = {}, None
    for line in txt.splitlines():
        if line.startswith("C "):
            parts = line[2:].split()
            cur = parts[0]
            out[cur] = (int(parts[1]) if len(parts) > 1 else 0, [])
        elif line.strip() and cur:
            out[cur][1].append(line.strip())
    return out


def last2(path: str) -> str:
    parts = [x for x in path.strip("/").split("/") if x not in (".", "")]
    return "/".join(parts[-2:]).lower()


def base(path: str) -> str:
    return path.strip("/").split("/")[-1].lower()


# ============================================================================ R2 + file history
def build_file_tables(units, commits, repos, r3_repos):
    shared = (commits.filter(pl.col("unit").is_in(R2_UNITS)).group_by("unit", "repo_id", "agent").len()
              .filter(pl.col("len") >= MIN_WRITER_COMMITS).group_by("unit", "repo_id")
              .agg(pl.len().alias("nw")).filter(pl.col("nw") >= 2))
    tot = commits.group_by("unit", "repo_id").len().rename({"len": "nc"})
    shared = shared.join(tot, on=["unit", "repo_id"]).filter(pl.col("nc") >= MIN_REPO_COMMITS)
    need = sorted(set(shared["repo_id"].to_list()) | set(r3_repos))
    rname = dict(repos.select("repo_id", "repo").iter_rows())
    fmap, frows = {}, []
    hist = {}
    for i, rid in enumerate(need):
        gf = git_files(rname[rid])
        hist[rid] = gf
        for h, (ct, paths) in gf.items():
            for pth in paths:
                key = (rid, pth)
                if key not in fmap:
                    fmap[key] = len(fmap)
                frows.append((rid, h, ct, fmap[key]))
        if i % 50 == 0:
            log(f"git log {i}/{len(need)} repos, {len(frows)} file rows")
    file_map = pl.DataFrame([(v, k[0], k[1]) for k, v in fmap.items()], schema=["file_id", "repo_id", "path"],
                            orient="row").with_columns(pl.col("file_id").cast(pl.Int32), pl.col("repo_id").cast(pl.Int32))
    fc = pl.DataFrame(frows, schema=["repo_id", "hash", "t_git", "file_id"], orient="row").with_columns(
        pl.col("repo_id").cast(pl.Int32), pl.col("file_id").cast(pl.Int32), pl.col("t_git").cast(pl.Int64))
    # R2 panels: agent work commits on eligible shared repos, file level, bulk commits dropped
    cs = commits.join(shared.select("unit", "repo_id"), on=["unit", "repo_id"], how="semi")
    nfile = fc.group_by("repo_id", "hash").len().rename({"len": "nf"})
    cs = cs.join(nfile, on=["repo_id", "hash"], how="left").filter(pl.col("nf").is_not_null() & (pl.col("nf") <= BULK_FILES))
    fs = cs.join(fc.select("repo_id", "hash", "file_id"), on=["repo_id", "hash"], how="inner") \
        .select("unit", "repo_id", "agent", "day", "m", "hash", "file_id")
    return file_map, fc, fs, shared, hist


# ============================================================================ R3
def parse_cmd(cmd: str):
    """(is_read_verb, tokens) from one command string; comment lines and quoted heredoc bodies are not special-cased."""
    if not cmd:
        return False, []
    simple = re.split(r"\s*(?:&&|\|\||;|\|)\s*", cmd)
    read = False
    for sc in simple:
        w = sc.strip().split()
        while w and ("=" in w[0] and not w[0].startswith("-")) or (w and w[0] in ("sudo", "time", "env")):
            w = w[1:]
        if not w:
            continue
        v = w[0].split("/")[-1]
        if v in READ_VERBS or (v == "git" and len(w) > 1 and w[1] in GIT_READ) or \
                (v == "sed" and "-n" in w) or (v in ("python", "python3") and False):
            read = True
    toks = []
    for m in TOKEN_RX.finditer(cmd):
        t = m.group(1)
        if "://" in cmd[max(0, m.start() - 8):m.start() + 3] or t.startswith("http"):
            continue
        toks.append(t)
    return read, toks


def build_r3(units, commits, hist, repos):
    meta = {x["unit"]: x for x in units}
    E = pl.read_parquet(D / "erasures.parquet").filter(pl.col("k_pre").is_not_null())
    guard_days(E["pt_date"].unique().to_list())
    days = E["pt_date"].unique().to_list()
    calls = pl.scan_parquet(SH / "calls.parquet").filter(pl.col("pt_date").is_in(days) & ~pl.col("holdout")) \
        .select("turn_id", "agent", "pt_date", "t_call", "seq", "is_reset", "n_work").collect().sort("agent", "t_call")
    calls = calls.with_columns(pl.col("agent").cast(pl.Int64))
    ev = E.join(calls.select("turn_id", "seq", "t_call"), on="turn_id", how="inner")
    log(f"events with k_pre: {ev.height}")
    # action rows of these agent-days mapped to calls (latest call at or before the row)
    t0 = calls["t_call"].min()
    t1 = calls["t_call"].max() + dt.timedelta(hours=1)
    to = pl.scan_parquet(ROOT / "data/processed/behavior_states/turn_outcomes.parquet") \
        .filter((pl.col("t") >= t0) & (pl.col("t") <= t1)) \
        .select("t", "agent", "act", "file_write", "commit_ok", "push_ok", "cmd").collect() \
        .with_columns(pl.col("agent").cast(pl.Int64)).sort("agent", "t")
    to = to.join_asof(calls.select("agent", "t_call", "pt_date", "seq"), left_on="t", right_on="t_call", by="agent",
                      strategy="backward")
    to = to.filter(pl.col("seq").is_not_null())
    # keep rows in calls 1-10 of some event: (agent, pt_date, seq) within [seq_e, seq_e + 9]
    win = ev.select("agent", "pt_date", "seq").with_columns(pl.int_ranges(pl.col("seq"), pl.col("seq") + 10).alias("s")) \
        .explode("s").select("agent", "pt_date", pl.col("s").cast(pl.Int32).alias("seq")).unique()
    to = to.join(win, on=["agent", "pt_date", "seq"], how="semi")
    log(f"action rows in event windows: {to.height}")
    reads = {}
    for (a, d, s, act, fw, co, pu, cmd) in to.select("agent", "pt_date", "seq", "act", "file_write", "commit_ok",
                                                    "push_ok", "cmd").iter_rows():
        if act != "bash" or fw or co or pu:
            continue
        rd, toks = parse_cmd(cmd or "")
        if rd and toks:
            reads.setdefault((a, d, s), []).extend(toks)
    log(f"read calls with tokens: {len(reads)}")
    # per-repo file index: last2 -> path set, basename -> path set, and commit times
    cm = commits.select("agent", "repo_id", "hash", "t").sort("agent", "t")
    by_agent_commits = {a: g for (a,), g in cm.partition_by("agent", as_dict=True).items()}
    calls_by = {k: g for k, g in calls.partition_by(["agent", "pt_date"], as_dict=True).items()}
    rows = []
    idx_cache = {}

    def repo_index(rid):
        if rid not in idx_cache:
            gf = hist.get(rid, {})
            l2, bs, first_t = {}, {}, {}
            for h, (ct, paths) in gf.items():
                for p in paths:
                    l2.setdefault(last2(p), set()).add(p)
                    bs.setdefault(base(p), set()).add(p)
                    first_t[p] = min(first_t.get(p, ct), ct)
            idx_cache[rid] = (l2, bs, first_t)
        return idx_cache[rid]

    def agent_ranks(a, rid, t_e):
        """path -> code (0..4) from the agent's own commits on repo rid before t_e (commit-recency rank)."""
        C = by_agent_commits.get(a)
        if C is None:
            return {}
        cc = C.filter((pl.col("repo_id") == rid) & (pl.col("t") < t_e)).sort("t", descending=True)
        gf = hist.get(rid, {})
        ranks = {}
        for i, h in enumerate(cc["hash"].to_list()):
            code = 0 if i == 0 else 1 if i == 1 else 2 if i == 2 else 3 if i <= 4 else 4
            for p in gf.get(h, (0, []))[1]:
                ranks.setdefault(p, code)
        return ranks

    def code_of(path, ranks, rid_known=True):
        if path is None:
            return C_NONE
        return ranks.get(path, C_OTH)

    def match(tok, rid, t_e_s):
        l2, bs, first_t = repo_index(rid)
        cand = l2.get(last2(tok))
        if not cand:
            b = bs.get(base(tok))
            cand = b if (b and len(b) == 1) else None
        if not cand:
            return None
        cand = [p for p in cand if first_t.get(p, 0) <= t_e_s]
        return sorted(cand)[0] if cand else None

    for r in ev.iter_rows(named=True):
        a, d, s0, t_e, A = r["agent"], r["pt_date"], r["seq"], r["t_call"], r["k_pre"]
        t_e_s = int(t_e.timestamp())
        ranks = agent_ranks(a, A, t_e)
        if not ranks:
            continue
        cday = calls_by.get((a, d))
        seqs = cday["seq"].to_numpy()
        tcs = cday["t_call"].to_list()
        isr = cday["is_reset"].to_numpy()
        nw = cday["n_work"].to_numpy()
        i0 = int(np.searchsorted(seqs, s0))
        # window: calls 1..20 truncated at the next reset
        j = i0 + 1
        while j < len(seqs) and j < i0 + 20 and not isr[j]:
            j += 1
        i_end = j                                                    # exclusive
        n_win = i_end - i0
        V = float(nw[i0:i_end].sum()) * (20.0 / n_win if n_win < 20 else 1.0) if n_win >= 10 else np.nan
        V_pre = float(nw[max(0, i0 - 20):i0].sum())
        t_end = tcs[i_end] if i_end < len(tcs) else tcs[-1] + dt.timedelta(minutes=5)
        t_end = min(t_end, t_e + dt.timedelta(minutes=30))
        # re-read pointer: first file of A read in calls 1-10 (before the window end)
        S, first_call, goal = C_NONE, -1, False
        read_paths = set()
        for q in range(i0, min(i0 + 10, i_end)):
            toks = reads.get((a, d, int(seqs[q])), [])
            for tk in toks:
                if GOAL_RX.search(base(tk)):
                    goal = True
                pth = match(tk, A, t_e_s)
                if pth is not None:
                    read_paths.add(pth)
                    if S == C_NONE:
                        S = code_of(pth, ranks)
                        first_call = q - i0 + 1
        # outcome: first work commit of the agent in (t_e, t_end)
        C = by_agent_commits.get(a)
        X = C_NONE
        if C is not None:
            nx = C.filter((pl.col("t") >= t_e) & (pl.col("t") < t_end)).head(1)
            if nx.height:
                rid, h = int(nx["repo_id"][0]), nx["hash"][0]
                if rid != A:
                    X = C_XREPO
                else:
                    paths = hist.get(A, {}).get(h, (0, []))[1]
                    X = min([code_of(p, ranks) for p in paths], default=C_OTH)
        r1_paths = {p for p, c in ranks.items() if c == 0}
        rows.append({"etype": r["etype"], "agent": a, "unit": r["unit"], "day": r["day"], "pt_date": d,
                     "t_call": t_e, "k_pre": A, "S": S, "first_read_call": first_call, "X": X, "V": V, "V_pre": V_pre,
                     "n_win": n_win, "open_own": S <= 4, "open_oth": S == C_OTH, "open_goal": goal,
                     "r1_read": bool(read_paths & r1_paths), "n_read_A": len(read_paths)})
    out = pl.DataFrame(rows)
    log(f"R3 events coded: {out.height}")
    # time-shifted artifact state: X re-coded against the same agent's ranks at another event >= 1 day away (same unit)
    out = out.with_row_index("eid")
    xs = []
    rng = np.random.default_rng(58)
    groups = {k: g for k, g in out.partition_by(["agent", "unit"], as_dict=True).items()}
    # outcome paths are needed for re-coding: recompute the first-commit paths per event
    first_paths = {}
    for r in out.iter_rows(named=True):
        C = by_agent_commits.get(r["agent"])
        if C is None or r["X"] in (C_NONE, C_XREPO):
            continue
        nx = C.filter(pl.col("t") >= r["t_call"]).head(1)
        if nx.height and int(nx["repo_id"][0]) == r["k_pre"]:
            first_paths[r["eid"]] = hist.get(r["k_pre"], {}).get(nx["hash"][0], (0, []))[1]
    for (a, u), g in groups.items():
        for r in g.iter_rows(named=True):
            if r["X"] in (C_NONE, C_XREPO):
                xs.append((r["eid"], r["X"]))
                continue
            far = g.filter((pl.col("pt_date") != r["pt_date"]) & (pl.col("k_pre") == r["k_pre"]))
            if far.height == 0:
                xs.append((r["eid"], None))
                continue
            o = far.row(int(rng.integers(far.height)), named=True)
            rk = agent_ranks(a, r["k_pre"], o["t_call"])
            paths = first_paths.get(r["eid"], [])
            xs.append((r["eid"], min([rk.get(p, C_OTH) for p in paths], default=C_OTH) if rk else None))
    out = out.join(pl.DataFrame(xs, schema=["eid", "X_shift"], orient="row"), on="eid", how="left")
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    units = json.loads((D / "units.json").read_text())
    for x in units:
        assert not any(holdout_mask(x["days"], [x["goal_no"]] * len(x["days"]))), x["unit"]
    commits = pl.read_parquet(D / "commits.parquet")
    guard_days(commits["pt_date"].unique().to_list())
    # commit times for R3 (shared work_commits t; same filter as round 1)
    wc = pl.read_parquet(SH / "work_commits.parquet", columns=["hash", "t"]).unique("hash")
    commits = commits.join(wc, on="hash", how="left").with_columns(pl.col("agent").cast(pl.Int64))
    repos = pl.read_parquet(D / "repos.parquet")
    E = pl.read_parquet(D / "erasures.parquet").filter(pl.col("k_pre").is_not_null())
    r3_repos = E["k_pre"].unique().to_list()
    file_map, fc, fs, shared, hist = build_file_tables(units, commits, repos, r3_repos)
    file_map.write_parquet(OUT / "file_map.parquet", compression="zstd")
    fc.write_parquet(OUT / "file_commits.parquet", compression="zstd")
    fs.write_parquet(OUT / "files_shared.parquet", compression="zstd")
    shared.write_parquet(OUT / "shared_repos.parquet", compression="zstd")
    log(f"files: {file_map.height} files, {fc.height} file-commit rows, R2 rows {fs.height}, shared repos {shared.height}")
    r3 = build_r3(units, commits, hist, repos)
    r3.write_parquet(OUT / "r3_events.parquet", compression="zstd")
    prov = {"built_by": "hypotheses/H58-coordinated-superagents/scheme/build_r2.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["H58 round-1 panels (units.json, commits.parquet, repos.parquet, erasures.parquet)",
                                   "work_commits (t)", "calls", "calendar",
                                   "behavior_states/turn_outcomes (cmd parsed in memory; not stored)",
                                   "data/raw/repos bare clones (read-only git log --all --name-only)"]}],
            "params": {"R2_units": R2_UNITS, "bulk_files": BULK_FILES, "min_writer_commits": MIN_WRITER_COMMITS,
                       "min_repo_commits": MIN_REPO_COMMITS, "codes": CODES, "read_verbs": sorted(READ_VERBS),
                       "git_read": sorted(GIT_READ), "goal_regex": GOAL_RX.pattern,
                       "window": "calls 1-20 (truncated at the next reset, >= 10 calls for V); reads in calls 1-10; "
                                 "outcome = first work commit before the window end (<= 30 min)"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))
    log("done")


if __name__ == "__main__":
    main()
