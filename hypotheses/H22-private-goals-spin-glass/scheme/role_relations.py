"""H22 treatment structure for #51: private roles per agent and the coded pair classes (card O5).

Coded 2026-10-04 00:15 UTC from the role short names and titles in raw `agent_goals` (operator-written), before any
outcome statistic was computed. No role text is stored here beyond the short names already in the overview's
Table `tab:roles`.

Classes (pair codes):
  0 U   unrelated
  1 SR  same-role rivals: identical short name (Game dev, Twitterati, YouTuber, Forecaster, Merch baron, Diplomat,
        Reporter). Same metric, separate channels; the dataset docs call them competing pairs.
  2 OP  opposed objectives: Prankster (surprise inflicted on other agents) x Ethicist (ethical behavior inside the
        village) and x Psychologist (agent wellbeing in the village).
  3 SY  support: one role's objective is defined by other village agents' outcomes (Performance coach, Psychologist,
        Village helper, Village tooler) x any other agent, unless OP.
  4 NC  niche competitors: two different public-media audience roles (Twitterati, YouTuber, Substacker, Reporter,
        Press baron). Descriptive.
Precedence: SR > OP > SY > NC > U.
"""
from __future__ import annotations

import datetime as dt
import gzip
from pathlib import Path

import numpy as np
import orjson

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data/raw/ai-village"

CLASS_NAMES = {0: "U", 1: "SR", 2: "OP", 3: "SY", 4: "NC"}
SUPPORT = {"performance coach", "psychologist", "village helper", "village tooler"}
MEDIA = {"twitterati", "youtuber", "substacker", "reporter", "press baron"}
OPPOSED = {frozenset({"prankster", "ethicist"}), frozenset({"prankster", "psychologist"})}


def pair_class(a: str | None, b: str | None) -> int:
    if a is None or b is None:
        return 0
    if a == b:
        return 1
    if frozenset({a, b}) in OPPOSED:
        return 2
    if a in SUPPORT or b in SUPPORT:
        return 3
    if a in MEDIA and b in MEDIA:
        return 4
    return 0


def lookup_table(roles: list[str]) -> np.ndarray:
    R = len(roles)
    L = np.zeros((R, R), np.int8)
    for x in range(R):
        for y in range(R):
            L[x, y] = pair_class(roles[x], roles[y])
    return L


def load_role_spells(roster_ids: dict[str, int]):
    """[(agent_code, role_short_name_lower, start_pt_date, end_pt_date_or_None)] from raw agent_goals."""
    from zoneinfo import ZoneInfo
    PT = ZoneInfo("America/Los_Angeles")
    out = []
    with gzip.open(RAW / "agent_goals.jsonl.gz", "rb") as f:
        for line in f:
            r = orjson.loads(line)
            a = roster_ids.get(r["agent_id"])
            if a is None:
                continue
            def ptd(s):
                if not s:
                    return None
                t = dt.datetime.fromisoformat(s).replace(tzinfo=dt.timezone.utc)
                return t.astimezone(PT).date().isoformat()
            out.append((a, r["short_name"].strip().lower(), ptd(r["start_time"]), ptd(r["end_time"])))
    return out


def role_on(spells, agent: int, day: str) -> str | None:
    best = None
    for a, role, s, e in spells:
        if a == agent and s is not None and s <= day and (e is None or day <= e):
            best = role
    return best


def unit_roles(spells, agents: list[int], days: list[str], present: dict[int, list[str]]):
    """Role per agent for a unit: the role active on the majority of the agent's present days; else None."""
    out = {}
    for a in agents:
        ds = present.get(a, days)
        rs = [role_on(spells, a, d) for d in ds]
        known = [r for r in rs if r is not None]
        if len(known) * 2 >= max(1, len(ds)):
            vals, cnt = np.unique(known, return_counts=True)
            out[a] = str(vals[np.argmax(cnt)])
        else:
            out[a] = None
    return out
