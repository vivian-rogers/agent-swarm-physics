"""H115 estimators: additive in/out kinetic Ising per window, sink scores, pair-type model (team blocks).

Conventions (card, Model): J_ij = effect of j's read talk on i's next talk (row = recipient); Ising units
(P(s=+1) = sigmoid(2H)); sink score S_i = sum_j (J_ij - J_ji) over present agents; rank 1 = largest S.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scheme"))
import callspins as CS  # noqa: E402

ROOT = CS.ROOT
DATA = ROOT / "data/processed/H115-debate-judge-role-recovery"
LAM_INT = 0.1      # ridge on intercepts (logit^2)
LAM_NUIS = 1.0     # ridge on self, wake, human terms
MIN_CALLS = 5


def load(period: str):
    d = DATA / period
    calls = pl.read_parquet(d / "calls.parquet")
    XR = np.load(d / "xr.npy")
    XP = np.load(d / "xp.npy")
    agents = json.loads((d / "agents.json").read_text())
    return calls, XR, XP, agents


def present_agents(calls_w: pl.DataFrame, min_calls: int = MIN_CALLS) -> list[int]:
    vc = calls_w.group_by("agent").len()
    return sorted(int(a) for a, n in vc.iter_rows() if n >= min_calls)


def _intercepts(ag, cols_phase, pres):
    """Agent x mode intercepts, plus agent x phase deviations (phases other than the agent's most common)."""
    blocks, names = [], []
    for a in pres:
        m = ag["agent"] == a
        for md in (0, 1):
            mm = m & (ag["mode"] == md)
            if mm.sum() > 0:
                blocks.append(mm.astype(float))
                names.append(f"h_{a}_m{md}")
        if cols_phase is not None:
            ph = cols_phase[m]
            vals, cnt = np.unique(ph, return_counts=True)
            ref = vals[np.argmax(cnt)]
            for v in vals:
                if v == ref:
                    continue
                blocks.append((m & (cols_phase == v)).astype(float))
                names.append(f"ph_{a}_{v}")
    return blocks, names


def additive_design(calls_w: pl.DataFrame, XR_w: np.ndarray, XP_w: np.ndarray, agents: list[int], pres: list[int],
                    phase: np.ndarray | None = None, s_override: np.ndarray | None = None):
    """Rows: calls of present agents. Columns: intercepts | self_a | wake | hum | alpha_a | beta_b | alphaP_a | betaP_b."""
    a_all = calls_w["agent"].to_numpy()
    rows = np.isin(a_all, pres)
    col = {a: agents.index(a) for a in pres}
    XRp = XR_w[rows][:, [col[a] for a in pres]].astype(float)
    XPp = XP_w[rows][:, [col[a] for a in pres]].astype(float)
    ag = {"agent": a_all[rows], "mode": calls_w["mode"].to_numpy()[rows]}
    ph = None if phase is None else phase[rows]
    blocks, names = _intercepts(ag, ph, pres)
    n_int = len(blocks)
    sp = calls_w["sprev"].to_numpy()[rows].astype(float)
    for a in pres:
        blocks.append((ag["agent"] == a) * sp)
        names.append(f"self_{a}")
    blocks.append(calls_w["wake"].to_numpy()[rows].astype(float))
    names.append("wake")
    blocks.append((calls_w["hum"].to_numpy()[rows] > 0).astype(float))
    names.append("hum")
    n_nuis = len(blocks) - n_int
    A = len(pres)
    selfmask = np.zeros_like(XRp)
    for q, a in enumerate(pres):
        selfmask[:, q] = ag["agent"] == a
    XRp = XRp * (1 - selfmask)
    XPp = XPp * (1 - selfmask)
    for X, tag in ((XRp, ""), (XPp, "P")):
        tot = X.sum(1)
        for q, a in enumerate(pres):
            blocks.append((ag["agent"] == a) * tot)
            names.append(f"alpha{tag}_{a}")
        for q, a in enumerate(pres):
            blocks.append(X[:, q])
            names.append(f"beta{tag}_{a}")
    D = np.column_stack(blocks)
    s = calls_w["s"].to_numpy()[rows] if s_override is None else s_override[rows]
    y = (s > 0).astype(float)
    return D, y, names, n_int, n_nuis, A


def fit_additive(calls_w, XR_w, XP_w, agents, pres, lam: float, phase=None, s_override=None):
    D, y, names, n_int, n_nuis, A = additive_design(calls_w, XR_w, XP_w, agents, pres, phase, s_override)
    lamv = np.r_[np.full(n_int, LAM_INT), np.full(n_nuis, LAM_NUIS), np.full(4 * A, lam)]
    b, _ = CS.fit_logit(D, y, lamv)
    o = n_int + n_nuis
    al, be, alP, beP = (b[o + k * A: o + (k + 1) * A] / 2 for k in range(4))   # Ising units
    return {"pres": pres, "alpha": al, "beta": be, "alphaP": alP, "betaP": beP, "n": int(len(y)),
            "S": sink(al, be), "SP": sink(alP, beP)}


def sink(al: np.ndarray, be: np.ndarray) -> np.ndarray:
    A = len(al)
    J = al[:, None] + be[None, :]
    np.fill_diagonal(J, 0.0)
    return J.sum(1) - J.sum(0)


def ranks_desc(S: np.ndarray) -> np.ndarray:
    """Rank 1 = largest; ties broken by order (none expected for continuous S)."""
    order = np.argsort(-S, kind="stable")
    r = np.empty(len(S), dtype=int)
    r[order] = np.arange(1, len(S) + 1)
    return r


# ============================================================================ pair-type model (P2, after unblinding)
TYPES = ["ST", "OT", "JD", "DJ", "B"]


def pair_type(i, j, judge, gov, opp):
    if i == judge and (j in gov or j in opp):
        return "JD"
    if j == judge and (i in gov or i in opp):
        return "DJ"
    if (i in gov and j in gov) or (i in opp and j in opp):
        return "ST"
    if (i in gov and j in opp) or (i in opp and j in gov):
        return "OT"
    return "B"


def pairtype_design(windows: list, agents: list[int], with_phase_split: bool = False):
    """windows: list of dicts {calls, XR, XP, pres, judge, gov, opp, phase, wid}. Intercepts per agent x window x
    phase and agent x mode; coupling columns = number of read senders of each pair type (and in-flight)."""
    blocks_all, ys = [], []
    names = None
    nwin = len(windows)
    for wi, w in enumerate(windows):
        c = w["calls"]
        a_all = c["agent"].to_numpy()
        rows = np.isin(a_all, w["pres"])
        a = a_all[rows]
        ph = w["phase"][rows]
        md = c["mode"].to_numpy()[rows]
        XR = w["XR"][rows]
        XP = w["XP"][rows]
        cols = []
        nm = []
        # intercepts are added later as sparse-ish indicator blocks (agent x window x phase)
        typ_R = {t: np.zeros(rows.sum()) for t in TYPES}
        typ_P = {t: np.zeros(rows.sum()) for t in TYPES}
        for j in w["pres"]:
            q = agents.index(j)
            for i in w["pres"]:
                if i == j:
                    continue
                t = pair_type(i, j, w["judge"], w["gov"], w["opp"])
                m = a == i
                typ_R[t][m] += XR[m, q]
                typ_P[t][m] += XP[m, q]
        phases = ["all"] if not with_phase_split else ["pre", "deb", "post"]
        for t in TYPES:
            for p in phases:
                pm = np.ones(rows.sum(), bool) if p == "all" else (ph == p)
                cols.append(typ_R[t] * pm)
                nm.append(f"R_{t}_{p}")
        for t in TYPES:
            for p in phases:
                pm = np.ones(rows.sum(), bool) if p == "all" else (ph == p)
                cols.append(typ_P[t] * pm)
                nm.append(f"P_{t}_{p}")
        sp = c["sprev"].to_numpy()[rows].astype(float)
        cols += [sp, c["wake"].to_numpy()[rows].astype(float), (c["hum"].to_numpy()[rows] > 0).astype(float)]
        nm += ["self", "wake", "hum"]
        blocks_all.append((np.column_stack(cols), a, ph, md, wi))
        ys.append((c["s"].to_numpy()[rows] > 0).astype(float))
        names = nm
    # intercepts: agent x window x phase, plus agent x mode (cu)
    keys = sorted({(int(ai), wi, str(p)) for (_, a, ph, md, wi) in blocks_all for ai, p in zip(a, ph)})
    kidx = {k: q for q, k in enumerate(keys)}
    agm = sorted({int(ai) for (_, a, _, _, _) in blocks_all for ai in a})
    nrow = sum(len(b[1]) for b in blocks_all)
    Iint = np.zeros((nrow, len(keys) + len(agm)))
    r0 = 0
    for (X, a, ph, md, wi) in blocks_all:
        for k in range(len(a)):
            Iint[r0 + k, kidx[(int(a[k]), wi, str(ph[k]))]] = 1
            if md[k] == 1:
                Iint[r0 + k, len(keys) + agm.index(int(a[k]))] = 1
        r0 += len(a)
    Xc = np.vstack([b[0] for b in blocks_all])
    D = np.column_stack([Iint, Xc])
    y = np.concatenate(ys)
    return D, y, names, Iint.shape[1]


def fit_pairtype(windows, agents, lam: float, with_phase_split=False, se=True):
    D, y, names, n_int = pairtype_design(windows, agents, with_phase_split)
    lamv = np.r_[np.full(n_int, LAM_INT), np.full(D.shape[1] - n_int, lam)]
    for k, nm in enumerate(names):
        if nm in ("self", "wake", "hum"):
            lamv[n_int + k] = LAM_NUIS
    b, cov = CS.fit_logit(D, y, lamv, se=se)
    coef = {nm: b[n_int + k] / 2 for k, nm in enumerate(names)}
    sev = {nm: (np.sqrt(cov[n_int + k, n_int + k]) / 2 if cov is not None else np.nan) for k, nm in enumerate(names)}
    covc = None if cov is None else cov[n_int:, n_int:] / 4
    return {"coef": coef, "se": sev, "names": names, "cov": covc, "n": int(len(y))}


def contrast(fit, a: str, b: str):
    k1, k2 = fit["names"].index(a), fit["names"].index(b)
    est = fit["coef"][a] - fit["coef"][b]
    v = fit["cov"][k1, k1] + fit["cov"][k2, k2] - 2 * fit["cov"][k1, k2]
    return float(est), float(np.sqrt(max(v, 0)))


# ============================================================================ variants
def fit_fullJ(calls_w, XR_w, XP_w, agents, pres, lam: float, phase=None, s_override=None):
    """Full J variant: one coefficient per ordered pair (recipient i, sender j) for read and in-flight inputs."""
    a_all = calls_w["agent"].to_numpy()
    rows = np.isin(a_all, pres)
    ag = {"agent": a_all[rows], "mode": calls_w["mode"].to_numpy()[rows]}
    ph = None if phase is None else phase[rows]
    blocks, names = _intercepts(ag, ph, pres)
    n_int = len(blocks)
    sp = calls_w["sprev"].to_numpy()[rows].astype(float)
    for a in pres:
        blocks.append((ag["agent"] == a) * sp)
    blocks.append(calls_w["wake"].to_numpy()[rows].astype(float))
    blocks.append((calls_w["hum"].to_numpy()[rows] > 0).astype(float))
    n_nuis = len(blocks) - n_int
    A = len(pres)
    pairs = [(i, j) for i in range(A) for j in range(A) if i != j]
    for X0 in (XR_w, XP_w):
        X = X0[rows].astype(float)
        for (i, j) in pairs:
            blocks.append((ag["agent"] == pres[i]) * X[:, agents.index(pres[j])])
    D = np.column_stack(blocks)
    s = calls_w["s"].to_numpy()[rows] if s_override is None else s_override[rows]
    y = (s > 0).astype(float)
    lamv = np.r_[np.full(n_int, LAM_INT), np.full(n_nuis, LAM_NUIS), np.full(2 * len(pairs), lam)]
    b, _ = CS.fit_logit(D, y, lamv)
    o = n_int + n_nuis
    J = np.zeros((A, A))
    JP = np.zeros((A, A))
    for k, (i, j) in enumerate(pairs):
        J[i, j] = b[o + k] / 2
        JP[i, j] = b[o + len(pairs) + k] / 2
    return {"pres": pres, "J": J, "JP": JP, "S": J.sum(1) - J.sum(0), "SP": JP.sum(1) - JP.sum(0), "n": int(len(y))}


def chat_clock(calls: pl.DataFrame, XR: np.ndarray):
    """H67-R1 regime-I clock: keep chat-mode calls; reads at a chat-mode call = OR of the reads of the agent's calls
    since (and excluding) its previous chat-mode call on the same day, including the chat call itself."""
    a = calls["agent"].to_numpy()
    md = calls["mode"].to_numpy()
    d = calls["pt_date"].to_numpy()
    XRc = XR.copy()
    acc: dict = {}
    for k in range(calls.height):
        key = (a[k], d[k])
        cur = acc.get(key)
        cur = XR[k].copy() if cur is None else (cur | XR[k])
        if md[k] == 0:
            XRc[k] = cur
            acc[key] = None
        else:
            acc[key] = cur
    return md == 0, XRc
