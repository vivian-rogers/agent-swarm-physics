"""H116 estimators: winner-focused event model (coupling step), placebo windows, call-clock multipartite EP, role steps.

Conventions (card, Model): J_jw = effect of w's read talk on j's next talk; Ising units (P(s=+1) = sigmoid(2H)).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scheme"))
import callspins as CS  # noqa: E402

ROOT = CS.ROOT
SH = CS.SH
DATA = ROOT / "data/processed/H116-election-coupling-step"
sys.path.insert(0, str(ROOT / "infra/shared"))
import ep_newton as EPN  # noqa: E402

UTC = dt.timezone.utc
LAM_INT = 0.1
LAM_NUIS = 1.0
WINNER = 17
T_STAR = dt.datetime(2026, 1, 5, 19, 35, 22, 589746, tzinfo=UTC)
T_G = dt.datetime(2026, 1, 5, 19, 25, 0, tzinfo=UTC)
T2 = dt.datetime(2026, 1, 9, 19, 0, 43, 77738, tzinfo=UTC)
T2_G = dt.datetime(2026, 1, 9, 18, 45, 0, tzinfo=UTC)
EVENT_DAY = "2026-01-05"
RE_DAY = "2026-01-09"


def load(period: str):
    d = DATA / period
    calls = pl.read_parquet(d / "calls.parquet")
    return calls, np.load(d / "xr.npy"), np.load(d / "xp.npy"), json.loads((d / "agents.json").read_text())


def day_span(calls: pl.DataFrame, day: str):
    """(all-present start, all-present end) of a day from the scheme's trim flag; None if empty."""
    c = calls.filter((pl.col("pt_date") == day) & pl.col("trim"))
    if c.height == 0:
        return None
    return c["t_call"].min(), c["t_call"].max()


def win_start(day: str):
    cal = pl.read_parquet(SH / "calendar.parquet").filter(pl.col("pt_date") == day)
    return cal["win_start"][0]


def event_offsets():
    """Offsets (from the event day's calendar win_start) of the pre start, guard start and event, in seconds."""
    ws = win_start(EVENT_DAY)
    return ws


def windows_at(calls: pl.DataFrame, day: str, T, Tg, t0=None, trim: bool = True):
    """pre = [t0, Tg), post = [T, T + (Tg - t0)); t0 defaults to the day's all-present start. Trimmed calls only,
    unless trim=False (then t0 must be given and the day's calendar window bounds the post side)."""
    if trim:
        sp = day_span(calls, day)
        if sp is None:
            return None
        t0 = sp[0] if t0 is None else max(t0, sp[0])
    else:
        cal = pl.read_parquet(SH / "calendar.parquet").filter(pl.col("pt_date") == day)
        sp = (cal["win_start"][0], cal["win_end"][0])
    L = Tg - t0
    if L.total_seconds() < 20 * 60:
        return None
    t1 = T + L
    if t1 > sp[1] + dt.timedelta(seconds=1):
        return None
    tc = calls["t_call"]
    m_day = (calls["pt_date"] == day) & (calls["trim"] if trim else True)
    pre = (m_day & (tc >= t0) & (tc < Tg)).to_numpy()
    post = (m_day & (tc >= T) & (tc < t1)).to_numpy()
    return pre, post, (t0, Tg, T, t1)


def event_design(calls, XR, XP, agents, w, pre, post, min_calls: int = 5):
    """Winner-focused design (card, Model). Returns D, y, names, n_int, keep-row mask, pres."""
    m = pre | post
    c = calls.filter(pl.Series(m))
    a = c["agent"].to_numpy()
    side = post[m].astype(float)
    pres = []
    for ag in sorted(set(a.tolist())):
        if ((a == ag) & (side == 0)).sum() >= min_calls and ((a == ag) & (side == 1)).sum() >= min_calls:
            pres.append(int(ag))
    if w not in pres:
        return None
    rows = np.isin(a, pres)
    a = a[rows]
    side = side[rows]
    md = c["mode"].to_numpy()[rows]
    col = {q: agents.index(q) for q in pres}
    XRr = XR[m][rows][:, [col[q] for q in pres]].astype(float)
    XPr = XP[m][rows][:, [col[q] for q in pres]].astype(float)
    for q, ag in enumerate(pres):          # no self-reads
        XRr[a == ag, q] = 0
        XPr[a == ag, q] = 0
    wi = pres.index(w)
    isw = (a == w).astype(float)
    rec = 1 - isw
    blocks, names = [], []
    for ag in pres:
        for mm in (0, 1):
            for sd in (0, 1):
                sel = (a == ag) & (md == mm) & (side == sd)
                if sel.sum():
                    blocks.append(sel.astype(float))
                    names.append(f"h_{ag}_{mm}_{sd}")
    n_int = len(blocks)
    sp = c["sprev"].to_numpy()[rows].astype(float)
    for ag in pres:
        blocks.append((a == ag) * sp)
        names.append(f"self_{ag}")
    blocks.append(c["wake"].to_numpy()[rows].astype(float))
    names.append("wake")
    blocks.append((c["hum"].to_numpy()[rows] > 0).astype(float))
    names.append("hum")
    n_nuis = len(blocks) - n_int
    for X, tag in ((XRr, ""), (XPr, "P")):
        xw = X[:, wi] * rec
        xo = (X.sum(1) - X[:, wi]) * rec
        xin = X.sum(1) * isw
        blocks += [xw, xw * side, xo, xo * side, xin, xin * side]
        names += [f"Jout{tag}", f"dJout{tag}", f"Joth{tag}", f"dJoth{tag}", f"Jin{tag}", f"dJin{tag}"]
    D = np.column_stack(blocks)
    y = (c["s"].to_numpy()[rows] > 0).astype(float)
    return D, y, names, n_int, n_nuis, pres


def fit_event(calls, XR, XP, agents, w, pre, post, lam: float, se: bool = True, s_override=None):
    if s_override is not None:
        calls = calls.with_columns(pl.Series("s", s_override))
    r = event_design(calls, XR, XP, agents, w, pre, post)
    if r is None:
        return None
    D, y, names, n_int, n_nuis, pres = r
    lamv = np.r_[np.full(n_int, LAM_INT), np.full(n_nuis, LAM_NUIS), np.full(D.shape[1] - n_int - n_nuis, lam)]
    b, cov = CS.fit_logit(D, y, lamv, se=se)
    o = n_int + n_nuis
    coef = {nm: float(b[o + k] / 2) for k, nm in enumerate(names[o:])}
    sev = {nm: (float(np.sqrt(cov[o + k, o + k]) / 2) if cov is not None else np.nan) for k, nm in enumerate(names[o:])}
    out = {"coef": coef, "se": sev, "n": int(len(y)), "pres": pres,
           "n_exposed_pre": int(D[:, names.index("Jout")][D[:, names.index("dJout")] == 0].sum()),
           "n_exposed_post": int(D[:, names.index("dJout")].sum())}
    out["did"] = coef["dJout"] - coef["dJoth"]
    out["read_minus_inflight"] = coef["dJout"] - coef["dJoutP"]
    if cov is not None:
        k1, k2 = o + names[o:].index("dJout"), o + names[o:].index("dJoutP")
        out["se_read_minus_inflight"] = float(np.sqrt(max(cov[k1, k1] + cov[k2, k2] - 2 * cov[k1, k2], 0)) / 2)
        k3 = o + names[o:].index("dJoth")
        out["se_did"] = float(np.sqrt(max(cov[k1, k1] + cov[k3, k3] - 2 * cov[k1, k3], 0)) / 2)
    return out


# ============================================================================ EP (call-clock multipartite bound)
def ep_multipartite(calls: pl.DataFrame, mask: np.ndarray, pres: list[int], w: int | None = None, block_s: int = 600,
                    s_override=None):
    """Held-out Newton bound (ep_newton_heldout) on g_ij(c) = (s_i(c) - s_i(c-)) s_j(c), ordered pairs of `pres`.
    Folds = 10-min blocks. Returns {"all": sigma, "winner": sigma (pairs with w), "T": n calls}."""
    c = calls.filter(pl.Series(mask)).sort("t_call", "turn_id")
    s = c["s"].to_numpy() if s_override is None else s_override[mask][np.argsort(
        calls.filter(pl.Series(mask))["t_call"].to_numpy(), kind="stable")]
    a = c["agent"].to_numpy()
    tc = c["t_call"].dt.epoch("s").to_numpy()
    day = c["pt_date"].to_numpy()
    A = len(pres)
    idx = {q: k for k, q in enumerate(pres)}
    pairs = [(i, j) for i in range(A) for j in range(A) if i != j]
    pk = {p: k for k, p in enumerate(pairs)}
    state = np.zeros(A)
    G, blk = [], []
    lastday = None
    for k in range(len(a)):
        if day[k] != lastday:
            state[:] = 0
            lastday = day[k]
        if a[k] not in idx:
            continue
        i = idx[a[k]]
        new = float(s[k])
        if state[i] != 0 and (state != 0).all():
            g = np.zeros(len(pairs))
            dlt = new - state[i]
            for j in range(A):
                if j != i:
                    g[pk[(i, j)]] = dlt * state[j]
            G.append(g)
            blk.append(int(tc[k] // block_s))
        state[i] = new
    if len(G) < 20:
        return {"all": np.nan, "winner": np.nan, "T": len(G)}
    G = np.asarray(G)
    blk = np.asarray(blk)
    res = {"all": EPN.ep_newton_heldout(G, blk, k=5)["sigma"], "T": int(len(G))}
    if w is not None and w in idx:
        wi = idx[w]
        cols = [pk[p] for p in pairs if wi in p]
        res["winner"] = EPN.ep_newton_heldout(G[:, cols], blk, k=5)["sigma"]
    return res


# ============================================================================ role steps (replication)
def role_design(windows: list, agents: list[int]):
    """windows: [{calls, XR, XP, pres, lead, wid}] (lead = designated agent or None). Columns: intercepts agent x window
    (x mode), self, wake, hum, beta_a (reads of sender a), dOut (reads of the window's designated agent), alpha_a
    (number of read senders, rows of a), dIn (rows of the designated agent), and the in-flight analogs."""
    rows_all = []
    for w in windows:
        c = w["calls"]
        a_all = c["agent"].to_numpy()
        rows = np.isin(a_all, w["pres"])
        rows_all.append(rows)
    allag = sorted({q for w in windows for q in w["pres"]})
    AA = len(allag)
    keys = sorted({(int(q), w["wid"], int(md)) for w, rows in zip(windows, rows_all)
                   for q, md in zip(w["calls"]["agent"].to_numpy()[rows], w["calls"]["mode"].to_numpy()[rows])})
    kidx = {k: q for q, k in enumerate(keys)}
    parts, ys = [], []
    for w, rows in zip(windows, rows_all):
        c = w["calls"]
        a = c["agent"].to_numpy()[rows]
        md = c["mode"].to_numpy()[rows]
        n = len(a)
        I = np.zeros((n, len(keys)))
        for k in range(n):
            I[k, kidx[(int(a[k]), w["wid"], int(md[k]))]] = 1
        cols = [c["sprev"].to_numpy()[rows].astype(float), c["wake"].to_numpy()[rows].astype(float),
                (c["hum"].to_numpy()[rows] > 0).astype(float)]
        for X0 in (w["XR"], w["XP"]):
            X = np.zeros((n, AA))
            for q in w["pres"]:
                X[:, allag.index(q)] = X0[rows][:, agents.index(q)]
            for q in w["pres"]:
                X[a == q, allag.index(q)] = 0
            beta = X
            lead = w["lead"]
            dout = X[:, allag.index(lead)] if lead is not None and lead in w["pres"] else np.zeros(n)
            tot = X.sum(1)
            alpha = np.column_stack([(a == q) * tot for q in allag])
            din = (a == lead) * tot if lead is not None else np.zeros(n)
            cols += list(beta.T) + [dout] + list(alpha.T) + [din]
        parts.append(np.column_stack([I] + [np.asarray(v)[:, None] if np.ndim(v) == 1 else v for v in cols]))
        ys.append((c["s"].to_numpy()[rows] > 0).astype(float))
    names = ["self", "wake", "hum"]
    for tag in ("", "P"):
        names += [f"beta{tag}_{q}" for q in allag] + [f"dOut{tag}"] + [f"alpha{tag}_{q}" for q in allag] + [f"dIn{tag}"]
    return np.vstack(parts), np.concatenate(ys), names, len(keys)


def fit_role(windows, agents, lam: float, se: bool = False):
    D, y, names, n_int = role_design(windows, agents)
    lamv = np.r_[np.full(n_int, LAM_INT), np.full(3, LAM_NUIS), np.full(D.shape[1] - n_int - 3, lam)]
    b, cov = CS.fit_logit(D, y, lamv, se=se)
    coef = {nm: float(b[n_int + k] / 2) for k, nm in enumerate(names)}
    out = {"dOut": coef["dOut"], "dIn": coef["dIn"], "dOutP": coef["dOutP"], "dInP": coef["dInP"], "n": int(len(y))}
    if cov is not None:
        k = n_int + names.index("dOut")
        out["se_dOut"] = float(np.sqrt(cov[k, k]) / 2)
    return out
