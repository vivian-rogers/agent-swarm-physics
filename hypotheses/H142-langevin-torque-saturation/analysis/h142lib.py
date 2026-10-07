"""H142 estimators: the step curve f(n) of the directional step on the aligned-read count, with call fixed effects
(alpha_c) and direction x room x hour fixed effects (delta), in-flight dummies, the newest-item indicator and the
named count as nuisance terms.

Every shape is a linear combination of indicators 1[n = v, k in bin b] (n >= 1), so the two-way fixed effects are
partialled out once from the indicator bank Z = [E, Q] (Frisch-Waugh-Lovell; alternating projections), and every fit
then works on per-day (and, for the dummies, per agent-day) sufficient statistics.

Shapes (Amendment A1, 2026-10-07, before real data: the shape amplitude is free per batch-size bin, so the linear
rival is linear in n at fixed k; the card's pooled-amplitude form is kept as the variant 'pooled'):
  linear     a_b n
  power      a_b n^p           (p on a grid; profile)
  Langevin   f_inf,b L(c n)    (c on a grid; profile), L(x) = coth x - 1/x, n_sat = 3 / c
  dummies    f(1), f(2), f(3), f(4-5), f(6+) pooled over k (O1, O2, O4; the card's model-free curve)
Out-of-fold: leave-one-day-out (the FE cells lie within a day, so partialling commutes with day folds); Gaussian
log-likelihood per test row with the training residual variance. Bootstrap: agent-day clusters (O1, O2, O4), days
(paired ΔLL; the profile CIs of c, n_sat and p).
"""
from __future__ import annotations

import math

import numpy as np
import polars as pl
import scipy.sparse as sp

BINS = [(1, 1), (2, 2), (3, 3), (4, 5), (6, 10_000)]
BIN_NAMES = ["n1", "n2", "n3", "n4_5", "n6p"]
F_BINS = [(1, 1), (2, 2), (3, 3), (4, 5), (6, 10_000)]
# batch-size bins for the shape amplitude (A1): log-spaced, edge ratio <= 1.25 above k = 8
K_BINS = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 8), (9, 10), (11, 13), (14, 16), (17, 20), (21, 25), (26, 32),
          (33, 40), (41, 50), (51, 63), (64, 80), (81, 100), (101, 126), (127, 160), (161, 200), (201, 250), (251, 320),
          (321, 400), (401, 500), (501, 10 ** 7)]
MIN_BIN_ROWS, MIN_BIN_DAYS = 100, 3      # A4 (2026-10-07): support of each amplitude bin
C_GRID = np.exp(np.linspace(np.log(0.02), np.log(30.0), 61))
P_GRID = np.round(np.r_[np.linspace(0.05, 1.5, 30), 1.0], 4)
LN_2PI = math.log(2 * math.pi)
SHAPES = {"linear": [None], "power": list(P_GRID), "langevin": list(C_GRID)}


def langevin(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    out = np.empty_like(x)
    small = np.abs(x) < 1e-3
    xs = x[small]
    out[small] = xs / 3 - xs ** 3 / 45
    xl = x[~small]
    out[~small] = 1 / np.tanh(xl) - 1 / xl
    return out


def shape_w(shape: str, theta, v: np.ndarray) -> np.ndarray:
    v = v.astype(float)
    if shape == "linear":
        return v
    if shape == "power":
        return v ** theta
    if shape == "langevin":
        return langevin(theta * v)
    raise ValueError(shape)


class Design:
    """Partialled indicator bank for one period's rows (fixed per skeleton; y can change).

    amplitude: 'kbin' (A1 primary: free amplitude per batch-size bin) or 'pooled' (card's original form)."""

    def __init__(self, rows: pl.DataFrame, amplitude: str = "kbin", tol: float = 1e-9, max_iter: int = 2000):
        self.amplitude = amplitude
        n = rows["n"].to_numpy().astype(int)
        k = rows["k"].to_numpy().astype(int)
        kb = np.full(len(k), -1)
        for j, (lo, hi) in enumerate(K_BINS):
            kb[(k >= lo) & (k <= hi)] = j
        if amplitude == "pooled":
            kb = np.where(k >= 1, 0, -1)
        else:
            kb = self._merge_kbins(kb, n, rows["pt_date"].to_numpy())
        self.call = np.unique(rows["call"].to_numpy(), return_inverse=True)[1]
        cell_key = (rows["u"].cast(pl.Int64) * 1_000_000_000 + rows["room"].cast(pl.Int64).fill_null(-1) * 10_000_000
                    + rows["hour"].cast(pl.Int64)).to_numpy()
        self.cell = np.unique(cell_key, return_inverse=True)[1]
        self.cl = np.unique((rows["agent"].cast(pl.String) + "|" + rows["pt_date"]).to_numpy(), return_inverse=True)[1]
        self.day_names, self.day = np.unique(rows["pt_date"].to_numpy(), return_inverse=True)
        self.n_cl = int(self.cl.max()) + 1; self.n_day = len(self.day_names)
        self.cl_day = np.zeros(self.n_cl, int); self.cl_day[self.cl] = self.day
        self.tol, self.max_iter = tol, max_iter
        nr = len(n)
        self._M = []
        for idx in (self.call, self.cell):
            cnt = np.bincount(idx).astype(float)
            self._M.append((sp.csr_matrix((np.ones(nr), (idx, np.arange(nr))), shape=(cnt.size, nr)), idx, cnt))
        self._Mcl = sp.csr_matrix((np.ones(nr), (self.cl, np.arange(nr))), shape=(self.n_cl, nr))
        self._Mday = sp.csr_matrix((np.ones(nr), (self.day, np.arange(nr))), shape=(self.n_day, nr))
        # indicator bank E over (value, k-bin) pairs with n >= 1
        pos = n >= 1
        pairs = np.unique(np.stack([n[pos], kb[pos]], 1), axis=0)
        self.pairs = pairs                                   # (P_e, 2): value, kbin
        pid = {(int(a), int(b)): i for i, (a, b) in enumerate(pairs)}
        e_col = np.array([pid[(int(a), int(b))] for a, b in zip(n[pos], kb[pos])], dtype=int)
        E = sp.csc_matrix((np.ones(int(pos.sum())), (np.flatnonzero(pos), e_col)), shape=(nr, len(pairs)))
        nF = rows["nF"].to_numpy().astype(int)
        Q = [((nF >= lo) & (nF <= hi)).astype(float) for lo, hi in F_BINS]
        qn = [f"nF{lo}" if lo == hi else f"nF{lo}_{min(hi, 99)}" for lo, hi in F_BINS]
        Q.append(rows["newest"].to_numpy().astype(float)); qn.append("newest")
        Q.append(rows["nname"].to_numpy().astype(float)); qn.append("nname")
        Q = np.column_stack(Q)
        keepq = Q.any(0)
        self.q_names = [nm for nm, kq in zip(qn, keepq) if kq]
        self.Pe, self.q = len(pairs), int(keepq.sum())
        Q = Q[:, keepq]
        self.Zt = np.empty((nr, self.Pe + self.q), np.float32)
        for a in range(0, self.Pe, 64):
            self.Zt[:, a:min(a + 64, self.Pe)] = self.partial(E[:, a:a + 64].toarray())
        self.Zt[:, self.Pe:] = self.partial(Q)
        self.iters_Z = self._last_iter
        del E, Q
        P = self.Pe + self.q
        self.G_day = np.zeros((self.n_day, P, P))
        order = np.argsort(self.day, kind="stable")
        bounds = np.r_[0, np.cumsum(np.bincount(self.day, minlength=self.n_day))]
        for d in range(self.n_day):
            Zd = self.Zt[order[bounds[d]:bounds[d + 1]]].astype(np.float64)
            self.G_day[d] = Zd.T @ Zd
        self.n_day_rows = np.bincount(self.day, minlength=self.n_day).astype(float)
        self.n_cl_rows = np.bincount(self.cl, minlength=self.n_cl).astype(float)
        # amplitude groups
        self.kbins_used = np.unique(pairs[:, 1])
        self.n_amp = len(self.kbins_used)
        # dummies (pooled over k): T_d
        self.n_by_bin = np.array([int(((n >= lo) & (n <= hi)).sum()) for lo, hi in BINS])
        Dm = np.zeros((self.Pe, len(BINS)))
        for j, (lo, hi) in enumerate(BINS):
            Dm[(pairs[:, 0] >= lo) & (pairs[:, 0] <= hi), j] = 1.0
        self.bins_present = Dm.any(0)
        self.T_d = self._T(Dm[:, self.bins_present])
        Xd = self.Zt @ self.T_d.astype(np.float32)
        self.Xd = Xd
        self.Hd_cl = np.zeros((self.n_cl, Xd.shape[1], Xd.shape[1]))
        oc = np.argsort(self.cl, kind="stable")
        bc = np.r_[0, np.cumsum(np.bincount(self.cl, minlength=self.n_cl))]
        for c in range(self.n_cl):
            Xc = Xd[oc[bc[c]:bc[c + 1]]].astype(np.float64)
            self.Hd_cl[c] = Xc.T @ Xc
        # per-day Grams for every shape and grid point (independent of y)
        self.Ts = {s: np.stack([self.shape_T(s, th) for th in SHAPES[s]]) for s in SHAPES}
        self.A_day = {}
        for s, T in self.Ts.items():
            A = np.zeros((T.shape[0], self.n_day, T.shape[2], T.shape[2]))
            for g in range(T.shape[0]):
                A[g] = T[g].T @ (self.G_day @ T[g])
            self.A_day[s] = A
        self.Ad_day = np.einsum("ip,dij,jq->dpq", self.T_d, self.G_day, self.T_d, optimize=True)

    @staticmethod
    def _merge_kbins(kb: np.ndarray, n: np.ndarray, day: np.ndarray) -> np.ndarray:
        """A4: merge sparse batch-size bins (top down, then the lowest upward) until every amplitude bin has
        >= MIN_BIN_ROWS rows with n >= 1 on >= min(MIN_BIN_DAYS, n_days) days, so no leave-one-day-out fold
        loses an amplitude's whole support."""
        pos = n >= 1
        need_d = min(MIN_BIN_DAYS, len(np.unique(day)))
        bins = sorted(set(kb[pos].tolist()))
        stats = {b: (int((kb[pos] == b).sum()), set(day[pos][kb[pos] == b].tolist())) for b in bins}
        groups = [[b] for b in bins]

        def ok(g):
            return sum(stats[b][0] for b in g) >= MIN_BIN_ROWS and len(set().union(*[stats[b][1] for b in g])) >= need_d
        i = len(groups) - 1
        while i > 0:
            if not ok(groups[i]):
                groups[i - 1] = groups[i - 1] + groups[i]; groups.pop(i)
            i -= 1
        while len(groups) > 1 and not ok(groups[0]):
            groups[1] = groups[0] + groups[1]; groups.pop(0)
        mp = {b: j for j, g in enumerate(groups) for b in g}
        out = np.full(len(kb), -1)
        out[pos] = [mp[b] for b in kb[pos]]
        return out

    def _T(self, W: np.ndarray) -> np.ndarray:
        P = self.Pe + self.q
        T = np.zeros((P, W.shape[1] + self.q))
        T[:self.Pe, :W.shape[1]] = W
        T[self.Pe:, W.shape[1]:] = np.eye(self.q)
        return T

    def shape_T(self, shape: str, theta) -> np.ndarray:
        w = shape_w(shape, theta, self.pairs[:, 0])
        W = np.zeros((self.Pe, self.n_amp))
        for j, b in enumerate(self.kbins_used):
            m = self.pairs[:, 1] == b
            W[m, j] = w[m]
        return self._T(W)

    def partial(self, X: np.ndarray) -> np.ndarray:
        X = np.array(X, dtype=float, copy=True)
        one = X.ndim == 1
        if one:
            X = X[:, None]
        scale = np.sqrt((X ** 2).mean(0)) + 1e-12
        it = 0
        for it in range(self.max_iter):
            X_old = X.copy() if it % 10 == 0 else None
            for Mt, idx, cnt in self._M:
                S = Mt @ X
                X -= (S / cnt[:, None])[idx]
            if X_old is not None and np.max(np.abs(X - X_old).max(0) / scale) < self.tol:
                break
        self._last_iter = it + 1
        return X[:, 0] if one else X

    def y_stats(self, y: np.ndarray) -> dict:
        yt = self.partial(y)
        y32 = yt[:, None].astype(np.float32)
        z_day = np.asarray(self._Mday @ (self.Zt * y32), dtype=np.float64)
        rd_cl = np.asarray(self._Mcl @ (self.Xd * y32), dtype=np.float64)
        return {"z_day": z_day, "rd_cl": rd_cl, "yy_day": np.bincount(self.day, weights=yt ** 2, minlength=self.n_day),
                "yy_cl": np.bincount(self.cl, weights=yt ** 2, minlength=self.n_cl), "n_day": self.n_day_rows.copy(),
                "n_cl": self.n_cl_rows.copy()}


def _solve(A: np.ndarray, b: np.ndarray, yy):
    p = A.shape[-1]
    tr = np.trace(A, axis1=-2, axis2=-1)
    A = A + (1e-10 * tr / p + 1e-14)[..., None, None] * np.eye(p)
    beta = np.linalg.solve(A, b[..., None])[..., 0]
    sse = yy - np.einsum("...i,...i->...", beta, b)
    return beta, sse


def _shape_stats(D: Design, st: dict, s: str):
    """r_day (g, d, p) for shape s."""
    return np.einsum("gip,di->gdp", D.Ts[s], st["z_day"])


def oof_loglik(D: Design, st: dict) -> dict:
    """Leave-one-day-out Gaussian log-likelihood per shape (linear, power, Langevin, pooled dummies)."""
    nd = st["n_day"]; yyd = st["yy_day"]
    out, theta = {}, {}
    use = (nd > 0) & (nd.sum() - nd > 0)
    for s in list(SHAPES) + ["dummies"]:
        if s == "dummies":
            Ad = D.Ad_day[None]; rd = np.einsum("ip,di->dp", D.T_d, st["z_day"])[None]; grid = [None]
        else:
            Ad = D.A_day[s]; rd = _shape_stats(D, st, s); grid = SHAPES[s]
        At = Ad.sum(1); rt = rd.sum(1); yyt = yyd.sum()
        Atr = At[:, None] - Ad; rtr = rt[:, None] - rd; yytr = yyt - yyd             # (g, d, ...)
        beta, sse = _solve(Atr, rtr, yytr[None, :])                                    # (g, d, p), (g, d)
        j = np.argmin(sse, 0)                                                          # best grid point per fold
        dd = np.arange(D.n_day)
        be = beta[j, dd]; ss = sse[j, dd]
        s2 = np.maximum(ss / np.maximum(nd.sum() - nd, 1), 1e-12)
        A_te = Ad[j, dd]; r_te = rd[j, dd]
        sse_te = yyd - 2 * np.einsum("dp,dp->d", be, r_te) + np.einsum("dp,dpq,dq->d", be, A_te, be)
        ll = -0.5 * nd * (LN_2PI + np.log(s2)) - sse_te / (2 * s2)
        out[s] = np.where(use, ll, 0.0)
        theta[s] = [grid[i] for i in j[use]]
    return {"ll_day": out, "n_day": np.where(use, nd, 0), "theta": theta}


def dll_summary(ll: dict, a: str, b: str, B: int = 1000, seed: int = 0) -> dict:
    """ΔLL(a - b) summed over day folds; paired bootstrap over day folds."""
    nd = ll["n_day"]; use = nd > 0
    dd = (ll["ll_day"][a] - ll["ll_day"][b])[use]
    tot = float(dd.sum()); N = float(nd[use].sum())
    rng = np.random.default_rng(seed)
    bs = dd[rng.integers(0, len(dd), (B, len(dd)))].sum(1)
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return {"dll": tot, "lo": float(lo), "hi": float(hi), "dll_per_row": tot / N if N else None, "n_rows": N,
            "n_days": int(use.sum()), "boot": bs}


def fit_profiles(D: Design, st: dict, B: int = 300, seed: int = 0, boot: bool = True) -> dict:
    """Full-data profile fits of the three shapes; day-bootstrap CIs of the shape parameter."""
    out = {}
    rng = np.random.default_rng(seed)
    Wd = np.stack([np.bincount(rng.integers(0, D.n_day, D.n_day), minlength=D.n_day) for _ in range(B)]).astype(float) if boot else None
    for s in SHAPES:
        Ad = D.A_day[s]; rd = _shape_stats(D, st, s)
        beta, sse = _solve(Ad.sum(1), rd.sum(1), st["yy_day"].sum())
        j = int(np.argmin(sse))
        amp = beta[j, :D.n_amp]
        o = {"theta": SHAPES[s][j], "sse": float(sse[j]), "amp": amp.tolist(), "grid_index": j}
        if boot and len(SHAPES[s]) > 1:
            Ab = np.einsum("bd,gdpq->bgpq", Wd, Ad); rb = np.einsum("bd,gdp->bgp", Wd, rd); yb = Wd @ st["yy_day"]
            _, sb = _solve(Ab, rb, yb[:, None])
            jb = np.argmin(sb, 1); th = np.asarray(SHAPES[s], dtype=float)[jb]
            o["theta_lo"] = float(np.percentile(th, 2.5)); o["theta_hi"] = float(np.percentile(th, 97.5))
            o["edge_share"] = float(np.mean((jb == 0) | (jb == len(SHAPES[s]) - 1)))
            o["theta_boot"] = th
        out[s] = o
    c = out["langevin"]["theta"]
    out["langevin"]["nsat"] = 3.0 / c
    if "theta_boot" in out["langevin"]:
        nsb = 3.0 / out["langevin"]["theta_boot"]
        out["langevin"]["nsat_lo"] = float(np.percentile(nsb, 2.5)); out["langevin"]["nsat_hi"] = float(np.percentile(nsb, 97.5))
        out["langevin"]["ln_nsat_boot"] = np.log(nsb)
    return out


def fit_dummies(D: Design, st: dict, B: int = 300, seed: int = 0, cluster: str = "agent_day") -> dict:
    """O1 step curve (pooled over k), O2 curvature contrast, O4 in-flight curve; cluster bootstrap over agent-days
    (card) or days."""
    Hc, rc, yc = D.Hd_cl, st["rd_cl"], st["yy_cl"]
    if cluster == "day":
        Hc = np.zeros((D.n_day,) + Hc.shape[1:]); np.add.at(Hc, D.cl_day, D.Hd_cl)
        rc = np.zeros((D.n_day, rc.shape[1])); np.add.at(rc, D.cl_day, st["rd_cl"])
        yc = np.bincount(D.cl_day, weights=st["yy_cl"], minlength=D.n_day)
    H = Hc.sum(0); r = rc.sum(0); yy = yc.sum()
    beta, _ = _solve(H, r, yy)
    rng = np.random.default_rng(seed)
    nc = Hc.shape[0]
    W = np.stack([np.bincount(rng.integers(0, nc, nc), minlength=nc) for _ in range(B)]).astype(float)
    betab, _ = _solve(np.einsum("bc,cij->bij", W, Hc), W @ rc, W @ yc)
    names = [nm for nm, p in zip(BIN_NAMES, D.bins_present) if p]
    nb = len(names)
    f = {nm: float(beta[j]) for j, nm in enumerate(names)}
    fb = {nm: betab[:, j] for j, nm in enumerate(names)}
    out = {"n_rows": int(st["n_cl"].sum()), "n_clusters": int(D.n_cl), "n_days": int(D.n_day)}
    out["f"] = {nm: {"est": f[nm], "lo": float(np.percentile(fb[nm], 2.5)), "hi": float(np.percentile(fb[nm], 97.5)),
                     "se": float(fb[nm].std()), "n": int(D.n_by_bin[BIN_NAMES.index(nm)])} for nm in names}
    gq = {nm: (float(beta[nb + j]), betab[:, nb + j]) for j, nm in enumerate(D.q_names)}
    out["nuis"] = {nm: {"est": v[0], "lo": float(np.percentile(v[1], 2.5)), "hi": float(np.percentile(v[1], 97.5))}
                   for nm, v in gq.items()}
    out["_fboot"] = fb
    if all(x in f for x in ("n1", "n2", "n3", "n6p")):
        with np.errstate(divide="ignore", invalid="ignore"):
            dcb = np.log(fb["n2"] / fb["n1"]) - np.log(fb["n6p"] / fb["n3"])
            r63 = fb["n6p"] / fb["n3"]
        pos = min(f["n1"], f["n2"], f["n3"], f["n6p"]) > 0
        est = float(np.log(f["n2"] / f["n1"]) - np.log(f["n6p"] / f["n3"])) if pos else float("nan")
        valid = np.isfinite(dcb) & (fb["n1"] > 0) & (fb["n2"] > 0) & (fb["n3"] > 0) & (fb["n6p"] > 0)
        ok = valid.mean() >= 0.5
        out["dcurv"] = {"est": est, "lo": float(np.percentile(dcb[valid], 2.5)) if ok else None,
                        "hi": float(np.percentile(dcb[valid], 97.5)) if ok else None, "valid_share": float(valid.mean()),
                        "defined": bool(out["f"]["n1"]["lo"] > 0 and pos)}
        out["ratio63"] = {"est": float(f["n6p"] / f["n3"]) if f["n3"] != 0 else None,
                          "lo": float(np.nanpercentile(r63, 2.5)), "hi": float(np.nanpercentile(r63, 97.5))}
    else:
        out["dcurv"] = {"est": None, "lo": None, "hi": None, "valid_share": 0.0, "defined": False}
    if "n1" in f and "nF1" in gq:
        g1b = gq["nF1"][1]; f1b = fb["n1"]
        with np.errstate(divide="ignore", invalid="ignore"):
            rat = g1b / f1b
        out["inflight"] = {"g1": gq["nF1"][0], "g1_lo": float(np.percentile(g1b, 2.5)), "g1_hi": float(np.percentile(g1b, 97.5)),
                           "ratio": gq["nF1"][0] / f["n1"] if f["n1"] != 0 else None,
                           "ratio_lo": float(np.nanpercentile(rat, 2.5)), "ratio_hi": float(np.nanpercentile(rat, 97.5)),
                           "contrast": f["n1"] - gq["nF1"][0], "contrast_lo": float(np.percentile(f1b - g1b, 2.5)),
                           "contrast_hi": float(np.percentile(f1b - g1b, 97.5))}
    return out


def re_pool(est, se) -> dict:
    """DerSimonian-Laird random-effects pool."""
    est, se = np.asarray(est, float), np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[ok], se[ok]
    if len(est) == 0:
        return {"est": None, "lo": None, "hi": None, "tau2": None, "k": 0}
    w = 1 / se ** 2
    mu = (w * est).sum() / w.sum()
    Qs = (w * (est - mu) ** 2).sum()
    c = w.sum() - (w ** 2).sum() / w.sum()
    tau2 = max(0.0, (Qs - (len(est) - 1)) / c) if len(est) > 1 and c > 0 else 0.0
    ws = 1 / (se ** 2 + tau2)
    mu = (ws * est).sum() / ws.sum(); s = math.sqrt(1 / ws.sum())
    return {"est": float(mu), "lo": float(mu - 1.96 * s), "hi": float(mu + 1.96 * s), "se": s, "tau2": float(tau2),
            "k": int(len(est))}
