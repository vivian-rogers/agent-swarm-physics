"""H91 library: eigenvector rotation between consecutive days, the pooled-split (finite-T Dyson) null, the trailing
alarm and event-study helpers. Functions only; matrices and synthetic days come from scheme/daymat.py."""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scheme"))
import daymat as DM  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = DM.ROOT
OUT = ROOT / "data/processed/H91-eigenvector-rotation-signal"
KS = (1, 2, 3)
K_PRIMARY = 2
R_NULL = 199
BASE_DAYS, MIN_BASE = 10, 5
TRIM_C = {5: 0.5206, 6: 0.5788, 7: 0.6212, 8: 0.6542, 9: 0.6798, 10: 0.7007}  # H36 h36lib (consistency factor)
THRESH = 2.0
BLOCK_W = 2           # moving-block length (30-min windows) for the content bootstrap null
SEED = 20261004


# ============================================================================================ rotation
def _dists(Ma, Mb, ks):
    w_a, V_a = np.linalg.eigh(Ma); w_b, V_b = np.linalg.eigh(Mb)
    V_a, V_b = V_a[:, ::-1], V_b[:, ::-1]
    return [DM.subspace_dist(V_a[:, :k], V_b[:, :k]) for k in ks], w_a[::-1], w_b[::-1]


def recenter(Z: np.ndarray) -> np.ndarray:
    """Re-center each agent on its present (non-zero) windows of this (pseudo-)day, as the real day construction."""
    pres = np.abs(Z).sum(2) > 0
    n = np.maximum(pres.sum(1), 1)
    mu = Z.sum(1) / n[:, None]
    return (Z - mu[:, None, :]) * pres[:, :, None]


def _mbb_idx(W: int, rng, b: int) -> np.ndarray:
    """Moving-block bootstrap indices (block length b, circular) of length W."""
    nb = int(np.ceil(W / b))
    st = rng.integers(0, W, nb)
    return ((st[:, None] + np.arange(b)[None, :]) % W).ravel()[:W]


def rot_content(Za: np.ndarray, Zb: np.ndarray, rng, R: int = R_NULL, ks=KS, block: int = BLOCK_W) -> dict:
    """Za, Zb: N x W x d day arrays of the SAME agents (rows aligned), each centered on its own day.
    Two finite-T (Dyson) nulls for "same population matrix on both days":
      split: windows of both days pooled and split at random into pseudo-days of the real sizes (re-centered);
      boot : distance between two independent moving-block bootstrap resamples (block = 2 windows) of the SAME day,
             drawn for day a and for day b (R/2 each); it does not mix the two days' structures."""
    Wa, Wb = Za.shape[1], Zb.shape[1]
    obs, la, lb = _dists(DM.overlap(Za), DM.overlap(Zb), ks)
    P = np.concatenate([Za, Zb], axis=1)
    n = P.shape[1]
    split = np.empty((R, len(ks)))
    for r in range(R):
        p = rng.permutation(n)
        split[r] = _dists(DM.overlap(recenter(P[:, p[:Wa]])), DM.overlap(recenter(P[:, p[Wa:]])), ks)[0]
    boot = np.empty((R, len(ks)))
    for r in range(R):
        Z, W = (Za, Wa) if r % 2 == 0 else (Zb, Wb)
        A = recenter(Z[:, _mbb_idx(W, rng, block)]); B = recenter(Z[:, _mbb_idx(W, rng, block)])
        boot[r] = _dists(DM.overlap(A), DM.overlap(B), ks)[0]
    return _summ(obs, {"split": split, "boot": boot}, ks, la, lb)


def rot_spins(Sa: np.ndarray, ma: np.ndarray, Sb: np.ndarray, mb: np.ndarray, rng, R: int = R_NULL, ks=KS,
              block: int = 30) -> dict:
    """Sa, Sb: N x L spins of the same agents (kept minutes ma, mb), standardized per agent and day.
    split: whole 30-min blocks of both days pooled and split (each day's block count kept);
    boot : two independent bootstrap resamples of the 30-min blocks of the SAME day (a or b)."""
    Xa, Xb = DM.standardize(Sa), DM.standardize(Sb)
    obs, la, lb = _dists(DM.corr(Xa), DM.corr(Xb), ks)
    ba = [Xa[:, np.asarray(ma) // block == b] for b in np.unique(np.asarray(ma) // block)]
    bb = [Xb[:, np.asarray(mb) // block == b] for b in np.unique(np.asarray(mb) // block)]
    blocks, na = ba + bb, len(ba)
    split = np.empty((R, len(ks)))
    for r in range(R):
        p = rng.permutation(len(blocks))
        A = np.concatenate([blocks[i] for i in p[:na]], axis=1)
        B = np.concatenate([blocks[i] for i in p[na:]], axis=1)
        split[r] = _dists(DM.corr(A), DM.corr(B), ks)[0]
    boot = np.empty((R, len(ks)))
    for r in range(R):
        bl = ba if r % 2 == 0 else bb
        A = np.concatenate([bl[i] for i in rng.integers(0, len(bl), len(bl))], axis=1)
        B = np.concatenate([bl[i] for i in rng.integers(0, len(bl), len(bl))], axis=1)
        boot[r] = _dists(DM.corr(A), DM.corr(B), ks)[0]
    return _summ(obs, {"split": split, "boot": boot}, ks, la, lb)


def _summ(obs, nulls: dict, ks, la, lb) -> dict:
    out = {"N": int(len(la)), "l1_a": float(la[0]), "l1_b": float(lb[0]),
           "l2_a": float(la[1]) if len(la) > 1 else np.nan, "l2_b": float(lb[1]) if len(lb) > 1 else np.nan}
    for j, k in enumerate(ks):
        out[f"d{k}"] = float(obs[j])
        for nm, null in nulls.items():
            m, s = float(null[:, j].mean()), float(null[:, j].std(ddof=1))
            out[f"d{k}_{nm}"] = m; out[f"d{k}_{nm}_sd"] = s
            out[f"z{k}_{nm}"] = (obs[j] - m) / s if s > 0 else np.nan
            out[f"p{k}_{nm}"] = float((1 + (null[:, j] >= obs[j]).sum()) / (len(null) + 1))
    return out


# ============================================================================================ alarm
def trailing_z(x: np.ndarray, base: int = BASE_DAYS, min_base: int = MIN_BASE) -> np.ndarray:
    """H36's trailing robust z (h36lib.trailing_z, re-implemented): (x - median of the previous `base` finite values)
    / (SD after dropping max and min / consistency factor). NaN with fewer than min_base baseline values."""
    z = np.full(x.size, np.nan)
    hist: list = []
    for d in range(x.size):
        if np.isfinite(x[d]) and len(hist) >= min_base:
            h = np.array(hist[-base:])
            hs = np.sort(h)[1:-1] if h.size >= 4 else h
            sd = hs.std(ddof=1) / TRIM_C[h.size] if hs.size >= 2 else np.nan
            if sd and np.isfinite(sd) and sd > 0:
                z[d] = (x[d] - np.median(h)) / sd
        if np.isfinite(x[d]):
            hist.append(float(x[d]))
    return z


# ============================================================================================ evaluation
def auc(pos: np.ndarray, neg: np.ndarray) -> float:
    pos, neg = pos[np.isfinite(pos)], neg[np.isfinite(neg)]
    if not len(pos) or not len(neg):
        return np.nan
    r = (pos[:, None] > neg[None, :]).mean() + 0.5 * (pos[:, None] == neg[None, :]).mean()
    return float(r)


def auc_ci(pos, neg, rng, B: int = 2000):
    pos, neg = pos[np.isfinite(pos)], neg[np.isfinite(neg)]
    a = auc(pos, neg)
    bs = [auc(rng.choice(pos, len(pos)), rng.choice(neg, len(neg))) for _ in range(B)]
    return a, float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))


def paired_dauc(pa, pb, na, nb, rng, B: int = 2000):
    """ΔAUC(a − b) on the same event and placebo days (rows aligned; rows with any NaN dropped)."""
    okp = np.isfinite(pa) & np.isfinite(pb); okn = np.isfinite(na) & np.isfinite(nb)
    pa, pb, na, nb = pa[okp], pb[okp], na[okn], nb[okn]
    d = auc(pa, na) - auc(pb, nb)
    bs = []
    for _ in range(B):
        i = rng.integers(0, len(pa), len(pa)); j = rng.integers(0, len(na), len(na))
        bs.append(auc(pa[i], na[j]) - auc(pb[i], nb[j]))
    return float(d), float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975)), int(len(pa)), int(len(na))


def wilson(k: int, n: int, z: float = 1.96):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n; den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (float(max(0.0, c - h)), float(min(1.0, c + h)))


def spearman(a, b) -> float:
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 4:
        return np.nan
    ra = pl.Series(a[ok]).rank().to_numpy(); rb = pl.Series(b[ok]).rank().to_numpy()
    return float(np.corrcoef(ra, rb)[0, 1])


def mannwhitney_p(x, y, rng, B: int = 5000) -> float:
    """One-sided permutation p for mean(x) > mean(y)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    x, y = x[np.isfinite(x)], y[np.isfinite(y)]
    if len(x) == 0 or len(y) == 0:
        return np.nan
    obs = x.mean() - y.mean()
    allv = np.concatenate([x, y]); n = len(x)
    cnt = 0
    for _ in range(B):
        p = rng.permutation(allv)
        cnt += (p[:n].mean() - p[n:].mean()) >= obs
    return float((cnt + 1) / (B + 1))
