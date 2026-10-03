"""Shared helpers for the Phase 0 tables: paths, streaming readers, time/goal/regime/holdout.

All outputs go to data/processed/shared/ as zstd parquet with a _provenance.json.
Text never goes into core tables; only into *_text sidecars.
"""
from __future__ import annotations

import datetime as dt
import gzip
import hashlib
import json
import re
import subprocess
from pathlib import Path
from zoneinfo import ZoneInfo

import orjson

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/ai-village"
OUT = ROOT / "data/processed/shared"
REVISION = "838b4150303ca8228e8edb432d8b8ccae353d258"
PT = ZoneInfo("America/Los_Angeles")
UTC = dt.timezone.utc

REGIME_BOUNDS = [("I", None, "2026-02-25"), ("II", "2026-02-25", "2026-03-24"), ("III", "2026-03-24", None)]


def rows(name: str):
    """Stream a raw jsonl.gz table as dicts."""
    with gzip.open(RAW / f"{name}.jsonl.gz", "rb") as f:
        for line in f:
            yield orjson.loads(line)


def parse_ts(s: str | None) -> dt.datetime | None:
    """Raw timestamps are UTC without a zone suffix ('2025-12-29 18:49:21.291984')."""
    if not s:
        return None
    return dt.datetime.fromisoformat(s.replace("Z", "")).replace(tzinfo=UTC)


def pt_date(t: dt.datetime) -> str:
    return t.astimezone(PT).date().isoformat()


def regime(t: dt.datetime) -> str:
    d = t.date().isoformat()
    for name, lo, hi in REGIME_BOUNDS:
        if (lo is None or d >= lo) and (hi is None or d < hi):
            return name
    return "?"


def short_hash(s: str | None) -> str | None:
    """Stable pseudonym for human speaker ids (no identities in processed tables)."""
    return None if s is None else hashlib.sha1(s.encode()).hexdigest()[:10]


def load_goals():
    """Village goals sorted by start, with 1-based goal numbers and UTC bounds."""
    goals = sorted(rows("village_goals"), key=lambda g: g["start_time"])
    out = []
    for i, g in enumerate(goals, 1):
        out.append({"goal_no": i, "start": parse_ts(g["start_time"]), "end": parse_ts(g["end_time"]),
                    "goal": g["goal"].strip()})
    return out


class GoalLookup:
    def __init__(self):
        self.goals = load_goals()

    def __call__(self, t: dt.datetime) -> int:
        n = 0
        for g in self.goals:
            if t >= g["start"]:
                n = g["goal_no"]
            else:
                break
        return n  # 0 = before the first goal


def load_holdout():
    return json.loads((ROOT / "hypotheses/holdout.json").read_text())


def holdout_mask(pt_dates, goal_nos):
    """True where a row is in the locked holdout (exclude from exploration)."""
    h = load_holdout()
    held_goals = set(h["goal_periods_held_out"])
    wins = [(w["start"], w["end"]) for w in h["ne_windows"]]
    return [(g in held_goals) or any(s <= d < e for s, e in wins) for d, g in zip(pt_dates, goal_nos)]


def git_commit() -> str:
    r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain"], capture_output=True, text=True).stdout
    return (r.stdout.strip() or "none") + ("+uncommitted" if dirty.strip() else "")


def write_provenance(name: str, tables: list[str], params: dict | None = None):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "_provenance.json"
    prov = json.loads(path.read_text()) if path.exists() else {}
    prov[name] = {"built_by": f"infra/shared/{name}.py", "git_commit": git_commit(),
                  "inputs": {"source": "ai-village", "revision": REVISION, "tables": tables},
                  "params": params or {}, "built_at": dt.datetime.now(UTC).isoformat()}
    path.write_text(json.dumps(prov, indent=1))


AGENT_NAME_RE_CACHE: dict = {}


def mention_regexes(agents):
    """Regexes for agent names in chat (estimates). Same rules as the overview's planned mentions."""
    pats = {}
    for a in agents:
        name = a["name"]
        if name.startswith("[Temporary]") or "Claude Code" in name:
            continue
        aliases = {name}
        if name.startswith("Claude "):
            aliases.add(name[len("Claude "):])
        if name.endswith(" Pro"):
            aliases.add(name[: -len(" Pro")])
        aliases = {x for x in aliases if len(x) >= 4 or x in ("o1", "o3")}
        if not aliases:  # an empty alternation would match every message (the 2026-10-03 `o1` bug)
            continue
        alt = "|".join(re.escape(x) for x in sorted(aliases, key=len, reverse=True))
        flags = 0 if name in ("o1", "o3") else re.IGNORECASE
        pats[a["id"]] = re.compile(rf"(?<![\w.])(?:{alt})(?![\w]|\.\d)", flags)
    return pats


URL_RE = re.compile(r"https?://[^\s<>()\"'`\]]+")


def load_whitener(regime_name: str, dim: int = 32):
    """Return W(x) mapping raw embeddings (n x 384) to whitened, centered n x dim coordinates for a regime.

    Fitted on non-holdout statements by infra/shared/build_agent_vectors.py."""
    import numpy as np
    z = np.load(OUT / "embeddings" / f"whitening_{regime_name}.npz")
    mu, U, w = z["mean"], z["components"][:, :dim], z["eigenvalues"][:dim]

    def W(x):
        return ((np.asarray(x, dtype=np.float32) - mu) @ U) / np.sqrt(w)
    return W
