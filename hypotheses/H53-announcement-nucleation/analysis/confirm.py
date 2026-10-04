"""H53 confirmatory test on the LOCKED HOLDOUT. Frozen after round 1 (2026-10-04). NOT RUN in round 1.

Targets (card): #22, #29, #32, #45, #46, #47, #49, #50 and the #51 tail (2026-09-07 -> 09-21); #28, #34, #43 reported
but not scored (<= 4 seeds). Same scheme and estimators as round 1 (scheme/build.py, analysis/h53core.py):
primary receptive window = one call cycle, uncommitted = no other-project strict mention in 30 active min,
adoption = H11 W=15 project label, follow-up 60 active min after own read-out, wave horizon 2 h, seed model NB2 with
period intercepts partially pooled (tau = 1).

Frozen predictions:
  C1 (H53 as hypothesized): pooled RR_timely >= 1.5 with 95% CI > 1.              Round 1 predicts: NOT confirmed.
  C2 (round-1 negative replicates): RR_timely CI includes 1, or RR < 1.2.          Round 1 predicts: confirmed.
  C3 (announcement-seeded, room-bounded): F1 step ratio >= 3, F2 other-room ratio <= 0.3 (#45, #46-#51 rooms),
     F3 unexposed adopters <= 0.2.                                                  Round 1 predicts: confirmed.
  C4 (current share, not R, separates herded from never-herded seeds): within-period AUC(share) > AUC(R) and
     AUC(R) <= 0.6.                                                                  Round 1 predicts: confirmed.
  C5 (no call-clock lever for projects): held-out log score M_R - M0 <= 0, or its period-bootstrap 90% CI includes 0.
                                                                                     Round 1 predicts: confirmed.
Power rules: C1/C2 need >= 100 agent-level adoptions; C4 >= 10 herded seeds; C3's F2 >= 20 multi-room seeds;
otherwise "inconclusive (underpowered)".
Reuse policy (hypotheses/holdout.md): H11 (#22, #28, #45), H28 (#22, #28, #45), H27 (#22, #28, #29, #32, #34,
#45-#50, #51 tail), H31 (#29, #46, #47, #49, #50) and H06 (#22) target overlapping periods with different
statistics; H53's (read-out timing of seed recipients -> adoption; wave-size models) is unexamined. Disclose in both
cards and LOG.md when run.

Usage:
  uv run python analysis/confirm.py --dry-run                     # stand-ins #18, #31, #44 (non-holdout), pipeline check
  uv run python analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scheme"))
from h53lib import OUT, ROOT  # noqa: E402

TARGETS = [22, 29, 32, 45, 46, 47, 49, 50, 51]
REPORT_ONLY = [28, 34, 43]
STANDINS = [18, 31, 44]


def evaluate(out_dir: Path, goals: list[int], only_holdout_51: bool) -> dict:
    from h53core import (agent_rr, agent_table, auc_within, cv_compare, field_diagnostics, load, prep, seed_models)
    seeds, rec = load(out_dir)
    if only_holdout_51:   # #51: only the locked tail (2026-09-07 -> 09-21)
        seeds = seeds.filter((pl.col("goal_no") != 51) | (pl.col("pt_date") >= "2026-09-07"))
    s, r = prep(seeds, rec)
    s = s.filter(pl.col("goal_no").is_in(goals)); r = r.filter(pl.col("goal_no").is_in(goals))
    el = s.filter(pl.col("eligible"))
    res = dict(goals=goals, n_seeds=int(el.height), seeds_by_period={int(g): int(n) for g, n in el.group_by("goal_no").len().iter_rows()})
    t = agent_table(s, r)
    a = agent_rr(t)
    res["agent"] = a
    fd = field_diagnostics(s, r)
    fd["F1"].pop("curve", None)
    res["field"] = fd
    s2 = el.with_columns(pl.max_horizontal(pl.lit(3), (pl.col("n_room") / 3).ceil()).alias("thr"))
    pos, neg = pl.col("herd_kmax") >= pl.col("thr"), pl.col("herd_kmax") <= 1
    res["auc"] = {c: auc_within(s2, c, pos, neg)["auc"] for c in ("R", "share", "N_sus", "U")}
    res["n_herded"] = int(s2.filter(pos).height)
    scored = [g for g in goals if el.filter(pl.col("goal_no") == g).height >= 3]
    sm = s.filter(pl.col("goal_no").is_in(scored))
    if sm.filter(pl.col("eligible")).height >= 10:
        mod, cvll, cg = seed_models(sm, cv="lodo", ridge_tau=1.0, models={"M0": [], "M_R": ["lR"], "M_share": ["share"]})
        res["cv"] = {"M_R-M0": cv_compare(cvll, cg, "M_R", "M0"), "M_share-M0": cv_compare(cvll, cg, "M_share", "M0")}
    tim = a.get("x_timely", {})
    n_ad = a.get("n_adopt", 0)
    v = {}
    if n_ad < 100:
        v["C1"] = v["C2"] = "inconclusive (underpowered)"
    else:
        v["C1"] = "confirmed" if (tim.get("rr", 0) >= 1.5 and tim.get("lo", 0) > 1) else "not confirmed"
        v["C2"] = "confirmed" if (tim.get("lo", 0) <= 1 or tim.get("rr", 9) < 1.2) else "not confirmed"
    f1, f2, f3 = fd["F1"]["ratio"], fd["F2"]["ratio"], fd["F3"]["unexposed"]
    c3 = (f1 is not None and f1 >= 3) and (f3 is not None and f3 <= 0.2)
    if fd["F2"]["n_seeds"] >= 20:
        c3 = c3 and (f2 is not None and f2 <= 0.3)
    v["C3"] = "confirmed" if c3 else "not confirmed"
    if res["n_herded"] < 10:
        v["C4"] = "inconclusive (underpowered)"
    else:
        v["C4"] = "confirmed" if (res["auc"]["share"] > res["auc"]["R"] and res["auc"]["R"] <= 0.6) else "not confirmed"
    if "cv" in res:
        c = res["cv"]["M_R-M0"]
        v["C5"] = "confirmed" if (c["diff"] <= 0 or c["lo90"] <= 0 <= c["hi90"]) else "not confirmed"
    else:
        v["C5"] = "inconclusive (underpowered)"
    res["verdicts"] = v
    return res


def git_clean() -> bool:
    r = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "hypotheses/H53-announcement-nucleation"], capture_output=True, text=True)
    return r.stdout.strip() == ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    from build import build  # scheme/build.py
    if a.dry_run:
        tmp = OUT / "confirm_dryrun_tables"
        build(allow_holdout=False, goals=STANDINS, out=tmp)
        res = evaluate(tmp, STANDINS, only_holdout_51=False)
        res["note"] = "DRY RUN on non-holdout stand-ins (#18, #31, #44); a pipeline check, not evidence (stand-ins were explored in round 1)."
        (OUT / "confirm_dryrun.json").write_text(json.dumps(res, indent=1, default=str))
        for f in list(tmp.glob("*.parquet")) + list(tmp.glob("*.json")):
            f.unlink()
        tmp.rmdir()
        print(json.dumps(res["verdicts"], indent=1))
        return
    if not (a.confirm and a.ack):
        sys.exit("Refusing: the confirmatory run needs --confirm --i-understand-this-uses-the-locked-holdout (and Vivian's sign-off).")
    if not git_clean():
        sys.exit("Refusing: commit the H53 card and code first (git status shows changes under hypotheses/H53-announcement-nucleation).")
    cdir = OUT / "confirm"
    build(allow_holdout=True, goals=TARGETS + REPORT_ONLY, out=cdir)
    res = evaluate(cdir, TARGETS, only_holdout_51=True)
    res["report_only"] = evaluate(cdir, REPORT_ONLY, only_holdout_51=True)
    (OUT / "confirm_results.json").write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps(res["verdicts"], indent=1))


if __name__ == "__main__":
    main()
