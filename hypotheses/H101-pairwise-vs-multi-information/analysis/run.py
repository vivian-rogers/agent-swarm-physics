"""H101 replication pipeline: per unit, the max-ent hierarchy on random agent subsets of each day, bias-corrected by a
parametric bootstrap, with the independent and pairwise-truth nulls and the shared-field (latent-class) reference.

unit_stats(mats, rng) is the estimator shared with synthetic.py and the natives. Per day (one item x agent matrix):
  S random subsets of n = min(N_SUB, N_d) agents (all subsets if fewer); rows with K_sub = 0 dropped (support K >= 1).
  For each subset: hierarchy() (uncorrected entropies), then
   - pairwise-truth bootstrap (B draws from the fitted K-pairwise model P2K at the same T): the bias of every entropy
     = mean(refit) - exact value in the bootstrap world; corrected entropy = estimate - bias.  The same draws give
     the null distribution of the higher-order remainder D = S2K - SN (true D = 0 in that world).
   - independent bootstrap (B draws from the fitted independent model on the support): null of I_N.
   - shared-field reference (first F_SUB subsets per day): latent-class EM fit, one draw at the same T, same estimator.
Aggregation: ratio of T-weighted sums over subsets and days; z-tests use the aggregated bootstrap draws.
Per-unit CIs: item bootstrap within days (B_CI resamples of rows, re-running the corrected estimator on F_SUB subsets).

Usage: uv run python hypotheses/H101-pairwise-vs-multi-information/analysis/run.py [--units 27,40] [--family conv]
"""
from __future__ import annotations

import argparse
import zlib
import itertools
import json
import math
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h101lib as L  # noqa: E402

ROOT = HERE.parents[2]
BASE = ROOT / "data/processed/H101-pairwise-vs-multi-information"
N_SUB = 6
S_SUB = 10
B = 12
F_SUB = 3
B_CI = 30
KEYS = ("S1", "SK", "S2", "S2K", "SN")


def exact_entropies(p: np.ndarray, n: int, T_big: float = 1e7) -> dict:
    """Entropies of the hierarchy for an exact distribution p on the support (projections by max-ent fits)."""
    c = p * T_big
    e = {}
    for kind, key in (("ind", "S1"), ("K", "SK"), ("pair", "S2"), ("pairK", "S2K")):
        e[key] = L.fit_maxent(c, n, kind, prior_var=1e6)[2]
    pp = p[p > 0]
    e["SN"] = float(-(pp * np.log(pp)).sum())
    return e


def raw_entropies(X: np.ndarray) -> dict:
    r = L.hierarchy(X, correct=False)
    return {k: r[k] for k in KEYS}, r["_fits"]


def subset_stats(X: np.ndarray, rng, boot: bool = True, Bn: int = B) -> dict:
    """One subset-day: uncorrected and bias-corrected entropies plus null draws (aggregatable sums)."""
    X = L.support(X)
    T, n = X.shape
    e, fits = raw_entropies(X)
    out = {"T": T, "n": n, "raw": e}
    if not boot or T < 20:
        out["corr"] = e
        return out
    # pairwise-truth world
    p2k = fits["pairK"][1]
    truth = exact_entropies(p2k, n)
    bias = {k: [] for k in KEYS}
    Dnull = []
    for _ in range(Bn):
        Xb = L.sample_from(p2k, n, T, rng)
        eb, _ = raw_entropies(Xb)
        for k in KEYS:
            bias[k].append(eb[k] - truth[k])
        Dnull.append(eb["S2K"] - eb["SN"])
    corr = {k: e[k] - float(np.mean(bias[k])) for k in KEYS}
    out["corr"] = corr
    out["D_null"] = np.array(Dnull)
    # independent world: null of I_N
    p1 = fits["ind"][1]
    INnull = []
    for _ in range(Bn):
        Xb = L.sample_from(p1, n, T, rng)
        c = L.counts(Xb)
        S1b = L.fit_maxent(c, n, "ind")[2]
        INnull.append(S1b - L.entropy_plugin(c, mm=False))
    out["IN_null"] = np.array(INnull)
    return out


def field_reference(X: np.ndarray, rng) -> dict:
    X = L.support(X)
    T, n = X.shape
    pi, q = L.latent_field_fit(X, rng=rng)
    Y = L.latent_field_sample(pi, q, int(T * 1.6) + 20, rng)
    Y = L.support(Y)[:T]
    return subset_stats(Y, rng, Bn=4)


def _subsets(N, n, S, rng):
    if math.comb(N, n) <= S:
        return [list(c) for c in itertools.combinations(range(N), n)]
    seen, out = set(), []
    while len(out) < S:
        c = tuple(sorted(rng.choice(N, n, replace=False)))
        if c not in seen:
            seen.add(c)
            out.append(list(c))
    return out


def unit_stats(mats: list[np.ndarray], rng, n_sub: int = N_SUB, S: int = S_SUB, field: bool = True,
               subsets: list | None = None, ci: bool = False) -> dict:
    rows, frows = [], []
    for k, X in enumerate(mats):
        N = X.shape[1]
        if N < 3 or X.shape[0] < 30:
            continue
        n = min(n_sub, N)
        subs = subsets[k] if subsets is not None else _subsets(N, n, S, rng)
        for j, sub in enumerate(subs):
            st = subset_stats(X[:, sub], rng)
            if st["T"] < 20:
                continue
            st["day"] = k
            rows.append(st)
            if field and j < F_SUB:
                frows.append(field_reference(X[:, sub], rng))
    if not rows:
        return {"ok": False}
    res = summarize(rows)
    if field and frows:
        fr = summarize(frows)
        res.update({f"field_{k}": fr[k] for k in ("rho_F", "phi", "rho_raw", "r_HO", "I_N")})
    res["n_subset_days"] = len(rows)
    res["n_days"] = len({r["day"] for r in rows})
    res["n"] = int(np.median([r["n"] for r in rows]))
    res["ok"] = True
    if ci:
        res.update(item_bootstrap(mats, rng, n_sub))
    return res


def summarize(rows: list[dict]) -> dict:
    w = np.array([r["T"] for r in rows], float)
    W = w.sum()
    raw = {k: float((w * np.array([r["raw"][k] for r in rows])).sum() / W) for k in KEYS}
    cor = {k: float((w * np.array([r["corr"][k] for r in rows])).sum() / W) for k in KEYS}
    out = {"T_total": W}
    out.update({f"raw_{k}": v for k, v in L.ratios(raw).items()})
    out.update(L.ratios(cor))
    out.update({f"E_{k}": v for k, v in cor.items()})
    D = cor["S2K"] - cor["SN"]
    if all("D_null" in r for r in rows):
        Dn = (w[:, None] * np.stack([r["D_null"] for r in rows])).sum(0) / W
        INn = (w[:, None] * np.stack([r["IN_null"] for r in rows])).sum(0) / W
        Dobs = raw["S2K"] - raw["SN"]
        INobs = raw["S1"] - raw["SN"]
        sdD, sdI = Dn.std(ddof=1), INn.std(ddof=1)
        out["D_corr"] = D
        out["ho_excess_z"] = float((Dobs - Dn.mean()) / sdD) if sdD > 0 else np.nan
        out["ho_excess_p"] = float(0.5 * math.erfc(out["ho_excess_z"] / math.sqrt(2))) if np.isfinite(out["ho_excess_z"]) else np.nan
        out["I_N_z"] = float((INobs - INn.mean()) / sdI) if sdI > 0 else np.nan
        out["I_N_p"] = float(0.5 * math.erfc(out["I_N_z"] / math.sqrt(2))) if np.isfinite(out["I_N_z"]) else np.nan
    return out


def item_bootstrap(mats, rng, n_sub, Bci: int = B_CI) -> dict:
    """Rows resampled within each day; the corrected estimator re-run on F_SUB fixed subsets per day."""
    subs = [_subsets(X.shape[1], min(n_sub, X.shape[1]), F_SUB, rng) if X.shape[1] >= 3 else [] for X in mats]
    vals = {k: [] for k in ("rho_F", "phi", "rho_raw", "r_HO", "I_N")}
    for _ in range(Bci):
        bm = [X[rng.integers(0, X.shape[0], X.shape[0])] for X in mats]
        rows = []
        for k, X in enumerate(bm):
            if X.shape[1] < 3 or X.shape[0] < 30:
                continue
            for sub in subs[k]:
                st = subset_stats(X[:, sub], rng, Bn=4)
                if st["T"] >= 20:
                    rows.append(st)
        if rows:
            s = summarize(rows)
            for k in vals:
                vals[k].append(s[k])
    out = {}
    for k, v in vals.items():
        v = np.array(v, float)
        v = v[np.isfinite(v)]
        out[f"{k}_lo"] = float(np.percentile(v, 2.5)) if len(v) > 5 else np.nan
        out[f"{k}_hi"] = float(np.percentile(v, 97.5)) if len(v) > 5 else np.nan
    return out


def load_unit(unit: str, family: str = "conv", variant: str = "main"):
    z = np.load(BASE / "days" / f"{unit}.npz")
    mats, meta = [], []
    for k in range(len(z["days"])):
        X = z[f"{family}_{k}"]
        if variant == "noexo":
            X = X[~z[f"{family}H_{k}"]]
        if variant == "noW" and family == "conv":
            X = X[~z[f"convW_{k}"]]
        mats.append(X)
        meta.append({"day": str(z["days"][k]), "agents": z[f"agents_{k}"], "rooms": z[f"rooms_{k}"]})
    return mats, meta


def pooled_projects(mats):
    """Projects are sparse per day: pool the unit's days on the agents active on every day of the unit."""
    return mats


def run_unit(args):
    unit, family, variant, ci = args
    rng = np.random.default_rng(zlib.crc32(f"{unit}|{family}|{variant}".encode()))
    mats, meta = load_unit(unit, family, variant)
    if family == "proj":
        # pool days on agents present every day (codes), so one matrix per unit
        common = set(meta[0]["agents"].tolist())
        for m in meta[1:]:
            common &= set(m["agents"].tolist())
        common = sorted(common)
        if len(common) < 3:
            return {"unit": unit, "family": family, "variant": variant, "ok": False}
        rows = []
        for X, m in zip(mats, meta):
            ix = [list(m["agents"]).index(a) for a in common]
            rows.append(X[:, ix])
        mats = [np.concatenate(rows)] if rows else []
    st = unit_stats(mats, rng, ci=ci)
    st.update({"unit": unit, "family": family, "variant": variant})
    return st


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", default="")
    ap.add_argument("--family", default="conv")
    ap.add_argument("--variants", default="main")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--no-ci", action="store_true")
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    meta = pl.read_parquet(BASE / "unit_meta.parquet")
    units = a.units.split(",") if a.units else meta["unit_id"].to_list()
    jobs = [(u, a.family, v, not a.no_ci and v == "main") for u in units for v in a.variants.split(",")]
    (BASE / "results").mkdir(parents=True, exist_ok=True)
    with ProcessPoolExecutor(a.workers) as ex:
        res = list(ex.map(run_unit, jobs))
    df = pl.DataFrame([{k: (float(v) if isinstance(v, (np.floating,)) else v) for k, v in r.items()
                        if not isinstance(v, (list, dict, np.ndarray))} for r in res], infer_schema_length=None)
    df = df.join(meta.select("unit_id", "goal_no", "regime", "n_days", "N_med").rename({"unit_id": "unit", "n_days": "days_all"}),
                 on="unit", how="left")
    out = BASE / "results" / f"units_{a.family}{a.tag}.parquet"
    df.write_parquet(out)
    print(df.select([c for c in ("unit", "variant", "ok", "n", "T_total", "I_N", "I_N_p", "rho_raw", "phi", "rho_F",
                                 "r_HO", "ho_excess_p", "field_rho_F") if c in df.columns]))


if __name__ == "__main__":
    main()
