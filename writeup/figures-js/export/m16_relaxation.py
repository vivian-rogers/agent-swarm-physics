"""Model 16 (Langevin relaxation) paper figure, single column: a fast read kick on a slow, overdamped well.

    uv run python writeup/figures-js/export/m16_relaxation.py

Reuses writeup/papers/thermodynamics/figs/make_model16.py: panel_a() and panel_b() compute the shown numbers (drawn on a throwaway
matplotlib axis and discarded), and the simulation of panel_c() is repeated here with the same code and seed.
(a) H125 kickoff day profile, bge and gte, 90% CI, and the card's U; (b) H130 #51 own well vs read kick, each divided
by its fitted amplitude, with the e^{-gamma n} fits and the rate ratio; (c) x = s + k simulation at the H130 rates.
Inputs (all non-reserved by construction of the H125 / H130 schemes: 27 non-holdout kickoffs, #51 non-holdout units):
  data/processed/H125-kickoff-damped-oscillator/NE34/{series.json, card.json}
  data/processed/H130-ou-private-wells-51/results/{natives.json, summary.json}
"""
from __future__ import annotations

import importlib.util

import numpy as np

from common import ROOT, write


def load_m16():
    spec = importlib.util.spec_from_file_location("make_model16", ROOT / "writeup/papers/thermodynamics/figs/make_model16.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def simulate(ga: float, gk: float, seed: int = 7):
    """Same as make_model16.panel_c: s is an OU well (rate ga per call), k a kick (rate gk) added at each read."""
    rng = np.random.default_rng(seed)
    n = 400
    reads = np.array([70, 150, 230, 245, 320])
    s = np.zeros(n); k = np.zeros(n)
    sig = 0.3 * np.sqrt(2 * ga)
    for t in range(1, n):
        s[t] = s[t - 1] * (1 - ga) + sig * rng.standard_normal()
        k[t] = k[t - 1] * (1 - gk) + (0.7 if t in reads else 0.0)
    return dict(s=s, x=s + k, reads=reads)


def main():
    import matplotlib.pyplot as plt
    m16 = load_m16()
    fig, ax = plt.subplots(1, 2)
    sa, card = m16.panel_a(ax[0])
    sb = m16.panel_b(ax[1])
    plt.close(fig)
    days = list(range(1, 11))
    prof = {}
    for lab in ("bge", "gte"):
        mm, ci, nn = sa[lab]
        prof[lab] = [dict(day=d, m=float(mm[i]), lo=float(mm[i] - ci[i]), hi=float(mm[i] + ci[i]), n=int(nn[i]))
                     for i, d in enumerate(days)]
    ub = card["bge_white"]
    U = dict(U=ub["U"], lo=ub["U_lo"], hi=ub["U_hi"], k=ub["k"])
    s = sb["summ"]
    well = [dict(lag=float(t), y=float(y)) for t, y in zip(sb["Ct"], sb["yC"])]
    kick = [dict(lag=float(t), y=float(y), se=float(e)) for t, y, e in zip(sb["tK"], sb["yK"], sb["eK"])]
    sim = simulate(sb["g_auto_fit"], sb["g_kick_fit"])
    data = dict(profile=prof, U=U,
                well=well, kick=kick, g_well=sb["g_auto_fit"], g_kick=sb["g_kick_fit"],
                t_well=round(1 / sb["g_auto_fit"], -1), t_kick=round(1 / sb["g_kick_fit"]),
                rho=s["rho"], rho_ci90=s["rho_ci90"],
                sim=dict(s=sim["s"], x=sim["x"], reads=sim["reads"]))
    print("U bge", U, "| t_well", data["t_well"], "t_kick", data["t_kick"], "| rho", round(s["rho"], 2),
          [round(v, 2) for v in s["rho_ci90"]])
    print("bge profile:", [(p["day"], round(p["m"], 3), p["n"]) for p in prof["bge"]])
    write("m16_relaxation", data, "writeup/figures-js/export/m16_relaxation.py",
          ["data/processed/H125-kickoff-damped-oscillator/NE34/series.json", "NE34/card.json",
           "data/processed/H130-ou-private-wells-51/results/natives.json", "results/summary.json"],
          dict(ci="90%", sim_seed=7, sim_reads=[70, 150, 230, 245, 320]))


if __name__ == "__main__":
    main()
