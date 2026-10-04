"""H51 library: phase-diagram axes, observables, one-dial collapse scores, rivals and the within-regime permutation null.

Unit: goal period (non-holdout). All fits are across periods (points on a phase diagram), never on pooled events.
Collapse score: leave-one-period-out (LOPO) cross-validated R^2 relative to the LOPO mean (M0).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data/processed/H51-one-dial-collapse"
HYP = ROOT / "hypotheses/H51-one-dial-collapse"
sys.path.insert(0, str(ROOT / "infra" / "shared"))
from common import load_holdout  # noqa: E402

HELD = set(load_holdout()["goal_periods_held_out"])
OBS = ["Y1_settle", "Y2_herd", "Y3_branch", "Y4_loop"]
OBS_LABEL = {"Y1_settle": "settling time (log h)", "Y2_herd": "herding share", "Y3_branch": "idea branching (logit R)",
             "Y4_loop": "loop rate (logit)", "Y5_cons": "consensus time (log h)"}
AXES = ["K", "h", "kick", "logN"]
# collapse rule thresholds (card, written before data)
MIN_R2, MARGIN, RESID = 0.15, 0.05, 0.05


def logit(p):
    p = np.clip(np.asarray(p, float), 1e-4, 1 - 1e-4)
    return np.log(p / (1 - p))


def load(variant: str = "primary") -> pl.DataFrame:
    """One row per non-holdout goal period with axes and transformed observables.
    variant: primary | gte (Y1 gte) | calls (Y1 in calls) | h11 (Y2 = H11 rows) | both (Y4 both-model) | phi (h = phi)
             | h34tab (Y3 = H34 table values)"""
    ap = pl.read_parquet(DATA / "axes_periods.parquet")
    op = pl.read_parquet(DATA / "observables_periods.parquet")
    d = ap.join(op, on="goal_no", how="inner")
    assert not set(d["goal_no"].to_list()) & HELD
    tau = d["tau_settle_gte"] if variant == "gte" else d["tau_settle"]
    tau = tau.to_numpy().astype(float)
    if variant == "calls":
        tau = tau * 3600.0 / d["med_call_s"].to_numpy().astype(float)
    herd = d["herd"] if variant == "h11" else d["herd_own"]
    R = d["R_h34tab"] if variant == "h34tab" else d["R_hat"]
    loop = d["loop_rate_both"] if variant == "both" else d["loop_rate"]
    h = d["phi_trim"].to_numpy() if variant == "phi" else np.arcsinh(d["c_x_trim"].to_numpy() / 0.01)
    with np.errstate(divide="ignore", invalid="ignore"):
        out = d.select("goal_no", "regime", "N_active", "g_lag", "g_lag_se", "g_eq", "c_x_trim", "phi_trim", "S_text",
                       "f_sched", "med_call_s", "units", "n_days").with_columns(
            K=pl.col("g_lag"), h=pl.Series(h), kick=pl.col("S_text"), logN=pl.col("N_active").log(),
            Y1_settle=pl.Series(np.log(np.where(tau > 0, tau, np.nan))),
            Y2_herd=pl.Series(herd.to_numpy().astype(float)),
            Y3_branch=pl.Series(np.where(np.isfinite(R.to_numpy().astype(float)), logit(R.to_numpy().astype(float)), np.nan)),
            Y4_loop=pl.Series(np.where(np.isfinite(loop.to_numpy().astype(float)), logit(loop.to_numpy().astype(float)), np.nan)),
            Y5_cons=pl.Series(np.log(d["t_cons"].to_numpy().astype(float))))
    out = out.with_columns([pl.when(pl.col(c).is_nan()).then(None).otherwise(pl.col(c)).alias(c)
                            for c in OBS + ["Y5_cons", "h", "kick", "logN", "K"]])
    return out.sort("goal_no")


def regime_dummies(reg: np.ndarray) -> np.ndarray:
    levels = ["II", "III"]
    return np.column_stack([(reg == L).astype(float) for L in levels])


def zs(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, float)
    s = x.std()
    return (x - x.mean()) / (s if s > 0 else 1.0)


def lopo_r2(y: np.ndarray, X: np.ndarray | None) -> tuple[float, np.ndarray]:
    """LOPO CV R^2 of OLS y ~ 1 + X, relative to the LOPO mean. Returns (R2_cv, LOPO predictions)."""
    n = len(y)
    A = np.ones((n, 1)) if X is None else np.column_stack([np.ones(n), X])
    # closed-form leave-one-out residuals e_i / (1 - h_ii) (pseudo-inverse handles empty dummy columns)
    P = A @ np.linalg.pinv(A)
    e = y - P @ y
    hii = np.clip(np.diag(P), None, 1 - 1e-9)
    pred = y - e / (1 - hii)
    base = (y.sum() - y) / (n - 1)
    sse, sst = np.sum((y - pred) ** 2), np.sum((y - base) ** 2)
    return (1 - sse / sst if sst > 0 else np.nan), pred


def in_r2(y: np.ndarray, x: np.ndarray) -> float:
    """In-sample R^2 of y on one regressor (squared Pearson correlation)."""
    yc, xc = y - y.mean(), x - x.mean()
    den = np.sqrt((yc @ yc) * (xc @ xc))
    return float((yc @ xc / den) ** 2) if den > 0 else 0.0


def fit_index(Z: dict[str, np.ndarray], Ys: dict[str, np.ndarray], masks: dict[str, np.ndarray], starts: int = 8,
              seed: int = 0) -> np.ndarray:
    """Shared single-index direction w (|w| = 1) maximizing the mean in-sample R^2 of each Y_k on u = Z w.
    Z: (n, p) standardized axes on the common sample; Ys/masks per observable."""
    from scipy.optimize import minimize
    rng = np.random.default_rng(seed)
    Zm = Z["Z"]

    def obj(v):
        w = v / (np.linalg.norm(v) + 1e-12)
        u = Zm @ w
        return -np.mean([in_r2(Ys[k], u[masks[k]]) for k in Ys])

    best = None
    for s in range(starts):
        v0 = rng.normal(size=Zm.shape[1])
        r = minimize(obj, v0, method="Nelder-Mead", options={"xatol": 1e-4, "fatol": 1e-6, "maxiter": 2000})
        if best is None or r.fun < best.fun:
            best = r
    w = best.x / np.linalg.norm(best.x)
    return w * np.sign(w[0]) if w[0] != 0 else w


def common_sample(d: pl.DataFrame) -> pl.DataFrame:
    return d.filter(pl.all_horizontal([pl.col(a).is_not_null() for a in AXES]))


def model_matrices(d: pl.DataFrame) -> dict[str, np.ndarray | None]:
    reg = regime_dummies(d["regime"].to_numpy())
    K = d["K"].to_numpy().astype(float)
    return {"M0": None, "regime": reg, "logN": d["logN"].to_numpy()[:, None], "K": K[:, None],
            "K2": np.column_stack([K, K ** 2]), "field": np.column_stack([d["h"].to_numpy(), d["kick"].to_numpy()]),
            "g_eq": d["g_eq"].to_numpy()[:, None], "K+regime": np.column_stack([K, reg]),
            "regime+logN": np.column_stack([reg, d["logN"].to_numpy()])}


def collapse_scores(d: pl.DataFrame, obs: list[str] = OBS, index: bool = True, seed: int = 0) -> dict:
    """Per observable: LOPO CV-R^2 for every model, the single-index dial (direction from the other observables),
    and the collapse-rule verdicts for D1 = K and D2 = index."""
    d = common_sample(d)
    Zfull = np.column_stack([zs(d[a].to_numpy()) for a in AXES])
    out = {}
    for j in obs:
        m = d[j].is_not_null().to_numpy()
        y = d[j].to_numpy().astype(float)[m]
        mats = model_matrices(d.filter(pl.Series(m)))
        r = {k: lopo_r2(y, X)[0] for k, X in mats.items()}
        res = {"n": int(m.sum()), "cv_r2": r}
        if index:
            others = [k for k in obs if k != j]
            Ys = {k: d[k].to_numpy().astype(float)[d[k].is_not_null().to_numpy()] for k in others}
            Ys = {k: zs(v) for k, v in Ys.items()}
            masks = {k: d[k].is_not_null().to_numpy() for k in others}
            w = fit_index({"Z": Zfull}, Ys, masks, seed=seed)
            u = (Zfull @ w)[m]
            reg = regime_dummies(d.filter(pl.Series(m))["regime"].to_numpy())
            r["index"] = lopo_r2(y, u[:, None])[0]
            r["index+regime"] = lopo_r2(y, np.column_stack([u, reg]))[0]
            res["w"] = dict(zip(AXES, map(float, w)))
            res["u"] = u.tolist()
        rival = max(r["regime"], r["logN"])
        res["collapse_K"] = bool(r["K"] >= MIN_R2 and r["K"] >= rival + MARGIN and r["K+regime"] - r["K"] <= RESID)
        if index:
            res["collapse_index"] = bool(r["index"] >= MIN_R2 and r["index"] >= rival + MARGIN
                                         and r["index+regime"] - r["index"] <= RESID)
        out[j] = res
    return out


def perm_stat(d: pl.DataFrame, dial: str = "K", obs: list[str] = OBS, n_perm: int = 2000, seed: int = 1,
              dial_values: dict[str, np.ndarray] | None = None) -> dict:
    """Within-regime permutation null for T = sum_j [CV-R^2(dial + regime) - CV-R^2(regime)]."""
    d = common_sample(d)
    rng = np.random.default_rng(seed)
    reg_all = d["regime"].to_numpy()

    def T_of(x_all):
        t = 0.0
        parts = {}
        for j in obs:
            m = d[j].is_not_null().to_numpy()
            y = d[j].to_numpy().astype(float)[m]
            reg = regime_dummies(reg_all[m])
            x = x_all[j][m] if isinstance(x_all, dict) else x_all[m]
            a = lopo_r2(y, np.column_stack([x, reg]))[0] - lopo_r2(y, reg)[0]
            parts[j] = a
            t += a
        return t, parts

    x0 = dial_values if dial_values is not None else d[dial].to_numpy().astype(float)
    T0, parts0 = T_of(x0)
    groups = [np.flatnonzero(reg_all == L) for L in np.unique(reg_all)]
    Ts = []
    for _ in range(n_perm):
        perm = np.arange(len(reg_all))
        for gidx in groups:
            perm[gidx] = rng.permutation(gidx)
        xp = {k: v[perm] for k, v in x0.items()} if isinstance(x0, dict) else x0[perm]
        Ts.append(T_of(xp)[0])
    Ts = np.array(Ts)
    return {"T": float(T0), "parts": parts0, "p": float((1 + np.sum(Ts >= T0)) / (1 + len(Ts))),
            "null_mean": float(Ts.mean()), "null_q95": float(np.quantile(Ts, 0.95))}


def jdump(obj, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)))
