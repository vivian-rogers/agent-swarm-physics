"""H52 round 2 library (card section "Round 2"): quote-free DiD content candidates and the read vs in-flight
partition contrast. Round-1 code (h52lib.py, estimate.py) is unchanged; this module only adds functions.

Content candidates per (message m, recipient j, receiving call c); S_1..S_k = j's statements in the 2 h before t_call
(S_k most recent), Q1 = first post statement, Qbar = mean of the first <= 5 post statements, u = message direction:
  chi_q1 = (Q1 - S_{k-1}) . unit(u perp S_k)              minus the placebo mean of the same
  chi_qm = (Qbar - Sbar_old) . unit(u perp S_k)            Sbar_old = mean of S_1..S_{k-1} within 60 min
  chi_qa = (Qbar - alpha S_k) . unit(u perp S_1..S_{k-1})  alpha = persistence slope along placebo directions
  chi_dd (A1) is chi_qa with alpha = 1 (recomputed here as a check against round 1).
Partition contrast: C = sum over (period x after-lag x before-age) cells of w (mean read - mean in-flight), w = in-flight
count; message-cluster bootstrap.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h52lib as L  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

R2OUT = L.OUT / "r2"
LAG_BINS = np.array([0, 30, 60, 120, 300, 900], float)
AGE_BINS = np.array([0, 120, 600, np.inf])
MIN_PL = 10


def _unit_rows(X):
    n = np.linalg.norm(X, axis=-1, keepdims=True)
    return X / np.where(n > 1e-9, n, 1.0)


def _perp1(u, s):
    """u: (n, d) or (n, p, d); s: (n, d) unit (zero rows = missing). Returns unit(u perp s) (u itself where s missing)."""
    if u.ndim == 2:
        c = np.einsum("nd,nd->n", u, s)[:, None]
        return _unit_rows(u - c * s)
    c = np.einsum("npd,nd->np", u, s)[..., None]
    return _unit_rows(u - c * s[:, None, :])


def content_rows_r2(V, bidx, pmask, qidx, U, Upl, chunk: int = 20000) -> dict:
    """Per-row pieces of the round-2 candidates. V: statement vectors (unit); bidx (n, K) right-aligned recent
    statements (-1 missing), pmask (n, K) within the 60-min pre window, qidx (n, K_POST) post statements; U (n, d)
    message vectors (NaN if missing); Upl (n, P, d) placebo vectors (NaN rows ignored).
    Returns arrays: q1_t, q1_p (chi_q1 = q1_t - q1_p), qm_t, qm_p, a_t, b_t, a_p, b_p (chi_qa = (a_t - al b_t) -
    (a_p - al b_p)), and the sums for alpha (Sxy, Sxx, Sx, Sy, n) over all rows x placebos."""
    n = len(U)
    keys = ("q1_t", "q1_p", "qm_t", "qm_p", "a_t", "b_t", "a_p", "b_p")
    out = {k: np.full(n, np.nan, np.float32) for k in keys}
    sums = np.zeros(5)
    npost = (qidx >= 0).sum(1)
    for s0 in range(0, n, chunk):
        e0 = min(n, s0 + chunk)
        bi = bidx[s0:e0]
        S = L._gather(V, bi).astype(np.float64)                     # (m, K, d)
        Sk = S[:, -1]
        Sk1 = S[:, -2]
        has_k = bi[:, -1] >= 0
        has_k1 = bi[:, -2] >= 0
        old_mask = pmask[s0:e0, :-1] & (bi[:, :-1] >= 0)
        n_old = old_mask.sum(1)
        Sold = (S[:, :-1] * old_mask[..., None]).sum(1) / np.maximum(n_old, 1)[:, None]
        qi = qidx[s0:e0]
        Q = L._gather(V, qi).astype(np.float64)
        np_ = npost[s0:e0]
        Qbar = Q.sum(1) / np.maximum(np_, 1)[:, None]
        Q1 = Q[:, 0]
        okq = np_ > 0
        u = U[s0:e0].astype(np.float64)
        hasu = np.isfinite(u).all(1)
        u = np.nan_to_num(u)
        up = Upl[s0:e0].astype(np.float64)
        okp = np.isfinite(up).all(2)
        nokp = okp.sum(1)
        up = np.nan_to_num(up)
        plok = nokp >= MIN_PL
        # quote-free direction (last statement removed)
        uq = _perp1(u, Sk)
        upq = _perp1(up, Sk)
        ok1 = hasu & has_k & has_k1 & okq & plok
        d1 = Q1 - Sk1
        out["q1_t"][s0:e0] = np.where(ok1, np.einsum("nd,nd->n", uq, d1), np.nan)
        out["q1_p"][s0:e0] = np.where(ok1, (np.einsum("npd,nd->np", upq, d1) * okp).sum(1) / np.maximum(nokp, 1), np.nan)
        okm = hasu & has_k & (n_old > 0) & okq & plok
        dm = Qbar - Sold
        out["qm_t"][s0:e0] = np.where(okm, np.einsum("nd,nd->n", uq, dm), np.nan)
        out["qm_p"][s0:e0] = np.where(okm, (np.einsum("npd,nd->np", upq, dm) * okp).sum(1) / np.maximum(nokp, 1), np.nan)
        # A1 direction (older statements projected out), pieces for chi_qa / chi_dd
        S2 = S.copy()
        S2[:, -1] = 0.0
        B2 = L.orth_basis_batched(S2)
        uh2, _ = L.perp(u, B2)
        uph2, _ = L.perp(up, B2)
        oka = hasu & has_k & okq & plok
        at = np.einsum("nd,nd->n", uh2, Qbar)
        bt = np.einsum("nd,nd->n", uh2, Sk)
        ap_all = np.einsum("npd,nd->np", uph2, Qbar)
        bp_all = np.einsum("npd,nd->np", uph2, Sk)
        out["a_t"][s0:e0] = np.where(oka, at, np.nan)
        out["b_t"][s0:e0] = np.where(oka, bt, np.nan)
        out["a_p"][s0:e0] = np.where(oka, (ap_all * okp).sum(1) / np.maximum(nokp, 1), np.nan)
        out["b_p"][s0:e0] = np.where(oka, (bp_all * okp).sum(1) / np.maximum(nokp, 1), np.nan)
        w = okp & oka[:, None]
        x, y = bp_all[w], ap_all[w]
        sums += np.array([(x * y).sum(), (x * x).sum(), x.sum(), y.sum(), w.sum()])
    out["alpha_sums"] = sums
    return out


def alpha_from_sums(s) -> float:
    sxy, sxx, sx, sy, n = s
    if n < 10:
        return np.nan
    return float((sxy - sx * sy / n) / (sxx - sx * sx / n))


def candidates(pieces: dict, alpha: float | None = None) -> dict:
    """Candidate statistics from the per-row pieces."""
    al = alpha_from_sums(pieces["alpha_sums"]) if alpha is None else alpha
    p = {k: np.asarray(v, float) for k, v in pieces.items() if k != "alpha_sums"}
    return {"chi_q1": p["q1_t"] - p["q1_p"], "chi_qm": p["qm_t"] - p["qm_p"],
            "chi_qa": (p["a_t"] - al * p["b_t"]) - (p["a_p"] - al * p["b_p"]),
            "chi_dd2": (p["a_t"] - p["b_t"]) - (p["a_p"] - p["b_p"]), "alpha": al}


# ============================================================================ partition contrast
def lag_bin(lag):
    b = np.searchsorted(LAG_BINS, lag, side="right") - 1
    return np.where((lag >= 0) & (lag < LAG_BINS[-1]), b, -1)


def age_bin(age):
    return np.searchsorted(AGE_BINS, age, side="right") - 1


def partition_contrast(P: pl.DataFrame, col: str, n_boot: int = 2000, seed: int = 52, cluster: str = "msg",
                       weights: np.ndarray | None = None) -> dict:
    """C = sum_cells w (mean read - mean in-flight) with cells = period x lag x before-age, w = in-flight pairs in the
    cell; message-cluster bootstrap. Also the read-arm mean over all pairs (A) and the matched read / in-flight means.
    P columns: msg (cluster), period, arm ('read'/'inflight'), lag_s, age_s, col. weights: optional pair weights."""
    P = P.filter(pl.col(col).is_not_null() & pl.col(col).is_not_nan())
    if P.height == 0:
        return {"n_pairs": 0}
    y = P[col].to_numpy().astype(float)
    wpair = np.ones(P.height) if weights is None else np.asarray(weights, float)
    rd = (P["arm"] == "read").to_numpy()
    lb = lag_bin(P["lag_s"].to_numpy().astype(float))
    ab = age_bin(P["age_s"].to_numpy().astype(float))
    per = P["period"].to_numpy()
    plab, pid = np.unique(per, return_inverse=True)
    nA, nL = len(AGE_BINS) - 1, len(LAG_BINS) - 1
    cell = np.where(lb >= 0, (pid * nL + lb) * nA + ab, -1)
    ncell = len(plab) * nL * nA
    clab, cid = np.unique(P[cluster].to_numpy(), return_inverse=True)
    nC = len(clab)
    inb = cell >= 0
    S = np.zeros((2, nC, ncell)); N = np.zeros((2, nC, ncell))
    for arm, m in ((0, rd & inb), (1, ~rd & inb)):
        np.add.at(S[arm], (cid[m], cell[m]), (wpair * y)[m]); np.add.at(N[arm], (cid[m], cell[m]), wpair[m])
    ra_s = np.bincount(cid[rd], (wpair * y)[rd], nC); ra_n = np.bincount(cid[rd], wpair[rd], nC)
    ni_raw = np.zeros((nC, ncell)); np.add.at(ni_raw, (cid[~rd & inb], cell[~rd & inb]), 1.0)

    def stat(w):
        Sr, Nr = w @ S[0], w @ N[0]
        Si, Ni = w @ S[1], w @ N[1]
        Wc = w @ ni_raw
        ok = (Nr > 0) & (Ni > 0)
        A = float((w @ ra_s) / (w @ ra_n)) if (w @ ra_n) > 0 else np.nan
        if not ok.any():
            return A, np.nan, np.nan, np.nan
        xr, xi, wt = Sr[ok] / Nr[ok], Si[ok] / Ni[ok], Wc[ok]
        return A, float(np.average(xr - xi, weights=wt)), float(np.average(xr, weights=wt)), float(np.average(xi, weights=wt))
    obs = stat(np.ones(nC))
    rng = np.random.default_rng(seed)
    bs = np.array([stat(rng.multinomial(nC, np.full(nC, 1 / nC)).astype(float)) for _ in range(n_boot)]) if n_boot else np.zeros((0, 4))

    def ci(j, q=(2.5, 97.5)):
        v = bs[:, j][np.isfinite(bs[:, j])] if len(bs) else np.array([])
        return [float(np.percentile(v, q[0])), float(np.percentile(v, q[1]))] if len(v) > 20 else [np.nan, np.nan]
    okc = (N[0].sum(0) > 0) & (N[1].sum(0) > 0)
    return {"n_pairs": int(P.height), "n_read": int(rd.sum()), "n_inflight": int((~rd).sum()),
            "n_inflight_matched": int(ni_raw.sum(0)[okc].sum()), "n_msgs": int(nC),
            "n_msgs_inflight": int(len(np.unique(cid[~rd]))),
            "A": obs[0], "A_ci": ci(0), "C": obs[1], "C_ci": ci(1), "C_ci90": ci(1, (5, 95)),
            "C_se": float(np.nanstd(bs[:, 1])) if len(bs) else np.nan,
            "read_matched": obs[2], "inflight_matched": obs[3],
            "conv_share": (obs[3] / obs[2]) if np.isfinite(obs[2]) and abs(obs[2]) > 1e-9 else None,
            "_boot_C": bs[:, 1] if len(bs) else None}


def diff_independent(r1: dict, r0: dict) -> dict:
    """Difference of two contrasts from independent message sets (bootstrap draws paired by index)."""
    b1, b0 = r1.get("_boot_C"), r0.get("_boot_C")
    if b1 is None or b0 is None or not np.isfinite(r1.get("C", np.nan)) or not np.isfinite(r0.get("C", np.nan)):
        return {"diff": np.nan, "ci": [np.nan, np.nan]}
    d = b1 - b0
    d = d[np.isfinite(d)]
    return {"diff": float(r1["C"] - r0["C"]), "ci": [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))] if len(d) > 20 else [np.nan, np.nan],
            "se": float(np.std(d)) if len(d) > 20 else np.nan}


def strip_boot(r: dict) -> dict:
    return {k: v for k, v in r.items() if not k.startswith("_")}
