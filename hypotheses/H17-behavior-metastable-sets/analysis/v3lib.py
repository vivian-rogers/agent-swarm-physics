"""H17 round 1b: soft-state MSM tools for the Jev v3.1 behavior states (DQ3).

States: the 11 Jev v3.1 states (probability vectors p_*) plus `absent` for in-span windows with no record
(active = false, in_span = true; "idle by absence", one-hot). Windows outside the agent's daily span are dropped.
Rare states (< 1% of a period's mass) are merged into `rare`; if `rare` itself has < 1% it is dropped and the
vectors renormalized. Holdout windows are never read (filtered on the table's `holdout` flag and holdout.json).

Estimators (validated in synthetic_v3.py before any real-data run):
  shifted ITS     eigenvalues of K(tau) = C(1)^-1 C(1 + tau), C(tau) = sum_t p_t p_{t+tau}^T within segments:
                  cancels window-independent classifier noise (lambda^tau exactly for a hidden Markov chain)
  soft CK         C(k) observed vs C_pred(k) = C(1) K(1)^(k-1); set-level P(A -> A, k) with PCCA+ memberships
  soft N2         argmax runs (with their vectors) permuted inside each agent-day; first/last run in place
  PCCA+           on T_soft = rownorm(C(1)) (reversibilized), for set composition only
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ.setdefault(_v, "2")

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "infra/shared"))
import h17lib as L  # noqa: E402

SH = ROOT / "data/processed/shared"
V3 = SH / "behavior_states_v3.parquet"
JEV = ["plan_coordinate", "execute_task", "research_browse", "communicate_external", "debug_recover", "verify_report",
       "monitor_wait", "self_maintenance", "social", "meta", "idle"]
STATES12 = JEV + ["absent"]
COV = ["p_blocked", "n_errors", "n_actions", "n_stderr", "longest_run", "repeated_error_share", "post_reset",
       "first_active_window", "session_start_in_window", "n_commit_ok", "n_push_ok", "n_file_write", "progress_score",
       "self_repeat_share", "n_seen_mentioning", "n_seen_automated", "labeled", "active", "t0"]


def load_v3_table(goals=None, days=None):
    """Non-holdout, in-span v3 windows (optionally restricted to goals / PT days), sorted by agent, day, window."""
    import polars as pl
    from common import holdout_mask
    v = pl.read_parquet(V3).filter(~pl.col("holdout") & pl.col("in_span"))
    if goals is not None:
        v = v.filter(pl.col("goal_no").is_in(list(goals)))
    if days is not None:
        v = v.filter(pl.col("pt_date").is_in(list(days)))
    hm = holdout_mask(v["pt_date"].to_list(), v["goal_no"].to_list())
    assert not any(hm), "holdout window reached the v3 loader"
    return v.sort("agent", "pt_date", "w")


def soft_matrix(v, rare=0.01, names=None):
    """(P, names): 12-column probability matrix (11 Jev + absent) with the rare-state merge, or the given names."""
    P = np.zeros((v.height, len(STATES12)))
    lab = v["labeled"].to_numpy()
    for j, s in enumerate(JEV):
        P[:, j] = np.nan_to_num(v[f"p_{s}"].to_numpy().astype(np.float64)) * lab
    P[~lab, -1] = 1.0
    rs = P.sum(1, keepdims=True)
    P = P / np.where(rs > 0, rs, 1.0)
    if names is not None:                      # reuse a fixed state list (e.g. across a split)
        idx = [STATES12.index(n) for n in names if n != "rare"]
        out = P[:, idx]
        if "rare" in names:
            rest = [i for i in range(len(STATES12)) if STATES12[i] not in names]
            out = np.column_stack([out, P[:, rest].sum(1)])
        rs = out.sum(1, keepdims=True)
        return out / np.where(rs > 0, rs, 1.0), list(names)
    mass = P.mean(0)
    keep = [j for j in range(len(STATES12)) if mass[j] >= rare]
    rest = [j for j in range(len(STATES12)) if mass[j] < rare]
    out = P[:, keep]
    nm = [STATES12[j] for j in keep]
    if rest and P[:, rest].sum(1).mean() >= rare:
        out = np.column_stack([out, P[:, rest].sum(1)])
        nm.append("rare")
    rs = out.sum(1, keepdims=True)
    return out / np.where(rs > 0, rs, 1.0), nm


def sequences(v, P):
    """Sequence dict (segments = agent-days, consecutive windows) with soft P and argmax x."""
    agent = v["agent"].to_numpy().astype(np.int64)
    day = v["pt_date"].to_numpy()
    w = v["w"].to_numpy().astype(np.int64)
    n = len(w)
    newseg = np.ones(n, dtype=bool)
    if n > 1:
        newseg[1:] = ~((agent[1:] == agent[:-1]) & (day[1:] == day[:-1]) & (w[1:] - w[:-1] == 1))
    seg = np.cumsum(newseg) - 1
    st = np.flatnonzero(newseg)
    return {"x": P.argmax(1).astype(np.int64), "P": P, "seg": seg, "seg_agent": agent[st], "seg_day": day[st],
            "q": P.shape[1], "agent": agent, "day": day}


# ============================================================================ soft counts and the shifted estimator
def seg_soft_counts(P, seg, tau, nseg=None):
    """Per-segment soft count matrices (nseg, q, q) at lag tau."""
    nseg = int(seg.max()) + 1 if nseg is None else nseg
    q = P.shape[1]
    out = np.zeros((nseg, q, q))
    if len(P) <= tau:
        return out
    ok = seg[:-tau] == seg[tau:]
    A, B, s = P[:-tau][ok], P[tau:][ok], seg[:-tau][ok]
    # outer products summed per segment
    np.add.at(out, s, A[:, :, None] * B[:, None, :])
    return out


def K_shift(C0, C1, ridge=1e-6):
    q = len(C0)
    return np.linalg.solve(C0 + ridge * np.trace(C0) / q * np.eye(q), C1)


def its_shift(C0, C1, tau, k=4):
    return L.its_from_T(K_shift(C0, C1), tau, k)


def soft_T(C):
    rs = C.sum(1, keepdims=True)
    return C / np.where(rs > 0, rs, 1.0)


def soft_ck(C, chi, kmax=5):
    """Set-level soft CK. C: dict lag -> soft count matrix (lags 1..kmax+1 used as C[k]). chi: (q, m) memberships.
    Returns (est, pred) arrays (kmax, m) with rows k = 1..kmax; row 1 is identical by construction."""
    K1 = K_shift(C[1], C[2])
    m = chi.shape[1]
    est = np.full((kmax, m), np.nan)
    pred = np.full((kmax, m), np.nan)
    Kp = np.eye(len(K1))
    one = np.ones(len(K1))
    for k in range(1, kmax + 1):
        Cp = C[1] @ Kp
        Kp = Kp @ K1
        for A in range(m):
            ca = chi[:, A]
            den_e = ca @ C[k] @ one
            den_p = ca @ Cp @ one
            est[k - 1, A] = (ca @ C[k] @ ca) / den_e if den_e > 0 else np.nan
            pred[k - 1, A] = (ca @ Cp @ ca) / den_p if den_p > 0 else np.nan
    return est, pred


def soft_ck_full(C, kmax=5):
    """Full-matrix soft CK error: mean |C_pred(k) - C(k)| / mean C(k), k = 2..kmax."""
    K1 = K_shift(C[1], C[2])
    errs = []
    Kp = K1.copy()
    for k in range(2, kmax + 1):
        Cp = C[1] @ Kp
        Kp = Kp @ K1
        errs.append(float(np.abs(Cp - C[k]).sum() / max(np.abs(C[k]).sum(), 1e-12)))
    return errs


def soft_sets(C1, m=None):
    """PCCA+ on the row-normalized soft count matrix (composition of the slow sets; not used for timescales)."""
    T = soft_T(C1 + 1e-9)
    pi = L.stationary(T)
    Tr = L.reversibilize(T, pi)
    m_auto, w = L.eigengap_m(Tr)
    m = m or m_auto
    if m is None or m >= len(T):
        return {"m": None}
    chi, _ = L.pcca(Tr, pi, m)
    return {"m": m, "m_auto": m_auto, "chi": chi, "labels": chi.argmax(1), "pi": pi,
            "crispness": float(np.sum(pi * chi.max(1))), "eig_rev": w}


# ============================================================================ nulls
def sojourn_index(x, seg, rng, max_pass=10):
    """Soft N2: permutation index that reorders the interior argmax runs of each segment (first/last run in place);
    adjacent identical run states are broken up by random swaps where possible."""
    rs, rl, rg = L.runs_of(x, seg)
    starts = np.r_[0, np.cumsum(rl)][:-1]
    bounds = np.flatnonzero(np.r_[True, rg[1:] != rg[:-1], True])
    idx = np.empty(len(x), dtype=np.int64)
    pos = 0
    for b0, b1 in zip(bounds[:-1], bounds[1:]):
        order = np.arange(b0, b1)
        k = len(order)
        if k > 3:
            inner = order[1:-1].copy()
            rng.shuffle(inner)
            order[1:-1] = inner
            s = rs[order]
            for _ in range(max_pass):
                bad = np.flatnonzero(s[1:] == s[:-1]) + 1
                bad = bad[(bad >= 1) & (bad <= k - 2)]
                if len(bad) == 0:
                    break
                for i in bad:
                    j = int(rng.integers(1, k - 1))
                    if j == i:
                        continue
                    order[i], order[j] = order[j], order[i]
                    s = rs[order]
        for r in order:
            idx[pos:pos + rl[r]] = np.arange(starts[r], starts[r] + rl[r])
            pos += rl[r]
    return idx


def block_ids(seg, block_len):
    """Contiguous within-segment blocks of block_len steps (for bootstraps and flip nulls)."""
    n = len(seg)
    seg_start = np.flatnonzero(np.r_[True, seg[1:] != seg[:-1]])
    pos = np.arange(n) - np.repeat(seg_start, np.diff(np.append(seg_start, n)))
    key = seg * 100000 + pos // block_len
    _, b = np.unique(key, return_inverse=True)
    return b


# ============================================================================ synthetic generators (validation)
def hmm_soft(T, E, n_seg, L_seg, acc_conc, rng, start=None):
    """Hidden Markov chain (T over hidden states) observed through an emission map E (hidden -> observed state)
    and Jev-like soft vectors: Dirichlet around a noisy one-hot (correct state with prob acc). Returns P, seg, hidden."""
    nh = len(T)
    q = int(E.max()) + 1
    acc, conc = acc_conc
    cT = np.cumsum(T, 1)
    pi = L.stationary(T)
    Hs, Ps, Ss = [], [], []
    for s in range(n_seg):
        h = np.empty(L_seg, dtype=np.int64)
        h[0] = rng.choice(nh, p=pi) if start is None else start
        u = rng.random(L_seg)
        for t in range(1, L_seg):
            h[t] = min(int(np.searchsorted(cT[h[t - 1]], u[t])), nh - 1)
        o = E[h]
        lab = np.where(rng.random(L_seg) < acc, o, rng.integers(0, q, L_seg))
        alpha = np.full((L_seg, q), 0.3)
        alpha[np.arange(L_seg), lab] += conc
        Pm = np.array([rng.dirichlet(a) for a in alpha])
        Hs.append(h); Ps.append(Pm); Ss.append(np.full(L_seg, s))
    return np.vstack(Ps), np.concatenate(Ss), np.concatenate(Hs)
