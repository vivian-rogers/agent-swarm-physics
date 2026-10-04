"""H85 synthetic validation at the real unit layout (N_u, T_u, regime, goal clusters, git_dense, mode class).

Uses only design facts from units.parquet (N, T, regime, goal, mode class, git_dense); no output column is read.
Scenarios (Poisson counts, goal effect SD 0.3, unit residual SD 0.4, per-agent-hour rate 2 at the regime median N):
  S-beta   planted beta in {0.85, 1.00, 1.15, 1.34}, M1 fit: bias, cluster-CI coverage, power vs beta = 1 and vs 1.34
  S-conf   beta = 1, regime III intercept +0.7 (N rises with regime): bias of M0 (no regime) vs M1
  S-commit beta in {1.0, 1.15} on the 36 git-dense units: CI width and power
  S-repos  own-artifact beta 1.0, shared beta 0.7 on git-dense units: power of the one-sided interaction test
  S-reply  message-level mechanism: addressed responses per message ~ Poisson(lambda), lambda ∝ k^0.34, k ∝ N;
           DQ2-like parent = (count >= 1), calibrated to the documented parent fractions per regime.
Output: data/processed/H85-output-scaling-with-n/synthetic/synthetic.json
Usage: uv run python hypotheses/H85-output-scaling-with-n/analysis/synthetic.py [--reps 200]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h85lib as L  # noqa: E402


def layout():
    u = pl.read_parquet(L.DATA / "units.parquet").select("unit_id", "goal_no", "regime", "N", "T_h", "shared_mode",
                                                         "git_dense")
    return u


def simulate_counts(u, beta, rng, reg_shift=None, sd_goal=0.3, sd_unit=0.4, rate=2.0, beta_by=None):
    lnN = np.log(u["N"].to_numpy())
    reg = u["regime"].to_numpy()
    goals = u["goal_no"].to_numpy()
    g_eff = {g: rng.normal(0, sd_goal) for g in set(goals)}
    med = {r: np.median(lnN[reg == r]) for r in set(reg)}
    b = np.full(len(lnN), beta) if beta_by is None else beta_by
    eta = np.log(rate) + np.array([med[r] for r in reg]) + b * (lnN - np.array([med[r] for r in reg]))
    if reg_shift:
        eta = eta + np.array([reg_shift.get(r, 0.0) for r in reg])
    eta = eta + np.array([g_eff[g] for g in goals]) + rng.normal(0, sd_unit, len(lnN))
    Y = rng.poisson(u["T_h"].to_numpy() * np.exp(eta))
    return np.maximum(Y, 0)


def run(reps: int, B: int):
    rng = np.random.default_rng(20261004)
    u = layout()
    lnN, reg, goals, T = np.log(u["N"].to_numpy()), u["regime"].to_numpy(), u["goal_no"].to_numpy(), u["T_h"].to_numpy()
    res = {"layout": {"n_units": u.height, "n_goals": int(len(set(goals))), "sd_lnN": float(lnN.std()),
                      "sd_lnN_within_regime": {r: float(lnN[reg == r].std()) for r in sorted(set(reg))}}}

    def summarize(est, lo, hi, truth):
        est, lo, hi = map(np.asarray, (est, lo, hi))
        return {"mean": float(est.mean()), "bias": float(est.mean() - truth), "sd": float(est.std()),
                "coverage": float(((lo <= truth) & (hi >= truth)).mean()), "ci_width": float(np.mean(hi - lo)),
                "reject_1": float(((lo > 1) | (hi < 1)).mean()), "reject_134": float(((lo > 1.34) | (hi < 1.34)).mean())}

    # S-beta
    sb = {}
    for beta in (0.85, 1.0, 1.15, 1.34):
        e, lo, hi = [], [], []
        for _ in range(reps):
            Y = simulate_counts(u, beta, rng)
            ok = Y > 0
            f = L.fit_beta(np.log(Y[ok] / T[ok]), lnN[ok], reg[ok], goals[ok], B=B, rng=rng)
            e.append(f["beta"]); lo.append(f["ci_lo"]); hi.append(f["ci_hi"])
        sb[str(beta)] = summarize(e, lo, hi, beta)
    res["S_beta"] = sb

    # S-conf
    e0, e1 = [], []
    for _ in range(reps):
        Y = simulate_counts(u, 1.0, rng, reg_shift={"III": 0.7})
        y = np.log(np.maximum(Y, 1) / T)
        e0.append(L.ols(L.design(lnN, None)[0], y)[0]); e1.append(L.ols(L.design(lnN, reg)[0], y)[0])
    res["S_conf"] = {"M0_mean": float(np.mean(e0)), "M1_mean": float(np.mean(e1)), "truth": 1.0}

    # S-commit on git-dense units
    gd = u["git_dense"].to_numpy().astype(bool)
    sc = {}
    for beta in (1.0, 1.15):
        e, lo, hi = [], [], []
        for _ in range(reps):
            Y = simulate_counts(u, beta, rng, rate=0.5)
            ok = gd & (Y > 0)
            f = L.fit_beta(np.log(Y[ok] / T[ok]), lnN[ok], reg[ok], goals[ok], B=B, rng=rng)
            e.append(f["beta"]); lo.append(f["ci_lo"]); hi.append(f["ci_hi"])
        sc[str(beta)] = summarize(e, lo, hi, beta)
    res["S_commit"] = sc

    # S-repos: interaction test on git-dense units (repos per day ~ Poisson, own 1.0, shared 0.7)
    sh = u["shared_mode"].to_numpy().astype(bool)
    rej, rej0 = 0, 0
    for k in range(reps):
        for bs, tag in ((0.7, "alt"), (1.0, "null")):
            bb = np.where(sh, bs, 1.0)
            Y = simulate_counts(u, 1.0, rng, beta_by=bb, rate=0.05, sd_unit=0.3)
            ok = gd & (Y > 0)
            y = np.log(Y[ok] / T[ok])
            extra = {"lnN_x_shared": lnN[ok] * sh[ok], "shared": sh[ok].astype(float)}
            f = L.fit_beta(y, lnN[ok], reg[ok], goals[ok], extra=extra, coef="lnN_x_shared", B=B, rng=rng)
            if f["ci_hi"] < 0 or (f["beta"] < 0 and f["se_boot"] > 0 and f["beta"] / f["se_boot"] < -1.2816):
                if tag == "alt":
                    rej += 1
                else:
                    rej0 += 1
    res["S_repos"] = {"power_one_sided_p10": rej / reps, "size_one_sided_p10": rej0 / reps,
                      "n_units": int(gd.sum()), "n_shared": int((gd & sh).sum())}

    # S-reply: message-level mechanism
    medN = {r: np.median(u["N"].to_numpy()[reg == r]) for r in set(reg)}
    er, em, emsg = [], [], []
    for _ in range(reps):
        M = simulate_counts(u, 1.0, rng, rate=2.0)
        par, men = np.zeros(len(M)), np.zeros(len(M))
        for i in range(len(M)):
            f0 = L.F_PARENT[reg[i]]
            lam0 = -np.log(1 - f0)
            lam = lam0 * (u["N"][i] / medN[reg[i]]) ** (1 - L.BETA_D)
            cnt = rng.poisson(lam, size=int(M[i]))
            par[i], men[i] = (cnt >= 1).sum(), cnt.sum()
        ok = (M > 0) & (par > 0)
        X = L.design(lnN[ok], reg[ok])[0]
        emsg.append(L.ols(X, np.log(M[ok] / T[ok]))[0])
        er.append(L.ols(X, np.log(par[ok] / T[ok]))[0])
        em.append(L.ols(X, np.log(men[ok] / T[ok]))[0])
    res["S_reply"] = {"beta_msg": float(np.mean(emsg)), "beta_parent": float(np.mean(er)), "beta_ment": float(np.mean(em)),
                      "sd_parent": float(np.std(er)), "sd_ment": float(np.std(em)),
                      "sd_dbeta_ment": float(np.std(np.array(em) - np.array(emsg))),
                      "budget_factor": {r: L.budget_factor(f) for r, f in L.F_PARENT.items()}}

    # S-ratio: per-message addressing intensity ln(ment/msg) with extra ratio noise (goal SD 0.15, unit SD 0.25);
    # planted d = 0.34 (H18 aggregates) and d = 0 (saturation): bias, coverage and power of the cluster CI
    sr = {}
    for d in (0.0, 0.17, 0.34):
        e, lo, hi = [], [], []
        for _ in range(reps):
            gq = {g: rng.normal(0, 0.15) for g in set(goals)}
            med = {r: np.median(lnN[reg == r]) for r in set(reg)}
            M = simulate_counts(u, 1.0, rng)
            lam = np.exp(np.log(1.0) + d * (lnN - np.array([med[r] for r in reg])) + np.array([gq[g] for g in goals])
                         + rng.normal(0, 0.25, len(lnN)))
            A = rng.poisson(M * lam)
            ok = (M > 0) & (A > 0)
            f = L.fit_beta(np.log(A[ok] / M[ok]), lnN[ok], reg[ok], goals[ok], B=B, rng=rng)
            e.append(f["beta"]); lo.append(f["ci_lo"]); hi.append(f["ci_hi"])
        e, lo, hi = map(np.asarray, (e, lo, hi))
        sr[str(d)] = {"mean": float(e.mean()), "sd": float(e.std()), "coverage": float(((lo <= d) & (hi >= d)).mean()),
                      "reject_0": float(((lo > 0) | (hi < 0)).mean()), "reject_034": float(((lo > 0.34) | (hi < 0.34)).mean()),
                      "ci_width": float(np.mean(hi - lo))}
    res["S_ratio"] = sr
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=200)
    ap.add_argument("--B", type=int, default=300)
    a = ap.parse_args()
    res = run(a.reps, a.B)
    out = L.DATA / "synthetic"
    out.mkdir(parents=True, exist_ok=True)
    (out / "synthetic.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
