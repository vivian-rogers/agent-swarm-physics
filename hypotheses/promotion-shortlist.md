# Promotion shortlist

The ideas we plan to promote and test first, with plans, observables and implications. IDs refer to [hypohypotheses/HYPOHYPOTHESES.md](hypohypotheses/HYPOHYPOTHESES.md) (HH numbers are permanent), [natural-experiments.md](natural-experiments.md) (NE) and [hypohypotheses/goal-periods.md](hypohypotheses/goal-periods.md) (#). Faithfulness axes A–I are from `writeup/paper.tex`, Sec. VI.

**Before any of them (Phase 0):** shared processed tables (planned in [`infra/README.md`](../infra/README.md)), the synthetic simulators, and a **locked holdout** of goal periods and NEs.

| # | Hypothesis | From | Models (primary first) | Needs text? | Becomes |
| --- | --- | --- | --- | --- | --- |
| S1 | Inferred couplings reflect real influence | HH44 + HH23 | 01, 02, 09 | no | H02 |
| S2 | Activity is self-exciting; criticality set by coupling mode | HH30 + HH32 | 09, 02 | no | H03 |
| S3 | External forcing reshapes the response kernel, reversibly | HH46 + HH31 | 09, 02 | speaker labels only | H04 |
| S4 | Cutting the cross-room channel lowers entropy production; rooms become coupled blocks | HH33 (+ H01 D1.1.a) | 02, 01, 09 | no | H05 |
| S5 | Ideological order is coupling-driven, not field-driven | HH27 + HH29 (= H01 D3.2) | 11, 03, 10 | embeddings | stays in H01 |
| S6 | Free weeks show neutral cooperative dynamics with a cooperator core | HH42 | 06, 10, 11 | topic labels | H06 |
| S7 | The RPG forks diverge from a common ancestor at a measurable rate | HH38 | 08, 10, 09 | artifact extraction | H07 |

Order: S1 and S2, then S3 and S4 (all laptop), then S5–S7 after Phase 2 (text → states, GPU). H02–H05 were assigned on 2026-10-03, when their cards were opened (H02 `H02-couplings-are-real`, H03 `H03-self-excited-criticality`, H04 `H04-reversible-forcing`, H05 `H05-rooms-cut`); permanent. H06 and H07 stay reserved for S6 and S7. H08 was assigned to "Context is the coupling" and H09 to the thermodynamics framing.

---

## S1 · Inferred couplings reflect real influence (validation)
- **Windows:** null weeks #10, #14, #49; leader week #45, contrasted with #44 and #26.
- **Plan:**
  1. Synthetic recovery: simulate swarms with known couplings and a planted leader, sampled like the village.
  2. On the null weeks, fit against the null hierarchy: independent agents; time-of-day and kickoff drive; turn-taking exclusion; model-family field.
  3. In #45, rank each agent's net outgoing influence, Σ_j(J_ji − J_ij).
- **Observables:** coupling strengths vs. circular-shift nulls; fraction of significant couplings; the leader's rank and z-score; agreement between the Ising and Hawkes influence networks.
- **Falsifier:** null weeks couple as strongly as collaborative weeks, or the leader isn't the top influencer.
- **Implications:** pass → couplings can be interpreted elsewhere, including H01. Fail → the artifact is found before it contaminates anything.
- **Axes reachable:** A, C, F, G.

## S2 · Self-exciting activity; criticality set by coupling mode
- **Windows:** all 51 periods; rolling windows through #51.
- **Plan:**
  1. Hawkes fits per period, with a baseline for the daily window and kickoffs; exponential and power-law kernels.
  2. Time-rescaling diagnostics.
  3. Day-level bootstrap for confidence intervals.
  4. Synthetic non-stationary Poisson fits as a guard against spurious criticality.
- **Observables:** branching ratio n per period; kernel timescales; cascade-size distributions; phase diagram #1 (n over agent count × hours, colored by mode).
- **Prediction:** holidays and free weeks n < 0.5; shared-objective weeks higher; #51 drifts toward n → 1.
- **Implications:** how much activity is self-generated vs. driven; which periods are near-critical. If n doesn't depend on mode, the scheduler, not social interaction, drives activity.
- **Axes:** B, C, D, I.

## S3 · Forcing reshapes the response kernel, reversibly
- **Window:** #46–#50: NE21 (hours 4→8→4→8 h) and NE23 (nudger off/on); NE10 (nudger switch-on, #30) as a replicate.
- **Plan:**
  1. Averaged responses (Green's functions) to nudges, human messages and kickoffs.
  2. Linearity tests: dose, superposition, time-translation.
  3. Kernel and n per segment of the reversal.
  4. Fluctuation vs. response comparison, giving an effective temperature per segment.
- **Observables:** response shape, amplitude and decay per segment; susceptibility; effective temperature.
- **Falsifier:** no reversal; the kernel drifts one way regardless of the switches.
- **Implications:** the first true interventional test (E = 2). Shows which operator levers are control parameters, and gives a direct measure of distance from equilibrium.
- **Data note:** nudger messages are identifiable from the speaker name "automated" (2,230 messages), so no text processing is needed.
- **Axes:** B, D, E.

## S4 · Rooms cut lowers entropy production; rooms become coupled blocks
- **Windows:** NE12 (2026-02-25, inside #32): #31 and early #32 before; late #32 through #35 after. NE15 as a second cut.
- **Plan:**
  1. Entropy-production lower bound per window, per agent-hour.
  2. Within-room vs. cross-room couplings.
  3. **Difference-in-differences across agent pairs**: pairs that stay co-located are the control. This removes the same-day operator reset (NE35), which affects all pairs alike.
- **Observables:** change in cross-room vs. within-room coupling; change in entropy production; room-level individuality.
- **Prediction:** cross-room coupling → 0; within-room coupling holds or rises; entropy production falls.
- **Implications:** an interventional validation with known structure, and first evidence on rooms as candidate superagents (H01 D1).
- **Axes:** C, E, G.

## S5 · Ideological order: coupling vs. field (H01 D3.2)
- **Windows:** #8, #41 (independent convergence); #21 (coupling switched on mid-week); NE12 (coupling cut); NE32 (isolated triplet: an exposure-free baseline).
- **Plan:** embed and whiten chat and session goals; polarization and alignment with the goal per window; split agreement into a field part (agents who couldn't see each other) and a coupling part (residual given exposure); semantic entropy of positions per group.
- **Rival predictions:**
  - *Field-driven:* alignment survives NE12, appears in isolated agents, jumps at kickoffs.
  - *Coupling-driven:* alignment drops at NE12, is absent in isolated agents, grows with exposure.
- **Implications:** decides H01's direction. Coupling → superagents plausible; continue to D1 and D4. Field → reframe around model families as pre-formed units.
- **Compute:** a few GPU-hours for embeddings.
- **Axes:** C, D, E, H.

## S6 · Neutral cooperative dynamics in free weeks (HH42)
- **Windows:** pooled free weeks #11, #16, #22, #31, #37, plus #44 #rest; #51 as a check. Batch joins NE27 and NE33 act as pulses of new arrivals (μ).
- **Plan:**
  1. Project labels from the self-written goals (session goals before F, `CONSOLIDATE` `nextSessionGoal` after): embed and cluster, with sensitivity to the clustering.
  2. Individuals = agent slots or sessions (agents alone give N of only 7–13 in these weeks); species = project clusters.
  3. Estimate μ (rate of novel clusters per replacement).
  4. Compare the abundance distribution P_n and Simpson λ with the predicted λ*(μ, N) and the boundaries μ_B (bimodal) and μ_L (log-series).
  5. Scatter of residence time vs. maximum abundance: expect two clusters.
  6. Frequency dependence: per-capita recruitment vs. share.
  7. Small N: simulate the exact finite-N rules rather than rely on asymptotics.
- **Observables:** P_n histograms; λ vs. λ*; the two-cluster scatter; the slope of recruitment vs. share.
- **Rival:** Hubbell neutral theory (log-series, no cooperation).
- **Falsifier:** log-series abundances in low-μ free weeks; no frequency dependence; λ far from λ*.
- **Implications:** the only test against an analytic theory with essentially no free parameters beyond μ and N. If it holds, cooperation-requiring recruitment explains the project ecology. If it fails, projects are field-driven (pretraining attractors), which bears on H01 D8.
- **Axes:** C, D, H, I.

## S7 · RPG forks diverge from a common ancestor (HH38)
- **Windows:** #34 (shared RPG build) → #35 (fork into #best and #rest, NE15) and after; NE32 (isolated triplet) as a second split; #44 distillation for contrast.
- **Plan:**
  1. Reconstruct each fork's lineage from git commands and outputs in `computer_use_turns`, repository and file names, and links shared in chat.
  2. Extract comparable features: identifiers, mechanics and item names, numeric parameters.
  3. Copy vs. transformation decomposition per feature type, as a function of days since the split.
  4. Detect leakage across rooms (via history search, or agents who moved rooms).
- **Observables:** the decay curve of copy information; the copy fraction per feature type; leakage events.
- **Falsifier:** forks stay identical (no divergence), or diverge totally at once (no inheritance). Either outcome is informative.
- **Implications:** a measured "mutation rate" and inheritance curve for agent-made artifacts; validates model 08's decomposition; tests whether room isolation is real (feeds H01 D1 and D5).
- **Data note:** needs the artifact table. Fetching the public repositories' commit histories was approved by Vivian (2026-10-03).
- **Axes:** C, D, E (the split itself), G (known fork date).


## Shortlist 2 (2026-10-03): magnet-like and Kolchinsky models, chosen for practical swarm analysis

Proposed after exploratory round 1 (H02–H05, H07, H09) and the first holdout runs. Vivian picked items 1, 2, 3, 4, 6, 9 and 10. She had no intuition for item 5 (HH90, attention conservation) and was lukewarm on items 7 (HH13 + HH09, transmission) and 8 (HH12 + HH57, consolidation), so those stay as HHs.

| # | Hypothesis | From | Models | Assigned |
| --- | --- | --- | --- | --- |
| S8 | Goals are Legendre pushes | HH49 + HH85 | 11, 01 | H10 |
| S9 | Division of labor vs herding is the sign of a Potts coupling | HH24 + HH26 + HH84 | 10 | H11 |
| S10 | Groupthink is dimensional collapse | HH77 + HH58 | 01, 11 + RMT | H12 |
| S11 | Model families carry their own fields and couple by family | HH10 + HH75 + HH89 | 11, 10, 01/02 | H13 |
| S12 | Entropy production of behavior-state sequences | HH19 + HH67 | 02 + AIK estimator | H14 |
| S13 | Semantic information through natural scrambles | HH43 → H01 D4.1.b | 04 | H15 |
| S14 | Metastable traps and Kramers escape | HH53 + HH86 | 02, 01, 11 | H16 |

### Round-1-inspired promotions (2026-10-03)
| # | Hypothesis | From | Models | Assigned |
| --- | --- | --- | --- | --- |
| S15 | Behavior is a Markov state model with metastable sets | HH97 | 02, 10 + MSM | H17 |
| S16 | Attention dilutes as 1/k | HH99 | 01, 09, 02 | H18 |
| S17 | One curve for all periods (loop-gain data collapse) | HH100 | 01, 09, 02 | H19 |
| S18 | Aging of content correlations | HH101 | 01 (SK), 11 | H20 |

### Goal-period-specific promotions (2026-10-03)
| # | Hypothesis | From | Models | Assigned |
| --- | --- | --- | --- | --- |
| S19 | The debate week (#12) is a two-sublattice antiferromagnet | HH103 | 11, 10, 01 | H21 |
| S20 | Private, conflicting goals make #51 a spin glass | HH102 | 01 (SK), 11, 10 | H22 |
| S21 | Leader distillation copies vocabulary, transforms plans (#44) | HH39 | 08, 04, 11 | H23 |
| S22 | Forecast week (#21): drafting → comparison switches the coupling on | HH28 | 11, 01 | H24 |
| S23 | Potts explains the election (#26) | HH22 | 10 | folded into H11 as `G26` |

### Usefulness-first promotions (2026-10-04)
Vivian picked these from HH107–HH126 and the leftovers. HH92 was already H08's primary test (H08 is running). HH119 is low priority.

| # | Hypothesis | From | Models | Assigned |
| --- | --- | --- | --- | --- |
| S24 | A distance-to-criticality dial, T/T_c, per window and per channel | HH107 | 01, 09, 11 | H25 (wave 1) |
| S25 | The swarm is near-critical in what it says but subcritical in when it acts | HH108 | 11, 01 | H26 (wave 2) |
| S26 | Critical slowing down warns of herding waves hours ahead | HH109 | 10, 01 | H27 (wave 1) |
| S27 | Links are the contagion vector of herding | HH114 | 10 (kinetic), 03 | H28 (wave 1) |
| S28 | Driver nodes: where an operator message moves the whole swarm | HH110 | 02 (linear response), graph controllability | H29 (wave 1) |
| S29 | An operator-susceptibility gauge χ_op: how steerable is the swarm today? | HH116 | 01, 11 | H30 (wave 1) |
| S30 | Consensus time scales with the interaction graph's spectral gap | HH115 | 10, graph diffusion | H31 (wave 1) |
| S31 | A net information current identifies de facto leaders | HH118 | 11, 02 | H32 (wave 1) |
| S32 | The diversity–productivity curve is an inverted U: the swarm's operating point | HH119 | 11, 06 | H33 (wave 2) |
| S33 | Idea cascades follow a power law whose exponent reads off the distance to criticality | HH122 | 03, 09 | H34 (wave 2) |
| S34 | The nudger is a measurably inefficient Maxwell demon | HH124 | 04 (Kolchinsky), 02 | H35 (wave 2) |
| S35 | A reorganization alarm: susceptibility and multi-information peak at transitions | HH126 | 01, 11 | H36 (wave 2) |
| S36 | Conflict lives in stance, not topic: stance spins are antiferromagnetic | HH125 | 01 (signed), 10 | H37 (wave 2) |
| S37 | Joint silences are platform stalls | HH94 | 01, 09 | H38 (wave 1) |
| S38 | Catalysts vs. fields | HH52 | 09, 02, 10 | H39 (wave 2) |
| S39 | The call clock sets the coupling | HH154 | 02, 09 | H40 (waits for DQ) |
| S40 | Read-out gating gives the swarm a light cone | HH155 | 02, 03 | H41 (waits for DQ) |
| S41 | Cross-excitation is a delayed step at the next read-out | HH174 | 09 | H42 (waits for DQ) |
| S42 | Kicks leave a refractory window | HH177 | 09, 03 | H43 (wave A, ready) |
| S43 | Erasure makes agents busy but unproductive | HH156 | 02, 04 | H44 (waits for DQ) |
| S44 | Context homeostasis: each agent keeps its context near a set point | HH166 | 04, 05 | H45 (waits for DQ) |
| S45 | Style is a conserved charge | HH170 | 04, 11 | H46 (wave A, ready) |
| S46 | Rooms set the coherence length | HH172 | 11 | H47 (wave A, ready) |
| S47 | The settling time is a mixing time on the read-out graph | HH173 | 11, 03 | H48 (waits for DQ) |
| S48 | Edge-trimmed regime III is a dilute ferromagnet | HH159 | 01 | H49 (wave A, ready) |
| S49 | Field or coupling: transfer functions and lag tell which | HH167 | 01, 02 | H50 (waits for DQ) |
| S50 | One dial: an effective coupling collapses the phase diagram | HH178 | 10, 02 | H51 (waits for DQ) |
| S51 | Humans are just loud agents | HH164 | 02 | H52 (waits for DQ) |
| S52 | Herding is announcement-seeded nucleation | HH168 | 10, 03 | H53 (waits for DQ) |
| S53 | The kickoff text is the quench target | HH169 | 11, 10 | H54 (wave A, ready) |
| S54 | Norm-enforcers are the swarm's immune cells | HH162 | 04, 06 | H55 (waits for DQ) |
| S55 | Entropy production fingerprints the platform | HH175 | 02, 05 | H56 (wave A, ready) |
| S56 | Copying beats transformation when the backlog is large | HH171 | 08, 03 | H57 (waits for DQ) |
| S57 | Effective superagents are coordinated agents plus their artifacts | HH176 | 04 | H58 (waits for DQ) |
