"""H44 shared helpers: paths, thread caps, holdout guards, period units, call categories.

Imported by scheme/build.py and analysis/*.py. Threads are capped at 2 before numpy / polars import (shared machine).
No agent text is ever written by any H44 script: command text is classified and hashed in memory only.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
           "NUMEXPR_NUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ[_v] = "2"

import datetime as dt  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
HYP = HERE.parent
ROOT = HYP.parents[1]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit, holdout_mask, load_holdout  # noqa: E402,F401

SH = ROOT / "data/processed/shared"
EMB = SH / "embeddings"
BS = ROOT / "data/processed/behavior_states"
OUT = ROOT / "data/processed/H44-erasure-reacquisition-thrash"
FIG = HYP / "figures"
SEED = 20261004
UTC = dt.timezone.utc
REGIME3_START = "2026-03-24"

# ----------------------------------------------------------------------------------------------- call categories
CATS = ["write", "talk", "room_read", "notes_read", "local_read", "remote_read", "run", "look", "gui_type", "gui",
        "monitor", "setup", "idle", "other"]
CAT = {c: i for i, c in enumerate(CATS)}           # priority order = list order (lower index wins inside a call)
REACQ = ["room_read", "notes_read", "local_read", "remote_read", "look"]
REACQ_IDX = [CAT[c] for c in REACQ]
CAT_LABEL = {"write": "write", "talk": "talk", "room_read": "room read", "notes_read": "notes read",
             "local_read": "local read", "remote_read": "remote read", "run": "run", "look": "look",
             "gui_type": "GUI type", "gui": "GUI", "monitor": "monitor", "setup": "setup", "idle": "idle",
             "other": "other"}

GUI_LOOK = {"screenshot", "get_pixel_coords_of_element", "cursor_position", "view_clipboard", "zoom"}
GUI_NAV = {"left_click", "scroll", "key", "mouse_move", "double_click", "triple_click", "middle_click", "right_click",
           "left_click_drag", "hold_key", "left_mouse_down", "left_mouse_up"}
EVENT_CAT = {"send_message_back_to_chat": "talk", "search_history": "room_read", "pause": "idle", "wait": "idle",
             "none": "other", "other": "other", "move_to_room": "other", "request_Google_sign_in": "other",
             "request_approval_for_unsolicited_outreach": "other", "request_human_helper": "other",
             "cancel_request_for_human_helper": "other", "type": "gui_type"}

SPLIT = re.compile(r"\s*(?:;|&&|\|\||\|)\s*")
ASSIGN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=\S*$")
SETUP_VERBS = {"exit", "cd", "export", "set", "source", ".", "mkdir", "touch", "chmod", "pushd", "popd", "unset", "alias",
               "umask", "true", ":", "clear", "shopt", "trap", "eval", "local", "declare"}
READ_VERBS = {"cat", "head", "tail", "less", "more", "grep", "egrep", "fgrep", "rg", "find", "ls", "tree", "wc", "stat",
              "diff", "cmp", "jq", "awk", "pwd", "which", "file", "du", "df", "realpath", "readlink", "md5sum",
              "sha256sum", "basename", "dirname", "column", "sort", "uniq", "cut", "nl", "xxd", "od", "strings",
              "type", "whereis", "printenv", "env", "echo", "printf", "id", "whoami", "hostname", "uname", "lsof",
              "zcat", "unzip"}
GIT_READ = {"status", "log", "show", "diff", "branch", "remote", "rev-parse", "ls-files", "blame", "reflog",
            "describe", "shortlog", "config", "tag", "ls-tree", "cat-file", "grep", "stash"}
GIT_REMOTE = {"fetch", "pull", "clone", "ls-remote"}
REMOTE_VERBS = {"curl", "wget", "http", "lynx", "w3m"}
GHGL_READ = {"view", "list", "status", "api", "browse", "search", "auth", "diff", "checks"}
RUN_VERBS = {"python", "python3", "node", "npm", "npx", "make", "pytest", "bash", "sh", "zsh", "codex", "tmux",
             "nohup", "timeout", "ffmpeg", "java", "go", "cargo", "ruby", "perl", "deno", "bun", "yarn", "pnpm",
             "pip", "pip3", "uv", "docker", "convert", "magick", "sqlite3", "firefox", "chromium", "google-chrome",
             "xdg-open", "xdotool", "dfrotz", "frotz", "gcc", "rustc", "tsc", "vite", "jekyll", "hugo", "pandoc",
             "openssl", "base64", "zip", "tar", "gzip", "rsync", "scp", "ssh", "cp", "mv", "rm", "ln", "sed", "tee",
             "patch", "git", "gh", "glab", "xargs", "for", "while", "if", "do", "then", "else", "fi", "done",
             "watch", "crontab", "systemctl", "service", "pkill", "killall"}
MON_VERBS = {"sleep", "ps", "top", "htop", "pgrep", "kill", "date", "uptime", "jobs", "wait", "free", "nproc", "time"}
NOTES_RX = re.compile(r"(note|memory|memo|todo|handoff|journal|diary|scratch|progress|checklist|context|plan|session)"
                      r"[\w./-]*", re.I)
WRITE_FLAG = re.compile(r"\s-X\s*['\"]?(POST|PUT|PATCH|DELETE)|--data|\s-d\s|\s-F\s|--form|--method\s+(POST|PUT|PATCH|DELETE)"
                        r"|\s-f\s", re.I)


def _verb(seg: str) -> tuple[str, list[str]]:
    toks = seg.strip().split()
    while toks and (ASSIGN.match(toks[0]) or toks[0] in ("sudo", "env", "command", "builtin", "exec", "nice", "time",
                                                         "DISPLAY=:0", "DISPLAY=:1")):
        toks = toks[1:]
    if not toks:
        return "", []
    v = toks[0].rsplit("/", 1)[-1]
    return v, toks[1:]


def classify_bash(cmd: str | None) -> str:
    """Category of a bash command without write evidence (write evidence is applied by the caller)."""
    if not cmd:
        return "other"
    segs = [s for s in SPLIT.split(cmd) if s.strip()]
    kinds = []
    for s in segs:
        v, args = _verb(s)
        if not v or v in SETUP_VERBS:
            kinds.append("setup")
            continue
        if v == "git":
            sub = next((a for a in args if not a.startswith("-")), "")
            kinds.append("local_read" if sub in GIT_READ else "remote_read" if sub in GIT_REMOTE else "run")
            continue
        if v in ("gh", "glab"):
            subs = [a for a in args if not a.startswith("-")][:2]
            if any(x in GHGL_READ for x in subs) and not WRITE_FLAG.search(" " + s + " "):
                kinds.append("remote_read")
            else:
                kinds.append("run")
            continue
        if v in REMOTE_VERBS:
            kinds.append("run" if WRITE_FLAG.search(" " + s + " ") else "remote_read")
            continue
        if v == "sed":
            kinds.append("local_read" if ("-n" in args and "-i" not in args) else "run")
            continue
        if v in READ_VERBS:
            if v in ("echo", "printf") or (v in ("env", "printenv", "id", "whoami", "hostname", "uname") and len(segs) > 1):
                kinds.append("setup")
                continue
            tgt = " ".join(a for a in args if not a.startswith("-"))
            kinds.append("notes_read" if (v in ("cat", "head", "tail", "less", "more", "grep", "rg", "awk", "wc", "jq",
                                                "nl") and NOTES_RX.search(tgt)) else "local_read")
            continue
        if v in MON_VERBS:
            kinds.append("monitor")
            continue
        if v in RUN_VERBS or v.startswith("./") or v.endswith((".sh", ".py", ".js")):
            kinds.append("run")
            continue
        kinds.append("other")
    subst = [k for k in kinds if k != "setup"]
    if not subst:
        return "setup"
    known = [k for k in subst if k != "other"]   # unparsed fragments (subshells, continuations) do not decide
    if not known:
        return "other"
    subst = known
    # a command that runs anything counts as run; it is a read only if every substantive segment reads (or monitors)
    if "run" in subst:
        return "run"
    if all(x in ("notes_read", "remote_read", "local_read", "monitor") for x in subst):
        for k in ("notes_read", "remote_read", "local_read", "monitor"):
            if k in subst:
                return k
    return "other" if "other" in subst else subst[0]


DIGITS = re.compile(r"\d+")


def norm_cmd(cmd: str | None) -> str | None:
    """Substantive segments of a command (setup segments such as cd / export dropped), digits collapsed: the loop-hash
    robustness variant (a loop re-issued with a new cd prefix or a new timestamp still matches)."""
    if not cmd:
        return None
    segs = []
    for s in SPLIT.split(cmd):
        v, _ = _verb(s)
        if v and v not in SETUP_VERBS:
            segs.append(" ".join(s.split()))
    return DIGITS.sub("#", " ; ".join(segs)) if segs else None


def nonholdout_days() -> pl.DataFrame:
    """Regime-III active PT days outside the locked holdout (calendar flag AND holdout_mask)."""
    cal = pl.read_parquet(SH / "calendar.parquet")
    hm = holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    cal = cal.with_columns(pl.Series("hm", hm))
    return cal.filter(~pl.col("holdout") & ~pl.col("hm") & (pl.col("pt_date") >= REGIME3_START)
                      & (pl.col("n_agent_events") > 0)).select("pt_date", "goal_no")


def holdout_days() -> set[str]:
    cal = pl.read_parquet(SH / "calendar.parquet")
    hm = holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    return {d for d, h, f in zip(cal["pt_date"], hm, cal["holdout"]) if h or f}


def refuse_holdout(pt_dates, what: str = "rows"):
    bad = set(pt_dates) & holdout_days()
    if bad:
        raise SystemExit(f"HOLDOUT GUARD: {len(bad)} holdout days in {what} (e.g. {sorted(bad)[:3]})")


def unit_map(include_holdout: bool = False) -> pl.DataFrame:
    """(pt_date, unit_id, period) for regime-III units; days listed in two units go to the later one."""
    pu = pl.read_parquet(SH / "period_units.parquet").filter(pl.col("regime") == "III")
    if not include_holdout:
        pu = pu.filter(~pl.col("holdout"))
    m = (pu.select("unit_id", "goal_no", "seq", "days").explode("days").rename({"days": "pt_date"})
         .sort("goal_no", "seq").unique("pt_date", keep="last"))
    return m.with_columns(pl.format("G{}", pl.col("goal_no").cast(pl.Utf8).str.zfill(2)).alias("period")).select(
        "pt_date", "unit_id", "period")


def write_provenance(params: dict | None = None, built_by: str = "hypotheses/H44-erasure-reacquisition-thrash/scheme/build.py",
                     tables: list[str] | None = None, out: Path | None = None):
    out = out or OUT
    prov = {"built_by": built_by, "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": tables or ["context_ledger_turns", "context_ledger_items", "call_windows", "actions",
                                             "actions_bash_head_fixed", "turn_outcomes (DQ3; command text read in memory, "
                                             "never stored)", "work_commits", "behavior_states_v3", "reply_pairs",
                                             "embeddings/statements + white32 (bge, gte)", "chat_core", "memory_stats",
                                             "period_units", "calendar"]}],
            "params": params or {}, "built_at": dt.datetime.now(UTC).isoformat(timespec="seconds")}
    out.mkdir(parents=True, exist_ok=True)
    (out / "_provenance.json").write_text(json.dumps(prov, indent=1))


def log(*a):
    print(f"[{dt.datetime.now().strftime('%H:%M:%S')}]", *a, flush=True)
