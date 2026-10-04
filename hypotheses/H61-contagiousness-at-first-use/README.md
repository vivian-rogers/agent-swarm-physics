# H61: Contagiousness is predictable at first use

**Status:** exploratory round 1 done (2026-10-04). **Mostly not forecastable beyond the strongest baseline.**
- **P1 fails.** Seed features beat the poster + kickoff + room-size baseline (B4) on held-out days in 4/27 eligible periods (G08, G31, G38, G51). The pooled gain is +0.1 ± 1.6 millinats per idea. In the two largest regime-III periods the gain is small but clear: G51 +5.5 [+4.1, +7.1], G38 +6.3 [+3.0, +9.7].
- **What carries fitness is message-level dilution, not authority or timing.** An idea spreads less when its seed message is long (pooled −0.26 ± 0.04 standardised log-odds; CI < 0 in 16/27 periods) and when the message coins many items (−0.08 ± 0.03). It also spreads less when the message lies far from the kickoff field (−0.08 ± 0.02), and more when the message is a DQ2 reply (+0.10 ± 0.02). The poster's reply in-degree (+0.04 ± 0.04) and the receptive fraction (+0.00 ± 0.02) carry nothing.
- **The convergence test (P5) is inconclusive.** Unread-5 adopters are ≈ 1% of adopters, so only 7 periods are testable (pooled −0.004 ± 0.028).
- **Natives.** G26: the elected leader's 0.22× spread survives every feature adjustment (0.28 [0.09, 0.53]): **failed**. G35: designated lead designers add nothing (1.39 [0.86, 2.35]): **supported**. NE42: the #39 model transfers to the merged #40 (+33 millinats) but not to #41: **mixed**.
- Scorecard A1 B1 C1 D1 E1 F2 G1 H1 I0. `analysis/confirm.py` is frozen and dry-run on stand-ins, not run.
**Question (GOALS.md):** Q1 (what couples agents: which items the read-out channel carries), with an operator use under Q5 (a spread forecast at first use).
**Fields:** sociophysics, info theory, stat mech
**Literature:** [Kolchinsky & Corominas-Murtra 2020](../../literature/kolchinsky-2020-copying-versus-transformation.md) (the prior of a copy channel may be any distribution; here the prior is the reproduction rate of agents who had *not* read the item at a matched lag, the in-flight placebo). Background named, not filed: fitness models of popularity (Bianconi–Barabási 2001)†; predictability of cascades from early features (Cheng et al., WWW 2014)†; Vosoughi, Roy & Aral, *Science* 359, 1146 (2018)† (novelty and spread).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime; Population N(t); Contagion / adoption event with the marker set of **Idea (H34 marker rule)**; **Interaction (ledger-visible exposure)** and **Unread (in-flight) exposure placebo** (RE-D1); **Exposure (turn read-out)** (H08); **Receptive count** (H53, adapted below); **Net reply current** is *not* used. New named variants, defined under "Operational definitions" and proposed for DEFINITIONS.md (not edited here): **Idea reach (24 h)**, **Seed features (H61)**, **Focus (novel load)**, **Specificity (goal distance)**, **Poster reply in-degree (causal)**, **Receptive fraction (5 min)**, **Read-5 / unread-5 adopter**.
**From:** HH253 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` ("Making the faithful ones better") · **Models:** `physics-models/03-contagion/` (primary: heterogeneous-fitness branching)
**Data inputs (shared tables first):** H34 round-1b cascades (`data/processed/H34-idea-cascades/r1b/G<NN>/first_uses.parquet`, `trees.parquet`) and markers (`markers/uses.parquet`, `first_seen.parquet`), read as data; DQ1 context ledger (`call_windows`, `context_ledger_items`); DQ2 `reply_pairs` (`parent`, `pair_set = cand`); DQ5 chat embeddings (bge-small primary, gte-modernbert variant) and `embeddings/goals.parquet` (kickoff field); `chat_core`, `chat_mentions_clean`, `calendar`, `roster`, `period_units`; DQ6 `ground_truth_labels` (natives). Shared loader: `infra/shared/idea_ledger.py` (new; serves H61 and H62).

## Question
Is an idea's cascade size forecastable out of sample from features available at its first use (class, specificity, the poster's reply in-degree, the receptive fraction at posting), beyond class-only and poster-only baselines?

## Design: two layers (Vivian, 2026-10-04)
- **Replication:** the common estimator on every eligible goal period: the 32 non-holdout periods H34 analysed (#5–#51 minus the holdout). Period README role: `replication`.
- **Period-native tests** (`period-affordances.md`, `natural-experiments.md`), each with its own dated prediction, role `native`:
  - **NE42** (#39 → #40 → #41, rooms merged then split at a fixed roster): does the forecast trained before the merge transfer across it, and does the receptive term carry the change? Axis E.
  - **G26** (DQ6 elected leader, 01-05 19:35 →): H34 found the leader's ideas spread at 0.36× the others' and that the leader seeds 7.5× more markers per message. Do first-use features (focus) explain the deficit? Axis G.
  - **G35** (DQ6 daily lead designers): does a designated role add spread beyond the seed features? Axis G.
- **Faithfulness lever (HH253):** D (out-of-sample prediction) and H (class-only and poster-only baselines). Answered in the scorecard.

## Model
**From:** `physics-models/03-contagion/`. H61 variant: **subcritical branching with idea-level fitness.**
- H34 found that a single branching law under-predicts trees of five or more agents (25/32 periods) and that a beta-binomial with heterogeneous salience forecasts as well as branching. The natural repair is a fitness model: idea *i* has its own reproduction number R_i, and its reach is a branching process with that mean.
- **Fitness at first use.** log R_i = α_g + β_class(i) + γ_poster(i) + **θ · x_i** + η_i, where x_i are seed features observable at the first use (within 5 min for the receptive term) and η_i is unobserved idiosyncratic fitness. H61 holds if θ ≠ 0 carries out-of-sample information beyond the class and poster terms.
- **Observation model.** The forecast target is the reach within 24 h, S_i ∈ {1, …, N}. The primary event is "spreads at all", Y_i = 1[S_i ≥ 2]; for small R_i, P(Y_i = 1) ≈ 1 − e^{−R_i}, so a logistic model in x_i is the first-order fitness model. Rankings use the fitted probability; a Poisson model on S_i − 1 is the secondary.
- **What separates contagiousness from co-generation.** An idea with high fitness can spread because agents read it and reuse it (transmission), or because many agents produce it at the same moment from a common source (a field: a dashboard number, a goal term). The two predict different things for adopters who could *not* have read it: transmission needs the read; co-generation does not. So the same model is fitted to two outcomes, read-5 adoption and unread-5 (in-flight) adoption (see Observables, O5).
- **Rivals.** (R0) period base rate; (R1) class only; (R2) poster only (poster fixed effects); (R3) class + poster. (R4) a pure field: the features predict co-generated (unread) adoption as well as read adoption.

## Operational definitions (written 2026-10-04 19:15 UTC, before any real-data outcome)
- **Ideas and seeds.** H34 round-1b ideas of period g (H34 marker rule; novelty relative to the non-holdout corpus) whose first use in g is an agent message (H34 `status == seed`; Claude Code agents excluded). The seed message is m0, posted by agent p at t0 in room r on day d.
- **Idea reach (24 h).** S_i = number of distinct agents (seed included) whose first use of the idea falls in [t0, t0 + 24 h]. Ideas whose window runs past the period's last non-holdout agent message are dropped (right-censoring). Y_i = 1[S_i ≥ 2]; Y3_i = 1[S_i ≥ 3].
- **Read-5 / unread-5 adopter.** For a non-seed first use u by agent j at t_u ≤ t0 + 24 h, take the other agents' uses of the idea posted in (t_u − 300 s, t_u). j is *read-5* if at least one of them reached one of j's receiving calls no later than the call that produced u (ledger `t_call` ≤ producing-call start); *unread-5* if such uses exist, none was read, and at least one is later received by j (same room, in flight). Y_read5 = 1[≥ 1 read-5 adopter]; Y_unread5 = 1[≥ 1 unread-5 adopter].
- **Seed features (H61)** x_i, all computable at t0 (receptive: within 5 min):
  1. **class** U/D/N/W (dummies; part of the class baseline).
  2. **Focus (novel load):** log n_novel(m0), the number of period-novel ideas first used in m0. A message that coins many items spreads each one thinner.
  3. **Seed length:** log characters of m0 (`chat_core.length`).
  4. **Specificity (goal distance):** 1 − cos(m0, kickoff field) in the regime's 32-d whitened basis (bge-small primary; gte-modernbert variant). Kickoff field: `goals.parquet` kind `kickoff_room` for m0's room when present, else `kickoff`, else `goal`. Low specificity = on the goal's direction (the kickoff field impostor).
  5. **Poster reply in-degree (causal):** (R_p + 1)/(M_p + 2), where R_p = DQ2 parent replies (`pair_set = cand`, `parent`) to p's messages whose replying message was posted before t0 inside the period, and M_p = p's messages before t0 in the period.
  6. **Receptive fraction (5 min):** the share of the other agents present that day in room r (agents who posted there that day) whose ledger receiving call of m0 has t_call − t0 ≤ 300 s. It is a scheduler variable (who is about to read), adapted from H53's receptive count.
  7. **Addressed:** m0 names at least one roster agent (`chat_mentions_clean.mentions_roster`).
  8. **Threaded:** m0 has a DQ2 parent.
  9. **Period day:** log(1 + day index of t0 within the period's non-holdout days); day 0 carries the kickoff.
  10. **Room size:** log of the number of agents present that day in room r.
- **Models.** L2-penalised logistic regressions (standardised features; ridge λ = 1 on every non-intercept coefficient, so poster effects are partially pooled):
  - B0 intercept; B1 class; B2 poster; B3 class + poster;
  - **F (full)** = B3 + features 2–10; F⁻ = F without the poster terms (diagnostic).
- **Out-of-sample design: forward chaining by day.** For each test day d that has at least one earlier non-holdout day in the period with ≥ 100 ideas, every model is fitted on all earlier days and scored on day d. Scores pool all test ideas of the period.
- **Scores.**
  - ΔLL(F − B) = mean held-out log-likelihood gain per idea (millinats) for Y; 95% CI by bootstrap over seed messages (2,000 replicates; ideas sharing a seed message move together).
  - AUC for Y; Spearman ρ(predicted P, S_i); **top-decile lift** = P(Y3 = 1 | top 10% of predicted P) ÷ P(Y3 = 1), and the same for Y.
- **Eligibility:** ≥ 300 test ideas with ≥ 20 positive (Y = 1) test ideas.

## Data scheme (`scheme/`)
- **Inputs:** listed above. Held-out days are removed with `holdout_mask` and `calendar.holdout` before any table is read; the ledger join asserts that no held-out call enters.
- **Transform:** `scheme/build.py` → per period, for every agent-seeded idea: seed message, class, t0, poster, room, day; features 2–10 (both embedding models for 4); outcomes S_i, Y, Y3, Y_read5, Y_unread5 and the adopter counts by type. No text is read; markers are hashes.
- **Output:** `data/processed/H61-contagiousness-at-first-use/G<NN>/ideas.parquet`, `results/`, `synthetic/`, `_provenance.json`. Budget ≤ 30 MB.
- **Regimes covered:** I, II, III (all 32 periods; regime is recorded per period).

## Observables
- **O1.** ΔLL(F − B3), ΔLL(F − B1), ΔLL(F − B2) per period (primary: F − B3).
- **O2.** AUC and Spearman ρ for B1, B2, B3, F.
- **O3.** Top-decile lift of F for Y and Y3.
- **O4.** Fitted standardised coefficients of features 2–10 (in-sample, all days), with Wald 95% CIs from the penalised Hessian.
- **O5 (convergence impostor).** The same forward-chained models refitted to Y_read5 and Y_unread5: G_read = AUC_F − AUC_B1 for Y_read5, G_unread = the same for Y_unread5, in periods with ≥ 15 positives of each.
- **O6.** Pooled (random-effects, DerSimonian–Laird) ΔLL and G_read − G_unread across periods, reported next to the per-period values (exception (d) of CLAUDE.md does not apply; pooling is a summary, not a fit).

## Null / baseline
- **Null hierarchy:** B0 → B1 (class) → B2 (poster) → B3 (class + poster). F must beat B3 on held-out days.
- **Synthetic null (size):** real feature matrices with outcomes simulated from class + poster + day drift only (θ = 0). The P1 test (ΔLL CI > 0) must reject in ≤ 10% of replicates (S1 below).
- **Convergence null:** read-5 and unread-5 adoption generated from the same latent fitness. G_read − G_unread must then centre on 0 (S3).

## Impostors (STANDARDS.md §1)
| Impostor | How it could fake "contagiousness is predictable" | How H61 removes it, or why it does not apply |
| --- | --- | --- |
| Scheduler field | Ideas posted when many agents are about to call (day starts, bursts) reach more agents for scheduling reasons alone. | The receptive fraction and room size enter as *named* scheduler features; their coefficient is reported as a scheduler effect, not as contagiousness. The ΔLL test is forward-chained by day, so day-level activity shifts do not leak into training. Edge trimming does not apply (the unit is an idea, not a minute). |
| Exogenous field (kickoff, goal, operator) | Goal-aligned ideas are produced by many agents from the kickoff; R̂ is higher on kickoff days (H34). | Specificity (distance from the kickoff field) and the period day are features. Ideas first used by humans or the operator are excluded (seed must be an agent). O5 tests whether features predict co-generated adoption. |
| Shared model priors | Same-family agents produce the same coinages (style), which looks like spread. | Poster fixed effects absorb the poster's own style; class absorbs marker type. Family of the adopters is not modelled (stated limit); O5's unread-5 outcome catches simultaneous co-production whatever its source. |
| Contemporaneous convergence | Agents answering the same prior turn reuse the same terms without reading each other (H57; ≈ half of H34's HR₁₀). | **In-flight placebo at matched lag (O5):** read-5 vs unread-5 adoption, both within 300 s of a prior use. Contagiousness requires G_read > G_unread. |

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R0–R3 (baselines), R4 (pure field / co-generation).
**Locked holdout used for confirmation:** none yet; `analysis/confirm.py` (frozen, dry-run on stand-ins, not run) targets the #51 tail (primary), #15 and #28.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | All features come from shared tables (ledger, DQ2, DQ5 embeddings, H34 markers) with no text; assumptions are listed. **Not invariant:** a gain appears only in large regime-III periods, and class effects reverse across days in several periods (class-only held-out AUC < 0.5 in 8/27). |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | **Non-stationarity found and handled:** the kickoff bump and within-period drift are why A1 replaced log-day with a kickoff indicator. Censoring is handled by dropping ideas whose 24-h window runs past the period. **Not checked:** the fixed 24-h horizon and the 300-s lag. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Forward-chained by day. F beats B4 in 4/27 periods (pooled +0.1 ± 1.6 millinats); F beats class-only B1 in AUC in 23/27 (median +0.11), but most of that is poster identity (B2 − B1 +0.06). |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | Held-out ranking: top-decile lift median 1.8 for reach ≥ 2 and 1.9 for reach ≥ 3; held-out Spearman ρ with reach 0.16. The dilution signs (long or many-item seeds spread each item less) recur in 16/27 and 19/27 periods. |
| E interventional | predicts the change across a natural experiment | 1 | NE42: the #39 model predicts the merged #40 better than B3 (+33 [+22, +44] millinats) and calibrates the rise (0.127 vs observed 0.155; B3 0.077). It fails on the split (#40 → #41, −298, from room-size extrapolation). The receptive-count sign is unstable. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 2 | Real feature matrices, simulated outcomes: after A1 the size is 0.03 and power is 0.79 (1.0 at ≥ 2,400 test ideas). Found and fixed the day-extrapolation artifact. Second embedding model: CI > 0 in 5/27 periods with gte vs 4/27 with bge. |
| G ground truth | agrees with known structure | 1 | DQ6 natives: designated lead designers add nothing beyond features and identity (G35, as predicted). The elected leader's deficit is *not* explained by the seed features (G26, failed): the leader's 32 novel items per message are not the whole story. |
| H comparative | beats the named rivals | 1 | Beats class-only (23/27 AUC) but not poster + kickoff (4/27). The co-generation rival (R4) is not separated: the read/unread contrast has no power (7 periods, pooled −0.004 ± 0.028). |
| I transfer | holds in other same-mode periods, including the holdout | 0 | The gain holds only in 2 large regime-III periods and the regime-I G08 and G31; the holdout is not run. |

**Faithfulness lever (HH253: D and H).** D rose (held-out ranking with lift ≈ 1.8 and a replicated dilution sign). H did not: the poster baseline absorbs most of the skill.

## Prediction
*Written 2026-10-04 19:15 UTC, before any H61 statistic was computed on real data.* Seen beforehand: H34's round-1 and 1b cards (R̂ 0.09–0.40; class medians U 0.35, D 0.27, W 0.27, N 0.19; leaders seed no more spreadable ideas, #26's elected leader 0.36×; tails heavier than one branching law; beta-binomial ties branching), H41 (numbers co-generated, names gated), H53 (receptive count adds nothing to project wave size), H32 (leaders are not content sources) and the table schemas. No feature–outcome relation had been computed.

"Eligible periods" are those meeting the eligibility rule above.

| # | Prediction | Counts against |
| --- | --- | --- |
| P1 | **Forecastable beyond both baselines.** ΔLL(F − B3) > 0 with lower 95% CI > 0 in ≥ 1/2 of eligible periods; pooled ΔLL > 0 | CI > 0 in < 1/4 of periods, or pooled ΔLL ≤ 0 |
| P2 | **Beyond class.** Spearman ρ and AUC of F exceed B1's in ≥ 2/3 of eligible periods; median AUC_F − AUC_B1 ≥ 0.05 | median gain < 0.02 |
| P3 | **Which features.** (a) Focus: coefficient of log n_novel < 0 in ≥ 2/3 of periods (CI < 0 in ≥ 1/2). (b) Receptive fraction > 0 in ≥ 1/2 (CI > 0 in ≥ 1/3). (c) Poster reply in-degree: CI includes 0 in ≥ 2/3 (authority does not raise fitness). (d) Specificity < 0 in ≥ 1/2 (goal-aligned ideas spread more: a field term) | (a) focus ≥ 0 in most periods; (c) in-degree CI > 0 in ≥ 1/2 |
| P4 | **Operator-usable ranking.** Top-decile lift for Y ≥ 2 in ≥ 2/3 of eligible periods | lift < 1.5 in most periods |
| P5 | **Contagiousness, not co-generation.** G_read > G_unread in ≥ 2/3 of periods with ≥ 15 positives of each, and pooled G_read − G_unread > 0 (CI) | G_read ≤ G_unread in ≥ 1/2: the features predict simultaneous co-production (field), not transmission |

Prior credences (2026-10-04): P1 0.55, P2 0.7, P3a 0.6, P3b 0.5, P3c 0.6, P3d 0.4, P4 0.6, P5 0.45.

**Per-period verdict rule** (replication folders; written before the run):
- **supported:** ΔLL(F − B3) lower 95% CI > 0 *and* top-decile lift for Y ≥ 1.5;
- **failed:** ΔLL(F − B3) point estimate ≤ 0;
- **mixed:** otherwise (positive point estimate with CI including 0, or lift < 1.5);
- **n/a:** not eligible.

**Synthetic validation plan (axis F; before real data).** Real feature matrices (no outcomes) from six periods spanning regimes and sizes (G13, G20, G27, G38, G41, a 10-day G51 block), outcomes simulated:
- **S1, size:** Y ~ Bernoulli(logistic(class + poster + day drift)), θ = 0, 40 replicates per period. The P1 test must reject in ≤ 10%.
- **S2, power:** θ planted on focus (−0.3 SD⁻¹), receptive (+0.3) and specificity (−0.2), base rate matched to the period. Power ≥ 0.8 required for P1 to count as a test; otherwise "inconclusive".
- **S3, convergence:** read-5 and unread-5 indicators drawn from the same latent fitness with the real read/unread mix. G_read − G_unread must centre on 0; its spread sets the P5 threshold.

## Synthetic validation (axis F; run 2026-10-04 19:18–19:30 UTC, before any real-data outcome was modelled)
Code: `analysis/synthetic.py`. Outputs: `data/processed/H61-contagiousness-at-first-use/synthetic/{s1s2.parquet, s3.parquet, summary.json}`. Real feature matrices of G13, G20, G27, G38, G41 and G51 (first 10 days) with every outcome column dropped; outcomes simulated (base rate 0.18; class effects, poster effects SD 0.4, a kickoff bump of +0.4, a downward trend of −0.08 per day and a day random walk SD 0.15).
- **First run (pre-registered estimator):** F vs B3 rejected the null in 30% of replicates (G38 73%). The log period-day feature extrapolates beyond the training range under forward chaining and absorbs the within-period trend; in G20 it cost up to 2 nats per idea on some replicates. So F "beats" B3 because it models drift, not seed fitness.
- **After amendment A1 (below), S1 size:** F vs B4 rejects in 2.8% of null replicates (per period 0–6.7%); F vs B3 still 39% (B3 has no kickoff term). F vs B1 rejects in 10–97%: class-only is not a valid null when posters differ.
- **S2 power** (θ: focus −0.3, receptive +0.3, specificity −0.2 per SD): F vs B4 rejects in 79% overall; 100% in G27, G38, G41 and G51 (≥ 2,400 test ideas); 53% in G20 and 20% in G13. AUC gain of F over B1: 0.05–0.10. Lift for Y: 1.7–2.1.
- **S3, convergence contrast** (read-5 and unread-5 from the same fitness; 36 replicates): G_read − G_unread mean +0.011, SD 0.030; CI > 0 in 11%, CI < 0 in 3%, positive point estimate in 67%. The contrast leans positive under the null because the read-5 event is 4× more common and its AUC gain is less noisy.

## Amendments (pre-real; written 2026-10-04 19:30 UTC, after the synthetic validation, before any real-data outcome was modelled)
- **A1 (estimator).** The period-day feature becomes a kickoff-day indicator (1 on the period's first non-holdout day), and standardised features are clipped at ±5 training SDs. The primary baseline becomes **B4 = class + poster + kickoff day + room size**, the strongest baseline without seed features. P1 and the per-period verdict use ΔLL(F − B4); ΔLL(F − B3) is reported. Reason: S1 (above).
- **A2 (power and the P5 threshold).** Periods with < 2,500 test ideas are flagged **underpowered** (S2 power < 0.8); P1's "≥ 1/2 of eligible periods" is reported on all eligible and on powered periods. P5 is re-scored against the S3 null: it passes if the pooled G_read − G_unread lower 95% CI exceeds +0.011 (the null mean) and the per-period CI > 0 rate exceeds 1/3 (null 0.11). The pre-registered "≥ 2/3 positive" is reported but is uninformative (null 0.67).

## Results by goal period
Verdict rule with amendment A1 (written in every G card before its run). Replication: **3 supported, 10 mixed, 14 failed, 5 n/a**. Natives: G26 failed, G35 supported, NE42 mixed.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | n/a | regime I, 174 test ideas (< 300 or < 20 positive) |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | failed | regime I, 964 test ideas (underpowered); ΔLL(F − B4) -12.2 [-24.5, -0.5] millinats/idea; AUC F 0.59 vs B4 0.61, B1 0.51; lift 1.75 |
| [G07](goalperiod-subhypotheses/G07/README.md) | replication | n/a | regime I, 0 test ideas (< 300 or < 20 positive) |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | supported | regime I, 1357 test ideas (underpowered); ΔLL(F − B4) +11.8 [+3.1, +21.4] millinats/idea; AUC F 0.63 vs B4 0.50, B1 0.57; lift 1.78 |
| [G10](goalperiod-subhypotheses/G10/README.md) | replication | n/a | regime I, 117 test ideas (< 300 or < 20 positive) |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | mixed | regime I, 317 test ideas (underpowered); ΔLL(F − B4) +20.7 [-30.2, +76.1] millinats/idea; AUC F 0.64 vs B4 0.47, B1 0.71; lift 1.42 |
| [G12](goalperiod-subhypotheses/G12/README.md) | replication | failed | regime I, 625 test ideas (underpowered); ΔLL(F − B4) -72.8 [-116.5, -31.9] millinats/idea; AUC F 0.45 vs B4 0.46, B1 0.54; lift 0.61 |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | failed | regime I, 963 test ideas (underpowered); ΔLL(F − B4) -8.9 [-22.6, +4.1] millinats/idea; AUC F 0.57 vs B4 0.55, B1 0.50; lift 1.27 |
| [G16](goalperiod-subhypotheses/G16/README.md) | replication | failed | regime I, 569 test ideas (underpowered); ΔLL(F − B4) -62.0 [-137.8, -9.1] millinats/idea; AUC F 0.69 vs B4 0.50, B1 0.37; lift 0.77 |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | n/a | regime I, 131 test ideas (< 300 or < 20 positive) |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | failed | regime I, 2865 test ideas; ΔLL(F − B4) -37.2 [-125.8, +22.1] millinats/idea; AUC F 0.51 vs B4 0.55, B1 0.56; lift 1.69 |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | failed | regime I, 2096 test ideas (underpowered); ΔLL(F − B4) -0.9 [-7.7, +5.4] millinats/idea; AUC F 0.66 vs B4 0.65, B1 0.54; lift 1.98 |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | failed | regime I, 2657 test ideas; ΔLL(F − B4) -6.4 [-15.6, +2.5] millinats/idea; AUC F 0.63 vs B4 0.62, B1 0.50; lift 2.04 |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | mixed | regime I, 1244 test ideas (underpowered); ΔLL(F − B4) +23.3 [-12.3, +52.9] millinats/idea; AUC F 0.66 vs B4 0.55, B1 0.51; lift 2.25 |
| [G23](goalperiod-subhypotheses/G23/README.md) | replication | failed | regime I, 564 test ideas (underpowered); ΔLL(F − B4) -0.8 [-12.2, +10.9] millinats/idea; AUC F 0.68 vs B4 0.69, B1 0.54; lift 4.03 |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | mixed | regime I, 1751 test ideas (underpowered); ΔLL(F − B4) +3.3 [-4.7, +11.6] millinats/idea; AUC F 0.61 vs B4 0.57, B1 0.47; lift 1.93 |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | mixed | regime I, 1633 test ideas (underpowered); ΔLL(F − B4) +20.4 [-12.9, +59.2] millinats/idea; AUC F 0.62 vs B4 0.53, B1 0.54; lift 2.27 |
| [G26](goalperiod-subhypotheses/G26/README.md) | native + replication | failed (native); failed (replication) | regime I, 690 test ideas (underpowered); ΔLL(F − B4) -19.4 [-38.7, -2.4] millinats/idea; AUC F 0.62 vs B4 0.63, B1 0.53; lift 0.95 |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | failed | regime I, 4840 test ideas; ΔLL(F − B4) -0.7 [-7.8, +6.4] millinats/idea; AUC F 0.61 vs B4 0.62, B1 0.57; lift 1.91 |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | mixed | regime I, 1356 test ideas (underpowered); ΔLL(F − B4) +4.5 [-11.5, +20.5] millinats/idea; AUC F 0.66 vs B4 0.60, B1 0.54; lift 1.93 |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | mixed | regime I, 2142 test ideas (underpowered); ΔLL(F − B4) +10.2 [+0.7, +19.6] millinats/idea; AUC F 0.59 vs B4 0.51, B1 0.46; lift 1.39 |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication | failed | regime II, 1158 test ideas (underpowered); ΔLL(F − B4) -3.4 [-19.0, +12.0] millinats/idea; AUC F 0.48 vs B4 0.44, B1 0.51; lift 1.07 |
| [G35](goalperiod-subhypotheses/G35/README.md) | native + replication | supported (native); failed (replication) | regime II, 1682 test ideas (underpowered); ΔLL(F − B4) -6.6 [-15.5, +2.1] millinats/idea; AUC F 0.62 vs B4 0.63, B1 0.54; lift 2.09 |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | mixed | regime III, 2531 test ideas; ΔLL(F − B4) +5.1 [-6.2, +15.5] millinats/idea; AUC F 0.58 vs B4 0.51, B1 0.39; lift 1.19 |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | n/a | regime III, 145 test ideas (< 300 or < 20 positive) |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | supported | regime III, 6625 test ideas; ΔLL(F − B4) +6.3 [+3.0, +9.7] millinats/idea; AUC F 0.80 vs B4 0.79, B1 0.68; lift 3.52 |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | mixed | regime III, 2061 test ideas (underpowered); ΔLL(F − B4) +6.2 [-8.1, +19.2] millinats/idea; AUC F 0.64 vs B4 0.57, B1 0.51; lift 2.23 |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | mixed | regime III, 4066 test ideas; ΔLL(F − B4) +14.2 [-0.5, +28.4] millinats/idea; AUC F 0.62 vs B4 0.61, B1 0.58; lift 1.19 |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | mixed | regime III, 3295 test ideas; ΔLL(F − B4) +0.5 [-3.1, +4.1] millinats/idea; AUC F 0.65 vs B4 0.65, B1 0.50; lift 1.45 |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | failed | regime III, 2473 test ideas (underpowered); ΔLL(F − B4) -10.4 [-18.0, -3.6] millinats/idea; AUC F 0.49 vs B4 0.49, B1 0.45; lift 1.28 |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | failed | regime III, 1423 test ideas (underpowered); ΔLL(F − B4) -21.2 [-50.6, +3.2] millinats/idea; AUC F 0.71 vs B4 0.71, B1 0.43; lift 2.08 |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication | supported | regime III, 47748 test ideas; ΔLL(F − B4) +5.5 [+4.1, +7.1] millinats/idea; AUC F 0.70 vs B4 0.69, B1 0.58; lift 2.54 |
| [NE42](goalperiod-subhypotheses/NE42/README.md) | native | mixed | #39 → #40 transfer ΔLL +33 [+22, +44]; #40 → #41 −298 [−343, −258] (room-size extrapolation); receptive-count sign unstable |

## Outcome vs prediction
| # | Prediction (19:15 UTC; A1–A2 19:30 UTC) | Outcome | Verdict |
| --- | --- | --- | --- |
| P1 | ΔLL(F − B4) CI > 0 in ≥ 1/2 of eligible periods; pooled > 0 | 4/27 (powered: 2/8: G38, G51); point > 0 in 13/27; pooled +0.1 ± 1.6 millinats (τ² large); vs B3 3/27 | **fail** |
| P2 | AUC_F > AUC_B1 in ≥ 2/3; median gain ≥ 0.05 | 23/27; median +0.11; but AUC_F − AUC_B4 median +0.01 | pass as written; the gain is poster identity |
| P3a | focus < 0 in ≥ 2/3 (CI < 0 in ≥ 1/2) | 19/27 negative; CI < 0 in 7/27; pooled −0.08 ± 0.03 | partial |
| P3b | receptive fraction > 0 in ≥ 1/2 (CI > 0 in ≥ 1/3) | 14/27 positive; CI > 0 in 4/27; pooled +0.004 ± 0.023 | **fail** |
| P3c | poster reply in-degree CI ∋ 0 in ≥ 2/3 | 18/27; pooled +0.04 ± 0.04 | pass |
| P3d | specificity < 0 in ≥ 1/2 | 21/27; CI < 0 in 8/27; pooled −0.08 ± 0.02 | pass |
| P4 | top-decile lift ≥ 2 in ≥ 2/3 | 9/27; median 1.78 (reach ≥ 3: 1.94) | **fail** |
| P5 (A2) | pooled G_read − G_unread lower CI > +0.011; per-period CI > 0 in > 1/3 | 7 testable periods; pooled −0.004 ± 0.028; CI > 0 in 0/7 | **inconclusive** (unread-5 adopters ≈ 1%) |

Prior credences: P1 0.55, P2 0.7, P3a 0.6, P3b 0.5, P3c 0.6, P3d 0.4, P4 0.6, P5 0.45.

## Results
`analysis/explore.py` writes `data/processed/H61-contagiousness-at-first-use/results/{periods.json, period_table.parquet, summary.json}`; `analysis/natives.py` writes `results/natives.json`. Figures are in `figures/summary_obs.pdf` and `figures/summary_obs2.pdf`.

**1. The fitness of an idea is mostly not visible at its first use.**
- **Scale:** 27 eligible periods; 99,695 held-out ideas on forward-chained test days.
- **Base rate:** 15% of ideas reach a second agent within 24 h (median period).
- **Skill:** the seed-feature model F ranks ideas better than class alone (AUC 0.62 vs 0.53). Almost all of that skill is already in who posted the idea and whether it is the kickoff day (B4 AUC 0.57, B3 0.60).
- **Held-out log score:** F beats B4 in only 4/27 periods. The pooled gain is +0.1 ± 1.6 millinats per idea, with large between-period variance.
- **Where it works:** the two big regime-III swarms (G51 +5.5, G38 +6.3 millinats; AUC 0.70 and 0.80; top-decile lift 2.5 and 3.5). There, a few thousand test ideas give power.
- **Where it fails:** in small regime-I periods the fitted coefficients do not transfer from day to day. Several periods lose (G12 −73, G16 −62, G42 −10).

**2. Message-level dilution is the replicated signal.** Standardised log-odds, pooled over 27 periods (random effects), in-sample:
- **Seed length:** −0.26 ± 0.04; CI < 0 in 16/27.
- **Novel load (focus):** −0.08 ± 0.03; 19/27 negative.
- **Distance from the kickoff field:** −0.08 ± 0.02; 21/27 negative.
- **Threaded seeds** (the seed message is a DQ2 reply): +0.10 ± 0.02; 24/27 positive.

An item buried in a long announcement or a list of coinages spreads less than one stated alone in a reply. This is the per-message analogue of H18's attention dilution. **Authority and timing carry nothing:** poster reply in-degree +0.04 ± 0.04, receptive fraction +0.00 ± 0.02, room size +0.04 ± 0.04.

**3. Contagiousness vs co-generation cannot be separated here.** Unread-5 adopters are rare: 76 of 10,978 adopters in G51, 0–35 elsewhere. The in-flight placebo is therefore testable in 7 periods only, and it finds nothing either way (pooled −0.004 ± 0.028).

**4. Natives.**
- **G26 (DQ6 elected leader; failed).** During the leader's term, its 696 ideas spread at OR 0.22 [0.12, 0.39] relative to the other agents'. The leader averages 32.5 novel items per seeding message vs 4.7 for the others. Adjusting for every seed feature leaves OR 0.28 [0.09, 0.53]. The deficit is a property of the leader's messages beyond length and load, consistent with H32's "leaders are not content sources".
- **G35 (DQ6 lead designers; supported).** Lead-day seeds: raw OR 1.22 [0.82, 1.70]; with features and poster identity, 1.39 [0.86, 2.35]. A designated role adds no detectable fitness.
- **NE42 (mixed).** The #39 model forecasts the merged week #40 better than B3 (+33 [+22, +44] millinats) and predicts its higher spread rate (0.127 vs observed 0.155; B3 0.077). Fitted on #40, it fails badly on #41 (−298 millinats; predicted 0.023 vs observed 0.212). The room-size and receptive-count terms extrapolate across the split. The receptive-count coefficient changes sign (−0.25, +0.04, +0.13).

**Model- and style-dependence.** Specificity uses bge (primary) and gte (variant). The F − B4 gain is CI > 0 in 4/27 periods with bge and 5/27 with gte (G40 added). No result depends on style.

**Operator reading.** If you want an item picked up, post it alone, short, and as a reply. In the largest swarm (#51), long multi-item announcements are the measurable drag: −0.24 log-odds per SD of length. Do not rank ideas or agents by reply in-degree or by who is awake to read; neither predicts spread.

## Caveats
- Ideas are hashed markers (H34 rule). Message length and novel load partly measure how H34's rule fires: long reports and code dumps coin many low-value N markers.
- Reach counts co-generated uses. The in-flight placebo lacks power, so "fitness" includes field-driven co-production.
- The seed-message cluster bootstrap treats days as exchangeable within a period. Per-period verdicts are replications of one estimator, not independent tests.
- Coefficients are in-sample on all days; only ΔLL, AUC and lift are held out.
- Some working timestamps were first written ahead of the real clock and were corrected from file times (Notes).

## Confirmatory predictions (frozen 2026-10-04 after round 1, before any holdout use; `analysis/confirm.py`, not run)
- **Targets:** T1 = #51 tail (primary; models trained on non-holdout #51); T2 = #15 and T3 = #28 (forward chaining inside each).
- **C1:** T1 ΔLL(F − B4) lower CI > 0.
- **C2:** T1 AUC_F − AUC_B1 ≥ 0.05 and lift ≥ 1.5.
- **C3:** T1 focus and seed-length coefficients both < 0 with CI < 0 (the dilution law).
- **C4:** T2 and T3 lower CI ≤ 0 (no gain in small regime-I periods; descriptive).
- **C5:** T1 G_read − G_unread lower CI > +0.011 (expected inconclusive).
- **Verdict:** supported if C1 and C2 pass; the dilution law is confirmed if C3 passes.
- **Disclosure:** #51 tail, #15 and #28 are also targets of H34's unrun script (same marker modality, different statistic). The script calls `holdout_ledger.check()`.
- **Dry run on stand-ins** (`results/confirm_dryrun.json`; non-holdout, already seen). T1 stand-in = #51 08-24 → 09-04 scored with a model trained on earlier #51 days:
  - C1 **fails**: +2.9 [−0.6, +6.4] millinats;
  - C2 passes: AUC gain +0.08, lift 2.1;
  - C3 **fails**: focus −0.23 ± 0.04, but seed length −0.01 ± 0.05;
  - C4 passes (#13, #25).

  The frozen predictions are kept as written. The stand-in shows they are fragile, even on data the round-1 estimates partly came from.
- The script refuses without both flags (checked).

## Round 2 redirects (2026-10-04)
*Proposed by the round-1 agent; the coordinator may revise.*
- **H61-R1.** Fitness with per-agent pooling across periods (exception (b): check that poster effects are invariant first). Poster identity carries most of the skill, so the question is whether it is an agent-level constant.
- **H61-R2.** Within-message position: is an item spread less because the message is long, or because it sits late in it? This needs marker offsets inside the message (the H34 rule plus positions).
- **H61-R3.** A powered convergence test: pool unread-5 adopters across periods with a hierarchical model, or use a longer in-flight window, so that co-generation can be separated from transmission.
- **H61-R4.** The leader anomaly (G26): what in the leader's messages lowers uptake beyond length and load? Candidates are announcement templates and lists of instructions.

## Notes
- 2026-10-04 19:15 UTC: round-1 agent wrote definitions, observables, nulls, impostor table and predictions before any real-data outcome.
- 19:18–19:30 UTC: features built (no outcome read), synthetic S1–S3 run twice, amendments A1–A2 written; period predictions first written 19:26 and rewritten with natives at 19:30. Real-data replication began after 19:30 (first attempt crashed on a test-set alignment bug in the P5 code; fixed and re-run from 19:36).
- **Timestamp correction (19:42 UTC):** the agent first wrote estimated clock times (19:58, 20:05, 20:10 UTC) into the period READMEs and the card; these were ahead of the real clock and were replaced with file modification times. The order of events (predictions → synthetic → amendments → real data) is unchanged.
- New shared code: `infra/shared/idea_ledger.py` (verified against H34 r1b first-use status) and `infra/shared/idea_markers.py` (verbatim copy of the H34 marker rule; verified identical).
- Proposed for DEFINITIONS.md: *Idea reach (24 h)*, *Seed features (H61)*, *Focus (novel load)*, *Specificity (goal distance)*, *Poster reply in-degree (causal)*, *Receptive fraction (5 min)*, *Read-5 / unread-5 adopter*.
