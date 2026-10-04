"""Newton-step (second-order AIK) entropy-production estimators for antisymmetric observables, shared.

Aguilera, Ito & Kolchinsky (PRL 136, 077101, 2026): for antisymmetric observables g (g(reversed) = -g) the
max-ent bound is Sigma_g = max_theta theta.<g> - ln<exp(-theta.g)>. Its second-order (Newton-step) form is
    L(theta) = 2 theta.mu - 1/2 theta' K theta,   maximized at theta* = 2 K^-1 mu, value 2 mu' K^-1 mu,
with mu = <g> and K = Cov(g). Two estimators of it live here.

LEGACY (kept callable for comparison; do not use for new work)
  ep_gauss_crossfit(G, days, k, ridge)        H05 analysis/ep.py, verbatim. Cross-product form
                                              2 mean_{a != b} gbar_a' (K + r I)^-1 gbar_b over day folds, K from all
                                              rows, scalar ridge r = ridge * tr(K)/d.
  newton_subsets_xprod(G, days, subsets, ...) H14 h14lib.newton_subsets, verbatim (same form, one K, per-subset r).
  newton_counts_xprod(C_labels, ridge)        H14 r1b_lib / H56 h56lib newton_counts, verbatim (closed form of
                                              ep_gauss_crossfit on transition indicators).
  Known issue (H90 A1, infra/README "Known issues"): when the number of observables d approaches the number of rows,
  K^-1 inflates and the cross product diverges in variance; with nested observable sets the subset-dependent scalar
  ridge shrinks the shared columns differently, so Sigma(S1 u S2) - Sigma(S1) is biased (+0.04 nats/step in
  independent synthetic worlds, H90).

CORRECTED (H90 amendments A1 + A2; the default for new work)
  ep_newton_heldout / newton_subsets_heldout / newton_counts_heldout
  For each day fold f: theta_f = 2 (K_-f + Lambda)^-1 mu_-f from the other folds, and L_f = 2 theta_f.mu_f
  - 1/2 theta_f' K_f theta_f on fold f; Sigma_hat = n-weighted mean of L_f.
  Lambda = diag(lambda_k), lambda_k = c (K_kk + mean diagonal of k's block) (per-column ridge, floored by the block's
  mean variance; c = 1 as validated by H90). Blocks are observable families (e.g. single / mean-field / pairwise);
  the default is one block. Because lambda_k depends only on column k and its block, a column shared by nested sets
  is shrunk identically in every set. L(theta) at any theta fitted without fold f is (to second order) a lower bound
  on Sigma_g, so overfitting lowers the estimate instead of inflating it. Price: the ridge shrinks theta, so in the
  large-sample limit with uncorrelated columns of equal variance the estimate is ~(4/3 - 2/9)/2 = 0.56 of
  2 mu'K^-1 mu at c = 1 (0.89 at c = 0.25). Compare estimates and nulls on the same estimator only.

Folds: sorted unique day labels, fold = rank % k, k = max(2, min(k, n_days)) (H05 `_folds`); the count forms merge
per-label count matrices by label index % k (H14 `_merge_folds`), which is the same rule for 0..L-1 day codes.

Synthetic size / power check (2026-10-04): `infra/shared/ep_newton_synthetic.py`.
Verify: `uv run python infra/shared/ep_newton.py --verify` (legacy copies equal the hypothesis originals; the count
and matrix forms of the corrected estimator agree; quick independent-world sanity check).
No project data is read here.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ.setdefault(_v, "2")

import sys  # noqa: E402

import numpy as np  # noqa: E402

LEGACY_RIDGE = 1e-3
RIDGE_C = 1.0


# ============================================================================ folds
def fold_ids(days, k: int = 5):
    """H05 rule: sorted unique day labels, fold = rank % k, k = max(2, min(k, n_days)). Returns (fold per row, k)."""
    days = np.asarray(days)
    u = np.unique(days)
    k = max(2, min(k, len(u)))
    rank = np.searchsorted(u, days)
    return rank % k, k


# ============================================================================ legacy (verbatim copies)
def ep_gauss_crossfit(G, days, k=5, ridge=LEGACY_RIDGE):
    """LEGACY. H05 `analysis/ep.py: ep_gauss_crossfit`, verbatim (see module docstring for the known issue)."""
    G = np.asarray(G, dtype=np.float64)
    days = np.asarray(days)
    f, k = fold_ids(days, k)
    K = np.cov(G, rowvar=False).reshape(G.shape[1], G.shape[1])
    K = K + ridge * np.trace(K) / max(len(K), 1) * np.eye(len(K))
    means = np.array([G[f == q].mean(0) for q in range(k) if (f == q).any()])
    W = np.linalg.solve(K, means.T).T
    M = means @ W.T
    kk = len(means)
    off = (M.sum() - np.trace(M)) / (kk * (kk - 1))
    per = np.array([(M[a].sum() - M[a, a]) / (kk - 1) for a in range(kk)])
    return {"sigma": float(2 * off), "se": float(2 * per.std(ddof=1) / np.sqrt(kk)),
            "plugin": float(2 * G.mean(0) @ np.linalg.solve(K, G.mean(0))), "T": int(len(G)), "d": int(G.shape[1])}


def newton_subsets_xprod(G, days, subsets, k=None, ridge=LEGACY_RIDGE):
    """LEGACY. H14 `h14lib.newton_subsets`, verbatim: one K and one set of fold means, scalar ridge per subset."""
    G = np.asarray(G, dtype=np.float64)
    days = np.asarray(days)
    if len(np.unique(days)) < 2:
        return {nm: np.nan for nm in subsets}
    u = np.unique(days)
    kk = int(min(5, len(u))) if k is None else k
    fold_of = {dd: i % kk for i, dd in enumerate(u)}
    f = np.array([fold_of[x] for x in days])
    K = np.cov(G, rowvar=False).reshape(G.shape[1], G.shape[1])
    means = np.array([G[f == qq].mean(0) for qq in range(kk) if (f == qq).any()])
    out = {}
    for nm, cols in subsets.items():
        cols = np.asarray(cols)
        if len(cols) == 0:
            out[nm] = np.nan
            continue
        Ks = K[np.ix_(cols, cols)]
        Ks = Ks + ridge * np.trace(Ks) / len(Ks) * np.eye(len(Ks))
        Ms = means[:, cols]
        W = np.linalg.solve(Ks, Ms.T).T
        M = Ms @ W.T
        m = len(Ms)
        out[nm] = float(2 * (M.sum() - np.trace(M)) / (m * (m - 1)))
    return out


def merge_folds(C_labels, k=None):
    """Per-label (day) count matrices (L, q, q) -> per-fold counts (k, q, q), fold = label index % k (H14)."""
    C_labels = np.asarray(C_labels, dtype=np.float64)
    Lb = len(C_labels)
    k = min(5, Lb) if k is None else k
    F = np.zeros((k,) + C_labels.shape[1:])
    for i in range(Lb):
        F[i % k] += C_labels[i]
    return F


def newton_counts_xprod(C_labels, ridge=LEGACY_RIDGE):
    """LEGACY. H14 `r1b_lib.newton_counts` / H56 `h56lib.newton_counts`, verbatim."""
    C_labels = np.asarray(C_labels, dtype=np.float64)
    if len(C_labels) < 2:
        return np.nan
    F = merge_folds(C_labels)
    C = F.sum(0)
    n = C.sum()
    if n < 3:
        return np.nan
    q = C.shape[0]
    iu, ju = np.triu_indices(q, 1)
    s = C[iu, ju] + C[ju, iu]
    keep = s > 0
    if not keep.any():
        return np.nan
    iu, ju, s = iu[keep], ju[keep], s[keep]
    gbar = (C[iu, ju] - C[ju, iu]) / n
    K = (np.diag(s) - n * np.outer(gbar, gbar)) / (n - 1)
    K = K + ridge * np.trace(K) / len(K) * np.eye(len(K))
    nf = F.sum((1, 2))
    ok = nf > 0
    means = (F[ok][:, iu, ju] - F[ok][:, ju, iu]) / nf[ok][:, None]
    kk = len(means)
    if kk < 2:
        return np.nan
    W = np.linalg.solve(K, means.T).T
    M = means @ W.T
    return float(2 * (M.sum() - np.trace(M)) / (kk * (kk - 1)))


# ============================================================================ corrected: sufficient statistics
def fold_stats(G, days, k: int = 5):
    """Per-fold sufficient statistics [(n_f, s1_f, s2_f)] with s1 = sum g, s2 = sum g g'. Folds by `fold_ids`."""
    G = np.asarray(G, dtype=np.float64)
    f, k = fold_ids(days, k)
    out = []
    for q in range(k):
        m = f == q
        Gq = G[m]
        out.append((int(m.sum()), Gq.sum(0), Gq.T @ Gq))
    return out


def _mean_cov(n, s1, s2):
    mu = s1 / n
    K = (s2 - n * np.outer(mu, mu)) / max(n - 1, 1)
    return mu, K


def _lambda(dK, block, c):
    """Per-column ridge lambda_k = c (K_kk + mean diagonal of k's block); one block when block is None."""
    if block is None:
        return c * (dK + dK.mean())
    block = np.asarray(block)
    ub, inv = np.unique(block, return_inverse=True)
    bm = np.array([dK[inv == b].mean() for b in range(len(ub))])
    return c * (dK + bm[inv])


def newton_heldout_from_folds(fst, subsets: dict, c: float = RIDGE_C, block=None) -> dict:
    """Corrected held-out Newton bound from per-fold statistics (see module docstring).

    fst: [(n_f, s1_f, s2_f)] per fold (all of dimension d); subsets: {name: column indices}; block: block id per column
    (None = one block). Returns {name: {"sigma", "per_fold", "w"}}; sigma is the n-weighted mean of the per-fold L_f."""
    fs = [x for x in fst if x[0] >= 2]
    out = {nm: {"sigma": np.nan, "per_fold": [], "w": []} for nm in subsets}
    if len(fs) < 2:
        return out
    ntot = sum(x[0] for x in fs)
    s1tot = sum(x[1] for x in fs)
    s2tot = sum(x[2] for x in fs)
    for nf, s1f, s2f in fs:
        nt = ntot - nf
        if nt < 2:
            continue
        mut, Kt = _mean_cov(nt, s1tot - s1f, s2tot - s2f)
        muf, Kf = _mean_cov(nf, s1f, s2f)
        dK = np.clip(np.diag(Kt), 0, None)
        lam_all = _lambda(dK, block, c)
        for nm, cols in subsets.items():
            cols = np.asarray(cols, dtype=np.int64)
            if len(cols) == 0:
                continue
            Ks = Kt[np.ix_(cols, cols)]
            tr = float(np.trace(Ks))
            if tr <= 0:
                out[nm]["per_fold"].append(0.0)
                out[nm]["w"].append(nf)
                continue
            lam = np.clip(lam_all[cols], 1e-12 * tr / len(cols), None)
            th = 2 * np.linalg.solve(Ks + np.diag(lam), mut[cols])
            out[nm]["per_fold"].append(float(2 * th @ muf[cols] - 0.5 * th @ Kf[np.ix_(cols, cols)] @ th))
            out[nm]["w"].append(nf)
    for nm, r in out.items():
        if r["per_fold"]:
            r["sigma"] = float(np.average(r["per_fold"], weights=r["w"]))
    return out


def _se(per_fold):
    v = np.asarray(per_fold, dtype=np.float64)
    return float(v.std(ddof=1) / np.sqrt(len(v))) if len(v) > 1 else np.nan


def ep_newton_heldout(G, days, k: int = 5, c: float = RIDGE_C, block=None) -> dict:
    """Corrected drop-in for `ep_gauss_crossfit`: held-out Newton bound (nats per row) on all columns of G.

    Returns {"sigma", "se" (between-fold SE of L_f), "per_fold", "T", "d"}."""
    G = np.asarray(G, dtype=np.float64)
    if G.shape[1] == 0 or len(np.unique(days)) < 2:
        return {"sigma": np.nan, "se": np.nan, "per_fold": [], "T": int(len(G)), "d": int(G.shape[1])}
    r = newton_heldout_from_folds(fold_stats(G, days, k), {"all": np.arange(G.shape[1])}, c=c, block=block)["all"]
    return {"sigma": r["sigma"], "se": _se(r["per_fold"]), "per_fold": r["per_fold"], "T": int(len(G)),
            "d": int(G.shape[1])}


def newton_subsets_heldout(G, days, subsets: dict, k=None, c: float = RIDGE_C, block=None, return_folds=False):
    """Corrected drop-in for `newton_subsets_xprod`: {name: sigma} for several column subsets of G sharing one set
    of fold statistics and one per-column ridge. k=None uses min(5, n_days) (H14). With return_folds, also returns
    {name: per-fold L_f list} (for SEs of nested differences: difference the per-fold lists)."""
    G = np.asarray(G, dtype=np.float64)
    days = np.asarray(days)
    nd = len(np.unique(days))
    if nd < 2:
        r = {nm: np.nan for nm in subsets}
        return (r, {nm: [] for nm in subsets}) if return_folds else r
    kk = int(min(5, nd)) if k is None else k
    res = newton_heldout_from_folds(fold_stats(G, days, kk), subsets, c=c, block=block)
    sig = {nm: v["sigma"] for nm, v in res.items()}
    return (sig, {nm: v["per_fold"] for nm, v in res.items()}) if return_folds else sig


def newton_counts_heldout(C_labels, c: float = RIDGE_C, k=None) -> float:
    """Corrected drop-in for `newton_counts_xprod`: the held-out Newton bound on antisymmetrized transition indicators
    g_ab = 1[a->b] - 1[b->a] (a < b, pairs with any count kept), from per-label count matrices (L, q, q).

    Closed form: within a fold, E[g_ab g_cd] = (n_ab + n_ba)/n if (a,b) = (c,d), else 0, so K = diag(s)/n - mu mu'
    (times n/(n-1)). Equal to `ep_newton_heldout` on the indicator matrix (checked in --verify). One block."""
    C_labels = np.asarray(C_labels, dtype=np.float64)
    if len(C_labels) < 2:
        return np.nan
    F = merge_folds(C_labels, k)
    C = F.sum(0)
    if C.sum() < 3:
        return np.nan
    q = C.shape[0]
    iu, ju = np.triu_indices(q, 1)
    keep = (C[iu, ju] + C[ju, iu]) > 0
    if not keep.any():
        return np.nan
    iu, ju = iu[keep], ju[keep]
    fst = []
    for Ff in F:
        n = Ff.sum()
        s = Ff[iu, ju] + Ff[ju, iu]
        s1 = Ff[iu, ju] - Ff[ju, iu]
        fst.append((int(round(n)), s1, np.diag(s)))
    return newton_heldout_from_folds(fst, {"all": np.arange(len(iu))}, c=c)["all"]["sigma"]


# ============================================================================ verify
def _random_chain(q, n_days, L, rng, drive=0.3):
    P = rng.dirichlet(np.ones(q) * 2, q)
    for a in range(q):
        P[a, (a + 1) % q] += drive
    P /= P.sum(1, keepdims=True)
    x, d = [], []
    for dd in range(n_days):
        s = rng.integers(q)
        for _ in range(L):
            x.append(s)
            d.append(dd)
            s = rng.choice(q, p=P[s])
    return np.array(x), np.array(d)


def verify():
    """Read-only checks. 1) legacy copies equal the hypothesis originals (read-only import); 2) count form ==
    matrix form of the corrected estimator; 3) quick independent-world nested check (old vs new sigma_coll)."""
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    rng = np.random.default_rng(1)
    ok = True
    # 1. legacy equality
    G = rng.normal(0, 1, (900, 40)) + 0.03
    days = np.repeat(np.arange(9), 100)
    sys.path.insert(0, str(root / "hypotheses/H05-rooms-cut/analysis"))
    try:
        import ep as h05ep  # read-only
        a, b = h05ep.ep_gauss_crossfit(G, days)["sigma"], ep_gauss_crossfit(G, days)["sigma"]
        print(f"[1] ep_gauss_crossfit legacy == H05: {a == b} ({a:.6g})")
        ok &= a == b
    except Exception as e:  # pragma: no cover
        print("[1] H05 ep.py not importable:", e)
    sys.path.insert(0, str(root / "hypotheses/H14-behavior-entropy-production/analysis"))
    try:
        import r1b_lib as h14b  # read-only
        x, d = _random_chain(6, 7, 300, rng)
        Cl = np.zeros((7, 6, 6))
        np.add.at(Cl, (d[1:][d[1:] == d[:-1]], x[:-1][d[1:] == d[:-1]], x[1:][d[1:] == d[:-1]]), 1)
        a = h14b.newton_counts(Cl) if getattr(h14b, "EP", "xprod") == "xprod" else h14b._newton_counts_xprod(Cl)
        b = newton_counts_xprod(Cl)
        print(f"[1] newton_counts legacy == H14 r1b_lib: {np.isclose(a, b, rtol=1e-12)} ({a:.6g})")
        ok &= bool(np.isclose(a, b, rtol=1e-12))
        sub = {"s1": np.arange(20), "s12": np.arange(40)}
        import h14lib as h14  # read-only
        fn = h14.newton_subsets if getattr(h14, "EP", "xprod") == "xprod" else h14._newton_subsets_xprod
        a, b = fn(G, days, sub), newton_subsets_xprod(G, days, sub)
        print(f"[1] newton_subsets legacy == H14 h14lib: {a == b}")
        ok &= a == b
    except Exception as e:  # pragma: no cover
        print("[1] H14 libs not importable:", e)
    # 2. counts == matrix form
    x, d = _random_chain(6, 8, 250, rng)
    okt = d[1:] == d[:-1]
    prev, nxt, dd = x[:-1][okt], x[1:][okt], d[1:][okt]
    Cl = np.zeros((8, 6, 6))
    np.add.at(Cl, (dd, prev, nxt), 1)
    iu, ju = np.triu_indices(6, 1)
    code = prev * 6 + nxt
    Gi = np.stack([(code == a * 6 + b).astype(float) - (code == b * 6 + a) for a, b in zip(iu, ju)], 1)
    Gi = Gi[:, np.any(Gi != 0, 0)]
    a, b = newton_counts_heldout(Cl), ep_newton_heldout(Gi, dd, k=5)["sigma"]
    print(f"[2] corrected count form == matrix form: {np.isclose(a, b, rtol=1e-9)} ({a:.6g} vs {b:.6g})")
    ok &= bool(np.isclose(a, b, rtol=1e-9))
    a0, b0 = newton_counts_xprod(Cl), ep_gauss_crossfit(Gi, dd)["sigma"]
    print(f"[2] legacy count form == legacy matrix form: {np.isclose(a0, b0, rtol=1e-9)} ({a0:.6g} vs {b0:.6g})")
    # 3. quick nested check: independent Gaussian 'single' block with a real mean, 'coupling' block pure noise, d ~ T/3
    d1, d2, n_days, Ld = 60, 120, 5, 120
    vals = {"old": [], "new": []}
    for _ in range(30):
        G1 = rng.normal(0, 1, (n_days * Ld, d1)) + 0.05
        G2 = rng.normal(0, 1, (n_days * Ld, d2)) * 0.3
        GG = np.hstack([G1, G2])
        dd = np.repeat(np.arange(n_days), Ld)
        sub = {"s1": np.arange(d1), "s12": np.arange(d1 + d2)}
        o = newton_subsets_xprod(GG, dd, sub)
        n = newton_subsets_heldout(GG, dd, sub, block=np.r_[np.zeros(d1), np.ones(d2)])
        vals["old"].append(o["s12"] - o["s1"])
        vals["new"].append(n["s12"] - n["s1"])
    for kx, v in vals.items():
        v = np.array(v)
        print(f"[3] independent blocks, d = {d1 + d2}, T = {n_days * Ld}: sigma_coll {kx} mean {v.mean():+.4f} "
              f"(SE {v.std(ddof=1) / np.sqrt(len(v)):.4f})")
    print("verify:", "OK" if ok else "FAILED")
    return ok


if __name__ == "__main__":
    if "--verify" in sys.argv:
        sys.exit(0 if verify() else 1)
    print(__doc__)
