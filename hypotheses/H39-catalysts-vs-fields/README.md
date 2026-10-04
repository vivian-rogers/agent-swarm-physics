# H39: Catalysts vs. fields

**Status:** exploratory round 1 done (2026-10-04, UTC; 32 non-holdout goal periods for point levers, 26 kickoffs, 10 scaffold steps, 2 room steps, 1 post hoc step). Design, observables, nulls and predictions P1–P8 were written before any real-data statistic; synthetic validation (axis F) came first. **Headline:** no lever is a pure catalyst. **Nudges are both:** they raise idle escape ×1.4–1.6 and also lower the stationary idle share (G51 −0.07), with catalytic fraction ρ ≈ 0.5; HH52's "catalyst, π unchanged" is rejected per episode. **Human messages are fields:** in regime I they move agents from chat to computer work; in G51 they move content toward the message but not behavior. **@-mentions steer content, not behavior** (no behavior effect in the best-powered periods). **Forced context erasure** is an anti-catalytic field toward work (idle share down in 8/8 regime-III periods). **Goal kickoffs** tilt content only in regime III. Scaffold steps are mostly undetectable. Confirmatory script written and dry-run on stand-ins; **not run**.
**Fields:** stat mech, sociophysics, info theory
**Origin:** HH52 (`../hypohypotheses/HYPOHYPOTHESES.md`; `../promotion-shortlist.md`); related HH116 (operator susceptibility, H30), HH124 (nudger as Maxwell demon, H35), HH53 (traps, H16).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime; Action; Agent state (categorical: action class), in H14's coarse scheme ("Action (turn-merged)" records, minute grid); Agent state (vector): the agent's 30-min embedding vector (`embeddings/agent_win30`); Interaction (broadcast) for room messages and Interaction (addressed) for mentions; Driving / external field (goals, human messages, nudges). New named terms proposed for DEFINITIONS.md (owner to add): **"field effect (occupancy shift)"**, **"catalytic effect (escape at fixed occupancy)"**, **"lever episode"** (defined below).

## Question
Some interventions lower activation barriers without changing which states are favored: *catalysts* (the nudger, human helpers, the sign-in hand-off). Others tilt the landscape: *fields* (goals, prompt changes). Catalysts change rates but not stationary occupancies; fields change occupancies. *Check:* across the nudger switching on (NE10) and off/on (NE23), compare escape rates from idle states with the stationary idle fraction.

Practical aim (usefulness-first batch): a lever taxonomy an operator can compute from logs: "to change what agents do, use X; to unstick them, use Y".

## Model
**From:** `physics-models/02-nonequilibrium-ising` (kinetic rules, fields vs. rates, detailed balance) and `10-potts` (kinetic Potts = categorical Markov chain); `09` (point-process kicks) for the kick timing.

**H39 variant: a kinetic Potts / Markov-jump agent with Arrhenius rates.** Each agent occupies one of q behavior states. Transition rates

  k_ij = ν exp[−(B_ij − G_i)/T],  B_ij = B_ji (barrier on edge ij), G_i (well depth of state i),

satisfy detailed balance with π_i ∝ exp(−G_i/T). Any change of rates splits uniquely into a time-symmetric part s_ij = ½(δ ln k_ij + δ ln k_ji) (kinetic: barrier, "frenesy") and a time-antisymmetric part a_ij = ½(δ ln k_ij − δ ln k_ji) (thermodynamic: tilt).
- **Field** (h): a_ij = (h_j − h_i)/2, s_ij = 0. Occupancies shift, π_i ∝ π_i⁰ e^{h_i}. At fixed occupancy the total escape rate changes only through net probability currents (zero at detailed balance, to first order).
- **Catalyst** (c): s_ij = c_ij > 0 (barriers lowered), a_ij = 0. Occupancies unchanged under detailed balance; everything moves faster. A uniform catalyst is a pure rescaling of time.
- **Escape-only kick** (raise the exit rates of one state, e.g. idle): half field, half catalyst in this decomposition. It shifts occupancy *and* raises traffic.
- **Caveats built into the design.** (i) The split depends on the load-distribution convention; a heat-bath (destination-only) field leaks into the traffic measure. The synthetic validation quantifies both conventions. (ii) Away from detailed balance (H14: the scaffold's consolidation step carries the coarse arrow of time) a symmetric change can shift occupancies ("blowtorch" effect). (iii) The village is non-Markov at minute scale (H17) and traps age (H16), so rates are compared only between matched windows (same agent, same start state, same dwell age), never extrapolated from a fitted generator.

## Data scheme (`scheme/`)
Shared tables only (`data/processed/shared/`; Known issues in `infra/README.md` respected: `chat_mentions_clean`, bookends dropped from `automated`, trimmed minute grid).
- **Behavior states (primary): H14's builder is imported, not copied** (`hypotheses/H14-behavior-entropy-production/scheme/build_states.py: build(days)`), run on non-holdout days and frozen as H39's own copy. Primary lumping **B4** = {work (browse, type, shell), chat, idle, consolidate}; robustness **B6** = H14's six coarse states. 1-min active-time grid; present agent-days only (≥ 10 records); **each agent-day is trimmed to [first, last] record minute** (H17 Known issue: pre-first / post-last idle minutes are not behavior).
- **Content states:** `embeddings/agent_win30` vectors (agent × 30-min window). (a) **C6 clusters:** k-means, k = 6, on regime-whitened (`common.load_whitener`, 32-d), unit-normalized vectors, fitted per analysis unit (seed 0). (b) **Directed content vectors:** the raw 384-d vector, unit-normalized, and the kick message's own embedding (`chat_bge_small`). Message text is never read or stored.
- **Kicks: H16's class mapping is imported** (`h16lib.load_kicks`; exposure-based recipients, `chat_mentions_clean.mentions_roster`): N_tgt = nudge naming the agent; H_men / H_und = human message naming / not naming the agent; A_men = agent message naming the agent. H04's nudge rule is the same (automated + valid mention; bookends dropped).
- **Erasures (NE41):** H15's `consolidations.parquet` (kind CF = forced at the 41-turn cap, CV = voluntary), read only.
- **Output:** `data/processed/H39-catalysts-vs-fields/`: `states_b6.parquet` (frozen H14 states, B4 derived on the fly), `kicks.parquet` (message-level kicks with embedding rows, no text), `erasures.parquet` (H15 CF/CV events), per-period `G<NN>/results.json` + `boot_draws.npz`, `steps/` (kickoffs, rooms, scaffold, P9), `synthetic/`, `confirm_dryrun/`, `summary.json`; `_provenance.json`. Budget ≤ 200 MB (used: see Notes).

## Lever classes and designs
| Class | Lever | Design | Unit |
| --- | --- | --- | --- |
| nudges | N_tgt episodes | point-kick matched windows | per goal period |
| human messages | H_men, H_und episodes (also pooled H_any) | point-kick matched windows | per goal period |
| @-mentions | A_men episodes | point-kick matched windows | per goal period |
| context erasure (NE41) | CF events (CV as comparison) | point-kick matched windows | per regime-III goal period |
| goal kickoffs (NE34) | period boundary | step: last 2 days vs first 2 days, placebo = within-goal day boundaries | transition (exception c), `NE34/` |
| room changes | NE42 merge 05-04 and split 05-11; NE15 split 03-16 | step, against the regime-III kickoff and day-boundary placebos | `NE42/`, `NE15/` |
| scaffold changes | NE10 (nudger on, 02-13), NE07 (12-04), NE16 (03-26), NE17 (04-14), NE18 (04-20), NE03 (08-20), NE06 (11-20); unnumbered CHANGELOG prompt steps 2025-08-01 (#8), 2025-10-22 (#18), 2026-05-28 (#44) | step within a goal period, placebo = within-goal day boundaries | numbered: `NE<NN>/`; unnumbered: in the period's `G<NN>/` |

**Lever episode (point kicks).** The first kick of class c to agent a after ≥ 30 min with no directed or human kick to a (N_tgt, H_men, H_und, A_men), with no kick of another class in the same minute. The window is minutes m_k+1 … m_k+W of the agent's trimmed day, **W = 30 min** (H04: response plateaus by ~15 min; sensitivity W = 15, 60). Erasure episodes: a CF (or CV) consolidation event with no kick or other consolidation in the 10 min before; s0 = the last non-consolidate state in the 10 min before; controls ≥ 10 min after the agent's last consolidation; both arms cut at the next kick or consolidation.

**Matched controls (placebo times).** For each episode, 10 minutes (drawn with replacement) of the same agent in the same period, in the same stratum: start state s0 (B4) × dwell age of the current run {1, 2–4, 5–14, ≥ 15 min} × other agents' activity level {< ⅓, ⅓–⅔, > ⅔ in work or chat} × day third; no directed/human kick in the 30 min before (past only); window inside the trimmed day. Fallbacks: drop day third, then pool agents (same period, s0, age, swarm level). Each episode's controls weigh 1 in total. **Both arms are cut at the next directed/human kick** for the transition statistics (the hazard after exactly one kick vs none); the transient occupancy O4 uses uncut windows in both arms (kick now vs not now). *Design amended 2026-10-04 after the synthetic null (see Synthetic validation): the first draft required a kick-free future window and 15 quiet minutes.* Episode quiet period: 30 min (≥ W, so no lingering effect of an earlier kick).

## Observables
All on B4 unless stated; per unit (period × class, or step).
- **Kicked and control transition matrices** T^K, T^C: lag-1 minute transitions inside the windows, shrunk by one pseudo-transition per row distributed as the unit's pooled T.
- **O1 field effect (occupancy shift).** π^K = stationary(T^K), π^C = stationary(T^C). Signed Δπ_s for each state; TV distance D_F; and the **field index** φ = π^C-weighted standard deviation of δ ln π_s (units of T, i.e. the RMS change in well depth). Bias-corrected φ_exc = √max(φ² − median φ²_placebo, 0).
- **O2 catalytic effect (escape at fixed occupancy).** K = ln[Σ_s π^C_s e^K_s / Σ_s π^C_s e^C_s], e_s = 1 − T_ss (escape probability per minute), i.e. the change in total traffic with occupancies held at the control values. Per-state escape log-ratios ln(e^K_s/e^C_s). Companion: κ_sym = control-traffic-weighted mean of s_ij.
- **O3 catalytic fraction** ρ = |K| / (|K| + φ_exc): 0 = pure field, 1 = pure catalyst.
- **O4 transient occupancy shift** Δocc_s: occupancy over the window, kicked minus matched. Descriptive only: a pure catalyst acting on agents that start out stuck lowers the transient idle share, so Δocc looks like a field even when π does not move (the "transient fallacy"; quantified synthetically).
- **O5 content, steps:** O1–O3 on C6 clusters (lag = one 30-min window).
- **O6 content, point kicks (drift vs. diffusion).** pre = the agent's vector in the window before the kick window, post = the window after; u = the kick message vector. Displacement d = post − pre splits into the component along the unit vector (u − pre)/|u − pre| (drift: **field toward the message**) and the perpendicular remainder (diffusion: **content catalysis**). Field_c = mean d_∥ (kicked) − mean d_∥ (controls given the same u); Cat_c = ln[mean |d_⊥|² kicked / mean |d_⊥|² controls]. Controls: window triples of the same agent with no directed/human kick in them.
- **O7 HH52 check (NE10, and nudges in every nudger-on period):** ln(e^K_idle / e^C_idle) against Δπ_idle.

## Null / baseline
- **N1 placebo episodes (primary):** pseudo-episodes drawn from control-eligible minutes with the real episodes' stratum mix, each with its own matched controls; 200 draws. Gives the bias floor for φ and D_F (TV is positive by construction) and the sampling distribution of K. p_F = share of placebo φ ≥ observed; p_K two-sided around the placebo median.
- **N2 day-block bootstrap** (300 resamples of days, controls attached to their episode) for CIs of Δπ_s, φ, K. For steps: agent-block bootstrap.
- **N3 step placebo:** every within-goal day boundary in the same regime with ≥ D days on both sides, non-holdout, balanced agent panel, excluding ±1 day around the tested steps. A step is judged by its percentile in this distribution.
- **N4 no-effect synthetic** (axis F) and the **transient-fallacy control** (O4 vs O1 on planted catalysts).
- **Rivals.** R0 *neither* (levers are inert at this resolution); R1 *pure field* (occupancy moves, K = 0); R2 *pure catalyst* (HH52's claim for nudges and human helpers: K > 0, π fixed); R3 *message-specific field* (heterogeneous messages each pull toward their own content; pooled over messages this looks like diffusion: tested by O6 drift).

## Classification rule (pre-registered)
Per class, over its **powered** units (point kicks: ≥ 20 episodes; steps: all usable):
- **Field effect present:** Stouffer-combined p_F < 0.01 *and* p_F < 0.05 in ≥ ⅓ of powered units. Steps: ≥ 2 of the class's steps above the placebo p95 for φ (or the single step, if only one).
- **Catalytic effect present:** random-effects pooled K with 95% CI excluding 0, |K̂| ≥ 0.10, and the same sign in ≥ ⅔ of powered units. Steps: K outside the placebo [p2.5, p97.5] with |K| ≥ 0.10 in ≥ 2 steps (or the single step).
- **Lever class** = field / catalyst / both / neither. **Class probabilities** from a bootstrap over units (each unit drawing one of its own bootstrap replicates), using effect-size thresholds φ_exc ≥ 0.10 and |K| ≥ 0.10.
- **Multiplicity:** 7 classes × 2 effects × 2 state families = 28 class-level decisions. Verdicts at the thresholds above are reported, with a flag for those that also survive Bonferroni (p < 0.0018).

## Synthetic validation (axis F)
`analysis/synthetic.py`, same estimators (`analysis/h39lib.py`). Four-state Markov agents (work, chat, idle, consolidate) at village sampling (1-min grid; 12 agents × 5 days × 240 min, and 25 agents × 20 days × 480 min), with agent heterogeneity, optional aging in idle (H16) and optional kinetic-Potts herding. Planted 20-min lever effects with a 0–4 min onset delay, nudges targeted at agents idle ≥ 10 min: θ = ½ field (a = 0.8 on work/idle); destination-only (heat-bath) field; uniform catalyst (×2); edge catalyst (idle ↔ work ×2.5); escape-only kick (idle exits ×2.5); null. Steps: 2 + 2 days with day-level noise (SD 0.25 on log rates), placebo = the other day boundaries of a 40-day series. Content: q = 6 chain at 30-min windows.

**Results (2026-10-04, before any real-data run).** `data/processed/H39-catalysts-vs-fields/synthetic/synthetic_results.json`; figure `figures/synthetic_validation.pdf`. Rates are shares of replicates (8 per cell, 16 for nulls; Markov and aging + Potts variants pooled) recovering the expected class, with the A1 rule.

| Planted | G51-like (≈ 500–1,500 episodes) | 5-day period (≈ 30–100) | 5-day, sparse kicks (≈ 37) |
| --- | --- | --- | --- |
| null → neither | 0.97 | 0.88 | 0.75 |
| field θ = ½ → field | 1.00 | 0.44 | 0.25 |
| field, destination-only → field | 0.56 (1.00 Markov; aging masks it) | 0.25 | 0.00 |
| catalyst, uniform → catalyst | 0.94 | 1.00 | 0.88 |
| catalyst, edge → catalyst | 1.00 | 0.88 | 0.75 |
| escape-only → both | 1.00 | 0.50 (else "catalyst") | 0.12 |
| step: null / field / catalyst | 14/16 neither (2 false catalysts) / 5 field + 2 both of 8 / 8 of 8 catalyst | | |
| content clusters, point kicks: null / field / catalyst | 7/8 neither / 2/8 field / 7/8 catalyst | | |

What this means for the design:
- **Catalytic effects are identifiable at village sampling, field effects only at G51 scale.** With ≈ 30–100 episodes a planted field is found in 25–44% of replicates; a catalyst in 88–100%. So a "catalyst" verdict in a small period means "catalyst, field undetermined", and a "both" lever looks like a catalyst there. Class verdicts lean on G51 (nudges, mentions, human messages) and on the pooled meta-analysis.
- **The transient fallacy is real:** a pure catalyst acting on agents that start out stuck lowers the 30-min idle share significantly (all G51-like replicates) while the stationary Δπ_idle stays ≈ 0. Reading "less idle after a nudge" as a field is wrong without the stationary decomposition.
- **Leakage is small and known:** at the 1-min grid, fast states saturate (one jump per minute), so a "uniform" catalyst shifts π slightly (φ_exc ≈ 0.06); the non-equilibrium base chain gives a θ = ½ field K ≈ +0.14 (theory) at fixed occupancy. Both sit below the 0.10 / detectable thresholds most of the time.
- **Design fix found in the synthetic null (before real data):** requiring controls to stay kick-free over the *future* window manufactured a field (the nudger targets agents that stay idle, so future-clean controls are agents that escaped on their own; null φ p = 0.01). Fixed: control eligibility uses the past only, and both arms are cut at the next kick (hazards stay unbiased when kicks depend on the past). Herding confounding (nudges arriving in swarm-wide lulls; 2–3/16 false fields) was reduced by adding the other agents' activity level (3 bins) to the matching strata.
- **Content-cluster fields from single kicks are not identifiable** (2/8). Point-kick content effects therefore use O6 (drift toward the message vs diffusion; continuous, calibrated by its placebo, not separately simulated). Content clusters are used only for steps, which have many transitions.

**Amendment A1 (2026-10-04, after the synthetic validation, before any real-data run).** The field criterion gets the same effect-size floor as the catalytic one: field present only if φ_exc ≥ 0.10 as well as p_F < 0.05 (unit level), and if the mean φ_exc over powered units ≥ 0.10 (class level). Reason: at G51 scale the significance-only test flags sub-threshold π shifts from catalysts (discretization leakage) and from herding. With A1, G51-like recovery is 0.94–1.00 for every planted class except the destination-only field under aging (0.56). Steps: the same floor applies to the placebo-p95 test.

## Candidate goal periods
- **Point kicks (per period):** all non-holdout periods with ≥ 3 days and states: G03–G06, G08, G10–G13, G16–G21, G23–G27, G30, G31, G33, G35, G37–G42, G44, G51 (non-holdout days to 09-04). Nudges exist from 02-13 (G30 last day), so nudge units are G31 onward. NE41 units: G37–G42, G44, G51.
- **Spanning:** NE34 (kickoffs between consecutive non-holdout periods in one regime), NE42, NE15, NE10, NE07, NE16, NE17, NE18, NE03, NE06.
- **Not used:** the locked holdout (#1, #9, #14, #15, #22, #28, #29, #32, #34, #43, #45–#50, NE12, NE21+NE23, NE30, the #51 tail); G36 straddles the regime boundary except for NE16's regime-III days; G02, G07 (2 days).
- **Card candidates not testable here:** NE23 is held out (confirmation target); "B" (human helpers, 2025-07-16) is the first day of the 2-day #7 and coincides with a start-time change (07-18), so it is reported only as a descriptive step; the sign-in hand-off has no dated event in the shared tables.
- **What had been seen before writing this:** the round-1 results in `LOG.md`; the H14, H16, H17, H04 cards; structural counts only (kicks per class per period: e.g. N_tgt 970 exposures in G51, 120 in G38, ≤ 72 elsewhere; H_men ≤ 35 per period except G04/G05/G51; A_men thousands), and table schemas. No H39 statistic had been computed on real data.

## Prediction
*Written 2026-10-04 (UTC), before running the analysis on real data, before the synthetic validation results.*

**P1 nudges (N_tgt): both, field-leaning.** Nudges raise escape from idle (pooled ln(e^K_idle/e^C_idle) > 0, CI excluding 0) and lower the stationary idle share (pooled Δπ_idle < 0, CI excluding 0). K > 0. ρ in [0.3, 0.7]. **HH52's pure-catalyst claim (π unchanged) is predicted to fail.** Counts against: Δπ CI including 0 with K > 0 (HH52 right), or K ≈ 0 (pure field). Power: powered units G38, G41, G51 at most; expect a class verdict carried by G51.

**P2 human messages (H_any; H_men and H_und reported): both, with the field toward chat.** Δπ_chat > 0 (pooled CI excluding 0); K > 0. Mentioned (H_men) effects ≥ unmentioned (H_und). Content: drift toward the message (Field_c > 0) in the pooled estimate. Low confidence on K.

**P3 @-mentions (A_men): field toward chat, weaker than human messages.** Δπ_chat > 0 (pooled CI excluding 0) and |Δπ_chat| below P2's; K > 0 small (|K| < 0.2). Content drift toward the mentioning message > 0.

**P4 context erasure (NE41, CF): field within work, no catalysis.** On B6, after a forced erasure the agent browses/looks more and types/shells less (Δπ_browse > 0, Δπ_type+shell < 0, pooled CIs excluding 0; H15's write dip); on B4 |K| < 0.10. CF and CV give the same class.

**P5 goal kickoffs (NE34): a content field, not a behavior lever.**
- Content (C6): φ above the placebo p95 in ≥ 70% of usable kickoffs; content K above the placebo median in ≥ 60% (H20's kickoff relaxation: faster topic churn after a kickoff).
- Behavior (B4): φ above the placebo p95 in ≤ 30% of kickoffs; K inside the placebo [p2.5, p97.5] in ≥ 70% (H04: kickoffs change what, not how much).
- Class: content = field (or both); behavior = neither.

**P6 room changes (NE42, NE15).** Merge (05-04) → Δπ_chat > 0; split (05-11) → Δπ_chat < 0 (more or fewer interlocutors). Both kickoff-confounded; expected inconclusive (neither exceeds the regime-III kickoff-placebo p95). NE15: its pre-side is in the holdout; only a #33-vs-#35 comparison is possible and is reported as descriptive.

**P7 scaffold changes.**
- Prompt instructions about activity (2025-08-01 "keep going", 2025-10-22 "keep working until the end of the day", NE07 "don't do nothing") and style (2026-05-28): field if anything (Δπ_idle < 0 for the activity prompts), but **underpowered: at most 1 of 4 above the placebo p95.**
- NE16 (03-26 fix of agents getting stuck on empty responses): catalyst (K above the placebo p97.5).
- NE10 (nudger on, 02-13): the same direction as P1 (Δπ_idle < 0, idle escape up), not significant at step level (one post day).
- Tool/channel changes (NE03, NE06, NE17, NE18): neither (inside the placebo band).

**P8 operator taxonomy (the deliverable).** No message-borne lever is a pure catalyst: every message carries content and therefore a field. Expected table: *to change what agents talk about*: goal kickoffs (content field); *to pull an agent into conversation*: a directed human message or @-mention (field toward chat); *to unstick an idle agent*: a nudge (raises idle escape, and also tilts away from idle); *pure catalysis* only from scaffold fixes that remove a stall (NE16), if at all.

**What would count against the framework as a whole:** the synthetic validation failing to separate planted fields from catalysts at village sampling (then no real-data verdict is interpreted), or every real lever landing in *neither*.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness". Scored after round 1 (2026-10-04).
**Rival models:** R0 neither; R1 pure field; R2 pure catalyst (HH52); R3 message-specific field.
**Locked holdout used for confirmation:** none. `analysis/confirm.py` (C1–C8 on #45–#47, #49, #50, the #51 tail, held-out kickoffs and NE23) is written and dry-run on stand-ins; **not run**.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | States, levers, windows and controls come from shared tables, with the assumptions listed (past-only kick dependence; matched strata; load-distribution convention for the split). B4 does not mean the same thing in regimes I and III ("work" = sessions vs perma-computer-use), and content clusters partly track agents (style) rather than topics |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | No Markov extrapolation: kicked and control rates are compared in matched windows, which is valid under the known non-Markov aging (H16, H17) and robust to it in synthetic data. Truncation assumes kicks depend only on the past (sequential ignorability), which is untestable. Within-window stationarity is not tested |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Beats the placebo-episode null for nudges (K and φ), human messages (φ, Stouffer 2e−9), erasure (8/8 periods) and, in direction-free form, mentions. Day-block bootstrap CIs throughout. No held-out-day prediction |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | The escape-only signature (half field, half catalyst; ρ ≈ 0.5, with K > 0 *and* Δπ_idle < 0) was predicted for nudges and observed (ρ 0.51). The kickoff prediction "content, not behavior" holds only in regime III |
| E interventional | predicts the change across a natural experiment | 1 | NE34 kickoffs 3/4 of P5; NE10 wrong sign (not significant); NE16 predicted catalyst, observed neither; NE03 unexpected catalyst. The post hoc 08-21 nudger-off step (P9, dated before running) behaves as predicted (neither) and leans catalytic (idle escape −13%, idle share flat). NE23 held out |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Planted classes recovered at G51 scale (0.94–1.00, except a destination-only field under aging, 0.56); catalysts recovered even at 30–100 episodes, fields not (25–44%). The synthetic null found and fixed a future-conditioning bias. W = 15 / 60 and B6 give the same nudge class. Content-cluster point fields are not identifiable |
| G ground truth | agrees with known structure | 1 | Nudges raise idle escape ×1.4–1.6 (H16: a directed message at the pause gate raises the odds of acting ×1.5–2.9; H04: a delayed nudge response). Regime-III kickoffs change content, not activity (H04). The erasure result is the opposite of a naive reading of H15's write dip, but H15 measured a different observable (functional-output turns) |
| H comparative | beats the named rivals | 1 | R2 (pure catalyst) rejected for nudges per episode (field present in G51, p 0.005). R1 (pure field) rejected for nudges (K CI excludes 0). R3 (message-specific field) wins for mentions and G51 human messages: content drifts toward the message while behavior does not move. R0 wins for mentions in the best-powered units |
| I transfer | holds in other same-mode periods, including the holdout | 1 | Erasure transfers across all 8 regime-III periods. Nudges rest on G51 (G38 same sign, not significant). Human-message effects do not transfer from regime I to III. Holdout not used |

## Results by goal period
Verdict rule (per period, dated in each folder): every powered class matches its predicted class and direction → supported; none → failed; else mixed; no powered class → descriptive. Most "failed" verdicts come from P3 (mentions predicted to pull agents into chat; they do not) and P4 (erasure).

| Period | Role | Verdict | Key numbers (B4 class per powered lever, episodes, K) |
| --- | --- | --- | --- |
| [G03](goalperiod-subhypotheses/G03/README.md) | exploratory | descriptive | no powered class |
| [G04](goalperiod-subhypotheses/G04/README.md) | exploratory | supported | human both (n 63, K +0.58) |
| [G05](goalperiod-subhypotheses/G05/README.md) | exploratory | descriptive | no powered class |
| [G06](goalperiod-subhypotheses/G06/README.md) | exploratory | mixed | human field (n 29, K -0.28); mention field (n 23, K -0.11) |
| [G08](goalperiod-subhypotheses/G08/README.md) | exploratory | failed | human field (n 30, K -0.01); mention field (n 59, K -0.01) |
| [G10](goalperiod-subhypotheses/G10/README.md) | exploratory | failed | human neither (n 24, K -0.15); mention neither (n 21, K +0.05) |
| [G11](goalperiod-subhypotheses/G11/README.md) | exploratory | failed | human field (n 22, K -0.08); mention neither (n 38, K +0.09) |
| [G12](goalperiod-subhypotheses/G12/README.md) | exploratory | failed | mention field (n 42, K -0.01) |
| [G13](goalperiod-subhypotheses/G13/README.md) | exploratory | mixed | human field (n 40, K +0.08); mention field (n 55, K +0.02) |
| [G16](goalperiod-subhypotheses/G16/README.md) | exploratory | failed | mention neither (n 37, K +0.07) |
| [G17](goalperiod-subhypotheses/G17/README.md) | exploratory | failed | human both (n 25, K +0.14); mention catalyst (n 31, K +0.23) |
| [G18](goalperiod-subhypotheses/G18/README.md) | exploratory | failed | mention field (n 128, K +0.09) |
| [G19](goalperiod-subhypotheses/G19/README.md) | exploratory | failed | mention neither (n 123, K +0.02) |
| [G20](goalperiod-subhypotheses/G20/README.md) | exploratory | failed | mention neither (n 150, K +0.07) |
| [G21](goalperiod-subhypotheses/G21/README.md) | exploratory | failed | mention both (n 62, K +0.25) |
| [G23](goalperiod-subhypotheses/G23/README.md) | exploratory | failed | human field (n 21, K +0.15); mention catalyst (n 82, K +0.10) |
| [G24](goalperiod-subhypotheses/G24/README.md) | exploratory | failed | mention neither (n 66, K +0.04) |
| [G25](goalperiod-subhypotheses/G25/README.md) | exploratory | failed | mention neither (n 72, K -0.07) |
| [G26](goalperiod-subhypotheses/G26/README.md) | exploratory | supported | mention both (n 68, K +0.10) |
| [G27](goalperiod-subhypotheses/G27/README.md) | exploratory | supported | mention field (n 151, K +0.03) |
| [G30](goalperiod-subhypotheses/G30/README.md) | exploratory | failed | mention field (n 98, K -0.05) |
| [G31](goalperiod-subhypotheses/G31/README.md) | exploratory | failed | mention field (n 82, K +0.02) |
| [G33](goalperiod-subhypotheses/G33/README.md) | exploratory | failed | mention field (n 48, K +0.03) |
| [G35](goalperiod-subhypotheses/G35/README.md) | exploratory | failed | mention neither (n 117, K +0.07) |
| [G37](goalperiod-subhypotheses/G37/README.md) | exploratory | failed | mention neither (n 62, K +0.09); erasure Δπ_idle -0.01, K -0.05 |
| [G38](goalperiod-subhypotheses/G38/README.md) | exploratory | failed | nudge neither (n 32, K +0.13); mention catalyst (n 333, K -0.11); erasure Δπ_idle -0.13, K -0.29 |
| [G39](goalperiod-subhypotheses/G39/README.md) | exploratory | failed | human field (n 34, K -0.02); mention field (n 125, K +0.04); erasure Δπ_idle -0.13, K -0.19 |
| [G40](goalperiod-subhypotheses/G40/README.md) | exploratory | failed | mention catalyst (n 111, K +0.12); erasure Δπ_idle -0.13, K -0.11 |
| [G41](goalperiod-subhypotheses/G41/README.md) | exploratory | failed | mention neither (n 110, K -0.03); erasure Δπ_idle -0.08, K -0.17 |
| [G42](goalperiod-subhypotheses/G42/README.md) | exploratory | failed | mention both (n 130, K +0.12); erasure Δπ_idle -0.11, K -0.27 |
| [G44](goalperiod-subhypotheses/G44/README.md) | exploratory | mixed | human neither (n 21, K +0.20); mention field (n 69, K +0.05); erasure Δπ_idle -0.16, K +0.05 |
| [G51](goalperiod-subhypotheses/G51/README.md) | exploratory | mixed | nudge both (n 304, K +0.16); human neither (n 407, K -0.02); mention neither (n 3060, K +0.00); erasure Δπ_idle -0.20, K -0.06; 08-21 nudger-off step: neither (P9 ✓) |
| [NE34](goalperiod-subhypotheses/NE34/README.md) | exploratory (spanning) | mixed | 26 kickoffs; P5 3/4 (content field only in regime III) |
| [NE42](goalperiod-subhypotheses/NE42/README.md) | exploratory (spanning) | mixed | merge chat +0.04 n.s.; split not separable from kickoff |
| [NE15](goalperiod-subhypotheses/NE15/README.md) | descriptive | descriptive | #33 vs #35, descriptive |
| [NE41](goalperiod-subhypotheses/NE41/README.md) | exploratory (spanning) | failed | idle −0.13, work +0.13, K −0.15 (A2 chain); P4 failed |
| [NE10](goalperiod-subhypotheses/NE10/README.md) | exploratory (spanning) | failed | neither; idle +0.035 (wrong sign, n.s.) |
| [NE07](goalperiod-subhypotheses/NE07/README.md) | exploratory (spanning) | supported | neither (as predicted) |
| [NE16](goalperiod-subhypotheses/NE16/README.md) | exploratory (spanning) | failed | neither (predicted catalyst) |
| [NE17](goalperiod-subhypotheses/NE17/README.md) | exploratory (spanning) | supported | behavior neither; content field |
| [NE18](goalperiod-subhypotheses/NE18/README.md) | exploratory (spanning) | supported | behavior neither; content catalyst |
| [NE03](goalperiod-subhypotheses/NE03/README.md) | exploratory (spanning) | failed | catalyst K +0.135 (98th pct; predicted neither) |
| [NE06](goalperiod-subhypotheses/NE06/README.md) | exploratory (spanning) | supported | neither (as predicted) |
## Results
### Exploratory round 1 (2026-10-04; non-holdout only)
- **Scripts:** `scheme/build.py`; `analysis/h39lib.py` (estimators); `analysis/synthetic.py` and `synthetic_figure.py`; `analysis/run_period.py` (one goal period) and `run_all.py`; `analysis/run_steps.py` (kickoffs, rooms, scaffold); `analysis/run_autooff.py` (post hoc P9); `analysis/summarize.py`; `analysis/figures.py`; `analysis/write_period_folders.py` + `write_results.py`; `analysis/confirm.py`.
- **Numbers:** `data/processed/H39-catalysts-vs-fields/G<NN>/results.json`, `steps/steps_results.json`, `steps/autooff_results.json`, `summary.json`, `period_verdicts.json`, `synthetic/synthetic_results.json`, `confirm_dryrun/confirm_results.json`.
- **Figures:** `figures/summary_obs.pdf` (the lever plane and where each field points), `figures/cross_period.pdf` (K per period per lever), `figures/synthetic_validation.pdf`.

### The lever taxonomy (deliverable)
Pooled over powered units (≥ 20 episodes). φ_exc: placebo-corrected RMS shift of ln occupancy (field strength, in units of T). K: ln change of the total escape rate at fixed occupancy (catalysis). Class probabilities: unit bootstrap with the effect-size thresholds (0.10).

| Lever | Field: what changes (stationary Δπ) | Catalysis: K [95% CI]; escape | Class (probabilities) | Operator reading |
| --- | --- | --- | --- | --- |
| **Nudge** (automated, names the agent) | idle share −0.073 [−0.108, −0.035] in G51 (pooled over G38 + G51: −0.043, CI spans 0); small gains in chat, work, consolidate | **+0.150 [+0.070, +0.231]**; idle escape +0.34 (×1.4; G51 ×1.57) | **both** (P = 0.81; field 0.12, catalyst 0.06); ρ = 0.51 | *Unsticks* idle agents and also keeps them out of idle while it acts. What was measured is one nudge after a quiet spell; the nudger re-fires often (only 316 of 965 G51 nudge minutes qualify as episodes) |
| **Human message** (to the room or naming the agent) | strong field (φ_exc 0.24 [0.15, 0.42]); regime I: chat → computer work (work +0.08, chat −0.04, 8 periods); G51: **none** on behavior (n = 407) | +0.01 [−0.04, +0.13] | **field** (P = 0.94) | Changes *what agents do* in the early, small village; in the large regime-III village it moves content toward the message (drift +0.27 SD, p 0.001) but not activity. Directed (mentioning) human messages were too rare to test (≤ 8 episodes per period) |
| **@-mention** by another agent | significant in 14/29 periods, but the direction changes from period to period (pooled Δπ ≈ 0 for every state; I² ≈ 0.7); **none** in G51 (n = 3,060) or G38 (n = 333) | +0.044 [+0.013, +0.075] (below the 0.10 floor) | field by the rule (P = 0.77, neither 0.23); precision-weighted φ_exc 0.09 | Does not reliably change behavior state. **Does steer content:** the mentioned agent's next 30 min move toward the mentioning message (+0.32 SD [0.20, 0.43], 12 periods) |
| **Context erasure** (forced consolidation at the 41-turn cap, NE41) | idle share −0.13 (work/chat/idle chain), work +0.13; idle down in **8/8** regime-III periods (voluntary consolidations: 8/8 too) | −0.148 [−0.22, −0.08] (switching slows: work escape −0.5) | **both** (anti-catalytic field toward work; P(both) = 0.73) | Right after a context reset agents work more steadily and idle less, for ~20 min. The cap is not a costless knob, but its short-run activity effect is positive (H15's write dip is a different observable) |
| **Goal kickoff** (NE34) | behavior: small (individually 27% above the day-boundary placebo p95; jointly Stouffer p 1e−4); content: 4/6 regime-III kickoffs above p95, 0/13 regime-I | inside the placebo band in 77% | behavior **neither / weak field**; content **field in regime III** | Use goals to change *topics* in the regime-III village; in regime I, content already turns over as much between two ordinary days |
| **Room merge / split** (NE42) | merge chat +0.04 (n.s.); split beyond placebo, but like most regime-III kickoffs | — | **inconclusive** (kickoff-confounded) | No separable evidence |
| **Scaffold prompt steps** (NE07, 08-01, 10-22, 05-28) | none beyond placebo (0/4) | none | **neither** (underpowered at day level) | Prompt nudges to "keep working" did not visibly change behavior over 2 days |
| **Scaffold fixes / tools** (NE16, NE17, NE18, NE06, NE03) | NE17 content field, NE18 content catalyst; behavior none except NE03 | NE03 +0.135 (98th pct), others inside | NE03 **catalyst**; others **neither** | One single-step hit among 10 steps is about what chance gives; not a lever |
| **Nudger off** (08-21, post hoc) | idle share flat (−0.005 to +0.025) | −0.05 / −0.08 (5 + 5: lowest of 20 placebos); idle escape −0.12 to −0.14 | **neither** by rule, leaning catalytic | At swarm level, losing the nudger slows escape slightly without changing occupancy; the per-episode field is too diluted to see |

**Rule for an operator:** *to change what agents do* (work vs. chat, topics), use content-bearing levers: goals (topics, regime III) and human requests (activity, small village). *To unstick an idle agent*, send one directed nudge: it raises idle escape by ~40–60% and keeps the agent out of idle while it acts. Expect side effects, because no message is a pure catalyst. *To steer what an agent writes without changing how busy it is*, mention it: content follows the mentioning message. Repeated or broadcast messages, prompt tweaks and channel changes did not measurably move behavior at day scale.

### Outcome vs prediction
| Prediction | Outcome | Verdict |
| --- | --- | --- |
| P1 nudges: both; pooled Δπ_idle < 0 (CI excl. 0); idle escape up; K > 0; ρ in [0.3, 0.7] | class both (P 0.81); K +0.150 [+0.070, +0.231] (Bonferroni ✓); idle escape +0.34 [+0.09, +0.59]; ρ 0.51; Δπ_idle −0.043 [−0.109, +0.023] pooled (G51 alone −0.073 [−0.108, −0.035]) | **mostly supported** (4/5; the idle-share CI rests on G51 alone). HH52's pure catalyst rejected per episode |
| P2 human messages: both; field toward chat; H_men ≥ H_und; content drift > 0 | field (P 0.94, Bonferroni ✓), K ≈ 0; field points *away* from chat toward work (regime I), none in G51; H_men untestable; content drift +0.27 SD (G51) | **failed** (class and direction); content part ✓ |
| P3 @-mentions: field toward chat, small K, content drift > 0 | behavior: direction-free shifts only, pooled Δπ_chat −0.001 [−0.010, +0.007]; K +0.044; content drift +0.32 SD [0.20, 0.43] | **mixed** (behavior ✗, content ✓) |
| P4 erasure: browse up, type+shell down, \|K\| < 0.10, CF = CV | browse +0.056 ✓; type+shell +0.099 ✗; K −0.148 in the A2 chain ✗; CF ≠ CV ✗ | **failed** |
| P5 kickoffs: content field ≥ 70%; content churn ≥ 60%; behavior field ≤ 30%; behavior K inside ≥ 70% | 25% ✗ (5/20); 65% ✓; 27% ✓; 77% ✓ | **mixed** (3/4; content field only in regime III) |
| P6 rooms: merge chat up, split chat down; inconclusive | merge +0.039 (n.s.) ✓; split +0.021 ✗; not separable from kickoffs | **mixed / inconclusive** |
| P7 scaffold: prompts ≤ 1/4 above p95; NE16 catalyst; NE10 idle down (n.s.); tools neither | 0/4 ✓; NE16 neither ✗; NE10 idle +0.035 ✗ (n.s. ✓); tools 3/4 ✓ (NE03 catalyst) | **mixed** |
| P8 taxonomy: no message is a pure catalyst; goals content field; directed messages pull into chat; nudge unsticks and tilts; pure catalysis only from fixes | ✓; regime III only; ✗; ✓; ✗ (NE16 neither; NE03 and the nudger-off step lean catalytic) | **mixed** |
| P9 (post hoc, dated before running): nudger-off step at 08-21 is neither | neither; leans catalytic | **supported** |

### Per-class results
- **Nudges (P1).** Powered only in G51 (304 episodes) and G38 (32). G51: K +0.160 [+0.06, +0.25]; idle escape +0.45 [+0.29, +0.59]; Δπ (work, chat, idle, consolidate) = +0.018, +0.013, −0.073, +0.041; transient 30-min idle share −0.056. W = 15 / 60 give K 0.14 / 0.12. On B6 the idle drop goes to shell (+0.028) and consolidate. Nudge content drift: n.s. G38: same signs, n.s. Every other period has < 20 episodes (nudges re-fire within 30 min, so few are isolated).
- **Human messages (P2).** 11 powered units (10 for H_und; H_men never powered). Regime I (8 units): work +0.077, chat −0.042, K +0.06, field in 7/8. G04 (2025 public chat; 63 episodes) is the one *both*: idle → work + chat, idle escape ×3. G51 (407 episodes): nothing on behavior, content drift toward the message +0.27 SD.
- **@-mentions (P3).** 29 powered units. Fields in 14/29, but the direction varies: toward idle in G08, G13, G31, G33; toward work in G12, G21, G26, G30. K small and positive (G38 the exception, −0.11). Content drift +0.32 SD, consistent across 12 units.
- **Erasure (P4, NE41).** 144–5,558 CF events per regime-III period. A2 chain: idle −0.13, work +0.13, K −0.15 (CF); CV the same direction. Full B4 chain: consolidate −0.19 (the consolidation clock); K +0.24, CI spans 0.
- **Kickoffs (P5).** 26 usable; content in 20. Era dependence as above. The B4 kickoff shift is jointly significant but small (on average work +0.017, idle −0.020).
- **Scaffold and rooms (P6, P7).** Single steps against 12–58 day-boundary placebos, 2-day windows; all but NE03 inside the band on behavior.

### Caveats
- **Power is uneven.** The nudge verdict rests on one period (G51). Synthetic validation says fields are invisible below ~100 episodes, so "catalyst" or "neither" in small units does not rule out a field.
- **Multiplicity.** 28 class-level decisions. Bonferroni (p < 0.0018) is survived by: nudge K; the human-message field; the mention field (direction-free); the erasure field. The nudge field is not (Stouffer p 0.009).
- **The field/catalyst split is a convention** (load distribution). A destination-only field leaks into K at fixed occupancy, and away from detailed balance a θ = ½ field does too (K ≈ +0.14 at a = 0.8 on the synthetic base). Small |K| (< 0.10) is not interpretable as catalysis.
- **States.** B4 has different meanings in regimes I and III. Mentions are noisy (H18: mention "responses" carry a common-cause component). Content clusters partly track agent style (H13). Human speakers are anonymized, so a human "helper" cannot be separated from public chat.
- **Design choices made after seeing data:**
  - A2: the no-consolidate chain for erasure, added after a quick G38 test run showed the consolidation clock.
  - The era-specific content-TV check of kickoffs.
  - P9: the post hoc discovery of the 08-21 switch-off (its prediction was dated before running).
  - Moving C1/C2 in the confirm script from the #51 tail to #45–#50, because the nudger is silent after 08-20.

  Each is labelled where it appears; pre-registered verdicts are reported unchanged.
- **Matching** uses only the past, state, dwell age, swarm activity and day third. Targeted levers (nudges to idle agents, mentions after an agent spoke) may still be confounded by unobserved context, e.g. what the agent is waiting for.

### One-page figure summary
`figures/summary_obs.pdf`.
- **(a)** Each lever is plotted as (catalytic K, field φ_exc), with 95% CIs:
  - only the nudge sits in the "both" corner;
  - human messages and erasure are fields (erasure is anti-catalytic);
  - mentions sit near the floor;
  - kickoffs (behavior) sit near zero catalysis.
- **(b)** Where each field points:
  - the nudge lowers idle;
  - human messages in regime I raise work and lower chat;
  - mentions point nowhere on average;
  - erasure trades idle for work.

## Confirmatory predictions (C-*; written 2026-10-04 after round 1; not run)
Script: `analysis/confirm.py`. It refuses to run without `--confirm --i-understand-this-uses-the-locked-holdout`.
- **Dry run.** `--dry-run` uses non-holdout stand-ins and wrote `confirm_dryrun/` (stand-in values only):
  - late #51 for the tail;
  - G38, G41, G42 and G44 for #45–#50;
  - regime-III kickoffs;
  - a G38 day pair for NE23.

  The CF/CV classifier agrees with H15's labels on 87% of the stand-in consolidations.
- **Reuse policy.** These held-out periods are reused under `hypotheses/holdout.md`:
  - #45 (H02, H23);
  - NE21 + NE23 / #46–#50 (H04);
  - the #51 tail (others, planned).

  H39's statistics differ (matched-window stationary decomposition, content drift toward the kick message, kickoff step decomposition), and none has been computed there. The card and script must be committed, and the reuse disclosed in `LOG.md`, before a run.
- **Power warning.** The dry run had 42 nudge episodes over four stand-in periods, and C1 was not significant there. C1 may be underpowered on #45–#50 as well.

| ID | Target | Statement | Primary |
| --- | --- | --- | --- |
| C1 | #45–#47, #49, #50 pooled | nudges: pooled K > 0, CI excluding 0 | yes |
| C2 | same | nudges: idle escape up and Δπ_idle < 0, pooled CIs excluding 0 | no |
| C3 | #51 tail | @-mentions: \|K\| < 0.10 and φ_exc < 0.10 (no behavior lever) | yes |
| C4 | #51 tail | @-mentions and human messages: content drift toward the message > 0 (p < 0.05) | yes |
| C5 | #51 tail | human messages: \|K\| < 0.10 and φ_exc < 0.10 | no |
| C6 | #45–#47, #49, #50 pooled | forced erasure (A2 chain): Δπ_idle < 0 and Δπ_work > 0 | yes |
| C7 | held-out regime-III kickoffs (#44 → #45 … #49 → #50) | content φ above the frozen regime-III placebo p95 in ≥ 50% | no |
| C8 | NE23 (06-13 off vs 06-12 on, #best panel) | Δπ_idle (off − on) > 0 | no |

- **Overall rule:** supported if C1 and at least two of C3/C4/C6 pass; failed if C1 fails and at most one of C3/C4/C6 passes; mixed otherwise.
- **Dry run (stand-ins, not evidence):** C1 ✗, C2 ✗, C3 ✓, C4 ✗, C5 ✓, C6 ✓, C7 ✓, C8 ✗.

## Notes
- **From H44 (2026-10-04):** "busy but unproductive" resolves at call resolution: after a forced erasure agents re-read in an orderly burst (read share 0.22 → 0.47) and write less (−26%); Jev's 5-min windows label those windows as more executing. No temperature pulse.
- **From H43 (2026-10-04):** a nudge's escape effect exists only when a glance counts as escape; on sustained runs (≥ 3 active calls) a first nudge's effect is null (lnHR 0.07). Kicks show no refractory window beyond the read-out: a second kick read by a later call keeps 80–130% of the first's effect.
- 2026-10-04: promoted from HH52 by Vivian (usefulness-first batch); wave 2.
- 2026-10-04: design, observables, nulls, classification rule and predictions P1–P8 written before any real-data run.
- 2026-10-04: synthetic validation. Design fixes, all before real data: past-only controls, both arms cut at the next kick, a swarm-activity stratum, a 30-min quiet period, and Amendment A1.
- 2026-10-04: **Amendment A2** (after a quick G38 test run, before the full run). Erasure is also scored on the work/chat/idle chain without the consolidate state, because the consolidation clock mechanically depletes transitions into consolidate right after any consolidation. Both chains are reported; P4 is scored on the pre-registered chains.
- 2026-10-04: **Data finding.** The `automated` speaker (nudges and daily bookends) is silent from 2026-08-21 (last nudges 08-20); this is not in the CHANGELOG. Proposed as a new NE (nudger off inside #51, non-holdout) and used for P9.
- 2026-10-04: round 1 done. Scorecard A1 B1 C1 D1 E1 F1 G1 H1 I1. Not promoted. Disk: 6.2 MB in `data/processed/H39-catalysts-vs-fields/`. Summary pages follow the updated two-page rubric (page-2 macros written).
