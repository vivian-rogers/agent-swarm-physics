"""H111 library: windowed talk counts, the collective Fano ratio Phi(T), its sum-rule prediction, nulls, bootstrap.

Phi(T) = Var(sum_i n_i) / sum_i Var(n_i) on T-minute windows, counts demeaned within (agent, day, 60-min block).
Phi_pred(g) = [N/(1-g)^2] / sum_b [1/(1-g)^2 + (n_b-1)/(1+g/(n_b-1))^2]  (mean-field linear Hawkes, rooms b).
Bootstrap: resample (day, 60-min block) cells; the same cell keys across T, so T-contrasts are joint.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import math  # noqa: E402
from dataclasses import dataclass  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data/processed/H111-talk-fano-sum-rule"
TS = (1, 2, 5, 10, 15, 20, 30)
T_STAR = 10
BLOCK_S = 3600.0
EXO_S = 900.0          # drop windows overlapping [t_h, t_h + 15 min)
KICK_S = 3600.0        # drop the kickoff day's first hour
MIN_DAY_S = 3600.0
CLOCK = "percall"        # wall | percall (residual of talk on own calls per window); set by the pipeline
EXO_RULE = "session10"    # msg15 (window overlaps [t_h, t_h + 15 min)) | session10 (human sessions, gaps <= 10 min,
                       # footprint [first, last + 10 min))


@dataclass
class Unit:
    uid: str
    days: pl.DataFrame
    present: pl.DataFrame
    msgs: pl.DataFrame
    calls: pl.DataFrame
    exo: pl.DataFrame


def load_unit(uid: str, base: Path = OUT) -> Unit:
    r = lambda s: pl.read_parquet(base / s / f"{uid}.parquet")  # noqa: E731
    return Unit(uid, r("days"), r("present"), r("msgs"), r("calls"), r("exo"))


# ============================================================================================ prediction
def phi_pred(g: float, sizes) -> float:
    """Mean-field linear-response collective Fano ratio for rooms of the given sizes."""
    sizes = [int(s) for s in sizes if s >= 1]
    N = sum(sizes)
    if N < 2 or not math.isfinite(g) or g >= 1:
        return float("nan")
    a = 1.0 / (1.0 - g) ** 2
    den = 0.0
    for n in sizes:
        den += a
        if n > 1:
            den += (n - 1) / (1.0 + g / (n - 1)) ** 2
    return N * a / den


# ============================================================================================ windows
def _day_frame(U: Unit, mode: str):
    """Yield (day, lo, hi, kickoff, agents, rooms) for the chosen time frame."""
    pres = U.present
    for r in U.days.sort("day").iter_rows(named=True):
        d = r["day"]
        if mode in ("trim", "cc", "exo_in", "talkcalls"):
            lo, hi = r["ap_lo"], r["ap_hi"]
        else:
            lo, hi = r["win_start"], r["win_end"]
        if lo is None or hi is None or hi - lo < MIN_DAY_S:
            continue
        p = pres.filter(pl.col("day") == d).sort("agent")
        if p.height < 2:
            continue
        rooms = p["room"].fill_null(-1).to_numpy()
        yield d, float(lo), float(hi), bool(r["kickoff_day"]), p["agent"].to_numpy(), rooms


def _bin(times: np.ndarray, aidx: np.ndarray, edges: np.ndarray, A: int) -> np.ndarray:
    W = len(edges) - 1
    n = np.zeros((W, A), np.int32)
    k = np.searchsorted(edges, times, side="right") - 1
    ok = (k >= 0) & (k < W) & (aidx >= 0)
    np.add.at(n, (k[ok], aidx[ok]), 1)
    return n


def build_days(U: Unit, T_min: float, mode: str = "trim", shift_rng=None, sim_msgs: pl.DataFrame | None = None,
               cc_K: int | None = None):
    """Per day: counts (W x A), block id per window, keep flag, rooms. mode in trim | untrim | raw | exo_in | cc |
    talkcalls. shift_rng: circularly shift each agent's events within the day frame (offset >= 60 min)."""
    msgs = sim_msgs if sim_msgs is not None else U.msgs
    if mode == "talkcalls":
        ev = U.calls.filter(pl.col("talk")).select(pl.col("t_first").alias("t"), "day", "agent")
    else:
        ev = msgs.select("t", "day", "agent")
    exo_t = np.sort(U.exo["t"].to_numpy()) if U.exo.height else np.zeros(0)
    if EXO_RULE == "session10" and len(exo_t):
        brk = np.flatnonzero(np.diff(exo_t) > 600.0)
        s0 = np.r_[exo_t[0], exo_t[brk + 1]]
        s1 = np.r_[exo_t[brk], exo_t[-1]] + 600.0
    else:
        s0, s1 = exo_t, exo_t + EXO_S
    out = []
    for d, lo, hi, kick, agents, rooms in _day_frame(U, mode):
        A = len(agents)
        amap = {int(a): i for i, a in enumerate(agents)}
        e = ev.filter((pl.col("day") == d) & (pl.col("t") >= lo) & (pl.col("t") < hi))
        t = e["t"].to_numpy().astype(np.float64)
        ai = np.array([amap.get(int(a), -1) for a in e["agent"].to_list()], dtype=np.int64)
        L = hi - lo
        off = None
        if shift_rng is not None:
            off = np.empty(A)
            for i in range(A):
                off[i] = shift_rng.uniform(BLOCK_S, L - BLOCK_S) if L > 2 * BLOCK_S + 60 else shift_rng.uniform(0, L)
            sel = ai >= 0
            t = t.copy()
            t[sel] = lo + np.mod(t[sel] - lo + off[ai[sel]], L)
        if mode == "cc":
            c = U.calls.filter((pl.col("day") == d) & (pl.col("t_call") >= lo) & (pl.col("t_call") <= hi)
                               & pl.col("agent").is_in(agents.tolist()))["t_call"].sort().to_numpy()
            K = cc_K or 100
            if len(c) < 2 * K:
                continue
            edges = c[::K]
            if len(edges) < 3:
                continue
            blk = np.arange(len(edges) - 1) // 4
            starts = edges[:-1]
        else:
            Ts = T_min * 60.0
            W = int(L // Ts)
            if W < 2:
                continue
            edges = lo + Ts * np.arange(W + 1)
            starts = edges[:-1]
            blk = np.floor((starts - lo) / BLOCK_S + 1e-9).astype(int) if mode != "raw" else np.zeros(W, int)
        n = _bin(t, ai, edges, A)
        cl = U.calls.filter((pl.col("day") == d) & (pl.col("t_call") >= lo) & (pl.col("t_call") < hi))
        ci = np.array([amap.get(int(a), -1) for a in cl["agent"].to_list()], dtype=np.int64)
        tc = cl["t_call"].to_numpy().astype(np.float64)
        if off is not None:          # the shift null moves each agent's calls with its messages (per-call clock)
            sc = ci >= 0
            tc = tc.copy()
            tc[sc] = lo + np.mod(tc[sc] - lo + off[ci[sc]], L)
        ncall = _bin(tc, ci, edges, A)
        keep = np.ones(len(starts), bool)
        if mode not in ("exo_in",) and len(s0):
            ends = edges[1:]
            for a0, a1 in zip(s0, s1):
                keep &= ~((a0 < ends) & (a1 > starts))
        if kick and mode != "exo_in":
            keep &= starts >= lo + KICK_S
        out.append({"day": d, "n": n, "c": ncall, "blk": blk, "keep": keep, "rooms": rooms, "agents": agents,
                    "lo": lo, "hi": hi, "edges": edges})
    return out


def cells(days, clock: str = "wall") -> dict:
    """Per (day, block) cell sums: num = sum_w (sum_i x)^2, den = sum_w sum_i x^2, raw = sum_w sum_i n,
    same / cross = sum_w sum_{i != j same / other room} x_i x_j, and pair-normalisers."""
    keys, num, den, raw, same, cross, dsame, dcross, nwin = [], [], [], [], [], [], [], [], []
    for D in days:
        n, blk, keep, rooms = D["n"], D["blk"], D["keep"], D["rooms"]
        A = n.shape[1]
        same_m = (rooms[:, None] == rooms[None, :]) & (rooms[:, None] >= 0)
        np.fill_diagonal(same_m, False)
        cross_m = ~same_m
        np.fill_diagonal(cross_m, False)
        n_same, n_cross = same_m.sum(), cross_m.sum()
        for b in np.unique(blk):
            m = (blk == b) & keep
            if m.sum() < 2:
                continue
            X = n[m].astype(np.float64)
            if clock == "percall":
                Cc = D["c"][m].astype(np.float64)
                cs_ = Cc.sum(0)
                p_ = np.where(cs_ > 0, X.sum(0) / np.maximum(cs_, 1), 0.0)
                x = X - Cc * p_[None, :]
            else:
                x = X - X.mean(0, keepdims=True)
            tot = x.sum(1)
            dd = (x ** 2).sum()
            C = x.T @ x
            keys.append((D["day"], int(b)))
            num.append(float((tot ** 2).sum()))
            den.append(float(dd))
            raw.append(float(X.sum()))
            same.append(float(C[same_m].sum()))
            cross.append(float(C[cross_m].sum()))
            dsame.append(float(dd * n_same / A))
            dcross.append(float(dd * n_cross / A))
            nwin.append(int(m.sum()))
    return {"keys": keys, "num": np.array(num), "den": np.array(den), "raw": np.array(raw),
            "same": np.array(same), "cross": np.array(cross), "dsame": np.array(dsame), "dcross": np.array(dcross),
            "nwin": np.array(nwin)}


def phi_of(c: dict, idx=None) -> float:
    if idx is None:
        return float(c["num"].sum() / c["den"].sum()) if c["den"].sum() > 0 else float("nan")
    d = c["den"][idx].sum()
    return float(c["num"][idx].sum() / d) if d > 0 else float("nan")


def rho_part(c: dict, idx=None):
    sl = slice(None) if idx is None else idx
    ds, dc = c["dsame"][sl].sum(), c["dcross"][sl].sum()
    rs = c["same"][sl].sum() / ds if ds > 0 else float("nan")
    rc = c["cross"][sl].sum() / dc if dc > 0 else float("nan")
    return rs, rc


def fano_of(c: dict) -> float:
    return float(c["num"].sum() / c["raw"].sum()) if c["raw"].sum() > 0 else float("nan")


def boot_idx(keys_by_T: dict, B: int, rng) -> list:
    """Joint cell bootstrap: resample the union of cell keys; map to each T's cell indices."""
    allk = sorted(set().union(*[set(k) for k in keys_by_T.values()]))
    pos = {T: {k: i for i, k in enumerate(keys)} for T, keys in keys_by_T.items()}
    draws = []
    for _ in range(B):
        s = [allk[i] for i in rng.integers(0, len(allk), len(allk))]
        draws.append({T: np.array([pos[T][k] for k in s if k in pos[T]], dtype=np.int64) for T in keys_by_T})
    return draws


def pred_for_unit(days, g: float) -> float:
    """Phi_pred averaged over days, weighted by kept windows x agents."""
    num = den = 0.0
    for D in days:
        rooms = D["rooms"]
        _, sizes = np.unique(rooms, return_counts=True)
        p = phi_pred(g, sizes)
        w = D["keep"].sum() * len(rooms)
        if math.isfinite(p) and w > 0:
            num += w * p
            den += w
    return num / den if den > 0 else float("nan")


def cc_K_for(U: Unit, T_equiv: float = T_STAR) -> int:
    tot_calls = tot_min = 0.0
    for d, lo, hi, kick, agents, rooms in _day_frame(U, "cc"):
        c = U.calls.filter((pl.col("day") == d) & (pl.col("t_call") >= lo) & (pl.col("t_call") <= hi)
                           & pl.col("agent").is_in(agents.tolist()))
        tot_calls += c.height
        tot_min += (hi - lo) / 60.0
    if tot_min <= 0:
        return 100
    return max(int(round(tot_calls / (tot_min / T_equiv))), 10)


def unit_stats(U: Unit, g: float | None, g_se: float | None, g3: float | None = None, g_het: float | None = None,
               B: int = 500, n_shift: int = 49, seed: int = 0, sim_msgs=None, variants: bool = True,
               Ts=TS) -> dict:
    """All per-unit statistics. sim_msgs replaces the real messages (synthetic runs)."""
    rng = np.random.default_rng(seed)
    days_T = {T: build_days(U, T, "trim", sim_msgs=sim_msgs) for T in Ts}
    cs = {T: cells(days_T[T], CLOCK) for T in Ts}
    res = {"unit_id": U.uid}
    for T in Ts:
        res[f"phi_{T}"] = phi_of(cs[T])
        res[f"ncell_{T}"] = len(cs[T]["keys"])
        res[f"nwin_{T}"] = int(cs[T]["nwin"].sum())
    draws = boot_idx({T: cs[T]["keys"] for T in Ts}, B, rng)
    bt = {T: np.array([phi_of(cs[T], d[T]) for d in draws]) for T in Ts}
    for T in Ts:
        res[f"phi_{T}_lo"], res[f"phi_{T}_hi"] = np.nanpercentile(bt[T], [2.5, 97.5]).tolist()
        res[f"phi_{T}_se"] = float(np.nanstd(bt[T]))
    # shape
    if 5 in Ts and 30 in Ts:
        s = np.log(bt[30] / bt[5]) / np.log(6)
        res["s_F"] = float(np.log(res["phi_30"] / res["phi_5"]) / np.log(6))
        res["s_F_lo"], res["s_F_hi"] = np.nanpercentile(s, [2.5, 97.5]).tolist()
    # partition
    rs, rc = rho_part(cs[T_STAR])
    res["rho_same"], res["rho_cross"] = rs, rc
    pr = np.array([rho_part(cs[T_STAR], d[T_STAR]) for d in draws])
    res["rho_same_lo"], res["rho_same_hi"] = np.nanpercentile(pr[:, 0], [2.5, 97.5]).tolist()
    res["rho_cross_lo"], res["rho_cross_hi"] = np.nanpercentile(pr[:, 1], [2.5, 97.5]).tolist()
    dlt = pr[:, 0] - pr[:, 1]
    res["rho_diff_lo"], res["rho_diff_hi"] = np.nanpercentile(dlt, [2.5, 97.5]).tolist()
    res["two_rooms"] = bool(any(len(np.unique(D["rooms"])) > 1 for D in days_T[T_STAR]))
    # prediction
    dT = days_T[T_STAR]
    N_mean = np.mean([len(D["rooms"]) for D in dT]) if dT else float("nan")
    res["N_present"] = float(N_mean)
    if g is not None and math.isfinite(g):
        pp = pred_for_unit(dT, g)
        res["g"], res["g_se"], res["phi_pred"] = g, g_se, pp
        res["phi_pred_g3"] = pred_for_unit(dT, g3) if g3 is not None else float("nan")
        res["phi_pred_het"] = pred_for_unit(dT, g_het) if g_het is not None else float("nan")
        gb = rng.normal(g, g_se or 0.0, B)
        ppb = np.array([pred_for_unit(dT, x) for x in gb[:100]])
        ppb = np.resize(ppb, B)
        rF = bt[T_STAR] / ppb
        res["r_F"] = res[f"phi_{T_STAR}"] / pp
        res["r_F_lo"], res["r_F_hi"] = np.nanpercentile(rF, [2.5, 97.5]).tolist()
        res["r_F_se_log"] = float(np.nanstd(np.log(rF[rF > 0])))
        res["delta_F"] = res[f"phi_{T_STAR}"] - pp
        if pp - 1 >= 0.05:
            eF = (bt[T_STAR] - 1) / (ppb - 1)
            res["E_F"] = (res[f"phi_{T_STAR}"] - 1) / (pp - 1)
            res["E_F_lo"], res["E_F_hi"] = np.nanpercentile(eF, [2.5, 97.5]).tolist()
        else:
            res["E_F"] = res["E_F_lo"] = res["E_F_hi"] = float("nan")
    if not variants:
        return res
    # block-shift null at T*
    ph_null, f_null = [], []
    for k in range(n_shift):
        c0 = cells(build_days(U, T_STAR, "trim", shift_rng=np.random.default_rng(seed * 1000 + k + 1),
                              sim_msgs=sim_msgs), CLOCK)
        ph_null.append(phi_of(c0))
        f_null.append(fano_of(c0))
    res["phi_null_mean"] = float(np.nanmean(ph_null))
    res["phi_null_q95"] = float(np.nanpercentile(ph_null, 95))
    res["fano"] = fano_of(cs[T_STAR])
    res["fano_shift"] = float(np.nanmean(f_null))
    res["fano_ratio"] = res["fano"] / res["fano_shift"] if res["fano_shift"] > 0 else float("nan")
    # variants at T*
    for mode in ("untrim", "raw", "exo_in", "talkcalls"):
        if sim_msgs is not None and mode == "talkcalls":
            continue
        dv = build_days(U, T_STAR, mode, sim_msgs=sim_msgs)
        cv = cells(dv, CLOCK if mode != "raw" else "wall")
        res[f"phi_{mode}"] = phi_of(cv)
        dr = [rng.integers(0, len(cv["keys"]), len(cv["keys"])) for _ in range(200)] if cv["keys"] else []
        b = np.array([phi_of(cv, i) for i in dr]) if dr else np.array([np.nan])
        res[f"phi_{mode}_lo"], res[f"phi_{mode}_hi"] = np.nanpercentile(b, [2.5, 97.5]).tolist()
    K = cc_K_for(U)
    cv = cells(build_days(U, T_STAR, "cc", sim_msgs=sim_msgs, cc_K=K), "wall")
    res["cc_K"] = K
    res["phi_cc"] = phi_of(cv)
    dr = [rng.integers(0, len(cv["keys"]), len(cv["keys"])) for _ in range(200)] if cv["keys"] else []
    b = np.array([phi_of(cv, i) for i in dr]) if dr else np.array([np.nan])
    res["phi_cc_lo"], res["phi_cc_hi"] = np.nanpercentile(b, [2.5, 97.5]).tolist()
    return res


# ============================================================================================ pooling
def re_pool(est, se):
    """DerSimonian-Laird random-effects mean; returns (mu, lo, hi, tau2)."""
    est, se = np.asarray(est, float), np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[ok], se[ok]
    if len(est) == 0:
        return (float("nan"),) * 4
    if len(est) == 1:
        return float(est[0]), float(est[0] - 1.96 * se[0]), float(est[0] + 1.96 * se[0]), 0.0
    w = 1 / se ** 2
    mu = (w * est).sum() / w.sum()
    Q = (w * (est - mu) ** 2).sum()
    tau2 = max(0.0, (Q - (len(est) - 1)) / (w.sum() - (w ** 2).sum() / w.sum()))
    ws = 1 / (se ** 2 + tau2)
    m = (ws * est).sum() / ws.sum()
    s = math.sqrt(1 / ws.sum())
    return float(m), float(m - 1.96 * s), float(m + 1.96 * s), float(tau2)
