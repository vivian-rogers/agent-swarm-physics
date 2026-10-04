# H22: Private, conflicting goals make #51 a spin glass

**Status:** exploratory round 1 **done (2026-10-04): not supported; leans failed.**

The #51 content couplings are real but mostly positive, and same-role rivals co-move *more*, not less (the homophily rival). The balance index is indeterminate, and there are no collective metastable states. Observables, nulls and predictions were written 2026-10-04 00:15 UTC, and Amendment 1 (synthetic-based) at 00:42 UTC, both before any real-data run. The confirmatory script for the #51 tail is written, not run.
**Fields:** stat mech, sociophysics
**Origin:** HH102 (`../hypohypotheses/HYPOHYPOTHESES.md`; `../promotion-shortlist.md`)
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Population; Regime; Driving / external field; Interaction (broadcast); Agent state, variant vector, in H01's named form **agent state (vector), whitened statement mean**. H13's operational *talk spin* (+1 in a 1-min bin where `activity_bins.state == 4`, else −1). Five terms not yet in DEFINITIONS.md are defined below under Observables and proposed for the shared file: *coupling (content co-movement, within-day)*, *coupling (talk, excess)*, *frustration index (triangle)*, *balance index τ₃*, *overlap (day-to-day content)*.

## Question
In #51 each agent maximizes a privately assigned goal, and some goals conflict. Do the couplings between agents carry random signs, with frustration (unsatisfied triangles) well above shared-objective weeks? Couplings here means content alignment beyond the field, and talk coupling. Are the dynamics glassy: many metastable configurations, and overlaps between days that decay slowly and depend on history? Aging belongs to H20. Practical payoff: how mixed-motive swarms behave.

## Model
**From:** `physics-models/01-inverse-ising` (Sherrington–Kirkpatrick / spin-glass phenomenology: frustration, Edwards–Anderson overlap, P(q), SK phase diagram via moment matching, HH87), `11-vector-spins` (content as O(n) spins), `10-potts`. Block / mean-field statistics where pairwise inference is weak (H02); H05's `block_J` reused by import.

### The magnet dictionary (H22 variant)
| Magnet | Village (#51) | Dataset fields |
| --- | --- | --- |
| spin s_i(t) | what agent i is talking about in a 30-min window: an n = 32 vector spin | whitened (regime III, `load_whitener`), unit-normalized bge embeddings of i's own chat messages, averaged per window |
| uniform field h(t) | the day's shared topic: goal, kickoff, the day's events | day mean over agents, m_d |
| random static field h_i | i's private role, plus family and style | agent mean over the unit, H_i |
| coupling J_ij | "when i's topic moves, j's moves the same way (J > 0) or the opposite way (J < 0)", beyond both fields | co-movement of within-day fluctuations, minus the cross-day surrogate (below) |
| frustration | no assignment of positions satisfies every coupling around a triangle | sign of J_ij J_jk J_ki |
| replicas / overlap q | two days of the same swarm; how similar the configuration of positions is | q(d, d′) of day-demeaned agent-day states |

### Phases and their signatures (what separates them)
- **Paramagnet:** couplings indistinguishable from the noise floor. Positions are set by fields alone. With private roles this is a **random-field paramagnet**: positions are frozen (q_EA > 0) without any coupling. So frozen positions alone are *not* evidence of a glass (Imry–Ma / random-field Ising logic).
- **Ferromagnet:** mean coupling dominates the spread. In SK units J₀/J = √N·J̄/σ_J > 1. Signs mostly positive.
- **Mattis state / factions (structural balance):** signs mixed, but J_ij = ξ_i ξ_j |J_ij| for some ±1 labels ξ. A gauge transformation s_i → ξ_i s_i maps it onto a ferromagnet (Mattis 1976; Harary's balanced signed graphs). Negative couplings alone are therefore *not* glassiness. H21's debate antiferromagnet is of this kind.
- **Spin glass (SK):** couplings real (above noise), J₀/J < 1, signs **unbalanced**: frustration sits at the random-sign level. Toulouse (1977): frustration of a loop, the sign of its coupling product, is the gauge-invariant quantity. So it is what separates a glass from a disguised ferromagnet.
- **Gauge-invariant summary statistic:** the **balance index** τ₃ = tr(J³) / tr(J²)^{3/2}, the normalized third moment of J's spectrum.
  - Uniform ferromagnet: ≈ 1.
  - Balanced, heterogeneous magnitudes (Mattis with half-normal |J|): ≈ 0.5.
  - SK, a Wigner matrix: ≈ 0.
  - Over-frustrated, e.g. antiferromagnetic triangles: < 0.

  It is invariant under every relabeling ξ.

### Three theory caveats, stated before the data
1. **Common drive is balanced.** A shared time-varying field seen by all agents adds a rank-one, all-positive term c_i c_j to the co-movement. It can only raise τ₃ and J̄. So every frustration test here is **one-sided conservative for the glass**: a glass verdict survives common drive, but a ferro/balanced verdict can't be told apart from common drive.
2. **Large-n vector glasses have few metastable states.** For O(n) spin glasses the number of metastable states falls with n; the n → ∞ (spherical) SK model condenses onto J's top eigenvectors with a trivial P(q). At n = 32 a true content glass need not show a broad P(q). So the overlap tests (P5) are secondary to frustration (P3): a P5 pass is strong support for metastability, a P5 fail does not refute frustration.
3. **"Conflict" need not mean anti-alignment in content.** Two agents competing for the same audience talk about the *same* things. The rival **homophily / engagement** model predicts that same-role rivals co-move *positively*. The treatment test (P4) is built to decide between the two.

## Data scheme (`scheme/`)
`scheme/build.py` reads shared tables only and refuses holdout days unless called by the confirmatory script with its flags. Inputs:
- `embeddings/statements.parquet` + `chat_bge_small.npy`, `common.load_whitener("III", 32)`;
- `activity_bins` (talk spins), `roster` (lab), `rooms_timeline` / `statements.room` (modal room), `calendar`;
- raw `agent_goals` (#51 role per agent; short names only; the coded pair classes are in `scheme/role_relations.py`, written before any outcome data).

**Output:** `data/processed/H22-private-goals-spin-glass/G<NN>/<unit>/` with `_provenance.json`. Contents:
- agent-window and agent-day whitened chat vectors (float16, plus two half-splits by alternating statements);
- talk-spin pair-day correlations and the cross-day surrogate;
- unit metadata.

No text is written.

**Units** (goal period split at step changes; same split as H01/H13 so results line up):

| Unit | Dates (PT) | Step change at start | Days | Role |
| --- | --- | --- | --- | --- |
| 51a | 07-06 → 07-08 | NE26 roles start | 3 | descriptive (short) |
| 51b | 07-09 → 08-04 | NE32 batch join (+3 GPT-5.6), isolated rooms 07-09 | 19 | counted |
| 51c | 08-05 → 08-24 | #focus room opens (Gemini 2.5 Pro, Opus 4.8 move) | 14 | counted |
| 51d | 08-25 → 09-02 | #focus ends | 7 | counted |
| 51e | 09-03 → 09-04 | NE33 batch join (+3) | 2 | descriptive (short) |
| 38a / 38b / 38c | 04-02 → 04-13 / 04-14 → 04-17 / 04-20 → 04-24 | NE17, NE18 | 8 / 4 / 5 | contrast (38a counted; others low power) |
| 40 | 05-04 → 05-08 | — | 5 | contrast (low power) |
| 44 | 05-26 → 05-29 | — | 4 | contrast (low power; only #best has the shared objective) |

- **Single joins inside 51b** (Grok 4.5 on 07-10, Kimi K3 on 07-17, Opus 5 on 07-24), 51d (GLM-5.3 Flash on 08-28, Fable 5.1 on 09-01) are handled by the population rule, not split:
  - an agent enters a unit's coupling matrix if it has ≥ 20 observed windows (≥ 2 chat statements each) and is present on ≥ half the unit's days;
  - a pair needs ≥ 10 shared windows.
- **In 51c,** the two #focus agents (6, 29) are excluded from couplings (different room), as in H13. A variant keeps them.
- **Holdout:** the #51 tail 09-07 → 09-18 is confirmation only (`analysis/confirm_tail.py`).

## Candidate goal periods
#51 non-holdout days (51a–51e) vs shared-objective weeks #38, #40, #44. The #51 tail (09-07 → 09-18) is 🔒, for confirmation.

## Links to other hypotheses
- **H17** (mixing times; behavior states, not content).
- **H20** (aging: t_w-dependence of autocorrelation). H22 does not test t_w-dependence; it tests coupling signs, frustration, and synchrony of day-to-day state changes.
- **H13** (family fields; the family confound check here).
- **H05** (`block_J`), **H18** (attention), **H21** (balanced antiferromagnet on #12: the Mattis rival).

## Observables
*Written 2026-10-04 00:15 UTC, before any real-data run. What I had seen: the role table and role titles (to code pair classes); per unit, the days, agents, eligible agents, agent-window occupancy (≈ 0.6–0.8 of windows have ≥ 2 chat statements; mean 3.5–5.4 statements per observed window); the #51 talk rate (≈ 3% of agent-minutes); rooms and roster dates. No coupling, overlap, or alignment statistic of any period.*

**O0. Agent states.**
- Each own chat statement is whitened (regime III, n = 32) and unit-normalized.
- v_{i,w} is the mean over agent i's statements in 30-min window w (`win30` of the day's active window). A window counts if it has ≥ 2 statements.
- Agent-day state v̄_{i,d}: the mean over the day's statements. It counts if ≥ 3 statements, with two half-splits (odd/even statements in time order).

**O1. Coupling (content co-movement, within-day): J^c_ij.**
- Fast fluctuations: x_{i,w} = v_{i,w} − v̄^win_{i,d(w)}, i's window vector minus the mean of its own windows that day (agent-day centering). This removes both static fields, the day field, and any day-level state. Unlike demeaning across agents, it imposes no zero-sum constraint between agents.
- r_ij = Σ_w ⟨x_iw, x_jw⟩ / √(Σ_w |x_iw|² Σ_w |x_jw|²), over windows observed for both (summed over the unit's days).
- **Cross-day surrogate:** the same with i's day d paired to j's day e ≠ d at the same window index, averaged over all ordered day pairs. This removes time-of-day–locked fields.
- **J^c_ij = r_ij − r^surr_ij.** The window-level common drive (everyone reacts to the same event) stays in, as a positive bias (caveat 1).
- **Slow variant J^s:** the same on agent-day states, per-agent centered over the unit, across days. Descriptive.

**O2. Coupling (talk, excess): J^t_ij.** Per day, the equal-time Pearson correlation of talk spins over the day's 1-min bins (both agents with ≥ 4 talk minutes), minus the cross-day surrogate (i's day d against j's day e, aligned by minute), averaged over days. Same estimand as H05's c0_x.

**Cross-fitting.** All moment statistics use day folds, so noise does not enter squares or cubes:
- **two folds** (even/odd days of the unit) for second moments;
- **three folds** (day index mod 3) for third moments.

**O3. Signal and SK placement (HH87, moment matching).**
- **Signal variance:** S² = mean over pairs of J^A_ij J^B_ij (unbiased for the mean squared true coupling).
- **Spread:** σ_J² = S² − J̄^A J̄^B, the cross-fitted variance of the true couplings across pairs.
- **SK ratio:** κ = √N · J̄ / σ_J (N = agents in the matrix). κ > 1 is the ferromagnetic side, κ < 1 the glass side.
- **Reliability:** ρ_split = corr(J^A, J^B) over pairs.

**O4. Frustration.**
- **Primary: the balance index τ₃ (cross-fitted).**
  - τ₃ = Σ_{i≠j≠k} J^{(a)}_ij J^{(b)}_jk J^{(c)}_ki / (Σ_{i≠j} J^A_ij J^B_ij)^{3/2}, averaged over the 6 assignments of folds (a, b, c) to the three edges.
  - The numerator is unbiased for tr(J³) of the true couplings; the denominator, for tr(J²)^{3/2}.
  - SK ≈ 0; balanced-heterogeneous ≈ 0.5; uniform ferro ≈ 1.
- **Secondary: the triangle frustration index.**
  - F = fraction of triangles with J_ij J_jk J_ki < 0 on the full-unit point estimates, plus the |product|-weighted version F_w.
  - Each against its **sign-shuffle null** (magnitudes kept, signs permuted across pairs; expectation 3p(1−p)² + p³ for negative fraction p) and its **noise null** (the same statistic on surrogate-only couplings).
  - Also reported: the negative fraction p_neg, and F restricted to *reliable* edges (sign agrees in folds A and B).
- **Descriptive:** the ground-state frustration, the fraction of |J| weight left unsatisfied by the best Ising assignment (200 random-restart descents), against the sign-shuffle null.

**O5. Treatment structure (#51 only).** Pair classes, coded from the role titles before any outcome data (`scheme/role_relations.py`):
- **SR, same-role rivals:** the 7 roles held by two agents (Game dev, Twitterati, YouTuber, Forecaster, Merch baron, Diplomat, Reporter). Same metric, separate channels. The dataset docs call them "competing pairs".
- **OP, opposed objectives:** Prankster × Ethicist and Prankster × Psychologist. One maximizes surprise inflicted on others; the others are charged with ethics and wellbeing inside the village.
- **SY, support:** roles whose objective is defined by other agents' outcomes (Performance coach, Psychologist, Village helper, Village tooler) × every other agent, except OP pairs.
- **NC, niche competitors:** different roles maximizing a public-media audience (Twitterati, YouTuber, Substacker, Reporter, Press baron). Descriptive.
- **U:** all other pairs. Agents with no recorded role for most of a unit's days enter as U, flagged.

Statistics, for J = J^c (primary) and J^t (secondary):
- T_SR = mean J(SR) − mean J(U); T_K for K = SR ∪ OP; T_SY.
- Each **family-adjusted:** J residualized on a same-lab indicator by OLS before the class means.
- **Role-label permutation:** agents' roles shuffled among role-holding agents, keeping role multiplicities; 5,000 permutations.
- **Mean-field form:** `block_J` with role labels (SR pairs = within-blocks) on the block-averaged excess correlations.
- **Manipulation check (field, not coupling):** static alignment cos(H_i, H_j) of SR pairs vs U (role fields visible in content).

**O6. Overlap (day-to-day content).**
- δ_{i,d} = v̄_{i,d} − m_d (day field removed; static field kept); δ̂ is unit-normalized.
- q(d, d′) = mean over agents present both days of δ̂^{(1)}_{i,d} · δ̂^{(2)}_{i,d′}, using half-split states so that the self-overlap q_self(d) (halves 1 and 2 of the same day) has the same reliability.
- **q_∞ (EA plateau):** the mean q at lags ≥ D/2.
- **Memory:** M = (q̄(1) − q_∞) / (q̄_self − q_∞).
- **Synchrony of state changes:** W = Var_{d<d′}[q(d, d′) − q̄(lag)] / the same under the **per-agent circular day-shift null**. The null keeps each agent's own day-to-day dynamics and desynchronizes agents; 2,000 shifts.
  - W > 1 means the swarm changes configuration *collectively*: metastable collective states rather than independent agent drift.
- P(q) histograms (descriptive).
- Units with ≥ 7 days only (51b, 51c, 51d, 38a); others descriptive.

**Multiplicity.** Five primary predictions (P1–P5 below) per counted #51 unit, plus the contrast P6.
- Per-unit verdicts are counts.
- Across #51 units, DerSimonian–Laird random-effects summaries of the per-unit estimates.
- Holm correction across P1–P6 for the headline.
- Everything else (F, F_w, slow J^s, talk J^t, NC, 51a/51e, the low-power contrast units) is descriptive.

## Null / baseline
*Written 2026-10-04 00:15 UTC, before any real-data run.*
- **Noise floor (paramagnet):** the cross-day surrogate.
  - It defines J = 0 per pair.
  - The S² null is the distribution of S² when every fold's couplings are replaced by surrogate-only couplings: random day re-pairings, 500 draws.
- **Sign-randomized couplings:** magnitudes kept, signs permuted across pairs, 5,000 draws. Null for F, F_w and the ground-state frustration: what random signs give at this sign mix. The glass predicts the *real* value to sit inside this null; balance predicts below it.
- **Balanced reference (Mattis rival):** τ₃ ≈ 0.5 for heterogeneous balanced couplings; ≈ 1 for uniform ferro. Exact reference values at each unit's N and sampling come from the synthetic runs (`analysis/synthetic.py`).
- **Role-label permutation:** for the treatment tests (O5).
- **Family-field confound:**
  - O5 is repeated on same-lab–residualized couplings, and with the role permutation;
  - τ₃ and F are recomputed after removing the family-block mean coupling (J_ij − mean J over the pair's lab×lab block);
  - SR pairs are mostly cross-lab (6/7), so a cross-lab coupling deficit could pose as "rivals repel".
- **Room rival** (contrast periods): #38/#40/#44 have two rooms, which make J block-diagonal and balanced. τ₃ and F are recomputed within the largest room alone.
- **Overlap nulls:**
  - the per-agent circular day shift (W);
  - for M, the random-field paramagnet expectation M ≈ 0 (fast decorrelation between days).

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** random-field paramagnet (roles as fields, no coupling); ferromagnet / common drive; Mattis / balanced factions; homophily-engagement (rivals co-move positively).
**Locked holdout used for confirmation:** none yet. `analysis/confirm_tail.py` (#51 tail, 09-07 → 09-18) is written, not run. `--dry-run` on the non-holdout stand-in 08-25 → 09-04 works. Predictions: see "Confirmatory predictions" below.
**Overall A–I:** A1 B1 C1 D0 E0 F1 G1 H0 I0 (not promoted).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Spins, fields and couplings are defined from whitened chat embeddings, 30-min windows and talk spins (magnet dictionary); assumptions are listed. Weakness: "conflict" is mapped onto anti-co-movement in *topic* space, which competing agents need not show (caveat 3). Family invariance checked only as a lab×lab block residual. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Day-blocked cross-fitting; within-unit stationarity assumed, not tested. Equal-time couplings read as equilibrium J without an FDT check; no update-order audit. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Content-coupling heterogeneity beats the per-agent day-permutation null in 51b and 51c (ρ_split 0.46, p = 0.003; cross-fitted by day). None of the H22-specific statistics beats its null in the predicted direction. |
| D unfitted predictions | unfitted statistics and the model's signature | 0 | Glass signatures absent: τ₃(dc) indeterminate; T_SR > 0 (opposite sign, meta p = 0.02); W ≈ 1 in all counted units. |
| E interventional | predicts the change across a natural experiment | 0 | Not tested. NE33 (51e) and NE38 (inside 51b) are descriptive only. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | **Identifiable:** heterogeneity, factions vs random signs (τ₃(dc)), collective switching (W) and the treatment test, all at #51 sampling. **Not identifiable:** SK vs heterogeneous ferro, or κ under common drive. Weighted / ground-state frustration vs sign-shuffle is non-specific. Contrast units are near-powerless. No embedding swap yet. |
| G ground truth | agrees with known structure | 1 | Same-role pairs share a content field (static alignment, role permutation p = 0.0002 / 0.010 / 0.026 in 51b / c / d). Two-room contrast weeks show balanced room blocks (τ₃(dc) ≈ 1), and #44's overlap synchrony vanishes once per-room day fields are removed. |
| H comparative | beats the named rivals | 0 | The rivals fit better: homophily (T_SR > 0), and a random-field system with positive mean coupling (κ̂ 4–10, M 0.5–0.75 with W ≈ 1). |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Holdout not run. Contrast weeks are too underpowered to transfer anything. |

## Prediction
*Written 2026-10-04 00:15 UTC (2026-10-03 PT), before running the analysis on any real data.*

What the spin-glass hypothesis predicts, unit by unit for the counted #51 units (51b, 51c, 51d), with content couplings J^c:

- **P1 (couplings are real, not a paramagnet):** S² > 0 against the surrogate null (p < 0.05) and ρ_split > 0. *Against:* S² at the noise floor (then no sign claim is possible in that unit).
- **P2 (glass side of the SK diagram):** κ < 1. *Against:* κ > 1 (ferromagnetic side; note caveat 1, common drive pushes κ up).
- **P3 (frustration at the random-sign level, the primary signature):** τ₃ < 0.25 (nearer SK's 0 than the balanced 0.5), with the day-bootstrap 90% CI upper bound below 0.5. Secondary: F within the sign-shuffle null's central 90%. *Against:* τ₃ ≥ 0.25, or F significantly below the sign-shuffle null (balanced, Mattis or ferro).
- **P4 (conflict carries negative coupling):** T_SR < 0, role-permutation p < 0.05 (one-sided), surviving family adjustment, and mean J^c(SR) < 0 in absolute terms. Also T_SY > 0. *Against:* T_SR ≥ 0. *Rival:* T_SR > 0 significantly (homophily/engagement).
- **P5 (collective metastable states):** W > 1 (shift-null p < 0.05) and M > 0.2. *Against:* W ≈ 1 (independent agent drift or a random-field paramagnet). Caveat 2 applies.
- **P6 (contrast):** #51 is more frustrated than shared-objective weeks.
  - τ₃(#51 units, random-effects mean) < τ₃(contrast units, random-effects mean). Contrast units sit on the ferro/balanced side (τ₃ ≥ 0.25 or κ > 1) or at the noise floor.
  - The single-room variant of the contrast (largest room only) must show the same ordering.
  - *Against:* #51 τ₃ ≥ contrast τ₃.

**Talk couplings (secondary):** H22 predicts T_SR(J^t) < 0. By H02, the expectation is that talk S² sits at the noise floor (P1 fails for talk), making talk signs uninterpretable.

**Short and contrast units:** 51a, 51e, 38b, 38c, #40 and #44 are reported with the same statistics, labelled low power. Synthetic runs give the power at each N and number of days.

**Hypothesis-level verdict rule:**
- **Supported:** P1, P3 and P4 pass in ≥ 2 of 3 counted #51 units, and P6 passes.
- **Failed:** P1 passes but P3 fails in ≥ 2 of 3 (couplings real but balanced), or T_SR > 0 (homophily).
- **Inconclusive:** P1 fails (noise floor).

**My credence before data:**
- ~10% supported;
- ~45% failed via balance or homophily: couplings real, positive-leaning, rivals co-moving;
- ~45% inconclusive at the noise floor.

Reasons: H02 found pairwise activity couplings at the noise floor; the common-drive bias pushes toward balance; competing agents talk about the same things.

### Amendment 1 (2026-10-04 00:42 UTC, before any real-data run; based on synthetic validation only)
Synthetic validation: `analysis/synthetic.py`; results in `data/processed/H22-private-goals-spin-glass/synthetic/results.json`; figure `figures/synthetic_validation.pdf`. Setup:
- content vector spins at each unit's N, days and window occupancy;
- couplings: paramagnet, SK, SK plus a weak uniform part, heterogeneous ferro (κ_true = 3), Mattis factions, and SK with 5× exogenous drive;
- 50 replicates per cell.

It changed the estimators as follows.
1. **P1 tests heterogeneity, not S².**
   - **Rule:** ρ_split must exceed the per-agent day-permutation pseudo-null (p_ρ < 0.05).
   - **Why:** any exogenous common window drive makes S² significant through J̄² alone.
   - **Power at 51b sampling:** 1.0 for SK, ferro and Mattis at coupling RMS s ≥ 0.06; 0.5–0.7 at s = 0.03.
   - **False positives:** 0.24 for the paramagnet at 51b (heterogeneous drive loadings are real co-temporal structure); 0.02 at 51c.
2. **P3's primary statistic becomes the drive-robust balance index τ₃(dc).**
   - **Definition:** τ₃ of the cross-fitted couplings after removing each agent's mean coupling (double-centering, J_ij − J̄_i − J̄_j + J̄).
   - **Rule:** τ₃(dc) < 0.25 *and* day-bootstrap 90% CI upper bound < 0.5.
   - **Why:** raw τ₃ is inflated by exogenous drive (paramagnet with 2% drive: τ₃ ≈ 0.86; SK with 10% drive: 0.78–0.90). τ₃(dc) stays at 0.0 ± 0.1 for SK, SK + J₀ and heterogeneous ferro, and at 0.43–0.48 for Mattis factions.
   - **Classification at 51b, s = 0.06 (point estimate):** random-sign heterogeneity is called unbalanced in 96–100% of replicates. Mattis is called balanced in 84% (98% at s = 0.09; only 40% at s = 0.03, where 26% are misclassified as unbalanced; the CI condition guards this).
   - **Secondary:** raw τ₃ and the triangle index F. F's balance test is not specific under drive: it flags SK as balanced in 22–36% and heterogeneous ferro in 14–52% of replicates.
3. **P2 (κ < 1) is kept but has no power.**
   - κ̂ = 2–12 for pure SK under 2–10% exogenous drive.
   - A pass would be strong support; a fail is uninformative.
4. **Identifiability (main synthetic finding).**
   - τ₃(dc) separates **factions (balanced) from random-sign heterogeneity**.
   - It cannot separate SK from a **heterogeneous ferromagnet** (random couplings around a positive mean), and κ̂ cannot under common drive.
   - So "supported" can only mean frustrated, SK-like coupling heterogeneity beyond the uniform mode, with conflict carrying negative coupling (P4). It cannot mean J₀ < J.
5. **Overlap halves are time-split** (earlier vs later statements of the day), not odd/even. Odd/even halves share the day's window-level fluctuations and inflate q_self.
   - P5 rule unchanged (W, p < 0.05, and M > 0.2).
   - Synthetic size of the P5 rule: random-field paramagnet 0.00; independent agent drift 0.05–0.10.
   - Power against collective metastable states: 0.88 / 0.84 / 0.64 at 51b / 51c / 51d; 0.69 at 38a; 0.80 at the tail.
   - The W test alone has size 0.04–0.14.
6. **Short units (< 7 days: 51a, 51e, 38b, 38c, #40, #44)** use day-thirds as pseudo-days for folds and the surrogate.
   - Population rule: ≥ min(20, 0.4·D·W_median) observed windows.
   - Fold pair threshold scaled down (≥ 2 shared windows); only the full-unit matrix must be complete.
   - **Contrast units are near-powerless:** heterogeneity is detected in ≤ 30% of replicates at 38a and ≤ 18% at #40/#44, even at the strongest coupling.
   - So **P6 is descriptive unless a contrast unit passes P1**.
7. **Treatment test (P4) power at 51b:**
   - 0.96 at Δ = 0.1 (T ≈ ±0.037 in J^c units; per-pair noise SD 0.022);
   - size 0.04 (less) / 0.02 (greater).
8. **Disclosure.**
   - At ≈ 00:20 UTC, *after* the predictions above were written, a file-change notice showed me H13's G51 results:
     - family-block talk mean-field couplings positive (J_in 0.03–0.13);
     - family content co-movement Δ ≈ 0 (n.s.) in 51a–51e.
   - It showed no H22 statistic (no signs, frustration, role contrast or overlaps). Predictions were not changed afterwards.

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G51a](goalperiod-subhypotheses/G51a/README.md) (07-06 → 07-08) | exploratory (short) | descriptive | heterogeneity n.s. (ρ_split −0.05); OP pairs (Prankster × Ethicist/Psychologist) J^c ≈ −0.09 each, T_OP −0.13, p = 0.008 (2 pairs, short unit, one cell among many: a lead, not evidence) |
| [G51b](goalperiod-subhypotheses/G51b/README.md) (07-09 → 08-04) | exploratory | **failed** | ρ_split 0.46 (p 0.003); κ̂ 5.2 [4.5, 8.2]; τ₃ 0.57 [0.47, 0.74]; τ₃(dc) 0.22 [−0.21, 1.04]; p_neg 0.10; **T_SR +0.066 (p> 0.013; 3 pairs)**; W 1.16 (p 0.21); M 0.74 |
| [G51c](goalperiod-subhypotheses/G51c/README.md) (08-05 → 08-24) | exploratory | inconclusive | ρ_split 0.46 (p 0.003); κ̂ 3.9; τ₃ 0.60; τ₃(dc) −0.13 [−2.1, 2.5]; T_SR +0.036 (n.s.; 4 pairs); W 1.15 (p 0.24); M 0.75 |
| [G51d](goalperiod-subhypotheses/G51d/README.md) (08-25 → 09-02) | exploratory | inconclusive | ρ_split 0.12 (p 0.23, P1 fails); κ̂ 9.7; T_SR −0.002 (1 pair); W 0.69 (p 0.79); M 0.49 |
| [G51e](goalperiod-subhypotheses/G51e/README.md) (09-03 → 09-04) | exploratory (short) | descriptive | heterogeneity n.s.; T_SY +0.047 (p 0.012, 23 pairs; the new helper/tooler roles enter here) |
| [G38](goalperiod-subhypotheses/G38/README.md) (38a / 38b / 38c) | exploratory (contrast) | descriptive | 38a: ρ_split 0.56 (p 0.02), κ̂ 3.0, τ₃ 0.46, τ₃(dc) 1.03 (room blocks), W 3.14 (p 0.001; with per-room day fields 1.98, p 0.018, post hoc); 38b, 38c at the noise floor |
| [G40](goalperiod-subhypotheses/G40/README.md) | exploratory (contrast) | descriptive | ρ_split 0.31 (p 0.050), κ̂ 6.9, τ₃ 0.51, p_neg 0.06; W 1.48 (p 0.18) |
| [G44](goalperiod-subhypotheses/G44/README.md) | exploratory (contrast) | descriptive | ρ_split 0.59 (p 0.003), κ̂ 2.8, τ₃ 0.47, τ₃(dc) 0.95 (room blocks); W 3.99 (p 0.006) → 1.03 (p 0.39) with per-room day fields (post hoc) |

## Results
*Round 1, 2026-10-04. Code: `analysis/explore.py` (per unit), `analysis/summarize.py` (cross-unit), `analysis/period_cards.py` (period folders in `goalperiod-subhypotheses/`). Data: `data/processed/H22-private-goals-spin-glass/G<NN>/<unit>/results.json`, `summary.json`. Figures: `figures/summary.pdf` (one-page summary), `figures/summary_obs.pdf`, `figures/synthetic_validation.pdf`, and `goalperiod-subhypotheses/G*/figures/`.*

**Headline: #51 is not a spin glass in content space.**
- It looks like a **random-field system with weak, mostly positive (mean-field or drive) coupling**:
  - private roles freeze each agent's position (EA-like plateau q_∞ = 0.41–0.54, and same-role pairs share a content field);
  - positions persist from day to day (memory M = 0.5–0.75);
  - the swarm never switches collectively between metastable configurations (W ≈ 1).
- Couplings between agents are real (51b, 51c) but 85–94% positive (κ̂ ≈ 4–10), and the sign structure beyond the uniform mode is indeterminate.
- The decisive treatment test went the other way: **same-role rivals co-move *more* than unrelated pairs** (random-effects T_SR = +0.048 [0.008, 0.089], p = 0.02, I² = 0, k = 3 units). That is the homophily / engagement rival, not antiferromagnetic conflict.
- In SK terms, #51 sits on the ferromagnetic side with random fields (κ̂ includes common drive, so "ferro" here means "mean-field or drive dominated"), not in the glass phase.

### Outcome vs prediction (counted #51 units 51b / 51c / 51d)
| Prediction | Observed | Verdict |
| --- | --- | --- |
| P1 heterogeneous couplings (ρ_split > pseudo-null) | 0.46 (p 0.003) / 0.46 (p 0.003) / 0.12 (p 0.23); random-effects 0.35 [0.12, 0.57] | pass 2/3 |
| P2 κ̂ < 1 | 5.2 / 3.9 / 9.7; random-effects 4.6 [3.1, 6.0] | fail (uninformative: drive inflates κ̂, Amendment 1) |
| P3 τ₃(dc) < 0.25 with CI upper < 0.5 | 0.22 [−0.21, 1.04] / −0.13 [−2.1, 2.5] / −0.12 [−0.12, 0.21] (51d without P1) | indeterminate. Real heterogeneity is weak relative to noise, like synthetic s ≈ 0.03, where τ₃(dc) is unreliable. Raw τ₃ 0.56 [0.43, 0.69] is on the balanced/ferro side, but drive-inflated |
| P3 secondary: F vs sign shuffle | 0.25 vs 0.25 / 0.30 vs 0.32 / 0.16 vs 0.17 (few negatives: p_neg 0.06–0.14) | uninformative (F tracks the sign mix; weighted F and ground-state frustration are below the null in all units, but the synthetic shows that test is non-specific) |
| P4 T_SR < 0 (family-adjusted, p_less < 0.05) and mean J(SR) < 0 | +0.066 (p> 0.013, 3 pairs) / +0.036 (4) / −0.002 (1); mean J(SR) > 0 in every unit; meta +0.048, p = 0.02 | **fail, rival direction** |
| P4 T_OP < 0 (Prankster × Ethicist / Psychologist) | −0.048 / −0.014 / +0.008 (2 pairs each, n.s.); meta −0.018 (p 0.52) | fail (n.s.; 51a −0.13, p 0.008, descriptive) |
| P4 T_SY > 0 | +0.003 / +0.014 / +0.015 (n.s.); meta +0.010 (p 0.32); 51e +0.047 (p 0.012) | fail (right sign everywhere, never significant in a counted unit) |
| P5 W > 1 (p < 0.05) and M > 0.2 | W 1.16 (p 0.21) / 1.15 (p 0.24) / 0.69 (p 0.79); M 0.74 / 0.75 / 0.49 | fail. Memory without collective switching: the synthetic "independent drift / random field" signature |
| P6 #51 raw τ₃ and κ̂ below shared-objective weeks | #51 τ₃ 0.56 vs 0.46 (38a), 0.51 (#40), 0.47 (#44); κ̂ 3.9–9.7 vs 2.8–6.9; largest-room variants: no ordering | fail (descriptive: contrast units near-powerless, two-room confound) |
| Talk (secondary) T_SR(J^t) < 0 | talk heterogeneity at the noise floor (p_ρ 0.09–0.29), as H02 predicts; T_SR(talk) +0.002 / +0.013 / +0.020 (n.s.) | uninterpretable (noise floor) |
| Manipulation check: role fields visible | static SR alignment +0.40 / +0.26 / +0.44 over unrelated (p 0.0002 / 0.010 / 0.026) | pass |

- **Verdict:** by the card's rule (failed if T_SR > 0 significantly or P3 fails), H22 **fails in 51b** and is inconclusive in 51c and 51d.
- **Hypothesis level:** not supported. The only significant departure from the nulls in the role structure is the rival direction (homophily).
- **Multiplicity:** with 5 classes × 2 modalities, the rival T_SR result (meta p = 0.02; 51b p = 0.013) is modest and needs confirmation. It is pre-registered as the rival test in `confirm_tail.py`.
- **Family confound:**
  - The same-lab coefficient is ≈ 0 in all #51 units (51b β = 0.0000; 51c +0.018; 51d −0.021).
  - 6 of 7 rival pairs are cross-lab, so a family-homophily artifact would have pushed T_SR *down*, not up.
  - Removing lab×lab block means lowers raw τ₃ in 51b (0.57 → 0.25), so part of the raw balance there is family structure.

### What the contrast weeks show (descriptive)
- **Couplings:** where detectable (38a, #40, #44) they are also positive-mean and ferro-side (κ̂ 2.8–6.9, raw τ₃ 0.46–0.51). On these statistics #51 is no less ferromagnetic than shared-objective weeks.
- **Rooms:** the two-room weeks show balanced room blocks in τ₃(dc), the factional structure H21 expects for teams. So *rooms*, not goals, produce the only clearly balanced sign structure in the data.
- **Overlap synchrony:** W > 1 in 38a and #44 is mostly a room-level day field that the global day mean does not remove. In #44, W returns to 1 with per-room day fields (post hoc); in 38a a remnant persists (W 1.98, p 0.018), perhaps the campaign's phases.

### Confirmatory predictions for the #51 tail (written 2026-10-04 00:51 UTC, before any look at the tail; encoded in `analysis/confirm_tail.py`)
Unit 51T = 09-07 → 09-18 (10 days, ≈ 30 agents). Same pipeline.

**H22 is confirmed only if all of these pass:**
- **C1** heterogeneity: ρ_split above the pseudo-null, p < 0.05.
- **C2** τ₃(dc) < 0.25 with CI upper < 0.5.
- **C3** T_SR < 0, p_less < 0.05 (family-adjusted).
- **C4** W > 1, p < 0.05.

**The exploration-derived rival is confirmed if all of these pass:**
- C1;
- **C3r** T_SR > 0, p_greater < 0.05;
- **R1** raw τ₃ ≥ 0.25 and κ̂ > 1;
- **R2** W not significant and M > 0.2.

**Further rules:**
- If fewer than 3 same-role pairs pass the shared-window threshold, C3 and C3r are "not testable". In the dry-run stand-in (08-25 → 09-04) only 1 pair qualified, so this outcome is likely.
- C5 (F not below the sign-shuffle null) and the role-field manipulation check are reported, not decisive.

**My credence:**
- H22 confirmed: < 5%;
- rival confirmed: ~30%, limited mainly by testability;
- otherwise inconclusive.

Run only with Vivian's sign-off (`--confirm --i-understand-this-uses-the-locked-holdout`).

### Caveats
1. **Identifiability (synthetic, Amendment 1).**
   - SK cannot be told from a heterogeneous ferromagnet, and κ̂ is inflated by any common drive.
   - In one broadcast room, the endogenous mean field and exogenous drive are inseparable at 30-min resolution.
   - "Ferro side" therefore means "positive mean co-movement", which could be shared exogenous input.
2. **Topic is not stance.**
   - Content couplings measure co-movement in *what agents talk about*. Rivals in the same niche discuss the same things, so the treatment test speaks to topic homophily, not to strategic opposition.
   - A faithful test of "conflict → antiferromagnetic coupling" needs a stance spin (agree / disagree, support / undermine), e.g. Jev labels on reply pairs.
3. **Few testable rival pairs.**
   - Only 3 / 4 / 1 same-role pairs (51b / c / d) share ≥ 10 windows: under private roles many agents work off-chat (Opus 4.6 had no qualifying window in 51b).
   - Synthetic power assumed 7 pairs.
4. **Small complete matrices.** Frustration statistics use complete-matrix subsets (N = 17 / 13 / 12 of 22 / 19 / 15 eligible), and the τ₃(dc) CIs are very wide.
5. **Non-specific tests.** Weighted triangle frustration and ground-state frustration against the sign-shuffle null flag "balance" in most synthetic SK runs. They are reported, never used as evidence.
6. **W null calibration.** The overlap-synchrony null is mildly anti-conservative (synthetic size 0.04–0.14).
7. **Contrast weeks** are near-powerless and two-roomed. P6 is descriptive, and the per-room day-field overlap variant was added post hoc.
8. **Changes after the first real-data run, all disclosed; both versions are in the G folders.**
   - The treatment test moved from the complete-matrix agent set to the card's pair rule (every eligible pair with ≥ 10 shared windows). 51b: T_SR +0.067 (p 0.024) complete vs +0.066 (p 0.013) pairwise.
   - A bug that blanked all family-adjusted values was fixed.
   - Unit verdict labels were aligned with the card's rule (indeterminate ≠ failed).
   - The per-room overlap variant was added.
9. **Exposure.** I saw H13's G51 family-block results after the predictions were written (Amendment 1, point 8).
10. **One embedding model** (bge-small, whitened n = 32). No embedding swap. Agent narration is never used as ground truth: everything is computed from embeddings and talk timing; no message text is stored or quoted.

### Next steps
- **Confirmatory run** on the #51 tail after sign-off.
- **Stance spins** (Jev or Claude labels on reply pairs: agree / disagree, help / undermine), to test conflict → negative coupling in the space where conflict lives. Most valuable for the Prankster × Ethicist/Psychologist pairs, the only cells that leaned H22's way (51a).
- **Lagged (kinetic) content couplings** (window VAR, model 11 dynamics), to separate endogenous broadcast coupling from exogenous drive and so identify J₀.
- **Treat #51 as a random-field problem:** field strength (q_∞, static role alignment) vs coupling (J̄, σ_J). Use NE38 (Opus 5's role reassignment) as a field-step intervention (axis E): does that agent's position jump to the new role field with no change in couplings?
- **Robustness:** embedding swap; with H20, test whether the high M is aging (t_w dependence).

## Notes
- 2026-10-03: promoted from HH102.
- 2026-10-04 00:15 UTC: observables, nulls, predictions, units and pair-class coding written before any real-data run.
- 2026-10-04 00:42 UTC: Amendment 1 (synthetic only). 00:43 UTC: per-period predictions written in the G folders.
- 2026-10-04 ≈ 00:45–00:50 UTC: round 1 run on non-holdout units. 00:51 UTC: confirmatory predictions locked; dry run OK.
- 2026-10-04: period folders moved to `goalperiod-subhypotheses/` (Vivian's layout change); scripts write there. One-page hypothesis summary in `summary/` (content.tex, meta.json; built with `infra/summaries/build_summaries.py --only H22`). Round-1 one-page figure summary: `figures/summary.pdf`.

## Round 2 redirects (2026-10-04)
*From the round-1 reflection (`writeup/round1-reflection/round1-reflection.pdf`).*
- **Where round 1 went sideways:** Topic co-movement cannot see conflict.
- **What the direction is really after:** Do conflicting incentives produce conflict behavior at all?
- **H22-R1.** Cooperation default: agents help rivals at rates comparable to aligned pairs (Jev-labeled help acts).
- **H22-R2.** A quantitative random-field fit (HH129): roles as fields plus weak positive coupling.
