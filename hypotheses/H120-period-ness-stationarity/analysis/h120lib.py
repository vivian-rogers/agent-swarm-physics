"""H120 estimators: kinetic Ising (logistic Glauber) fits with weekday and session-length fields, per-day scores, the
permutation-calibrated drift score W for day contrasts (split, trend, boundaries), one-step weekly fits, and EP halves
with the corrected held-out Newton bound (infra/shared/ep_newton.py).

Grid input (scheme output): per window, a list of per-day spin arrays (T_d x N, uint8), weekdays, trimmed lengths.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
import ep_newton as EPN  # noqa: E402

DATA = ROOT / "data/processed/H120-period-ness-stationarity"
LAM_J = 1.0       # fixed ridge on J (card: fixed hyperparameters)
LAM_OTHER = 1e-4  # numerical floor on h, weekday, length


# ============================================================================ data
def load_window(name: str, channel: str) -> dict:
    z = np.load(DATA / "grids" / f"{name}.npz")
    days = z["days"].tolist()
    S = [z[f"{channel}_{i}"].astype(np.float64) for i in range(len(days))]
    return {"name": name, "channel": channel, "days": days, "core": z["core"].tolist(), "S": S,
            "weekday": z["weekday"].astype(int), "trim_len": z["trim_len"].astype(float)}


def design(win: dict, drop_first_day: bool = False):
    """Per-day design blocks: X_d (T_d-1 x p) and Y_d (T_d-1 x N). Columns: 1, s(t) (N), weekday dummies (present
    weekdays except the first), standardized session length (if it varies)."""
    S, wd, L = win["S"], win["weekday"], win["trim_len"]
    idx = list(range(len(S)))[1:] if drop_first_day else list(range(len(S)))
    wds = sorted(set(wd[idx].tolist()))
    wd_cols = wds[1:]
    Lz = (L - L[idx].mean()) / (L[idx].std() if L[idx].std() > 0 else 1.0)
    use_L = L[idx].std() > 0
    N = S[0].shape[1]
    Xs, Ys, keep = [], [], []
    for d in idx:
        s = S[d]
        T = len(s) - 1
        cols = [np.ones((T, 1)), s[:-1]]
        for w in wd_cols:
            cols.append(np.full((T, 1), 1.0 if wd[d] == w else 0.0))
        if use_L:
            cols.append(np.full((T, 1), Lz[d]))
        Xs.append(np.hstack(cols))
        Ys.append(s[1:])
        keep.append(d)
    p = Xs[0].shape[1]
    lam = np.full(p, LAM_OTHER)
    lam[1:1 + N] = LAM_J
    return {"X": Xs, "Y": Ys, "days": keep, "N": N, "p": p, "lam": lam, "drift_idx": np.arange(N + 1)}


# ============================================================================ fit
def _sig(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -30, 30)))


def fit_agent(Xs, ys, lam, iters=25, theta0=None):
    X = np.vstack(Xs)
    y = np.concatenate(ys)
    th = np.zeros(X.shape[1]) if theta0 is None else theta0.copy()
    for _ in range(iters):
        p = _sig(X @ th)
        g = X.T @ (y - p) - lam * th
        H = (X * (p * (1 - p))[:, None]).T @ X + np.diag(lam)
        step = np.linalg.solve(H, g)
        th += step
        if np.max(np.abs(step)) < 1e-7:
            break
    return th


def fit(des) -> dict:
    """Pooled penalized fit per agent; per-day gradients g (D x N x p) and Hessians H (D x N x p x p) at theta-hat."""
    N, p, D = des["N"], des["p"], len(des["X"])
    TH = np.zeros((N, p))
    G = np.zeros((D, N, p))
    H = np.zeros((D, N, p, p))
    for i in range(N):
        TH[i] = fit_agent(des["X"], [Y[:, i] for Y in des["Y"]], des["lam"])
        for d, (X, Y) in enumerate(zip(des["X"], des["Y"])):
            pr = _sig(X @ TH[i])
            G[d, i] = X.T @ (Y[:, i] - pr)
            H[d, i] = (X * (pr * (1 - pr))[:, None]).T @ X
    return {"theta": TH, "G": G, "H": H, "lam": des["lam"], "N": N, "p": p, "drift_idx": des["drift_idx"]}


def drift_score(F, tau) -> tuple:
    """Score statistic W for the day contrast tau (centred inside) on the drift parameters (h, J); returns
    (W, one-step drift ||delta_J||_F)."""
    tau = np.asarray(tau, float)
    tau = tau - tau.mean()
    G, H, lam, P = F["G"], F["H"], F["lam"], F["drift_idx"]
    W, dj2 = 0.0, 0.0
    Hsum = H.sum(0)                              # N x p x p
    Ht = np.einsum("d,dnij->nij", tau, H)
    Ht2 = np.einsum("d,dnij->nij", tau ** 2, H)
    U_all = np.einsum("d,dnp->np", tau, G)
    lamP = lam[P]
    for i in range(F["N"]):
        Itt = Hsum[i] + np.diag(lam)
        Idt = Ht[i][P]                           # |P| x p
        V = Ht2[i][np.ix_(P, P)] - Idt @ np.linalg.solve(Itt, Idt.T) + np.diag(lamP)
        U = U_all[i][P]
        sol = np.linalg.solve(V, U)
        W += float(U @ sol)
        dj2 += float(np.sum(sol[1:] ** 2))
    return W, float(np.sqrt(dj2))


def split_tau(n, first):
    t = np.zeros(n)
    t[list(first)] = 1.0
    return t


def contiguous_tau(n):
    return split_tau(n, range(n // 2))


def trend_tau(n):
    return np.arange(n, dtype=float)


def random_splits(n, R, rng):
    k = n // 2
    return [split_tau(n, rng.choice(n, size=k, replace=False)) for _ in range(R)]


def perm_test(F, tau_obs, taus_null):
    W_obs, dj = drift_score(F, tau_obs)
    Wn = np.array([drift_score(F, t)[0] for t in taus_null])
    p = (1 + np.sum(Wn >= W_obs)) / (1 + len(Wn))
    return {"W": W_obs, "R": W_obs / Wn.mean(), "p": float(p), "z": (W_obs - Wn.mean()) / Wn.std(ddof=1),
            "dJ": dj, "W_null_mean": float(Wn.mean())}


def boundary_rank(F, n, b_index):
    """Rank of the split at boundary b_index (days < b vs >= b) among all boundaries with >= 2 days per side."""
    Ws = {}
    for b in range(2, n - 1):
        Ws[b] = drift_score(F, split_tau(n, range(b)))[0]
    if b_index not in Ws:
        return {"rank_frac": np.nan, "W": np.nan, "n_boundaries": len(Ws)}
    vals = np.array(list(Ws.values()))
    r = float(np.mean(vals >= Ws[b_index]))  # share of boundaries at least as large (1/n = top)
    return {"rank_frac": r, "W": Ws[b_index], "n_boundaries": len(Ws), "all": Ws}


def onestep_window(F, day_idx):
    """One-step theta for a subset of days: theta + (H_w + Lam)^-1 (g_w - Lam theta)."""
    G, H, lam, TH = F["G"], F["H"], F["lam"], F["theta"]
    out = np.zeros_like(TH)
    for i in range(F["N"]):
        Hw = H[day_idx, i].sum(0) + np.diag(lam)
        gw = G[day_idx, i].sum(0) - lam * TH[i]
        out[i] = TH[i] + np.linalg.solve(Hw, gw)
    return out


# ============================================================================ EP
def ep_observables(s: np.ndarray):
    """Rows t = 0..T-3. Pair block g_ij = s_i(t+1)s_j(t) - s_j(t+1)s_i(t) (i<j); single block 1[001]-1[100], 1[011]-1[110]."""
    a, b, c = s[:-2], s[1:-1], s[2:]
    N = s.shape[1]
    iu, ju = np.triu_indices(N, 1)
    pair = b[:, iu] * a[:, ju] - b[:, ju] * a[:, iu]
    u = ((1 - a) * (1 - b) * c) - (a * (1 - b) * (1 - c))
    v = ((1 - a) * b * c) - (a * b * (1 - c))
    G = np.hstack([pair, u, v])
    block = np.concatenate([np.zeros(pair.shape[1], int), np.ones(2 * N, int)])
    return G, block


def ep_day_stats(win, drop_first_day=False):
    idx = list(range(len(win["S"])))[1:] if drop_first_day else list(range(len(win["S"])))
    out = []
    block = None
    for d in idx:
        G, block = ep_observables(win["S"][d])
        out.append((len(G), G.sum(0), G.T @ G))
    return out, block


def ep_of_days(stats, block, day_idx, k=5, fold_of=None):
    """Held-out Newton EP on the union of days; folds = day rank mod k, or fold_of[day] (bootstrap copies of one day
    stay in one fold)."""
    day_idx = sorted(day_idx) if fold_of is None else list(day_idx)
    kk = int(max(2, min(k, len(set(day_idx) if fold_of is None else set(fold_of)))))
    d = len(stats[0][1])
    folds = [[0, np.zeros(d), np.zeros((d, d))] for _ in range(kk)]
    for r, di in enumerate(day_idx):
        f = folds[(r if fold_of is None else fold_of[r]) % kk]
        n, s1, s2 = stats[di]
        f[0] += n
        f[1] = f[1] + s1
        f[2] = f[2] + s2
    fst = [tuple(f) for f in folds]
    cols = np.arange(d)
    res = EPN.newton_heldout_from_folds(fst, {"all": cols}, c=EPN.RIDGE_C, block=block)
    return res["all"]["sigma"]


def ep_split_test(stats, block, first_idx, null_splits, n):
    first = sorted(first_idx)
    second = sorted(set(range(n)) - set(first))
    obs = ep_of_days(stats, block, second) - ep_of_days(stats, block, first)
    nul = []
    for t in null_splits:
        a = np.flatnonzero(t > 0).tolist()
        b = np.flatnonzero(t <= 0).tolist()
        nul.append(ep_of_days(stats, block, b) - ep_of_days(stats, block, a))
    nul = np.array(nul)
    p = (1 + np.sum(np.abs(nul - nul.mean()) >= abs(obs - nul.mean()))) / (1 + len(nul))
    return {"dSigma": float(obs), "p": float(p), "null_sd": float(nul.std(ddof=1))}


def holm(ps):
    ps = np.asarray(ps, float)
    order = np.argsort(ps)
    m = len(ps)
    adj = np.empty(m)
    run = 0.0
    for r, i in enumerate(order):
        run = max(run, min(1.0, (m - r) * ps[i]))
        adj[i] = run
    return adj
