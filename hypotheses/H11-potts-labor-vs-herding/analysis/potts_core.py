"""H11 core: uniform-coupling (mean-field / Curie-Weiss) Potts estimators, nulls, MF theory, jump test, simulator.

Model (per room block b of N_b >= 2 labeled agents in one window; states 0..S-1, `coupled[a]` marks real
projects; state 0 = 'other' is neutral, i.e. carries no coupling):

    P(sigma) ∝ exp( sum_i h(sigma_i) + βJ/(N_b-1) * sum_{i<j} δ(sigma_i, sigma_j) [coupled(sigma_i)] )

With the 1/(N-1) normalization the mean-field self-consistency is x_a = softmax_a(h_a + βJ x_a), so the
pure-Potts thresholds are the textbook ones: first-order transition at βJ_c = 2(q-1)ln(q-1)/(q-2),
disordered spinodal at βJ = q, ordered spinodal at βJ_s(q) = min_s ln((1+(q-1)s)/(1-s))/s.

Estimators
  fit_cw   exact finite-N MLE of (βJ, fields) from block occupancy vectors (generating functions, no
           enumeration). Fields per day ('day') or per period ('period'). This is "βJ from the dominant
           share and its fluctuations": fields fit the mean shares, βJ fits the occupancy fluctuations.
  fit_pl   pseudo-likelihood (conditional logit) with one βJ and agent-specific fields: coupling beyond
           stable agent preferences.
  plm_diag plmDCA-style pairwise couplings (secondary), Potts-diagonal component averaged over pairs.
"""
from __future__ import annotations

import math

import numpy as np
from scipy.optimize import minimize
from scipy.special import gammaln, logsumexp

# ----------------------------------------------------------------------------------------------
# data containers


class Snap:
    """Observations of one period: obs-level and block-level arrays."""

    def __init__(self, agent, label, block, day, n_states, coupled, block_day=None, agent_day_room=None):
        self.agent = np.asarray(agent, dtype=np.int64)
        self.label = np.asarray(label, dtype=np.int64)
        self.block = np.asarray(block, dtype=np.int64)
        self.day = np.asarray(day, dtype=np.int64)
        self.S = int(n_states)
        self.coupled = np.asarray(coupled, dtype=bool)
        nb = int(self.block.max()) + 1 if len(self.block) else 0
        self.counts = np.zeros((nb, self.S), dtype=np.int64)
        np.add.at(self.counts, (self.block, self.label), 1)
        self.N = self.counts.sum(1)
        bd = np.zeros(nb, dtype=np.int64)
        bd[self.block] = self.day
        self.block_day = bd if block_day is None else np.asarray(block_day)
        self.n_agents = int(self.agent.max()) + 1 if len(self.agent) else 0
        self.n_days = int(self.day.max()) + 1 if len(self.day) else 0

    def with_labels(self, label):
        return Snap(self.agent, label, self.block, self.day, self.S, self.coupled)

    def subset_obs(self, keep):
        """Keep a subset of observations; re-index blocks."""
        keep = np.asarray(keep, dtype=bool)
        b = self.block[keep]
        ub, inv = np.unique(b, return_inverse=True)
        d = self.day[keep]
        ud, dinv = np.unique(d, return_inverse=True)
        return Snap(self.agent[keep], self.label[keep], inv, dinv, self.S, self.coupled)


# ----------------------------------------------------------------------------------------------
# exact Curie-Weiss Potts likelihood via generating functions


def _bconv(A, B):
    """Batched truncated convolution in the linear domain. A, B: (G, M). Returns (G, M)."""
    G, M = A.shape
    idx = np.arange(M)[None, :] - np.arange(M)[:, None]          # [k, n] -> n-k
    T = np.where(idx >= 0, B[:, np.clip(idx, 0, M - 1)], 0.0)     # (G, k, n)
    return np.einsum("gk,gkn->gn", A, T)


def _lconv(LA, LB):
    """Batched truncated convolution in the log domain (row-wise scaling)."""
    ma = LA.max(1, keepdims=True)
    mb = LB.max(1, keepdims=True)
    ma = np.where(np.isfinite(ma), ma, 0.0)
    mb = np.where(np.isfinite(mb), mb, 0.0)
    R = _bconv(np.exp(LA - ma), np.exp(LB - mb))
    with np.errstate(divide="ignore"):
        return np.log(R) + ma + mb


class CWGroups:
    """Precomputed sufficient statistics of the occupancy data grouped by (block size N, field group)."""

    def __init__(self, snap: Snap, field_mode="day", min_N=2):
        keep = snap.N >= min_N
        cnt, N, bd = snap.counts[keep], snap.N[keep], snap.block_day[keep]
        self.S = snap.S
        self.coupled = snap.coupled
        fg = bd if field_mode == "day" else np.zeros_like(bd)
        self.n_fg = int(fg.max()) + 1 if len(fg) else 0
        # state sets present per field group (absent states have field -inf: their MLE limit)
        present = np.zeros((self.n_fg, self.S), dtype=bool)
        for g in range(self.n_fg):
            present[g] = cnt[fg == g].sum(0) > 0
        self.present = present
        # parameter layout: [βJ, free fields...]; reference state per group = its most common state
        self.ref = np.array([int(np.argmax(cnt[fg == g].sum(0))) if (fg == g).any() else 0 for g in range(self.n_fg)])
        free = present.copy()
        free[np.arange(self.n_fg), self.ref] = False
        self.free = free
        self.n_par = 1 + int(free.sum())
        # sufficient stats per field group
        self.sum_n = np.zeros((self.n_fg, self.S))
        for g in range(self.n_fg):
            self.sum_n[g] = cnt[fg == g].sum(0)
        pair = (cnt * (cnt - 1) / 2.0)[:, self.coupled].sum(1)
        self.sum_s2 = float((pair / np.maximum(N - 1, 1)).sum())
        # unique (N, fg) groups with multiplicities
        key = N * 1000 + fg
        uk, inv, mult = np.unique(key, return_inverse=True, return_counts=True)
        self.gN = (uk // 1000).astype(int)
        self.gfg = (uk % 1000).astype(int)
        self.mult = mult.astype(float)
        self.M = int(self.gN.max()) + 1 if len(self.gN) else 1
        self.n_blocks = int(keep.sum())
        self.mean_N = float(N.mean()) if len(N) else 0.0

    def unpack(self, theta):
        bj = theta[0]
        H = np.full((self.n_fg, self.S), -np.inf)
        H[self.present] = 0.0
        H[self.free] = theta[1:]
        return bj, H

    def negll(self, theta, ridge=1e-3):
        bj, H = self.unpack(theta)
        G, S, M = len(self.gN), self.S, self.M
        k = np.arange(M)[None, :]
        c = bj / np.maximum(self.gN - 1, 1)                                  # (G,)
        Hg = H[self.gfg]                                                     # (G, S)
        # log coefficients of f_a(z) truncated at each group's N
        L = np.empty((S, G, M))
        valid = k <= self.gN[:, None]
        Hg = np.where(np.isfinite(Hg), Hg, np.nan)
        for a in range(S):
            ca = c if self.coupled[a] else np.zeros(G)
            La = np.nan_to_num(Hg[:, a:a + 1], nan=0.0) * k + ca[:, None] * k * (k - 1) / 2.0 - gammaln(k + 1)
            La = np.where(valid, La, -np.inf)
            if not np.isfinite(Hg[:, a]).all():
                La[~np.isfinite(Hg[:, a])] = -np.inf
                La[~np.isfinite(Hg[:, a]), 0] = 0.0  # absent state contributes the constant 1
            L[a] = La
        # prefix / suffix products
        pre = [None] * (S + 1)
        suf = [None] * (S + 1)
        one = np.full((G, M), -np.inf)
        one[:, 0] = 0.0
        pre[0] = one
        for a in range(S):
            pre[a + 1] = _lconv(pre[a], L[a])
        suf[S] = one
        for a in range(S - 1, -1, -1):
            suf[a] = _lconv(suf[a + 1], L[a])
        lZc = pre[S][np.arange(G), self.gN]                                  # log [z^N] prod f
        # marginals of n_a: P(n_a=k) ∝ exp(L_a[k] + R_a[N-k])
        En = np.zeros((G, S))
        Epair = np.zeros(G)
        Nidx = self.gN[:, None] - k                                          # N - k
        for a in range(S):
            if not np.isfinite(Hg[:, a]).any():
                continue
            R = _lconv(pre[a], suf[a + 1])
            Rg = np.where(Nidx >= 0, np.take_along_axis(R, np.clip(Nidx, 0, M - 1), 1), -np.inf)
            lp = L[a] + Rg - lZc[:, None]
            p = np.exp(lp)
            p = np.where(np.isfinite(lp), p, 0.0)
            En[:, a] = (p * k).sum(1)
            if self.coupled[a]:
                Epair += (p * k * (k - 1) / 2.0).sum(1)
        # log-likelihood (dropping the parameter-free multinomial term)
        ll = (np.where(np.isfinite(H), H, 0.0) * self.sum_n).sum() + bj * self.sum_s2
        lZ = lZc + gammaln(self.gN + 1)
        ll -= (self.mult * lZ).sum()
        # gradients
        gH = self.sum_n.copy()
        np.add.at(gH, self.gfg, -(self.mult[:, None] * En))
        gbj = self.sum_s2 - (self.mult * Epair / np.maximum(self.gN - 1, 1)).sum()
        free_theta = theta[1:]
        ll -= 0.5 * ridge * (free_theta ** 2).sum()
        grad = np.concatenate([[gbj], gH[self.free] - ridge * free_theta])
        return -ll, -grad

    def fit(self, bj0=0.0, fix_bj=None, ridge=1e-3):
        theta0 = np.zeros(self.n_par)
        theta0[0] = bj0
        # field start: log share ratio vs reference
        with np.errstate(divide="ignore"):
            ls = np.log(np.maximum(self.sum_n, 1e-9))
        h0 = ls - ls[np.arange(self.n_fg), self.ref][:, None]
        theta0[1:] = h0[self.free]
        if fix_bj is not None:
            def f(t):
                v, g = self.negll(np.concatenate([[fix_bj], t]), ridge)
                return v, g[1:]
            r = minimize(f, theta0[1:], jac=True, method="L-BFGS-B")
            th = np.concatenate([[fix_bj], r.x])
            return th, -r.fun
        bounds = [(-30.0, 30.0)] + [(-30.0, 30.0)] * (self.n_par - 1)
        r = minimize(lambda t: self.negll(t, ridge), theta0, jac=True, method="L-BFGS-B", bounds=bounds,
                     options={"maxiter": 500})
        return r.x, -r.fun


def fit_cw(snap: Snap, field_mode="day", min_N=2):
    g = CWGroups(snap, field_mode, min_N)
    if g.n_blocks < 3:
        return dict(bj=np.nan, ll=np.nan, n_blocks=g.n_blocks)
    th, ll = g.fit()
    _, ll0 = g.fit(fix_bj=0.0)
    return dict(bj=float(th[0]), ll=float(ll), ll0=float(ll0), lr=float(2 * (ll - ll0)), n_blocks=g.n_blocks,
                mean_N=g.mean_N, theta=th, groups=g)


def jackknife_cw(snap: Snap, field_mode="day"):
    """Leave-one-day-out jackknife SE for βJ_CW (days are the independent units)."""
    full = fit_cw(snap, field_mode)
    vals = []
    for d in range(snap.n_days):
        keep = snap.day != d
        if keep.sum() == 0:
            continue
        s = snap.subset_obs(keep)
        r = fit_cw(s, field_mode)
        if np.isfinite(r["bj"]):
            vals.append(r["bj"])
    vals = np.array(vals)
    D = len(vals)
    se = math.sqrt((D - 1) / D * ((vals - vals.mean()) ** 2).sum()) if D >= 2 else np.nan
    return full, se, vals


# ----------------------------------------------------------------------------------------------
# pseudo-likelihood with agent (or uniform / day) fields


def pl_design(snap: Snap):
    """x_{-i,a} = (n_{b,a} - [y_i = a]) / (N_b - 1) for coupled states; 0 for the neutral state."""
    cnt = snap.counts[snap.block].astype(float)
    cnt[np.arange(len(snap.label)), snap.label] -= 1.0
    Nm1 = (snap.N[snap.block] - 1).astype(float)
    ok = Nm1 >= 1
    X = np.zeros_like(cnt)
    X[ok] = cnt[ok] / Nm1[ok, None]
    X[:, ~snap.coupled] = 0.0
    return X, ok


def fit_pl(snap: Snap, fields="agent", ridge=0.1, return_fields=False, fix_bj=None):
    X, ok = pl_design(snap)
    y = snap.label[ok]
    X = X[ok]
    if fields == "agent":
        gidx = snap.agent[ok]
    elif fields == "agent_day":
        gidx = snap.agent[ok] * 1000 + snap.day[ok]
        gidx = np.unique(gidx, return_inverse=True)[1]
    elif fields == "day":
        gidx = snap.day[ok]
    else:
        gidx = np.zeros(ok.sum(), dtype=np.int64)
    n_g = int(gidx.max()) + 1 if len(gidx) else 0
    S = snap.S
    n = len(y)
    if n < 10:
        return dict(bj=np.nan, n=n)
    Y = np.zeros((n, S))
    Y[np.arange(n), y] = 1.0
    present = np.zeros(S, dtype=bool)
    present[np.unique(y)] = True

    def f(t):
        bj = t[0]
        H = t[1:].reshape(n_g, S)
        U = H[gidx] + bj * X
        U[:, ~present] = -np.inf
        lse = logsumexp(U, axis=1)
        P = np.exp(U - lse[:, None])
        ll = (U[np.arange(n), y]).sum() - lse.sum() - 0.5 * ridge * (H[:, present] ** 2).sum()
        R = Y - P
        gH = np.zeros((n_g, S))
        np.add.at(gH, gidx, R)
        gH -= ridge * H
        gH[:, ~present] = 0.0
        gbj = (R * X).sum()
        return -ll, -np.concatenate([[gbj], gH.ravel()])

    t0 = np.zeros(1 + n_g * S)
    b0 = (-30, 30) if fix_bj is None else (fix_bj, fix_bj)
    t0[0] = 0.0 if fix_bj is None else fix_bj
    r = minimize(f, t0, jac=True, method="L-BFGS-B", bounds=[b0] + [(-20, 20)] * (n_g * S))
    out = dict(bj=float(r.x[0]), ll=float(-r.fun), n=n)
    if return_fields:
        out["H"] = r.x[1:].reshape(n_g, S)
        out["gidx"] = gidx
    return out


def pl_loglik_heldout(train: Snap, test: Snap, with_coupling=True, ridge=0.1):
    """Fit agent-field PL (with or without coupling) on train, return mean held-out pseudo-loglik on test."""
    S = train.S
    r = fit_pl(train, "agent", ridge, return_fields=True, fix_bj=None if with_coupling else 0.0)
    bj = r["bj"] if with_coupling else 0.0
    H = r["H"]
    X, ok = pl_design(test)
    y, ag = test.label[ok], test.agent[ok]
    Hn = np.zeros((max(test.n_agents, H.shape[0]), S))
    Hn[:H.shape[0]] = H
    U = Hn[ag] + bj * X[ok]
    lse = logsumexp(U, axis=1)
    return float((U[np.arange(len(y)), y] - lse).mean()), int(len(y))


def _fit_fields_only(snap: Snap, ridge):
    S = snap.S
    n_g = snap.n_agents
    H = np.zeros((n_g, S))
    X, ok = pl_design(snap)
    for i in range(n_g):
        m = (snap.agent == i) & ok
        c = np.bincount(snap.label[m], minlength=S).astype(float)
        # MAP of a softmax with a Gaussian ridge ~ smoothed log counts
        H[i] = np.log(c + 0.5) - np.log(c + 0.5).mean()
    return dict(H=H)


# ----------------------------------------------------------------------------------------------
# nulls


def null_labels(snap: Snap, kind: str, rng: np.random.Generator):
    """Permuted labels. 'perm': within agent over the whole period; 'perm_day': within agent-day.
    (The circular-shift null is shift_snap, because observations move with their labels.)"""
    y = snap.label.copy()
    key = snap.agent if kind == "perm" else snap.agent * 1000 + snap.day
    order = np.argsort(key, kind="stable")
    ks = key[order]
    bounds = np.flatnonzero(np.diff(ks)) + 1
    for grp in np.split(order, bounds):
        y[grp] = y[rng.permutation(grp)]
    return y


def shift_snap(snap: Snap, rng: np.random.Generator, max_shift=None):
    """Circular-shift null: rotate each agent's within-day window sequence (labels and presence together)
    by a random offset; blocks are rebuilt from the shifted positions (room kept per agent-day)."""
    agent, label, day, pos = [], [], [], []
    key = snap.agent * 1000 + snap.day
    for k in np.unique(key):
        m = np.flatnonzero(key == k)
        d = int(snap.day[m[0]])
        K = int(snap.day_len[d])
        if max_shift is None:
            s = int(rng.integers(0, K))
        else:  # local shift: a random nonzero offset in [-max_shift, max_shift], circular within the day
            s = int(rng.choice([o for o in range(-max_shift, max_shift + 1) if o != 0]))
        agent.append(snap.agent[m])
        label.append(snap.label[m])
        day.append(snap.day[m])
        pos.append((snap.win_pos[m] + s) % K)
    agent, label, day, pos = map(np.concatenate, (agent, label, day, pos))
    room = snap.agent_day_room[agent * 1000 + day] if hasattr(snap, "agent_day_room") else np.zeros_like(agent)
    bkey = (day * 1000 + pos) * 100 + room
    block = np.unique(bkey, return_inverse=True)[1]
    s2 = Snap(agent, label, block, day, snap.S, snap.coupled)
    s2.win_pos, s2.day_len = pos, snap.day_len
    s2.agent_day_room = snap.agent_day_room
    return s2


# ----------------------------------------------------------------------------------------------
# pairwise plmDCA (secondary)


def plm_diag(snap: Snap, lam_h=0.01, lam_J=1.0):
    """plmDCA on window snapshots within blocks; returns the mean Potts-diagonal coupling over pairs
    (zero-sum gauge, coupled states only) and the per-pair matrix."""
    A, S = snap.n_agents, snap.S
    # one-hot of every agent's label per block (0 if absent)
    nb = snap.counts.shape[0]
    OH = np.zeros((nb, A, S))
    OH[snap.block, snap.agent, snap.label] = 1.0
    J = np.zeros((A, A, S, S))
    for i in range(A):
        m = snap.agent == i
        if m.sum() < 8:
            continue
        b = snap.block[m]
        y = snap.label[m]
        Xo = OH[b].copy()
        Xo[:, i, :] = 0.0
        Xf = Xo.reshape(len(b), A * S)
        n = len(y)

        def f(t):
            h = t[:S]
            W = t[S:].reshape(A * S, S)
            U = h[None, :] + Xf @ W
            lse = logsumexp(U, axis=1)
            P = np.exp(U - lse[:, None])
            ll = U[np.arange(n), y].sum() - lse.sum() - 0.5 * lam_h * (h ** 2).sum() - 0.5 * lam_J * (W ** 2).sum()
            R = -P
            R[np.arange(n), y] += 1.0
            gh = R.sum(0) - lam_h * h
            gW = Xf.T @ R - lam_J * W
            return -ll, -np.concatenate([gh, gW.ravel()])

        r = minimize(f, np.zeros(S + A * S * S), jac=True, method="L-BFGS-B")
        W = r.x[S:].reshape(A, S, S)          # W[j, b, a]: effect of j in state b on i choosing a
        J[i] = np.transpose(W, (0, 2, 1))     # J[i, j, a, b]
    Js = 0.5 * (J + np.transpose(J, (1, 0, 3, 2)))
    cs = np.flatnonzero(snap.coupled & (snap.counts.sum(0) > 0))
    D = np.full((A, A), np.nan)
    for i in range(A):
        for j in range(i + 1, A):
            M = Js[i, j][np.ix_(cs, cs)]
            if len(cs) < 2 or not np.any(M):
                continue
            M = M - M.mean(0, keepdims=True) - M.mean(1, keepdims=True) + M.mean()
            off = (M.sum() - np.trace(M)) / (len(cs) * (len(cs) - 1))
            D[i, j] = np.trace(M) / len(cs) - off
    return float(np.nanmean(D)) if np.isfinite(D).any() else np.nan, D


# ----------------------------------------------------------------------------------------------
# mean-field theory


def bj_c(q):
    return 2.0 if q == 2 else 2 * (q - 1) * math.log(q - 1) / (q - 2)


def bj_of_s(s, q):
    return np.log((1 + (q - 1) * s) / (1 - s)) / s


def bj_spinodal(q):
    """Ordered-phase spinodal of the pure q-state mean-field Potts model (lowest βJ with an ordered solution)."""
    if q <= 2:
        return 2.0
    s = np.linspace(1e-4, 0.9999, 200000)
    return float(bj_of_s(s, q).min())


def bj_from_share(x1, q):
    """Zero-field inversion: the βJ for which a dominant share x1 is a mean-field solution of pure Potts."""
    if q < 2 or x1 <= 1.0 / q:
        return np.nan
    s = (q * x1 - 1) / (q - 1)
    s = min(s, 0.99999)
    return float(bj_of_s(s, q))


def mf_ordered_share(bj, q):
    """Dominant share of the stable ordered MF solution at βJ (pure Potts, zero field); 1/q if none."""
    if bj < bj_spinodal(q):
        return 1.0 / q
    s = np.linspace(1e-4, 0.9999, 200000)
    v = bj_of_s(s, q)
    # largest s with bj_of_s(s) <= bj on the increasing branch
    smin = s[np.argmin(v)]
    br = (s >= smin) & (v <= bj)
    if not br.any():
        return 1.0 / q
    ss = s[br].max()
    return (1 + (q - 1) * ss) / q


# ----------------------------------------------------------------------------------------------
# jump detection on the dominant share


def _binll(k, n, p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return (k * np.log(p) + (n - k) * np.log(1 - p)).sum()


def fit_jump(t, k, n, tau_max=2.0, min_amp=0.3, dbic=6.0):
    """Logistic-step vs linear vs constant fits of k/n over window index t (binomial quasi-likelihood)."""
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        return _fit_jump(t, k, n, tau_max, min_amp, dbic)


def _fit_jump(t, k, n, tau_max, min_amp, dbic):
    t, k, n = map(lambda a: np.asarray(a, float), (t, k, n))
    m = n > 0
    t, k, n = t[m], k[m], n[m]
    T = len(t)
    if T < 8:
        return dict(verdict="n/a", T=T)
    p0 = k.sum() / n.sum()
    ll0 = _binll(k, n, np.full(T, p0))
    A = np.vstack([np.ones(T), t - t.mean()]).T
    best1 = (-np.inf, None)
    w = n / np.maximum(p0 * (1 - p0), 1e-3)
    beta = np.linalg.lstsq(A * np.sqrt(w)[:, None], (k / n) * np.sqrt(w), rcond=None)[0]
    r1 = minimize(lambda b: -_binll(k, n, A @ b), beta, method="Nelder-Mead")
    ll1 = -r1.fun
    taus = np.exp(np.linspace(np.log(0.25), np.log(max(T, 2.0)), 25))
    t0s = np.linspace(t.min(), t.max(), 60)
    best = (-np.inf, None)
    for tau in taus:
        for t0 in t0s:
            z = 1.0 / (1.0 + np.exp(-(t - t0) / tau))
            # lo, hi by weighted LS then clip, then refine
            B = np.vstack([1 - z, z]).T
            lohi = np.clip(np.linalg.lstsq(B * np.sqrt(n)[:, None], (k / n) * np.sqrt(n), rcond=None)[0], 0.0, 1.0)
            ll = _binll(k, n, B @ lohi)
            if ll > best[0]:
                best = (ll, (tau, t0, lohi[0], lohi[1]))
    tau, t0, lo, hi = best[1]

    def nll2(p):
        lo_, hi_, t0_, lt = p
        z = 1.0 / (1.0 + np.exp(-(t - t0_) / math.exp(lt)))
        return -_binll(k, n, np.clip(lo_ + (hi_ - lo_) * z, 0, 1))

    r2 = minimize(nll2, [lo, hi, t0, math.log(tau)], method="Nelder-Mead", options={"maxiter": 4000})
    lo, hi, t0, lt = r2.x
    tau = math.exp(lt)
    ll2 = -r2.fun
    z = 1.0 / (1.0 + np.exp(-(t - t0) / tau))
    pf = np.clip(lo + (hi - lo) * z, 1e-6, 1 - 1e-6)
    phi = max(1.0, float((((k - n * pf) ** 2) / (n * pf * (1 - pf))).sum() / max(T - 4, 1)))
    lnT = math.log(T)
    bic0, bic1, bic2 = -2 * ll0 / phi + 1 * lnT, -2 * ll1 / phi + 2 * lnT, -2 * ll2 / phi + 4 * lnT
    amp = hi - lo
    after = t >= t0 + 2 * tau
    mid = 0.5 * (lo + hi)
    pers = float(((k[after] / n[after]) < mid).mean()) if after.any() and amp > 0 else np.nan
    if bic2 + dbic <= min(bic0, bic1) and abs(amp) >= min_amp and tau <= tau_max and t.min() < t0 < t.max():
        verdict = "jump"
    elif min(bic1, bic2) + dbic <= bic0:
        verdict = "gradual"
    else:
        verdict = "none"
    return dict(verdict=verdict, tau=float(tau), t0=float(t0), lo=float(lo), hi=float(hi), amp=float(amp), phi=phi,
                dbic_step_vs_lin=float(bic1 - bic2), dbic_step_vs_const=float(bic0 - bic2),
                dbic_lin_vs_const=float(bic0 - bic1), persistence_below_mid=pers, T=T)


# ----------------------------------------------------------------------------------------------
# kinetic Potts simulator (heat bath), village-like sampling


def simulate(N=10, q=4, bj=0.0, days=5, wins_per_day=9, p_obs=0.6, sigma_h=0.0, other_field=-1.0,
             sweeps_per_window=0.5, overnight_sweeps=3.0, drift=None, field_step=None, field_ramp=None,
             rng=None):
    """Return dict(agent, label, day, win) of observed (agent, window) states.
    States: 0 = neutral 'other', 1..q coupled. Agent fields ~ N(0, sigma_h) on coupled states.
    drift: amplitude of a common day-level random field on coupled states (time-varying common drive).
    field_step: (t_frac, state, size) common field step at a fraction of the period.
    field_ramp: (state, h_start, h_end) common field ramped linearly over the period."""
    rng = rng or np.random.default_rng()
    S = q + 1
    H = np.zeros((N, S))
    H[:, 1:] = rng.normal(0, sigma_h, size=(N, q)) if sigma_h > 0 else 0.0
    H[:, 0] = other_field
    coupled = np.ones(S, bool)
    coupled[0] = False
    sig = rng.integers(0, S, size=N)
    n = np.bincount(sig, minlength=S).astype(float)
    T = days * wins_per_day
    out_a, out_l, out_d, out_w = [], [], [], []
    g_day = np.zeros(S)

    def sweep(nsweeps, g):
        nonlocal sig, n
        steps = int(round(nsweeps * N))
        for _ in range(steps):
            i = rng.integers(N)
            n[sig[i]] -= 1
            x = n / (N - 1)
            u = H[i] + g + bj * np.where(coupled, x, 0.0)
            p = np.exp(u - u.max())
            p /= p.sum()
            sig[i] = rng.choice(S, p=p)
            n[sig[i]] += 1

    sweep(20, np.zeros(S))  # burn-in
    for d in range(days):
        if drift:
            g_day = np.zeros(S)
            g_day[1:] = rng.normal(0, drift, size=q)
        sweep(overnight_sweeps, g_day)
        for w in range(wins_per_day):
            tt = (d * wins_per_day + w) / max(T - 1, 1)
            g = g_day.copy()
            if field_step is not None and tt >= field_step[0]:
                g[field_step[1]] += field_step[2]
            if field_ramp is not None:
                g[field_ramp[0]] += field_ramp[1] + (field_ramp[2] - field_ramp[1]) * tt
            sweep(sweeps_per_window, g)
            obs = rng.random(N) < p_obs
            for i in np.flatnonzero(obs):
                out_a.append(i)
                out_l.append(sig[i])
                out_d.append(d)
                out_w.append(w)
    return dict(agent=np.array(out_a), label=np.array(out_l), day=np.array(out_d), win=np.array(out_w), S=S,
                coupled=coupled, wins_per_day=wins_per_day)


def snap_from_arrays(agent, label, day, win, S, coupled, room=None, wins_per_day=None, day_len=None):
    agent, label, day, win = map(np.asarray, (agent, label, day, win))
    room = np.zeros_like(agent) if room is None else np.asarray(room)
    bkey = (day.astype(np.int64) * 1000 + win) * 100 + room
    block = np.unique(bkey, return_inverse=True)[1]
    ud, dinv = np.unique(day, return_inverse=True)
    ua, ainv = np.unique(agent, return_inverse=True)
    s = Snap(ainv, label, block, dinv, S, coupled)
    s.win_pos = win.astype(np.int64)
    if day_len is None:
        K = wins_per_day if wins_per_day else int(win.max()) + 1
        s.day_len = np.full(len(ud), K)
    else:
        s.day_len = np.asarray(day_len)
    # modal room per agent-day (for the circular-shift null)
    adr = {}
    for a_, d_, r_ in zip(ainv, dinv, room):
        adr.setdefault(a_ * 1000 + d_, []).append(r_)
    arr = np.zeros(int(ainv.max()) * 1000 + int(dinv.max()) + 1 if len(ainv) else 1, dtype=np.int64)
    for k, v in adr.items():
        arr[k] = np.bincount(v).argmax()
    s.agent_day_room = arr
    s.win = win
    s.room = room
    return s


def dominant_series(snap: Snap, state, win_index):
    """Share of `state` among labeled agents per window (all rooms pooled). win_index: global window index per obs."""
    wi = np.asarray(win_index)
    uw, inv = np.unique(wi, return_inverse=True)
    n = np.bincount(inv)
    k = np.bincount(inv, weights=(snap.label == state).astype(float))
    return uw, k, n
