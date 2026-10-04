# H123: Regime I's turn order is a sweep: equilibrium-looking statistics with nonzero entropy production

**Status:** specified (approved by Vivian in the dashboard vetting panel 2026-10-04 from HH364; round 1 launching)
**Fields:** <to be filled by the round-1 agent>
**Literature:** <links to literature/*.md>
**Definitions used:** <terms from physics-models/DEFINITIONS.md, with variant names if any>
**From:** HH364 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/02*/`, `physics-models/15*/`

## Source HH (verbatim from the HH list, including refinements)
- **HH364 · Regime I's turn order is a sweep: equilibrium-looking statistics with nonzero entropy production.** Model 02's subtle case: a fixed-order sweep keeps the Boltzmann distribution but breaks detailed balance. If regime I's turn pointer (`villages.turn_id`) cycles in a fixed order, the snapshots look like equilibrium while the dynamics is not.
  - *Prediction:* the next-actor distribution in regime I is closer to round-robin than random (count first); model 01 fits snapshots as well as in regime III; and the EP bound is positive even with the antisymmetric J set to 0, matching the value the sweep alone predicts.
  - *Check:* scheduler audit of next actor given the current state; simulate a symmetric-J kinetic Ising with the real turn order and compare its EP with the measured bound.
  - *Kill:* turn order is random sequential, or the measured EP far exceeds the sweep prediction (then real asymmetric coupling is present, which is also informative).
  - *Impostors:* this measures the scheduler's own share of irreversibility.
  - *Models:* 02, 15 · *Builds on:* H14, H56, H76, HH45

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
