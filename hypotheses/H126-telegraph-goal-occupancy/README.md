# H126: Goal occupancy is a telegraph process: dwell times predict the occupancy

**Status:** specified (approved by Vivian in the dashboard vetting panel 2026-10-04 from HH367; round 1 launching)
**Fields:** <to be filled by the round-1 agent>
**Literature:** <links to literature/*.md>
**Definitions used:** <terms from physics-models/DEFINITIONS.md, with variant names if any>
**From:** HH367 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/10*/`, `physics-models/02*/`

## Source HH (verbatim from the HH list, including refinements)
- **HH367 · Goal occupancy is a telegraph process: dwell times predict the occupancy.** H105 found on-goal occupancy p 0.23–0.44 with binomial variance. The simplest kinetic model is a two-state switch per agent with rates k_on (set by the goal field) and k_off: p = k_on/(k_on + k_off).
  - *Prediction:* on- and off-goal dwell times (in calls) are each roughly exponential, and p predicted from the two mean dwells matches the measured occupancy within 20% in each assigned week. A kickoff raises k_on, not k_off.
  - *Check:* per-statement on/off-goal labels (H105's decoy threshold; calibrate first, as H105 asked); dwell distributions per agent and week.
  - *Kill:* dwell distributions far from exponential (strongly heavy-tailed), or predicted p off by more than 30%.
  - *Impostors:* misclassified statements shorten dwells; run the synthetic misclassification correction from H105 first.
  - *Models:* 10, 02 · *Builds on:* H105, H10

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
