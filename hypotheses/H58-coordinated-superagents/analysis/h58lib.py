"""H58 estimators: coordinated superagents with an allocation ("which artifact") unit state.

Card: hypotheses/H58-coordinated-superagents/README.md, "Formal setup" F1-F10. Shared by analysis/synthetic.py (axis F)
and analysis/run.py (real data). Thread use is capped at 2 before numpy is imported.

Data model (one unit of analysis), class `Unit`:
  agents[nA]            committing agents (codes); repos[nR] local repo ids
  day_of_bin[nB]        day index of each active bin; first[nB] True at a day's first bin
  S[nA, nB] int         allocation state: local repo index of the agent's dominant commit repo in the bin, -1 none
  N[nA, nB] int         commits in the bin
  Wn[nA, nR]            period commits per agent and repo
  yh[nB] bool           exogenous input (nudge, human message, kickoff) in the bin
  C[nA, nB] int         content cluster (-1 none), optional
All information quantities are held-out (leave-one-day-out) log-loss differences in bits (card F5).
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
           "NUMEXPR_NUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ[_v] = "2"

import math  # noqa: E402
import sys  # noqa: E402
from dataclasses import dataclass, field  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
# H01 round-2 estimators, imported read-only (greedy modularity, Period container, binary individuality, Stouffer).
sys.path.insert(0, str(ROOT / "hypotheses/H01-emergent-superagents-exist/analysis"))
import r2lib  # noqa: E402

ALPHA = 0.5
SHARE_RULE = 0.5
MIN_PROJ = 3
LOG2 = math.log(2.0)


# ============================================================================ container
@dataclass
class Unit:
    name: str
    regime: str
    agents: list
    repos: list
    day_of_bin: np.ndarray
    S: np.ndarray
    N: np.ndarray
    yh: np.ndarray
    C: np.ndarray | None = None
    rooms: np.ndarray | None = None      # [nA, nB] room code at bin midpoint (-1 unknown)
    extra: dict = field(default_factory=dict)

    def __post_init__(self):
        self.nA, self.nB = self.S.shape
        nR = len(self.repos)
        self.Wn = np.zeros((self.nA, nR), np.int64)
        for a in range(self.nA):
            m = self.S[a] >= 0
            # period commits per repo: use N as weights on the dominant repo (exact counts are passed in extra if known)
            np.add.at(self.Wn[a], self.S[a][m], self.N[a][m])
        if "Wn" in self.extra:
            self.Wn = self.extra["Wn"]
        self.tot_k = self.Wn.sum(0)
        self.act_a = self.Wn.sum(1)
        self.first = np.ones(self.nB, bool)
        self.first[1:] = self.day_of_bin[1:] != self.day_of_bin[:-1]
        self.days = np.unique(self.day_of_bin)
        self.nD = len(self.days)
        self.day_slices = []
        for d in self.days:
            idx = np.flatnonzero(self.day_of_bin == d)
            self.day_slices.append((int(idx[0]), int(idx[-1]) + 1))

    def shared_artifacts(self, members) -> np.ndarray:
        m = np.asarray(members, int)
        own = self.Wn[m].sum(0)
        return np.flatnonzero((self.tot_k >= MIN_PROJ) & (own >= SHARE_RULE * self.tot_k) & (own > 0))


# ============================================================================ helpers
def _ffill_rows(X: np.ndarray) -> np.ndarray:
    """Forward fill -1 entries along axis 1 (carries the last state across bins and nights)."""
    n, B = X.shape
    idx = np.where(X >= 0, np.arange(B)[None, :], 0)
    np.maximum.accumulate(idx, axis=1, out=idx)
    out = X[np.arange(n)[:, None], idx]
    # positions before the first valid entry stay -1
    seen = np.maximum.accumulate(X >= 0, axis=1)
    out[~seen] = -1
    return out


def _lastday_rows(X: np.ndarray, day: np.ndarray) -> np.ndarray:
    """Day index of the last valid (>= 0) entry at or before each position (-1 if none)."""
    n, B = X.shape
    idx = np.where(X >= 0, np.arange(B)[None, :], -1)
    np.maximum.accumulate(idx, axis=1, out=idx)
    out = np.where(idx >= 0, day[np.maximum(idx, 0)], -1)
    return out


def map_states(U: Unit, members, R, S=None) -> np.ndarray:
    """Member states in the unit alphabet: 0..|R|-1 for R_G artifacts, |R| = outside R_G, -1 none."""
    S = U.S if S is None else S
    m = np.asarray(members, int)
    lut = np.full(len(U.repos) + 1, len(R), np.int64)
    lut[np.asarray(R, int)] = np.arange(len(R))
    X = S[m]
    out = np.where(X >= 0, lut[np.where(X >= 0, X, len(U.repos))], -1)
    return out


def _counts_per_bin(X: np.ndarray, nR: int) -> np.ndarray:
    """[n, B, nR] one-hot commit-state counts on R_G artifacts (values >= nR = outside are ignored)."""
    n, B = X.shape
    out = np.zeros((n, B, max(nR, 1)))
    valid = (X >= 0) & (X < nR)
    jj, bb = np.nonzero(valid)
    out[jj, bb, X[valid]] = 1
    return out[:, :, :nR] if nR > 0 else out[:, :, :0]


def _argmax_or_none(c: np.ndarray) -> np.ndarray:
    if c.shape[-1] == 0:
        return np.full(c.shape[:-1], -1, np.int64)
    return np.where(c.max(-1) > 0, c.argmax(-1), -1)


def others_alloc(X: np.ndarray, nR: int, Xo: np.ndarray | None = None, window=(0, 1), Xo_per=None) -> np.ndarray:
    """o_j(b): the R_G artifact the *others* are on, for the transition b -> b+1 (card F4 + amendment A1).
    Others = the other members (Xo None) or an explicit disjoint set Xo. window=(0, 1): others' states in bins b and
    b+1 (co-allocation, primary); (0,): bin b only (strictly lagged transfer entropy, secondary)."""
    n, B = X.shape
    if Xo_per is not None:                                # per-member explicit others (size-matched designs)
        tot = np.stack([_counts_per_bin(Xj, nR).sum(0) for Xj in Xo_per])
    elif Xo is None:
        cm = _counts_per_bin(X, nR)
        tot = cm.sum(0)[None] - cm                        # others = members except j
    else:
        co = _counts_per_bin(Xo, nR).sum(0)
        tot = np.broadcast_to(co, (n,) + co.shape)
    acc = np.zeros_like(tot)
    for w in window:
        if w == 0:
            acc = acc + tot
        else:
            sh = np.zeros_like(tot)
            sh[:, :-w] = tot[:, w:]
            acc = acc + sh
    return _argmax_or_none(acc)


# ============================================================================ F5a coordination gain
def _transitions(U: Unit, members, R=None, S=None, night=False, others=None, window=(0, 1), others_per=None):
    """Member working transitions for the relational mixture model. Returns dict of arrays or None."""
    R = U.shared_artifacts(members) if R is None else np.asarray(R, int)
    nR = len(R)
    X = map_states(U, members, R, S)                      # [n, B]
    Xo = None if others is None else map_states(U, others, R, S)
    Xo_per = None if others_per is None else [map_states(U, op, R, S) for op in others_per]
    n, B = X.shape
    L = _ffill_rows(X)                                    # last own state up to and including b
    LD = _lastday_rows(X, U.day_of_bin)
    if not night:
        O = others_alloc(X, nR, Xo, window, Xo_per)
        b0 = np.arange(B - 1)
        b0 = b0[U.day_of_bin[b0] == U.day_of_bin[b0 + 1]]
        tgt = X[:, b0 + 1]
        ell = L[:, b0]
        ld = LD[:, b0]
        o = O[:, b0]
        dd = np.broadcast_to(U.day_of_bin[b0 + 1], tgt.shape)
        jj = np.broadcast_to(np.arange(n)[:, None], tgt.shape)
        ok = tgt >= 0
        k, ell, o, dd, ld, jm = tgt[ok], ell[ok], o[ok], dd[ok], ld[ok], jj[ok]
        today = ld == dd
    else:
        # first working bin of each day d > 0; o = others' dominant R_G artifact over the previous day's last 4 bins
        rows = []
        Xs = X if Xo is None else Xo
        for (di, (lo, hi)) in enumerate(U.day_slices):
            if di == 0:
                continue
            plo, phi = U.day_slices[di - 1]
            tail = slice(max(plo, phi - 4), phi)
            for j in range(n):
                w = np.flatnonzero(X[j, lo:hi] >= 0)
                if len(w) == 0:
                    continue
                b = lo + w[0]
                ell_j = L[j, b - 1] if b > 0 else -1
                oth = np.delete(Xs[:, tail], j, 0) if Xo is None else Xs[:, tail]
                v = oth[(oth >= 0) & (oth < nR)]
                o_j = np.bincount(v, minlength=nR).argmax() if len(v) else -1
                rows.append((X[j, b], ell_j, o_j, U.days[di], j))
        if not rows:
            return None
        a = np.asarray(rows)
        k, ell, o, dd, jm = a[:, 0], a[:, 1], a[:, 2], a[:, 3], a[:, 4]
        today = np.zeros(len(k), bool)
    if len(k) == 0:
        return None
    c0 = np.where(ell < 0, 0, np.where(today, 1, 2))
    r = np.where(o < 0, 0, np.where(o == ell, 1, 2))
    return {"k": k.astype(np.int64), "ell": ell.astype(np.int64), "o": o.astype(np.int64), "c0": c0, "r": r,
            "day": dd.astype(np.int64), "K": nR + 1, "nR": nR, "j": jm.astype(np.int64), "n_mem": n}


def _cv_mixture(T: dict, days: np.ndarray):
    """Leave-one-day-out log2 p0 and log2 p1 for each transition (card F5a M0 / M1)."""
    k, ell, o, c0, r, dd, K = T["k"], T["ell"], T["o"], T["c0"], T["r"], T["day"], T["K"]
    n = len(k)
    stay = (ell >= 0) & (k == ell)
    join = (r == 2) & (k == o)
    cls1 = np.where(stay, 0, np.where(join, 1, 2))
    dmap = {d: i for i, d in enumerate(days)}
    di = np.array([dmap[d] for d in dd])
    nDd = len(days)
    A0 = np.zeros((nDd, 3, 2))
    np.add.at(A0, (di, c0, (~stay).astype(int)), 1)
    A1 = np.zeros((nDd, 3, 3, 3))
    np.add.at(A1, (di, c0, r, cls1), 1)
    jm, nm = T["j"], T["n_mem"]
    P = np.zeros((nDd, nm, K))
    np.add.at(P, (di, jm, k), 1)
    T0, T1, TP = A0.sum(0), A1.sum(0), P.sum(0)
    tr0 = T0[None] - A0                                   # training counts per held-out day
    tr1 = T1[None] - A1
    trP = TP[None] - P                                    # [nD, n_mem, K]
    # member-specific popularity (the null unit's own artifacts), shrunk toward the pooled popularity (beta = 2)
    pool = trP.sum(1)
    pi_pool = (pool + ALPHA) / (pool + ALPHA).sum(1, keepdims=True)          # [nD, K]
    beta = 2.0
    pi = (trP + beta * pi_pool[:, None, :]) / (trP.sum(2, keepdims=True) + beta)   # [nD, n_mem, K]
    pik = pi[di, jm, k]
    pil = np.where(ell >= 0, pi[di, jm, np.maximum(ell, 0)], 0.0)
    pio = np.where((r == 2), pi[di, jm, np.maximum(o, 0)], 0.0)
    # M0
    a0 = tr0[di, c0]                                      # [n, 2] (stay, not)
    ws0 = np.where(c0 == 0, 0.0, (a0[:, 0] + ALPHA) / (a0.sum(1) + 2 * ALPHA))
    p0 = np.where(stay, ws0, (1 - ws0) * pik / np.maximum(1 - pil, 1e-12))
    # M1 (amendment A1): M0's stay weight is kept; the unit's allocation enters only through the split of the
    # non-stay mass between the others' artifact o and the rest (join), so g carries no timing / persistence term.
    a1 = tr1[di, c0, r]                                   # [n, 3] (stay, join, other)
    has_j = r == 2
    vj = np.where(has_j, (a1[:, 1] + ALPHA) / (a1[:, 1] + a1[:, 2] + 2 * ALPHA), 0.0)
    rest = np.maximum(1 - pil - pio, 1e-12)
    p_move = 1 - ws0
    p1 = np.where(stay, ws0, np.where(join, p_move * vj, p_move * (1 - vj) * pik / rest))
    p1 = np.where(has_j, p1, p0)                          # no others' artifact distinct from own: M1 = M0
    p0 = np.clip(p0, 1e-12, 1)
    p1 = np.clip(p1, 1e-12, 1)
    return np.log2(p0), np.log2(p1), cls1


def coord_gain(U: Unit, members, R=None, S=None, night=False, others=None, window=(0, 1), return_parts=False,
               others_per=None):
    """g_G in bits per held-out working member-transition (card F5a, amendment A1); nan if undefined."""
    if len(members) < 2 and others is None and others_per is None:
        return np.nan if not return_parts else {"g": np.nan, "n": 0}
    T = _transitions(U, members, R, S, night=night, others=others, window=window, others_per=others_per)
    if T is None or T["nR"] == 0 or len(T["k"]) < 10 or len(np.unique(T["day"])) < 2:
        return np.nan if not return_parts else {"g": np.nan, "n": 0 if T is None else len(T["k"])}
    days = np.unique(T["day"])
    l0, l1, cls = _cv_mixture(T, days)
    g = float(np.mean(l1 - l0))
    if not return_parts:
        return g
    return {"g": g, "n": int(len(l0)), "L0": float(-l0.mean()), "L1": float(-l1.mean()),
            "share_stay": float((cls == 0).mean()), "share_join": float((cls == 1).mean()),
            "share_join_ctx": float((T["r"] == 2).mean()), "nR": int(T["nR"])}


def gain_ctx(U: Unit, members, R=None, **kw) -> float:
    """Gain per join-context transition (amendment A1c): g / share of transitions where the others' artifact differs
    from the member's own. Normalizes away how often the 'others' are working (their activity), so units, outsider
    groups and size-matched subsets with different activity compare fairly."""
    p = coord_gain(U, members, R, return_parts=True, **kw)
    if not np.isfinite(p.get("g", np.nan)) or not p.get("share_join_ctx"):
        return np.nan
    return p["g"] / p["share_join_ctx"]


def content_gain(U: Unit, members):
    """g^c: the same relational model on content clusters (alphabet = clusters)."""
    if U.C is None or len(members) < 2:
        return np.nan
    m = np.asarray(members, int)
    K = int(U.C.max()) + 1
    if K <= 1:
        return np.nan
    fake = Unit(U.name, U.regime, U.agents, list(range(K)), U.day_of_bin, U.C, (U.C >= 0).astype(int), U.yh,
                extra={"Wn": np.ones((U.nA, K), np.int64) * 10})
    R = np.arange(K)
    return coord_gain(fake, m, R=R)


# ============================================================================ nulls
def rotate_rows(U: Unit, members, rng, S=None) -> np.ndarray:
    """Member-shift surrogate: each member's row rotated within each day by an independent offset."""
    S = (U.S if S is None else S).copy()
    for a in members:
        for (lo, hi) in U.day_slices:
            L = hi - lo
            if L > 1:
                S[a, lo:hi] = np.roll(S[a, lo:hi], rng.integers(0, L))
    return S


def shift_null(U: Unit, members, n_draw=100, seed=0, g0=None, night=False, window=(0, 1)):
    rng = np.random.default_rng(seed)
    R = U.shared_artifacts(members)
    g0 = coord_gain(U, members, R, night=night, window=window) if g0 is None else g0
    vals, vctx = [], []
    for _ in range(n_draw):
        Sx = rotate_rows(U, members, rng)
        p = coord_gain(U, members, R, S=Sx, night=night, window=window, return_parts=True)
        vals.append(p.get("g", np.nan))
        vctx.append(p["g"] / p["share_join_ctx"] if (np.isfinite(p.get("g", np.nan)) and p.get("share_join_ctx")) else np.nan)
    v = np.asarray(vals, float)
    vc = np.asarray(vctx, float)
    v = v[np.isfinite(v)]
    vc = vc[np.isfinite(vc)]
    if len(v) < 10 or not np.isfinite(g0):
        return {"g": g0, "mu": np.nan, "sd": np.nan, "z": np.nan, "p": np.nan, "sd_ctx": np.nan}
    sd = v.std(ddof=1)
    return {"g": g0, "mu": float(v.mean()), "sd": float(sd), "z": float((g0 - v.mean()) / sd) if sd > 1e-12 else np.nan,
            "p": float((1 + (v >= g0).sum()) / (1 + len(v))),
            "sd_ctx": float(vc.std(ddof=1)) if len(vc) >= 10 else np.nan}


def matched_gains(U: Unit, members, R, k, n_draw=10, seed=0, window=(0, 1)):
    """Size-matched in/out gains per join-context transition (amendments A1b, A1c): for each member j, 'others' = k random
    other members (in) or k random non-members (out), same R_G; means over n_draw draws; k = min(n - 1, active
    non-members). An outsider set that never sits on another artifact contributes 0 (no information)."""
    rng = np.random.default_rng(seed)
    mem = list(members)
    out_pool = [a for a in np.flatnonzero(U.act_a > 0) if a not in set(mem)]
    gi, go = [], []
    for _ in range(n_draw):
        per_in = [list(rng.choice([b for b in mem if b != j], k, replace=False)) for j in mem]
        per_out = [list(rng.choice(out_pool, k, replace=False)) for j in mem]
        a1 = gain_ctx(U, mem, R, others_per=per_in, window=window)
        a2 = gain_ctx(U, mem, R, others_per=per_out, window=window)
        if np.isfinite(a1):
            gi.append(a1)
        if np.isfinite(a2):
            go.append(a2)
    return (float(np.mean(gi)) if gi else np.nan), (float(np.mean(go)) if go else 0.0)


class CompNull:
    """Composition null (card F5c(i) as amended by A1/A1b): random groups drawn from agents *outside* the test unit,
    activity-matched (+-50%), evaluated on the *test unit's* artifacts R_G (o from the random group), at a matched size
    k = min(n, number of active outsiders); the observed value is the unit's gain on random k-subsets of its members
    (= g when k = n). Under a common field outsiders who touch R_G co-allocate as members do; under a group store not."""

    def __init__(self, U: Unit, n_draw=200, seed=0, night=False, window=(0, 1)):
        self.U, self.n_draw, self.night, self.window = U, n_draw, night, window
        self.seed = seed
        self.pool = np.flatnonzero(U.act_a > 0)

    def null(self, members, R, k):
        rng = np.random.default_rng(self.seed + 31 * len(members))
        out_pool = np.setdiff1d(self.pool, np.asarray(members, int))
        if k < 2 or len(out_pool) < k:
            return np.array([])
        act = self.U.act_a[np.asarray(members, int)].sum() * k / len(members)
        gs, acts = [], []
        for _ in range(self.n_draw * 3):
            m = rng.choice(out_pool, k, replace=False)
            acts.append(self.U.act_a[m].sum())
            g = gain_ctx(self.U, list(m), R, night=self.night, window=self.window)
            gs.append(g if np.isfinite(g) else 0.0)
        gs, acts = np.asarray(gs), np.asarray(acts)
        sel = (acts >= 0.5 * act) & (acts <= 1.5 * act)
        # amendment A1d: no activity-matched outside reference (fewer than 30 matched draws, or fewer than 30 distinct
        # outsider groups) -> not testable against a common field; the unit cannot qualify
        if sel.sum() < 30:
            return np.array([])
        return gs[sel][:self.n_draw]

    def observed(self, members, R, k, g0=None):
        if k >= len(members):
            v = gain_ctx(self.U, list(members), R, night=self.night, window=self.window)
            return v
        rng = np.random.default_rng(self.seed + 7)
        vals = []
        for _ in range(20):
            sub = list(rng.choice(members, k, replace=False))
            v = gain_ctx(self.U, sub, R, night=self.night, window=self.window)
            if np.isfinite(v):
                vals.append(v)
        return float(np.mean(vals)) if vals else np.nan

    def z(self, members, g0, R=None, sd_floor=0.0):
        R = self.U.shared_artifacts(members) if R is None else R
        n_out = len(np.setdiff1d(self.pool, np.asarray(members, int)))
        # amendment A2.5: matched size = the largest k <= min(n, n_out) with >= 10 distinct outsider groups
        k = min(len(members), n_out)
        while k > 2 and math.comb(n_out, k) < 10:
            k -= 1
        if n_out < 2 or math.comb(n_out, k) < 10:
            return {"z": np.nan, "mu": np.nan, "sd": np.nan, "p": np.nan, "n": 0, "k": k, "obs": np.nan,
                    "testable": False}
        v = self.null(members, R, k)
        obs = self.observed(list(members), R, k, g0)
        if len(v) < 20 or not np.isfinite(obs):
            return {"z": np.nan, "mu": np.nan, "sd": np.nan, "p": np.nan, "n": int(len(v)), "k": k, "obs": obs,
                    "testable": False}
        sd = max(v.std(ddof=1), sd_floor)
        return {"z": float((obs - v.mean()) / sd) if sd > 1e-12 else np.nan, "mu": float(v.mean()), "sd": float(sd),
                "p": float((1 + (v >= obs).sum()) / (1 + len(v))), "n": int(len(v)), "k": k, "obs": obs,
                "testable": True}


def evaluate(U: Unit, members, cn: CompNull, n_shift=100, seed=0, night=False, window=(0, 1)) -> dict:
    """g with both nulls and the decision rule (card F5, amendments A1, A1b): g > 0, z_shift >= 2,
    z_spec >= 2 on the gain per join-context transition (A1c) at the matched size k (sd floor: the shift null's sd on
    that scale), and matched specificity 1 - g_out_k / g_in_k >= 0.5 (per join-context transition; others = k random
    non-members vs k random other members on the same artifacts)."""
    members = sorted(int(a) for a in members)
    R = U.shared_artifacts(members)
    parts = coord_gain(U, members, R, night=night, window=window, return_parts=True)
    g0 = parts["g"]
    sh = shift_null(U, members, n_shift, seed, g0, night=night, window=window)
    cz = cn.z(members, g0, R, sd_floor=sh["sd_ctx"] if np.isfinite(sh.get("sd_ctx", np.nan)) else 0.0)
    nonm = [a for a in range(U.nA) if a not in set(members) and U.act_a[a] > 0]
    g_out = coord_gain(U, members, R, night=night, others=nonm, window=window) if nonm else np.nan
    spec = np.nan
    gi_k = go_k = np.nan
    if np.isfinite(g0) and g0 > 0 and nonm and len(members) >= 2 and not night:
        k = min(len(members) - 1, len(nonm))
        gi_k, go_k = matched_gains(U, members, R, k, n_draw=10, seed=seed, window=window)
        spec = 1 - go_k / gi_k if (np.isfinite(gi_k) and gi_k > 0) else np.nan
    elif np.isfinite(g0) and g0 > 0 and not nonm:
        spec = np.nan
    qual = bool(len(members) >= 2 and np.isfinite(g0) and g0 > 0 and np.isfinite(cz["z"]) and cz["z"] >= 2
                and np.isfinite(sh["z"]) and sh["z"] >= 2 and np.isfinite(spec) and spec >= 0.5)
    return {"members": members, "n": len(members), "nR": int(len(R)), "g": g0, "n_trans": parts.get("n", 0),
            "share_join": parts.get("share_join", np.nan), "share_stay": parts.get("share_stay", np.nan),
            "z_comp": cz["z"], "p_comp": cz["p"], "null_comp_mu": cz["mu"], "comp_k": cz.get("k"),
            "testable": bool(cz.get("testable", False)),
            "z_shift": sh["z"], "p_shift": sh["p"], "null_shift_mu": sh["mu"], "null_shift_sd": sh["sd"],
            "g_out": g_out, "g_in_k": gi_k, "g_out_k": go_k, "specificity": spec, "qualifies": qual}


# ============================================================================ F5b Krakauer decomposition
def unit_state(U: Unit, members, R=None, S=None) -> np.ndarray:
    """x_G(b): R_G artifact with most member commits (ties lowest index); -1 = none of R_G advanced."""
    R = U.shared_artifacts(members) if R is None else R
    nR = len(R)
    X = map_states(U, members, R, S)
    m = np.asarray(members, int)
    Wt = (U.N[m] if S is None else np.ones_like(X))
    B = X.shape[1]
    cnt = np.zeros((B, nR + 1))
    valid = (X >= 0) & (X < nR)
    bb = np.broadcast_to(np.arange(B), X.shape)
    np.add.at(cnt, (bb[valid], X[valid]), Wt[valid])
    cnt = cnt[:, :nR]
    if nR == 0:
        return np.full(B, -1)
    return np.where(cnt.max(1) > 0, cnt.argmax(1), -1)


def env_state(U: Unit, members, R=None) -> np.ndarray:
    """y_G(b) in 0..7: (any non-member commit, a non-member commit on R_G, exogenous input)."""
    R = U.shared_artifacts(members) if R is None else R
    mask = np.ones(U.nA, bool)
    mask[np.asarray(members, int)] = False
    nm = U.S[mask]
    yw = (nm >= 0).any(0) if mask.any() else np.zeros(U.nB, bool)
    yr = np.isin(nm, R).any(0) if (mask.any() and len(R)) else np.zeros(U.nB, bool)
    return (yw.astype(int) * 4 + yr.astype(int) * 2 + U.yh.astype(int)).astype(np.int64)


def krakauer(U: Unit, x: np.ndarray, y: np.ndarray) -> dict:
    """Held-out (leave-one-day-out) log-losses for the unit state x (alphabet -1 = none, 0..K-1) (card F5b)."""
    b0 = np.arange(U.nB - 1)
    b0 = b0[U.day_of_bin[b0] == U.day_of_bin[b0 + 1]]
    if len(b0) < 10:
        return {"ok": False}
    xn, xc, yc = x[b0 + 1], x[b0], y[b0]
    dd = U.day_of_bin[b0 + 1]
    days = np.unique(dd)
    if len(days) < 2:
        return {"ok": False}
    K = int(max(x.max(), 0)) + 1
    sym = xn + 1                                           # 0 = none, 1..K
    work_n = xn >= 0
    stay = (xc >= 0) & (xn == xc)
    ec = (xc >= 0).astype(int)
    di = np.searchsorted(days, dd)
    nDd = len(days)
    # count tables per day
    Pm = np.zeros((nDd, K + 1)); np.add.at(Pm, (di, sym), 1)
    Pw = np.zeros((nDd, K)); np.add.at(Pw, (di[work_n], xn[work_n]), 1)
    Z_x = np.zeros((nDd, 2, 2)); np.add.at(Z_x, (di, ec, work_n.astype(int)), 1)
    Z_y = np.zeros((nDd, 8, 2)); np.add.at(Z_y, (di, yc, work_n.astype(int)), 1)
    Z_xy = np.zeros((nDd, 2, 8, 2)); np.add.at(Z_xy, (di, ec, yc, work_n.astype(int)), 1)
    m_st = work_n & (xc >= 0)
    S_x = np.zeros((nDd, 2)); np.add.at(S_x, (di[m_st], (~stay[m_st]).astype(int)), 1)
    S_xy = np.zeros((nDd, 8, 2)); np.add.at(S_xy, (di[m_st], yc[m_st], (~stay[m_st]).astype(int)), 1)

    def tr(A):
        return A.sum(0)[None] - A
    Pm_t, Pw_t, Zx_t, Zy_t, Zxy_t, Sx_t, Sxy_t = map(tr, (Pm, Pw, Z_x, Z_y, Z_xy, S_x, S_xy))
    pim = (Pm_t + ALPHA) / (Pm_t + ALPHA).sum(1, keepdims=True)
    piw = (Pw_t + ALPHA) / (Pw_t + ALPHA).sum(1, keepdims=True)

    def p_work(Z):
        return (Z[..., 1] + ALPHA) / (Z.sum(-1) + 2 * ALPHA)

    xi = np.maximum(xn, 0)
    xci = np.maximum(xc, 0)
    # marginal
    L0 = -np.log2(pim[di, sym])
    # which-artifact part given working: popularity, or stay mixture when x is an artifact
    pw_pop = piw[di, xi]
    ws_x = (Sx_t[di, 0] + ALPHA) / (Sx_t[di].sum(1) + 2 * ALPHA)
    ws_xy = (Sxy_t[di, yc, 0] + ALPHA) / (Sxy_t[di, yc].sum(1) + 2 * ALPHA)
    pil = piw[di, xci]

    def which(ws):
        return np.where(xc >= 0, np.where(stay, ws, (1 - ws) * pw_pop / np.maximum(1 - pil, 1e-12)), pw_pop)

    def ll(pwork, pwhich):
        return -np.log2(np.clip(np.where(work_n, pwork * pwhich, 1 - pwork), 1e-12, 1))
    L_x = ll(p_work(Zx_t[di, ec]), which(ws_x))
    L_y = ll(p_work(Zy_t[di, yc]), pw_pop)
    L_xy = ll(p_work(Zxy_t[di, ec, yc]), which(ws_xy))
    H = float(L0.mean())
    A = H - float(L_x.mean())
    Astar = float(L_y.mean() - L_xy.mean())
    E = float(L_x.mean() - L_xy.mean())
    return {"ok": True, "n": int(len(b0)), "H": H, "colonial": A, "organismal": Astar, "environmental": E,
            "iota": Astar / H if H > 1e-9 else np.nan, "rate": float(work_n.mean())}


def unit_krakauer(U: Unit, members) -> dict:
    R = U.shared_artifacts(members)
    if len(R) == 0:
        return {"ok": False}
    return krakauer(U, unit_state(U, members, R), env_state(U, members, R))


def krakauer_shift(U: Unit, members, n_draw=40, seed=0) -> dict:
    """Unit individuality against its aggregation baseline (amendment A1): iota_G vs iota of the same members with
    each member's series rotated within days (independent members aggregated by the same unit-state rule)."""
    R = U.shared_artifacts(members)
    if len(R) == 0:
        return {"ok": False}
    k0 = krakauer(U, unit_state(U, members, R), env_state(U, members, R))
    if not k0.get("ok"):
        return {"ok": False}
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(n_draw):
        Sx = rotate_rows(U, members, rng)
        x = unit_state(U, members, R, S=Sx)
        kk = krakauer(U, x, env_state(U, members, R))
        if kk.get("ok") and np.isfinite(kk["iota"]):
            vals.append(kk["iota"])
    v = np.asarray(vals)
    if len(v) < 10:
        return {**k0, "iota_shift_mu": np.nan, "z_iota_shift": np.nan}
    sd = v.std(ddof=1)
    return {**k0, "iota_shift_mu": float(v.mean()), "z_iota_shift": float((k0["iota"] - v.mean()) / sd) if sd > 1e-12 else np.nan}


def member_iota(U: Unit, members) -> float:
    """Commit-weighted mean iota of the members as agent + own artifact units (R_i = repos >= 50% by i)."""
    vals = []
    for a in members:
        Ra = U.shared_artifacts([a])
        if len(Ra):
            k1 = krakauer(U, unit_state(U, [a], Ra), env_state(U, [a], Ra))
            if k1.get("ok") and np.isfinite(k1["iota"]):
                vals.append((k1["iota"], U.act_a[a]))
    if not vals:
        return np.nan
    return float(np.average([v for v, _ in vals], weights=[w for _, w in vals]))


# ============================================================================ F7 multi-layer graph
LAYERS = ("w_sync", "w_coad", "w_reply", "w_coart")


def layer_matrices(agents: list, rows) -> dict:
    """rows: iterable of (i, j, w_sync, w_coad, w_reply, w_coart) agent codes. Returns normalized matrices + mean."""
    pos = {a: k for k, a in enumerate(agents)}
    n = len(agents)
    M = {L: np.zeros((n, n)) for L in LAYERS}
    for r in rows:
        i, j = r[0], r[1]
        if i not in pos or j not in pos:
            continue
        for t, L in enumerate(LAYERS):
            v = float(r[2 + t]) if r[2 + t] is not None and np.isfinite(r[2 + t]) else 0.0
            M[L][pos[i], pos[j]] = M[L][pos[j], pos[i]] = max(v, 0.0)
    for L in LAYERS:
        s = M[L].sum()
        if s > 0:
            M[L] = M[L] / s
    M["multi"] = sum(M[L] for L in LAYERS) / len(LAYERS)
    return M


def communities(W: np.ndarray, min_size=2) -> list[list[int]]:
    cs = r2lib.greedy_modularity(W)
    return [sorted(c) for c in cs if len(c) >= min_size]


# ============================================================================ F6 bounded subset search
def crew_seeds(U: Unit, max_size=8) -> list[list[int]]:
    """Joint-work seeds: for each repo with >= 2 writers (>= 2 commits each), its writers by commits (<= max_size)."""
    out, seen = [], set()
    for k in range(len(U.repos)):
        w = np.flatnonzero(U.Wn[:, k] >= 2)
        if len(w) < 2:
            continue
        w = w[np.argsort(-U.Wn[w, k])][:max_size]
        key = tuple(sorted(int(a) for a in w))
        if key not in seen:
            seen.add(key)
            out.append(list(key))
    return out


def subset_search(U: Unit, pool=None, max_size=8, max_evals=3000, n_seed_pairs=10, sa_steps=400, restarts=3,
                  seed=0, S=None, seeds=None) -> dict:
    """Coordination-first search maximizing J(A) = total held-out coordination bits (card F6 + amendment A1).
    Seeds: joint-work crews, any extra seeds given (e.g. multi-layer communities) and the n_seed_pairs best pairs;
    local search (add / remove / swap until no gain) from each seed, then simulated annealing from the best.
    Bounded: sizes 2..max_size, <= 20 candidate agents (most active), <= max_evals objective evaluations."""
    rng = np.random.default_rng(seed)
    if pool is None:
        pool = np.argsort(-U.act_a)[:20]
        pool = [int(a) for a in pool if U.act_a[a] > 0]
    pset = set(pool)
    cache = {}
    n_eval = [0]

    def J(A):
        key = tuple(sorted(A))
        if key in cache:
            return cache[key]
        if n_eval[0] >= max_evals or len(key) < 2:
            return -np.inf
        n_eval[0] += 1
        gp = coord_gain(U, list(key), S=S, return_parts=True)
        # amendment A1: J = total held-out bits (g x n transitions), the unit model's log-likelihood gain over the
        # product of agent + own artifact models; per-transition g rewards noisy small sets (winner's curse)
        v = gp["g"] * gp["n"] if np.isfinite(gp["g"]) else -np.inf
        cache[key] = v
        return v

    def local(A):
        A = sorted(set(A))
        cur = J(A)
        improved = True
        while improved and n_eval[0] < max_evals:
            improved = False
            moves = []
            if len(A) < max_size:
                moves += [A + [c] for c in pool if c not in A]
            if len(A) > 2:
                moves += [[x for x in A if x != a] for a in A]
            best_v, best_B = cur, None
            for B in moves:
                v = J(B)
                if v > best_v + 1e-12:
                    best_v, best_B = v, sorted(B)
            if best_B is not None:
                A, cur = best_B, best_v
                improved = True
        return A, cur

    starts = []
    for c in crew_seeds(U, max_size):
        c = [a for a in c if a in pset]
        if len(c) >= 2:
            starts.append(c)
    for c in (seeds or []):
        c = [int(a) for a in c if int(a) in pset][:max_size]
        if len(c) >= 2:
            starts.append(c)
    pairs = [(a, b) for i, a in enumerate(pool) for b in pool[i + 1:]]
    pv = sorted(((J([a, b]), (a, b)) for (a, b) in pairs), reverse=True)
    starts += [list(pr) for (_, pr) in pv[:n_seed_pairs]]
    best_val, best = -np.inf, None
    for st in starts:
        A, v = local(st)
        if v > best_val:
            best_val, best = v, A
    if best is not None:
        for rs in range(restarts):
            A = list(best)
            cur = J(A)
            for step in range(sa_steps):
                if n_eval[0] >= max_evals:
                    break
                T = 0.5 * (0.01 / 0.5) ** (step / max(sa_steps - 1, 1))    # in bits (J is a total)
                move = rng.integers(0, 3)
                B = list(A)
                outs = [c for c in pool if c not in A]
                if move == 0 and len(A) < max_size and outs:
                    B.append(outs[rng.integers(0, len(outs))])
                elif move == 1 and len(A) > 2:
                    B.pop(rng.integers(0, len(A)))
                elif outs:
                    B[rng.integers(0, len(A))] = outs[rng.integers(0, len(outs))]
                else:
                    continue
                v = J(B)
                if not np.isfinite(v):
                    continue
                if v >= cur or rng.random() < math.exp((v - cur) / T):
                    A, cur = B, v
                    if cur > best_val:
                        best_val, best = cur, sorted(A)
    # prune: drop the member with the lowest held-out contribution while that contribution is <= 0 and dropping it
    # does not lower J by more than max(1 bit, 2%) (every member should gain from the unit)
    pruned = 0
    while best is not None and len(best) > 2:
        T = _transitions(U, best, S=S)
        if T is None or T["nR"] == 0:
            break
        l0, l1, _ = _cv_mixture(T, np.unique(T["day"]))
        contrib = np.array([(l1 - l0)[T["j"] == j].sum() for j in range(len(best))])
        if contrib.min() > 0:
            break
        cand = [a for t, a in enumerate(best) if t != int(contrib.argmin())]
        key = tuple(sorted(cand))
        vc = cache.get(key)
        if vc is None:
            gp = coord_gain(U, list(key), S=S, return_parts=True)
            vc = gp["g"] * gp["n"] if np.isfinite(gp["g"]) else -np.inf
            cache[key] = vc
        if vc < best_val - max(1.0, 0.02 * abs(best_val)):
            break
        best, best_val = sorted(cand), vc
        pruned += 1
    return {"members": best, "J": float(best_val) if np.isfinite(best_val) else np.nan, "n_eval": n_eval[0],
            "pruned": pruned}


def search_calibrated(U: Unit, n_surr=10, seed=0, **kw) -> dict:
    """Search on the data and on n_surr surrogate datasets (every agent's series rotated within days)."""
    res = subset_search(U, seed=seed, **kw)
    rng = np.random.default_rng(seed + 991)
    nulls = []
    for s in range(n_surr):
        Sx = rotate_rows(U, range(U.nA), rng)
        r = subset_search(U, seed=seed + 7 + s, S=Sx, **kw)
        nulls.append(r["J"])
    nv = np.asarray([v for v in nulls if np.isfinite(v)], float)
    res["null_J"] = nv.tolist()
    res["p_search"] = float((1 + (nv >= res["J"]).sum()) / (1 + len(nv))) if np.isfinite(res["J"]) else np.nan
    res["beats_all_surrogates"] = bool(np.isfinite(res["J"]) and len(nv) and res["J"] > nv.max())
    return res


# ============================================================================ H01 binary state (comparison, synthetic)
def to_r2_period(U: Unit) -> "r2lib.Period":
    """Build an H01 round-2 Period (binary write state) from the allocation panel, for the binary-state comparison."""
    vec = {}
    for a in range(U.nA):
        for k in np.unique(U.S[a][U.S[a] >= 0]):
            vec[(a, int(k))] = U.S[a] == k
    pos = np.zeros(U.nB, int)
    for (lo, hi) in U.day_slices:
        pos[lo:hi] = np.arange(hi - lo)
    active = np.zeros((U.nA, U.nD), bool)
    for di, (lo, hi) in enumerate(U.day_slices):
        active[:, di] = (U.S[:, lo:hi] >= 0).any(1)
    return r2lib.Period(name=U.name, regime=U.regime, day_of_bin=U.day_of_bin.copy(), pos_of_bin=pos,
                        agents=list(U.agents), projects=list(U.repos), vec=vec, Wn=U.Wn.copy(),
                        any_w=(U.S >= 0), yh=U.yh.copy(), active=active)


def binary_h01(U: Unit, members, n_draw=300, seed=0) -> dict:
    P = to_r2_period(U)
    nc = r2lib.NullCache(P, n_draw=n_draw, seed=seed)
    r = r2lib.composition_excess(P, members, nc)
    al = r2lib.alloc_shift(P, members, n_draw=60, seed=seed)
    return {"z_bin": r.get("z", np.nan), "iota_bin": r.get("iota", np.nan), "z_alloc_bin": al.get("z", np.nan)}


def stouffer(zs):
    return r2lib.stouffer(zs)


def mh_logor(tables):
    """Mantel-Haenszel pooled log odds ratio over 2x2 tables [[a, b], [c, d]] (a = exposed & outcome), with the
    Robins-Breslow-Greenland variance."""
    R = S = 0.0
    P_R = PS_QR = Q_S = 0.0
    for t in tables:
        a, b, c, d = map(float, (t[0][0], t[0][1], t[1][0], t[1][1]))
        n = a + b + c + d
        if n == 0:
            continue
        r_, s_ = a * d / n, b * c / n
        p_, q_ = (a + d) / n, (b + c) / n
        R += r_; S += s_
        P_R += p_ * r_; PS_QR += p_ * s_ + q_ * r_; Q_S += q_ * s_
    if R <= 0 or S <= 0:
        return {"logor": np.nan, "se": np.nan, "z": np.nan}
    lor = math.log(R / S)
    var = P_R / (2 * R * R) + PS_QR / (2 * R * S) + Q_S / (2 * S * S)
    se = math.sqrt(var)
    return {"logor": lor, "se": se, "z": lor / se}
