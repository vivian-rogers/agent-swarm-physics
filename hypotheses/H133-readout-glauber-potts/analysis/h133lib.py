"""H133 library: risk-set skeletons, the read-out Glauber Potts conditional logit, the background cloglog, and nulls.

Skeleton (per unit, from scheme/build.py outputs): every risk call c (agent's carried label known) with its full option
set = projects touched by anyone in the unit in the last 4 active hours before t_call(c), minus the current project.
Per option row: x = [ln(1+N_nam), ln(1+N_un), ln(1+N_if), held_before, share] (+ lag-1 and lab-split variants).
Per call: agent, ln(1+d) (dwell in own calls), span, hour of day, previous call kind, timer-wake flag, the observed
outcome (stay, an option row, or a hop to a project outside the option set = "birth", dropped from the logit).

Conditional logit (Glauber heat bath): P(stay) and P(b) proportional to exp(u_stay) and exp(u_b), with
  u_stay = alpha_agent + phi ln(1+d);  u_b = kappa_{b,h} + x_b . beta,
kappa a project x active-hour fixed effect. Cells (b, h) with no chosen row drop out (their kappa -> -inf: exact
conditional-MLE limit); calls left with no option drop out. Fit: damped Newton on the sparse Hessian with a small
ridge (1e-3) on alpha and kappa (one direction is not identified). Inference: agent-cluster sandwich (t, G - 1 df) and
agent-block bootstrap. A read term enters only with >= 5 chosen rows having x > 0 (Known issue H11 r2); otherwise NA.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import polars as pl
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from scipy import stats

ROOT = Path(__file__).resolve().parents[3]
D = ROOT / "data/processed/H133-readout-glauber-potts"
WIN_S = 4 * 3600.0
FEATS = ["nam", "un", "if", "held", "share"]
READ_TERMS = ("nam", "un", "if")
MIN_CHOSEN = 5
RIDGE = 1e-3


# ============================================================================================ skeleton
@dataclass
class Skel:
    unit: str
    n_calls: int
    agent: np.ndarray        # (C,) int agent index 0..A-1
    agents: list
    lnd: np.ndarray          # (C,) ln(1+d)
    span: np.ndarray         # (C,) seconds (nan if null)
    hod: np.ndarray          # (C,) UTC hour
    prev_kind: np.ndarray    # (C,) int code
    timer: np.ndarray        # (C,) bool
    first4h: np.ndarray      # (C,) bool (first 4 active hours of the goal period)
    bg: np.ndarray           # (C,) bool: no read at c about a project other than cur
    a: np.ndarray            # (C,) active seconds
    h: np.ndarray            # (C,) active hour
    t: np.ndarray            # (C,) t_call epoch seconds
    hop_any: np.ndarray      # (C,) bool: observed hop (incl. births)
    y: np.ndarray            # (C,) observed chosen option row (global row idx), -1 stay, -2 birth hop
    row_call: np.ndarray     # (R,) call index of option row
    row_proj: np.ndarray     # (R,) project code
    row_cell: np.ndarray     # (R,) cell code (proj, h)
    X: dict = field(default_factory=dict)   # feature name -> (R,) float
    projects: list = field(default_factory=list)
    kinds: list = field(default_factory=list)
    turn: np.ndarray | None = None
    dst_code: np.ndarray | None = None      # (C,) destination project code of observed hops (-1 none, includes births)
    cur_code: np.ndarray | None = None


def _share_counts(lab: pl.DataFrame, pidx: dict):
    """Per project: sorted segment starts / ends (agent on project, within a PT day) for step-count lookups."""
    lab = lab.sort("agent", "t_call", "turn_id").with_columns(pl.col("t_call").dt.epoch("ms").truediv(1000).alias("ts"))
    segs = {}
    alls = ([], [])
    for (ag, day), d in lab.group_by(["agent", "pt_date"], maintain_order=True):
        ts = d["ts"].to_numpy()
        ls = d["label"].to_list()
        last_t = ts[-1]
        cur, st = None, None
        for k in range(len(ts)):
            if ls[k] != cur:
                if cur is not None:
                    segs.setdefault(cur, ([], []))
                    segs[cur][0].append(st)
                    segs[cur][1].append(ts[k])
                    alls[0].append(st)
                    alls[1].append(ts[k])
                cur, st = ls[k], ts[k]
        if cur is not None:
            segs.setdefault(cur, ([], []))
            segs[cur][0].append(st)
            segs[cur][1].append(last_t + 1e-3)
            alls[0].append(st)
            alls[1].append(last_t + 1e-3)
    out = {}
    for p, (s, e) in segs.items():
        if p is None or p not in pidx:
            continue
        out[pidx[p]] = (np.sort(np.array(s)), np.sort(np.array(e)))
    return out, (np.sort(np.array(alls[0])), np.sort(np.array(alls[1])))


def load_skeleton(unit: str, lag1: bool = False, labsplit: bool = False, root: Path | None = None) -> Skel:
    u = (root or D) / unit
    c = pl.read_parquet(u / "calls.parquet").sort("t_call", "turn_id")
    rd = pl.read_parquet(u / "reads.parquet")
    tc = pl.read_parquet(u / "touches.parquet")
    lab = pl.read_parquet(u / "labels.parquet")
    lab = lab.filter(pl.col("label").is_not_null())
    projects = sorted(set(tc["p"].to_list()) | set(c["cur"].to_list()) | set(c["dst"].drop_nulls().to_list()))
    pidx = {p: i for i, p in enumerate(projects)}
    C = c.height
    agents = sorted(c["agent"].unique().to_list())
    aidx = {a: i for i, a in enumerate(agents)}
    a = c["a"].to_numpy().astype(float)
    a = np.where(np.isnan(a), np.nanmax(a) if np.isfinite(np.nanmax(a)) else 0.0, a)
    cur = np.array([pidx[p] for p in c["cur"].to_list()])
    # active projects per call: last touch strictly before a_c within WIN_S
    tch = tc.sort("a")
    rows_c, rows_p = [], []
    for p, d in tch.group_by("p"):
        tp = np.sort(d["a"].to_numpy().astype(float))
        k = np.searchsorted(tp, a, side="left") - 1
        ok = (k >= 0)
        last = np.where(ok, tp[np.clip(k, 0, None)], -np.inf)
        act = ok & ((a - last) <= WIN_S)
        pi = pidx[p[0] if isinstance(p, tuple) else p]
        idx = np.nonzero(act & (cur != pi))[0]
        rows_c.append(idx)
        rows_p.append(np.full(idx.size, pi))
    row_call = np.concatenate(rows_c) if rows_c else np.zeros(0, int)
    row_proj = np.concatenate(rows_p) if rows_p else np.zeros(0, int)
    o = np.lexsort((row_proj, row_call))
    row_call, row_proj = row_call[o].astype(np.int64), row_proj[o].astype(np.int64)
    h = c["h"].to_numpy().astype(np.int64)
    row_cell = row_proj * (int(h.max()) + 1) + h[row_call]
    R = row_call.size
    # reads
    turn = c["turn_id"].to_numpy()
    tix = {t: i for i, t in enumerate(turn.tolist())}
    rkey = row_call * len(projects) + row_proj
    order = np.argsort(rkey)
    rks = rkey[order]
    X = {f: np.zeros(R) for f in FEATS}
    extra = []
    if lag1:
        extra += ["nam_l1", "un_l1"]
    if labsplit:
        extra += ["nam_same", "nam_cross"]
    for f in extra:
        X[f] = np.zeros(R)
    rd = rd.filter(pl.col("p").is_in(projects) & pl.col("turn_id").is_in(turn.tolist()))
    if rd.height:
        ci = np.array([tix[t] for t in rd["turn_id"].to_list()])
        pi = np.array([pidx[p] for p in rd["p"].to_list()])
        k = ci * len(projects) + pi
        pos = np.searchsorted(rks, k)
        hit = (pos < R) & (rks[np.clip(pos, 0, R - 1)] == k)
        ridx = order[np.clip(pos, 0, R - 1)][hit]
        for f, col in (("nam", "n_nam"), ("un", "n_un"), ("if", "n_if"), ("nam_l1", "n_nam_l1"), ("un_l1", "n_un_l1"),
                       ("nam_same", "n_nam_same"), ("nam_cross", "n_nam_cross")):
            if f in X:
                X[f][ridx] = np.log1p(rd[col].to_numpy()[hit].astype(float))
    # held before: first time the agent's label was p in the unit
    lab2 = lab.with_columns(pl.col("t_call").dt.epoch("ms").truediv(1000).alias("ts")).group_by("agent", "label").agg(
        pl.col("ts").min().alias("first"))
    fh = {(a_, pidx[p]): f for a_, p, f in lab2.iter_rows() if p in pidx}
    tcall = c["t_call"].dt.epoch("ms").to_numpy() / 1000.0
    ag_raw = c["agent"].to_numpy()
    held = np.array([fh.get((ag_raw[rc], rp), np.inf) < tcall[rc] for rc, rp in zip(row_call.tolist(), row_proj.tolist())],
                    dtype=float) if R else np.zeros(0)
    X["held"] = held
    # share of other present agents on b at t_call
    segs, (sa, ea) = _share_counts(lab, pidx)
    tr = tcall[row_call]
    nall = (np.searchsorted(sa, tcall, "right") - np.searchsorted(ea, tcall, "right")).astype(float)
    nall_o = np.maximum(nall - 1, 1)
    share = np.zeros(R)
    for p in np.unique(row_proj):
        if p not in segs:
            continue
        m = row_proj == p
        s_, e_ = segs[p]
        share[m] = (np.searchsorted(s_, tr[m], "right") - np.searchsorted(e_, tr[m], "right")) / nall_o[row_call[m]]
    X["share"] = np.clip(share, 0, 1)
    # outcome
    y = np.full(C, -1, dtype=np.int64)
    hop = c["hop"].to_numpy()
    dst = c["dst"].to_list()
    dst_code = np.array([pidx[x] if x is not None else -1 for x in dst])
    start = np.searchsorted(row_call, np.arange(C), "left")
    end = np.searchsorted(row_call, np.arange(C), "right")
    for i in np.nonzero(hop)[0]:
        seg = row_proj[start[i]:end[i]]
        k = np.nonzero(seg == dst_code[i])[0]
        y[i] = start[i] + k[0] if k.size else -2
    kinds = sorted(set(c["prev_kind"].fill_null("none").to_list()))
    kix = {k: i for i, k in enumerate(kinds)}
    span = c["span_s"].to_numpy().astype(float)
    return Skel(unit=unit, n_calls=C, agent=np.array([aidx[x] for x in ag_raw]), agents=agents,
                lnd=np.log1p(np.maximum(c["d"].fill_null(0).to_numpy().astype(float), 0)), span=span,
                hod=c["hod"].to_numpy().astype(int), prev_kind=np.array([kix[k] for k in c["prev_kind"].fill_null("none").to_list()]),
                timer=c["timer_wake"].to_numpy().astype(bool), first4h=c["first4h"].to_numpy().astype(bool),
                bg=~c["any_read_other"].to_numpy().astype(bool), a=a, h=h, t=tcall, hop_any=hop.astype(bool), y=y,
                row_call=row_call, row_proj=row_proj, row_cell=row_cell, X=X, projects=projects, kinds=kinds, turn=turn,
                dst_code=dst_code, cur_code=cur)


# ============================================================================================ conditional logit
@dataclass
class Fit:
    ok: bool
    names: list
    beta: dict
    se: dict
    ci: dict
    cov: np.ndarray | None
    n_calls: int
    n_rows: int
    n_hops: int
    n_cells: int
    G: int
    chosen_pos: dict
    theta: np.ndarray | None = None
    info: dict = field(default_factory=dict)


def restricted_design(sk: Skel, y: np.ndarray, feats: list, call_mask: np.ndarray | None = None):
    """Keep cells with >= 1 chosen row; keep calls with >= 1 kept option; births dropped. Returns a dict design."""
    C = sk.n_calls
    use = np.ones(C, bool) if call_mask is None else call_mask.copy()
    use &= y != -2
    chosen = y[(y >= 0) & use]
    cells_hit = np.unique(sk.row_cell[chosen])
    keep = np.isin(sk.row_cell, cells_hit) & use[sk.row_call]
    ridx = np.nonzero(keep)[0]
    has = np.zeros(C, bool)
    has[sk.row_call[ridx]] = True
    calls = np.nonzero(has & use)[0]
    return {"ridx": ridx, "calls": calls, "y": y, "feats": feats}


def _build(sk: Skel, des: dict, agent_map: np.ndarray | None = None, xover: dict | None = None):
    """Unified rows: per call, a stay row then its option rows. Returns sparse Z, call ids, chosen flags, groups."""
    ridx, calls, y, feats = des["ridx"], des["calls"], des["y"], des["feats"]
    callpos = -np.ones(sk.n_calls, np.int64)
    callpos[calls] = np.arange(calls.size)
    rc = callpos[sk.row_call[ridx]]
    o = np.argsort(rc, kind="stable")
    ridx, rc = ridx[o], rc[o]
    nC, nR = calls.size, ridx.size
    ag = sk.agent[calls] if agent_map is None else agent_map
    A = int(ag.max()) + 1 if nC else 0
    cells, cell_ix = np.unique(sk.row_cell[ridx], return_inverse=True)
    K = cells.size
    k = len(feats)
    # parameter layout: [beta (k), phi, alpha (A), kappa (K)]
    P = k + 1 + A + K
    # rows: stay rows 0..nC-1, option rows nC..nC+nR-1
    st_r = np.repeat(np.arange(nC), 2)
    st_c = np.column_stack([np.full(nC, k), k + 1 + ag]).ravel()
    st_v = np.column_stack([sk.lnd[calls], np.ones(nC)]).ravel()
    xs = []
    for f in feats:
        v = (xover or {}).get(f)
        xs.append((v if v is not None else sk.X[f])[ridx])
    Xr = np.column_stack(xs) if k else np.zeros((nR, 0))
    op_r = np.repeat(nC + np.arange(nR), k + 1)
    op_c = np.column_stack([np.tile(np.arange(k), (nR, 1)), (k + 1 + A + cell_ix)[:, None]]).ravel()
    op_v = np.column_stack([Xr, np.ones(nR)]).ravel()
    Z = sp.csr_matrix((np.concatenate([st_v, op_v]), (np.concatenate([st_r, op_r]), np.concatenate([st_c, op_c]))),
                      shape=(nC + nR, P))
    row_callpos = np.concatenate([np.arange(nC), rc])
    chosen = np.zeros(nC + nR)
    yy = y[calls]
    stay = yy == -1
    chosen[np.arange(nC)[stay]] = 1
    # option chosen: map global row idx -> position
    pos = -np.ones(sk.row_call.size, np.int64)
    pos[ridx] = nC + np.arange(nR)
    ch = yy[~stay]
    chosen[pos[ch]] = 1
    Gm = sp.csr_matrix((np.ones(nC + nR), (row_callpos, np.arange(nC + nR))), shape=(nC, nC + nR))
    reg = np.zeros(P)
    reg[k + 1:] = RIDGE
    return {"Z": Z, "Gm": Gm, "rcp": row_callpos, "chosen": chosen, "ag": ag, "A": A, "K": K, "P": P, "k": k, "nC": nC,
            "nR": nR, "reg": reg, "Xr": Xr, "ridx": ridx}


def _probs(Z, Gm, rcp, theta, nC):
    u = Z @ theta
    mx = np.full(nC, -np.inf)
    np.maximum.at(mx, rcp, u)
    e = np.exp(u - mx[rcp])
    den = Gm @ e
    p = e / den[rcp]
    return p, u, mx, den


def newton(B: dict, theta0: np.ndarray | None = None, tol: float = 1e-7, max_iter: int = 60):
    Z, Gm, rcp, y, reg, nC = B["Z"], B["Gm"], B["rcp"], B["chosen"], B["reg"], B["nC"]
    P = B["P"]
    th = np.zeros(P) if theta0 is None else theta0.copy()

    def obj(t):
        u = Z @ t
        mx = np.full(nC, -np.inf)
        np.maximum.at(mx, rcp, u)
        lse = mx + np.log(Gm @ np.exp(u - mx[rcp]))
        return float(y @ u - lse.sum() - 0.5 * np.sum(reg * t * t))

    f = obj(th)
    for it in range(max_iter):
        u = Z @ th
        mx = np.full(nC, -np.inf)
        np.maximum.at(mx, rcp, u)
        e = np.exp(u - mx[rcp])
        p = e / (Gm @ e)[rcp]
        g = Z.T @ (y - p) - reg * th
        Zp = sp.diags(p) @ Z
        M = Gm @ Zp
        H = (Z.T @ Zp - M.T @ M + sp.diags(reg)).tocsc()
        try:
            step = spla.spsolve(H, g)
        except Exception:  # noqa: BLE001
            return th, False, it
        if not np.all(np.isfinite(step)):
            return th, False, it
        s = 1.0
        while s > 1e-6:
            tn = th + s * step
            fn = obj(tn)
            if fn >= f - 1e-10:
                break
            s *= 0.5
        dec = fn - f
        th, f = tn, fn
        if abs(dec) < tol * (1 + abs(f)) and np.max(np.abs(s * step[:B["k"] + 1])) < 1e-6:
            return th, True, it + 1
    return th, True, max_iter


def sandwich(B: dict, th: np.ndarray, cluster: np.ndarray):
    """Agent-cluster sandwich covariance of (beta, phi). cluster: (nC,) cluster id per call."""
    Z, Gm, rcp, y, reg, nC = B["Z"], B["Gm"], B["rcp"], B["chosen"], B["reg"], B["nC"]
    u = Z @ th
    mx = np.full(nC, -np.inf)
    np.maximum.at(mx, rcp, u)
    e = np.exp(u - mx[rcp])
    p = e / (Gm @ e)[rcp]
    Zp = sp.diags(p) @ Z
    M = Gm @ Zp
    H = (Z.T @ Zp - M.T @ M + sp.diags(reg)).tocsc()
    gid, ginv = np.unique(cluster, return_inverse=True)
    Gn = gid.size
    Cm = sp.csr_matrix((np.ones(rcp.size), (ginv[rcp], np.arange(rcp.size))), shape=(Gn, rcp.size))
    S = (Cm @ sp.diags(y - p) @ Z).toarray()          # Gn x P
    lu = spla.splu(H)
    Xs = lu.solve(S.T)                                 # P x Gn
    kk = B["k"] + 1
    V = Xs[:kk] @ Xs[:kk].T * (Gn / max(Gn - 1, 1))
    return V, Gn


def fit_logit(sk: Skel, y: np.ndarray | None = None, feats: list | None = None, call_mask=None,
              xover: dict | None = None, theta0=None, min_chosen: int = MIN_CHOSEN, want_theta=False) -> Fit:
    y = sk.y if y is None else y
    feats = list(FEATS if feats is None else feats)
    des = restricted_design(sk, y, feats, call_mask)
    # term eligibility: >= min_chosen chosen rows with x > 0
    ch = y[des["calls"]]
    ch = ch[ch >= 0]
    pos = {}
    for f in list(feats):
        v = ((xover or {}).get(f) if xover else None)
        v = sk.X[f] if v is None else v
        pos[f] = int(np.sum(v[ch] > 0))
    use = [f for f in feats if not (f.startswith(READ_TERMS) and pos[f] < min_chosen) and not (f in ("held", "share") and pos[f] < 1)]
    des["feats"] = use
    n_hops = int(ch.size)
    if n_hops < 5 or des["calls"].size == 0:
        return Fit(False, use, {}, {}, {}, None, int(des["calls"].size), int(des["ridx"].size), n_hops, 0, 0, pos)
    B = _build(sk, des, xover=xover)
    th, ok, it = newton(B, theta0)
    k = B["k"]
    names = use + ["phi"]
    V, Gn = sandwich(B, th, B["ag"])
    se = np.sqrt(np.maximum(np.diag(V), 0))
    tq = stats.t.ppf(0.975, max(Gn - 1, 1))
    beta = {n: float(th[i]) for i, n in enumerate(names)}
    ses = {n: float(se[i]) for i, n in enumerate(names)}
    ci = {n: (beta[n] - tq * ses[n], beta[n] + tq * ses[n]) for n in names}
    fitobj = Fit(ok, names, beta, ses, ci, V, B["nC"], B["nR"], n_hops, B["K"], Gn, pos, th if want_theta else None,
                 {"iters": it, "tq": float(tq)})
    return fitobj


def _subset(sk: Skel, bc: np.ndarray) -> Skel:
    """A skeleton made of calls bc (with repeats), option rows copied, y remapped."""
    start = np.searchsorted(sk.row_call, bc, "left")
    end = np.searchsorted(sk.row_call, bc, "right")
    lens = end - start
    ridx = np.concatenate([np.arange(s, e) for s, e in zip(start, end)]) if bc.size else np.zeros(0, int)
    newcall = np.repeat(np.arange(bc.size), lens)
    offs = np.concatenate([[0], np.cumsum(lens)[:-1]])
    y = np.full(bc.size, -1, np.int64)
    yo = sk.y[bc]
    m = yo >= 0
    y[m] = offs[m] + (yo[m] - start[m])
    y[yo == -2] = -2
    X = {f: v[ridx] for f, v in sk.X.items()}
    return Skel(unit=sk.unit, n_calls=bc.size, agent=sk.agent[bc], agents=sk.agents, lnd=sk.lnd[bc], span=sk.span[bc],
                hod=sk.hod[bc], prev_kind=sk.prev_kind[bc], timer=sk.timer[bc], first4h=sk.first4h[bc], bg=sk.bg[bc],
                a=sk.a[bc], h=sk.h[bc], t=sk.t[bc], hop_any=sk.hop_any[bc], y=y, row_call=newcall,
                row_proj=sk.row_proj[ridx], row_cell=sk.row_cell[ridx], X=X, projects=sk.projects, kinds=sk.kinds)


def _remap_y(sk: Skel, y: np.ndarray, bc: np.ndarray) -> np.ndarray:
    start = np.searchsorted(sk.row_call, bc, "left")
    end = np.searchsorted(sk.row_call, bc, "right")
    lens = end - start
    offs = np.concatenate([[0], np.cumsum(lens)[:-1]])
    yo = y[bc]
    out = np.full(bc.size, -1, np.int64)
    m = yo >= 0
    out[m] = offs[m] + (yo[m] - start[m])
    out[yo == -2] = -2
    return out


def _remap_x(sk: Skel, v: np.ndarray, bc: np.ndarray) -> np.ndarray:
    start = np.searchsorted(sk.row_call, bc, "left")
    end = np.searchsorted(sk.row_call, bc, "right")
    ridx = np.concatenate([np.arange(s, e) for s, e in zip(start, end)])
    return v[ridx]


def bootstrap_fit(sk: Skel, feats: list, n: int, seed: int = 0, y: np.ndarray | None = None) -> dict:
    """Agent-block bootstrap of the logit (resampled agents are distinct agents)."""
    y = sk.y if y is None else y
    rng = np.random.default_rng(seed)
    base = restricted_design(sk, y, feats)
    calls = base["calls"]
    ags = np.unique(sk.agent[calls])
    out = []
    for _ in range(n):
        draw = rng.choice(ags, size=ags.size, replace=True)
        parts, amap = [], []
        for j, a_ in enumerate(draw):
            cc = np.nonzero(sk.agent == a_)[0]
            parts.append(cc)
            amap.append(np.full(cc.size, j))
        bc = np.concatenate(parts)
        am = np.concatenate(amap)
        bsk = _subset(sk, bc)
        bsk.y = _remap_y(sk, y, bc)
        f = fit_logit(bsk, bsk.y, feats, min_chosen=0)
        if f.ok:
            out.append({n_: f.beta.get(n_, np.nan) for n_ in feats + ["phi"]})
        del am
    return {"draws": out}


# ============================================================================================ N1 score permutation
def score_perm(sk: Skel, feats_full: list, n: int = 1000, seed: int = 0) -> dict:
    """N1: permute (N_nam, N_un) jointly across option rows within each project x active-hour cell. Statistic: the score
    for gamma_nam at the fit without the read terms nam and un (p does not depend on them, so no refit per draw)."""
    rest = [f for f in feats_full if f not in ("nam", "un")]
    des = restricted_design(sk, sk.y, rest)
    B = _build(sk, des)
    th, ok, _ = newton(B)
    Z, Gm, rcp, nC = B["Z"], B["Gm"], B["rcp"], B["nC"]
    u = Z @ th
    mx = np.full(nC, -np.inf)
    np.maximum.at(mx, rcp, u)
    e = np.exp(u - mx[rcp])
    p = e / (Gm @ e)[rcp]
    resid = (B["chosen"] - p)[nC:]          # option rows only
    ridx = B["ridx"]
    xn = sk.X["nam"][ridx]
    cells = sk.row_cell[ridx]
    T0 = float(resid @ xn)
    rng = np.random.default_rng(seed)
    o = np.argsort(cells, kind="stable")
    cs = cells[o]
    bounds = np.flatnonzero(np.diff(cs)) + 1
    groups = np.split(o, bounds)
    groups = [g for g in groups if g.size > 1]
    T = np.empty(n)
    for d in range(n):
        xp = xn.copy()
        for g in groups:
            xp[g] = xn[rng.permutation(g)]
        T[d] = resid @ xp
    return {"T_obs": T0, "p_one_sided": float((1 + np.sum(T >= T0)) / (n + 1)), "n_perm": n, "groups": len(groups)}


# ============================================================================================ background cloglog
def fit_cloglog(sk: Skel, hop: np.ndarray, mask: np.ndarray, hod_bins: int = 4, extra: np.ndarray | None = None) -> dict:
    """cloglog P(hop at c) = alpha_agent + eta ln(span) + hour-of-day bins + previous-call kind; agent-cluster sandwich."""
    m = mask & np.isfinite(sk.span) & (sk.span > 0)
    if m.sum() < 50 or hop[m].sum() < 5:
        return {"ok": False, "n": int(m.sum()), "hops": int(hop[m].sum())}
    ag = sk.agent[m]
    agu, agi = np.unique(ag, return_inverse=True)
    hb = (sk.hod[m] * hod_bins) // 24
    hbu, hbi = np.unique(hb, return_inverse=True)
    pk = sk.prev_kind[m]
    pku, pki = np.unique(pk, return_inverse=True)
    cols = [np.log(sk.span[m])]
    if extra is not None:
        cols.append(extra[m])
    Xa = np.zeros((m.sum(), agu.size))
    Xa[np.arange(m.sum()), agi] = 1
    Xh = np.zeros((m.sum(), max(hbu.size - 1, 0)))
    for j in range(1, hbu.size):
        Xh[:, j - 1] = hbi == j
    # previous kind: keep levels with >= 1 hop; others pooled into the reference
    yv = hop[m].astype(float)
    Xk = []
    ref = np.bincount(pki).argmax()
    for j in range(pku.size):
        if j == ref:
            continue
        col = (pki == j).astype(float)
        if yv[col > 0].sum() >= 1 and col.sum() >= 10:
            Xk.append(col)
    nx = len(cols)
    X = np.column_stack([np.array(cols).T, Xa, Xh] + ([np.column_stack(Xk)] if Xk else []))
    # drop agents with no hop (separation): their alpha -> -inf; drop rows
    keep_ag = np.array([yv[agi == j].sum() > 0 for j in range(agu.size)])
    rows = keep_ag[agi]
    X, yv, agc = X[rows], yv[rows], agi[rows]
    colkeep = np.ones(X.shape[1], bool)
    colkeep[nx:nx + agu.size] = keep_ag
    X = X[:, colkeep]
    b = np.zeros(X.shape[1])
    b[nx:nx + keep_ag.sum()] = math.log(max(yv.mean(), 1e-4))

    def nll(b):
        eta = np.clip(X @ b, -30, 5)
        mu = -np.expm1(-np.exp(eta))
        mu = np.clip(mu, 1e-12, 1 - 1e-12)
        return -np.sum(yv * np.log(mu) + (1 - yv) * np.log1p(-mu)) + 1e-6 * b @ b

    f = nll(b)
    for it in range(100):
        eta = np.clip(X @ b, -30, 5)
        ee = np.exp(eta)
        mu = np.clip(-np.expm1(-ee), 1e-12, 1 - 1e-12)
        dmu = ee * np.exp(-ee)
        w = dmu ** 2 / (mu * (1 - mu))
        z = (yv - mu) / dmu
        g = X.T @ (w * z) - 2e-6 * b
        H = X.T @ (X * w[:, None]) + 2e-6 * np.eye(X.shape[1])
        step = np.linalg.solve(H, g)
        s = 1.0
        while s > 1e-6:
            bn = b + s * step
            fn = nll(bn)
            if fn <= f + 1e-10:
                break
            s *= 0.5
        conv = abs(f - fn) < 1e-9 * (1 + abs(f))
        b, f = bn, fn
        if conv:
            break
    eta = np.clip(X @ b, -30, 5)
    ee = np.exp(eta)
    mu = np.clip(-np.expm1(-ee), 1e-12, 1 - 1e-12)
    dmu = ee * np.exp(-ee)
    w = dmu ** 2 / (mu * (1 - mu))
    H = X.T @ (X * w[:, None]) + 2e-6 * np.eye(X.shape[1])
    sc = X * ((yv - mu) / (mu * (1 - mu)) * dmu)[:, None]
    gids = np.unique(agc)
    Sg = np.array([sc[agc == g_].sum(0) for g_ in gids])
    Hi = np.linalg.pinv(H)
    Gn = gids.size
    V = Hi @ (Sg.T @ Sg) @ Hi * (Gn / max(Gn - 1, 1))
    se = float(np.sqrt(max(V[0, 0], 0)))
    tq = stats.t.ppf(0.975, max(Gn - 1, 1))
    return {"ok": True, "eta": float(b[0]), "se": se, "ci": (float(b[0] - tq * se), float(b[0] + tq * se)),
            "n": int(rows.sum()), "hops": int(yv.sum()), "G": int(Gn)}


# ============================================================================================ synthetic worlds
def calibrate_alpha(target: float, us_off: np.ndarray, sk: Skel, lse_opt: np.ndarray) -> float:
    """alpha0 such that mean P(hop) = target; P(hop_c) = 1 / (1 + exp(alpha0 - lse_opt_c))."""
    has = np.isfinite(lse_opt)
    lo, hi = -30.0, 30.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        ph = np.where(has, 1 / (1 + np.exp(mid - np.where(has, lse_opt, 0))), 0.0)
        if ph.mean() > target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def burst_intensity(sk: Skel, msg_t: dict, half_life_s: float = 1800.0) -> np.ndarray:
    """Two-sided exponential kernel sum of all project-linking messages about b around t_call(c), per option row."""
    lam = math.log(2) / half_life_s
    out = np.zeros(sk.row_call.size)
    tr = sk.t[sk.row_call]
    for p in np.unique(sk.row_proj):
        ts = msg_t.get(sk.projects[p])
        if ts is None or len(ts) == 0:
            continue
        ts = np.sort(np.asarray(ts))
        m = sk.row_proj == p
        tt = tr[m]
        # cumulative sums for exp(lam t) and exp(-lam t) relative to a reference to avoid overflow
        ref = ts[0]
        ep = np.exp(lam * np.clip(ts - ref, -1e6, 50 / lam))
        k = np.searchsorted(ts, tt, "right")
        cs_p = np.concatenate([[0], np.cumsum(ep)])
        # past: sum_{t_m <= t} exp(-lam (t - t_m)) = exp(-lam (t-ref)) * sum exp(lam (t_m - ref))
        past = np.exp(-lam * np.clip(tt - ref, -1e6, 50 / lam)) * cs_p[k]
        en = np.exp(-lam * np.clip(ts - ref, -1e6, 50 / lam))
        cs_n = np.concatenate([[0], np.cumsum(en[::-1])])[::-1]
        fut = np.exp(lam * np.clip(tt - ref, -1e6, 50 / lam)) * cs_n[k]
        out[m] = past + fut
    return out


def simulate(sk: Skel, world: str, rng, target: float, kappa_sd: float = 1.0, params: dict | None = None,
             burst: np.ndarray | None = None, dest: bool = True) -> np.ndarray:
    """Draw outcomes per call on the real skeleton. Returns y (row idx, -1 stay); no births."""
    params = params or {}
    R, C = sk.row_call.size, sk.n_calls
    cells, cinv = np.unique(sk.row_cell, return_inverse=True)
    kap = rng.normal(0, kappa_sd, cells.size)[cinv]
    eps = 0.05
    if world in ("W0", "W4"):
        ub = np.log(sk.X["share"] + eps)
    elif world == "W1":
        ub = kap + params.get("g_nam", 1.0) * sk.X["nam"]
    elif world == "W2":
        g = params.get("g", 1.0)
        ub = kap + g * sk.X["nam"] + g * sk.X["un"]
    elif world == "W3":
        ub = kap + params.get("lam", 1.0) * np.log1p(burst)
    elif world == "W5":
        ub = kap + params.get("bJ", 2.0) * sk.X["share"]
    else:
        raise ValueError(world)
    # per-call log-sum-exp over options
    mx = np.full(C, -np.inf)
    np.maximum.at(mx, sk.row_call, ub)
    se = np.zeros(C)
    np.add.at(se, sk.row_call, np.exp(ub - mx[sk.row_call]))
    lse = np.where(se > 0, mx + np.log(np.where(se > 0, se, 1)), -np.inf)
    has = np.isfinite(lse)
    if world == "W0":
        ph = np.where(has, target / max(has.mean(), 1e-9), 0.0)
    elif world == "W4":
        span = np.where(np.isfinite(sk.span) & (sk.span > 0), sk.span, np.nanmedian(sk.span[sk.span > 0]))
        lo, hi = 1e-9, 10.0
        for _ in range(80):
            mid = math.sqrt(lo * hi)
            pm = np.where(has, -np.expm1(-mid * span), 0).mean()
            lo, hi = (mid, hi) if pm < target else (lo, mid)
        ph = np.where(has, -np.expm1(-mid * span), 0.0)
    else:
        a0 = calibrate_alpha(target, None, sk, lse)
        ph = np.where(has, 1 / (1 + np.exp(a0 - np.where(has, lse, 0))), 0.0)
    ph = np.clip(ph, 0, 1)
    hop = rng.random(C) < ph
    y = np.full(C, -1, np.int64)
    if not dest:
        y[hop & has] = 0
        return y
    # destination ~ softmax(ub) within call
    pr = np.exp(ub - mx[sk.row_call])
    starts = np.searchsorted(sk.row_call, np.arange(C), "left")
    ends = np.searchsorted(sk.row_call, np.arange(C), "right")
    for i in np.nonzero(hop & has)[0]:
        w = pr[starts[i]:ends[i]]
        y[i] = starts[i] + rng.choice(w.size, p=w / w.sum())
    return y


# ============================================================================================ pooling
def dersimonian_laird(est, se):
    est, se = np.asarray(est, float), np.asarray(se, float)
    m = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[m], se[m]
    k = est.size
    if k == 0:
        return {"k": 0, "mean": np.nan, "se": np.nan, "ci": (np.nan, np.nan), "tau2": np.nan}
    w = 1 / se ** 2
    mu_f = np.sum(w * est) / w.sum()
    Q = float(np.sum(w * (est - mu_f) ** 2))
    tau2 = max(0.0, (Q - (k - 1)) / (w.sum() - np.sum(w ** 2) / w.sum())) if k > 1 else 0.0
    ws = 1 / (se ** 2 + tau2)
    mu = float(np.sum(ws * est) / ws.sum())
    s = float(math.sqrt(1 / ws.sum()))
    return {"k": int(k), "mean": mu, "se": s, "ci": (mu - 1.96 * s, mu + 1.96 * s), "tau2": float(tau2), "Q": Q}


def n_options(sk: Skel) -> np.ndarray:
    """Per call: ln(1 + number of options) (active projects other than the current one)."""
    return np.log1p(np.bincount(sk.row_call, minlength=sk.n_calls).astype(float))
