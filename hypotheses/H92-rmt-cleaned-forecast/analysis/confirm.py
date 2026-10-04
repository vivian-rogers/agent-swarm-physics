"""H92 confirmatory test on the locked holdout. FROZEN 2026-10-04 (round 1). DO NOT RUN without Vivian's sign-off.

Guard: runs on held-out data only with BOTH `--confirm` and the environment variable H92_CONFIRM=1, and only after
infra/shared/holdout_ledger.check() reports every target as allowed. Without them, `--dry-run` applies the same frozen
pipeline and rules to the non-holdout units (stand-ins); the dry run reads no held-out row.

Frozen design (round 1, unchanged): per-day content arrays (bge, gte) built in memory; forecasts within held-out
`period_units` units only (expanding training window), estimators E0-E6 of h92lib with the calibrated edge (49
within-day surrogates); score = off-diagonal MSE against the realized next day; per-period mean of r_k = 1 - MSE_E5/MSE_k.
Targets: held-out units of #28, #29, #45, #46, #47, #48, #49, #50 and the #51 tail (period_units holdout = True).

Frozen predictions (written 2026-10-04 after round 1; credences in brackets). They test the claim that stands:
  C1 (primary): in both embedding models, mean r_raw > 0 in >= 2/3 of held-out periods with >= 2 target days [0.75].
  C2 (primary, the shrinkage tie): in both models the mean over held-out periods of r_lwcc lies in [-0.05, +0.05]
     (RMT clipping neither beats nor loses to Ledoit-Wolf constant correlation by more than 5%) [0.6].
  C3 (RMT signature): Spearman(r_raw, q) across held-out target days > 0.3 in both models [0.6].
  Overall: CONFIRMED if C1 and C2 pass; PARTIAL if one passes; NOT CONFIRMED otherwise.
Reuse disclosure: H12 (content modes, C4 of its confirm script) plans the same held-out units with a spectral statistic.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np
import polars as pl

import h92lib as L
import run_forecast as RF

DM = L.DM
sys.path.insert(0, str(L.ROOT / "infra/shared"))
FROZEN = {"C1_share": 2 / 3, "C2_band": 0.05, "C3_rho": 0.3, "n_surr": L.N_SURR, "q_edge": L.Q_EDGE, "window": "expand"}
CH = ["content_bge", "content_gte"]
OUTC = L.OUT / "confirm"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.confirm:
        if os.environ.get("H92_CONFIRM") != "1":
            sys.exit("refused: set H92_CONFIRM=1 (Vivian's sign-off) as well as --confirm")
        import holdout_ledger as HL
        for tgt in ("G28", "G29", "G45", "G46", "G47", "G48", "G49", "G50", "#51-tail"):
            chk = HL.check("H92", tgt, "content", ["spectral_mode"])
            if not chk["allowed"]:
                sys.exit(f"refused by the holdout ledger: {tgt} {chk}")
        DM.ALLOW_HOLDOUT = True
    elif not a.dry_run:
        sys.exit("use --dry-run (non-holdout stand-ins) or --confirm with H92_CONFIRM=1")
    pu = pl.read_parquet(DM.SH / "period_units.parquet")
    held = set(pu.filter(pl.col("holdout"))["unit_id"].to_list())
    keep = (lambda u: u in held) if a.confirm else (lambda u: u not in held)
    cache = {m: DM.build_content(m) for m in DM.MODELS}
    f = RF.run(CH, loader=lambda ch: cache[ch.split("_")[1]], keep_unit=keep, seed_tag="confirm|")
    f = f.filter(pl.col("variant") == FROZEN["window"]).with_columns(
        (1 - pl.col("mse_E5_clip") / pl.col("mse_E2_raw")).alias("r_raw"),
        (1 - pl.col("mse_E5_clip") / pl.col("mse_E4_lwcc")).alias("r_lwcc"))
    res = {"mode": "confirm" if a.confirm else "dry-run (non-holdout stand-ins)", "frozen": FROZEN}
    c1, c2, c3 = [], [], []
    for ch in CH:
        x = f.filter(pl.col("channel") == ch)
        per = x.group_by("goal_no").agg(pl.len().alias("n"), pl.col("r_raw").mean(), pl.col("r_lwcc").mean()).filter(pl.col("n") >= 2)
        s1 = float((per["r_raw"] > 0).mean()) if per.height else float("nan")
        m2 = float(per["r_lwcc"].mean()) if per.height else float("nan")
        rho = L.spearman(x["r_raw"].to_numpy(), x["q"].to_numpy())
        res[ch] = {"n_periods": per.height, "n_targets": x.height, "share_r_raw_pos": s1, "mean_r_lwcc": m2, "spearman_r_raw_q": rho}
        c1.append(s1 >= FROZEN["C1_share"]); c2.append(abs(m2) <= FROZEN["C2_band"]); c3.append(rho > FROZEN["C3_rho"])
    res["C1"], res["C2"], res["C3"] = all(c1), all(c2), all(c3)
    res["overall"] = "CONFIRMED" if res["C1"] and res["C2"] else "PARTIAL" if res["C1"] or res["C2"] else "NOT CONFIRMED"
    OUTC.mkdir(parents=True, exist_ok=True)
    (OUTC / ("confirm.json" if a.confirm else "dryrun.json")).write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
