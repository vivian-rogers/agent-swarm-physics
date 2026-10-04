"""H118 estimators: replica overlap q between two rooms' content (split-half disattenuated), equal-time memory M(d),
damage time tau_D, late overlap, relabel reference, bootstraps; code overlap on ancestor keys.

Statement-level input per period (see `period_data`): agent code, agent's period room (2 = A/#best, 3 = B/#rest),
bin code (day*100 + hour), half (1/2), day, hour, active time of the bin mid-point, vectors X (n x 32, centred on the
leave-own-period-out reference).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = ROOT / "data/processed/H118-forked-rpg-replicas"
SH = ROOT / "data/processed/shared"
EMB = SH / "embeddings"
MIN_STMT = 4          # statements per room per bin (card O1)
TAU_GRID = np.exp(np.linspace(np.log(0.25), np.log(80.0), 60))
BAND = ("36", "37", "39", "41", "42")


# ============================================================================ data
def period_data(period: str, model: str = "bge_small", variant: str = "style_resid32") -> dict:
    st = pl.read_parquet(DATA / "statements.parquet").filter(pl.col("period") == period).sort("t")
    X = np.load(EMB / f"statements_{variant}_{model}.npy", mmap_mode="r")
    ref = np.load(DATA / f"ref_centres_{model}.npz")[period] if variant == "style_resid32" else None
    V = np.asarray(X[st["srow"].to_numpy()], dtype=np.float64)
    if ref is None:  # variant: centre on the same reference rule recomputed for this variant
        ref = _ref_variant(period, X)
    V = V - ref
    cal = pl.read_parquet(SH / "calendar.parquet").select("pt_date", "window_s")
    days = st.select("day", "pt_date").unique().sort("day").join(cal, on="pt_date", how="left")
    hrs = np.floor(days["window_s"].to_numpy() / 3600).clip(1, None)
    start = dict(zip(days["day"].to_list(), np.concatenate([[0], np.cumsum(hrs)[:-1]]).tolist()))
    tmid = np.array([start[d] + h + 0.5 for d, h in zip(st["day"].to_list(), st["hour"].to_list())])
    return {"period": period, "agent": st["agent"].to_numpy(), "room": st["room"].to_numpy(), "bin": st["bin"].to_numpy(),
            "half": st["half"].to_numpy(), "day": st["day"].to_numpy(), "hour": st["hour"].to_numpy(), "t": tmid, "X": V,
            "n_days": int(st["day"].max())}


def _ref_variant(period, X):
    allst = pl.read_parquet(EMB / "statements.parquet").with_row_index("srow")
    import sys
    sys.path.insert(0, str(ROOT / "infra/shared"))
    from common import holdout_mask
    hm = holdout_mask(allst["pt_date"].to_list(), allst["goal_no"].to_list())
    allst = allst.with_columns(pl.Series("hm", hm)).filter(~pl.col("hm") & ~pl.col("holdout"))
    g = int(period.rstrip("a"))
    reg = "II" if period in ("35", "36a") else "III"
    sel = allst.filter((pl.col("regime").cast(pl.String) == reg) & (pl.col("goal_no") != g) & (pl.col("goal_no") != 51))
    return np.asarray(X[np.sort(sel["srow"].to_numpy())], dtype=np.float64).mean(0)


# ============================================================================ core statistic
def _room_bin_centroids(pdat, w=None, mult=None, room_of=None):
    """Agent-weighted centroids per (room, bin): full and the two halves. Returns dict with bins (sorted codes),
    cA, cB (nb x d), A1, A2, B1, B2, nA, nB (statement counts), usable mask."""
    ag, bn, hf, X = pdat["agent"], pdat["bin"], pdat["half"], pdat["X"]
    n = len(ag)
    w = np.ones(n) if w is None else w
    room = pdat["room"] if room_of is None else np.array([room_of[a] for a in ag])
    bins = np.unique(bn)
    bi = np.searchsorted(bins, bn)
    agents = np.unique(ag)
    ai = np.searchsorted(agents, ag)
    m_ag = np.ones(len(agents)) if mult is None else np.array([mult.get(a, 0.0) for a in agents])
    na, nb = len(agents), len(bins)
    d = X.shape[1]
    out = {"bins": bins}
    for key, hsel in (("F", None), ("1", 1), ("2", 2)):
        sel = np.ones(n, bool) if hsel is None else (hf == hsel)
        g = ai[sel] * nb + bi[sel]
        S = np.zeros((na * nb, d))
        np.add.at(S, g, X[sel] * w[sel, None])
        C = np.bincount(g, weights=w[sel], minlength=na * nb)
        pres = C > 0
        M = np.zeros_like(S)
        M[pres] = S[pres] / C[pres, None]
        M = M.reshape(na, nb, d)
        P = pres.reshape(na, nb).astype(float) * m_ag[:, None]
        rag = np.array([room[np.flatnonzero(ag == a)[0]] for a in agents])
        for r, lab in ((2, "A"), (3, "B")):
            Pr = P * (rag == r)[:, None]
            den = Pr.sum(0)
            cen = np.einsum("ab,abd->bd", Pr, M) / np.where(den > 0, den, 1)[:, None]
            out[lab + key] = cen
            out[lab + key + "_ok"] = den > 0
            if key == "F":
                cnt = np.bincount(bi[sel & (room == r)], weights=w[sel & (room == r)], minlength=nb)
                out["n" + lab] = cnt
    ok = (out["nA"] >= MIN_STMT) & (out["nB"] >= MIN_STMT)
    for lab in "AB":
        ok &= out[lab + "1_ok"] & out[lab + "2_ok"]
    out["ok"] = ok
    return out


def overlap_core(pdat, w=None, mult=None, room_of=None) -> dict:
    """Usable bins and the cross-room / within-room products they need."""
    c = _room_bin_centroids(pdat, w, mult, room_of)
    ok = c["ok"]
    bins = c["bins"][ok]
    cA, cB = c["AF"][ok], c["BF"][ok]
    tb = {}
    for b, t in zip(pdat["bin"], pdat["t"]):
        tb[b] = t
    nA, nB = c["nA"][ok], c["nB"][ok]
    return {"bins": bins, "day": bins // 100, "Cx": cA @ cB.T,
            "SA": np.einsum("bd,bd->b", c["A1"][ok], c["A2"][ok]),
            "SB": np.einsum("bd,bd->b", c["B1"][ok], c["B2"][ok]),
            "t": np.array([tb[b] for b in bins]), "w_bin": 2 * nA * nB / np.maximum(nA + nB, 1),
            "n_days": pdat["n_days"]}


def stats_from_core(core, late_days=None, bw=None) -> dict:
    """q_eq(d), q_lag(d), M(d), q_late, q_all and per-bin q from the products; bw = bin weights (bin bootstrap)."""
    Cx, SA, SB, day = core["Cx"], core["SA"], core["SB"], core["day"]
    nb = len(day)
    bw = np.ones(nb) if bw is None else np.asarray(bw, float)
    nd = core["n_days"]
    res = {"q_eq_d": {}, "q_lag_d": {}, "M_d": {}}

    def wm(v, ww):
        s = ww.sum()
        return (v * ww).sum() / s if s > 0 else np.nan
    for d in range(1, nd + 1):
        i = np.flatnonzero((day == d) & (bw > 0))
        j = np.flatnonzero((day != d) & (bw > 0))
        if len(i) == 0:
            continue
        wi = bw[i]
        num = wm(np.diag(Cx)[i], wi)
        sa, sb = wm(SA[i], wi), wm(SB[i], wi)
        qe = num / np.sqrt(sa * sb) if sa > 0 and sb > 0 else np.nan
        res["q_eq_d"][d] = qe
        if len(j):
            wj = bw[j]
            W = np.outer(wi, wj)
            numl = 0.5 * ((Cx[np.ix_(i, j)] * W).sum() + (Cx[np.ix_(j, i)] * W.T).sum()) / W.sum()
            sa2 = 0.5 * (wm(SA[i], wi) + wm(SA[j], wj))
            sb2 = 0.5 * (wm(SB[j], wj) + wm(SB[i], wi))
            ql = numl / np.sqrt(sa2 * sb2) if sa2 > 0 and sb2 > 0 else np.nan
            res["q_lag_d"][d] = ql
            res["M_d"][d] = qe - ql
    if late_days is None:
        late_days = list(range(nd - int(np.ceil(nd / 2)) + 1, nd + 1))
    for key, sel in (("q_late", np.isin(day, late_days)), ("q_all", np.ones(nb, bool))):
        ww = bw * sel
        sa, sb = wm(SA, ww), wm(SB, ww)
        res[key] = wm(np.diag(Cx), ww) / np.sqrt(sa * sb) if (ww.sum() > 0 and sa > 0 and sb > 0) else np.nan
    late = np.flatnonzero(np.isin(day, late_days) & (bw > 0))
    res["M_late"] = float(np.nanmean([res["M_d"].get(d, np.nan) for d in range(2, nd + 1)])) if nd >= 2 else np.nan
    pos = np.concatenate([SA[SA > 0], SB[SB > 0]])
    smin = 0.25 * np.median(pos) if len(pos) else 1e-6
    res["q_bin"] = np.clip(np.diag(Cx) / np.sqrt(np.maximum(SA, smin) * np.maximum(SB, smin)), -1.5, 1.5)
    res["t"], res["w_bin"], res["bins"] = core["t"], core["w_bin"] * bw, core["bins"]
    res["SA"], res["SB"], res["diag"] = SA, SB, np.diag(Cx).copy()
    return res


def overlap_stats(pdat, w=None, mult=None, room_of=None, late_days=None) -> dict:
    return stats_from_core(overlap_core(pdat, w, mult, room_of), late_days)


def bin_weights(day, rng):
    """Multinomial resample of usable bins within each day (equal-time pairing kept)."""
    bw = np.zeros(len(day))
    for d in np.unique(day):
        idx = np.flatnonzero(day == d)
        np.add.at(bw, rng.choice(idx, size=len(idx), replace=True), 1.0)
    return bw


def fit_tau(t, q, w, grid=TAU_GRID) -> dict:
    """Weighted LS fit q(t) = a + c exp(-t/tau), tau profiled on a grid. Returns tau, q0 = a + c, q_inf = a, sse."""
    t, q, w = map(np.asarray, (t, q, w))
    ok = np.isfinite(q) & (w > 0)
    t, q, w = t[ok], q[ok], w[ok]
    if len(t) < 4:
        return {"tau": np.nan, "q0": np.nan, "q_inf": np.nan, "decays": False}
    best = None
    sw = np.sqrt(w)
    for tau in grid:
        A = np.column_stack([np.ones_like(t), np.exp(-t / tau)])
        coef, *_ = np.linalg.lstsq(A * sw[:, None], q * sw, rcond=None)
        sse = float(np.sum(w * (q - A @ coef) ** 2))
        if best is None or sse < best[0]:
            best = (sse, tau, coef)
    sse, tau, (a, c) = best
    return {"tau": float(tau), "q0": float(a + c), "q_inf": float(a), "decays": bool(c > 0), "sse": sse}


# ============================================================================ resampling
def relabel_ref(pdat, R=500, rng=None, late_days=None) -> dict:
    rng = rng or np.random.default_rng(20261004)
    agents = np.unique(pdat["agent"])
    rooms = np.array([pdat["room"][np.flatnonzero(pdat["agent"] == a)[0]] for a in agents])
    qd = {d: [] for d in range(1, pdat["n_days"] + 1)}
    ql = []
    for _ in range(R):
        perm = rng.permutation(rooms)
        r = overlap_stats(pdat, room_of=dict(zip(agents, perm)), late_days=late_days)
        for d, v in r["q_eq_d"].items():
            qd[d].append(v)
        ql.append(r["q_late"])
    return {"q_rel_d": {d: float(np.nanmean(v)) for d, v in qd.items() if v},
            "q_rel_late": float(np.nanmean(ql))}


def bootstrap(pdat, kind="agent", B=300, rng=None, late_days=None) -> list:
    rng = rng or np.random.default_rng(20261005)
    out = []
    ag = pdat["agent"]
    agents = np.unique(ag)
    rooms = {a: pdat["room"][np.flatnonzero(ag == a)[0]] for a in agents}
    for _ in range(B):
        mult, w = None, None
        if kind in ("agent", "agent_bin"):
            mult = {}
            for r in (2, 3):
                pool = [a for a in agents if rooms[a] == r]
                for a in rng.choice(pool, size=len(pool), replace=True):
                    mult[a] = mult.get(a, 0) + 1
        if kind in ("stmt", "stmt_bin"):
            w = rng.poisson(1.0, size=len(ag)).astype(float)
        core = overlap_core(pdat, w=w, mult=mult)
        bw = bin_weights(core["day"], rng) if kind.endswith("_bin") else None
        res = stats_from_core(core, late_days, bw)
        ft = fit_tau(res["t"], res["q_bin"], res["w_bin"])
        out.append({"q_eq_d": res["q_eq_d"], "M_d": res["M_d"], "q_late": res["q_late"], "tau": ft["tau"],
                    "q_all": res["q_all"], "M_late": res["M_late"]})
    return out


def ci(vals, lo=2.5, hi=97.5):
    v = np.asarray([x for x in vals if x is not None and np.isfinite(x)])
    if len(v) < 5:
        return (np.nan, np.nan)
    return (float(np.percentile(v, lo)), float(np.percentile(v, hi)))
