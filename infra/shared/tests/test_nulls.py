"""Tests for infra/shared/nulls.py (DQ8): surrogate invariants, placebo helpers, the parametric agent-field null, and
size checks: each calibrated (null, statistic) cell stays within its binomial band in a fast mini-calibration on toy
skeletons, and the documented traps stay anti-conservative (so the size table keeps catching them).

The full calibration (real skeletons, 100 replicates x 49 surrogates) is `uv run python infra/shared/nulls.py
--calibrate`; its table is infra/data-quality/null_sizes.json. These tests use 40 replicates x 19 surrogates.
Run: uv run python infra/shared/tests/test_nulls.py      (or: uv run --with pytest pytest infra/shared/tests)
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("POLARS_MAX_THREADS", "2")

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import nulls as NL  # noqa: E402
import simulate as SIM  # noqa: E402

REPS, SURR = 40, 19
# force toy skeletons for the activity family (fast, no data needed)
NL._SK_CACHE[tuple(NL.CAL_UNITS)] = [SIM.toy_skeleton(N=10, n_days=4, T=240, seed=s) for s in range(4)]


def _rate(family, scen, null, stat, reps=REPS, seed=7):
    fn = NL.FAMILIES[family][0]
    rng = np.random.default_rng(seed)
    ps = []
    for r in range(reps):
        for row in fn((scen, r, SURR, int(rng.integers(1 << 31)))):
            if row["null"] == null and row["statistic"] == stat and np.isfinite(row["p"]):
                ps.append(row["p"])
    ps = np.array(ps)
    return float(np.mean(ps <= NL.ALPHA)), len(ps)


# --------------------------------------------------------------------------------------------- invariants
def test_surrogate_invariants():
    rng = np.random.default_rng(0)
    days = [np.where(rng.random((T, 6)) < 0.4, 1.0, -1.0) for T in (50, 60, 55)]
    mins = [np.arange(len(d)) for d in days]
    cd = NL.crossday(days, rng)
    # each agent's column on day d comes from one of its own days (same multiset when lengths match)
    for d, Y in enumerate(cd):
        assert Y.shape == days[d].shape
    cs = NL.circshift(days, rng)
    for X, Y in zip(days, cs):
        assert np.allclose(np.sort(X, 0), np.sort(Y, 0))           # per-agent per-day values preserved
    bs = NL.block_shift(days, mins, rng, block_min=20)
    for X, Y, m in zip(days, bs, mins):
        for b in np.unique(m // 20):
            sel = m // 20 == b
            assert np.allclose(X[sel].sum(0), Y[sel].sum(0))         # per-agent block sums preserved
    # joint shifting moves extra arrays with the same offsets
    R = [np.arange(d.size).reshape(d.shape) for d in days]
    Y, (R2,) = NL.block_shift(days, mins, np.random.default_rng(1), joint=[R])
    Y0 = NL.block_shift(days, mins, np.random.default_rng(1))
    assert all(np.array_equal(a, b) for a, b in zip(Y, Y0))
    rooms = np.array([[0, 0, 1, 1, 1, 2]] * 5)
    rr = NL.room_relabel(rooms, rng)
    assert all(sorted(np.bincount(r)) == sorted(np.bincount(rooms[0])) for r in rr)


def test_placebo_dates_and_message_placebo():
    dates = []
    d = np.datetime64("2030-01-07")
    while len(dates) < 30:
        if np.is_busday(d):
            dates.append(str(d))
        d = d + np.timedelta64(1, "D")
    pl_ = NL.placebo_dates("2030-01-21", dates, match_weekday=True, gap=3)
    assert pl_ and all(np.datetime64(x).astype("datetime64[D]").item().weekday() == 0 for x in pl_)
    assert "2030-01-21" not in pl_ and "2030-01-07" not in pl_          # gap at both ends
    assert len(NL.placebo_dates("2030-01-21", dates, match_weekday=False, gap=3)) > len(pl_)
    sender = np.array([0, 0, 0, 1, 1])
    day = np.array([0, 1, 1, 0, 1])
    tod = np.array([100.0, 200.0, 9000.0, 50.0, 5000.0])
    plc = NL.crossday_message_placebo(sender, day, tod, np.random.default_rng(0), tol_s=1800)
    assert plc[0] == 1 and plc[1] == 0 and plc[2] == -1 and plc[3] == -1


def test_agent_field_null_recovers_fields():
    rng = np.random.default_rng(3)
    N, n = 12, 3000
    spk = rng.integers(0, N, n)
    tgt = (spk + rng.integers(1, N, n)) % N
    a, b = rng.normal(0, 0.7, N), rng.normal(0, 0.7, N)
    u = rng.logistic(size=n) + a[spk] + b[tgt]
    s = np.where(u < -2.0, -1.0, np.where(u < 1.2, 0.0, 1.0))
    c, ah, bh, ok = NL.fit_ordinal(spk, tgt, (s + 1).astype(int), N)
    assert ok and np.corrcoef(ah, a - a[0])[0, 1] > 0.8 and np.corrcoef(bh, b - b[0])[0, 1] > 0.8
    reps = list(NL.agent_field_null(spk, tgt, s, N, 5, rng))
    assert len(reps) == 5 and all(set(np.unique(x)) <= {-1.0, 0.0, 1.0} for x in reps)


def test_lull_filter_biases_gain_at_small_N():
    """H25's trap: dropping minutes with <= 1 active agent biases the variance-ratio gain at g = 0 for N <= 6."""
    sk = SIM.toy_skeleton(N=5, n_days=6, T=240, p_act=0.3, seed=11)
    graw, glull = [], []
    for s in range(6):
        sim = SIM.simulate(sk, seed=s)
        days = [np.where(ds.act, 1.0, -1.0) for ds in sim.days]
        valid = [ds.span.all(1) for ds in sim.days]
        mins = [d.minutes for d in sk.days]
        graw.append(NL.stat_cw_gain(days, mins, valid=valid))
        lull = [v & ((S > 0).sum(1) >= 2) for v, S in zip(valid, days)]
        glull.append(NL.stat_cw_gain(days, mins, valid=lull))
    assert abs(np.mean(graw)) < 0.05 and np.mean(glull) < np.mean(graw) - 0.1, (graw, glull)


# --------------------------------------------------------------------------------------------- sizes
CALIBRATED = [  # (family, scenario, null, statistic): documented as calibrated in null_sizes.json
    ("activity", "indep", "block_shift", "cw_gain_trim"),
    ("activity", "indep", "crossday", "cw_gain_trim"),
    ("room", "global_drive", "room_relabel", "room_excess"),
    ("event", "monday", "placebo_dates_weekday", "event_step_k1"),
    ("lever", "indep", "lever_controls_past", "lever_effect"),
    ("signed", "sparse", "agent_field", "signed_faction"),
    ("pull", "indep", "crossday_message_placebo", "message_pull"),
]
TRAPS = [  # (family, scenario, null, statistic, minimum false-positive rate in the mini-run)
    ("activity", "indep", "block_shift", "cw_gain_raw", 0.15),
    ("activity", "day_edge", "block_shift", "cw_gain_trim", 0.25),
    ("activity", "stalls", "crossday", "cw_gain_trim", 0.5),
    ("room", "room_drive", "room_relabel", "room_excess", 0.4),
    ("lever", "indep", "lever_controls_past_cut", "lever_effect", 0.2),
    ("signed", "sparse", "fdr_direct", "signed_negpairs", 0.15),
    ("pull", "day_drive", "crossday_message_placebo", "message_pull", 0.5),
]


def _documented(null, stat, scen):
    p = NL.SIZES_JSON
    if not p.exists():
        return None
    for r in json.loads(p.read_text())["table"]:
        if (r["null"], r["statistic"], r["scenario"]) == (null, stat, scen):
            return r
    return None


def test_calibrated_nulls_within_band():
    hi = NL.size_band(REPS)[1] + 0.025       # small-sample slack on top of the binomial 97.5% quantile
    for fam, scen, null, stat in CALIBRATED:
        doc = _documented(null, stat, scen)
        if doc is not None:
            assert doc["status"] == "calibrated", (null, stat, scen, doc["rate"])
        rate, n = _rate(fam, scen, null, stat)
        assert n >= REPS * 0.8 and rate <= hi, (fam, scen, null, stat, rate, n)


def test_known_traps_stay_anticonservative():
    for fam, scen, null, stat, lo in TRAPS:
        rate, n = _rate(fam, scen, null, stat)
        assert rate >= lo, (fam, scen, null, stat, rate, n)
        doc = _documented(null, stat, scen)
        if doc is not None:
            assert doc["status"] == "anti-conservative", (null, stat, scen, doc["rate"])


if __name__ == "__main__":
    import time
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            t0 = time.time()
            try:
                fn()
                print(f"PASS {name} ({time.time() - t0:.1f}s)")
            except Exception as e:  # noqa: BLE001
                fails += 1
                print(f"FAIL {name}: {type(e).__name__}: {e}")
    sys.exit(1 if fails else 0)
