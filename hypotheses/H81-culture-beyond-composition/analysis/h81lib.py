"""H81 library: composition null, culture residuals and the slow-mode statistics (no text; holdout already dropped by
scheme/build.py). Used by synthetic.py, replication.py and natives.py.

Notation (card): v_{i,d} unit agent-day vector; Pi_{G,i} projector removing the exogenous directions of goal G (and
agent i's own #51 goal); mu_i^{(-G)} leave-goal-out personal vector (mean of Pi-projected vectors of i's days in other
goals of the regime); r_{i,b} = Pi_{G,i}(vbar_{i,b} - mu_i^{(-G)}); u_b = mean_i r_{i,b}.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data/processed/H81-culture-beyond-composition"
GEMINI_25 = 6
NEAR, FAR = 14.0, 42.0
MIN_OTHER_DAYS = 3
METHOD = "fe"  # Amendment A1 (2026-10-04, after the synthetic, before real statistics); "mean" = literal HH null
CENTER = True  # Amendment A1: block culture vectors centered over the regime's blocks (removes the FE constant)
T0 = np.datetime64("2025-01-01")


def day_num(s) -> np.ndarray:
    return (np.array(s, dtype="datetime64[D]") - T0).astype(np.float64)


# ------------------------------------------------------------------------------------------------- loading
def load(model: str, variant: str, regime: str, drop_agents: frozenset = frozenset(), weights: bool = False):
    ad = pl.read_parquet(OUT / "agentdays.parquet").with_row_index("row")
    X = np.load(OUT / f"vecs_{model}_{variant}.npy").astype(np.float64)
    ad = ad.filter((pl.col("regime") == regime) & ~pl.col("agent").is_in(list(drop_agents)))
    rows = ad["row"].to_numpy()
    blocks = pl.read_parquet(OUT / "blocks.parquet").filter(pl.col("regime") == regime)
    return ad, X[rows], blocks


def projectors(model: str, regime: str, ad: pl.DataFrame, use_human: bool = True) -> dict:
    """(goal_no, agent) -> 32x32 projector removing the goal's exogenous directions (agent key -1 = no agent goal)."""
    V = np.load(OUT / f"dirs_{model}.npz")["V"].astype(np.float64)
    idx = json.loads((OUT / f"dirs_index_{model}.json").read_text())
    P = {}
    goals = sorted(set(ad["goal_no"].to_list()))
    agents_by_goal = {g: sorted(set(ad.filter(pl.col("goal_no") == g)["agent"].to_list())) for g in goals}
    for g in goals:
        base = [e["i"] for e in idx if e["level"] == "goal" and e["goal_no"] == g and e["regime"] == regime
                and e["kind"] in ("kickoff", "goal", "kickoff_room") ]
        if use_human:
            base += [e["i"] for e in idx if e["level"] == "goal" and e["goal_no"] == g and e["regime"] == regime
                     and e["kind"] == "human"]
        P[(g, -1)] = _proj(V[base])
        for a in agents_by_goal[g]:
            ag = [e["i"] for e in idx if e["level"] == "goal" and e["goal_no"] == g and e["regime"] == regime
                  and e["kind"] == "agent_goal" and e["agent"] == a]
            P[(g, a)] = _proj(V[base + ag]) if ag else P[(g, -1)]
    return P


def _proj(D: np.ndarray) -> np.ndarray:
    if len(D) == 0:
        return np.eye(32)
    Q, R = np.linalg.qr(D.T)
    keep = np.abs(np.diag(R)) > 1e-8
    Q = Q[:, keep]
    return np.eye(32) - Q @ Q.T


def goal_kickoff(model: str, regime: str, goals) -> dict:
    V = np.load(OUT / f"dirs_{model}.npz")["V"].astype(np.float64)
    idx = json.loads((OUT / f"dirs_index_{model}.json").read_text())
    out = {}
    for g in goals:
        k = [e["i"] for e in idx if e["level"] == "goal" and e["goal_no"] == g and e["regime"] == regime
             and e["kind"] == "kickoff"]
        if not k:
            k = [e["i"] for e in idx if e["level"] == "goal" and e["goal_no"] == g and e["regime"] == regime
                 and e["kind"] == "goal"]
        out[g] = V[k[0]] if k else np.zeros(32)
    return out


# ------------------------------------------------------------------------------------------------- panel
class Panel:
    """Index arrays of one regime's eligible agent-days."""

    def __init__(self, ad: pl.DataFrame, blocks: pl.DataFrame, P: dict):
        self.agent = ad["agent"].to_numpy().astype(int)
        self.goal = ad["goal_no"].to_numpy().astype(int)
        self.day = day_num(ad["pt_date"].to_list())
        self.date = ad["pt_date"].to_numpy()
        bl = blocks["block"].to_list()
        bid = {b: k for k, b in enumerate(bl)}
        self.block = np.array([bid[b] for b in ad["block"].to_list()])
        self.nb = len(bl)
        self.block_goal = blocks["goal_no"].to_numpy().astype(int)
        self.block_mid = blocks["mid_day"].to_numpy()
        self.block_name = bl
        self.n_stat = ad["n_stat"].to_numpy().astype(float)
        self.P = P
        self.Pi = np.stack([P.get((g, a), P[(g, -1)]) for g, a in zip(self.goal, self.agent)])


def project(pan: Panel, X: np.ndarray) -> np.ndarray:
    return np.einsum("nij,nj->ni", pan.Pi, X)


def personal_vectors(pan: Panel, Xp: np.ndarray, weights: np.ndarray | None = None, method: str | None = None):
    """mu[(agent, goal)]: the agent's personal vector estimated from its days in OTHER goals of the regime
    (>= MIN_OTHER_DAYS). method 'fe' (Amendment A1, primary): two-way fixed effects (agent + goal) fitted on agent-goal
    means without goal G, so other goals' village states are not folded into the personal vector; 'mean' (the HH's
    literal null, pre-amendment): plain mean of the agent's projected vectors in other goals."""
    method = method or METHOD
    w = np.ones(len(Xp)) if weights is None else weights
    agents = np.unique(pan.agent); goals = np.unique(pan.goal)
    ai = {a: k for k, a in enumerate(agents)}; gi = {g: k for k, g in enumerate(goals)}
    Y = np.zeros((len(agents), len(goals), Xp.shape[1])); Wt = np.zeros((len(agents), len(goals)))
    np.add.at(Y, (np.vectorize(ai.get)(pan.agent), np.vectorize(gi.get)(pan.goal)), Xp * w[:, None])
    np.add.at(Wt, (np.vectorize(ai.get)(pan.agent), np.vectorize(gi.get)(pan.goal)), w)
    cnt = np.zeros_like(Wt); np.add.at(cnt, (np.vectorize(ai.get)(pan.agent), np.vectorize(gi.get)(pan.goal)), 1)
    mu = {}
    for g in goals:
        keep = np.ones(len(goals), bool); keep[gi[g]] = False
        if method == "fe":
            A_hat = _twoway(Y[:, keep], Wt[:, keep])
        for a in agents:
            if cnt[ai[a], gi[g]] == 0 or cnt[ai[a], keep].sum() < MIN_OTHER_DAYS:
                continue
            if method == "fe":
                mu[(a, g)] = A_hat[ai[a]]
            else:
                mu[(a, g)] = Y[ai[a], keep].sum(0) / Wt[ai[a], keep].sum()
    return mu


def _twoway(Ysum: np.ndarray, W: np.ndarray, iters: int = 200) -> np.ndarray:
    """Weighted two-way FE on cell sums: minimize sum W_ig |ybar_ig - a_i - c_g|^2 with sum_g (W_.g) c_g = 0.
    Returns a (agents x d); agents with no cells get zeros."""
    Wa = W.sum(1); Wg = W.sum(0)
    Ybar = np.divide(Ysum, W[..., None], out=np.zeros_like(Ysum), where=W[..., None] > 0)
    a = np.divide(Ysum.sum(1), Wa[:, None], out=np.zeros((len(Wa), Ysum.shape[2])), where=Wa[:, None] > 0)
    c = np.zeros((len(Wg), Ysum.shape[2]))
    for _ in range(iters):
        c_new = np.divide((W[..., None] * (Ybar - a[:, None, :])).sum(0), Wg[:, None], out=np.zeros_like(c),
                          where=Wg[:, None] > 0)
        c_new -= (Wg[:, None] * c_new).sum(0) / Wg.sum()
        a_new = np.divide((W[..., None] * (Ybar - c_new[None, :, :])).sum(1), Wa[:, None], out=np.zeros_like(a),
                          where=Wa[:, None] > 0)
        if np.abs(a_new - a).max() < 1e-9 and np.abs(c_new - c).max() < 1e-9:
            a, c = a_new, c_new
            break
        a, c = a_new, c_new
    return a


def agent_block_residuals(pan: Panel, X: np.ndarray, weights: np.ndarray | None = None):
    """Rows (agent, block) with r_{i,b}; returns agents, blocks, R (n x 32)."""
    Xp = project(pan, X)
    mu = personal_vectors(pan, Xp, weights)
    w = np.ones(len(Xp)) if weights is None else weights
    keys = {}
    for k in range(len(Xp)):
        if (pan.agent[k], pan.goal[k]) not in mu:
            continue
        keys.setdefault((pan.agent[k], pan.block[k]), []).append(k)
    A, B, R = [], [], []
    for (a, b), ks in keys.items():
        ks = np.array(ks)
        vbar = (Xp[ks] * w[ks, None]).sum(0) / w[ks].sum()
        g = pan.goal[ks[0]]
        Pi = pan.P.get((g, a), pan.P[(g, -1)])
        A.append(a); B.append(b); R.append(Pi @ (vbar - mu[(a, g)]))
    return np.array(A), np.array(B), np.array(R)


def day_residuals(pan: Panel, X: np.ndarray):
    """Per agent-day residual r_{i,d} = Pi(v - mu^{(-G)}); rows with no personal vector get NaN."""
    Xp = project(pan, X)
    mu = personal_vectors(pan, Xp)
    R = np.full_like(Xp, np.nan)
    for k in range(len(Xp)):
        key = (pan.agent[k], pan.goal[k])
        if key in mu:
            R[k] = pan.Pi[k] @ (Xp[k] - mu[key])
    return R


# ------------------------------------------------------------------------------------------------- O1
def kappa_blocks(A, B, R, nb, rng=None, n_null=0):
    """Mean pairwise residual alignment per block, plus optional sign-flip null draws."""
    out = np.full(nb, np.nan); nulls = np.full((nb, n_null), np.nan); ns = np.zeros(nb, int)
    for b in range(nb):
        m = B == b
        if m.sum() < 3:
            continue
        Rb = R[m]; G = Rb @ Rb.T; N = len(Rb); tr = np.trace(G)
        ns[b] = N
        out[b] = (G.sum() - tr) / ((N - 1) * tr)
        if n_null:
            s = rng.choice([-1.0, 1.0], size=(n_null, N))
            q = np.einsum("ki,ij,kj->k", s, G, s)
            nulls[b] = (q - tr) / ((N - 1) * tr)
    return out, nulls, ns


# ------------------------------------------------------------------------------------------------- O2/O3
def block_vectors(A, B, R, nb, block_goal=None, subset_size: int | None = None, rng=None):
    """u_b = mean of the members' residuals (>= 3 members, or a random subset of size subset_size). With CENTER, the
    goal-equal-weight mean of the block vectors is subtracted (Amendment A1): each goal counts once, so a long goal
    (#51: nine weekly blocks) cannot set the center. Returns U (centered), members, center."""
    U = np.full((nb, R.shape[1]), np.nan); members = []
    for b in range(nb):
        m = np.flatnonzero(B == b)
        if subset_size and len(m) >= subset_size:
            m = rng.choice(m, subset_size, replace=False)
        members.append(set(A[m].tolist()))
        if len(m) >= (subset_size or 3):
            U[b] = R[m].mean(0)
    cen = np.zeros(R.shape[1])
    if CENTER:
        ok = ~np.isnan(U[:, 0])
        gm = [U[ok & (block_goal == g)].mean(0) for g in np.unique(block_goal[ok])]
        cen = np.mean(gm, axis=0)
        U[ok] -= cen
    return U, members, cen


def _cos(a, b):
    na, nb_ = np.linalg.norm(a), np.linalg.norm(b)
    return float(a @ b / (na * nb_)) if na > 0 and nb_ > 0 else np.nan


def pair_table(pan: Panel, A, B, R, kick: dict, subset_size=None, rng=None, disjoint=True):
    """One row per cross-goal block pair: b, c, dt, overlap J, goal similarity, s, s_perp, weight. Weights make every
    goal pair count once (Amendment A1): w = 1 / (n_pairs of that goal pair)."""
    U, members, cen = block_vectors(A, B, R, pan.nb, pan.block_goal, subset_size, rng)
    rows = []
    for b in range(pan.nb):
        for c in range(b + 1, pan.nb):
            if pan.block_goal[b] == pan.block_goal[c] or np.isnan(U[b, 0]) or np.isnan(U[c, 0]):
                continue
            mb, mc = members[b], members[c]
            J = len(mb & mc) / len(mb | mc)
            s = _cos(U[b], U[c])
            sd = np.nan
            if disjoint:
                # Amendment A2: one-sided turnover-disjoint similarity: the agents of one block that are absent from
                # the other block, against the other block (no agent on both sides); mean of both directions
                vals = []
                ob = [k for k in np.flatnonzero(B == b) if A[k] not in mc]
                oc = [k for k in np.flatnonzero(B == c) if A[k] not in mb]
                if len(oc) >= 2:
                    vals.append(_cos(U[b], R[oc].mean(0) - cen))
                if len(ob) >= 2:
                    vals.append(_cos(R[ob].mean(0) - cen, U[c]))
                if vals:
                    sd = float(np.mean(vals))
            gs = _cos(kick[pan.block_goal[b]], kick[pan.block_goal[c]])
            rows.append((b, c, abs(pan.block_mid[b] - pan.block_mid[c]), J, gs, s, sd,
                         pan.block_goal[b] * 1000 + pan.block_goal[c]))
    T = np.array(rows, dtype=float).reshape(-1, 8)
    if len(T):
        _, inv, cnt = np.unique(T[:, 7], return_inverse=True, return_counts=True)
        T[:, 7] = 1.0 / cnt[inv]
    return T


def _wmean(x, w):
    return float((x * w).sum() / w.sum()) if w.sum() > 0 else np.nan


def slow_stats(T: np.ndarray) -> dict:
    """D_near (raw), adjusted D_near (WLS with goal similarity and overlap), and far-epoch similarity, for s and the
    turnover-disjoint s_perp. Goal-pair weights (Amendment A1)."""
    out = {}
    if len(T) == 0:
        return {k + n: np.nan for k in ("D_near", "D_adj", "D_adjg", "far90") for n in ("", "_perp")}
    dt_, J, gs, w = T[:, 2], T[:, 3], T[:, 4], T[:, 7]
    for name, col in (("", 5), ("_perp", 6)):
        s = T[:, col]; ok = ~np.isnan(s)
        near = ok & (dt_ <= NEAR); far = ok & (dt_ >= FAR)
        out["D_near" + name] = _wmean(s[near], w[near]) - _wmean(s[far], w[far]) if near.any() and far.any() else np.nan
        mid = (dt_ > NEAR) & (dt_ < FAR)
        Xd = np.column_stack([np.ones(ok.sum()), (dt_ <= NEAR)[ok], mid[ok], gs[ok], J[ok]])
        if ok.sum() > 8 and near.any() and far.any():
            sw = np.sqrt(w[ok])
            beta, *_ = np.linalg.lstsq(Xd * sw[:, None], s[ok] * sw, rcond=None)
            out["D_adj" + name] = float(beta[1])
            Xg = Xd[:, :4]  # Amendment A3: goal similarity only (overlap J is collinear with lag; S0 carries overlap)
            beta, *_ = np.linalg.lstsq(Xg * sw[:, None], s[ok] * sw, rcond=None)
            out["D_adjg" + name] = float(beta[1])
        else:
            out["D_adj" + name] = np.nan
            out["D_adjg" + name] = np.nan
        f90 = ok & (dt_ >= 90)
        out["far90" + name] = _wmean(s[f90], w[f90]) if f90.any() else np.nan
    return out


def profile(T: np.ndarray, col=5, edges=(0, 14, 28, 56, 112, 1e9)):
    out = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (T[:, 2] > lo - (1e-9 if lo == 0 else 0)) & (T[:, 2] <= hi) & ~np.isnan(T[:, col])
        out.append((lo, hi, _wmean(T[m, col], T[m, 7]) if m.any() else np.nan, int(m.sum())))
    return out


def permute_time(pan: Panel, A, B, R, kick, rng, n=500):
    """Liberal null: goals keep their block vectors; goal time positions (mid-days) are permuted within regime."""
    T = pair_table(pan, A, B, R, kick, disjoint=False)
    goals = np.unique(pan.block_goal)
    gmid = {g: pan.block_mid[pan.block_goal == g].mean() for g in goals}
    res = []
    for _ in range(n):
        perm = dict(zip(goals, rng.permutation(goals)))
        T2 = T.copy()
        shift = {b: gmid[perm[pan.block_goal[b]]] - gmid[pan.block_goal[b]] for b in range(pan.nb)}
        T2[:, 2] = np.abs(np.array([pan.block_mid[int(b)] + shift[int(b)] for b in T[:, 0]])
                          - np.array([pan.block_mid[int(c)] + shift[int(c)] for c in T[:, 1]]))
        res.append(slow_stats(T2)["D_adj"])
    return np.array(res)


# ------------------------------------------------------------------------------------------------- O4
def day_jumps(pan: Panel, Rd: np.ndarray, roster_dates: set):
    """Within-goal consecutive eligible-day boundaries: scaled jump of the day residual, all agents and stayers."""
    days = np.unique(pan.day)
    rows = []
    for d0, d1 in zip(days[:-1], days[1:]):
        m0 = (pan.day == d0) & ~np.isnan(Rd[:, 0]); m1 = (pan.day == d1) & ~np.isnan(Rd[:, 0])
        if m0.sum() < 3 or m1.sum() < 3:
            continue
        g0, g1 = set(pan.goal[m0]), set(pan.goal[m1])
        if g0 != g1 or len(g0) != 1:
            continue
        R0, R1 = Rd[m0], Rd[m1]
        f0 = (R0 ** 2).sum() / len(R0) ** 2; f1 = (R1 ** 2).sum() / len(R1) ** 2
        J = np.linalg.norm(R1.mean(0) - R0.mean(0)) / np.sqrt(f0 + f1)
        a0 = dict(zip(pan.agent[m0], R0)); a1 = dict(zip(pan.agent[m1], R1))
        st = sorted(set(a0) & set(a1))
        Js = np.nan
        if len(st) >= 3:
            Dl = np.array([a1[a] - a0[a] for a in st])
            Js = np.linalg.norm(Dl.mean(0)) / np.sqrt((Dl ** 2).sum() / len(Dl) ** 2)
        ev = any(d0 < x <= d1 for x in roster_dates)
        rows.append((d0, d1, list(g0)[0], ev, J, Js, m1.sum()))
    return rows


def roster_event_days(drop=(19, 28, 30)) -> set:
    r = pl.read_parquet(ROOT / "data/processed/shared/roster.parquet").filter(~pl.col("agent").is_in(list(drop)))
    ds = [x for x in r["joined"].to_list() + r["left"].to_list() if x]
    return set(day_num(ds).tolist())


# ------------------------------------------------------------------------------------------------- synthetic
def variance_scales(pan: Panel, X: np.ndarray):
    """Empirical covariances of agent, goal, block and agent-day parts of the projected vectors (sampling facts for the
    synthetic; not a test statistic)."""
    Xp = project(pan, X)
    agents = np.unique(pan.agent)
    a_mean = {a: Xp[pan.agent == a].mean(0) for a in agents}
    E1 = Xp - np.stack([a_mean[a] for a in pan.agent])
    goals = np.unique(pan.goal)
    g_mean = {g: E1[pan.goal == g].mean(0) for g in goals}
    E2 = E1 - np.stack([g_mean[g] for g in pan.goal])
    b_mean = {b: E2[pan.block == b].mean(0) for b in np.unique(pan.block)}
    E3 = E2 - np.stack([b_mean[b] for b in pan.block])
    return {"Sa": np.cov(np.stack(list(a_mean.values())).T), "Sg": np.cov(np.stack(list(g_mean.values())).T),
            "Sb": np.cov(np.stack(list(b_mean.values())).T), "E": E3}


def simulate(pan: Panel, sc: dict, rng, share=0.0, tau=28.0, drift=0.0):
    """S0 (share=0, drift=0), S1 (share>0: OU slow mode with correlation time tau over block mid-days), S2 (drift>0:
    individual linear drift along an agent-specific direction over its tenure). Goal and block fields keep the real
    covariance; the slow mode takes `share` of the goal-field covariance. Noise = real agent-day residuals permuted."""
    def mvn(S, n):
        w, V = np.linalg.eigh((S + S.T) / 2); w = np.clip(w, 0, None)
        return rng.standard_normal((n, len(w))) * np.sqrt(w) @ V.T
    agents = np.unique(pan.agent); goals = np.unique(pan.goal)
    a = dict(zip(agents, mvn(sc["Sa"], len(agents))))
    g = dict(zip(goals, mvn(sc["Sg"], len(goals)) * np.sqrt(1 - share)))
    bf = mvn(sc["Sb"], pan.nb)
    X = np.stack([a[x] for x in pan.agent]) + np.stack([g[x] for x in pan.goal]) + bf[pan.block]
    if share > 0:
        order = np.argsort(pan.block_mid); z = mvn(sc["Sg"], pan.nb) * np.sqrt(share)
        u = np.zeros_like(z); prev = None
        for k in order:
            if prev is None:
                u[k] = z[k]
            else:
                rho = np.exp(-(pan.block_mid[k] - pan.block_mid[prev]) / tau)
                u[k] = rho * u[prev] + np.sqrt(1 - rho ** 2) * z[k]
            prev = k
        X = X + u[pan.block]
    if drift > 0:
        dirs = dict(zip(agents, mvn(sc["Sg"], len(agents)) * np.sqrt(drift * 3)))  # var of U(-1,1) = 1/3
        for ag in agents:
            m = pan.agent == ag
            t = pan.day[m]; s = (t - t.min()) / max(t.max() - t.min(), 1) * 2 - 1
            X[m] += s[:, None] * dirs[ag]
    X = X + sc["E"][rng.permutation(len(sc["E"]))]
    return X
