"""H43 round 2 library: timer-wake tables with nudge and directed-read histories, receiving-call dose tables, a
fixed-effect logit (exact Newton with the group intercepts profiled out), day-block bootstraps and random-effects
pooling. Used identically by `synthetic_r2.py` (simulated outcomes on the real skeleton) and `run_r2.py` (real outcomes).

Shared inputs only (data/processed/shared/), non-reserved rows only (common.holdout_mask re-checked on every load):
  idle_gates/idle_gates.parquet   timer wakes (call clock); after-PAUSE wakes are prev_kind == "pause"
  kicks_receipts, kicks_targets   nudge receipts at the receiving call; the nudge target is its leading @ (H35 rule)
  context_ledger_items / _turns   items read per call (kind, ment, uncertain, age_s); context resets per call
  call_windows                    t_call bounds (t_call_lo, t_call_hi), start_src (logged = Gemini HTTP timing)
  sustained_run_starts            rule h43_gap (>= 3 consecutive active calls; H43 round-1 definition)
No text is read. Round-1 code (h43lib.py and the scripts that use it) is untouched.
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

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H43-kick-refractory-window/r2"
NE43 = "2026-08-21"
PRE_WIN = ("2026-08-06", "2026-08-21")       # round-1 NE43 before window [from, to)
POST_WIN = ("2026-08-21", "2026-09-05")      # after window (non-reserved #51 days up to 09-04)
REGIME3 = (36, 37, 38, 39, 40, 41, 42, 44, 51)
FOCUS_ROOM = 15
LOOK_N = 240 * 60          # prior-nudge lookback (s)
FRESH_S = 60 * 60          # fresh wake: no directed read in the previous 60 min
REKICK_S = 120 * 60        # re-kicked wake: an effective directed read in the previous 120 min
EFFECTIVE_S = 15 * 60      # effective = a sustained run starts within 15 min of the read
SEED = 20261005


def ep(col: str) -> pl.Expr:
    return (pl.col(col).dt.epoch("us") / 1e6).alias(col)


def assert_open(df: pl.DataFrame):
    hm = holdout_mask(df["pt_date"].to_list(), df["goal_no"].to_list())
    assert not any(hm), "reserved rows in an exploratory load"


def jdump(obj, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)

    def conv(o):
        if isinstance(o, (np.floating, float)):
            return None if not np.isfinite(o) else float(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, np.bool_):
            return bool(o)
        if isinstance(o, np.ndarray):
            return [conv(x) for x in o.tolist()]
        if isinstance(o, dict):
            return {str(k): conv(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [conv(x) for x in o]
        return o
    path.write_text(json.dumps(conv(obj), indent=1))


# ============================================================================== fixed-effect logit

def _sig(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -35, 35)))


def fe_logit(X: np.ndarray, y: np.ndarray, g: np.ndarray, maxit: int = 60, tol: float = 1e-9, ridge=1e-6):
    """Logit with one intercept per group g (no global intercept in X). Exact Newton: the group intercepts are
    profiled out with the Schur complement. Groups whose outcomes do not vary are dropped (they carry no information
    on beta). Returns dict(beta, cov, keep, n, n_groups, converged)."""
    g = np.asarray(g)
    _, gi = np.unique(g, return_inverse=True)
    G = gi.max() + 1
    s = np.bincount(gi, weights=y, minlength=G)
    c = np.bincount(gi, minlength=G).astype(float)
    ok_g = (s > 0) & (s < c)
    keep = ok_g[gi]
    X, y, gi = X[keep], y[keep], gi[keep]
    _, gi = np.unique(gi, return_inverse=True)
    G = gi.max() + 1 if len(gi) else 0
    n, p = X.shape
    ridge = np.broadcast_to(np.asarray(ridge, float), (p,)) if np.ndim(ridge) else np.full(p, float(ridge))
    if n == 0 or G == 0:
        return {"beta": np.full(p, np.nan), "cov": np.full((p, p), np.nan), "keep": keep, "n": 0, "n_groups": 0,
                "converged": False}
    m = np.bincount(gi, weights=y, minlength=G) / np.bincount(gi, minlength=G)
    alpha = np.log(np.clip(m, 1e-3, 1 - 1e-3) / (1 - np.clip(m, 1e-3, 1 - 1e-3)))
    beta = np.zeros(p)
    conv = False
    ll_old = -np.inf
    for _ in range(maxit):
        eta = X @ beta + alpha[gi]
        mu = _sig(eta)
        W = np.maximum(mu * (1 - mu), 1e-10)
        r = y - mu
        gb = X.T @ r - ridge * beta
        ga = np.bincount(gi, weights=r, minlength=G)
        Daa = np.bincount(gi, weights=W, minlength=G)
        XW = X * W[:, None]
        Hbb = X.T @ XW + np.diag(ridge)
        Hba = np.zeros((p, G))
        for j in range(p):
            Hba[j] = np.bincount(gi, weights=XW[:, j], minlength=G)
        S = Hbb - (Hba / Daa[None, :]) @ Hba.T
        rhs = gb - Hba @ (ga / Daa)
        try:
            db = np.linalg.solve(S, rhs)
        except np.linalg.LinAlgError:
            db = np.linalg.lstsq(S, rhs, rcond=None)[0]
        da = (ga - Hba.T @ db) / Daa
        t = 1.0
        for _h in range(25):
            bn, an = beta + t * db, alpha + t * da
            mun = _sig(X @ bn + an[gi])
            ll = float(np.sum(y * np.log(np.clip(mun, 1e-12, 1)) + (1 - y) * np.log(np.clip(1 - mun, 1e-12, 1)))) - 0.5 * float(np.sum(ridge * bn ** 2))
            if ll >= ll_old - 1e-9:
                break
            t /= 2
        beta, alpha = bn, an
        if abs(ll - ll_old) < tol * (1 + abs(ll)) and np.max(np.abs(t * db)) < 1e-7:
            conv = True
            break
        ll_old = ll
    eta = X @ beta + alpha[gi]
    mu = _sig(eta)
    W = np.maximum(mu * (1 - mu), 1e-10)
    XW = X * W[:, None]
    Daa = np.bincount(gi, weights=W, minlength=G)
    Hba = np.zeros((p, G))
    for j in range(p):
        Hba[j] = np.bincount(gi, weights=XW[:, j], minlength=G)
    S = X.T @ XW + np.diag(ridge) - (Hba / Daa[None, :]) @ Hba.T
    try:
        cov = np.linalg.inv(S)
    except np.linalg.LinAlgError:
        cov = np.linalg.pinv(S)
    return {"beta": beta, "cov": cov, "keep": keep, "n": int(n), "n_groups": int(G), "converged": conv,
            "alpha": alpha, "gi": gi, "mu": mu}


def rows_by_day(day: np.ndarray) -> list:
    order = np.argsort(day, kind="stable")
    d = day[order]
    cuts = np.flatnonzero(np.diff(d)) + 1
    return np.split(order, cuts)


def day_boot(day: np.ndarray, rng, B: int):
    rb = rows_by_day(day)
    k = len(rb)
    for _ in range(B):
        pick = rng.integers(0, k, size=k)
        yield np.concatenate([rb[i] for i in pick])


def summarize(point: float, draws) -> dict:
    d = np.asarray([x for x in draws if x is not None and np.isfinite(x)], float)
    if len(d) < 10 or not np.isfinite(point):
        return {"est": point, "se": np.nan, "ci": [np.nan, np.nan], "n_draws": int(len(d))}
    return {"est": float(point), "se": float(np.std(d, ddof=1)), "ci": [float(np.percentile(d, 2.5)),
                                                                       float(np.percentile(d, 97.5))],
            "n_draws": int(len(d))}


def dl_pool(est, se) -> dict:
    """DerSimonian-Laird random effects; empirical-Bayes shrunk study values."""
    est, se = np.asarray(est, float), np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[ok], se[ok]
    k = len(est)
    if k == 0:
        return {"k": 0}
    w = 1 / se ** 2
    mu_f = np.sum(w * est) / np.sum(w)
    Q = float(np.sum(w * (est - mu_f) ** 2))
    C = np.sum(w) - np.sum(w ** 2) / np.sum(w)
    tau2 = max(0.0, (Q - (k - 1)) / C) if k > 1 and C > 0 else 0.0
    ws = 1 / (se ** 2 + tau2)
    mu = float(np.sum(ws * est) / np.sum(ws))
    smu = float(np.sqrt(1 / np.sum(ws)))
    I2 = max(0.0, (Q - (k - 1)) / Q) if k > 1 and Q > 0 else 0.0
    B = tau2 / (tau2 + se ** 2) if tau2 > 0 else np.zeros(k)
    eb = mu + B * (est - mu)
    return {"k": k, "mu": mu, "se": smu, "ci": [mu - 1.96 * smu, mu + 1.96 * smu], "tau2": tau2, "Q": Q, "I2": I2,
            "eb": eb.tolist(), "mask": ok.tolist()}


# ============================================================================== timer wakes

def load_wakes(goal_nos=REGIME3, after_pause: bool = True, date_from: str | None = None,
               date_to: str | None = None) -> pl.DataFrame:
    g = pl.read_parquet(SH / "idle_gates/idle_gates.parquet").filter(pl.col("goal_no").is_in(list(goal_nos)))
    if after_pause:
        g = g.filter(pl.col("prev_kind") == "pause")
    if date_from:
        g = g.filter(pl.col("pt_date") >= date_from)
    if date_to:
        g = g.filter(pl.col("pt_date") < date_to)
    g = g.filter(pl.col("y_sus").is_not_null())
    assert_open(g)
    g = g.with_columns(ep("t_call")).sort("agent", "pt_date", "t_call", "turn_id")
    age = pl.coalesce(pl.col("a_sus"), pl.col("a_any"), pl.lit(60.0)).clip(5.0, None)
    g = g.with_columns(
        age.alias("age_s"), pl.col("a_sus").is_null().alias("no_sus"),
        pl.col("k_sus").cast(pl.Float64).alias("k"),
        (pl.col("n_nudge_me") > 0).alias("N_now"), (pl.col("n_dir") > 0).alias("D_now"),
        ((pl.col("n_dir") - pl.col("n_nudge_me")).clip(0, None) > 0).alias("D_other"),
        (pl.col("n_peer") - pl.col("n_ment_agent") - pl.col("n_human_named")).clip(0, None).alias("n_peer_und"),
        (pl.col("room") == FOCUS_ROOM).alias("focus"),
        (pl.col("goal_no").cast(pl.Utf8) + "|" + pl.col("pt_date")).alias("gday"),
        (pl.col("agent").cast(pl.Utf8) + "|" + pl.col("pt_date")).alias("aday"),
    )
    # trap id: a new trap starts where k_sus restarts at 1 inside an agent-day
    g = g.with_columns(((pl.col("k_sus") <= pl.col("k_sus").shift(1).over("aday")) | pl.col("k_sus").shift(1).over("aday").is_null())
                       .cast(pl.Int32).cum_sum().alias("trap"))
    return g


def nudge_receipts() -> pl.DataFrame:
    kr = (pl.read_parquet(SH / "kicks_receipts.parquet")
          .filter((pl.col("kind") == "nudge") & pl.col("is_primary") & ~pl.col("holdout") & pl.col("turn_id").is_not_null())
          .select("agent", "turn_id", pl.col("rc_date").alias("pt_date"), ep("t_call")))
    return kr.sort("agent", "t_call")


def reset_calls(goal_nos) -> pl.DataFrame:
    tu = (pl.scan_parquet(SH / "context_ledger_turns.parquet")
          .filter(pl.col("goal_no").is_in(list(goal_nos)) & ~pl.col("holdout")
                  & (pl.col("reset_consol") | pl.col("reset_forced") | pl.col("reset_session")))
          .select("agent", "pt_date", ep("t_call"), "reset_forced").collect())
    return tu.sort("agent", "t_call")


def sustained_starts(goal_nos) -> pl.DataFrame:
    s = (pl.read_parquet(SH / "sustained_run_starts.parquet")
         .filter((pl.col("rule") == "h43_gap") & pl.col("goal_no").is_in(list(goal_nos)) & ~pl.col("holdout"))
         .select("agent", "pt_date", ep("t_start")))
    return s.sort("agent", "t_start")


def directed_calls(goal_nos) -> pl.DataFrame:
    """Calls (any kind, non-summary) that read >= 1 directed item: named agent/human item, or a nudge whose leading @
    is the recipient. Columns agent, pt_date, t_call, turn_id, n_dir."""
    cw = (pl.scan_parquet(SH / "call_windows.parquet")
          .filter(pl.col("goal_no").is_in(list(goal_nos)) & ~pl.col("holdout") & (pl.col("ctx_mode").cast(pl.Utf8) != "summary"))
          .select("turn_id", "agent", "pt_date", "goal_no", ep("t_call")).collect())
    it = (pl.scan_parquet(SH / "context_ledger_items.parquet").filter(~pl.col("omitted"))
          .select("turn_id", "message_id", pl.col("kind").cast(pl.Utf8), "ment")
          .filter(pl.col("turn_id").is_in(cw["turn_id"].implode())).collect())
    kt = pl.read_parquet(SH / "kicks_targets.parquet").filter(pl.col("kind").cast(pl.Utf8) == "nudge").select("message_id", "primary_target")
    it = it.join(cw.select("turn_id", "agent"), on="turn_id").join(kt, on="message_id", how="left")
    it = it.filter((pl.col("kind").is_in(["agent", "human"]) & pl.col("ment"))
                   | ((pl.col("kind") == "nudge") & (pl.col("primary_target") == pl.col("agent"))))
    d = it.group_by("turn_id").agg(pl.len().alias("n_dir"))
    out = cw.join(d, on="turn_id").sort("agent", "t_call")
    assert_open(out)
    return out


def _last_before(q_agent, q_day, q_t, ev_agent, ev_day, ev_t, strict=True):
    """For each query, time of the last event of the same agent-day strictly before (or at) q_t; nan if none."""
    out = np.full(len(q_t), np.nan)
    key_ev = {}
    for i, (a, d) in enumerate(zip(ev_agent, ev_day)):
        key_ev.setdefault((a, d), []).append(i)
    for (a, d), idx in key_ev.items():
        idx = np.array(idx)
        te = ev_t[idx]
        o = np.argsort(te)
        te = te[o]
        m = (q_agent == a) & (q_day == d)
        if not m.any():
            continue
        j = np.searchsorted(te, q_t[m], "left" if strict else "right") - 1
        v = np.full(m.sum(), np.nan)
        v[j >= 0] = te[j[j >= 0]]
        out[m] = v
    return out


def _count_between(q_agent, q_day, lo, hi, ev_agent, ev_day, ev_t):
    """Number of same agent-day events with lo < t <= hi."""
    out = np.zeros(len(lo), np.int64)
    groups = {}
    for i, (a, d) in enumerate(zip(ev_agent, ev_day)):
        groups.setdefault((a, d), []).append(i)
    for (a, d), idx in groups.items():
        te = np.sort(ev_t[np.array(idx)])
        m = (q_agent == a) & (q_day == d)
        if not m.any():
            continue
        out[m] = np.searchsorted(te, hi[m], "right") - np.searchsorted(te, lo[m], "right")
    return out


def add_nudge_history(w: pl.DataFrame) -> pl.DataFrame:
    """Prior-nudge state and class of the nudge read now (R2)."""
    kr = nudge_receipts()
    A, D, T = w["agent"].to_numpy(), w["pt_date"].to_numpy(), w["t_call"].to_numpy()
    tprev = _last_before(A, D, T, kr["agent"].to_numpy(), kr["pt_date"].to_numpy(), kr["t_call"].to_numpy(), strict=True)
    dt = T - tprev
    has = np.isfinite(dt) & (dt <= LOOK_N)
    age = w["age_s"].to_numpy()
    nosus = w["no_sus"].to_numpy()
    same = has & (nosus | (dt <= age))
    state = np.where(~has, 0, np.where(same, 1, 2))          # 0 none, 1 same trap, 2 before the last sustained run
    rs = reset_calls(sorted(set(w["goal_no"].to_list())))
    nres = _count_between(A, D, np.where(has, tprev, T), T, rs["agent"].to_numpy(), rs["pt_date"].to_numpy(),
                          rs["t_call"].to_numpy())
    return w.with_columns(pl.Series("nprev_state", state.astype(np.int8)), pl.Series("dt_prevN", np.where(has, dt, np.nan)),
                          pl.Series("reset_between", (has & (nres > 0))))


ISO_S = 30 * 60            # amendment A2-1: an effective primer must itself follow 30 min without a directed read


def add_directed_history(w: pl.DataFrame, strict: bool = True) -> pl.DataFrame:
    """R5 classes: fresh / re-kicked / other, from the agent's earlier directed reads (any call) and sustained runs.
    strict=True (amendment A2-1, primary): the effective primer must be isolated (no directed read in the 30 min
    before it), as round-1 primers were; strict=False is the pre-registered loose class (sensitivity)."""
    gs = sorted(set(w["goal_no"].to_list()))
    dc = directed_calls(gs)
    ss = sustained_starts(gs)
    A, D, T = w["agent"].to_numpy(), w["pt_date"].to_numpy(), w["t_call"].to_numpy()
    tlast = _last_before(A, D, T, dc["agent"].to_numpy(), dc["pt_date"].to_numpy(), dc["t_call"].to_numpy(), strict=True)
    fresh = ~(np.isfinite(tlast) & (T - tlast <= FRESH_S))
    # effective directed reads: a sustained run starts within 15 min after the read
    da, dd, dtt = dc["agent"].to_numpy(), dc["pt_date"].to_numpy(), dc["t_call"].to_numpy()
    sa, sd, st = ss["agent"].to_numpy(), ss["pt_date"].to_numpy(), ss["t_start"].to_numpy()
    groups = {}
    for i, (a, d) in enumerate(zip(sa, sd)):
        groups.setdefault((a, d), []).append(i)
    run_after = np.full(len(dtt), np.nan)
    for (a, d), idx in groups.items():
        ts = np.sort(st[np.array(idx)])
        m = (da == a) & (dd == d)
        if not m.any():
            continue
        j = np.searchsorted(ts, dtt[m], "left")
        v = np.full(m.sum(), np.nan)
        okj = j < len(ts)
        v[okj] = ts[j[okj]]
        run_after[m] = v
    eff = np.isfinite(run_after) & (run_after - dtt <= EFFECTIVE_S)
    if strict:
        prev_d = np.r_[np.nan, dtt[:-1]]
        same = np.r_[False, (da[1:] == da[:-1]) & (dd[1:] == dd[:-1])]
        iso = ~same | (dtt - prev_d > ISO_S)
        eff &= iso
    # for each wake: latest effective directed read in (T - 120 min, T) whose run started before T
    ea, ed, et, er = da[eff], dd[eff], dtt[eff], run_after[eff]
    rek = np.zeros(len(T), bool)
    groups = {}
    for i, (a, d) in enumerate(zip(ea, ed)):
        groups.setdefault((a, d), []).append(i)
    for (a, d), idx in groups.items():
        idx = np.array(idx)
        o = np.argsort(et[idx])
        te, tr = et[idx][o], er[idx][o]
        m = np.flatnonzero((A == a) & (D == d))
        for i in m:
            j = np.searchsorted(te, T[i], "left") - 1
            while j >= 0 and T[i] - te[j] <= REKICK_S:
                if tr[j] < T[i]:
                    rek[i] = True
                    break
                j -= 1
    cls = np.where(rek, 1, np.where(fresh, 0, 2)).astype(np.int8)    # 0 fresh, 1 re-kicked, 2 other
    return w.with_columns(pl.Series("dclass", cls), pl.Series("dt_lastD", T - tlast))


# ============================================================================== wake design matrices

HBINS = [1.0, 2.0, 4.0, 6.0]


def nuisance(w: pl.DataFrame, extra: tuple = ()) -> tuple[np.ndarray, list[str]]:
    cols, names = [], []
    cols.append(np.log(w["k"].to_numpy())); names.append("ln_k")
    cols.append(np.log(w["age_s"].to_numpy() / 60.0)); names.append("ln_age_min")
    cols.append(w["no_sus"].to_numpy().astype(float)); names.append("no_sus")
    cols.append(np.log(np.clip(w["prev_pause_s"].fill_null(180.0).to_numpy(), 10, None))); names.append("ln_pause")
    h = w["h_day"].fill_null(0.0).to_numpy()
    hb = np.digitize(h, HBINS)
    for b in range(1, len(HBINS) + 1):
        cols.append((hb == b).astype(float)); names.append(f"hday_{b}")
    cols.append(w["swarm_act10"].fill_null(0.0).to_numpy()); names.append("swarm_act10")
    cols.append(np.log1p(w["n_peer_und"].to_numpy())); names.append("ln1p_peer_und")
    for e in extra:
        cols.append(w[e].to_numpy().astype(float)); names.append(e)
    return np.column_stack(cols), names


def r2_design(w: pl.DataFrame, proxies: bool = False, split_refire: bool = False):
    """R2 wake model. Treatment columns: N_first, N_refire (or N_ref_same/N_ref_new); prior-state dummies."""
    X0, nm = nuisance(w, extra=("D_other",))
    st = w["nprev_state"].to_numpy()
    N = w["N_now"].to_numpy()
    cols = [X0, (st == 1).astype(float)[:, None], (st == 2).astype(float)[:, None]]
    nm = nm + ["prior_same", "prior_new"]
    first = N & (st == 0)
    if split_refire:
        cols += [first[:, None], (N & (st == 1))[:, None], (N & (st == 2))[:, None]]
        nm += ["N_first", "N_ref_same", "N_ref_new"]
    else:
        cols += [first[:, None], (N & (st > 0))[:, None]]
        nm += ["N_first", "N_refire"]
    if proxies:
        lk = np.log(w["k"].to_numpy())
        la = np.log(w["age_s"].to_numpy() / 60.0)
        rec = (w["age_s"].to_numpy() < 1800) & ~w["no_sus"].to_numpy()
        cols += [(N * (lk - 1.0))[:, None], (N * (la - 2.0))[:, None], (N * rec)[:, None]]
        nm += ["N_x_lnk", "N_x_lnage", "N_x_recent"]
    X = np.hstack([c.astype(float) for c in cols])
    return X, nm


def r5_design(w: pl.DataFrame):
    X0, nm = nuisance(w)
    c = w["dclass"].to_numpy()
    D = w["D_now"].to_numpy()
    cols = [X0, (c == 1).astype(float)[:, None], (c == 2).astype(float)[:, None],
            (D & (c == 0))[:, None], (D & (c == 1))[:, None], (D & (c == 2))[:, None]]
    nm = nm + ["cls_rekick", "cls_other", "D_fresh", "D_rekick", "D_oth"]
    return np.hstack([x.astype(float) for x in cols]), nm


def coef(fit, names, name):
    j = names.index(name)
    return float(fit["beta"][j]), float(np.sqrt(fit["cov"][j, j]))


# ============================================================================== receiving-call dose table (R3)

def dose_table(goal_nos, read_state: str = "active") -> pl.DataFrame:
    """One row per receiving call (non-summary, not first of day), with directed dose under the ledger assignment and
    with the call boundaries moved to t_call_lo / t_call_hi (S4), undirected counts, window, logged-start flag and the
    uncertain flag (this call's or the previous call's items). read_state: 'active' (not idle at read) or 'any'."""
    cw = (pl.scan_parquet(SH / "call_windows.parquet")
          .filter(pl.col("goal_no").is_in(list(goal_nos)) & ~pl.col("holdout") & (pl.col("ctx_mode").cast(pl.Utf8) != "summary"))
          .select("turn_id", "agent", "pt_date", "goal_no", pl.col("regime").cast(pl.Utf8), pl.col("kind").cast(pl.Utf8), "talk",
                  ep("t_call"), ep("t_call_lo"), ep("t_call_hi"), ep("t_end"), "first_of_day",
                  (pl.col("start_src").cast(pl.Utf8) == "logged").alias("logged"))
          .collect().sort("agent", "pt_date", "t_call", "turn_id"))
    assert_open(cw)
    cw = cw.with_columns((pl.col("kind").is_in(["pause", "wait"]) & ~pl.col("talk")).alias("idle_call"))
    cw = cw.with_columns(
        pl.col("t_call").shift(1).over("agent", "pt_date").alias("t_prev"),
        pl.col("t_end").shift(1).over("agent", "pt_date").alias("tend_prev"),
        pl.col("idle_call").shift(1).over("agent", "pt_date").alias("prev_idle"),
        pl.col("talk").shift(1).over("agent", "pt_date").alias("prev_talk"),
        pl.col("t_call_lo").cum_max().over("agent", "pt_date").alias("b_lo"),
        pl.col("t_call_hi").cum_max().over("agent", "pt_date").alias("b_hi"))
    cw = cw.with_columns((pl.col("prev_idle") | ((pl.col("t_call") - pl.col("tend_prev")) >= 180)).fill_null(False).alias("idle_at_read"))
    it = (pl.scan_parquet(SH / "context_ledger_items.parquet").filter(~pl.col("omitted"))
          .select("turn_id", "message_id", pl.col("kind").cast(pl.Utf8), "ment", "uncertain", "age_s")
          .filter(pl.col("turn_id").is_in(cw["turn_id"].implode())).collect())
    kt = pl.read_parquet(SH / "kicks_targets.parquet").filter(pl.col("kind").cast(pl.Utf8) == "nudge").select("message_id", "primary_target")
    it = it.join(cw.select("turn_id", "agent", "pt_date", "t_call"), on="turn_id").join(kt, on="message_id", how="left")
    it = it.with_columns(
        ((pl.col("kind").is_in(["agent", "human"]) & pl.col("ment"))
         | ((pl.col("kind") == "nudge") & (pl.col("primary_target") == pl.col("agent")))).alias("dir"),
        (pl.col("t_call") - pl.col("age_s")).alias("t_post"))
    per = it.group_by("turn_id").agg(
        pl.col("dir").sum().alias("dose"),
        ((pl.col("kind") == "agent") & ~pl.col("ment")).sum().alias("n_und_agent"),
        ((pl.col("kind") == "human") & ~pl.col("ment")).sum().alias("n_und_human"),
        pl.col("uncertain").any().alias("unc_here"),
        (pl.col("dir") & pl.col("uncertain")).any().alias("unc_dir"))
    cw = cw.join(per, on="turn_id", how="left").with_columns(
        [pl.col(c).fill_null(0) for c in ("dose", "n_und_agent", "n_und_human")] +
        [pl.col("unc_here").fill_null(False), pl.col("unc_dir").fill_null(False)])
    cw = cw.with_columns(pl.col("unc_here").shift(1).over("agent", "pt_date").fill_null(False).alias("unc_prev"))
    # S4 recount of directed items under shifted boundaries
    di = it.filter(pl.col("dir")).select("agent", "pt_date", "t_post")
    cw = cw.with_columns(pl.int_range(pl.len()).alias("_row"))
    lo = np.zeros(cw.height, np.int64)
    hi = np.zeros(cw.height, np.int64)
    rows = cw.select("_row", "agent", "pt_date", "b_lo", "b_hi")
    di_g = {k: v["t_post"].to_numpy() for k, v in di.group_by(["agent", "pt_date"])}
    for (a, d), sub in rows.group_by(["agent", "pt_date"]):
        tp = di_g.get((a, d))
        if tp is None or len(tp) == 0:
            continue
        r = sub["_row"].to_numpy()
        for arr, col in ((lo, "b_lo"), (hi, "b_hi")):
            b = sub[col].to_numpy()
            j = np.searchsorted(b, tp, "right")      # first call whose boundary is after the post time
            j = j[j < len(b)]
            np.add.at(arr, r[j], 1)
    cw = cw.with_columns(pl.Series("dose_lo", lo), pl.Series("dose_hi", hi))
    cw = cw.filter(pl.col("t_prev").is_not_null() & ~pl.col("first_of_day"))
    if read_state == "active":
        cw = cw.filter(~pl.col("idle_at_read"))
    cw = cw.with_columns((pl.col("t_call") - pl.col("t_prev")).clip(1.0, None).alias("window_s"),
                         (pl.col("agent").cast(pl.Utf8) + "|" + pl.col("pt_date")).alias("aday"))
    return cw.drop("_row")


def dose_design(d: pl.DataFrame, dose_col: str = "dose", window: bool = True):
    dose = d[dose_col].to_numpy()
    cols = [(dose == 1), (dose == 2), (dose >= 3)]
    nm = ["f1", "f2", "f3p"]
    if window:
        cols.append(np.log(d["window_s"].to_numpy())); nm.append("ln_window")
    cols += [np.log1p(d["n_und_agent"].to_numpy()), np.log1p(d["n_und_human"].to_numpy()),
             d["prev_talk"].fill_null(False).to_numpy()]
    nm += ["ln1p_und_agent", "ln1p_und_human", "prev_talk"]
    X = np.column_stack([np.asarray(c, float) for c in cols])
    return X, nm


def marginals(beta, names):
    f1, f2, f3 = (beta[names.index(k)] for k in ("f1", "f2", "f3p"))
    m2, m3 = f2 - f1, f3 - f2
    return {"f1": f1, "f2": f2, "f3p": f3, "m2": m2, "m3": m3, "rho2": m2 / f1 if f1 > 0.05 else np.nan}
