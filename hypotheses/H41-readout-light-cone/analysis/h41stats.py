"""H41 statistics on the scheme's tables: violation shares, cone-boundary jump, nulls, velocity, cadence regression.

Used by analysis/synthetic.py, analysis/explore.py and analysis/native.py.
"""
from __future__ import annotations

import numpy as np
import polars as pl

EARLY = 900.0


def _boot_days(days, fn, B=500, seed=0):
    rng = np.random.default_rng(seed)
    u = np.unique(days)
    out = []
    for _ in range(B):
        pick = rng.choice(u, size=len(u), replace=True)
        out.append(fn(pick))
    out = np.array(out, dtype=float)
    out = out[np.isfinite(out)]
    if len(out) < 20:
        return (np.nan, np.nan)
    return (float(np.quantile(out, 0.025)), float(np.quantile(out, 0.975)))


def violation_shares(adf: pl.DataFrame, B: int = 300, seed: int = 0) -> dict:
    """A (best), A_rob (lenient), early versions, V parts, time-shuffled null, room-cone A."""
    if adf.height == 0:
        return {}
    d = adf.with_columns(
        (~pl.col("in_cone")).alias("acaus"),
        (~pl.col("in_cone_len")).alias("acaus_rob"),
        (pl.col("delay") <= EARLY).alias("early"),
        (pl.col("n") < pl.col("h4")).alias("v4"),
        (pl.col("n") < pl.col("h24")).alias("v24"),
        (pl.col("n_hi") < pl.col("h4")).alias("v4_rob"),
        (pl.col("n") < pl.col("h_room")).alias("v_room"),
        (pl.col("h_room").is_infinite()).alias("out_room"),
    )
    days = d["day_use"].to_numpy()
    res = dict(n_adopt=d.height, n_early=int(d["early"].sum()))

    def share(col, mask=None):
        x = d[col].to_numpy().astype(float)
        m = np.ones(len(x), bool) if mask is None else mask
        return float(x[m].mean()) if m.any() else np.nan

    early = d["early"].to_numpy()
    for col in ["acaus", "acaus_rob", "v4", "v24", "v4_rob", "v_room", "out_room"]:
        res[col] = share(col)
        res[col + "_early"] = share(col, early)
    res["p_jit"] = float(d["p_jit"].mean())
    res["p_jit_early"] = float(d.filter(pl.col("early"))["p_jit"].mean()) if early.any() else np.nan
    res["pv_jit"] = float(d["pv_jit"].mean())
    # V parts
    h4 = d["h4"].to_numpy()
    n = d["n"].to_numpy()
    res["v4_h1_n0"] = float(np.mean((h4 == 1) & (n == 0)))
    res["v4_hmid"] = float(np.mean((h4 >= 2) & np.isfinite(h4) & (n < h4)))
    res["v4_hinf"] = float(np.mean(~np.isfinite(h4)))
    res["share_cross"] = float(d["cross"].mean())
    wi = ~d["cross"].to_numpy()
    res["acaus_within"] = share("acaus", wi)
    res["acaus_rob_within"] = share("acaus_rob", wi)
    res["acaus_cross"] = share("acaus", ~wi)
    res["acaus_rob_cross"] = share("acaus_rob", ~wi)
    # bootstrap CIs over days
    ac = d["acaus"].to_numpy().astype(float)
    acr = d["acaus_rob"].to_numpy().astype(float)
    pj = d["p_jit"].to_numpy()
    idx_by_day = {u: np.flatnonzero(days == u) for u in np.unique(days)}

    def agg(pick, x, mask=None):
        ii = np.concatenate([idx_by_day[p] for p in pick])
        if mask is not None:
            ii = ii[mask[ii]]
        return x[ii].mean() if len(ii) else np.nan

    res["acaus_ci"] = _boot_days(days, lambda p: agg(p, ac), B, seed)
    res["acaus_rob_ci"] = _boot_days(days, lambda p: agg(p, acr), B, seed)
    res["acaus_early_ci"] = _boot_days(days, lambda p: agg(p, ac, early), B, seed)
    res["diff_early_ci"] = _boot_days(days, lambda p: agg(p, ac, early) - agg(p, pj, early), B, seed)
    res["diff_all_ci"] = _boot_days(days, lambda p: agg(p, ac) - agg(p, pj), B, seed)
    return res


def hazard_jump(hz: pl.DataFrame, B: int = 500, seed: int = 0) -> dict:
    """h(pre), h(pre_in), h(pre_out), h(o1..o3), J = h(o1)/h(pre), J_room = h(o1)/h(pre_in) with day-bootstrap CIs."""
    if hz.height == 0:
        return {}
    h = hz.with_columns(pl.when(pl.col("group").str.starts_with("pre")).then(pl.lit("pre")).otherwise(pl.col("group")).alias("g2"))
    res = {}
    for g in ["pre_in", "pre_out", "o1", "o2", "o3"]:
        x = h.filter(pl.col("group") == g)
        res[f"risk_{g}"] = int(x["at_risk"].sum())
        res[f"adopt_{g}"] = int(x["adopt"].sum())
        res[f"h_{g}"] = float(x["adopt"].sum() / x["at_risk"].sum()) if x["at_risk"].sum() else np.nan
    pre = h.filter(pl.col("g2") == "pre")
    res["risk_pre"] = int(pre["at_risk"].sum())
    res["adopt_pre"] = int(pre["adopt"].sum())
    res["h_pre"] = float(pre["adopt"].sum() / pre["at_risk"].sum()) if pre["at_risk"].sum() else np.nan
    # within-room (o1 restricted to agents in room0) and cross-room offsets
    for g in ["o1"]:
        for inr in [True, False]:
            x = h.filter((pl.col("group") == g) & (pl.col("in_room0") == inr))
            res[f"h_{g}_{'in' if inr else 'out'}"] = float(x["adopt"].sum() / x["at_risk"].sum()) if x["at_risk"].sum() else np.nan
    x1 = h.filter((pl.col("group") == "o1") & pl.col("in_room0"))
    res["risk_o1_in"], res["adopt_o1_in"] = int(x1["at_risk"].sum()), int(x1["adopt"].sum())
    days = np.sort(h["day"].unique().to_numpy())  # sorted: deterministic bootstrap (round 1b)
    tab = {}
    for (day, g2, grp), sub in h.group_by(["day", "g2", "group"]):
        tab.setdefault(day, {})
        for key in (g2, grp):
            r = tab[day].setdefault(key, [0, 0])
            r[0] += int(sub["at_risk"].sum())
            r[1] += int(sub["adopt"].sum())
    for (day,), sub in h.filter((pl.col("group") == "o1") & pl.col("in_room0")).group_by(["day"]):
        tab.setdefault(day, {})["o1_in"] = [int(sub["at_risk"].sum()), int(sub["adopt"].sum())]

    def ratio(pick, num, den):
        a = np.zeros(2)
        b = np.zeros(2)
        for p in pick:
            a += np.array(tab[p].get(num, [0, 0]))
            b += np.array(tab[p].get(den, [0, 0]))
        if a[0] == 0 or b[0] == 0:
            return np.nan
        hn, hd = (a[1] + 0.5) / (a[0] + 0.5), (b[1] + 0.5) / (b[0] + 0.5)  # Haldane correction
        return hn / hd

    hc = lambda a, n: (a + 0.5) / (n + 0.5)  # Haldane-corrected hazard
    res["J"] = hc(res["adopt_o1"], res["risk_o1"]) / hc(res["adopt_pre"], res["risk_pre"]) if res["risk_pre"] and res["risk_o1"] else np.nan
    res["J_room"] = (hc(res["adopt_o1"], res["risk_o1"]) / hc(res["adopt_pre_in"], res["risk_pre_in"])
                     if res["risk_pre_in"] and res["risk_o1"] else np.nan)
    res["J_in"] = (hc(res["adopt_o1_in"], res["risk_o1_in"]) / hc(res["adopt_pre_in"], res["risk_pre_in"])
                   if res["risk_pre_in"] and res["risk_o1_in"] else np.nan)
    res["J_ci"] = _boot_logratio(days, lambda p: ratio(p, "o1", "pre"), B, seed)
    res["J_in_ci"] = _boot_logratio(days, lambda p: ratio(p, "o1_in", "pre_in"), B, seed)
    res["J_room_ci"] = _boot_logratio(days, lambda p: ratio(p, "o1", "pre_in"), B, seed)
    res["powered"] = bool(res["risk_pre"] >= 100 and res["adopt_o1"] >= 20)
    res["powered_in"] = bool(res["risk_pre_in"] >= 100 and res["adopt_o1_in"] >= 20)
    return res


def mh_rate_ratio(hz: pl.DataFrame, num: str = "o1", den: str = "pre_in", in_room: bool = True) -> float:
    """Mantel-Haenszel ratio of hazards num/den within delay-since-t0 bins (post hoc; recency confound, H29)."""
    x = hz.filter(pl.col("group").is_in([num, den]) & (pl.col("in_room0") == in_room))
    if x.height == 0:
        return np.nan
    t = x.group_by("dbin", "group").agg(pl.col("at_risk").sum(), pl.col("adopt").sum())
    top, bot = 0.0, 0.0
    for (b,), sub in t.group_by(["dbin"]):
        d = {r["group"]: (r["adopt"], r["at_risk"]) for r in sub.iter_rows(named=True)}
        if num not in d or den not in d:
            continue
        a1, n1 = d[num]
        a0, n0 = d[den]
        N = n1 + n0
        top += a1 * n0 / N
        bot += a0 * n1 / N
    if bot == 0:
        return np.inf if top > 0 else np.nan
    return top / bot


def hazard_jump_mh(hz: pl.DataFrame, B: int = 300, seed: int = 0, prefix: str = "", cls=None) -> dict:
    """Delay-matched J_in (MH over delay bins), point and day-bootstrap CI; optional class filter / lenient prefix."""
    h = hz if cls is None else hz.filter(pl.col("cls") == cls)
    if h.height == 0:
        return {}
    num, den = prefix + "o1", prefix + "pre_in"
    pt = mh_rate_ratio(h, num, den)
    days = np.sort(h["day"].unique().to_numpy())  # sorted: deterministic bootstrap (round 1b)
    by = {d: sub for (d,), sub in h.group_by(["day"])}
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(B):
        pick = rng.choice(days, size=len(days), replace=True)
        hh = pl.concat([by[p] for p in pick])
        out.append(mh_rate_ratio(hh, num, den))
    out = np.array(out, float)
    out = out[np.isfinite(out)]
    ci = (float(np.quantile(out, .025)), float(np.quantile(out, .975))) if len(out) >= 20 else (np.nan, np.nan)
    x = h.filter(pl.col("in_room0") & pl.col("group").is_in([num, den]))
    n_den = int(x.filter(pl.col("group") == den)["at_risk"].sum())
    a_den = int(x.filter(pl.col("group") == den)["adopt"].sum())
    return dict(J_mh=pt, J_mh_ci=ci, risk_pre_in=n_den, adopt_pre_in=a_den,
                adopt_o1_in=int(x.filter(pl.col("group") == num)["adopt"].sum()))


def _boot_logratio(days, fn, B, seed):
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(B):
        pick = rng.choice(days, size=len(days), replace=True)
        out.append(fn(pick))
    out = np.array(out, dtype=float)
    out = out[~np.isnan(out)]
    if len(out) < 20:
        return (np.nan, np.nan)
    return (float(np.quantile(out, 0.025)), float(np.quantile(out, 0.975)))


def velocity(adf: pl.DataFrame) -> dict:
    """Cycles per hop (exposed adopters with an agent parent), in receiving calls, talk calls, seconds."""
    e = adf.filter(pl.col("exposed") & pl.col("cyc_hop").is_not_null() & (pl.col("parent") < 64) & (pl.col("parent") >= 0))
    if e.height == 0:
        return {"n_hops": 0}
    cy = e["cyc_hop"].to_numpy().astype(float)
    tk = e["talk_hop"].to_numpy().astype(float)
    ds = e["dt_hop"].to_numpy().astype(float)
    return dict(n_hops=e.height, cyc_med=float(np.median(cy)), cyc_iqr=(float(np.quantile(cy, .25)), float(np.quantile(cy, .75))),
                talk_med=float(np.nanmedian(tk)), talk1_share=float(np.mean(tk == 1)), dt_med=float(np.median(ds)),
                v=float(1.0 / np.median(cy)), v_talk=float(1.0 / np.nanmedian(tk)))


def cadence_regression(adf: pl.DataFrame, B: int = 300, seed: int = 0) -> dict:
    """log dt_hop = b log tau_c + c log V + agent FE (within-agent demeaning); day-cluster bootstrap."""
    e = adf.filter(pl.col("exposed") & pl.col("dt_hop").is_not_null() & (pl.col("dt_hop") > 0)
                   & pl.col("tau_c").is_not_null() & pl.col("tau_c").is_finite() & (pl.col("tau_c") > 0) & (pl.col("vol") > 0))
    if e.height < 50:
        return {"n_reg": e.height}
    y = np.log(e["dt_hop"].to_numpy())
    x1 = np.log(e["tau_c"].to_numpy())
    x2 = np.log(e["vol"].to_numpy())
    ag = e["agent"].to_numpy()
    days = e["day_use"].to_numpy()

    def fit(ii):
        yy, a1, a2, gg = y[ii], x1[ii], x2[ii], ag[ii]
        Xd = np.column_stack([a1, a2])
        # demean within agent
        out_y = yy.copy()
        out_X = Xd.copy()
        for g in np.unique(gg):
            m = gg == g
            out_y[m] -= out_y[m].mean()
            out_X[m] -= out_X[m].mean(axis=0)
        try:
            beta, *_ = np.linalg.lstsq(out_X, out_y, rcond=None)
        except np.linalg.LinAlgError:
            return np.array([np.nan, np.nan])
        return beta

    allii = np.arange(len(y))
    b = fit(allii)
    rng = np.random.default_rng(seed)
    ud = np.unique(days)
    idx = {d: np.flatnonzero(days == d) for d in ud}
    bs = []
    for _ in range(B):
        pick = rng.choice(ud, size=len(ud), replace=True)
        ii = np.concatenate([idx[p] for p in pick])
        bs.append(fit(ii))
    bs = np.array(bs)
    ci = lambda k: (float(np.nanquantile(bs[:, k], 0.025)), float(np.nanquantile(bs[:, k], 0.975)))
    return dict(n_reg=int(len(y)), b=float(b[0]), b_ci=ci(0), c=float(b[1]), c_ci=ci(1),
                med_dt=float(np.median(e["dt_hop"])), med_tau=float(np.median(e["tau_c"])), med_vol=float(np.median(e["vol"])))
