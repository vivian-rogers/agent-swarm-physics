"""H104 estimators: burst sizes after field steps, the per-agent-day circular time-shuffle null (keeps step times),
step response X, tail statistics (V, avalanche Fano F_A, deconvolution MLE tau), quiet-window dispersion D and burst
ratio BR, dose slope, pre-step placebo, read-out split, kickoff ratio.

Vectorized core: a "window x agent-day" incidence (pairs) is built once; each null draw rotates all switch times and
counts switches per pair with one bincount.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import polars as pl
from scipy.stats import norm, spearmanr

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data/processed/H104-barkhausen-avalanches"
W_DEFAULT = 3600.0


# ------------------------------------------------------------------------------------------------ loading
def load_period(g: int, root: Path = DATA) -> dict:
    d = root / f"G{g:02d}"
    if not d.exists():
        return {}
    P = {"g": g}
    for k in ("days", "spans", "switches_work", "switches_attn", "daystart_work", "daystart_attn", "kickoffs", "nudges"):
        f = d / f"{k}.parquet"
        P[k] = pl.read_parquet(f) if f.exists() else None
    for k in ("steps", "step_receipts"):
        f = d / f"{k}.parquet"
        P[k] = pl.read_parquet(f) if f.exists() else None
    return P


def agent_days(P: dict, trim: str = "span") -> pl.DataFrame:
    """At-risk spans per agent-day. trim = 'span' (agent's own span) or 'allpresent' (intersect with the DQ8 window)."""
    s = P["spans"].filter(pl.col("risk_hi") > pl.col("risk_lo"))
    if trim == "allpresent":
        s = s.join(P["days"].select("pt_date", "ap_lo", "ap_hi"), on="pt_date", how="left").with_columns(
            pl.max_horizontal("risk_lo", "ap_lo").alias("risk_lo"), pl.min_horizontal("risk_hi", "ap_hi").alias("risk_hi"))
        s = s.filter(pl.col("risk_hi") > pl.col("risk_lo") + 600)
    elif trim == "none":
        s = s.with_columns(pl.col("first_call").alias("risk_lo"), pl.col("last_call").alias("risk_hi"))
    return s.select("pt_date", "agent", "risk_lo", "risk_hi").sort("pt_date", "agent").with_row_index("ad")


def switches_in(P: dict, channel: str, ad: pl.DataFrame) -> pl.DataFrame:
    sw = P[f"switches_{channel}"]
    s = sw.join(ad, on=["pt_date", "agent"], how="inner").filter(
        (pl.col("t") >= pl.col("risk_lo")) & (pl.col("t") <= pl.col("risk_hi")))
    return s.select("ad", "agent", "pt_date", "t").sort("ad", "t")


# ------------------------------------------------------------------------------------------------ windows
class Panel:
    """Windows (t0, t0 + W] with their at-risk agent-days, and the switch times, for fast null counting."""

    def __init__(self, ad: pl.DataFrame, sw: pl.DataFrame, t0: np.ndarray, W: float, pt_dates: np.ndarray):
        self.W = W
        self.t0 = np.asarray(t0, float)
        lo = ad["risk_lo"].to_numpy()
        hi = ad["risk_hi"].to_numpy()
        dd = ad["pt_date"].to_numpy()
        ag = ad["agent"].to_numpy()
        self.lo, self.hi, self.L = lo, hi, hi - lo
        self.ad_agent = ag
        win_of, ad_of = [], []
        for k, (t, d) in enumerate(zip(self.t0, pt_dates)):
            ok = np.flatnonzero((dd == d) & (lo <= t) & (hi >= t + W))
            win_of.append(np.full(len(ok), k))
            ad_of.append(ok)
        self.pair_win = np.concatenate(win_of) if win_of else np.zeros(0, int)
        self.pair_ad = np.concatenate(ad_of) if ad_of else np.zeros(0, int)
        self.n_at_risk = np.bincount(self.pair_win, minlength=len(self.t0))
        # switches
        self.sw_ad = sw["ad"].to_numpy()
        self.sw_t = sw["t"].to_numpy().astype(float)
        # expand pairs x switches of the pair's agent-day
        order = np.argsort(self.sw_ad, kind="stable")
        self.sw_ad, self.sw_t = self.sw_ad[order], self.sw_t[order]
        starts = np.searchsorted(self.sw_ad, np.arange(len(lo)))
        ends = np.searchsorted(self.sw_ad, np.arange(len(lo)), side="right")
        cnt = ends[self.pair_ad] - starts[self.pair_ad]
        self.e_pair = np.repeat(np.arange(len(self.pair_ad)), cnt)
        self.e_sw = np.concatenate([np.arange(starts[a], ends[a]) for a in self.pair_ad]) if len(self.pair_ad) else np.zeros(0, int)
        self.e_sw = self.e_sw.astype(int)

    def counts(self, t_sw: np.ndarray):
        """Per window: S (distinct at-risk agents with >= 1 switch), C (switches)."""
        x = t_sw[self.e_sw]
        tw = self.t0[self.pair_win[self.e_pair]]
        inw = (x > tw) & (x <= tw + self.W)
        cp = np.bincount(self.e_pair, weights=inw, minlength=len(self.pair_ad))
        S = np.bincount(self.pair_win, weights=(cp > 0), minlength=len(self.t0))
        C = np.bincount(self.pair_win, weights=cp, minlength=len(self.t0))
        return S, C

    def rotate(self, rng) -> np.ndarray:
        off = rng.random(len(self.lo)) * self.L
        a = self.sw_ad
        return self.lo[a] + np.mod(self.sw_t - self.lo[a] + off[a], self.L[a])

    def uniform(self, rng) -> np.ndarray:
        a = self.sw_ad
        return self.lo[a] + rng.random(len(a)) * self.L[a]

    def null(self, n_draw: int = 999, seed: int = 0, kind: str = "rotate"):
        rng = np.random.default_rng(seed)
        Sn = np.zeros((n_draw, len(self.t0)))
        Cn = np.zeros((n_draw, len(self.t0)))
        for b in range(n_draw):
            t = self.rotate(rng) if kind == "rotate" else self.uniform(rng)
            Sn[b], Cn[b] = self.counts(t)
        return Sn, Cn


def eligible_steps(P: dict, ad: pl.DataFrame, W: float, isolated: bool = True, min_risk: int = 3) -> pl.DataFrame:
    st = P.get("steps")
    if st is None or st.height == 0:
        return pl.DataFrame()
    st = st.sort("t").with_columns(pl.col("t").shift(1).alias("t_prev"))
    if isolated:
        st = st.filter(pl.col("t_prev").is_null() | ((pl.col("t") - pl.col("t_prev")) >= W))
    lo, hi, dd = ad["risk_lo"].to_numpy(), ad["risk_hi"].to_numpy(), ad["pt_date"].to_numpy()
    n = [int(((dd == d) & (lo <= t) & (hi >= t + W)).sum()) for t, d in zip(st["t"].to_numpy(), st["pt_date"].to_numpy())]
    return st.with_columns(pl.Series("n_risk", n)).filter(pl.col("n_risk") >= min_risk)


def quiet_windows(P: dict, ad: pl.DataFrame, W: float, min_risk: int = 3) -> tuple[np.ndarray, np.ndarray]:
    """Disjoint W-windows on each day's at-risk range with no step session in (t - W, t + W]."""
    st = P.get("steps")
    steps = st["t"].to_numpy() if st is not None and st.height else np.zeros(0)
    t0s, dds = [], []
    for d, g in ad.group_by("pt_date"):
        lo, hi = g["risk_lo"].to_numpy(), g["risk_hi"].to_numpy()
        t = lo.min()
        while t + W <= hi.max():
            if ((lo <= t) & (hi >= t + W)).sum() >= min_risk and not np.any((steps > t - W) & (steps <= t + W)):
                t0s.append(t)
                dds.append(d[0])
            t += W
    return np.asarray(t0s), np.asarray(dds)


# ------------------------------------------------------------------------------------------------ statistics
def tail_stats(S: np.ndarray, Sn: np.ndarray, idx: np.ndarray | None = None) -> dict:
    if idx is not None:
        S, Sn = S[idx], Sn[:, idx]
    mo, vo = S.mean(), S.var(ddof=1) if len(S) > 1 else np.nan
    mn = Sn.mean()
    vn = Sn.var(axis=1, ddof=1).mean() if Sn.shape[1] > 1 else np.nan
    dm = mo - mn
    return {"X": mo / mn if mn > 0 else np.nan, "V": vo / vn if vn > 0 else np.nan,
            "F_A": (vo - vn) / dm if dm > 0 else np.nan, "excess": dm, "mean_obs": mo, "mean_null": mn}


def step_response(S, Sn, B: int = 2000, seed: int = 0) -> dict:
    """X with its one-sided null p; V with null p; F_A with a step-bootstrap CI."""
    t = tail_stats(S, Sn)
    p_X = float((1 + (Sn.mean(1) >= S.mean()).sum()) / (1 + Sn.shape[0]))
    # V null: each draw's variance vs the mean null variance
    vn_draw = Sn.var(axis=1, ddof=1)
    p_V = float((1 + (vn_draw >= S.var(ddof=1)).sum()) / (1 + len(vn_draw)))
    rng = np.random.default_rng(seed)
    fa, xx, vv = [], [], []
    for _ in range(B):
        i = rng.integers(0, len(S), len(S))
        r = tail_stats(S, Sn, i)
        fa.append(r["F_A"])
        xx.append(r["X"])
        vv.append(r["V"])
    fa, xx, vv = map(np.asarray, (fa, xx, vv))
    q = lambda a: (float(np.nanpercentile(a, 2.5)), float(np.nanpercentile(a, 97.5)))  # noqa: E731
    return {**t, "p_X": p_X, "p_V": p_V, "X_ci": q(xx), "V_ci": q(vv), "F_A_ci": q(fa),
            "F_A_defined": float(np.isfinite(fa).mean()), "n": len(S)}


def null_pmf(Sn_k: np.ndarray, nmax: int) -> np.ndarray:
    h = np.bincount(np.clip(Sn_k.astype(int), 0, nmax), minlength=nmax + 1).astype(float) + 0.5
    return h / h.sum()


def tau_mle(S: np.ndarray, Sn: np.ndarray, nrisk: np.ndarray, taus=None, pis=None) -> dict:
    """Deconvolution MLE: S_k = min(A_k + B_k, n_k); B_k ~ step k's null pmf; A_k = 0 w.p. pi, else truncated power law
    on 1..n_k with exponent tau. Profile likelihood over pi; 95% CI where 2 dlogL <= 3.84."""
    taus = np.arange(0.5, 4.01, 0.05) if taus is None else taus
    pis = np.linspace(0.0, 0.99, 34) if pis is None else pis
    pm = [null_pmf(Sn[:, k], int(nrisk[k])) for k in range(len(S))]
    ll = np.full((len(taus), len(pis)), -np.inf)
    for a, tau in enumerate(taus):
        lik_av = []
        for k in range(len(S)):
            nk = int(nrisk[k])
            s = int(min(S[k], nk))
            sizes = np.arange(1, nk + 1)
            pl_ = sizes ** (-tau)
            pl_ /= pl_.sum()
            # P(S = s | A = a) = pmf_B(s - a) for s < nk; mass at the cap absorbs overflow
            pb = pm[k]
            if s < nk:
                conv = sum(pl_[aa - 1] * pb[s - aa] for aa in range(1, s + 1))
            else:
                conv = sum(pl_[aa - 1] * pb[max(0, s - aa):].sum() for aa in range(1, nk + 1))
            lik_av.append((pb[s] if s < nk else pb[s:].sum(), conv))
        lik_av = np.asarray(lik_av)
        for b, pi in enumerate(pis):
            ll[a, b] = np.log(pi * lik_av[:, 0] + (1 - pi) * lik_av[:, 1] + 1e-300).sum()
    prof = ll.max(1)
    ai = int(np.argmax(prof))
    bi = int(np.argmax(ll[ai]))
    ok = 2 * (prof.max() - prof) <= 3.84
    ll0 = np.log(np.asarray([null_pmf(Sn[:, k], int(nrisk[k]))[int(min(S[k], nrisk[k]))] for k in range(len(S))])).sum()
    return {"tau": float(taus[ai]), "tau_lo": float(taus[ok].min()), "tau_hi": float(taus[ok].max()),
            "pi": float(pis[bi]), "llr_vs_null": float(prof.max() - ll0), "at_edge": bool(ai in (0, len(taus) - 1))}


def burst_ratio(S_post, Sn_post, S_q, Sn_q, B: int = 2000, seed: int = 0) -> dict:
    q95p = np.percentile(Sn_post, 95, axis=0)
    q95q = np.percentile(Sn_q, 95, axis=0)
    ep = (S_post > q95p).astype(float)
    eq = (S_q > q95q).astype(float)
    pr = lambda e: (e.sum() + 0.5) / (len(e) + 1)  # noqa: E731
    br = pr(ep) / pr(eq)
    rng = np.random.default_rng(seed)
    bs = [pr(ep[rng.integers(0, len(ep), len(ep))]) / pr(eq[rng.integers(0, len(eq), len(eq))]) for _ in range(B)]
    return {"BR": float(br), "BR_ci": (float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))),
            "exceed_post": float(ep.mean()), "exceed_quiet": float(eq.mean()), "n_post": len(ep), "n_quiet": len(eq)}


def dispersion(S, Sn) -> dict:
    vn = Sn.var(axis=1, ddof=1)
    vo = S.var(ddof=1)
    return {"D": float(vo / vn.mean()), "D_band": (float(np.percentile(vn / vn.mean(), 5)), float(np.percentile(vn / vn.mean(), 95))),
            "p_D": float((1 + (vn >= vo).sum()) / (1 + len(vn))), "n": len(S)}


def dose(m, S, Sn) -> dict:
    E = S - Sn.mean(0)
    if len(np.unique(m)) < 2 or len(S) < 4:
        return {"rho": np.nan, "p": np.nan, "n": len(S)}
    r, p = spearmanr(m, E)
    return {"rho": float(r), "p": float(p), "n": len(S)}


def re_pool(est, se) -> dict:
    est, se = np.asarray(est, float), np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[ok], se[ok]
    k = len(est)
    if k == 0:
        return {"est": np.nan, "se": np.nan, "lo": np.nan, "hi": np.nan, "k": 0, "p": np.nan, "I2": np.nan}
    w = 1 / se ** 2
    fe = (w * est).sum() / w.sum()
    Q = (w * (est - fe) ** 2).sum()
    tau2 = max(0.0, (Q - (k - 1)) / (w.sum() - (w ** 2).sum() / w.sum())) if k > 1 else 0.0
    wr = 1 / (se ** 2 + tau2)
    m = (wr * est).sum() / wr.sum()
    s = np.sqrt(1 / wr.sum())
    return {"est": float(m), "se": float(s), "lo": float(m - 1.96 * s), "hi": float(m + 1.96 * s), "k": k,
            "p": float(2 * norm.sf(abs(m / s))), "I2": float(max(0.0, (Q - (k - 1)) / Q)) if Q > 0 else 0.0}


def log_ci_se(ci) -> float:
    lo, hi = ci
    if not (np.isfinite(lo) and np.isfinite(hi)) or lo <= 0 or hi <= 0:
        return np.nan
    return (np.log(hi) - np.log(lo)) / (2 * 1.96)
