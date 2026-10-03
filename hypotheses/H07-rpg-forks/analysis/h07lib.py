"""H07 helpers: snapshot features and the copy / transformation decomposition.

Copy information (our reading of Kolchinsky & Corominas-Murtra 2020, NOT verified against the paper; documented proxy):
    I_copy = sum_x p(x) * d( p(Y=x | X=x) || p_Y(x) ) * 1[ p(Y=x | X=x) > p_Y(x) ],   d = binary KL (bits)
    I_transform = I(X;Y) - I_copy  (>= 0 by data processing on the coarse-graining y -> [y == x]).
Plug-in estimates; every information value is also reported minus a shuffle null (Y permuted across keys), which
keeps both marginals and removes all key-level dependence.
"""
from __future__ import annotations

import datetime as dt
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
P = ROOT / "data/processed/H07-rpg-forks"
SH = ROOT / "data/processed/shared"
UTC = dt.timezone.utc
T0 = dt.datetime(2026, 3, 16, 16, 20, 5, 640000, tzinfo=UTC)
T35_END = dt.datetime(2026, 3, 23, 11, 17, 17, 918000, tzinfo=UTC)
F_REGIME = dt.datetime(2026, 3, 24, tzinfo=UTC)
ABSENT = "\x00ABSENT"
FEATURES = ["files", "files_src", "files_tests", "functions", "numbers_data", "numbers_all", "names", "entities"]
SETS = ["idents", "name_set", "entity_ids"]


# ----------------------------------------------------------------------------- information measures

def _xlogy(a, b):
    with np.errstate(divide="ignore", invalid="ignore"):
        r = a * np.log2(a / b)
    return np.where(a > 0, r, 0.0)


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


def decompose(xv: list, yv: list, n_null: int = 0, seed: int = 0) -> dict:
    """Copy/transform decomposition for paired values (any hashables); shuffle null if n_null > 0."""
    codes: dict = {}
    x = np.fromiter((codes.setdefault(v, len(codes)) for v in xv), dtype=np.int64, count=len(xv))
    y = np.fromiter((codes.setdefault(v, len(codes)) for v in yv), dtype=np.int64, count=len(yv))
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


def _p(x):
    c = np.bincount(x)
    c = c[c > 0]
    return c / c.sum()

# ----------------------------------------------------------------------------- snapshot features


class Features:
    """Keyed features {feature: {key: value}} and set features {set: set} for any tree (path -> blob)."""

    def __init__(self):
        self.num = pl.read_parquet(P / "blob_numbers.parquet")
        self.fun = pl.read_parquet(P / "blob_functions.parquet")
        self.idn = pl.read_parquet(P / "blob_idents.parquet")
        self.nam = pl.read_parquet(P / "blob_names.parquet")
        self.ent = pl.read_parquet(P / "blob_entities.parquet")
        self.cache: dict = {}
        self._by_blob = {}
        for name, df, cols in [("num", self.num, ["ctx", "k", "value", "raw", "data"]),
                               ("fun", self.fun, ["qualname", "k", "body_hash"]),
                               ("idn", self.idn, ["ident"]), ("nam", self.nam, ["ctx", "field", "k", "value"]),
                               ("ent", self.ent, ["entity_id", "name"])]:
            d: dict = {}
            for row in df.select(["blob", *cols]).iter_rows():
                d.setdefault(row[0], []).append(row[1:])
            self._by_blob[name] = d

    def of_tree(self, tree: dict) -> tuple[dict, dict]:
        """tree: {path: blob}. Returns (keyed, sets)."""
        K = {f: {} for f in FEATURES}
        S = {s: set() for s in SETS}
        for path, blob in tree.items():
            K["files"][path] = blob
            if path.startswith("tests/"):
                K["files_tests"][path] = blob
            if path.startswith("src/") and path.endswith(".js"):
                K["files_src"][path] = blob
                for ctx, k, val, raw, data in self._by_blob["num"].get(blob, ()):
                    v = val if val is not None else raw
                    K["numbers_all"][f"{path}::{ctx}#{k}"] = v
                    if data:
                        K["numbers_data"][f"{path}::{ctx}#{k}"] = v
                for q, k, h in self._by_blob["fun"].get(blob, ()):
                    K["functions"][f"{path}::{q}#{k}"] = h
                for (ident,) in self._by_blob["idn"].get(blob, ()):
                    S["idents"].add(ident)
                for ctx, field, k, v in self._by_blob["nam"].get(blob, ()):
                    K["names"][f"{path}::{ctx}::{field}#{k}"] = v
                    S["name_set"].add(v)
                for eid, nm in self._by_blob["ent"].get(blob, ()):
                    K["entities"][f"{path}::{eid}"] = nm
                    S["entity_ids"].add(eid)
        return K, S


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


def load_trees():
    t = pl.read_parquet(P / "fp_trees.parquet")
    snaps = t.select("lineage", "sha", "k", "t_commit", "n_commits", "active_h").unique().sort("lineage", "k")
    trees: dict = {}
    for lin, sha, path, blob in t.select("lineage", "sha", "path", "blob").iter_rows():
        trees.setdefault(sha, {})[path] = blob
    return snaps, trees


def transform_test(KA: dict, KY: dict, n_null: int = 200, seed: int = 1) -> dict:
    """Systematic-transformation test on keys present in both (deletions excluded).

    Conditional null: keep copied pairs fixed, permute the outputs among changed keys. This removes any systematic
    x -> y mapping among changed keys but keeps the copy part and both marginals. I_transform_cx = observed minus
    the conditional-null mean (bits); z = excess / null sd. Also counts changed pairs whose exact (x, y) mapping is
    shared with another key ('repeated mappings', e.g. mpCost 6 -> 4 in six abilities).
    """
    keys = [k for k in KA if k in KY]
    xv = [KA[k] for k in keys]
    yv = [KY[k] for k in keys]
    codes: dict = {}
    x = np.fromiter((codes.setdefault(v, len(codes)) for v in xv), dtype=np.int64, count=len(xv))
    y = np.fromiter((codes.setdefault(v, len(codes)) for v in yv), dtype=np.int64, count=len(yv))
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
        from collections import Counter
        cnt = Counter(pairs)
        out["repeated_mapping_frac"] = sum(v for v in cnt.values() if v >= 2) / len(pairs)
        inv = {v: k for k, v in codes.items()}
        out["top_mappings"] = [(str(inv[a])[:30], str(inv[b])[:30], n) for (a, b), n in cnt.most_common(5) if n >= 2]
    return out
