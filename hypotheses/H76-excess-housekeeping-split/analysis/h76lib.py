"""H76 library: Kolchinsky et al. (2026) excess / housekeeping split of ensemble behavior fluxes.

Estimator (per block of agent-steps):
  j_xy  = soft transition flux per agent-step, summed over agents and steps, + pseudocount alpha per directed edge
  sigma = sum_{x!=y} j_xy ln(j_xy / j_yx)                                    (total EP, nats per agent-step)
  sigma_ex = max_phi [ -phi.pdot - sum_{x!=y} j_xy (exp(phi_y - phi_x) - 1) ]  (Eq. 38; 0 iff pdot = 0)
  sigma_hk = sigma - sigma_ex                                                 (cyclic part; needs >= 3 states)
Reversible-surrogate floor: each agent's block flux is transposed with probability 1/2 (block flip).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
SH = ROOT / "data/processed/shared"
OUTD = ROOT / "data/processed/H76-excess-housekeeping-split"
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import holdout_mask  # noqa: E402

V3 = ["execute_task", "research_browse", "monitor_wait", "verify_report", "self_maintenance", "debug_recover",
      "communicate_external", "idle", "plan_coordinate", "social", "meta"]
FINE = ["absent"] + V3
COARSE_GROUPS = {"absent": [], "work": ["execute_task", "debug_recover", "verify_report"],
                 "explore": ["research_browse"],
                 "coord": ["plan_coordinate", "communicate_external", "social", "meta"],
                 "wait": ["monitor_wait", "idle", "self_maintenance"]}
COARSE = list(COARSE_GROUPS)
STEP_MIN = 5
ALPHA = 0.1


# ============================================================================ estimator
def pdot_of(j: np.ndarray) -> np.ndarray:
    """Net inflow per state: sum_y (j_yx - j_xy)."""
    return j.sum(0) - j.sum(1)


def sigma_total(j: np.ndarray) -> float:
    n = j.shape[0]
    off = ~np.eye(n, dtype=bool)
    a, b = j[off], j.T[off]
    return float(np.sum(a * np.log(a / b)))


def sigma_excess(j: np.ndarray, tol: float = 1e-12, maxit: int = 100) -> tuple[float, np.ndarray]:
    """Eq. 38 of Kolchinsky et al. 2026 by damped Newton on phi (phi_0 = 0). j must be > 0 off the diagonal."""
    n = j.shape[0]
    jj = j.copy()
    np.fill_diagonal(jj, 0.0)
    pd = pdot_of(jj)
    phi = np.zeros(n)

    def F(ph):
        E = jj * np.exp(ph[None, :] - ph[:, None])
        return -ph @ pd - (E.sum() - jj.sum()), E

    f, E = F(phi)
    for _ in range(maxit):
        g = -pd - (E.sum(0) - E.sum(1))
        Ssym = E + E.T
        L = np.diag(Ssym.sum(1)) - Ssym          # Hessian of F is -L
        gr, Lr = g[1:], L[1:, 1:]
        try:
            step = np.linalg.solve(Lr, gr)
        except np.linalg.LinAlgError:
            step = np.linalg.lstsq(Lr, gr, rcond=None)[0]
        dec = float(gr @ step)
        if dec < tol:
            break
        t = 1.0
        while True:
            ph2 = phi.copy()
            ph2[1:] += t * step
            f2, E2 = F(ph2)
            if f2 >= f + 0.25 * t * dec or t < 1e-8:
                break
            t *= 0.5
        phi, f, E = ph2, f2, E2
    return float(max(f, 0.0)), phi


def split(J: np.ndarray, M: float, alpha: float = ALPHA) -> tuple[float, float, float]:
    """J: summed flux counts (n x n) over M agent-steps. Returns (sigma, sigma_ex, sigma_hk) per agent-step."""
    if M <= 0:
        return (np.nan, np.nan, np.nan)
    n = J.shape[0]
    j = J / M + (alpha / M) * (1 - np.eye(n))
    s = sigma_total(j)
    se, _ = sigma_excess(j)
    se = min(se, s)
    return s, se, s - se


def surrogate_floor(Jper: np.ndarray, M: float, rng: np.random.Generator, R: int = 20,
                    alpha: float = ALPHA) -> np.ndarray:
    """Block-flip reversible surrogate: each agent's whole block flux matrix is transposed with probability 1/2
    (its block trajectory is time-reversed). Keeps each agent's telescoping net change, so the surrogate's
    occupancy noise matches the raw estimator's. Jper: (n_agents, n, n); M: agent-steps. Returns (R, 3)."""
    out = np.empty((R, 3))
    JT = np.transpose(Jper, (0, 2, 1))
    for r in range(R):
        s = rng.random(Jper.shape[0]) < 0.5
        J = Jper[s].sum(0) + JT[~s].sum(0)
        out[r] = split(J, M, alpha)
    return out


# ============================================================================ data
def kickoff_time(goal: int) -> dt.datetime:
    g = pl.read_parquet(SH / "embeddings/goals.parquet").filter((pl.col("goal_no") == goal) & (pl.col("kind") == "kickoff"))
    return g["win_start"][0]


def load_v3(goal: int, space: str = "coarse", days: list[str] | None = None, allow_holdout: bool = False) -> dict:
    """Per non-holdout day: {'agents': [...], 'X': (n_agents, n_windows, n_states) soft states, 'span': bool array,
    't0': window start times}. Absent = no labelled record in the window."""
    cols = ["pt_date", "agent", "w", "t0", "goal_no", "holdout", "active", "in_span", "labeled"] + [f"p_{s}" for s in V3]
    b = pl.read_parquet(SH / "behavior_states_v3.parquet", columns=cols).filter(pl.col("goal_no") == goal)
    if not allow_holdout:   # only confirm.py passes True
        hm = holdout_mask(b["pt_date"].to_list(), b["goal_no"].to_list())
        b = b.filter(~pl.Series(hm) & ~pl.col("holdout"))
    if days is not None:
        b = b.filter(pl.col("pt_date").is_in(days))
    P = b.select([f"p_{s}" for s in V3]).fill_null(0.0).to_numpy().astype(np.float64)
    tot = P.sum(1, keepdims=True)
    lab = (b["active"] & b["labeled"]).to_numpy() & (tot[:, 0] > 0)
    P = np.where(tot > 0, P / np.where(tot > 0, tot, 1), 0.0)
    fine = np.zeros((P.shape[0], len(FINE)))
    fine[lab, 1:] = P[lab]
    fine[~lab, 0] = 1.0
    if space == "coarse":
        idx = {s: i for i, s in enumerate(FINE)}
        X = np.stack([fine[:, [idx[s] for s in COARSE_GROUPS[g]]].sum(1) if g != "absent" else fine[:, 0]
                      for g in COARSE], 1)
    else:
        X = fine
    out = {}
    b = b.with_row_index("_r")
    for (d,), sub in b.group_by(["pt_date"], maintain_order=True):
        ags = sorted(sub["agent"].unique().to_list())
        nw = int(sub["w"].max()) + 1
        arr = np.zeros((len(ags), nw, X.shape[1]))
        arr[:, :, 0] = 1.0
        span = np.zeros((len(ags), nw), bool)
        ai = {a: k for k, a in enumerate(ags)}
        r = sub["_r"].to_numpy()
        ia = np.array([ai[a] for a in sub["agent"].to_list()])
        w = sub["w"].to_numpy()
        arr[ia, w] = X[r]
        span[ia, w] = sub["in_span"].to_numpy()
        keep = span.any(1)  # present that day
        t0 = sub.group_by("w").agg(pl.col("t0").min()).sort("w")
        out[d] = {"agents": [a for a, k in zip(ags, keep) if k], "X": arr[keep], "span": span[keep],
                  "t0": t0["t0"].to_list()}
    return dict(sorted(out.items()))


def trim_mask(span: np.ndarray) -> np.ndarray:
    """DQ8 all-present window (nulls.all_present_window): windows in which every present agent is in its span."""
    return span.all(0)


def steps_of(day: dict, trimmed: bool) -> np.ndarray:
    nw = day["X"].shape[1]
    s = np.arange(nw - 1)
    if trimmed:
        m = trim_mask(day["span"])
        s = s[m[:-1] & m[1:]]
    return s


def chunk_steps(steps: np.ndarray, size: int = 6, edge_aligned: bool = True) -> list[tuple[str, np.ndarray]]:
    """Blocks of `size` steps: first block 'start', last block 'end' (aligned to the day end), the rest 'mid'."""
    n = len(steps)
    if n == 0:
        return []
    if n <= 2 * size:
        return [("all", steps)]
    blocks = [("start", steps[:size])]
    mid = steps[size:n - size]
    k = len(mid) // size
    for i in range(k):
        sl = mid[i * size:(i + 1) * size] if i < k - 1 else mid[i * size:]
        blocks.append(("mid", sl))
    if k == 0 and len(mid):
        blocks.append(("mid", mid))
    blocks.append(("end", steps[n - size:]))
    return blocks


def block_flux(day: dict, steps: np.ndarray, agent_idx: np.ndarray | None = None):
    """Per-agent flux matrices (n_agents, n, n) summed over the block's steps."""
    X = day["X"] if agent_idx is None else day["X"][agent_idx]
    A = X[:, steps, :]
    B = X[:, steps + 1, :]
    Jper = np.einsum("ats,atu->asu", A, B)
    return Jper


def eval_block(Jper, M, rng, R=20, alpha=ALPHA):
    """Raw split, surrogate mean and 95th percentile for one block (Jper summed over agents; M agent-steps)."""
    raw = split(Jper.sum(0), M, alpha)
    if not R:
        return raw, np.zeros(3), np.full(3, np.nan)
    fl = surrogate_floor(Jper, M, rng, R, alpha)
    return raw, fl.mean(0), np.quantile(fl, 0.95, axis=0)


def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
