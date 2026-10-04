"""Work-output ledger: what the swarm actually produced, from the public git histories of the agents' repos.

Stages (run in order; `all` runs every stage):

  inventory  every repo the agents worked in, from the artifacts tables (no network). Tiers:
               org            github.com/ai-village-agents/* and gitlab.com/ai-village-agents/village/*
                              (`gitlab.com/village/<p>` refs are read as the agents' group; see REMAP)
               agent_account  repos owned by an agent's own account (owner name contains a roster name; o3-ux)
               other_write    any other repo with >= 1 strict write mention by an agent (push/commit/PR/MR/
                              repo create/deploy with how in url, output or bare)
             -> data/processed/shared/work_repos.parquet (rewritten by `fetch` with the fetch results)
  fetch      read-only, unauthenticated `git ls-remote` + `git clone --bare` into data/raw/repos/<host>/<path>.git.
             Size guard per repo: full clone (blobs, for line stats) up to FULL_MAX; else blobless (files, no
             line stats) up to PARTIAL_MAX; else commits only (tree:0); else skipped. Global cap TOTAL_CAP.
             Git runs with the user's global/system config disabled, no credential helper, no prompts.
  extract    `git log --all --source` per clone -> scratch per-commit records (numstat / name-only / none).
             Commit messages are read only to derive length and flags; never stored.
  build      work_commits.parquet, work_api_writes.parquet, work_daily.parquet, work_outcomes.parquet
  validate   out_hashes agreement, coverage per period, gaps -> work_ledger_validation.json

Usage:
  uv run python infra/shared/work_ledger.py                 offline: extract + build + validate (what build_all runs)
  uv run python infra/shared/work_ledger.py refresh         network: inventory + fetch + upgrade, then the offline stages
  uv run python infra/shared/work_ledger.py <stage> ...     any of inventory fetch upgrade extract build validate
Scratch (author e-mails and file paths, never written to data/): $DQ4_SCRATCH or <tmpdir>/dq4_work_ledger.
Docs: infra/data-quality/work_ledger.md
"""
from __future__ import annotations

import concurrent.futures as cf
import datetime as dt
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUT, PT, ROOT, UTC, git_commit, holdout_mask, load_goals, short_hash  # noqa: E402

REPOS = ROOT / "data/raw/repos"
SCRATCH = Path(os.environ.get("DQ4_SCRATCH") or Path(__import__("tempfile").gettempdir()) / "dq4_work_ledger")
FETCH_LOG = SCRATCH / "dq4_fetch_log.jsonl"
INV_SCRATCH = SCRATCH / "dq4_inventory.parquet"  # inventory stage output; build merges it into work_repos.parquet
EXTRACT_DIR = SCRATCH / "dq4_extract"
INV = OUT / "work_repos.parquet"

FULL_MAX = 60e6        # bytes on disk for a full (blob-bearing) clone (the first 75 fetched used 120e6)
PARTIAL_MAX = 60e6     # blobless / commits-only clone
TOTAL_CAP = 1.9e9      # all new clones together (task cap 2 GB, minus margin)
CLONE_TIMEOUT = 900    # s per attempt
LS_WORKERS = 6         # network-bound
CLONE_WORKERS = 3      # network-bound; index-pack pinned to 1 thread each

AGENT_ORG = "ai-village-agents"
REMAP = {"gitlab.com/village/": "gitlab.com/ai-village-agents/village/"}
WRITE_VERBS = ["git push", "git commit", "gh repo create", "glab repo create", "gh pr create", "gh pr merge",
               "glab mr create", "glab mr merge", "deploy"]
STRICT_HOW = ["url", "output", "bare"]
NAME_OK = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
EXTRA_ACCOUNTS = {"o3-ux": "o3"}  # agent accounts whose name doesn't contain the roster name (checked: 70% of
                                  # pushes to o3-ux/* are by o3, the rest are collaborators on its repos)

# ----------------------------------------------------------------------------- git, safely


def git_env():
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1", GIT_TERMINAL_PROMPT="0",
               GIT_ASKPASS="/usr/bin/false", SSH_ASKPASS="/usr/bin/false", GIT_LFS_SKIP_SMUDGE="1",
               GCM_INTERACTIVE="never", LC_ALL="C")
    return env


GIT = ["git", "-c", "credential.helper=", "-c", "pack.threads=1", "-c", "index.threads=1",
       "-c", "core.askPass=/usr/bin/false", "-c", "protocol.version=2", "-c", "http.lowSpeedLimit=1000",
       "-c", "http.lowSpeedTime=60"]


def url_of(repo: str) -> str:
    return f"https://{repo}.git"


def clone_dir(repo: str) -> Path:
    return REPOS / f"{repo}.git"


def dir_size(p: Path) -> int:
    n = 0
    for dp, _, fs in os.walk(p):
        for f in fs:
            try:
                n += os.lstat(os.path.join(dp, f)).st_size
            except OSError:
                pass
    return n

# ----------------------------------------------------------------------------- roster / identity mapping


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def roster_keys():
    r = pl.read_parquet(OUT / "roster.parquet")
    keys = {}
    for ag, name, ms in r.select("agent", "name", "model_string").iter_rows():
        for k in {norm(name), norm(name.replace("[Temporary] ", "")), norm(ms.split("::")[-1])}:
            if k:
                keys.setdefault(k, ag)
    return keys, r


def account_owner_agent(owner: str, keys: dict):
    """Agent code for an agent-owned account name, by the longest roster key it contains (len >= 4)."""
    if owner in EXTRA_ACCOUNTS:
        return keys.get(norm(EXTRA_ACCOUNTS[owner]))
    k = norm(owner)
    hits = sorted((n for n in keys if len(n) >= 4 and n in k), key=len, reverse=True)
    return keys[hits[0]] if hits else None

# ----------------------------------------------------------------------------- inventory


def canonical_repo(name: str) -> str | None:
    for a, b in REMAP.items():
        if name.startswith(a):
            name = b + name[len(a):]
    parts = name.split("/")
    if len(parts) < 3 or not all(NAME_OK.match(p) for p in parts[1:]):
        return None
    if parts[0] == "github.com" and len(parts) != 3:
        return None
    if parts[-1].endswith((".git", ".")) or parts[-1] in ("-", "_"):
        return None
    return name


def inventory():
    keys, _ = roster_keys()
    a = pl.read_parquet(OUT / "artifacts.parquet").filter(pl.col("kind") == "repo").select(
        "artifact", "name", "host", "first_t", "first_agent", "last_t", "n_chat", "n_action", "n_agents")
    m = (pl.read_parquet(OUT / "artifact_mentions.parquet", columns=["artifact", "agent", "source", "how", "verb"])
         .filter(pl.col("source") == "action").join(a.select("artifact"), on="artifact")
         .with_columns(pl.col("verb").cast(pl.Utf8), pl.col("how").cast(pl.Utf8)))
    ev = m.group_by("artifact").agg(
        (pl.col("verb").is_in(WRITE_VERBS) & pl.col("how").is_in(STRICT_HOW)).sum().alias("n_write_strict"),
        pl.col("verb").is_in(WRITE_VERBS).sum().alias("n_write_any"),
        ((pl.col("verb") == "git push") & (pl.col("how") == "output")).sum().alias("n_push_output"),
        pl.col("verb").is_in(["git clone", "gh repo clone", "glab repo clone"]).sum().alias("n_clone"),
        pl.col("agent").filter(pl.col("verb").is_in(WRITE_VERBS)).drop_nulls().n_unique().alias("n_write_agents"))
    a = a.join(ev, on="artifact", how="left").with_columns(
        *[pl.col(c).fill_null(0).cast(pl.Int32) for c in ("n_write_strict", "n_write_any", "n_push_output",
                                                           "n_clone", "n_write_agents")])
    a = a.with_columns(pl.col("name").map_elements(canonical_repo, return_dtype=pl.Utf8).alias("repo"))
    bad = a.filter(pl.col("repo").is_null())
    a = a.filter(pl.col("repo").is_not_null())

    def tier(repo, n_action, n_strict):
        parts = repo.split("/")
        if (parts[0] == "github.com" and parts[1] == AGENT_ORG) or repo.startswith(f"gitlab.com/{AGENT_ORG}/village/"):
            return "org"
        if parts[0] == "gitlab.com" and parts[1] == AGENT_ORG:
            return "org"
        if account_owner_agent(parts[1], keys) is not None and (n_action > 0 or n_strict > 0):
            return "agent_account"
        if n_strict > 0:
            return "other_write"
        return None

    a = a.with_columns(pl.struct("repo", "n_action", "n_write_strict").map_elements(
        lambda s: tier(s["repo"], s["n_action"], s["n_write_strict"]), return_dtype=pl.Utf8).alias("tier"))
    inv = (a.filter(pl.col("tier").is_not_null())
           .group_by("repo").agg(
               pl.col("tier").first(), pl.col("host").first(),
               pl.col("artifact").sort().alias("artifacts"),
               pl.col("first_t").min(), pl.col("last_t").max(),
               pl.col("first_agent").sort_by("first_t").first(),
               *[pl.col(c).sum() for c in ("n_chat", "n_action", "n_write_strict", "n_write_any", "n_push_output",
                                           "n_clone")],
               pl.col("n_agents").max(), pl.col("n_write_agents").max())
           .with_columns(pl.col("repo").str.split("/").list.get(1).map_elements(
               lambda o: account_owner_agent(o, keys), return_dtype=pl.Int8).alias("account_agent"))
           # other_write needs a git-printed push remote or >= 3 strict write mentions; single mentions of big
           # third-party projects (e.g. `gh pr create --repo nodejs/node`) are listed but not fetched
           .with_columns(pl.when((pl.col("tier") != "other_write") | (pl.col("n_push_output") >= 1)
                                 | (pl.col("n_write_strict") >= 3))
                         .then(pl.lit("fetch")).otherwise(pl.lit("weak_evidence")).alias("fetch_plan"))
           .sort("repo"))
    SCRATCH.mkdir(parents=True, exist_ok=True)
    inv.write_parquet(INV_SCRATCH, compression="zstd")
    c = Counter(zip(inv["tier"].to_list(), inv["fetch_plan"].to_list()))
    return f"inventory: {inv.height} repos {dict(c)}; {bad.height} repo artifacts dropped as malformed names"

def load_inventory() -> pl.DataFrame:
    """Inventory columns: from the inventory stage's scratch output if present, else from work_repos.parquet."""
    return pl.read_parquet(INV_SCRATCH if INV_SCRATCH.exists() else INV).select(INV_COLS)


def _seed_fetch_log():
    """Without a scratch fetch log, start from the fetch results persisted in work_repos.parquet, so `fetch` only
    clones repos never attempted (it never re-clones over an existing one)."""
    if FETCH_LOG.exists() or not INV.exists():
        return
    inv = pl.read_parquet(INV)
    if "mode" not in inv.columns:
        return
    SCRATCH.mkdir(parents=True, exist_ok=True)
    done = inv.filter(pl.col("mode").is_not_null() & (pl.col("mode") != "not_attempted"))
    with open(FETCH_LOG, "w") as f:
        for r in done.select("repo", "exists", "mode", "bytes", "default_ref", "head_sha", "n_heads", "ls_error",
                             "clone_error", "attempts", "fetched_at").to_dicts():
            f.write(json.dumps(r) + "\n")


# ----------------------------------------------------------------------------- fetch


def ls_remote(repo: str) -> dict:
    t0 = time.time()
    try:
        r = subprocess.run(GIT + ["ls-remote", "--symref", url_of(repo)], capture_output=True, text=True,
                           timeout=90, env=git_env(), stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return {"repo": repo, "exists": False, "ls_error": "timeout", "ls_s": round(time.time() - t0, 1)}
    if r.returncode != 0:
        err = r.stderr.strip().splitlines()[-1][:160] if r.stderr.strip() else f"rc={r.returncode}"
        return {"repo": repo, "exists": False, "ls_error": err, "ls_s": round(time.time() - t0, 1)}
    head_ref, heads, head_sha = None, 0, None
    for line in r.stdout.splitlines():
        if line.startswith("ref: ") and line.endswith("\tHEAD"):
            head_ref = line[5:].split("\t")[0]
        elif line.endswith("\tHEAD"):
            head_sha = line.split("\t")[0]
        elif "\trefs/heads/" in line:
            heads += 1
    return {"repo": repo, "exists": heads > 0 or head_sha is not None, "empty": heads == 0, "default_ref": head_ref,
            "head_sha": head_sha, "n_heads": heads, "ls_s": round(time.time() - t0, 1),
            "ls_error": None if heads else "no branches (empty repo)"}


def _clone_once(repo: str, filt: str | None, limit: float) -> tuple[str, int, str | None]:
    """Run one clone attempt with a size watchdog. Returns (status, bytes, error)."""
    d = clone_dir(repo)
    if d.exists():
        shutil.rmtree(d)
    d.parent.mkdir(parents=True, exist_ok=True)
    cmd = GIT + ["clone", "--bare", "--quiet", "--no-tags"] + ([f"--filter={filt}"] if filt else []) + \
        [url_of(repo), str(d)]
    p = subprocess.Popen(cmd, env=git_env(), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                         stderr=subprocess.PIPE, text=True, start_new_session=True)
    t0 = time.time()
    while True:
        try:
            p.wait(timeout=2)
            break
        except subprocess.TimeoutExpired:
            pass
        size = dir_size(d) if d.exists() else 0
        if size > limit or time.time() - t0 > CLONE_TIMEOUT:
            os.killpg(p.pid, signal.SIGTERM)  # only our own clone's process group
            try:
                p.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(p.pid, signal.SIGKILL)
                p.wait()
            shutil.rmtree(d, ignore_errors=True)
            return ("too_large" if size > limit else "timeout"), size, None
    err = p.stderr.read().strip() if p.stderr else ""
    if p.returncode != 0:
        shutil.rmtree(d, ignore_errors=True)
        return "error", 0, (err.splitlines()[-1][:160] if err else f"rc={p.returncode}")
    size = dir_size(d)
    if size > limit:
        shutil.rmtree(d, ignore_errors=True)
        return "too_large", size, None
    return "ok", size, None


_USED = {"bytes": 0.0}  # finished clone bytes, shared by the fetch threads


def _budget(lim: float) -> float:
    """Per-attempt size limit: never more than an equal share of what is left of TOTAL_CAP, so clones in flight
    together cannot overshoot it."""
    return max(0.0, min(lim, (TOTAL_CAP - _USED["bytes"]) / CLONE_WORKERS))


def fetch_one(repo: str) -> dict:
    rec = ls_remote(repo)
    rec["fetched_at"] = dt.datetime.now(UTC).isoformat(timespec="seconds")
    if not rec["exists"] or rec.get("empty"):
        rec.update(mode="none", bytes=0)
        return rec
    tries = [("full", None, FULL_MAX), ("blobless", "blob:none", PARTIAL_MAX), ("commits_only", "tree:0", PARTIAL_MAX)]
    if TOTAL_CAP - _USED["bytes"] < 10 * FULL_MAX:
        tries = tries[1:]
    attempts = []
    for mode, filt, lim in tries:
        if _budget(lim) < 1e6:
            attempts.append(f"{mode}:no_budget")
            continue
        st, size, err = _clone_once(repo, filt, _budget(lim))
        attempts.append(f"{mode}:{st}" + (f"({size/1e6:.0f}MB)" if st == "too_large" else ""))
        if st == "ok":
            rec.update(mode=mode, bytes=size)
            break
        if st == "error":
            rec.update(mode="none", bytes=0, clone_error=err)
            break
    else:
        rec.update(mode="skipped_too_large", bytes=0)
    rec["attempts"] = ";".join(attempts)
    return rec


def fetch(only: list[str] | None = None):
    SCRATCH.mkdir(parents=True, exist_ok=True)
    _seed_fetch_log()
    inv = load_inventory()
    done = {}
    if FETCH_LOG.exists():
        for line in FETCH_LOG.read_text().splitlines():
            r = json.loads(line)
            done[r["repo"]] = r
    todo = [r for r, plan in inv.select("repo", "fetch_plan").iter_rows()
            if plan == "fetch" and r not in done and (only is None or r in only)]
    # org repos first (the swarm's own output), then agent accounts, then third-party repos
    order = {"org": 0, "agent_account": 1, "other_write": 2}
    tiers = dict(inv.select("repo", "tier").iter_rows())
    todo.sort(key=lambda r: (order[tiers[r]], r))
    used = sum(r.get("bytes", 0) for r in done.values())
    _USED["bytes"] = used
    print(f"fetch: {len(done)} already logged ({used/1e6:.0f} MB), {len(todo)} to do", flush=True)
    t0 = time.time()
    with open(FETCH_LOG, "a") as log, cf.ThreadPoolExecutor(CLONE_WORKERS) as ex:
        futs = {}
        it = iter(todo)

        def submit_next():
            r = next(it, None)
            if r is not None:
                futs[ex.submit(fetch_one, r)] = r
        for _ in range(CLONE_WORKERS * 2):
            submit_next()
        n = 0
        while futs:
            fin, _ = cf.wait(list(futs), return_when=cf.FIRST_COMPLETED)
            for f in fin:
                futs.pop(f)
                rec = f.result()
                used += rec.get("bytes", 0)
                _USED["bytes"] = used
                log.write(json.dumps(rec) + "\n")
                log.flush()
                n += 1
                if n % 50 == 0:
                    print(f"  {n}/{len(todo)}  {used/1e6:.0f} MB  {time.time()-t0:.0f}s", flush=True)
                submit_next()
    return f"fetch: total {used/1e6:.0f} MB in new clones, {time.time()-t0:.0f}s"


def upgrade(limit: float = 40e6):
    """Second pass: org / agent-account repos that went straight to blobless because the budget guard skipped the
    full attempt get a full clone (into a temp dir, swapped in only on success), within TOTAL_CAP."""
    _seed_fetch_log()
    inv = load_inventory()
    fr = fetch_results().join(inv.select("repo", "tier"), on="repo")
    cand = fr.filter((pl.col("mode") == "blobless") & (pl.col("attempts") == "blobless:ok")
                     & pl.col("tier").is_in(["org", "agent_account"])).sort("bytes")
    _USED["bytes"] = float(fr["bytes"].fill_null(0).sum())
    recs = {json.loads(x)["repo"]: json.loads(x) for x in FETCH_LOG.read_text().splitlines()}
    n_up = 0
    for repo, old_bytes in cand.select("repo", "bytes").iter_rows():
        room = TOTAL_CAP - _USED["bytes"] + old_bytes
        lim = min(limit, room)
        if lim < 5e6:
            break
        d = clone_dir(repo)
        tmp = d.with_name(d.name + ".dq4tmp")
        shutil.rmtree(tmp, ignore_errors=True)
        cmd = GIT + ["clone", "--bare", "--quiet", "--no-tags", url_of(repo), str(tmp)]
        p = subprocess.Popen(cmd, env=git_env(), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, start_new_session=True)
        t0, ok = time.time(), False
        while True:
            try:
                p.wait(timeout=2)
                ok = p.returncode == 0
                break
            except subprocess.TimeoutExpired:
                if (tmp.exists() and dir_size(tmp) > lim) or time.time() - t0 > CLONE_TIMEOUT:
                    os.killpg(p.pid, signal.SIGTERM)
                    p.wait()
                    break
        size = dir_size(tmp) if tmp.exists() else 0
        if ok and size <= lim:
            shutil.rmtree(d)
            tmp.rename(d)
            r = recs[repo]
            r.update(mode="full", bytes=size, attempts=r["attempts"] + ";upgrade_full:ok",
                     fetched_at=dt.datetime.now(UTC).isoformat(timespec="seconds"))
            _USED["bytes"] += size - old_bytes
            n_up += 1
            p_ = EXTRACT_DIR / f"{_safe(repo)}.parquet"
            if p_.exists():
                p_.unlink()  # re-extract with line stats
        else:
            shutil.rmtree(tmp, ignore_errors=True)
            recs[repo]["attempts"] += f";upgrade_full:too_large({size/1e6:.0f}MB)"
    FETCH_LOG.write_text("".join(json.dumps(r) + "\n" for r in recs.values()))
    return f"upgrade: {n_up}/{cand.height} upgraded to full; total {_USED['bytes']/1e6:.0f} MB"


def fetch_results() -> pl.DataFrame:
    """Fetch outcome per repo: from the scratch fetch log, else from the persisted work_repos.parquet."""
    if not FETCH_LOG.exists():
        inv = pl.read_parquet(INV)
        if "mode" not in inv.columns:
            raise FileNotFoundError(f"no fetch log at {FETCH_LOG} and {INV} has no fetch columns; run `fetch`")
        return inv.filter(pl.col("mode").is_not_null() & (pl.col("mode") != "not_attempted")).select(
            "repo", "exists", "mode", "bytes", "default_ref", "head_sha", "n_heads", "ls_error", "clone_error",
            "attempts", "fetched_at")
    recs = [json.loads(x) for x in FETCH_LOG.read_text().splitlines()]
    cols = ["repo", "exists", "mode", "bytes", "default_ref", "head_sha", "n_heads", "ls_error", "clone_error",
            "attempts", "fetched_at"]
    return pl.DataFrame([{c: r.get(c) for c in cols} for r in recs], schema={
        "repo": pl.Utf8, "exists": pl.Boolean, "mode": pl.Utf8, "bytes": pl.Int64, "default_ref": pl.Utf8,
        "head_sha": pl.Utf8, "n_heads": pl.Int32, "ls_error": pl.Utf8, "clone_error": pl.Utf8, "attempts": pl.Utf8,
        "fetched_at": pl.Utf8}).unique("repo", keep="last")


# ----------------------------------------------------------------------------- extract

FMT = "%x1e%H%x1f%P%x1f%ae%x1f%an%x1f%aI%x1f%ce%x1f%cn%x1f%cI%x1f%S%x1f%B%x1d"
EXT = {
    "web": {"html", "htm", "css", "scss", "sass", "less", "svg", "vue", "svelte", "astro", "ejs", "hbs"},
    "code": {"js", "mjs", "cjs", "ts", "tsx", "jsx", "py", "sh", "bash", "go", "rs", "java", "kt", "c", "h", "cc",
             "cpp", "hpp", "rb", "php", "gd", "lua", "swift", "r", "jl", "sql", "pl", "cs", "dart", "zig", "wasm",
             "glsl", "frag", "vert", "ipynb", "toml_", "makefile", "dockerfile"},
    "doc": {"md", "markdown", "txt", "rst", "tex", "adoc", "org", "bib", "srt", "vtt"},
    "data": {"json", "jsonl", "ndjson", "csv", "tsv", "yml", "yaml", "toml", "xml", "ini", "cfg", "conf", "lock",
             "geojson", "parquet", "sqlite", "db"},
}
EXT_CAT = {e: c for c, es in EXT.items() for e in es}
REVERT_RE = re.compile(r"^Revert \"")
MERGE_MSG_RE = re.compile(r"^(Merge pull request #\d+|Merge branch '.*' into |Merge remote-tracking branch|"
                          r"Merge branch '[^']*'$)|See merge request ", re.M)
DEPLOY_MSG_RE = re.compile(r"\b(deploy(?:ed|ing|ment)?|publish(?:ed|ing)?|gh-pages|release[sd]?|go live|live site)\b",
                           re.I)
COAUTH_RE = re.compile(r"^co-authored-by:", re.I | re.M)
PAGES_BRANCHES = {"gh-pages", "pages", "docs-pages"}


def _cat(path: str) -> str:
    base = path.rsplit("/", 1)[-1].lower()
    if base in ("makefile", "dockerfile"):
        return "code"
    if "." not in base:
        return "other"
    return EXT_CAT.get(base.rsplit(".", 1)[-1], "other")


def _iso_utc(s: str):
    return dt.datetime.fromisoformat(s).astimezone(UTC)


def extract_repo(repo: str, mode: str, default_ref: str | None) -> pl.DataFrame | None:
    d = clone_dir(repo)
    if not d.exists():
        return None
    files_opt = {"full": ["--numstat"], "blobless": ["--name-only"], "commits_only": []}[mode]
    cmd = GIT + ["-C", str(d), "log", "--all", "--source", "--no-renames", "--no-color"] + files_opt + \
        [f"--format={FMT}"]
    r = subprocess.run(["nice", "-n", "10"] + cmd, capture_output=True, env=git_env(), stdin=subprocess.DEVNULL,
                       timeout=1800)
    if r.returncode != 0:
        raise RuntimeError(f"{repo}: git log failed: {r.stderr[-300:]!r}")
    default_set = set()
    if default_ref:
        rv = subprocess.run(GIT + ["-C", str(d), "rev-list", default_ref], capture_output=True, text=True,
                            env=git_env(), stdin=subprocess.DEVNULL)
        default_set = set(rv.stdout.split()) if rv.returncode == 0 else set()
    out = r.stdout.decode("utf-8", errors="replace")
    recs = []
    for chunk in out.split("\x1e")[1:]:
        head, _, rest = chunk.partition("\x1d")
        f = head.split("\x1f")
        if len(f) < 10:
            continue
        h, parents, ae, an, ta, ce, cn, tc, src = f[:9]
        msg = "\x1f".join(f[9:])
        npar = len(parents.split())
        n_files = ins = dele = nbin = 0
        cat_lines = Counter()
        paths = []
        for line in rest.splitlines():
            if not line.strip():
                continue
            if mode == "full":
                parts = line.split("\t", 2)
                if len(parts) != 3:
                    continue
                a_, d_, path = parts
                n_files += 1
                paths.append(path)
                if a_ == "-":
                    nbin += 1
                else:
                    ins += int(a_); dele += int(d_)
                    cat_lines[_cat(path)] += int(a_) + int(d_)
            elif mode == "blobless":
                n_files += 1
                paths.append(line.strip())
        first = msg.lstrip().split("\n", 1)[0]
        recs.append({
            "hash": h, "n_parents": npar, "author_email": ae.lower(), "author_name": an, "t_author": _iso_utc(ta),
            "committer_email": ce.lower(), "committer_name": cn, "t_commit": _iso_utc(tc),
            "branch": src.removeprefix("refs/heads/").removeprefix("refs/remotes/origin/"),
            "on_default": h in default_set,
            "msg_len": len(msg.strip()), "is_revert": bool(REVERT_RE.match(first)),
            "merge_msg": bool(MERGE_MSG_RE.search(msg)), "deploy_msg": bool(DEPLOY_MSG_RE.search(first)),
            "n_coauthors": len(COAUTH_RE.findall(msg)),
            "n_files": n_files if mode != "commits_only" else None,
            "insertions": ins if mode == "full" else None, "deletions": dele if mode == "full" else None,
            "n_binary": nbin if mode == "full" else None,
            "lines_web": cat_lines["web"] if mode == "full" else None,
            "lines_code": cat_lines["code"] if mode == "full" else None,
            "lines_doc": cat_lines["doc"] if mode == "full" else None,
            "lines_data": cat_lines["data"] if mode == "full" else None,
            "paths": paths,
        })
    if not recs:
        return None
    df = pl.DataFrame(recs, schema_overrides={"n_files": pl.Int32, "insertions": pl.Int64, "deletions": pl.Int64,
                                              "n_binary": pl.Int32, "lines_web": pl.Int64, "lines_code": pl.Int64,
                                              "lines_doc": pl.Int64, "lines_data": pl.Int64,
                                              "paths": pl.List(pl.Utf8)})
    return df.with_columns(pl.lit(repo).alias("repo"), pl.lit(mode).alias("fetch_mode"))


def _safe(repo: str) -> str:
    return repo.replace("/", "__")


def extract(workers: int = 2):
    """Per-clone commit records into scratch (author e-mails and paths stay in scratch; never in tables)."""
    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)
    fr = fetch_results().filter(pl.col("mode").is_in(["full", "blobless", "commits_only"]))
    todo = [(r, m, d) for r, m, d in fr.select("repo", "mode", "default_ref").iter_rows()
            if not (EXTRACT_DIR / f"{_safe(r)}.parquet").exists()]
    t0, n, nc, errs = time.time(), 0, 0, []

    def one(args):
        repo, mode, dref = args
        df = extract_repo(repo, mode, dref)
        p = EXTRACT_DIR / f"{_safe(repo)}.parquet"
        if df is None:
            pl.DataFrame({"hash": []}, schema={"hash": pl.Utf8}).write_parquet(p)
            return 0
        df.write_parquet(p, compression="zstd")
        return df.height
    with cf.ThreadPoolExecutor(workers) as ex:
        futs = {ex.submit(one, a): a[0] for a in todo}
        for f in cf.as_completed(futs):
            try:
                nc += f.result()
            except Exception as e:  # noqa: BLE001
                errs.append(f"{futs[f]}: {e}")
            n += 1
            if n % 100 == 0:
                print(f"  extract {n}/{len(todo)} {nc} commits {time.time()-t0:.0f}s", flush=True)
    if errs:
        (SCRATCH / "dq4_extract_errors.txt").write_text("\n".join(errs))
    return f"extract: {n} repos, {nc:,} commits, {len(errs)} errors, {time.time()-t0:.0f}s"


# ----------------------------------------------------------------------------- identity mapping

BOT_RE = re.compile(r"\[bot\]|github-actions|^actions?@github\.com$|^noreply@github\.com$|dependabot|renovate|"
                    r"gitlab-bot|semantic-release|^project_\d+_bot|snyk-bot|deepsource-autofix|imgbot|"
                    r"allcontributors|pre-commit-ci|netlify|vercel\[|copilot", re.I)
BOT_NAME_RE = re.compile(r"^(github actions?|github|gitlab|copilot|netlify|vercel|cloudflare pages|bot)$|\bbot\b", re.I)
PLACEHOLDER_LOCAL = {"root", "ubuntu", "user", "admin", "computeruse", "computer-use", "agent", "you", "me", "test",
                     "dev", "none", "noreply", "no-reply", "email", "your.email", "your_email", "youremail",
                     "your-email", "name", "git", "default", "runner", "codespace", "vscode"}
PLACEHOLDER_DOM = re.compile(r"(^|\.)(example\.(com|org|net|local)|localhost|localdomain|local|internal|invalid|"
                             r"none|ec2\.internal)$")
GH_NOREPLY = re.compile(r"^(?:\d+\+)?([^@]+)@users\.noreply\.github\.com$")
GL_NOREPLY = re.compile(r"^(?:\d+-)?([^@]+)@users\.noreply\.gitlab\.com$")


class IdentityMapper:
    """(email, name) -> (kind, agent, method). kind in {agent, bot, human, unknown}."""

    def __init__(self):
        self.keys, _ = roster_keys()

    def _key(self, s: str, allow_contains: bool):
        k = norm(s)
        if not k:
            return None
        if k in self.keys:
            return self.keys[k]
        if len(k) >= 5:
            pre = [n for n in self.keys if n.startswith(k)]
            if len(set(self.keys[n] for n in pre)) == 1:
                return self.keys[pre[0]]
        if allow_contains and len(k) >= 5:
            hits = sorted((n for n in self.keys if len(n) >= 5 and n in k), key=len, reverse=True)
            if hits and (len(hits) == 1 or len(hits[0]) > len(hits[1])):
                return self.keys[hits[0]]
        return None

    def __call__(self, email: str, name: str):
        email = (email or "").lower().strip()
        local, _, dom = email.partition("@")
        if dom == "agentvillage.org":
            ag = self._key(local, True)
            if ag is not None:
                return "agent", ag, "email_agentvillage"
        m = GH_NOREPLY.match(email) or GL_NOREPLY.match(email)
        if m:
            ag = account_owner_agent(m.group(1).lower(), self.keys)
            if ag is not None:
                return "agent", ag, "noreply_account"
        if BOT_RE.search(email) or BOT_RE.search(name or "") or BOT_NAME_RE.search((name or "").strip()):
            return "bot", None, None
        ag = self._key(name or "", False)
        if ag is not None:
            return "agent", ag, "name"
        ag = self._key(local, dom in ("agentvillage.org",))
        if ag is not None and len(norm(local)) >= 4:
            return "agent", ag, "email_local"
        if dom == "agentvillage.org":
            return "unknown", None, "agentvillage_unmapped"  # village domain, not a roster agent (e.g. swarm-*)
        if not email or local in PLACEHOLDER_LOCAL or PLACEHOLDER_DOM.search(dom) or "@" not in email:
            return "unknown", None, None
        return "human", None, None


def committer_kind(email: str, name: str, mapper: IdentityMapper) -> str:
    e = (email or "").lower()
    if e in ("noreply@github.com", "noreply@gitlab.com") or (name or "") in ("GitHub", "GitLab"):
        return "web"
    return mapper(email, name)[0]

# ----------------------------------------------------------------------------- calendar helpers


def calendar_frame() -> pl.DataFrame:
    return pl.read_parquet(OUT / "calendar.parquet", columns=["pt_date", "goal_no", "regime", "win_start", "win_end",
                                                             "holdout"])


def add_time_keys(df: pl.DataFrame, tcol: str = "t") -> pl.DataFrame:
    """pt_date, goal_no, regime, holdout (holdout_mask), in_window for a frame with a UTC time column."""
    cal = calendar_frame()
    goals = pl.DataFrame([{"g_start": g["start"], "g_no": g["goal_no"]} for g in load_goals()]).with_columns(
        pl.col("g_no").cast(pl.Int8)).sort("g_start")
    df = df.with_columns(pl.col(tcol).dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.Utf8)
                         .alias("pt_date"))
    df = df.join(cal.select("pt_date", "goal_no", pl.col("regime").cast(pl.Utf8), "win_start", "win_end"),
                 on="pt_date", how="left")
    df = (df.with_row_index("_i").sort(tcol)
          .join_asof(goals, left_on=tcol, right_on="g_start", strategy="backward")
          .sort("_i").drop("_i", "g_start"))
    bounds = [("I", None, "2026-02-25"), ("II", "2026-02-25", "2026-03-24"), ("III", "2026-03-24", None)]
    reg = pl.when(pl.col("pt_date") < bounds[0][2]).then(pl.lit("I")).when(pl.col("pt_date") < bounds[1][2]) \
        .then(pl.lit("II")).otherwise(pl.lit("III"))
    df = df.with_columns(pl.coalesce("goal_no", "g_no").fill_null(0).cast(pl.Int8).alias("goal_no"),
                         pl.coalesce("regime", reg).alias("regime"),
                         pl.col("win_start").is_not_null().alias("calendar_day"),
                         ((pl.col(tcol) >= pl.col("win_start") - pl.duration(minutes=15))
                          & (pl.col(tcol) <= pl.col("win_end") + pl.duration(minutes=15))).fill_null(False)
                         .alias("in_window")).drop("g_no", "win_start", "win_end")
    hm = holdout_mask(df["pt_date"].to_list(), df["goal_no"].to_list())
    return df.with_columns(pl.Series("holdout", hm, dtype=pl.Boolean))

# ----------------------------------------------------------------------------- API writes (glab/gh api, curl)

API_START = re.compile(r"(?<![\w-])(glab\s+api|gh\s+api|curl)(?![\w-])")
METHOD_RE = re.compile(r"(?:-X|--method|--request)\s*=?\s*[\"']?(GET|POST|PUT|PATCH|DELETE)\b", re.I)
GL_FIELDS = re.compile(r"(?:^|\s)(?:-f|-F|--field|--raw-field|--input)(?:\s|=)")
CURL_DATA = re.compile(r"(?:^|\s)(?:-d|--data(?:-raw|-binary|-urlencode|-ascii)?|--form|-F|--json)(?:\s|=)")
CURL_PUT = re.compile(r"(?:^|\s)(?:-T|--upload-file)(?:\s|=)")
GL_URL = re.compile(r"gitlab\.com/api/v4/([^\s\"'?#]+)")
GH_URL = re.compile(r"api\.github\.com/([^\s\"'?#]+)")
ARG_RE = re.compile(r"(?:glab|gh)\s+api\s+((?:(?:-[A-Za-z]|--[\w-]+)(?:[ =](?:\"[^\"]*\"|'[^']*'|[^\s\"'-][^\s]*))?\s+)*)"
                    r"([\"']?)([^\s\"']+)\2")
AGENT_PATH = re.compile(r"ai-village-agents(?:/|%2[Ff])village(?:/|%2[Ff])([A-Za-z0-9][A-Za-z0-9._-]*)")


def _gl_category(ep: str, method: str) -> str:
    e = ep.split("?")[0].rstrip("/")
    if re.search(r"/repository/files(/|$)", e) or (re.search(r"/repository/commits$", e) and method == "POST"):
        return "content"
    if re.search(r"/merge_requests/\d+/(merge|rebase)$", e):
        return "mr_merge"
    if re.search(r"/(notes|discussions)(/\d+)?$", e):
        return "comment"
    if re.search(r"/merge_requests$", e) and method == "POST":
        return "mr_create"
    if re.search(r"/merge_requests/\d+$", e):
        return "mr_update"
    if re.search(r"/issues(/\d+)?$", e):
        return "issue"
    if re.search(r"/(pipeline|pipelines|jobs/\d+/(retry|play)|trigger/pipeline)", e):
        return "pipeline"
    if re.search(r"/(releases|repository/tags|repository/branches)", e):
        return "release_branch"
    if re.search(r"/wikis", e):
        return "wiki"
    if re.fullmatch(r"projects", e) and method == "POST":
        return "repo_create"
    if re.search(r"/fork$", e):
        return "fork"
    if re.fullmatch(r"projects/[^/]+", e) or re.search(r"/(variables|members|hooks|pages|protected_branches|"
                                                        r"share|access_tokens|deploy_keys)", e):
        return "settings"
    return "other"


def _gh_category(ep: str, method: str, seg: str) -> str | None:
    e = ep.split("?")[0].rstrip("/")
    if e == "graphql":
        return "graphql_mutation" if "mutation" in seg else None
    if re.search(r"/contents/", e) or re.search(r"/git/(commits|trees|blobs|refs)", e):
        return "content"
    if re.search(r"/pulls/\d+/merge$", e):
        return "mr_merge"
    if re.search(r"/(issues|pulls)/\d+/(comments|reviews)$|/comments(/\d+)?$", e):
        return "comment"
    if re.search(r"/pulls$", e) and method == "POST":
        return "mr_create"
    if re.search(r"/pulls/\d+$", e):
        return "mr_update"
    if re.search(r"/issues(/\d+)?$", e):
        return "issue"
    if re.search(r"/(actions/workflows/[^/]+/dispatches|actions/runs/\d+/rerun|dispatches)$", e):
        return "pipeline"
    if re.search(r"/(releases|git/tags)", e):
        return "release_branch"
    if re.search(r"/pages(/builds)?$", e):
        return "settings"
    if re.fullmatch(r"(user|orgs/[^/]+)/repos", e) or re.search(r"/generate$", e):
        return "repo_create"
    if re.search(r"/forks$", e):
        return "fork"
    if re.fullmatch(r"repos/[^/]+/[^/]+", e) or re.search(r"/(collaborators|hooks|topics|actions/secrets)", e):
        return "settings"
    return "other"


def parse_api_calls(cmd: str) -> list[dict]:
    """Write calls (non-GET) to the GitLab / GitHub REST APIs in one logged command (truncated to 300 chars)."""
    out = []
    starts = [m for m in API_START.finditer(cmd)]
    for i, m in enumerate(starts):
        seg = cmd[m.start(): starts[i + 1].start() if i + 1 < len(starts) else len(cmd)]
        seg = re.split(r"\s;\s|\s&&\s|\s\|\|?\s", seg)[0] if m.group(1) != "curl" else seg.split(" ; ")[0]
        tool = re.sub(r"\s+", " ", m.group(1))
        host, ep = None, None
        if tool == "curl":
            g = GL_URL.search(seg) or None
            h = GH_URL.search(seg) or None
            if g:
                host, ep = "gitlab", g.group(1)
            elif h:
                host, ep = "github", h.group(1)
            else:
                continue
            mm = METHOD_RE.search(seg)
            method = mm.group(1).upper() if mm else ("PUT" if CURL_PUT.search(seg) else
                                                     "POST" if CURL_DATA.search(seg) else "GET")
        else:
            a = ARG_RE.search(seg)
            if not a:
                continue
            ep = a.group(3)
            host = "gitlab" if tool == "glab api" else "github"
            for rx in (GL_URL, GH_URL):
                u = rx.search(ep)
                if u:
                    ep = u.group(1)
            ep = ep.lstrip("/")
            mm = METHOD_RE.search(seg)
            method = mm.group(1).upper() if mm else ("POST" if GL_FIELDS.search(seg) else "GET")
            if host == "github" and ep == "graphql":
                method = "POST"
        if method == "GET":
            continue
        cat = _gl_category(ep, method) if host == "gitlab" else _gh_category(ep, method, seg)
        if cat is None:
            continue
        ref = None
        if host == "gitlab":
            pm = re.match(r"projects/([^/?\s]+)", ep)
            ref = pm.group(1) if pm else None
            if ref and "%2" in ref:
                ref = re.sub("%2f", "/", ref, flags=re.I).lower()
        else:
            pm = re.match(r"repos/([^/\s]+)/([^/?\s]+)", ep)
            ref = f"{pm.group(1)}/{pm.group(2)}".lower() if pm else None
        out.append({"tool": tool, "host": host, "method": method, "category": cat, "project_ref": ref})
    return out


def api_writes(gl_paths: dict[str, set] | None = None) -> pl.DataFrame:
    """One row per API write call found in artifact_commands_text, with the target repo where resolvable."""
    c = pl.read_parquet(OUT / "artifact_commands_text.parquet", columns=["row", "t", "agent", "cmd", "error"]) \
        .filter(pl.col("cmd").is_not_null() & pl.col("cmd").str.contains(r"glab api|gh api|gitlab\.com/api/v4|"
                                                                          r"api\.github\.com"))
    recs = []
    id_votes = defaultdict(Counter)
    for row, t, agent, cmd, err in c.iter_rows():
        calls = parse_api_calls(cmd)
        paths_in_cmd = {p.lower() for p in AGENT_PATH.findall(cmd)}
        for k, call in enumerate(calls):
            ref = call["project_ref"]
            repo, how = None, None
            if call["host"] == "gitlab" and ref:
                if ref.startswith("ai-village-agents/") or ("/" in ref and not ref.isdigit()):
                    repo, how = f"gitlab.com/{ref}", "path"
                elif ref.startswith("$") and len(paths_in_cmd) == 1:
                    repo, how = f"gitlab.com/ai-village-agents/village/{next(iter(paths_in_cmd))}", "var_path"
                elif ref.isdigit() and len(paths_in_cmd) == 1:
                    id_votes[ref][next(iter(paths_in_cmd))] += 1
            elif call["host"] == "github" and ref and not ref.startswith("$"):
                repo, how = f"github.com/{ref}", "path"
            fpath = None
            fm = re.search(r"/repository/files/([^/?\s\"']+)", cmd) if call["category"] == "content" else None
            if fm:
                fpath = re.sub("%2f", "/", fm.group(1), flags=re.I).replace("%2E", ".").replace("%2e", ".")
            recs.append({"row": row, "call": k, "t": t, "agent": agent, "error": err, **call, "repo": repo,
                         "repo_how": how, "_fpath": fpath})
    df = pl.DataFrame(recs, schema_overrides={"agent": pl.Int8, "row": pl.UInt32, "call": pl.Int16},
                      infer_schema_length=None)
    # numeric GitLab project ids -> repo: (1) co-occurrence votes with a path in the same command,
    # (2) the files written through the API matched against the paths in the fetched GitLab histories
    id_map = {i: f"gitlab.com/ai-village-agents/village/{v.most_common(1)[0][0]}" for i, v in id_votes.items()
              if v.most_common(1)[0][1] >= 2 and v.most_common(1)[0][1] >= 0.6 * sum(v.values())}
    how_map = {i: "id_cooccur" for i in id_map}
    if gl_paths:
        by_path = defaultdict(set)
        for repo, ps in gl_paths.items():
            for p in ps:
                by_path[p].add(repo)
        fp = df.filter((pl.col("host") == "gitlab") & pl.col("project_ref").str.contains(r"^\d+$")
                       & pl.col("_fpath").is_not_null())
        for pid, paths in fp.group_by("project_ref").agg(pl.col("_fpath").unique()).iter_rows():
            if pid in id_map:
                continue
            votes = Counter()
            for p in paths:
                cands = by_path.get(p, set())
                if 0 < len(cands) <= 3:
                    for r in cands:
                        votes[r] += 1 / len(cands)
            if votes:
                best, v = votes.most_common(1)[0]
                if v >= 1 and v >= 0.5 * len(paths):
                    id_map[pid], how_map[pid] = best, "id_filepaths"
    df = df.with_columns(
        pl.when(pl.col("repo").is_null() & pl.col("project_ref").is_in(list(id_map)))
        .then(pl.col("project_ref").replace_strict(id_map, default=None)).otherwise(pl.col("repo")).alias("repo"),
        pl.when(pl.col("repo").is_null() & pl.col("project_ref").is_in(list(id_map)))
        .then(pl.col("project_ref").replace_strict(how_map, default=None)).otherwise(pl.col("repo_how"))
        .alias("repo_how"))
    return df.drop("_fpath")

# ----------------------------------------------------------------------------- build


def load_extracted() -> pl.DataFrame:
    frames = []
    for p in sorted(EXTRACT_DIR.glob("*.parquet")):
        df = pl.read_parquet(p)
        if df.height and "repo" in df.columns:
            frames.append(df)
    return pl.concat(frames, how="diagonal_relaxed")


def command_hashes() -> pl.DataFrame:
    """Commit hashes printed by git in agents' commands (push ranges and `git commit` output)."""
    c = pl.read_parquet(OUT / "artifact_commands_text.parquet",
                        columns=["row", "t", "agent", "verbs", "out_urls", "out_hashes", "error"])
    c = c.filter(pl.col("out_hashes").list.len() > 0)
    c = c.with_columns(pl.col("verbs").list.contains("git push").alias("v_push"),
                       pl.col("verbs").list.contains("git commit").alias("v_commit"))
    return c.explode("out_hashes").rename({"out_hashes": "prefix"}).with_columns(
        pl.col("prefix").str.to_lowercase())


def match_prefixes(prefixes: pl.Series, full: pl.Series) -> dict:
    """prefix -> full hash (unique match only)."""
    by7 = defaultdict(list)
    for h in full.unique().to_list():
        by7[h[:7]].append(h)
    out = {}
    for p in prefixes.unique().to_list():
        c = [h for h in by7.get(p[:7], []) if h.startswith(p)]
        if len(set(c)) == 1:
            out[p] = c[0]
    return out


TURN_GAP_S = 300        # a commit is "turn-backed" if its author agent had a logged turn within this many seconds
# clockwork stream: one identity, one repo, one day, >= N commits over >= SPAN minutes, and more commits than
# CW_RATIO x the author's own logged turns in that span (hand-made commits need >= ~2 turns each: edit, commit)
CLOCKWORK_N, CLOCKWORK_SPAN_MIN, CW_RATIO = 20, 20, 0.5


def turn_backing(df: pl.DataFrame) -> pl.DataFrame:
    """turn_gap_s: seconds from each agent-authored commit to the author's nearest logged turn (actions or agent
    events; the Claude Code agent's SDK sessions count as continuous turns). Commits by scripts, CI or cron jobs
    that use an agent's identity have no nearby turn."""
    ev = pl.read_parquet(OUT / "events_core.parquet", columns=["t", "agent", "actor_kind"]).filter(
        (pl.col("actor_kind") == "agent") & pl.col("agent").is_not_null()).select("t", pl.col("agent").cast(pl.Int8))
    ac = pl.scan_parquet(OUT / "actions.parquet").select("t", pl.col("agent").cast(pl.Int8)).drop_nulls("agent") \
        .collect()
    turns = pl.concat([ev, ac]).unique().sort("t").rename({"t": "t_turn"})
    x = df.select("_k", "t", "author_agent").filter(pl.col("author_agent").is_not_null()).sort("t")
    x = x.join_asof(turns.with_columns(pl.col("t_turn").alias("t")), on="t", by_left="author_agent",
                    by_right="agent", strategy="nearest")
    x = x.with_columns((pl.col("t_turn") - pl.col("t")).dt.total_seconds().abs().cast(pl.Int32).alias("turn_gap_s"))
    # Claude Code agent: SDK session intervals
    ses = [(json.loads(l)) for l in __import__("gzip").open(ROOT / "data/raw/ai-village/claude_code_sessions.jsonl.gz",
                                                             "rt")]
    cc_agent = pl.read_parquet(OUT / "roster.parquet").filter(pl.col("claude_code"))["agent"].to_list()
    iv = [(dt.datetime.fromisoformat(r["created_at"].replace("Z", "")).replace(tzinfo=UTC),
           dt.datetime.fromisoformat(r["updated_at"].replace("Z", "")).replace(tzinfo=UTC)) for r in ses
          if r.get("created_at") and r.get("updated_at")]
    if cc_agent and iv:
        def in_session(t):
            return any(a - dt.timedelta(seconds=TURN_GAP_S) <= t <= b + dt.timedelta(seconds=TURN_GAP_S) for a, b in iv)
        xs = x.filter(pl.col("author_agent").is_in(cc_agent))
        inside = {k for k, t in xs.select("_k", "t").iter_rows() if in_session(t)}
        x = x.with_columns(pl.when(pl.col("_k").is_in(list(inside))).then(pl.lit(0, pl.Int32))
                           .otherwise(pl.col("turn_gap_s")).alias("turn_gap_s"))
    df = df.join(x.select("_k", "turn_gap_s"), on="_k", how="left")
    # clockwork streams: more commits than the author's own turns could make by hand (scripts, loops, monitors)
    import numpy as np
    tarr = {a: np.sort(g["t_turn"].cast(pl.Int64).to_numpy()) for (a,), g in turns.group_by("agent")}
    grp = (df.filter(pl.col("author_agent").is_not_null())
           .group_by("author_agent", "repo", "pt_date").agg(pl.len().alias("_n"), pl.col("t").min().alias("_t0"),
                                                            pl.col("t").max().alias("_t1"))
           .filter((pl.col("_n") >= CLOCKWORK_N)
                   & ((pl.col("_t1") - pl.col("_t0")).dt.total_minutes() >= CLOCKWORK_SPAN_MIN)))
    flags = []
    for a, repo, d, n, t0_, t1_ in grp.iter_rows():
        ta = tarr.get(a)
        k = 0 if ta is None else int(np.searchsorted(ta, int(t1_.timestamp() * 1e6), "right")
                                     - np.searchsorted(ta, int(t0_.timestamp() * 1e6), "left"))
        flags.append((a, repo, d, n > CW_RATIO * k))
    cw = pl.DataFrame(flags, schema={"author_agent": pl.Int8, "repo": df.schema["repo"], "pt_date": pl.Utf8,
                                     "clockwork": pl.Boolean}, orient="row").filter(pl.col("clockwork"))
    df = df.join(cw, on=["author_agent", "repo", "pt_date"], how="left").with_columns(
        pl.col("clockwork").fill_null(False))
    return df.with_columns(
        (pl.col("turn_gap_s") <= TURN_GAP_S).fill_null(False).alias("turn_backed"),
        ((pl.col("author_kind") == "agent") & ((pl.col("turn_gap_s") > TURN_GAP_S) | pl.col("clockwork")))
        .fill_null(False).alias("automated"))


INV_COLS = ["repo", "tier", "host", "artifacts", "first_t", "last_t", "first_agent", "n_chat", "n_action",
            "n_write_strict", "n_write_any", "n_push_output", "n_clone", "n_agents", "n_write_agents", "account_agent",
            "fetch_plan"]


def build():
    t0 = time.time()
    keys, roster = roster_keys()
    inv = load_inventory()  # inventory part (build rewrites INV with fetch and history columns)
    fr = fetch_results()
    raw = load_extracted()
    print(f"  {raw.height:,} (repo, commit) rows from {raw['repo'].n_unique()} clones", flush=True)
    # ---- identities
    mapper = IdentityMapper()
    ids = raw.select("author_email", "author_name").unique()
    idrec = [(e, n, *mapper(e, n)) for e, n in ids.iter_rows()]
    ids = pl.DataFrame(idrec, schema={"author_email": pl.Utf8, "author_name": pl.Utf8, "author_kind": pl.Utf8,
                                      "author_agent": pl.Int8, "author_attr": pl.Utf8}, orient="row")
    cids = raw.select("committer_email", "committer_name").unique()
    cids = pl.DataFrame([(e, n, committer_kind(e, n, mapper)) for e, n in cids.iter_rows()],
                        schema={"committer_email": pl.Utf8, "committer_name": pl.Utf8, "committer_kind": pl.Utf8},
                        orient="row")
    df = raw.join(ids, on=["author_email", "author_name"], how="left").join(
        cids, on=["committer_email", "committer_name"], how="left")
    # ---- repo metadata
    meta = inv.select("repo", "tier", "host", "first_t", "account_agent").join(
        fr.select("repo", "default_ref"), on="repo", how="left")
    ncom = raw.group_by("repo").agg(pl.len().alias("_n"))
    meta = meta.join(ncom, on="repo", how="left")
    df = df.join(meta.select("repo", "tier", "host", pl.col("first_t").alias("repo_first_t")), on="repo", how="left")
    # ---- out_hashes: agent attribution for unknown identities, and validation flags
    ch = command_hashes()
    pmap = match_prefixes(ch["prefix"], df["hash"])
    ch = ch.with_columns(pl.col("prefix").replace_strict(pmap, default=None).alias("hash"))
    first_seen = (ch.drop_nulls("hash").sort("t").group_by("hash").agg(
        pl.col("agent").first().alias("out_hash_agent"), pl.col("t").first().alias("out_hash_t"),
        pl.col("v_commit").any().alias("out_hash_commit_cmd"), pl.col("v_push").any().alias("out_hash_push_cmd")))
    df = df.join(first_seen, on="hash", how="left").with_columns(pl.col("out_hash_t").is_not_null()
                                                                 .alias("in_out_hashes"))
    recov = (pl.col("author_kind") == "unknown") & pl.col("out_hash_agent").is_not_null()
    df = df.with_columns(pl.when(recov).then(pl.col("out_hash_agent")).otherwise(pl.col("author_agent"))
                         .alias("author_agent"),
                         pl.when(recov).then(pl.lit("out_hash")).otherwise(pl.col("author_attr")).alias("author_attr"),
                         pl.when(recov).then(pl.lit("agent")).otherwise(pl.col("author_kind")).alias("author_kind"))
    # ---- time keys (t = author time)
    df = df.rename({"t_author": "t"})
    df = add_time_keys(df, "t").with_row_index("_k")
    df = turn_backing(df).drop("_k")
    # ---- flags
    lines = pl.col("insertions") + pl.col("deletions")
    df = df.with_columns(
        (pl.col("n_parents") > 1).alias("is_merge"),
        pl.col("branch").is_in(list(PAGES_BRANCHES)).alias("pages_branch"),
        ((pl.col("n_files") > 200) | (lines > 20000)).fill_null(False).alias("bulk"),
        ((pl.col("t") < dt.datetime(2025, 4, 1, tzinfo=UTC))
         | ((pl.col("author_kind") != "agent") & (pl.col("t") < pl.col("repo_first_t") - pl.duration(days=1))))
        .alias("imported"),
        pl.when(pl.col("author_kind") != "agent").then(
            pl.col("author_email").map_elements(short_hash, return_dtype=pl.Utf8)).alias("author_id"))
    # canonical row per commit hash: the repo first seen in the record (ties: more commits)
    order = meta.select("repo", "first_t", "_n").sort(["first_t", "_n"], descending=[False, True]) \
        .with_row_index("_rank")
    df = df.join(order.select("repo", "_rank"), on="repo", how="left")
    canon = df.sort("_rank").group_by("hash").agg(pl.col("repo").first().alias("_crepo"),
                                                  pl.col("repo").n_unique().alias("n_repos"))
    df = df.join(canon, on="hash").with_columns((pl.col("repo") == pl.col("_crepo")).alias("canonical"))
    # ---- per-day distinct files (paths stay out of the table)
    paths = df.filter(pl.col("canonical") & ~pl.col("imported")).select(
        "repo", "hash", "author_agent", "pt_date", "paths").explode("paths").drop_nulls("paths")
    # ---- work_commits
    commits = df.select(
        pl.col("repo"), pl.col("tier"), pl.col("host"), "hash", "t", pl.col("t_commit"), "pt_date", "goal_no",
        "regime", "holdout", "calendar_day", "in_window",
        "author_agent", "author_kind", "author_attr", "author_id", "committer_kind",
        pl.col("n_parents").cast(pl.Int8), "is_merge", "branch", "on_default", "pages_branch",
        "n_files", "insertions", "deletions", "n_binary", "lines_web", "lines_code", "lines_doc", "lines_data", "bulk",
        pl.col("msg_len").cast(pl.Int32), "is_revert", "merge_msg", "deploy_msg", pl.col("n_coauthors").cast(pl.Int8),
        "turn_gap_s", "turn_backed", "clockwork", "automated",
        "canonical", pl.col("n_repos").cast(pl.Int16), "imported", "fetch_mode",
        "in_out_hashes", "out_hash_agent", "out_hash_t",
    ).with_columns(*[pl.col(c).cast(pl.Categorical) for c in ("repo", "tier", "host", "regime", "author_kind",
                                                               "author_attr", "committer_kind", "branch",
                                                               "fetch_mode")],
                   pl.col("out_hash_agent").cast(pl.Int8)).sort("t", "repo")
    commits.write_parquet(OUT / "work_commits.parquet", compression="zstd", compression_level=10)
    print(f"  work_commits {commits.height:,} rows ({time.time()-t0:.0f}s)", flush=True)
    # ---- API writes
    gl_paths = {r: set(p) for r, p in paths.filter(pl.col("repo").str.starts_with("gitlab.com/"))
                .group_by("repo").agg(pl.col("paths").unique()).iter_rows()}
    aw = add_time_keys(api_writes(gl_paths), "t").with_columns(
        *[pl.col(c).cast(pl.Categorical) for c in ("tool", "host", "method", "category", "repo_how", "regime")])
    aw.write_parquet(OUT / "work_api_writes.parquet", compression="zstd")
    print(f"  work_api_writes {aw.height:,} rows", flush=True)
    # ---- daily
    daily = build_daily(commits, paths, aw, meta, inv)
    daily.write_parquet(OUT / "work_daily.parquet", compression="zstd")
    print(f"  work_daily {daily.height:,} rows ({time.time()-t0:.0f}s)", flush=True)
    # ---- repos table (inventory + fetch + history summary)
    repos_out = build_repos_table(inv, fr, commits)
    repos_out.write_parquet(INV, compression="zstd")
    outcomes = build_outcomes(commits, inv)
    outcomes.write_parquet(OUT / "work_outcomes.parquet", compression="zstd")
    print(f"  work_outcomes {outcomes.height} rows", flush=True)
    write_ledger_provenance()
    return f"build: done in {time.time()-t0:.0f}s"


def active_agent_days() -> pl.DataFrame:
    ev = pl.read_parquet(OUT / "events_core.parquet", columns=["pt_date", "agent", "actor_kind"]).filter(
        (pl.col("actor_kind") == "agent") & pl.col("agent").is_not_null()).select("pt_date", "agent").unique()
    ac = pl.scan_parquet(OUT / "actions.parquet").select("t", "agent").drop_nulls("agent").with_columns(
        pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.Utf8).alias("pt_date")) \
        .select("pt_date", "agent").unique().collect()
    return pl.concat([ev.with_columns(pl.col("agent").cast(pl.Int8)), ac.with_columns(pl.col("agent").cast(pl.Int8))]
                     ).unique().with_columns(pl.lit(True).alias("active"))


def command_counts() -> pl.DataFrame:
    """Per agent-day counts of write-ish commands from the command sidecar (turns, not calls)."""
    c = pl.read_parquet(OUT / "artifact_commands_text.parquet", columns=["t", "agent", "verbs", "out_hashes", "error"]) \
        .drop_nulls("agent").filter(pl.col("verbs").list.len() > 0)
    has = lambda pfx: pl.col("verbs").list.eval(pl.element().str.starts_with(pfx)).list.any()  # noqa: E731
    c = c.with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.Utf8)
                       .alias("pt_date"))
    return c.group_by("agent", "pt_date").agg(
        pl.col("verbs").list.contains("git push").sum().alias("cmd_push"),
        (pl.col("verbs").list.contains("git push") & (pl.col("out_hashes").list.len() > 0)).sum()
        .alias("cmd_push_printed"),
        pl.col("verbs").list.contains("git commit").sum().alias("cmd_commit"),
        has("deploy:").sum().alias("deploy_cmds"),
        (pl.col("verbs").list.contains("gh pr create") | pl.col("verbs").list.contains("glab mr create")).sum()
        .alias("pr_mr_create_cmds"),
        (pl.col("verbs").list.contains("gh pr merge") | pl.col("verbs").list.contains("glab mr merge")).sum()
        .alias("pr_mr_merge_cmds"),
        (pl.col("verbs").list.contains("gh repo create") | pl.col("verbs").list.contains("glab repo create")).sum()
        .alias("repo_create_cmds"),
        (pl.col("verbs").list.contains("gh release create") | pl.col("verbs").list.contains("glab release create")
         | has("npm publish")).sum().alias("release_cmds"),
    ).with_columns(pl.col("agent").cast(pl.Int8))


def build_daily(commits, paths, aw, meta, inv) -> pl.DataFrame:
    cm = commits.filter(pl.col("canonical") & ~pl.col("imported")).with_columns(
        pl.col("repo").cast(pl.Utf8), (pl.col("insertions") + pl.col("deletions")).alias("lines"))
    has_site = site_repos(inv)
    cm = cm.with_columns((pl.col("repo").is_in(list(has_site)) & pl.col("on_default")).alias("site_default"))
    roots = cm.filter(pl.col("n_parents") == 0).sort("t").group_by("repo").agg(
        pl.col("author_agent").first().alias("root_agent"), pl.col("pt_date").first().alias("root_date"),
        pl.col("author_kind").first().alias("root_kind"))
    # repos whose root commit predates the village are imports (forks/templates), not new repos
    roots = roots.filter(pl.col("root_date") >= "2025-04-01")

    def agg(df, by):
        return df.group_by(by).agg(
            pl.len().cast(pl.Int32).alias("commits"),
            pl.col("lines").sum().alias("lines_changed"),
            pl.col("lines").filter(~pl.col("bulk")).sum().alias("lines_changed_nobulk"),
            pl.col("insertions").sum(), pl.col("deletions").sum(),
            pl.col("lines_code").sum(), pl.col("lines_web").sum(), pl.col("lines_doc").sum(),
            pl.col("lines_data").sum(),
            pl.col("is_merge").sum().cast(pl.Int32).alias("merges"),
            pl.col("merge_msg").sum().cast(pl.Int32).alias("pr_merge_commits"),
            pl.col("is_revert").sum().cast(pl.Int32).alias("reverts"),
            pl.col("bulk").sum().cast(pl.Int32).alias("bulk_commits"),
            pl.col("pages_branch").sum().cast(pl.Int32).alias("pages_commits"),
            pl.col("deploy_msg").sum().cast(pl.Int32).alias("deploy_msg_commits"),
            pl.col("site_default").sum().cast(pl.Int32).alias("site_default_commits"),
            pl.col("in_window").mean().alias("in_window_frac"),
            pl.col("fetch_mode").cast(pl.Utf8).is_in(["blobless", "commits_only"]).sum().cast(pl.Int32)
            .alias("commits_no_linestats"),
        )
    ag = cm.filter((pl.col("author_kind") == "agent") & ~pl.col("automated"))   # agent work
    auto = cm.filter(pl.col("automated"))                                         # scripts/CI under agent identity
    a_day = agg(ag, ["author_agent", "pt_date"]).rename({"author_agent": "agent"})
    a_auto = auto.group_by("author_agent", "pt_date").agg(pl.len().cast(pl.Int32).alias("commits_automated")) \
        .rename({"author_agent": "agent"})
    a_day = a_day.join(ag.group_by("author_agent", "pt_date").agg(pl.col("repo").n_unique().cast(pl.Int16)
                                                                   .alias("repos_touched"))
                       .rename({"author_agent": "agent"}), on=["agent", "pt_date"], how="left")
    fa = paths.filter(pl.col("author_agent").is_not_null()).group_by("author_agent", "pt_date").agg(
        pl.struct("repo", "paths").n_unique().cast(pl.Int32).alias("distinct_files")).rename({"author_agent": "agent"})
    a_day = a_day.join(fa, on=["agent", "pt_date"], how="left")
    nr = roots.filter(pl.col("root_kind") == "agent").group_by("root_agent", "root_date").agg(
        pl.len().cast(pl.Int16).alias("new_repos")).rename({"root_agent": "agent", "root_date": "pt_date"})
    cc = command_counts()
    aw_ = aw.filter(pl.col("agent").is_not_null())
    awd = aw_.group_by("agent", "pt_date").agg(
        (pl.col("host") == "gitlab").sum().cast(pl.Int32).alias("api_writes_gitlab"),
        (pl.col("host") == "github").sum().cast(pl.Int32).alias("api_writes_github"),
        pl.col("row").n_unique().cast(pl.Int32).alias("api_write_turns"),
        (pl.col("category") == "content").sum().cast(pl.Int32).alias("api_content_writes"),
        pl.col("category").cast(pl.Utf8).is_in(["mr_create", "mr_merge", "mr_update"]).sum().cast(pl.Int32)
        .alias("api_mr_pr_writes"),
        pl.col("category").cast(pl.Utf8).is_in(["comment", "issue"]).sum().cast(pl.Int32)
        .alias("api_issue_comment_writes"),
        pl.col("category").cast(pl.Utf8).is_in(["settings", "repo_create", "fork"]).sum().cast(pl.Int32)
        .alias("api_settings_writes"),
        pl.col("category").cast(pl.Utf8).is_in(["pipeline", "release_branch", "wiki", "graphql_mutation", "other"])
        .sum().cast(pl.Int32).alias("api_other_writes"))
    act = active_agent_days()
    keys = pl.concat([x.select("agent", "pt_date") for x in (a_day, a_auto, nr, cc, awd, act)]).unique()
    A = (keys.join(act, on=["agent", "pt_date"], how="left").join(a_day, on=["agent", "pt_date"], how="left")
         .join(a_auto, on=["agent", "pt_date"], how="left")
         .join(nr, on=["agent", "pt_date"], how="left").join(cc, on=["agent", "pt_date"], how="left")
         .join(awd, on=["agent", "pt_date"], how="left")
         .with_columns(pl.col("active").fill_null(False), pl.lit("agent").alias("level"),
                       pl.lit(None, pl.Utf8).alias("repo")))
    # ---- repo-day
    r_day = agg(ag, ["repo", "pt_date"])
    r_auto = auto.group_by("repo", "pt_date").agg(pl.len().cast(pl.Int32).alias("commits_automated"))
    other = cm.filter(pl.col("author_kind") != "agent").group_by("repo", "pt_date").agg(
        pl.len().cast(pl.Int32).alias("commits_other"),
        (pl.col("author_kind") == "bot").sum().cast(pl.Int32).alias("commits_bot"),
        ((pl.col("author_kind") == "bot") & pl.col("pages_branch")).sum().cast(pl.Int32).alias("bot_pages_commits"))
    nag = ag.group_by("repo", "pt_date").agg(pl.col("author_agent").n_unique().cast(pl.Int16).alias("n_agents"))
    fr_ = paths.group_by("repo", "pt_date").agg(pl.col("paths").n_unique().cast(pl.Int32).alias("distinct_files"))
    newr = roots.select("repo", pl.col("root_date").alias("pt_date"), pl.lit(1, pl.Int16).alias("new_repos"))
    awr = aw_.drop_nulls("repo").group_by("repo", "pt_date").agg(
        (pl.col("host") == "gitlab").sum().cast(pl.Int32).alias("api_writes_gitlab"),
        (pl.col("host") == "github").sum().cast(pl.Int32).alias("api_writes_github"),
        (pl.col("category") == "content").sum().cast(pl.Int32).alias("api_content_writes"))
    rkeys = pl.concat([x.select("repo", "pt_date") for x in (r_day, r_auto, other, newr, awr)]).unique()
    R = (rkeys.join(r_day, on=["repo", "pt_date"], how="left").join(other, on=["repo", "pt_date"], how="left")
         .join(r_auto, on=["repo", "pt_date"], how="left")
         .join(nag, on=["repo", "pt_date"], how="left").join(fr_, on=["repo", "pt_date"], how="left")
         .join(newr, on=["repo", "pt_date"], how="left").join(awr, on=["repo", "pt_date"], how="left")
         .join(meta.select("repo", "tier"), on="repo", how="left")
         .with_columns(pl.lit("repo").alias("level"), pl.lit(None, pl.Int8).alias("agent")))
    D = pl.concat([A, R], how="diagonal_relaxed")
    cal = calendar_frame().select("pt_date", "goal_no", pl.col("regime").cast(pl.Utf8))
    D = D.join(cal, on="pt_date", how="left").with_columns(pl.col("goal_no").is_not_null().alias("calendar_day"))
    # non-calendar days: goal from the goal start dates
    gs = sorted((g["start"].astimezone(PT).date().isoformat(), g["goal_no"]) for g in load_goals())
    def goal_of(d):
        n = 0
        for s, g in gs:
            if d >= s:
                n = g
        return n
    D = D.with_columns(pl.when(pl.col("goal_no").is_null()).then(
        pl.col("pt_date").map_elements(goal_of, return_dtype=pl.Int8)).otherwise(pl.col("goal_no"))
        .cast(pl.Int8).alias("goal_no"))
    D = D.with_columns(pl.Series("holdout", holdout_mask(D["pt_date"].to_list(), D["goal_no"].to_list()),
                                 dtype=pl.Boolean))
    count_cols = [c for c in D.columns if c not in ("level", "agent", "repo", "tier", "pt_date", "goal_no", "regime",
                                                     "holdout", "calendar_day", "active", "in_window_frac")]
    D = D.with_columns(*[pl.col(c).fill_null(0) for c in count_cols])
    front = ["level", "pt_date", "agent", "repo", "tier", "goal_no", "regime", "holdout", "calendar_day", "active"]
    D = D.select(front + [c for c in D.columns if c not in front]).with_columns(
        pl.col("level").cast(pl.Categorical), pl.col("repo").cast(pl.Categorical), pl.col("regime").cast(pl.Categorical),
        pl.col("tier").cast(pl.Categorical),
        pl.col("agent").cast(pl.Int8))
    return D.sort("level", "pt_date", "agent", "repo")


def site_repos(inv: pl.DataFrame) -> set:
    """Repos with a published site: a site artifact whose parent is the repo, or a pages branch in the clone."""
    a = pl.read_parquet(OUT / "artifacts.parquet", columns=["artifact", "kind", "name", "parent"])
    names = dict(zip(a["artifact"].to_list(), a["name"].to_list()))
    s = a.filter((pl.col("kind") == "site") & pl.col("parent").is_not_null())
    out = {canonical_repo(names[p]) for p in s["parent"].to_list() if p in names}
    for repo in inv["repo"].to_list():
        d = clone_dir(repo)
        if d.exists() and any((d / "refs/heads" / b).exists() for b in PAGES_BRANCHES):
            out.add(repo)
        elif d.exists() and (d / "packed-refs").exists():
            txt = (d / "packed-refs").read_text(errors="replace")
            if any(f"refs/heads/{b}\n" in txt for b in PAGES_BRANCHES):
                out.add(repo)
    return {r for r in out if r}


def build_repos_table(inv, fr, commits) -> pl.DataFrame:
    c = commits.filter(~pl.col("imported")).with_columns(pl.col("repo").cast(pl.Utf8))
    summ = c.group_by("repo").agg(
        pl.len().cast(pl.Int32).alias("n_commits"),
        (pl.col("author_kind") == "agent").sum().cast(pl.Int32).alias("n_commits_agent"),
        (pl.col("canonical") & (pl.col("author_kind") == "agent") & ~pl.col("automated")).sum().cast(pl.Int32)
        .alias("n_commits_agent_work"),
        pl.col("automated").sum().cast(pl.Int32).alias("n_commits_automated"),
        pl.col("author_agent").drop_nulls().n_unique().cast(pl.Int16).alias("n_commit_agents"),
        pl.col("t").min().alias("first_commit_t"), pl.col("t").max().alias("last_commit_t"))
    imp = commits.filter(pl.col("imported")).group_by(pl.col("repo").cast(pl.Utf8)).agg(
        pl.len().cast(pl.Int32).alias("n_commits_imported"))
    sites = site_repos(inv)
    out = (inv.join(fr.drop("fetched_at"), on="repo", how="left")
           .join(fr.select("repo", "fetched_at"), on="repo", how="left")
           .join(summ, on="repo", how="left").join(imp, on="repo", how="left")
           .with_columns(pl.col("repo").is_in(list(sites)).alias("has_site"),
                         pl.when(pl.col("fetch_plan") == "weak_evidence").then(pl.lit("not_attempted"))
                         .otherwise(pl.col("mode")).alias("mode")))
    return out


def write_ledger_provenance():
    path = OUT / "_provenance.json"
    prov = json.loads(path.read_text()) if path.exists() else {}
    fr = fetch_results()
    prov["work_ledger"] = {
        "built_by": "infra/shared/work_ledger.py", "git_commit": git_commit(),
        "inputs": [
            {"source": "ai-village", "revision": "838b4150303ca8228e8edb432d8b8ccae353d258",
             "tables": ["artifacts", "artifact_mentions", "artifact_commands_text", "roster", "calendar", "events_core",
                        "actions", "chat_core", "chat_text (urls only)"]},
            {"source": "repos (public git histories; data/raw/repos/_source.md)",
             "fetched": f"{fr['fetched_at'].min()} .. {fr['fetched_at'].max()}",
             "n_cloned": int(fr.filter(pl.col("mode").is_in(["full", "blobless", "commits_only"])).height)}],
        "outputs": ["work_repos.parquet", "work_commits.parquet", "work_api_writes.parquet", "work_daily.parquet",
                    "work_outcomes.parquet", "work_ledger_validation.json"],
        "params": {"full_max_bytes": FULL_MAX, "partial_max_bytes": PARTIAL_MAX, "total_cap_bytes": TOTAL_CAP,
                   "t": "author time (UTC); pt_date in America/Los_Angeles", "dedupe": "canonical row per hash",
                   "commit_text": "message length and derived flags only"},
        "built_at": dt.datetime.now(UTC).isoformat()}
    path.write_text(json.dumps(prov, indent=1))


# ----------------------------------------------------------------------------- goal-specific outcomes

YT_RE = r"(?:youtube\.com/(?:watch\?(?:[^ ]*&)?v=|shorts/|embed/|live/)|youtu\.be/|studio\.youtube\.com/video/)([A-Za-z0-9_-]{11})"
SUBSTACK_RE = r"^https?://([a-z0-9-]+)\.substack\.com/p/([a-z0-9-]+)"
LICHESS_RE = r"lichess\.org/([A-Za-z0-9]{8})(?:[A-Za-z0-9]{4})?(?:$|[/?#])"
SITE_GOALS = {17: "personal website", 19: "daily puzzle game", 25: "digital museum", 28: "personality quiz",
              39: "interactive world"}


def _goal_window(goal_no: int):
    g = {x["goal_no"]: x for x in load_goals()}[goal_no]
    return g["start"], g["end"]


def url_mentions() -> pl.DataFrame:
    """Every URL posted by anyone in chat, or used in an agent's command: t, agent, speaker_kind, source, url."""
    cc = pl.read_parquet(OUT / "chat_core.parquet", columns=["message_id", "t", "speaker_kind", "agent"])
    ct = pl.read_parquet(OUT / "chat_text.parquet", columns=["message_id", "urls"])
    ch = cc.join(ct, on="message_id").explode("urls").drop_nulls("urls").select(
        "t", pl.col("agent").cast(pl.Int8), pl.col("speaker_kind").cast(pl.Utf8), pl.lit("chat").alias("source"),
        pl.col("urls").alias("url"))
    cm = pl.read_parquet(OUT / "artifact_commands_text.parquet", columns=["t", "agent", "urls"]).explode("urls") \
        .drop_nulls("urls").select("t", pl.col("agent").cast(pl.Int8), pl.lit("agent").alias("speaker_kind"),
                                   pl.lit("command").alias("source"), pl.col("urls").alias("url"))
    return pl.concat([ch, cm])


def build_outcomes(commits, inv) -> pl.DataFrame:
    rows = []
    hold = set(json.loads((ROOT / "hypotheses/holdout.json").read_text())["goal_periods_held_out"])

    def add(goal, agent, outcome, value, unit, source, reliability, note=""):
        rows.append({"goal_no": goal, "agent": agent, "outcome": outcome, "value": float(value), "unit": unit,
                     "source": source, "reliability": reliability, "holdout": goal in hold, "note": note})
    U = url_mentions()
    # ---- #42 YouTube channel week: videos
    s, e = _goal_window(42)
    yt = U.with_columns(pl.col("url").str.extract(YT_RE, 1).alias("vid"),
                        pl.col("url").str.contains("studio.youtube.com/video/").alias("studio")).drop_nulls("vid")
    first = yt.sort("t").group_by("vid").agg(pl.col("t").first().alias("t0"), pl.col("agent").first().alias("a0"),
                                             pl.col("speaker_kind").first().alias("k0"))
    new = first.filter((pl.col("t0") >= s) & (pl.col("t0") < e) & (pl.col("k0") == "agent"))
    for a, n in new.group_by("a0").len().iter_rows():
        add(42, a, "youtube_videos_first_linked", n, "videos", "chat_text.urls + artifact_commands_text.urls: distinct "
            "video ids first seen (anyone, all time) in a link by this agent during #42", "link",
            "a link by the first poster; a video can be linked first by a teammate")
    st = yt.filter(pl.col("studio") & (pl.col("t") >= s) & (pl.col("t") < e) & (pl.col("source") == "command"))
    for a, n in st.group_by("agent").agg(pl.col("vid").n_unique()).iter_rows():
        add(42, a, "youtube_videos_studio", n, "videos", "artifact_commands_text.urls: distinct video ids in "
            "studio.youtube.com/video/<id> URLs the agent opened during #42 (only the channel owner can open them)",
            "link", "lower bound: GUI navigation by clicks leaves no URL")
    newc = new.join(yt.filter(pl.col("source") == "chat").sort("t").group_by("vid").agg(
        pl.col("agent").first().alias("a_chat")), on="vid").filter(pl.col("a_chat") == pl.col("a0"))
    for a, n in newc.group_by("a0").len().iter_rows():
        add(42, a, "youtube_videos_first_linked_chat", n, "videos", "as youtube_videos_first_linked, restricted to "
            "videos the same agent also linked first in chat (an announcement)", "link",
            "ownership unverified: agents also link other channels' videos")
    add(42, None, "youtube_videos_new_total", new.height, "videos", "distinct video ids first seen during #42 "
        "(agent links)", "link")
    # ---- #20 Substack week: posts
    s, e = _goal_window(20)
    ss = U.with_columns(pl.col("url").str.to_lowercase().str.extract_groups(SUBSTACK_RE).alias("m")) \
        .unnest("m").rename({"1": "sub", "2": "slug"}).drop_nulls("slug")
    owner = (U.with_columns(pl.col("url").str.to_lowercase().str.extract(r"^https?://([a-z0-9-]+)\.substack\.com", 1)
                            .alias("sub")).drop_nulls("sub").filter(pl.col("speaker_kind") == "agent")
             .sort("t").group_by("sub").agg(pl.col("agent").first().alias("owner"), pl.col("t").first().alias("ts")))
    posts = ss.sort("t").group_by("sub", "slug").agg(pl.col("t").first().alias("t0")).join(owner, on="sub") \
        .filter((pl.col("t0") >= s) & (pl.col("t0") < e))
    for a, n in posts.group_by("owner").len().iter_rows():
        add(20, a, "substack_posts_linked", n, "posts", "chat_text.urls + artifact_commands_text.urls: distinct "
            "<sub>.substack.com/p/<slug> first seen during #20; credited to the agent that first linked <sub>", "link",
            "subdomain ownership inferred from first mention")
    add(20, None, "substack_posts_total", posts.height, "posts", "distinct post URLs first seen during #20", "link")
    # ---- #23 chess tournament: games
    s, e = _goal_window(23)
    lc = U.filter((pl.col("t") >= s) & (pl.col("t") < e) & (pl.col("speaker_kind") == "agent")).with_columns(
        pl.col("url").str.extract(LICHESS_RE, 1).alias("gid")).drop_nulls("gid").filter(
        ~pl.col("gid").str.contains(r"^[a-z]+$"))  # game ids are random base62; all-lowercase words are pages
    for a, n in lc.group_by("agent").agg(pl.col("gid").n_unique()).iter_rows():
        add(23, a, "lichess_games_linked", n, "games", "lichess.org/<8-char id> links by the agent during #23",
            "link", "games played (linked), not results")
    add(23, None, "lichess_games_total", lc["gid"].n_unique(), "games", "distinct game ids linked by agents in #23",
        "link")
    # ---- site-building goals: repos created in the period that publish a site
    sites = site_repos(inv)
    c = commits.filter(pl.col("canonical") & ~pl.col("imported") & (pl.col("n_parents") == 0)).with_columns(
        pl.col("repo").cast(pl.Utf8))
    roots = c.sort("t").group_by("repo").agg(pl.col("t").first(), pl.col("author_agent").first(),
                                             pl.col("author_kind").first(), pl.col("goal_no").first())
    for g, what in SITE_GOALS.items():
        r = roots.filter((pl.col("goal_no") == g) & (pl.col("author_kind") == "agent"))
        r = r.with_columns(pl.col("repo").is_in(list(sites)).alias("site"))
        for a, n_rep, n_site in r.group_by("author_agent").agg(pl.len(), pl.col("site").sum()).iter_rows():
            add(g, a, "repos_created", n_rep, "repos", "work_commits: root commits authored by the agent in the period",
                "artifact")
            add(g, a, "site_repos_created", n_site, "repos", "work_repos.has_site: of those, repos with a pages "
                "branch or a site URL resolved to them (artifacts)", "artifact", f"goal: {what}; not checked live")
    # ---- every period: commits and contributors (artifact)
    cg = commits.filter(pl.col("canonical") & ~pl.col("imported") & (pl.col("author_kind") == "agent")
                        & ~pl.col("automated"))
    for g, n, na, nr in cg.group_by("goal_no").agg(pl.len(), pl.col("author_agent").n_unique(),
                                                   pl.col("repo").n_unique()).iter_rows():
        add(int(g), None, "agent_commits", n, "commits", "work_commits (canonical, not imported, agent-authored, "
            "not automated)",
            "artifact")
        add(int(g), None, "committing_agents", na, "agents", "work_commits", "artifact")
        add(int(g), None, "repos_committed_to", nr, "repos", "work_commits", "artifact")
    return pl.DataFrame(rows, schema={"goal_no": pl.Int8, "agent": pl.Int8, "outcome": pl.Utf8, "value": pl.Float64,
                                      "unit": pl.Utf8, "source": pl.Utf8, "reliability": pl.Utf8,
                                      "holdout": pl.Boolean, "note": pl.Utf8}).sort("goal_no", "outcome", "agent")


# ----------------------------------------------------------------------------- validation


def _canon_out_repo(urls) -> str | None:
    urls = list(urls) if urls is not None else []
    for u in urls:
        m = re.match(r"https?://(github\.com|gitlab\.com)/(.+?)(?:\.git)?/?$", u.strip())
        if m:
            r = canonical_repo(f"{m.group(1)}/{m.group(2).lower()}")
            if r:
                return r
    return None


def validate():
    t0 = time.time()
    hold = set(json.loads((ROOT / "hypotheses/holdout.json").read_text())["goal_periods_held_out"])
    C = pl.read_parquet(OUT / "work_commits.parquet").with_columns(pl.col("repo").cast(pl.Utf8))
    R = pl.read_parquet(INV)
    fetched = set(R.filter(pl.col("mode").is_in(["full", "blobless", "commits_only"]))["repo"].to_list())
    tried = set(R.filter(pl.col("mode").is_not_null() & (pl.col("mode") != "not_attempted"))["repo"].to_list())
    res = {"built_at": dt.datetime.now(UTC).isoformat(), "holdout_rule": "per-period numbers for non-holdout periods "
           "only; held-out periods appear only pooled"}
    # ---- V1: commits printed in agents' commands vs fetched histories
    ch = command_hashes().with_columns(pl.col("out_urls").map_elements(_canon_out_repo, return_dtype=pl.Utf8)
                                       .alias("out_repo"))
    ch = add_time_keys(ch, "t")
    full = C["hash"]
    pmap = match_prefixes(ch["prefix"], full)
    ch = ch.with_columns(pl.col("prefix").replace_strict(pmap, default=None).alias("hash"))
    first = C.filter(pl.col("canonical")).select("hash", "author_agent", "author_kind", "t", "t_commit", "repo")
    ch = ch.join(first.rename({"t": "t_c_author", "repo": "c_repo"}), on="hash", how="left")
    ch = ch.with_columns(pl.col("hash").is_not_null().alias("found"),
                         pl.when(pl.col("out_repo").is_null()).then(pl.lit("no_remote_printed"))
                         .when(pl.col("out_repo").is_in(list(fetched))).then(pl.lit("repo_fetched"))
                         .when(pl.col("out_repo").is_in(list(tried))).then(pl.lit("repo_not_public"))
                         .otherwise(pl.lit("repo_not_in_inventory")).alias("repo_status"))
    u = ch.unique(["prefix", "agent"])  # one row per printed hash per agent

    def rate(df):
        return {"n": df.height, "found": int(df["found"].sum()), "found_rate": round(float(df["found"].mean()), 4)
                if df.height else None}
    v1 = {"all": rate(u), "git_commit_output": rate(u.filter(pl.col("v_commit"))),
          "push_output": rate(u.filter(pl.col("v_push") & ~pl.col("v_commit"))),
          "by_repo_status": {k: rate(u.filter(pl.col("repo_status") == k))
                             for k in ["repo_fetched", "repo_not_public", "repo_not_in_inventory",
                                       "no_remote_printed"]},
          "era_github_before_2026-06-29": rate(u.filter(pl.col("pt_date") < "2026-06-29")),
          "era_gitlab_from_2026-06-29": rate(u.filter(pl.col("pt_date") >= "2026-06-29"))}
    fc = u.filter(pl.col("found") & pl.col("v_commit") & ~pl.col("v_push"))
    if fc.height:
        dtA = (fc["t"] - fc["t_c_author"]).dt.total_seconds().abs()
        dtC = (fc["t"] - fc["t_commit"]).dt.total_seconds().abs()
        v1["git_commit_time_agreement"] = {
            "n": fc.height, "median_abs_s_author_time": float(dtA.median()),
            "share_within_300s_author_time": round(float((dtA <= 300).mean()), 4),
            "median_abs_s_commit_time": float(dtC.median()),
            "share_within_300s_commit_time": round(float((dtC <= 300).mean()), 4)}
        v1["git_commit_agent_agreement"] = {
            "n_mapped": int((fc["author_kind"] == "agent").sum()),
            "same_agent": round(float((fc.filter(pl.col("author_kind") == "agent")["author_agent"]
                                       == fc.filter(pl.col("author_kind") == "agent")["agent"]).mean()), 4),
            "author_kinds": dict(Counter(fc["author_kind"].cast(pl.Utf8).to_list()))}
    fp = u.filter(pl.col("found") & pl.col("v_push"))
    if fp.height:
        v1["push_agent_agreement"] = {"n": fp.height, "same_agent_as_author": round(float(
            (fp["author_agent"] == fp["agent"]).fill_null(False).mean()), 4)}
    per = (u.filter(~pl.col("holdout")).group_by("goal_no").agg(pl.len().alias("n"), pl.col("found").mean().alias("found_rate"),
                                     (pl.col("repo_status") == "repo_not_public").mean().alias("share_repo_not_public"))
           .sort("goal_no"))
    v1["by_period"] = [r for r in per.to_dicts() if r["goal_no"] not in hold]
    hp = u.filter(pl.col("holdout"))
    v1["holdout_pooled"] = rate(hp)
    res["V1_out_hashes"] = v1
    # ---- V1b: ledger agent commits that were printed in a command
    W = C.filter(pl.col("canonical") & ~pl.col("imported") & (pl.col("author_kind") == "agent"))
    res["V1b_ledger_commits_seen_in_commands"] = {
        "work": round(float(W.filter(~pl.col("automated"))["in_out_hashes"].mean()), 4),
        "automated": round(float(W.filter(pl.col("automated"))["in_out_hashes"].mean()), 4),
        "note": "commands print the head of a push range and `git commit` summaries only, so this is a floor"}
    # ---- V2: coverage per period
    D = pl.read_parquet(OUT / "work_daily.parquet").filter(pl.col("level") == "agent")

    def cov_of(D):
        return D.group_by("goal_no").agg(
        pl.col("active").sum().alias("active_agent_days"),
        (pl.col("active") & ((pl.col("cmd_push") + pl.col("cmd_commit")) > 0)).sum().alias("agent_days_git_write_cmd"),
        (pl.col("active") & (pl.col("commits") > 0)).sum().alias("agent_days_with_commits"),
        (pl.col("active") & ((pl.col("cmd_push") + pl.col("cmd_commit")) > 0) & (pl.col("commits") > 0)).sum()
        .alias("write_cmd_days_with_commits"),
        (pl.col("active") & (pl.col("commits") > 0) & ((pl.col("cmd_push") + pl.col("cmd_commit")) == 0)).sum()
        .alias("commit_days_without_git_cmd"),
        pl.col("commits").sum().alias("work_commits"), pl.col("commits_automated").sum().alias("automated_commits"),
        (pl.col("api_writes_gitlab") + pl.col("api_writes_github")).sum().alias("api_writes"),
        pl.col("commits_no_linestats").sum().alias("commits_no_linestats"),
    ).with_columns((pl.col("write_cmd_days_with_commits") / pl.col("agent_days_git_write_cmd")).round(3)
                   .alias("share_write_cmd_days_with_commits")).sort("goal_no")
    cov = cov_of(D.filter(~pl.col("holdout")))
    res["V2_coverage_by_period"] = [r for r in cov.to_dicts() if r["goal_no"] not in hold]
    hc = cov_of(D.filter(pl.col("holdout"))).select(pl.exclude("goal_no", "share_write_cmd_days_with_commits")).sum()
    res["V2_coverage_holdout_pooled"] = hc.to_dicts()[0] if hc.height else {}
    # ---- V3: gaps
    wr = R.filter(pl.col("fetch_plan") == "fetch")
    nf = wr.filter(~pl.col("repo").is_in(list(fetched)))
    res["V3_gaps"] = {
        "repos_inventoried": R.height, "repos_fetch_attempted": len(tried), "repos_fetched": len(fetched),
        "repos_not_public_or_missing": int(nf.height),
        "strict_write_mentions_in_fetched": int(wr.filter(pl.col("repo").is_in(list(fetched)))["n_write_strict"].sum()),
        "strict_write_mentions_in_not_fetched": int(nf["n_write_strict"].sum()),
        "top_unfetched_by_write_mentions": nf.sort("n_write_strict", descending=True).head(15)
        .select("repo", "n_write_strict", "n_push_output").to_dicts(),
        "weak_evidence_not_attempted": int(R.filter(pl.col("fetch_plan") == "weak_evidence").height),
        "fetch_modes": dict(Counter(R["mode"].fill_null("none").to_list())),
        "commit_identity_kinds_canonical": dict(Counter(C.filter(pl.col("canonical") & ~pl.col("imported"))
                                                        ["author_kind"].cast(pl.Utf8).to_list())),
        "agent_commits_automated_share": round(float(W["automated"].mean()), 4),
        "automated_by_reason": {"not_turn_backed": int((~W["turn_backed"]).sum()),
                                "clockwork": int(W["clockwork"].sum())},
        "claude_code_agent_work_commits": int(W.filter((pl.col("author_agent") == 19) & ~pl.col("automated")).height),
    }
    A = pl.read_parquet(OUT / "work_api_writes.parquet")
    g = A.filter(pl.col("host") == "gitlab")
    res["V3_gaps"]["gitlab_api_writes"] = {"n": g.height, "repo_resolved": round(float(g["repo"].is_not_null().mean()), 4)
                                           if g.height else None,
                                           "by_how": dict(Counter(g["repo_how"].cast(pl.Utf8).fill_null("unresolved")
                                                                  .to_list()))}
    # API content writes that left a commit by the same agent in the same repo within [-120 s, +600 s]
    cw = A.filter((pl.col("category") == "content") & pl.col("repo").is_not_null() & ~pl.col("error").fill_null(False)) \
        .select("row", "call", "t", "agent", "repo").with_columns(pl.col("repo").cast(pl.Utf8)).sort("t")
    ca = C.filter(pl.col("author_kind") == "agent").select(pl.col("t").alias("tc"), "author_agent", "repo") \
        .with_columns(pl.col("tc").alias("t")).sort("t")
    if cw.height:
        m = cw.join_asof(ca, on="t", by_left=["agent", "repo"], by_right=["author_agent", "repo"], strategy="forward",
                         tolerance="10m")
        res["V3_gaps"]["api_content_writes_with_commit"] = {
            "n": cw.height, "share_commit_within_10min_after": round(float(m["tc"].is_not_null().mean()), 4),
            "note": "API file/commit writes appear in git history as commits; don't add api_content_writes to commits"}
    (OUT / "work_ledger_validation.json").write_text(json.dumps(res, indent=1, default=str))
    v = res["V1_out_hashes"]
    return (f"validate: printed hashes found {v['all']['found_rate']} (git commit {v['git_commit_output']['found_rate']},"
            f" push {v['push_output']['found_rate']}); in fetched repos {v['by_repo_status']['repo_fetched']['found_rate']}"
            f"; {time.time()-t0:.0f}s")


if __name__ == "__main__":
    os.environ.setdefault("POLARS_MAX_THREADS", "2")
    what = sys.argv[1:] or ["extract", "build", "validate"]
    stages = ["inventory", "fetch", "upgrade", "extract", "build", "validate"] if what == ["refresh"] else what
    for s in stages:
        print(globals()[s](), flush=True)
