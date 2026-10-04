"""H70 axis F: the kappa-row estimator on planted worlds built on the real event skeleton (before real outcomes).

The skeleton keeps agents, periods, days, event types and the real channel flags and pointers (pre-outcome
structure). Outcomes are simulated:
  V ~ Poisson(lam_agent * exp(-0.3 * scramble) * (1 + 0.3 * open)^r2 * (1 + v * open * scramble))
  X = A_prev w.p. p_ret, else a random repo of the agent's period set, and 'none' w.p. 0.3 (independent of S if p=0)
Worlds: value (v = 0.3, r2 = 1), reading-precedes-writing (v = 0, r2 = 1), null (v = 0, r2 = 0).
Writes data/processed/H70-artifact-store-semantic-info/synthetic/synthetic.json.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h70lib as L  # noqa: E402

K = L.K
WORLDS = {"value": (0.3, 1), "reading_precedes_writing": (0.0, 1), "null": (0.0, 0)}


def plant(ev: pl.DataFrame, v: float, r2: int, p_ret: float, rng) -> pl.DataFrame:
    ag = ev["agent"].to_numpy()
    lam = {a: rng.uniform(0.3, 3.0) for a in np.unique(ag)}
    sc = ev["etype"].is_in(["F", "N"]).to_numpy()
    op = ev["openA"].to_numpy()
    mu = np.array([lam[a] for a in ag]) * np.exp(-0.3 * sc) * (1 + 0.3 * op) ** r2 * (1 + v * op * sc)
    V = rng.poisson(mu).astype(float)
    # repo sets per agent-period from the real pointers (A_prev values)
    sets = (ev.filter(pl.col("A_prev") >= 0).group_by("agent", "period").agg(pl.col("A_prev").unique())
            .to_dicts())
    rs = {(d["agent"], d["period"]): np.array(d["A_prev"]) for d in sets}
    A = ev["A_prev"].to_numpy()
    per = ev["period"].to_list()
    X = np.empty(len(A), dtype=np.int64)
    for i in range(len(A)):
        if rng.random() < 0.3:
            X[i] = -1
            continue
        pool = rs.get((ag[i], per[i]))
        if A[i] >= 0 and rng.random() < p_ret:
            X[i] = A[i]
        elif pool is not None and len(pool):
            X[i] = int(rng.choice(pool))
        else:
            X[i] = -1
    return ev.with_columns(pl.Series("V", V), pl.Series("X_next", X))


def main(reps: int = 12):
    ev0 = L.load_events()
    res = {}
    for scale, periods in (("call", ["G51", "G38", "G41"]), ("day", ["G51", "G38", "G31"])):
        for per in periods + ["pooled"]:
            if per == "pooled" and scale == "day":
                e = ev0.filter(pl.col("goal_no") >= 30)
            elif per == "pooled":
                e = ev0.filter(pl.col("regime") == "III")
            else:
                e = ev0.filter(pl.col("period") == per)
            key = f"{scale}:{per}"
            res[key] = {}
            for wname, (v, r2) in WORLDS.items():
                for p_ret in (0.0, 0.6):
                    dvs, Is, Ip, sig = [], [], [], []
                    for k in range(reps):
                        rng = np.random.default_rng(10_000 + 97 * k + int(100 * p_ret))
                        sim = plant(e, v, r2, p_ret, rng)
                        r = K.kappa_row(L.frame(sim, scale, "A"), n_perm=30, B=50, n_perm_boot=3, seed=k)
                        dvs.append(r["dV_rel"])
                        lo, hi = r["dV_rel_ci"]
                        sig.append(lo is not None and (lo > 0 or hi < 0))
                        Is.append(r["I"])
                        Ip.append(r["p_perm"])
                    vbar = float(sim["V"].filter(sim["etype"].is_in(["P", "PN"])).mean())
                    res[key][f"{wname}|p{p_ret}"] = {
                        "dV_rel_mean": float(np.mean(dvs)), "dV_rel_sd": float(np.std(dvs)), "planted_dV_rel": v,
                        "reject_rate": float(np.mean(sig)), "I_mean": float(np.mean(Is)), "I_sd": float(np.std(Is)),
                        "I_p_lt_05": float(np.mean(np.array(Ip) < 0.05)), "V_placebo_mean": vbar,
                        "n_scramble": int(r["n_scramble"]), "n_placebo": int(r["n_placebo"]), "reps": reps}
                    print(key, wname, p_ret, {k2: round(v2, 3) if isinstance(v2, float) else v2
                                              for k2, v2 in res[key][f'{wname}|p{p_ret}'].items()}, flush=True)
    (L.OUT / "synthetic").mkdir(parents=True, exist_ok=True)
    (L.OUT / "synthetic/synthetic.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 12)
