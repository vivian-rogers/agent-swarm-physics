"""Unit tests for hawkes_core: recursions, gradients, simple recovery. Run: uv run python .../analysis/test_core.py"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hawkes_core as hc  # noqa: E402

rng = np.random.default_rng(0)

# 1. recursions vs O(n^2) reference
t = np.sort(rng.random(300) * 1000); g = np.repeat([0, 1, 2], 100).astype(np.int64)
t = np.concatenate([np.sort(t[g == k]) for k in range(3)])
A, B = hc.exp_sums(t, g, 0.01, want_b=True)
Ar, Br = hc.exp_sums_reference(t, g, 0.01)
assert np.allclose(A, Ar) and np.allclose(B, Br), "exp_sums mismatch"
x = np.sort(rng.random(40) * 1100 - 100); gx = np.sort(rng.integers(0, 3, 40)).astype(np.int64)
x = np.concatenate([np.sort(x[gx == k]) for k in range(3)])
X = hc.exo_sums(t, g, x, gx, 0.005)
Xr = np.array([np.sum(np.exp(-0.005 * (t[i] - x[(gx == g[i]) & (x < t[i])]))) for i in range(len(t))])
assert np.allclose(X, Xr), "exo_sums mismatch"
print("recursions ok")

# 2. synthetic days, gradient check for every spec
def synth_daymap(n_days=6, T=4 * 3600.0, mu=0.01, alpha=0.5, beta=1 / 60, n_agents=5):
    dm = {}
    for d in range(n_days):
        base = np.sort(rng.random(rng.poisson(mu * T)) * T)
        allt = [base]; gen = base
        while len(gen):
            k = rng.poisson(alpha, len(gen)); ch = np.repeat(gen, k) + rng.exponential(1 / beta, k.sum())
            gen = ch[ch <= T]; allt.append(gen)
        tt = np.sort(np.concatenate(allt))
        xs = np.sort(rng.random(5) * T - 600)
        dm[d] = hc.Day(t=tt, agent=rng.integers(0, n_agents, len(tt)).astype(np.int64), T=T, first=(d == 0), x=xs,
                       active=np.arange(n_agents))
    return dm

dm = synth_daymap()
for spec in [hc.Spec("B0"), hc.Spec("B1"), hc.Spec("B2"), hc.Spec("B3"), hc.Spec("B2", kernel="grid"),
             hc.Spec("B2", kernel="powerlaw"), hc.Spec("B2a", kernel="selfcross"), hc.Spec("B2", kernel="none")]:
    ds = hc.Dataset(dm, list(dm), spec)
    p = ds.init_params() + rng.normal(0, 0.1, ds.layout()[1])
    ll, gr = ds.loglik(p)
    eps = 1e-6
    idx = rng.choice(len(p), min(12, len(p)), replace=False)
    num = np.array([(ds.loglik(p + eps * np.eye(len(p))[i], grad=False) - ds.loglik(p - eps * np.eye(len(p))[i], grad=False)) / (2 * eps) for i in idx])
    err = np.max(np.abs(num - gr[idx]) / (np.abs(num) + 1e-3))
    assert err < 1e-4, (spec, err, num, gr[idx])
    print(f"gradient ok {spec.baseline}/{spec.kernel}: rel err {err:.1e}")

# 3. recovery (constant baseline, n=0.5, tau=60 s)
dm = synth_daymap(n_days=20, alpha=0.5)
for spec in [hc.Spec("B2"), hc.Spec("B2", kernel="grid")]:
    f = hc.Dataset(dm, list(dm), spec).fit(beta_starts=[1 / 10, 1 / 300, 1 / 3000])
    s = f.summary()
    print(spec.kernel, {k: round(v, 3) for k, v in s.items() if k in ("n", "tau_s", "n_fast300", "ll")})
dm0 = synth_daymap(n_days=20, alpha=0.0)
f = hc.Dataset(dm0, list(dm0), hc.Spec("B2")).fit(beta_starts=[1 / 10, 1 / 300, 1 / 3000])
print("n=0 truth ->", round(f.summary()["n"], 4))
z = f.rescaled_intervals(); print("KS on true-model n=0 fit", hc.ks_exp1(z))
f = hc.Dataset(dm, list(dm), hc.Spec("B2")).fit(beta_starts=[1 / 10, 1 / 300, 1 / 3000])
print("KS on n=.5 fit", hc.ks_exp1(f.rescaled_intervals()))
print("cascade mean size", hc.reconstruct_cascades(f, rng, 2).mean(), "theory 1/(1-n)=", 1 / (1 - f.summary()["n"]))
print("all tests passed")
