"""H98 estimators: random-field decomposition (R), mean-field gain (b), overlap distribution P(q) with the per-agent
circular day-shift null, H22 content co-movement J^c, niche regression and mediation gap, stance slope, role share.

All estimators take plain arrays so the synthetic worlds (synthetic.py) and the real units (run_units.py) share code.
Conventions: states are float32 (n, 32); `agent`, `day`, `win`, `room` are int arrays aligned with the rows.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data/processed/H98-random-field-51"
VARS = ("style_resid_period", "white32")
MODELS = ("bge_small", "gte_modernbert")


def unit(x: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(x, axis=-1, keepdims=True)
    return x / np.where(n > 0, n, 1)


# ------------------------------------------------------------------------------------------------ loading
def load_unit(u: str, var: str = "style_resid_period", model: str = "bge_small", root: Path = DATA) -> dict:
    d = root / u
    ad = pl.read_parquet(d / "agent_day.parquet")
    hv = pl.read_parquet(d / "halves.parquet")
    wn = pl.read_parquet(d / "win.parquet")
    out = {"unit": u, "ad": ad, "S": unit(np.load(d / f"S_{var}_{model}.npy")),
           "hv": hv, "H1": unit(np.load(d / f"H1_{var}_{model}.npy")), "H2": unit(np.load(d / f"H2_{var}_{model}.npy")),
           "wn": wn, "X": unit(np.load(d / f"X_{var}_{model}.npy")), "pairs": pl.read_parquet(d / "pairs.parquet")}
    if (d / "roles.parquet").exists():
        out["roles"] = pl.read_parquet(d / "roles.parquet")
    return out


def role_table(model: str = "bge_small", root: Path = DATA) -> dict:
    r = pl.read_parquet(root / "roles.parquet")
    V = np.load(root / f"roles_{model}.npy")
    return {(a, ro): V[k] for k, (a, ro) in enumerate(zip(r["agent"].to_list(), r["role"].to_list()))}


# ------------------------------------------------------------------------------------------------ O1: R
def day_field_replace(S: np.ndarray, day: np.ndarray) -> np.ndarray:
    """s'_id = s_id - m_d + mean_d m_d (removes the day field without changing the unit mean)."""
    days = np.unique(day)
    M = np.stack([S[day == d].mean(0) for d in days])
    out = S.copy()
    for k, d in enumerate(days):
        out[day == d] -= M[k]
    return out + M.mean(0)


def disorder(S: np.ndarray, agent: np.ndarray, day: np.ndarray, c_ref: np.ndarray | None = None,
             min_days: int = 2) -> dict:
    """Random-field variance Delta^2, uniform-field strength M^2 (from c_ref; 0-vector = whitening center), R."""
    Sp = day_field_replace(S, day)
    ags = [a for a in np.unique(agent) if (agent == a).sum() >= min_days]
    if len(ags) < 3:
        return {"R": np.nan, "D2": np.nan, "M2": np.nan, "N": len(ags)}
    phi, noise = [], []
    for a in ags:
        Y = Sp[agent == a]
        f = Y.mean(0)
        phi.append(f)
        D = len(Y)
        noise.append(((Y - f) ** 2).sum(1).sum() / (D - 1) / D)
    phi = np.asarray(phi)
    noise = np.asarray(noise)
    N = len(ags)
    mu = phi.mean(0)
    D2 = N / (N - 1) * ((phi - mu) ** 2).sum(1).mean() - noise.mean()
    ref = np.zeros_like(mu) if c_ref is None else c_ref
    M2 = ((mu - ref) ** 2).sum() - (max(D2, 0) + noise.mean()) / N
    R = D2 / (D2 + M2) if (D2 + M2) > 0 else np.nan
    return {"R": float(R), "D2": float(D2), "M2": float(M2), "N": N, "noise": float(noise.mean()),
            "phi": phi, "mu": mu, "agents": np.asarray(ags)}


def disorder_boot(S, agent, day, c_ref=None, B: int = 500, seed: int = 0) -> tuple:
    """Agent bootstrap CI for R (agents resampled with replacement; duplicates relabelled)."""
    rng = np.random.default_rng(seed)
    ags = np.unique(agent)
    rs = []
    for _ in range(B):
        pick = rng.choice(ags, len(ags), replace=True)
        idx, lab = [], []
        for k, a in enumerate(pick):
            ii = np.flatnonzero(agent == a)
            idx.append(ii)
            lab.append(np.full(len(ii), k))
        idx = np.concatenate(idx)
        rs.append(disorder(S[idx], np.concatenate(lab), day[idx], c_ref)["R"])
    rs = np.asarray(rs)
    rs = rs[np.isfinite(rs)]
    return (float(np.percentile(rs, 2.5)), float(np.percentile(rs, 97.5))) if len(rs) > 20 else (np.nan, np.nan)


def role_share(phi: np.ndarray, rvec: np.ndarray, n_perm: int = 2000, seed: int = 0) -> dict:
    """R^2 of (phi_i - mu) on a(r_i - rbar) with one scalar gain a; role-permutation p."""
    P = phi - phi.mean(0)
    Rc = rvec - rvec.mean(0)

    def r2(Rc_):
        a = (P * Rc_).sum() / (Rc_ ** 2).sum()
        return 1 - ((P - a * Rc_) ** 2).sum() / (P ** 2).sum(), a
    obs, a = r2(Rc)
    rng = np.random.default_rng(seed)
    null = np.array([r2(Rc[rng.permutation(len(Rc))])[0] for _ in range(n_perm)])
    return {"R2_role": float(obs), "a": float(a), "p": float((1 + (null >= obs).sum()) / (1 + n_perm)),
            "null_mean": float(null.mean())}


# ------------------------------------------------------------------------------------------------ O2: gain b
def center_agent_day(X: np.ndarray, agent: np.ndarray, day: np.ndarray, min_w: int = 2):
    """x_iw = v_iw - mean of i's windows that day; rows of agent-days with < min_w windows are dropped."""
    key = agent.astype(np.int64) * 1000 + day
    keep = np.zeros(len(X), bool)
    out = np.zeros_like(X)
    for k in np.unique(key):
        ii = np.flatnonzero(key == k)
        if len(ii) >= min_w:
            out[ii] = X[ii] - X[ii].mean(0)
            keep[ii] = True
    return out, keep


def _gain_sums(x, agent, day, win, room, pair_day=None):
    """Numerator and denominator of b over all (i, w): <x_iw, m_{-i,w}>, |m_{-i,w}|^2.
    pair_day: None for the real pairing, or a dict day -> other day for the surrogate (others' windows from e)."""
    idx = {}
    for r, (d, w, ro) in enumerate(zip(day, win, room)):
        idx.setdefault((d, w, ro), []).append(r)
    num = den = 0.0
    for (d, w, ro), rows in idx.items():
        if pair_day is None:
            src = rows
        else:
            e = pair_day.get(d)
            if e is None:
                continue
            src = idx.get((e, w, ro), [])
        if not src:
            continue
        Xs = x[src]
        As = agent[src]
        tot = Xs.sum(0)
        for r in rows:
            same = As == agent[r]
            k = len(src) - same.sum()
            if k < 1:
                continue
            m = (tot - Xs[same].sum(0)) / k
            num += float(x[r] @ m)
            den += float(m @ m)
    return num, den


def gain(X, agent, day, win, room, B: int = 200, seed: int = 0) -> dict:
    x, keep = center_agent_day(X, agent, day)
    x, agent, day, win, room = x[keep], agent[keep], day[keep], win[keep], room[keep]
    days = np.unique(day)
    if len(days) < 2:
        return {"b": np.nan, "b_surr": np.nan, "b_ex": np.nan, "ci": (np.nan, np.nan)}

    def stat(sel_days):
        # real
        num = den = 0.0
        snum = sden = 0.0
        for d in sel_days:
            m = day == d
            n_, d_ = _gain_sums(x[m], agent[m], day[m], win[m], room[m])
            num += n_
            den += d_
        # surrogate: every ordered pair (d, e != d) of selected days
        for d in sel_days:
            for e in sel_days:
                if e == d:
                    continue
                m = (day == d) | (day == e)
                # build sums with i from day d and others from day e
                xs, ag, dy, wn, rm = x[m], agent[m], day[m], win[m], room[m]
                n_, d_ = _cross_sums(xs, ag, dy, wn, rm, d, e)
                snum += n_
                sden += d_
        b = num / den if den > 0 else np.nan
        bs = snum / sden if sden > 0 else np.nan
        return b, bs
    b, bs = stat(list(days))
    rng = np.random.default_rng(seed)
    boots = []
    if B:
        for _ in range(B):
            pick = rng.choice(days, len(days), replace=True)
            if len(np.unique(pick)) < 2:
                continue
            bb, bbs = stat(list(np.unique(pick)))  # unique days (pair surrogate needs distinct days)
            boots.append(bb - bbs)
    boots = np.asarray(boots)
    ci = (float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))) if len(boots) > 20 else (np.nan, np.nan)
    return {"b": float(b), "b_surr": float(bs), "b_ex": float(b - bs), "ci": ci, "n_windows": int(len(x))}


def _cross_sums(x, agent, day, win, room, d, e):
    """i's windows on day d against the others' windows on day e at the same window index and room."""
    idx_e = {}
    for r in np.flatnonzero(day == e):
        idx_e.setdefault((win[r], room[r]), []).append(r)
    num = den = 0.0
    for r in np.flatnonzero(day == d):
        src = idx_e.get((win[r], room[r]))
        if not src:
            continue
        src = [s for s in src if agent[s] != agent[r]]
        if not src:
            continue
        m = x[src].mean(0)
        num += float(x[r] @ m)
        den += float(m @ m)
    return num, den


def agent_gain(X, agent, day, win, room, target: int, ref_room: int | None = None) -> dict:
    """Pull of one agent toward the mean of the others (optionally only others in ref_room), surrogate-corrected."""
    x, keep = center_agent_day(X, agent, day)
    x, agent, day, win, room = x[keep], agent[keep], day[keep], win[keep], room[keep]
    days = np.unique(day)

    def sums(d, e):
        num = den = 0.0
        for r in np.flatnonzero((day == d) & (agent == target)):
            src = np.flatnonzero((day == e) & (win == win[r]) & (agent != target)
                                 & ((room == ref_room) if ref_room is not None else True))
            if len(src) == 0:
                continue
            m = x[src].mean(0)
            num += float(x[r] @ m)
            den += float(m @ m)
        return num, den
    n = d_ = sn = sd = 0.0
    for d in days:
        a, b = sums(d, d)
        n += a
        d_ += b
        for e in days:
            if e != d:
                a, b = sums(d, e)
                sn += a
                sd += b
    b = n / d_ if d_ > 0 else np.nan
    bs = sn / sd if sd > 0 else np.nan
    return {"b": b, "b_surr": bs, "b_ex": b - bs if np.isfinite(b) and np.isfinite(bs) else np.nan}


# ------------------------------------------------------------------------------------------------ O3: P(q)
def overlaps(H1, H2, S_day_mean_rm, agent, day, D):
    """q(d, d') for d < d' (symmetric half pairing) and q_self(d). Inputs: unit-normalized delta halves."""
    ags = np.unique(agent)
    A = {a: {} for a in ags}
    for r, (a, d) in enumerate(zip(agent, day)):
        A[a][d] = r
    q = np.full((D, D), np.nan)
    for d in range(D):
        for e in range(d, D):
            vals = []
            for a in ags:
                if d in A[a] and e in A[a]:
                    i, j = A[a][d], A[a][e]
                    if d == e:
                        vals.append(float(H1[i] @ H2[i]))
                    else:
                        vals.append(0.5 * float(H1[i] @ H2[j] + H2[i] @ H1[j]))
            if len(vals) >= 3:
                q[d, e] = q[e, d] = np.mean(vals)
    return q


def delta_halves(H1, H2, S, hv_agent, hv_day, ad_agent, ad_day):
    """Remove the day field m_d (mean of full agent-day states that day) from each half, then normalize."""
    m = {d: S[ad_day == d].mean(0) for d in np.unique(ad_day)}
    M = np.stack([m[d] for d in hv_day])
    return unit(H1 - M), unit(H2 - M)


def q_stats(q: np.ndarray) -> dict:
    D = q.shape[0]
    iu = np.triu_indices(D, 1)
    v = q[iu]
    lag = (iu[1] - iu[0])
    ok = np.isfinite(v)
    v, lag = v[ok], lag[ok]
    if len(v) < 4:
        return {"qbar": np.nan, "sd": np.nan, "bc": np.nan, "W_res": np.nan}
    from scipy.stats import kurtosis, skew
    n = len(v)
    g1 = skew(v, bias=False) if n > 3 else 0.0
    g2 = kurtosis(v, bias=False) if n > 3 else 0.0
    bc = (g1 ** 2 + 1) / (g2 + 3 * (n - 1) ** 2 / ((n - 2) * (n - 3))) if n > 3 else np.nan
    res = v.copy()
    for L in np.unique(lag):
        res[lag == L] -= v[lag == L].mean()
    qself = np.nanmean(np.diag(q))
    long = v[lag >= max(1, D // 2)]
    qinf = long.mean() if len(long) else np.nan
    q1 = v[lag == 1].mean() if (lag == 1).any() else np.nan
    M = (q1 - qinf) / (qself - qinf) if np.isfinite(qinf) and qself != qinf else np.nan
    return {"qbar": float(v.mean()), "var": float(v.var()), "sd": float(v.std()), "bc": float(bc),
            "skew": float(g1), "var_res": float(res.var()), "qself": float(qself), "qinf": float(qinf),
            "M": float(M), "n_pairs": int(len(v))}


def pq_test(H1d, H2d, agent, day, D, n_shift: int = 2000, seed: int = 0) -> dict:
    q = overlaps(H1d, H2d, None, agent, day, D)
    obs = q_stats(q)
    rng = np.random.default_rng(seed)
    ags = np.unique(agent)
    nv, nr, nq = [], [], []
    for _ in range(n_shift):
        sh = {a: rng.integers(D) for a in ags}
        d2 = np.array([(d + sh[a]) % D for a, d in zip(agent, day)])
        s = q_stats(overlaps(H1d, H2d, None, agent, d2, D))
        nv.append(s["var"])
        nr.append(s["var_res"])
        nq.append(s["qbar"])
    nv, nr, nq = map(np.asarray, (nv, nr, nq))
    return {**obs, "W_P": float(obs["var"] / np.nanmean(nv)), "W": float(obs["var_res"] / np.nanmean(nr)),
            "W_P_band": (float(np.nanpercentile(nv / np.nanmean(nv), 5)), float(np.nanpercentile(nv / np.nanmean(nv), 95))),
            "p_WP": float((1 + (nv >= obs["var"]).sum()) / (1 + len(nv))),
            "p_W": float((1 + (nr >= obs["var_res"]).sum()) / (1 + len(nr))),
            "qbar_band": (float(np.nanpercentile(nq, 5)), float(np.nanpercentile(nq, 95))), "q": q}


# ------------------------------------------------------------------------------------------------ O4: J^c and niche
def comovement(X, agent, day, win, min_shared: int = 10) -> pl.DataFrame:
    """H22's J^c: r_ij over shared windows of agent-day-centered window states minus the cross-day surrogate."""
    x, keep = center_agent_day(X, agent, day)
    x, agent, day, win = x[keep], agent[keep], day[keep], win[keep]
    ags = np.unique(agent)
    days = np.unique(day)
    # per agent: dict (day, win) -> row
    pos = {a: {} for a in ags}
    for r, (a, d, w) in enumerate(zip(agent, day, win)):
        pos[a][(d, w)] = r
    rows = []
    for k, i in enumerate(ags):
        for j in ags[k + 1:]:
            shared = [(pos[i][key], pos[j][key]) for key in pos[i] if key in pos[j]]
            if len(shared) < min_shared:
                continue
            a_ = np.array([s[0] for s in shared])
            b_ = np.array([s[1] for s in shared])
            num = float((x[a_] * x[b_]).sum())
            den = np.sqrt(float((x[a_] ** 2).sum()) * float((x[b_] ** 2).sum()))
            r = num / den if den > 0 else np.nan
            # surrogate over ordered day pairs (d, e != d), same window index
            sn = si = sj = 0.0
            for (d, w), ri in pos[i].items():
                for e in days:
                    if e == d:
                        continue
                    rj = pos[j].get((e, w))
                    if rj is None:
                        continue
                    sn += float(x[ri] @ x[rj])
                    si += float(x[ri] @ x[ri])
                    sj += float(x[rj] @ x[rj])
            rs = sn / np.sqrt(si * sj) if si > 0 and sj > 0 else 0.0
            rows.append((int(i), int(j), r, rs, r - rs, len(shared)))
    return pl.DataFrame(rows, schema={"i": pl.Int8, "j": pl.Int8, "r": pl.Float64, "r_surr": pl.Float64,
                                      "J": pl.Float64, "n_shared": pl.Int32}, orient="row")


def niche_overlap(pairs: pl.DataFrame, rv: dict) -> pl.DataFrame:
    """n_ij = cos(r_i - rbar, r_j - rbar) over the agents with role vectors (rv: agent -> vector)."""
    ags = sorted(rv)
    rb = np.mean([rv[a] for a in ags], 0)
    c = {a: unit(rv[a] - rb) for a in ags}
    return pairs.with_columns(pl.struct("i", "j").map_elements(
        lambda r: float(c[r["i"]] @ c[r["j"]]) if r["i"] in c and r["j"] in c else None,
        return_dtype=pl.Float64).alias("niche")).with_columns((pl.col("niche") ** 2).alias("niche2"))


def ols(y: np.ndarray, X: np.ndarray) -> np.ndarray:
    return np.linalg.lstsq(X, y, rcond=None)[0]


def niche_fit(P: pl.DataFrame, covs=("same_lab", "log_reads"), reg: str = "niche2") -> dict:
    """beta_n on non-SR, non-OP pairs; T_SR, That_SR and the mediation gap G. reg: niche2 (squared overlap, the model's
    prediction; Amendment A1) or niche (linear, variant)."""
    P = P.filter(pl.col(reg).is_not_null() & pl.col("J").is_not_null())
    U = P.filter(pl.col("cls").is_null())
    SR = P.filter(pl.col("cls") == "SR")
    if U.height < 15:
        return {}
    Xu = np.column_stack([np.ones(U.height), U[reg].to_numpy()] + [U[c].cast(pl.Float64).to_numpy() for c in covs])
    beta = ols(U["J"].to_numpy(), Xu)
    out = {"beta_n": float(beta[1]), "n_U": U.height, "n_SR": SR.height}
    for k, c in enumerate(covs):
        out[f"beta_{c}"] = float(beta[2 + k])
    if SR.height:
        T = float(SR["J"].mean() - U["J"].mean())
        That = float(beta[1] * (SR[reg].mean() - U[reg].mean()))
        out.update({"T_SR": T, "That_SR": That, "G": T - That, "n_SR_niche": float(SR[reg].mean()),
                    "n_U_niche": float(U[reg].mean())})
    return out


def jackknife(P: pl.DataFrame, fn, keys) -> dict:
    """Leave-one-agent-out jackknife SEs for the scalar outputs `keys` of fn(P)."""
    full = fn(P)
    ags = sorted(set(P["i"].to_list()) | set(P["j"].to_list()))
    reps = {k: [] for k in keys}
    for a in ags:
        r = fn(P.filter((pl.col("i") != a) & (pl.col("j") != a)))
        for k in keys:
            if k in r and np.isfinite(r[k]):
                reps[k].append(r[k])
    out = {}
    for k in keys:
        v = np.asarray(reps[k])
        n = len(v)
        out[f"{k}_se"] = float(np.sqrt((n - 1) / n * ((v - v.mean()) ** 2).sum())) if n > 2 else np.nan
    return {**full, **out}


def niche_perm(P: pl.DataFrame, rv: dict, covs=("same_lab", "log_reads"), n_perm: int = 2000, seed: int = 0,
               reg: str = "niche2") -> float:
    """Role-permutation p (one-sided, greater) for beta_n: role vectors reassigned across agents."""
    obs = niche_fit(P, covs, reg).get("beta_n", np.nan)
    rng = np.random.default_rng(seed)
    ags = sorted(rv)
    V = np.stack([rv[a] for a in ags])
    null = []
    base = P.drop("niche", "niche2")
    for _ in range(n_perm):
        perm = rng.permutation(len(ags))
        rvp = {a: V[perm[k]] for k, a in enumerate(ags)}
        null.append(niche_fit(niche_overlap(base, rvp), covs, reg).get("beta_n", np.nan))
    null = np.asarray(null)
    null = null[np.isfinite(null)]
    return float((1 + (null >= obs).sum()) / (1 + len(null)))


def sr_adjusted(P: pl.DataFrame, covs) -> float:
    """Coefficient of the SR indicator over non-OP pairs with the given covariates."""
    Q = P.filter((pl.col("cls").is_null() | (pl.col("cls") == "SR")) & pl.col("J").is_not_null())
    if Q.filter(pl.col("cls") == "SR").height == 0:
        return np.nan
    X = np.column_stack([np.ones(Q.height), (Q["cls"] == "SR").fill_null(False).cast(pl.Float64).to_numpy()]
                        + [Q[c].cast(pl.Float64).to_numpy() for c in covs])
    return float(ols(Q["J"].to_numpy(), X)[1])


def re_pool(est, se) -> dict:
    """DerSimonian-Laird random-effects pool."""
    est, se = np.asarray(est, float), np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[ok], se[ok]
    k = len(est)
    if k == 0:
        return {"est": np.nan, "se": np.nan, "lo": np.nan, "hi": np.nan, "k": 0, "I2": np.nan, "p": np.nan}
    w = 1 / se ** 2
    fe = (w * est).sum() / w.sum()
    Q = (w * (est - fe) ** 2).sum()
    tau2 = max(0.0, (Q - (k - 1)) / (w.sum() - (w ** 2).sum() / w.sum())) if k > 1 else 0.0
    wr = 1 / (se ** 2 + tau2)
    m = (wr * est).sum() / wr.sum()
    s = np.sqrt(1 / wr.sum())
    from scipy.stats import norm
    return {"est": float(m), "se": float(s), "lo": float(m - 1.96 * s), "hi": float(m + 1.96 * s), "k": k,
            "I2": float(max(0.0, (Q - (k - 1)) / Q)) if Q > 0 else 0.0, "p": float(2 * norm.sf(abs(m / s)))}
