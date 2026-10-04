"""H27 confirmatory test on the LOCKED HOLDOUT. Written in round 1; NOT RUN.

What it does (frozen rule C1-C5, see FROZEN below and the card, "Confirmatory prediction"):
  1. builds H27 series for the held-out target periods into a separate folder
     (data/processed/H27-herding-early-warning/holdout/, via scheme/build.py --allow-holdout --out ...);
     for #51 only the locked tail (2026-09-07 -> 09-21, PT) is kept;
  2. applies the coverage rule, the O1 onset rule, the O2 indicators and the frozen operator alarm (tau* from the
     synthetic S0 calibration), exactly as in analysis/explore.py, with no re-tuning;
  3. scores the frozen confirmatory predictions C1-C3 below and writes holdout_results.json.

Safety:
  * refuses to touch held-out periods without BOTH --confirm and --i-understand-this-uses-the-locked-holdout;
  * --dry-run runs the identical pipeline on non-holdout stand-ins (no holdout data is read);
  * holdout reuse policy (hypotheses/holdout.md): refuses to run unless this script and the card are committed
    (no uncommitted changes), and prints the reuse disclosure that must go into both cards and LOG.md.

Usage:
  uv run python hypotheses/H27-herding-early-warning/analysis/confirm_holdout.py --dry-run
  uv run python hypotheses/H27-herding-early-warning/analysis/confirm_holdout.py --confirm --i-understand-this-uses-the-locked-holdout
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ews_core as E  # noqa: E402
import explore as X  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
HYP = ROOT / "hypotheses/H27-herding-early-warning"
DATA = ROOT / "data/processed/H27-herding-early-warning"
HOLD = DATA / "holdout"

# Targets chosen 2026-10-04 before any real-data run (card, Prediction). #43 and #48 are single days (skipped).
TARGETS = [22, 28, 29, 32, 34, 45, 46, 47, 49, 50, 51]
TAIL51 = ("2026-09-07", "2026-09-21")
STAND_INS = [30, 31, 38]  # dry run only (non-holdout, already explored; periods with onsets)

# Earlier or planned confirmatory uses of these periods by other hypotheses (holdout.md reuse policy, item 3).
REUSE = {
    22: "H11 target (coupling sign, not run)",
    28: "H11 target (coupling sign, not run)",
    32: "inside NE12: H05 confirmatory (activity-spin couplings, run)",
    45: "H02 confirmatory (activity-timing couplings, run); H23 (message content); H11 target",
    46: "inside NE21+NE23: H04 confirmatory (activity Hawkes n, run)",
    47: "inside NE21+NE23: H04 confirmatory (activity Hawkes n, run)",
    49: "inside NE21+NE23: H04 confirmatory (activity Hawkes n, run)",
    50: "inside NE21+NE23: H04 confirmatory (activity Hawkes n, run)",
}

# ------------------------------------------------------------------ frozen confirmatory rule (C1-C5)
# Frozen 2026-10-04 after exploratory round 1 and before any holdout data was read. See the card,
# "Confirmatory prediction". Round 1 (W = 15, lead 1 h): composite AUC 0.62 [0.51, 0.76] (n = 8 evaluable onsets),
# tau_AR1 AUC 0.42, EWS alarm 5/21 hits vs 3.1 rate-matched (p = 0.07), level alarm 5/21; post hoc: 11/21 onsets
# preceded by a chat link to the project within 30 min (within-period permutation p = 0.0005).
FROZEN = dict(
    lead=4,                       # windows (1 h at W = 15)
    W=15,
    min_eval_onsets=5,            # fewer evaluable onsets -> C1-C3 'inconclusive (underpowered)'
    c1_auc_min=0.70,              # C1 (H27 as hypothesized): composite AUC >= 0.70 and CI lower bound > 0.5
    c2_auc_max=0.60,              # C2 (round-1 negative replicates): composite AUC < 0.60 or CI includes 0.5
    c3_ar1_auc_max=0.55,          # C3 (no slowing down): tau_AR1 AUC <= 0.55
    c4_n2_alpha=0.05,             # C4 (no operator value): EWS hits do not beat the rate-matched null (p >= 0.05)
                                  #     or the naive level alarm hits at least as many onsets
    c5_min_onsets=5,              # C5 (announcement precursor, post hoc in round 1): chat link to the project in the
    c5_mh_or_min=2.0,             #     previous 30 min: Mantel-Haenszel OR > 2 and within-period permutation p < 0.05
    c5_alpha=0.05,
)


def committed(paths) -> bool:
    r = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "--", *map(str, paths)], capture_output=True, text=True)
    return r.returncode == 0 and not r.stdout.strip()


def build_holdout(goals):
    cmd = [sys.executable, str(HYP / "scheme/build.py"), "--allow-holdout", "--out", str(HOLD), "--goals", *map(str, goals)]
    subprocess.run(cmd, check=True)


def restrict_tail51(base: Path):
    """Keep only the #51 locked tail in the holdout series (re-index gwin)."""
    import polars as pl
    for W in (15, 30):
        f = base / "G51" / f"series_w{W}.parquet"
        if not f.exists():
            continue
        s = pl.read_parquet(f).filter((pl.col("pt_date") >= TAIL51[0]) & (pl.col("pt_date") < TAIL51[1])).sort("gwin")
        s = s.with_columns(pl.int_range(0, s.height).cast(pl.Int32).alias("gwin"),
                           (pl.col("day") - pl.col("day").min()).alias("day"))
        s.write_parquet(f, compression="zstd")
        cov = json.loads((base / "coverage.json").read_text())
        cov["51"][f"w{W}"].update(windows=s.height, days=int(s["day"].n_unique()), frac_n_ge3=float((s["n"] >= 3).mean()),
                                  mean_n=float(s["n"].mean()))
        (base / "coverage.json").write_text(json.dumps(cov, indent=1))


def score(arm, base):
    import assemble as AS
    A = arm["auc"][FROZEN["lead"]]
    a, ci = A["composite"]["auc"], A["composite"]["ci"]
    a_ar1 = A["tau_ar1"]["auc"]
    n_eval = A["n_onset_segments"]
    ews, lvl = arm["operator"]["ews"], arm["operator"]["level"]
    out = dict(auc=a, ci=ci, auc_ar1=a_ar1, n_eval=n_eval, n_onsets=ews["n_onsets"],
               ews={k: ews[k] for k in ("hits", "n_onsets", "far", "ppv", "median_lead_h", "N2_p", "false_alarms_per_day") if k in ews},
               level={k: lvl[k] for k in ("hits", "n_onsets", "far", "ppv", "median_lead_h", "false_alarms_per_day")})
    if n_eval < FROZEN["min_eval_onsets"]:
        out.update(C1="inconclusive (underpowered)", C2="inconclusive (underpowered)", C3="inconclusive (underpowered)")
    else:
        out["C1"] = "confirmed" if (a >= FROZEN["c1_auc_min"] and ci[0] > 0.5) else "not confirmed"
        out["C2"] = "confirmed" if (a < FROZEN["c2_auc_max"] or ci[0] <= 0.5) else "not confirmed"
        out["C3"] = "confirmed" if (a_ar1 is not None and a_ar1 <= FROZEN["c3_ar1_auc_max"]) else "not confirmed"
    if ews["n_onsets"] == 0:
        out["C4"] = "inconclusive (no onsets)"
    else:
        out["C4"] = "confirmed" if (ews.get("N2_p", 1.0) >= FROZEN["c4_n2_alpha"] or lvl["hits"] >= ews["hits"]) else "not confirmed"
    tr = AS.trigger_check(arm["periods"], W=FROZEN["W"], base=base)["link"]
    out["C5_link"] = tr
    if tr["onsets"] < FROZEN["c5_min_onsets"] or tr.get("mh_odds_ratio") is None:
        out["C5"] = "inconclusive (underpowered)"
    else:
        out["C5"] = "confirmed" if (tr["mh_odds_ratio"] > FROZEN["c5_mh_or_min"] and tr["perm_p_within_period"] < FROZEN["c5_alpha"]) else "not confirmed"
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    a = ap.parse_args()
    tau_star = X.load_tau_star()
    if a.dry_run:
        print(f"DRY RUN on non-holdout stand-ins {STAND_INS} (no holdout data read). tau* = {tau_star:.3f}")
        arm = X.run_arm(FROZEN["W"], E.P0, tau_star, goals=STAND_INS, base=DATA, robust=False, n_shift=100)
        res = score(arm, DATA)
        (DATA / "confirm_dryrun.json").write_text(json.dumps(dict(stand_ins=STAND_INS, frozen=FROZEN, result=res), indent=1, default=float))
        print(json.dumps(res, indent=1, default=float))
        return
    if not (a.confirm and a.ack):
        raise SystemExit("refusing: the holdout run needs --confirm --i-understand-this-uses-the-locked-holdout (and Vivian's sign-off)")
    if not committed([Path(__file__), HYP / "README.md", HYP / "analysis/ews_core.py", HYP / "analysis/explore.py",
                      DATA.parent.parent.parent / "hypotheses/holdout.json"]):
        raise SystemExit("refusing: commit the card and the confirmatory code first (holdout reuse policy, item 1)")
    print("Holdout reuse disclosure (add to both cards and LOG.md):")
    for g in TARGETS:
        if g in REUSE:
            print(f"  #{g}: {REUSE[g]} -> H27 uses a different, unexamined statistic (project-label onset timing and early-warning trends)")
    build_holdout(TARGETS)
    restrict_tail51(HOLD)
    arm = X.run_arm(FROZEN["W"], E.P0, tau_star, goals=TARGETS, base=HOLD, robust=False, n_shift=500)
    res = score(arm, HOLD)
    (HOLD / "holdout_results.json").write_text(json.dumps(dict(targets=TARGETS, frozen=FROZEN, result=res,
                                                               periods=arm["periods"], per_period=arm["per_period"]),
                                                          indent=1, default=float))
    print(json.dumps({k: v for k, v in res.items() if k not in ("ews", "level")}, indent=1, default=float))


if __name__ == "__main__":
    main()
