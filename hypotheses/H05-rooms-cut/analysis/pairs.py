"""Pair-day outcomes and difference-in-differences machinery for H05 (numpy only).

Outcomes per pair (i<j) per day, from within-day transitions of +-1 spins:
  kappa   symmetric lagged correlation 0.5 [corr(s_i(t+1), s_j(t)) + corr(s_j(t+1), s_i(t))]
  c0      contemporaneous correlation corr(s_i(t), s_j(t))
  sig     bias-corrected Gaussian pair EP bound 2 (gbar^2 - s^2/T) / s^2 for g_ij (nats per bin)
  gbar    mean of g_ij (sign = direction: > 0 means j leads i)
plus the co-location fraction (share of the day's transitions with room_i == room_j, both known).
"""
from __future__ import annotations

import numpy as np

from ep import g_matrix, pair_ep_gauss


def pair_day_table(S, day, agent_ids, room=None, min_trans=30, min_flips=4):
    """S: (T, N) +-1 sorted by (day, minute); day: (T,); room: (T, N) room codes (-1 unknown) or None.

    Returns dict of equal-length arrays, one row per (day, i<j) with both spins non-constant that day."""
    rows = {k: [] for k in ("day", "i", "j", "kappa", "c0", "sig", "gbar", "n", "act_i", "act_j", "coloc", "known")}
    N = S.shape[1]
    pi, pj = np.triu_indices(N, 1)
    for d in np.unique(day):
        idx = np.flatnonzero(day == d)
        if len(idx) < min_trans + 1:
            continue
        Sd = S[idx].astype(np.float64)
        Sp, Sn = Sd[:-1], Sd[1:]
        flips = (Sp != Sn).sum(0)
        okag = flips >= min_flips
        m = Sd.mean(0)
        Xc = Sn - Sn.mean(0); Yc = Sp - Sp.mean(0)
        sx, sy = Xc.std(0), Yc.std(0)
        with np.errstate(invalid="ignore", divide="ignore"):
            C1 = (Xc.T @ Yc) / len(Xc) / np.outer(sx, sy)
            Z = Sd - m; sz = Z.std(0)
            C0 = (Z.T @ Z) / len(Z) / np.outer(sz, sz)
        sel = okag[pi] & okag[pj]
        if not sel.any():
            continue
        a, b = pi[sel], pj[sel]
        G = g_matrix(Sp, Sn, a, b, dtype=np.float64)
        sig = pair_ep_gauss(G)
        if room is not None:
            R = room[idx][:-1]
            known = (R[:, a] >= 0) & (R[:, b] >= 0)
            same = (R[:, a] == R[:, b]) & known
            kn = known.mean(0)
            with np.errstate(invalid="ignore", divide="ignore"):
                col = np.where(known.sum(0) > 0, same.sum(0) / np.maximum(known.sum(0), 1), np.nan)
        else:
            kn = np.ones(len(a)); col = np.ones(len(a))
        rows["day"].append(np.full(len(a), d)); rows["i"].append(agent_ids[a]); rows["j"].append(agent_ids[b])
        rows["kappa"].append(0.5 * (C1[a, b] + C1[b, a])); rows["c0"].append(C0[a, b])
        rows["sig"].append(sig); rows["gbar"].append(G.mean(0)); rows["n"].append(np.full(len(a), len(Sp)))
        rows["act_i"].append((m[a] + 1) / 2); rows["act_j"].append((m[b] + 1) / 2)
        rows["coloc"].append(col); rows["known"].append(kn)
    return {k: (np.concatenate(v) if v else np.array([])) for k, v in rows.items()}


def _demean(y, groups, iters=200, tol=1e-10):
    """Alternating projections: remove every set of group means (two-way fixed effects)."""
    y = y.astype(np.float64).copy()
    for _ in range(iters):
        before = y.copy()
        for g in groups:
            s = np.bincount(g, weights=y)
            c = np.bincount(g)
            y -= (s / np.maximum(c, 1))[g]
        if np.max(np.abs(y - before)) < tol:
            break
    return y


def _codes(x):
    _, inv = np.unique(x, return_inverse=True)
    return inv


def twfe(y, x, pair_key, day_key, controls=None):
    """y = a_pair + g_day + beta x (+ controls) + e. Returns beta and cluster-robust SEs.

    SEs: clustered by pair, by day, and two-way (Cameron-Gelbach-Miller: V_pair + V_day - V_het)."""
    ok = np.isfinite(y) & np.isfinite(x)
    if controls is not None:
        ok &= np.all(np.isfinite(controls), axis=1)
    y, x = y[ok], x[ok]
    pk, dk = _codes(pair_key[ok]), _codes(day_key[ok])
    X = x[:, None] if controls is None else np.column_stack([x, controls[ok]])
    yt = _demean(y, [pk, dk])
    Xt = np.column_stack([_demean(X[:, c], [pk, dk]) for c in range(X.shape[1])])
    XtX = Xt.T @ Xt
    if np.linalg.cond(XtX) > 1e12 or np.allclose(Xt[:, 0], 0):
        return {"beta": np.nan, "n": int(ok.sum())}
    B = np.linalg.solve(XtX, Xt.T @ yt)
    e = yt - Xt @ B
    Ainv = np.linalg.inv(XtX)

    def vclust(g):
        k = g.max() + 1
        sc = np.zeros((k, Xt.shape[1]))
        for c in range(Xt.shape[1]):
            sc[:, c] = np.bincount(g, weights=Xt[:, c] * e, minlength=k)
        M = sc.T @ sc
        G = len(np.unique(g))
        return Ainv @ M @ Ainv * G / max(G - 1, 1)

    Vp, Vd = vclust(pk), vclust(dk)
    Vh = vclust(np.arange(len(e)))
    V2 = Vp + Vd - Vh
    return {"beta": float(B[0]), "se_pair": float(np.sqrt(Vp[0, 0])), "se_day": float(np.sqrt(Vd[0, 0])),
            "se_twoway": float(np.sqrt(max(V2[0, 0], Vp[0, 0], Vd[0, 0]))), "n": int(ok.sum()),
            "n_pairs": int(pk.max() + 1), "n_days": int(dk.max() + 1),
            "n_switchers": int(np.sum(np.bincount(pk, weights=x) % np.maximum(np.bincount(pk), 1) != 0))}


def did_2x2(y, pair_key, period, treated, pre, post):
    """Classic pair DiD: mean over treated pairs of (post - pre) minus the same for controls.

    Pair means are taken first (each pair weighs once). Returns effect, n pairs, and pair-level diffs."""
    out = {}
    pairs = np.unique(pair_key)
    diffs, tr = [], []
    for p in pairs:
        m = pair_key == p
        a = y[m & (period == pre)]; b = y[m & (period == post)]
        a, b = a[np.isfinite(a)], b[np.isfinite(b)]
        if len(a) == 0 or len(b) == 0:
            continue
        diffs.append(b.mean() - a.mean()); tr.append(bool(treated[m][0]))
    diffs, tr = np.array(diffs), np.array(tr)
    if tr.sum() == 0 or (~tr).sum() == 0:
        return {"effect": np.nan, "n_treated": int(tr.sum()), "n_control": int((~tr).sum())}
    out["effect"] = float(diffs[tr].mean() - diffs[~tr].mean())
    out["d_treated"] = float(diffs[tr].mean()); out["d_control"] = float(diffs[~tr].mean())
    out["n_treated"] = int(tr.sum()); out["n_control"] = int((~tr).sum())
    return out
