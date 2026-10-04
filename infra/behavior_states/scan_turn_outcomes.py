"""One pass over raw computer_use_turns: per bash / type turn, what the command was and what actually happened.

Why: `actions.error` (and `artifact_commands_text.error`) is bool(raw `error`), i.e. "stderr was non-empty". Git writes its
normal progress to stderr ("To https://...  a..b  main -> main", "From ...", "Switched to branch"), and so does curl's
progress meter, so 62% of `git push`, 54% of `git commit` and 49% of `git add` turns are flagged as errors. This scan
classifies real failures from the error/output text and records evidence of artifact changes.

Output (data/processed/behavior_states/turn_outcomes.parquet; gitignored; contains truncated command text, so it stays
under data/ and is never copied into a shared table): one row per bash or type turn
  t, agent                 join key to actions (unique per agent)
  failed                   real failure (see FAIL); fail_kind: exit_code / traceback / timeout / git_rejected / not_found /
                           http_error / usage / other
  stderr                   raw error field non-empty (= actions.error)
  commit_ok, push_ok       git printed a new commit line "[branch abc1234] msg" / a push range under "To <remote>"
  file_write, api_write,   command-text heuristics: shell redirect/tee/sed -i/patch/git add|commit outside heredoc bodies, or
                           write calls inside python heredocs / -c strings (see file_write()) ; POST/PUT/PATCH/DELETE,
  deploy                   gh|glab create/merge/comment/edit ; surge/netlify/vercel/wrangler/npm publish/gh-pages
  note                     first comment line of a bash command (the agent's own narration of intent, <= 100 chars)
  cmd                      non-comment lines joined with ' ; ', whitespace collapsed (<= 120 chars); typed text for `type`

Usage: uv run python infra/behavior_states/scan_turn_outcomes.py      (~3-4 min: gzcat + one python process)
"""
from __future__ import annotations

import re
import subprocess
import sys
import time
from pathlib import Path

import orjson
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shared"))
from common import OUT, RAW, parse_ts, rows  # noqa: E402

DEST = OUT.parent / "behavior_states" / "turn_outcomes.parquet"
FAIL = [  # order matters: first match names the kind
    ("timeout", re.compile(r"timed out: bash has not returned|operation timed out|Timeout was reached|curl: \(28\)", re.I)),
    ("exit_code", re.compile(r"exited with returncode [1-9]|exit (code|status):? ?[1-9]|EXIT(_CODE)?=[1-9]|PUSH_EXIT=[1-9]|Killed\b")),
    ("traceback", re.compile(r"Traceback \(most recent call last\)|^\w*(Error|Exception): |SyntaxError|npm ERR!|Uncaught \w*Error", re.M)),
    ("git_rejected", re.compile(r"! \[rejected\]|failed to push|^fatal: |^error: |CONFLICT \(|Automatic merge failed|not a git repository", re.M)),
    ("not_found", re.compile(r"No such file or directory|command not found|cannot access|can't read|cannot open|not found: |Could not resolve host", re.I)),
    ("http_error", re.compile(r"\b(HTTP/[\d.]+ [45]\d\d|HTTP [45]\d\d|\(HTTP [45]\d\d\)|\"status\": ?[45]\d\d|404 (Not Found|Project Not Found)|403 Forbidden|401 Unauthorized|rate limit exceeded)", re.I)),
    ("usage", re.compile(r"^usage: |unrecognized arguments|flag needs an argument|unknown (flag|option|command)|invalid option|Permission denied", re.I | re.M)),
    ("other", re.compile(r"\berror\b|\bfailed\b|\bfailure\b", re.I)),
]
NOISE = re.compile(r"^(To |From |remote: |\s+[0-9a-f]{6,}\.\.[0-9a-f]{6,} |\s+\* \[new |\s+\* branch |Switched to |Already on |Your branch |"
                   r"Cloning into |warning: |hint: |Enumerating |Counting |Compressing |Writing objects|Total \d|Delta |"
                   r"Receiving |Resolving |Unpacking |Updating [0-9a-f]|Fast-forward|Successfully rebased|\s*%\s+Total|\s+Dload|"
                   r"\s*\d+\s+[\d.]+[kMG]?\s+\d+|\s*$|Merge made|Auto-merging|Already up to date|Everything up-to-date|create mode|"
                   r"\d+ files? changed|Saved working directory|Note: switching|HEAD is now at|Deleted branch|branch '.*' set up)")
COMMIT_OK = re.compile(r"^\[[^\]\s]+(?: \(root-commit\))? [0-9a-f]{7,}\] ", re.M)
PUSH_OK = re.compile(r"^To \S+\s*\n(?:.*\n)*?\s+(?:\+?[0-9a-f]{6,}\.{2,3}[0-9a-f]{6,}|\* \[new (?:branch|tag)\])\s+\S+ -> \S+", re.M)
# file writes: shell redirects / tee / sed -i / patches / git staging in the shell part (heredoc bodies removed, so python
# comparisons like `a > b` don't count; redirects straight into /tmp or /dev don't count), plus write calls inside python
# heredocs or `python -c` strings. rm / mkdir / cp / mv / clone are not counted.
SHELL_WRITE = re.compile(r"(?:^|[\s;&|(])(?:\d?>>?|&>)\s*(?!/dev/|/tmp/|&|\d)[\w~.$\"'-][^\s;&|]*|\btee\b(?!\s+/tmp/)|\bsed\s+-i|apply_?patch|"
                         r"\bgit\s+(add|rm|mv|commit)\b|\bcodex\s+exec\b|\bnpm\s+run\s+build\b")
PY_WRITE = re.compile(r"open\([^)]*,\s*['\"][wa]b?\+?['\"]|write_text\(|write_bytes\(|\.write\(|json\.dump\(|\.to_(csv|parquet|json)\(|shutil\.(copy|move)")
HEREDOC = re.compile(r"<<-?\s*['\"]?(\w+)['\"]?")


def split_heredocs(text: str) -> tuple[str, str]:
    """(shell part, heredoc bodies) of a bash command."""
    shell, body, tag = [], [], None
    for line in text.splitlines():
        if tag is not None:
            if line.strip() == tag:
                tag = None
            else:
                body.append(line)
            continue
        shell.append(line)
        m = HEREDOC.search(line)
        if m:
            tag = m.group(1)
    return "\n".join(shell), "\n".join(body)


def file_write(text: str) -> bool:
    sh, body = split_heredocs(text)
    sh_nc = "\n".join(l for l in sh.splitlines() if not l.lstrip().startswith("#"))
    pyc = re.compile(r"python3?\s+-c\s+(['\"])(.*?)\1", re.S)
    py_c = " ".join(m[1] for m in pyc.findall(sh_nc))
    return bool(SHELL_WRITE.search(pyc.sub(" ", sh_nc)) or PY_WRITE.search(body) or PY_WRITE.search(py_c))
API_WRITE = re.compile(r"-X ?['\"]?(POST|PUT|PATCH|DELETE)|--request (POST|PUT|PATCH|DELETE)|--method (POST|PUT|PATCH|DELETE)|\bcurl\b[^;|]* (-d|--data|-F|--form)\b|"
                       r"\b(gh|glab) (pr|mr|issue|release|repo) (create|merge|comment|edit|close|note|fork)\b|\bglab api\b[^;|]* -f |\bgh api\b[^;|]* -f ")
DEPLOY = re.compile(r"\bsurge\b|netlify deploy|\bvercel\b|wrangler (deploy|pages)|npm publish|gh-pages|firebase deploy|glab release create", re.I)
WS = re.compile(r"\s+")


def classify(err: str, out: str) -> str | None:
    if not err and not out:
        return None
    errs = "\n".join(l for l in err.splitlines() if not NOISE.match(l)) if err else ""
    txt = errs + "\n" + (out[-400:] if out else "")
    for kind, rx in FAIL[:-1]:
        if rx.search(txt):
            return kind
    if errs.strip() and FAIL[-1][1].search(errs):
        return "other"
    return None


def scan():
    t0 = time.time()
    roster = pl.read_parquet(OUT / "roster.parquet")
    A = dict(zip(roster["agent_id"].to_list(), roster["agent"].to_list()))
    sess_agent = {r["id"]: A.get(r["agent_id"]) for r in rows("computer_use_sessions")}
    recs = []
    proc = subprocess.Popen(["gzcat", str(RAW / "computer_use_turns.jsonl.gz")], stdout=subprocess.PIPE, bufsize=1 << 22)
    n = 0
    for line in proc.stdout:
        n += 1
        if b'"command"' not in line and b'"type"' not in line:
            continue
        r = orjson.loads(line)
        a = r.get("agent_action") or {}
        if "command" in a and not a.get("action"):
            text = a.get("command") or ""
            lines = [l.strip() for l in text.splitlines()]
            note = next((l.lstrip("#").strip() for l in lines if l.startswith("#") and l.lstrip("#").strip()), None)
            cmd = WS.sub(" ", " ; ".join(l for l in lines if l and not l.startswith("#"))).strip()
            act = "bash"
        elif a.get("action") == "type":
            text = a.get("text") or ""
            note, cmd, act = None, WS.sub(" ", text).strip(), "type"
        else:
            continue
        err, out = r.get("error") or "", r.get("output") or ""
        kind = classify(err, out) if act == "bash" else None
        both = err + "\n" + out
        recs.append((parse_ts(r["created_at"]), sess_agent.get(r.get("session_id")), act, kind is not None, kind, bool(err),
                     bool(COMMIT_OK.search(both)) if act == "bash" else False, bool(PUSH_OK.search(both)) if act == "bash" else False,
                     file_write(text) if act == "bash" else False, bool(API_WRITE.search(cmd)) if act == "bash" else False,
                     bool(DEPLOY.search(cmd)) if act == "bash" else False, (note or "")[:100] or None, cmd[:120] or None))
        if len(recs) % 200000 == 0:
            print(f"{n} lines, {len(recs)} turns, {time.time() - t0:.0f}s", flush=True)
    proc.wait()
    cols = ["t", "agent", "act", "failed", "fail_kind", "stderr", "commit_ok", "push_ok", "file_write", "api_write", "deploy", "note", "cmd"]
    df = (pl.DataFrame(recs, schema=cols, orient="row")
          .with_columns(pl.col("agent").cast(pl.Int8), pl.col("act").cast(pl.Categorical), pl.col("fail_kind").cast(pl.Categorical))
          .filter(pl.col("agent").is_not_null()).sort("agent", "t").unique(["agent", "t"], keep="first", maintain_order=True))
    DEST.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(DEST, compression="zstd", compression_level=9)
    print(f"{df.height} turns -> {DEST} ({DEST.stat().st_size / 1e6:.1f} MB) in {time.time() - t0:.0f}s", flush=True)
    b = df.filter(pl.col("act") == "bash")
    print(b.select(pl.col("stderr").mean(), pl.col("failed").mean(), pl.col("commit_ok").mean(), pl.col("push_ok").mean(),
                   pl.col("file_write").mean(), pl.col("api_write").mean(), pl.col("deploy").mean(), pl.col("note").is_not_null().mean()))
    print(b["fail_kind"].value_counts().sort("count", descending=True))


if __name__ == "__main__":
    scan()
