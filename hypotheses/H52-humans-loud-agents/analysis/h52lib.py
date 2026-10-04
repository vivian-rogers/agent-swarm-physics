"""H52 library: sender-class premium on the read-out-gated, name-gated channel.

Two layers:
1. Village loaders and the per-row content statistic (used by scheme/build.py). Shared tables only; holdout days are
   refused unless allow_holdout=True (only analysis/confirm.py passes it).
2. Estimators (CEM ATT, regression adjustment, day-block / message-cluster bootstrap, placebo-class null,
   random-effects pooling), used by analysis/synthetic.py, analysis/run_period.py and the native tests.

Definitions are on the card (hypotheses/H52-humans-loud-agents/README.md). Read-only imports (never modified):
  hypotheses/H30-operator-susceptibility/analysis/h30lib.py   content_scores / _orth_basis (verification of `chi`)
  hypotheses/H29-driver-nodes/analysis/h29lib.py              rd_kappa (boundary design per class)
Threads pinned low: callers use at most 2 processes.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")
os.environ.setdefault("POLARS_MAX_THREADS", "2")

import datetime as dt  # noqa: E402
import json  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
HYP = ROOT / "hypotheses/H52-humans-loud-agents"
SH = ROOT / "data/processed/shared"
ED = SH / "embeddings"
OUT = ROOT / "data/processed/H52-humans-loud-agents"
FIG = HYP / "figures"
HOLDOUT = json.loads((ROOT / "hypotheses/holdout.json").read_text())
SEED = 20261004
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION  # noqa: E402

CLS = {"agent": 0, "human": 1, "nudge": 2}
CLS_NAME = {0: "agent", 1: "human", 2: "bot", 3: "leader"}
IDLE_GAPS = ("pause", "pause_early", "first_of_day", "session_start")
N_PL = 30              # placebo messages per row (content)
PRE_WIN, POST_WIN, BASIS_WIN = 3600.0, 3600.0, 7200.0
K_PRE, K_POST, K_BASIS = 5, 5, 8
AGENT_CAP = 300_000    # agent rows kept per period (uniform seeded subsample; humans and bots always kept)

# CEM bins (card, "Estimator")
AGE_EDGES = np.array([30.0, 120.0, 600.0, 1800.0])           # 0-30 s | 30-120 s | 2-10 min | 10-30 min | > 30 min
ROOM_EDGES = np.array([4, 8, 16])                              # 1-3 | 4-7 | 8-15 | >= 16 recipients
PRE15_EDGES = np.array([1, 4, 8, 12, 15])                      # 0 | 1-3 | 4-7 | 8-11 | 12-14 | 15 (A1: finer)
KNEW_EDGES = np.array([2, 3, 4, 5, 7, 10, 15, 25])             # 1 | 2 | 3 | 4 | 5-6 | 7-9 | 10-14 | 15-24 | >= 25 (A1)

# Periods (non-holdout parts). Native tests are on the card; date windows exclude nothing beyond the holdout mask.
REPLICATION = ["G03", "G04", "G05", "G06", "G08", "G10", "G12", "G13", "G16", "G17", "G18", "G20", "G23", "G30",
               "G38", "G44", "G51"]
EXTRA = ["G26", "G31", "G33", "G35", "G36", "G37", "G39", "G40", "G41", "G42"]   # native leader tests / bot-only
PERIODS = {p: dict(goal=int(p[1:3])) for p in REPLICATION + EXTRA}


# =============================================================================== io helpers

def git_commit() -> str:
    r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "--", str(HYP)], capture_output=True,
                           text=True).stdout
    return (r.stdout.strip() or "none") + ("+uncommitted" if dirty.strip() else "")


def write_provenance(folder: Path, built_by: str, tables: list[str], params: dict):
    folder.mkdir(parents=True, exist_ok=True)
    prov = {"built_by": built_by, "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION, "tables": tables}],
            "params": params, "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (folder / "_provenance.json").write_text(json.dumps(prov, indent=1, default=str))


def jdump(obj, path: Path):
    def conv(o):
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return None if not np.isfinite(o) else float(o)
        if isinstance(o, np.ndarray):
            return [conv(x) for x in o.tolist()]
        if isinstance(o, float) and not np.isfinite(o):
            return None
        return str(o)
    path.parent.mkdir(parents=True, exist_ok=True)

    def clean(x):
        if isinstance(x, dict):
            return {str(k): clean(v) for k, v in x.items()}
        if isinstance(x, (list, tuple)):
            return [clean(v) for v in x]
        if isinstance(x, float) and not np.isfinite(x):
            return None
        if isinstance(x, (np.floating,)):
            return None if not np.isfinite(x) else float(x)
        if isinstance(x, (np.integer,)):
            return int(x)
        return x
    path.write_text(json.dumps(clean(obj), indent=1, default=conv))


# =============================================================================== calendar / holdout

def is_holdout(d: str, goal_no) -> bool:
    if goal_no in set(HOLDOUT["goal_periods_held_out"]):
        return True
    return any(w["start"] <= d < w["end"] for w in HOLDOUT["ne_windows"])


def period_days(goal: int, allow_holdout: bool = False, date_from: str | None = None,
                date_to: str | None = None) -> list[str]:
    cal = pl.read_parquet(SH / "calendar.parquet").filter(pl.col("goal_no") == goal)
    days = sorted(cal["pt_date"].to_list())
    if date_from:
        days = [d for d in days if d >= date_from]
    if date_to:
        days = [d for d in days if d <= date_to]
    if not allow_holdout:
        days = [d for d in days if not is_holdout(d, goal)]
    return days


def assert_no_holdout(days: list[str], goal: int):
    bad = [d for d in days if is_holdout(d, goal)]
    if bad:
        raise RuntimeError(f"holdout days requested in exploratory mode: {bad[:3]}")


# =============================================================================== vectors

def unit(x: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(x, axis=-1, keepdims=True)
    return x / np.where(n > 0, n, 1)


def whitener(regime: str, model: str):
    from embed_models import load_whitener
    return load_whitener(regime, 32, model)


def message_vectors(msgs: np.ndarray, regime: str, model: str = "bge_small") -> np.ndarray:
    """(len(msgs), 32) unit whitened vectors for chat_core row indices `msgs` (NaN where no embedding)."""
    from embed_models import emb_path
    cc = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id"]).with_row_index("msg")
    ci = pl.read_parquet(ED / "chat_index.parquet").with_row_index("erow")
    erow = cc.join(ci, on="message_id", how="left").sort("msg")["erow"].fill_null(-1).to_numpy().astype(np.int64)
    E = np.load(emb_path("chat", model), mmap_mode="r")
    W = whitener(regime, model)
    out = np.full((len(msgs), 32), np.nan, np.float32)
    rows = erow[msgs]
    ok = rows >= 0
    if ok.any():
        r = rows[ok]
        o = np.argsort(r)
        X = np.asarray(E[r[o]], np.float32)
        V = unit(W(X)).astype(np.float32)
        tmp = np.empty_like(V)
        tmp[o] = V
        out[ok] = tmp
    return out


def statement_table(days: list[str], model: str = "bge_small", variant: str = "white32"):
    """Statements (agent chat + intentions) on `days`: agent, ts, vec (32-d unit), kind, src_row, srow."""
    st = pl.read_parquet(ED / "statements.parquet").with_row_index("srow").filter(pl.col("pt_date").is_in(days))
    V = np.load(ED / f"statements_{variant}_{model}.npy", mmap_mode="r")
    srow = st["srow"].to_numpy()
    o = np.argsort(srow)
    X = np.asarray(V[srow[o]], np.float32)
    vec = np.empty_like(X)
    vec[o] = X
    ts = (st["t"].dt.epoch("us") / 1e6).to_numpy()
    return st.select("srow", "agent", "kind", "src_row", "pt_date").with_columns(pl.Series("ts", ts)), unit(vec)


# =============================================================================== content statistic (vectorized H30 chi_orth)

def window_indices(st_agent: np.ndarray, st_ts: np.ndarray, recv: np.ndarray, t: np.ndarray):
    """Per row: indices (into the statement arrays, sorted by agent then time) of the last <= K_BASIS pre statements
    within BASIS_WIN, the last <= K_PRE within PRE_WIN (mask), and the first <= K_POST post statements within POST_WIN.
    Pre = ts < t; post = ts >= t. Returns (basis_idx (n, K_BASIS), pre_mask (n, K_BASIS), post_idx (n, K_POST)),
    -1 for missing."""
    n = len(recv)
    bidx = np.full((n, K_BASIS), -1, np.int64)
    pmask = np.zeros((n, K_BASIS), bool)
    qidx = np.full((n, K_POST), -1, np.int64)
    order = np.lexsort((st_ts, st_agent))
    sa, stt = st_agent[order], st_ts[order]
    for a in np.unique(recv):
        lo, hi = np.searchsorted(sa, a, "left"), np.searchsorted(sa, a, "right")
        if hi <= lo:
            continue
        T = stt[lo:hi]
        rows = np.flatnonzero(recv == a)
        tt = t[rows]
        mid = np.searchsorted(T, tt, "left")
        for k in range(K_BASIS):          # k = 0 is the most recent pre statement
            j = mid - 1 - k
            ok = j >= 0
            jj = np.where(ok, j, 0)
            ok &= T[jj] >= tt - BASIS_WIN
            bidx[rows[ok], K_BASIS - 1 - k] = order[lo + jj[ok]]
            pmask[rows[ok & (k < K_PRE) & (T[jj] >= tt - PRE_WIN)], K_BASIS - 1 - k] = True
        for k in range(K_POST):
            j = mid + k
            ok = j < len(T)
            jj = np.where(ok, j, 0)
            ok &= T[jj] < tt + POST_WIN
            qidx[rows[ok], k] = order[lo + jj[ok]]
    return bidx, pmask, qidx


def _gather(V: np.ndarray, idx: np.ndarray) -> np.ndarray:
    X = V[np.where(idx >= 0, idx, 0)]
    X[idx < 0] = 0.0
    return X


def orth_basis_batched(S: np.ndarray) -> np.ndarray:
    """S: (n, k, d) statements (zero rows = missing). Returns B: (n, d, k) with orthonormal columns spanning the
    non-zero rows (the batched equivalent of h30lib._orth_basis). Uses an SVD, so missing (zero) and exactly
    dependent statements are dropped without distorting the span (a QR with zero columns first would)."""
    A = np.transpose(S, (0, 2, 1)).astype(np.float64)          # (n, d, k)
    u, sv, _ = np.linalg.svd(A, full_matrices=False)           # u: (n, d, k), sv: (n, k)
    keep = sv > 1e-6
    return u * keep[:, None, :]


def perp(u: np.ndarray, B: np.ndarray):
    """u: (n, d) or (n, p, d); B: (n, d, k). Returns (unit(u_perp), |u_perp|)."""
    if u.ndim == 2:
        c = np.einsum("nd,ndk->nk", u, B)
        up = u - np.einsum("nk,ndk->nd", c, B)
    else:
        c = np.einsum("npd,ndk->npk", u, B)
        up = u - np.einsum("npk,ndk->npd", c, B)
    nrm = np.linalg.norm(up, axis=-1)
    return up / np.where(nrm > 1e-9, nrm, 1)[..., None], nrm


def content_rows(V: np.ndarray, bidx: np.ndarray, pmask: np.ndarray, qidx: np.ndarray, U: np.ndarray,
                 Upl: np.ndarray, chunk: int = 20000, call_id: np.ndarray | None = None, ridge: float = 0.05) -> dict:
    """Per row: chi = Q . unit(P_perp u) - mean_p Q . unit(P_perp u_p); q_true, q_pl, nov = |P_perp u|, n_pre, n_post.
    V: statement vectors; U: (n, d) message vectors; Upl: (n, N_PL, d) placebo vectors (NaN rows ignored)."""
    n = len(U)
    out = {k: np.full(n, np.nan, np.float32) for k in ("chi", "q_true", "q_pl", "nov", "chi_dd", "dd_true")}
    W2 = np.zeros((n, U.shape[1]), np.float32) if call_id is not None else None
    DL = np.zeros((n, U.shape[1]), np.float32) if call_id is not None else None
    PLM = np.full(n, np.nan, np.float32) if call_id is not None else None
    npre = pmask.sum(1).astype(np.int16)
    npost = (qidx >= 0).sum(1).astype(np.int16)
    nbas = (bidx >= 0).sum(1)
    for s in range(0, n, chunk):
        e = min(n, s + chunk)
        S = _gather(V, bidx[s:e])                                 # (m, K_BASIS, d)
        B = orth_basis_batched(S)
        u = np.nan_to_num(U[s:e].astype(np.float64))
        uh, nrm = perp(u, B)
        hasu = np.isfinite(U[s:e]).all(1)
        nov = np.where(hasu & (nbas[s:e] > 0), nrm, np.nan)
        Q = _gather(V, qidx[s:e]).sum(1) / np.maximum(npost[s:e], 1)[:, None]
        P_ok = npre[s:e] > 0
        okq = npost[s:e] > 0
        qt = np.einsum("nd,nd->n", uh, Q)
        up = Upl[s:e].astype(np.float64)
        okp = np.isfinite(up).all(2)
        uph, _ = perp(np.nan_to_num(up), B)
        qp = np.einsum("npd,nd->np", uph, Q)
        qp_mean = np.where(okp.sum(1) >= 10, (qp * okp).sum(1) / np.maximum(okp.sum(1), 1), np.nan)
        # difference-in-differences variant: basis from the older pre statements (all but the most recent), baseline =
        # the most recent pre statement P_last (made before the receiving call, so it cannot have read m)
        last = bidx[s:e, -1]
        has_last = last >= 0
        P_last = _gather(V, last[:, None])[:, 0]
        S2 = S.copy(); S2[:, -1] = 0.0
        B2 = orth_basis_batched(S2)
        uh2, _ = perp(u, B2)
        dd_t = np.einsum("nd,nd->n", uh2, Q - P_last)
        uph2, _ = perp(np.nan_to_num(up), B2)
        dd_p = np.einsum("npd,nd->np", uph2, Q - P_last)
        dd_pm = np.where(okp.sum(1) >= 10, (dd_p * okp).sum(1) / np.maximum(okp.sum(1), 1), np.nan)
        ok2 = hasu & has_last & okq
        if call_id is not None:
            W2[s:e] = uh2; DL[s:e] = Q - P_last; PLM[s:e] = np.where(ok2, dd_pm, np.nan)
        out["dd_true"][s:e] = np.where(ok2, dd_t, np.nan)
        out["chi_dd"][s:e] = np.where(ok2, dd_t - dd_pm, np.nan)
        ok = hasu & P_ok & okq
        out["q_true"][s:e] = np.where(ok, qt, np.nan)
        out["q_pl"][s:e] = np.where(ok, qp_mean, np.nan)
        out["chi"][s:e] = np.where(ok, qt - qp_mean, np.nan)
        out["nov"][s:e] = nov
    out["n_pre"] = npre
    out["n_post"] = npost
    if call_id is not None:
        # joint per-call deconvolution of the DiD displacement: Delta_c = sum_i beta_i w_i (ridge), over the rows of
        # the call with a defined DiD statistic; chi_jd = beta_i - placebo mean (marginal placebo term)
        jd = np.full(n, np.nan, np.float32)
        okr = np.isfinite(out["chi_dd"])
        idx = np.flatnonzero(okr)
        o = idx[np.argsort(call_id[idx], kind="stable")]
        cid = call_id[o]
        starts = np.r_[0, np.flatnonzero(np.diff(cid)) + 1, len(o)]
        for a_, b_ in zip(starts[:-1], starts[1:]):
            rr = o[a_:b_]
            Wc = W2[rr].astype(np.float64)          # (k, d)
            dl = DL[rr[0]].astype(np.float64)       # shared within the call
            G = Wc @ Wc.T + ridge * np.eye(len(rr))
            beta = np.linalg.solve(G, Wc @ dl)
            jd[rr] = beta - PLM[rr]
        out["chi_jd"] = jd
    return out


def draw_placebos(row_cls: np.ndarray, row_day: np.ndarray, row_recv: np.ndarray, pool: dict, rng,
                  n_pl: int = N_PL, bot_target_pool: dict | None = None, min_same: int = 10) -> np.ndarray:
    """Placebo message indices (n, n_pl), -1 if missing. pool[c] = (msgs, days) of class c in the period;
    rows draw from other days of their own class. Bot rows use nudges whose leading target is the recipient
    when >= min_same exist on other days (H30's rule)."""
    n = len(row_cls)
    out = np.full((n, n_pl), -1, np.int64)
    for c, (pm, pd_) in pool.items():
        rows = np.flatnonzero(row_cls == c)
        if not len(rows) or not len(pm):
            continue
        draw = rng.integers(len(pm), size=(len(rows), 3 * n_pl))
        ok = pd_[draw] != row_day[rows][:, None]
        for i, r in enumerate(rows):
            sel = draw[i][ok[i]][:n_pl]
            out[r, :len(sel)] = pm[sel]
    if bot_target_pool:
        rows = np.flatnonzero(row_cls == 2)
        for r in rows:
            tp = bot_target_pool.get(int(row_recv[r]))
            if tp is None:
                continue
            pm, pd_ = tp
            cand = pm[pd_ != row_day[r]]
            if len(cand) >= min_same:
                out[r] = cand[rng.integers(len(cand), size=n_pl)]
    return out


# =============================================================================== bins

def bin_edges(x: np.ndarray, edges) -> np.ndarray:
    return np.searchsorted(np.asarray(edges), x, side="right").astype(np.int16)


def quantile_bins(x: np.ndarray, q, ref_mask: np.ndarray | None = None) -> tuple[np.ndarray, list]:
    """Bins by quantiles of x (computed on ref_mask rows, finite only); NaN -> bin 0, others 1..len(q)+1."""
    ref = x[np.isfinite(x) & (ref_mask if ref_mask is not None else True)]
    if len(ref) == 0:
        return np.zeros(len(x), np.int16), []
    cuts = list(np.quantile(ref, q))
    b = np.where(np.isfinite(x), 1 + np.searchsorted(np.array(cuts), np.nan_to_num(x), side="right"), 0)
    return b.astype(np.int16), cuts


def room_n(df: pl.DataFrame) -> np.ndarray:
    """Agents in the room = ledger recipients + the sender when the sender is an agent (a human or bot message is
    read by everyone present; an agent message by everyone but its author)."""
    return df["n_recv"].to_numpy().astype(int) + (df["cls"].to_numpy() == 0).astype(int)


def add_strata(df: pl.DataFrame, activity: bool = False, with_named: bool = True) -> pl.DataFrame:
    """Adds `stratum` (int64 code) from the card's CEM bins. Novelty terciles and length quartiles within the frame."""
    age = bin_edges(df["age_s"].to_numpy(), AGE_EDGES)
    nov = df["nov"].to_numpy().astype(float)
    nb, _ = quantile_bins(nov, [1 / 3, 2 / 3])
    ln = np.log1p(df["len"].to_numpy().astype(float))
    lb, _ = quantile_bins(ln, [0.25, 0.5, 0.75])
    idle = df["idle"].to_numpy().astype(np.int16)
    room = bin_edges(room_n(df), ROOM_EDGES)
    named = df["named"].to_numpy().astype(np.int16) if with_named else np.zeros(df.height, np.int16)
    code = ((((named.astype(np.int64) * 5 + age) * 4 + nb) * 4 + (lb - 1).clip(0)) * 2 + idle) * 4 + room
    if activity:
        pre = bin_edges(df["pre15"].to_numpy(), PRE15_EDGES)
        kn = bin_edges(df["k_new"].to_numpy(), KNEW_EDGES)
        code = (code * 6 + pre) * 9 + kn
    return df.with_columns(pl.Series("stratum", code))


def add_strata_coarse(df: pl.DataFrame) -> pl.DataFrame:
    """Coarse strata for the small stance sample (A1): named x read-out age x room size."""
    age = bin_edges(df["age_s"].to_numpy(), AGE_EDGES)
    room = bin_edges(room_n(df), ROOM_EDGES)
    named = df["named"].to_numpy().astype(np.int64)
    return df.with_columns(pl.Series("stratum", (named * 5 + age) * 4 + room))


# =============================================================================== estimators

def cem_sums(y: np.ndarray, treat: np.ndarray, ctrl: np.ndarray, stratum: np.ndarray, cluster: np.ndarray):
    """Per (cluster, stratum) sums for treated and control rows: arrays keyed by compact stratum and cluster ids.
    Returns (S_t, N_t, S_c, N_c) of shape (n_clusters, n_strata) and cluster labels."""
    ok = np.isfinite(y)
    sel = ok & (treat | ctrl)
    sel &= np.isin(stratum, np.unique(stratum[ok & treat]))     # only strata holding treated rows matter for the ATT
    s_lab, s_id = np.unique(stratum[sel], return_inverse=True)
    c_lab, c_id = np.unique(cluster[sel], return_inverse=True)
    ns, nc = len(s_lab), len(c_lab)
    t = treat[sel]
    yy = y[sel]
    St = np.zeros((nc, ns)); Nt = np.zeros((nc, ns)); Sc = np.zeros((nc, ns)); Nc = np.zeros((nc, ns))
    np.add.at(St, (c_id[t], s_id[t]), yy[t]); np.add.at(Nt, (c_id[t], s_id[t]), 1)
    np.add.at(Sc, (c_id[~t], s_id[~t]), yy[~t]); np.add.at(Nc, (c_id[~t], s_id[~t]), 1)
    return St, Nt, Sc, Nc, c_lab


def cem_att(St, Nt, Sc, Nc, w=None) -> tuple[float, float, float]:
    """ATT over treated rows in strata with >= 1 control: (att, matched share, treated mean)."""
    if w is not None:
        St, Nt, Sc, Nc = (w[:, None] * X for X in (St, Nt, Sc, Nc))
    st, nt, sc, nc = St.sum(0), Nt.sum(0), Sc.sum(0), Nc.sum(0)
    m = (nt > 0) & (nc > 0)
    if not m.any() or nt.sum() == 0:
        return np.nan, 0.0, np.nan
    att = float(((st[m] / nt[m] - sc[m] / nc[m]) * nt[m]).sum() / nt[m].sum())
    return att, float(nt[m].sum() / nt.sum()), float(st[m].sum() / nt[m].sum())


def boot_weights(n: int, B: int, rng) -> np.ndarray:
    return np.stack([np.bincount(rng.integers(n, size=n), minlength=n) for _ in range(B)]).astype(float)


def ci(v, q=(2.5, 97.5)):
    v = np.asarray(v, float)
    v = v[np.isfinite(v)]
    return [float(np.percentile(v, q[0])), float(np.percentile(v, q[1]))] if len(v) > 5 else [np.nan, np.nan]


def premium(df: pl.DataFrame, y: str, treat_cls: int, B: int = 1000, seed: int = SEED, cluster: str = "day_idx",
            ctrl_cls: int = 0, mask: np.ndarray | None = None, naive: bool = True) -> dict:
    """CEM ATT of class `treat_cls` vs `ctrl_cls` on outcome y (frame must carry `stratum`), with a cluster bootstrap.
    cluster = 'day_idx' (day blocks) or 'msg_cluster' (both classes resampled by message)."""
    yy = df[y].to_numpy().astype(float)
    cls = df["cls"].to_numpy()
    m = np.ones(df.height, bool) if mask is None else mask
    treat = (cls == treat_cls) & m & np.isfinite(yy)
    ctrl = (cls == ctrl_cls) & m & np.isfinite(yy)
    if treat.sum() < 5 or ctrl.sum() < 5:
        return dict(att=np.nan, ci=[np.nan, np.nan], n_t=int(treat.sum()), n_c=int(ctrl.sum()))
    cl = df[cluster].to_numpy()
    St, Nt, Sc, Nc, clab = cem_sums(yy, treat, ctrl, df["stratum"].to_numpy(), cl)
    att, share, tmean = cem_att(St, Nt, Sc, Nc)
    rng = np.random.default_rng(seed)
    nclu = len(clab)
    bs = []
    if nclu >= 3:
        for w in boot_weights(nclu, B, rng):
            bs.append(cem_att(St, Nt, Sc, Nc, w)[0])
    bs = np.array(bs)
    out = dict(att=att, ci=ci(bs), se=float(np.nanstd(bs)) if len(bs) else np.nan,
               p_le0=float(np.mean(bs[np.isfinite(bs)] <= 0)) if np.isfinite(bs).any() else np.nan,
               matched_share=share, treated_mean=tmean, ctrl_matched_mean=tmean - att if np.isfinite(att) else np.nan,
               n_t=int(treat.sum()), n_c=int(ctrl.sum()), n_clusters=int(nclu), cluster=cluster,
               n_t_msgs=int(df.filter(pl.Series(treat))["msg"].n_unique()))
    if naive:
        nv = float(yy[treat].mean() - yy[ctrl].mean())
        nb = []
        if nclu >= 3:
            Tt = np.zeros(nclu); Ct = np.zeros(nclu); Tn = np.zeros(nclu); Cn = np.zeros(nclu)
            ci_t = np.searchsorted(clab, cl[treat]); ci_c = np.searchsorted(clab, cl[ctrl])
            np.add.at(Tt, ci_t, yy[treat]); np.add.at(Tn, ci_t, 1)
            np.add.at(Ct, ci_c, yy[ctrl]); np.add.at(Cn, ci_c, 1)
            for w in boot_weights(nclu, B, np.random.default_rng(seed + 1)):
                nb.append((w @ Tt) / max(w @ Tn, 1e-9) - (w @ Ct) / max(w @ Cn, 1e-9))
        out["naive"] = nv
        out["naive_ci"] = ci(nb)
        out["naive_se"] = float(np.nanstd(nb)) if len(nb) else np.nan
    return out


def placebo_class_null(df: pl.DataFrame, y: str, treat_cls: int, draws: int = 200, seed: int = SEED) -> dict:
    """N2: agent rows drawn to reproduce the treated rows' stratum counts (by message clusters is not possible for
    agents spread over strata, so rows are drawn within stratum) are relabelled as treated; ATT vs the rest."""
    yy = df[y].to_numpy().astype(float)
    cls = df["cls"].to_numpy()
    s = df["stratum"].to_numpy()
    ok = np.isfinite(yy)
    tr = (cls == treat_cls) & ok
    ag = np.flatnonzero((cls == 0) & ok)
    if tr.sum() < 5 or len(ag) < 50:
        return dict(null_mean=np.nan, null_band=[np.nan, np.nan])
    need = {k: v for k, v in zip(*np.unique(s[tr], return_counts=True))}
    by_s = {}
    for i in ag:
        by_s.setdefault(s[i], []).append(i)
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(draws):
        pick = []
        for k, cnt in need.items():
            pool = by_s.get(k)
            if pool is None or len(pool) < 2:
                continue
            take = min(cnt, len(pool) - 1)
            pick.extend(rng.choice(pool, size=take, replace=False))
        pick = np.array(pick, int)
        if len(pick) < 5:
            continue
        t = np.zeros(len(yy), bool); t[pick] = True
        c = (cls == 0) & ok & ~t
        St, Nt, Sc, Nc, _ = cem_sums(yy, t, c, s, np.zeros(len(yy)))
        vals.append(cem_att(St, Nt, Sc, Nc)[0])
    vals = np.array(vals)
    return dict(null_mean=float(np.nanmean(vals)), null_band=ci(vals), null_sd=float(np.nanstd(vals)), draws=len(vals))


def regression_premium(df: pl.DataFrame, y: str, B: int = 1000, seed: int = SEED, cluster: str = "day_idx",
                       activity: bool = False, mask: np.ndarray | None = None) -> dict:
    """OLS: y ~ class x named indicators + covariate bins (main effects) + day FE + recipient FE. Coefficients for
    human (cls 1) and bot (cls 2), named and unnamed, relative to agent rows of the same named status. Day-block
    bootstrap via per-cluster sufficient statistics."""
    yy = df[y].to_numpy().astype(float)
    m = np.isfinite(yy) if mask is None else (mask & np.isfinite(yy))
    d = df.filter(pl.Series(m))
    if d.height < 50:
        return {}
    yy = yy[m]
    cls = d["cls"].to_numpy(); named = d["named"].to_numpy().astype(int)
    cols = []
    names = []
    for c in (1, 2):
        for nm in (0, 1):
            v = ((cls == c) & (named == nm)).astype(float)
            if v.sum() >= 3:
                cols.append(v); names.append(f"{CLS_NAME[c]}_{'named' if nm else 'unnamed'}")
    cols.append(named.astype(float)); names.append("named")
    cats = [bin_edges(d["age_s"].to_numpy(), AGE_EDGES), quantile_bins(d["nov"].to_numpy().astype(float), [1 / 3, 2 / 3])[0],
            quantile_bins(np.log1p(d["len"].to_numpy().astype(float)), [0.25, 0.5, 0.75])[0],
            d["idle"].to_numpy().astype(int), bin_edges(room_n(d), ROOM_EDGES),
            d["day_idx"].to_numpy(), d["recv"].to_numpy()]
    if activity:
        cats += [bin_edges(d["pre15"].to_numpy(), PRE15_EDGES), bin_edges(d["k_new"].to_numpy(), KNEW_EDGES)]
    X = [np.ones(len(yy))] + cols
    for c in cats:
        u = np.unique(c)
        for v in u[1:]:
            X.append((c == v).astype(float))
    X = np.column_stack(X)
    cl = d[cluster].to_numpy()
    clab, cid = np.unique(cl, return_inverse=True)
    k = X.shape[1]
    XtX = np.zeros((len(clab), k, k)); Xty = np.zeros((len(clab), k))
    for i in range(len(clab)):
        r = cid == i
        XtX[i] = X[r].T @ X[r]; Xty[i] = X[r].T @ yy[r]

    def solve(w):
        A = np.tensordot(w, XtX, 1); b = w @ Xty
        return np.linalg.lstsq(A + 1e-8 * np.eye(k), b, rcond=None)[0]
    beta = solve(np.ones(len(clab)))
    rng = np.random.default_rng(seed)
    bs = np.array([solve(w) for w in boot_weights(len(clab), B, rng)]) if len(clab) >= 3 else np.zeros((0, k))
    out = {}
    for j, nm in enumerate(names):
        out[nm] = dict(coef=float(beta[1 + j]), ci=ci(bs[:, 1 + j]) if len(bs) else [np.nan, np.nan])
    return out


def re_pool(est: list[float], se: list[float]) -> dict:
    """DerSimonian-Laird random-effects pooling."""
    e = np.array(est, float); s = np.array(se, float)
    ok = np.isfinite(e) & np.isfinite(s) & (s > 0)
    e, s = e[ok], s[ok]
    if len(e) == 0:
        return dict(pooled=np.nan, ci=[np.nan, np.nan], k=0)
    w = 1 / s ** 2
    mu_f = (w * e).sum() / w.sum()
    Q = (w * (e - mu_f) ** 2).sum()
    tau2 = max(0.0, (Q - (len(e) - 1)) / (w.sum() - (w ** 2).sum() / w.sum())) if len(e) > 1 else 0.0
    ws = 1 / (s ** 2 + tau2)
    mu = (ws * e).sum() / ws.sum()
    se_mu = np.sqrt(1 / ws.sum())
    return dict(pooled=float(mu), ci=[float(mu - 1.96 * se_mu), float(mu + 1.96 * se_mu)], se=float(se_mu),
                tau2=float(tau2), Q=float(Q), k=int(len(e)), I2=float(max(0, (Q - (len(e) - 1)) / Q)) if Q > 0 else 0.0)


def verdict_from_ci(c, delta: float | None = None) -> str:
    lo, hi = c
    if lo is None or hi is None or not (np.isfinite(lo) and np.isfinite(hi)):
        return "n/a"
    if lo > 0:
        return "premium+"
    if hi < 0:
        return "premium-"
    if delta is not None and -delta < lo and hi < delta:
        return "equivalent"
    return "inconclusive"


# =============================================================================== generic ATT and fixed effects

def att(y: np.ndarray, treat: np.ndarray, ctrl: np.ndarray, stratum: np.ndarray, cluster: np.ndarray,
        B: int = 1000, seed: int = SEED, naive: bool = True, msg: np.ndarray | None = None) -> dict:
    """CEM ATT of `treat` rows vs `ctrl` rows within strata, cluster bootstrap (clusters = days or messages)."""
    y = np.asarray(y, float)
    treat = treat & np.isfinite(y); ctrl = ctrl & np.isfinite(y)
    if treat.sum() < 5 or ctrl.sum() < 5:
        return dict(att=np.nan, ci=[np.nan, np.nan], se=np.nan, n_t=int(treat.sum()), n_c=int(ctrl.sum()))
    St, Nt, Sc, Nc, clab = cem_sums(y, treat, ctrl, stratum, cluster)
    a, share, tmean = cem_att(St, Nt, Sc, Nc)
    rng = np.random.default_rng(seed)
    nclu = len(clab)
    bs = np.array([cem_att(St, Nt, Sc, Nc, w)[0] for w in boot_weights(nclu, B, rng)]) if nclu >= 3 else np.array([])
    fin = bs[np.isfinite(bs)] if len(bs) else bs
    out = dict(att=a, ci=ci(bs) if len(bs) else [np.nan, np.nan], se=float(np.std(fin)) if len(fin) > 5 else np.nan,
               p_le0=float(np.mean(fin <= 0)) if len(fin) > 5 else np.nan, matched_share=share, treated_mean=tmean,
               ctrl_matched_mean=(tmean - a) if np.isfinite(a) else np.nan, n_t=int(treat.sum()), n_c=int(ctrl.sum()),
               n_clusters=int(nclu))
    if msg is not None:
        out["n_t_msgs"] = int(len(np.unique(msg[treat])))
    if naive:
        sel = treat | ctrl
        nlab, nid = np.unique(cluster[sel], return_inverse=True)
        k = len(nlab)
        ts, cs = treat[sel], ctrl[sel]
        ys = y[sel]
        Tt = np.bincount(nid[ts], ys[ts], k); Tn = np.bincount(nid[ts], None, k)
        Ct = np.bincount(nid[cs], ys[cs], k); Cn = np.bincount(nid[cs], None, k)
        out["naive"] = float(Tt.sum() / Tn.sum() - Ct.sum() / Cn.sum())
        if k >= 3:
            nb = [(w @ Tt) / max(w @ Tn, 1e-9) - (w @ Ct) / max(w @ Cn, 1e-9) for w in boot_weights(k, B, np.random.default_rng(seed + 1))]
            out["naive_ci"] = ci(nb); out["naive_se"] = float(np.nanstd(nb))
    return out


def fe_residualize(y: np.ndarray, *groups, iters: int = 30) -> np.ndarray:
    """Two-way (or more) fixed-effect residuals by alternating projections (finite rows only); the grand mean is
    added back so levels stay interpretable."""
    y = np.asarray(y, float)
    ok = np.isfinite(y)
    r = y.copy()
    mu = r[ok].mean() if ok.any() else 0.0
    r[ok] -= mu
    gids = [np.unique(np.asarray(g)[ok], return_inverse=True)[1] for g in groups]
    for _ in range(iters):
        for gi in gids:
            s = np.bincount(gi, r[ok]); c = np.bincount(gi)
            r[ok] -= (s / np.maximum(c, 1))[gi]
    r[ok] += mu
    r[~ok] = np.nan
    return r


SINCE_EDGES = np.array([0, 1, 5, 15, 30])


def bc_residualize(d: pl.DataFrame, y: np.ndarray, fit_mask: np.ndarray, activity: bool = False) -> np.ndarray:
    """Bias-correction for CEM: y minus a linear prediction from continuous salience covariates plus day and
    recipient fixed effects, fitted on `fit_mask` rows only (clean agent rows), applied to all rows; the fitted
    rows' mean is added back. Covariates: log1p(age), novelty (+ missing flag), log1p(length), log(room size),
    named, idle; activity adds pre15, log1p(k_new) and since-active bins."""
    age = np.log1p(d["age_s"].to_numpy().astype(float))
    nov = d["nov"].cast(pl.Float64).fill_null(np.nan).to_numpy()
    nmiss = ~np.isfinite(nov)
    nov = np.where(nmiss, np.nanmean(nov) if np.isfinite(nov).any() else 0.0, nov)
    cols = [np.ones(d.height), age, nov, nmiss.astype(float), np.log1p(d["len"].to_numpy().astype(float)),
            np.log(np.maximum(room_n(d), 1)), d["named"].to_numpy().astype(float), d["idle"].to_numpy().astype(float)]
    if activity:
        cols += [d["pre15"].to_numpy().astype(float), np.log1p(d["k_new"].to_numpy().astype(float))]
        sb = bin_edges(d["since_act"].to_numpy(), SINCE_EDGES)
        cols += [(sb == v).astype(float) for v in np.unique(sb)[1:]]
    for g in (d["day_idx"].to_numpy(), d["recv"].to_numpy()):
        u = np.unique(g)
        cols += [(g == v).astype(float) for v in u[1:]]
    X = np.column_stack(cols)
    ok = fit_mask & np.isfinite(y)
    if ok.sum() < X.shape[1] + 10:
        return y.copy()
    beta = np.linalg.lstsq(X[ok], y[ok], rcond=None)[0]
    r = y - X @ beta + y[ok].mean()
    r[~np.isfinite(y)] = np.nan
    return r
