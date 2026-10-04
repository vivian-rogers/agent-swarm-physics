"""H76 confirmatory tests on the LOCKED HOLDOUT. Written after exploratory round 1 (2026-10-04); NOT RUN.

Guard: the holdout is touched only with BOTH flags, a clean git state for H76's code, and a holdout-ledger check:
  uv run python hypotheses/H76-excess-housekeeping-split/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
Without the flags the script prints the frozen predictions and exits.

Targets (frozen in FROZEN below and on the card, "Confirmatory predictions"):
  C1-C4  transfer to the kickoffs and days of #45, #46, #47 (regime III, 4-h and 8-h days; coarse 5-state v3 fluxes):
         edge share, trim removal of excess, the final block's share, and the (expected) absence of a kickoff signal.
  C5     NE21 hours ABAB (4 h -> 8 h -> 4 h -> 8 h on 06-07 / 06-15 / 06-29, inside the NE21+NE23 window):
         the daily edge excess per agent does not scale with day length.
Reuse policy: #45-#47 and the NE21+NE23 window are planned or used by H02, H04, H05, H14 (EP on v3, same family!),
H30, H35, H40. H14's planned confirm uses pooled v3 EP per transition (entropy_production family). H76's statistic is the
excess/housekeeping split of ensemble fluxes; the ledger check below decides; disclose in both cards and LOG.md.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h76lib as L  # noqa: E402
import h76run as RN  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))

FROZEN = {  # frozen 2026-10-04 after exploratory round 1 (card, "Confirmatory predictions")
    "space": "coarse", "R": 20,
    "C1_edge_share_min": 0.6,        # pooled edge share of sigma_ex >= 0.6 in each of #45, #46, #47 (round 1: 0.80-1.00)
    "C2_trim_rm_ex_min": 0.7,        # trimming removes >= 70% of sigma_ex in each (round 1: 0.81-1.00)
    "C3_end_share_min": 0.5,         # the final 30-min block holds >= 50% of the day's sigma_ex in >= 2 of 3 (round 1: 0.72-1.00)
    "C4_kick_not_top": True,         # kickoff 2-h sigma_ex is NOT above every day start in >= 2 of 3 (round 1: 3/3)
    "C5_edge_ratio_8h_4h": [0.5, 2.0],   # NE21: median daily edge excess per agent, 8-h days / 4-h days
    "transfer_goals": [45, 46, 47], "ne21_window": ["2026-06-08", "2026-07-06"],
}
FILES = ["hypotheses/H76-excess-housekeeping-split/analysis/confirm.py", "hypotheses/H76-excess-housekeeping-split/analysis/h76lib.py",
         "hypotheses/H76-excess-housekeeping-split/analysis/h76run.py"]


def git_clean() -> bool:
    out = subprocess.run(["git", "-C", str(L.ROOT), "status", "--porcelain", "--", *FILES], capture_output=True, text=True).stdout
    return out.strip() == ""


def end_share(blocks) -> float:
    ex_end, ex_all = 0.0, 0.0
    for k, lst in blocks["untrim"].items():
        for kind, b in lst:
            v, m = b.value()
            ex_all += v[1] * m
            if kind == "end":
                ex_end += v[1] * m
    return ex_end / ex_all if ex_all > 0 else float("nan")


def run():
    import holdout_ledger as HL
    for tgt in ("G45", "G46", "G47", "NE21+NE23"):
        chk = HL.check("H76", tgt, "behavior_states_v3", "entropy_production")
        print(tgt, "allowed" if chk["allowed"] else "NOT ALLOWED", "disclosure needed" if chk["needs_disclosure"] else "")
        if not chk["allowed"]:
            raise SystemExit("holdout ledger refuses a same-family reuse: ask the coordinator")
    rng = np.random.default_rng(7676)
    cal = pl.read_parquet(L.SH / "calendar.parquet")
    goals = pl.read_parquet(L.SH / "embeddings/goals.parquet").filter(pl.col("kind") == "kickoff")
    res, edge_day = {}, []
    for g in FROZEN["transfer_goals"]:
        days = L.load_v3(g, FROZEN["space"], allow_holdout=True)
        kd = goals.filter(pl.col("goal_no") == g)["first_day"][0]
        bl = RN.build_blocks(days, kd, rng, R=FROZEN["R"])
        s = RN.stats(bl, days, kd)
        res[g] = {k: s.get(k) for k in ("edge_share", "trim_rm_ex", "trim_rm_hk", "trim_rm_steps", "hk_share", "kick_rank",
                                        "kick_share", "n_days")} | {"end_share": end_share(bl)}
        hrs = dict(cal.select("pt_date", "documented_hours").iter_rows())
        for d, e, n in zip(s.get("days", []), s.get("ex_edge_by_day", []), s.get("n_agents_by_day", [])):
            if FROZEN["ne21_window"][0] <= d < FROZEN["ne21_window"][1]:
                edge_day.append({"day": d, "edge_per_agent": e / n, "hours": hrs.get(d)})
    c1 = all(res[g]["edge_share"] >= FROZEN["C1_edge_share_min"] for g in res)
    c2 = all(res[g]["trim_rm_ex"] >= FROZEN["C2_trim_rm_ex_min"] for g in res)
    c3 = sum(res[g]["end_share"] >= FROZEN["C3_end_share_min"] for g in res) >= 2
    c4 = sum(res[g]["kick_rank"] is not None and res[g]["kick_rank"] < 1.0 for g in res) >= 2
    ed = pl.DataFrame(edge_day)
    r8 = ed.filter(pl.col("hours") >= 7.5)["edge_per_agent"].median()
    r4 = ed.filter(pl.col("hours") <= 4.5)["edge_per_agent"].median()
    ratio = r8 / r4 if (r8 is not None and r4 and r4 > 0) else float("nan")
    c5 = FROZEN["C5_edge_ratio_8h_4h"][0] <= ratio <= FROZEN["C5_edge_ratio_8h_4h"][1]
    out = {"transfer": res, "C1": c1, "C2": c2, "C3": c3, "C4": c4, "C5_ratio": ratio, "C5": c5, "ne21_days": edge_day}
    L.write_json(L.OUTD / "confirm" / "confirm_results.json", out)
    print(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", action="store_true", dest="ack")
    a = ap.parse_args()
    if not (a.confirm and a.ack):
        print("H76 confirm.py: frozen predictions (not run):")
        for k, v in FROZEN.items():
            print(f"  {k}: {v}")
        print("Pass --confirm --i-understand-this-uses-the-locked-holdout to run on the holdout.")
        return
    if not git_clean():
        raise SystemExit("commit H76's code first (predictions and script must be committed before a confirmatory run)")
    run()


if __name__ == "__main__":
    main()
