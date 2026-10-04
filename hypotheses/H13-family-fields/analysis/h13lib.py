"""H13 estimators (numpy only; no project data touched here). Used by synthetic.py, explore.py and confirm.py.

Family labels: multi-member labs (>= 2 eligible agents in the unit, up to KMAX largest) get codes 0..K-1; every
other agent gets its own unique code >= K (a singleton: enters cross-family pairs only).

(a)  family field:   T_field = mean cos(H_i, H_j) [same multi-member family] - mean cos [different family]
(b)  K x K coupling: H05's block_J (naive mean-field inversion of block-averaged correlations) with family blocks
(c)  family vs room: pair OLS y = c + b_lab same_lab + b_room same_room, node-level permutations
(d)  leave-one-agent-out nearest-family-centroid classification
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "H05-rooms-cut/analysis"))
from mf_blocks import block_J  # noqa: E402  (H05 two-block MF, already general in the number of blocks)

KMAX = 5


# ----------------------------------------------------------------------------- basics
def unit(X, axis=-1):
    X = np.asarray(X, dtype=np.float64)
    n = np.linalg.norm(X, axis=axis, keepdims=True)
    return X / np.where(n > 0, n, 1)


def fam_labels(labs, kmax=KMAX, min_size=2):
    """labs: sequence of lab names. Returns (codes, multi_names)."""
    c = Counter(labs)
    multi = [l for l, n in sorted(c.items(), key=lambda x: (-x[1], str(x[0]))) if n >= min_size and l is not None][:kmax]
    code = {l: k for k, l in enumerate(multi)}
    out = np.empty(len(labs), dtype=np.int64)
    nxt = len(multi)
    for i, l in enumerate(labs):
        if l in code:
            out[i] = code[l]
        else:
            out[i] = nxt
            nxt += 1
    return out, multi


def pairs(n):
    return np.triu_indices(n, 1)


def dl_meta(est, se):
    """DerSimonian-Laird random-effects summary. Returns dict(mu, se, lo, hi, z, p, tau2, I2, k)."""
    est, se = np.asarray(est, float), np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[ok], se[ok]
    k = len(est)
    if k == 0:
        return {"k": 0}
    w = 1 / se ** 2
    mu_f = np.sum(w * est) / np.sum(w)
    Q = np.sum(w * (est - mu_f) ** 2)
    c = np.sum(w) - np.sum(w ** 2) / np.sum(w)
    tau2 = max(0.0, (Q - (k - 1)) / c) if k > 1 and c > 0 else 0.0
    ws = 1 / (se ** 2 + tau2)
    mu = np.sum(ws * est) / np.sum(ws)
    s = np.sqrt(1 / np.sum(ws))
    from scipy.stats import norm
    I2 = max(0.0, (Q - (k - 1)) / Q) if Q > 0 and k > 1 else 0.0
    return {"k": int(k), "mu": float(mu), "se": float(s), "lo": float(mu - 1.96 * s), "hi": float(mu + 1.96 * s),
            "z": float(mu / s), "p": float(2 * norm.sf(abs(mu / s))), "tau2": float(tau2), "I2": float(I2)}


def jackknife_se(fn, n):
    """Delete-one-agent jackknife SE of a statistic fn(keep_mask)."""
    vals = []
    for i in range(n):
        m = np.ones(n, bool)
        m[i] = False
        v = fn(m)
        if np.isfinite(v):
            vals.append(v)
    vals = np.array(vals)
    if len(vals) < 3:
        return np.nan
    return float(np.sqrt((len(vals) - 1) / len(vals) * np.sum((vals - vals.mean()) ** 2)))


# ----------------------------------------------------------------------------- (a) family field
def day_demean(V, days, agents, min_agents=3):
    """Subtract the equal-weight mean over agents present each day. Rows on days with < min_agents are dropped."""
    D = np.full_like(V, np.nan, dtype=np.float64)
    for d in np.unique(days):
        k = days == d
        if k.sum() < min_agents:
            continue
        D[k] = V[k] - V[k].mean(0)
    return D


def agent_means(D, agents, min_days=2):
    ok = np.isfinite(D).all(1)
    ags, H, nd = [], [], []
    for a in np.unique(agents[ok]):
        k = ok & (agents == a)
        if k.sum() >= min_days:
            ags.append(a); H.append(D[k].mean(0)); nd.append(int(k.sum()))
    return np.array(ags), (np.array(H) if H else np.zeros((0, D.shape[1]))), np.array(nd)


def wa_stat(c, ii, jj, fam, K, keep=None):
    same = fam[ii] == fam[jj]
    w = same & (fam[ii] < K)
    a = ~same
    if keep is not None:
        w &= keep; a &= keep
    if w.sum() == 0 or a.sum() == 0:
        return np.nan
    return float(c[w].mean() - c[a].mean())


def wa_perm(c, ii, jj, fam, K, keep=None, nperm=5000, rng=None, chunk=1000):
    """Within-minus-across mean of a pair statistic c, with lab-label permutation null (sizes preserved)."""
    rng = np.random.default_rng(rng)
    obs = wa_stat(c, ii, jj, fam, K, keep)
    kp = np.ones(len(c), bool) if keep is None else keep
    null = []
    done = 0
    while done < nperm:
        m = min(chunk, nperm - done)
        P = np.stack([rng.permutation(fam) for _ in range(m)])
        Fi, Fj = P[:, ii], P[:, jj]
        same = Fi == Fj
        w = same & (Fi < K) & kp
        a = ~same & kp
        with np.errstate(invalid="ignore", divide="ignore"):
            null.append((w * c).sum(1) / w.sum(1) - (a * c).sum(1) / a.sum(1))
        done += m
    null = np.concatenate(null)
    null = null[np.isfinite(null)]
    p = float((1 + np.sum(null >= obs)) / (1 + len(null))) if np.isfinite(obs) else np.nan
    return {"obs": obs, "p": p, "null_mean": float(null.mean()) if len(null) else np.nan,
            "null_sd": float(null.std()) if len(null) else np.nan}


def field_test(H, fam, K, keep_pairs=None, nperm=5000, rng=None, jack=True):
    """T_field on agent mean vectors H (n x d). keep_pairs: optional boolean (n, n) of pairs to use."""
    n = len(H)
    ii, jj = pairs(n)
    C = unit(H) @ unit(H).T
    c = C[ii, jj]
    keep = keep_pairs[ii, jj] if keep_pairs is not None else None
    r = wa_perm(c, ii, jj, fam, K, keep, nperm, rng)
    r["n_within"] = int(((fam[ii] == fam[jj]) & (fam[ii] < K) & (keep if keep is not None else True)).sum())
    r["n_across"] = int(((fam[ii] != fam[jj]) & (keep if keep is not None else True)).sum())
    if jack:
        def f(m):
            sub = np.flatnonzero(m)
            i2, j2 = pairs(len(sub))
            c2 = C[np.ix_(sub, sub)][i2, j2]
            k2 = keep_pairs[np.ix_(sub, sub)][i2, j2] if keep_pairs is not None else None
            return wa_stat(c2, i2, j2, fam[sub], K, k2)
        r["se_jack"] = jackknife_se(f, n)
    return r


def r2_fam(H, fam, K):
    m = fam < K
    if m.sum() < 3 or len(np.unique(fam[m])) < 2:
        return np.nan
    X = unit(H[m]); f = fam[m]
    tot = ((X - X.mean(0)) ** 2).sum()
    btw = sum((f == k).sum() * ((X[f == k].mean(0) - X.mean(0)) ** 2).sum() for k in np.unique(f))
    return float(btw / tot)


def r2_perm(H, fam, K, nperm=2000, rng=None):
    rng = np.random.default_rng(rng)
    obs = r2_fam(H, fam, K)
    null = np.array([r2_fam(H, rng.permutation(fam), K) for _ in range(nperm)])
    return {"obs": obs, "p": float((1 + np.sum(null >= obs)) / (1 + nperm)), "null_mean": float(np.nanmean(null))}


def family_fields(H, fam, K):
    """h_f = mean of unit-normalized member vectors, for f < K."""
    Hn = unit(H)
    return {k: Hn[fam == k].mean(0) for k in range(K) if (fam == k).sum() > 0}


# ----------------------------------------------------------------------------- (d) classification
def loo_acc(H, fam, K):
    Hn = unit(H)
    idx = np.flatnonzero(fam < K)
    if len(idx) < 3:
        return np.nan
    hit = 0
    for i in idx:
        best, arg = -np.inf, -1
        for k in range(K):
            m = fam == k
            m[i] = False
            if m.sum() == 0:
                continue
            s = float(unit(Hn[m].mean(0)) @ Hn[i])
            if s > best:
                best, arg = s, k
        hit += int(arg == fam[i])
    return hit / len(idx)


def loo_perm(H, fam, K, nperm=1000, rng=None):
    rng = np.random.default_rng(rng)
    obs = loo_acc(H, fam, K)
    null = np.array([loo_acc(H, rng.permutation(fam), K) for _ in range(nperm)])
    return {"obs": obs, "p": float((1 + np.sum(null >= obs)) / (1 + nperm)), "null_mean": float(np.nanmean(null)),
            "n": int((fam < K).sum())}


# ----------------------------------------------------------------------------- (b) K x K mean-field couplings
def kxk_from_pairs(ai, aj, r, sv, fam, K):
    """block_J on pair arrays (indices into fam). Returns (point dict, K x K matrix with 'other' row/col)."""
    q = block_J(ai, aj, r, sv, fam)
    J = q["J"]; npairs = q["n_pairs"]
    M = np.full((K + 1, K + 1), np.nan)
    acc = {}
    for key, v in J.items():
        a, b = (int(x) for x in key.split("-"))
        A, B = min(a, K), min(b, K)
        A, B = min(A, B), max(A, B)
        acc.setdefault((A, B), []).append((v, npairs[key]))
    for (A, B), lst in acc.items():
        vals = np.array([x for x, _ in lst]); wts = np.array([w for _, w in lst], float)
        ok = np.isfinite(vals)
        if ok.any():
            M[A, B] = M[B, A] = float(np.average(vals[ok], weights=wts[ok]))
    q["M"] = M
    return q


def kxk_test(Rm, Sv, ai, aj, fam, K, nboot=500, nperm=2000, rng=None):
    """Rm, Sv: (pairs x days) excess correlations and sqrt(v_i v_j). Day bootstrap + lab permutation of Delta."""
    rng = np.random.default_rng(rng)
    with np.errstate(invalid="ignore"):
        rbar, sbar = np.nanmean(Rm, 1), np.nanmean(Sv, 1)
    point = kxk_from_pairs(ai, aj, rbar, sbar, fam, K)
    out = {"J_in": point["J_in"], "J_out": point["J_out"], "delta": point["J_in_minus_out"],
           "loop_gain": point["loop_gain"], "M": point["M"].tolist(),
           "ratio": float(point["J_in"] / point["J_out"]) if point["J_out"] and np.isfinite(point["J_out"]) else np.nan}
    nd = Rm.shape[1]
    if nboot and nd >= 2:
        bs = []
        for _ in range(nboot):
            c = rng.integers(nd, size=nd)
            with np.errstate(invalid="ignore"):
                q = block_J(ai, aj, np.nanmean(Rm[:, c], 1), np.nanmean(Sv[:, c], 1), fam)
            bs.append(q["J_in_minus_out"])
        bs = np.array(bs, float)
        out["delta_ci95"] = [float(np.nanpercentile(bs, 2.5)), float(np.nanpercentile(bs, 97.5))]
        out["delta_se"] = float(np.nanstd(bs))
    if nperm:
        null = np.array([block_J(ai, aj, rbar, sbar, rng.permutation(fam))["J_in_minus_out"] for _ in range(nperm)])
        null = null[np.isfinite(null)]
        out["p_perm"] = float((1 + np.sum(null >= out["delta"])) / (1 + len(null))) if np.isfinite(out["delta"]) else np.nan
        out["null_sd"] = float(null.std())
    # raw pair-mean contrast (no inversion), as a check
    out["r_within_minus_across"] = wa_stat(rbar, ai, aj, fam, K)
    return out


def comove_matrix(agent, win, V, min_agents=4, min_shared=5, window_demean=False):
    """Content co-movement. V rows = agent-window vectors; windows with >= min_agents agents are kept.

    Primary (window_demean=False, amended after synthetic F3): x = v - agent mean of v. The common window field then
    adds a uniform positive correlation to every pair, which cancels in J_in - J_out. Removing the window mean
    instead gives every pair r ~ -1/(n_w - 1) and makes the naive mean-field inversion singular.
    Returns (agents, X residual rows, keep mask)."""
    V = np.asarray(V, np.float64)
    keep = np.zeros(len(V), bool)
    Xm = np.full_like(V, np.nan)
    for w in np.unique(win):
        k = win == w
        if k.sum() >= min_agents:
            Xm[k] = V[k] - V[k].mean(0) if window_demean else V[k]
            keep[k] = True
    ags = np.unique(agent[keep])
    for a in ags:
        k = keep & (agent == a)
        Xm[k] -= Xm[k].mean(0)
    return ags, Xm, keep


def comove_r(ags, agent, win, X, keep, min_shared=5, rot=None):
    """Vector correlation r_ij over shared windows. rot: optional dict agent -> orthogonal matrix."""
    n = len(ags)
    wins = np.unique(win[keep])
    widx = {w: k for k, w in enumerate(wins)}
    d = X.shape[1]
    T = np.zeros((n, len(wins), d)); P = np.zeros((n, len(wins)), bool)
    ai = {a: k for k, a in enumerate(ags)}
    for r in np.flatnonzero(keep):
        a, w = agent[r], win[r]
        x = X[r] if rot is None else rot[a] @ X[r]
        T[ai[a], widx[w]] = x; P[ai[a], widx[w]] = True
    R = np.full((n, n), np.nan)
    for i in range(n):
        for j in range(i + 1, n):
            s = P[i] & P[j]
            if s.sum() < min_shared:
                continue
            num = np.sum(T[i, s] * T[j, s]); den = np.sqrt(np.sum(T[i, s] ** 2) * np.sum(T[j, s] ** 2))
            if den > 0:
                R[i, j] = R[j, i] = num / den
    return R


def random_rotation(d, rng):
    Q, Rr = np.linalg.qr(rng.normal(size=(d, d)))
    return Q * np.sign(np.diag(Rr))


# ----------------------------------------------------------------------------- (a3) invariance across units
def invariance(Hu, lab_of, fams, nperm=1000, rng=None, A=None, B=None):
    """Hu: list (ordered by date) of dicts agent -> unit-normalized H_i in that unit (one regime basis).

    Family level: units split alternately into A/B; h_f^S = unit(mean over units in S of the unit family field), the
    unit family field being unit(mean of members' H). Statistic: cos(h_f^A, h_f^B), median over fams.
    Null (amended after synthetic F2): a fixed random regrouping of the agent pool (one global permutation of
    agent -> lab, applied to every unit), so stable agent offsets alone set the baseline. The cross-family cosine is
    reported too, but it is negative by construction (day-demeaned fields sum to ~0).
    Agent level: cos(unit(mean_A H_i), unit(mean_B H_i)) for agents present in both halves.
    All pairs: mean over unit pairs of cos(h_{f,u}, h_{f,u'})."""
    rng = np.random.default_rng(rng)
    U = len(Hu)
    if A is None or B is None:          # default: alternate split; confirm.py passes A = exploration, B = holdout
        A, B = list(range(0, U, 2)), list(range(1, U, 2))
    pool = sorted(set().union(*[set(h) for h in Hu]))

    def ufield(labmap):
        out = []
        for h in Hu:
            d = {}
            for f in fams:
                m = [h[a] for a in h if labmap.get(a) == f]
                if m:
                    d[f] = unit(np.mean(m, 0))
            out.append(d)
        return out

    def stats(labmap):
        uf = ufield(labmap)
        hs = lambda S, f: unit(np.mean([uf[u][f] for u in S if f in uf[u]], 0)) if any(f in uf[u] for u in S) else None
        cs, cross, allp = {}, [], {}
        hA = {f: hs(A, f) for f in fams}; hB = {f: hs(B, f) for f in fams}
        for f in fams:
            if hA[f] is not None and hB[f] is not None:
                cs[f] = float(hA[f] @ hB[f])
            for g in fams:
                if g != f and hA[f] is not None and hB[g] is not None:
                    cross.append(float(hA[f] @ hB[g]))
            v = [float(uf[u][f] @ uf[w][f]) for u in range(U) for w in range(u + 1, U) if f in uf[u] and f in uf[w]]
            allp[f] = float(np.mean(v)) if v else np.nan
        return cs, (float(np.median(list(cs.values()))) if cs else np.nan), \
            (float(np.mean(cross)) if cross else np.nan), allp

    cs, med, cross, allp = stats(lab_of)
    labs_pool = [lab_of[a] for a in pool]
    null_med, null_all = [], []
    for _ in range(nperm):
        perm = dict(zip(pool, rng.permutation(labs_pool)))
        _, m, _, ap = stats(perm)
        null_med.append(m); null_all.append(np.nanmean(list(ap.values())))
    null_med = np.array(null_med); null_all = np.array(null_all)
    ag = []
    for a in pool:
        xa = [Hu[u][a] for u in A if a in Hu[u]]; xb = [Hu[u][a] for u in B if a in Hu[u]]
        if xa and xb:
            ag.append(float(unit(np.mean(xa, 0)) @ unit(np.mean(xb, 0))))
    obs_all = float(np.nanmean(list(allp.values())))
    return {"family_cos": cs, "family_median": med, "crossfamily_cos": cross,
            "null_regroup_median_mean": float(np.nanmean(null_med)), "null_regroup_median_p95": float(np.nanpercentile(null_med, 95)),
            "p_regroup": float((1 + np.sum(null_med >= med)) / (1 + np.sum(np.isfinite(null_med)))),
            "allpairs_cos": allp, "allpairs_mean": obs_all, "allpairs_null_mean": float(np.nanmean(null_all)),
            "p_allpairs": float((1 + np.sum(null_all >= obs_all)) / (1 + np.sum(np.isfinite(null_all)))),
            "agent_median": float(np.median(ag)) if ag else np.nan, "n_agents_both": len(ag), "units_A": A, "units_B": B}


def fixed_offset_residual(Hn, S):
    """S-b: remove the cross-fitted fixed per-agent offset S (agent mean over other units) by projection
    (primary) and by subtraction (variant). Hn, S: (n x d), Hn unit-normalized."""
    Sn = unit(S)
    proj = Hn - np.sum(Hn * Sn, 1, keepdims=True) * Sn
    sub = Hn - S
    return proj, sub


# ----------------------------------------------------------------------------- (c) family vs room
def famroom(Y, lab, room, K, nperm=2000, rng=None, jack=True):
    """Y: (n x n) symmetric pair outcome (NaN = missing). lab: family codes; room: room codes (-1 = drop)."""
    rng = np.random.default_rng(rng)
    n = len(lab)
    ii, jj = pairs(n)
    y = Y[ii, jj]
    ok = np.isfinite(y) & (room[ii] >= 0) & (room[jj] >= 0)
    ii, jj, y = ii[ok], jj[ok], y[ok]

    def fit(L, Rm, sub=None):
        i2, j2, yy = (ii, jj, y) if sub is None else sub
        sl = ((L[i2] == L[j2]) & (L[i2] < K)).astype(float)
        sr = (Rm[i2] == Rm[j2]).astype(float)
        X = np.column_stack([np.ones(len(yy)), sl, sr])
        if np.linalg.matrix_rank(X) < 3:
            return np.nan, np.nan
        b = np.linalg.lstsq(X, yy, rcond=None)[0]
        return b[1], b[2]

    bl, br = fit(lab, room)
    nl = np.array([fit(rng.permutation(lab), room)[0] for _ in range(nperm)])
    # room permutation among agents with a known room only
    kn = np.flatnonzero(room >= 0)
    def proom():
        r2 = room.copy(); r2[kn] = rng.permutation(room[kn]); return r2
    nr = np.array([fit(lab, proom())[1] for _ in range(nperm)])
    out = {"b_lab": float(bl), "b_room": float(br), "n_pairs": int(len(y)),
           "p_lab": float((1 + np.sum(nl >= bl)) / (1 + np.sum(np.isfinite(nl)))) if np.isfinite(bl) else np.nan,
           "p_room": float((1 + np.sum(nr >= br)) / (1 + np.sum(np.isfinite(nr)))) if np.isfinite(br) else np.nan,
           "null_sd_lab": float(np.nanstd(nl)), "null_sd_room": float(np.nanstd(nr)),
           "n_same_lab_cross_room": int(np.sum((lab[ii] == lab[jj]) & (lab[ii] < K) & (room[ii] != room[jj]))),
           "n_same_lab_same_room": int(np.sum((lab[ii] == lab[jj]) & (lab[ii] < K) & (room[ii] == room[jj])))}
    if jack:
        def f_l(m, which=0):
            sub_ok = m[ii] & m[jj]
            r = fit(lab, room, (ii[sub_ok], jj[sub_ok], y[sub_ok]))
            return r[which]
        out["se_lab"] = jackknife_se(lambda m: f_l(m, 0), n)
        out["se_room"] = jackknife_se(lambda m: f_l(m, 1), n)
    return out
