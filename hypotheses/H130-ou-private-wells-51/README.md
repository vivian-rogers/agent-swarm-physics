# H130: #51 agents are Ornstein–Uhlenbeck particles in private wells: reads kick them and the kick decays at the well's rate

**Status:** specified (approved by Vivian in the dashboard vetting panel 2026-10-04 from HH371; round 1 launching)
**Fields:** <to be filled by the round-1 agent>
**Literature:** <links to literature/*.md>
**Definitions used:** <terms from physics-models/DEFINITIONS.md, with variant names if any>
**From:** HH371 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/11*/`, `physics-models/02*/`

## Source HH (verbatim from the HH list, including refinements)
- **HH371 · #51 agents are Ornstein–Uhlenbeck particles in private wells: reads kick them and the kick decays at the well's rate.** H98 found #51 is a static random field with a weak pull, plus co-movement through conversation. The simplest kinetic version: each agent relaxes toward its own private goal direction at rate γ, and each read of another agent's message is a small kick toward it.
  - *Prediction:* after a read, an agent's content moves toward the sender by a small amount that decays as e^(−γτ), and the same γ also sets the agent's own autocorrelation decay (an unfitted consistency check). Pairs with more reads co-move more, and the co-movement decays at γ.
  - *Check:* per-call content projections in #51 main body; event-triggered averages after reads vs matched non-read calls; fit γ two ways.
  - *Kill:* the two γ estimates differ by more than ×2, or no read kick beyond the in-flight placebo.
  - *Impostors:* niche overlap (shared role text) is a common field; use the read vs in-flight contrast.
  - *Models:* 11, 02 · *Builds on:* H98, H22, H65 (read_response)

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
