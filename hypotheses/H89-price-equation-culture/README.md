# H89: Price equation for village culture

**Status:** specified (approved by Vivian in the dashboard vetting panel 2026-10-04 from HH313; round 1 launching)
**Fields:** <to be filled by the round-1 agent>
**Literature:** <links to literature/*.md>
**Definitions used:** <terms from physics-models/DEFINITIONS.md, with variant names if any>
**From:** HH313 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/13*/`, `physics-models/05*/`

## Source HH (verbatim from the HH list, including literature refinements)
A Price equation for village culture: selection, transmission and migration. For a cultural trait z, use Δz̄ = Cov(w, z)/w̄ + E(w Δz)/w̄ + migration. The trait can be a culture-vector projection (HH293) or a convention's use (HH291). w is the number of agents who adopt from i inside the logged light cone (H41).
  - The migration term is roster in/out flow.
  - *Predictions:*
    - Style: migration dominates; it is a charge (H46).
    - Content: transmission bias dominates, as convergence to the field.
    - Selection (differential influence): small, carried by named messages (H29), at most ~20% of Δz̄.
  - *Egregore reading:* a transmission bias toward a village-specific attractor that persists across migration events.
  - *Kill:* migration plus kickoff explain Δz̄ fully.
  - *Models:* 05, 06 · *Builds on:* H41, H46, H29, HH293

## Question
<What do you want to know, in one or two sentences.>

## Model
**From:** `physics-models/<NN-slug>/`
<Which variant of that model this hypothesis uses, its parameters, and what it
predicts here. E.g. "SIS with spontaneous adoption field ε; λ, γ, ε fit per regime.">

## Data scheme (`scheme/`)
<How raw data becomes the processed dataset this hypothesis uses.>
- **Inputs:** <raw tables and fields>
- **Transform:** <steps>
- **Output:** `data/processed/H<NN>-<slug>/` (<files and columns>)
- **Regimes covered:** <which time intervals; see physics-models/DEFINITIONS.md "Regime">

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
<Dated notes, dead ends, decisions.>
