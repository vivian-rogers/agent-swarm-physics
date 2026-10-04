"""H95 synthetic validation (axis F): is the slack S a monotone gauge of the captured fraction q, and how much negative
rho(S, x) does churn alone make when x and S share the same commits?

Generator: H75's synthetic agents (commit-observed states; lognormal call rates, median 130/h, SD 0.8; commits Poisson
at 4 (r/130)^0.5 per active h with lognormal scatter; excursions to a side repo at rate a_i, mean 20 min), copied from
hypotheses/H75-reallocation-speed-limit/analysis/synthetic.py with attribution, extended with a captured fraction q:
captured agents are on their named target from t = 0 (seen at the first commit); searchers explore a non-named repo and
move to the target at hazard 1/tau (tau = 5 active h). Every agent starts at the null state (W_null variant).
Targets: 'shared' (one named repo for all) or 'own' (a named repo per agent, G39-like).

  uv run python hypotheses/H95-slack-specificity-gauge/analysis/synthetic.py
Writes data/processed/H95-slack-specificity-gauge/synthetic/{gauge,churn_null,power}.parquet and summary.json.
"""
from __future__ import annotations

import itertools
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h95lib as L  # noqa: E402

OUT = L.OUTD / "synthetic"
H = 20.0
TAU = 5.0
NS_REAL = [12, 13, 14, 13, 13, 15, 4, 12, 16]     # nine kickoff units, sizes as expected from H75 and roster counts


def simulate(N, q, rng, a0=1.0, target="shared", tau=TAU, exc_mean=1 / 3, c0=4.0):
    r = np.exp(np.log(130) + 0.8 * rng.standard_normal(N))
    a = a0 * r / 130
    c = c0 * np.sqrt(r / 130) * np.exp(0.5 * rng.standard_normal(N) - 0.125)
    times, codes = [], []
    for i in range(N):
        tgt = 3000 if target == "shared" else 2000 + i
        explore = 1000 if rng.random() < 0.3 else 100 + i
        side = 5000 if rng.random() < 0.5 else 6000 + i
        tm = 0.0 if rng.random() < q else rng.exponential(tau)
        ex, t = [], rng.exponential(1 / a[i])
        while t < H:
            d = rng.exponential(exc_mean)
            ex.append((t, t + d))
            t = t + d + rng.exponential(1 / a[i])
        n = max(rng.poisson(c[i] * H), 1)
        tc = np.sort(rng.uniform(0, H, n))
        cc = np.where(tc < tm, explore, tgt)
        for s0, s1 in ex:
            cc = np.where((tc >= s0) & (tc < s1), side, cc)
        times.append(tc)
        codes.append(cc.astype(np.int64))
    E = L.Ensemble(list(range(N)), times, codes, np.full(N, L.NULL, np.int64), H)
    named = {3000} if target == "shared" else {2000 + i for i in range(N)}
    return E, named


def unit(N, q, rng, a0=1.0, target="shared"):
    E, named = simulate(N, q, rng, a0, target)
    s = L.settle_stats(E)
    return {"N": N, "q": q, "a0": a0, "target": target, "S_e": s["S_e"], "T_e": s["T_e"], "W_e": s["W_e"],
            "x": L.specificity(E, named), "conc": L.concentration(E)[0]}


def unit_norm(N, q, rng, a0=1.0, target="shared", R=20):
    """unit() plus the within-agent label-permutation baseline S0 (median S over R permutations) and S/S0."""
    E, named = simulate(N, q, rng, a0, target)
    s = L.settle_stats(E)
    s0 = [L.settle_stats(L.permuted_ensemble(E, rng))["S_e"] for _ in range(R)]
    S0 = float(np.nanmedian(s0)) if np.isfinite(s0).any() else np.nan
    return {"N": N, "q": q, "a0": a0, "S_e": s["S_e"], "S0": S0, "S_norm": s["S_e"] / S0 if S0 and S0 > 0 else np.nan,
            "x": L.specificity(E, named), "T_e": s["T_e"]}


def norm_power(rng, draws=200):
    """Power and churn-null of rho(S/S0, x) at n = 9 (A1 check, run with --norm)."""
    out = []
    for kind in ("churn_null", "power"):
        for k in range(draws):
            a0s = np.exp(rng.uniform(np.log(0.5), np.log(8), 9))
            qs = [0.5] * 9 if kind == "churn_null" else rng.uniform(0.05, 0.95, 9)
            tg = rng.choice(["shared", "own"], 9)
            u = [unit_norm(N, q, rng, a0, t) for N, q, a0, t in zip(NS_REAL, qs, a0s, tg)]
            x = [v["x"] for v in u]
            out.append({"kind": kind, "draw": k, "rho_S_x": L.spearman(x, [v["S_e"] for v in u]),
                        "rho_Snorm_x": L.spearman(x, [v["S_norm"] for v in u]),
                        "rho_T_x": L.spearman(x, [v["T_e"] for v in u])})
    df = pl.DataFrame(out)
    df.write_parquet(OUT / "norm_power.parquet")
    crit = -0.5833333333333333
    res = {}
    for kind in ("churn_null", "power"):
        d = df.filter(pl.col("kind") == kind)
        res[kind] = {c: {"median": float(d[c].median()), "q05": float(d[c].quantile(0.05)),
                         "P_le_crit": float((d[c] <= crit).mean()), "P_abs_lt_0.3": float((d[c].abs() < 0.3).mean())}
                     for c in ("rho_S_x", "rho_Snorm_x", "rho_T_x")}
    L.write_json(OUT / "norm_power.json", res)
    print(res)


def rho_crit(n=9, alpha=0.05) -> float:
    """Exact one-sided critical value of Spearman's rho (no ties) for n: the alpha quantile of the permutation law."""
    base = np.arange(n)
    d2 = np.array([((base - np.array(p)) ** 2).sum() for p in itertools.permutations(range(n))])
    rho = 1 - 6 * d2 / (n * (n * n - 1))
    return float(np.quantile(rho, alpha))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(9595)
    rows = []
    for target in ("shared", "own"):
        for N in (4, 12, 15, 27):
            for q in np.round(np.linspace(0, 1, 11), 2):
                for _ in range(30):
                    rows.append(unit(N, q, rng, 1.0, target))
    gauge = pl.DataFrame(rows)
    gauge.write_parquet(OUT / "gauge.parquet")
    g = gauge.group_by(["target", "N", "q"], maintain_order=True).agg(
        pl.col("S_e").median().alias("S_med"), pl.col("S_e").quantile(0.1).alias("S_q10"),
        pl.col("S_e").quantile(0.9).alias("S_q90"), pl.col("x").median().alias("x_med"),
        pl.col("T_e").median().alias("T_med"), pl.col("S_e").is_nan().mean().alias("cens"))
    with pl.Config(tbl_rows=100, tbl_cols=-1, float_precision=2, tbl_width_chars=200):
        print(g.filter(pl.col("N").is_in([4, 15])))
    crit = rho_crit(9)
    print("rho_crit(9, 0.05) =", crit)

    def kickoff_set(qs, a0s, targets):
        out = []
        for N, q, a0, tg in zip(NS_REAL, qs, a0s, targets):
            out.append(unit(N, q, rng, a0, tg))
        return out

    nul, pw = [], []
    for k in range(500):
        a0s = np.exp(rng.uniform(np.log(0.5), np.log(8), 9))
        tg = rng.choice(["shared", "own"], 9)
        u = kickoff_set([0.5] * 9, a0s, tg)
        nul.append({"draw": k, "rho_S_x": L.spearman([x["x"] for x in u], [x["S_e"] for x in u]),
                    "rho_T_x": L.spearman([x["x"] for x in u], [x["T_e"] for x in u])})
    nul = pl.DataFrame(nul)
    nul.write_parquet(OUT / "churn_null.parquet")
    q05 = float(nul["rho_S_x"].quantile(0.05))
    for k in range(300):
        a0s = np.exp(rng.uniform(np.log(0.5), np.log(8), 9))
        qs = rng.uniform(0.05, 0.95, 9)
        tg = rng.choice(["shared", "own"], 9)
        u = kickoff_set(qs, a0s, tg)
        rS = L.spearman([x["x"] for x in u], [x["S_e"] for x in u])
        pw.append({"draw": k, "rho_S_x": rS, "rho_S_q": L.spearman(qs, [x["S_e"] for x in u]),
                   "rho_T_x": L.spearman([x["x"] for x in u], [x["T_e"] for x in u])})
    pw = pl.DataFrame(pw)
    pw.write_parquet(OUT / "power.parquet")
    summ = {
        "rho_crit_n9_one_sided_0.05": crit,
        "churn_null": {"median_rho_S_x": float(nul["rho_S_x"].median()), "q05_rho_S_x": q05,
                       "q95_rho_S_x": float(nul["rho_S_x"].quantile(0.95)),
                       "P_rho_le_crit": float((nul["rho_S_x"] <= crit).mean()),
                       "P_kill_abs_lt_0.3": float((nul["rho_S_x"].abs() < 0.3).mean()),
                       "median_rho_T_x": float(nul["rho_T_x"].median())},
        "power": {"median_rho_S_x": float(pw["rho_S_x"].median()), "median_rho_S_q": float(pw["rho_S_q"].median()),
                  "P_rho_le_crit": float((pw["rho_S_x"] <= crit).mean()),
                  "P_rho_le_crit_and_below_churn_q05": float(((pw["rho_S_x"] <= crit) & (pw["rho_S_x"] < q05)).mean()),
                  "P_rho_le_-0.5": float((pw["rho_S_x"] <= -0.5).mean()),
                  "P_rhoT_le_-0.5": float((pw["rho_T_x"] <= -0.5).mean())},
        "gauge_monotone_check": {},
    }
    for tg in ("shared", "own"):
        for N in (4, 12, 15, 27):
            s = g.filter((pl.col("target") == tg) & (pl.col("N") == N)).sort("q")["S_med"].to_numpy()
            summ["gauge_monotone_check"][f"{tg}_N{N}"] = {"S_med_by_q": [round(float(v), 3) for v in s],
                                                          "non_increasing": bool(np.all(np.diff(s[np.isfinite(s)]) <= 0.15))}
    L.write_json(OUT / "summary.json", summ)
    print(summ)


if __name__ == "__main__":
    if "--norm" in sys.argv:
        OUT.mkdir(parents=True, exist_ok=True)
        norm_power(np.random.default_rng(959595))
    else:
        main()
