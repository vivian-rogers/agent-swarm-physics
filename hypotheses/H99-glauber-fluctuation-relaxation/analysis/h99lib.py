"""H99 core: mean-field split of a unit's spins into a collective mode and transverse modes, the fluctuation gain g_chi,
the relaxation gain g_tau and the fluctuation-relaxation gap dg = g_tau - g_chi, with 1-h block bootstrap CIs.

Binary channels (talk, activity): per day an N x L int8 grid, a contiguous kept-minute mask (all-present window).
Spins are centred per agent within (day, 30-min block of the minute index); blocks with < 5 kept minutes dropped.
Per minute t (N agents):  M_t = sum_i X_it / sqrt(N);  c_t = M_t^2;  q_t = sum_i X_it^2 - c_t  (= |X_perp|^2);
p_t = q_t / (N - 1).  Lag-k pairs (t, t+k) inside one block: cc = M_t M_t+k;  qq = sum_i X_it X_i,t+k - cc.
Sums are kept per 1-h bootstrap block; every estimator is a ratio of sums:
  g_chi = 1 - sum p / sum c
  rho_c(k) = sum cc_k / sum (c_t + c_t+k)/2,   rho_perp(k) = sum qq_k / sum (q_t + q_t+k)/2
  g_tau = 1 - ln rho_c(1) / ln rho_perp(1),    dg = g_tau - g_chi
Variants: 'ml' (rates from the slope of ln rho over k = 1..3), 'nr' (noise-robust: lambda = rho(2)/rho(1), signal
variance C(1)/lambda for g_chi), K = tau_c / tau_c^pred.
Content (vector spins per 30-min window) uses the same sums with common agent sets per window pair (content_sums).
"""
from __future__ import annotations

import math

import numpy as np

BLOCK = 30
BOOT_MIN = 60
KMAX = 5
FIELDS = ["n_min", "c", "p"] + [f"{a}{k}" for k in range(1, KMAX + 1) for a in ("cc", "cd", "qq", "qd", "qqn", "np")]


def _zero():
    return {f: 0.0 for f in FIELDS}


def binary_sums(days, keeps, minutes0=None, block=BLOCK, boot_min=BOOT_MIN, stall=None):
    """days: list of N x L arrays; keeps: list of bool L masks. Returns array (n_blocks x len(FIELDS)) of sums per
    (day, 1-h block) and the block ids."""
    out = []
    for k, (S, keep) in enumerate(zip(days, keeps)):
        keep = np.asarray(keep, bool).copy()
        if stall is not None:
            keep &= ~np.asarray(stall[k], bool)
        idx = np.flatnonzero(keep)
        if len(idx) < 10:
            continue
        S = np.asarray(S, float)
        N = S.shape[0]
        if N < 3:
            continue
        blk = idx // block
        X = np.zeros((N, len(idx)))
        ok = np.zeros(len(idx), bool)
        for b in np.unique(blk):
            j = np.flatnonzero(blk == b)
            if len(j) < 5:
                continue
            Y = S[:, idx[j]]
            X[:, j] = Y - Y.mean(1, keepdims=True)
            ok[j] = True
        M = X.sum(0) / math.sqrt(N)
        c = M ** 2
        tot = (X ** 2).sum(0)
        q = tot - c
        p = q / (N - 1)
        hb = idx // boot_min
        for h in np.unique(hb[ok]):
            sel = (hb == h) & ok
            r = _zero()
            r["n_min"] = float(sel.sum())
            r["c"] = float(c[sel].sum())
            r["p"] = float(p[sel].sum())
            js = np.flatnonzero(sel)
            for kk in range(1, KMAX + 1):
                a = js[:-kk] if kk < len(js) else js[:0]
                bb = a + kk
                valid = (bb < len(idx))
                a, bb = a[valid], bb[valid]
                valid = ok[bb] & (idx[bb] - idx[a] == kk) & (blk[bb] == blk[a])
                a, bb = a[valid], bb[valid]
                if not len(a):
                    continue
                cc = M[a] * M[bb]
                tt = (X[:, a] * X[:, bb]).sum(0)
                r[f"cc{kk}"] = float(cc.sum())
                r[f"cd{kk}"] = float(((c[a] + c[bb]) / 2).sum())
                r[f"qq{kk}"] = float((tt - cc).sum())
                r[f"qd{kk}"] = float(((q[a] + q[bb]) / 2).sum())
                r[f"qqn{kk}"] = float(((tt - cc) / (N - 1)).sum())
                r[f"np{kk}"] = float(len(a))
            out.append([r[f] for f in FIELDS])
    return np.array(out, float).reshape(-1, len(FIELDS))


def content_sums(agent, day, win, V, min_common=2, win_block=4):
    """Vector spins: rows (agent, day, window, vector), already centred. One bootstrap block per (day, 2-h block)."""
    out = []
    for d in np.unique(day):
        sd = day == d
        a_d, w_d, V_d = agent[sd], win[sd], V[sd]
        wins = {}
        for i, (a, w) in enumerate(zip(a_d, w_d)):
            wins.setdefault(int(w), {})[int(a)] = V_d[i]
        for hb in sorted({w // win_block for w in wins}):
            r = _content_block({w: dd for w, dd in wins.items() if w // win_block == hb}, wins, min_common)
            out.append([r[f] for f in FIELDS])
    return np.array(out, float).reshape(-1, len(FIELDS))


def _content_block(sub, wins, min_common):
        r = _zero()
        for w, dd in sub.items():
            n = len(dd)
            if n < 2:
                continue
            Xs = np.stack(list(dd.values()))
            M = Xs.sum(0) / math.sqrt(n)
            cw = float(M @ M)
            r["c"] += cw
            r["p"] += (float((Xs ** 2).sum()) - cw) / (n - 1)
            r["n_min"] += 1
        for kk in range(1, KMAX + 1):
            for w, dd in sub.items():
                d2 = wins.get(w + kk)
                if d2 is None:
                    continue
                common = sorted(set(dd) & set(d2))
                n = len(common)
                if n < min_common:
                    continue
                A = np.stack([dd[a] for a in common])
                Bv = np.stack([d2[a] for a in common])
                Ma, Mb = A.sum(0) / math.sqrt(n), Bv.sum(0) / math.sqrt(n)
                cc = float(Ma @ Mb)
                tt = float((A * Bv).sum())
                ca, cb = float(Ma @ Ma), float(Mb @ Mb)
                qa, qb = float((A ** 2).sum()) - ca, float((Bv ** 2).sum()) - cb
                r[f"cc{kk}"] += cc
                r[f"cd{kk}"] += (ca + cb) / 2
                r[f"qq{kk}"] += tt - cc
                r[f"qd{kk}"] += (qa + qb) / 2
                r[f"qqn{kk}"] += (tt - cc) / (n - 1)
                r[f"np{kk}"] += 1
        return r


def _lnr(x):
    return math.log(x) if (x is not None and np.isfinite(x) and 0 < x < 1) else np.nan


def estimates(tot: np.ndarray) -> dict:
    """tot: summed FIELDS vector -> estimators."""
    s = dict(zip(FIELDS, tot))
    out = {"n_min": s["n_min"]}
    out["g_chi"] = 1 - s["p"] / s["c"] if s["c"] > 0 else np.nan
    rc = [s[f"cc{k}"] / s[f"cd{k}"] if s[f"cd{k}"] > 0 else np.nan for k in range(1, KMAX + 1)]
    rp = [s[f"qq{k}"] / s[f"qd{k}"] if s[f"qd{k}"] > 0 else np.nan for k in range(1, KMAX + 1)]
    out.update({f"rho_c{k}": rc[k - 1] for k in range(1, KMAX + 1)})
    out.update({f"rho_p{k}": rp[k - 1] for k in range(1, KMAX + 1)})
    lc, lp = _lnr(rc[0]), _lnr(rp[0])
    out["g_tau"] = 1 - lc / lp if np.isfinite(lc) and np.isfinite(lp) else np.nan
    out["dg"] = out["g_tau"] - out["g_chi"]
    for k in range(2, KMAX + 1):
        a_, b_ = _lnr(rc[k - 1]), _lnr(rp[k - 1])
        out[f"g_tau{k}"] = 1 - a_ / b_ if np.isfinite(a_) and np.isfinite(b_) else np.nan
        out[f"dg{k}"] = out[f"g_tau{k}"] - out["g_chi"]
    # Amendment A2 (post hoc, robust at rho_perp ~ 0): collective memory excess over the Glauber prediction
    for k in (1, 2):
        rpk = rp[k - 1]
        if np.isfinite(rc[k - 1]) and np.isfinite(rpk) and np.isfinite(out["g_chi"]) and out["g_chi"] < 1:
            out[f"drho{k}"] = rc[k - 1] - min(max(rpk, 1e-3), 0.999) ** (1 - out["g_chi"])
        else:
            out[f"drho{k}"] = np.nan
    out["tau_c"] = -1 / lc if np.isfinite(lc) else np.nan
    out["tau_p"] = -1 / lp if np.isfinite(lp) else np.nan
    out["tau_c_pred"] = out["tau_p"] / (1 - out["g_chi"]) if np.isfinite(out["tau_p"]) and out["g_chi"] < 1 else np.nan
    out["K"] = out["tau_c"] / out["tau_c_pred"] if np.isfinite(out["tau_c_pred"]) and out["tau_c_pred"] > 0 else np.nan
    # multi-lag slopes (k = 1..3, with intercept)
    ks = np.arange(1, 4)
    def slope(r):
        r = np.array(r, float)
        ok = np.isfinite(r) & (r > 0) & (r < 1)
        if ok.sum() < 2:
            return np.nan
        return -np.polyfit(ks[ok], np.log(r[ok]), 1)[0]
    sc, sp = slope(rc[:3]), slope(rp[:3])
    out["g_tau_ml"] = 1 - sc / sp if np.isfinite(sc) and np.isfinite(sp) and sp > 0 else np.nan
    out["dg_ml"] = out["g_tau_ml"] - out["g_chi"]
    # noise-robust
    lam_c = rc[1] / rc[0] if np.isfinite(rc[0]) and rc[0] > 0 and np.isfinite(rc[1]) else np.nan
    lam_p = rp[1] / rp[0] if np.isfinite(rp[0]) and rp[0] > 0 and np.isfinite(rp[1]) else np.nan
    llc, llp = _lnr(lam_c), _lnr(lam_p)
    out["g_tau_nr"] = 1 - llc / llp if np.isfinite(llc) and np.isfinite(llp) else np.nan
    if s["np1"] > 0 and np.isfinite(lam_c) and np.isfinite(lam_p) and lam_c > 0 and lam_p > 0 and s["qqn1"] > 0:
        Cc = s["cc1"] / s["np1"] / lam_c
        Cp = s["qqn1"] / s["np1"] / lam_p
        out["g_chi_nr"] = 1 - Cp / Cc if Cc > 0 else np.nan
    else:
        out["g_chi_nr"] = np.nan
    out["dg_nr"] = out["g_tau_nr"] - out["g_chi_nr"]
    return out


STATS = ["g_chi", "g_tau", "dg", "rho_c1", "rho_p1", "tau_c", "tau_p", "tau_c_pred", "K", "g_tau_ml", "dg_ml",
         "g_tau_nr", "g_chi_nr", "dg_nr", "g_tau2", "dg2", "g_tau3", "dg3", "g_tau5", "dg5", "rho_c3", "rho_p3",
         "drho1", "drho2", "rho_c2", "rho_p2"]


def boot(rows: np.ndarray, B: int = 400, rng=None) -> dict:
    """Point estimates and percentile CIs from per-block sums (resampling blocks with replacement)."""
    rng = rng or np.random.default_rng(0)
    est = estimates(rows.sum(0))
    if len(rows) < 3:
        return {**est, **{f"{k}_lo": np.nan for k in STATS}, **{f"{k}_hi": np.nan for k in STATS}, "n_blocks": len(rows)}
    draws = {k: [] for k in STATS}
    for _ in range(B):
        e = estimates(rows[rng.integers(0, len(rows), len(rows))].sum(0))
        for k in STATS:
            draws[k].append(e[k])
    out = dict(est)
    for k in STATS:
        v = np.array(draws[k], float)
        v = v[np.isfinite(v)]
        out[f"{k}_lo"] = float(np.percentile(v, 2.5)) if len(v) > 0.8 * B else np.nan
        out[f"{k}_hi"] = float(np.percentile(v, 97.5)) if len(v) > 0.8 * B else np.nan
        out[f"{k}_se"] = float(v.std(ddof=1)) if len(v) > 0.8 * B else np.nan
    out["n_blocks"] = len(rows)
    return out


def block_shift(days, keeps, rng, block=BLOCK):
    """DQ8 trimmed block-shift surrogate: each agent's series circularly shifted within each (day, 30-min block)."""
    out = []
    for S, keep in zip(days, keeps):
        S = np.asarray(S).copy()
        idx = np.flatnonzero(keep)
        blk = idx // block
        for b in np.unique(blk):
            j = idx[blk == b]
            if len(j) < 2:
                continue
            for i in range(S.shape[0]):
                S[i, j] = np.roll(S[i, j], rng.integers(1, len(j)))
        out.append(S)
    return out


def re_pool(est, se):
    """DerSimonian-Laird random-effects mean."""
    est, se = np.asarray(est, float), np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[ok], se[ok]
    if not len(est):
        return {"mean": np.nan, "lo": np.nan, "hi": np.nan, "k": 0}
    w = 1 / se ** 2
    m = (w * est).sum() / w.sum()
    Q = (w * (est - m) ** 2).sum()
    tau2 = max(0.0, (Q - (len(est) - 1)) / (w.sum() - (w ** 2).sum() / w.sum())) if len(est) > 1 else 0.0
    ws = 1 / (se ** 2 + tau2)
    mm = (ws * est).sum() / ws.sum()
    s = math.sqrt(1 / ws.sum())
    return {"mean": float(mm), "lo": float(mm - 1.96 * s), "hi": float(mm + 1.96 * s), "k": int(len(est))}


# ------------------------------------------------------------------------------------------- kick layer
def kick_kernel(days, keeps, kicks_by_day, rooms_by_day, L=15, block=BLOCK):
    """Distributed-lag OLS of the room's centred talk count on lagged kick indicators (lags 0..L), both centred within
    (day, 30-min block). Returns the design pieces per 1-h block so the bootstrap can resample blocks:
    list of (XtX, Xty) per block."""
    pieces = []
    for k, (S, keep) in enumerate(zip(days, keeps)):
        idx = np.flatnonzero(keep)
        if len(idx) < 30:
            continue
        S = np.asarray(S, float)
        rooms = rooms_by_day[k]
        kk = kicks_by_day.get(k, [])
        if not kk:
            continue
        for rm in np.unique([r for _, r in kk]):
            members = np.flatnonzero((rooms == rm) | (rm < 0)) if (rooms >= 0).any() else np.arange(S.shape[0])
            if len(members) < 2:
                continue
            y = S[members][:, idx].sum(0)
            kick = np.zeros(S.shape[1])
            for m, r in kk:
                if r == rm:
                    kick[m] += 1
            Xl = np.stack([np.r_[np.zeros(l), kick[:S.shape[1] - l]][idx] for l in range(L + 1)], 1)
            blk = idx // block
            yc, Xc = y.copy(), Xl.copy()
            for b in np.unique(blk):
                j = blk == b
                yc[j] -= yc[j].mean()
                Xc[j] -= Xc[j].mean(0)
            hb = idx // BOOT_MIN
            for h in np.unique(hb):
                j = hb == h
                pieces.append((Xc[j].T @ Xc[j], Xc[j].T @ yc[j], float(Xl[j, 0].sum())))
    return pieces


def kernel_from(pieces, ridge=1e-6):
    XtX = sum(p[0] for p in pieces)
    Xty = sum(p[1] for p in pieces)
    return np.linalg.solve(XtX + ridge * np.eye(len(Xty)), Xty)


def tail_mean_delay(beta, start=None):
    """Mean delay after the peak, sum_{j>=0} j b_{p+j} / sum b_{p+j} over positive tail (geometric: lam/(1-lam))."""
    beta = np.asarray(beta, float)
    p = int(np.argmax(beta[:6])) if start is None else start
    t = np.clip(beta[p:], 0, None)
    if t.sum() <= 0:
        return np.nan, p
    j = np.arange(len(t))
    return float((j * t).sum() / t.sum()), p


def geom_ratio(beta, K=5):
    """Geometric-ratio decay estimate of a kernel over lags 0..K: lambda = sum b[1..K] / sum b[0..K-1] (exact for
    b_l = A lambda^l). Amendment A2: replaces the tail mean delay, which reads noise as a long tail."""
    beta = np.asarray(beta, float)
    den = beta[:K].sum()
    return float(beta[1:K + 1].sum() / den) if den > 0 else np.nan


def geom_mean_delay(lam, J):
    """Mean of j under weights lam^j truncated at j = 0..J (comparable to tail_mean_delay)."""
    if not np.isfinite(lam) or lam <= 0:
        return np.nan
    j = np.arange(J + 1)
    w = lam ** j
    return float((j * w).sum() / w.sum())
