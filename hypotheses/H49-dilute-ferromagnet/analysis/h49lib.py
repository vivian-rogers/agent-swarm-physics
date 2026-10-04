"""H49 core library: conditioned pseudolikelihood (PL) inverse Ising per unit, joint block-shift surrogates,
bond statistics against the pooled-surrogate null, percolation of the significant-bond graph, excess-covariance
concentration (CV-C10), day-block bootstrap.

Read-only imports (never modified): H02 `h02lib.block_ids` (30-min blocks, short trailing block merged) and H38
`h38lib` (MASK_SETS reason codes; `impute`/`block_suff`/`cw` only to verify that the conditioned covariance reproduces
H38's mask_scaffold gain).

Conventions:
  spins s in {-1,+1}; logistic coefficients B = 2J (P(+1) = sigma(2H)); ridge LAM on B (H02's lambda = 1);
  block field delta_i(b) unpenalized; symmetrized bond Js = (J + J^T)/2.
  Conditioning (H38 agent-state conditioning): rows with sched dropped; an agent-minute is unavailable if the agent is
  silent with a reason in `codes`; predictors x_j = s_j - m_j(b) on available minutes (m over available minutes of the
  block), 0 otherwise; target i's likelihood uses its available minutes in blocks where it is not constant.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
os.environ.setdefault("POLARS_MAX_THREADS", "2")

import importlib.util  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
from scipy.sparse import csr_matrix  # noqa: E402
from scipy.sparse.csgraph import connected_components  # noqa: E402

sys.dont_write_bytecode = True
HYP = Path(__file__).resolve().parents[1]
ROOT = HYP.parents[1]
DATA = ROOT / "data/processed/H49-dilute-ferromagnet"
SH = ROOT / "data/processed/shared"
SEED = 20261049
LAM = 1.0
MIN_BLOCK_N = 5
R_NONE, R_PRE, R_POST, R_INFRA, R_CONSOL, R_PAUSE = 0, 1, 2, 3, 4, 5
CODES = {"raw": (), "edge": (R_PRE, R_POST), "scaffold": (R_PRE, R_POST, R_INFRA, R_CONSOL)}


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


h02 = _load("h02lib", ROOT / "hypotheses/H02-couplings-are-real/analysis/h02lib.py")


def h38():
    """H38 library (lazy: it imports H12's library too)."""
    if "h38lib" not in sys.modules:
        _load("h38lib", ROOT / "hypotheses/H38-platform-stalls/analysis/h38lib.py")
    return sys.modules["h38lib"]


# ------------------------------------------------------------------------------------------- provenance
def write_prov(name: str, built_by: str, params: dict | None = None, tables=None):
    """Add / replace one entry of data/processed/H49-dilute-ferromagnet/_provenance.json."""
    import datetime as dt
    import json
    import subprocess
    r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    d = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain"], capture_output=True, text=True).stdout
    p = DATA / "_provenance.json"
    prov = json.loads(p.read_text()) if p.exists() else {}
    prov[name] = {"built_by": built_by, "git_commit": (r.stdout.strip() or "none") + ("+uncommitted" if d.strip() else ""),
                  "inputs": [{"source": "ai-village (shared derived tables)",
                              "revision": "838b4150303ca8228e8edb432d8b8ccae353d258",
                              "tables": tables or ["activity_bins_fixed", "outages_fixed/reasons",
                                                   "outages_fixed/stall_minutes", "period_units", "calendar"]}],
                  "params": params or {}, "built_at": dt.datetime.now(dt.UTC).isoformat()}
    p.write_text(json.dumps(prov, indent=1, default=str))


# ------------------------------------------------------------------------------------------- layout
def block_starts(bid: np.ndarray) -> np.ndarray:
    """Start index of each run of equal block id (rows are in (day, minute) order, so ids are non-decreasing)."""
    return np.flatnonzero(np.r_[True, bid[1:] != bid[:-1]])


def prep(S, R, sched, day, minute, variant: str, Tk=None):
    """Rows, availability and block ids for one variant. raw keeps every minute and every agent-minute."""
    codes = CODES[variant]
    keep = np.ones(S.shape[0], bool) if variant == "raw" else ~sched
    S2, R2 = S[keep], R[keep]
    bid = h02.block_ids(day[keep], minute[keep])
    avail = np.ones_like(S2, dtype=bool) if not codes else ~((S2 < 0) & np.isin(R2, codes))
    T2 = Tk[keep] if Tk is not None else None
    return S2, avail, bid, T2, keep


def center(S, avail, bid):
    """x = s - block mean over available minutes (available minutes), 0 elsewhere. Also per-block counts."""
    st = block_starts(bid)
    Xf = np.where(avail, S, 0).astype(np.float64)
    A = avail.astype(np.float64)
    sums = np.add.reduceat(Xf, st, axis=0)
    cnt = np.add.reduceat(A, st, axis=0)
    m = np.where(cnt > 0, sums / np.maximum(cnt, 1), 0.0)
    nb = np.diff(np.r_[st, len(bid)])
    bidx = np.repeat(np.arange(len(st)), nb)
    x = np.where(avail, S - m[bidx], 0.0)
    return x, st, bidx, cnt, sums


# ------------------------------------------------------------------------------------------- PL fit
def _sig(z):
    return 0.5 * (1.0 + np.tanh(0.5 * z))


def fit_pl(S, avail, bid, lam: float = LAM, max_iter: int = 30, tol: float = 1e-7):
    """Conditioned equal-time pseudolikelihood with unpenalized block fields, exact joint Newton per target
    (Schur complement over the block-field parameters). Returns J (N x N, J[i, j] = effect of j on i, Ising units),
    Js (symmetrized), info."""
    T, N = S.shape
    x, st, bidx, cnt, sums = center(S, avail, bid)
    y = (S > 0).astype(np.float64)
    npos = np.add.reduceat(np.where(avail, y, 0.0), st, axis=0)
    inform = (npos > 0) & (npos < cnt)  # (nb, N)
    w = (avail & inform[bidx]).astype(np.float64)
    d = np.log((npos + 0.5) / (cnt - npos + 0.5))  # logit init
    B = np.zeros((N, N))
    eye = np.eye(N)

    def objective(Bm, dm):
        eta = dm[bidx] + x @ Bm.T
        return -(w * (y * eta - np.logaddexp(0.0, eta))).sum(0) + 0.5 * lam * (Bm ** 2).sum(1)

    obj = objective(B, d)
    it = 0
    for it in range(max_iter):
        eta = d[bidx] + x @ B.T
        mu = _sig(eta)
        r = w * (y - mu)
        W = w * mu * (1 - mu)
        gd = np.add.reduceat(r, st, axis=0)
        D = np.add.reduceat(W, st, axis=0)
        gB = (x.T @ r).T - lam * B
        sB = np.zeros((N, N)); sd = np.zeros_like(d)
        for i in range(N):
            Wi = W[:, i]
            xw = x * Wi[:, None]
            F = xw.T @ x + lam * eye
            E = np.add.reduceat(xw, st, axis=0)
            Di = D[:, i]
            Dinv = np.where(Di > 1e-12, 1.0 / np.maximum(Di, 1e-12), 0.0)
            Sch = F - E.T @ (E * Dinv[:, None])
            rhs = gB[i] - E.T @ (gd[:, i] * Dinv)
            Sch[i, :] = 0.0; Sch[:, i] = 0.0; Sch[i, i] = 1.0; rhs[i] = 0.0
            s_b = np.linalg.solve(Sch, rhs)
            sB[i] = s_b
            sd[:, i] = Dinv * (gd[:, i] - E @ s_b)
        t = np.ones(N)
        for _bt in range(15):
            Bn = B + t[:, None] * sB
            dn = d + t[None, :] * sd
            on = objective(Bn, dn)
            bad = on > obj + 1e-9
            if not bad.any():
                break
            t[bad] *= 0.5
        B, d, obj = Bn, dn, on
        if np.abs(t[:, None] * sB).max() < tol:
            break
    J = B / 2.0
    np.fill_diagonal(J, 0.0)
    return J, (J + J.T) / 2.0, {"iters": it + 1, "rows_used": w.sum(0)}


def cov_bar(x, st, mask_small=True, rows=None):
    """Pooled within-block covariance C = sum_t x_i x_j / sum_b n_b over blocks with >= MIN_BLOCK_N rows
    (optionally only rows selected by boolean `rows`)."""
    nb = np.diff(np.r_[st, x.shape[0]])
    ok = np.repeat(nb >= MIN_BLOCK_N, nb) if mask_small else np.ones(x.shape[0], bool)
    if rows is not None:
        ok = ok & rows
    xs = x[ok]
    n = ok.sum()
    if n == 0:
        return np.full((x.shape[1], x.shape[1]), np.nan)
    return xs.T @ xs / n


def vr_g(C):
    tr = np.trace(C)
    if not np.isfinite(tr) or tr <= 0:
        return np.nan, np.nan
    VR = C.sum() / tr
    return VR, 1 - 1 / VR


# ------------------------------------------------------------------------------------------- surrogates
def segments(day, minute):
    """Index arrays of (day, 30-min block) segments over all rows (H38's joint shift segments)."""
    bid = h02.block_ids(day, minute)
    st = block_starts(bid)
    en = np.r_[st[1:], len(bid)]
    return [np.arange(a, b) for a, b in zip(st, en)]


def joint_shift(arrays, segs, rng):
    """Independent circular shift of each agent's series within each segment; the same shift for every array."""
    outs = [np.empty_like(a) for a in arrays]
    N = arrays[0].shape[1]
    cols = np.arange(N)[None, :]
    for idx in segs:
        L = idx.size
        if L < 2:
            for a, o in zip(arrays, outs):
                o[idx] = a[idx]
            continue
        sh = rng.integers(1, L, size=N)
        ar = (np.arange(L)[:, None] - sh[None, :]) % L
        for a, o in zip(arrays, outs):
            o[idx] = a[idx][ar, cols]
    return outs


# ------------------------------------------------------------------------------------------- one dataset, one variant
def analyze_variant(S, R, sched, day, minute, variant, Tk=None, talk_cols=None, parity=None):
    """Fit PL and covariance for one variant. Returns dict with Js (activity), C, C halves (even/odd block parity),
    and the talk versions if Tk given (talk_cols: boolean agent subset)."""
    S2, av, bid, T2, keep = prep(S, R, sched, day, minute, variant, Tk)
    J, Js, info = fit_pl(S2, av, bid)
    x, st, bidx, _, _ = center(S2, av, bid)
    C = cov_bar(x, st)
    par = bidx % 2 == 0
    out = {"Js": Js, "C": C, "CA": cov_bar(x, st, rows=par), "CB": cov_bar(x, st, rows=~par), "iters": info["iters"]}
    if T2 is not None and talk_cols is not None and talk_cols.sum() >= 3:
        Tt = T2[:, talk_cols]; at = av[:, talk_cols]
        _, Jst, _ = fit_pl(Tt, at, bid)
        xt, stt, _, _, _ = center(Tt, at, bid)
        out["Js_t"] = Jst
        out["C_t"] = cov_bar(xt, stt)
    return out


# ------------------------------------------------------------------------------------------- bond statistics
def triu(N):
    return np.triu_indices(N, 1)


def loo_z(nul):
    """nul: (B, P) surrogate bond values. Returns per-pair mean, sd and the leave-one-out z of every surrogate."""
    Bn = nul.shape[0]
    s1 = nul.sum(0); s2 = (nul ** 2).sum(0)
    mu = s1 / Bn
    sd = np.sqrt(np.maximum((s2 - Bn * mu ** 2) / (Bn - 1), 1e-30))
    mu_l = (s1[None, :] - nul) / (Bn - 1)
    var_l = (s2[None, :] - nul ** 2 - (Bn - 1) * mu_l ** 2) / (Bn - 2)
    zl = (nul - mu_l) / np.sqrt(np.maximum(var_l, 1e-30))
    return mu, sd, zl


def _moments(z):
    z = np.asarray(z, float)
    m = z.mean(); v = z.var()
    if v <= 0:
        return m, 0.0, 0.0
    sk = ((z - m) ** 3).mean() / v ** 1.5
    ku = ((z - m) ** 4).mean() / v ** 2 - 3
    return m, sk, ku


def bond_stats(obs, nul, alpha_graph=None):
    """obs (P,), nul (B, P). Empirical p-values from the pooled leave-one-out null; significant bonds at one-sided
    p < 1/P (expected ~1 false bond per tail); BH q=0.1; distribution-shape statistics against their null."""
    P = obs.size
    mu, sd, zl = loo_z(nul)
    z = (obs - mu) / sd
    pool = np.sort(zl.ravel())
    M = pool.size
    ge = M - np.searchsorted(pool, z, side="left")
    le = np.searchsorted(pool, z, side="right")
    p_pos = (1 + ge) / (1 + M)
    p_neg = (1 + le) / (1 + M)
    a = (1.0 / P) if alpha_graph is None else alpha_graph
    sig_pos = p_pos < a
    sig_neg = p_neg < a
    zthr_pos = float(pool[min(M - 1, int(np.ceil((1 - a) * M)))])
    zthr_neg = float(pool[max(0, int(np.floor(a * M)) - 1)])
    p2 = np.minimum(1.0, 2 * np.minimum(p_pos, p_neg))
    o = np.argsort(p2)
    bh = np.zeros(P, bool)
    passed = np.flatnonzero(p2[o] <= 0.1 * np.arange(1, P + 1) / P)
    if passed.size:
        bh[o[: passed.max() + 1]] = True
    pi0 = min(1.0, (p2 > 0.5).sum() / (0.5 * P))
    m, sk, ku = _moments(z)
    nm = np.array([_moments(r) for r in zl])
    # internal calibration: false positive bonds per surrogate (its own LOO z against the pooled null)
    fp = (zl > zthr_pos).sum(1)
    return {"z": z, "dJ": obs - mu, "mu": mu, "sd": sd, "p_pos": p_pos, "p_neg": p_neg, "sig_pos": sig_pos,
            "sig_neg": sig_neg, "bh": bh, "zthr_pos": zthr_pos, "zthr_neg": zthr_neg,
            "n_pos": int(sig_pos.sum()), "n_neg": int(sig_neg.sum()), "n_bh": int(bh.sum()),
            "n_bh_pos": int((bh & (z > 0)).sum()),
            "pi1": 1 - pi0, "mean_z": m, "skew_z": sk, "kurt_z": ku,
            "p_mean": float((nm[:, 0] >= m).mean()), "p_skew": float((nm[:, 1] >= sk).mean()),
            "p_kurt": float((nm[:, 2] >= ku).mean()), "q95_skew": float(np.quantile(nm[:, 1], 0.95)),
            "null_fp_mean": float(fp.mean()), "null_fp_any": float((fp > 0).mean()),
            "frac05_pos": float((p_pos < 0.05).mean())}


def graph_stats(sig_pos, iu, N, rng, n_cm: int = 200):
    """Percolation statistics of the significant positive-bond graph."""
    A = np.zeros((N, N), bool)
    A[iu[0][sig_pos], iu[1][sig_pos]] = True
    A = A | A.T
    k = A.sum(1)
    mk = k.mean()
    kappa = float((k ** 2).mean() / mk) if mk > 0 else 0.0
    nc, lab = connected_components(csr_matrix(A), directed=False)
    sizes = np.bincount(lab)
    S1 = sizes.max() / N
    clusters = sorted([int(s) for s in sizes if s >= 2], reverse=True)
    # configuration model with the same degree sequence (stub matching, erased)
    cm = []
    stubs0 = np.repeat(np.arange(N), k)
    for _ in range(n_cm if stubs0.size >= 2 else 0):
        stubs = rng.permutation(stubs0)
        if stubs.size % 2:
            stubs = stubs[:-1]
        a, b = stubs[0::2], stubs[1::2]
        ok = a != b
        G = np.zeros((N, N), bool)
        G[a[ok], b[ok]] = True
        G = G | G.T
        _, lb = connected_components(csr_matrix(G), directed=False)
        cm.append(np.bincount(lb).max() / N)
    S1_cm = float(np.mean(cm)) if cm else 1.0 / N
    return {"mean_k": float(mk), "kappa": kappa, "S1": float(S1), "S1_cm": S1_cm, "clusters": clusters,
            "n_edges": int(A.sum() // 2), "small_clusters_frac": (float(np.mean([c <= 3 for c in clusters]))
                                                                   if clusters else np.nan)}


def concentration(dA, dB, frac: float = 0.10):
    """Cross-validated share of the excess covariance carried by the top `frac` of pairs (ranked on one half,
    measured on the other). dA, dB: (P,) excess covariances on even / odd blocks."""
    P = dA.size
    k = max(1, int(np.ceil(frac * P)))
    out = []
    num = den = 0.0
    for r, m in ((dA, dB), (dB, dA)):
        tot = m.sum()
        top = np.argsort(-r)[:k]
        out.append(m[top].sum() / tot if tot > 0 else np.nan)
        num += m[top].sum(); den += tot
    # Amendment 1 (2026-10-04): pooled ratio over the two directions (stable when one half's total excess is ~0)
    pooled = float(num / den) if den > 0 else np.nan
    return float(np.nanmean(out)) if np.isfinite(out).any() else np.nan, out, pooled


# ------------------------------------------------------------------------------------------- full unit pipeline
def run_dataset(S, R, sched, day, minute, Tk=None, n_surr=200, seed=SEED, variants=("scaffold", "edge", "raw"),
                talk_min=30, n_boot=0, boot_variant="scaffold", graph_cm=200, keep_null=False):
    """Observed fits, joint block-shift surrogates (same shift for spins, reasons, talk spins), bond statistics,
    graph statistics, concentration; optional day-block bootstrap of the primary variant."""
    rng = np.random.default_rng(seed)
    N = S.shape[1]
    iu = triu(N)
    talk_cols = None
    if Tk is not None:
        talk_cols = (Tk > 0).sum(0) >= talk_min
    segs = segments(day, minute)
    obs = {v: analyze_variant(S, R, sched, day, minute, v, Tk, talk_cols) for v in variants}
    nul = {v: [] for v in variants}
    for _ in range(n_surr):
        arrs = [S, R] + ([Tk] if Tk is not None else [])
        sh = joint_shift(arrs, segs, rng)
        Sx, Rx = sh[0], sh[1]
        Tx = sh[2] if Tk is not None else None
        for v in variants:
            nul[v].append(analyze_variant(Sx, Rx, sched, day, minute, v, Tx, talk_cols))
    res = {"N": N, "T": int(S.shape[0]), "n_pairs": int(iu[0].size), "variants": {}}
    for v in variants:
        o = obs[v]
        bs = bond_stats(o["Js"][iu], np.array([u["Js"][iu] for u in nul[v]]))
        gs = graph_stats(bs["sig_pos"], iu, N, rng, graph_cm)
        VR, g = vr_g(o["C"])
        gn = np.array([vr_g(u["C"])[1] for u in nul[v]])
        cA = o["CA"][iu] - np.mean([u["CA"][iu] for u in nul[v]], 0)
        cB = o["CB"][iu] - np.mean([u["CB"][iu] for u in nul[v]], 0)
        cfull = o["C"][iu] - np.mean([u["C"][iu] for u in nul[v]], 0)
        cv10_orig, cv_parts, cv10 = concentration(cA, cB)
        tot = cfull.sum()
        ent = {"bonds": bs, "graph": gs, "g": float(g), "VR": float(VR), "E": float(g - np.nanmean(gn)),
               "z_g": float((g - np.nanmean(gn)) / np.nanstd(gn)) if np.nanstd(gn) > 0 else np.nan,
               "rho_bar_ex": float((VR - np.nanmean([vr_g(u["C"])[0] for u in nul[v]])) / max(N - 1, 1)),
               "cv_c10": cv10, "cv_c10_orig": cv10_orig, "cv_c10_parts": cv_parts, "dC": cfull,
               "dC_tot": float(tot), "dC_half_tot": [float(cA.sum()), float(cB.sum())],
               "share_sig": float(cfull[bs["sig_pos"]].sum() / tot) if tot > 0 else np.nan,
               "c10_insample": float(np.sort(cfull)[::-1][: max(1, int(np.ceil(0.1 * cfull.size)))].sum() / tot)
               if tot > 0 else np.nan, "iters": o["iters"]}
        if keep_null:
            ent["null_Js"] = np.array([u["Js"][iu] for u in nul[v]], dtype=np.float32)
        if "Js_t" in o:
            ntc = int(talk_cols.sum())
            iut = triu(ntc)
            bst = bond_stats(o["Js_t"][iut], np.array([u["Js_t"][iut] for u in nul[v]]))
            gst = graph_stats(bst["sig_pos"], iut, ntc, rng, graph_cm)
            VRt, gt = vr_g(o["C_t"])
            gnt = np.array([vr_g(u["C_t"])[1] for u in nul[v]])
            ent["talk"] = {"N": ntc, "bonds": bst, "graph": gst, "g": float(gt), "E": float(gt - np.nanmean(gnt)),
                           "z_g": float((gt - np.nanmean(gnt)) / np.nanstd(gnt)) if np.nanstd(gnt) > 0 else np.nan}
        res["variants"][v] = ent
    res["talk_cols"] = talk_cols
    if n_boot:
        res["boot"] = bootstrap(S, R, sched, day, minute, res["variants"][boot_variant]["bonds"], iu, N,
                                boot_variant, n_boot, rng)
    return res


def boot_blocks(day, minute):
    """Bootstrap resampling blocks: whole days if >= 4 days, else half-days (split at each day's median minute)."""
    days = np.unique(day)
    if days.size >= 4:
        return [np.flatnonzero(day == d) for d in days], "day"
    out = []
    for d in days:
        idx = np.flatnonzero(day == d)
        mid = np.median(minute[idx])
        out += [idx[minute[idx] <= mid], idx[minute[idx] > mid]]
    return [b for b in out if b.size], "half-day"


def bootstrap(S, R, sched, day, minute, bs, iu, N, variant, n_boot, rng):
    blocks, kind = boot_blocks(day, minute)
    nb = len(blocks)
    keys = []
    Jz = []; stats = []
    for _ in range(n_boot):
        pick = rng.integers(0, nb, size=nb)
        idx = np.concatenate([blocks[p] for p in pick])
        # new day labels so duplicated blocks stay separate blocks
        newday = np.concatenate([np.full(blocks[p].size, k) for k, p in enumerate(pick)])
        S2, av, bid, _, _ = prep(S[idx], R[idx], sched[idx], newday, minute[idx], variant)
        _, Js, _ = fit_pl(S2, av, bid)
        z = (Js[iu] - bs["mu"]) / bs["sd"]
        sig = z > bs["zthr_pos"]
        gs = graph_stats(sig, iu, N, rng, n_cm=0)
        Jz.append(z.astype(np.float32))
        stats.append([sig.sum(), gs["mean_k"], gs["kappa"], gs["S1"], z.mean()])
        keys.append(pick)
    st = np.array(stats, float)
    q = lambda a: [float(np.nanquantile(a, 0.025)), float(np.nanquantile(a, 0.975))]
    Jz = np.array(Jz)
    return {"kind": kind, "n_blocks": nb, "n_boot": n_boot, "n_pos_ci": q(st[:, 0]), "mean_k_ci": q(st[:, 1]),
            "kappa_ci": q(st[:, 2]), "S1_ci": q(st[:, 3]), "mean_z_ci": q(st[:, 4]),
            "frac_kappa_ge2": float((st[:, 2] >= 2).mean()), "z_lo": np.quantile(Jz, 0.025, axis=0),
            "z_hi": np.quantile(Jz, 0.975, axis=0), "stab": (Jz > bs["zthr_pos"]).mean(0)}
