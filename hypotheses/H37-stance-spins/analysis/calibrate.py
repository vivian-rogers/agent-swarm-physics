"""H37 Amendment 2 (post hoc, 2026-10-04, after synthetic S6 showed the sign-shuffle faction null and the per-pair
FDR are anti-conservative on residual stance graphs): a calibrated null for the operator detector.

Null model ("agent fields only"): ordered logit on the hard sign labels, P(class <= k) = sigmoid(c_k - a_speaker -
b_target), fitted by maximum likelihood (L2 penalty 0.1 on fields). It reproduces each agent's agreeableness and
likability, including the non-additivity that ordinal labels create, but has no pair structure. For each period:
simulate R replicate label sets on the real reply structure, recompute the detector's faction score (1 - 2f of the
residual stance graph's ground state) and the count of significantly negative pairs (FDR 0.1), and compare with the
observed values. Hard labels are used on both sides (the soft-label score is reported in explore.py).

Writes data/processed/H37-stance-spins/calibration.json.
Usage: uv run python hypotheses/H37-stance-spins/analysis/calibrate.py [--reps 200]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("POLARS_MAX_THREADS", "2")
import numpy as np
import polars as pl
from scipy.optimize import minimize

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h37lib as L  # noqa: E402
import h37data as D  # noqa: E402


def fit_ordinal(spk, tgt, y, N, lam=0.1):
    """y in {0,1,2} (-, 0, +). Params: c1, log(c2-c1), a[1:], b[1:]. Returns c, a, b."""
    def unpack(th):
        c1 = th[0]; c2 = c1 + np.exp(th[1])
        a = np.r_[0, th[2:N + 1]]; b = np.r_[0, th[N + 1:]]
        return c1, c2, a, b

    def nll(th):
        c1, c2, a, b = unpack(th)
        eta = a[spk] + b[tgt]
        F1 = 1 / (1 + np.exp(-(c1 - eta))); F2 = 1 / (1 + np.exp(-(c2 - eta)))
        p = np.where(y == 0, F1, np.where(y == 1, F2 - F1, 1 - F2))
        p = np.clip(p, 1e-12, 1)
        f1 = F1 * (1 - F1); f2 = F2 * (1 - F2)
        # gradient
        d_eta = np.where(y == 0, -f1 / p, np.where(y == 1, (-f2 + f1) / p, f2 / p))  # d log p / d eta
        d_c1 = np.where(y == 0, f1 / p, np.where(y == 1, -f1 / p, 0))
        d_c2 = np.where(y == 1, f2 / p, np.where(y == 2, -f2 / p, 0))
        ga = np.bincount(spk, d_eta, N)[1:]; gb = np.bincount(tgt, d_eta, N)[1:]
        g = -np.r_[d_c1.sum() + d_c2.sum(), d_c2.sum() * (c2 - c1), ga, gb]
        th_f = th[2:]
        return -np.log(p).sum() + lam * (th_f ** 2).sum(), g + np.r_[0, 0, 2 * lam * th_f]
    th0 = np.r_[-2.5, np.log(3.0), np.zeros(2 * (N - 1))]
    r = minimize(nll, th0, jac=True, method="L-BFGS-B")
    c1, c2, a, b = unpack(r.x)
    return (c1, c2), a, b, bool(r.success)


def simulate(spk, tgt, c, a, b, rng):
    eta = a[spk] + b[tgt]
    u = rng.logistic(size=len(eta)) + eta
    return np.where(u < c[0], -1.0, np.where(u < c[1], 0.0, 1.0))


def stats(spk, tgt, s, N, rng, restarts):
    Jr, C = L.residual_matrix(spk, tgt, s, N, nmin=3)
    A = np.nan_to_num(Jr); np.fill_diagonal(A, 0)
    tot = np.abs(L.h22lib.triu_vals(A)).sum()
    x, e = L.ground_state(A, rng=rng, restarts=restarts)
    sig, _ = L.significant_negative_pairs(spk, tgt, s, N, nmin=3, q=0.1)
    return float(e / tot) if tot > 0 else np.nan, len(sig)  # e / tot = 1 - 2f


def period_frame(g):
    P = D.load_pairs(g).filter(pl.col("responds") >= 0.5)
    return P


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=200)
    ap.add_argument("--check", action="store_true", help="size/power of the calibrated test (see check())")
    a_ = ap.parse_args()
    rng = np.random.default_rng(20261006)
    out = {"note": __doc__.split("\n\n")[0], "reps": a_.reps}
    for g in (12, 26, 40, 51):
        P = period_frame(g)
        agents = sorted(set(P["agent_a"].to_list()) | set(P["agent_b"].to_list()))
        ix = {x: k for k, x in enumerate(agents)}
        N = len(agents)
        spk = np.array([ix[x] for x in P["agent_b"]]); tgt = np.array([ix[x] for x in P["agent_a"]])
        s = P["s_hard"].to_numpy().astype(float)
        c, a, b, ok = fit_ordinal(spk, tgt, (s + 1).astype(int), N)
        restarts = 60 if N > 22 else 300
        sc_obs, nsig_obs = stats(spk, tgt, s, N, rng, restarts)
        null_sc, null_n = [], []
        for _ in range(a_.reps):
            ss = simulate(spk, tgt, c, a, b, rng)
            x1, x2 = stats(spk, tgt, ss, N, rng, restarts)
            null_sc.append(x1); null_n.append(x2)
        null_sc = np.array(null_sc); null_n = np.array(null_n)
        out[f"G{g}"] = {"N": N, "n_replies": int(len(s)), "fit_ok": ok, "faction_score_obs": sc_obs,
                        "faction_score_null_mean": float(np.nanmean(null_sc)), "faction_score_null_q95": float(np.nanquantile(null_sc, 0.95)),
                        "p_faction_calibrated": float((1 + np.sum(null_sc >= sc_obs)) / (1 + len(null_sc))),
                        "n_sig_neg_obs": nsig_obs, "n_sig_neg_null_mean": float(null_n.mean()), "n_sig_neg_null_q95": float(np.quantile(null_n, 0.95)),
                        "p_sig_neg_calibrated": float((1 + np.sum(null_n >= nsig_obs)) / (1 + len(null_n))),
                        "rate_null_any_sig_neg": float(np.mean(null_n >= 1))}
        print(g, out[f"G{g}"], flush=True)
    (D.DATA / "calibration.json").write_text(json.dumps(out, indent=1))
    D.record("calibration", "hypotheses/H37-stance-spins/analysis/calibrate.py", {"reps": a_.reps, "seed": 20261006})


if __name__ == "__main__" and "--check" not in sys.argv:
    main()


def check(n_data=25, reps=40, seed=20261007):
    """Size and power of the calibrated test itself, at #40 and #51 reply structure: data from a known ordinal
    agent-field model (size), or with two balanced camps +-0.5 logit added (power). Writes calibration_check.json."""
    rng = np.random.default_rng(seed)
    res = {}
    for g in (40, 51):
        P = period_frame(g)
        agents = sorted(set(P["agent_a"].to_list()) | set(P["agent_b"].to_list()))
        ix = {x: k for k, x in enumerate(agents)}
        N = len(agents)
        spk = np.array([ix[x] for x in P["agent_b"]]); tgt = np.array([ix[x] for x in P["agent_a"]])
        restarts = 40 if N > 22 else 300
        for cell in ("fields", "mattis0.5", "pairs_extra"):
            pf, pn = [], []
            for _ in range(n_data if cell != "mattis0.5" else max(10, n_data // 2)):
                a = rng.normal(0, 0.5, N); b = rng.normal(0, 0.5, N)
                eta = a[spk] + b[tgt]
                if cell == "mattis0.5":
                    xi = rng.permutation(np.r_[np.ones(N // 2), -np.ones(N - N // 2)]); eta = eta + 0.5 * xi[spk] * xi[tgt]
                if cell == "pairs_extra":  # three random antagonistic pairs at -1 logit (no camps)
                    M = np.zeros((N, N))
                    for _k in range(3):
                        i, j = rng.choice(N, 2, replace=False); M[i, j] = M[j, i] = -1.0
                    eta = eta + M[spk, tgt]
                u = rng.logistic(size=len(eta)) + eta
                s = np.where(u < -2.5, -1.0, np.where(u < 1.2, 0.0, 1.0))
                c, ah, bh, ok = fit_ordinal(spk, tgt, (s + 1).astype(int), N)
                so, no = stats(spk, tgt, s, N, rng, restarts)
                ns, nn = [], []
                for _r in range(reps):
                    x1, x2 = stats(spk, tgt, simulate(spk, tgt, c, ah, bh, rng), N, rng, restarts)
                    ns.append(x1); nn.append(x2)
                pf.append((1 + np.sum(np.array(ns) >= so)) / (1 + reps)); pn.append((1 + np.sum(np.array(nn) >= no)) / (1 + reps))
            pf, pn = np.array(pf), np.array(pn)
            res[f"G{g}|{cell}"] = {"n_datasets": len(pf), "rate_p_faction_lt05": float(np.mean(pf < 0.05)),
                                   "rate_p_signeg_lt05": float(np.mean(pn < 0.05))}
            print(g, cell, res[f"G{g}|{cell}"], flush=True)
    (D.DATA / "calibration_check.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__" and "--check" in sys.argv:
    check()
