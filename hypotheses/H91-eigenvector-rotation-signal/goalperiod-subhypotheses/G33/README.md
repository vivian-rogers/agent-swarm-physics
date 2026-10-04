# H91 × G33: Discuss, debate, and act on your views about the recent Pentagon-AI company news (2026-03-02 → 2026-03-04, non-holdout days)

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** regime II · 3 non-holdout active days · median – agents per scored content pair · 0 quiet within-period content pairs.

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
| s_sig, content (quiet pairs) | – [–, –] (n = 0) | ≤ 0.15; synthetic size ≤ 0.05 |
| median rotation excess z_boot, content | – [–, –] | stationary synthetic 0.1–0.75 |
| kickoff pair | no scorable kickoff pair (the previous active day is held out, or < 4 common agents) | alarm at 2 |
| s_sig, talk (quiet pairs) | – (n = 0) | size 0.13–0.28 at N ≤ 8 |

Data: `data/processed/H91-eigenvector-rotation-signal/periods.parquet`, `rotation.parquet`, `days_scored.parquet`.

## Scorecard (period-specific axes)
- C (adequacy): the rotation alarm on this period's kickoff, as tabulated; the card pools kickoffs into one AUC.
- B (assumptions): s_sig tests the stationarity of the co-movement structure between events.

## Notes
- Templated folder (replication layer), written by `analysis/write_period_folders.py`.
