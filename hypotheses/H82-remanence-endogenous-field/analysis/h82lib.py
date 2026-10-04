"""H82 library: remanence regression at goal boundaries (no text; holdout dropped by scheme/build.py).

v_{i,d} (unit, 32-d) = sum_k alpha_k X_ex,k + beta p_i^{(-P,-X)} + gamma e_X^{(-i)} + delta k_{P-1} + eps
X_ex: kickoff k_P, goal text g_P, the agent's room kickoff (only when P has >= 2 room kickoffs), the day's human-message
centroid. X = P-1 (remanence), a placebo period Q (|Q-P| >= 2), or P+1 (future placebo). The prior leaves out P and X.
Fits stack the 32 coordinates of all agents present on day d (no intercept).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data/processed/H82-remanence-endogenous-field"
MIN_PRIOR_DAYS = 3
NDAYS = 5


def unit(x):
    x = np.asarray(x, dtype=np.float64)
    n = np.linalg.norm(x, axis=-1, keepdims=True)
    n[n == 0] = 1.0
    return x / n


class Data:
    def __init__(self, model: str, variant: str = "style_resid", drop_agents=frozenset(), use_human: bool = True):
        ad = pl.read_parquet(OUT / "agentdays.parquet").with_row_index("row")
        X = np.load(OUT / f"vecs_{model}_{variant}.npy").astype(np.float64)
        ad = ad.filter(~pl.col("agent").is_in(list(drop_agents)))
        self.X = X[ad["row"].to_numpy()]
        self.agent = ad["agent"].to_numpy().astype(int)
        self.goal = ad["goal_no"].to_numpy().astype(int)
        self.date = np.array(ad["pt_date"].to_list())
        self.regime = np.array(ad["regime"].to_list())
        self.room = ad["room"].fill_null(-1).to_numpy().astype(int)
        self.bd = pl.read_parquet(OUT / "boundaries.parquet")
        V = np.load(OUT / f"dirs_{model}.npz")["V"].astype(np.float64)
        idx = json.loads((OUT / f"dirs_index_{model}.json").read_text())
        self.goal_dir = {}
        self.room_dir = {}
        self.day_human = {}
        self.agent_goal = {}
        for e in idx:
            if e["level"] == "goal" and e["kind"] in ("kickoff", "goal", "human"):
                self.goal_dir[(e["goal_no"], e["regime"], e["kind"])] = V[e["i"]]
            elif e["level"] == "goal" and e["kind"] == "kickoff_room":
                self.room_dir.setdefault((e["goal_no"], e["regime"]), {})[e["room"]] = V[e["i"]]
            elif e["level"] == "goal" and e["kind"] == "agent_goal":
                self.agent_goal.setdefault((e["agent"], e["regime"]), []).append(V[e["i"]])
            elif e["level"] == "day" and e["kind"] == "human" and use_human:
                self.day_human[(e["pt_date"], e["regime"])] = V[e["i"]]
        self.use_human = use_human
        self._cent = {}

    # -------------------------------------------------------------------------------------- fields
    def centroid(self, goal: int, regime: str, leave_agent: int | None = None):
        key = (goal, regime, leave_agent)
        if key not in self._cent:
            m = (self.goal == goal) & (self.regime == regime)
            if leave_agent is not None:
                m &= self.agent != leave_agent
            self._cent[key] = unit(self.X[m].mean(0)) if m.sum() >= 3 else None
        return self._cent[key]

    def prior(self, agent: int, regime: str, leave_goals: set):
        m = (self.agent == agent) & (self.regime == regime) & ~np.isin(self.goal, list(leave_goals))
        return unit(self.X[m].mean(0)) if m.sum() >= MIN_PRIOR_DAYS else None

    def goals_in_regime(self, regime: str):
        return sorted(set(self.goal[self.regime == regime].tolist()))

    # -------------------------------------------------------------------------------------- design
    def day_rows(self, P: int, regime: str, day: str):
        return np.flatnonzero((self.goal == P) & (self.regime == regime) & (self.date == day))

    def design(self, P, prev, regime, day, X_goal, newcomer_split=False, extra_prior_leave=(), mates=False):
        """Returns y (32N), Z (32N x k), names, agents, is_new; X_goal = the goal whose centroid is the endogenous
        regressor (prev for remanence; a placebo or the next goal otherwise)."""
        rows = self.day_rows(P, regime, day)
        kP = self.goal_dir.get((P, regime, "kickoff")); gP = self.goal_dir.get((P, regime, "goal"))
        kprev = self.goal_dir.get((prev, regime, "kickoff"))
        hum = self.day_human.get((day, regime)) if self.use_human else None
        rooms = self.room_dir.get((P, regime), {})
        multi_room = len(rooms) >= 2
        prev_agents = set(self.agent[(self.goal == prev) & (self.regime == regime)].tolist())
        ys, Zs, agents, isnew = [], [], [], []
        for r in rows:
            a = self.agent[r]
            pr = self.prior(a, regime, {P, X_goal, *extra_prior_leave})
            e = self.centroid(X_goal, regime, leave_agent=a)
            if pr is None or e is None:
                continue
            cols = [kP if kP is not None else np.zeros(32), gP if gP is not None else np.zeros(32),
                    kprev if kprev is not None else np.zeros(32)]
            cols.append(hum if hum is not None else np.zeros(32))
            cols.append(rooms.get(self.room[r], np.zeros(32)) if multi_room else np.zeros(32))
            ag = self.agent_goal.get((a, regime))
            cols.append(unit(np.mean(ag, axis=0)) if (ag and P == 51) else np.zeros(32))
            cols.append(pr)
            if mates:  # R4 variant: mean prior of the other agents present on the day
                others = [self.prior(b, regime, {P, X_goal, *extra_prior_leave}) for b in self.agent[rows] if b != a]
                others = [o for o in others if o is not None]
                cols.append(unit(np.mean(others, axis=0)) if others else np.zeros(32))
            new = a not in prev_agents
            if newcomer_split:
                cols += [e * (not new), e * new]
            else:
                cols.append(e)
            ys.append(self.X[r]); Zs.append(np.stack(cols, 1)); agents.append(a); isnew.append(new)
        names = ["kP", "gP", "kprev", "human", "room", "agoal", "prior"] + (["mates"] if mates else []) + \
            (["e_vet", "e_new"] if newcomer_split else ["e"])
        if not ys:
            return None
        return np.array(ys), np.array(Zs), names, np.array(agents), np.array(isnew)


def fit(Y, Z, idx=None):
    """OLS of stacked coordinates; Y (N x 32), Z (N x 32 x k). Columns that are all zero are dropped (coef NaN)."""
    if idx is not None:
        Y, Z = Y[idx], Z[idx]
    y = Y.reshape(-1); Zf = Z.transpose(0, 1, 2).reshape(-1, Z.shape[2])
    keep = np.abs(Zf).sum(0) > 0
    beta = np.full(Z.shape[2], np.nan)
    if keep.sum() == 0 or len(y) <= keep.sum():
        return beta
    b, *_ = np.linalg.lstsq(Zf[:, keep], y, rcond=None)
    beta[keep] = b
    return beta


def re_meta(est: np.ndarray, se: np.ndarray):
    """DerSimonian-Laird random-effects mean; returns mu, se, lo, hi, tau2, k."""
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    e, s = est[ok], se[ok]
    k = len(e)
    if k == 0:
        return dict(mu=np.nan, se=np.nan, lo=np.nan, hi=np.nan, tau2=np.nan, k=0)
    w = 1 / s ** 2
    mu_f = (w * e).sum() / w.sum()
    Q = (w * (e - mu_f) ** 2).sum()
    c = w.sum() - (w ** 2).sum() / w.sum()
    tau2 = max(0.0, (Q - (k - 1)) / c) if k > 1 and c > 0 else 0.0
    wr = 1 / (s ** 2 + tau2)
    mu = (wr * e).sum() / wr.sum(); se_mu = np.sqrt(1 / wr.sum())
    return dict(mu=float(mu), se=float(se_mu), lo=float(mu - 1.96 * se_mu), hi=float(mu + 1.96 * se_mu),
                tau2=float(tau2), k=int(k))


def boundary_designs(D: Data, brow: dict, days=NDAYS, newcomer_split=False, extra_prior_leave=(), mates=False):
    """Precomputed designs for one boundary: list over days of {key: design}; keys prev, next, q<Q>."""
    P, prev, nxt, regime = brow["P"], brow["prev"], brow["next"], brow["regime"]
    goals = D.goals_in_regime(regime)
    placebos = [q for q in goals if abs(q - P) >= 2 and q != prev]
    out = []
    for day in brow["days_P"][:days]:
        des = {"prev": D.design(P, prev, regime, day, prev, newcomer_split, extra_prior_leave, mates)}
        if des["prev"] is None:
            out.append(None)
            continue
        if nxt is not None:
            des["next"] = D.design(P, prev, regime, day, nxt, newcomer_split, extra_prior_leave, mates)
        for q in placebos:
            des[f"q{q}"] = D.design(P, prev, regime, day, q, newcomer_split, extra_prior_leave, mates)
        out.append((day, des, placebos))
    return out


def boundary_stats(brow: dict, designs, n_boot=300, rng=None, Ysub=None):
    """Per day d of P: gamma[prev], gamma[next], median gamma[placebos], Delta gamma; agent-cluster bootstrap (the same
    agent draw for every regressor set). Ysub(P, day, agent_array, Z, names) -> synthetic Y rows (deterministic per
    agent within a replicate)."""
    P, prev, regime = brow["P"], brow["prev"], brow["regime"]
    out = []
    for di, item in enumerate(designs):
        if item is None:
            continue
        day, des, placebos = item
        Y0, Z0, names, agents, isnew = des["prev"]
        ecols = [k for k, n in enumerate(names) if n.startswith("e")]
        k = len(ecols)
        Ys = {}
        for key, d in des.items():
            if d is None:
                continue
            Yk, Zk, _, ag, _ = d
            Ys[key] = Ysub(P, day, ag, Zk, names) if Ysub is not None else Yk
        pos = {key: {a: j for j, a in enumerate(d[3])} for key, d in des.items() if d is not None}

        def coefs(key, idx_agents):
            d = des.get(key)
            if d is None:
                return np.full(k, np.nan)
            sel = [pos[key][a] for a in idx_agents if a in pos[key]]
            if len(sel) < 2:
                return np.full(k, np.nan)
            return fit(Ys[key], d[1], np.array(sel))[ecols]

        def stats(idx_agents):
            g_prev = coefs("prev", idx_agents)
            g_next = coefs("next", idx_agents)
            g_pl = np.array([coefs(f"q{q}", idx_agents) for q in placebos]) if placebos else np.full((1, k), np.nan)
            med = np.nanmedian(g_pl, axis=0) if np.isfinite(g_pl).any() else np.full(k, np.nan)
            return g_prev, g_next, med

        agset = list(agents)
        g_prev, g_next, med = stats(agset)
        boots = []
        if n_boot and len(agset) >= 3:
            for _ in range(n_boot):
                boots.append(np.concatenate(stats(list(rng.choice(agset, len(agset), replace=True)))))
        boots = np.array(boots) if boots else np.full((1, 3 * k), np.nan)
        for j, nm in enumerate([names[c] for c in ecols]):
            bdg = boots[:, j] - boots[:, 2 * k + j]; basym = boots[:, j] - boots[:, k + j]
            okb = np.isfinite(bdg).sum() > 10; oka = np.isfinite(basym).sum() > 10
            n_grp = int((~isnew).sum()) if nm == "e_vet" else int(isnew.sum()) if nm == "e_new" else len(agset)
            out.append({"P": P, "prev": prev, "regime": regime, "d": di + 1, "day": day, "term": nm,
                        "n_agents": len(agset), "n_group": n_grp, "gamma_prev": float(g_prev[j]),
                        "gamma_next": float(g_next[j]), "gamma_placebo_med": float(med[j]), "n_placebo": len(placebos),
                        "dgamma": float(g_prev[j] - med[j]),
                        "dgamma_se": float(np.nanstd(bdg)) if okb else np.nan,
                        "dgamma_lo": float(np.nanquantile(bdg, 0.025)) if okb else np.nan,
                        "dgamma_hi": float(np.nanquantile(bdg, 0.975)) if okb else np.nan,
                        "asym": float(g_prev[j] - g_next[j]), "asym_se": float(np.nanstd(basym)) if oka else np.nan,
                        "gamma_prev_se": float(np.nanstd(boots[:, j])) if np.isfinite(boots[:, j]).sum() > 10 else np.nan})
    return out
