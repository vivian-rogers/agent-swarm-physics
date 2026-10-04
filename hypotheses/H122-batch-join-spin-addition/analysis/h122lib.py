"""H122 estimators: per-call logistic kinetic-Ising models for incumbents around a join, cross-fitted in time
(PRE + F37 fit, P12 scored), paired block bootstrap of log-loss differences, coupling stability, response trajectory,
and the outcome simulator on real event skeletons (axis F).

Input frame: data/processed/H122-batch-join-spin-addition/calls/<event>.parquet (scheme/build.py). win: 0 PRE,
1 P12, 2 F37.
"""
from __future__ import annotations

import numpy as np
import polars as pl

BETA_DIL = 0.66          # H18 dilution exponent (swarm-constants)
CLIP = 10                # counts are clipped at 10 (leverage)
RIDGE_FE = 1.0           # weak ridge on the agent x class baselines (separation in rare classes)
RIDGE_COV = 0.1          # weak ridge on covariates (A1: separation in small regime-I PRE windows)

COV0 = ["Rm_I", "Ro_I", "P_I", "E_h", "E_n", "E_nme", "Yprev", "lk", "lk2"]
READ_COV = ["Rm_I", "Ro_I", "P_I"]


def prep(df: pl.DataFrame) -> pl.DataFrame:
    cl = lambda c: pl.col(c).clip(0, CLIP).cast(pl.Float64)  # noqa: E731
    return df.with_columns(
        [cl(c) for c in ("Rm_I", "Ro_I", "P_I", "Rm_N", "Ro_N", "P_N", "RN_named", "RN_unnamed", "PN_named",
                         "E_h", "E_n", "E_nme")]
        + [(pl.col("Rm_N") + pl.col("Ro_N")).clip(0, CLIP).cast(pl.Float64).alias("RN"),
           (pl.col("k") + 1).log().alias("lk"), ((pl.col("k") + 1).log() ** 2).alias("lk2"),
           pl.col("Yprev").cast(pl.Float64),
           (pl.col("agent").cast(pl.Int32) * 4 + pl.col("cls").cast(pl.Int32)).alias("fe")])


def _sig(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -30, 30)))


def _pll(X, y, off, R, b):
    eta = X @ b + off
    return float(np.sum(y * eta - np.logaddexp(0, eta)) - 0.5 * np.sum(R * b * b))


def irls(X: np.ndarray, y: np.ndarray, offset: np.ndarray | None = None, ridge: np.ndarray | None = None,
         iters: int = 60, tol: float = 1e-8):
    """Penalized Newton with step halving (guards against separation; A1)."""
    n, p = X.shape
    off = np.zeros(n) if offset is None else offset
    R = np.zeros(p) if ridge is None else ridge
    b = np.zeros(p)
    ll = _pll(X, y, off, R, b)
    for _ in range(iters):
        eta = X @ b + off
        mu = _sig(eta)
        w = np.maximum(mu * (1 - mu), 1e-9)
        g = X.T @ (y - mu) - R * b
        H = (X * w[:, None]).T @ X + np.diag(R)
        try:
            step = np.linalg.solve(H, g)
        except np.linalg.LinAlgError:
            step = np.linalg.lstsq(H, g, rcond=None)[0]
        t = 1.0
        while t > 1e-4:
            ll_new = _pll(X, y, off, R, b + t * step)
            if ll_new >= ll - 1e-10:
                break
            t /= 2
        b = b + t * step
        conv = abs(ll_new - ll) < 1e-9 * max(1.0, abs(ll)) or np.max(np.abs(t * step)) < tol
        ll = ll_new
        if conv:
            break
    return b


def irls1(x: np.ndarray, y: np.ndarray, offset: np.ndarray, iters: int = 40) -> float:
    """One coefficient (no intercept) with offset; Newton."""
    b = 0.0
    for _ in range(iters):
        mu = _sig(offset + b * x)
        g = float(np.sum(x * (y - mu))) - RIDGE_COV * b
        h = float(np.sum(x * x * mu * (1 - mu))) + RIDGE_COV
        st = float(np.clip(g / h, -2.0, 2.0))
        b += st
        if abs(st) < 1e-9:
            break
    return b


def irls2(X: np.ndarray, y: np.ndarray, offset: np.ndarray) -> np.ndarray:
    return irls(X, y, offset, ridge=np.full(X.shape[1], RIDGE_COV))


class M0:
    """PRE fit: agent x class baselines + incumbent-class reads, placebo, exogenous, persistence, boot transient."""

    def __init__(self, pre: pl.DataFrame):
        self.fe_levels = np.sort(pre["fe"].unique().to_numpy())
        self.fe_ix = {v: i for i, v in enumerate(self.fe_levels)}
        X, y = self._X(pre), pre["Y"].to_numpy().astype(float)
        nf = len(self.fe_levels)
        ridge = np.r_[np.full(nf, RIDGE_FE), np.full(len(COV0), RIDGE_COV)]
        # FE ridge shrinks toward 0 in logit: centre with a global intercept first
        self.c0 = float(np.log(max(y.mean(), 1e-4) / max(1 - y.mean(), 1e-4)))
        self.b = irls(X, y, offset=np.full(len(y), self.c0), ridge=ridge)
        self.nf = nf
        # agent-level fallback for an incumbent x class unseen in PRE: the agent's mean FE
        self.agent_fe = {}
        for v, i in self.fe_ix.items():
            self.agent_fe.setdefault(v // 4, []).append(self.b[i])

    def _X(self, df: pl.DataFrame) -> np.ndarray:
        fe = df["fe"].to_numpy()
        D = np.zeros((df.height, len(self.fe_levels)))
        for j, v in enumerate(fe):
            i = self.fe_ix.get(v)
            if i is not None:
                D[j, i] = 1.0
        C = df.select(COV0).to_numpy().astype(float)
        return np.hstack([D, C])

    def eta(self, df: pl.DataFrame, dil: float = 1.0, newcomer_as_incumbent: bool = False) -> np.ndarray:
        fe = df["fe"].to_numpy()
        base = np.array([self.b[self.fe_ix[v]] if v in self.fe_ix else
                         (np.mean(self.agent_fe[v // 4]) if v // 4 in self.agent_fe else 0.0) for v in fe])
        cov = dict(zip(COV0, self.b[self.nf:]))
        z = self.c0 + base
        for c in COV0:
            coef = cov[c] * (dil if c in READ_COV else 1.0)
            z = z + coef * df[c].to_numpy()
        if newcomer_as_incumbent:
            z = z + dil * (cov["Rm_I"] * df["Rm_N"].to_numpy() + cov["Ro_I"] * df["Ro_N"].to_numpy()
                           + cov["P_I"] * df["P_N"].to_numpy())
        return z

    def coefs(self) -> dict:
        return dict(zip(COV0, map(float, self.b[self.nf:])))


def logloss(y: np.ndarray, z: np.ndarray) -> np.ndarray:
    p = np.clip(_sig(z), 1e-9, 1 - 1e-9)
    return -(y * np.log(p) + (1 - y) * np.log(1 - p))


def dil_factor(N_post: float, N_pre: float) -> float:
    if not (N_post and N_pre):
        return 1.0
    return float((N_post / N_pre) ** (-BETA_DIL))


def fit_models(df: pl.DataFrame, N: dict) -> dict:
    """Fit every model on PRE + F37 and return the P12 linear predictors (and fitted parameters)."""
    pre, p12, f37 = (df.filter(pl.col("win") == w) for w in (0, 1, 2))
    m0 = M0(pre)
    f_f37, f_p12 = dil_factor(N[2], N[0]), dil_factor(N[1], N[0])
    yF = f37["Y"].to_numpy().astype(float)
    eF0, eF = m0.eta(f37), m0.eta(f37, f_f37)
    eP0, eP = m0.eta(p12), m0.eta(p12, f_p12)
    RN_F, RN_P = f37["RN"].to_numpy(), p12["RN"].to_numpy()
    PN_F, PN_P = f37["P_N"].to_numpy(), p12["P_N"].to_numpy()
    par = {"pre": m0.coefs(), "dil_f37": f_f37, "dil_p12": f_p12}
    delta = irls1(np.ones_like(yF), yF, eF)
    J = irls1(RN_F, yF, eF) if RN_F.sum() > 0 else 0.0
    JP = irls1(PN_F, yF, eF) if PN_F.sum() > 0 else 0.0
    bc = irls2(np.c_[np.ones_like(yF), RN_F], yF, eF)
    Xn = np.c_[f37["RN_named"].to_numpy(), f37["RN_unnamed"].to_numpy()]
    bn = irls2(Xn, yF, eF) if Xn.sum() > 0 else np.zeros(2)
    par.update(delta=delta, J_N=J, J_P=JP, delta_c=float(bc[0]), J_c=float(bc[1]), J_named=float(bn[0]),
               J_unnamed=float(bn[1]))
    Z = {"M0": eP0, "M0D": eP, "MC": eP + delta, "MJ": eP + J * RN_P, "MJC": eP + bc[0] + bc[1] * RN_P,
         "MJ_pl": eP + JP * PN_P, "M_same": m0.eta(p12, f_p12, newcomer_as_incumbent=True),
         "MJn": eP + bn[0] * p12["RN_named"].to_numpy() + bn[1] * p12["RN_unnamed"].to_numpy()}
    # stability: J fitted on P12 itself (same offset)
    yP = p12["Y"].to_numpy().astype(float)
    par["J_N_p12"] = irls1(RN_P, yP, eP) if RN_P.sum() > 0 else 0.0
    par["delta_p12"] = irls1(np.ones_like(yP), yP, eP)
    par["mean_RN_p12"], par["mean_RN_f37"] = float(RN_P.mean()), float(RN_F.mean())
    par["sd_RN_p12"] = float(RN_P.std())
    par["mean_p_p12"] = float(_sig(eP).mean())
    return {"Z": Z, "par": par, "y": yP, "blocks": block_ids(p12), "p12": p12, "m0": m0, "eF": eF}


def block_ids(p12: pl.DataFrame) -> np.ndarray:
    b = p12.select(pl.struct("agent", "pt_date", "hour").rank("dense").alias("b"))["b"].to_numpy()
    return b - 1


def paired_boot(loss_a: np.ndarray, loss_b: np.ndarray, blocks: np.ndarray, B: int = 2000, seed: int = 0):
    """Mean (loss_a - loss_b) per call x 1000 and a percentile CI from a block bootstrap."""
    d = loss_a - loss_b
    nb = blocks.max() + 1
    s = np.bincount(blocks, weights=d, minlength=nb)
    n = np.bincount(blocks, minlength=nb).astype(float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, nb, size=(B, nb))
    est = 1000 * s.sum() / n.sum()
    bs = 1000 * s[idx].sum(1) / n[idx].sum(1)
    return float(est), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def scores(fit: dict, B: int = 2000, seed: int = 0) -> dict:
    y, Z, bl = fit["y"], fit["Z"], fit["blocks"]
    L = {k: logloss(y, z) for k, z in Z.items()}
    out = {f"LL_{k}": float(1000 * v.mean()) for k, v in L.items()}
    for name, a, b in (("C_J", "MC", "MJ"), ("PL_J", "MJ_pl", "MJ"), ("SAME_J", "M_same", "MJ"),
                       ("M0_M0D", "M0", "M0D"), ("M0D_J", "M0D", "MJ"), ("C_JC", "MC", "MJC"), ("J_Jn", "MJ", "MJn"),
                       ("M0D_C", "M0D", "MC")):
        e, lo, hi = paired_boot(L[a], L[b], bl, B, seed)
        out[f"d_{name}"], out[f"d_{name}_lo"], out[f"d_{name}_hi"] = e, lo, hi
    return out


def trajectory(fit: dict) -> dict:
    p12 = fit["p12"]
    Z = fit["Z"]
    hb = p12.select(pl.struct("pt_date", "hour").rank("dense").alias("h"))["h"].to_numpy() - 1
    nh = hb.max() + 1
    n = np.bincount(hb, minlength=nh).astype(float)
    ok = n >= 30
    mean = lambda v: np.bincount(hb, weights=v, minlength=nh) / np.maximum(n, 1)  # noqa: E731
    p0 = mean(_sig(Z["M0D"]))
    r = mean(fit["y"]) - p0
    out = {"n_hours": int(ok.sum())}
    for k in ("MC", "MJ", "MJC", "M_same"):
        rh = mean(_sig(Z[k])) - p0
        ss = np.sum((r[ok]) ** 2)
        out[f"R2h_{k}"] = float(1 - np.sum((r[ok] - rh[ok]) ** 2) / ss) if ss > 0 else np.nan
    out["resp_mean"] = float(np.sum(r[ok] * n[ok]) / np.sum(n[ok])) if ok.any() else np.nan
    return out


def boot_params(df: pl.DataFrame, N: dict, B: int = 200, seed: int = 0) -> dict:
    """Block bootstrap (agent x day x hour) of the F37 and P12 one-parameter fits, PRE model held fixed."""
    rng = np.random.default_rng(seed)
    fit = fit_models(df, N)
    m0 = fit["m0"]
    f37 = df.filter(pl.col("win") == 2)
    p12 = fit["p12"]
    eF = fit["eF"]
    eP = fit["Z"]["M0D"]
    out = {k: [] for k in ("J_N", "J_N_p12", "delta", "J_named", "J_unnamed", "ratio")}
    bF = f37.select(pl.struct("agent", "pt_date", "hour").rank("dense").alias("b"))["b"].to_numpy() - 1
    bP = fit["blocks"]
    yF, yP = f37["Y"].to_numpy().astype(float), fit["y"]
    RF, RP = f37["RN"].to_numpy(), p12["RN"].to_numpy()
    XnF = np.c_[f37["RN_named"].to_numpy(), f37["RN_unnamed"].to_numpy()]
    for _ in range(B):
        sF = np.concatenate([np.where(bF == i)[0] for i in rng.integers(0, bF.max() + 1, bF.max() + 1)])
        sP = np.concatenate([np.where(bP == i)[0] for i in rng.integers(0, bP.max() + 1, bP.max() + 1)])
        j = irls1(RF[sF], yF[sF], eF[sF]) if RF[sF].sum() > 0 else 0.0
        jp = irls1(RP[sP], yP[sP], eP[sP]) if RP[sP].sum() > 0 else 0.0
        out["J_N"].append(j); out["J_N_p12"].append(jp)
        out["delta"].append(irls1(np.ones(len(sF)), yF[sF], eF[sF]))
        bn = irls2(XnF[sF], yF[sF], eF[sF]) if XnF[sF].sum() > 0 else np.zeros(2)
        out["J_named"].append(bn[0]); out["J_unnamed"].append(bn[1])
        out["ratio"].append(jp / j if abs(j) > 1e-6 else np.nan)
    q = {}
    for k, v in out.items():
        v = np.array(v, float)
        q[f"{k}_lo"], q[f"{k}_hi"] = float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5))
    return q


# ------------------------------------------------------------------ simulator (axis F)
def simulate(df: pl.DataFrame, N: dict, m0: M0, rng, J: float = 0.0, delta: float = 0.0) -> pl.DataFrame:
    """Simulate Y on the real skeleton: logit = M0 (true PRE params, dilution in post windows) + planted J * RN +
    delta in P12 and F37; Yprev is regenerated sequentially per agent-day."""
    d = df.sort("agent", "pt_date", "k")
    win = d["win"].to_numpy()
    dil = np.where(win == 0, 1.0, np.where(win == 1, dil_factor(N[1], N[0]), dil_factor(N[2], N[0])))
    cov = m0.coefs()
    # linear predictor without the Yprev term, per row (dilution applied per window)
    base = np.zeros(d.height)
    for w in (0, 1, 2):
        s = win == w
        if s.any():
            sub = d.filter(pl.col("win") == w).with_columns(pl.lit(0.0).alias("Yprev"))
            base[s] = m0.eta(sub, float(dil[s][0]))
    base = base + np.where(win > 0, delta + J * d["RN"].to_numpy(), 0.0)
    ad = d.select(pl.struct("agent", "pt_date").rank("dense").alias("a"))["a"].to_numpy()
    k = d["k"].to_numpy()
    y = np.zeros(d.height)
    yprev = np.zeros(d.height)
    order = np.lexsort((k, ad))
    last = {}
    rho = cov["Yprev"]
    for i in order:
        a = ad[i]
        yp = last.get(a, 0.0)
        yprev[i] = yp
        y[i] = 1.0 if rng.random() < _sig(base[i] + rho * yp) else 0.0
        last[a] = y[i]
    return d.with_columns(pl.Series("Y", y.astype(np.int8)), pl.Series("Yprev", yprev))
