"""H75 library: repo allocation after a kickoff and the Wasserstein speed limit T >= W / A-bar.

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
OUTD = ROOT / "data/processed/H75-reallocation-speed-limit"
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


def agent_settling(E: Ensemble, S=None, grid=None) -> pl.DataFrame:
    """t_i = first commit (t > 0) on the agent's settled repo (modal state over the settled window)."""
    grid = np.arange(0, E.H + 1e-9, GRID_H) if grid is None else grid
    S = state_matrix(E, grid) if S is None else S
    sw = grid >= E.H - E.settle_win - 1e-9
    rows = []
    for i, a in enumerate(E.agents):
        vals, cnt = np.unique(S[i, sw], return_counts=True)
        settled = vals[np.argmax(cnt)]
        t, c = E.times[i], E.codes[i]
        n_commit = int((t <= E.H).sum())
        tmid = np.nan
        if settled == NULL:
            ti, why = np.nan, "settled_null"
        elif E.init[i] == settled:
            ti, why = np.nan, "no_move"
        else:
            hit = np.nonzero(c == settled)[0]
            if len(hit):
                k = hit[0]
                ti, why = float(t[k]), "ok"
                tprev = float(t[k - 1]) if k > 0 else 0.0     # last observation off the settled repo (or the kickoff)
                tmid = 0.5 * (tprev + ti)
            else:
                ti, why = np.nan, "never"
        rows.append({"agent": a, "t_i": ti, "t_mid": tmid, "why": why, "commit_rate": n_commit / E.H,
                     "first_commit": float(t[0]) if len(t) else np.nan})
    return pl.DataFrame(rows)


def ols_slope(y, X):
    """OLS with HC1 SE. X without intercept; returns (coef, se) arrays incl. intercept first."""
    X = np.c_[np.ones(len(y)), X]
    n, k = X.shape
    if n <= k:
        return np.full(k, np.nan), np.full(k, np.nan)
    XtX = np.linalg.pinv(X.T @ X)
    b = XtX @ X.T @ y
    e = y - X @ b
    V = XtX @ (X.T * e ** 2) @ X @ XtX * n / (n - k)
    return b, np.sqrt(np.diag(V))


def elasticity(df: pl.DataFrame, col: str = "t_i") -> dict:
    df = df.with_columns(pl.col(col).alias("t_i"))
    d = df.filter(pl.col("t_i").is_not_null() & pl.col("t_i").is_not_nan() & (pl.col("t_i") > 0)
                  & (pl.col("call_rate") > 0) & (pl.col("commit_rate") > 0))
    out = {"n": d.height}
    if d.height < 4:
        return out | {"eps": np.nan, "se": np.nan, "eps_ctrl": np.nan, "se_ctrl": np.nan}
    y = np.log(d["t_i"].to_numpy())
    lr = np.log(d["call_rate"].to_numpy())
    lc = np.log(d["commit_rate"].to_numpy())
    b, se = ols_slope(y, lr[:, None])
    out.update(eps=float(b[1]), se=float(se[1]))
    if d.height >= 5:
        b2, se2 = ols_slope(y, np.c_[lr, lc])
        out.update(eps_ctrl=float(b2[1]), se_ctrl=float(se2[1]), commit_coef=float(b2[2]))
    else:
        out.update(eps_ctrl=np.nan, se_ctrl=np.nan)
    return out


def re_mean(est, se):
    """DerSimonian-Laird random-effects mean."""
    est, se = np.asarray(est, float), np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[ok], se[ok]
    if len(est) == 0:
        return np.nan, np.nan, np.nan
    w = 1 / se ** 2
    m = (w * est).sum() / w.sum()
    Q = (w * (est - m) ** 2).sum()
    tau2 = max(0.0, (Q - (len(est) - 1)) / (w.sum() - (w ** 2).sum() / w.sum())) if len(est) > 1 else 0.0
    ws = 1 / (se ** 2 + tau2)
    mr = (ws * est).sum() / ws.sum()
    return float(mr), float(np.sqrt(1 / ws.sum())), float(np.sqrt(tau2))


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
