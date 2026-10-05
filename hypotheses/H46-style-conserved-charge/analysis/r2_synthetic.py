"""H46 round 2 synthetic validation (axis F), run before any round-2 statistic on real data.

Village sampling: the real eligible-message schedule, genre and position covariates, NE41 pair schedule, goal-switch
boundary catalog and regime-III context segments. Message vectors are synthetic:
  x_m = q_i + eta_{i,d} + eps_m + planted structure,
eps resampled from the agent's own real within-agent-day residuals (day and context structure destroyed), q_i the agent
mean, eta ~ N(0, 0.05 * per-dimension message variance). Everything downstream is the real round-2 code (r2lib, h46lib).

Blocks:
  R1  residualization (NE41 forced T and goal-switch T): S0 null; SG common genre + position effects (no jump);
      SJ random-direction segment offset (an erasure excursion that a common profile cannot absorb).
  R2  drift-and-reset estimators: S0 none; S1a OU reset phi 0.7; S1b OU reset phi 0.9; S2 OU without reset (chain over
      the agent-day); S3 clock-time OU (tau 30 min) without reset. s^2 = 10% of the per-message noise trace.
  R3  function-word class test: size (S0) and power (unit shift 0.5 day-jitter SD) at goal switches; NE41 size.
Output: data/processed/H46-style-conserved-charge/r2/synthetic.json
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h46lib as L  # noqa: E402
import r2lib as R  # noqa: E402

F_JIT = 0.05


def pools(m: pl.DataFrame, X: np.ndarray):
    key = (m["agent"].cast(pl.Utf8) + "|" + m["pt_date"]).to_numpy()
    _, inv = np.unique(key, return_inverse=True)
    S = np.zeros((inv.max() + 1, X.shape[1]))
    np.add.at(S, inv, X)
    Res = X - (S / np.bincount(inv)[:, None])[inv]
    ag = m["agent"].to_numpy()
    return {a: Res[ag == a] for a in np.unique(ag)}, {a: X[ag == a].mean(0) for a in np.unique(ag)}, X.var(0)


def base_draw(m, P_, rng):
    pool, mean, var = P_
    ag = m["agent"].to_numpy()
    key = (m["agent"].cast(pl.Utf8) + "|" + m["pt_date"]).to_numpy()
    _, dinv = np.unique(key, return_inverse=True)
    X = np.empty((len(m), len(var)))
    for a in np.unique(ag):
        ix = np.where(ag == a)[0]
        X[ix] = mean[a] + pool[a][rng.integers(0, len(pool[a]), len(ix))]
    X += (rng.standard_normal((dinv.max() + 1, len(var))) * np.sqrt(F_JIT * var))[dinv]
    return X


# ----------------------------------------------------------------------------------------------- R1
def block_r1(m, P_, n_rep=20, seed=11):
    ag, rg = m["agent"].to_numpy(), m["regime"].to_numpy()
    G, Pp = R.genre_block(m), R.position_block(m)
    GP = np.hstack([G, Pp])
    GPz = (GP - GP.mean(0)) / np.where(GP.std(0) > 0, GP.std(0), 1)
    var = P_[2]
    pr, i1, i2 = R.ne41_pairs(m)
    segkey = (m["agent"].cast(pl.Int64) * 100000 + m["seg"].fill_null(-1).cast(pl.Int64)).to_numpy()
    _, sinv = np.unique(segkey, return_inverse=True)
    r3 = (rg == "III")
    bounds = pl.read_parquet(L.DATA / "boundaries.parquet").filter(pl.col("cls") == "goal")
    fd = L.unit_first_days()
    rng = np.random.default_rng(seed)
    out = {}
    for scen in ("S0", "SG", "SJ"):
        t0 = time.time()
        acc = {v: {"ne41_T": [], "ne41_moves": 0, "goal_T": []} for v in ("tc", "g", "gp")}
        for rep in range(n_rep):
            X = base_draw(m, P_, rng)
            if scen == "SG":   # common directed genre + position effects: 5% of per-message variance
                B = rng.standard_normal((GPz.shape[1], X.shape[1]))
                eff = GPz @ B
                eff *= np.sqrt(0.05 * var.sum() / (eff ** 2).sum(1).mean())
                X += eff
            if scen == "SJ":   # random-direction offset per regime-III segment: 4% of per-message variance
                U = rng.standard_normal((sinv.max() + 1, X.shape[1])) * np.sqrt(0.04 * var)
                X += np.where(r3[:, None], U[sinv], 0.0)
            V = {"tc": X, "g": R.residualize(X, G, ag, rg), "gp": R.residualize(X, GP, ag, rg)}
            for v, Xv in V.items():
                t = R.ne41_test(pr, i1, i2, Xv, n_rand=2000, seed=rep)["forced"]
                acc[v]["ne41_T"].append(t["T"])
                acc[v]["ne41_moves"] += int(t["p_rand"] < 0.05 and t["lo"] > 0.5)
            if rep < 8:
                dt_ = L.day_table(m, V)
                ev = L.eval_boundaries(bounds, dt_, {v: v for v in V}, fd)
                for v in V:
                    acc[v]["goal_T"].append(L.class_test(ev, v, n_rand=2000, n_boot=200, seed=rep)["T"])
        out[scen] = {v: {"ne41_T_mean": float(np.mean(a["ne41_T"])), "ne41_T_sd": float(np.std(a["ne41_T"])),
                         "ne41_P_moves": a["ne41_moves"] / n_rep, "goal_T_mean": float(np.mean(a["goal_T"])),
                         "goal_T_sd": float(np.std(a["goal_T"]))} for v, a in acc.items()}
        print("R1", scen, f"{time.time() - t0:.0f}s", json.dumps(out[scen]), flush=True)
    return out


# ----------------------------------------------------------------------------------------------- R2
def plant_excursion(m3, var, scen, rng, s2_frac=0.10):
    n, D = len(m3), len(var)
    s2 = s2_frac * var.sum()
    sd_dim = np.sqrt(s2 / D)
    E = np.zeros((n, D))
    if scen == "S0":
        return E
    ag = m3["agent"].to_numpy()
    day = m3["pt_date"].to_numpy()
    seg = m3["seg"].to_numpy()
    tt = m3["t"].dt.epoch("us").to_numpy() / 1e6
    phi = {"S1a": 0.7, "S1b": 0.9, "S2": 0.9, "S3": None}[scen]
    e = np.zeros(D)
    for i in range(n):
        new_day = i == 0 or ag[i] != ag[i - 1] or day[i] != day[i - 1]
        if scen in ("S1a", "S1b"):
            if i == 0 or ag[i] != ag[i - 1] or seg[i] != seg[i - 1]:
                e = np.zeros(D)
            e = phi * e + np.sqrt(1 - phi ** 2) * sd_dim * rng.standard_normal(D)
        elif scen == "S2":
            if new_day:
                e = sd_dim * rng.standard_normal(D)
            else:
                e = phi * e + np.sqrt(1 - phi ** 2) * sd_dim * rng.standard_normal(D)
        else:   # S3 clock-time OU, tau 30 min, stationary start each day
            if new_day:
                e = sd_dim * rng.standard_normal(D)
            else:
                a = np.exp(-(tt[i] - tt[i - 1]) / 1800.0)
                e = a * e + np.sqrt(1 - a ** 2) * sd_dim * rng.standard_normal(D)
        E[i] = e
    return E


def block_r2(m, P_, n_rep=10, seed=21):
    m3i = np.where(m["regime"].to_numpy() == "III")[0]
    m3 = m[m3i]
    ag3, rg3 = m3["agent"].to_numpy(), m3["regime"].to_numpy()
    GP = np.hstack([R.genre_block(m3), R.position_block(m3)])
    var = P_[2]
    lp = R.lag_pairs(m3)
    rows, refs, labs, gaps, nref = R.pull_obs(m3)
    rng = np.random.default_rng(seed)
    out = {}
    for scen in ("S0", "S1a", "S1b", "S2", "S3"):
        t0 = time.time()
        res = {"s2": [], "phi": [], "slope_lo_gt0": 0, "dC1": [], "dC1_lo_gt0": 0, "phi_C": [],
               "rho_within": [], "rho_forced": [], "diff_lo_gt0": 0, "phi_in_ci": 0, "dbar_lo_gt0": 0, "ratio": [],
               "ratio_ok": 0, "dbar": []}
        for rep in range(n_rep):
            X = base_draw(m, P_, rng)[m3i]
            X = X + plant_excursion(m3, var, scen, rng)
            Xg = R.residualize(X, GP, ag3, rg3)
            Xc = R.unit_center(Xg, m3)
            gf = R.growth_fit(R.growth(Xc, m3), n_boot=100, seed=rep)
            cp = R.cross_products(Xc, lp, n_boot=100, seed=rep)
            pu = R.pull(Xc, rows, refs, labs, gaps, nref, ag3, n_boot=100, seed=rep)
            res["s2"].append(gf["s2"] / var.sum()); res["phi"].append(gf["phi"])
            res["slope_lo_gt0"] += int(gf["slope_ci"][0] > 0)
            res["dC1"].append(cp["lags"][1]["dC"] / var.sum())
            res["dC1_lo_gt0"] += int(cp["lags"][1]["dC_ci"][0] > 0)
            res["phi_C"].append(cp.get("phi_C", np.nan))
            res["phi_in_ci"] += int("phi_C" in cp and gf["phi_ci"][0] <= cp["phi_C"] <= gf["phi_ci"][1])
            res["rho_within"].append(pu["rho_within"]); res["rho_forced"].append(pu["rho_forced"])
            res["diff_lo_gt0"] += int(pu["diff_ci"][0] > 0)
            res["dbar_lo_gt0"] += int(gf["dbar_ci"][0] > 0)
            res["dbar"].append(gf["dbar"])
            ig = R.implied_growth(cp, lp, gf)
            res["ratio"].append(ig.get("ratio", np.nan))
            res["ratio_ok"] += int(ig.get("ok", False) and 0.5 <= ig["ratio"] <= 2)
        out[scen] = {"s2_frac_mean": float(np.mean(res["s2"])), "phi_mean": float(np.mean(res["phi"])),
                     "phi_sd": float(np.std(res["phi"])), "P_slope_ci_gt0": res["slope_lo_gt0"] / n_rep,
                     "dC1_frac_mean": float(np.mean(res["dC1"])), "P_dC1_ci_gt0": res["dC1_lo_gt0"] / n_rep,
                     "phi_C_median": float(np.nanmedian(res["phi_C"])), "P_phiC_in_phi_ci": res["phi_in_ci"] / n_rep,
                     "rho_within_mean": float(np.mean(res["rho_within"])), "rho_forced_mean": float(np.mean(res["rho_forced"])),
                     "P_diff_ci_gt0": res["diff_lo_gt0"] / n_rep, "P_dbar_ci_gt0": res["dbar_lo_gt0"] / n_rep,
                     "dbar_mean": float(np.mean(res["dbar"])), "ratio_median": float(np.nanmedian(res["ratio"])),
                     "P_ratio_in_band": res["ratio_ok"] / n_rep, "s2_true_frac": 0.10 if scen != "S0" else 0.0}
        print("R2", scen, f"{time.time() - t0:.0f}s", json.dumps(out[scen]), flush=True)
    return out


# ----------------------------------------------------------------------------------------------- R3
def block_r3(m, n_rep=20, seed=31):
    words = R.fw_words(m)
    mf = m.filter(pl.col("n_tok") >= R.MIN_TOK)
    F = R.fw_matrix(m, words)[(m["n_tok"].to_numpy() >= R.MIN_TOK)]
    P_ = pools(mf, F)
    var = P_[2]
    bounds = pl.read_parquet(L.DATA / "boundaries.parquet").filter(pl.col("cls") == "goal")
    fd = L.unit_first_days()
    key_u = (mf["agent"].cast(pl.Utf8) + "|" + mf["unit2"]).to_numpy()
    _, uinv = np.unique(key_u, return_inverse=True)
    m3 = mf.filter(pl.col("regime") == "III")
    i3 = np.where(mf["regime"].to_numpy() == "III")[0]
    pr, i1, i2 = R.ne41_pairs(m3)
    rng = np.random.default_rng(seed)
    out = {}
    for scen, ds in (("S0", 0.0), ("S2 fw shift 0.5", 0.5)):
        Ts, moves, ne = [], 0, []
        for rep in range(n_rep):
            X = base_draw(mf, P_, rng)
            if ds > 0:
                X += (rng.standard_normal((uinv.max() + 1, X.shape[1])) * np.sqrt(F_JIT * var) * ds)[uinv]
            dt_ = L.day_table(mf, {"fw": X})
            ev = L.eval_boundaries(bounds, dt_, {"fw": "fw"}, fd)
            t = L.class_test(ev, "fw", n_rand=2000, n_boot=200, seed=rep)
            Ts.append(t["T"])
            moves += int(t["p_rand"] < 0.05 and t["p_wilcoxon"] < 0.05)
            if ds == 0 and rep < 10:
                ne.append(R.ne41_test(pr, i1, i2, X[i3], n_rand=2000, seed=rep)["forced"]["T"])
        out[scen] = {"goal_T_mean": float(np.mean(Ts)), "goal_T_sd": float(np.std(Ts)), "P_moves": moves / n_rep,
                     "ne41_T_mean": float(np.mean(ne)) if ne else None}
        print("R3", scen, json.dumps(out[scen]), flush=True)
    out["n_words"] = len(words)
    out["n_messages"] = mf.height
    return out


def block_r1b(m, P_, n_rep=10, seed=12):
    """After Amendment R2-A5: NE41 forced T with scaled distances, tc / gp / fw, S0 and SJ."""
    ag, rg = m["agent"].to_numpy(), m["regime"].to_numpy()
    GP = np.hstack([R.genre_block(m), R.position_block(m)])
    keep = m["n_tok"].to_numpy() >= R.MIN_TOK
    mf = m.filter(pl.Series(keep))
    F = R.fw_matrix(m, R.fw_words(m))[keep]
    Pf = pools(mf, F)
    pr, i1, i2 = R.ne41_pairs(m)
    prf, j1, j2 = R.ne41_pairs(mf)
    segkey = (m["agent"].cast(pl.Int64) * 100000 + m["seg"].fill_null(-1).cast(pl.Int64)).to_numpy()
    _, sinv = np.unique(segkey, return_inverse=True)
    r3 = rg == "III"
    rng = np.random.default_rng(seed)
    out = {}
    for scen in ("S0", "SJ"):
        acc = {v: {"T": [], "moves": 0, "T_unscaled": []} for v in ("tc", "gp", "fw")}
        for rep in range(n_rep):
            X = base_draw(m, P_, rng)
            Xf = base_draw(mf, Pf, rng)
            if scen == "SJ":
                U = rng.standard_normal((sinv.max() + 1, X.shape[1])) * np.sqrt(0.04 * P_[2])
                X += np.where(r3[:, None], U[sinv], 0.0)
                Uf = rng.standard_normal((sinv.max() + 1, Xf.shape[1])) * np.sqrt(0.04 * Pf[2])
                Xf += np.where(r3[keep][:, None], Uf[sinv[keep]], 0.0)
            for v, (Xv, prr, a1, a2) in {"tc": (X, pr, i1, i2), "gp": (R.residualize(X, GP, ag, rg), pr, i1, i2),
                                         "fw": (Xf, prf, j1, j2)}.items():
                t = R.ne41_test(prr, a1, a2, Xv, n_rand=2000, seed=rep)["forced"]
                acc[v]["T"].append(t["T"])
                acc[v]["moves"] += int(t["p_rand"] < 0.05 and t["lo"] > 0.5)
                acc[v]["T_unscaled"].append(R.ne41_test(prr, a1, a2, Xv, n_rand=500, seed=rep, scale=False)["forced"]["T"])
        out[scen] = {v: {"T_mean": float(np.mean(a["T"])), "T_sd": float(np.std(a["T"])), "P_moves": a["moves"] / n_rep,
                         "T_unscaled_mean": float(np.mean(a["T_unscaled"]))} for v, a in acc.items()}
        print("R1b", scen, json.dumps(out[scen]), flush=True)
    return out


def main():
    m = R.load()
    X = L.style_matrix(m, "tc")
    P_ = pools(m, X)
    only = sys.argv[1:] or ["R1", "R2", "R3"]
    path = R.R2 / "synthetic.json"
    res = json.loads(path.read_text()) if path.exists() else {}
    if "R1" in only:
        res["R1"] = block_r1(m, P_)
    if "R2" in only:
        res["R2"] = block_r2(m, P_)
    if "R3" in only:
        res["R3"] = block_r3(m)
    if "R1b" in only:
        res["R1b"] = block_r1b(m, P_)
    path.write_text(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
