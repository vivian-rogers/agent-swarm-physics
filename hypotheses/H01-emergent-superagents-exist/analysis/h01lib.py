"""H01 estimators for D3.1.a (ideological order on mined statements) and D3.2 / D3.2' (coupling vs field).

Data-structure agnostic: every estimator takes a `Unit` (one analysis unit = goal period split at step changes, or one
synthetic period), so the synthetic validation, the exploration and the confirm script run the same code.

Unit fields
  agents (n_ad,) agent code per agent-day; day (n_ad,) day index 0..T-1; room (n_ad,) room code (-1 unknown)
  V (n_ad, d) unit agent-day vectors; nstmt (n_ad,); rows: list of int arrays (statement rows for the agent-day)
  U (n_stmt, d) unit statement vectors; lab: dict k -> (n_stmt,) cluster labels
  E: dict (day, i, j) -> # messages of j that i was exposed to (i <- j)
  ghat (d,), ghat_room: dict room -> (d,), ghat_agent: dict agent -> (d,) (optional), h: dict agent -> unit (d,)
  h_firstday: set of agents whose h comes from their first day in the unit (their pairs on that day are dropped)
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
from h01common import unit  # noqa: E402,F401  (sets thread caps before numpy)

import numpy as np  # noqa: E402
from scipy import special, stats  # noqa: E402


@dataclass
class Unit:
    name: str
    agents: np.ndarray
    day: np.ndarray
    room: np.ndarray
    V: np.ndarray
    nstmt: np.ndarray
    rows: list
    U: np.ndarray
    lab: dict
    E: dict
    ghat: np.ndarray
    h: dict
    ghat_room: dict = field(default_factory=dict)
    ghat_agent: dict = field(default_factory=dict)
    h_firstday: set = field(default_factory=set)
    labs: dict = field(default_factory=dict)       # agent -> lab name
    day_names: list = field(default_factory=list)


# ============================================================================ entropy (P1-P3)
def rarefied_counts(u: Unit, idx, k: int, M: int, R: int, rng, labels=None):
    """(R, len(idx), k) cluster counts from M statements drawn without replacement per agent-day (idx into agent-days)."""
    lab = u.lab[k] if labels is None else labels
    out = np.zeros((R, len(idx), k), np.float32)
    for a, i in enumerate(idx):
        rr = u.rows[i]
        for r in range(R):
            out[r, a] = np.bincount(lab[rng.choice(rr, M, replace=False)], minlength=k)
    return out


def full_counts(u: Unit, idx, k: int, labels=None):
    lab = u.lab[k] if labels is None else labels
    return np.stack([np.bincount(lab[u.rows[i]], minlength=k) for i in idx]).astype(np.float32)[None]


def ent(p, axis=-1):
    p = p / np.maximum(p.sum(axis, keepdims=True), 1e-12)
    with np.errstate(divide="ignore", invalid="ignore"):
        return -np.nansum(np.where(p > 0, p * np.log(p), 0.0), axis=axis)


def partition_entropy(counts, assign_mat, min_size=2):
    """counts (R, n, k); assign_mat (P, n, G) one-hot. Size-weighted mean over groups with >= min_size members of the
    group entropy (averaged over rarefaction draws). Returns (P,)."""
    gc = np.einsum("png,rnk->prgk", assign_mat, counts, optimize=True)        # (P, R, G, k)
    H = ent(gc).mean(1)                                                        # (P, G)
    sz = assign_mat.sum(1)                                                     # (P, G)
    w = np.where(sz >= min_size, sz, 0.0)
    return (H * w).sum(1) / np.maximum(w.sum(1), 1e-12)


def onehot(labels, G):
    m = np.zeros((len(labels), G), np.float32)
    m[np.arange(len(labels)), labels] = 1
    return m


def partition_test(counts, labels, n_perm, rng, min_size=2):
    """Observed partition vs random partitions with the same group sizes (agent labels permuted)."""
    labels = np.asarray(labels)
    _, lab_c = np.unique(labels, return_inverse=True)
    G = lab_c.max() + 1
    obs = partition_entropy(counts, onehot(lab_c, G)[None], min_size)[0]
    perms = np.stack([onehot(rng.permutation(lab_c), G) for _ in range(n_perm)])
    null = np.concatenate([partition_entropy(counts, perms[i:i + 200], min_size) for i in range(0, n_perm, 200)])
    return {"H_obs": float(obs), "H_null_mean": float(null.mean()), "dH": float(obs - null.mean()),
            "z": float((obs - null.mean()) / (null.std() + 1e-12)), "p": float((1 + (null <= obs).sum()) / (1 + n_perm))}


def js_distance(p, q):
    p = p / p.sum(-1, keepdims=True); q = q / q.sum(-1, keepdims=True); m = 0.5 * (p + q)
    with np.errstate(divide="ignore", invalid="ignore"):
        kl = lambda a, b: np.nansum(np.where(a > 0, a * np.log(a / b), 0.0), -1)  # noqa: E731
    return np.sqrt(np.clip(0.5 * kl(p, m) + 0.5 * kl(q, m), 0, None))


# ============================================================================ fields, pair-day table (P5-P8)
def field_basis(u: Unit, i: int, j: int, d: int, room_i=None, room_j=None, use_room=False, h=None):
    """Orthonormal basis of the field subspace for pair (i, j): g-hat, h_i, h_j [+ agent goals] [+ room goals]."""
    h = u.h if h is None else h
    cols = [u.ghat, h[i], h[j]]
    for a in (i, j):
        if a in u.ghat_agent:
            cols.append(u.ghat_agent[a])
    if use_room:
        for r in {room_i, room_j}:
            gr = u.ghat_room.get(r)
            if gr is not None and abs(gr @ u.ghat) < 0.98:
                cols.append(gr)
    return np.stack(cols, 1)


def pair_table(u: Unit, n_min=3, use_room=False, Vover=None, hover=None, rare=None):
    """Pair-day table. Vover: optional replacement agent-day vectors (rotation / shuffle nulls, rarefied draws: then
    shape (R, n_ad, d) and the residual cosine is averaged over draws). Returns dict of arrays."""
    V = u.V if Vover is None else Vover
    if V.ndim == 2:
        V = V[None]
    h = u.h if hover is None else hover
    T = int(u.day.max()) + 1
    out = {k: [] for k in ("i", "j", "day", "a", "phi", "Tg", "r", "rho", "Eij", "Eji", "ni", "nj", "same", "Eij_lag", "Eji_lag",
                           "xi", "yi")}
    first_day = {}
    for a in u.h_firstday:
        m = u.agents == a
        if m.any():
            first_day[a] = u.day[m].min()
    for t in range(T):
        idx = np.where((u.day == t) & (u.nstmt >= n_min))[0]
        idx = [x for x in idx if u.agents[x] in h and first_day.get(u.agents[x], -1) != t]
        if len(idx) < 2:
            continue
        P = [(x, y) for ai, x in enumerate(idx) for y in idx[ai + 1:]]
        Fs = [field_basis(u, u.agents[x], u.agents[y], u.ghat.shape[0], u.room[x], u.room[y], use_room, h) for x, y in P]
        Pr = np.zeros((len(P), u.ghat.shape[0], u.ghat.shape[0]))           # projector onto each pair's field subspace
        widths = np.array([f.shape[1] for f in Fs])
        for wdt in np.unique(widths):
            sel = np.where(widths == wdt)[0]
            Q, _ = np.linalg.qr(np.stack([Fs[s] for s in sel]))               # batched, (n_sel, d, wdt)
            Pr[sel] = Q @ np.swapaxes(Q, 1, 2)
        xs = np.array([p[0] for p in P]); ys = np.array([p[1] for p in P])
        vi = V[:, xs]; vj = V[:, ys]                                           # (R, P, d)
        fi = np.einsum("pde,rpe->rpd", Pr, vi); fj = np.einsum("pde,rpe->rpd", Pr, vj)
        ri = vi - fi; rj = vj - fj
        a_ = (vi * vj).sum(-1); phi = (fi * fj).sum(-1)
        rho = (ri * rj).sum(-1)
        rc = rho / np.maximum(np.linalg.norm(ri, axis=-1) * np.linalg.norm(rj, axis=-1), 1e-9)
        g = u.ghat
        Tg = (vi @ g) * (vj @ g)
        ai_ = u.agents[xs]; aj_ = u.agents[ys]
        lo = np.minimum(ai_, aj_); hi = np.maximum(ai_, aj_)
        swap = ai_ > aj_
        out["xi"].append(np.where(swap, ys, xs)); out["yi"].append(np.where(swap, xs, ys))
        out["i"].append(lo); out["j"].append(hi); out["day"].append(np.full(len(P), t))
        out["a"].append(a_.mean(0)); out["phi"].append(phi.mean(0)); out["Tg"].append(Tg.mean(0))
        out["r"].append(rc.mean(0)); out["rho"].append(rho.mean(0))
        out["Eij"].append(np.array([u.E.get((t, l, m_), 0) for l, m_ in zip(lo, hi)]))   # lo saw hi
        out["Eji"].append(np.array([u.E.get((t, m_, l), 0) for l, m_ in zip(lo, hi)]))   # hi saw lo
        out["Eij_lag"].append(np.array([u.E.get((t - 1, l, m_), 0) if t > 0 else -1 for l, m_ in zip(lo, hi)]))
        out["Eji_lag"].append(np.array([u.E.get((t - 1, m_, l), 0) if t > 0 else -1 for l, m_ in zip(lo, hi)]))
        nmap = dict(zip(u.agents[idx], u.nstmt[idx])); rmap = dict(zip(u.agents[idx], u.room[idx]))
        out["ni"].append(np.array([nmap[l] for l in lo])); out["nj"].append(np.array([nmap[m_] for m_ in hi]))
        out["same"].append(np.array([(rmap[l] == rmap[m_]) and rmap[l] >= 0 for l, m_ in zip(lo, hi)]))
    if not out["i"]:
        return None
    res = {k: np.concatenate(v) for k, v in out.items()}
    res["i"] = res["i"].astype(np.int64); res["j"] = res["j"].astype(np.int64)
    return res


def r2_field(pt):
    """P5: R^2 of a_ij on [T_g, phi - T_g] (OLS with intercept)."""
    X = np.column_stack([np.ones(len(pt["a"])), pt["Tg"], pt["phi"] - pt["Tg"]])
    b, *_ = np.linalg.lstsq(X, pt["a"], rcond=None)
    e = pt["a"] - X @ b
    return float(1 - e.var() / pt["a"].var())


def demean2(M, pid, did, tol=1e-11, max_iter=1000):
    """Two-way within transformation (pair and day fixed effects) by alternating projections."""
    M = np.array(M, float, copy=True)
    if M.ndim == 1:
        M = M[:, None]
    npair, nday = pid.max() + 1, did.max() + 1
    cp = np.bincount(pid, minlength=npair)[:, None]; cd = np.bincount(did, minlength=nday)[:, None]
    for _ in range(max_iter):
        gp = np.zeros((npair, M.shape[1])); np.add.at(gp, pid, M); M -= (gp / cp)[pid]
        gd = np.zeros((nday, M.shape[1])); np.add.at(gd, did, M); step = (gd / cd)[did]; M -= step
        if np.abs(step).max() < tol:
            break
    return M


def fe_slope(pt, xcols, ycol="r", mask=None, covars=(), y_override=None):
    """y = pair FE + day FE + b . x (+ covariates). FWL with a two-way within transformation; pair-clustered SEs
    (CR1, t with G-1 df). Returns b, se, p and the residualized design for fast null recomputation."""
    m = np.ones(len(pt["a"]), bool) if mask is None else mask
    pid = np.unique(pt["i"][m] * 1000 + pt["j"][m], return_inverse=True)[1]
    did = np.unique(pt["day"][m], return_inverse=True)[1]
    X = np.column_stack([np.asarray(pt[c] if isinstance(c, str) else c, float)[m] for c in xcols])
    y = np.asarray(pt[ycol] if y_override is None else y_override, float)[m]
    Xt = demean2(X, pid, did)
    yt = demean2(y, pid, did)[:, 0]
    ncov = 0
    if covars:
        C = demean2(np.column_stack([np.asarray(pt[c] if isinstance(c, str) else c, float)[m] for c in covars]), pid, did)
        ncov = C.shape[1]
        P = C @ np.linalg.pinv(C)
        Xt = Xt - P @ Xt; yt = yt - P @ yt
    XtX = Xt.T @ Xt
    if np.linalg.matrix_rank(XtX) < XtX.shape[0] or np.diag(XtX).min() < 1e-9:
        return None
    XtXi = np.linalg.inv(XtX)
    b = XtXi @ Xt.T @ yt
    e = yt - Xt @ b
    G = pid.max() + 1; n = len(y); kdf = G + did.max() + ncov + X.shape[1]
    meat = np.zeros((X.shape[1], X.shape[1]))
    S = np.zeros((G, X.shape[1])); np.add.at(S, pid, Xt * e[:, None])
    meat = S.T @ S
    cr = G / max(G - 1, 1) * (n - 1) / max(n - kdf, 1)
    V = cr * XtXi @ meat @ XtXi
    se = np.sqrt(np.clip(np.diag(V), 1e-30, None))
    z = b / se
    p = 2 * stats.t.sf(np.abs(z), df=max(G - 1, 1))
    return {"b": b, "se": se, "p": p, "n": int(n), "n_pairs": int(G), "Xt": Xt, "XtXi": XtXi, "mask": m}


def fe_slope_fast(fit, y):
    """Slope for a new outcome vector with the same design (null draws)."""
    return fit["XtXi"] @ fit["Xt"].T @ y[fit["mask"]].astype(float)


def random_effects(b, se):
    """DerSimonian-Laird random-effects summary."""
    b = np.asarray(b, float); se = np.asarray(se, float)
    w = 1 / se ** 2
    bf = (w * b).sum() / w.sum()
    Q = (w * (b - bf) ** 2).sum(); k = len(b)
    tau2 = max(0.0, (Q - (k - 1)) / (w.sum() - (w ** 2).sum() / w.sum())) if k > 1 else 0.0
    ws = 1 / (se ** 2 + tau2)
    mu = (ws * b).sum() / ws.sum(); s = np.sqrt(1 / ws.sum())
    I2 = max(0.0, (Q - (k - 1)) / Q) if Q > 0 else 0.0
    return {"mu": float(mu), "se": float(s), "z": float(mu / s), "p_two": float(2 * stats.norm.sf(abs(mu / s))),
            "p_one": float(stats.norm.sf(mu / s)), "tau2": float(tau2), "I2": float(I2), "Q": float(Q), "k": int(k)}


def random_rotation(d, rng):
    A = rng.standard_normal((d, d))
    Q, R = np.linalg.qr(A)
    return Q * np.sign(np.diag(R))


def rotate_agents(u: Unit, rng, extra=None):
    """Per-agent random rotation of every agent-day vector and of the agent's field h_i (keeps each trajectory,
    destroys cross-alignment and alignment with g-hat). extra: optional (R, n_ad, d) stacks rotated the same way."""
    d = u.V.shape[1]
    V = u.V.copy(); h = dict(u.h); Ex = None if extra is None else extra.copy()
    for a in np.unique(u.agents):
        Rm = random_rotation(d, rng)
        m = u.agents == a
        V[m] = V[m] @ Rm.T
        if Ex is not None:
            Ex[:, m] = Ex[:, m] @ Rm.T
        if a in h:
            h[a] = Rm @ h[a]
    return V, h, Ex


def shuffle_days(u: Unit, rng, extra=None, n_min=1):
    """Within-unit day shuffle per agent: each agent's agent-day vectors are permuted across its own days (only among
    agent-days with >= n_min statements, so the set of usable agent-days is unchanged)."""
    V = u.V.copy(); Ex = None if extra is None else extra.copy()
    for a in np.unique(u.agents):
        ix = np.where((u.agents == a) & (u.nstmt >= n_min))[0]
        p = rng.permutation(ix)
        V[ix] = u.V[p]
        if Ex is not None:
            Ex[:, ix] = extra[:, p]
    return V, Ex


def permute_unit_days(u: Unit, rng):
    """Copy of the unit with each agent's day labels permuted among its own days (day-shuffle null for P9)."""
    day = u.day.copy()
    for a in np.unique(u.agents):
        ix = np.where(u.agents == a)[0]
        day[ix] = rng.permutation(u.day[ix])
    return Unit(**{**u.__dict__, "day": day})


def rarefied_vectors(u: Unit, M: int, R: int, rng):
    """(R, n_ad, d) agent-day vectors from M statements each (agent-days with < M statements get NaN)."""
    out = np.full((R, len(u.V), u.V.shape[1]), np.nan)
    for i, rr in enumerate(u.rows):
        if len(rr) < M:
            continue
        for r in range(R):
            out[r, i] = unit(u.U[rng.choice(rr, M, replace=False)].mean(0))
    return out


def split_half_vectors(u: Unit, rng):
    A = np.full_like(u.V, np.nan); B = np.full_like(u.V, np.nan)
    for i, rr in enumerate(u.rows):
        if len(rr) < 2:
            continue
        p = rng.permutation(rr); h = len(p) // 2
        A[i] = unit(u.U[p[:h]].mean(0)); B[i] = unit(u.U[p[h:]].mean(0))
    return A, B


# ============================================================================ mean-field O(n) (P9)
def A_n(x, n):
    x = np.maximum(np.asarray(x, float), 1e-12)
    return special.ive(n / 2, x) / special.ive(n / 2 - 1, x)


def A_n_prime(x, n):
    a = A_n(x, n)
    return 1 - a ** 2 - (n - 1) * a / np.maximum(x, 1e-12)


def A_n_inv(m, n):
    m = float(np.clip(m, 1e-9, 0.999))
    lo, hi = 1e-9, 1e4
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if A_n(mid, n) < m:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def mf_fit(u: Unit, rng, n_split=5, Vover=None):
    """Mean-field O(n) fit for one unit: m along g-hat and the collective fluctuation enhancement R of within-agent
    day-to-day deviations (noise-corrected with split halves). R = 1 + (N-1) rho; MF: R = sum chi_k/(1 - bJ chi_k) /
    sum chi_k with chi = A(x)/x (n-1 transverse) and A'(x) (longitudinal); x = A^-1(m); bh = x - bJ m."""
    V = u.V if Vover is None else Vover
    n = V.shape[1]
    ags = np.unique(u.agents)
    T = int(u.day.max()) + 1
    keep = [a for a in ags if (u.agents == a).sum() >= 2]
    if len(keep) < 3 or T < 2:
        return None
    # deviations from each agent's own unit mean
    dev = {}
    for a in keep:
        ix = np.where(u.agents == a)[0]
        dev[a] = (u.day[ix], V[ix] - V[ix].mean(0), ix)
    # signal variance per agent from split halves (averaged over splits)
    S = {a: 0.0 for a in keep}
    for _ in range(n_split):
        A, B = split_half_vectors(u, rng) if Vover is None else (V, V)
        for a in keep:
            ix = dev[a][2]
            ok = ~np.isnan(A[ix]).any(1) & ~np.isnan(B[ix]).any(1)
            if ok.sum() < 2:
                S[a] += np.nan; continue
            dA = A[ix][ok] - A[ix][ok].mean(0); dB = B[ix][ok] - B[ix][ok].mean(0)
            S[a] += (dA * dB).sum(1).mean() * ok.sum() / (ok.sum() - 1)
    S = {a: max(S[a] / n_split, 1e-6) for a in keep if np.isfinite(S[a])}
    keep = [a for a in keep if a in S]
    num = den = 0.0
    for ai, a in enumerate(keep):
        da, Xa, _ = dev[a]
        for b in keep[ai + 1:]:
            db, Xb, _ = dev[b]
            common, ia, ib = np.intersect1d(da, db, return_indices=True)
            if len(common) < 2:
                continue
            c = (Xa[ia] * Xb[ib]).sum(1).mean() * T / max(T - 1, 1)
            num += c; den += np.sqrt(S[a] * S[b])
    if den == 0:
        return None
    rho = num / den
    Nbar = np.mean([len(np.unique(u.agents[u.day == t])) for t in range(T)])
    R = 1 + (Nbar - 1) * rho
    m = float(np.mean(V @ u.ghat))
    x = A_n_inv(abs(m), n)
    chi_t = A_n(x, n) / x; chi_l = A_n_prime(x, n)
    chis = np.array([chi_l] + [chi_t] * (n - 1))
    if R <= 1:
        bJ = (1 - 1 / R) / chis.mean() if R > 0 else -np.inf
    else:
        lo, hi = 0.0, 1 / chis.max() * (1 - 1e-9)
        f = lambda bj: (chis / (1 - bj * chis)).sum() / chis.sum() - R  # noqa: E731
        if f(hi) < 0:
            bJ = hi
        else:
            for _ in range(200):
                mid = 0.5 * (lo + hi)
                if f(mid) < 0:
                    lo = mid
                else:
                    hi = mid
            bJ = 0.5 * (lo + hi)
    bh = x - bJ * abs(m)
    return {"m_g": m, "rho": float(rho), "R": float(R), "Nbar": float(Nbar), "bJ": float(bJ), "bJ_over_n": float(bJ / n),
            "bh": float(bh), "x": float(x), "coupling_share": float(bJ * abs(m) / x) if x > 0 else np.nan, "n": n}


def fluct_rho_rooms(u: Unit, rng, n_split=5):
    """Noise-corrected correlation of within-agent day-to-day deviations, split by same-room vs cross-room pairs
    (room = agent's modal room in the unit). Cross-room pairs cannot see each other's chat, so their co-fluctuation
    measures a common (field-like) daily drive; within - cross is the part attributable to the room channel."""
    ags = [a for a in np.unique(u.agents) if (u.agents == a).sum() >= 2]
    T = int(u.day.max()) + 1
    room = {}
    for a in ags:
        m = (u.agents == a) & (u.room >= 0)
        room[a] = int(np.bincount(u.room[m]).argmax()) if m.any() else -1
    dev = {a: (u.day[u.agents == a], u.V[u.agents == a] - u.V[u.agents == a].mean(0), np.where(u.agents == a)[0]) for a in ags}
    S = {a: 0.0 for a in ags}
    for _ in range(n_split):
        A, B = split_half_vectors(u, rng)
        for a in ags:
            ix = dev[a][2]; ok = ~np.isnan(A[ix]).any(1) & ~np.isnan(B[ix]).any(1)
            if ok.sum() < 2:
                S[a] = np.nan; continue
            dA = A[ix][ok] - A[ix][ok].mean(0); dB = B[ix][ok] - B[ix][ok].mean(0)
            S[a] += (dA * dB).sum(1).mean() * ok.sum() / (ok.sum() - 1) / n_split
    num = {True: 0.0, False: 0.0}; den = {True: 0.0, False: 0.0}; cnt = {True: 0, False: 0}
    for ai, a in enumerate(ags):
        for b in ags[ai + 1:]:
            if not (np.isfinite(S[a]) and np.isfinite(S[b])) or room[a] < 0 or room[b] < 0:
                continue
            da, Xa, _ = dev[a]; db, Xb, _ = dev[b]
            common, ia, ib = np.intersect1d(da, db, return_indices=True)
            if len(common) < 2:
                continue
            same = room[a] == room[b]
            num[same] += (Xa[ia] * Xb[ib]).sum(1).mean() * T / max(T - 1, 1)
            den[same] += np.sqrt(max(S[a], 1e-6) * max(S[b], 1e-6)); cnt[same] += 1
    return {"rho_within": float(num[True] / den[True]) if den[True] else None, "rho_cross": float(num[False] / den[False]) if den[False] else None,
            "n_within_pairs": cnt[True], "n_cross_pairs": cnt[False]}


# ============================================================================ vMF sampling (synthetic)
def sample_vmf(mu, kappa, rng):
    """Wood (1994). mu (m, p) unit rows, kappa (m,) >= 0. Returns (m, p) unit samples."""
    mu = np.atleast_2d(mu); m, p = mu.shape
    kappa = np.broadcast_to(np.asarray(kappa, float), (m,)).copy()
    w = np.empty(m)
    small = kappa < 1e-8
    if small.any():
        x = rng.standard_normal((small.sum(), p)); x /= np.linalg.norm(x, axis=1, keepdims=True)
        w[small] = (x * mu[small]).sum(1)
    big = ~small
    if big.any():
        k = kappa[big]
        b = (-2 * k + np.sqrt(4 * k ** 2 + (p - 1) ** 2)) / (p - 1)
        x0 = (1 - b) / (1 + b)
        c = k * x0 + (p - 1) * np.log(1 - x0 ** 2)
        wb = np.empty(len(k)); todo = np.arange(len(k))
        while len(todo):
            z = rng.beta((p - 1) / 2, (p - 1) / 2, len(todo))
            ww = (1 - (1 + b[todo]) * z) / (1 - (1 - b[todo]) * z)
            u_ = rng.random(len(todo))
            acc = k[todo] * ww + (p - 1) * np.log(1 - x0[todo] * ww) - c[todo] >= np.log(u_)
            wb[todo[acc]] = ww[acc]; todo = todo[~acc]
        w[big] = wb
    v = rng.standard_normal((m, p))
    v -= (v * mu).sum(1, keepdims=True) * mu
    v /= np.linalg.norm(v, axis=1, keepdims=True)
    return w[:, None] * mu + np.sqrt(np.clip(1 - w ** 2, 0, None))[:, None] * v


def kappa_for_A(a, n):
    lo, hi = 1e-6, 1e4
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        if A_n(mid, n) < a:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)
