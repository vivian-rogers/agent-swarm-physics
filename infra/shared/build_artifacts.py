"""Shared artifacts table: repos, sites, files and URL domains, with every mention in chat, actions and intentions.

Two phases (run both by default):

  scan    one streaming pass over raw computer_use_turns (orjson, `gzcat` in a second process). Keeps only
          bash commands and typed text that contain git / gh / glab / deploy commands or URLs. Writes the small
          intermediate `artifact_commands_text.parquet` (a *_text sidecar: command lines truncated to 300 chars,
          URLs, directories, and hashes/remotes parsed from git output). ~2-3 min, 2 processes.
  build   canonicalizes every reference into an artifact and writes
            artifacts.parquet          one row per artifact (no text: ids, names, counts)
            artifact_mentions.parquet  one row per (artifact, mention): t, agent, source, how, verb, room, refs
          from chat (`chat_text.urls` + scheme-less repo/site refs in `chat_text.text`), intentions
          (`intentions_text`) and the command sidecar. ~10 s.

Usage: uv run python infra/shared/build_artifacts.py [scan|build]   (default: both)

Canonical names
  repo    github.com/<owner>/<repo>; gitlab.com/<group>/.../<project> (path before '/-/'; for the agents' group,
          gitlab.com/ai-village-agents/village/<project>). Lowercased, '.git' stripped. API URLs map to their repo
          (api.github.com/repos/o/r/...; gitlab.com/api/v4/projects/<url-encoded path>/...); numeric-id GitLab
          API calls count as the domain gitlab.com.
  file    <repo>:<path> for blob/raw links (ref dropped); docs.google.com/<type>/<id>; drive.google.com/file/<id>;
          gist.github.com/<id>.
  site    <owner>.github.io/<repo> (or the bare host for a user site); <host> for GitLab Pages unique domains and
          other hosting platforms (pages.dev, workers.dev, netlify.app, vercel.app, surge.sh, substack, ...);
          sites.google.com/view/<name>.
  domain  registrable domain of any other URL (last two labels; three for co.uk-style). github.com/<owner>
          pages without a repo count as the domain github.com.
  Dropped: localhost, loopback and private IPs, hosts without a dot, '[REDACTED]' hosts.
  parent: file -> repo; site -> repo when derivable (github.io path; GitLab Pages host minus its -xxxxxx suffix
          matched to a gitlab project of that name).

Mentions ('how'):
  url          a URL (chat: the `chat_text.urls` list; actions/intentions: same URL regex)
  bare         scheme-less 'github.com/o/r', '*.github.io/...', or 'ai-village-agents/<name>' (resolved by name)
  output       a remote URL printed by git (e.g. 'To https://github.com/o/r.git' after a push)
  cwd          a git/gh/deploy command run in a directory named like a known repo ('cd X && git ...', 'git -C X')
  session_cwd  same, but the directory comes from an earlier 'cd' in the same computer-use session
  Directory names resolve first to the repo the same agent cloned into that directory, else to the unique repo
  with that name (GitHub before 2026-06-29, GitLab after, NE24), else are dropped.
The Claude Code agent's separate stream (claude_code_messages) is not scanned (design rule: kept out of core tables).
"""
from __future__ import annotations

import re
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import orjson
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUT, RAW, URL_RE, parse_ts, rows, write_provenance  # noqa: E402

CMD_OUT = OUT / "artifact_commands_text.parquet"
MAX_CMD = 300
MAX_URL = 200
GITLAB_SWITCH = "2026-06-29"  # NE24: GitHub -> GitLab

# ----------------------------------------------------------------------------- command parsing

GIT_RE = re.compile(r"(?<![\w-])git\s+(?:(?:-C|-c)\s+\S+\s+|--[\w-]+(?:=\S+)?\s+)*([a-z][a-z-]+)")
GH_RE = re.compile(r"(?<![\w-])(gh|glab)\s+([a-z][a-z-]+)(?:\s+([a-z][a-z-]+))?")
DEPLOY_RE = re.compile(r"(?<![\w-])(wrangler|vercel|netlify|firebase\s+deploy|surge|gh-pages|npm\s+run\s+deploy|"
                       r"pages\s+deploy|flyctl|heroku)(?![\w-])")
FETCH_RE = re.compile(r"(?<![\w-])(curl|wget)(?![\w-])")
CD_RE = re.compile(r"(?:^|[;&|(]\s*|\s)cd\s+(\"[^\"]+\"|'[^']+'|[^\s;&|)]+)")
GIT_C_RE = re.compile(r"(?<![\w-])git\s+-C\s+(\"[^\"]+\"|'[^']+'|\S+)")
CLONE_RE = re.compile(r"(?<![\w-])(?:git\s+clone|gh\s+repo\s+clone|glab\s+repo\s+clone)\s+(?:-{1,2}[\w-]+(?:[ =]\S+)?\s+)*"
                      r"(\S+)(?:\s+([^\s;&|]+))?")
PUSH_RANGE_RE = re.compile(r"([0-9a-f]{7,40})\.\.\.?([0-9a-f]{7,40})\s+\S+\s*->\s*\S+")
NEW_BRANCH_RE = re.compile(r"\*\s+\[new (?:branch|tag)\]\s+\S+\s*->\s*\S+")
COMMIT_RE = re.compile(r"\[([^\]\s]+)(?: \(root-commit\))? ([0-9a-f]{7,12})\]")
REPO_HOST_RE = re.compile(r"https?://(?:[^@/\s]+@)?(?:github\.com|gitlab\.com)/[^\s'\"<>]+")


def _basename(d: str) -> str | None:
    d = d.strip("\"'").rstrip("/")
    if not d or d in ("~", ".", "..", "-") or "$" in d:
        return None
    b = d.split("/")[-1]
    return b[:80] if b and b not in (".", "..") else None


def parse_command(text: str):
    """Return (verbs, relevant_lines, urls, dirs, clone) for one bash command or typed text."""
    verbs = []
    rel = []
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        hit = False
        for m in GIT_RE.finditer(s):
            verbs.append("git " + m.group(1)); hit = True
        for m in GH_RE.finditer(s):
            verbs.append(f"{m.group(1)} {m.group(2)}" + (f" {m.group(3)}" if m.group(3) else "")); hit = True
        for m in DEPLOY_RE.finditer(s):
            verbs.append("deploy:" + m.group(1).split()[0]); hit = True
        if FETCH_RE.search(s) and "http" in s:
            verbs.append("fetch:" + FETCH_RE.search(s).group(1)); hit = True
        if hit or "http" in s:
            rel.append(s)
    urls = list(dict.fromkeys(u[:MAX_URL] for u in URL_RE.findall(text)))[:50]
    dirs = [b for b in (_basename(m.group(1)) for m in CD_RE.finditer(text)) if b]
    dirs += [b for b in (_basename(m.group(1)) for m in GIT_C_RE.finditer(text)) if b]
    clone = None
    m = CLONE_RE.search(text)
    if m:
        src, dst = m.group(1), m.group(2)
        dst = _basename(dst) if dst and not dst.startswith("-") else None
        if not dst:
            dst = _basename(src.removesuffix(".git"))
        clone = (src[:MAX_URL], dst)
    return list(dict.fromkeys(verbs)), " ; ".join(rel)[:MAX_CMD], urls, list(dict.fromkeys(dirs)), clone


def parse_git_output(out: str):
    """Remote URLs and commit hashes printed by git (push ranges, new commits)."""
    urls = list(dict.fromkeys(u.split("@")[-1] if "@" in u.split("/")[2] else u
                              for u in REPO_HOST_RE.findall(out)))[:5]
    hashes = [m.group(2) for m in PUSH_RANGE_RE.finditer(out)] + [m.group(2) for m in COMMIT_RE.finditer(out)]
    return [u[:MAX_URL] for u in urls], list(dict.fromkeys(hashes))[:10], bool(NEW_BRANCH_RE.search(out))


def scan():
    t0 = time.time()
    roster = pl.read_parquet(OUT / "roster.parquet")
    A = dict(zip(roster["agent_id"].to_list(), roster["agent"].to_list()))
    sess_agent, sess_code = {}, {}
    for r in rows("computer_use_sessions"):
        sess_agent[r["id"]] = A.get(r["agent_id"])
        sess_code[r["id"]] = len(sess_code)
    last_t: dict = {}
    out_of_order = 0
    recs = []
    n = 0
    proc = subprocess.Popen(["gzcat", str(RAW / "computer_use_turns.jsonl.gz")], stdout=subprocess.PIPE, bufsize=1 << 22)
    for line in proc.stdout:
        n += 1
        r = orjson.loads(line)
        a = r.get("agent_action") or {}
        restart = False
        if "command" in a and not a.get("action"):
            act, text = "bash", a.get("command") or ""
            restart = bool(a.get("restart"))
        elif a.get("action") == "type":
            act, text = "type", a.get("text") or ""
        else:
            continue
        if not text and not restart:
            continue
        sid = r.get("session_id")
        t = parse_ts(r["created_at"])
        if sid in last_t and t < last_t[sid]:
            out_of_order += 1
        last_t[sid] = max(t, last_t.get(sid, t))
        verbs, rel, urls, dirs, clone = parse_command(text) if text else ([], "", [], [], None)
        if not verbs and not urls and not dirs and not restart:
            continue
        out_urls, hashes, new_branch = [], [], False
        if any(v.startswith(("git ", "gh ", "glab ")) for v in verbs):
            out_urls, hashes, new_branch = parse_git_output((r.get("output") or "") + "\n" + (r.get("error") or ""))
        # rows kept only for cwd tracking (a 'cd' or a shell restart) carry no command text
        recs.append((t, sess_agent.get(sid), sess_code.get(sid), act, verbs, rel if (verbs or urls) else None,
                     urls, dirs, restart, clone[0] if clone else None, clone[1] if clone else None,
                     out_urls, hashes, new_branch, bool(r.get("error"))))
    proc.wait()
    cols = ["t", "agent", "session", "act", "verbs", "cmd", "urls", "dirs", "restart", "clone_src",
            "clone_dir", "out_urls", "out_hashes", "new_branch", "error"]
    df = pl.DataFrame(recs, schema=cols, orient="row").with_columns(
        pl.col("agent").cast(pl.Int8), pl.col("session").cast(pl.Int32), pl.col("act").cast(pl.Categorical)
    ).sort("t").with_row_index("row")
    df.write_parquet(CMD_OUT, compression="zstd", compression_level=10)
    write_provenance("build_artifacts:scan", ["computer_use_turns", "computer_use_sessions", "agents"],
                     {"kept": "bash/type turns with git|gh|glab|deploy verbs or URLs (cmd text kept), plus "
                              "cd-only / restart turns (no text) for working-directory tracking",
                      "cmd_max_chars": MAX_CMD,
                      "turns_read": n, "session_out_of_order_turns": out_of_order})
    return f"scan: {n:,} turns read, {len(df):,} kept, file-order inversions within session {out_of_order:,}, " \
           f"{CMD_OUT.stat().st_size/1e6:.1f} MB, {time.time()-t0:.0f}s"

# ----------------------------------------------------------------------------- canonicalization

HOSTING = ("pages.dev", "workers.dev", "netlify.app", "vercel.app", "surge.sh", "web.app", "firebaseapp.com",
           "glitch.me", "replit.app", "repl.co", "onrender.com", "herokuapp.com", "fly.dev", "substack.com",
           "neocities.org", "itch.io", "wordpress.com", "blogspot.com", "carrd.co", "fourthwall.com", "loca.lt",
           "ngrok.io", "ngrok-free.app", "github.io", "gitlab.io", "streamlit.app", "hf.space", "telegra.ph")
GH_RESERVED = {"settings", "orgs", "features", "login", "logout", "join", "apps", "marketplace", "topics", "search",
               "notifications", "sponsors", "about", "pricing", "explore", "collections", "trending", "new",
               "codespaces", "issues", "pulls", "site", "contact", "enterprise", "security", "customer-stories",
               "readme", "team", "users", "account", "signup", "password_reset", "sessions", "dashboard", "watching",
               "stars", "github-copilot", "copilot", "events", "resources", "solutions"}
PRIVATE_HOST = re.compile(r"^(localhost|127\.|0\.0\.0\.0|10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.|\[)")
TRAIL = ".,;:!?)]}>*'\"`"
HYPHENS = str.maketrans({"‐": "-", "‑": "-", "‒": "-", "–": "-", "—": "-", "−": "-"})
SLD = {"co", "com", "org", "net", "ac", "gov", "edu", "ne", "or"}


def _clean(u: str) -> str:
    u = u.translate(HYPHENS).strip()
    while u and u[-1] in TRAIL:
        u = u[:-1]
    return u.replace("**", "")


def _regdomain(host: str) -> str:
    parts = host.split(".")
    if len(parts) >= 3 and parts[-2] in SLD and len(parts[-1]) == 2:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


def canon(url: str):
    """URL (with or without scheme) -> (kind, name, host, parent_name) or None if dropped."""
    u = _clean(url)
    m = re.match(r"^(?:[a-zA-Z][\w+.-]*://)?(?:[^@/\s]+@)?([^/\s?#]+)([^?#\s]*)", u)
    if not m:
        return None
    host = m.group(1).lower().rstrip(".")
    host = host.split(":")[0] if not host.startswith("[") else host
    if host.startswith("www."):
        host = host[4:]
    if not host or "." not in host or PRIVATE_HOST.match(host) or "redacted" in host or not re.match(r"^[a-z0-9.-]+$", host):
        return None
    segs = [s for s in m.group(2).split("/") if s]
    if host == "github.com":
        if len(segs) >= 2 and segs[0].lower() not in GH_RESERVED:
            o, r = segs[0].lower(), segs[1].lower().removesuffix(".git")
            repo = f"github.com/{o}/{r}"
            if len(segs) >= 5 and segs[2] in ("blob", "raw"):
                return ("file", f"{repo}:{'/'.join(segs[4:])}", host, repo)
            return ("repo", repo, host, None)
        return ("domain", "github.com", host, None)
    if host == "raw.githubusercontent.com" and len(segs) >= 4:
        repo = f"github.com/{segs[0].lower()}/{segs[1].lower()}"
        return ("file", f"{repo}:{'/'.join(segs[3:])}", "github.com", repo)
    if host == "gist.github.com" and len(segs) >= 2:
        return ("file", f"gist.github.com/{segs[1].lower()}", host, None)
    if host == "api.github.com":
        if len(segs) >= 3 and segs[0] == "repos":
            return ("repo", f"github.com/{segs[1].lower()}/{segs[2].lower()}", "github.com", None)
        return ("domain", "github.com", host, None)
    if host == "gitlab.com" and segs[:2] == ["api", "v4"]:
        if len(segs) >= 4 and segs[2] == "projects" and "%2f" in segs[3].lower():
            path = re.sub("%2f", "/", segs[3], flags=re.IGNORECASE).lower()
            return ("repo", "gitlab.com/" + path.removesuffix(".git"), host, None)
        return ("domain", "gitlab.com", host, None)
    if host == "gitlab.com":
        if "-" in segs:
            i = segs.index("-")
            proj, rest = segs[:i], segs[i + 1:]
        else:
            k = 3 if len(segs) >= 3 and [s.lower() for s in segs[:2]] == ["ai-village-agents", "village"] else 2
            proj, rest = segs[:k], []
            if k == 2 and [s.lower() for s in segs[:2]] == ["ai-village-agents", "village"]:
                proj = []
        if len(proj) >= 2 and proj[0].lower() not in ("users", "explore", "dashboard", "groups", "help", "api",
                                                       "oauth", "uploads", "assets", "search", "-"):
            repo = "gitlab.com/" + "/".join(p.lower() for p in proj).removesuffix(".git")
            if len(rest) >= 3 and rest[0] in ("blob", "raw"):
                return ("file", f"{repo}:{'/'.join(rest[2:])}", host, repo)
            return ("repo", repo, host, None)
        return ("domain", "gitlab.com", host, None)
    if host.endswith(".github.io"):
        owner = host[: -len(".github.io")]
        if segs and "." not in segs[0]:
            return ("site", f"{host}/{segs[0].lower()}", host, f"github.com/{owner}/{segs[0].lower()}")
        return ("site", host, host, f"github.com/{owner}/{host}")
    if host.endswith(".gitlab.io"):
        sub = host[: -len(".gitlab.io")]
        if sub == "ai-village-agents" and segs and "." not in segs[0]:
            return ("site", f"{host}/{segs[0].lower()}", host, f"gitlab.com/ai-village-agents/village/{segs[0].lower()}")
        base = re.sub(r"-[0-9a-f]{6}$", "", sub)
        return ("site", host, host, f"gitlab.com/ai-village-agents/village/{base}")
    if host == "docs.google.com" and len(segs) >= 3 and segs[1] == "d":
        return ("file", f"docs.google.com/{segs[0]}/{segs[2]}", host, None)
    if host == "docs.google.com" and len(segs) >= 4 and segs[0] == "forms" and segs[2] == "d":
        return ("file", f"docs.google.com/forms/{segs[3]}", host, None)
    if host == "drive.google.com" and len(segs) >= 3 and segs[0] == "file" and segs[1] == "d":
        return ("file", f"drive.google.com/file/{segs[2]}", host, None)
    if host == "forms.gle" and segs:
        return ("file", f"forms.gle/{segs[0]}", host, None)
    if host == "sites.google.com" and len(segs) >= 2 and segs[0] == "view":
        return ("site", f"sites.google.com/view/{segs[1].lower()}", host, None)
    if any(host == h or host.endswith("." + h) for h in HOSTING) and host.count(".") >= 2:
        return ("site", host, host, None)
    return ("domain", _regdomain(host), host, None)


BARE_RE = re.compile(r"(?<![\w/.@-])((?:github\.com|gitlab\.com|[a-z0-9-]+\.github\.io|[a-z0-9-]+\.gitlab\.io)"
                     r"/[^\s<>()\"'`\]]*)", re.IGNORECASE)
ORG_RE = re.compile(r"(?<![\w/.@-])ai-village-agents/(?:village/)?([A-Za-z0-9][A-Za-z0-9_.-]*[A-Za-z0-9_])")


def refs_in_text(text: str, urls: list | None = None):
    """[(how, raw_ref)] for URLs and scheme-less references in free text."""
    out = []
    if urls is None:
        urls = URL_RE.findall(text)
    out += [("url", u) for u in urls]
    stripped = URL_RE.sub(" ", text)
    out += [("bare", m.group(1)) for m in BARE_RE.finditer(stripped)]
    stripped = BARE_RE.sub(" ", stripped)
    out += [("org", m.group(1)) for m in ORG_RE.finditer(stripped)]
    return out

# ----------------------------------------------------------------------------- build


class Registry:
    def __init__(self):
        self.ids: dict = {}
        self.meta: list = []

    def get(self, kind, name, host, parent):
        k = (kind, name)
        if k not in self.ids:
            self.ids[k] = len(self.meta)
            self.meta.append({"artifact": len(self.meta), "kind": kind, "name": name, "host": host,
                              "parent_name": parent})
        return self.ids[k]


def build():
    t0 = time.time()
    reg = Registry()
    M = []  # (artifact, t, agent, speaker_kind, source, how, verb, room, message_id, ref_index)
    pending_names = []  # (name, t, agent, speaker_kind, source, how, verb, room, message_id, ref_index)

    def add_ref(how, ref, t, agent, sk, source, verb, room, mid, idx):
        if how == "org":
            pending_names.append((ref.lower().removesuffix(".git"), t, agent, sk, source, "bare", verb, room, mid, idx))
            return
        c = canon(ref)
        if c:
            M.append((reg.get(*c), t, agent, sk, source, how, verb, room, mid, idx))

    # chat
    cc = pl.read_parquet(OUT / "chat_core.parquet", columns=["message_id", "t", "room", "speaker_kind", "agent"])
    ct = pl.read_parquet(OUT / "chat_text.parquet")
    chat = cc.join(ct, on="message_id", how="left")
    for mid, t, room, sk, agent, text, urls in chat.iter_rows():
        text = text or ""
        if not urls and "github" not in text and "gitlab" not in text and "ai-village-agents" not in text:
            continue
        for how, ref in refs_in_text(text, urls or []):
            add_ref(how, ref, t, agent, str(sk), "chat", None, room, mid, None)
    n_chat = len(M)
    # intentions
    it = pl.read_parquet(OUT / "intentions.parquet").join(
        pl.read_parquet(OUT / "intentions_text.parquet"), on="event_index", how="left")
    for ei, t, agent, src, goal, short in it.select("event_index", "t", "agent", "source", "goal_text",
                                                    "short_text").iter_rows():
        seen = set()
        for txt in (goal or "", short or ""):
            for how, ref in refs_in_text(txt):
                if (how, ref) in seen:
                    continue
                seen.add((how, ref))
                add_ref(how, ref, t, agent, "agent", "intention", None, None, None, ei)
    n_int = len(M) - n_chat
    # actions (command sidecar)
    cmd = pl.read_parquet(CMD_OUT).sort("session", "t", "row")
    # working directory: explicit 'cd X' / 'git -C X' in the same command, else the last one earlier in the session
    cwd_col, how_col, last, last_s = [], [], None, None
    for sess, dirs, restart, verbs in cmd.select("session", "dirs", "restart", "verbs").iter_rows():
        if sess != last_s:
            last, last_s = None, sess
        if restart:
            last = None
        if dirs:
            cwd_col.append(dirs[-1]); how_col.append("cwd"); last = dirs[-1]
        else:
            cwd_col.append(last); how_col.append("session_cwd" if last else None)
    cmd = cmd.with_columns(pl.Series("cwd", cwd_col), pl.Series("cwd_how", how_col)).filter(
        (pl.col("verbs").list.len() > 0) | (pl.col("urls").list.len() > 0)).sort("t")
    clones = []  # (t, agent, dir, artifact)
    action_dirs = []  # (row, t, agent, dir, how, verb)
    for row, t, agent, verbs, cmdtxt, urls, cwd, cwd_how, csrc, cdir, out_urls in cmd.select(
            "row", "t", "agent", "verbs", "cmd", "urls", "cwd", "cwd_how", "clone_src", "clone_dir",
            "out_urls").iter_rows():
        verb = _main_verb(verbs)
        got = set()
        for u in urls:
            c = canon(u)
            if c:
                a = reg.get(*c)
                if a not in got:
                    got.add(a)
                    M.append((a, t, agent, "agent", "action", "url", verb, None, None, row))
        for how, ref in refs_in_text(cmdtxt or "", []):
            if how == "org":
                pending_names.append((ref.lower().removesuffix(".git"), t, agent, "agent", "action", "bare", verb,
                                      None, None, row))
            else:
                c = canon(ref)
                if c and reg.get(*c) not in got:
                    a = reg.get(*c); got.add(a)
                    M.append((a, t, agent, "agent", "action", "bare", verb, None, None, row))
        for u in out_urls:
            c = canon(u)
            if c and c[0] == "repo":
                a = reg.get(*c)
                if a not in got:
                    got.add(a)
                    M.append((a, t, agent, "agent", "action", "output", verb, None, None, row))
        if csrc and cdir:
            c = canon(csrc)
            if c and c[0] == "repo":
                clones.append((t, agent, cdir.lower(), reg.get(*c)))
        if cwd and verbs and not got:
            action_dirs.append((row, t, agent, cwd.lower(), str(cwd_how), verb))
    # resolve bare org names and directory names to repos
    by_name = defaultdict(list)
    for (kind, name), a in reg.ids.items():
        if kind == "repo":
            by_name[name.split("/")[-1]].append((name, a))

    def resolve(name, t):
        cands = by_name.get(name)
        if not cands:
            return None
        if len(cands) == 1:
            return cands[0][1]
        want = "gitlab.com" if t.date().isoformat() >= GITLAB_SWITCH else "github.com"
        pref = [a for nm, a in cands if nm.startswith(want + "/ai-village-agents")] or \
               [a for nm, a in cands if nm.startswith(want)]
        return pref[0] if len(pref) == 1 else None

    unresolved = Counter()
    for name, t, agent, sk, source, how, verb, room, mid, idx in pending_names:
        a = resolve(name, t)
        if a is None:
            unresolved["org:" + source] += 1
        else:
            M.append((a, t, agent, sk, source, how, verb, room, mid, idx))
    clone_map = defaultdict(list)
    for t, agent, d, a in sorted(clones, key=lambda x: x[0]):
        clone_map[(agent, d)].append((t, a))
    for row, t, agent, d, how, verb in action_dirs:
        a = None
        for tc, ac in clone_map.get((agent, d), []):
            if tc <= t:
                a = ac
        if a is None:
            a = resolve(d, t)
        if a is None:
            unresolved["dir"] += 1
            continue
        M.append((a, t, agent, "agent", "action", how, verb, None, None, row))
    # tables
    ment = pl.DataFrame(M, schema=["artifact", "t", "agent", "speaker_kind", "source", "how", "verb", "room",
                                   "message_id", "ref_index"], orient="row", infer_schema_length=None).with_columns(
        pl.col("artifact").cast(pl.Int32), pl.col("agent").cast(pl.Int8), pl.col("room").cast(pl.Int8),
        pl.col("ref_index").cast(pl.Int64),
        *[pl.col(c).cast(pl.Categorical) for c in ("speaker_kind", "source", "how", "verb")])
    ment = ment.unique(subset=["artifact", "source", "message_id", "ref_index"], keep="first").sort("t", "artifact")
    meta = pl.DataFrame(reg.meta)
    name2id = dict(zip(meta["name"].to_list(), meta["artifact"].to_list()))
    meta = meta.with_columns(pl.col("parent_name").replace_strict(name2id, default=None).alias("parent"),
                             pl.col("name").map_elements(lambda n: _regdomain(n.split("/")[0].split(":")[0]),
                                                         return_dtype=pl.Utf8).alias("domain"))
    first = ment.sort("t").group_by("artifact").agg(
        pl.col("t").first().alias("first_t"), pl.col("agent").first().alias("first_agent"),
        pl.col("speaker_kind").first().alias("first_speaker_kind"), pl.col("source").first().alias("first_source"),
        pl.col("t").last().alias("last_t"),
        (pl.col("source") == "chat").sum().cast(pl.Int32).alias("n_chat"),
        (pl.col("source") == "action").sum().cast(pl.Int32).alias("n_action"),
        (pl.col("source") == "intention").sum().cast(pl.Int32).alias("n_intention"),
        pl.len().cast(pl.Int32).alias("n_mentions"),
        pl.col("agent").drop_nulls().n_unique().cast(pl.Int16).alias("n_agents"))
    art = meta.join(first, on="artifact", how="inner").select(
        pl.col("artifact").cast(pl.Int32), pl.col("kind").cast(pl.Categorical), "name", "host", "domain",
        pl.col("parent").cast(pl.Int32), "first_t", "first_agent", "first_speaker_kind", "first_source", "last_t",
        "n_chat", "n_action", "n_intention", "n_mentions", "n_agents").sort("artifact")
    art.write_parquet(OUT / "artifacts.parquet", compression="zstd")
    ment.write_parquet(OUT / "artifact_mentions.parquet", compression="zstd")
    write_provenance("build_artifacts", ["chat_text (via chat_core/chat_text)", "intentions_text",
                                         "computer_use_turns (via artifact_commands_text)"],
                     {"canonicalization": "see module docstring", "unresolved": dict(unresolved),
                      "mentions_chat": n_chat, "mentions_intentions": n_int})
    return (f"build: {len(art):,} artifacts ({dict(Counter(art['kind'].cast(pl.Utf8).to_list()))}), "
            f"{len(ment):,} mentions ({dict(Counter(ment['source'].cast(pl.Utf8).to_list()))}), "
            f"unresolved {dict(unresolved)}, {time.time()-t0:.0f}s")


def _main_verb(verbs):
    if not verbs:
        return None
    for key in ("git push", "git clone", "git commit", "git pull", "git fetch", "gh repo", "glab repo", "deploy:"):
        for v in verbs:
            if v.startswith(key):
                return v if key != "deploy:" else "deploy"
    v = verbs[0]
    if v.startswith("fetch:"):
        return "fetch"
    return v if v.startswith(("git ", "gh ", "glab ")) else "other"


if __name__ == "__main__":
    what = sys.argv[1:] or ["scan", "build"]
    if "scan" in what:
        print(scan(), flush=True)
    if "build" in what:
        print(build(), flush=True)
