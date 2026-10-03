"""H04 exploratory Hawkes fits per regime (non-holdout): n, exogenous kernels, CV vs. Poisson null, time-rescaling,
synthetic recovery and a day-bootstrap. Also the NE10 pre/post fits (exploratory).

Run: uv run python hypotheses/H04-reversible-forcing/analysis/hawkes_explore.py   (~3 worker processes)
"""
from __future__ import annotations

import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hawkes import *  # noqa: E402,F403

NBOOT = 40
NE10_PRE = ("2026-01-12", "2026-02-10")   # #27 (01-12..01-23) + 02-09; #28-#29 held out and dropped by select_days
NE10_POST = ("2026-02-10", "2026-02-21")  # #30 (from 02-10), #31


def suites():
    cal = calendar()
    return {
        "I": select_days(cal, regimes=["I"]),
        "II": select_days(cal, regimes=["II"]),
        "III": select_days(cal, regimes=["III"]),
        "III_4h": select_days(cal, regimes=["III"], hours=[4]),
        "III_8h": select_days(cal, regimes=["III"], hours=[8]),
        "NE10_pre": select_days(cal, date_from=NE10_PRE[0], date_to=NE10_PRE[1]),
        "NE10_post": select_days(cal, date_from=NE10_POST[0], date_to=NE10_POST[1]),
    }


def run(label_days):
    label, days = label_days
    t0 = time.time()
    ser = build_series(days)
    m = fit_suite(ser)
    out = {"label": label, "days": [days[0], days[-1], len(days)], "fit": m.summary()}
    m0 = Model(ser, null_params()).fit()
    out["poisson_loglik_per_event"] = m0.loglik(m0.theta) / max(1, ser.n_events)
    out["ks_hawkes"], out["ks_poisson"] = m.rescaled_ks(), m0.rescaled_ks()
    if len(ser.days) >= 10:
        out["cv"] = cv(ser)
    if label in ("I", "III"):
        out["recovery"] = recovery(m, reps=3)
    rng = np.random.default_rng(RNG_SEED)
    bs = []
    for b in range(NBOOT if len(ser.days) >= 5 else 0):
        idx = rng.integers(0, len(ser.days), len(ser.days))
        mb = Model(ser.subset(list(idx)), m.free).fit(x0=m.theta).summary()
        bs.append({k: mb.get(k) for k in ("n", "a1", "a2", "eh", "en", "tau_fast_s", "tau_slow_s", "tau_h_s", "tau_n_s")})
    out["boot"] = bs
    for k in ("n", "eh", "en", "a1", "a2"):
        v = np.array([b[k] for b in bs if b.get(k) is not None], float)
        if len(v) > 5:
            out[f"{k}_ci"] = [float(out["fit"].get(k, np.nan)), float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]
    out["runtime_s"] = time.time() - t0
    print(f"[{label}] n={out['fit']['n']:.3f} events={ser.n_events} {out['runtime_s']:.0f}s", flush=True)
    return label, out


if __name__ == "__main__":
    S_ = suites()
    with ProcessPoolExecutor(max_workers=3) as ex:
        res = dict(ex.map(run, [(k, v) for k, v in S_.items() if len(v) >= 3]))
    jdump(res, OUT / "explore_hawkes.json")
    write_provenance("explore_hawkes.json", "hypotheses/H04-reversible-forcing/analysis/hawkes_explore.py",
                     ["calendar", "chat_core", "exposure", "roster"],
                     {"DT_s": DT, "quarters": NQ, "bounds": {k: list(v) for k, v in BOUNDS.items()}, "boot": NBOOT,
                      "cv_folds": 5, "holdout": "excluded", "suites": {k: [v[0], v[-1], len(v)] for k, v in S_.items() if v}})
    print("done")
