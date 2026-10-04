"""H10 real-data access: statements, goal directions and segments (non-holdout; built by scheme/build.py)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
sys.path.insert(0, str(HERE))
from common import load_holdout, load_whitener  # noqa: E402
from h10lib import aggregate, random_transverse  # noqa: E402

DATA = ROOT / "data/processed/H10-goals-are-legendre-pushes"
SH = ROOT / "data/processed/shared"
UNTOUCHED = {23}  # kept blind for the #22 -> #23 confirmatory pair

# Segments (card, "Segments"): F = all active days; A = first unit of the assigned week, days 2+.
PAIRS = {
    "11-12": {"F": 11, "A": 12, "A_days": ("2025-09-02", "2025-09-04"), "regime": "I", "primary": True},
    "16-17": {"F": 16, "A": 17, "A_days": ("2025-10-14", "2025-10-17"), "regime": "I", "primary": True},
    "37-38": {"F": 37, "A": 38, "A_days": ("2026-04-03", "2026-04-13"), "regime": "III", "primary": True},
    "3-4": {"F": 3, "A": 4, "A_days": None, "regime": "I", "primary": False},
    "5-6": {"F": 5, "A": 6, "A_days": None, "regime": "I", "primary": False},
}
# Units: periods cut at catalogued step changes inside them (only the cuts that matter for H10).
UNIT_END = {4: "2025-05-22", 6: "2025-07-02", 12: "2025-09-04", 31: "2026-02-19", 38: "2026-04-13"}


def guard(goal_nos):
    held = set(load_holdout()["goal_periods_held_out"]) | UNTOUCHED
    bad = set(goal_nos) & held
    if bad:
        raise SystemExit(f"refusing: goal periods {sorted(bad)} are held out or kept untouched in exploration")


_cache = {}


def statements():
    if "st" not in _cache:
        _cache["st"] = pl.read_parquet(DATA / "statements.parquet")
        _cache["Z"] = np.load(DATA / "stmt_w64.npy", mmap_mode="r")
    return _cache["st"], _cache["Z"]


def goal_direction(goal_no: int, regime: str, n: int = 32, variant: str = "combined") -> np.ndarray:
    gz = np.load(DATA / "goal_vecs.npz")
    i = int(np.flatnonzero(gz["goal_no"] == goal_no)[0])
    W = load_whitener(regime, n)
    gv = W(gz["goal_raw"][i][None])[0]
    gv /= np.linalg.norm(gv)
    kr = gz["kick_raw"][i]
    if variant == "goal" or not np.isfinite(kr).all():
        return gv
    kv = W(kr[None])[0]
    kv /= np.linalg.norm(kv)
    if variant == "kickoff":
        return kv
    v = gv + kv
    return v / np.linalg.norm(v)


def load_period(goal_no: int, n: int = 32, days=None, win_min: int = 30):
    """Statements of one goal period (optionally a day range), unit vectors in the first n whitened dims."""
    guard([goal_no])
    st, Z = statements()
    s = st.filter((pl.col("goal_no") == goal_no) & pl.col("win30").is_not_null())
    if goal_no in UNIT_END:
        s = s.filter(pl.col("pt_date") <= UNIT_END[goal_no])
    if days is not None:
        s = s.filter((pl.col("pt_date") >= days[0]) & (pl.col("pt_date") <= days[1]))
    rows = s["row"].to_numpy()
    X = np.asarray(Z[np.sort(rows)][:, :n], dtype=np.float64)[np.argsort(np.argsort(rows))]
    X /= np.linalg.norm(X, axis=1, keepdims=True)
    dlist = sorted(s["pt_date"].unique().to_list())
    dmap = {d: k for k, d in enumerate(dlist)}
    day = np.array([dmap[d] for d in s["pt_date"].to_list()])
    w = s["win30"].to_numpy().astype(int) // (win_min // 30)
    win = day * 1000 + w
    return {"Z": X, "agent": s["agent"].to_numpy().astype(int), "day": day, "win": win, "days": dlist,
            "regime": s["regime"][0] if s.height else None, "kind": s["kind"].to_numpy()}


def segment(P: dict, U: np.ndarray, meta=None):
    return aggregate(P["Z"], P["agent"], P["day"], P["win"], U, meta=meta)


def pair_segments(key: str, n: int = 32, K: int = 50, seed: int = 0, variant: str = "combined", include_day1=False,
                  win_min: int = 30):
    cfg = PAIRS[key]
    guard([cfg["F"], cfg["A"]])
    g = goal_direction(cfg["A"], cfg["regime"], n, variant)
    U = random_transverse(g, K, np.random.default_rng(seed))
    PF = load_period(cfg["F"], n, win_min=win_min)
    if cfg["A_days"] is None:
        PA_all = load_period(cfg["A"], n, win_min=win_min)
        d = PA_all["days"]
        days = (d[0], d[-1]) if include_day1 else (d[1], d[-1])
    else:
        days = cfg["A_days"]
        if include_day1:
            days = (load_period(cfg["A"], n)["days"][0], days[1])
    PA = load_period(cfg["A"], n, days=days, win_min=win_min)
    return segment(PF, U, {"goal": cfg["F"], "days": PF["days"]}), segment(PA, U, {"goal": cfg["A"], "days": PA["days"]}), g


def save_json(obj, path: Path):
    def conv(o):
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        raise TypeError(type(o))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, default=conv))
