"""Krakauer individuality estimators (held-out log-loss), shared by H145-H148 (H145 owns this module, 2026-10-09).

Generalized from hypotheses/H58-coordinated-superagents/analysis/h58lib.py: krakauer (lines 483-543). Every
information quantity is a difference of held-out log-losses in bits per transition, leave-one-day-out.

Names follow Krakauer et al. 2020 (published version; literature/krakauer-2020-information-theory-of-individuality.md):
  A*   organismal individuality   I(S';S)     = L(S')   - L(S'|S)
  A    colonial individuality     I(S';S|E)   = L(S'|E) - L(S'|S,E)
  nC   environmental determination I(S';E|S)  = L(S'|S) - L(S'|S,E)
  NTIC environmental coding       A* - A
H58 swapped the first two names: H58 "colonial" = A*, H58 "organismal" = A, H58 "environmental" = nC
(`H58_NAME_MAP`). The H58 tests ran on the right quantities; only the words were swapped.

Estimators (all vectorized; no Python loop over bins):
  dirichlet_loss(tgt, day, K, ctx=None, nctx=1, back=None, nback=1, alpha, beta)
      Discrete target, discrete context. Dirichlet(alpha) table on `back` (or the marginal), then an interpolated
      table on `ctx` with weight beta toward it. Leave-one-day-out by the total-minus-day trick: one count table per
      day (np.bincount on integer-encoded symbols), the held-out table is total minus the row's own day.
  krakauer_discrete(xn, xc, e, day, Kx, Ke)       L0, Lx, Le, Lxe and A*, A, nC, NTIC (count tables).
  logit_loss(y, X, day, C, lam)                   Ridge multinomial logistic regression, refit per held-out day with
                                                  a warm start from the full fit (L-BFGS). For additive environments
                                                  whose joint table is not identifiable (e.g. 216 E cells).
  krakauer_logit(yn, Sc, E, day, C, lam)          the four losses with one-hot S and E design blocks.
  delta_integration(yn, Sc, parts, E, day, C)     Delta = L(S'|parts, E) - L(S'|S, E) (parts: the components fitted
                                                  additively, e.g. members' own states or elements' prevalences).
  gauss_loss(y, X, day, ridge)                    1-d Gaussian (ridge OLS) held-out density loss in bits; per-day XtX,
                                                  Xty, yy sums, total minus day, batched solves. krakauer_gauss.
  encode(cols, sizes)                             joint integer symbol for several discrete columns.
  transitions(day_of_bin, valid)                  within-day (b, b+1) pairs.
Nulls:
  besag_clifford(obs, draw, h=10, n_max=300)      sequential Monte Carlo p-value (Besag & Clifford 1991): stop at h
                                                  exceedances or n_max draws; returns p, z, mu, sd, n.
  NullBank                                        cache of null draws keyed by (window, channel, bin, size, band ...),
                                                  extended lazily and reused across candidates of the same key.
  rotate_within_day(X, day_of_bin, rng)           independent circular shift of every row within each day (gathered
                                                  index arithmetic).
Search:
  boundary_expand(seed, candidates, score, max_size=8)
      Krakauer's boundary rule, greedy: among candidate additions that lower nC, add the one with the largest A;
      stop when no addition lowers nC (or at max_size). `score(members)` returns a dict with "A" and "nC".
Reference port (verification only):
  h58_unit_losses(x, y, day_of_bin)               H58's stay/popularity estimator with the correct names.

Run `uv run python infra/shared/individuality.py --verify`.
"""
from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

ALPHA = 0.5
BETA = 2.0
LN2 = math.log(2.0)
H58_NAME_MAP = {"colonial": "A_star", "organismal": "A", "environmental": "nC"}


# ============================================================================ helpers
def encode(cols, sizes) -> tuple[np.ndarray, int]:
    """Joint integer symbol of several discrete columns (each in 0..size-1). Returns (codes, total size)."""
    code = np.zeros(len(np.asarray(cols[0])), np.int64)
    K = 1
    for c, s in zip(cols, sizes):
        c = np.asarray(c, np.int64)
        if len(c) and (c.min() < 0 or c.max() >= s):
            raise ValueError("encode: symbol out of range")
        code = code * int(s) + c
        K *= int(s)
    return code, K


def transitions(day_of_bin: np.ndarray, valid: np.ndarray | None = None) -> np.ndarray:
    """Indices b0 with (b0, b0+1) on the same day (and both valid)."""
    d = np.asarray(day_of_bin)
    b0 = np.arange(len(d) - 1)
    ok = d[b0] == d[b0 + 1]
    if valid is not None:
        v = np.asarray(valid, bool)
        ok &= v[b0] & v[b0 + 1]
    return b0[ok]


def _day_index(day) -> tuple[np.ndarray, int]:
    u, di = np.unique(np.asarray(day), return_inverse=True)
    return di.astype(np.int64), len(u)


# ============================================================================ discrete (count tables)
def _heldout_counts(flat: np.ndarray, di: np.ndarray, nD: int, size: int) -> tuple[np.ndarray, np.ndarray]:
    """For each row: (total count of its cell) - (its own day's count of that cell). Returns (n_cell_heldout, total).
    Day tables are flattened (day * size + cell) and counted with one bincount."""
    tot = np.bincount(flat, minlength=size)
    if nD * size <= 50_000_000:
        dc = np.bincount(di * size + flat, minlength=nD * size)
        own = dc[di * size + flat]
    else:  # sparse fallback: unique (day, cell) pairs
        key = di * size + flat
        u, inv, cnt = np.unique(key, return_inverse=True, return_counts=True)
        own = cnt[inv]
    return tot[flat] - own, tot


def dirichlet_loss(tgt, day, K, ctx=None, nctx=1, back=None, nback=1, alpha=ALPHA, beta=BETA) -> np.ndarray:
    """Held-out (leave-one-day-out) -log2 p(tgt | ctx) per row.

    Without ctx: Dirichlet(alpha) marginal. With ctx and no back: Dirichlet(alpha) table per ctx cell (H58 style).
    With ctx and back (a coarser context, e.g. S alone when ctx = (S, E)): p_back = Dirichlet(alpha) table on back;
    p = (n(ctx, tgt) + beta * p_back) / (n(ctx) + beta) (interpolated backoff)."""
    tgt = np.asarray(tgt, np.int64)
    di, nD = _day_index(day)
    if ctx is None:
        n_cell, _ = _heldout_counts(tgt, di, nD, K)
        n_all = len(tgt) - np.bincount(di, minlength=nD)[di]
        p = (n_cell + alpha) / (n_all + alpha * K)
        return -np.log2(p)
    ctx = np.asarray(ctx, np.int64)
    if back is None:
        n_cell, _ = _heldout_counts(ctx * K + tgt, di, nD, nctx * K)
        n_ctx, _ = _heldout_counts(ctx, di, nD, nctx)
        p = (n_cell + alpha) / (n_ctx + alpha * K)
        return -np.log2(p)
    back = np.asarray(back, np.int64)
    pb = 2.0 ** (-dirichlet_loss(tgt, day, K, ctx=back, nctx=nback, alpha=alpha))
    n_cell, _ = _heldout_counts(ctx * K + tgt, di, nD, nctx * K)
    n_ctx, _ = _heldout_counts(ctx, di, nD, nctx)
    p = (n_cell + beta * pb) / (n_ctx + beta)
    return -np.log2(p)


def krakauer_discrete(xn, xc, e, day, Kx, Ke, alpha=ALPHA, beta=BETA) -> dict:
    """Count-table Krakauer decomposition. xn: next state, xc: current state (0..Kx-1), e: environment (0..Ke-1).
    L(S'|S,E) backs off to L(S'|S); L(S'|E) backs off to the marginal through its Dirichlet prior."""
    xn = np.asarray(xn, np.int64)
    if len(xn) < 10 or len(np.unique(day)) < 2:
        return {"ok": False}
    L0 = dirichlet_loss(xn, day, Kx, alpha=alpha)
    Lx = dirichlet_loss(xn, day, Kx, ctx=xc, nctx=Kx, alpha=alpha)
    Le = dirichlet_loss(xn, day, Kx, ctx=e, nctx=Ke, alpha=alpha)
    xe = np.asarray(xc, np.int64) * Ke + np.asarray(e, np.int64)
    Lxe = dirichlet_loss(xn, day, Kx, ctx=xe, nctx=Kx * Ke, back=xc, nback=Kx, alpha=alpha, beta=beta)
    return _decomp(L0, Lx, Le, Lxe)


def _decomp(L0, Lx, Le, Lxe) -> dict:
    H, mx, me, mxe = float(L0.mean()), float(Lx.mean()), float(Le.mean()), float(Lxe.mean())
    return {"ok": True, "n": int(len(L0)), "H": H, "L_S": mx, "L_E": me, "L_SE": mxe,
            "A_star": H - mx, "A": me - mxe, "nC": mx - mxe, "NTIC": (H - mx) - (me - mxe),
            "I_SE": H - mxe, "loss": {"L0": L0, "Lx": Lx, "Le": Le, "Lxe": Lxe}}


# ============================================================================ multinomial logistic (ridge)
def _softmax_nll(w, X, Y1, C, pen):
    p = X.shape[1]
    W = w.reshape(p, C)
    Z = X @ W
    Z -= Z.max(1, keepdims=True)
    lse = np.log(np.exp(Z).sum(1))
    logp = Z - lse[:, None]
    f = -(logp * Y1).sum() + 0.5 * float((pen[:, None] * W * W).sum())
    P = np.exp(logp)
    g = X.T @ (P - Y1) + pen[:, None] * W
    return f, g.ravel()


def _fit_logit(X, Y1, C, pen, w0=None, maxiter=200):
    from scipy.optimize import minimize
    p = X.shape[1]
    w0 = np.zeros(p * C) if w0 is None else w0
    r = minimize(_softmax_nll, w0, args=(X, Y1, C, pen), jac=True, method="L-BFGS-B",
                 options={"maxiter": maxiter, "gtol": 1e-6})
    return r.x


def logit_loss(y, X, day, C, lam=1.0, lam0=0.01, maxiter=200) -> np.ndarray:
    """Held-out -log2 p(y | x) per row from a ridge multinomial logit refit without each row's day (warm start from
    the full fit). X must contain an intercept column first (penalty lam0 on it, lam on the rest)."""
    y = np.asarray(y, np.int64)
    X = np.asarray(X, float)
    di, nD = _day_index(day)
    Y1 = np.zeros((len(y), C))
    Y1[np.arange(len(y)), y] = 1.0
    pen = np.full(X.shape[1], float(lam))
    pen[0] = lam0
    wf = _fit_logit(X, Y1, C, pen, maxiter=maxiter)
    out = np.empty(len(y))
    for d in range(nD):
        te = di == d
        if not te.any():
            continue
        tr = ~te
        w = _fit_logit(X[tr], Y1[tr], C, pen, w0=wf, maxiter=maxiter)
        Z = X[te] @ w.reshape(X.shape[1], C)
        Z -= Z.max(1, keepdims=True)
        logp = Z - np.log(np.exp(Z).sum(1))[:, None]
        out[te] = -logp[np.arange(te.sum()), y[te]] / LN2
    return out


def onehot(x, K, drop_first=True) -> np.ndarray:
    x = np.asarray(x, np.int64)
    M = np.zeros((len(x), K))
    M[np.arange(len(x)), x] = 1.0
    return M[:, 1:] if drop_first else M


def _design(*blocks, n):
    cols = [np.ones((n, 1))] + [b for b in blocks if b is not None and b.size]
    return np.hstack(cols)


def compact_states(*arrs) -> tuple[list, int]:
    """Relabel the union of observed symbols to 0..C-1 (so unused symbols do not enter the softmax)."""
    u = np.unique(np.concatenate([np.asarray(a, np.int64) for a in arrs]))
    lut = {int(v): i for i, v in enumerate(u)}
    return [np.array([lut[int(v)] for v in a], np.int64) for a in arrs], len(u)


def krakauer_logit(yn, Sc, E, day, C, lam=1.0) -> dict:
    """Krakauer decomposition with logistic models. yn: next state (0..C-1); Sc: design block of the current state
    (e.g. onehot(xc, Kx)); E: design block of the environment (one-hot blocks, additive). Returns A*, A, nC, NTIC."""
    n = len(yn)
    if n < 10 or len(np.unique(day)) < 2:
        return {"ok": False}
    L0 = logit_loss(yn, _design(n=n), day, C, lam)
    Lx = logit_loss(yn, _design(Sc, n=n), day, C, lam)
    Le = logit_loss(yn, _design(E, n=n), day, C, lam)
    Lxe = logit_loss(yn, _design(Sc, E, n=n), day, C, lam)
    return _decomp(L0, Lx, Le, Lxe)


def delta_integration(yn, Sc, parts, E, day, C, lam=1.0, L_SE=None) -> dict:
    """Integration Delta = L(S'|parts, E) - L(S'|S, E): what the joint state adds beyond its parts fitted additively.
    Pass L_SE (per-row losses of the S, E model) to reuse a fit."""
    n = len(yn)
    Lp = logit_loss(yn, _design(parts, E, n=n), day, C, lam)
    Lse = logit_loss(yn, _design(Sc, E, n=n), day, C, lam) if L_SE is None else L_SE
    return {"Delta": float(Lp.mean() - Lse.mean()), "L_parts_E": float(Lp.mean()), "L_SE": float(Lse.mean()),
            "loss_parts": Lp}


# ============================================================================ 1-d Gaussian
def gauss_loss(y, X, day, ridge=1e-3) -> np.ndarray:
    """Held-out Gaussian density loss -log2 N(y; x'b, s2) per row (bits; a density, so only differences matter).
    Per-day sums XtX, Xty, yy; the held-out fit is total minus day; s2 from the training residuals."""
    y = np.asarray(y, float)
    X = np.asarray(X, float)
    di, nD = _day_index(day)
    p = X.shape[1]
    XtX = np.zeros((nD, p, p))
    np.add.at(XtX, di, X[:, :, None] * X[:, None, :])
    Xty = np.zeros((nD, p))
    np.add.at(Xty, di, X * y[:, None])
    yy = np.bincount(di, weights=y * y, minlength=nD)
    nn = np.bincount(di, minlength=nD).astype(float)
    tXX, tXy, tyy, tn = XtX.sum(0), Xty.sum(0), yy.sum(), nn.sum()
    A = tXX[None] - XtX + ridge * np.eye(p)[None]
    bvec = tXy[None] - Xty
    beta = np.linalg.solve(A, bvec[..., None])[..., 0]
    # training RSS = yy - 2 b'Xty + b'XtX b (on the training part)
    rss = (tyy - yy) - 2 * np.einsum("dp,dp->d", beta, bvec) + np.einsum("dp,dpq,dq->d", beta, tXX[None] - XtX, beta)
    ntr = tn - nn
    s2 = np.maximum(rss / np.maximum(ntr - p, 1), 1e-12)
    mu = np.einsum("np,np->n", X, beta[di])
    s2r = s2[di]
    return (0.5 * np.log(2 * np.pi * s2r) + 0.5 * (y - mu) ** 2 / s2r) / LN2


def krakauer_gauss(yn, yc, E, day, ridge=1e-3) -> dict:
    """1-d Gaussian Krakauer decomposition: yn next value, yc current value, E environment design block."""
    n = len(yn)
    yc = np.asarray(yc, float).reshape(n, -1)
    L0 = gauss_loss(yn, _design(n=n), day, ridge)
    Lx = gauss_loss(yn, _design(yc, n=n), day, ridge)
    Le = gauss_loss(yn, _design(E, n=n), day, ridge)
    Lxe = gauss_loss(yn, _design(yc, E, n=n), day, ridge)
    return _decomp(L0, Lx, Le, Lxe)


# ============================================================================ nulls
def besag_clifford(obs: float, draw, h: int = 10, n_max: int = 300, side: str = "greater", min_draws: int = 0) -> dict:
    """Sequential Monte Carlo test (Besag & Clifford 1991). draw() returns one null statistic (or nan to skip).
    Stops when h null values reach obs (>= for 'greater', <= for 'less') or after n_max valid draws.
    p = h / n at an early stop, else (1 + #exceed) / (n + 1). z uses the drawn null mean and sd (descriptive when the
    run stopped early). min_draws forces at least that many draws (for a stable z)."""
    vals = []
    k = 0
    tries = 0
    while len(vals) < n_max and tries < 5 * n_max:
        tries += 1
        v = draw()
        if v is None or not np.isfinite(v):
            continue
        vals.append(float(v))
        if (v >= obs) if side == "greater" else (v <= obs):
            k += 1
        if k >= h and len(vals) >= min_draws:
            break
    v = np.asarray(vals)
    n = len(v)
    if n == 0 or not np.isfinite(obs):
        return {"p": np.nan, "z": np.nan, "mu": np.nan, "sd": np.nan, "n": n, "k": k, "stopped": False, "null": v}
    stopped = k >= h and n < n_max
    p = k / n if stopped else (1 + k) / (n + 1)
    mu, sd = float(v.mean()), float(v.std(ddof=1)) if n > 1 else np.nan
    z = (obs - mu) / sd if (sd and np.isfinite(sd) and sd > 1e-12) else np.nan
    return {"p": float(p), "z": float(z) if np.isfinite(z) else np.nan, "mu": mu, "sd": sd, "n": n, "k": k,
            "stopped": bool(stopped), "null": v}


@dataclass
class NullBank:
    """Cache of null statistics keyed by any hashable key; draws are extended lazily and reused across candidates."""
    store: dict = field(default_factory=dict)

    def get(self, key, draw, n: int) -> np.ndarray:
        cur = self.store.setdefault(key, [])
        while len(cur) < n:
            v = draw()
            if v is not None and np.isfinite(v):
                cur.append(float(v))
        return np.asarray(cur[:n])

    def test(self, key, obs: float, draw, h: int = 10, n_max: int = 300, side: str = "greater") -> dict:
        """Besag-Clifford against the cached draws for key (extends the cache as needed)."""
        cur = self.store.setdefault(key, [])
        i = 0

        def nxt():
            nonlocal i
            if i < len(cur):
                v = cur[i]
            else:
                v = draw()
                if v is not None and np.isfinite(v):
                    cur.append(float(v))
                else:
                    return v
            i += 1
            return v
        return besag_clifford(obs, nxt, h=h, n_max=n_max, side=side)


def rotate_within_day(X: np.ndarray, day_of_bin: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Every row of X (rows x bins) circularly shifted by its own random offset within each day (gathered index)."""
    X = np.asarray(X)
    d = np.asarray(day_of_bin)
    n, B = X.shape
    starts = np.flatnonzero(np.r_[True, d[1:] != d[:-1]])
    ends = np.r_[starts[1:], B]
    lens = ends - starts
    idx = np.empty((n, B), np.int64)
    for s, L in zip(starts, lens):
        off = rng.integers(0, L, size=n)
        j = np.arange(L)[None, :]
        idx[:, s:s + L] = s + (j + off[:, None]) % L
    return np.take_along_axis(X, idx, axis=1)


# ============================================================================ boundary expansion
def boundary_expand(seed, candidates, score, max_size: int = 8, tol: float = 0.0) -> dict:
    """Krakauer's boundary rule, greedy. score(members) -> {"A": float, "nC": float}. Start from seed; at each step
    evaluate every candidate addition, keep those that lower nC by more than tol (held-out estimates are noisy, so a
    tol > 0 stops estimator-variance growth), add the one with the largest A; stop when none qualifies or the size
    reaches max_size. Returns members, the path and the per-step scores."""
    members = list(seed)
    cur = score(members)
    path = [{"members": list(members), **{k: cur[k] for k in ("A", "nC")}}]
    pool = [c for c in candidates if c not in members]
    while len(members) < max_size and pool:
        best = None
        for c in pool:
            s = score(members + [c])
            if not (np.isfinite(s["nC"]) and np.isfinite(s["A"])):
                continue
            if s["nC"] < cur["nC"] - tol and (best is None or s["A"] > best[1]["A"]):
                best = (c, s)
        if best is None:
            break
        members.append(best[0])
        pool.remove(best[0])
        cur = best[1]
        path.append({"members": list(members), "A": cur["A"], "nC": cur["nC"]})
    return {"members": members, "path": path, "final": cur}


# ============================================================================ H58 reference port
def h58_unit_losses(x: np.ndarray, y: np.ndarray, day_of_bin: np.ndarray, alpha: float = 0.5) -> dict:
    """Port of h58lib.krakauer (unit state x in -1..K-1, environment y in 0..7) returning the correct names."""
    nB = len(x)
    b0 = np.arange(nB - 1)
    b0 = b0[day_of_bin[b0] == day_of_bin[b0 + 1]]
    if len(b0) < 10:
        return {"ok": False}
    xn, xc, yc = x[b0 + 1], x[b0], y[b0]
    dd = day_of_bin[b0 + 1]
    days = np.unique(dd)
    if len(days) < 2:
        return {"ok": False}
    K = int(max(x.max(), 0)) + 1
    sym = xn + 1
    work_n = xn >= 0
    stay = (xc >= 0) & (xn == xc)
    ec = (xc >= 0).astype(int)
    di = np.searchsorted(days, dd)
    nDd = len(days)
    Pm = np.zeros((nDd, K + 1)); np.add.at(Pm, (di, sym), 1)
    Pw = np.zeros((nDd, K)); np.add.at(Pw, (di[work_n], xn[work_n]), 1)
    Z_x = np.zeros((nDd, 2, 2)); np.add.at(Z_x, (di, ec, work_n.astype(int)), 1)
    Z_y = np.zeros((nDd, 8, 2)); np.add.at(Z_y, (di, yc, work_n.astype(int)), 1)
    Z_xy = np.zeros((nDd, 2, 8, 2)); np.add.at(Z_xy, (di, ec, yc, work_n.astype(int)), 1)
    m_st = work_n & (xc >= 0)
    S_x = np.zeros((nDd, 2)); np.add.at(S_x, (di[m_st], (~stay[m_st]).astype(int)), 1)
    S_xy = np.zeros((nDd, 8, 2)); np.add.at(S_xy, (di[m_st], yc[m_st], (~stay[m_st]).astype(int)), 1)

    def tr(A):
        return A.sum(0)[None] - A
    Pm_t, Pw_t, Zx_t, Zy_t, Zxy_t, Sx_t, Sxy_t = map(tr, (Pm, Pw, Z_x, Z_y, Z_xy, S_x, S_xy))
    pim = (Pm_t + alpha) / (Pm_t + alpha).sum(1, keepdims=True)
    piw = (Pw_t + alpha) / (Pw_t + alpha).sum(1, keepdims=True)

    def p_work(Z):
        return (Z[..., 1] + alpha) / (Z.sum(-1) + 2 * alpha)
    xi = np.maximum(xn, 0)
    xci = np.maximum(xc, 0)
    L0 = -np.log2(pim[di, sym])
    pw_pop = piw[di, xi]
    ws_x = (Sx_t[di, 0] + alpha) / (Sx_t[di].sum(1) + 2 * alpha)
    ws_xy = (Sxy_t[di, yc, 0] + alpha) / (Sxy_t[di, yc].sum(1) + 2 * alpha)
    pil = piw[di, xci]

    def which(ws):
        return np.where(xc >= 0, np.where(stay, ws, (1 - ws) * pw_pop / np.maximum(1 - pil, 1e-12)), pw_pop)

    def ll(pwork, pwhich):
        return -np.log2(np.clip(np.where(work_n, pwork * pwhich, 1 - pwork), 1e-12, 1))
    L_x = ll(p_work(Zx_t[di, ec]), which(ws_x))
    L_y = ll(p_work(Zy_t[di, yc]), pw_pop)
    L_xy = ll(p_work(Zxy_t[di, ec, yc]), which(ws_xy))
    out = _decomp(L0, L_x, L_y, L_xy)
    out["h58_names"] = {"colonial": out["A_star"], "organismal": out["A"], "environmental": out["nC"]}
    return out


# ============================================================================ verify
def _brute_dirichlet(tgt, day, K, ctx, nctx, alpha):
    out = np.empty(len(tgt))
    for d in np.unique(day):
        tr, te = day != d, day == d
        T = np.zeros((nctx, K))
        np.add.at(T, (ctx[tr], tgt[tr]), 1)
        P = (T + alpha) / (T.sum(1, keepdims=True) + alpha * K)
        out[te] = -np.log2(P[ctx[te], tgt[te]])
    return out


def _markov_mi(P, pi):
    """I(S';S) in bits of a stationary chain with transition matrix P and stationary pi."""
    joint = pi[:, None] * P
    pn = joint.sum(0)
    m = joint > 0
    return float((joint[m] * np.log2(joint[m] / (pi[:, None] * pn[None, :])[m])).sum())


def verify() -> bool:
    rng = np.random.default_rng(20261009)
    ok = True

    def check(name, cond, detail=""):
        nonlocal ok
        print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")
        ok &= bool(cond)

    # 1. total-minus-day Dirichlet == brute-force refit per day
    n, K, nctx = 3000, 5, 7
    day = rng.integers(0, 30, n)
    ctx = rng.integers(0, nctx, n)
    tgt = (ctx + rng.integers(0, 3, n)) % K
    a = dirichlet_loss(tgt, day, K, ctx=ctx, nctx=nctx)
    b = _brute_dirichlet(tgt, day, K, ctx, nctx, ALPHA)
    check("dirichlet_loss == brute-force leave-one-day-out", np.allclose(a, b, atol=1e-10), f"max|d|={np.abs(a-b).max():.2e}")
    a0 = dirichlet_loss(tgt, day, K)
    b0 = _brute_dirichlet(tgt, day, K, np.zeros(n, np.int64), 1, ALPHA)
    check("marginal dirichlet == brute force", np.allclose(a0, b0, atol=1e-10))

    # 2. known-MI Markov chain with a random environment: A* ~ I(S';S), A ~ A*, nC ~ 0
    Kx = 4
    P = np.full((Kx, Kx), 0.1)
    np.fill_diagonal(P, 0.7)
    P /= P.sum(1, keepdims=True)
    pi = np.full(Kx, 1 / Kx)
    T = 40000
    x = np.empty(T, np.int64)
    x[0] = 0
    u = rng.random(T)
    cP = P.cumsum(1)
    for t in range(1, T):
        x[t] = np.searchsorted(cP[x[t - 1]], u[t])
    dob = np.repeat(np.arange(T // 50), 50)
    e = rng.integers(0, 3, T)
    b0i = transitions(dob)
    kd = krakauer_discrete(x[b0i + 1], x[b0i], e[b0i], dob[b0i + 1], Kx, 3)
    true = _markov_mi(P, pi)
    check("A* recovers I(S';S) of a known chain", abs(kd["A_star"] - true) < 0.02, f"A*={kd['A_star']:.4f} true={true:.4f}")
    check("A ~ A* and nC ~ 0 when E is independent noise", abs(kd["A"] - kd["A_star"]) < 0.02 and abs(kd["nC"]) < 0.01,
          f"A={kd['A']:.4f} nC={kd['nC']:.4f}")
    # 3. environment-driven chain: S' copies E, S irrelevant -> A ~ 0, nC large, A* ~ 0
    e2 = rng.integers(0, Kx, T)
    x2 = np.r_[0, e2[:-1]]
    x2 = np.where(rng.random(T) < 0.8, x2, rng.integers(0, Kx, T))
    kd2 = krakauer_discrete(x2[b0i + 1], x2[b0i], e2[b0i], dob[b0i + 1], Kx, Kx)
    check("E-driven chain: A ~ 0, nC > 0.5 bit", abs(kd2["A"]) < 0.02 and kd2["nC"] > 0.5, f"A={kd2['A']:.4f} nC={kd2['nC']:.3f}")

    # 4. logistic held-out loss == brute-force refit (scipy, cold start) per day
    n = 400
    day = rng.integers(0, 12, n)
    X = np.c_[np.ones(n), rng.normal(size=(n, 3))]
    C = 3
    W = rng.normal(size=(4, C))
    Pz = np.exp(X @ W)
    Pz /= Pz.sum(1, keepdims=True)
    y = np.array([rng.choice(C, p=pp) for pp in Pz])
    a = logit_loss(y, X, day, C, lam=1.0)
    bb = np.empty(n)
    Y1 = np.eye(C)[y]
    pen = np.r_[0.01, np.ones(3)]
    for d in np.unique(day):
        tr, te = day != d, day == d
        w = _fit_logit(X[tr], Y1[tr], C, pen, maxiter=2000).reshape(4, C)
        Z = X[te] @ w
        Z -= Z.max(1, keepdims=True)
        lp = Z - np.log(np.exp(Z).sum(1))[:, None]
        bb[te] = -lp[np.arange(te.sum()), y[te]] / LN2
    check("logit_loss (warm start) == cold-start refit per day", np.abs(a - bb).max() < 1e-3, f"max|d|={np.abs(a-bb).max():.2e}")
    # logistic Krakauer on the known chain (smaller T) agrees with the count estimator
    T2 = 6000
    b0s = transitions(dob[:T2])
    kl = krakauer_logit(x[b0s + 1], onehot(x[b0s], Kx), onehot(e[b0s], 3), dob[b0s + 1], Kx, lam=0.1)
    check("krakauer_logit A* ~ true I(S';S)", abs(kl["A_star"] - true) < 0.05, f"A*={kl['A_star']:.4f} true={true:.4f}")

    # 5. Gaussian held-out loss == explicit per-day OLS
    n = 600
    day = rng.integers(0, 15, n)
    X = np.c_[np.ones(n), rng.normal(size=(n, 2))]
    yv = X @ np.array([0.5, 1.0, -0.5]) + rng.normal(size=n)
    a = gauss_loss(yv, X, day, ridge=0.0)
    bb = np.empty(n)
    for d in np.unique(day):
        tr, te = day != d, day == d
        beta = np.linalg.lstsq(X[tr], yv[tr], rcond=None)[0]
        res = yv[tr] - X[tr] @ beta
        s2 = (res ** 2).sum() / (tr.sum() - 3)
        bb[te] = (0.5 * np.log(2 * np.pi * s2) + 0.5 * (yv[te] - X[te] @ beta) ** 2 / s2) / LN2
    check("gauss_loss == explicit per-day OLS", np.allclose(a, bb, atol=1e-8), f"max|d|={np.abs(a-bb).max():.2e}")
    # Gaussian AR(1): A* ~ -0.5 log2(1-phi^2)
    phi, T3 = 0.6, 20000
    z = np.zeros(T3)
    for t in range(1, T3):
        z[t] = phi * z[t - 1] + rng.normal()
    dob3 = np.repeat(np.arange(T3 // 100), 100)
    b3 = transitions(dob3)
    kg = krakauer_gauss(z[b3 + 1], z[b3], rng.normal(size=(len(b3), 1)), dob3[b3 + 1])
    tg = -0.5 * np.log2(1 - phi ** 2)
    check("krakauer_gauss A* ~ -0.5 log2(1-phi^2)", abs(kg["A_star"] - tg) < 0.02, f"A*={kg['A_star']:.4f} true={tg:.4f}")

    # 6. H58 port == h58lib.krakauer (read-only import inside verify) on synthetic units
    try:
        root = Path(__file__).resolve().parents[2]
        sys.path.insert(0, str(root / "hypotheses/H58-coordinated-superagents/analysis"))
        import h58lib  # noqa: E402
        good = True
        for rep in range(5):
            nB, nA = 600, 4
            dob6 = np.repeat(np.arange(nB // 20), 20)
            S = np.where(rng.random((nA, nB)) < 0.4, rng.integers(0, 3, (nA, nB)), -1)
            U = h58lib.Unit(name="v", regime="III", agents=list(range(nA)), repos=[0, 1, 2], day_of_bin=dob6, S=S,
                            N=(S >= 0).astype(int), yh=rng.random(nB) < 0.1)
            xs = h58lib.unit_state(U, [0, 1, 2], np.array([0, 1, 2]))
            ys = h58lib.env_state(U, [0, 1, 2], np.array([0, 1, 2]))
            ref = h58lib.krakauer(U, xs, ys)
            mine = h58_unit_losses(xs, ys, dob6)
            good &= ref["ok"] and all(abs(ref[k] - mine[H58_NAME_MAP[k]]) < 1e-12 for k in H58_NAME_MAP)
        check("h58_unit_losses == h58lib.krakauer with names mapped (colonial->A*, organismal->A)", good)
    except Exception as ex:  # pragma: no cover
        check("h58lib reference import", False, repr(ex))

    # 7. Besag-Clifford: stops at h exceedances under the null; p roughly uniform
    ps, ns = [], []
    for r in range(300):
        obs = rng.normal()
        res = besag_clifford(obs, lambda: rng.normal(), h=10, n_max=300)
        ps.append(res["p"])
        ns.append(res["n"])
    ps = np.asarray(ps)
    check("Besag-Clifford size at 0.05 under the null", abs((ps <= 0.05).mean() - 0.05) < 0.035,
          f"rate={(ps <= 0.05).mean():.3f}, median draws={np.median(ns):.0f}")
    res = besag_clifford(5.0, lambda: rng.normal(), h=10, n_max=300)
    check("Besag-Clifford runs to n_max for an extreme statistic", res["n"] == 300 and res["p"] < 0.01)
    bank = NullBank()
    v1 = bank.get(("w", 3), lambda: rng.normal(), 50)
    v2 = bank.get(("w", 3), lambda: rng.normal(), 50)
    check("NullBank reuses cached draws", np.array_equal(v1, v2))

    # 8. rotation keeps each row's per-day multiset
    Xr = rng.integers(0, 5, (6, 40))
    dr = np.repeat(np.arange(4), 10)
    R = rotate_within_day(Xr, dr, rng)
    same = all(np.array_equal(np.sort(Xr[i, dr == d]), np.sort(R[i, dr == d])) for i in range(6) for d in range(4))
    check("rotate_within_day keeps per-row per-day multisets", same and not np.array_equal(R, Xr))

    # 9. boundary expansion logic on a known score surface: nC falls by 0.3 per planted member added and rises by
    # 0.01 per outsider; A rises with planted members. The rule must add exactly the planted set and stop.
    planted = {2, 5, 7}

    def score(m):
        ms = set(m)
        return {"A": float(len(ms & planted)) + 0.001 * len(ms), "nC": 0.3 * len(planted - ms) + 0.01 * len(ms - planted)}
    be = boundary_expand([2], list(range(10)), score, max_size=8)
    check("boundary_expand adds the planted set and stops", set(be["members"]) == planted, f"members={be['members']}")
    be2 = boundary_expand([2], list(range(10)), score, max_size=2)
    check("boundary_expand respects max_size", len(be2["members"]) == 2)
    print("verify:", "OK" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    if "--verify" in sys.argv:
        sys.exit(0 if verify() else 1)
    print(__doc__)
