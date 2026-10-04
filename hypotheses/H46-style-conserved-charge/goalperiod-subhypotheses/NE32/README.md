# H46 × NE32: Roster changes (class folder named after NE32)

**Verdict:** n/a
**Role:** replication (exploratory)
**Boundaries:** Roster changes (class folder named after NE32): 20 within-period joins and leaves with no other step change (incl. NE29, NE32, NE33); incumbents only.

## Why this class
A natural-experiment class for the conservation test (exception (c): the transition is the object). Each boundary is scored against the agent's own day-to-day transitions near it.

## Prediction
*Written 2026-10-04 05:45 UTC, before running on this class.*
- incumbents' content moves little (T_c ≈ 0.55, possibly uninformative); style conserved.

## Result
*Run 2026-10-04 06:05 UTC on non-holdout data; `analysis/conservation.py` → `data/processed/H46-style-conserved-charge/conservation.json`, `conservation_rows.parquet`, `fingerprint.parquet`.*

| Channel | T (mean percentile vs own day-to-day) | 95% CI (boundaries, then agents) | randomization p | boundary Wilcoxon p | median z |
| --- | --- | --- | --- | --- | --- |
| style, type-controlled (primary) | 0.490 | [0.429, 0.551] | 0.691 | 0.905 | -0.38 |
| style, raw 20 features | 0.483 | [0.425, 0.539] | 0.815 | 0.929 | -0.35 |
| content, style-residualized (primary) | 0.488 | [0.427, 0.550] | 0.724 | 0.565 | -0.27 |
| content, raw whitened | 0.486 | [0.419, 0.551] | 0.766 | 0.689 | -0.24 |
| style, day field removed | 0.501 | [0.443, 0.558] | 0.478 | 0.449 | -0.26 |
| content, day field removed | 0.503 | [0.434, 0.576] | 0.444 | 0.324 | -0.25 |

- **Agent × boundary rows:** 260 over 20 boundaries.
- **Holm (six classes):** content p = 0.728, style p = 1.000.
- **Pre-registered class verdict:** **uninformative**.
- **Fingerprint (train before, test after; day-demeaned):** style 0.79 vs content 0.72 at chance 0.11 (ceilings 0.78 / 0.68); style ≥ 3× chance at 95% of boundaries; style > content at 50%. Anthropic-only: style 0.84 vs content 0.73 at chance 0.19.
- **Per boundary (mean percentile, style / content):** 18a->18b 0.34 / 0.37; 18b->18c 0.43 / 0.45; 19a->19b 0.43 / 0.59; 20a->20b 0.38 / 0.51; 31a->31b 0.62 / 0.62; 31b->31c 0.86 / 0.64; 38b->38c 0.25 / 0.17; 38d->38e 0.32 / 0.21; 42a->42b 0.65 / 0.38; 44a->44b 0.43 / 0.70; 4a->4b 0.24 / 0.67; 4b->4c 0.47 / 0.39; 51a->51b 0.49 / 0.58; 51b->51c 0.48 / 0.39; 51c->51d 0.41 / 0.54; 51d->51e 0.51 / 0.47; 51h->51i 0.52 / 0.58; 51i->51j 0.46 / 0.50; 51j->51k 0.61 / 0.50; 51k->51l 0.53 / 0.42

## Scorecard (period-specific axes)
- **E:** 0 for this class: content does not move either, so the boundary is not a perturbation of the state and conservation cannot be tested (R3).
- **C:** the estimator holds size here (style and content both at ½), consistent with the synthetic null.
