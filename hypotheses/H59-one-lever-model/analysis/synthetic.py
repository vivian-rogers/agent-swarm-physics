"""H59 synthetic validation (axis F): the real design (from-states, covariates, kick exposures) of a period, outcomes
drawn from a planted baseline plus planted kick terms, then the identical pipeline (baseline, triples, LOCO).

Worlds: lever (shared theta 60 deg), dirviol (N toward work, others toward talk), delay (one amplitude), null.
Usage: uv run python analysis/synthetic.py --goal 51 --worlds lever,dirviol,delay,null --reps 2
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h59lib as L  # noqa: E402

K_TRUE = [1.0, 0.3, 0.1, 0.05, 0.0, 0.0]
TRIPLES = {"N": (0.8, 2.0), "Hu": (0.0, 0.3), "Hm": (0.3, 2.0), "A": (0.2, 2.5)}
TH = 75.0


def planted_B(world):
    B = np.zeros((len(L.CLASSES), L.NL, 3, 3))
    for ci, c in enumerate(L.CLASSES):
        if world == "null":
            continue
        kap, h = TRIPLES[c] if world != "delay" else (0.3, 2.0)
        th = np.radians(TH)
        if world == "dirviol":
            th = 0.0 if c == "N" else np.pi / 2
        u, _ = L.u_vec(th)
        core = kap + h * (u[None, :] - u[:, None]) / 2
        np.fill_diagonal(core, 0)
        B[ci] = np.array(K_TRUE)[:, None, None] * core[None]
    return B


def simulate(d, B, rng, real_y):
    n = d["n"]
    # baseline: marginal transition log-odds per from-state (structural) + agent/day heterogeneity + idle aging
    E = np.zeros((n, 3))
    na, nd = d["agent"].max() + 1, d["day"].max() + 1
    for i in range(3):
        sel = d["fs"] == i
        cnt = np.bincount(real_y[sel], minlength=3) + 1.0
        for j in L.OTHER[i]:
            ae, de = rng.normal(0, 0.5, na), rng.normal(0, 0.3, nd)
            E[sel, j] = np.log(cnt[j] / cnt[i]) + ae[d["agent"][sel]] + de[d["day"][sel]]
            if i == 0:
                E[sel, j] -= 0.2 * (d["run"][sel] - 2)
    D = d["bits"][:, :, 1:].reshape(n, -1).astype(float)
    for i in range(3):
        sel = d["fs"] == i
        E[sel] += D[sel] @ B[:, :, i, :].reshape(-1, 3)
        E[sel, i] = 0
    P = np.exp(E - E.max(1, keepdims=True))
    P /= P.sum(1, keepdims=True)
    u = rng.random(n)
    return (u[:, None] > P.cumsum(1)).sum(1).clip(0, 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--goal", type=int, default=51)
    ap.add_argument("--worlds", default="lever,dirviol,delay,null")
    ap.add_argument("--reps", type=int, default=2)
    a = ap.parse_args()
    d = L.arrays(L.load(a.goal))
    real_y = d["y"].copy()          # used only for marginal transition counts per from-state
    cls = L.powered(d)
    outp = L.OUT / "synthetic"
    outp.mkdir(parents=True, exist_ok=True)
    fn = outp / f"synthetic_G{a.goal}.json"
    res = json.loads(fn.read_text()) if fn.exists() else {}
    for world in a.worlds.split(","):
        for rep in range(a.reps):
            t0 = time.time()
            rng = np.random.default_rng(1000 * rep + hash(world) % 997)
            B = planted_B(world)
            d["y"] = simulate(d, B, rng, real_y)
            b = L.baseline(d)
            kd = L.KD(d, b["off"])
            tri, v, lv = L.triples(kd, cls, nboot=0)
            lo = L.loco(d, kd, cls, nboot=100, seed=rep)
            res[f"{world}_{rep}"] = {"world": world, "triples": tri, "loco": lo, "classes": [L.CLASSES[c] for c in cls],
                                     "secs": time.time() - t0}
            fn.write_text(json.dumps(res, indent=1))
            print(world, rep, f"{time.time() - t0:.0f}s", {c: (round(x["T"], 2) if x["T"] is not None else None,
                                                           round(x["S"]["lever"], 1), round(x["S"]["free"], 1),
                                                           round(x["S"]["delay"], 1)) for c, x in lo.items()},
                  {c: (round(tri[c]["kappa"]["est"], 2), round(tri[c]["h"]["est"], 2)) for c in tri if c in L.CLASSES},
                  round(tri["theta_deg"]["est"], 1), flush=True)


if __name__ == "__main__":
    main()
