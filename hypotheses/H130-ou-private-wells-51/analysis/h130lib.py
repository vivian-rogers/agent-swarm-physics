"""H130 estimators: Ornstein-Uhlenbeck wells with read kicks on the per-call clock (#51).

Data (scheme/build.py): statements (srow, agent, t, pt_date, room, unit_id, turn_id, t_call, n, nf, nc), reads (reader,
turn_id, t_call, n, nf, nc, sender, srow_m, t_post, room_m, pt_date, unit_id), calls.

Objects (card, Observables):
  h_i        well centre, leave-day-out mean of agent i's chat statement vectors over all non-holdout #51 days
  x_B        z_B - h_i(day(B))
  u_m        unit(z_m - c_m), c_m = room consensus within +-15 min of t_m, leaving out the sender and the reader
  C(tau)     own autocorrelation: mean x_B . x_B' over same-agent-day pairs, tau = n_B' - n_B >= 1 call
  K(tau)     kick response: mean x_B . u_m over (statement B, message m read at call n_r <= n_B), tau = n_B - n_r
  J_K        read jump: mean y(read at the producing call, posted in (T_c - d, T_c)) - mean y(in flight, (T_c, t_B))
Accumulators are kept per agent-day so the agent-day block bootstrap is a weighted sum.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import sys  # noqa: E402
import warnings  # noqa: E402
from dataclasses import dataclass  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy.optimize import curve_fit  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
SH = ROOT / "data/processed/shared"
DATA = ROOT / "data/processed/H130-ou-private-wells-51"

# lag bins (calls): 0 | 1-3 | 4-7 | 8-15 | 16-31 | 32-63 | 64-127 | 128-255 | 256-511 | 512-1023
EDGES_N = np.array([0, 1, 4, 8, 16, 32, 64, 128, 256, 512, 1024])
# lag bins (seconds, between call starts)
EDGES_S = np.array([0, 30, 60, 120, 240, 480, 960, 1920, 3840, 7680, 15360, 30720])
WIN_S = 900.0          # consensus half-window
D_MAX = 300.0          # mirror window cap for J_K
MIN_WELL = 10          # statements outside the day needed for a well centre
VEC = {"style_resid_period": "style_resid_period32", "white32": "white32"}


# ---------------------------------------------------------------------------------------------- loading
@dataclass
class Data:
    st: pl.DataFrame            # all statements (sorted), row index = position in Z
    rd: pl.DataFrame            # reads with column mi (row of the read message in st)
    Z: np.ndarray               # statement vectors (n x 32)
    H: np.ndarray               # well centre per statement row (nan where undefined)
    ok: np.ndarray              # well defined
    W: dict | None = None       # (agent, day) -> leave-day-out well over ALL loaded statements (kept by subsets)


def load(model: str = "bge_small", variant: str = "style_resid_period", root: Path = DATA,
         drop_kickoff: bool = False, Z_override: np.ndarray | None = None, st=None, rd=None) -> Data:
    st = (pl.read_parquet(root / "statements.parquet") if st is None else st)
    st = st.sort("agent", "t").with_row_index("i")
    rd = pl.read_parquet(root / "reads.parquet") if rd is None else rd
    if drop_kickoff:
        st = st.filter(pl.col("pt_date") != "2026-07-06").drop("i").with_row_index("i")
        rd = rd.filter(pl.col("pt_date") != "2026-07-06")
    if Z_override is None:
        V = np.load(SH / f"embeddings/statements_{VEC[variant]}_{model}.npy", mmap_mode="r")
        Z = np.asarray(V[st["srow"].to_numpy()], dtype=np.float64)
    else:
        Z = Z_override
    pos = pl.DataFrame({"srow_m": st["srow"], "mi": st["i"]})
    rd = rd.join(pos, on="srow_m", how="inner")
    H, ok = well_centres(st, Z)
    D = Data(st=st, rd=rd, Z=Z, H=H, ok=ok)
    D.W = day_wells(D)
    return D


def well_centres(st: pl.DataFrame, Z: np.ndarray, min_n: int = MIN_WELL):
    a = st["agent"].to_numpy()
    d = st["pt_date"].to_numpy()
    H = np.full_like(Z, np.nan)
    ok = np.zeros(len(a), bool)
    for ag in np.unique(a):
        ia = np.flatnonzero(a == ag)
        tot = Z[ia].sum(0)
        n = len(ia)
        for dd in np.unique(d[ia]):
            idd = ia[d[ia] == dd]
            m = n - len(idd)
            if m >= min_n:
                H[idd] = (tot - Z[idd].sum(0)) / m
                ok[idd] = True
    return H, ok


# ---------------------------------------------------------------------------------------------- consensus
class Consensus:
    """Room consensus sums for leave-sender-and-reader-out directions."""

    def __init__(self, st: pl.DataFrame, Z: np.ndarray, mode: str = "past"):
        self.mode = mode          # "past": [t - WIN_S, t); "sym": [t - WIN_S, t + WIN_S]
        self.t = st["t"].dt.epoch("us").to_numpy() / 1e6
        self.room = st["room"].to_numpy()
        self.agent = st["agent"].to_numpy()
        self.Z = Z
        self.rooms = {}
        for r in np.unique(self.room):
            idx = np.flatnonzero(self.room == r)
            idx = idx[np.argsort(self.t[idx], kind="stable")]
            cs = np.vstack([np.zeros((1, Z.shape[1])), np.cumsum(Z[idx], 0)])
            self.rooms[r] = (self.t[idx], cs)
        self.ra = {}
        for r in np.unique(self.room):
            for ag in np.unique(self.agent[self.room == r]):
                idx = np.flatnonzero((self.room == r) & (self.agent == ag))
                idx = idx[np.argsort(self.t[idx], kind="stable")]
                cs = np.vstack([np.zeros((1, Z.shape[1])), np.cumsum(Z[idx], 0)])
                self.ra[(r, ag)] = (self.t[idx], cs)

    def _wsum(self, key_t, cs, t, t_hi=None):
        lo = np.searchsorted(key_t, t - WIN_S, "left")
        if t_hi is not None:
            hi = np.searchsorted(key_t, t_hi, "left")
        elif self.mode == "past":
            hi = np.searchsorted(key_t, t, "left")
        else:
            hi = np.searchsorted(key_t, t + WIN_S, "right")
        hi = np.maximum(hi, lo)
        return cs[hi] - cs[lo], (hi - lo).astype(float)

    def window(self, room: np.ndarray, t: np.ndarray, leave: list[np.ndarray], t_hi=None):
        """Mean of statements in (room, window around t), leaving out the agents in each array of `leave`.
        Window: [t - WIN_S, t) ('past'), [t - WIN_S, t + WIN_S] ('sym'), or [t - WIN_S, t_hi) when t_hi is given."""
        S = np.zeros((len(t), self.Z.shape[1]))
        N = np.zeros(len(t))
        for r in np.unique(room):
            k = np.flatnonzero(room == r)
            if r not in self.rooms:
                continue
            th = None if t_hi is None else t_hi[k]
            s, n = self._wsum(*self.rooms[r], t[k], th)
            S[k] += s
            N[k] += n
            for lv in leave:
                for ag in np.unique(lv[k]):
                    kk = k[lv[k] == ag]
                    if (r, ag) in self.ra:
                        s2, n2 = self._wsum(*self.ra[(r, ag)], t[kk], None if t_hi is None else t_hi[kk])
                        S[kk] -= s2
                        N[kk] -= n2
        return S, N

    def next_time(self, agent: np.ndarray, t: np.ndarray):
        """Time of the agent's first statement (any room) strictly after t (inf if none)."""
        if not hasattr(self, "_at"):
            self._at = {a: np.sort(self.t[self.agent == a]) for a in np.unique(self.agent)}
        out = np.full(len(t), np.inf)
        for a in np.unique(agent):
            k = np.flatnonzero(agent == a)
            ts = self._at.get(a)
            if ts is None or len(ts) == 0:
                continue
            j = np.searchsorted(ts, t[k], "right")
            ok = j < len(ts)
            out[k[ok]] = ts[j[ok]]
        return out

    def dirs(self, mi: np.ndarray, reader: np.ndarray, min_n: int = 3):
        """u_m = unit(z_m - c_m) with c_m leaving out the sender and the reader.
        mode 'trunc': window [t_m - WIN_S, min(t_m + WIN_S, reader's next statement after t_m))."""
        room, t, snd = self.room[mi], self.t[mi], self.agent[mi]
        t_hi = np.minimum(t + WIN_S, self.next_time(reader, t)) if self.mode == "trunc" else None
        S, N = self.window(room, t, [snd, reader], t_hi)
        good = N >= min_n
        c = np.where(good[:, None], S / np.maximum(N, 1)[:, None], 0.0)
        u = self.Z[mi] - c
        nr = np.linalg.norm(u, axis=1)
        good &= nr > 1e-9
        u = u / np.maximum(nr, 1e-9)[:, None]
        return u, good


# ---------------------------------------------------------------------------------------------- accumulators
@dataclass
class Acc:
    """Per agent-day sums for each lag bin."""
    keys: list              # (unit, agent, day)
    unit: np.ndarray
    S: np.ndarray           # (n_ad, n_bins) sum of products
    S2: np.ndarray
    N: np.ndarray
    T: np.ndarray           # sum of tau
    edges: np.ndarray


def _bin(tau, edges):
    b = np.searchsorted(edges, tau, "right") - 1
    b[(tau < edges[0]) | (tau >= edges[-1])] = -1
    return b


def _acc_add(S, S2, N, T, row, b, y, tau):
    m = b >= 0
    if not m.any():
        return
    nb = S.shape[1]
    S[row] += np.bincount(b[m], weights=y[m], minlength=nb)
    S2[row] += np.bincount(b[m], weights=y[m] ** 2, minlength=nb)
    N[row] += np.bincount(b[m], minlength=nb)
    T[row] += np.bincount(b[m], weights=tau[m], minlength=nb)


def agent_days(D: Data):
    st = D.st.filter(pl.Series(D.ok))
    g = st.group_by("unit_id", "agent", "pt_date", maintain_order=True).agg(pl.col("i"))
    return g.sort("unit_id", "agent", "pt_date")


def autocorr(D: Data, X: np.ndarray, clock: str = "n", edges=None, split=None) -> Acc | tuple:
    """O1: pairs of one agent-day's statements; tau = n' - n >= 1 (calls) or t_call difference (seconds) > 0.
    split='reset': returns (within, crossed) accumulators by whether nf differs between the two calls."""
    edges = (EDGES_N if clock == "n" else EDGES_S) if edges is None else edges
    g = agent_days(D)
    nb = len(edges) - 1
    shape = (g.height, nb)
    outs = [np.zeros(shape) for _ in range(4)] if split is None else [[np.zeros(shape) for _ in range(4)] for _ in range(2)]
    nn = D.st["n"].to_numpy()
    tc = D.st["t_call"].dt.epoch("us").to_numpy() / 1e6
    nf = D.st["nf"].to_numpy()
    for row, idx in enumerate(g["i"].to_list()):
        idx = np.asarray(idx)
        if len(idx) < 2:
            continue
        ii, jj = np.triu_indices(len(idx), 1)
        a, b_ = idx[ii], idx[jj]
        tau = (nn[b_] - nn[a]).astype(float) if clock == "n" else (tc[b_] - tc[a])
        tau = np.abs(tau)
        keep = tau >= (1 if clock == "n" else 1e-6)
        a, b_, tau = a[keep], b_[keep], tau[keep]
        y = np.einsum("ij,ij->i", X[a], X[b_])
        bins = _bin(tau, edges)
        if split is None:
            _acc_add(*outs, row, bins, y, tau)
        else:
            cr = nf[a] != nf[b_]
            _acc_add(*outs[0], row, np.where(~cr, bins, -1), y, tau)
            _acc_add(*outs[1], row, np.where(cr, bins, -1), y, tau)
    mk = lambda o: Acc(list(zip(g["unit_id"], g["agent"], g["pt_date"])), g["unit_id"].to_numpy(), *o, edges)  # noqa: E731
    return mk(outs) if split is None else (mk(outs[0]), mk(outs[1]))


def read_dirs(D: Data, C: Consensus):
    """u for every read (reader-left-out consensus) and a validity mask."""
    mi = D.rd["mi"].to_numpy()
    reader = D.rd["reader"].to_numpy()
    return C.dirs(mi, reader)


def kick_profile(D: Data, X: np.ndarray, U: np.ndarray, Uok: np.ndarray, clock: str = "n", edges=None,
                 sender_mask: np.ndarray | None = None, split=None, rival=None) -> Acc | tuple:
    """O2: (statement B, read m at n_r <= n_B, same agent-day). Bin 0 = read at the producing call.
    sender_mask: optional bool per read row (restrict reads). split='reset' -> (within, crossed)."""
    edges = (EDGES_N if clock == "n" else EDGES_S) if edges is None else edges
    g = agent_days(D)
    nb = len(edges) - 1
    shape = (g.height, nb)
    outs = [np.zeros(shape) for _ in range(4)] if split is None else [[np.zeros(shape) for _ in range(4)] for _ in range(2)]
    rd = D.rd.with_row_index("r")
    keep = Uok if sender_mask is None else (Uok & sender_mask)
    rd = rd.filter(pl.Series(keep))
    rg = {(a, d): (np.asarray(r)) for a, d, r in rd.group_by("reader", "pt_date").agg(pl.col("r")).iter_rows()}
    rn = D.rd["n"].to_numpy()
    rt = D.rd["t_call"].dt.epoch("us").to_numpy() / 1e6
    rf = D.rd["nf"].to_numpy()
    nn = D.st["n"].to_numpy()
    tc = D.st["t_call"].dt.epoch("us").to_numpy() / 1e6
    nf = D.st["nf"].to_numpy()
    for row, (ag, day, idx) in enumerate(zip(g["agent"].to_list(), g["pt_date"].to_list(), g["i"].to_list())):
        r = rg.get((ag, day))
        if r is None:
            continue
        idx = np.asarray(idx)
        Y = X[idx] @ U[r].T                          # (nB, nr)
        tau_n = nn[idx][:, None] - rn[r][None, :]
        valid = tau_n >= 0
        tau = tau_n.astype(float) if clock == "n" else (tc[idx][:, None] - rt[r][None, :])
        tau = np.where(valid, np.maximum(tau, 0), -1.0)
        bins = _bin(tau.ravel(), edges)
        bins[~valid.ravel()] = -1
        y = Y.ravel()
        if split is None:
            _acc_add(*outs, row, bins, y, tau.ravel())
        else:
            cr = (nf[idx][:, None] != rf[r][None, :]).ravel()
            _acc_add(*outs[0], row, np.where(~cr, bins, -1), y, tau.ravel())
            _acc_add(*outs[1], row, np.where(cr, bins, -1), y, tau.ravel())
    mk = lambda o: Acc(list(zip(g["unit_id"], g["agent"], g["pt_date"])), g["unit_id"].to_numpy(), *o, edges)  # noqa: E731
    return mk(outs) if split is None else (mk(outs[0]), mk(outs[1]))


def read_jump(D: Data, C: Consensus, X: np.ndarray, sender_class=None):
    """O3: per agent-day sums for the read arm and the in-flight arm at matched posting age.
    sender_class: optional function (reader array, sender array, t array) -> bool mask for a sender subset."""
    g = agent_days(D)
    st = D.st
    t = st["t"].dt.epoch("us").to_numpy() / 1e6
    tc = st["t_call"].dt.epoch("us").to_numpy() / 1e6
    room = st["room"].to_numpy()
    agent = st["agent"].to_numpy()
    turn = st["turn_id"].to_numpy()
    # read arm: reads at the producing call
    rd = D.rd
    rturn = rd["turn_id"].to_numpy()
    rpost = rd["t_post"].dt.epoch("us").to_numpy() / 1e6
    by_turn = {}
    for k, tt in enumerate(rturn):
        by_turn.setdefault(int(tt), []).append(k)
    # room timelines for in-flight
    order = np.argsort(t, kind="stable")
    room_t = {r: order[room[order] == r] for r in np.unique(room)}
    rows = {key: r for r, key in enumerate(zip(g["unit_id"], g["agent"], g["pt_date"]))}
    ad_of = {}
    for r, idx in enumerate(g["i"].to_list()):
        for k in idx:
            ad_of[k] = r
    pr_B, pr_m, pr_reader, kind = [], [], [], []
    for B in ad_of:
        Tc, tB = tc[B], t[B]
        d = min(max(tB - Tc, 1.0), D_MAX)
        for k in by_turn.get(int(turn[B]), []):
            if rpost[k] > Tc - d:
                pr_B.append(B)
                pr_m.append(int(rd["mi"][k]))
                kind.append(0)
        rt = room_t.get(room[B])
        if rt is None:
            continue
        lo = np.searchsorted(t[rt], Tc, "right")
        hi = np.searchsorted(t[rt], min(tB, Tc + D_MAX), "left")
        for m in rt[lo:hi]:
            if agent[m] != agent[B]:
                pr_B.append(B)
                pr_m.append(int(m))
                kind.append(1)
    pr_B = np.array(pr_B, int)
    pr_m = np.array(pr_m, int)
    kind = np.array(kind, int)
    U, ok = C.dirs(pr_m, agent[pr_B])
    if sender_class is not None:
        ok &= sender_class(agent[pr_B], agent[pr_m], t[pr_B])
    y = np.einsum("ij,ij->i", X[pr_B], U)
    nad = g.height
    out = {}
    for name, kk in (("read", 0), ("if", 1)):
        m = ok & (kind == kk)
        rr = np.array([ad_of[b] for b in pr_B[m]], int)
        out[f"S_{name}"] = np.bincount(rr, weights=y[m], minlength=nad)
        out[f"S2_{name}"] = np.bincount(rr, weights=y[m] ** 2, minlength=nad)
        out[f"N_{name}"] = np.bincount(rr, minlength=nad).astype(float)
    out["unit"] = g["unit_id"].to_numpy()
    out["keys"] = list(rows)
    return out


# ---------------------------------------------------------------------------------------------- statistics
def expfit(tau, y, se, plateau: bool = True):
    """Weighted LS of y = A exp(-g tau) + B (B = 0 if not plateau). Returns dict(A, g, B, ok)."""
    m = np.isfinite(y) & np.isfinite(se) & (se > 0) & np.isfinite(tau)
    tau, y, se = tau[m], y[m], se[m]
    if len(tau) < (4 if plateau else 3):
        return {"A": np.nan, "g": np.nan, "B": np.nan, "ok": False}
    f = (lambda x, A, g, B: A * np.exp(-g * x) + B) if plateau else (lambda x, A, g: A * np.exp(-g * x))
    best = None
    for g0 in (1e-3, 3e-3, 1e-2, 3e-2, 1e-1):
        if tau.max() > 100 * 30:          # seconds clock: rescale starting rates
            g0 = g0 / 40
        p0 = [max(y[0] - (y[-1] if plateau else 0), 1e-6), g0] + ([y[-1]] if plateau else [])
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                lb = [-np.inf, 1e-6] + ([-np.inf] if plateau else [])
                ub = [np.inf, 5.0] + ([np.inf] if plateau else [])
                p, _ = curve_fit(f, tau, y, p0=p0, sigma=se, absolute_sigma=True, bounds=(lb, ub), maxfev=20000)
            r = np.sum(((f(tau, *p) - y) / se) ** 2)
            if best is None or r < best[1]:
                best = (p, r)
        except Exception:  # noqa: BLE001
            continue
    if best is None:
        return {"A": np.nan, "g": np.nan, "B": np.nan, "ok": False}
    p, r = best
    return {"A": float(p[0]), "g": float(p[1]), "B": float(p[2]) if plateau else 0.0, "ok": True, "chi2": float(r),
            "nbins": int(len(tau))}


def profile(acc: Acc, w: np.ndarray | None = None, start_bin: int = 0):
    """Bin means, cluster SEs (agent-day) and bin-mean tau, with optional agent-day weights."""
    w = np.ones(acc.S.shape[0]) if w is None else w
    S = (w[:, None] * acc.S).sum(0)
    N = (w[:, None] * acc.N).sum(0)
    T = (w[:, None] * acc.T).sum(0)
    mean = np.where(N > 0, S / np.maximum(N, 1), np.nan)
    tau = np.where(N > 0, T / np.maximum(N, 1), np.nan)
    # cluster SE of a ratio estimator: residual sums per agent-day
    R = acc.S - mean[None, :] * acc.N
    var = (w[:, None] * R ** 2).sum(0) / np.maximum(N, 1) ** 2
    se = np.sqrt(var)
    sl = slice(start_bin, None)
    return tau[sl], mean[sl], se[sl], N[sl]


def boot_weights(unit: np.ndarray, B: int, seed: int):
    """Agent-day block bootstrap within unit: multiplicity weights (B x n_ad)."""
    rng = np.random.default_rng(seed)
    n = len(unit)
    W = np.zeros((B, n))
    for u in np.unique(unit):
        idx = np.flatnonzero(unit == u)
        for b in range(B):
            W[b] += np.bincount(rng.choice(idx, len(idx)), minlength=n)
    return W


def rates(accC: Acc, accK: Acc, mask: np.ndarray, Bw: np.ndarray | None, plateau: bool = True, min_n: int = 30):
    """gamma_auto (bins >= 1 of C) and gamma_kick (bins >= 0 of K) on agent-days in mask, with bootstrap draws."""
    def one(w):
        tC, mC, sC, nC = profile(accC, w, 1)
        tK, mK, sK, nK = profile(accK, w, 0)
        sC = np.where(nC >= min_n, sC, np.nan)
        sK = np.where(nK >= min_n, sK, np.nan)
        return expfit(tC, mC, sC, plateau), expfit(tK, mK, sK, plateau)
    w0 = mask.astype(float)
    fa, fk = one(w0)
    res = {"auto": fa, "kick": fk, "rho": fk["g"] / fa["g"] if fa["ok"] and fk["ok"] else np.nan}
    if Bw is not None:
        ga, gk = [], []
        for w in Bw:
            a, k = one(w * w0)
            ga.append(a["g"])
            gk.append(k["g"])
        ga, gk = np.array(ga), np.array(gk)
        res["boot_auto"], res["boot_kick"] = ga, gk
        rr = gk / ga
        res["ci_auto"] = np.nanpercentile(ga, [2.5, 97.5]).tolist()
        res["ci_kick"] = np.nanpercentile(gk, [2.5, 97.5]).tolist()
        res["ci_rho95"] = np.nanpercentile(rr, [2.5, 97.5]).tolist()
        res["ci_rho90"] = np.nanpercentile(rr, [5, 95]).tolist()
        res["se_lnrho"] = float(np.nanstd(np.log(rr[(rr > 0) & np.isfinite(rr)]))) if np.any(rr > 0) else np.nan
        res["frac_fit"] = float(np.mean(np.isfinite(rr)))
    return res


def jump_stats(J: dict, mask: np.ndarray, Bw: np.ndarray | None):
    def one(w):
        r = (w * J["S_read"]).sum() / max((w * J["N_read"]).sum(), 1)
        f = (w * J["S_if"]).sum() / max((w * J["N_if"]).sum(), 1)
        return r, f, r - f
    w0 = mask.astype(float)
    r, f, j = one(w0)
    out = {"K_read": r, "K_if": f, "J": j, "n_read": float((w0 * J["N_read"]).sum()), "n_if": float((w0 * J["N_if"]).sum())}
    if Bw is not None:
        bs = np.array([one(w * w0) for w in Bw])
        out["ci"] = np.percentile(bs[:, 2], [2.5, 97.5]).tolist()
        out["se"] = float(bs[:, 2].std())
        out["ci_read"] = np.percentile(bs[:, 0], [2.5, 97.5]).tolist()
    return out


def dl_pool(est: np.ndarray, se: np.ndarray):
    """DerSimonian-Laird random-effects pool. Returns (mu, se_mu, tau2, I2)."""
    m = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[m], se[m]
    if len(est) == 0:
        return np.nan, np.nan, np.nan, np.nan
    w = 1 / se ** 2
    mu_f = (w * est).sum() / w.sum()
    Q = (w * (est - mu_f) ** 2).sum()
    k = len(est)
    c = w.sum() - (w ** 2).sum() / w.sum()
    tau2 = max(0.0, (Q - (k - 1)) / c) if k > 1 and c > 0 else 0.0
    ws = 1 / (se ** 2 + tau2)
    mu = (ws * est).sum() / ws.sum()
    I2 = max(0.0, (Q - (k - 1)) / Q) if Q > 0 and k > 1 else 0.0
    return float(mu), float(np.sqrt(1 / ws.sum())), float(tau2), float(I2)


# ---------------------------------------------------------------------------------------------- Amendment A1 estimators
# Synthetic finding (A1): the message-direction profile K(tau) carries the common room drive (leak through x_B and
# z_m), so gamma_kick from K(tau) reads the drive's rate. Two drive-robust estimators replace it:
#   (a) gamma_kick from a distributed-lag regression of y_Bj = x_B . unit(h_j - h_i) (static pair direction) on counts
#       of j's messages read by i in lag bins, with pair fixed effects (the drive does not project systematically on a
#       static pair direction);
#   (b) gamma_auto from the own autocorrelation minus the cross-agent covariance at the same wall lag (the common drive
#       is shared by all agents; what is left is the agent's own well relaxation).
DOSE_EDGES = np.array([0, 1, 4, 16, 64, 256, 1024])     # bins after the two bin-0 columns: 1-3, 4-15, 16-63, 64-255, 256-1023
DOSE_NAMES = ["R0m", "R0o", "R1_3", "R4_15", "R16_63", "R64_255", "R256_1023", "U"]


def day_wells(D: Data, min_n: int = MIN_WELL) -> dict:
    """(agent, day) -> leave-day-out well centre over all statements in D."""
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


@dataclass
class Dose:
    pair: np.ndarray        # pair code
    ad: np.ndarray          # agent-day row (as agent_days order)
    unit: np.ndarray        # unit per agent-day row
    y: np.ndarray
    R: np.ndarray           # (rows, 8) regressors in DOSE_NAMES order
    tau: np.ndarray         # mean lag (calls) per dose bin (R0o..R256_1023)
    extra: dict


def dose_design(D: Data, X: np.ndarray, reset_split: bool = False, sender_filter=None) -> Dose:
    """Rows = (statement B of reader i, other agent j with a well that day).
    reset_split: adds columns for reads in lag 4-39 split by whether a forced reset of i lies between (cross/within)."""
    W = D.W if D.W is not None else day_wells(D)
    g = agent_days(D)
    st = D.st
    t = st["t"].dt.epoch("us").to_numpy() / 1e6
    tc = st["t_call"].dt.epoch("us").to_numpy() / 1e6
    nn = st["n"].to_numpy()
    nf = st["nf"].to_numpy()
    turn = st["turn_id"].to_numpy()
    room = st["room"].to_numpy()
    agent = st["agent"].to_numpy()
    rd = D.rd
    r_reader = rd["reader"].to_numpy()
    r_day = rd["pt_date"].to_numpy()
    r_n = rd["n"].to_numpy()
    r_nf = rd["nf"].to_numpy()
    r_turn = rd["turn_id"].to_numpy()
    r_snd = rd["sender"].to_numpy()
    r_post = rd["t_post"].dt.epoch("us").to_numpy() / 1e6
    rg = {}
    for k, key in enumerate(zip(r_reader, r_day)):
        rg.setdefault(key, []).append(k)
    order = np.argsort(t, kind="stable")
    room_t = {r: order[room[order] == r] for r in np.unique(room)}
    ag_all = np.unique(agent)
    days_here = set(st["pt_date"].unique().to_list())
    W = {k: v for k, v in W.items() if k[1] in days_here}
    aidx = {a: k for k, a in enumerate(ag_all)}
    nA = len(ag_all)
    nbins = len(DOSE_EDGES) - 1
    ys, Rs, pairs, ads, extras, bids = [], [], [], [], [], []
    tau_sum = np.zeros(nbins + 1)
    tau_cnt = np.zeros(nbins + 1)
    for row, (ag, day, idx) in enumerate(zip(g["agent"].to_list(), g["pt_date"].to_list(), g["i"].to_list())):
        hi = W.get((ag, day))
        if hi is None:
            continue
        idx = np.asarray(idx)
        js = [j for j in ag_all if j != ag and (j, day) in W]
        if not js:
            continue
        Wd = np.array([W[(j, day)] - hi for j in js])
        Wd /= np.maximum(np.linalg.norm(Wd, axis=1, keepdims=True), 1e-9)
        Y = X[idx] @ Wd.T                                   # (nB, nJ)
        jpos = {j: k for k, j in enumerate(js)}
        nJ = len(js)
        R = np.zeros((len(idx), nJ, 8 + (4 if reset_split else 0)))
        rr = np.asarray(rg.get((ag, day), []), int)
        if len(rr):
            keep = np.array([s in jpos for s in r_snd[rr]])
            if sender_filter is not None:
                keep &= sender_filter(np.full(len(rr), ag), r_snd[rr], r_post[rr])
            rr = rr[keep]
        if len(rr):
            jj = np.array([jpos[s] for s in r_snd[rr]])
            lag = nn[idx][:, None] - r_n[rr][None, :]              # (nB, nR)
            valid = lag >= 0
            b = np.searchsorted(DOSE_EDGES, lag, "right") - 1     # 0 for lag 0
            b[(lag < 0) | (lag >= DOSE_EDGES[-1])] = -1
            same_call = turn[idx][:, None] == r_turn[rr][None, :]
            d_m = np.clip(t[idx] - tc[idx], 1.0, D_MAX)
            mirror = same_call & (r_post[rr][None, :] > (tc[idx] - d_m)[:, None])
            col = np.where(b == 0, np.where(mirror, 0, 1), b + 1)   # R0m=0, R0o=1, then bins 1.. -> 2..
            col[~valid | (b < 0)] = -1
            kk, rr_i = np.nonzero(col >= 0)
            np.add.at(R, (kk, jj[rr_i], col[kk, rr_i]), 1.0)
            # mean lag per dose bin (R0o..)
            cb = col[kk, rr_i]
            lg = lag[kk, rr_i]
            for c in range(1, nbins + 1):
                m = cb == c
                tau_sum[c] += lg[m].sum()
                tau_cnt[c] += m.sum()
            if reset_split:
                crossed = nf[idx][:, None] != r_nf[rr][None, :]
                inwin = (lag >= 4) & (lag < 40)
                for c_off, (lo, hi_) in enumerate(((4, 16), (16, 40))):
                    w = (lag >= lo) & (lag < hi_) & inwin
                    k1, r1 = np.nonzero(w & ~crossed)
                    np.add.at(R, (k1, jj[r1], 8 + 2 * c_off), 1.0)
                    k2, r2 = np.nonzero(w & crossed)
                    np.add.at(R, (k2, jj[r2], 8 + 2 * c_off + 1), 1.0)
        # in flight: j's statements in B's room posted in (T_c, min(t_B, T_c + D_MAX))
        for k, B in enumerate(idx):
            rt = room_t.get(room[B])
            if rt is None:
                continue
            lo = np.searchsorted(t[rt], tc[B], "right")
            hi_ = np.searchsorted(t[rt], min(t[B], tc[B] + D_MAX), "left")
            for m in rt[lo:hi_]:
                p = jpos.get(agent[m])
                if p is not None:
                    R[k, p, 7] += 1.0
        ys.append(Y.ravel())
        Rs.append(R.reshape(-1, R.shape[2]))
        pairs.append(np.repeat(aidx[ag] * nA, len(idx) * nJ) + np.tile([aidx[j] for j in js], len(idx)))
        ads.append(np.full(len(idx) * nJ, row))
        bids.append(np.repeat(idx, nJ))
    tau = np.where(tau_cnt > 0, tau_sum / np.maximum(tau_cnt, 1), 0.0)
    tau[0] = 0.0
    unit_codes = g["unit_id"].to_numpy()
    ad = np.concatenate(ads)
    pr = np.concatenate(pairs)
    # fixed effects per (pair, agent-day of the reader): the wells are leave-day-out, so their estimation noise is a
    # day-level pair offset that correlates with the day's activity (synthetic null, A1)
    pr = pr.astype(np.int64) + np.int64(nA * nA) * ad.astype(np.int64)
    return Dose(pair=pr, ad=ad, unit=unit_codes, y=np.concatenate(ys), R=np.vstack(Rs), tau=tau,
                extra={"bid": np.concatenate(bids)})


def with_totals(Ds: Dose, cols) -> np.ndarray:
    """Design [R_j[:, cols], T[:, cols]] with T = the same counts summed over all senders for the statement (generic
    reading). The R_j coefficients are then the sender-specific excess: the kick toward the sender that was read,
    beyond the pull that any read gives (A1b)."""
    b = Ds.extra["bid"]
    ub, inv = np.unique(b, return_inverse=True)
    T = np.column_stack([np.bincount(inv, weights=Ds.R[:, c])[inv] for c in cols])
    return np.column_stack([Ds.R[:, cols], T])


def dose_fit(Ds: Dose, mask_ad: np.ndarray | None = None, Bw: np.ndarray | None = None, cols=None):
    """Pair-FE OLS of y on dose columns; agent-day bootstrap via per-agent-day cross products."""
    cols = list(range(Ds.R.shape[1])) if cols is None else cols
    keep = np.ones(len(Ds.y), bool) if mask_ad is None else mask_ad[Ds.ad]
    y, R, pr, ad = Ds.y[keep], Ds.R[keep][:, cols], Ds.pair[keep], Ds.ad[keep]
    # demean within pair
    up, inv = np.unique(pr, return_inverse=True)
    cnt = np.bincount(inv)
    ym = np.bincount(inv, weights=y) / cnt
    yd = y - ym[inv]
    Rd = R.copy()
    for c in range(R.shape[1]):
        Rd[:, c] = R[:, c] - (np.bincount(inv, weights=R[:, c]) / cnt)[inv]
    nad = Ds.unit.shape[0]
    k = Rd.shape[1]
    XtX = np.zeros((nad, k, k))
    Xty = np.zeros((nad, k))
    for c1 in range(k):
        Xty[:, c1] = np.bincount(ad, weights=Rd[:, c1] * yd, minlength=nad)
        for c2 in range(c1, k):
            v = np.bincount(ad, weights=Rd[:, c1] * Rd[:, c2], minlength=nad)
            XtX[:, c1, c2] = v
            XtX[:, c2, c1] = v
    def solve(w):
        A = (w[:, None, None] * XtX).sum(0)
        b = (w[:, None] * Xty).sum(0)
        return np.linalg.lstsq(A + 1e-9 * np.eye(k), b, rcond=None)[0]
    beta = solve(np.ones(nad))
    out = {"beta": beta, "n_rows": int(len(y))}
    if Bw is not None:
        bs = np.array([solve(w) for w in Bw])
        out["boot"] = bs
        out["se"] = bs.std(0)
    return out


def kick_rate(beta, se, tau, first: int = 1, last: int = 6):
    """gamma_kick from dose coefficients beta[first..last] (R0o..R256_1023) at mean lags tau[0..]."""
    b = np.asarray(beta[first:last + 1])
    s = np.asarray(se[first:last + 1]) if se is not None else np.ones_like(b) * 0.01
    tt = np.asarray(tau[first:last + 1])
    return expfit(tt, b, s, plateau=False)


def cross_corr(D: Data, X: np.ndarray, edges=EDGES_S) -> Acc:
    """O6: pairs of statements by different agents, same room and day; tau = |t' - t| seconds (bin edges)."""
    st = D.st.filter(pl.Series(D.ok))
    g = st.group_by("unit_id", "pt_date", "room", maintain_order=True).agg(pl.col("i")).sort("unit_id", "pt_date", "room")
    nb = len(edges) - 1
    S, S2, N, T = (np.zeros((g.height, nb)) for _ in range(4))
    t = D.st["t"].dt.epoch("us").to_numpy() / 1e6
    a = D.st["agent"].to_numpy()
    for row, idx in enumerate(g["i"].to_list()):
        idx = np.asarray(idx)
        if len(idx) < 2:
            continue
        G = X[idx] @ X[idx].T
        ii, jj = np.triu_indices(len(idx), 1)
        m = a[idx][ii] != a[idx][jj]
        ii, jj = ii[m], jj[m]
        tau = np.abs(t[idx][jj] - t[idx][ii])
        b = _bin(tau, edges)
        _acc_add(S, S2, N, T, row, b, G[ii, jj], tau)
    return Acc(list(zip(g["unit_id"], g["pt_date"], g["room"])), g["unit_id"].to_numpy(), S, S2, N, T, edges)


def autocorr_corrected(D: Data, X: np.ndarray, cx_tau: np.ndarray, cx_val: np.ndarray, clock: str = "n",
                       edges=None, split=None):
    """O1 with the common part removed: x_B . x_B' - C_x(|t_B' - t_B|), C_x interpolated (log-lag) from O6."""
    edges = (EDGES_N if clock == "n" else EDGES_S) if edges is None else edges
    good = np.isfinite(cx_val) & np.isfinite(cx_tau) & (cx_tau > 0)
    lt, cv = np.log(cx_tau[good]), cx_val[good]
    def cx(s):
        return np.interp(np.log(np.maximum(s, 1.0)), lt, cv, left=cv[0], right=cv[-1])
    g = agent_days(D)
    nb = len(edges) - 1
    shape = (g.height, nb)
    outs = [np.zeros(shape) for _ in range(4)] if split is None else [[np.zeros(shape) for _ in range(4)] for _ in range(2)]
    nn = D.st["n"].to_numpy()
    t = D.st["t"].dt.epoch("us").to_numpy() / 1e6
    tc = D.st["t_call"].dt.epoch("us").to_numpy() / 1e6
    nf = D.st["nf"].to_numpy()
    for row, idx in enumerate(g["i"].to_list()):
        idx = np.asarray(idx)
        if len(idx) < 2:
            continue
        ii, jj = np.triu_indices(len(idx), 1)
        a, b_ = idx[ii], idx[jj]
        tau = np.abs((nn[b_] - nn[a]).astype(float)) if clock == "n" else np.abs(tc[b_] - tc[a])
        keep = tau >= (1 if clock == "n" else 1e-6)
        a, b_, tau = a[keep], b_[keep], tau[keep]
        y = np.einsum("ij,ij->i", X[a], X[b_]) - cx(np.abs(t[b_] - t[a]))
        bins = _bin(tau, edges)
        if split is None:
            _acc_add(*outs, row, bins, y, tau)
        else:
            cr = nf[a] != nf[b_]
            _acc_add(*outs[0], row, np.where(~cr, bins, -1), y, tau)
            _acc_add(*outs[1], row, np.where(cr, bins, -1), y, tau)
    mk = lambda o: Acc(list(zip(g["unit_id"], g["agent"], g["pt_date"])), g["unit_id"].to_numpy(), *o, edges)  # noqa: E731
    return mk(outs) if split is None else (mk(outs[0]), mk(outs[1]))


def auto_rate(acc: Acc, w=None, plateau=True, min_n=30):
    tC, mC, sC, nC = profile(acc, w, 1)
    sC = np.where(nC >= min_n, sC, np.nan)
    return expfit(tC, mC, sC, plateau)


# ---------------------------------------------------------------------------------------------- one pipeline
def analyze(D: Data, B: int = 200, seed: int = 0, mask_ad: np.ndarray | None = None, clock: str = "n",
            do_old: bool = True, do_natives: bool = True) -> dict:
    """Every primary (A1) and registered statistic on one Data object (one unit, or several units with unit-stratified
    bootstrap). Identical for synthetic and real data."""
    X = np.where(D.ok[:, None], D.Z - np.nan_to_num(D.H), 0.0)
    g = agent_days(D)
    unit = g["unit_id"].to_numpy()
    mask = np.ones(g.height, bool) if mask_ad is None else mask_ad
    Bw = boot_weights(unit, B, seed) if B else None
    out = {"n_ad": int(mask.sum()), "n_statements": int(sum(len(x) for x, m in zip(g["i"].to_list(), mask) if m))}
    # O6 cross-agent covariance (seconds), used to correct O1
    cx = cross_corr(D, X)
    cxt, cxm, cxs, cxn = profile(cx)
    out["Cx_tau"], out["Cx"], out["Cx_se"] = cxt.tolist(), cxm.tolist(), cxs.tolist()
    fx = expfit(cxt, cxm, np.where(cxn >= 30, cxs, np.nan), True)
    out["g_cross_s"] = fx["g"]
    # O1 corrected (A1 primary) and raw
    accA = autocorr_corrected(D, X, cxt, cxm, clock)
    accR = autocorr(D, X, clock)
    fa = auto_rate(accA, mask.astype(float))
    fr = auto_rate(accR, mask.astype(float))
    out["g_auto"], out["g_auto_raw"] = fa["g"], fr["g"]
    out["C_prof"] = profile(accA, mask.astype(float), 0)[1].tolist()
    out["C_raw_prof"] = profile(accR, mask.astype(float), 0)[1].tolist()
    out["C_tau"] = profile(accA, mask.astype(float), 0)[0].tolist()
    # seconds-clock own autocorrelation (for gamma_x comparison)
    accAs = autocorr_corrected(D, X, cxt, cxm, "s")
    out["g_auto_s"] = auto_rate(accAs, mask.astype(float))["g"]
    out["g_auto_raw_s"] = auto_rate(autocorr(D, X, "s"), mask.astype(float))["g"]
    # dose regression (A1 primary for gamma_kick; secondary J)
    Ds = dose_design(D, X, reset_split=do_natives)
    main_cols = list(range(8))
    Dm = Dose(pair=Ds.pair, ad=Ds.ad, unit=Ds.unit, y=Ds.y, R=with_totals(Ds, main_cols), tau=Ds.tau, extra=Ds.extra)
    df = dose_fit(Dm, mask, Bw)
    out["beta_total"] = df["beta"][8:].tolist()
    df["beta"] = df["beta"][:8]
    if "boot" in df:
        df["boot"] = df["boot"][:, :8]
        df["se"] = df["se"][:8]
    beta, se = df["beta"], df.get("se", np.full(8, np.nan))
    out["beta"], out["beta_se"], out["dose_tau"] = beta.tolist(), se.tolist(), Ds.tau.tolist()
    fk = kick_rate(beta, se if Bw is not None else None, Ds.tau)
    out["g_kick"] = fk["g"]
    out["A_kick"] = fk["A"]
    out["J_pair"] = float(beta[0] - beta[7])
    out["rho"] = fk["g"] / fa["g"] if fk["ok"] and fa["ok"] else np.nan
    if Bw is not None:
        ga, gk, jp = [], [], []
        for b, w in enumerate(Bw):
            ww = w * mask
            ga.append(auto_rate(accA, ww)["g"])
            gk.append(kick_rate(df["boot"][b], se, Ds.tau)["g"])
            jp.append(df["boot"][b][0] - df["boot"][b][7])
        ga, gk, jp = np.array(ga), np.array(gk), np.array(jp)
        rr = gk / ga
        out["ci_auto"] = np.nanpercentile(ga, [2.5, 97.5]).tolist()
        out["ci_kick"] = np.nanpercentile(gk, [2.5, 97.5]).tolist()
        out["ci_rho95"] = np.nanpercentile(rr, [2.5, 97.5]).tolist()
        out["ci_rho90"] = np.nanpercentile(rr, [5, 95]).tolist()
        out["se_lnrho"] = float(np.nanstd(np.log(rr[np.isfinite(rr) & (rr > 0)]))) if np.any(np.isfinite(rr) & (rr > 0)) else np.nan
        out["se_lng_auto"] = float(np.nanstd(np.log(ga[np.isfinite(ga) & (ga > 0)]))) if np.any(ga > 0) else np.nan
        out["frac_fit"] = float(np.mean(np.isfinite(rr)))
        out["ci_J_pair"] = np.percentile(jp, [2.5, 97.5]).tolist()
        out["se_J_pair"] = float(jp.std())
    # registered J (message direction, symmetric consensus window), primary for kill K2
    C = Consensus(D.st, D.Z, "sym")
    J = jump_stats(read_jump(D, C, X), mask, Bw)
    out.update({"J": J["J"], "K_read": J["K_read"], "K_if": J["K_if"], "n_read": J["n_read"], "n_if": J["n_if"]})
    if Bw is not None:
        out["ci_J"], out["se_J"] = J["ci"], J["se"]
    if do_old:
        # registered message-direction profile (superseded by A1; reported)
        Cp = Consensus(D.st, D.Z, "sym")
        U, Uok = read_dirs(D, Cp)
        accK = kick_profile(D, X, U, Uok, clock)
        fko = expfit(*profile(accK, mask.astype(float), 0)[:2], np.where(profile(accK, mask.astype(float), 0)[3] >= 30,
                     profile(accK, mask.astype(float), 0)[2], np.nan), True)
        out["g_kick_msgdir"] = fko["g"]
        out["K_prof"] = profile(accK, mask.astype(float), 0)[1].tolist()
    if do_natives:
        # N2: erasure split, autocorrelation (corrected) and dose
        e = np.array([4, 16, 40])
        cw, cxr = autocorr_corrected(D, X, cxt, cxm, "n", edges=e, split="reset")
        def ratio_acc(a, b, w):
            _, ma, sa, na = profile(a, w, 0)
            _, mb, sb, nb = profile(b, w, 0)
            ww = np.minimum(na, nb)
            return float(np.nansum(mb * ww) / np.nansum(ma * ww)) if np.nansum(ma * ww) else np.nan
        out["R_C"] = ratio_acc(cw, cxr, mask.astype(float))
        R = Ds.R
        r40 = R[:, 4] - R[:, 10] - R[:, 11]
        R2 = np.column_stack([R[:, 0], R[:, 1], R[:, 2], R[:, 8], R[:, 9], R[:, 10], R[:, 11], r40, R[:, 5], R[:, 6], R[:, 7]])
        b_ = Ds.extra["bid"]
        _, inv_ = np.unique(b_, return_inverse=True)
        T2 = np.column_stack([np.bincount(inv_, weights=R2[:, c])[inv_] for c in range(R2.shape[1])])
        D2 = Dose(pair=Ds.pair, ad=Ds.ad, unit=Ds.unit, y=Ds.y, R=np.column_stack([R2, T2]), tau=Ds.tau, extra={})
        f2 = dose_fit(D2, mask, Bw)
        b2 = f2["beta"]
        out["N2_beta"] = b2.tolist()
        out["R_K"] = float((b2[4] + b2[6]) / (b2[3] + b2[5])) if (b2[3] + b2[5]) != 0 else np.nan
        if Bw is not None:
            rk = (f2["boot"][:, 4] + f2["boot"][:, 6]) / (f2["boot"][:, 3] + f2["boot"][:, 5])
            out["ci_R_K"] = np.nanpercentile(rk, [2.5, 97.5]).tolist()
            rc = []
            for w in Bw:
                rc.append(ratio_acc(cw, cxr, w * mask))
            out["ci_R_C"] = np.nanpercentile(np.array(rc), [2.5, 97.5]).tolist()
    return out
