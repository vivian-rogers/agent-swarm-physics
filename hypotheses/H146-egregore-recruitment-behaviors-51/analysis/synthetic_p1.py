"""H146 synthetic validation (axis F) for P1/P2/P3 on the real #51 ledger skeleton.

The real skeleton is kept: talk rows (who called when, d_c, room), the real message stream (who posted when), the
matched-lag window items (mirror read vs in flight), read-out items at the call and in the previous 2 h, and the
names. Only item labels (carries K) and outcomes (adoption at a talk row) are planted.

Worlds
  W_conv_slow   shared field bursts (5-60 min): items in a burst carry K with prob q_b, outcome raised by gamma.
  W_conv_fast   the same with 0.5-3 min bursts (worst case for matched windows of ~8 s).
  W_contagion   no field; each K item read at the producing call (mirror or earlier at that call) raises the
                adoption log-odds by beta (0.3, 0.6); items read at earlier calls in 2 h by beta/5; named reads x3
                (log-odds beta + ln 3) in the named variants.
  W_hub         as W_contagion (beta 0.6) but only the hub's (DeepSeek-V3.2) items act.
  W_mix         slow field + contagion beta 0.3.
Outcome rows: all talk rows (estimator calibration); base rate set for a target number of events (50, 150, 400).
Statistics: delta = beta_Rm - beta_P with the 1-h-block cluster sandwich; size = share of null worlds with the 95% CI
above 0 (and |z| > 1.96); power = share of contagion worlds with the CI above 0; bias = mean(delta) - planted beta.
Output: data/processed/H146-.../synthetic/p1_synthetic.json
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h146lib as L  # noqa: E402

OUT = L.ROOT / "data" / "processed" / "H146-egregore-recruitment-behaviors-51" / "synthetic"


def bursts(rng, t0, t1, rate_per_h, dur_min):
    n = rng.poisson(rate_per_h * (t1 - t0) / (3600 * L.US))
    on = np.sort(rng.uniform(t0, t1, n)).astype(np.int64)
    du = (rng.uniform(*dur_min, n) * 60 * L.US).astype(np.int64)
    return on, on + du


def in_burst(t, on, off):
    # number of active bursts at t
    return (np.searchsorted(on, t, "right") - np.searchsorted(np.sort(off), t, "right")) > 0


def world(ev, rng, kind, beta=0.0, named_x3=False, n_target=150, q0=0.04, qb=0.4, gamma=1.0):
    a = ev.a
    mt, ma = a["msg_t"], a["msg_agent"]
    t0, t1 = mt.min(), mt.max()
    field_m = np.zeros(len(mt), bool); field_r = np.zeros(a["n_rows"], bool)
    if kind in ("conv_slow", "conv_fast", "mix"):
        dur = (5, 60) if kind in ("conv_slow", "mix") else (0.5, 3)
        rate = 0.6 if kind in ("conv_slow", "mix") else 4.0
        on, off = bursts(rng, t0, t1, rate, dur)
        field_m = in_burst(mt, on, off)
        tf = a["row_t"] + (a["row_d"] * L.US).astype(np.int64)   # output time = t_first
        field_r = in_burst(tf, on, off)
    q = np.where(field_m, qb, q0)
    c = (rng.random(len(mt)) < q) & (ma >= 0)
    c = c.astype(np.float32)
    act = c * (ma == L.HUB) if kind == "hub" else c
    Rcall = np.asarray((a["W_read"] @ act) + (a["R_call_rest"] @ act)).ravel()
    R2 = np.asarray(a["R_prev2h"] @ act).ravel()
    Rn = np.asarray(a["W_read_named"] @ act).ravel()
    eta = beta * Rcall + (beta / 5) * R2 + (np.log(3) * Rn if named_x3 else 0)
    if kind in ("conv_slow", "conv_fast", "mix"):
        eta = eta + gamma * field_r
    # base rate for the target count
    lo, hi = -15.0, 0.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if (1 / (1 + np.exp(-(mid + eta)))).sum() > n_target:
            hi = mid
        else:
            lo = mid
    p = 1 / (1 + np.exp(-(lo + eta)))
    y = rng.random(len(p)) < p
    pn = L.Panel(np.array([0]), None, None, c, c > 0, np.zeros(a["n_rows"]), 2)
    return pn, y


def run(reps_null=100, reps_power=60, seed=20261009, designs=("adopt", "expr")):
    ev = L.load()
    a = ev.a
    ctrl = L.controls(ev)
    rng = np.random.default_rng(seed)
    allrows = np.ones(a["n_rows"], bool)
    res = {}
    t_start = time.time()
    specs = []
    # adoption design (card P1): rare events
    if "adopt" in designs:
        for q0 in (0.04, 0.12):
            for n_t in (50, 150, 400):
                specs += [("adopt", "conv_slow", 0.0, False, n_t, q0, reps_null),
                          ("adopt", "conv_fast", 0.0, False, n_t, q0, reps_null),
                          ("adopt", "contagion", 0.3, False, n_t, q0, reps_power),
                          ("adopt", "contagion", 0.6, False, n_t, q0, reps_power)]
    # expression-response design (Amendment A1, O1b): own chat carries K, more events
    if "expr" in designs:
        for q0 in (0.04, 0.12):
            for n_t in (500, 1500, 4000):
                specs += [("expr", "conv_slow", 0.0, False, n_t, q0, reps_null),
                          ("expr", "conv_fast", 0.0, False, n_t, q0, reps_null),
                          ("expr", "contagion", 0.3, False, n_t, q0, reps_power),
                          ("expr", "contagion", 0.6, False, n_t, q0, reps_power)]
            specs += [("expr", "contagion", 0.3, True, 1500, q0, reps_power),
                      ("expr", "contagion", 0.0, True, 1500, q0, reps_power),
                      ("expr", "hub", 0.6, False, 1500, q0, reps_power),
                      ("expr", "mix", 0.3, False, 1500, q0, reps_power),
                      ("expr", "contagion", 0.0, False, 1500, q0, reps_null)]
    for design, kind, beta, nx3, n_t, q0, reps in specs:
        key = f"{design}_{kind}_b{beta}_n{n_t}_q{q0}" + ("_named3" if nx3 else "")
        d, z, dn, ratio, dnh, est_ok = [], [], [], [], [], []
        for r in range(reps):
            pn, y = world(ev, rng, kind, beta, nx3, n_t, q0=q0)
            Xd = L.exposures(ev, pn, host_only=False)
            o = L.p1_fit(ev, Xd, allrows, y, ctrl=ctrl)
            e, se = o["delta"]
            d.append(e); z.append(e / se if se > 0 else 0.0); est_ok.append(o["estimable"])
            if nx3:
                o2 = L.p1_fit(ev, Xd, allrows, y, split_named=True, ctrl=ctrl)
                en, sen = o2["delta_Rm_named"]; eu, seu = o2["delta_Rm_unnamed"]
                dn.append((en, sen, eu, seu))
                ratio.append((np.expm1(en) / np.expm1(eu)) if eu > 0 else np.inf)
            if kind in ("hub", "contagion") and n_t == 1500 and not nx3:
                Xh = L.exposures(ev, pn, host_only=False, nohub=True)
                oh = L.p1_fit(ev, Xh, allrows, y, ctrl=ctrl)
                dnh.append(oh["delta"])
        d, z = np.array(d), np.array(z)
        rec = {"design": design, "world": kind, "reps": reps, "beta": beta, "n_target": n_t, "q0": q0,
               "named_x3": nx3, "mean_delta": float(d.mean()), "sd_delta": float(d.std()),
               "bias": float(d.mean() - beta), "rej_ci_above0": float((z > 1.96).mean()),
               "rej_two_sided": float((np.abs(z) > 1.96).mean()), "estimable_share": float(np.mean(est_ok))}
        if dn:
            dn = np.array(dn)
            rec["named"] = {"mean_delta_named": float(dn[:, 0].mean()), "mean_delta_unnamed": float(dn[:, 2].mean()),
                            "rej_named_minus_unnamed": float(
                                (((dn[:, 0] - dn[:, 2]) / np.sqrt(dn[:, 1] ** 2 + dn[:, 3] ** 2)) > 1.96).mean()),
                            "share_ratio_ge3": float(np.mean(np.array(ratio) >= 3)),
                            "share_ratio_le1": float(np.mean(np.array(ratio) <= 1)),
                            "median_ratio": float(np.median(np.array(ratio)))}
        if dnh:
            dh = np.array(dnh)
            rec["nohub"] = {"mean_delta": float(dh[:, 0].mean()),
                            "rej_ci_above0": float((dh[:, 0] / np.maximum(dh[:, 1], 1e-9) > 1.96).mean())}
        res[key] = rec
        print(key, json.dumps(rec), f"{time.time() - t_start:.0f}s", flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "p1_synthetic.json").write_text(json.dumps({"seed": seed, "worlds": res}, indent=1))


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    A = ap.parse_args()
    if A.quick:
        run(10, 10)
    else:
        run()
