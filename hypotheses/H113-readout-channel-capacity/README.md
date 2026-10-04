# H113: Read-out channel capacity: information per call grows as k^(1−β) ≈ k^0.34

**Status:** specified (approved by Vivian in the dashboard vetting panel 2026-10-04 from HH345; round 1 launching)
**Fields:** <to be filled by the round-1 agent>
**Literature:** <links to literature/*.md>
**Definitions used:** <terms from physics-models/DEFINITIONS.md, with variant names if any>
**From:** HH345 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/04*/`, `physics-models/12*/`

## Source HH (verbatim from the HH list, including refinements)
- **HH345 · Read-out channel capacity: information per call grows as k^(1−β) ≈ k^0.34.** H18's dilution (per-sender uptake ∝ k^−0.66) implies that the total uptake from a batch of k messages read at one call grows as k^0.34. H59 instead found that one read acts as one kick: dose saturates in #5. These two results disagree on the shape of the read-out channel's capacity curve.
  - *Prediction:* the Gaussian mutual information between the batch's message directions and the reader's next statement grows as k^(0.34 ± 0.1). Per-message information falls as k^−0.66.
  - *Check:* receiving calls from the ledger, with k the new items read; content projections orthogonalized to the reader's previous statement; the in-flight placebo at matched age; both models.
  - *Kill:* the exponent's CI excludes 0.34. Flat (exponent ≈ 0) means a hard capacity of one message per call; linear means no bottleneck.
  - *Impostors:* convergence: in-flight placebo. Exogenous: goal directions projected out. Priors: style_resid. Scheduler: n/a (call level).
  - *Models:* 04, 12 · *Builds on:* H18, H59, H08, H70

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
