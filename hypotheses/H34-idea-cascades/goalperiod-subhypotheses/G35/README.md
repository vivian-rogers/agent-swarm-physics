# H34 × G35: Test your game to make it as fun and functional as you can! (2026-03-16 → 2026-03-23)

**Verdict:** mixed
**Verdict (1b):** mixed (native: lead-designer seeds P(s≥2) ratio 1.11 [0.82, 1.45]; replication mixed, HR₁₀ 25.6)
**Round 2 (2026-10-05):** replication only; the 1b verdict stands. Gamma-mixed branching α̂ 2.14 [1.73, 2.79], tail covered; semantic R̂ 0.15 (bge) / 0.11 (gte).
**Role:** native (round 1b: designated lead designers as idea seeders, DQ6; round 1: exploratory)
**Period:** regime II · mode C · 13 agents at start (median room size 9) · 5 non-holdout days. Setup: Test your game. The village split into #best (GPT-5.4, Opus 4.6, Gemini 3.1 Pro) and #rest to evolve **separate forks** of the RPG.

## Why this period
Secondary period for the cross-period criticality link (P4) and transfer of the forecast rule (P7). Mode C (shared objective), regime II.

## Prediction
*Written 2026-10-04 02:00 UTC, before running on this period* (after the synthetic validation and amendments A1–A5 of the main card; no real cascade statistic had been computed for any period).

| # | Prediction here | Counts against |
| --- | --- | --- |
| P1 | R̂ < 1 with upper 95% CI < 1; typical 0.05–0.5 | lower CI ≥ 1 |
| P2 | R̂ < H03 n̂_talk = 0.08; R_c < R̂ | R̂ > n̂_talk beyond its CI |
| P3a (A1) | observed P(s ≥ 3) and P(s ≥ 5) inside the FN-GW 90% band (if ≥ 50 trees) | outside the band |
| P5 (A2) | contagion beyond the field: HR₁₀ > 1 with lower CI > 1 | HR₁₀ CI includes 1 or < 1 |
| P6 (A3) | pooled recency HR(2 vs 1) ≤ 2.5 (not complex) | HR(2 vs 1) > 3 with lower CI > 2.5 |

**Verdict rule (A2):** supported = P5 (HR₁₀ lower CI > 1) and P3a pass; failed = both fail, or R̂ lower CI ≥ 1; mixed = exactly one passes; n/a = fewer than 20 non-seed agent first uses (or < 50 trees for P3a, which then counts as not tested and the verdict rests on P5: supported → mixed at best).

## Result
**mixed.** 3000 ideas, 4839 agent first uses, 3350 trees, N_room 9; R̂ = 0.332, contagion share R_c = 0.318, HR₁₀ = 22.66; P(s ≥ 2) = 0.238, largest tree 12.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 R̂ < 1 (upper CI < 1) | R̂ = 0.332 [0.315, 0.350] | critical R = 1 | pass |
| P2 R̂ < H03 n̂_talk | R̂ 0.332 vs n̂ 0.08; R_c = 0.318 | HH108: R̂ > n̂ | fail |
| P3a FN-GW band covers P(s ≥ 3), P(s ≥ 5) | P(s≥3) 0.097 (band 0.104–0.130); P(s≥5) 0.030 (band 0.019–0.030) | GW-NB band covers both: no | fail |
| P3b pure s^−3/2 rejected; τ_app ≥ 2 | LR 1400.8; τ_app 2.61 | critical branching | pass |
| P5 HR₁₀ > 1, lower CI > 1 (A2) | HR₁₀ = 22.66 [20.09, 25.79] (288 adoptions at k = 0) | field: HR₁₀ ≤ 1 | pass |
| P5a jitter excess (pre-registered; failed guard) | exposed 0.847 vs null 0.854, p = 0.98 | uninterpretable (S2) | n/a |
| P6 pooled HR(2 vs 1) ≤ 2.5 | 3.54 [2.98, 4.15] | complex > 3; heterogeneity inflates | ambiguous |
| P5c cross-room ratio > 3 | 13.5 [10.7, 17.6] (P(adopt) 0.066 vs 0.0049) | field ≈ 1–1.8 (S2) | pass (room fields confound) |
| P7 day-ahead 90% PI coverage (pre-registered FN-GW) | P(s≥2) 0.00, P(s≥3) 0.00 over 4 days | post-hoc V3: 0.50, 1.00 | fail |

**By idea class** (U artifact, D number, N name/coinage, W rare word):

| Class | ideas | agent nodes | R̂ [95% CI] | R_c | P(s ≥ 2) | P(s ≥ 3) | s_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D | 78 | 117 | 0.34 [0.24, 0.44] | 0.33 | 0.265 | 0.084 | 5 |
| N | 2863 | 4617 | 0.33 [0.31, 0.35] | 0.32 | 0.238 | 0.098 | 12 |
| U | 8 | 26 | 0.69 [0.27, 0.81] | 0.68 | 0.667 | 0.333 | 9 |
| W | 51 | 79 | 0.24 [0.08, 0.38] | 0.21 | 0.161 | 0.065 | 5 |

Data: `data/processed/H34-idea-cascades/G35/`. Figures: `../../figures/` (cross-period); numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
C (adequacy): HR₁₀ beats the field null (lower CI 20.09). D (unfitted shape): FN-GW band misses the tail; pure s^−3/2 rejected. G (rooms): never-exposed agents adopt far less (ratio 13.5), confounded by room fields. E: no natural experiment inside this period was used.

## Notes
- Two rooms active: the cross-room contrast is available but confounded by room-specific fields (rooms often worked on different projects).
- Censoring check: R̂ without trees rooted on the last day = 0.341.
- Root vs non-root mean offspring 0.284 vs 0.361 (GW assumes equal).
- Root types: invented 0.88, from humans 0.038, field (unexposed) 0.087; 0.85 of non-seed first uses were visibly exposed.

## Round 1b native: are the day's lead designers idea sources? (DQ6)
*Prediction written 2026-10-04 16:50 UTC, before running.* **Seen beforehand:** round 1 for this period (above) and the card; DQ6's `ground_truth_labels` rows (leader terms and lead designers; codes and times only); H29's round-1b native summary (#35: designated leaders get 1.4x more replies per message; #26: the elected leader's broadcast pull rose most); H32's round-1 finding that formal leaders are not content sources. No round-1b H34 statistic (ledger trees, any idea split by seeder) had been computed.

**Design.** DQ6 lead designers: 03-16 (#rest 18, #best 23), 03-17 (19, 20), 03-18 (6, 22). Window = the lead designer's PT day, its room. Trees from the round-1b build (context-ledger visibility: j's first use is *exposed* if an earlier use reached one of j's receiving calls before the call that produced j's use). For each idea whose **seed** (first use in the period) falls in the window, the seed's tree size s (agents reached through visible exposure). Statistic: the ratio of P(s ≥ 2) for leader-seeded ideas to that for ideas seeded by other agents in the same room and window, with an idea-bootstrap 95% CI (2,000 draws); mean s as a secondary. Pooled over the six room-days (Mantel–Haenszel-style: ideas pooled, stratum = room-day).

**Predictions:**
- **N35a:** leader-seeded ideas spread more: the pooled P(s ≥ 2) ratio > 1 with CI excluding 1 [0.55].
- **N35b (negative control):** ideas seeded in one room reach the other room only without ledger exposure: the share of cross-room first uses classified *exposed* is ≤ 2% [0.85].

**Verdict rule (H34 here):** N35a decides: *supported* (a known idea source is visible in the branching) if the ratio > 1 with CI excluding 1; *failed* if the point estimate ≤ 1; *mixed* if the point estimate > 1 but the CI includes 1.

### Result (round 1b, run 2026-10-04)
`analysis/r1b_natives.py natives` → `data/processed/H34-idea-cascades/r1b/results/natives.json`.

| Test | Observed | Prediction | Verdict |
| --- | --- | --- | --- |
| N35a pooled P(s ≥ 2), leader-seeded / other-seeded (6 room-days; 227 vs 1,621 seeds) | **1.11 [0.82, 1.45]**; P(s ≥ 2) 0.24 vs 0.24; mean size 1.31 vs 1.48. Per room-day: 03-16 #rest 0.33 vs 0.28, #best 0.27 vs 0.29; 03-17 #rest leader seeded nothing, #best 0.18 vs 0.12; 03-18 #rest 0.20 vs 0.22, #best 0.10 vs 0.09 | > 1, CI excluding 1 | prediction **failed**; rule → *mixed* (point > 1, CI includes 1) |
| N35b share of cross-room first uses classified exposed | **0.49** (229/464) vs 0.99 within the seed room | ≤ 2% | **failed as written** |
| N35b' (post hoc) the *crossing* event: an idea's first use in the other of #best/#rest | exposed in **6/235 (2.6%)** | — | descriptive |

**Reading.** Designated lead designers do not seed ideas that spread further than their room-mates' (H29's 1.4× reply premium does not show up in idea branching). The pre-registered negative control was mis-specified: once an idea crosses rooms (almost always without ledger exposure, 97%), it spreads inside the new room through visible exposure, so most cross-room first uses *are* exposed. The crossing events themselves behave as the control intended: rooms gate visible exposure, and ideas cross by independent invention or channels the ledger does not log (artifacts, history search).

**Verdict (H34 here):** mixed (no leader premium; crossing events confirm room gating, post hoc).

## Round 2 (2026-10-05)
*Replication rows for the card's R1 and R4 (predictions in the main card, written 03:50 UTC). Role: replication; no verdict change.*

| Quantity | Value | Reference |
| --- | --- | --- |
| R1 gamma-mixed FN-GW: α̂ (CV² = 1/α), μ̂ | 2.14 [1.73, 2.79], μ̂ 0.291 | LR vs one R: 117.3 (5% point 2.71) |
| R1 tail: P(s ≥ 3), P(s ≥ 5) | 0.099, 0.0309 | Γ-FN 90% band [0.086, 0.108], [0.0204, 0.0319]: covered |
| R1 non-root / root offspring (unfitted) | 1.30 | Γ-FN band [1.04, 1.29]; one R 0.81; homogeneous skeleton ≤ 0.91 |
| R1 day-ahead log score, Γ-FN minus beta-binomial | 11.5 nats | > 0 favours Γ-FN |
| R4 semantic R̂, bge (θ 0.90) | 0.15 [0.13, 0.17], 1804 first uses | marker R̂ (1b) in the 1b line above |
| R4 semantic R̂, gte (θ 0.877) | 0.11 [0.09, 0.12], 1845 first uses | |
| R4 HR₁₀ (bge / gte) | 26.3 / 48.7 | field null 1 |
| R4 HR_unread5 / HR_seen5 (bge / gte) | 1.10 / 0.99 | copying < 1; marker median 0.56 |
