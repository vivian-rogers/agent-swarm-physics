"""H54 shared helpers: paths, eligibility, whitening, vectors, estimators. No text is ever stored.

Conventions
  - Every comparison for a target period p is made in p's regime basis: z = unit(W_r(raw)), d = 32.
  - Eligible kickoffs: non-holdout goal periods with a shared kickoff (goal_fields), minus #23 (kept blind for H10).
  - Holdout rows are masked with common.holdout_mask unless allow_holdout=True (confirm.py only).
  - Round 2 (2026-10-04): embedding-model switch H54_MODEL in {bge_small (default, round 1 unchanged), gte_modernbert}.
    With gte_modernbert, raw vectors, goal vectors and whiteners come from DQ5's second model, and OUT moves to
    data/processed/H54-kickoff-quench-target/r2_gte/ so round-1 outputs are never overwritten.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import json  # noqa: E402
import sys  # noqa: E402
from functools import lru_cache  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
HYP = ROOT / "hypotheses/H54-kickoff-quench-target"
SHARED = ROOT / "data/processed/shared"
ED = SHARED / "embeddings"
MODEL = os.environ.get("H54_MODEL", "bge_small")
assert MODEL in ("bge_small", "gte_modernbert"), MODEL
OUT_BASE = ROOT / "data/processed/H54-kickoff-quench-target"
OUT = OUT_BASE if MODEL == "bge_small" else OUT_BASE / "r2_gte"
H31 = ROOT / "data/processed/H31-consensus-time-spectral-gap"
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import holdout_mask, load_whitener, git_commit, REVISION  # noqa: E402
import embed_models as _EM  # noqa: E402

EXCLUDE = {23}          # kept blind for H10's confirmatory #22 -> #23 pair
CLAUDE_CODE = 19        # separate scaffolding; never an agent here
N_MIN = 3               # statements per agent segment
N_RARE = 5              # rarefaction size for spread
D = 32


def unit(x, axis=-1):
    x = np.asarray(x, dtype=np.float64)
    n = np.linalg.norm(x, axis=axis, keepdims=True)
    return x / np.where(n > 0, n, 1.0)


@lru_cache(maxsize=None)
def W(regime: str):
    if MODEL == "bge_small":
        return load_whitener(regime, D)
    return _EM.load_whitener(regime, D, MODEL)


def whiten_unit(raw, regime):
    return unit(W(regime)(np.asarray(raw, dtype=np.float32)))


@lru_cache(maxsize=1)
def calendar(allow_holdout: bool = False) -> pl.DataFrame:
    cal = pl.read_parquet(SHARED / "calendar.parquet").with_columns(pl.col("regime").cast(pl.String))
    cal = cal.filter(pl.col("goal_no") > 0)
    ho = holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    cal = cal.with_columns(pl.Series("ho", ho))
    if not allow_holdout:
        cal = cal.filter(~pl.col("ho"))
    return cal.sort("pt_date")


@lru_cache(maxsize=1)
def goals() -> pl.DataFrame:
    return pl.read_parquet(ED / "goals.parquet").with_columns(pl.col("kind").cast(pl.String))


@lru_cache(maxsize=1)
def goal_raw() -> np.ndarray:
    if MODEL == "bge_small":
        return np.load(ED / "goal_vectors.npy").astype(np.float32)
    return np.asarray(_EM.goal_vectors(MODEL), dtype=np.float32)


def eligible(allow_holdout: bool = False, include_excluded: bool = False) -> list[int]:
    g = goals().filter(pl.col("kind") == "kickoff")
    if not allow_holdout:
        g = g.filter(~pl.col("holdout"))
    out = sorted(set(g["goal_no"].to_list()))
    if not include_excluded:
        out = [x for x in out if x not in EXCLUDE]
    return out


def period_regime(p: int) -> str:
    r = goals().filter((pl.col("goal_no") == p) & (pl.col("kind") == "goal"))["regime"]
    return str(r[0])


def gvec(p: int, kind: str = "kickoff", room: int | None = None, agent: int | None = None, regime: str | None = None):
    """Unit whitened vector of a goal row in `regime`'s basis (default: the row's own period regime)."""
    g = goals().filter((pl.col("goal_no") == p) & (pl.col("kind") == kind))
    if room is not None:
        g = g.filter(pl.col("room") == room)
    if agent is not None:
        g = g.filter(pl.col("agent") == agent)
    if g.height == 0:
        return None
    gid = int(g["gid"][0])
    return whiten_unit(goal_raw()[gid][None], regime or period_regime(p))[0]


def kick_matrix(periods: list[int], regime: str, kind: str = "kickoff") -> np.ndarray:
    return np.vstack([gvec(q, kind, regime=regime) for q in periods])


# ----------------------------------------------------------------------------------------- statements
@lru_cache(maxsize=1)
def statements() -> pl.DataFrame:
    st = pl.read_parquet(ED / "statements.parquet").with_row_index("srow")
    return st


@lru_cache(maxsize=1)
def raw_arrays():
    return (np.load(_EM.emb_path("chat", MODEL), mmap_mode="r"), np.load(_EM.emb_path("intentions", MODEL), mmap_mode="r"))


def raw_for(st: pl.DataFrame) -> np.ndarray:
    chat, intent = raw_arrays()
    out = np.zeros((st.height, chat.shape[1]), dtype=np.float32)
    kind = st["kind"].to_numpy()
    src = st["src_row"].to_numpy()
    m = kind == "chat"
    if m.any():
        idx = src[m]
        o = np.argsort(idx)
        tmp = np.asarray(chat[idx[o]], dtype=np.float32)
        out[np.flatnonzero(m)[o]] = tmp
    m2 = ~m
    if m2.any():
        idx = src[m2]
        o = np.argsort(idx)
        out[np.flatnonzero(m2)[o]] = np.asarray(intent[idx[o]], dtype=np.float32)
    return out


@lru_cache(maxsize=1)
def chat_rows() -> pl.DataFrame:
    """message_id -> row of chat_bge_small."""
    return pl.read_parquet(ED / "chat_index.parquet").with_row_index("crow")


def chat_vec(message_ids: list[str], regime: str) -> np.ndarray:
    ci = chat_rows().filter(pl.col("message_id").is_in(message_ids))
    order = {m: i for i, m in enumerate(message_ids)}
    chat, _ = raw_arrays()
    out = np.full((len(message_ids), D), np.nan)
    for mid, r in zip(ci["message_id"].to_list(), ci["crow"].to_list()):
        out[order[mid]] = whiten_unit(np.asarray(chat[r], dtype=np.float32)[None], regime)[0]
    return out


# ----------------------------------------------------------------------------------------- H54 tables
def load_stmt(base: Path | None = None):
    """H54 statement table (build.py) and its whitened vectors in the target period's basis."""
    base = base or OUT
    st = pl.read_parquet(base / "stmt.parquet")
    Z = np.load(base / "stmt_z.npy").astype(np.float64)
    ZS = np.load(base / "stmt_zs.npy").astype(np.float64)
    return st, Z, ZS


def agent_vectors(st: pl.DataFrame, Z: np.ndarray, keys=("goal_no", "day", "agent"), n_min: int = N_MIN):
    """Unit mean vector per group; returns (frame with keys + n, V)."""
    g = (st.with_row_index("i").group_by(list(keys), maintain_order=True)
         .agg(pl.col("i"), pl.len().alias("n")).filter(pl.col("n") >= n_min))
    V = np.vstack([unit(Z[np.asarray(ix)].mean(0)) for ix in g["i"].to_list()]) if g.height else np.zeros((0, D))
    return g.drop("i"), V


def rarefied_q(groups: list[np.ndarray], n: int = N_RARE, B: int = 50, rng=None) -> float:
    """Mean pairwise cosine of agent vectors, each built from n random statements (B draws). groups: per-agent Z."""
    rng = rng or np.random.default_rng(0)
    gs = [g for g in groups if len(g) >= n]
    if len(gs) < 3:
        return np.nan
    vals = []
    for _ in range(B):
        V = np.vstack([unit(g[rng.choice(len(g), n, replace=False)].mean(0)) for g in gs])
        G = V @ V.T
        k = len(gs)
        vals.append((G.sum() - np.trace(G)) / (k * (k - 1)))
    return float(np.mean(vals))


def pairwise_q(V: np.ndarray) -> float:
    k = len(V)
    if k < 2:
        return np.nan
    G = V @ V.T
    return float((G.sum() - np.trace(G)) / (k * (k - 1)))


def own_percentile(scores: np.ndarray, own: int) -> float:
    """Share of decoys (all other entries, NaN skipped) strictly below the own score; ties count half."""
    s = np.asarray(scores, dtype=float)
    o = s[own]
    d = np.delete(s, own)
    d = d[np.isfinite(d)]
    if not len(d) or not np.isfinite(o):
        return np.nan
    return float(((d < o).sum() + 0.5 * (d == o).sum()) / len(d))


def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)

    def conv(o):
        if isinstance(o, (np.floating,)):
            return None if not np.isfinite(o) else float(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, np.ndarray):
            return [conv(x) for x in o.tolist()]
        if isinstance(o, float) and not np.isfinite(o):
            return None
        return str(o)
    path.write_text(json.dumps(obj, indent=1, default=conv, allow_nan=False) if _finite(obj) else json.dumps(_clean(obj), indent=1, default=conv))


def _finite(o):
    try:
        json.dumps(o, allow_nan=False, default=lambda x: 0)
        return True
    except ValueError:
        return False


def _clean(o):
    if isinstance(o, dict):
        return {k: _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, (float, np.floating)):
        return None if not np.isfinite(o) else float(o)
    if isinstance(o, np.integer):
        return int(o)
    return o


def provenance(name: str, inputs: list[str], params: dict | None = None):
    p = OUT / "_provenance.json"
    prov = json.loads(p.read_text()) if p.exists() else {}
    import datetime as dt
    prov[name] = {"built_by": f"hypotheses/H54-kickoff-quench-target/{name}", "git_commit": git_commit(),
                  "inputs": [{"source": "ai-village", "revision": REVISION, "tables": inputs}],
                  "params": params or {}, "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    OUT.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(prov, indent=1))
