# H115: Blind role recovery in the debate week: the judge is a sink of antisymmetric coupling (#12)

**Status:** specified (approved by Vivian in the dashboard vetting panel 2026-10-04 from HH353; round 1 launching)
**Fields:** <to be filled by the round-1 agent>
**Literature:** <links to literature/*.md>
**Definitions used:** <terms from physics-models/DEFINITIONS.md, with variant names if any>
**From:** HH353 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/02*/`, `physics-models/01*/`

## Source HH (verbatim from the HH list, including refinements)
- **HH353 · Blind role recovery in the debate week: the judge is a sink of antisymmetric coupling (#12).** Debaters address the judge and the judge rules on them. That is a known one-way influence pattern.
  - *Prediction:* from talk spins alone, the agent with the largest in-minus-out antisymmetric coupling Σ_j(J_ji − J_ij) is the judge (rank 1 of 7), and the team blocks show positive within-team J. The judge's rulings act as field steps on the debaters, not the other way round.
  - *Check:* fit on non-holdout #12 days; compare against the DQ6 ground-truth roles only after the ranking is frozen.
  - *Kill:* judge rank ≥ 4, or team blocks absent from symmetric J (H101 found them in co-usage, J +0.15 within vs −0.60 across).
  - *Impostors:* assigned roles are a field; the read-gated contrast separates reacting to a read message from following the schedule.
  - *Models:* 02, 01 · *Builds on:* H21, H37, H101

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
