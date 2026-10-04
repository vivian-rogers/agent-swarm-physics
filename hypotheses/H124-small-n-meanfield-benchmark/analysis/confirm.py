"""H124 confirmatory tests on the LOCKED HOLDOUT. Written after exploratory round 1 (2026-10-04); NOT RUN.

Guard: the holdout is touched only with BOTH flags, a clean git state for H124's code, and a holdout-ledger check:
  uv run python hypotheses/H124-small-n-meanfield-benchmark/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
Without the flags the script prints the frozen predictions and exits. `--dry-run` runs the pipeline on two non-holdout
stand-in units under names absent from the exploration files; nothing is written.

Targets: held-out regime-I N = 4 goal periods #1 (units 1a, 1c, 1d, 1e; 1b is one day) and #9 (3 days).
  C1  persistence law (per-call talk clock): in units with max ML self-coupling J_ii > 0.6, plain TAP has no solution
      on >= 1 row AND MS eps_J > 0.25; in units with max J_ii <= 0.6, min(TAP, MS) eps_J <= 0.10 with TAP defined on
      every row. Holds in >= 4/5 target units.                         round 1: 9/9 units
  C2  nMF eps_J > 0.10 in >= 2/3 of units.                              round 1: 8/9
  C3  off-diagonal ML J inside the circular-shift null q95 in >= 1/2 of units (couplings at noise level).
                                                                        round 1: 7/9
  C4  1-min talk grid: MS eps_J <= 0.10 in >= 1/2 of units with >= 3 grid days.   round 1: 5/7
  C5  leave-one-day-out log-likelihood: nMF|s within 0.01 nats/call of exact ML in >= 2/3 of units with >= 5 days.
                                                                        round 1: 5/5 (4a, 4c, 5, 6a, 6b, 8 within 0.005)
Reuse: #1 is planned by many (Hawkes, regime-I culture: H03, H19, H81 ...); #9 by H81, H97. H124's statistic (exact vs
mean-field kinetic Ising inversion errors on the per-call talk clock) is a new family ("kinetic_ising_inverse");
the ledger check decides; disclose in both cards and LOG.md.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h124lib as L  # noqa: E402
import run as RUN  # noqa: E402
import build as B  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))

FROZEN = {  # frozen 2026-10-04 after exploratory round 1 (card, "Confirmatory predictions")
    "units": ["1a", "1c", "1d", "1e", "9"], "boot": 200, "n_shift": 20,
    "C1_Jii_split": 0.6, "C1_ms_bad": 0.25, "C1_good": 0.10, "C1_min_units": 4,
    "C2_nmf_min": 0.10, "C2_share": 2 / 3,
    "C3_share": 0.5,
    "C4_ms_max": 0.10, "C4_min_grid_days": 3, "C4_share": 0.5,
    "C5_ll_gap": 0.01, "C5_min_days": 5, "C5_share": 2 / 3,
}
FILES = ["hypotheses/H124-small-n-meanfield-benchmark/analysis/confirm.py",
         "hypotheses/H124-small-n-meanfield-benchmark/analysis/h124lib.py",
         "hypotheses/H124-small-n-meanfield-benchmark/analysis/run.py",
         "hypotheses/H124-small-n-meanfield-benchmark/scheme/build.py"]


def git_clean() -> bool:
    out = subprocess.run(["git", "-C", str(L.ROOT), "status", "--porcelain", "--", *FILES], capture_output=True,
                         text=True).stdout
    return out.strip() == ""


def evaluate(frames: dict, stores: dict, boot: int, n_shift: int) -> dict:
    rng = np.random.default_rng(1240)
    res = {}
    for u, P in frames.items():
        rows, N = L.rows_from_frame(P)
        r = RUN.bench(rows, N, rng, boot, shift_fn=lambda g, P=P: L.shift_null_from_frame(P, g), n_shift=n_shift)
        r["n_days"] = P["day"].n_unique()
        g, _ = L.grid_rows_from_store(stores.get(u, {}), "talk")
        if g is not None and len(set(g[0][2])) >= 2:
            r["grid_talk"] = RUN.bench(g, 4, rng, min(boot, 100), ll=False)
            r["grid_days"] = len(set(g[0][2]))
        res[u] = r
    return res


def decide(res: dict) -> dict:
    F = FROZEN
    us = list(res)
    c1 = 0
    for u in us:
        r = res[u]
        if max(r["Jii"]) > F["C1_Jii_split"]:
            c1 += int(r["TAP"]["cover"] < 1 and r["MS"]["epsJ"] > F["C1_ms_bad"])
        else:
            c1 += int(r["TAP"]["cover"] == 1 and min(r["TAP"]["epsJ"], r["MS"]["epsJ"]) <= F["C1_good"])
    c2 = np.mean([res[u]["nMF"]["epsJ"] > F["C2_nmf_min"] for u in us]) >= F["C2_share"]
    c3 = np.mean([not res[u]["informative"] for u in us]) >= F["C3_share"]
    g = [u for u in us if res[u].get("grid_days", 0) >= F["C4_min_grid_days"]]
    c4 = (np.mean([res[u]["grid_talk"]["MS"]["epsJ"] <= F["C4_ms_max"] and res[u]["grid_talk"]["MS"]["cover"] == 1
                   for u in g]) >= F["C4_share"]) if g else None
    l5 = [u for u in us if res[u]["n_days"] >= F["C5_min_days"]]
    c5 = (np.mean([res[u]["heldout_ll"]["ML"] - res[u]["heldout_ll"]["nMF|s"] <= F["C5_ll_gap"] for u in l5])
          >= F["C5_share"]) if l5 else None
    return {"C1": bool(c1 >= min(F["C1_min_units"], len(us))), "C1_units": int(c1), "C2": bool(c2), "C3": bool(c3),
            "C4": None if c4 is None else bool(c4), "C5": None if c5 is None else bool(c5), "n_units": len(us)}


def run():
    import holdout_ledger as HL
    for tgt in ("G01", "G09"):
        chk = HL.check("H124", tgt, "call_windows+activity_bins_fixed", ["kinetic_ising_inverse"])
        print(tgt, "allowed" if chk["allowed"] else "NOT ALLOWED", "disclosure needed" if chk["needs_disclosure"] else "")
        if not chk["allowed"]:
            raise SystemExit("holdout ledger refuses a same-family reuse: ask the coordinator")
    pu = pl.read_parquet(L.ROOT / "data/processed/shared/period_units.parquet")
    cc = pl.read_parquet(L.ROOT / "data/processed/shared/roster.parquet").filter(pl.col("claude_code"))["agent"].to_list()
    frames = B.build_percall(pu, cc, units=FROZEN["units"], allow_holdout=True, write=False)
    stores = B.build_grid(pu, cc, units=FROZEN["units"], allow_holdout=True, write=False)
    res = evaluate(frames, stores, FROZEN["boot"], FROZEN["n_shift"])
    out = {"results": res, **decide(res)}
    d = L.OUT / "confirm"
    d.mkdir(exist_ok=True)
    (d / "confirm_results.json").write_text(json.dumps(out, indent=1, default=float))
    print({k: v for k, v in out.items() if k != "results"})


def dry_run():
    pu = pl.read_parquet(L.ROOT / "data/processed/shared/period_units.parquet")
    cc = pl.read_parquet(L.ROOT / "data/processed/shared/roster.parquet").filter(pl.col("claude_code"))["agent"].to_list()
    frames = B.build_percall(pu, cc, units=["5", "6b"], allow_holdout=False, write=False)
    stores = B.build_grid(pu, cc, units=["5", "6b"], allow_holdout=False, write=False)
    frames = {f"STANDIN_{k}": v for k, v in frames.items()}
    stores = {f"STANDIN_{k}": v for k, v in stores.items()}
    res = evaluate(frames, stores, 5, 3)
    print("dry-run decisions (stand-ins, not a test):", decide(res))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", action="store_true", dest="ack")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.dry_run:
        dry_run()
        return
    if not (a.confirm and a.ack):
        print("H124 confirm.py: frozen predictions (not run):")
        for k, v in FROZEN.items():
            print(f"  {k}: {v}")
        print("Pass --confirm --i-understand-this-uses-the-locked-holdout to run on the holdout.")
        return
    if not git_clean():
        raise SystemExit("commit H124's code first (predictions and script must be committed before a confirmatory run)")
    run()


if __name__ == "__main__":
    main()
