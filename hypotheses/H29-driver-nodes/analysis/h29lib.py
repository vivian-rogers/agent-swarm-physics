"""H29 core library: content-pull influence network, linear controllability, and the observed-spread validators.

Used by analysis/synthetic.py, analysis/explore.py and analysis/confirm.py. Threads pinned (<= 2 workers).

Conventions (card, "Model" and "Observables"):
- statement vectors: bge-small chat embeddings, regime-III whitener (common.load_whitener, 32 dims), unit-normalized;
- row = (recipient talk turn tau_n, message m in V(tau_n) or I(tau_n)); y = x(tau_n) - x(tau_{n-1}); u = x_m - x(tau_{n-1});
- pull slope a(S) = sum_S y.u / sum_S |u|^2 (least-squares slope of the displacement on the gap to m);
- cross-day placebo: u' = x_{m'} - x(tau_{n-1}), m' a seeded random message of the same sender (same kind for humans)
  from another day of the unit;
- net pull per message kappa = [a(V) - a(X_V)] - [a(I) - a(X_I)] (difference in differences);
- A_ij (per active hour) = max(0, shrunk kappa_ij) * (messages from i absorbed by j per active hour);
- dynamics: dx_j/dt = sum_i A_ij (x_i - x_j) - Gamma_j x_j + b_j u(t); Q[j, i] = A[i, j], Q[j, j] = -sum_i A[i, j] - Gamma_j.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("POLARS_MAX_THREADS", "2")

import datetime as dt  # noqa: E402
import json  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy.linalg import expm  # noqa: E402
from scipy.sparse import csr_matrix  # noqa: E402
from scipy.sparse.csgraph import connected_components, maximum_bipartite_matching  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
HYP = ROOT / "hypotheses/H29-driver-nodes"
OUT_BASE = ROOT / "data/processed/H29-driver-nodes"
SH = ROOT / "data/processed/shared"
# Round 1b switches (2026-10-04), read from the environment so every script runs unchanged:
#   H29_DATA = r1 (default; H18 call-start visibility, round 1) | r1b (DQ1 context-ledger visibility; units in OUT_BASE/r1b)
#   H29_EMB  = bge_small (default) | gte_modernbert (DQ5 second model)
DATA_VERSION = os.environ.get("H29_DATA", "r1")
EMB_MODEL = os.environ.get("H29_EMB", "bge_small")
DATA = OUT_BASE if DATA_VERSION == "r1" else OUT_BASE / "r1b"
OUT = OUT_BASE if (DATA_VERSION == "r1" and EMB_MODEL == "bge_small") else (
    OUT_BASE / (("r1b" if DATA_VERSION == "r1b" else "r1") + ("" if EMB_MODEL == "bge_small" else "_gte")))
FIG = HYP / "figures"
SEED = 20261004
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, load_whitener  # noqa: E402,F401

T_HORIZON_H = 4.0      # Gramian horizon: one regime-III active day
DT_H = 1.0 / 12        # 5-min grid for the Gramian integral
N_MIN_PAIR = 15        # minimum visible rows for a pair estimate
SPREAD_H = 2.0         # horizon of the observed swarm spread (hours)


# ----------------------------------------------------------------------------- embeddings

class Emb:
    """Map chat_core row index (msg) -> unit-normalized whitened vector (regime III, 32 dims) or raw centered."""

    def __init__(self, regime: str = "III", dim: int = 32, model: str | None = None):
        from embed_models import emb_path, load_whitener as load_whitener_m
        model = model or EMB_MODEL
        ci = pl.read_parquet(SH / "embeddings/chat_index.parquet").with_row_index("erow")
        chat = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id"]).with_row_index("msg")
        self.erow = chat.join(ci, on="message_id", how="left").sort("msg")["erow"].fill_null(-1).to_numpy().astype(np.int64)
        self.E = np.load(emb_path("chat", model), mmap_mode="r")
        self.W = load_whitener_m(regime, dim, model)
        self.model = model

    def vectors(self, msgs: np.ndarray, kind: str = "white") -> np.ndarray:
        msgs = np.asarray(msgs, dtype=np.int64)
        er = self.erow[msgs]
        ok = er >= 0
        raw = np.zeros((len(msgs), self.E.shape[1]), dtype=np.float32)
        if ok.any():
            o = np.argsort(er[ok])
            tmp = np.asarray(self.E[er[ok][o]], dtype=np.float32)
            back = np.empty_like(tmp)
            back[o] = tmp
            raw[ok] = back
        if kind == "white":
            X = self.W(raw)
        elif kind == "raw":
            X = raw - raw[ok].mean(0, keepdims=True)
        else:
            raise ValueError(kind)
        n = np.linalg.norm(X, axis=1, keepdims=True)
        X = X / np.where(n > 0, n, 1)
        X[~ok] = np.nan
        return X.astype(np.float32)


# ----------------------------------------------------------------------------- unit data

def load_unit(name: str, root: Path | None = None) -> dict:
    root = DATA if root is None else root
    (OUT / name).mkdir(parents=True, exist_ok=True)
    d = root / name
    U = {k: pl.read_parquet(d / f"{k}.parquet") for k in ("turns", "rows", "msgs")}
    U["meta"] = json.loads((d / "meta.json").read_text())
    U["name"] = name
    return U


def attach_vectors(U: dict, emb: Emb, kind: str = "white"):
    m = U["msgs"]["msg"].to_numpy().astype(np.int64)
    U["msg_ids"] = m                     # sorted? ensure by sorting index
    o = np.argsort(m)
    U["msg_sorted"] = m[o]
    U["X"] = emb.vectors(m[o], kind)
    return U


def vec_index(U: dict, msgs: np.ndarray) -> np.ndarray:
    return np.searchsorted(U["msg_sorted"], np.asarray(msgs, dtype=np.int64))


def placebo_partner(U: dict, rows: pl.DataFrame, rng: np.random.Generator) -> np.ndarray:
    """Cross-day placebo message for each row: a random message by the same sender (agents) or the same kind
    (humans, automated) from another PT day of the unit; -1 when none exists."""
    msgs = U["msgs"]
    day = msgs["pt_date"].to_numpy()
    kind = msgs["kind"].to_numpy()
    snd = msgs["sender"].to_numpy()
    mid = msgs["msg"].to_numpy().astype(np.int64)
    key = np.where(kind == 0, snd.astype(np.int64), -10 - kind.astype(np.int64))
    pools = {}
    for k in np.unique(key):
        sel = key == k
        pools[int(k)] = (mid[sel], day[sel])
    mday = dict(zip(mid.tolist(), day.tolist()))
    r_msg = rows["msg"].to_numpy().astype(np.int64)
    r_kind = rows["kind"].to_numpy()
    r_snd = rows["sender"].to_numpy()
    r_key = np.where(r_kind == 0, r_snd.astype(np.int64), -10 - r_kind.astype(np.int64))
    out = np.full(len(r_msg), -1, dtype=np.int64)
    # vectorize per key x day
    for k in np.unique(r_key):
        pm, pd_ = pools.get(int(k), (np.zeros(0, np.int64), np.zeros(0, object)))
        idx = np.where(r_key == k)[0]
        if not len(pm):
            continue
        rd = np.array([mday[int(x)] for x in r_msg[idx]])
        for d in np.unique(rd):
            cand = pm[pd_ != d]
            if not len(cand):
                continue
            ii = idx[rd == d]
            out[ii] = cand[rng.integers(len(cand), size=len(ii))]
    return out


def row_stats(U: dict, seed: int = SEED) -> pl.DataFrame:
    """Per (turn, message) row: y.u, |u|^2, dsim and the cross-day placebo versions."""
    rng = np.random.default_rng(seed)
    T = U["turns"]
    R = U["rows"].join(T.select("talk_id", "agent", "day_idx", "pt_date", "msg", "prev_msg", "t_us", "n_room")
                       .rename({"msg": "tmsg", "agent": "recv"}), on="talk_id", how="inner")
    kturn = R.filter(pl.col("vis")).group_by("talk_id").len().rename({"len": "k"})
    R = R.join(kturn, on="talk_id", how="left").with_columns(pl.col("k").fill_null(0))
    X = U["X"]
    xn = X[vec_index(U, R["tmsg"].to_numpy())]
    xo = X[vec_index(U, R["prev_msg"].to_numpy())]
    xm = X[vec_index(U, R["msg"].to_numpy())]
    part = placebo_partner(U, R, rng)
    xp = np.full_like(xm, np.nan)
    okp = part >= 0
    xp[okp] = X[vec_index(U, part[okp])]
    y = xn - xo
    u = xm - xo
    up = xp - xo
    out = R.select("talk_id", "recv", "day_idx", "pt_date", "t_us", "n_room", "msg", "kind", "sender", "vis", "ment_j",
                   "k").with_columns(
        pl.Series("partner", part),
        pl.Series("yu", (y * u).sum(1)), pl.Series("uu", (u * u).sum(1)),
        pl.Series("dsim", (xn * xm).sum(1) - (xo * xm).sum(1)),
        pl.Series("yu_x", (y * up).sum(1)), pl.Series("uu_x", (up * up).sum(1)),
        pl.Series("dsim_x", (xn * xp).sum(1) - (xo * xp).sum(1)))
    return out.filter(pl.col("yu").is_not_nan() & pl.col("uu").is_not_nan())


# ----------------------------------------------------------------------------- estimators

def _ratio(num, den):
    return float(num / den) if den > 0 else np.nan


def kappa_from_sums(s: dict) -> dict:
    aV = _ratio(s["yu_V"], s["uu_V"])
    aXV = _ratio(s["yux_V"], s["uux_V"])
    aI = _ratio(s["yu_I"], s["uu_I"])
    aXI = _ratio(s["yux_I"], s["uux_I"])
    return dict(a_V=aV, a_XV=aXV, a_I=aI, a_XI=aXI, kappa=(aV - aXV) - (aI - aXI), kappa_x=aV - aXV,
                kappa_i=aV - aI, contamination=aI - aXI)


def day_sums(R: pl.DataFrame, by: list[str] | None = None) -> pl.DataFrame:
    """Per day (x by) sums needed by kappa, for the day-block bootstrap. Placebo sums use rows with a partner."""
    by = by or []
    ok_x = pl.col("yu_x").is_not_nan()
    agg = [
        pl.col("yu").filter(pl.col("vis")).sum().alias("yu_V"), pl.col("uu").filter(pl.col("vis")).sum().alias("uu_V"),
        pl.col("yu_x").filter(pl.col("vis") & ok_x).sum().alias("yux_V"),
        pl.col("uu_x").filter(pl.col("vis") & ok_x).sum().alias("uux_V"),
        pl.col("yu").filter(~pl.col("vis")).sum().alias("yu_I"), pl.col("uu").filter(~pl.col("vis")).sum().alias("uu_I"),
        pl.col("yu_x").filter(~pl.col("vis") & ok_x).sum().alias("yux_I"),
        pl.col("uu_x").filter(~pl.col("vis") & ok_x).sum().alias("uux_I"),
        pl.col("vis").sum().alias("n_V"), (~pl.col("vis")).sum().alias("n_I")]
    return R.group_by(["day_idx", *by]).agg(agg).sort(["day_idx", *by])


SUM_COLS = ["yu_V", "uu_V", "yux_V", "uux_V", "yu_I", "uu_I", "yux_I", "uux_I"]


def kappa_unit(R: pl.DataFrame, B: int = 1000, seed: int = SEED) -> dict:
    """Unit-level net pull with a day-block bootstrap CI."""
    D = day_sums(R)
    M = D.select(SUM_COLS).to_numpy()
    tot = dict(zip(SUM_COLS, M.sum(0)))
    est = kappa_from_sums(tot)
    rng = np.random.default_rng(seed)
    nd = M.shape[0]
    bs = {k: [] for k in ("kappa", "kappa_x", "kappa_i", "contamination", "a_V")}
    if nd >= 2:
        for _ in range(B):
            w = np.bincount(rng.integers(nd, size=nd), minlength=nd)
            s = dict(zip(SUM_COLS, (M * w[:, None]).sum(0)))
            e = kappa_from_sums(s)
            for k in bs:
                bs[k].append(e[k])
    out = dict(est)
    for k, v in bs.items():
        v = np.array(v, dtype=float)
        v = v[np.isfinite(v)]
        if len(v):
            out[f"{k}_ci"] = [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]
            out[f"{k}_p_le0"] = float((v <= 0).mean())
    out["n_V"] = int(D["n_V"].sum())
    out["n_I"] = int(D["n_I"].sum())
    out["n_days"] = nd
    return out


def pair_kappa(R: pl.DataFrame, agents: list[int], contamination: float, B: int = 300, seed: int = SEED,
               n_min: int = N_MIN_PAIR) -> dict:
    """Per-pair net-of-field pull kappa_ij = a_ij(V) - a_ij(X_V) - c, with day-bootstrap SEs and empirical-Bayes
    shrinkage toward an additive sender + receiver structure. Agent senders only."""
    Ra = R.filter(pl.col("vis") & (pl.col("kind") == 0) & pl.col("sender").is_in(agents) & pl.col("recv").is_in(agents)
                  & pl.col("yu_x").is_not_nan())
    N = len(agents)
    pos = {a: i for i, a in enumerate(agents)}
    days = sorted(set(Ra["day_idx"].to_list()))
    dpos = {d: i for i, d in enumerate(days)}
    S = np.zeros((len(days), 5, N, N))  # yu, uu, yux, uux, n
    if Ra.height:
        di = np.array([dpos[d] for d in Ra["day_idx"].to_list()])
        si = np.array([pos[a] for a in Ra["sender"].to_list()])
        ri = np.array([pos[a] for a in Ra["recv"].to_list()])
        for c, col in enumerate(("yu", "uu", "yu_x", "uu_x")):
            np.add.at(S[:, c], (di, si, ri), Ra[col].to_numpy())
        np.add.at(S[:, 4], (di, si, ri), 1)

    def est(T):
        with np.errstate(invalid="ignore", divide="ignore"):
            k = T[0] / T[1] - T[2] / T[3] - contamination
        k[T[4] < n_min] = np.nan
        np.fill_diagonal(k, np.nan)
        return k

    tot = S.sum(0)
    K = est(tot)
    n = tot[4]
    rng = np.random.default_rng(seed)
    nd = len(days)
    if nd >= 2:
        bs = np.stack([est((S * np.bincount(rng.integers(nd, size=nd), minlength=nd)[:, None, None, None]).sum(0))
                       for _ in range(B)])
        se = np.nanstd(bs, axis=0)
    else:
        se = np.full_like(K, np.nan)
    se = np.where(np.isfinite(se) & (se > 0), se, np.nan)
    # empirical Bayes toward mu + s_i + r_j (weighted additive fit)
    ok = np.isfinite(K) & np.isfinite(se)
    prior = np.full_like(K, np.nan)
    Ks = K.copy()
    if ok.sum() >= 5:
        w = 1.0 / se[ok] ** 2
        ii, jj = np.where(ok)
        Xd = np.zeros((ok.sum(), 2 * N + 1))
        Xd[:, 0] = 1
        Xd[np.arange(len(ii)), 1 + ii] = 1
        Xd[np.arange(len(ii)), 1 + N + jj] = 1
        lam = 1.0
        Wm = Xd * w[:, None]
        reg = lam * np.eye(2 * N + 1) * np.median(w)
        reg[0, 0] = 0
        beta = np.linalg.solve(Xd.T @ Wm + reg, Wm.T @ K[ok])
        full = beta[0] + beta[1:1 + N][:, None] + beta[1 + N:][None, :]
        prior = full
        resid = K[ok] - full[ok]
        tau2 = max(float(np.average(resid ** 2, weights=w) - np.average(se[ok] ** 2, weights=w)), 1e-8)
        shrink = tau2 / (tau2 + se ** 2)
        Ks = np.where(ok, shrink * K + (1 - shrink) * full, np.where(n > 0, full, np.nan))
        np.fill_diagonal(Ks, np.nan)
    z = K / se
    return dict(agents=agents, K=K, se=se, Ks=Ks, prior=prior, n=n, z=z)


def joint_pull(R: pl.DataFrame, U: dict, agents: list[int], ridge: float = 1.0) -> np.ndarray:
    """Joint per-receiver ridge regression y_n = sum_i a_ij U_i,n + sum_i b_ij X_i,n (agent senders), returning
    a_ij - b_ij. Rival estimator; chosen against the marginal one on synthetic data only."""
    N = len(agents)
    pos = {a: i for i, a in enumerate(agents)}
    X = U["X"]
    T = U["turns"]
    Rv = R.filter(pl.col("vis") & (pl.col("kind") == 0) & pl.col("sender").is_in(agents) & pl.col("recv").is_in(agents))
    tmap = T.select("talk_id", "msg", "prev_msg")
    out = np.full((N, N), np.nan)
    for (j,), sub in Rv.group_by(["recv"], maintain_order=True):
        tids = np.unique(sub["talk_id"].to_numpy())
        tt = tmap.filter(pl.col("talk_id").is_in(tids)).sort("talk_id")
        tpos = {t: q for q, t in enumerate(tt["talk_id"].to_list())}
        xn = X[vec_index(U, tt["msg"].to_numpy())]
        xo = X[vec_index(U, tt["prev_msg"].to_numpy())]
        Y = xn - xo
        d = Y.shape[1]
        nT = len(tids)
        Ucol = np.zeros((nT, N, d))
        Xcol = np.zeros((nT, N, d))
        q = np.array([tpos[t] for t in sub["talk_id"].to_list()])
        s = np.array([pos[a] for a in sub["sender"].to_list()])
        xm = X[vec_index(U, sub["msg"].to_numpy())]
        np.add.at(Ucol, (q, s), xm - xo[q])
        if "partner" in sub.columns:
            pm = sub["partner"].to_numpy()
            okp = pm >= 0
            xp = np.zeros_like(xm)
            xp[okp] = X[vec_index(U, pm[okp])]
            np.add.at(Xcol, (q[okp], s[okp]), xp[okp] - xo[q][okp])
        good = np.isfinite(Y).all(1) & np.isfinite(Ucol).all((1, 2)) & np.isfinite(Xcol).all((1, 2))
        Yf = Y[good].reshape(-1)
        D = np.concatenate([Ucol[good].transpose(0, 2, 1).reshape(-1, N), Xcol[good].transpose(0, 2, 1).reshape(-1, N)], 1)
        if len(Yf) < 4 * N:
            continue
        G = D.T @ D
        beta = np.linalg.solve(G + ridge * np.eye(2 * N) * np.mean(np.diag(G)) * 1e-3, D.T @ Yf)
        used = np.zeros(N, bool)
        used[np.unique(s)] = True
        col = beta[:N] - beta[N:]
        col[~used] = np.nan
        out[:, pos[j]] = col
    np.fill_diagonal(out, np.nan)
    return out


# ----------------------------------------------------------------------------- network and control

def exposure_rates(R: pl.DataFrame, agents: list[int], active_hours: float) -> np.ndarray:
    """r_ij: messages from i absorbed by j's talk turns (visible rows), per active hour of the unit."""
    N = len(agents)
    pos = {a: i for i, a in enumerate(agents)}
    Rv = R.filter(pl.col("vis") & (pl.col("kind") == 0) & pl.col("sender").is_in(agents) & pl.col("recv").is_in(agents))
    M = np.zeros((N, N))
    if Rv.height:
        np.add.at(M, (np.array([pos[a] for a in Rv["sender"].to_list()]), np.array([pos[a] for a in Rv["recv"].to_list()])), 1)
    return M / max(active_hours, 1e-9)


def build_Q(A: np.ndarray, gamma) -> np.ndarray:
    A = np.nan_to_num(np.clip(A, 0, None))
    np.fill_diagonal(A, 0)
    N = A.shape[0]
    g = np.broadcast_to(np.asarray(gamma, dtype=float), (N,))
    Q = A.T.copy()
    Q[np.diag_indices(N)] = -A.sum(0) - g
    return Q


def gramian_scores(Q: np.ndarray, T: float = T_HORIZON_H, dt_h: float = DT_H) -> dict:
    """Single-driver scores for every agent k (B = e_k), finite horizon T (hours):
    D_k = int_0^T (1' e^{Qt} e_k)^2 dt  (mean-output reachability); E_k = N^2 / D_k (energy to shift the swarm mean
    by one unit at T through k alone); AC_k = tr W_k (average controllability); G_k = int_0^T 1' e^{Qt} e_k dt / N
    (mean impulse response, the swarm-mean displacement-hours per unit kick at k)."""
    N = Q.shape[0]
    step = expm(Q * dt_h)
    P = np.eye(N)
    D = np.zeros(N)
    AC = np.zeros(N)
    G = np.zeros(N)
    nstep = int(round(T / dt_h))
    for s in range(nstep):
        # trapezoid on the grid: weight 0.5 at ends
        w = dt_h * (0.5 if s == 0 else 1.0)
        col = P.sum(0)
        D += w * col ** 2
        AC += w * (P ** 2).sum(0)
        G += w * col / N
        P = step @ P
    col = P.sum(0)
    D += 0.5 * dt_h * col ** 2
    AC += 0.5 * dt_h * (P ** 2).sum(0)
    G += 0.5 * dt_h * col / N
    E = N ** 2 / np.where(D > 0, D, np.nan)
    return dict(D=D, E=E, AC=AC, G=G)


def lsb_drivers(adj: np.ndarray, self_loops: bool = False) -> dict:
    """Liu-Slotine-Barabasi structural controllability on a directed graph adj[i, j] = 1 if i -> j.
    N_D = max(N - |M*|, 1), drivers = nodes whose in-copy is unmatched in a maximum matching.
    Classes (Jia et al. 2013): critical (driver in every maximum matching), redundant (never), intermittent.
    With self_loops (nodal dynamics) every node matches itself; N_D = number of root strongly connected components."""
    N = adj.shape[0]
    A = (np.nan_to_num(adj) > 0).astype(int)
    np.fill_diagonal(A, 1 if self_loops else 0)

    def match_size(M):
        if M.sum() == 0:
            return 0, np.full(M.shape[1], -1)
        m = maximum_bipartite_matching(csr_matrix(M), perm_type="row")  # m[j] = row matched to column j
        return int((m >= 0).sum()), m

    size, m = match_size(A)
    nd = max(N - size, 1)
    drivers = [int(j) for j in range(N) if m[j] < 0] or [0]
    cls = []
    for j in range(N):
        Aj = A.copy()
        Aj[:, j] = 0  # remove in-copy j: can j be unmatched in some maximum matching?
        sj, _ = match_size(Aj)
        can_unmatched = sj == size
        # can j be matched in some maximum matching? some in-neighbour i with match(A - row i - col j) = size - 1
        can_matched = False
        for i in np.nonzero(A[:, j])[0]:
            Ak = A.copy()
            Ak[i, :] = 0
            Ak[:, j] = 0
            sk, _ = match_size(Ak)
            if sk == size - 1:
                can_matched = True
                break
        cls.append("critical" if not can_matched else ("intermittent" if can_unmatched else "redundant"))
    ncomp, lab = connected_components(csr_matrix(A - np.diag(np.diag(A))), directed=True, connection="strong")
    # root SCCs: no incoming edge from another SCC
    has_in = np.zeros(ncomp, bool)
    ii, jj = np.nonzero(A - np.diag(np.diag(A)))
    for i, j in zip(ii, jj):
        if lab[i] != lab[j]:
            has_in[lab[j]] = True
    n_root = int((~has_in).sum())
    return dict(N=N, N_D=int(nd) if not self_loops else max(n_root, 1), matching=size, drivers=drivers, classes=cls,
                n_root_scc=n_root, n_scc=int(ncomp))


# ----------------------------------------------------------------------------- restoring rate

def gamma_unit(U: dict, win_min: int = 30, min_windows: int = 6, day_set: set[int] | None = None) -> dict:
    """Common restoring rate Gamma (per hour): decay of an agent's content deviations from its own unit mean, from
    30-min window means, noise-corrected by the lag-2 / lag-1 autocorrelation ratio (readout noise cancels)."""
    T = U["turns"] if day_set is None else U["turns"].filter(pl.col("day_idx").is_in(list(day_set)))
    X = U["X"]
    rho = []
    for (a,), sub in T.group_by(["agent"], maintain_order=True):
        xi = X[vec_index(U, sub["msg"].to_numpy())]
        t = sub["t_us"].to_numpy()
        d = sub["day_idx"].to_numpy()
        ok = np.isfinite(xi).all(1)
        if ok.sum() < 20:
            continue
        xi, t, d = xi[ok], t[ok], d[ok]
        mu = xi.mean(0)
        w = (t - t.min()) // int(win_min * 60e6)
        keys = d.astype(np.int64) * 10_000 + (w - w.min())
        uk, inv = np.unique(keys, return_inverse=True)
        if len(uk) < min_windows:
            continue
        V = np.zeros((len(uk), xi.shape[1]))
        np.add.at(V, inv, xi - mu)
        V /= np.bincount(inv)[:, None]
        c1, c2 = [], []
        kd = uk // 10_000
        kw = uk % 10_000
        lookup = {(int(a_), int(b_)): q for q, (a_, b_) in enumerate(zip(kd, kw))}
        for q, (a_, b_) in enumerate(zip(kd, kw)):
            q1 = lookup.get((int(a_), int(b_) + 1))
            q2 = lookup.get((int(a_), int(b_) + 2))
            if q1 is not None:
                c1.append((V[q] * V[q1]).sum())
            if q2 is not None:
                c2.append((V[q] * V[q2]).sum())
        if len(c1) >= 5 and len(c2) >= 5 and np.mean(c1) > 0:
            rho.append(np.clip(np.mean(c2) / np.mean(c1), 0.05, 0.99))
    if not rho:
        return dict(gamma=1.0, rho_med=np.nan, n=0)
    r = float(np.median(rho))
    return dict(gamma=float(-np.log(r) * (60 / win_min)), rho_med=r, n=len(rho))


# ----------------------------------------------------------------------------- observed spread (validators)

def active_hours(U: dict, days: list[str] | None = None) -> float:
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "window_s"])
    dd = days if days is not None else U["meta"]["days"]
    return float(cal.filter(pl.col("pt_date").is_in(dd))["window_s"].sum()) / 3600.0


def per_message_spread(R: pl.DataFrame, day_set: set[int] | None = None) -> pl.DataFrame:
    """One-step observed spread per message: sum over recipients of (dsim - dsim_x) for visible rows."""
    Rv = R.filter(pl.col("vis") & pl.col("dsim_x").is_not_nan())
    if day_set is not None:
        Rv = Rv.filter(pl.col("day_idx").is_in(list(day_set)))
    return Rv.group_by("msg", "kind", "sender", "day_idx").agg(
        (pl.col("dsim") - pl.col("dsim_x")).sum().alias("spread1"),
        (pl.col("dsim") - pl.col("dsim_x")).mean().alias("pull1"), pl.len().alias("n_recv"),
        pl.col("ment_j").sum().alias("n_named"))


def horizon_spread(U: dict, msgs_sel: pl.DataFrame, H_h: float = SPREAD_H, window_min: float = 15.0,
                   seed: int = SEED) -> pl.DataFrame:
    """Swarm spread toward message m over H hours, against a CONTEMPORANEOUS placebo (amended 2026-10-04 on synthetic
    data, before any real-data run): m* = the agent message nearest in time (|dt| <= window_min) in the same room by a
    different agent (sender l). For every other agent j (j not k, not l) with a statement before t_m and one in
    (t_m, t_m + H] on the same day: contribution (x_j,after - x_j,before) . (x_m - x_m*), 'after' = j's last statement in
    the horizon, 'before' = j's last statement before t_m. A common topic drift enters x_m and x_m* alike and cancels.
    Returns per message: spreadH (sum over j), split by j in the sender's room or not, and dd = |x_m - x_m*|^2."""
    msgs = U["msgs"]
    X = U["X"]
    ag = msgs.filter(pl.col("kind") == 0).sort("t_us")
    sel = msgs_sel.sort("t_us")
    H_us = int(H_h * 3600e6)
    W_us = int(window_min * 60e6)
    rows = []
    for (d,), Sd in sel.group_by(["pt_date"], maintain_order=True):
        Ad = ag.filter(pl.col("pt_date") == d)
        if Ad.height < 3:
            continue
        a_t = Ad["t_us"].to_numpy()
        a_m = Ad["msg"].to_numpy().astype(np.int64)
        a_s = Ad["sender"].to_numpy()
        a_r = Ad["room"].to_numpy()
        q_t = Sd["t_us"].to_numpy()
        q_m = Sd["msg"].to_numpy().astype(np.int64)
        q_s = Sd["sender"].to_numpy()
        q_r = Sd["room"].to_numpy()
        q_k = Sd["kind"].to_numpy()
        n = len(q_t)
        part = np.full(n, -1, dtype=np.int64)
        part_s = np.full(n, -99, dtype=np.int64)
        for r in np.unique(q_r):
            inr = np.where(a_r == r)[0]
            if not len(inr):
                continue
            tr = a_t[inr]
            for qq in np.where(q_r == r)[0]:
                i0 = np.searchsorted(tr, q_t[qq])
                best, bdt = -1, W_us + 1
                for step in range(0, 12):
                    for ii in (i0 - 1 - step, i0 + step):
                        if 0 <= ii < len(inr):
                            g = inr[ii]
                            if a_m[g] == q_m[qq] or (q_k[qq] == 0 and a_s[g] == q_s[qq]):
                                continue
                            dtv = abs(int(a_t[g]) - int(q_t[qq]))
                            if dtv < bdt:
                                best, bdt = g, dtv
                if best >= 0 and bdt <= W_us:
                    part[qq] = a_m[best]
                    part_s[qq] = a_s[best]
        ok = part >= 0
        if not ok.any():
            continue
        xm = X[vec_index(U, q_m)]
        xs = np.full_like(xm, np.nan)
        xs[ok] = X[vec_index(U, part[ok])]
        dvec = xm - xs
        good = ok & np.isfinite(dvec).all(1)
        spread = np.zeros(n)
        sp_same = np.zeros(n)
        sp_other = np.zeros(n)
        n_same = np.zeros(n, dtype=np.int32)
        n_other = np.zeros(n, dtype=np.int32)
        for (j,), Aj in Ad.group_by(["sender"], maintain_order=True):
            tj = Aj["t_us"].to_numpy()
            xj = X[vec_index(U, Aj["msg"].to_numpy())]
            rj = Aj["room"].to_numpy()
            ib = np.searchsorted(tj, q_t, "left") - 1
            ia = np.searchsorted(tj, q_t + H_us, "right") - 1
            use = good & (ib >= 0) & (ia > ib) & ~((q_k == 0) & (q_s == j)) & (part_s != j)
            if not use.any():
                continue
            disp = xj[np.clip(ia, 0, None)] - xj[np.clip(ib, 0, None)]
            c = np.where(use, np.nan_to_num((disp * np.nan_to_num(dvec)).sum(1)), 0.0)
            c = np.where(np.isfinite(disp).all(1), c, 0.0)
            same = rj[np.clip(ib, 0, None)] == q_r
            spread += c
            sp_same += np.where(same, c, 0.0)
            sp_other += np.where(~same, c, 0.0)
            n_same += (use & same).astype(np.int32)
            n_other += (use & ~same).astype(np.int32)
        dd = np.where(good, (np.nan_to_num(dvec) ** 2).sum(1), np.nan)
        di = Sd["day_idx"].to_numpy() if "day_idx" in Sd.columns else np.full(n, -1)
        for qq in np.where(good)[0]:
            rows.append((int(q_m[qq]), int(q_k[qq]), int(q_s[qq]), int(di[qq]), float(spread[qq]), float(sp_same[qq]),
                         float(sp_other[qq]), int(n_same[qq]), int(n_other[qq]), float(dd[qq])))
    return pl.DataFrame(rows, orient="row", schema={"msg": pl.Int64, "kind": pl.Int8, "sender": pl.Int16,
                                                    "day_idx": pl.Int16, "spreadH": pl.Float64, "spreadH_same": pl.Float64,
                                                    "spreadH_other": pl.Float64, "n_same": pl.Int32, "n_other": pl.Int32,
                                                    "dd": pl.Float64})


def hourly_spread(hs: pl.DataFrame, agents: list[int], hours: float, day_set: set[int] | None = None) -> np.ndarray:
    """V2 per sender: sum of 2-h swarm spread over the sender's messages / mean |x_m - x_m*|^2 / active hours."""
    h = hs if day_set is None else hs.filter(pl.col("day_idx").is_in(list(day_set)))
    g = h.filter(pl.col("kind") == 0).group_by("sender").agg(pl.col("spreadH").sum().alias("s"), pl.col("dd").mean().alias("dd"))
    mp = {a: (s / dd if dd and dd > 0 else np.nan) for a, s, dd in zip(g["sender"].to_list(), g["s"].to_list(), g["dd"].to_list())}
    return np.array([mp.get(a, np.nan) for a in agents]) / max(hours, 1e-9)


# ----------------------------------------------------------------------------- Amendment 2 (post hoc): visibility boundary

DT_BINS_RD = (0.0, 10.0, 20.0, 30.0)          # seconds before the talk, matched bins for the boundary test
C_MAX_S = 30.0 if DATA_VERSION == "r1" else float("inf")   # 'truly invisible': call window <= 30 s (round 1, H18 rule);
                                                           # under the ledger every invisible row is strictly invisible
DT_BINS_ADJ = (0, 10, 20, 30, 60, 120, 240, 480, 960, 1920, 1e12)


def add_timing(U: dict, R: pl.DataFrame) -> pl.DataFrame:
    """dt_talk = t_talk - t_m (s) and c = t_talk - s (call window, s) for every row."""
    tm = U["msgs"].select(pl.col("msg").cast(pl.UInt32), pl.col("t_us").alias("tm"))
    tt = U["turns"].select("talk_id", "s_us")
    return (R.join(tm, on="msg", how="left").join(tt, on="talk_id", how="left")
            .with_columns(((pl.col("t_us") - pl.col("tm")) / 1e6).alias("dt_talk"),
                          ((pl.col("t_us") - pl.col("s_us")) / 1e6).alias("c"))
            .drop("tm", "s_us"))


def rd_kappa(R: pl.DataFrame, bins=DT_BINS_RD, c_max: float = C_MAX_S, B: int = 1000, seed: int = SEED,
             kinds=(0,)) -> dict:
    """Visibility jump at matched time-to-reply: in each dt bin, field-corrected pull of visible rows minus that of
    truly invisible rows (posted during a call window <= c_max s); weighted mean over bins (weights = harmonic mean of
    the two counts). Day-block bootstrap. Agent senders by default."""
    Rk = R.filter(pl.col("kind").is_in(list(kinds)) & pl.col("yu_x").is_not_nan())
    days = sorted(set(Rk["day_idx"].to_list()))
    dpos = {d: i for i, d in enumerate(days)}
    nb = len(bins) - 1
    S = np.zeros((len(days), 2, nb, 5))  # [vis/inv][bin][yu, uu, yux, uux, n]
    for v, flt in ((0, pl.col("vis")), (1, ~pl.col("vis") & (pl.col("c") <= c_max))):
        sub = Rk.filter(flt & (pl.col("dt_talk") >= bins[0]) & (pl.col("dt_talk") < bins[-1]))
        if not sub.height:
            continue
        b = np.clip(np.searchsorted(np.array(bins), sub["dt_talk"].to_numpy(), side="right") - 1, 0, nb - 1)
        di = np.array([dpos[d] for d in sub["day_idx"].to_list()])
        for c, col in enumerate(("yu", "uu", "yu_x", "uu_x")):
            np.add.at(S[:, v, :, c], (di, b), sub[col].to_numpy())
        np.add.at(S[:, v, :, 4], (di, b), 1)

    def est(T):
        with np.errstate(invalid="ignore", divide="ignore"):
            pull = T[:, :, 0] / T[:, :, 1] - T[:, :, 2] / T[:, :, 3]
        n = T[:, :, 4]
        w = np.where((n[0] >= 5) & (n[1] >= 5), 2 * n[0] * n[1] / np.maximum(n[0] + n[1], 1), 0)
        d = pull[0] - pull[1]
        ok = w > 0
        if not ok.any():
            return np.nan, pull
        return float((w[ok] * d[ok]).sum() / w[ok].sum()), pull

    tot = S.sum(0)
    jump, pull = est(tot)
    rng = np.random.default_rng(seed)
    bs = []
    if len(days) >= 2:
        for _ in range(B):
            wd = np.bincount(rng.integers(len(days), size=len(days)), minlength=len(days)).astype(float)
            bs.append(est((S * wd[:, None, None, None]).sum(0))[0])
    bs = np.array([x for x in bs if np.isfinite(x)])
    return dict(jump=jump, ci=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))] if len(bs) else None,
                p_le0=float((bs <= 0).mean()) if len(bs) else None, pull_vis=pull[0].tolist(), pull_inv=pull[1].tolist(),
                n_vis=tot[0, :, 4].tolist(), n_inv=tot[1, :, 4].tolist(),
                frac_inv_long_window=float(R.filter(~pl.col("vis"))["c"].gt(c_max).mean()) if R.filter(~pl.col("vis")).height else None)


def pair_kappa_prox(R: pl.DataFrame, agents: list[int], base: float, B: int = 300, seed: int = SEED,
                    n_min: int = N_MIN_PAIR) -> dict:
    """Proximity-adjusted per-pair pull: base (the unit's visibility jump) + the pair's residual pull after removing
    the unit-level field-corrected pull at the same time-to-reply (dt bins). Day-bootstrap SEs, EB shrinkage."""
    Ra = R.filter(pl.col("vis") & (pl.col("kind") == 0) & pl.col("sender").is_in(agents) & pl.col("recv").is_in(agents)
                  & pl.col("yu_x").is_not_nan())
    bins = np.array(DT_BINS_ADJ)
    b = np.clip(np.searchsorted(bins, Ra["dt_talk"].to_numpy(), side="right") - 1, 0, len(bins) - 2)
    yu, uu, yx, ux = (Ra[c].to_numpy() for c in ("yu", "uu", "yu_x", "uu_x"))
    nb = len(bins) - 1
    f = np.array([yu[b == q].sum() / uu[b == q].sum() if uu[b == q].sum() > 0 else 0 for q in range(nb)])
    fx = np.array([yx[b == q].sum() / ux[b == q].sum() if ux[b == q].sum() > 0 else 0 for q in range(nb)])
    ryu = yu - f[b] * uu
    ryx = yx - fx[b] * ux
    N = len(agents)
    pos = {a: i for i, a in enumerate(agents)}
    days = sorted(set(Ra["day_idx"].to_list()))
    dpos = {d: i for i, d in enumerate(days)}
    S = np.zeros((len(days), 5, N, N))
    if Ra.height:
        di = np.array([dpos[d] for d in Ra["day_idx"].to_list()])
        si = np.array([pos[a] for a in Ra["sender"].to_list()])
        ri = np.array([pos[a] for a in Ra["recv"].to_list()])
        for c, arr in enumerate((ryu, uu, ryx, ux)):
            np.add.at(S[:, c], (di, si, ri), arr)
        np.add.at(S[:, 4], (di, si, ri), 1)

    def est(T):
        with np.errstate(invalid="ignore", divide="ignore"):
            k = base + T[0] / T[1] - T[2] / T[3]
        k[T[4] < n_min] = np.nan
        np.fill_diagonal(k, np.nan)
        return k

    tot = S.sum(0)
    K = est(tot)
    rng = np.random.default_rng(seed)
    nd = len(days)
    se = np.full_like(K, np.nan)
    if nd >= 2:
        bs = np.stack([est((S * np.bincount(rng.integers(nd, size=nd), minlength=nd)[:, None, None, None]).sum(0))
                       for _ in range(B)])
        se = np.nanstd(bs, axis=0)
    se = np.where(np.isfinite(se) & (se > 0), se, np.nan)
    ok = np.isfinite(K) & np.isfinite(se)
    Ks = K.copy()
    if ok.sum() >= 5:
        w = 1.0 / se[ok] ** 2
        ii, jj = np.where(ok)
        Xd = np.zeros((ok.sum(), 2 * N + 1))
        Xd[:, 0] = 1
        Xd[np.arange(len(ii)), 1 + ii] = 1
        Xd[np.arange(len(ii)), 1 + N + jj] = 1
        Wm = Xd * w[:, None]
        reg = np.eye(2 * N + 1) * np.median(w)
        reg[0, 0] = 0
        beta = np.linalg.solve(Xd.T @ Wm + reg, Wm.T @ K[ok])
        full = beta[0] + beta[1:1 + N][:, None] + beta[1 + N:][None, :]
        resid = K[ok] - full[ok]
        tau2 = max(float(np.average(resid ** 2, weights=w) - np.average(se[ok] ** 2, weights=w)), 1e-8)
        shrink = tau2 / (tau2 + se ** 2)
        Ks = np.where(ok, shrink * K + (1 - shrink) * full, np.where(tot[4] > 0, full, np.nan))
        np.fill_diagonal(Ks, np.nan)
    return dict(agents=agents, K=K, se=se, Ks=Ks, n=tot[4], z=K / se)


def fit_network_v2(U: dict, R: pl.DataFrame, agents: list[int], day_set: set[int] | None = None,
                   gamma: float | None = None, base: float | None = None, B_pair: int = 200, seed: int = SEED,
                   floor_base: bool = True) -> dict:
    """Amendment 2 network: base = visibility jump (rd_kappa; floored at 0), proximity-adjusted pair residuals."""
    Rs = R if day_set is None else R.filter(pl.col("day_idx").is_in(list(day_set)))
    days = U["meta"]["days"]
    dsel = days if day_set is None else [days[d] for d in sorted(day_set)]
    rd = rd_kappa(Rs, B=100, seed=seed) if base is None else dict(jump=base)
    b0 = rd["jump"] if np.isfinite(rd.get("jump", np.nan)) else 0.0
    if floor_base:
        b0 = max(b0, 0.0)
    pk = pair_kappa_prox(Rs, agents, b0, B=B_pair, seed=seed)
    hours = active_hours(U, dsel)
    r = exposure_rates(Rs, agents, hours)
    A = np.clip(np.where(np.isfinite(pk["Ks"]), pk["Ks"], 0.0), 0, None) * r
    np.fill_diagonal(A, 0)
    g = gamma if gamma is not None else gamma_unit(U, day_set=day_set)["gamma"]
    Q = build_Q(A, g)
    sc = gramian_scores(Q)
    return dict(agents=agents, rd=rd, base=b0, pair=pk, K=pk["Ks"], A=A, r=r, gamma=g, Q=Q, D=sc["D"], E=sc["E"],
                AC=sc["AC"], G=sc["G"], out=A.sum(1), inn=A.sum(0), net=A.sum(1) - A.sum(0),
                vol=message_rates(U, agents, day_set), hours=hours)


# ----------------------------------------------------------------------------- full fit

def message_rates(U: dict, agents: list[int], day_set: set[int] | None = None) -> np.ndarray:
    m = U["msgs"].filter(pl.col("kind") == 0)
    days = U["meta"]["days"]
    if day_set is not None:
        m = m.filter(pl.col("pt_date").is_in([days[d] for d in day_set]))
        hours = active_hours(U, [days[d] for d in day_set])
    else:
        hours = active_hours(U)
    cnt = dict(zip(*[x.to_list() for x in m.group_by("sender").len().get_columns()]))
    return np.array([cnt.get(a, 0) for a in agents], dtype=float) / max(hours, 1e-9)


def fit_network(U: dict, R: pl.DataFrame, agents: list[int], day_set: set[int] | None = None,
                estimator: str = "marginal", gamma: float | None = None, clip: bool = True,
                gamma_mult: float = 1.0, B_unit: int = 200, B_pair: int = 200, seed: int = SEED) -> dict:
    """Estimate kappa, the influence network A (per active hour), Q and the driver scores on a subset of days."""
    Rs = R if day_set is None else R.filter(pl.col("day_idx").is_in(list(day_set)))
    days = U["meta"]["days"]
    dsel = days if day_set is None else [days[d] for d in sorted(day_set)]
    ku = kappa_unit(Rs, B=B_unit, seed=seed)
    c = ku["contamination"] if np.isfinite(ku.get("contamination", np.nan)) else 0.0
    if estimator == "marginal":
        pk = pair_kappa(Rs, agents, c, B=B_pair, seed=seed)
        K = pk["Ks"]
    elif estimator == "joint":
        pk = None
        K = joint_pull(Rs, U, agents) - c
    else:
        raise ValueError(estimator)
    hours = active_hours(U, dsel)
    r = exposure_rates(Rs, agents, hours)
    A = np.where(np.isfinite(K), K, 0.0) * r
    if clip:
        A = np.clip(A, 0, None)
    np.fill_diagonal(A, 0)
    g = gamma if gamma is not None else gamma_unit(U, day_set=day_set)["gamma"]
    g = g * gamma_mult
    Q = build_Q(A, g) if clip else _build_Q_signed(A, g)
    sc = gramian_scores(Q)
    return dict(agents=agents, kappa_unit=ku, pair=pk, K=K, A=A, r=r, gamma=g, Q=Q, D=sc["D"], E=sc["E"],
                AC=sc["AC"], G=sc["G"], out=A.sum(1), inn=A.sum(0), net=A.sum(1) - A.sum(0),
                vol=message_rates(U, agents, day_set), hours=hours)


def _build_Q_signed(A: np.ndarray, gamma) -> np.ndarray:
    A = np.nan_to_num(A.copy())
    np.fill_diagonal(A, 0)
    N = A.shape[0]
    Q = A.T.copy()
    Q[np.diag_indices(N)] = -A.sum(0) - np.broadcast_to(np.asarray(gamma, dtype=float), (N,))
    return Q


def network_agents(U: dict, min_turns: int = 20) -> list[int]:
    """Agents in the network: recipients with >= min_turns talk turns in the unit that also send messages."""
    T = U["turns"].group_by("agent").len()
    return sorted(int(a) for a, n in zip(T["agent"].to_list(), T["len"].to_list()) if n >= min_turns)


# ----------------------------------------------------------------------------- misc

def spearman(a, b) -> float:
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 4 or np.std(a[ok]) == 0 or np.std(b[ok]) == 0:
        return np.nan
    return float(spearmanr(a[ok], b[ok]).statistic)


def git_commit() -> str:
    r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain"], capture_output=True, text=True).stdout
    return (r.stdout.strip() or "none") + ("+uncommitted" if dirty.strip() else "")


def write_provenance(entry: str, built_by: str, params: dict, root: Path = OUT):
    root.mkdir(parents=True, exist_ok=True)
    p = root / "_provenance.json"
    prov = json.loads(p.read_text()) if p.exists() else {}
    if "built_by" in prov:     # the scheme's top-level record: keep it as the 'scheme' entry
        prov = {"scheme": prov}
    prov[entry] = {"built_by": built_by, "git_commit": git_commit(),
                   "inputs": [{"source": "ai-village", "revision": REVISION,
                               "tables": ["H29 scheme outputs", f"shared/embeddings/chat_{EMB_MODEL}", "shared/embeddings/chat_index",
                                          "shared/embeddings/whitening[_model]_III", "shared/calendar"]}],
                   "params": {**params, "data_version": DATA_VERSION, "embedding": EMB_MODEL},
                   "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    p.write_text(json.dumps(prov, indent=1, default=str))


def jdump(obj, path: Path):
    def conv(o):
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return None if not np.isfinite(o) else float(o)
        if isinstance(o, np.ndarray):
            return [conv(x) for x in o.tolist()] if o.ndim else conv(o.item())
        if isinstance(o, float):
            return None if not np.isfinite(o) else o
        if isinstance(o, dict):
            return {str(k): conv(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [conv(x) for x in o]
        return o
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(conv(obj), indent=1))
