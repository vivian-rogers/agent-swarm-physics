# H46 × NE14: Scaffold steps (class folder named after NE14)

**Verdict:** n/a
**Role:** replication (exploratory)
**Boundaries:** Scaffold steps (class folder named after NE14): NE02, NE03, NE04, NE06 (×2), NE07, NE10, NE11, NE14 (regime II→III, content in raw bge space), NE16, NE17, NE18.

## Why this class
A natural-experiment class for the conservation test (exception (c): the transition is the object). Each boundary is scored against the agent's own day-to-day transitions near it.

## Prediction
*Written 2026-10-04 05:45 UTC, before running on this class.*
- style conserved at the small steps. NE14 (chat now written from inside continuous computer use) is where H46 is most at risk; the hypothesis predicts conservation there too (prior: about 40% that it breaks).

## Result
*Run 2026-10-04 06:05 UTC on non-holdout data; `analysis/conservation.py` → `data/processed/H46-style-conserved-charge/conservation.json`, `conservation_rows.parquet`, `fingerprint.parquet`.*

| Channel | T (mean percentile vs own day-to-day) | 95% CI (boundaries, then agents) | randomization p | boundary Wilcoxon p | median z |
| --- | --- | --- | --- | --- | --- |
| style, type-controlled (primary) | 0.491 | [0.385, 0.598] | 0.614 | 0.515 | -0.37 |
| style, raw 20 features | 0.481 | [0.383, 0.585] | 0.739 | 0.536 | -0.40 |
| content, style-residualized (primary) | 0.511 | [0.369, 0.640] | 0.364 | 0.212 | -0.20 |
| content, raw whitened | 0.514 | [0.377, 0.644] | 0.327 | 0.285 | -0.21 |
| style, day field removed | 0.486 | [0.379, 0.593] | 0.684 | 0.575 | -0.37 |
| content, day field removed | 0.505 | [0.394, 0.613] | 0.441 | 0.259 | -0.18 |

- **Agent × boundary rows:** 104 over 12 boundaries.
- **Holm (six classes):** content p = 0.728, style p = 1.000.
- **Pre-registered class verdict:** **uninformative**.
- **Fingerprint (train before, test after; day-demeaned):** style 0.79 vs content 0.62 at chance 0.12 (ceilings 0.78 / 0.82); style ≥ 3× chance at 100% of boundaries; style > content at 75%. Anthropic-only: style 0.64 vs content 0.61 at chance 0.23.
- **Per boundary (mean percentile, style / content):** 10a->10b (NE03) 0.48 / 0.56; 12a->12b (NE04) 0.70 / 0.81; 20b->20c (NE06) 0.47 / 0.20; 20c->20d (NE06) 0.55 / 0.52; 21a->21b (NE07) 0.21 / 0.43; 30a->30b (NE10) 0.42 / 0.70; 31c->31d (NE11) 0.77 / 0.58; 36a->36b (NE14) 0.67 / 0.75; 36b->36c (NE16) 0.35 / 0.51; 38a->38b (NE17) 0.25 / 0.05; 38c->38d (NE18) 0.47 / 0.56; 6a->6b (NE02) 0.69 / 0.51
- **NE14 alone (regime II→III, 11 agents, descriptive):** style 0.673 (p 0.033), raw 0.650, content (raw bge) 0.747 (p 0.004).

## Scorecard (period-specific axes)
- **E:** 0 for this class: content does not move either, so the boundary is not a perturbation of the state and conservation cannot be tested (R3).
- **C:** the estimator holds size here (style and content both at ½), consistent with the synthetic null.
