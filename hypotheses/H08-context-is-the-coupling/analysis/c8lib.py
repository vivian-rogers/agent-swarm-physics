"""C8 (HH92): zero-parameter prediction of message -> activity kernels from turn timing.

Kernels are H04's matched Green's functions (imported from hypotheses/H04-reversible-forcing/analysis/h04lib.py,
not modified). The pause-matched variant adds a pre-treatment pause-remaining stratum by adjusting the cell strata and
h04lib's module constant N_STRATA_LOCAL for the duration of the call (no file of H04 is changed).

Model shapes (tau in minutes, tau = 0 the kick minute, fitted on tau = 1..45):
  ctx      A * F(tau),              F = P(read-out minute <= tau) over the cells (zero free shape parameters)
  ctx_d    A * mean[ 1(tau >= tau_r) exp(-(tau - tau_r)/theta) ]
  imm      A                        (immediate step)
  delay    A * 1(tau >= d)          (constant dead time)
  hawkes   A * exp(-(tau - 1)/theta) (exogenous Hawkes kernel)
  gamma    A * GammaCDF(tau; k, theta) (flexible ceiling)
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scheme"))
from h08lib import *  # noqa: E402,F403  (sets thread env to 2)

sys.path.insert(0, str(ROOT / "hypotheses/H04-reversible-forcing/analysis"))
import h04lib  # noqa: E402
from scipy.stats import gamma as gamma_dist  # noqa: E402

LAGS = h04lib.LAGS
L0 = h04lib.L0
TAU = np.arange(1, 46)                 # fit range
PLATEAU = (16, 45)
N_CODES = 46                           # agent codes 0..45
PB_EDGES = np.array([0.0, 120.0, 300.0])  # pause remaining (s): not paused / <=2 min / 2-5 min / >5 min
N_PB = 4


def pause_bin(inp: np.ndarray, rem: np.ndarray) -> np.ndarray:
    b = np.zeros(len(inp), np.int64)
    b[inp & (rem <= 120)] = 1
    b[inp & (rem > 120) & (rem <= 300)] = 2
    b[inp & (rem > 300)] = 3
    return b


# ----------------------------------------------------------------------------- data preparation

class Prep:
    """Days (H04 structures), messages, responder rows, turns, for one set of PT dates."""

    def __init__(self, days: list[str], chat: pl.DataFrame | None = None, turns: dict | None = None):
        self.days_str = days
        self.D = h04lib.load_days(days)
        self.msgs = h04lib.load_messages(days)
        self.resp = h04lib.responder_rows(self.D, self.msgs)
        self.T = turns if turns is not None else build_turns(days, chat)
        self.msg_t = dict(zip(self.msgs["msg"].to_list(), us(self.msgs["t"]).tolist()))
        self.win_us = [int(d.win_start.timestamp() * US) for d in self.D]

    def attach(self, resp=None):
        h04lib.attach_hits(self.D, self.resp if resp is None else resp)


def cell_pause_bins(P: Prep, c) -> np.ndarray:
    """Pause bin of every cell at minute start + 30 s (pre-treatment)."""
    pb = np.zeros(len(c.day), np.int64)
    for k, d in enumerate(P.D):
        sel = np.nonzero(c.day == k)[0]
        if not len(sel):
            continue
        for i, a in enumerate(d.agents):
            s2 = sel[c.row[sel] == i]
            if not len(s2):
                continue
            tr = P.T.get((int(a), d.pt_date))
            if tr is None:
                continue
            t = P.win_us[k] + (c.minute[s2].astype(np.int64) * 60 + 30) * US
            inp, rem, _ = pause_state(tr, t)
            pb[s2] = pause_bin(inp, rem)
    return pb


N_FINE = 4 * 16 * 3   # state(m-1) x inactive minutes in [m-15, m-1] (0..15) x day third


def fine_local(P: Prep, c) -> np.ndarray:
    """Finer pre-history stratum: state at m-1 (1..4) x exact inactive count in the last 15 min x day third."""
    out = np.zeros(len(c.day), np.int64)
    for k, d in enumerate(P.D):
        sel = np.nonzero(c.day == k)[0]
        if not len(sel):
            continue
        st = d.state
        inact = h04lib.window_sum((st <= 2).astype(np.int64), -15, -1)
        r, m = c.row[sel].astype(int), c.minute[sel].astype(int)
        tod = m * 3 // st.shape[1]
        out[sel] = ((st[r, m - 1].astype(np.int64) - 1) * 16 + inact[r, m]) * 3 + tod
    return out


def build_kernel_inputs(P: Prep, pause_matched: bool = False, var: str = "active", fine: bool = False):
    """H04 cells and matched controls. pause_matched adds the pause-remaining bin; fine replaces H04's pre-history
    strata by fine_local (exact recent idleness). Both are pre-treatment."""
    c = h04lib.build_cells(P.D, np.arange(64), var=var)
    c.loc0 = c.s_base_local.copy()
    n_loc = h04lib.N_LOCAL
    aidx = c.s_base_full // h04lib.N_LOCAL
    loc = c.s_base_local
    if fine:
        loc = fine_local(P, c); n_loc = N_FINE
    if pause_matched:
        pb = cell_pause_bins(P, c)
        loc = loc * N_PB + pb; n_loc = n_loc * N_PB
        c.pb = pb
    c.s_base_local = loc
    c.s_base_full = aidx * n_loc + loc
    c.n_loc = n_loc
    old = h04lib.N_STRATA_LOCAL
    h04lib.N_STRATA_LOCAL = n_loc * 3
    try:
        ctl = h04lib.control_means(c, 64)
    finally:
        h04lib.N_STRATA_LOCAL = old
    return c, ctl


def matched(c, ctl, ids, nd, name, nb_adjust=0):
    old = h04lib.N_STRATA_LOCAL
    h04lib.N_STRATA_LOCAL = getattr(c, "n_loc", h04lib.N_LOCAL) * 3
    try:
        return h04lib.matched_response(c, ctl, ids, nd, name, len(ids), nb_adjust)
    finally:
        h04lib.N_STRATA_LOCAL = old


# ----------------------------------------------------------------------------- read-out of treated cells

def treated_readout(P: Prep, c, ids: np.ndarray, kick_rows: pl.DataFrame):
    """For treated cells: kick time, read-out minute (obs / sched), pause state at the kick.

    kick_rows: rows (day, row, minute, msg) of the kicks; the earliest message in the cell's minute is used."""
    first = (kick_rows.sort("msg").group_by(["day", "row", "minute"]).agg(pl.col("msg").first()))
    key = {(int(a), int(b), int(m)): int(x) for a, b, m, x in first.select("day", "row", "minute", "msg").iter_rows()}
    n = len(ids)
    out = {k: np.full(n, np.nan) for k in ("tau_obs", "tau_sched", "W_obs", "rem_s")}
    out["paused"] = np.zeros(n, bool)
    out["day"] = c.day[ids].astype(np.int64)
    for j, cid in enumerate(ids):
        k, i, m = int(c.day[cid]), int(c.row[cid]), int(c.minute[cid])
        msg = key.get((k, i, m))
        d = P.D[k]
        tr = P.T.get((int(d.agents[i]), d.pt_date))
        if msg is None or tr is None:
            continue
        tm = P.msg_t.get(msg) if isinstance(P.msg_t, dict) else None
        if tm is None:
            continue
        mstart = P.win_us[k] + m * 60 * US
        idx = int(readout_idx(tr, np.array([tm]))[0])
        inp, rem, exp_ = pause_state(tr, np.array([tm]))
        if idx < len(tr.t):
            out["W_obs"][j] = (tr.t[idx] - tm) / US
            out["tau_obs"][j] = (tr.t[idx] - mstart) // (60 * US)
        out["paused"][j] = bool(inp[0])
        out["rem_s"][j] = float(rem[0])
        if inp[0]:
            out["tau_sched"][j] = (exp_[0] + 10 * US - mstart) // (60 * US)
        else:
            out["tau_sched"][j] = out["tau_obs"][j]
    return out


def renewal_tau(T: dict, rng, n: int = 20000) -> np.ndarray:
    """Read-out minute for random arrivals: length-biased call interval, uniform position, plus the call latency."""
    D, L = [], []
    for tr in T.values():
        if len(tr.t) < 3:
            continue
        dlt = tr.s[2:] - tr.s[1:-1]                                  # s_k - s_{k-1}, k >= 2 (both finite)
        lat = tr.t[2:] - tr.s[2:]                                    # call latency of turn k
        ok = (dlt > 0) & (dlt < 6 * 3600 * US) & (lat >= 0)
        D.append(dlt[ok]); L.append(lat[ok])
    D = np.concatenate(D).astype(float); L = np.concatenate(L).astype(float)
    p = D / D.sum()
    k = rng.choice(len(D), size=n, p=p)
    w = rng.uniform(0, 1, n) * D[k] + L[k]
    u = rng.uniform(0, 60 * US, n)
    return np.floor((u + w) / (60 * US))


def F_from_tau(tau: np.ndarray) -> np.ndarray:
    """F(tau) = P(read-out minute <= tau) for tau = LAGS index range (array over LAGS); NaN taus count as never."""
    t = np.asarray(tau, float)
    t = np.where(np.isfinite(t), t, 1e9)
    return np.array([(t <= x).mean() for x in LAGS])


def F_boot(tau: np.ndarray, day: np.ndarray, W: np.ndarray, nd: int) -> np.ndarray:
    """Bootstrap rows of F using the same day weights as the kernel."""
    t = np.where(np.isfinite(tau), tau, 1e9)
    ind = (t[:, None] <= LAGS[None, :]).astype(float)               # cells x lags
    num = np.zeros((nd, len(LAGS))); cnt = np.zeros(nd)
    np.add.at(num, day, ind); np.add.at(cnt, day, 1.0)
    with np.errstate(invalid="ignore", divide="ignore"):
        return (W @ num) / (W @ cnt)[:, None]


# ----------------------------------------------------------------------------- statistics

def phi(G: np.ndarray, a: int, b: int) -> np.ndarray:
    """Onset fraction per row: mean G[a..b] / mean G[16..45] (G indexed by LAGS)."""
    num = np.nanmean(G[..., L0 + a:L0 + b + 1], axis=-1)
    den = np.nanmean(G[..., L0 + PLATEAU[0]:L0 + PLATEAU[1] + 1], axis=-1)
    with np.errstate(invalid="ignore", divide="ignore"):
        return num / den


def t_half(F: np.ndarray) -> float:
    f = F[L0 + 1:L0 + 46]
    if not np.isfinite(f).all() or f[-1] <= 0:
        return np.nan
    k = np.nonzero(f >= 0.5 * f[-1])[0]
    return float(k[0] + 1) if len(k) else np.nan


def _wls_A(g, f, w):
    den = np.sum(w * f * f)
    return float(np.sum(w * g * f) / den) if den > 0 else 0.0


def shape_ctx_d(tau_r: np.ndarray, theta: float) -> np.ndarray:
    t = np.where(np.isfinite(tau_r), tau_r, 1e9)
    x = TAU[None, :] - t[:, None]
    return np.where(x >= 0, np.exp(-np.clip(x, 0, None) / theta), 0.0).mean(0)


THETAS = np.exp(np.linspace(np.log(1.0), np.log(300.0), 25))
GK = np.exp(np.linspace(np.log(0.3), np.log(12.0), 18))
GT = np.exp(np.linspace(np.log(0.3), np.log(40.0), 18))
DELAYS = np.arange(1, 31)
MODELS = ["ctx", "ctx_step", "ctx_d", "imm", "imm_hr", "delay", "delay_hr", "hawkes", "gamma"]
N_PAR = {"ctx": 1, "ctx_step": 1, "ctx_d": 2, "imm": 1, "imm_hr": 1, "delay": 2, "delay_hr": 2, "hawkes": 2, "gamma": 3}


def make_X(sub: np.ndarray, tau: np.ndarray, Mhr: np.ndarray, CM: np.ndarray) -> dict:
    """Model inputs over TAU for a subset of treated cells: F (step), Fhr (headroom-weighted), tau_r, E0 (controls)."""
    sl = slice(L0 + 1, L0 + 46)
    return {"F": F_from_tau(tau[sub])[sl], "Fhr": np.nanmean(Mhr[sub], 0)[sl], "tau": tau[sub],
            "E0": np.nanmean(CM[sub], 0)[sl]}


def _grid(g, w, shapes):
    best = None
    for par, f in shapes:
        a = _wls_A(g, f, w); sse = np.sum(w * (g - a * f) ** 2)
        if best is None or sse < best[0]:
            best = (sse, a, par)
    return best


def fit_models(g: np.ndarray, w: np.ndarray, X: dict) -> dict:
    """Fit each model to kernel g over TAU. Returns {model: (params, fn(X_eval) -> curve over TAU)}."""
    fits = {}
    A = _wls_A(g, X["Fhr"], w); fits["ctx"] = ({"A": A}, lambda Y, A=A: A * Y["Fhr"])
    A = _wls_A(g, X["F"], w); fits["ctx_step"] = ({"A": A}, lambda Y, A=A: A * Y["F"])
    sse, a, th = _grid(g, w, [(th, shape_ctx_d(X["tau"], th)) for th in THETAS])
    fits["ctx_d"] = ({"A": a, "theta": th}, lambda Y, a=a, th=th: a * shape_ctx_d(Y["tau"], th))
    one = np.ones(len(TAU))
    A = _wls_A(g, one, w); fits["imm"] = ({"A": A}, lambda Y, A=A: A * np.ones(len(TAU)))
    A = _wls_A(g, 1 - X["E0"], w); fits["imm_hr"] = ({"A": A}, lambda Y, A=A: A * (1 - Y["E0"]))
    sse, a, d = _grid(g, w, [(d, (TAU >= d).astype(float)) for d in DELAYS])
    fits["delay"] = ({"A": a, "d": int(d)}, lambda Y, a=a, d=d: a * (TAU >= d).astype(float))
    sse, a, d = _grid(g, w, [(d, (TAU >= d) * (1 - X["E0"])) for d in DELAYS])
    fits["delay_hr"] = ({"A": a, "d": int(d)}, lambda Y, a=a, d=d: a * (TAU >= d) * (1 - Y["E0"]))
    sse, a, th = _grid(g, w, [(th, np.exp(-(TAU - 1) / th)) for th in THETAS])
    fits["hawkes"] = ({"A": a, "theta": th}, lambda Y, a=a, th=th: a * np.exp(-(TAU - 1) / th))
    sse, a, kt = _grid(g, w, [((k, th), gamma_dist.cdf(TAU, k, scale=th)) for k in GK for th in GT])
    fits["gamma"] = ({"A": a, "k": kt[0], "theta": kt[1]},
                     lambda Y, a=a, k=kt[0], th=kt[1]: a * gamma_dist.cdf(TAU, k, scale=th))
    return fits


def kernel_weights(Gb: np.ndarray) -> np.ndarray:
    v = np.nanvar(Gb[1:, L0 + 1:L0 + 46], axis=0)
    v = np.where(np.isfinite(v) & (v > 0), v, np.nan)
    floor = np.nanmedian(v) * 0.1 if np.isfinite(v).any() else 1.0
    return 1.0 / np.maximum(np.nan_to_num(v, nan=np.nanmax(v) if np.isfinite(v).any() else 1.0), floor)


def cross_validate(r, Gb, tau, day, nd, Mhr, CM, n_split: int = 100, seed: int = 0) -> dict:
    """Day-split CV: fit on half the days' kernel, score the other half's (weighted SSE over tau = 1..45). The
    zero-parameter inputs (F, Fhr, E0) of the scored half come from that half's own cells (no response data)."""
    rng = np.random.default_rng(seed)
    w = kernel_weights(Gb)
    days_with = np.unique(day)
    if len(days_with) < 4:
        return {"n_split": 0}
    sse = {m: [] for m in MODELS}
    for _ in range(n_split):
        perm = rng.permutation(days_with)
        A_, B_ = perm[: len(perm) // 2], perm[len(perm) // 2:]
        res = []
        for tr_d, te_d in ((A_, B_), (B_, A_)):
            Wa = np.zeros((1, nd)); Wa[0, tr_d] = 1
            Wb = np.zeros((1, nd)); Wb[0, te_d] = 1
            ga = h04lib.curves(r, Wa)[0, L0 + 1:L0 + 46]; gb = h04lib.curves(r, Wb)[0, L0 + 1:L0 + 46]
            if not (np.isfinite(ga).all() and np.isfinite(gb).all()):
                continue
            ma, mb = np.isin(day, tr_d), np.isin(day, te_d)
            fits = fit_models(ga, w, make_X(ma, tau, Mhr, CM))
            Xb = make_X(mb, tau, Mhr, CM)
            res.append({m: float(np.sum(w * (gb - fits[m][1](Xb)) ** 2)) for m in MODELS})
        if res:
            for m in MODELS:
                sse[m].append(np.mean([x[m] for x in res]))
    out = {"n_split": len(sse["ctx"])}
    if not out["n_split"]:
        return out
    S = {m: np.array(v) for m, v in sse.items()}
    out["median_sse"] = {m: float(np.median(S[m])) for m in MODELS}
    out["ratio_to_ctx"] = {m: float(np.median(S[m] / S["ctx"])) for m in MODELS}
    out["ctx_wins_share"] = {m: float(np.mean(S["ctx"] < S[m])) for m in MODELS if m != "ctx"}
    stack = np.stack([S[x] for x in MODELS])
    out["best_share"] = {m: float(np.mean(np.argmin(stack, 0) == i)) for i, m in enumerate(MODELS)}
    return out


def full_fit(Gb, tau, Mhr, CM) -> dict:
    w = kernel_weights(Gb)
    g = np.nan_to_num(Gb[0, L0 + 1:L0 + 46])
    X = make_X(np.ones(len(tau), bool), tau, Mhr, CM)
    fits = fit_models(g, w, X)
    return {m: {"params": {k: float(v) for k, v in fits[m][0].items()}, "curve": fits[m][1](X).tolist(),
                "wsse": float(np.sum(w * (g - fits[m][1](X)) ** 2)), "n_par": N_PAR[m]} for m in MODELS}


def shape_tests(Gb: np.ndarray, Fb: dict, W: np.ndarray) -> dict:
    """Phi(1,5), Phi(6,15) measured vs predicted (each F version), with paired bootstrap differences."""
    out = {}
    plat = np.nanmean(Gb[:, L0 + PLATEAU[0]:L0 + PLATEAU[1] + 1], axis=1)
    out["plateau_mean"] = ci(plat)
    out["plateau_significant"] = bool(np.isfinite(out["plateau_mean"][1]) and out["plateau_mean"][1] > 0)
    out["A30"] = ci(np.nansum(Gb[:, L0 + 1:L0 + 31], 1))
    out["A60"] = ci(np.nansum(Gb[:, L0 + 1:L0 + 61], 1))
    for (a, b) in ((1, 5), (6, 15)):
        pm = phi(Gb, a, b)
        out[f"phi_{a}_{b}"] = ci(pm)
        for kname, F in Fb.items():
            pp = phi(F, a, b)
            out[f"phi_{a}_{b}_pred_{kname}"] = ci(pp)
            out[f"phi_{a}_{b}_diff_{kname}"] = ci(pm - pp)
            out[f"phi_{a}_{b}_imm_excluded"] = bool(np.isfinite(ci(pm)[2]) and ci(pm)[2] < 1)
    for kname, F in Fb.items():
        out[f"t_half_{kname}"] = t_half(F[0])
    out["share_after5"] = ci(np.nansum(Gb[:, L0 + 6:L0 + 31], 1) / np.nansum(Gb[:, L0 + 1:L0 + 31], 1))
    return out

# ----------------------------------------------------------------------------- headroom after read-out

H_LEN = 61


def hkey_cells(P: Prep, c, ids) -> np.ndarray:
    """Headroom key of cells: 16 * state class at m-1 (0 silent, 1 idle/paused, 2 active) + inactive minutes in
    [m-15, m-1] (0..15). Finer than H04's strata on recent idleness, which predicts post-wake idleness."""
    out = np.zeros(len(ids), np.int64)
    for j, cid in enumerate(ids):
        k, i, m = int(c.day[cid]), int(c.row[cid]), int(c.minute[cid])
        st = P.D[k].state[i]
        s1 = int(st[m - 1])
        cls = 0 if s1 == 1 else (1 if s1 == 2 else 2)
        out[j] = cls * 16 + int((st[m - 15:m] <= 2).sum())
    return out


def headroom_profiles(P: Prep, c, max_cells: int = 150000, seed: int = 0) -> dict:
    """Post-read-out inactivity profile h(u), u = 0..60 min, from control-eligible cells (no kick): for a cell at minute m,
    the 'wake' is the agent's first turn after m + 30 s; h(u) = P(inactive at wake minute + u). Kept per headroom key
    (hkey_cells), with a fallback by state class. Treated cells use their own key's profile (no kick data enters h)."""
    rng = np.random.default_rng(seed)
    el = np.nonzero(c.eligible)[0]
    if len(el) > max_cells:
        el = rng.choice(el, max_cells, replace=False)
    keys = hkey_cells(P, c, el)
    acc = np.zeros((48, H_LEN)); cnt = np.zeros((48, H_LEN))
    accc = np.zeros((3, H_LEN)); cntc = np.zeros((3, H_LEN))
    for cid, key in zip(el, keys):
        k, i, m = int(c.day[cid]), int(c.row[cid]), int(c.minute[cid])
        d = P.D[k]
        tr = P.T.get((int(d.agents[i]), d.pt_date))
        if tr is None:
            continue
        t = P.win_us[k] + (m * 60 + 30) * US
        j = np.searchsorted(tr.t, t, side="right")
        if j >= len(tr.t):
            continue
        mw = int((tr.t[j] - P.win_us[k]) // (60 * US))
        seg = (d.state[i, mw:mw + H_LEN] <= 2)
        L = len(seg)
        acc[key, :L] += seg; cnt[key, :L] += 1
        accc[key // 16, :L] += seg; cntc[key // 16, :L] += 1
    with np.errstate(invalid="ignore", divide="ignore"):
        hs = acc / cnt
        hc = accc / cntc
    return {"strata": hs, "n": cnt[:, 0], "class": hc}


def treated_class(P: Prep, c, ids) -> np.ndarray:
    return np.array([int(P.D[int(c.day[j])].state[int(c.row[j]), int(c.minute[j]) - 1] >= 3) for j in ids], np.int64)


def F_hr_cells(tau: np.ndarray, cls: np.ndarray, h: dict, strata: np.ndarray | None = None, min_n: int = 30) -> np.ndarray:
    """Per cell and lag: 1(tau >= tau_r) * h(tau - tau_r), h from the cell's stratum (fallback: its class)."""
    t = np.where(np.isfinite(tau), tau, 1e9)
    u = LAGS[None, :] - t[:, None]
    ok = u >= 0
    ui = np.clip(u, 0, H_LEN - 1).astype(int)
    out = np.zeros((len(t), len(LAGS)))
    for j in range(len(t)):
        prof = None
        if strata is not None and strata[j] < len(h["n"]) and h["n"][strata[j]] >= min_n:
            prof = h["strata"][strata[j]]
        if prof is None or not np.isfinite(prof).all():
            prof = h["class"][min(int(cls[j]), len(h["class"]) - 1)]
        prof = np.nan_to_num(prof, nan=np.nanmean(prof) if np.isfinite(prof).any() else 0.5)
        out[j] = np.where(ok[j], prof[ui[j]], 0.0)
    return out


def F_hr_boot(M: np.ndarray, day: np.ndarray, W: np.ndarray, nd: int) -> np.ndarray:
    num = np.zeros((nd, len(LAGS))); cnt = np.zeros(nd)
    np.add.at(num, day, M); np.add.at(cnt, day, 1.0)
    with np.errstate(invalid="ignore", divide="ignore"):
        return (W @ num) / (W @ cnt)[:, None]


def control_matrix(c, ctl, ids) -> np.ndarray:
    """Matched-control trajectory per treated cell (cells x LAGS): the no-kick baseline used by H04's G."""
    old = h04lib.N_STRATA_LOCAL
    h04lib.N_STRATA_LOCAL = getattr(c, "n_loc", h04lib.N_LOCAL) * 3
    try:
        sf, sl = c.strata(ids, 0)
        use_full = ctl.cnt_full[sf, L0 + 1] >= h04lib.MIN_CTRL
        cm = np.where(use_full[:, None], ctl.mean_full[sf], ctl.mean_local[sl])
    finally:
        h04lib.N_STRATA_LOCAL = old
    return cm
