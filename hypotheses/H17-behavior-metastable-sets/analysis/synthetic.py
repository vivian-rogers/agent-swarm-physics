"""H17 synthetic validation (axis F, card P1): Markov chains with planted metastable sets at village sampling.

Experiments
  A  t2 recovery and small-sample bias vs. t2_true and sampling (N agents x days x steps/day); bootstrap coverage;
     PCCA+ partition recovery and the eigen-gap choice of m; CK pass rate on true Markov chains.
  B  CK power: a lumped hidden-state (non-Markov) chain (idle split into a short and a long hidden idle).
  C  N2 sojourn null: false positives on sticky-only (R1) chains; power on planted sets.
  D  agent heterogeneity: per-agent t2 spread 4x; I^2; pooled vs per-agent CK error.
  E  soft states (Jev-like q = 10, argmax accuracy ~0.6): argmax / soft-count / shifted estimators.

Usage: uv run python hypotheses/H17-behavior-metastable-sets/analysis/synthetic.py [--reps 30] [--workers 2]
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h17lib as L  # noqa: E402

ROOT = HERE.parents[2]
OUT = ROOT / "data/processed/H17-behavior-metastable-sets/synthetic"
TAU = 5
Q = 6
SAMPLING = {  # (agents, days, steps/day): village period sizes (present agent-days ~ agents x days)
    "small_3d": (12, 3, 240), "typical_5d": (15, 5, 240), "long_17d": (14, 17, 240), "g51_45d": (27, 45, 480)}


# ----------------------------------------------------------------------------- chains
def planted(m, t2_target, rng, stick=0.5):
    """q = 6 chain with m planted sets; leak eps tuned so the exact t2 (tau = 1) equals t2_target."""
    sets = {2: [(0, 1, 2), (3, 4, 5)], 3: [(0, 1), (2, 3), (4, 5)]}[m]
    lab = np.zeros(Q, int)
    for k, s in enumerate(sets):
        lab[list(s)] = k
    W = np.zeros((Q, Q))
    for i in range(Q):
        mem = [j for j in range(Q) if lab[j] == lab[i]]
        w = rng.dirichlet(np.ones(len(mem)) * 2)
        W[i, mem] = (1 - stick) * w
        W[i, i] += stick
    Out = np.zeros((Q, Q))
    for i in range(Q):
        oth = [j for j in range(Q) if lab[j] != lab[i]]
        Out[i, oth] = rng.dirichlet(np.ones(len(oth)) * 2)

    def make(eps):
        return (1 - eps) * W + eps * Out

    lo, hi = 1e-6, 0.5
    for _ in range(80):
        mid = np.sqrt(lo * hi)
        t2 = L.its_from_T(make(mid), 1)[0]
        lo, hi = (mid, hi) if t2 > t2_target else (lo, mid)
    return make(np.sqrt(lo * hi)), lab


def sticky_chain(t2_target, pi_sticky=0.35, sticky_state=4, s_other=0.5):
    """R1 chain: one very sticky state (occupancy ~pi_sticky), the rest moderately sticky; jumps go to a fixed
    destination distribution nu (no set structure). The sticky state's escape is tuned for the exact t2."""
    r_in = pi_sticky / t2_target
    nu = np.full(Q, 0.0)
    nu[sticky_state] = min(0.9, r_in / (1 - s_other))
    others = [j for j in range(Q) if j != sticky_state]
    nu[others] = (1 - nu[sticky_state]) / len(others)

    def make(s4):
        s = np.full(Q, s_other)
        s[sticky_state] = s4
        T = np.zeros((Q, Q))
        for i in range(Q):
            T[i] = (1 - s[i]) * nu / (1 - nu[i])
            T[i, i] = s[i]
        return T

    lo, hi = 0.0, 0.99999
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        t2 = L.its_from_T(make(mid), 1)[0]
        lo, hi = (lo, mid) if t2 > t2_target else (mid, hi)
    return make(0.5 * (lo + hi))


def hidden_lumped(t2_target, rng):
    """Non-Markov: a planted 2-set chain on 7 hidden states; sets A = {0,1,2,6}, B = {3,4,5}. Hidden 6 belongs to
    set A but is observed as 4 (idle, in set B): a state definition that lumps across the barrier (the classic
    MSM failure)."""
    T6, lab = planted(2, t2_target, rng)
    T = np.zeros((7, 7))
    T[:6, :6] = T6
    A = [0, 1, 2]
    # set-A states send a third of their within-set mass to hidden 6; hidden 6 behaves like an A state
    for i in A:
        move = T[i, A].sum() / 3
        T[i, A] *= 2 / 3
        T[i, 6] = move
    T[6, :6] = T6[0, :6]
    T[6, 6] = T6[0, 0]
    T[6, 0] = 0.0
    T[6] /= T[6].sum()
    emit = np.array([0, 1, 2, 3, 4, 5, 4])
    return T, emit


def simulate(T, nseg, Ld, rng, start_state=5, emit=None):
    q = len(T)
    cdf = np.cumsum(T, 1)
    cdf[:, -1] = 1.0
    X = np.empty((nseg, Ld), np.int64)
    X[:, 0] = start_state if start_state < q else rng.integers(q, size=nseg)
    for t in range(1, Ld):
        u = rng.random(nseg)
        X[:, t] = (u[:, None] > cdf[X[:, t - 1]]).sum(1)
    if emit is not None:
        X = emit[X]
    return X.ravel(), np.repeat(np.arange(nseg), Ld)


def exact_crossings(T, lab, n_steps):
    pi = L.stationary(T)
    flux = sum(pi[i] * T[i, j] for i in range(len(T)) for j in range(len(T)) if lab[i] != lab[j])
    return flux * n_steps


def t2_R1_exact(T, tau=TAU):
    pi = L.stationary(T)
    C = pi[:, None] * np.linalg.matrix_power(T, tau)
    return L.its_from_T(L.sticky_fit(C * 1e6), tau)[0]


def estimate(x, seg, q=Q, tau=TAU, R=100, rng=None, nulls=0, kmax=5):
    nseg = int(seg.max()) + 1
    Csk = {k: L.seg_counts(x, seg, q, tau * k, nseg) for k in range(1, kmax + 1)}
    C = Csk[1].sum(0)
    its = L.its_from_C(C, tau)
    out = {"t2": its[0], "t3": its[1]}
    M = L.msm_sets(C)
    out["m_auto"] = M.get("m_auto")
    Cs = {k: Csk[k].sum(0) for k in Csk}
    if M.get("m"):
        est, pred = L.ck_sets(Cs, M["T"], M["active"], M["labels"], M["m"], kmax)
        d0 = (est - pred)[:4]
        out["ck_max"] = float(np.nanmax(np.abs(d0)))
    T0, a0 = L.T_mle(C)
    out["ck_full"] = L.ck_full_error(Cs, T0, a0, L.stationary(T0), kmax)
    out["M"] = M
    if R:
        Wb = L.boot_weights(nseg, R, rng)
        bs, dd = [], []
        for w in Wb:
            Cb = {k: np.tensordot(w, Csk[k], 1) for k in Csk}
            bs.append(L.its_from_C(Cb[1], tau)[0])
            if M.get("m"):
                Tb, ab = L.T_mle(Cb[1])
                if len(ab) == len(M["active"]):
                    e, p_ = L.ck_sets(Cb, Tb, ab, M["labels"], M["m"], kmax)
                    dd.append((e - p_)[:4])
        bs = np.array(bs)
        out["ci"] = np.nanpercentile(bs, [2.5, 97.5])
        if dd:
            se = np.nanstd(np.array(dd), axis=0)
            out["ck_sig_fail"] = bool(np.any(np.abs(d0) > 2 * np.maximum(se, 1e-9)))
    if nulls:
        nt2 = []
        for _ in range(nulls):
            xn, _m = L.null_sojourn(x, seg, rng)
            nt2.append(L.its_from_C(L.counts(xn, seg, q, tau), tau)[0])
        nt2 = np.array(nt2)
        out["n2_p95"] = float(np.nanpercentile(nt2, 95))
        out["n2_med"] = float(np.nanmedian(nt2))
        out["n2_exceed"] = bool(t2 > out["n2_p95"] and t2 / out["n2_med"] >= 1.25) if (t2 := its[0]) == its[0] else False
    return out


# ----------------------------------------------------------------------------- experiments
def exp_A(args):
    samp, m, t2_true, reps, seed = args
    rng = np.random.default_rng(seed)
    N, D, Ld = SAMPLING[samp]
    rows = []
    for r in range(reps):
        T, lab = planted(m, t2_true, rng)
        t2_exact = L.its_from_T(np.linalg.matrix_power(T, TAU), TAU)[0]
        x, seg = simulate(T, N * D, Ld, rng)
        e = estimate(x, seg, R=60, rng=rng)
        M = e["M"]
        exact_part = None
        Mm = L.msm_sets(L.counts(x, seg, Q, TAU), m=m)
        if Mm.get("labels") is not None and len(Mm["active"]) == Q:
            a = Mm["labels"]  # partition equality up to relabeling
            exact_part = all(len(set(a[lab == k])) == 1 for k in range(m)) and len(set(a)) == m
        t3_exact = L.its_from_T(np.linalg.matrix_power(T, TAU), TAU)[1]
        rows.append({"samp": samp, "m": m, "t2_true": t2_exact, "t3_true": t3_exact, "t2": e["t2"],
                     "ratio": e["t2"] / t2_exact, "cover": bool(e["ci"][0] <= t2_exact <= e["ci"][1]),
                     "m_auto_ok": e["m_auto"] == m, "partition_ok": exact_part, "ck_max": e.get("ck_max"),
                     "ck_pass": (e.get("ck_max") is not None and e["ck_max"] < 0.05), "ck_sig_fail": e.get("ck_sig_fail"),
                     "crossings": exact_crossings(T, lab, N * D * Ld), "sep_true": t2_exact / t3_exact})
    return rows


def exp_B(args):
    samp, t2_true, reps, seed = args
    rng = np.random.default_rng(seed)
    N, D, Ld = SAMPLING[samp]
    rows = []
    for r in range(reps):
        T, emit = hidden_lumped(t2_true, rng)
        x, seg = simulate(T, N * D, Ld, rng, emit=emit)
        e = estimate(x, seg, R=60, rng=rng)
        its1 = L.its_from_C(L.counts(x, seg, Q, 1), 1)[0]
        its15 = L.its_from_C(L.counts(x, seg, Q, 15), 15)[0]
        rows.append({"samp": samp, "t2_target": t2_true, "ck_max": e.get("ck_max"),
                     "ck_fail": (e.get("ck_max") is None or e["ck_max"] >= 0.05), "ck_sig_fail": e.get("ck_sig_fail"),
                     "its1": its1, "its5": e["t2"], "its15": its15, "its_rise_15_over_1": its15 / its1})
    return rows


def exp_C(args):
    samp, kind, t2_true, reps, seed, nnull = args
    rng = np.random.default_rng(seed)
    N, D, Ld = SAMPLING[samp]
    rows = []
    for r in range(reps):
        if kind == "R1":
            T = sticky_chain(t2_true)
        else:
            T, _ = planted(2, t2_true, rng)
        ratio_R1 = L.its_from_T(np.linalg.matrix_power(T, TAU), TAU)[0] / t2_R1_exact(T)
        x, seg = simulate(T, N * D, Ld, rng, start_state=4)
        e = estimate(x, seg, R=0, rng=rng, nulls=nnull)
        rows.append({"samp": samp, "kind": kind, "t2_target": t2_true, "t2": e["t2"], "n2_med": e["n2_med"],
                     "n2_p95": e["n2_p95"], "exceed": e["n2_exceed"], "ratio_true_over_R1": ratio_R1})
    return rows


def exp_D(args):
    samp, t2_mid, spread, reps, seed = args
    rng = np.random.default_rng(seed)
    N, D, Ld = SAMPLING[samp]
    rows = []
    for r in range(reps):
        base_rng = np.random.default_rng(seed * 1000 + r)
        xs, segs, t2s = [], [], []
        T0, lab = planted(2, t2_mid, base_rng)
        for a in range(N):
            t2a = t2_mid * spread ** rng.uniform(-0.5, 0.5)
            Ta, _ = planted(2, t2a, np.random.default_rng(seed * 1000 + r))  # same within-set structure, different leak
            x, seg = simulate(Ta, D, Ld, rng)
            xs.append(x)
            segs.append(seg + a * D)
            t2s.append(L.its_from_T(np.linalg.matrix_power(Ta, TAU), TAU)[0])
        x, seg = np.concatenate(xs), np.concatenate(segs)
        nseg = N * D
        Cseg = L.seg_counts(x, seg, Q, TAU, nseg)
        y, se, ckA, se_blk = [], [], [], []
        for a in range(N):
            Ca = Cseg[a * D:(a + 1) * D]
            t2a = L.its_from_C(Ca.sum(0), TAU)[0]
            Wb = L.boot_weights(D, 60, rng)
            bs = np.array([L.its_from_C(np.tensordot(w, Ca, 1), TAU)[0] for w in Wb])
            y.append(np.log(t2a))
            se.append(np.nanstd(np.log(bs[bs > 0])))
            xa = x[a * D * Ld:(a + 1) * D * Ld]
            sa = seg[a * D * Ld:(a + 1) * D * Ld] - a * D
            Cb, _bs = L.block_counts(xa, sa, Q, TAU, 60)
            Wbb = L.boot_weights(len(Cb), 60, rng)
            bsb = np.array([L.its_from_C(np.tensordot(w, Cb, 1), TAU)[0] for w in Wbb])
            se_blk.append(np.nanstd(np.log(bsb[bsb > 0])))
            msk = np.zeros(nseg, bool)
            msk[a * D:(a + 1) * D] = True
            Sa = L.subset({"x": x, "seg": seg, "seg_agent": np.repeat(np.arange(N), D), "seg_day": np.tile(np.arange(D), N), "q": Q}, msk)
            Csa = {k: L.counts(Sa["x"], Sa["seg"], Q, TAU * k) for k in range(1, 6)}
            Ta_hat, act = L.T_mle(Csa[1])
            ckA.append(L.ck_full_error(Csa, Ta_hat, act, L.stationary(Ta_hat))[1:4].mean())
        I2, Q_ = L.i_squared(y, se)
        I2b, _ = L.i_squared(y, se_blk)
        segfold = np.tile(np.arange(D), N) % min(5, D)
        ho = L.agent_heldout(Cseg, np.repeat(np.arange(N), D), segfold, min(5, D))
        Cp = {k: L.counts(x, seg, Q, TAU * k) for k in range(1, 6)}
        Tp, actp = L.T_mle(Cp[1])
        ckP = L.ck_full_error(Cp, Tp, actp, L.stationary(Tp))[1:4].mean()
        rows.append({"samp": samp, "spread": spread, "I2": I2, "I2_gt_05": bool(I2 > 0.5), "I2_block": I2b,
                     "I2_block_gt_05": bool(I2b > 0.5), "ck_pooled": ckP,
                     "ck_agent_median": float(np.median(ckA)), "pooled_worse": bool(ckP > np.median(ckA)),
                     "t2_pooled": float(L.its_from_C(Cp[1], TAU)[0]), "t2_agents_median": float(np.median(t2s)),
                     "frac_own_or_shrink_beats_pooled": ho["frac_beats"], "frac_shrink_beats_pooled": ho["frac_shrink"]})
    return rows


def jev_like(t2_true_win, rng, q=10, m=3):
    sets = [list(range(0, 4)), list(range(4, 7)), list(range(7, 10))]
    lab = np.zeros(q, int)
    for k, s in enumerate(sets):
        lab[s] = k
    W = np.zeros((q, q))
    Out = np.zeros((q, q))
    for i in range(q):
        mem = [j for j in range(q) if lab[j] == lab[i]]
        W[i, mem] = 0.5 * rng.dirichlet(np.ones(len(mem)) * 2)
        W[i, i] += 0.5
        oth = [j for j in range(q) if lab[j] != lab[i]]
        Out[i, oth] = rng.dirichlet(np.ones(len(oth)) * 2)
    lo, hi = 1e-6, 0.6
    for _ in range(80):
        mid = np.sqrt(lo * hi)
        t2 = L.its_from_T((1 - mid) * W + mid * Out, 1)[0]
        lo, hi = (mid, hi) if t2 > t2_true_win else (lo, mid)
    return (1 - np.sqrt(lo * hi)) * W + np.sqrt(lo * hi) * Out


def noisy_posteriors(xh, q, rng, a=0.3, beta=0.6):
    """Posterior-like vectors: Dirichlet(beta * q * (a e_s + (1-a)/q)); independent across windows."""
    base = np.full((len(xh), q), (1 - a) / q)
    base[np.arange(len(xh)), xh] += a
    G = rng.gamma(beta * q * base)
    return G / G.sum(1, keepdims=True)


def exp_E(args):
    samp, t2_win, reps, seed = args
    rng = np.random.default_rng(seed)
    N, D, Lmin = SAMPLING[samp]
    Ld = Lmin // 5
    q = 10
    rows = []
    for r in range(reps):
        T = jev_like(t2_win, rng)
        xh, seg = simulate(T, N * D, Ld, rng, start_state=0)
        P = noisy_posteriors(xh, q, rng)
        hard = P.argmax(1)
        acc = float(np.mean(hard == xh))
        row = {"samp": samp, "t2_true_win": t2_win, "acc": acc}
        for tau in (1, 2, 4):
            t2_true = L.its_from_T(np.linalg.matrix_power(T, tau), tau)[0]
            row[f"true_{tau}"] = t2_true
            row[f"hidden_{tau}"] = L.its_from_C(L.counts(xh, seg, q, tau), tau)[0] / t2_true
            row[f"argmax_{tau}"] = L.its_from_C(L.counts(hard, seg, q, tau), tau)[0] / t2_true
            row[f"softcount_{tau}"] = L.soft_its(P, seg, tau)[0] / t2_true
            row[f"shifted_{tau}"] = L.shifted_its(P, seg, tau, tau0=1)[0] / t2_true
        rows.append(row)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=30)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--nnull", type=int, default=40)
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    R = args.reps
    jobs = []
    seed = 20261003
    for samp in SAMPLING:
        for m in (2, 3):
            for t2 in (3, 10, 30, 60, 120):
                if samp == "g51_45d" and m == 3:
                    continue
                seed += 1
                jobs.append(("A", (samp, m, t2, R if samp != "g51_45d" else max(10, R // 3), seed)))
    for samp in ("typical_5d", "long_17d"):
        for t2 in (10, 30):
            seed += 1
            jobs.append(("B", (samp, t2, R, seed)))
    for samp in ("small_3d", "typical_5d", "long_17d"):
        for kind in ("R1", "sets"):
            for t2 in (10, 30):
                seed += 1
                jobs.append(("C", (samp, kind, t2, R, seed, args.nnull)))
    for samp in ("typical_5d", "long_17d"):
        for spread in (1.0, 4.0):
            seed += 1
            jobs.append(("D", (samp, 15, spread, max(10, R // 2), seed)))
    for samp in ("typical_5d", "g51_45d"):
        for t2w in (3, 6, 12):
            seed += 1
            jobs.append(("E", (samp, t2w, max(10, R // 2) if samp != "g51_45d" else 6, seed)))
    fn = {"A": exp_A, "B": exp_B, "C": exp_C, "D": exp_D, "E": exp_E}
    res = {k: [] for k in fn}
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = [(k, ex.submit(fn[k], a)) for k, a in jobs]
        for k, f in futs:
            res[k].extend(f.result())
            print(k, len(res[k]), f"{time.time() - t0:.0f}s", flush=True)
    (OUT / "synthetic_rows.json").write_text(json.dumps(L.jsonable(res)))
    print(f"done {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
