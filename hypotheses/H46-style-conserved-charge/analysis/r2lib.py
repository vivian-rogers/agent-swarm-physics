"""H46 round 2 library: genre/position residualization, function-word vectors, drift-and-reset (OU) estimators.

All estimators take plain arrays so the synthetic validation (r2_synthetic.py) runs the same code as the real run
(r2_run.py). Round-1 code (h46lib) is reused for day tables, class tests, fingerprints and NE41 percentiles.
"""
from __future__ import annotations
import os
for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h46lib as L  # noqa: E402

R2 = L.DATA / "r2"
DQ3 = ["p_plan_coordinate", "p_research_browse", "p_communicate_external", "p_debug_recover", "p_verify_report",
       "p_monitor_wait", "p_self_maintenance", "p_social", "p_meta", "p_idle", "p_addresses_participant", "p_blocked"]
LAB_GROUPS = {"Anthropic": "Anthropic", "OpenAI": "OpenAI", "Google": "Google", "DeepSeek": "DeepSeek"}
CORE = [f for f in L.TC if f not in ("digit_share", "upper_share", "colon")]
N_FW = 50
MIN_TOK = 10


# ----------------------------------------------------------------------------------------------- loading
def load(eligible: bool = True) -> pl.DataFrame:
    m = pl.read_parquet(R2 / "messages_r2.parquet")
    if eligible:
        m = m.filter(~pl.col("self_repeat"))
    ro = pl.read_parquet(L.SH / "roster.parquet").select("agent", "lab")
    m = m.join(ro, on="agent", how="left").with_columns(
        pl.col("lab").replace_strict(LAB_GROUPS, default="other").alias("labg"))
    return m.sort("agent", "pt_date", "t", "msg")


# ----------------------------------------------------------------------------------------------- design blocks
def genre_block(m: pl.DataFrame) -> np.ndarray:
    ok = m["dq3_ok"].fill_null(False).to_numpy()
    cols = [m["is_reply"].to_numpy().astype(float),
            (m["parent_kind"].to_numpy() == 1).astype(float),
            (m["parent_kind"].to_numpy() == 2).astype(float),
            m["p_supports"].to_numpy(), m["p_opposes"].to_numpy(), m["p_asks"].to_numpy(),
            m["p_reply_max"].to_numpy(),
            (m["n_mention"].to_numpy() > 0).astype(float), np.log1p(m["n_mention"].to_numpy().astype(float)),
            m["lead_at"].fill_null(False).to_numpy().astype(float)]
    cols += [np.where(ok, m[c].fill_null(0.0).to_numpy(), 0.0) for c in DQ3]
    cols.append((~ok).astype(float))
    return np.column_stack(cols).astype(np.float64)


def position_block(m: pl.DataFrame) -> np.ndarray:
    mode = m["ctx_mode"].to_numpy()
    cu = (mode == "cu").astype(float)
    chat = (mode == "chat").astype(float)
    cp = np.where(mode == "cu", np.log2(1 + m["ctx_pos"].fill_null(0).to_numpy().astype(float)), 0.0)
    kc = np.where(mode == "cu", np.log2(1 + m["k_ctx"].fill_null(0).to_numpy().astype(float)), 0.0)
    r3 = (m["regime"].to_numpy() == "III")
    k = m["pos_elig"].fill_null(0).to_numpy().astype(float)
    lk = np.where(r3 & (k >= 1), np.log2(np.maximum(k, 1)), 0.0)
    k1 = (r3 & (k == 1)).astype(float)
    return np.column_stack([cu, chat, cp, kc, lk, k1])


def residualize(X: np.ndarray, Z: np.ndarray, agents: np.ndarray, regimes: np.ndarray, fit_mask=None) -> np.ndarray:
    """Within each regime: B from OLS of agent-demeaned X on agent-demeaned Z; remove (Z - mean_regime(Z)) B only."""
    out = X.copy()
    fit_mask = np.ones(len(X), bool) if fit_mask is None else fit_mask
    for r in np.unique(regimes):
        ix = np.where(regimes == r)[0]
        a = agents[ix]
        _, inv = np.unique(a, return_inverse=True)
        cnt = np.bincount(inv).astype(float)

        def dm(M):
            S = np.zeros((inv.max() + 1, M.shape[1]))
            np.add.at(S, inv, M)
            return M - (S / cnt[:, None])[inv]
        Zr = Z[ix]
        keep = Zr.std(0) > 1e-9
        Zr = Zr[:, keep]
        Zd, Xd = dm(Zr), dm(X[ix])
        fm = fit_mask[ix]
        B, *_ = np.linalg.lstsq(Zd[fm], Xd[fm], rcond=None)
        out[ix] = X[ix] - (Zr - Zr.mean(0)) @ B
    return out


def type_control(Y: np.ndarray, m: pl.DataFrame) -> np.ndarray:
    """H46 step 3: within regime, regress on a log-length spline (quartile knots), has_code, has_url; residuals."""
    out = Y.copy()
    lc = m["s_log_chars"].to_numpy().astype(float)
    hc = m["has_code"].to_numpy().astype(float)
    hu = m["has_url"].to_numpy().astype(float)
    rg = m["regime"].to_numpy()
    for r in np.unique(rg):
        ix = np.where(rg == r)[0]
        kn = np.quantile(lc[ix], [0.25, 0.5, 0.75])
        D = np.column_stack([np.ones(len(ix)), lc[ix]] + [np.maximum(lc[ix] - k, 0) for k in kn] + [hc[ix], hu[ix]])
        B, *_ = np.linalg.lstsq(D, Y[ix], rcond=None)
        out[ix] = Y[ix] - D @ B
    return out


def fw_words(m: pl.DataFrame, n: int = N_FW) -> list[str]:
    wc = [c for c in m.columns if c.startswith("w_")]
    tot = m.filter(pl.col("n_tok") >= MIN_TOK).select([pl.col(c).cast(pl.Int64).sum() for c in wc]).row(0)
    order = np.argsort(-np.array(tot))
    return [wc[q] for q in order[:n]]


def fw_matrix(m: pl.DataFrame, words: list[str]) -> np.ndarray:
    """sqrt relative frequency, winsorized 0.1/99.9%, z-scored, type-controlled within regime. Rows with n_tok < MIN_TOK
    are returned too (caller filters)."""
    C = m.select(words).to_numpy().astype(np.float64)
    nt = np.maximum(m["n_tok"].to_numpy().astype(np.float64), 1)
    F = np.sqrt(C / nt[:, None])
    lo, hi = np.quantile(F, 0.001, axis=0), np.quantile(F, 0.999, axis=0)
    F = np.clip(F, lo, hi)
    F = (F - F.mean(0)) / np.where(F.std(0) > 1e-9, F.std(0), 1)
    return type_control(F, m)


def variants(m: pl.DataFrame, words: list[str] | None = None) -> dict:
    """All round-2 per-message matrices aligned with m."""
    ag, rg = m["agent"].to_numpy(), m["regime"].to_numpy()
    tc = L.style_matrix(m, "tc")
    G, P = genre_block(m), position_block(m)
    out = {"tc": tc, "g": residualize(tc, G, ag, rg), "gp": residualize(tc, np.hstack([G, P]), ag, rg),
           "core": tc[:, [L.TC.index(f) for f in CORE]]}
    if words is not None:
        fw = fw_matrix(m, words)
        out["fw"] = fw
        out["fw_g"] = residualize(fw, G, ag, rg)
    return out


def content(m: pl.DataFrame, model: str) -> np.ndarray:
    f = {"bge": "statements_style_resid32_bge_small.npy", "gte": "statements_style_resid32_gte_modernbert.npy"}[model]
    arr = np.load(L.SH / "embeddings" / f, mmap_mode="r")
    X = np.asarray(arr[m["srow"].to_numpy()], dtype=np.float64)
    return X / np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-9)


# ----------------------------------------------------------------------------------------------- NE41
def ne41_pairs(m: pl.DataFrame) -> tuple[pl.DataFrame, np.ndarray, np.ndarray]:
    pr = (pl.read_parquet(L.SH / "style_ne41_pairs.parquet")
          .filter((pl.col("rule") == "time") & (pl.col("dedup") == "self_repeat") & (pl.col("label") != "other")))
    idx = {k: i for i, k in enumerate(m["msg"].to_list())}
    ok = np.array([(a in idx) and (b in idx) for a, b in zip(pr["msg"].to_list(), pr["msg2"].to_list())])
    pr = pr.filter(pl.Series(ok))
    i1 = np.array([idx[k] for k in pr["msg"].to_list()])
    i2 = np.array([idx[k] for k in pr["msg2"].to_list()])
    return pr, i1, i2


def ne41_test(pr: pl.DataFrame, i1, i2, X: np.ndarray, cosine: bool = False, cell=None, n_rand: int = 20000,
              seed: int = 0, scale: bool = True) -> dict:
    """Round-1 gap-matched percentile test. Amendment R2-A5: with scale=True each pair distance is divided by the
    median within-pair distance of its agent x unit before ranking, because most crossing pairs fall back to agent-free
    strata, where agents with noisier vectors bias T upward (synthetic null 0.52 for function words)."""
    lab = pr["label"].to_numpy()
    ag = pr["agent"].to_numpy()
    un = pr["unit2"].to_numpy()
    gap = np.maximum(pr["gap_s"].to_numpy().astype(float), 1.0)
    gb = np.floor(np.log10(gap) / L.GAP_BIN).astype(int)
    if cell is None:
        S1 = np.array([f"{a}|{u}|{g}" for a, u, g in zip(ag, un, gb)])
        S2 = np.array([f"{u}|{g}" for u, g in zip(un, gb)])
    else:
        S1 = np.array([f"{a}|{u}|{g}|{c}" for a, u, g, c in zip(ag, un, gb, cell)])
        S2 = np.array([f"{u}|{g}|{c}" for u, g, c in zip(un, gb, cell)])
    d = (1 - (X[i1] * X[i2]).sum(1)) if cosine else ((X[i1] - X[i2]) ** 2).sum(1)
    if scale:
        key = np.array([f"{a}|{u}" for a, u in zip(ag, un)])
        w = lab == "within"
        med = {}
        for k_ in np.unique(key[w]):
            v_ = np.median(d[w & (key == k_)])
            if v_ > 0:
                med[k_] = v_
        sc = np.array([med.get(k_, np.nan) for k_ in key])
        d = d / sc
        lab = np.where(np.isnan(d), "drop", lab)
        d = np.nan_to_num(d, nan=0.0)
    p, npl = L.pair_percentiles(lab, d, S1, S2)
    out = {}
    for k in ("forced", "voluntary"):
        f = lab == k
        out[k] = L.mean_pct_test(p[f], npl[f], ag[f], n_rand=n_rand, seed=seed)
        out[k]["per_unit"] = {u: {"T": float(np.nanmean(p[f & (un == u)])), "n": int((~np.isnan(p[f & (un == u)])).sum())}
                              for u in np.unique(un[f]) if (~np.isnan(p[f & (un == u)])).sum() >= 30}
    return out


# ----------------------------------------------------------------------------------------------- drift and reset (R2)
CLIP = 3.0   # Amendment R2-A1: per-dimension clip of unit-centred vectors (heavy tails)


def unit_center(X: np.ndarray, m: pl.DataFrame, clip: float | None = CLIP) -> np.ndarray:
    key = (m["agent"].cast(pl.Utf8) + "|" + m["unit2"]).to_numpy()
    _, inv = np.unique(key, return_inverse=True)
    S = np.zeros((inv.max() + 1, X.shape[1]))
    np.add.at(S, inv, X)
    Xc = X - (S / np.bincount(inv)[:, None])[inv]
    return np.clip(Xc, -clip, clip) if clip else Xc


def growth(Xc: np.ndarray, m3: pl.DataFrame, kmax: int = 8):
    """Delta_k = d_k - d_1 within segment (d = squared norm of the unit-centred vector). Returns per-k arrays of
    (delta values, agent ids). m3 must be regime III, eligible, sorted by agent, t; pos_elig = k."""
    d = (Xc ** 2).sum(1)
    seg = (m3["agent"].cast(pl.Int64) * 100000 + m3["seg"].cast(pl.Int64)).to_numpy()
    k = m3["pos_elig"].to_numpy()
    ag = m3["agent"].to_numpy()
    first = {}
    for s_, kk, dd in zip(seg, k, d):
        if kk == 1:
            first[s_] = dd
    res = {}
    for q in range(2, kmax + 1):
        sel = np.where(k == q)[0]
        sel = sel[[seg[i] in first for i in sel]]
        res[q] = (d[sel] - np.array([first[seg[i]] for i in sel]), ag[sel])
    return res


def ou_curve(k, s2, phi):
    k = np.asarray(k, float)
    return s2 * (phi ** 2 - phi ** (2 * k))


def fit_ou(ks, means, w):
    """Weighted LS for (s2, phi) on E[Delta_k] = s2 (phi^2 - phi^(2k)); grid over phi, closed-form s2."""
    best = None
    ks, means, w = np.asarray(ks, float), np.asarray(means, float), np.asarray(w, float)
    for phi in np.concatenate([np.linspace(0.05, 0.99, 189), [0.995, 0.998, 0.999]]):
        f = phi ** 2 - phi ** (2 * ks)
        s2 = (w * f * means).sum() / max((w * f * f).sum(), 1e-12)
        if s2 < 0:
            s2 = 0.0
        sse = (w * (means - s2 * f) ** 2).sum()
        if best is None or sse < best[0]:
            best = (sse, s2, phi)
    _, s2, phi = best
    return {"s2": float(s2), "phi": float(phi), "tau": float(-1 / np.log(phi)) if 0 < phi < 1 else np.inf}


def growth_fit(res: dict, agents_sel=None, n_boot: int = 500, seed: int = 0) -> dict:
    ks = sorted(res)
    def summarize(sample_agents=None, weights=None):
        means, ns = [], []
        for q in ks:
            v, a = res[q]
            if agents_sel is not None:
                keep = np.isin(a, agents_sel)
                v, a = v[keep], a[keep]
            if weights is not None:
                wv = np.array([weights.get(x, 0) for x in a], float)
                means.append((wv * v).sum() / max(wv.sum(), 1e-12))
                ns.append(wv.sum())
            else:
                means.append(v.mean() if len(v) else np.nan)
                ns.append(len(v))
        return np.array(means), np.array(ns, float)
    mu, n = summarize()
    ok = n > 0
    fit = fit_ou(np.array(ks)[ok], mu[ok], n[ok])
    slope = np.polyfit(np.array(ks)[ok], mu[ok], 1, w=np.sqrt(n[ok]))[0] if ok.sum() >= 2 else np.nan
    all_a = np.unique(np.concatenate([res[q][1] for q in ks]))
    if agents_sel is not None:
        all_a = all_a[np.isin(all_a, agents_sel)]
    rng = np.random.default_rng(seed)
    bs = {"s2": [], "phi": [], "tau": [], "slope": [], "means": []}
    for _ in range(n_boot):
        draw = rng.choice(all_a, len(all_a), replace=True)
        wts = {}
        for x in draw:
            wts[x] = wts.get(x, 0) + 1
        mb, nb = summarize(weights=wts)
        okb = nb > 0
        if okb.sum() < 3:
            continue
        f = fit_ou(np.array(ks)[okb], mb[okb], nb[okb])
        bs["s2"].append(f["s2"]); bs["phi"].append(f["phi"]); bs["tau"].append(min(f["tau"], 1e4))
        bs["slope"].append(np.polyfit(np.array(ks)[okb], mb[okb], 1, w=np.sqrt(nb[okb]))[0])
        bs["means"].append(mb)
        bs.setdefault("dbar", []).append((mb[okb] * nb[okb]).sum() / nb[okb].sum())
    q = lambda v: [float(np.quantile(v, 0.025)), float(np.quantile(v, 0.975))]  # noqa: E731
    dbar = float((mu[ok] * n[ok]).sum() / n[ok].sum())
    out = {"k": ks, "mean_delta": mu.tolist(), "n": n.tolist(), "n_agents": int(len(all_a)), **fit,
           "slope": float(slope), "dbar": dbar}
    if bs["s2"]:
        out.update({"s2_ci": q(bs["s2"]), "phi_ci": q(bs["phi"]), "tau_ci": q(bs["tau"]), "slope_ci": q(bs["slope"]), "dbar_ci": q(bs["dbar"]),
                    "mean_delta_ci": [q(np.array(bs["means"])[:, j]) for j in range(len(ks))]})
    return out


def lag_pairs(m3: pl.DataFrame, lmax: int = 4) -> pl.DataFrame:
    """Pairs (j, j+l) of one agent on one PT day by eligible-message order; n_reset kinds between from the segment ids
    (forced = the later message's segment was opened by a forced erasure and exactly one reset lies between)."""
    b = m3.with_row_index("i").select("i", "agent", "pt_date", "t", "seg", "seg_open", "pos_elig")
    out = []
    for l in range(1, lmax + 1):
        p = b.with_columns(*[pl.col(c).shift(-l).over("agent", "pt_date").alias(c + "2")
                             for c in ("i", "t", "seg", "seg_open", "pos_elig")]).filter(pl.col("i2").is_not_null())
        p = p.with_columns(pl.lit(l).alias("lag"), (pl.col("seg2") - pl.col("seg")).alias("nseg"),
                           ((pl.col("t2") - pl.col("t")).dt.total_milliseconds() / 1000.0).alias("gap_s"))
        p = p.with_columns(pl.when(pl.col("nseg") == 0).then(pl.lit("within"))
                           .when((pl.col("nseg") == 1) & (pl.col("seg_open2") == "forced")).then(pl.lit("forced"))
                           .when((pl.col("nseg") == 1) & (pl.col("seg_open2") == "voluntary")).then(pl.lit("voluntary"))
                           .otherwise(pl.lit("other")).alias("label"))
        out.append(p.select("i", "i2", "agent", "lag", "gap_s", "label", "pos_elig", "pos_elig2"))
    return pl.concat(out)


def gap_weights(gap_ref: np.ndarray, gap: np.ndarray, width: float = 0.1) -> np.ndarray:
    """Weights that reweight `gap` to the distribution of `gap_ref` (log10 bins of `width`)."""
    br = np.floor(np.log10(np.maximum(gap_ref, 1)) / width).astype(int)
    bg = np.floor(np.log10(np.maximum(gap, 1)) / width).astype(int)
    w = np.zeros(len(gap))
    cr = {b_: c for b_, c in zip(*np.unique(br, return_counts=True))}
    cg = {b_: c for b_, c in zip(*np.unique(bg, return_counts=True))}
    for b_, c in cg.items():
        if b_ in cr:
            w[bg == b_] = cr[b_] / c
    return w


def cross_products(Xc: np.ndarray, lp: pl.DataFrame, across: str = "forced", n_boot: int = 500, seed: int = 0) -> dict:
    """C_within(l) (reweighted to the across gap distribution of the same lag) and C_across(l); agent-cluster bootstrap."""
    i1, i2 = lp["i"].to_numpy(), lp["i2"].to_numpy()
    c = (Xc[i1] * Xc[i2]).sum(1)
    lab, lag, ag = lp["label"].to_numpy(), lp["lag"].to_numpy(), lp["agent"].to_numpy()
    gap = lp["gap_s"].to_numpy()
    w = np.zeros(len(c))
    for l in np.unique(lag):
        a = (lag == l) & (lab == across)
        wi = (lag == l) & (lab == "within")
        w[wi] = gap_weights(gap[a], gap[wi])
        w[a] = 1.0
    agents = np.unique(ag)

    def stat(wt):
        r = {}
        for l in np.unique(lag):
            wi = (lag == l) & (lab == "within")
            a = (lag == l) & (lab == across)
            cw = (wt[wi] * c[wi]).sum() / max(wt[wi].sum(), 1e-12)
            ca = (wt[a] * c[a]).sum() / max(wt[a].sum(), 1e-12)
            r[int(l)] = (cw, ca, cw - ca)
        return r
    base = stat(w)
    rng = np.random.default_rng(seed)
    bs = {int(l): [] for l in np.unique(lag)}
    for _ in range(n_boot):
        cnt = np.bincount(np.searchsorted(agents, rng.choice(agents, len(agents))), minlength=len(agents))
        wb = w * cnt[np.searchsorted(agents, ag)]
        for l, v in stat(wb).items():
            bs[l].append(v[2])
    out = {"lags": {}}
    for l, (cw, ca, dc) in base.items():
        out["lags"][l] = {"C_within": float(cw), "C_across": float(ca), "dC": float(dc),
                          "dC_ci": [float(np.quantile(bs[l], 0.025)), float(np.quantile(bs[l], 0.975))],
                          "n_within": int(((lag == l) & (lab == "within")).sum()),
                          "n_across": int(((lag == l) & (lab == across)).sum())}
    L_ = sorted(out["lags"])
    dcs = np.array([out["lags"][l]["dC"] for l in L_])
    if (dcs > 0).sum() >= 2:
        pos = dcs > 0
        sl = np.polyfit(np.array(L_)[pos], np.log(dcs[pos]), 1)[0]
        out["phi_C"] = float(np.exp(sl))
        bphi = []
        arr = np.array([bs[l] for l in L_]).T
        for row in arr:
            pz = row > 0
            if pz.sum() >= 2:
                bphi.append(np.exp(np.polyfit(np.array(L_)[pz], np.log(row[pz]), 1)[0]))
        if bphi:
            out["phi_C_ci"] = [float(np.quantile(bphi, 0.025)), float(np.quantile(bphi, 0.975))]
    return out


def pull_obs(m3: pl.DataFrame, nrec: int = 3):
    """Reference sets for the pull coefficient. For each eligible message k (one agent, one PT day):
    within: the previous <= nrec eligible messages of k's own segment (k >= 2);
    forced / voluntary: k among the first 3 messages of a segment opened by that erasure kind, reference = the last
    <= nrec messages of the previous segment on the same day (erased from context).
    Returns rows, refs (padded with -1), labels, gaps (k minus the latest reference, s), n_ref."""
    ag = m3["agent"].to_numpy()
    day = m3["pt_date"].to_numpy()
    seg = m3["seg"].to_numpy()
    op = m3["seg_open"].to_numpy()
    k = m3["pos_elig"].to_numpy()
    tt = m3["t"].dt.epoch("us").to_numpy() / 1e6
    rows, refs, labs, gaps = [], [], [], []
    for i in range(len(m3)):
        within, prev = [], []
        j = i - 1
        while j >= 0 and ag[j] == ag[i] and day[j] == day[i] and (len(within) < nrec or len(prev) < nrec):
            if seg[j] == seg[i] and len(within) < nrec:
                within.append(j)
            elif seg[j] == seg[i] - 1 and len(prev) < nrec:
                prev.append(j)
            elif seg[j] < seg[i] - 1:
                break
            j -= 1
        if within:
            rows.append(i); refs.append(within + [-1] * (nrec - len(within))); labs.append("within")
            gaps.append(tt[i] - tt[within[0]])
        if prev and k[i] <= 3 and op[i] in ("forced", "voluntary"):
            rows.append(i); refs.append(prev + [-1] * (nrec - len(prev))); labs.append(op[i])
            gaps.append(tt[i] - tt[prev[0]])
    refs = np.array(refs)
    return np.array(rows), refs, np.array(labs), np.array(gaps), (refs >= 0).sum(1)


def pull(Xc: np.ndarray, rows, refs, labs, gaps, nref, agents, room_dev=None, n_boot: int = 500, seed: int = 0) -> dict:
    """rho = sum <x_k, rbar> / sum ||rbar||^2 on unit-centred vectors. Within observations are reweighted to the forced
    observations' joint (time-gap bin x n_ref) distribution (rbar noise depends on n_ref)."""
    R = np.where(refs[..., None] >= 0, Xc[np.maximum(refs, 0)], 0.0)
    rbar = R.sum(1) / nref[:, None]
    xk = Xc[rows]
    ag = agents[rows]
    f, wi, vo = labs == "forced", labs == "within", labs == "voluntary"
    gb = np.floor(np.log10(np.maximum(gaps, 1)) / 0.1).astype(int)
    cell = gb * 10 + nref
    w = np.zeros(len(rows))
    cf = dict(zip(*np.unique(cell[f], return_counts=True)))
    cw = dict(zip(*np.unique(cell[wi], return_counts=True)))
    for c_, n_ in cw.items():
        if c_ in cf:
            w[wi & (cell == c_)] = cf[c_] / n_
    w[f] = 1.0
    w[vo] = 1.0
    w_all = np.where(wi, 1.0, w)
    ua = np.unique(ag)

    def rho(sel, wt):
        num = (wt[sel] * (xk[sel] * rbar[sel]).sum(1)).sum()
        den = (wt[sel] * (rbar[sel] ** 2).sum(1)).sum()
        return num / den if den > 0 else np.nan

    def rho2(sel, wt):   # own-recent and room regressors together (normal equations pooled over dimensions)
        Rm = room_dev[sel]
        A = np.array([[(wt[sel] * (rbar[sel] ** 2).sum(1)).sum(), (wt[sel] * (rbar[sel] * Rm).sum(1)).sum()],
                      [(wt[sel] * (rbar[sel] * Rm).sum(1)).sum(), (wt[sel] * (Rm ** 2).sum(1)).sum()]])
        bvec = np.array([(wt[sel] * (xk[sel] * rbar[sel]).sum(1)).sum(), (wt[sel] * (xk[sel] * Rm).sum(1)).sum()])
        try:
            return np.linalg.solve(A, bvec)
        except np.linalg.LinAlgError:
            return np.array([np.nan, np.nan])
    hasr = None if room_dev is None else ((room_dev ** 2).sum(1) > 0)

    def allstats(wt, wta):
        v = {"rho_within_raw": rho(wi, wta), "rho_within": rho(wi, wt), "rho_forced": rho(f, wt),
             "rho_voluntary": rho(vo, wt)}
        if room_dev is not None:
            r2_ = rho2(wi & hasr, wta)
            v["rho_within_room"], v["room_coef"] = r2_[0], r2_[1]
        v["diff"] = v["rho_within"] - v["rho_forced"]
        return v
    base = allstats(w, w_all)
    rng = np.random.default_rng(seed)
    bs = {k_: [] for k_ in base}
    for _ in range(n_boot):
        cnt = np.bincount(np.searchsorted(ua, rng.choice(ua, len(ua))), minlength=len(ua))
        mult = cnt[np.searchsorted(ua, ag)]
        for k_, v_ in allstats(w * mult, w_all * mult).items():
            bs[k_].append(v_)
    out = {k_: float(v_) for k_, v_ in base.items()}
    for k_, v_ in bs.items():
        v_ = np.array(v_, float)
        v_ = v_[np.isfinite(v_)]
        if len(v_):
            out[k_ + "_ci"] = [float(np.quantile(v_, 0.025)), float(np.quantile(v_, 0.975))]
    out["n"] = {k_: int((labs == k_).sum()) for k_ in ("within", "forced", "voluntary")}
    out["within_weight_share"] = float((w[wi] > 0).mean())
    if hasr is not None:
        out["share_with_room"] = float(hasr[wi].mean())
    return out


def room_deviation(Xc: np.ndarray, m3: pl.DataFrame, rows: np.ndarray, window_s: float = 600.0) -> np.ndarray:
    """Mean unit-centred style of other agents' eligible messages in the same room in the window before message k."""
    tt = m3["t"].dt.epoch("us").to_numpy() / 1e6
    room = m3["room"].to_numpy()
    ag = m3["agent"].to_numpy()
    out = np.zeros((len(rows), Xc.shape[1]))
    order = np.argsort(tt, kind="stable")
    ts = tt[order]
    for q, i in enumerate(rows):
        lo = np.searchsorted(ts, tt[i] - window_s, "left")
        hi = np.searchsorted(ts, tt[i], "left")
        cand = order[lo:hi]
        cand = cand[(room[cand] == room[i]) & (ag[cand] != ag[i])]
        if len(cand):
            out[q] = Xc[cand].mean(0)
    return out


def implied_growth(cp: dict, lp: pl.DataFrame, gf: dict) -> dict:
    """Amendment R2-A3: the OU growth implied by the cross-products. s2_C = dC(1) / (phi_C * mean_j(1 - phi_C^(2j)))
    over the earlier message positions j of lag-1 within pairs; predicted dbar = n-weighted mean over k of
    s2_C (phi_C^2 - phi_C^(2k)); ratio = observed dbar / predicted."""
    if "phi_C" not in cp or not (0 < cp["phi_C"] < 1):
        return {"ok": False}
    ph = cp["phi_C"]
    sel = (lp["lag"] == 1) & (lp["label"] == "within")
    j = np.minimum(lp.filter(sel)["pos_elig"].to_numpy().astype(float), 200)
    s2c = cp["lags"][1]["dC"] / (ph * np.mean(1 - ph ** (2 * j)))
    ks, n = np.array(gf["k"], float), np.array(gf["n"], float)
    pred = float((n * s2c * (ph ** 2 - ph ** (2 * ks))).sum() / n.sum())
    return {"ok": True, "s2_C": float(s2c), "dbar_pred": pred, "dbar_obs": gf["dbar"],
            "ratio": float(gf["dbar"] / pred) if pred > 0 else np.nan, "tau_C": float(-1 / np.log(ph))}
