"""H38 core library: stall flags on a fixed population, stall-adjusted Curie-Weiss gain, joint N1 surrogates,
stall-adjusted market mode (lambda_1) with joint cross-day surrogates.

Reused by import (never modified): H02 `h02lib.block_ids` (30-min blocks, short trailing block merged), H12 `h12lib`
(`corr_eig`, `_pad_days`, `unit_of`). The Curie-Weiss estimator is H02/H19's: within (day, block) b,
VR = sum_b n_b Var_b(M) / sum_b n_b sum_i Var_b(s_i), q = mean single-spin variance, g = 1 - 1/VR, bJ0 = g/q; blocks
(or sub-blocks) with < 5 minutes are skipped (H19's MIN_BLOCK_N).

Reason codes (scheme/build_outages.py): 0 none, 1 pre, 2 post, 3 infra_err, 4 consol, 5 pause.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("POLARS_MAX_THREADS", "2")

import importlib.util  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

sys.dont_write_bytecode = True  # never leave __pycache__ in other hypotheses' folders
HYP = Path(__file__).resolve().parents[1]
ROOT = HYP.parents[1]
DATA = ROOT / "data/processed/H38-platform-stalls"
SH = ROOT / "data/processed/shared"
SEED = 20261004


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


h02 = _load("h02lib", ROOT / "hypotheses/H02-couplings-are-real/analysis/h02lib.py")
h12 = _load("h12lib", ROOT / "hypotheses/H12-groupthink-dimensional-collapse/analysis/h12lib.py")

MIN_BLOCK_N = 5
CAUSES = ["scheduled", "edge", "infra_error", "pause", "consolidation", "unexplained"]
R_NONE, R_PRE, R_POST, R_INFRA, R_CONSOL, R_PAUSE = 0, 1, 2, 3, 4, 5


# ------------------------------------------------------------------------------------------- stall flags
def stall_flags(S: np.ndarray, R: np.ndarray, sched: np.ndarray, strict: bool = False) -> dict:
    """S (T, N) in {-1,+1}; R (T, N) reason codes (only meaningful where S = -1); sched (T,) village-level flag.
    Returns per-minute K, js (K <= 1), explained (js & (sched | >= half of silent agents have a reason)), cause index
    (into CAUSES; -1 where not js), and the infra-burst flag (>= 2 agents in an infra-error gap)."""
    T, N = S.shape
    act = S > 0
    K = act.sum(1)
    sil = ~act
    has = sil & (R > 0)
    n_sil = N - K
    nrec = has.sum(1)
    js = K <= 1
    if strict:
        expl_r = nrec >= n_sil - 1
    else:
        expl_r = 2 * nrec >= n_sil
    explained = js & (sched | expl_r)
    edge = (sil & ((R == R_PRE) | (R == R_POST))).sum(1)
    inf = (sil & (R == R_INFRA)).sum(1)
    pau = (sil & (R == R_PAUSE)).sum(1)
    con = (sil & (R == R_CONSOL)).sum(1)
    counts = np.stack([edge, inf, pau, con], 1)
    best = counts.argmax(1)  # ties -> first (edge > infra > pause > consolidation)
    cause = np.where(~js, -1, np.where(sched, 0, np.where(explained, 1 + best, 5)))
    return {"K": K, "js": js, "explained": explained, "cause": cause, "burst": inf >= 2}


# ------------------------------------------------------------------------------------------- Curie-Weiss
def block_suff(S: np.ndarray, bid: np.ndarray, keep: np.ndarray | None = None, sub: np.ndarray | None = None) -> np.ndarray:
    """Per (block[, sub-block]) with >= MIN_BLOCK_N kept minutes: n, n Var(M), n sum_i Var(s_i), n mean_i Var(s_i)."""
    X = S.astype(np.float64)
    key = bid.astype(np.int64) * 4 + (0 if sub is None else sub.astype(np.int64))
    if keep is not None:
        X, key = X[keep], key[keep]
    if X.shape[0] == 0:
        return np.zeros((0, 4))
    order = np.argsort(key, kind="stable")
    X, key = X[order], key[order]
    cuts = np.flatnonzero(np.diff(key)) + 1
    starts = np.r_[0, cuts]
    ends = np.r_[cuts, len(key)]
    n = ends - starts
    ok = n >= MIN_BLOCK_N
    M = X.sum(1)
    cs = np.vstack([np.zeros((1, X.shape[1])), np.cumsum(X, 0)])
    cs2 = np.vstack([np.zeros((1, X.shape[1])), np.cumsum(X ** 2, 0)])
    cm = np.r_[0, np.cumsum(M)]
    cm2 = np.r_[0, np.cumsum(M ** 2)]
    s1 = cs[ends] - cs[starts]
    s2 = cs2[ends] - cs2[starts]
    nn = n[:, None].astype(np.float64)
    v = s2 / nn - (s1 / nn) ** 2
    vm = (cm2[ends] - cm2[starts]) / n - ((cm[ends] - cm[starts]) / n) ** 2
    out = np.column_stack([n, vm * n, v.sum(1) * n, v.mean(1) * n])
    return out[ok]


def cw(st: np.ndarray) -> dict:
    if st.shape[0] == 0 or st[:, 2].sum() <= 0:
        return {"VR": np.nan, "q": np.nan, "g": np.nan, "bJ0": np.nan, "n": 0}
    VR = st[:, 1].sum() / st[:, 2].sum()
    q = st[:, 3].sum() / st[:, 0].sum()
    return {"VR": VR, "q": q, "g": 1 - 1 / VR, "bJ0": (1 - 1 / VR) / q, "n": int(st[:, 0].sum())}


def variant_masks(S, R, sched):
    """Minute masks (keep) / sub-block labels for every stall adjustment. Returns dict name -> (keep, sub)."""
    f = stall_flags(S, R, sched)
    fs = stall_flags(S, R, sched, strict=True)
    stall = f["explained"]
    out = {"raw": (None, None),
           "lull": (~f["js"], None),
           "stall": (~stall, None),
           "stall_strict": (~fs["explained"], None),
           "field": (None, stall.astype(np.int8)),
           "exo": (~(sched | f["burst"]), None)}
    for ci, c in enumerate(CAUSES):
        out[f"drop_{c}"] = (~(f["cause"] == ci), None)
    return out, f


MASK_SETS = {"mask_edge": (R_PRE, R_POST), "mask_infra": (R_PRE, R_POST, R_INFRA),
             "mask_scaffold": (R_PRE, R_POST, R_INFRA, R_CONSOL), "mask_all": (R_PRE, R_POST, R_INFRA, R_CONSOL, R_PAUSE)}


def impute(S: np.ndarray, R: np.ndarray, bid: np.ndarray, codes) -> np.ndarray:
    """Agent-state conditioning: agent-minutes whose silence has a recorded reason in `codes` are treated as
    unavailable and set to the agent's mean spin over its available minutes of the same block (zero deviation), so a
    synchronized scaffold state contributes no covariance. Returns a float matrix."""
    X = S.astype(np.float64)
    un = np.isin(R, codes) & (S < 0)
    if not un.any():
        return X
    nb = int(bid.max()) + 1
    N = S.shape[1]
    av = ~un
    sums = np.zeros((nb, N)); cnt = np.zeros((nb, N))
    np.add.at(sums, bid, np.where(av, X, 0.0))
    np.add.at(cnt, bid, av.astype(np.float64))
    mean = np.where(cnt > 0, sums / np.maximum(cnt, 1), -1.0)
    X[un] = mean[bid][un]
    return X


def gains(S, R, sched, bid, talk: np.ndarray | None = None, masks_on: bool = True, talk_cols=None) -> dict:
    """g for every variant on activity spins (and on talk spins with the activity-defined masks if talk is given).
    Returns {name: (suffstats_active, suffstats_talk or None)} plus flags.
    Variants: raw, lull, stall, stall_strict, field, exo, drop_<cause>, and the agent-state-conditioned mask_* sets
    (scheduled minutes dropped, then unavailable agent-minutes imputed)."""
    masks, f = variant_masks(S, R, sched)
    res = {}
    for name, (keep, sub) in masks.items():
        a = block_suff(S, bid, keep, sub)
        t = block_suff(talk, bid, keep, sub) if talk is not None else None
        res[name] = (a, t)
    if masks_on:
        keep = ~sched
        for name, codes in MASK_SETS.items():
            Xa = impute(S, R, bid, codes)
            a = block_suff(Xa, bid, keep)
            Rt = R if talk_cols is None else R[:, talk_cols]
            t = block_suff(impute(talk, Rt, bid, codes), bid, keep) if talk is not None else None
            res[name] = (a, t)
    return res, f


# ------------------------------------------------------------------------------------------- surrogates
def joint_shift(arrays: list[np.ndarray], segs: list[np.ndarray], rng: np.random.Generator) -> list[np.ndarray]:
    """Independent circular shift of each agent's series within each segment, the same shift for every array
    (spins, reasons, talk spins all move together for an agent). arrays: (T, N) each."""
    outs = [np.empty_like(a) for a in arrays]
    N = arrays[0].shape[1]
    for idx in segs:
        L = idx.size
        if L < 2:
            for a, o in zip(arrays, outs):
                o[idx] = a[idx]
            continue
        sh = rng.integers(1, L, size=N)
        ar = (np.arange(L)[:, None] - sh[None, :]) % L
        cols = np.arange(N)[None, :]
        for a, o in zip(arrays, outs):
            o[idx] = a[idx][ar, cols]
    return outs


def block_segments(day: np.ndarray, minute: np.ndarray) -> tuple[np.ndarray, list[np.ndarray]]:
    bid = h02.block_ids(day, minute)
    order = np.argsort(bid, kind="stable")
    k = bid[order]
    cuts = np.flatnonzero(np.diff(k)) + 1
    return bid, np.split(order, cuts)


# ------------------------------------------------------------------------------------------- lambda_1 (H12)
def crossday_joint(P_list: list[np.ndarray], L: np.ndarray, rng: np.random.Generator) -> list[np.ndarray]:
    """H12's cross-day surrogate applied jointly to several padded arrays (N x D x Lmax): agent i's day d <- the same
    agent's day (d + c_i) mod D, offsets balanced over agents; then cut each day back to its own length."""
    N, D = P_list[0].shape[0], P_list[0].shape[1]
    c = rng.permutation(np.arange(N) % D)
    idx = (np.arange(D)[None, :] + c[:, None]) % D
    outs = []
    for P in P_list:
        Sx = P[np.arange(N)[:, None], idx]
        outs.append(np.concatenate([Sx[:, d, :L[d]] for d in range(D)], axis=1))
    return outs


def l1_variants(X: np.ndarray, R: np.ndarray, sched: np.ndarray, bid: np.ndarray) -> dict:
    """X, R: N x T (H12 orientation); sched, bid (T,). Top eigenvalue of the equal-time correlation: raw / lull /
    stall (drop explained JS minutes) / mask_scaffold (scheduled dropped, scaffold-unavailable agent-minutes imputed
    with the agent's unit-level mean over its available minutes: H12's correlation is over the whole unit, not within
    blocks, so a constant fill is what removes their contribution to the covariance)."""
    f = stall_flags(X.T, R.T, sched)
    out = {}
    for name, keep in (("raw", None), ("lull", ~f["js"]), ("stall", ~f["explained"])):
        Y = X if keep is None else X[:, keep]
        out[name] = float(h12.corr_eig(Y)[0]) if Y.shape[1] > Y.shape[0] else np.nan
    Xi = impute(X.T, R.T, np.zeros(X.shape[1], dtype=np.int64), MASK_SETS["mask_scaffold"]).T[:, ~sched]
    out["mask_scaffold"] = float(h12.corr_eig(Xi)[0]) if Xi.shape[1] > Xi.shape[0] else np.nan
    return out


# ------------------------------------------------------------------------------------------- O6 two-state formula
def o6_predict(S: np.ndarray, bid: np.ndarray, stall: np.ndarray) -> dict:
    """Predict the raw within-block variance ratio from the stall indicator and the non-stall process only:
    x = (s+1)/2; per block, pi = stall fraction, p_i and C_ij from non-stall minutes;
    Var(x_i) = (1-pi) p_i - (1-pi)^2 p_i^2, Cov(x_i, x_j) = (1-pi) C_ij + pi (1-pi) p_i p_j (agents all off in stalls)."""
    X = (S > 0).astype(np.float64)
    num = den = 0.0
    for b in np.unique(bid):
        m = bid == b
        n = int(m.sum())
        if n < MIN_BLOCK_N:
            continue
        ns = m & ~stall
        if ns.sum() < 2:
            continue
        pi = 1 - ns.sum() / n
        Y = X[ns]
        p = Y.mean(0)
        C = np.cov(Y, rowvar=False, bias=True)
        var = (1 - pi) * p - (1 - pi) ** 2 * p ** 2
        cov = (1 - pi) * C + pi * (1 - pi) * np.outer(p, p)
        np.fill_diagonal(cov, var)
        num += n * cov.sum()
        den += n * var.sum()
    if den <= 0:
        return {"VR": np.nan, "g": np.nan, "num": 0.0, "den": 0.0}
    VR = num / den
    return {"VR": VR, "g": 1 - 1 / VR, "num": num, "den": den}
