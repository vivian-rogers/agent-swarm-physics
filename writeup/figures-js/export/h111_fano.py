"""H111 Fano sum rule (Fig. fig:fano): (a) simulated linear Hawkes talk swarm, Fano ratio vs loop gain with the sum-rule
curve; (b) village units, observed vs predicted Fano ratio, by regime, with the pooled r_F per regime.

    uv run python writeup/figures-js/export/h111_fano.py

Reuses simulate / phi_pred / load from writeup/visuals/H111-talk-fano-sum-rule/make.py (the old fig_col.pdf), so the
simulation (same seeds) and the unit rows are identical. load() asserts the units are outside the reserved data.
The 95% interval of each unit's prediction is the old script's delta-method interval from g's SE.
"""
from __future__ import annotations

import importlib.util
import sys

import numpy as np
import polars as pl

from common import ROOT, write


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


sc = load_module("shared_common", ROOT / "infra/shared/common.py")
_ours = sys.modules["common"]; sys.modules["common"] = sc
mk = load_module("h111make", ROOT / "writeup/visuals/H111-talk-fano-sum-rule/make.py")
sys.modules["common"] = _ours

N_SIM, GS, RUNS = 15, [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6], 8


def main():
    # (a) simulation, exactly as panel_a of the old script
    gs = np.array(GS)
    reps = np.array([[mk.simulate(g, n=N_SIM, seed=100 * i + k) for k in range(RUNS)] for i, g in enumerate(gs)])
    m = reps.mean(1)
    lo, hi = np.percentile(reps, [2.5, 97.5], axis=1)
    gg = np.linspace(0, 0.62, 125)
    sim = dict(n=N_SIM, runs=RUNS, points=[dict(g=g, mean=a, lo=b, hi=c) for g, a, b, c in zip(gs, m, lo, hi)],
               curve=[dict(g=x, rule=float(mk.phi_pred(x, N_SIM)), plain=float(1 / (1 - x) ** 2)) for x in gg],
               null_band=[float(lo[0]), float(hi[0])])
    # (b) village units, as panel_b of the old script
    u, s = mk.load()
    units = []
    for r in u.iter_rows(named=True):
        dphi = (mk.phi_pred(r["g"] + 1e-4, r["N_present"]) - mk.phi_pred(r["g"] - 1e-4, r["N_present"])) / 2e-4
        xe = 1.96 * abs(float(dphi)) * r["g_se"]
        units.append(dict(unit=r["unit_id"], regime=r["regime"], g=r["g"], pred=r["phi_pred"], pred_lo=r["phi_pred"] - xe,
                          pred_hi=r["phi_pred"] + xe, obs=r["phi_10"], obs_lo=r["phi_10_lo"], obs_hi=r["phi_10_hi"],
                          r_F=r["r_F"]))
    nreg = {k: sum(1 for x in units if x["regime"] == k) for k in ("I", "II", "III")}
    r3, r1 = s["r_F_pooled_III"][:3], s["r_F_pooled_I"][:3]
    assert nreg["III"] == 18 and nreg["I"] == 21, nreg
    assert [round(v, 2) for v in r3] == [1.01, 0.94, 1.09] and [round(v, 2) for v in r1] == [1.34, 1.18, 1.52], (r3, r1)
    within = sum(abs(x["r_F"] - 1) <= 0.2 for x in units if x["regime"] == "III")
    assert within == 14, within                                               # paper: 14/18 within +-20%
    q95 = float(u["phi_null_q95"].median())
    print("sim means", np.round(m, 3).tolist(), "units", nreg, "within20", within, "null q95 median", round(q95, 3))
    write("h111_fano", dict(sim=sim, units=units, n=nreg, rF_III=r3, rF_I=r1, null_q95_median=q95, within20_III=within),
          "writeup/figures-js/export/h111_fano.py",
          ["data/processed/H111-talk-fano-sum-rule/results/units.parquet", "results/summary.json"],
          dict(sim_n=N_SIM, sim_g=GS, sim_runs=RUNS, sim_T_min=24000, window_min=10, block_min=60, min_windows=40))


if __name__ == "__main__":
    main()
