"""H85 confirmatory test on the locked holdout. WRITTEN 2026-10-04 after round 1, NOT RUN on the holdout.

  uv run python hypotheses/H85-output-scaling-with-n/analysis/confirm.py --dry-run
      runs the full pipeline on the 71 non-holdout units (exploration data only) and prints what it would score.
  uv run python hypotheses/H85-output-scaling-with-n/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
      rebuilds the unit table with held-out rows in memory (scheme/build.py, include_holdout=True), keeps ONLY the
      held-out units (period_units.holdout), writes confirm/confirm_sealed.json (SHA-256 of the frozen predictions)
      BEFORE reading any held-out row, then fits and scores. Refuses without BOTH flags; checks the holdout ledger.

Round-1 picture under test: messages scale sublinearly with the active population (agents talk less as the room
fills; regime I keeps a nearly fixed room talk budget), addressing per message rises with N at least as fast as H18's
dilution predicts from the pending set, reply parents per message do not rise with N (one-parent budget).

Targets: held-out period units (goal periods #1, #9, #14, #15, #22, #28, #29, #32, #34, #43, #45-#50 and the NE-window
units that period_units marks holdout). Fit on the held-out units only (M1: regime intercepts, goal-cluster bootstrap).
Frozen predictions:
  C1 messages sublinear: beta_msg < 0.85 and its cluster-CI upper bound < 1.10.
  C2 addressing aggregates: Delta_beta_ment (M1 slope of ln(ment/msg)) CI excludes 0, and the CI of
     Delta_beta_ment - 0.34 gamma_k (joint bootstrap) contains 0.
  C3 reply parents saturate: slope of ln(reply/msg) < 0.20 with its CI containing 0.
  C4 regime-I talk budget (regime-I held-out units only, descriptive if < 5 units): slope of ln(talk calls / calls)
     on ln N < -0.5.
  Overall: CONFIRMED if C1 and C2 pass.
Reuse disclosure: held-out goal periods are targeted by many unrun scripts (see infra/data-quality/holdout_ledger.json);
H85's modality is unit-level output totals (messages, mentions, reply parents) — family "dilution_addressing" overlaps
H18's confirm script on the same targets; disclose in both cards and LOG.md if both run.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h85lib as L  # noqa: E402

OUTD = L.DATA / "confirm"
PRED = {"C1": "beta_msg < 0.85 and CI hi < 1.10 (held-out units, M1, goal-cluster bootstrap)",
        "C2": "Delta_beta_ment CI excludes 0 and CI of Delta_beta_ment - 0.34 gamma_k contains 0",
        "C3": "slope ln(reply/msg) < 0.20 with CI containing 0",
        "C4": "regime-I held-out units: slope ln(talk/calls) < -0.5 (descriptive if < 5 units)",
        "overall": "C1 & C2"}
B = 2000


def score(u: pl.DataFrame, calls: pl.DataFrame | None, rng) -> dict:
    u = u.filter((pl.col("T_h") >= 1) & (pl.col("msg") >= 20) & (pl.col("ment") > 0) & (pl.col("reply") > 0)
                 & (pl.col("k_n") > 0))
    lnN, reg, cl = np.log(u["N"].to_numpy()), u["regime"].to_numpy(), u["goal_no"].to_numpy()
    ys = {"msg": np.log(u["msg"].to_numpy() / u["T_h"].to_numpy()), "ment_per_msg": np.log(u["ment"].to_numpy() / u["msg"].to_numpy()),
          "reply_per_msg": np.log(u["reply"].to_numpy() / u["msg"].to_numpy()), "k": np.log(u["k_talk"].to_numpy())}
    X = L.design(lnN, reg)[0]
    pt = {k: float(L.ols(X, y)[0]) for k, y in ys.items()}
    groups = sorted(set(cl))
    idx = {g: np.where(cl == g)[0] for g in groups}
    bs = {k: [] for k in ys}
    for _ in range(B):
        ii = np.concatenate([idx[groups[p]] for p in rng.choice(len(groups), len(groups))])
        for k, y in ys.items():
            bs[k].append(L.ols(X[ii], y[ii])[0])
    q = lambda a: [float(np.nanquantile(a, 0.025)), float(np.nanquantile(a, 0.975))]  # noqa: E731
    bs = {k: np.asarray(v) for k, v in bs.items()}
    d = bs["ment_per_msg"] - (1 - L.BETA_D) * bs["k"]
    res = {"n_units": u.height, "n_goals": len(groups), "est": pt, "ci": {k: q(v) for k, v in bs.items()},
           "dment_minus_pred_ci": q(d)}
    res["C1"] = bool(pt["msg"] < 0.85 and res["ci"]["msg"][1] < 1.10)
    res["C2"] = bool((res["ci"]["ment_per_msg"][0] > 0 or res["ci"]["ment_per_msg"][1] < 0)
                     and res["dment_minus_pred_ci"][0] <= 0 <= res["dment_minus_pred_ci"][1])
    res["C3"] = bool(pt["reply_per_msg"] < 0.20 and res["ci"]["reply_per_msg"][0] <= 0 <= res["ci"]["reply_per_msg"][1])
    if calls is not None:
        v = u.join(calls, on="unit_id").filter(pl.col("regime") == "I")
        if v.height >= 2:
            s = float(L.ols(L.design(np.log(v["N"].to_numpy()), None)[0],
                            np.log(v["talk_calls"].to_numpy() / v["calls_all"].to_numpy()))[0])
            res["C4"] = {"slope": s, "n_units": v.height, "pass": bool(s < -0.5), "descriptive": v.height < 5}
    res["overall"] = bool(res["C1"] and res["C2"])
    return res


def calls_table(Bld, include_holdout: bool) -> pl.DataFrame:
    """All model calls per unit (call_windows rows by t_call, Claude Code agents excluded)."""
    sh = L.ROOT / "data/processed/shared"
    units = Bld.load_units(include_holdout)
    cc = pl.read_parquet(sh / "roster.parquet").filter(pl.col("claude_code"))["agent"].to_list()
    cw = (pl.scan_parquet(sh / "call_windows.parquet").select("agent", pl.col("t_call").alias("t")).collect()
          .filter(pl.col("t").is_not_null() & ~pl.col("agent").is_in(cc)))
    return Bld.assign(cw, units).group_by("unit_id").agg(pl.len().alias("calls_all"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    a = ap.parse_args()
    rng = np.random.default_rng(20261008)
    OUTD.mkdir(parents=True, exist_ok=True)
    import build as Bld  # scheme/build.py
    if a.dry_run and not a.confirm:
        u, *_ = Bld.build(include_holdout=False)
        calls = calls_table(Bld, False)
        res = {"mode": "dry-run (non-holdout units)", "predictions": PRED, **score(u, calls, rng)}
        (OUTD / "confirm_dryrun.json").write_text(json.dumps(res, indent=1, default=float))
        print(json.dumps(res, indent=1, default=float))
        return
    if not (a.confirm and a.ack):
        sys.exit("refusing: confirmatory runs need --confirm AND --i-understand-this-uses-the-locked-holdout "
                 "(and Vivian's sign-off)")
    sys.path.insert(0, str(L.ROOT / "infra" / "shared"))
    import holdout_ledger as HL
    pu = pl.read_parquet(L.ROOT / "data/processed/shared/period_units.parquet").filter(pl.col("holdout"))
    for g in sorted(set(pu["goal_no"].to_list())):
        chk = HL.check("H85", f"G{g:02d}", "unit output totals", "dilution_addressing")
        if not chk["allowed"]:
            sys.exit(f"ledger refuses G{g:02d}: {chk['prior_runs_same_family']}")
        if chk["needs_disclosure"]:
            print(f"G{g:02d}: disclosure needed (prior/competing uses)")
    sealed = {"hypothesis": "H85", "sealed_at": dt.datetime.now(dt.timezone.utc).isoformat(), "predictions": PRED,
              "sha256": hashlib.sha256(json.dumps(PRED, sort_keys=True).encode()).hexdigest()}
    (OUTD / "confirm_sealed.json").write_text(json.dumps(sealed, indent=1))
    u, *_ = Bld.build(include_holdout=True)
    u = u.filter(pl.col("unit_id").is_in(pu["unit_id"].to_list()))
    res = {"mode": "CONFIRMATORY (held-out units only)", "sealed": sealed, **score(u, calls_table(Bld, True), rng)}
    (OUTD / "confirm_result.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
