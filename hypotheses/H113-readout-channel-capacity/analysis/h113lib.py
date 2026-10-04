"""H113 estimators: capacity exponent b (profile LS with in-flight term), binned slopes, cross-fitted Gaussian
information per call, redundancy exponent, matched-age placebo contrast, recency, discrete check (semantic_kappa)."""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))

B_GRID = np.round(np.arange(-0.5, 1.5001, 0.01), 2)
K_BINS = [(1, 1), (2, 2), (3, 4), (5, 8), (9, 16), (17, 10_000)]
AGE_BINS = [(0, 30), (30, 60), (60, 120)]
D = 32
LN2 = math.log(2)
I_ID = 0.02  # bits: H87's identified rule


def cluster_ids(c: pl.DataFrame) -> np.ndarray:
    return np.unique((c["agent"].cast(pl.String) + "|" + c["pt_date"]).to_numpy(), return_inverse=True)[1]


def _grid_sums(c: pl.DataFrame, k_col: str = "k", ys="ys", ss="ss", with_F: bool = True):
    """Per-cluster sufficient statistics for every b in B_GRID: arrays (n_clusters, n_grid)."""
    k = c[k_col].to_numpy().astype(float)
    cl = cluster_ids(c); ncl = cl.max() + 1
    W = k[:, None] ** (-B_GRID[None, :])          # (n, g)
    def agg(v):
        out = np.zeros((ncl,) + v.shape[1:]); np.add.at(out, cl, v); return out
    A11 = agg(W ** 2 * c[ss].to_numpy()[:, None]); C1 = agg(W * c[ys].to_numpy()[:, None])
    if with_F:
        A12 = agg(W * c["ssF"].to_numpy()[:, None]); A22 = agg(c["sFsF"].to_numpy()[:, None] * np.ones((1, len(B_GRID))))
        C2 = agg(c["ysF"].to_numpy()[:, None] * np.ones((1, len(B_GRID))))
    else:
        A12 = A22 = C2 = None
    Syy = agg(c["yy"].to_numpy()[:, None] * np.ones((1, len(B_GRID))))
    return dict(A11=A11, A12=A12, A22=A22, C1=C1, C2=C2, Syy=Syy, n_cl=ncl)


def _solve(sm: dict, w: np.ndarray | None = None):
    def S(x):
        return (x if w is None else x * w[:, None]).sum(0)
    A11, C1, Syy = S(sm["A11"]), S(sm["C1"]), S(sm["Syy"])
    if sm["A12"] is not None:
        A12, A22, C2 = S(sm["A12"]), S(sm["A22"]), S(sm["C2"])
        det = A11 * A22 - A12 ** 2
        ok = det > 1e-12
        g1 = np.where(ok, (A22 * C1 - A12 * C2) / np.where(ok, det, 1), C1 / np.maximum(A11, 1e-12))
        gF = np.where(ok, (A11 * C2 - A12 * C1) / np.where(ok, det, 1), 0.0)
        sse = Syy - g1 * C1 - gF * C2
    else:
        g1 = C1 / np.maximum(A11, 1e-12); gF = np.zeros_like(g1)
        sse = Syy - g1 * C1
    j = int(np.argmin(sse))
    return B_GRID[j], g1[j], gF[j], sse


def fit_b(c: pl.DataFrame, k_col: str = "k", ys="ys", ss="ss", with_F: bool = True, B: int = 300, seed: int = 0) -> dict:
    c = c.filter(pl.col(k_col) >= 1)
    if len(c) < 30:
        return {"n": len(c)}
    sm = _grid_sums(c, k_col, ys, ss, with_F)
    b, g1, gF, sse = _solve(sm)
    rng = np.random.default_rng(seed)
    bs = []
    for _ in range(B):
        w = np.bincount(rng.integers(0, sm["n_cl"], sm["n_cl"]), minlength=sm["n_cl"]).astype(float)
        bb, gg, ff, _ = _solve(sm, w)
        bs.append((bb, gg, ff))
    bs = np.array(bs)
    lo, hi = np.percentile(bs[:, 0], [2.5, 97.5])
    edge = float(np.mean((bs[:, 0] <= B_GRID[0]) | (bs[:, 0] >= B_GRID[-1])))
    return {"n": int(len(c)), "n_clusters": int(sm["n_cl"]), "b": float(b), "b_lo": float(lo), "b_hi": float(hi),
            "a_U": float(1 - b), "a_U_lo": float(1 - hi), "a_U_hi": float(1 - lo), "gamma1": float(g1),
            "gamma1_lo": float(np.percentile(bs[:, 1], 2.5)), "gamma1_hi": float(np.percentile(bs[:, 1], 97.5)),
            "gammaF": float(gF), "gammaF_lo": float(np.percentile(bs[:, 2], 2.5)), "gammaF_hi": float(np.percentile(bs[:, 2], 97.5)),
            "boot_edge_share": edge, "k_max": int(c[k_col].max()), "k_mean": float(c[k_col].mean())}


def placebo_corrected(c: pl.DataFrame, it: pl.DataFrame, age_max: float = 120.0) -> tuple[pl.DataFrame, dict]:
    """Subtract the in-flight (unreadable) per-item pull kappa_F from every read item: ys_pc = ys - k * kappa_F.
    kappa_F = the mean <y_perp, x_perp> over in-flight items (age <= age_max). A time-local field adds the same
    per-item pull to read and in-flight items; reading adds only to read items."""
    f = it.filter(~pl.col("read") & (pl.col("age_s") <= age_max)) if len(it) else it
    kF = float(f["xy"].mean()) if len(f) else 0.0
    return c.with_columns((pl.col("ys") - pl.col("k") * kF).alias("ys_pc")), {"kappa_F": kF, "n_inflight_items": len(f)}


def kbin_of(k: np.ndarray) -> np.ndarray:
    out = np.full(len(k), -1)
    for i, (lo, hi) in enumerate(K_BINS):
        out[(k >= lo) & (k <= hi)] = i
    return out


def binned(c: pl.DataFrame, k_col="k", ys="ys", ss="ss", B: int = 300, seed: int = 0) -> list[dict]:
    c = c.filter(pl.col(k_col) >= 1)
    kb = kbin_of(c[k_col].to_numpy()); cl = cluster_ids(c); ncl = cl.max() + 1
    rng = np.random.default_rng(seed)
    Wb = [np.bincount(rng.integers(0, ncl, ncl), minlength=ncl).astype(float)[cl] for _ in range(B)]
    out = []
    for i, (lo, hi) in enumerate(K_BINS):
        m = kb == i
        if m.sum() < 20:
            continue
        y = c[ys].to_numpy()[m]; s = c[ss].to_numpy()[m]; kk = c[k_col].to_numpy()[m]
        g = y.sum() / s.sum()
        gb = np.array([(y * w[m]).sum() / max((s * w[m]).sum(), 1e-12) for w in Wb])
        out.append({"bin": f"{lo}-{hi}" if hi < 10_000 else f">={lo}", "k_mean": float(kk.mean()), "n": int(m.sum()),
                    "gamma": float(g), "lo": float(np.percentile(gb, 2.5)), "hi": float(np.percentile(gb, 97.5)),
                    "U": float(g * kk.mean()), "ss_mean": float(s.mean())})
    return out


def info_curve(c: pl.DataFrame, k_col="k", ys="ys", ss="ss", B: int = 200, seed: int = 0) -> list[dict]:
    """Day-cross-fitted Gaussian information per call (bits) by k bin: gamma per bin fitted on the other days."""
    c = c.filter(pl.col(k_col) >= 1)
    kb = kbin_of(c[k_col].to_numpy())
    days = c["pt_date"].to_numpy(); ud = np.unique(days)
    y = c[ys].to_numpy(); s = c[ss].to_numpy(); yy = c["yy"].to_numpy()
    sse = np.zeros(len(c))
    for d in ud:
        te = days == d
        for i in range(len(K_BINS)):
            tr = (~te) & (kb == i); tt = te & (kb == i)
            if tt.sum() == 0:
                continue
            g = y[tr].sum() / s[tr].sum() if tr.sum() >= 10 and s[tr].sum() > 0 else 0.0
            sse[tt] = yy[tt] - 2 * g * y[tt] + g * g * s[tt]
    cl = cluster_ids(c); ncl = cl.max() + 1
    rng = np.random.default_rng(seed)
    Wb = [np.bincount(rng.integers(0, ncl, ncl), minlength=ncl).astype(float)[cl] for _ in range(B)]
    out = []
    def I_of(r2):
        return -(D / 2) * math.log2(1 - r2) if r2 > 0 else 0.0
    for i, (lo, hi) in enumerate(K_BINS):
        m = kb == i
        if m.sum() < 20:
            continue
        r2 = 1 - sse[m].sum() / yy[m].sum()
        bs = []
        for w in Wb:
            ww = w[m]
            bs.append(I_of(1 - (sse[m] * ww).sum() / max((yy[m] * ww).sum(), 1e-12)))
        lo_i, hi_i = np.percentile(bs, [2.5, 97.5])
        out.append({"bin": f"{lo}-{hi}" if hi < 10_000 else f">={lo}", "k_mean": float(c[k_col].to_numpy()[m].mean()),
                    "n": int(m.sum()), "R2": float(r2), "I_bits": I_of(r2), "I_lo": float(lo_i), "I_hi": float(hi_i),
                    "identified": bool(lo_i > I_ID)})
    return out


def slope_loglog(xs, ys, ws=None) -> dict:
    xs = np.log(np.asarray(xs, float)); ys = np.asarray(ys, float)
    ok = np.isfinite(ys) & (ys > 0)
    if ok.sum() < 2:
        return {"slope": float("nan"), "n": int(ok.sum())}
    X = np.vstack([np.ones(ok.sum()), xs[ok]]).T; Y = np.log(ys[ok])
    w = np.ones(ok.sum()) if ws is None else np.asarray(ws, float)[ok]
    beta = np.linalg.lstsq(X * np.sqrt(w)[:, None], Y * np.sqrt(w), rcond=None)[0]
    return {"slope": float(beta[1]), "n": int(ok.sum())}


def redundancy(c: pl.DataFrame, k_col="k", ss="ss") -> dict:
    """r = d ln E|s|^2 / d ln k - 1 over k bins (WLS by counts)."""
    c = c.filter(pl.col(k_col) >= 1)
    kb = kbin_of(c[k_col].to_numpy())
    xs, ys, ws = [], [], []
    for i in range(len(K_BINS)):
        m = kb == i
        if m.sum() >= 20:
            xs.append(c[k_col].to_numpy()[m].mean()); ys.append(c[ss].to_numpy()[m].mean()); ws.append(m.sum())
    r = slope_loglog(xs, ys, ws)
    return {"r": r["slope"] - 1 if np.isfinite(r["slope"]) else float("nan"), "n_bins": r["n"]}


def placebo_contrast(c: pl.DataFrame, it: pl.DataFrame, B: int = 300, seed: int = 0) -> dict:
    """Matched-age per-item slopes: read items (age <= 120 s) vs in-flight items, age bins weighted by in-flight counts."""
    if len(it) == 0:
        return {}
    cl_of = cluster_ids(c)
    it = it.with_columns(pl.Series("cl", cl_of[it["call_row"].to_numpy()]))
    rows = {}
    cl = it["cl"].to_numpy(); ncl = int(cl.max()) + 1
    rng = np.random.default_rng(seed)
    Wb = [np.bincount(rng.integers(0, ncl, ncl), minlength=ncl).astype(float)[cl] for _ in range(B)]
    age = it["age_s"].to_numpy(); rd = it["read"].to_numpy(); xy = it["xy"].to_numpy(); xx = it["xx"].to_numpy()
    def contrast(w):
        num = den = 0.0; gr_all = gf_all = 0.0
        for lo, hi in AGE_BINS:
            mb = (age >= lo) & (age < hi)
            mr = mb & rd; mf = mb & ~rd
            if mr.sum() < 5 or mf.sum() < 5:
                continue
            gr = (xy[mr] * w[mr]).sum() / max((xx[mr] * w[mr]).sum(), 1e-12)
            gf = (xy[mf] * w[mf]).sum() / max((xx[mf] * w[mf]).sum(), 1e-12)
            wt = mf.sum(); num += wt * (gr - gf); den += wt; gr_all += wt * gr; gf_all += wt * gf
        return (num / den, gr_all / den, gf_all / den) if den else (float("nan"),) * 3
    est = contrast(np.ones(len(it)))
    bs = np.array([contrast(w) for w in Wb])
    ok = np.isfinite(bs[:, 0])
    if ok.sum() < 20:
        return {"contrast": est[0], "gamma_read": est[1], "gamma_inflight": est[2], "n_read": int((rd & (age < 120)).sum()),
                "n_inflight": int((~rd).sum())}
    return {"contrast": float(est[0]), "lo": float(np.percentile(bs[ok, 0], 2.5)), "hi": float(np.percentile(bs[ok, 0], 97.5)),
            "gamma_read": float(est[1]), "gamma_inflight": float(est[2]),
            "n_read": int((rd & (age < 120)).sum()), "n_inflight": int((~rd).sum())}


def recency(c: pl.DataFrame, it: pl.DataFrame, B: int = 300, seed: int = 0) -> dict:
    """Per-item slope of the newest read item (rank 1) vs older read items (rank >= 2)."""
    r = it.filter(pl.col("read"))
    if len(r) == 0:
        return {}
    cl_of = cluster_ids(c)
    cl = cl_of[r["call_row"].to_numpy()]; ncl = int(cl_of.max()) + 1
    nw = (r["rank"] == 1).to_numpy(); xy = r["xy"].to_numpy(); xx = r["xx"].to_numpy()
    def est(w):
        a = (xy[nw] * w[nw]).sum() / max((xx[nw] * w[nw]).sum(), 1e-12)
        b = (xy[~nw] * w[~nw]).sum() / max((xx[~nw] * w[~nw]).sum(), 1e-12)
        return a, b, a - b
    e = est(np.ones(len(r)))
    rng = np.random.default_rng(seed)
    bs = np.array([est(np.bincount(rng.integers(0, ncl, ncl), minlength=ncl).astype(float)[cl]) for _ in range(B)])
    return {"gamma_newest": float(e[0]), "gamma_older": float(e[1]), "diff": float(e[2]),
            "lo": float(np.percentile(bs[:, 2], 2.5)), "hi": float(np.percentile(bs[:, 2], 97.5)),
            "n_newest": int(nw.sum()), "n_older": int((~nw).sum())}


def discrete_check(c: pl.DataFrame, it: pl.DataFrame, B: int = 30, n_perm: int = 50, seed: int = 0) -> list[dict]:
    """semantic_kappa.mi_corrected per k bin on (cluster of reader statement `ylab`, cluster of read item `xlab`; K = 8
    k-means fitted in the scheme), strata = agent; bootstrap over agent-days for the interval (under-covers; Known issues)."""
    from semantic_kappa import mi_corrected
    if "ylab" not in c.columns or "xlab" not in it.columns:
        return []
    rd = it["read"].to_numpy()
    if rd.sum() < 50:
        return []
    ly = c["ylab"].to_numpy(); lx = it["xlab"].to_numpy()
    cr = it["call_row"].to_numpy()
    k = c["k"].to_numpy()[cr]; ag = c["agent"].to_numpy()[cr]
    clu = cluster_ids(c)[cr]
    kb = kbin_of(k)
    rng = np.random.default_rng(seed)
    out = []
    for i, (lo, hi) in enumerate(K_BINS):
        m = rd & (kb == i)
        if m.sum() < 50:
            continue
        r = mi_corrected(ly[cr[m]], lx[m], ag[m], n_perm=n_perm, rng=np.random.default_rng(seed + i))
        mi_ = np.flatnonzero(m); ucl = np.unique(clu[m]); idx = {u: mi_[clu[m] == u] for u in ucl}
        bs = []
        for _ in range(B):
            mm = np.concatenate([idx[u] for u in rng.choice(ucl, len(ucl))])
            bs.append(mi_corrected(ly[cr[mm]], lx[mm], ag[mm], n_perm=10, rng=np.random.default_rng(int(rng.integers(1 << 30))))["I"])
        lo_i, hi_i = np.percentile(bs, [2.5, 97.5])
        out.append({"bin": f"{lo}-{hi}" if hi < 10_000 else f">={lo}", "n_items": int(m.sum()), "I_bits": r["I"],
                    "I_lo": float(lo_i), "I_hi": float(hi_i), "p_perm": r["p_perm"], "identified": bool(lo_i > I_ID)})
    return out


def dl_pool(est, lo, hi) -> dict:
    est = np.asarray(est, float); se = (np.asarray(hi, float) - np.asarray(lo, float)) / (2 * 1.96)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[ok], se[ok]
    if len(est) == 0:
        return {"est": float("nan"), "lo": float("nan"), "hi": float("nan"), "k": 0}
    w = 1 / se ** 2; mu = (w * est).sum() / w.sum(); Q = (w * (est - mu) ** 2).sum()
    C = w.sum() - (w ** 2).sum() / w.sum(); tau2 = max(0.0, (Q - (len(est) - 1)) / C) if C > 0 else 0.0
    ws = 1 / (se ** 2 + tau2); m = (ws * est).sum() / ws.sum(); s = math.sqrt(1 / ws.sum())
    return {"est": float(m), "lo": float(m - 1.96 * s), "hi": float(m + 1.96 * s), "k": int(len(est)), "tau2": float(tau2)}
