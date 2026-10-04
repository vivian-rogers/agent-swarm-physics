"""H59 estimator: three-state call-level Markov GLM with one lever per input class.

Baseline: per from-state multinomial logit (stay = reference) with agent, day, run-length, Markov-2, time-of-day and
nuisance-context terms plus free kick dummies for every class and every lag bit (so kick rows do not bias it).
Kick models are fitted on the exposed rows with the baseline (incl. the lag -1 pre-read term) as a fixed offset:
  B[c, l, i, j] = K_l * (kappa_c + h_c * (u_j - u_i) / 2),  u(theta) = (0, cos theta, sin theta),  K_0 = 1.
Parametrizations: lever (shared theta, K), dir (theta per class), delay (one kappa, h for all classes), free (36 betas
per class, ridge).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
import scipy.sparse as sp  # noqa: E402
from scipy.optimize import minimize  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data/processed/H59-one-lever-model"
CLASSES = ["N", "Hu", "Hm", "A"]
NL = 6                     # lag bins 0, 1, 2, 3-5, 6-10, 11-30 (bits 1..6); bit 0 = lag -1 (pre-read, in baseline)
LAG_LABELS = ["0", "1", "2", "3-5", "6-10", "11-30"]
STATES = ["I", "W", "T"]
OTHER = {0: [1, 2], 1: [0, 2], 2: [0, 1]}
MIN_REC = 50


# ------------------------------------------------------------------------------------------------ data
def load(goal: int, days: list[str] | None = None) -> pl.DataFrame:
    t = pl.read_parquet(OUT / "transitions.parquet").filter(pl.col("goal_no") == goal)
    if days is not None:
        t = t.filter(pl.col("pt_date").is_in(days))
    return t.sort("agent", "pt_date", "t_call")


def arrays(t: pl.DataFrame) -> dict:
    n = t.height
    d = {"n": n, "fs": t["s_prev"].to_numpy().astype(np.int64), "y": t["s"].to_numpy().astype(np.int64)}
    d["agent"] = t["agent"].rank("dense").to_numpy().astype(np.int64) - 1
    days = sorted(t["pt_date"].unique().to_list())
    d["days"] = days
    d["day"] = t["pt_date"].replace_strict({x: i for i, x in enumerate(days)}, return_dtype=pl.Int64).to_numpy()
    d["run"] = np.digitize(t["run_prev"].to_numpy(), [2, 5, 15, 50]).astype(np.int64)
    d["prev2"] = t["s_prev2"].to_numpy().astype(np.int64) + 1
    d["tod"] = t["tod"].to_numpy().astype(np.int64)
    d["chat"] = np.log1p(t["n_chat"].to_numpy().astype(float))
    d["book"] = (t["n_bookend"].to_numpy() > 0).astype(float)
    m = np.stack([t[f"m_{c}"].to_numpy() for c in CLASSES], 1)            # n x C uint8
    d["bits"] = ((m[:, :, None] >> np.arange(7)[None, None, :]) & 1).astype(np.uint8)   # n x C x 7
    d["n0"] = np.stack([t[f"n_{c}"].to_numpy() for c in CLASSES], 1)
    d["age0"] = np.stack([t[f"age_{c}"].fill_null(np.nan).to_numpy().astype(float) for c in CLASSES], 1)
    d["t_call"] = t["t_call"].to_numpy()
    d["pt_date"] = t["pt_date"].to_numpy()
    return d


def base_design(d: dict) -> tuple[sp.csr_matrix, int]:
    """Sparse baseline design; returns (X, index of the first kick column). Kick columns: C x 7 bits."""
    n = d["n"]
    blocks, off = [], 0
    rows = np.arange(n)

    def onehot(v, k):
        return sp.csr_matrix((np.ones(n), (rows, v)), shape=(n, k))
    blocks.append(sp.csr_matrix(np.ones((n, 1))))
    blocks.append(onehot(d["agent"], d["agent"].max() + 1))
    blocks.append(onehot(d["day"], d["day"].max() + 1))
    blocks.append(onehot(d["run"], 5)[:, 1:])
    blocks.append(onehot(d["prev2"], 4)[:, 1:])
    blocks.append(onehot(d["tod"], 4)[:, 1:])
    blocks.append(sp.csr_matrix(np.c_[d["chat"], d["book"]]))
    k0 = sum(b.shape[1] for b in blocks)
    blocks.append(sp.csr_matrix(d["bits"].reshape(n, -1).astype(float)))
    return sp.hstack(blocks).tocsr(), k0


def fit_mnl(X, y, i, ridge=1e-2, w=None):
    """Multinomial logit for from-state i (stay = reference). Returns W (p x 2) for outcomes OTHER[i]."""
    o = OTHER[i]
    Y = np.c_[(y == o[0]).astype(float), (y == o[1]).astype(float)]
    w = np.ones(X.shape[0]) if w is None else w
    p = X.shape[1]

    def f(v):
        Wm = v.reshape(p, 2)
        E = X @ Wm
        mx = np.maximum(E.max(1), 0)
        Z = np.exp(-mx) + np.exp(E - mx[:, None]).sum(1)
        ll = (w * ((Y * E).sum(1) - mx - np.log(Z))).sum()
        P = np.exp(E - mx[:, None]) / Z[:, None]
        g = X.T @ (w[:, None] * (Y - P))
        return -ll + 0.5 * ridge * (v ** 2).sum(), -g.ravel() + ridge * v
    r = minimize(f, np.zeros(p * 2), jac=True, method="L-BFGS-B", options={"maxiter": 2000, "maxfun": 4000})
    return r.x.reshape(p, 2)


def baseline(d: dict) -> dict:
    """Fit the baseline per from-state; return offsets (n x 3; kick bits 1..6 excluded, lag -1 kept) and the free
    all-days kick dummies (C x 7 x 3 x 3) for reference."""
    X, k0 = base_design(d)
    C = len(CLASSES)
    off = np.zeros((d["n"], 3))
    Bfull = np.zeros((C, 7, 3, 3))
    keep = np.ones(X.shape[1], bool)
    kick_cols = np.arange(k0, k0 + C * 7).reshape(C, 7)
    keep[kick_cols[:, 1:].ravel()] = False
    for i in range(3):
        sel = d["fs"] == i
        if sel.sum() < 30:
            continue
        Xi = X[sel]
        Wm = fit_mnl(Xi, d["y"][sel], i)
        Eb = Xi[:, keep] @ Wm[keep]
        for k, j in enumerate(OTHER[i]):
            off[sel, j] = Eb[:, k]
            Bfull[:, :, i, j] = Wm[kick_cols.ravel(), k].reshape(C, 7)
    return {"off": off, "Bfull": Bfull}


# ------------------------------------------------------------------------------------------------ kick models
class KD:
    """Exposed rows (any lag bin 0..5 of any class) with offsets."""

    def __init__(self, d, off, rows=None):
        D = d["bits"][:, :, 1:]                                   # n x C x 6
        exp_ = D.reshape(d["n"], -1).any(1) if rows is None else rows
        self.idx = np.flatnonzero(exp_)
        self.fs = d["fs"][self.idx]
        self.y = d["y"][self.idx]
        self.off = off[self.idx]
        self.D = D[self.idx].astype(float)                        # m x C x 6
        self.day = d["day"][self.idx]
        self.ndays = int(d["day"].max()) + 1
        self.m = len(self.idx)
        self.by = [np.flatnonzero(self.fs == i) for i in range(3)]

    def nll_grad(self, B, w, extra=None):
        """B: C x 6 x 3 x 3. Returns (-ll, dB, per-row ll)."""
        C = B.shape[0]
        E = self.off.copy() if extra is None else self.off + extra
        G = np.zeros_like(B)
        llr = np.zeros(self.m)
        for i in range(3):
            r = self.by[i]
            if len(r) == 0:
                continue
            Di = self.D[r].reshape(len(r), -1)                    # r x (C*6)
            Bi = B[:, :, i, :].reshape(C * NL, 3)
            Ei = E[r] + Di @ Bi
            Ei[:, i] = 0.0
            mx = Ei.max(1, keepdims=True)
            P = np.exp(Ei - mx)
            Z = P.sum(1, keepdims=True)
            P /= Z
            yi = self.y[r]
            llr[r] = Ei[np.arange(len(r)), yi] - mx[:, 0] - np.log(Z[:, 0])
            R = -P
            R[np.arange(len(r)), yi] += 1
            R[:, i] = 0
            G[:, :, i, :] = (Di.T @ (w[r, None] * R)).reshape(C, NL, 3)
        return -(w * llr).sum(), -G, llr


def u_vec(th):
    return np.array([0.0, np.cos(th), np.sin(th)]), np.array([0.0, -np.sin(th), np.cos(th)])


class Lever:
    """Parameter vector -> B for a subset of classes. spec: per class (kappa_idx, h_idx, theta_idx); K idx 0..4."""

    def __init__(self, cls, kind, nclass_total=len(CLASSES)):
        self.cls = list(cls)             # class indices fitted
        self.kind = kind
        self.C = nclass_total
        k = 5                            # K_1..K_5
        self.th_shared = None
        self.map = {}
        if kind in ("lever", "delay"):
            self.th_shared = k
            k += 1
        if kind == "delay":
            for c in self.cls:
                self.map[c] = (k, k + 1, self.th_shared)
            k += 2
        else:
            for c in self.cls:
                if kind == "dir":
                    self.map[c] = (k, k + 1, k + 2)
                    k += 3
                else:
                    self.map[c] = (k, k + 1, self.th_shared)
                    k += 2
        self.P = k

    def init(self):
        v = np.zeros(self.P)
        v[:5] = 0.2
        for c, (a, b, t) in self.map.items():
            v[a], v[b], v[t] = 0.05, 0.3, np.pi / 4
        return v

    def B(self, v):
        Kf = np.r_[1.0, v[:5]]
        B = np.zeros((self.C, NL, 3, 3))
        for c, (a, b, t) in self.map.items():
            u, _ = u_vec(v[t])
            du = u[None, :] - u[:, None]                        # du[i, j] = u_j - u_i
            core = v[a] + v[b] * du / 2
            np.fill_diagonal(core, 0)
            B[c] = Kf[:, None, None] * core[None]
        return B

    def grad(self, v, G):
        Kf = np.r_[1.0, v[:5]]
        g = np.zeros(self.P)
        off = 1 - np.eye(3)
        for c, (a, b, t) in self.map.items():
            u, up = u_vec(v[t])
            du = (u[None, :] - u[:, None]) * off
            dup = (up[None, :] - up[:, None]) * off
            core = (v[a] + v[b] * du / 2) * off
            Gc = G[c]
            g[:5] += np.einsum("lij,ij->l", Gc, core)[1:]
            g[a] += np.einsum("lij,l,ij->", Gc, Kf, off)
            g[b] += np.einsum("lij,l,ij->", Gc, Kf, du / 2)
            g[t] += np.einsum("lij,l,ij->", Gc, Kf, v[b] * dup / 2)
        return g


def fit_param(kd: KD, model: Lever, w, extra=None, v0=None, fixed=None, ridge=0.1):
    """Fit model params (optionally with some fixed: dict idx -> value)."""
    v0 = model.init() if v0 is None else v0.copy()
    fixed = fixed or {}
    free = np.array([i for i in range(model.P) if i not in fixed], int)
    for i, val in fixed.items():
        v0[i] = val

    def f(x):
        v = v0.copy()
        v[free] = x
        nll, G, _ = kd.nll_grad(model.B(v), w, extra)
        g = model.grad(v, G)[free]
        return nll + 0.5 * ridge * (x ** 2).sum(), g + ridge * x
    r = minimize(f, v0[free], jac=True, method="L-BFGS-B", options={"maxiter": 500})
    v = v0.copy()
    v[free] = r.x
    return v


def fit_free(kd: KD, c, w, extra, ridge=1.0):
    """Free 6 x 6 off-diagonal betas for class c."""
    off = (1 - np.eye(3)).astype(bool)

    def tob(x):
        B = np.zeros((len(CLASSES), NL, 3, 3))
        B[c][:, off] = x.reshape(NL, 6)
        return B

    def f(x):
        nll, G, _ = kd.nll_grad(tob(x), w, extra)
        return nll + 0.5 * ridge * (x ** 2).sum(), G[c][:, off].ravel() + ridge * x
    r = minimize(f, np.zeros(NL * 6), jac=True, method="L-BFGS-B", options={"maxiter": 500})
    return tob(r.x)


def contrib(kd: KD, B):
    """Kick log-odds contribution (m x 3) of B."""
    E = np.zeros((kd.m, 3))
    C = B.shape[0]
    for i in range(3):
        r = kd.by[i]
        if len(r):
            E[r] = kd.D[r].reshape(len(r), -1) @ B[:, :, i, :].reshape(C * NL, 3)
            E[r, i] = 0
    return E


def powered(d, classes=None):
    out = []
    for ci, c in enumerate(CLASSES):
        if classes is not None and c not in classes:
            continue
        if int(d["bits"][:, ci, 1].sum()) >= MIN_REC:
            out.append(ci)
    return out


# ------------------------------------------------------------------------------------------------ LOCO
def loco(d, kd: KD, cls: list[int], nfold=5, nboot=200, seed=0):
    """Leave-one-class-out skill for each class in cls. Returns dict per class name."""
    rng = np.random.default_rng(seed)
    w1 = np.ones(kd.m)
    res = {}
    for c in cls:
        others = [o for o in cls if o != c]
        ex_c = kd.D[:, c, :].any(1)
        # step 1: shape from the other classes (rows exposed to them)
        lv = Lever(others, "lever")
        w_o = (kd.D[:, others, :].reshape(kd.m, -1).any(1)).astype(float)
        v_o = fit_param(kd, lv, w_o)
        dl = Lever(others, "delay")
        v_d = fit_param(kd, dl, w_o, v0=np.r_[v_o[:6], np.zeros(dl.P - 6)] if dl.P > 6 else None)
        extra_o = contrib(kd, lv.B(v_o))          # other classes' contribution, fixed (lever fit)
        K_o, th_o = v_o[:5], v_o[5]
        kap_d, h_d = v_d[6], v_d[7]
        # step 2: folds on c's rows
        fold = kd.day % nfold
        lls = {m: np.zeros(kd.m) for m in ("M0", "delay", "lever", "dir", "free")}
        pars = []
        for f in range(nfold):
            tr = (ex_c & (fold != f)).astype(float)
            te = ex_c & (fold == f)
            if tr.sum() < 20 or te.sum() == 0:
                continue
            # M0
            _, _, ll = kd.nll_grad(np.zeros((len(CLASSES), NL, 3, 3)), w1, extra_o)
            lls["M0"][te] = ll[te]
            # delay: c gets the pooled amplitude with the delay fit's own K, theta
            mdl = Lever([c], "delay")
            vd = np.r_[v_d[:6], kap_d, h_d]
            _, _, ll = kd.nll_grad(mdl.B(vd), w1, extra_o)
            lls["delay"][te] = ll[te]
            # lever: kappa_c, h_c with K, theta fixed from others
            ml = Lever([c], "lever")
            fx = {i: K_o[i] for i in range(5)}
            fx[5] = th_o
            vl = fit_param(kd, ml, tr, extra_o, fixed=fx)
            _, _, ll = kd.nll_grad(ml.B(vl), w1, extra_o)
            lls["lever"][te] = ll[te]
            pars.append(vl[6:8])
            # dir: kappa, h, theta_c with K fixed
            md = Lever([c], "dir")
            v0 = np.r_[K_o, vl[6], vl[7], th_o]
            vdi = fit_param(kd, md, tr, extra_o, v0=v0, fixed={i: K_o[i] for i in range(5)})
            _, _, ll = kd.nll_grad(md.B(vdi), w1, extra_o)
            lls["dir"][te] = ll[te]
            # free
            Bf = fit_free(kd, c, tr, extra_o)
            _, _, ll = kd.nll_grad(Bf, w1, extra_o)
            lls["free"][te] = ll[te]
        # per-day sums of skill
        days = kd.day[ex_c]
        S = {}
        perday = {}
        for m in ("delay", "lever", "dir", "free"):
            diff = lls[m][ex_c] - lls["M0"][ex_c]
            perday[m] = np.bincount(days, diff, minlength=kd.ndays)
            S[m] = float(diff.sum())
        nd = kd.ndays
        dd = np.flatnonzero(np.bincount(days, minlength=nd) > 0)
        boots = {k: [] for k in ("lever", "free", "delay", "dir", "free-lever", "lever-delay", "T")}
        for _ in range(nboot):
            s = rng.choice(dd, len(dd), replace=True)
            wv = np.bincount(s, minlength=nd)
            sv = {m: float((perday[m] * wv).sum()) for m in perday}
            for m in ("lever", "free", "delay", "dir"):
                boots[m].append(sv[m])
            boots["free-lever"].append(sv["free"] - sv["lever"])
            boots["lever-delay"].append(sv["lever"] - sv["delay"])
            boots["T"].append(sv["lever"] / sv["free"] if sv["free"] > 0 else np.nan)
        ci = {k: [float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5))] for k, v in boots.items()}
        early = kd.D[:, c, 0:3].any(1)[ex_c]
        split = {m: {"early": float((lls[m][ex_c] - lls["M0"][ex_c])[early].sum()),
                     "late": float((lls[m][ex_c] - lls["M0"][ex_c])[~early].sum())} for m in ("delay", "lever", "dir", "free")}
        T = S["lever"] / S["free"] if S["free"] > 0 else None
        res[CLASSES[c]] = {"n_rec": int(kd.D[:, c, 0].sum()), "n_rows": int(ex_c.sum()), "S": S, "ci": ci, "T": T, "split_early_late": split,
                           "shape_from_others": {"K": [1.0] + list(map(float, K_o)), "theta_deg": float(np.degrees(th_o))},
                           "delay_amp": [float(kap_d), float(h_d)],
                           "fold_kappa_h": [list(map(float, p)) for p in pars]}
    return res


def triples(kd: KD, cls: list[int], nboot=100, seed=1):
    """One-lever fit on all powered classes; day-block bootstrap (offsets fixed)."""
    lv = Lever(cls, "lever")
    w1 = np.ones(kd.m)
    v = fit_param(kd, lv, w1)
    rng = np.random.default_rng(seed)
    dd = np.unique(kd.day)
    draws = []
    for _ in range(nboot):
        s = rng.choice(dd, len(dd), replace=True)
        wd = np.bincount(s, minlength=kd.ndays).astype(float)
        draws.append(fit_param(kd, lv, wd[kd.day], v0=v))
    draws = np.array(draws)

    def summ(k):
        x = draws[:, k] if len(draws) else np.array([np.nan])
        return {"est": float(v[k]), "ci": [float(np.nanpercentile(x, 2.5)), float(np.nanpercentile(x, 97.5))]}
    out = {"K": [{"lag": LAG_LABELS[0], "est": 1.0, "ci": [1.0, 1.0]}] +
                [dict(lag=LAG_LABELS[i + 1], **summ(i)) for i in range(5)],
           "theta_deg": {"est": float(np.degrees(v[5])),
                         "ci": [float(np.degrees(np.nanpercentile(draws[:, 5], 2.5))),
                                float(np.degrees(np.nanpercentile(draws[:, 5], 97.5)))] if len(draws) else None}}
    for c in cls:
        a, b, _ = lv.map[c]
        out[CLASSES[c]] = {"kappa": summ(a), "h": summ(b)}
    return out, v, lv


def stale_test(d, kd: KD, cls, v, lv):
    """Lag-0 amplitude multiplier for stale reads (age above the class median) with everything else fixed."""
    B = lv.B(v)
    out = {}
    age = d["age0"][kd.idx]
    lag0 = kd.D[:, :, 0]
    base_extra = contrib(kd, B)
    for c in cls:
        a = age[:, c]
        rec = lag0[:, c] > 0
        if rec.sum() < 2 * MIN_REC:
            continue
        med = np.nanmedian(a[rec])
        stale = rec & (a > med)
        # lag-0 contribution of class c
        B0 = np.zeros_like(B)
        B0[c, 0] = B[c, 0]
        c0 = np.zeros((kd.m, 3))
        for i in range(3):
            r = kd.by[i]
            c0[r] = lag0[r, c][:, None] * B0[c, 0, i][None, :]
        lls = []
        grid = np.linspace(0, 2.5, 51)
        for g in grid:
            extra = base_extra + (g - 1) * c0 * stale[:, None]
            _, _, ll = kd.nll_grad(np.zeros_like(B), np.ones(kd.m), extra)
            lls.append(ll[rec].sum())
        lls = np.array(lls)
        k = int(np.argmax(lls))
        inside = grid[lls >= lls[k] - 1.92]
        out[CLASSES[c]] = {"median_age_s": float(med), "mult": float(grid[k]),
                           "ci_profile": [float(inside.min()), float(inside.max())], "n_stale": int(stale.sum())}
    return out
