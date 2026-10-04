"""H86 confirmatory test on the locked holdout. WRITTEN 2026-10-04 after round 1, NOT RUN on the holdout.

  uv run python hypotheses/H86-taylor-law-field-gauge/analysis/confirm.py --dry-run
      runs the full pipeline on non-holdout units (exploration data only).
  uv run python hypotheses/H86-taylor-law-field-gauge/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
      rebuilds the bin tables with held-out rows in memory (scheme/build.py, include_holdout=True), keeps ONLY held-out
      units, seals the frozen predictions (confirm/confirm_sealed.json, SHA-256) before reading any held-out row, then
      scores. Refuses without BOTH flags; checks the holdout ledger.

Round-1 picture under test: across agents, activity variance grows no faster than the mean (Taylor b <= ~1, c_T <= 0:
faster agents are more regular), so the HH's c_T and b are not field gauges; the pair-covariance coefficient c_x is,
and trimming removes most of it in regime III; the shared share of excess variance is small (private variance
dominates); talk shares more of its variance than activity.

Targets: held-out period units (goal periods #1, #9, #14, #15, #22, #28, #29, #32, #34, #43, #45-#50 and NE-window units),
and the NE21+NE23 window (2026-06-08 -> 07-06: hours reversals) for C5.
Frozen predictions (medians over eligible held-out units; activity channel, 15-min bins unless stated):
  C1 Taylor across agents is not multiplicative: median b_raw < 1.2 and median c_T,raw < 0.05.
  C2 trimming removes the shared field in regime III: median r_x = 1 - c_x,trim / c_x,raw >= 0.5 over regime-III units
     with c_x,raw > 0.01 (descriptive if < 5 such units), and median c_x,trim < 0.01.
  C3 private variance dominates: median phi_trim < 0.15 in regime III.
  C4 talk shares more: phi_msg,trim > phi_activity,trim in >= 2/3 of units with >= 300 messages.
  C5 (descriptive) NE21+NE23: mean daily c_x,trim differs by < 0.01 between the longer-window and shorter-window days.
  Overall: CONFIRMED if C1, C2 and C3 pass.
Reuse disclosure: the NE21+NE23 window is targeted by H02/H04/H05-type activity statistics (curie_weiss_gain family);
H86's statistic is the pair-covariance coefficient of counts (spectral/equal-time family overlap possible): disclose.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h86lib as L  # noqa: E402

OUTD = L.DATA / "confirm"
PRED = {"C1": "median b_raw < 1.2 and median c_T,raw < 0.05 (activity)",
        "C2": "regime III: median r_x >= 0.5 (units with c_x,raw > 0.01) and median c_x,trim < 0.01",
        "C3": "regime III: median phi_trim < 0.15",
        "C4": "phi_msg,trim > phi_act,trim in >= 2/3 of units with >= 300 messages",
        "C5": "NE21+NE23: |mean daily c_x,trim (long - short window days)| < 0.01 (descriptive)",
        "overall": "C1 & C2 & C3"}


def unit_stats(b15: pl.DataFrame, units: pl.DataFrame) -> pl.DataFrame:
    rows = []
    for unit, regime in units.select("unit_id", "regime").iter_rows():
        d = b15.filter(pl.col("unit_id") == unit)
        if d.height == 0:
            continue
        for ch in ("activity", "msg"):
            for grid in ("raw", "trim"):
                sub = d if grid == "raw" else d.filter(pl.col("trim"))
                if sub.height == 0:
                    continue
                Y, days, _ = L.matrix(sub, ch)
                st = L.taylor(Y, days, ad=False)
                rows.append({"unit_id": unit, "regime": regime, "channel": ch, "grid": grid, "nmsg": int(d["msg"].sum()),
                             **{k: float(st.get(k, np.nan)) for k in ("b", "c_T", "c_x", "phi")}})
    return pl.DataFrame(rows)


def score(b15: pl.DataFrame, units: pl.DataFrame, cal: pl.DataFrame) -> dict:
    s = unit_stats(b15, units)
    a = s.filter(pl.col("channel") == "activity").pivot(on="grid", index=["unit_id", "regime"], values=["b", "c_T", "c_x", "phi"])
    a3 = a.filter(pl.col("regime") == "III")
    sx = a3.filter(pl.col("c_x_raw") > 0.01)
    rx = (1 - sx["c_x_trim"] / sx["c_x_raw"]).drop_nans()
    res = {"n_units": a.height, "b_raw_med": float(a["b_raw"].median()), "cT_raw_med": float(a["c_T_raw"].median()),
           "rx_III_med": float(rx.median()) if len(rx) else None, "n_rx": len(rx),
           "cx_trim_III_med": float(a3["c_x_trim"].median()) if a3.height else None,
           "phi_trim_III_med": float(a3["phi_trim"].median()) if a3.height else None}
    res["C1"] = bool(res["b_raw_med"] < 1.2 and res["cT_raw_med"] < 0.05)
    res["C2"] = bool(res["rx_III_med"] is not None and res["rx_III_med"] >= 0.5 and res["cx_trim_III_med"] < 0.01)
    res["C2_descriptive"] = len(rx) < 5
    res["C3"] = bool(res["phi_trim_III_med"] is not None and res["phi_trim_III_med"] < 0.15)
    m = s.filter(pl.col("grid") == "trim").pivot(on="channel", index=["unit_id", "nmsg"], values="phi").filter(pl.col("nmsg") >= 300)
    m = m.drop_nulls(["msg", "activity"]).filter(pl.col("msg").is_not_nan() & pl.col("activity").is_not_nan())
    res["C4_share"] = float((m["msg"] > m["activity"]).mean()) if m.height else None
    res["C4"] = bool(res["C4_share"] is not None and res["C4_share"] >= 2 / 3)
    # C5: NE21+NE23 window days by window length
    w = cal.filter(pl.col("pt_date").is_between(pl.lit("2026-06-08"), pl.lit("2026-07-05")))
    if w.height:
        d = b15.filter(pl.col("pt_date").is_in(w["pt_date"].to_list()) & pl.col("trim"))
        vals = []
        for day in d["pt_date"].unique().to_list():
            Y, days, _ = L.matrix(d.filter(pl.col("pt_date") == day), "activity")
            vals.append((day, L.taylor(Y, days, min_cells=4, ad=False).get("c_x", np.nan)))
        if vals:
            dv = pl.DataFrame(vals, schema=["pt_date", "c_x"], orient="row").join(w.select("pt_date", "window_s"), on="pt_date")
            med_w = dv["window_s"].median()
            lo, hi = dv.filter(pl.col("window_s") <= med_w)["c_x"].mean(), dv.filter(pl.col("window_s") > med_w)["c_x"].mean()
            res["C5"] = {"long_minus_short": (hi - lo) if hi is not None and lo is not None else None, "n_days": dv.height}
    res["overall"] = bool(res["C1"] and res["C2"] and res["C3"])
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    a = ap.parse_args()
    OUTD.mkdir(parents=True, exist_ok=True)
    import build as Bld  # scheme/build.py
    pu = pl.read_parquet(L.ROOT / "data/processed/shared/period_units.parquet")
    cal = pl.read_parquet(L.ROOT / "data/processed/shared/calendar.parquet").select("pt_date", "window_s")
    if a.dry_run and not a.confirm:
        b15, _, _ = Bld.build(include_holdout=False)
        res = {"mode": "dry-run (non-holdout units)", "predictions": PRED, **score(b15, pu.filter(~pl.col("holdout")), cal)}
        (OUTD / "confirm_dryrun.json").write_text(json.dumps(res, indent=1, default=float))
        print(json.dumps(res, indent=1, default=float))
        return
    if not (a.confirm and a.ack):
        sys.exit("refusing: confirmatory runs need --confirm AND --i-understand-this-uses-the-locked-holdout "
                 "(and Vivian's sign-off)")
    sys.path.insert(0, str(L.ROOT / "infra" / "shared"))
    import holdout_ledger as HL
    held = pu.filter(pl.col("holdout"))
    for tgt in [f"G{g:02d}" for g in sorted(set(held["goal_no"].to_list()))] + ["NE21+NE23"]:
        chk = HL.check("H86", tgt, "activity count covariance", "spectral_mode")
        if not chk["allowed"]:
            sys.exit(f"ledger refuses {tgt}: {chk['prior_runs_same_family']}")
        if chk["needs_disclosure"]:
            print(f"{tgt}: disclosure needed (prior/competing uses)")
    sealed = {"hypothesis": "H86", "sealed_at": dt.datetime.now(dt.timezone.utc).isoformat(), "predictions": PRED,
              "sha256": hashlib.sha256(json.dumps(PRED, sort_keys=True).encode()).hexdigest()}
    (OUTD / "confirm_sealed.json").write_text(json.dumps(sealed, indent=1))
    b15, _, _ = Bld.build(include_holdout=True)
    b15 = b15.filter(pl.col("unit_id").is_in(held["unit_id"].to_list()))
    res = {"mode": "CONFIRMATORY (held-out units only)", "sealed": sealed, **score(b15, held, cal)}
    (OUTD / "confirm_result.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
