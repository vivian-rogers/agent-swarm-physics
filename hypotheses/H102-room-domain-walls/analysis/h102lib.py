"""H102 estimators: domain axis, wall coordinate s, bimodality D, interior occupancy I, hopper positions,
dose-response on hopping read-outs with a posted-unread placebo, field alignment of the axis. Card Observables O1-O6.

Statement vectors (32-d unit, style-residualized) are day-centered: minus the mean over agents of that day's agent-day
means (unit-specific), which removes the day field.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data/processed/H102-room-domain-walls"
UNITS = ["G35", "G36", "G37", "G38", "G39", "G41", "G42", "G44", "51g"]
SPLIT = ["G35", "G38", "G41", "G44"]          # instruction or work split (card P1)
IDENT = ["G37", "G39", "G42"]                  # identical kickoffs (G36 is the hopper native)
FOCUS, GENERAL, BEST, REST = 15, 0, 2, 3


def load(model="bge_small", variant="style_resid", dedupe=False):
    st = pl.read_parquet(DATA / "statements.parquet")
    X = np.load(DATA / f"x_{variant}_{model}.npy").astype(np.float64)
    if dedupe:
        keep = ~st["self_repeat_both"].fill_null(False).to_numpy()
        st, X = st.filter(pl.Series(keep)), X[keep]
        st = st.with_row_index("row2")
    dom = pl.read_parquet(DATA / "domains.parquet")
    rd = pl.read_parquet(DATA / "reads_day.parquet")
    return st, day_center(st, X), dom, rd


def day_center(st, X):
    Xc = X.copy()
    key = (st["unit"] + "|" + st["pt_date"]).to_numpy()
    ag = st["agent"].to_numpy()
    for k in np.unique(key):
        m = key == k
        means = [X[m & (ag == a)].mean(0) for a in np.unique(ag[m])]
        Xc[m] -= np.mean(means, 0)
    return Xc


def unit_frame(st, dom, unit):
    m = (st["unit"] == unit).to_numpy()
    sub = st.filter(pl.Series(m)).with_columns(pl.Series("ix", np.nonzero(m)[0]))
    d = dom.filter(pl.col("unit") == unit)
    return sub.join(d.select("agent", "home", "role"), on="agent", how="left")


def rooms_of(dom, unit):
    d = dom.filter(pl.col("unit") == unit)
    if unit == "51g":
        return GENERAL, FOCUS
    homes = sorted(set(d["home"].to_list()) & {BEST, REST})
    return (homes[0], homes[1]) if len(homes) == 2 else (None, None)


def agent_halves(sub, Xc, only_home=True):
    """agent -> (home, role, full mean, half1 mean, half2 mean, n_days) using statements in the agent's home room."""
    out = {}
    s = sub.filter(pl.col("room_at") == pl.col("home")) if only_home else sub
    for (a,), g in s.group_by("agent"):
        days = sorted(g["pt_date"].unique().to_list())
        ix = g["ix"].to_numpy(); dd = g["pt_date"].to_numpy()
        h1d, h2d = set(days[0::2]), set(days[1::2])
        i1 = ix[np.isin(dd, list(h1d))]; i2 = ix[np.isin(dd, list(h2d))]
        out[int(a)] = (int(g["home"][0]), g["role"][0], Xc[ix].mean(0),
                       Xc[i1].mean(0) if len(i1) else None, Xc[i2].mean(0) if len(i2) else None, len(days))
    return out


def wall_coords(ah, A, B, roles_core=("stayer", "core"), halves=True, labels=None):
    """Cross-fitted wall coordinate s and projection z for every agent in ah.
    Centroids of A and B from core stayers (leave-one-out). labels: optional relabeled home rooms for stayers."""
    lab = {a: (labels[a] if labels is not None and a in labels else v[0]) for a, v in ah.items()}
    core = [a for a, v in ah.items() if v[1] in roles_core and v[3] is not None and v[4] is not None]
    res = {}
    for a, v in ah.items():
        vals_s, vals_z = [], []
        pairs = [(3, 4), (4, 3)] if halves else [(2, 2)]
        for hc, hp in pairs:
            if v[hp] is None:
                continue
            cA = [ah[b][hc] for b in core if lab[b] == A and b != a and ah[b][hc] is not None]
            cB = [ah[b][hc] for b in core if lab[b] == B and b != a and ah[b][hc] is not None]
            if len(cA) < 1 or len(cB) < 1:
                continue
            cA, cB = np.mean(cA, 0), np.mean(cB, 0)
            u = cB - cA; nu = np.linalg.norm(u)
            if nu == 0:
                continue
            home, other = (cA, cB) if lab[a] == A else (cB, cA)
            vals_s.append((v[hp] - home) @ u / ((other - home) @ u))
            vals_z.append((v[hp] - cA) @ u / nu)
        if vals_s:
            res[a] = (float(np.mean(vals_s)), float(np.mean(vals_z)), lab[a])
    return res


def bimodality(ah, A, B, labels=None):
    wc = wall_coords(ah, A, B, labels=labels)
    st = [a for a in wc if ah[a][1] in ("stayer", "core")]
    zA = np.array([wc[a][1] for a in st if wc[a][2] == A]); zB = np.array([wc[a][1] for a in st if wc[a][2] == B])
    if len(zA) < 2 or len(zB) < 1:
        return None
    dfA, dfB = len(zA) - 1, max(len(zB) - 1, 0)
    pooled = (dfA * zA.var(ddof=1) + (dfB * zB.var(ddof=1) if dfB else 0)) / (dfA + dfB)
    D = (zB.mean() - zA.mean()) / np.sqrt(pooled)
    s_st = np.array([wc[a][0] for a in st])
    I = float(np.mean((s_st >= 0.25) & (s_st <= 0.75)))
    acc = float(np.mean(s_st < 0.5))
    return {"D": float(D), "I_stayers": I, "acc": acc, "n_A": len(zA), "n_B": len(zB), "wc": wc}


def bimodality_test(ah, A, B, n_null=1000, seed=0):
    obs = bimodality(ah, A, B)
    if obs is None:
        return None
    rng = np.random.default_rng(seed)
    st = [a for a, v in ah.items() if v[1] in ("stayer", "core") and v[3] is not None and v[4] is not None]
    labs = np.array([ah[a][0] for a in st])
    nul = []
    for _ in range(n_null):
        lp = dict(zip(st, rng.permutation(labs)))
        r = bimodality(ah, A, B, labels=lp)
        if r is not None:
            nul.append(r["D"])
    nul = np.array(nul)
    obs["D_null_p95"] = float(np.percentile(nul, 95)); obs["D_null_mean"] = float(nul.mean())
    obs["p"] = float((1 + (nul >= obs["D"]).sum()) / (1 + len(nul)))
    return obs


def hopper_positions(sub, Xc, ah, A, B):
    """s(all) and s(home) for hoppers against full-data core centroids; stayers' leave-one-out s distribution."""
    core = [a for a, v in ah.items() if v[1] in ("stayer", "core")]
    cent = {r: [ah[a][2] for a in core if ah[a][0] == r] for r in (A, B)}
    out = {"stayers": {}, "hoppers": {}}
    for a in core:
        h = ah[a][0]; o = B if h == A else A
        ch = np.mean([ah[b][2] for b in core if ah[b][0] == h and b != a], 0)
        co = np.mean(cent[o], 0)
        out["stayers"][a] = float((ah[a][2] - ch) @ (co - ch) / ((co - ch) @ (co - ch)))
    hop = sub.filter(pl.col("role") == "hopper")
    for (k,), g in hop.group_by("agent"):
        h = int(g["home"][0]); o = B if h == A else A
        ch, co = np.mean(cent[h], 0), np.mean(cent[o], 0)
        u = co - ch; den = u @ u
        ix_all = g["ix"].to_numpy(); ix_home = g.filter(pl.col("room_at") == h)["ix"].to_numpy()
        ix_oth = g.filter(pl.col("room_at") == o)["ix"].to_numpy()
        rec = {"n_all": len(ix_all), "n_home": len(ix_home), "n_other": len(ix_oth),
               "s_all": float((Xc[ix_all].mean(0) - ch) @ u / den),
               "s_home": float((Xc[ix_home].mean(0) - ch) @ u / den) if len(ix_home) else None,
               "s_other": float((Xc[ix_oth].mean(0) - ch) @ u / den) if len(ix_oth) else None,
               "days": {}}
        for (d,), gd in g.group_by("pt_date"):
            ih = gd.filter(pl.col("room_at") == h)["ix"].to_numpy()
            rec["days"][d] = {"n_home": len(ih), "n_all": gd.height,
                              "s_home": float((Xc[ih].mean(0) - ch) @ u / den) if len(ih) else None,
                              "s_all": float((Xc[gd["ix"].to_numpy()].mean(0) - ch) @ u / den)}
        out["hoppers"][int(k)] = rec
    s = np.array(list(out["stayers"].values()))
    hs = [a for a in out["stayers"] if ah[a][0] == A]
    sh = np.array([out["stayers"][a] for a in hs])
    out["home_stayers_p95"] = float(np.percentile(sh, 95)) if len(sh) else None
    out["home_stayers_median"] = float(np.median(sh)) if len(sh) else None
    out["stayers_all_p95"] = float(np.percentile(s, 95))
    return out


def dose_response(hp, rd, unit, min_n=3, n_boot=1000, seed=0, lag=False):
    """Hopper-day s(home) on log1p(R_hop) and log1p(U) with hopper fixed effects (WLS by n_home)."""
    rows = []
    r = rd.filter(pl.col("unit") == unit)
    rdd = {(x["agent"], x["pt_date"]): x for x in r.to_dicts()}
    for k, rec in hp["hoppers"].items():
        dl = sorted(rec["days"])
        for i, d in enumerate(dl):
            v = rec["days"][d]
            if v["s_home"] is None or v["n_home"] < min_n:
                continue
            key = (k, dl[i - 1]) if lag else (k, d)
            if lag and i == 0:
                continue
            x = rdd.get(key)
            if x is None:
                continue
            rows.append((k, d, v["s_home"], v["n_home"], np.log1p(x["R_hop"]), np.log1p(x["U"])))
    if len(rows) < 6:
        return {"n": len(rows)}
    k_, d_, y, w, R, U = map(np.array, zip(*rows))

    def fit(ix):
        kk, yy, ww, RR, UU = k_[ix], y[ix], w[ix], R[ix], U[ix]
        # within-hopper demeaning (weighted)
        Xr, Xu, Y = RR.copy(), UU.copy(), yy.copy()
        for a in np.unique(kk):
            m = kk == a
            for arr in (Xr, Xu, Y):
                arr[m] -= np.average(arr[m], weights=ww[m])
        Xm = np.column_stack([Xr, Xu]); W = np.sqrt(ww)
        beta, *_ = np.linalg.lstsq(Xm * W[:, None], Y * W, rcond=None)
        return beta
    b = fit(np.arange(len(y)))
    rng = np.random.default_rng(seed)
    hops = np.unique(k_); days = np.array(sorted(set(d_)))
    bs_h, bs_d = [], []
    for _ in range(n_boot):
        hh = rng.choice(hops, len(hops))
        ix = np.concatenate([np.nonzero(k_ == a)[0] for a in hh])
        if len(np.unique(k_[ix])) >= 1 and len(ix) >= 4:
            try:
                bs_h.append(fit(ix))
            except np.linalg.LinAlgError:
                pass
        dd = rng.choice(days, len(days))
        ix = np.concatenate([np.nonzero(d_ == x)[0] for x in dd])
        try:
            bs_d.append(fit(ix))
        except np.linalg.LinAlgError:
            pass
    bs_h, bs_d = np.array(bs_h), np.array(bs_d)
    ci = lambda a, j: [float(np.nanpercentile(a[:, j], 2.5)), float(np.nanpercentile(a[:, j], 97.5))]  # noqa: E731
    return {"n": len(y), "n_hoppers": int(len(hops)), "kappa_R": float(b[0]), "kappa_U": float(b[1]),
            "kappa_R_ci_hopper": ci(bs_h, 0), "kappa_R_ci_day": ci(bs_d, 0), "kappa_U_ci_day": ci(bs_d, 1),
            "diff_ci_day": [float(np.nanpercentile(bs_d[:, 0] - bs_d[:, 1], 2.5)),
                            float(np.nanpercentile(bs_d[:, 0] - bs_d[:, 1], 97.5))],
            "p_R_day": float(np.mean(bs_d[:, 0] <= 0))}


def field_alignment(ah, A, B, uf, n_null=2000, seed=0):
    core = [a for a, v in ah.items() if v[1] in ("stayer", "core")]
    cA = np.mean([ah[a][2] for a in core if ah[a][0] == A], 0); cB = np.mean([ah[a][2] for a in core if ah[a][0] == B], 0)
    u = cB - cA; u /= np.linalg.norm(u)
    c = float(abs(u @ uf))
    xw = np.array([ah[a][2] - (cA if ah[a][0] == A else cB) for a in core])
    C = np.cov(xw.T) + 1e-9 * np.eye(len(u)); Lc = np.linalg.cholesky(C)
    rng = np.random.default_rng(seed)
    nul = []
    for _ in range(n_null):
        v = Lc @ rng.standard_normal(len(u)); v /= np.linalg.norm(v)
        nul.append(abs(u @ v))
    nul = np.array(nul)
    return {"cos": c, "null_p95": float(np.percentile(nul, 95)), "p": float((1 + (nul >= c).sum()) / (1 + n_null))}
