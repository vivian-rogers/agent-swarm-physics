"""Tests for infra/shared/spectra.py.

1. Exact reproduction of H12's synthetic-validation numbers (hypotheses/H12-groupthink-dimensional-collapse/analysis/
   synthetic.py), with H12's generators copied below and H12's seeds:
     C1  flat rank-4 Gaussian spectrum, n = 10, 300 draws: mean bias-corrected PR, naive PR and effective rank
         (needs nothing but numpy; expected values pinned from H12's synthetic/C_pr.parquet);
     A1  activity spins, N 15, D 5, L 240: no mode (k 0) and one planted market mode (k 1, a 0.35), rep 0;
     B1  content overlap: regime I null (k 0) and regime III planted mode (k 1, a 0.45), rep 0.
   A1 and B1 need H12's calibration.json (numbers derived from real data; gitignored): skipped when absent.
2. Equivalence with h12lib on random inputs (skipped when H12's file is absent).
3. Self-contained checks on synthetic data (planted mode found, null not, PR unbiased, near-duplicate shares).

Run: uv run python infra/shared/tests/test_spectra.py      (or: uv run --with pytest pytest infra/shared/tests)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import spectra as S  # noqa: E402

ROOT = HERE.parents[2]
H12_SYN = ROOT / "data/processed/H12-groupthink-dimensional-collapse/synthetic"
H12_LIB = ROOT / "hypotheses/H12-groupthink-dimensional-collapse/analysis/h12lib.py"
D32 = 32

EXPECTED_C1 = {"pr": 4.228592097858312, "pr_naive": 2.7953141012878313, "erank": 3.1813580165454876}
EXPECTED_A1 = {
    (0, 0.0): {"N_eff": 15, "k_cd": 0, "k_rank": 0, "l1": 1.2716245485711324, "edge_cd": 1.3034206951764042, "k_mp": 1,
               "k_mpeff": 0, "tauB": 1.7011936052333265},
    (1, 0.35): {"N_eff": 15, "k_cd": 1, "k_rank": 1, "l1": 2.208617172822578, "edge_cd": 1.4243102251357724, "k_mp": 1,
                "k_mpeff": 1, "tauB": 2.0702214406324644},
}
EXPECTED_B1 = {
    ("I", 10, 0, 0.0): {"N_eff": 10, "k_cd": 0, "k_rank": 0, "l1": 1.1250610741336804, "edge_cd": 1.1901684733587412, "k_mp": 0},
    ("III", 15, 1, 0.45): {"N_eff": 15, "k_cd": 1, "k_rank": 1, "l1": 1.8218887985426253, "edge_cd": 1.3222064697507807, "k_mp": 1},
}


class Skip(Exception):
    pass


# ----------------------------------------------------------------------------- H12's generators (copied, test-only)
def _ar1(rng, shape_lead, T, phi):
    phi = np.broadcast_to(np.asarray(phi, float), shape_lead)
    x = np.empty(shape_lead + (T,))
    x[..., 0] = rng.standard_normal(shape_lead)
    s = np.sqrt(1 - phi ** 2)
    e = rng.standard_normal(shape_lead + (T,))
    for t in range(1, T):
        x[..., t] = phi * x[..., t - 1] + s * e[..., t]
    return x


def _loadings(N, k, rng):
    V = np.zeros((N, k))
    if k >= 1:
        V[:, 0] = 1.0
    if k >= 2:
        V[:, 1] = np.where(rng.permutation(N) < N // 2, 1.0, -1.0)
    if k >= 3:
        V[rng.permutation(N)[: max(3, N // 3)], 2] = 1.0
    return V


def _gen_spins(rng, N, D, Lmin, k, a, cal_r, tau_f=10.0):
    from scipy.stats import norm
    p = rng.choice(cal_r["p"], N); phi = rng.choice(cal_r["phi"], N)
    V = _loadings(N, k, rng)
    load2 = np.minimum((a ** 2) * (V ** 2).sum(1), 0.95)
    prof = np.interp(np.linspace(0, 9, Lmin), np.arange(10), cal_r["profile"])
    days = []
    for _ in range(D):
        eta = _ar1(rng, (N,), Lmin, phi)
        z = np.sqrt(1 - load2)[:, None] * eta
        if k:
            f = _ar1(rng, (k,), Lmin, np.exp(-1 / tau_f))
            z += a * V @ f
        pt = np.clip(p[:, None] * prof[None, :], 0.01, 0.99)
        days.append(np.where(z > norm.ppf(1 - pt), 1, -1).astype(np.int8))
    return days


def _gen_content(rng, N, D, Wd, k, a, cal_c, d=D32, phi_f=0.5, phi_g=0.5):
    V = _loadings(N, k, rng)
    load2 = np.minimum((a ** 2) * (V ** 2).sum(1), 0.95)
    U = np.linalg.qr(rng.standard_normal((d, max(k, 1))))[0][:, :max(k, 1)]
    pres = np.clip(rng.choice(cal_c["pres"], N), 0.02, 1)
    pmf = np.asarray(cal_c["pmf"])
    s_t = np.sqrt(cal_c["s2t"] * d); s_w = np.sqrt(cal_c["s2w"])
    raw, cnts = [], []
    for _ in range(D):
        g = _ar1(rng, (N, d), Wd, phi_g).transpose(0, 2, 1) / np.sqrt(d)
        x = np.sqrt(1 - load2)[:, None, None] * g
        if k:
            f = _ar1(rng, (k,), Wd, phi_f)
            x += a * np.einsum("im,mw,dm->iwd", V, f, U)
        x *= s_t
        n = np.where(rng.random((N, Wd)) < pres[:, None], rng.choice(np.arange(1, 41), (N, Wd), p=pmf), 0)
        noise = rng.standard_normal((N, Wd, d)) * s_w / np.sqrt(np.maximum(n, 1))[:, :, None]
        raw.append(np.where(n[:, :, None] > 0, x + noise, 0.0)); cnts.append(n)
    allx = np.concatenate(raw, 1); alln = np.concatenate(cnts, 1)
    w = alln > 0
    mu = (allx * w[:, :, None]).sum(1) / np.maximum(w.sum(1), 1)[:, None]
    return [np.where(c[:, :, None] > 0, r - mu[:, None, :], 0.0) for r, c in zip(raw, cnts)]


def _cal():
    f = H12_SYN / "calibration.json"
    if not f.exists():
        raise Skip("H12 calibration.json not present")
    return json.loads(f.read_text())


def _close(a, b, tol=1e-12):
    return abs(a - b) <= tol * max(1.0, abs(b))


# ----------------------------------------------------------------------------- 1. reproduce H12's synthetic numbers
def test_reproduce_h12_C1_pr_estimators():
    rng = np.random.default_rng(S.SEED)
    lam = np.r_[np.ones(4), np.full(D32 - 4, 1e-12)]
    est = [S.pr_from_samples(rng.standard_normal((10, D32)) * np.sqrt(lam)) for _ in range(300)]
    for key, want in EXPECTED_C1.items():
        got = float(np.nanmean([e[key] for e in est]))
        assert _close(got, want), (key, got, want)


def test_reproduce_h12_A1_activity_spectrum():
    cal = _cal()["activity"]["III"]
    for (k, a), want in EXPECTED_A1.items():
        cond = {"exp": "A1", "reg": "III", "N": 15, "D": 5, "L": 240, "k": k, "a": a}
        rng = np.random.default_rng([S.SEED, S.stable_seed(cond), 0])
        days = _gen_spins(rng, 15, 5, 240, k, a, cal)
        keep = np.concatenate(days, 1).std(1) > 0
        days = [x[keep] for x in days]
        N = int(keep.sum()); T = sum(x.shape[1] for x in days)
        cd = S.spectrum_test(days, 200, rng, "spin", "crossday")
        tau = S.bartlett_tau(days)
        got = {"N_eff": N, "k_cd": cd["k"], "k_rank": cd["k_rank"], "l1": float(cd["eig"][0]), "edge_cd": cd["edge"],
               "k_mp": int((cd["eig"] > S.mp_edge(N, T)).sum()), "k_mpeff": int((cd["eig"] > S.mp_edge(N, T / tau)).sum()),
               "tauB": tau}
        for key, w in want.items():
            assert _close(got[key], w), (cond, key, got[key], w)


def test_reproduce_h12_B1_content_spectrum():
    cal = _cal()["content"]
    for (reg, N, k, a), want in EXPECTED_B1.items():
        cond = {"exp": "B1", "reg": reg, "N": N, "D": 5, "W": 8, "k": k, "a": a}
        rng = np.random.default_rng([S.SEED, S.stable_seed(cond), 0])
        days = _gen_content(rng, N, 5, 8, k, a, cal[reg])
        X = np.concatenate(days, 1)
        keep = np.abs(X).sum((1, 2)) > 0
        days = [x[keep] for x in days]
        Ne = int(keep.sum()); T = X.shape[1]
        cd = S.spectrum_test(days, 200, rng, "content", "crossday")
        got = {"N_eff": Ne, "k_cd": cd["k"], "k_rank": cd["k_rank"], "l1": float(cd["eig"][0]), "edge_cd": cd["edge"],
               "k_mp": int((cd["eig"] > S.mp_edge(Ne, T * D32)).sum())}
        for key, w in want.items():
            assert _close(got[key], w), (cond, key, got[key], w)


# ----------------------------------------------------------------------------- 2. equivalence with h12lib
def test_equivalent_to_h12lib():
    if not H12_LIB.exists():
        raise Skip("h12lib not present")
    import importlib.util
    spec = importlib.util.spec_from_file_location("h12lib_ro", H12_LIB)
    L = importlib.util.module_from_spec(spec)
    sys.modules["h12lib_ro"] = L
    spec.loader.exec_module(L)
    rng = np.random.default_rng(7)
    days = [np.where(rng.random((9, int(rng.integers(50, 80)))) < 0.4, 1, -1) for _ in range(4)]
    cdays = [rng.standard_normal((7, 6, 5)) * (rng.random((7, 6, 1)) < 0.6) for _ in range(3)]
    for kind, dd in (("spin", days), ("content", cdays)):
        for null in ("crossday", "circ"):
            a = S.spectrum_test(dd, 30, np.random.default_rng(1), kind, null)
            b = L.spectrum_test(dd, 30, np.random.default_rng(1), kind, null)
            assert np.array_equal(a["eig"], b["eig"]) and a["edge"] == b["edge"] and a["k"] == b["k"], (kind, null)
    Y = rng.standard_normal((120, 16)); ag = rng.integers(0, 9, 120)
    for f, args in ((S.pr_rarefied, (Y, ag, 30, 8, 5)), (S.pr_balanced, (Y, ag, 4, 8, 5))):
        a = f(*args, np.random.default_rng(3))
        b = getattr(L, f.__name__)(*args, np.random.default_rng(3))
        assert all((np.isnan(a[k]) and np.isnan(b[k])) or a[k] == b[k] for k in a), f.__name__
    a = S.between_pr(Y, ag, np.random.default_rng(4)); b = L.between_pr(Y, ag, np.random.default_rng(4))
    assert a == b
    assert S.bartlett_tau(days) == L.bartlett_tau(days)


# ----------------------------------------------------------------------------- 3. self-contained checks
def test_planted_mode_detected_and_null_clean():
    rng = np.random.default_rng(11)
    N, D, L = 12, 6, 200
    f = [rng.standard_normal(L) for _ in range(D)]
    signal = [np.sign(0.8 * fd[None, :] + rng.standard_normal((N, L))) for fd in f]
    noise = [np.sign(rng.standard_normal((N, L))) for _ in range(D)]
    assert S.spectrum_test(signal, 100, np.random.default_rng(1), "spin", "crossday")["k"] >= 1
    assert S.spectrum_test(noise, 100, np.random.default_rng(1), "spin", "crossday")["k"] == 0
    w = S.corr_eig(np.concatenate(signal, 1))
    assert w[0] > S.mp_edge(N, D * L) and abs(w.sum() - N) < 1e-9


def test_pr_unbiased_on_flat_gaussian():
    rng = np.random.default_rng(5)
    lam = np.r_[np.ones(8), np.zeros(24)]
    pr = np.mean([S.pr_from_samples(rng.standard_normal((60, 32)) * np.sqrt(lam))["pr"] for _ in range(300)])
    naive = np.mean([S.pr_from_samples(rng.standard_normal((60, 32)) * np.sqrt(lam))["pr_naive"] for _ in range(300)])
    assert abs(pr - 8) < 0.4 and naive < 7.5          # bias-corrected ~ unbiased; naive biased low
    r = S.pr_rarefied(rng.standard_normal((20, 32)), np.zeros(20, int), 30, None, 3, rng)
    assert np.isnan(r["pr"]) and r["n_pool"] == 20


def test_near_dup_share():
    rng = np.random.default_rng(2)
    V = rng.standard_normal((6, 16)); V /= np.linalg.norm(V, axis=1, keepdims=True)
    V = np.vstack([V, V[0], V[1]])                     # rows 6, 7 duplicate rows 0, 1
    agent = np.array([0, 1, 2, 3, 4, 5, 0, 2])          # row 6 same agent as row 0; row 7 a different agent from row 1
    r = S.near_dup_share(V, agent)
    assert r["n"] == 8 and abs(r["dup_share"] - 4 / 8) < 1e-12
    assert abs(r["dup_within"] - 2 / 8) < 1e-12 and abs(r["dup_cross"] - 2 / 8) < 1e-12
    by = S.near_dup_share_by(np.array(["a"] * 8), V, agent, min_n=5)
    assert len(by) == 1 and by[0]["dup_share"] == r["dup_share"]


def _run_all():
    fails, skips = 0, 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn(); print(f"PASS {name}")
            except Skip as e:
                skips += 1; print(f"SKIP {name}: {e}")
            except Exception as e:  # noqa: BLE001
                fails += 1; print(f"FAIL {name}: {e!r}")
    print(f"{fails} failed, {skips} skipped")
    return fails


if __name__ == "__main__":
    sys.exit(1 if _run_all() else 0)
