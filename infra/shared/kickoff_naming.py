"""Kickoff naming rule (H54): does a kickoff or goal text name a repo? Token helpers used by replicator_hosts.

Copied verbatim from hypotheses/H54-kickoff-quench-target/scheme/build.py (GENERIC, name_tokens, text_tokens, tok_match;
2026-10-04, STANDARDS §8) so that shared code no longer loads a hypothesis file at run time (replicator_hosts did, via
importlib). H54's file is untouched. Text is handled in memory only by the callers.

  name_tokens(project) -> set   distinctive tokens of a canonical artifact name (owner, hosts, generic words, hashes,
                                long digit runs and tokens shorter than 4 characters dropped)
  text_tokens(text) -> set      lower-cased alphanumeric tokens of a text, plus de-pluralized forms
  tok_match(ptoks, ttoks) -> int  how many project tokens occur in the text (plural-tolerant)
A repo is kickoff-named when it is strictly linked in a kickoff message or tok_match(name_tokens(repo), tokens) > 0 for
the kickoff tokens (minus goal tokens) or the goal tokens (replicator_hosts.kickoff_named).

Verify: uv run python infra/shared/kickoff_naming.py --verify   (H54's functions, read-only import, on every artifact
        name and every goal text: identical outputs)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

GENERIC = {"village", "agent", "agents", "github", "gitlab", "www", "main", "master", "repo", "project", "projects",
           "test", "tests", "site", "page", "pages", "docs", "the", "and", "for", "with", "from", "your", "html", "index",
           "http", "https", "netlify", "vercel", "app", "apps", "com", "org", "io", "net", "dev", "blob", "tree", "src",
           "readme", "public", "data", "file", "files", "edit", "view", "google", "document", "drive", "folder",
           "spreadsheets", "presentation", "forms", "sheet", "sheets", "new", "final", "draft", "home", "aivillage",
           "aidigest", "digest", "agentvillage", "ai-village-agents"}


def name_tokens(project: str) -> set[str]:
    s = project.lower()
    s = re.sub(r"^(https?://)?", "", s)
    parts = s.split("/")
    host = parts[0]
    path = parts[1:]
    if host in ("github.com", "gitlab.com") and path:
        path = path[1:]  # drop owner
        if path[:1] == ["village"]:
            path = path[1:]
    toks = []
    if host.endswith("github.io") or host.endswith("netlify.app") or host.endswith("vercel.app") or host.endswith("pages.dev"):
        toks += re.split(r"[-_.]", host.split(".")[0]) if not host.endswith("github.io") else []
    elif host not in ("github.com", "gitlab.com", "docs.google.com", "drive.google.com"):
        toks += re.split(r"[-_.]", host.rsplit(".", 1)[0])
    for p in path:
        toks += re.split(r"[-_.:]", p)
    out = set()
    for t in toks:
        t = t.strip()
        if len(t) < 4 or t.isdigit() or t in GENERIC or re.fullmatch(r"[0-9a-f]{8,}", t) or re.search(r"\d{3,}", t):
            continue
        if len(t) > 20 and not re.search(r"[aeiou]{1}", t):
            continue
        out.add(t)
    return out


def text_tokens(text: str) -> set[str]:
    toks = {t.lower() for t in re.findall(r"[A-Za-z][A-Za-z0-9]+", text)}
    toks |= {t[:-1] for t in toks if t.endswith("s") and len(t) > 4}
    return toks


def tok_match(ptoks: set[str], ttoks: set[str]) -> int:
    n = 0
    for t in ptoks:
        if t in ttoks or (t.endswith("s") and t[:-1] in ttoks):
            n += 1
    return n


def verify() -> bool:
    import importlib.util
    import polars as pl
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from common import OUT, ROOT, load_goals
    sys.dont_write_bytecode = True          # read-only import: never write into hypotheses/
    spec = importlib.util.spec_from_file_location("_h54_build_ro", ROOT / "hypotheses/H54-kickoff-quench-target/scheme/build.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    names = pl.read_parquet(OUT / "artifacts.parquet", columns=["name"])["name"].drop_nulls().unique().to_list()
    goals = [g["goal"] or "" for g in load_goals()]
    bad_n = sum(name_tokens(x) != m.name_tokens(x) for x in names)
    bad_t = sum(text_tokens(x) != m.text_tokens(x) for x in goals)
    gt = [text_tokens(x) for x in goals]
    bad_m = sum(tok_match(name_tokens(x), t) != m.tok_match(m.name_tokens(x), t) for x in names[:2000] for t in gt[:10])
    ok = (bad_n == 0 and bad_t == 0 and bad_m == 0 and GENERIC == m.GENERIC)
    print({"names": len(names), "name_tokens_mismatch": bad_n, "goal_texts": len(goals), "text_tokens_mismatch": bad_t,
           "tok_match_mismatch": bad_m, "generic_equal": GENERIC == m.GENERIC, "ok": ok})
    return ok


if __name__ == "__main__":
    if "--verify" in sys.argv:
        sys.exit(0 if verify() else 1)
    print(__doc__)
