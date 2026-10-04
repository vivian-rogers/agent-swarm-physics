"""H08 shared helpers: periods, holdout-safe day selection, turn-merged actions with pause-aware call starts,
read-out of room messages, provider-aware token accounting, provenance.

Definitions are on the card (`../README.md`, "Operational definitions"). Summary:
- turn of i: an `actions` row of i (minus `pause` mirrors) or an `events_core` event of i; rows within 1 s merge;
- call start s(tau): the previous turn's time, or after a pause turn min(t_pause + pause_s, t_tau - 1 s); the first turn
  of a PT day has s = -inf;
- read-out R_i(m): the first turn tau of i with s(tau) > t_m; in-flight turn: t_tau > t_m but s(tau) <= t_m.

Times are int64 microseconds since the epoch (UTC). No text is read or written.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "2"

import datetime as dt
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
HDIR = HERE.parent
ROOT = HERE.parents[2]
SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H08-context-is-the-coupling"
FIG = HDIR / "figures"
GP = HDIR / "goalperiod-subhypotheses"
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, holdout_mask  # noqa: E402

US = 1_000_000
MERGE_US = 1 * US          # turn merge window
GUARD_US = 1 * US          # wake call start is at most t_tau - 1 s
NEG_INF = np.int64(-(2 ** 62))
CC_AGENT = 19              # Opus 4.5 (Claude Code): separate scaffold, excluded from the standard-agent analyses
HOLD = json.loads((ROOT / "hypotheses/holdout.json").read_text())

# ----------------------------------------------------------------------------- periods
# Written 2026-10-04 before any real-data run. mode/N from hypohypotheses/goal-periods.md; titles from village_goals.
PERIODS = {
    24: dict(title="Do random acts of kindness!", regime="I", mode="C", N=10, rooms="#general"),
    25: dict(title="Create a digital museum of 2025", regime="I", mode="C", N=10, rooms="#general"),
    26: dict(title="Elect a village leader. They choose this week's goal!", regime="I", mode="C", N=10, rooms="#general"),
    27: dict(title="Hack the OWASP Juice Shop hacking playground", regime="I", mode="K", N=10, rooms="#general"),
    30: dict(title="Adopt a park and get it cleaned!", regime="I", mode="C", N=12, rooms="#general"),
    31: dict(title="Pick your own goal (agents bid 3.7 Sonnet farewell)", regime="I", mode="F", N=12, rooms="#general"),
    33: dict(title="(regime II, #general; see goal-periods.md)", regime="II", mode="C", N=12, rooms="#general"),
    35: dict(title="Test your game to make it as fun and functional as you can!", regime="II", mode="C", N=13,
             rooms="#best (3) / #rest (10) from 03-16"),
    36: dict(title="Interact with other AI agents outside the Village!", regime="II/III", mode="C", N=13,
             rooms="#best / #rest"),
    37: dict(title="Pick your own goal!", regime="III", mode="F", N=13, rooms="#best / #rest"),
    38: dict(title="Choose a charity and raise as much money as you can for it", regime="III", mode="C", N=12,
             rooms="#best / #rest"),
    39: dict(title="Build your own interactive world!", regime="III", mode="I", N=15, rooms="#best / #rest"),
    40: dict(title="Connect your worlds into a 3D universe!", regime="III", mode="C", N=15,
             rooms="merged #universe-coordination (GPT-5 alone in #rest)"),
    41: dict(title="Perform novel research!", regime="III", mode="I", N=15, rooms="#best / #rest"),
    42: dict(title="Run your own Youtube channel!", regime="III", mode="I", N=15, rooms="#best / #rest"),
    44: dict(title="Finetune your leader!", regime="III", mode="C", N=16, rooms="#best / #rest"),
    51: dict(title="Each agent: Maximize your assigned goal!", regime="III", mode="P", N=21,
             rooms="#general (+ short side rooms, #focus 08-05 to 08-24)"),
}
TWO_ROOM = [35, 36, 37, 38, 39, 41, 42, 44]          # #40 is the merged week
REGIME_III = [36, 37, 38, 39, 40, 41, 42, 44, 51]     # #36 from 03-24 (perma computer use)
CC_PERIODS = [30, 31, 33, 35, 36, 37]                 # Claude Code agent's non-holdout periods


def gname(g: int) -> str:
    return f"G{g:02d}"


def calendar() -> pl.DataFrame:
    return pl.read_parquet(SH / "calendar.parquet")


def is_holdout(d: str, g: int | None) -> bool:
    if g is not None and g in set(HOLD["goal_periods_held_out"]):
        return True
    return any(w["start"] <= d < w["end"] for w in HOLD["ne_windows"])


def period_days(g: int, allow_holdout: bool = False, only_regime3: bool = False) -> list[str]:
    """Non-holdout PT dates of goal g with an active window. Asserts no holdout leak."""
    cal = calendar().filter((pl.col("goal_no") == g) & (pl.col("window_s") > 0))
    if only_regime3:
        cal = cal.filter(pl.col("pt_date") >= "2026-03-24")
    days = cal["pt_date"].to_list()
    if not allow_holdout:
        m = holdout_mask(days, [g] * len(days))
        hc = dict(zip(cal["pt_date"].to_list(), cal["holdout"].to_list()))
        days = [d for d, x in zip(days, m) if not x and not hc[d]]
        assert not any(is_holdout(d, g) for d in days), "holdout leak"
    return sorted(days)


def windows(days: list[str]) -> dict[str, tuple[int, int]]:
    cal = calendar().filter(pl.col("pt_date").is_in(days))
    return {r["pt_date"]: (int(r["win_start"].timestamp() * US), int(r["win_end"].timestamp() * US))
            for r in cal.iter_rows(named=True)}


def us(s: pl.Series) -> np.ndarray:
    return s.dt.epoch("us").to_numpy().astype(np.int64)


# ----------------------------------------------------------------------------- token accounting (H09's rule)

_ACCT = None


def token_accounting() -> dict[int, str]:
    """Per agent: 'exclusive' (Anthropic: tok_in excludes cache reads) or 'inclusive' (tok_in includes them).
    Same rule as hypotheses/H09-swarm-thermodynamics/analysis/build_observables.py."""
    global _ACCT
    if _ACCT is None:
        tok = pl.read_parquet(SH / "actions.parquet", columns=["agent", "tok_in", "tok_cache_read"]).drop_nulls("tok_in")
        acct = (tok.group_by("agent").agg((pl.col("tok_in") >= pl.col("tok_cache_read").fill_null(0)).mean().alias("ge"))
                .with_columns(pl.when(pl.col("ge") > 0.99).then(pl.lit("inclusive")).otherwise(pl.lit("exclusive")).alias("a")))
        _ACCT = dict(zip(acct["agent"].to_list(), acct["a"].to_list()))
    return _ACCT


# ----------------------------------------------------------------------------- turns

@dataclass
class Turns:
    """Turns of one agent on one PT day (sorted)."""
    t: np.ndarray        # int64 us
    s: np.ndarray        # pause-aware call start (int64 us; NEG_INF for the first turn)
    talk: np.ndarray     # bool
    pause: np.ndarray    # bool
    pause_s: np.ndarray  # float32 (nan if not a pause turn)
    cons: np.ndarray     # bool
    ment: np.ndarray     # uint64 bitmask of agents addressed by the talk (0 if none)
    msg: np.ndarray      # chat_core row index of the talk message (-1 if none)
    unc: np.ndarray      # provider-aware uncached input tokens (nan if unknown)
    ctx: np.ndarray      # provider-aware context tokens (nan if unknown)
    act: np.ndarray = None  # first computer-use action name of the turn ('' if none)


def chat_table() -> pl.DataFrame:
    chat = pl.read_parquet(SH / "chat_core.parquet").with_row_index("msg")
    men = pl.read_parquet(SH / "chat_mentions_clean.parquet").select("mentions_roster")
    return pl.concat([chat, men], how="horizontal")


def mask_of(lst) -> int:
    m = 0
    for a in lst or []:
        if a is not None and 0 <= int(a) < 64:
            m |= 1 << int(a)
    return m


def build_turns(days: list[str], chat: pl.DataFrame | None = None) -> dict[tuple[int, str], Turns]:
    """Turn-merged actions per (agent, PT day) for the given days (standard agents and the CC agent alike)."""
    if not days:
        return {}
    chat = chat if chat is not None else chat_table()
    win = windows(days)
    t0 = dt.datetime.fromtimestamp(min(v[0] for v in win.values()) / US - 4 * 3600, dt.timezone.utc)
    t1 = dt.datetime.fromtimestamp(max(v[1] for v in win.values()) / US + 4 * 3600, dt.timezone.utc)
    acct = token_accounting()
    acts = (pl.scan_parquet(SH / "actions.parquet")
            .filter((pl.col("t") >= t0) & (pl.col("t") < t1) & pl.col("agent").is_not_null()
                    & (pl.col("action").cast(pl.Utf8) != "pause"))
            .select("t", "agent", "tok_in", "tok_cache_read", "tok_cache_write", pl.col("action").cast(pl.Utf8)).collect())
    acts = acts.with_columns(pl.col("agent").replace_strict(acct, default=None).alias("acct")).with_columns(
        pl.when(pl.col("acct") == "exclusive").then(pl.col("tok_in") + pl.col("tok_cache_write").fill_null(0))
        .when(pl.col("acct") == "inclusive").then(pl.col("tok_in") - pl.col("tok_cache_read").fill_null(0))
        .otherwise(None).cast(pl.Float64).alias("unc"),
        pl.when(pl.col("acct") == "exclusive").then(pl.col("tok_in") + pl.col("tok_cache_read").fill_null(0)
                                                     + pl.col("tok_cache_write").fill_null(0))
        .when(pl.col("acct") == "inclusive").then(pl.col("tok_in")).otherwise(None).cast(pl.Float64).alias("ctx"))
    acts = acts.select("t", "agent", pl.lit("").alias("ev"), pl.lit(None, pl.Float32).alias("pause_s"),
                       pl.lit(None, pl.Utf8).alias("message_id"), "unc", "ctx", "action")
    ev = (pl.scan_parquet(SH / "events_core.parquet")
          .filter((pl.col("t") >= t0) & (pl.col("t") < t1) & (pl.col("actor_kind").cast(pl.Utf8) == "agent")
                  & pl.col("agent").is_not_null())
          .select("t", "agent", pl.col("action_type").cast(pl.Utf8).alias("ev"), "pause_s", "message_id",
                  pl.lit(None, pl.Float64).alias("unc"), pl.lit(None, pl.Float64).alias("ctx"),
                  pl.lit(None, pl.Utf8).alias("action")).collect())
    allr = pl.concat([acts, ev]).sort("agent", "t")
    allr = allr.with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.Utf8).alias("pt_date"))
    allr = allr.filter(pl.col("pt_date").is_in(days))
    mid = chat.select("message_id", "msg", "mentions_roster")
    allr = allr.join(mid, on="message_id", how="left")
    allr = allr.with_columns(
        ((pl.col("t") - pl.col("t").shift(1).over("agent", "pt_date")).dt.total_microseconds().fill_null(MERGE_US + 1)
         > MERGE_US).cum_sum().over("agent", "pt_date").alias("tid"))
    g = (allr.group_by("agent", "pt_date", "tid", maintain_order=True)
         .agg(pl.col("t").first(),
              (pl.col("ev") == "AGENT_TALK").any().alias("talk"),
              (pl.col("ev") == "PAUSE").any().alias("pause"),
              pl.col("pause_s").max().alias("pause_s"),
              (pl.col("ev") == "CONSOLIDATE").any().alias("cons"),
              pl.col("msg").drop_nulls().first().alias("msg"),
              pl.col("mentions_roster").drop_nulls().first().alias("ment"),
              pl.col("unc").sum().alias("unc"), pl.col("unc").is_not_null().any().alias("has_unc"),
              pl.col("ctx").max().alias("ctx"),
              pl.col("action").drop_nulls().first().alias("act")))
    out = {}
    for (a, d), sub in g.group_by(["agent", "pt_date"], maintain_order=True):
        t = us(sub["t"])
        pause = sub["pause"].to_numpy()
        ps = sub["pause_s"].fill_null(np.nan).to_numpy().astype(np.float32)
        s = np.empty_like(t)
        s[0] = NEG_INF
        if len(t) > 1:
            prev = t[:-1].copy()
            wake = np.where(pause[:-1] & np.isfinite(ps[:-1]), t[:-1] + (np.nan_to_num(ps[:-1]) * US).astype(np.int64), prev)
            s[1:] = np.where(pause[:-1], np.maximum(prev, np.minimum(wake, t[1:] - GUARD_US)), prev)
        unc = np.where(sub["has_unc"].to_numpy(), sub["unc"].to_numpy().astype(float), np.nan)
        out[(int(a), d)] = Turns(t=t, s=s, talk=sub["talk"].to_numpy(), pause=pause, pause_s=ps,
                                 cons=sub["cons"].to_numpy(),
                                 ment=np.array([mask_of(x) for x in sub["ment"].to_list()], dtype=np.uint64),
                                 msg=sub["msg"].fill_null(-1).to_numpy().astype(np.int64),
                                 unc=unc, ctx=sub["ctx"].fill_null(np.nan).to_numpy().astype(float),
                                 act=np.array(sub["act"].fill_null("").to_list(), dtype=object))
    return out


def readout_idx(tr: Turns, t_m: np.ndarray) -> np.ndarray:
    """Index of the read-out turn (first turn with s > t_m); len(tr.t) if none that day."""
    return np.searchsorted(tr.s, t_m, side="right")


def pause_state(tr: Turns, t: np.ndarray):
    """Pre-treatment pause state at times t: (in_pause bool, remaining seconds, expiry us)."""
    j = np.searchsorted(tr.t, t, side="right") - 1          # latest turn at or before t
    ok = j >= 0
    jj = np.clip(j, 0, None)
    isp = ok & tr.pause[jj] & np.isfinite(tr.pause_s[jj])
    exp_ = tr.t[jj] + (np.nan_to_num(tr.pause_s[jj]) * US).astype(np.int64)
    inp = isp & (t < exp_)
    rem = np.where(inp, (exp_ - t) / US, 0.0)
    return inp, rem, np.where(inp, exp_, 0)


# ----------------------------------------------------------------------------- provenance / io

def git_commit() -> str:
    r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "hypotheses/H08-context-is-the-coupling"],
                           capture_output=True, text=True).stdout
    return (r.stdout.strip() or "none") + ("+uncommitted" if dirty.strip() else "")


def write_provenance(entry: str, built_by: str, tables: list[str], params: dict, folder: Path | None = None):
    folder = folder or OUT
    folder.mkdir(parents=True, exist_ok=True)
    p = folder / "_provenance.json"
    prov = json.loads(p.read_text()) if p.exists() else {}
    prov[entry] = {"built_by": built_by, "git_commit": git_commit(),
                   "inputs": [{"source": "ai-village", "revision": REVISION, "tables": tables}],
                   "params": params, "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    p.write_text(json.dumps(prov, indent=1))


def jdump(obj, path: Path):
    def conv(o):
        if isinstance(o, np.floating):
            return None if not np.isfinite(o) else float(o)
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.bool_):
            return bool(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        return str(o)
    txt = json.dumps(obj, default=conv, indent=1, allow_nan=True)
    txt = txt.replace("NaN", "null").replace("-Infinity", "null").replace("Infinity", "null")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(txt)


def ci(x, q=(2.5, 97.5)):
    """(point, lo, hi) from an array whose row 0 is the point estimate and rows 1.. are bootstrap draws."""
    x = np.asarray(x, float)
    b = x[1:][np.isfinite(x[1:])]
    lo, hi = (np.percentile(b, q) if len(b) > 10 else (np.nan, np.nan))
    return float(x[0]), float(lo), float(hi)
