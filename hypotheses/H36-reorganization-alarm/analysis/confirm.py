"""H36 confirmatory test on the locked holdout (WRITTEN, NOT RUN in round 1).

Refuses to touch held-out days unless called with BOTH flags:
    --confirm --i-understand-this-uses-the-locked-holdout
Without them it runs a DRY RUN on non-holdout stand-ins (the exploratory goal kickoffs and placebo days), which checks
the code path and prints what the criteria would say in-sample. Dry-run output: data/processed/H36-reorganization-alarm/
confirm_dryrun/confirm.json. Confirm output: .../confirm/confirm.json.

Frozen rules (card, "Confirmatory predictions", written 2026-10-04 before any holdout access):
- Statistics, masks, surrogates, trailing baseline (10 days, Gaussian-consistent trimmed SD), families and thresholds are
  exactly h36lib/build.py as of round 1. In confirm mode the trailing baseline runs over ALL active days in time order
  (held-out and not), which is what an operator would do.
- Targets: goal kickoffs whose day 0 is held out (#9, #14, #15, #22, #28, #29, #32, #34, #43, #45-#50).
  Placebos: held-out active days >= 3 active days from every catalogued event.
- C1 (primary, pre-registered alarm): AUC(Z_phys day 0 vs placebo days) >= 0.60 AND hit rate (Z_phys >= 2.0 on days
  -1..+1) > placebo window FAR.
- C2 (content channel): AUC(Z_cont day 0) >= 0.65 with bootstrap 95% CI lower bound > 0.5.
- C3 (operator rule, post hoc candidate from round 1): alarm if R1 >= 3.0 or Z_cont >= 2.0 on any of days -1..+1:
  hit rate >= 0.40 AND placebo window FAR <= 0.10.
- C4 (rival ordering): AUC(R1 day 0) > AUC(Z_phys day 0).
- C5 (activity channel carries no goal signal): AUC(Z_act day 0) <= 0.65.
- C6 (descriptive): alarm table for held-out NEs (NE12/NE35 room cut, #voted-out, NE30, NE13, NE14 start, NE19-NE26,
  NE37, NE01, NE05, NE08).
Overall: CONFIRMED if C1 and C2 pass; PARTIAL if exactly one of C1, C2 passes; NOT CONFIRMED otherwise. C3-C5 are
reported as secondary.

Reuse policy (hypotheses/holdout.md): several held-out periods are targeted by other hypotheses' confirm scripts
(#34: H01, H05, H07, H12, H19, H21; #45: H02 run, H23 planned; #14, #15, #22, #28, #43 by H13, H20, H24 and others).
H36's observables are new statistics (within-day surrogate-excess co-fluctuation of activity, behavior and content;
trailing-z alarm on them). R1 (day-to-day content centroid shift) is closest to H20's two-time content correlation and
H12's participation ratio: disclose in both cards and LOG.md before running, and commit this script and the card first.

Usage: uv run python hypotheses/H36-reorganization-alarm/analysis/confirm.py               # dry run (non-holdout)
       uv run python hypotheses/H36-reorganization-alarm/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
"""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h36lib as L  # noqa: E402
import build as B  # noqa: E402
import evaluate as E  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

GOAL_TARGETS_HOLDOUT = [9, 14, 15, 22, 28, 29, 32, 34, 43, 45, 46, 47, 48, 49, 50]
NE_TARGETS_HOLDOUT = ["NE12", "NE35", "NE-voted-out", "NE30", "NE13", "NE14", "NE19", "NE20", "NE21", "NE22", "NE23",
                      "NE24", "NE25", "NE26", "NE37", "NE01", "NE05", "NE08"]
RULES = {"C1_auc": 0.60, "C2_auc": 0.65, "C3_hit": 0.40, "C3_far": 0.10, "C5_auc": 0.65}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    confirm = a.confirm and a.ack
    if a.confirm != a.ack:
        sys.exit("refusing: the confirmatory run needs BOTH --confirm and --i-understand-this-uses-the-locked-holdout")
    out_dir = L.OUT / ("confirm" if confirm else "confirm_dryrun")
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(L.SEED + 99)

    cal = B.calendar()
    ev, allev = B.catalog(cal)
    if confirm:
        print("CONFIRMATORY RUN on the locked holdout (reuse policy: see docstring).")
        days = cal.filter(pl.col("goal_no") > 0)
    else:
        print("DRY RUN on non-holdout stand-ins (no held-out day is read).")
        days = cal.filter(~pl.col("holdout") & (pl.col("goal_no") > 0))
        assert not any(L.holdout_mask(days["pt_date"].to_list(), days["goal_no"].to_list()))
    payloads, use_h38, h38prov, cons = B.make_payloads(days)
    with ProcessPoolExecutor(max_workers=min(2, a.workers)) as ex:
        res = list(ex.map(B.day_worker, payloads, chunksize=4))
    st = pl.DataFrame(res, infer_schema_length=None)
    base = days.select("aday", "pt_date", "goal_no", "regime", "weekday", "gap_days", "monday", "window_s", "documented_hours", "holdout")
    st = base.join(st, on="aday", how="inner").join(cons, on="pt_date", how="left").sort("aday")
    st = B.add_rivals(st, cal, days["pt_date"].to_list(), allow_holdout_prev=confirm)
    if not confirm:
        assert not st["holdout"].any()
    sc = E.compute_scores(st)
    aday = st["aday"].to_numpy(); pos = {int(x): i for i, x in enumerate(aday)}
    hold = st["holdout"].to_numpy()
    ev_days = np.unique(allev["aday0"].drop_nulls().to_numpy())
    dist = np.array([np.min(np.abs(ev_days - x)) for x in aday])
    okz = np.isfinite(sc["Z_phys"])
    role = hold if confirm else ~hold
    placebo = role & (dist >= L.PLACEBO_DIST) & okz
    if confirm:
        tg = ev.filter((pl.col("cls") == "goal") & pl.col("ref").is_in([f"#{g}" for g in GOAL_TARGETS_HOLDOUT]))
    else:
        tg = ev.filter((pl.col("cls") == "goal") & ~pl.col("holdout0"))

    def v(k, c):
        i = pos.get(int(c))
        return np.nan if i is None else float(sc[k][i])

    def win(k, c, thr):
        vals = [v(k, c + o) for o in (-1, 0, 1)]
        fin = [x for x in vals if np.isfinite(x)]
        return (any(x >= thr for x in fin), len(fin))

    def rule3(c):
        hits = [(v("R1", c + o) >= 3.0) or (v("Z_cont", c + o) >= 2.0) for o in (-1, 0, 1)]
        return any(hits)

    cent = tg["aday0"].drop_nulls().to_list()
    d0 = {k: np.array([v(k, c) for c in cent]) for k in ["Z_phys", "Z_cont", "Z_act", "R1"]}
    pc = aday[placebo]
    out = {"mode": "confirm" if confirm else "dryrun", "n_targets": len(cent), "n_placebo": int(placebo.sum()),
           "mask": "H38" if use_h38 else "fallback", "h38_built_at": h38prov}
    for k in d0:
        out[f"auc_{k}"] = L.auc(d0[k], sc[k][placebo])
        out[f"auc_{k}_ci"] = L.auc_ci(d0[k], sc[k][placebo], rng, 2000)
    hits = [win("Z_phys", c, 2.0) for c in cent]
    out["C1_hit"] = float(np.mean([h for h, n in hits if n]))
    out["C1_far_win"] = float(np.mean([win("Z_phys", c, 2.0)[0] for c in pc]))
    out["C3_hit"] = float(np.mean([rule3(c) for c, (h, n) in zip(cent, hits) if n]))
    out["C3_far_win"] = float(np.mean([rule3(c) for c in pc]))
    out["C1"] = bool(out["auc_Z_phys"] >= RULES["C1_auc"] and out["C1_hit"] > out["C1_far_win"])
    out["C2"] = bool(out["auc_Z_cont"] >= RULES["C2_auc"] and out["auc_Z_cont_ci"][0] > 0.5)
    out["C3"] = bool(out["C3_hit"] >= RULES["C3_hit"] and out["C3_far_win"] <= RULES["C3_far"])
    out["C4"] = bool(out["auc_R1"] > out["auc_Z_phys"])
    out["C5"] = bool(out["auc_Z_act"] <= RULES["C5_auc"])
    out["overall"] = "CONFIRMED" if out["C1"] and out["C2"] else ("PARTIAL" if out["C1"] or out["C2"] else "NOT CONFIRMED")
    # C6 descriptive
    netab = []
    sub = ev.filter(pl.col("ref").is_in(NE_TARGETS_HOLDOUT)) if confirm else ev.filter(pl.col("cls").is_in(["room", "scaffold"]) & ~pl.col("holdout0"))
    for r in sub.iter_rows(named=True):
        c = r["aday0"]
        netab.append({"ref": r["ref"], "pt_date0": r["pt_date0"], "Z_phys": [v("Z_phys", c + o) for o in (-1, 0, 1)],
                      "Z_cont": [v("Z_cont", c + o) for o in (-1, 0, 1)], "R1": [v("R1", c + o) for o in (-1, 0, 1)],
                      "alarm": win("Z_phys", c, 2.0)[0], "rule3": rule3(c)})
    out["C6"] = netab
    (out_dir / "confirm.json").write_text(json.dumps(out, indent=1, default=lambda o: None if isinstance(o, float) and not np.isfinite(o) else str(o)))
    L.write_provenance(f"hypotheses/H36-reorganization-alarm/analysis/confirm.py ({out['mode']})",
                       ["activity_bins", "calendar", "kicks", "rooms", "rooms_timeline", "embeddings"],
                       {"mode": out["mode"], "rules": RULES}, path=out_dir / "_provenance.json")
    print(json.dumps({k: v_ for k, v_ in out.items() if k != "C6"}, indent=1, default=str))


if __name__ == "__main__":
    main()
