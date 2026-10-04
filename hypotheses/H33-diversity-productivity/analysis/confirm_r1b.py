"""H33 confirmatory test on the LOCKED HOLDOUT, RE-FROZEN ON ROUND-1B INPUTS (written 2026-10-04; NOT RUN).

Re-freeze of `confirm.py` (left byte-for-byte untouched; holdout.md ledger item 17). Written before any holdout data
was read. Details and reasons: `CONFIRM_R1B.md`.

What changed vs confirm.py (pipeline = round 1b, `H33_ROUND=r1b`, card section "Round 1b")
  * Output: y = log(1 + DQ4 agent work commits) (`work_daily.commits`: canonical, not imported, author agent, not
    automated), not write turns from artifact mentions. Active minutes are attention, not work (STANDARDS §2).
  * Engaged-minute control from `activity_bins_fixed`, not `activity_bins`.
  * Diversity under both embedding models: PR10 (round-1 column: bge, H12's raw-cosine dedup) and PR10_gte (DQ5
    white32 gte vectors, `statement_flags.self_repeat_gte` dedup); every PR criterion must hold under both.
    Reported, not scored: bge/gte with copies-only and restatement dedups (`statement_flags`).
  * Eligibility: the round-1b rule (output share on work commits; units from #30 on, because work-ledger zeros before
    #30 are ambiguous). Held-out #22, #28, #29 therefore drop out mechanically; #32 (32a/32b), #34, #45-#50 and the
    #51 tail ("51t") remain candidates.
  * Not inputs: context ledger, failures, nudge targets (H33 is an agent-day response curve, no coupling claim).
  * Guard added: holdout-ledger gate (blocks a target with a same-family, same-modality prior run; none found).

Predictions ("-r1b" = changed; credences after round 1b):
  C1-r1b  H33 as stated (P1 rule: spline maximum interior AND two-lines b1 > 0, b2 < 0, both p < 0.05) on work
          commits, under BOTH PR10 (bge) and PR10_gte. Predicted to FAIL (credence it passes 0.08). Reason: outcome and
          second model (round 1b: b1 +0.032, p 0.17; b2 -0.040, p 0.31).
  C2-r1b  no PR10 term (linear, quadratic, spline) improves 5-fold day-blocked CV MSE over FE + controls by >= 1%,
          under both models. Predicted to HOLD (0.75). Reason: outcome and second model (round 1b: linear -0.4%).
  C3-r1b  spline contrast f(x_max) - f(q90) in residual-SD units has 95% upper bound < 0.30, under both models.
          Predicted to HOLD (0.55; lower than 0.65 because the round-1b bge right-side slopes are a #51 property and
          the #51 tail is a target). Reason: outcome and second model.
  C4-r1b  low-side lead: two-lines b1 > 0, one-sided p < 0.05, under both models (0.20). Reason: as C1.
  C5-r1b  #51 lead: in unit 51t, PR15 (bge) two-lines b2 < 0 with p < 0.05, on work commits (0.15; round 1b found
          the right-side drop model-dependent: gte n.s.). PR10_gte and the restatement-dedup variants are reported.
  Reading: H33 is confirmed only if C1-r1b passes. The null reading (no operating point) is confirmed if C1-r1b fails
  AND C2-r1b and C3-r1b hold. Sensitivity (decides nothing): C1-C4 without #34 and #45.

Reuse (hypotheses/holdout.md; ledger L200-L211): executed runs on #32/#34 (H05) and #45-#50 (H02, H04) are activity
timing, another modality. Planned same-family content users (H12, H13, H26, H36 ...) and work-output users (H01, H15)
on most targets: whoever runs first consumes the statistic; disclose in both cards and LOG.md.

Guard: refuses without --confirm --i-understand-this-uses-the-locked-holdout; refuses unless the card and this file
are committed. --dry-run runs the identical pipeline on non-holdout stand-ins (#30, #31, #35, #38, #41, #42, #44 and
#51's last two non-holdout weeks as "51t") into data/processed/H33-diversity-productivity/confirm_r1b_dryrun/.

Usage:
  uv run python hypotheses/H33-diversity-productivity/analysis/confirm_r1b.py --dry-run
  uv run python hypotheses/H33-diversity-productivity/analysis/confirm_r1b.py --confirm --i-understand-this-uses-the-locked-holdout
"""
from __future__ import annotations

import os

os.environ["H33_ROUND"] = "r1b"   # before h33common is imported: commits_w outcome, MIN_GOAL 30
import importlib.util  # noqa: E402
import json  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

import h33lib as H  # noqa: E402,I001
import h33common as C  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

assert C.ROUND == "r1b" and C.Y_PRIMARY == "commits_w" and C.MIN_GOAL == 30


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


E = _load("h33_evaluate", C.HYP / "analysis/evaluate.py")
B = _load("h33_build", C.HYP / "scheme/build.py")
sys.path.insert(0, str(C.ROOT / "infra/shared"))
import holdout_ledger as HL  # noqa: E402

HYP = "H33"
FLAG_A, FLAG_B = "--confirm", "--i-understand-this-uses-the-locked-holdout"
HOLDOUT_GOALS = [22, 28, 29, 32, 34, 45, 46, 47, 48, 49, 50]
HOLDOUT_TAIL = ("2026-09-07", "2026-09-21")
REUSED = {"34", "45"}
STANDIN_GOALS = [30, 31, 35, 38, 41, 42, 44]
STANDIN_TAIL = ("2026-08-24", "2026-09-07")
X_MODELS = {"bge": "pr10", "gte": "pr10_gte"}
X_REPORT = ("pr10_bge_copies", "pr10_gte_copies", "pr10_bge_restate", "pr10_gte_restate")
Y = C.Y_PRIMARY
LEDGER_TARGETS = ["G22", "G28", "G29", "G32", "G34", "G45", "G46", "G47", "G48", "G49", "G50", "#51-tail"]
MODALITY = "message content"


def select_calendar(holdout: bool) -> pl.DataFrame:
    cal = pl.read_parquet(C.SH / "calendar.parquet")
    hm = C.holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    cal = cal.with_columns(pl.Series("hm", hm), pl.col("regime").cast(pl.Utf8))
    goals, tail = (HOLDOUT_GOALS, HOLDOUT_TAIL) if holdout else (STANDIN_GOALS, STANDIN_TAIL)
    in_tail = (pl.col("goal_no") == 51) & (pl.col("pt_date") >= tail[0]) & (pl.col("pt_date") < tail[1])
    sel = cal.filter((pl.col("hm") == holdout) & (pl.col("goal_no").is_in(goals) | in_tail) & (pl.col("n_agent_events") > 0))
    if not holdout:
        assert not any(C.holdout_mask(sel["pt_date"].to_list(), sel["goal_no"].to_list())), "dry run touched the holdout"
        assert not sel["holdout"].any(), "dry run touched a calendar-holdout day"
    unit = (pl.when(in_tail).then(pl.lit("51t"))
            .when((pl.col("goal_no") == 32) & (pl.col("pt_date") < "2026-02-25")).then(pl.lit("32a"))
            .when(pl.col("goal_no") == 32).then(pl.lit("32b"))
            .otherwise(C.unit_expr()))
    return sel.drop("hm").with_columns(unit.alias("unit"))


def committed_or_die():
    paths = [str(C.HYP / "README.md"), str(C.HYP / "analysis/confirm_r1b.py")]
    for p in paths:
        tracked = subprocess.run(["git", "-C", str(C.ROOT), "ls-files", "--error-unmatch", p], capture_output=True).returncode == 0
        dirty = subprocess.run(["git", "-C", str(C.ROOT), "status", "--porcelain", "--", p], capture_output=True, text=True).stdout
        if not tracked or dirty.strip():
            raise SystemExit("REUSE POLICY: commit the H33 card and confirm_r1b.py before the confirmatory run: " + p)


def ledger_gate():
    led = HL.load()
    rep, bad = {}, []
    for t in LEDGER_TARGETS:
        mine = [e for e in led["entries"] if e["hypothesis"] == HYP and e["target"] == t]
        fam = sorted({f for e in mine for f in e["estimator_family"]}) or ["content_alignment", "work_output"]
        r = HL.check(HYP, t, MODALITY, fam)
        same = sorted({x["hypothesis"] for x in r["prior_runs_same_family"] if x["modality"] == MODALITY})
        rep[t] = {"family": fam, "allowed": r["allowed"], "same_family_same_modality_runs": same,
                  "prior_runs": sorted({x["hypothesis"] for x in r["prior_runs"]}),
                  "competing_planned": sorted({x["hypothesis"] for x in r["competing_planned"]})}
        if same:
            bad.append(t)
    return rep, bad


def augment_r1b(cal: pl.DataFrame, root, guard: bool):
    """scheme/build.py build_r1b, parameterized for the selected days and root: engaged minutes from
    activity_bins_fixed, DQ4 work outcomes, PR10 under both models and three dedups. guard=False only on the holdout."""
    days = sorted(set(cal["pt_date"].to_list()))
    if guard:
        C.refuse_holdout(days, "calendar")
    ad = C.load_agent_day(root)
    if guard:
        C.refuse_holdout(ad["pt_date"].unique().to_list(), "agent_day")
    ab = (pl.scan_parquet(C.SH / "activity_bins_fixed.parquet")
          .filter(pl.col("pt_date").is_in(days) & (pl.col("agent") != C.CLAUDE_CODE_AGENT))
          .group_by("pt_date", "agent").agg((pl.col("state") >= 3).sum().alias("engaged_fx")).collect())
    wd = (pl.read_parquet(C.SH / "work_daily.parquet")
          .filter((pl.col("level") == "agent") & pl.col("pt_date").is_in(days))
          .select("pt_date", "agent", pl.col("commits").alias("commits_w"), pl.col("distinct_files").alias("files_w"),
                  pl.col("lines_changed_nobulk").alias("lines_nb")))
    st = (pl.read_parquet(C.EMB / "statements.parquet").with_row_index("srow")
          .filter((pl.col("kind") == "chat") & pl.col("pt_date").is_in(days) & (pl.col("agent") != C.CLAUDE_CODE_AGENT)))
    if guard:
        C.refuse_holdout(st["pt_date"].unique().to_list(), "statements")
    fl = pl.read_parquet(C.SH / "statement_flags.parquet", columns=["srow", "self_repeat_bge", "self_repeat_gte", "self_repeat_both"])
    st = st.join(fl, on="srow", how="left")
    emb = {m: np.load(C.EMB / f"statements_white32_{m}.npy", mmap_mode="r") for m in ("bge_small", "gte_modernbert")}
    recs = {}
    for name, (model, drop) in B.VARIANTS.items():
        kept = st.filter(~drop.fill_null(False))
        Em = emb[model]
        for (d, a), g in kept.sort("t").group_by(["pt_date", "agent"]):
            Yv = np.asarray(Em[g["srow"].to_numpy()], dtype=np.float64)
            rng = np.random.default_rng([C.SEED, C.stable_seed([d, int(a), name])])
            r = B.L12.pr_rarefied(Yv, np.zeros(len(Yv), dtype=np.int64), C.N_PR, None, C.DRAWS, rng, erank=False)
            rec = recs.setdefault((d, int(a)), {"pt_date": d, "agent": int(a)})
            rec[name] = r["pr"]
    prv = pl.DataFrame(list(recs.values())).with_columns(pl.col("agent").cast(pl.Int8))
    prv = prv.with_columns([pl.col(c).cast(pl.Float32).fill_nan(None) for c in B.VARIANTS])
    ad = (ad.join(ab, on=["pt_date", "agent"], how="left").join(wd, on=["pt_date", "agent"], how="left")
          .join(prv, on=["pt_date", "agent"], how="left")
          .with_columns(pl.col("engaged_min").alias("engaged_min_r1"), pl.col("engaged_fx").fill_null(0).alias("engaged_min"),
                        *[pl.col(c).fill_null(0).cast(pl.Int32) for c in ("commits_w", "files_w")], pl.col("lines_nb").fill_null(0))
          .drop("engaged_fx"))
    for u in sorted(ad["unit"].unique().to_list()):
        g = int(u.rstrip("abt"))
        od = root / C.unit_dir(u).name
        od.mkdir(parents=True, exist_ok=True)
        ad.filter(pl.col("goal_no") == g).write_parquet(od / "agent_day.parquet", compression="zstd")
    return ad


def tests_x(root, holdout: bool, x_col: str, exclude=frozenset()):
    units = None
    if exclude:
        units = [u for u in H.eligibility(C.load_agent_day(root)).filter("eligible")["unit"].to_list() if u not in exclude]
    ad, x, y, Z, au, day = H.load_pooled(x_col, Y, units=units, root=root, guard=not holdout)
    out = {"x": x_col, "units": sorted(set(ad["unit"].to_list())), "n": int(len(x))}
    if len(x) < 30:
        return {**out, "C1": {"pass": None}, "C2": {"pass": None}, "C3": {"pass": None}, "C4": {"pass": None}}
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
    return out


def both(rs, key):
    v = [r[key]["pass"] for r in rs.values()]
    return None if any(x is None for x in v) else bool(all(v))


def tests(root, holdout: bool, exclude=frozenset()):
    per = {m: tests_x(root, holdout, xc, exclude) for m, xc in X_MODELS.items()}
    out = {"per_model": per, **{f"{k}-r1b": both(per, k) for k in ("C1", "C2", "C3", "C4")}}
    if not exclude:
        el = H.eligibility(C.load_agent_day(root)).filter("eligible")["unit"].to_list()
        out["C5-r1b"] = {"pass": None, "note": "unit 51t not eligible"}
        if "51t" in el:
            res5 = {}
            for xc in ("pr15", "pr10_gte", "pr10_bge_restate", "pr10_gte_restate"):
                a5, x5, y5, Z5, au5, d5 = H.load_pooled(xc, Y, units=["51t"], root=root, guard=not holdout)
                res5[xc] = E.shape_block(x5, y5, Z5, au5, d5)[0]["two_lines"] if len(x5) >= 30 else None
            b5 = res5["pr15"]
            out["C5-r1b"] = {"pass": None if b5 is None else bool(b5["b2"] < 0 and b5["p2"] < 0.05), "two_lines": res5}
        out["report_dedup_variants"] = {}
        for xc in X_REPORT:
            try:
                a_, x_, y_, Z_, au_, d_ = H.load_pooled(xc, Y, root=root, guard=not holdout)
                tl = E.shape_block(x_, y_, Z_, au_, d_)[0]["two_lines"]
                out["report_dedup_variants"][xc] = {k: tl[k] for k in ("b1", "p1", "b2", "p2", "xc")}
            except Exception as ex:  # noqa: BLE001  (reported, decides nothing)
                out["report_dedup_variants"][xc] = f"failed: {ex}"
    return out


def run(holdout: bool):
    root = C.OUT_R1 / ("confirm_r1b" if holdout else "confirm_r1b_dryrun")
    t0 = time.time()
    gate, bad = ledger_gate()
    if holdout and bad:
        raise SystemExit(f"Refusing: same-family same-modality prior run on {bad} (holdout ledger); needs Vivian's ruling")
    cal = select_calendar(holdout)
    if not holdout:
        print(f"DRY RUN r1b (non-holdout stand-ins): {cal.height} days, units {sorted(set(cal['unit'].to_list()))}", flush=True)
    B.build(cal, root, guard=not holdout)          # round-1 columns (PR10/PR15 bge, H12 dedup) for the selected days
    augment_r1b(cal, root, guard=not holdout)      # round-1b columns
    elig = H.eligibility(C.load_agent_day(root))
    elig.write_parquet(root / "eligibility.parquet")
    res = {"holdout": holdout, "ledger": gate, "eligibility": elig.sort("unit").to_dicts() if not holdout else None,
           "primary": tests(root, holdout)}
    res["sensitivity_without_34_45"] = tests(root, holdout, exclude=frozenset(REUSED)) if holdout else None
    p = res["primary"]
    res["reading"] = ("H33 confirmed (inverted U, both models)" if p["C1-r1b"] else
                      "null reading confirmed (no operating point)" if (p["C2-r1b"] and p["C3-r1b"]) else
                      "neither H33 nor the null reading confirmed")
    res["secs"] = round(time.time() - t0, 1)
    (root / "confirm_results.json").write_text(json.dumps(res, indent=1, default=float))
    C.write_provenance("hypotheses/H33-diversity-productivity/analysis/confirm_r1b.py",
                       ["H33 round-1 build on selected days", "activity_bins_fixed", "work_daily", "embeddings/statements",
                        "embeddings/statements_white32_{bge_small,gte_modernbert}", "statement_flags", "calendar"],
                       {"holdout": holdout, "goals": HOLDOUT_GOALS if holdout else STANDIN_GOALS,
                        "tail": HOLDOUT_TAIL if holdout else STANDIN_TAIL, "y": Y, "x_models": X_MODELS},
                       path=root / "_provenance.json")
    if holdout:
        print(json.dumps({k: res["primary"].get(k) for k in ("C1-r1b", "C2-r1b", "C3-r1b", "C4-r1b")}, default=float))
        print(res["reading"])
        return
    summ = {m: {"units": r["units"], "n": r["n"], "C1": r["C1"]["pass"], "b1": r["C1"]["two_lines"]["b1"],
                "p1": r["C1"]["two_lines"]["p1"], "b2": r["C1"]["two_lines"]["b2"], "p2": r["C1"]["two_lines"]["p2"],
                "cv_rel": r["C2"]["rel_change"], "C3_upper95_sd": r["C3"]["upper95_sd"], "C4_p": r["C4"]["p_one_sided"]}
            for m, r in p["per_model"].items()}
    print(json.dumps({"scores": {k: p[k] for k in ("C1-r1b", "C2-r1b", "C3-r1b", "C4-r1b")},
                      "C5-r1b": p["C5-r1b"]["pass"], "per_model": summ, "reading": res["reading"],
                      "secs": res["secs"]}, indent=1, default=float))


def main(argv):
    if "--dry-run" in argv and not (FLAG_A in argv or FLAG_B in argv):
        run(holdout=False)
        return
    if FLAG_A in argv and FLAG_B in argv and "--dry-run" not in argv:
        committed_or_die()
        run(holdout=True)
        return
    raise SystemExit(f"Refusing: the confirmatory run uses the locked holdout. Pass {FLAG_A} {FLAG_B} (needs sign-off), "
                     "or --dry-run for non-holdout stand-ins.")


if __name__ == "__main__":
    main(sys.argv[1:])
