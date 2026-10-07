"""H139 estimators: the two-rate split of an agent's own content autocovariance on the per-call clock.

Objects (card, Observables):
  h_i        leave-day-out well centre (agent's mean statement vector over the period's other non-reserved days; H130)
  x_B        z_B - h_i(day(B))
  C(tau)     O1: mean x_B . x_B' over same-agent-day pairs, tau = n_B' - n_B >= 1 call, in 14 lag bins.
             Drive-corrected (primary): minus the cross-agent covariance at the same wall lag (H130 A1 point 3),
             computed per room class (same room r, or different rooms).
  fits       O2: C(tau) = A_k (1-g_k)^tau + A_s (1-g_s)^tau + B (constrained: g_k fixed; free: all five free) and the
             one-rate fit A (1-g)^tau + B. Weighted least squares on bin means (weights 1/bootstrap variance). The
             model is averaged over each bin's real lag distribution (not evaluated at the bin-mean lag). Nonlinear
             rates are profiled on a grid; amplitudes are linear (exact WLS for each grid value).
  R_fast     O5: pairs at lags 1-7 calls that cross a forced reset vs pairs that do not, matched per (agent-day, bin).
Accumulators are per agent-day, so the agent-day block bootstrap within unit is a weighted sum.
Synthetic and real data go through the same functions.
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
DATA = ROOT / "data/processed/H139-two-rate-variance-split"

# O1 lag bins (calls): {1},{2},{3},{4-5},{6-7},{8-11},{12-15},{16-23},{24-31},{32-63},{64-127},{128-255},{256-511},{512-1023}
EDGES = np.array([1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 64, 128, 256, 512, 1024])
NB = len(EDGES) - 1
TAU_MAX = int(EDGES[-1])
FAST_BINS = np.arange(5)                      # lags 1-7 (O5)
SLOW_BINS = np.array([9, 10, 11])             # lags 32-255 (R_slow, as H130's R_C)
EDGES_S = np.array([0, 30, 60, 120, 240, 480, 960, 1920, 3840, 7680, 15360, 30720, 10 ** 6])   # wall lag (s)
MIN_WELL = 10
MIN_N = 30                                    # pairs per bin needed (H130)
VEC = {"style_resid_period": "style_resid_period32", "white32": "white32"}
GS_GRID = np.geomspace(3e-4, 0.08, 60)        # slow rate grid (well rates; H130 gamma_auto 0.0094)
G1_GRID = np.geomspace(3e-4, 1.0, 90)         # one-rate grid
GK_GRID = np.geomspace(0.02, 1.0, 40)         # free fast-rate grid


# ================================================================================ skeleton (no content)
@dataclass
class Skel:
    unit: str
    st: pl.DataFrame              # statements of the unit, sorted (agent, t), row index i
    rd: pl.DataFrame              # reads of these agent-days (reader, n, nf, srow_m, pt_date)
    calls: pl.DataFrame
    ad: np.ndarray                # agent-day id per statement
    ad_keys: list
    ad_day: np.ndarray            # day index per agent-day
    days: list
    # own pairs
    pa: np.ndarray = None
    pb: np.ndarray = None
    ptau: np.ndarray = None
    pbin: np.ndarray = None
    pad: np.ndarray = None
    pcross: np.ndarray = None     # crosses a forced reset
    pdt: np.ndarray = None        # wall lag (s) between the two statements
    pcls: np.ndarray = None       # room class of the pair for the drive correction
    hist: np.ndarray = None       # (NB, TAU_MAX+1) lag histogram per bin (all pairs)
    # cross-agent pairs (drive correction)
    xa: np.ndarray = None
    xb: np.ndarray = None
    xbin: np.ndarray = None
    xcls: np.ndarray = None
    xdt: np.ndarray = None
    ncls: int = 0
    rbar: float = np.nan          # reads per call (all calls of the unit's agents with statements; ledger count)
    rbar_talk: float = np.nan
    rbar_agent: dict = field(default_factory=dict)


def load_skeleton(period: str, unit: str | None, units: list[str] | None = None) -> Skel:
    root = DATA / period
    st = pl.read_parquet(root / "statements.parquet")
    rd = pl.read_parquet(root / "reads.parquet")
    calls = pl.read_parquet(root / "calls.parquet")
    us = [unit] if unit else units
    st = st.filter(pl.col("unit_id").is_in(us))
    rd = rd.filter(pl.col("unit_id").is_in(us))
    calls = calls.filter(pl.col("unit_id").is_in(us))
    return make_skeleton(st, rd, calls, unit or "+".join(us))


def make_skeleton(st: pl.DataFrame, rd: pl.DataFrame, calls: pl.DataFrame, name: str) -> Skel:
    st = st.sort("agent", "t").with_row_index("i")
    g = st.group_by("agent", "pt_date", maintain_order=True).agg(pl.col("i")).sort("agent", "pt_date")
    keys = list(zip(g["agent"].to_list(), g["pt_date"].to_list()))
    ad = np.zeros(st.height, np.int32)
    for r, idx in enumerate(g["i"].to_list()):
        ad[np.asarray(idx)] = r
    days = sorted(st["pt_date"].unique().to_list())
    dpos = {d: k for k, d in enumerate(days)}
    S = Skel(unit=name, st=st, rd=rd, calls=calls, ad=ad, ad_keys=keys,
             ad_day=np.array([dpos[d] for _, d in keys]), days=days)
    _own_pairs(S, g)
    _cross_pairs(S)
    # read rate per call: agents that have statements in the unit, all their calls on those days
    cl = calls.join(st.select("agent", "pt_date").unique(), on=["agent", "pt_date"], how="semi")
    S.rbar = float(cl["n_read"].mean())
    S.rbar_talk = float(cl.filter(pl.col("talk"))["n_read"].mean()) if cl["talk"].any() else np.nan
    S.rbar_agent = {a: float(v) for a, v in cl.group_by("agent").agg(pl.col("n_read").mean()).iter_rows()}
    return S


def _room_classes(S: Skel):
    rooms = sorted(S.st["room"].unique().to_list())
    return {r: k for k, r in enumerate(rooms)}, len(rooms)    # class len(rooms) = different rooms


def _own_pairs(S: Skel, g: pl.DataFrame):
    nn = S.st["n"].to_numpy()
    nf = S.st["nf"].to_numpy()
    t = S.st["t"].dt.epoch("us").to_numpy() / 1e6
    room = S.st["room"].to_numpy()
    rcls, nr = _room_classes(S)
    rc = np.array([rcls[r] for r in room])
    A, Bv, T, AD = [], [], [], []
    for r, idx in enumerate(g["i"].to_list()):
        idx = np.asarray(idx)
        if len(idx) < 2:
            continue
        ii, jj = np.triu_indices(len(idx), 1)
        a, b = idx[ii], idx[jj]
        tau = np.abs(nn[b] - nn[a])
        k = (tau >= 1) & (tau < TAU_MAX)
        A.append(a[k]); Bv.append(b[k]); T.append(tau[k]); AD.append(np.full(k.sum(), r))
    S.pa = np.concatenate(A).astype(np.int32)
    S.pb = np.concatenate(Bv).astype(np.int32)
    S.ptau = np.concatenate(T).astype(np.int32)
    S.pad = np.concatenate(AD).astype(np.int32)
    S.pbin = (np.searchsorted(EDGES, S.ptau, "right") - 1).astype(np.int16)
    S.pcross = nf[S.pa] != nf[S.pb]
    S.pdt = np.abs(t[S.pb] - t[S.pa])
    S.pcls = np.where(rc[S.pa] == rc[S.pb], rc[S.pa], nr).astype(np.int16)
    S.hist = np.zeros((NB, TAU_MAX + 1))
    np.add.at(S.hist, (S.pbin, S.ptau), 1)


def _cross_pairs(S: Skel):
    """Pairs of statements by different agents on the same day (same room -> class of the room; else 'different')."""
    t = S.st["t"].dt.epoch("us").to_numpy() / 1e6
    ag = S.st["agent"].to_numpy()
    room = S.st["room"].to_numpy()
    day = S.st["pt_date"].to_numpy()
    rcls, nr = _room_classes(S)
    rc = np.array([rcls[r] for r in room])
    A, Bv = [], []
    for d in S.days:
        idx = np.flatnonzero(day == d)
        if len(idx) < 2:
            continue
        ii, jj = np.triu_indices(len(idx), 1)
        a, b = idx[ii], idx[jj]
        k = ag[a] != ag[b]
        A.append(a[k]); Bv.append(b[k])
    S.xa = np.concatenate(A).astype(np.int32)
    S.xb = np.concatenate(Bv).astype(np.int32)
    S.xdt = np.abs(t[S.xb] - t[S.xa])
    S.xbin = (np.searchsorted(EDGES_S, S.xdt, "right") - 1).astype(np.int16)
    S.xcls = np.where(rc[S.xa] == rc[S.xb], rc[S.xa], nr).astype(np.int16)
    S.ncls = nr + 1


# ================================================================================ content -> accumulators
def wells(st: pl.DataFrame, Z: np.ndarray, min_n: int = MIN_WELL):
    """Leave-day-out well centre per statement row (nan where < min_n statements outside the day)."""
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


def _dot(X, a, b, chunk=2_000_000):
    out = np.empty(len(a))
    for s in range(0, len(a), chunk):
        out[s:s + chunk] = np.einsum("ij,ij->i", X[a[s:s + chunk]], X[b[s:s + chunk]])
    return out


def cross_profile(S: Skel, X: np.ndarray, ok: np.ndarray):
    """Cross-agent covariance per room class and wall-lag bin: (ncls, nbins_s) means, mean lags, counts."""
    k = ok[S.xa] & ok[S.xb]
    y = _dot(X, S.xa[k], S.xb[k])
    nbs = len(EDGES_S) - 1
    key = S.xcls[k].astype(np.int64) * nbs + S.xbin[k]
    sm = np.bincount(key, weights=y, minlength=S.ncls * nbs).reshape(S.ncls, nbs)
    st_ = np.bincount(key, weights=S.xdt[k], minlength=S.ncls * nbs).reshape(S.ncls, nbs)
    n = np.bincount(key, minlength=S.ncls * nbs).reshape(S.ncls, nbs).astype(float)
    # a class with too few pairs borrows the pooled profile
    pooled_s, pooled_t, pooled_n = sm.sum(0), st_.sum(0), n.sum(0)
    for c in range(S.ncls):
        bad = n[c] < MIN_N
        sm[c, bad], st_[c, bad], n[c, bad] = pooled_s[bad], pooled_t[bad], pooled_n[bad]
    with np.errstate(invalid="ignore", divide="ignore"):
        return sm / n, st_ / n, n


def cx_values(S: Skel, prof, pk: np.ndarray) -> np.ndarray:
    """Interpolated cross-agent covariance (log wall lag) for own pairs pk, per the pair's room class."""
    mean, tau, n = prof
    out = np.zeros(len(pk))
    for c in range(S.ncls):
        m = S.pcls[pk] == c
        if not m.any():
            continue
        g = np.isfinite(mean[c]) & np.isfinite(tau[c]) & (tau[c] > 0)
        if g.sum() < 2:
            continue
        lt, cv = np.log(tau[c][g]), mean[c][g]
        out[m] = np.interp(np.log(np.maximum(S.pdt[pk][m], 1.0)), lt, cv, left=cv[0], right=cv[-1])
    return out


@dataclass
class Acc:
    S: np.ndarray       # (n_ad, NB) sums
    N: np.ndarray       # (n_ad, NB) counts
    Sc: np.ndarray      # crossed-reset sums (O5)
    Nc: np.ndarray
    Sw: np.ndarray      # within-segment sums
    Nw: np.ndarray


def accumulate(S: Skel, Z: np.ndarray, mode: str = "corrected", Hok: tuple | None = None) -> tuple[Acc, np.ndarray]:
    """Own-autocovariance accumulators. mode: 'corrected' (primary), 'raw', or 'roomhour' (room x hour means
    subtracted from every vector before the well; variant). Hok: precomputed (H, ok) wells (period-level, real data);
    default: leave-day-out wells over the skeleton's own statements (synthetic)."""
    if mode == "roomhour":
        assert Hok is None, "real data: subtract room x hour means over the period first, then pass mode='raw'"
        Z = roomhour_resid(S, Z)
    H, ok = wells(S.st, Z) if Hok is None else Hok
    X = np.where(ok[:, None], Z - np.nan_to_num(H), 0.0)
    k = ok[S.pa] & ok[S.pb]
    pk = np.flatnonzero(k)
    y = _dot(X, S.pa[pk], S.pb[pk])
    if mode == "corrected":
        y = y - cx_values(S, cross_profile(S, X, ok), pk)
    nad = len(S.ad_keys)
    key = S.pad[pk].astype(np.int64) * NB + S.pbin[pk]
    sz = nad * NB
    Ssum = np.bincount(key, weights=y, minlength=sz).reshape(nad, NB)
    N = np.bincount(key, minlength=sz).reshape(nad, NB).astype(float)
    cr = S.pcross[pk]
    Sc = np.bincount(key[cr], weights=y[cr], minlength=sz).reshape(nad, NB)
    Nc = np.bincount(key[cr], minlength=sz).reshape(nad, NB).astype(float)
    return Acc(Ssum, N, Sc, Nc, Ssum - Sc, N - Nc), X


def roomhour_resid(S: Skel, Z: np.ndarray) -> np.ndarray:
    t = S.st["t"].dt.epoch("us").to_numpy() // 3_600_000_000
    room = S.st["room"].to_numpy().astype(np.int64)
    key = room * 10 ** 7 + (t - t.min())
    u, inv = np.unique(key, return_inverse=True)
    M = np.zeros((len(u), Z.shape[1]))
    np.add.at(M, inv, Z)
    M /= np.bincount(inv)[:, None]
    return Z - M[inv]


# ================================================================================ bootstrap and fits
def boot_weights(n_ad: int, B: int, seed: int, strata: np.ndarray | None = None) -> np.ndarray:
    """Agent-day block bootstrap (within strata if given): multiplicity weights (B x n_ad)."""
    rng = np.random.default_rng(seed)
    W = np.zeros((B, n_ad))
    strata = np.zeros(n_ad, int) if strata is None else strata
    for s in np.unique(strata):
        idx = np.flatnonzero(strata == s)
        for b in range(B):
            W[b] += np.bincount(rng.choice(idx, len(idx)), minlength=n_ad)
    return W


def bin_means(acc: Acc, W: np.ndarray):
    """W: (B, n_ad) weights -> (B, NB) bin means, (B, NB) counts."""
    s = W @ acc.S
    n = W @ acc.N
    with np.errstate(invalid="ignore", divide="ignore"):
        return s / n, n


def basis(hist: np.ndarray, g: np.ndarray) -> np.ndarray:
    """Bin-averaged (1-g)^tau: (len(g), NB) using the bins' real lag histograms."""
    tau = np.arange(TAU_MAX + 1)
    E = (1.0 - g[:, None]) ** tau[None, :]                 # (G, TAU)
    num = E @ hist.T                                       # (G, NB)
    den = hist.sum(1)
    with np.errstate(invalid="ignore", divide="ignore"):
        return num / den[None, :]


class Fitter:
    """Grid-profiled WLS fits for one skeleton (lag histograms fixed)."""

    def __init__(self, hist: np.ndarray):
        self.hist = hist
        self.Bs = basis(hist, GS_GRID)
        self.B1 = basis(hist, G1_GRID)
        self.Bk = basis(hist, GK_GRID)
        self._bk_cache = {}

    def bk(self, gk: float):
        if gk not in self._bk_cache:
            self._bk_cache[gk] = basis(self.hist, np.array([gk]))[0]
        return self._bk_cache[gk]

    @staticmethod
    def _wls_grid(Y: np.ndarray, w: np.ndarray, designs: list[np.ndarray]):
        """Y (D, b) bin means; w (b,) weights; designs: list of (b, p). Returns best coef (D, p), best index (D,),
        chi2 (D,)."""
        D = Y.shape[0]
        best_c = None
        best_r = np.full(D, np.inf)
        best_i = np.zeros(D, int)
        sw = np.sqrt(w)
        for gi, X in enumerate(designs):
            Xw = X * sw[:, None]
            Yw = Y * sw[None, :]
            coef, *_ = np.linalg.lstsq(Xw, Yw.T, rcond=None)      # (p, D)
            r = ((Yw.T - Xw @ coef) ** 2).sum(0)
            if best_c is None:
                best_c = np.zeros((D, X.shape[1]))
            m = r < best_r
            best_r[m] = r[m]
            best_c[m] = coef.T[m]
            best_i[m] = gi
        return best_c, best_i, best_r

    def two_rate(self, Y, w, keep, gk: float):
        """Constrained: g_k fixed. Returns dict of arrays (D,): A_k, A_s, g_s, B, chi2."""
        bk = self.bk(gk)[keep]
        designs = [np.column_stack([bk, self.Bs[i][keep], np.ones(keep.sum())]) for i in range(len(GS_GRID))
                   if GS_GRID[i] < gk / 3]
        gs = GS_GRID[GS_GRID < gk / 3]
        c, i, r = self._wls_grid(Y[:, keep], w[keep], designs)
        return {"A_k": c[:, 0], "A_s": c[:, 1], "B": c[:, 2], "g_s": gs[i], "g_k": np.full(len(i), gk), "chi2": r}

    def two_rate_free(self, Y, w, keep):
        designs, gks, gss = [], [], []
        for a, gk in enumerate(GK_GRID):
            for b, gs in enumerate(GS_GRID):
                if gs < gk / 3:
                    designs.append(np.column_stack([self.Bk[a][keep], self.Bs[b][keep], np.ones(keep.sum())]))
                    gks.append(gk)
                    gss.append(gs)
        c, i, r = self._wls_grid(Y[:, keep], w[keep], designs)
        return {"A_k": c[:, 0], "A_s": c[:, 1], "B": c[:, 2], "g_s": np.array(gss)[i], "g_k": np.array(gks)[i], "chi2": r}

    def one_rate(self, Y, w, keep):
        designs = [np.column_stack([self.B1[i][keep], np.ones(keep.sum())]) for i in range(len(G1_GRID))]
        c, i, r = self._wls_grid(Y[:, keep], w[keep], designs)
        return {"A": c[:, 0], "B": c[:, 1], "g": G1_GRID[i], "chi2": r}

    def predict_two(self, p, gk, keep):
        gi = np.searchsorted(GS_GRID, p["g_s"])
        return p["A_k"][:, None] * self.bk(gk)[keep][None, :] + p["A_s"][:, None] * self.Bs[gi][:, keep] + p["B"][:, None]

    def predict_one(self, p, keep):
        gi = np.searchsorted(G1_GRID, p["g"])
        return p["A"][:, None] * self.B1[gi][:, keep] + p["B"][:, None]


def ci(x, lo=2.5, hi=97.5):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    return [float(np.percentile(x, lo)), float(np.percentile(x, hi))] if len(x) else [np.nan, np.nan]


def kick_memory(gk: float) -> float:
    return 1.0 / (1.0 - (1.0 - gk) ** 2)


def analyze(S: Skel, acc: Acc, F: Fitter, gk: float, Apred: float, B: int = 200, seed: int = 0,
            ad_mask: np.ndarray | None = None, oof: bool = True, free: bool = True, natives: bool = True) -> dict:
    """O1-O5 on one unit (or agent subset via ad_mask). Apred = A_k^pred for this unit."""
    nad = len(S.ad_keys)
    m0 = np.ones(nad) if ad_mask is None else ad_mask.astype(float)
    W = boot_weights(nad, B, seed) * m0[None, :] if B else None
    Y0, N0 = bin_means(acc, m0[None, :])
    keep = (N0[0] >= MIN_N) & np.isfinite(Y0[0])
    out = {"n_ad": int((m0 > 0).sum()), "n_pairs": float(N0[0].sum()), "n_pairs_fast": float(N0[0][:5].sum()),
           "C": Y0[0].tolist(), "N": N0[0].tolist(), "keep": keep.tolist()}
    if keep.sum() < 5:
        out["ok"] = False
        return out
    if W is not None:
        Yb, Nb = bin_means(acc, W)
        Yb = np.where(np.isfinite(Yb), Yb, Y0)
        var = np.nanvar(Yb, 0)
    else:
        var = np.ones(NB)
    w = np.where(keep & (var > 0), 1.0 / np.maximum(var, 1e-12), 0.0)
    Yall = Y0 if W is None else np.vstack([Y0, Yb])
    p2 = F.two_rate(Yall, w, keep, gk)
    p1 = F.one_rate(Yall, w, keep)
    tot = p2["A_k"] + p2["A_s"] + p2["B"]
    with np.errstate(invalid="ignore", divide="ignore"):
        fk = p2["A_k"] / tot
        fs = (p2["A_s"] + p2["B"]) / tot
        Q = p2["A_k"] / Apred
    out.update({"ok": True, "g_k": gk, "A_k": float(p2["A_k"][0]), "A_s": float(p2["A_s"][0]), "B": float(p2["B"][0]),
                "g_s": float(p2["g_s"][0]), "f_k": float(fk[0]), "f_s": float(fs[0]), "Q_k": float(Q[0]),
                "A_pred": Apred, "f_k_pred": float(Apred / tot[0]) if tot[0] else np.nan,
                "A_1": float(p1["A"][0]), "g_1": float(p1["g"][0]), "B_1": float(p1["B"][0]),
                "chi2_two": float(p2["chi2"][0]), "chi2_one": float(p1["chi2"][0])})
    if W is not None:
        out.update({"ci_A_k": ci(p2["A_k"][1:]), "ci90_A_k": ci(p2["A_k"][1:], 5, 95),
                    "se_A_k": float(np.nanstd(p2["A_k"][1:])), "p_A_k_pos": float(np.mean(p2["A_k"][1:] > 0)),
                    "ci_A_s": ci(p2["A_s"][1:]), "ci_B": ci(p2["B"][1:]), "ci_g_s": ci(p2["g_s"][1:]),
                    "ci_f_k": ci(fk[1:]), "ci_f_s": ci(fs[1:]), "ci_Q_k": ci(Q[1:]), "ci90_Q_k": ci(Q[1:], 5, 95),
                    "ci_g_1": ci(p1["g"][1:]), "boot_A_k": p2["A_k"][1:].tolist(), "boot_f_s": fs[1:].tolist()})
        if free:
            pf = F.two_rate_free(Yall, w, keep)
            out.update({"free_A_k": float(pf["A_k"][0]), "free_g_k": float(pf["g_k"][0]),
                        "free_g_s": float(pf["g_s"][0]), "ci_free_A_k": ci(pf["A_k"][1:]),
                        "ci_free_g_k": ci(pf["g_k"][1:])})
    if oof:
        out.update(oof_compare(S, acc, F, gk, w, keep, m0))
    if natives:
        out.update(erasure_ratio(acc, p2, F, gk, keep, m0, W))
    return out


def oof_compare(S: Skel, acc: Acc, F: Fitter, gk: float, w, keep, m0) -> dict:
    """Day-blocked out-of-fold squared error (pair-count weighted) of the constrained two-rate vs one-rate fit."""
    days = np.unique(S.ad_day[m0 > 0])
    if len(days) < 2:
        return {"oof_two": np.nan, "oof_one": np.nan, "oof_n_folds": int(len(days))}
    e2 = e1 = 0.0
    for d in days:
        tr = m0 * (S.ad_day != d)
        te = m0 * (S.ad_day == d)
        Ytr, Ntr = bin_means(acc, tr[None, :])
        Yte, Nte = bin_means(acc, te[None, :])
        k = keep & (Ntr[0] >= MIN_N) & np.isfinite(Ytr[0])
        kt = k & (Nte[0] > 0) & np.isfinite(Yte[0])
        if k.sum() < 5 or kt.sum() == 0:
            continue
        p2 = F.two_rate(Ytr, w, k, gk)
        p1 = F.one_rate(Ytr, w, k)
        pr2 = F.predict_two(p2, gk, k)[0]
        pr1 = F.predict_one(p1, k)[0]
        sel = kt[k]
        e2 += float((Nte[0][kt] * (Yte[0][kt] - pr2[sel]) ** 2).sum())
        e1 += float((Nte[0][kt] * (Yte[0][kt] - pr1[sel]) ** 2).sum())
    return {"oof_two": e2, "oof_one": e1, "oof_n_folds": int(len(days)), "two_beats_one": bool(e2 < e1)}


def erasure_ratio(acc: Acc, p2: dict, F: Fitter, gk: float, keep, m0, W) -> dict:
    """O5: R_fast (lags 1-7) and R_slow (lags 32-255), crossed vs within a forced reset, matched per (agent-day, bin)."""
    def one(wv, idx):
        slow = (p2["A_s"][idx] * F.Bs[np.searchsorted(GS_GRID, p2["g_s"][idx])] + p2["B"][idx])
        Wm = np.minimum(acc.Nc, acc.Nw) * wv[:, None]                # matched weights (n_ad, NB)
        with np.errstate(invalid="ignore", divide="ignore"):
            mc = np.where(acc.Nc > 0, acc.Sc / acc.Nc, 0.0)
            mw = np.where(acc.Nw > 0, acc.Sw / acc.Nw, 0.0)
        res = {}
        for name, bins, sub in (("R_fast", FAST_BINS, True), ("R_slow", SLOW_BINS, False)):
            ww = Wm[:, bins]
            if ww.sum() <= 0:
                res[name] = np.nan
                res[name + "_n"] = 0.0
                continue
            c = (ww * mc[:, bins]).sum() / ww.sum()
            wi = (ww * mw[:, bins]).sum() / ww.sum()
            s = (ww.sum(0) * slow[bins]).sum() / ww.sum() if sub else 0.0
            res[name] = float((c - s) / (wi - s)) if (wi - s) != 0 else np.nan
            res[name + "_n"] = float(ww.sum())
        return res
    out = one(m0, 0)
    if W is not None:
        rf, rs = [], []
        for b in range(W.shape[0]):
            r = one(W[b], b + 1)
            rf.append(r["R_fast"])
            rs.append(r["R_slow"])
        out["ci_R_fast"] = ci(rf)
        out["ci_R_slow"] = ci(rs)
        out["boot_R_fast"] = rf
    return out


# ================================================================================ read jump J_K (input for shared weeks)
# Copied (not imported; STANDARDS 8) from hypotheses/H130-ou-private-wells-51/analysis/h130lib.py: Consensus ('sym'
# mode), read_jump and jump_stats, unchanged in logic. J_K = mean y(read at the producing call, posted in the mirror
# window (T_c - d, T_c)) - mean y(in flight, posted in (T_c, t_B) in B's room by others); y = x_B . unit(z_m - c_m), c_m
# the room consensus within +-15 min of t_m leaving out the sender and the reader.
WIN_S = 900.0
D_MAX = 300.0


class Consensus:
    def __init__(self, st: pl.DataFrame, Z: np.ndarray):
        self.t = st["t"].dt.epoch("us").to_numpy() / 1e6
        self.room = st["room"].to_numpy()
        self.agent = st["agent"].to_numpy()
        self.Z = Z
        self.rooms, self.ra = {}, {}
        for r in np.unique(self.room):
            idx = np.flatnonzero(self.room == r)
            idx = idx[np.argsort(self.t[idx], kind="stable")]
            self.rooms[r] = (self.t[idx], np.vstack([np.zeros((1, Z.shape[1])), np.cumsum(Z[idx], 0)]))
            for ag in np.unique(self.agent[idx]):
                j = idx[self.agent[idx] == ag]
                self.ra[(r, ag)] = (self.t[j], np.vstack([np.zeros((1, Z.shape[1])), np.cumsum(Z[j], 0)]))

    @staticmethod
    def _wsum(key_t, cs, t):
        lo = np.searchsorted(key_t, t - WIN_S, "left")
        hi = np.maximum(np.searchsorted(key_t, t + WIN_S, "right"), lo)
        return cs[hi] - cs[lo], (hi - lo).astype(float)

    def dirs(self, mi: np.ndarray, reader: np.ndarray, min_n: int = 3):
        room, t, snd = self.room[mi], self.t[mi], self.agent[mi]
        S = np.zeros((len(mi), self.Z.shape[1]))
        N = np.zeros(len(mi))
        for r in np.unique(room):
            k = np.flatnonzero(room == r)
            s, n = self._wsum(*self.rooms[r], t[k])
            S[k] += s
            N[k] += n
            for lv in (snd, reader):
                for ag in np.unique(lv[k]):
                    kk = k[lv[k] == ag]
                    if (r, ag) in self.ra:
                        s2, n2 = self._wsum(*self.ra[(r, ag)], t[kk])
                        S[kk] -= s2
                        N[kk] -= n2
        good = N >= min_n
        c = np.where(good[:, None], S / np.maximum(N, 1)[:, None], 0.0)
        u = self.Z[mi] - c
        nr = np.linalg.norm(u, axis=1)
        good &= nr > 1e-9
        return u / np.maximum(nr, 1e-9)[:, None], good


def read_jump(st: pl.DataFrame, rd: pl.DataFrame, Z: np.ndarray, X: np.ndarray, ok: np.ndarray, ad: np.ndarray,
              n_ad: int) -> dict:
    """Per agent-day sums of the read arm and the in-flight arm. st rows must index Z/X; rd needs turn_id, t_post,
    srow_m (read message's statement row, matched to st by srow)."""
    t = st["t"].dt.epoch("us").to_numpy() / 1e6
    tc = st["t_call"].dt.epoch("us").to_numpy() / 1e6
    room = st["room"].to_numpy()
    agent = st["agent"].to_numpy()
    turn = st["turn_id"].to_numpy()
    pos = dict(zip(st["srow"].to_list(), range(st.height)))
    mi_all = np.array([pos.get(s, -1) for s in rd["srow_m"].to_list()])
    rturn = rd["turn_id"].to_numpy()
    rpost = rd["t_post"].dt.epoch("us").to_numpy() / 1e6
    by_turn = {}
    for k, tt in enumerate(rturn):
        if mi_all[k] >= 0:
            by_turn.setdefault(int(tt), []).append(k)
    order = np.argsort(t, kind="stable")
    room_t = {r: order[room[order] == r] for r in np.unique(room)}
    pr_B, pr_m, kind = [], [], []
    for B in np.flatnonzero(ok):
        Tc, tB = tc[B], t[B]
        d = min(max(tB - Tc, 1.0), D_MAX)
        for k in by_turn.get(int(turn[B]), []):
            if rpost[k] > Tc - d:
                pr_B.append(B); pr_m.append(int(mi_all[k])); kind.append(0)
        rt = room_t.get(room[B])
        lo_ = np.searchsorted(t[rt], Tc, "right")
        hi_ = np.searchsorted(t[rt], min(tB, Tc + D_MAX), "left")
        for m in rt[lo_:hi_]:
            if agent[m] != agent[B]:
                pr_B.append(B); pr_m.append(int(m)); kind.append(1)
    pr_B, pr_m, kind = np.array(pr_B, int), np.array(pr_m, int), np.array(kind, int)
    U, good = Consensus(st, Z).dirs(pr_m, agent[pr_B])
    y = np.einsum("ij,ij->i", X[pr_B], U)
    out = {}
    for name, kk in (("read", 0), ("if", 1)):
        m = good & (kind == kk)
        rr = ad[pr_B[m]]
        out[f"S_{name}"] = np.bincount(rr, weights=y[m], minlength=n_ad)
        out[f"N_{name}"] = np.bincount(rr, minlength=n_ad).astype(float)
    return out


def jump_stats(J: dict, W: np.ndarray | None) -> dict:
    def one(w):
        r = (w * J["S_read"]).sum() / max((w * J["N_read"]).sum(), 1)
        f = (w * J["S_if"]).sum() / max((w * J["N_if"]).sum(), 1)
        return r - f
    w0 = np.ones(len(J["S_read"]))
    out = {"J": float(one(w0)), "n_read": float(J["N_read"].sum()), "n_if": float(J["N_if"].sum())}
    if W is not None:
        bs = np.array([one(w) for w in W])
        out["ci_J"] = ci(bs)
        out["se_J"] = float(bs.std())
    return out


def dl_pool(est, se):
    """DerSimonian-Laird random-effects pool -> (mu, se_mu, tau2, I2)."""
    est, se = np.asarray(est, float), np.asarray(se, float)
    m = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[m], se[m]
    if len(est) == 0:
        return np.nan, np.nan, np.nan, np.nan
    w = 1 / se ** 2
    mu_f = (w * est).sum() / w.sum()
    Q = (w * (est - mu_f) ** 2).sum()
    k = len(est)
    c = w.sum() - (w ** 2).sum() / w.sum()
    tau2 = max(0.0, (Q - (k - 1)) / c) if k > 1 and c > 0 else 0.0
    ws = 1 / (se ** 2 + tau2)
    mu = (ws * est).sum() / ws.sum()
    I2 = max(0.0, (Q - (k - 1)) / Q) if Q > 0 and k > 1 else 0.0
    return float(mu), float(np.sqrt(1 / ws.sum())), float(tau2), float(I2)
