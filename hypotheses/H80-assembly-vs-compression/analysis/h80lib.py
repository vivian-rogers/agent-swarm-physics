"""H80 estimators: assembly index (exact for short strings, Re-Pair grammar bound), compression family, AUC tools.

All functions take a token sequence (list/tuple of hashable tokens). Token identity matters only through equality,
so sequences are relabelled to first-occurrence ids before byte-level compression.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import math  # noqa: E402
import subprocess  # noqa: E402
import tempfile  # noqa: E402
import zlib  # noqa: E402
from collections import Counter  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402


# ============================================================================ relabel / bytes
def relabel(seq) -> tuple:
    ids, out = {}, []
    for s in seq:
        if s not in ids:
            ids[s] = len(ids)
        out.append(ids[s])
    return tuple(out)


def to_bytes(seq) -> bytes:
    r = relabel(seq)
    if max(r, default=0) < 256:
        return bytes(r)
    return b"".join(int(x).to_bytes(2, "little") for x in r)


# ============================================================================ assembly index
def _has_repeat(x) -> bool:
    seen = set()
    for i in range(len(x) - 1):
        if (x[i], x[i + 1]) in seen:
            return True
        seen.add((x[i], x[i + 1]))
    return False


def brute_assembly(seq, max_len: int = 9) -> int | None:
    """Exact assembly index by iterative deepening over pools of built substrings (reference implementation,
    tiny strings only). Every object on a minimal pathway is a substring of seq."""
    x = tuple(seq)
    n = len(x)
    if n <= 1:
        return 0
    if not _has_repeat(x):
        return n - 1
    if n > max_len:
        return None
    subs = {x[i:j] for i in range(n) for j in range(i + 2, n + 1)}
    base = frozenset((s,) for s in set(x))

    def dfs(pool, depth, seen):
        if x in pool:
            return True
        if depth == 0 or max(len(p) for p in pool) * (2 ** depth) < n:
            return False
        if seen.get(pool, -1) >= depth:
            return False
        seen[pool] = depth
        cands = {u + v for u in pool for v in pool if (u + v) in subs and (u + v) not in pool}
        return any(dfs(pool | {w}, depth - 1, seen) for w in sorted(cands, key=len, reverse=True))

    for d in range(math.ceil(math.log2(n)), n):
        if dfs(base, d, {}):
            return d
    return n - 1


def _tiles(d, avail) -> int:
    """Minimum number of pieces from avail (set of tuples) that tile d exactly."""
    n = len(d)
    best = [0] + [10 ** 9] * n
    lens = sorted({len(a) for a in avail})
    for i in range(1, n + 1):
        for L in lens:
            if L <= i and best[i - L] + 1 < best[i] and d[i - L:i] in avail:
                best[i] = best[i - L] + 1
    return best[n]


def exact_assembly(seq, max_len: int = 16, kmax: int = 5) -> int | None:
    """Assembly index via the duplicate-tiling formulation: choose a set D of repeated substrings; each d in
    D + {x} is built by sequential concatenation of a minimum tiling from single symbols and shorter members of D.
    a(x) = min_D sum_{d in D+{x}} (tiles(d) - 1). Checked against brute_assembly for L <= 9 (synthetic.py).
    |D| <= kmax (enough for L <= 16: a doubling chain needs ceil(log2 L) members). None if len > max_len."""
    from itertools import combinations
    x = tuple(seq)
    n = len(x)
    if n <= 1:
        return 0
    if not _has_repeat(x):
        return n - 1
    if n > max_len:
        return None
    cnt = Counter(x[i:j] for i in range(n) for j in range(i + 2, n + 1) if j - i < n)
    dup = sorted([s for s, c in cnt.items() if c >= 2], key=len)
    basis = {(s,) for s in set(x)}
    best = n - 1
    for k in range(1, min(kmax, len(dup)) + 1):
        if k > best:
            break
        for D in combinations(dup, k):
            cost, avail = 0, set(basis)
            for d in D:                       # sorted by length: shorter members are available
                t = _tiles(d, avail)
                if t < 2:
                    cost = 10 ** 9
                    break
                cost += t - 1
                avail.add(d)
                if cost >= best:
                    break
            if cost >= best:
                continue
            cost += _tiles(x, avail) - 1
            if cost < best:
                best = cost
    return best


def repair(seq):
    """Re-Pair grammar compression. Returns (n_rules, final_length). Ties broken by first occurrence."""
    s = list(relabel(seq))
    nxt = max(s, default=-1) + 1
    rules = 0
    while len(s) >= 2:
        cnt = Counter()
        first = {}
        i = 0
        last_pos = {}
        # non-overlapping pair counts
        for i in range(len(s) - 1):
            p = (s[i], s[i + 1])
            if last_pos.get(p, -2) == i - 1:   # overlap (aaa)
                continue
            cnt[p] += 1
            last_pos[p] = i
            first.setdefault(p, i)
        if not cnt:
            break
        best = max(cnt.items(), key=lambda kv: (kv[1], -first[kv[0]]))
        if best[1] < 2:
            break
        p = best[0]
        out, i = [], 0
        while i < len(s):
            if i < len(s) - 1 and (s[i], s[i + 1]) == p:
                out.append(nxt)
                i += 2
            else:
                out.append(s[i])
                i += 1
        s = out
        nxt += 1
        rules += 1
    return rules, len(s)


def assembly_rp(seq) -> int:
    """Upper bound on the assembly index: Re-Pair rules + (final string length - 1)."""
    if len(seq) <= 1:
        return 0
    r, m = repair(seq)
    return r + m - 1


def assembly_lower(seq) -> int:
    return math.ceil(math.log2(len(seq))) if len(seq) > 1 else 0


# ============================================================================ compression family
def lz76(seq) -> int:
    """Lempel-Ziv 1976 complexity (Kaspar-Schuster counting of new phrases)."""
    s = relabel(seq)
    n = len(s)
    if n == 0:
        return 0
    c, i = 1, 1
    while i < n:
        k = 1
        while i + k <= n and _occurs(s, i, k):
            k += 1
        c += 1
        i += k
    return c


def _occurs(s, i, k) -> bool:
    """True if s[i:i+k] occurs starting before i (overlap with the prefix allowed: search in s[:i+k-1])."""
    pat = s[i:i + k]
    hay = s[:i + k - 1]
    for j in range(0, len(hay) - k + 1):
        if hay[j:j + k] == pat:
            return True
    return False


def lz78(seq) -> int:
    """Number of LZ78 phrases."""
    s = relabel(seq)
    d, cur, c = set(), (), 0
    for t in s:
        cur = cur + (t,)
        if cur not in d:
            d.add(cur)
            c += 1
            cur = ()
    return c + (1 if cur else 0)


def entropies(seq):
    """Plug-in H1 (bits/token) and block entropy rate h2 = H(bigrams) - H1."""
    s = relabel(seq)
    n = len(s)
    if n < 2:
        return 0.0, 0.0
    c1 = np.array(list(Counter(s).values()), float)
    p1 = c1 / c1.sum()
    h1 = float(-(p1 * np.log2(p1)).sum())
    c2 = np.array(list(Counter(zip(s[:-1], s[1:])).values()), float)
    p2 = c2 / c2.sum()
    h2 = float(-(p2 * np.log2(p2)).sum())
    return h1, h2 - h1


def gzip_ratio(seq) -> float:
    b = to_bytes(seq)
    return len(zlib.compress(b, 9)) / max(len(b), 1)


def zstd_sizes(byte_list: list[bytes], level: int = 19) -> list[int]:
    """Compressed sizes with the zstd CLI, in one call (files in a temp dir)."""
    with tempfile.TemporaryDirectory(dir=os.environ.get("H80_TMP")) as d:
        d = Path(d)
        for i, b in enumerate(byte_list):
            (d / f"{i}.bin").write_bytes(b)
        subprocess.run(["zstd", "-q", f"-{level}", "-r", str(d), "-T2"], check=True, capture_output=True)
        return [(d / f"{i}.bin.zst").stat().st_size for i in range(len(byte_list))]


def ncd(x: bytes, y: bytes) -> float:
    cx, cy, cxy = (len(zlib.compress(b, 9)) for b in (x, y, x + y))
    return (cxy - min(cx, cy)) / max(cx, cy)


def features(seq) -> dict:
    h1, h2 = entropies(seq)
    return {"lz76": lz76(seq), "lz78": lz78(seq), "h1": h1, "h_rate": h2, "gzip": gzip_ratio(seq),
            "a_rp": assembly_rp(seq), "n_distinct": len(set(seq))}


# ============================================================================ classifier
def standardize(Xtr, Xte):
    mu, sd = Xtr.mean(0), Xtr.std(0)
    sd[sd == 0] = 1
    return (Xtr - mu) / sd, (Xte - mu) / sd


def fit_logit(X, y, w=None, lam: float = 1.0):
    from scipy.optimize import minimize
    n, k = X.shape
    w = np.ones(n) if w is None else w
    Xb = np.hstack([np.ones((n, 1)), X])

    def f(b):
        z = Xb @ b
        ll = w * (y * z - np.logaddexp(0, z))
        pen = 0.5 * lam * (b[1:] ** 2).sum()
        p = 1 / (1 + np.exp(-z))
        g = -(Xb.T @ (w * (y - p))) + lam * np.r_[0, b[1:]]
        return -ll.sum() + pen, g

    r = minimize(f, np.zeros(k + 1), jac=True, method="L-BFGS-B")
    return r.x


def predict_logit(b, X):
    return 1 / (1 + np.exp(-(b[0] + X @ b[1:])))


def auc(y, s, w=None) -> float:
    """Weighted Mann-Whitney AUC (ties count 1/2)."""
    y = np.asarray(y).astype(bool)
    s = np.asarray(s, float)
    w = np.ones(len(y)) if w is None else np.asarray(w, float)
    if y.all() or (~y).all():
        return float("nan")
    order = np.argsort(s, kind="mergesort")
    s, y, w = s[order], y[order], w[order]
    # group ties
    uniq, idx = np.unique(s, return_index=True)
    bounds = list(idx) + [len(s)]
    cum_neg = 0.0
    num = 0.0
    for a, b in zip(bounds[:-1], bounds[1:]):
        wp = w[a:b][y[a:b]].sum()
        wn = w[a:b][~y[a:b]].sum()
        num += wp * (cum_neg + 0.5 * wn)
        cum_neg += wn
    return float(num / (w[y].sum() * w[~y].sum()))


def oof_scores(X, y, groups, w=None, k: int = 5, seed: int = 0, lam: float = 1.0):
    """Out-of-fold predicted probabilities with folds blocked by group."""
    rng = np.random.default_rng(seed)
    ug = np.array(sorted(set(groups)))
    rng.shuffle(ug)
    fold_of = {g: i % k for i, g in enumerate(ug)}
    f = np.array([fold_of[g] for g in groups])
    out = np.full(len(y), np.nan)
    for i in range(k):
        te, tr = f == i, f != i
        if tr.sum() == 0 or te.sum() == 0 or len(set(y[tr])) < 2:
            continue
        Xtr, Xte = standardize(X[tr], X[te])
        b = fit_logit(Xtr, y[tr], None if w is None else w[tr], lam)
        out[te] = predict_logit(b, Xte)
    return out
