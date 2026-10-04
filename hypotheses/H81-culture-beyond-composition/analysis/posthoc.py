"""H81 post hoc checks (labelled post hoc in the card; written after the replication result was seen).

PH1 R4 (slow scaffold change) in regime I: the slow-mode contrast on pairs whose two blocks lie in the same scaffold
    segment (split at NE04 2025-09-05 and NE08 2025-12-10), with its own S0 calibration; and the similarity of pairs
    that straddle a step vs pairs that do not, at matched lag (14-56 d).
PH2 R1 (exogenous slow drift): D_adjg with three exogenous similarity covariates (kickoff, goal text, human-message
    centroid) instead of one.
PH3 G51 native power: L_slow and L(1..4) under a planted common OU mode (tau = 3 and 20 active days) on the real #51
    panel (agents' own residual series permuted in time), to read the N1 failure.

Output: data/processed/H81-culture-beyond-composition/posthoc/posthoc.json
Usage: uv run python hypotheses/H81-culture-beyond-composition/analysis/posthoc.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h81lib as L  # noqa: E402
import natives as N  # noqa: E402

STEPS = L.day_num(["2025-09-05", "2025-12-10"])


def seg_of(mid):
    return int(np.searchsorted(STEPS, mid, side="right"))


def dirs_sim(model, regime, goals):
    V = np.load(L.OUT / f"dirs_{model}.npz")["V"].astype(np.float64)
    idx = json.loads((L.OUT / f"dirs_index_{model}.json").read_text())
    out = {}
    for kind in ("kickoff", "goal", "human"):
        d = {}
        for g in goals:
            k = [e["i"] for e in idx if e["level"] == "goal" and e["goal_no"] == g and e["regime"] == regime and e["kind"] == kind]
            d[g] = V[k[0]] if k else np.zeros(32)
        out[kind] = d
    return out


def restricted_stats(pan, T):
    seg = np.array([seg_of(m) for m in pan.block_mid])
    same = np.array([seg[int(b)] == seg[int(c)] for b, c in T[:, :2]])
    st_same = L.slow_stats(T[same])
    mid = (T[:, 2] >= 14) & (T[:, 2] <= 56) & ~np.isnan(T[:, 5])
    w = T[:, 7]
    straddle = ~same
    s_in = L._wmean(T[mid & same, 5], w[mid & same]); s_x = L._wmean(T[mid & straddle, 5], w[mid & straddle])
    return st_same, s_in, s_x, int(same.sum())


def multi_cov(pan, T, sims):
    s = T[:, 5]; ok = ~np.isnan(s); dt_ = T[:, 2]; w = T[:, 7]
    cols = [np.ones(len(T)), (dt_ <= L.NEAR).astype(float), ((dt_ > L.NEAR) & (dt_ < L.FAR)).astype(float)]
    for kind in ("kickoff", "goal", "human"):
        d = sims[kind]
        cols.append(np.array([L._cos(d[pan.block_goal[int(b)]], d[pan.block_goal[int(c)]]) for b, c in T[:, :2]]))
    X = np.column_stack(cols)[ok]; X = np.nan_to_num(X)
    sw = np.sqrt(w[ok])
    beta, *_ = np.linalg.lstsq(X * sw[:, None], s[ok] * sw, rcond=None)
    return float(beta[1])


def main():
    out = L.OUT / "posthoc"; out.mkdir(parents=True, exist_ok=True)
    res = {"PH1": {}, "PH2": {}, "PH3": {}}
    for model in ("bge_small", "gte_modernbert"):
        ad, X, blocks = L.load(model, "style_resid", "I")
        P = L.projectors(model, "I", ad)
        pan = L.Panel(ad, blocks, P)
        kick = L.goal_kickoff(model, "I", np.unique(pan.goal))
        A, B, R = L.agent_block_residuals(pan, X)
        T = L.pair_table(pan, A, B, R, kick)
        st, s_in, s_x, n_same = restricted_stats(pan, T)
        sims = dirs_sim(model, "I", np.unique(pan.goal))
        mc = multi_cov(pan, T, sims)
        sc = L.variance_scales(pan, X); rng = np.random.default_rng(81081)
        s0 = []
        for _ in range(100):
            Xs = L.simulate(pan, sc, rng)
            A2, B2, R2 = L.agent_block_residuals(pan, Xs)
            T2 = L.pair_table(pan, A2, B2, R2, kick)
            a, si, sx, _ = restricted_stats(pan, T2)
            s0.append((a["D_adjg"], a["D_adj"], si - sx, multi_cov(pan, T2, sims)))
        s0 = np.array(s0)
        res["PH1"][model] = {"n_pairs_same_segment": n_same, "D_adjg_same": st["D_adjg"], "D_adj_same": st["D_adj"],
                             "S0_q95_D_adjg_same": float(np.nanquantile(s0[:, 0], 0.95)),
                             "S0_q95_D_adj_same": float(np.nanquantile(s0[:, 1], 0.95)),
                             "s_within_14_56": s_in, "s_straddle_14_56": s_x, "diff": s_in - s_x,
                             "S0_q95_diff": float(np.nanquantile(s0[:, 2], 0.95)),
                             "S0_q05_diff": float(np.nanquantile(s0[:, 2], 0.05))}
        res["PH2"][model] = {"D_adjg_3cov": mc, "S0_q95": float(np.nanquantile(s0[:, 3], 0.95)),
                             "S0_mean": float(np.nanmean(s0[:, 3]))}
        # PH3: G51 native power
        Rr, M, ud = N.g51_arrays(model)
        rng = np.random.default_rng(5151)
        norm = (Rr ** 2).sum() / M.sum()
        ph3 = {}
        for tau in (3.0, 20.0):
            for share in (0.05, 0.1):
                vals, short = [], []
                for _ in range(100):
                    Rs = Rr.copy()
                    for j in range(Rs.shape[1]):  # destroy real cross-agent timing: permute each agent's days
                        idx = np.flatnonzero(M[:, j]); perm = rng.permutation(idx)
                        Rs[idx, j] = Rr[perm, j]
                    z = rng.standard_normal((len(ud), 32)) * np.sqrt(share * norm / 32)
                    c = np.zeros_like(z); c[0] = z[0]
                    rho = np.exp(-1 / tau)
                    for t in range(1, len(ud)):
                        c[t] = rho * c[t - 1] + np.sqrt(1 - rho ** 2) * z[t]
                    Rs = Rs + c[:, None, :] * M[:, :, None]
                    for j in range(Rs.shape[1]):
                        mj = M[:, j]
                        if mj.sum() >= 3:
                            Rs[mj, j] -= Rs[mj, j].mean(0)
                    Lk = N.lag_profile(Rs, M)
                    vals.append(np.nanmean(Lk[list(N.SLOW)])); short.append(np.nanmean(Lk[1:5]))
                ph3[f"tau{tau:g}_share{share}"] = {"L_slow_mean": float(np.mean(vals)), "L_slow_q05": float(np.quantile(vals, 0.05)),
                                                   "L_slow_q95": float(np.quantile(vals, 0.95)), "L1_4_mean": float(np.mean(short))}
        res["PH3"][model] = ph3
        print(model, json.dumps({k: res[k][model] for k in res}, indent=1, default=float), flush=True)
    (out / "posthoc.json").write_text(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
