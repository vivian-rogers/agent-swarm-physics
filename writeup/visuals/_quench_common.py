"""Shared content-projection pipeline for the quench visuals (H96, H97; reused by H82/H103 helpers).

A kickoff transition P-1 -> P is read from H97's processed design (statement rows + kickoff vector), the shared
DQ5 statement vectors (bge-small, regime-whitened, d = 32) and H97's whitened kickoff direction k_hat. Every agent
state is projected onto a 2-D plane:

    x = <z, k_hat>             the goal axis: alignment with the new kickoff (P's field)
    y = <z, e_old>             the old-state axis: P-1's last-day swarm centroid, orthogonalized to k_hat

No text is read. Every statement row passes `common.holdout_mask` (asserted). The Claude Code agent (19) is dropped.

Usage:
    import sys; sys.path.insert(0, "writeup/visuals"); import _quench_common as qc
    T = qc.load_transition("T39")           # dict: stmt (polars), X (n x 32), k, e_old, days, names, ...
    P = qc.seg_means(T, mask)                # {agent: mean projection (x, y)}
    traj = qc.kernel_trajectories(T, ...)   # frame times, (F, A, 2) positions for the animation
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import holdout_mask  # noqa: E402

PROC = ROOT / "data/processed"
SH = PROC / "shared"
H97 = PROC / "H97-quench-restoring-force"
CC_AGENT = 19
MODEL = "bge_small"

_Z = {}


def statement_matrix(model: str = MODEL) -> np.ndarray:
    """Shared DQ5 statement vectors (regime-whitened, unit, d = 32), memory-mapped."""
    if model not in _Z:
        _Z[model] = np.load(SH / "embeddings" / f"statements_white32_{model}.npy", mmap_mode="r")
    return _Z[model]


def names() -> dict:
    r = pl.read_parquet(SH / "roster.parquet", columns=["agent", "name"])
    return dict(zip(r["agent"].to_list(), r["name"].to_list()))


def unit(v):
    return v / np.linalg.norm(v)


def load_transition(design: str, model: str = MODEL) -> dict:
    """Statements of an H97 kickoff design (P-1's days, P's days 1-5), their vectors and the projection axes."""
    stmt = pl.read_parquet(H97 / "stmt.parquet").filter((pl.col("design") == design) & (pl.col("agent") != CC_AGENT))
    ho = holdout_mask(stmt["pt_date"].to_list(), stmt["goal_no"].cast(pl.Int64).to_list())
    assert not any(ho), "holdout rows in the design"
    tr = pl.read_parquet(H97 / "transitions.parquet").filter(pl.col("design") == design).row(0, named=True)
    rows = stmt["row"].to_numpy()
    o = np.argsort(rows)
    Xs = np.asarray(statement_matrix(model)[rows[o]], dtype=np.float64)
    X = np.empty_like(Xs); X[o] = Xs
    k = unit(np.asarray(np.load(H97 / "vectors.npz")[f"{design}|k|{model}"], dtype=np.float64))
    prev = (stmt["seg"] == "prev").to_numpy()
    c = X[prev].mean(0)
    e_old = unit(c - (c @ k) * k)
    days = (stmt.select("goal_no", "pt_date", "day_idx", "seg").unique()
            .sort("pt_date").with_row_index("ord").to_dicts())
    # day offsets relative to P's first day (0 = kickoff day, -1 = P-1's last day, ...)
    i1 = [d["ord"] for d in days if d["seg"] == "day1"][0]
    for d in days:
        d["rel"] = int(d["ord"]) - int(i1)
    stmt = stmt.with_columns(pl.Series("x", X @ k), pl.Series("y", X @ e_old))
    return dict(design=design, tr=tr, stmt=stmt, X=X, k=k, e_old=e_old, days=days, names=names(),
                t0=tr["t0"], p=tr["p"], prev=tr["prev"])


def day_mask(T: dict, rel: int) -> pl.Expr:
    d = [x for x in T["days"] if x["rel"] == rel][0]
    return (pl.col("pt_date") == d["pt_date"]) & (pl.col("goal_no") == d["goal_no"])


def seg_means(T: dict, mask: pl.Expr, min_stmt: int = 4) -> dict:
    """{agent: (x, y, n)} plain means of the projections over the rows selected by mask."""
    g = (T["stmt"].filter(mask).group_by("agent")
         .agg(pl.col("x").mean(), pl.col("y").mean(), pl.len().alias("n")).filter(pl.col("n") >= min_stmt))
    return {int(a): (float(x), float(y), int(n)) for a, x, y, n in g.iter_rows()}


def day_means(T: dict) -> pl.DataFrame:
    """Swarm-mean projections per day (rows: rel, x, y, n_agents) from agent means (agents weighted equally)."""
    out = []
    for d in T["days"]:
        m = seg_means(T, day_mask(T, d["rel"]))
        if len(m) >= 3:
            v = np.array([[a[0], a[1]] for a in m.values()])
            out.append(dict(rel=d["rel"], x=float(v[:, 0].mean()), y=float(v[:, 1].mean()), n_agents=len(m)))
    return pl.DataFrame(out)


def kernel_trajectories(T: dict, rel_days: list, step_min: float = 4.0, tau_min: float = 40.0,
                        window_min: float = 120.0, min_weight: float = 2.0):
    """Per-agent positions on a frame grid over the chosen days (active time only; nights are skipped).

    Position of agent i at time t: exponentially weighted mean (time constant tau_min) of its statement projections
    in (t - window_min, t] on the same day. If the effective weight is below min_weight, the agent keeps its last
    position (carried over the night as well), and is marked stale. Returns dict(frames=[(rel, datetime)], pos (F,A,2),
    fresh (F,A) bool, agents, day_starts (frame indices))."""
    st = T["stmt"]
    agents = sorted(st["agent"].unique().to_list())
    ai = {a: j for j, a in enumerate(agents)}
    frames, pos, fresh, day_starts = [], [], [], []
    last = np.full((len(agents), 2), np.nan)
    for rel in rel_days:
        d = st.filter(day_mask(T, rel))
        if rel == 0:   # kickoff day: start at the first kickoff message
            d = d.filter(pl.col("t") >= T["t0"])
        t_s = d["t"].min(); t_e = d["t"].max()
        ts = d["t"].dt.epoch("s").to_numpy() / 60.0
        ag = np.array([ai[a] for a in d["agent"].to_list()])
        xy = d.select("x", "y").to_numpy()
        grid = np.arange(t_s.timestamp() / 60.0 + step_min, t_e.timestamp() / 60.0 + step_min, step_min)
        day_starts.append(len(frames))
        for g in grid:
            sel = (ts <= g) & (ts > g - window_min)
            w = np.exp(-(g - ts[sel]) / tau_min)
            P = np.full((len(agents), 2), np.nan); F = np.zeros(len(agents), bool)
            if sel.any():
                W = np.bincount(ag[sel], weights=w, minlength=len(agents))
                Sx = np.bincount(ag[sel], weights=w * xy[sel, 0], minlength=len(agents))
                Sy = np.bincount(ag[sel], weights=w * xy[sel, 1], minlength=len(agents))
                ok = W >= min_weight
                P[ok, 0] = Sx[ok] / W[ok]; P[ok, 1] = Sy[ok] / W[ok]; F = ok
            last = np.where(F[:, None], P, last)
            frames.append((rel, g))
            pos.append(last.copy()); fresh.append(F)
    return dict(frames=frames, pos=np.array(pos), fresh=np.array(fresh), agents=agents, day_starts=day_starts)
