"""H88 core: decay-model fits of post-period attention shares (Poisson quasi-likelihood with offsets), model
selection by QAIC, block bootstraps, and the pooled newcomer/veteran log-k slope contrast."""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy.optimize import minimize  # noqa: E402
from scipy.special import gammaln  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import holdout_mask  # noqa: E402

DATA = ROOT / "data/processed/H88-collective-memory-decay"
SH = ROOT / "data/processed/shared"
TAU_MIN, TAU_MAX = 0.2, 3000.0
MODELS = ("M1", "M2", "M1c", "MP")
NPAR = {"M1": 2, "M2": 4, "M1c": 3, "MP": 2}


def load_daily():
    d = pl.read_parquet(DATA / "daily.parquet")
    obs = d.filter(pl.col("observed"))
    assert not any(holdout_mask(obs["pt_date"].to_list(), [None] * obs.height))
    return d


def series(daily: pl.DataFrame, P: int, kind: str, group: str):
    s = daily.filter((pl.col("P") == P) & (pl.col("kind") == kind) & (pl.col("group") == group)
                     & pl.col("observed") & (pl.col("O") > 0)).sort("k")
    return s["k"].to_numpy().astype(float), s["y"].to_numpy().astype(float), s["O"].to_numpy().astype(float)


# ----------------------------------------------------------------------------- models
def f_of(model, th, k):
    if model == "M1":
        return np.exp(th[0] - k / np.exp(th[1]))
    if model == "M2":
        t1 = np.exp(th[1]); t2 = t1 + np.exp(th[3])
        return np.exp(th[0] - k / t1) + np.exp(th[2] - k / t2)
    if model == "M1c":
        return np.exp(th[0] - k / np.exp(th[1])) + np.exp(th[2])
    if model == "MP":
        return np.exp(th[0]) * k ** (-th[1])
    raise ValueError(model)


def nll(th, model, k, y, O):
    mu = O * np.clip(f_of(model, th, k), 1e-12, 1.0)
    return -(y * np.log(mu) - mu).sum()


def starts(model, k, y, O):
    s0 = max(y[:3].sum() / max(O[:3].sum(), 1), 1e-6)
    sl = max(y[-30:].sum() / max(O[-30:].sum(), 1), 1e-7)
    la = np.log(s0)
    out = []
    for lt in np.log([0.7, 2.0, 6.0, 20.0, 60.0]):
        if model == "M1":
            out.append([la, lt])
        elif model == "M2":
            for lt2 in np.log([10.0, 40.0, 150.0]):
                out.append([la, lt, np.log(sl) + 1, lt2])
        elif model == "M1c":
            out.append([la, lt, np.log(sl)])
    if model == "MP":
        out = [[la, a] for a in (0.3, 0.8, 1.5)]
    return out


def bounds(model):
    lt = (np.log(TAU_MIN), np.log(TAU_MAX))
    la = (-25, 0.5)
    return {"M1": [la, lt], "M2": [la, lt, la, (np.log(0.05), np.log(TAU_MAX))], "M1c": [la, lt, la],
            "MP": [la, (0.0, 5.0)]}[model]


def fit(model, k, y, O):
    best = None
    for s in starts(model, k, y, O):
        r = minimize(nll, np.array(s, float), args=(model, k, y, O), method="L-BFGS-B", bounds=bounds(model))
        if best is None or r.fun < best.fun:
            best = r
    return best


def fit_all(k, y, O):
    """All four models; QAIC with phi from the M2 Pearson chi2. Returns dict."""
    res = {m: fit(m, k, y, O) for m in MODELS}
    n = len(k)
    mu2 = O * f_of("M2", res["M2"].x, k)
    phi = max(float(((y - mu2) ** 2 / np.maximum(mu2, 1e-9)).sum() / max(n - 4, 1)), 1.0)
    const = -gammaln(y + 1).sum()
    out = {"n": n, "phi": phi, "models": {}}
    for m, r in res.items():
        ll = -r.fun + const
        out["models"][m] = {"ll": float(ll), "qaic": float(-2 * ll / phi + 2 * NPAR[m]), "theta": r.x.tolist()}
    q = {m: v["qaic"] for m, v in out["models"].items()}
    out["best"] = min(q, key=q.get)
    out["dq_M1_M2"] = q["M1"] - q["M2"]
    out["biexp"] = bool(out["best"] == "M2" and out["dq_M1_M2"] >= 2)
    th = res["M2"].x
    t1 = float(np.exp(th[1])); t2 = float(t1 + np.exp(th[3]))
    A1, A2 = float(np.exp(th[0])), float(np.exp(th[2]))
    out["M2_params"] = {"A1": A1, "tau1": t1, "A2": A2, "tau2": t2,
                        "slow_share": A2 * t2 / (A1 * t1 + A2 * t2)}
    th1 = res["M1"].x
    out["M1_params"] = {"A": float(np.exp(th1[0])), "tau": float(np.exp(th1[1]))}
    out["MP_params"] = {"A": float(np.exp(res["MP"].x[0])), "alpha": float(res["MP"].x[1])}
    thc = res["M1c"].x
    out["M1c_params"] = {"A": float(np.exp(thc[0])), "tau": float(np.exp(thc[1])), "c": float(np.exp(thc[2]))}
    return out


def block_boot_M2(k, y, O, B=200, block=5, seed=0):
    """Day-block bootstrap of (tau1, tau2, slow share) for M2."""
    rng = np.random.default_rng(seed)
    blocks = np.unique((k - 1) // block)
    idx = [np.flatnonzero((k - 1) // block == b) for b in blocks]
    out = []
    for _ in range(B):
        pick = np.concatenate([idx[i] for i in rng.integers(0, len(idx), len(idx))])
        kk, yy, oo = k[pick], y[pick], O[pick]
        o = np.argsort(kk, kind="stable")
        r = fit("M2", kk[o], yy[o], oo[o])
        th = r.x; t1 = np.exp(th[1]); t2 = t1 + np.exp(th[3]); A1, A2 = np.exp(th[0]), np.exp(th[2])
        out.append((t1, t2, A2 * t2 / (A1 * t1 + A2 * t2)))
    a = np.array(out)
    return {n: [float(np.quantile(a[:, i], .025)), float(np.quantile(a[:, i], .975))]
            for i, n in enumerate(("tau1", "tau2", "slow_share"))}


def share_ratio(k, y, O, early=(1, 3), late=(21, 40), B=2000, block=5, seed=0):
    """Share in k late / share in k early, day-block bootstrap."""
    def r(kk, yy, oo):
        e = (kk >= early[0]) & (kk <= early[1]); l_ = (kk >= late[0]) & (kk <= late[1])
        if oo[e].sum() == 0 or oo[l_].sum() == 0 or yy[e].sum() == 0:
            return np.nan
        return (yy[l_].sum() / oo[l_].sum()) / (yy[e].sum() / oo[e].sum())
    est = r(k, y, O)
    rng = np.random.default_rng(seed)
    # resample within the early and late windows separately (days are the units)
    e = np.flatnonzero((k >= early[0]) & (k <= early[1])); l_ = np.flatnonzero((k >= late[0]) & (k <= late[1]))
    if len(e) == 0 or len(l_) == 0:
        return {"ratio": None}
    bs = []
    for _ in range(B):
        pe = rng.choice(e, len(e)); pl_ = rng.choice(l_, len(l_))
        p = np.concatenate([pe, pl_])
        bs.append(r(k[p], y[p], O[p]))
    bs = np.array(bs); bs = bs[np.isfinite(bs)]
    return {"ratio": float(est), "ci": [float(np.quantile(bs, .025)), float(np.quantile(bs, .975))] if len(bs) else None,
            "n_early": int(len(e)), "n_late": int(len(l_))}


# ----------------------------------------------------------------------------- pooled newcomer slope (O3)
def pooled_b(rows: pl.DataFrame):
    """rows: P, group (vet|new), k, y, O. Poisson: log mu = log O + alpha_{P,g} + c_P log k + b * new * log k.
    Returns b (the newcomer minus veteran log-k slope)."""
    Ps = sorted(rows["P"].unique().to_list())
    pidx = {p: i for i, p in enumerate(Ps)}
    P_ = np.array([pidx[p] for p in rows["P"].to_list()])
    new = (rows["group"] == "new").to_numpy().astype(float)
    lk = np.log(rows["k"].to_numpy().astype(float))
    y = rows["y"].to_numpy().astype(float); O = rows["O"].to_numpy().astype(float)
    nP = len(Ps)
    g = (P_ * 2 + new.astype(int))

    def unpack(th):
        return th[:2 * nP], th[2 * nP:3 * nP], th[-1]

    def f(th):
        a, c, b = unpack(th)
        eta = np.log(O) + a[g] + c[P_] * lk + b * new * lk
        mu = np.exp(np.clip(eta, -50, 5))
        nl = -(y * eta - mu).sum()
        r_ = mu - y
        ga = np.bincount(g, weights=r_, minlength=2 * nP)
        gc = np.bincount(P_, weights=r_ * lk, minlength=nP)
        gb = (r_ * new * lk).sum()
        return nl, np.concatenate([ga, gc, [gb]])
    th0 = np.concatenate([np.full(2 * nP, np.log(max(y.sum() / O.sum(), 1e-6))), np.zeros(nP), [0.0]])
    r = minimize(f, th0, jac=True, method="L-BFGS-B")
    return float(r.x[-1]), r


def pooled_b_boot(rows: pl.DataFrame, B=500, seed=0):
    b, _ = pooled_b(rows)
    Ps = sorted(rows["P"].unique().to_list())
    rng = np.random.default_rng(seed)
    bs = []
    for _ in range(B):
        pick = rng.choice(Ps, len(Ps))
        parts = [rows.filter(pl.col("P") == p).with_columns(pl.lit(i).cast(pl.Int32).alias("P")) for i, p in enumerate(pick)]
        bs.append(pooled_b(pl.concat(parts))[0])
    return {"b": b, "ci": [float(np.quantile(bs, .025)), float(np.quantile(bs, .975))], "n_periods": len(Ps),
            "n_rows": rows.height}


# ----------------------------------------------------------------------------- O3 (Amendment A1): standardized ratio
BANDS = ((1, 10), (11, 40), (41, 120))


def _band_table(rows: pl.DataFrame, bands=BANDS):
    """Per period: observed and expected newcomer uses per band (expected = newcomer offset x veteran share)."""
    r = rows.with_columns(pl.lit(-1).alias("band"))
    for i, (lo, hi) in enumerate(bands):
        r = r.with_columns(pl.when((pl.col("k") >= lo) & (pl.col("k") <= hi)).then(i).otherwise(pl.col("band")).alias("band"))
    r = r.filter(pl.col("band") >= 0)
    # day-level standardization: newcomers' offsets sit late in a band, where the share is lower
    v = r.filter(pl.col("group") == "vet").select("P", "k", "band", pl.col("y").alias("yv"), pl.col("O").alias("Ov"))
    n = r.filter(pl.col("group") == "new").select("P", "k", pl.col("y").alias("yn"), pl.col("O").alias("On"))
    t = n.join(v, on=["P", "k"], how="inner").filter((pl.col("Ov") > 0) & (pl.col("On") > 0))
    t = t.with_columns((pl.col("On") * pl.col("yv") / pl.col("Ov")).alias("exp"))
    Ps = sorted(rows["P"].unique().to_list())
    obs = np.zeros((len(Ps), len(bands))); exp = np.zeros((len(Ps), len(bands)))
    pi = {p: i for i, p in enumerate(Ps)}
    for P, b, yn, e in t.select("P", "band", "yn", "exp").iter_rows():
        obs[pi[P], b] += yn; exp[pi[P], b] += e
    return Ps, obs, exp


def _rb(obs, exp, bands=BANDS):
    o, e = obs.sum(0), exp.sum(0)
    R = {f"{lo}-{hi}": (float(o[i] / e[i]) if e[i] > 0 else None) for i, (lo, hi) in enumerate(bands)}
    b = float(np.log(o[-1] / e[-1]) - np.log(o[0] / e[0])) if (e[0] > 0 and e[-1] > 0 and o[0] > 0 and o[-1] > 0) else None
    return R, b


def ratio_bands(rows: pl.DataFrame, bands=BANDS):
    """Indirect standardization: newcomers' observed uses over their expected uses at the veterans' share (same P,
    same age band), summed over P. b = log R(last band) - log R(first band)."""
    Ps, obs, exp = _band_table(rows, bands)
    R, b = _rb(obs, exp, bands)
    return {"R": R, "b": b, "per_P": {int(p): {"obs": obs[i].tolist(), "exp": exp[i].tolist()} for i, p in enumerate(Ps)}}


def ratio_bands_boot(rows: pl.DataFrame, B=2000, seed=0):
    Ps, obs, exp = _band_table(rows)
    R, b = _rb(obs, exp)
    rng = np.random.default_rng(seed)
    bs = []
    for _ in range(B):
        pick = rng.integers(0, len(Ps), len(Ps))
        _, bb = _rb(obs[pick], exp[pick])
        if bb is not None:
            bs.append(bb)
    return {"R": R, "b": b, "b_ci": [float(np.quantile(bs, .025)), float(np.quantile(bs, .975))] if bs else None,
            "n_periods": len(Ps)}
