"""H33 confirmatory test on the LOCKED HOLDOUT. Written 2026-10-04 after exploratory round 1; NOT RUN.

Pre-registered predictions (thresholds fixed here before any holdout data is read; card section "Confirmatory plan"):
  Held-out goal periods with logged write verbs: #22, #28, #29, #32 (split 32a < 2026-02-25 <= 32b, regime boundary),
  #34, #45, #46, #47, #48, #49, #50, and the #51 tail (2026-09-07 -> 09-21) as unit "51t". The card's eligibility
  rule (>= 30 agent-days with PR10, >= 4 agents with >= 3 days, write turns on >= 20% of agent-days) is applied
  mechanically; one-day periods (#43 never included; #48) are expected to drop out.
  Pipeline = round 1 exactly (scheme/build.py `build`, evaluate.shape_block): agent-day PR10 after H12 self-repeat
  removal, y = log(1 + write turns), FE agent x unit + day, controls log raw chat and log(1 + engaged minutes),
  clusters agent x unit; the Robin Hood breakpoint is re-estimated on held-out data (the procedure is the test).
  C1  H33 as stated (round-1 rule P1): spline maximum interior AND two-lines b1 > 0, b2 < 0, both p < 0.05.
      Prediction after round 1: FAILS (credence that it passes 0.10).
  C2  Operator claim "content diversity carries no usable information about write output": no PR10 term (linear,
      quadratic, spline) improves 5-fold day-blocked CV MSE over FE + controls by >= 1%, i.e.
      (MSE_m - MSE_FE+controls) / MSE_FE+controls > -0.01 for every m (mean over 5 fold seeds). One-sided: overfitting
      that makes MSE worse is consistent with "no usable information" (amended after the non-holdout dry run, where
      curved terms were 1-3% worse). Prediction: HOLDS (credence 0.75).
  C3  No "unfocused" penalty inside the observed range: spline contrast f(x_max) - f(q90), in residual-SD units, has
      95% upper bound < 0.30 (≈ 25% fewer write turns at the 90th percentile than at the best PR10). Threshold set
      after the dry run (559 stand-in agent-days gave 0.30; 0.25 is beyond the attainable precision). Prediction:
      HOLDS (credence 0.65).
  C4  Low-side (loop) lead from round 1: two-lines b1 > 0 with one-sided p < 0.05. Credence 0.25.
  C5  Post hoc lead from round 1 (#51, PR15): in unit 51t, two-lines on PR15 gives b2 < 0 with p < 0.05. Credence 0.20.
  Reading: H33 is confirmed only if C1 passes. The round-1 reading (no operating point; diversity uninformative about
  output) is confirmed if C1 fails AND C2 and C3 hold. Sensitivity (reported, decides nothing): all of C1-C4 without
  #34 and #45.

Reuse policy (hypotheses/holdout.md): H02 has used #45 (activity timing; different modality). Unrun confirm scripts
target #34 (H01, H05, H07, H12, H19, H21), #45 (H23, message content style) and most held-out periods (H12: swarm-day
content PR, near-duplicate share). H33's observable, the relation between agent-day content PR and artifact write
output, has not been computed on any held-out period by anyone; if H12's confirm runs first, H33's x overlaps H12's
content-PR statistic and the reuse must be disclosed in both cards and LOG.md. This script refuses to run unless the
card and this file are committed (policy item 1).

Usage:
  uv run python hypotheses/H33-diversity-productivity/analysis/confirm.py --dry-run     # NON-HOLDOUT stand-ins
  uv run python hypotheses/H33-diversity-productivity/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
"""
from __future__ import annotations

import json
import subprocess
import sys

import h33lib as H  # noqa: I001
import h33common as C
import numpy as np
import polars as pl

import importlib.util


def _load(name, path):
    """Load an H33 module by file path (H12 and H15 also have evaluate.py / build.py on sys.path)."""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


E = _load("h33_evaluate", C.HYP / "analysis/evaluate.py")
B = _load("h33_build", C.HYP / "scheme/build.py")

FLAG_A, FLAG_B = "--confirm", "--i-understand-this-uses-the-locked-holdout"
HOLDOUT_GOALS = [22, 28, 29, 32, 34, 45, 46, 47, 48, 49, 50]
HOLDOUT_TAIL = ("2026-09-07", "2026-09-21")
REUSED = {"34", "45"}
# Non-holdout stand-ins for --dry-run (same roles: several weekly units, one long-period tail)
STANDIN_GOALS = [30, 31, 35, 38, 41, 42, 44]
STANDIN_TAIL = ("2026-08-24", "2026-09-07")  # last two non-holdout weeks of #51, labelled "51t"


def select_calendar(holdout: bool) -> pl.DataFrame:
    cal = pl.read_parquet(C.SH / "calendar.parquet")
    hm = C.holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    cal = cal.with_columns(pl.Series("hm", hm), pl.col("regime").cast(pl.Utf8))
    goals, tail = (HOLDOUT_GOALS, HOLDOUT_TAIL) if holdout else (STANDIN_GOALS, STANDIN_TAIL)
    in_tail = (pl.col("goal_no") == 51) & (pl.col("pt_date") >= tail[0]) & (pl.col("pt_date") < tail[1])
    sel = cal.filter((pl.col("hm") == holdout) & (pl.col("goal_no").is_in(goals) | in_tail)
                     & (pl.col("n_agent_events") > 0))
    if not holdout:
        assert not any(C.holdout_mask(sel["pt_date"].to_list(), sel["goal_no"].to_list())), "dry run touched the holdout"
    unit = (pl.when(in_tail).then(pl.lit("51t"))
            .when((pl.col("goal_no") == 32) & (pl.col("pt_date") < "2026-02-25")).then(pl.lit("32a"))
            .when(pl.col("goal_no") == 32).then(pl.lit("32b"))
            .otherwise(C.unit_expr()))
    return sel.drop("hm").with_columns(unit.alias("unit"))


def committed_or_die():
    paths = [str(C.HYP / "README.md"), str(C.HYP / "analysis/confirm.py")]
    dirty = subprocess.run(["git", "-C", str(C.ROOT), "status", "--porcelain", "--"] + paths, capture_output=True, text=True).stdout
    if dirty.strip():
        raise SystemExit("REUSE POLICY: commit the H33 card and confirm.py before the confirmatory run:\n" + dirty)


def tests(root, holdout: bool, exclude=frozenset()):
    units = None
    if exclude:
        ad_all = C.load_agent_day(root)
        units = [u for u in H.eligibility(ad_all).filter("eligible")["unit"].to_list() if u not in exclude]
    ad, x, y, Z, au, day = H.load_pooled("pr10", "writes", units=units, root=root, guard=not holdout)
    out = {"units": sorted(set(ad["unit"].to_list())), "n": int(len(x))}
    blk, sp, D, y_dm = E.shape_block(x, y, Z, au, day)
    tl = blk["two_lines"]
    out["C1"] = {"pass": bool(blk["P1"]), "two_lines": tl, "spline_interior": blk["spline"]["interior"], "quad": blk["quad"]}
    cvs = [H.cv_day_blocked(y, x, Z, np.array([str(a) for a in au]), day, k=5, seed=s) for s in range(5)]
    cv = {m: float(np.mean([c[m] for c in cvs])) for m in ("fe_controls", "linear", "quadratic", "spline")}
    rel = {m: (cv[m] - cv["fe_controls"]) / cv["fe_controls"] for m in ("linear", "quadratic", "spline")}
    out["C2"] = {"pass": bool(all(v > -0.01 for v in rel.values())), "cv": cv, "rel_change": rel}
    b, V, e_res, G = D.fit(y_dm, np.zeros((len(y), 0)))
    sd = float(e_res.std())
    q90 = float(np.quantile(x, 0.9))
    dvec = (H.ns_basis(np.array([sp["x_max"]]), sp["knots"]) - H.ns_basis(np.array([q90]), sp["knots"]))[0]
    est, se = float(dvec @ sp["beta"]), float(np.sqrt(dvec @ sp["V"] @ dvec))
    out["C3"] = {"pass": bool((est + 1.96 * se) / sd < 0.30), "contrast_sd": est / sd, "upper95_sd": (est + 1.96 * se) / sd}
    p1_one = tl["p1"] / 2 if tl["b1"] > 0 else 1 - tl["p1"] / 2
    out["C4"] = {"pass": bool(tl["b1"] > 0 and p1_one < 0.05), "b1": tl["b1"], "p_one_sided": p1_one}
    if "51t" in out["units"] and not exclude:
        a5, x5, y5, Z5, au5, d5 = H.load_pooled("pr15", "writes", units=["51t"], root=root, guard=not holdout)
        b5 = E.shape_block(x5, y5, Z5, au5, d5)[0]["two_lines"]
        out["C5"] = {"pass": bool(b5["b2"] < 0 and b5["p2"] < 0.05), "two_lines": b5}
    else:
        out["C5"] = {"pass": None, "note": "unit 51t not eligible or excluded"}
    return out


def run(holdout: bool):
    root = C.OUT / ("confirm" if holdout else "confirm_dryrun")
    cal = select_calendar(holdout)
    print(f"{'HOLDOUT' if holdout else 'DRY RUN (non-holdout stand-ins)'}: {cal.height} days, units {sorted(set(cal['unit'].to_list()))}")
    B.build(cal, root, guard=not holdout)
    elig = H.eligibility(C.load_agent_day(root))
    elig.write_parquet(root / "eligibility.parquet")
    res = {"holdout": holdout, "eligibility": elig.sort("unit").to_dicts(), "primary": tests(root, holdout)}
    res["sensitivity_without_34_45"] = tests(root, holdout, exclude=frozenset(REUSED)) if holdout else None
    p = res["primary"]
    res["reading"] = ("H33 confirmed (inverted U)" if p["C1"]["pass"] else
                      "round-1 null reading confirmed (no operating point)" if (p["C2"]["pass"] and p["C3"]["pass"]) else
                      "neither H33 nor the null reading confirmed")
    (root / "confirm_results.json").write_text(json.dumps(res, indent=1, default=float))
    C.write_provenance("hypotheses/H33-diversity-productivity/analysis/confirm.py", ["H33 build on selected days"],
                       {"holdout": holdout, "goals": HOLDOUT_GOALS if holdout else STANDIN_GOALS,
                        "tail": HOLDOUT_TAIL if holdout else STANDIN_TAIL}, path=root / "_provenance.json")
    print(json.dumps({k: (v if k != "eligibility" else None) for k, v in res.items()}, indent=1, default=float)[:5000])


def main(argv):
    if "--dry-run" in argv:
        run(holdout=False)
        return
    if FLAG_A in argv and FLAG_B in argv:
        committed_or_die()
        run(holdout=True)
        return
    raise SystemExit(f"Refusing: the confirmatory run uses the locked holdout. Pass {FLAG_A} {FLAG_B} (needs sign-off), "
                     "or --dry-run for non-holdout stand-ins.")


if __name__ == "__main__":
    main(sys.argv[1:])
