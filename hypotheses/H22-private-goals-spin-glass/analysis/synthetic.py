"""H22 synthetic validation (faithfulness axis F). No project data is read.

Generative model for content vector spins at village sampling (card O0-O6):
  latent L_{i,d,w} = a_st H_i + a_day g_d + a_drv c_i f_{d,w} + a_ds u_{i,d} + a_fl Z_{i,d,w}     (per-dim variances = shares)
  Z: per day and per embedding dim, AR(1) over windows (phi) with stationary correlation Sigma = corr(I + K)
  statements: s = unit(L + eps), eps ~ N(0, I/psi); k ~ Poisson(lambda_i) statements per agent-window; a window is
  observed if k >= 2; v_{i,w} = mean of its statements; agent-day states = mean (and odd/even halves) of the day's.
Coupling regimes K (entry RMS s): para (0); sk (Gaussian, kappa_true = 0); sk_j0 (Gaussian + uniform, kappa_true
0.5); ferro (Gaussian + uniform, kappa_true 3); mattis (two balanced factions, heterogeneous magnitudes); sk_drive
(sk with a 5x larger exogenous common window drive). Exogenous drive share 0.02 elsewhere. Day-state models u: none, rf (iid daily), glass (P collective patterns,
Markov switching), drift (each agent its own independent Markov over its own patterns).

E1 frustration / SK placement per unit configuration; E2 treatment-test power; E3 overlap statistics (W, M);
E4 talk spins (dichotomized Gaussian, 3% talk rate).

Usage: uv run python hypotheses/H22-private-goals-spin-glass/analysis/synthetic.py [--quick]
Writes data/processed/H22-private-goals-spin-glass/synthetic/results.json and figures/synthetic_validation.pdf.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")

import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h22lib as L  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data/processed/H22-private-goals-spin-glass/synthetic"
FIG = Path(__file__).resolve().parents[1] / "figures"

# unit configurations: (N eligible agents, days, windows per day) from the sampling design (card, Observables)
UNITS = {"51b": (24, 19, 16), "51c": (23, 14, 16), "51d": (20, 7, 16), "38a": (11, 8, 8), "40": (13, 5, 8),
         "44": (16, 4, 8), "tail": (30, 10, 16)}
SHARES = {"static": 0.30, "day": 0.15, "drive": 0.02, "ds": 0.0, "fl": 0.53}
PSI = 0.5
LAMBDA = 2.6
PHI = 0.5


KAPPA = {"sk": 0.0, "sk_drive": 0.0, "sk_j0": 0.5, "ferro": 3.0}


def coupling_matrix(rng, N, regime, s):
    """Entry RMS s. sk / sk_j0 / ferro: Gaussian couplings plus a uniform part with SK ratio kappa_true = sqrt(N) mean / sd."""
    g = rng.standard_normal((N, N)); g = np.triu(g, 1); g = g + g.T
    if regime == "para" or s == 0:
        return np.zeros((N, N))
    if regime in KAPPA:
        kap = KAPPA[regime]
        sig = s / np.sqrt(1 + kap ** 2 / N)
        K = sig * g + (kap * sig / np.sqrt(N)) * (np.ones((N, N)) - np.eye(N))
        np.fill_diagonal(K, 0)
        return K
    elif regime == "ferro_het":
        K = np.abs(g)
    elif regime == "ferro_uniform":
        K = np.ones((N, N))
    elif regime == "mattis":
        xi = np.where(rng.random(N) < 0.5, -1.0, 1.0)
        K = np.outer(xi, xi) * np.abs(g)
    else:
        raise ValueError(regime)
    np.fill_diagonal(K, 0)
    rms = np.sqrt(np.mean(L.triu_vals(K) ** 2))
    return K * (s / rms)


def true_tau3(K):
    return float(np.trace(K @ K @ K) / np.trace(K @ K) ** 1.5) if np.any(K) else np.nan


def corr_from_K(K):
    S = np.eye(len(K)) + K
    w = np.linalg.eigvalsh(S).min()
    if w < 0.05:
        S = S + (0.05 - w) * np.eye(len(K))
    d = np.sqrt(np.diag(S))
    return S / np.outer(d, d)


def day_states(rng, model, N, D, n, P=3, stay=0.75):
    if model == "none":
        return np.zeros((D, N, n))
    if model == "rf":
        return rng.standard_normal((D, N, n))
    if model == "glass":
        pats = rng.standard_normal((P, N, n))
        mu = [rng.integers(P)]
        for _ in range(D - 1):
            mu.append(mu[-1] if rng.random() < stay else rng.choice([p for p in range(P) if p != mu[-1]]))
        return pats[np.array(mu)] + 0.3 * rng.standard_normal((D, N, n))
    if model == "drift":
        pats = rng.standard_normal((N, P, n))
        out = np.zeros((D, N, n))
        for i in range(N):
            m = rng.integers(P)
            for d in range(D):
                if d and rng.random() >= stay:
                    m = rng.choice([p for p in range(P) if p != m])
                out[d, i] = pats[i, m]
        return out + 0.3 * rng.standard_normal((D, N, n))
    raise ValueError(model)


def simulate(rng, N, D, W, K, n=32, shares=SHARES, psi=PSI, lam=LAMBDA, phi=PHI, ds_model="none", absent=0.08):
    sh = dict(shares)
    if ds_model != "none" and sh["ds"] == 0:
        sh["ds"] = 0.25
    tot = sum(sh.values())
    a = {k: np.sqrt(v / tot) for k, v in sh.items()}
    H = rng.standard_normal((N, n))
    c = rng.uniform(0.5, 1.5, N)
    U = day_states(rng, ds_model, N, D, n)
    Lc = np.linalg.cholesky(corr_from_K(K))
    lam_i = rng.gamma(4.0, lam / 4.0, N)
    present = rng.random((D, N)) > absent
    X = np.zeros((D, N, W, n)); O = np.zeros((D, N, W), bool)
    Hf = np.zeros((D, N, n)); H1 = np.zeros((D, N, n)); H2 = np.zeros((D, N, n)); P = np.zeros((D, N), bool)
    sig = 1 / np.sqrt(psi)
    for d in range(D):
        g = rng.standard_normal(n)
        Z = np.zeros((W, N, n))
        z = Lc @ rng.standard_normal((N, n))
        for w in range(W):
            z = phi * z + np.sqrt(1 - phi ** 2) * (Lc @ rng.standard_normal((N, n))) if w else z
            Z[w] = z
        f = rng.standard_normal((W, n))
        k = rng.poisson(lam_i[None, :], size=(W, N)) * present[d][None, :]
        lat = (a["static"] * H[None] + a["day"] * g[None, None] + a["drive"] * c[None, :, None] * f[:, None, :]
               + a["ds"] * U[d][None] + a["fl"] * Z)  # [W, N, n]
        # statements
        tot_k = k.sum()
        if tot_k == 0:
            continue
        ww, ii = np.nonzero(k)
        reps = k[ww, ii]
        rw = np.repeat(ww, reps); ri = np.repeat(ii, reps)
        st = lat[rw, ri] + sig * rng.standard_normal((len(rw), n))
        st /= np.linalg.norm(st, axis=1, keepdims=True)
        # window means
        acc = np.zeros((W, N, n)); np.add.at(acc, (rw, ri), st)
        m = k >= 2
        X[d] = np.where(m.T[..., None], (acc / np.maximum(k, 1)[..., None]).transpose(1, 0, 2), 0)
        O[d] = m.T
        # agent-day states and halves (statements in window order)
        order = np.lexsort((rw, ri))
        ri_o, st_o = ri[order], st[order]
        for i in np.unique(ri_o):
            s_i = st_o[ri_o == i]
            if len(s_i) >= 3:  # halves: earlier vs later statements of the day (time split, Amendment 1)
                h = len(s_i) // 2
                Hf[d, i] = s_i.mean(0); H1[d, i] = s_i[:h].mean(0); H2[d, i] = s_i[h:].mean(0); P[d, i] = True
    return X, O, Hf, H1, H2, P


# ----------------------------------------------------------------------------- experiments


def run_e1(args):
    unit, regime, s, seed, drive = args
    rng = np.random.default_rng(seed)
    N, D, W = UNITS[unit]
    K = coupling_matrix(rng, N, regime, s)
    sh = dict(SHARES)
    if regime == "sk_drive":  # exogenous common drive at 5x the default share
        sh["fl"] -= 0.08; sh["drive"] = 0.10
    X, O, *_ = simulate(rng, N, D, W, K, shares=sh)
    if D < 7:  # short units: day-thirds as pseudo-days (Amendment 1)
        X, O = L.to_pseudo_days(X, O, 3)
    st = L.ContentStats(X, O)
    m = L.unit_moments(st, X.shape[0], nboot=0, nnull=40, rng=rng)
    out = {"unit": unit, "regime": regime, "s": s, "drive": drive, "true_tau3": true_tau3(K), "N": m.get("N")}
    for k in ("S2", "kappa", "tau3", "tau3_dc", "rho_split", "Jbar", "sigma", "p_S2", "p_sigma2", "p_rho"):
        out[k] = m.get(k)
    out["true_tau3_dc"] = true_tau3(L.double_center(K)) if np.any(K) else np.nan
    out["true_kappa"] = float(np.sqrt(N) * np.mean(L.triu_vals(K)) / np.std(L.triu_vals(K))) if np.any(K) else np.nan
    if m.get("N", 0) >= 4 and "J_full" in m:
        fb = L.frustration_block(m, rng, nperm=300, gs=False)
        out.update({"F": fb["shuffle"]["F"], "F_null": fb["shuffle"]["F_null_mean"], "p_F_low": fb["shuffle"]["p_F_low"],
                    "Fw": fb["shuffle"]["Fw"], "Fw_null": fb["shuffle"]["Fw_null_mean"], "p_Fw_low": fb["shuffle"]["p_Fw_low"],
                    "p_neg": fb["shuffle"]["p_neg"], "F_rel": fb.get("reliable", {}).get("F"),
                    "F_rel_rand": fb.get("reliable", {}).get("F_rand")})
    return out


def roles_synthetic(N):
    """#51-like role structure: 7 two-agent roles (SR), the rest singletons; codes 0 = U, 1 = SR."""
    r = np.empty(N, int)
    r[:14] = np.repeat(np.arange(7), 2)
    r[14:] = np.arange(7, 7 + N - 14)
    R = r.max() + 1
    lookup = np.zeros((R, R), np.int8)
    for a in range(R):
        lookup[a, a] = 1
    return r, lookup


def run_e2(args):
    delta, sign, seed = args
    rng = np.random.default_rng(seed)
    N, D, W = UNITS["51b"]
    K = coupling_matrix(rng, N, "sk", 0.05)
    r, lookup = roles_synthetic(N)
    perm = rng.permutation(N)
    r = r[perm]
    for a in range(7):
        i, j = np.flatnonzero(r == a)
        K[i, j] = K[j, i] = sign * delta
    X, O, *_ = simulate(rng, N, D, W, K)
    st = L.ContentStats(X, O)
    J = np.nan_to_num(st.J(np.ones(D, bool)))
    t = L.treatment_test(J, r, lookup, {"SR": 1}, labs=None, nperm=400, rng=rng)["raw"]["SR"]
    # noise SD of J per pair (from split halves)
    JA, JB = st.J(L.folds(D, 2)[0]), st.J(L.folds(D, 2)[1])
    nsd = float(np.nanstd(L.triu_vals(JA - JB)) / 2)
    return {"delta": delta, "sign": sign, "T": t["T"], "p_less": t["p_less"], "p_greater": t["p_greater"], "pair_noise_sd": nsd}


def run_e3(args):
    unit, model, seed = args
    rng = np.random.default_rng(seed)
    N, D, W = UNITS[unit]
    X, O, Hf, H1, H2, P = simulate(rng, N, D, W, np.zeros((N, N)), ds_model=model)
    keepA = P.sum(0) >= D / 2
    h1, h2, hf = L.day_field_remove(Hf[:, keepA], H1[:, keepA], H2[:, keepA], P[:, keepA])
    o = L.overlap_stats(h1, h2, P[:, keepA], nshift=200, rng=rng)
    return {"unit": unit, "model": model, "W": o["W"], "p_W": o["p_W"], "M": o["M"], "q_inf": o["q_inf"], "q_self": o["q_self"]}


def run_e4(args):
    regime, s, seed = args
    rng = np.random.default_rng(seed)
    N, D, _ = UNITS["51b"]
    T, rate, phi = 480, 0.03, 0.9
    K = coupling_matrix(rng, N, regime, s)
    Lc = np.linalg.cholesky(corr_from_K(K))
    thr = np.quantile(rng.standard_normal(200000), 1 - rate)
    days = []
    for d in range(D):
        z = Lc @ rng.standard_normal(N)
        Zs = np.zeros((T, N))
        for t in range(T):
            z = phi * z + np.sqrt(1 - phi ** 2) * (Lc @ rng.standard_normal(N)) if t else z
            Zs[t] = z
        days.append(np.where(Zs > thr, 1.0, -1.0))
    S = np.stack(days)  # [D, T, N]
    ok = (S > 0).sum(1) >= 4  # [D, N]
    Zc = S - S.mean(1, keepdims=True)
    sd = Zc.std(1)
    c = np.einsum("dti,dtj->dij", Zc, Zc) / T
    c = c / (sd[:, :, None] * sd[:, None, :] + 1e-12)
    valid = ok[:, :, None] & ok[:, None, :]
    c[~valid] = np.nan
    cs = np.einsum("dti,etj->deij", Zc, Zc) / T / (sd[:, None, :, None] * sd[None, :, None, :] + 1e-12)
    vs = ok[:, None, :, None] & ok[None, :, None, :]
    cs[~vs] = np.nan
    for d in range(D):
        cs[d, d] = np.nan
    st = L.TalkStats(c, cs)
    m = L.unit_moments(st, D, nboot=0, nnull=40, rng=rng)
    out = {"regime": regime, "s": s, "true_tau3": true_tau3(K), "N": m.get("N")}
    for k in ("S2", "kappa", "tau3", "rho_split", "p_S2", "p_rho"):
        out[k] = m.get(k)
    return out


def summarize(rows, keys, stats):
    from collections import defaultdict
    g = defaultdict(list)
    for r in rows:
        g[tuple(r[k] for k in keys)].append(r)
    out = []
    for k, rs in sorted(g.items(), key=lambda x: str(x[0])):
        d = dict(zip(keys, k)); d["n"] = len(rs)
        for name, fn in stats.items():
            try:
                d[name] = fn(rs)
            except Exception:
                d[name] = None
        out.append(d)
    return out


def med(key):
    return lambda rs: float(np.nanmedian([r[key] if r.get(key) is not None else np.nan for r in rs]))


def q(key, p):
    return lambda rs: float(np.nanquantile([r[key] if r.get(key) is not None else np.nan for r in rs], p))


def frac(fn):
    return lambda rs: float(np.mean([bool(fn(r)) for r in rs]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    reps1 = 12 if a.quick else 50
    reps2 = 20 if a.quick else 100
    reps3 = 20 if a.quick else 100
    reps4 = 8 if a.quick else 30
    t0 = time.time()
    seed = 20261004
    jobs1 = []
    for unit in UNITS:
        for regime in ("para", "sk", "sk_j0", "ferro", "mattis", "sk_drive"):
            for s in ((0.0,) if regime == "para" else (0.03, 0.06, 0.09)):
                for r in range(reps1):
                    seed += 1; jobs1.append((unit, regime, s, seed, True))
    jobs2 = []
    for delta in (0.0, 0.1, 0.2, 0.3):
        for sign in (-1, 1):
            if delta == 0 and sign == 1:
                continue
            for r in range(reps2):
                seed += 1; jobs2.append((delta, sign, seed))
    jobs3 = []
    for unit in ("51b", "51c", "51d", "38a", "tail"):
        for model in ("rf", "glass", "drift"):
            for r in range(reps3):
                seed += 1; jobs3.append((unit, model, seed))
    jobs4 = []
    for regime in ("para", "ferro", "mattis", "sk"):
        for s in ((0.0,) if regime == "para" else (0.05, 0.1)):
            for r in range(reps4):
                seed += 1; jobs4.append((regime, s, seed))
    with Pool(a.workers) as pool:
        e1 = pool.map(run_e1, jobs1, chunksize=4); print(f"E1 {len(e1)} done {time.time() - t0:.0f}s", flush=True)
        e2 = pool.map(run_e2, jobs2, chunksize=4); print(f"E2 {len(e2)} done {time.time() - t0:.0f}s", flush=True)
        e3 = pool.map(run_e3, jobs3, chunksize=4); print(f"E3 {len(e3)} done {time.time() - t0:.0f}s", flush=True)
        e4 = pool.map(run_e4, jobs4, chunksize=2); print(f"E4 {len(e4)} done {time.time() - t0:.0f}s", flush=True)

    sig = lambda r: r.get("p_S2") is not None and r["p_S2"] < 0.05
    het = lambda r: r.get("p_rho") is not None and r["p_rho"] < 0.05
    fin = lambda r, k: r.get(k) is not None and np.isfinite(r[k])
    glass = lambda r: het(r) and fin(r, "kappa") and r["kappa"] < 1 and fin(r, "tau3") and r["tau3"] < 0.25
    s1 = summarize(e1, ["unit", "regime", "s"], {
        "true_tau3": med("true_tau3"), "true_tau3_dc": med("true_tau3_dc"), "true_kappa": med("true_kappa"), "N": med("N"),
        "power_S2": frac(sig), "power_rho": frac(het), "tau3_med": med("tau3"), "tau3_q10": q("tau3", 0.1), "tau3_q90": q("tau3", 0.9),
        "tau3_dc_med": med("tau3_dc"), "tau3_dc_q10": q("tau3_dc", 0.1), "tau3_dc_q90": q("tau3_dc", 0.9),
        "kappa_med": med("kappa"), "kappa_q10": q("kappa", 0.1), "kappa_q90": q("kappa", 0.9), "rho_med": med("rho_split"),
        "glass_call": frac(glass),
        "balanced_call": frac(lambda r: het(r) and fin(r, "tau3") and r["tau3"] >= 0.25),
        "kappa_lt1": frac(lambda r: het(r) and fin(r, "kappa") and r["kappa"] < 1),
        "F_med": med("F"), "F_null_med": med("F_null"), "p_F_low_lt05": frac(lambda r: r.get("p_F_low") is not None and r["p_F_low"] < 0.05),
        "Fw_med": med("Fw"), "Fw_null_med": med("Fw_null"), "p_Fw_low_lt05": frac(lambda r: r.get("p_Fw_low") is not None and r["p_Fw_low"] < 0.05),
        "F_rel_med": med("F_rel"), "F_rel_rand_med": med("F_rel_rand"), "S2_med": med("S2")})
    s2 = summarize(e2, ["delta", "sign"], {
        "power_less": frac(lambda r: r["p_less"] is not None and r["p_less"] < 0.05),
        "power_greater": frac(lambda r: r["p_greater"] is not None and r["p_greater"] < 0.05),
        "T_med": med("T"), "pair_noise_sd": med("pair_noise_sd")})
    s3 = summarize(e3, ["unit", "model"], {
        "W_med": med("W"), "power_W": frac(lambda r: r["p_W"] is not None and r["p_W"] < 0.05),
        "M_med": med("M"), "M_gt02": frac(lambda r: r["M"] is not None and r["M"] > 0.2),
        "both": frac(lambda r: r["p_W"] is not None and r["p_W"] < 0.05 and r["M"] is not None and r["M"] > 0.2),
        "q_inf_med": med("q_inf"), "q_self_med": med("q_self")})
    s4 = summarize(e4, ["regime", "s"], {"true_tau3": med("true_tau3"), "power_S2": frac(sig), "power_rho": frac(het), "tau3_med": med("tau3"),
                                         "tau3_q10": q("tau3", 0.1), "tau3_q90": q("tau3", 0.9), "rho_med": med("rho_split")})
    res = {"params": {"units": UNITS, "shares": SHARES, "psi": PSI, "lambda": LAMBDA, "phi": PHI, "reps": [reps1, reps2, reps3, reps4],
                      "glass_rule": "p_rho < 0.05 and kappa < 1 and tau3 < 0.25"},
           "E1": s1, "E2": s2, "E3": s3, "E4": s4, "runtime_s": time.time() - t0}
    tag = "_quick" if a.quick else ""
    (OUT / f"results{tag}.json").write_text(json.dumps(res, indent=1, default=float))
    (OUT / f"raw{tag}.json").write_text(json.dumps({"E1": e1, "E2": e2, "E3": e3, "E4": e4}, default=float))
    print(f"done {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
