"""H31 library: block schedules, exposure-graph spectral gaps, time-respecting DeGroot gap, simulators on the real
reading schedule (DeGroot / voter / contagion / herding / field), consensus-event detection, and regression tools.

Units: active seconds inside, active hours in every reported rate or time. Definitions: ../README.md.
"""
from __future__ import annotations

import os

os.environ.setdefault("POLARS_MAX_THREADS", "2")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data/processed/H31-consensus-time-spectral-gap"
HYP = ROOT / "hypotheses/H31-consensus-time-spectral-gap"
W_H = 0.5          # window length (h) for W = 30 min
CARRY = 4          # carry-forward windows
EVENT_WINDOW_H = 4.0


# ----------------------------------------------------------------------------------------------- loading
def load_period(g: int, root: Path = DATA) -> dict:
    f = root / f"G{g:02d}"
    P = {"g": g}
    for name in ("days", "msgs", "turns", "reads", "block_windows", "alignment", "kicks"):
        p = f / f"{name}.parquet"
        P[name] = pl.read_parquet(p) if p.exists() else None
    for W in (15, 30, 60):
        p = f / f"states_project_w{W}.parquet"
        P[f"states{W}"] = pl.read_parquet(p) if p.exists() else None
    return P


def blocks_of(P: dict, min_agents: int = 3) -> list[int]:
    bw = P["block_windows"]
    if bw is None or "room" not in bw.columns:
        return []
    n = bw.drop_nulls("room").group_by("day", "win", "room").agg(pl.col("agent").n_unique().alias("n"))
    med = n.group_by("room").agg(pl.col("n").median().alias("m"), pl.len().alias("nw"))
    tot = bw.select("day", "win").unique().height
    keep = med.filter((pl.col("m") >= min_agents) & (pl.col("nw") >= 0.25 * tot))
    return sorted(int(r) for r in keep["room"].to_list())


def period_T(P: dict) -> float:
    return float(P["days"]["window_s"].sum())


# ----------------------------------------------------------------------------------------------- schedule
@dataclass
class Schedule:
    agents: np.ndarray            # agent codes (index = position)
    a0: float
    a1: float
    msg_t: np.ndarray             # active s
    msg_s: np.ndarray             # sender index
    upd_t: np.ndarray             # active s
    upd_i: np.ndarray             # recipient index
    upd_ptr: np.ndarray           # CSR pointers into upd_m
    upd_m: np.ndarray             # message indices (local)
    turns: list = field(default_factory=list)   # per agent active-s turn times
    W: np.ndarray | None = None   # seen-weighted graph per active hour, W[i, j] = j's messages seen by i

    @property
    def N(self):
        return len(self.agents)

    @property
    def T_h(self):
        return (self.a1 - self.a0) / 3600.0

    def events(self):
        """Merged event order: (time, type, index) with emissions (type 0) before updates (type 1) at ties."""
        t = np.r_[self.msg_t, self.upd_t]
        typ = np.r_[np.zeros(len(self.msg_t), np.int8), np.ones(len(self.upd_t), np.int8)]
        idx = np.r_[np.arange(len(self.msg_t)), np.arange(len(self.upd_t))]
        o = np.lexsort((typ, t))
        return t[o], typ[o], idx[o]


def core_agents(P: dict, room: int, frac: float = 0.5) -> set[int]:
    """Robustness variant (declared 2026-10-03 before outcomes): agents present in the room in >= frac of the
    block-period's windows."""
    bw = P["block_windows"].filter(pl.col("room") == room)
    nw = bw.select("day", "win").unique().height
    c = bw.group_by("agent").agg(pl.len().alias("n"))
    return set(c.filter(pl.col("n") >= frac * nw)["agent"].to_list())


def make_schedule(P: dict, room: int, a0: float | None = None, a1: float | None = None,
                  keep: set[int] | None = None) -> Schedule | None:
    a0 = 0.0 if a0 is None else a0
    a1 = period_T(P) + 1.0 if a1 is None else a1
    msgs, reads, turns, bw = P["msgs"], P["reads"], P["turns"], P["block_windows"]
    if reads is None or msgs is None:
        return None
    present = set(bw.filter(pl.col("room") == room)["agent"].drop_nulls().to_list())
    if keep is not None:
        present &= set(keep)
    m = msgs.filter((pl.col("kind") == 0) & (pl.col("room") == room) & (pl.col("act") >= a0) & (pl.col("act") < a1)
                    & pl.col("sender").is_in(list(present)))
    r = reads.filter((pl.col("room") == room) & (pl.col("act_upd") >= a0) & (pl.col("act_upd") < a1)
                     & pl.col("recipient").is_in(list(present)) & pl.col("msg").is_in(m["msg"].implode()))
    act_agents = sorted(set(m["sender"].to_list()) | set(r["recipient"].to_list()))
    if len(act_agents) < 3:
        return None
    ag = np.array(act_agents, np.int16)
    pos = {int(a): i for i, a in enumerate(ag)}
    m = m.filter(pl.col("sender").is_in(act_agents)).sort("act", "t_us")
    mloc = {int(x): i for i, x in enumerate(m["msg"].to_list())}
    msg_t = m["act"].to_numpy().astype(np.float64)
    msg_s = np.array([pos[int(s)] for s in m["sender"].to_list()], np.int16)
    r = r.filter(pl.col("msg").is_in(list(mloc))).sort("t_upd_us", "recipient")
    # batches: one update per (recipient, t_upd)
    rr = r.select("recipient", "t_upd_us", "act_upd", "msg").to_numpy()
    upd_t, upd_i, ptr, um = [], [], [0], []
    if len(rr):
        keys = rr[:, 0].astype(np.int64) * (1 << 50) + rr[:, 1].astype(np.int64)
        o = np.argsort(keys, kind="stable")
        rr = rr[o]
        keys = keys[o]
        starts = np.r_[0, np.flatnonzero(np.diff(keys)) + 1, len(keys)]
        for s, e in zip(starts[:-1], starts[1:]):
            upd_t.append(float(rr[s, 2]))
            upd_i.append(pos[int(rr[s, 0])])
            um.extend(mloc[int(x)] for x in rr[s:e, 3])
            ptr.append(len(um))
        o2 = np.argsort(np.array(upd_t), kind="stable")
        upd_t = np.array(upd_t)[o2]
        upd_i = np.array(upd_i, np.int16)[o2]
        ptr_a = np.array(ptr)
        lens = np.diff(ptr_a)[o2]
        st = ptr_a[:-1][o2]
        um_a = np.array(um, np.int64)
        um = np.concatenate([um_a[s:s + l] for s, l in zip(st, lens)]) if len(st) else np.zeros(0, np.int64)
        ptr = np.r_[0, np.cumsum(lens)]
    else:
        upd_t, upd_i, ptr, um = np.zeros(0), np.zeros(0, np.int16), np.zeros(1, np.int64), np.zeros(0, np.int64)
    tl = []
    if turns is not None:
        tsub = turns.filter((pl.col("act") >= a0) & (pl.col("act") < a1))
        for a in ag:
            tl.append(np.sort(tsub.filter(pl.col("agent") == int(a))["act"].to_numpy()))
    S = Schedule(ag, a0, a1, msg_t, msg_s, np.asarray(upd_t, float), np.asarray(upd_i, np.int16),
                 np.asarray(ptr, np.int64), np.asarray(um, np.int64), tl)
    # seen-weighted graph per active hour
    W = np.zeros((S.N, S.N))
    for k in range(len(S.upd_t)):
        i = S.upd_i[k]
        js = S.msg_s[S.upd_m[S.upd_ptr[k]:S.upd_ptr[k + 1]]]
        np.add.at(W[i], js, 1.0)
    S.W = W / max(S.T_h, 1e-9)
    return S


# ----------------------------------------------------------------------------------------------- spectra
def lam2_sym(W: np.ndarray) -> float:
    A = (W + W.T) / 2
    np.fill_diagonal(A, 0)
    L = np.diag(A.sum(1)) - A
    ev = np.linalg.eigvalsh(L)
    return float(max(ev[1], 0.0)) if len(ev) > 1 else 0.0


def lam2_dir(W: np.ndarray) -> float:
    A = W.copy()
    np.fill_diagonal(A, 0)
    L = np.diag(A.sum(1)) - A          # in-degree Laplacian: dx_i/dt = sum_j W_ij (x_j - x_i)
    ev = np.sort(np.linalg.eigvals(L).real)
    return float(max(ev[1], 0.0)) if len(ev) > 1 else 0.0


def lam2_bin(W: np.ndarray) -> float:
    A = ((W + W.T) > 0).astype(float)
    np.fill_diagonal(A, 0)
    d = A.sum(1)
    if (d == 0).any():
        return 0.0
    Dm = np.diag(1 / np.sqrt(d))
    ev = np.linalg.eigvalsh(np.eye(len(d)) - Dm @ A @ Dm)
    return float(max(ev[1], 0.0))


def lam2_rw(W: np.ndarray) -> float:
    A = W.copy()
    np.fill_diagonal(A, 0)
    d = A.sum(1)
    if (d == 0).any():
        return 0.0
    Pm = A / d[:, None]
    ev = np.sort(np.linalg.eigvals(np.eye(len(d)) - Pm).real)
    return float(max(ev[1], 0.0))


def reading_rate(S: Schedule) -> float:
    """Median over agents of reading turns (updates that see >= 1 new agent message) per active hour."""
    c = np.bincount(S.upd_i, minlength=S.N) / max(S.T_h, 1e-9)
    return float(np.median(c))


def mention_W(P: dict, S: Schedule) -> np.ndarray:
    m = P["msgs"].filter((pl.col("kind") == 0) & (pl.col("act") >= S.a0) & (pl.col("act") < S.a1)
                         & pl.col("sender").is_in(S.agents.tolist()))
    pos = {int(a): i for i, a in enumerate(S.agents)}
    M = np.zeros((S.N, S.N))
    for s, ms in zip(m["sender"].to_list(), m["mentions"].to_list()):
        for i in (ms or []):
            if int(i) in pos and int(i) != int(s):
                M[pos[int(i)], pos[int(s)]] += 1      # j (sender) addresses i: edge j -> i
    return M / max(S.T_h, 1e-9)


# ----------------------------------------------------------------------------------------------- time-respecting DeGroot
def gamma_tr(S: Schedule, alpha: float = 0.5, K: int = 8, seed: int = 0, burn_h: float = 0.5) -> float:
    """Decay rate (1/active h) of disagreement for linear DeGroot at reading turns, messages carrying the sender's
    state at emission. Exact for the linear system with delays (renormalized); slope of ln D on time after burn-in."""
    rng = np.random.default_rng(seed)
    X = rng.standard_normal((S.N, K))
    MS = np.zeros((len(S.msg_t), K))
    t, typ, idx = S.events()
    logscale = 0.0
    rec_t, rec_D = [], []
    for k in range(len(t)):
        if typ[k] == 0:
            MS[idx[k]] = X[S.msg_s[idx[k]]]
        else:
            u = idx[k]
            ms = S.upd_m[S.upd_ptr[u]:S.upd_ptr[u + 1]]
            if len(ms):
                i = S.upd_i[u]
                X[i] = (1 - alpha) * X[i] + alpha * MS[ms].mean(0)
            if k % 25 == 0 or k == len(t) - 1:
                mu = X.mean(0)
                X -= mu
                MS -= mu
                D = np.sqrt((X ** 2).sum())
                if D <= 1e-280:          # exact consensus reached: stop recording
                    break
                if D < 1e-3:
                    X /= D
                    MS /= D
                    logscale += np.log(D)
                    D = 1.0
                rec_t.append(t[k])
                rec_D.append(np.log(D) + logscale)
    rec_t = (np.array(rec_t) - S.a0) / 3600
    rec_D = np.array(rec_D)
    ok = rec_t >= burn_h
    if ok.sum() < 5:
        ok = np.ones(len(rec_t), bool)
    if ok.sum() < 3:
        return np.nan
    b = np.polyfit(rec_t[ok], rec_D[ok], 1)[0]
    return float(max(-b, 0.0))


def tau_wave(S: Schedule, n: int = 400, seed: int = 0) -> float:
    """Herding-wave timescale (h): median over agents of the wait to the next turn after a random broadcast time,
    averaged over random times in the interval."""
    rng = np.random.default_rng(seed)
    ts = rng.uniform(S.a0, S.a1, n)
    out = []
    for t in ts:
        w = []
        for T in S.turns:
            j = np.searchsorted(T, t, side="right")
            w.append(T[j] - t if j < len(T) else np.inf)
        out.append(np.median(w))
    out = np.array(out)
    out = out[np.isfinite(out)]
    return float(np.mean(out) / 3600) if len(out) else np.nan


# ----------------------------------------------------------------------------------------------- categorical simulators
def simulate_states(S: Schedule, model: str, prm: dict, start_s: float, R: int, rng, grid_s: np.ndarray,
                    max_cycles: int = 12, other_states: int = 3):
    """Run R replicates of a categorical adoption process on the real schedule, starting at active time start_s with
    one random seed agent holding the new state (1). Non-adopters hold 0. Returns (states at grid times (R, G, N),
    time-to-true-50% in h (R,), nan if not reached).

    Models (update at reading turns of i, batch B of newly seen agent messages, n1 = adopter messages in B):
      'D' count contagion (SI):      adopt w.p. 1 - exp(-beta * n1)
      'A' fraction contagion (SI):   adopt w.p. 1 - exp(-beta * n1 / |B|)
      'V' voter:                     w.p. alpha copy the state carried by a random m in B (both directions)
      'H' herding wave (SI, strong): adopt w.p. p_h if n1 >= 1 (one-shot per batch)
      'F' field:                     agent i adopts at start + Exp(mean d_h), independent of the graph
    The schedule is replayed cyclically (offset by its length) if needed."""
    N = S.N
    T = S.a1 - S.a0
    t_ev, typ, idx = S.events()
    X = np.zeros((R, N), np.int8)
    seed_ag = rng.integers(0, N, R)
    X[np.arange(R), seed_ag] = 1
    MS = np.zeros((R, len(S.msg_t)), np.int8)
    t50 = np.full(R, np.nan)
    G = len(grid_s)
    out = np.zeros((R, G, N), np.int8)
    gi = 0
    half = N / 2.0
    if model == "F":
        dly = rng.exponential(prm["d_h"] * 3600, (R, N))
        dly[np.arange(R), seed_ag] = 0
        tad = start_s + dly
        for g_ in range(G):
            out[:, g_, :] = (tad <= grid_s[g_]).astype(np.int8)
        srt = np.sort(tad, 1)
        k = int(np.ceil(half))
        t50 = (srt[:, k - 1] - start_s) / 3600
        return out, t50
    k0 = int(np.searchsorted(t_ev, start_s, side="left"))
    cyc = 0
    k = k0
    while gi < G and cyc < max_cycles:
        if k >= len(t_ev):
            k = 0
            cyc += 1
            continue
        tt = t_ev[k] + cyc * T
        if cyc == 0 and tt < start_s:
            k += 1
            continue
        while gi < G and grid_s[gi] <= tt:
            out[:, gi, :] = X
            gi += 1
        if typ[k] == 0:
            MS[:, idx[k]] = X[:, S.msg_s[idx[k]]]
        else:
            u = idx[k]
            ms = S.upd_m[S.upd_ptr[u]:S.upd_ptr[u + 1]]
            if len(ms):
                i = S.upd_i[u]
                b = MS[:, ms]
                n1 = b.sum(1)
                if model == "D":
                    p = 1 - np.exp(-prm["beta"] * n1)
                    X[:, i] = np.maximum(X[:, i], (rng.random(R) < p).astype(np.int8))
                elif model == "A":
                    p = 1 - np.exp(-prm["beta"] * n1 / len(ms))
                    X[:, i] = np.maximum(X[:, i], (rng.random(R) < p).astype(np.int8))
                elif model == "H":
                    X[:, i] = np.maximum(X[:, i], ((n1 > 0) & (rng.random(R) < prm["p_h"])).astype(np.int8))
                elif model == "V":
                    pick = b[np.arange(R), rng.integers(0, len(ms), R)]
                    cp = rng.random(R) < prm["alpha"]
                    X[cp, i] = pick[cp]
        nn = X.sum(1)
        newly = np.isnan(t50) & (nn >= half)
        t50[newly] = (tt - start_s) / 3600
        k += 1
    while gi < G:
        out[:, gi, :] = X
        gi += 1
    return out, t50


def observe(states: np.ndarray, p_obs: float, rng, other_labels: np.ndarray) -> np.ndarray:
    """Observation model: each agent-window labeled w.p. p_obs; adopters -> 1, others -> their own project (>= 2)."""
    R, G, N = states.shape
    lab = np.where(states == 1, 1, other_labels[None, None, :]).astype(np.int16)
    miss = rng.random((R, G, N)) >= p_obs
    lab[miss] = -1
    return lab


# ----------------------------------------------------------------------------------------------- event detection (E-P)
def carry_forward(lab: np.ndarray, L: int = CARRY) -> np.ndarray:
    """lab (G, N): -1 missing, 0 other, >= 1 real. Returns the most recent real label within the last L windows."""
    G, N = lab.shape
    out = np.full((G, N), -1, lab.dtype)
    last = np.full(N, -1, lab.dtype)
    age = np.full(N, 10 ** 6)
    for g in range(G):
        real = lab[g] >= 1
        last = np.where(real, lab[g], last)
        age = np.where(real, 0, age + 1)
        out[g] = np.where(age < L, last, -1)
    return out


def detect_project_events(lab: np.ndarray, act_h: np.ndarray, Nb: np.ndarray, L: int = CARRY, w_h: float = W_H,
                          restrict_label: int | None = None) -> list[dict]:
    """E-P rule (card): consensus for a at w iff n_a >= max(3, ceil(Nb/3)) and n_a / N_lab >= 0.5 in w and w+1.
    Onset t0 = first window any agent holds a (raw label). tau = act(t_c) - act(t0), floored at w_h/2.
    Frozen if the criterion holds at t0 or at the first window with N_lab >= 3."""
    cf = carry_forward(lab, L)
    G = lab.shape[0]
    nlab = (cf >= 1).sum(1)
    labels = sorted(set(np.unique(lab[lab >= 1]).tolist()))
    if restrict_label is not None:
        labels = [x for x in labels if x == restrict_label]
    first_ok = int(np.argmax(nlab >= 3)) if (nlab >= 3).any() else None
    evs = []
    for a in labels:
        na = (cf == a).sum(1)
        need = np.maximum(3, np.ceil(Nb / 3.0))
        crit = (na >= need) & (na >= 0.5 * np.maximum(nlab, 1)) & (nlab >= 3)
        crit2 = crit[:-1] & crit[1:]
        held = np.flatnonzero((lab == a).any(1))
        t0 = int(held[0])
        hits = np.flatnonzero(crit2[t0:]) + t0 if t0 < G - 1 else np.array([], int)
        x = np.where(nlab > 0, na / np.maximum(nlab, 1), np.nan)
        maxheld = int(((cf == a).sum(1)).max())
        if len(hits) == 0:
            evs.append(dict(label=int(a), t0=t0, tc=None, tau_h=np.nan, frozen=False, consensus=False,
                            max_n=maxheld, rise=None))
            continue
        tc = int(hits[0])
        frozen = bool(crit[t0] or (first_ok is not None and crit[first_ok] and first_ok >= t0 and tc <= first_ok))
        tau = max(float(act_h[tc] - act_h[t0]), w_h / 2)
        # rise: windows from the last window with x < 0.25 (before tc) to tc
        pre = np.flatnonzero((x[:tc] < 0.25) & np.isfinite(x[:tc]))
        rise = int(tc - pre[-1]) if len(pre) else None
        evs.append(dict(label=int(a), t0=t0, tc=tc, tau_h=tau, frozen=frozen, consensus=True, max_n=maxheld, rise=rise))
    return evs


# ----------------------------------------------------------------------------------------------- content (E-C)
def fit_relaxation(t_h: np.ndarray, A: np.ndarray, w: np.ndarray, T_h: float):
    """A(t) = Ainf - dA exp(-t/tau), weighted LS; tau on a log grid [0.25 h, 2T]. Returns dict with tau, dA, Ainf,
    dBIC (exp vs const; positive favours exp), at_bound flag."""
    w = w / w.mean()
    n = len(t_h)
    mu = np.sum(w * A) / np.sum(w)
    rss0 = np.sum(w * (A - mu) ** 2)
    best = None
    for tau in np.geomspace(0.25, max(2 * T_h, 0.5), 80):
        Xm = np.c_[np.ones(n), -np.exp(-t_h / tau)]
        sw = np.sqrt(w)
        coef, *_ = np.linalg.lstsq(Xm * sw[:, None], A * sw, rcond=None)
        rss = np.sum(w * (A - Xm @ coef) ** 2)
        if best is None or rss < best[0]:
            best = (rss, tau, coef)
    rss1, tau, coef = best
    bic0 = n * np.log(rss0 / n) + 1 * np.log(n)
    bic1 = n * np.log(rss1 / n) + 3 * np.log(n)
    return dict(tau=float(tau), Ainf=float(coef[0]), dA=float(coef[1]), A0=float(coef[0] - coef[1]),
                dBIC=float(bic0 - bic1), at_bound=bool(tau >= T_h), n=n)


def detect_content_event(al: pl.DataFrame, room: int, T_h: float, min_agents: int = 3, min_windows: int = 12) -> dict:
    a = al.filter((pl.col("room") == room) & (pl.col("n_agents") >= min_agents)).sort("act_mid")
    if a.height < min_windows:
        return dict(kind="n/a", n=a.height)
    t = a["act_mid"].to_numpy() / 3600
    t = t - t.min() + W_H / 2
    n = a["n_agents"].to_numpy()
    f = fit_relaxation(t, a["A"].to_numpy(), n * (n - 1) / 2.0, T_h)
    if f["dBIC"] >= 6 and f["dA"] > 0 and not f["at_bound"]:
        kind = "convergence"
    elif f["dBIC"] >= 6 and f["dA"] < 0:
        kind = "divergence"
    else:
        kind = "none"
    f["kind"] = kind
    return f


# ----------------------------------------------------------------------------------------------- regression tools
def ols(x, y):
    X = np.c_[np.ones(len(x)), x]
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    return coef


def cluster_boot_slope(x, y, cl, B=2000, seed=0):
    rng = np.random.default_rng(seed)
    x, y, cl = map(np.asarray, (x, y, cl))
    u = np.unique(cl)
    if len(u) < 3:
        return np.nan, (np.nan, np.nan)
    b0 = ols(x, y)[1]
    bs = []
    groups = {c: np.flatnonzero(cl == c) for c in u}
    for _ in range(B):
        pick = rng.choice(u, len(u), replace=True)
        ii = np.concatenate([groups[c] for c in pick])
        if np.ptp(x[ii]) == 0:
            continue
        bs.append(ols(x[ii], y[ii])[1])
    bs = np.array(bs)
    return float(b0), (float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975)))


def lopo(y, cl, X=None, offset=None):
    """Leave-one-period-out predictions of y. X: free-slope regressors (n, k) or None; offset: fixed-slope term."""
    y = np.asarray(y, float)
    cl = np.asarray(cl)
    off = np.zeros(len(y)) if offset is None else np.asarray(offset, float)
    pred = np.full(len(y), np.nan)
    for c in np.unique(cl):
        te = cl == c
        tr = ~te
        if tr.sum() < 2:
            continue
        yt = y[tr] - off[tr]
        if X is None:
            pred[te] = yt.mean() + off[te]
        else:
            Xtr = np.c_[np.ones(tr.sum()), np.asarray(X)[tr]]
            coef, *_ = np.linalg.lstsq(Xtr, yt, rcond=None)
            pred[te] = np.c_[np.ones(te.sum()), np.asarray(X)[te]] @ coef + off[te]
    return pred


def rmse(a, b):
    m = np.isfinite(a) & np.isfinite(b)
    return float(np.sqrt(np.mean((a[m] - b[m]) ** 2))) if m.any() else np.nan
