"""H51 replication layer: one-dial collapse across non-holdout goal periods (exploratory).

Outputs data/processed/H51-one-dial-collapse/results/:
  collapse.json        per observable x variant: LOPO CV-R^2 of every model, collapse verdicts, index directions
  perm.json            within-regime permutation nulls for D1 (g_lag), D2 (index) and the equal-time dial
  tests.json           P1-P7 numbers (card), mean-field range check
  phase_points.parquet one row per period: axes (h, K, N, kick, f_sched), observables, D1 LOPO predictions and residuals
Usage: uv run python hypotheses/H51-one-dial-collapse/analysis/collapse.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import polars as pl
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h51lib as L  # noqa: E402

RES = L.DATA / "results"
VARIANTS = ["primary", "gte", "calls", "h11", "both", "phi", "h34tab"]


def rho(x, y):
    m = np.isfinite(x) & np.isfinite(y)
    if m.sum() < 4:
        return {"rho": None, "p": None, "n": int(m.sum())}
    r = spearmanr(x[m], y[m])
    n = int(m.sum())
    z, se = np.arctanh(np.clip(r.statistic, -0.999, 0.999)), 1 / np.sqrt(max(n - 3, 1))
    return {"rho": float(r.statistic), "p": float(r.pvalue), "n": n,
            "lo": float(np.tanh(z - 1.96 * se)), "hi": float(np.tanh(z + 1.96 * se))}


def main():
    RES.mkdir(parents=True, exist_ok=True)
    out = {}
    for v in VARIANTS:
        d = L.load(v)
        obs = L.OBS + (["Y5_cons"] if v == "primary" else [])
        cs = L.collapse_scores(d, obs=L.OBS, seed=0)
        if v == "primary":
            # Y5 is report-only: rival scores without the index (its direction would need Y5 in the shared fit)
            cs.update(L.collapse_scores(d, obs=["Y5_cons"], index=False))
        out[v] = cs
        print(v, {j: (round(cs[j]["cv_r2"]["K"], 3), round(cs[j]["cv_r2"]["regime"], 3), round(cs[j]["cv_r2"]["logN"], 3),
                      round(cs[j]["cv_r2"].get("index", np.nan), 3), cs[j]["collapse_K"], cs[j].get("collapse_index"))
                  for j in obs})
    L.jdump(out, RES / "collapse.json")

    d = L.load("primary")
    dc = L.common_sample(d)
    perm = {"K": L.perm_stat(d, "K", n_perm=2000, seed=11),
            "g_eq": L.perm_stat(d, "g_eq", n_perm=2000, seed=12)}
    u = {j: np.full(dc.height, np.nan) for j in L.OBS}
    for j in L.OBS:
        m = dc[j].is_not_null().to_numpy()
        u[j][m] = np.array(out["primary"][j]["u"])
    perm["index"] = L.perm_stat(d, "index", n_perm=2000, seed=13, dial_values={j: np.nan_to_num(u[j]) for j in L.OBS})
    for k in ("logN",):
        perm[k] = L.perm_stat(d, k, n_perm=2000, seed=14)
    L.jdump(perm, RES / "perm.json")
    print("perm", {k: (round(v["T"], 3), v["p"]) for k, v in perm.items()})

    # ---------------------------------------------------------------- card tests
    P = out["primary"]
    nK = sum(P[j]["collapse_K"] for j in L.OBS)
    nI = sum(P[j]["collapse_index"] for j in L.OBS)
    t = {"P1": {"n_collapse_K": nK, "perm_p": perm["K"]["p"], "supported": bool(nK <= 1 and perm["K"]["p"] >= 0.05)},
         "P2": {"n_collapse_index": nI, "supported": bool(nI <= 2)},
         "P3": {"diff_K_minus_regime": {j: P[j]["cv_r2"]["K"] - P[j]["cv_r2"]["regime"] for j in L.OBS}},
         "P6": {"field_minus_K": {j: P[j]["cv_r2"]["field"] - P[j]["cv_r2"]["K"] for j in L.OBS}},
         "P7": {"geq_minus_K": {j: P[j]["cv_r2"]["g_eq"] - P[j]["cv_r2"]["K"] for j in L.OBS}}}
    t["P3"]["n_within_0.05"] = int(sum(abs(x) <= 0.05 for x in t["P3"]["diff_K_minus_regime"].values()))
    t["P3"]["n_K_beats_by_0.05"] = int(sum(x > 0.05 for x in t["P3"]["diff_K_minus_regime"].values()))
    t["P3"]["supported"] = t["P3"]["n_within_0.05"] >= 3
    t["P6"]["n_field_beats_K"] = int(sum(x > 0 for x in t["P6"]["field_minus_K"].values()))
    t["P6"]["supported"] = t["P6"]["n_field_beats_K"] >= 2
    t["P7"]["n_geq_not_better"] = int(sum(x <= 0.05 for x in t["P7"]["geq_minus_K"].values()))
    t["P7"]["supported"] = t["P7"]["n_geq_not_better"] >= 3
    r3 = dc.filter(pl.col("regime") == "III")
    t["P4"] = rho(r3["K"].to_numpy().astype(float), r3["Y3_branch"].to_numpy().astype(float))
    t["P4"]["all_periods"] = rho(dc["K"].to_numpy().astype(float), dc["Y3_branch"].to_numpy().astype(float))
    t["P4"]["supported"] = bool(t["P4"]["rho"] is not None and t["P4"]["rho"] > 0)
    t["P5"] = rho(dc["K"].to_numpy().astype(float), dc["Y1_settle"].to_numpy().astype(float))
    t["P5"]["supported"] = bool(t["P5"]["rho"] is not None and t["P5"]["rho"] >= -0.2)
    # all rank correlations of observables with each axis, within regime III and over all periods (descriptive)
    t["rho_table"] = {a: {j: {"all": rho(dc[a].to_numpy().astype(float), dc[j].to_numpy().astype(float)),
                              "III": rho(r3[a].to_numpy().astype(float), r3[j].to_numpy().astype(float))}
                          for j in L.OBS} for a in L.AXES + ["g_eq", "f_sched"]}
    # mean-field range check: max amplification vs across-period spread of each observable (natural scale)
    Kmax = float(np.nanmax(dc["K"].to_numpy()))
    raw = pl.read_parquet(L.DATA / "observables_periods.parquet").filter(pl.col("goal_no").is_in(dc["goal_no"].implode()))
    spread = {}
    for j, c in (("Y1_settle", "tau_settle"), ("Y2_herd", "herd_own_rate"), ("Y3_branch", "R_hat"), ("Y4_loop", "loop_rate")):
        x = raw[c].drop_nulls().to_numpy()
        x = x[x > 0]
        spread[j] = float(np.quantile(x, 0.9) / np.quantile(x, 0.1))
    t["meanfield"] = {"K_max_period": Kmax, "chi_max": 1 / (1 - Kmax), "obs_p90_over_p10": spread}
    L.jdump(t, RES / "tests.json")
    print({k: (v.get("supported") if isinstance(v, dict) else v) for k, v in t.items() if k.startswith("P")})
    print("meanfield", t["meanfield"])

    # ---------------------------------------------------------------- per-period points and D1 residuals
    rows = dc.select("goal_no", "regime", "N_active", "logN", "K", "g_lag_se", "g_eq", "c_x_trim", "phi_trim", "h", "kick",
                     "f_sched", *L.OBS)
    pts = rows.to_dict(as_series=False)
    for j in L.OBS:
        m = dc[j].is_not_null().to_numpy()
        y = dc[j].to_numpy().astype(float)[m]
        _, predK = L.lopo_r2(y, dc["K"].to_numpy().astype(float)[m][:, None])
        _, predR = L.lopo_r2(y, L.regime_dummies(dc["regime"].to_numpy()[m]))
        sd = float(np.std(y - predK, ddof=1))
        full = np.full(dc.height, np.nan)
        full[m] = predK
        fr = np.full(dc.height, np.nan)
        fr[m] = predR
        pts[f"{j}_predK"] = full.tolist()
        pts[f"{j}_predReg"] = fr.tolist()
        pts[f"{j}_zK"] = ((dc[j].to_numpy().astype(float) - full) / sd).tolist()
    pl.DataFrame(pts).write_parquet(RES / "phase_points.parquet")
    print("wrote", RES)


if __name__ == "__main__":
    main()
