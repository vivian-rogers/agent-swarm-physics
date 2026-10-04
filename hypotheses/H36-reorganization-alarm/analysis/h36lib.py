"""H36 core library: day-level fluctuation statistics (multi-information, susceptibility, heat capacity) for activity
spins, 4-state behavior and content vector spins; surrogate excesses; trailing-baseline z-scores; the alarm rule;
and the evaluation helpers (hit rate, false-alarm rate, AUC, timing, random-date null).

Used by scheme/build.py, analysis/synthetic.py, analysis/evaluate.py and analysis/confirm.py.
Threads are pinned to 1 per process (callers use at most 2 processes).
"""
from __future__ import annotations

import os
import warnings

warnings.filterwarnings("ignore", message="Mean of empty slice")
warnings.filterwarnings("ignore", message="All-NaN slice encountered")
for _v in ("OMP_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("POLARS_MAX_THREADS", "2")

import datetime as dt  # noqa: E402
import json  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
HYP = ROOT / "hypotheses/H36-reorganization-alarm"
OUT = ROOT / "data/processed/H36-reorganization-alarm"
SH = ROOT / "data/processed/shared"
FIG = HYP / "figures"
SEED = 20261004
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, holdout_mask, load_holdout, load_whitener  # noqa: E402,F401

# ---------------------------------------------------------------------------------------------- frozen rule
N_SURR = 30            # surrogates per day and statistic
BASE_DAYS = 10         # trailing baseline length (non-holdout active days with the statistic)
MIN_BASE = 5           # minimum baseline days for a z-score
THRESH = 2.0           # primary alarm: Z_phys >= THRESH
OR_THRESH = 3.0        # secondary OR rule: any family Z >= OR_THRESH
MIN_ACTIVE_MIN = 10    # day-present: >= 10 active minutes
MIN_PRESENT = 3        # days with fewer present agents are skipped
OFF_RUN = 10           # village-off gap: K = 0 for >= 10 consecutive minutes
HIT_WINDOW = (-1, 0, 1)
PLACEBO_DIST = 3       # placebo days are >= 3 active days from every catalogued event

ACT_STATS = ["I_act", "I_beh", "chi_act", "C_act"]
CONT_STATS = ["I_cont", "chi_cont", "C_cont"]
FAMILIES = {"Z_I": ["I_act", "I_beh", "I_cont"], "Z_chi": ["chi_act", "chi_cont"], "Z_C": ["C_act", "C_cont"]}
RIVALS = {"R1_shift": "one", "R2_level": "two", "R3_polar": "two"}


def git_commit() -> str:
    r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "--", str(HYP)],
                           capture_output=True, text=True).stdout
    return (r.stdout.strip() or "none") + ("+uncommitted" if dirty.strip() else "")


def write_provenance(built_by: str, tables: list[str], params: dict, path: Path | None = None):
    path = path or (OUT / "_provenance.json")
    prov = json.loads(path.read_text()) if path.exists() else {}
    prov[built_by] = {"built_by": built_by, "git_commit": git_commit(),
                      "inputs": [{"source": "ai-village", "revision": REVISION, "tables": tables}],
                      "params": params, "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(prov, indent=1))


# ---------------------------------------------------------------------------------------------- outage masks
def off_runs(K: np.ndarray, min_len: int = OFF_RUN) -> np.ndarray:
    """Boolean mask of minutes inside runs of K == 0 lasting >= min_len minutes (village-off gaps)."""
    z = np.r_[False, K == 0, False]
    d = np.diff(z.astype(np.int8))
    starts, ends = np.flatnonzero(d == 1), np.flatnonzero(d == -1)
    m = np.zeros(K.size, bool)
    for s, e in zip(starts, ends):
        if e - s >= min_len:
            m[s:e] = True
    return m


# ---------------------------------------------------------------------------------------------- activity statistics
def _ridge_logdet(R: np.ndarray, r: float = 1e-3) -> float:
    n = R.shape[0]
    s, ld = np.linalg.slogdet((R + r * np.eye(n)) / (1 + r))
    return float(ld)


def _act_one(S: np.ndarray, Bh: np.ndarray) -> np.ndarray:
    """S: n x T (+-1 floats); Bh: n x T int states 0..3. Returns [I_act, I_beh, chi_act, C_act]."""
    n, T = S.shape
    npairs = n * (n - 1) / 2
    R = np.corrcoef(S)
    i_act = -0.5 * _ridge_logdet(R) / npairs
    i_beh = pair_mi_mm(Bh) / npairs
    M = S.sum(0)
    vr = M.var() / S.var(1).sum()
    E = -(M ** 2 - n) / (2 * n)
    c = E.var() / n
    return np.array([i_act, i_beh, vr, c])


def pair_mi_mm(Bh: np.ndarray, q: int = 4) -> float:
    """Sum over pairs of the plug-in mutual information (nats) between categorical series, Miller-Madow corrected."""
    n, T = Bh.shape
    O = np.zeros((n * q, T), np.float64)
    O[(np.arange(n)[:, None] * q + Bh), np.arange(T)[None, :]] = 1.0
    Cn = (O @ O.T).reshape(n, q, n, q).transpose(0, 2, 1, 3)  # n, n, q, q
    P = Cn / T
    px = P.sum(3)
    py = P.sum(2)
    den = px[..., :, None] * py[..., None, :]
    with np.errstate(divide="ignore", invalid="ignore"):
        term = np.where(P > 0, P * np.log(P / den), 0.0)
    mi = term.sum((2, 3))
    kxy = (Cn > 0).sum((2, 3)); kx = (px > 0).sum(2); ky = (py > 0).sum(2)
    mi = mi - (kxy - kx - ky + 1) / (2 * T)
    iu = np.triu_indices(n, 1)
    return float(mi[iu].sum())


def activity_stats(S: np.ndarray, Bh: np.ndarray, rng: np.random.Generator, n_surr: int = N_SURR) -> dict:
    """Observed statistics and surrogate mean/sd (independent circular shifts per agent).
    S: n x T +-1 spins (masked minutes already removed); Bh: n x T 4-state codes 0..3.
    Agents with zero spin variance are dropped. Returns {} if fewer than MIN_PRESENT agents or T < 30."""
    keep = S.std(1) > 0
    S, Bh = S[keep].astype(np.float64), Bh[keep]
    n, T = S.shape
    if n < MIN_PRESENT or T < 30:
        return {}
    obs = _act_one(S, Bh)
    sur = np.empty((n_surr, 4))
    idx0 = np.arange(T)
    for k in range(n_surr):
        lag = rng.integers(0, T, size=n)
        idx = (idx0[None, :] + lag[:, None]) % T
        sur[k] = _act_one(S[np.arange(n)[:, None], idx], Bh[np.arange(n)[:, None], idx])
    out = {"n_act": n, "T_act": T}
    for j, name in enumerate(ACT_STATS):
        out[name + "_obs"] = obs[j]
        out[name + "_sm"] = sur[:, j].mean()
        out[name + "_ss"] = sur[:, j].std()
        out[name] = obs[j] - sur[:, j].mean()
    return out


# ---------------------------------------------------------------------------------------------- content statistics
def _cont_one(V: np.ndarray, Z: np.ndarray, M: np.ndarray) -> np.ndarray:
    """V: n x W x d unit vectors (0 where missing); Z: agent-centered (0 where missing); M: n x W bool.
    Returns [I_cont, chi_cont, C_cont]."""
    n = V.shape[0]
    npairs = n * (n - 1) / 2
    Q = np.einsum("iwd,jwd->ij", Z, Z)
    dg = np.sqrt(np.clip(np.diag(Q), 1e-12, None))
    Qn = Q / np.outer(dg, dg)
    i_c = -0.5 * _ridge_logdet(Qn, 1e-2) / npairs
    chi = Qn.sum() / n
    G = np.einsum("iwd,jwd->wij", V, V)
    c = M.sum(0).astype(float)
    S_w = (G.sum((1, 2)) - c) / 2.0
    npw = c * (c - 1) / 2
    ok = npw > 0
    if ok.sum() >= 3:
        e = -S_w[ok] / npw[ok]
        cc = e.var() * npw[ok].mean()
    else:
        cc = np.nan
    return np.array([i_c, chi, cc])


def content_stats(V: np.ndarray, M: np.ndarray, rng: np.random.Generator, n_surr: int = N_SURR,
                  min_windows: int = 3) -> dict:
    """Content vector-spin statistics for one day. V: n x W x d unit vectors (any values where ~M); M: n x W bool.
    Agents with < min_windows windows are dropped; needs >= MIN_PRESENT agents and >= 3 windows.
    Surrogate: each agent's vectors permuted among its own present windows."""
    keep = M.sum(1) >= min_windows
    V, M = V[keep].astype(np.float64), M[keep]
    n, W = M.shape
    if n < MIN_PRESENT or W < 3:
        return {}
    V = np.where(M[..., None], V, 0.0)
    mu = V.sum(1, keepdims=True) / M.sum(1)[:, None, None]
    Z = np.where(M[..., None], V - mu, 0.0)
    obs = _cont_one(V, Z, M)
    sur = np.empty((n_surr, 3))
    pres = [np.flatnonzero(M[i]) for i in range(n)]
    for k in range(n_surr):
        Vs = np.zeros_like(V); Zs = np.zeros_like(Z)
        for i in range(n):
            p = pres[i]; q = rng.permutation(p)
            Vs[i, p] = V[i, q]; Zs[i, p] = Z[i, q]
        sur[k] = _cont_one(Vs, Zs, M)
    out = {"n_cont": n, "W_cont": W}
    for j, name in enumerate(CONT_STATS):
        out[name + "_obs"] = obs[j]
        out[name + "_sm"] = np.nanmean(sur[:, j]) if np.isfinite(sur[:, j]).any() else np.nan
        out[name + "_ss"] = np.nanstd(sur[:, j]) if np.isfinite(sur[:, j]).any() else np.nan
        out[name] = obs[j] - out[name + "_sm"]
    return out


# ---------------------------------------------------------------------------------------------- z-scores and alarm
# Amendment 1 (2026-10-04, after the synthetic run, before real data): E[SD of the middle k-2 of k Gaussian draws]/sigma,
# so the trailing scale is unbiased for Gaussian day-to-day noise (the uncorrected scale inflated z by ~1.4).
TRIM_C = {5: 0.5206, 6: 0.5788, 7: 0.6212, 8: 0.6542, 9: 0.6798, 10: 0.7007}


def trailing_z(x: np.ndarray, base: int = BASE_DAYS, min_base: int = MIN_BASE, two_sided: bool = False) -> np.ndarray:
    """x: statistic per day in time order (non-holdout days only; NaN = unavailable). z(d) against the previous `base`
    finite values: (x - median) / (SD after dropping the max and min, divided by the Gaussian consistency factor
    TRIM_C[k]). NaN if fewer than min_base finite values."""
    z = np.full(x.size, np.nan)
    hist: list[float] = []
    for d in range(x.size):
        if np.isfinite(x[d]) and len(hist) >= min_base:
            h = np.array(hist[-base:])
            hs = np.sort(h)[1:-1] if h.size >= 4 else h
            sd = hs.std(ddof=1) / TRIM_C[h.size] if hs.size >= 2 else np.nan
            if sd and np.isfinite(sd) and sd > 0:
                z[d] = (x[d] - np.median(h)) / sd
        if np.isfinite(x[d]):
            hist.append(float(x[d]))
    return np.abs(z) if two_sided else z


def alarm_scores(Zs: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    """Zs: per-statistic z arrays. Family z = nanmean of available members; Z_phys = nanmean of the families."""
    out = {}
    for fam, mem in FAMILIES.items():
        A = np.vstack([Zs[m] for m in mem if m in Zs])
        with np.errstate(all="ignore"):
            out[fam] = np.where(np.isfinite(A).any(0), np.nanmean(np.where(np.isfinite(A), A, np.nan), 0), np.nan)
    F = np.vstack([out[f] for f in FAMILIES])
    with np.errstate(all="ignore"):
        out["Z_phys"] = np.where(np.isfinite(F).any(0), np.nanmean(F, 0), np.nan)
        out["Z_act"] = np.nanmean(np.vstack([Zs[m] for m in ACT_STATS if m in Zs]), 0)
        cm = [Zs[m] for m in CONT_STATS if m in Zs]
        out["Z_cont"] = np.nanmean(np.vstack(cm), 0) if cm else np.full(F.shape[1], np.nan)
        out["Z_or"] = np.nanmax(F, 0)                                   # secondary OR rule (>= OR_THRESH)
        out["Z_chan"] = np.nanmax(np.vstack([out["Z_act"], out["Z_cont"]]), 0)  # Amendment 1 secondary: channel max
    return out


# ---------------------------------------------------------------------------------------------- evaluation
def auc(pos: np.ndarray, neg: np.ndarray) -> float:
    pos = pos[np.isfinite(pos)]; neg = neg[np.isfinite(neg)]
    if pos.size == 0 or neg.size == 0:
        return np.nan
    gt = (pos[:, None] > neg[None, :]).sum() + 0.5 * (pos[:, None] == neg[None, :]).sum()
    return float(gt / (pos.size * neg.size))


def auc_ci(pos, neg, rng, n_boot=2000):
    pos = pos[np.isfinite(pos)]; neg = neg[np.isfinite(neg)]
    if pos.size < 2 or neg.size < 2:
        return (np.nan, np.nan)
    b = [auc(rng.choice(pos, pos.size), rng.choice(neg, neg.size)) for _ in range(n_boot)]
    return (float(np.nanpercentile(b, 2.5)), float(np.nanpercentile(b, 97.5)))


def window_alarm(alarm_by_idx: dict[int, bool], center: int, offsets=HIT_WINDOW):
    """alarm_by_idx: active-day index -> alarm bool (only days with a score). Returns (any alarm, first offset or None,
    number of scored days in the window)."""
    hit, first, ns = False, None, 0
    for o in offsets:
        a = alarm_by_idx.get(center + o)
        if a is None:
            continue
        ns += 1
        if a and not hit:
            hit, first = True, o
    return hit, first, ns
