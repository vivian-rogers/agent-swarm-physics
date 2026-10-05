"""H42 round 2, R3 synthetic validation: does a fitted Cox field remove shared-field cross-excitation and keep real
read-out excitation? Round-1 simulator (synthetic.py) on the real call grids of #27, #33, #40, #51c.

Truths: '0' (no cross-excitation, round-1 field m = exp(0.5 z - 0.125), OU tau 15 min); '0s' (strong field
exp(z - 0.5)); 'B' (read-out gated, n_x = 0.15, round-1 field). Fits: world B S0/B and world A S0/A with the round-1
shared 30-min shape ('r1') and the per-day 10-min Cox field ('cox10'). In-sample n_x only.

Writes data/processed/H42-readout-hawkes-kernel/round2/synthetic/r3_synth.parquet.
Usage: uv run python hypotheses/H42-readout-hawkes-kernel/analysis/r3_synthetic.py [--reps 2]
"""
from __future__ import annotations

import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import r3lib as R  # noqa: E402
import synthetic as S  # noqa: E402
import h42lib as H  # noqa: E402

UNITS = ["27", "33", "40", "51c"]
TRUTHS = [("0", 0.0, 0.5), ("0s", 0.0, 1.0), ("B", 0.15, 0.5)]
OUT = H.DATA / "round2" / "synthetic"


def ou_amp(amp):
    def ou(T, rng, tau=900.0, dt=30.0):
        n = int(T // dt) + 2
        z = np.zeros(n)
        a = np.exp(-dt / tau)
        for k in range(1, n):
            z[k] = a * z[k - 1] + np.sqrt(1 - a * a) * rng.normal()
        return lambda t: np.exp(amp * z[np.minimum((np.asarray(t) // dt).astype(int), n - 1)] - amp * amp / 2)
    return ou


def task(args):
    uid, truth, nx, amp, rep = args
    t0 = time.time()
    rng = np.random.default_rng(5000 + 100 * rep + abs(hash((uid, truth))) % 97)
    u = H.load_unit(uid)
    S.ou = ou_amp(amp)
    ev = S.simulate(u, "0" if truth.startswith("0") else "B", nx, rng)
    v = S.synth_unit(u, ev)
    res = {"unit_id": uid, "truth": truth, "n_x_planted": nx, "amp": amp, "rep": rep, "n_events": len(ev),
           "n_x_true": float((ev["kind"] == "cross").sum() / max(len(ev), 1))}
    dsb = R.world_b(v, split=False)
    calls = R.b_call_index(v, dsb)
    dsa = H.build_talk(v, world="A", specs=("A",))
    for base in ("r1", "cox10"):
        resl, mode = R.BASES[base]
        db = R.b_field(dsb, calls, resl, mode)
        o = R.fit_block(db, R.SPECS_B, ["S0", "B"], cv=False)
        res[f"B:{base}:nx"] = o["B:nx"]
        res[f"B:{base}:dll"] = o["B:ll"] - o["S0:ll"]
        da = R.a_field(dsa, resl, mode)
        o = R.fit_block(da, R.SPECS_A, ["S0", "A"], cv=False)
        res[f"A:{base}:nx"] = o["A:nx"]
        res[f"A:{base}:dll"] = o["A:ll"] - o["S0:ll"]
    res["secs"] = time.time() - t0
    print(uid, truth, rep, {k: round(v_, 4) for k, v_ in res.items() if k.endswith(":nx")}, f"{res['secs']:.0f}s",
          flush=True)
    return res


def main():
    reps = int(sys.argv[sys.argv.index("--reps") + 1]) if "--reps" in sys.argv else 2
    units = sys.argv[sys.argv.index("--units") + 1].split(",") if "--units" in sys.argv else UNITS
    jobs = [(u, t, x, a, r) for r in range(reps) for u in units for t, x, a in TRUTHS]
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    with ProcessPoolExecutor(2) as ex:
        for res in ex.map(task, jobs):
            rows.append(res)
            pl.DataFrame(rows).write_parquet(OUT / "r3_synth.parquet")


if __name__ == "__main__":
    main()
