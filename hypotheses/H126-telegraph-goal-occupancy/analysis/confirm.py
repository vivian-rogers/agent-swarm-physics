"""H126 confirmatory run on the LOCKED HOLDOUT. Written and frozen 2026-10-04 after round 1; NOT RUN.

Guard: the held-out path runs only with BOTH `--confirm` and H126_CONFIRM=1, only if this file's SHA-256 matches
`confirm.sha256` (written at freeze), only if `holdout_ledger.check` allows every target, and it writes only under
data/processed/H126-telegraph-goal-occupancy/confirm/. `--dry-run` runs the identical pipeline on non-holdout stand-in
periods (built fresh into a scratch folder whose path contains 'confirm_dry'), so the code path is tested without the
holdout. Nothing held out is read in a dry run.

Targets (assigned held-out goal periods; free weeks #9, #22 and #51 excluded): #1, #14, #15, #28, #29, #32, #34, #43,
#45, #46, #47, #48, #49, #50. Units are the shared period_units of those periods (eligibility as in round 1: >= 3 agents
with >= 30 deduplicated statements and >= 10 in each day fold).

Frozen estimator (round 1 after Amendment A1): bge_small white32 decoy-threshold labels (95th percentile of non-holdout
same-regime decoys), self-repeat copies dropped, call clock, per-agent HMM with jointly fitted emissions; kickoff
designs (F = last <= 5 active days of g-1, A = first unit of g; assigned destinations; >= 3 agents with >= 20
statements per segment) fitted with segment rates and a 200-draw agent-cluster bootstrap (90% CIs).

Frozen predictions (round-1 numbers in brackets):
  C1 (primary): Delta ln k_off 90% CI below 0 in >= 2/3 of testable held-out kickoff designs. [15/17]  Credence 0.75.
  C2: the HH's one-rate field fails again: verdict 'k_on' (k_on up, k_off CI containing 0) in < 1/3 of testable
      designs. [2/17]  Credence 0.75.
  C3: the call clock beats the wall clock (held-out-day dLL > 0) in >= 2/3 of eligible regime-III held-out units. [9/11]
      Credence 0.65.
  C4 (consistency, P2 kill): |rho_p| > ln 1.3 in <= 1/2 of eligible held-out units. [5/39]  Credence 0.85.
  Descriptive: P1 heavy-tailed count (not identifiable, Amendment A1).
Reading: C1 + C2 confirm that a goal kickoff lowers k_off (it holds agents on goal), not only raises k_on.
Usage:
  uv run --with numba python hypotheses/H126-telegraph-goal-occupancy/analysis/confirm.py --dry-run
  H126_CONFIRM=1 uv run --with numba python hypotheses/H126-telegraph-goal-occupancy/analysis/confirm.py --confirm
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import build as B  # noqa: E402
import h126lib as L  # noqa: E402

ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
D = ROOT / "data/processed/H126-telegraph-goal-occupancy"
OUT = D / "confirm"
SCRATCH = Path(os.environ.get("TMPDIR", "/tmp")) / "h126_confirm_dry"
TARGETS = [1, 14, 15, 28, 29, 32, 34, 43, 45, 46, 47, 48, 49, 50]
STANDINS = [13, 25, 27, 41]   # stand-ins with kickoff designs K13, K25, K27, K41
FROZEN = dict(B_null=30, n_sim=100, qmode="free", variant="bge", dedupe=True, B_seg=200, min_seg=20,
              C1_share=2 / 3, C2_share=1 / 3, C3_share=2 / 3, C4_share=1 / 2)


def unit_stats(stmts: pl.DataFrame, design: str, rng) -> dict:
    df = stmts.filter(pl.col("design") == design)
    S, meta = L.design_seq(df, variant=FROZEN["variant"], dedupe=FROZEN["dedupe"])
    if S is None:
        return dict(design=design, eligible=False)
    r = L.evaluate_unit(S, meta, rng, n_sim=FROZEN["n_sim"], qmode=FROZEN["qmode"])
    if not r.get("eligible"):
        return dict(design=design, eligible=False)
    null = L.bootstrap_shape_null(r["_S"], r["_meta"], r["_fit2"], rng, B=FROZEN["B_null"], qmode=FROZEN["qmode"])
    p1, q95 = L.p1_verdict(r["dll4_held"], null, r["cv_on"], r["cv_off"])
    return dict(design=design, eligible=True, n_agents=r["n_agents"], n_stmt=r["n_stmt"], dll4_held=r["dll4_held"],
                null_q95=q95, cv_on=r["cv_on"], cv_off=r["cv_off"], P1=p1, rho_p=r["rho_p"], p_dw=r["p_dw"],
                p_win=r["p_win"], tau_on_med=r["tau_on_med"], tau_off_med=r["tau_off_med"], q0=r["q0"], q1=r["q1"],
                dllw_held=r["dllw_held"])


def kick_stats(stmts: pl.DataFrame, design: str, rng) -> dict:
    df = stmts.filter(pl.col("design") == design)

    def build(fr):
        S, m = L.design_seq(fr, rg_mode="seg", seg_split=True, min_seg=FROZEN["min_seg"])
        if S is None or len(m["segs"]) < 2:
            return None
        if m["segs"].index("F") != 0:
            S.rg[:] = 1 - S.rg
        return S
    S = build(df)
    if S is None:
        return dict(design=design, eligible=False)
    S0, m0 = L.design_seq(df, rg_mode="seg", seg_split=True, min_seg=FROZEN["min_seg"])
    if len(m0["agents"]) < 3:
        return dict(design=design, eligible=False, n_agents=len(m0["agents"]))
    f = L.fit2(S)
    dla, dlb = math.log(f["a"][1] / f["a"][0]), math.log(f["b"][1] / f["b"][0])
    bs = L.seg_bootstrap(m0["frame"], build, rng, B=FROZEN["B_seg"])
    lo, hi = np.percentile(bs, 5, axis=0), np.percentile(bs, 95, axis=0)
    k_on = bool(lo[0] > 0 and lo[1] <= 0 <= hi[1])
    return dict(design=design, eligible=True, n_agents=len(m0["agents"]), dln_a=dla, dln_b=dlb, a_lo=float(lo[0]),
                a_hi=float(hi[0]), b_lo=float(lo[1]), b_hi=float(hi[1]), koff_down=bool(hi[1] < 0), k_on_only=k_on)


def score(rows: list, krows: list, regime: dict) -> dict:
    el = [r for r in rows if r.get("eligible")]
    kel = [k for k in krows if k.get("eligible")]
    out = dict(n_units=len(el), n_kick=len(kel))
    if kel:
        down = sum(k["koff_down"] for k in kel)
        kon = sum(k["k_on_only"] for k in kel)
        out.update(n_koff_down=down, n_kon_only=kon, C1=bool(down >= FROZEN["C1_share"] * len(kel)),
                   C2=bool(kon < FROZEN["C2_share"] * len(kel)))
    else:
        out.update(C1="untestable", C2="untestable")
    r3 = [r for r in el if regime.get(r["design"]) == "III"]
    if r3:
        cw = sum(r["dllw_held"] > 0 for r in r3)
        out.update(n_regIII=len(r3), n_call_wins=cw, C3=bool(cw >= FROZEN["C3_share"] * len(r3)))
    else:
        out["C3"] = "untestable"
    if el:
        off = sum(abs(r["rho_p"]) > math.log(1.3) for r in el)
        out.update(n_off30=off, C4=bool(off <= FROZEN["C4_share"] * len(el)),
                   n_heavy_descriptive=sum(r["P1"] == "heavy" for r in el))
    else:
        out["C4"] = "untestable"
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    rng = np.random.default_rng(20261005)
    if a.dry_run:
        SCRATCH.mkdir(parents=True, exist_ok=True)
        B.main(allow_holdout=False, out_dir=SCRATCH, natives=True)
        st = pl.read_parquet(SCRATCH / "stmts.parquet")
        des0 = pl.read_parquet(SCRATCH / "designs.parquet").filter(pl.col("goal_no").is_in(STANDINS))
        des = des0.filter(pl.col("kind") == "unit")
        kd = des0.filter((pl.col("kind") == "kickoff") & (pl.col("mode") != "F"))
        rows = [unit_stats(st, d, rng) for d in des["design"].to_list()]
        krows = [kick_stats(st, d, rng) for d in kd["design"].to_list()]
        out = score(rows, krows, dict(zip(des0["design"], des0["regime"])))
        out["kick"] = krows
        (SCRATCH / "confirm_dryrun.json").write_text(json.dumps(dict(sha256=sha, dry_run=True, standins=STANDINS,
                                                                     units=rows, **out), indent=1, default=float))
        print(json.dumps(out, indent=1, default=float))
        return
    if not (a.confirm and os.environ.get("H126_CONFIRM") == "1"):
        sys.exit("refusing: confirmatory run needs --confirm and H126_CONFIRM=1 (Vivian's sign-off)")
    shaf = HERE / "confirm.sha256"
    if not shaf.exists() or shaf.read_text().strip() != sha:
        sys.exit("refusing: confirm.py differs from its frozen SHA-256 (confirm.sha256)")
    import holdout_ledger as HL
    for g in TARGETS:
        chk = HL.check("H126", f"G{g}", "content", ["content_alignment", "behavior_states"])
        if not chk["allowed"]:
            sys.exit(f"refusing: holdout ledger blocks G{g}: {chk['prior_runs_same_family']}")
    OUT.mkdir(parents=True, exist_ok=True)
    B.main(allow_holdout=True, target_goals=TARGETS, out_dir=OUT, natives=False)
    st = pl.read_parquet(OUT / "stmts.parquet")
    des0 = pl.read_parquet(OUT / "designs.parquet").filter(pl.col("goal_no").is_in(TARGETS))
    des = des0.filter(pl.col("kind") == "unit")
    kd = des0.filter((pl.col("kind") == "kickoff") & (pl.col("mode") != "F"))
    rows = [unit_stats(st, d, rng) for d in des["design"].to_list()]
    krows = [kick_stats(st, d, rng) for d in kd["design"].to_list()]
    out = score(rows, krows, dict(zip(des0["design"], des0["regime"])))
    out["kick"] = krows
    (OUT / "confirm_result.json").write_text(json.dumps(dict(sha256=sha, dry_run=False, units=rows, **out), indent=1,
                                                        default=float))
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
