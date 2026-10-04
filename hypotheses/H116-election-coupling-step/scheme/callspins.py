"""Per-call talk spins with read-gated and in-flight sender inputs (H115 / H116 shared scheme).

Byte-identical copies live in hypotheses/H115-debate-judge-role-recovery/scheme/ and
hypotheses/H116-election-coupling-step/scheme/ (STANDARDS section 8 asks for infra/shared/; that move is a suggested
shared-file change). No text is read; held-out rows are refused.

Degrees of freedom (per non-summary model call c of recipient i, the context ledger's call clock):
  s_i(c)      +1 if the call produces a chat message (call_windows.talk), else -1
  x_ij(c)     1 if sender j posted >= 1 agent chat message in i's room in [t_call(prev call of i), t_call(c))
              (the ledger's visibility rule: new at c iff posted at or after the previous receiving call's t_call)
  xp_ij(c)    1 if j posted in i's room in (t_call(c), t_first(c)): during c's model call, unreadable by c
              (H67's matched-lag in-flight placebo)
  hum_i(c)    number of human messages in i's room in the read window
  sprev_i(c)  the spin of i's previous non-summary call on the same PT day (0 for the first call of a day)
  wake(c)     gap_kind in {pause, pause_early, first_of_day, after_summary, session_start, marker}
  mode(c)     0 = chat context, 1 = computer-use context

Library:
  load_calls(goal_nos, days=None, exclude_agents=(19,))  -> calls frame (sorted by t_call, turn_id)
  load_messages(goal_nos, days=None)                      -> agent and human chat messages (t, room, agent, kind)
  build_inputs(calls, msgs, agents)                       -> (calls with columns, XR, XP) for the agent list
  validate_against_ledger(calls, XR, agents)              -> share of calls whose read sender set equals the ledger's
  all_present_trim(calls, min_calls=20)                   -> boolean mask of calls inside each day's all-present span
  simulate(calls, agents, h, J_of, Jself, seed)           -> synthetic spins and inputs on the real call skeleton
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import bisect  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
SH = ROOT / "data/processed/shared"
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import holdout_mask  # noqa: E402

# Confirm-only switch: guarded confirm scripts set this in memory (never the CLI, never exploration code).
ALLOW_HOLDOUT = False

WAKE = {"pause", "pause_early", "first_of_day", "after_summary", "session_start", "marker"}
US = 1_000_000


def _us(col: pl.Series) -> np.ndarray:
    return col.dt.epoch("us").to_numpy().astype(np.int64)


def _guard(df: pl.DataFrame, what: str):
    if df.height == 0 or ALLOW_HOLDOUT:
        return
    hm = np.array(holdout_mask(df["pt_date"].to_list(), df["goal_no"].to_list()))
    if hm.any() or ("holdout" in df.columns and df["holdout"].any()):
        raise RuntimeError(f"callspins: held-out rows reached {what}; refusing")


def load_calls(goal_nos, days=None, exclude_agents=(19,), include_holdout: bool = False) -> pl.DataFrame:
    """Non-summary, non-holdout calls of the listed goal periods (and days), with the call's room.
    include_holdout=True only when ALLOW_HOLDOUT was set by a guarded confirm script."""
    if include_holdout and not ALLOW_HOLDOUT:
        raise RuntimeError("callspins: include_holdout needs ALLOW_HOLDOUT (guarded confirm scripts only)")
    hk = pl.lit(True) if include_holdout else ~pl.col("holdout")
    q = (pl.scan_parquet(SH / "call_windows.parquet")
         .filter(pl.col("goal_no").is_in(list(goal_nos)) & hk & (pl.col("ctx_mode") != "summary")))
    if days is not None:
        q = q.filter(pl.col("pt_date").is_in(list(days)))
    cw = q.select("turn_id", "agent", "pt_date", "goal_no", "holdout", "t_call", "t_first", "talk", "ctx_mode",
                  "gap_kind", "kind").collect()
    cw = cw.filter(~pl.col("agent").is_in(list(exclude_agents)))
    rm = (pl.scan_parquet(SH / "context_ledger_turns.parquet").filter(pl.col("goal_no").is_in(list(goal_nos)))
          .select("turn_id", "room").collect())
    cw = cw.join(rm, on="turn_id", how="left").with_columns(pl.col("room").fill_null(-1))
    _guard(cw, "load_calls")
    return cw.sort("t_call", "turn_id")


def load_messages(goal_nos, days=None, include_holdout: bool = False) -> pl.DataFrame:
    if include_holdout and not ALLOW_HOLDOUT:
        raise RuntimeError("callspins: include_holdout needs ALLOW_HOLDOUT (guarded confirm scripts only)")
    q = (pl.scan_parquet(SH / "chat_core.parquet")
         .filter(pl.col("goal_no").is_in(list(goal_nos)) & pl.col("speaker_kind").is_in(["agent", "human"])))
    if days is not None:
        q = q.filter(pl.col("pt_date").is_in(list(days)))
    m = q.select("message_id", "t", "pt_date", "goal_no", "room", "speaker_kind", "agent").collect()
    _guard(m, "load_messages")
    return m.sort("t")


def build_inputs(calls: pl.DataFrame, msgs: pl.DataFrame, agents: list[int]):
    """Add s, sprev, wake, mode, t_prev, hum to calls; return (calls, XR, XP) with XR/XP columns = agents order."""
    calls = calls.sort("t_call", "turn_id")
    tc = _us(calls["t_call"])
    tf = _us(calls["t_first"])
    ag = calls["agent"].to_numpy()
    day = calls["pt_date"].to_numpy()
    room = calls["room"].to_numpy()
    n = calls.height
    # previous non-summary call of the same agent (any day: the ledger's previous receiving call)
    tprev = np.full(n, np.iinfo(np.int64).min // 4, dtype=np.int64)
    sprev = np.zeros(n, dtype=np.int8)
    talk = calls["talk"].to_numpy().astype(bool)
    s = np.where(talk, 1, -1).astype(np.int8)
    last_t, last_s, last_d = {}, {}, {}
    for k in range(n):
        a = ag[k]
        if a in last_t:
            tprev[k] = last_t[a]
            if last_d[a] == day[k]:
                sprev[k] = last_s[a]
        last_t[a], last_s[a], last_d[a] = tc[k], s[k], day[k]
    am = msgs.filter(pl.col("speaker_kind") == "agent")
    hm = msgs.filter(pl.col("speaker_kind") == "human")
    idx = {a: q for q, a in enumerate(agents)}
    XR = np.zeros((n, len(agents)), dtype=np.uint8)
    XP = np.zeros((n, len(agents)), dtype=np.uint8)
    for (r, a), g in am.group_by(["room", "agent"]):
        if a not in idx:
            continue
        t = np.sort(_us(g["t"]))
        sel = (room == r) & (ag != a)
        if not sel.any():
            continue
        lo = np.searchsorted(t, tprev[sel], "left")
        hi = np.searchsorted(t, tc[sel], "left")
        XR[sel, idx[a]] = (hi > lo).astype(np.uint8)
        lo2 = np.searchsorted(t, tc[sel], "right")
        hi2 = np.searchsorted(t, tf[sel], "left")
        XP[sel, idx[a]] = (hi2 > lo2).astype(np.uint8)
    hum = np.zeros(n, dtype=np.int16)
    for (r,), g in hm.group_by(["room"]):
        t = np.sort(_us(g["t"]))
        sel = room == r
        hum[sel] = (np.searchsorted(t, tc[sel], "left") - np.searchsorted(t, tprev[sel], "left")).astype(np.int16)
    calls = calls.with_columns(
        pl.Series("s", s), pl.Series("sprev", sprev),
        pl.Series("wake", np.isin(calls["gap_kind"].cast(pl.String).to_numpy(), list(WAKE)).astype(np.int8)),
        pl.Series("mode", (calls["ctx_mode"].cast(pl.String) == "cu").to_numpy().astype(np.int8)),
        pl.Series("t_prev_us", tprev), pl.Series("hum", hum))
    return calls, XR, XP


def validate_against_ledger(calls: pl.DataFrame, XR: np.ndarray, agents: list[int]) -> dict:
    """Share of calls whose read sender set (agent senders in `agents`) equals the ledger items' sender set."""
    items = (pl.scan_parquet(SH / "context_ledger_items.parquet")
             .filter(pl.col("turn_id").is_in(calls["turn_id"].to_list()) & (pl.col("kind") == "agent"))
             .select("turn_id", "sender").collect())
    idx = {a: q for q, a in enumerate(agents)}
    pos = {t: k for k, t in enumerate(calls["turn_id"].to_list())}
    L = np.zeros_like(XR)
    for t, snd in items.iter_rows():
        if snd in idx and t in pos:
            L[pos[t], idx[snd]] = 1
    eq = (L == XR).all(1)
    return {"n_calls": int(len(eq)), "share_equal": float(eq.mean()), "cells_mine": int(XR.sum()),
            "cells_ledger": int(L.sum()), "cells_both": int((L & XR).sum())}


def all_present_trim(calls: pl.DataFrame, min_calls: int = 20) -> np.ndarray:
    """Per PT day: keep calls between the latest first call and the earliest last call of present agents
    (agents with >= min_calls calls that day). Days where the span is empty keep nothing."""
    tc = _us(calls["t_call"])
    keep = np.zeros(calls.height, dtype=bool)
    d = calls["pt_date"].to_numpy()
    a = calls["agent"].to_numpy()
    for day in np.unique(d):
        m = d == day
        firsts, lasts = [], []
        for ag in np.unique(a[m]):
            mm = m & (a == ag)
            if mm.sum() >= min_calls:
                firsts.append(tc[mm].min())
                lasts.append(tc[mm].max())
        if firsts:
            lo, hi = max(firsts), min(lasts)
            keep |= m & (tc >= lo) & (tc <= hi)
    return keep


def simulate(calls: pl.DataFrame, agents: list[int], h: np.ndarray, J_of, Jself, seed: int,
             post_lag_us: np.ndarray | None = None):
    """Kinetic Ising on the real call skeleton and update order.

    calls: output of build_inputs (sorted by t_call); h: per-call field in Ising units; J_of(k) -> (A x A) coupling
    matrix in Ising units for call k (row = recipient, column = sender; may depend on time); Jself: per-agent self
    coupling (array over agents). A talking call posts one message at its real t_first (or t_call + post_lag).
    Returns (s, XR, XP) with the same rule as build_inputs (one room per call, read window [t_prev, t_call))."""
    rng = np.random.default_rng(seed)
    tc = _us(calls["t_call"])
    tf = _us(calls["t_first"]) if post_lag_us is None else tc + post_lag_us
    tprev = calls["t_prev_us"].to_numpy()
    ag = calls["agent"].to_numpy()
    room = calls["room"].to_numpy()
    day = calls["pt_date"].to_numpy()
    idx = {a: q for q, a in enumerate(agents)}
    ai = np.array([idx.get(a, -1) for a in ag])
    n = calls.height
    A = len(agents)
    posts: dict = {}
    s = np.empty(n, dtype=np.int8)
    XR = np.zeros((n, A), dtype=np.uint8)
    last_s, last_d = {}, {}
    u = rng.random(n)
    for k in range(n):
        i = ai[k]
        x = XR[k]
        r = room[k]
        for q in range(A):
            if q == i:
                continue
            lst = posts.get((r, q))
            if lst:
                lo = bisect.bisect_left(lst, tprev[k])
                if lo < len(lst) and lst[lo] < tc[k]:
                    x[q] = 1
        sp = last_s.get(i, 0) if last_d.get(i) == day[k] else 0
        J = J_of(k)
        H = h[k] + Jself[i] * sp + float(J[i] @ x)
        p = 1.0 / (1.0 + np.exp(-2.0 * H))
        s[k] = 1 if u[k] < p else -1
        last_s[i], last_d[i] = s[k], day[k]
        if s[k] == 1:
            bisect.insort(posts.setdefault((r, i), []), int(tf[k]))
    XP = np.zeros((n, A), dtype=np.uint8)
    for (r, q), lst in posts.items():
        t = np.asarray(lst, dtype=np.int64)
        sel = (room == r) & (ai != q)
        lo = np.searchsorted(t, tc[sel], "right")
        hi = np.searchsorted(t, tf[sel], "left")
        XP[sel, q] = (hi > lo).astype(np.uint8)
    return s, XR, XP


# ============================================================================ penalized logistic (shared by the fits)
def fit_logit(X: np.ndarray, y01: np.ndarray, lam: np.ndarray, beta0: np.ndarray | None = None, se: bool = False,
              maxiter: int = 500):
    """min sum[log(1+e^eta) - y eta] + 1/2 sum lam_k b_k^2, eta = X b (L-BFGS-B). Returns (b, cov or None).
    Coefficients are logits; divide by 2 for Ising units (P(s=+1) = e^H / 2cosh H = sigmoid(2H))."""
    from scipy.optimize import minimize
    X = np.asarray(X, dtype=np.float64)
    y = np.asarray(y01, dtype=np.float64)
    lam = np.broadcast_to(np.asarray(lam, dtype=np.float64), (X.shape[1],)).copy()

    def f(b):
        eta = X @ b
        ll = np.logaddexp(0, eta) - y * eta
        p = 0.5 * (1 + np.tanh(0.5 * eta))
        return ll.sum() + 0.5 * (lam * b * b).sum(), X.T @ (p - y) + lam * b

    b0 = np.zeros(X.shape[1]) if beta0 is None else beta0
    r = minimize(f, b0, jac=True, method="L-BFGS-B", options={"maxiter": maxiter, "gtol": 1e-6})
    b = r.x
    cov = None
    if se:
        p = 0.5 * (1 + np.tanh(0.5 * (X @ b)))
        Hs = (X * (p * (1 - p))[:, None]).T @ X + np.diag(lam)
        cov = np.linalg.pinv(Hs)
    return b, cov
