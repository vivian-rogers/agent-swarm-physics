# H87: κ table: commits per bit by channel

**Status:** specified (approved by Vivian in the dashboard vetting panel 2026-10-04 from HH307; round 1 launching)
**Fields:** <to be filled by the round-1 agent>
**Literature:** <links to literature/*.md>
**Definitions used:** <terms from physics-models/DEFINITIONS.md, with variant names if any>
**From:** HH307 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/04*/`, `physics-models/12*/`

## Source HH (verbatim from the HH list, including literature refinements)
The semantic-information channel table: κ in commits per bit, by channel. This is the flagship quantitative Kolchinsky test. For each channel c (memory, context window, own artifacts, chat reads, human messages, kickoff, history search), estimate:
  - the information I_c the channel carries about the agent's next allocation (bits; plug-in with Miller–Madow or NSB bias correction on the discretized which-repo/which-state variable);
  - its value ΔV_c, the viability lost when it is naturally scrambled.

  Viability is commits in the next 40 calls, or P(return to own artifact). The natural scrambles are: memory size at erasure, forced erasure, the re-read vs no-re-read contrast, the room cut, the human-message dose, the kickoff change, and the search outage. Report κ_c = ΔV_c / I_c and η_c = S_c / I_c.

  Prediction, ordered: κ_artifact > κ_context > κ_chat > κ_kickoff > κ_memory ≈ 0. From H15, κ_memory has a CI including 0. From H44, the context channel is worth ~10% of segment output, and H58's re-read gives P(return) 0.96 vs 0.85. *Kill:* the order is not separable (CIs overlap across all channels), or chat ≥ artifact.
  *Models:* 04 · *Builds on:* H15, H44, H58, H05, H54, HH294

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
