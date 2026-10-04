"""H14 round 1b scheme (improved data, 2026-10-04): per-record flags for the corrected state spaces.

The round-1 builder (`build_states.py`) is unchanged and still runnable; this script adds what round 1 could not use:
  * shell sub-classes from `actions_bash_head_fixed.bash_head_fixed` (regime-III coverage 12.8% -> 99.6%) plus
    the per-turn change evidence in `behavior_states/turn_outcomes.parquet` (commit/push/file write/API write/deploy).
    Wrapper heads (cd, export, VAR=..., for, ...) are resolved to the first real command from the command text, which
    is read in memory only; nothing but the class code is written.
  * the scaffold/agent split used by H56 for its "agent-only chain": infrastructure-error turns (`error_class` in
    timeout/vm/resource/network) and calls whose start the scaffold set (`call_windows.gap_kind` in after_summary,
    marker, session_start, first_of_day). `actions_bash_head_fixed.system_class` is constant `none` (known issue).
  * real task failures (`turn_outcomes.failed`) instead of `actions.error` (stderr non-empty), for descriptives.

Input: shared `states_turn.parquet` (the consolidated H14 builder, identical records), non-holdout rows only.
Output: data/processed/H14-behavior-entropy-production/r1b/records_r1b.parquet
  agent, t, pt_date, goal_no, regime, act (round-1 fine class), coarse, sh (shell sub-class code, -1 if not bash),
  infra (bool), sgap (bool), failed (bool), and _provenance.json (key `r1b_records`).

Usage: uv run python hypotheses/H14-behavior-entropy-production/scheme/build_r1b.py
"""
from __future__ import annotations

import os

os.environ.setdefault("POLARS_MAX_THREADS", "2")

import datetime as dt
import json
import re
import sys
from pathlib import Path

import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit, holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H14-behavior-entropy-production/r1b"
TO = ROOT / "data/processed/behavior_states/turn_outcomes.parquet"

SHELL_SUB = ["vcs", "net", "run", "read", "write", "wait", "sh_other"]
INFRA_ERR = ["timeout", "vm", "resource", "network"]
SCAFFOLD_GAPS = ["after_summary", "marker", "session_start", "first_of_day"]
CLAUDE_CODE_AGENT = 19

VCS = {"git", "gh", "glab"}
NET = {"curl", "wget", "ssh", "scp", "http", "https", "nc", "ping", "dig", "rsync"}
RUN = {"python", "python3", "node", "npm", "npx", "codex", "bash", "sh", "zsh", "pip", "pip3", "nohup", "tmux", "screen",
       "firefox", "chromium", "google-chrome", "xdotool", "dfrotz", "make", "pytest", "uv", "deno", "java", "go", "cargo",
       "ruby", "perl", "php", "docker", "yarn", "pnpm", "bun", "ts-node", "tsc", "jest", "playwright", "xvfb-run",
       "convert", "ffmpeg", "sqlite3", "psql", "apt-get", "apt", "brew", "systemctl", "service", "crontab", "at", "kill",
       "pkill", "killall", "xclip", "xdg-open", "open"}
READ = {"cat", "grep", "ls", "head", "tail", "find", "wc", "rg", "pwd", "which", "ps", "jq", "awk", "nl", "date", "less",
        "more", "diff", "stat", "file", "du", "df", "tree", "whoami", "printenv", "env", "md5sum", "sha256sum", "sort",
        "uniq", "cut", "realpath", "basename", "dirname", "readlink", "type", "command", "hostname", "uname", "id", "top",
        "free", "lsof", "netstat", "history", "column", "xxd", "od", "strings", "comm", "test", "[", "column", "base64"}
WRITE = {"sed", "echo", "printf", "cp", "mv", "rm", "mkdir", "touch", "tee", "chmod", "ln", "tar", "unzip", "zip",
         "patch", "truncate", "install", "rmdir", "gzip", "gunzip"}
WAIT = {"sleep", "wait"}
WRAP = {"cd", "export", "set", "source", ".", "true", "false", "unset", "pushd", "popd", "alias", "for", "do", "done",
        "if", "then", "else", "fi", "while", "until", "local", "declare", "eval", "exec", "time", "sudo", "timeout", "trap",
        "shopt", "umask", "builtin", "{", "}", "(", ")", "!", "case", "esac", "function", "return", "exit", "read"}
_SPLIT = re.compile(r"&&|\|\||;|\||\n")
_ASSIGN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
_SKIP = re.compile(r"^\s*(?:#.*)?$")


def first_real_command(cmd: str | None) -> str | None:
    """First non-wrapper command word of a (possibly truncated) bash command; None if none is found."""
    if not cmd:
        return None
    lines = [ln for ln in cmd.split("\n") if not _SKIP.match(ln)]
    for part in _SPLIT.split("\n".join(lines)):
        toks = part.strip().split()
        i = 0
        while i < len(toks) and (_ASSIGN.match(toks[i]) or toks[i] in WRAP):
            if toks[i] in ("cd", "pushd", "source", ".", "timeout"):
                i += 2           # skip the argument too
            else:
                i += 1
        if i < len(toks):
            w = toks[i].split("/")[-1]
            if w and not _ASSIGN.match(w) and w not in WRAP:
                return w[:24]
    return None


def head_class(h: str | None) -> str:
    if h is None:
        return "sh_other"
    if h in VCS:
        return "vcs"
    if h in NET:
        return "net"
    if h in WAIT:
        return "wait"
    if h in READ:
        return "read"
    if h in WRITE:
        return "write"
    if h in RUN or h.endswith(".py") or h.endswith(".sh") or h.endswith(".js") or h.startswith("./"):
        return "run"
    return "sh_other"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    st = pl.read_parquet(SH / "states_turn.parquet").filter(~pl.col("holdout"))
    assert not any(holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list())), "holdout rows in the H14 r1b scheme"
    st = st.filter(pl.col("agent") != CLAUDE_CODE_AGENT)
    a = pl.read_parquet(SH / "actions.parquet", columns=["t", "agent", "action"]).with_row_index("row")
    b = pl.read_parquet(SH / "actions_bash_head_fixed.parquet", columns=["row", "t", "bash_head_fixed", "error_class"])
    a = a.join(b.rename({"t": "t_b"}), on="row", how="left")
    assert (a["t"] == a["t_b"]).all(), "actions_bash_head_fixed is not row-aligned with actions"
    a = a.unique(["agent", "t"], keep="first").select(
        "agent", "t", pl.col("bash_head_fixed").cast(pl.Utf8).alias("head"), pl.col("error_class").cast(pl.Utf8))
    to = (pl.read_parquet(TO, columns=["t", "agent", "act", "failed", "commit_ok", "push_ok", "file_write", "api_write",
                                       "deploy", "cmd"])
          .unique(["agent", "t"], keep="first"))
    # resolve wrapper heads from the command text, in memory; then drop the text
    heads = to.select("agent", "t", "cmd")
    real = [first_real_command(c) for c in heads["cmd"].to_list()]
    to = to.with_columns(pl.Series("head_cmd", real, dtype=pl.Utf8)).drop("cmd")
    cw = (pl.read_parquet(SH / "call_windows.parquet", columns=["agent", "t_first", "gap_kind", "holdout"])
          .filter(~pl.col("holdout")).select("agent", pl.col("t_first").alias("t"), pl.col("gap_kind").cast(pl.Utf8))
          .unique(["agent", "t"], keep="first"))
    st = (st.join(a, on=["agent", "t"], how="left").join(to, on=["agent", "t"], how="left")
          .join(cw, on=["agent", "t"], how="left").sort("agent", "t"))
    is_bash = st["kind"].cast(pl.Utf8) == "bash"
    head = st["head"].to_list()
    hcmd = st["head_cmd"].to_list()
    flags = st.select(pl.col("commit_ok").fill_null(False), pl.col("push_ok").fill_null(False),
                      pl.col("file_write").fill_null(False), pl.col("api_write").fill_null(False),
                      pl.col("deploy").fill_null(False))
    co, pu, fw, aw, de = (flags[c].to_list() for c in flags.columns)
    sh = []
    n_wrap_resolved = 0
    for i, ib in enumerate(is_bash.to_list()):
        if not ib:
            sh.append(-1)
            continue
        h = head[i]
        if h is None or h in WRAP or _ASSIGN.match(h + "=") and h.isupper():
            if hcmd[i] is not None:
                h = hcmd[i]
                n_wrap_resolved += 1
        if co[i] or pu[i]:
            c = "vcs"
        elif aw[i] or de[i]:
            c = "net"
        else:
            c = head_class(h)
            if c in ("sh_other", "read") and fw[i]:
                c = "write"
        sh.append(SHELL_SUB.index(c))
    st = st.with_columns(pl.Series("sh", sh, dtype=pl.Int8),
                         pl.col("error_class").is_in(INFRA_ERR).fill_null(False).alias("infra"),
                         pl.col("gap_kind").is_in(SCAFFOLD_GAPS).fill_null(False).alias("sgap"),
                         pl.col("failed").fill_null(False))
    out = st.select("agent", "t", "pt_date", "goal_no", "regime", "kind", "act", "coarse", "sh", "infra", "sgap", "failed")
    out.write_parquet(OUT / "records_r1b.parquet", compression="zstd")
    b_ = out.filter(pl.col("sh") >= 0)
    audit = {"records": out.height, "bash": b_.height, "wrapper_heads_resolved_from_text": n_wrap_resolved,
             "shell_sub_mix_by_regime": {r: {SHELL_SUB[k]: int(v) for k, v in g.group_by("sh").len().sort("sh").iter_rows()}
                                         for (r,), g in b_.group_by("regime")},
             "infra_records": int(out["infra"].sum()), "scaffold_call_starts": int(out["sgap"].sum()),
             "failed_bash_share": float(b_["failed"].mean()) if b_.height else None}
    (OUT / "records_r1b_audit.json").write_text(json.dumps(audit, indent=1))
    prov_path = ROOT / "data/processed/H14-behavior-entropy-production/_provenance.json"
    prov = json.loads(prov_path.read_text()) if prov_path.exists() else {}
    prov["r1b_records"] = {
        "built_by": "hypotheses/H14-behavior-entropy-production/scheme/build_r1b.py", "git_commit": git_commit(),
        "inputs": [{"source": "ai-village", "revision": REVISION,
                    "tables": ["shared/states_turn", "shared/actions", "shared/actions_bash_head_fixed", "shared/call_windows",
                               "behavior_states/turn_outcomes (flags; command text in memory only)"]}],
        "params": {"shell_sub": SHELL_SUB, "infra_error_classes": INFRA_ERR, "scaffold_gap_kinds": SCAFFOLD_GAPS,
                   "days": "non-holdout only"},
        "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    prov_path.write_text(json.dumps(prov, indent=1))
    print(json.dumps(audit, indent=1))


if __name__ == "__main__":
    main()
