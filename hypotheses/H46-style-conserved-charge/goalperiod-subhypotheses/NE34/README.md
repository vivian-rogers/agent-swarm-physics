# H46 × NE34: Goal switches (NE34)

**Verdict:** failed
**Role:** replication (exploratory)
**Boundaries:** Goal switches (NE34): the common estimator over the 24 adjacent non-holdout goal transitions (39→40 and 40→41 go to NE42), plus 3 transitions that skip one held-out goal (sensitivity).

## Why this class
A natural-experiment class for the conservation test (exception (c): the transition is the object). Each boundary is scored against the agent's own day-to-day transitions near it.

## Prediction
*Written 2026-10-04 05:45 UTC, before running on this class.*
- content moves strongly (T_c ≥ 0.70); type-controlled style conserved (T_s ≤ 0.60; verdict rule in the card). Raw style may leak (T_s,raw up to 0.65), and the type control removes most of it (R2). Fingerprint: style balanced accuracy ≥ 3× chance at ≥ 80% of boundaries, retention ≥ 0.8; content retention ≤ 0.6; style > content at ≥ 2/3; Anthropic-only style accuracy above chance at ≥ 2/3. *Falsifier:* type-controlled style broken.

## Result
*Run 2026-10-04 06:05 UTC on non-holdout data; `analysis/conservation.py` → `data/processed/H46-style-conserved-charge/conservation.json`, `conservation_rows.parquet`, `fingerprint.parquet`.*

| Channel | T (mean percentile vs own day-to-day) | 95% CI (boundaries, then agents) | randomization p | boundary Wilcoxon p | median z |
| --- | --- | --- | --- | --- | --- |
| style, type-controlled (primary) | 0.694 | [0.612, 0.769] | < 0.001 | < 0.001 | 0.37 |
| style, raw 20 features | 0.677 | [0.608, 0.741] | < 0.001 | < 0.001 | 0.33 |
| content, style-residualized (primary) | 0.858 | [0.795, 0.912] | < 0.001 | < 0.001 | 1.82 |
| content, raw whitened | 0.867 | [0.803, 0.918] | < 0.001 | < 0.001 | 1.90 |
| style, day field removed | 0.639 | [0.570, 0.705] | < 0.001 | < 0.001 | 0.11 |
| content, day field removed | 0.671 | [0.590, 0.748] | < 0.001 | < 0.001 | 0.36 |

- **Agent × boundary rows:** 189 over 24 boundaries.
- **Holm (six classes):** content p = < 0.001, style p = < 0.001.
- **Pre-registered class verdict:** **broken**.
- **Fingerprint (train before, test after; day-demeaned):** style 0.76 vs content 0.51 at chance 0.15 (ceilings 0.83 / 0.70); style ≥ 3× chance at 100% of boundaries; style > content at 92%. Anthropic-only: style 0.66 vs content 0.45 at chance 0.25.
- **Per boundary (mean percentile, style / content):** 10->11 0.60 / 0.56; 11->12 0.69 / 0.96; 12->13 0.69 / 0.75; 16->17 0.41 / 0.57; 17->18 0.80 / 0.96; 18->19 0.65 / 0.70; 19->20 0.81 / 0.70; 2->3 0.80 / 1.00; 20->21 0.48 / 0.94; 23->24 0.91 / 0.99; 24->25 0.42 / 0.94; 25->26 0.60 / 0.97; 26->27 0.74 / 0.96; 3->4 0.66 / 0.66; 30->31 0.91 / 1.00; 35->36 0.56 / 0.88; 36->37 0.72 / 0.83; 37->38 0.53 / 0.81; 38->39 0.92 / 0.98; 4->5 0.52 / 0.37; 41->42 0.89 / 0.91; 5->6 0.66 / 0.88; 6->7 0.74 / 0.77; 7->8 0.55 / 0.92
- **Post hoc (PH1; after seeing the result):** not a kickoff transient (second post day: style 0.626 [0.554, 0.701], content 0.790), not a wrap-up transient (second-to-last pre day: style 0.623), and not the weekend gap (placebo pairs ≥ 2 calendar days apart: style 0.684, content 0.713; 47 rows).
- **Post hoc (PH2):** the excess style displacement sits in content-adjacent features: digit_share 17%, upper_share 14%, colon 10%, excl 9%, word_len 7%, fpp 7% of the excess.
- **Sensitivity, transitions skipping one held-out goal (8→10, 21→23, 42→44):** style 0.760, content 0.941.

## Scorecard (period-specific axes)
- **E (interventional):** 1. The goal quench moves content strongly; style moves too, beyond its day-to-day band (prediction failed), though by much less in z units (0.37 vs 1.82).
- **D:** the fingerprint (an unfitted statistic) survives: style identifies agents across goal switches better than content.
- **H:** R2 (task leakage via length/code/links) does not explain the shift; the excess sits in digit, uppercase and colon shares (content-adjacent features).

## Round 2 (2026-10-05)
**Round-2 result:** the goal-switch style shift is not speech-act genre (R1-P4 passed); function words move more than formatting (R3-P1 failed); topic-adjacent features carry a small part (R3-P4 passed, marginal); function words plus style identify agents best.
*Pre-registered in the card (Round 2, 2026-10-05 02:44 UTC), synthetic validation and amendments R2-A1..A5 before this run; `analysis/r2_run.py` → `data/processed/H46-style-conserved-charge/r2/`. Non-reserved data.*

| Channel (24 switches) | T [boundary-bootstrap 95% CI] |
| --- | --- |
| style tc (round 1) | 0.694 [0.612, 0.769] |
| style g (genre) | 0.691 [0.616, 0.761] |
| style gp (genre + position) | 0.687 [0.613, 0.758] |
| style core (no digits, uppercase, colons) | 0.661 [0.583, 0.733] |
| function words | 0.727 [0.656, 0.791] |
| function words, genre-controlled | 0.699 [0.626, 0.762] |
| content bge / gte | 0.858 / 0.881 |

- **Identity across the switch (train before, test after):** content 0.51, style 0.77, function words 0.79, function words + style 0.85 (chance 0.15); function words ≥ 3× chance at 24/24 and above content at 24/24; function words + style beat style at 19/24. gp style 0.78.
- **Post hoc (PH-R3a):** pronouns carry the function-word shift: their 0.10, my 0.09, we 0.07, our 0.06, the 0.05, about 0.05 (shares of the excess). Who the agent writes about changes with the task.
