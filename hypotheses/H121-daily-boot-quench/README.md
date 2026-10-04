# H121: The daily boot is a reproducible quench: hundreds of replicas of relaxation to the steady state

**Status:** exploratory round 1 done (2026-10-04; non-holdout only). **The HH's single-exponential relation fails in regime III (kill fires); the boot is a one-call spike plus a slow day-scale talk excess.**
- **Regimes I–II:** the first call of the day talks with probability 0.49 against a steady state of 0.12. The excess is gone by the next call: registered τ_boot median 0.99 calls, K_boot ≈ 1 (τ₀ at its 1-call floor, so this agreement is nearly trivial).
- **Regime III:** pooled K_boot = 22 [6.9, 71] (27 units): the kill fires. The curve has a weak first-call spike (excess 0.044) and a slow excess of +12% [4, 20]% over calls 20–240. The single exponential locks onto one part or the other.
- **Post hoc (labelled):** the fast part relaxes in 0.54 [0.41, 0.67] calls (I) and 2.4 [0.9, 27] calls (III), within ×2 of τ₀/(1 − g_lag) (K_fast 0.51 and 2.0).
- Collapse across days and the late-booter contrast are untestable at day resolution; natives NE14, NE43 and NE42 are mixed (registered fits uninformative). Scorecard A1 B1 C0 D1 E0 F1 G1 H1 I0. `confirm.py` frozen, guarded and dry-run; **not run**.
(Card, observables and predictions written 2026-10-04 22:00 UTC, before any real-data statistic; approved by Vivian in the dashboard vetting panel 2026-10-04 from HH361.)
**Research question (GOALS.md):** **Q2** (what is field and what is coupling?): the boot is a scheduler field by construction; the test asks whether the relaxation after it carries the coupling's signature τ = τ₀/(1 − g_lag). **Q3** second (how close to criticality; a slowed collective mode would be collective order beyond the field).
**Fields:** stat mech (kinetic Ising, quench dynamics, linear response), dynamics
**Literature:** model references in [`physics-models/02-nonequilibrium-ising/README.md`](../../physics-models/02-nonequilibrium-ising/README.md) ("Mean-field forward version") and [`physics-models/09-hawkes/README.md`](../../physics-models/09-hawkes/README.md). Glauber, *J. Math. Phys.* 4, 294 (1963)†; Onsager, *Phys. Rev.* 37, 405 (1931)† (regression hypothesis). No notes file in `literature/` covers quench relaxation in kinetic mean field.
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent (Claude Code agent excluded); Population N(t) (active variant: agents with ≥ 30 receiving calls that PT day); Regime; Driving / external field; **Call cycle (hop)** (H50); **Read-out loop gain g_lag** (H67; read as data, never refitted); **Mean-field split** (H99) for the reading of the boot as a collective-mode quench. New named variants proposed for DEFINITIONS.md (not edited here), defined under Model: *boot (daily quench)*, *boot curve m(k)*, *boot relaxation time τ_boot*, *single-agent call memory ρ_self*, *slowing ratio K_boot*.
**From:** HH361 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/02-nonequilibrium-ising/` (primary: mean-field Glauber relaxation), `physics-models/09-hawkes/` (rival: discrete per-call branching form)
**Data inputs (shared tables first):** DQ1 `call_windows` (receiving calls, talk flag, t_call, gap kind); `outages_fixed/outages.parquet` (village-off gaps); `calendar`, `period_units`, `roster`. Read as data only: H67 `results/units.parquet` and `periods.parquet` (g_lag per unit and period). Not used: `activity_bins` (minute grids; talk minutes have ρ_⊥(1) ≈ 0, Known issues).

## Source HH (verbatim from the HH list, including refinements)
- **HH361 · The daily boot is a reproducible quench: hundreds of replicas of relaxation to the steady state.** Every day, all agents start from off. That is the same quench repeated on every active day.
  - *Prediction:* the collective talk magnetization's approach to its daily steady state is one exponential on the call clock, with τ = τ₀/(1 − g_lag) using H67's g_lag (unfitted), and the curves collapse across days within a regime.
  - *Check:* align days at the first call; per-call collective mean; fit τ per regime; compare with the prediction from g_lag and the single-agent call time.
  - *Kill:* τ off by more than ×2 from the prediction, or no collapse across days.
  - *Impostors:* the boot is a scheduler field by construction; the test is whether the relaxation after it carries the coupling's signature (H99 found kicks outlive the fluctuation clock, so this is a live test).
  - *Models:* 02, 09 · *Builds on:* H67, H99, H38, HH344

## Question
After the daily boot, does the collective talk rate relax to its steady state as one exponential on the call clock, at the rate mean-field Glauber predicts from the single-agent call memory and H67's read-out gain, τ = τ₀/(1 − g_lag)? Do the boot curves collapse across days?

**Why it matters.** Each active day is one replica of the same quench, so the boot gives hundreds of relaxation curves with no operator input. If they relax at τ₀/(1 − g_lag), the coupling measured from fluctuations (H67) also governs the response to a large, common perturbation. If they relax much more slowly, as H99 found for kicks (×9.5), the boot transient is set by something else: an agent-internal start-up routine (reading memory and backlog, planning), or a slow field.

## Design: two layers (STANDARDS §4)
- **Replication (layer 1):** the common estimator on every eligible non-holdout period unit (`period_units`: ≥ 3 agents with an eligible agent-day; ≥ 8 eligible agent-days in the unit). Every eligible agent-day is one boot replica. One README per goal period, role `replication`. Units of a split period are fitted separately and pooled by a random-effects mean of ln τ (CLAUDE.md exception (d)). Regime-level pooling of the *same* statistic is reported only as a summary of per-unit fits; the regime collapse test compares days, which is the HH's design (exception (c): the replicated transition is the object).
- **Period-native tests (layer 2), each with its own dated prediction in its folder:**
  - **NE14** (#35 ∪ 36a, regime II → 36b ∪ 36c, regime III; N = 12, fixed roster): the boot changes from session starts to the runner's start of perma-computer-use, while g_lag switches on (H67: −0.06 → 0.12).
  - **NE43** (51f → 51g, 2026-08-05): the operator's daily pause/resume messages stop. If the boot transient is the resume message (an exogenous kick), its amplitude or τ changes; if it is the runner's start and agent start-up, neither changes (H38: the day-edge share did not drop).
  - **NE42** (#39 → #40 → #41): g_lag 0.144 → 0.003 → 0.189 (H67) at a fixed roster: a dose test of τ_boot/τ₀ = 1/(1 − g_lag).
- **Partition contrast (STANDARDS §3; inside replication):** synchronous booters vs late booters. A synchronous boot excites the collective mode (τ₀/(1 − g)); an agent that boots into a swarm already in steady state excites a transverse mode (τ₀). Coupling predicts τ_late ≤ τ_sync. An agent-internal catch-up field predicts τ_late ≥ τ_sync, because a late booter has more backlog to read.

## Model
**From:** `physics-models/02-nonequilibrium-ising` (mean-field Glauber), mapped onto the per-call clock (H40: coupling runs on the call clock in regimes II–III; H67: read-out gain).

**Degrees of freedom.** Agent i's k-th receiving call of PT day d (k = 0 is its first call of the day; `call_windows` with `ctx_mode != summary`, sorted by `t_call`, `turn_id`). The talk spin is Y_ikd = 1 if the call is a talk call (`talk`). An agent-day is eligible with ≥ 30 receiving calls. Each agent-day is truncated at the first village-off gap ≥ 30 min that is not at a day edge (`outages_fixed`), so a mid-day restart is not mixed into the curve.

**Boot (daily quench), named variant.** The boot of agent-day (i, d) is its call k = 0. Every agent is off before it. In regime III the runner starts all agents within minutes (H38), so the boot is a common, synchronous quench.

**Boot curve m(k).** m(k) = mean of Y_ikd over the eligible agent-days of a unit (equal weight per agent-day), for k = 0 … K_max. K_max = min(400, the 25th percentile of eligible agent-day call counts in the unit).

**Mean-field Glauber after a quench.** τ₀ dm/dk = −(1 − g) m + h. After the quench m(k) = m_∞ + A e^{−k/τ}, with **τ = τ₀/(1 − g)**. Here g = g_lag (H67 read-out loop gain of talk, per unit; unfitted) and τ₀ is the single-agent relaxation time on the call clock.

**Single-agent call memory ρ_self and τ₀ (named variants).** ρ_self = the lag-1 autocorrelation of an agent's own talk spin across consecutive receiving calls, pooled over agent-days, after centring Y per (agent, day, 30-min block) (H25's centring; removes slow drifts and the boot itself). Only calls ≥ 60 min after the agent's boot and ≥ 30 min before its last call enter. Then
  **τ₀ = max(1, −1/ln ρ_self) calls** (primary). One call is the update quantum: a heat-bath update with no self-memory is fully relaxed after one call. Variant: unfloored τ₀ (ρ_self > 0 only).

**Predictions of the boot relaxation time (unfitted).**
- **HH form (primary):** τ_pred = τ₀/(1 − g_lag).
- **Discrete per-call form (variant, model 09 / linear AR reading):** a deviation decays per call by ρ_self + g_lag, so τ_pred,AR = −1/ln(ρ_self + g_lag), floored at 1 call. It is the exact mean field of a linear per-call update with self-memory ρ_self and read-out gain g_lag at equal call rates. The two forms differ by ≤ ×1.4 at village values (ρ_self ≤ 0.5, g ≤ 0.25); the kill tolerance is ×2.

**Slowing ratio K_boot (named variant).** K_boot = τ_boot / τ_pred. Glauber predicts K_boot = 1 (kill outside [0.5, 2]). A slow boot field gives K_boot ≫ 1.

**Measured τ_boot.** Weighted least squares of m(k) = m_∞ + A e^{−k/τ} on k = 0 … K_max (weights = agent-days observed at k; τ bounded to [0.2, 5 K_max]). Uncertainty: cluster bootstrap over PT days within the unit (B = 200); units with < 4 days resample agent-days and are flagged (H67: day blocks with few days are anti-conservative). Wall-clock variant: the same fit on minutes since the agent's boot (1-min bins), compared with τ_pred × the unit's median steady-state call interval.

**One exponential.** Two-fold cross-validation over days (odd vs even PT days; units with < 2 days split agent-days): the double exponential m_∞ + A₁e^{−k/τ₁} + A₂e^{−k/τ₂} against the single. *One exponential adequate* if the double cuts the held-out squared error by < 10%.

**Collapse across days.** Per-day fits of the same form (day curve = mean over that day's eligible agents, log-spaced k bins), with an agent-bootstrap CI per day. A day is *resolved* if its τ_d CI spans less than ×4 (hi/lo < 4). **Collapse share** = the share of resolved days with τ_d within ×2 of the regime's pooled τ_boot (the median of unit τ_boot in the regime). *Collapse holds* if the share is ≥ 1/2 (HH kill: "no collapse"); reported with Cochran's I² of ln τ_d per unit.

**Late-booter contrast.** Per day, t₀ = the median boot time of its eligible agents. *Synchronous* agent-day: boot within 10 min of t₀. *Late* agent-day: boot ≥ 60 min after t₀, with ≥ 3 other agents already booted ≥ 30 min earlier. τ_sync and τ_late from the pooled boot curves of each class per regime (day bootstrap). Mean field: τ_sync/τ_late = 1/(1 − g); internal catch-up field: τ_late ≥ τ_sync.

**What each reading predicts.**
| World | τ_boot | K_boot | Collapse | τ_late vs τ_sync |
| --- | --- | --- | --- | --- |
| Mean-field Glauber coupling | τ₀/(1 − g) ≈ 1–2 calls | ≈ 1 | yes | τ_late < τ_sync (×(1 − g)) |
| Agent-internal start-up routine (slow field) | its own lifetime | ≫ 1 | yes, if the routine is fixed | τ_late ≥ τ_sync |
| Day-specific exogenous kick (resume message, kickoff) | varies by day | ≫ 1 | no | τ_late ≈ τ_sync |
| Independent agents (g = 0) | τ₀ | ≈ 1 (trivial) | yes | equal |

## Data scheme (`scheme/`)
- **Inputs:** `call_windows` (turn_id, agent, pt_date, goal_no, regime, holdout, talk, ctx_mode, t_call, gap_kind, first_of_day), `outages_fixed/outages.parquet` (t_start, village_off, at_day_edge), `calendar` (holdout), `period_units` (unit days), `roster` (Claude Code excluded). H67 `results/units.parquet` and `periods.parquet` (g, g_lo, g_hi per unit / period; read only).
- **Transform (`scheme/build.py`):** per non-holdout unit (held-out days dropped by `calendar.holdout` and `common.holdout_mask`, asserted twice):
  1. receiving calls per agent-day, sorted (t_call, turn_id); k index; minutes since the agent's boot; truncation at the first non-edge village-off gap ≥ 30 min;
  2. eligible agent-days (≥ 30 calls); boot time, day t₀, synchronous / late class;
  3. per-unit metadata: N, days, eligible agent-days, median steady-state call interval, H67 g_lag.
- **Output:** `data/processed/H121-daily-boot-quench/` with `calls/<unit>.parquet` (agent, pt_date, k, Y, minutes since boot, block id, class; codes only), `unit_meta.parquet`, `results/`, `synthetic/`, `natives/`, `_provenance.json`. Budget ≤ 80 MB.
- **Regimes covered:** I, II, III (non-holdout). Fits are within unit.

## Observables
Per unit (per period by random-effects pooling of ln τ over units; per regime as the median of unit values):
1. Boot curve m(k), τ_boot [95% CI], m_∞, A, m(0); the wall-clock τ_boot (min).
2. ρ_self, τ₀, τ_pred (HH form), τ_pred,AR, K_boot and K_boot,AR with CIs (bootstrap ratio; g_lag's CI propagated by drawing g from its normal approximation).
3. One-exponential CV gain of the double exponential.
4. Per-day τ_d, collapse share (per regime), I² per unit.
5. Late-booter contrast: τ_sync, τ_late, their ratio, counts (per regime).
6. Phase-diagram slope (descriptive): across periods within regime III, the slope of ln(τ_boot/τ₀) on −ln(1 − g_lag) (Glauber: 1).

## Null / baseline
- **The model is the null:** K_boot = 1. Its finite-sample bias at real counts comes from the Glauber synthetic on real call grids (axis F).
- **Independent agents (g = 0):** τ_boot = τ₀. A unit whose g_lag CI includes 0 tests only the single-agent part; its verdict is labelled accordingly (K_boot still has to lie in [0.5, 2]).
- **Shuffled-day collapse null:** the collapse share under the synthetic heterogeneous-day world sizes the collapse test (axis F).
- **Rivals:** an agent-internal slow boot field; day-specific exogenous kicks; the discrete per-call form (model 09). Each is simulated on real call grids.

## Impostors (STANDARDS §1)
| Impostor | How H121 removes it | Status |
| --- | --- | --- |
| Scheduler field | The boot *is* the scheduler field by construction (the measured perturbation). The test is on the relaxation after it, on each agent's own call clock (k since its boot), so staggered starts do not smear the curve. ρ_self uses block-centred steady-state calls (the boot and day ends excluded). Day ends are outside K_max for almost all agent-days; mid-day restarts are truncated. The late-booter contrast separates the collective quench from the agent's own restart. | removed for the relaxation (the boot itself is the object) |
| Exogenous field (kickoff, goal, operator) | Kickoff days (day 1 of each goal) reported with and without (variant); the operator's daily resume message is the NE43 native; human messages are not modelled (they are part of the steady state). | partly |
| Shared model priors | Each agent-day is aligned to its own boot; ρ_self is per agent (block-centred). Family composition differs between units, so unit-level τ_boot is reported with the share of each lab (descriptive) rather than corrected. | partly |
| Contemporaneous convergence | Not a copying claim: the coupling enters only through H67's g_lag, which is placebo-corrected (matched-lag in-flight). The late-booter contrast is the partition test (STANDARDS §3) of whether the collective quench differs from a transverse one. | partly (via H67) |

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** an agent-internal slow start-up field (no coupling needed); day-specific exogenous kicks (resume message, kickoff); the discrete per-call branching form (model 09; τ = −1/ln(ρ_self + g)); independent agents.
**Locked holdout used for confirmation:** none yet. `analysis/confirm.py` (frozen 2026-10-04, guarded, dry-run on stand-ins 27, 24, 41, 51g; **not run**) targets #22, #28 (regime I), #43 and the #51 tail (regime III), with H67's confirmatory g_lag as the unfitted input (H67's confirm must run first). C1: the registered K_boot > 2 again in regime III; C2: K_fast in [0.5, 2] (regime III); C3: regime-I τ_fast < 1 call; C4: regime-III slow excess > 0; C5: regime-I spike ≥ 0.2 and no spike in the #51 tail.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Ledger-defined boot and call index in every regime; τ₀ floored at 1 call in 58/67 units (coupling enters τ_pred by ≤ ×1.4) |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | One exponential fails on pooled curves (spike + slow tail); CV test unpowered; call vs wall clock reported |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 0 | Regime-III K_boot 22 [6.9, 71]; per-day fits unresolved |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | τ_pred matches regime-I/II τ_boot (K ≈ 1), fails in III; post hoc K_fast within ×2 |
| E interventional | predicts the change across a natural experiment | 0 | NE14, NE43, NE42 uninformative on the registered statistic |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | S1, S3 passed; S2 narrow fail; S4 failed and replaced pre-data; two-timescale world not simulated |
| G ground truth | agrees with known structure | 1 | NE43 agrees with H38 (runner schedule); call-clock relaxation agrees with H40 |
| H comparative | beats the named rivals | 1 | Slow-field rival fits the regime-III tail; call-clock Glauber fits the fast part (post hoc) |
| I transfer | holds in other same-mode periods, including the holdout | 0 | No holdout run |

**Scorecard plan.** A from the mapping audit (eligible share, truncations, regime invariance of the estimator). B from the one-exponential CV and the wall-clock vs call-clock comparison. C from K_boot against the null band and the day-split CV. D from K_boot (the unfitted τ_pred) and the late-booter sign. E from NE14, NE43, NE42. F from the synthetic worlds below. G from H38's day-edge finding and H99's kick result. H from the rival comparison (HH form vs AR form vs slow field). I stays 0 until the holdout runs.

## Prediction
*Written 2026-10-04 22:00 UTC, before any real-data statistic. Seen beforehand: table schemas; skeleton counts (receiving calls per agent-day: median 413 / 651 / 589 in regimes I / II / III; non-holdout `period_units`); the published results of H67 (g_lag regime-III median 0.13, regime I 0.005), H99 (talk ρ_⊥(1) ≈ 0 on minutes; kicks outlive the fluctuation clock ×9.5; collective talk memory excess +0.077 in regime III), H38 (two thirds of regime-III co-activation is the runner's daily start/stop) and H40 (call clock in regimes II–III). Not seen: any boot curve, any per-call autocorrelation.*

**Synthetic validation (axis F), before real data.** Talk simulated on the real call grids (real t_call per agent and day) of three units: 27 (regime I, N 10), 41 (regime III, N 15) and 51c (regime III, N 25). Each world is a linear per-call update p_ik = b + ρ(Y_i,k−1 − b) + J·(R_ik − R̄) + F_i(k), with R_ik = other agents' talk calls since i's previous call and J = g/(N − 1). The boot starts every agent in the talking state (Y_i,−1 = 1).
- **S1 recovery (Glauber worlds,** ρ = 0.5, g ∈ {0, 0.15, 0.3, 0.6}): median τ_boot within ±25% of the world's true per-call relaxation time, and the 95% CI covers it in ≥ 80% of replicates. [0.6]
- **S2 τ₀:** ρ_self within ±0.05 of the planted ρ in every world (including the field world). [0.7]
- **S3 kill sizing:** in the Glauber worlds K_boot (against the true form) lies in [0.5, 2] in ≥ 90% of replicates; in the slow-field world (g = 0.13, F_i(k) = 0.25 e^{−k/30}) K_boot > 2 in ≥ 90%. [0.7]
- **S4 collapse sizing:** collapse holds in ≥ 80% of replicates of a day-homogeneous slow-field world, and fails in ≥ 80% of a heterogeneous world (τ_F,d log-uniform over ×1/3 to ×3 around 30 calls). [0.5]

**Real data (exploratory, non-holdout).**

| # | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| P1 | **The HH relation (kill test).** The regime-pooled K_boot (HH form) lies in [0.5, 2] in regime III, and in ≥ 1/2 of eligible units. | regime-III K_boot outside [0.5, 2] (**kill**) | 0.15 |
| P1′ | **Rival expected instead:** τ_boot > 2 τ_pred, i.e. the boot transient outlives the call-clock prediction (as H99's kicks did), in ≥ 2/3 of units of every regime. | K_boot ≤ 2 in > 1/3 of units | 0.7 |
| P2 | **One exponential.** The double exponential cuts the held-out squared error by < 10% in ≥ 2/3 of units. | ≥ 10% in > 1/2 of units | 0.4 |
| P3 | **Collapse across days (kill test).** Collapse share ≥ 1/2 in each regime with ≥ 10 resolved days. | share < 1/2 in regime III (**kill**) | 0.55 |
| P4 | **Late-booter sign.** In regime III, τ_late ≤ τ_sync (coupling sign), if ≥ 30 late agent-days exist. | τ_late > τ_sync with CI excluding equality (catch-up field) | 0.35 |
| P5 | **Regime dependence.** τ_boot (in calls) differs between regime I and regime III by more than the Glauber factor (1 − g_I)/(1 − g_III) ≈ 1.15; i.e. the scaffold, not the coupling, sets the boot. | ratio of regime medians within [0.8, 1.25] | 0.7 |
| P6 | **Phase-diagram slope** (descriptive; reported only if the synthetic gives power ≥ 0.8 for slope 0 vs 1). Slope of ln(τ_boot/τ₀) on −ln(1 − g_lag) across regime-III periods includes 1. | slope CI excludes 1 | 0.3 |

**Amendment A1 (2026-10-04 22:42 UTC, after the synthetic validation, before any real-data statistic).** Seen: only synthetic runs on the real call grids of units 27, 41 and 51c (12 replicates × 6 worlds, B = 50; `data/processed/H121-daily-boot-quench/synthetic/`).
- **World grid:** g = 0.6 was replaced by g = 0.45. With ρ = 0.5 the per-call update is unstable at ρ + g ≥ 1, so g = 0.6 is not a valid Glauber world. The HH form and the AR form are equal only when ρ_self = 0. H67's g_lag is the *direct* per-call jump with Y_{c−1} controlled. So the self-consistent mean-field prediction is the AR form, τ ≈ τ₀/(1 − g_lag/(1 − ρ_self)). The card's claim of "≤ ×1.4" between the two forms holds only for g ≤ 0.15; at ρ = 0.5 and g = 0.25 they differ by ×1.8. Both forms stay reported; the HH form stays primary as registered.
- **S1 recovery: passed on bias, marginal on coverage.** The median relative error of τ_boot is within ±19% in every cell (pooled −4% in coupling worlds, +1% in field worlds). Pooled 95% CI coverage is 0.84 in coupling worlds and 0.78 in field worlds; single cells range from 0.50 to 1.00 (12 replicates each). The bootstrap CI is mildly anti-conservative, so per-unit CIs are read as ≈ 90% intervals.
- **S2 ρ_self: failed narrowly.** Block centring biases ρ_self by −0.03 (max |error| 0.058 > 0.05). This lowers τ₀ by about 10% at ρ = 0.5 and changes nothing when τ₀ hits its 1-call floor. No correction is applied; the bias is quoted.
- **S3 kill sizing: passed for the decision that matters.** In the Glauber worlds with g ≤ 0.3, K_boot lies in [0.5, 2] in 91% of replicates against the true τ (90% for both the HH and the AR forms). Near criticality (g = 0.45) the HH form drifts above the band (K up to 3.8). In the slow-field world K_boot > 2 in 100% of replicates (median K ≈ 20).
- **S4 collapse: failed as registered; statistic replaced.** The registered "share of resolved days within ×2" holds in 100% of homogeneous worlds, but also in 75–100% of heterogeneous ones. A log-uniform ×1/3–×3 spread puts 63% of days inside ×2 anyway, so the statistic cannot detect it. **New primary collapse statistic:** the DerSimonian–Laird between-day SD of ln τ_d per unit (resolved days, agent-bootstrap SEs). *Collapse holds* in a unit if SD_between ≤ ln 2/1.96 = 0.354, i.e. 95% of days fall within ×2. It holds in a regime if it holds in ≥ 1/2 of that regime's units with ≥ 3 resolved days. Calibration (8 replicates × 3 units per world): it holds in 100% of homogeneous worlds (median SD 0.15) and in 12.5% of heterogeneous worlds (median 0.53). The registered share statistic is still reported.
- **One exponential:** the double exponential gains nothing in single-exponential worlds (median CV gain −0.01 to +0.02; the test passes in 99% of replicates), so the test is correctly sized. Its power against a real two-timescale boot was not simulated.

**Per-period verdict rule (replication):** *supported* if the period's pooled K_boot (HH form) CI overlaps [0.5, 2] with its point estimate inside, and the one-exponential test passes; *failed* if K_boot's CI lies entirely outside [0.5, 2]; *mixed* otherwise; *descriptive* if the period has < 8 eligible agent-days or τ_boot is unresolved (CI spans > ×10).

Native predictions are in `goalperiod-subhypotheses/NE14/`, `NE43/` and `NE42/` (written before those runs).

## Results by goal period
Per-period rule (card). **5 supported, 2 failed, 28 descriptive** (35 periods; 67 units fitted; 3,135 boot replicas). "Descriptive" dominates because the registered single-exponential fit is unresolved (CI spans > ×10) in most units: the real boot curve has two timescales (see Results).

| Period | Role | Verdict | Key numbers (period random-effects pool; post hoc fast part) |
| --- | --- | --- | --- |
| [G02](goalperiod-subhypotheses/G02/README.md) | replication | descriptive | I, 7 agent-days (< 8): not fitted |
| [G03](goalperiod-subhypotheses/G03/README.md) | replication | descriptive | I, 12 agent-days: τ_boot 77.1 [8.4, 707.0] calls · K_boot 62.2 [6.5, 594.7] · post hoc τ_fast ∞, e(0) 0.23 |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | descriptive | I, 96 agent-days: τ_boot 24.1 [0.0, 19036.8] calls · K_boot 17.3 [0.0, 8095.3] · post hoc τ_fast 0.50, e(0) 0.29 |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | descriptive | I, 20 agent-days: τ_boot 1.5 [0.4, 5.8] calls · K_boot 1.1 [0.2, 5.0] · post hoc τ_fast 1.27, e(0) 0.55 |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | descriptive | I, 56 agent-days: τ_boot 16.1 [0.0, 32190.0] calls · K_boot 16.2 [0.0, 32703.8] · post hoc τ_fast 0.00, e(0) 0.27 |
| [G07](goalperiod-subhypotheses/G07/README.md) | replication | descriptive | I, 8 agent-days: τ_boot 0.5 [0.0, 52.2] calls · K_boot 0.5 [0.0, 50.1] · post hoc τ_fast 0.64, e(0) 0.48 |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | supported | I, 72 agent-days: τ_boot 0.7 [0.4, 1.4] calls · K_boot 0.7 [0.4, 1.4] · post hoc τ_fast 0.84, e(0) 0.30 |
| [G10](goalperiod-subhypotheses/G10/README.md) | replication | descriptive | I, 35 agent-days: τ_boot 0.7 [0.0, 11.5] calls · K_boot 0.7 [0.0, 11.3] · post hoc τ_fast 0.60, e(0) 0.39 |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | descriptive | I, 35 agent-days: τ_boot 153.0 [3.6, 6480.3] calls · K_boot 148.9 [3.5, 6265.1] · post hoc τ_fast 0.53, e(0) 0.37 |
| [G12](goalperiod-subhypotheses/G12/README.md) | replication | descriptive | I, 28 agent-days: τ_boot 0.6 [0.0, 161.0] calls · K_boot 0.6 [0.0, 137.8] · post hoc τ_fast 0.51, e(0) 0.25 |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | descriptive | I, 60 agent-days: τ_boot 1.0 [0.0, 35.9] calls · K_boot 1.0 [0.0, 35.9] · post hoc τ_fast 0.87, e(0) 0.34 |
| [G16](goalperiod-subhypotheses/G16/README.md) | replication | descriptive | I, 35 agent-days: τ_boot 0.8 [0.0, 273.7] calls · K_boot 0.7 [0.0, 256.2] · post hoc τ_fast 0.97, e(0) 0.40 |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | descriptive | I, 35 agent-days: τ_boot 1.1 [0.0, 719.8] calls · K_boot 1.1 [0.0, 691.1] · post hoc τ_fast 1.61, e(0) 0.37 |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | descriptive | I, 75 agent-days: τ_boot 53.1 [2.7, 1048.2] calls · K_boot 46.2 [2.4, 899.0] · post hoc τ_fast 0.49, e(0) 0.38 |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | descriptive | I, 71 agent-days: τ_boot 36.9 [0.0, 86594.5] calls · K_boot 33.8 [0.0, 97619.7] · post hoc τ_fast 0.49, e(0) 0.45 |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | descriptive | I, 92 agent-days: τ_boot 0.9 [0.2, 3.6] calls · K_boot 0.9 [0.2, 3.6] · post hoc τ_fast 0.27, e(0) 0.50 |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | failed | I, 42 agent-days: τ_boot 1841.6 [1608.6, 2108.4] calls · K_boot 1829.7 [1476.7, 2267.2] · post hoc τ_fast 0.00, e(0) 0.29 |
| [G23](goalperiod-subhypotheses/G23/README.md) | replication | failed | I, 50 agent-days: τ_boot 0.2 [0.2, 0.2] calls · K_boot 0.2 [0.2, 0.2] · post hoc τ_fast 0.00, e(0) 0.37 |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | supported | I, 50 agent-days: τ_boot 0.5 [0.3, 1.1] calls · K_boot 0.5 [0.3, 1.1] · post hoc τ_fast 0.57, e(0) 0.46 |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | descriptive | I, 49 agent-days: τ_boot 0.9 [0.0, 45.5] calls · K_boot 0.9 [0.0, 45.0] · post hoc τ_fast 1.14, e(0) 0.46 |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication | supported | I, 50 agent-days: τ_boot 1.9 [0.7, 5.6] calls · K_boot 1.9 [0.6, 5.6] · post hoc τ_fast 3.01, e(0) 0.35 |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | descriptive | I, 100 agent-days: τ_boot 0.2 [0.0, 7.4] calls · K_boot 0.2 [0.0, 7.3] · post hoc τ_fast 0.00, e(0) 0.40 |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | descriptive | I, 55 agent-days: τ_boot 0.2 [0.0, 1.1] calls · K_boot 0.2 [0.0, 1.2] · post hoc τ_fast 0.00, e(0) 0.26 |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | descriptive | I, 56 agent-days: τ_boot 5.6 [0.8, 41.3] calls · K_boot 5.8 [0.8, 42.3] · post hoc τ_fast 0.00, e(0) 0.06 |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication | descriptive | II, 33 agent-days: τ_boot 0.3 [0.0, 441.8] calls · K_boot 0.3 [0.0, 454.4] · post hoc τ_fast 0.47, e(0) 0.34 |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | supported | II, 60 agent-days: τ_boot 0.8 [0.4, 1.6] calls · K_boot 0.8 [0.4, 1.5] · post hoc τ_fast 0.79, e(0) 0.44 |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication (NE14 native separate) | descriptive | II/III, 60 agent-days: τ_boot 19.7 [0.1, 2671.3] calls · K_boot 18.1 [0.2, 2065.0] · post hoc τ_fast 1.30, e(0) 0.16 |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | descriptive | III, 36 agent-days: τ_boot 1980.0 [1.3, 2988550.4] calls · K_boot 1544.4 [1.0, 2314165.4] · post hoc τ_fast 0.00, e(0) 0.03 |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | descriptive | III, 211 agent-days: τ_boot 3.6 [0.4, 30.4] calls · K_boot 3.4 [0.4, 28.1] · post hoc τ_fast 1.43, e(0) 0.10 |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication + NE42 | descriptive | III, 74 agent-days: τ_boot 0.7 [0.1, 4.2] calls · K_boot 0.6 [0.1, 3.6] · post hoc τ_fast 0.77, e(0) 0.11 |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication + NE42 | descriptive | III, 74 agent-days: τ_boot 1.1 [0.0, 81.6] calls · K_boot 1.1 [0.0, 79.9] · post hoc τ_fast 2.12, e(0) 0.11 |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication + NE42 | descriptive | III, 75 agent-days: τ_boot 3.5 [0.0, 263.0] calls · K_boot 2.8 [0.0, 213.5] · post hoc τ_fast 3.07, e(0) 0.10 |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | supported | III, 78 agent-days: τ_boot 2.4 [0.8, 7.1] calls · K_boot 1.9 [0.6, 5.7] · post hoc τ_fast 1.87, e(0) 0.12 |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | descriptive | III, 66 agent-days: τ_boot 160.6 [6.1, 4198.4] calls · K_boot 123.0 [4.7, 3221.0] · post hoc τ_fast n/a, e(0) -0.00 |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication (NE43 native separate) | descriptive | III, 1186 agent-days: τ_boot 107.1 [14.2, 807.2] calls · K_boot 91.6 [12.2, 687.9] · post hoc τ_fast ∞, e(0) 0.02 |
| [NE14](goalperiod-subhypotheses/NE14/README.md) | native | mixed | II side τ_boot 0.90 [0.42, 1.38]; III side unresolved (at bound); post hoc τ_fast 0.90 → 0.90 calls, spike amplitude ×0.14 |
| [NE43](goalperiod-subhypotheses/NE43/README.md) | native | mixed | registered fits at opposite bounds (uninformative); post hoc: no first-call spike on either side; slow excess +0.13 → +0.17 |
| [NE42](goalperiod-subhypotheses/NE42/README.md) | native | mixed | τ_boot/τ₀ 0.67 → 1.14 → 3.46 (CIs overlap); predicted 1.17 → 1.00 → 1.23 |

## Results
*Exploratory round 1, 2026-10-04: 67 non-holdout units in 34 goal periods, 3,135 eligible agent-days (boot replicas), receiving calls from the DQ1 context ledger. Numbers from `data/processed/H121-daily-boot-quench/results/{units,periods,days}.parquet`, `summary.json`, `natives.json`, `posthoc.json`; synthetic in `synthetic/`. Code: `scheme/build.py`, `analysis/h121lib.py`, `synthetic.py`, `synthetic_collapse.py`, `run.py`, `summarize.py`, `posthoc.py`, `confirm.py`.*

### Headline
**The HH's single-exponential relation fails in regime III, and the kill fires.** The pooled slowing ratio is K_boot = τ_boot/τ_pred = 22 [6.9, 71] (27 units). In regimes I and II the registered fit gives τ_boot ≈ 1 call (median 0.99 and 0.83 calls), equal to the Glauber prediction τ₀/(1 − g_lag) ≈ 1 call. That agreement is nearly trivial: ρ_self is ≤ 0.37 almost everywhere, so τ₀ sits at its 1-call floor. The boot curve is not one exponential. It has a first-call talk spike that relaxes in about one call, plus, in regime III, a slow talk excess that lasts hundreds of calls. The single-exponential fit locks onto one part or the other, unit by unit.

### Outcome vs prediction
| # | Prediction | Observed | Outcome |
| --- | --- | --- | --- |
| S1 | τ_boot recovery ±25%, coverage ≥ 80% | bias −4% / +1%; coverage 0.84 / 0.78 (coupling / field worlds) | passed (coverage marginal) |
| S2 | ρ_self within ±0.05 | bias −0.03, max 0.058 | failed narrowly (A1) |
| S3 | K in band (Glauber), > 2 (slow field) | 91% in band (g ≤ 0.3); 100% > 2 | passed |
| S4 | collapse statistic sized | share statistic blind to ×3 spread; replaced by SD_between (holds 100% / 12.5%) | failed, replaced (A1) |
| P1 | regime-III K_boot in [0.5, 2] (**kill**) | 22 [6.9, 71]; 37% of units in band | **failed: kill fires** |
| P1′ | K_boot > 2 in ≥ 2/3 of units, every regime | I 35%, II 0%, III 63% | failed |
| P2 | one exponential (CV gain < 10% in ≥ 2/3) | 95% / 100% / 100% of units pass | supported as registered, but uninformative (no power; pooled curves show two timescales) |
| P3 | collapse across days (**kill**) | 10/175 regime-I days and 0/93 regime-III days resolved; no unit has ≥ 3 resolved days for the A1 statistic | untestable |
| P4 | τ_late ≤ τ_sync (≥ 30 late agent-days) | 5 / 0 / 19 late agent-days | untestable |
| P5 | τ_boot(III)/τ_boot(I) outside [0.8, 1.25] | 48 (registered); 4.4 (post hoc fast part) | supported |
| P6 | phase slope includes 1 (if power ≥ 0.8) | slope 11.6 [−2.4, 41.8]; power 0.05 | not reported as a test (unpowered) |
| NE14 | III/II change > ×1.5 | III side unresolved | mixed |
| NE43 | τ unchanged; amplitude −20% | registered fits uninformative | mixed |
| NE42 | #40 lowest τ/τ₀ | not lowest; CIs overlap | mixed |

### Findings
1. **Regimes I and II: the boot is a one-call spike.** The first call of the day talks with probability 0.49 (regime I; II 0.48). The steady-state rate is 0.12 (I) and 0.06 (II). By the second call the excess has fallen to 15% of its first-call value (regime I: excess 0.36 → 0.05). A small undershoot follows at calls 4–30 (about −0.02).
2. **Regime III: a weak spike and a slow tail.** The first call talks at 0.094 against a 20–60-call plateau of 0.050 and a whole-day steady state of 0.045. The fast part decays by ×0.66 per call. A slow excess of +12% [4, 20]% over the steady state persists over calls 20–240 (hours). In late #51 (51f, 51g) the first-call spike is absent, and only the slow excess remains.
3. **The registered estimator cannot hold both parts.** Eight regime-III units and eleven regime-I units have their τ_boot at a bound (0.2 or 5·K_max calls). The two-fold day CV did not detect the second timescale: the slow part is small per call, and the synthetic did not test CV power.
4. **ρ_self ≤ 0 in regime III** (median −0.05): a talk call is followed by a non-talk call slightly more often than chance. So τ₀ = 1 call, and the Glauber prediction τ_pred ≈ 1/(1 − g_lag) ≈ 1.1–1.4 calls hardly depends on the coupling. The slowing factor 1/(1 − g_lag) ≤ 1.4 is below the resolution of any per-unit fit (P6 power 0.05).
5. **Collapse across days is not measurable at day resolution.** A day has 4–30 boots, too few to fit τ per day. The post hoc day-half proxy (below) is the only collapse evidence.

### Post hoc (labelled; after the first real-data pass)
*Written 2026-10-04 ~23:15 UTC. Estimator: ratio estimators on the plateau-centred boot curve (Known issues: prefer ratios for decay times). `analysis/posthoc.py`.* Plateau m_plat = mean m(k) over k = 20–60; first-call excess e(k) = m(k) − m_plat; τ_fast = −1/ln[e(1)/e(0)]; slow excess = mean m over k = 20–240 divided by the steady state, minus 1. Cluster bootstrap over unit-days (B = 400).

| Regime | e(0) | τ_fast (calls) | τ_fast from e(2) | K_fast = τ_fast/τ_pred | slow excess |
| --- | --- | --- | --- | --- | --- |
| I (37 units) | 0.36 [0.32, 0.40] | 0.54 [0.41, 0.67] | 0.49 | 0.51 [0.39, 0.63] | +0.14 [0.02, 0.25] |
| II (3 units) | 0.42 [0.32, 0.51] | 0.77 [0.42, 1.42] | 0 | 0.76 [0.41, 1.40] | −0.00 [−0.24, 0.26] |
| III (27 units) | 0.044 [0.024, 0.068] | 2.38 [0.92, 26.7] | 2.25 | 2.04 [0.80, 23] | +0.12 [0.04, 0.20] |

- The fast part sits within ×2 of the call-clock Glauber prediction in every regime: K_fast is 0.51 in I, at the band's lower edge, and 2.0 in III, at its upper edge. The fast part relaxes in less than one update in regime I and in about two updates in regime III.
- Collapse proxy: odd vs even unit-days give τ_fast 0.66 vs 0.41 calls (I) and 2.9 vs 2.0 calls (III), within ×1.6. Kickoff days relax more slowly in regime I (1.29 [0.65, 3.2] vs 0.47 [0.35, 0.58] calls), so the kickoff adds a field to the boot.
- NE14: τ_fast 0.90 → 0.90 calls across the regime boundary, while the spike amplitude falls ×0.14. NE43: no first-call spike on either side of 08-05; the slow excess persists after the operator's resume messages stop.

### Caveats
- τ₀ is at its 1-call floor in 58 of 67 units, so "τ_pred ≈ 1 call" is set by the update quantum, not by measured single-agent memory. The HH relation is therefore barely testable as posed: g_lag ≤ 0.29 changes τ_pred by at most ×1.4.
- The post hoc decomposition was chosen after seeing the curves; its K_fast band agreement is not a confirmation.
- The slow excess may be a diurnal decline of talk (agents talk more early in the day) rather than a relaxation; nothing here separates the two.
- H99 round 2 withdrew the "×9.5 kick excess" that motivated the HH (constants file still lists it).
- The steady-state rate uses calls ≥ 60 min after boot, so it absorbs part of the slow component.

**Claim that stands:** The daily boot is a first-call talk spike that relaxes within about one call (regime I: excess 0.36, registered τ_boot median 0.99 calls), and in regime III a weak spike plus a slow day-scale talk excess. The HH's single-exponential relation τ = τ₀/(1 − g_lag) fails in regime III (pooled K_boot 22 [6.9, 71]; the kill fires). *Excluded:* the fast/slow decomposition and its K_fast (post hoc); collapse across days (untestable at day resolution); the late-booter contrast (untestable, 19 late agent-days); the phase-diagram slope (power 0.05); the three natives (registered statistics uninformative).

### Scorecard (round 1)
| Axis | Score | Evidence |
| --- | --- | --- |
| A mapping | 1 | Boot, call index and talk spin come from the DQ1 ledger and hold in every regime. τ₀ is floored at 1 call in 58/67 units, so the coupling enters τ_pred only through a factor ≤ 1.4. |
| B assumptions | 1 | One-exponential assumption fails on pooled curves (spike + slow tail); the registered CV test was unpowered. Call-clock and wall-clock versions are both reported (wall-clock K median 2.0 / 12 in I / III). |
| C adequacy | 0 | The registered model misses regime III (K 22); per-day fits are unresolved. |
| D unfitted predictions | 1 | The unfitted τ_pred matches the regime-I/II registered τ_boot (K ≈ 1) but fails in III; post hoc K_fast lies within ×2 everywhere. |
| E interventional | 0 | NE14, NE43 and NE42 are uninformative on the registered statistic. |
| F identifiability | 1 | S1 and S3 passed; S2 failed narrowly; S4 failed and was replaced before real data; the two-timescale world was not simulated. |
| G ground truth | 1 | NE43 agrees with H38 (the runner's schedule, not the resume message, sets the day edge); the call-clock relaxation agrees with H40. |
| H comparative | 1 | The slow-field rival describes the regime-III tail; the Glauber call-clock form describes the fast part (post hoc); the day-specific kick rival is untested. |
| I transfer | 0 | No holdout run. |

## Round 2 redirects
- **H121-R1. Pre-register the two-component boot.** Fit m(k) = m_∞ + A_f e^{−k/τ_f} + A_s e^{−k/τ_s} with τ_f, τ_s and the ratio estimators, with a synthetic two-timescale world for power. Test K_fast on the holdout (C2 of `confirm.py`).
- **H121-R2. Separate the slow excess from a diurnal profile.** Use mid-day restarts after village-off gaps (second boots at a different clock time) and late booters as clock-shifted replicas.
- **H121-R3. Make the coupling term testable.** Use a coupling-sensitive observable: the boot spike of agents who read a peer's first message at their first call vs those who do not (partition at the read-out call), instead of a τ ratio that the coupling moves by ≤ ×1.4.
- **H121-R4. Kickoff boots.** Kickoff days relax ×2.7 more slowly in regime I: model the kickoff as a field on top of the boot.

## Notes
- 2026-10-04 22:00 UTC: round 1 started; card filled before any real-data statistic. Compute: local, ≤ 2 workers, one heavy job at a time (STANDARDS §9). The machine load was 30–85 during the run.
- 2026-10-04 22:42 UTC: Amendment A1 after the synthetic validation (before real data).
- 2026-10-04 22:43–22:55 UTC: replication run. A first attempt crashed on a single-day unit (read-only array in the agent split); fixed and rerun.
- 2026-10-04 ~23:15 UTC: post hoc fast/slow decomposition, labelled.
- Data: `data/processed/H121-daily-boot-quench/` (≈ 16 MB).
- Proposed for `physics-models/DEFINITIONS.md` (not edited): *boot (daily quench)*, *boot curve m(k)*, *boot relaxation time τ_boot*, *single-agent call memory ρ_self*, *slowing ratio K_boot*, and post hoc *first-call excess e(0)*, *fast boot time τ_fast*, *slow boot excess*.
