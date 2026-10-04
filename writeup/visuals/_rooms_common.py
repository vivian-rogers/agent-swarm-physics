"""Shared room-projection pipeline for the "rooms as magnetic domains" visuals (H05, H47, H100, H102, H108).

Instrument (the project's shared rulers, nothing new):
- statements: `data/processed/shared/embeddings/statements.parquet` (agent chat + intentions), with
  `statements_style_resid32_bge_small.npy` (DQ5: 32-d regime-whitened, style-residualized; bge, as STYLE.md asks);
- room of each statement: `infra/shared/rooms_asof.statement_rooms` (chat = message room; intentions = as-of
  `rooms_timeline` with open stays closed at +inf);
- non-holdout only: the shared `holdout` flag AND `infra/shared/common.holdout_mask` (goal periods and NE windows);
  the Claude Code agent is excluded (as in H100/H102/H108). Never reads `data/processed/holdout_labels/`.
- day centring: minus the mean over agents of that day's agent-day means (removes the day / goal field g_d).

Room-difference nulls use the JOINT relabel (infra Known issues, H100/H108): one random partition of the agents with
room sizes kept, applied to every day, so leftover agent constants stay inside the null.

No text is read anywhere: only codes, times and vectors.
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

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SH = ROOT / "data/processed/shared"
PROC = ROOT / "data/processed"
sys.path.insert(0, str(ROOT / "infra/shared"))
sys.path.insert(0, str(HERE))

import rooms_asof  # noqa: E402
from common import holdout_mask  # noqa: E402

GENERAL, BEST, REST, UNIVERSE, FOCUS = 0, 2, 3, 4, 15
ROOM_NAME = {0: "#general", 2: "#best", 3: "#rest", 4: "#universe-coordination", 15: "#focus"}


@lru_cache(maxsize=1)
def roster() -> dict[int, str]:
    r = pl.read_parquet(SH / "roster.parquet")
    return dict(zip(r["agent"].to_list(), r["name"].to_list()))


@lru_cache(maxsize=1)
def claude_code_agents() -> tuple[int, ...]:
    r = pl.read_parquet(SH / "roster.parquet")
    return tuple(r.filter(pl.col("claude_code"))["agent"].to_list())


def load_statements(goals=None, date_range=None, model: str = "bge_small", variant: str = "style_resid32"):
    """Non-holdout agent statements (chat + intentions) with `srow`, `room_at` and their 32-d vectors (float64).

    goals: iterable of goal numbers to keep (None = all); date_range: (first, last) PT dates inclusive.
    Returns (st, X) with X rows aligned to st rows."""
    st = pl.read_parquet(SH / "embeddings/statements.parquet").with_row_index("srow")
    if goals is not None:
        st = st.filter(pl.col("goal_no").is_in(list(goals)))
    if date_range is not None:
        st = st.filter((pl.col("pt_date") >= date_range[0]) & (pl.col("pt_date") <= date_range[1]))
    st = st.filter(~pl.col("holdout") & ~pl.col("agent").is_in(list(claude_code_agents())))
    held = np.array(holdout_mask(st["pt_date"].to_list(), st["goal_no"].fill_null(-1).to_list()), dtype=bool)
    st = st.filter(pl.Series(~held))
    assert not np.any(holdout_mask(st["pt_date"].to_list(), st["goal_no"].fill_null(-1).to_list())), "holdout row"
    st = rooms_asof.statement_rooms(st)
    X = np.load(SH / f"embeddings/statements_{variant}_{model}.npy", mmap_mode="r")
    X = np.asarray(X[st["srow"].to_numpy()], dtype=np.float64)
    return st, X


def day_center(st: pl.DataFrame, X: np.ndarray, key_cols=("pt_date",)) -> np.ndarray:
    """Statement vectors minus the mean over agents of that day's agent-day means (H102 rule)."""
    Xc = X.copy()
    key = st.select(pl.concat_str([pl.col(c).cast(pl.String) for c in key_cols], separator="|")).to_series().to_numpy()
    ag = st["agent"].to_numpy()
    for k in np.unique(key):
        m = key == k
        means = [X[m & (ag == a)].mean(0) for a in np.unique(ag[m])]
        Xc[m] -= np.mean(means, 0)
    return Xc


def agent_day_means(st: pl.DataFrame, Xc: np.ndarray, by_room: bool = False, min_n: int = 1):
    """Mean statement vector per (agent, pt_date[, room_at]). Returns (table, V) with V aligned to table rows.
    The table also carries the agent's room of the day (majority room of its statements) and n statements."""
    keys = ["agent", "pt_date"] + (["room_at"] if by_room else [])
    s = st.with_row_index("__i")
    if by_room:
        s = s.drop_nulls("room_at")
    g = (s.group_by(keys, maintain_order=True)
         .agg(pl.col("__i"), pl.len().alias("n"), pl.col("goal_no").first(),
              pl.col("room_at").drop_nulls().mode().sort().first().alias("room_day"))
         .filter(pl.col("n") >= min_n).sort(keys))
    V = np.stack([Xc[np.asarray(ix)].mean(0) for ix in g["__i"].to_list()]) if g.height else np.zeros((0, Xc.shape[1]))
    return g.drop("__i"), V


def unit(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v)
    return v / n if n > 0 else v


def plane(u1: np.ndarray, u2: np.ndarray) -> np.ndarray:
    """Orthonormal 2 x d basis: e1 = u1/|u1|, e2 = the part of u2 orthogonal to e1 (Gram-Schmidt)."""
    e1 = unit(u1)
    e2 = unit(u2 - (u2 @ e1) * e1)
    return np.stack([e1, e2])


def room_diff(V: np.ndarray, labels: np.ndarray, a: int = BEST, b: int = REST) -> np.ndarray:
    return V[labels == a].mean(0) - V[labels == b].mean(0)


def daily_room_split(tab: pl.DataFrame, V: np.ndarray, partition: dict[int, int], days: list[str],
                     n_null: int = 2000, seed: int = 0, a: int = BEST, b: int = REST):
    """Daily room difference Δ(d) of agent-day means under a FIXED partition (agent -> room), with its squared norm
    and a joint-relabel null (one permutation of the partition per draw, applied to every day).

    Returns dict with days, delta (n_days x d), E_obs = |Δ(d)|², E_null (n_null x n_days)."""
    agents = np.array(sorted(partition))
    labs = np.array([partition[x] for x in agents])
    rng = np.random.default_rng(seed)
    perms = [labs] + [rng.permutation(labs) for _ in range(n_null)]
    ag_col = tab["agent"].to_numpy(); d_col = tab["pt_date"].to_numpy()
    delta, E = [], np.full((n_null + 1, len(days)), np.nan)
    for k, d in enumerate(days):
        m = (d_col == d) & np.isin(ag_col, agents)
        idx = np.nonzero(m)[0]
        pos = {x: i for i, x in enumerate(agents)}
        rows = np.array([pos[x] for x in ag_col[idx]])
        Vd = V[idx]
        for p, lab in enumerate(perms):
            ll = lab[rows]
            if (ll == a).sum() >= 2 and (ll == b).sum() >= 2:
                dd = Vd[ll == a].mean(0) - Vd[ll == b].mean(0)
                E[p, k] = dd @ dd
                if p == 0:
                    delta.append(dd)
            elif p == 0:
                delta.append(np.full(V.shape[1], np.nan))
    return {"days": days, "delta": np.array(delta), "E_obs": E[0], "E_null": E[1:]}


def load_json(rel: str):
    return json.loads((PROC / rel).read_text())


def ema_positions(times_frames: np.ndarray, t_obs: np.ndarray, x_obs: np.ndarray, tau: float,
                  reset_at: list[float] | None = None) -> np.ndarray:
    """Causal exponential average of observations (t_obs sorted, x_obs rows) evaluated at frame times.
    reset_at: times at which the memory is cleared (goal boundaries). Before the first observation -> NaN."""
    out = np.full((len(times_frames), x_obs.shape[1]), np.nan)
    if len(t_obs) == 0:
        return out
    resets = sorted(reset_at or [])
    j, acc, w, last_t = 0, np.zeros(x_obs.shape[1]), 0.0, None
    for f, tf in enumerate(times_frames):
        while j < len(t_obs) and t_obs[j] <= tf:
            if last_t is not None:
                if any(last_t < r <= t_obs[j] for r in resets):
                    acc, w = np.zeros_like(acc), 0.0
                else:
                    dec = np.exp(-(t_obs[j] - last_t) / tau); acc *= dec; w *= dec
            acc = acc + x_obs[j]; w += 1.0; last_t = t_obs[j]; j += 1
        if w > 0:
            out[f] = acc / w
    return out
