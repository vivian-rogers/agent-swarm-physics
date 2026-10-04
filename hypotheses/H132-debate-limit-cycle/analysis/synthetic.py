"""H132 synthetic validation on the real #12 skeleton (axis F; before any real-data statistic).

Keeps the real debater message sequences (debate, phase, team, agent, time; turn runs; visibility flags); only the
message projections on the issue axis (y_a) and topic axis (y_g) are synthetic:
  y_a = eps_team * mu + a_agent + u_turn + e,   y_g = b_agent + v_turn + e'
Worlds (turn-level latent u, v):
  W0 speaker-only alternation (u = v = 0; static staggered field mu and agent fields only)
  W1 symmetric limit cycle: u_{t+1} = -k u_t + eta (k = 0.3, 0.6)
  W2 common drift: u_{t+1} = +0.5 u_t + eta
  W3 directed cycle: Opposition responds (-k u_t), Government does not (fresh eta)
  W4 staggered-field ramp: mu grows linearly from 0 to 2 mu over the debate (no dynamics)
  W5 rotation (probability current): (u, v)_{t+1} = k R90 (u, v)_t + noise
Noise: message noise sd 1 per projection (whitened units); mu = 0.2 (H21's tilt); agent fields sd 0.3; latent sd s.

    uv run python hypotheses/H132-debate-limit-cycle/analysis/synthetic.py [--reps 100] [--perm 300]
Output: data/processed/H132-debate-limit-cycle/synthetic/summary.json
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h132lib as L  # noqa: E402

OUT = L.DATA.parent / "synthetic"
WORLDS = {
    "W0_speaker_only": dict(kind="none", k=0.0, s=0.0),
    "W1_cycle_k0.3_s1": dict(kind="cycle", k=0.3, s=1.0),
    "W1_cycle_k0.6_s1": dict(kind="cycle", k=0.6, s=1.0),
    "W1_cycle_k0.6_s0.5": dict(kind="cycle", k=0.6, s=0.5),
    "W2_drift": dict(kind="drift", k=0.5, s=1.0),
    "W3_directed_k0.6": dict(kind="directed", k=0.6, s=1.0),
    "W4_ramp": dict(kind="ramp", k=0.0, s=0.0),
    "W5_rotation_k0.6": dict(kind="rotation", k=0.6, s=1.0),
}


def simulate(M: L.Msgs, P: dict, rng, mu=0.2):
    """Message-level y_a, y_g (indexed by message row r) on the real skeleton."""
    df = M.df.sort("debate", "phase", "t")
    r = df["r"].to_numpy()
    deb, ph, tm, ag = df["debate"].to_numpy(), df["phase"].to_numpy(), df["team"].to_numpy(), df["agent"].to_numpy()
    n_all = int(M.df["r"].max()) + 1
    ya, yg = np.zeros(n_all), np.zeros(n_all)
    fa = {a: rng.normal(0, 0.3) for a in np.unique(ag)}
    fb = {a: rng.normal(0, 0.3) for a in np.unique(ag)}
    i, n = 0, len(r)
    u = v = 0.0
    prev_key = None
    while i < n:
        j = i
        while j + 1 < n and deb[j + 1] == deb[i] and ph[j + 1] == ph[i] and tm[j + 1] == tm[i]:
            j += 1
        key = (deb[i], ph[i])
        if key != prev_key:
            u, v = rng.normal(0, P["s"]), rng.normal(0, P["s"])
            pos, nturn = 0, int(1 + np.sum([(deb[q] == deb[i]) and (ph[q] == ph[i]) and (q == 0 or tm[q] != tm[q - 1] or deb[q] != deb[q - 1] or ph[q] != ph[q - 1]) for q in range(i, n)]))
        else:
            eta, eta2 = rng.normal(0, P["s"]), rng.normal(0, P["s"])
            if P["kind"] == "cycle":
                u = -P["k"] * u + eta * np.sqrt(1 - P["k"] ** 2)
            elif P["kind"] == "drift":
                u = P["k"] * u + eta * np.sqrt(1 - P["k"] ** 2)
            elif P["kind"] == "directed":
                u = (-P["k"] * u + eta * np.sqrt(1 - P["k"] ** 2)) if tm[i] == -1 else eta
            elif P["kind"] == "rotation":
                u, v = P["k"] * (-v) + eta * np.sqrt(1 - P["k"] ** 2), P["k"] * u + eta2 * np.sqrt(1 - P["k"] ** 2)
            pos += 1
        m_eff = mu * (2 * pos / max(nturn - 1, 1)) if P["kind"] == "ramp" else mu
        for q in range(i, j + 1):
            ya[r[q]] = tm[q] * m_eff + fa[ag[q]] + u + rng.normal(0, 1)
            yg[r[q]] = fb[ag[q]] + v + rng.normal(0, 1)
        prev_key = key
        i = j + 1
    return ya, yg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=100)
    ap.add_argument("--perm", type=int, default=300)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    M = L.load("bge_small", "masked")
    summ = {}
    for w, P in WORLDS.items():
        rng = np.random.default_rng(abs(hash(w)) % 2 ** 31 if False else sum(map(ord, w)))
        rej = {"Lam": 0, "rho1_neg": 0, "rho2_pos": 0, "A": 0, "L": 0, "dRho_vis": 0, "Lam_detrend": 0}
        vals = {"Lam": [], "rho1": [], "rho2": [], "A": [], "L": []}
        for rep in range(a.reps):
            ya, yg = simulate(M, P, rng)
            T = L.turns(M, ("deb",), ya, yg)
            T.V = np.zeros((len(T.ya), 1))
            res = L.shuffle_test(T, a.perm, seed=rep, keys=("rho1", "rho2", "Lam", "A", "L", "dRho_vis"))
            rd = L.shuffle_test(T, a.perm, seed=rep + 7, detrend=True, keys=("Lam",))
            rej["Lam"] += res["Lam"]["p_hi"] < 0.05
            rej["Lam_detrend"] += rd["Lam"]["p_hi"] < 0.05
            rej["rho1_neg"] += res["rho1"]["p_lo"] < 0.05
            rej["rho2_pos"] += res["rho2"]["p_hi"] < 0.05
            rej["A"] += res["A"]["p_two"] < 0.05
            rej["L"] += res["L"]["p_two"] < 0.05
            rej["dRho_vis"] += res["dRho_vis"]["p_lo"] < 0.05
            for k in vals:
                vals[k].append(res[k]["obs"])
        summ[w] = {"params": P, "reps": a.reps, **{f"rate_{k}": v / a.reps for k, v in rej.items()},
                   **{f"mean_{k}": float(np.mean(v)) for k, v in vals.items()}}
        print(w, {k: round(v, 3) if isinstance(v, float) else v for k, v in summ[w].items() if k != "params"}, flush=True)
    (OUT / "summary.json").write_text(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
