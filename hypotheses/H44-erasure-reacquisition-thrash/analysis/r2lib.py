"""H44 round-2 estimators (R2 sawtooth and cap, R3 re-open share, R4 loop lever, R1 checked Theta_c).

Every function takes frames with the round-1 / round-2 scheme columns, so the synthetic validation runs the same code.
Round-1 code (h44lib) is imported read-only; nothing here changes a round-1 number.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import h44lib as L  # noqa: E402
from h44lib import C  # noqa: E402

KMAX = 40
L1_GRID = np.exp(np.linspace(np.log(0.3), np.log(3.0), 12))
L2_GRID = np.exp(np.linspace(np.log(2.0), np.log(20.0), 14))
READ_IDX = [C.CAT[c] for c in ("local_read", "notes_read", "remote_read")]


# ================================================================================================= R2: curves and fits
def sawtooth_calls(calls: pl.DataFrame, open_kinds=("forced",), close_kinds=("forced",), full: bool = True) -> pl.DataFrame:
    """Calls of segments opened by `open_kinds` and closed by `close_kinds` (complete sawtooths: forced -> forced,
    40 calls). k = pos."""
    c = calls.filter(pl.col("seg_kind").is_in(list(open_kinds)) & pl.col("seg_end_kind").is_in(list(close_kinds)))
    if full:
        c = c.filter(pl.col("seg_len") == KMAX)
    c = c.filter(pl.col("pos") <= KMAX)
    return c.with_columns(pl.col("pos").alias("k"), (pl.col("agent").cast(pl.Utf8) + "_" + pl.col("pt_date")).alias("cl"))


def curve_sums(c: pl.DataFrame, ycol: str, kmax: int = KMAX, cl_codes=None):
    """Per-cluster sums: num[cl, k-1], den[cl, k-1] for y = ycol (bool or count)."""
    if cl_codes is None:
        cl_codes = np.unique(c["cl"].to_numpy())
    idx = {v: i for i, v in enumerate(cl_codes)}
    ci = np.array([idx[v] for v in c["cl"].to_numpy()])
    k = c["k"].to_numpy().astype(int) - 1
    y = c[ycol].to_numpy().astype(float)
    num = np.zeros((len(cl_codes), kmax)); den = np.zeros((len(cl_codes), kmax))
    np.add.at(num, (ci, k), y); np.add.at(den, (ci, k), 1.0)
    return num, den, cl_codes


def _design(k, l1, l2, model):
    x = k - 1.0
    cols = [np.ones_like(x)]
    if model in ("M2", "M1", "M2g"):
        cols.append(x)
    if model == "M2g":
        cols.append(x ** 2)
    cols.append(np.exp(-x / l1))
    if model in ("M2", "M0", "M2g"):
        cols.append(np.exp(-x / l2))
    return np.c_[tuple(cols)]


NPAR = {"M2": 6, "M1": 4, "M0": 5, "M2g": 7}


def fit_curve(y: np.ndarray, n: np.ndarray, model: str = "M2", binary: bool = True, l2max: float | None = None) -> dict:
    """Weighted least squares on per-k rates y (weights n), grid over (l1, l2). Log-likelihood binomial (binary) or
    Gaussian with pooled variance (counts). Returns params and AIC."""
    k = np.arange(1, len(y) + 1, dtype=float)
    ok = n > 0
    best = None
    l2s = L2_GRID if model in ("M2", "M0", "M2g") else [None]
    for l1 in L1_GRID:
        for l2 in l2s:
            if l2 is not None and (l2 < 1.5 * l1 or (l2max is not None and l2 > l2max)):
                continue
            X = _design(k, l1, l2 if l2 is not None else 1.0, model)
            w = np.sqrt(n[ok])
            coef, *_ = np.linalg.lstsq(X[ok] * w[:, None], y[ok] * w, rcond=None)
            yh = X @ coef
            sse = float((n[ok] * (yh[ok] - y[ok]) ** 2).sum())
            if best is None or sse < best[0]:
                best = (sse, l1, l2, coef, yh)
    sse, l1, l2, coef, yh = best
    if binary:
        p = np.clip(yh, 1e-6, 1 - 1e-6)
        ll = float((n[ok] * (y[ok] * np.log(p[ok]) + (1 - y[ok]) * np.log(1 - p[ok]))).sum())
    else:
        s2 = max(sse / max(n[ok].sum(), 1), 1e-12)
        ll = float(-0.5 * n[ok].sum() * (np.log(2 * np.pi * s2) + 1))
    names = {"M2": ["c", "beta", "A1", "A2"], "M1": ["c", "beta", "A1"], "M0": ["c", "A1", "A2"],
             "M2g": ["c", "beta", "gamma", "A1", "A2"]}[model]
    out = {nm: float(v) for nm, v in zip(names, coef)}
    out.update({"l1": float(l1), "l2": float(l2) if l2 is not None else None, "ll": ll,
                "aic": 2 * NPAR[model] - 2 * ll, "yhat": yh.tolist()})
    return out


def fit_compare(num, den, binary=True, B_disp: np.ndarray | None = None) -> dict:
    """M2 / M1 / M0 (+ M2g) on the pooled curve. Quasi-AIC uses the dispersion c-hat = mean over k of the bootstrap
    variance of the rate divided by its binomial variance (cluster dependence)."""
    n = den.sum(0); y = num.sum(0) / np.clip(n, 1e-12, None)
    fits = {m: fit_curve(y, n, m, binary) for m in ("M2", "M1", "M0", "M2g")}
    chat = 1.0
    if B_disp is not None and binary:
        bs = (B_disp @ num) / np.clip(B_disp @ den, 1e-12, None)
        v_bs = bs.var(0)
        v_bin = y * (1 - y) / np.clip(n, 1, None)
        okk = v_bin > 0
        chat = float(max(1.0, np.median(v_bs[okk] / v_bin[okk])))
    out = {"fits": {m: {k_: v for k_, v in f.items() if k_ != "yhat"} for m, f in fits.items()}, "chat": chat,
           "y": y.tolist(), "n": n.tolist()}
    for a, b in (("M2", "M1"), ("M2", "M0"), ("M1", "M0"), ("M2g", "M2")):
        d_aic = fits[b]["aic"] - fits[a]["aic"]
        d_qaic = (-2 * fits[b]["ll"] / chat + 2 * NPAR[b]) - (-2 * fits[a]["ll"] / chat + 2 * NPAR[a])
        out[f"dAIC_{a}_vs_{b}"] = float(d_aic)
        out[f"dQAIC_{a}_vs_{b}"] = float(d_qaic)
    return out


def param_boot(num, den, B: np.ndarray, model: str = "M2", binary: bool = True, l2max: float | None = 12.0) -> dict:
    """Cluster-bootstrap CIs of the fitted parameters (beta, l1, l2, A1, A2, c) with l2 capped (Amendment A3: a slow
    exponential with l2 near 20 mimics the ramp over 40 calls, so beta is read with l2 <= 12)."""
    n = den.sum(0); y = num.sum(0) / np.clip(n, 1e-12, None)
    pt = fit_curve(y, n, model, binary, l2max)
    keys = [k_ for k_ in ("c", "beta", "gamma", "A1", "A2", "l1", "l2") if pt.get(k_) is not None]
    bs = {k_: [] for k_ in keys}
    for b in range(B.shape[0]):
        nb = B[b] @ den; yb = (B[b] @ num) / np.clip(nb, 1e-12, None)
        f = fit_curve(yb, nb, model, binary, l2max)
        for k_ in keys:
            bs[k_].append(f[k_])
    out = {k_: [float(pt[k_]), *L._ci(np.array(bs[k_], float))] for k_ in keys}
    out["yhat"] = pt["yhat"]
    return out


def cap_curve(W: np.ndarray, c0: float = 1.0, dt: np.ndarray | None = None, dt_reset: float | None = None) -> np.ndarray:
    """Y(L) for L = 1..len(W): output per call (dt None) or per second (dt per call k, dt_reset = consolidation gap)."""
    cs = np.cumsum(W)
    Ls = np.arange(1, len(W) + 1)
    if dt is None:
        return cs / (Ls + c0)
    return cs / (np.cumsum(dt) + (dt_reset or 0.0))


def cap_stats(num, den, B: np.ndarray, c0: float = 1.0, lmin: int = 5, dt_num=None, dt_den=None, dt_reset=None) -> dict:
    """L* = argmax Y(L) on [lmin, 40] with cluster bootstrap; P(L* = 40), P(L* < 35); Y(L)/Y(40) at L = 10, 20, 30."""
    def ystar(nu, de, dn=None, dd=None):
        W = nu / np.clip(de, 1e-12, None)
        dt = None if dn is None else dn / np.clip(dd, 1e-12, None)
        Y = cap_curve(W, c0, dt, dt_reset)
        Ls = np.arange(lmin, len(W) + 1)
        return Ls[np.argmax(Y[lmin - 1:])], Y
    Lpt, Ypt = ystar(num.sum(0), den.sum(0), None if dt_num is None else dt_num.sum(0),
                     None if dt_den is None else dt_den.sum(0))
    bsL, bsY = [], []
    for b in range(B.shape[0]):
        l_, y_ = ystar(B[b] @ num, B[b] @ den, None if dt_num is None else B[b] @ dt_num,
                       None if dt_den is None else B[b] @ dt_den)
        bsL.append(l_); bsY.append(y_)
    bsL = np.array(bsL); bsY = np.array(bsY)
    rel = {f"Y{L_}_over_Y40": [float(Ypt[L_ - 1] / Ypt[-1]), *L._ci(bsY[:, L_ - 1] / bsY[:, -1])] for L_ in (10, 20, 30)}
    return {"L_star": int(Lpt), "P_edge": float((bsL == len(Ypt)).mean()), "P_lt35": float((bsL < 35).mean()),
            "L_star_ci": [float(np.percentile(bsL, 2.5)), float(np.percentile(bsL, 97.5))], "Y": Ypt.tolist(), **rel}


def extrapolate(fit_g: dict, fit_lin: dict, W_emp: np.ndarray, c0: float = 1.0, Lmax: int = 200) -> dict:
    """Y(L) beyond 40 from the curvature fit (M2g) and the linear-ramp fit (M2): empirical W for k <= 40."""
    out = {}
    for nm, f in (("M2g", fit_g), ("M2", fit_lin)):
        k = np.arange(41, Lmax + 1, dtype=float)
        x = k - 1
        ext = f["c"] + f.get("beta", 0) * x + f.get("gamma", 0) * x ** 2 + f["A1"] * np.exp(-x / f["l1"]) + \
            f.get("A2", 0) * np.exp(-x / (f["l2"] or 1))
        Wf = np.r_[W_emp, np.clip(ext, 0, 1)]
        Y = cap_curve(Wf, c0)
        Ls = np.arange(5, Lmax + 1)
        out[nm] = {"L_star": int(Ls[np.argmax(Y[4:])]), "Y60_over_Y40": float(Y[59] / Y[39]),
                   "Y80_over_Y40": float(Y[79] / Y[39]), "Yinf_proxy_over_Y40": float(Y[-1] / Y[39])}
    return out


# ================================================================================================= reference sensitivity
def reference_table(calls: pl.DataFrame, ev: pl.DataFrame, B: int = 300, seed: int = 0) -> dict:
    """Omega (+1..+10) and Delta V (+1..+20) of forced resets against five references, consistent cluster bootstrap."""
    rng = np.random.default_rng(seed)
    e = ev.filter(pl.col("ev_kind") == "forced")
    p = L.panel(calls, e, -40, 20)
    if p.height == 0:
        return {}
    cl_codes = np.unique(p["cl"].to_numpy())
    idx = {v: i for i, v in enumerate(cl_codes)}
    ncl = len(cl_codes)

    def sums(df, mask):
        d = df.filter(mask)
        ci = np.array([idx[v] for v in d["cl"].to_numpy()], dtype=int)
        return (np.bincount(ci, d["any_write"].to_numpy().astype(float), ncl), np.bincount(ci, minlength=ncl).astype(float))

    S = {"post10": sums(p, pl.col("k").is_between(1, 10)), "far": sums(p, pl.col("k").is_between(-20, -11)),
         "near": sums(p, pl.col("k").is_between(-10, -1)), "whole": sums(p, pl.col("k").is_between(-40, -1))}
    cc = calls.with_columns((pl.col("agent").cast(pl.Utf8) + "_" + pl.col("pt_date")).alias("cl")).filter(
        pl.col("cl").is_in(list(cl_codes)))
    S["steady"] = sums(cc, pl.col("pos").is_between(11, 30))
    S["sawtooth"] = sums(cc, (pl.col("seg_kind") == "forced") & (pl.col("seg_end_kind") == "forced")
                         & (pl.col("seg_len") == KMAX))
    # per-k post curve for Delta V
    kk = p.filter(pl.col("k").is_between(1, 20))
    ci = np.array([idx[v] for v in kk["cl"].to_numpy()], dtype=int)
    kn = np.zeros((ncl, 20)); kd = np.zeros((ncl, 20))
    np.add.at(kn, (ci, kk["k"].to_numpy() - 1), kk["any_write"].to_numpy().astype(float))
    np.add.at(kd, (ci, kk["k"].to_numpy() - 1), 1.0)
    W = L.boot_weights(ncl, B, rng)
    out = {"n_events": int(e.height), "n_clusters": ncl, "refs": {}}
    post = S["post10"][0].sum() / S["post10"][1].sum()
    bpost = (W @ S["post10"][0]) / np.clip(W @ S["post10"][1], 1e-12, None)
    curve = kn.sum(0) / np.clip(kd.sum(0), 1e-12, None)
    bcurve = (W @ kn) / np.clip(W @ kd, 1e-12, None)
    for r in ("far", "near", "whole", "steady", "sawtooth"):
        num, den = S[r]
        if den.sum() == 0:
            continue
        ref = num.sum() / den.sum()
        bref = (W @ num) / np.clip(W @ den, 1e-12, None)
        om = post / ref - 1
        bom = bpost / np.clip(bref, 1e-12, None) - 1
        dv = float((curve - ref).sum())
        bdv = (bcurve - bref[:, None]).sum(1)
        out["refs"][r] = {"W_ref": float(ref), "Omega": [float(om), *L._ci(bom)], "dV": [dv, *L._ci(bdv)]}
    oms = [v["Omega"][0] for v in out["refs"].values()]
    out["spread"] = float(max(oms) - min(oms))
    out["all_neg"] = bool(all(v["Omega"][2] < 0 for v in out["refs"].values()))
    out["W_post10"] = float(post)
    return out


# ================================================================================================= R3 re-open share
def object_panel(calls: pl.DataFrame, ev: pl.DataFrame, obj: pl.DataFrame, col: str, kinds=("forced", "voluntary", "pseudo31")):
    e = ev.filter(pl.col("ev_kind").is_in(list(kinds)) & (pl.col("n_pre_avail").cast(pl.Int32) >= 20)
                  & (pl.col("n_post_avail").cast(pl.Int32) >= 10))
    p = L.panel(calls, e, -20, 10)
    tid = calls.select("agent", "pt_date", pl.col("seq").alias("cseq"), "turn_id")
    p = p.join(tid, on=["agent", "pt_date", "cseq"], how="left").join(obj.select("turn_id", pl.col(col).alias("obj")),
                                                                         on="turn_id", how="left")
    return p


def reopen_sums(p: pl.DataFrame, kind: str, cl_index: dict, ncl: int, newcol: str | None = None):
    """Per-cluster: n post read calls with objects, n hits (>= 1 object in the pre set), recency ranks of hits."""
    q = p.filter(pl.col("ev_kind") == kind)
    pre = (q.filter(pl.col("k") < 0).select("ev_id", "k", "obj").explode("obj").drop_nulls("obj")
           .group_by("ev_id", "obj").agg(pl.col("k").max().alias("k_last")))
    post = (q.filter(pl.col("k").is_between(1, 10) & pl.col("cat").is_in(READ_IDX) & pl.col("obj").is_not_null()
                     & (pl.col("obj").list.len() > 0))
            .select("ev_id", "k", "cl", "obj"))
    if post.height == 0:
        return np.zeros(ncl), np.zeros(ncl), np.array([]), 0.0
    hit = (post.explode("obj").join(pre, on=["ev_id", "obj"], how="left")
           .group_by("ev_id", "k").agg(pl.col("k_last").max().alias("k_last"), pl.col("cl").first()))
    ci = np.array([cl_index[v] for v in hit["cl"].to_numpy()], dtype=int)
    is_hit = hit["k_last"].is_not_null().to_numpy().astype(float)
    n = np.bincount(ci, minlength=ncl).astype(float)
    h = np.bincount(ci, is_hit, ncl)
    ranks = -hit["k_last"].drop_nulls().to_numpy()
    pre_size = float(pre.group_by("ev_id").len()["len"].mean()) if pre.height else 0.0
    return n, h, ranks, pre_size


def reopen_stats(p: pl.DataFrame, B: int = 500, seed: int = 0) -> dict:
    rng = np.random.default_rng(seed)
    cl_codes = np.unique(p["cl"].to_numpy())
    cl_index = {v: i for i, v in enumerate(cl_codes)}
    ncl = len(cl_codes)
    W = L.boot_weights(ncl, B, rng)
    res, S = {}, {}
    for kind in ("forced", "voluntary", "pseudo31"):
        n, h, ranks, ps = reopen_sums(p, kind, cl_index, ncl)
        S[kind] = (n, h)
        if n.sum() == 0:
            res[kind] = {"n_read_calls": 0}
            continue
        rho = h.sum() / n.sum()
        b = (W @ h) / np.clip(W @ n, 1e-12, None)
        res[kind] = {"n_read_calls": int(n.sum()), "rho": [float(rho), *L._ci(b)], "mean_pre_set": ps,
                     "n_events": int(p.filter(pl.col("ev_kind") == kind)["ev_id"].n_unique()),
                     "rank_median": float(np.median(ranks)) if len(ranks) else None,
                     "rank_share_last5": float((ranks <= 5).mean()) if len(ranks) else None}
    for a, bk in (("forced", "pseudo31"), ("forced", "voluntary")):
        na, ha = S[a]; nb, hb = S[bk]
        if na.sum() == 0 or nb.sum() == 0:
            continue
        d = ha.sum() / na.sum() - hb.sum() / nb.sum()
        bd = (W @ ha) / np.clip(W @ na, 1e-12, None) - (W @ hb) / np.clip(W @ nb, 1e-12, None)
        res[f"d_{a}_{bk}"] = [float(d), *L._ci(bd)]
    return res


def new_object_flags(calls: pl.DataFrame, obj: pl.DataFrame, col: str) -> pl.DataFrame:
    """Per call: all of its objects are new to the agent-day (first occurrence at this call)."""
    c = calls.select("turn_id", "agent", "pt_date", "seq").join(obj.select("turn_id", pl.col(col).alias("obj")),
                                                                   on="turn_id", how="inner")
    x = c.explode("obj").drop_nulls("obj")
    first = x.group_by("agent", "pt_date", "obj").agg(pl.col("seq").min().alias("s0"))
    x = x.join(first, on=["agent", "pt_date", "obj"]).with_columns((pl.col("seq") == pl.col("s0")).alias("new"))
    return x.group_by("turn_id").agg(pl.col("new").all().alias("all_new"))


# ================================================================================================= R4 loop lever
def loop_strata(calls: pl.DataFrame, ev: pl.DataFrame, kinds=("forced", "pseudo31"), lcol: str = "in_loop",
                wcol: str = "any_write") -> pl.DataFrame:
    """Per event: pre-window (-10..-1) loop count, write and work sums pre / post (+1..+10)."""
    e = ev.filter(pl.col("ev_kind").is_in(list(kinds)))
    p = L.panel(calls, e, -10, 10)
    if lcol != "in_loop":
        p = p.with_columns(pl.col(lcol).alias("in_loop"))
    if wcol != "any_write":
        p = p.with_columns(pl.col(wcol).alias("any_write"))
    g = p.group_by("ev_id").agg(
        pl.col("ev_kind").first(), pl.col("cl").first(), pl.col("agent").first(),
        pl.col("in_loop").filter(pl.col("k") < 0).sum().alias("nl"),
        pl.col("any_write").filter(pl.col("k") < 0).sum().alias("w_pre"), (pl.col("k") < 0).sum().alias("n_pre"),
        pl.col("any_write").filter(pl.col("k") > 0).sum().alias("w_post"), (pl.col("k") > 0).sum().alias("n_post"),
        pl.col("n_work").filter(pl.col("k") < 0).sum().alias("k_pre"),
        pl.col("n_work").filter(pl.col("k") > 0).sum().alias("k_post"))
    return g.with_columns(pl.when(pl.col("nl") >= 3).then(pl.lit("loop")).when(pl.col("nl") == 0)
                          .then(pl.lit("free")).otherwise(pl.lit("light")).alias("stratum"))


def lever_stats(g: pl.DataFrame, B: int = 500, seed: int = 0, outcome: str = "w") -> dict:
    """E_s = dW(forced, s) - dW(pseudo31, s), ratio of sums per (kind, stratum); DDD = E_loop - E_free."""
    rng = np.random.default_rng(seed)
    cl_codes = np.unique(g["cl"].to_numpy())
    idx = {v: i for i, v in enumerate(cl_codes)}
    ncl = len(cl_codes)
    W = L.boot_weights(ncl, B, rng)
    S = {}
    for kind in ("forced", "pseudo31"):
        for s in ("loop", "free"):
            d = g.filter((pl.col("ev_kind") == kind) & (pl.col("stratum") == s))
            ci = np.array([idx[v] for v in d["cl"].to_numpy()], dtype=int)
            S[(kind, s)] = tuple(np.bincount(ci, d[c].to_numpy().astype(float), ncl) for c in
                                 (f"{outcome}_post", "n_post", f"{outcome}_pre", "n_pre")) + (d.height,)

    def dW(t, w=None):
        a, b, c, d_, _ = t
        if w is None:
            return a.sum() / max(b.sum(), 1e-12) - c.sum() / max(d_.sum(), 1e-12)
        return (w @ a) / np.clip(w @ b, 1e-12, None) - (w @ c) / np.clip(w @ d_, 1e-12, None)

    out = {"n": {f"{k}_{s}": int(v[4]) for (k, s), v in S.items()}}
    for (k, s), v in S.items():
        out[f"rate_{k}_{s}"] = {"pre": float(v[2].sum() / max(v[3].sum(), 1)), "post": float(v[0].sum() / max(v[1].sum(), 1))}
    E = {}
    for s in ("loop", "free"):
        pt = dW(S[("forced", s)]) - dW(S[("pseudo31", s)])
        bs = dW(S[("forced", s)], W) - dW(S[("pseudo31", s)], W)
        E[s] = (pt, bs)
        out[f"E_{s}"] = [float(pt), *L._ci(bs)]
    out["DDD"] = [float(E["loop"][0] - E["free"][0]), *L._ci(E["loop"][1] - E["free"][1])]
    # relative (log-ratio) version: ln(post/pre)_F - ln(post/pre)_P per stratum
    def lr(t, w=None):
        a, b, c, d_, _ = t
        if w is None:
            return np.log(max(a.sum() / max(b.sum(), 1e-12), 1e-6)) - np.log(max(c.sum() / max(d_.sum(), 1e-12), 1e-6))
        return np.log(np.clip((w @ a) / np.clip(w @ b, 1e-12, None), 1e-6, None)) - \
            np.log(np.clip((w @ c) / np.clip(w @ d_, 1e-12, None), 1e-6, None))
    R = {}
    for s in ("loop", "free"):
        R[s] = (lr(S[("forced", s)]) - lr(S[("pseudo31", s)]), lr(S[("forced", s)], W) - lr(S[("pseudo31", s)], W))
        out[f"logE_{s}"] = [float(R[s][0]), *L._ci(R[s][1])]
    out["logDDD"] = [float(R["loop"][0] - R["free"][0]), *L._ci(R["loop"][1] - R["free"][1])]
    return out


def loop_curve(saw: pl.DataFrame) -> list:
    s = saw.group_by("k").agg(pl.col("in_loop").mean()).sort("k")
    return s["in_loop"].to_list()


# ================================================================================================= R1 checked Theta_c
def theta_c_soft(calls: pl.DataFrame, ev: pl.DataFrame, q_post: np.ndarray, q_mid: np.ndarray,
                 q_post_bs: np.ndarray | None = None, q_mid_bs: np.ndarray | None = None, B: int = 300, seed: int = 0):
    """Theta_c (post5 vs far, forced) with soft re-acquisition labels q[cat] (post window: q_post; far: q_mid).
    q_*_bs: (B, NCAT) label-bootstrap draws used jointly with the cluster bootstrap."""
    rng = np.random.default_rng(seed)
    p = L.panel(calls, ev.filter(pl.col("ev_kind") == "forced"), -20, 5)
    cl_codes, cl = np.unique(p["cl"].to_numpy(), return_inverse=True)
    ncl = len(cl_codes)
    ag_codes, ag = np.unique(p["agent"].to_numpy(), return_inverse=True)
    NC = len(C.CATS)
    cell = ag * (NC + 1) + (p["pcat"].to_numpy().astype(int) + 1)
    ncell = len(ag_codes) * (NC + 1)
    cat = p["cat"].to_numpy().astype(int)
    nw = 1 - p["any_write"].to_numpy().astype(float)
    k = p["k"].to_numpy()
    out = {}
    T = {}
    for wn, (lo, hi) in (("post5", (1, 5)), ("far", (-20, -11))):
        m = (k >= lo) & (k <= hi) & (nw > 0)
        # N[cl, cell, cat] stored sparse via flat index
        flat = (cl[m] * ncell + cell[m]) * NC + cat[m]
        cnt = np.bincount(flat, minlength=ncl * ncell * NC).reshape(ncl, ncell, NC).astype(np.float32)
        T[wn] = cnt
    W = L.boot_weights(ncl, B, rng)

    def th(qp, qm, w=None):
        A = T["post5"]; Bm = T["far"]
        if w is None:
            an = (A @ qp).sum(0); ad = A.sum((0, 2))
            bn = (Bm @ qm).sum(0); bd = Bm.sum((0, 2))
        else:
            an = w @ (A @ qp); ad = w @ A.sum(2)
            bn = w @ (Bm @ qm); bd = w @ Bm.sum(2)
        ok = (ad > 0) & (bd > 0)
        wt = np.where(ok, ad, 0); wt = wt / max(wt.sum(), 1e-12)
        return float((wt * (np.where(ok, an / np.clip(ad, 1e-12, None), 0) - np.where(ok, bn / np.clip(bd, 1e-12, None), 0))).sum())

    out["theta_c"] = th(q_post, q_mid)
    bs = []
    for b in range(B):
        qp = q_post_bs[b % len(q_post_bs)] if q_post_bs is not None else q_post
        qm = q_mid_bs[b % len(q_mid_bs)] if q_mid_bs is not None else q_mid
        bs.append(th(qp, qm, W[b]))
    out["ci"] = list(L._ci(np.array(bs)))
    out["n_events"] = int(p["ev_id"].n_unique())
    return out


def recency_frac(calls: pl.DataFrame, ev: pl.DataFrame, obj: pl.DataFrame, col: str, ev_ids, tau: float = 15.0,
                 pre: int = 20) -> pl.DataFrame:
    """Per event: recency-weighted (exp(-age/tau), age in calls since the object's last touch) share of the agent-day's
    earlier objects that sit in the pre window (age <= pre). Under a recency null a read call re-opens a pre-window
    object with probability q * frac (Amendment A4)."""
    ev2 = ev.filter(pl.col("ev_id").is_in(list(ev_ids))).select("ev_id", "ev_kind", "agent", "pt_date",
                                                                 pl.col("seq").alias("seq_e"))
    hist = (calls.select("turn_id", "agent", "pt_date", "seq").join(obj.select("turn_id", pl.col(col).alias("o")),
                                                                     on="turn_id")
            .explode("o").drop_nulls("o"))
    jn = hist.join(ev2, on=["agent", "pt_date"]).filter(pl.col("seq") < pl.col("seq_e"))
    jn = jn.group_by("ev_id", "o").agg((pl.col("seq_e") - pl.col("seq")).min().alias("age"))
    jn = jn.with_columns((-pl.col("age") / tau).exp().alias("w"), (pl.col("age") <= pre).alias("inpre"))
    fr = jn.group_by("ev_id").agg((pl.col("w") * pl.col("inpre")).sum().alias("wp"), pl.col("w").sum().alias("wa"))
    return ev2.select("ev_id", "ev_kind").join(fr.with_columns((pl.col("wp") / pl.col("wa")).alias("frac")),
                                               on="ev_id", how="left").with_columns(pl.col("frac").fill_null(0.0))


def recency_adjusted(p: pl.DataFrame, fr: pl.DataFrame, st: dict, B: int = 500, seed: int = 0) -> dict:
    """Excess re-open share over the recency null: d_obs - q_hat (frac_a - frac_b), q_hat = rho_pseudo / frac_pseudo,
    with frac averaged over post read calls (call-weighted), cluster bootstrap over the same clusters."""
    rng = np.random.default_rng(seed)
    is_post = (pl.col("k").is_between(1, 10) & pl.col("cat").is_in(READ_IDX) & pl.col("obj").is_not_null()
               & (pl.col("obj").list.len() > 0))
    q = p.filter(is_post).join(fr.select("ev_id", "frac"), on="ev_id", how="left").with_columns(pl.col("frac").fill_null(0.0))
    pre = (p.filter(pl.col("k") < 0).select("ev_id", "obj").explode("obj").drop_nulls("obj").unique())
    hit = (q.select("ev_id", "k", "obj").explode("obj").join(pre, on=["ev_id", "obj"], how="semi")
           .select("ev_id", "k").unique().with_columns(pl.lit(1.0).alias("hit")))
    q = q.join(hit, on=["ev_id", "k"], how="left").with_columns(pl.col("hit").fill_null(0.0))
    cl_codes = np.unique(p["cl"].to_numpy()); idx = {v: i for i, v in enumerate(cl_codes)}; ncl = len(cl_codes)
    W = L.boot_weights(ncl, B, rng)
    S = {}
    for kind in ("forced", "voluntary", "pseudo31"):
        g = q.filter(pl.col("ev_kind") == kind)
        ci = np.array([idx[v] for v in g["cl"].to_numpy()], dtype=int)
        S[kind] = (np.bincount(ci, minlength=ncl).astype(float), np.bincount(ci, g["hit"].to_numpy(), ncl),
                   np.bincount(ci, g["frac"].to_numpy(), ncl))
    out = {k_: {"frac_mean": float(v[2].sum() / max(v[0].sum(), 1))} for k_, v in S.items()}

    def est(w=None):
        f = (lambda x: x.sum()) if w is None else (lambda x: w @ x)
        r = {k_: f(v[1]) / np.maximum(f(v[0]), 1e-12) for k_, v in S.items()}
        fr_ = {k_: f(v[2]) / np.maximum(f(v[0]), 1e-12) for k_, v in S.items()}
        qh = r["pseudo31"] / np.maximum(fr_["pseudo31"], 1e-12)
        return {"q_hat": qh,
                "excess_FP": (r["forced"] - r["pseudo31"]) - qh * (fr_["forced"] - fr_["pseudo31"]),
                "excess_FV": (r["forced"] - r["voluntary"]) - qh * (fr_["forced"] - fr_["voluntary"]),
                "null_dFP": qh * (fr_["forced"] - fr_["pseudo31"])}
    pt = est(); bs = est(W)
    for k_ in pt:
        out[k_] = [float(pt[k_]), *L._ci(np.asarray(bs[k_], float))]
    return out
