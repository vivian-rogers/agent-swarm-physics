"""H44 estimators: event panels around resets, window contrasts with agent-day cluster bootstrap, curves, entropy and
switching, relaxation length, thrash classification, reply-rate (susceptibility) and content-pull estimators.

Every function takes frames from scheme/build.py (or synthetic frames with the same columns), so the synthetic validation
runs the exact estimators used on real data.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import h44common as C  # noqa: E402

NCAT = len(C.CATS)
WIN = {"post5": (1, 5), "post10": (1, 10), "late": (11, 20), "far": (-20, -11), "near": (-10, -1)}
N_AGE = 5
THETA_FLOOR = 0.01   # Amendment A2: a pure output dip leaks Theta_c <= ~0.005 at G51 counts (synthetic)


# ------------------------------------------------------------------------------------------------- panels
def panel(calls: pl.DataFrame, events: pl.DataFrame, kmin: int = -20, kmax: int = 20) -> pl.DataFrame:
    """Stack calls at offsets k (k < 0: k calls before the anchor; k > 0: anchor = +1) within the window the event
    allows (pre: n_pre_avail calls of the closed segment / before the pseudo-boundary; post: n_post_avail)."""
    ks = [k for k in range(kmin, kmax + 1) if k != 0]
    ev = events.select("ev_id", "ev_kind", "agent", "pt_date", "seq", "n_pre_avail", "n_post_avail", "period", "unit_id")
    ev = ev.with_columns(pl.lit(ks).alias("k")).explode("k")
    ev = ev.filter(((pl.col("k") < 0) & (-pl.col("k") <= pl.col("n_pre_avail").cast(pl.Int32)))
                   | ((pl.col("k") > 0) & (pl.col("k") <= pl.col("n_post_avail").cast(pl.Int32))))
    ev = ev.with_columns(pl.when(pl.col("k") > 0).then(pl.col("seq") + pl.col("k") - 1)
                         .otherwise(pl.col("seq") + pl.col("k")).cast(pl.Int32).alias("cseq"))
    cc = calls.sort("agent", "pt_date", "seq").select(
        "agent", "pt_date", pl.col("seq").alias("cseq"), "cat", "any_write", "n_work", "n_fail", "in_loop", "h",
        *[c for c in ("h_norm", "in_loop_norm") if c in calls.columns], "talk",
        "k_new", "n_ment", pl.col("cat").shift(1).over("agent", "pt_date").fill_null(-1).alias("pcat"))
    p = ev.join(cc, on=["agent", "pt_date", "cseq"], how="inner")
    return p.with_columns(pl.col("cat").is_in(C.REACQ_IDX).alias("reacq"),
                          (pl.col("agent").cast(pl.Utf8) + "_" + pl.col("pt_date")).alias("cl"))


# ------------------------------------------------------------------------------------------------- bootstrap core
def boot_weights(n_cl: int, B: int, rng) -> np.ndarray:
    """B x n_cl multinomial cluster weights (resampling clusters with replacement)."""
    idx = rng.integers(0, n_cl, size=(B, n_cl))
    W = np.zeros((B, n_cl), np.float32)
    for b in range(B):
        W[b] = np.bincount(idx[b], minlength=n_cl)
    return W


def _ci(x: np.ndarray) -> tuple[float, float]:
    x = x[np.isfinite(x)]
    if len(x) < 10:
        return float("nan"), float("nan")
    return float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))


def _mm_entropy(counts: np.ndarray) -> np.ndarray:
    """Miller-Madow entropy (nats) of count vectors along the last axis."""
    n = counts.sum(-1, keepdims=True)
    p = counts / np.clip(n, 1e-12, None)
    h = -(np.where(p > 0, p * np.log(np.clip(p, 1e-12, None)), 0.0)).sum(-1)
    k = (counts > 0).sum(-1)
    return h + (k - 1) / (2 * np.clip(n[..., 0], 1, None))


def window_stats(p: pl.DataFrame, B: int = 1000, seed: int = 0, windows=("post5", "post10", "late", "far", "near")) -> dict:
    """Ratio-of-sums rates per window + contrasts with cluster bootstrap (cluster = agent-day).
    Returns point estimates and CIs for R, R_nw, W, work, fail, talk, sigma (switching), H (cross-sectional entropy),
    within-event block entropy; contrasts Theta, dR, Omega, d_sigma, d_H, work dip."""
    rng = np.random.default_rng(seed)
    if p.height == 0:
        return {}
    cl_codes, cl = np.unique(p["cl"].to_numpy(), return_inverse=True)
    ncl = len(cl_codes)
    k = p["k"].to_numpy()
    cat = p["cat"].to_numpy().astype(int)
    wr = p["any_write"].to_numpy().astype(float)
    rq = p["reacq"].to_numpy().astype(float)
    wk = p["n_work"].to_numpy().astype(float)
    fl = (p["n_fail"].to_numpy() > 0).astype(float)
    tk = p["talk"].to_numpy().astype(float)
    pc0 = p["pcat"].to_numpy().astype(int) + 1         # 0 = no previous call that day
    ag_codes, ag = np.unique(p["agent"].to_numpy(), return_inverse=True)
    pc = ag * (NCAT + 1) + pc0                          # cell = agent x previous category
    ncell = len(ag_codes) * (NCAT + 1)
    # switching: previous call of the same event on the same side
    ps = p.sort("ev_id", "k").with_columns(pl.col("cat").shift(1).over("ev_id").alias("pcat"),
                                           pl.col("k").shift(1).over("ev_id").alias("pk"))
    sw_ok = ((ps["pk"] == ps["k"] - 1) & (ps["k"] != 1)).fill_null(False).to_numpy()
    sw = (ps["pcat"] != ps["cat"]).fill_null(False).to_numpy().astype(float)
    cl_s = np.unique(ps["cl"].to_numpy(), return_inverse=True)[1]
    k_s = ps["k"].to_numpy()
    W = boot_weights(ncl, B, rng)
    out = {"n_events": int(p["ev_id"].n_unique()), "n_clusters": int(ncl), "windows": {}}
    sums = {}
    for wn in windows:
        lo, hi = WIN[wn]
        m = (k >= lo) & (k <= hi)
        ms = (k_s >= lo) & (k_s <= hi) & sw_ok
        S = {}
        S["n"] = np.bincount(cl[m], minlength=ncl).astype(float)
        S["w"] = np.bincount(cl[m], wr[m], minlength=ncl)
        S["r"] = np.bincount(cl[m], rq[m], minlength=ncl)
        S["nw"] = S["n"] - S["w"]
        S["rnw"] = np.bincount(cl[m], rq[m] * (1 - wr[m]), minlength=ncl)
        S["wk"] = np.bincount(cl[m], wk[m], minlength=ncl)
        S["fl"] = np.bincount(cl[m], fl[m], minlength=ncl)
        S["tk"] = np.bincount(cl[m], tk[m], minlength=ncl)
        S["swn"] = np.bincount(cl_s[ms], minlength=ncl).astype(float)
        S["sw"] = np.bincount(cl_s[ms], sw[ms], minlength=ncl)
        cc = np.zeros((ncl, NCAT))
        np.add.at(cc, (cl[m], cat[m]), 1)
        S["cat"] = cc
        cn = np.zeros((ncl, ncell)); cd = np.zeros((ncl, ncell))
        np.add.at(cn, (cl[m], pc[m]), rq[m] * (1 - wr[m]))
        np.add.at(cd, (cl[m], pc[m]), 1 - wr[m])
        S["cnum"], S["cden"] = cn, cd
        sums[wn] = S
        est = {"n_calls": int(S["n"].sum())}
        for name, num, den in (("R", "r", "n"), ("R_nw", "rnw", "nw"), ("W", "w", "n"), ("work", "wk", "n"),
                               ("fail", "fl", "n"), ("talk", "tk", "n"), ("sigma", "sw", "swn")):
            pt = S[num].sum() / max(S[den].sum(), 1e-12)
            bs = (W @ S[num]) / np.clip(W @ S[den], 1e-12, None)
            est[name] = [float(pt), *_ci(bs)]
        Hb = _mm_entropy(W @ cc)
        est["H"] = [float(_mm_entropy(cc.sum(0))), *_ci(Hb)]
        est["shares"] = (cc.sum(0) / max(cc.sum(), 1)).round(5).tolist()
        out["windows"][wn] = est
    # contrasts (post vs reference)
    def contrast(a, b, num, den, kind="diff"):
        A, Bw = sums[a], sums[b]
        pa = A[num].sum() / max(A[den].sum(), 1e-12)
        pb = Bw[num].sum() / max(Bw[den].sum(), 1e-12)
        ba = (W @ A[num]) / np.clip(W @ A[den], 1e-12, None)
        bb = (W @ Bw[num]) / np.clip(W @ Bw[den], 1e-12, None)
        if kind == "diff":
            return [float(pa - pb), *_ci(ba - bb)]
        return [float(pa / max(pb, 1e-12) - 1), *_ci(ba / np.clip(bb, 1e-12, None) - 1)]

    con = {}
    pairs = [("post5", "far"), ("post10", "far"), ("post5", "near"), ("late", "near"), ("near", "far"), ("post10", "near")]
    for a, b in pairs:
        if a in sums and b in sums and sums[a]["n"].sum() > 0 and sums[b]["n"].sum() > 0:
            tag = f"{a}_vs_{b}"
            con[tag] = {"Theta": contrast(a, b, "rnw", "nw"), "dR": contrast(a, b, "r", "n"),
                        "Omega": contrast(a, b, "w", "n", "ratio"), "work_rel": contrast(a, b, "wk", "n", "ratio"),
                        "d_sigma": contrast(a, b, "sw", "swn"), "d_fail": contrast(a, b, "fl", "n"),
                        "d_talk": contrast(a, b, "tk", "n")}
            ha = _mm_entropy(sums[a]["cat"].sum(0)) - _mm_entropy(sums[b]["cat"].sum(0))
            hb = _mm_entropy(W @ sums[a]["cat"]) - _mm_entropy(W @ sums[b]["cat"])
            con[tag]["d_H"] = [float(ha), *_ci(hb)]
            con[tag]["Theta_c"] = theta_c(sums[a], sums[b], W)
    out["contrasts"] = con
    return out


def theta_c(A: dict, Bw: dict, W: np.ndarray) -> list:
    """Previous-state-conditioned thrash index: sum_c w_c [R_nw(a | c) - R_nw(b | c)] over cells c = agent x category
    of the previous call, w_c = share of the a-window's non-write calls in cell c. Removes the Markov and agent-mix
    spillover that a pure output dip leaks into the raw Theta (synthetic, Amendment A2)."""
    def one(an, ad, bn, bd):
        ok = (ad > 0) & (bd > 0)
        w = np.where(ok, ad, 0)
        w = w / np.clip(w.sum(-1, keepdims=True), 1e-12, None)
        return (w * (np.where(ok, an / np.clip(ad, 1e-12, None), 0) - np.where(ok, bn / np.clip(bd, 1e-12, None), 0))).sum(-1)
    pt = one(A["cnum"].sum(0), A["cden"].sum(0), Bw["cnum"].sum(0), Bw["cden"].sum(0))
    bs = one(W @ A["cnum"], W @ A["cden"], W @ Bw["cnum"], W @ Bw["cden"])
    return [float(pt), *_ci(bs)]


def curves(p: pl.DataFrame, B: int = 300, seed: int = 0, kmin: int = -20, kmax: int = 20) -> dict:
    """Per-offset rates (R, R_nw, W, work, sigma, H) with cluster-bootstrap CIs, and the relaxation length of R(k)."""
    rng = np.random.default_rng(seed)
    cl_codes, cl = np.unique(p["cl"].to_numpy(), return_inverse=True)
    ncl = len(cl_codes)
    ks = [k for k in range(kmin, kmax + 1) if k != 0]
    kk = p["k"].to_numpy()
    cat = p["cat"].to_numpy().astype(int)
    vals = {"R": p["reacq"].to_numpy().astype(float), "W": p["any_write"].to_numpy().astype(float),
            "work": p["n_work"].to_numpy().astype(float), "talk": p["talk"].to_numpy().astype(float),
            "loop": p["in_loop"].to_numpy().astype(float)}
    nw = 1 - vals["W"]
    W = boot_weights(ncl, B, rng)
    res = {"k": ks}
    num = {n: np.zeros((len(ks), ncl)) for n in vals}
    den = np.zeros((len(ks), ncl))
    rnw = np.zeros((len(ks), ncl)); nwd = np.zeros((len(ks), ncl))
    catc = np.zeros((len(ks), ncl, NCAT))
    for i, k in enumerate(ks):
        m = kk == k
        den[i] = np.bincount(cl[m], minlength=ncl)
        for n, v in vals.items():
            num[n][i] = np.bincount(cl[m], v[m], minlength=ncl)
        rnw[i] = np.bincount(cl[m], vals["R"][m] * nw[m], minlength=ncl)
        nwd[i] = np.bincount(cl[m], nw[m], minlength=ncl)
        np.add.at(catc[i], (cl[m], cat[m]), 1)
    for n in vals:
        pt = num[n].sum(1) / np.clip(den.sum(1), 1e-12, None)
        bs = (W @ num[n].T) / np.clip(W @ den.T, 1e-12, None)
        res[n] = {"est": pt.tolist(), "lo": np.percentile(bs, 2.5, 0).tolist(), "hi": np.percentile(bs, 97.5, 0).tolist()}
    pt = rnw.sum(1) / np.clip(nwd.sum(1), 1e-12, None)
    bs = (W @ rnw.T) / np.clip(W @ nwd.T, 1e-12, None)
    res["R_nw"] = {"est": pt.tolist(), "lo": np.percentile(bs, 2.5, 0).tolist(), "hi": np.percentile(bs, 97.5, 0).tolist()}
    H = _mm_entropy(catc.sum(1))
    res["H"] = {"est": H.tolist()}
    res["n"] = den.sum(1).astype(int).tolist()
    res["shares"] = (catc.sum(1) / np.clip(catc.sum(1).sum(1, keepdims=True), 1, None)).round(5).tolist()
    # relaxation length of R(k), k = 1..kmax: R = Rinf + A exp(-(k-1)/l)
    kpos = np.array([k for k in ks if k > 0])
    ipos = np.array([i for i, k in enumerate(ks) if k > 0])
    if len(kpos) >= 8:
        Rk = np.array(res["R"]["est"])[ipos]
        res["ell"] = fit_relax(kpos, Rk)
        bsR = ((W @ num["R"].T) / np.clip(W @ den.T, 1e-12, None))[:, ipos]
        ells = np.array([fit_relax(kpos, r)["ell"] for r in bsR[:200]])
        res["ell"]["lo"], res["ell"]["hi"] = _ci(ells)
        # writes (dip relaxation) and the re-acquisition tail without the first-call spike
        Wk = np.array(res["W"]["est"])[ipos]
        res["ell_W"] = fit_relax(kpos, Wk)
        bsW = ((W @ num["W"].T) / np.clip(W @ den.T, 1e-12, None))[:, ipos]
        res["ell_W"]["lo"], res["ell_W"]["hi"] = _ci(np.array([fit_relax(kpos, r)["ell"] for r in bsW[:200]]))
        m2 = kpos >= 2
        res["ell_R_tail"] = fit_relax(kpos[m2], Rk[m2])
        res["ell_R_tail"]["lo"], res["ell_R_tail"]["hi"] = _ci(np.array([fit_relax(kpos[m2], r[m2])["ell"] for r in bsR[:200]]))
    return res


def fit_relax(k: np.ndarray, y: np.ndarray) -> dict:
    best = None
    for ell in np.exp(np.linspace(np.log(0.3), np.log(60), 80)):
        x = np.exp(-(k - 1) / ell)
        X = np.c_[np.ones_like(x), x]
        coef, *_ = np.linalg.lstsq(X, y, rcond=None)
        sse = ((X @ coef - y) ** 2).sum()
        if best is None or sse < best[0]:
            best = (sse, ell, coef)
    return {"ell": float(best[1]), "Rinf": float(best[2][0]), "A": float(best[2][1])}


def classify(stats: dict, tag: str = "post5_vs_far", tag_out: str = "post10_vs_far") -> str:
    """thrash / dip / busy / none from Theta_c (post5 vs far; previous-state conditioned, Amendment A2) and Omega
    (post10 vs far) CIs."""
    c, d = stats["contrasts"].get(tag), stats["contrasts"].get(tag_out)
    if not c or not d:
        return "n/a"
    th, om = c["Theta_c"], d["Omega"]
    th_pos = th[1] > 0 and th[0] >= THETA_FLOOR
    om_neg = om[2] < 0
    if om_neg and th_pos:
        return "thrash"
    if om_neg:
        return "dip"
    if th_pos:
        return "busy"
    return "none"


# ------------------------------------------------------------------------------------------------- random effects
def dl_pool(est: list[float], lo: list[float], hi: list[float]) -> dict:
    """DerSimonian-Laird random-effects pool from point estimates and 95% CIs (SE = width / 3.92)."""
    e = np.array(est, float); se = (np.array(hi, float) - np.array(lo, float)) / 3.92
    ok = np.isfinite(e) & np.isfinite(se) & (se > 0)
    e, se = e[ok], se[ok]
    if len(e) == 0:
        return {"est": float("nan"), "lo": float("nan"), "hi": float("nan"), "tau": float("nan"), "k": 0}
    w = 1 / se ** 2
    mu = (w * e).sum() / w.sum()
    Q = (w * (e - mu) ** 2).sum()
    tau2 = max(0.0, (Q - (len(e) - 1)) / max(w.sum() - (w ** 2).sum() / w.sum(), 1e-12))
    ws = 1 / (se ** 2 + tau2)
    mus = (ws * e).sum() / ws.sum()
    s = np.sqrt(1 / ws.sum())
    return {"est": float(mus), "lo": float(mus - 1.96 * s), "hi": float(mus + 1.96 * s), "tau": float(np.sqrt(tau2)),
            "k": int(len(e)), "n_pos": int((e > 0).sum())}


# ------------------------------------------------------------------------------------------------- susceptibility
def reply_rates(rp: pl.DataFrame, anchor: str, B: int = 1000, seed: int = 0) -> dict:
    """Reply rate per visible message by read class for talk messages B after a forced/voluntary reset (pos 1..20)
    vs after the pseudo-boundary at pos 21 (pos 21..40 of segments with >= 40 calls), Mantel-Haenszel across
    strata age bin x offset bin (1-5, 6-10, 11-20).
    P4a coupling cut: RR_e(pre_erased : post) / RR_p(pre_ctx : post)  (log DiD < 0 predicted)
    P4b susceptibility: RR(post | erasure : post | pseudo)              (> 1 predicted)
    Also P(B has a parent) erasure vs pseudo at matched offset bins."""
    rng = np.random.default_rng(seed)
    e = rp.filter((pl.col("seg_kind") == anchor) & (pl.col("pos") <= 20)).with_columns(pl.col("pos").alias("kk"))
    q = rp.filter((pl.col("pos") >= 21) & (pl.col("pos") <= 40) & (pl.col("seg_len") >= 40)).with_columns(
        (pl.col("pos") - 20).alias("kk"))
    if e.height < 50 or q.height < 50:
        return {"n_e": e.height, "n_p": q.height}

    def arrays(df, ncol, pcol):
        n = np.stack(df[ncol].to_numpy()).reshape(-1, 3, N_AGE).astype(float)
        par_c = df[pcol].to_numpy().astype(int)
        par_a = df["par_age"].to_numpy().astype(int)
        hit = np.zeros_like(n)
        ok = par_c >= 0
        hit[np.nonzero(ok)[0], par_c[ok], par_a[ok]] = 1
        kb = np.digitize(df["kk"].to_numpy(), [6, 11])  # 0: 1-5, 1: 6-10, 2: 11-20
        cl = (df["agent"].cast(pl.Utf8) + "_" + df["pt_date"]).to_numpy()
        hp = df["has_parent"].to_numpy().astype(float)
        return n, hit, kb, cl, hp

    ne, he, kbe, cle, hpe = arrays(e, "n_e", "par_cls_e")
    nq, hq, kbq, clq, hpq = arrays(q, "n_p", "par_cls_p")
    allcl, inv = np.unique(np.r_[cle, clq], return_inverse=True)
    ie, iq = inv[: len(cle)], inv[len(cle):]
    ncl = len(allcl)
    # per cluster sums: [cluster, offset bin, class, age]
    def agg(n, h, kb, ic):
        N = np.zeros((ncl, 3, 3, N_AGE)); H = np.zeros((ncl, 3, 3, N_AGE))
        np.add.at(N, (ic, kb), n); np.add.at(H, (ic, kb), h)
        return N, H

    Ne, He = agg(ne, he, kbe, ie)
    Nq, Hq = agg(nq, hq, kbq, iq)
    HPe = np.zeros((ncl, 3)); CNe = np.zeros((ncl, 3)); HPq = np.zeros((ncl, 3)); CNq = np.zeros((ncl, 3))
    np.add.at(HPe, (ie, kbe), hpe); np.add.at(CNe, (ie, kbe), 1)
    np.add.at(HPq, (iq, kbq), hpq); np.add.at(CNq, (iq, kbq), 1)

    def mh(a, n1, c, n0):
        """MH rate ratio over strata (last axes flattened): events a over exposure n1 vs c over n0."""
        T = n1 + n0
        with np.errstate(invalid="ignore", divide="ignore"):
            num = np.nansum(np.where(T > 0, a * n0 / T, 0), axis=-1)
            den = np.nansum(np.where(T > 0, c * n1 / T, 0), axis=-1)
        return num / np.clip(den, 1e-12, None)

    def stats(w):
        if w is None:
            ne_, he_, nq_, hq_ = Ne.sum(0), He.sum(0), Nq.sum(0), Hq.sum(0)
            hpe_, cne_, hpq_, cnq_ = HPe.sum(0), CNe.sum(0), HPq.sum(0), CNq.sum(0)
        else:
            ne_, he_ = np.tensordot(w, Ne, 1), np.tensordot(w, He, 1)
            nq_, hq_ = np.tensordot(w, Nq, 1), np.tensordot(w, Hq, 1)
            hpe_, cne_, hpq_, cnq_ = w @ HPe, w @ CNe, w @ HPq, w @ CNq
        f = lambda x: x.reshape(*x.shape[:-3], -1) if x.ndim > 3 else x
        # erasure: class 2 (pre_erased) vs 0 (post); pseudo: class 1 (pre_ctx) vs 0 (post); strata = offset bin x age
        rr_e = mh(he_[..., :, 2, :].reshape(*he_.shape[:-3], -1), ne_[..., :, 2, :].reshape(*ne_.shape[:-3], -1),
                  he_[..., :, 0, :].reshape(*he_.shape[:-3], -1), ne_[..., :, 0, :].reshape(*ne_.shape[:-3], -1))
        rr_p = mh(hq_[..., :, 1, :].reshape(*hq_.shape[:-3], -1), nq_[..., :, 1, :].reshape(*nq_.shape[:-3], -1),
                  hq_[..., :, 0, :].reshape(*hq_.shape[:-3], -1), nq_[..., :, 0, :].reshape(*nq_.shape[:-3], -1))
        rr_post = mh(he_[..., :, 0, :].reshape(*he_.shape[:-3], -1), ne_[..., :, 0, :].reshape(*ne_.shape[:-3], -1),
                     hq_[..., :, 0, :].reshape(*hq_.shape[:-3], -1), nq_[..., :, 0, :].reshape(*nq_.shape[:-3], -1))
        rr_pre = mh(he_[..., :, 2, :].reshape(*he_.shape[:-3], -1), ne_[..., :, 2, :].reshape(*ne_.shape[:-3], -1),
                    hq_[..., :, 2, :].reshape(*hq_.shape[:-3], -1), nq_[..., :, 2, :].reshape(*nq_.shape[:-3], -1))
        p_par = mh(hpe_, cne_, hpq_, cnq_)
        return {"log_did": np.log(rr_e) - np.log(rr_p), "rr_e": rr_e, "rr_p": rr_p, "rr_post": rr_post,
                "rr_pre_erased": rr_pre, "rr_has_parent": p_par}

    pt = stats(None)
    W = boot_weights(ncl, B, rng)
    bs = stats(W)
    out = {"n_e": int(e.height), "n_p": int(q.height), "n_parent_e": int((he.sum((1, 2)) > 0).sum()),
           "n_parent_p": int((hq.sum((1, 2)) > 0).sum()),
           "rate_post_e": float(He.sum((0, 1))[0].sum() / max(Ne.sum((0, 1))[0].sum(), 1)),
           "rate_post_p": float(Hq.sum((0, 1))[0].sum() / max(Nq.sum((0, 1))[0].sum(), 1)),
           "rate_pre_e": float(He.sum((0, 1))[2].sum() / max(Ne.sum((0, 1))[2].sum(), 1)),
           "rate_prectx_p": float(Hq.sum((0, 1))[1].sum() / max(Nq.sum((0, 1))[1].sum(), 1))}
    for k_ in pt:
        out[k_] = [float(pt[k_]), *_ci(np.asarray(bs[k_], float))]
    return out


def pull_did(pp: pl.DataFrame, label: str, model: str = "bge", B: int = 300, seed: int = 0, gap_bin: float = 0.05) -> dict:
    """Content pull (H29 slope) toward post- vs pre-boundary messages across `label` pairs vs within pairs, strata
    agent x log10 gap bin (0.05 decades) x age bin; within pairs reweighted to the crossing pairs' strata.
    Returns a_post, a_pre for crossing and (reweighted) within pairs, D = (a_post - a_pre)_x - (a_post - a_pre)_w,
    and the separate post / pre differences, with agent-day cluster bootstrap."""
    rng = np.random.default_rng(seed)
    d = pp.filter(pl.col("label").is_in([label, "within"]))
    if d.filter(pl.col("label") == label).height < 30:
        return {"n": d.filter(pl.col("label") == label).height}
    gb = np.floor(np.log10(np.maximum(d["gap_s"].to_numpy(), 1.0)) / gap_bin).astype(int)
    stratum = np.array([f"{a}|{g}" for a, g in zip(d["agent"].to_numpy(), gb)])
    isx = (d["label"] == label).to_numpy()
    sx = set(stratum[isx])
    sw = set(stratum[~isx])
    keep = np.array([s in sx and s in sw for s in stratum])
    d = d.filter(pl.Series(keep)); stratum = stratum[keep]; isx = isx[keep]
    if isx.sum() < 30:
        return {"n": int(isx.sum())}
    num = np.stack(d[f"num_{model}"].to_numpy()).reshape(-1, 2, N_AGE).astype(float)
    den = np.stack(d[f"den_{model}"].to_numpy()).reshape(-1, 2, N_AGE).astype(float)
    su, si = np.unique(stratum, return_inverse=True)
    cl_codes, cl = np.unique((d["agent"].cast(pl.Utf8) + "_" + d["pt_date"]).to_numpy(), return_inverse=True)
    ns = len(su)
    # within weights: each within pair in stratum s gets weight nx_s / nw_s
    nx = np.bincount(si[isx], minlength=ns).astype(float)
    nwc = np.bincount(si[~isx], minlength=ns).astype(float)
    wpair = np.where(isx, 1.0, nx[si] / np.clip(nwc[si], 1, None))

    def est(w_cl):
        ww = wpair * (w_cl[cl] if w_cl is not None else 1.0)
        res = {}
        for grp, msk in (("x", isx), ("w", ~isx)):
            N = (num[msk] * ww[msk, None, None]).sum(0)
            D = (den[msk] * ww[msk, None, None]).sum(0)
            res[grp] = (N, D)
        # age-standardize: per age bin slopes, weighted by the crossing pairs' den in that bin (both classes)
        Nx, Dx = res["x"]; Nw, Dw = res["w"]
        wa = Dx.sum(0)
        wa = wa / max(wa.sum(), 1e-12)
        ax = Nx / np.clip(Dx, 1e-12, None)
        aw = Nw / np.clip(Dw, 1e-12, None)
        okb = (Dx > 0).all(0) & (Dw > 0).all(0)
        wa = np.where(okb, wa, 0); wa = wa / max(wa.sum(), 1e-12)
        a = {f"{g}_{c}": float((A[i] * wa).sum()) for g, A in (("x", ax), ("w", aw)) for i, c in enumerate(("post", "pre"))}
        a["D"] = (a["x_post"] - a["x_pre"]) - (a["w_post"] - a["w_pre"])
        a["d_post"] = a["x_post"] - a["w_post"]
        a["d_pre"] = a["x_pre"] - a["w_pre"]
        return a

    pt = est(None)
    W = boot_weights(len(cl_codes), B, rng)
    bs = [est(W[b]) for b in range(B)]
    out = {"n_cross": int(isx.sum()), "n_within": int((~isx).sum()), "n_strata": int((nx > 0).sum())}
    for k_ in pt:
        out[k_] = [pt[k_], *_ci(np.array([b[k_] for b in bs]))]
    return out
