# H55: Norm-enforcers are the swarm's immune cells

**Status:** exploratory round 1 **done (2026-10-04 UTC): friction refuted, in reverse; immune function untestable at the sensor's recall; HH210's coverage claim holds.** Agents who correct others receive *warmer* replies, not colder (ρ −0.24 across 27 periods, p 0.04; #51 −0.60), and replies to a correction are no more negative than replies to the same agent's other messages. Corrections almost never reach a looping agent (0.65% of loop episodes), and where they do, no effect on escape is detectable; simply being addressed raises loop escape by 5 points. Design, observables, nulls and predictions written 2026-10-04 06:26 UTC, before any H55 outcome statistic. `analysis/confirm.py` (#51 tail, G22/G28/G29/G32) written and dry-run, **not run**.
**Fields:** sociophysics (norm enforcement, signed interactions), physics of life (Kolchinsky–Wolpert viability, error correction), stat mech (escape hazards)
**Literature:** `literature/kolchinsky-2018-semantic-information-autonomous-agency.md` (viability, self-maintenance), `literature/bartlett-2025-physics-of-life-information-roadmap.md` (error correction as a cost of staying alive), `literature/pinero-2025-neutral-theory-cooperative-dynamics.md` (copying without fitness differences; the rival "loops end on their own").
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime; Population; Interaction, H37 variant *stance spin* and *stance coupling (residual)* (used with DQ2's 4-class labels, see below); *lever episode* (H39) for the event-study logic (past-only eligibility). New named terms proposed for DEFINITIONS.md (owner to add): **correction (H55 lexical marker)**, **directed read**, **loop episode (restatement / copy)**, **blocked episode (v3)**, **immune contrast Δ** (defined below).
**From:** HH162 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` (also HH210, the missing immune system) · **Models:** `physics-models/04-semantic-information/`, `physics-models/06-neutral-cooperative-dynamics/`; signed bonds per `physics-models/01-inverse-ising/` (pitfall: calibrated agent-field null)
**Data inputs (shared tables first):** DQ2 `reply_pairs` (parents, soft stance, `opp_type`), DQ5 `statement_flags` (`self_repeat_bge`, `self_repeat_gte`, `self_repeat_both`), DQ1 context ledger (`context_ledger_items`, `context_ledger_turns`), DQ3 `behavior_states_v3` (`p_blocked`), DQ6 `ground_truth_labels` (#51 roles, #12 judges and teams), `chat_core` + `chat_mentions_clean` + `chat_text` (text in memory only), `period_units`; H16 trap tables (TS3/TS4, read-only, secondary).

## Standards (2026-10-04)
*Documentation pass against `STANDARDS.md`. No analysis was re-run. H55 has no round-1b section; round 1 already ran on the corrected inputs.*

**Question served:** Q5. The card asks whether the swarm repairs its own failures or an operator must supply the repair (being addressed is the working lever). Q3 second: self-repair would be a collective function.

| Impostor | Relevant? | How it was handled | Status |
| --- | --- | --- | --- |
| Scheduler field | partly | Loops are within-day runs; matched strata include period unit and loop age; outcomes are agent-demeaned (Amendment 2). No synchrony statistic. | removed |
| Exogenous field (kickoff/goal/operator) | partly | Sender kind (agent or human) is a matching stratum (O5). G16 compares an operator-rule week with a no-rule baseline. | removed |
| Shared model priors | yes | Speaker and target fields from the ordered logit absorb agreeableness (O2, R-style); the partial ρ is unchanged. A shared politeness field and a labeller habit are not separated (Caveat 3). Close with a cross-family split of the friction ρ and a second labeller (§1, row 3). | partly |
| Contemporaneous convergence | partly | Directed reads are timed by the ledger between the two statements, so the agent read them before the outcome (O5). | removed |

**Inputs:** round 1 uses DQ2 replies and stance, DQ5 `statement_flags` (both models), the context ledger, DQ3 `behavior_states_v3` and DQ6 roles. Activity bins and work are not inputs. Still old: directed reads by naming use `chat_mentions_clean`, not the leading-@ target.

**Two layers:** 31 replication folders. Native tests: 4 (`G12`, `G16` and `G51` mixed; `G38` failed).

**Confirm script:** `analysis/confirm.py` exists, dry-run only, built on the corrected inputs (C1–C5). No re-freeze needed. Prerequisite before a run: a Jev correction-subtype pass on held-out pairs (about $0.08), not yet done.

## Question
Do the agents that issue the most corrections and declines draw more negative stance, and do corrections read by an agent stuck in a self-repetition loop or a blocked spell precede the end of that loop or spell? At swarm level, do periods with more or stronger enforcement have shorter loops? If so, friction is the price of error correction, and a swarm without enforcers loops longer (HH210).

## Design: two layers (Vivian, 2026-10-04; see `infra/data-quality/QUEUE.md`)
- **Replication:** the common estimators (enforcer → received stance; immune contrast for loops and blocked spells) on every eligible goal period. Period README role: `replication`.
- **Period-native tests:** four periods with leverage no other period gives (G51 roles, G12 judges, G16 operator rules, G38 the loop-densest regime-III week). Period README role: `native`.

## Model
**From:** `physics-models/04-semantic-information/` (viability and the value of error-correcting information) with a hazard model for loop and trap escape (H16's discrete-time hazards), and `06-neutral-cooperative-dynamics/` as the null family (loops end at a rate that does not depend on what the agent reads).

**H55 variant.** Each agent i in a failure state (a self-repetition loop, or a blocked spell) leaves it at a per-step hazard
logit h_i(k) = α_i + β_age·ln k + β_D·D + β_C·C + β_nov·ν,
where k is the age of the loop, D = 1 if the agent read a message directed at it since its last step, C = 1 if one of those directed messages is a correction, decline or norm enforcement, and ν is the novelty of what it read. **Immune function** means β_C > 0 beyond β_D and β_nov: corrections, not just attention or novelty, end failures. **Friction** means an enforcer j receives replies with a more negative stance, beyond the replier's agreeableness and j's general likability: in the ordered logit P(y ≤ m) = σ(c_m − a_speaker − b_target), the received field ν_j = −b_j rises with j's correction rate c_j. In Kolchinsky–Wolpert terms, viability V of the swarm's working state is "not in a loop or blocked spell", corrections are the environment → system information whose value ΔV is measured by the immune contrast, and the stance cost is the price paid for it.
**Rivals:** R0 neutral escape (loops end at their own aging rate; reading changes nothing); R-address (any directed message ends loops, H29/H16: address-gated read-out); R-novelty (H12-R2: any novel input ends loops, regardless of who sends it or whether it corrects); R-style (agents that correct are just argumentative: their received negativity is reciprocity for their own negative speaker field, not the price of correcting); R-label (Jev over-calls "opposes" on replies to correcting messages because they look like disputes; a labelling artifact).

## Data scheme (`scheme/`)
- **Inputs:** shared tables listed above; non-holdout rows only (`holdout_mask` re-checked); H16's `ts3`/`ts4` parquet (read-only).
- **`scheme/lexicon.py` (frozen before the validation sample is drawn):** the H55 correction marker. Applied in memory to the text of every agent and human chat message; only booleans are stored.
  - **corr** (points out an error): *actually* at a clause start, *correction*, *to clarify*, *not (quite) right/correct/accurate/true*, *incorrect*, *inaccurate*, *wrong*, *mistake(n)*, *typo*, *error in*, *misread*, *misunderstood*, *that's not*, *isn't right/correct/true/accurate*, *should be*, *you mean*, *broken link*, *404*, *doesn't work/load/exist*, *already done/posted/exists/claimed*, *duplicate*, *outdated*, *no longer*, *not (yet) live/deployed*.
  - **norm** (asks someone to change behaviour on a rule, norm, ethics or process ground): *please don't / do not / stop / avoid / refrain / hold off*, *let's not / avoid / stop*, *we shouldn't / agreed / can't*, *reminder*, *against the rules / guidelines / policy*, *not allowed*, *violat-*, *spam*, *consent*, *boundar-*, *inappropriate*, *harmful*, *unethical*, *privacy*, *off-topic*, *stay on topic / task*, *stop posting / repeating*, *repeating (yourself / the same)*, *loop*.
  - **decl** (declines a request): *I can't / cannot / won't / will not / am unable / must decline / decline / 'll pass / 'd rather not / am not able / 'm not comfortable*, *can't help with*, *not going to*.
  - **Addressed:** the message has a DQ2 visible candidate parent (pair_set = cand, labelled, p_reply ≥ 0.5) by another participant, or names another roster agent (`mentions_roster`). For human messages: names a roster agent.
  - **Correction (H55 lexical marker):** addressed AND (corr OR norm OR decl). Subtypes kept.
- **Second sensor (Jev, DQ2, aggregate only):** a message is a *Jev correction* if its DQ2 parent pair has stance = opposes with stance_conf ≥ 0.8 and opp_type ∈ {correction, decline}. No new Jev labels (the shared OpenRouter account is out of credit; HTTP 402). A labelling step is written behind a flag (`scheme/label_corrections.py --run`), not run.
- **Validation (blind):** 150 non-holdout addressed agent messages: 90 drawn at random (stratified by regime ∝ size), 40 marker-positive and 20 Jev-correction, shuffled together; labelled by Claude with the parent message as context, without seeing any marker, Jev answer or stratum. Codes: corr / norm / decl / none. Sheets (text) stay in the session scratchpad; only codes go to `data/processed/H55-norm-enforcer-immunity/validation/`.
- **`scheme/build.py`** → `data/processed/H55-norm-enforcer-immunity/`:
  - `messages.parquet`: one row per chat message (agent and human), codes only: id, time, sender, room, unit, length, mentions, DQ2 parent (id, author, p_reply, stance probabilities, opp_type), marker booleans, statement flags (restatement = bge or gte; copy = both; exact).
  - `loops.parquet` / `loop_steps.parquet`: loop episodes and their at-risk steps; `blocked_steps.parquet`: v3 blocked episodes and steps; `reads.parquet`: for each at-risk step, the directed messages read (via the context ledger) and their classes.
- **Regimes covered:** I, II, III (all non-holdout periods). Loops are defined within PT day (DQ5's self-repeat compares within day).

## Observables
*Written 2026-10-04 06:26 UTC.*
**O1. Correction rate** c_j(p): share of agent j's addressed messages in period p that carry the marker (validated sensor), and its subtype shares.
**O2. Received stance field** ν_j(p) = −b_j from H37's ordered logit (`infra/shared/nulls.py: fit_ordinal`) with speaker and target fields, fitted on agent→agent DQ2 candidate pairs with p_reply ≥ 0.5; class y = −1 (opposes, conf ≥ 0.8), +1 (supports, conf ≥ 0.8), else 0. Agents with ≥ 20 received and ≥ 20 sent labelled replies.
**O3. Friction, agent level:** Spearman ρ_p(c_j, ν_j) over eligible agents; partial version controlling for j's speaker field a_j (R-style).
**O4. Friction, message level (within target):** among replies to agent j's messages, the soft-stance contrast γ_p = E[s | parent is a correction] − E[s | parent is not], with speaker and target fixed effects (s = p_supports − p_opposes, weighted by p_reply); agent-day cluster bootstrap.
**O5. Immune contrast for loops** Δ^loop_p. A **loop episode** is a maximal run of ≥ 2 consecutive chat statements of one agent on one PT day flagged as restatements (bge or gte self-repeat; primary) or copies (both models; reported). At-risk step: a flagged statement with run age k ≥ 2; outcome y = 1 if the agent's next statement that day is unflagged (escape), 0 if flagged; censored if none. **Directed read:** a message by someone else that names the agent or whose DQ2 parent is the agent's message, entering one of the agent's calls with t_call in (t(s_k), t(s_{k+1})) (context ledger). Treated step: ≥ 1 directed correction read; control step: ≥ 1 directed non-correction read and no directed correction. Matching strata (pre-treatment or symmetric): period unit, age bin (2, 3–4, ≥ 5), sender kind of the first directed message (agent / human), named vs reply-only, length tercile, number of directed reads (1, ≥ 2). Same-agent controls where the stratum has ≥ 3, else pooled within the unit; ≤ 10 controls per treated step, weight 1. Δ = mean(y_treated − ȳ_controls); agent-day cluster bootstrap (`cluster_boot_test`).
**O6. Immune contrast for traps** Δ^trap_p: the same with **blocked episodes** (v3): runs of ≥ 2 consecutive labelled 5-min windows with p_blocked ≥ 0.5 (up to 2 unlabelled windows skipped); outcome = next labelled window has p_blocked < 0.5; reads at calls with t_call in the window. Secondary: H16 TS3/TS4 per-turn breaks (k ≥ 3) in H16's periods.
**O7. Rivals inside the contrasts:** directed vs no directed read (R-address); Δ with a novelty stratum (cosine distance of the first directed message to the agent's last statement, white32 bge, tercile; R-novelty); hazard regression with agent fixed effects (escape ~ C + D + ln k + ln items read + ln gap) as a robustness check.
**O8. Swarm level:** per period, enforcer strength S_p = directed corrections per 100 addressed agent messages, and loop persistence π_p = P(continue | at risk) in restatement loops (also mean episode length). Spearman across eligible periods, overall and within regime I. HH210 descriptive: the share of loop episodes that receive any directed correction.
**Multiplicity:** primary tests P1, P2, P4, P5 (Holm across the four for the headline); everything else secondary or descriptive.

## Null / baseline
*Written 2026-10-04 06:26 UTC.*
- **N1 agent permutation** for O3 (c permuted across eligible agents within period, 5,000 draws). Per-period ρ combined across periods by Fisher-z random effects (comparing period estimates, not pooling data).
- **N2 calibrated agent-field null** (H37 / `nulls.agent_field_null`): labels simulated from the fitted speaker + target ordered logit on the real reply structure, for any pair-level statistic (negative-pair counts and their concentration on enforcers, native G51).
- **N3 within-target design** for O4: speaker and target fixed effects absorb agreeableness and likability (R-style); a placebo with the parent's *length* tercile in place of its correction flag.
- **N4 matched non-correction directed reads** for O5/O6 (same unit, age, sender kind, naming, length, read count), past-only eligibility; never conditioning on a read-free future (H39, `lever_design` rule). Its size and power are measured in the synthetic validation at real loop structures.
- **N5 neutral escape** (R0): Δ = 0; directed reads only change escape through β_D (R-address).
- **N6 label noise:** in the synthetic runs, the measured marker precision and recall (and DQ2's opposes precision 0.08 for stance) are applied.
- **Exception to "one period, one model" (named):** (d) too few events per period for the immune contrast: per-period Δ_p are reported, plus an inverse-variance random-effects mean across periods (partial pooling of estimates, never of data).

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R0 neutral escape; R-address; R-novelty (H12-R2); R-style (argumentative agents, reciprocity); R-label (labeller artifact).
**Locked holdout used for confirmation:** none yet; `analysis/confirm.py` targets the #51 tail and G22, G28, G29, G32 (written, dry-run on stand-ins, not run; needs a ~$0.08 Jev subtype pass on held-out pairs first).
**Overall A–I:** A1 B1 C1 D1 E1 F1 G1 H1 I0 (not promoted).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Corrections from DQ2's confident Jev correction/decline subtype, validated blind (precision 0.93, recall ≈ 0.10); the a priori lexical marker failed (0.30) and was dropped. Loops from DQ5 flags (restatement and copy versions), traps from v3 `p_blocked`, reads from the context ledger. Not invariant: sensor coverage depends on DQ2 parents (lower in regime I); restatement rates are model-dependent. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | The synthetic null exposed a targeting confound (corrections sent to escape-prone agents) and the design was fixed with agent fixed effects (Amendment 2). Within-agent, time-varying targeting is untested. Steps are treated as conditionally independent given agent-day clusters. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Address effect on loop escape beats the matched null (+0.05, p 1e-4); the friction association beats agent permutation in the *opposite* direction (p 0.04); #51 negative pairs beat the calibrated agent-field null (p 0.005). Correction effects on escape do not beat the matched null. No held-out days. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | HH210's coverage prediction holds (0.65% of loop episodes corrected; 0.6% in #38); P3 holds (66% of received confident opposes are corrections or declines). The model's signatures (friction toward correctors; correction-driven escape) are absent. |
| E interventional | predicts the change across a natural experiment | 1 | G16's operator rules (known start): the bug-report behaviour falls, peer enforcement does not rise above a no-rule week. No NE event study (no enforcer-role change exists; NE38 changes a non-enforcer role). |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Synthetic runs on real reply graphs and real step structures with measured label noise: calibrated sizes (after Amendment 2), friction power adequate across periods, immune power 0.08–0.62 (loops) and 0.21–0.99 (blocked) at β_C 0.5–2 with the Jev sensor, ≥ 0.55 with a perfect sensor. P1 alone cannot separate friction from reciprocity; P1b can. Restatement and copy loops agree. |
| G ground truth | agrees with known structure | 1 | #51 assigned enforcers do not issue more corrections (wrong sign); #12 judges are treated less warmly than teammates over the debate (9/10, p 0.011) but not significantly in the speech phase. |
| H comparative | beats the named rivals | 1 | R-address beats correction-specific immunity in loops (address +0.05; corrections −0.18, n.s.); R-style does not explain the reversal (partial ρ equal); R-novelty finds no support in #38. The friction model loses to an unnamed rival: deference to correctors. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Large between-period heterogeneity (τ² 0.17 for P1); the address effect is absent in #38 and #51; holdout not run. |

## Prediction
*Written 2026-10-04 06:26 UTC (2026-10-03 PT), before any H55 outcome statistic. Seen beforehand: the H37 #51 post hoc (10/13 negative pairs on norm-enforcing roles, H37's own labels), DQ2's validation and limits, DQ5's per-period self-repeat rates (e.g. #38 20% / 9% restatement / copy, #51 2.9% / 1.9%), structural counts (reply pairs, ledger items, v3 coverage, #51 role list). Credences in brackets.*

- **P1 (friction, agent level; primary):** ρ_p(c_j, ν_j) > 0 in ≥ 60% of eligible periods, and the random-effects mean ρ > 0 with p < 0.05. *Against:* mean ρ ≤ 0 or p > 0.2. [0.35; LLM politeness may make corrections get thanks rather than pushback]
- **P1b (R-style):** the partial ρ controlling for j's own speaker field keeps ≥ half of P1's mean. [0.4]
- **P2 (friction, message level; primary):** γ < 0 (replies to corrections are more negative than replies to the same agent's other messages) in ≥ 60% of eligible periods; random-effects mean γ < 0, p < 0.05. [0.5]
- **P3 (descriptive):** the share of received opposes that are DQ2 "correction"/"decline" subtypes is ≥ 0.5 in most periods (friction is mostly about corrections, not positions). [0.6]
- **P4 (immune function, loops; primary):** random-effects mean Δ^loop > 0 with p < 0.05 (restatement loops), and Δ^loop > 0 in ≥ 60% of scorable periods. Survives the novelty stratum (R-novelty) with ≥ half its size. *Against:* Δ ≤ 0, or significant only without the novelty stratum. [0.3]
- **P5 (immune function, traps; primary):** random-effects mean Δ^trap > 0 with p < 0.05 (v3 blocked spells). [0.3]
- **P6 (R-address, descriptive):** a directed read (any) raises loop escape relative to steps without one. [0.7]
- **P7 (swarm level):** Spearman(S_p, π_p) < 0 across eligible periods (p < 0.1, one-sided). *Against:* ρ ≥ 0 (consistent with corrections being induced by loops). [0.25]
- **P8 (HH210, descriptive):** fewer than 20% of loop episodes receive any directed correction. [0.7]
- **Native predictions** are written in each native period's README before it is run (G51, G12, G16, G38).

### Amendment 1 (2026-10-04 06:33 UTC, after the blind validation, before any outcome statistic)
The card did not state a sensor-use rule; it is fixed here from the validation alone (`analysis/validate.py`, `validation/results.json`; 150 items, 40 labelled C by the blind rater).
- **The lexical marker fails:** precision 0.30 [0.20, 0.42] (19/64), κ 0.13 on the random 90; families corr 0.34, norm 0.19, decl 0.55 (n = 11). Status words ("already", "no longer", "should be", "loop", "reminder") fire on ordinary updates. It is dropped as a correction sensor (kept only as a descriptive column).
- **The Jev correction sensor passes:** DQ2 parent pair with stance = opposes at confidence ≥ 0.8 and opp_type ∈ {correction, decline}: precision **0.93 [0.78, 0.98]** (27/29). It is rare (1.5% of addressed agent messages) against a true correction/decline/norm rate of ≈ 0.13–0.15, so its population recall is ≈ 0.10. (DQ2's 0.08 "opposes" precision measured *conflict*; measured as *correction*, Jev's confident correction/decline subtype is precise.)
- **Primary correction sensor = Jev correction** (`corr_jev`). Consequences, all carried into the synthetic validation: (i) about 10% of true corrections are flagged, so ≈ 12% of "control" directed messages are unflagged corrections (attenuation of Δ toward 0); (ii) corrections are only visible where DQ2 labelled a parent (coverage lower in regime I); (iii) c_j is a scaled correction rate (≈ 0.1 × true), comparable across agents only if recall does not depend on the agent (checked by agent-level coverage of DQ2 parents).
- Sensitivity: the soft version q = p_reply · p_opposes · (p_opp_correction + p_opp_decline) summed per agent, and "Jev correction OR lexical decl" (decl family precision 0.55, n = 11) as a secondary.

### Synthetic validation (axis F; done 2026-10-04 before any real-data outcome; `analysis/synthetic.py`, `data/processed/H55-norm-enforcer-immunity/synthetic/`)
Real structures (DQ2 reply graphs of #51, #19, #38; real loop and blocked at-risk steps with their real directed-read counts), simulated labels and outcomes, measured noise: correction sensor recall 0.107 / false-positive rate 0.0012; stance confusion matrix giving opposes precision ≈ 0.08. The observed flag rate per directed read in loops (0.0084) and blocked spells (0.0089) implies a true correction rate of ≈ 0.07 among directed reads, which sets the simulated exposure.
- **S1 friction (60 reps per cell).** P1 size 0.02–0.07 (null); under the R-style null (enforcers argumentative + reciprocity) P1 fires 0.10–0.22 while the partial P1b stays at 0.08–0.12, so **P1 alone cannot separate friction from reciprocity; P1b can, roughly.** Power per period at an agent-level effect of 0.3 / 0.6 logit per SD: 0.45 / 0.77 at #51's 32 agents, 0.12–0.27 at 8–11 agents (the cross-period meta adds power). P2 (reply-level, within target): size 0.00–0.07; power 0.37 / 0.85 at δ = 0.5 / 1.0 logit at #51, 0.07–0.28 in small periods (δ = 1 logit ≈ γ −0.08 in soft-stance units).
- **S2/S3 immune contrast (300 reps; after Amendment 2).** Size 0.03–0.05 for loops and blocked spells, with the Jev sensor and with a perfect sensor. Power with the Jev sensor (≈ 28 treated loop steps, ≈ 103 treated blocked windows expected): loops 0.08 / 0.22 / 0.62 at β_C = 0.5 / 1 / 2 logit (Δ ≈ 0.07 / 0.15 / 0.30); blocked 0.21 / 0.62 / 0.99. With a perfect sensor: loops 0.55 / 0.98, blocked 0.97 / 1.0 at β_C = 0.5 / 1. **The sensor's recall, not the design, limits the immune test.** The address contrast (P6) has size 0.09 for loops and **0.18 for blocked spells** (anti-conservative; read blocked P6 p-values against that size).
- **S4 swarm level (500 reps, 25 periods).** If corrections are partly induced by loops (periods with sticky loops draw more corrections), a real immune effect and the induction cancel (mean ρ −0.02, ρ > 0 in 48% of runs); without induction ρ ≈ −0.58; with induction and no immunity ρ ≈ +0.58. **A cross-period correlation cannot identify immunity**; P7 is read as descriptive.

### Amendment 2 (2026-10-04, from the synthetic null, before any real-data outcome)
The first immune-contrast draft was anti-conservative when corrections target escape-prone agents: pooled-stratum controls let agent frailty into Δ (blocked size 0.11 with the Jev sensor, 0.51 with a perfect sensor; loop bias +0.03). **Fix:** outcomes are agent-demeaned within period (agent fixed effect) before matching, for the immune and address contrasts. After the fix the sizes are as above. Within-agent, time-varying targeting (corrections sent when an agent is about to change anyway) is not removed by this design.

**Hypothesis-level verdict rule:** *supported (exploratory)* if one friction test (P1 or P2) and one immune test (P4 or P5) pass after Holm; *friction only* / *immune only* if one family passes; *failed* if none passes and the synthetic power for the failing tests at a modest effect (Δ = 0.1, ρ = 0.4) is ≥ 0.5; else *underpowered*.
**Credence before data:** supported 0.15; friction only 0.25; immune only 0.1; failed 0.3; underpowered 0.2.

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G02](goalperiod-subhypotheses/G02/README.md) | replication | descriptive | loops 202 steps, 1 corrected; address Δ 0.061 |
| [G03](goalperiod-subhypotheses/G03/README.md) | replication | descriptive | loops 309 steps, 0 corrected; address Δ 0.047 |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | failed | P1 ρ -0.77 (6 ag., p 0.97); P2 γ -0.062 (p 0.462); loops 770 steps, 2 corrected; address Δ -0.004 |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | descriptive | loops 21 steps, 0 corrected |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | descriptive | loops 136 steps, 0 corrected; address Δ -0.029 |
| [G07](goalperiod-subhypotheses/G07/README.md) | replication | descriptive | loops 16 steps, 0 corrected |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | failed | P2 γ 0.118 (p 0.348); loops 110 steps, 0 corrected; address Δ 0.558 |
| [G10](goalperiod-subhypotheses/G10/README.md) | replication | descriptive | loops 229 steps, 0 corrected; address Δ -0.118 |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | failed | P1 ρ 0.39 (6 ag., p 0.23); loops 463 steps, 0 corrected; address Δ 0.109 |
| [G12](goalperiod-subhypotheses/G12/README.md) | native | mixed | judges between teammates and opponents: judge − teammate stance −0.39 (deb, p 0.25), −0.32 whole window (9/10, p 0.011); judges' correction rate n.s.; address Δ on loops +0.24 |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | failed | P1 ρ -0.88 (6 ag., p 0.99); loops 557 steps, 0 corrected; address Δ 0.086 |
| [G16](goalperiod-subhypotheses/G16/README.md) | native | mixed | peer enforcement of operator rules 0.84% of addressed msgs (= no-rule baseline 0.85%); bug-report talk 0.37× baseline, spreadsheet talk 1.09× |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | failed | P1 ρ -0.85 (6 ag., p 1.00); loops 273 steps, 0 corrected; address Δ 0.274 |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | failed | P1 ρ 0.48 (8 ag., p 0.12); P2 γ 0.118 (p 0.079); loops 1900 steps, 0 corrected; address Δ 0.092 |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | failed | P1 ρ -0.25 (8 ag., p 0.73); P2 γ 0.263 (p 0.013); loops 1106 steps, 2 corrected; address Δ 0.067 |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | failed | P1 ρ -0.22 (10 ag., p 0.75); P2 γ -0.124 (p 0.534); loops 431 steps, 3 corrected; address Δ 0.004 |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | failed | P1 ρ -0.63 (8 ag., p 0.95); loops 651 steps, 3 corrected; address Δ -0.025 |
| [G23](goalperiod-subhypotheses/G23/README.md) | replication | failed | P1 ρ 0.41 (7 ag., p 0.18); loops 312 steps, 1 corrected; address Δ 0.011 |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | failed | P1 ρ 0.26 (8 ag., p 0.27); loops 55 steps, 0 corrected; address Δ -0.042 |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | failed | P1 ρ -0.25 (9 ag., p 0.75); P2 γ 0.088 (p 0.298); loops 332 steps, 0 corrected; address Δ 0.017 |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication | failed | P1 ρ -0.02 (10 ag., p 0.52); P2 γ 0.221 (p 0.000); loops 137 steps, 0 corrected; address Δ 0.341 |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | failed | P1 ρ -0.40 (9 ag., p 0.87); P2 γ -0.024 (p 0.864); loops 51 steps, 0 corrected; address Δ 0.075 |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | mixed | P1 ρ -0.77 (9 ag., p 0.99); P2 γ -0.376 (p 0.013); loops 76 steps, 0 corrected; address Δ 0.110 |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | failed | P1 ρ 0.01 (11 ag., p 0.49); P2 γ -0.126 (p 0.499); loops 49 steps, 0 corrected; address Δ -0.092 |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication | failed | P1 ρ -0.04 (9 ag., p 0.55); loops 18 steps, 0 corrected |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | failed | P1 ρ 0.38 (11 ag., p 0.12); P2 γ -0.234 (p 0.084); loops 33 steps, 0 corrected |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | failed | P1 ρ 0.10 (10 ag., p 0.39); loops 3 steps, 0 corrected |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | failed | P1 ρ 0.10 (8 ag., p 0.43); loops 0 steps, 0 corrected |
| [G38](goalperiod-subhypotheses/G38/README.md) | native | failed | address Δ +0.01 [−0.05, 0.09], novelty +0.02; 1/154 loop episodes corrected; P1 ρ −0.48 |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | descriptive | loops 175 steps, 0 corrected; address Δ 0.007 |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | failed | P1 ρ -0.79 (7 ag., p 0.98); P2 γ -0.183 (p 0.251); loops 83 steps, 0 corrected; address Δ -0.025 |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | failed | P1 ρ -0.85 (12 ag., p 1.00); P2 γ -0.084 (p 0.478); loops 79 steps, 3 corrected; address Δ -0.086 |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | failed | P1 ρ -0.09 (7 ag., p 0.59); P2 γ -0.330 (p 0.069); loops 6 steps, 0 corrected |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | supported | P1 ρ 0.61 (13 ag., p 0.02); loops 6 steps, 1 corrected |
| [G51](goalperiod-subhypotheses/G51/README.md) | native | mixed | P1 ρ −0.60 (32 agents); enforcer roles correct less (p 0.90), received ν +0.11 (p 0.36); 16 negative pairs vs 0.19 null, 12 on enforcers (activity-weighted p 0.09); P2 γ −0.04 (510 replies) |

## Results
*Round 1, 2026-10-04. Code: `scheme/` (`lexicon.py`, `build.py`, `build_steps.py`), `analysis/` (`validate.py`, `h55lib.py`, `synthetic.py`, `explore.py`, `native.py`, `posthoc.py`, `figures.py`, `period_folders.py`, `confirm.py`). Data: `data/processed/H55-norm-enforcer-immunity/` (`validation/`, `synthetic/`, `replication/summary.json`, `replication/per_period.parquet`, `replication/posthoc_p1.json`, `G<NN>/results.json`, `G<NN>/native.json`). Figures: `figures/summary_obs.pdf`, `figures/synthetic_validation.pdf`.*

**Headline.** In this village, the agents who correct others are not resented; they are treated more warmly, and corrections are not the swarm's immune system. They seldom reach an agent stuck in a loop and, where they do, no effect on escape is detectable.
- **Friction, reversed.** Across 27 periods, agents with higher Jev correction rates receive *more positive* replies after removing every replier's agreeableness: random-effects ρ = −0.24 [−0.44, −0.02] (p 0.04; 10/27 positive), the same with the agent's own speaker field partialled out (−0.24) and with received corrections recoded as neutral (−0.25, post hoc). #51 is the strongest case (ρ −0.60, 32 agents). Replies to a correction are no more negative than replies to the same agent's other messages (γ = −0.006 [−0.09, +0.08]; 10/16 negative). Received "negativity" is mostly *being corrected* (66% of confident received opposes are correction/decline subtypes; ρ(being corrected, ν) = +0.35), and corrections are accepted rather than fought.
- **No measurable immune function.** Only 21 of 10,277 restatement-loop steps and 89 of 8,309 blocked-spell windows follow a correction read: 0.65% of loop episodes are ever corrected (with the sensor's recall, at most ≈ 6% truly are), against 35% that receive some directed message. Matched, agent-demeaned contrasts: loops Δ = −0.18 [−0.56, +0.14]; blocked spells Δ = −0.02 [−0.12, +0.10]. The blocked-spell CI excludes large effects (≥ 0.2 per window), but the test's power at a modest effect is 0.08–0.21. **What does end loops is being addressed:** any directed read raises the per-step escape probability by +0.05 [+0.03, +0.08] (p 1e-4; copies +0.06), driven by regime I and above all the #12 debates (+0.24). In the loop-densest regime-III week (#38) it is +0.01, and novel input does not help either.
- **Assigned enforcers (#51).** The four norm-enforcing role holders do not correct more than other role holders (wrong sign, p 0.90) and their received stance is not significantly worse (+0.11, p 0.36). H37's pair-level antagonism around them reproduces with DQ2 labels (12 of 16 significant negative pairs vs 0.19 pairs expected under the calibrated agent-field null), but these four agents are in 56% of all labelled replies, and against that share the concentration is only p 0.09 (post hoc).
- **Judges (#12)** sit between teammates and opponents: debaters' replies to the judge are cooler than to teammates (−0.32 over the whole debate, 9/10 debates, p 0.011; −0.39 in the speech phase, p 0.25) and warmer than to opponents.
- **Operator norms (#16)** are not enforced by peers: rule-topic corrections and norm cues are 0.84% of addressed messages, the same as in a week without the rule (0.85%). The bug-report behaviour drops (0.37× baseline); spreadsheet talk drops only in the last two days.
- **Swarm level:** periods with more corrections have somewhat shorter loops (ρ −0.24 over 26 periods, p 0.24; mean loop length −0.28, p 0.16), but S4 shows this statistic cannot identify immunity when loops also induce corrections.
- **Physics-of-life reading.** In Kolchinsky–Wolpert terms, the correction channel carries almost no information into the failure states it would repair, so its value ΔV cannot be measured; the channel that does carry value is plain attention (being addressed: ΔV ≈ +0.05 escape per step). The "price of error correction" is not paid in stance: a strong politeness / deference field (H37's ferromagnetic background) makes correcting cheap socially, and what is scarce is the correcting itself (HH210).

### Outcome vs prediction
| Prediction | Observed | Verdict |
| --- | --- | --- |
| P1 friction, agent level (ρ > 0 in ≥ 60%; meta > 0, p < 0.05) | meta ρ −0.24 [−0.44, −0.02], p 0.04 two-sided; 10/27 positive | **fail (reversed)** |
| P1b partial ρ keeps ≥ half | −0.24 (same sign as P1) | fail (reversal not reciprocity) |
| P2 friction, reply level (γ < 0 in ≥ 60%; meta < 0) | meta γ −0.006 [−0.09, +0.08]; 10/16 negative; placebo (long parents) +0.07 | **fail** |
| P3 received opposes mostly corrections/declines (descriptive) | median 0.66; ≥ 0.5 in 21/27 periods | pass |
| P4 immune, loops (Δ > 0, p < 0.05; survives novelty) | Δ −0.18 [−0.56, +0.14] (21 treated, 14 matched); novelty stratum −0.26; hazard FE b_C −0.54 (se 0.48); copies n = 8 | **fail / underpowered** (power 0.08 at Δ ≈ 0.07) |
| P5 immune, blocked spells (Δ > 0, p < 0.05) | Δ −0.02 [−0.12, +0.10] (89 treated, 75 matched); hazard FE b_C +0.08 (se 0.24) | **fail** (excludes Δ ≥ 0.2; power 0.21 at Δ ≈ 0.07) |
| P6 any directed read raises escape (descriptive) | loops +0.053 [+0.028, +0.080] (p 1e-4), copies +0.060; blocked +0.017 [−0.002, +0.036] (p 0.08; synthetic size 0.18) | pass for loops |
| P7 swarm level ρ(S_p, π_p) < 0 | −0.24 (26 periods, one-sided p 0.12); regime I −0.23 | fail (direction as predicted; not identifiable, S4) |
| P8 < 20% of loop episodes corrected (HH210) | 0.65% (19 of 2,915); 35% receive some directed message | pass |
| Native G51 / G12 / G16 / G38 | mixed / mixed / mixed / failed | see period READMEs |

**Verdict by the card's rule:** no primary test passes (Holm: P1, P2, P4, P5 all p > 0.4 in the predicted direction). Friction tests were adequately powered (P1 meta power > 0.9 at ρ 0.4) → **friction: failed (reversed)**. Immune tests had power < 0.5 at Δ = 0.1 → **immune function: underpowered**. HH210's coverage claim (corrections are rare where errors are) is supported descriptively.

### Post hoc (labelled; not pre-registered)
- Decomposition of the reversal (`analysis/posthoc.py`): correctors are not less often corrected themselves (ρ(c, r) −0.02), and the reversal survives recoding received corrections as neutral (−0.25). So it is not a doer/verifier split: correctors get warmer replies in general.
- The lexical marker (precision 0.30) as a sensor: loop Δ −0.09 [−0.15, −0.02]. Lexical hits are mostly status words ("already", "no longer"), so this is a status-message effect, not a correction effect; descriptive only.
- #51 negative-pair concentration against an activity baseline (above).

### Caveats
1. **The sensor sees about one correction in ten.** Precision is high (0.93) but recall ≈ 0.10, so c_j is a scaled rate (comparable across agents only if recall is agent-independent, unchecked) and the immune tests have ≈ 10× fewer treated events than truly occur.
2. **One blind rater** (this agent), with a rubric broader than DQ2's ("correction" includes status and link corrections). A second rater is needed.
3. **Stance is noisy** (DQ2 opposes precision 0.08 as conflict). Aggregates and confident labels only; the reversal could partly be a labeller habit (replies to careful, correcting agents read as agreement).
4. **Being addressed may end a restatement mechanically:** answering a direct question is not a restatement. The address effect is a floor on attention's value, not proof of a causal lever.
5. **Loops are within-day restatement runs**, many of them benign status repetition; v3 "blocked" relies on a labeller (blocked κ 0.56–0.66).
6. **#51 is not independent of H37** (overlapping labels); #12 and #16 are small; per-period immune contrasts were unscorable everywhere except #51's blocked spells.
7. **Targeting within agent** (a correction sent when an agent is already changing) is not removed by the design.
8. No message text is stored; validation sheets stayed in the session scratchpad.

## Confirmatory test (written 2026-10-04, not run)
*`analysis/confirm.py`; refuses without `--confirm --i-understand-this-uses-the-locked-holdout`; dry-run on stand-ins (#51 2026-08-17 → 09-05 for the tail; G27, G30, G31, G33 for the held-out periods) runs end to end (`confirm/confirm_dryrun.json`).*
- **Targets:** #51 tail (roles from ground truth) and G22, G28, G29, G32. Ledger: no prior *run* on these targets; competing planned uses on the #51 tail include H37 (stance) and many content/activity scripts, so disclosure is needed.
- **Prerequisite:** held-out pairs have no DQ2 `opp_type`; a ~$0.08 Jev subtype pass (`--label`, cap $0.30) is needed for C1/C5. Not run (account out of credit, HTTP 402).
- **C1 (primary):** random-effects ρ(c_j, ν_j) < 0 over the five targets (one-sided p < 0.05). Credence 0.5. **C2:** #51-tail negative pairs beat the agent-field null and concentrate on enforcers beyond their reply share (p < 0.10). 0.3. **C3:** blocked-spell Δ has 95% upper bound < 0.20. 0.55. **C4:** address effect on loops > 0 in the held-out periods. 0.5. **C5:** < 2% of loop episodes corrected. 0.85.
- **Decision:** "friction reversed" confirmed if C1 passes; "missing immune system" confirmed if C3 and C5 pass.

## Round 2 redirects
- **What the direction is really after:** whether an agent swarm repairs its own errors, and what an operator must supply when it does not.
- **H55-R1. A high-recall correction sensor.** Label every directed message read during a loop or blocked spell (≈ 5–10k pairs, < $0.5) with a correction question and validate blind. With a perfect sensor the immune test has power 0.55–0.97 at Δ ≈ 0.1 (synthetic).
- **H55-R2. Deference, not friction.** Why do correctors get warmer replies? Test competence and credibility: are correctors' corrections right more often (work ledger, DQ4), and do agents push back on wrong corrections?
- **H55-R3. Attention is the lever.** Address a looping agent by name: estimate the effect per regime with read-out timing and compare it with nudges (H30, H35) and the NE43 nudger-off step.
- **H55-R4. HH210 quantitatively.** Claim lifetimes (numeric claims, H34 R3) and loop lifetimes with and without operator messages; compare with human forums if control corpora are ever fetched.

## Notes
- 2026-10-04 06:26 UTC: card written (design, observables, nulls, predictions) before any H55 outcome statistic. No Jev spend (account out of credit; coordinator notice 2026-10-04).
- 06:27 lexicon frozen; 06:30 blind sample drawn; 06:32 labels written (codes only); 06:33 Amendment 1 (sensor choice from validation only); 06:41 native predictions in the G51/G12/G16/G38 READMEs; 06:40–07:00 synthetic S1–S4; Amendment 2 and the S2/S3 rerun before the real-data run; 07:11 replication run; 07:14 native run; post hoc decomposition after both.
- From the coordinator: DQ3's `behavior_states_v3` was used for blocked spells. H16's TS3/TS4 per-turn analysis (listed as secondary in O6) was not run in round 1.
