"""H72 estimator: two-clock discrete-time escape hazard at idle gates, agent fixed effects, day-block bootstrap,
day-blocked cross-validation. Shared fitting code: infra/shared/hazard_fe.py."""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "4")

import sys
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
import hazard_fe as HF  # noqa: E402

OUT = ROOT / "data/processed/H72-trap-aging-input-starvation"
FLOOR = 10.0
MIN_EVENTS = 30
B_PRIMARY = 200
B_VARIANT = 100


def lmin(x):
    return np.log(np.maximum(np.asarray(x, dtype=float), FLOOR) / 60.0)


def prep(df: pl.DataFrame, outcome: str = "sus", s_var: str = "novel") -> dict:
    """Arrays for one period. outcome 'sus' pairs with a_sus, 'any' with a_any."""
    a_col = "a_sus" if outcome == "sus" else "a_any"
    y_col = "y_sus" if outcome == "sus" else "y_any"
    d = df.filter(pl.col(y_col).is_not_null() & pl.col(a_col).is_not_null())
    y = d[y_col].cast(pl.Float64).to_numpy()
    la = lmin(d[a_col].to_numpy())
    s_none = d[f"s_{s_var}_none"].to_numpy()
    s_raw = np.where(s_none, d["s_lc"].fill_null(FLOOR).to_numpy(), d[f"s_{s_var}"].fill_null(FLOOR).to_numpy())
    ls = lmin(s_raw)
    n_dir = d["n_dir"].to_numpy().astype(float)
    n_nov = d["n_novel"].to_numpy().astype(float)
    nuis = {
        "cur_dir": np.log1p(n_dir),
        "cur_other": np.log1p(np.maximum(n_nov - n_dir, 0)),
        "cur_nudge": (d["n_nudge_me"].to_numpy() > 0).astype(float),
        "cur_bookend": (d["n_bookend"].to_numpy() > 0).astype(float),
        "swarm_act10": d["swarm_act10"].fill_null(0).to_numpy().astype(float),
        "ln_last_run": np.log(np.maximum(d["last_run_len"].fill_null(1).to_numpy().astype(float), 1)),
    }
    # previous-call declared duration bins (reference: pause <= 60 s)
    pk = d["prev_kind"].to_numpy()
    ps = d["prev_pause_s"].to_numpy().astype(float)
    nuis["prev_wait"] = (pk == "wait").astype(float)
    nuis["pause_nodur"] = ((pk == "pause") & ~np.isfinite(ps)).astype(float)
    for lo, hi, nm in ((60, 300, "p60_300"), (300, 1800, "p300_1800"), (1800, np.inf, "p1800")):
        nuis[nm] = ((pk == "pause") & (ps > lo) & (ps <= hi)).astype(float)
    hd = np.clip(np.floor(d["h_day"].fill_null(0).to_numpy()), 0, 6)
    for h in range(1, 7):
        nuis[f"hday{h}"] = (hd == h).astype(float)
    if s_none.any():
        nuis["s_none"] = s_none.astype(float)
    # drop constant nuisance columns
    nuis = {k: v for k, v in nuis.items() if np.std(v) > 0}
    days = d["pt_date"].to_numpy()
    _, day_codes = np.unique(days, return_inverse=True)
    return {"y": y, "la": la, "ls": ls, "nuis": nuis, "agent": d["agent"].to_numpy(), "day": day_codes,
            "days": days, "inflight": np.log1p(d["n_inflight_call"].to_numpy().astype(float)),
            "h_day": d["h_day"].fill_null(0).to_numpy(), "first_day": days == days.min(), "n": len(y),
            "room": d["room"].fill_null(-1).to_numpy()}


def build_X(P: dict, terms: tuple, idx=None, extra: dict | None = None):
    cols, names = [], []
    for t in terms:
        cols.append(P[t]); names.append(t)
    for k, v in P["nuis"].items():
        cols.append(v); names.append(k)
    for k, v in (extra or {}).items():
        cols.append(v); names.append(k)
    C = np.column_stack(cols)
    ag = P["agent"]
    if idx is not None:
        C, ag = C[idx], ag[idx]
    X, nm = HF.design(C, names, ag)
    return X, nm


def coef(fit, names, term):
    j = names.index(term)
    return float(fit["beta"][j]), float(np.sqrt(fit["cov"][j, j]))


def fit_terms(P, terms, idx=None, link="logit", extra=None, beta0=None):
    X, nm = build_X(P, terms, idx, extra)
    y = P["y"] if idx is None else P["y"][idx]
    # drop all-zero columns (e.g., an agent absent from a bootstrap draw)
    keep = np.r_[True, X[:, 1:].std(axis=0) > 0]
    f = HF.fit_binary(X[:, keep], y, link=link, beta0=None if beta0 is None else beta0)
    nm2 = [n for n, k in zip(nm, keep) if k]
    return f, nm2


MODELS = {"a0": ("la",), "as": ("la", "ls"), "s0": ("ls",)}


def point(P, link="logit", extra=None):
    out = {}
    for m, terms in MODELS.items():
        f, nm = fit_terms(P, terms, link=link, extra=extra if m == "as" else None)
        out[m] = (f, nm)
    b_a0, se_a0 = coef(*out["a0"], "la")
    b_a, se_a = coef(*out["as"], "la")
    b_s, se_s = coef(*out["as"], "ls")
    b_s0, se_s0 = coef(*out["s0"], "ls")
    r = {"beta_a0": b_a0, "se_a0": se_a0, "beta_a": b_a, "se_a": se_a, "beta_s": b_s, "se_s": se_s,
         "beta_s0": b_s0, "se_s0": se_s0, "rho": 1 - b_a / b_a0 if b_a0 != 0 else np.nan,
         "converged": all(o[0]["converged"] for o in out.values())}
    if extra:
        for k in extra:
            r[f"beta_{k}"], r[f"se_{k}"] = coef(*out["as"], k)
    return r


def bootstrap(P, B, seed=0, link="logit"):
    rng = np.random.default_rng(seed)
    rpd = HF.rows_per_day(P["day"])
    draws = []
    for _ in range(B):
        idx = HF.block_resample(P["day"], rng, rpd)
        try:
            fa0, na0 = fit_terms(P, MODELS["a0"], idx, link)
            fas, nas = fit_terms(P, MODELS["as"], idx, link)
            ba0 = coef(fa0, na0, "la")[0]
            ba = coef(fas, nas, "la")[0]
            bs = coef(fas, nas, "ls")[0]
            draws.append((ba0, ba, bs, 1 - ba / ba0 if ba0 != 0 else np.nan))
        except Exception:
            continue
    D = np.array(draws)
    q = lambda c: [float(np.nanpercentile(D[:, c], 2.5)), float(np.nanpercentile(D[:, c], 97.5))]  # noqa: E731
    return {"ci_a0": q(0), "ci_a": q(1), "ci_s": q(2), "ci_rho": q(3), "n_draws": int(len(D)),
            "draws": D.tolist()}


def cv_ll(P, k=5, link="logit"):
    """Day-blocked CV: per-day held-out log-lik for models a0, as, s0 (agent FE; unseen agents get the reference)."""
    folds = HF.interleaved_folds(P["day"], k)
    per_day = {m: np.zeros(P["day"].max() + 1) for m in MODELS}
    for f in range(k):
        tr = np.flatnonzero(folds != f)
        te = np.flatnonzero(folds == f)
        for m, terms in MODELS.items():
            Xtr, nm = build_X(P, terms, tr)
            keep = np.r_[True, Xtr[:, 1:].std(axis=0) > 0]
            fit = HF.fit_binary(Xtr[:, keep], P["y"][tr], link=link)
            beta = np.zeros(Xtr.shape[1]); beta[keep] = fit["beta"]
            # test design with the same agent columns
            Xall, nm_all = build_X(P, terms)
            Xte = Xall[te]
            # map columns: build_X on all rows has all agents; training design may lack some agents
            col = {n: i for i, n in enumerate(nm)}
            b_full = np.array([beta[col[n]] if n in col else 0.0 for n in nm_all])
            ll = HF.loglik_binary(Xte, P["y"][te], b_full, link)
            np.add.at(per_day[m], P["day"][te], ll)
    return per_day


def cv_summary(per_day, B=1000, seed=0):
    rng = np.random.default_rng(seed)
    nd = len(per_day["as"])
    s_add = per_day["as"] - per_day["a0"]
    a_add = per_day["as"] - per_day["s0"]
    out = {}
    for nm, v in (("s_adds", s_add), ("a_adds", a_add)):
        bs = [v[rng.integers(0, nd, nd)].sum() for _ in range(B)]
        out[nm] = float(v.sum())
        out[nm + "_ci"] = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
    return out


def kappa(P, idx=None):
    """Within-agent OLS slope of ln s on ln a with the nuisance terms (for the starvation-implied aging)."""
    cols = [P["la"]] + list(P["nuis"].values())
    C = np.column_stack(cols)
    ag = P["agent"]
    y = P["ls"]
    if idx is not None:
        C, ag, y = C[idx], ag[idx], y[idx]
    X, _ = HF.design(C, ["la"] + list(P["nuis"].keys()), ag)
    keep = np.r_[True, X[:, 1:].std(axis=0) > 0]
    f = HF.fit_ols(X[:, keep], y)
    return float(f["beta"][1])


def verdict(r, n_esc, n_non):
    if n_esc < MIN_EVENTS or n_non < MIN_EVENTS:
        return "descriptive (underpowered)"
    lo0, hi0 = r["ci_a0"]
    lo_a, hi_a = r["ci_a"]
    lo_s, hi_s = r["ci_s"]
    if not (hi0 < 0):
        if hi_s < 0 and lo_a <= 0 <= hi_a:
            return "supported (starvation without aging)"
        return "descriptive (no aging to explain)"
    if hi_s < 0 and (lo_a <= 0 <= hi_a or abs(r["beta_a"]) <= 0.15):
        return "supported"
    if hi_a < 0 and (r["rho"] < 0.25 or lo_s <= 0 <= hi_s):
        return "failed"
    return "mixed"
