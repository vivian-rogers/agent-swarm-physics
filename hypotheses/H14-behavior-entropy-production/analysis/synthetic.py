"""H14 synthetic validation (axis F): known-EP Markov chains and kinetic Potts at village sequence lengths.

S1  q = 6 chains, reversible base + a driven 6-cycle; turn-like (low self-transition) and minute-like (sticky)
    chains; 500-50,000 transitions in 5 or 20 days; stationary or cold daily starts.
    -> bias and recovery of plugin, chi2, Newton (H05), cfx (cross-fitted exact dual), ML (H05, subset)
S1n DB-surrogate test: size at Sigma = 0 (cold starts included) and power at small Sigma.
S2  family heterogeneity: 12 agents in families of 6/4/2 that differ in sequence length and stickiness only
    (size), or also in EP (power); permutation eta^2 on raw plugin vs. DB-excess estimates.
S3  kinetic Potts, N = 15, q = 6, 5 days x 240 bins: independent agents; + shared daily field; + asymmetric
    chat -> work couplings. Sigma_1, Delta_MF, Delta_PW (Newton) vs. cross-day surrogates; within-day circular
    shift shown for contrast; exact joint EP and long-run single-agent marginal EP as ground truth.

Usage: uv run python hypotheses/H14-behavior-entropy-production/analysis/synthetic.py [--quick] [--parts S1,S1n,S2,S3]
Writes data/processed/H14-behavior-entropy-production/synthetic/*.json and figures/synthetic_validation.pdf.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h14lib as L  # noqa: E402  (sets thread env vars before numpy)

import numpy as np  # noqa: E402

ROOT = HERE.parents[2]
OUT = ROOT / "data/processed/H14-behavior-entropy-production/synthetic"
FIG = HERE.parent / "figures"
QUICK = "--quick" in sys.argv
PARTS = sys.argv[sys.argv.index("--parts") + 1].split(",") if "--parts" in sys.argv else ["S1", "S1n", "S2", "S3"]
RNG = np.random.default_rng(20261003)
Q = 6


# ============================================================================ chains with known EP
def make_chain(rng, f, sticky, q=Q):
    """Reversible base W (symmetric lognormal weights) with self-weight `sticky` x mean off-diagonal weight,
    then a drive f around the cycle 0 -> 1 -> ... -> q-1 -> 0 (forward x e^{f/2}, backward x e^{-f/2})."""
    W = np.exp(rng.normal(0, 0.7, (q, q)))
    W = (W + W.T) / 2
    np.fill_diagonal(W, 0)
    np.fill_diagonal(W, sticky * W.sum() / (q * (q - 1)))
    for a in range(q):
        b = (a + 1) % q
        W[a, b] *= np.exp(f / 2)
        W[b, a] *= np.exp(-f / 2)
    P = W / W.sum(1, keepdims=True)
    return P


def stationary(P):
    w, v = np.linalg.eig(P.T)
    pi = np.real(v[:, np.argmin(np.abs(w - 1))])
    return pi / pi.sum()


def exact_ep(P):
    pi = stationary(P)
    q = len(P)
    return float(sum(pi[a] * P[a, b] * np.log(pi[a] * P[a, b] / (pi[b] * P[b, a]))
                     for a in range(q) for b in range(q) if a != b and P[a, b] > 0))


def sample(P, n, days, rng, cold=False):
    L_ = n // days
    pi = stationary(P)
    starts = [Q - 1] * days if cold else list(rng.choice(len(P), size=days, p=pi))
    X, dl = L.simulate_days(P, starts, [L_] * days, 1, rng)
    return X[0], dl


def estimators(x, dl, q=Q, with_ml=False):
    p, n_, d = L.transitions(x, dl)
    out = {"plugin": L.ep_plugin(p, n_, q), "chi2": L.ep_chi2(p, n_, q), "newton": L.ep_newton(p, n_, d, q),
           "cfx": L.ep_cfx(p, n_, d, q)}
    out["tur"] = L.ep_tur(out["newton"])
    if with_ml:
        out["ml"] = L.ep_ml(p, n_, d, q)
    return out


def s1(rng):
    fs = [0.0, 0.3, 0.6, 1.0, 1.5, 2.2, 3.0, 4.5]
    ns = [500, 2000, 10000, 50000] if not QUICK else [2000]
    reps = 6 if QUICK else 20
    recs = []
    for sticky_name, sticky in (("turn", 1.0), ("minute", 12.0)):
        for f in fs:
            for days in (5, 20):
                for n in ns:
                    if n // days < 20:
                        continue
                    for r in range(reps):
                        P = make_chain(rng, f, sticky)
                        sig = exact_ep(P)
                        x, dl = sample(P, n, days, rng, cold=False)
                        e = estimators(x, dl, with_ml=(n <= 10000 and r < 3))
                        if n <= 10000:
                            nl = L.db_null(x, dl, Q, 20, rng, stats=("newton", "cfx", "plugin"))
                            e["cfx_bc"] = e["cfx"] - float(np.nanmean(nl["cfx"]))
                            e["newton_bc"] = e["newton"] - float(np.nanmean(nl["newton"]))
                            e["plugin_bc"] = e["plugin"] - float(np.nanmean(nl["plugin"]))
                        recs.append({"sticky": sticky_name, "f": f, "days": days, "n": n, "true": sig, **e})
        print("S1", sticky_name, "done", flush=True)
    return recs


def s1_null(rng):
    """DB-surrogate test at Sigma = 0 (size) and small Sigma (power)."""
    R = 40 if QUICK else 100
    reps0 = 20 if QUICK else 150
    reps1 = 10 if QUICK else 60
    out = []
    cells = [(n, days, sticky_name, sticky, cold) for n in (2000, 10000) for days in (5,)
             for sticky_name, sticky in (("turn", 1.0), ("minute", 12.0)) for cold in (True, False)]
    if QUICK:
        cells = cells[:2]
    for n, days, sname, sticky, cold in cells:
        for f, reps in ((0.0, reps0), (0.6, reps1), (1.0, reps1), (1.5, reps1)):
            if f > 0 and not cold:
                continue
            for r in range(reps):
                P = make_chain(rng, f, sticky)
                sig = exact_ep(P)
                x, dl = sample(P, n, days, rng, cold=cold)
                p, n_, d = L.transitions(x, dl)
                obs = {"newton": L.ep_newton(p, n_, d, Q), "cfx": L.ep_cfx(p, n_, d, Q), "plugin": L.ep_plugin(p, n_, Q)}
                nl = L.db_null(x, dl, Q, R, rng, stats=("newton", "cfx", "plugin"))
                rec = {"n": n, "days": days, "sticky": sname, "cold": cold, "f": f, "true": sig}
                for k in obs:
                    rec[f"{k}"] = obs[k]
                    rec[f"{k}_p"] = float((1 + (nl[k] >= obs[k]).sum()) / (R + 1))
                    rec[f"{k}_null_mean"] = float(np.nanmean(nl[k]))
                out.append(rec)
            print("S1n", n, sname, "cold" if cold else "stat", f, flush=True)
    return out


def s2(rng):
    """Family test size/power with heterogeneous lengths and stickiness."""
    fam = np.array(["A"] * 6 + ["B"] * 4 + ["C"] * 2)
    n_of = {"A": 10000, "B": 2500, "C": 1000}
    sticky_of = {"A": 1.0, "B": 4.0, "C": 12.0}
    reps = 20 if QUICK else 100
    R = 30
    nperm = 999
    out = []
    for scen, ratio in (("size", 1.0), ("power_x2", 2.0), ("power_x3", 3.0)):
        for r in range(reps):
            vals = {"plugin": [], "cfx": [], "cfx_excess": [], "newton_excess": [], "true": []}
            for g in fam:
                f = rng.lognormal(np.log(1.0), 0.3) * (np.sqrt(ratio) if g == "B" else 1.0)
                P = make_chain(rng, f, sticky_of[g])
                x, dl = sample(P, n_of[g], 5, rng)
                p, n_, d = L.transitions(x, dl)
                c = L.ep_cfx(p, n_, d, Q)
                nw = L.ep_newton(p, n_, d, Q)
                nl = L.db_null(x, dl, Q, R, rng, stats=("newton", "cfx"))
                vals["plugin"].append(L.ep_plugin(p, n_, Q))
                vals["cfx"].append(c)
                vals["cfx_excess"].append(c - np.nanmean(nl["cfx"]))
                vals["newton_excess"].append(nw - np.nanmean(nl["newton"]))
                vals["true"].append(exact_ep(P))
            rec = {"scenario": scen, "rep": r}
            for k, v in vals.items():
                e, p_, _ = L.perm_eta2(np.array(v), fam, nperm, rng)
                rec[f"{k}_eta2"] = e
                rec[f"{k}_p"] = p_
            out.append(rec)
        print("S2", scen, "done", flush=True)
    return out


# ============================================================================ kinetic Potts
WORK, CHAT = [0, 1, 2], 3


def potts_params(rng, N, q, coupling, field):
    """Heterogeneous agents: own fields, persistence, and a self-kernel that drives work -> chat -> idle -> work
    (a single-agent cycle); optional chat -> work / chat -> chat cross couplings with random directed strengths."""
    H0 = rng.normal(0, 0.5, (N, q))
    K = np.zeros((N, q, q))
    for i in range(N):
        K[i] += np.eye(q) * rng.uniform(1.5, 2.5)          # persistence
        drive = rng.uniform(0.3, 0.9)
        for cur, nxt in ((0, 3), (1, 3), (2, 3), (3, 4), (4, 0)):   # work -> chat -> idle -> work
            K[i, nxt, cur] += drive                                  # K[i, next, current]
    J = np.zeros((N, N, q, q))
    if coupling > 0:
        A = rng.random((N, N)) < 0.3                          # directed: j -> i
        np.fill_diagonal(A, False)
        S = A * rng.uniform(0.5, 1.5, (N, N)) * coupling
        for w in WORK:
            J[:, :, w, CHAT] = S                              # j chatting at t -> i works at t+1
        J[:, :, CHAT, CHAT] = 0.5 * S.T                       # replies, other direction
    h_t = None
    if field:
        L_ = 240
        tt = np.arange(L_) / L_
        h_t = np.zeros((L_, q))
        h_t[:, CHAT] = 1.2 * np.exp(-((tt - 0.1) / 0.08) ** 2) + 0.8 * np.exp(-((tt - 0.9) / 0.08) ** 2)
        h_t[:, 4] = 1.0 * tt
    return H0, K, J, h_t


def potts_truth(H0, K, J, rng, n_long):
    X, d = L.simulate_potts(H0, K, J, 1, n_long, rng)
    joint = L.potts_exact_ep(H0, K, J, X, d)
    N = X.shape[1]
    marg = []
    for i in range(N):
        p, n_, _ = L.transitions(X[:, i], d)
        marg.append(L.ep_plugin(p, n_, H0.shape[1]))
    return joint, float(np.sum(marg))


def aligned(X, days, L_):
    nd = len(np.unique(days))
    return X.reshape(nd, L_, -1)


def s3(rng):
    N, q, nd, L_ = 15, Q, 5, 240
    reps = 4 if QUICK else 30
    R = 10 if QUICK else 40
    n_long = 20000 if QUICK else 100000
    out = {"cases": {}}
    for case, coupling, field in (("independent", 0.0, False), ("shared_field", 0.0, True),
                                  ("coupled", 1.0, False), ("coupled_weak", 0.5, False)):
        recs = []
        for r in range(reps):
            H0, K, J, h_t = potts_params(rng, N, q, coupling, field)
            truth = potts_truth(H0, K, J, rng, n_long) if (not field and r < (2 if QUICK else 5)) else (np.nan, np.nan)
            X, days = L.simulate_potts(H0, K, J, nd, L_, rng, h_t=h_t)
            A = aligned(X, days, L_)
            Xp, Xn, d = L.stack_aligned(A)
            obs = L.collective_ep(Xp, Xn, d, q, WORK, CHAT)
            null = {k: [] for k in ("sigma1", "delta_mf", "delta_pw")}
            for _ in range(R):
                Y = L.crossday_surrogate(A, rng)
                ns = L.collective_ep(*L.stack_aligned(Y), q, WORK, CHAT)
                for k in null:
                    null[k].append(ns[k])
            rec = {"rep": r, "true_joint": truth[0], "true_single_marginal_sum": truth[1],
                   "true_collective": truth[0] - truth[1] if np.isfinite(truth[0]) else np.nan, **obs}
            for k in null:
                v = np.array(null[k])
                rec[f"{k}_null_mean"] = float(np.mean(v))
                rec[f"{k}_null_p95"] = float(np.percentile(v, 95))
                rec[f"{k}_p"] = float((1 + (v >= obs[k]).sum()) / (R + 1))
            if case == "shared_field" and r < 3:
                cs = [L.collective_ep(*L.stack_aligned(L.circshift_surrogate(A, rng)), q, WORK, CHAT)["delta_mf"] for _ in range(5)]
                rec["circshift_delta_mf_mean"] = float(np.mean(cs))
                cs1 = [L.collective_ep(*L.stack_aligned(L.circshift_surrogate(A, rng)), q, WORK, CHAT, which=())["sigma1"] for _ in range(5)]
                rec["circshift_sigma1_mean"] = float(np.mean(cs1))
            recs.append(rec)
            print("S3", case, r, {k: round(rec[k], 4) for k in ("sigma1", "delta_mf", "delta_pw", "delta_mf_p", "delta_pw_p", "true_collective") if isinstance(rec.get(k), float)}, flush=True)
        out["cases"][case] = recs
    return out


def chain_with_ep(rng, target, sticky, q=Q):
    """Chain with the make_chain construction whose exact EP equals `target` (bisection on the drive f)."""
    seed = int(rng.integers(1 << 31))
    lo, hi = 0.0, 8.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if exact_ep(make_chain(np.random.default_rng(seed), mid, sticky, q)) < target:
            lo = mid
        else:
            hi = mid
    return make_chain(np.random.default_rng(seed), (lo + hi) / 2, sticky, q)


def s2c(rng):
    """Family test with calibrated EP: every agent's true EP drawn from one lognormal (median 0.03, sd 0.5 in log);
    families differ in n (10k / 2.5k / 1k) and stickiness (1 / 4 / 12). Size = 'size'; power: family B x2, x3."""
    fam = np.array(["A"] * 6 + ["B"] * 4 + ["C"] * 2)
    n_of = {"A": 10000, "B": 2500, "C": 1000}
    sticky_of = {"A": 1.0, "B": 4.0, "C": 12.0}
    reps = 20 if QUICK else 100
    R = 30
    out = []
    for scen, ratio in (("size", 1.0), ("power_x2", 2.0), ("power_x3", 3.0)):
        for r in range(reps):
            vals = {"plugin": [], "cfx": [], "cfx_excess": [], "newton_excess": [], "newton": [], "true": []}
            for g in fam:
                target = float(np.exp(rng.normal(np.log(0.03), 0.5))) * (ratio if g == "B" else 1.0)
                P = chain_with_ep(rng, target, sticky_of[g])
                x, dl = sample(P, n_of[g], 5, rng)
                p, n_, d = L.transitions(x, dl)
                c = L.ep_cfx(p, n_, d, Q)
                nw = L.ep_newton(p, n_, d, Q)
                nl = L.db_null(x, dl, Q, R, rng, stats=("newton", "cfx"))
                vals["plugin"].append(L.ep_plugin(p, n_, Q))
                vals["cfx"].append(c)
                vals["newton"].append(nw)
                vals["cfx_excess"].append(c - np.nanmean(nl["cfx"]))
                vals["newton_excess"].append(nw - np.nanmean(nl["newton"]))
                vals["true"].append(exact_ep(P))
            rec = {"scenario": scen, "rep": r}
            for k, v in vals.items():
                e, p_, _ = L.perm_eta2(np.array(v), fam, 999, rng)
                rec[f"{k}_eta2"] = e
                rec[f"{k}_p"] = p_
            out.append(rec)
        print("S2c", scen, "done", flush=True)
    return out


def s3b(rng):
    """Detection limit of the collective term: weaker couplings (0.1, 0.2), N = 15, q = 6, 5 days x 240."""
    N, q, nd, L_ = 15, Q, 5, 240
    reps = 4 if QUICK else 20
    R = 10 if QUICK else 40
    out = {"cases": {}}
    for case, coupling in (("coupled_0.1", 0.1), ("coupled_0.2", 0.2)):
        recs = []
        for r in range(reps):
            H0, K, J, h_t = potts_params(rng, N, q, coupling, False)
            truth = potts_truth(H0, K, J, rng, 100000) if r < 5 else (np.nan, np.nan)
            X, days = L.simulate_potts(H0, K, J, nd, L_, rng)
            A = aligned(X, days, L_)
            obs = L.collective_ep(*L.stack_aligned(A), q, WORK, CHAT)
            null = {k: [] for k in ("sigma1", "delta_mf", "delta_pw")}
            for _ in range(R):
                ns = L.collective_ep(*L.stack_aligned(L.crossday_surrogate(A, rng)), q, WORK, CHAT)
                for k in null:
                    null[k].append(ns[k])
            rec = {"rep": r, "true_joint": truth[0], "true_single_marginal_sum": truth[1],
                   "true_collective": truth[0] - truth[1] if np.isfinite(truth[0]) else np.nan, **obs}
            for k in null:
                v = np.array(null[k])
                rec[f"{k}_null_mean"] = float(np.mean(v))
                rec[f"{k}_null_p95"] = float(np.percentile(v, 95))
                rec[f"{k}_p"] = float((1 + (v >= obs[k]).sum()) / (R + 1))
            recs.append(rec)
        out["cases"][case] = recs
        print("S3b", case, "done", flush=True)
    return out


# ============================================================================ summaries and figure
def summarize(res):
    S = {}
    if "S1" in res:
        import collections
        g = collections.defaultdict(list)
        for r in res["S1"]:
            g[(r["sticky"], r["days"], r["n"])].append(r)
        tab = []
        for (st, days, n), rs in sorted(g.items()):
            for lo, hi in ((0, 1e-9), (0.003, 0.03), (0.03, 0.1), (0.1, 0.3), (0.3, 3)):
                sel = [r for r in rs if lo <= r["true"] < hi] if hi > 1e-9 else [r for r in rs if r["f"] == 0]
                if not sel:
                    continue
                row = {"sticky": st, "days": days, "n": n, "true_range": [lo, hi], "k": len(sel),
                       "true_median": float(np.median([r["true"] for r in sel]))}
                for e in ("plugin", "chi2", "newton", "cfx", "tur", "ml", "cfx_bc", "newton_bc", "plugin_bc"):
                    v = [r[e] for r in sel if e in r and np.isfinite(r[e])]
                    if not v:
                        continue
                    if hi > 1e-9:
                        rr = [r[e] / r["true"] for r in sel if e in r and np.isfinite(r[e])]
                        row[f"{e}_recovery_median"] = float(np.median(rr))
                    row[f"{e}_mean"] = float(np.mean(v))
                    row[f"{e}_rmse"] = float(np.sqrt(np.mean([(r[e] - r["true"]) ** 2 for r in sel if e in r and np.isfinite(r[e])])))
                tab.append(row)
        S["S1"] = tab
    if "S1n" in res:
        import collections
        g = collections.defaultdict(list)
        for r in res["S1n"]:
            g[(r["n"], r["sticky"], r["cold"], r["f"])].append(r)
        S["S1n"] = [{"n": n, "sticky": st, "cold": c, "f": f, "k": len(rs),
                     "true_median": float(np.median([r["true"] for r in rs])),
                     **{f"{e}_reject": float(np.mean([r[f"{e}_p"] < 0.05 for r in rs])) for e in ("newton", "cfx", "plugin")},
                     **{f"{e}_null_mean": float(np.mean([r[f"{e}_null_mean"] for r in rs])) for e in ("newton", "cfx", "plugin")}}
                    for (n, st, c, f), rs in sorted(g.items())]
    if "S2" in res:
        out = {}
        for scen in ("size", "power_x2", "power_x3"):
            rs = [r for r in res["S2"] if r["scenario"] == scen]
            out[scen] = {k: float(np.mean([r[f"{k}_p"] < 0.05 for r in rs])) for k in ("plugin", "cfx", "cfx_excess", "newton_excess", "true")}
            out[scen]["k"] = len(rs)
        S["S2"] = out
    if "S2c" in res:
        out = {}
        for scen in ("size", "power_x2", "power_x3"):
            rs = [r for r in res["S2c"] if r["scenario"] == scen]
            out[scen] = {k: float(np.mean([r[f"{k}_p"] < 0.05 for r in rs])) for k in ("plugin", "cfx", "cfx_excess", "newton", "newton_excess", "true")}
            out[scen]["k"] = len(rs)
        S["S2c"] = out
    if "S3" in res:
        out = {}
        for case, rs in res["S3"]["cases"].items():
            out[case] = {"k": len(rs)}
            for k in ("sigma1", "delta_mf", "delta_pw"):
                out[case][f"{k}_reject"] = float(np.mean([r[f"{k}_p"] < 0.05 for r in rs]))
                out[case][f"{k}_mean"] = float(np.mean([r[k] for r in rs]))
                out[case][f"{k}_null_mean"] = float(np.mean([r[f"{k}_null_mean"] for r in rs]))
            tc = [r["true_collective"] for r in rs if np.isfinite(r["true_collective"])]
            if tc:
                out[case]["true_collective_mean"] = float(np.mean(tc))
                out[case]["true_joint_mean"] = float(np.mean([r["true_joint"] for r in rs if np.isfinite(r["true_joint"])]))
                out[case]["true_single_marginal_mean"] = float(np.mean([r["true_single_marginal_sum"] for r in rs if np.isfinite(r["true_single_marginal_sum"])]))
            cs = [r["circshift_delta_mf_mean"] for r in rs if "circshift_delta_mf_mean" in r]
            if cs:
                out[case]["circshift_delta_mf_mean"] = float(np.mean(cs))
                out[case]["circshift_sigma1_mean"] = float(np.mean([r["circshift_sigma1_mean"] for r in rs if "circshift_sigma1_mean" in r]))
        S["S3"] = out
    return S


def figure(res, S):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "serif", "font.size": 7, "axes.linewidth": 0.5, "pdf.fonttype": 42})
    fig, axs = plt.subplots(2, 3, figsize=(7.0, 4.4))
    cols = {"plugin": "#999999", "chi2": "#c2662d", "newton": "#3f6fb5", "cfx": "#2a8a4a", "tur": "#8a5ab5"}
    if "S1" in res:
        for ax, st in zip(axs[0, :2], ("turn", "minute")):
            rs = [r for r in res["S1"] if r["sticky"] == st and r["days"] == 5 and r["n"] == 2000]
            t = np.array([r["true"] for r in rs])
            for e in ("plugin", "newton", "cfx"):
                ax.scatter(t + 1e-4, np.array([r[e] for r in rs]) + 1e-4, s=3, color=cols[e], label=e, alpha=0.7)
            ax.plot([1e-4, 3], [1e-4, 3], "k-", lw=0.5)
            ax.set_xscale("log"); ax.set_yscale("symlog", linthresh=1e-3)
            ax.set_xlabel("true Σ (nats/transition)"); ax.set_ylabel("estimate")
            ax.set_title(f"S1 {st}-like chains, n = 2,000, 5 days", fontsize=7)
            ax.legend(frameon=False, fontsize=6)
    if "S1n" in S:
        ax = axs[0, 2]
        rows = [r for r in S["S1n"] if r["cold"]]
        labs = [f"{r['sticky'][0]} n={r['n']//1000}k Σ={r['true_median']:.3f}" for r in rows]
        y = np.arange(len(rows))
        ax.barh(y - 0.2, [r["cfx_reject"] for r in rows], 0.4, color=cols["cfx"], label="cfx")
        ax.barh(y + 0.2, [r["newton_reject"] for r in rows], 0.4, color=cols["newton"], label="newton")
        ax.axvline(0.05, color="k", lw=0.5, ls="--")
        ax.set_yticks(y); ax.set_yticklabels(labs, fontsize=5)
        ax.set_xlabel("rejection rate vs DB surrogate (α = 0.05)"); ax.set_title("S1n size (Σ=0) and power, cold starts", fontsize=7)
        ax.legend(frameon=False, fontsize=6)
    if "S2c" in S:
        ax = axs[1, 0]
        ks = ["plugin", "cfx", "cfx_excess", "newton_excess", "true"]
        x = np.arange(len(ks))
        for i, scen in enumerate(("size", "power_x2", "power_x3")):
            ax.bar(x + (i - 1) * 0.27, [S["S2c"][scen][k] for k in ks], 0.27, label=scen)
        ax.axhline(0.05, color="k", lw=0.5, ls="--")
        ax.set_xticks(x); ax.set_xticklabels(ks, fontsize=6)
        ax.set_ylabel("P(perm p < 0.05)"); ax.set_title("S2c family test: equal true EP, families differ in n, stickiness", fontsize=7)
        ax.legend(frameon=False, fontsize=6)
    if "S3" in S:
        ax = axs[1, 1]
        cases = list(S["S3"])
        x = np.arange(len(cases))
        for i, k in enumerate(("sigma1", "delta_mf", "delta_pw")):
            ax.bar(x + (i - 1) * 0.27, [S["S3"][c][f"{k}_reject"] for c in cases], 0.27, label=k)
        ax.axhline(0.05, color="k", lw=0.5, ls="--")
        ax.set_xticks(x); ax.set_xticklabels(cases, fontsize=6)
        ax.set_ylabel("P(cross-day p < 0.05)"); ax.set_title("S3 kinetic Potts N=15, 5 d x 240", fontsize=7)
        ax.legend(frameon=False, fontsize=6)
        ax = axs[1, 2]
        for c in cases:
            rs = res["S3"]["cases"][c]
            ax.scatter([r["delta_mf"] - r["delta_mf_null_mean"] for r in rs], [r["delta_pw"] - r["delta_pw_null_mean"] for r in rs], s=5, label=c)
        ax.axhline(0, color="k", lw=0.4); ax.axvline(0, color="k", lw=0.4)
        ax.set_xlabel("ΔΣ_MF − null mean"); ax.set_ylabel("ΔΣ_PW − null mean"); ax.set_title("S3 collective excess per run", fontsize=7)
        ax.legend(frameon=False, fontsize=6)
    fig.tight_layout()
    fig.savefig(FIG / "synthetic_validation.pdf")
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    tag = "_quick" if QUICK else ""
    if "--summarize" not in sys.argv:
        for part, fn in (("S1", s1), ("S1n", s1_null), ("S2", s2), ("S3", s3), ("S2c", s2c), ("S3b", s3b)):
            if part in PARTS:
                t0 = time.time()
                r = fn(np.random.default_rng(20261003 + {"S1": 1, "S1n": 2, "S2": 3, "S3": 4, "S2c": 5, "S3b": 6}[part]))
                (OUT / f"raw_{part}{tag}.json").write_text(json.dumps(r, default=float))
                print(part, f"{time.time() - t0:.0f}s", flush=True)
    res = {}
    for part in ("S1", "S1n", "S2", "S3", "S2c", "S3b"):
        f = OUT / f"raw_{part}{tag}.json"
        if f.exists():
            res[part] = json.loads(f.read_text())
    if "S3b" in res:
        res["S3"] = {"cases": {**res.get("S3", {"cases": {}})["cases"], **res["S3b"]["cases"]}}
    S = summarize(res)
    (OUT / f"synthetic_summary{tag}.json").write_text(json.dumps(S, indent=1, default=float))
    figure(res, S)
    print(json.dumps(S, default=float)[:3000])


if __name__ == "__main__":
    main()
