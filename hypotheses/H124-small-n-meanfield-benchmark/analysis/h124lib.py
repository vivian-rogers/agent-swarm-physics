"""H124 library: kinetic Ising exact ML and the mean-field inversions (nMF, TAP, MS), model EP sigma_J, errors,
designs for the per-call clock and the 1-min parallel grid, and a per-call simulator. No data read at import.

Convention: spins +-1; P(s_i' = +1 | s) = 1 / (1 + exp(-2 (h_i + sum_j J_ij s_j))), own previous spin included
(J_ii = self-coupling).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data/processed/H124-small-n-meanfield-benchmark"
METHODS = ("nMF", "TAP", "MS", "nMF|s", "TAP|s", "MS|s")   # "|s": stratified on the own previous spin (A1)
GH_X, GH_W = np.polynomial.hermite_e.hermegauss(80)
GH_W = GH_W / GH_W.sum()


# ============================================================================ designs
def percall_rows(unit: str):
    """{i: (X n x N, y n, days n)} from percall/<unit>.parquet."""
    return rows_from_frame(pl.read_parquet(OUT / "percall" / f"{unit}.parquet"))


def rows_from_frame(P: pl.DataFrame):
    N = 4
    X = P.select([f"s{j}" for j in range(N)]).to_numpy().astype(np.float64)
    y = P["talk"].to_numpy().astype(np.float64)
    a = P["agent"].to_numpy()
    d = P["day"].to_numpy()
    return {i: (X[a == i], y[a == i], d[a == i]) for i in range(N)}, N


def grid_rows(unit: str, channel: str = "talk"):
    """Parallel grid: {i: (X = s(t), y = s_i(t+1), days)} from grid/<unit>.npz."""
    z = np.load(OUT / "grid" / f"{unit}.npz")
    return grid_rows_from_store({k: z[k] for k in z.files}, channel)


def grid_rows_from_store(z: dict, channel: str = "talk"):
    suf = "_talk" if channel == "talk" else "_act"
    Xs, Ys, Ds = [], [], []
    for k in sorted(z):
        if not k.endswith(suf):
            continue
        S = z[k].astype(np.float64)
        if len(S) < 3:
            continue
        Xs.append(S[:-1])
        Ys.append(S[1:])
        Ds.append(np.array([k.split("_")[0]] * (len(S) - 1)))
    if not Xs:
        return None, 4
    X, Y, D = np.vstack(Xs), np.vstack(Ys), np.concatenate(Ds)
    N = X.shape[1]
    return {i: (X, Y[:, i], D) for i in range(N)}, N


def subset_days(rows, keep):
    keep = set(keep)
    out = {}
    for i, (X, y, d) in rows.items():
        m = np.array([v in keep for v in d])
        out[i] = (X[m], y[m], d[m])
    return out


def boot_days(rows, rng):
    days = sorted(set(np.concatenate([d for _, _, d in rows.values()])))
    pick = rng.choice(days, len(days), replace=True)
    out = {}
    for i, (X, y, d) in rows.items():
        idx = np.concatenate([np.flatnonzero(d == p) for p in pick])
        out[i] = (X[idx], y[idx], d[idx])
    return out


# ============================================================================ estimators
def ml_row(X, y, l2=1e-4, iters=100):
    """Exact ML (logistic, Newton). Returns (h_i, J_i row) in the +-1 convention."""
    n, p = X.shape
    Z = np.hstack([np.ones((n, 1)), X])
    t = (y > 0).astype(float)
    w = np.zeros(p + 1)
    R = l2 * n * np.eye(p + 1)
    R[0, 0] = 0
    for _ in range(iters):
        mu = 1 / (1 + np.exp(-np.clip(Z @ w, -30, 30)))
        g = Z.T @ (t - mu) - R @ w
        H = (Z * (mu * (1 - mu))[:, None]).T @ Z + R
        st = np.linalg.solve(H, g)
        w += st
        if np.max(np.abs(st)) < 1e-9:
            break
    return w[0] / 2, w[1:] / 2


def row_stats(X, y):
    mp = y.mean()
    m = X.mean(0)
    C = np.cov(X, rowvar=False, bias=True)
    D = ((y - mp)[:, None] * (X - m)).mean(0)
    B = np.linalg.solve(C + 1e-9 * np.eye(len(m)), D)
    return mp, m, C, D, B


def nmf_row(mp, m, C, D, B):
    a = 1 - mp ** 2
    J = B / a
    return np.arctanh(np.clip(mp, -0.999999, 0.999999)) - J @ m, J, True


def tap_row(mp, m, C, D, B):
    """Kinetic TAP (Roudi & Hertz 2011): a = a0 x, x^3 - x^2 + S/a0 = 0, S = sum_j B_j^2 (1 - m_j^2)."""
    a0 = 1 - mp ** 2
    S = float((B ** 2 * (1 - m ** 2)).sum())
    c = S / a0
    if c > 4 / 27:
        return np.nan, np.full_like(B, np.nan), False
    roots = np.roots([1, -1, 0, c])
    x = max(r.real for r in roots if abs(r.imag) < 1e-9 and 0 < r.real <= 1 + 1e-12)
    a = a0 * x
    J = B / a
    h = np.arctanh(np.clip(mp, -0.999999, 0.999999)) - J @ m + mp * (J ** 2 * (1 - m ** 2)).sum()
    return h, J, True


def _gauss_mean(g, sd, f):
    return float((GH_W * f(g + sd * GH_X)).sum())


def ms_row(mp, m, C, D, B, iters=200):
    """Mezard-Sakellariou / Plefka[t]: Gaussian local field with variance Delta = J C J'."""
    V = float(B @ C @ B)
    a = 1 - mp ** 2
    g = np.arctanh(np.clip(mp, -0.999999, 0.999999))
    ok = False
    for _ in range(iters):
        sd = np.sqrt(max(V, 0)) / a
        lo, hi = -20.0, 20.0
        for _ in range(80):
            mid = (lo + hi) / 2
            if _gauss_mean(mid, sd, np.tanh) < mp:
                lo = mid
            else:
                hi = mid
        g = (lo + hi) / 2
        a_new = _gauss_mean(g, sd, lambda u: 1 - np.tanh(u) ** 2)
        if a_new <= 1e-6:
            break
        if abs(a_new - a) < 1e-10:
            a = a_new
            ok = True
            break
        a = 0.5 * a + 0.5 * a_new
    J = B / a
    return g - J @ m, J, ok


def strat_row(X, y, i, base):
    """Amendment A1 (2026-10-04, after the synthetic, before real data): invert the off-diagonal couplings within
    each stratum of the own previous spin s_i = +-1 (the local field minus the self term is then closer to the
    approximations' assumptions); J_ii = (h(+) - h(-))/2, h = (h(+) + h(-))/2, J_off = count-weighted mean."""
    N = X.shape[1]
    others = [j for j in range(N) if j != i]
    hs, Js, ns = {}, {}, {}
    for v in (1.0, -1.0):
        m = X[:, i] == v
        if m.sum() < 20 or y[m].min() == y[m].max():
            return np.nan, np.full(N, np.nan), False
        st = row_stats(X[m][:, others], y[m])
        hv, Jv, ok = base(*st)
        if not ok or np.isnan(Jv).any():
            return np.nan, np.full(N, np.nan), False
        hs[v], Js[v], ns[v] = hv, Jv, m.sum()
    J = np.zeros(N)
    J[others] = (ns[1.0] * Js[1.0] + ns[-1.0] * Js[-1.0]) / (ns[1.0] + ns[-1.0])
    J[i] = (hs[1.0] - hs[-1.0]) / 2
    return (hs[1.0] + hs[-1.0]) / 2, J, True


def fit_all(rows, N, methods=METHODS):
    """Returns {method: [h, J, D, ok_rows]} for ML and the approximations. D = per-row Cov(y_i, x)."""
    base = {"nMF": nmf_row, "TAP": tap_row, "MS": ms_row}
    res = {k: [np.zeros(N), np.zeros((N, N)), np.zeros((N, N)), 0] for k in ("ML",) + tuple(methods)}
    for i in range(N):
        X, y, _ = rows[i]
        if len(y) < 20 or y.min() == y.max():
            for k in res:
                res[k][1][i] = np.nan
            continue
        h, J = ml_row(X, y)
        st = row_stats(X, y)
        res["ML"][0][i], res["ML"][1][i], res["ML"][2][i] = h, J, st[3]
        res["ML"][3] += 1
        for k in methods:
            if k.endswith("|s"):
                hk, Jk, ok = strat_row(X, y, i, base[k[:-2]])
            else:
                hk, Jk, ok = base[k](*st)
            res[k][0][i], res[k][1][i], res[k][2][i] = hk, Jk, st[3]
            res[k][3] += int(ok)
    return res


def sigma_J(J, D):
    return float(np.nansum((J - J.T) * D))


def errors(res, ref="ML", J_true=None):
    """eps_J (off-diagonal, all) and eps_sigma vs the reference (ML or the true J), on the rows where both the
    reference and the method are defined; `cover` = share of reference rows on which the method is defined."""
    N = res["ML"][1].shape[0]
    Jr = res[ref][1] if J_true is None else J_true
    D = res["ML"][2]
    okr = ~np.isnan(res["ML"][1]).any(1) & ~np.isnan(Jr).any(1)
    out = {}
    for k in res:
        if k == ref and J_true is None:
            continue
        J = res[k][1]
        rows = okr & ~np.isnan(J).any(1)
        cover = float(rows.sum() / max(okr.sum(), 1))
        if rows.sum() == 0:
            out[k] = {"epsJ": np.nan, "epsJ_all": np.nan, "eps_sigma": np.nan, "sigma": np.nan, "cover": 0.0,
                      "shrink": np.nan, "ok_rows": res[k][3]}
            continue
        R = np.zeros((N, N), bool)
        R[rows] = True
        off = R & ~np.eye(N, dtype=bool)
        both = np.outer(rows, rows)          # sigma needs both (i,j) and (j,i)
        Jm = np.where(both, J, 0.0)
        Jrm = np.where(both, Jr, 0.0)
        sr = sigma_J(Jrm, np.where(both, D, 0.0))
        sk = sigma_J(Jm, np.where(both, D, 0.0))
        out[k] = {"epsJ": float(np.linalg.norm((J - Jr)[off]) / np.linalg.norm(Jr[off])),
                  "epsJ_all": float(np.linalg.norm((J - Jr)[R]) / np.linalg.norm(Jr[R])),
                  "eps_sigma": float(abs(sk - sr) / abs(sr)) if sr != 0 and both.sum() > N else np.nan,
                  "sigma": sk, "cover": cover, "ok_rows": res[k][3],
                  "shrink": float(np.sum(J[off] * Jr[off]) / np.sum(Jr[off] ** 2))}
    full = okr
    off = np.outer(full, full) & ~np.eye(N, dtype=bool)
    out["ref_sigma"] = sigma_J(np.where(np.outer(full, full), Jr, 0), np.where(np.outer(full, full), D, 0))
    out["ref_normJ_off"] = float(np.linalg.norm(Jr[off]))
    return out


def heldout_ll(rows, N, method):
    """Leave-one-day-out mean log-likelihood per row of each estimator's (h, J)."""
    days = sorted(set(np.concatenate([d for _, _, d in rows.values()])))
    tot, n = 0.0, 0
    for dd in days:
        tr = {i: (X[d != dd], y[d != dd], d[d != dd]) for i, (X, y, d) in rows.items()}
        te = {i: (X[d == dd], y[d == dd]) for i, (X, y, d) in rows.items()}
        r = fit_all(tr, N)[method]
        for i in range(N):
            X, y = te[i]
            if len(y) == 0 or np.isnan(r[1][i]).any():
                continue
            H = r[0][i] + X @ r[1][i]
            tot += float(np.sum(y * H - np.logaddexp(H, -H)))
            n += len(y)
    return tot / max(n, 1)


# ============================================================================ simulation (per-call clock)
def simulate_percall(actor_days, h, J, rng, R=1):
    """Asynchronous kinetic Ising on given actor sequences; R worlds in parallel share the schedule.
    Returns list over worlds of rows {i: (X, y, days)} (X = configuration just before i's call)."""
    N = len(h)
    Xs = [[[] for _ in range(N)] for _ in range(R)]
    ys = [[[] for _ in range(N)] for _ in range(R)]
    ds = [[[] for _ in range(N)] for _ in range(R)]
    p0 = 1 / (1 + np.exp(-2 * h))
    for day, a in actor_days:
        a = np.asarray(a)
        T = len(a)
        cur = np.where(rng.random((R, N)) < p0, 1.0, -1.0)
        U = rng.random((T, R))
        prev = np.empty((T, R, N), np.int8)
        newv = np.empty((T, R), np.int8)
        for t in range(T):
            i = a[t]
            prev[t] = cur
            Hh = h[i] + cur @ J[i]
            v = np.where(U[t] < 1 / (1 + np.exp(-2 * Hh)), 1.0, -1.0)
            cur[:, i] = v
            newv[t] = v
        burn = min(T // 10, 200)
        for i in range(N):
            ix = np.flatnonzero(a == i)
            ix = ix[ix >= burn]
            for r in range(R):
                Xs[r][i].append(prev[ix, r, :].astype(np.float64))
                ys[r][i].append(newv[ix, r].astype(np.float64))
                ds[r][i].append(np.array([day] * len(ix)))
    out = []
    for r in range(R):
        out.append({i: (np.vstack(Xs[r][i]), np.concatenate(ys[r][i]), np.concatenate(ds[r][i])) for i in range(N)})
    return out


def actor_days_from_percall(unit: str):
    P = pl.read_parquet(OUT / "percall" / f"{unit}.parquet").sort("day", "step")
    return [(d, g["agent"].to_numpy()) for (d,), g in P.group_by("day", maintain_order=True)]


def shift_null_rows(unit: str, rng):
    """Coupling-free null on the per-call clock: within each day, each agent's talk path (forward-filled over steps)
    is circularly shifted against the others; the updating agent's own previous spin is kept."""
    return shift_null_from_frame(pl.read_parquet(OUT / "percall" / f"{unit}.parquet"), rng)


def shift_null_from_frame(P: pl.DataFrame, rng):
    P = P.sort("day", "step")
    N = 4
    rows = {i: ([], [], []) for i in range(N)}
    for (d,), g in P.group_by("day", maintain_order=True):
        S = g.select([f"s{j}" for j in range(N)]).to_numpy().astype(np.float64)
        a = g["agent"].to_numpy()
        y = g["talk"].to_numpy().astype(np.float64)
        T = len(a)
        S2 = S.copy()
        for j in range(N):
            S2[:, j] = np.roll(S[:, j], rng.integers(T // 10, T - T // 10 + 1))
        for i in range(N):
            ix = a == i
            X = S2[ix].copy()
            X[:, i] = S[ix, i]
            rows[i][0].append(X)
            rows[i][1].append(y[ix])
            rows[i][2].append(np.array([d] * ix.sum()))
    return {i: (np.vstack(v[0]), np.concatenate(v[1]), np.concatenate(v[2])) for i, v in rows.items()}
