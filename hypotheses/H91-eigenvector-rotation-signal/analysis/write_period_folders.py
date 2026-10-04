"""H91: per-goal-period replication folders (templated from the card's replication rule, labelled as such) and
per-period rows in the shared per_period_estimates table. G51 is a native folder: its replication numbers are written
into data/processed only, and the native README carries them.
Run after evaluate.py: uv run python hypotheses/H91-eigenvector-rotation-signal/analysis/write_period_folders.py
"""
from __future__ import annotations

import json
import re
import sys

import numpy as np
import polars as pl

import h91lib as L

sys.path.insert(0, str(L.ROOT / "infra/shared"))
import estimates as E  # noqa: E402

HYPD = L.ROOT / "hypotheses/H91-eigenvector-rotation-signal/goalperiod-subhypotheses"
NATIVE = {51}
METHOD = ("H91 round 1: subspace distance between consecutive days' top-2 eigenvectors of the agent content overlap "
          "matrix (agent-day and kind centered DQ5 vectors, bge + gte), excess over a same-day moving-block bootstrap "
          "(R = 199); s_sig = share of within-period pairs >= 2 active days from any event with p_boot < 0.05")


def titles() -> dict:
    t = {}
    for line in (L.ROOT / "hypotheses/hypohypotheses/goal-periods.md").read_text().splitlines():
        m = re.match(r"^### (\d+) · (.+)$", line)
        if m:
            t[int(m.group(1))] = m.group(2).strip()
    return t


def fmt(x, nd=2):
    return "–" if x is None or (isinstance(x, float) and not np.isfinite(x)) else f"{x:.{nd}f}"


def main():
    per = pl.read_parquet(L.OUT / "periods.parquet")
    ttl = titles()
    rows = []
    for r in per.iter_rows(named=True):
        g = int(r["goal_no"])
        unit = E.map_unit(g)
        base = {"period_unit": unit, "goal_no": g, "method": METHOD, "role": "replication", "first_day": r["first_day"],
                "last_day": r["last_day"], "source": "data/processed/H91-eigenvector-rotation-signal/periods.parquet",
                "null": "same-day moving-block bootstrap (finite-T eigenvector diffusion)", "post_hoc": False}
        if r["n_pairs"]:
            rows.append({**base, "statistic": "rotation_sig_share_quiet_pairs", "channel": "content", "estimate": r["s_sig"],
                         "ci_lo": r["s_sig_lo"], "ci_hi": r["s_sig_hi"], "ci_kind": "parametric", "ci_level": 0.95,
                         "n": r["n_pairs"], "n_kind": "day pairs (quiet, within period)",
                         "notes": "mean of bge and gte shares; Wilson interval on the pair count; synthetic size <= 0.05"})
            rows.append({**base, "statistic": "rotation_excess_z_median", "channel": "content", "estimate": r["z_med"],
                         "ci_lo": r["z_lo"], "ci_hi": r["z_hi"], "ci_kind": "percentile" if r["z_lo"] is not None else "none",
                         "ci_level": 0.95, "n": r["n_pairs"], "n_kind": "day pairs (quiet, within period)",
                         "notes": "z_boot (k = 2), mean of bge and gte per pair; stationary synthetic swarms give 0.1-0.75"})
        if r["kick_A_C"] is not None:
            rows.append({**base, "statistic": "rotation_alarm_kickoff", "channel": "content", "estimate": r["kick_A_C"],
                         "ci_lo": None, "ci_hi": None, "ci_kind": "none", "n": 1, "n_kind": "kickoff day pair",
                         "notes": f"trailing robust z of z_boot (B = 10); alarm at 2; R1 (H36) on the same day {fmt(r['kick_R1m'])}"})
        if r["talk_pairs"]:
            k = int(round(r["talk_s_sig"] * r["talk_pairs"]))
            lo, hi = L.wilson(k, r["talk_pairs"])
            rows.append({**base, "statistic": "rotation_sig_share_quiet_pairs", "channel": "talk", "estimate": r["talk_s_sig"],
                         "ci_lo": lo, "ci_hi": hi, "ci_kind": "parametric", "ci_level": 0.95, "n": r["talk_pairs"],
                         "n_kind": "day pairs (quiet, within period)",
                         "notes": "talk spins, all-present window; p_boot size 0.13-0.28 at N <= 8 (synthetic), so read high values with care"})
        if g in NATIVE:
            continue
        folder = HYPD / f"G{g:02d}"
        (folder / "figures").mkdir(parents=True, exist_ok=True)
        kickline = ("no scorable kickoff pair (the previous active day is held out, or < 4 common agents)"
                    if r["kick_A_C"] is None else
                    f"A_C {fmt(r['kick_A_C'])} (alarm at 2); z_boot {fmt(r['kick_z'])}; R1 (H36) {fmt(r['kick_R1m'])}")
        text = f"""# H91 × G{g:02d}: {ttl.get(g, 'goal period ' + str(g))} ({r['first_day']} → {r['last_day']}, non-holdout days)

**Verdict:** {r['verdict']}
**Role:** replication (exploratory)
**Period:** regime {r['regime']} · {r['n_days']} non-holdout active days · median {fmt(r['N_med'], 0)} agents per scored content pair · {r['n_pairs']} quiet within-period content pairs.

## Why this period
A replication point for the common estimator (layer 1). Every eligible goal period gets the same statistics, so periods are comparable points, not independent tests.

## Prediction
*Templated from the card's replication rule, written 2026-10-04 ~20:10 UTC before any real-data rotation statistic (Amendment 1 changed the null to the same-day block bootstrap before real data).*
- Between events the eigenvectors follow the finite-T (Dyson) null: the share s_sig of quiet within-period day pairs (≥ 2 active days from any catalogued event) with p_boot < 0.05 is ≤ 0.15 (content, bge and gte averaged).
- The kickoff pair (last day of the previous period → day 0) fires the rotation alarm, A_C ≥ 2.
- *Supported* if both hold; *failed* if s_sig > 0.15 and the kickoff pair (if scorable) has A_C < 2; *mixed* otherwise; *descriptive* with < 3 quiet pairs.

## Result
| Statistic | Observed | Reference |
| --- | --- | --- |
| s_sig, content (quiet pairs) | {fmt(r['s_sig'])} [{fmt(r['s_sig_lo'])}, {fmt(r['s_sig_hi'])}] (n = {r['n_pairs']}) | ≤ 0.15; synthetic size ≤ 0.05 |
| median rotation excess z_boot, content | {fmt(r['z_med'])} [{fmt(r['z_lo'])}, {fmt(r['z_hi'])}] | stationary synthetic 0.1–0.75 |
| kickoff pair | {kickline} | alarm at 2 |
| s_sig, talk (quiet pairs) | {fmt(r['talk_s_sig'])} (n = {r['talk_pairs']}) | size 0.13–0.28 at N ≤ 8 |

Data: `data/processed/H91-eigenvector-rotation-signal/periods.parquet`, `rotation.parquet`, `days_scored.parquet`.

## Scorecard (period-specific axes)
- C (adequacy): the rotation alarm on this period's kickoff, as tabulated; the card pools kickoffs into one AUC.
- B (assumptions): s_sig tests the stationarity of the co-movement structure between events.

## Notes
- Templated folder (replication layer), written by `analysis/write_period_folders.py`.
"""
        (folder / "README.md").write_text(text)
    E.write_estimates(rows, hypothesis="H91")
    print(f"{len(rows)} estimate rows; {per.height - len(NATIVE)} period folders")


if __name__ == "__main__":
    main()
