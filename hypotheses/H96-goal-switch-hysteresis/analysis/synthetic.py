"""H96 synthetic validation (axis F), run before any real-data outcome.

Planted statement vectors on the real statement skeleton (agents, times, days) of every eligible non-holdout statement:
  s_r = unit( A_c c_g + A_k k_g + A_v v_reg + A_p p_a + rem_r c_{P-1} + xi_r )
  c_g   random unit topic of period g, amplitude A_c,g ~ U(0.3, 0.9) per period (sets the old state's order q)
  k_g   the real whitened kickoff of g (random unit where none)
  v_reg a regime-wide village direction; p_a an agent prior (random units)
  xi_r  real within-agent-day residual rows (s - agent-day mean), permuted across rows of the regime (real anisotropy)
  rem_r = A_c,{P-1} exp(-h/tau_P) for statements of P after its kickoff (h active hours), else 0
Scenarios: S0 quench (tau 0.1 h), S1 lag (tau 8 h, no order dependence), S2 hysteresis (tau 8 h at the median old
amplitude, doubling across its interquartile range), S3 long lag (tau 30 h). The full pipeline runs unchanged.
Outputs: data/processed/H96-goal-switch-hysteresis/synthetic/synthetic.json
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h96lib as L  # noqa: E402

OUTD = L.DATA / "synthetic"
A_K, A_V, A_P = 0.5, 0.4, 0.6
SCEN = {"S0_quench": dict(tau=0.1, beta=0.0), "S1_lag": dict(tau=8.0, beta=0.0),
        "S2_hysteresis": dict(tau=8.0, beta=1.0), "S3_long": dict(tau=30.0, beta=0.0)}


def residual_pool(S: L.Store):
    """Real within-agent-day residuals per regime (rows), the noise pool."""
    keys = np.char.add(np.char.add(S.agent.astype(str), "|"), S.day.astype(str))
    _, inv = np.unique(keys, return_inverse=True)
    sums = np.zeros((inv.max() + 1, 32)); cnt = np.bincount(inv)
    np.add.at(sums, inv, S.X)
    mean = sums / cnt[:, None]
    R = S.X - mean[inv]
    R[cnt[inv] < 2] = 0
    return R.astype(np.float32)


def kickoff_h(S: L.Store, recs):
    """For every statement of a transition's new period after its kickoff: active hours since t0 and P-1."""
    h = np.full(len(S.agent), np.nan); prev = np.full(len(S.agent), -1)
    for r in recs:
        rows = S.rows(r["post_days"], t_lo=r["t0"])
        rows = rows[S.goal[rows] == r["P"]]
        h[rows] = S.active_hours(rows, r["t0"], r["post_days"])
        prev[rows] = r["Pm1"]
    return h, prev


def plant(S, R, recs, h, prev, tau_of, amp, rng):
    n = len(S.agent)
    goals = np.unique(S.goal)
    C = {g: L.unit(rng.standard_normal(32)) for g in goals}
    Kreg = {}
    V = {r: L.unit(rng.standard_normal(32)) for r in ("I", "II", "III")}
    P = {a: L.unit(rng.standard_normal(32)) for a in np.unique(S.agent)}
    reg = S.st["regime"].to_numpy()
    X = np.zeros((n, 32), np.float32)
    for g in goals:
        m = S.goal == g
        r0 = reg[m][0]
        k = S.kickoff_vec(int(g), r0)
        k = k if k is not None else L.unit(rng.standard_normal(32))
        X[m] += amp[g] * C[g] + A_K * k
    for r0 in V:
        X[reg == r0] += A_V * V[r0]
    for a in P:
        X[S.agent == a] += A_P * P[a]
    # remanence of the old period's topic after the switch
    m = np.isfinite(h)
    for g in np.unique(prev[m]):
        mm = m & (prev == g)
        tau = tau_of[int(g) + 1]
        X[mm] += (amp[g] * np.exp(-h[mm] / tau))[:, None] * C[g][None, :]
    # noise: real residuals permuted within regime
    for r0 in ("I", "II", "III"):
        idx = np.flatnonzero(reg == r0)
        X[idx] += R[rng.permutation(idx)]
    return L.unit(X)


def main(n_rep: int = 40, seed: int = 7, out_name: str = "synthetic.json"):
    OUTD.mkdir(parents=True, exist_ok=True)
    S = L.Store("bge_small", "style_resid32")
    R = residual_pool(S)
    recs = L.transition_records()
    h, prev = kickoff_h(S, recs)
    rng = np.random.default_rng(seed)
    res = {}
    t_start = time.time()
    for name, sc in SCEN.items():
        reps = []
        for rep in range(n_rep):
            amp = {g: rng.uniform(0.3, 0.9) for g in np.unique(S.goal)}
            olds = np.array([amp[r["Pm1"]] for r in recs])
            q25, q50, q75 = np.percentile(olds, [25, 50, 75])
            tau_of = {}
            for r in recs:
                z = (amp[r["Pm1"]] - q50) / max(q75 - q25, 1e-6)
                tau_of[r["P"]] = sc["tau"] * 2.0 ** (sc["beta"] * z)
            X = plant(S, R, recs, h, prev, tau_of, amp, rng)
            rows = []
            for r in recs:
                pr = L.projections(S, X, r)
                s = L.summarize(pr, n_boot=60, seed=rep)
                rows.append({"P": r["P"], "tau_true": tau_of[r["P"]], "amp_old": amp[r["Pm1"]], "q": s["q"],
                             "tau": s["tau"]["est"], "tau_lo": s["tau"]["lo"], "tau_hi": s["tau"]["hi"],
                             "R1": s["R1"]["est"], "Mpre": s["M_pre"]["est"], "Mpre_lo": s["M_pre"]["lo"],
                             "tau_sw": s["tau_sw"]["est"]})
            # pseudo-switch reference (sample of 30 for speed)
            ps = L.pseudo_records()
            pick = rng.choice(len(ps), size=min(30, len(ps)), replace=False)
            r1p = [L.summarize(L.projections(S, X, ps[j]), n_boot=0)["R1"]["est"] for j in pick]
            okr = [x for x in rows if np.isfinite(x["tau"]) and x["Mpre_lo"] > 0]
            rho, p = (spearmanr([x["q"] for x in okr], np.log([x["tau"] for x in okr])) if len(okr) >= 5
                      else (np.nan, np.nan))
            oks = [x for x in rows if np.isfinite(x["tau_sw"]) and x["Mpre_lo"] > 0]
            rho_sw, p_sw = (spearmanr([x["q"] for x in oks], np.log([x["tau_sw"] for x in oks])) if len(oks) >= 5
                            else (np.nan, np.nan))
            reps.append({"rows": rows, "rho_q_logtau": float(rho), "p_two": float(p),
                         "rho_q_logtau_sw": float(rho_sw), "n_ok_sw": len(oks),
                         "p_one": float(p / 2 if rho > 0 else 1 - p / 2) if np.isfinite(p) else None,
                         "n_ok": len(okr), "R1_pseudo_median": float(np.nanmedian(r1p))})
            print(name, rep, f"rho_sw {rho_sw:+.2f} n_sw {len(oks)} rho {rho:+.2f} n {len(okr)} R1p {np.nanmedian(r1p):.2f} t {time.time()-t_start:.0f}s",
                  flush=True)
        # summaries
        allr = [x for rp in reps for x in rp["rows"]]
        ok = [x for x in allr if np.isfinite(x["tau"]) and x["Mpre_lo"] > 0]
        lt = np.log([x["tau"] for x in ok]); lt0 = np.log([x["tau_true"] for x in ok])
        cover = np.mean([(x["tau_lo"] <= x["tau_true"] <= x["tau_hi"]) for x in ok]) if ok else np.nan
        rhos = np.array([rp["rho_q_logtau"] for rp in reps]); ps1 = np.array([rp["p_one"] or 1 for rp in reps])
        oksw = [x for x in allr if np.isfinite(x["tau_sw"]) and x["Mpre_lo"] > 0]
        ltw = np.log([x["tau_sw"] for x in oksw]); ltw0 = np.log([x["tau_true"] for x in oksw])
        res[name] = {"scenario": sc, "n_rep": n_rep, "identified_share": len(ok) / len(allr),
                     "sw_identified_share": len(oksw) / len(allr),
                     "log_tau_sw_bias_median": float(np.median(ltw - ltw0)) if oksw else None,
                     "log_tau_sw_abs_err_median": float(np.median(np.abs(ltw - ltw0))) if oksw else None,
                     "rho_sw_median": float(np.nanmedian([rp["rho_q_logtau_sw"] for rp in reps])),
                     "rho_sw_p95": float(np.nanpercentile([rp["rho_q_logtau_sw"] for rp in reps], 95)),
                     "rho_p95": float(np.nanpercentile([rp["rho_q_logtau"] for rp in reps], 95)),
                     "log_tau_bias_median": float(np.median(lt - lt0)) if ok else None,
                     "log_tau_abs_err_median": float(np.median(np.abs(lt - lt0))) if ok else None,
                     "tau_ci_coverage": float(cover),
                     "R1_median": float(np.nanmedian([x["R1"] for x in allr])),
                     "R1_pseudo_median": float(np.nanmedian([rp["R1_pseudo_median"] for rp in reps])),
                     "rho_median": float(np.nanmedian(rhos)), "reject_rate_one_sided_0.05": float(np.mean(ps1 < 0.05)),
                     "reps": reps}
        print(name, {k: v for k, v in res[name].items() if k != "reps"}, flush=True)
    (OUTD / out_name).write_text(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 40, 7, sys.argv[2] if len(sys.argv) > 2 else "synthetic.json")
