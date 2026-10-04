"""H123 confirmatory tests on the LOCKED HOLDOUT. Written after exploratory round 1 (2026-10-04); NOT RUN.

Guard: the holdout is touched only with BOTH flags, a clean git state for H123's code, and a holdout-ledger check:
  uv run python hypotheses/H123-regime1-turn-sweep/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
Without the flags the script prints the frozen predictions and exits. `--dry-run` runs the full pipeline on two
non-holdout stand-in units relabelled with names absent from the exploration files (lesson from H13), writes nothing.

Targets: the held-out regime-I goal periods #9, #14, #15, #22, #28, #29 (their period_units with >= 2 days for the EP
clauses; every unit for the audit clauses).
  C1  audit: no unit is classified sweep, and >= 2/3 of units are self-clocked asynchronous (kappa_par >= 0.3,
      eta_ord < 0.2).                                   round 1: 41/41 self-clocked, eta_ord <= 0.125, kappa >= 0.67
  C2  state dependence is weak: L_name < 1.5 in every unit.          round 1: max 1.32
  C3  the order makes no EP: |sigma_sweep - sigma_rand| < 1e-3 nats/step at lags 2 and 4 (talk) in every EP unit.
                                                                    round 1: median 2e-5; max 1.9e-3, all > 1e-3 in
      units with < 7,000 steps (frozen at 3e-3 there, where the simulation SD is larger)
  C4  sigma_x(talk) above the A1 floor (block-flip q95 and sigma_rand q95) in <= 25% of EP units at every lag.
                                                                    round 1: 2/31 units (6%) at each lag
Reuse: regime-I held-out periods are planned by H81 (content, culture family), H99/H101 (#22, #28; curie_weiss_gain,
multi_information), H67 (#22, #28), H51 (#22, #28). H123's statistics (call-order audit; event-time EP with simulated
sweep predictions) are a new modality/family ("scheduler_order", "entropy_production"); the ledger check decides;
disclose in both cards and LOG.md.
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
import h123lib as L  # noqa: E402
import run as RUN  # noqa: E402
import build as B  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))

FROZEN = {  # frozen 2026-10-04 after exploratory round 1 (card, "Confirmatory predictions")
    "goals": [9, 14, 15, 22, 28, 29],
    "estimator": "held-out Newton (ep_newton, c=1, family blocks); A1 floor = max(block-flip q95, sigma_rand q95)",
    "n_floor": 30, "reps": 20, "lags": [1, 2, 4],
    "C1_min_share_selfclocked": 2 / 3, "C1_eta_max": 0.2, "C1_kappa_min": 0.3,
    "C2_Lname_max": 1.5,
    "C3_sweep_minus_rand_max": 1e-3, "C3_small_unit_max": 3e-3, "C3_small_unit": {"steps_max": 7000},
    "C4_max_share_above": 0.25,
}
FILES = ["hypotheses/H123-regime1-turn-sweep/analysis/confirm.py",
         "hypotheses/H123-regime1-turn-sweep/analysis/h123lib.py",
         "hypotheses/H123-regime1-turn-sweep/analysis/run.py",
         "hypotheses/H123-regime1-turn-sweep/scheme/build.py"]


def git_clean() -> bool:
    out = subprocess.run(["git", "-C", str(L.ROOT), "status", "--porcelain", "--", *FILES], capture_output=True,
                         text=True).stdout
    return out.strip() == ""


def evaluate(steps: dict, n_floor: int, reps: int) -> dict:
    res = {}
    for u, S in steps.items():
        rng = np.random.default_rng(abs(hash(("H123c", u))) % (1 << 30))
        nd = S["day"].n_unique()
        ln = L.name_lift(S, rng=rng, n_null=50, boot_days=200 if nd >= 2 else 0)
        st = L.audit_unit(S, "all", n_shuffle=50, seed=1)
        r = {"class": L.classify(st, ln), "eta": st.get("eta"), "kappa": st.get("kappa_par"), "L_name": ln["L_name"],
             "n_days": nd}
        if nd >= 2:
            ep = RUN.unit_channel(S, "talk", n_floor, reps, rng)
            if ep is not None:
                r["ep"] = {k: v for k, v in ep.items() if not isinstance(v, list)}
        res[u] = r
    return res


def decide(res: dict) -> dict:
    F = FROZEN
    units = list(res)
    selfc = [u for u in units if res[u]["class"] == "self-clocked asynchronous" and res[u]["eta"] < F["C1_eta_max"]
             and res[u]["kappa"] >= F["C1_kappa_min"]]
    c1 = (not any(res[u]["class"] == "sweep" for u in units)) and len(selfc) >= F["C1_min_share_selfclocked"] * len(units)
    c2 = all(res[u]["L_name"] < F["C2_Lname_max"] for u in units)
    epu = [u for u in units if "ep" in res[u]]
    c3 = True
    for u in epu:
        e = res[u]["ep"]
        small = e["T"] < F["C3_small_unit"]["steps_max"]
        lim = F["C3_small_unit_max"] if small else F["C3_sweep_minus_rand_max"]
        c3 &= all(abs(e[f"sweep_x{lag}"] - e[f"rand_x{lag}"]) < lim for lag in (2, 4))
    c4 = all(np.mean([res[u]["ep"][f"above{lag}"] for u in epu]) <= F["C4_max_share_above"] for lag in F["lags"]) \
        if epu else None
    return {"C1": bool(c1), "C2": bool(c2), "C3": bool(c3) if epu else None, "C4": c4, "n_units": len(units),
            "n_ep_units": len(epu)}


def targets(allow_holdout: bool) -> pl.DataFrame:
    pu = pl.read_parquet(L.ROOT / "data/processed/shared/period_units.parquet")
    return pu.filter(pl.col("goal_no").is_in(FROZEN["goals"]) & (pl.col("regime") == "I"))


def run():
    import holdout_ledger as HL
    for g in FROZEN["goals"]:
        chk = HL.check("H123", f"G{g:02d}", "call_windows+chat_mentions", ["entropy_production"])
        print(f"G{g:02d}", "allowed" if chk["allowed"] else "NOT ALLOWED", "disclosure needed" if chk["needs_disclosure"] else "")
        if not chk["allowed"]:
            raise SystemExit("holdout ledger refuses a same-family reuse: ask the coordinator")
    steps, _ = B.make_steps(targets(True), allow_holdout=True)
    res = evaluate(steps, FROZEN["n_floor"], FROZEN["reps"])
    out = {"results": res, **decide(res)}
    d = L.OUT / "confirm"
    d.mkdir(exist_ok=True)
    (d / "confirm_results.json").write_text(json.dumps(out, indent=1, default=float))
    print({k: out[k] for k in ("C1", "C2", "C3", "C4", "n_units", "n_ep_units")})


def dry_run():
    """Pipeline check on two non-holdout units under stand-in names; small reps; nothing written."""
    pu = pl.read_parquet(L.ROOT / "data/processed/shared/period_units.parquet")
    U = pu.filter(pl.col("unit_id").is_in(["5", "26"]))
    steps, _ = B.make_steps(U, allow_holdout=False)
    steps = {f"STANDIN_{k}": v for k, v in steps.items()}
    res = evaluate(steps, 5, 3)
    print({u: {k: (v if not isinstance(v, dict) else "ep ok") for k, v in r.items()} for u, r in res.items()})
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
        print("H123 confirm.py: frozen predictions (not run):")
        for k, v in FROZEN.items():
            print(f"  {k}: {v}")
        print("Pass --confirm --i-understand-this-uses-the-locked-holdout to run on the holdout.")
        return
    if not git_clean():
        raise SystemExit("commit H123's code first (predictions and script must be committed before a confirmatory run)")
    run()


if __name__ == "__main__":
    main()
