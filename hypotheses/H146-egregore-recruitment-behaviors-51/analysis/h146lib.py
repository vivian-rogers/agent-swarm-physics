"""H146 core: item coding, pattern panels, adoption rows, matched-lag read vs in-flight fits, wipes, repair,
specialization and O-information. Plain numpy / scipy.sparse; single-threaded.

Data: data/processed/H146-egregore-recruitment-behaviors-51/events/ (scheme/build.py). Reserved days are absent
from those tables by construction; `load()` asserts it again.

Element coding interface (`Coding`): a common element index 0..E-1 with
  M_msg   (n_msgs x E, bool CSR)      chat item carries element e
  M_row   (n_talkrows x E, bool CSR)  the talk row's own chat message(s) carry e
  M_ab    (n_agentbins x E, bool CSR) agent expresses e in a 2-h bin (statements + practices)
  ab_agent, ab_bin                    agent and bin of each agent-bin row
Two builders: `coding_candidates` (the post hoc qualitative candidates, regex on text in memory) and
`coding_h145` (H145's element map; see the function).
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import polars as pl
import scipy.sparse as sp

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra" / "shared"))
EV = ROOT / "data" / "processed" / "H146-egregore-recruitment-behaviors-51" / "events"
SH = ROOT / "data" / "processed" / "shared"
US = 1_000_000
BIN_US = 2 * 3600 * US
D1 = "2026-09-04"
HUB = 17  # DeepSeek-V3.2, the loudest sender (W_hub)


# ----------------------------------------------------------------------------------------------------------- data
@dataclass
class Ev:
    msgs: pl.DataFrame
    calls: pl.DataFrame
    stmts: pl.DataFrame
    rows: pl.DataFrame
    win: pl.DataFrame
    reads: pl.DataFrame
    touches: pl.DataFrame
    er: pl.DataFrame
    chg: pl.DataFrame
    newcomers: list
    # derived arrays
    a: dict = field(default_factory=dict)


def load() -> Ev:
    r = lambda n: pl.read_parquet(EV / f"{n}.parquet")  # noqa: E731
    ev = Ev(r("msgs"), r("calls"), r("stmts"), r("talkrows"), r("window_items"), r("reads"), r("touches"),
            r("erasures"), r("challenges"), json.loads((EV / "newcomers.json").read_text()))
    for df in (ev.msgs, ev.calls, ev.stmts, ev.rows, ev.er):
        assert df["pt_date"].max() <= D1, "reserved day present"
    _derive(ev)
    return ev


def _derive(ev: Ev):
    a = ev.a
    a["n_msgs"] = ev.msgs.height
    a["msg_t"] = ev.msgs["t"].to_numpy()
    a["msg_agent"] = ev.msgs["agent"].to_numpy().astype(np.int16)
    a["msg_bin"] = (a["msg_t"] // BIN_US).astype(np.int64)
    R = ev.rows
    a["n_rows"] = R.height
    a["row_agent"] = R["agent"].to_numpy().astype(np.int16)
    a["row_t"] = R["t_call"].to_numpy()
    a["row_bin"] = (a["row_t"] // BIN_US).astype(np.int64)
    days = sorted(set(R["pt_date"].to_list()) | set(ev.stmts["pt_date"].to_list()))
    a["days"] = days
    dix = {d: i for i, d in enumerate(days)}
    a["row_day"] = np.array([dix[d] for d in R["pt_date"].to_list()], dtype=np.int32)
    a["row_hourblock"] = a["row_day"].astype(np.int64) * 100 + ((a["row_t"] // (3600 * US)) % 24)
    a["row_d"] = R["d_s"].to_numpy()
    a["row_before"] = R["before_age_s"].to_numpy()
    a["row_dens"] = R["dens10"].to_numpy().astype(np.float64)
    # window items as CSR (rows x msgs), split by w and named
    W = ev.win
    wr, wm, ww, wn = (W["row"].to_numpy(), W["msg"].to_numpy(), W["w"].to_numpy(), W["named"].to_numpy())
    n, M = a["n_rows"], a["n_msgs"]
    def csr(mask):
        return sp.csr_matrix((np.ones(mask.sum(), dtype=np.float32), (wr[mask], wm[mask])), shape=(n, M))
    a["W_read"] = csr(ww == 0)
    a["W_read_named"] = csr((ww == 0) & wn)
    a["W_read_unnamed"] = csr((ww == 0) & ~wn)
    a["W_fly"] = csr(ww == 1)
    a["W_fly_named"] = csr((ww == 1) & wn)
    a["W_read_nohub"] = csr((ww == 0) & (a["msg_agent"][wm] != HUB))
    a["W_fly_nohub"] = csr((ww == 1) & (a["msg_agent"][wm] != HUB))
    a["A_read"] = np.asarray(a["W_read"].sum(1)).ravel()
    a["A_fly"] = np.asarray(a["W_fly"].sum(1)).ravel()
    # reads: items received at the producing call (t_recv == t_call of the row) and in the previous 2 h
    rd = ev.reads
    ra, rt, rm = rd["agent"].to_numpy(), rd["t_recv"].to_numpy(), rd["msg"].to_numpy()
    a["reads_by_agent"] = {}
    for ag in np.unique(ra):
        s = ra == ag
        o = np.argsort(rt[s], kind="stable")
        a["reads_by_agent"][int(ag)] = (rt[s][o], rm[s][o])
    # read-at-call and read-in-2h CSR (rows x msgs); computed once
    ri, rj, ci, cj = [], [], [], []
    for ag, (tt, mm) in a["reads_by_agent"].items():
        sel = np.where(a["row_agent"] == ag)[0]
        if sel.size == 0:
            continue
        tc = a["row_t"][sel]
        lo_c = np.searchsorted(tt, tc, "left"); hi_c = np.searchsorted(tt, tc, "right")
        lo_2 = np.searchsorted(tt, tc - 2 * 3600 * US, "right")
        for r, l2, lc, hc in zip(sel, lo_2, lo_c, hi_c):
            if hc > lc:
                ci.append(np.full(hc - lc, r)); cj.append(mm[lc:hc])
            if lc > l2:
                ri.append(np.full(lc - l2, r)); rj.append(mm[l2:lc])
    def mk(ii, jj):
        if not ii:
            return sp.csr_matrix((n, M), dtype=np.float32)
        ii = np.concatenate(ii); jj = np.concatenate(jj)
        m = sp.csr_matrix((np.ones(ii.size, dtype=np.float32), (ii, jj)), shape=(n, M))
        m.data[:] = 1.0
        return m
    Rc = mk(ci, cj)
    a["R_call_rest"] = (Rc - Rc.multiply(a["W_read"] > 0)).tocsr()   # read at the call, posted before the mirror
    a["R_call_rest"].eliminate_zeros()
    R2 = mk(ri, rj)
    a["R_prev2h"] = (R2 - R2.multiply(a["W_read"] > 0)).tocsr()          # read at earlier calls in the last 2 h
    a["R_prev2h"].eliminate_zeros()
    # agent-bin index from statements + touches (filled by coding)
    # named target per message: mentions
    a["msg_mentions"] = ev.msgs["mentions"].to_list()


# --------------------------------------------------------------------------------------------------------- coding
@dataclass
class Coding:
    names: list
    kinds: list
    M_msg: sp.csr_matrix
    M_row: sp.csr_matrix
    M_ab: sp.csr_matrix
    ab_agent: np.ndarray
    ab_bin: np.ndarray
    ab_day: np.ndarray
    source: str
    practice_slugs: dict = field(default_factory=dict)  # element index -> slug (practice elements)
    M_st: sp.csr_matrix | None = None                   # statements x E (chat + intents)

    def idx(self, names):
        m = {n: i for i, n in enumerate(self.names)}
        return np.array([m[x] for x in names if x in m], dtype=np.int64)


def _agentbin_index(ev: Ev, agents: np.ndarray, t: np.ndarray, days: list):
    b = t // BIN_US
    key = agents.astype(np.int64) * 10**9 + b
    uk, inv = np.unique(key, return_inverse=True)
    return uk, inv


def _build_ab(ev, st_agent, st_t, st_day, st_E, tc_agent, tc_t, tc_day, tc_E, E):
    """Agent-bin x element boolean CSR from statement codes (st_E: n_st x E CSR) and touch codes."""
    ag = np.concatenate([st_agent, tc_agent]).astype(np.int64)
    tt = np.concatenate([st_t, tc_t]).astype(np.int64)
    dd = np.concatenate([st_day, tc_day]).astype(np.int32)
    key = ag * 10**9 + tt // BIN_US
    uk, inv = np.unique(key, return_inverse=True)
    X = sp.vstack([st_E, tc_E]).tocsr()
    P = sp.csr_matrix((np.ones(len(inv), dtype=np.float32), (inv, np.arange(len(inv)))), shape=(len(uk), len(inv)))
    M = (P @ X).tocsr()
    M.data[:] = 1.0
    ab_day = np.zeros(len(uk), dtype=np.int32)
    ab_day[inv] = dd
    return M, (uk // 10**9).astype(np.int16), (uk % 10**9).astype(np.int64), ab_day


def coding_candidates(ev: Ev, path: Path | None = None) -> tuple[Coding, dict]:
    """Code items and statements with the post hoc candidate patterns (regex on text, read in memory only)."""
    path = path or (ROOT / "hypotheses" / "H146-egregore-recruitment-behaviors-51" / "scheme" /
                    "candidates_story.json")
    C = json.loads(path.read_text())
    names, kinds, pats, K = [], [], [], {}
    slug_el = {}
    for cname, c in C["candidates"].items():
        K[cname] = []
        for en, rx in c["terms"].items():
            names.append(en); kinds.append("term"); pats.append(re.compile(rx, re.I)); K[cname].append(en)
        for s in c["practices"]:
            en = f"{cname}:repo:{s}"
            names.append(en); kinds.append("practice"); pats.append(None); K[cname].append(en)
            slug_el.setdefault(s.lower(), []).append(len(names) - 1)
    E = len(names)
    term_ix = [i for i, k in enumerate(kinds) if k == "term"]
    # chat text (in memory)
    txt = pl.read_parquet(SH / "chat_text.parquet", columns=["message_id", "text"]).join(
        ev.msgs.select("message_id", "msg"), on="message_id", how="inner").sort("msg")
    def code_texts(texts):
        ii, jj = [], []
        for r, s in enumerate(texts):
            if not s:
                continue
            for j in term_ix:
                if pats[j].search(s):
                    ii.append(r); jj.append(j)
        return ii, jj
    ii, jj = code_texts(txt["text"].to_list())
    msg_ids = txt["msg"].to_numpy()
    ii = msg_ids[np.array(ii, dtype=np.int64)] if ii else np.array([], dtype=np.int64)
    # chat items that name a practice repo
    pm = pl.read_parquet(SH / "project_mentions_chat.parquet", columns=["message_id", "project"]).join(
        ev.msgs.select("message_id", "msg"), on="message_id", how="inner")
    pi, pj = [], []
    for m, pr in pm.select("msg", "project").iter_rows():
        s = (pr or "").rstrip("/").split("/")[-1].lower()
        for j in slug_el.get(s, []):
            pi.append(m); pj.append(j)
    n_m = ev.a["n_msgs"]
    M_msg = sp.csr_matrix((np.ones(len(ii) + len(pi), dtype=np.float32),
                           (np.concatenate([ii, np.array(pi, dtype=np.int64)]),
                            np.concatenate([np.array(jj, dtype=np.int64), np.array(pj, dtype=np.int64)]))),
                          shape=(n_m, E))
    M_msg.data[:] = 1.0
    # statements: chat (= message codes, terms only) and intents (regex on intent text)
    st = ev.stmts
    it = st.filter(pl.col("kind") == "intent")
    ii_idx = pl.read_parquet(SH / "embeddings" / "intentions_index.parquet").with_row_index("irow")
    stall = pl.read_parquet(SH / "embeddings" / "statements.parquet", columns=["kind", "src_row"]).with_row_index(
        "srow")
    it = it.join(stall.select("srow", "src_row"), on="srow").join(ii_idx, left_on="src_row", right_on="irow")
    itx = pl.read_parquet(SH / "intentions_text.parquet").join(it.select("event_index", "srow"), on="event_index")
    itx = itx.with_columns(pl.coalesce("short_text", "goal_text").alias("text"))
    srow_to_st = {s: i for i, s in enumerate(st["srow"].to_list())}
    i2, j2 = code_texts(itx["text"].to_list())
    st_i = [srow_to_st[s] for s in itx["srow"].to_list()]
    i2 = [st_i[r] for r in i2]
    chat_rows = np.where(st["kind"].to_numpy() == "chat")[0]
    chat_msg = st["msg"].to_numpy()[chat_rows].astype(np.int64)
    Mt = M_msg.copy()
    Mt[:, [j for j, k in enumerate(kinds) if k == "practice"]] = 0  # statements carry terms only
    Mt.eliminate_zeros()
    Mc = Mt[chat_msg]
    Mc = sp.csr_matrix((Mc.data, Mc.indices, Mc.indptr), shape=(len(chat_rows), E)).tocoo()
    st_E = sp.csr_matrix((np.ones(len(Mc.row) + len(i2), dtype=np.float32),
                          (np.concatenate([chat_rows[Mc.row], np.array(i2, dtype=np.int64)]),
                           np.concatenate([Mc.col, np.array(j2, dtype=np.int64)]))), shape=(st.height, E))
    st_E.data[:] = 1.0
    cod = _finish_coding(ev, names, kinds, M_msg, st_E, slug_el, "candidates_story (post hoc)")
    Kix = {k: cod.idx(v) for k, v in K.items()}
    return cod, Kix


def _finish_coding(ev, names, kinds, M_msg, st_E, slug_el, source):
    E = len(names)
    st = ev.stmts
    dix = {d: i for i, d in enumerate(ev.a["days"])}
    st_day = np.array([dix[d] for d in st["pt_date"].to_list()], dtype=np.int32)
    tc = ev.touches
    ti, tj = [], []
    tsl = tc["slug"].to_list()
    for r, s in enumerate(tsl):
        for j in slug_el.get((s or "").lower(), []):
            ti.append(r); tj.append(j)
    tc_E = sp.csr_matrix((np.ones(len(ti), dtype=np.float32), (ti, tj)), shape=(tc.height, E))
    tc_dates = ev.calls.select("turn_id", "pt_date").join(tc.select("turn_id"), on="turn_id", how="right")
    tc_day = np.array([dix.get(d, 0) for d in tc_dates["pt_date"].to_list()], dtype=np.int32)
    M_ab, ab_agent, ab_bin, ab_day = _build_ab(ev, st["agent"].to_numpy(), st["t"].to_numpy(), st_day, st_E,
                                               tc["agent"].to_numpy(), tc["t"].to_numpy(), tc_day, tc_E, E)
    # talk rows: their own chat messages' codes (terms and named practices)
    R = ev.rows
    ri, rj = [], []
    for r, ms in enumerate(R["msgs"].to_list()):
        for m in ms:
            ri.append(r); rj.append(m)
    P = sp.csr_matrix((np.ones(len(ri), dtype=np.float32), (ri, rj)), shape=(R.height, ev.a["n_msgs"]))
    M_row = (P @ M_msg).tocsr(); M_row.data[:] = 1.0
    ps = {j: s for s, js in slug_el.items() for j in js}
    return Coding(names, kinds, M_msg.tocsr(), M_row, M_ab, ab_agent, ab_bin, ab_day, source, ps, st_E.tocsr())


def coding_h145(ev: Ev):
    """H145 element map -> Coding. Filled after H145.READY (see analysis/coding_h145.py)."""
    from coding_h145 import build  # noqa: WPS433 (local module in this folder)
    return build(ev, _finish_coding)


# ------------------------------------------------------------------------------------------------ pattern panels
@dataclass
class Panel:
    K: np.ndarray
    nK_ab: np.ndarray        # distinct K elements per agent-bin
    host_ab: np.ndarray      # bool, >= m
    carries: np.ndarray      # per msg: number of K elements carried
    carries_host: np.ndarray  # per msg: carries >= 1 and sender is a host in the msg's bin
    row_own: np.ndarray      # per talk row: K elements in its own chat
    m: int


def panel(ev: Ev, cod: Coding, K: np.ndarray, m: int = 2) -> Panel:
    ind = np.zeros(len(cod.names), dtype=np.float32); ind[K] = 1
    nK = cod.M_ab @ ind
    host = nK >= m
    carries = cod.M_msg @ ind
    # sender host status in the message's bin
    key_ab = cod.ab_agent.astype(np.int64) * 10**9 + cod.ab_bin
    a = ev.a
    key_m = a["msg_agent"].astype(np.int64) * 10**9 + a["msg_bin"]
    pos = np.searchsorted(key_ab, key_m)
    pos = np.clip(pos, 0, len(key_ab) - 1)
    ok = (key_ab[pos] == key_m) & (a["msg_agent"] >= 0)
    hs = np.zeros(len(key_m), dtype=bool); hs[ok] = host[pos[ok]]
    return Panel(K, nK, host, carries, (carries > 0) & hs, cod.M_row @ ind, m)


def adoption_rows(ev: Ev, cod: Coding, pn: Panel, gap_days: int = 2):
    """At-risk talk rows and the adoption indicator (card definition, Amendment A1 operational rule).

    Agent i adopts K in bin b if i is a host of K in b and was not a host in any bin of its previous `gap_days`
    active days (or earlier the same day), having >= gap_days active days before. The adoption call = the first talk
    row in b whose own chat carries >= 1 K element. Rows of i are at risk while i is in such a spell, up to and
    including the adoption call. Adoption bins without a K-carrying talk row are counted (`n_nonchat`) and their
    rows dropped."""
    a = ev.a
    n = a["n_rows"]
    at_risk = np.zeros(n, dtype=bool); y = np.zeros(n, dtype=bool)
    n_adopt = n_nonchat = 0
    ab_ag, ab_b, ab_d = cod.ab_agent, cod.ab_bin, cod.ab_day
    # active days per agent: days with any statement
    st_ag = ev.stmts["agent"].to_numpy()
    dix = {d: i for i, d in enumerate(a["days"])}
    st_day = np.array([dix[d] for d in ev.stmts["pt_date"].to_list()])
    for ag in np.unique(a["row_agent"]):
        act = np.unique(st_day[st_ag == ag])
        if act.size == 0:
            continue
        s = ab_ag == ag
        hb = ab_b[s][pn.host_ab[s]]; hd = ab_d[s][pn.host_ab[s]]
        o = np.argsort(hb); hb, hd = hb[o], hd[o]
        rows = np.where(a["row_agent"] == ag)[0]
        rb, rdy = a["row_bin"][rows], a["row_day"][rows]
        # for each row: last host bin strictly before the row's bin
        k = np.searchsorted(hb, rb, "left") - 1
        last_day = np.where(k >= 0, hd[np.clip(k, 0, None)], -10**6) if hb.size else np.full(len(rows), -10**6)
        # index of the row's day among active days; the gap_days-th previous active day
        ai = np.searchsorted(act, rdy, "left")
        enough = ai >= gap_days
        prevd = np.where(enough, act[np.clip(ai - gap_days, 0, None)], 10**6)
        risk = enough & (last_day < prevd)
        # host in the row's own bin?
        in_host = np.isin(rb, hb)
        own = pn.row_own[rows] > 0
        # walk adoption bins
        done_bins = set()
        for j in range(len(rows)):
            if not risk[j]:
                continue
            b = rb[j]
            if in_host[j]:
                if b in done_bins:
                    continue
                at_risk[rows[j]] = True
                if own[j]:
                    y[rows[j]] = True; done_bins.add(b); n_adopt += 1
            else:
                at_risk[rows[j]] = True
        # adoption bins (risk at bin start) without a K-carrying talk row: drop their rows
        for b in np.unique(rb[risk & in_host]):
            if b not in done_bins:
                at_risk[rows[rb == b]] = False; n_nonchat += 1
    return at_risk, y, {"n_adopt_chat": int(n_adopt), "n_adopt_nonchat": int(n_nonchat),
                        "n_rows_at_risk": int(at_risk.sum())}


def exposures(ev: Ev, pn: Panel, host_only: bool = True, nohub: bool = False):
    a = ev.a
    c = (pn.carries_host if host_only else pn.carries > 0).astype(np.float32)
    if nohub:
        c = c * (a["msg_agent"] != HUB)
    X = {
        "Rm": a["W_read"] @ c, "P": a["W_fly"] @ c,
        "Rm_named": a["W_read_named"] @ c, "Rm_unnamed": a["W_read_unnamed"] @ c, "P_named": a["W_fly_named"] @ c,
        "Rc_rest": a["R_call_rest"] @ c, "R2h": a["R_prev2h"] @ c,
    }
    return {k: np.asarray(v).ravel() for k, v in X.items()}


def controls(ev: Ev):
    a = ev.a
    d, b = a["row_d"], a["row_before"]
    lagb = np.digitize(d, [5, 10, 20])
    befb = np.digitize(b, [60, 300, 1800])
    cols = [np.log1p(a["row_dens"]), a["A_read"], a["A_fly"]]
    names = ["log_dens10", "A_read", "A_fly"]
    for k in (1, 2, 3):
        cols.append((lagb == k).astype(float)); names.append(f"lag{k}")
        cols.append((befb == k).astype(float)); names.append(f"bef{k}")
    return np.column_stack(cols), names


# --------------------------------------------------------------------------------------- conditional Poisson fit
def strata_codes(*arrs):
    key = np.zeros(len(arrs[0]), dtype=np.int64)
    for x in arrs:
        u, inv = np.unique(x, return_inverse=True)
        key = key * (len(u) + 1) + inv
    _, s = np.unique(key, return_inverse=True)
    return s


def fit_cpois(y, X, s, ridge=0.5, pen=None, w=None, maxit=50, tol=1e-8, beta0=None):
    """Conditional (stratum-profiled) Poisson: max sum_s [sum y x b - n_s log sum exp(x b)] - ridge/2 |b_pen|^2.

    Returns beta, cov (inverse penalized information), scores per row (for cluster sandwich), converged."""
    n, p = X.shape
    w = np.ones(n) if w is None else w
    pen = np.ones(p) if pen is None else pen
    S = s.max() + 1
    yw = y * w
    ns = np.bincount(s, weights=yw, minlength=S)
    keep = ns[s] > 0
    beta = np.zeros(p) if beta0 is None else beta0.copy()
    conv = False
    for it in range(maxit):
        eta = X @ beta
        mx = np.full(S, -np.inf); np.maximum.at(mx, s, eta)
        ex = np.exp(eta - mx[s]) * w
        den = np.bincount(s, weights=ex, minlength=S)
        pi = np.where(keep, ex / np.maximum(den[s], 1e-300), 0.0)
        mu = ns[s] * pi
        g = X.T @ (yw - mu) - ridge * pen * beta
        # Hessian: sum_s n_s [sum pi x x' - xbar xbar']
        Xm = np.zeros((S, p))
        np.add.at(Xm, s, X * pi[:, None])
        H = (X * mu[:, None]).T @ X - (Xm * ns[:, None]).T @ Xm + np.diag(ridge * pen)
        try:
            step = np.linalg.solve(H, g)
        except np.linalg.LinAlgError:
            step = np.linalg.lstsq(H, g, rcond=None)[0]
        # damping
        sc = 1.0
        mxs = np.abs(step).max()
        if mxs > 2:
            sc = 2 / mxs
        beta = beta + sc * step
        if np.abs(sc * step).max() < tol:
            conv = True
            break
    eta = X @ beta
    mx = np.full(S, -np.inf); np.maximum.at(mx, s, eta)
    ex = np.exp(eta - mx[s]) * w
    den = np.bincount(s, weights=ex, minlength=S)
    pi = np.where(keep, ex / np.maximum(den[s], 1e-300), 0.0)
    mu = ns[s] * pi
    Xm = np.zeros((S, p)); np.add.at(Xm, s, X * pi[:, None])
    H = (X * mu[:, None]).T @ X - (Xm * ns[:, None]).T @ Xm + np.diag(ridge * pen)
    cov = np.linalg.pinv(H)
    # per-row score contributions (y - mu) (x - xbar_s)
    sc_rows = (yw - mu)[:, None] * (X - Xm[s])
    return {"beta": beta, "cov": cov, "H": H, "scores": sc_rows, "conv": conv}


def sandwich(fit, cluster):
    """Cluster-robust covariance H^-1 (sum_c u_c u_c') H^-1 for cluster ids."""
    u = fit["scores"]
    _, c = np.unique(cluster, return_inverse=True)
    U = np.zeros((c.max() + 1, u.shape[1])); np.add.at(U, c, u)
    Hi = np.linalg.pinv(fit["H"])
    G = len(U)
    return Hi @ (U.T @ U) @ Hi * (G / max(G - 1, 1))


def contrast(fit, cov, names, a, b):
    i, j = names.index(a), names.index(b)
    est = fit["beta"][i] - fit["beta"][j]
    var = cov[i, i] + cov[j, j] - 2 * cov[i, j]
    se = float(np.sqrt(max(var, 0)))
    return float(est), se


def p1_fit(ev: Ev, Xd: dict, at_risk, y, ridge=0.5, variant="adopt", split_named=False, ctrl=None):
    """Read vs in-flight contrast on at-risk talk rows. Strata agent x day. Clusters 1-h blocks within PT day."""
    a = ev.a
    r = np.where(at_risk)[0]
    C, cn = ctrl if ctrl is not None else controls(ev)
    if split_named:
        ex = ["Rm_named", "Rm_unnamed", "P", "Rc_rest", "R2h"]
    else:
        ex = ["Rm", "P", "Rc_rest", "R2h"]
    X = np.column_stack([Xd[k][r] for k in ex] + [C[r]])
    names = ex + cn
    pen = np.ones(X.shape[1])
    s = strata_codes(a["row_agent"][r], a["row_day"][r])
    yy = y[r].astype(float)
    # quasi-separation guard: chosen rows with exposure > 0
    n_ch = {k: int(((Xd[k][r] > 0) & (yy > 0)).sum()) for k in ex}
    f = fit_cpois(yy, X, s, ridge=ridge, pen=pen)
    V = sandwich(f, a["row_hourblock"][r])
    out = {"n_rows": int(len(r)), "n_events": int(yy.sum()), "chosen_with_exposure": n_ch, "conv": f["conv"]}
    out["beta"] = {k: float(f["beta"][names.index(k)]) for k in ex}
    if split_named:
        for k in ("Rm_named", "Rm_unnamed"):
            e, se = contrast(f, V, names, k, "P"); out[f"delta_{k}"] = (e, se)
        e, se = contrast(f, V, names, "Rm_named", "Rm_unnamed"); out["delta_named_minus_unnamed"] = (e, se)
    else:
        e, se = contrast(f, V, names, "Rm", "P"); out["delta"] = (e, se)
    out["estimable"] = (n_ch.get("Rm", n_ch.get("Rm_unnamed", 0)) >= 5) and (n_ch["P"] >= 5)
    return out


def block_boot_delta(ev, Xd, at_risk, y, B=200, seed=0, ridge=0.5, ctrl=None):
    """1-h-block bootstrap within PT day for delta = beta_Rm - beta_P (multiplicity weights)."""
    a = ev.a
    r = np.where(at_risk)[0]
    C, cn = ctrl if ctrl is not None else controls(ev)
    ex = ["Rm", "P", "Rc_rest", "R2h"]
    X = np.column_stack([Xd[k][r] for k in ex] + [C[r]])
    s = strata_codes(a["row_agent"][r], a["row_day"][r])
    yy = y[r].astype(float)
    _, blk = np.unique(a["row_hourblock"][r], return_inverse=True)
    rng = np.random.default_rng(seed)
    G = blk.max() + 1
    f0 = fit_cpois(yy, X, s, ridge=ridge)
    out = []
    for _ in range(B):
        wb = np.bincount(rng.integers(0, G, G), minlength=G)[blk].astype(float)
        f = fit_cpois(yy, X, s, ridge=ridge, w=wb, beta0=f0["beta"], maxit=25)
        out.append(f["beta"][0] - f["beta"][1])
    return np.array(out)


# ------------------------------------------------------------------------------------------- erasures (P4, P5)
def agent_days(ev: Ev):
    """Per agent: sorted active-day indices (days with >= 1 statement)."""
    a = ev.a
    if "act_days" in a:
        return a["act_days"]
    dix = {d: i for i, d in enumerate(a["days"])}
    st_day = np.array([dix[d] for d in ev.stmts["pt_date"].to_list()])
    st_ag = ev.stmts["agent"].to_numpy()
    a["act_days"] = {int(g): np.unique(st_day[st_ag == g]) for g in np.unique(st_ag)}
    return a["act_days"]


def call_times(ev: Ev):
    a = ev.a
    if "call_t" not in a:
        c = ev.calls.filter(pl.col("kind") != "consolidate").select("agent", "t_call").sort("agent", "t_call")
        ag, t = c["agent"].to_numpy(), c["t_call"].to_numpy()
        a["call_t"] = {int(g): t[ag == g] for g in np.unique(ag)}
    return a["call_t"]


def host_before(ev, cod, pn, agent, t, day, gap_days=2):
    """True if `agent` was a host of K in a bin before t within its previous `gap_days` active days or earlier
    on the same day."""
    s = (cod.ab_agent == agent) & pn.host_ab
    hb = cod.ab_bin[s]; hd = cod.ab_day[s]
    b = t // BIN_US
    ok = hb < b
    if not ok.any():
        return False
    act = agent_days(ev).get(int(agent), np.array([], dtype=int))
    k = np.searchsorted(act, day, "left")
    d0 = act[max(k - gap_days, 0)] if k > 0 else day
    return bool((hd[ok] >= d0).any())


def k_statement_times(ev, cod, K):
    """Per agent: sorted times of statements (chat + intents) carrying >= 1 K element."""
    ind = np.zeros(len(cod.names), dtype=np.float32); ind[K] = 1
    c = (cod.M_st @ ind) > 0
    ag = ev.stmts["agent"].to_numpy(); t = ev.stmts["t"].to_numpy()
    return {int(g): np.sort(t[c & (ag == g)]) for g in np.unique(ag)}


def host_flags(ev, cod, pn, agent, t, day, gap_days=2):
    """Vectorized host_before for one agent's events (t, day arrays)."""
    s = (cod.ab_agent == agent) & pn.host_ab
    hb = cod.ab_bin[s]; hd = cod.ab_day[s]
    o = np.argsort(hb); hb, hd = hb[o], hd[o]
    if hb.size == 0:
        return np.zeros(len(t), bool)
    act = agent_days(ev).get(int(agent), np.array([0]))
    k = np.searchsorted(act, day, "left")
    d0 = np.where(k > 0, act[np.clip(k - gap_days, 0, None)], day)
    j = np.searchsorted(hb, t // BIN_US, "left") - 1        # last host bin strictly before the event's bin
    last_d = np.where(j >= 0, hd[np.clip(j, 0, None)], -10**6)
    return last_d >= d0


def p4_events(ev, cod, pn, K, practice_slugs=()):
    """Host F/P events with follow-up (calls 1-20), re-expression and read-gating (calls 1-10)."""
    a = ev.a
    er = ev.er
    if "er_arr" not in a:
        dix = {d: i for i, d in enumerate(a["days"])}
        a["er_arr"] = {"agent": er["agent"].to_numpy(), "t": er["t_call"].to_numpy(),
                       "day": np.array([dix[d] for d in er["pt_date"].to_list()]),
                       "t10": er["t10"].to_numpy(), "t20": er["t20"].to_numpy(),
                       "F": (er["etype"] == "F").to_numpy(), "unit": er["unit_id"].to_numpy(),
                       "projs": er["projs10"].to_list()}
    R = a["er_arr"]
    kt = k_statement_times(ev, cod, K)
    ct = call_times(ev)
    rb = a["reads_by_agent"]
    car = (pn.carries > 0).astype(np.int64)
    ps = set(practice_slugs)
    cols = {k: [] for k in ("F", "agent", "unit", "day", "t", "d", "T", "expr10", "nread", "touched", "lm_d",
                            "lm_T", "n10", "n20")}
    for g in np.unique(R["agent"]):
        sel = np.where(R["agent"] == g)[0]
        hf = host_flags(ev, cod, pn, g, R["t"][sel], R["day"][sel])
        sel = sel[hf]
        if sel.size == 0:
            continue
        t, t10, t20 = R["t"][sel], R["t10"][sel], R["t20"][sel]
        cts = ct.get(int(g), np.array([0], dtype=np.int64))
        i0 = np.searchsorted(cts, t, "left"); i20 = np.searchsorted(cts, t20, "right")
        i10 = np.searchsorted(cts, t10, "right")
        n20 = np.maximum(i20 - i0, 1); n10c = i10 - i0
        ts = kt.get(int(g), np.array([], dtype=np.int64))
        j = np.searchsorted(ts, t, "left")
        te = np.where(j < len(ts), ts[np.clip(j, 0, max(len(ts) - 1, 0))] if len(ts) else 0, np.iinfo(np.int64).max)
        hit = te <= t20
        Te = np.maximum(np.searchsorted(cts, np.where(hit, te, 0), "right") - i0, 1)
        T = np.where(hit, Te, n20)
        e10 = hit & (te <= t10)
        lm_d = (hit & ~e10).astype(float)
        lm_T = np.where(lm_d > 0, np.maximum(Te - n10c, 1), np.maximum(n20 - n10c, 0))
        tt, mm = rb.get(int(g), (np.array([], dtype=np.int64), np.array([], dtype=np.int64)))
        cs = np.concatenate([[0], np.cumsum(car[mm])]) if len(mm) else np.array([0])
        lo, hi = np.searchsorted(tt, t, "left"), np.searchsorted(tt, t10, "right")
        nread = cs[hi] - cs[lo]
        touched = np.array([bool(ps & set(R["projs"][i] or [])) for i in sel]) if ps else np.zeros(len(sel), bool)
        for k, v in (("F", R["F"][sel]), ("agent", np.full(len(sel), int(g), dtype=np.int64)), ("unit", R["unit"][sel]),
                     ("day", R["day"][sel]), ("t", t), ("d", hit.astype(float)), ("T", T.astype(float)),
                     ("expr10", e10.astype(int)), ("nread", nread), ("touched", touched), ("lm_d", lm_d),
                     ("lm_T", lm_T.astype(float)), ("n10", np.maximum(n10c, 1)), ("n20", n20)):
            cols[k].append(v)
    if not cols["F"]:
        return None
    return {k: np.concatenate(v) for k, v in cols.items()}


def p4_stats(E, B=300, seed=0):
    if E is None or E["F"].sum() < 5 or (~E["F"]).sum() < 5:
        return None
    s = strata_codes(E["agent"], E["unit"])
    cl = E["agent"] * 1000 + E["day"]
    F = E["F"]
    d1, T1 = np.where(F, E["d"], 0), np.where(F, E["T"], 0)
    d0, T0 = np.where(~F, E["d"], 0), np.where(~F, E["T"], 0)
    rr, lo, hi, _ = cluster_boot_rr(d1, T1, d0, T0, s, cl, B=B, seed=seed)
    out = {"n_F": int(F.sum()), "n_P": int((~F).sum()), "events_F": int(E["d"][F].sum()),
           "events_P": int(E["d"][~F].sum()), "HR_F_vs_P": rr, "ci": [lo, hi]}
    # read-gating (landmark at call 10; events not re-expressed by call 10 and with follow-up left)
    Rp = (E["nread"] > 0) | E["touched"]
    keep = (E["expr10"] == 0) & (E["lm_T"] > 0)
    for lab, grp in (("F", F), ("P", ~F)):
        k = keep & grp
        if k.sum() < 10 or (Rp & k).sum() < 3 or ((~Rp) & k).sum() < 3:
            out[f"HR_read_{lab}"] = None
            continue
        a1 = np.where(Rp & k, E["lm_d"], 0); b1 = np.where(Rp & k, E["lm_T"], 0)
        a0 = np.where(~Rp & k, E["lm_d"], 0); b0 = np.where(~Rp & k, E["lm_T"], 0)
        r2, l2, h2, _ = cluster_boot_rr(a1, b1, a0, b0, s, cl, B=B, seed=seed + 1)
        out[f"HR_read_{lab}"] = {"est": r2, "ci": [l2, h2], "n_Rplus": int((Rp & k).sum()),
                                 "n_Rminus": int((~Rp & k).sum()), "events": int(E["lm_d"][k].sum())}
    out["share_Rplus_F"] = float(Rp[F].mean()); out["share_Rplus_P"] = float(Rp[~F].mean())
    return out


def mention_pairs(ev: Ev):
    a = ev.a
    if "ment_msg" not in a:
        mm, tg = [], []
        for m, L_ in enumerate(a["msg_mentions"]):
            for x in (L_ or []):
                mm.append(m); tg.append(x)
        a["ment_msg"] = np.array(mm, dtype=np.int64); a["ment_tgt"] = np.array(tg, dtype=np.int64)
    return a["ment_msg"], a["ment_tgt"]


def repair_times(ev, pn):
    """Per target agent: sorted times of named K messages from other hosts (carries K, sender host in bin)."""
    a = ev.a
    mm, tg = mention_pairs(ev)
    ok = pn.carries_host[mm] & (a["msg_agent"][mm] != tg)
    out = {}
    for g in np.unique(tg[ok]):
        out[int(g)] = np.sort(a["msg_t"][mm[ok & (tg == g)]])
    return out


def count_in(times_by_agent, agent, t0, t1, exclude_t=None):
    ts = times_by_agent.get(int(agent))
    if ts is None:
        return 0
    n = np.searchsorted(ts, t1, "right") - np.searchsorted(ts, t0, "right")
    return int(n)


def mh_rate_ratio(d1, T1, d0, T0, strata):
    """Mantel-Haenszel rate ratio over strata (events d, person-time T, groups 1 vs 0)."""
    S = strata.max() + 1
    D1 = np.bincount(strata, d1, S); P1 = np.bincount(strata, T1, S)
    D0 = np.bincount(strata, d0, S); P0 = np.bincount(strata, T0, S)
    Tt = P1 + P0
    ok = Tt > 0
    num = (D1 * P0 / np.where(ok, Tt, 1))[ok].sum()
    den = (D0 * P1 / np.where(ok, Tt, 1))[ok].sum()
    return num / den if den > 0 else np.nan


def cluster_boot_rr(d1, T1, d0, T0, strata, cluster, B=300, seed=0):
    """Rate ratio with a cluster bootstrap (clusters resampled, MH over strata)."""
    rng = np.random.default_rng(seed)
    _, c = np.unique(cluster, return_inverse=True)
    G = c.max() + 1
    est = mh_rate_ratio(d1, T1, d0, T0, strata)
    bs = []
    for _ in range(B):
        w = np.bincount(rng.integers(0, G, G), minlength=G)[c].astype(float)
        bs.append(mh_rate_ratio(d1 * w, T1 * w, d0 * w, T0 * w, strata))
    bs = np.array(bs); bs = bs[np.isfinite(bs) & (bs > 0)]
    if bs.size < 20:
        return est, np.nan, np.nan, bs
    lo, hi = np.exp(np.percentile(np.log(bs), [2.5, 97.5]))
    return est, float(lo), float(hi), bs


# --------------------------------------------------------------------------------------- specialization (P6)
def mi_host_element(h, e):
    """I(host; element) in bits pooled over host-bins (plug-in, Miller-Madow). With the within-bin set-swap null
    (`perm_within_bin`) this measures consistent host-element association beyond each bin's composition.
    (I(host; element | bin) is invariant under the within-bin swap and cannot be used with it.)"""
    n = len(h)
    if n == 0:
        return 0.0
    _, hh = np.unique(h, return_inverse=True); _, ee = np.unique(e, return_inverse=True)
    def ent(codes):
        c = np.bincount(codes).astype(float); c = c[c > 0]; p = c / n
        return -(p * np.log2(p)).sum() + (len(c) - 1) / (2 * n * np.log(2))
    return float(ent(hh) + ent(ee) - ent(hh * (ee.max() + 1) + ee))


def cond_mi_host_element(h, e, b):
    """I(host; element | bin) in bits, plug-in with Miller-Madow per bin, from integer-coded triples."""
    if len(h) == 0:
        return 0.0
    _, hb = np.unique(b, return_inverse=True)
    _, hh = np.unique(h, return_inverse=True)
    _, ee = np.unique(e, return_inverse=True)
    Hn, En, Bn = hh.max() + 1, ee.max() + 1, hb.max() + 1
    n = len(h)
    def H_of(codes, K):
        c = np.bincount(codes, minlength=K).astype(float)
        c = c[c > 0]
        return c
    # I(H;E|B) = H(H,B) + H(E,B) - H(H,E,B) - H(B)
    def ent(codes):
        c = np.bincount(codes).astype(float); c = c[c > 0]; p = c / n
        return -(p * np.log2(p)).sum() + (len(c) - 1) / (2 * n * np.log(2))
    hbk = hb * Hn + hh
    ebk = hb * En + ee
    hebk = (hb * Hn + hh) * En + ee
    return float(ent(hbk) + ent(ebk) - ent(hebk) - ent(hb))


def perm_within_bin(e, b, rng, h=None):
    """Null for specialization: within each bin, reassign the hosts' element SETS among the hosts present in that
    bin (host labels permuted across (bin, host) groups). Keeps every bin's sets and every host's bins; breaks the
    host-element association. Returns the permuted HOST labels for the triples (pass h)."""
    gk = b.astype(np.int64) * 1000 + h
    ug, ginv = np.unique(gk, return_inverse=True)
    gb = ug // 1000; gh = ug % 1000
    o = np.lexsort((rng.random(len(ug)), gb))   # groups sorted by bin, random within bin
    ob = np.argsort(gb, kind="stable")           # groups sorted by bin, original order
    newh = gh.copy()
    newh[ob] = gh[o]
    return newh[ginv]


# ------------------------------------------------------------------------------------------ O-information (P6)
def gauss_entropy(C):
    sign, ld = np.linalg.slogdet(C)
    k = C.shape[0]
    return 0.5 * (k * np.log(2 * np.pi * np.e) + ld) / np.log(2)


def o_information_discrete(X):
    """Plug-in O-information (bits, Miller-Madow) of binary columns of X (T x n), integer-coded patterns."""
    X = (np.asarray(X) > 0.5).astype(np.int64)
    T, n = X.shape
    def H(cols):
        if len(cols) == 0:
            return 0.0
        code = (X[:, cols] * (1 << np.arange(len(cols)))).sum(1)
        c = np.bincount(code).astype(float); c = c[c > 0]; p = c / T
        return float(-(p * np.log2(p)).sum() + (len(c) - 1) / (2 * T * np.log(2)))
    allc = list(range(n))
    om = (n - 2) * H(allc)
    for i in range(n):
        om += H([i]) - H([j for j in allc if j != i])
    return om


def o_information(X):
    """Gaussian O-information (bits) of the columns of X (T x n): (n-2) H(X) + sum_i [H(X_i) - H(X_-i)]."""
    n = X.shape[1]
    C = np.cov(X, rowvar=False) + 1e-9 * np.eye(n)
    om = (n - 2) * gauss_entropy(C)
    for i in range(n):
        idx = [j for j in range(n) if j != i]
        om += gauss_entropy(C[[i]][:, [i]]) - gauss_entropy(C[np.ix_(idx, idx)])
    return float(om)


def field_removed(X, Z):
    """Residuals of each column on Z and on the leave-one-out mean of the other columns (H101 rule)."""
    T, n = X.shape
    R = np.zeros_like(X, dtype=float)
    tot = X.sum(1)
    for i in range(n):
        loo = (tot - X[:, i]) / (n - 1)
        D = np.column_stack([np.ones(T), Z, loo])
        b = np.linalg.lstsq(D, X[:, i], rcond=None)[0]
        R[:, i] = X[:, i] - D @ b
    return R


def curveball(B, rng, n_iter=None):
    """Curveball swap randomization of a binary matrix (rows: hosts, cols: bins); keeps row and column sums."""
    rows = [set(np.where(B[i])[0]) for i in range(B.shape[0])]
    n = len(rows)
    n_iter = n_iter or 5 * n * max(1, n)
    for _ in range(n_iter):
        i, j = rng.choice(n, 2, replace=False)
        a, b = rows[i], rows[j]
        ab = a - b; ba = b - a
        if not ab and not ba:
            continue
        pool = list(ab | ba)
        rng.shuffle(pool)
        k = len(ab)
        na = (a & b) | set(pool[:k]); nb = (a & b) | set(pool[k:])
        rows[i], rows[j] = na, nb
    out = np.zeros_like(B)
    for i, r in enumerate(rows):
        out[i, list(r)] = 1
    return out
