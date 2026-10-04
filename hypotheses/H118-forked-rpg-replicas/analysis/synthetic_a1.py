"""H118 Amendment-1 supplementary synthetic (2026-10-04, after synthetic.py, before any real-data statistic).
Evaluates two replacement rules on the same planted worlds (synthetic.simulate):
  (1) plateau prediction-interval rule: q_late(G35) > mean(band) + t_{4,0.95} sd(band) sqrt(1 + 1/5);
  (2) slow-memory rule: day-2 excess E2 = q_eq(2) - q_late with an agent x bin bootstrap 95% lower bound > 0;
  plus the memory rule M_late (mean of M(d), d >= 2) with the agent x bin bootstrap interval.
Writes data/processed/H118-forked-rpg-replicas/synthetic/summary_a1.json
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h118lib as L  # noqa: E402
import synthetic as S  # noqa: E402

T4 = 2.1318


def main(worlds=100, boot=100, seed=20261006):
    rng = np.random.default_rng(seed)
    sk = {p: L.period_data(p) for p in S.PER}
    taus = {"W0": 2.0, "W1": 48.0, "W2": 2.0, "W3": 2.0, "W4": 200.0}
    summ = {}
    for variant in ("eq", "var"):
        for world, tau in taus.items():
            if variant == "var" and world not in ("W0", "W2"):
                continue
            pi, slow, mlate = [], [], []
            for _ in range(worlds):
                ql = {}
                for p in S.PER:
                    gv = S.CAL["g"] * (np.exp(rng.uniform(np.log(0.5), np.log(2))) if variant == "var" else 1.0)
                    s = dict(sk[p])
                    s["X"] = S.simulate(s, world, rng, gv, tau)
                    r = L.overlap_stats(s)
                    ql[p] = r["q_late"]
                    if p == "35":
                        bs = L.bootstrap(s, kind="agent_bin", B=boot, rng=rng)
                        e2 = [b["q_eq_d"].get(2, np.nan) - b["q_late"] for b in bs]
                        slow.append(L.ci(e2)[0] > 0)
                        lo, hi = L.ci([b["M_late"] for b in bs])
                        mlate.append(not (lo <= 0 <= hi))
                band = np.array([ql[p] for p in L.BAND])
                pi.append(ql["35"] > band.mean() + T4 * band.std(ddof=1) * np.sqrt(1 + 1 / 5))
            summ[f"{world}_{variant}"] = {"planted_tau_h": tau, "worlds": worlds,
                                          "plateau_PI_rule": float(np.mean(pi)),
                                          "slow_E2_rule": float(np.mean(slow)),
                                          "M_late_rejects0": float(np.mean(mlate))}
            print(world, variant, summ[f"{world}_{variant}"], flush=True)
    (L.DATA / "synthetic" / "summary_a1.json").write_text(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
