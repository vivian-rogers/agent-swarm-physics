"""H125 estimators and loaders: kickoff excess alignment, undershoot U, overshoot E1, placebo-day U, decoy-direction U,
30-min window series on the active-hour clock, and the M_osc vs M_fade fits (variable projection on a grid).
The same code runs on real data (run.py, natives.py, confirm.py) and synthetic data (synthetic.py)."""
from __future__ import annotations

import os

for _v, _n in (("POLARS_MAX_THREADS", "2"), ("OMP_NUM_THREADS", "2"), ("OPENBLAS_NUM_THREADS", "2"),
               ("MKL_NUM_THREADS", "2"), ("VECLIB_MAXIMUM_THREADS", "2")):
    os.environ.setdefault(_v, _n)

import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
S = ROOT / "data/processed/shared"
ED = S / "embeddings"
DATA = ROOT / "data/processed/H125-kickoff-damped-oscillator"
MIN_DAY_STMT = 3
CFGS = {  # name: (model, variant, dedupe)
    "bge_white": ("bge_small", "white", False), "gte_white": ("gte_modernbert", "white", False),
    "bge_style": ("bge_small", "style", False), "gte_style": ("gte_modernbert", "style", False),
    "bge_dedupe": ("bge_small", "white", True), "gte_dedupe": ("gte_modernbert", "white", True),
}
_C: dict = {}


# ============================================================================================ loading
def statement_matrix(model: str, variant: str) -> np.ndarray:
    key = ("Z", model, variant)
    if key not in _C:
        name = {"white": "statements_white32", "style": "statements_style_resid_period32"}[variant]
        _C[key] = np.load(ED / f"{name}_{model}.npy", mmap_mode="r")
    return _C[key]


def dedupe_rows() -> np.ndarray:
    if "dedupe" not in _C:
        sf = pl.read_parquet(S / "statement_flags.parquet", columns=["srow", "self_repeat_both"])
        _C["dedupe"] = np.sort(sf.filter(pl.col("self_repeat_both"))["srow"].to_numpy())
    return _C["dedupe"]


def kickoffs(data: Path = DATA) -> pl.DataFrame:
    return pl.read_parquet(data / "kickoffs.parquet")


def stmt(design: str, data: Path = DATA) -> pl.DataFrame:
    key = ("stmt", str(data))
    if key not in _C:
        _C[key] = pl.read_parquet(data / "stmt.parquet")
    return _C[key].filter(pl.col("design") == design).sort("t")


def vecs(data: Path = DATA) -> dict:
    key = ("vec", str(data))
    if key not in _C:
        _C[key] = dict(np.load(data / "vectors.npz"))
    return _C[key]


def decoy_set(p: int, kick_goals: np.ndarray) -> np.ndarray:
    return np.array([j for j, g in enumerate(kick_goals) if g not in (p - 1, p, p + 1, 23)])


def excess_alignment(st: pl.DataFrame, krow: dict, cfg: str, data: Path = DATA, with_decoys: bool = False):
    """Per-statement excess alignment a_s (own target minus mean decoy), linear in the statement vectors.
    Kickoff designs: own k-hat vs the other non-holdout kickoffs (not p-1, p, p+1, #23), in the regime basis.
    Native designs (G51, NE38): each agent's own role vs the other agents' roles (near-duplicates cos > 0.95 dropped).
    with_decoys: also the (n_stmt x n_decoy) matrix of decoy excess alignments (kickoff designs only)."""
    model, variant, dd = CFGS[cfg]
    V = vecs(data)
    Z = statement_matrix(model, variant)
    rows = st["row"].to_numpy()
    X = np.asarray(Z[rows], dtype=np.float64)
    keep = np.ones(len(rows), bool)
    if dd:
        keep = ~np.isin(rows, dedupe_rows())
    if krow["native"] in ("G51", "NE38"):
        import json
        roles = {int(k): int(v) for k, v in json.loads(krow["role_gids"]).items()}
        R = V[f"R|{model}"]; rg = list(V["role_gid"])
        ag = st["agent"].to_numpy()
        a = np.full(len(rows), np.nan)
        for i in np.unique(ag):
            if int(i) not in roles:
                continue
            own = R[rg.index(roles[int(i)])]
            others = [R[rg.index(g)] for j, g in roles.items() if j != int(i)]
            others = [o for o in others if float(o @ own) < 0.95]
            m = ag == i
            a[m] = X[m] @ own - np.mean([X[m] @ o for o in others], axis=0)
        a[~keep] = np.nan
        return (a, None) if with_decoys else a
    K = V[f"K|{model}|{krow['regime']}"]; kg = V["kick_goal_no"]
    own = K[list(kg).index(krow["goal_no"])]
    D = K[decoy_set(krow["goal_no"], kg)]
    P = X @ D.T
    a = X @ own - P.mean(1)
    a[~keep] = np.nan
    if not with_decoys:
        return a
    nd = D.shape[0]
    tot = P.sum(1, keepdims=True)
    Pq = P - (tot - P) / (nd - 1)          # decoy q minus the mean of the other decoys
    Pq[~keep] = np.nan
    return a, Pq


# ============================================================================================ day-level statistics
def agent_day(st: pl.DataFrame, a: np.ndarray) -> dict:
    """{agent: {day_idx: (mean, n)}} over post-t0 statements (day 1 uses t >= t0 by the 'post' segment)."""
    ag = st["agent"].to_numpy().astype(np.int64); di = st["day_idx"].to_numpy().astype(np.int64)
    ok = (st["seg"] == "post").to_numpy() & np.isfinite(a)
    key = ag[ok] * 1000 + di[ok]
    u, inv = np.unique(key, return_inverse=True)
    s = np.bincount(inv, weights=a[ok]); c = np.bincount(inv)
    out: dict = {}
    for k_, s_, c_ in zip(u, s, c):
        out.setdefault(int(k_ // 1000), {})[int(k_ % 1000)] = (float(s_ / c_), int(c_))
    return out


def _pair(dd: dict, days) -> float:
    v = [dd[d][0] for d in days if d in dd and dd[d][1] >= MIN_DAY_STMT]
    return float(np.mean(v)) if v else np.nan


def u_agents(ad: dict, o: int = 1, settled=(4, 5)) -> tuple[np.ndarray, np.ndarray]:
    """Per-agent U_i (origin o: days o+1,o+2 vs o+settled) and E1_i (day o vs settled)."""
    U, E = [], []
    for i, dd in ad.items():
        lo = _pair(dd, (o + 1, o + 2))
        hi = _pair(dd, tuple(o + s - 1 for s in settled))
        d1 = dd.get(o, (np.nan, 0))
        U.append(hi - lo)
        E.append(d1[0] - hi if d1[1] >= MIN_DAY_STMT else np.nan)
    return np.array(U), np.array(E)


def mean_jack(x: np.ndarray) -> tuple[float, float, int]:
    x = x[np.isfinite(x)]
    n = len(x)
    if n < 2:
        return (float(x[0]) if n else np.nan), np.nan, n
    m = x.mean()
    loo = (x.sum() - x) / (n - 1)
    se = float(np.sqrt((n - 1) / n * ((loo - loo.mean()) ** 2).sum()))
    return float(m), se, n


def zeta_pk(E1: float, U: float) -> float:
    """Peak-ratio damping from successive extremes half a period apart; >= 1 (returned as 1.0) when there is no undershoot."""
    if not (np.isfinite(E1) and np.isfinite(U)) or E1 <= 0:
        return np.nan
    if U <= 0:
        return 1.0
    d = np.log(E1 / U)
    return float(d / np.sqrt(np.pi ** 2 + d ** 2)) if d > 0 else 0.0


def placebo_origins(n_days: int) -> list[int]:
    return list(range(6, n_days - 4 + 1))


# ============================================================================================ window series and fits
def window_series(st: pl.DataFrame, a: np.ndarray, h_end: float, bin_h: float = 0.5, idx=None):
    """30-min window series over [0, h_end) on the active-hour clock, within-agent centred.
    Returns h (bin centres), y (mean over agents of agent-centred window means), w (agents per bin), slot (modal slot).
    idx: optional array of agent ids (bootstrap draw, duplicates allowed)."""
    post = (st["seg"] == "post").to_numpy()
    h = st["h"].to_numpy().astype(float); ag = st["agent"].to_numpy(); sl = st["slot"].to_numpy()
    ok = post & np.isfinite(a) & (h >= 0) & (h < h_end)
    b = np.floor(h[ok] / bin_h).astype(int); A = a[ok]; G = ag[ok]; L = sl[ok]
    nb = int(np.ceil(h_end / bin_h))
    agents = np.unique(G) if idx is None else np.asarray(idx)
    num = np.zeros(nb); cnt = np.zeros(nb); slots = np.zeros((nb, 4))
    # per-agent window means
    for i in agents:
        m = G == i
        if not m.any():
            continue
        s = np.bincount(b[m], weights=A[m], minlength=nb); c = np.bincount(b[m], minlength=nb)
        wm = np.where(c > 0, s / np.maximum(c, 1), np.nan)
        if np.isfinite(wm).sum() < 3:
            continue
        wm = wm - np.nanmean(wm)
        f = np.isfinite(wm)
        num[f] += wm[f]; cnt[f] += 1
        for k in range(4):
            slots[:, k] += np.bincount(b[m][L[m] == k], minlength=nb)
    keep = cnt > 0
    y = np.where(keep, num / np.maximum(cnt, 1), np.nan)
    hc = (np.arange(nb) + 0.5) * bin_h
    return hc[keep], y[keep], cnt[keep], slots[keep].argmax(1)


def _basis_slots(slot):
    return np.stack([(slot == k).astype(float) for k in (1, 2, 3)], 1)


def grids(day_h_med: float):
    lam = np.geomspace(0.002, 1.5, 32)
    half = np.linspace(0.5, 4.0, 32) * day_h_med          # half-period bounds in active hours
    om = np.pi / half
    tau = np.geomspace(0.2, 300.0, 30)
    t12 = [(a, b) for i, a in enumerate(tau) for b in tau[i + 1:]]
    return lam, om, t12


def _sse_grid(y, w, mats):
    """mats: list of design matrices (n x p). Weighted SSE for each (sqrt-weight scaling)."""
    sw = np.sqrt(w)
    ys = y * sw
    out = np.empty(len(mats))
    for j, X in enumerate(mats):
        Xs = X * sw[:, None]
        beta, res, rk, _ = np.linalg.lstsq(Xs, ys, rcond=None)
        r = ys - Xs @ beta
        out[j] = r @ r
    return out


class Fitter:
    """Grid variable-projection fits of M_osc and M_fade for one skeleton (h, slot, w fixed; y varies)."""

    def __init__(self, h, slot, w, day_h_med):
        self.h, self.w = h, w
        lam, om, t12 = grids(day_h_med)
        Sl = _basis_slots(slot)
        one = np.ones_like(h)
        self.osc_par = [(l, o) for l in lam for o in om]
        self.fade_par = t12
        sw = np.sqrt(w)
        self.Q_osc = self._qs([np.c_[one, np.exp(-l * h) * np.cos(o * h), np.exp(-l * h) * np.sin(o * h), Sl] for l, o in self.osc_par], sw)
        self.Q_fade = self._qs([np.c_[one, np.exp(-h / a), np.exp(-h / b), Sl] for a, b in t12], sw)
        self.sw = sw

    @staticmethod
    def _qs(mats, sw):
        Qs = []
        for X in mats:
            q, r = np.linalg.qr(X * sw[:, None])
            keep = np.abs(np.diag(r)) > 1e-8 * max(1.0, np.abs(np.diag(r)).max())
            q = q[:, keep]
            if q.shape[1] < 7:
                q = np.c_[q, np.zeros((q.shape[0], 7 - q.shape[1]))]
            Qs.append(q)
        return np.stack(Qs)   # G x n x 7

    def fit(self, y):
        ys = y * self.sw
        yy = ys @ ys
        so = yy - (np.einsum("gnp,n->gp", self.Q_osc, ys) ** 2).sum(1)
        sf = yy - (np.einsum("gnp,n->gp", self.Q_fade, ys) ** 2).sum(1)
        jo, jf = int(np.argmin(so)), int(np.argmin(sf))
        l, o = self.osc_par[jo]
        zeta = l / np.sqrt(l ** 2 + o ** 2)
        return dict(sse_osc=float(so[jo]), sse_fade=float(sf[jf]), dsse=float((sf[jf] - so[jo]) / sf[jf]) if sf[jf] > 0 else np.nan,
                    zeta_fit=float(zeta), lam=float(l), omega=float(o), tau1=float(self.fade_par[jf][0]), tau2=float(self.fade_par[jf][1]))


# ============================================================================================ meta-analysis
def dl_meta(est, se):
    est = np.asarray(est, float); se = np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[ok], se[ok]
    if len(est) < 2:
        return dict(mean=float(est[0]) if len(est) else np.nan, se=np.nan, tau2=np.nan, k=len(est))
    w = 1 / se ** 2
    m0 = (w * est).sum() / w.sum()
    Q = (w * (est - m0) ** 2).sum()
    c = w.sum() - (w ** 2).sum() / w.sum()
    tau2 = max(0.0, (Q - (len(est) - 1)) / c)
    ws = 1 / (se ** 2 + tau2)
    return dict(mean=float((ws * est).sum() / ws.sum()), se=float(np.sqrt(1 / ws.sum())), tau2=float(tau2), k=int(len(est)))


def sign_p(x, alternative="greater"):
    from scipy.stats import binomtest
    x = np.asarray(x, float); x = x[np.isfinite(x) & (x != 0)]
    if not len(x):
        return np.nan
    return float(binomtest(int((x > 0).sum()), len(x), 0.5, alternative=alternative).pvalue)


# ============================================================================================ one kickoff, end to end
def analyze_kickoff(st: pl.DataFrame, krow: dict, a: np.ndarray, Pq: np.ndarray | None, fitter_cache: dict | None = None,
                    n_boot: int = 0, seed: int = 0, settled=(4, 5), fit_days: int = 5) -> dict:
    ad = agent_day(st, a)
    Ui, Ei = u_agents(ad, 1, settled)
    U, seU, nU = mean_jack(Ui)
    E1, seE1, nE = mean_jack(Ei)
    r = dict(U=U, se_U=seU, n_u=nU, E1=E1, se_E1=seE1, n_e=nE, zeta_pk=zeta_pk(E1, U), n_agents=len(ad))
    # placebo-day U along the same direction
    pl_u = []
    for o in placebo_origins(krow["n_days"]):
        Uo, _ = u_agents(ad, o, settled)
        m, s_, n = mean_jack(Uo)
        if n >= 3:
            pl_u.append(m)
    r["placebo_u"] = pl_u
    # decoy-direction U (same days, same agents)
    if Pq is not None:
        ud = []
        for q in range(Pq.shape[1]):
            adq = agent_day(st, Pq[:, q])
            Uq, _ = u_agents(adq, 1, settled)
            ud.append(mean_jack(Uq)[0])
        ud = np.array(ud)
        r["decoy_u"] = ud.tolist()
        r["pi_U"] = float(np.mean(ud[np.isfinite(ud)] < U)) if np.isfinite(U) else np.nan
    # window series and fits on days 1..fit_days
    hmax = float(st.filter(pl.col("seg") == "post").filter(pl.col("day_idx") <= fit_days)["h"].max() or 0) + 1e-6
    h, y, w, sl = window_series(st, a, hmax)
    if len(h) >= 12:
        key = (krow["design"], fit_days, len(h))
        dhm = float(np.median(krow["day_h"][:fit_days]))
        if fitter_cache is not None and key in fitter_cache:
            F = fitter_cache[key]
        else:
            F = Fitter(h, sl, w, dhm)
            if fitter_cache is not None:
                fitter_cache[key] = F
        r.update(F.fit(y))
        r["_series"] = (h.tolist(), y.tolist(), w.tolist())
        if n_boot:
            rng = np.random.default_rng(seed)
            agents = np.array(sorted(ad))
            zs, ds = [], []
            for _ in range(n_boot):
                idx = rng.choice(agents, len(agents), replace=True)
                hb, yb, wb, slb = window_series(st, a, hmax, idx=idx)
                if len(hb) < 12:
                    continue
                Fb = Fitter(hb, slb, wb, dhm)
                fb = Fb.fit(yb)
                zs.append(fb["zeta_fit"]); ds.append(fb["dsse"])
            if zs:
                r["zeta_ci"] = [float(np.percentile(zs, 5)), float(np.percentile(zs, 95))]
                r["dsse_ci"] = [float(np.percentile(ds, 5)), float(np.percentile(ds, 95))]
    else:
        r.update(dict(sse_osc=np.nan, sse_fade=np.nan, dsse=np.nan, zeta_fit=np.nan))
    return r
