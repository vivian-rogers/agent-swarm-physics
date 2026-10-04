"""H72 confirmatory test on the LOCKED HOLDOUT. Written and frozen 2026-10-04 after exploratory round 1; NOT RUN.

Refuses to touch held-out data unless called with BOTH flags
    --confirm --i-understand-this-uses-the-locked-holdout
and refuses if hypotheses/H72-trap-aging-input-starvation/ or infra/shared/idle_gates.py has uncommitted changes
(reuse policy: predictions and code committed before the run). It also prints the holdout-ledger reuse check
(infra/shared/holdout_ledger.check) for each target. Without the flags it runs a DRY RUN on non-holdout stand-ins and
writes data/processed/H72-trap-aging-input-starvation/confirm_dryrun/confirm_results.json.

Frozen predictions (round-1 findings as confirmable claims; same estimator as analysis/run_period.py, primary
variant: sustained escape, a = a_sus, s = s_novel, logit with agent FE, day-block bootstrap B = 200):
  C1  #51 tail (2026-09-07 -> 09-18, regime III): trap aging survives the starvation control:
      beta_a < -0.2 with 95% CI below 0, and rho (aging absorbed) < 0.25.                                   [primary]
  C2  #51 tail: input starvation does not lower escape: the 95% CI of beta_s has its lower bound > -0.1.    [primary]
  C3  each held-out regime-III period #45, #47, #48, #49, #50 that is powered (>= 30 escapes and >= 30
      non-escapes) and shows aging (beta_a0 CI below 0): the card's per-period verdict is "failed"
      (aging is not starvation). Pass if this holds in every such period; n/a if none qualifies.           [primary]
  C4  #32 (regime I): beta_s point estimate >= 0 (recent chatter holds agents idle; not the starvation sign). [secondary]
Overall: "trap aging is not input starvation" is confirmed if no primary C fails and >= 1 passes.

Reuse (hypotheses/holdout.md default policy): #45 (H02), #46-#50 (NE21+NE23; H04) and the #51 tail have prior or
planned confirmatory uses by other hypotheses with different statistics; nobody has computed an idle-gate escape
hazard there. Disclose in LOG.md and in this card before running.
Stand-ins for the dry run: #51 tail -> G51 2026-08-24 .. 09-04; #45/#47-#50 -> G38, G41, G44; #32 -> G18.
Usage:  uv run python hypotheses/H72-trap-aging-input-starvation/analysis/confirm.py                 (dry run)
        uv run python hypotheses/H72-trap-aging-input-starvation/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h72lib as L  # noqa: E402

ROOT = L.ROOT
sys.path.insert(0, str(ROOT / "infra/shared"))

TARGETS = {"tail": {"goals": [51], "from": "2026-09-07", "to": "2026-09-18"},
           "III": {"goals": [45, 47, 48, 49, 50]}, "I": {"goals": [32]}}
STANDINS = {"tail": {"goals": [51], "from": "2026-08-24", "to": "2026-09-04"},
            "III": {"goals": [38, 41, 44]}, "I": {"goals": [18]}}


def frames(spec, holdout: bool) -> pl.DataFrame:
    if holdout:
        import idle_gates as IG
        from common import holdout_mask
        g = IG.build(include_holdout=True, goal_nos=spec["goals"])
        g = g.filter(pl.Series(holdout_mask(g["pt_date"].to_list(), g["goal_no"].to_list())))
    else:
        g = pl.read_parquet(L.OUT / "gates.parquet").filter(pl.col("goal_no").is_in(spec["goals"]))
    if spec.get("from"):
        g = g.filter(pl.col("pt_date").is_between(pl.lit(spec["from"]), pl.lit(spec["to"])))
    return g


def fit(df, B):
    P = L.prep(df, "sus", "novel")
    n_esc = int(P["y"].sum())
    r = {"n": P["n"], "n_escape": n_esc}
    if n_esc < L.MIN_EVENTS or P["n"] - n_esc < L.MIN_EVENTS:
        r["verdict"] = "descriptive (underpowered)"
        return r
    pt = L.point(P)
    bt = L.bootstrap(P, B, seed=72)
    r.update({k: pt[k] for k in ("beta_a0", "beta_a", "beta_s", "rho")})
    r.update({k: bt[k] for k in ("ci_a0", "ci_a", "ci_s", "ci_rho")})
    r["verdict"] = L.verdict(r, n_esc, P["n"] - n_esc)
    return r


def run(holdout: bool, B: int):
    S = TARGETS if holdout else STANDINS
    res = {"mode": "CONFIRM" if holdout else "dry run (stand-ins, not evidence)", "B": B}
    t = fit(frames(S["tail"], holdout), B)
    res["tail"] = t
    if "beta_a" in t:
        res["C1"] = "pass" if (t["beta_a"] < -0.2 and t["ci_a"][1] < 0 and t["rho"] < 0.25) else "fail"
        res["C2"] = "pass" if t["ci_s"][0] > -0.1 else "fail"
    else:
        res["C1"] = res["C2"] = "n/a"
    per = {}
    for g in S["III"]["goals"]:
        per[f"G{g:02d}"] = fit(frames({"goals": [g]}, holdout), B)
    res["III"] = per
    q = [v for v in per.values() if "beta_a0" in v and v["ci_a0"][1] < 0]
    res["C3"] = "n/a" if not q else ("pass" if all(v["verdict"] == "failed" for v in q) else "fail")
    r1 = fit(frames(S["I"], holdout), B)
    res["I"] = r1
    res["C4"] = "n/a" if "beta_s" not in r1 else ("pass" if r1["beta_s"] >= 0 else "fail")
    prim = [res["C1"], res["C2"], res["C3"]]
    res["overall"] = "confirmed" if ("fail" not in prim and "pass" in prim) else ("not confirmed" if "fail" in prim else "n/a")
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    a = ap.parse_args()
    if a.confirm or a.ack:
        if not (a.confirm and a.ack):
            sys.exit("both --confirm and --i-understand-this-uses-the-locked-holdout are required")
        dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "--",
                                "hypotheses/H72-trap-aging-input-starvation", "infra/shared/idle_gates.py"],
                               capture_output=True, text=True).stdout.strip()
        if dirty:
            sys.exit("refusing: uncommitted changes in the H72 folder or idle_gates.py\n" + dirty)
        import holdout_ledger as HL
        for tgt in ("#51-tail", "G45", "G47", "G48", "G49", "G50", "G32"):
            print(tgt, HL.check("H72", tgt, "activity", ["behavior_states"]))
        res = run(True, 200)
        od = L.OUT / "confirm"
    else:
        res = run(False, 50)
        od = L.OUT / "confirm_dryrun"
    od.mkdir(parents=True, exist_ok=True)
    (od / "confirm_results.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps({k: v for k, v in res.items() if k.startswith("C") or k in ("mode", "overall")}))


if __name__ == "__main__":
    main()
