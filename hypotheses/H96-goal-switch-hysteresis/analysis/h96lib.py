"""H96 library: field-orthogonal old-state remanence after a goal switch, its inertia time and the old state's order.

Conventions (card, Observables):
  statement vectors   DQ5 32-d regime-whitened (style-residualized) unit vectors, eligible agents, non-holdout
  units               'pre' (pre day L + P's first-day statements before t0), 'day1' (P's first active day after t0),
                      bins of active hours since t0: BINS
  old state           e_old^(-i) = unit mean of the other agents' agent-day vectors over the old-state days
  placebo states      e_Q^(-i), last 3 active days of non-adjacent same-regime periods
  field span          kickoff, goal text, room kickoffs of the new period (whitened, orthonormalized); projected out
  M_exc(u)            mean_i s_iu . P_perp e_old^(-i)  -  median_Q mean_i s_iu . P_perp e_Q^(-i)
No text is read. Thread caps: sitecustomize (2).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import OUT, holdout_mask  # noqa: E402
from embed_models import goal_vectors, load_whitener, statement_vectors  # noqa: E402

DATA = ROOT / "data/processed/H96-goal-switch-hysteresis"
EXCLUDE_AGENTS = {19, 28, 30}
EXCLUDE_GOALS = {23}
BINS = [0, 0.5, 1, 2, 4, 8, 16, 32]           # active hours since t0
UNITS = ["pre", "day1"] + [f"b{i}" for i in range(len(BINS) - 1)]
MIN_DAY, MIN_BIN = 3, 2                        # statements per agent-day / agent-bin vector
TAU_GRID = np.exp(np.linspace(np.log(0.05), np.log(500), 400))
MODELS = ["bge_small", "gte_modernbert"]
VARIANTS = {"style_resid32": "style_resid32", "white32": "white32", "style_resid_period32": "style_resid_period32"}


def unit(v, axis=-1):
    n = np.linalg.norm(v, axis=axis, keepdims=True)
    return np.where(n > 0, v / np.where(n > 0, n, 1), np.nan)


class Store:
    """Eligible non-holdout statements with their vectors, the calendar and whitened goal vectors."""

    def __init__(self, model: str = "bge_small", variant: str = "style_resid32", X=None):
        st = pl.read_parquet(OUT / "embeddings/statements.parquet").with_row_index("row")
        st = st.filter(~pl.col("holdout") & ~pl.col("agent").is_in(list(EXCLUDE_AGENTS))
                       & ~pl.col("goal_no").is_in(list(EXCLUDE_GOALS)))
        ho = np.array(holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list()))
        st = st.filter(pl.Series(~ho))
        assert not np.any(holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list()))
        self.st = st.with_columns(pl.col("regime").cast(pl.String))
        if X is None:
            X = statement_vectors(model, variant)[self.st["row"].to_numpy()].astype(np.float32)
            X = unit(X)
        self.X = X
        self.model = model
        cal = pl.read_parquet(OUT / "calendar.parquet").with_columns(pl.col("regime").cast(pl.String))
        self.cal = cal
        self.win_start = dict(zip(cal["pt_date"].to_list(), cal["win_start"].to_list()))
        self.win_s = dict(zip(cal["pt_date"].to_list(), cal["window_s"].to_list()))
        self.goals = pl.read_parquet(OUT / "embeddings/goals.parquet").with_columns(pl.col("kind").cast(pl.String))
        graw = goal_vectors(model).astype(np.float32)
        self.G = {r: unit(load_whitener(r, 32, model)(graw)) for r in ("I", "II", "III")}
        # per-row lookup arrays
        self.agent = self.st["agent"].to_numpy()
        self.day = self.st["pt_date"].to_numpy()
        self.t = self.st["t"].to_numpy()  # datetime64[us]
        self.goal = self.st["goal_no"].to_numpy()

    # ------------------------------------------------------------------ helpers
    def rows(self, days, t_lo=None, t_hi=None, agents=None):
        m = np.isin(self.day, list(days))
        if t_lo is not None:
            m &= self.t >= np.datetime64(t_lo.replace(tzinfo=None), "us")
        if t_hi is not None:
            m &= self.t < np.datetime64(t_hi.replace(tzinfo=None), "us")
        if agents is not None:
            m &= np.isin(self.agent, list(agents))
        return np.flatnonzero(m)

    def field_basis(self, gids, regime):
        F = self.G[regime][list(gids)] if len(gids) else np.zeros((0, 32), np.float32)
        F = F[np.all(np.isfinite(F), axis=1)]
        if F.shape[0] == 0:
            return np.zeros((32, 0), np.float32)
        q, r = np.linalg.qr(F.T.astype(np.float64))
        keep = np.abs(np.diag(r)) > 1e-6
        return q[:, keep].astype(np.float32)

    @staticmethod
    def perp(v, Q):
        return v - (v @ Q) @ Q.T if Q.shape[1] else v

    def kickoff_vec(self, g, regime):
        k = self.goals.filter((pl.col("goal_no") == g) & (pl.col("kind") == "kickoff"))
        return None if k.height == 0 else self.G[regime][k["gid"][0]]

    def eligible_kickoffs(self):
        from common import load_holdout
        held = set(load_holdout()["goal_periods_held_out"])
        k = self.goals.filter((pl.col("kind") == "kickoff") & ~pl.col("goal_no").is_in(list(held | EXCLUDE_GOALS))
                              & ~pl.col("holdout"))
        return dict(zip(k["goal_no"].to_list(), k["gid"].to_list()))

    def active_hours(self, rows, t0, days):
        """Active hours since t0 over the calendar windows of `days` (ordered) for statement rows."""
        days = list(days)
        cum, off = {}, 0.0
        t0n = np.datetime64(t0.replace(tzinfo=None), "us")
        for d in days:
            ws = np.datetime64(self.win_start[d].replace(tzinfo=None), "us")
            start = max(ws, t0n) if d == days[0] else ws
            cum[d] = (off, start)
            off += (ws + np.timedelta64(int(self.win_s[d]), "s") - start) / np.timedelta64(1, "h")
        h = np.full(len(rows), np.nan)
        for j, r in enumerate(rows):
            d = self.day[r]
            if d in cum:
                o, s = cum[d]
                h[j] = o + (self.t[r] - s) / np.timedelta64(1, "h")
        return h


def group_means(X, rows, keys, min_n):
    """Unit mean vectors per key (keys aligned to rows); returns dict key -> (vector, n)."""
    out = {}
    if len(rows) == 0:
        return out
    keys = np.asarray(keys)
    order = np.argsort(keys, kind="stable")
    ks, idx = np.unique(keys[order], return_index=True)
    bounds = list(idx) + [len(order)]
    for a, k in enumerate(ks):
        sel = rows[order[bounds[a]:bounds[a + 1]]]
        if len(sel) >= min_n:
            out[k] = (unit(X[sel].mean(0)), len(sel))
    return out


def agent_day_vectors(S: Store, X, days, t_hi=None, agents=None):
    """dict (agent, day) -> unit vector, for agent-days with >= MIN_DAY statements."""
    r = S.rows(days, t_hi=t_hi, agents=agents)
    keys = [f"{a}|{d}" for a, d in zip(S.agent[r], S.day[r])]
    g = group_means(X, r, keys, MIN_DAY)
    return {(int(k.split("|")[0]), k.split("|")[1]): v for k, (v, n) in g.items()}


def leave_out_dirs(adv: dict, agents):
    """Leave-agent-out unit centroids of agent-day vectors for each agent in `agents` (plus key -1: all)."""
    if not adv:
        return {}
    keys = list(adv)
    V = np.stack([adv[k] for k in keys])
    A = np.array([k[0] for k in keys])
    tot = V.sum(0)
    out = {-1: unit(tot)}
    for a in agents:
        m = A == a
        out[a] = unit(tot - V[m].sum(0)) if (~m).any() else np.full(32, np.nan, np.float32)
    return out


def order_q(adv: dict):
    """Mean cosine between different agents' agent-day vectors on the same day (pairs pooled over days)."""
    by_day = {}
    for (a, d), v in adv.items():
        by_day.setdefault(d, []).append(v)
    num, den = 0.0, 0
    for d, vs in by_day.items():
        if len(vs) < 2:
            continue
        V = np.stack(vs)
        C = V @ V.T
        n = len(vs)
        num += (C.sum() - np.trace(C)); den += n * (n - 1)
    return num / den if den else np.nan


def unit_vectors(S: Store, X, t0, pre_day, post_days, Pfirst_day):
    """Agent x unit vectors: 'pre', 'day1', bins. Returns agents, V (nA, nU, 32) with NaN, H centres (nU)."""
    pre_rows = np.concatenate([S.rows([pre_day]), S.rows([Pfirst_day], t_hi=t0)])
    post_rows = S.rows(post_days, t_lo=t0)
    h = S.active_hours(post_rows, t0, post_days)
    agents = sorted(set(S.agent[pre_rows].tolist()) | set(S.agent[post_rows].tolist()))
    ai = {a: j for j, a in enumerate(agents)}
    V = np.full((len(agents), len(UNITS), 32), np.nan, np.float32)
    Hc = np.full(len(UNITS), np.nan)
    def fill(rows, u, min_n):
        g = group_means(X, rows, S.agent[rows], min_n)
        for a, (v, n) in g.items():
            V[ai[a], u] = v
    fill(pre_rows, 0, MIN_BIN)
    d1 = post_rows[S.day[post_rows] == post_days[0]]
    fill(d1, 1, MIN_BIN)
    for b in range(len(BINS) - 1):
        m = (h >= BINS[b]) & (h < BINS[b + 1])
        if m.any():
            fill(post_rows[m], 2 + b, MIN_BIN)
            Hc[2 + b] = float(np.mean(h[m]))
    return agents, V, Hc


def projections(S: Store, X, rec: dict, mode: str = "state", old_days_override=None):
    """Per-agent projections for one transition (or pseudo-switch) record.

    rec keys: P (new period), Pm1 (old period or same for pseudo), regime, t0, pre_day, old_days, post_days,
              placebos, field_gids, first_day (P's first day; pseudo: post_days[0]).
    mode 'state': old state = leave-i-out late centroid of the old days; 'kickoff': the old kickoff vector.
    Returns dict with agents, m (nA, nU), mq (nA, nU, nQ), Hc, q (order), Ak (nA, nU) new-kickoff excess."""
    reg = rec["regime"]
    Q = S.field_basis(rec["field_gids"], reg)
    agents, V, Hc = unit_vectors(S, X, rec["t0"], rec["pre_day"], rec["post_days"], rec["first_day"])
    nA, nU = V.shape[:2]
    old_days = old_days_override or rec["old_days"]
    adv_old = agent_day_vectors(S, X, old_days)
    q = order_q(adv_old)
    if mode == "state":
        lo = leave_out_dirs(adv_old, agents)
        Eold = np.stack([lo.get(a, lo.get(-1)) for a in agents])
    else:
        k = S.kickoff_vec(rec["Pm1"], reg)
        Eold = np.tile(k, (nA, 1)) if k is not None else np.full((nA, 32), np.nan, np.float32)
    Eold = unit(S.perp(Eold, Q))
    m = np.einsum("aud,ad->au", V, Eold)
    plac = rec["placebos"]
    late = pl.read_parquet(DATA / "late_days.parquet")
    mq = np.full((nA, nU, len(plac)), np.nan, np.float32)
    for j, g in enumerate(plac):
        if mode == "state":
            dd = late.filter((pl.col("goal_no") == g) & (pl.col("regime") == reg))["pt_date"].to_list()
            lo = leave_out_dirs(agent_day_vectors(S, X, dd), agents)
            if not lo:
                continue
            Eq = np.stack([lo.get(a, lo.get(-1)) for a in agents])
        else:
            k = S.kickoff_vec(g, reg)
            if k is None:
                continue
            Eq = np.tile(k, (nA, 1))
        Eq = unit(S.perp(Eq, Q))
        mq[:, :, j] = np.einsum("aud,ad->au", V, Eq)
    # new-kickoff decoy-corrected alignment (coercive-field proxy, quench depth)
    ks = S.eligible_kickoffs()
    kP = S.kickoff_vec(rec["P"], reg)
    dec = [S.G[reg][gid] for g, gid in ks.items() if g not in (rec["P"] - 1, rec["P"], rec["P"] + 1)]
    if kP is not None and dec:
        D = np.stack(dec)
        Ak = np.einsum("aud,d->au", V, kP) - np.nanmean(np.einsum("aud,qd->auq", V, D), axis=2)
    else:
        Ak = np.full((nA, nU), np.nan)
    # Amendment 1 (after the synthetic, before real data): the new state, for the normalization-free switching time
    pdays = S.cal.filter((pl.col("goal_no") == rec["P"]) & (pl.col("regime") == reg)).sort("pt_date")["pt_date"].to_list()
    later = [d for d in pdays if d not in set(rec["post_days"]) and d > rec["post_days"][-1]]
    new_days = later[-3:] if later else pdays[-1:]
    lo_new = leave_out_dirs(agent_day_vectors(S, X, new_days), agents)
    if lo_new:
        Enew = unit(S.perp(np.stack([lo_new.get(a, lo_new.get(-1)) for a in agents]), Q))
        mnew = np.einsum("aud,ad->au", V, Enew)
    else:
        mnew = np.full((nA, nU), np.nan, np.float32)
    return {"agents": agents, "m": m, "mq": mq, "Hc": Hc, "q": q, "Ak": Ak, "n_old_agentdays": len(adv_old),
            "mnew": mnew, "new_overlap": not bool(later)}


def m_exc(m, mq, idx=None):
    """M_exc per unit for agent rows idx (bootstrap multiset) -> (nU,), plus n agents per unit."""
    if idx is not None:
        m, mq = m[idx], mq[idx]
    with np.errstate(all="ignore"):
        Mo = np.nanmean(m, axis=0)
        Mq = np.nanmedian(np.nanmean(mq, axis=0), axis=1) if mq.shape[2] else np.zeros(m.shape[1])
    n = np.sum(np.isfinite(m), axis=0)
    return Mo - Mq, n


def fit_tau(M, n, Hc, Mpre):
    """Weighted LS fit of M_b = Mpre exp(-h_b / tau) over post bins; returns tau (active h) or nan."""
    b = np.arange(2, len(UNITS))
    ok = np.isfinite(M[b]) & (n[b] >= 2) & np.isfinite(Hc[b])
    if ok.sum() < 2 or not np.isfinite(Mpre) or Mpre <= 0:
        return np.nan
    h, y, w = Hc[b][ok], M[b][ok], n[b][ok].astype(float)
    pred = Mpre * np.exp(-h[None, :] / TAU_GRID[:, None])
    sse = ((pred - y[None, :]) ** 2 * w[None, :]).sum(1)
    return float(TAU_GRID[np.argmin(sse)])


def t_half(M, n, Hc, Mpre):
    b = np.arange(2, len(UNITS))
    if not np.isfinite(Mpre) or Mpre <= 0:
        return np.nan
    for j in b:
        if n[j] >= 2 and np.isfinite(M[j]) and M[j] < 0.5 * Mpre:
            return float(Hc[j])
    return np.inf


def switch_time(Mo, Mn, n, Hc):
    """Amendment 1: normalization-free switching time. L_b = ln(M_old/M_new) on post bins with both > 0;
    weighted LS L_b = L0 - h_b / tau_sw (>= 3 bins). The unit norm cancels in the ratio, so tau_sw does not depend
    on the old state's amplitude when the decay rate does not."""
    b = np.arange(2, len(UNITS))
    ok = np.isfinite(Mo[b]) & np.isfinite(Mn[b]) & (Mo[b] > 0) & (Mn[b] > 0) & (n[b] >= 2) & np.isfinite(Hc[b])
    if ok.sum() < 3:
        return np.nan, np.nan
    h, y, w = Hc[b][ok], np.log(Mo[b][ok] / Mn[b][ok]), n[b][ok].astype(float)
    X = np.column_stack([np.ones(len(h)), h]) * np.sqrt(w)[:, None]
    beta, *_ = np.linalg.lstsq(X, y * np.sqrt(w), rcond=None)
    slope = beta[1]
    tau = float(np.clip(-1.0 / slope, 0.05, 500)) if slope < 0 else 500.0
    return tau, float(beta[0])


def summarize(pr: dict, n_boot: int = 300, seed: int = 0):
    """Point estimates and agent-bootstrap CIs of M_pre, M_1, R1, tau, t_half, A_K(day1)."""
    m, mq, Hc = pr["m"], pr["mq"], pr["Hc"]
    rng = np.random.default_rng(seed)
    def stats(idx):
        M, n = m_exc(m, mq, idx)
        Mpre, M1 = M[0], M[1]
        R1 = M1 / Mpre if (np.isfinite(Mpre) and Mpre > 0) else np.nan
        tau = fit_tau(M, n, Hc, Mpre)
        Ak = np.nanmean(pr["Ak"][idx if idx is not None else slice(None), 1])
        Mn, _ = m_exc(pr["mnew"], mq, idx)
        tsw, _ = switch_time(M, Mn, n, Hc)
        return np.array([Mpre, M1, R1, tau, Ak, tsw])
    est = stats(None)
    M, n = m_exc(m, mq)
    nA = m.shape[0]
    boots = (np.array([stats(rng.integers(0, nA, nA)) for _ in range(n_boot)]) if (nA >= 2 and n_boot > 0)
             else np.full((1, 6), np.nan))
    with np.errstate(all="ignore"):
        lo = np.nanpercentile(boots, 2.5, axis=0); hi = np.nanpercentile(boots, 97.5, axis=0)
    names = ["M_pre", "M_1", "R1", "tau", "A_K1", "tau_sw"]
    out = {k: {"est": float(est[j]), "lo": float(lo[j]), "hi": float(hi[j])} for j, k in enumerate(names)}
    out["t_half"] = t_half(M, n, Hc, M[0])
    out["M_series"] = [None if not np.isfinite(x) else float(x) for x in M]
    out["n_series"] = [int(x) for x in n]
    out["H_centres"] = [None if not np.isfinite(x) else float(x) for x in Hc]
    out["q"] = float(pr["q"]); out["n_agents"] = int(nA); out["n_placebos"] = int(mq.shape[2])
    Mn, _ = m_exc(pr["mnew"], mq)
    out["Mnew_series"] = [None if not np.isfinite(x) else float(x) for x in Mn]
    out["new_overlap"] = bool(pr.get("new_overlap", False))
    out["Ak_series"] = [None if not np.isfinite(x) else float(x) for x in np.nanmean(pr["Ak"], axis=0)]
    return out


def transition_records():
    tr = pl.read_parquet(DATA / "transitions.parquet").filter(pl.col("eligible"))
    cal = pl.read_parquet(OUT / "calendar.parquet")
    recs = []
    for r in tr.iter_rows(named=True):
        first = cal.filter(pl.col("goal_no") == r["P"]).sort("pt_date")["pt_date"][0]
        recs.append({**r, "first_day": first})
    return recs


def pseudo_records():
    ps = pl.read_parquet(DATA / "pseudo.parquet").filter(pl.col("n_placebos") >= 3)
    recs = []
    for r in ps.iter_rows(named=True):
        recs.append({**r, "P": r["goal_no"], "Pm1": r["goal_no"], "first_day": r["post_days"][0]})
    return recs
