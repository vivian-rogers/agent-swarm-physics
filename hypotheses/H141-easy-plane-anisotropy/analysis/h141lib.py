"""H141 estimators: subspace autocorrelation on the call clock, anisotropy ratio, variance ratio, day-scale persistence,
random-plane band, cross-fitted principal subspace, and the sender-specific kick split by subspace.

Data (scheme/build.py): G<NN>/statements.parquet (srow, agent, t, pt_date, room, unit_id, turn_id, t_call, n, nf, nc,
half, plane), reads.parquet, planes.npz (text vectors and plane bases; texts only).

Objects (card, Observables):
  h_i      agent well: leave-day-out mean of the agent's statement vectors over the goal period's non-reserved days
  x_B      z_B - h_i(day(B))
  C_P(tau) mean <P x_B, P x_B'> / d_P over same agent-day pairs at call lag tau >= 1, minus the cross-agent covariance
           of the same subspace at the same wall lag (same room, same day; drive correction, H130 A1 point 3)
  rho_A    gamma_perp / gamma_par from A exp(-gamma tau) + B fits of C_E and C_{E-perp}
  V_A      (E|P_E x|^2 / d_E) / (E|(1-P_E) x|^2 / (32 - d_E))
  P_P(1)   day-scale persistence: sum over (agent, consecutive day pair) of <P xbar_d, P xbar_d'> over the root of the
           products of split-half day variances (H108's split-half form), xbar relative to a leave-pair-out well
Every subspace statistic is a linear functional tr(P M) of 32 x 32 second-moment sums kept per agent-day (or per agent
for the day scale), so any plane (text plane, complement, 200 random planes, cross-fitted principal subspace) and the
agent-day block bootstrap are cheap contractions.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import sys  # noqa: E402
from dataclasses import dataclass, field  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
SH = ROOT / "data/processed/shared"
DATA = ROOT / "data/processed/H141-easy-plane-anisotropy"
DIM = 32
CALL_EDGES = np.array([1, 4, 8, 16, 32, 64, 128, 256, 512])          # card bins 1-3 ... 256-511
WALL_EDGES = np.r_[0.0, np.logspace(1, 5, 33)]                      # 0-10 s, then log bins to ~28 h
MIN_WELL = 10
MIN_BIN_N = 30
GRID = np.logspace(-4, np.log10(2.0), 161)                           # gamma grid (per call)
VEC = {"style_resid_period": "style_resid_period32", "white32": "white32"}
VARIANTS = [("bge_small", "style_resid_period"), ("gte_modernbert", "style_resid_period"), ("bge_small", "white32")]


# ============================================================================================ loading
@dataclass
class Data:
    goal: int
    st: pl.DataFrame               # sorted by agent, t; column i = row in Z
    Z: np.ndarray                  # (n, 32)
    X: np.ndarray                  # deviations from the leave-day-out well (0 where undefined)
    ok: np.ndarray                 # well defined
    planes: dict                   # key -> basis (32 x d) for the model in use
    texts: dict                    # key -> unit text vector
    model: str = "bge_small"
    extra: dict = field(default_factory=dict)


def load_planes(goal: int, model: str) -> tuple[dict, dict]:
    z = np.load(DATA / f"G{goal:02d}" / "planes.npz")
    planes, texts = {}, {}
    for k in z.files:
        m, *rest = k.split("|")
        if m != model:
            continue
        if rest[0] == "E":
            planes[rest[1]] = z[k]
        else:
            texts[rest[0]] = z[k]
    return planes, texts


def load(goal: int, model: str = "bge_small", variant: str = "style_resid_period", Z_override=None, st=None) -> Data:
    st = pl.read_parquet(DATA / f"G{goal:02d}" / "statements.parquet") if st is None else st
    if Z_override is None:
        st = st.sort("agent", "t", maintain_order=True)
    if "i" in st.columns:
        st = st.drop("i")
    st = st.with_row_index("i")
    if Z_override is None:
        V = np.load(SH / f"embeddings/statements_{VEC[variant]}_{model}.npy", mmap_mode="r")
        Z = np.asarray(V[st["srow"].to_numpy()], dtype=np.float64)
    else:
        Z = Z_override
    planes, texts = load_planes(goal, model)
    H, ok = wells(st, Z)
    X = np.where(ok[:, None], Z - np.nan_to_num(H), 0.0)
    return Data(goal=goal, st=st, Z=Z, X=X, ok=ok, planes=planes, texts=texts, model=model)


def wells(st: pl.DataFrame, Z: np.ndarray, min_n: int = MIN_WELL):
    """Leave-day-out agent mean over all loaded statements (one goal period)."""
    a = st["agent"].to_numpy()
    d = st["pt_date"].to_numpy()
    H = np.full_like(Z, np.nan)
    ok = np.zeros(len(a), bool)
    for ag in np.unique(a):
        ia = np.flatnonzero(a == ag)
        tot = Z[ia].sum(0)
        n = len(ia)
        for dd in np.unique(d[ia]):
            idd = ia[d[ia] == dd]
            m = n - len(idd)
            if m >= min_n:
                H[idd] = (tot - Z[idd].sum(0)) / m
                ok[idd] = True
    return H, ok


def subset(D: Data, units: list[str]) -> Data:
    """Rows of the given units; wells stay period-level (computed on the full load)."""
    m = D.st["unit_id"].is_in(units).to_numpy()
    st = D.st.filter(pl.Series(m)).drop("i").with_row_index("i")
    return Data(goal=D.goal, st=st, Z=D.Z[m], X=D.X[m], ok=D.ok[m], planes=D.planes, texts=D.texts, model=D.model,
                extra=dict(D.extra))


# ============================================================================================ projectors
def proj(B: np.ndarray) -> np.ndarray:
    B = np.atleast_2d(B)
    if B.shape[0] != DIM:
        B = B.T
    Q, _ = np.linalg.qr(B)
    return Q @ Q.T


def haar_planes(d: int, n: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    out = np.zeros((n, DIM, DIM))
    for k in range(n):
        Q, R = np.linalg.qr(rng.normal(size=(DIM, d)))
        out[k] = Q @ Q.T
    return out


# ============================================================================================ accumulators
@dataclass
class Acc:
    keys: list                     # (unit, agent, day, plane) per agent-day group
    unit: np.ndarray
    agent: np.ndarray
    day: np.ndarray
    plane: np.ndarray
    M: np.ndarray                  # (n_ad, n_cb, 1024) sym sum of x x'^T over own pairs per call-lag bin
    N: np.ndarray                  # (n_ad, n_cb)
    T: np.ndarray                  # (n_ad, n_cb) sum of tau
    NW: np.ndarray                 # (n_ad, n_cb, n_wb) own-pair counts by wall-lag bin
    G0: np.ndarray                 # (n_ad, 1024) sum of x x^T (lag 0 second moment)
    n0: np.ndarray                 # (n_ad,)
    Mx: np.ndarray                 # (n_wb, 1024) cross-agent sums (same room, same day), whole unit
    Nx: np.ndarray                 # (n_wb,)


def ad_groups(D: Data) -> pl.DataFrame:
    st = D.st.filter(pl.Series(D.ok))
    return (st.group_by("unit_id", "agent", "pt_date", "plane", maintain_order=True).agg(pl.col("i"))
            .sort("unit_id", "agent", "pt_date", "plane"))


def _bin(v, edges):
    b = np.searchsorted(edges, v, "right") - 1
    b[(v < edges[0]) | (v >= edges[-1])] = -1
    return b


def _window_pair_sums(tt: np.ndarray, Xs: np.ndarray):
    """For time-sorted rows: per wall-lag bin, sym sum of x_a x_b^T over unordered pairs (a before b) and counts.
    Window sums of a cumulative sum: O(n * 32^2) per bin."""
    n_wb = len(WALL_EDGES) - 1
    n = len(tt)
    C = np.vstack([np.zeros((1, DIM)), np.cumsum(Xs, 0)])
    ar = np.arange(n)
    S = np.zeros((n_wb, DIM * DIM))
    N = np.zeros(n_wb)
    for b in range(n_wb):
        lo, hi = WALL_EDGES[b], WALL_EDGES[b + 1]
        j0 = np.maximum(np.searchsorted(tt, tt + lo, "left"), ar + 1)
        j1 = np.maximum(np.searchsorted(tt, tt + hi, "left"), j0)
        cnt = j1 - j0
        if cnt.sum() == 0:
            continue
        Wn = C[j1] - C[j0]
        M = Xs.T @ Wn
        S[b] = (0.5 * (M + M.T)).ravel()
        N[b] = cnt.sum()
    return S, N


def accumulate(D: Data) -> Acc:
    g = ad_groups(D)
    X = D.X
    n_ad, n_cb, n_wb = g.height, len(CALL_EDGES) - 1, len(WALL_EDGES) - 1
    M = np.zeros((n_ad, n_cb, DIM * DIM))
    N = np.zeros((n_ad, n_cb))
    T = np.zeros((n_ad, n_cb))
    NW = np.zeros((n_ad, n_cb, n_wb))
    G0 = np.zeros((n_ad, DIM * DIM))
    n0 = np.zeros(n_ad)
    nn = D.st["n"].to_numpy().astype(float)
    t = D.st["t"].dt.epoch("us").to_numpy() / 1e6
    for row, idx in enumerate(g["i"].to_list()):
        idx = np.asarray(idx)
        Xi = X[idx]
        G0[row] = (Xi.T @ Xi).ravel()
        n0[row] = len(idx)
        if len(idx) < 2:
            continue
        ii, jj = np.triu_indices(len(idx), 1)
        tau = np.abs(nn[idx][jj] - nn[idx][ii])
        cb = _bin(tau, CALL_EDGES)
        keep = cb >= 0
        if not keep.any():
            continue
        ii, jj, tau, cb = ii[keep], jj[keep], tau[keep], cb[keep]
        wl = np.abs(t[idx][jj] - t[idx][ii])
        wb = np.clip(_bin(wl, WALL_EDGES), 0, n_wb - 1)
        for c in np.unique(cb):
            m = cb == c
            A, B = Xi[ii[m]], Xi[jj[m]]
            S = A.T @ B
            M[row, c] = (0.5 * (S + S.T)).ravel()
            N[row, c] = m.sum()
            T[row, c] = tau[m].sum()
            NW[row, c] = np.bincount(wb[m], minlength=n_wb)
    # cross-agent covariance by wall lag (same unit, day and room)
    Mx = np.zeros((n_wb, DIM * DIM))
    Nx = np.zeros(n_wb)
    st = D.st.filter(pl.Series(D.ok))
    room = st["room"].fill_null(-1).to_numpy()
    agents_all = D.st["agent"].to_numpy()
    for (u, d, r), grp in st.with_columns(pl.Series("rm", room)).group_by("unit_id", "pt_date", "rm"):
        idx = grp["i"].to_numpy()
        if len(idx) < 2:
            continue
        o = np.argsort(t[idx], kind="stable")
        idx = idx[o]
        S_all, N_all = _window_pair_sums(t[idx], X[idx])
        ag = agents_all[idx]
        for a_ in np.unique(ag):
            k = np.flatnonzero(ag == a_)
            if len(k) < 2:
                continue
            S_a, N_a = _window_pair_sums(t[idx][k], X[idx][k])
            S_all -= S_a
            N_all -= N_a
        Mx += S_all
        Nx += N_all
    return Acc(keys=list(zip(g["unit_id"], g["agent"], g["pt_date"], g["plane"])), unit=g["unit_id"].to_numpy(),
               agent=g["agent"].to_numpy(), day=g["pt_date"].to_numpy(), plane=g["plane"].to_numpy(), M=M, N=N, T=T,
               NW=NW, G0=G0, n0=n0, Mx=Mx, Nx=Nx)


def acc_subset(A: Acc, mask: np.ndarray) -> Acc:
    """Agent-day subset; the cross-agent sums stay those of the full accumulation (a ruler)."""
    return Acc(keys=[k for k, m in zip(A.keys, mask) if m], unit=A.unit[mask], agent=A.agent[mask], day=A.day[mask],
               plane=A.plane[mask], M=A.M[mask], N=A.N[mask], T=A.T[mask], NW=A.NW[mask], G0=A.G0[mask],
               n0=A.n0[mask], Mx=A.Mx, Nx=A.Nx)


# ============================================================================================ subspace profiles
def cx_values(A: Acc, Pflat: np.ndarray) -> np.ndarray:
    """Cross-agent covariance per wall bin for each projector (n_wb, n_p); sparse bins filled from the nearest valid."""
    val = (A.Mx @ Pflat.T) / np.maximum(A.Nx, 1)[:, None]
    good = A.Nx >= MIN_BIN_N
    if not good.any():
        return np.zeros_like(val)
    gi = np.flatnonzero(good)
    near = gi[np.abs(np.arange(len(A.Nx))[:, None] - gi[None, :]).argmin(1)]
    return val[near]


def subspace_sums(A: Acc, P: np.ndarray, idx: np.ndarray | None = None, corrected: bool = True) -> np.ndarray:
    """S[ad, cb, p] = sum over own pairs of <P x, P x'> (minus the cross-agent covariance at the pair's wall lag).
    P: (n_p, 32, 32). idx None: every projector for every agent-day. idx (n_ad,): one projector per agent-day
    (returns n_p = 1)."""
    Pf = P.reshape(P.shape[0], -1)
    if idx is None:
        S = A.M @ Pf.T                                            # (n_ad, n_cb, n_p)
        if corrected:
            Cx = cx_values(A, Pf)                                  # (n_wb, n_p)
            S = S - np.einsum("acw,wp->acp", A.NW, Cx)
        return S
    S = np.zeros(A.M.shape[:2] + (1,))
    Cx = cx_values(A, Pf) if corrected else None
    for k in np.unique(idx):
        m = idx == k
        S[m, :, 0] = A.M[m] @ Pf[k]
        if corrected:
            S[m, :, 0] -= A.NW[m] @ Cx[:, k]
    return S


def var_sums(A: Acc, P: np.ndarray, idx: np.ndarray | None = None) -> np.ndarray:
    """Lag-0 second moment along each projector, per agent-day: (n_ad, n_p)."""
    Pf = P.reshape(P.shape[0], -1)
    if idx is None:
        return A.G0 @ Pf.T
    out = np.zeros((A.G0.shape[0], 1))
    for k in np.unique(idx):
        m = idx == k
        out[m, 0] = A.G0[m] @ Pf[k]
    return out


def profiles(S: np.ndarray, A: Acc, w: np.ndarray | None = None):
    """Bin means (n_cb, n_p), cluster SEs (agent-day), bin-mean tau, counts."""
    w = np.ones(S.shape[0]) if w is None else w
    Nb = (w[:, None] * A.N).sum(0)
    Tb = (w[:, None] * A.T).sum(0)
    Sb = np.einsum("a,acp->cp", w, S)
    mean = Sb / np.maximum(Nb, 1)[:, None]
    R = S - mean[None] * A.N[:, :, None]
    var = np.einsum("a,acp->cp", w, R ** 2) / np.maximum(Nb, 1)[:, None] ** 2
    tau = Tb / np.maximum(Nb, 1)
    return tau, mean, np.sqrt(var), Nb


def grid_fit(tau: np.ndarray, Y: np.ndarray, SE: np.ndarray):
    """Weighted LS of y = A exp(-g tau) + B over a log grid of g, vectorized over the columns of Y (n_bins, n_p).
    Returns g, A, B, chi2, edge flag (-1 at the slow edge, +1 at the fast edge, 0 inside); NaN where < 4 bins."""
    n_b, n_p = Y.shape
    W = np.where(np.isfinite(SE) & (SE > 0) & np.isfinite(Y), 1.0 / np.maximum(SE, 1e-300) ** 2, 0.0)
    Yz = np.where(W > 0, Y, 0.0)
    nbins = (W > 0).sum(0)
    E = np.exp(-GRID[:, None] * tau[None, :])                          # (n_g, n_b)
    sw = W.sum(0)
    swy = (W * Yz).sum(0)
    swe = E @ W                                                        # (n_g, n_p)
    swee = (E ** 2) @ W
    swey = E @ (W * Yz)
    det = swee * sw[None] - swe ** 2
    A = (swey * sw[None] - swe * swy[None]) / np.where(np.abs(det) > 0, det, np.nan)
    B = (swy[None] - A * swe) / np.where(sw > 0, sw, np.nan)[None]
    swyy = (W * Yz ** 2).sum(0)
    chi2 = swyy[None] - 2 * A * swey - 2 * B * swy[None] + A ** 2 * swee + 2 * A * B * swe + B ** 2 * sw[None]
    chi2 = np.where(np.isfinite(chi2), chi2, np.inf)
    k = chi2.argmin(0)
    lg = np.log(GRID)
    g = GRID[k].copy()
    inner = (k > 0) & (k < len(GRID) - 1)
    cols = np.flatnonzero(inner)
    if len(cols):
        c0, c1, c2 = chi2[k[cols] - 1, cols], chi2[k[cols], cols], chi2[k[cols] + 1, cols]
        den = c0 - 2 * c1 + c2
        off = np.where(den > 0, 0.5 * (c0 - c2) / np.where(den > 0, den, 1), 0.0)
        g[cols] = np.exp(lg[k[cols]] + np.clip(off, -1, 1) * (lg[1] - lg[0]))
    edge = np.where(k == 0, -1, np.where(k == len(GRID) - 1, 1, 0))
    Aout = A[k, np.arange(n_p)]
    Bout = B[k, np.arange(n_p)]
    bad = nbins < 4
    g = np.where(bad, np.nan, g)
    return g, Aout, Bout, chi2[k, np.arange(n_p)], edge


def fit_subspaces(S: np.ndarray, A: Acc, w: np.ndarray | None = None):
    tau, mean, se, Nb = profiles(S, A, w)
    se = np.where(Nb[:, None] >= MIN_BIN_N, se, np.nan)
    return grid_fit(tau, mean, se) + (tau, mean, se)


def boot_weights(groups: np.ndarray, B: int, seed: int) -> np.ndarray:
    """Block bootstrap multiplicity weights over the levels of `groups` (B x n)."""
    rng = np.random.default_rng(seed)
    lv, inv = np.unique(groups, return_inverse=True)
    out = np.zeros((B, len(groups)))
    for b in range(B):
        cnt = np.bincount(rng.integers(0, len(lv), len(lv)), minlength=len(lv))
        out[b] = cnt[inv]
    return out


def rate_ratio(S_par: np.ndarray, S_perp: np.ndarray, A: Acc, Bw: np.ndarray | None):
    """gamma_par, gamma_perp, rho_A = gamma_perp / gamma_par, plateau shares; bootstrap over agent-days.
    S_par, S_perp: (n_ad, n_cb, n_p) with matched columns (one plane each)."""
    gp, Ap, Bp, _, ep, tau, mp, sp = fit_subspaces(S_par, A)
    gq, Aq, Bq, _, eq, _, mq, sq = fit_subspaces(S_perp, A)
    out = {"g_par": gp, "g_perp": gq, "rho": gq / gp, "edge_par": ep, "edge_perp": eq,
           "plateau_par": Bp / (Ap + Bp), "plateau_perp": Bq / (Aq + Bq), "tau": tau, "C_par": mp, "C_perp": mq,
           "se_par": sp, "se_perp": sq}
    if Bw is not None:
        bp, bq = [], []
        for w in Bw:
            bp.append(fit_subspaces(S_par, A, w)[0])
            bq.append(fit_subspaces(S_perp, A, w)[0])
        bp, bq = np.array(bp), np.array(bq)
        out["boot_g_par"], out["boot_g_perp"] = bp, bq
        out["boot_rho"] = bq / bp
    return out


# ============================================================================================ day scale (O3)
@dataclass
class DayAcc:
    agent: np.ndarray              # one row per (agent, plane) group used
    plane: np.ndarray
    Mnum: np.ndarray               # (n_g, 1024) sum over consecutive day pairs of sym(xbar_d xbar_d'^T)
    ME1: np.ndarray                # split-half products of the first day of each pair
    ME2: np.ndarray                # split-half products of the second day
    npairs: np.ndarray


def day_accumulate(D: Data, unit_days: list[str], min_stmt: int = 4, centre: bool = False,
                   arm_of=None) -> DayAcc:
    """Consecutive (in the unit's day list) day pairs per agent; wells leave the pair out (period-level, or within the
    arm when arm_of(agent, day) gives an arm label). centre=True subtracts the other agents' mean day deviation (variant).
    Pairs whose two days carry different planes are skipped."""
    st = D.st
    a = st["agent"].to_numpy()
    d = st["pt_date"].to_numpy()
    pln = st["plane"].to_numpy()
    half = st["half"].to_numpy()
    Z = D.Z
    if arm_of is not None:
        arm = np.array([arm_of(x, y) for x, y in zip(a, d)])
    else:
        arm = np.zeros(len(a), dtype=object)
    days = list(unit_days)
    # agent-day sums
    key_sum, key_n, key_h = {}, {}, {}
    for k in range(len(a)):
        kk = (a[k], d[k], pln[k], arm[k])
        if kk not in key_sum:
            key_sum[kk] = np.zeros(DIM); key_n[kk] = 0
            key_h[kk] = [np.zeros(DIM), np.zeros(DIM), 0, 0]
        key_sum[kk] += Z[k]; key_n[kk] += 1
        hh = key_h[kk]; hh[half[k]] += Z[k]; hh[2 + half[k]] += 1
    # agent totals per arm
    tot, totn = {}, {}
    for (ag, dd, p, ar), s in key_sum.items():
        tot[(ag, ar)] = tot.get((ag, ar), np.zeros(DIM)) + s
        totn[(ag, ar)] = totn.get((ag, ar), 0) + key_n[(ag, dd, p, ar)]
    # per-day mean deviation of all agents (for the centred variant), using leave-day-out wells
    groups = {}
    for (ag, dd, p, ar) in key_sum:
        groups.setdefault((ag, p, ar), []).append(dd)
    pairs = []
    for (ag, p, ar), dl in groups.items():
        dl = sorted(set(dl) & set(days), key=days.index)
        for x, y in zip(dl[:-1], dl[1:]):
            if days.index(y) - days.index(x) != 1:
                continue
            pairs.append((ag, p, ar, x, y))
    centre_vec = {}
    if centre:
        for dd in days:
            vs = []
            for (ag, d2, p, ar), s in key_sum.items():
                if d2 != dd:
                    continue
                m = totn[(ag, ar)] - key_n[(ag, d2, p, ar)]
                if m >= MIN_WELL and key_n[(ag, d2, p, ar)] >= min_stmt:
                    h = (tot[(ag, ar)] - s) / m
                    vs.append((ag, s / key_n[(ag, d2, p, ar)] - h))
            centre_vec[dd] = vs
    rows = {}
    for ag, p, ar, x, y in pairs:
        kx, ky = (ag, x, p, ar), (ag, y, p, ar)
        if key_n[kx] < min_stmt or key_n[ky] < min_stmt:
            continue
        hx, hy = key_h[kx], key_h[ky]
        if min(hx[2], hx[3], hy[2], hy[3]) < 2:
            continue
        m = totn[(ag, ar)] - key_n[kx] - key_n[ky]
        if m < MIN_WELL:
            continue
        h = (tot[(ag, ar)] - key_sum[kx] - key_sum[ky]) / m
        xb = key_sum[kx] / key_n[kx] - h
        yb = key_sum[ky] / key_n[ky] - h
        xa, xb2 = hx[0] / hx[2] - h, hx[1] / hx[3] - h
        ya, yb2 = hy[0] / hy[2] - h, hy[1] / hy[3] - h
        if centre:
            cx = [v for (o, v) in centre_vec.get(x, []) if o != ag]
            cy = [v for (o, v) in centre_vec.get(y, []) if o != ag]
            if len(cx) < 2 or len(cy) < 2:
                continue
            mx, my = np.mean(cx, 0), np.mean(cy, 0)
            xb, yb, xa, xb2, ya, yb2 = xb - mx, yb - my, xa - mx, xb2 - mx, ya - my, yb2 - my
        r = rows.setdefault((ag, p), [np.zeros(DIM * DIM), np.zeros(DIM * DIM), np.zeros(DIM * DIM), 0])
        S = np.outer(xb, yb); r[0] += (0.5 * (S + S.T)).ravel()
        S = np.outer(xa, xb2); r[1] += (0.5 * (S + S.T)).ravel()
        S = np.outer(ya, yb2); r[2] += (0.5 * (S + S.T)).ravel()
        r[3] += 1
    ks = sorted(rows)
    if not ks:
        z = np.zeros((0, DIM * DIM))
        return DayAcc(np.zeros(0, int), np.zeros(0, object), z, z, z, np.zeros(0))
    return DayAcc(agent=np.array([k[0] for k in ks]), plane=np.array([k[1] for k in ks], dtype=object),
                  Mnum=np.array([rows[k][0] for k in ks]), ME1=np.array([rows[k][1] for k in ks]),
                  ME2=np.array([rows[k][2] for k in ks]), npairs=np.array([rows[k][3] for k in ks], float))


def day_persistence(DA: DayAcc, P: np.ndarray, idx: np.ndarray | None = None, w: np.ndarray | None = None):
    """P(1) per projector: tr(P Mnum) / sqrt(tr(P ME1) tr(P ME2)), sums over groups (weights w)."""
    Pf = P.reshape(P.shape[0], -1)
    w = np.ones(len(DA.agent)) if w is None else w
    if idx is None:
        num = w @ (DA.Mnum @ Pf.T); e1 = w @ (DA.ME1 @ Pf.T); e2 = w @ (DA.ME2 @ Pf.T)
    else:
        num = np.zeros(1); e1 = np.zeros(1); e2 = np.zeros(1)
        for k in np.unique(idx):
            m = idx == k
            num += w[m] @ (DA.Mnum[m] @ Pf[k]); e1 += w[m] @ (DA.ME1[m] @ Pf[k]); e2 += w[m] @ (DA.ME2[m] @ Pf[k])
    den = np.sqrt(np.clip(e1, 0, None) * np.clip(e2, 0, None))
    return np.where(den > 0, num / np.where(den > 0, den, 1), np.nan)


@dataclass
class VarioAcc:
    agent: np.ndarray
    plane: np.ndarray
    V1: np.ndarray                 # (n_g, 1024) sum over lag-1 day pairs of noise-corrected (zbar_d - zbar_d')(...)^T
    V2: np.ndarray                 # the same over day pairs at lag >= 2
    c1: np.ndarray
    c2: np.ndarray


def day_vario(D: Data, unit_days: list[str], min_stmt: int = 4, centre: bool = False) -> VarioAcc:
    """Amendment A1 (O3): noise-corrected day-level variogram. The agent's well cancels in day differences, so no well
    error enters. Noise of a day mean from the split halves: (zbar_a - zbar_b)(...)^T * n_a n_b / n^2.
    centre=True subtracts the other agents' mean day offset (agent-mean-centred) on each day (variant)."""
    st = D.st
    a = st["agent"].to_numpy()
    d = st["pt_date"].to_numpy()
    pln = st["plane"].to_numpy()
    half = st["half"].to_numpy()
    Z = D.Z
    days = list(unit_days)
    S, n, H = {}, {}, {}
    for k in range(len(a)):
        kk = (a[k], d[k], pln[k])
        if kk not in S:
            S[kk] = np.zeros(DIM); n[kk] = 0; H[kk] = [np.zeros(DIM), np.zeros(DIM), 0, 0]
        S[kk] += Z[k]; n[kk] += 1
        h = H[kk]; h[half[k]] += Z[k]; h[2 + half[k]] += 1
    good = {kk for kk in S if n[kk] >= min_stmt and min(H[kk][2], H[kk][3]) >= 2 and kk[1] in days}
    mean = {kk: S[kk] / n[kk] for kk in good}
    noise = {}
    for kk in good:
        h = H[kk]
        dv = h[0] / h[2] - h[1] / h[3]
        noise[kk] = np.outer(dv, dv).ravel() * h[2] * h[3] / n[kk] ** 2
    if centre:
        amean = {}
        for kk in good:
            amean.setdefault(kk[0], []).append(mean[kk])
        amean = {k: np.mean(v, 0) for k, v in amean.items()}
        off = {}
        for kk in good:
            off.setdefault(kk[1], []).append((kk[0], mean[kk] - amean[kk[0]]))
    groups = {}
    for kk in good:
        groups.setdefault((kk[0], kk[2]), []).append(kk[1])
    rows = {}
    for (ag, p), dl in groups.items():
        dl = sorted(dl, key=days.index)
        for i1 in range(len(dl)):
            for i2 in range(i1 + 1, len(dl)):
                x, y = dl[i1], dl[i2]
                lag = days.index(y) - days.index(x)
                kx, ky = (ag, x, p), (ag, y, p)
                dv = mean[kx] - mean[ky]
                if centre:
                    cx = [v for (o, v) in off[x] if o != ag]
                    cy = [v for (o, v) in off[y] if o != ag]
                    if len(cx) < 2 or len(cy) < 2:
                        continue
                    dv = dv - (np.mean(cx, 0) - np.mean(cy, 0))
                val = np.outer(dv, dv).ravel() - noise[kx] - noise[ky]
                r = rows.setdefault((ag, p), [np.zeros(DIM * DIM), np.zeros(DIM * DIM), 0, 0])
                if lag == 1:
                    r[0] += val; r[2] += 1
                else:
                    r[1] += val; r[3] += 1
    ks = sorted(rows)
    if not ks:
        z = np.zeros((0, DIM * DIM))
        return VarioAcc(np.zeros(0, int), np.zeros(0, object), z, z, np.zeros(0), np.zeros(0))
    return VarioAcc(agent=np.array([k[0] for k in ks]), plane=np.array([k[1] for k in ks], dtype=object),
                    V1=np.array([rows[k][0] for k in ks]), V2=np.array([rows[k][1] for k in ks]),
                    c1=np.array([rows[k][2] for k in ks], float), c2=np.array([rows[k][3] for k in ks], float))


def vario_persistence(VA: VarioAcc, P: np.ndarray, idx: np.ndarray | None = None, w=None, complement=False):
    """P_vg(1) = 1 - G(1)/G(>=2), G = per-pair noise-corrected semivariogram along the projector (or its complement)."""
    w = np.ones(len(VA.agent)) if w is None else w
    If = np.eye(DIM).ravel()
    Pf = P.reshape(P.shape[0], -1)
    if idx is None:
        Q = (If[None, :] - Pf) if complement else Pf
        g1 = w @ (VA.V1 @ Q.T); g2 = w @ (VA.V2 @ Q.T)
    else:
        g1 = np.zeros(1); g2 = np.zeros(1)
        for k in np.unique(idx):
            m = idx == k
            Q = (If - Pf[k]) if complement else Pf[k]
            g1 += w[m] @ (VA.V1[m] @ Q); g2 += w[m] @ (VA.V2[m] @ Q)
    c1, c2 = (w * VA.c1).sum(), (w * VA.c2).sum()
    if c1 == 0 or c2 == 0:
        return np.full(np.shape(g1), np.nan)
    G1, G2 = g1 / c1, g2 / c2
    return np.where(G2 > 0, 1 - G1 / np.where(G2 > 0, G2, 1), np.nan)


# ============================================================================================ pooling
def dl_pool(est: np.ndarray, se: np.ndarray):
    """DerSimonian-Laird random-effects pool. Returns (mu, se_mu, tau2, I2, k)."""
    est, se = np.asarray(est, float), np.asarray(se, float)
    m = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[m], se[m]
    k = len(est)
    if k == 0:
        return np.nan, np.nan, np.nan, np.nan, 0
    w = 1 / se ** 2
    mu_f = (w * est).sum() / w.sum()
    Q = (w * (est - mu_f) ** 2).sum()
    c = w.sum() - (w ** 2).sum() / w.sum()
    tau2 = max(0.0, (Q - (k - 1)) / c) if k > 1 and c > 0 else 0.0
    ws = 1 / (se ** 2 + tau2)
    mu = (ws * est).sum() / ws.sum()
    I2 = max(0.0, (Q - (k - 1)) / Q) if Q > 0 and k > 1 else 0.0
    return float(mu), float(np.sqrt(1 / ws.sum())), float(tau2), float(I2), k


def ln_se(boot: np.ndarray) -> float:
    b = boot[np.isfinite(boot) & (boot > 0)]
    return float(np.std(np.log(b))) if len(b) >= 20 else np.nan


# ============================================================================================ one unit
def plane_index(A: Acc, planes: dict, keys: list | None = None):
    """Projector stack for the planes keyed by the agent-day plane labels; idx per agent-day."""
    keys = sorted(set(A.plane.tolist())) if keys is None else keys
    P = np.array([proj(planes[k]) for k in keys])
    idx = np.array([keys.index(p) for p in A.plane])
    dims = np.array([planes[k].shape[1] if planes[k].ndim == 2 else 1 for k in keys])
    return P, idx, dims


def _pct(v: float, band: np.ndarray) -> float:
    band = band[np.isfinite(band)]
    if not np.isfinite(v) or len(band) == 0:
        return np.nan
    return float(np.mean(band < v))


def ratio_summary(rr: dict, prefix: str) -> dict:
    out = {f"{prefix}g_par": float(rr["g_par"][0]), f"{prefix}g_perp": float(rr["g_perp"][0]),
           f"{prefix}rho": float(rr["rho"][0]), f"{prefix}edge_par": int(rr["edge_par"][0]),
           f"{prefix}edge_perp": int(rr["edge_perp"][0]),
           f"{prefix}plateau_par": float(rr["plateau_par"][0]), f"{prefix}plateau_perp": float(rr["plateau_perp"][0])}
    if "boot_rho" in rr:
        b = rr["boot_rho"][:, 0]
        fin = b[np.isfinite(b)]
        out[f"{prefix}ci90"] = np.percentile(fin, [5, 95]).tolist() if len(fin) > 20 else [np.nan, np.nan]
        out[f"{prefix}ci95"] = np.percentile(fin, [2.5, 97.5]).tolist() if len(fin) > 20 else [np.nan, np.nan]
        out[f"{prefix}se_ln"] = ln_se(b)
        out[f"{prefix}frac_edge_par_boot"] = float(np.mean(rr["boot_g_par"][:, 0] <= GRID[0] * 1.0001))
    return out


def analyze_unit(D: Data, A: Acc, unit_days: list[str], B: int = 200, n_rand: int = 200, seed: int = 0,
                 extra_planes: dict | None = None, day_scale: bool = True, centre_variant: bool = True,
                 raw_variant: bool = True) -> dict:
    """Every H141 statistic on one unit. D is the unit's Data (wells period-level), A its accumulators.
    extra_planes: name -> (planes dict keyed like A.plane, or a dict keyed by day with key '__by_day__')."""
    out = {"n_ad": int(len(A.agent)), "n_statements": int(A.n0.sum()), "n_agents": int(len(np.unique(A.agent))),
           "n_days": len(unit_days)}
    Bw = boot_weights(np.arange(len(A.agent)), B, seed) if B else None
    I = np.eye(DIM)[None]
    S_tr = subspace_sums(A, I)                                    # (n_ad, n_cb, 1), corrected
    S_tr_raw = subspace_sums(A, I, corrected=False)
    V_tr = var_sums(A, I)[:, 0]
    # ---- text plane E (primary)
    P, idx, dims = plane_index(A, D.planes)
    dE = int(dims[0])
    out["d_E"] = dE
    S_par = subspace_sums(A, P, idx)
    rr = rate_ratio(S_par, S_tr - S_par, A, Bw)
    out.update(ratio_summary(rr, ""))
    out["C_tau"] = rr["tau"].tolist()
    out["C_par"] = (rr["C_par"][:, 0] / dE).tolist()
    out["C_perp"] = (rr["C_perp"][:, 0] / (DIM - dE)).tolist()
    out["C_par_se"] = (rr["se_par"][:, 0] / dE).tolist()
    out["C_perp_se"] = (rr["se_perp"][:, 0] / (DIM - dE)).tolist()
    if raw_variant:
        S_par_raw = subspace_sums(A, P, idx, corrected=False)
        rraw = rate_ratio(S_par_raw, S_tr_raw - S_par_raw, A, Bw)
        out.update(ratio_summary(rraw, "raw_"))
    # ---- O4 variance ratio (lag 0) and the noise-free variant (lag bin 1-3, drive-corrected)
    V_par = var_sums(A, P, idx)[:, 0]

    def vratio(w):
        vp = (w * V_par).sum() / dE
        vq = (w * (V_tr - V_par)).sum() / (DIM - dE)
        return vp / vq if vq > 0 else np.nan
    out["V_A"] = float(vratio(np.ones(len(V_par))))
    out["V_A_lag1"] = float((rr["C_par"][0, 0] / dE) / (rr["C_perp"][0, 0] / (DIM - dE)))
    if Bw is not None:
        vb = np.array([vratio(w) for w in Bw])
        out["V_A_ci95"] = np.percentile(vb, [2.5, 97.5]).tolist()
        out["V_A_se_ln"] = ln_se(vb)
    # ---- random-plane band (same dimension)
    R = haar_planes(dE, n_rand, seed + 7)
    S_r = subspace_sums(A, R)
    g_r = fit_subspaces(S_r, A)[0]
    g_rq = fit_subspaces(S_tr - S_r, A)[0]
    rho_r = g_rq / g_r
    out["rand_rho_q"] = np.nanpercentile(rho_r, [5, 50, 90, 95]).tolist()
    out["rand_pct"] = _pct(out["rho"], rho_r)
    out["rand_V_q"] = None
    Vr = (var_sums(A, R).sum(0) / dE) / ((V_tr.sum() - var_sums(A, R).sum(0)) / (DIM - dE))
    out["rand_V_q"] = np.percentile(Vr, [5, 50, 95]).tolist()
    out["rand_V_pct"] = _pct(out["V_A"], Vr)
    # ---- R-modes benchmark: top-d_E principal subspace of the unit's deviations, cross-fitted on other days
    days = sorted(set(A.day.tolist()))
    if len(days) >= 2:
        Gd = {d: A.G0[A.day == d].sum(0).reshape(DIM, DIM) for d in days}
        Gall = sum(Gd.values())
        Ppca = []
        for d in days:
            w_, v_ = np.linalg.eigh(Gall - Gd[d])
            Ppca.append(v_[:, ::-1][:, :dE] @ v_[:, ::-1][:, :dE].T)
        Ppca = np.array(Ppca)
        idx_d = np.array([days.index(d) for d in A.day])
        S_pca = subspace_sums(A, Ppca, idx_d)
        rp = rate_ratio(S_pca, S_tr - S_pca, A, Bw)
        out.update(ratio_summary(rp, "pca_"))
        out["pca_rand_pct"] = _pct(out["pca_rho"], rho_r)
        # overlap of E with the principal subspace (mean squared cosine per dimension)
        out["pca_E_overlap"] = float(np.mean([np.trace(Ppca[idx_d[k]] @ P[idx[k]]) / dE for k in range(len(idx))]))
    # ---- extra planes (variants and natives)
    for name, spec in (extra_planes or {}).items():
        if "__by_day__" in spec:
            byd = spec["__by_day__"]
            keys = sorted(byd)
            Pk = np.array([proj(byd[k]) for k in keys])
            ix = np.array([keys.index(d) if d in byd else -1 for d in A.day])
            if (ix < 0).any():
                continue
            dk = byd[keys[0]].shape[1] if byd[keys[0]].ndim == 2 else 1
        else:
            Pk, ix, dd = plane_index(A, spec)
            dk = int(dd[0])
        S_k = subspace_sums(A, Pk, ix)
        rk = rate_ratio(S_k, S_tr - S_k, A, Bw if spec.get("__boot__", True) else None)
        out.update(ratio_summary(rk, f"{name}_"))
        out[f"{name}_d"] = dk
        if dk == dE:
            out[f"{name}_rand_pct"] = _pct(out[f"{name}_rho"], rho_r)
        else:
            Rk = haar_planes(dk, n_rand, seed + 11 + dk)
            S_rk = subspace_sums(A, Rk)
            rho_rk = fit_subspaces(S_tr - S_rk, A)[0] / fit_subspaces(S_rk, A)[0]
            out[f"{name}_rand_pct"] = _pct(out[f"{name}_rho"], rho_rk)
            out[f"{name}_rand_q"] = np.nanpercentile(rho_rk, [50, 90, 95]).tolist()
    # ---- O3 day scale
    if day_scale:
        for tag, centre in (("", False), ("cen_", True)):
            if centre and not centre_variant:
                continue
            DA = day_accumulate(D, unit_days, centre=centre)
            out[f"{tag}day_n_pairs"] = float(DA.npairs.sum())
            if DA.npairs.sum() < 3:
                continue
            Pd, idd, _ = plane_index_day(DA, D.planes)
            p_par = day_persistence(DA, Pd, idd)[0]
            p_tr = day_persistence(DA, I)[0]
            # complement: tr((1-P) M) = tr(M) - tr(P M), per group
            p_perp = _day_perp(DA, Pd, idd)
            out[f"{tag}P_par"], out[f"{tag}P_perp"] = float(p_par), float(p_perp)
            out[f"{tag}P_diff"] = float(p_par - p_perp)
            out[f"{tag}P_all"] = float(p_tr)
            Rb = haar_planes(dE, n_rand, seed + 7)
            pr = day_persistence(DA, Rb)
            prq = _day_perp_global(DA, Rb)
            out[f"{tag}P_rand_pct"] = _pct(out[f"{tag}P_diff"], pr - prq)
            out[f"{tag}P_rand_q"] = np.nanpercentile(pr - prq, [5, 50, 95]).tolist()
            if B:
                Wa = boot_weights(DA.agent, B, seed + 3)
                bd = np.array([day_persistence(DA, Pd, idd, w)[0] - _day_perp(DA, Pd, idd, w) for w in Wa])
                bp = np.array([day_persistence(DA, Pd, idd, w)[0] for w in Wa])
                bq = np.array([_day_perp(DA, Pd, idd, w) for w in Wa])
                out[f"{tag}P_diff_ci95"] = np.nanpercentile(bd, [2.5, 97.5]).tolist()
                out[f"{tag}P_diff_se"] = float(np.nanstd(bd))
                out[f"{tag}P_par_ci95"] = np.nanpercentile(bp, [2.5, 97.5]).tolist()
                out[f"{tag}P_perp_ci95"] = np.nanpercentile(bq, [2.5, 97.5]).tolist()
        # Amendment A1: noise-corrected day-level variogram (no well error)
        for tag, centre in (("vg_", False), ("vgcen_", True)):
            if centre and not centre_variant:
                continue
            VA = day_vario(D, unit_days, centre=centre)
            out[f"{tag}n_pairs1"], out[f"{tag}n_pairs2"] = float(VA.c1.sum()), float(VA.c2.sum())
            if VA.c1.sum() < 3 or VA.c2.sum() < 3:
                continue
            Pd, idd, _ = plane_index_day(VA, D.planes)
            p_par = vario_persistence(VA, Pd, idd)[0]
            p_perp = vario_persistence(VA, Pd, idd, complement=True)[0]
            out[f"{tag}P_par"], out[f"{tag}P_perp"], out[f"{tag}P_diff"] = float(p_par), float(p_perp), float(p_par - p_perp)
            out[f"{tag}P_all"] = float(vario_persistence(VA, I)[0])
            Rb = haar_planes(dE, n_rand, seed + 7)
            band = vario_persistence(VA, Rb) - vario_persistence(VA, Rb, complement=True)
            out[f"{tag}P_rand_pct"] = _pct(out[f"{tag}P_diff"], band)
            out[f"{tag}P_rand_q"] = np.nanpercentile(band, [5, 50, 95]).tolist()
            if B:
                Wa = boot_weights(VA.agent, B, seed + 5)
                bp = np.array([vario_persistence(VA, Pd, idd, w)[0] for w in Wa])
                bq = np.array([vario_persistence(VA, Pd, idd, w, complement=True)[0] for w in Wa])
                out[f"{tag}P_diff_ci95"] = np.nanpercentile(bp - bq, [2.5, 97.5]).tolist()
                out[f"{tag}P_diff_se"] = float(np.nanstd(bp - bq))
                out[f"{tag}P_par_ci95"] = np.nanpercentile(bp, [2.5, 97.5]).tolist()
                out[f"{tag}P_perp_ci95"] = np.nanpercentile(bq, [2.5, 97.5]).tolist()
    return out


def plane_index_day(DA: DayAcc, planes: dict):
    keys = sorted(set(DA.plane.tolist()))
    P = np.array([proj(planes[k]) for k in keys])
    idx = np.array([keys.index(p) for p in DA.plane])
    return P, idx, keys


def _day_perp(DA: DayAcc, P: np.ndarray, idx: np.ndarray, w=None) -> float:
    w = np.ones(len(DA.agent)) if w is None else w
    If = np.eye(DIM).ravel()
    num = w @ (DA.Mnum @ If); e1 = w @ (DA.ME1 @ If); e2 = w @ (DA.ME2 @ If)
    for k in np.unique(idx):
        m = idx == k
        Pf = P[k].ravel()
        num -= w[m] @ (DA.Mnum[m] @ Pf); e1 -= w[m] @ (DA.ME1[m] @ Pf); e2 -= w[m] @ (DA.ME2[m] @ Pf)
    den = np.sqrt(max(e1, 0) * max(e2, 0))
    return float(num / den) if den > 0 else np.nan


def _day_perp_global(DA: DayAcc, R: np.ndarray) -> np.ndarray:
    If = np.eye(DIM).ravel()
    Rf = R.reshape(R.shape[0], -1)
    num = DA.Mnum.sum(0) @ (If[:, None] - Rf.T)
    e1 = DA.ME1.sum(0) @ (If[:, None] - Rf.T)
    e2 = DA.ME2.sum(0) @ (If[:, None] - Rf.T)
    den = np.sqrt(np.clip(e1, 0, None) * np.clip(e2, 0, None))
    return np.where(den > 0, num / np.where(den > 0, den, 1), np.nan)
