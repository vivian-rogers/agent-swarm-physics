"""H24 statistics shared by synthetic.py, explore.py and confirm.py (observables O1-O4 of the card)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
from h24lib import alignment_stats, betaJ_snapshot, project_out, unit  # noqa: E402,F401


def rarefied_vectors(Z, groups, k, rng):
    """One rarefaction draw: for each group (array of statement row indices) the normalized mean of k rows.
    Groups with fewer than k rows give None."""
    out = []
    for g in groups:
        if len(g) < k:
            out.append(None)
        else:
            out.append(unit(Z[rng.choice(g, size=k, replace=False)].mean(0)))
    return out


def seg_alignment(Z, groups_pre, groups_post, k, B, rng):
    """Rarefied A and |m| for two segments over the agents that have >= k statements in both.
    Z: statements x n (unit rows, residualized or not). Returns dict with means over B draws."""
    keep = [i for i, (a, b) in enumerate(zip(groups_pre, groups_post)) if len(a) >= k and len(b) >= k]
    if len(keep) < 3:
        return None
    gp = [groups_pre[i] for i in keep]; gq = [groups_post[i] for i in keep]
    Ap, Aq, mp, mq = [], [], [], []
    for _ in range(B):
        vp = np.array(rarefied_vectors(Z, gp, k, rng)); vq = np.array(rarefied_vectors(Z, gq, k, rng))
        a, m = alignment_stats(vp); Ap.append(a); mp.append(m)
        a, m = alignment_stats(vq); Aq.append(a); mq.append(m)
    N = len(keep)
    A_pre, A_post = float(np.mean(Ap)), float(np.mean(Aq))
    return {"N": N, "agents_idx": keep, "A_pre": A_pre, "A_post": A_post, "dA": A_post - A_pre,
            "m_pre": float(np.mean(mp)), "m_post": float(np.mean(mq)), "dm": float(np.mean(mq) - np.mean(mp)),
            "bJ_pre": betaJ_snapshot(A_pre, N), "bJ_post": betaJ_snapshot(A_post, N),
            "A_pre_sd": float(np.std(Ap)), "A_post_sd": float(np.std(Aq))}


def segments(times, agents, agent_list, tau, post_len, lo=None, hi=None):
    """Statement row indices per agent for pre = [lo, tau_i) and post = [tau_i, tau_i + post_len) (minutes).
    tau: dict agent -> switch minute. lo/hi bound the day (minutes)."""
    pre, post = [], []
    for a in agent_list:
        ta = tau[a]
        sel = agents == a
        if lo is not None:
            sel &= times >= lo
        if hi is not None:
            sel &= times < hi
        pre.append(np.flatnonzero(sel & (times < ta)))
        post.append(np.flatnonzero(sel & (times >= ta) & (times < ta + post_len)))
    return pre, post


def random_rotations(n, size, rng):
    """Haar-random orthogonal matrices."""
    out = []
    for _ in range(size):
        Q, R = np.linalg.qr(rng.standard_normal((n, n)))
        out.append(Q * np.sign(np.diag(R)))
    return out


# ------------------------------------------------------------------ numeric herding (O4)
def degroot(first, last, qid):
    """first, last: arrays over (agent, question) units; qid: question id per unit.
    Returns kappa (= -slope of delta on deviation from the others' mean, question fixed effects) and the
    per-question dispersion change."""
    first = np.asarray(first, float); last = np.asarray(last, float); qid = np.asarray(qid)
    d, D = [], []
    dsd = {}
    for q in np.unique(qid):
        s = qid == q
        if s.sum() < 3:
            continue
        x = first[s]; y = last[s]
        others = (x.sum() - x) / (len(x) - 1)
        dev = x - others
        delta = y - x
        d.append(dev - dev.mean()); D.append(delta - delta.mean())
        dsd[q] = float(np.std(y, ddof=1) - np.std(x, ddof=1))
    if not d:
        return None, dsd
    d = np.concatenate(d); D = np.concatenate(D)
    slope = float((d @ D) / (d @ d)) if (d @ d) > 0 else np.nan
    return -slope, dsd


def degroot_null(first, last, qid, rng, n_perm=10000):
    """Independent-updating null: permute deltas across agents within question."""
    first = np.asarray(first, float); last = np.asarray(last, float); qid = np.asarray(qid)
    delta = last - first
    ks, sds = [], []
    for _ in range(n_perm):
        dl = delta.copy()
        for q in np.unique(qid):
            s = np.flatnonzero(qid == q)
            dl[s] = dl[rng.permutation(s)]
        k, dsd = degroot(first, first + dl, qid)
        ks.append(k); sds.append(np.mean(list(dsd.values())) if dsd else np.nan)
    return np.array(ks), np.array(sds)
