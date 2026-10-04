"""H66 estimators: residual trimmed co-activation, the latency field, its share, lags, rooms and edges.

One entry point, `analyze_grid(grid)`, takes a unit's minute grid (schema of scheme/build.py) and returns a dict of
statistics. The same function runs on synthetic grids (analysis/synthetic.py) and real ones (analysis/replication.py).

Definitions (card, "Model"):
  a_i(m)  act call in minute m; n_i(m) number of act calls (intensity variant)
  z_i(m)  latency spin: median log turnaround in m, standardized within agent-day (median, 1.4826 MAD); NaN if none
  L_-ij   third-party latency field: mean of z_k over agents k != i, j with a value in m
  u_-ij   third-party infrastructure-error field: errors of agents k != i, j in m
  window  all-present minutes (every day-present agent between its first and last act minute) with >= FIELD_MIN
          agents contributing a latency value
  e_i     a_i demeaned within (day, 30-min block) on the window
  rho     mean pairwise corr(e_i, e_j); rho_adj on residuals after regressing e_i, e_j on (L_-ij, u_-ij), block-demeaned
  E       rho - mean(rho under block shift of activity), E_adj likewise; f_lat = 1 - E_adj / E
  Delta f f_lat - mean f_lat with the field circularly shifted within day (shifted-input null)
"""
from __future__ import annotations

import numpy as np
import polars as pl

BLOCK = 30
KLAG = 5          # field kernel: L(m), L(m-1), ..., L(m-KLAG)  (Amendment 1)
FIELD_MIN = 5
PRESENT_MIN = 10
EDGE = 30


# --------------------------------------------------------------------------------------------- assembly
def _day_arrays(gd: pl.DataFrame, agents: list[int]):
    T = int(gd["m"].max()) + 1
    N = len(agents)
    idx = {a: k for k, a in enumerate(agents)}
    out = {k: np.full((T, N), np.nan, np.float64) for k in ("a", "n", "lat", "api", "err", "room")}
    m = gd["m"].to_numpy().astype(int)
    c = np.array([idx[a] for a in gd["agent"].to_list()])
    for k in out:
        v = gd[k].to_numpy().astype(float) if gd[k].dtype != pl.Null else np.full(gd.height, np.nan)
        out[k][m, c] = v
    for k in ("a", "n", "err"):
        out[k] = np.nan_to_num(out[k])
    return out


def _zscore_day(lat: np.ndarray) -> np.ndarray:
    z = np.full_like(lat, np.nan)
    for j in range(lat.shape[1]):
        v = lat[:, j]
        ok = ~np.isnan(v)
        if ok.sum() < 10:
            continue
        med = np.median(v[ok])
        mad = 1.4826 * np.median(np.abs(v[ok] - med))
        if mad <= 0:
            mad = np.std(v[ok]) or 1.0
        z[ok, j] = (v[ok] - med) / mad
    return z


def assemble(grid: pl.DataFrame, field_min: int = FIELD_MIN, window: str = "allpresent"):
    """Stack the unit's days into row arrays on the analysis window. Returns a dict of arrays (R rows x N agents)."""
    agents = sorted(grid["agent"].unique().to_list())
    N = len(agents)
    rows = {k: [] for k in ("A", "Nn", "Z", "Api", "U", "Room", "P", "day", "blk", "minute", "edge", "Zl", "Ul")}
    full = []  # per-day full-window arrays for lag profiles
    for di, (d, gd) in enumerate(sorted(grid.group_by("pt_date"), key=lambda x: x[0][0])):
        X = _day_arrays(gd, agents)
        a = X["a"]
        present = a.sum(0) >= PRESENT_MIN
        if present.sum() < 3:
            continue
        T = a.shape[0]
        inspan = np.zeros_like(a, bool)
        for j in np.flatnonzero(present):
            on = np.flatnonzero(a[:, j] > 0)
            inspan[on[0]:on[-1] + 1, j] = True
        if window == "allpresent":
            win = inspan[:, present].all(1)
        else:  # "span": any two present agents in span; pairs restricted later via P
            win = inspan[:, present].sum(1) >= 2
        z = _zscore_day(np.where(inspan, X["lat"], np.nan))
        api = _zscore_day(np.where(inspan, X["api"], np.nan))
        z[:, ~present] = np.nan
        api[:, ~present] = np.nan
        cnt = (~np.isnan(z)).sum(1)
        keep = win & (cnt >= field_min)
        if keep.sum() < 10:
            continue
        P = np.repeat(present[None, :], T, 0) & (inspan if window == "span" else True)
        ix = np.flatnonzero(win)
        edge = np.zeros(T, bool)
        if ix.size:
            edge[ix[0]:ix[0] + EDGE] = True
            edge[max(ix[-1] - EDGE + 1, 0):ix[-1] + 1] = True
        full.append({"a": np.where(P, a, np.nan)[win], "z": z[win], "present": present, "minute": np.flatnonzero(win)})
        sel = np.flatnonzero(keep)
        rows["A"].append(a[sel]); rows["Nn"].append(X["n"][sel]); rows["Z"].append(z[sel]); rows["Api"].append(api[sel])
        rows["U"].append(X["err"][sel]); rows["Room"].append(X["room"][sel]); rows["P"].append(P[sel])
        rows["day"].append(np.full(sel.size, di)); rows["blk"].append(di * 1000 + sel // BLOCK)
        rows["minute"].append(sel); rows["edge"].append(edge[sel])
        zl, ul = [], []
        for k in range(1, KLAG + 1):
            ii = sel - k
            okk = ii >= 0
            zk = np.full((sel.size, N), np.nan); uk = np.zeros((sel.size, N))
            zk[okk] = z[ii[okk]]; uk[okk] = X["err"][ii[okk]]
            zl.append(zk); ul.append(uk)
        rows["Zl"].append(np.stack(zl)); rows["Ul"].append(np.stack(ul))
    if not rows["A"]:
        return None
    out = {k: np.concatenate(v, axis=1 if k in ("Zl", "Ul") else 0) for k, v in rows.items()}
    out["agents"] = np.array(agents)
    out["full"] = full
    return out


# --------------------------------------------------------------------------------------------- helpers
def block_demean(X: np.ndarray, blk: np.ndarray, P: np.ndarray | None = None) -> np.ndarray:
    """Demean each column within blocks (over rows where P is True); rows outside P get 0."""
    Y = np.where(np.isnan(X), 0.0, X).astype(float)
    W = np.ones_like(Y) if P is None else (P & ~np.isnan(X)).astype(float)
    if X.ndim == 1:
        Y, W = Y[:, None], W[:, None]
    ub, inv = np.unique(blk, return_inverse=True)
    s = np.zeros((ub.size, Y.shape[1])); c = np.zeros_like(s)
    np.add.at(s, inv, Y * W); np.add.at(c, inv, W)
    mu = s / np.maximum(c, 1)
    out = (Y - mu[inv]) * W
    return out[:, 0] if X.ndim == 1 else out


def shift_within_blocks(X: np.ndarray, blk: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Independent circular shift (>= 1) of every column within each block (DQ8's block shift)."""
    Y = np.empty_like(X)
    for b in np.unique(blk):
        ix = np.flatnonzero(blk == b)
        L = ix.size
        if L < 2:
            Y[ix] = X[ix]
            continue
        sh = rng.integers(1, L, X.shape[1])
        ar = (np.arange(L)[:, None] - sh[None, :]) % L
        Y[ix] = X[ix][ar, np.arange(X.shape[1])[None, :]]
    return Y


def shift_within_days(X: np.ndarray, day: np.ndarray, rng: np.random.Generator, min_shift: int = 30) -> np.ndarray:
    """One common circular shift of all columns within each day by >= min_shift rows (shifted-input null)."""
    Y = np.empty_like(X)
    for d in np.unique(day):
        ix = np.flatnonzero(day == d)
        L = ix.size
        lo, hi = min(min_shift, L // 3), max(L - min_shift, L // 3 + 1)
        s = int(rng.integers(lo, hi)) if hi > lo else 1
        Y[ix] = np.roll(X[ix], s, axis=0)
    return Y


def _pairs(N):
    return [(i, j) for i in range(N) for j in range(i + 1, N)]


def _corr(x, y):
    sx, sy = (x * x).sum(), (y * y).sum()
    return float((x * y).sum() / np.sqrt(sx * sy)) if sx > 0 and sy > 0 else np.nan


class PairField:
    """Third-party fields per pair (latency kernel L_-ij(m-k), k = 0..klag; error field u_-ij; optional lab fields),
    with an orthonormal basis for residualization."""

    def __init__(self, Z, U, P, blk, pairs, use=("lat", "err"), Zl=None, Ul=None, klag=0, labs=None):
        self.P, self.blk, self.use, self.labs = P, blk, use, labs
        self.layers = [(Z, U)] + ([(Zl[k], Ul[k]) for k in range(klag)] if klag and Zl is not None else [])
        self.pre = []
        for Zk, Uk in self.layers:
            valid = ~np.isnan(Zk) & P
            Zv = np.where(valid, Zk, 0.0)
            Uv = np.where(P, Uk, 0.0)
            self.pre.append((valid, Zv, Zv.sum(1), valid.sum(1), Uv, Uv.sum(1)))
        self.Q = {pr: self.basis(*pr) for pr in pairs}

    def basis(self, i, j):
        rows = self.P[:, i] & self.P[:, j]
        cols = []
        for (valid, Zv, S, C, Uv, Us) in self.pre:
            if "lat" in self.use:
                cnt = C - valid[:, i] - valid[:, j]
                Lf = np.where(cnt > 0, (S - Zv[:, i] - Zv[:, j]) / np.maximum(cnt, 1), 0.0)
                cols.append(Lf)
            if "lab" in self.use and self.labs is not None:
                for lab in {self.labs[i], self.labs[j]}:
                    m = (self.labs == lab)
                    m[[i, j]] = False
                    if m.sum() >= 2:
                        c2 = valid[:, m].sum(1)
                        cols.append(np.where(c2 > 0, Zv[:, m].sum(1) / np.maximum(c2, 1), 0.0))
            if "err" in self.use:
                cols.append(Us - Uv[:, i] - Uv[:, j])
        if not cols:
            return np.zeros((rows.size, 0))
        X = np.column_stack([block_demean(c, self.blk) * rows for c in cols])
        keep = X.std(0) > 1e-12
        if not keep.any():
            return np.zeros((X.shape[0], 0))
        q, _ = np.linalg.qr(X[:, keep])
        return q


def _resid(e, Q):
    return e - Q @ (Q.T @ e) if Q.shape[1] else e


def pair_corrs(E: np.ndarray, P: np.ndarray, pairs, Qmap=None, blocks=None):
    """Pairwise corr of block-demeaned columns (and optionally residualized). If blocks is given, also returns
    per-pair per-block sums (xy, xx, yy) for the bootstrap."""
    r = np.full(len(pairs), np.nan)
    sums = None
    if blocks is not None:
        ub, inv = np.unique(blocks, return_inverse=True)
        sums = np.zeros((len(pairs), 3, ub.size))
    for k, (i, j) in enumerate(pairs):
        rows = P[:, i] & P[:, j]
        if rows.sum() < 20:
            continue
        x, y = E[:, i] * rows, E[:, j] * rows
        if Qmap is not None:
            Q = Qmap[(i, j)]
            x, y = _resid(x, Q) * rows, _resid(y, Q) * rows
        r[k] = _corr(x, y)
        if sums is not None:
            np.add.at(sums[k, 0], inv, x * y); np.add.at(sums[k, 1], inv, x * x); np.add.at(sums[k, 2], inv, y * y)
    return r, sums


def _rho_from_sums(sums, w=None):
    xy, xx, yy = sums[:, 0], sums[:, 1], sums[:, 2]
    if w is not None:
        xy, xx, yy = xy @ w, xx @ w, yy @ w
    else:
        xy, xx, yy = xy.sum(1), xx.sum(1), yy.sum(1)
    with np.errstate(invalid="ignore", divide="ignore"):
        r = xy / np.sqrt(xx * yy)
    return np.nanmean(r)


# --------------------------------------------------------------------------------------------- latency field strength
def latency_strength(Z, P, blk, pairs, labs, rooms_mode, rng, R=49):
    valid = ~np.isnan(Z) & P
    Zd = block_demean(np.where(valid, Z, np.nan), blk, valid)

    def rhos(Zd_, valid_):
        out = np.full(len(pairs), np.nan)
        for k, (i, j) in enumerate(pairs):
            rows = valid_[:, i] & valid_[:, j]
            if rows.sum() < 30:
                continue
            out[k] = _corr(Zd_[rows, i] - Zd_[rows, i].mean(), Zd_[rows, j] - Zd_[rows, j].mean())
        return out
    obs = rhos(Zd, valid)
    same_lab = np.array([labs[i] == labs[j] for i, j in pairs])
    same_room = np.array([rooms_mode[i] == rooms_mode[j] and rooms_mode[i] >= 0 for i, j in pairs])
    null_all, null_same, null_cross = [], [], []
    Zn = np.where(valid, Z, np.nan)
    for _ in range(R):
        Zs = shift_within_blocks(Zn, blk, rng)
        vs = ~np.isnan(Zs) & P
        rn = rhos(block_demean(Zs, blk, vs), vs)
        null_all.append(np.nanmean(rn)); null_same.append(np.nanmean(rn[same_lab]) if same_lab.any() else np.nan)
        null_cross.append(np.nanmean(rn[~same_lab]) if (~same_lab).any() else np.nan)
    na = np.array(null_all)

    def summ(mask, nl):
        if not mask.any() or np.all(np.isnan(obs[mask])):
            return {"rho": None, "excess": None, "p": None, "n_pairs": 0}
        o = float(np.nanmean(obs[mask]))
        nl = np.array(nl)
        return {"rho": o, "excess": o - float(np.nanmean(nl)), "p": float((1 + np.sum(nl >= o)) / (1 + len(nl))),
                "n_pairs": int(np.isfinite(obs[mask]).sum())}
    res = {"all": summ(np.ones(len(pairs), bool), na), "same_lab": summ(same_lab, null_same),
           "cross_lab": summ(~same_lab, null_cross)}
    if same_room.any() and (~same_room).any() and len(set(rooms_mode[rooms_mode >= 0])) > 1:
        res["same_room"] = {"rho": float(np.nanmean(obs[same_room])), "n_pairs": int(np.isfinite(obs[same_room]).sum())}
        res["cross_room"] = {"rho": float(np.nanmean(obs[~same_room])), "n_pairs": int(np.isfinite(obs[~same_room]).sum())}
    res["null_mean"] = float(np.nanmean(na))
    res["pair_rho"] = obs
    return res


def lag_profiles(full, kmax=5):
    """C_l(k): mean over ordered pairs of corr(z_i(m), z_j(m+k)); C_e(k): mean over agents of corr(a_i(m), L_-i(m+k))
    on each day's all-present window (consecutive minutes only)."""
    num_l = np.zeros(2 * kmax + 1); den_l = np.zeros(2 * kmax + 1)
    num_e = np.zeros(2 * kmax + 1); den_e = np.zeros(2 * kmax + 1)
    for D in full:
        z, a, mins, pres = D["z"], D["a"], D["minute"], D["present"]
        if z.shape[0] < 30:
            continue
        # consecutive-minute index within the window
        T = mins.max() + 1
        Zf = np.full((T, z.shape[1]), np.nan); Af = np.full((T, z.shape[1]), np.nan)
        Zf[mins] = z; Af[mins] = a
        Zf[:, ~pres] = np.nan; Af[:, ~pres] = np.nan
        Zc = Zf - np.nanmean(Zf, 0); Ac = Af - np.nanmean(Af, 0)
        valid = ~np.isnan(Zc)
        S = np.where(valid, Zc, 0).sum(1); C = valid.sum(1)
        for ki, k in enumerate(range(-kmax, kmax + 1)):
            lo, hi = max(0, -k), T - max(0, k)
            Zi = Zc[lo:hi]; Zj = Zc[lo + k:hi + k]
            for i in np.flatnonzero(pres):
                xi = Zi[:, i]
                for j in np.flatnonzero(pres):
                    if i == j:
                        continue
                    yj = Zj[:, j]
                    ok = ~np.isnan(xi) & ~np.isnan(yj)
                    if ok.sum() < 20:
                        continue
                    c = _corr(xi[ok] - xi[ok].mean(), yj[ok] - yj[ok].mean())
                    if np.isfinite(c):
                        num_l[ki] += c; den_l[ki] += 1
            # activity vs leave-one-out field
            for i in np.flatnonzero(pres):
                Lm = np.where(C - valid[:, i] > 0, (S - np.where(valid[:, i], Zc[:, i], 0)) / np.maximum(C - valid[:, i], 1), np.nan)
                x = Ac[lo:hi, i]; y = Lm[lo + k:hi + k]
                ok = ~np.isnan(x) & ~np.isnan(y)
                if ok.sum() < 20:
                    continue
                c = _corr(x[ok] - x[ok].mean(), y[ok] - y[ok].mean())
                if np.isfinite(c):
                    num_e[ki] += c; den_e[ki] += 1
    return {"k": list(range(-kmax, kmax + 1)), "C_lat": (num_l / np.maximum(den_l, 1)).tolist(),
            "C_act_field": (num_e / np.maximum(den_e, 1)).tolist()}


# --------------------------------------------------------------------------------------------- main estimator
def coactivation(Y, D, pairs, rng, R=99, K=20, B=200, use=("lat", "err"), boot_unit="auto", extra_masks=None,
                 klag=KLAG, labs=None):
    """E, E_adj, f_lat, Delta f with CIs for the activity-like matrix Y (A or Nn) on assembled rows D."""
    P, blk, day = D["P"], D["blk"], D["day"]
    Ed = block_demean(Y, blk, P)
    pf = PairField(D["Z"], D["U"], P, blk, pairs, use=use, Zl=D["Zl"], Ul=D["Ul"], klag=klag, labs=labs)
    n_days = len(np.unique(day))
    bunits = day if (boot_unit == "day" or (boot_unit == "auto" and n_days >= 3)) else blk
    r_raw, s_raw = pair_corrs(Ed, P, pairs, None, bunits)
    r_adj, s_adj = pair_corrs(Ed, P, pairs, pf.Q, bunits)
    nr, na = [], []
    nmask = {k: [] for k in (extra_masks or {})}
    for _ in range(R):
        Ys = shift_within_blocks(Y, blk, rng)
        Es = block_demean(Ys, blk, P)
        a_, _ = pair_corrs(Es, P, pairs)
        b_, _ = pair_corrs(Es, P, pairs, pf.Q)
        nr.append(np.nanmean(a_)); na.append(np.nanmean(b_))
        for k, m in (extra_masks or {}).items():
            nmask[k].append(np.nanmean(a_[m]) if m.any() else np.nan)
    nr, na = np.array(nr), np.array(na)
    rho, rho_adj = float(np.nanmean(r_raw)), float(np.nanmean(r_adj))
    E, E_adj = rho - nr.mean(), rho_adj - na.mean()
    p_E = float((1 + np.sum(nr >= rho)) / (1 + R))
    f = 1 - E_adj / E if E != 0 else np.nan
    # shifted-field control
    fs = []
    for _ in range(K):
        seed_k = int(rng.integers(1 << 31))
        Zs = shift_within_days(D["Z"], day, np.random.default_rng(seed_k))
        Us = shift_within_days(D["U"], day, np.random.default_rng(seed_k))
        Zls = np.stack([shift_within_days(D["Zl"][k], day, np.random.default_rng(seed_k)) for k in range(D["Zl"].shape[0])])
        Uls = np.stack([shift_within_days(D["Ul"][k], day, np.random.default_rng(seed_k)) for k in range(D["Ul"].shape[0])])
        pfs = PairField(Zs, Us, P, blk, pairs, use=use, Zl=Zls, Ul=Uls, klag=klag, labs=labs)
        b_, _ = pair_corrs(Ed, P, pairs, pfs.Q)
        fs.append(1 - (np.nanmean(b_) - na.mean()) / E if E != 0 else np.nan)
    fs = np.array(fs)
    df = f - np.nanmean(fs)
    # bootstrap over resampling units
    nb = s_raw.shape[2]
    boot = []
    for _ in range(B):
        w = np.bincount(rng.integers(0, nb, nb), minlength=nb).astype(float)
        Eb = _rho_from_sums(s_raw, w) - nr.mean()
        Eab = _rho_from_sums(s_adj, w) - na.mean()
        boot.append((Eb, Eab, 1 - Eab / Eb - np.nanmean(fs) if Eb != 0 else np.nan))
    boot = np.array(boot)
    q = lambda x: [float(np.nanpercentile(x, 2.5)), float(np.nanpercentile(x, 97.5))]  # noqa: E731
    out = {"rho": rho, "rho_null": float(nr.mean()), "rho_null_sd": float(nr.std()), "E": float(E), "E_ci": q(boot[:, 0]),
           "z_E": float((rho - nr.mean()) / nr.std()) if nr.std() > 0 else None, "p_E": p_E,
           "rho_adj": rho_adj, "E_adj": float(E_adj), "E_adj_ci": q(boot[:, 1]), "f_lat": float(f),
           "f_shift_mean": float(np.nanmean(fs)), "f_shift_sd": float(np.nanstd(fs)), "delta_f": float(df),
           "delta_f_ci": q(boot[:, 2]), "n_pairs": int(np.isfinite(r_raw).sum()), "n_rows": int(Y.shape[0]),
           "n_boot_units": int(nb), "boot_unit": "day" if bunits is day else "30-min block", "pair_rho": r_raw}
    for k, m in (extra_masks or {}).items():
        if m.any():
            o = float(np.nanmean(r_raw[m]))
            out[f"E_{k}"] = o - float(np.nanmean(nmask[k]))
            out[f"rho_{k}"] = o
            out[f"n_pairs_{k}"] = int(np.isfinite(r_raw[m]).sum())
    return out


def edge_split(Y, D, pairs, rng, R=49):
    """E on the first/last 30 min of each day's all-present window vs the middle (same surrogates)."""
    P, blk = D["P"], D["blk"]
    Ed = block_demean(Y, blk, P)
    res = {}
    for name, rows in (("edge", D["edge"]), ("mid", ~D["edge"])):
        if rows.sum() < 30:
            res[name] = None
            continue
        Pm = P & rows[:, None]
        o, _ = pair_corrs(Ed, Pm, pairs)
        nl = []
        for _ in range(R):
            Es = block_demean(shift_within_blocks(Y, blk, rng), blk, P)
            a_, _ = pair_corrs(Es, Pm, pairs)
            nl.append(np.nanmean(a_))
        res[name] = {"rho": float(np.nanmean(o)), "E": float(np.nanmean(o) - np.mean(nl)), "rows": int(rows.sum())}
    return res


def analyze_grid(grid: pl.DataFrame, seed: int = 0, R: int = 99, K: int = 20, B: int = 200, full: bool = True,
                 window: str = "allpresent") -> dict | None:
    rng = np.random.default_rng(seed)
    D = assemble(grid, window=window)
    if D is None:
        return None
    N = len(D["agents"])
    pairs = _pairs(N)
    lab_of = dict(zip(grid["agent"].to_list(), grid["lab"].to_list()))
    labs = np.array([lab_of[a] for a in D["agents"]])
    Rm = np.where(np.isnan(D["Room"]), -1, D["Room"]).astype(int)
    rooms_mode = np.array([np.bincount(Rm[D["P"][:, k] & (Rm[:, k] >= 0), k]).argmax()
                           if (D["P"][:, k] & (Rm[:, k] >= 0)).any() else -1 for k in range(N)])
    two_rooms = len(set(rooms_mode[rooms_mode >= 0])) > 1
    masks = {}
    same_room = np.array([rooms_mode[i] == rooms_mode[j] and rooms_mode[i] >= 0 for i, j in pairs])
    if two_rooms:
        masks = {"same_room": same_room, "cross_room": ~same_room}
    same_lab = np.array([labs[i] == labs[j] for i, j in pairs])
    masks["cross_lab"] = ~same_lab
    out = {"n_agents": N, "n_days": int(len(np.unique(D["day"]))), "n_rows": int(D["A"].shape[0]),
           "act_share": float(np.nanmean(np.where(D["P"], D["A"], np.nan))), "two_rooms": bool(two_rooms)}
    out["binary"] = coactivation(D["A"], D, pairs, rng, R=R, K=K, B=B, extra_masks=masks)
    lat = latency_strength(D["Z"], D["P"], D["blk"], pairs, labs, rooms_mode, rng, R=min(R, 49))
    out["lat_strength"] = {k: v for k, v in lat.items() if k != "pair_rho"}
    # reliability of the third-party field (Spearman-Brown on the mean of K contributors; Amendment 1)
    kbar = float(np.mean((~np.isnan(D["Z"]) & D["P"]).sum(1))) - 2
    rl = lat["all"]["rho"] or 0.0
    lam = kbar * rl / (1 + (kbar - 1) * rl) if rl > 0 else np.nan
    out["field_reliability"] = {"k_bar": kbar, "rho_lat": rl, "lambda": float(lam) if np.isfinite(lam) else None}
    # (Amendment 1: the Spearman-Brown correction overshoots in synthetic worlds; reported, not used)
    if not full:
        return out
    out["intensity"] = coactivation(D["Nn"], D, pairs, rng, R=min(R, 49), K=min(K, 10), B=B)
    out["binary_lab"] = {k: v for k, v in coactivation(D["A"], D, pairs, rng, R=min(R, 49), K=min(K, 10), B=B,
                                                       use=("lat", "lab", "err"), labs=labs).items() if k != "pair_rho"}
    out["binary_lag0"] = {k: v for k, v in coactivation(D["A"], D, pairs, rng, R=min(R, 49), K=min(K, 10), B=B,
                                                        klag=0).items() if k != "pair_rho"}
    out["binary_lat_only"] = {k: v for k, v in coactivation(D["A"], D, pairs, rng, R=min(R, 49), K=min(K, 10), B=B,
                                                            use=("lat",)).items() if k != "pair_rho"}
    out["edge"] = edge_split(D["A"], D, pairs, rng, R=min(R, 49))
    out["lags"] = lag_profiles(D["full"])
    # per-agent loading on the leave-one-out field
    valid = ~np.isnan(D["Z"]) & D["P"]
    S, C = np.where(valid, D["Z"], 0).sum(1), valid.sum(1)
    load = []
    for i in range(N):
        Lm = np.where(C - valid[:, i] > 0, (S - np.where(valid[:, i], D["Z"][:, i], 0)) / np.maximum(C - valid[:, i], 1), np.nan)
        ok = valid[:, i] & ~np.isnan(Lm)
        if ok.sum() >= 30:
            x = D["Z"][ok, i]; y = Lm[ok]
            load.append({"agent": int(D["agents"][i]), "lab": int(labs[i]), "g": _corr(x - x.mean(), y - y.mean()), "n": int(ok.sum())})
    out["loadings"] = load
    for k in ("binary", "intensity"):
        out[k].pop("pair_rho", None)
    return out
