"""Tests for infra/shared/copy_info.py: analytic cases, null behavior, and equivalence with H07's h07lib (skipped when
absent). Run: uv run python infra/shared/tests/test_copy_info.py   (or: uv run --with pytest pytest infra/shared/tests)
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import copy_info as CI  # noqa: E402

ROOT = HERE.parents[2]
H07_LIB = ROOT / "hypotheses/H07-rpg-forks/analysis/h07lib.py"


class Skip(Exception):
    pass


def test_pure_copy_is_all_copy_information():
    m = 8
    x = np.repeat(np.arange(m), 50)
    c, kappa, I, Ic = CI.mi_parts(x, x.copy())
    assert c == 1.0 and abs(kappa - 1) < 1e-12
    assert abs(I - np.log2(m)) < 1e-12 and abs(Ic - np.log2(m)) < 1e-12   # I_transform = 0


def test_pure_relabeling_is_all_transformation():
    m = 8
    x = np.repeat(np.arange(m), 50)
    y = (x + 1) % m                                                      # a bijection with no fixed points
    c, kappa, I, Ic = CI.mi_parts(x, y)
    assert c == 0.0 and Ic == 0.0 and abs(I - np.log2(m)) < 1e-12


def test_independent_samples_near_zero_and_null_matches():
    rng = np.random.default_rng(0)
    xv = rng.integers(0, 5, 4000).tolist(); yv = rng.integers(0, 5, 4000).tolist()
    d = CI.decompose(xv, yv, n_null=50, seed=1)
    assert d["I"] < 0.01 and d["I_copy"] < 0.01
    assert abs(d["I_ex"]) < 0.005 and abs(d["I_transform_ex"]) < 0.005
    assert d["I_transform"] >= -1e-12


def test_transform_test_detects_systematic_mapping():
    rng = np.random.default_rng(3)
    KA = {f"k{i}": int(rng.integers(0, 10)) for i in range(400)}
    # systematic: every changed key maps v -> (v + 3) % 10; half the keys copied
    KY = {k: (v if i % 2 else (v + 3) % 10) for i, (k, v) in enumerate(KA.items())}
    sysm = CI.transform_test(KA, KY, n_null=100, seed=1)
    # random changes: changed keys get arbitrary new values
    KR = {k: (v if i % 2 else int(rng.integers(0, 10))) for i, (k, v) in enumerate(KA.items())}
    rand = CI.transform_test(KA, KR, n_null=100, seed=1)
    assert sysm["z"] > 10 and sysm["repeated_mapping_frac"] > 0.9
    assert abs(rand["z"]) < 4


def test_vertical_horizontal_and_sets():
    KA = {"a": 1, "b": 2, "c": 3}
    KY = {"a": 1, "b": 5, "d": 7}
    v = CI.vertical(KA, KY)
    assert v["n"] == 3 and abs(v["c"] - 1 / 3) < 1e-12
    h = CI.horizontal(KA, KY)
    assert h["n"] == 4
    s = CI.set_stats({1, 2, 3}, {2, 3, 4, 5})
    assert s["survival"] == 2 / 3 and s["innovations"] == 2 and s["lost"] == 1 and s["jaccard"] == 2 / 5


def test_equivalent_to_h07lib():
    if not H07_LIB.exists():
        raise Skip("h07lib not present")
    spec = importlib.util.spec_from_file_location("h07lib_ro", H07_LIB)
    L = importlib.util.module_from_spec(spec)
    sys.modules["h07lib_ro"] = L
    spec.loader.exec_module(L)
    rng = np.random.default_rng(9)
    for _ in range(5):
        n = int(rng.integers(50, 400))
        xv = rng.integers(0, 12, n).tolist()
        yv = [x if rng.random() < 0.5 else int(rng.integers(0, 12)) for x in xv]
        a, b = CI.decompose(xv, yv, n_null=20, seed=2), L.decompose(xv, yv, n_null=20, seed=2)
        assert a.keys() == b.keys() and all(a[k] == b[k] or (np.isnan(a[k]) and np.isnan(b[k])) for k in a)
        KA = {i: x for i, x in enumerate(xv)}; KY = {i: y for i, y in enumerate(yv) if i % 7}
        a, b = CI.transform_test(KA, KY, n_null=30, seed=4), L.transform_test(KA, KY, n_null=30, seed=4)
        assert a == b
        assert CI.vertical(KA, KY) == L.vertical(KA, KY)


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
