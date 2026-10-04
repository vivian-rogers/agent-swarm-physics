"""H95 library: slack S = A-bar T / W of the post-kickoff re-allocation, and kickoff specificity x.

COPIED (2026-10-04, with attribution) from hypotheses/H75-reallocation-speed-limit/analysis/h75lib.py: Ensemble,
state_matrix, switch_cum, occupancy, settle_stats, bootstrap, write_json (unchanged). Not imported across folders.
New here: day1_shares, specificity, concentration, permuted_ensemble (within-agent label permutation, S0),
subsample (size-matched S12).

H75 docstring: repo allocation after a kickoff and the Wasserstein speed limit T >= W / A-bar.

An ensemble is a dict agent -> (times, codes) of work commits in active hours since the kickoff (t = 0), plus each
agent's initial state at t = 0- (a repo code, or -1 for the null state). The same functions run on real commits
(`scheme/build.py`) and on synthetic agents (`synthetic.py`).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import json  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402
from dataclasses import dataclass, field  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
SH = ROOT / "data/processed/shared"
OUTD = ROOT / "data/processed/H95-slack-specificity-gauge"
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import holdout_mask  # noqa: E402

GRID_H = 0.25
NULL = -1
SUMMARY_CALLS = ("consolidate", "session_start", "session_stop")


@dataclass
class Ensemble:
    agents: list
    times: list            # per agent: np.ndarray of commit times (active h), sorted, > 0
    codes: list            # per agent: np.ndarray of repo codes
    init: np.ndarray       # per agent: initial state at t = 0-
    H: float               # horizon (active h)
    settle_win: float = 4.0
    extra: dict = field(default_factory=dict)


# ============================================================================ statistics
def state_matrix(E: Ensemble, grid: np.ndarray) -> np.ndarray:
    S = np.empty((len(E.agents), len(grid)), np.int64)
    for i in range(len(E.agents)):
        t, c = E.times[i], E.codes[i]
        k = np.searchsorted(t, grid, side="right")   # commits <= g
        S[i] = np.where(k > 0, c[np.maximum(k - 1, 0)], E.init[i])
    return S


def switch_cum(E: Ensemble, grid: np.ndarray) -> np.ndarray:
    """Cumulative switches per agent up to each grid time (a change of state between consecutive observations)."""
    C = np.zeros((len(E.agents), len(grid)), np.int64)
    for i in range(len(E.agents)):
        t, c = E.times[i], E.codes[i]
        if len(t) == 0:
            continue
        prev = np.r_[E.init[i], c[:-1]]
        sw_t = t[c != prev]
        C[i] = np.searchsorted(sw_t, grid, side="right")
    return C


def occupancy(S: np.ndarray, rows: np.ndarray | None = None) -> np.ndarray:
    """(n_grid, n_states) occupancy shares; states remapped to 0..K-1 over the whole matrix."""
    X = S if rows is None else S[rows]
    _, inv = np.unique(S, return_inverse=True)
    inv = inv.reshape(S.shape)
    if rows is not None:
        inv = inv[rows]
    K = inv.max() + 1
    P = np.zeros((X.shape[1], K))
    for g in range(X.shape[1]):
        P[g] = np.bincount(inv[:, g], minlength=K)
    return P / X.shape[0]


def settle_stats(E: Ensemble, rows: np.ndarray | None = None, S=None, C=None, grid=None) -> dict:
    grid = np.arange(0, E.H + 1e-9, GRID_H) if grid is None else grid
    S = state_matrix(E, grid) if S is None else S
    C = switch_cum(E, grid) if C is None else C
    rows = np.arange(S.shape[0]) if rows is None else rows
    N = len(rows)
    # state at 0- (initial) prepended
    S0 = np.c_[E.init, S]
    P = occupancy(S0, rows)                       # row 0 = t = 0-, then grid
    P0, Pg = P[0], P[1:]
    sw = grid >= E.H - E.settle_win - 1e-9
    pinf = Pg[sw].mean(0)
    D = 0.5 * np.abs(Pg - pinf).sum(1)
    D0 = 0.5 * np.abs(P0 - pinf).sum()
    Df = float(np.median(D[sw]))
    out = {"N": N, "D0": float(D0), "Df": Df, "W_total": float(0.5 * np.abs(P0 - Pg[-1]).sum())}
    Cs = C[rows]
    A_ss = (Cs[:, -1] - Cs[:, np.argmax(sw)]).sum() / (N * E.settle_win)   # switches in the settled window
    out["A_ss"] = float(A_ss)
    for lab, frac in (("e", 1 / math.e), ("90", 0.1)):
        thr = Df + frac * (D0 - Df)
        hit = np.nonzero(D <= thr + 1e-12)[0]
        if D0 - Df <= 0.02 or len(hit) == 0:
            out.update({f"T_{lab}": np.nan, f"W_{lab}": np.nan, f"A_{lab}": np.nan, f"S_{lab}": np.nan,
                        f"R_{lab}": np.nan, f"Sigma_ex_min_{lab}": np.nan, f"viol_{lab}": False})
            continue
        g = hit[0]
        T = max(grid[g], GRID_H)
        gT = max(g, 1) if grid[g] == 0 else g
        W = 0.5 * np.abs(P0 - Pg[gT]).sum()
        nsw = Cs[:, gT].sum()
        A = nsw / (N * T)
        Sl = A * T / W if W > 0 else np.nan
        out.update({f"T_{lab}": float(T), f"W_{lab}": float(W), f"A_{lab}": float(A), f"S_{lab}": float(Sl),
                    f"R_{lab}": float(A_ss * T / W) if W > 0 else np.nan,
                    f"Sigma_ex_min_{lab}": float(2 * W * math.atanh(min(1 / Sl, 1 - 1e-12))) if Sl and Sl >= 1 else np.nan,
                    f"viol_{lab}": bool(A * T < W - 1e-9)})
    out["curve_D"] = D.tolist()
    return out


def bootstrap(E: Ensemble, B: int, rng, keys=("T_e", "W_e", "A_e", "S_e", "R_e", "T_90", "S_90", "R_90")) -> dict:
    grid = np.arange(0, E.H + 1e-9, GRID_H)
    S = state_matrix(E, grid)
    C = switch_cum(E, grid)
    n = len(E.agents)
    acc = {k: [] for k in keys}
    for _ in range(B):
        rows = rng.choice(n, n, replace=True)
        s = settle_stats(E, rows, S, C, grid)
        for k in keys:
            acc[k].append(s.get(k, np.nan))
    out = {}
    for k, v in acc.items():
        v = np.array(v, float)
        out[k] = [float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5))] if np.isfinite(v).any() else [np.nan, np.nan]
        out[k + "_cens"] = float(np.isnan(v).mean())
    return out


def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)

    def enc(o):
        if hasattr(o, "item"):
            return o.item()
        return str(o)
    path.write_text(json.dumps(obj, indent=1, default=enc))


# ============================================================================ H95 additions
def day1_shares(E: Ensemble, t1: float = 4.0) -> np.ndarray:
    """Commit counts per repo code in (0, t1] active hours, summed over the ensemble's agents (codes as in E)."""
    c = [E.codes[i][(E.times[i] > 0) & (E.times[i] <= t1)] for i in range(len(E.agents))]
    c = np.concatenate(c) if c else np.zeros(0, np.int64)
    return c


def specificity(E: Ensemble, named_codes: set, t1: float = 4.0, agent_weighted: bool = False) -> float:
    """x = share of day-1 agent-work commits on kickoff-named repos (agent_weighted: mean of per-agent shares)."""
    if agent_weighted:
        v = []
        for i in range(len(E.agents)):
            c = E.codes[i][(E.times[i] > 0) & (E.times[i] <= t1)]
            if len(c):
                v.append(np.isin(c, list(named_codes)).mean())
        return float(np.mean(v)) if v else np.nan
    c = day1_shares(E, t1)
    return float(np.isin(c, list(named_codes)).mean()) if len(c) else np.nan


def concentration(E: Ensemble, t1: float = 4.0) -> tuple[float, float]:
    """(1 - H/ln n_repos, top-repo share) of day-1 commits."""
    c = day1_shares(E, t1)
    if len(c) == 0:
        return np.nan, np.nan
    _, n = np.unique(c, return_counts=True)
    p = n / n.sum()
    if len(p) == 1:
        return 1.0, 1.0
    H = -(p * np.log(p)).sum()
    return float(1 - H / np.log(len(p))), float(p.max())


def permuted_ensemble(E: Ensemble, rng) -> Ensemble:
    """Within-agent label permutation: each agent's repo codes in the horizon are shuffled among its own commit times.
    Keeps commit times, each agent's repo multiset and commit count; destroys directed movement (S0 baseline)."""
    codes = [rng.permutation(c) for c in E.codes]
    return Ensemble(E.agents, E.times, codes, E.init, E.H, E.settle_win, dict(E.extra))


def subsample(E: Ensemble, idx) -> Ensemble:
    idx = list(idx)
    return Ensemble([E.agents[i] for i in idx], [E.times[i] for i in idx], [E.codes[i] for i in idx], E.init[idx],
                    E.H, E.settle_win, dict(E.extra))


def spearman(x, y) -> float:
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    if len(x) < 3:
        return np.nan
    from scipy.stats import rankdata          # average ranks for ties
    rx, ry = rankdata(x), rankdata(y)
    return float(np.corrcoef(rx, ry)[0, 1])


def perm_p_spearman(x, y, rng=None, exact_max: int = 9) -> tuple[float, float]:
    """One-sided p for rho <= observed (negative tail): exact over all orderings when n <= exact_max, else 20,000 draws."""
    import itertools
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    r0 = spearman(x, y)
    n = len(x)
    if n < 3:
        return r0, np.nan
    if n <= exact_max:
        vals = [spearman(x, y[list(p)]) for p in itertools.permutations(range(n))]
    else:
        rng = rng or np.random.default_rng(0)
        vals = [spearman(x, rng.permutation(y)) for _ in range(20000)]
    vals = np.array(vals)
    return r0, float((vals <= r0 + 1e-12).mean())


