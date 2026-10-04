"""H73 core estimators: three-component style decomposition (O1), attribution with and without the context component
(O2), context-held dispersion (O3), NE41 drift-reversal projection, and helpers shared by the native tests.

All functions take numpy arrays or the messages frame built by scheme/build.py. No text, no holdout rows.
"""
from __future__ import annotations
import os
for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "4")
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
SH = ROOT / "data/processed/shared"
DATA = ROOT / "data/processed/H73-style-three-components"
HYP = ROOT / "hypotheses/H73-style-three-components"
sys.path.insert(0, str(ROOT / "infra" / "shared"))

STYLE = ["log_chars", "lines", "bullet_share", "headers", "bold", "emoji", "excl", "ques", "urls", "backticks",
         "digit_share", "upper_share", "at", "emdash", "fps", "fpp", "sp", "colon", "word_len", "parens"]
TC = [f for f in STYLE if f not in ("log_chars", "backticks", "urls")]
BIN_EDGES = [0, 2, 4, 8, 16, 32]          # p in [0,1], [2,3], [4,7], [8,15], [16,31], [32, inf)
BIN_NAMES = ["chat", "p0-1", "p2-3", "p4-7", "p8-15", "p16-31", "p32+"]
REF_BIN = 4                                # p8-15 is the reference level for dummies
HOUR_KNOTS = [1.0, 2.0, 4.0]


# ============================================================================================ data
def load_messages(dedupe: str = "copy", main_only: bool = True) -> pl.DataFrame:
    m = pl.read_parquet(DATA / "messages.parquet")
    assert not m["holdout"].any(), "holdout rows in the message table"
    if main_only:
        m = m.filter(pl.col("main"))
    if dedupe == "copy":
        m = m.filter(~pl.col("copy"))
    elif dedupe == "restate":
        m = m.filter(~pl.col("restate"))
    return m.sort("agent", "t")


def ctx_bin(ctx_mode: np.ndarray, ctx_pos: np.ndarray) -> np.ndarray:
    """0 = chat mode; 1..6 = computer-use fill bins."""
    p = np.nan_to_num(ctx_pos.astype(float), nan=0.0)
    b = 1 + np.searchsorted(np.array(BIN_EDGES[1:]), p, side="right")
    return np.where(ctx_mode == "cu", b, 0).astype(np.int8)


def zfill(ctx_mode: np.ndarray, ctx_pos: np.ndarray) -> np.ndarray:
    """log2(1+p), centred on the period's computer-use mean; 0 in chat mode."""
    cu = ctx_mode == "cu"
    z = np.log2(1.0 + np.nan_to_num(ctx_pos.astype(float), nan=0.0))
    if cu.any():
        z = z - z[cu].mean()
    return np.where(cu, z, 0.0)


def arrays(m: pl.DataFrame, feats: str = "tc") -> dict:
    cols = [f"tc_{f}" for f in TC] if feats == "tc" else [f"s_{f}" for f in STYLE]
    mode = m["ctx_mode"].to_numpy()
    pos = m["ctx_pos"].fill_null(0).to_numpy()
    out = {"X": m.select(cols).to_numpy().astype(np.float64), "agent": m["agent"].to_numpy(),
           "day": m["pt_date"].to_numpy(), "hours": m["hours"].to_numpy().astype(float),
           "bin": ctx_bin(mode, pos), "z": zfill(mode, pos), "cu": mode == "cu", "pos": pos.astype(float),
           "kctx": m["k_ctx"].fill_null(0).to_numpy().astype(float), "register": m["register"].to_numpy(),
           "is_reply": m["is_reply"].to_numpy(), "has_mention": m["has_mention"].to_numpy(),
           "t": m["t"].dt.epoch("us").to_numpy(), "turn": m["turn_id"].to_numpy()}
    return out


# ============================================================================================ design blocks
def dummies(codes: np.ndarray, drop: object | None = "first") -> np.ndarray:
    lv, inv = np.unique(codes, return_inverse=True)
    D = np.zeros((len(codes), len(lv)))
    D[np.arange(len(codes)), inv] = 1.0
    if drop == "first":
        return D[:, 1:]
    if drop is None:
        return D
    keep = lv != drop
    return D[:, keep]


def hour_basis(h: np.ndarray) -> np.ndarray:
    return np.column_stack([h] + [np.maximum(h - k, 0.0) for k in HOUR_KNOTS])


def block_G(a: dict) -> np.ndarray:
    return np.column_stack([dummies(a["day"]), hour_basis(a["hours"])])


def block_A(a: dict) -> np.ndarray:
    return dummies(a["agent"])


def block_C(a: dict, bins: np.ndarray | None = None, z: np.ndarray | None = None, agent_slopes: bool = True) -> np.ndarray:
    bins = a["bin"] if bins is None else bins
    z = a["z"] if z is None else z
    present = np.unique(bins)
    ref = REF_BIN if REF_BIN in present else present[0]
    parts = [dummies(bins, drop=ref)] if len(present) > 1 else []
    if agent_slopes and np.any(z != 0):
        Da = dummies(a["agent"], drop=None)
        S = Da * z[:, None]
        S = S[:, np.abs(S).sum(0) > 0]
        parts.append(S)
    return np.column_stack(parts) if parts else np.zeros((len(bins), 0))


def block_R(a: dict) -> np.ndarray:
    reg = a["register"]
    if (reg != "none").sum() == 0:
        return np.zeros((len(reg), 0))
    return dummies(reg, drop="none")


def fit_r2(Y: np.ndarray, blocks: list[np.ndarray], return_resid: bool = False):
    """Trace R^2 (raw and df-adjusted) of multivariate OLS of Y on [1, blocks]."""
    n = len(Y)
    X = np.column_stack([np.ones(n)] + [b for b in blocks if b.shape[1]])
    B, _, rank, _ = np.linalg.lstsq(X, Y, rcond=None)
    R = Y - X @ B
    rss = float((R ** 2).sum())
    tss = float(((Y - Y.mean(0)) ** 2).sum())
    r2 = 1 - rss / tss
    r2a = 1 - (rss / max(n - rank, 1)) / (tss / (n - 1))
    if return_resid:
        return r2, r2a, rank, R, B, X
    return r2, r2a, rank


def cell_ceiling(Y: np.ndarray, a: dict) -> tuple[float, int]:
    """Adjusted R^2 of the cell-means model, cells = agent x day x context bin x register."""
    key = np.array([f"{g}|{d}|{b}|{r}" for g, d, b, r in zip(a["agent"], a["day"], a["bin"], a["register"])])
    _, inv = np.unique(key, return_inverse=True)
    k = inv.max() + 1
    cnt = np.bincount(inv)
    S = np.zeros((k, Y.shape[1]))
    np.add.at(S, inv, Y)
    mu = S / cnt[:, None]
    rss = float(((Y - mu[inv]) ** 2).sum())
    tss = float(((Y - Y.mean(0)) ** 2).sum())
    n = len(Y)
    return 1 - (rss / max(n - k, 1)) / (tss / (n - 1)), int(k)


def permute_within(groups: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Index permutation that shuffles rows within each group."""
    idx = np.arange(len(groups))
    out = idx.copy()
    order = np.argsort(groups, kind="stable")
    g = groups[order]
    cuts = np.flatnonzero(g[1:] != g[:-1]) + 1
    for seg in np.split(order, cuts):
        if len(seg) > 1:
            out[seg] = rng.permutation(seg)
    return out


def decompose(a: dict, n_perm: int = 200, seed: int = 0, extra_G: list[np.ndarray] | None = None,
              mask: np.ndarray | None = None) -> dict:
    """O1. Nested and drop-one adjusted R^2, ceiling, F3, unique shares, context permutation null."""
    if mask is not None:
        a = {k: (v[mask] if isinstance(v, np.ndarray) and len(v) == len(mask) else v) for k, v in a.items()}
    Y = a["X"] - a["X"].mean(0)
    G = [block_G(a)] + (extra_G or [])
    A, C, R = block_A(a), block_C(a), block_R(a)
    r = {}
    r["G"] = fit_r2(Y, G)[1]
    r["GA"] = fit_r2(Y, G + [A])[1]
    r["GAC"] = fit_r2(Y, G + [A, C])[1]
    r["GACR"] = fit_r2(Y, G + [A, C, R])[1]
    r["GCR"] = fit_r2(Y, G + [C, R])[1]
    r["GAR"] = fit_r2(Y, G + [A, R])[1]
    kappa, ncell = cell_ceiling(Y, a)
    denom = kappa - r["G"]
    out = {"n": int(len(Y)), "n_agents": int(len(np.unique(a["agent"]))), "n_days": int(len(np.unique(a["day"]))),
           "n_cu": int(a["cu"].sum()), "n_cells": ncell, "r2a": r, "kappa": kappa,
           "F3": (r["GACR"] - r["G"]) / denom if denom > 0 else np.nan,
           "u_A": (r["GACR"] - r["GCR"]) / denom if denom > 0 else np.nan,
           "u_C": (r["GACR"] - r["GAR"]) / denom if denom > 0 else np.nan,
           "u_R": (r["GACR"] - r["GAC"]) / denom if denom > 0 and R.shape[1] else np.nan,
           "share_G_of_kappa": r["G"] / kappa if kappa > 0 else np.nan}
    if n_perm and C.shape[1]:
        rng = np.random.default_rng(seed)
        grp = np.array([f"{g}|{d}" for g, d in zip(a["agent"], a["day"])])
        obs = r["GACR"] - r["GAR"]
        null = []
        for _ in range(n_perm):
            pi = permute_within(grp, rng)
            Cp = block_C(a, bins=a["bin"][pi], z=a["z"][pi])
            null.append(fit_r2(Y, G + [A, Cp, R])[1] - r["GAR"])
        null = np.array(null)
        out["dC_obs"] = obs
        out["dC_null_med"] = float(np.median(null))
        out["dC_null_q95"] = float(np.quantile(null, 0.95))
        out["p_C"] = float((1 + (null >= obs).sum()) / (1 + n_perm))
        out["u_C_nullcorr"] = (obs - float(np.median(null))) / denom if denom > 0 else np.nan
    return out


# ============================================================================================ O2 attribution
def _blocks(agent: np.ndarray, t: np.ndarray, k: int) -> list[np.ndarray]:
    out = []
    for g in np.unique(agent):
        ix = np.where(agent == g)[0]
        ix = ix[np.argsort(t[ix])]
        if k == 1:
            out += [ix[i:i + 1] for i in range(len(ix))]
        else:
            out += [ix[i:i + k] for i in range(0, len(ix) - k + 1, k)]
    return out


def attribution(a: dict, ks=(1, 5), min_train: int = 10, lam_msgs: float = 20.0, min_days: int = 2) -> dict:
    """O2. Leave-one-day-out balanced accuracy: blind, common-detrended, agent-specific context."""
    X0 = a["X"].copy()
    day, ag = a["day"], a["agent"]
    # label-free day centring
    for d in np.unique(day):
        ix = day == d
        X0[ix] -= X0[ix].mean(0)
    days = np.unique(day)
    res = {k: {"blind": [], "det": [], "agent": [], "truth": []} for k in ks}
    zz = a["z"]
    bins = a["bin"]
    for d in days:
        te = day == d
        tr = ~te
        agents = [g for g in np.unique(ag[tr]) if (ag[tr] == g).sum() >= min_train]
        if len(agents) < 2:
            continue
        agents = np.array(agents)
        Xtr, atr, btr, ztr = X0[tr], ag[tr], bins[tr], zz[tr]
        keep = np.isin(atr, agents)
        Xtr, atr, btr, ztr = Xtr[keep], atr[keep], btr[keep], ztr[keep]
        mu = np.stack([Xtr[atr == g].mean(0) for g in agents])
        amap = {g: i for i, g in enumerate(agents)}
        ai = np.array([amap[g] for g in atr])
        Rtr = Xtr - mu[ai]
        sd = np.sqrt((Rtr ** 2).mean(0)) + 1e-9
        # common profile chat:bins (agent-demeaned bin means, weighted-centred)
        chat_bins = np.zeros((len(BIN_NAMES), Xtr.shape[1]))
        for b in range(len(BIN_NAMES)):
            mb = btr == b
            if mb.sum() >= 5:
                chat_bins[b] = Rtr[mb].mean(0)
        chat_bins -= (np.bincount(btr, minlength=len(BIN_NAMES))[:, None] * chat_bins).sum(0) / len(btr)
        Xd_tr = Xtr - chat_bins[btr]
        mu_d = np.stack([Xd_tr[atr == g].mean(0) for g in agents])
        Rd = Xd_tr - mu_d[ai]
        sd_d = np.sqrt((Rd ** 2).mean(0)) + 1e-9
        lam = lam_msgs * max(float((ztr ** 2).mean()), 1e-9)
        bslope = np.stack([(Rd[atr == g] * ztr[atr == g, None]).sum(0) / ((ztr[atr == g] ** 2).sum() + lam)
                           for g in agents])
        # resid sd under the agent-specific model
        Ra = Rd - bslope[ai] * ztr[:, None]
        sd_a = np.sqrt((Ra ** 2).mean(0)) + 1e-9
        tidx = np.where(te & np.isin(ag, agents))[0]
        if len(tidx) == 0:
            continue
        for k in ks:
            for blk in _blocks(ag[tidx], a["t"][tidx], k):
                ix = tidx[blk]
                x = X0[ix]
                xd = x - chat_bins[bins[ix]]
                s_blind = (((x[:, None, :] - mu[None]) / sd) ** 2).sum(2).mean(0)
                s_det = (((xd[:, None, :] - mu_d[None]) / sd_d) ** 2).sum(2).mean(0)
                pred = mu_d[None] + bslope[None] * zz[ix][:, None, None]
                s_ag = (((xd[:, None, :] - pred) / sd_a) ** 2).sum(2).mean(0)
                res[k]["blind"].append(agents[np.argmin(s_blind)])
                res[k]["det"].append(agents[np.argmin(s_det)])
                res[k]["agent"].append(agents[np.argmin(s_ag)])
                res[k]["truth"].append(ag[ix[0]])
    out = {}
    for k in ks:
        tr_ = np.array(res[k]["truth"])
        if len(tr_) == 0:
            out[k] = None
            continue
        acc = {}
        for v in ("blind", "det", "agent"):
            pr = np.array(res[k][v])
            per = [np.mean(pr[tr_ == g] == g) for g in np.unique(tr_)]
            acc[v] = float(np.mean(per))
        out[k] = {"n_blocks": int(len(tr_)), "n_agents": int(len(np.unique(tr_))),
                  "chance": 1.0 / max(len(np.unique(a["agent"])), 1), **acc,
                  "gain_det": acc["det"] - acc["blind"], "gain_agent": acc["agent"] - acc["blind"]}
    return out


# ============================================================================================ O3 dispersion
def dispersion_slope(a: dict, n_boot: int = 200, seed: int = 1) -> dict:
    Y = a["X"] - a["X"].mean(0)
    _, _, _, R, _, _ = fit_r2(Y, [block_G(a), block_A(a), block_C(a), block_R(a)], return_resid=True)
    e2 = (R ** 2).sum(1)
    cu = a["cu"]
    if cu.sum() < 50:
        return {"n_cu": int(cu.sum()), "slope": np.nan}
    ag, z, e = a["agent"][cu], a["z"][cu], e2[cu]
    # within-agent demeaning
    zd, ed = z.copy(), e.copy()
    for g in np.unique(ag):
        ix = ag == g
        zd[ix] -= z[ix].mean(); ed[ix] -= e[ix].mean()
    slope = float((zd * ed).sum() / (zd ** 2).sum())
    rng = np.random.default_rng(seed)
    ags = np.unique(ag)
    bs = []
    for _ in range(n_boot):
        pick = rng.choice(ags, len(ags), replace=True)
        ix = np.concatenate([np.where(ag == g)[0] for g in pick])
        den = (zd[ix] ** 2).sum()
        if den > 0:
            bs.append((zd[ix] * ed[ix]).sum() / den)
    bs = np.array(bs)
    return {"n_cu": int(cu.sum()), "slope": slope, "slope_rel": slope / float(e.mean()),
            "lo": float(np.quantile(bs, 0.025)), "hi": float(np.quantile(bs, 0.975)),
            "p_le0": float((bs <= 0).mean())}


# ============================================================================================ NE41 pairs
def ne41_pairs(m: pl.DataFrame, include_holdout: bool = False) -> pl.DataFrame:
    """Consecutive eligible messages of one agent on one PT day (regime III), labelled by resets between their calls."""
    ct = (pl.scan_parquet(SH / "context_ledger_turns.parquet")
          .filter((pl.col("regime") == "III") & (pl.lit(include_holdout) | ~pl.col("holdout")))
          .select("turn_id", "agent", "reset_forced", "reset_consol", "reset_session").collect().sort("turn_id"))
    ct = ct.with_columns(
        pl.col("reset_forced").cast(pl.Int32).cum_sum().over("agent").alias("cf"),
        (pl.col("reset_consol") & ~pl.col("reset_forced")).cast(pl.Int32).cum_sum().over("agent").alias("cv"),
        (pl.col("reset_session") & ~pl.col("reset_consol")).cast(pl.Int32).cum_sum().over("agent").alias("cs"))
    mm = m.filter(pl.col("regime") == "III").with_row_index("i").sort("agent", "t")
    mm = mm.join(ct.select("turn_id", "cf", "cv", "cs"), on="turn_id", how="left")
    p = mm.with_columns(*[pl.col(c).shift(-1).over("agent", "pt_date").alias(c + "2")
                          for c in ("i", "t", "cf", "cv", "cs", "turn_id")]).filter(pl.col("i2").is_not_null())
    p = p.filter(pl.col("turn_id2") != pl.col("turn_id"))
    p = p.with_columns((pl.col("cf2") - pl.col("cf")).alias("nf"), (pl.col("cv2") - pl.col("cv")).alias("nv"),
                       (pl.col("cs2") - pl.col("cs")).alias("ns"),
                       ((pl.col("t2") - pl.col("t")).dt.total_milliseconds() / 1000.0).alias("gap_s"))
    p = p.with_columns(pl.when((pl.col("nf") == 0) & (pl.col("nv") == 0) & (pl.col("ns") == 0)).then(pl.lit("within"))
                       .when((pl.col("nf") == 1) & (pl.col("nv") == 0) & (pl.col("ns") == 0)).then(pl.lit("forced"))
                       .when((pl.col("nf") == 0) & (pl.col("nv") == 1) & (pl.col("ns") == 0)).then(pl.lit("voluntary"))
                       .otherwise(pl.lit("other")).alias("label"))
    return p.select("i", "i2", "agent", "pt_date", "unit_id", "gap_s", "label")


def ne41_fit(a: dict, pairs: pl.DataFrame, n_boot: int = 300, seed: int = 2, xs: np.ndarray | None = None) -> dict:
    """Fit the context profile on within pairs only (differences), predict forced/voluntary jumps."""
    X = a["X"] if xs is None else xs
    i1, i2 = pairs["i"].to_numpy(), pairs["i2"].to_numpy()
    lab = pairs["label"].to_numpy()
    ag = pairs["agent"].to_numpy()
    nb = len(BIN_NAMES)
    Db = np.zeros((len(i1), nb))
    Db[np.arange(len(i1)), a["bin"][i2]] += 1
    Db[np.arange(len(i1)), a["bin"][i1]] -= 1
    Db = np.delete(Db, [0, REF_BIN], axis=1)               # no chat in regime III; reference bin
    agents = np.unique(ag)
    amap = {g: j for j, g in enumerate(agents)}
    aj = np.array([amap[g] for g in ag])
    dz = a["z"][i2] - a["z"][i1]
    Dz = np.zeros((len(i1), len(agents)))
    Dz[np.arange(len(i1)), aj] = dz
    Dh = hour_basis(a["hours"][i2]) - hour_basis(a["hours"][i1])
    dX = X[i2] - X[i1]
    W = lab == "within"
    Xd = np.column_stack([np.ones(len(i1)), Dh, Db, Dz])
    nh = 1 + Dh.shape[1]
    # Amendment A1 (synthetic): 2-fold cross-fitting by PT day, so that no fitted within pair shares an endpoint
    # message with an evaluated pair (shared endpoints biased beta to +0.29 under the null).
    days = pairs["pt_date"].to_numpy()
    ud = np.unique(days)
    fold = np.isin(days, ud[::2]).astype(int)
    pred_ctx = np.zeros_like(dX)
    nuis = np.zeros_like(dX)
    for f in (0, 1):
        fit = W & (fold != f)
        B, *_ = np.linalg.lstsq(Xd[fit], dX[fit], rcond=None)
        ev = fold == f
        pred_ctx[ev] = Xd[ev, nh:] @ B[nh:]                 # context-only predicted jump (out of fold)
        nuis[ev] = Xd[ev, :nh] @ B[:nh]
    obs = dX - nuis
    out = {"n_within": int(W.sum())}
    rng = np.random.default_rng(seed)
    for L in ("forced", "voluntary"):
        F = lab == L
        if F.sum() < 20:
            continue
        num = (obs[F] * pred_ctx[F]).sum(1)
        den = (pred_ctx[F] ** 2).sum(1)
        beta = float(num.sum() / den.sum())
        agF = ag[F]
        ags = np.unique(agF)
        bs = []
        for _ in range(n_boot):
            pick = rng.choice(ags, len(ags), replace=True)
            ix = np.concatenate([np.where(agF == g)[0] for g in pick])
            bs.append(num[ix].sum() / den[ix].sum())
        out[L] = {"n": int(F.sum()), "beta": beta, "lo": float(np.quantile(bs, 0.025)),
                  "hi": float(np.quantile(bs, 0.975)), "pred_norm2": float(den.mean()),
                  "obs_norm2": float((obs[F] ** 2).sum(1).mean())}
    # gap-matched percentiles before / after removing the predicted context jump
    gbin = np.floor(np.log10(np.maximum(pairs["gap_s"].to_numpy(), 1.0)) / 0.05).astype(int)
    d_raw = (dX ** 2).sum(1)
    d_cor = ((dX - pred_ctx) ** 2).sum(1)
    for L in ("forced", "voluntary"):
        if L not in out:
            continue
        for nm, d in (("T_raw", d_raw), ("T_corr", d_cor)):
            pct, agp = [], []
            key_w = {}
            for j in np.where(W)[0]:
                key_w.setdefault((ag[j], gbin[j]), []).append(d[j])
            for j in np.where(lab == L)[0]:
                ref = key_w.get((ag[j], gbin[j]))
                if ref is None or len(ref) < 5:
                    continue
                ref = np.asarray(ref)
                pct.append(((ref < d[j]).sum() + 0.5 * (ref == d[j]).sum()) / len(ref))
                agp.append(ag[j])
            pct, agp = np.array(pct), np.array(agp)
            if len(pct) < 20:
                continue
            ags = np.unique(agp)
            bs = []
            for _ in range(n_boot):
                pick = rng.choice(ags, len(ags), replace=True)
                bs.append(np.concatenate([pct[agp == g] for g in pick]).mean())
            out[L][nm] = {"T": float(pct.mean()), "lo": float(np.quantile(bs, 0.025)),
                          "hi": float(np.quantile(bs, 0.975)), "n": int(len(pct))}
    return out
