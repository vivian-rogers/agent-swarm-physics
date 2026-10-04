"""H89 synthetic validation (axis F): recover a planted selection / transmission / migration split at real counts.

Village sampling: the real active populations, roster flow, per-half message counts and in-cone parentage of
G12, G20, G31, G38 and G51 (non-holdout). Message noise: the agent's own real message residuals (from its agent-day
means), resampled within agent. Planted noise-free agent-day traits mu (scale set by the period's cross-fitted
between-agent-day signal variance v of that trait; only this scale is read from real traits). Scenarios (SPEC):
  S0 static agents (q only); F99 / F97 / S1w / S1: agent constant + iid day field holding 1% / 3% / 10% / 50% of v;
  S2 copy by the real parentage + field steps; S3 / S3x3 / S3x6 planted selection along a fixed axis (beta = 1, 3,
  6 sqrt(v) per SD of w); S4 field drift along a fixed axis (step energy 2x the per-day field energy).
Truth = the same estimator on noise-free mu (both halves = mu). Naive = whole-sample means in both halves (no
cross-fit). Output: data/processed/H89-price-equation-culture/synthetic/synthetic.json
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h89lib as L  # noqa: E402

OUT = L.DATA / "synthetic"
GOALS = [12, 20, 31, 38, 51]
TYPES = {"content": "content_bge", "style": "style"}
SCEN = ["S0", "F99", "F97", "S1w", "S1", "S2", "S3", "S3x3", "S3x6", "S4"]


def signal_var(P: L.Period, tag: str) -> float:
    rows = [P.keys[(a, d)] for d, v in P.active.items() for a in v]
    X = P.traits[tag][rows]
    A, B = X[:, 1] - X[:, 1].mean(0), X[:, 2] - X[:, 2].mean(0)
    return max(float((A * B).mean()), 1e-6) * 1.0   # per-dimension mean signal variance


SPEC = {
    "S0": dict(fq=1.0), "F99": dict(fq=0.99), "F97": dict(fq=0.97), "S1w": dict(fq=0.9), "S1": dict(fq=0.5),
    "S2": dict(fq=0.5, copy=True), "S3": dict(fq=0.5, beta=1.0), "S3x3": dict(fq=0.5, beta=3.0),
    "S3x6": dict(fq=0.5, beta=6.0), "S4": dict(fq=0.5, drift=2.0),
}


def make_mu(P: L.Period, scen: str, D: int, v: float, rng) -> dict:
    """Noise-free agent-day traits. fq: agent-constant fraction of the signal variance v (rest: iid day field);
    copy: stayers inherit by the real parentage; beta: planted selection along a fixed axis (x sqrt(v) per unit
    standardized w); drift: a fixed-direction field step whose energy is `drift` x the per-day field energy."""
    sp = SPEC[scen]
    fq = sp["fq"]
    agents = sorted({a for vv in P.active.values() for a in vv})
    ds = sorted(P.active)
    q = {a: rng.normal(0, np.sqrt(v * fq), D) for a in agents}
    f = {d: rng.normal(0, np.sqrt(v * (1 - fq)), D) for d in ds}
    if sp.get("drift"):
        u = rng.normal(size=D); u /= np.linalg.norm(u)
        step = np.sqrt(sp["drift"] * D * v * (1 - fq))
        f = {d: f[d] + k * step * u for k, d in enumerate(ds)}
    mu = {}
    for d in ds:
        for a in P.active[d]:
            mu[(a, d)] = q[a] + f[d]
    if sp.get("copy"):
        mu = {}
        for a in P.active[ds[0]]:
            mu[(a, ds[0])] = q[a] + f[ds[0]]
        for d0, d1 in zip(ds[:-1], ds[1:]):
            S = sorted(set(P.active[d0]) & set(P.active[d1]))
            if S:
                al_s, al_n, al_u, _ = L.parentage(P, d1, S)
                al = al_s + al_n + al_u
                Z0 = np.stack([mu[(a, d0)] for a in S])
                Z1 = al @ Z0 + (f[d1] - f[d0])[None, :] + rng.normal(0, np.sqrt(v / 10), (len(S), D))
                for k, a in enumerate(S):
                    mu[(a, d1)] = Z1[k]
            for a in P.active[d1]:
                if (a, d1) not in mu:
                    mu[(a, d1)] = q[a] + f[d1]
    if sp.get("beta"):
        u = rng.normal(size=D); u /= np.linalg.norm(u)
        beta = np.sqrt(v) * sp["beta"]
        for d0, d1 in zip(ds[:-1], ds[1:]):
            S = sorted(set(P.active[d0]) & set(P.active[d1]))
            if len(S) < L.MIN_STAY:
                continue
            al_s, al_n, al_u, _ = L.parentage(P, d1, S)
            w = (al_s + al_n + al_u).sum(0)
            sw = w.std()
            if sw <= 0:
                continue
            for k, a in enumerate(S):
                mu[(a, d0)] = mu[(a, d0)] + beta * (w[k] - w.mean()) / sw * u
    return mu


def build_arrays(P: L.Period, mu: dict, pool: dict, tag: str, rng, D: int):
    nk = len(P.keys)
    true = np.zeros((nk, 3, D)); noisy = np.zeros((nk, 3, D)); naive = np.zeros((nk, 3, D))
    z = np.load(L.DATA / "traits" / f"G{P.goal:02d}.npz")
    nA_all, nB_all = z["nA"], z["nB"]
    for (a, d), m in mu.items():
        k = P.keys[(a, d)]
        R = pool[a]
        nA, nB = int(nA_all[k]), int(nB_all[k])
        eA = R[rng.integers(0, len(R), nA)].mean(0)
        eB = R[rng.integers(0, len(R), nB)].mean(0)
        true[k] = m
        noisy[k, 1], noisy[k, 2] = m + eA, m + eB
        noisy[k, 0] = m + (nA * eA + nB * eB) / (nA + nB)
        naive[k] = noisy[k, 0]
    return true, noisy, naive


def with_traits(P: L.Period, arr: np.ndarray) -> L.Period:
    return L.Period(P.goal, P.days, P.keys, {"syn": arr}, P.active, P.F, P.adop, {})


def est(P: L.Period) -> dict:
    res, _ = L.run_period(P, tags=["syn"])
    e = L.shares(res, "syn")
    c = L.shares(res, "syn", cumulative=True)
    return dict(sel=e["s_sel"], trans=e["s_trans"], mig=e["s_mig"], mig_roster=e["s_mig_roster"],
                cum_mig=c["s_mig"], cum_mig_roster=c["s_mig_roster"], cum_sel=c["s_sel"],
                C=L.persistence(res, "syn", None), rho=e["rho"], rho_cum=c["rho"])


def main(n_rep: int = 60, n_perm: int = 200, n_jk: int = 20):
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(20261004)
    ad = pl.read_parquet(L.DATA / "agent_days.parquet")
    adop = pl.read_parquet(L.DATA / "adoptions.parquet")
    kick = np.load(L.DATA / "kickoff.npz")
    out = {}
    t0 = time.time()
    for g in GOALS:
        P = L.load_period(g, ad, adop, kick)
        rp = np.load(L.DATA / "residual_pool" / f"G{g:02d}.npz")
        out[g] = {}
        for typ, tag in TYPES.items():
            v = signal_var(P, tag)
            Rall = rp["content_bge" if typ == "content" else "style"].astype(np.float64)
            pool = {int(a): Rall[rp["agent"] == a] for a in np.unique(rp["agent"])}
            D = Rall.shape[1]
            out[g][typ] = {"v_signal_per_dim": v, "noise_sd_per_dim": float(Rall.std(0).mean())}
            for sc in SCEN:
                recs = []
                for r in range(n_rep):
                    mu = make_mu(P, sc, D, v, rng)
                    tr, no, na = build_arrays(P, mu, pool, tag, rng, D)
                    T, N, NV = est(with_traits(P, tr)), est(with_traits(P, no)), est(with_traits(P, na))
                    rec = {f"true_{k}": T[k] for k in T} | {f"xf_{k}": N[k] for k in N} | {f"naive_{k}": NV[k] for k in NV}
                    if sc in ("S0", "S1", "S3", "S3x3", "S3x6") and r < 40:
                        Q = with_traits(P, no)
                        pt = L.perm_sel_all(Q, "syn", n_perm=n_perm, seed=r)
                        for nm in ("energy", "cum", "mag"):
                            rec[f"perm_p_{nm}"] = pt[nm]["p"]
                    if sc in ("S1w", "S3x3") and r < n_jk and g in (20, 38):
                        Q = with_traits(P, no)

                        def f_mig(QQ):
                            res, _ = L.run_period(QQ, tags=["syn"])
                            return L.shares(res, "syn")["s_mig"]

                        def f_sel(QQ):
                            res, _ = L.run_period(QQ, tags=["syn"])
                            return L.shares(res, "syn")["s_sel"]
                        for nm, fn in (("mig", f_mig), ("sel", f_sel)):
                            full, se, n = L.jackknife(Q, fn)
                            rec[f"jk_cover_{nm}"] = bool(np.isfinite(se) and abs(full - T[nm]) <= 1.96 * se)
                    recs.append(rec)
                df = pl.DataFrame(recs)
                summ = {}
                for k in ("sel", "trans", "mig", "mig_roster", "cum_mig", "cum_mig_roster", "cum_sel", "C", "rho",
                          "rho_cum"):
                    tcol, xcol, ncol = df[f"true_{k}"].to_numpy(), df[f"xf_{k}"].to_numpy(), df[f"naive_{k}"].to_numpy()
                    ok = np.isfinite(tcol) & np.isfinite(xcol)
                    summ[k] = dict(true_mean=float(np.nanmean(tcol)), xf_mean=float(np.nanmean(xcol)),
                                   naive_mean=float(np.nanmean(ncol)),
                                   xf_bias=float(np.nanmean(xcol[ok] - tcol[ok])),
                                   xf_rmse=float(np.sqrt(np.nanmean((xcol[ok] - tcol[ok]) ** 2))),
                                   naive_bias=float(np.nanmean(ncol - tcol)))
                for nm in ("energy", "cum", "mag"):
                    if f"perm_p_{nm}" in df.columns:
                        summ[f"perm_reject_005_{nm}"] = float((df[f"perm_p_{nm}"].drop_nulls() < 0.05).mean())
                for nm in ("mig", "sel"):
                    c = f"jk_cover_{nm}"
                    if c in df.columns:
                        summ[f"jk_coverage_{nm}"] = float(df[c].drop_nulls().mean())
                out[g][typ][sc] = summ
                print(f"G{g:02d} {typ:7s} {sc}: true sel/trans/mig {summ['sel']['true_mean']:+.2f}/"
                      f"{summ['trans']['true_mean']:+.2f}/{summ['mig']['true_mean']:+.2f}  xf bias "
                      f"{summ['sel']['xf_bias']:+.3f}/{summ['trans']['xf_bias']:+.3f}/{summ['mig']['xf_bias']:+.3f}  "
                      f"naive bias {summ['sel']['naive_bias']:+.3f}/{summ['trans']['naive_bias']:+.3f}/"
                      f"{summ['mig']['naive_bias']:+.3f}  C true {summ['C']['true_mean']:+.2f} xf {summ['C']['xf_mean']:+.2f}"
                      f"  perm e/c/m {summ.get('perm_reject_005_energy', float('nan')):.2f}/{summ.get('perm_reject_005_cum', float('nan')):.2f}/{summ.get('perm_reject_005_mag', float('nan')):.2f} rho {summ['rho']['xf_mean']:.2f} jk {summ.get('jk_coverage_mig', float('nan')):.2f}/"
                      f"{summ.get('jk_coverage_sel', float('nan')):.2f}  ({time.time() - t0:.0f}s)", flush=True)
    (OUT / "synthetic.json").write_text(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
