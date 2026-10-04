# H30: An operator-susceptibility gauge χ_op: how steerable is the swarm today?

**Status:** specified (promoted 2026-10-04 by Vivian from HH116). Exploratory round 1 starting. Predictions to be written below before any real-data run.
**Fields:** stat mech, sociophysics, info theory
**Origin:** HH116 (`../hypohypotheses/HYPOHYPOTHESES.md`; `../promotion-shortlist.md`)
**Definitions used:** <terms from physics-models/DEFINITIONS.md, with variant names if any>

## Question
The response of the collective mode and of content alignment to operator and human messages, per message, tracked daily. Does steerability fall as the swarm ages within a goal? *Check:* daily χ_op from H04-style matched kernels; trend within goals; regime differences.

Practical aim (usefulness-first batch): produce a number or rule an operator of an LLM agent swarm could compute from logs and act on.

## Model
**From:** 01, 11. The round-1 agent specifies the exact variant.

## Data scheme (`scheme/`)
Shared tables in `data/processed/shared/` (see `infra/README.md`, including Known issues). Use `chat_mentions_clean.parquet` and the embedding-derived agent states (`embeddings/`).
- **Output:** `data/processed/H30-operator-susceptibility/` (one subfolder per goal period), with `_provenance.json`.

## Candidate goal periods
regime III (nudger on); #51. Per-period folders go in `goalperiod-subhypotheses/G<NN>/` (spanning tests in `goalperiod-subhypotheses/NE<NN>/`).

## Observables
<The quantities computed from the processed data that the model makes predictions about.>

## Null / baseline
<What you'd see if the effect isn't there. E.g. shuffled timestamps, model with β = 0, independent agents.>

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** <the models that predict differently here>
**Locked holdout used for confirmation:** <goal periods / NEs>

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | | |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | | |
| C adequacy | beats the null hierarchy, day-blocked held-out data | | |
| D unfitted predictions | unfitted statistics and the model's signature | | |
| E interventional | predicts the change across a natural experiment | | |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | | |
| G ground truth | agrees with known structure | | |
| H comparative | beats the named rivals | | |
| I transfer | holds in other same-mode periods, including the holdout | | |

## Prediction
*Written <YYYY-MM-DD>, before running the analysis on real data.*
<What the model predicts for the observables, and what result would count against it.>

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G<NN>](goalperiod-subhypotheses/G<NN>/README.md) | exploratory | | |

## Results
<Cross-period synthesis, filled in after analysis: how the result depends on mode, regime and rooms; heterogeneity across periods. Link to analysis/ and figures/.>

## Notes
- 2026-10-04: promoted from HH116 by Vivian (usefulness-first batch); wave 1.
