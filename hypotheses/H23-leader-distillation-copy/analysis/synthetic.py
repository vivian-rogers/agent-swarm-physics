"""H23 synthetic validation (axis F): can the observables detect copy / transformation at the village's sample sizes?

All data here are synthetic; nothing is read from the village. Sample sizes and coder accuracy are the real ones:
    leader n = 16 (#44) and 70 (#45); same-window controls 45 (#44) and ~600 (#45); corpus 31 recovered rows;
    plan coder agreement 0.60 (10 acts) / 0.68 (3 coarse classes) on blind validation.

A. Plan level, corpus -> leader channel (soft, situation-matched), 10 acts and 3 coarse classes.
   Leader y | corpus x: copy y = x with prob alpha; transform y = pi(x) (fixed derangement) with prob beta;
   else y ~ q (a follower-like profile). Situations: 10 buckets with bucket-specific corpus profiles; the leader's
   situations are concentrated (3 of 10 buckets, as expected live). Corpus profile per bucket estimated from 31 rows.
   Coder noise: each true act is kept with prob = accuracy, else replaced uniformly.
B. Conversational channel (context act -> response act), same mixture, n = 16 / 45 / 70.
C. Lexical marker-rate test (leader vs controls), beta-binomial per-message rates.
D. Embedding d-statistic, 32-d vectors: shared topic + speaker field + isotropic noise; leader field
   h_L = h_K + lam (h_C - h_K).
E. Estimator bias: pure copy / pure permutation channels, plug-in vs null-corrected.

Output: data/processed/H23-leader-distillation-copy/synthetic.json and figures/synthetic_validation.pdf
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h23lib as L  # noqa: E402

OUT = L.OUT
FIG = Path(__file__).resolve().parents[1] / "figures"
RNG = np.random.default_rng(20261003)
N_SIM = 200
N_NULL = 300


def noisy(codes: np.ndarray, k: int, acc: float, rng) -> np.ndarray:
    flip = rng.random(len(codes)) > acc
    out = codes.copy()
    out[flip] = rng.integers(0, k, flip.sum())
    return out


def bucket_profiles(k: int, rng, n_b: int = 10, conc: float = 0.6) -> np.ndarray:
    """Corpus p(x | bucket): each bucket has a dominant act among the first min(k, 4) ('directive') acts."""
    P = np.full((n_b, k), (1 - conc) / (k - 1))
    for b in range(n_b):
        P[b, b % min(k, 4)] = conc
    return P / P.sum(1, keepdims=True)


def follower_q(k: int) -> np.ndarray:
    q = np.ones(k)
    if k == 10:
        q[[5, 6, 7]] = 4.0   # REQUEST / REPORT / ACK heavy
    else:
        q = np.array([1.0, 3.0, 2.0])
    return q / q.sum()


def sim_corpus_leader(k, alpha, beta, n_l, acc, rng, n_c=31, n_live_buckets=3):
    Pb = bucket_profiles(k, rng)
    # corpus rows (31) spread over 10 buckets, coded with noise; empirical p_C(x|b) used for pairing
    cb = rng.integers(0, 10, n_c)
    cx = np.array([rng.choice(k, p=Pb[b]) for b in cb])
    cx_obs = noisy(cx, k, acc, rng)
    pc_hat = np.zeros((10, k))
    for b, x in zip(cb, cx_obs):
        pc_hat[b, x] += 1
    pc_hat = (pc_hat + 0.5 / k) / (pc_hat + 0.5 / k).sum(1, keepdims=True)
    live_b = rng.choice(10, n_live_buckets, replace=False)
    sb = rng.choice(live_b, n_l)
    perm = np.roll(np.arange(k), 1)
    q = follower_q(k)
    y = np.empty(n_l, int)
    for m in range(n_l):
        x = rng.choice(k, p=Pb[sb[m]])
        u = rng.random()
        y[m] = x if u < alpha else (perm[x] if u < alpha + beta else rng.choice(k, p=q))
    y_obs = noisy(y, k, acc, rng)
    return L.soft_channel_test(pc_hat[sb], y_obs, k, n_null=N_NULL, seed=int(rng.integers(1e9)))


def sim_conversation(k, alpha, beta, n, acc, rng):
    q = follower_q(k)
    x = rng.choice(k, p=q, size=n)
    perm = np.roll(np.arange(k), 1)
    u = rng.random(n)
    y = np.where(u < alpha, x, np.where(u < alpha + beta, perm[x], rng.choice(k, p=q, size=n)))
    return L.sample_channel_test(list(noisy(x, k, acc, rng)), list(noisy(y, k, acc, rng)), n_null=N_NULL,
                                 seed=int(rng.integers(1e9)))


def summarize(rs, keys=("c_ex", "I_copy_ex", "I_transform_ex")):
    out = {}
    for kk in keys:
        v = np.array([r[kk] for r in rs], float)
        out[kk] = [float(np.nanmean(v)), float(np.nanpercentile(v, 5)), float(np.nanpercentile(v, 95))]
    for kk in ("c_p", "I_copy_p", "I_transform_p"):
        v = np.array([r[kk] for r in rs], float)
        out["power_" + kk.replace("_p", "")] = float(np.mean(v < 0.10))
    return out


def part_a():
    res = []
    for k, acc in [(10, 0.60), (3, 0.68), (10, 1.0)]:
        for n_l in (16, 70):
            for alpha, beta in [(0, 0), (0.3, 0), (0.6, 0), (0, 0.3), (0, 0.6), (0.3, 0.3)]:
                rs = [sim_corpus_leader(k, alpha, beta, n_l, acc, RNG) for _ in range(N_SIM)]
                res.append({"k": k, "acc": acc, "n": n_l, "alpha": alpha, "beta": beta, **summarize(rs)})
                print("A", res[-1]["k"], acc, n_l, alpha, beta, {x: round(res[-1][x], 2) for x in res[-1]
                                                                 if x.startswith("power")}, flush=True)
    return res


def part_b():
    res = []
    for k, acc in [(10, 0.60), (3, 0.68)]:
        for n in (16, 45, 70):
            for alpha, beta in [(0, 0), (0.3, 0), (0.6, 0), (0, 0.3), (0, 0.6)]:
                rs = [sim_conversation(k, alpha, beta, n, acc, RNG) for _ in range(N_SIM)]
                res.append({"k": k, "acc": acc, "n": n, "alpha": alpha, "beta": beta, **summarize(rs)})
                print("B", k, acc, n, alpha, beta, {x: round(res[-1][x], 2) for x in res[-1]
                                                    if x.startswith("power")}, flush=True)
    return res


def part_c():
    """Per-message marker rate: tokens ~ NB(mean 55), per-message p ~ Beta(mean p, conc 15); test leader > controls."""
    res = []
    for n_l, n_c in [(16, 45), (70, 600)]:
        for p0 in (0.02, 0.05):
            for rel in (1.0, 1.25, 1.5, 2.0, 3.0):
                pw = []
                for _ in range(N_SIM):
                    def rates(n, p):
                        tok = RNG.negative_binomial(4, 4 / (4 + 55), n) + 5
                        pm = RNG.beta(p * 15, (1 - p) * 15, n)
                        return 100 * RNG.binomial(tok, pm) / tok
                    a, b = rates(n_l, p0 * rel), rates(n_c, p0)
                    pw.append(L.perm_mean_diff(a, b, n=1000, seed=int(RNG.integers(1e9)))["p"] < 0.10)
                res.append({"n_l": n_l, "n_c": n_c, "p0": p0, "ratio": rel, "power": float(np.mean(pw))})
                print("C", res[-1], flush=True)
    return res


def part_d():
    """d = cos(z, C) - cos(z, K). Fields have norm f in units of the per-coordinate noise sd (whitened: sd 1)."""
    res = []
    dim = 32
    for n_l, n_c in [(16, 45), (70, 600)]:
        for f in (1.0, 2.0):
            for lam in (0.0, 0.25, 0.5, 1.0):
                pw = []
                for _ in range(N_SIM):
                    hK = RNG.normal(size=dim)
                    hC = 0.5 * hK + RNG.normal(size=dim)        # corpus partly shares the base direction
                    hK, hC = f * hK / np.linalg.norm(hK), f * hC / np.linalg.norm(hC)
                    topic = 1.5 * RNG.normal(size=dim)
                    others = [f * v / np.linalg.norm(v) for v in RNG.normal(size=(4, dim))]
                    zc_ref, zk_ref = hC + RNG.normal(size=dim) / np.sqrt(31), hK + RNG.normal(size=dim) / np.sqrt(150)
                    hL = hK + lam * (hC - hK)
                    zl = topic + hL + RNG.normal(size=(n_l, dim))
                    zo = np.vstack([topic + others[i % 4] + RNG.normal(size=dim) for i in range(n_c)])
                    d = lambda Z: L.cos_rows(Z, zc_ref) - L.cos_rows(Z, zk_ref)
                    pw.append(L.perm_mean_diff(d(zl), d(zo), n=1000, seed=int(RNG.integers(1e9)))["p"] < 0.10)
                res.append({"n_l": n_l, "n_c": n_c, "field_norm": f, "lam": lam, "power": float(np.mean(pw))})
                print("D", res[-1], flush=True)
    return res


def part_e():
    res = []
    for k in (10, 3):
        for n in (16, 70, 1000):
            for kind in ("copy", "perm", "indep"):
                vals = []
                for _ in range(100):
                    x = RNG.integers(0, k, n)
                    y = x if kind == "copy" else (np.roll(np.arange(k), 1)[x] if kind == "perm" else RNG.integers(0, k, n))
                    r = L.sample_channel_test(list(x), list(y), n_null=200, seed=int(RNG.integers(1e9)))
                    vals.append([r["I"], r["I_copy"], r["I_transform"], r["I_copy_ex"], r["I_transform_ex"]])
                v = np.array(vals).mean(0)
                res.append({"k": k, "n": n, "kind": kind, "true_I": float(np.log2(k)) if kind != "indep" else 0.0,
                            "I": v[0], "I_copy": v[1], "I_transform": v[2], "I_copy_ex": v[3], "I_transform_ex": v[4]})
                print("E", {a: (round(b, 3) if isinstance(b, float) else b) for a, b in res[-1].items()}, flush=True)
    return res


def figure(S):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, 2, figsize=(10, 7.5))
    # A: power for copy and transform, corpus->leader channel
    a = ax[0, 0]
    for (k, acc), mk in [((10, 0.6), "o"), ((3, 0.68), "s"), ((10, 1.0), "^")]:
        for n, ls in [(16, "--"), (70, "-")]:
            rows = [r for r in S["A"] if r["k"] == k and r["acc"] == acc and r["n"] == n and r["beta"] == 0]
            a.plot([r["alpha"] for r in rows], [r["power_c"] for r in rows], ls, marker=mk, color="C0",
                   alpha=0.9 if n == 70 else 0.5)
            rows = [r for r in S["A"] if r["k"] == k and r["acc"] == acc and r["n"] == n and r["alpha"] == 0]
            a.plot([r["beta"] for r in rows], [r["power_I_transform"] for r in rows], ls, marker=mk, color="C3",
                   alpha=0.9 if n == 70 else 0.5)
    a.axhline(0.1, color="gray", lw=0.8)
    a.set(xlabel="copy prob. α (blue: excess c) / transform prob. β (red: I_transform)", ylabel="power (p < 0.10)",
          title="A. corpus → leader plan channel\n(○ 10 acts, coder 0.6; □ 3 classes, 0.68; △ 10 acts, perfect; -- n=16, — n=70)",
          ylim=(0, 1))
    b = ax[0, 1]
    for (k, acc), mk in [((10, 0.6), "o"), ((3, 0.68), "s")]:
        for n, ls in [(16, "--"), (45, ":"), (70, "-")]:
            rows = [r for r in S["B"] if r["k"] == k and r["n"] == n and r["beta"] == 0]
            b.plot([r["alpha"] for r in rows], [r["power_c"] for r in rows], ls, marker=mk, color="C0")
            rows = [r for r in S["B"] if r["k"] == k and r["n"] == n and r["alpha"] == 0]
            b.plot([r["beta"] for r in rows], [r["power_I_transform"] for r in rows], ls, marker=mk, color="C3")
    b.axhline(0.1, color="gray", lw=0.8)
    b.set(xlabel="α (blue: excess c) / β (red: I_transform)", ylabel="power", ylim=(0, 1),
          title="B. conversational channel (context → response)\n(-- n=16, ··· 45, — 70)")
    c = ax[1, 0]
    for (nl, nc), ls in [((16, 45), "--"), ((70, 600), "-")]:
        for p0, col in [(0.02, "C2"), (0.05, "C4")]:
            rows = [r for r in S["C"] if r["n_l"] == nl and r["p0"] == p0]
            c.plot([r["ratio"] for r in rows], [r["power"] for r in rows], ls, marker="o", color=col,
                   label=f"n={nl} vs {nc}, base rate {p0}")
    c.axhline(0.1, color="gray", lw=0.8)
    c.set(xlabel="leader / control marker-rate ratio", ylabel="power", ylim=(0, 1), title="C. corpus-marker rate test")
    c.legend(fontsize=7)
    d = ax[1, 1]
    for (nl, nc), ls in [((16, 45), "--"), ((70, 600), "-")]:
        for f, col in [(1.0, "C1"), (2.0, "C5")]:
            rows = [r for r in S["D"] if r["n_l"] == nl and r["field_norm"] == f]
            d.plot([r["lam"] for r in rows], [r["power"] for r in rows], ls, marker="o", color=col,
                   label=f"n={nl} vs {nc}, field norm {f}")
    d.axhline(0.1, color="gray", lw=0.8)
    d.set(xlabel="λ: leader field moved toward the corpus", ylabel="power", ylim=(0, 1),
          title="D. embedding d = cos(z, C̄) − cos(z, K̄)")
    d.legend(fontsize=7)
    fig.suptitle("H23 synthetic validation at village sample sizes (200 simulations per point)", fontsize=11)
    fig.tight_layout()
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / "synthetic_validation.pdf")


def main():
    assert L.self_test()
    S = {"A": part_a(), "B": part_b(), "C": part_c(), "D": part_d(), "E": part_e(),
         "settings": {"n_sim": N_SIM, "n_null": N_NULL, "seed": 20261003}}
    (OUT / "synthetic.json").write_text(json.dumps(S, indent=1))
    figure(S)


if __name__ == "__main__":
    main()
