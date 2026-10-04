"""H118 synthetic validation (axis F; run before any real-data statistic): planted replica worlds on the real statement
skeletons of G35 and the identical-kickoff band (G36 regime-III days, G37, G39, G41, G42).

Worlds (card N5): W0 fast damage spreading (tau_D 2 h), W1 slow (2 days), W2 = W0 + a rules field in G35 only,
W3 = W0 + a shared day-level drive in both rooms, W4 frozen (200 h). Variants 'eq' (same shared-goal strength in every
period) and 'var' (strength log-uniform in [0.5, 2] x base per period).
x_s = g_P + a_i + u_r(b) [+ v_d] [+ h_rules] + eta_{i,d} + eps_s; u_r is an OU process on active hours with both rooms
starting from one shared u_0 at the kickoff.
Calibration (instrument; H107 regime-III values): s_eps^2 0.0195, s_eta^2 0.0026, tau_a^2 0.0014 per coordinate;
sigma_u^2 = sigma_g^2 = sigma_v^2 = 0.0026.

Usage: uv run python hypotheses/H118-forked-rpg-replicas/analysis/synthetic.py [--worlds 40] [--boot 100]
Writes data/processed/H118-forked-rpg-replicas/synthetic/summary.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h118lib as L  # noqa: E402

PER = ("35",) + L.BAND
KINDS = ("stmt", "stmt_bin", "agent_bin")
CAL = {"eps": 0.0195, "eta": 0.0026, "a": 0.0014, "u": 0.0026, "g": 0.0026, "v": 0.0026}


def simulate(sk, world, rng, g_var, tau):
    n, dim = len(sk["agent"]), 32
    X = np.zeros((n, dim))
    X += rng.normal(0, np.sqrt(g_var), dim)                       # shared goal field g_P
    agents = np.unique(sk["agent"])
    A = {a: rng.normal(0, np.sqrt(CAL["a"]), dim) for a in agents}
    X += np.stack([A[a] for a in sk["agent"]])
    keys = sk["agent"].astype(np.int64) * 1000 + sk["day"]
    E = {k: rng.normal(0, np.sqrt(CAL["eta"]), dim) for k in np.unique(keys)}
    X += np.stack([E[k] for k in keys])
    X += rng.normal(0, np.sqrt(CAL["eps"]), (n, dim))
    # room OU states with a shared initial state
    bins = np.unique(sk["bin"])
    tb = {b: sk["t"][np.flatnonzero(sk["bin"] == b)[0]] for b in bins}
    order = sorted(bins, key=lambda b: tb[b])
    u0 = rng.normal(0, np.sqrt(CAL["u"]), dim)
    U = {}
    for r in (2, 3):
        prev_t, prev_u = 0.0, u0
        for b in order:
            phi = np.exp(-(tb[b] - prev_t) / tau)
            prev_u = phi * prev_u + np.sqrt(1 - phi ** 2) * rng.normal(0, np.sqrt(CAL["u"]), dim)
            prev_t = tb[b]
            U[(r, b)] = prev_u
    X += np.stack([U[(r, b)] for r, b in zip(sk["room"], sk["bin"])])
    if world == "W3":
        Vd = {d: rng.normal(0, np.sqrt(CAL["v"]), dim) for d in np.unique(sk["day"])}
        X += np.stack([Vd[d] for d in sk["day"]])
    if world == "W2" and sk["period"] == "35":
        X += rng.normal(0, np.sqrt(g_var), dim)
    return X


def run(worlds=40, boot=100, seed=20261004):
    rng = np.random.default_rng(seed)
    sk = {p: L.period_data(p) for p in PER}
    taus = {"W0": 2.0, "W1": 48.0, "W2": 2.0, "W3": 2.0, "W4": 200.0}
    summ = {}
    for variant in ("eq", "var"):
        for world, tau in taus.items():
            if variant == "var" and world not in ("W0", "W2"):
                continue
            rec = {k: [] for k in ("tau", "plateau", "plateau_ci", "rank")}
            for kind in KINDS:
                rec["cover_" + kind], rec["pos_" + kind], rec["late_cover_" + kind] = [], [], []
            for _ in range(worlds):
                ql = {}
                lo35 = np.nan
                for p in PER:
                    gv = CAL["g"] * (np.exp(rng.uniform(np.log(0.5), np.log(2))) if variant == "var" else 1.0)
                    s = dict(sk[p])
                    s["X"] = simulate(s, world, rng, gv, tau)
                    r = L.overlap_stats(s)
                    ql[p] = r["q_late"]
                    if p == "35":
                        ft = L.fit_tau(r["t"], r["q_bin"], r["w_bin"])
                        rec["tau"].append(ft["tau"])
                        for kind in KINDS:
                            bs = L.bootstrap(s, kind=kind, B=boot, rng=rng)
                            cov, pos = [], []
                            for d in range(2, s["n_days"] + 1):
                                lo, hi = L.ci([b["M_d"].get(d, np.nan) for b in bs])
                                cov.append(lo <= 0 <= hi)
                                pos.append(lo > 0)
                            rec["cover_" + kind].append(all(cov))
                            rec["pos_" + kind].append(any(pos))
                            lo, hi = L.ci([b["M_late"] for b in bs])
                            rec["late_cover_" + kind].append(lo <= 0 <= hi)
                            if kind == "agent_bin":
                                lo35 = L.ci([b["q_late"] for b in bs])[0]
                band = [ql[p] for p in L.BAND]
                rec["plateau"].append(ql["35"] > np.nanmax(band))
                rec["plateau_ci"].append(lo35 > np.nanmax(band))
                rec["rank"].append(int(np.sum(np.array(band) < ql["35"])))
            t = np.array(rec["tau"])
            res = {"planted_tau_h": tau, "worlds": worlds,
                   "tau_fast_le4h": float(np.mean(t <= 4)), "tau_slow_ge8h": float(np.mean(t >= 8)),
                   "tau_median": float(np.nanmedian(t)),
                   "plateau_point_gt_max": float(np.mean(rec["plateau"])),
                   "plateau_lowerCI_gt_max": float(np.mean(rec["plateau_ci"])),
                   "rank_mean": float(np.mean(rec["rank"]))}
            for kind in KINDS:
                res[f"M_d>=2_all_cover0_{kind}"] = float(np.mean(rec["cover_" + kind]))
                res[f"M_d>=2_any_pos_{kind}"] = float(np.mean(rec["pos_" + kind]))
                res[f"M_late_cover0_{kind}"] = float(np.mean(rec["late_cover_" + kind]))
            summ[f"{world}_{variant}"] = res
            print(world, variant, res, flush=True)
    out = L.DATA / "synthetic"
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps({"calibration": CAL, "results": summ}, indent=1))
    return summ


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--worlds", type=int, default=40)
    ap.add_argument("--boot", type=int, default=100)
    a = ap.parse_args()
    run(a.worlds, a.boot)
