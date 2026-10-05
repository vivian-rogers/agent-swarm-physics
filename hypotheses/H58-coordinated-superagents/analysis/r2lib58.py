"""H58 round-2 estimators: occupied-set attraction (Lambda), exclusion on shared artifacts (T), static partition.

Card: hypotheses/H58-coordinated-superagents/README.md, "Round 2 design" (R1, R2) and amendments. No import from any
other hypothesis folder. Thread use is capped at 2 before numpy is imported.

Panel (one unit of analysis, or one shared repo at file level):
  agents[nA]   agent codes;  K   alphabet size (repos, or files)
  S[nA, nB]    dominant artifact of the agent in the bin (-1 none)
  day[nB]      day index of each active bin;  act[nA]  commits (or touches) per agent

Pair matrices (the core object; amendment R2-A1): for a draw of the panel (observed, or every row rotated within days),
  J[j, q]  joins: moves of j onto an artifact q occupies in bin b or b+1 (other than j's own last artifact)
  E[j, q]  their expectation under agent + own artifacts (leave-one-day-out member popularity, shrunk to the pool)
  N[j, q]  join-context moves of j with respect to q
  SAME[i, j], BOTH[i, j]  same-artifact and eligible pair-bins (both working, a common artifact that day)
Any group's attraction, exclusion and their rotation nulls are sums over its pairs, so groups, outsider references and
random-partition references are evaluated from one set of draws.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
           "NUMEXPR_NUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ.setdefault(_v, "2")

import datetime as dt  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402
from dataclasses import dataclass, field  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
D = ROOT / "data/processed/H58-coordinated-superagents"
R2 = D / "r2"
SH = ROOT / "data/processed/shared"
sys.path.insert(0, str(ROOT / "infra/shared"))

ALPHA, BETA = 0.5, 2.0
REPL = ["38a", "38b", "38c", "51a", "51b", "51c", "51d", "51e"]
NATIVE = ["39", "40", "41", "44"]
POWERED = ["51b", "51c", "51d"]


# ============================================================================ panel
@dataclass
class Panel:
    name: str
    agents: list
    K: int
    S: np.ndarray
    day: np.ndarray
    act: np.ndarray
    extra: dict = field(default_factory=dict)

    def __post_init__(self):
        self.nA, self.nB = self.S.shape
        self.days = np.unique(self.day)
        self.nD = len(self.days)
        self.slices = []
        for d in self.days:
            idx = np.flatnonzero(self.day == d)
            self.slices.append((int(idx[0]), int(idx[-1]) + 1))
        self.dpos = np.searchsorted(self.days, self.day)


def units_meta():
    return json.loads((D / "units.json").read_text())


def assert_no_reserved(meta):
    from common import holdout_mask
    for x in meta:
        assert not any(holdout_mask(x["days"], [x["goal_no"]] * len(x["days"]))), x["unit"]


def panel_from_commits(name, cm, meta, bin_min=30, art_col="repo_id", t_col="m"):
    """Dominant artifact per agent x bin (ties: the latest commit), as round 1's loader. cm: polars frame with
    unit-filtered rows (day, m, agent, art_col)."""
    nb_day = []
    for ws, we in zip(meta["win_start"], meta["win_end"]):
        w = (dt.datetime.fromisoformat(we) - dt.datetime.fromisoformat(ws)).total_seconds() / 60
        nb_day.append(int(np.ceil(w / bin_min)))
    offs = np.concatenate([[0], np.cumsum(nb_day)])
    nB = int(offs[-1])
    day = np.repeat(np.arange(len(nb_day)), nb_day)
    agents = sorted(cm["agent"].unique().to_list())
    apos = {a: i for i, a in enumerate(agents)}
    arts = sorted(cm[art_col].unique().to_list())
    rpos = {r: i for i, r in enumerate(arts)}
    dd = cm["day"].to_numpy().astype(int)
    b = (offs[dd] + (cm[t_col].to_numpy() // bin_min)).astype(int)
    b = np.minimum(b, offs[dd + 1] - 1)
    ai = np.array([apos[a] for a in cm["agent"].to_list()], int)
    ri = np.array([rpos[r] for r in cm[art_col].to_list()], int)
    nA, K = len(agents), len(arts)
    cnt = np.zeros((nA, nB, K), np.int32)
    np.add.at(cnt, (ai, b, ri), 1)
    N = cnt.sum(2)
    S = np.where(N > 0, cnt.argmax(2), -1)
    tie = (cnt == cnt.max(2, keepdims=True)).sum(2) > 1
    if tie.any():
        order = np.argsort(cm[t_col].to_numpy(), kind="stable")
        last = {}
        for t in order:
            last[(ai[t], b[t])] = ri[t]
        for (a_, b_) in zip(*np.nonzero(tie & (N > 0))):
            S[a_, b_] = last[(a_, b_)]
    act = np.bincount(ai, minlength=nA).astype(float)
    # active bins only matter through S; keep every bin of the calendar window (as round 1)
    return Panel(name, agents, K, S.astype(np.int64), day, act,
                 extra={"arts": arts, "offs": offs, "nb_day": nb_day, "N": N})


def load_panel(name, bin_min=30):
    import polars as pl
    meta = {x["unit"]: x for x in units_meta()}[name]
    assert_no_reserved([meta])
    cm = pl.read_parquet(D / "commits.parquet").filter(pl.col("unit") == name)
    return panel_from_commits(name, cm, meta, bin_min)


# ============================================================================ helpers
def ffill(S):
    n, B = S.shape
    idx = np.where(S >= 0, np.arange(B)[None, :], 0)
    np.maximum.accumulate(idx, axis=1, out=idx)
    out = S[np.arange(n)[:, None], idx]
    seen = np.maximum.accumulate(S >= 0, axis=1)
    out[~seen] = -1
    return out


def rotate_all(P: Panel, rng, rows=None) -> np.ndarray:
    S = P.S.copy()
    rows = range(P.nA) if rows is None else rows
    for a in rows:
        for (lo, hi) in P.slices:
            L = hi - lo
            if L > 1:
                S[a, lo:hi] = np.roll(S[a, lo:hi], rng.integers(0, L))
    return S


def lodo_pi(P: Panel, S=None) -> np.ndarray:
    """pi[a, d, k]: agent a's leave-day-d-out artifact frequencies (working bins), shrunk toward the pooled
    frequencies of all agents (weight BETA); pooled smoothed with ALPHA. Rotations within days keep it unchanged."""
    S = P.S if S is None else S
    C = np.zeros((P.nA, P.nD, P.K))
    a_, b_ = np.nonzero(S >= 0)
    np.add.at(C, (a_, P.dpos[b_], S[a_, b_]), 1)
    tot = C.sum(1)                                   # [nA, K]
    tr = tot[:, None, :] - C                         # [nA, nD, K]
    pool = tr.sum(0)                                 # [nD, K]
    pp = (pool + ALPHA) / (pool + ALPHA).sum(1, keepdims=True)
    return (tr + BETA * pp[None]) / (tr.sum(2, keepdims=True) + BETA)


def moves_of(P: Panel, S: np.ndarray, L: np.ndarray, j: int):
    """Within-day moves of agent j: b (source bin), k (target), ell (own last artifact up to b), day position."""
    b0 = np.arange(P.nB - 1)
    b0 = b0[P.day[b0] == P.day[b0 + 1]]
    k = S[j, b0 + 1]
    ell = L[j, b0]
    ok = (k >= 0) & (ell >= 0) & (k != ell)
    return b0[ok], k[ok], ell[ok], P.dpos[b0[ok] + 1]


# ============================================================================ pair matrices
def pair_attraction(P: Panel, S: np.ndarray, pi: np.ndarray, window=(0, 1)):
    """J, E, N [nA, nA] for one draw S (amendment R2-A1: pairwise-additive occupied-set attraction)."""
    nA = P.nA
    L = ffill(S)
    J = np.zeros((nA, nA))
    E = np.zeros((nA, nA))
    N = np.zeros((nA, nA))
    for j in range(nA):
        b, k, ell, dp = moves_of(P, S, L, j)
        if len(b) == 0:
            continue
        den = np.maximum(1 - pi[j, dp, ell], 1e-9)            # [m]
        acc_j = np.zeros(nA)
        acc_e = np.zeros(nA)
        ctx = np.zeros((nA, len(b)), bool)
        v0 = None
        val0 = None
        for w in window:
            v = S[:, b + w]                                    # [nA, m]
            val = (v >= 0) & (v != ell[None, :])
            ctx |= val
            if v0 is not None:                                 # the same artifact in both bins counts once
                val = val & ~(val0 & (v == v0))
            pv = np.where(val, pi[j, dp[None, :], np.maximum(v, 0)], 0.0) / den[None, :]
            acc_e += pv.sum(1)
            acc_j += (val & (v == k[None, :])).sum(1)
            if v0 is None:
                v0, val0 = v, val
        J[j] = acc_j
        E[j] = acc_e
        N[j] = ctx.sum(1)
    np.fill_diagonal(J, 0)
    np.fill_diagonal(E, 0)
    np.fill_diagonal(N, 0)
    return J, E, N


def pair_exclusion(P: Panel, S: np.ndarray):
    """SAME, BOTH [nA, nA]: same-artifact and eligible pair-bins (both working; a common artifact that day)."""
    nA = P.nA
    SAME = np.zeros((nA, nA))
    BOTH = np.zeros((nA, nA))
    for (lo, hi) in P.slices:
        Sd = S[:, lo:hi]
        W = (Sd >= 0).astype(float)
        if W.sum() == 0:
            continue
        ks = np.unique(Sd[Sd >= 0])
        oh = (Sd[:, :, None] == ks[None, None, :]).astype(float)   # [nA, Ld, Kd]
        Dset = oh.max(1)                                           # [nA, Kd] day sets
        share = (Dset @ Dset.T) > 0
        same = np.einsum("ilk,jlk->ij", oh, oh)
        both = W @ W.T
        SAME += np.where(share, same, 0)
        BOTH += np.where(share, both, 0)
    np.fill_diagonal(SAME, 0)
    np.fill_diagonal(BOTH, 0)
    return SAME, BOTH


@dataclass
class Draws:
    """Observed and rotation-null pair matrices of one panel."""
    J: np.ndarray        # [R + 1, nA, nA]; index 0 = observed
    E: np.ndarray
    N: np.ndarray
    SAME: np.ndarray
    BOTH: np.ndarray
    act: np.ndarray


def make_draws(P: Panel, R=100, seed=0, attraction=True, exclusion=True, window=(0, 1)) -> Draws:
    rng = np.random.default_rng(seed)
    pi = lodo_pi(P)
    Js, Es, Ns, SAs, BOs = [], [], [], [], []
    for r in range(R + 1):
        S = P.S if r == 0 else rotate_all(P, rng)
        if attraction:
            J, E, N = pair_attraction(P, S, pi, window)
            Js.append(J); Es.append(E); Ns.append(N)
        if exclusion:
            SA, BO = pair_exclusion(P, S)
            SAs.append(SA); BOs.append(BO)
    z = np.zeros((R + 1, P.nA, P.nA))
    return Draws(np.array(Js) if Js else z, np.array(Es) if Es else z, np.array(Ns) if Ns else z,
                 np.array(SAs) if SAs else z, np.array(BOs) if BOs else z, P.act.copy())


# ============================================================================ group statistics
def _zs(obs, null):
    null = null[np.isfinite(null)]
    if len(null) < 10 or not np.isfinite(obs):
        return np.nan, np.nan
    sd = null.std(ddof=1)
    return (float((obs - null.mean()) / sd) if sd > 1e-12 else np.nan), float(sd)


def lam_group(Dr: Draws, G, Q=None):
    """Lambda (observed and per rotation) of members G with reference set Q (default: co-members). Returns arrays."""
    G = np.asarray(G, int)
    if Q is None:
        J = Dr.J[:, G][:, :, G].sum((1, 2))
        E = Dr.E[:, G][:, :, G].sum((1, 2))
        N = Dr.N[:, G][:, :, G].sum((1, 2))
    else:
        Q = np.asarray(Q, int)
        J = Dr.J[:, G][:, :, Q].sum((1, 2))
        E = Dr.E[:, G][:, :, Q].sum((1, 2))
        N = Dr.N[:, G][:, :, Q].sum((1, 2))
    with np.errstate(invalid="ignore", divide="ignore"):
        lam = np.where(E > 0, J / E, np.nan)
    return lam, J, E, N


def excl_group(Dr: Draws, G):
    G = np.asarray(G, int)
    iu = np.triu_indices(len(G), 1)
    sa = Dr.SAME[:, G][:, :, G][:, iu[0], iu[1]].sum(1)
    bo = Dr.BOTH[:, G][:, :, G][:, iu[0], iu[1]].sum(1)
    with np.errstate(invalid="ignore", divide="ignore"):
        C = np.where(bo > 0, sa / bo, np.nan)
    return C, sa, bo


def a_rule(Dr: Draws, G, n_draw=200, n_in=20, seed=0, min_ctx=10, min_matched=30):
    """Attraction candidate test (card R1 A-rule, amendment R2-A1 pairwise form)."""
    rng = np.random.default_rng(seed)
    G = sorted(int(a) for a in G)
    n = len(G)
    nA = Dr.J.shape[1]
    lam, J, E, N = lam_group(Dr, G)
    z_shift, sd_shift = _zs(lam[0], lam[1:])
    out = {"members": G, "n": n, "lam": float(lam[0]) if np.isfinite(lam[0]) else np.nan, "joins": float(J[0]),
           "expected": float(E[0]), "n_ctx": float(N[0]), "lam_rot_mu": float(np.nanmean(lam[1:])),
           "z_shift": z_shift}
    act = Dr.act
    pool = [a for a in range(nA) if a not in set(G) and act[a] > 0]
    k = min(n - 1, len(pool))
    out.update({"k": k, "testable": False, "z_out": np.nan, "lam_in_k": np.nan, "lam_out_k": np.nan,
                "specificity": np.nan})
    if k >= 1 and n >= 2:
        # in: k random co-members per member (mean over n_in draws)
        lin = []
        for _ in range(n_in):
            Jt = Et = 0.0
            for j in G:
                q = rng.choice([b for b in G if b != j], k, replace=False)
                Jt += Dr.J[0, j, q].sum(); Et += Dr.E[0, j, q].sum()
            if Et > 0:
                lin.append(Jt / Et)
        lam_in_k = float(np.mean(lin)) if lin else np.nan
        # out: k activity-matched outsiders per member
        louts = []
        for _ in range(n_draw):
            Jt = Et = 0.0
            ok = True
            for j in G:
                co = [b for b in G if b != j]
                ref = act[rng.choice(co, k, replace=False)].sum()
                hit = None
                for _t in range(20):
                    q = rng.choice(pool, k, replace=False)
                    if 0.5 * ref <= act[q].sum() <= 1.5 * ref:
                        hit = q
                        break
                if hit is None:
                    ok = False
                    break
                Jt += Dr.J[0, j, hit].sum(); Et += Dr.E[0, j, hit].sum()
            if ok and Et > 0:
                louts.append(Jt / Et)
        louts = np.asarray(louts)
        if len(louts) >= min_matched and np.isfinite(lam_in_k):
            sd = max(louts.std(ddof=1), sd_shift if np.isfinite(sd_shift) else 0.0)
            mo = float(louts.mean())
            out.update({"testable": True, "lam_in_k": lam_in_k, "lam_out_k": mo,
                        "z_out": float((lam_in_k - mo) / sd) if sd > 1e-12 else np.nan,
                        "specificity": float(1 - (mo - 1) / (lam_in_k - 1)) if lam_in_k > 1 else np.nan,
                        "n_out": int(len(louts))})
        else:
            out["n_out"] = int(len(louts))
    out["qualifies"] = bool(n >= 2 and out["n_ctx"] >= min_ctx and np.isfinite(out["lam"]) and out["lam"] > 1
                            and np.isfinite(z_shift) and z_shift >= 2 and out["testable"]
                            and np.isfinite(out["z_out"]) and out["z_out"] >= 2
                            and np.isfinite(out["specificity"]) and out["specificity"] >= 0.5)
    return out


def _t_in_cross(Dr: Draws, G, others):
    """Exclusion within the group's pairs (T_in) and between members and the other agents (T_cross), each relative
    to its own rotation mean; D = T_in - T_cross (amendment R2-A2)."""
    G = np.asarray(G, int)
    O = np.asarray(others, int)
    iu = np.triu_indices(len(G), 1)
    sa = Dr.SAME[:, G][:, :, G][:, iu[0], iu[1]].sum(1)
    bo = Dr.BOTH[:, G][:, :, G][:, iu[0], iu[1]].sum(1)
    sx = Dr.SAME[:, G][:, :, O].sum((1, 2)) if len(O) else np.zeros(Dr.SAME.shape[0])
    bx = Dr.BOTH[:, G][:, :, O].sum((1, 2)) if len(O) else np.zeros(Dr.SAME.shape[0])
    with np.errstate(invalid="ignore", divide="ignore"):
        Ci = np.where(bo > 0, sa / bo, np.nan)
        Cx = np.where(bx > 0, sx / bx, np.nan)
    mi = np.nanmean(Ci[1:]) if np.isfinite(Ci[1:]).sum() else np.nan
    mx = np.nanmean(Cx[1:]) if np.isfinite(Cx[1:]).sum() else np.nan
    Ti = 1 - Ci[0] / mi if (np.isfinite(Ci[0]) and np.isfinite(mi) and mi > 0) else np.nan
    Tx = 1 - Cx[0] / mx if (np.isfinite(Cx[0]) and np.isfinite(mx) and mx > 0) else np.nan
    return Ti, Tx, Ci, float(bo[0]), float(bx[0])


def _within_sums(Dr: Draws, g):
    g = np.asarray(g, int)
    iu = np.triu_indices(len(g), 1)
    return (Dr.SAME[:, g][:, :, g][:, iu[0], iu[1]].sum(1), Dr.BOTH[:, g][:, :, g][:, iu[0], iu[1]].sum(1))


def t_rule(Dr: Draws, G, n_part=200, seed=0, min_pairbins=30, min_matched=30, max_groups=60):
    """Territorial candidate test (card R1 T-rule as amended by R2-A2): within-group exclusion T > 0 against
    rotations, and T beats the random-partition reference. A reference draw is a block of random activity-matched
    groups of size k = min(n, outsiders) drawn from the agents outside G (the other blocks of a random partition),
    pooled until its eligible pair-bins match G's (accepted at >= min(G's, 30)); T_ref = 1 - C_obs / mean C_rot on the pooled counts, so the
    reference has the same sampling noise as G and no small-count ratio bias. If random blocks exclude each other as
    much, exclusion is a village property, not a group state. T_cross (members vs the other agents) is reported."""
    rng = np.random.default_rng(seed + 17)
    G = sorted(int(a) for a in G)
    n = len(G)
    act = Dr.act
    allag = [a for a in range(Dr.SAME.shape[1]) if act[a] > 0]
    oth = [a for a in allag if a not in set(G)]
    Ti, Tx, Ci, bo, bx = _t_in_cross(Dr, G, oth)
    z_rot, _ = _zs(Ci[0], Ci[1:])                    # negative = fewer co-occupied bins than rotation
    out = {"members": G, "n": n, "T": float(Ti) if np.isfinite(Ti) else np.nan,
           "T_cross": float(Tx) if np.isfinite(Tx) else np.nan,
           "C_obs": float(Ci[0]) if np.isfinite(Ci[0]) else np.nan, "pairbins": bo, "pairbins_cross": bx,
           "z_rot": float(-z_rot) if np.isfinite(z_rot) else np.nan}
    k = min(n, len(oth))
    out["k"] = k
    Ts = []
    if n >= 2 and k >= 2 and bo > 0 and np.isfinite(Ti):
        ref = act[G].sum() * k / n
        for _ in range(n_part):
            sa = np.zeros(Dr.SAME.shape[0])
            sb = np.zeros(Dr.SAME.shape[0])
            ng = 0
            for _t in range(max_groups * 4):
                g = rng.choice(oth, k, replace=False)
                if not (0.5 * ref <= act[g].sum() <= 1.5 * ref):
                    continue
                a_, b_ = _within_sums(Dr, g)
                sa += a_
                sb += b_
                ng += 1
                if sb[0] >= bo or ng >= max_groups:
                    break
            if sb[0] >= min(bo, 30) and sb[0] > 0:
                with np.errstate(invalid="ignore", divide="ignore"):
                    Cr = np.where(sb > 0, sa / sb, np.nan)
                mr = np.nanmean(Cr[1:])
                if np.isfinite(mr) and mr > 0:
                    Ts.append(1 - Cr[0] / mr)
    Ts = np.asarray(Ts)
    out["n_part"] = int(len(Ts))
    if len(Ts) >= min_matched:
        sd = Ts.std(ddof=1)
        out["T_part_mu"] = float(Ts.mean())
        out["z_part"] = float((Ti - Ts.mean()) / sd) if sd > 1e-12 else np.nan
    else:
        out["T_part_mu"] = np.nan
        out["z_part"] = np.nan
    out["qualifies"] = bool(n >= 2 and np.isfinite(Ti) and Ti > 0 and out["pairbins"] >= min_pairbins
                            and np.isfinite(out["z_rot"]) and out["z_rot"] >= 2
                            and np.isfinite(out["z_part"]) and out["z_part"] >= 2)
    return out


def village(Dr: Draws):
    """Village-level Lambda_V and T_V against rotations (all agents with commits)."""
    G = [a for a in range(Dr.J.shape[1]) if Dr.act[a] > 0]
    lam, J, E, N = lam_group(Dr, G)
    zl, _ = _zs(lam[0], lam[1:])
    C, sa, bo = excl_group(Dr, G)
    mu = np.nanmean(C[1:])
    zc, _ = _zs(C[0], C[1:])
    return {"n": len(G), "lam_V": float(lam[0]), "lam_V_rot": float(np.nanmean(lam[1:])),
            "lam_V_ratio": float(lam[0] / np.nanmean(lam[1:])) if np.nanmean(lam[1:]) > 0 else np.nan,
            "z_lam": zl, "joins": float(J[0]), "expected": float(E[0]), "n_ctx": float(N[0]),
            "T_V": float(1 - C[0] / mu) if mu > 0 else np.nan, "C_obs": float(C[0]), "C_rot": float(mu),
            "z_T": float(-zc) if np.isfinite(zc) else np.nan, "pairbins": float(bo[0])}


# ============================================================================ static partition
def static_partition(P: Panel, n_draw=200, seed=0, min_act=5):
    """Own-artifact share (commit-weighted share on artifacts where the agent holds >= 50% of the working bins) vs a
    random partition at matched activity: each agent keeps its number of working bins and number of distinct
    artifacts and its sorted share profile; which artifacts it holds is drawn by pooled popularity without
    replacement. Also exclusivity E = share of working bins on single-agent artifacts (the file-level R2a statistic)."""
    rng = np.random.default_rng(seed)
    W = np.zeros((P.nA, P.K))
    a_, b_ = np.nonzero(P.S >= 0)
    np.add.at(W, (a_, P.S[a_, b_]), 1)
    keep = W.sum(1) >= min_act
    W = W[keep]
    if W.shape[0] < 2:
        return {"ok": False}

    def stats(M):
        tot = M.sum(0)
        own = (M >= 0.5 * np.maximum(tot, 1e-9)[None, :]) & (M > 0)
        own_share = float((M * own).sum() / M.sum())
        single = ((M > 0).sum(0) == 1)
        excl = float(M[:, single].sum() / M.sum())
        return own_share, excl
    o0, e0 = stats(W)
    pop = W.sum(0) / W.sum()
    profiles = [np.sort(r[r > 0])[::-1] for r in W]
    on, en = [], []
    for _ in range(n_draw):
        M = np.zeros_like(W)
        for i, pr in enumerate(profiles):
            ks = rng.choice(P.K, len(pr), replace=False, p=pop) if len(pr) <= (pop > 0).sum() else \
                rng.choice(P.K, len(pr), replace=True, p=pop)
            np.add.at(M[i], ks, pr)
        o, e = stats(M)
        on.append(o)
        en.append(e)
    on, en = np.array(on), np.array(en)
    return {"ok": True, "n_agents": int(W.shape[0]), "own_share": o0, "own_null": float(on.mean()),
            "z_own": float((o0 - on.mean()) / on.std(ddof=1)) if on.std(ddof=1) > 0 else np.nan,
            "excl": e0, "excl_null": float(en.mean()),
            "z_excl": float((e0 - en.mean()) / en.std(ddof=1)) if en.std(ddof=1) > 0 else np.nan}


def jsonable(o):
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, (np.floating, float)):
        return None if not np.isfinite(o) else float(o)
    if isinstance(o, np.ndarray):
        return jsonable(o.tolist())
    if isinstance(o, np.bool_):
        return bool(o)
    return o
