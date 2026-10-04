"""H123 library: scheduler audit (O1), event-time spins, cross-agent EP at lag L (O3), kinetic Ising fit and the
symmetric-J sweep simulation (O4). Estimator: infra/shared/ep_newton.py corrected held-out Newton bound.
No project data is read at import time.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
import ep_newton as EN  # noqa: E402

OUT = ROOT / "data/processed/H123-regime1-turn-sweep"
LAGS = (1, 2, 4)
EDGE = 0.10


def load_steps(unit: str) -> pl.DataFrame:
    return pl.read_parquet(OUT / "steps" / f"{unit}.parquet")


# ============================================================================ O1 scheduler audit
def _entropy(p):
    p = p[p > 0]
    return float(-(p * np.log(p)).sum())


def order_stats(seqs: list[np.ndarray], n_codes: int) -> dict:
    """seqs: per-day actor index arrays (0..n_codes-1). Pooled over days."""
    T = np.zeros((n_codes, n_codes))
    rep = 0
    ntr = 0
    r0_num = 0.0
    cv_num = 0.0
    cv_den = 0.0
    cvref_num = 0.0
    for a in seqs:
        if len(a) < 3:
            continue
        np.add.at(T, (a[:-1], a[1:]), 1)
        rep += int((a[:-1] == a[1:]).sum())
        ntr += len(a) - 1
        p = np.bincount(a, minlength=n_codes) / len(a)
        r0_num += (p ** 2).sum() * (len(a) - 1)
        for i in np.unique(a):
            idx = np.flatnonzero(a == i)
            if len(idx) < 3:
                continue
            g = np.diff(idx) - 1
            if g.mean() <= 0:
                cv = 0.0
            else:
                cv = g.std() / g.mean()
            w = len(g)
            cv_num += cv * w
            cv_den += w
            cvref_num += np.sqrt(max(1 - p[i], 0)) * w
    r = rep / max(ntr, 1)
    r0 = r0_num / max(ntr, 1)
    pn = T.sum(0) / T.sum()
    Hn = _entropy(pn)
    rows = T.sum(1)
    Hc = sum(rows[i] / T.sum() * _entropy(T[i] / rows[i]) for i in range(n_codes) if rows[i] > 0)
    eta = 1 - Hc / Hn if Hn > 0 else np.nan
    off = T.copy()
    np.fill_diagonal(off, 0)
    q = off.max(1).sum() / max(off.sum(), 1)
    return {"r": r, "r0": r0, "r_ratio": r / r0 if r0 > 0 else np.nan, "cv_gap": cv_num / max(cv_den, 1),
            "cv_ref": cvref_num / max(cv_den, 1), "eta": eta, "q_succ": q, "n_tr": ntr}


def concurrency(day: pl.DataFrame) -> float:
    """Share of steps whose t_call falls inside another agent's in-flight call [t_call, t_log)."""
    t0 = day["t_call"].dt.epoch("us").to_numpy().astype(np.float64)
    t1 = day["t_log"].dt.epoch("us").to_numpy().astype(np.float64)
    t1 = np.where(np.isnan(t1) | (t1 < t0), t0, t1)
    ag = day["agent"].to_numpy()
    o = np.argsort(t0, kind="stable")
    t0, t1, ag = t0[o], t1[o], ag[o]
    best = (-np.inf, -1)   # (max t_log, agent)
    second = -np.inf       # max t_log among agents != best agent
    hit = 0
    for k in range(len(t0)):
        other = best[0] if best[1] != ag[k] else second
        if other > t0[k]:
            hit += 1
        if t1[k] > best[0]:
            if best[1] != ag[k]:
                second = best[0]
            best = (t1[k], ag[k])
        elif ag[k] != best[1] and t1[k] > second:
            second = t1[k]
    return hit / max(len(t0), 1)


def own_interval_cv(day: pl.DataFrame) -> float:
    """Median over agents of the CV of the agent's own inter-call times (s)."""
    out = []
    for _, g in day.group_by("agent"):
        t = np.sort(g["t_call"].dt.epoch("us").to_numpy() / 1e6)
        if len(t) >= 5:
            d = np.diff(t)
            if d.mean() > 0:
                out.append(d.std() / d.mean())
    return float(np.median(out)) if out else np.nan


def name_lift(S: pl.DataFrame, rng=None, n_null: int = 0, boot_days=None) -> dict:
    """Mantel-Haenszel rate ratio P(a(t+1)=j | j named before t+1) / P(a(t+1)=j | not named), strata = agent j.
    Uses the named_mask attached to step t+1 (latest agent message before its t_call, <= 10 min)."""
    def mh(df, masks):
        num = den = 0.0
        agents = np.unique(df["agent"].to_numpy())
        a_next = df["agent"].to_numpy()
        for j in agents:
            X = ((masks >> np.int64(j)) & 1).astype(bool)
            Y = a_next == j
            n1, n0 = X.sum(), (~X).sum()
            if n1 == 0 or n0 == 0:
                continue
            a = (X & Y).sum()
            b = (~X & Y).sum()
            n = n1 + n0
            num += a * n0 / n
            den += b * n1 / n
        return num / den if den > 0 else np.nan
    masks = S["named_mask"].to_numpy().astype(np.int64)
    obs = mh(S, masks)
    res = {"L_name": obs}
    if n_null and rng is not None:
        null = []
        days = S["day"].to_numpy()
        for _ in range(n_null):
            m2 = masks.copy()
            for d in np.unique(days):
                ix = np.flatnonzero(days == d)
                m2[ix] = m2[rng.permutation(ix)]
            null.append(mh(S, m2))
        res["null_q95"] = float(np.nanquantile(null, 0.95))
        res["null_med"] = float(np.nanmedian(null))
        res["p"] = float((1 + np.sum(np.array(null) >= obs)) / (n_null + 1))
    if boot_days and rng is not None:
        dl = S["day"].unique().to_list()
        bs = []
        for _ in range(boot_days):
            pick = rng.choice(dl, len(dl), replace=True)
            parts = [S.filter(pl.col("day") == d) for d in pick]
            B = pl.concat(parts)
            bs.append(mh(B, B["named_mask"].to_numpy().astype(np.int64)))
        res["ci"] = [float(np.nanquantile(bs, 0.025)), float(np.nanquantile(bs, 0.975))]
    return res


def audit_unit(S: pl.DataFrame, subset: str = "all", n_shuffle: int = 50, seed: int = 0) -> dict:
    """O1 statistics for one unit. subset 'all' or 'chat' (ctx_mode chat calls only)."""
    rng = np.random.default_rng(seed)
    X = S if subset == "all" else S.filter(~pl.col("cu"))
    codes = np.unique(X["agent"].to_numpy())
    cmap = {c: i for i, c in enumerate(codes)}
    seqs, kap, ocv = [], [], []
    for day in sorted(X["day"].unique().to_list()):
        d = X.filter(pl.col("day") == day).sort("t_call", "step")
        if d.height < 10:
            continue
        seqs.append(np.array([cmap[a] for a in d["agent"].to_list()]))
        if subset == "all":
            kap.append(concurrency(d))
        ocv.append(own_interval_cv(d))
    if not seqs:
        return {}
    st = order_stats(seqs, len(codes))
    sh = [order_stats([rng.permutation(a) for a in seqs], len(codes)) for _ in range(n_shuffle)]
    for k in ("r", "cv_gap", "eta", "q_succ"):
        v = np.array([x[k] for x in sh])
        st[f"{k}_shuf"] = float(np.mean(v))
        st[f"{k}_shuf_q"] = [float(np.quantile(v, 0.025)), float(np.quantile(v, 0.975))]
    st["kappa_par"] = float(np.mean(kap)) if kap else np.nan
    st["own_cv"] = float(np.nanmedian(ocv))
    st["n_agents"] = len(codes)
    st["n_days"] = len(seqs)
    st["n_steps"] = int(sum(len(a) for a in seqs))
    return st


def classify(st: dict, lname: dict | None) -> str:
    """Pre-registered rule (card O1)."""
    if not st:
        return "n/a"
    eta, cv, rr = st["eta"], st["cv_gap"], st["r_ratio"]
    L = lname.get("L_name") if lname else np.nan
    Lci = lname.get("ci") if lname else None
    if eta >= 0.5 and cv <= 0.5 and rr <= 0.5:
        return "sweep"
    if Lci is not None and L >= 1.5 and Lci[0] > 1.2:
        return "state-dependent"
    cv_ok = abs(cv / st["cv_gap_shuf"] - 1) <= 0.2 if st["cv_gap_shuf"] > 0 else False
    if eta <= 0.1 and cv_ok and abs(rr - 1) <= 0.2 and (Lci is None or (Lci[0] >= 0.8 and Lci[1] <= 1.25)):
        return "random sequential"
    if st.get("kappa_par", 0) >= 0.3:
        return "self-clocked asynchronous"
    return "mixed"


# ============================================================================ event-time spins and EP
def spins(S: pl.DataFrame, channel: str = "talk", edge: float = EDGE):
    """Per day: (actor index array, spin matrix T x N in {-1,+1}) over warm steps, edges cut.
    Returns list of (day, actors, Sp) and agent codes."""
    codes = np.unique(S["agent"].to_numpy())
    cmap = {c: i for i, c in enumerate(codes)}
    N = len(codes)
    out = []
    for day in sorted(S["day"].unique().to_list()):
        d = S.filter(pl.col("day") == day).sort("step")
        a = np.array([cmap[x] for x in d["agent"].to_list()])
        v = (d["talk"] if channel == "talk" else d["cu"]).to_numpy().astype(bool)
        warm = d["warm"].to_numpy()
        Sp = np.zeros((len(a), N), dtype=np.int8)
        cur = np.zeros(N, dtype=np.int8)
        for t in range(len(a)):
            cur[a[t]] = 1 if v[t] else -1
            Sp[t] = cur
        keep = warm & np.all(Sp != 0, axis=1)
        ix = np.flatnonzero(keep)
        if len(ix) < 50:
            continue
        lo, hi = int(len(ix) * edge), int(len(ix) * (1 - edge))
        ix = ix[lo:hi]
        out.append((day, a[ix], Sp[ix]))
    return out, codes


def observables(days_data, N: int, lags=LAGS):
    """Build G (rows = steps t with t + max(lags) < T, per day), day labels, and column families.
    single: per agent 2 own-sequence 3-step patterns at the step of the agent's own update.
    cross_L: s_i(t+L)s_j(t) - s_i(t)s_j(t+L), i<j."""
    Lmax = max(lags)
    iu, ju = np.triu_indices(N, 1)
    rows, dl = [], []
    for di, (day, a, Sp) in enumerate(days_data):
        T = len(a)
        if T <= Lmax + 3:
            continue
        S = Sp.astype(np.float64)
        single = np.zeros((T, 2 * N))
        for i in range(N):
            own = np.flatnonzero(a == i)
            if len(own) < 3:
                continue
            x = S[own, i]
            k = np.arange(2, len(own))
            p0, p1, p2 = x[k - 2], x[k - 1], x[k]
            u1 = ((p0 < 0) & (p1 < 0) & (p2 > 0)).astype(float) - ((p0 > 0) & (p1 < 0) & (p2 < 0))
            u2 = ((p0 < 0) & (p1 > 0) & (p2 > 0)).astype(float) - ((p0 > 0) & (p1 > 0) & (p2 < 0))
            single[own[k], 2 * i] = u1
            single[own[k], 2 * i + 1] = u2
        nT = T - Lmax
        cols = [single[:nT]]
        for L in lags:
            A, B = S[L:L + nT], S[:nT]
            cols.append(A[:, iu] * B[:, ju] - B[:, iu] * A[:, ju])
        rows.append(np.hstack(cols))
        dl.append(np.full(nT, di))
    G = np.vstack(rows)
    days = np.concatenate(dl)
    npair = len(iu)
    fam = {"single": np.arange(2 * N)}
    off = 2 * N
    for L in lags:
        fam[f"cross{L}"] = np.arange(off, off + npair)
        off += npair
    block = np.zeros(G.shape[1], dtype=int)
    for b, (nm, cols) in enumerate(fam.items()):
        block[cols] = b
    return G, days, fam, block


def ep_cross(days_data, N: int, lags=LAGS) -> dict:
    """sigma_x(L) = Sigma(single u cross_L) - Sigma(single), held-out Newton, day folds (k = min(5, days))."""
    G, days, fam, block = observables(days_data, N, lags)
    subsets = {"single": fam["single"]}
    for L in lags:
        subsets[f"sc{L}"] = np.concatenate([fam["single"], fam[f"cross{L}"]])
    sig, folds = EN.newton_subsets_heldout(G, days, subsets, block=block, return_folds=True)
    out = {"single": sig["single"], "T": int(len(G)), "d": int(G.shape[1]), "n_days": int(len(np.unique(days)))}
    for L in lags:
        dfold = np.array(folds[f"sc{L}"]) - np.array(folds["single"])
        out[f"x{L}"] = sig[f"sc{L}"] - sig["single"]
        out[f"x{L}_se"] = float(dfold.std(ddof=1) / np.sqrt(len(dfold))) if len(dfold) > 1 else np.nan
    return out


def block_flip(days_data, rng, block: int = 30):
    """Per agent and 30-step block, reverse the agent's spin path with probability 1/2 (floor null)."""
    out = []
    for day, a, Sp in days_data:
        S2 = Sp.copy()
        T, N = S2.shape
        for b0 in range(0, T, block):
            b1 = min(T, b0 + block)
            flip = rng.random(N) < 0.5
            for i in np.flatnonzero(flip):
                S2[b0:b1, i] = S2[b0:b1, i][::-1]
        out.append((day, a, S2))
    return out


# ============================================================================ kinetic Ising: fit and simulate
def logistic_fit(X, y01, l2=1e-3, iters=50):
    """Logistic regression with intercept (Newton). Returns (b0, b). X n x p, y in {0,1}."""
    n, p = X.shape
    Z = np.hstack([np.ones((n, 1)), X])
    w = np.zeros(p + 1)
    R = l2 * n * np.eye(p + 1)
    R[0, 0] = 0
    for _ in range(iters):
        eta = Z @ w
        mu = 1 / (1 + np.exp(-eta))
        g = Z.T @ (y01 - mu) - R @ w
        W = mu * (1 - mu)
        H = (Z * W[:, None]).T @ Z + R
        step = np.linalg.solve(H, g)
        w += step
        if np.max(np.abs(step)) < 1e-8:
            break
    return w[0], w[1:]


def fit_heatbath(days_data, N: int, l2=1e-3):
    """Heat-bath kinetic Ising in event time: at a's step, P(s_a=+1) = sigmoid(2(h_a + sum_{j!=a} J_aj s_j)),
    s_j = others' spins just before the step. Returns h (N), J (N x N, zero diagonal) in the +-1 convention."""
    h = np.zeros(N)
    J = np.zeros((N, N))
    Xs = {i: [] for i in range(N)}
    ys = {i: [] for i in range(N)}
    for day, a, Sp in days_data:
        prev = np.vstack([Sp[:1], Sp[:-1]]).astype(float)
        for i in range(N):
            ix = np.flatnonzero(a == i)
            ix = ix[ix > 0]
            if len(ix) == 0:
                continue
            Xs[i].append(np.delete(prev[ix], i, axis=1))
            ys[i].append((Sp[ix, i] > 0).astype(float))
    for i in range(N):
        if not Xs[i]:
            continue
        X = np.vstack(Xs[i])
        y = np.concatenate(ys[i])
        if y.min() == y.max():
            h[i] = 3.0 if y[0] > 0 else -3.0
            continue
        b0, b = logistic_fit(X, y, l2=l2)
        h[i] = b0 / 2
        J[i, np.arange(N) != i] = b / 2
    return h, J


def simulate(actor_days, h, J, R: int, rng, shuffle: bool = False):
    """Heat-bath updates along the given per-day actor sequences, R replicates in parallel.
    Returns list over replicates of days_data [(day, actors, spins)]."""
    N = len(h)
    reps = [[] for _ in range(R)]
    p0 = 1 / (1 + np.exp(-2 * h))
    for day, a in actor_days:
        a = rng.permutation(a) if shuffle else a
        burn = min(len(a), 20 * N)
        seq = np.concatenate([a[:burn], a])          # burn-in on the day's own opening order
        T = len(seq)
        cur = np.where(rng.random((R, N)) < p0, 1.0, -1.0)
        out = np.empty((T, R, N), dtype=np.int8)
        u = rng.random((T, R))
        for t in range(T):
            i = seq[t]
            H = h[i] + cur @ J[i]          # J[i, i] = 0
            p = 1 / (1 + np.exp(-2 * H))
            cur[:, i] = np.where(u[t] < p, 1.0, -1.0)
            out[t] = cur
        out = out[burn:]
        for r in range(R):
            reps[r].append((day, a, out[:, r, :]))
    return reps


def sweep_predictions(days_data, N: int, R: int = 20, seed: int = 0, lags=LAGS, J_override=None, h_override=None):
    """sigma_sweep (symmetric J, real order), sigma_rand (symmetric J, shuffled order), sigma_full (fitted J, real
    order); each the mean (and sd) over R replicates of the same held-out estimator."""
    rng = np.random.default_rng(seed)
    if J_override is None:
        h, J = fit_heatbath(days_data, N)
    else:
        h, J = h_override, J_override
    Js = (J + J.T) / 2
    actor_days = [(d, a) for d, a, _ in days_data]
    res = {"h": h.tolist(), "J": J.tolist(), "rms_Js": float(np.sqrt(np.mean(Js[~np.eye(N, dtype=bool)] ** 2))),
           "rms_Ja": float(np.sqrt(np.mean(((J - J.T) / 2)[~np.eye(N, dtype=bool)] ** 2)))}
    for nm, JJ, sh in (("sweep", Js, False), ("rand", Js, True), ("full", J, False)):
        sims = simulate(actor_days, h, JJ, R, rng, shuffle=sh)
        vals = [ep_cross(s, N, lags) for s in sims]
        for L in lags:
            v = np.array([x[f"x{L}"] for x in vals])
            res[f"{nm}_x{L}"] = float(np.mean(v))
            res[f"{nm}_x{L}_sd"] = float(np.std(v, ddof=1))
            res[f"{nm}_x{L}_q95"] = float(np.quantile(v, 0.95))
    return res
