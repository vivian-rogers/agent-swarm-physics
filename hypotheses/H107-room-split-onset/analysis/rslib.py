"""Room-split estimators shared by H107 (onset) and H108 (direction wandering). Byte-identical copies live in
hypotheses/H107-room-split-onset/analysis/rslib.py and hypotheses/H108-goldstone-room-wandering/analysis/rslib.py
(STANDARDS section 8 forbids cross-hypothesis imports; candidate for infra/shared/).

Objects
- Panel: for one period P, the eligible agents (one room over their days, >= 2 days; H100's rule), their room labels,
  and per time bin b an (n_agents x 32) matrix of bin-centred agent vectors (mean of unit statement vectors, >= MIN_ST
  statements), minus the agent constant a_i when requested, with a presence mask. Bins: days, half-days, or blocks
  (agent means over a set of days).
- Excess cross-product C(b, b') = D(b).D(b') - <D_pi(b).D_pi(b')>_pi, D = mean(#best present) - mean(#rest present),
  pi = joint relabels of the period's agents (room sizes kept; the same partition in every bin). E(b) = C(b, b).
Rooms: BEST = 2, REST = 3. Statement vectors: shared embeddings/statements_<variant>_<model>.npy rows `srow`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
ED = ROOT / "data/processed/shared/embeddings"
BEST, REST = 2, 3
MIN_ST = 2
REG3 = [36, 37, 38, 39, 40, 41, 42, 44, 51]   # regime-III periods for agent constants (H100)
PERIODS = [35, 36, 37, 38, 39, 41, 42, 44]     # eligible #best/#rest periods
IDENTICAL = [36, 37, 39, 41, 42]
FIELDED = [38, 44]
PRE = {35: 33, 36: 35, 37: 36, 38: 37, 39: 38, 41: 40, 42: 41, 44: 42}  # previous non-holdout goal period (#34, #43 held out)
ARR = {"style_resid": "statements_style_resid32_{m}.npy", "white32": "statements_white32_{m}.npy"}


def regime_of(P: int) -> str:
    return "II" if P == 35 else "III"


def load_vectors(model: str, variant: str) -> np.ndarray:
    return np.load(ED / ARR[variant].format(m=model), mmap_mode="r")


# ----------------------------------------------------------------------------------------------- aggregation
def group_means(st: pl.DataFrame, V: np.ndarray, keys: list[str], min_n: int = MIN_ST):
    """Mean statement vector per group of `keys` (rows of st, column srow into V). Returns (keys frame with n, M)."""
    g = st.select(keys + ["srow"]).with_columns(pl.struct(keys).rank("dense").alias("_g") - 1)
    gi = g["_g"].to_numpy()
    ng = int(gi.max()) + 1 if len(gi) else 0
    X = np.asarray(V[g["srow"].to_numpy()], dtype=np.float64)
    S = np.zeros((ng, X.shape[1]))
    np.add.at(S, gi, X)
    n = np.bincount(gi, minlength=ng)
    kf = g.group_by("_g").agg([pl.col(k).first() for k in keys]).sort("_g")
    kf = kf.with_columns(pl.Series("n", n))
    M = S / np.maximum(n, 1)[:, None]
    keep = n >= min_n
    return kf.filter(pl.Series(keep)).drop("_g"), M[keep]


def day_centered_agent_days(st: pl.DataFrame, V: np.ndarray, goals) -> tuple[pl.DataFrame, np.ndarray]:
    """Agent-day means (>= MIN_ST statements), centred on the mean over agents present that day (same goal)."""
    s = st.filter(pl.col("goal_no").is_in(list(goals)))
    kf, M = group_means(s, V, ["goal_no", "pt_date", "agent", "regime", "room_day"])
    key = (kf["goal_no"].cast(pl.String) + "|" + kf["pt_date"]).to_numpy()
    Mc = M.copy()
    for k in np.unique(key):
        m = key == k
        Mc[m] -= M[m].mean(0)
    return kf, Mc


def constants(ad: pl.DataFrame, Xc: np.ndarray, exclude: set[int]) -> dict[int, np.ndarray]:
    """H100's leave-period-out agent constant: mean over regime-III periods not in `exclude` of the agent's period mean."""
    acc: dict[int, list] = {}
    for P in REG3:
        if P in exclude:
            continue
        m = ((ad["goal_no"] == P) & (ad["regime"] == "III")).to_numpy()
        if not m.any():
            continue
        sub = ad.filter(pl.Series(m)).with_columns(pl.Series("ix", np.nonzero(m)[0]))
        for a, g in sub.group_by("agent"):
            acc.setdefault(int(a[0]), []).append(Xc[g["ix"].to_numpy()].mean(0))
    return {a: np.mean(v, 0) for a, v in acc.items()}


# ------------------------------------------------------------------------------------------------- panel
@dataclass
class Panel:
    P: int
    agents: np.ndarray            # agent codes (n,)
    lab: np.ndarray               # room labels (n,)
    days: list                    # sorted PT days used
    bins: list                    # bin keys
    X: np.ndarray                 # (n_bins, n, 32), 0 where absent
    M: np.ndarray                 # (n_bins, n) bool presence
    X1: np.ndarray | None = None  # split halves (statement parity), day bins only
    X2: np.ndarray | None = None
    M12: np.ndarray | None = None
    info: dict = field(default_factory=dict)


def period_statements(st: pl.DataFrame, P: int) -> pl.DataFrame:
    return st.filter((pl.col("goal_no") == P) & (pl.col("regime") == regime_of(P)))


def eligible_agents(sp: pl.DataFrame, min_days: int = 2):
    """Agents whose room of the day is one room (#best or #rest) on all their days with >= MIN_ST statements."""
    ad = sp.group_by("agent", "pt_date").agg(pl.len().alias("n"), pl.col("room_day").first())
    ad = ad.filter(pl.col("n") >= MIN_ST)
    g = ad.group_by("agent").agg(pl.col("room_day").n_unique().alias("nr"), pl.col("room_day").first(),
                                 pl.len().alias("nd"))
    g = g.filter((pl.col("nr") == 1) & (pl.col("nd") >= min_days) & pl.col("room_day").is_in([BEST, REST]))
    g = g.sort("agent")
    return g["agent"].to_numpy(), g["room_day"].to_numpy()


def build_panel(st: pl.DataFrame, V: np.ndarray, P: int, level: str = "day", consts: dict | None = None,
                halves: bool = False, days: list | None = None) -> Panel:
    """level: 'day' or 'half'. Bin centring uses every agent with a vector in the bin (both rooms, all agents)."""
    sp = period_statements(st, P)
    if days is not None:
        sp = sp.filter(pl.col("pt_date").is_in(list(days)))
    agents, lab = eligible_agents(sp)
    dlist = sorted(sp["pt_date"].unique().to_list())
    keys = ["pt_date"] if level == "day" else ["pt_date", "half"]
    kf, Mx = group_means(sp, V, keys + ["agent"])
    bkeys = sorted(set(map(tuple, kf.select(keys).rows())))
    bidx = {b: k for k, b in enumerate(bkeys)}
    aidx = {int(a): k for k, a in enumerate(agents)}
    nb, n = len(bkeys), len(agents)
    X = np.zeros((nb, n, Mx.shape[1])); M = np.zeros((nb, n), bool)
    kb = [bidx[tuple(r)] for r in kf.select(keys).rows()]
    ka = kf["agent"].to_list()
    kb = np.array(kb)
    for b in range(nb):  # centre on all agents present in the bin
        m = kb == b
        cen = Mx[m].mean(0)
        for r in np.nonzero(m)[0]:
            a = int(ka[r])
            if a in aidx:
                v = Mx[r] - cen
                if consts is not None:
                    v = v - consts.get(a, np.zeros_like(v))
                X[b, aidx[a]] = v; M[b, aidx[a]] = True
    pan = Panel(P, agents, lab, dlist, bkeys, X, M, info={"n_best": int((lab == BEST).sum()),
                                                         "n_rest": int((lab == REST).sum())})
    if halves and level == "day":
        kf2, M2 = group_means(sp, V, ["pt_date", "agent", "parity"], min_n=1)
        X1 = np.zeros_like(X); X2 = np.zeros_like(X); M12 = np.zeros_like(M)
        # centre halves with the same bin centre as the full vectors (all agents present in the bin)
        cen_full = {}
        for b in range(nb):
            m = kb == b
            cen_full[b] = Mx[m].mean(0)
        H = {}
        for (d, a, p), v in zip(kf2.select("pt_date", "agent", "parity").rows(), M2):
            H[(d, int(a), int(p))] = v
        for b, bk in enumerate(bkeys):
            d = bk[0]
            for a, k in aidx.items():
                if not M[b, k]:
                    continue
                if (d, a, 0) in H and (d, a, 1) in H:
                    c = cen_full[b] + (consts.get(a, 0) if consts is not None else 0)
                    X1[b, k] = H[(d, a, 0)] - c; X2[b, k] = H[(d, a, 1)] - c; M12[b, k] = True
        pan.X1, pan.X2, pan.M12 = X1, X2, M12
    return pan


def block(pan: Panel, bins_ix: list[int]):
    """Agent means over a set of bins (equal bin weights). Returns (x (n, 32), mask (n,))."""
    M = pan.M[bins_ix]; X = pan.X[bins_ix]
    cnt = M.sum(0)
    x = X.sum(0) / np.maximum(cnt, 1)[:, None]
    return x, cnt > 0


# ------------------------------------------------------------------------------------------ joint relabel
def perms(lab: np.ndarray, n: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    is_b = lab == BEST
    return np.array([rng.permutation(is_b) for _ in range(n)])  # (n, n_agents) bool


def deltas(x: np.ndarray, m: np.ndarray, isb: np.ndarray, min_room: int = 2):
    """D for each labelling row of isb (k, n): mean(best present) - mean(rest present); NaN rows if a room has
    < min_room present agents."""
    B = isb & m[None, :]; R = (~isb) & m[None, :]
    nb, nr = B.sum(1), R.sum(1)
    D = (B @ x) / np.maximum(nb, 1)[:, None] - (R @ x) / np.maximum(nr, 1)[:, None]
    D[(nb < min_room) | (nr < min_room)] = np.nan
    return D


def excess(xa, ma, xb, mb, lab, PI):
    """C = D_a.D_b - mean over joint relabels; returns dict(obs, null_mean, C, z, p)."""
    isb0 = (lab == BEST)[None, :]
    Da, Db = deltas(xa, ma, isb0)[0], deltas(xb, mb, isb0)[0]
    obs = float(Da @ Db)
    Pa, Pb = deltas(xa, ma, PI), deltas(xb, mb, PI)
    nul = np.einsum("ij,ij->i", Pa, Pb)
    nul = nul[np.isfinite(nul)]
    if not np.isfinite(obs) or len(nul) < 20:
        return {"obs": np.nan, "null_mean": np.nan, "C": np.nan, "z": np.nan, "p": np.nan, "n_null": len(nul)}
    mu, sd = float(nul.mean()), float(nul.std())
    return {"obs": obs, "null_mean": mu, "C": obs - mu, "z": (obs - mu) / sd if sd > 0 else np.nan,
            "p": float((1 + (nul >= obs).sum()) / (1 + len(nul))), "n_null": len(nul)}


def excess_matrix(xs: list, ms: list, lab, PI):
    """All pairwise C over a list of bins (vectorized over relabels). Returns C (k,k), obs, z (k,k), p diag."""
    k = len(xs)
    isb0 = (lab == BEST)[None, :]
    D0 = np.array([deltas(x, m, isb0)[0] for x, m in zip(xs, ms)])      # (k, 32)
    Dp = np.array([deltas(x, m, PI) for x, m in zip(xs, ms)])           # (k, nperm, 32)
    obs = D0 @ D0.T
    C = np.full((k, k), np.nan); Z = np.full((k, k), np.nan); Pv = np.full((k, k), np.nan)
    for a in range(k):
        for b in range(a, k):
            nul = np.einsum("ij,ij->i", Dp[a], Dp[b]); nul = nul[np.isfinite(nul)]
            if not np.isfinite(obs[a, b]) or len(nul) < 20:
                continue
            mu, sd = nul.mean(), nul.std()
            C[a, b] = C[b, a] = obs[a, b] - mu
            Z[a, b] = Z[b, a] = (obs[a, b] - mu) / sd if sd > 0 else np.nan
            Pv[a, b] = Pv[b, a] = (1 + (nul >= obs[a, b]).sum()) / (1 + len(nul))
    return C, obs, Z, Pv


def resample_agents(pan: Panel, rng) -> Panel:
    """Agent bootstrap within rooms (duplicates kept as distinct agents)."""
    ix = []
    for r in (BEST, REST):
        idx = np.nonzero(pan.lab == r)[0]
        ix.append(rng.choice(idx, len(idx)))
    ix = np.concatenate(ix)
    q = Panel(pan.P, pan.agents[ix], pan.lab[ix], pan.days, pan.bins, pan.X[:, ix], pan.M[:, ix], info=pan.info)
    if pan.X1 is not None:
        q.X1, q.X2, q.M12 = pan.X1[:, ix], pan.X2[:, ix], pan.M12[:, ix]
    return q


# ------------------------------------------------------------------------------------------- directions
def split_share(d1, d2, u):
    """H100's field share (D1.u)(D2.u)/S with S = D1.D2; NaN if S <= 0."""
    S = float(d1 @ d2)
    if not np.isfinite(S) or S <= 0:
        return np.nan, S
    return float((d1 @ u) * (d2 @ u) / S), S


def direction_null(xw: np.ndarray, d1, d2, n: int = 2000, seed: int = 1):
    """Random unit directions from the empirical (within-room centred) between-agent covariance (H20, H100)."""
    rng = np.random.default_rng(seed)
    C = np.cov(xw.T)
    L = np.linalg.cholesky(C + 1e-9 * np.eye(C.shape[0]))
    S = float(d1 @ d2)
    U = (L @ rng.standard_normal((C.shape[0], n))).T
    U /= np.linalg.norm(U, axis=1, keepdims=True)
    return (U @ d1) * (U @ d2) / S


def alt_day_halves(pan: Panel):
    """Agent half means over alternating days (H100's S): returns (H1, H2, ok)."""
    n = len(pan.agents)
    H1 = np.zeros((n, pan.X.shape[2])); H2 = np.zeros_like(H1); ok = np.zeros(n, bool)
    for k in range(n):
        b = np.nonzero(pan.M[:, k])[0]
        if len(b) < 2:
            continue
        H1[k] = pan.X[b[0::2], k].mean(0); H2[k] = pan.X[b[1::2], k].mean(0); ok[k] = True
    return H1, H2, ok
