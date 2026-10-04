"""H74 confirmatory test on the locked holdout. FROZEN 2026-10-04 (round 1). DO NOT RUN without Vivian's sign-off.

Guard: runs on held-out data only with BOTH `--confirm` and the environment variable H74_CONFIRM=1, and only after
infra/shared/holdout_ledger.check() passes. Without them, `--dry-run` applies the same frozen rules to the
non-holdout round-1 scores (stand-ins) so the mechanics can be checked.

Design (frozen): the detector of round 1 (h74lib, tau = 4, B = 10, channels S, M, O, D, C; fused = max) runs over ALL
active days in time order (trailing baselines cross holdout boundaries as a live monitor would). Targets are events
whose day 0 is held out (`events.parquet`, held0 = True): scaffold changes in the NE12, NE30 and NE21+NE23 windows and
in held-out goal periods (#22, #28 ...), NE14's 03-11..03-13 rollout, NE20 (06-03), NE21's hour switches, NE22/NE44
(06-11), NE23 nudger off/on, NE24 (GitLab), NE25, NE26, held-out goal kickoffs and roster changes, the #51 tail.
Placebo days: held-out active days >= 3 active days from every catalogued event.

Frozen predictions (written 2026-10-04 after round 1; credences in brackets):
  C1 (primary; the schema channel as a precision alarm): S per-day FAR on held-out placebo days <= 0.05 AND S hits
     >= 1/3 of held-out scaffold_tool events [0.5].
  C2 (primary; operator counters): D hits >= 2/3 of held-out operator + operator_schedule events [0.6].
  C3: fused AUC (event window vs placebo window) for scaffold_tool >= 0.65 [0.45].
  C4: content channel C AUC for goal kickoffs >= 0.85 [0.75].
  C5 (descriptive): fused per-day placebo FAR (expected 0.10-0.25).
  Overall: CONFIRMED if C1 and C2 pass; PARTIAL if one passes; NOT CONFIRMED otherwise.
Reuse disclosure: H36 (R1 on held-out kickoffs) and H56 (EP on held-out scaffold events) plan the same targets with
different statistics; C4 is close to H36's R1 and must be disclosed as a second use.
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
sys.path.insert(0, str(HERE))
import h74lib as L  # noqa: E402

OUT = ROOT / "data/processed/H74-change-detector"
FROZEN = {"tau": L.TAU, "B": L.B, "C1_far_max": 0.05, "C1_hit_min": 1 / 3, "C2_hit_min": 2 / 3, "C3_auc_min": 0.65,
          "C4_auc_min": 0.85}


def judge(res: dict) -> dict:
    cl, far = res["classes"], res["far"]
    s_tool = cl.get("scaffold_tool", {}).get("S", {})
    c1 = far["S"]["per_day"] <= FROZEN["C1_far_max"] and s_tool.get("hit", 0) >= FROZEN["C1_hit_min"]
    op = [e for c in ("operator", "operator_schedule") for e in cl.get(c, {}).get("D", {}).get("events", [])]
    op_hit = np.mean([e["score"] is not None and e["score"] >= L.TAU for e in op]) if op else float("nan")
    c2 = bool(op) and op_hit >= FROZEN["C2_hit_min"]
    c3 = cl.get("scaffold_tool", {}).get("F", {}).get("auc", 0) >= FROZEN["C3_auc_min"]
    c4 = cl.get("goal", {}).get("C", {}).get("auc", 0) >= FROZEN["C4_auc_min"]
    overall = "CONFIRMED" if (c1 and c2) else "PARTIAL" if (c1 or c2) else "NOT CONFIRMED"
    return {"C1": {"pass": bool(c1), "S_far": far["S"]["per_day"], "S_hit_tool": s_tool.get("hit")},
            "C2": {"pass": bool(c2), "D_hit_operator": float(op_hit), "n": len(op)},
            "C3": {"pass": bool(c3), "auc": cl.get("scaffold_tool", {}).get("F", {}).get("auc")},
            "C4": {"pass": bool(c4), "auc": cl.get("goal", {}).get("C", {}).get("auc")},
            "C5": {"fused_far": far["F"]["per_day"]}, "overall": overall}


def dry_run():
    res = json.loads((OUT / "replication" / "results.json").read_text())
    out = judge(res)
    (OUT / "confirm_dryrun").mkdir(exist_ok=True)
    (OUT / "confirm_dryrun" / "confirm.json").write_text(json.dumps({"stand_in": "non-holdout round-1 scores", **out}, indent=1))
    print(json.dumps(out, indent=1))


def confirm():
    if os.environ.get("H74_CONFIRM") != "1":
        sys.exit("refused: set H74_CONFIRM=1 (and have Vivian's sign-off)")
    sys.path.insert(0, str(ROOT / "infra/shared"))
    import holdout_ledger  # noqa: E402
    for tgt in ["NE12", "NE21+NE23", "NE30", "#51-tail", "G22", "G28", "G45"]:
        st = holdout_ledger.check("H74", tgt, "platform logs + content", None)
        if not st.get("allowed", True):
            sys.exit(f"refused by holdout ledger for {tgt}: {st}")
        if st.get("needs_disclosure"):
            print(f"disclosure needed for {tgt} (other users listed in the ledger)")
    sys.path.insert(0, str(ROOT / "hypotheses/H74-change-detector/scheme"))
    import build  # noqa: E402
    import scan_signatures  # noqa: E402
    cdir = OUT / "confirm"
    cdir.mkdir(exist_ok=True)
    scan_signatures.main(include_holdout=True, out=cdir)
    build.main(include_holdout=True, out=cdir)
    import run_detector as RD  # noqa: E402
    days = pl.read_parquet(cdir / "days.parquet").sort("pt_date")
    cal = pl.read_parquet(ROOT / "data/processed/shared/calendar.parquet").filter(pl.col("n_agent_events") > 0).sort("pt_date")
    cal_days = cal["pt_date"].to_list()
    held = dict(zip(cal_days, cal["holdout"].to_list()))
    days = days.with_columns(pl.lit(False).alias("gap_return"), (pl.col("idx") >= 10).alias("has_baseline"))
    RD.OUT = cdir
    sc, tab = RD.scores_for(days)
    tab.write_parquet(cdir / "scores.parquet")
    ev = pl.read_parquet(cdir / "events.parquet")
    # evaluate on held-out days only: targets with held0, placebo days among held-out days
    days_h = days.with_columns(pl.col("pt_date").replace_strict(held, return_dtype=pl.Boolean).alias("_h"))
    ev_h = ev.filter(pl.col("held0")).with_columns(pl.lit(False).alias("held0"))
    keep = days_h["_h"].to_numpy()
    sc_h = {k: np.where(keep, v, np.nan) for k, v in sc.items()}
    rng = np.random.default_rng(20261004)
    res = L.evaluate(sc_h, days_h, ev_h, cal_days, ["scaffold_tool", "scaffold_prompt", "operator", "operator_schedule", "goal", "roster", "room"],
                     rng, exclude_from_placebo=ev.filter(~pl.col("held0")))
    out = judge(res)
    (cdir / "confirm.json").write_text(json.dumps({"results": res, "verdict": out}, indent=1, default=float))
    print("record the run in the holdout ledger: holdout_ledger.record_run(<entry id>, evidence=<this file + LOG.md date>)")
    print(json.dumps(out, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.confirm:
        confirm()
    else:
        dry_run()


if __name__ == "__main__":
    main()
