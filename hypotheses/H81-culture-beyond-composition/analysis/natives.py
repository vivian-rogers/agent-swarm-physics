"""H81 natives (non-holdout).

N1 G51  within-period slow common mode under private goals: cross-agent lagged residual alignment L(k) over #51 active
        days; L_slow = mean L(k), k = 5..15; null = independent circular shifts of each agent's day series (offset >= 5).
N2 NE33 (+NE32) coherent jump of the stayers (agents present on both days) at batch-join day boundaries, as a percentile
        among all other #51 within-period day boundaries (placebo). Composition alone predicts no stayer jump.

Output: data/processed/H81-culture-beyond-composition/natives/natives.json (+ G51 L(k) parquet)
Usage: uv run python hypotheses/H81-culture-beyond-composition/analysis/natives.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h81lib as L  # noqa: E402

MODELS = ["bge_small", "gte_modernbert"]
KMAX = 20
SLOW = range(5, 16)


def g51_arrays(model, drop=frozenset()):
    ad, X, blocks = L.load(model, "style_resid", "III", drop)
    P = L.projectors(model, "III", ad)
    pan = L.Panel(ad, blocks, P)
    m = pan.goal == 51
    Xp = L.project(pan, X)[m]
    agents = pan.agent[m]; days = pan.day[m]
    ud = np.unique(days); ua = np.unique(agents)
    ti = {d: k for k, d in enumerate(ud)}; ai = {a: k for k, a in enumerate(ua)}
    R = np.zeros((len(ud), len(ua), 32)); M = np.zeros((len(ud), len(ua)), bool)
    for x, a, d in zip(Xp, agents, days):
        R[ti[d], ai[a]] = x; M[ti[d], ai[a]] = True
    for j in range(len(ua)):  # within-#51 agent demeaning (newcomers have no other non-holdout period)
        mj = M[:, j]
        if mj.sum() >= 3:
            R[mj, j] -= R[mj, j].mean(0)
        else:
            R[:, j] = 0; M[:, j] = False
    # re-apply each agent's projector (agent-goal directions) after demeaning
    for j, a in enumerate(ua):
        Pi = P.get((51, a), P[(51, -1)])
        R[:, j] = R[:, j] @ Pi.T
    return R, M, ud


def lag_profile(R, M, kmax=KMAX):
    T = R.shape[0]
    U = R.sum(1); n = M.sum(1).astype(float)
    norm = (R ** 2).sum() / M.sum()
    out = np.full(kmax + 1, np.nan)
    for k in range(kmax + 1):
        if k >= T:
            break
        cross = (U[: T - k] * U[k:]).sum() - (R[: T - k] * R[k:]).sum()
        cnt = (n[: T - k] * n[k:]).sum() - (M[: T - k] & M[k:]).sum()
        out[k] = cross / cnt / norm if cnt > 0 else np.nan
    return out


def g51(model, rng, drop=frozenset(), n_null=1000):
    R, M, ud = g51_arrays(model, drop)
    T = R.shape[0]
    Lk = lag_profile(R, M)
    real = float(np.nanmean(Lk[list(SLOW)]))
    nulls = []
    for _ in range(n_null):
        Rs = np.empty_like(R); Ms = np.empty_like(M)
        for j in range(R.shape[1]):
            s = rng.integers(5, T - 5)
            Rs[:, j] = np.roll(R[:, j], s, axis=0); Ms[:, j] = np.roll(M[:, j], s)
        nulls.append(np.nanmean(lag_profile(Rs, Ms)[list(SLOW)]))
    nulls = np.array(nulls)
    return {"T_days": int(T), "n_agents": int(M.any(0).sum()), "L0": float(Lk[0]), "L1": float(Lk[1]),
            "L_slow": real, "null_mean": float(nulls.mean()), "null_q95": float(np.quantile(nulls, 0.95)),
            "null_q05": float(np.quantile(nulls, 0.05)), "p_upper": float((np.sum(nulls >= real) + 1) / (len(nulls) + 1)),
            "Lk": Lk.tolist()}


def ne33(model):
    ad, X, blocks = L.load(model, "style_resid", "III")
    P = L.projectors(model, "III", ad)
    pan = L.Panel(ad, blocks, P)
    Rd = L.day_residuals(pan, X)
    # within-#51 stayers' coherent jump uses projected vectors directly (personal vectors cancel for stayers);
    # agents without a leave-goal-out personal vector (newcomers) are kept by using the projected vector itself
    Xp = L.project(pan, X)
    Rfull = np.where(np.isnan(Rd), Xp, Rd)
    rows = [r for r in L.day_jumps(pan, Rfull, L.roster_event_days()) if r[2] == 51]
    days = {L.day_num([x])[0]: x for x in ["2026-07-09", "2026-07-10", "2026-09-03", "2026-09-04"]}
    out = {}
    plc = np.array([r[5] for r in rows if not r[3] and np.isfinite(r[5])])
    for r in rows:
        if r[1] in days:
            out[days[r[1]]] = {"J_stayers": float(r[5]), "percentile": float((plc < r[5]).mean()), "roster": bool(r[3]),
                               "n": int(r[6])}
    out["n_placebo"] = int(len(plc)); out["placebo_median"] = float(np.median(plc))
    return out


def main():
    out = L.OUT / "natives"; out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(8151)
    res = {"G51": {}, "NE33": {}}
    for model in MODELS:
        res["G51"][model] = g51(model, rng)
        res["G51"][f"{model}/no_gemini25"] = g51(model, rng, drop=frozenset({L.GEMINI_25}), n_null=500)
        res["NE33"][model] = ne33(model)
        print(model, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in res["G51"][model].items() if k != "Lk"},
              flush=True)
        print(model, res["NE33"][model], flush=True)
    (out / "natives.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
