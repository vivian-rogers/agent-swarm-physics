# H37: Conflict lives in stance, not topic: stance spins are antiferromagnetic

**Status:** exploratory round 1 **done (2026-10-04): detector validated on assigned conflict; the generalization failed.** Zero-shot stance labels see the #12 debate teams that topic embeddings cannot (AUC 0.74 vs 0.48; teams recovered exactly in 7/10 debates), but find no stance antagonism between rival or opposed roles in #51 or between voting blocs in #26. Observables, nulls and predictions written 2026-10-04 01:35 UTC, before any stance label of an analysed pair was looked at or any outcome statistic computed. `analysis/confirm_g34.py` (#34 saboteurs) written and dry-run, **not run**.
**Round 1c (2026-10-04, stance v2.1, section below): verdict unchanged, now on validated disagreement.** On DQ2 ledger-visible replies with DQ10's validated flag (labeller noise built into the nulls), #12 opponents disagree in 33/74 replies and teammates in 0/60 (stress null p 0.001; topic AUC 0.48). #40 raises no false alarm (mixed → supported). #51 rivals and opposed roles show no excess disagreement (rivals excluded at +2 log-odds, opposed at +3; +1 inconclusive). #26 is untestable. The governance-friction lead does not replicate. A re-freeze of the #34 script on held-out v2.1 labels is proposed (needs sign-off).
**Fields:** stat mech, sociophysics, info theory
**Origin:** HH125 (`../hypohypotheses/HYPOHYPOTHESES.md`; `../promotion-shortlist.md`); leads from H22 (51a Prankster pairs), H21 (#12 stance tilt, HH127), H11 G26 (votes).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Population; Regime; Agent state, variant categorical (debate team, #51 role, #26 vote set). Two named variants of **Interaction**, proposed for the shared file: *interaction (addressed reply, 30 min)* and *interaction (adjacent reply, 5 min)* (defined under Data scheme). New terms defined below and proposed for the shared file: *stance spin*, *stance coupling*, *frustration index (ground-state)*. H22's *balance index τ₃* and its double-centred version τ₃(dc) are used exactly as H22 defined them (`../H22-private-goals-spin-glass/README.md`, O4 and Amendment 1).

## Standards (2026-10-04)
*Documentation pass against `STANDARDS.md`. No analysis was re-run. H37 has no round-1b section; every entry rests on round 1.*

**Question served:** Q3. The card tests for an antiferromagnet in stance and finds one only where a protocol assigns sides. Q2 second: the #12 stance order is set by the assignment, a field.

| Impostor | Relevant? | How it was handled | Status |
| --- | --- | --- | --- |
| Scheduler field | no | Reply-level stance labels; no activity or timing statistic. | n/a |
| Exogenous field (kickoff/goal/operator) | yes | The #12 contrast is read as assigned opposition, not emergent coupling (Headline). Agent fields and the politeness field are removed by two-way effects and the ordered-logit null (N3, Amendment 2). No `goal_fields` regression on the topic baseline. | partly |
| Shared model priors | yes | Same-lab residualization in the #51 role test (N6). Family writing-style invariance of the labels is not checked (axis A). Close with a cross-family label audit and `style_resid` topic cosines (§1, row 3). | partly |
| Contemporaneous convergence | partly | Not handled. An adjacent reply within 5 min may answer a message its author had not yet read. Close by keeping pairs whose A is in B's receiving-call context (ledger; §1, row 4). | open |

**Inputs:** round 1c (section below) moves to current inputs: DQ2 ledger-visible reply pairs, DQ10 `reply_stance_v2` (validated flag), DQ6 `ground_truth_labels` (#12 teams and phases, #51 roles per day, #26 ballots) and DQ2's `cos` as topic. Round-1 results below stay on round-1 inputs. Still old: reply pairs from `chat_mentions_clean` and room adjacency, not DQ2 replies or ledger visibility; topic cosine from bge only; #51 roles from H22's coding and #26 votes from H11, not DQ6 `ground_truth_labels` (Notes: one role was overwritten). Activity, work and failures are not inputs.

**Two layers:** none yet. Four period folders (G12, G26, G40, G51) run period-specific tests under role `exploratory`; no common replication estimator and no native folder.

**Confirm script:** `analysis/confirm_g34.py` exists, dry-run only. Round 1c proposes a re-freeze on held-out v2.1 labels (section "Proposed re-freeze"); it needs Vivian's sign-off, and the frozen script is untouched. It uses neither activity bins nor a visibility rule, so holdout.md item 8 does not force a re-freeze. Before any run: correct its reuse note (H05's #34 run was executed; holdout.md item 4) and take saboteur labels from DQ6 where they exist.

## Question
H22 found that in #51 rivals co-move in *topic* (content embeddings), so topic coupling cannot see conflict. Does conflict appear in *stance*, the sign of how one agent's reply treats another's message (agree / support vs oppose / undermine)? If so, a signed reply graph built from stance labels should carry negative couplings where conflict is (debate opponents in #12; opposed or rival roles in #51; electoral rivals in #26), and its frustration and balance should say whether conflict is factional (two camps) or diffuse. Practical aim (usefulness-first batch): a conflict and faction detector an operator can compute from chat logs with a cheap zero-shot labeller, with measured accuracy, and a saboteur-detection design for #34 (holdout, D8.3).

## Model
**From:** `physics-models/01-inverse-ising` (signed couplings, frustration, Mattis/balanced states) and `physics-models/10-potts` (communities as Potts ground states; q-faction generalization).

### The magnet dictionary (H37 variant)
| Magnet | Village | Dataset fields |
| --- | --- | --- |
| bond variable s_e ∈ [−1, 1] | the stance of one reply e: agent j's message B toward agent i's earlier message A | Jev probabilities: s_e = p(agree) + p(support) − p(oppose) − p(undermine); hard version σ_e ∈ {+1, 0, −1} |
| coupling J_ij | how i and j treat each other on average | mean of s_e over replies in both directions (n_ij ≥ 3) |
| agent fields a_j, b_i | j's agreeableness as a replier; how i is treated by everyone | two-way fixed effects (speaker, target), removed by double-centring |
| faction spin ξ_i ∈ {±1} (Potts σ_i ∈ 1..q) | which camp i is in | ground state of H(ξ) = −Σ_{i<j} J_ij ξ_i ξ_j (signed Potts for q > 2) |
| frustration | antagonisms that no two-camp split explains | unsatisfied |J| weight in the ground state |
| balance (Mattis) | conflict is factional: friends within camps, enemies across | τ₃ ≈ 0.5 (heterogeneous balanced) to 1 (uniform), τ₃(dc) ≈ 0.45 for factions, ≈ 0 for random signs |

**Generative model** (used for the synthetic validation and as the reading of the estimators): for reply e from j to i, a latent stance y_e = μ + a_j + b_i + Δ ξ_i ξ_j + ε_e, ε logistic; the observed class is − / 0 / + by two cut points (ordered logit). Then label noise through Jev's measured confusion matrix. Δ > 0 is a balanced (Mattis) antiferromagnet across camps; random-sign pair terms J_ij in place of Δ ξ_i ξ_j give a frustrated (SK-like) graph; Δ = 0 with heterogeneous a, b is the "agent field" null.

**Why stance is a bond, not a site variable.** In H21/H22 the spin was an agent's content vector, and conflict had to show up as anti-alignment of positions. Here the spin is the sign of an interaction itself, so the coupling is measured directly rather than inferred from co-movement. That removes H22's main confound (rivals share a niche and so co-move) but adds two others: agents' general agreeableness (an agent field on bonds) and LLM politeness (a uniform positive field).

## Data scheme (`scheme/`)
Shared tables only (`infra/README.md`): `chat_core`, `chat_mentions_clean` (o1-bug-free, `mentions_roster`), `chat_text` (in memory only, sent to Jev), `roster`, `embeddings/chat_bge_small` + per-regime whitener. H21's verified #12 team labels (`../H21-debate-antiferromagnet/scheme/labels/g12_debates.json`), H22's #51 role coding (`../H22-private-goals-spin-glass/scheme/role_relations.py`) and H11's #26 declared votes (`data/processed/H11-potts-labor-vs-herding/G26/votes.parquet`) are imported, never modified.

1. **`scheme/build_pairs.py`** → `data/processed/H37-stance-spins/pairs/G<NN>.parquet` (codes only). A reply pair (A → B): B an agent message, A an earlier agent message by a different agent in the same room.
   - **Interaction (addressed reply, 30 min):** B names agent i (`mentions_roster`, i ≠ speaker of B); A = i's latest message in B's room within 30 min before B.
   - **Interaction (adjacent reply, 5 min):** A = the latest message by any other agent in B's room within 5 min before B.
   - A pair found both ways is kept once (kind = both). Also stored: lag, and the **topic cosine** of A and B (bge-small, per-regime whitened, n = 32).
   - Counts (non-holdout): #12 7,002 pairs (2,763 inside debate windows); #26 4,889; #51 68,675 (36,515 mention/both); #40 2,828.
2. **`scheme/label_stance.py`**: Jev (`typesafe/jev-1.13` on OpenRouter; API pattern, model and key loader imported from `infra/behavior_states/label_windows.py`). Jev sees only the two messages (A ≤ 800 chars; B ≤ 1,000 chars around its first mention of A's author) and the two display names. No team, role, vote or period information. Questions: stance (agree / support / neutral / oppose / undermine) and responds (does B engage with A?). Stored: probabilities and codes only. Hard spend cap $2.00 (script cap $1.90, summed over all runs).
   - **What gets labelled:** all pairs of #12, #26 and #40; in #51 the mention/both pairs, capped at 40 per unordered agent pair per H22 unit (51a–51e), sampled at random (seed 20261004): ≈ 15.5k pairs. Adjacent pairs in #51 (20+ agents in a room) are too ambiguous to be worth the spend.
3. **Validation:** a blind sample of 60 pairs (stratified by period and kind) labelled by Claude without seeing Jev's answers; Cohen's κ on the sign (+ / 0 / −) and on the 5 classes, and the confusion matrix that feeds the synthetic noise model.

**Output:** `data/processed/H37-stance-spins/` (`pairs/`, `labels/`, `validation/`, `G<NN>/`, `synthetic/`), `_provenance.json`. No message text is written anywhere.

## Candidate goal periods
| Period | Role | Why |
| --- | --- | --- |
| #12 (2025-09-01 → 09-08, regime I, 7 agents, 1 room) | positive control | 10 debates with verified, re-drafted teams: the rules force cross-team disagreement |
| #51 non-holdout (07-06 → 09-04, regime III, 32 agents, 4 rooms) | main test | private roles, some opposed (Prankster × Ethicist / Psychologist) or rival (same role); H22 found rivals co-move in topic |
| #26 (2026-01-05 → 01-12, regime I, 10 agents, 1 room) | election | approval vote, three-way tie, runoff (H11 G26) |
| #40 (2026-05-04 → 05-08, regime III, 15 agents, 3 rooms) | false-alarm contrast | a shared-objective consensus week with no assigned conflict |
| #34 (🔒 holdout) | confirmation only | hidden saboteurs; `analysis/confirm_g34.py` written, not run |

## Observables
*Written 2026-10-04 01:35 UTC, before any real-data outcome. What I had seen: pair counts per period, kind, #51 role class and unit (sampling design); the #12 debate windows and team line-ups (H21's labels); H11's vote-declaration table structure; and the Jev answers for 4 smoke-test pairs from #40 (all "neutral"; no relation information).*

**O0. Stance labels and their accuracy.** Per pair: soft stance s_e and hard class. Validation: κ (sign and 5-class) against Claude's blind labels on 60 pairs; confusion matrix.

**O1. Relation contrast (reply level, agent-adjusted).** For a period with a relation label r_e per reply (same / opposite team; role class; vote similarity):
- γ̂ from OLS s_e = μ + a_speaker + b_target + γ · 1[r_e = same] + ε over replies with r ∈ {same, opposite} (two-way fixed effects absorb agreeableness and likability).
- Also the raw means s̄(same), s̄(opposite) and the negative share f_neg (hard class oppose or undermine).
- Null: relation-label permutation within the structural unit (N1), 5,000 draws.

**O2. Topic contrast on the same pairs ("beyond topic").** The same γ̂ with the topic cosine as the outcome; AUC of agent-adjusted stance vs agent-adjusted topic cosine for telling same from opposite; and γ̂(stance) with topic cosine as a covariate.

**O3. Signed graph.** J_ij = mean s_e over replies between i and j (both directions; n_ij ≥ 3; missing = 0 in traces).
- Negative-pair share p_neg; pairs significantly negative after removing agent fields (BH-FDR 0.1, per-pair t on double-centred reply residuals).
- **Frustration index (ground-state):** f_gs = fraction of |J| weight unsatisfied by the best two-camp split (exact enumeration for N ≤ 20, else 200-restart descent; `h22lib.gs_frustration`), against the sign-shuffle null; triangle frustration F against the same null.
- **Balance:** τ₃ and τ₃(dc) (H22), cross-fitted on three folds (day folds where a unit has ≥ 6 days, else folds of whole conversations: replies grouped by B's 10-min block), day/block bootstrap CI.

**O4. Faction recovery.** ξ̂ = ground state of the double-centred J. #12: per debate, debaters only, accuracy against the true teams (up to a global flip); chance from all balanced partitions of that debate's line-up. #26: ARI against vote blocs (descriptive). The same on the **topic graph** (mean topic cosine per pair, double-centred).

**O5. #51 role treatment.** `h22lib.treatment_test` on J^stance (pair rule n_ij ≥ 3 replies): T_OP, T_SR, T_SY, T_NC = class mean − U mean, raw and same-lab-adjusted, role permutation among role holders (5,000). The same on J^topic (mean topic cosine per pair, the same replies). Pooled over non-holdout #51 (roles per agent = majority role over its present days), and per counted H22 unit (51b, 51c, 51d) as robustness.

**O6. Operator-facing detector metrics** (computed identically in every period): conflict level f_neg; count of significantly negative pairs (O3); faction score = best-split satisfied weight vs the sign-shuffle null; per-agent "received" and "given" residual stance z-scores (saboteur / scapegoat flags at z < −2).

**O7 (HH127, secondary).** #12: γ̂ in the post-verdict window vs during the debate.

**Multiplicity.** Seven primary tests (P1, P2, P3, P6, P7, P10, P12 below); Holm across them for the headline. Everything else is descriptive.

## Null / baseline
*Written 2026-10-04 01:35 UTC, before any real-data run.*
- **N1 relation permutation:** team labels re-drawn within each debate (sizes and judge fixed); #51 roles permuted among role holders (multiplicities fixed); #26 vote sets permuted among voters.
- **N2 sign shuffle:** magnitudes kept, signs permuted across pairs (frustration, faction score).
- **N3 agent fields:** two-way fixed effects (speaker agreeableness, target likability) or double-centring. Conflict must survive them: an argumentative agent is not a faction.
- **N4 topic:** stance must separate relations where topic cosine does not, and survive topic cosine as a covariate.
- **N5 label noise:** the synthetic runs give the detection floor and the false-positive rate at Jev's measured accuracy.
- **N6 family:** same-lab residualization (as H22); family style is the dominant content field (H13).
- **Uniform politeness field:** LLM replies lean positive, which shifts every J up (ferromagnetic τ₃). Absolute negativity (s̄ < 0) and relative negativity (after double-centring) are reported separately.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** topic coupling (H22: conflict invisible, rivals co-move); agent fields only (agreeable vs argumentative agents, no pair structure); uniform politeness field (everyone agrees); frustrated random antagonism (SK-like signs) vs balanced factions (Mattis).
**Locked holdout used for confirmation:** none yet. `analysis/confirm_g34.py` targets #34 (written, dry-run on #33 and #26 stand-ins, not run). #34 is already targeted by the unrun confirm scripts of H01, H05, H07, H12, H19 and H21: H37's observable (Jev stance labels on reply pairs) is a different modality that nobody has computed on #34, and H37 shares H21's saboteur ground-truth rule (a label, not an observable). Disclosure needed in H21's card and LOG.md (see the round-1 report).
**Overall A–I:** A1 B1 C1 D1 E1 F1 G1 H1 I0 (not promoted).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Reply pairs from clean mentions and adjacency; stance from a zero-shot labeller validated against blind labels (κ_sign 0.67 random sample; 0.37 enriched; 0.56 population-reweighted). Jev's negative calls are only 30% precise. Invariance across model families of writing style (e.g. procedural "I will wait" messages) not checked. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Assumption audit found that agent fields are not additive on ordinal labels, which makes the sign-shuffle faction null and the per-pair FDR anti-conservative (S6); replaced by a parametric ordered-logit agent-field null (Amendment 2; size 0.04 at #40's structure). Reply independence assumed within pairs; stationarity within debates assumed. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | #12: beats within-debate team permutation, agent fields and topic (p = 0.0002). #51: negative pairs beat the calibrated agent-field null (10 vs 0.33, p = 0.005), camps do not. #26 and #40: nothing beyond the nulls. No held-out days. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | Per-debate team recovery from the stance graph (unfitted): 0.89, exact in 7/10; balance below the sign-shuffle null; post-verdict relaxation predicted (P5). Role-class predictions in #51 (P6, P7, P9) and the ballot prediction in #26 (P10) failed. |
| E interventional | predicts the change across a natural experiment | 1 | The verdict is a dated switch inside #12: the predicted drop of the team contrast after it is observed (γ̂ 0.42 → 0.03). No village-level NE tested. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Synthetic at the real reply graphs with measured label noise (S1–S6): team contrast detectable from Δ ≈ 0.5 logit; camps recovered with accuracy 0.91–1.0 at ±0.5 logit; τ₃(dc) separates camps from random signs at #51 size but is unstable on real residual graphs. Robust to pair construction, relevance filter and hard vs soft labels. One labeller, one validation rater. |
| G ground truth | agrees with known structure | 1 | #12 verified teams recovered (2 for this period). Assigned rivalries and oppositions in #51 and ballots in #26 are not visible in stance (0 for those). |
| H comparative | beats the named rivals | 1 | Beats the topic-coupling rival and the agent-field rival in #12. In #51 the homophily rival wins: rivals are friendlier in stance as well as closer in topic. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Does not transfer from the debate to roles (#51) or the election (#26); #34 not run. |

## Prediction
*Written 2026-10-04 01:35 UTC (2026-10-03 PT), before running the analysis on real data. Credences in brackets.*

**#12, positive control** (replies with B inside a debate's speech window [first speech, verdict) and both authors among that debate's debaters):
- **P1 (assigned conflict is negative in stance):** s̄(opposite) < 0 < s̄(same), and γ̂ > 0 with N1 p < 0.01. *Against:* γ̂ ≤ 0 or p > 0.05, i.e. the labeller cannot see forced disagreement. [0.85]
- **P2 (beyond topic):** AUC_stance(same vs opposite) ≥ 0.65 while AUC_topic ∈ [0.40, 0.60]; γ̂(stance) keeps p < 0.01 with topic cosine as covariate. *Against:* topic separates the teams as well as stance does. [0.7]
- **P3 (faction recovery):** the ground state of each debate's double-centred stance graph recovers the teams with mean accuracy ≥ 0.80 over debates, above random balanced partitions (p < 0.05); the topic graph does not (p > 0.05). [0.55]
- **P4 (balance, descriptive):** pooled debate graphs have f_gs below the sign-shuffle null. [0.6]
- **P5 (HH127, descriptive):** γ̂(post-verdict) < γ̂(debate). [0.6; a sign flip 0.3]

**#51, unassigned conflict:**
- **P6 (opposed objectives):** T_OP(stance) < 0, role-permutation p_less < 0.05, same-lab-adjusted. [0.3; 2 role pairs, low power]
- **P7 (rivals: stance vs topic dissociation):** T_SR(stance) < 0 with p_less < 0.05, while T_SR(topic) on the same pairs is ≥ 0 (H22's direction). *Against:* T_SR(stance) ≥ 0, i.e. rivals are not antagonistic in stance either. [0.2]
- **P8 (descriptive prior):** the graph is ferromagnetic overall: f_neg < 0.10 of replies, raw τ₃ > 0.5. [0.8]
- **P9 (descriptive):** significantly negative pairs (O3) are enriched in OP ∪ SR ∪ NC pairs (odds ratio ≥ 2, Fisher p < 0.05). [0.2]

**#26, election:**
- **P10 (stance tracks votes):** J^stance correlates with voters' vote-set similarity (Jaccard of their declared candidate sets; Mantel test with agent permutation, r > 0, p < 0.05), and more strongly than J^topic does. [0.3]
- **P11 (descriptive):** pairs of rival candidates (each named by ≥ 2 distinct voters in first-person declarations) have lower stance than other pairs (N1 p < 0.05). [0.25]

**#40, false-alarm contrast:**
- **P12 (no false alarm):** f_neg(#40) ≤ ½ f_neg(#12 opposite-team pairs); at most one significantly negative pair (FDR 0.1); faction score not significant (p > 0.05). [0.7]

**Hypothesis-level verdict rule:**
- **Supported (exploratory):** P1 and P2 pass (stance sees assigned conflict beyond topic), *and* at least one of P6, P7, P10 passes (stance finds conflict nobody assigned).
- **Detector validated, generalization not shown:** P1 and P2 pass, none of P6, P7, P10.
- **Failed:** P1 fails: zero-shot stance cannot even see forced debate disagreement.

**My credence before data:** supported 0.25; detector validated only 0.5; failed 0.15; other 0.1.

### Amendment 1 (2026-10-04 01:39 UTC, before any outcome statistic; from reading the 60 blind validation pairs, before Jev labelled them)
1. **Debater-adjacent pairs for #12.** In the 20 debate-window validation pairs the adjacent "reply" of a speech is usually the judge's call to speak, and most debate-window messages are procedural ("I will wait for …"). Added `scheme/build_debate_pairs.py`: for each message B by a debater inside a debate window, A = the latest message by a *different debater of the same debate* (judge and bench excluded; teams not used) within 10 min. 883 such pairs already existed; 207 are new (`pairs/G12_debater.parquet`). P1–P3 use the union of all #12 pair kinds, as before; a debater-adjacent-only variant is reported as robustness.
2. **Enriched second validation sample.** My random 60 contain only 2 negatives (2 oppose, 15 agree/support, 43 neutral), too few to estimate accuracy on the class the hypothesis is about. After Jev runs, I will label a second blind set of 45 pairs drawn equally from Jev's negative, positive and neutral predictions, shuffled so that I do not know any item's stratum. Per-class precision comes from it directly; recall and κ are reweighted by the strata's population shares. Both sets are reported.
3. **Relevance filter.** Primary analyses use pairs with Jev's responds probability ≥ 0.5 (as written); all-pairs results are reported alongside.

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G12](goalperiod-subhypotheses/G12/README.md) | exploratory (positive control) | supported | debate replies: stance same +0.32 vs opposite −0.13, γ̂ 0.42 (p 0.0002); AUC 0.74 (stance) vs 0.48 (topic); team recovery 0.89, exact 7/10 (topic 0.71, chance 0.70); contrast gone after the verdict (γ̂ 0.03) |
| [G51](goalperiod-subhypotheses/G51/README.md) | exploratory | failed | T_SR(stance) +0.085 (p_less 0.81; topic +0.078), T_OP +0.02 (2 pairs, both positive); 10 negative pairs vs 0.33 expected (calibrated p 0.005), none in conflict classes; camps not beyond agent fields (p 0.36); post hoc: 10/13 negative pairs involve norm-enforcing roles |
| [G26](goalperiod-subhypotheses/G26/README.md) | exploratory | failed | stance vs ballot similarity r = 0.01 (p 0.47; power 0.25–0.42 at 1–2 logit); rival-candidate test untestable; no negative pairs, no camps (p 0.91) |
| [G12](goalperiod-subhypotheses/G12/README.md) round 1c | exploratory (positive control) | supported (validated flag) | flags 0/60 within vs 33/74 across; γ_f 0.40 (stress p 0.001); topic AUC 0.48; camps 0.81 (p 0.001); 0 flags in 90 post-verdict replies |
| [G51](goalperiod-subhypotheses/G51/README.md) round 1c | exploratory | failed (rivals excluded ≥ +2, opposed ≥ +3 log-odds) | SR 6/400 flags, β +0.46 [−1.46, 1.37], p 0.33; OP 0/55, β −2.0; 3 excess pairs (null 0.8), 1 in a conflict class; 0/3 norm-enforcing; NC 14/299 (post hoc, one pair) |
| [G26](goalperiod-subhypotheses/G26/README.md) round 1c | exploratory | n/a (untestable) | 7 flags; Mantel r −0.30 (p 0.95); power 0.05 at +1 log-odds |
| [G40](goalperiod-subhypotheses/G40/README.md) round 1c | exploratory (contrast) | supported (no false alarm) | true disagreement rate 0.042 [0, 0.078] = 0.05× #12 opponents; 0 excess pairs |
| [G40](goalperiod-subhypotheses/G40/README.md) | exploratory (contrast) | mixed | no negative pairs, no camps (calibrated p 0.73): no structural false alarm; but 20% of replies labelled "oppose" (task corrections plus label noise), so P12's conflict-level clause fails |

## Results
*Round 1, 2026-10-04. Code: `scheme/` (pairs, labels, samples), `analysis/explore.py` (per period), `analysis/validate.py`, `analysis/synthetic.py`, `analysis/calibrate.py`, `analysis/figures.py`, `analysis/confirm_g34.py`. Data: `data/processed/H37-stance-spins/` (`summary.json`, `G<NN>/results.json`, `validation/`, `synthetic/results.json`, `calibration*.json`). Figures: `figures/summary.pdf` (one-page figure summary), `figures/summary_obs.pdf`, `figures/summary_obsb.pdf`, and `goalperiod-subhypotheses/G*/figures/`.*

**Headline.** Stance labels are a working sensor for *assigned, explicit* conflict and a poor one for anything else in this village.
- In the #12 debates, reply stance separates opponents from teammates (AUC 0.74 after agent effects) while the same reply pairs are equally similar in topic (cosine 0.53 vs 0.54; AUC 0.48). The best two-camp split of each debate's stance graph recovers the drafted teams exactly in 7 of 10 debates; the three misses are the three smallest debates (29–49 replies). The contrast switches off within 10 min of the verdict.
- Where nobody assigned sides, the swarm shows almost no stance conflict. Same-role rivals in #51 are, if anything, friendlier than unrelated pairs (and closer in topic, as H22 found); the Prankster is on good terms with the Ethicist and the Psychologist; #26 voters' stance does not track their ballots.
- The negativity that exists is diffuse: #51 has 10 agent pairs more negative than agent fields predict (0.33 expected), none in a conflict-coded role pair. Post hoc, 10 of 13 involve a norm-enforcing role: governance friction, not rivalry.
- In the HH125 terms: stance couplings are antiferromagnetic exactly where a protocol forces opposition, and nowhere else. "Conflict lives in stance" holds for debates; in the rest of the village there is little conflict to live anywhere.

### Outcome vs prediction
| Prediction | Observed | Verdict |
| --- | --- | --- |
| P1 #12 opponents negative, teammates positive, γ̂ > 0 (p < 0.01) | +0.32 vs −0.13; γ̂ 0.42, p 0.0002 (Holm 0.0006) | **pass** |
| P2 #12 beyond topic: AUC_stance ≥ 0.65, AUC_topic in [0.40, 0.60], survives topic covariate | 0.74 vs 0.48; p 0.0002 with covariate | **pass** |
| P3 #12 camp recovery ≥ 0.80 (p < 0.05), topic graph not | 0.89 (p < 10⁻⁴), exact 7/10; topic 0.71 (p 0.46) | **pass** |
| P4 #12 balance (descriptive) | unsatisfied weight 0.08 vs sign-shuffle 0.14 (p 0.0015) | pass |
| P5 #12 contrast drops after the verdict (descriptive) | γ̂ 0.42 → 0.03; opponents' stance −0.13 → +0.36 | pass (relaxation; no flip, so HH127's remanence is not seen in stance) |
| P6 #51 T_OP(stance) < 0 | +0.02 (p_less 0.55; 2 pairs) | fail |
| P7 #51 T_SR(stance) < 0 while topic ≥ 0 | stance +0.085 (p_less 0.81), topic +0.078 | fail (homophily rival) |
| P8 #51 ferromagnetic overall (descriptive) | f_neg 0.091, τ₃ 0.75 | pass |
| P9 #51 negative pairs enriched in conflict classes | 0 of 13 (Fisher p 1) | fail |
| P10 #26 stance tracks ballots | r 0.01 (p 0.47) | fail (low power) |
| P11 #26 rival candidates lower (descriptive) | untestable: every agent was a candidate | n/a |
| P12 #40 no false alarm | no negative pairs, no camps; f_neg 0.20 > ½ × 0.26 | mixed (fails on f_neg) |

**Verdict by the card's rule:** P1 and P2 pass; none of P6, P7, P10 pass → **detector validated, generalization not shown.** Holm-adjusted primary p: P1 0.0006, P2 0.0006, P3 0.0003, P6 1, P7 1, P10 1.

### Label validation (O0)
- Blind Claude labels, written before seeing Jev's answers: a random 60 (stratified by period) and an enriched 45 (15 each from Jev's −/0/+ calls, strata hidden while labelling).
- Random 60: κ_sign 0.67 (agreement 0.83), 5-class κ 0.58; responds κ 0.47. Enriched 45: κ_sign 0.37.
- Precision of Jev's calls: negative 0.30 (6/20), neutral 0.96, positive 0.65. Jev labels 8.9% of replies negative; the blind labels put the true rate near 5%. Many Jev "opposes" are task corrections, polite declines or status contradictions.
- Population-reweighted P(Jev | true): recall 0.56 (−), 0.73 (0), 0.89 (+); κ_sign 0.56. This matrix is the synthetic noise model. The label-noise floor (Jev "negative" rate with no true negatives) is ≈ 0.065.

### Synthetic validation (axis F; real reply graphs, measured label noise)
- **S1 (#12):** the team contrast test has size 0.005 and power 0.90 at Δ = 0.5 logit (0.28 at 0.25; 1.0 at 1.0); camp recovery 0.79 / 0.88 at Δ = 0.5 / 1.0 (chance 0.70). The real #12 values (γ̂ 0.42, recovery 0.89) correspond to Δ ≈ 1 logit or more.
- **S2 (#51 roles):** with Jev noise, power for T_SR is 0.53 at a pair term of −1 logit and 0.95 at −2; T_OP (2 pairs) 0.05 / 0.40. So P7's failure excludes strong rival antagonism (≥ 1–2 logit), not weak; and the observed T_SR is positive.
- **S3 (balance):** τ₃(dc) separates two-camp from random-sign couplings at #51 size (0.74 vs 0.0; 25% misclassification of random signs at Δ = 0.5 with Jev noise). On real residual graphs it was unstable (#51 CI −0.9 to 29; negative at #26's N = 10), so it is reported, not used.
- **S4 (#26 ballots):** Mantel power 0.25 / 0.42 / 0.83 at 1 / 2 / 4 logit.
- **S5 (saboteur design):** per-agent-day suspicion AUC 0.81 if saboteurs receive −1 logit stance, 0.81 if they give −1 logit (combined score 0.71 for one channel only, 0.89 for both); null 0.50.
- **S6 (detector false alarms):** with the sign-shuffle null, the camp test fires in 10% (#12, #26), 28% (#40) and **100%** (#51) of agent-field-only simulations; ≥ 1 "significant" negative pair in 0–63%. Both nulls are invalid on residual stance graphs → Amendment 2.

### Amendment 2 (2026-10-04, post hoc, after S6 and after the first real-data run; disclosed)
The detector's camp and negative-pair statistics are compared with a **parametric agent-field null**: an ordered logit with speaker and target effects fitted to each period's hard labels, simulated 200 times on the real reply structure (`analysis/calibrate.py`). Its own size and power at #40's structure: size 0.04 (camps) and 0.00 (pairs); power 1.0 for two camps at ±0.5 logit; 0.12 / 0.08 for three isolated antagonistic pairs at −1 logit. At #51's structure: size 0.04 (camps) and 0.00 (pairs); power 1.0 for camps at ±0.5 logit; 0.08 / 0.08 for three isolated antagonistic pairs (`calibration_check.json`; 25 null and 12 camp datasets, 40 bootstrap replicates each). Calibrated results: #12 whole period camps p 0.01, 2 negative pairs vs 0.03 expected; #26 p 0.91, 0 pairs; #40 p 0.73, 0 pairs; #51 camps p 0.36, 10 pairs vs 0.33 (p 0.005). The pre-registered sign-shuffle values are kept in the G folders.

### Operator-facing detector (round-1 spec)
1. **Reply pairs** from chat logs: addressed replies (B names A's author within 30 min) plus adjacent replies (5 min; exclude moderator or judge calls where known).
2. **Stance** with a zero-shot labeller (Jev stance-v1; $0.037 per 1,000 pairs; 30k pairs labelled for $1.12). Keep pairs the labeller says respond (p ≥ 0.5); soft stance s = p(agree) + p(support) − p(oppose) − p(undermine).
3. **Agent fields**: fit an ordered logit with speaker and target effects; work with residual pair stance J_ij.
4. **Alarms**, each against the parametric agent-field null (alarm above its 95th percentile):
   - *antagonistic pairs*: pairs whose residual stance is significantly negative; report the count against the null count;
   - *factions*: the ground-state two-camp split of the residual graph and its satisfied-weight score; report the split;
   - *scapegoat / aggressor*: agents with received or given residual stance z < −2.
5. **Never alarm on the raw negative share alone**: subtract the label-noise floor (≈ 0.065) and read it as correction friction unless the structural alarms agree.

**Measured accuracy.** On ground truth (#12): per-reply team relation AUC 0.74; per-debate camp recovery 0.89, exact for every debate with ≥ 82 replies (7/7). Synthetic, at real reply graphs with measured label noise: camp power ≈ 1.0 at ±0.5 logit with calibrated size 0.04; camp accuracy 0.91–1.0. Real cooperative weeks (#26, #40): no structural false alarm. Weak spots: Jev's negative calls (precision 0.30) and isolated antagonistic pairs (power ≈ 0.1 for three −1-logit pairs at #40's and #51's sizes).

### Caveats
1. **One labeller, one rater.** κ is moderate, and my blind labels define "truth"; a second human or model rater is needed. Jev over-calls "oppose" on corrections.
2. **Debate speeches address teams, not people.** Many debate rebuttals name no opponent and follow the judge's call, so the reply graph undersamples the real exchange (Amendment 1 partly fixes this).
3. **Small graphs.** N = 7–14 outside #51; balance indices are unstable there, and the per-pair tests needed calibration.
4. **Power.** #51's role tests rest on 6 rival and 2 opposed pairs; #26 has 10 agents. Failures exclude strong effects only.
5. **Post hoc.** The governance-friction reading of #51's negative pairs (OR 4.4, p 0.016) and Amendment 2 came after the data.
6. **Topic baseline** is one embedding model (bge-small, whitened); H21 used masked text for #12.
7. No message text was stored; only codes and probabilities. Agent narration was not used as ground truth (labels are about how B treats A, not what B claims).

## Confirmatory test (#34, written 2026-10-04, not run)
*`analysis/confirm_g34.py`; refuses to run without `--confirm --i-understand-this-uses-the-locked-holdout`; dry-run on non-holdout stand-ins (#33 label rule; #26 detection with seeded stand-in saboteurs: null AUC 0.50, planted −0.1 / −0.3 soft stance → AUC 0.77 / 0.96).*
- **Pairs and labels:** the same two constructions and Jev prompt on #34 (≈ 9k pairs, own cap $0.50).
- **Ground truth:** H21's self-identification rule (agent's own intentions or chat; ambiguous days dropped); untestable if < 4 saboteur agent-days.
- **C1 (primary):** suspicion from *received* stance (agent-day target effect, z within day) has AUC ≥ 0.60 with within-day permutation p < 0.05. Credence 0.25.
- **C2:** suspicion from *given* stance, AUC > 0.5, p < 0.05. Credence 0.15. **C3:** combined AUC ≥ 0.60. Credence 0.25. **C4 (descriptive):** saboteurs in the daily minority camp.
- **Decision:** supported if C1 passes; failed if AUC < 0.55 or p > 0.20; else mixed.
- **Reuse policy:** different modality from every earlier #34 script; commit before running; disclose in H21's card and LOG.md.

## Round 1c (stance v2.1, 2026-10-04)
*Re-test of round 1 with the validated conflict flag of DQ10 (`infra/data-quality/stance_v2.md`). Round 1 used H37's own Jev stance-v1 labels, whose "oppose" was 30% precise (6/20 on the enriched sheet) and mixed task corrections, declines and status contradictions with conflict. DQ10 found the same for DQ2's `opposes`: only 12% dispute A on the merits. Round 1c asks whether the round-1 pattern (assigned conflict seen; no conflict elsewhere) holds for disagreement on the merits.*

### Pre-registration (written 2026-10-04 22:10 UTC, before any round-1c statistic)
**Seen before writing.**
- Round 1 results (above); H21 rounds 1 and 1b; DQ10's validation (all rounds).
- Marginal flag counts per goal period (`disagree_validated_agent`): #12 44 of 1,325 pairs; #26 8 of 1,037; #40 17 of 616; #51 202 of 24,143 (non-holdout). No count split by team, role, ballot or pair.
- Structural counts of #12 debater-to-debater pairs (debate phase 134; 60 within team, 74 across; post 90).
- DQ10 per-stratum flag precision: #12 stratum 10/10 flagged pairs were reference `disagree`.
- DQ6 #51 role labels (role names per agent), to code pair classes. No stance statistic by class.

**What changes from round 1.**
- **Pairs:** DQ2 candidate pairs (ledger visibility, p_reply ≥ 0.5, agent parents, B ≠ A, non-holdout), the v2 population, instead of H37's mention/adjacency pairs. This also closes the round-1 "old inputs" gap.
- **Stance:** the flag `disagree_validated_agent` (primary). Secondary, unvalidated, aggregate only: `s2_soft` and `p_disagree`.
- **Ground truth:** DQ6 `ground_truth_labels` for #12 teams and phases, #51 roles (per day; corrects the overwritten Claude Opus 5 role, Notes) and #26 ballots. Pair classes follow H22's coding rule (SR, OP, SY, NC, U), re-implemented in H37's own code, not imported.
- **Topic:** the DQ2 pair feature `cos` (bge-small cosine of A and B).

**Label-noise model (built into every null).** Identical to H21's round 1c (`analysis/labelnoise.py`):
- True disagreement d_e is flagged with probability R (recall), a non-disagreement with probability φ: P(f = 1) = φ + (R − φ)·π_e.
- K = 40 draws of precision ~ Beta(mean 0.64, sd 0.065) and R ~ Beta(mean 0.60, sd 0.08); φ = q(1 − PPV)/(1 − qPPV/R) with q = 0.0106.
- **Noise-aware agent-field model:** logit π_e = μ + a_speaker + b_target + Σ_k β_k x_k (relation or role-class indicators, same-lab covariate in #51), fitted through the noise map (L2 0.1 on fields). β̂ are true-scale log-odds.
- **Noise-aware agent-field null:** β = 0, fitted to the observed flags, simulated on the real reply structure. It replaces round 1's ordered-logit null for flags.
- **Label-confusion stress null:** false-positive rate per group proportional to its share of Jev `correct` + `inform` labels.
- Rogan–Gladen corrected rates per group. Sensitivity: #12-specific noise (precision Beta(11, 1), recall 0.9).

**Synthetic validation first** (`analysis/r1c_synthetic.py`). On the real reply structures of #12 (debate phase) and #51 (role holders), simulate null worlds (agent fields only; plus differential false positives) and planted worlds: #12 opponents Δ = 0.7, 1.5, 2.5 log-odds; #51 rivals (SR) and opposed roles (OP) at +1, +2 log-odds. Report expected observed rates, test size, power and the bias of β̂. Tests with size > 0.08 are replaced by their stress-null version before the real run.

**Predictions (credences in brackets).**
- **P1c (#12, re-tests P1).** Agent-adjusted contrast γ_f (two-way fixed-effects linear probability of the flag, opposite minus same team, debate phase) > 0, team-permutation p < 0.01, above the noise-aware agent-field null's 95th percentile; β̂_opp > 0 with interval excluding 0. [0.75]
- **P2c (#12, re-tests P2).** γ_f keeps p < 0.01 with topic cosine as a covariate, and topic cosine does not separate the teams (agent-adjusted AUC in [0.40, 0.60]). [0.7]
- **P3c (#12, re-tests P3).** Camp recovery from the per-debate flag graph: mean accuracy ≥ 0.80 above random balanced partitions (p < 0.05). [0.4] Secondary on `s2_soft`. [0.65]
- **P5c (#12, re-tests P5).** γ_f(post-verdict) < γ_f(debate). [0.7]
- **P6c (#51 opposed roles, re-tests P6).** β̂_OP > 0 (more disagreement), role-permutation p < 0.05. [0.15]
- **P7c (#51 rivals, re-tests P7).** β̂_SR > 0, role-permutation p < 0.05. [0.15]
- **P9c (#51, re-tests P9).** Pairs with excess disagreement (≥ 2 flagged replies on ≥ 2 distinct days, upper-tail p < 0.01 under the noise-aware agent-field model) are enriched in SR ∪ OP ∪ NC (odds ratio ≥ 2, Fisher p < 0.05). [0.15] Descriptive: the round-1 governance-friction lead (norm-enforcing roles), read with H55's activity caveat.
- **P10c (#26, re-tests P10).** Pair disagreement rises with ballot dissimilarity (Mantel r > 0, p < 0.05). [0.15] Untestable if the synthetic power at +1 log-odds per unit dissimilarity is < 0.3.
- **P12c (#40, re-tests P12).** The noise-corrected disagreement rate in #40 is ≤ ½ of the #12 opposite-team rate, and no excess-disagreement pair beyond the null. [0.8] Round 1 failed the rate clause on correction friction; the validated flag should not.

**Kill rules.**
- **K1.** P1c fails: the round-1 detector claim ("stance sees assigned conflict") is withdrawn for disagreement on the merits and rescoped to pushback (corrections, declines).
- **K2.** The stress null's expected #12 contrast is ≥ half the observed: P1c is not separable from label confusion.
- **K3.** The generalization claim changes only on a pass: any of P6c, P7c, P10c passing reverses "generalization failed". If none pass, the failure is called *powered* only where the synthetic power at +1 log-odds (true scale) is ≥ 0.8; otherwise *inconclusive at +1, excluded at the largest effect with power ≥ 0.8*.

**Verdict rule (unchanged in form).** Supported: P1c and P2c, and at least one of P6c, P7c, P10c. Detector validated, generalization not shown: P1c and P2c, none of the three. Failed: P1c fails. Holm across the primary tests (P1c, P2c, P3c, P6c, P7c, P10c).

**Code and outputs.** `analysis/labelnoise.py`, `analysis/r1c_synthetic.py`, `analysis/r1c.py`, `analysis/r1c_estimates.py`; outputs in `data/processed/H37-stance-spins/r1c/`. Round-1 code is unchanged, so round 1 reproduces.

### Synthetic validation, #12 part, and Amendment 1c-1 (2026-10-04 22:23 UTC, before the real #12 run)
`r1c/synthetic.json`; 100 worlds per row on the real #12 structure (134 debate-phase debater pairs; 74 across, 60 within; 7 agents; 10 debates).

| World | Expected observed flag rate, same / opposite | Team permutation p < 0.05 (< 0.01) | Noise-aware null p < 0.05 (< 0.01) | Stress null p < 0.05 (< 0.01) | β̂ median; CI coverage; CI excludes 0 |
| --- | --- | --- | --- | --- | --- |
| null, fields sd 0.5 | 3.2% / 3.7% | **0.09** (0.02) | 0.06 (0.00) | 0.05 (0.00) | 0.30; 0.80; 0.09 |
| null, fields sd 1.0 | 5.6% / 4.9% | 0.06 (0.02) | 0.05 (0.00) | 0.04 (0.00) | −0.17; 0.84; 0.04 |
| null, false positives ×2 across | 3.0% / 2.8% | **0.12** (0.04) | 0.05 (0.00) | 0.03 (0.00) | −0.01; 0.74; 0.05 |
| null, false positives ×4 across | 3.2% / 3.8% | **0.11** (0.04) | 0.05 (0.00) | 0.03 (0.00) | 0.04; 0.81; 0.07 |
| AF Δ = 0.7 (true 5.3% / 9.8%) | 3.7% / 6.4% | 0.18 (0.07) | 0.16 (0.03) | 0.14 (0.01) | 0.74; 0.84; 0.16 |
| AF Δ = 1.5 (true 4.7% / 17%) | 3.3% / 9.9% | 0.34 (0.21) | 0.35 (0.14) | 0.36 (0.09) | 1.50; 0.77; 0.44 |
| AF Δ = 2.5 (true 5.5% / 35%) | 3.7% / 21.7% | 0.88 (0.64) | 0.85 (0.59) | 0.87 (0.50) | 2.68; 0.75; 0.87 |

**Amendment 1c-1 (pre-specified rule: size > 0.08 → stress-null version).**
- The FE linear-probability team permutation is liberal (size 0.09–0.12). **P1c's decision now uses the stress-null p < 0.01** in its place, plus the noise-aware null's 95th percentile. **P2c's topic-covariate test likewise uses its stress-null p** (same simulated flag sets, γ refitted with topic cosine).
- **β̂'s interval under-covers** (0.74–0.84); its clause is dropped from P1c. β̂ is reported as an estimate.
- **Power at p < 0.01 is about 0.5 at Δ = 2.5 and about 0.1 at Δ = 1.5.** A P1c failure would exclude only very strong assigned conflict.
- The #51 and #26 parts follow below, before their real runs.

### Synthetic validation, #51 and #26 parts (2026-10-04 22:27 UTC, before the real #51, #26 and #40 runs)
**#51 structure (role holders, non-holdout):** 23,670 replies among 32 agents. Class rows: U 15,434; SY 7,482; SR 400; NC 299; OP 55. Thirty worlds per row; agent fields sd 0.7; true base rate 1.2%; role permutation 300.

| World (true log-odds vs U) | Expected observed flag rate U / SR / OP | Role-permutation power p < 0.05, SR / OP | Noise-aware β̂ median, SR / OP |
| --- | --- | --- | --- |
| null | 1.7% / 1.5% / 1.8% | 0.00 / 0.00 | 0.01 / 0.06 |
| SR +1 | 1.7% / 3.7% / 1.3% | 0.37 / 0.00 | 0.99 / — |
| SR +2 | 1.6% / 8.2% / 1.0% | **1.00** / 0.03 | 2.07 / — |
| OP +1 | 1.5% / 1.5% / 3.9% | 0.03 / 0.20 | — / 1.30 |
| OP +2 | 1.6% / 1.7% / 6.7% | 0.00 / 0.57 | — / 1.93 |
| OP +3 | 1.5% / 1.5% / 15.5% | 0.00 / **0.97** | — / 3.03 |

**#26 (9 voters, 937 replies):** Mantel power 0.05 / 0.18 / 0.71 at +1 / +2 / +4 log-odds per unit of ballot dissimilarity (size 0.035; 200 worlds).

**Consequences (pre-registered rules, no new choices).**
- The role-permutation tests are conservative (size 0.00 in 30 null worlds) and the true-scale β̂ is close to unbiased.
- **K3 thresholds:** power at +1 log-odds is 0.37 (SR) and 0.20 (OP), below 0.8. A failure of P7c is therefore "inconclusive at +1, excluded at +2". A failure of P6c is "inconclusive at +1 and +2, excluded at +3".
- **P10c is untestable:** power at +1 is 0.05, below the registered 0.3. It is still computed and reported as descriptive.

### Results (2026-10-04, `analysis/r1c.py`; data `r1c/r1c.json`)
**What changed under the result.** Both the pairs (DQ2 ledger-visible replies in place of H37's mention/adjacency pairs) and the labels (validated v2.1 flag in place of stance-v1) are new. Round 1's numbers are kept above.

**#12: the detector still sees assigned conflict, now as disagreement on the merits.**
- 33 of 74 opposite-team debate replies are flagged, and 0 of 60 same-team replies. Agent-adjusted γ_f = 0.40.
- γ_f beats the stress null (expected 0.011; p 0.001), the noise-aware agent-field null (95th percentile 0.13; p 0.001) and team re-draw (p 10⁻⁴). The #12-specific noise gives the same p.
- Topic does not separate the teams (agent-adjusted AUC 0.48), and γ_f keeps its size with topic as a covariate (0.39; stress p 0.001).
- The flag graph recovers the camps with mean accuracy 0.81 (chance 0.66; p 0.001; exact 4/10). This is just over the 0.80 line; round 1's stance-v1 graph had 0.89.
- After the verdict: 0 flags in 90 post-window replies.
- Opposite-team true disagreement rate ≈ 0.75 (population noise). β̂_opp sits at the separation bound (no teammate flag) and is not used.

**#51: no excess disagreement between rivals or opposed roles.** 23,670 replies among 32 role holders; 201 flags (0.85%).
- **Opposed roles (P6c):** 0 flags in 55 replies (2 pairs). LP β −0.012 (role permutation p_upper 0.75). True-scale β −2.0 [−3.4, −0.6]: if anything, *less* disagreement.
- **Same-role rivals (P7c):** 6 flags in 400 replies (1.5%; unrelated pairs 1.0%), all in 2 of the 6 rival pairs. LP β +0.0035 (p 0.33). True-scale β +0.46 [−1.46, 1.37].
- **Support roles (SY):** less disagreement than unrelated pairs (true-scale β −1.4 [−3.4, −0.3]).
- **Topic (round-1 P7 clause):** rivals are not closer in topic on these pairs (β +0.005, p 0.25).
- **Excess-disagreement pairs (P9c):** 3, against 0.8 under the noise-aware null (p 0.05). One is in a conflict class (NC); Fisher p 0.21, so **fail**. None involves a norm-enforcing role (41% of tested pairs do), so **the round-1 governance-friction lead does not replicate** with the validated flag.
- **Post hoc (not pre-registered as a primary): media-niche competitors (NC)** carry more flags: 14 of 299 replies (4.7%), role permutation p 0.006, stress p 0.04. But 8 of the 14 come from one pair on 2 days, and only 5 of 19 NC pairs have any flag. It is a lead, not a result.

**#26: untestable.** 7 flags among 937 voter-to-voter replies. Mantel r = −0.30 (p_greater 0.95); power at +1 log-odds is 0.05.

**#40: no false alarm (P12c passes).** True disagreement rate 0.042 [0, 0.078] (17 flags in 599 replies), 0.05× [0, 0.14] the #12 opposite-team rate. No excess-disagreement pair (null mean 0.07). Round 1 failed the rate clause because 20% of #40 replies were labelled "oppose". DQ2 calls 23% of these replies "opposes"; the validated flag calls 2.8%.

**Old vs new.**

| Prediction | Round 1 (stance-v1, H37 pairs) | Round 1c (validated flag, DQ2 pairs) | Verdict 1 → 1c |
| --- | --- | --- | --- |
| P1 #12 assigned conflict | +0.32 vs −0.13; γ̂ 0.42 (p 0.0002) | flags 0/60 vs 33/74; γ_f 0.40; stress p 0.001 | pass → **pass** |
| P2 #12 beyond topic | AUC 0.74 vs topic 0.48 | topic-covariate γ_f 0.39 (stress p 0.001); topic AUC 0.48 | pass → **pass** |
| P3 #12 camps | 0.89; exact 7/10 | 0.81 (p 0.001); exact 4/10 | pass → **pass** (at the line) |
| P5 #12 after the verdict | γ̂ 0.42 → 0.03 | 0 flags in 90 replies | pass → **pass** |
| P6 #51 opposed roles | T_OP +0.02 (2 pairs) | 0/55 replies; β −2.0 [−3.4, −0.6] | fail → **fail** (excluded at ≥ +3 log-odds) |
| P7 #51 rivals | T_SR +0.085 (homophily) | 6/400 vs 1.0% baseline; β +0.46 [−1.46, 1.37]; p 0.33 | fail → **fail** (inconclusive at +1, excluded at +2) |
| P9 #51 negative pairs in conflict classes | 0 of 13; post hoc 10/13 norm-enforcing | 1 of 3 (NC); Fisher p 0.21; 0/3 norm-enforcing | fail → **fail**; governance lead not replicated |
| P10 #26 ballots | r 0.01 (p 0.47) | r −0.30 (p 0.95); 7 flags | fail → **untestable** (power 0.05) |
| P12 #40 false alarm | no pairs; f_neg 0.20 > ½ × 0.26 (mixed) | true rate 0.05× #12 opponents; 0 excess pairs | mixed → **pass** |

**Holm** (P1c, P2c, P3c, P6c, P7c, P10c): 0.006, 0.006, 0.006, 1, 0.99, 1.

**Verdict by the card's rule:** P1c and P2c pass, and none of P6c, P7c, P10c does. The verdict is unchanged: **detector validated, generalization not shown.**

**Which verdicts change.**
- **G40: mixed → supported.** The rate clause failed in round 1 only because the labeller counted correction friction as conflict.
- **G26: failed → untestable** for round 1c. Too few flags; the round-1 failure was also low-powered.
- **G12 and G51 stay supported and failed.** G12 now rests on disagreement on the merits. In G51 the failure now has a stated reach (rivals ≥ +2, opposed ≥ +3 log-odds excluded) and loses the governance-friction lead.
- **Operator spec:** the validated flag replaces stance-v1's "oppose". The "subtract the 0.065 noise floor" rule is replaced by the Rogan–Gladen correction with precision ≈ 0.64 and recall ≈ 0.6.

**Scorecard (1c notes, for the v2 rater).**
- A: the label is validated (precision 0.61–0.67; #12 stratum 10/10); the pairs use ledger visibility; DQ6 roles. Family invariance of the label is still unchecked.
- C: unchanged. The #12 contrast beats a stress null built from the labeller's confusion; nothing elsewhere beats its null.
- F: the synthetic now uses the validated noise on the real structures, with power tables for every test.
- I: still 0 (#34 not run).

**Estimates:** 11 rows in `per_period_estimates`, status "round 1c, stance v2.1".

### Proposed re-freeze of `confirm_g34.py` (needs Vivian's sign-off; the frozen script is not edited)
The frozen #34 script labels new #34 pairs with stance-v1 (negative precision 0.30) through the Jev API. Round 1c shows the validated v2.1 flag carries assigned conflict cleanly. Held-out v2.1 labels for the locked holdout already exist (`data/processed/holdout_labels/reply_stance_v2_holdout.parquet`, prepared by DQ10; no statistic computed; not opened here). Proposal for a new frozen script (`confirm_g34_v2.py`), to be written and dry-run only after sign-off:
1. **Pairs and labels:** #34 DQ2 candidate pairs (`pair_set = cand`, p_reply ≥ 0.5) joined to the held-out v2.1 labels. Flag = `stance2 == "disagree"` and `stance2_conf ≥ 0.6`, agent parents (`a_kind = 0`). No API call, no spend.
2. **Primary (C1-v2):** suspicion from *received* disagreement. This is the agent-day target effect of the noise-aware agent-field logistic, z-scored within day. AUC (saboteur > villager) against a within-day label permutation. The decision thresholds are unchanged (supported if AUC ≥ 0.60 and p < 0.05; failed if AUC < 0.55 or p > 0.20).
3. **Secondary:** given disagreement (C2-v2); received `s2_soft` (unvalidated, aggregate); the stance-v1 primary is dropped.
4. **Ground truth:** H21's self-identification rule as frozen, or DQ6 saboteur labels where they exist (checked at freeze time).
5. **Before freezing:** a synthetic power check on the #33 and #26 stand-in structures, with planted received disagreement at +1 and +2 log-odds. At the village flag rate (≈ 1%), #34 may hold too few flags. If the power at +2 is below 0.5, the test should stay on stance-v1 or be dropped, not re-frozen.
6. **Disclosure:** this is the first read of the held-out v2.1 labels for #34. Holdout ledger and LOG.md entries are needed.

**Claim that stands:** A validated zero-shot disagreement flag on reply pairs separates assigned debate opponents from teammates in #12 (33/74 vs 0/60 replies; beyond a stress null built from the labeller's confusion, p 0.001; topic AUC 0.48). It stays quiet in a consensus week (#40: true rate 0.05× the debate rate, no excess pair), and rival and opposed roles in #51 show no excess disagreement (rivals +0.46 log-odds [−1.5, 1.4]; opposed roles 0 of 55 replies). Excluded: generalization beyond assigned conflict (inconclusive at +1 log-odds; excluded at +2 for rivals and +3 for opposed roles); #26 ballots (untestable, power 0.05); the media-niche excess (post hoc, one pair); the governance-friction lead (not replicated).

## Round 2 redirects
- **What the direction is really after:** a cheap, calibrated sensor for adversarial or factional behaviour in agent swarms, and its detection limits.
- **H37-R1. A second labeller and rater.** Relabel the validation sets with another model and a human; report inter-labeller κ and whether the #12 result survives.
- **H37-R2. Find conflict where it might exist.** Run the calibrated detector on periods with contested decisions or vote-outs (#19, #31, #13) and on the #51 tail (holdout, with pre-registration), testing the governance-friction lead (negative pairs concentrate on norm-enforcing roles).
- **H37-R3. Kinetic stance.** Does a negative reply beget a negative reply (reciprocity, escalation)? A Hawkes or kinetic-Ising model on signed reply events, with the verdict and goal changes as interventions.
- **H37-R4. Run the #34 confirmation** after sign-off, as the saboteur test (D8.3).

## Notes
- **From H55 (2026-10-04):** the #51 norm-enforcer antagonism concentration is largely activity: the four enforcers are in 56% of all replies, and against that share the concentration is only p 0.09. Correctors get warmer, not colder, replies across 27 periods (ρ −0.24).
- **From DQ6 (2026-10-04):** `agent_goals` overwrote Claude Opus 5's first #51 role (game dev, 07-24 → 07-29, then Mathematician at NE38), so this card treated it as roleless for those days. That adds two rival pairs. Use `ground_truth_labels` (`preferred`) in the re-evaluation.
- 2026-10-04: promoted from HH125 by Vivian (usefulness-first batch); wave 2.
- 2026-10-04 01:35 UTC: data scheme, observables, nulls and predictions written before any real-data outcome (pair counts and 4 smoke-test labels from #40 seen; disclosed above).
- 2026-10-04 01:39 UTC: Amendment 1 (debater-adjacent pairs; enriched validation set). 01:40–02:00 UTC: Jev labelled 30,461 pairs ($1.116, 0 errors). 01:53 UTC: per-period predictions in the G folders.
- 2026-10-04: validation (blind labels before Jev answers), synthetic S1–S5, then the real-data run; S6 and Amendment 2 (calibrated null) after the first real-data run; `confirm_g34.py` written and dry-run, not run.
- The rubric changed to a two-page summary during the run; `summary/` follows the two-page version.
