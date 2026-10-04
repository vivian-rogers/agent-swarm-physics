"""H99 confirmatory run on the LOCKED HOLDOUT. Written and frozen 2026-10-04 after round 1; NOT RUN.

Guard: runs on held-out data only with BOTH `--confirm` and H99_CONFIRM=1, and only if `holdout_ledger.check` allows
every target. Otherwise it refuses. `--dry-run` runs the identical scoring on non-holdout stand-in units (already
built) and writes to a scratch directory, so the code path is tested without touching the holdout.

Targets: goal periods #22 and #28 (regime I) and #43 (regime III). Channel: talk (primary), content (C4).
Estimator (frozen = round 1 after Amendments A1/A2): all-present trim, 30-min block centring, mean-field split,
1-h block bootstrap B = 400; A2 rule for units with rho_perp(1) < 0.15 (talk): fast call if drho1 <= -0.03 with CI
below 0; slow call if drho1 or drho2 >= +0.03 with CI above 0; A1 rule otherwise (+/- 0.08 on dg1 / dg2).

Frozen predictions (from round 1: regime-I talk consistent in 18/20 resolved periods; regime-III talk pooled drho1
positive, #51 0.067 [0.034, 0.100]; content dg1 < 0 in most units):
  C1  Regime I is Glauber-consistent: in #22 and #28, every talk unit with a resolved g_chi (CI > 0) has no field
      call, and the pooled drho1 has |point| < 0.05.
  C2  Regime III keeps collective memory beyond Glauber: #43's random-effects pooled talk drho1 has a 95% CI above 0
      and a point estimate in [0.02, 0.15].
  C3  Subcritical: every target talk unit's g_chi upper bound < 0.6.
  C4  Content is field-like: content dg1 < 0 (point) in >= 2/3 of target units with >= 30 content window pairs.
Reading: C1 + C2 confirm "fluctuations predict relaxation in regime I but not in regime III, where the collective
outlives the prediction (delayed read-out coupling or a conversation field)". C4 confirms the content field reading.

Reuse policy (hypotheses/holdout.md): #22, #28 and #43 are planned by H25, H19, H38 (equal-time gain family) and H67
(talk read-out). H99's g_chi is H25's estimator family: if H25/H19 run first, C3 is a second use of their statistic
and must be disclosed. drho (C1, C2) and the content gap (C4) are new statistics. Disclose in the card and LOG.md.

Usage:
  uv run python hypotheses/H99-glauber-fluctuation-relaxation/analysis/confirm.py --dry-run
  H99_CONFIRM=1 uv run python hypotheses/H99-glauber-fluctuation-relaxation/analysis/confirm.py --confirm
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
import h99lib as L  # noqa: E402
import run as R  # noqa: E402
import summarize as S  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H99-glauber-fluctuation-relaxation/confirm"
SCRATCH = Path(os.environ.get("TMPDIR", "/tmp")) / "h99_confirm_dryrun"
TARGET_GOALS = {22: "I", 28: "I", 43: "III"}
STANDINS = {"24": "I", "27": "I", "42b": "III", "51j": "III"}
FROZEN = dict(C1=dict(abs_drho=0.05), C2=dict(range=(0.02, 0.15)), C3=dict(g_hi=0.6), C4=dict(share=2 / 3, min_pairs=30))


def unit_rows(units):
    rows = []
    for u in units:
        res, _ = R.run_unit(u)
        for r in res:
            if r["variant"] == "main":
                r["rule"], r["call"] = S.call_of(r)
                rows.append(r)
    return rows


def score(rows, regime_of):
    out = {"units": [{k: r.get(k) for k in ("unit", "channel", "g_chi", "g_chi_lo", "g_chi_hi", "drho1", "drho1_lo",
                                            "drho1_hi", "dg", "call", "n_min")} for r in rows]}
    talk = [r for r in rows if r["channel"] == "talk"]
    I = [r for r in talk if regime_of[r["unit"]] == "I"]
    III = [r for r in talk if regime_of[r["unit"]] == "III"]
    resI = [r for r in I if r["g_chi_lo"] is not None and r["g_chi_lo"] > 0]
    pI = L.re_pool([r["drho1"] for r in I], [r["drho1_se"] for r in I])
    out["C1"] = {"pass": bool(all(r["call"] == "consistent" for r in resI) and abs(pI["mean"]) < FROZEN["C1"]["abs_drho"]),
                 "resolved_calls": [r["call"] for r in resI], "pooled_drho1": pI}
    pIII = L.re_pool([r["drho1"] for r in III], [r["drho1_se"] for r in III])
    lo, hi = FROZEN["C2"]["range"]
    out["C2"] = {"pass": bool(pIII["lo"] > 0 and lo <= pIII["mean"] <= hi), "pooled_drho1": pIII}
    out["C3"] = {"pass": bool(all((r["g_chi_hi"] if r["g_chi_hi"] is not None else 1) < FROZEN["C3"]["g_hi"] for r in talk)),
                 "max_g_chi_hi": max((r["g_chi_hi"] or np.nan) for r in talk) if talk else None}
    con = [r for r in rows if r["channel"] == "content" and r["n_min"] >= FROZEN["C4"]["min_pairs"]]
    neg = [r for r in con if r["dg"] is not None and np.isfinite(r["dg"]) and r["dg"] < 0]
    out["C4"] = {"pass": bool(con and len(neg) / len(con) >= FROZEN["C4"]["share"]), "n": len(con), "n_neg": len(neg)}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    if a.dry_run:
        rows = unit_rows(list(STANDINS))
        out = score(rows, STANDINS)
        SCRATCH.mkdir(parents=True, exist_ok=True)
        (SCRATCH / "dryrun.json").write_text(json.dumps({"sha256": sha, **out}, indent=1, default=float))
        print(json.dumps({k: v for k, v in out.items() if k != "units"}, indent=1, default=float))
        return
    if not (a.confirm and os.environ.get("H99_CONFIRM") == "1"):
        sys.exit("refusing: confirmatory run needs --confirm and H99_CONFIRM=1 (Vivian's sign-off)")
    import holdout_ledger as HL
    for g in TARGET_GOALS:
        chk = HL.check("H99", f"G{g}", "talk", ["curie_weiss_gain"])
        if not chk["allowed"]:
            sys.exit(f"refusing: holdout ledger blocks G{g}: {chk['prior_runs_same_family']}")
    pu = pl.read_parquet(SH / "period_units.parquet").filter(pl.col("holdout") & pl.col("goal_no").is_in(list(TARGET_GOALS)))
    B.OUT = OUT
    R.BASE = OUT
    B.build(pu, allow_holdout=True)
    regime_of = {u: TARGET_GOALS[g] for u, g in zip(pu["unit_id"].to_list(), pu["goal_no"].to_list())}
    built = pl.read_parquet(OUT / "unit_meta.parquet")["unit_id"].to_list()
    rows = unit_rows([u for u in built if u in regime_of])
    out = score(rows, regime_of)
    (OUT / "confirm_result.json").write_text(json.dumps({"sha256": sha, **out}, indent=1, default=float))
    print(json.dumps({k: v for k, v in out.items() if k != "units"}, indent=1, default=float))


if __name__ == "__main__":
    main()
