"""H35 library: the nudger as a Maxwell demon. Information used, work bought, and the information-work frontier.

One set of definitions and estimators, used identically by the synthetic validation (`synthetic.py`), the per-period
exploratory pipeline (`run_period.py`) and the confirmatory script (`confirm.py`). See the card,
hypotheses/H35-nudger-maxwell-demon/README.md ("Model", "Definitions").

Pieces
  states        minute-level agent states (idle duration D, gate timing G, trap age K, controller memory N) from
                h16lib-format rows (active-row times, PAUSE times and declared durations) and TS2r gates
  information   plug-in mutual information with Miller-Madow correction; circular-shift permutation null; chain rule
  work          minute-level matched ITT (past-only isolation; future kicks allowed in both arms) and H04's
                future-isolated variant; gate-level logistic model with agent fixed effects
  frontier      rate-constrained Blahut-Arimoto curve V*(R) for a binary action with budget r; efficiencies
                kappa = dV/I, eta_SU = dV/V*(I), eta_KW = R*(dV)/I; Donsker-Varadhan ceiling
Units: information in bits unless a name ends in _nats; work in extra active minutes (A30) or extra gate escapes.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2" if _v == "POLARS_MAX_THREADS" else "1")

import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import polars as pl
from scipy import special

ROOT = Path(__file__).resolve().parents[3]
HDIR = ROOT / "hypotheses/H35-nudger-maxwell-demon"
OUT = ROOT / "data/processed/H35-nudger-maxwell-demon"
SH = ROOT / "data/processed/shared"
SEED = 20261003
LN2 = np.log(2.0)

sys.path.insert(0, str(ROOT / "hypotheses/H16-metastable-traps-kramers/analysis"))
import h16lib  # noqa: E402  (imported, never modified)

# ------------------------------------------------------------------------------------------------ state bins (card)
BURN_MIN = 15
HORIZON = 30
D_EDGES = np.array([1.0, 3.0, 10.0, 30.0])          # minutes: [0,1) [1,3) [3,10) [10,30) >=30 ; cold = 5
D_LABELS = ["active", "1-3", "3-10", "10-30", ">=30", "cold"]
G_LABELS = ["none", ">5 left", "2-5 left", "<=2 left", "overdue"]
K_LABELS = ["0", "1", "2-3", "4-9", ">=10"]
N_LABELS = ["none", "<30", "30-90", ">=90"]
DECL_LABELS = ["<=5", "5-30", ">30"]
PAUSE_TOL_S = 5.0       # an active row within this long after a PAUSE event is the same turn (mirror / companion)
CTRL_MIN = 20


def d_bin(D: np.ndarray, cold: np.ndarray) -> np.ndarray:
    b = np.searchsorted(D_EDGES, D, side="right")
    return np.where(cold, 5, b).astype(np.int8)


def k_bin(k: np.ndarray) -> np.ndarray:
    k = np.asarray(k)
    return np.select([k <= 0, k == 1, k <= 3, k <= 9], [0, 1, 2, 3], 4).astype(np.int8)


def n_bin(since_min: np.ndarray) -> np.ndarray:
    s = np.asarray(since_min, float)
    return np.select([~np.isfinite(s), s < 30, s < 90], [0, 1, 2], 3).astype(np.int8)


def decl_bin(dec_s: np.ndarray) -> np.ndarray:
    d = np.asarray(dec_s, float)
    return np.select([~np.isfinite(d) | (d <= 300), d <= 1800], [0, 1], 2).astype(np.int8)


def g_bin(in_pause: np.ndarray, rem_min: np.ndarray, overdue: np.ndarray) -> np.ndarray:
    r = np.asarray(rem_min, float)
    out = np.zeros(len(r), np.int8)
    out[in_pause & (r > 5)] = 1
    out[in_pause & (r > 2) & (r <= 5)] = 2
    out[in_pause & (r <= 2)] = 3
    out[overdue] = 4
    return out


# ------------------------------------------------------------------------------------------------ minute grid

def build_grid(rows: dict, W: dict, gates: pl.DataFrame, kicks: dict, tool_rows: dict | None = None,
               regime_gate: bool = True) -> pl.DataFrame:
    """Agent-minute decision epochs with states, actions and outcomes.

    rows      h16lib.load_rows format: (agent, pt_date) -> {"act", "pause_t", "pause_s", "wait_t", ...}
    W         h16lib.windows format: pt_date -> {"t0", "t1", ...}
    gates     h16lib.build_ts2 output (TS2r chains); may be empty (regime I/II)
    kicks     agent -> class -> sorted times; classes used: N_tgt (nudge to the agent), A_men, H_men, H_und
    tool_rows (agent, pt_date) -> sorted times of non-mirror tool turns (outcome Y2); defaults to active rows
    regime_gate False: no pause tool (regime I/II): G = none and K = current run of consecutive WAIT events
    """
    gate_by = {}
    if gates is not None and gates.height:
        g = gates.select("agent", "pt_date", "t_pause", "k_r", "outcome_r", "t_gate").sort("agent", "pt_date", "t_pause")
        for (a, d), sub in g.group_by(["agent", "pt_date"]):
            gate_by[(int(a), d)] = (sub["t_pause"].to_numpy(), sub["k_r"].to_numpy(), sub["outcome_r"].to_numpy(),
                                    sub["t_gate"].to_numpy())
    parts = []
    for (a, d), v in rows.items():
        act = v["act"]
        if d not in W or len(act) == 0:
            continue
        t0, t1 = W[d]["t0"], W[d]["t1"]
        n_min = int(np.ceil((t1 - t0) / 60.0))
        if n_min < BURN_MIN + HORIZON + 1:
            continue
        tm = t0 + 60.0 * np.arange(n_min)
        mi = np.floor((act - t0) / 60.0).astype(int)
        mi = mi[(mi >= 0) & (mi < n_min)]
        amin = np.zeros(n_min, np.int8)
        amin[mi] = 1
        tools = tool_rows.get((a, d), act) if tool_rows is not None else act
        ti = np.floor((tools - t0) / 60.0).astype(int)
        ti = ti[(ti >= 0) & (ti < n_min)]
        tcount = np.bincount(ti, minlength=n_min).astype(np.int32)
        # agent state is read at the END of minute m (ts = tm + 60 s), so it includes the event that triggers a nudge
        # inside minute m (e.g. the PAUSE call); the controller memory N is read at the start (nudges before minute m).
        ts = tm + 60.0
        j = np.searchsorted(act, ts, "left") - 1
        cold = j < 0
        last = np.where(cold, t0, act[np.maximum(j, 0)])
        D = (ts - last) / 60.0
        # gate timing G
        in_pause = np.zeros(n_min, bool)
        overdue = np.zeros(n_min, bool)
        rem = np.full(n_min, np.nan)
        K = np.zeros(n_min, np.int32)
        pt, ps = v.get("pause_t", np.zeros(0)), v.get("pause_s", np.zeros(0))
        if regime_gate and len(pt):
            p = np.searchsorted(pt, ts, "right") - 1
            has = p >= 0
            pp = np.maximum(p, 0)
            quiet = has & (cold | (last <= pt[pp] + PAUSE_TOL_S))
            dec = np.where(np.isfinite(ps[pp]) & (ps[pp] > 0), ps[pp], np.nan)
            expiry = pt[pp] + np.nan_to_num(dec, nan=0.0)
            rem = (expiry - ts) / 60.0
            in_pause = quiet & np.isfinite(dec) & (rem > 0)
            overdue = quiet & np.isfinite(dec) & (rem <= 0)
            rem = np.where(in_pause, rem, np.nan)
        if regime_gate and (a, d) in gate_by:
            gp, gk, go, gt = gate_by[(a, d)]
            p = np.searchsorted(gp, ts, "right") - 1
            has = p >= 0
            pp = np.maximum(p, 0)
            ended = (go[pp] == "escape") & (gt[pp] <= ts)
            K = np.where(has & ~ended, gk[pp], 0).astype(np.int32)
        elif not regime_gate:
            wt = np.sort(v.get("wait_t", np.zeros(0)))
            if len(wt):
                # run of consecutive WAITs with no active row in between, counted up to time ts
                ev_t = np.r_[wt, act]
                ev_w = np.r_[np.ones(len(wt), int), np.zeros(len(act), int)]
                o = np.argsort(ev_t, kind="stable")
                ev_t, ev_w = ev_t[o], ev_w[o]
                run = np.zeros(len(ev_t), int)
                c = 0
                for i, w_ in enumerate(ev_w):
                    c = c + 1 if w_ else 0
                    run[i] = c
                q = np.searchsorted(ev_t, ts, "right") - 1
                K = np.where(q >= 0, run[np.maximum(q, 0)], 0).astype(np.int32)
        # controller memory and kicks
        ka = kicks.get(a, {})
        nt = ka.get("N_tgt", np.zeros(0))
        if len(nt):
            jn = np.searchsorted(nt, tm, "left") - 1
            lastn = nt[np.maximum(jn, 0)]
            since = np.where((jn >= 0) & (lastn >= t0 - 1), (tm - lastn) / 60.0, np.inf)
        else:
            since = np.full(n_min, np.inf)

        def per_min(arr):
            if arr is None or len(arr) == 0:
                return np.zeros(n_min, np.int16)
            q = np.floor((arr - t0) / 60.0).astype(int)
            q = q[(q >= 0) & (q < n_min)]
            return np.bincount(q, minlength=n_min).astype(np.int16)

        M = per_min(nt)
        dirk = per_min(ka.get("A_men")) + per_min(ka.get("H_men")) + per_min(ka.get("H_und"))
        amen = per_min(ka.get("A_men"))
        allk = M + dirk
        hk = M + per_min(ka.get("H_men")) + per_min(ka.get("H_und"))
        chh = np.r_[0, np.cumsum(hk)]
        cs = np.r_[0, np.cumsum(allk)]
        cm = np.r_[0, np.cumsum(M)]
        ca = np.r_[0, np.cumsum(amin)]
        ct = np.r_[0, np.cumsum(tcount)]
        m = np.arange(n_min)
        lo30 = np.clip(m - 30, 0, n_min)
        past_dir = cs[m] - cs[lo30]                      # direct kicks in [m-30, m-1]
        past_h04 = chh[m] - chh[lo30]                    # H04's direct kicks (nudges + human messages) in [m-30, m-1]
        past_n60 = cm[m] - cm[np.clip(m - 60, 0, n_min)]  # nudges to the agent in [m-60, m-1]
        hi = np.clip(m + HORIZON + 1, 0, n_min)
        fut_dir = cs[hi] - cs[np.clip(m + 1, 0, n_min)]  # direct kicks in [m+1, m+30]
        y30 = ca[hi] - ca[np.clip(m + 1, 0, n_min)]
        ytool = ct[hi] - ct[np.clip(m + 1, 0, n_min)]
        ypre = ca[np.clip(m - 15, 0, n_min)] - ca[np.clip(m - 30, 0, n_min)]   # placebo window [m-30, m-16]
        keep = (m >= BURN_MIN) & (m + HORIZON < n_min)
        parts.append(pl.DataFrame({
            "agent": np.full(keep.sum(), a, np.int16), "pt_date": [d] * int(keep.sum()), "minute": m[keep].astype(np.int16),
            "tod3": (m[keep] * 3 // n_min).astype(np.int8),
            "D": D[keep].astype(np.float32), "Db": d_bin(D, cold)[keep], "Gb": g_bin(in_pause, rem, overdue)[keep],
            "K": K[keep].astype(np.int16), "Kb": k_bin(K)[keep], "Kx": np.minimum(K, 15)[keep].astype(np.int8),
            "Nb": n_bin(since)[keep],
            "M": (M[keep] > 0).astype(np.int8), "n_nudge": M[keep], "dir_now": (dirk[keep]).astype(np.int16),
            "amen_now": amen[keep].astype(np.int16), "h04_now": hk[keep].astype(np.int16),
            "past_h04": past_h04[keep].astype(np.int16),
            "past_dir": past_dir[keep].astype(np.int16), "past_n60": past_n60[keep].astype(np.int16),
            "fut_dir": fut_dir[keep].astype(np.int16), "a_now": amin[keep],
            "y30": y30[keep].astype(np.int16), "ytool": ytool[keep].astype(np.int32), "ypre": ypre[keep].astype(np.int16)}))
    if not parts:
        return pl.DataFrame()
    return pl.concat(parts).sort("pt_date", "agent", "minute")


def gate_table(rows: dict, W: dict, kicks: dict) -> pl.DataFrame:
    """TS2r gates (h16lib.build_ts2) plus gate-level states and outcomes.

    M_g = a nudge to the agent between the PAUSE and its gate (n_N_tgt > 0 in h16lib's counting window).
    y30_gate = active minutes in [t_pause, t_pause + 30 min); escape = TS2r outcome 'escape' (censored dropped later)."""
    g = h16lib.build_ts2(rows, W, kicks)
    if g.height == 0:
        return g
    y = []
    for (a, d), sub in g.group_by(["agent", "pt_date"], maintain_order=True):
        act = rows[(int(a), d)]["act"]
        tp = sub["t_pause"].to_numpy()
        # active minutes in [tp, tp+30min): count distinct minutes (relative to tp) with >= 1 active row
        out = np.zeros(len(tp), np.int16)
        lo = np.searchsorted(act, tp, "left")
        hi = np.searchsorted(act, tp + 1800.0, "left")
        for i in range(len(tp)):
            if hi[i] > lo[i]:
                out[i] = len(np.unique(np.floor((act[lo[i]:hi[i]] - tp[i]) / 60.0)))
        y.append(sub.select("agent", "pt_date", "t_pause").with_columns(pl.Series("y30_gate", out)))
    y = pl.concat(y)
    g = g.join(y, on=["agent", "pt_date", "t_pause"], how="left")
    # time since the previous nudge to this agent (controller memory) at the pause
    nm = []
    for (a, d), sub in g.group_by(["agent", "pt_date"], maintain_order=True):
        nt = kicks.get(int(a), {}).get("N_tgt", np.zeros(0))
        tp = sub["t_pause"].to_numpy()
        t0 = W[d]["t0"]
        if len(nt):
            j = np.searchsorted(nt, tp, "left") - 1
            lastn = nt[np.maximum(j, 0)]
            s = np.where((j >= 0) & (lastn >= t0 - 1), (tp - lastn) / 60.0, np.inf)
        else:
            s = np.full(len(tp), np.inf)
        nm.append(sub.select("agent", "pt_date", "t_pause").with_columns(pl.Series("since_nudge_min", s)))
    g = g.join(pl.concat(nm), on=["agent", "pt_date", "t_pause"], how="left")
    dirc = [c for c in ("n_A_men", "n_H_men") if c in g.columns]
    g = g.with_columns(
        (pl.col("n_N_tgt") > 0).cast(pl.Int8).alias("M"),
        (pl.sum_horizontal([pl.col(c) for c in dirc]) > 0).cast(pl.Int8).alias("dir_other") if dirc else pl.lit(0, pl.Int8).alias("dir_other"),
        (pl.col("outcome_r") == "escape").cast(pl.Int8).alias("escape"),
        pl.Series("Kb", k_bin(g["k_r"].to_numpy())),
        pl.Series("declb", decl_bin(g["declared_s"].to_numpy())),
    ).with_columns(pl.Series("Nb", n_bin(g["since_nudge_min"].to_numpy())))
    return g


# ------------------------------------------------------------------------------------------------ information

def mi_table(tab: np.ndarray, mm: bool = True) -> float:
    """I(X;M) in nats from a (n_x, n_m) count table; Miller-Madow corrected if mm."""
    tab = np.asarray(tab, float)
    N = tab.sum()
    if N <= 0:
        return float("nan")
    pxy = tab / N
    px = pxy.sum(1, keepdims=True)
    py = pxy.sum(0, keepdims=True)
    nz = pxy > 0
    I = float(np.sum(pxy[nz] * np.log(pxy[nz] / (px @ py)[nz])))
    if mm:
        kxy, kx, ky = int(nz.sum()), int((px > 0).sum()), int((py > 0).sum())
        I -= (kxy - kx - ky + 1) / (2 * N)
    return I


def codes(*cols) -> np.ndarray:
    """Joint integer code of several small-integer columns."""
    out = np.zeros(len(cols[0]), np.int64)
    for c in cols:
        c = np.asarray(c, np.int64)
        out = out * (int(c.max()) + 1 if len(c) else 1) + c
    return np.unique(out, return_inverse=True)[1]


def mi(x_code: np.ndarray, m: np.ndarray, mm: bool = True) -> float:
    """I(X;M) in nats for integer-coded X and binary M."""
    nx = int(x_code.max()) + 1
    tab = np.zeros((nx, 2))
    np.add.at(tab, (x_code, m.astype(int)), 1)
    return mi_table(tab, mm)


def cmi(y_code, z_code, m, mm=True) -> float:
    """I(M; Y | Z) = I(M; Y,Z) - I(M; Z)."""
    return mi(codes(y_code, z_code), m, mm) - mi(z_code, m, mm)


def entropy_bin(r: float) -> float:
    if r <= 0 or r >= 1:
        return 0.0
    return float(-(r * np.log(r) + (1 - r) * np.log(1 - r)))


def circular_shift_null(m: np.ndarray, groups: np.ndarray, rng) -> np.ndarray:
    """Permutation null: within each group (agent-day, rows in time order), circularly shift M by a random offset."""
    out = np.empty_like(m)
    order = np.argsort(groups, kind="stable")
    g_sorted = groups[order]
    bounds = np.r_[0, np.nonzero(np.diff(g_sorted))[0] + 1, len(g_sorted)]
    for s, e in zip(bounds[:-1], bounds[1:]):
        idx = order[s:e]
        n = e - s
        out[idx] = np.roll(m[idx], rng.integers(0, n) if n > 1 else 0)
    return out


def permute_within(m: np.ndarray, strata: np.ndarray, rng) -> np.ndarray:
    """Conditional permutation null: shuffle M within each stratum (keeps I(M; stratum), destroys anything beyond it)."""
    out = m.copy()
    order = np.argsort(strata, kind="stable")
    s_sorted = strata[order]
    bounds = np.r_[0, np.nonzero(np.diff(s_sorted))[0] + 1, len(s_sorted)]
    for s0, e0 in zip(bounds[:-1], bounds[1:]):
        if e0 - s0 > 1:
            idx = order[s0:e0]
            out[idx] = m[rng.permutation(idx)]
    return out


def info_block(df: pl.DataFrame, rng, n_null: int = 50) -> dict:
    """Minute-level information decomposition (bits; per epoch and per nudge).

    Bias nulls (subtracted): marginal terms use a full permutation of M over all epochs; conditional terms I(M;Y|Z) a
    permutation of M within Z cells (keeps I(M;Z), destroys only the extra dependence on Y). With Miller-Madow the
    marginal bias is ~0 at these sample sizes, so the chain rule holds for the corrected values.
    Within-day timing (reported, not subtracted): I(M;X) minus its circular-shift null mean (nudge count and spacing kept
    within each agent-day). On real data agent-days differ in idleness, so the circular-shift null keeps real
    "which agent-days" information; the difference is the information in the nudge's timing within the day.
    [Amendment A1, 2026-10-03, after the first G51 run: round-1 code subtracted the circular-shift null from marginal
    terms, which is a pure bias floor only without day-to-day heterogeneity (true in the synthetic, false in the data).]"""
    m = df["M"].to_numpy().astype(int)
    r = m.mean()
    if m.sum() == 0:
        return {"n_nudge_epochs": 0}
    Db, Gb, Kb = (df[c].to_numpy() for c in ("Db", "Gb", "Kb"))
    A = np.unique(df["agent"].to_numpy(), return_inverse=True)[1]
    Nb = df["Nb"].to_numpy()
    grp = codes(df["agent"].to_numpy(), np.unique(df["pt_date"].to_numpy(), return_inverse=True)[1])
    X = codes(Db, Gb, Kb)
    DG = codes(Db, Gb)
    marg = {"I_X": lambda mm_: mi(X, mm_), "I_D": lambda mm_: mi(Db, mm_), "I_K": lambda mm_: mi(Kb, mm_),
            "I_G": lambda mm_: mi(Gb, mm_), "I_DK": lambda mm_: mi(codes(Db, Kb), mm_),
            "I_XN": lambda mm_: mi(codes(X, Nb), mm_), "I_XNA": lambda mm_: mi(codes(X, Nb, A), mm_)}
    cond = {"I_G_given_D": (Gb, Db), "I_K_given_DG": (Kb, DG), "I_A_given_X": (A, X), "I_N_given_X": (Nb, X),
            "I_D_given_K": (Db, Kb), "I_G_given_K": (Gb, Kb)}
    res = {"n_epochs": int(len(m)), "n_nudge_epochs": int(m.sum()), "r": float(r), "H_M_bits": entropy_bin(r) / LN2,
           "H_M_bits_per_nudge": entropy_bin(r) / LN2 / r}

    def put(k, v, nv):
        corr = v - nv.mean()
        res[k] = {"bits": v / LN2, "null_mean_bits": nv.mean() / LN2, "null_p95_bits": np.percentile(nv, 95) / LN2,
                  "corrected_bits": corr / LN2, "bits_per_nudge": corr / LN2 / r, "above_null": bool(v > np.percentile(nv, 95))}

    perms = [rng.permutation(m) for _ in range(n_null)]
    for k, f in marg.items():
        put(k, f(m), np.array([f(z) for z in perms]))
    for k, (Y, Z) in cond.items():
        v = cmi(Y, Z, m)
        put(k, v, np.array([cmi(Y, Z, permute_within(m, Z, rng)) for _ in range(n_null)]))
    shifts = [circular_shift_null(m, grp, rng) for _ in range(n_null)]
    for k in ("I_X", "I_K"):
        f = marg[k]
        nv = np.array([f(z) for z in shifts])
        v = f(m)
        res[k + "_withinday"] = {"bits_per_nudge": (v - nv.mean()) / LN2 / r, "circshift_null_mean_bits_per_nudge": nv.mean() / LN2 / r,
                                 "above_circshift_p95": bool(v > np.percentile(nv, 95))}
    tot = res["I_X"]["corrected_bits"]
    if tot > 0:
        for k_out, k_in in (("share_DK", "I_DK"), ("share_D", "I_D"), ("share_K", "I_K"), ("share_G", "I_G"),
                            ("share_G_given_D", "I_G_given_D"), ("share_K_given_DG", "I_K_given_DG"),
                            ("share_A_given_X", "I_A_given_X"), ("share_N_given_X", "I_N_given_X")):
            res[k_out] = res[k_in]["corrected_bits"] / tot
        res["share_withinday"] = res["I_X_withinday"]["bits_per_nudge"] / res["I_X"]["bits_per_nudge"]
    res["determinism_X"] = res["I_X"]["corrected_bits"] / res["H_M_bits"] if res["H_M_bits"] > 0 else float("nan")
    res["determinism_XNA"] = res["I_XNA"]["corrected_bits"] / res["H_M_bits"] if res["H_M_bits"] > 0 else float("nan")
    return res


def propensity_profile(df: pl.DataFrame, col: str, labels: list[str]) -> list[dict]:
    """Nudge rate per bin of one state variable (per 1,000 epochs) and the share of nudges in that bin."""
    g = df.group_by(col).agg(pl.len().alias("n"), pl.col("M").sum().alias("m")).sort(col)
    tot = max(1, int(df["M"].sum()))
    return [{"bin": labels[int(b)] if int(b) < len(labels) else str(b), "epochs": int(n), "nudges": int(mm),
             "rate_per_1000": 1000.0 * mm / n if n else None, "share_of_nudges": mm / tot} for b, n, mm in g.iter_rows()]


# ------------------------------------------------------------------------------------------------ work: minute ITT

def matched_att(df: pl.DataFrame, treated: np.ndarray, control: np.ndarray, ycol: str = "y30",
                strata_full=("agent", "Db", "Gb", "Kx", "tod3"), strata_local=("Db", "Gb", "Kx", "tod3"),
                min_ctrl: int = CTRL_MIN) -> dict:
    """Per-treated residual Y - mean_control(stratum) with fallback to the agent-free stratum. Returns arrays."""
    y = df[ycol].to_numpy().astype(float)
    sf = codes(*[df[c].to_numpy() for c in strata_full])
    sl = codes(*[df[c].to_numpy() for c in strata_local])
    nf, nl = sf.max() + 1, sl.max() + 1
    cf = np.bincount(sf[control], minlength=nf).astype(float)
    cl = np.bincount(sl[control], minlength=nl).astype(float)
    with np.errstate(invalid="ignore", divide="ignore"):
        mf = np.bincount(sf[control], weights=y[control], minlength=nf) / cf
        ml = np.bincount(sl[control], weights=y[control], minlength=nl) / cl
    t = np.nonzero(treated)[0]
    use_f = cf[sf[t]] >= min_ctrl
    cm = np.where(use_f, mf[sf[t]], ml[sl[t]])
    ok = np.isfinite(cm) & (np.where(use_f, cf[sf[t]], cl[sl[t]]) >= 1)
    return {"idx": t[ok], "resid": (y[t] - cm)[ok], "fallback": float(1 - use_f[ok].mean()) if ok.any() else float("nan"),
            "n_dropped": int((~ok).sum())}


def day_boot_mean(vals: np.ndarray, days: np.ndarray, rng, B: int = 1000) -> tuple:
    """Mean with a day-block bootstrap 95% CI."""
    if len(vals) == 0:
        return (float("nan"),) * 3
    u, inv = np.unique(days, return_inverse=True)
    s = np.bincount(inv, weights=vals, minlength=len(u))
    c = np.bincount(inv, minlength=len(u)).astype(float)
    pt = s.sum() / c.sum()
    if len(u) < 2:
        return float(pt), float("nan"), float("nan")
    w = rng.multinomial(len(u), np.full(len(u), 1 / len(u)), size=B).astype(float)
    with np.errstate(invalid="ignore", divide="ignore"):
        bs = (w @ s) / (w @ c)
    lo, hi = np.nanpercentile(bs, [2.5, 97.5])
    return float(pt), float(lo), float(hi)


def work_minute(df: pl.DataFrame, rng, B: int = 1000) -> dict:
    """First-nudge and repeat-nudge ATT on A30 and tool turns; past-only design (primary) and H04-style variant."""
    M = df["M"].to_numpy() > 0
    past = df["past_dir"].to_numpy()
    pn60 = df["past_n60"].to_numpy()
    fut = df["fut_dir"].to_numpy()
    dirnow = df["dir_now"].to_numpy()
    days = df["pt_date"].to_numpy()
    first = M & (past == 0) & (dirnow == 0)
    repeat = M & (pn60 > 0) & (dirnow == 0)
    ctrl_past = (~M) & (past == 0) & (dirnow == 0)
    ctrl_fut = ctrl_past & (fut == 0)
    first_fut = first & (fut == 0)
    # H04's isolation set (nudges to the agent + human messages; agent mentions allowed), past-only
    past_h = df["past_h04"].to_numpy() if "past_h04" in df.columns else past
    now_h = df["h04_now"].to_numpy() if "h04_now" in df.columns else dirnow
    first_h = M & (past_h == 0) & (now_h - M.astype(int) <= 0)
    ctrl_h = (~M) & (past_h == 0) & (now_h == 0)
    out = {}
    for name, tr, ct in (("first_pastonly", first, ctrl_past), ("repeat_pastonly", repeat, ctrl_past),
                         ("first_futureisolated_H04", first_fut, ctrl_fut), ("first_mixed_H04ctrl", first, ctrl_fut),
                         ("first_pastonly_H04iso", first_h, ctrl_h)):
        res = {}
        for ycol in ("y30", "ytool", "ypre"):
            r = matched_att(df, tr, ct, ycol)
            res[ycol] = day_boot_mean(r["resid"], days[r["idx"]], rng, B)
            if ycol == "y30":
                res["n"] = int(len(r["idx"]))
                res["fallback_share"] = r["fallback"]
                res["_idx"] = r["idx"]
                res["_resid"] = r["resid"]
        out[name] = res
    return out


def shrink(means: np.ndarray, ses: np.ndarray, w_counts: np.ndarray) -> tuple[np.ndarray, float]:
    """Empirical-Bayes shrinkage of cell estimates toward their precision-weighted mean (method of moments tau^2)."""
    ok = np.isfinite(means) & np.isfinite(ses) & (ses > 0)
    if ok.sum() < 2:
        return np.where(ok, means, np.nan), float("nan")
    wv = 1 / ses[ok] ** 2
    mu = np.sum(wv * means[ok]) / wv.sum()
    tau2 = max(0.0, (np.sum((means[ok] - mu) ** 2) - np.sum(ses[ok] ** 2)) / (ok.sum() - 1))
    lam = tau2 / (tau2 + ses ** 2)
    out = np.where(ok, mu + lam * (means - mu), mu)
    return out, tau2


# ------------------------------------------------------------------------------------------------ work: gate model

def logit_fe(y: np.ndarray, X: np.ndarray, g: np.ndarray, ridge_fe: float = 1e-2, ridge_b: float = 1e-6,
             max_iter: int = 100, tol: float = 1e-10) -> dict:
    """Logistic regression with group intercepts (lightly ridge-penalized so all-0/all-1 groups stay finite).

    Returns beta, se (from the profiled Hessian), alpha per group (aligned with np.unique(g))."""
    y = np.asarray(y, float)
    X = np.asarray(X, float)
    if X.ndim == 1:
        X = X[:, None]
    ug, gi = np.unique(g, return_inverse=True)
    G = len(ug)
    n, p = X.shape
    ybar = np.clip(np.bincount(gi, y, G) / np.bincount(gi, None, G), 0.02, 0.98)
    alpha = np.log(ybar / (1 - ybar))
    beta = np.zeros(p)
    prev = -np.inf
    for it in range(max_iter):
        eta = alpha[gi] + X @ beta
        mu = special.expit(eta)
        w = np.maximum(mu * (1 - mu), 1e-10)
        ra = np.bincount(gi, y - mu, G) - ridge_fe * alpha
        rb = X.T @ (y - mu) - ridge_b * beta
        Haa = np.bincount(gi, w, G) + ridge_fe
        Hab = np.stack([np.bincount(gi, w * X[:, j], G) for j in range(p)], 1)
        Hbb = X.T @ (w[:, None] * X) + ridge_b * np.eye(p)
        S = Hbb - Hab.T @ (Hab / Haa[:, None])
        db = np.linalg.solve(S, rb - Hab.T @ (ra / Haa))
        da = (ra - Hab @ db) / Haa
        step = 1.0
        ll0 = float(np.sum(y * eta - np.logaddexp(0, eta))) - 0.5 * ridge_fe * np.sum(alpha ** 2)
        for _ in range(30):
            na, nb = alpha + step * da, beta + step * db
            e2 = na[gi] + X @ nb
            ll = float(np.sum(y * e2 - np.logaddexp(0, e2))) - 0.5 * ridge_fe * np.sum(na ** 2)
            if ll >= ll0 - 1e-9:
                break
            step /= 2
        alpha, beta = na, nb
        if abs(ll - prev) < tol * (1 + abs(ll)):
            break
        prev = ll
    eta = alpha[gi] + X @ beta
    mu = special.expit(eta)
    w = np.maximum(mu * (1 - mu), 1e-10)
    Haa = np.bincount(gi, w, G) + ridge_fe
    Hab = np.stack([np.bincount(gi, w * X[:, j], G) for j in range(p)], 1)
    Hbb = X.T @ (w[:, None] * X)
    S = Hbb - Hab.T @ (Hab / Haa[:, None])
    cov = np.linalg.pinv(S)
    return {"beta": beta, "se": np.sqrt(np.maximum(np.diag(cov), 0)), "cov": cov, "alpha": alpha, "groups": ug,
            "loglik": float(np.sum(y * eta - np.logaddexp(0, eta))), "n": int(n), "n_events": int(y.sum())}


GATE_C = np.log(3.0)   # centring of ln k in the nudge x trap-age interaction


def gate_design(g: pl.DataFrame, nudge: np.ndarray | None = None, variant: str = "shared") -> tuple[np.ndarray, list[str]]:
    """Gate-model design.

    shared (primary): any directed kick during the pause (nudge or agent/human mention; one kick counts) with a common
      trap-age slope, plus a nudge level offset. Mentions identify the slope where the nudger never acts (transport of
      the slope, not of the level).
    separate (variant): nudge and other directed kicks each with their own level and slope."""
    lk = np.log(np.maximum(g["k_r"].to_numpy(), 1))
    ld = np.log(np.clip(np.nan_to_num(g["declared_s"].to_numpy(), nan=300.0), 30, 86400) / 300.0)
    N = g["M"].to_numpy().astype(float) if nudge is None else nudge.astype(float)
    O = g["dir_other"].to_numpy().astype(float)
    tod = g["tod"].to_numpy().astype(float)
    if variant == "separate":
        X = np.column_stack([lk, ld, N, N * (lk - GATE_C), O, O * (lk - GATE_C), tod])
        return X, ["ln_k", "ln_decl", "nudge", "nudge_x_lnk", "dir_other", "dir_other_x_lnk", "tod"]
    K_ = np.maximum(N, O)
    X = np.column_stack([lk, ld, K_, K_ * (lk - GATE_C), N, tod])
    return X, ["ln_k", "ln_decl", "kick", "kick_x_lnk", "nudge_offset", "tod"]


def gate_fit(g: pl.DataFrame, variant: str = "shared") -> dict:
    """Fit the gate model on non-censored gates; returns the fit plus names."""
    gg = g.filter(pl.col("outcome_r") != "censored")
    X, names = gate_design(gg, variant=variant)
    f = logit_fe(gg["escape"].to_numpy(), X, gg["agent"].to_numpy())
    f["names"] = names
    f["variant"] = variant
    return f


def gate_dp(fit: dict, g: pl.DataFrame) -> np.ndarray:
    """Per-gate predicted change in escape probability if nudged during the pause vs not (other kicks as observed)."""
    v = fit.get("variant", "shared")
    X1, _ = gate_design(g, np.ones(g.height), v)
    X0, _ = gate_design(g, np.zeros(g.height), v)
    amap = dict(zip(fit["groups"].tolist(), fit["alpha"].tolist()))
    a = np.array([amap.get(int(x), np.nan) for x in g["agent"].to_numpy()])
    a = np.where(np.isfinite(a), a, np.nanmean(fit["alpha"]))
    return special.expit(a + X1 @ fit["beta"]) - special.expit(a + X0 @ fit["beta"])


def crossfit_dp(g: pl.DataFrame, variant: str = "shared", n_folds: int = 5, min_nudged: int = 5) -> np.ndarray:
    """Cross-fitted per-gate dp: K folds by day (K = min(n_folds, n_days)); fit on the other folds, predict this one.

    Bootstrap copies of a day ("<date>#<j>") are kept in the same fold as their original date (no train/test leakage).
    A fold whose training set has fewer than min_nudged nudged gates is left NaN."""
    base = [str(d).split("#")[0] for d in g["pt_date"].to_list()]
    days = sorted(set(base))
    K = max(2, min(n_folds, len(days)))
    fold_of = {d: i % K for i, d in enumerate(days)}
    h = np.array([fold_of[d] for d in base])
    out = np.full(g.height, np.nan)
    for s in range(K):
        tr = g.filter(pl.Series(h != s))
        if tr.filter(pl.col("M") == 1).height < min_nudged or not (h == s).any():
            continue
        f = gate_fit(tr, variant)
        if not np.all(np.isfinite(f["beta"])):
            continue
        out[h == s] = gate_dp(f, g.filter(pl.Series(h == s)))
    return out


def gate_minutes_per_escape(g: pl.DataFrame) -> dict:
    """B(K bin): mean active minutes in [t_pause, +30) after escape minus after re-pause, un-nudged gates, agent-centred."""
    gg = g.filter((pl.col("outcome_r") != "censored") & (pl.col("M") == 0))
    out = {}
    for kb in range(1, 5):
        s = gg.filter(pl.col("Kb") == kb)
        if s.height < 20 or s["escape"].sum() < 5 or (s.height - s["escape"].sum()) < 5:
            out[kb] = float("nan")
            continue
        # within-agent difference, weighted by gates
        d = s.group_by("agent").agg(
            pl.col("y30_gate").filter(pl.col("escape") == 1).mean().alias("e"),
            pl.col("y30_gate").filter(pl.col("escape") == 0).mean().alias("r"), pl.len().alias("n")).drop_nulls()
        out[kb] = float(np.average(d["e"] - d["r"], weights=d["n"])) if d.height else float("nan")
    return out


# ------------------------------------------------------------------------------------------------ frontier

def policy_info(p: np.ndarray, pi: np.ndarray) -> float:
    """I(X;M) in nats for state distribution p and nudge probabilities pi(x)."""
    r = float(np.sum(p * pi))
    if r <= 0 or r >= 1:
        return 0.0
    with np.errstate(divide="ignore", invalid="ignore"):
        t1 = np.where(pi > 0, pi * np.log(pi / r), 0.0)
        t0 = np.where(pi < 1, (1 - pi) * np.log((1 - pi) / (1 - r)), 0.0)
    return float(np.sum(p * (t1 + t0)))


def policy_value(p: np.ndarray, pi: np.ndarray, g: np.ndarray) -> float:
    """Value of information per epoch: E[pi g] - r E[g]."""
    r = np.sum(p * pi)
    return float(np.sum(p * pi * g) - r * np.sum(p * g))


def frontier_curve(p: np.ndarray, g: np.ndarray, r: float, n_beta: int = 80) -> dict:
    """Information-work frontier for budget r: pi_beta(x) = sigmoid(logit r + beta (g(x) - lam)), lam fixes E[pi] = r."""
    p = np.asarray(p, float) / np.sum(p)
    g = np.asarray(g, float)
    sg = np.sqrt(np.sum(p * (g - np.sum(p * g)) ** 2))
    if not np.isfinite(sg) or sg <= 0:
        return {"I_nats": np.array([0.0]), "V": np.array([0.0]), "beta": np.array([0.0]), "sigma_g": float(sg)}
    lr = np.log(r / (1 - r))
    betas = np.r_[0.0, np.geomspace(1e-3, 1e3, n_beta) / sg]
    I, V, P = [], [], []
    for b in betas:
        lo, hi = -50.0 / max(b, 1e-9) - np.abs(g).max() - 1, 50.0 / max(b, 1e-9) + np.abs(g).max() + 1
        if b == 0:
            pi = np.full(len(p), r)
        else:
            for _ in range(200):
                lam = 0.5 * (lo + hi)
                pi = special.expit(lr + b * (g - lam))
                if np.sum(p * pi) > r:
                    lo = lam
                else:
                    hi = lam
        I.append(policy_info(p, pi)); V.append(policy_value(p, pi, g)); P.append(pi)
    I, V = np.array(I), np.array(V)
    o = np.argsort(I)
    I, V = I[o], np.maximum.accumulate(V[o])
    return {"I_nats": I, "V": V, "beta": betas[o], "sigma_g": float(sg), "pis": [P[i] for i in o]}


def frontier_at(curve: dict, I_nats: float) -> float:
    return float(np.interp(I_nats, curve["I_nats"], curve["V"]))


def frontier_inverse(curve: dict, V: float) -> float:
    """Least information achieving value V on the frontier (nan if V exceeds the curve)."""
    Vc, Ic = curve["V"], curve["I_nats"]
    if V <= 0:
        return 0.0
    if V > Vc.max() + 1e-12:
        return float("nan")
    i = int(np.argmax(Vc >= V))
    if i == 0:
        return float(Ic[0])
    return float(Ic[i - 1] + (V - Vc[i - 1]) * (Ic[i] - Ic[i - 1]) / max(Vc[i] - Vc[i - 1], 1e-15))


def dv_ceiling(sigma_g: float, r: float, I_nats: float) -> float:
    """Donsker-Varadhan ceiling on the value of information per epoch: s sqrt(2 r I), with s a sub-Gaussian scale of g.

    Strict with s = half the range of g (Hoeffding); with s = SD of g it is the Gaussian heuristic."""
    return float(sigma_g * np.sqrt(2 * r * max(I_nats, 0.0)))


def efficiencies(p: np.ndarray, pi_log: np.ndarray, g: np.ndarray) -> dict:
    """Logged policy's information, value, frontier and efficiencies in one state space (per epoch and per nudge)."""
    p = np.asarray(p, float)
    if p.size < 2 or not np.isfinite(np.sum(p)) or np.sum(p) <= 0 or not np.all(np.isfinite(g)):
        return {"r": float("nan"), "error": "fewer than 2 usable cells"}
    p = p / np.sum(p)
    r = float(np.sum(p * pi_log))
    if r <= 0:
        return {"r": 0.0, "error": "no nudges in usable cells"}
    I = policy_info(p, pi_log)
    V = policy_value(p, pi_log, g)
    cur = frontier_curve(p, g, r)
    Vstar = frontier_at(cur, I)
    Rstar = frontier_inverse(cur, V)
    det = cur["V"][-1]
    out = {"r": r, "I_bits": I / LN2, "bits_per_nudge": I / LN2 / r if r > 0 else float("nan"),
           "dV_per_epoch": V, "dV_per_nudge": V / r if r > 0 else float("nan"),
           "V_rand_per_nudge": float(np.sum(p * g)), "V_log_per_nudge": float(np.sum(p * pi_log * g) / r) if r > 0 else float("nan"),
           "Vstar_at_I_per_nudge": Vstar / r if r > 0 else float("nan"), "V_max_per_nudge": det / r if r > 0 else float("nan"),
           "eta_SU": V / Vstar if Vstar > 0 else float("nan"),
           "eta_KW": Rstar / I if (I > 0 and np.isfinite(Rstar)) else float("nan"),
           "kappa_min_per_bit_per_nudge": (V / r) / (I / LN2 / r) if I > 0 else float("nan"),
           "sigma_g": cur["sigma_g"], "dv_ceiling_per_nudge": dv_ceiling(cur["sigma_g"], r, I) / r if r > 0 else float("nan"),
           "half_range_g": float((np.max(g) - np.min(g)) / 2),
           "dv_ceiling_hoeffding_per_nudge": dv_ceiling(float((np.max(g) - np.min(g)) / 2), r, I) / r if r > 0 else float("nan")}
    out["_curve"] = cur
    return out


# ------------------------------------------------------------------------------------------------ provenance and io

def git_commit() -> str:
    r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "--", "hypotheses/H35-nudger-maxwell-demon"],
                           capture_output=True, text=True).stdout
    return (r.stdout.strip() or "none") + ("+uncommitted-H35" if dirty.strip() else "")


def write_provenance(folder: Path, built_by: str, tables: list[str], params: dict):
    rev = None
    try:
        sp = json.loads((SH / "_provenance.json").read_text())
        for v in sp.values():
            if isinstance(v, dict) and isinstance(v.get("inputs"), dict) and v["inputs"].get("revision"):
                rev = v["inputs"]["revision"]
                break
    except Exception:
        pass
    prov = {"built_by": built_by, "git_commit": git_commit(),
            "inputs": [{"source": "ai-village (via data/processed/shared)", "revision": rev, "tables": tables}],
            "params": params, "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "_provenance.json").write_text(json.dumps(prov, indent=1, default=str))


def jdump(obj, path: Path):
    def conv(o):
        if isinstance(o, np.floating):
            return float(o) if np.isfinite(o) else None
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, np.bool_):
            return bool(o)
        return str(o)

    def clean(o):
        if isinstance(o, dict):
            return {str(k): clean(v) for k, v in o.items() if not str(k).startswith("_")}
        if isinstance(o, (list, tuple)):
            return [clean(v) for v in o]
        if isinstance(o, float) and not np.isfinite(o):
            return None
        return o
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean(obj), indent=1, default=conv))
