"""H50 confirmatory run on the LOCKED HOLDOUT. Written 2026-10-04 (round 1); NOT RUN.

Guard: runs on held-out data only with BOTH `--confirm` and the environment variable H50_CONFIRM=1. Without them it
refuses. `--dry-run` runs the identical pipeline on non-holdout stand-in units and writes to a scratch directory, so the
code path is tested without touching the holdout.

Frozen predictions (from round 1, 2026-10-04; thresholds fixed here, not tuned on holdout data):
  CP1  Gated talk coupling: pooled J1 (talk; W = 1.5 x median call interval; placebo-corrected) > 0 at 95% in >= 60% of
       held-out goal periods with >= 2,000 (message, recipient) pairs; no unit with J1 < 0 at 95%.
  CP2  Activity co-movement is a schedule field: activity field excess (full window, f_F - f_F,null) > 0.10 in >= 80%
       of held-out periods; median edges-alone field excess >= 0.40.
  CP3  Talk co-movement is coupling-dominated: CF coupling share f_C (talk, span) > talk field excess in >= 70% of
       held-out units with talk S > 0.05.
  CP4  NE23 (nudger off 2026-06-13..06-14, inside the NE21+NE23 window): nudge -> target talk J1 > 0 on nudger-on days
       (06-08..06-12, 06-15..06-19); peer J1 ratio off/on in [0.5, 2]; activity span rho off/on within +-25%;
       day-start onset IQR ratio off/on in [0.5, 2]. (Low power: the off days are a weekend session of one room.)
  CP5  (post hoc pattern from round 1, flagged as such) Kernel shape: regime-III pooled hop-2 increment J2 < 0
       (partial decay after the read-out step); regime-I pooled J2 >= 0 (continuing rise).

Reuse policy (hypotheses/holdout.md): #45 was used by H02 (activity couplings) and H23 (message content); #46-#50 by H04
(NE21 branching ratio, NE23 manipulation check). H50's statistics (the read-out jump in talk at call boundaries, the
field excess of the edge inputs, the CF coupling share) are different statistics that nobody has computed on these
periods. Disclose in the card and LOG.md before running.

Usage:
  uv run python hypotheses/H50-field-vs-coupling-transfer-lag/analysis/confirm.py --dry-run
  H50_CONFIRM=1 uv run python hypotheses/H50-field-vs-coupling-transfer-lag/analysis/confirm.py --confirm
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ.setdefault(_v, "2")

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import build as B  # noqa: E402
import run_unit as RU  # noqa: E402

ROOT = HERE.parents[2]
SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H50-field-vs-coupling-transfer-lag/confirm"
SCRATCH = Path(os.environ.get("TMPDIR", "/tmp")) / "h50_confirm_dryrun"
HOLDOUT_GOALS = json.loads((ROOT / "hypotheses/holdout.json").read_text())["goal_periods_held_out"]   # all 16
NE23_OFF = ("2026-06-13", "2026-06-14")
NE23_ON = [("2026-06-08", "2026-06-12"), ("2026-06-15", "2026-06-19")]
STANDINS = dict(regime_III=["42a", "44a"], regime_I=["21a", "24"], ne23_on="NE43B", ne23_off="NE43C")
FROZEN = dict(CP1=dict(frac_periods=0.60, min_pairs=2000), CP2=dict(fFex=0.10, frac=0.80, edges_median=0.40),
              CP3=dict(frac=0.70, min_S=0.05), CP4=dict(ratio=(0.5, 2.0), rho=0.25), CP5="J2_III<0, J2_I>=0 (post hoc)")


def holdout_units():
    """Holdout period units (period_units rows with holdout) of the target goals, + NE23 on/off pseudo-units."""
    pu = pl.read_parquet(SH / "period_units.parquet").filter(pl.col("goal_no").is_in(HOLDOUT_GOALS) | pl.col("holdout"))
    rows = [dict(unit=f"H{r['unit_id']}", goal_no=r["goal_no"], regime=r["regime"], days=list(r["days"]), kind="holdout")
            for r in pu.iter_rows(named=True)]
    cal = pl.read_parquet(SH / "calendar.parquet")
    off = cal.filter((pl.col("pt_date") >= NE23_OFF[0]) & (pl.col("pt_date") <= NE23_OFF[1]))["pt_date"].to_list()
    on = []
    for a, b in NE23_ON:
        on += cal.filter((pl.col("pt_date") >= a) & (pl.col("pt_date") <= b))["pt_date"].to_list()
    rows += [dict(unit="HNE23off", goal_no=46, regime="III", days=off, kind="ne23"),
             dict(unit="HNE23on", goal_no=46, regime="III", days=on, kind="ne23")]
    return rows


def run_units(rows, out_dir, allow_holdout, from_npz=None):
    out_dir.mkdir(parents=True, exist_ok=True)
    tabs = B.load_tabs()
    res = {}
    for u in rows:
        if from_npz:
            U = B.load_unit(from_npz / f"{u['unit']}.npz")
        else:
            U = B.build_unit(u, tabs, allow_holdout=allow_holdout)
            if U["N"] < 3 or len(U["msgs"]["t"]) < 100:
                continue
        (out_dir / "units").mkdir(exist_ok=True)
        B.save_unit(U, out_dir / "units" / f"{u['unit']}.npz")
        RU.OUT = out_dir
        RU.run(u["unit"])
        for p in out_dir.glob(f"*/{u['unit']}.json"):
            res[u["unit"]] = json.loads(p.read_text()) | dict(goal_no=u["goal_no"])
    return res


def evaluate(res):
    rows = []
    for u, r in res.items():
        g = r["gate_talk"]
        c1 = r["c1"]
        attr = r.get("c1_attr", {})
        rows.append(dict(unit=u, goal_no=r["goal_no"], regime=r["regime"], n_pairs=r["n_pairs"], n_days=r["n_days"],
                         J1=g["jumps"][0], J1_lo=g["j_lo"][0], J1_hi=g["j_hi"][0], J2=g["jumps"][1], J2_lo=g["j_lo"][1], J2_hi=g["j_hi"][1],
                         fFex=c1["A_full"]["f_F"] - c1["A_full"]["f_F_null"],
                         edges=(attr.get("A_full_edges", {}).get("f_F", np.nan) or np.nan) - (attr.get("A_full_edges", {}).get("f_F_null", 0) or 0),
                         S_T=c1["T_span"]["S_raw"], fFexT=c1["T_span"]["f_F"] - c1["T_span"]["f_F_null"], fC=r["cf_talk"]["span_k1"]["f_C"],
                         rho_span=c1["A_span"]["rho_raw"]))
    T = pl.DataFrame(rows)
    out = {}
    ne = pl.col("unit").str.contains("NE23") | pl.col("unit").is_in([STANDINS["ne23_on"], STANDINS["ne23_off"]])
    per = T.filter(~ne).group_by("goal_no").agg(
        pl.col("n_pairs").sum(), ((pl.col("J1") / ((pl.col("J1_hi") - pl.col("J1_lo")) / 3.92) ** 2).sum()
                                  / (1 / ((pl.col("J1_hi") - pl.col("J1_lo")) / 3.92) ** 2).sum()).alias("J1p"),
        (1 / (1 / ((pl.col("J1_hi") - pl.col("J1_lo")) / 3.92) ** 2).sum().sqrt()).alias("J1p_se"),
        ((pl.col("fFex") * pl.col("n_days")).sum() / pl.col("n_days").sum()).alias("fFex"))
    per = per.filter(pl.col("n_pairs") >= FROZEN["CP1"]["min_pairs"])
    out["CP1"] = dict(periods=len(per), pos=int(((per["J1p"] - 1.96 * per["J1p_se"]) > 0).sum()),
                      neg_units=int((T["J1_hi"] < 0).sum()))
    out["CP1"]["pass"] = bool(out["CP1"]["periods"] and out["CP1"]["pos"] / out["CP1"]["periods"] >= FROZEN["CP1"]["frac_periods"]
                              and out["CP1"]["neg_units"] == 0)
    out["CP2"] = dict(frac=float((per["fFex"] > FROZEN["CP2"]["fFex"]).mean()) if len(per) else None,
                      edges_median=float(T["edges"].median()))
    out["CP2"]["pass"] = bool(out["CP2"]["frac"] is not None and out["CP2"]["frac"] >= FROZEN["CP2"]["frac"]
                              and out["CP2"]["edges_median"] >= FROZEN["CP2"]["edges_median"])
    tt = T.filter(pl.col("S_T") > FROZEN["CP3"]["min_S"])
    out["CP3"] = dict(units=len(tt), frac=float((tt["fC"] > tt["fFexT"]).mean()) if len(tt) else None)
    out["CP3"]["pass"] = bool(out["CP3"]["frac"] is not None and out["CP3"]["frac"] >= FROZEN["CP3"]["frac"])
    on = [r for u, r in res.items() if u.endswith("NE23on") or u == STANDINS["ne23_on"]]
    off = [r for u, r in res.items() if u.endswith("NE23off") or u == STANDINS["ne23_off"]]
    if on and off:
        a, b = on[0], off[0]
        nt = a["exo"].get("nudge_target", {})
        ratio = b["gate_talk"]["jumps"][0] / a["gate_talk"]["jumps"][0] if a["gate_talk"]["jumps"][0] else None
        rho = b["c1"]["A_span"]["rho_raw"] / a["c1"]["A_span"]["rho_raw"] if a["c1"]["A_span"]["rho_raw"] else None
        out["CP4"] = dict(nudge_J1_on=nt.get("gate_talk", {}).get("jumps", [None])[0],
                          nudge_J1_on_lo=nt.get("gate_talk", {}).get("j_lo", [None])[0], peer_ratio=ratio, rho_ratio=rho)
        lo, hi = FROZEN["CP4"]["ratio"]
        out["CP4"]["pass"] = bool(out["CP4"]["nudge_J1_on_lo"] is not None and out["CP4"]["nudge_J1_on_lo"] > 0
                                  and ratio is not None and lo <= ratio <= hi and rho is not None and abs(rho - 1) <= FROZEN["CP4"]["rho"])
    for reg in ("I", "III"):
        s = T.filter((pl.col("regime") == reg) & ~ne)
        if len(s):
            se = ((s["J2_hi"] - s["J2_lo"]) / 3.92).to_numpy()
            w = 1 / se ** 2
            out.setdefault("CP5", {})[reg] = float((w * s["J2"].to_numpy()).sum() / w.sum())
    return T, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.confirm:
        if os.environ.get("H50_CONFIRM") != "1":
            sys.exit("Refusing: set H50_CONFIRM=1 together with --confirm to touch the locked holdout.")
        rows = holdout_units()
        res = run_units(rows, OUT, allow_holdout=True)
        T, out = evaluate(res)
        T.write_parquet(OUT / "confirm_units.parquet")
        (OUT / "confirm_result.json").write_text(json.dumps(dict(frozen=FROZEN, result=out, run_at=dt.datetime.now(dt.timezone.utc).isoformat()),
                                                            indent=1, default=float))
        print(json.dumps(out, indent=1, default=float))
    elif args.dry_run:
        stand = STANDINS["regime_III"] + STANDINS["regime_I"] + [STANDINS["ne23_on"], STANDINS["ne23_off"]]
        units = pl.read_parquet(ROOT / "data/processed/H50-field-vs-coupling-transfer-lag/units.parquet")
        rows = [dict(unit=u, goal_no=int(units.filter(pl.col("unit") == u)["goal_no"][0])) for u in stand]
        res = run_units(rows, SCRATCH, allow_holdout=False, from_npz=ROOT / "data/processed/H50-field-vs-coupling-transfer-lag/units")
        T, out = evaluate(res)
        print("DRY RUN on non-holdout stand-ins (not a confirmation):")
        print(json.dumps(out, indent=1, default=float))
    else:
        sys.exit("Use --dry-run, or --confirm with H50_CONFIRM=1.")


if __name__ == "__main__":
    main()
