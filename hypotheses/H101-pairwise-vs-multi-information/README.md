# H101: Pairwise Ising vs full multi-information in co-usage

**Status:** specified (approved by Vivian in the dashboard vetting panel 2026-10-04 from HH322; round 1 launching)
**Fields:** <to be filled by the round-1 agent>
**Literature:** <links to literature/*.md>
**Definitions used:** <terms from physics-models/DEFINITIONS.md, with variant names if any>
**From:** HH322 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/01*/`, `physics-models/12*/`

## Source HH (verbatim from the HH list, including refinements)
Higher-order structure in co-usage: pairwise max-ent vs the full multi-information (Schneidman). For binary use of conventions or projects per agent-day, fit a pairwise Ising model and report the fraction of multi-information I_N it captures, I_2/I_N.
  - *Prediction:* I_2/I_N > 0.9 after field removal: pairwise structure suffices, there is no higher-order "group mind", and this matches H49's dense-field reading. A substantial higher-order remainder (I_2/I_N < 0.8) beyond a shared-field null would be the egregore-positive outcome.
  - *Kill for the egregore reading:* I_2/I_N ≈ 1.
  - *Models:* 01 · *Builds on:* H49, H11, HH298

*Suggested first picks.*

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
