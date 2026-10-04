"""H66 confirmatory test on the locked holdout. FROZEN 2026-10-04 (round 1). DO NOT RUN without Vivian's sign-off.

Guard: held-out data are read only with BOTH `--confirm` and H66_CONFIRM=1, after infra/shared/holdout_ledger.check().
Without them, the default dry run applies the frozen rules to the non-holdout round-1 unit table (stand-ins).

Design (frozen): the round-1 scheme (scheme/build.py logic, act-call spins, chained-call turnaround) and estimator
(h66lib.analyze_grid, R = 99, K = 20, B = 200, all-present window, field kernel 0-5 min) on every held-out regime-III
`period_units` unit with >= 4 agents (held-out goal periods #43, #45-#50 and the #51 tail), plus the post hoc
load-sign statistic corr(L, K) (latency field vs active count, block-demeaned) promoted to a frozen test.

Frozen predictions (written 2026-10-04 after round 1; credences in brackets):
  C1 (primary; load, not drive): corr(L, K) > 0 in >= 80% of held-out units, and > 0 in every unit with a
     significant E [0.75].
  C2 (primary; not a provider field): in units with a significant latency field (block-shift p <= 0.05), median
     same-lab rho_lat < 2 x median cross-lab rho_lat [0.75].
  C3: residual trimmed co-activation E significant (p < 0.05) in <= 1/3 of held-out units [0.7].
  C4: rho_lat grows with N across held-out units (Spearman rho > 0) [0.55].
  Overall: CONFIRMED if C1 and C2 pass; PARTIAL if one; NOT CONFIRMED otherwise.
Reuse disclosure: #45 was used by H02 and H04 (activity timing) and is planned by many; H66's statistics (call
turnaround co-movement and its relation to the active count) are a different modality (latency) from those runs.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "data/processed/H66-platform-latency-field"


def judge(t: pl.DataFrame) -> dict:
    t = t.filter(pl.col("eligible"))
    c1 = (t["corr_LK"] > 0).mean() >= 0.8 and bool((t.filter(pl.col("sig_E"))["corr_LK"] > 0).all())
    s = t.filter(pl.col("p_lat") <= 0.05)
    c2 = s.height > 0 and float(s["rho_same_lab"].median()) < 2 * float(s["rho_cross_lab"].median())
    c3 = float(t["sig_E"].mean()) <= 1 / 3
    from scipy.stats import spearmanr
    c4 = float(spearmanr(t["N"], t["rho_lat"]).statistic) > 0 if t.height >= 3 else False
    return {"C1": bool(c1), "share_pos_corr_LK": float((t["corr_LK"] > 0).mean()), "C2": bool(c2),
            "same_lab_med": float(s["rho_same_lab"].median()) if s.height else None,
            "cross_lab_med": float(s["rho_cross_lab"].median()) if s.height else None, "C3": bool(c3),
            "share_sig_E": float(t["sig_E"].mean()), "C4": bool(c4), "n_units": t.height,
            "overall": "CONFIRMED" if (c1 and c2) else "PARTIAL" if (c1 or c2) else "NOT CONFIRMED"}


def dry_run():
    t = pl.read_parquet(OUT / "replication" / "unit_table.parquet").filter(pl.col("regime") == "III")
    out = judge(t)
    (OUT / "confirm_dryrun").mkdir(exist_ok=True)
    (OUT / "confirm_dryrun" / "confirm.json").write_text(json.dumps({"stand_in": "non-holdout regime-III units", **out}, indent=1))
    print(json.dumps(out, indent=1))


def confirm():
    if os.environ.get("H66_CONFIRM") != "1":
        sys.exit("refused: set H66_CONFIRM=1 (and have Vivian's sign-off)")
    sys.path.insert(0, str(ROOT / "infra/shared"))
    import holdout_ledger  # noqa: E402
    for tgt in ["G43", "G45", "G46", "G47", "G48", "G49", "G50", "#51-tail", "NE21+NE23"]:
        st = holdout_ledger.check("H66", tgt, "call latency (turnaround)", None)
        if not st.get("allowed", True):
            sys.exit(f"refused by holdout ledger for {tgt}: {st}")
    cdir = OUT / "confirm"
    sys.path.insert(0, str(ROOT / "hypotheses/H66-platform-latency-field/scheme"))
    sys.path.insert(0, str(HERE))
    import build  # noqa: E402
    import h66lib as L  # noqa: E402
    import summarize as SM  # noqa: E402
    build.main(holdout_units=True, out=cdir)
    SM.OUT = cdir
    units = pl.read_parquet(cdir / "units.parquet")
    rows = []
    for u in units.iter_rows(named=True):
        g = pl.read_parquet(cdir / "grid" / f"{u['unit_id']}.parquet")
        r = L.analyze_grid(g, seed=hash(u["unit_id"]) % (2**31), R=99, K=20, B=200, full=False)
        if r is None or r["n_agents"] < 4:
            rows.append({"unit": u["unit_id"], "eligible": False})
            continue
        cLK, _, _ = SM.load_sign(u["unit_id"])
        b, ls = r["binary"], r["lat_strength"]
        rows.append({"unit": u["unit_id"], "eligible": True, "N": r["n_agents"], "sig_E": b["p_E"] < 0.05, "E": b["E"],
                     "delta_f": b["delta_f"], "rho_lat": ls["all"]["rho"], "p_lat": ls["all"]["p"],
                     "rho_same_lab": ls["same_lab"]["rho"], "rho_cross_lab": ls["cross_lab"]["rho"], "corr_LK": cLK})
    t = pl.DataFrame(rows, infer_schema_length=None)
    t.write_parquet(cdir / "unit_table.parquet")
    out = judge(t)
    (cdir / "confirm.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))
    print("record the run: holdout_ledger.record_run(<entry id>, evidence=<this file + LOG.md date>)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    a = ap.parse_args()
    confirm() if a.confirm else dry_run()
