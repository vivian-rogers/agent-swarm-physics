"""H114 library: reply-depth survival, continuation hazard, Markov model ladder (M0/M1/M2), pair gains, cuts.

Depth D(m): agent -> agent parent links back to the root (one DQ2 parent per message; cross-day links cut).
S(d) = P(D >= d) over in-window messages; h(d) = S(d+1)/S(d); g_rep = S(1).
h_tail = sum_{d>=4} S(d+1) / sum_{d>=4} S(d) (d <= DMAX); h_1 = h(1); dh = h_tail - g_rep; delta_h = h_tail - h_1.
M1: first-order author chain, p_k = k's parent share, P(k'|k) ~ R_kk' b_k' (rank 1, IPF fit of L ~ R a b).
M2: same chain with the empirical P(k'|k) = L_kk' / L_k.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import math  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy.stats import chi2  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data/processed/H114-griffiths-phase-pairs"
DMAX = 30
D_TAIL = 4
R_MIN = 10
G_STRONG = 0.5


def load_unit(uid: str, base: Path = OUT):
    return pl.read_parquet(base / "msgs" / f"{uid}.parquet"), pl.read_parquet(base / "reads" / f"{uid}.parquet")


def depth_pass(par: np.ndarray) -> np.ndarray:
    d = np.zeros(len(par), np.int32)
    for k in range(len(par)):
        p = par[k]
        if p >= 0:
            d[k] = d[p] + 1
    return d


# ============================================================================================ survival statistics
def surv_counts(depth: np.ndarray, w: np.ndarray | None = None) -> np.ndarray:
    """N(d) = # messages with depth >= d, d = 0..DMAX+1."""
    dd = np.minimum(depth, DMAX + 1)
    h = np.bincount(dd, weights=w, minlength=DMAX + 2)[: DMAX + 2]
    return np.cumsum(h[::-1])[::-1]


def stats_from_counts(N: np.ndarray) -> dict:
    if N[0] <= 0:
        return {"g_rep": np.nan, "h_1": np.nan, "h_tail": np.nan, "dh": np.nan, "delta_h": np.nan, "n_tail": 0.0}
    g = N[1] / N[0]
    h1 = N[2] / N[1] if N[1] > 0 else np.nan
    num, den = N[D_TAIL + 1: DMAX + 2].sum(), N[D_TAIL: DMAX + 1].sum()
    ht = num / den if den > 0 else np.nan
    return {"g_rep": g, "h_1": h1, "h_tail": ht, "dh": ht - g, "delta_h": ht - h1, "n_tail": float(N[D_TAIL])}


def hazard_curve(N: np.ndarray, dmax: int = 12) -> list:
    return [float(N[d + 1] / N[d]) if N[d] > 0 else float("nan") for d in range(dmax + 1)]


def block_ids(m: pl.DataFrame, n_days: int) -> np.ndarray:
    """Bootstrap blocks: days when the unit has > 5 days, else (day, hour)."""
    day = m["day"].to_numpy().astype(np.int64)
    if n_days > 5:
        return day
    hr = np.floor(m["t"].to_numpy() / 3600.0).astype(np.int64)
    return day * 100000 + (hr - hr.min())


def boot_stats(depth: np.ndarray, sel: np.ndarray, blocks: np.ndarray, B: int, rng) -> dict:
    """Block bootstrap of the survival statistics over in-window messages (sel)."""
    ub, inv = np.unique(blocks[sel], return_inverse=True)
    dd = np.minimum(depth[sel], DMAX + 1)
    Nb = np.zeros((len(ub), DMAX + 2))
    np.add.at(Nb, (inv, dd), 1)
    Nb = np.cumsum(Nb[:, ::-1], 1)[:, ::-1]
    out = {k: [] for k in ("g_rep", "h_1", "h_tail", "dh", "delta_h")}
    for _ in range(B):
        k = rng.integers(0, len(ub), len(ub))
        s = stats_from_counts(Nb[k].sum(0))
        for kk in out:
            out[kk].append(s[kk])
    return {k: np.array(v) for k, v in out.items()}


# ============================================================================================ pair gains and models
def pair_table(m: pl.DataFrame, R: pl.DataFrame) -> pl.DataFrame:
    """Directed pairs (i replies to j): L_ij links (both endpoints in the unit, same day), R_ij reads, g, bounds."""
    au = m["author"].to_numpy()
    par = m["par"].to_numpy()
    nm = m["names"].to_numpy()
    ch = np.flatnonzero(par >= 0)
    L = pl.DataFrame({"reader": au[ch].astype(np.int16), "author": au[par[ch]].astype(np.int16),
                      "names": nm[ch]}).group_by("reader", "author").agg(pl.len().alias("L"),
                                                                        pl.col("names").sum().alias("L_named"))
    Rr = R.with_columns(pl.col("reader").cast(pl.Int16), pl.col("author").cast(pl.Int16))
    P = Rr.join(L, on=["reader", "author"], how="full", coalesce=True).with_columns(
        pl.col("L").fill_null(0), pl.col("L_named").fill_null(0), pl.col("R").fill_null(0))
    P = P.filter(pl.col("reader") != pl.col("author"))
    Lv, Rv = P["L"].to_numpy().astype(float), P["R"].to_numpy().astype(float)
    lo = np.where(Lv > 0, chi2.ppf(0.025, 2 * Lv) / 2, 0.0) / np.maximum(Rv, 1)
    hi = chi2.ppf(0.975, 2 * (Lv + 1)) / 2 / np.maximum(Rv, 1)
    g = np.where(Rv > 0, Lv / np.maximum(Rv, 1), np.nan)
    P = P.with_columns(pl.Series("g", g), pl.Series("g_lo", lo), pl.Series("g_hi", hi))
    return P.with_columns(((pl.col("R") >= R_MIN) & (pl.col("g_lo") > G_STRONG)).alias("strong"))


def ipf_rank1(Lm: np.ndarray, Rm: np.ndarray, iters: int = 500) -> np.ndarray:
    """Fit Lambda_kk' = R_kk' a_k b_k' with row and column sums matching L (Poisson MLE)."""
    K = Lm.shape[0]
    a, b = np.ones(K), np.ones(K)
    rs, cs = Lm.sum(1), Lm.sum(0)
    for _ in range(iters):
        a = np.where(rs > 0, rs / np.maximum((Rm * b[None, :]).sum(1), 1e-12), 0.0)
        b = np.where(cs > 0, cs / np.maximum((Rm * a[:, None]).sum(0), 1e-12), 0.0)
    return Rm * a[:, None] * b[None, :]


def model_survival(m: pl.DataFrame, R: pl.DataFrame, sel: np.ndarray, kind: str, cut_mask: np.ndarray | None = None):
    """Exact S(d) under M1 (rank-1) or M2 (pair Markov); returns N-like array scaled to the in-window count."""
    au = m["author"].to_numpy().astype(int)
    par = m["par"].to_numpy().copy()
    if cut_mask is not None:
        par[cut_mask] = -1
    agents = np.unique(au)
    ix = {a: k for k, a in enumerate(agents)}
    K = len(agents)
    has = par >= 0
    n_k = np.bincount([ix[a] for a in au], minlength=K).astype(float)
    p_k = np.bincount([ix[a] for a in au[has]], minlength=K) / np.maximum(n_k, 1)
    Lm = np.zeros((K, K))
    ch = np.flatnonzero(has)
    np.add.at(Lm, ([ix[a] for a in au[ch]], [ix[a] for a in au[par[ch]]]), 1)
    if kind == "M2":
        Pm = Lm / np.maximum(Lm.sum(1, keepdims=True), 1e-12)
    else:
        Rm = np.zeros((K, K))
        for r in R.iter_rows(named=True):
            if r["reader"] in ix and r["author"] in ix and r["reader"] != r["author"]:
                Rm[ix[r["reader"]], ix[r["author"]]] += r["R"]
        lam = ipf_rank1(Lm, Rm)
        Pm = lam / np.maximum(lam.sum(1, keepdims=True), 1e-12)
    pi = np.bincount([ix[a] for a in au[sel]], minlength=K).astype(float)
    s = np.ones(K)
    N = [pi.sum()]
    for d in range(1, DMAX + 2):
        s = p_k * (Pm @ s)
        N.append(float(pi @ s))
    return np.array(N)


def cut_depth(m: pl.DataFrame, cut: np.ndarray) -> np.ndarray:
    par = m["par"].to_numpy().copy()
    par[cut] = -1
    return depth_pass(par)


def strong_cut_test(m: pl.DataFrame, P: pl.DataFrame, sel: np.ndarray, n_rand: int, rng):
    au = m["author"].to_numpy().astype(int)
    par = m["par"].to_numpy()
    ch = np.flatnonzero(par >= 0)
    strong = set(map(tuple, P.filter(pl.col("strong")).select("reader", "author").to_numpy().tolist()))
    is_s = np.array([(au[c], au[par[c]]) in strong for c in ch], bool)
    n_cut = int(is_s.sum())
    res = {"n_strong_links": n_cut, "strong_link_share": n_cut / max(len(ch), 1)}
    if n_cut == 0:
        return res
    cut = np.zeros(len(par), bool)
    cut[ch[is_s]] = True
    d1 = cut_depth(m, cut)
    s1 = stats_from_counts(surv_counts(d1[sel]))
    res.update({"dh_cut": s1["dh"], "g_rep_cut": s1["g_rep"], "h_tail_cut": s1["h_tail"]})
    pool = ch[~is_s]
    rd = []
    for _ in range(n_rand):
        if len(pool) < n_cut:
            break
        c2 = np.zeros(len(par), bool)
        c2[rng.choice(pool, n_cut, replace=False)] = True
        rd.append(stats_from_counts(surv_counts(cut_depth(m, c2)[sel]))["dh"])
    rd = np.array(rd)
    res["dh_rand_q05"] = float(np.nanpercentile(rd, 5)) if len(rd) else float("nan")
    res["dh_rand_med"] = float(np.nanmedian(rd)) if len(rd) else float("nan")
    res["p_cut_vs_rand"] = float(np.mean(rd <= s1["dh"])) if len(rd) else float("nan")
    res["cut_mask"] = cut
    return res


# ============================================================================================ tail exponent
def tail_fit(depth: np.ndarray, dmin: int = 3) -> dict:
    x = depth[depth >= dmin].astype(float)
    n = len(x)
    if n < 10:
        return {"alpha": np.nan, "vuong_z": np.nan, "n_tail_pl": n}
    alpha = 1 + n / np.sum(np.log(x / (dmin - 0.5)))
    from scipy.special import zeta
    lp = -alpha * np.log(x) - np.log(zeta(alpha, dmin))
    lam = math.log(1 + 1 / max(x.mean() - dmin, 1e-9))     # geometric on {dmin, ...}
    q = math.exp(-lam)
    le = (x - dmin) * math.log(q) + math.log(1 - q)
    dl = lp - le
    z = dl.sum() / (math.sqrt(n) * dl.std()) if dl.std() > 0 else np.nan
    return {"alpha": float(alpha), "vuong_z": float(z), "n_tail_pl": n}


# ============================================================================================ one unit
def unit_stats(m: pl.DataFrame, R: pl.DataFrame, n_days: int, B: int = 500, n_rand: int = 200, seed: int = 0,
               trim: bool = True) -> dict:
    rng = np.random.default_rng(seed)
    depth = m["depth"].to_numpy()
    sel = m["in_win"].to_numpy() if trim else np.ones(m.height, bool)
    N = surv_counts(depth[sel])
    res = {"n_msgs_win": int(sel.sum()), "n_links": int((m["par"] >= 0).sum())}
    res.update(stats_from_counts(N))
    res["hazard"] = hazard_curve(N)
    res["S"] = (N[:16] / max(N[0], 1)).tolist()
    res["max_depth"] = int(depth[sel].max()) if sel.any() else 0
    blocks = block_ids(m, n_days)
    bt = boot_stats(depth, sel, blocks, B, rng)
    for k, v in bt.items():
        res[f"{k}_lo"], res[f"{k}_hi"] = np.nanpercentile(v, [2.5, 97.5]).tolist()
    # KS distance vs geometric at g_rep
    dd = np.minimum(depth[sel], DMAX)
    emp = np.cumsum(np.bincount(dd, minlength=DMAX + 1)) / max(len(dd), 1)
    g = res["g_rep"]
    geo = 1 - g ** (np.arange(DMAX + 1) + 1)
    res["ks"] = float(np.max(np.abs(emp - geo)))
    # model ladder
    for kind in ("M1", "M2"):
        Nm = model_survival(m, R, sel, kind)
        sm = stats_from_counts(Nm)
        res[f"h_tail_{kind}"] = sm["h_tail"]
        res[f"S_{kind}"] = (Nm[:16] / max(Nm[0], 1)).tolist()
    # pairs
    P = pair_table(m, R)
    elig = P.filter(pl.col("R") >= R_MIN)
    res["n_pairs_elig"] = elig.height
    res["n_strong"] = int(P["strong"].sum())
    res["g_pair_max"] = float(elig["g"].max()) if elig.height else float("nan")
    res["g_pair_med"] = float(elig["g"].median()) if elig.height else float("nan")
    sp = P.filter(pl.col("strong"))
    res["strong_pairs"] = [(int(a), int(b), float(g_), int(l_), int(r_)) for a, b, g_, l_, r_ in
                           sp.select("reader", "author", "g", "L", "R").iter_rows()]
    pp = P.filter((pl.col("R") >= R_MIN) & (pl.col("g") > G_STRONG))
    ppset = set(map(tuple, pp.select("reader", "author").to_numpy().tolist()))
    res["n_pingpong"] = sum(1 for (a, b) in ppset if (b, a) in ppset) // 2
    links_strong = sp["L"].sum() if sp.height else 0
    named_strong = sp["L_named"].sum() if sp.height else 0
    oth = P.filter(~pl.col("strong"))
    res["named_share_strong"] = float(named_strong / links_strong) if links_strong else float("nan")
    res["named_share_other"] = float(oth["L_named"].sum() / max(oth["L"].sum(), 1))
    cut = strong_cut_test(m, P, sel, n_rand, rng)
    cm = cut.pop("cut_mask", None)
    res.update(cut)
    if cm is not None:
        d1 = cut_depth(m, cm)
        bt1 = boot_stats(d1, sel, blocks, 300, rng)
        res["dh_cut_lo"], res["dh_cut_hi"] = np.nanpercentile(bt1["dh"], [2.5, 97.5]).tolist()
        res["h_tail_M1_cut"] = stats_from_counts(model_survival(m, R, sel, "M1", cut_mask=cm))["h_tail"]
    res.update(tail_fit(depth[sel]))
    res["_pairs"] = P
    return res


def re_pool(est, se):
    est, se = np.asarray(est, float), np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[ok], se[ok]
    if len(est) == 0:
        return (float("nan"),) * 4
    if len(est) == 1:
        return float(est[0]), float(est[0] - 1.96 * se[0]), float(est[0] + 1.96 * se[0]), 0.0
    w = 1 / se ** 2
    mu = (w * est).sum() / w.sum()
    Q = (w * (est - mu) ** 2).sum()
    tau2 = max(0.0, (Q - (len(est) - 1)) / (w.sum() - (w ** 2).sum() / w.sum()))
    ws = 1 / (se ** 2 + tau2)
    mm = (ws * est).sum() / ws.sum()
    s = math.sqrt(1 / ws.sum())
    return float(mm), float(mm - 1.96 * s), float(mm + 1.96 * s), float(tau2)
