"""H110 estimators: field-orthogonal old-state remanence per agent (H96's construction, re-implemented), own-state
remanence, pinned vs unpinned group persistence, decay ratio, offset end, natives. Works on real or synthetic
statement vectors aligned with windows.parquet rows (column `srow` indexes the DQ5 arrays).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
SH = ROOT / "data/processed/shared"
ED = SH / "embeddings"
D = ROOT / "data/processed/H110-exchange-bias-own-artifact"
MODELS = ("bge_small", "gte_modernbert")
MIN_AD = 3       # statements per agent-day (old state, placebos)
MIN_PRE = 3
MIN_POST = 2
FLOOR = 0.02
POST = ["d1", "d2", "d3", "d4", "d5"]


def unit(X):
    X = np.asarray(X, dtype=np.float64)
    n = np.linalg.norm(X, axis=-1, keepdims=True)
    n[n == 0] = 1.0
    return X / n


def load_tables(root: Path = D):
    return (pl.read_parquet(root / "transitions.parquet"), pl.read_parquet(root / "windows.parquet"),
            pl.read_parquet(root / "pinning.parquet"))


def load_X(srows: np.ndarray, model: str, variant: str = "style_resid32") -> np.ndarray:
    A = np.load(ED / f"statements_{variant}_{model}.npy", mmap_mode="r")
    u, inv = np.unique(srows, return_inverse=True)
    return unit(np.asarray(A[u], dtype=np.float64))[inv]


def field_projectors(tr: pl.DataFrame, model: str, include_holdout: bool = False) -> dict:
    import culture_vectors as CV
    ad = pl.DataFrame({"goal_no": tr["P"].cast(pl.Int64).to_list(), "regime": tr["regime"].to_list()})
    V, idx = CV.directions(model, ad, include_holdout=include_holdout)
    out = {}
    for row in tr.iter_rows(named=True):
        P, reg = int(row["P"]), row["regime"]
        cols = [V[e["i"]] for e in idx if e["level"] == "goal" and e["goal_no"] == P and e["regime"] == reg
                and e["kind"] in ("kickoff", "goal", "kickoff_room")]
        kick = [V[e["i"]] for e in idx if e["level"] == "goal" and e["goal_no"] == P and e["regime"] == reg
                and e["kind"] == "kickoff"]
        if cols:
            Q, R = np.linalg.qr(np.array(cols, dtype=np.float64).T)
            Q = Q[:, np.abs(np.diag(R)) > 1e-8]
            Pp = np.eye(32) - Q @ Q.T
        else:
            Pp = np.eye(32)
        out[P] = {"Pperp": Pp, "kick": unit(kick[0]) if kick else None, "dim": int(len(cols))}
    return out


def _ad_vectors(sub: pl.DataFrame, X: np.ndarray, rows: np.ndarray) -> dict:
    """agent -> list of agent-day unit vectors (>= MIN_AD statements)."""
    out = {}
    ag = sub["agent"].to_numpy()
    dd = sub["pt_date"].to_numpy()
    key = ag.astype(np.int64) * 100000 + np.unique(dd, return_inverse=True)[1]
    for k in np.unique(key):
        m = key == k
        if m.sum() >= MIN_AD:
            out.setdefault(int(k // 100000), []).append(unit(X[rows[m]].mean(0)))
    return out


def remanence(tr: pl.DataFrame, win: pl.DataFrame, X: np.ndarray, proj: dict) -> pl.DataFrame:
    """Rows: P, agent, window (pre, d1..d5), n, m (old-state remanence), o (own-state), b (new-kickoff alignment).
    X rows align with `win` rows."""
    out = []
    win = win.with_row_index("wr")
    for row in tr.iter_rows(named=True):
        P = int(row["P"])
        Pp = proj[P]["Pperp"]
        kick = proj[P]["kick"]
        w = win.filter(pl.col("P") == P)
        rows = w["wr"].to_numpy()
        wl = w["window"].to_numpy()
        old = _ad_vectors(w.filter(pl.col("window") == "old"), X, rows[wl == "old"])
        if len(old) < 2:
            continue
        own = {a: unit(np.mean(v, 0)) for a, v in old.items()}
        allv = [(a, v) for a, vs in old.items() for v in vs]
        plc = []
        for q in json.loads(row["placebos"]):
            name = f"plc_{q['Q']}"
            sub = w.filter(pl.col("window") == name)
            vq = _ad_vectors(sub, X, rows[wl == name])
            vv = [v for vs in vq.values() for v in vs]
            if vv:
                plc.append(unit(Pp @ unit(np.mean(vv, 0))))
        if len(plc) < 3:
            continue
        PL = np.array(plc)
        ownP = {a: unit(Pp @ v) for a, v in own.items()}
        for wn in ["pre"] + POST:
            sub = w.filter(pl.col("window") == wn)
            r_ = rows[wl == wn]
            ag = sub["agent"].to_numpy()
            for a in np.unique(ag):
                m = ag == a
                need = MIN_PRE if wn == "pre" else MIN_POST
                if m.sum() < need:
                    continue
                v = unit(X[r_[m]].mean(0))
                others = [vv for (aa, vv) in allv if aa != a]
                if not others:
                    continue
                e = unit(Pp @ unit(np.mean(others, 0)))
                mi = float(v @ e - np.median(PL @ v))
                oi = np.nan
                if int(a) in ownP and len(ownP) >= 2:
                    oo = [float(v @ ownP[j]) for j in ownP if j != int(a)]
                    oi = float(v @ ownP[int(a)] - np.mean(oo))
                bi = float(v @ kick) if kick is not None else np.nan
                out.append({"P": P, "agent": int(a), "window": wn, "n": int(m.sum()), "m": mi, "o": oi, "b": bi})
    return pl.DataFrame(out)


# ------------------------------------------------------------------------------------------------ group statistics
def panel(rem: pl.DataFrame, pin: pl.DataFrame, stat: str = "m", pin_col: str = "pinned_own") -> pl.DataFrame:
    w = rem.pivot(index=["P", "agent"], on="window", values=stat)
    for c in ["pre"] + POST:
        if c not in w.columns:
            w = w.with_columns(pl.lit(None, dtype=pl.Float64).alias(c))
    w = w.join(pin.select("P", "agent", pl.col(pin_col).alias("pinned"), "post_commits", "last_day", "n_post_days")
               .with_columns(pl.col("P").cast(w["P"].dtype)), on=["P", "agent"], how="inner")
    return w


def _ratio_stats(pre, d1, grp, tr_id, w):
    """Pooled ratio-of-sums per group over transitions where both groups have >= 2 agents (by weight presence)."""
    out = {}
    for g in (True, False):
        m = grp == g
        num = np.sum(w[m] * d1[m])
        den = np.sum(w[m] * pre[m])
        out[g] = (num, den)
    RP = out[True][0] / out[True][1] if out[True][1] != 0 else np.nan
    RU = out[False][0] / out[False][1] if out[False][1] != 0 else np.nan
    lP = -np.log(max(RP, FLOOR)) if np.isfinite(RP) else np.nan
    lU = -np.log(max(RU, FLOOR)) if np.isfinite(RU) else np.nan
    ratio = lU / lP if (np.isfinite(lP) and lP > 0) else (np.inf if np.isfinite(lU) and lU > 0 else np.nan)
    return RP, RU, lP, lU, ratio, out[True][1], out[False][1]


def persistence(pan: pl.DataFrame, nboot: int = 2000, seed: int = 0, switchers: bool = False, post: str = "d1") -> dict:
    p = pan.filter(pl.col("pre").is_not_null() & pl.col(post).is_not_null())
    # transitions with both groups >= 2
    cnt = p.group_by("P").agg(pl.col("pinned").sum().alias("nP"), (~pl.col("pinned")).sum().alias("nU"))
    okP = cnt.filter((pl.col("nP") >= 2) & (pl.col("nU") >= 2))["P"].to_list()
    per = {}
    for P_, sub in p.group_by("P"):
        P_ = int(P_[0]) if isinstance(P_, tuple) else int(P_)
        g = sub["pinned"].to_numpy()
        r = _ratio_stats(sub["pre"].to_numpy(), sub[post].to_numpy(), g, None, np.ones(sub.height))
        per[P_] = {"nP": int(g.sum()), "nU": int((~g).sum()), "R1_P": r[0], "R1_U": r[1], "lam_ratio": r[4],
                   "pre_P": r[5] / max(g.sum(), 1), "pre_U": r[6] / max((~g).sum(), 1)}
    q = p.filter(pl.col("P").is_in(okP))
    if switchers:
        sw = q.group_by("agent").agg(pl.col("pinned").any().alias("a"), (~pl.col("pinned")).any().alias("b"))
        keep = sw.filter(pl.col("a") & pl.col("b"))["agent"].to_list()
        q = q.filter(pl.col("agent").is_in(keep))
    if q.height == 0 or q["pinned"].sum() == 0 or (~q["pinned"]).sum() == 0:
        return {"per_transition": per, "n": 0, "transitions": okP}
    pre, d1, g = q["pre"].to_numpy(), q[post].to_numpy(), q["pinned"].to_numpy()
    ag = q["agent"].to_numpy()
    # equal weight per agent within group for the switcher variant
    w0 = np.ones(q.height)
    if switchers:
        for a in np.unique(ag):
            for gg in (True, False):
                m = (ag == a) & (g == gg)
                if m.any():
                    w0[m] = 1.0 / m.sum()
    est = _ratio_stats(pre, d1, g, None, w0)
    ua, ai = np.unique(ag, return_inverse=True)
    rng = np.random.default_rng(seed)
    bs = []
    for _ in range(nboot):
        c = rng.multinomial(len(ua), np.full(len(ua), 1 / len(ua))).astype(float)
        bs.append(_ratio_stats(pre, d1, g, None, w0 * c[ai]))
    bs = np.array(bs, dtype=float)
    ci = lambda v: [float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5))]  # noqa: E731
    lr = np.log(np.clip(bs[:, 4], 1e-3, 1e3))
    return {"per_transition": per, "transitions": okP, "n": int(q.height), "n_agents": int(len(ua)),
            "nP": int(g.sum()), "nU": int((~g).sum()),
            "R1_P": est[0], "R1_P_ci": ci(bs[:, 0]), "R1_U": est[1], "R1_U_ci": ci(bs[:, 1]),
            "lam_P": est[2], "lam_U": est[3], "ratio": est[4],
            "ratio_ci": [float(np.exp(np.nanpercentile(lr, 2.5))), float(np.exp(np.nanpercentile(lr, 97.5)))],
            "preP_ci": ci(bs[:, 5]), "preU_ci": ci(bs[:, 6]),
            "dR": est[0] - est[1], "dR_ci": ci(bs[:, 0] - bs[:, 1])}


def offset_end(pan: pl.DataFrame, nboot: int = 2000, seed: int = 0) -> dict:
    """Pinned excess over the same transition's unpinned mean, split live / after (card O3)."""
    rows = []
    for P_, sub in pan.group_by("P"):
        U = sub.filter(~pl.col("pinned"))
        for k, d in enumerate(POST, start=1):
            mu = U[d].drop_nulls()
            if len(mu) == 0:
                continue
            base = float(mu.mean())
            for r in sub.filter(pl.col("pinned") & pl.col(d).is_not_null()).iter_rows(named=True):
                last = r["last_day"]
                cls = "live" if k <= last else ("after" if k >= last + 2 else "edge")
                rows.append({"P": int(P_[0]) if isinstance(P_, tuple) else int(P_), "agent": r["agent"], "k": k,
                             "e": r[d] - base, "cls": cls})
    if not rows:
        return {"n": 0}
    e = pl.DataFrame(rows)
    ag = e["agent"].to_numpy()
    ua, ai = np.unique(ag, return_inverse=True)
    ev, cl = e["e"].to_numpy(), e["cls"].to_numpy()

    def stat(w):
        o = {}
        for c in ("live", "after", "edge"):
            m = cl == c
            o[c] = np.sum(w[m] * ev[m]) / np.sum(w[m]) if np.sum(w[m]) > 0 else np.nan
        return o
    est = stat(np.ones(len(ev)))
    rng = np.random.default_rng(seed)
    bs = [stat(rng.multinomial(len(ua), np.full(len(ua), 1 / len(ua))).astype(float)[ai]) for _ in range(nboot)]
    out = {"n": int(len(ev)), "counts": {c: int((cl == c).sum()) for c in ("live", "after", "edge")}}
    for c in ("live", "after", "edge"):
        v = np.array([b[c] for b in bs], float)
        out[c] = float(est[c]) if np.isfinite(est[c]) else None
        out[c + "_ci"] = [float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5))] if np.isfinite(v).any() else None
    return out


def spearman(x, y) -> float:
    from scipy.stats import spearmanr
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    if ok.sum() < 4:
        return float("nan")
    return float(spearmanr(x[ok], y[ok]).statistic)
