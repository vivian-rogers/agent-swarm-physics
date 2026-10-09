"""H145 analysis library: synthetic worlds on the real #51 skeleton, discovery wrappers, pattern environment E,
Krakauer pattern-level tests, pseudo-pattern nulls, host renewal.

Shared instruments come from infra/shared/memeplex.py (elements, panels, discovery) and infra/shared/individuality.py
(held-out log-loss estimators, Besag-Clifford). Nothing here reads reserved data: the panels are built by
scheme/build.py from non-reserved #51 days only.
"""
from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
CARD = HERE.parent
ROOT = CARD.parents[1]
sys.path.insert(0, str(ROOT / "infra/shared"))
sys.path.insert(0, str(CARD / "scheme"))
import individuality as IND  # noqa: E402
import memeplex as MP  # noqa: E402

OUT = ROOT / "data/processed/H145-ideology-egregores-51"
N_PLANT = 8
BOOKEND_DAY = "2026-08-04"


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


# ============================================================================ skeleton
@dataclass
class Skeleton:
    bins: object
    present: np.ndarray        # [nA, nB] bool
    g: np.ndarray              # [nA, nB] activity factor (distinct elements / agent mean), 0 where absent
    R: np.ndarray              # [nA, nE] per-agent element rates per present bin (binary expression)
    nE: int
    act: np.ndarray            # [nA, nB] distinct elements expressed (real)


def skeleton(panel) -> Skeleton:
    b = panel.bins
    Y = panel.binary()
    act = np.asarray(Y.sum(1)).ravel().reshape(b.nA, b.nB) * b.present
    n_i = b.present.sum(1)
    mean_a = act.sum(1) / np.maximum(n_i, 1)
    g = np.where(b.present, act / np.maximum(mean_a, 1e-9)[:, None], 0.0)
    pr = panel.present_rows()
    agent_of = pr // b.nB
    import scipy.sparse as sp
    A = sp.csr_matrix((np.ones(len(pr)), (agent_of, np.arange(len(pr)))), shape=(b.nA, len(pr)))
    C = (A @ Y[pr]).toarray()
    R = C / np.maximum(n_i, 1)[:, None]
    return Skeleton(b, b.present.copy(), g, R, panel.nE, act)


# ============================================================================ synthetic worlds
def _host_chain(present, dob, rng, eps, rho, stay, init=0.0, field_logit=None):
    """Bin-level host dynamics on the real presence mask. A non-host becomes a host with prob eps + rho * prev(b)
    (prev = village host share among present agents in the previous bin, carried across day ends); a host stays a host
    with prob `stay`. Absent agent-bins keep their status (hidden) and do not count in prev. With field_logit, hosting
    is i.i.d. given a shared field: P(host) = sigmoid(field_logit[b])."""
    nA, nB = present.shape
    H = np.zeros((nA, nB), bool)
    if field_logit is not None:
        p = 1.0 / (1.0 + np.exp(-field_logit))
        return (rng.random((nA, nB)) < p[None, :]) & present
    h = rng.random(nA) < init
    prev = init
    for b in range(nB):
        pres = present[:, b]
        u = rng.random(nA)
        new = np.where(h, u < stay, u < eps + rho * prev)
        h = np.where(pres, new, h)
        H[:, b] = h & pres
        prev = H[pres, b].mean() if pres.any() else prev
    return H


def world(sk: Skeleton, kind: str, rng: np.random.Generator, rho: float = 0.0, q_host: float = 0.5,
          field_noise: float = 0.0) -> dict:
    """One synthetic panel on the real skeleton: background = every real element, expressed independently with
    p = min(1, r_ie * g_ib) on present agent-bins (agent vocabulary and agent-bin activity, no co-expression beyond
    them); plus N_PLANT planted elements (columns nE .. nE+7) whose rule depends on `kind`:
      W0        independent, p = 0.05 g_ib (no pattern)
      W_field   hosting i.i.d. given a shared field f(b) (day AR(1) 0.8 + bin noise); E observes f (field_noise adds
                observation noise with that sd)
      W_hub     one hub agent with a persistent on/off state (stay 0.8) expresses q 0.6; others echo in b+1 with
                prob 0.05 when the hub was on in b (each echo expresses an element with prob 0.35)
      W_prior   one lab's agents express each element with prob 0.25 in every present bin (constant)
      W_sticky  five fixed agents from >= 2 labs with persistent hosting (stay 0.97), no recruitment
      W_egr     self-reinforcing memeplex: eps 0.005 + rho * prev(b) recruitment, stay 0.85, newcomers recruited too
    Hosts express each planted element with prob q_host per bin. Returns dict(panel, planted, field, H_true)."""
    import scipy.sparse as sp
    b = sk.bins
    nA, nB, nE = b.nA, b.nB, sk.nE
    pres = sk.present
    dob = b.day_of_bin
    # background, sparse by element blocks to keep memory small
    rows, cols = [], []
    for e0 in range(0, nE, 256):
        e1 = min(nE, e0 + 256)
        p = np.minimum(1.0, sk.R[:, None, e0:e1] * sk.g[:, :, None])
        X = rng.random(p.shape, dtype=np.float32) < p
        X &= pres[:, :, None]
        a, bb, e = np.nonzero(X)
        rows.append(a * nB + bb)
        cols.append(e + e0)
    fieldv = None
    H = np.zeros((nA, nB), bool)
    Pl = np.zeros((nA, nB, N_PLANT), bool)
    g = sk.g
    if kind == "W0":
        Pl = rng.random((nA, nB, N_PLANT)) < np.minimum(1, 0.05 * g)[:, :, None]
    elif kind == "W_field":
        nd = int(dob.max()) + 1
        z = np.zeros(nd)
        for d in range(1, nd):
            z[d] = 0.8 * z[d - 1] + np.sqrt(1 - 0.64) * rng.normal()
        f = z[dob] + 0.5 * rng.normal(size=nB)
        H = _host_chain(pres, dob, rng, 0, 0, 0, field_logit=-2.0 + 1.5 * f)
        Pl = H[:, :, None] & (rng.random((nA, nB, N_PLANT)) < q_host)
        fieldv = f + field_noise * rng.normal(size=nB)
    elif kind == "W_hub":
        hub = int(np.argmax(pres.sum(1) * (sk.act.sum(1) + 1)))
        on = np.zeros(nB, bool)
        s = False
        for t in range(nB):
            s = (rng.random() < 0.8) if s else (rng.random() < 0.3)
            on[t] = s and pres[hub, t]
        Pl[hub] = on[:, None] & (rng.random((nB, N_PLANT)) < 0.6)
        echo = np.zeros((nA, nB), bool)
        echo[:, 1:] = (rng.random((nA, nB - 1)) < 0.05) & on[None, :-1] & (dob[1:] == dob[:-1])[None, :]
        echo[hub] = False
        echo &= pres
        Pl |= echo[:, :, None] & (rng.random((nA, nB, N_PLANT)) < 0.35)
        H = echo.copy()
        H[hub] = on
    elif kind == "W_prior":
        labs = np.array([b.labs[a] for a in b.agents])
        big = max(set(labs), key=lambda L: (pres[labs == L].sum(), L))
        mem = labs == big
        Pl = mem[:, None, None] & pres[:, :, None] & (rng.random((nA, nB, N_PLANT)) < 0.25)
        H = mem[:, None] & pres
    elif kind == "W_sticky":
        labs = np.array([b.labs[a] for a in b.agents])
        order = np.argsort(-pres.sum(1))
        chosen, seen = [], set()
        for i in order:                    # five frequently present agents, at least two labs
            if len(chosen) < 5 and (len(seen) < 2 or labs[i] in seen or len(chosen) < 4):
                chosen.append(i)
                seen.add(labs[i])
        sel = np.zeros(nA, bool)
        sel[chosen] = True
        Hs = _host_chain(pres, dob, rng, 0.03, 0.0, 0.97, init=0.5)
        H = Hs & sel[:, None]
        Pl = H[:, :, None] & (rng.random((nA, nB, N_PLANT)) < q_host)
    elif kind == "W_egr":
        H = _host_chain(pres, dob, rng, 0.005, rho, 0.85, init=0.1)
        Pl = H[:, :, None] & (rng.random((nA, nB, N_PLANT)) < q_host)
    elif kind == "W_egr3":          # three independent planted memeplexes (P1 power)
        Hs = [_host_chain(pres, dob, rng, 0.005, rho, 0.85, init=0.1) for _ in range(3)]
        Pl = np.concatenate([h[:, :, None] & (rng.random((nA, nB, N_PLANT)) < q_host) for h in Hs], 2)
        H = np.stack(Hs)
    else:
        raise ValueError(kind)
    Pl &= pres[:, :, None]
    nP = Pl.shape[2]
    a, bb, e = np.nonzero(Pl)
    rows.append(a * nB + bb)
    cols.append(e + nE)
    r = np.concatenate(rows)
    c = np.concatenate(cols)
    X = sp.csr_matrix((np.ones(len(r), np.float32), (r, c)), shape=(nA * nB, nE + nP))
    X.sum_duplicates()
    planted = [list(range(nE + j, nE + j + N_PLANT)) for j in range(0, nP, N_PLANT)]
    return {"panel": MP.Panel(b, X, nE + nP), "planted": planted[0], "planted_all": planted, "field": fieldv,
            "H_true": H}


# ============================================================================ discovery (variants)
def ppmi_activity(panel, min_co: int = 3, p_edge: float | None = 0.01) -> np.ndarray:
    """PPMI beyond the agent-constant expectation adjusted for agent-bin activity (Amendment A1 candidate):
    E_ef = sum_i w_i c_ie c_if with w_i = sum_b a_ib^2 / (sum_b a_ib)^2, a_ib = distinct elements agent i expresses
    in bin b (the independence model P(x_ieb) = c_ie a_ib / A_i). With a_ib constant this is memeplex.ppmi_graph."""
    return MP.ppmi_graph(panel, min_co, p_edge, activity=True)


def planted_match(communities, planted) -> dict:
    P = set(planted)
    best = {"jaccard": 0.0}
    for c in communities:
        s = set(c["elements"])
        j = len(s & P) / len(s | P)
        if j > best["jaccard"]:
            best = {"jaccard": j, "n_elements": c["n_elements"], "qualifies": c["qualifies"],
                    "hub_free": c["qualifies_hub_free"], "h_K": c["h_K"], "n_hosts": c["n_hosts"]}
    return best


# ============================================================================ host renewal (P2)
def _daily(H, present, dob):
    nd = int(dob.max()) + 1
    Hd = np.zeros((H.shape[0], nd), bool)
    Pd = np.zeros((H.shape[0], nd), bool)
    for d in range(nd):
        sel = dob == d
        Hd[:, d] = H[:, sel].any(1)
        Pd[:, d] = present[:, sel].any(1)
    return Hd, Pd


def renewal(panel, K, m: int = 2, k: int = 5) -> dict:
    """As written (card P2): rho_K(k) = autocorrelation of daily prevalence, J_K(k) = host-set Jaccard across
    adjacent k-day windows, diff = rho - J. Amendment A4: the renewal contrast D_K(k) = S_K(k) - S_H(k), where
    S_K(k) = share of days d with >= 1 host for which day d+k also has >= 1 host (pattern survival) and
    S_H(k) = share of (host i, day d) pairs with i present on day d+k for which i hosts on day d+k (host return).
    A pattern carried by the same agents has S_H ~ S_K (D ~ 0); a pattern that survives while hosts turn over has
    S_H < S_K."""
    H, _ = MP.host_matrix(panel, K, m)
    b = panel.bins
    prev = MP.daily_prevalence(H, b.present, b.day_of_bin)
    rho = MP.autocorr(prev, k)
    J = MP.jaccard_renewal(H, b.day_of_bin, k)
    Hd, Pd = _daily(H, b.present, b.day_of_bin)
    nd = Hd.shape[1]
    alive = Hd.any(0)
    SK = float(alive[k:][alive[:-k]].mean()) if alive[:-k].any() else np.nan
    src = Hd[:, :-k] & Pd[:, k:]
    SH = float(Hd[:, k:][src].mean()) if src.any() else np.nan
    return {"rho": rho, "J": J, "diff": (rho - J) if np.isfinite(rho) and np.isfinite(J) else np.nan,
            "S_K": SK, "S_H": SH, "D": (SK - SH) if np.isfinite(SK) and np.isfinite(SH) else np.nan}


def _jaccard_days(Hd: np.ndarray, k: int) -> float:
    """J(k) from a daily host matrix [nA, nd] (as memeplex.jaccard_renewal, vectorized over days)."""
    nd = Hd.shape[1]
    if nd < 2 * k + 1:
        return np.nan
    cs = np.concatenate([np.zeros((Hd.shape[0], 1), int), np.cumsum(Hd, 1)], 1)
    d = np.arange(k - 1, nd - k)
    a = (cs[:, d + 1] - cs[:, d - k + 1]) > 0
    b = (cs[:, d + k + 1] - cs[:, d + 1]) > 0
    inter, uni = (a & b).sum(0), (a | b).sum(0)
    ok = a.any(0) & b.any(0)
    return float((inter[ok] / uni[ok]).mean()) if ok.any() else np.nan


def host_memory(panel, K, m: int = 2, k: int = 5, H=None) -> float:
    """Amendment A4 candidate: host memory phi_K(k) = the correlation, over (agent i, day d) with i present on d and
    d+k, between "i hosts K on d" and "i hosts K on d+k". ~0 when hosts are drawn afresh (renewal); high when the
    same agents carry the pattern (sticky hosts, a hub, one lab)."""
    if H is None:
        H, _ = MP.host_matrix(panel, K, m)
    b = panel.bins
    Hd, Pd = _daily(H, b.present, b.day_of_bin)
    sel = Pd[:, :-k] & Pd[:, k:]
    x = Hd[:, :-k][sel].astype(float)
    y = Hd[:, k:][sel].astype(float)
    if len(x) < 10 or x.std() == 0 or y.std() == 0:
        return np.nan
    return float(np.corrcoef(x, y)[0, 1])


def internal_strength(W: np.ndarray, K) -> float:
    """Mean PPMI weight over K's internal element pairs (zeros included)."""
    K = np.asarray(K)
    if len(K) < 2:
        return 0.0
    sub = W[np.ix_(K, K)]
    return float(sub[np.triu_indices(len(K), 1)].mean())


# ============================================================================ pseudo-patterns
@dataclass
class ElementStats:
    freq: np.ndarray           # expressed agent-bins per element (present only)
    nag: np.ndarray            # agents expressing the element


def element_stats(panel) -> ElementStats:
    pr = panel.present_rows()
    Y = panel.binary()[pr]
    freq = np.asarray(Y.sum(0)).ravel()
    agent_of = pr // panel.bins.nB
    C = Y.tocoo()
    pairs = np.unique(agent_of[C.row].astype(np.int64) * panel.nE + C.col)
    nag = np.bincount(pairs % panel.nE, minlength=panel.nE)
    return ElementStats(freq, nag)


def matched_pool(es: ElementStats, K, tol_f=0.25, tol_h=1, min_pool=5) -> list:
    """For each element of K: the elements (not in K) within +-25% frequency and +-1 host count; widened to the
    min_pool nearest (by |log freq| + |host diff|/5) when fewer match."""
    Ks = set(int(e) for e in K)
    out = []
    lf = np.log(np.maximum(es.freq, 1))
    for e in K:
        ok = (np.abs(es.freq - es.freq[e]) <= tol_f * es.freq[e]) & (np.abs(es.nag - es.nag[e]) <= tol_h) & (es.freq > 0)
        ok[list(Ks)] = False
        idx = np.flatnonzero(ok)
        if len(idx) < min_pool:
            d = np.abs(lf - lf[e]) + np.abs(es.nag - es.nag[e]) / 5.0
            d[list(Ks)] = np.inf
            d[es.freq == 0] = np.inf
            idx = np.argsort(d)[:min_pool]
        out.append(idx)
    return out


def draw_pseudo(pools, rng) -> list:
    """One pseudo-pattern: one element from each pool, without repeats."""
    chosen = []
    for pool in pools:
        cand = pool[~np.isin(pool, chosen)] if chosen else pool
        if len(cand) == 0:
            cand = pool
        chosen.append(int(rng.choice(cand)))
    return chosen


# ============================================================================ environment E and the Krakauer test
@dataclass
class EnvBase:
    """Pattern-independent parts of E at one bin width (computed once)."""
    phase: np.ndarray          # e1: bin_in_day x bookends (int)
    n_phase: int
    exo_any: np.ndarray        # e2 indicator: any human / operator / relayed message in the bin
    exo_vec: np.ndarray | None  # [nB, 32] mean exo vector (white32), zeros where none
    act_all: np.ndarray        # [nB] distinct-element expressions by present agents (all elements)
    act_el: object = None      # [nB, nE] element prevalence (present agents expressing e)
    role_vec: np.ndarray | None = None   # [nA, 32] role-text vector per agent row (unit norm) or None
    kick_vec: np.ndarray | None = None
    M: np.ndarray | None = None          # [nA, nB, 32] mean white32 statement vector per agent-bin (or None)
    Mn: np.ndarray | None = None         # [nA, nB] statement count per agent-bin
    synthetic_field: np.ndarray | None = None


def tertile(x, valid=None) -> np.ndarray:
    x = np.asarray(x, float)
    v = x if valid is None else x[valid]
    if len(v) == 0 or np.all(v == v[0]):
        return np.zeros(len(x), np.int64)
    q = np.quantile(v, [1 / 3, 2 / 3])
    return np.searchsorted(np.unique(q), x, side="right").clip(0, 2)


def env_base_synthetic(panel, field=None, exo_any=None) -> EnvBase:
    b = panel.bins
    bid = b.bin_in_day
    nper = int(bid.max()) + 1
    book = np.array([b.days[d] <= BOOKEND_DAY for d in b.day_of_bin], int)
    phase = bid * 2 + book
    act_el = element_prevalence_all(panel)
    return EnvBase(phase, nper * 2, np.zeros(b.nB, int) if exo_any is None else exo_any, None, act_el.sum(1),
                   act_el=act_el, synthetic_field=field)


def element_prevalence_all(panel) -> np.ndarray:
    """[nB, nE] number of present agents expressing each element in each bin (dense float32)."""
    b = panel.bins
    pr = panel.present_rows()
    C = panel.binary()[pr].tocoo()
    out = np.zeros((b.nB, panel.nE), np.float32)
    np.add.at(out, ((pr[C.row]) % b.nB, C.col), 1.0)
    return out


def pattern_env(eb: EnvBase, panel, K, H: np.ndarray, centroid: np.ndarray | None = None) -> np.ndarray:
    """E design block (one-hot, additive) for pattern K at each bin: e1 phase; e2 exo (none / low / high similarity
    to K's centroid, or the indicator alone); e3 role-text field tertile; e4 rest-of-village activity tertile; in
    synthetic worlds with a field, the field tertile replaces e2-e3."""
    nB = len(eb.phase)
    blocks = [IND.onehot(eb.phase, eb.n_phase)]
    if eb.synthetic_field is not None:
        blocks.append(IND.onehot(tertile(eb.synthetic_field), 3))
    else:
        if centroid is not None and eb.exo_vec is not None:
            sim = eb.exo_vec @ centroid
            has = eb.exo_any > 0
            lvl = np.zeros(nB, np.int64)
            if has.any():
                med = np.median(sim[has])
                lvl[has] = 1 + (sim[has] > med)
            blocks.append(IND.onehot(lvl, 3))
        else:
            blocks.append(IND.onehot((eb.exo_any > 0).astype(int), 2))
        if centroid is not None and eb.role_vec is not None:
            rs = eb.role_vec @ centroid                         # [nA]
            pres = panel.bins.present
            r = (pres * rs[:, None]).sum(0) / np.maximum(pres.sum(0), 1)
            blocks.append(IND.onehot(tertile(r), 3))
    # e4: rest of village (expressions outside K by present agents)
    if eb.act_el is not None:
        rest = eb.act_all - eb.act_el[:, np.asarray(K)].sum(1)
    else:
        rest = eb.act_all
    blocks.append(IND.onehot(tertile(rest), 3))
    return np.hstack(blocks)


def pattern_centroid(eb: EnvBase, H: np.ndarray) -> np.ndarray | None:
    """Mean white32 statement vector over K's host agent-bins (unit norm); None without vectors."""
    if eb.M is None:
        return None
    w = (H * eb.Mn)
    if w.sum() == 0:
        return None
    c = (eb.M * w[:, :, None]).sum((0, 1)) / w.sum()
    n = np.linalg.norm(c)
    return c / n if n > 0 else None


@dataclass
class KStats:
    A: float
    A_star: float
    nC: float
    NTIC: float
    Delta: float
    n: int


def krakauer_pattern(panel, K, eb: EnvBase, m: int = 2, lam: float = 1.0, with_delta: bool = True,
                     cross_day: bool = False) -> KStats | None:
    """Pattern-level Krakauer quantities for K at the panel's width. Transitions within days (cross_day=True for
    1-day bins: consecutive days). S = memeplex.pattern_state symbols (compacted); E = pattern_env (lagged: E at b
    predicts S at b+1 with S at b); parts for Delta = the elements' own prevalences s_e(b) (standardized, additive)."""
    ps = MP.pattern_state(panel, K, m)
    b = panel.bins
    sym = ps["sym"]
    if cross_day:
        b0 = np.arange(b.nB - 1)
    else:
        b0 = IND.transitions(b.day_of_bin)
    if len(b0) < 20:
        return None
    (yn, yc), C = IND.compact_states(sym[b0 + 1], sym[b0])
    if C < 2:
        return None
    day = b.day_of_bin[b0 + 1]
    cen = pattern_centroid(eb, ps["H"])
    Eb = pattern_env(eb, panel, K, ps["H"], cen)[b0]
    Sc = IND.onehot(yc, C)
    kd = IND.krakauer_logit(yn, Sc, Eb, day, C, lam)
    if not kd.get("ok"):
        return None
    D = np.nan
    if with_delta:
        prev = eb.act_el[:, np.asarray(K)] if eb.act_el is not None else MP.element_prevalence(panel, K)
        parts = prev[b0].astype(float)
        sd = parts.std(0)
        parts = (parts - parts.mean(0)) / np.where(sd > 0, sd, 1)
        dl = IND.delta_integration(yn, Sc, parts, Eb, day, C, lam, L_SE=kd["loss"]["Lxe"])
        D = dl["Delta"]
    return KStats(kd["A"], kd["A_star"], kd["nC"], kd["NTIC"], D, kd["n"])


# ============================================================================ real-data environment
def env_base_real(panel) -> EnvBase:
    """E inputs for #51 at the panel's width (non-reserved days only, from scheme outputs and shared tables):
    e1 phase = bin_in_day x bookends on; e2 = exogenous messages (human, operator nudges and bookends, relayed human
    input) in the bin and their mean white32 vector; e3 = per-agent role vectors (mean of the agent's role texts; the
    kickoff for agents without one); e4 = element expressions by present agents. M = mean white32 statement vector per
    agent-bin (for pattern centroids)."""
    import polars as pl
    b = panel.bins
    bid = b.bin_in_day
    nper = int(bid.max()) + 1
    book = np.array([b.days[d] <= BOOKEND_DAY for d in b.day_of_bin], int)
    phase = bid * 2 + book
    width = np.timedelta64(b.width_min if b.width_min < 1440 else 8 * 60, "m")

    def bin_of(t):
        t = np.asarray(t).astype("datetime64[us]")
        pos = np.searchsorted(b.t0, t, side="right") - 1
        ok = (pos >= 0) & (t < b.t0[np.clip(pos, 0, None)] + width)
        return np.where(ok, pos, -1)
    exo = pl.read_parquet(OUT / "exo.parquet")
    V = np.load(OUT / "exo_white32.npy")
    bb = bin_of(exo["t"].dt.replace_time_zone(None).to_numpy())
    has = exo["has_vec"].to_numpy()
    exo_any = np.bincount(bb[bb >= 0], minlength=b.nB)
    ev = np.zeros((b.nB, V.shape[1]))
    sel = (bb >= 0) & has
    np.add.at(ev, bb[sel], V[sel])
    nrm = np.linalg.norm(ev, axis=1, keepdims=True)
    ev = np.where(nrm > 0, ev / np.maximum(nrm, 1e-12), 0)
    # role vectors per agent row
    roles = pl.read_parquet(OUT / "roles.parquet")
    Vr = np.load(OUT / "roles_white32.npy")
    Vr = Vr / np.linalg.norm(Vr, axis=1, keepdims=True)
    kick = Vr[(roles["kind"] == "kickoff").to_numpy()][0]
    R = np.tile(kick, (b.nA, 1))
    pos = {a: i for i, a in enumerate(b.agents)}
    for a in set(roles.filter(pl.col("kind") == "agent_goal")["agent"].to_list()):
        if a in pos:
            v = Vr[(roles["agent"] == a).fill_null(False).to_numpy()].mean(0)
            R[pos[a]] = v / np.linalg.norm(v)
    # statement vectors per agent-bin
    st = MP.load_statements(51)
    W32 = np.load(MP.EMB / "statements_white32_bge_small.npy", mmap_mode="r")
    ai, bi = b.locate(st["agent"].to_numpy(), st["t"].dt.replace_time_zone(None).to_numpy())
    ok = (ai >= 0) & (bi >= 0)
    rows = st["srow"].to_numpy()[ok]
    Vs = np.asarray(W32[rows], np.float32)
    M = np.zeros((b.nA, b.nB, Vs.shape[1]), np.float32)
    np.add.at(M, (ai[ok], bi[ok]), Vs)
    Mn = np.zeros((b.nA, b.nB), np.float32)
    np.add.at(Mn, (ai[ok], bi[ok]), 1)
    M = M / np.maximum(Mn, 1)[:, :, None]
    act_el = element_prevalence_all(panel)
    return EnvBase(phase, nper * 2, exo_any, ev, act_el.sum(1), act_el=act_el, role_vec=R, kick_vec=kick, M=M, Mn=Mn)
