"""H105 calibrated tilt test (Amendment 1): a parametric bootstrap of the two-state tilt at the real structure of one
design. The latent model (heterogeneous Curie-Weiss Glauber spins observed through statements, synthetic.py) is matched
to the design's measured free-week occupancy p_F and loop gain g_F (grid over the latent base rate and J) and to the
assigned week's measured occupancy p_A (grid over the uniform tilt LAM). Then N_SIM pairs are simulated under the tilt
(J unchanged) and under the coupling-change rival R5 (J_A = 2.5 J_F); the real rho_V and logit slope s are located in
both distributions. No real statistic other than p_F, g_F and p_A enters the null."""
from __future__ import annotations

import numpy as np

import h105lib as L
import synthetic as SY

P0_GRID = [0.01, 0.02, 0.04, 0.06, 0.1, 0.15, 0.2, 0.3, 0.4]
J_GRID = [0.0, 1.5, 3.0, 4.5]
LAM_GRID = np.arange(-1.0, 6.01, 0.25)


def _simF(rng, F, P0, J, n=8):
    out = []
    for _ in range(n):
        h = np.log(P0 / (1 - P0)) + rng.normal(0, SY.H_SD, len(F["agents"]))
        S, _ = SY.observe(rng, SY.glauber(rng, h, J, F["S"].shape[0]), F["N"])
        s = L.seg_stats(S)
        out.append((s["p"], s["g"]))
    a = np.array(out, float)
    return np.nanmean(a[:, 0]), np.nanmean(a[:, 1])


def _simA_p(rng, A, P0, J, lam, n=6):
    ps = []
    for _ in range(n):
        h = np.log(P0 / (1 - P0)) + rng.normal(0, SY.H_SD, len(A["agents"])) + lam
        S, _ = SY.observe(rng, SY.glauber(rng, h, J, A["S"].shape[0]), A["N"])
        ps.append(float(np.nanmean(np.nanmean(S, 1))))
    return float(np.mean(ps))


def calibrate(F, A, pF_obs, gF_obs, pA_obs, seed=0):
    rng = np.random.default_rng(seed)
    best = None
    for J in J_GRID:
        for P0 in P0_GRID:
            p, g = _simF(rng, F, P0, J)
            loss = ((p - pF_obs) / 0.02) ** 2 + ((g - gF_obs) / 0.15) ** 2 if np.isfinite(g) else 1e9
            if best is None or loss < best[0]:
                best = (loss, P0, J)
    _, P0, J = best
    lam_best, lb = None, None
    for lam in LAM_GRID:
        p = _simA_p(rng, A, P0, J, lam)
        d = abs(p - pA_obs)
        if lb is None or d < lb:
            lam_best, lb = lam, d
    return dict(P0=P0, J=J, LAM=float(lam_best), fit_loss=float(best[0]), pA_gap=float(lb))


def null_distribution(F, A, par, scen="H", n_sim=200, seed=1):
    rng = np.random.default_rng(seed)
    rhos, ss, dgs = [], [], []
    for _ in range(n_sim):
        n = len(F["agents"])
        hF = np.log(par["P0"] / (1 - par["P0"])) + rng.normal(0, SY.H_SD, n)
        hA = hF + par["LAM"]
        if scen == "R2":   # common target: every agent's field equal after the push (same mean push)
            hA = np.full(n, float(np.mean(hF)) + par["LAM"])
        JA = par["J"] * 2.5 if scen == "R5" else par["J"]
        if scen == "R5" and par["J"] == 0:
            JA = 3.0
        SF, KF = SY.observe(rng, SY.glauber(rng, hF, par["J"], F["S"].shape[0]), F["N"])
        SA, KA = SY.observe(rng, SY.glauber(rng, hA, JA, A["S"].shape[0]), A["N"])
        core = L.pair_core(SF, SA)
        rhos.append(core["rho"]); dgs.append(core["dg"])
        try:
            ss.append(L.logit_slope(dict(F, S=SF, K=KF), dict(A, S=SA, K=KA), n_boot=1)["s"])
        except Exception:  # noqa: BLE001
            ss.append(np.nan)
    return dict(rho=np.array(rhos), s=np.array(ss), dg=np.array(dgs))


def percentile(x, dist):
    d = dist[np.isfinite(dist)]
    if not np.isfinite(x) or len(d) == 0:
        return np.nan
    return float((np.sum(d < x) + 0.5 * np.sum(d == x)) / len(d))
