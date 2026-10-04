# H77: Repos as replicators: the selection-resolution bound

**Status:** specified (promoted 2026-10-04 from HH325 by Vivian; round 1 launching)
**Fields:** <to be filled by the round-1 agent>
**Literature:** <links to literature/*.md>
**Definitions used:** <terms from physics-models/DEFINITIONS.md, with variant names if any>
**From:** HH325 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` ("From the thermodynamics and origins-of-life notes") · **Models:** `physics-models/05-replicator-dissipation/`, `physics-models/06-neutral-cooperative-dynamics/`

## Source HH (verbatim from the HH list)
Repos as replicators: recruitment order and the selection-resolution bound.
  - First, fit the order of recruitment: does per-host recruitment rise with project share (conformist, H53) or is it first-order (Kolchinsky's class)?
  - Then test the resolution bound: rivals that die have fitness gap s ≥ e^{−σ*}, with σ* = ln(recruitments/departures) for the top project on its plateau.
  - *Predictions:* σ* ≥ 1 nat in herding weeks and ≤ 0.3 in fragmented free weeks. At ≤ 0.3, H06's near-neutral coexistence is a near-equilibrium regime: selection can't resolve small differences, so everything coexists.
  - *Kill:* σ* is the same in herding and free weeks.
  - *Models:* 05, 06 · *Builds on:* H06, H11, H53, HH301 · *Literature:* Kolchinsky 2025

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
