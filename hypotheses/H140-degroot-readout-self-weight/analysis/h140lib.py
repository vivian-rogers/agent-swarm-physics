"""H140 estimators on the per-row Gram terms written by scheme/h140scheme.py.

O1 (primary): exactly identified IV (2SLS) over the 32 coordinates of y, one scalar weight per term:
    y = w0 p + w1 s_self p + w2 g p + gamma1 k^-b s + gammaF sF + w_anchor h + e,   g = (1 - gamma_auto)^dn,
    instruments: z, s_self z, g z, k^-b s, sF, h   (z = mean of the reader's third- and fourth-last segment statements).
    b is profiled on a grid by the structural residual sum of squares; agent-day cluster bootstrap (b re-profiled).
Variants are specs (lists of (base, coef) terms): no call-gap term (the HH's form), chat-form s_self, s_self deciles,
OLS (instruments = regressors), p1 (last statement only).
Also: closure per k bin (O3), matched-age read - in-flight contrast and batch redundancy r (O4; H113's estimators),
N1 cross-day surrogate batches, N2 within-agent-day permutation of s_self, DerSimonian-Laird pooling.
"""
from __future__ import annotations

import math

import numpy as np
import polars as pl
import scipy.sparse as sp

BASES = ("y", "p", "p1", "z", "s", "sF", "h", "f")
BI = {b: i for i, b in enumerate(BASES)}
B_GRID = np.round(np.arange(-0.5, 1.5001, 0.02), 2)
K_BINS = [(1, 1), (2, 2), (3, 4), (5, 8), (9, 16), (17, 10_000)]
AGE_BINS = [(0, 30), (30, 60), (60, 120)]
GAMMA_AUTO = 0.0094   # H130, #51 (per call)

# spec: list of (regressor base, instrument base, coef name)
SPEC_MAIN = [("p", "z", "1"), ("p", "z", "sig"), ("p", "z", "g"), ("s", "s", "kap"), ("sF", "sF", "1"), ("h", "h", "1")]
NAMES_MAIN = ["w0", "w1", "w2", "gamma1", "gammaF", "w_anchor"]


def spec_variant(name: str) -> tuple[list, list]:
    if name == "main":
        return SPEC_MAIN, NAMES_MAIN
    if name == "noDn":          # the HH's form
        return [t for t in SPEC_MAIN if t[2] != "g"], [n for n in NAMES_MAIN if n != "w2"]
    if name == "chat":
        return [(a, b, "sigc" if c == "sig" else c) for a, b, c in SPEC_MAIN], NAMES_MAIN
    if name == "ols":
        return [(a, a, c) for a, b, c in SPEC_MAIN], NAMES_MAIN
    if name == "p1":
        return [("p1" if a == "p" else a, b, c) for a, b, c in SPEC_MAIN], NAMES_MAIN
    if name == "deciles":
        sp_ = [("p", "z", f"dec{d}") for d in range(10)] + [("p", "z", "g"), ("s", "s", "kap"), ("sF", "sF", "1"), ("h", "h", "1")]
        return sp_, [f"wdec{d}" for d in range(10)] + ["w2", "gamma1", "gammaF", "w_anchor"]
    if name in ("main_t", "main_tk", "noDn_t"):
        base, nms = spec_variant("main" if name != "noDn_t" else "noDn")
        extra = [("p", "z", "e30")] + ([("p", "z", "gk")] if name == "main_tk" else [])
        return base[:3 if name != "noDn_t" else 2] + extra + base[3 if name != "noDn_t" else 2:], \
            nms[:3 if name != "noDn_t" else 2] + ["w3"] + (["w4"] if name == "main_tk" else []) + nms[3 if name != "noDn_t" else 2:]
    if name in ("firstA1", "firstA1noDn"):
        base, nms = spec_variant("first")
        if name == "firstA1noDn":
            base, nms = [t for t in base if t[2] != "g"], [n for n in nms if n != "w2"]
        m = 3 if name == "firstA1" else 2
        ex = [("p", "z", "e30"), ("p", "z", "lk"), ("p", "z", "lkF")]
        return base[:m] + ex + base[m:], nms[:m] + ["w3", "w5", "w6"] + nms[m:]
    if name in ("A1chat", "A1ols", "A1p1", "A1deciles"):
        base, nms = spec_variant("A1")
        if name == "A1chat":
            return [(a, b, "sigc" if c == "sig" else c) for a, b, c in base], nms
        if name == "A1ols":
            return [(a, a, c) for a, b, c in base], nms
        if name == "A1p1":
            return [("p1" if a == "p" else a, b, c) for a, b, c in base], nms
        sp_ = [("p", "z", f"dec{d}") for d in range(10)] + [t for t in base if t[2] not in ("1", "sig") or t[0] != "p"]
        return sp_, [f"wdec{d}" for d in range(10)] + [n for t, n in zip(base, nms) if t[2] not in ("1", "sig") or t[0] != "p"]
    if name == "o2A1":          # regime I/II: no self-share, A1 nuisance terms kept
        base, nms = spec_variant("A1")
        keep = [i for i, t in enumerate(base) if t[2] not in ("sig", "g")]
        return [base[i] for i in keep], [nms[i] for i in keep]
    if name in ("A1", "A1noDn"):
        # Amendment A1 (2026-10-07, after the synthetic, before real data): add the wall-clock gap term exp(-dt/30 min) and
        # the batch-size nuisance terms log(1+k), log(1+kF) on the self-weight
        base, nms = spec_variant("main" if name == "A1" else "noDn")
        m = 3 if name == "A1" else 2
        ex = [("p", "z", "e30"), ("p", "z", "lk"), ("p", "z", "lkF")]
        return base[:m] + ex + base[m:], nms[:m] + ["w3", "w5", "w6"] + nms[m:]
    if name in ("main_k", "main_f", "main_kf", "main_tkf"):
        base, nms = spec_variant("main")
        ex, en = [], []
        if name in ("main_tkf",):
            ex += [("p", "z", "e30")]; en += ["w3"]
        if name in ("main_k", "main_kf", "main_tkf"):
            ex += [("p", "z", "lk"), ("p", "z", "lkF")]; en += ["w5", "w6"]
        tail, tn = base[3:], nms[3:]
        if name in ("main_f", "main_kf", "main_tkf"):
            tail = tail + [("f", "f", "1")]; tn = tn + ["w_field"]
        return base[:3] + ex + tail, nms[:3] + en + tn
    if name == "o2only":        # regime I/II: no self-share
        return [("p", "z", "1"), ("s", "s", "kap"), ("sF", "sF", "1"), ("h", "h", "1")], ["w0", "gamma1", "gammaF", "w_anchor"]
    if name == "first":         # NE41: first post-reset call indicator interacting with p
        return [("p", "z", "1"), ("p", "z", "first"), ("p", "z", "g"), ("s", "s", "kap"), ("sF", "sF", "1"), ("h", "h", "1")], \
            ["w_base", "dw_first", "w2", "gamma1", "gammaF", "w_anchor"]
    raise KeyError(name)


def gram_tensor(g: pl.DataFrame) -> np.ndarray:
    n = len(g)
    G = np.zeros((n, len(BASES), len(BASES)))
    for i, a in enumerate(BASES):
        for j, b in enumerate(BASES):
            if j < i:
                continue
            v = g[f"g_{a}_{b}"].to_numpy().astype(np.float64)
            G[:, i, j] = v; G[:, j, i] = v
    return G


def coef_matrix(meta: pl.DataFrame, spec, b: float, gamma_auto: float = GAMMA_AUTO) -> np.ndarray:
    n = len(meta)
    k = meta["k"].to_numpy().astype(float)
    sig = meta["s_self"].to_numpy().astype(float)
    out = np.zeros((n, len(spec)))
    for c, (_, _, nm) in enumerate(spec):
        if nm == "1":
            out[:, c] = 1.0
        elif nm == "sig":
            out[:, c] = sig
        elif nm == "sigc":
            out[:, c] = meta["s_self_chat"].to_numpy().astype(float)
        elif nm == "g":
            out[:, c] = (1 - gamma_auto) ** np.maximum(meta["dn"].to_numpy().astype(float), 0)
        elif nm == "e30":       # wall-clock field decay (amendment candidate): exp(-dt / 30 min)
            out[:, c] = np.exp(-np.maximum(meta["dt_s"].to_numpy().astype(float), 0) / 1800.0)
        elif nm == "lk":        # batch-size nuisance on the self-weight (amendment candidate)
            out[:, c] = np.log1p(meta["k"].to_numpy().astype(float))
        elif nm == "lkF":
            out[:, c] = np.log1p(meta["kF"].to_numpy().astype(float))
        elif nm == "gk":        # H130 kick decay per call (amendment candidate)
            out[:, c] = 0.85 ** np.maximum(meta["dn"].to_numpy().astype(float), 0)
        elif nm == "kap":
            out[:, c] = np.where(k >= 1, np.maximum(k, 1) ** (-b), 0.0)
        elif nm == "first":
            out[:, c] = meta["first"].to_numpy().astype(float)
        elif nm.startswith("dec"):
            d = int(nm[3:])
            out[:, c] = (meta["sig_dec"].to_numpy() == d).astype(float)
        else:
            raise KeyError(nm)
    return out


def cluster_ids(meta: pl.DataFrame) -> np.ndarray:
    return np.unique((meta["agent"].cast(pl.String) + "|" + meta["pt_date"]).to_numpy(), return_inverse=True)[1]


class Fit:
    """Per-cluster sufficient statistics on a b grid for one spec."""

    def __init__(self, meta: pl.DataFrame, G: np.ndarray, spec, grid=B_GRID, gamma_auto: float = GAMMA_AUTO):
        self.meta, self.spec, self.grid = meta, spec, np.atleast_1d(grid)
        cl = cluster_ids(meta); self.ncl = int(cl.max()) + 1
        n = len(meta); J = len(spec)
        C = sp.csr_matrix((np.ones(n), (cl, np.arange(n))), shape=(self.ncl, n))
        xb = np.array([BI[a] for a, _, _ in spec]); zb = np.array([BI[b] for _, b, _ in spec])
        Gzx = G[:, zb[:, None], xb[None, :]]; Gxx = G[:, xb[:, None], xb[None, :]]
        Gzy = G[:, zb, 0]; Gxy = G[:, xb, 0]
        nb = len(self.grid)
        self.ZX = np.zeros((nb, self.ncl, J, J)); self.XX = np.zeros_like(self.ZX)
        self.Zy = np.zeros((nb, self.ncl, J)); self.Xy = np.zeros_like(self.Zy)
        self.yy = C @ G[:, 0, 0]
        kapc = [c for c, t in enumerate(spec) if t[2] == "kap"]
        base = None
        for ib, b in enumerate(self.grid):
            if base is not None and not kapc:
                self.ZX[ib], self.XX[ib], self.Zy[ib], self.Xy[ib] = self.ZX[0], self.XX[0], self.Zy[0], self.Xy[0]
                continue
            Cx = coef_matrix(meta, spec, b, gamma_auto)
            Cz = Cx  # instruments carry the same coefficients
            self.ZX[ib] = (C @ (Cz[:, :, None] * Cx[:, None, :] * Gzx).reshape(n, -1)).reshape(self.ncl, J, J)
            self.XX[ib] = (C @ (Cx[:, :, None] * Cx[:, None, :] * Gxx).reshape(n, -1)).reshape(self.ncl, J, J)
            self.Zy[ib] = C @ (Cz * Gzy); self.Xy[ib] = C @ (Cx * Gxy)
            base = True

    def solve(self, w: np.ndarray | None = None):
        """w: (B, ncl) weights or None. Returns b index, beta (B, J), sse grid (B, nb)."""
        W = np.ones((1, self.ncl)) if w is None else w
        nb, ncl, J = self.ZX.shape[0], self.ncl, self.ZX.shape[-1]
        nB = W.shape[0]

        def agg(A):  # (nb, ncl, ...) -> (B, nb, ...)
            sh = A.shape[2:]
            M = np.moveaxis(A, 1, 0).reshape(ncl, -1)
            return (W @ M).reshape((nB, nb) + sh)
        ZX = agg(self.ZX); XX = agg(self.XX); Zy = agg(self.Zy); Xy = agg(self.Xy); yy = W @ self.yy
        ZXr = ZX + 1e-12 * np.eye(J)
        try:
            beta = np.linalg.solve(ZXr, Zy[..., None])[..., 0]
        except np.linalg.LinAlgError:
            beta = np.einsum("...ij,...j->...i", np.linalg.pinv(ZXr), Zy)
        sse = yy[:, None] - 2 * np.einsum("Bbj,Bbj->Bb", beta, Xy) + np.einsum("Bbj,Bbjk,Bbk->Bb", beta, XX, beta)
        ib = np.argmin(sse, axis=1)
        return ib, beta[np.arange(len(ib)), ib], sse


def fit(meta: pl.DataFrame, G: np.ndarray, spec_name: str = "main", B: int = 300, seed: int = 0, grid=B_GRID,
        gamma_auto: float = GAMMA_AUTO, keep_draws: bool = False) -> dict:
    spec, names = spec_variant(spec_name)
    if len(meta) < 30:
        return {"n": len(meta)}
    F = Fit(meta, G, spec, grid, gamma_auto)
    ib, beta, sse = F.solve()
    out = {"n": len(meta), "n_clusters": F.ncl, "b": float(F.grid[ib[0]]), "a": float(1 - F.grid[ib[0]])}
    for nm, v in zip(names, beta[0]):
        out[nm] = float(v)
    if B:
        rng = np.random.default_rng(seed)
        W = np.stack([np.bincount(rng.integers(0, F.ncl, F.ncl), minlength=F.ncl).astype(float) for _ in range(B)])
        ibb, bb, _ = F.solve(W)
        bd = F.grid[ibb]
        out["b_lo"], out["b_hi"] = (float(x) for x in np.percentile(bd, [2.5, 97.5]))
        out["a_lo"], out["a_hi"] = 1 - out["b_hi"], 1 - out["b_lo"]
        out["b_edge"] = float(np.mean((bd <= F.grid[0]) | (bd >= F.grid[-1]))) if len(F.grid) > 1 else 0.0
        for c, nm in enumerate(names):
            out[f"{nm}_lo"], out[f"{nm}_hi"] = (float(x) for x in np.percentile(bb[:, c], [2.5, 97.5]))
            out[f"{nm}_se"] = float(np.std(bb[:, c], ddof=1))
        out["a_se"] = float(np.std(bd, ddof=1))
        if keep_draws:
            out["_draws"] = {"b": bd, "beta": bb, "names": names}
    return out


def closure(meta: pl.DataFrame, res: dict, spec_name: str = "A1", gamma_auto: float = GAMMA_AUTO) -> list[dict]:
    """O3: Sigma = w_self (self terms at bin means) + gamma1 * mean k^(1-b) + w_anchor per k bin (bootstrap draws if kept)."""
    spec, names = spec_variant(spec_name)
    k = meta["k"].to_numpy().astype(float)
    C = coef_matrix(meta, spec, 0.0, gamma_auto)
    selfc = [i for i, t in enumerate(spec) if t[0] in ("p", "p1")]
    ix = {n: i for i, n in enumerate(names)}
    out = []
    dr = res.get("_draws")
    for lo, hi in K_BINS:
        m = (k >= lo) & (k <= hi)
        if m.sum() < 20:
            continue
        cm = C[m].mean(0)

        def S(b, beta):
            ws = sum(beta[i] * cm[i] for i in selfc)
            wr = beta[ix["gamma1"]] * np.mean(k[m] ** (1 - b))
            return ws, wr, ws + wr + beta[ix["w_anchor"]]
        beta0 = np.array([res[n] for n in names])
        ws, wr, est = S(res["b"], beta0)
        row = {"bin": f"{lo}-{hi}" if hi < 10_000 else f">={lo}", "n": int(m.sum()), "k_mean": float(k[m].mean()),
               "w_self": float(ws), "W_read": float(wr), "w_anchor": float(res["w_anchor"]), "Sigma": float(est)}
        if dr is not None:
            ss = np.array([S(dr["b"][q], dr["beta"][q])[2] for q in range(len(dr["beta"]))])
            row["lo"], row["hi"] = (float(x) for x in np.percentile(ss, [2.5, 97.5])); row["se"] = float(np.std(ss, ddof=1))
        out.append(row)
    return out


def placebo_contrast(meta: pl.DataFrame, it: pl.DataFrame, B: int = 300, seed: int = 0) -> dict:
    """H113 O5: matched-age per-item slopes, read items (age <= 120 s) vs in-flight items, weighted by in-flight counts."""
    if it is None or len(it) == 0:
        return {}
    clr = cluster_ids(meta)
    rowpos = {int(r): i for i, r in enumerate(meta["row"].to_list())}
    keep = np.array([int(r) in rowpos for r in it["row"].to_list()])
    it = it.filter(pl.Series(keep))
    if len(it) == 0:
        return {}
    cl = clr[np.array([rowpos[int(r)] for r in it["row"].to_list()])]
    ncl = int(clr.max()) + 1
    rng = np.random.default_rng(seed)
    Wb = [np.bincount(rng.integers(0, ncl, ncl), minlength=ncl).astype(float)[cl] for _ in range(B)]
    age = it["age_s"].to_numpy(); rd = it["read"].to_numpy(); xy = it["xy"].to_numpy().astype(float); xx = it["xx"].to_numpy().astype(float)

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
    out = {"contrast": float(est[0]), "gamma_read": float(est[1]), "gamma_inflight": float(est[2]),
           "n_read": int(rd.sum()), "n_inflight": int((~rd).sum())}
    if ok.sum() >= 20:
        out.update({"lo": float(np.percentile(bs[ok, 0], 2.5)), "hi": float(np.percentile(bs[ok, 0], 97.5)),
                    "se": float(np.std(bs[ok, 0], ddof=1))})
    return out


def redundancy(meta: pl.DataFrame, G: np.ndarray) -> float:
    """H113's r = d ln E|s|^2 / d ln k - 1 over k bins (WLS by counts)."""
    k = meta["k"].to_numpy(); ss = G[:, BI["s"], BI["s"]]
    xs, ys, ws = [], [], []
    for lo, hi in K_BINS:
        m = (k >= lo) & (k <= hi)
        if m.sum() >= 20 and ss[m].mean() > 0:
            xs.append(math.log(k[m].mean())); ys.append(math.log(ss[m].mean())); ws.append(m.sum())
    if len(xs) < 2:
        return float("nan")
    X = np.vstack([np.ones(len(xs)), xs]).T; w = np.sqrt(ws)
    beta = np.linalg.lstsq(X * w[:, None], np.array(ys) * w, rcond=None)[0]
    return float(beta[1] - 1)


def surrogate_gram(G: np.ndarray, g: pl.DataFrame, d: int) -> np.ndarray:
    """Replace the batch sum s by the d-th cross-day surrogate batch (N1)."""
    G2 = G.copy()
    si = BI["s"]
    for bname in ("y", "p", "p1", "z", "sF", "h"):
        v = g[f"u{d}_{bname}"].to_numpy().astype(float)
        G2[:, si, BI[bname]] = v; G2[:, BI[bname], si] = v
    G2[:, si, si] = g[f"u{d}_ss"].to_numpy().astype(float)
    return G2


def permute_sig(meta: pl.DataFrame, seed: int) -> pl.DataFrame:
    """N2: permute s_self across talk calls within each agent-day."""
    rng = np.random.default_rng(seed)
    cl = cluster_ids(meta)
    sig = meta["s_self"].to_numpy().copy()
    order = np.argsort(cl, kind="stable")
    cs = cl[order]
    bounds = np.flatnonzero(np.diff(cs)) + 1
    for grp in np.split(order, bounds):
        sig[grp] = sig[rng.permutation(grp)]
    return meta.with_columns(pl.Series("s_self", sig))


def dl_pool(est, se) -> dict:
    est = np.asarray(est, float); se = np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[ok], se[ok]
    if len(est) == 0:
        return {"k": 0}
    w = 1 / se ** 2
    mu_f = (w * est).sum() / w.sum()
    Q = (w * (est - mu_f) ** 2).sum(); dfq = len(est) - 1
    tau2 = max(0.0, (Q - dfq) / (w.sum() - (w ** 2).sum() / w.sum())) if dfq > 0 else 0.0
    ws = 1 / (se ** 2 + tau2)
    mu = (ws * est).sum() / ws.sum(); s = math.sqrt(1 / ws.sum())
    I2 = max(0.0, (Q - dfq) / Q) if Q > 0 and dfq > 0 else 0.0
    return {"k": int(len(est)), "est": float(mu), "se": float(s), "lo": float(mu - 1.96 * s), "hi": float(mu + 1.96 * s),
            "tau2": float(tau2), "I2": float(I2)}


def prep(meta: pl.DataFrame, gram: pl.DataFrame, pmode: str = "in", require_z: bool = True, drop_templated: bool = True,
         need_sig: bool = True) -> tuple[pl.DataFrame, np.ndarray, pl.DataFrame]:
    """Join meta and gram, apply the scoring filters; returns (meta, G, joined frame)."""
    d = pl.concat([meta, gram], how="horizontal")
    f = (pl.col("pmode") == pmode) & pl.col("h_ok") & (pl.col("dn") >= 0)
    if require_z:
        f = f & pl.col("z_ok")
    if drop_templated:
        f = f & ~pl.col("templated")
    if need_sig:
        f = f & pl.col("s_self").is_not_nan() & pl.col("s_self").is_not_null()
    d = d.filter(f)
    return d, gram_tensor(d), d
