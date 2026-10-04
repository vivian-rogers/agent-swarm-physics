"""H50 synthetic validation (axis F): gated swarms at village sampling with real input schedules.

Scenarios plant a field (human / nudge / day-edge inputs), a gated coupling (peer chat read at the next call),
an unmeasured slow common field (OU), dead times, schedule-clustered inputs and an ungated rival. Every estimator
used on real data runs here, and is compared with the planted truth:
  - gate: hop-1 read-out jump vs the per-pair marginal effect at the read-out call; onset hop with dead time;
  - Part B: onset hop of the response to human messages (field dead time);
  - Part A: FIR dead time and gain of the swarm response;
  - C1: field share f_F and peer share f_peer vs the true shares (component switched off, same seeds);
  - CF: coupling share of talk co-movement from the gated kernel vs the true coupling share.

Usage: uv run python hypotheses/H50-field-vs-coupling-transfer-lag/analysis/synthetic.py [--seeds 4] [--quick]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "POLARS_MAX_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h50lib as L  # noqa: E402
import schedules as SC  # noqa: E402
import simulate as S  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data/processed/H50-field-vs-coupling-transfer-lag/synthetic"

DAYS_III = ['2026-07-13', '2026-07-14', '2026-07-15', '2026-07-16', '2026-07-17', '2026-07-20', '2026-07-21',
            '2026-07-22']                                  # #51c-d (non-holdout): bookends, nudges, human messages
DAYS_I = ['2025-05-27', '2025-05-28', '2025-05-29', '2025-05-30', '2025-06-02', '2025-06-03', '2025-06-04',
          '2025-06-05', '2025-06-06', '2025-06-09']        # #4c (non-holdout): human-rich, 2-h days

BASE_III = dict(a_talk=-3.3, a_pause=-3.75)
BASE_I = dict(a_talk=-2.2, a_pause=-3.0, cadence=60.0, pause_med=60.0, busy_med=9.0)
FIELD = dict(g_talk={'human': (1.5, 0.5), 'nudge': (1.0, 0.0)}, g_act={'human': (1.0, 0.3), 'nudge': (1.5, 0.0)},
             edge_amp=1.0)
COUP = dict(J_talk=0.3, J_act=0.3)
OU = dict(ou_sig=0.8)

SCEN = {
    # name: (world, params, truth pairs (on, off_field, off_coupling) names)
    "S0_null": ("III", {}),
    "S1_field": ("III", dict(**FIELD)),
    "S2_coupling": ("III", dict(**COUP)),
    "S3_both": ("III", dict(**FIELD, **COUP)),
    "S4_ou": ("III", dict(**OU)),
    "S5_all": ("III", dict(**FIELD, **COUP, **OU)),
    "S5f_field_ou": ("III", dict(**FIELD, **OU)),         # S5 with coupling off (truth)
    "S5c_coup_ou": ("III", dict(**COUP, **OU)),           # S5 with field off (truth)
    "S6_edge_clustered": ("III-clustered", dict(**FIELD, **COUP, **OU)),
    "S7_dead": ("III", dict(**FIELD, **COUP, dead_c=2, dead_f=2)),
    "S8_ungated": ("III", dict(**COUP, ungated=True)),
    "I2_coupling": ("I", dict(**COUP)),
    "I3_both": ("I", dict(**FIELD, **COUP)),
    "I1_field": ("I", dict(**FIELD)),
    "I4_ou": ("I", dict(**OU)),
}


def cluster_humans(sched, rng):
    """Move every human message to within ~10 min after its day's start (inputs correlated with schedule edges)."""
    days = sched["days"]
    new = []
    for (t, kind, room, tg) in sched["inputs"]:
        if kind == "human":
            d = int(np.argmin([abs(t - (a + b) / 2) for a, b in days]))
            t = days[d][0] + rng.exponential(600.0)
        new.append((t, kind, room, tg))
    new.sort()
    return dict(days=days, inputs=new)


def world(name, seed):
    if name.startswith("III"):
        sch = SC.real_schedule(DAYS_III, 10, seed=0)
        base = dict(BASE_III)
        if name == "III-clustered":
            sch = cluster_humans(sch, np.random.default_rng(7))
    else:
        sch = SC.real_schedule(DAYS_I, 8, seed=0)
        base = dict(BASE_I, N=8)
    return sch, base


def analyse(U, truth, nboot=60, full=True):
    c = U["calls"]
    keys = L.call_keys(U)
    m, mp = U["msgs"], U["mpairs"]
    te, de, rec = m["t"][mp["msg"]], m["day"][mp["msg"]], mp["rec"]
    W = 1.5 * L.median_call_interval(U)
    res = dict(W=W, n_calls=int(len(c["tc"])), n_msgs=int(len(m["t"])), talk=float(c["talk"].mean()),
               act=float(c["act"].mean()), w_read_s=L.mean_readout_wait(U))
    yT, yA = c["talk"].astype(float), c["act"].astype(float)
    gk = L.gate_kernel(U, keys, te, de, rec, yT, K=6, W=W, nboot=nboot)
    ga = L.gate_kernel(U, keys, te, de, rec, yA, K=3, W=W, nboot=nboot)
    tp = truth["pairs"]
    res["truth_kernel"] = [float(tp[tp[:, 4] == h, 2].sum() / max(len(te), 1)) if len(tp) else 0.0 for h in range(1, 7)]
    res["gate_talk"] = {k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in gk.items()}
    res["gate_act_J1"] = [float(ga["jumps"][0]), float(ga["j_lo"][0]), float(ga["j_hi"][0])]
    if not full:
        return res
    grid = L.make_grid(U)
    # Part B: human messages -> recipients (talk), targets vs bystanders
    inp, ip = U["inputs"], U["ipairs"]
    hk = inp["kind"][ip["inp"]] == L.K["human"]
    if hk.sum() > 20:
        t_h, d_h = inp["t"][ip["inp"]][hk], inp["day"][ip["inp"]][hk]
        hr = L.hop_response(U, keys, t_h, d_h, ip["rec"][hk], {"talk": yT}, nboot=nboot)
        res["human_hop_talk"] = dict(r=hr["talk"]["r"].tolist(), lo=hr["talk"]["lo"].tolist(), onset=L.onset_hop(hr["talk"]))
        gh = L.gate_kernel(U, keys, t_h, d_h, ip["rec"][hk], yT, K=4, W=W, nboot=nboot)
        res["human_gate_talk"] = {k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in gh.items()}
        tg = ip["tgt"][hk]
        if tg.sum() > 10:
            hr2 = L.hop_response(U, keys, t_h[tg], d_h[tg], ip["rec"][hk][tg], {"talk": yT}, nboot=nboot)
            res["human_target_onset"] = L.onset_hop(hr2["talk"])
            res["human_target_r"] = hr2["talk"]["r"].tolist()
    # Part A: swarm FIR
    Xs = L.swarm_inputs(U, grid)
    out_fir = {}
    for which in ("A", "T"):
        ys = L.swarm_output(grid, which)
        st = L.fir_stats(ys, Xs)
        g, lam = L.fir_fit(st, len(L.SWARM_CLASSES))
        out_fir[which] = {cl: L.kernel_metrics(g[ci], w_read_min=res["w_read_s"] / 60) for ci, cl in enumerate(L.SWARM_CLASSES)}
        out_fir[which]["lam"] = lam
        ws = L.welch_sums(ys, Xs)
        summ, _, _ = L.welch_summary(ws)
        out_fir[which]["welch"] = {cl: summ[ci] for ci, cl in enumerate(L.SWARM_CLASSES)}
    res["fir"] = out_fir
    # C1 decomposition
    Xa = L.agent_inputs(U, grid)
    Xp = L.peer_series(U, grid)
    c1 = {}
    for which in ("A", "T"):
        for variant in ("span", "full"):
            r = L.c1_decompose(grid, Xa, Xp, which=which, variant=variant)
            c1[(which, variant)] = r
            res[f"c1_{which}_{variant}"] = L.floats(r)
    # counterfactual coupling share (talk), from the gated kernel (hop 1, and hops 1..6 cumulative)
    kern = np.array(gk["kernel"])
    for lab, dlt in (("k1", np.r_[kern[:1], np.zeros(5)]), ("k6", np.clip(kern, 0, None))):
        cf = L.cf_coupling_series(U, grid, keys, te, de, rec, dlt)
        for variant in ("span", "full"):
            res[f"cf_T_{variant}_{lab}"] = L.cf_share(grid, cf, "T", variant)
            r = c1[("T", variant)]
            res[f"cfF_T_{variant}_{lab}"] = L.cf_share_resid(r["resid_F"], r["masks"], cf)
    # true-kernel counterfactual (oracle) for reference
    cf = L.cf_coupling_series(U, grid, keys, te, de, rec, np.array(res["truth_kernel"]))
    res["cf_T_span_oracle"] = L.cf_share(grid, cf, "T", "span")
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=4)
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    allres = {}
    names = [n for n in SCEN if not args.only or n in args.only.split(",")]
    for name in names:
        wname, prm = SCEN[name]
        allres[name] = []
        for sd in range(args.seeds):
            t = time.time()
            sch, base = world(wname, sd)
            p = dict(base)
            p.update(prm)
            U, tr = S.simulate(sch, p, seed=100 + sd)
            r = analyse(U, tr)
            r["seed"] = sd
            allres[name].append(r)
            print(f"{name} seed {sd}: {time.time() - t:.1f}s  J1 {r['gate_talk']['jumps'][0]:.4f} truth {r['truth_kernel'][0]:.4f} "
                  f"fF_A {r['c1_A_full']['f_F']:.3f} fFnull_A {r['c1_A_full']['f_F_null']:.3f} fC_T {r['cf_T_span_k1']['f_C']:.3f}",
                  flush=True)
        (OUT / "synthetic_results.json").write_text(json.dumps(allres, default=lambda o: o.tolist() if isinstance(o, np.ndarray) else float(o)))
    print("written", OUT / "synthetic_results.json")


if __name__ == "__main__":
    main()
