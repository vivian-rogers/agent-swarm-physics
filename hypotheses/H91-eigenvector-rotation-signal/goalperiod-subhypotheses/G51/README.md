# H91 × G51: private roles, the long era (2026-07-06 → 2026-09-04, non-holdout part)

**Verdict:** mixed
**Role:** native (exploratory)
**Period:** regime III · mode I/K (private roles) · 21 → 32 agents · #general, plus #focus 08-05 → ~08-24 · ~44 non-holdout active days · units 51a–51l (split at roster joins, NE32, NE38, NE33 and the #focus room). The #51 tail (09-07 → 09-21) is held out.

## Why this period
The densest baseline in the village: many consecutive active days at 8 h, N ≥ 21, with one room change (#focus) and nine roster joins. It tests the HH's second clause directly: between events, does eigenvector rotation stay at the finite-T (Dyson) level? It also separates a room event (#focus) from composition changes (joins).

## Prediction
*Written 2026-10-04 ~20:12 UTC, before running on this period. Credences in brackets.*
- **N2a (Dyson between events).** On #51 day pairs ≥ 2 active days from any catalogued event, the share with p_rot < 0.05 is ≤ 0.15 in content (models averaged) [0.35] and in talk [0.35].
- **N2b (room event).** The 08-05 pair (#focus opens) has talk z_rot ≥ 2 or talk A_rot ≥ 2 [0.5]; the 08-24 pair (#focus empties, 51h) has talk z_rot ≥ 2 [0.4].
- **N2c (composition does not rotate).** On roster-join pairs (first days of 51b–51l), mean content z_rot lies within 1 SD of the #51 non-event pairs [0.6].
- **Counts against:** N2a fails in both channels (the co-movement structure drifts every day) and N2b fails (the one room event is not seen).
- **Verdict rule:** *supported* if N2a holds in content and N2b's 08-05 clause holds; *failed* if N2a fails in content and N2b's 08-05 clause fails; *mixed* otherwise.

## Result
*Run 2026-10-04 ~20:30 UTC.* Quiet pairs = within-#51 day pairs ≥ 2 active days from any catalogued event.

| Prediction | Observed | Reference | Verdict |
| --- | --- | --- | --- |
| N2a content s_sig ≤ 0.15 | 0.125 (bge 0.06 [0.01, 0.28], gte 0.19 [0.07, 0.43]; n 16); all 44 #51 pairs: 0.09 / 0.30 | content size ≤ 0.05 | pass (model-dependent) |
| N2a talk s_sig ≤ 0.15 | 0.40 [0.17, 0.69] (n 10, N ≥ 16, ≥ 240 min); all 32 pairs 0.38 | talk size ≤ 0.07 at N ≥ 16 | fail |
| N2b #focus opens (08-05) | talk z 1.35, p 0.08, A 0.11; content A_C −1.18 | alarm at 2 | fail |
| N2b #focus empties (08-24) | talk z 0.75, p 0.22 | z ≥ 2 | fail |
| N2c joins do not rotate | content z 1.12 on 8 join pairs vs 1.09 ± 0.19 on quiet pairs (p 0.32) | within 1 SD | pass |

Median content z_boot is 1.04 / 1.14 (bge / gte) on every kind of #51 pair, above the 0.1–0.75 of stationary synthetic swarms at N 16–32, W 16. The co-movement structure drifts by a similar amount every day; roster joins and the #focus room add nothing visible.

**Replication numbers (common estimator):** s_sig 0.125 on 16 quiet pairs; median z 1.09 [0.97, 1.18]; no scorable kickoff pair (07-03 is held out).

Data: `data/processed/H91-eigenvector-rotation-signal/native/results.json`, `periods.parquet`.

## Scorecard (period-specific axes)
- B (assumptions): 1. Content eigenvectors stay within the finite-T null on 88% of quiet pairs; talk does not (60%).
- E (interventional): 0. The #focus room step is not seen.
- F (identifiability): 2 here. #51 days (N ≈ 24, W = 17) are in the synthetic range where a strong regrouping is detected with power ≥ 0.9.
