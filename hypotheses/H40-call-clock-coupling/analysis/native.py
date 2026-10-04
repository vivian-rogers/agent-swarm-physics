"""H40 period-native tests (role: native). Each has its own observable and dated prediction (card, "Native tests").

  N1  G51: (a) pause-timer dose at timer-wake read-outs, (b) heavy spins (32 agents; lab / style controls; pair level),
           (c) eta per unit
  N2  NE41: forced consolidation as an exogenous call gap (regime-III non-holdout periods)
  N3  G18: scheduled chat-mode calls (regime I)
  N4  G36: NE14 regime switch inside the period (36a -> 36b/36c, #35 as extra pre-days; exception (c))

  uv run python hypotheses/H40-call-clock-coupling/analysis/native.py --test N1 N2 N3 N4
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h40lib as L  # noqa: E402
import replication as R  # noqa: E402

NAT = L.OUT / "native"
REG3 = [37, 38, 39, 40, 41, 42, 44, 51]


def combo(f: L.Fit, a: str, b: str | None):
    """estimate and model SE of coef a (+ coef b)."""
    if a not in f.names:
        return np.nan, np.nan
    i = f.names.index(a)
    if b is None or b not in f.names:
        return f.get(a), f.se(a)
    j = f.names.index(b)
    v = f.cov[i, i] + f.cov[j, j] + 2 * f.cov[i, j]
    return f.get(a) + f.get(b), float(np.sqrt(max(v, 0)))


def boot_combo(cells, spec, n_au, a, b, B, seed):
    draws, _, names = L.day_bootstrap(cells, spec, B, seed, n_au=n_au)
    if a not in names:
        return np.nan
    v = draws[:, names.index(a)] + (draws[:, names.index(b)] if (b and b in names) else 0)
    return float(np.nanstd(v))


def summarize(est, se_model, se_boot):
    se = float(np.nanmax([se_model, se_boot]))
    return dict(est=float(est), se=se, lo=float(est - 1.96 * se), hi=float(est + 1.96 * se), se_model=float(se_model),
                se_boot=float(se_boot) if np.isfinite(se_boot) else None)


def gap_replies(cells: pl.DataFrame) -> dict:
    g = cells.group_by(["gap", (pl.col("nb") == 0).alias("n1")]).agg(pl.col("y").sum(), pl.col("N").sum())
    return {f"{L.GAPS[r['gap']]}|{'n1' if r['n1'] else 'later'}": (float(r["y"]), float(r["N"])) for r in g.iter_rows(named=True)}


# ----------------------------------------------------------------------------- N1: G51

def n1_pause_dose(calls: L.Calls, B: int = 100) -> dict:
    """Timer-wake read-outs in G51: the read-out call is the wake after a declared pause; W = time the message waited
    (set by a timer declared before it arrived). Sub-model on n = 1 rows at pause wakes:
    cloglog h = alpha_au + eta1p log(W/60) + delta log(1+k) + rank + ment (+ prev-talk). Reduced form: log declared pause."""
    it = pl.read_parquet(L.OUT / "G51/items.parquet")
    c1 = it["c1"].to_numpy()
    wake = calls.gap[c1] == L.GAP_CODE["pause"]
    prev = np.maximum(c1 - 1, 0)
    declared = np.where((calls.agent[prev] == calls.agent[c1]) & (calls.pause_s[prev] > 0), calls.pause_s[prev], np.nan)
    sub = it.filter(pl.Series(wake)).with_columns(pl.Series("declared", declared[wake]))
    y = ((sub["r_tid"] == sub["c1"]).to_numpy()).astype(float)        # reply produced by the wake call itself
    W = np.maximum(sub["W"].to_numpy(), 1.0)
    k = calls.k_new[sub["c1"].to_numpy()].astype(float)
    rank = sub["rank"].to_numpy().astype(float)
    ment = sub["ment"].to_numpy().astype(float)
    au = sub["au"].to_numpy()
    day = sub["day"].to_numpy()
    dec = sub["declared"].to_numpy()
    out = dict(n_items=sub.height, n_replies_at_wake=float(y.sum()), n_wake_calls=int(np.unique(sub["c1"]).size),
               declared_median_s=float(np.nanmedian(dec)), W_median_s=float(np.median(W)))
    n_au = int(au.max()) + 1

    def fit_rows(xcols, w=None):
        # aggregate exact rows into cells: unique on (au, day, binned covariates) is unnecessary at this size; use rows
        X = np.column_stack(xcols)
        import scipy.sparse as sp
        FE = sp.csr_matrix((np.ones(len(au)), (np.arange(len(au)), au)), shape=(len(au), n_au))
        f, _ = L.fit(FE, X, np.zeros(len(au)), y, np.ones(len(au)), w=w)
        return f

    base = [np.log1p(k), np.log(rank), ment]
    f = fit_rows([np.log(W / 60)] + base)
    f.names = ["logW", "logk", "logrank", "ment"]
    okd = np.isfinite(dec)
    rng = np.random.default_rng(L.SEED + 51)
    ud = np.unique(day)
    bs, bs2 = [], []
    for _ in range(B):
        wd = rng.multinomial(len(ud), np.ones(len(ud)) / len(ud)).astype(float)[np.searchsorted(ud, day)]
        bs.append(fit_rows([np.log(W / 60)] + base, w=wd).beta[0])
    out["eta1_pause"] = summarize(f.beta[0], f.se("logW"), float(np.std(bs)))
    out["logk"] = float(f.beta[1])
    # reduced form on the declared duration (items with a parsed declared pause)
    if okd.sum() > 1000:
        yk, auk = y[okd], au[okd]
        import scipy.sparse as sp
        FE = sp.csr_matrix((np.ones(okd.sum()), (np.arange(okd.sum()), auk)), shape=(okd.sum(), n_au))
        Xk = np.column_stack([np.log(dec[okd] / 300), np.log1p(k[okd]), np.log(rank[okd]), ment[okd]])
        fk, _ = L.fit(FE, Xk, np.zeros(okd.sum()), yk, np.ones(okd.sum()))
        fk.names = ["logdeclared", "logk", "logrank", "ment"]
        dk = day[okd]
        udk = np.unique(dk)
        for _ in range(B):
            wd = rng.multinomial(len(udk), np.ones(len(udk)) / len(udk)).astype(float)[np.searchsorted(udk, dk)]
            bs2.append(L.fit(FE, Xk, np.zeros(okd.sum()), yk, np.ones(okd.sum()), w=wd)[0].beta[0])
        out["declared_reduced_form"] = summarize(fk.beta[0], fk.se("logdeclared"), float(np.std(bs2)))
        # descriptive: reply-at-wake rate by declared duration band
        bands = [(0, 90), (90, 240), (240, 360), (360, 1200), (1200, 1e9)]
        out["by_declared"] = [dict(band=f"{a:.0f}-{b:.0f}s", n=int(((dec >= a) & (dec < b)).sum()),
                                   rate=float(y[okd & (dec >= a) & (dec < b)].mean()) if ((dec >= a) & (dec < b)).sum() else None,
                                   mean_k=float(k[okd & (dec >= a) & (dec < b)].mean()) if ((dec >= a) & (dec < b)).sum() else None)
                              for a, b in bands]
    return out


def n1_heavy_spins(calls: L.Calls) -> dict:
    """Between-agent tests in G51 from the replication fit, plus the pair level (sender FE) and the R2 comparison."""
    rj = json.loads((R.RES / "G51.json").read_text())
    out = dict(between=rj["between"], modelfree={k: v for k, v in rj["modelfree"].items() if k.startswith("slope")})
    at = pl.DataFrame(rj["au_table"]).filter(pl.col("replies") >= R.MIN_REPLIES_AU)
    # per-hour coupling (model) = alpha + log r; variance explained by log r vs lab + style (unit-demeaned)
    y_hour = at["fe"].to_numpy() + np.log(at["rate"].to_numpy())
    y_call = at["fe"].to_numpy()
    u = at["unit"].to_numpy()
    w = 1 / (at["fe_se"].to_numpy() ** 2 + rj["between"].get("tau", 0) ** 2)
    x = np.log(at["rate"].to_numpy())
    labs = at["lab"].to_numpy()
    ul = sorted(set(labs))
    Zl = np.column_stack([(labs == v).astype(float) for v in ul[1:]] + [at["pc1"].to_numpy(), at["pc2"].to_numpy()])

    def r2(yv, X):
        yd = R._demean(yv, u, w)
        Xd = R._demean(X, u, w)
        b = np.linalg.lstsq(Xd * np.sqrt(w)[:, None], yd * np.sqrt(w), rcond=None)[0]
        res = yd - Xd @ b
        n, p = len(yd), Xd.shape[1]
        r2v = 1 - (w * res ** 2).sum() / (w * yd ** 2).sum()
        return float(r2v), float(1 - (1 - r2v) * (n - len(np.unique(u))) / max(n - len(np.unique(u)) - p, 1))

    # agent-clustered SE of the agent-unit slope (the same agent appears in up to 12 units), and an agent-level
    # regression on unit-demeaned, agent-averaged quantities (32 points), with and without lab + style controls
    agent = at["agent"].to_numpy()
    xd, yd = R._demean(x, u, w), R._demean(y_call, u, w)
    s_au = float((w * xd * yd).sum() / (w * xd ** 2).sum())
    e = yd - s_au * xd
    ag = np.unique(agent)
    Sg = np.array([(w[agent == g] * xd[agent == g] * e[agent == g]).sum() for g in ag])
    se_cl = float(np.sqrt((Sg ** 2).sum() / ((w * xd ** 2).sum()) ** 2 * len(ag) / (len(ag) - 1)))
    out["s_agent_clustered"] = dict(s=s_au, se=se_cl, lo=s_au - 1.96 * se_cl, hi=s_au + 1.96 * se_cl, n_agents=int(len(ag)))
    A = pl.DataFrame({"agent": agent, "xd": xd, "yd": yd, "w": w, "lab": labs, "pc1": at["pc1"].to_numpy(), "pc2": at["pc2"].to_numpy()})
    A = A.group_by("agent").agg(((pl.col("xd") * pl.col("w")).sum() / pl.col("w").sum()).alias("x"),
                                ((pl.col("yd") * pl.col("w")).sum() / pl.col("w").sum()).alias("y"),
                                pl.col("w").sum(), pl.col("lab").first(), pl.col("pc1").mean(), pl.col("pc2").mean())
    def wls_hc1(yv, X, wv):
        X = np.column_stack([np.ones(len(yv)), X])
        sw = np.sqrt(wv)
        Xw, yw = X * sw[:, None], yv * sw
        XtX_inv = np.linalg.pinv(Xw.T @ Xw)
        b = XtX_inv @ Xw.T @ yw
        r = yw - Xw @ b
        n, k = Xw.shape
        meat = (Xw * r[:, None]).T @ (Xw * r[:, None])
        V = XtX_inv @ meat @ XtX_inv * n / max(n - k, 1)
        se = float(np.sqrt(V[1, 1]))
        return float(b[1]), se
    xa, ya, wa = A["x"].to_numpy(), A["y"].to_numpy(), A["w"].to_numpy()
    s1, se1 = wls_hc1(ya, xa[:, None], np.sqrt(wa))
    la = A["lab"].to_numpy(); ula = sorted(set(la))
    Za = np.column_stack([xa] + [(la == v).astype(float) for v in ula[1:]] + [A["pc1"].to_numpy(), A["pc2"].to_numpy()])
    s2, se2 = wls_hc1(ya, Za, np.sqrt(wa))
    out["s_agent_level"] = dict(s=s1, se=se1, lo=s1 - 1.96 * se1, hi=s1 + 1.96 * se1, s_ctrl=s2, se_ctrl=se2,
                                lo_ctrl=s2 - 1.96 * se2, hi_ctrl=s2 + 1.96 * se2, n_agents=A.height, n_labs=len(ula),
                                weights="sqrt of summed inverse variances (tempered)")
    out["R2_hour"] = dict(cadence=r2(y_hour, x[:, None]), lab_style=r2(y_hour, Zl),
                          both=r2(y_hour, np.column_stack([x, Zl])), n_au=int(len(x)), n_labs=len(ul))
    out["R2_call"] = dict(cadence=r2(y_call, x[:, None]), lab_style=r2(y_call, Zl),
                          both=r2(y_call, np.column_stack([x, Zl])))
    # quintiles of call rate (agent-units, item-weighted from the model-free table)
    pa = rj["modelfree"]["per_au"]
    rate, b10, p5 = map(np.array, (pa["rate"], pa["b10"], pa["p5"]))
    n10 = np.array(pa["n10"])
    q = np.quantile(rate, [0.2, 0.8])
    slow, fast = rate <= q[0], rate >= q[1]
    out["quintiles"] = dict(rate_slow=float(np.average(rate[slow])), rate_fast=float(np.average(rate[fast])),
                            hour_ratio_slow_fast=float(np.average(p5[slow], weights=n10[slow]) / np.average(p5[fast], weights=n10[fast])),
                            call_ratio_slow_fast=float(np.average(b10[slow], weights=n10[slow]) / np.average(b10[fast], weights=n10[fast])),
                            n_slow=int(slow.sum()), n_fast=int(fast.sum()))
    # pair level: per (sender, recipient agent-unit) beta(10 calls) and P(5 min), sender FE in the meta-regression
    it = pl.read_parquet(L.OUT / "G51/items.parquet")
    rt = R.reply_timing(calls, it)
    df = it.select("sender", "au").with_columns(pl.Series("y10", (rt["n_r"] <= 10) & rt["full10"]),
                                               pl.Series("f10", rt["full10"]), pl.Series("y5", (rt["a_r"] <= 300) & rt["full5"]),
                                               pl.Series("f5", rt["full5"]))
    g = (df.group_by(["sender", "au"]).agg(pl.col("y10").sum(), pl.col("f10").sum(), pl.col("y5").sum(), pl.col("f5").sum())
         .filter((pl.col("f10") >= 60) & (pl.col("f5") >= 60) & (pl.col("y10") >= 2) & (pl.col("y5") >= 2)))
    aut = pl.DataFrame(rj["au_table"]).select("au", "rate", "unit")
    g = g.join(aut, on="au", how="left").filter(pl.col("rate").is_finite())
    b = (g["y10"] / g["f10"]).to_numpy(); p = (g["y5"] / g["f5"]).to_numpy()
    se_b = np.sqrt((1 - b) / (g["f10"].to_numpy() * b)); se_p = np.sqrt((1 - p) / (g["f5"].to_numpy() * p))
    snd = g["sender"].to_numpy()
    us = sorted(set(snd))
    Zs = np.column_stack([(snd == v).astype(float) for v in us[1:]])
    xr = np.log(g["rate"].to_numpy())
    uu = g["unit"].to_numpy()
    out["pair_level"] = dict(n_pairs=g.height, call10=R.meta_slope(np.log(b), se_b, xr, uu, Zs),
                             wall5=R.meta_slope(np.log(p), se_p, xr, uu, Zs))
    return out


def n1_per_unit(B: int = 50) -> dict:
    it_c = pl.read_parquet(L.OUT / "G51/cells.parquet")
    it = pl.read_parquet(L.OUT / "G51/items.parquet")
    au = pl.read_parquet(L.OUT / "G51/au.parquet")
    n_au = int(au["au"].max()) + 1
    out = {}
    for u in sorted(au["unit_id"].unique().to_list()):
        aus = au.filter(pl.col("unit_id") == u)["au"].to_list()
        c = it_c.filter(pl.col("au").is_in(aus))
        nd = c["day"].n_unique()
        if nd < 2 or c["y"].sum() < 100:
            out[u] = dict(n_days=int(nd), replies=float(c["y"].sum()), skipped=True)
            continue
        f, full = L.fit_cells(c, L.SPEC_FULL, n_au=n_au)
        dr, _, names = L.day_bootstrap(c, L.SPEC_FULL, B, L.SEED + hash(u) % 1000, start=full, n_au=n_au)
        out[u] = dict(n_days=int(nd), replies=float(c["y"].sum()),
                      eta=summarize(f.get("eta"), f.se("eta"), float(np.nanstd(dr[:, names.index("eta")]))),
                      eta1=summarize(f.get("eta1"), f.se("eta1"), float(np.nanstd(dr[:, names.index("eta1")]))),
                      phi=f.get("phi"), psi=f.get("psi"), chi=f.get("chi"))
    del it
    return out


# ----------------------------------------------------------------------------- N2: NE41

def n2_ne41(calls: L.Calls, B: int = 60) -> dict:
    out = {}
    for g in REG3:
        p = L.OUT / f"G{g:02d}"
        if not (p / "cells.parquet").exists():
            continue
        cells = pl.read_parquet(p / "cells.parquet")
        it = pl.read_parquet(p / "items.parquet")
        n_au = int(pl.read_parquet(p / "au.parquet")["au"].max()) + 1
        gr = gap_replies(cells)
        f, full = L.fit_cells(cells, L.SPEC_GAP, n_au=n_au)
        Bg = B if g != 51 else 30
        draws, _, names = L.day_bootstrap(cells, L.SPEC_GAP, Bg, L.SEED + 4100 + g, start=full, n_au=n_au)

        def bsd(a, b=None):
            if a not in names:
                return np.nan
            v = draws[:, names.index(a)] + (draws[:, names.index(b)] if (b and b in names) else 0)
            return float(np.nanstd(v))
        res = dict(gap_replies=gr)
        e, s = combo(f, "eta", "eta_x_after_forced")
        res["eta_after_forced"] = summarize(e, s, bsd("eta", "eta_x_after_forced"))
        e, s = combo(f, "eta1", "eta1_x_after_forced")
        res["eta1_after_forced"] = summarize(e, s, bsd("eta1", "eta1_x_after_forced"))
        e, s = combo(f, "n1_gap_after_forced", None)
        res["n1_level_after_forced"] = summarize(e, s, bsd("n1_gap_after_forced"))
        e, s = combo(f, "eta1", None)
        res["eta1_busy"] = summarize(e, s, bsd("eta1"))
        # pre-registered ratio: items read out at the call after a forced consolidation, arrived DURING the
        # consolidation (A) vs during the call before it (B); P(reply within 10 calls of read-out)
        c1 = it["c1"].to_numpy()
        tm = it["t_m"].to_numpy()
        af = calls.gap[c1] == L.GAP_CODE["after_forced"]
        # the consolidation call is the latest summary call before c1 (same agent)
        s_idx = c1 - 1
        ok = af & calls.summary[s_idx] & (calls.agent[s_idx] == calls.agent[c1])
        grpA = ok & (tm >= calls.t[s_idx])
        grpB = ok & (tm < calls.t[s_idx])
        rt = R.reply_timing(calls, it)
        y10 = (rt["n_r"] <= 10) & rt["full10"]
        fA, fB = grpA & rt["full10"], grpB & rt["full10"]
        res["ratio_A_B"] = dict(nA=int(fA.sum()), nB=int(fB.sum()), pA=float(y10[fA].mean()) if fA.sum() else None,
                                pB=float(y10[fB].mean()) if fB.sum() else None,
                                ratio=float(y10[fA].mean() / y10[fB].mean()) if fA.sum() and fB.sum() and y10[fB].sum() else None,
                                yA=int(y10[fA].sum()), yB=int(y10[fB].sum()),
                                W_med_A=float(np.median(it["W"].to_numpy()[fA])) if fA.sum() else None,
                                W_med_B=float(np.median(it["W"].to_numpy()[fB])) if fB.sum() else None)
        # consolidation gap length (s) distribution at after_forced calls
        tids = np.flatnonzero((calls.goal == g) & ~calls.holdout & (calls.gap == L.GAP_CODE["after_forced"]))
        gapv = calls.t[tids] - calls.t[np.maximum(tids - 1, 0)]
        res["forced_gap_s"] = dict(n=int(len(tids)), median=float(np.median(gapv)) if len(tids) else None,
                                   q10=float(np.percentile(gapv, 10)) if len(tids) else None,
                                   q90=float(np.percentile(gapv, 90)) if len(tids) else None)
        out[f"G{g:02d}"] = res
        print(g, {k: (v.get("est") if isinstance(v, dict) and "est" in v else None) for k, v in res.items()},
              res["ratio_A_B"], flush=True)
    # random-effects means across periods (exception (d))
    per = {k: v for k, v in out.items() if k.startswith("G")}
    for key in ("eta_after_forced", "eta1_after_forced", "n1_level_after_forced", "eta1_busy"):
        est = np.array([v[key]["est"] for v in per.values()])
        se = np.array([v[key]["se"] for v in per.values()])
        ok = np.isfinite(se) & (se < 2)
        out[f"RE_{key}"] = L.re_mean(est[ok], se[ok])
    # pooled MH-style ratio
    yA = sum(v["ratio_A_B"]["yA"] for v in per.values())
    nA = sum(v["ratio_A_B"]["nA"] for v in per.values())
    yB = sum(v["ratio_A_B"]["yB"] for v in per.values())
    nB = sum(v["ratio_A_B"]["nB"] for v in per.values())
    if yA and yB:
        lr = np.log((yA / nA) / (yB / nB))
        se = np.sqrt(1 / yA - 1 / nA + 1 / yB - 1 / nB)
        out["ratio_A_B_pooled"] = dict(ratio=float(np.exp(lr)), lo=float(np.exp(lr - 1.96 * se)), hi=float(np.exp(lr + 1.96 * se)),
                                       yA=yA, nA=nA, yB=yB, nB=nB)
    return out


# ----------------------------------------------------------------------------- N3: G18 chat mode

def n3_g18(calls: L.Calls, B: int = 100) -> dict:
    p = L.OUT / "G18"
    cells = pl.read_parquet(p / "cells.parquet")
    n_au = int(pl.read_parquet(p / "au.parquet")["au"].max()) + 1
    f, full = L.fit_cells(cells, L.SPEC_GAP, n_au=n_au)
    draws, _, names = L.day_bootstrap(cells, L.SPEC_GAP, B, L.SEED + 1800, start=full, n_au=n_au)

    def bsd(a, b=None):
        if a not in names:
            return np.nan
        v = draws[:, names.index(a)] + (draws[:, names.index(b)] if (b and b in names) else 0)
        return float(np.nanstd(v))
    out = dict(gap_replies=gap_replies(cells))
    cr = cells.group_by("chat", (pl.col("nb") == 0).alias("n1")).agg(pl.col("y").sum(), pl.col("N").sum())
    out["mode_replies"] = {f"{'chat' if r['chat'] else 'cu'}|{'n1' if r['n1'] else 'later'}": (float(r["y"]), float(r["N"]))
                           for r in cr.iter_rows(named=True)}
    e, s = combo(f, "eta", "eta_x_chat")
    out["eta_chat"] = summarize(e, s, bsd("eta", "eta_x_chat"))
    e, s = combo(f, "eta1", "eta1_x_chat")
    out["eta1_chat"] = summarize(e, s, bsd("eta1", "eta1_x_chat"))
    e, s = combo(f, "eta", None)
    out["eta_cu"] = summarize(e, s, bsd("eta"))
    e, s = combo(f, "chat", None)
    out["chat_vs_cu_log_hr"] = summarize(e, s, bsd("chat"))
    # scheduled chat-call cadence (start-to-start), G18 non-holdout
    sel = np.flatnonzero((calls.goal == 18) & ~calls.holdout & calls.chat)
    prev = sel - 1
    okp = (calls.agent[prev] == calls.agent[sel]) & calls.chat[prev] & (calls.day[prev] == calls.day[sel])
    d = calls.t[sel[okp]] - calls.t[prev[okp]]
    out["chat_interval_s"] = dict(n=int(okp.sum()), median=float(np.median(d)), q25=float(np.percentile(d, 25)),
                                  q75=float(np.percentile(d, 75)))
    return out


# ----------------------------------------------------------------------------- N4: G36 / NE14

def n4_ne14(calls: L.Calls) -> dict:
    """Per agent: model-free per-call (10 calls) and per-hour (5 min) coupling and call rate, pre (#35 + 36a, regime II)
    vs post (36b + 36c, regime III). The transition is the object (exception (c))."""
    rows = []
    for g in (35, 36):
        it = pl.read_parquet(L.OUT / f"G{g:02d}/items.parquet")
        rt = R.reply_timing(calls, it)
        side = np.where(it["unit_id"].is_in(["35", "36a"]).to_numpy(), "pre", "post")
        rows.append(pl.DataFrame({"agent": it["recv"].to_numpy(), "side": side, "y10": (rt["n_r"] <= 10) & rt["full10"],
                                  "f10": rt["full10"], "y5": (rt["a_r"] <= 300) & rt["full5"], "f5": rt["full5"],
                                  "W": it["W"].to_numpy()}))
    df = pl.concat(rows)
    a = df.group_by(["agent", "side"]).agg(pl.col("y10").sum(), pl.col("f10").sum(), pl.col("y5").sum(), pl.col("f5").sum(),
                                           pl.col("W").median().alias("W_med"))
    cad = pl.concat([pl.read_parquet(L.OUT / f"G{g:02d}/cadence.parquet") for g in (35, 36)])
    cad = cad.with_columns(pl.when(pl.col("unit_id").is_in(["35", "36a"])).then(pl.lit("pre")).otherwise(pl.lit("post")).alias("side"))
    c = cad.group_by(["agent", "side"]).agg(pl.col("calls").sum(), pl.col("hours").sum(), pl.col("name").first())
    c = c.with_columns((pl.col("calls") / pl.col("hours")).alias("rate"))
    m = a.join(c, on=["agent", "side"], how="inner")
    w = m.pivot(on="side", index=["agent", "name"], values=["y10", "f10", "y5", "f5", "rate", "W_med"])
    w = w.drop_nulls()
    res = []
    for r in w.iter_rows(named=True):
        if min(r["y10_pre"], r["y10_post"], r["y5_pre"], r["y5_post"]) < 3:
            continue
        b_pre, b_post = r["y10_pre"] / r["f10_pre"], r["y10_post"] / r["f10_post"]
        p_pre, p_post = r["y5_pre"] / r["f5_pre"], r["y5_post"] / r["f5_post"]
        res.append(dict(agent=r["agent"], name=r["name"], dlog_rate=float(np.log(r["rate_post"] / r["rate_pre"])),
                        dlog_call=float(np.log(b_post / b_pre)), dlog_hour=float(np.log(p_post / p_pre)),
                        W_pre=r["W_med_pre"], W_post=r["W_med_post"], y10=(r["y10_pre"], r["y10_post"]),
                        y5=(r["y5_pre"], r["y5_post"])))
    out = dict(agents=res)
    if res:
        dr = np.array([x["dlog_rate"] for x in res]); dc = np.array([x["dlog_call"] for x in res]); dh = np.array([x["dlog_hour"] for x in res])
        out.update(median_abs_dlog_call=float(np.median(np.abs(dc))), median_abs_dlog_rate=float(np.median(np.abs(dr))),
                   share_call_smaller=float(np.mean(np.abs(dc) < np.abs(dr))), median_dlog_rate=float(np.median(dr)),
                   median_dlog_call=float(np.median(dc)), median_dlog_hour=float(np.median(dh)),
                   corr_hour_rate=float(np.corrcoef(dh, dr)[0, 1]) if len(res) > 2 else None,
                   corr_call_rate=float(np.corrcoef(dc, dr)[0, 1]) if len(res) > 2 else None, n_agents=len(res))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", nargs="*", default=["N1", "N2", "N3", "N4"])
    a = ap.parse_args()
    calls = L.load_calls()
    NAT.mkdir(parents=True, exist_ok=True)
    if "N1" in a.test:
        res = dict(pause_dose=n1_pause_dose(calls))
        print("N1a", res["pause_dose"]["eta1_pause"], res["pause_dose"].get("declared_reduced_form"), flush=True)
        if (R.RES / "G51.json").exists():
            res["heavy_spins"] = n1_heavy_spins(calls)
            print("N1b", res["heavy_spins"]["R2_hour"], res["heavy_spins"]["quintiles"], flush=True)
        res["per_unit"] = n1_per_unit()
        L.jdump(res, NAT / "N1_G51.json")
    if "N2" in a.test:
        L.jdump(n2_ne41(calls), NAT / "N2_NE41.json")
    if "N3" in a.test:
        r = n3_g18(calls)
        print("N3", r["eta_chat"], r["eta1_chat"], r["chat_interval_s"], flush=True)
        L.jdump(r, NAT / "N3_G18.json")
    if "N4" in a.test:
        r = n4_ne14(calls)
        print("N4", {k: v for k, v in r.items() if k != "agents"}, flush=True)
        L.jdump(r, NAT / "N4_G36.json")


if __name__ == "__main__":
    main()
