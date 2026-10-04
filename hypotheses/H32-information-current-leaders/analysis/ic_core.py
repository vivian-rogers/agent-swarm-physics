"""H32 core: exposure-conditioned content transfer (isotropic vector autoregression, cross-validated Gaussian TE).

For agent j's chat message m (time t, day d, room r), with z = whitened unit embedding minus the field subspace:
    z_m ~ a1 z_j,last + a2 z_j,ewma + a3 z_j,intent + b f_{d,r,-ij} + c r_{m,-i} + eH h_m + eA q_m  [+ u s^unseen_ij]  + k s_ij(m)
Scalar (isotropic) coefficients, least squares on the stacked coordinates, leave-one-day-out (or block) CV.
G_ij = 1 - SSE_full / SSE_base (held out). Null: circular shift of the sender timelines in active time.

Everything is computed from per-message Gram matrices (A_m = X_m X_m^T, b_m = X_m y_m, |y_m|^2) summed by fold,
so CV is exact and cheap. Used by synthetic.py, explore.py and confirm.py; no file I/O except Period.load.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from dataclasses import dataclass, field  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
HYP = HERE.parent
ROOT = HYP.parents[1]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import holdout_mask, load_holdout, load_whitener  # noqa: E402

SH = ROOT / "data/processed/shared"
DATA = ROOT / "data/processed/H32-information-current-leaders"
HUMAN, AUTO = 100, 101
SEED = 20261003

# frozen analysis parameters (card, Observables; 2026-10-03)
P = dict(dim=32, K_field=5, tau=900.0, win_mult=3.0, half_life_own=5.0, min_target=20, min_source=10, n_null=40,
         ridge=1e-3, min_gap_s=1.0, min_exposed=10, min_train_exposed=5, normalize_sums=True,
         null_kind="crossday", min_train_targets=0)
# Amendment A1 (2026-10-03, synthetic only, before any real-data run): min_exposed (a pair needs >= 10 of j's messages
# with a nonzero source term, in >= 2 folds) and ridge 1e-3 (relative to the mean diagonal of the design), after the
# two-room synthetic showed coefficients fitted on 1-2 exposed messages extrapolating to G of -15% to -150%.

# column names of the design
COLS = ["own_last", "own_ewma", "own_int", "field", "mean_field", "human", "auto"]


def unit(X, axis=-1, eps=1e-9):
    X = np.asarray(X, dtype=np.float64)
    return X / np.maximum(np.linalg.norm(X, axis=axis, keepdims=True), eps)


# ======================================================================================== data container
@dataclass
class Skeleton:
    """A period's message skeleton plus vectors. All times are float seconds (UTC epoch)."""
    goal_no: int
    days: list
    day_start: np.ndarray          # UTC epoch of each day's window start
    day_off: np.ndarray            # active-time offset of each day (s)
    day_len: np.ndarray            # window length (s)
    a_total: float
    # chat messages (sources and targets), time-sorted
    t: np.ndarray
    a: np.ndarray                  # active time
    day: np.ndarray
    room: np.ndarray
    spk: np.ndarray                # agent code, 100 human, 101 automated
    z: np.ndarray                  # (n, dim) field-removed vectors
    # intentions (own past only)
    it_t: np.ndarray
    it_spk: np.ndarray
    it_z: np.ndarray
    # rooms timeline per agent: dict agent -> (t_start, t_end, room)
    rooms_tl: dict
    agents: np.ndarray             # agents that speak in the period
    meta: dict = field(default_factory=dict)

    def room_of(self, agent: int, T: np.ndarray) -> np.ndarray:
        """Room of `agent` at times T (-1 if absent)."""
        ts, te, rm = self.rooms_tl.get(int(agent), (np.zeros(0), np.zeros(0), np.zeros(0, int)))
        out = np.full(len(T), -1, np.int16)
        if len(ts) == 0:
            return out
        idx = np.searchsorted(ts, T, side="right") - 1
        ok = idx >= 0
        ii = np.clip(idx, 0, None)
        ok &= T < te[ii]
        out[ok] = rm[ii[ok]]
        return out

    def subset_days(self, keep_days) -> "Skeleton":
        keep_days = set(int(d) for d in keep_days)
        m = np.array([d in keep_days for d in self.day]); mi = np.array([self.day_of(t) in keep_days for t in self.it_t]) \
            if len(self.it_t) else np.zeros(0, bool)
        return Skeleton(self.goal_no, self.days, self.day_start, self.day_off, self.day_len, self.a_total,
                        self.t[m], self.a[m], self.day[m], self.room[m], self.spk[m], self.z[m],
                        self.it_t[mi], self.it_spk[mi], self.it_z[mi], self.rooms_tl, self.agents, dict(self.meta))

    def day_of(self, t: float) -> int:
        return int(np.searchsorted(self.day_start, t, side="right") - 1)

    def with_z(self, z, it_z=None) -> "Skeleton":
        return Skeleton(self.goal_no, self.days, self.day_start, self.day_off, self.day_len, self.a_total, self.t, self.a,
                        self.day, self.room, self.spk, z, self.it_t, self.it_spk, self.it_z if it_z is None else it_z,
                        self.rooms_tl, self.agents, dict(self.meta))


def load_rooms_tl(agents) -> dict:
    rt = pl.read_parquet(SH / "rooms_timeline.parquet")
    out = {}
    far = 4.0e9
    for a in agents:
        r = rt.filter(pl.col("agent") == int(a)).sort("t_start")
        if r.height == 0:
            continue
        ts = np.array([x.timestamp() for x in r["t_start"].to_list()])
        te = np.array([far if x is None else x.timestamp() for x in r["t_end"].to_list()])
        out[int(a)] = (ts, te, r["room"].to_numpy().astype(np.int16))
    return out


def field_basis(goal_no: int, regime: str, u_agent: np.ndarray, day: np.ndarray, room: np.ndarray, K: int, dim: int,
                fields: dict | None = None) -> np.ndarray:
    """Orthonormal field subspace (dim x K'): goal text, kickoffs (whitened, unit), period mean, then leading PCs of
    the day x room mean vectors. K = 1 reproduces H01's single g-hat (goal + mean kickoff)."""
    vecs = []
    if fields is not None and ((f"g{goal_no}_raw" in fields and len(fields[f"g{goal_no}_raw"])) or "white" in fields):
        if "white" in fields:  # synthetic: field vectors already in the whitened space
            G = unit(fields["white"]); kind = fields["kind"]
        else:
            W = load_whitener(regime, dim)
            G = unit(W(fields[f"g{goal_no}_raw"]))
            kind = fields[f"g{goal_no}_kind"]
        if K == 1:
            g = G[kind == 0][0] if (kind == 0).any() else G[0]
            k = unit(G[kind == 1].mean(0)) if (kind == 1).any() else np.zeros(dim)
            return unit(g + k)[:, None]
        vecs += list(G)
    elif K == 1:
        return unit(u_agent.mean(0))[:, None]
    vecs.append(unit(u_agent.mean(0)))
    keys = day.astype(np.int64) * 100 + room.astype(np.int64)
    ks = np.unique(keys)
    M = np.stack([u_agent[keys == k].mean(0) for k in ks]) if len(ks) else np.zeros((0, dim))
    if len(M) >= 2:
        Mc = M - M.mean(0)
        _, _, Vt = np.linalg.svd(Mc, full_matrices=False)
        vecs += list(Vt[:K])
    Q = []
    for v in vecs:
        w = np.asarray(v, float).copy()
        for q in Q:
            w -= (w @ q) * q
        n = np.linalg.norm(w)
        if n > 1e-6:
            Q.append(w / n)
        if len(Q) >= K:
            break
    return np.stack(Q, 1) if Q else np.zeros((dim, 0))


def load_period(goal_no: int, dim: int = None, K_field: int = None, allow_holdout: bool = False,
                base: Path = DATA, text_fields: bool = True) -> Skeleton:
    dim = dim or P["dim"]; K_field = P["K_field"] if K_field is None else K_field
    periods = {p["goal_no"]: p for p in json.loads((base / "periods.json").read_text())}
    pi = periods[goal_no]
    if not allow_holdout:
        h = load_holdout()
        assert goal_no not in set(h["goal_periods_held_out"]), "held-out goal period"
        assert not any(holdout_mask(pi["days"], [goal_no] * len(pi["days"]))), "holdout day"
    msgs = pl.read_parquet(base / "messages.parquet").with_row_index("row").filter(pl.col("goal_no") == goal_no)
    V = np.load(base / "vec_w64.npy", mmap_mode="r")
    rows = msgs["row"].to_numpy()
    U = unit(np.asarray(V[rows, :dim], np.float32))
    kind = msgs["kind"].to_numpy(); spk = msgs["spk"].to_numpy().astype(np.int16)
    tt = np.array([x.timestamp() for x in msgs["t"].to_list()])
    day = msgs["day"].to_numpy().astype(np.int16)
    room = msgs["room"].fill_null(-1).to_numpy().astype(np.int16)
    fz = dict(np.load(base / "fields.npz")) if text_fields else None
    ag_chat = (kind == 0) & (spk < 100)
    Q = field_basis(goal_no, pi["regime_basis"], U[ag_chat], day[ag_chat], room[ag_chat], K_field, dim, fz)
    Z = U - (U @ Q) @ Q.T
    ws = np.array([dt.datetime.fromisoformat(x).timestamp() for x in pi["win_start"]])
    c = kind == 0
    agents = np.unique(spk[ag_chat])
    sk = Skeleton(goal_no, pi["days"], ws, np.array(pi["day_offset_s"], float), np.array(pi["day_len_s"], float),
                  float(pi["a_total_s"]), tt[c], msgs["a"].to_numpy()[c], day[c], room[c], spk[c], Z[c],
                  tt[~c], spk[~c], Z[~c], load_rooms_tl(agents), agents,
                  {"mode": pi["mode"], "regime": pi["regime_basis"], "K_field_eff": int(Q.shape[1]), "dim": dim,
                   "rooms_populated": pi["rooms_populated"]})
    return sk


# ======================================================================================== predictors
def exposure_matrix(sk: Skeleton, t_src: np.ndarray, room_src: np.ndarray, agents) -> np.ndarray:
    """R[x, a] = 1 if agent a was in message x's room at time t_src[x], 0 if present elsewhere, -1 if absent."""
    R = np.full((len(t_src), len(agents)), -1, np.int8)
    for k, a in enumerate(agents):
        ra = sk.room_of(a, t_src)
        R[:, k] = np.where(ra < 0, -1, (ra == room_src).astype(np.int8))
    return R


def decayed_sums(sk: Skeleton, tgt: np.ndarray, t_src: np.ndarray, day_src: np.ndarray, z_src: np.ndarray,
                 spk_src: np.ndarray, R: np.ndarray, senders: np.ndarray, tau: float, win: float, agent_index: dict):
    """For targets (indices into sk's chat arrays), decayed sums of seen / unseen source messages per sender.

    Returns S_seen, S_unseen of shape (n_tgt, n_senders, dim). Sources must be time-sorted (t_src)."""
    nt, ns, d = len(tgt), len(senders), z_src.shape[1]
    S1 = np.zeros((nt, ns, d)); S0 = np.zeros((nt, ns, d))
    W1 = np.zeros((nt, ns)); W0 = np.zeros((nt, ns))
    sidx = {int(s): k for k, s in enumerate(senders)}
    src_k = np.array([sidx.get(int(s), -1) for s in spk_src])
    tm = sk.t[tgt]; dm = sk.day[tgt]; jm = sk.spk[tgt]
    lo = np.searchsorted(t_src, tm - win, side="left")
    hi = np.searchsorted(t_src, tm - P["min_gap_s"], side="left")
    lens = hi - lo
    tot = int(lens.sum())
    if tot == 0:
        return S1, S0, W1, W0
    rep = np.repeat(np.arange(nt), lens)
    off = np.arange(tot) - np.repeat(np.cumsum(lens) - lens, lens)
    x = lo[rep] + off
    keep = (day_src[x] == dm[rep]) & (spk_src[x] != jm[rep]) & (src_k[x] >= 0)
    rep, x = rep[keep], x[keep]
    ja = np.array([agent_index[int(j)] for j in jm])
    ex = R[x, ja[rep]]
    w = np.exp(-(tm[rep] - t_src[x]) / tau)
    for val, S, W in ((1, S1, W1), (0, S0, W0)):
        m = ex == val
        np.add.at(S, (rep[m], src_k[x[m]]), w[m, None] * z_src[x[m]])
        np.add.at(W, (rep[m], src_k[x[m]]), w[m])
    return S1, S0, W1, W0


def own_past(sk: Skeleton, tgt: np.ndarray, half_life: float):
    """j's previous chat message, EWMA of its previous messages, latest intention before t (zeros if none)."""
    d = sk.z.shape[1]
    last = np.zeros((len(tgt), d)); ew = np.zeros((len(tgt), d)); intent = np.zeros((len(tgt), d))
    alpha = 1 - 2 ** (-1 / half_life)
    pos = {int(m): k for k, m in enumerate(tgt)}
    for a in np.unique(sk.spk[tgt]):
        idx = np.flatnonzero(sk.spk == a)
        e = np.zeros(d); prev = np.zeros(d)
        for m in idx:
            if m in pos:
                last[pos[m]] = prev; ew[pos[m]] = e
            prev = sk.z[m]; e = (1 - alpha) * e + alpha * sk.z[m]
        ii = np.flatnonzero(sk.it_spk == a)
        if len(ii):
            it_t = sk.it_t[ii]
            mine = [m for m in idx if m in pos]
            if mine:
                j = np.searchsorted(it_t, sk.t[mine], side="left") - 1
                ok = j >= 0
                for mm, jj, o in zip(mine, j, ok):
                    if o:
                        intent[pos[mm]] = sk.it_z[ii[jj]]
    return last, ew, intent


@dataclass
class Design:
    """Per-target arrays for one period (or one shifted replica of the sources)."""
    tgt: np.ndarray
    y: np.ndarray
    fold: np.ndarray
    jm: np.ndarray
    own: np.ndarray        # (nt, 3, d)
    fsum: np.ndarray       # day-room sums (nt, d) and counts, for leave-out fields
    fcnt: np.ndarray
    fsum_a: dict           # agent -> (nt, d) that agent's day-room sum at the target's (day, room)
    fcnt_a: dict
    senders: np.ndarray
    S1: np.ndarray         # seen   (nt, ns, d)  raw decayed sums
    S0: np.ndarray         # unseen (nt, ns, d)
    W1: np.ndarray = None  # seen weight sums (nt, ns)
    W0: np.ndarray = None


def build_design(sk: Skeleton, fold_kind: str = "day", block_s: float = 1800.0, min_target: int = None,
                 tau: float = None, targets_mask: np.ndarray | None = None) -> Design:
    min_target = P["min_target"] if min_target is None else min_target
    tau = P["tau"] if tau is None else tau
    is_ag = sk.spk < 100
    cnt = {int(a): int((sk.spk == a).sum()) for a in sk.agents}
    tmask = is_ag & np.array([cnt.get(int(s), 0) >= min_target for s in sk.spk])
    if targets_mask is not None:
        tmask &= targets_mask
    tgt = np.flatnonzero(tmask)
    senders = np.array(sorted(set(int(a) for a in sk.agents)) + [HUMAN, AUTO])
    agents = np.array(sorted(set(int(a) for a in sk.agents)))
    aidx = {int(a): k for k, a in enumerate(agents)}
    R = exposure_matrix(sk, sk.t, sk.room, agents)
    S1, S0, W1, W0 = decayed_sums(sk, tgt, sk.t, sk.day, sk.z, sk.spk, R, senders, tau, P["win_mult"] * tau, aidx)
    last, ew, intent = own_past(sk, tgt, P["half_life_own"])
    own = np.stack([last, ew, intent], 1)
    # day x room sums over agent chat
    key = sk.day.astype(np.int64) * 100 + sk.room.astype(np.int64)
    d = sk.z.shape[1]
    ksum, kcnt = {}, {}
    ka = {}
    for i in np.flatnonzero(is_ag):
        k = key[i]
        ksum[k] = ksum.get(k, 0) + sk.z[i]; kcnt[k] = kcnt.get(k, 0) + 1
        ka[(k, int(sk.spk[i]))] = ka.get((k, int(sk.spk[i])), 0) + sk.z[i]
    kt = key[tgt]
    fsum = np.stack([ksum.get(k, np.zeros(d)) for k in kt]); fcnt = np.array([kcnt.get(k, 0) for k in kt], float)
    fsum_a, fcnt_a = {}, {}
    acnt = {}
    for i in np.flatnonzero(is_ag):
        acnt[(key[i], int(sk.spk[i]))] = acnt.get((key[i], int(sk.spk[i])), 0) + 1
    for a in agents:
        fsum_a[int(a)] = np.stack([np.asarray(ka.get((k, int(a)), np.zeros(d))) for k in kt])
        fcnt_a[int(a)] = np.array([acnt.get((k, int(a)), 0) for k in kt], float)
    if fold_kind == "day":
        fold = sk.day[tgt].astype(np.int64)
    else:  # 30-min blocks of active time
        fold = (sk.a[tgt] // block_s).astype(np.int64)
    return Design(tgt, sk.z[tgt], fold, sk.spk[tgt].astype(np.int64), own, fsum, fcnt, fsum_a, fcnt_a, senders, S1, S0, W1, W0)


def shifted_sources(sk: Skeleton, D: Design, delta: float, tau: float = None, kind: str = None):
    """Seen/unseen decayed sums with every sender's timeline circularly shifted.
    kind 'crossday' (N1): shift by `delta` active seconds over the whole period (wraps around).
    kind 'withinday' (N1w, A1c): within each day, shift by u * (L_d - 6 tau) + 3 tau with u = delta in [0, 1), wrapping
    inside the day; days shorter than 7 tau keep no shifted messages."""
    tau = P["tau"] if tau is None else tau
    kind = P.get("null_kind", "crossday") if kind is None else kind
    a = sk.a.copy()
    # clip each message into its own day's window before shifting (messages slightly outside the agent window)
    a = np.clip(a, sk.day_off[sk.day], sk.day_off[sk.day] + sk.day_len[sk.day] - 1e-3)
    keep = np.ones(len(a), bool)
    if kind == "crossday":
        a2 = (a + delta) % sk.a_total
        d2 = np.clip(np.searchsorted(sk.day_off, a2, side="right") - 1, 0, len(sk.day_off) - 1)
    else:
        L = sk.day_len[sk.day]; off = sk.day_off[sk.day]
        sh = (delta % 1.0) * np.maximum(L - 6 * tau, 0) + 3 * tau
        a2 = off + ((a - off + sh) % np.maximum(L, 1.0))
        d2 = sk.day.astype(np.int64)
        keep = L >= 7 * tau
    t2 = sk.day_start[d2] + (a2 - sk.day_off[d2])
    t2 = np.where(keep, t2, -1e12)  # dropped messages fall outside every window
    o = np.argsort(t2, kind="stable")
    agents = np.array(sorted(set(int(x) for x in sk.agents)))
    aidx = {int(x): k for k, x in enumerate(agents)}
    R = exposure_matrix(sk, t2[o], sk.room[o], agents)
    S1, S0, W1, W0 = decayed_sums(sk, D.tgt, t2[o], d2[o].astype(np.int16), sk.z[o], sk.spk[o], R, D.senders, tau,
                                  P["win_mult"] * tau, aidx)
    return (S1, W1), (S0, W0)


# ======================================================================================== fitting
def _gram(X: np.ndarray, y: np.ndarray):
    """X (n, C, d), y (n, d) -> A (n, C, C), b (n, C), yy (n,)"""
    return np.einsum("ncd,ned->nce", X, X), np.einsum("ncd,nd->nc", X, y), np.einsum("nd,nd->n", y, y)


def cv_sse(A, b, yy, fold, cols, ridge=None, src_col=None, expo=None):
    """Held-out SSE per fold for the column subset `cols` (leave-one-fold-out). If `src_col` is given, folds whose
    training set has fewer than P['min_train_exposed'] messages with a nonzero source term drop that column
    (coefficient 0: no estimate, no effect) -- Amendment A1."""
    ridge = P["ridge"] if ridge is None else ridge
    cols = list(cols)
    fs = np.unique(fold)
    out = np.zeros(len(fs))
    Afull = A[:, cols][:, :, cols]; bfull = b[:, cols]
    Af = np.stack([Afull[fold == f].sum(0) for f in fs]); bf = np.stack([bfull[fold == f].sum(0) for f in fs])
    yf = np.array([yy[fold == f].sum() for f in fs])
    At, bt = Af.sum(0), bf.sum(0)
    ef = np.array([expo[fold == f].sum() for f in fs]) if expo is not None else None
    for k in range(len(fs)):
        Ak = At - Af[k]; bk = bt - bf[k]
        use = np.arange(len(cols))
        if src_col is not None and ef is not None and (ef.sum() - ef[k]) < P["min_train_exposed"]:
            use = np.array([c for c in range(len(cols)) if cols[c] != src_col])
        Au = Ak[np.ix_(use, use)]; bu = bk[use]
        lam = ridge * max(np.trace(Au) / len(use), 1e-12)
        beta = np.linalg.solve(Au + lam * np.eye(len(use)), bu)
        Afk = Af[k][np.ix_(use, use)]; bfk = bf[k][use]
        out[k] = yf[k] - 2 * beta @ bfk + beta @ Afk @ beta
    return fs, out


def _norm(S, W):
    """Saturating normalization of a decayed sum: sum w z / (1 + sum w) (A1b); identity if P['normalize_sums'] is off."""
    if not P.get("normalize_sums", True) or W is None:
        return S
    return S / (1.0 + W)[..., None]


def pair_columns(D: Design, sel: np.ndarray, i: int, j: int, S1src=None, S0src=None, use_unseen=False, human_source=False):
    """Design tensor for target agent j's messages `sel` and source i. S1src / S0src are (S, W) tuples of decayed sums
    and weights (default: the observed ones). Returns X (n, C, d) and the index of the source column."""
    S1src = (D.S1, D.W1) if S1src is None else S1src
    S0src = (D.S0, D.W0) if S0src is None else S0src
    k_of = {int(s): k for k, s in enumerate(D.senders)}
    own = D.own[sel]
    if i in D.fsum_a:
        num = D.fsum[sel] - D.fsum_a[j][sel] - D.fsum_a[i][sel]
        den = D.fcnt[sel] - D.fcnt_a[j][sel] - D.fcnt_a[i][sel]
    else:
        num = D.fsum[sel] - D.fsum_a[j][sel]; den = D.fcnt[sel] - D.fcnt_a[j][sel]
    f = num / np.maximum(den, 1)[:, None]
    ag = [k for s, k in k_of.items() if s < 100 and s != j]
    S1o, W1o = D.S1[sel], D.W1[sel]
    hk, ak = k_of[HUMAN], k_of[AUTO]
    if human_source:
        r = _norm(S1o[:, ag].sum(1), W1o[:, ag].sum(1))
        cols = [own[:, 0], own[:, 1], own[:, 2], f, r, _norm(S1o[:, ak], W1o[:, ak])]
        src = _norm(S1src[0][sel][:, hk], S1src[1][sel][:, hk])
    else:
        ki = k_of[i]
        ag_i = [k for k in ag if k != ki]
        r = _norm(S1o[:, ag_i].sum(1), W1o[:, ag_i].sum(1))
        cols = [own[:, 0], own[:, 1], own[:, 2], f, r, _norm(S1o[:, hk], W1o[:, hk]), _norm(S1o[:, ak], W1o[:, ak])]
        src = _norm(S1src[0][sel][:, ki], S1src[1][sel][:, ki])
        if use_unseen:
            cols.append(_norm(S0src[0][sel][:, ki], S0src[1][sel][:, ki]))
    cols.append(src)
    return np.stack(cols, 1), len(cols) - 1


def pair_gain(D: Design, i: int, j: int, S1src=None, S0src=None, mode="seen", human_source=False):
    """Cross-validated gain of the source column for pair i -> j. mode: 'seen' (primary), 'seen_beyond_unseen',
    'unseen' (unseen source instead of seen). Returns (G, per-fold SSE_base, SSE_full, folds, n_targets)."""
    sel = np.flatnonzero(D.jm == j)
    mt = P.get("min_train_targets", 0)
    if mt:  # A2 (POST HOC, 2026-10-03): drop held-out folds whose training set has < mt of j's messages
        f_ = D.fold[sel]
        fs_, cnt_ = np.unique(f_, return_counts=True)
        okf = fs_[(len(sel) - cnt_) >= mt]
        sel = sel[np.isin(f_, okf)]
    if mode == "unseen":
        X, s = pair_columns(D, sel, i, j, S1src=(S0src if S0src is not None else (D.S0, D.W0)), S0src=None,
                            human_source=human_source)
    else:
        X, s = pair_columns(D, sel, i, j, S1src, S0src, use_unseen=(mode == "seen_beyond_unseen"), human_source=human_source)
    expo = np.any(X[:, s] != 0, axis=1)
    fold = D.fold[sel]
    if expo.sum() < P["min_exposed"] or len(np.unique(fold[expo])) < 2 or len(np.unique(fold)) < 2:
        return np.nan, None, None, None, len(sel)
    A, b, yy = _gram(X, D.y[sel])
    C = X.shape[1]
    base = [c for c in range(C) if c != s]
    keepb = [c for c in base if np.any(X[:, c])]
    fs, sb = cv_sse(A, b, yy, fold, keepb)
    _, sf = cv_sse(A, b, yy, fold, keepb + [s], src_col=s, expo=expo)
    return 1 - sf.sum() / sb.sum(), sb, sf, fs, len(sel)


def eligible(D: Design, sk: Skeleton, min_source=None):
    min_source = P["min_source"] if min_source is None else min_source
    targets = sorted(set(int(j) for j in D.jm))
    cnt = {int(a): int((sk.spk == a).sum()) for a in sk.agents}
    sources = [int(a) for a in sk.agents if cnt[int(a)] >= min_source]
    return targets, sources


def gain_matrix(D: Design, sk: Skeleton, S1src=None, S0src=None, mode="seen", with_folds=False):
    targets, sources = eligible(D, sk)
    nodes = sorted(set(targets) | set(sources))
    ix = {a: k for k, a in enumerate(nodes)}
    G = np.full((len(nodes), len(nodes)), np.nan)
    folds = {}
    for j in targets:
        for i in sources:
            if i == j:
                continue
            g, sb, sf, fs, _ = pair_gain(D, i, j, S1src, S0src, mode)
            G[ix[i], ix[j]] = g
            if with_folds and sb is not None:
                folds[(i, j)] = (fs, sb, sf)
    return nodes, G, folds


def human_gain(D: Design, sk: Skeleton, S1src=None):
    targets, _ = eligible(D, sk)
    out = {}
    for j in targets:
        g, *_ = pair_gain(D, HUMAN, j, S1src, None, "seen", human_source=True)
        out[j] = g
    return out


# ======================================================================================== agent-level statistics
def currents(dG: np.ndarray):
    """Out_i (row means over targets), In_j (column means over sources), Net = Out - In (nan-aware)."""
    with np.errstate(invalid="ignore"):
        out = np.nanmean(dG, 1); inn = np.nanmean(dG, 0)
    return out, inn, out - inn


def centralization(out: np.ndarray, var_noise: np.ndarray):
    """Phi = CV^2_true / (N-1); CV^2_true = (Var(Out) - mean noise var) / mean(Out)^2. Also Gini(Out+), top share."""
    o = out[np.isfinite(out)]; v = var_noise[np.isfinite(out)]
    N = len(o)
    mu = o.mean()
    var_true = o.var(ddof=1) - np.nanmean(v)
    phi = (var_true / mu ** 2) / (N - 1) if mu > 0 else np.nan
    op = np.clip(o, 0, None)
    if op.sum() > 0:
        s = np.sort(op); n = len(s)
        gini = (2 * np.sum((np.arange(1, n + 1)) * s) / (n * s.sum())) - (n + 1) / n
        top = s[-1] / s.sum()
    else:
        gini = top = np.nan
    Q = np.sum((o - np.average(o, weights=1 / np.maximum(v, 1e-12))) ** 2 / np.maximum(v, 1e-12))
    from scipy.stats import chi2
    pQ = float(chi2.sf(Q, N - 1))
    return {"phi": float(phi), "gini": float(gini), "top_share": float(top), "Q": float(Q), "pQ": pQ,
            "I2": float(max(0.0, (Q - (N - 1)) / Q)) if Q > 0 else 0.0, "mean_out": float(mu), "var_out": float(o.var(ddof=1)),
            "noise_var": float(np.nanmean(v))}


def trimmed_mean(x, frac=0.1) -> float:
    """10% trimmed mean of the finite entries (robust total transfer; added post hoc, A2)."""
    x = np.sort(np.asarray(x, float)[np.isfinite(x)])
    k = int(len(x) * frac)
    return float(x[k:len(x) - k].mean()) if len(x) > 2 * k else float("nan")


def standout(out: np.ndarray) -> float:
    """How far the top agent's outflow stands above the others: (max - mean of the rest) / sd of the rest."""
    o = out[np.isfinite(out)]
    if len(o) < 3:
        return np.nan
    k = int(np.argmax(o)); rest = np.delete(o, k)
    return float((o[k] - rest.mean()) / max(rest.std(ddof=1), 1e-12))


def jackknife_out(nodes, folds, med_null, all_days):
    """Delete-one-day jackknife variance of Out_i from the per-fold SSEs (null median held fixed)."""
    ix = {a: k for k, a in enumerate(nodes)}
    n = len(nodes)
    reps = []
    for d in all_days:
        dG = np.full((n, n), np.nan)
        for (i, j), (fs, sb, sf) in folds.items():
            m = fs != d
            if m.sum() < 1 or sb[m].sum() <= 0:
                continue
            dG[ix[i], ix[j]] = (1 - sf[m].sum() / sb[m].sum()) - med_null[ix[i], ix[j]]
        reps.append(currents(dG)[0])
    R = np.array(reps)
    D = len(all_days)
    with np.errstate(invalid="ignore"):
        mean = np.nanmean(R, 0)
        var = (D - 1) / D * np.nansum((R - mean) ** 2, 0)
    return var


def null_offsets(sk: Skeleton, n: int, rng, kind: str = None) -> np.ndarray:
    kind = P.get("null_kind", "crossday") if kind is None else kind
    if kind == "withinday":
        return (np.arange(n) + rng.uniform(0, 1, n)) / n   # stratified fractions in [0, 1)
    mlen = float(np.mean(sk.day_len))
    lo, hi = 0.5 * mlen, sk.a_total - 0.5 * mlen
    if hi <= lo:
        lo, hi = 0.25 * sk.a_total, 0.75 * sk.a_total
    return rng.uniform(lo, hi, n)


def withinday_check(sk: Skeleton, D: Design, G: np.ndarray, n: int, rng) -> dict:
    """N1w (A1c): the same statistics against within-day circular shifts (offset >= 3 tau): T, Out z, standout."""
    offs = null_offsets(sk, n, rng, kind="withinday")
    Gw = np.array([gain_matrix(D, sk, *shifted_sources(sk, D, d, kind="withinday"))[1] for d in offs])
    with np.errstate(invalid="ignore"):
        med = np.nanmedian(Gw, 0)
        dG = G - med
        out = currents(dG)[0]
        Tn, On = [], []
        for k in range(n):
            dk = Gw[k] - np.nanmedian(np.delete(Gw, k, 0), 0)
            Tn.append(np.nanmean(dk)); On.append(currents(dk)[0])
        Tn, On = np.array(Tn), np.array(On)
        T = float(np.nanmean(dG))
        z = (out - np.nanmean(On, 0)) / np.nanstd(On, 0)
    Hs, Hn = standout(out), np.array([standout(o) for o in On])
    return {"T": T, "p_T": float((1 + np.sum(Tn >= T)) / (1 + n)), "out": out, "z_out": z,
            "standout": float(Hs), "p_standout": float((1 + np.sum(Hn >= Hs)) / (1 + n)),
            "p_max": float((1 + np.sum(np.nanmax(On, 1) >= np.nanmax(out))) / (1 + n))}


def run_unit(sk: Skeleton, n_null: int = None, seed: int = SEED, modes=("seen",), do_human=True, verbose=False,
             n_withinday: int = 0):
    """Full pipeline for one unit: G matrix, null replicas, currents, centralization. Returns a result dict."""
    n_null = P["n_null"] if n_null is None else n_null
    rng = np.random.default_rng(seed)
    D = build_design(sk)
    nodes, G, folds = gain_matrix(D, sk, with_folds=True)
    res = {"nodes": nodes, "G": G}
    if n_withinday:
        res["withinday"] = withinday_check(sk, D, G, n_withinday, np.random.default_rng(seed + 99))
    offs = null_offsets(sk, n_null, rng, kind="crossday")
    Gn = np.zeros((n_null,) + G.shape)
    Hn = []
    extra = {m: [] for m in modes if m != "seen"}
    extra_obs = {}
    for m in modes:
        if m != "seen":
            extra_obs[m] = gain_matrix(D, sk, mode=m)[1]
    hobs = human_gain(D, sk) if do_human else {}
    for k, dlt in enumerate(offs):
        S1s, S0s = shifted_sources(sk, D, dlt, kind="crossday")
        Gn[k] = gain_matrix(D, sk, S1s, S0s)[1]
        for m in extra:
            extra[m].append(gain_matrix(D, sk, S1s, S0s, mode=m)[1])
        if do_human:
            Hn.append(human_gain(D, sk, S1s))
        if verbose and k % 10 == 0:
            print("  null", k, flush=True)
    with np.errstate(invalid="ignore"):
        med = np.nanmedian(Gn, 0)
    dG = G - med
    out, inn, net = currents(dG)
    # null replicas of the agent statistics (each centered by the median of the other replicas)
    Tn, On, Nn, In_, Ttn = [], [], [], [], []
    for k in range(n_null):
        others = np.delete(Gn, k, 0)
        with np.errstate(invalid="ignore"):
            dk = Gn[k] - np.nanmedian(others, 0)
        o, i_, ne = currents(dk)
        On.append(o); Nn.append(ne); In_.append(i_)
        Tn.append(np.nanmean(dk)); Ttn.append(trimmed_mean(dk))
    On, Nn, Tn = np.array(On), np.array(Nn), np.array(Tn)
    T = float(np.nanmean(dG))
    days = sorted(set(int(x) for x in D.fold))
    var_j = jackknife_out(nodes, folds, med, days)
    with np.errstate(invalid="ignore", divide="ignore"):
        z_out = (out - np.nanmean(On, 0)) / np.nanstd(On, 0)
        z_net = (net - np.nanmean(Nn, 0)) / np.nanstd(Nn, 0)
    Tt, Ttn = trimmed_mean(dG), np.array(Ttn)
    res["T_trim"] = Tt; res["p_T_trim"] = float((1 + np.sum(Ttn >= Tt)) / (1 + n_null))
    var_n = np.nanvar(On, 0, ddof=1)
    Hs, Hn_ = standout(out), np.array([standout(o) for o in On])
    Mx, Mn = np.nanmax(out), np.nanmax(On, 1)
    res.update({"dG": dG, "G_null_median": med, "out": out, "in": inn, "net": net, "z_out": z_out, "z_net": z_net,
                "var_jack": var_j, "var_null": var_n, "T": T, "T_null": Tn, "p_T": float((1 + np.sum(Tn >= T)) / (1 + n_null)),
                "cent": centralization(out, var_j), "cent_nullvar": centralization(out, var_n),
                "standout": float(Hs), "p_standout": float((1 + np.sum(Hn_ >= Hs)) / (1 + n_null)),
                "p_max": float((1 + np.sum(Mn >= Mx)) / (1 + n_null)),
                "n_targets": {int(j): int((D.jm == j).sum()) for j in set(D.jm)}})
    if do_human:
        hj = np.array([hobs[j] for j in sorted(hobs)])
        hn = np.array([[h[j] for j in sorted(hobs)] for h in Hn])
        with np.errstate(invalid="ignore"):
            hmed = np.nanmedian(hn, 0)
            out_h = float(np.nanmean(hj - hmed))
            outh_null = np.array([np.nanmean(hn[k] - np.nanmedian(np.delete(hn, k, 0), 0)) for k in range(n_null)])
        res["human"] = {"out": out_h, "z": float((out_h - np.nanmean(outh_null)) / np.nanstd(outh_null)) if np.nanstd(outh_null) > 0 else np.nan,
                        "p": float((1 + np.sum(outh_null >= out_h)) / (1 + n_null)),
                        "per_target": {int(j): float(v - m) for j, v, m in zip(sorted(hobs), hj, hmed)}}
    for m in extra:
        Ge = extra_obs[m]; Gen = np.array(extra[m])
        with np.errstate(invalid="ignore"):
            mede = np.nanmedian(Gen, 0)
        res[f"dG_{m}"] = Ge - mede
        res[f"T_{m}"] = float(np.nanmean(Ge - mede))
        Tm = []
        for k in range(n_null):
            with np.errstate(invalid="ignore"):
                Tm.append(np.nanmean(Gen[k] - np.nanmedian(np.delete(Gen, k, 0), 0)))
        res[f"T_{m}_null"] = np.array(Tm)
        res[f"p_T_{m}"] = float((1 + np.sum(np.array(Tm) >= res[f"T_{m}"])) / (1 + n_null))
    return res


def pooled_sender_gain(sk: Skeleton, targets_mask: np.ndarray, sources, n_null: int = 20, seed: int = SEED,
                       block_s: float = 1800.0):
    """O9: for each sender i, CV gain (30-min blocks) of adding s_i to every other agent's model in the segment, with
    all coefficients shared across receivers; null = circular shift of sender timelines over the whole period."""
    D = build_design(sk, fold_kind="block", block_s=block_s, min_target=1, targets_mask=targets_mask)
    rng = np.random.default_rng(seed)
    offs = null_offsets(sk, n_null, rng)

    def gains(S1src):
        out = {}
        for i in sources:
            Ab = []; bb = []; yb = []; fb = []; Xs = None
            for j in sorted(set(int(x) for x in D.jm)):
                if j == i:
                    continue
                sel = np.flatnonzero(D.jm == j)
                X, s = pair_columns(D, sel, i, j, S1src, None, human_source=(i == HUMAN))
                A, b, yy = _gram(X, D.y[sel])
                Ab.append(A); bb.append(b); yb.append(yy); fb.append(D.fold[sel])
            if not Ab:
                out[i] = np.nan; continue
            A = np.concatenate(Ab); b = np.concatenate(bb); yy = np.concatenate(yb); fold = np.concatenate(fb)
            C = A.shape[1]; s = C - 1
            ex = A[:, s, s] > 0
            if ex.sum() < P["min_exposed"] or len(np.unique(fold[ex])) < 2 or len(np.unique(fold)) < 2:
                out[i] = np.nan; continue
            base = [c for c in range(C - 1) if np.any(A[:, c, c] > 0)]
            _, sb = cv_sse(A, b, yy, fold, base); _, sf = cv_sse(A, b, yy, fold, base + [s], src_col=s, expo=ex)
            out[i] = 1 - sf.sum() / sb.sum()
        return out
    obs = gains((D.S1, D.W1))
    nulls = [gains(shifted_sources(sk, D, dlt)[0]) for dlt in offs]
    res = {}
    for i in sources:
        nv = np.array([x[i] for x in nulls], float)
        with np.errstate(invalid="ignore"):
            res[i] = {"G": float(obs[i]), "dG": float(obs[i] - np.nanmedian(nv)),
                      "z": float((obs[i] - np.nanmean(nv)) / np.nanstd(nv)) if np.nanstd(nv) > 0 else np.nan,
                      "p": float((1 + np.sum(nv >= obs[i])) / (1 + len(nv)))}
    return res
