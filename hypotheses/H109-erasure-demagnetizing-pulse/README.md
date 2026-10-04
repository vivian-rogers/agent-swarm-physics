# H109: The forced erasure is a demagnetizing pulse: where is the room's order stored?

**Status:** specified (approved by Vivian in the dashboard vetting panel 2026-10-04 from HH339; round 1 launching)
**Fields:** <to be filled by the round-1 agent>
**Literature:** <links to literature/*.md>
**Definitions used:** <terms from physics-models/DEFINITIONS.md, with variant names if any>
**From:** HH339 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/11*/`, `physics-models/04*/`

## Source HH (verbatim from the HH list, including refinements)
- **HH339 · The forced erasure is a demagnetizing pulse: where is the room's order stored?** NE41 wipes an agent's context at a time set by the scaffold (about 18.6k forced events, regime III). If the room's spontaneous order is held by coupling through the context (H08; H102: content follows the room you speak in), the agent's alignment with its room's direction should drop right after a forced erasure, then recover as it re-reads the room. If the order is held by a self-made field (its own repo, H70: 89% return), alignment should not drop. This is a Kolchinsky scramble of one channel.
  - *Prediction:* alignment with the room direction Δ_spont falls by ≥ 30% in the first 3 post-erasure statements and recovers in proportion to room items re-read (ledger). Alignment with the kickoff target, which is held in the prompt since NE13, does not fall.
  - *Check:* statement-level projections around forced erasures vs matched placebo calls (same agent, same day, no erasure); voluntary erasures as a second contrast. Use H100's identical-kickoff periods and #51g (#focus). Both models.
  - *Kill (context-held order):* no drop, with power ≥ 0.8 at a 30% drop. The spontaneous share is then held in artifacts or memory, not by coupling.
  - *Impostors:* scheduler: the timing is set by the scaffold, so the design is quasi-random. Exogenous: the kickoff-alignment control. Priors: agent fixed effects. Convergence: the recovery is regressed on items read vs posted-unread at matched age.
  - *Models:* 11, 04 · *Builds on:* H100, H102, H15, H69, H70

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
