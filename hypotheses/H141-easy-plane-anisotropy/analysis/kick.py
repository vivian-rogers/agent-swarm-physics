"""H141 O5 / P4: the sender-specific read kick (H130 Amendment A1 point 2) with the response split into the reader's text
plane E and its complement. Adapted (copied, not imported) from H130's h130lib.dose_design / dose_fit.

Rows = (statement B of reader i, other agent j with a leave-day-out well that day). Responses:
  y_par  = x_B . unit(P_E (h_j - h_i)),   y_perp = x_B . unit((1 - P_E)(h_j - h_i))
Regressors: counts of j's messages that i read at call lag 0 | 1 | 2-3 | 4-7 | 8-15 | 16-1023, j's in-flight messages
(posted in B's room after the producing call started, before B, at most 300 s), and the same counts summed over all
senders (generic reading). Fixed effects per (pair, reader agent-day). Agent-day bootstrap via per-agent-day cross
products. Across-plane decay: beta_perp(lag 1) / beta_perp(lag 0).
"""
from __future__ import annotations

import numpy as np
import polars as pl

import h141lib as L

LAG_EDGES = np.array([0, 1, 2, 4, 8, 16, 1024])
NAMES = ["L0", "L1", "L2_3", "L4_7", "L8_15", "L16_1023", "U"]
D_MAX = 300.0


def day_wells(D: L.Data, min_n: int = L.MIN_WELL) -> dict:
    a = D.st["agent"].to_numpy()
    d = D.st["pt_date"].to_numpy()
    out = {}
    days = np.unique(d)
    for ag in np.unique(a):
        ia = np.flatnonzero(a == ag)
        tot = D.Z[ia].sum(0)
        n = len(ia)
        own = {dd: ia[d[ia] == dd] for dd in np.unique(d[ia])}
        for dd in days:
            idd = own.get(dd, np.array([], int))
            m = n - len(idd)
            if m >= min_n:
                out[(ag, dd)] = (tot - D.Z[idd].sum(0)) / m
    return out


def design(Du: L.Data, rd: pl.DataFrame, W: dict, Pmap: dict):
    """Pmap: plane key -> projector (32 x 32)."""
    st = Du.st
    g = st.filter(pl.Series(Du.ok)).group_by("agent", "pt_date", "plane", maintain_order=True).agg(pl.col("i")).sort(
        "agent", "pt_date", "plane")
    t = st["t"].dt.epoch("us").to_numpy() / 1e6
    tc = st["t_call"].dt.epoch("us").to_numpy() / 1e6
    nn = st["n"].to_numpy()
    room = st["room"].fill_null(-1).to_numpy()
    agent = st["agent"].to_numpy()
    r_reader, r_day, r_n, r_snd = (rd["reader"].to_numpy(), rd["pt_date"].to_numpy(), rd["n"].to_numpy(),
                                   rd["sender"].to_numpy())
    rg = {}
    for k, key in enumerate(zip(r_reader, r_day)):
        rg.setdefault(key, []).append(k)
    order = np.argsort(t, kind="stable")
    room_t = {r: order[room[order] == r] for r in np.unique(room)}
    ag_all = np.unique(agent)
    aidx = {a: k for k, a in enumerate(ag_all)}
    nA = len(ag_all)
    ncol = len(NAMES)
    Y1, Y2, Rs, pairs, ads, bids = [], [], [], [], [], []
    for row, (ag, day, pk, idx) in enumerate(g.iter_rows()):
        hi = W.get((ag, day))
        if hi is None:
            continue
        idx = np.asarray(idx)
        js = [j for j in ag_all if j != ag and (j, day) in W]
        if not js:
            continue
        Pi = Pmap[pk]
        Dd = np.array([W[(j, day)] - hi for j in js])
        Dpar = Dd @ Pi
        Dperp = Dd - Dpar
        Dpar /= np.maximum(np.linalg.norm(Dpar, axis=1, keepdims=True), 1e-12)
        Dperp /= np.maximum(np.linalg.norm(Dperp, axis=1, keepdims=True), 1e-12)
        Xb = Du.X[idx]
        y1 = (Xb @ Dpar.T).ravel()
        y2 = (Xb @ Dperp.T).ravel()
        jpos = {j: k for k, j in enumerate(js)}
        nJ = len(js)
        R = np.zeros((len(idx), nJ, ncol))
        rr = np.asarray(rg.get((ag, day), []), int)
        if len(rr):
            rr = rr[np.array([s in jpos for s in r_snd[rr]], bool)]
        if len(rr):
            jj = np.array([jpos[s] for s in r_snd[rr]])
            lag = nn[idx][:, None] - r_n[rr][None, :]
            b = np.searchsorted(LAG_EDGES, lag, "right") - 1
            b[(lag < 0) | (lag >= LAG_EDGES[-1])] = -1
            kk, ri = np.nonzero(b >= 0)
            np.add.at(R, (kk, jj[ri], b[kk, ri]), 1.0)
        for k, B in enumerate(idx):
            rt = room_t.get(room[B])
            if rt is None:
                continue
            lo = np.searchsorted(t[rt], tc[B], "right")
            hi_ = np.searchsorted(t[rt], min(t[B], tc[B] + D_MAX), "left")
            for m in rt[lo:hi_]:
                p = jpos.get(agent[m])
                if p is not None:
                    R[k, p, ncol - 1] += 1.0
        Y1.append(y1); Y2.append(y2)
        Rs.append(R.reshape(-1, ncol))
        pairs.append(np.repeat(aidx[ag] * nA, len(idx) * nJ) + np.tile([aidx[j] for j in js], len(idx)))
        ads.append(np.full(len(idx) * nJ, row))
        bids.append(np.repeat(idx, nJ))
    ad = np.concatenate(ads)
    pr = np.concatenate(pairs).astype(np.int64) + np.int64(nA * nA) * ad.astype(np.int64)
    R = np.vstack(Rs)
    b = np.concatenate(bids)
    _, inv = np.unique(b, return_inverse=True)
    T = np.column_stack([np.bincount(inv, weights=R[:, c])[inv] for c in range(ncol)])
    return {"y_par": np.concatenate(Y1), "y_perp": np.concatenate(Y2), "R": np.column_stack([R, T]), "pair": pr,
            "ad": ad, "n_ad": g.height}


def fit(Ds: dict, y: np.ndarray, Bw: np.ndarray | None):
    R, pr, ad = Ds["R"], Ds["pair"], Ds["ad"]
    up, inv = np.unique(pr, return_inverse=True)
    cnt = np.bincount(inv)
    yd = y - (np.bincount(inv, weights=y) / cnt)[inv]
    Rd = R - np.column_stack([(np.bincount(inv, weights=R[:, c]) / cnt)[inv] for c in range(R.shape[1])])
    nad, k = Ds["n_ad"], Rd.shape[1]
    XtX = np.zeros((nad, k, k))
    Xty = np.zeros((nad, k))
    for c1 in range(k):
        Xty[:, c1] = np.bincount(ad, weights=Rd[:, c1] * yd, minlength=nad)
        for c2 in range(c1, k):
            v = np.bincount(ad, weights=Rd[:, c1] * Rd[:, c2], minlength=nad)
            XtX[:, c1, c2] = v
            XtX[:, c2, c1] = v

    def solve(w):
        A_ = (w[:, None, None] * XtX).sum(0)
        b_ = (w[:, None] * Xty).sum(0)
        return np.linalg.lstsq(A_ + 1e-9 * np.eye(k), b_, rcond=None)[0]
    beta = solve(np.ones(nad))
    out = {"beta": beta[:len(NAMES)]}
    if Bw is not None:
        bs = np.array([solve(w) for w in Bw])[:, :len(NAMES)]
        out["boot"] = bs
        out["se"] = bs.std(0)
    return out


def kick_unit(Du: L.Data, rd: pl.DataFrame, W: dict, B: int, seed: int) -> dict:
    keys = sorted(set(Du.st["plane"].to_list()))
    Pmap = {k: L.proj(Du.planes[k]) for k in keys}
    Ds = design(Du, rd, W, Pmap)
    Bw = L.boot_weights(np.arange(Ds["n_ad"]), B, seed) if B else None
    out = {"n_rows": int(len(Ds["y_par"]))}
    for nm in ("par", "perp"):
        f = fit(Ds, Ds[f"y_{nm}"], Bw)
        out[f"beta_{nm}"] = f["beta"].tolist()
        if Bw is not None:
            out[f"se_{nm}"] = f["se"].tolist()
            out[f"boot_{nm}"] = f["boot"][:, :2]              # lag 0 and lag 1 draws, for the pooled ratio
        out[f"ratio_{nm}"] = float(f["beta"][1] / f["beta"][0]) if f["beta"][0] != 0 else np.nan
    return out


def pooled_ratio(units: list[dict], nm: str):
    """Pool lag-0 and lag-1 coefficients over units with DL weights of the lag-0 coefficient; the ratio of pooled values,
    with a percentile CI from the per-unit bootstrap draws (independent across units)."""
    b0 = np.array([u[f"beta_{nm}"][0] for u in units]); s0 = np.array([u[f"se_{nm}"][0] for u in units])
    b1 = np.array([u[f"beta_{nm}"][1] for u in units]); s1 = np.array([u[f"se_{nm}"][1] for u in units])
    mu0, se0, t20, _, k = L.dl_pool(b0, s0)
    mu1, se1, _, _, _ = L.dl_pool(b1, s1)
    w = 1 / (s0 ** 2 + t20)
    w = w / w.sum()
    nb = min(u[f"boot_{nm}"].shape[0] for u in units)
    draws = np.array([sum(w[k_] * units[k_][f"boot_{nm}"][b, 1] for k_ in range(len(units))) /
                      sum(w[k_] * units[k_][f"boot_{nm}"][b, 0] for k_ in range(len(units))) for b in range(nb)])
    r = float(sum(w * b1) / sum(w * b0))
    return {"beta0": mu0, "beta0_se": se0, "beta1": mu1, "beta1_se": se1, "ratio": r,
            "ratio_ci90": np.percentile(draws, [5, 95]).tolist(), "ratio_ci95": np.percentile(draws, [2.5, 97.5]).tolist(),
            "k": k}
