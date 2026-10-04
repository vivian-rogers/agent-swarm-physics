"""H19 synthetic validation (axis F): can the meta-regression + P1 decision rule tell a true collapse from
method-specific scatter, regime steps, an era trend or a size effect, at the real number of periods and SEs?

Design = the real one: the 9 non-validation methods, each with its actual periods and actual standard errors, and the
actual control parameters of those periods (x_att, regime, date, N), so the real collinearity (x_att is higher in
regime III) is built in. Per method, the intercept a_m and the total between-period SD tau_m are set to the real
intercept-only REML values; a truth explains a fraction R2 of tau_m^2 and the rest is method noise, with a shared
period component (rho_u = 0.3 of the residual variance, common to all methods).

Truths:
  null              no period structure
  collapse_R{25,50,75}  every method affine-increasing in x_att (positive scale), R2 = 0.25 / 0.5 / 0.75
  scatter_sign      every method linear in x_att but with an independent random sign (R2 = 0.5): no common curve
  scatter_control   every method driven by a different, randomly chosen control (R2 = 0.5): no common curve
  regime            same-sign regime step (II halfway between I and III), R2 = 0.5
  era               same-sign linear trend in calendar date, R2 = 0.5
  logN              same-sign effect of log N_roster, R2 = 0.5

Output: data/processed/H19-loop-gain-collapse/synthetic/{runs.parquet, summary.json}
Usage: uv run python hypotheses/H19-loop-gain-collapse/analysis/synthetic.py [n_rep]
"""
from __future__ import annotations

import json
import sys
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import h19common as C  # noqa: E402
import h19lib as L  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

XP = "x_att_village"
PRIMARIES = ("H03.n_talk", "H19.geq_active")
RHO_U = 0.3
SCAN = ["x_att_village", "x_att_llm", "N_roster", "N_room", "m_turn_llm", "m_turn_village", "m_hour", "k_village",
        "k_llm", "hours_emp", "human_share", "date_mid"]
TRUTHS = ["null", "collapse_R25", "collapse_R50", "collapse_R75", "scatter_sign", "scatter_control", "regime", "era", "logN"]


def load_design():
    est = pl.read_parquet(C.OUT / "estimates.parquet").filter(~pl.col("validation_only"))
    ctr = pl.read_parquet(C.OUT / "controls.parquet")
    ctrd = {r["goal_no"]: r for r in ctr.iter_rows(named=True)}
    allg = sorted(ctrd)

    def z(v):
        v = np.asarray(v, float)
        return (v - v.mean()) / v.std()

    Z = {k: dict(zip(allg, z([ctrd[g][k] for g in allg]))) for k in SCAN}
    Z["logN"] = dict(zip(allg, z([np.log(ctrd[g]["N_roster"]) for g in allg])))
    reg = np.array([{"I": 0.0, "II": 0.5, "III": 1.0}[ctrd[g]["regime"]] for g in allg])
    Z["regime"] = dict(zip(allg, z(reg)))
    design = {}
    for (m,), d in est.group_by(["method"], maintain_order=True):
        rows = [dict(ctrd[g]) for g in d["goal_no"].to_list()]
        y, s = d["value"].to_numpy(), d["se"].to_numpy()
        f0 = L.reml_fit(y, s, np.ones((len(y), 1)))
        design[m] = {"goals": d["goal_no"].to_list(), "rows": rows, "s": s, "a": float(f0["b"][0]),
                     "tau": float(np.sqrt(max(f0["tau2"], (0.5 * np.median(s)) ** 2)))}
    return design, Z, allg


def simulate(truth: str, design, Z, allg, rng):
    u = dict(zip(allg, rng.normal(size=len(allg))))  # shared period component
    R2 = {"collapse_R25": 0.25, "collapse_R75": 0.75}.get(truth, 0.0 if truth == "null" else 0.5)
    out = {}
    for m, D in design.items():
        g = D["goals"]
        if truth.startswith("collapse") or truth == "scatter_sign":
            sig = 1.0 if truth.startswith("collapse") else rng.choice([-1.0, 1.0])
            L_ = sig * np.array([Z[XP][x] for x in g])
        elif truth == "scatter_control":
            L_ = np.array([Z[SCAN[rng.integers(len(SCAN))]][x] for x in g]) * rng.choice([-1.0, 1.0])
        elif truth in ("regime", "era", "logN"):
            key = {"regime": "regime", "era": "date_mid", "logN": "logN"}[truth]
            L_ = np.array([Z[key][x] for x in g])
        else:
            L_ = np.zeros(len(g))
        resid = np.sqrt(RHO_U) * np.array([u[x] for x in g]) + np.sqrt(1 - RHO_U) * rng.normal(size=len(g))
        y = D["a"] + D["tau"] * (np.sqrt(R2) * L_ + np.sqrt(1 - R2) * resid) + D["s"] * rng.normal(size=len(g))
        out[m] = y
    return out


_CACHE = {}


def run_one(args):
    truth, rep, seed = args
    if "d" not in _CACHE:
        _CACHE["d"] = load_design()
    design, Z, allg = _CACHE["d"]
    rng = np.random.default_rng(seed)
    Y = simulate(truth, design, Z, allg, rng)
    per = {}
    for m, D in design.items():
        rows = [dict(r, y=float(yv), s=float(sv)) for r, yv, sv in zip(D["rows"], Y[m], D["s"])]
        per[m] = L.method_fits(rows, XP)
    dec = L.p1_decision(per, PRIMARIES, XP)
    # collapse quality Q (scatter relative to measurement error only), x model vs constant
    Qx, Q0, nobs = 0.0, 0.0, 0
    for m, fm in per.items():
        y = Y[m]; s = design[m]["s"]
        X1, _ = L.design(design[m]["rows"], "x", XP); X0 = np.ones((len(y), 1))
        Qx += float(np.sum((y - X1 @ fm["x"]["fit"]["b"]) ** 2 / s ** 2)); Q0 += float(np.sum((y - X0 @ fm["const"]["fit"]["b"]) ** 2 / s ** 2))
        nobs += len(y)
    return {"truth": truth, "rep": rep, "verdict": dec["verdict"], "a": dec["a_sign"], "b": dec["b_r2"], "c": dec["c_rivals"],
            "slope_T1": dec["slopes"]["H03.n_talk"]["b"], "slope_E1": dec["slopes"]["H19.geq_active"]["b"],
            "r2_T1": dec["r2_het"]["H03.n_talk"], "r2_E1": dec["r2_het"]["H19.geq_active"],
            "d_const": dec["elpd_x_minus_rival"]["const"], "d_regime": dec["elpd_x_minus_rival"]["regime"],
            "d_era": dec["elpd_x_minus_rival"]["era"], "d_logN": dec["elpd_x_minus_rival"]["logN"],
            "n_neg_slopes": int(sum(v["hi"] < 0 for v in dec["slopes"].values())),
            "n_pos_slopes": int(sum(v["lo"] > 0 for v in dec["slopes"].values())),
            "Q_ratio": Qx / Q0, "Qx_per_dof": Qx / (nobs - 2 * len(per))}


def main():
    nrep = int(sys.argv[1]) if len(sys.argv) > 1 else 150
    jobs = [(t, r, 1000003 * (i + 1) + r) for i, t in enumerate(TRUTHS) for r in range(nrep)]
    with Pool(2) as pool:
        res = pool.map(run_one, jobs, chunksize=4)
    df = pl.DataFrame(res)
    (C.OUT / "synthetic").mkdir(parents=True, exist_ok=True)
    df.write_parquet(C.OUT / "synthetic/runs.parquet", compression="zstd")
    summ = {}
    for (t,), d in df.group_by(["truth"], maintain_order=True):
        summ[t] = {"n": d.height, "P_supported": float((d["verdict"] == "supported").mean()),
                   "P_mixed": float((d["verdict"] == "mixed").mean()), "P_failed": float((d["verdict"] == "failed").mean()),
                   "P_a": float(d["a"].mean()), "P_b": float(d["b"].mean()), "P_c": float(d["c"].mean()),
                   "median_d_regime": float(d["d_regime"].median()), "median_d_const": float(d["d_const"].median()),
                   "median_Q_ratio": float(d["Q_ratio"].median()), "median_r2_T1": float(d["r2_T1"].median()),
                   "median_r2_E1": float(d["r2_E1"].median()), "mean_n_neg_slopes": float(d["n_neg_slopes"].mean())}
    (C.OUT / "synthetic/summary.json").write_text(json.dumps(summ, indent=1))
    C.write_provenance("synthetic", "hypotheses/H19-loop-gain-collapse/analysis/synthetic.py",
                       [{"source": "data/processed/H19-loop-gain-collapse", "tables": ["estimates.parquet (SEs, periods)", "controls.parquet"]}],
                       {"n_rep": nrep, "truths": TRUTHS, "rho_u": RHO_U, "x": XP, "primaries": PRIMARIES})
    for t, s in summ.items():
        print(f"{t:16s} sup {s['P_supported']:.2f} mix {s['P_mixed']:.2f} fail {s['P_failed']:.2f} | a {s['P_a']:.2f} b {s['P_b']:.2f} "
              f"c {s['P_c']:.2f} | dELPD(x-regime) {s['median_d_regime']:+.1f} | Q {s['median_Q_ratio']:.2f} | neg slopes {s['mean_n_neg_slopes']:.1f}")


if __name__ == "__main__":
    main()
