# H06: Free weeks show neutral cooperative dynamics with a cooperator core

**Status:** specified (shortlist S6 / HH42; approved by Vivian 2026-10-03; started 2026-10-04). Exploratory round 1 starting; predictions to be written before any real-data run.
**Fields:** stat mech, sociophysics
**Origin:** HH42 + HH16 (`../hypohypotheses/HYPOHYPOTHESES.md`; shortlist S6 in `../promotion-shortlist.md`)
**Definitions used:** <terms from physics-models/DEFINITIONS.md, with variant names if any>

## Question
In "pick your own goal" weeks, agents choose and abandon projects freely. Do project abundances follow *neutral cooperative dynamics* (Piñero-style: species, here projects, are equivalent, but joining is frequency-dependent and cooperative)? Signatures: bimodal abundances with a persistent cooperator core, Simpson concentration λ near the predicted λ*(μ, N), and boundaries μ_B (bimodal) and μ_L (log-series) in the novelty rate μ. Or does plain Hubbell neutral drift (log-series, no cooperation) explain them? Practical payoff: whether a free swarm concentrates its effort on a few shared projects by a predictable law, and what sets how many projects survive.

## Model
**From:** `physics-models/06-neutral-cooperative-dynamics` (read its README for the rules, λ*, μ_B, μ_L and the finite-N simulation), with `physics-models/10-potts` as the categorical-state view. H11 found strong herding (ferromagnetic Potts coupling) on project labels in 11/14 periods, including free weeks #31 and #37. That is the cooperative ingredient this model formalizes.

## Data scheme (`scheme/`)
Project labels per agent per window. Two sources:
- H11's strict artifact-based project states (`hypotheses/H11-potts-labor-vs-herding/scheme/`, `data/processed/H11-potts-labor-vs-herding/`). Reuse by import; don't modify.
- Clusters of self-written goals (intentions; `data/processed/shared/embeddings/` statements of kind `intent`).

Individuals = agent slots or sessions; species = projects. Batch joins (NE27, NE33) are pulses of new arrivals. Use `chat_mentions_clean.parquet` if mentions are needed.
- **Output:** `data/processed/H06-neutral-cooperative-dynamics/` (one subfolder per goal period, `G<NN>/`), with `_provenance.json`.

## Candidate goal periods
Free weeks #11, #16, #31, #37 (#22 🔒 held out), #44 #rest; #51 as a check (private goals, not free). Shared-objective weeks as contrasts.

## Links to other hypotheses
H11 (herding on project labels), H01 D7.1 (condensation vs leaders), H12 (dimensionality), HH16 (cooperator core), HH71 (rich club).

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
| [G<NN>](G<NN>/README.md) | exploratory | | |

## Results
<Cross-period synthesis, filled in after analysis: how the result depends on mode, regime and rooms; heterogeneity across periods. Link to analysis/ and figures/.>

## Notes
- 2026-10-04: created and launched (S6, HH42; approved 2026-10-03, started 2026-10-04).
