# H97: A restoring-force law for the kickoff quench

**Status:** **exploratory round 1 done (2026-10-04). A kickoff is a restoring force, but not HH246's linear, isotropic, agent-constant one.**
- **Restoring force (P1, supported):** across 18 kickoffs the cross-agent memory of the pre-kickoff position falls from ρ0 = 0.68 on ordinary days to ρ = 0.42 at the kickoff: extra forgetting Δρ = +0.26 ± 0.04 (meta, 90% CI ±0.07), positive in 16/18, in both embedding models and all 7 input variants.
- **Not isotropic (P2 fragile):** the IV isotropy test passes by its rule (β∥ − β⊥ = −0.17 ± 0.16) but fails under `style_resid`; the scale-free version forgets 0.63 along k̂ vs 0.25 transverse. The well is stiffer along the kickoff.
- **Not through the origin (P3 intercept failed):** relative to the settled plateau, day 1 overshoots: a = +0.12 ± 0.02 (agent-centered; gte +0.17). Rivals R5/R6 (overshoot or a common-mode jump) beat the HH-literal law.
- **χ_i is not shown to be an agent constant (P4 inconclusive):** split-half r = 0.30 (p 0.14, bge), 0.48 (p 0.03, gte), −0.06 centered; synthetic power 0.30. No lab effect (p 0.49).
- Natives: NE38 supported (a one-agent goal change erases Opus 5's position 6× more than its ordinary days, 88th–100th percentile of the other agents); G44 failed (room field changes the direction of the move, not the amount of forgetting); G26 failed by rule but confounded by the day-1 transient.
- Card and predictions written ~20:25 UTC before any real-data statistic; Amendment 1 (~20:48 UTC) after the synthetic. `analysis/confirm.py` frozen and dry-run; **not run**.
**Question (GOALS.md):** **Q2** (what is field and what is coupling): is the kickoff a harmonic well that every agent relaxes into at its own rate, and is that rate an agent constant? Second: **Q5** (an operator who knows each agent's susceptibility can predict who follows a new goal).
**Fields:** stat mech, dynamics
**Literature:** none new; builds on the round-1 results of H10, H54, H73, H75, H13 (cards linked below).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Population N(t); Regime (whitening per regime, no transition crosses a regime boundary); Driving / external field (the kickoff); Agent state, variant *vector*, in H54's form (unit regime-whitened statement vectors, d = 32, agent state = plain mean over a segment); H54's **quench target t̂_p** and **jump**. New named variants proposed for DEFINITIONS.md (not edited there; defined under Observables): **kickoff memory β**, **restoring susceptibility χ = 1 − β**, **extra forgetting Δβ**, **per-agent susceptibility χ_ip**.
**From:** HH246 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/11-vector-spins/` (primary), `physics-models/02-nonequilibrium-ising/` (overdamped relaxation, secondary)
**Model folder:** `physics-models/16-langevin-relaxation/` (added 2026-10-07)

## Source HH (verbatim from the HH list, including refinements)
A restoring-force law for the quench. If the kickoff is a field, each agent's day-1 displacement should be proportional to its pre-kickoff distance from the target, with one susceptibility per agent: Δv_i ≈ χ_i (k̂ − v_i,prev). That is an unfitted shape prediction (linear, through the origin) the current analysis doesn't test. *Check:* per-agent day-1 displacement along k̂ vs pre-period distance; linearity, intercept 0, χ stability across kickoffs.
  *Models:* 11, 02 · *Builds on:* H54, H10 · *Lever:* D (unfitted prediction)

## Standards (2026-10-04)
**Question served:** Q2 (field vs coupling: the kickoff as a well with a stiffness), Q5 (per-agent steerability).

| Impostor | Relevant? | How it is handled | Status |
| --- | --- | --- | --- |
| Scheduler field | no | Content statistics on day-level segments; no timing statistic. The kickoff boundary spans a weekend; a weekend-matched placebo (Friday → Monday boundaries inside periods) checks gap length. | n/a |
| Exogenous field (kickoff/goal/operator) | yes | The kickoff field is the object. The placebo is the same estimator on ordinary day boundaries of the same agents along the same k̂ (kickoff-matched placebo). The target level comes from shared `goal_fields`. Other operator messages on day 1 are not regressed out. | partly |
| Shared model priors | yes | A persistent agent offset (style, family prior) fakes memory. Variants: `statements_style_resid_period32` (DQ5) and a leave-period-out agent-mean centering (R3); lab effect on χ (permutation). | removed (by the variants) |
| Contemporaneous convergence | no | No agent-to-agent influence claim. The common target is a field response; whether agents converge by reading each other is out of scope. | n/a |

**Inputs:** shared `goal_fields` (kickoff and goal vectors, both models), DQ5 statements in bge-small and gte-modernbert (`statements_white32_*`, `statements_style_resid_period32_*`), DQ5 `statement_flags` (dedupe variant), `period_units`, `roster`, `ground_truth_labels` (#51 roles, NE38), H54's `kickoffs.parquet` (kickoff message time t0) and `projects.parquet` (goal-text naming tags), read-only. No activity table.

**Two layers:** replication on every eligible kickoff transition (role `replication`); natives NE38, G44, G26 (role `native`).

**Confirm script:** `analysis/confirm.py`, frozen and guarded, not run.

## Question
When a goal kickoff arrives, does each agent's day-1 content move toward the kickoff target in proportion to how far it started (a linear restoring force), and is each agent's restoring rate χ_i a constant of that agent across kickoffs, as its style is?

**Practical payoff:** if χ_i is an agent constant, an operator can rank agents by how fast they adopt a new goal before issuing it, and a scaffold builder can measure one number per model.

## Model
**From:** `physics-models/11-vector-spins` (agent states s_i ∈ S^{31} in the regime-whitened basis), with the overdamped relaxation of `physics-models/02-nonequilibrium-ising` written for vectors.

**H97 variant: overdamped relaxation into a harmonic well centred by the kickoff.** Before the kickoff, agent i sits at x_i (its previous-period state). At the kickoff the well centre jumps to the target t_p. During day 1 each agent relaxes with its own stiffness:

ẋ_i = −κ_i (x_i − t_p) + ξ_i  ⇒  y_i ≡ x_i(day 1) = t_p + β_i (x_i − t_p) + η_i,  β_i = e^{−κ_i τ},  χ_i = 1 − β_i,

which is HH246's Δv_i = χ_i (t_p − x_i) with a scalar χ_i. A scalar χ_i means the well is **isotropic**: the transverse part of the offset (⊥ k̂) decays at the same rate as the part along k̂. The target t_p = c_p k̂_p + b_p sits along the kickoff direction up to an unknown transverse offset b_p (a text-embedding proxy error).
- **Swarm memory** β_p: the cross-agent regression slope of y_i on x_i. χ_p = 1 − β_p.
- **Agent constant:** χ_ip = χ_i + ε_ip with var(χ_i) a stable share of the reliable variance.
- **Ordinary days** have their own memory β0 < 1 (topic turnover). The kickoff's restoring force is the **extra forgetting** Δβ = β0 − β_kick.

**Rivals:**
- **R0 pure translation** (H10's R1; field without a well): y_i = x_i + λ k̂ + turnover. β_kick = β0 (Δβ = 0), and the displacement along k̂ does not depend on the starting distance (slope b = 0).
- **R1 common target / full reset** (H10's R2): β_kick ≈ 0, slope b = 1.
- **R2 longitudinal-only quench:** the field resets only the k̂ component (β∥ ≈ 0), transverse components keep ordinary memory (β⊥ ≈ β0). Not isotropic.
- **R3 persistent agent prior** (H13, H73): memory survives only through the agent's constant offset a_i (style, family); with a_i removed β_kick ≈ 0.
- **R4 constant speed** (bounded displacement, H75's speed limit): Δ_i ∝ sign(D_i), not ∝ D_i (concave).
- **R5 impulse with overshoot** (H54 remanence: kickoff excess 0.24 on day 1 → 0.11 plateau): on day 1 agents pass beyond the settled level, so relative to the settled target the intercept is positive.

## Data scheme (`scheme/`)
`scheme/build.py` builds `data/processed/H97-quench-restoring-force/` from shared tables only. No text is read.
- **Inputs:** `embeddings/statements.parquet` (+ `statements_white32_{bge_small,gte_modernbert}.npy`, `statements_style_resid_period32_*.npy`), `statement_flags.parquet`, `embeddings/goals.parquet` + `goal_vectors*.npy`, whiteners per regime and model, `period_units`, `roster`, `ground_truth_labels`; H54 `kickoffs.parquet` (t0) and `projects.parquet` (naming tags), read-only.
- **Transform:** every statement passes `common.holdout_mask`; the Claude Code agent (19) is excluded. For each eligible transition the scheme stores, per statement, the segment code (prev, day 1, plateau days 2–5, placebo day d) and the row index into the shared statement arrays. Kickoff and goal vectors are whitened in the target regime basis of each model and unit-normalized.
- **Eligible transitions:** p non-holdout, p − 1 non-holdout, same regime, both with statements; #23 excluded (H10 keeps it blind for its confirmatory #22 → #23 pair), so #24 is unavailable. Cross-regime #37 is a variant only. Per transition, agents with ≥ 4 statements in both the previous period's last active day and day 1. Per-transition statistics need N ≥ 5; per-agent statistics use N ≥ 4.
- **Segments:** *prev* = the previous period's last active day; *day 1* = statements on p's first active day at or after the first kickoff message (H54 t0); *plateau* = days 2–5 of p; *placebo boundaries* = consecutive active days (d, d + 1) inside one `period_units` unit of p − 1 or p, not touching day 1 of p, both non-holdout, with ≥ 5 agents at ≥ 4 statements on both days.
- **Output:** `transitions.parquet` (one row per transition: p, regime, mode, N, day dates, t0, kickoff gid per model, naming tags), `segments.parquet` (statement row, transition, segment, agent, day), `_provenance.json`. Analysis outputs in `G<NN>/`, `NE34/` (cross-kickoff), `natives/`, `synthetic/`.
- **Regimes covered:** I, II, III (each transition within one regime).

## Observables
*Specified 2026-10-04, before any real-data statistic along a kickoff direction.* z = unit regime-whitened statement vector (d = 32). k̂_p = unit(W_r · kickoff_p). Per agent and segment, the state is the plain mean of z.
- **Split halves.** Agent i's prev statements are split at random into halves A and B (R = 50 splits, both orientations). x_i^A, x_i^B: half means; y_i: day-1 mean. Bars denote means over the transition's agents.
- **Kickoff memory along a subspace P** (P∥ = k̂k̂ᵀ, P⊥ = I − k̂k̂ᵀ, or full I):
  β_P = Σ_i ⟨P(y_i − ȳ), P(x_i^A − x̄^A)⟩ / Σ_i ⟨P(x_i^B − x̄^B), P(x_i^A − x̄^A)⟩.
  This is an instrumental-variable slope. Statement noise in x biases neither numerator nor denominator, so β is unbiased where OLS would be attenuated toward 0 (which fakes a restoring force). χ_P = 1 − β_P.
- **Placebo memory β0_P:** the same estimator on each placebo boundary of the transition (day d plays prev, day d + 1 plays day 1), along the same k̂_p; β0 = median over boundaries. **Extra forgetting** Δβ_P = β0_P − β_P.
- **Isotropy:** β∥ − β⊥ (kickoff boundary).
- **HH-literal shape test along k̂:** u_i^A, u_i^B = ⟨x_i^{A,B}, k̂⟩, w_i = ⟨y_i, k̂⟩. Target level T_{p,−i} = the other agents' mean alignment on plateau days 2–5 (an out-of-sample settled target). Distance D_i = T_{p,−i} − u_i^A, displacement Δ_i = w_i − u_i^B. Fit Δ_i = a + b D_i per transition; b is divided by the split-half reliability of u (errors-in-variables correction) and a adjusted to match. The law predicts a = 0, 0 < b ≤ 1. Curvature: the coefficient c of D_i² (descriptive).
- **Per-agent susceptibility χ_ip** (two estimators):
  - *memory form* (full space, leave-agent-out centroids): χ^mem_ip = 1 − ⟨y_i − ȳ_{−i}, x_i^A − x̄^A_{−i}⟩ / ⟨x_i^B − x̄^B_{−i}, x_i^A − x̄^A_{−i}⟩;
  - *HH form* along k̂: χ^∥_ip = Δ_i / D_i (median over splits; D_i from half A, Δ_i from half B).
  - Because ratios are heavy-tailed, the agent-constancy tests use within-transition ranks (rank / (N + 1)).
- **Agent constancy:** for agents in ≥ 4 eligible transitions: split-half r = Pearson correlation across agents between the mean rank over odd-numbered and even-numbered transitions (by date); permutation null shuffles agent labels within each transition (2,000 draws). Agent share u_χ = between-agent variance / total variance of ranks (one-way random effects), with the same permutation null. Benchmarks: H73's style agent constant u_A = 0.55; H54's raw move split-half r = 0.09.
- **Noise ceiling:** within-transition reliability of χ_ip from two random halves of the day-1 statements (Spearman–Brown). If it is below 0.3, agent constancy is not testable at this resolution.

## Null / baseline
- **N0 placebo boundaries** (R0): ordinary day-to-day memory of the same agents along the same k̂ (kickoff-matched placebo). Weekend-matched variant: placebo boundaries that span ≥ 2 calendar days.
- **N1 agent-label permutation** within transition (agent constancy).
- **N2 agent bootstrap** within transition for every CI (percentile, 2,000 draws); across transitions, a random-effects meta-analysis (DerSimonian–Laird) of per-transition estimates and a sign test. Periods are never pooled into one fit.
- **N3 synthetic truths** (axis F): vector-spin swarms at the real agent and statement counts under H (restoring, isotropic, agent-constant χ_i), H′ (restoring, χ not agent-constant), R0, R1, R2, R3, R4, R5, analyzed by the same pipeline.
- **Known confounds:** text-embedding proxy for the target; wrap-up content on the previous period's last day; day 1 mixes the kickoff transient with ordinary turnover; agents present on day 1 are those who talk (selection by activity); the weekend gap.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R0 pure translation; R1 common target; R2 longitudinal-only quench; R3 persistent agent prior; R4 constant speed; R5 impulse with overshoot.
**Locked holdout used for confirmation:** none yet. Planned: held-out kickoffs #9, #14, #15, #28, #29, #34, #43, #45–#50 (`analysis/confirm.py`, frozen, not run).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Memory from DQ5 statement vectors, kickoff from shared `goal_fields`; both models, style, dedupe, centered variants agree on P1. Holds in regimes I, II, III. The target is a text proxy; the unit-normalization artifact needed the correlation estimator. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Weekend gap ruled out (P8). Day 1 is not a quasi-static step: the overshoot shows the field decays during relaxation. Ordinary-day memory differs by regime (0.62 vs 0.83). |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 2 | Beats the kickoff-matched placebo (same agents, same k̂, ordinary day boundaries) in 16/18 kickoffs; meta CI excludes 0 in all 7 variants; estimator calibrated on synthetic R0 (false positives 0.025–0.05). |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | Δρ∥ > 0 passes; the through-origin intercept fails (+0.12); isotropy passes only in the raw variant; agent constancy inconclusive. |
| E interventional | predicts the change across a natural experiment | 1 | NE38 (one-agent reassignment) supported in both models; G44 room contrast failed; G26 confounded. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 2 | 9 scenarios at the real structure of 23 kickoffs; the β artifact found and replaced before real data; P4 power stated (0.30). |
| G ground truth | agrees with known structure | 1 | NE38's DQ6 role change and G44's DQ6 rooms; no ground truth for χ itself. |
| H comparative | beats the named rivals | 1 | R0 (translation) rejected; R2 (longitudinal-only) rejected as complete (transverse forgetting +0.25) but anisotropy favours it partly; R5/R6 beat the HH-literal law on the intercept. |
| I transfer | holds in other same-mode periods, including the holdout | 1 | Positive in 16/18 across modes C, I, K, M, F; holdout not run. |

## Prediction
*Written 2026-10-04 ~20:25 UTC, before running the analysis on real data.*

**What I had seen when writing this:** the round-1 cards of H10 (goals are quenches; common-target slope −1.41 in #11 → #12a; cross-kickoff jump falls with the pre-period level), H54 (day-1 centroids land on their own kickoff; the move points at the kickoff in 92%; raw move along k̂ "χ" split-half r = 0.09 across kickoffs, no lab effect; kickoff excess 0.24 on day 1 → 0.11 plateau), H73 (style agent constant u_A = 0.55), H75 (named-target kickoffs freeze within 0.5 active h), H13 (family fields are style). Counts only for H97: 25 within-regime-or-adjacent transitions with non-holdout neighbours (18 within one regime with N ≥ 5), 3–15 shared agents, median 15–161 statements per agent on day 1 and 22–165 on the previous last day. No memory, displacement or χ statistic computed.

**Primary predictions** (combined across transitions by meta-analysis; per-transition numbers are descriptive):

| ID | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| **P1** restoring force | Extra forgetting Δβ_full = β0 − β_kick > 0: meta-analytic mean with 90% CI above 0 **and** Δβ > 0 in ≥ 2/3 of transitions with N ≥ 5 | mean Δβ ≤ 0, or Δβ > 0 in ≤ half (R0) | 0.65 |
| **P2** isotropy (scalar χ) | β∥ − β⊥: meta-analytic 90% CI contains 0 and \|mean\| < 0.2 | CI excludes 0 with β∥ < β⊥ by ≥ 0.2 (R2) | 0.35 |
| **P3** HH-literal shape | Along k̂ with the settled target: slope b > 0 (meta CI above 0) **and** intercept a with meta CI containing 0 | b ≤ 0 (R0), or a > 0 with CI above 0 (R5 overshoot) | slope 0.7; intercept 0.3 |
| **P4** agent constant | split-half r ≥ 0.3 with permutation p < 0.05, and u_χ ≥ 0.3 (p < 0.05), for the memory form; the HH form reported beside it | r < 0.15 or p ≥ 0.2 | 0.2 |

**Secondary:**

| ID | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| P5 | Named-target kickoffs forget more: Δβ higher in non-free kickoffs than in free-choice (mode F) kickoffs (Mann–Whitney one-sided p < 0.1), and higher where H54 tags a goal-named frozen project | no difference or reversed | 0.5 |
| P6 | No lab effect on χ_ip (within-transition permutation of lab labels, p ≥ 0.2) | p < 0.05 | 0.75 |
| P7 | P1's sign survives gte-modernbert, `style_resid_period`, dedupe (`self_repeat_both`) and the leave-period-out agent centering | sign flips in ≥ 2 variants | 0.6 |
| P8 | The weekend gap does not cause the extra forgetting: weekend-spanning placebo boundaries have β0 within 0.1 of weekday ones | weekend β0 lower by > 0.15 | 0.7 |

**Native predictions** (each also in its folder README):

| ID | Unit | Prediction | Counts against | Credence |
| --- | --- | --- | --- | --- |
| N1 | NE38 (#51, 2026-07-29) | Claude Opus 5's reassignment is a one-agent kickoff: its memory form χ^mem across 07-28 → 07-29 exceeds the 90th percentile of the other agents' χ^mem at the same boundary; its move points at its new goal (cos > 0) | χ^mem within the others' range | 0.6 |
| N2 | G44 (#42 → #44, two rooms) | The room with an assigned, named target (#best) forgets more than the free-choice room (#rest) at the same boundary: mean χ^mem(#best) > mean χ^mem(#rest) | reversed or equal | 0.55 |
| N3 | G26 (election leader's announcement, 2026-01-05 19:36 UTC) | An agent-authored second target does not act as a well: memory across the announcement (day-1 statements before vs after) lies inside the distribution of memory across clock-time-matched splits on days 2–5 (percentile 0.1–0.9) | percentile > 0.9 or < 0.1 | 0.6 |

**Overall verdict rule:** the law is **supported** if P1 holds, P3's slope holds and P2 does not fail; **failed** if P1 fails; **mixed** otherwise. The agent-constant question (P4) gets its own verdict line. Per-transition replication rule (templated): supported if Δβ_full > 0 with agent-bootstrap 90% CI above 0 and b > 0; failed if Δβ_full ≤ 0; mixed otherwise.

**Multiplicity and power.** Four primaries, each at one-sided 0.05 or a 90% CI. The synthetic run states the realized power before the real run.

**Amendment 1** (2026-10-04 ~20:48 UTC, after the calibration and the synthetic run, before any real-data statistic along a kickoff direction; the calibration used only full-space placebo memory and statement resultants on ordinary day boundaries). Synthetic: `analysis/synthetic.py`, 40 replicates × 9 scenarios at the real structure of 23 same-regime transitions (`synthetic/results_main.json`), plus a P4 power run (`synthetic/p4_power.json`).
1. **P1 uses the disattenuated memory correlation ρ, not the IV slope β.** ρ = cov(y, x) / √(var_true(x) var_true(y)), with both true variances from split-half cross products. Reason: under pure translation (R0) the β version passes P1 in 45–90% of replicates. Statements are unit-normalized, so a common component that grows on day 1 compresses every agent's deviation and lowers the slope without any forgetting. ρ is scale-free: R0 false-positive rate 0.025–0.05; power 1.00 at Δρ ≈ 0.10–0.25 (H, H′, weak H). Δρ = ρ0 − ρ_kick replaces Δβ in P1, P5, P7 and the templated per-transition rule; β is reported beside it.
2. **P2 stays on β∥ − β⊥.** It passes in 80–90% of H replicates and fails in 100% under R2. The ρ version is biased by +0.1 under H.
3. **P3.** The slope b = 1 − β∥ is > 0 under R0 as well (ordinary turnover), so it adds nothing beyond P1; its informative form is Δρ∥ (reported). **The intercept test uses the leave-period-out centered variant**: under H its CI contains 0 in 65–85% of replicates; under translation, overshoot, common-mode jump and constant speed (R0, R5, R6, R4) the intercept is flagged positive in 93–100%. In the raw variant persistent agent offsets bias it (H passes in 35%).
4. **P4 rule:** split-half r ≥ 0.3 with permutation p < 0.05. The ICC share u is reported but not used: per-agent noise attenuates it to ≈ 0.09 even when the true agent share is 0.69. **Power is 0.30** at a true agent share of 0.69 (false-positive rate 0.03), so a P4 miss is "inconclusive", not a negative, unless r ≤ 0.
5. Isotropy rival R4 (constant speed) gives β∥ − β⊥ ≈ +0.4 (neither pass nor fail by the P2 rule); reported as such if seen.

## Results by goal period
Replication rule (templated, after Amendment 1): supported if Δρ's 90% CI is above 0 and Δρ∥ > 0; failed if Δρ ≤ 0; mixed otherwise; descriptive if N < 5 or no placebo boundary. bge-small; ± is one jackknife SE.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [NE34](goalperiod-subhypotheses/NE34/README.md) (18 kickoffs) | replication (cross-kickoff) | supported | Δρ +0.26 ± 0.04, 16/18 > 0; Δρ∥ 0.63 vs Δρ⊥ 0.25; intercept +0.12 ± 0.02 (overshoot); agent-constancy r 0.30 (p 0.14) |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | descriptive | N 4, no placebo; ρ_kick 0.29 |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | descriptive | N 4, no placebo; ρ_kick 0.49 |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | descriptive | N 4, no placebo; ρ_kick 0.18 |
| [G07](goalperiod-subhypotheses/G07/README.md) | replication | descriptive | N 4, no placebo; ρ_kick 0.35 |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | descriptive | N 4, no placebo; ρ_kick 0.42 |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | mixed | ρ 0.62 vs ρ0 0.70; Δρ +0.08 ± 0.15 |
| [G12](goalperiod-subhypotheses/G12/README.md) | replication | supported | ρ 0.48 vs 0.75; Δρ +0.27 ± 0.16 |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | supported | ρ 0.54 vs 0.75; Δρ +0.21 ± 0.08 |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | mixed | ρ 0.46 vs 0.56; Δρ +0.10 ± 0.16 |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | failed | ρ 0.54 vs 0.54; Δρ −0.01 |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | failed | ρ 0.53 vs 0.53; Δρ −0.00 |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | supported | ρ 0.36 vs 0.55; Δρ +0.18 ± 0.05 |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | supported | ρ 0.28 vs 0.64; Δρ +0.35 ± 0.08 |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | supported | ρ 0.35 vs 0.73; Δρ +0.38 ± 0.10 |
| [G26](goalperiod-subhypotheses/G26/README.md) | native (+ replication) | mixed | N3 failed (announcement memory 0.37 below 3/3 placebos, no move toward it; day-1 transient confound); replication Δρ +0.13 ± 0.07, Δρ∥ < 0 |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | supported | ρ 0.16 vs 0.58; Δρ +0.43 ± 0.14 |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | supported | ρ 0.36 vs 0.66; Δρ +0.29 ± 0.11 |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | supported | ρ 0.26 vs 0.63; Δρ +0.37 ± 0.07 |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | descriptive | cross-regime (II → III); Δρ +0.20 |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | supported | ρ 0.41 vs 0.84; Δρ +0.43 ± 0.09 |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | supported | ρ 0.23 vs 0.84; Δρ +0.60 ± 0.07 |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | supported | ρ 0.69 vs 0.83; Δρ +0.14 ± 0.06 |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | supported | ρ 0.40 vs 0.81; Δρ +0.42 ± 0.14 |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | supported | ρ 0.55 vs 0.81; Δρ +0.27 ± 0.09 |
| [G44](goalperiod-subhypotheses/G44/README.md) | native | failed | χ^mem #best − #rest +0.00 (bge, p 0.49) / −0.16 (gte); the move's direction is room-specific (+0.31 vs −0.10) |
| [NE38](goalperiod-subhypotheses/NE38/README.md) | native | supported | Opus 5 χ^mem 0.57 / 0.70 vs others' 90th pct 0.47 / 0.40 and its own ordinary 0.05–0.10; move · new goal +0.54 |

## Results
**Headline.** A goal kickoff erases each agent's position relative to the swarm faster than an ordinary night does. The cross-agent memory correlation drops from 0.68 to 0.42 (Δρ = +0.26 ± 0.04 over 18 kickoffs, 16/18 positive, every variant). That is a restoring force toward a new centre. It is not HH246's law: the well is stiffer along the kickoff direction than across it, day 1 overshoots the settled level, and the per-agent susceptibility is not shown to be a trait of the agent.

**Outcome vs prediction**

| Prediction | Credence | Outcome | Verdict |
| --- | --- | --- | --- |
| P1 extra forgetting Δρ > 0 (meta CI > 0, ≥ 2/3 positive) | 0.65 | +0.26 ± 0.04; 16/18; all 7 variants +0.22 to +0.28 | supported |
| P2 isotropy (β∥ − β⊥ CI ∋ 0, \|·\| < 0.2) | 0.35 | −0.17 ± 0.16 (bge) passes; style −0.37 fails; dedupe −0.28 and centered −0.20 neither; scale-free Δρ∥ 0.63 vs Δρ⊥ 0.25 in all variants | passes by rule; fragile |
| P3 slope (Δρ∥ > 0 after Amendment 1) | 0.7 | +0.63 ± 0.27 | supported |
| P3 intercept 0 (centered) | 0.3 | +0.12 ± 0.02 (gte +0.17 ± 0.03); R5/R6 | failed |
| P4 agent constant (r ≥ 0.3, p < 0.05) | 0.2 | r 0.30 (p 0.14); gte 0.48 (p 0.03); centered −0.06; style 0.19; HH form −0.19; power 0.30 | inconclusive |
| P5 named > free | 0.5 | 0.27 vs 0.19 (n free = 2, p 0.27); named-frozen 0.42 vs 0.27 (p 0.22) | not supported (underpowered) |
| P6 no lab effect | 0.75 | p 0.49 | supported |
| P7 sign survives variants | 0.6 | 7/7 | supported |
| P8 weekend gap does not cause it | 0.7 | placebo ρ0 0.73 (weekend) vs 0.69 (weekday) | supported |
| N1 NE38 one-agent kickoff | 0.6 | 0.57 > 0.47 (bge); 0.70 > 0.40 (gte); cos +0.54 | supported |
| N2 G44 #best forgets more | 0.55 | +0.00 / −0.16 | failed |
| N3 G26 announcement inside placebo | 0.6 | percentile 0.0 (3 placebos), no move toward it | failed (confounded) |
| **Overall (rule)** | | P1 holds, P3 slope holds, P2 does not fail | **supported** (the HH-literal shape fails) |

**Synthesis**
1. **The kickoff is a well, not only a push.** Pure translation (R0, H10's uniform push) predicts Δρ = 0; the data give +0.26 in 16/18 kickoffs and +0.25 transverse to k̂. The kickoff resets content in directions it does not name. Ordinary-day memory is higher in regime III (ρ0 ≈ 0.83) than in regime I (≈ 0.62), and the kickoff takes both down to ≈ 0.4.
2. **Anisotropic stiffness.** Forgetting along k̂ is 2–3× the transverse forgetting in the scale-free estimator (all variants). The IV slope version passes the isotropy rule only in the raw variant. Physically: the field fixes the k̂ coordinate (as H10's common target), and a weaker reset scrambles the rest.
3. **Overshoot.** With the agent offsets removed, the swarm on day 1 sits beyond its own plateau along k̂ (a = +0.12). This is H54's day-1 excess (0.24 → 0.11) seen as a law violation: the field is strongest on day 1 and then weakens (remanence), so day 1 is not a partial relaxation toward the final state.
4. **No trait susceptibility yet.** How much an agent forgets at a kickoff is reliable within a kickoff (split-half ≈ 0.9, an upper bound) but does not repeat across kickoffs beyond chance in 3 of 4 variants. The power is low (0.30 at a true agent share of 0.69), so this is "not shown", not "absent". H54's raw move gave r = 0.09.
5. **Natives.** A one-agent field (NE38) acts like a kickoff on that agent only: an operator can quench one agent without touching the others. A room's field (G44) sets where agents go, not how much they forget.

**Instrument lesson (Known issue candidate).** Memory slopes between unit-normalized embedding segments are biased whenever the common component changes size: a day where everyone talks about one thing compresses every agent's deviation and fakes forgetting. Use the disattenuated correlation (split halves of both segments) or rescale by the segment's spread.

**Caveats.** bge and gte agree on every headline except P4 (gte significant) and the G44 sign. The target is a text-embedding proxy. Day 1 includes the kickoff text being quoted. 18 kickoffs with 6–15 agents; per-transition CIs are wide. The previous period's last day may carry wrap-up content (the placebo boundaries do not). The noise ceiling for χ is an upper bound.

**Code.** `scheme/build.py`; `analysis/h97lib.py` (estimators), `calibrate.py`, `synthetic.py`, `run.py`, `natives.py`, `figures.py`, `period_folders.py`, `write_rows.py`, `confirm.py` (not run). **Data:** `data/processed/H97-quench-restoring-force/` (≈ 3 MB). **Figures:** `figures/summary_obs.pdf`, `figures/synthetic_compact.pdf`.

**Per-period estimates:** rows written with `write_estimates` (`kickoff_memory_rho`, `kickoff_extra_forgetting_drho[_par|_perp]`, `kickoff_isotropy_beta_par_minus_perp`, `kickoff_overshoot_intercept`; channels bge, gte, centered; natives `ne38_opus5_chi_mem`, `g44_chi_best_minus_rest`, `g26_memory_rho_across_announcement`).

## Confirmatory test (written 2026-10-04 after exploration; NOT run)
`analysis/confirm.py` refuses to run without `--confirm --i-understand-this-uses-the-locked-holdout`, a clean git state for its files and a holdout-ledger check. `--dry-run` runs the identical in-memory pipeline on stand-ins (#11–#13, #38–#42): C1 Δρ +0.31 ± 0.07 (8/8), C2 0.75 (p 0.14), C3 +0.11 ± 0.04, C4 ρ 0.53 (circular on stand-ins). Frozen predictions on the held-out kickoffs #9, #14, #15, #28, #29, #34, #43, #45–#50 (#22, #23, #32 excluded for H10):
- **C1:** meta Δρ 90% CI above 0 and ≥ 2/3 positive (credence 0.85).
- **C2:** anisotropy, Δρ∥ > Δρ⊥ in ≥ 2/3, sign p < 0.05 (credence 0.55).
- **C3:** overshoot intercept (centered) CI above 0 (credence 0.7).
- **C4:** agent constancy out of sample, Spearman of exploration vs held-out mean χ ranks, p < 0.05 (credence 0.3).
- Reuse: H54 plans the same held-out kickoffs with a different statistic (day-1 target percentile); #34 and #45 have activity runs (H05, H02, H04). Disclose in both cards and `LOG.md`.

## Round 2 redirects (2026-10-04)
- **H97-R1. Time-resolved relaxation.** Fit ρ(t) and the k̂ coordinate hour by hour after the kickoff to separate the day-1 overshoot (field decay, H54 remanence) from the restoring rate; test whether the overshoot scales with kickoff specificity.
- **H97-R2. Read-out-resolved forgetting.** Use the context ledger: does an agent's memory drop at its first read-out call of the kickoff (H08 gating), and do late readers forget less?
- **H97-R3. Agent constancy with power.** Pool the per-agent χ hierarchically (exception (d)) over kickoffs and both models; the holdout C4 is the out-of-sample check.

## Notes
- 2026-10-04: promoted from HH246 (Vivian). Card, observables and predictions written before any real-data statistic.
- #23 is excluded although it is not in `holdout.json` (H10's confirmatory pair #22 → #23 must stay blind on both sides).
- 2026-10-04: calibration (placebo boundaries, full space only) and synthetic → Amendment 1 → replication (25 transitions, 7 configurations) → natives → per-period estimates → confirm.py frozen and dry-run.
- Proposed DEFINITIONS.md variants (H97): **kickoff memory ρ** = disattenuated cross-agent correlation between agents' pre-kickoff (previous period's last day) and day-1 mean statement vectors, split-half true variances; **placebo memory ρ0** = the same on ordinary consecutive days of the same period unit; **extra forgetting Δρ** = ρ0 − ρ; **per-agent susceptibility χ^mem_ip** = 1 − (agent's own offset memory relative to leave-agent-out centroids); **overshoot intercept a** = mean day-1 displacement along k̂ minus (1 − β∥) × mean distance to the settled (days 2–5, leave-agent-out) level.
