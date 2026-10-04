"""Shared copy / transformation information decomposition for paired categorical samples. Functions only (no table).
Moved here unchanged from H07 (hypotheses/H07-rpg-forks/analysis/h07lib.py: mi_parts, decompose, vertical,
horizontal, set_stats, transform_test), which H23 imports. Test: infra/shared/tests/test_copy_info.py.

Copy information (H07's reading of Kolchinsky & Corominas-Murtra 2020; NOT verified against the paper, a documented
proxy):
    I_copy      = sum_x p(x) * d( p(Y=x | X=x) || p_Y(x) ) * 1[ p(Y=x | X=x) > p_Y(x) ],   d = binary KL (bits)
    I_transform = I(X;Y) - I_copy   (>= 0 by data processing on the coarse-graining y -> [y == x])
Plug-in estimates (bits).
  mi_parts(x, y)           (c = P(X == Y), Cohen's kappa, I, I_copy) for integer-coded pairs on a shared alphabet
  decompose(xv, yv, n_null, seed)
                           the decomposition for any hashable values; with n_null > 0 also the shuffle null (Y permuted
                           across keys: keeps both marginals, removes all key-level dependence) and excess values *_ex
  transform_test(KA, KY, n_null, seed)
                           systematic-transformation test on keys present in both maps (deletions excluded). Conditional
                           null: copied pairs fixed, outputs permuted among changed keys; I_transform_cx = observed minus
                           conditional-null mean, z = excess / null sd; also the share of changed pairs whose exact
                           (x, y) mapping repeats ("repeated mappings")
  vertical(KA, KY), horizontal(KX, KY)
                           ancestor -> descendant over ancestor keys (deleted keys -> ABSENT); fork vs fork over the union
  set_stats(SA, SY)        survival, innovations, losses, Jaccard of two sets
"""
from __future__ import annotations

from collections import Counter

import numpy as np

ABSENT = "\x00ABSENT"


def _xlogy(a, b):
    with np.errstate(divide="ignore", invalid="ignore"):
        r = a * np.log2(a / b)
    return np.where(a > 0, r, 0.0)


def _p(x):
    c = np.bincount(x)
    c = c[c > 0]
    return c / c.sum()


def mi_parts(x: np.ndarray, y: np.ndarray):
    """(c, kappa, I, I_copy) for integer-coded paired samples on a shared alphabet."""
    n = len(x)
    if n == 0:
        return (np.nan,) * 4
    m = max(x.max(), y.max()) + 1
    px = np.bincount(x, minlength=m) / n
    py = np.bincount(y, minlength=m) / n
    pair = x.astype(np.int64) * m + y
    u, cnt = np.unique(pair, return_counts=True)
    pxy = cnt / n
    xi, yi = u // m, u % m
    I = float(np.sum(pxy * np.log2(pxy / (px[xi] * py[yi]))))
    same = x == y
    c = float(same.mean())
    pe = float(np.sum(px * py))
    kappa = (c - pe) / (1 - pe) if pe < 1 else np.nan
    # copy information
    nx = np.bincount(x, minlength=m)
    ncopy = np.bincount(x[same], minlength=m)
    vals = np.nonzero(nx)[0]
    a = ncopy[vals] / nx[vals]
    b = py[vals]
    mask = a > b
    a, b, w = a[mask], b[mask], px[vals][mask]
    d = _xlogy(a, b) + _xlogy(1 - a, 1 - b)
    Icopy = float(np.sum(w * d))
    return c, kappa, I, Icopy


def encode(xv: list, yv: list):
    """Integer codes on a shared alphabet for two lists of hashables (order of first appearance)."""
    codes: dict = {}
    x = np.fromiter((codes.setdefault(v, len(codes)) for v in xv), dtype=np.int64, count=len(xv))
    y = np.fromiter((codes.setdefault(v, len(codes)) for v in yv), dtype=np.int64, count=len(yv))
    return x, y, codes


def decompose(xv: list, yv: list, n_null: int = 0, seed: int = 0) -> dict:
    """Copy/transform decomposition for paired values (any hashables); shuffle null if n_null > 0."""
    x, y, _ = encode(xv, yv)
    c, kappa, I, Ic = mi_parts(x, y)
    out = {"n": len(x), "c": c, "kappa": kappa, "I": I, "I_copy": Ic, "I_transform": I - Ic if len(x) else np.nan,
           "H_x": float(-np.sum(_p(x) * np.log2(_p(x)))) if len(x) else np.nan}
    if n_null and len(x):
        rng = np.random.default_rng(seed)
        nul = np.array([mi_parts(x, rng.permutation(y))[2:] for _ in range(n_null)])
        out.update({"I_null": float(nul[:, 0].mean()), "I_copy_null": float(nul[:, 1].mean()),
                    "I_transform_null": float((nul[:, 0] - nul[:, 1]).mean()),
                    "I_transform_null_sd": float((nul[:, 0] - nul[:, 1]).std())})
        out["I_ex"] = out["I"] - out["I_null"]
        out["I_copy_ex"] = out["I_copy"] - out["I_copy_null"]
        out["I_transform_ex"] = out["I_transform"] - out["I_transform_null"]
    return out


def vertical(KA: dict, KY: dict, n_null=0) -> dict:
    """Ancestor -> descendant, over ancestor keys (deleted keys -> ABSENT)."""
    keys = list(KA)
    return decompose([KA[k] for k in keys], [KY.get(k, ABSENT) for k in keys], n_null)


def horizontal(KX: dict, KY: dict, n_null=0) -> dict:
    """Fork X vs fork Y over the union of their keys."""
    keys = list(set(KX) | set(KY))
    return decompose([KX.get(k, ABSENT) for k in keys], [KY.get(k, ABSENT) for k in keys], n_null)


def set_stats(SA: set, SY: set) -> dict:
    return {"survival": len(SA & SY) / len(SA) if SA else np.nan, "n_ancestor": len(SA), "n_now": len(SY),
            "innovations": len(SY - SA), "lost": len(SA - SY),
            "jaccard": len(SA & SY) / len(SA | SY) if SA | SY else np.nan}


def transform_test(KA: dict, KY: dict, n_null: int = 200, seed: int = 1) -> dict:
    """Systematic-transformation test on keys present in both (deletions excluded).

    Conditional null: keep copied pairs fixed, permute the outputs among changed keys. This removes any systematic
    x -> y mapping among changed keys but keeps the copy part and both marginals. I_transform_cx = observed minus
    the conditional-null mean (bits); z = excess / null sd. Also counts changed pairs whose exact (x, y) mapping is
    shared with another key ('repeated mappings', e.g. mpCost 6 -> 4 in six abilities).
    """
    keys = [k for k in KA if k in KY]
    x, y, codes = encode([KA[k] for k in keys], [KY[k] for k in keys])
    if len(x) == 0:
        return {}
    c, kappa, I, Ic = mi_parts(x, y)
    changed = np.nonzero(x != y)[0]
    out = {"n_surv": len(x), "n_changed": len(changed), "I": I, "I_copy": Ic, "I_transform": I - Ic}
    if len(changed) >= 2:
        rng = np.random.default_rng(seed)
        nul = []
        for _ in range(n_null):
            yy = y.copy()
            yy[changed] = rng.permutation(y[changed])
            _, _, In, Icn = mi_parts(x, yy)
            nul.append(In - Icn)
        nul = np.array(nul)
        out["I_transform_cnull"] = float(nul.mean())
        out["I_transform_cx"] = out["I_transform"] - float(nul.mean())
        out["z"] = float(out["I_transform_cx"] / nul.std()) if nul.std() > 0 else np.nan
        pairs = list(zip(x[changed].tolist(), y[changed].tolist()))
        cnt = Counter(pairs)
        out["repeated_mapping_frac"] = sum(v for v in cnt.values() if v >= 2) / len(pairs)
        inv = {v: k for k, v in codes.items()}
        out["top_mappings"] = [(str(inv[a])[:30], str(inv[b])[:30], n) for (a, b), n in cnt.most_common(5) if n >= 2]
    return out
