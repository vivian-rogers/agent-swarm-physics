"""H01 shared helpers: paths, holdout guard, analysis units (goal periods split at step changes), k-means.

Imported by scheme/build.py, analysis/*.py and analysis/confirm_d32.py. Thread use is capped at 4 (other agents
share the machine): set the env vars below before numpy is imported.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
HYP = HERE.parent
ROOT = HYP.parents[1]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit, holdout_mask, load_holdout  # noqa: E402,F401

SH = ROOT / "data/processed/shared"
EMB = SH / "embeddings"
OUT = ROOT / "data/processed/H01-emergent-superagents-exist"
FIG = HYP / "figures"
SEED = 20261003

# Step changes inside goal periods (natural-experiments.md + H05 room events). A unit = goal period, split here.
#   #36: regime boundary 03-24 (NE14 F).  #38: NE17 outreach approval 04-14, NE18 history search 04-20.
#   #51: NE32 GPT-5.6 triplet 07-09; #focus room 08-05 -> 08-24 (H05); NE33 batch join 09-03.
GOAL_SPLITS = {36: ["2026-03-24"], 38: ["2026-04-14", "2026-04-20"],
               51: ["2026-07-09", "2026-08-05", "2026-08-25", "2026-09-03"]}
FOCUS_UNIT = "51c"


def unit_of(goal_no: int, pt_date: str) -> str:
    cuts = GOAL_SPLITS.get(int(goal_no))
    if not cuts:
        return str(int(goal_no))
    k = sum(pt_date >= c for c in cuts)
    return f"{int(goal_no)}{'abcdefgh'[k]}"


def nonholdout_days() -> list[str]:
    """Active PT days that are not in the locked holdout (calendar flag AND holdout_mask, belt and braces)."""
    cal = pl.read_parquet(SH / "calendar.parquet")
    hm = holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    cal = cal.with_columns(pl.Series("hm", hm)).filter(~pl.col("holdout") & ~pl.col("hm") & (pl.col("goal_no") > 0))
    return sorted(cal["pt_date"].to_list())


def holdout_days() -> set[str]:
    cal = pl.read_parquet(SH / "calendar.parquet")
    hm = holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    cal = cal.with_columns(pl.Series("hm", hm))
    return set(cal.filter(pl.col("holdout") | pl.col("hm"))["pt_date"].to_list())


def guard_holdout(days, allow=False):
    """Raise if any day is in the locked holdout (calendar flag, held-out goal periods, or NE windows)."""
    if allow:
        return
    h = load_holdout()
    held = holdout_days()
    cal = pl.read_parquet(SH / "calendar.parquet")
    goal = dict(zip(cal["pt_date"].to_list(), cal["goal_no"].to_list()))
    for d in days:
        assert d not in held, f"holdout day {d} in exploration"
        assert not any(w["start"] <= d < w["end"] for w in h["ne_windows"]), f"NE-window day {d} in exploration"
        assert goal.get(d) not in set(h["goal_periods_held_out"]), f"held-out goal period day {d}"


def write_provenance(name: str, built_by: str, tables: list[str], params: dict):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "_provenance.json"
    prov = json.loads(path.read_text()) if path.exists() else {}
    prov[name] = {"built_by": built_by, "git_commit": git_commit(),
                  "inputs": [{"source": "ai-village", "revision": REVISION, "tables": tables}],
                  "params": params, "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    path.write_text(json.dumps(prov, indent=1))


# ============================================================================ k-means (numpy; no sklearn in the env)
def kmeans(X: np.ndarray, k: int, seed: int = SEED, n_init: int = 3, max_iter: int = 100, init_sub: int = 20000):
    """Lloyd k-means with k-means++ init. X float32 (n, d). Returns (centroids (k, d), labels (n,), inertia)."""
    rng = np.random.default_rng(seed)
    X = np.ascontiguousarray(X, dtype=np.float32)
    x2 = (X * X).sum(1)
    best = None
    for _ in range(n_init):
        sub = X[rng.choice(len(X), size=min(init_sub, len(X)), replace=False)]
        s2 = (sub * sub).sum(1)
        C = [sub[rng.integers(len(sub))]]
        d2 = s2 - 2 * sub @ C[0] + C[0] @ C[0]
        for _j in range(1, k):
            p = np.clip(d2, 0, None); p = p / p.sum()
            c = sub[rng.choice(len(sub), p=p)]
            C.append(c)
            d2 = np.minimum(d2, s2 - 2 * sub @ c + c @ c)
        C = np.array(C, dtype=np.float32)
        lab_prev = None
        for _it in range(max_iter):
            D = x2[:, None] - 2 * X @ C.T + (C * C).sum(1)[None, :]
            lab = D.argmin(1)
            if lab_prev is not None and (lab == lab_prev).mean() > 0.9995:
                break
            lab_prev = lab
            for j in range(k):
                m = lab == j
                C[j] = X[m].mean(0) if m.any() else X[rng.integers(len(X))]
        D = x2[:, None] - 2 * X @ C.T + (C * C).sum(1)[None, :]
        lab = D.argmin(1)
        inertia = float(D[np.arange(len(X)), lab].sum())
        if best is None or inertia < best[2]:
            best = (C.copy(), lab.astype(np.int16), inertia)
    return best


def assign(X: np.ndarray, C: np.ndarray) -> np.ndarray:
    X = X.astype(np.float32)
    D = (X * X).sum(1)[:, None] - 2 * X @ C.T + (C * C).sum(1)[None, :]
    return D.argmin(1).astype(np.int16)


def unit(X, axis=-1, eps=1e-9):
    X = np.asarray(X, dtype=np.float64)
    return X / np.maximum(np.linalg.norm(X, axis=axis, keepdims=True), eps)


def whiten_apply(raw: np.ndarray, basis: dict, d: int) -> np.ndarray:
    """Center with the regime mean, project on the top-d PCs, divide by sqrt(eigenvalue)."""
    Z = (raw.astype(np.float32) - basis["mean"]) @ basis["components"][:d].T
    return Z / np.sqrt(basis["eigvals"][:d])


def load_basis(regime: str) -> dict:
    z = np.load(OUT / f"basis_{regime}.npz")
    return {k: z[k] for k in z.files}
