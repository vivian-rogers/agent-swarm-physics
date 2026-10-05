"""H73 round 2 estimators: conversation-state decomposition, read vs in-flight style accommodation, register transients
(split-half shift norms, exponential decay fit) and reset-and-hold segment statistics.

Every estimator takes a deviation/style matrix and schedule arrays, so the synthetic worlds (r2_synthetic.py) and the
real run (r2_run.py) share the code. No text; non-reserved rows only (asserted at load).
"""
from __future__ import annotations
import os
for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "2"
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h73lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra" / "shared"))
from common import holdout_mask  # noqa: E402

R2 = L.DATA / "r2"
TC = L.TC
TC16 = [f for f in TC if f != "at"]
CLIP = 3.0
LAG_EDGES = [0, 10, 20, 40, 80, 160]
AGE_EDGES = [0, 60, 300, 1800, np.inf]
DENS_EDGES = [0, 2, 5, np.inf]       # 1-2, 3-5, 6+


# ============================================================================================ data
def load() -> tuple[pl.DataFrame, pl.DataFrame]:
    """Eligible messages (main & ~copy) with round-1 style and round-2 state; source pairs restricted to them."""
    st = pl.read_parquet(L.DATA / "messages.parquet",
                         columns=["message_id", "srow", "register", "debate", "role", "role_class", "hours"]
                         + [f"tc_{f}" for f in TC])
    m = pl.read_parquet(R2 / "messages_r2.parquet").filter(pl.col("main") & ~pl.col("copy"))
    m = m.join(st, on="message_id", how="inner").sort("agent", "t")
    assert not any(holdout_mask(m["pt_date"].to_list(), m["goal_no"].to_list()))
    m = m.with_row_index("row")
    P = pl.read_parquet(R2 / "src_pairs.parquet").filter(pl.col("cls") != "mismatch")
    rowmap = m.select(pl.col("message_id"), pl.col("row"))
    P = (P.join(rowmap.rename({"message_id": "B_id", "row": "B_row"}), on="B_id", how="inner")
         .join(rowmap.rename({"message_id": "A_id", "row": "A_row"}), on="A_id", how="inner"))
    return m, P


def deviations(X: np.ndarray, agent: np.ndarray, unit: np.ndarray, clip: float | None = CLIP) -> np.ndarray:
    key = np.array([f"{a}|{u}" for a, u in zip(agent, unit)])
    _, inv = np.unique(key, return_inverse=True)
    k = inv.max() + 1
    S = np.zeros((k, X.shape[1]))
    np.add.at(S, inv, X)
    mu = S / np.bincount(inv, minlength=k)[:, None]
    D = X - mu[inv]
    return np.clip(D, -clip, clip) if clip else D


# ============================================================================================ R2-1b accommodation
CA_EDGES = [0, 10, 20, 40, 80, 160]
U_MAX = float(os.environ.get("H73_UMAX", "60"))


DC_EDGES = [-60, -20, 0, 10, 20, 40, 80, 160, 300]


def pair_cells(P: pl.DataFrame, design: str = "lag", caA: np.ndarray | None = None) -> np.ndarray:
    """design 'lag' (pre-registered): lag x before-age x density cells.
    design 'boundary' (Amendment R2-A1): B's call-age x before-age x density cells, pairs with |u| <= U_MAX where
    u = lag - call age = t_call(B) - t_A (u > 0 read, u < 0 in flight)."""
    lag = P["lag_s"].to_numpy()
    age = P["before_age_s"].to_numpy()
    den = P["density"].to_numpy()
    if design == "withinB":
        ca = P["call_age_s"].to_numpy()
        u = lag - ca
        ok = np.abs(u) <= U_MAX
        return np.where(ok, P["B_row"].to_numpy().astype(np.int64), -1)
    if design == "ctx":
        ca = P["call_age_s"].to_numpy()
        u = lag - ca
        dc = u + caA                                   # t_call(B) - t_call(A): context-time gap
        cb = np.searchsorted(CA_EDGES, ca, side="right") - 1
        cab = np.searchsorted(CA_EDGES, caA, side="right") - 1
        dcb = np.searchsorted(DC_EDGES, dc, side="right") - 1
        ab = np.searchsorted(AGE_EDGES, age, side="right") - 1
        db = np.searchsorted(DENS_EDGES, np.maximum(den, 1), side="left") - 1
        ok = ((ca >= 0) & (ca < CA_EDGES[-1]) & (caA >= 0) & (caA < CA_EDGES[-1]) & (dc >= DC_EDGES[0])
              & (dc < DC_EDGES[-1]) & (np.abs(u) <= U_MAX))
        return np.where(ok, (((cb * 10 + cab) * 10 + dcb) * 10 + ab) * 10 + db, -1)
    if design == "boundary":
        ca = P["call_age_s"].to_numpy()
        u = lag - ca
        cb = np.searchsorted(CA_EDGES, ca, side="right") - 1
        ab = np.searchsorted(AGE_EDGES, age, side="right") - 1
        db = np.searchsorted(DENS_EDGES, np.maximum(den, 1), side="left") - 1
        ok = (ca >= 0) & (ca < CA_EDGES[-1]) & (np.abs(u) <= U_MAX)
        return np.where(ok, cb * 100 + ab * 10 + db, -1)
    lb = np.searchsorted(LAG_EDGES, lag, side="right") - 1
    ab = np.searchsorted(AGE_EDGES, age, side="right") - 1
    db = np.searchsorted(DENS_EDGES, np.maximum(den, 1), side="left") - 1
    ok = (lag >= 0) & (lag < LAG_EDGES[-1])
    cell = np.where(ok, lb * 100 + ab * 10 + db, -1)
    return cell


class AccData:
    """Pair-level arrays for one population (e.g. regime III, uncertain dropped)."""

    def __init__(self, P: pl.DataFrame, design: str = "lag", m: pl.DataFrame | None = None):
        self.P = P
        self.design = design
        caA = None
        if m is not None:
            tt = m["t"].dt.epoch("us").to_numpy() / 1e6
            tc = m["t_call"].fill_null(m["t"]).dt.epoch("us").to_numpy() / 1e6
            caA = (tt - tc)[P["A_row"].to_numpy()]
        self.b = P["B_row"].to_numpy()
        self.a = P["A_row"].to_numpy()
        self.read = (P["cls"] == "read").to_numpy()
        self.cell = pair_cells(P, design, caA)
        self.unit = P["unit_id"].to_numpy()
        blk = (P["unit_id"] + "|" + P["pt_date"] + "|" + P["hour"].cast(pl.String)).to_numpy()
        _, self.blk = np.unique(blk, return_inverse=True)
        self.u = (P["lag_s"] - P["call_age_s"]).to_numpy().astype(float)
        self.named = P["named"].to_numpy()
        self.parent = P["parentAB"].to_numpy()


def _unit_tables(y, s2, read, cell, blk, sel):
    """Per (block, cell) sums for read and in-flight; returns compact arrays."""
    ix = np.where(sel & (cell >= 0))[0]
    if len(ix) == 0:
        return None
    _, ci = np.unique(cell[ix], return_inverse=True)
    ub, bi = np.unique(blk[ix], return_inverse=True)
    nc, nb = ci.max() + 1, len(ub)
    r = read[ix]
    T = {}
    for nm, msk in (("r", r), ("i", ~r)):
        Sy = np.zeros((nb, nc)); N = np.zeros((nb, nc)); Ss = np.zeros((nb, nc))
        np.add.at(Sy, (bi[msk], ci[msk]), y[ix][msk])
        np.add.at(N, (bi[msk], ci[msk]), 1.0)
        np.add.at(Ss, (bi[msk], ci[msk]), s2[ix][msk])
        T[nm] = (Sy, N, Ss)
    return T


def _J_from(T, wb=None):
    Syr, Nr, Ssr = T["r"]; Syi, Ni, _ = T["i"]
    if wb is not None:
        Syr, Nr, Ssr, Syi, Ni = (wb @ Syr, wb @ Nr, wb @ Ssr, wb @ Syi, wb @ Ni)
    else:
        Syr, Nr, Ssr, Syi, Ni = Syr.sum(0), Nr.sum(0), Ssr.sum(0), Syi.sum(0), Ni.sum(0)
    ok = (Nr > 0) & (Ni > 0)
    if not ok.any():
        return np.nan, np.nan, 0.0, 0, 0, np.nan
    w = Nr[ok] * Ni[ok] / (Nr[ok] + Ni[ok])
    dif = Syr[ok] / Nr[ok] - Syi[ok] / Ni[ok]
    J = float((w * dif).sum() / w.sum())
    s2 = float(Ssr[ok].sum() / Nr[ok].sum())
    lvl_i = float((w * Syi[ok] / Ni[ok]).sum() / w.sum())
    return J, s2, float(w.sum()), int(Nr[ok].sum()), int(Ni[ok].sum()), lvl_i


def accommodation(D: np.ndarray, A: AccData, sel: np.ndarray | None = None, n_boot: int = 400, seed: int = 0,
                  min_pairs: int = 200, units_keep: list | None = None, Dfull: np.ndarray | None = None,
                  change_prev: np.ndarray | None = None) -> dict:
    """Pooled read minus in-flight alignment J and accommodation coefficient gamma = J / s2_A.

    D: deviations used for the outcome (rows = eligible messages). change_prev: optional row index of B's previous
    message for the change-score outcome (y = <d_B - d_prev, d_A>/D)."""
    dim = D.shape[1]
    dB = D[A.b] if change_prev is None else D[A.b] - D[change_prev[A.b]]
    y = (dB * D[A.a]).sum(1) / dim
    s2 = (D[A.a] ** 2).sum(1) / dim
    sel = np.ones(len(y), bool) if sel is None else sel
    if change_prev is not None:
        sel = sel & (change_prev[A.b] >= 0)
    units = np.unique(A.unit[sel]) if units_keep is None else np.array(units_keep)
    res, tabs = {}, {}
    for u in units:
        T = _unit_tables(y, s2, A.read, A.cell, A.blk, sel & (A.unit == u))
        if T is None:
            continue
        J, s2u, W, nr, ni, lvl = _J_from(T)
        if units_keep is None and (nr < min_pairs or ni < min_pairs):
            continue
        if not np.isfinite(J):
            continue
        res[u] = {"J": J, "gamma": J / s2u, "s2A": s2u, "W": W, "n_read": nr, "n_inflight": ni, "level_inflight": lvl}
        tabs[u] = T
    if not res:
        return {"units": {}, "pooled": None}
    rng = np.random.default_rng(seed)
    draws = {u: [] for u in res}
    for u, T in tabs.items():
        nb = T["r"][0].shape[0]
        for _ in range(n_boot):
            wb = rng.multinomial(nb, np.full(nb, 1.0 / nb)).astype(float)
            J, s2u, *_ = _J_from(T, wb)
            draws[u].append(J / s2u if np.isfinite(J) else np.nan)
        dr = np.array(draws[u])
        res[u]["lo"], res[u]["hi"] = (float(np.nanquantile(dr, 0.025)), float(np.nanquantile(dr, 0.975)))
    W = np.array([res[u]["W"] for u in res])
    G = np.array([res[u]["gamma"] for u in res])
    Jv = np.array([res[u]["J"] for u in res])
    Dr = np.array([draws[u] for u in res])            # units x draws
    pooled_draws = np.nansum(Dr * W[:, None], 0) / W.sum()
    pooled = {"gamma": float((G * W).sum() / W.sum()), "J": float((Jv * W).sum() / W.sum()),
              "lo": float(np.quantile(pooled_draws, 0.025)), "hi": float(np.quantile(pooled_draws, 0.975)),
              "n_units": int(len(res)), "n_read": int(sum(res[u]["n_read"] for u in res)),
              "n_inflight": int(sum(res[u]["n_inflight"] for u in res)),
              "level_inflight": float(np.array([res[u]["level_inflight"] for u in res]) @ W / W.sum()),
              "s2A": float(np.array([res[u]["s2A"] for u in res]) @ W / W.sum())}
    return {"units": res, "pooled": pooled, "draws": pooled_draws}


# ============================================================================================ R2-3 reset-and-hold
def rh_pairs(m: pl.DataFrame, regimes: list[str], max_lag: int = 4) -> dict:
    """Consecutive (lag l) eligible computer-use message pairs of one agent on one PT day, labelled by resets between."""
    cu = m.filter(pl.col("regime").is_in(regimes) & (pl.col("ctx_mode") == "cu")).sort("agent", "t")
    row = cu["row"].to_numpy(); ag = cu["agent"].to_numpy(); day = cu["pt_date"].to_numpy()
    seg = cu["seg"].to_numpy(); segk = cu["seg_k"].to_numpy(); t = cu["t"].dt.epoch("us").to_numpy()
    unit = cu["unit_id"].to_numpy()
    out = {"a": [], "b": [], "lag": [], "nres": [], "gap": [], "k1": [], "agent": [], "unit": []}
    for l in range(1, max_lag + 1):
        ok = np.zeros(len(row), bool)
        ok[:-l] = (ag[:-l] == ag[l:]) & (day[:-l] == day[l:])
        i = np.where(ok)[0]; j = i + l
        out["a"].append(row[i]); out["b"].append(row[j]); out["lag"].append(np.full(len(i), l))
        out["nres"].append(seg[j] - seg[i]); out["gap"].append((t[j] - t[i]) / 1e6)
        out["k1"].append(segk[i]); out["agent"].append(ag[i]); out["unit"].append(unit[i])
    o = {k: np.concatenate(v) for k, v in out.items()}
    o["gbin"] = np.floor(np.log10(np.maximum(o["gap"], 1.0)) / 0.1).astype(int)
    o["gbin5"] = np.floor(np.log10(np.maximum(o["gap"], 1.0)) / 0.05).astype(int)
    # segments for the growth statistic and the common profile
    o["seg_rows"] = cu.select("row", "agent", "seg", "seg_k", "unit_id").to_dict(as_series=False)
    return o


def _cw(y, n, wmask, amask, gb):
    """Within mean reweighted to the across gap distribution (bins with both)."""
    ga = np.bincount(gb[amask], minlength=gb.max() + 1).astype(float)
    nw = np.bincount(gb[wmask], weights=n[wmask], minlength=gb.max() + 1)
    sw = np.bincount(gb[wmask], weights=(y * n)[wmask], minlength=gb.max() + 1)
    ok = (ga > 0) & (nw > 0)
    if not ok.any():
        return np.nan
    return float((ga[ok] * sw[ok] / nw[ok]).sum() / ga[ok].sum())


def rh_stats(D: np.ndarray, R: dict, n_boot: int = 500, seed: int = 3, scaled_T: bool = True) -> dict:
    dim = D.shape[1]
    a, b = R["a"], R["b"]
    y = (D[a] * D[b]).sum(1) / dim
    dist = ((D[a] - D[b]) ** 2).sum(1) / dim
    lag, nres, k1, gb = R["lag"], R["nres"], R["k1"], R["gbin"] - R["gbin"].min()
    ag = R["agent"]
    sr = R["seg_rows"]
    srow, sag, sseg, sk = (np.array(sr["row"]), np.array(sr["agent"]), np.array(sr["seg"]), np.array(sr["seg_k"]))
    Vbar_all = (D[srow] ** 2).sum(1) / dim
    agents = np.unique(ag)

    def compute(wts_pair, wts_msg):
        n = wts_pair
        res = {}
        acr1 = (lag == 1) & (nres == 1) & (n > 0)
        C_acr = float((y * n)[acr1].sum() / n[acr1].sum()) if acr1.any() else np.nan
        for l in (1, 2, 3):
            w = (lag == l) & (nres == 0) & (n > 0)
            ac = (lag == l) & (nres == 1) & (n > 0)
            if w.any() and ac.any():
                res[f"dC{l}"] = _cw(y, n, w, ac, gb) - float((y * n)[ac].sum() / n[ac].sum())
            else:
                res[f"dC{l}"] = np.nan
        w1 = (lag == 1) & (nres == 0) & (n > 0)
        res["dC_first"] = _cw(y, n, w1 & (k1 == 1), acr1, gb) - C_acr
        res["dC_late"] = _cw(y, n, w1 & (k1 >= 3), acr1, gb) - C_acr
        acr2 = (lag == 1) & (nres == 2) & (n > 0)
        if acr2.any():
            ga = np.bincount(gb[acr1], minlength=gb.max() + 1).astype(float)
            n2 = np.bincount(gb[acr2], weights=n[acr2], minlength=gb.max() + 1)
            s2 = np.bincount(gb[acr2], weights=(y * n)[acr2], minlength=gb.max() + 1)
            ok = (ga > 0) & (n2 > 0)
            C2 = float((ga[ok] * s2[ok] / n2[ok]).sum() / ga[ok].sum()) if ok.any() else np.nan
            ga_ok = ok
            # C_across,1 restricted to the same bins
            s1 = np.bincount(gb[acr1], weights=(y * n)[acr1], minlength=gb.max() + 1)
            n1 = np.bincount(gb[acr1], weights=n[acr1], minlength=gb.max() + 1)
            C1 = float((ga[ga_ok] * s1[ga_ok] / n1[ga_ok]).sum() / ga[ga_ok].sum()) if ga_ok.any() else np.nan
            res["carry"] = (C1 - C2) / res["dC1"] if res["dC1"] and np.isfinite(res["dC1"]) else np.nan
            res["C_acr1_minus_acr2"] = C1 - C2
        else:
            res["carry"] = np.nan
        vb = float((Vbar_all * wts_msg).sum() / wts_msg.sum())
        res["Vbar"] = vb
        res["kappa_seg"] = res["dC1"] / vb if np.isfinite(res["dC1"]) else np.nan
        res["r_first_late"] = res["dC_first"] / res["dC_late"] if res["dC_late"] else np.nan
        res["r_dC3_dC1"] = res["dC3"] / res["dC1"] if res["dC1"] else np.nan
        # growth: d_k - d_1 within segments, k = 2..8
        dk = Vbar_all
        key = sag.astype(np.int64) * 10_000_000 + sseg
        first = {}
        for i in np.where(sk == 1)[0]:
            first[key[i]] = dk[i]
        gsum, gn = 0.0, 0.0
        for i in np.where((sk >= 2) & (sk <= 8))[0]:
            f = first.get(key[i])
            if f is not None and wts_msg[i] > 0:
                gsum += (dk[i] - f) * wts_msg[i]; gn += wts_msg[i]
        res["growth"] = gsum / gn if gn else np.nan
        return res

    base = compute(np.ones(len(y)), np.ones(len(srow)))
    # common profile: split-half mean first-message deviation (point only)
    rng = np.random.default_rng(seed)
    fm = srow[sk == 1]
    vals = []
    for _ in range(20):
        h = rng.random(len(fm)) < 0.5
        vals.append(float(D[fm[h]].mean(0) @ D[fm[~h]].mean(0)) / dim)
    base["common_profile"] = float(np.mean(vals))
    base["common_share"] = base["common_profile"] / base["dC1"] if base["dC1"] else np.nan
    # scaled percentile T of one-reset pairs among within pairs at matched 0.05-decade gaps
    base.update(scaled_T_stat(dist, R, n_boot=n_boot, seed=seed, scaled=scaled_T))
    # agent-cluster bootstrap
    apos = {g: np.where(ag == g)[0] for g in agents}
    mpos = {g: np.where(sag == g)[0] for g in agents}
    keys = ["dC1", "dC2", "dC3", "dC_first", "dC_late", "carry", "kappa_seg", "r_first_late", "r_dC3_dC1", "growth"]
    bs = {k: [] for k in keys}
    for _ in range(n_boot):
        pick = rng.choice(agents, len(agents), replace=True)
        cnt = {g: 0 for g in agents}
        for g in pick:
            cnt[g] += 1
        wp = np.zeros(len(y)); wm = np.zeros(len(srow))
        for g, c in cnt.items():
            if c:
                wp[apos[g]] = c; wm[mpos[g]] = c
        r = compute(wp, wm)
        for k in keys:
            bs[k].append(r.get(k, np.nan))
    for k in keys:
        arr = np.array(bs[k], dtype=float)
        arr = arr[np.isfinite(arr)]
        base[k + "_ci"] = [float(np.quantile(arr, 0.025)), float(np.quantile(arr, 0.975))] if len(arr) > 20 else [np.nan, np.nan]
    base["n_within1"] = int(((lag == 1) & (nres == 0)).sum())
    base["n_across1"] = int(((lag == 1) & (nres == 1)).sum())
    base["n_across2"] = int(((lag == 1) & (nres == 2)).sum())
    base["n_first"] = int(((lag == 1) & (nres == 0) & (k1 == 1)).sum())
    base["n_agents"] = int(len(agents))
    return base


def scaled_T_stat(dist, R, n_boot=500, seed=4, scaled=True, labels=None, min_ref=5) -> dict:
    """Percentile of across-one-reset (or labelled) pairs among same-agent within pairs at matched 0.05-decade gaps
    (agent-free cell if < min_ref), distances divided by the agent x unit median within-pair distance (H46 R2-A5)."""
    lag, nres, ag, un, g5 = R["lag"], R["nres"], R["agent"], R["unit"], R["gbin5"]
    l1 = lag == 1
    W = l1 & (nres == 0)
    F = l1 & (nres == 1) if labels is None else labels
    d = dist.copy()
    if scaled:
        key = np.array([f"{a}|{u}" for a, u in zip(ag, un)])
        med = {}
        for k in np.unique(key[W]):
            med[k] = np.median(d[W & (key == k)])
        sc = np.array([med.get(k, np.nan) for k in key])
        d = d / sc
    okd = np.isfinite(d)
    refA, refG = {}, {}
    for j in np.where(W & okd)[0]:
        refA.setdefault((ag[j], g5[j]), []).append(d[j]); refG.setdefault(g5[j], []).append(d[j])
    refA = {k: np.sort(v) for k, v in refA.items()}
    refG = {k: np.sort(v) for k, v in refG.items()}
    pct, agp, own = [], [], []
    for j in np.where(F & okd)[0]:
        ref = refA.get((ag[j], g5[j]))
        o = True
        if ref is None or len(ref) < min_ref:
            ref = refG.get(g5[j]); o = False
        if ref is None or len(ref) < min_ref:
            continue
        lo_, hi_ = np.searchsorted(ref, d[j], "left"), np.searchsorted(ref, d[j], "right")
        pct.append((lo_ + 0.5 * (hi_ - lo_)) / len(ref)); agp.append(ag[j]); own.append(o)
    pct, agp = np.array(pct), np.array(agp)
    if len(pct) < 20:
        return {"T": np.nan, "T_ci": [np.nan, np.nan], "T_n": int(len(pct))}
    rng = np.random.default_rng(seed)
    ags = np.unique(agp)
    pos = {g: np.where(agp == g)[0] for g in ags}
    bs = []
    for _ in range(n_boot):
        pick = rng.choice(ags, len(ags), replace=True)
        bs.append(np.concatenate([pct[pos[g]] for g in pick]).mean())
    return {"T": float(pct.mean()), "T_ci": [float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))],
            "T_n": int(len(pct)), "T_share_own_agent": float(np.mean(own))}


# ============================================================================================ R2-2 transients
def split_half_shift(Xi: np.ndarray, Xo: np.ndarray, oi: np.ndarray, rng, n_split: int = 20) -> float:
    """Unbiased squared shift norm / D: s = mean(Xi) - mean over comparison agents of their means (Xo rows with agent
    labels oi); both sides split at random into halves; returns mean <s1, s2>/D over n_split splits."""
    dim = Xi.shape[1]
    if len(Xi) < 2:
        return np.nan
    vals = []
    ua = np.unique(oi) if len(oi) else np.array([])
    for _ in range(n_split):
        hi_ = rng.random(len(Xi)) < 0.5
        if hi_.sum() == 0 or (~hi_).sum() == 0:
            continue
        ho = rng.random(len(Xo)) < 0.5 if len(Xo) else np.zeros(0, bool)
        s = []
        for h, hoh in ((hi_, ho), (~hi_, ~ho)):
            si = Xi[h].mean(0)
            if len(ua):
                ms = [Xo[hoh & (oi == g)].mean(0) for g in ua if (hoh & (oi == g)).sum() > 0]
                so = np.mean(ms, axis=0) if ms else np.zeros(dim)
            else:
                so = np.zeros(dim)
            s.append(si - so)
        vals.append(float(s[0] @ s[1]) / dim)
    return float(np.mean(vals)) if vals else np.nan


def fit_decay(k: np.ndarray, S: np.ndarray, w: np.ndarray, taus=None) -> dict:
    """S(k) = S_inf + A exp(-k/tau), weighted least squares, tau on a grid."""
    taus = np.geomspace(0.25, 60, 80) if taus is None else taus
    ok = np.isfinite(S) & (w > 0)
    k, S, w = k[ok], S[ok], w[ok]
    best = None
    for tau in taus:
        X = np.column_stack([np.ones(len(k)), np.exp(-k / tau)])
        Wh = np.sqrt(w)
        B, *_ = np.linalg.lstsq(X * Wh[:, None], S * Wh, rcond=None)
        rss = float((w * (S - X @ B) ** 2).sum())
        if best is None or rss < best[0]:
            best = (rss, tau, B)
    return {"tau": float(best[1]), "S_inf": float(best[2][0]), "A": float(best[2][1]), "rss": best[0]}


# ============================================================================================ R2-1a conversation state
def cv_block(m: pl.DataFrame) -> np.ndarray:
    """Conversation-state block Cv (columns centred)."""
    cu = (m["ctx_mode"] == "cu").to_numpy()
    kst = np.log2(1 + m["k_since_talk"].fill_null(0).to_numpy().astype(float))
    kctx = np.where(cu, np.log2(1 + m["k_ctx"].fill_null(0).to_numpy().astype(float)), 0.0)
    pm = m["pend_ment"].fill_null(0).to_numpy()
    pn = m["pend_nudge"].fill_null(0).to_numpy()
    td = m["thread_depth"].to_numpy()
    cols = [kst, kctx, (pm == 1).astype(float), (pm >= 2).astype(float), (pn >= 1).astype(float),
            (td == 1).astype(float), (td == 2).astype(float), (td >= 3).astype(float)]
    C = np.column_stack(cols)
    C = C[:, C.std(0) > 0]
    return C - C.mean(0)


def decompose_cv(a: dict, Cv: np.ndarray, n_perm: int = 100, seed: int = 0) -> dict:
    """Unique shares of fill (Cf) and conversation state (Cv) beyond G (+ mode level), A, R; Cv permutation null."""
    Y = a["X"] - a["X"].mean(0)
    mode = a["cu"].astype(float)[:, None]
    G = [L.block_G(a)] + ([mode] if 0 < mode.mean() < 1 else [])
    A, Cf, R = L.block_A(a), L.block_C(a), L.block_R(a)
    full = L.fit_r2(Y, G + [A, Cf, Cv, R])[1]
    noCv = L.fit_r2(Y, G + [A, Cf, R])[1]
    noCf = L.fit_r2(Y, G + [A, Cv, R])[1]
    rG = L.fit_r2(Y, G)[1]
    kappa, _ = L.cell_ceiling(Y, a)
    den = kappa - rG
    out = {"u_Cf": (full - noCf) / den, "u_Cv": (full - noCv) / den, "kappa": kappa, "r2G": rG, "n": int(len(Y)),
           "n_cu": int(a["cu"].sum())}
    if n_perm:
        rng = np.random.default_rng(seed)
        grp = np.array([f"{g}|{d}" for g, d in zip(a["agent"], a["day"])])
        obs = full - noCv
        null = []
        for _ in range(n_perm):
            pi = L.permute_within(grp, rng)
            null.append(L.fit_r2(Y, G + [A, Cf, Cv[pi], R])[1] - noCv)
        null = np.array(null)
        out["p_Cv"] = float((1 + (null >= obs).sum()) / (1 + n_perm))
        out["u_Cv_nullcorr"] = (obs - float(np.median(null))) / den
    return out


# ============================================================================================ R2-2 event-study helpers
def onset_series(X: np.ndarray, agent: np.ndarray, day: np.ndarray, focus: list, comp: list, pre_days, post_days,
                 rng, onset: str, min_msgs: int = 4, n_split: int = 10) -> dict:
    """Daily split-half shift norms S_i(k) of focus agents relative to their pre mean, minus the comparison agents'
    mean shift (difference-in-differences). Every message (pre and post) is split at random into halves; the pre means
    are computed within each half, so no estimation error is shared by the two halves (unbiased S).
    Returns {agent: (k array, S array, n array)}."""
    import datetime as _dt
    dim = X.shape[1]
    pre = np.isin(day, list(pre_days))
    post_days = sorted(post_days)
    d0 = _dt.date.fromisoformat(onset)
    kday = {d: (_dt.date.fromisoformat(d) - d0).days for d in post_days}
    agents = sorted(set(focus) | set(comp))
    # message index sets
    pre_ix = {g: np.where(pre & (agent == g))[0] for g in agents}
    okag = [g for g in agents if len(pre_ix[g]) >= 10]
    post_ix = {(g, d): np.where((day == d) & (agent == g))[0] for g in okag for d in post_days}
    acc = {g: {d: [] for d in post_days} for g in focus if g in okag}
    for _ in range(n_split):
        h = rng.random(len(X)) < 0.5
        q = {g: (X[pre_ix[g][h[pre_ix[g]]]].mean(0), X[pre_ix[g][~h[pre_ix[g]]]].mean(0)) for g in okag}
        for d in post_days:
            # per-agent half shifts on day d
            sh = {}
            for g in okag:
                ix = post_ix[(g, d)]
                if len(ix) < 2:
                    continue
                a1, a0 = ix[h[ix]], ix[~h[ix]]
                if len(a1) == 0 or len(a0) == 0:
                    continue
                sh[g] = (X[a1].mean(0) - q[g][0], X[a0].mean(0) - q[g][1])
            for g in acc:
                if g not in sh or len(post_ix[(g, d)]) < min_msgs:
                    continue
                oth = [sh[c] for c in comp if c != g and c in sh]
                o1 = np.mean([o[0] for o in oth], axis=0) if oth else np.zeros(dim)
                o0 = np.mean([o[1] for o in oth], axis=0) if oth else np.zeros(dim)
                acc[g][d].append(float((sh[g][0] - o1) @ (sh[g][1] - o0)) / dim)
    out = {}
    for g, dd in acc.items():
        ks, Ss, ns = [], [], []
        for d in post_days:
            if dd[d]:
                ks.append(kday[d]); Ss.append(float(np.mean(dd[d]))); ns.append(int(len(post_ix[(g, d)])))
        out[g] = (np.array(ks), np.array(Ss), np.array(ns))
    return out


# ============================================================================================ R2-1b local-linear boundary
def _rd_tables(y, s2, read, u, cell, blk, sel):
    """Per (block, cell) sufficient statistics for y ~ cell FE + R + u*R + u*(1-R)."""
    ix = np.where(sel & (cell >= 0))[0]
    if len(ix) == 0:
        return None
    _, ci = np.unique(cell[ix], return_inverse=True)
    ub, bi = np.unique(blk[ix], return_inverse=True)
    nc, nb = ci.max() + 1, len(ub)
    r = read[ix].astype(float); uu = u[ix]
    Z = np.column_stack([r, uu * r, uu * (1 - r)])
    yy = y[ix]
    feats = [np.ones(len(ix))] + [Z[:, j] for j in range(3)] + [Z[:, j] * Z[:, k] for j in range(3) for k in range(j, 3)] \
        + [yy] + [Z[:, j] * yy for j in range(3)] + [r * s2[ix], r]
    F = np.column_stack(feats)          # 1 + 3 + 6 + 1 + 3 + 2 = 16
    T = np.zeros((nb, nc, F.shape[1]))
    np.add.at(T, (bi, ci), F)
    return T


def _rd_solve(T, wb=None):
    S = T.sum(0) if wb is None else np.tensordot(wb, T, axes=(0, 0))      # cells x 16
    n = S[:, 0]
    nr = S[:, 15]
    ok = (nr >= 2) & (n - nr >= 2)
    if not ok.any():
        return np.nan, np.nan, 0, 0
    S = S[ok]; n = n[ok]
    Sz = S[:, 1:4]
    idx = {}
    c = 4
    for j in range(3):
        for k in range(j, 3):
            idx[(j, k)] = c; idx[(k, j)] = c; c += 1
    Szz = np.zeros((3, 3)); Szy = np.zeros(3)
    for j in range(3):
        for k in range(3):
            Szz[j, k] = (S[:, idx[(j, k)]] - Sz[:, j] * Sz[:, k] / n).sum()
        Szy[j] = (S[:, 11 + j] - Sz[:, j] * S[:, 10] / n).sum()
    try:
        b = np.linalg.solve(Szz, Szy)
    except np.linalg.LinAlgError:
        return np.nan, np.nan, 0, 0
    s2 = S[:, 14].sum() / S[:, 15].sum()
    return float(b[0]), float(s2), int(S[:, 15].sum()), int((n - S[:, 15]).sum())


def accommodation_rd(D, A, sel=None, n_boot=400, seed=0, min_pairs=200, units_keep=None, change_prev=None) -> dict:
    """Local-linear jump at u = 0 (read side minus in-flight side) with cell fixed effects (Amendment R2-A1).
    gamma = jump / s2_A (share of a read item's deviation taken on per item)."""
    dim = D.shape[1]
    dB = D[A.b] if change_prev is None else D[A.b] - D[change_prev[A.b]]
    y = (dB * D[A.a]).sum(1) / dim
    s2 = (D[A.a] ** 2).sum(1) / dim
    sel = np.ones(len(y), bool) if sel is None else sel.copy()
    if change_prev is not None:
        sel &= change_prev[A.b] >= 0
    units = np.unique(A.unit[sel]) if units_keep is None else np.array(units_keep)
    res, tabs = {}, {}
    for un in units:
        T = _rd_tables(y, s2, A.read, A.u, A.cell, A.blk, sel & (A.unit == un))
        if T is None:
            continue
        J, s2u, nr, ni = _rd_solve(T)
        if (units_keep is None and (nr < min_pairs or ni < min_pairs)) or not np.isfinite(J):
            continue
        res[un] = {"J": J, "gamma": J / s2u, "s2A": s2u, "W": nr * ni / (nr + ni), "n_read": nr, "n_inflight": ni}
        tabs[un] = T
    if not res:
        return {"units": {}, "pooled": None}
    rng = np.random.default_rng(seed)
    draws = {}
    for un, T in tabs.items():
        nb = T.shape[0]
        dd = []
        for _ in range(n_boot):
            wb = rng.multinomial(nb, np.full(nb, 1.0 / nb)).astype(float)
            J, s2u, *_ = _rd_solve(T, wb)
            dd.append(J / s2u if np.isfinite(J) else np.nan)
        draws[un] = np.array(dd)
        res[un]["lo"], res[un]["hi"] = float(np.nanquantile(draws[un], 0.025)), float(np.nanquantile(draws[un], 0.975))
    W = np.array([res[k]["W"] for k in res]); G = np.array([res[k]["gamma"] for k in res])
    Dr = np.array([draws[k] for k in res])
    pd_ = np.nansum(Dr * W[:, None], 0) / W.sum()
    pooled = {"gamma": float((G * W).sum() / W.sum()), "lo": float(np.quantile(pd_, 0.025)),
              "hi": float(np.quantile(pd_, 0.975)), "n_units": len(res),
              "n_read": int(sum(res[k]["n_read"] for k in res)), "n_inflight": int(sum(res[k]["n_inflight"] for k in res)),
              "s2A": float(np.array([res[k]["s2A"] for k in res]) @ W / W.sum()), "level_inflight": np.nan}
    return {"units": res, "pooled": pooled, "draws": pd_}
