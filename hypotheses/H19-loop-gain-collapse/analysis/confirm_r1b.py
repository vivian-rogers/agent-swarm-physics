"""H19 CONFIRMATORY test on the LOCKED HOLDOUT -- ROUND-1B RE-FREEZE of `confirm.py`. Written 2026-10-04 after round 1b,
before any holdout outcome was computed. NOT RUN. `confirm.py` stays byte-for-byte unchanged.

Why a re-freeze (holdout ledger items 2, 4, 5, 9): confirm.py's primary model (`results/frozen_channel_model.json`) was
fitted on the buggy activity_bins; its activity channel (g_eq active rising with x_att) was the operator's day edges
(round 1b: slope +0.18 raw -> -0.03 after the DQ8 trim); its #45 Hawkes cell is blocked (H04 ran Hawkes on #45); and its
#32 / #34 cells collide with H05's executed Curie-Weiss-family run.

Inputs (H19_DATA=r1b, H19_E1=trim, set below before any H19 import):
  * H19's own equal-time gains on activity_bins_fixed, DQ8-trimmed (all-present window + H38's explained joint
    silences from outages_fixed removed) -- scheme/geq_r1b.own_geq_r1b, method *_trim, scored under the frozen names
    H19.geq_active / H19.geq_talk;
  * H02 / H03 round-1b estimates in the frozen fit; H04.K_week and H05 two-block gains dropped (built on the buggy
    table, not re-run by their owners); H04.n_week (chat-based) kept;
  * controls unchanged (scheme/build_controls; k_llm = agent messages delivered per LLM step; no activity_bins input).
  Embeddings, the work ledger, failures, nudge targets and context-ledger visibility are not inputs of this design.

Re-frozen models (fitted ONLY on exploratory, non-holdout round-1b estimates; hash-locked below):
  C1-r1b  PRIMARY: one control for every method -- all six methods (H03.n_talk, H03.n_all, H03.nx_fast, H04.n_week,
          H19.geq_talk, H19.geq_active[trim]) on k_llm, frozen to r1b/results_trim/frozen_kllm_model_r1b.json by
          freeze() below. Reason: round 1b found k_llm the one control with one positive, significant slope for all six
          methods once activity gains are trimmed (post hoc: k_llm was chosen in round 1 from 16 controls).
  C2-r1b  SECONDARY: the round-1 channel model refitted on round-1b trimmed data (talk on k_llm, activity on x_att;
          r1b/results_trim/frozen_channel_model.json). Expected to lose on the activity cells (flat in x_att).
  C3      SECONDARY: the pre-registered P1 model (every method on x_att), refitted on round-1b trimmed data
          (r1b/results_trim/frozen_model.json).
  Pass rule (unchanged): >= 70% of eligible held-out estimates inside their 90% PIs AND held-out RMSE below the
  regime-only rival's on the same cells. Also reported for the talk channel alone.
Eligible held-out periods (re-scoped): #1, #9, #14, #15, #22, #28, #29, #43, #51 tail (2026-09-07 -> 09-21).
  Dropped vs confirm.py: #45 (Hawkes cell blocked, H04 ran Hawkes on #45; item 2), #32 (H05's executed run is
  Curie-Weiss family; item 4), #34 (H05 same modality, pair equal-time correlations; item 4).
  Still colliding (planned, same family; first runner consumes): H38's equal-time gain on these 9 periods (item 5),
  H25 (#1, #9, #14, #15, #22, #43), H12 (#28, #29, #51 tail), H03 Hawkes (#9-#43). Disclose in both cards and LOG.md.

Usage:
  uv run python hypotheses/H19-loop-gain-collapse/analysis/confirm_r1b.py --dry-run       # non-holdout stand-ins #24, #41
  uv run python hypotheses/H19-loop-gain-collapse/analysis/confirm_r1b.py --confirm --i-understand-this-uses-the-locked-holdout
"""
from __future__ import annotations

import os

os.environ["H19_DATA"] = "r1b"
os.environ["H19_E1"] = "trim"
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "2"
os.environ.setdefault("POLARS_MAX_THREADS", "2")

import datetime as dt  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import h19common as C  # noqa: E402
import h19lib as L  # noqa: E402
import explore as E  # noqa: E402
import confirm as CF  # noqa: E402  (frozen helpers predict_one / jsonable; main() is not called)
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

assert C.DATA_VERSION == "r1b" and C.E1_VARIANT == "trim"
FLAGS = ("--confirm", "--i-understand-this-uses-the-locked-holdout")
ELIGIBLE = [1, 9, 14, 15, 22, 28, 29, 43, 51]                 # 51 = the held-out tail only
TAIL_51 = ("2026-09-07", "2026-09-21")
DRY_RUN_PERIODS = [24, 41]
LEDGER_TARGETS = ["G01", "G09", "G14", "G15", "G22", "G28", "G29", "G43", "#51-tail"]
F_KLLM = C.RES / "frozen_kllm_model_r1b.json"                  # r1b/results_trim/
F_CHAN = C.RES / "frozen_channel_model.json"
F_P1 = C.RES / "frozen_model.json"
# sha256 of the three frozen model files, fixed 2026-10-04 after the freeze (exploratory data only). --confirm refuses
# to run if any file differs.
FROZEN_SHA = {"kllm": "22c64e28ebdb76ee530953a021db2af5bbf65c7ecf0a6144e20a05ec9b4b7075",
              "channel_r1b": "a58023353a22c679ec6574aac9f7c7a89e073d3cbbbfc59162e89edf591a7c7e",
              "p1_r1b": "d866bd7d2690a4ff966b375152c60c6faecba6108aca1407326ba43b3f853889"}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def freeze():
    """Fit the k_llm-for-all model on the exploratory round-1b (trimmed) estimates; same estimator as posthoc_channels'
    freeze (method_fits 'x' with regime-only rival levels). Writes once; never overwrites."""
    if F_KLLM.exists():
        return
    est, ctr, ctrd, methods = E.load()
    fr = {"frozen_at": dt.datetime.now(dt.timezone.utc).isoformat(),
          "status": "post hoc (round 1b), frozen for confirmation before any holdout use",
          "data": "H19_DATA=r1b, H19_E1=trim (non-holdout exploratory estimates only)", "x": "k_llm", "methods": {}}
    for m in sorted(methods):
        f = L.method_fits(methods[m]["rows"], "k_llm", models=("x", "regime"), do_lopo=False)
        fx = f["x"]["fit"]
        fr["methods"][m] = {"channel": "talk" if m != "H19.geq_active" else "activity", "x": "k_llm",
                            "names": f["x"]["names"], "b": fx["b"].tolist(), "tau2": fx["tau2"],
                            "cov": (fx["cov"] * max(1.0, fx["q"])).tolist(),
                            "regime_levels": E.regime_levels(methods[m]["rows"], f["regime"]),
                            "median_se": float(np.median([r["s"] for r in methods[m]["rows"]]))}
    F_KLLM.write_text(json.dumps(E.jsonable(fr), indent=1))


def check_frozen(confirm: bool) -> dict:
    now = {"kllm": sha(F_KLLM), "channel_r1b": sha(F_CHAN), "p1_r1b": sha(F_P1)}
    bad = [k for k, v in FROZEN_SHA.items() if v is not None and v != now[k]]
    if confirm and (bad or any(v is None for v in FROZEN_SHA.values())):
        sys.exit(f"frozen model files changed or hashes not fixed: {bad or 'unset'}; refusing to run.")
    return {"now": now, "fixed": FROZEN_SHA, "mismatch": bad}


def held_out_calendar(dry: bool) -> pl.DataFrame:
    cal = pl.read_parquet(C.SHARED / "calendar.parquet").filter((pl.col("window_s") > 0) & pl.col("goal_no").is_not_null())
    if dry:
        sel = cal.filter(pl.col("goal_no").is_in(DRY_RUN_PERIODS) & ~pl.col("holdout"))
        C.assert_no_holdout(sel["pt_date"], sel["goal_no"])
        return sel
    held = C.heldout_goals()
    return cal.filter(pl.col("goal_no").is_in([g for g in ELIGIBLE if g in held and g != 51]) |
                      ((pl.col("goal_no") == 51) & (pl.col("pt_date") >= TAIL_51[0]) & (pl.col("pt_date") < TAIL_51[1])))


def ledger_checks():
    sys.path.insert(0, str(C.ROOT / "infra/shared"))
    import holdout_ledger as HL
    out = {}
    for t in LEDGER_TARGETS:
        c = HL.check("H19", t, "activity timing", ["curie_weiss_gain", "hawkes_branching"])
        out[t] = {"allowed": c["allowed"], "needs_disclosure": c["needs_disclosure"],
                  "prior_runs": sorted({u["hypothesis"] for u in c["prior_runs"]}),
                  "prior_runs_same_family": sorted({u["hypothesis"] for u in c["prior_runs_same_family"]}),
                  "competing_planned": sorted({u["hypothesis"] for u in c["competing_planned"]})}
    return out


def stage_predict(cal, outdir, dry):
    import build_controls as BC
    sealed = outdir / "sealed_predictions.json"
    if sealed.exists() and not dry:
        sys.exit(f"refusing to overwrite sealed predictions: {sealed}")
    MODELS = {"kllm": json.loads(F_KLLM.read_text()), "chan": json.loads(F_CHAN.read_text()), "p1": json.loads(F_P1.read_text())}
    ctr = BC.build(cal, allow_holdout=not dry, write_days=False)
    preds = []
    for row in ctr.iter_rows(named=True):
        g = row["goal_no"]
        pid = "G51tail" if (g == 51 and not dry) else C.pname(g)
        allm = set(MODELS["kllm"]["methods"]) | set(MODELS["chan"]["methods"]) | set(MODELS["p1"]["methods"])
        for m in sorted(allm):
            rec = {"period": pid, "goal_no": g, "method": m, "regime": row["regime"]}
            for key, F in MODELS.items():
                spec = F["methods"].get(m)
                if spec is None:
                    continue
                x = spec.get("x") or F.get("x")
                p = CF.predict_one(spec, row, x)
                rec.update({f"{key}_{k}": v for k, v in p.items()})
                rec[f"{key}_x"] = x
                if key == "kllm":
                    rec["channel"] = spec["channel"]
                    r = CF.predict_one(spec, row, x, rival=True)
                    if r:
                        rec.update({f"rival_{k}": v for k, v in r.items()})
            preds.append(rec)
    doc = {"written_at": dt.datetime.now(dt.timezone.utc).isoformat(), "dry_run": dry, "frozen_sha": {k: sha(p) for k, p in
           (("kllm", F_KLLM), ("channel_r1b", F_CHAN), ("p1_r1b", F_P1))}, "primary": "kllm (C1-r1b)",
           "secondary": ["chan (C2-r1b)", "p1 (C3)"], "controls": CF.jsonable(ctr.to_dicts()), "predictions": preds}
    txt = json.dumps(doc, indent=1, default=str)
    outdir.mkdir(parents=True, exist_ok=True)
    sealed.write_text(txt)
    (outdir / "sealed_predictions.sha256").write_text(hashlib.sha256(txt.encode()).hexdigest() + "\n")
    print(f"sealed {len(preds)} predictions (sha256 {hashlib.sha256(txt.encode()).hexdigest()[:16]}...)")
    return doc


def stage_score(cal, doc, outdir, dry):
    import geq_r1b as GQ
    rng = np.random.default_rng(20261004)
    own = GQ.own_geq_r1b(cal, rng, bins="fixed")
    own = (own.filter(pl.col("method").str.ends_with("_trim"))
           .with_columns(pl.col("method").str.replace("_trim", ""), (1 / pl.col("se") ** 2).alias("w")))
    est = own.group_by("goal_no", "method").agg(((pl.col("w") * pl.col("value")).sum() / pl.col("w").sum()).alias("value"),
                                                (1 / pl.col("w").sum().sqrt()).alias("se"))
    ext = []
    for p in sorted(C.PROC.glob("H*/per_period_estimates.parquet")):
        d = pl.read_parquet(p)
        if {"goal_no", "method", "value", "se", "confirmatory"} <= set(d.columns):
            d = d.filter(pl.col("confirmatory") & pl.col("goal_no").is_in(cal["goal_no"].unique().to_list()))
            hyp = p.parent.name.split("-")[0]
            ext.append(d.select("goal_no", (pl.lit(hyp + ".") + pl.col("method")).alias("method"), "value", "se"))
    if ext:
        est = pl.concat([est] + ext, how="diagonal_relaxed")
    P = pl.DataFrame(doc["predictions"], infer_schema_length=None)
    sc = P.join(est, on=["goal_no", "method"], how="inner")
    if sc.height == 0:
        print("no held-out estimates to score yet")
        return {}

    def score(d, prefix):
        d = d.filter(pl.col(f"{prefix}_mu").is_not_null())
        if d.height == 0:
            return None
        inside = ((d["value"] >= d[f"{prefix}_lo90"]) & (d["value"] <= d[f"{prefix}_hi90"])).mean()
        r = d.filter(pl.col("rival_mu").is_not_null()) if "rival_mu" in d.columns else d.head(0)
        rm = float(np.sqrt(((r["value"] - r["rival_mu"]) ** 2).mean())) if r.height else None
        cm = float(np.sqrt(((r["value"] - r[f"{prefix}_mu"]) ** 2).mean())) if r.height else None
        return {"n": d.height, "coverage90": float(inside), "rmse_model_on_rival_cells": cm, "rmse_regime_rival": rm,
                "verdict": "PASS" if (inside >= 0.7 and rm is not None and cm < rm) else "FAIL"}
    talk = sc.filter(pl.col("channel") == "talk")
    res = {"scored_at": dt.datetime.now(dt.timezone.utc).isoformat(), "dry_run": dry, "n_scored": sc.height,
           "C1-r1b_kllm_primary": score(sc, "kllm"), "C1-r1b_kllm_talk_only": score(talk, "kllm") if talk.height else None,
           "C2-r1b_channel_refit": score(sc, "chan"), "C3_p1_refit": score(sc, "p1"), "rows": CF.jsonable(sc.to_dicts())}
    (outdir / "score.json").write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps({k: v for k, v in res.items() if k != "rows"}, indent=1, default=str))
    return res


def main():
    dry = "--dry-run" in sys.argv
    confirm = all(f in sys.argv for f in FLAGS)
    if dry and confirm:
        sys.exit("choose either --dry-run or the two confirmation flags, not both")
    if not dry and not confirm:
        sys.exit("This script uses the LOCKED HOLDOUT. Refusing to run without both flags:\n  " + " ".join(FLAGS) +
                 "\n(or --dry-run for a code-path check on non-holdout periods).")
    led = ledger_checks()
    if confirm:
        blocked = [t for t, c in led.items() if not c["allowed"]]
        if blocked:
            sys.exit(f"holdout_ledger.check refuses {blocked} (same-family prior run); resolve before running.")
    if dry:
        freeze()                                   # exploratory data only; no-op once written
    fz = check_frozen(confirm)
    print("frozen model sha256:", json.dumps(fz))
    outdir = C.OUT / ("confirm_r1b_dryrun" if dry else "confirm_r1b")
    cal = held_out_calendar(dry)
    print(f"{'DRY RUN (non-holdout stand-ins)' if dry else 'CONFIRMATORY RUN ON THE LOCKED HOLDOUT'}")
    doc = stage_predict(cal, outdir, dry)
    stage_score(cal, doc, outdir, dry)
    (outdir / "ledger.json").write_text(json.dumps(led, indent=1))
    print("ledger:", json.dumps({t: {k: v for k, v in c.items() if k != "competing_planned"} for t, c in led.items()}))


if __name__ == "__main__":
    main()
