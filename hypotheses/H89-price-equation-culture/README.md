# H89: Price equation for village culture

**Status:** **exploratory round 1 done (2026-10-04, non-holdout only). Mixed: content moves by transmission and selection is small, as predicted; style moves by migration more than content but transmission still dominates it; no village attractor.**
- **Content transmission share 0.98** (median over 33 periods, both embedding models; 33/33 ≥ 0.5); migration 0.004, \|selection\| 0.010. Conventions behave like content.
- **Style:** migration share 0.044 (max 0.29), above content's in 21/26 periods with turnover, but never the largest term (P1(b) 0/33). Implied day-field fraction: style 0.07, content 0.32.
- **Selection:** at the chance rate against its permutation null; synthetic shows it is not detectable in vector traits at village counts. Copying is not separable from a field (social share ratio 1.02).
- **Kill does not fire** (R 0.92; kickoff share 0.04), but **no attractor:** persistence C −0.28, > 0 in 0/29 periods.
- Natives: NE29 supported, NE32 supported, #51 growth failed (the net style change is not the newcomers).
- Card and predictions written 2026-10-04 20:15 UTC before any Price statistic; amendments A1–A5 after the synthetic (20:30). Scorecard A1 B1 C1 D1 E1 F1 G1 H1 I1. `analysis/confirm.py` frozen and dry-run, **not run**.
**Question (GOALS.md):** **Q3** (is there collective order beyond fields?): it splits the change of the village's mean trait into selection, transmission and migration, and asks whether anything is left after migration and the kickoff field. It also serves **Q2** (field vs coupling: transmission lumps both).
**Fields:** sociophysics, cultural evolution, stat mech
**Literature:** none filed for Price (Price 1970†; El Mouden et al. 2014† for cultural parentage weights; both from memory, not in `literature/`). Project cards used: H34 (idea marker rule, in-cone first uses), H41 (logged light cone), H61 (spread is not forecastable beyond the poster), H62 (reply premium, thread field), H46 and H73 (style is an agent constant, u_A 0.55), H29 (named messages pull).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Population N(t) and its **active population** variant; Regime; Driving / external field (kickoff); **Idea (H34 marker rule)**; **Interaction (ledger-visible exposure)** and **Unread (in-flight) exposure placebo** (RE-D1); H41's **logged light cone**; H46's **agent state (vector, chat agent-day, style-residualized)** (DQ5 `style_resid_period`). New named variants proposed for DEFINITIONS.md (not edited here; see "Operational definitions"): **cultural parentage (in-cone adoption)**, **cultural fitness w (Price)**, **Price shares s_Sel, s_Trans, s_Mig (cross-fitted)**, **agent state (style, chat agent-day, raw 20)**, **agent state (convention use, agent-day)**.
**From:** HH313 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/13-cultural-evolution-conventions/` (primary, sub-model 3 "Price equation"), `physics-models/05-replicator-dissipation/` (secondary: selection as replicator dynamics), `physics-models/06-neutral-cooperative-dynamics/` (named on the stub; the neutral null is the w-permutation here)

## Source HH (verbatim from the HH list, including literature refinements)
A Price equation for village culture: selection, transmission and migration. For a cultural trait z, use Δz̄ = Cov(w, z)/w̄ + E(w Δz)/w̄ + migration. The trait can be a culture-vector projection (HH293) or a convention's use (HH291). w is the number of agents who adopt from i inside the logged light cone (H41).
  - The migration term is roster in/out flow.
  - *Predictions:*
    - Style: migration dominates; it is a charge (H46).
    - Content: transmission bias dominates, as convergence to the field.
    - Selection (differential influence): small, carried by named messages (H29), at most ~20% of Δz̄.
  - *Egregore reading:* a transmission bias toward a village-specific attractor that persists across migration events.
  - *Kill:* migration plus kickoff explain Δz̄ fully.
  - *Models:* 05, 06 · *Builds on:* H41, H46, H29, HH293

## Question
When the village's mean trait changes from one day to the next, how much of the change is migration (who is present), selection (influential agents carry different traits) and transmission (agents change, by copying or by fields)? Does the split differ between style, content and conventions as HH313 predicts?

## Design: two layers (Vivian, 2026-10-04)
- **Replication:** the common Price estimator on every eligible non-holdout goal period, role `replication`.
- **Period-native tests** (`natural-experiments.md`, `period-affordances.md`), each with its own dated prediction, role `native`:
  - **NE29** (#31, 02-18 / 02-19): the longest-serving agent retires the day after a newcomer joins. A clean single-carrier loss.
  - **NE32** (#51, 07-09 / 07-10): three same-family newcomers start in isolated rooms and merge the next day. Isolation switches the newcomers' cultural parentage off, then on.
  - **G51 growth** (#51, 07-06 → 09-04, non-holdout): 11 roster joins into one long period. The strongest test of "style moves by migration".
- **Faithfulness lever:** the Price equation is an identity, so the test is in the partition. Axes F (cross-fitted shares recover a planted split at real counts) and H (the split differs by trait type as predicted) carry the weight.

## Model
**From:** `physics-models/13-cultural-evolution-conventions/`, sub-model 3. H89 variant: **a cultural Price equation with in-cone parentage and open-population migration.**

*Degrees of freedom.* A trait vector z_i(d) per agent i and day d (three trait types, below). Generations are consecutive active days d → d′ of one goal period (overlapping generations; a day is one read-out-dominated generation of chat). The population is the active population A_d.

*Cultural parentage (in-cone adoption).* Stayer j's day-d′ trait descends from itself and from the agents it adopted ideas from inside the logged light cone. j's social weight λ_j is the share of j's first uses of period ideas on d′ that are in-cone adoptions with at least one stayer source. The social weight is split over the sources by adoption counts (an adoption with k visible stayer sources gives 1/k to each). Parentage: α_jj = 1 − λ_j, α_ji = λ_j a_ji / Σ_i a_ji.

*Fitness.* w_i = Σ_j α_ji: one unit of self-continuity, minus what i took from others, plus its fractional in-cone adopters (HH313's "agents who adopt from i inside the cone", counted fractionally). Σ w_i = |S|, so w̄ = 1.

*The identity.* With S = A_d ∩ A_d′ (stayers), E = A_d \ A_d′ (leavers), I = A_d′ \ A_d (entrants):

  Δz̄ = z̄_A(d′) − z̄_A(d) = Sel + Trans + Mig_out + Mig_in
  - Sel = Cov_S(w, z(d)) (w̄ = 1): influential stayers carry different traits.
  - Trans = E_S(w Δz), Δz_i = z′_i − z_i(d), z′_i = Σ_j α_ji z_j(d′)/w_i: descendants differ from their parents. Fields (kickoff, day topic) act here.
  - Mig_out = −(1/|A_d|) Σ_{i∈E} (z_i(d) − z̄_S(d)); Mig_in = (1/|A_d′|) Σ_{j∈I} (z_j(d′) − z̄_S(d′)).
  The identity is exact for every vector trait (componentwise).

*Linear sub-splits* (each exact):
- Mig = Mig_roster + Mig_presence. Roster = the agent joined the roster after d (entrant) or left it by d′ (leaver), per `roster.joined/left`; presence = on the roster both days but silent (below threshold) on one.
- Sel = Sel_self + Sel_named + Sel_unnamed, from w = w_self + w_named + w_unnamed (an adoption is *named* if at least one visible source message names the adopter, `chat_mentions_clean.mentions_roster`).
- Trans = Trans_self + Trans_social.
- For content: Sel + Trans = its component along the period's kickoff direction ĝ (Trans_kick) + the orthogonal rest.

*Rivals.*
- **R0, composition only (kill clause):** Δz̄ = migration + kickoff field; nothing else.
- **R1, field only:** all non-migration change is a common shift of every stayer (a day field); parentage is irrelevant (Sel at its permutation null, Trans_social ≈ λ̄ × Trans_self direction).
- **R2, selection-driven culture:** influential agents' traits spread: |s_Sel| > 0.2.
- **R3, contemporaneous convergence:** parentage from posted-but-unread uses gives the same Sel and Trans_social as read parentage.

## Operational definitions (written 2026-10-04 20:15 UTC, before any real-data Price statistic)
- **Eligible message:** non-holdout agent chat in the period (`chat_core`, speaker_kind agent), Claude Code agent (19) excluded, DQ5 copies (`statement_flags.self_repeat_both`) dropped.
- **Split halves:** each eligible message goes to half A or B by a fixed hash of its message_id (SHA-1, last bit). Every trait is computed per agent-day per half and on the whole.
- **Active population A_d:** agents with ≥ 6 eligible messages on PT day d and ≥ 2 in each half.
- **Traits (three types):**
  1. **Content:** the mean of the agent-day's chat statement vectors, DQ5 `statements_style_resid_period32` (bge-small primary; gte-modernbert variant). 32-d, whitened per regime; style removed.
  2. **Style (agent state, chat agent-day, raw 20):** H13's 20 numeric features (`text_features` f_*), winsorized at the non-holdout 0.1% / 99.9% quantiles and z-scored on non-holdout messages (a shared ruler, exception (a)); the agent-day mean.
  3. **Conventions (agent state, convention use):** the period's 50 N-class ideas (H34 marker rule, cls N) with the most distinct agent users on non-holdout days; z_ik(d) = the share of i's eligible messages on d that use idea k.
- **Parentage inputs:** `infra/shared/idea_ledger.py` (H34 round-1b ledger visibility, verified against H34): for each period idea and each non-seed agent first use u by agent j, the *visible sources* are the senders of earlier agent uses with TS[use, j] ≤ cs[u] (read by j's producing call). An *in-cone adoption* has ≥ 1 visible agent source. The **unread placebo**: a first use with no visible source but ≥ 1 earlier agent use posted the same PT day before u and not yet read (in flight); its placebo sources are those senders. Human and automated sources do not count (exogenous); sources outside S are dropped from the parentage and counted (`ext_share`).
- **Leave-trait-out parentage (conventions):** for the convention trait, the parentage is also rebuilt without the 50 trait ideas (variant), so that selection is not the adoption of the trait itself.
- **Cross-fitted shares.** For each transition t and term X: X_t^A, X_t^B from half-A and half-B traits (same parentage). The **energy share** s_X = Σ_t ½(⟨X_t^A, Δ_t^B⟩ + ⟨X_t^B, Δ_t^A⟩) / Σ_t ⟨Δ_t^A, Δ_t^B⟩. Message sampling noise is independent between halves, so it drops out of every inner product in expectation. Shares sum to 1. The **cumulative share** uses X_cum = Σ_t X_t in place of the per-transition sums (the net change over the period). **Reliability** ρ_Δ = Σ_t ⟨Δ^A, Δ^B⟩ / √(Σ|Δ^A|² Σ|Δ^B|²); if the denominator Σ⟨Δ^A, Δ^B⟩ ≤ 0 the period has no reliable change and its shares are n/a.
- **Uncertainty:** jackknife over agents (leave one agent out of every population and of all parentage, recompute), `ci_kind` = jackknife_z.
- **Kickoff direction ĝ:** `goals.parquet` kind `kickoff` for the goal (fallback `goal`), whitened with the regime's 32-d whitener of that embedding model, unit-normalized. s_kick = the share of Trans_kick + Sel_kick (components along ĝ). **Residual R** = s_Sel + s_Trans − s_kick: non-migration change orthogonal to the kickoff field.
- **Attractor persistence C:** for consecutive transitions, the cross-fitted cosine between the non-migration, non-kickoff change vectors of t and t+1 (half A of one with half B of the other, symmetrized), averaged over pairs. C > 0: the transmission keeps pointing one way (an attractor); C ≤ 0: day-to-day topic swings.
- **Eligibility (replication):** non-holdout period with H34 ideas, ≥ 2 transitions with |S| ≥ 3, and ≥ 20 in-cone adoptions by stayers over its transitions.

## Data scheme (`scheme/`)
Script: `scheme/build.py` (shared tables only; no text read; holdout rows dropped by `calendar.holdout` and `common.holdout_mask`, asserted).
- **Inputs:** `chat_core` (via `idea_ledger.Base`), DQ1 ledger through `idea_ledger.load_period` (`context_ledger_items`, `call_windows`), H34 markers (`data/processed/H34-idea-cascades/markers/`, hashes), `chat_mentions_clean`, DQ5 `embeddings/statements.parquet` + `statements_style_resid_period32_{bge_small,gte_modernbert}.npy` + `chat_index`, `statement_flags` (`self_repeat_both`), `text_features` (f_*), `roster`, `calendar`, `embeddings/goals.parquet` + `goal_vectors*.npy` + whiteners.
- **Transform:** per period: eligible messages → halves → agent-day traits (whole, A, B) for content (2 models), style, conventions; ledger first uses → adoption rows (adopter, day, sources, named flag, read vs unread placebo, in-trait flag); first-use counts per agent-day; kickoff directions.
- **Output:** `data/processed/H89-price-equation-culture/` (`traits/G<NN>.npz`, `adoptions.parquet`, `first_uses.parquet`, `agent_days.parquet`, `kickoff.npz`, `residual_pool.npz` for the synthetic check; analysis outputs in `synthetic/`, `replication/`, `natives/`, `confirm/`; `_provenance.json`).
- **Regimes covered:** I, II, III, non-holdout days only.

## Observables
*Written 2026-10-04 20:15 UTC. Sampling facts already known from other cards (not computed here): H34/H41 adoption counts (45,183 in-cone adoptions over 32 periods), roster join and leave dates, period lengths.*
- **O1 Price shares per period and trait:** energy shares s_Sel, s_Trans, s_Mig (and sub-splits), cumulative shares, reliability ρ_Δ, jackknife CIs. Traits: content (bge, gte), style, conventions.
- **O2 Selection null:** permute w among stayers within each transition (500 draws); p for |s_Sel|.
- **O3 Convergence placebo:** Sel and Trans_social with unread-placebo parentage vs read parentage.
- **O4 Kill test:** s_kick, residual R (content, both models).
- **O5 Attractor persistence:** C (content), periods with ≥ 4 transitions.
- **O6 Named vs unnamed selection:** the named part's share of social selection vs its share of social weight.
- **O7 Natives:** below.

## Null / baseline
*Written 2026-10-04 20:15 UTC, before any real-data Price statistic.*
- **Noise floor:** the cross-fit removes message-sampling noise from the shares in expectation. The synthetic check measures its residual bias at real counts.
- **Selection null:** w permuted among stayers within a transition (keeps the fitness distribution, breaks its link to the trait). Its size is checked on synthetic data.
- **Convergence placebo:** unread (in-flight) parentage, same day, same idea.
- **Kill (R0):** Mig + kickoff component carry the whole change: R's CI includes 0.
- **Composition-only baseline for style:** stayers' style constant (Trans = Sel = 0).

## Impostor table (STANDARDS.md §1)
| Impostor | How it could fake this result | How H89 removes it | Status |
| --- | --- | --- | --- |
| Scheduler field | day-level presence follows the schedule, so presence "migration" and day-edge bursts could look like cultural flow | generations are whole PT days (no within-day edges); presence turnover is reported separately from roster migration | partly |
| Exogenous field (kickoff, goal, operator) | a common topic shift makes every stayer change: transmission without copying | Trans is split into its kickoff-direction component and the rest (R); Trans_self vs Trans_social; the field-only rival R1; human and operator sources are exogenous, not parents | partly (round 1: the kickoff direction carries 0.04; R1 is not rejected, so most of Trans is plausibly a day field) |
| Shared model priors (family, style) | family-shared content could covary with influence and look like selection | content uses `style_resid_period`; style is a separate trait; selection is tested against a w-permutation within transition | partly (no within-family selection split) |
| Contemporaneous convergence | co-generated terms look like in-cone adoptions and inflate parentage | parentage uses ledger visibility (read before the producing call); the unread placebo parentage is run side by side (O3) | open (round 1: median 8 placebo adoptions per period, too few; parentage changes nothing measurable anyway, see Results 4) |

## Prediction
*Written 2026-10-04 20:15 UTC, before running the analysis on real data. Verdict rules fixed now.*

**Replication (card level).**
- **P1 style moves by migration (HH: "style: migration dominates").** (a) s_Mig(style) > s_Mig(content, bge) in ≥ 2/3 of eligible periods with both shares defined (sign test p < 0.05). (b) s_Mig(style) is the largest of the three style terms in ≥ 1/2 of eligible periods. *Against:* (a) fails. My prior: 60% for (a), 40% for (b): H73 says style is an agent constant, but the day field also moves style (14% of κ).
- **P2 content moves by transmission (HH: "content: transmission bias dominates").** s_Trans(content) ≥ 0.5 and the largest term in ≥ 2/3 of eligible periods, for bge and for gte separately. *Against:* < 2/3 for either model. Prior 75%.
- **P3 selection is small (HH: "at most ~20%").** |s_Sel| ≤ 0.2 in ≥ 2/3 of eligible periods for each trait (content bge, style, conventions) and median |s_Sel| ≤ 0.2. *Against:* |s_Sel| > 0.2 in more than 1/3 of periods for any trait. Prior 80%. Note: |Sel| ≤ SD(w)·SD(z), and λ is small, so P3 is partly mechanical; the informative part is O2.
- **P4 selection beyond the null (descriptive, H29).** Count of periods with permutation p < 0.05 per trait; in those periods, read parentage |s_Sel| exceeds the unread placebo's (O3); the named part of social selection exceeds the named share of social weight in ≥ 1/2 of periods (O6). No verdict weight.
- **P5 kill test (HH kill).** R(content) ≥ 0.1 with jackknife CI > 0 in ≥ 2/3 of eligible periods (both models). *Kill:* R's CI includes 0 in ≥ 2/3 of periods (migration plus kickoff explain Δz̄). Prior 85% not killed. Passing P5 does not show an egregore: day topics are fields outside ĝ.
- **P6 egregore reading (attractor persistence).** C(content, bge) > 0 with CI > 0 in ≥ 1/2 of periods with ≥ 4 transitions. *Against:* C ≤ 0 in most periods (transmission is day-to-day topic swing, not drift toward a village attractor). Prior 35%.

**Overall reading (fixed now).** H89's HH is **supported** if P1(a), P2 and P3 pass; **mixed** if one or two pass; **failed** if none. The egregore reading is reported separately: positive only if P5 and P6 both pass.

**Per-period verdict (replication):** supported = s_Mig(style) > s_Mig(content), s_Trans(content) ≥ 0.5 and largest, and |s_Sel| ≤ 0.2 for every trait; failed = none of the three holds; mixed = otherwise; n/a = not eligible or Σ⟨Δ^A, Δ^B⟩ ≤ 0 for content or style.

**Natives (exception (c): the transition is the object; dated predictions also in each folder).**
- **N1 NE29 (#31).** Sonnet 4.6 joins 02-18; Claude 3.7 Sonnet leaves 02-19. (a) At each roster-flow transition, the roster-migration share of style exceeds that of content (cross-fitted, that transition alone). (b) The stayers' content change at the retirement transition is not larger than at the placebo transitions of #30 and #31: cross-fitted |Trans + Sel|² percentile < 0.9. Prior 0.5. Supported = (a) at both transitions and (b); failed = neither; mixed otherwise.
- **N2 NE32 (#51).** GPT-5.6 Sol, Terra and Luna join on 07-09 in isolated rooms; the rooms close 07-10. (a) At 07-08 → 07-09 the roster-migration share of style exceeds that of content. (b) Enculturation at the merge: the newcomers' content change 07-09 → 07-10 points toward the veterans' 07-09 centroid (cross-fitted cosine > 0) and more so than their style change does. If a newcomer has < 6 eligible messages on 07-09, its first active day replaces 07-09. Prior 0.45. Supported = (a) and (b); failed = neither; mixed otherwise.
- **N3 G51 growth (#51, non-holdout 07-06 → 09-04; 11 joins).** (a) Cumulative roster-migration share of style ≥ 0.5. (b) Cumulative roster-migration share of content (bge and gte) < that of style. (c) Energy |s_Sel| ≤ 0.2 for every trait. Prior 0.55. Supported = (a) and (b); failed = neither; mixed otherwise. (c) is reported, not voted.

## Synthetic validation (axis F; run 2026-10-04 20:11–20:24 UTC, before any real-data Price statistic)
`analysis/synthetic.py` → `data/processed/H89-price-equation-culture/synthetic/synthetic.json`. Village sampling: the real active populations, roster flow, per-half message counts and in-cone parentage of G12, G20, G31 (regime I), G38 and G51 (regime III). Message noise: each agent's own real message residuals from its agent-day means, resampled. Planted noise-free traits at the period's real between-agent-day signal variance v (the only quantity read from real traits). Truth = the same estimator on the noise-free traits. 60 replicates per cell (40 for permutation tests, 200 permutations; 20 for jackknife coverage). Content-like = 32-d with content residuals; style-like = 20-d with style residuals.

| Check | Result |
| --- | --- |
| Identity | exact on all 247 real transitions (asserted) |
| Static agents, no field (S0): true s_Mig = 1 | cross-fit recovers it where change is reliable (G38, G51: bias ≤ 0.04); where migration is tiny (G20, G31) the ratio is unstable (bias +0.5 to +1.6) at reliability ρ 0.06–0.20 |
| Day-field fraction φ of the agent-day signal → true energy s_Mig | φ = 0.01: 0.16–0.56; 0.03: 0.06–0.29; 0.10: 0.02–0.10; 0.50: 0.00–0.01 (G12 has no turnover: 0). s_Mig is a steep gauge of the field fraction. |
| Naive (no cross-fit) bias toward transmission | +0.33 to +0.87 at φ = 0; +0.05 to +0.23 at φ = 0.01; < 0.01 at φ ≥ 0.1. Cross-fit bias ≤ 0.03 wherever ρ ≥ 0.3 (one G12 cell with no turnover and φ = 0.01: ratio blow-up) |
| Copying by the real parentage (S2) | indistinguishable from a field in the shares (Trans 0.98–1.00) |
| Planted selection along one axis, β = 1, 3, 6 √v per SD of w (S3) | true energy s_Sel stays 0.00: one axis of selection is negligible against a 20–32-d day field |
| Selection tests, size (S1, no selection) | energy-share permutation 0.00–0.05 (valid); cumulative-share permutation 0.05–0.72 and magnitude test 0.05–0.40 (invalid: fitness is persistent across transitions, the per-transition permutation is too narrow) |
| Selection tests, power (S3x6) | energy 0.00–0.23 (no power); magnitude 1.00 (but invalid size) |
| Persistence C | iid day topics: −0.50 (true and estimated); drift energy 2× the fluctuation energy (S4): +0.25 (recovered exactly) |
| Static agents, true energy s_Sel vs cumulative s_Sel | energy ≈ 0.00–0.02; cumulative up to 1.5–2.2 (G51) with Trans = −Sel exactly: Sel and Trans cancel when stayers do not change |
| Jackknife coverage (95%) of s_Mig, s_Sel (G20, G38; S1w, S3x3) | 1.00 (conservative) |

Readings: (1) The energy shares are unbiased at real counts once the change is reliable. (2) The migration share measures how weak the trait's day field is: it reaches 0.5 only when the day field holds about 1% of the agent-day signal. (3) Selection in a vector trait is bounded far below 0.2 by the dimension and the small fitness spread (λ̄ 0.09–0.48), and no valid test has power to detect it. P3 is therefore near-mechanical, and P4 is descriptive. (4) C's null is −0.5, not 0: C > 0 needs a directed drift whose energy exceeds the day-to-day topic swing.

## Amendments (2026-10-04 20:30 UTC, after the synthetic validation, before any real-data Price statistic)
- **A1 (reliability).** A trait's shares count in P1–P6 only if its energy reliability ρ_Δ ≥ 0.3; otherwise the trait is n/a in that period (S0 shows unstable ratios below 0.3).
- **A2 (selection tests).** Only the energy-share w-permutation test is used (valid size). The cumulative and magnitude tests are reported nowhere as evidence (invalid size). P4 stays descriptive; a P3 pass is read as "selection is not a material share", not as "selection is absent".
- **A3 (implied field fraction, a derived constant).** For each eligible period, the noise-free calibration curve s_Mig(φ) (φ ∈ {0, 0.01, 0.03, 0.1, 0.3, 0.5}, real populations, 30 replicates) converts the observed energy s_Mig of each trait into an implied day-field fraction φ̂ (log-linear interpolation; φ̂ < 0.01 reported as "< 0.01"). It is a reading aid, not a test.
- **A4 (persistence reading).** From C = (δ² − s)/(δ² + 2s) (directed drift energy δ² per transition, topic swing energy s), report the implied drift ratio δ²/s = (1 + 2C)/(1 − C) next to C. P6 is unchanged.
- **A5 (cumulative shares).** Cumulative shares are descriptive only, except where a native pre-registered them (N3). For N3, the Sel–Trans cancellation (static agents give cumulative |s_Sel| up to 2) means (c) uses the energy share as written.

## Results by goal period
Roles: `replication` = templated layer-1 point (not an independent test); `native` = period-specific design. G51 carries the replication estimator inside its native README; its verdict here is the native one (N3).

| Period | Role | Verdict | Key numbers (energy shares) |
| --- | --- | --- | --- |
| [G02](goalperiod-subhypotheses/G02/README.md) | replication | n/a | 1 transition, 14 adoptions (not eligible) |
| [G03](goalperiod-subhypotheses/G03/README.md) | replication | mixed | s_Mig style +0.00 vs content +0.00; s_Trans content 0.99; s_Sel content +0.010; C -0.54 |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | supported | s_Mig style +0.10 vs content +0.00; s_Trans content 1.00; s_Sel content -0.005; C -0.34 |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | mixed | s_Mig style +0.00 vs content +0.00; s_Trans content 0.98; s_Sel content +0.019; C -0.28 |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | mixed | s_Mig style +0.00 vs content +0.00; s_Trans content 1.00; s_Sel content -0.004; C -0.46 |
| [G07](goalperiod-subhypotheses/G07/README.md) | replication | n/a | 1 transition, 10 adoptions (not eligible) |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | supported | s_Mig style +0.08 vs content +0.00; s_Trans content 0.99; s_Sel content +0.010; C -0.33 |
| [G10](goalperiod-subhypotheses/G10/README.md) | replication | supported | s_Mig style +0.07 vs content +0.06; s_Trans content 0.95; s_Sel content -0.010; C +0.20 |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | supported | s_Mig style +0.13 vs content +0.06; s_Trans content 0.94; s_Sel content -0.002; C -0.36 |
| [G12](goalperiod-subhypotheses/G12/README.md) | replication | mixed | s_Mig style +0.00 vs content +0.00; s_Trans content 1.00; s_Sel content -0.004; C -0.27 |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | mixed | s_Mig style +0.00 vs content +0.00; s_Trans content 0.99; s_Sel content +0.005; C -0.24 |
| [G16](goalperiod-subhypotheses/G16/README.md) | replication | mixed | s_Mig style +0.00 vs content +0.00; s_Trans content 1.00; s_Sel content +0.003; C -0.43 |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | supported | s_Mig style +0.13 vs content +0.08; s_Trans content 0.95; s_Sel content -0.028; C -0.39 |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | supported | s_Mig style +0.07 vs content -0.02; s_Trans content 0.99; s_Sel content +0.026; C -0.19 |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | supported | s_Mig style +0.05 vs content +0.00; s_Trans content 0.98; s_Sel content +0.014; C -0.34 |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | mixed | s_Mig style +0.02 vs content +0.02; s_Trans content 0.97; s_Sel content +0.014; C -0.17 |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | mixed | s_Mig style -0.00 vs content +0.05; s_Trans content 0.95; s_Sel content -0.002; C -0.15 |
| [G23](goalperiod-subhypotheses/G23/README.md) | replication | mixed | s_Mig style +0.00 vs content +0.00; s_Trans content 1.06; s_Sel content -0.061; C +0.05 |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | supported | s_Mig style +0.05 vs content -0.02; s_Trans content 1.01; s_Sel content +0.019; C -0.41 |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | supported | s_Mig style +0.27 vs content -0.00; s_Trans content 0.99; s_Sel content +0.008; C -0.21 |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication | supported | s_Mig style -0.00 vs content -0.02; s_Trans content 0.98; s_Sel content +0.035; C -0.22 |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | supported | s_Mig style +0.04 vs content +0.00; s_Trans content 0.97; s_Sel content +0.027; C -0.17 |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | supported | s_Mig style +0.12 vs content +0.00; s_Trans content 0.98; s_Sel content +0.012; C -0.36 |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | supported | s_Mig style +0.04 vs content +0.01; s_Trans content 0.98; s_Sel content +0.009; C -0.30 |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication | supported | s_Mig style -0.00 vs content -0.00; s_Trans content 1.03; s_Sel content -0.025; C -0.11 |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | supported | s_Mig style -0.01 vs content -0.01; s_Trans content 1.02; s_Sel content -0.009; C -0.31 |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | supported | s_Mig style +0.22 vs content +0.02; s_Trans content 0.98; s_Sel content +0.008; C -0.47 |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | supported | s_Mig style +0.02 vs content -0.01; s_Trans content 1.00; s_Sel content +0.002; C -0.61 |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | supported | s_Mig style +0.25 vs content +0.23; s_Trans content 0.76; s_Sel content +0.005; C -0.20 |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | mixed | s_Mig style +0.09 vs content +0.11; s_Trans content 0.92; s_Sel content -0.033; C -0.28 |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | mixed | s_Mig style +0.03 vs content +0.20; s_Trans content 0.82; s_Sel content -0.025; C -0.25 |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | supported | s_Mig style +0.24 vs content +0.00; s_Trans content 1.00; s_Sel content -0.001; C -0.35 |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | supported | s_Mig style +0.16 vs content +0.07; s_Trans content 0.91; s_Sel content +0.016; C -0.24 |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | mixed | s_Mig style -0.02 vs content +0.06; s_Trans content 0.97; s_Sel content -0.027; C -0.19 |
| [G51](goalperiod-subhypotheses/G51/README.md) | native | failed | N3: cumulative style roster share -0.14 [-0.34, +0.05]. Replication (supported): s_Mig style +0.29 vs content +0.19; s_Trans content 0.81; s_Sel content +0.002; C -0.27 |
| [NE29](goalperiod-subhypotheses/NE29/README.md) | native | supported | roster share style vs content: entry +0.164 vs +0.051, retirement +0.033 vs -0.002; stayer change at the retirement: percentile 0.00 of 7 placebos |
| [NE32](goalperiod-subhypotheses/NE32/README.md) | native | supported | newcomer entry share style +0.083 vs content +0.023; newcomers toward veterans: content cos +0.26 (gte -0.03), style -0.48 |

## Outcome vs prediction
*Run 2026-10-04 20:26–20:45 UTC (`analysis/replication.py`, `analysis/natives.py`). Non-holdout only. 33 eligible periods (G02 and G07 have one transition), 245 day transitions, 2,568 active agent-days, 36,313 in-cone adoptions by stayers. Every trait passes A1 (ρ_Δ ≥ 0.3) in every eligible period (median ρ_Δ: content 0.82, style 0.75, conventions 0.85).*

| Prediction | Observed | Verdict |
| --- | --- | --- |
| P1(a) s_Mig(style) > s_Mig(content) in ≥ 2/3, sign p < 0.05 | 21/33 (sign p 0.08). Seven periods have no entries or exits, so both shares are 0 (ties). Post hoc, ties excluded: 21/26 (p 0.001) | **fail** (narrow) |
| P1(b) migration is the largest style term in ≥ 1/2 | 0/33; median style s_Mig 0.044 (IQR 0.00–0.12), max 0.29 (G51) | **fail** |
| P2 s_Trans(content) ≥ 0.5 and largest in ≥ 2/3, both models | bge 33/33 (median 0.98); gte 33/33 (median 0.98) | **pass** |
| P3 \|s_Sel\| ≤ 0.2 in ≥ 2/3 for each trait | 33/33 for content, style and conventions; median \|s_Sel\| 0.010 / 0.032 / 0.012 | **pass** (near-mechanical, see synthetic) |
| P4 selection beyond the w-permutation null (descriptive) | p < 0.05 in 1, 3, 3, 3 of 33 periods (content bge, gte, style, conventions): the chance rate is 1.7. Named adoptions carry more than their weight share of social selection in 16/33 | descriptive: no selection beyond chance |
| P5 R ≥ 0.1 with CI > 0 in ≥ 2/3 (kill test) | 33/33 for both models; median R 0.92 (IQR 0.86–0.97); kickoff share 0.04 (IQR 0.02–0.10, max 0.31) | **pass** (not killed) |
| P6 persistence C > 0 with CI > 0 in ≥ 1/2 (egregore reading) | 0/29; median C −0.28 (IQR −0.36 to −0.20); C above the iid-topic value −0.5 (CI) in 17/29; drift ratio δ²/s 0.35 | **fail** |
| N1 NE29 | roster share of style > content at the entry (0.164 vs 0.051) and at the retirement (0.033 vs −0.002); stayer change at the retirement is the smallest of 8 transitions in #30–#31 | **supported** |
| N2 NE32 | newcomer entry share style 0.083 vs content 0.023 (energy-pooled over 3 entries); newcomers move toward the veterans in content (cos +0.26 bge, −0.03 gte) and away in style (−0.48) | **supported** (gte disagrees on N2-b) |
| N3 G51 growth | cumulative style roster share −0.14 [−0.34, +0.05]; content +0.02, conventions +0.11; energy \|s_Sel\| ≤ 0.04 | **failed** |

**Overall (pre-registered reading):** P2 and P3 pass, P1(a) fails narrowly, so H89's HH is **mixed**. The egregore reading is **rejected**: the HH's kill does not fire (R 0.92), but the non-kickoff change does not keep a direction (P6 0/29). Natives: 2 supported, 1 failed. Replication verdicts: 21 supported (including G51's replication point), 12 mixed, 2 n/a. Every mixed verdict fails only c1: seven by zero-turnover ties, five by a style–content migration reversal (G20, G21, G39, G40, G44). G51's folder carries its native verdict (failed).

## Results
**1. Content and conventions move by transmission; selection and migration are small.** Over 245 day transitions in 33 periods, the stayers' own change carries the day-to-day change of the village's mean content: median energy share 0.98 for both embedding models and for conventions. Migration carries 0.004 (IQR 0.00–0.06) and selection 0.010 in absolute value. Only the largest, most open periods have a visible migration share in content: G38 0.23, G40 0.20, G51 0.19.

**2. Style moves by migration more than content does, but transmission still dominates.** The style migration share exceeds the content share in 21 of the 26 periods with any turnover. Its median is 0.044 and its largest value 0.29 (G51). Converted through the synthetic calibration curve (A3), the implied day-field fraction of the agent-day signal is 0.07 for style (IQR 0.04–0.34), 0.32 for content (0.10–>0.5) and 0.20 for conventions. It is lower for style than for content in 17/26 periods. So style has a day field too. It is weaker than content's, but it is still strong enough to outweigh composition change inside a period: style migration would dominate only for φ ≲ 0.01. This is H73's day field (14% of the style ceiling) seen from the Price side.

**3. Selection is not detectable, and the design cannot detect it.** The w-permutation test rejects at the chance rate. The synthetic shows why: the fitness spread is small (λ̄ 0.28; SD of w 0.26), and one axis of selection is diluted among 20–32 dimensions of day-field change. The planted selection stays at an energy share of 0.00 even at 6√v per SD of w. P3 is therefore a bound from the design, not a discovery. Named adoptions carry 23% of the social weight and no more than their share of selection (16/33).

**4. Copying by in-cone adoption is indistinguishable from a field.** The social part of transmission carries exactly its parentage weight: s_Trans,social / (s_Trans · λ̄) = 1.02 (IQR 0.98–1.10) for content and 1.02 for style. Field-only rival R1 predicts 1. The synthetic copy scenario S2 (traits really inherited through the real parentage) also gives Trans ≈ 1, so the Price partition at day resolution cannot separate copying from a common field. The unread placebo is too sparse to help: a median of 8 placebo adoptions per period (337 in G51), with placebo shares ≈ 0.

**5. The kill does not fire, but the remainder is day-topic swing, not an attractor.** The kickoff direction carries a median 0.04 of the change (max 0.31), so migration plus kickoff leave R = 0.92. The non-kickoff change has persistence C = −0.28: above the iid-topic value −0.5 in 17/29 periods, below 0 in all 29. In the drift-plus-swing reading (A4), the directed drift energy is about 0.35 of the day-to-day swing. That fits slow topic drift (a random-walk-like field) plus daily swings. A village-specific attractor would need C > 0.

**6. Roster events (natives).** At the NE29 retirement and the preceding join, style moves by the roster event more than content does (0.164 vs 0.051; 0.033 vs −0.002). The stayers' content changes less at the retirement than at any of the seven placebo transitions. Losing the longest-serving agent does not perturb the others' content. At NE32, the newcomers' entry moves style more than content (0.083 vs 0.023). The first newcomer's next-day content moves toward the veterans' centroid (cos +0.26 with bge, but −0.03 with gte) while its style moves away (−0.48). Over #51's 11 joins (N3), the net style change of the period is not the newcomers: the cumulative roster share is −0.14 [−0.34, +0.05]. The cumulative Sel and Trans vectors of style are 4.4× the net change in norm and cancel (A5): influential agents keep a persistent style while stayers drift.

Figures: `figures/summary_obs.pdf` (style vs content migration shares per period; persistence C against the iid-topic value), `figures/summary_obsb.pdf` (synthetic calibration of s_Mig against the field fraction; noise bias, naive vs cross-fitted). Data: `data/processed/H89-price-equation-culture/` (`replication/replication.json`, `natives/natives.json`, `synthetic/synthetic.json`, `confirm/confirm_dryrun.json`). Estimates: 712 rows in `per_period_estimates` (hypothesis H89).

## Caveats
- **A day is a coarse generation.** Within-day copying and the day field share one transition; finer generations (read-out cycles) would make migration even rarer per step.
- **Presence is not roster.** Most migration is presence turnover (agents silent one day); roster migration is a small sub-share (style median 0.000, IQR 0.000–0.006).
- **The w spread is small by construction.** λ counts in-cone first uses of H34 ideas; agents whose adoptions are not marker-visible (paraphrase, artifacts) get no social weight.
- **The cumulative shares are not interpretable as causes.** With persistent fitness, Sel and Trans accumulate in opposite directions (G51 style: both ≈ 4.4× the net change).
- **N2 rests on one newcomer across the merge** (Terra); the other two pass the activity threshold only on 07-14 and 07-17. gte does not reproduce the content cosine.
- **The kickoff direction is one of 32.** Day topics outside it stay in Trans, so R is an upper bound on anything village-specific.

## Faithfulness scorecard
*Round 1, 2026-10-04.*
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R0 composition + kickoff (kill), R1 field only, R2 selection-driven culture, R3 contemporaneous convergence.
**Locked holdout used for confirmation:** none yet (`analysis/confirm.py`, dry-run only).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Traits from DQ5, `text_features` and H34 markers; parentage from the DQ1 ledger through `idea_ledger`; roster flow from `roster`. The generation (a PT day) and the activity threshold (≥ 6 messages) are choices; presence turnover dominates "migration". |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | The identity is exact on all 247 transitions. Overlapping generations: an adopter can read a source posted the same day. Static stayers make Sel and Trans cancel (synthetic S0), so selection is read only against its null. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | The kill rival R0 is beaten in 33/33 (R 0.92). Selection never beats its permutation null (chance rate). R1 (field only) is not beaten. No held-out-day test (an identity has no out-of-sample fit). |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | The style vs content migration ordering (21/26 with turnover; pre-registered form 21/33 fails narrowly); persistence C (0/29 > 0) and the field fractions (style 0.07, content 0.32) are unfitted readings. |
| E interventional | predicts the change across a natural experiment | 1 | NE29 and NE32 supported (style moves with the roster event more than content); #51 growth fails (the net style change is not the newcomers). |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Synthetic at real counts in five periods: shares unbiased (≤ 0.03) at ρ ≥ 0.3, naive bias found and removed, two invalid selection tests found, C calibrated. But selection has no power, and copying is not separable from a field (S2). Both embedding models agree on P2–P6. |
| G ground truth | agrees with known structure | 1 | Migration appears where the roster changes (NE29 entry and exit, NE32); retirement leaves stayers unperturbed. |
| H comparative | beats the named rivals | 1 | Beats R0 and R2; does not separate R1 (social share ratio 1.02) and cannot test R3 (median 8 placebo adoptions). |
| I transfer | holds in other same-mode periods, including the holdout | 1 | P2 and P3 hold in all 33 periods across regimes I–III; holdout not run. |

**Faithfulness lever.** The Price split is a measurement, not a mechanism: it confirms the HH's content and selection clauses, narrowly misses the style clause and rejects the egregore reading. It cannot raise H (copying vs field) at day resolution.

## Confirmatory predictions (written 2026-10-04 20:50 UTC after round 1, before any holdout use; `analysis/confirm.py`, dry-run only, **not run**)
Targets: #15, #22, #29 (regime I; each has a roster join inside), #34 = NE30 (Gemini 3 Pro → 3.1 Pro succession), the #51 tail. Dry run on stand-ins (#18, #20, #19, #31, #51 08-24 → 09-04): all C pass.
- **C1:** s_Trans(content) ≥ 0.5 and largest in ≥ 4/5 eligible targets, bge and gte.
- **C2:** \|s_Sel\| ≤ 0.2 for content, style and conventions in every eligible target.
- **C3:** s_Mig(style) > s_Mig(content) in ≥ 3/4 of targets with at least one entry or exit (the tie-excluded form; post hoc from round 1).
- **C4:** C(content) < 0 in every target with ≥ 4 transitions and median C > −0.5.
- **C5:** R ≥ 0.1 with CI > 0 in ≥ 4/5 targets. **C6 (NE30):** at the succession, style roster share > content's.
- Overall: CONFIRMED if C1, C2 and C3 pass.

## Round 2 redirects (2026-10-04)
- **H89-R1 (separate copying from fields):** a parent–offspring regression per transition: does j's day-d′ trait move toward its in-cone parents' day-d traits beyond the day mean, with unread parents as the placebo? This is Price's heritability term, which the day-level partition cannot resolve (synthetic S2).
- **H89-R2 (per-axis Price):** run the partition on single interpretable axes (the `goal_fields` directions, H13 style features one at a time, single conventions) so selection is not diluted by 20–32 dimensions of day field.
- **H89-R3 (cross-boundary Price, exception (c)):** run the split across goal switches with roster changes, where migration is large. Style should then be migration-dominated and content field-dominated.
- **H89-R4 (a valid selection null):** permute agent labels for the whole period (fitness trajectories kept), so the persistent-fitness inflation of the magnitude test goes away.

## Notes
- 2026-10-04 20:15 UTC: card written from the stub; HH313 and model 13 read; predictions fixed before any Price statistic.
- 2026-10-04 20:30 UTC: synthetic validation and amendments A1–A5, before any real-data Price statistic.
- 2026-10-04 20:35 UTC: period READMEs written with dated predictions (`analysis/write_period_cards.py --predict`).
- 2026-10-04 20:45 UTC: N2-a implementation detail: the three newcomer entries are pooled as energy (sum of numerators over sum of denominators), as in the card's energy share. A per-entry mean is undefined because one entry transition has negative cross-fitted style energy (ρ −0.17). Decided before reading the pooled value; the per-entry values are in the NE32 README.
- Holdout: masked by `idea_ledger` (`holdout_mask` + `calendar.holdout`, asserted in the build and again in `h89lib.load_period`). No held-out count was printed.
- Compute: one job at a time, 2 threads; the full round (build 7 s, synthetic 7 min, replication 35 s) stayed far inside STANDARDS §9.
