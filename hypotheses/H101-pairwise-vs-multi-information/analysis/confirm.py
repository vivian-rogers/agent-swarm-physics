"""H101 confirmatory run on the LOCKED HOLDOUT. Written and frozen 2026-10-04 after round 1; NOT RUN.

Guard: runs on held-out data only with BOTH `--confirm` and H101_CONFIRM=1, and only if `holdout_ledger.check` allows
every target. Otherwise it refuses. `--dry-run` runs the identical estimator and scoring on non-holdout stand-in units
(already built) and writes to a scratch directory.

Targets: goal periods #22 and #28 (regime I) and #43 (regime III); family: conventions (H34 marker classes N, W, D),
re-extracted for the held-out rows with idea_markers.uses_for_rows(..., allow_holdout=True).
Estimator (frozen = round 1 after Amendment A1): per-day ensembles, 6-agent subsets (10 per day), K >= 1 support,
parametric-bootstrap bias correction (B = 12), remainder z against the pairwise bootstrap, latent-class field reference.

Frozen predictions (round 1: median rho_F 0.91; remainder z >= 2.33 in 83% of N >= 6 units; r_HO <= field reference
in 92%; raw I2/IN 0.95; phi 0.71 in regime I, 0.26 in regime III):
  C1  Pairs + fields capture most of the beyond-field multi-information: the median rho_F over target units with
      N_d >= 6 is >= 0.85, and no unit has rho_F < 0.8 together with z >= 2.33 and r_HO above its field reference.
  C2  The remainder is field-sized: in >= 75% of target units with z >= 2.33, r_HO <= the field reference r_HO.
  C3  Raw I2/IN >= 0.9 (median over target units).
  C4  The uniform-field share is larger in regime I than in regime III: median phi(#22, #28) - phi(#43) > 0.15.
Reading: C1 + C2 confirm "no separable group term in co-usage; the remainder is heterogeneous-field sized". C4
confirms the regime split of the field share. The egregore-positive outcome is a C1 violation.

Reuse policy (hypotheses/holdout.md): #22, #28, #43 have planned content users (H12, H26, H32, H34 and others). H101's
statistic (multi-information of marker co-usage on agent subsets) is new; H34/H61/H62 planned marker uses on these
periods (cascade statistics) are a different statistic of the same modality: disclose in the card and LOG.md.

Usage:
  uv run python hypotheses/H101-pairwise-vs-multi-information/analysis/confirm.py --dry-run
  H101_CONFIRM=1 uv run python hypotheses/H101-pairwise-vs-multi-information/analysis/confirm.py --confirm
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
import build as B  # noqa: E402
import run as R  # noqa: E402
import summarize as S  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H101-pairwise-vs-multi-information/confirm"
SCRATCH = Path(os.environ.get("TMPDIR", "/tmp")) / "h101_confirm_dryrun"
TARGET_GOALS = {22: "I", 28: "I", 43: "III"}
STANDINS = {"24": "I", "27": "I", "42b": "III"}
FROZEN = dict(C1=dict(rho_F_med=0.85, egregore_rho=0.8, z=2.33), C2=dict(share=0.75), C3=dict(raw=0.9), C4=dict(dphi=0.15))


def unit_rows(units, n_med):
    rows = []
    for u in units:
        r = R.run_unit((u, "conv", "main", False))
        if r.get("ok"):
            r["N_med"] = n_med.get(u)
            r["class"] = S.unit_class(r)
            rows.append(r)
    return rows


def score(rows, regime_of):
    keep = ("unit", "N_med", "rho_F", "phi", "r_HO", "rho_raw", "ho_excess_z", "field_r_HO", "I_N", "class")
    out = {"units": [{k: r.get(k) for k in keep} for r in rows]}
    big = [r for r in rows if (r["N_med"] or 0) >= 6]
    med = float(np.nanmedian([r["rho_F"] for r in big])) if big else np.nan
    egg = [r["unit"] for r in rows if r["class"] == "higher-order candidate"]
    out["C1"] = {"pass": bool(np.isfinite(med) and med >= FROZEN["C1"]["rho_F_med"] and not egg), "median_rho_F": med,
                 "egregore_units": egg}
    zz = [r for r in big if (r.get("ho_excess_z") or -9) >= FROZEN["C1"]["z"]]
    sh = float(np.mean([r["r_HO"] <= r["field_r_HO"] for r in zz])) if zz else np.nan
    out["C2"] = {"pass": bool(zz and sh >= FROZEN["C2"]["share"]), "share": sh, "n": len(zz)}
    raw = float(np.nanmedian([r["rho_raw"] for r in rows])) if rows else np.nan
    out["C3"] = {"pass": bool(np.isfinite(raw) and raw >= FROZEN["C3"]["raw"]), "median_raw": raw}
    pI = [r["phi"] for r in rows if regime_of[r["unit"]] == "I"]
    pIII = [r["phi"] for r in rows if regime_of[r["unit"]] == "III"]
    d = float(np.nanmedian(pI) - np.nanmedian(pIII)) if pI and pIII else np.nan
    out["C4"] = {"pass": bool(np.isfinite(d) and d > FROZEN["C4"]["dphi"]), "dphi": d}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    if a.dry_run:
        meta = pl.read_parquet(R.BASE / "unit_meta.parquet")
        n_med = dict(zip(meta["unit_id"].to_list(), meta["N_med"].to_list()))
        rows = unit_rows(list(STANDINS), n_med)
        out = score(rows, STANDINS)
        SCRATCH.mkdir(parents=True, exist_ok=True)
        (SCRATCH / "dryrun.json").write_text(json.dumps({"sha256": sha, **out}, indent=1, default=float))
        print(json.dumps({k: v for k, v in out.items() if k != "units"}, indent=1, default=float))
        return
    if not (a.confirm and os.environ.get("H101_CONFIRM") == "1"):
        sys.exit("refusing: confirmatory run needs --confirm and H101_CONFIRM=1 (Vivian's sign-off)")
    import holdout_ledger as HL
    import idea_markers as IM
    for g in TARGET_GOALS:
        chk = HL.check("H101", f"G{g}", "content", ["multi_information"])
        if not chk["allowed"]:
            sys.exit(f"refusing: holdout ledger blocks G{g}: {chk['prior_runs_same_family']}")
    pu = pl.read_parquet(SH / "period_units.parquet").filter(pl.col("holdout") & pl.col("goal_no").is_in(list(TARGET_GOALS)))
    ch = pl.read_parquet(SH / "chat_core.parquet", columns=["goal_no", "speaker_kind"]).with_row_index("msg")
    rows_ = ch.filter(pl.col("goal_no").is_in(list(TARGET_GOALS)) & (pl.col("speaker_kind").is_in(["agent", "human"])))["msg"].to_numpy()
    OUT.mkdir(parents=True, exist_ok=True)
    uses = IM.uses_for_rows(rows_, allow_holdout=True)
    uses.write_parquet(OUT / "uses.parquet")
    B.OUT = OUT
    R.BASE = OUT
    B.build(pu, allow_holdout=True, uses_path=OUT / "uses.parquet")
    meta = pl.read_parquet(OUT / "unit_meta.parquet")
    n_med = dict(zip(meta["unit_id"].to_list(), meta["N_med"].to_list()))
    regime_of = {u: TARGET_GOALS[g] for u, g in zip(meta["unit_id"].to_list(), meta["goal_no"].to_list())}
    rows = unit_rows(list(regime_of), n_med)
    out = score(rows, regime_of)
    (OUT / "confirm_result.json").write_text(json.dumps({"sha256": sha, **out}, indent=1, default=float))
    print(json.dumps({k: v for k, v in out.items() if k != "units"}, indent=1, default=float))


if __name__ == "__main__":
    main()
