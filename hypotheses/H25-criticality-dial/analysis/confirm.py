"""H25 CONFIRMATORY test on the LOCKED HOLDOUT. Written 2026-10-04 at the end of exploratory round 1; NOT RUN.

Holdout reuse policy (hypotheses/holdout.md): a held-out period may confirm a second hypothesis only with committed
predictions, a statistic nobody has examined there, and disclosure. The holdout is crowded:
  * H19's planned confirmation computes g_eq active/talk (the PERIOD MEAN of H25's activity/talk estimator) on #1, #9,
    #14, #15, #22, #28, #29, #32, #34, #43 and the #51 tail. H25 must not compute activity/talk dials there before H19.
  * H12's planned confirmation computes content and activity collective-mode statistics on #28, #29, #32, #34,
    #45-#50 and the #51 tail. H25 avoids those for content.
Hence two stages:
  Stage A (content, runnable once this script and the card are committed): the daily CONTENT dial (F2) on #1, #9, #14,
           #15, #22 (and #43 if estimable). Nobody computes a within-day content co-fluctuation statistic there
           (H20: day-to-day aging on #1; H24: forecast numbers on #14; H12 C7: a participation ratio on #22; disclosed).
  Stage B (activity/talk day-level statistics), GATED: runs only if H19's confirmatory score exists
           (data/processed/H19-loop-gain-collapse/confirm/score.json), and then scores only statistics H19 does not
           compute (per-day subcriticality, within-period heterogeneity), disclosed as reuse.
  H03 agreement on the holdout is scored only if H03 has exported held-out n-hat in H19's shared schema
  (data/processed/H03-*/per_period_estimates.parquet with confirmatory = true); H25 never fits Hawkes models here.

Steps:
  --freeze   (exploratory data only) derive the frozen predictions from round-1 outputs and write
             results/frozen_confirm.json + .sha256. Must be run before any confirmatory run; refuses to overwrite.
  --dry-run  the full pipeline on NON-holdout stand-ins (#24, #27, #41 for Stage A; #23, #42 for Stage B):
             code-path check only, numbers meaningless as confirmation. Writes confirm_dryrun/.
  --confirm --i-understand-this-uses-the-locked-holdout
             the real run. Refuses unless both flags are given, the frozen file exists with a matching hash, and
             this script and the card are committed (git shows no changes to them).

Frozen predictions (filled from round 1 by --freeze; see the card's "Confirmatory design"):
  CA1 (content level transfers): the median daily content dial (F2) of each held-out period lies inside the
      exploratory 5th-95th percentile range of period medians; pass if >= 4 of the 5-6 eligible periods do.
  CA2 (content subcriticality share): the share of held-out days whose content upper bound is < 0.8 lies within
      +-0.2 of the exploratory share.
  CA3 (content above its null): the share of held-out days with content dial above its circular-shift null 95th
      percentile is >= the exploratory share minus 0.2.
  CA4 (size scaling, from post hoc PH1): each held-out period's median content dial is predicted from its median content
      population N alone, g = (N-1) rho / (1 + (N-1) rho) with the frozen exploratory per-pair rho; pass if >= 4 of the
      eligible periods fall within +-0.15 AND the summed squared error beats the constant predictor (exploratory median g).
  CB1 (Stage B, gated): activity and talk dials subcritical (upper bound < 0.8) on >= 95% of held-out days.
  CB2 (Stage B, gated): Cochran's Q p < 0.05 for the activity dial in a share of held-out periods within +-0.25 of
      the exploratory share (periods with >= 5 days).
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import h25common as C  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import dial as D  # noqa: E402

FLAGS = ("--confirm", "--i-understand-this-uses-the-locked-holdout")
STAGE_A = [1, 9, 14, 15, 22, 43]
STAGE_B = [1, 9, 14, 15, 22, 43]  # H19's cells; only day-level statistics H19 does not compute
DRY_A, DRY_B = [24, 27, 41], [23, 42]
FROZEN = C.OUT / "results/frozen_confirm.json"
H19_SCORE = C.PROC / "H19-loop-gain-collapse/confirm/score.json"


def calendar_for(goals: list[int], holdout: bool) -> pl.DataFrame:
    cal = C.calendar_all().filter(pl.col("goal_no").is_in(goals))
    if not holdout:
        cal = cal.filter(~pl.col("holdout") & ~pl.col("hm"))
        C.assert_no_holdout(cal["pt_date"], cal["goal_no"])
    else:
        cal = cal.filter(pl.col("holdout") | pl.col("hm"))
        tail = C.load_holdout()["ne_windows"]
        assert cal.height > 0
    return cal.drop("hm")


def freeze():
    if FROZEN.exists():
        sys.exit(f"refusing to overwrite frozen predictions: {FROZEN}")
    per = pl.read_parquet(C.OUT / "dial_period.parquet")
    daily = pl.read_parquet(C.OUT / "dial_daily.parquet")
    C.assert_no_holdout(daily["pt_date"], daily["goal_no"])
    c = per.filter((pl.col("channel") == "content") & (pl.col("variant") == "F2"))
    cd = daily.filter((pl.col("channel") == "content") & (pl.col("variant") == "F2") & (pl.col("flag") == "ok"))
    a = per.filter((pl.col("channel") == "activity") & (pl.col("variant") == "auto") & (pl.col("k") >= 5))
    bd = daily.filter(pl.col("channel").is_in(["activity", "talk"]) & (pl.col("variant") == "auto") & (pl.col("flag") == "ok"))
    fz = {"written_from": "exploratory round 1 (non-holdout only)",
          "CA1_range": [float(c["median"].quantile(0.05)), float(c["median"].quantile(0.95))],
          "CA2_share_hi_lt_08": float((cd["hi"] < 0.8).mean()),
          "CA3_share_above_null": float((cd["g"] > cd["null_q95"]).mean()),
          "CA4_rho": float(cd.with_columns(((pl.col("VR") - 1) / (pl.col("N") - 1)).alias("r"))["r"].median()),
          "CA4_const": float(c["median"].median()), "CA4_tol": 0.15,
          "CB1_threshold": 0.95, "CB1_exploratory_share": float((bd["hi"] < 0.8).mean()),
          "CB2_share_Q_sig": float((a["p_Q"] < 0.05).mean()) if a.height else None,
          "stage_a_periods": STAGE_A, "stage_b_periods": STAGE_B}
    txt = json.dumps(fz, indent=1)
    FROZEN.parent.mkdir(parents=True, exist_ok=True)
    FROZEN.write_text(txt)
    FROZEN.with_suffix(".sha256").write_text(hashlib.sha256(txt.encode()).hexdigest() + "\n")
    print(txt)


def committed() -> bool:
    files = ["hypotheses/H25-criticality-dial/analysis/confirm.py", "hypotheses/H25-criticality-dial/README.md",
             "hypotheses/H25-criticality-dial/analysis/dial.py"]
    r = subprocess.run(["git", "-C", str(C.ROOT), "status", "--porcelain", *files], capture_output=True, text=True)
    t = subprocess.run(["git", "-C", str(C.ROOT), "ls-files", "--error-unmatch", *files], capture_output=True, text=True)
    return r.stdout.strip() == "" and t.returncode == 0


def content_stage(goals: list[int], holdout: bool) -> pl.DataFrame:
    import build as B  # scheme functions, called in memory; nothing is written to inputs/
    cal = calendar_for(goals, holdout)
    meta, V = B.build_statements(cal)
    ex, EV = B.build_exo(cal)
    meta = meta.with_row_index("_i").filter(~pl.col("dup"))
    rows = []
    for day in cal["pt_date"].to_list():
        s = meta.filter(pl.col("pt_date") == day)
        e = ex.with_row_index("_i").filter(pl.col("pt_date") == day)
        r = D.compute_dial(None, statements=s.select(pl.col("pt_date").alias("day"), "minute", "agent", "window"),
                           statement_vectors=V[s["_i"].to_numpy()].astype(np.float32), channels=("content",),
                           exo_statements=e.select(pl.col("pt_date").alias("day"), "minute") if e.height else None,
                           exo_vectors=EV[e["_i"].to_numpy()].astype(np.float32) if e.height else None,
                           seed=int(hashlib.sha1(day.encode()).hexdigest()[:8], 16))
        for x in r.iter_rows(named=True):
            rows.append({**x, "goal_no": int(cal.filter(pl.col("pt_date") == day)["goal_no"][0])})
    return pl.DataFrame(rows, infer_schema_length=None)


def binary_stage(goals: list[int], holdout: bool) -> pl.DataFrame:
    import build as B
    cal = calendar_for(goals, holdout)
    sp = B.build_spins(cal)
    ms = sp.select(pl.col("pt_date").alias("day"), pl.col("minute").cast(pl.Int32), "agent", (pl.col("state") >= 3).alias("active"),
                   (pl.col("state") == 4).alias("talk"), (pl.col("state") >= 2).alias("any_event"))
    r = D.compute_dial(ms, channels=("activity", "talk"), seed=20261004)
    return r.join(cal.select(pl.col("pt_date").alias("day"), "goal_no"), on="day")


def score(fz: dict, ca: pl.DataFrame, cb: pl.DataFrame | None) -> dict:
    res = {}
    ok = ca.filter(pl.col("flag") == "ok") if "flag" in ca.columns else ca
    med = ok.group_by("goal_no").agg(pl.col("g").median())
    lo, hi = fz["CA1_range"]
    inside = ((med["g"] >= lo) & (med["g"] <= hi)).sum()
    res["CA1"] = {"periods": med.to_dicts(), "inside": int(inside), "n": med.height, "pass": bool(inside >= min(4, med.height))}
    pm = ok.group_by("goal_no").agg(pl.col("g").median(), pl.col("N").median())
    rho = fz["CA4_rho"]
    pred = (pm["N"] - 1) * rho / (1 + (pm["N"] - 1) * rho)
    inside4 = int(((pm["g"] - pred).abs() <= fz["CA4_tol"]).sum())
    sse_m, sse_c = float(((pm["g"] - pred) ** 2).sum()), float(((pm["g"] - fz["CA4_const"]) ** 2).sum())
    res["CA4"] = {"periods": pm.with_columns(pred.alias("pred")).to_dicts(), "inside": inside4, "sse_model": sse_m, "sse_const": sse_c,
                  "pass": bool(inside4 >= min(4, pm.height) and sse_m < sse_c)}
    sh = float((ok["hi"] < 0.8).mean()) if ok.height else float("nan")
    res["CA2"] = {"share": sh, "frozen": fz["CA2_share_hi_lt_08"], "pass": bool(abs(sh - fz["CA2_share_hi_lt_08"]) <= 0.2)}
    an = float((ok["g"] > ok["null_q95"]).mean()) if ok.height else float("nan")
    res["CA3"] = {"share": an, "frozen": fz["CA3_share_above_null"], "pass": bool(an >= fz["CA3_share_above_null"] - 0.2)}
    if cb is not None:
        okb = cb.filter(pl.col("flag") == "ok")
        s1 = float((okb["hi"] < 0.8).mean())
        res["CB1"] = {"share": s1, "pass": bool(s1 >= fz["CB1_threshold"])}
        qs = []
        for g, d in okb.filter(pl.col("channel") == "activity").group_by("goal_no"):
            a = D.aggregate_days(d["g"].to_numpy(), d["se"].to_numpy())
            if a.get("k", 0) >= 5:
                qs.append(a["p_Q"] < 0.05)
        s2 = float(np.mean(qs)) if qs else float("nan")
        res["CB2"] = {"share": s2, "n_periods": len(qs), "frozen": fz["CB2_share_Q_sig"],
                      "pass": bool(qs and fz["CB2_share_Q_sig"] is not None and abs(s2 - fz["CB2_share_Q_sig"]) <= 0.25)}
    else:
        res["stage_B"] = "skipped: H19's confirmatory score not found (gate)"
    h03 = list(C.PROC.glob("H03-*/per_period_estimates.parquet"))
    res["H03_holdout_estimates"] = [str(p) for p in h03] or "absent: H03 agreement not scored"
    return res


def main():
    args = set(sys.argv[1:])
    if "--freeze" in args:
        return freeze()
    dry = "--dry-run" in args
    if not dry and not all(f in args for f in FLAGS):
        sys.exit("This script uses the LOCKED HOLDOUT. Refusing to run without both flags:\n  " + " ".join(FLAGS) +
                 "\n(or --dry-run for the non-holdout code-path check, or --freeze on exploratory outputs).")
    if not FROZEN.exists():
        sys.exit("frozen predictions missing: run --freeze on the exploratory outputs first")
    txt = FROZEN.read_text()
    if hashlib.sha256(txt.encode()).hexdigest() != FROZEN.with_suffix(".sha256").read_text().strip():
        sys.exit("frozen predictions do not match their hash")
    fz = json.loads(txt)
    if not dry and not committed():
        sys.exit("reuse policy: commit this script, dial.py and the card before the confirmatory run")
    out = C.OUT / ("confirm_dryrun" if dry else "confirm")
    out.mkdir(parents=True, exist_ok=True)
    print(f"{'DRY RUN (non-holdout stand-ins)' if dry else 'CONFIRMATORY RUN ON THE LOCKED HOLDOUT'}")
    ca = content_stage(DRY_A if dry else STAGE_A, holdout=not dry)
    ca.write_parquet(out / "stage_a_content.parquet")
    gate = dry or H19_SCORE.exists()
    cb = binary_stage(DRY_B if dry else STAGE_B, holdout=not dry) if gate else None
    if cb is not None:
        cb.write_parquet(out / "stage_b_binary.parquet")
    res = score(fz, ca, cb)
    res["mode"] = "dry-run (numbers meaningless as confirmation)" if dry else "confirmatory"
    (out / "score.json").write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
