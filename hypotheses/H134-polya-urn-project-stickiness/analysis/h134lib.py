"""H134 library: call skeletons, the project self-share f_proj, the leave-hazard design, fits, day-blocked CV (aging
share eps(F)), forward simulation of dwell (O3), and the reset-step contrast (O4).

Card: hypotheses/H134-polya-urn-project-stickiness/README.md. Fits use infra/shared/hazard_fe.py (agent-FE logit).

Terms (card, Model):
  y      leave at own call c (the call touches a new project: a project hop (call), H133);
  F      ln(1 - f_proj(c)) with the amended ruler A1: 1 - f = (n_own - n_a + 1/2) / (n_own + 1/2), so f = 0 at a
         segment start (a reset sets the field to 0, as the card's Model says);
  A      ln d(c), d = own calls from the visit's first call to c (risk rows d >= 2);
  z      nuisance: hours since the day's window start (bins 1..6), kind of the previous own call, forced and voluntary
         reset at c, first call of the day;
  K      kick: ln(1 + N^nam_other(c)) when the label table carries it (else absent).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
import hazard_fe as HF  # noqa: E402
from common import holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H134-polya-urn-project-stickiness"
F_CAP = 0.98
E_EXPIRY = 100
SEED = 20261007
D_RESET = 10          # reset native: visits with d >= 10 at the reset call
PSEUDO_LAG = 20       # pseudo-reset placebo: 20 own calls before each forced reset
KM_D = (10, 30, 100, 300)


# ============================================================================ skeleton
def unit_days(unit: str) -> list[str]:
    pu = pl.read_parquet(SH / "period_units.parquet").filter(pl.col("unit_id") == unit)
    assert pu.height == 1, unit
    assert not pu["holdout"][0], f"{unit} is reserved"
    return sorted(pu["days"][0])


def load_skeleton(unit: str) -> pl.DataFrame:
    """All own calls (context-ledger turns) of the unit's agents, regime III, reserved rows dropped and asserted.
    Sorted by agent, t_call, turn_id. Adds seg (segment id per agent, cut at reset_consol | reset_session), day code,
    hour bin, previous-kind code."""
    days = unit_days(unit)
    cc = pl.read_parquet(SH / "roster.parquet").filter(pl.col("claude_code"))["agent"].to_list()
    t = (pl.scan_parquet(SH / "context_ledger_turns.parquet")
         .filter(pl.col("pt_date").is_in(days), pl.col("regime") == "III", ~pl.col("agent").is_in(cc))
         .select("turn_id", "agent", "pt_date", "goal_no", "holdout", "t_call", "kind", "talk", "ctx_mode",
                 "reset_consol", "reset_forced", "reset_session", "first_of_day").collect())
    hm = np.array(holdout_mask(t["pt_date"].to_list(), t["goal_no"].to_list()))
    assert not hm.any() and not t["holdout"].any(), "reserved rows in skeleton"
    cal = pl.read_parquet(SH / "calendar.parquet").select("pt_date", "win_start")
    t = t.join(cal, on="pt_date", how="left").sort("agent", "t_call", "turn_id")
    t = t.with_columns(
        hbin=((pl.col("t_call") - pl.col("win_start")).dt.total_seconds() / 3600).floor().clip(0, 6).cast(pl.Int8),
        reset=(pl.col("reset_consol") | pl.col("reset_session")).fill_null(False),
        forced=pl.col("reset_forced").fill_null(False),
        vol=(pl.col("reset_consol").fill_null(False) & ~pl.col("reset_forced").fill_null(False)),
        sess=pl.col("reset_session").fill_null(False),
        fod=pl.col("first_of_day").fill_null(False),
    )
    k = pl.col("kind").cast(pl.Utf8)
    t = t.with_columns(kcode=pl.when(k == "cu_action").then(0).when(k == "talk").then(1)
                       .when(k.is_in(["pause", "wait"])).then(2).when(k.is_in(["consolidate", "session_start", "session_stop"]))
                       .then(3).otherwise(4).cast(pl.Int8))
    t = t.with_columns(prev_k=pl.col("kcode").shift(1).over("agent").fill_null(4),
                       seg=(pl.col("reset") | (pl.col("agent") != pl.col("agent").shift(1)).fill_null(True))
                       .cast(pl.Int32).cum_sum())
    dcode = {d: i for i, d in enumerate(days)}
    t = t.with_columns(day=pl.col("pt_date").replace_strict(dcode, return_dtype=pl.Int16))
    return t.drop("win_start")


def nuisance(sk: pl.DataFrame) -> dict:
    """z columns per call (dict name -> float array)."""
    hb = sk["hbin"].to_numpy()
    pk = sk["prev_k"].to_numpy()
    z = {f"h{h}": (hb == h).astype(float) for h in range(1, 7)}
    for c, nm in ((1, "prev_talk"), (2, "prev_idle"), (3, "prev_consol"), (4, "prev_other")):
        z[nm] = (pk == c).astype(float)
    z["forced"] = sk["forced"].to_numpy().astype(float)
    z["vol"] = (sk["vol"].to_numpy() | sk["sess"].to_numpy()).astype(float)
    z["fod"] = sk["fod"].to_numpy().astype(float)
    return z


def lnq(f) -> np.ndarray:
    f = np.asarray(f, float)
    return np.log(np.clip(1.0 - np.nan_to_num(f, nan=0.0), 1.0 - F_CAP, 1.0))


def share(n_a, n_own):
    """Amended ruler A1: f = n_a / (n_own + 1/2) (0 at a segment start)."""
    return np.asarray(n_a, float) / (np.asarray(n_own, float) + 0.5)


# ============================================================================ composition on real labels
def composition(agent, seg, touches, cur, visit, d, reset, rec: int = 10):
    """Per-call self-share variants from touch sets.
    agent, seg: per-call codes (rows sorted by agent, time); touches: list (per call) of project codes the call touched
    (strict mention in the call window; empty if none); cur: the visit's project at the call (-1 if none); visit: visit
    id (-1 none). Returns dict of arrays: n_a, n_own, n_lab (own earlier calls in segment touching any project),
    n_a_pre / n_own_pre (counts carried over the reset at this call: the counterfactual f_pre for O4), f, f_lab, f_rec,
    f_pre, ntv (earlier calls of this visit that touched its project; not cut by resets)."""
    n = len(agent)
    out = {k: np.zeros(n) for k in ("n_a", "n_own", "n_lab", "n_a_pre", "n_own_pre", "ntv", "rec_a", "rec_n")}
    seg_cnt: dict = {}
    seg_own = seg_lab = 0
    prev_cnt: dict = {}
    prev_own = 0
    hist: list = []
    vis_cnt = 0
    last_vis = -2
    for i in range(n):
        new_agent = i == 0 or agent[i] != agent[i - 1]
        if new_agent or seg[i] != seg[i - 1]:
            prev_cnt, prev_own = (seg_cnt, seg_own) if not new_agent else ({}, 0)
            seg_cnt, seg_own, seg_lab, hist = {}, 0, 0, []
        if new_agent:
            last_vis = -2
        a = cur[i]
        if visit[i] != last_vis:
            vis_cnt = 0
            last_vis = visit[i]
        if a >= 0:
            out["n_a"][i] = seg_cnt.get(a, 0)
            out["n_own"][i] = seg_own
            out["n_lab"][i] = seg_lab
            if reset[i]:
                out["n_a_pre"][i] = prev_cnt.get(a, 0)
                out["n_own_pre"][i] = prev_own
            else:
                out["n_a_pre"][i] = out["n_a"][i]
                out["n_own_pre"][i] = seg_own
            h = hist[-rec:]
            out["rec_n"][i] = len(h)
            out["rec_a"][i] = sum(1 for s in h if a in s)
            out["ntv"][i] = vis_cnt
        tc = touches[i]
        for p in tc:
            seg_cnt[p] = seg_cnt.get(p, 0) + 1
        if a >= 0 and a in tc:
            vis_cnt += 1
        seg_own += 1
        seg_lab += 1 if len(tc) else 0
        hist.append(set(tc))
    out["f"] = share(out["n_a"], out["n_own"])
    out["f_lab"] = share(out["n_a"], out["n_lab"])
    out["f_pre"] = share(out["n_a_pre"], out["n_own_pre"])
    out["f_rec"] = share(out["rec_a"], out["rec_n"])
    return out


# ============================================================================ fits
def design(cols: dict, z: dict, agent: np.ndarray):
    names = list(cols) + [k for k in z if np.std(z[k]) > 0]
    C = np.column_stack([cols[k] for k in cols] + [z[k] for k in z if np.std(z[k]) > 0]) if names else np.zeros((len(agent), 0))
    return HF.design(C, names, agent)


def fit(cols: dict, z: dict, agent, y, idx=None, cluster=None):
    X, nm = design(cols, z, agent)
    if idx is not None:
        X, y = X[idx], y[idx]
        cluster = None if cluster is None else cluster[idx]
    keep = np.r_[True, X[:, 1:].std(axis=0) > 0]
    f = HF.fit_binary(X[:, keep], y)
    beta = np.zeros(X.shape[1]); beta[keep] = f["beta"]
    se = np.full(X.shape[1], np.nan); se[keep] = np.sqrt(np.clip(np.diag(f["cov"]), 0, None))
    out = {"beta": dict(zip(nm, beta)), "se": dict(zip(nm, se)), "ll": f["ll"], "conv": f["converged"], "bvec": beta}
    if cluster is not None:
        Xk = X[:, keep]
        mu = 1 / (1 + np.exp(-(Xk @ f["beta"])))
        sc = Xk * (y - mu)[:, None]
        _, cl = np.unique(cluster, return_inverse=True)
        G = np.zeros((cl.max() + 1, Xk.shape[1]))
        np.add.at(G, cl, sc)
        V = f["cov"] @ (G.T @ G) @ f["cov"]
        sr = np.full(X.shape[1], np.nan); sr[keep] = np.sqrt(np.clip(np.diag(V), 0, None))
        out["se_cl"] = dict(zip(nm, sr))
    return out


def predict(fitres: dict, cols: dict, z: dict, agent):
    X, nm = design(cols, z, agent)
    b = np.array([fitres["beta"].get(k, 0.0) for k in nm])
    return 1 / (1 + np.exp(-(X @ b)))


def cv_eps(F: np.ndarray, A: np.ndarray, z: dict, agent, y, day, k: int = 5, boot: int = 0, seed: int = 0) -> dict:
    """Day-blocked k-fold CV (interleaved day folds, agent FE refitted per fold): per-day held-out LL of B, B+A, B+F,
    B+F+A. G(A) = LL(B+A) - LL(B) (nats per 1,000 risk calls); eps(F) = 1 - [LL(B+F+A) - LL(B+F)] / G(A).
    With boot > 0, a day bootstrap of the per-day contributions gives percentile CIs."""
    models = {"B": {}, "B+A": {"A": A}, "B+F": {"F": F}, "B+F+A": {"F": F, "A": A}}
    folds = HF.interleaved_folds(day, k)
    nd = int(day.max()) + 1
    per = {}
    for m, cols in models.items():
        X, _ = design(cols, z, agent)
        p = np.zeros(nd)
        for fo in range(k):
            tr = np.flatnonzero(folds != fo); te = np.flatnonzero(folds == fo)
            if not len(te) or not len(tr):
                continue
            keep = np.r_[True, X[tr][:, 1:].std(axis=0) > 0]
            fr = HF.fit_binary(X[tr][:, keep], y[tr])
            beta = np.zeros(X.shape[1]); beta[keep] = fr["beta"]
            np.add.at(p, day[te], HF.loglik_binary(X[te], y[te], beta))
        per[m] = p
    n = len(y)
    GA = per["B+A"] - per["B"]
    left = per["B+F+A"] - per["B+F"]
    gF = per["B+F"] - per["B"]
    res = {"G_A": float(GA.sum() * 1000 / n), "G_F": float(gF.sum() * 1000 / n),
           "eps_F": float(1 - left.sum() / GA.sum()) if GA.sum() != 0 else float("nan"), "per": per}
    if boot:
        rng = np.random.default_rng(seed)
        ga, ef, gf = [], [], []
        for _ in range(boot):
            i = rng.integers(0, nd, nd)
            g = GA[i].sum()
            ga.append(g * 1000 / n); gf.append(gF[i].sum() * 1000 / n)
            ef.append(1 - left[i].sum() / g if g > 0 else np.nan)
        res["G_A_ci"] = pct(ga); res["G_F_ci"] = pct(gf); res["eps_F_ci"] = pct(ef)
    return res


def pct(a, lo=2.5, hi=97.5):
    a = np.asarray(a, float)
    a = a[np.isfinite(a)]
    if len(a) < 10:
        return [float("nan"), float("nan")]
    return [float(np.percentile(a, lo)), float(np.percentile(a, hi))]


# ============================================================================ O3: dwell statistics and forward simulation
def visit_bounds(visit: np.ndarray):
    """Row ranges [s, e) of each visit among risk rows (rows sorted by visit then d)."""
    cuts = np.flatnonzero(visit[1:] != visit[:-1]) + 1
    return np.r_[0, cuts], np.r_[cuts, len(visit)]


def dwell_stats(d: np.ndarray, y: np.ndarray, at_risk: np.ndarray, comp_d: np.ndarray) -> dict:
    """gamma (logit h(d) = a + gamma ln d, by grouped binomial fit), KM survival at KM_D, P90 of completed dwell.
    d, y: risk rows (at_risk mask selects the rows still at risk); comp_d: d at the leave call of completed visits."""
    dd = d[at_risk].astype(np.int64); yy = y[at_risk]
    mx = int(dd.max()) + 1
    N = np.bincount(dd, minlength=mx).astype(float)
    Y = np.bincount(dd, weights=yy, minlength=mx)
    ok = N > 0
    du = np.flatnonzero(ok)
    g = grouped_logit(np.log(du), Y[du], N[du])
    h = np.where(ok, Y / np.maximum(N, 1), 0.0)
    S = np.cumprod(1 - h)
    km = {}
    for k in KM_D:
        km[k] = float(S[min(k, mx - 1)]) if (k < mx and N[k] > 0) else float("nan")
    p90 = float(np.percentile(comp_d, 90)) if len(comp_d) >= 10 else float("nan")
    return {"gamma": g, "km": km, "p90": p90, "n_at_risk_100": float(N[100]) if mx > 100 else 0.0,
            "n_at_risk_300": float(N[300]) if mx > 300 else 0.0}


def grouped_logit(x, Y, N, it=50):
    """Two-parameter binomial logit on grouped counts; returns the slope."""
    X = np.column_stack([np.ones_like(x), x])
    p0 = np.clip(Y.sum() / N.sum(), 1e-6, 1 - 1e-6)
    b = np.array([np.log(p0 / (1 - p0)), 0.0])
    for _ in range(it):
        mu = 1 / (1 + np.exp(-(X @ b)))
        W = N * mu * (1 - mu)
        H = (X * W[:, None]).T @ X + 1e-9 * np.eye(2)
        g = X.T @ (Y - N * mu)
        st = np.linalg.solve(H, g)
        b = b + st
        if np.max(np.abs(st)) < 1e-9:
            break
    return float(b[1])


def first_hits(hit: np.ndarray, s: np.ndarray, e: np.ndarray) -> np.ndarray:
    """Index of the first True in each [s, e) (or e - 1 + 1 = e if none: censored at the real end)."""
    idx = np.where(hit, np.arange(len(hit)), len(hit) + 1)
    fh = np.minimum.reduceat(idx, s)
    return np.where(fh < e, fh, -1)


def simulate_dwell(p: np.ndarray, d: np.ndarray, s: np.ndarray, e: np.ndarray, rng, reps: int = 200) -> list:
    """Forward simulation from each visit's arrival with probabilities p along the real path; censor at the real end.
    Returns dwell stats per copy."""
    out = []
    n = len(p)
    pos = np.arange(n)
    vid = np.repeat(np.arange(len(s)), e - s)
    for _ in range(reps):
        hit = rng.random(n) < p
        fh = first_hits(hit, s, e)
        stop = np.where(fh >= 0, fh, e - 1)
        at = pos <= stop[vid]
        yy = np.zeros(n); yy[fh[fh >= 0]] = 1
        out.append(dwell_stats(d, yy, at, d[fh[fh >= 0]]))
    return out


def calib(obs: dict, sims: list) -> dict:
    """95% simulation bands and inside flags for gamma, KM at KM_D, P90."""
    res = {}
    keys = [("gamma", lambda r: r["gamma"]), ("p90", lambda r: r["p90"])] + \
           [(f"km{k}", (lambda r, k=k: r["km"][k])) for k in KM_D]
    for nm, fn in keys:
        v = np.array([fn(r) for r in sims], float)
        o = fn(obs)
        lo, hi = pct(v)
        res[nm] = {"obs": o, "sim_med": float(np.nanmedian(v)) if np.isfinite(v).any() else float("nan"),
                   "band": [lo, hi], "inside": (bool(lo <= o <= hi) if np.isfinite(o) and np.isfinite(lo) else None)}
    return res


# ============================================================================ O4: reset step
def mh_logor(y, treat, strata):
    """Mantel-Haenszel log odds ratio (treated vs control) over strata, with the Robins-Breslow-Greenland SE."""
    _, s = np.unique(strata, return_inverse=True)
    K = s.max() + 1
    a = np.bincount(s, weights=treat * y, minlength=K)        # treated, leave
    b = np.bincount(s, weights=treat * (1 - y), minlength=K)  # treated, stay
    c = np.bincount(s, weights=(1 - treat) * y, minlength=K)
    dd = np.bincount(s, weights=(1 - treat) * (1 - y), minlength=K)
    n = a + b + c + dd
    ok = (a + b > 0) & (c + dd > 0)
    a, b, c, dd, n = a[ok], b[ok], c[ok], dd[ok], n[ok]
    R = a * dd / n; S = b * c / n
    if R.sum() <= 0 or S.sum() <= 0:
        return float("nan"), float("nan"), int((a + b).sum())
    P = (a + dd) / n; Q = (b + c) / n
    lor = np.log(R.sum() / S.sum())
    var = (P * R).sum() / (2 * R.sum() ** 2) + ((P * S).sum() + (Q * R).sum()) / (2 * R.sum() * S.sum()) + \
          (Q * S).sum() / (2 * S.sum() ** 2)
    return float(lor), float(np.sqrt(var)), int((a + b).sum())


def deciles(x):
    q = np.nanpercentile(x, np.arange(10, 100, 10))
    return np.searchsorted(q, x, side="right")


def reset_contrast(y, d, f_now, f_pre, forced, agent, treat_mask):
    """Treated rows: treat_mask (reset calls, or placebo calls) with d >= D_RESET; controls: non-reset rows with
    d >= D_RESET that are not treated. Strata: agent x dwell decile x f decile (f_pre for treated, f for controls)."""
    base = d >= D_RESET
    treat = treat_mask & base
    ctrl = base & ~forced & ~treat_mask
    rows = treat | ctrl
    fm = np.where(treat, f_pre, f_now)
    dq = deciles(np.log(d[rows].astype(float)))
    fq = deciles(fm[rows])
    strata = agent[rows].astype(np.int64) * 1000 + dq * 10 + fq
    return mh_logor(y[rows].astype(float), treat[rows].astype(float), strata), rows


def jdump(obj, path: Path):
    def conv(o):
        if isinstance(o, (np.floating,)):
            return None if not np.isfinite(o) else float(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, np.bool_):
            return bool(o)
        if isinstance(o, np.ndarray):
            return [conv(x) for x in o.tolist()]
        if isinstance(o, float) and not np.isfinite(o):
            return None
        if isinstance(o, dict):
            return {str(k): conv(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [conv(x) for x in o]
        return o
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(conv(obj), indent=1))


# ============================================================================ unit loader (risk rows from scheme/build.py)
def load_unit(unit: str, extra: tuple = ()) -> dict:
    """Risk rows of one unit, sorted by (visit, d). Returns arrays plus z (nuisance) and visit bounds."""
    c = pl.read_parquet(OUT / "calls.parquet").filter(pl.col("unit_id") == unit).sort("visit", "d")
    hm = np.array(holdout_mask(c["pt_date"].to_list(), c["goal_no"].to_list()))
    assert not hm.any(), "reserved rows"
    days = sorted(set(c["pt_date"].to_list()))
    dcode = {d: i for i, d in enumerate(days)}
    hb = c["hbin"].to_numpy(); pk = c["prev_k"].to_numpy()
    z = {f"h{h}": (hb == h).astype(float) for h in range(1, 7)}
    for k, nm in ((1, "prev_talk"), (2, "prev_idle"), (3, "prev_consol"), (4, "prev_other")):
        z[nm] = (pk == k).astype(float)
    z["forced"] = c["forced"].to_numpy().astype(float)
    z["vol"] = (c["vol"].to_numpy() | c["sess"].to_numpy()).astype(float)
    z["fod"] = c["fod"].to_numpy().astype(float)
    vis = c["visit"].to_numpy()
    s, e = visit_bounds(vis)
    U = {"unit": unit, "n": c.height, "agent": c["agent"].to_numpy().astype(np.int64),
         "day": c["pt_date"].replace_strict(dcode, return_dtype=pl.Int64).to_numpy(), "days": days,
         "visit": vis, "vidx": np.repeat(np.arange(len(s)), e - s), "s": s, "e": e,
         "d": c["d"].to_numpy().astype(float), "y": c["y"].to_numpy().astype(float),
         "f": c["f"].to_numpy().astype(float), "f_pre": c["f_pre"].to_numpy().astype(float),
         "ntv": c["ntv"].to_numpy().astype(float), "forced": c["forced"].to_numpy(), "pseudo": c["pseudo"].to_numpy(),
         "z": z}
    for k in extra:
        U[k] = c[k].to_numpy()
    return U


# ============================================================================ O3 with parameter uncertainty (amendment A6)
def fit_draws(cols: dict, z: dict, agent, y, cluster):
    """Fit and keep what is needed to draw coefficient vectors from N(beta_hat, V_cluster)."""
    X, nm = design(cols, z, agent)
    keep = np.r_[True, X[:, 1:].std(axis=0) > 0]
    Xk = X[:, keep]
    f = HF.fit_binary(Xk, y)
    mu = 1 / (1 + np.exp(-(Xk @ f["beta"])))
    sc = Xk * (y - mu)[:, None]
    _, cl = np.unique(cluster, return_inverse=True)
    G = np.zeros((cl.max() + 1, Xk.shape[1]))
    np.add.at(G, cl, sc)
    V = f["cov"] @ (G.T @ G) @ f["cov"]
    V = (V + V.T) / 2
    w, Q = np.linalg.eigh(V)
    R = Q * np.sqrt(np.clip(w, 0, None))
    return {"X": Xk, "beta": f["beta"], "R": R, "names": [n for n, k in zip(nm, keep) if k]}


def draw_p(fd: dict, rng):
    b = fd["beta"] + fd["R"] @ rng.standard_normal(len(fd["beta"]))
    return 1 / (1 + np.exp(-(fd["X"] @ b)))


def simulate_dwell_draws(fd, d, s, e, rng, reps=200):
    """O3 forward copies (as simulate_dwell) with a fresh coefficient draw per copy."""
    out = []
    n = len(d)
    pos = np.arange(n)
    vid = np.repeat(np.arange(len(s)), e - s)
    for _ in range(reps):
        p = draw_p(fd, rng)
        hit = rng.random(n) < p
        fh = first_hits(hit, s, e)
        stop = np.where(fh >= 0, fh, e - 1)
        at = pos <= stop[vid]
        yy = np.zeros(n); yy[fh[fh >= 0]] = 1
        out.append(dwell_stats(d, yy, at, d[fh[fh >= 0]]))
    return out


def predictive_dwell(fd, d, rng, reps=200):
    """O3-pp: posterior-predictive leave outcomes on the observed risk rows (one Bernoulli per row, fresh coefficient
    draw per copy); the hazard by d, gamma and the KM product are computed as for the observed rows. No P90."""
    out = []
    n = len(d)
    allr = np.ones(n, bool)
    for _ in range(reps):
        p = draw_p(fd, rng)
        yy = (rng.random(n) < p).astype(float)
        r = dwell_stats(d, yy, allr, np.array([]))
        out.append(r)
    return out
