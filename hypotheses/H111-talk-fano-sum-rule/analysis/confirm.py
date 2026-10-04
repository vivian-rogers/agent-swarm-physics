"""H111 confirmatory run on the LOCKED HOLDOUT. Written and frozen 2026-10-04 after round 1; NOT RUN.

Guard: runs on held-out data only with BOTH `--confirm` and H111_CONFIRM=1, only if `holdout_ledger.check` allows every
target, and only after H67's confirmatory run has written its held-out g_lag
(data/processed/H67-lagged-criticality-dial/confirm/confirm_result.json). Otherwise it refuses.
`--dry-run` runs the identical pipeline on non-holdout stand-in units (built fresh into a scratch directory, with
H67's exploratory g_lag standing in for the confirmatory one), so the code path is tested without the holdout.

Targets (period units of): #22, #28 (regime I), #43 and the #51 tail (regime III) = H67's confirm targets.

Frozen estimator (round 1 primary after Amendment A1): talk messages of present agents (>= 20 receiving calls) in the
DQ8 all-present window; 10-min windows; per-call residual within (agent, day, 60-min block); human sessions (gaps
<= 10 min) excluded with a 10-min tail, kickoff day's first hour excluded; cell bootstrap B = 500;
Phi_pred(g_lag, rooms) with H67's confirmatory g_lag and its SE propagated.

Frozen predictions:
  C1  Sum rule (regime III): the random-effects pooled r_F = Phi(10)/Phi_pred over the #43 and #51-tail units lies in
      [0.80, 1.25] and its 95% CI includes 1.  (Round 1: 1.01 [0.94, 1.09], 18 units.)
  C2  No kill (regime III): no regime-III target unit with >= 40 windows has r_F >= 2.  (Round 1: 0/18.)
  C3  Regime-I excess (post hoc pattern from round 1, flagged): the pooled r_F over the #22 and #28 units is > 1.10.
      (Round 1: 1.34 [1.18, 1.52]; the pre-registered unit-count version, P4, failed narrowly at 62%.)
  C4  Wall-clock agreement (regime III): the pooled wall-clock r_F also lies in [0.80, 1.25].  (Round 1: 1.04.)
Reading: C1 + C2 confirm that H67's hop-1 read-out gain accounts for all regime-III collective talk variance at
10-min windows; C3 confirms an excess where the read-out gain is ~0 (field or a coupling the hop-1 clock misses).

Reuse policy (hypotheses/holdout.md): these targets are planned by H67 (C1-C4, same units; g_lag is H67's statistic,
Phi is a different statistic: windowed count covariance), H51, H99, H101 and the H25/H19 equal-time family on
#22/#28/#43. Phi on 10-min per-call residuals is a cousin of H25's equal-time VR (1-min spins): if H25/H19 run first,
disclose C1-C4 as a close cousin. Disclose in the card and LOG.md before running.

Usage:
  uv run python hypotheses/H111-talk-fano-sum-rule/analysis/confirm.py --dry-run
  H111_CONFIRM=1 uv run python hypotheses/H111-talk-fano-sum-rule/analysis/confirm.py --confirm
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
import h111lib as L  # noqa: E402

ROOT = HERE.parents[2]
SH = ROOT / "data/processed/shared"
sys.path.insert(0, str(ROOT / "infra/shared"))
OUT = ROOT / "data/processed/H111-talk-fano-sum-rule/confirm"
H67C = ROOT / "data/processed/H67-lagged-criticality-dial/confirm/confirm_result.json"
H67X = ROOT / "data/processed/H67-lagged-criticality-dial/results/units.parquet"
SCRATCH = Path(os.environ.get("TMPDIR", "/tmp")) / "h111_confirm_dryrun"
TARGET_GOALS = {22: "I", 28: "I", 43: "III", 51: "III"}
STANDINS = {"27": "I", "24": "I", "42b": "III", "51h": "III"}
FROZEN = dict(T=10, clock="percall", exo="session10", B=500, C1=(0.80, 1.25), C2=2.0, C3=1.10, C4=(0.80, 1.25),
              minwin=40)


def stats_for(base: Path, uid: str, g: float, g_se: float) -> dict:
    out = {}
    for clock in ("percall", "wall"):
        L.CLOCK, L.EXO_RULE, L.T_STAR = clock, FROZEN["exo"], FROZEN["T"]
        U = L.load_unit(uid, base)
        r = L.unit_stats(U, g=g, g_se=g_se, B=FROZEN["B"], seed=7, variants=False)
        out[clock] = r
    L.CLOCK = FROZEN["clock"]
    return out


def pool_log(rf, se):
    m, lo, hi, _ = L.re_pool(np.log(np.asarray(rf, float)), np.asarray(se, float))
    return {"r_F": math.exp(m), "lo": math.exp(lo), "hi": math.exp(hi)} if math.isfinite(m) else {"r_F": np.nan}


def score(rows: list) -> dict:
    df = pl.DataFrame(rows)
    ok = df.filter(pl.col("nwin") >= FROZEN["minwin"])
    r3, r1 = ok.filter(pl.col("regime") == "III"), ok.filter(pl.col("regime") == "I")
    p3 = pool_log(r3["r_F"], r3["se"])
    p3w = pool_log(r3["r_F_wall"], r3["se_wall"])
    p1 = pool_log(r1["r_F"], r1["se"])
    lo, hi = FROZEN["C1"]
    out = {"C1": bool(lo <= p3["r_F"] <= hi and p3["lo"] <= 1 <= p3["hi"]), "C1_detail": p3,
           "C2": bool((r3["r_F"] < FROZEN["C2"]).all()), "C3": bool(p1.get("r_F", np.nan) > FROZEN["C3"]),
           "C3_detail": p1, "C4": bool(FROZEN["C4"][0] <= p3w["r_F"] <= FROZEN["C4"][1]), "C4_detail": p3w,
           "units": df.to_dicts()}
    return out


def run(units: dict, base: Path, g_of: dict) -> list:
    rows = []
    for uid, reg in units.items():
        g, gse = g_of[uid]
        s = stats_for(base, uid, g, gse)
        p, w = s["percall"], s["wall"]
        rows.append({"unit": uid, "regime": reg, "nwin": p["nwin_10"], "phi": p["phi_10"], "phi_pred": p.get("phi_pred"),
                     "r_F": p.get("r_F"), "se": p.get("r_F_se_log"), "r_F_wall": w.get("r_F"),
                     "se_wall": w.get("r_F_se_log"), "g": g})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    pu = pl.read_parquet(SH / "period_units.parquet")
    cal = pl.read_parquet(SH / "calendar.parquet")
    if a.dry_run:
        # stand-ins rebuilt from shared tables into scratch (code path identical; names absent from scratch)
        SCRATCH.mkdir(parents=True, exist_ok=True)
        cw, lt, cc, kk, cal_, gp = B.load_shared(allow_holdout=False)
        for u in pu.filter(pl.col("unit_id").is_in(list(STANDINS))).to_dicts():
            B.build_unit(u, cw, lt, cc, kk, cal_, gp, out=SCRATCH, allow_holdout=False)
        gx = pl.read_parquet(H67X).filter(pl.col("unit_id").is_in(list(STANDINS)))
        g_of = {r["unit_id"]: (r["g"], r["g_se"]) for r in gx.iter_rows(named=True)}
        out = score(run(STANDINS, SCRATCH, g_of))
        (SCRATCH / "confirm_dryrun.json").write_text(json.dumps({"sha256": sha, "dry_run": True, **out}, indent=1,
                                                                default=float))
        print(json.dumps({k: v for k, v in out.items() if k != "units"}, indent=1, default=float))
        return
    if not (a.confirm and os.environ.get("H111_CONFIRM") == "1"):
        sys.exit("refusing: confirmatory run needs --confirm and H111_CONFIRM=1 (Vivian's sign-off)")
    if not H67C.exists():
        sys.exit("refusing: H67's confirmatory g_lag (confirm_result.json) does not exist; run H67's confirm first")
    import holdout_ledger as HL
    for g in TARGET_GOALS:
        tgt = "#51-tail" if g == 51 else f"G{g}"
        chk = HL.check("H111", tgt, "talk", ["sum_rule_fano", "curie_weiss_gain"])
        if not chk["allowed"]:
            sys.exit(f"refusing: holdout ledger blocks {tgt}: {chk['prior_runs_same_family']}")
    h67 = json.loads(H67C.read_text())
    g_of = {u["unit"]: (u["g"], u.get("g_se") or 0.0) for u in h67["units"] if u.get("ok")}
    held = pu.filter(pl.col("holdout") & pl.col("goal_no").is_in(list(TARGET_GOALS)))
    cw, lt, cc, kk, cal_, gp = B.load_shared(allow_holdout=True)
    units = {}
    for u in held.to_dicts():
        if u["unit_id"] not in g_of:
            continue
        if B.build_unit(u, cw, lt, cc, kk, cal_, gp, out=OUT, allow_holdout=True):
            units[u["unit_id"]] = TARGET_GOALS[u["goal_no"]]
    out = score(run(units, OUT, g_of))
    (OUT / "confirm_result.json").write_text(json.dumps({"sha256": sha, **out}, indent=1, default=float))
    print(json.dumps({k: v for k, v in out.items() if k != "units"}, indent=1, default=float))


if __name__ == "__main__":
    main()
