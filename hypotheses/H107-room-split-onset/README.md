# H107: Does the room split grow from zero (an instability) or appear at once (a hidden field)?

**Status:** specified (approved by Vivian in the dashboard vetting panel 2026-10-04 from HH337; round 1 launching)
**Fields:** <to be filled by the round-1 agent>
**Literature:** <links to literature/*.md>
**Definitions used:** <terms from physics-models/DEFINITIONS.md, with variant names if any>
**From:** HH337 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/11*/`, `physics-models/10*/`

## Source HH (verbatim from the HH list, including refinements)
- **HH337 · Does the room split grow from zero (an instability) or appear at once (a hidden field)?** H100 found that two rooms with identical kickoffs still diverge (Q_spont up to 4.2 in #41), but the spontaneous share is a residual. True spontaneous symmetry breaking starts at zero separation. The separation then grows, and its direction is chosen by early fluctuations (nucleation, then coarsening). A hidden field, such as the work each room inherits, gives full separation on day 1, along a direction that the members' previous repos predict.
  - *Prediction (SSB):* in H100's identical-kickoff periods, the day-1 separation is ≤ 0.3 of the period's final separation and grows monotonically. The day-1 direction aligns with the final direction at |cos| < 0.5. The members' previous-period repo labels (DQ4) do not predict the direction.
  - *Check:* H100's cross-fitted separation S(d) and relabel excess per active day (or half-day). Correlate the direction Δ(d) with Δ(final). Predict Δ from a Potts field built from each room's pre-period repos (H100-R3 machinery).
  - *Kill (SSB):* S(1) ≥ 0.8 S_final with day-1 direction cos ≥ 0.7, or the pre-period repos predict the direction. The "spontaneous" share is then a hidden field.
  - *Impostors:* exogenous: identical kickoffs plus the repo field as an explicit covariate. Priors: agent constants removed (H100). Scheduler: n/a. Convergence: growth alone cannot separate coupling from a self-made room drive; HH339 does that.
  - *Models:* 11, 10 · *Builds on:* H100, H102, H93

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
