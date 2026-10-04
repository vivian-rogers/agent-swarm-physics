# H88: Collective memory decays biexponentially

**Status:** specified (approved by Vivian in the dashboard vetting panel 2026-10-04 from HH316; round 1 launching)
**Fields:** <to be filled by the round-1 agent>
**Literature:** <links to literature/*.md>
**Definitions used:** <terms from physics-models/DEFINITIONS.md, with variant names if any>
**From:** HH316 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/13*/`, `physics-models/04*/`

## Source HH (verbatim from the HH list, including literature refinements)
Collective memory decays biexponentially (communicative + cultural). After a goal period ends, follow attention to its artifacts and terms: references, reads and commits. Candia et al. find a fast communicative component, carried by the people who were there, and a slow cultural component, carried by the record.
  - *Prediction:* a biexponential, with a fast τ₁ of days carried by veterans of that period and a slow τ₂ of weeks carried by the record. Newcomers contribute only to the τ₂ component.
  - *Egregore reading:* the slow component is the village's cultural memory.
  - *Kill:* a single exponential, or decay set entirely by veterans' departure.
  - *Models:* 04 · *Builds on:* H15, H44, HH290, HH294
  *Refinement (literature, 2026-10-04):* The primary paper (Candia et al. 2019) has no arXiv version and is not in `literature/`; the biexponential form is quoted from memory.

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
