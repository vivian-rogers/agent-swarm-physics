"""H19 CONFIRMATORY test on the LOCKED HOLDOUT. Written 2026-10-04 in exploratory round 1; NOT RUN.

AMENDMENT (2026-10-04, after the exploratory P1 failed, BEFORE any holdout data was touched): the primary confirmatory
model is now the CHANNEL model frozen in results/frozen_channel_model.json (talk-channel gains on k_llm = agent messages
delivered per LLM step; activity-channel gains on x_att), found post hoc in exploration (analysis/posthoc_channels.py).
The pre-registered P1 model (every method on x_att; results/frozen_model.json) is sealed and scored as a secondary.

Predicts held-out periods' loop gains from their control parameters with the collapse model frozen at the end of
exploration (data/processed/H19-loop-gain-collapse/results/frozen_model.json), seals the predictions (SHA-256)
BEFORE any loop gain is estimated on those periods, then scores them.

Stages (one invocation runs them in order; stage 1's file is written and hashed before stage 2 starts):
  1. predict  controls of the eligible held-out periods (scheme/build_controls.build, identical definitions);
              90% prediction intervals from the frozen per-method model (x_att) and from the regime-only rival.
              Written to confirm/sealed_predictions.json (+ .sha256). Refuses to overwrite an existing sealed file.
  2. score    H19's own equal-time estimator (scheme/build_estimates.own_geq; E1 geq_active, E2 geq_talk) on the
              eligible periods; Hawkes and other methods only if their owners have written held-out estimates in the
              shared schema (data/processed/H*/per_period_estimates.parquet with a `confirmatory` = true column).
Pass rule (card, "Confirmatory design"; unchanged by the amendment): >= 70% of eligible held-out estimates inside their
90% intervals AND the model's held-out RMSE below the regime-only rival's on the same cells. Applied to the channel model
(primary; also reported for the talk channel alone) and to the P1 model (secondary).

Eligible (nobody has estimated a loop gain there; card): #1, #9, #14, #15, #22, #28, #29, #32, #34, #43, #51 tail
(2026-09-07 -> 09-21); #45 for Hawkes methods only (H02 computed #45's Curie-Weiss gain); #46-#50 excluded (H04
computed Hawkes n and K on the NE21 segments).

Usage:
  uv run python hypotheses/H19-loop-gain-collapse/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
  uv run python hypotheses/H19-loop-gain-collapse/analysis/confirm.py --dry-run      # code-path check on NON-holdout periods only
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import h19common as C  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402

FLAGS = ("--confirm", "--i-understand-this-uses-the-locked-holdout")
ELIGIBLE = [1, 9, 14, 15, 22, 28, 29, 32, 34, 43, 51]          # 51 = the held-out tail only
TAIL_51 = ("2026-09-07", "2026-09-21")
HAWKES_ONLY = [45]
E_METHODS = ("H19.geq_active", "H19.geq_talk")
DRY_RUN_PERIODS = [24, 41]  # non-holdout stand-ins for the code-path check (they were fitted: numbers meaningless)
Z90 = stats.norm.ppf(0.95)


def held_out_calendar(dry: bool) -> pl.DataFrame:
    cal = pl.read_parquet(C.SHARED / "calendar.parquet").filter((pl.col("window_s") > 0) & pl.col("goal_no").is_not_null())
    if dry:
        sel = cal.filter(pl.col("goal_no").is_in(DRY_RUN_PERIODS) & ~pl.col("holdout"))
        C.assert_no_holdout(sel["pt_date"], sel["goal_no"])
        return sel
    held = C.heldout_goals()
    sel = cal.filter(pl.col("goal_no").is_in([g for g in ELIGIBLE + HAWKES_ONLY if g in held]) |
                     ((pl.col("goal_no") == 51) & (pl.col("pt_date") >= TAIL_51[0]) & (pl.col("pt_date") < TAIL_51[1])))
    return sel


def frozen():
    return json.loads((C.OUT / "results/frozen_model.json").read_text())


def frozen_channel():
    return json.loads((C.OUT / "results/frozen_channel_model.json").read_text())


def predict_one(spec: dict, row: dict, x: str, rival=False):
    if rival:
        lv = spec["regime_levels"].get(row["regime"])
        if lv is None:
            return None  # regime level unseen in exploration for this method
        mu, var = lv["mu"], spec["median_se"] ** 2 + lv["tau2"] + lv["var_b"]
    else:
        vec = np.array([1.0 if nm == "intercept" else row[nm] for nm in spec["names"]])
        mu = float(vec @ np.array(spec["b"]))
        var = float(spec["median_se"] ** 2 + spec["tau2"] + vec @ np.array(spec["cov"]) @ vec)
    sd = float(np.sqrt(var))
    return {"mu": mu, "sd": sd, "lo90": mu - Z90 * sd, "hi90": mu + Z90 * sd}


def stage_predict(cal: pl.DataFrame, outdir: Path, dry: bool) -> dict:
    import build_controls as BC
    sealed = outdir / "sealed_predictions.json"
    if sealed.exists() and not dry:
        sys.exit(f"refusing to overwrite sealed predictions: {sealed}")
    F = frozen()
    FC = frozen_channel()
    ctr = BC.build(cal, allow_holdout=not dry, write_days=False)
    preds = []
    for row in ctr.iter_rows(named=True):
        g = row["goal_no"]
        pid = "G51tail" if (g == 51 and not dry) else C.pname(g)
        for m in sorted(set(F["methods"]) | set(FC["methods"])):
            fam_T = not m.startswith(("H19.", "H04.K", "H05.", "H02."))
            if g in HAWKES_ONLY and not fam_T:
                continue
            rec = {"period": pid, "goal_no": g, "method": m, "regime": row["regime"]}
            if m in FC["methods"]:
                spec = FC["methods"][m]
                p = predict_one(spec, row, spec["x"])
                rec.update({"channel": spec["channel"], "channel_x": spec["x"], "x_value": row[spec["x"]],
                            **{f"channel_{k}": v for k, v in p.items()}})
                r = predict_one(spec, row, spec["x"], rival=True)
                if r:
                    rec.update({f"rival_{k}": v for k, v in r.items()})
            if m in F["methods"]:
                p = predict_one(F["methods"][m], row, F["x"])
                rec.update({f"p1_{k}": v for k, v in p.items()})
            preds.append(rec)
    doc = {"written_at": dt.datetime.now(dt.timezone.utc).isoformat(), "dry_run": dry, "frozen_p1_model_at": F["frozen_at"],
           "frozen_channel_model_at": FC["frozen_at"], "primary": "channel", "secondary": "p1 (x_att for all methods)",
           "controls": jsonable(ctr.to_dicts()), "predictions": preds}
    txt = json.dumps(doc, indent=1, default=str)
    outdir.mkdir(parents=True, exist_ok=True)
    sealed.write_text(txt)
    (outdir / "sealed_predictions.sha256").write_text(hashlib.sha256(txt.encode()).hexdigest() + "\n")
    print(f"sealed {len(preds)} predictions -> {sealed} (sha256 {hashlib.sha256(txt.encode()).hexdigest()[:16]}...)")
    return doc


def jsonable(o):
    return json.loads(json.dumps(o, default=str))


def stage_score(cal: pl.DataFrame, doc: dict, outdir: Path, dry: bool) -> dict:
    import build_estimates as BE
    rng = np.random.default_rng(BE.SEED)
    own = BE.own_geq(cal, rng)  # per chunk; combine within period by inverse variance
    own = own.with_columns((1 / pl.col("se") ** 2).alias("w"))
    est = (own.group_by("goal_no", "method").agg(((pl.col("w") * pl.col("value")).sum() / pl.col("w").sum()).alias("value"),
                                                  (1 / pl.col("w").sum().sqrt()).alias("se")))
    ext = []
    for p in sorted(C.PROC.glob("H*/per_period_estimates.parquet")):
        d = pl.read_parquet(p)
        if {"goal_no", "method", "value", "se", "confirmatory"} <= set(d.columns):
            d = d.filter(pl.col("confirmatory") & pl.col("goal_no").is_in(cal["goal_no"].unique().to_list()))
            hyp = p.parent.name.split("-")[0]
            ext.append(d.select("goal_no", (pl.lit(hyp + ".") + pl.col("method")).alias("method"), "value", "se"))
    if ext:
        est = pl.concat([est] + ext, how="diagonal_relaxed")
    P = pl.DataFrame(doc["predictions"])
    sc = P.join(est, on=["goal_no", "method"], how="inner")
    if sc.height == 0:
        print("no held-out estimates to score yet"); return {}
    def score(prefix):
        d = sc.filter(pl.col(f"{prefix}_mu").is_not_null())
        if d.height == 0:
            return None
        inside = ((d["value"] >= d[f"{prefix}_lo90"]) & (d["value"] <= d[f"{prefix}_hi90"])).mean()
        r = d.filter(pl.col("rival_mu").is_not_null()) if "rival_mu" in d.columns else d.head(0)
        rm = float(np.sqrt(((r["value"] - r["rival_mu"]) ** 2).mean())) if r.height else None
        cm = float(np.sqrt(((r["value"] - r[f"{prefix}_mu"]) ** 2).mean())) if r.height else None
        return {"n": d.height, "coverage90": float(inside), "rmse_model_on_rival_cells": cm, "rmse_regime_rival": rm,
                "verdict": "PASS" if (inside >= 0.7 and rm is not None and cm < rm) else "FAIL"}
    res = {"scored_at": dt.datetime.now(dt.timezone.utc).isoformat(), "dry_run": dry, "n_scored": sc.height,
           "primary_channel_model": score("channel"),
           "primary_talk_channel_only": None,
           "secondary_p1_model": score("p1"), "rows": jsonable(sc.to_dicts())}
    talk = sc.filter(pl.col("channel") == "talk") if "channel" in sc.columns else sc.head(0)
    if talk.height:
        sc_all = sc
        sc = talk
        res["primary_talk_channel_only"] = score("channel")
        sc = sc_all
    (outdir / "score.json").write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps({k: v for k, v in res.items() if k != "rows"}, indent=1, default=str))
    return res


def main():
    dry = "--dry-run" in sys.argv
    if not dry and not all(f in sys.argv for f in FLAGS):
        sys.exit("This script uses the LOCKED HOLDOUT. Refusing to run without both flags:\n  " + " ".join(FLAGS) +
                 "\n(or --dry-run for a code-path check on non-holdout periods).")
    outdir = C.OUT / ("confirm_dryrun" if dry else "confirm")
    cal = held_out_calendar(dry)
    print(f"{'DRY RUN (non-holdout stand-ins)' if dry else 'CONFIRMATORY RUN ON THE LOCKED HOLDOUT'}: "
          f"{cal['goal_no'].n_unique()} periods, {cal.height} days")
    doc = stage_predict(cal, outdir, dry)
    stage_score(cal, doc, outdir, dry)


if __name__ == "__main__":
    main()
