"""Calibrate the synthetic world from NON-TEST periods along RANDOM directions only (no goal vector is used).

Regime I: #8, #10, #13, #18-#21, #24-#27, #30. Regime III: #39-#42, #44. None of these is a pre- or post-period of
an H10 pair. Outputs data/processed/H10-goals-are-legendre-pushes/calibration.json.

Usage: uv run python hypotheses/H10-goals-are-legendre-pushes/analysis/calibrate.py
"""
from __future__ import annotations

import numpy as np

from h10data import DATA, load_period, save_json
from h10lib import agent_cov, agent_stats, aggregate, random_transverse, swarm_stats

CAL = {"I": [8, 10, 13, 18, 19, 20, 21, 24, 25, 26, 27, 30], "III": [39, 40, 41, 42, 44]}
TEST = {"I": [3, 4, 5, 6, 11, 12, 16, 17, 31], "III": [37, 38]}


def main():
    rng = np.random.default_rng(7)
    out = {"periods": {}, "counts": {}}
    for reg, gl in CAL.items():
        for gno in gl:
            P = load_period(gno)
            g0 = rng.standard_normal(32)
            U = random_transverse(g0, 19, rng)  # 20 random directions (column 0 is random too)
            seg = aggregate(P["Z"], P["agent"], P["day"], P["win"], U)
            st = agent_stats(seg)
            sw = swarm_stats(seg, st)
            a, mu, C = agent_cov(seg)
            y = P["Z"] @ U
            var_stmt = float(y.var(0).mean())
            xm = seg.S1 / seg.c[:, None]
            res2 = (xm ** 2).sum(1)
            # E|xbar|^2 = a2 + (1 - a2)/c  ->  least squares for a2
            A_ = 1 - 1 / seg.c
            a2 = float(((res2 - 1 / seg.c) * A_).sum() / (A_ ** 2).sum())
            # lag-1 autocorrelation of aw projections within agent-day (consecutive windows)
            x = xm @ U
            ac = []
            for ag in np.unique(seg.agent):
                for d in np.unique(seg.day[seg.agent == ag]):
                    s = (seg.agent == ag) & (seg.day == d)
                    if s.sum() >= 4:
                        xs = x[s] - x[seg.agent == ag].mean(0)
                        ac.append(((xs[1:] * xs[:-1]).mean(0) / (xs ** 2).mean(0)).mean())
            trC = np.array([np.trace(c) for c in C]) if len(C) else np.array([np.nan])
            out["periods"][gno] = {
                "regime": reg, "n_agents": int(len(st.agents)), "n_aw": int(len(seg.c)),
                "n_days": len(P["days"]), "win_per_day": float(len(np.unique(seg.win)) / len(P["days"])),
                "var_stmt": var_stmt, "k2_mean": float(np.mean(st.k2)), "r_sig": float(np.mean(st.k2) / var_stmt),
                "mu_between_var": float(np.var(st.mu, axis=0).mean()), "mu_between_rel": float(np.var(st.mu, axis=0).mean() / var_stmt),
                "trC_mean": float(np.nanmean(trC)), "trC_cv": float(np.nanstd(trC) / np.nanmean(trC)),
                "k2_cv_dir_mean": float(np.mean(np.std(st.k2, 0) / np.abs(np.mean(st.k2, 0)))),
                "R_median": float(np.nanmedian(sw["R"])) if sw else None, "g_median": float(np.nanmedian(sw["g"])) if sw else None,
                "a2_window": a2, "lag1_ac": float(np.nanmean(ac)) if ac else None,
                "gamma_median": float(np.nanmedian(st.gamma)), "eta_median": float(np.nanmedian(st.eta)),
                "c_q10_50_90": [float(q) for q in np.quantile(seg.c, [0.1, 0.5, 0.9])],
            }
            print(gno, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in out["periods"][gno].items()}, flush=True)
    for reg, gl in TEST.items():
        for gno in gl:
            P = load_period(gno)
            U = random_transverse(rng.standard_normal(32), 1, rng)
            seg = aggregate(P["Z"], P["agent"], P["day"], P["win"], U)
            out["counts"][gno] = {"c": seg.c.astype(int).tolist(), "n_agents": int(len(np.unique(seg.agent))),
                                  "n_days": len(P["days"]), "n_win": int(len(np.unique(seg.win)))}
    for reg in CAL:
        vals = [v for v in out["periods"].values() if v["regime"] == reg]
        out[f"summary_{reg}"] = {k: float(np.nanmedian([v[k] for v in vals if v[k] is not None]))
                                 for k in ("var_stmt", "r_sig", "mu_between_rel", "trC_cv", "k2_cv_dir_mean", "R_median",
                                           "g_median", "a2_window", "lag1_ac", "gamma_median", "eta_median", "win_per_day")}
        print(reg, out[f"summary_{reg}"])
    save_json(out, DATA / "calibration.json")


if __name__ == "__main__":
    main()
