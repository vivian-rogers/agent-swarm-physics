"""H06 confirmatory test on the locked holdout free week #22 (2025-12-08 -> 12-12). NOT RUN in round 1.

The decision rule below was frozen on 2026-10-04 after exploratory round 1 and before any #22 data was read
(card: "Confirmatory prediction"). Same pipeline as round 1: scheme/build.py labels (intention clusters, k-means /
Ward ladder m in {8, 24, 64}, primary km24; strict artifact labels with carry-forward), the exact finite-N simulators,
profile synthetic-likelihood fits, 400 fresh replicates, joint PPC (analysis/ncd_core.py, analysis/explore.py).

Frozen claims for #22:
  C1  (the original H06 P1 rule) NCD 'supported' on intention clusters km24 (LLR_NH >= 2, LLR_NC >= 2 in >= 4/6
      clusterings, NCD adequate, mu_NCD < mu_L/2).  Round 1 predicts C1 FAILS (NCD supported in 0/5 free weeks).
  C2  (round-1 pattern: agent-bound projects that no exchangeable copying model reproduces), all three on km24:
      (a) the copying models are not adequate: joint PPC p < 0.01 for NCD AND for Hubbell;
      (b) copy-consistency below 0.8 (agents switch to projects nobody else holds), outside NCD's 95% interval;
      (c) singleton fraction above NCD's 97.5% predictive point.
      C2 holds if (a) and at least one of (b), (c) hold. Refuted if NCD is adequate and (b) and (c) both fail.
  C3  (frequency dependence) beta_hat is not below the Hubbell predictive median (no rare-project advantage).
  C4  (some coordination) lambda_bar above the day-shift independent-agents null (one-sided p < 0.05).

Usage:
  uv run python .../confirm_holdout.py --dry-run                       # non-holdout stand-ins (#11, #16), no holdout read
  uv run python .../confirm_holdout.py --confirm --i-understand-this-uses-the-locked-holdout
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import explore as X  # noqa: E402
import ncd_core as M  # noqa: E402

DATA = X.DATA
TARGET = "G22"
STANDINS = ["G11", "G16"]  # N = 7 free weeks (#22 has N = 9); fast


def evaluate(scope: str, allow_holdout: bool) -> dict:
    if scope == TARGET:
        if not allow_holdout:
            raise SystemExit("refusing: #22 is in the locked holdout")
        X.SCOPES[TARGET] = (TARGET, None, "CONFIRMATORY")
        X.guard = lambda folder, dates: None  # holdout guard lifted only on the --confirm path
    r = X.run_scope(scope)
    p = r["sets"].get(X.PRIMARY, {})
    out = {"scope": scope, "P1_rule": r["P1"]}
    if not p.get("testable"):
        out["verdict"] = "n/a (insufficient labels)"
        return out
    f = p["fits"]
    c1 = r["P1"]["verdict"] == "supported"
    a = (f["ncd"]["ppc_joint"] < 0.01) and (f["hubbell"]["ppc_joint"] < 0.01)
    b = (p["copyfrac"] < 0.8) and not (f["ncd"]["pred"]["copyfrac"][1] <= p["copyfrac"] <= f["ncd"]["pred"]["copyfrac"][2])
    c = p["obs"]["single"] > f["ncd"]["pred"]["single"][2]
    c2 = a and (b or c)
    c2_refuted = f["ncd"]["adequate"] and not b and not c
    c3 = not (np.isfinite(p["obs"]["beta"]) and p["obs"]["beta"] < f["hubbell"]["pred"]["beta"][3])
    nul = p.get("null_ind", {})
    c4 = nul.get("lam_p_greater", 1.0) < 0.05
    out.update({"C1_ncd_supported": c1, "C2a_models_inadequate": a, "C2b_copy_low": b, "C2c_singletons_high": c,
                "C2_agent_bound": c2, "C2_refuted": c2_refuted, "C3_no_rare_advantage": c3, "C4_coordination": c4,
                "numbers": {"LLR_NH": p["LLR_NH"], "LLR_NC": p["LLR_NC"], "ppcj": {m: f[m]["ppc_joint"] for m in M.MODELS},
                            "copyfrac": p["copyfrac"], "copy_pred_ncd": f["ncd"]["pred"]["copyfrac"], "single": p["obs"]["single"],
                            "single_pred_ncd": f["ncd"]["pred"]["single"], "beta": p["obs"]["beta"],
                            "beta_hub_median": f["hubbell"]["pred"]["beta"][3], "lam": p["obs"]["lam"], "null_ind": nul}})
    out["verdict"] = ("C1 confirmed (NCD supported)" if c1 else
                      "C1 not confirmed; C2 " + ("confirmed" if c2 else ("refuted" if c2_refuted else "inconclusive")))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.dry_run:
        X.OUT_SUFFIX = "_confirm_dryrun"
        res = {s: evaluate(s, allow_holdout=False) for s in STANDINS}
        (DATA / "confirm_dryrun.json").write_text(json.dumps(res, indent=1, default=float))
        for s, r in res.items():
            print(f"[dry run, stand-in {s}] {r['verdict']}")
        return
    if not (a.confirm and a.ack):
        raise SystemExit("refusing: the confirmatory run reads the locked holdout (#22). "
                         "Use --dry-run, or --confirm --i-understand-this-uses-the-locked-holdout after sign-off.")
    import build as B  # scheme/build.py
    X.OUT_SUFFIX = "_confirm"
    B.build_scope(TARGET, allow_holdout=True)
    res = evaluate(TARGET, allow_holdout=True)
    (DATA / TARGET / "confirm.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
