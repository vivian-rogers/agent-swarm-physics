"""R1 synthetic validation (axis F): content gate on the real skeleton (#51b, #38a, #27; plus #51c for power).
Real message times, ledger reads and producing calls; synthetic statement vectors (r2lib.syn_content).
Worlds: N0 no pull; N1 gated pull (named x5); N2 ungated pull; N3 gated pull with dead time 1; P* power ladder.
Writes r2/synthetic_content.json.

Usage: uv run python hypotheses/H50-field-vs-coupling-transfer-lag/analysis/r2_content_synth.py [--seeds 5] [--calib]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import r2lib as R2  # noqa: E402
from build import load_unit  # noqa: E402

ROOT = HERE.parents[2]
OUT = ROOT / "data/processed/H50-field-vs-coupling-transfer-lag"
BASE = dict(rho=0.40, sig_slow=0.06, tau_slow=1800.0, sig_fast=0.09, tau_fast=60.0, sig_n=0.18, a=0.0, named=5.0,
            lam=0.5, mode="gated")
WORLDS = {
    "N0_null": dict(a=0.0),
    "N1_gated": dict(a=0.06),
    "N2_ungated": dict(a=0.06, mode="ungated"),
    "N3_dead1": dict(a=0.06, mode="dead1"),
    "P_half": dict(a=0.03),
    "P_quarter": dict(a=0.015),
}
UNITS = ["51b", "38a", "27", "51c"]


def calib(U, R, Zm):
    """Lag-1 own cosine and same-room cross-agent cosine within 60 s (H29's calibration analogues)."""
    t, s = R["m_t"], R["m_sender"]
    own = []
    for a in np.unique(s[s >= 0]):
        idx = np.where(s == a)[0]
        own.append(np.einsum("ij,ij->i", Zm[idx[1:]], Zm[idx[:-1]]))
    own = np.concatenate(own)
    cross = []
    for i in range(1, len(t)):
        j = i - 1
        if t[i] - t[j] < 60 and s[i] != s[j] and R["m_room"][i] == R["m_room"][j]:
            cross.append(Zm[i] @ Zm[j])
    return float(np.mean(own)), float(np.mean(cross)) if cross else np.nan


def run_world(U, R, prm, seed, plc):
    Zm, truth = R2.syn_content(U, R, prm, seed=seed)
    rows = R2.content_rows(U, R, Zm, plc)
    res = {}
    for lab, sel in (("all", None), ("named", rows["ment"]), ("unnamed", ~rows["ment"])):
        mj = R2.matched_age_jump(rows, U, "y", sel=sel, nboot=200, seed=seed)
        res[lab] = dict(J=mj["J"].tolist(), lo=mj["lo"].tolist(), hi=mj["hi"].tolist(), se=mj["se"].tolist(),
                        n_h=mj["n_h"].tolist(), truth1=R2.truth_hop1(rows, truth, sel),
                        naive=R2.unmatched_contrast(rows, "y", sel))
    res["calib"] = calib(U, R, Zm)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--calib", action="store_true")
    ap.add_argument("--units", default=",".join(UNITS))
    ap.add_argument("--worlds", default=",".join(WORLDS))
    args = ap.parse_args()
    out = {}
    p = OUT / "r2/synthetic_content.json"
    if p.exists():
        out = json.loads(p.read_text())
    for u in args.units.split(","):
        U = load_unit(OUT / "units" / f"{u}.npz")
        U["N"] = int(U["N"])
        R = R2.load_r2(OUT / "r2/units" / f"{u}.npz")
        plc = R2.placebo_index(R, np.random.default_rng(1))
        if args.calib:
            Zm, _ = R2.syn_content(U, R, dict(BASE), seed=0)
            print(u, "own lag-1 cos, cross 60 s cos:", calib(U, R, Zm))
            continue
        for w in args.worlds.split(","):
            prm = dict(BASE)
            prm.update(WORLDS[w])
            key = f"{u}|{w}"
            out[key] = []
            for sd in range(args.seeds):
                t0 = time.time()
                r = run_world(U, R, prm, 100 + sd, plc)
                out[key].append(r)
                a = r["all"]
                print(f"{key} s{sd} {time.time() - t0:.0f}s J1 {a['J'][0]:.4f} [{a['lo'][0]:.4f},{a['hi'][0]:.4f}] "
                      f"J2 {a['J'][1]:.4f} truth {a['truth1']:.4f} naive {a['naive']:.4f} | named {r['named']['J'][0]:.4f} "
                      f"(t {r['named']['truth1']:.4f}) unnamed {r['unnamed']['J'][0]:.4f} (t {r['unnamed']['truth1']:.4f}) "
                      f"calib {r['calib'][0]:.2f}/{r['calib'][1]:.2f}", flush=True)
            p.write_text(json.dumps(out))


if __name__ == "__main__":
    main()
