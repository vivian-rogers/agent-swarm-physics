"""H40 replication layer: the call-clock hazard model on every eligible goal period (role: replication).

Per period: eta (exposure-time elasticity at calls n >= 2), eta1 (read-out wait), phi / psi / chi (decay clocks),
gap-specific eta, day-block bootstrap; between-agent slope s of per-call coupling on call rate; model-free per-call
(10 calls) and per-hour (5 min) coupling slopes; tertile collapse in call count vs wall time; held-out call-clock vs
wall-clock log-likelihood; cadence elasticity eps(T); sensitivity to outcome definition and call-start uncertainty.

  uv run python hypotheses/H40-call-clock-coupling/analysis/replication.py --period 38 [--B 200]
  uv run python hypotheses/H40-call-clock-coupling/analysis/replication.py --all
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h40lib as L  # noqa: E402

RES = L.OUT / "results"
MIN_REPLIES_AU = 5
N_GRID = np.array([1, 2, 3, 5, 10, 20])
EPS_T = (300.0, 900.0, 1800.0)


def load_G(goal: int):
    d = L.OUT / f"G{goal:02d}"
    return (pl.read_parquet(d / "items.parquet"), pl.read_parquet(d / "cells.parquet"),
            pl.read_parquet(d / "cadence.parquet"), pl.read_parquet(d / "au.parquet"))


def style_pcs(goal: int) -> pl.DataFrame:
    """Per agent in the period: first two PCs of the mean DQ5 style component (white32 - style_resid_period)."""
    ed = L.SH / "embeddings"
    a = pl.read_parquet(ed / "agent_day.parquet")
    W = np.load(ed / "agent_day_white32_bge_small.npy").astype(np.float32)
    S = np.load(ed / "agent_day_style_resid_period_bge_small.npy").astype(np.float32)
    sel = ((a["goal_no"] == goal) & ~a["holdout"]).to_numpy()
    if sel.sum() < 3:
        return pl.DataFrame({"agent": [], "pc1": [], "pc2": []}, schema={"agent": pl.Int16, "pc1": pl.Float64, "pc2": pl.Float64})
    sub = a.filter(pl.Series(sel))
    st = (W - S)[sel]
    w = sub["n_chat"].to_numpy().astype(float) + 1e-9
    ag = sub["agent"].to_numpy()
    ua = np.unique(ag)
    M = np.stack([(st[ag == u] * w[ag == u, None]).sum(0) / w[ag == u].sum() for u in ua])
    M = M - M.mean(0)
    if len(ua) < 3:
        pcs = np.zeros((len(ua), 2))
    else:
        U, s, Vt = np.linalg.svd(M, full_matrices=False)
        pcs = U[:, :2] * s[:2]
    return pl.DataFrame({"agent": ua.astype(np.int16), "pc1": pcs[:, 0], "pc2": pcs[:, 1] if pcs.shape[1] > 1 else 0.0})


def wls_fe(y, x, unit, w, Z=None):
    """Weighted slope of y on x with unit fixed effects (and optional extra covariates Z), by within-unit demeaning."""
    y, x, w = map(np.asarray, (y, x, w))
    cols = [x] + ([Z[:, j] for j in range(Z.shape[1])] if Z is not None and Z.size else [])
    X = np.column_stack(cols)
    yd, Xd = y.astype(float).copy(), X.astype(float).copy()
    for u in np.unique(unit):
        m = unit == u
        ww = w[m] / w[m].sum()
        yd[m] -= (ww * y[m]).sum()
        Xd[m] -= (ww[:, None] * X[m]).sum(0)
    A = Xd.T @ (Xd * w[:, None])
    try:
        b = np.linalg.solve(A, Xd.T @ (w * yd))
    except np.linalg.LinAlgError:
        return np.nan
    return float(b[0])


def summary_cumsum(calls: L.Calls):
    return np.cumsum(calls.summary.astype(np.int64)), np.cumsum((~calls.summary).astype(np.int64))


def reply_timing(calls: L.Calls, it: pl.DataFrame, tid_col: str = "r_tid", horizon: float = 3600.0):
    """Per item: event/censor in call count and in wall time (60-min window, same day)."""
    S, NS = summary_cumsum(calls)
    c1 = it["c1"].to_numpy()
    t_m = it["t_m"].to_numpy()
    r = it[tid_col].to_numpy()
    de = calls.day_end[c1]
    t_last = calls.t_end[de]
    # censoring time in wall clock and the last call within the window
    cw = np.minimum(t_last, t_m + horizon) - t_m
    lastc = np.minimum(np.searchsorted(calls.key, calls.agent[c1].astype(np.float64) * 1e9 + t_m + horizon, "right") - 1, de)
    lastc = np.maximum(lastc, c1)
    cn = NS[lastc] - NS[c1] + 1
    has = r >= 0
    rr = np.where(has, r, c1)
    n_r = NS[rr] - NS[c1] + 1
    a_r = calls.t[rr] - t_m
    ev = has & (a_r <= horizon) & (rr <= de)
    tn = np.where(ev, n_r, cn).astype(float)
    tw = np.where(ev, a_r, cw)
    # complete follow-up for the fixed horizons (10 calls; 5 min)
    idx10 = np.searchsorted(NS, NS[c1] + 9, side="left")
    full10 = idx10 <= de
    full5 = t_last >= t_m + 300
    return dict(ev=ev, tn=tn, tw=tw, n_r=np.where(ev, n_r, 10 ** 6), a_r=np.where(ev, a_r, 1e12), full10=full10,
                full5=full5)


def km_curve(t: np.ndarray, ev: np.ndarray, grid: np.ndarray) -> np.ndarray:
    """Kaplan-Meier cumulative incidence 1 - S(x) at grid points."""
    o = np.argsort(t, kind="stable")
    t, ev = t[o], ev[o]
    ut, idx = np.unique(t, return_index=True)
    n = len(t)
    at_risk = n - idx
    d = np.add.reduceat(ev.astype(float), idx)
    S = np.cumprod(1 - d / at_risk)
    pos = np.searchsorted(ut, grid, side="right") - 1
    return np.where(pos >= 0, 1 - S[np.clip(pos, 0, None)], 0.0)


def _demean(M, unit, w):
    M = np.asarray(M, dtype=float).copy()
    for u in np.unique(unit):
        m = unit == u
        ww = w[m] / w[m].sum()
        M[m] -= (ww[:, None] * M[m]).sum(0) if M.ndim == 2 else (ww * M[m]).sum()
    return M


def meta_slope(y, se, x, unit, Z=None) -> dict:
    """Random-effects meta-regression of y on x with unit fixed effects (and optional covariates Z):
    y = c_u + s x + Z g + u + e, var(e) = se^2 (known), var(u) = tau^2 (Paule-Mandel). t-based CI."""
    y, se, x = map(lambda v: np.asarray(v, dtype=float), (y, se, x))
    X = np.column_stack([x] + ([Z] if Z is not None and np.size(Z) else []))
    n_units = len(np.unique(unit))
    p = X.shape[1] + n_units
    df = len(y) - p
    if df < 1:
        return dict(s=np.nan, se=np.nan, lo=np.nan, hi=np.nan, tau=np.nan, df=int(df))

    def solve(tau2):
        w = 1 / (se ** 2 + tau2)
        yd, Xd = _demean(y, unit, w), _demean(X, unit, w)
        A = Xd.T @ (Xd * w[:, None])
        b = np.linalg.lstsq(A, Xd.T @ (w * yd), rcond=None)[0]
        r = yd - Xd @ b
        return b, np.linalg.pinv(A), float((w * r ** 2).sum())

    lo_t, hi_t = 0.0, max(10 * np.var(y), 1e-6)
    b, V, Q = solve(0.0)
    tau2 = 0.0
    if Q > df:
        for _ in range(60):
            mid = (lo_t + hi_t) / 2
            _, _, Qm = solve(mid)
            lo_t, hi_t = (mid, hi_t) if Qm > df else (lo_t, mid)
        tau2 = (lo_t + hi_t) / 2
        b, V, Q = solve(tau2)
    from scipy.stats import t as tdist
    s, s_se = float(b[0]), float(np.sqrt(V[0, 0]))
    q = tdist.ppf(0.975, df)
    pval = float(2 * tdist.sf(abs(s / s_se), df)) if s_se > 0 else np.nan
    p_m1 = float(2 * tdist.sf(abs((s + 1) / s_se), df)) if s_se > 0 else np.nan
    return dict(s=s, se=s_se, lo=s - q * s_se, hi=s + q * s_se, tau=float(np.sqrt(tau2)), df=int(df), p0=pval,
                p_m1=p_m1)


def between_agent(fe, fe_se, n_rep_au, r_au, unit_au, labs, pcs, n_perm=1000, seed=L.SEED):
    """Slope s of per-call coupling (FE) on log call rate across agent-units: random-effects meta-regression with unit
    FE (agent heterogeneity tau^2 included), within-unit permutation p-value; controlled version (lab FE + 2 style PCs)."""
    se = fe_se
    ok = (n_rep_au >= MIN_REPLIES_AU) & np.isfinite(fe) & np.isfinite(r_au) & (r_au > 0) & np.isfinite(se) & (se > 0)
    out = dict(n_au=int(ok.sum()))
    if ok.sum() < 4:
        return out | dict(s=np.nan)
    x = np.log(r_au[ok]); y = fe[ok]; u = unit_au[ok]; sv = se[ok]
    m = meta_slope(y, sv, x, u)
    rng = np.random.default_rng(seed)
    w = 1 / (sv ** 2 + m["tau"] ** 2) if np.isfinite(m["tau"]) else 1 / sv ** 2
    perm = []
    for _ in range(n_perm):
        xp = x.copy()
        for uu in np.unique(u):
            mm = np.flatnonzero(u == uu)
            xp[mm] = x[rng.permutation(mm)]
        perm.append(wls_fe(y, xp, u, w))
    perm = np.array(perm)
    out.update(s=m["s"], s_lo=m["lo"], s_hi=m["hi"], s_se=m["se"], tau=m["tau"], df=m["df"], p0=m.get("p0"),
               p_m1=m.get("p_m1"), p_perm=float((np.abs(perm) >= abs(m["s"])).mean()) if np.isfinite(m["s"]) else np.nan,
               hour_slope=1 + m["s"], sd_logr=float(np.std(_demean(x, u, np.ones(len(x))))))
    lab = labs[ok]
    ul = sorted(set(lab))
    Z = [np.array([1.0 if l == v else 0.0 for l in lab]) for v in ul[1:]]
    pc = pcs[ok]
    Zm = np.column_stack(Z + [pc[:, 0], pc[:, 1]])
    dof = ok.sum() - len(np.unique(u)) - 1 - Zm.shape[1]
    out["dof_controlled"] = int(dof)
    if dof >= 6:
        mc = meta_slope(y, sv, x, u, Zm)
        out.update(s_ctrl=mc["s"], s_ctrl_lo=mc["lo"], s_ctrl_hi=mc["hi"], s_ctrl_se=mc["se"], tau_ctrl=mc["tau"])
    return out


def modelfree(calls, it, au_df, r_au, unit_au, B=200, seed=L.SEED):
    """Per agent-unit beta(10 calls) and P(5 min), their slopes on log call rate (unit FE), and the tertile collapse."""
    rt = reply_timing(calls, it)
    aucode = it["au"].to_numpy()
    day = it["day"].to_numpy()
    n_au = len(r_au)
    y10 = (rt["n_r"] <= 10).astype(float)
    y5 = (rt["a_r"] <= 300).astype(float)
    f10, f5 = rt["full10"], rt["full5"]

    def per_au(wd=None):
        ww = np.ones(len(day)) if wd is None else wd[np.searchsorted(ud, day)]
        n10 = np.bincount(aucode, weights=ww * f10, minlength=n_au)
        b10 = np.bincount(aucode, weights=ww * f10 * y10, minlength=n_au) / np.maximum(n10, 1e-9)
        n5 = np.bincount(aucode, weights=ww * f5, minlength=n_au)
        p5 = np.bincount(aucode, weights=ww * f5 * y5, minlength=n_au) / np.maximum(n5, 1e-9)
        return b10, p5, n10, n5

    ud = np.unique(day)
    b10, p5, n10, n5 = per_au()
    ok = (n10 >= 100) & (n5 >= 100) & (b10 > 0) & (p5 > 0) & np.isfinite(r_au) & (r_au > 0)
    res = dict(n_au=int(ok.sum()))
    if ok.sum() >= 4:
        x = np.log(r_au[ok]); u = unit_au[ok]
        # binomial delta-method SEs of the log proportions, agent heterogeneity via the meta-regression
        se10 = np.sqrt((1 - b10[ok]) / (n10[ok] * b10[ok]))
        se5 = np.sqrt((1 - p5[ok]) / (n5[ok] * p5[ok]))
        for k, yy, ss in (("slope_call10", np.log(b10[ok]), se10), ("slope_wall5", np.log(p5[ok]), se5)):
            m = meta_slope(yy, ss, x, u)
            res[k], res[k + "_lo"], res[k + "_hi"], res[k + "_se"], res[k + "_tau"] = m["s"], m["lo"], m["hi"], m["se"], m["tau"]
    res["per_au"] = dict(au=np.flatnonzero(ok).tolist(), b10=b10[ok].tolist(), p5=p5[ok].tolist(),
                         rate=r_au[ok].tolist(), n10=n10[ok].tolist(), n5=n5[ok].tolist())
    # tertile collapse (item-weighted tertiles of call rate)
    rate_item = r_au[aucode]
    good = np.isfinite(rate_item)
    q1, q2 = np.quantile(rate_item[good], [1 / 3, 2 / 3])
    terc = np.where(rate_item <= q1, 0, np.where(rate_item <= q2, 1, 2))
    r_med = float(np.median(rate_item[good]))
    wgrid = N_GRID * 3600.0 / r_med
    Fc = np.array([km_curve(rt["tn"][good & (terc == g)], rt["ev"][good & (terc == g)], N_GRID) for g in range(3)])
    Fw = np.array([km_curve(rt["tw"][good & (terc == g)], rt["ev"][good & (terc == g)], wgrid) for g in range(3)])
    with np.errstate(divide="ignore", invalid="ignore"):
        Dc = float(np.nanmean(np.abs(np.log(Fc[2] / Fc[0]))[Fc.min(0) > 0]))
        Dw = float(np.nanmean(np.abs(np.log(Fw[2] / Fw[0]))[Fw.min(0) > 0]))
        sgn_c = float(np.nanmean(np.log(Fc[2] / Fc[0])[Fc.min(0) > 0]))
        sgn_w = float(np.nanmean(np.log(Fw[2] / Fw[0])[Fw.min(0) > 0]))
    res["collapse"] = dict(D_call=Dc, D_wall=Dw, logratio_call=sgn_c, logratio_wall=sgn_w, grid_calls=N_GRID.tolist(),
                           grid_wall_s=wgrid.tolist(), F_call=Fc.tolist(), F_wall=Fw.tolist(), r_median=r_med,
                           tertile_rates=[float(np.median(rate_item[good & (terc == g)])) for g in range(3)])
    return res


def heldout(cells: pl.DataFrame, n_au: int) -> dict:
    d = cells["day"].to_numpy()
    out = {"call": 0.0, "wall": 0.0, "full": 0.0}
    n_items = 0.0
    for fold in (0, 1):
        tr = cells.filter(pl.Series(d % 2 == fold))
        te = cells.filter(pl.Series(d % 2 != fold))
        # evaluate only agent-units with >= 3 training replies (one-day units have no training data in one fold)
        nrep = np.bincount(tr["au"].to_numpy(), weights=tr["y"].to_numpy(), minlength=n_au)
        te = te.filter(pl.col("au").is_in(np.flatnonzero(nrep >= 3).tolist()))
        if tr.height == 0 or te.height == 0:
            continue
        n_items += float(te.filter(pl.col("nb") == 0)["N"].sum())
        for spec, nm in ((L.SPEC_CALL, "call"), (L.SPEC_WALL, "wall"), (L.SPEC_FULL, "full")):
            f, _ = L.fit_cells(tr, spec, n_au=n_au)
            out[nm] += L.loglik(te, spec, f, n_au)
    return dict(ll_call=out["call"], ll_wall=out["wall"], ll_full=out["full"], n_items_test=n_items,
                dll_call_wall=(out["call"] - out["wall"]) / max(n_items, 1),
                dll_full_call=(out["full"] - out["call"]) / max(n_items, 1))


def cells_for(calls, it, tid_col, sel=None, calls_rows=None):
    """Rebuild cells for another outcome column / item subset / call-time version."""
    cc = calls if calls_rows is None else calls_rows
    sub = it if sel is None else it.filter(sel)
    c1 = sub["c1"].to_numpy(); t_m = sub["t_m"].to_numpy(); rank = sub["rank"].to_numpy().astype(np.int64)
    ment = sub["ment"].to_numpy().astype(np.int64); day = sub["day"].to_numpy(); aucode = sub["au"].to_numpy()
    rt = sub[tid_col].to_numpy()
    parts = []
    for dd in np.unique(day):
        s = np.flatnonzero(day == dd)
        rows = L.expand(cc, c1[s], t_m[s], rank[s])
        rows.item = s[rows.item]
        rows, y = L.truncate(rows, rt)
        parts.append(L.aggregate(rows, y.astype(float), day, aucode, ment, rank))
    return L.merge_cells(parts)


def coef_dict(f: L.Fit, beta=None):
    b = f.beta if beta is None else beta
    return {nm: float(b[i]) for i, nm in enumerate(f.names)}


def run_period(goal: int, B: int = 200, B_eps: int = 100, sens: bool = True, calls: L.Calls | None = None) -> dict:
    t0 = time.time()
    calls = calls or L.load_calls()
    it, cells, cad, au = load_G(goal)
    n_au = int(au["au"].max()) + 1
    rate = au.join(cad.select("agent", "unit_id", "rate", "hours", "lab"), on=["agent", "unit_id"], how="left").sort("au")
    r_au = np.full(n_au, np.nan); r_au[rate["au"].to_numpy()] = rate["rate"].to_numpy()
    unit_au = np.empty(n_au, dtype=object); unit_au[rate["au"].to_numpy()] = rate["unit_id"].to_numpy()
    lab_au = np.empty(n_au, dtype=object); lab_au[rate["au"].to_numpy()] = rate["lab"].fill_null("?").to_numpy()
    agent_au = np.full(n_au, -1); agent_au[rate["au"].to_numpy()] = rate["agent"].to_numpy()
    sp = style_pcs(goal)
    pcm = {a: (p1, p2) for a, p1, p2 in zip(sp["agent"].to_list(), sp["pc1"].to_list(), sp["pc2"].to_list())}
    pcs = np.array([pcm.get(int(a), (0.0, 0.0)) for a in agent_au])
    res = dict(goal=goal, n_items=it.height, n_replies_window=float(cells["y"].sum()), n_cells=cells.height,
               n_days=int(cells["day"].n_unique()), n_au=n_au, regime=None)
    def stage(nm):
        print(f"  [G{goal:02d}] {nm} at {time.time() - t0:.0f}s", flush=True)
    # --- primary fit + bootstrap
    f, full = L.fit_cells(cells, L.SPEC_FULL, n_au=n_au)
    stage("primary fit")
    draws, fe_draws, names = L.day_bootstrap(cells, L.SPEC_FULL, B, L.SEED + goal, start=full, n_au=n_au)
    stage("bootstrap")
    res["coef"] = coef_dict(f)
    res["converged"] = f.converged
    res["boot_ci_pct"] = {nm: [float(np.nanpercentile(draws[:, i], 2.5)), float(np.nanpercentile(draws[:, i], 97.5))]
                          for i, nm in enumerate(names)}
    res["boot_se"] = {nm: float(np.nanstd(draws[:, i])) for i, nm in enumerate(names)}
    res["model_se"] = {nm: f.se(nm) for nm in names}
    # SE used for inference: the larger of the day-bootstrap and model SEs (the day bootstrap is degenerate in periods
    # with few days); Wald 95% CI
    res["se"] = {nm: float(np.nanmax([res["boot_se"][nm], res["model_se"][nm]])) for nm in names}
    res["boot_ci"] = {nm: [res["coef"][nm] - 1.96 * res["se"][nm], res["coef"][nm] + 1.96 * res["se"][nm]] for nm in names}
    # --- gap-specific eta
    fg, _ = L.fit_cells(cells, L.SPEC_GAP, n_au=n_au)
    res["coef_gap"] = coef_dict(fg)
    res["model_se_gap"] = {nm: fg.se(nm) for nm in fg.names}
    gd, _, gnames = L.day_bootstrap(cells, L.SPEC_GAP, max(B // 4, 10 if goal == 51 else 30), L.SEED + 1000 + goal, n_au=n_au)
    stage("gap model")
    res["boot_se_gap"] = {nm: float(np.nanstd(gd[:, i])) for i, nm in enumerate(gnames)}
    res["se_gap"] = {nm: float(np.nanmax([res["boot_se_gap"][nm], res["model_se_gap"].get(nm, np.nan)])) for nm in gnames}
    # gap-specific total eta = eta + interaction, with SE from the bootstrap draws (or model covariance)
    gi = {nm: i for i, nm in enumerate(gnames)}
    tot = {}
    for g in L.GAPS:
        nm = "eta" if g == "busy" else f"eta_x_{g}"
        if nm not in gi:
            continue
        v = gd[:, gi["eta"]] + (gd[:, gi[nm]] if g != "busy" else 0)
        est = res["coef_gap"]["eta"] + (res["coef_gap"][nm] if g != "busy" else 0)
        cov = fg.cov
        if g == "busy":
            mse = fg.se("eta")
        else:
            i1, i2 = fg.names.index("eta"), fg.names.index(nm)
            mse = float(np.sqrt(cov[i1, i1] + cov[i2, i2] + 2 * cov[i1, i2]))
        se_ = float(np.nanmax([np.nanstd(v), mse]))
        tot[g] = dict(est=est, se=se_, lo=est - 1.96 * se_, hi=est + 1.96 * se_)
    if "eta_x_chat" in gi:
        v = gd[:, gi["eta"]] + gd[:, gi["eta_x_chat"]]
        i1, i2 = fg.names.index("eta"), fg.names.index("eta_x_chat")
        mse = float(np.sqrt(fg.cov[i1, i1] + fg.cov[i2, i2] + 2 * fg.cov[i1, i2]))
        est = res["coef_gap"]["eta"] + res["coef_gap"]["eta_x_chat"]
        se_ = float(np.nanmax([np.nanstd(v), mse]))
        tot["chat_busy"] = dict(est=est, se=se_, lo=est - 1.96 * se_, hi=est + 1.96 * se_)
    res["eta_by_gap"] = tot
    # --- between agents (FE SE = larger of bootstrap and model SE)
    n_rep_au = np.bincount(cells["au"].to_numpy(), weights=cells["y"].to_numpy(), minlength=n_au)
    fe_se = np.fmax(np.nanstd(fe_draws, axis=0), f.fe_se)
    res["between"] = between_agent(f.fe, fe_se, n_rep_au, r_au, unit_au, lab_au, pcs, seed=L.SEED + goal)
    res["au_table"] = dict(au=list(range(n_au)), agent=agent_au.tolist(), unit=[str(x) for x in unit_au],
                           lab=[str(x) for x in lab_au], rate=r_au.tolist(), fe=f.fe.tolist(),
                           fe_se=fe_se.tolist(), replies=n_rep_au.tolist(),
                           pc1=pcs[:, 0].tolist(), pc2=pcs[:, 1].tolist())
    # --- model-free per-call vs per-hour, collapse
    res["modelfree"] = modelfree(calls, it, au, r_au, unit_au, B=min(B, 200), seed=L.SEED + goal)
    stage("model-free")
    # --- held-out
    res["heldout"] = heldout(cells, n_au)
    stage("held-out")
    # --- cadence elasticity
    rng = np.random.default_rng(L.SEED + goal)
    sub = np.sort(rng.choice(it.height, size=min(40000, it.height), replace=False))
    rank = it["rank"].to_numpy().astype(np.int64)
    rws = L.expand(calls, it["c1"].to_numpy()[sub], it["t_m"].to_numpy()[sub], rank[sub], horizon=L.H_EPS_S)
    im, ir, ia = it["ment"].to_numpy()[sub], rank[sub], it["au"].to_numpy()[sub]
    eps = {}
    nb = min(B_eps, len(draws))
    if res["n_days"] >= 8:
        cdraws = [coef_dict(f, draws[b]) for b in range(nb)]
        fdraws = [np.nan_to_num(fe_draws[b], nan=-20.0) for b in range(nb)]
    else:   # too few days for a day bootstrap: parametric draws from the model covariance
        prng = np.random.default_rng(L.SEED + 5 + goal)
        md = prng.multivariate_normal(f.beta, f.cov, size=nb)
        cdraws = [coef_dict(f, md[b]) for b in range(nb)]
        fdraws = [f.fe + prng.normal(0, 1, len(f.fe)) * f.fe_se for _ in range(nb)]
    res["eps_draws"] = "day_bootstrap" if res["n_days"] >= 8 else "parametric"
    pt = L.cadence_elasticity_multi(rws, im, ir, ia, coef_dict(f), f.fe, EPS_T, len(sub))
    bsl = [L.cadence_elasticity_multi(rws, im, ir, ia, cdraws[b], fdraws[b], EPS_T, len(sub)) for b in range(nb)]
    for T in EPS_T:
        bs = [x[T] for x in bsl]
        eps[str(int(T))] = dict(est=pt[T], lo=float(np.percentile(bs, 2.5)), hi=float(np.percentile(bs, 97.5)),
                                se=float(np.std(bs)))
    res["eps"] = eps
    stage("elasticity")
    # --- sensitivity
    if sens:
        sn = {}
        for col in ("any_tid", "addr_tid"):
            cs = cells_for(calls, it, col)
            fs, _ = L.fit_cells(cs, L.SPEC_FULL, n_au=n_au)
            sn[col] = dict(eta=fs.get("eta"), se=fs.se("eta"), eta1=fs.get("eta1"), phi=fs.get("phi"),
                           psi=fs.get("psi"), replies=float(cs["y"].sum()))
        cs = cells_for(calls, it, "r_tid", sel=~pl.col("uncertain"))
        fs, _ = L.fit_cells(cs, L.SPEC_FULL, n_au=n_au)
        sn["certain_only"] = dict(eta=fs.get("eta"), se=fs.se("eta"), eta1=fs.get("eta1"), phi=fs.get("phi"),
                                  psi=fs.get("psi"), replies=float(cs["y"].sum()))
        jit = []
        for j in range(2):
            cj = L.with_times(calls, L.jitter_times(calls, np.random.default_rng(L.SEED + 77 * j + goal)))
            cs = cells_for(calls, it, "r_tid", calls_rows=cj)
            fs, _ = L.fit_cells(cs, L.SPEC_FULL, n_au=n_au)
            jit.append(dict(eta=fs.get("eta"), eta1=fs.get("eta1"), phi=fs.get("phi"), psi=fs.get("psi")))
        sn["jitter"] = jit
        res["sensitivity"] = sn
    res["regime"] = str(pl.read_parquet(L.SH / "calendar.parquet").filter(pl.col("goal_no") == goal)["regime"][0])
    res["secs"] = round(time.time() - t0, 1)
    RES.mkdir(parents=True, exist_ok=True)
    L.jdump(res, RES / f"G{goal:02d}.json")
    return res


def short(res: dict) -> str:
    c, ci = res["coef"], res["boot_ci"]
    b = res["between"]
    h = res["heldout"]
    mf = res["modelfree"]
    return (f"G{res['goal']:02d} rep={res['n_replies_window']:.0f} eta={c.get('eta', np.nan):+.2f} "
            f"[{ci.get('eta', [np.nan] * 2)[0]:+.2f},{ci.get('eta', [np.nan] * 2)[1]:+.2f}] "
            f"eta1={c.get('eta1', np.nan):+.2f} phi={c.get('phi', np.nan):+.2f} psi={c.get('psi', np.nan):+.2f} "
            f"chi={c.get('chi', np.nan):+.2f} | s={b.get('s', np.nan):+.2f} [{b.get('s_lo', np.nan):+.2f},"
            f"{b.get('s_hi', np.nan):+.2f}] nau={b.get('n_au')} | mf call={mf.get('slope_call10', np.nan):+.2f} "
            f"wall={mf.get('slope_wall5', np.nan):+.2f} | Dc={mf['collapse']['D_call']:.2f} "
            f"Dw={mf['collapse']['D_wall']:.2f} | dLL={h['dll_call_wall']:+.4f} | eps5={res['eps']['300']['est']:.2f} "
            f"eps30={res['eps']['1800']['est']:.2f} ({res['secs']}s)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", type=int, nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--B", type=int, default=200)
    ap.add_argument("--no-sens", action="store_true")
    ap.add_argument("--skip-existing", action="store_true")
    a = ap.parse_args()
    bs = pl.read_parquet(L.OUT / "build_summary.parquet")
    goals = a.period or bs.filter(pl.col("eligible"))["goal"].to_list()
    calls = L.load_calls()
    for g in goals:
        if a.skip_existing and (RES / f"G{g:02d}.json").exists():
            continue
        B = a.B if g != 51 else min(a.B, 100)
        r = run_period(int(g), B=B, B_eps=min(100, B), sens=not a.no_sens, calls=calls)
        print(short(r), flush=True)


if __name__ == "__main__":
    main()
