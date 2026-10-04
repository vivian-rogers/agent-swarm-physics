# H68: Attention dilution is a mixture of two strategies

**Status:** round 1 done (2026-10-04; exploratory, non-holdout). **Refuted: dilution is one narrow, unimodal agent-level exponent, not a mixture of two strategies.** Per-agent exponents (ledger k, mention response, agent-day propensities) spread with a between-agent SD τ̂ of 0.09–0.20 around μ̂ 0.54–0.87; no period passes the bimodality test (0/17; 0/9 powered), and in 7/9 powered periods τ̂'s upper 95% bound is below 0.35, which the two-strategy world never produces (≤ 0.1 of synthetic runs). No agent-period sits near β = 0 (lowest 0.25 of 170). Lab does not set the exponent (permutation p 0.37; G51 p 0.12), an agent's exponent barely persists across periods (ICC 0.23 [−0.10, 0.50]), and concentrated agents dilute *more*, not less (ρ +0.36). Predictions, synthetic validation (axis F) and amendments B1–B4 came before real data; one labelled post-hoc variant (H18's per-message mention factor) changes no verdict. `confirm.py` written, dry-run only, **not run**.
**Question:** **Q1** (what couples agents?): dilution sets the per-pair coupling normalization J ∝ N^−β. H68 asks whether β is one agent-level constant or an average over two kinds of agents.
**Verdicts:** 0 supported, 2 mixed (G30, G38), 7 failed (G25, G26, G31, G36, G41, G44, G51), 9 descriptive (8 underpowered periods + NE42).
**Fields:** sociophysics (contagion, attention), stat mech (heterogeneous mean field, mixture order parameters)
**Literature:** none in `literature/` specific to attention mixtures; the mean-field normalization is H18's (`physics-models/03-contagion/`, `01-inverse-ising/`).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime; *Talk turn / pending set (ledger)* (RE-V1); *Interaction*, variant *addressed* (mention-based, `chat_mentions_clean.mentions_roster`); *Exposure (ledger receiving call)*. New named variants proposed (not edited into DEFINITIONS.md), defined under Observables: **dilution exponent (per-agent, ledger)**, **attention-strategy mixture**, **thread concentration**.
**From:** HH258 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` ("Making the faithful ones better") · **Models:** `physics-models/03-contagion/` (per-pair uptake hazard with a dilution normalization)
**Data inputs (shared tables first):** H18 round-1b pending tables (`data/processed/H18-attention-dilution/r1b/G<NN>/{talks,pending,wakes,wake_pending}.parquet`, built by H18's `scheme/build_ledger.py` from the DQ1 ledger, `chat_mentions_clean`, DQ2 `reply_pairs`); `roster` (lab = family); `calendar` + `holdout_mask`.

## Question
H18 measured a population dilution exponent β ≈ 0.66 (ledger k, 16/16 periods): the chance that a talk turn addresses a given pending sender falls as k^−0.66. Is this one exponent shared by all agents, or a mixture of agents that attend thinly to everything (β ≈ 1) and agents that follow one thread (β ≈ 0)? HH258 predicts bimodal per-agent exponents with mixture weights set by model family.

## Design: two layers (Vivian, 2026-10-04; see `infra/data-quality/QUEUE.md`)
- **Replication:** the per-agent estimator and the mixture test on every H18 period (16 periods + G10). Period README role: `replication`.
- **Period-native tests** (written before running them):
  - **G51** (32 agents, 9 labs, k up to > 100, timer wakes with exogenous k): the most agents per period, the family test with the most labs, and a per-agent timer-wake exponent that removes the reactive-timing impostor.
  - **NE42** (#39 → #40 → #41: merge and split at a fixed roster; k ×1.45): is an agent's exponent a trait that survives a step in k, or a state set by load?
- **Faithfulness lever:** HH258 targets axis D (the shape of the β distribution, an unfitted statistic of the population fit) and axis A (family invariance). The scorecard says whether it moved them.

## Model
**From:** `physics-models/03-contagion/`, H18's uptake model with an agent-specific exponent.

At talk turn τ of agent i on day d, each pending sender j (n_j pending messages, m_j = 1 if one of them @-mentions i) is addressed with
P(r_τj = 1) = 1 − exp[−θ_{i,d} · n_j · k_τ^{−β_i} · e^{γ_i m_j}]
(complementary log-log; H18's M_pow with the exponent indexed by agent). θ_{i,d} is an agent-day propensity (ridge toward the agent mean, σ = 1.5, as H18), so β_i is identified only from k variation within an agent-day.

**Population layer (the hypothesis).** Across the agents of one period:
- **U (unimodal, null):** β_i ~ N(μ, τ²). A homogeneous population has τ ≈ 0.
- **H68 (two strategies):** β_i ~ π_A N(1, τ_w²) + (1 − π_A) N(0, τ_w²), τ_w ≤ 0.15: "thin attenders" (budget 1/k) and "thread followers" (k⁰). π_A = π(lab). With β̄ ≈ 0.66 this needs π_A ≈ 0.66 and a between-agent SD ≈ 0.47.
- **M2 (free two-component mixture):** two Gaussians with free means, common τ, free weight.
Each fitted on the per-agent estimates with their own sampling variances (heteroscedastic: β̂_i ~ N(β_i, s_i²)).

**What separates them.** U with τ ≤ 0.2 vs H68: the deconvolved spread τ̂ (H68 needs ≈ 0.45) and the two-component likelihood ratio. Family: the lab share of between-agent variance. Trait: the correlation of an agent's β across periods (exception (b) of CLAUDE.md: an agent-level property, checked for invariance before any pooling).

**Mean-field consequence.** If H68 holds, J_ij ∝ N^−β_i is agent-specific and the population β is a composition variable: a swarm's dilution is set by its family mix, and H03's per-pair triggering vs N should depend on the roster.

## Data scheme (`scheme/`)
- **Inputs:** H18 round-1b `talks.parquet` (ledger talk calls: agent, pt_date, k = `k_since_talk`, after-pause flag) and `pending.parquet` (one row per pending message: sender, rank, `ment_i`, `scored`, `resp` = mention response, `resp_reply` = DQ2 reply parent); `wakes` / `wake_pending` (timer-wake batches, D2) for G51; `roster.lab`.
- **Transform (`scheme/build.py`):**
  1. Re-apply `holdout_mask` and `calendar.holdout` on `pt_date` (H18 already dropped held-out days; the build asserts zero held-out rows and drops any it finds).
  2. Collapse scored pending messages to units (talk, sender j): n_j, min rank, m_j = any mention of i, resp = mention response, resp_reply = reply response, engaged = i addressed j in its previous talk turn that day (H18's engagement control).
  3. Attach agent, day, k, lab, after-pause flag. Same for D2 wake units in G51.
- **Output:** `data/processed/H68-dilution-mixture/G<NN>/units.parquet` (codes only), `wake_units.parquet` (G51), per-period `agents.json` / `period.json`, `synthetic/`, `_provenance.json`. No text.
- **Regimes covered:** I (#24–#31), II (#35), II/III (#36), III (#37–#44, #51 non-holdout days), plus #10 (NE03 side). Each period is one unit (per-agent fits need the whole period); #51 is one unit with a segment variant.

## Observables
*Written 2026-10-04 before any per-agent statistic on real data.*
1. **Dilution exponent (per-agent, ledger)** β̂_i with model SE s_i; mention response (primary), reply response (secondary; one-parent budget, so only its ranking of agents is used). Eligibility: ≥ 150 units, ≥ 15 responses, within-agent-day SD of log k ≥ 0.3.
2. **Between-agent spread** τ̂ (heteroscedastic random-effects ML; profile 95% CI) and the precision-weighted mean μ̂.
3. **Mixture test:** LR = 2[ℓ(M2) − ℓ(U)], p from a parametric bootstrap under the fitted U (B = 200). **H68-literal fit:** ℓ(H68) − ℓ(U) with the modes fixed at 0 and 1 and τ_w, π free.
4. **Family:** the lab share of between-agent variance η²_lab (weighted, period fixed effects, agent-periods ≥ 1 per lab), with a permutation p (labs permuted across agents, an agent's periods kept together). **Trait:** the correlation of β̂ for the same agent across periods, deconvolved by the sampling variances.
5. **Thread concentration** C_i: per agent-day, the Herfindahl index of addressed senders among scored addressed units, normalized by the number of distinct pending senders that day ((H − 1/S)/(1 − 1/S)); averaged per agent. Signature: thread followers have low β and high C.
6. **Consistency (unfitted):** precision-weighted mean of β̂_i vs the pooled common-β estimate (same likelihood, agent-day θ).
7. **G51 only:** per-agent timer-wake exponent β̂_i^D2 (batch size set by a pause chosen before the messages arrived; H18 D2, 300 s window) and its correlation with β̂_i; per-agent shape (power vs floor h = k^−1 + ρ).

## Null / baseline
- **U with τ = 0** (one shared exponent): every per-agent spread is sampling noise. Its size is measured by simulation on the real unit skeletons (real k, n_j, mentions, agent-days; synthetic responses at the real rate).
- **U with τ = 0.15** (modest real heterogeneity, unimodal): the mixture test must not call this bimodal.
- **Lab null:** labs permuted across agents (agent kept whole).
- **Reactive-timing null (H18):** endogenous turn timing fakes β ≈ 0.8 at the population level; per agent, a reactive agent looks "thin". Removed in G51 by the per-agent timer-wake exponent.

## Impostors (`STANDARDS.md` §1)
| Impostor | How it could fake H68 | How H68 removes it, or why it does not apply |
| --- | --- | --- |
| Scheduler field | Agents differ in cadence; reactive agents (talk right after a message) get spurious steep β | Agent-day propensities absorb day-level activity; k is the ledger backlog (call clock, not wall clock); G51 native: per-agent timer-wake β^D2 (exogenous batch size) must track β̂_i |
| Exogenous field (kickoff, goal, operator) | Roles or rooms (G51 private goals; #best/#rest) give some agents one conversation partner | Day propensities absorb goal state; human and nudge messages count in k but are not scored; G51 role and room are reported next to the lab test |
| Shared model priors (family, style) | Families differ in naming habits, so the mention response measures style, not attention | The exponent is scale-free (a naming rate enters θ, not β); β̂_i(mention) vs β̂_i(reply) rank agreement is required (P5); the family test is the hypothesis, so a family effect counts only if it survives the reply ranking |
| Contemporaneous convergence | Mid-exchange agents name partners they were already talking with (H18 placebo, H08) | Engagement covariate variant (i addressed j in its previous talk turn); β̂_i with and without it |

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** U (one exponent, τ = 0), U with spread (unimodal heterogeneity), M2 (free two-component), reactive timing (H18 null).
**Locked holdout used for confirmation:** none in round 1. Targets frozen in `analysis/confirm.py` (not run): #51 tail, #45–#47, #49, #50 (regime III), #28, #29 (regime I). It needs holdout pending-set inputs that no builder produces yet (see "Confirmatory design").
**Scorecard (round 1): A1 B1 C0 D0 E0 F2 G0 H0 I0.**

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Per-agent β from ledger pending sets and mention responses (shared tables via H18 r1b). Agent rankings agree between the mention and reply responses (ρ 0.52, n 156) and with an engagement control (ρ 0.99). The level depends on the mention-factor convention (G51 0.87 per unit vs 0.63 per message), the spread does not. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Stationarity of an agent's β across periods fails (ICC 0.23 [−0.10, 0.50]): the residual spread is mostly agent × period. The reactive-timing impostor is not removed per agent: G51 timer-wake β^D2 does not track β_i (ρ 0.15, n 24). |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 0 | The H68 model does not beat the unimodal null: the bootstrap LR rejects U in 0/15 periods (1/15 in the per-message variant: G30, driven by one agent at 1.8), and the H68-literal mixture is 1.3–29 log-likelihood units worse than U in every period. |
| D unfitted predictions | unfitted statistics and the model's signature | 0 | The model's signatures fail: no β near 0 (min 0.25 of 170), τ̂ 0.09–0.20 vs ≈ 0.45 needed, thread concentration rises with β (ρ +0.36, opposite sign). The consistency check passes (precision-weighted mean of β_i within 0.035 of the pooled β in 15/15). **Lever:** HH258 did move axis D for the dilution law itself: H18's population exponent is now shown to be an agent-level constant with a measured narrow spread, not an average over species. |
| E interventional | predicts the change across a natural experiment | 0 | NE42 (merge at a fixed roster) has only 5 agents eligible in all three weeks; ρ(β_40, sides) 0.40 (p 0.50) and ρ(β_39, β_41) −0.50: no information. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 2 | On real skeletons (17 periods × 4 worlds × 20 runs): β̂_i unbiased (≤ 0.04), SEs calibrated (coverage 0.89–0.99); P1 false passes ≤ 0.05, power ≥ 0.85 in 9 periods; lab test size 0.08, power 0.92. Verdicts unchanged under the per-message mention factor and the engagement control. |
| G ground truth | agrees with known structure | 0 | No ground truth for attention strategy exists (DQ6 has none). |
| H comparative | beats the named rivals | 0 | The unimodal rival U wins in every powered period; the free two-component fit finds no separated modes (it splits off single outliers). |
| I transfer | holds in other same-mode periods, including the holdout | 0 | The H68 pattern appears in no period of any regime or mode. Holdout not used. |

## Prediction
*Written 2026-10-04 19:15 UTC, before any per-agent statistic on real data.*

**What I had seen first:** H18's card (pooled and per-period β, I² 0.92 across periods, 0.99 across #51 segments), H45's and RE-V1's notes on the one-parent budget, and the row counts of H18's round-1b tables (talk calls and pending rows per period, agents per period). No per-agent exponent, spread or lab breakdown had been computed by anyone.

**Powered period:** ≥ 6 eligible agents and synthetic power ≥ 0.8 for the H68-literal world in that period (set by the synthetic validation, before real data). Other periods are *descriptive*.

| # | Prediction (HH258 as written) | Counts against |
| --- | --- | --- |
| P1 | **Bimodal exponents.** In ≥ 50% of powered periods the mixture LR rejects U (bootstrap p < 0.05) with one mode in [0.7, 1.3] and one in [−0.3, 0.3], each holding ≥ 2 agents | LR rejects in < 25% of powered periods, or τ̂ (upper 95% CI) < 0.35 in ≥ 50% of powered periods: the spread is too small for two strategies |
| P2 | **Family sets the weights.** η²_lab ≥ 0.4 of between-agent variance (permutation p < 0.05), and the cross-period trait correlation ≥ 0.5 | η²_lab < 0.15 or p > 0.2; trait correlation < 0.2 |
| P3 | **Consistency (unfitted check).** Precision-weighted mean of β̂_i within ±0.1 of the pooled common-β estimate in ≥ 80% of periods | a larger gap: the per-agent fits are biased |
| P4 | **Thread signature.** Spearman(β̂_i, C_i) < −0.3 across agent-periods | ρ ≥ 0 |
| P5 | **Not a naming habit.** β̂_i(mention) and β̂_i(reply) rank-correlate ρ ≥ 0.3 across agent-periods | ρ ≤ 0 |
| N-G51 | **(a)** P1's test passes in G51; **(b)** lab η² ≥ 0.4 in G51; **(c)** per-agent β̂^D2 correlates with β̂_i (ρ ≥ 0.4); **(d)** ≤ 20% of eligible agents have β̂_i in [0.3, 0.7] | (a) fails; ≥ 50% of agents in [0.3, 0.7]; ρ(D2, D1) ≤ 0 |
| N-NE42 | **Trait across a k step.** For agents present in #39, #40 and #41: ρ(β̂_{i,40}, mean of β̂_{i,39}, β̂_{i,41}) ≥ 0.4, and the mean within-agent change Δβ (40 vs 39/41) within ±0.15 | ρ ≤ 0, or Δβ beyond ±0.3 in the direction of the k change (a load state, not a trait) |

**Verdict rule per period:** *supported* = P1's test passes in that period; *mixed* = U rejected but the modes are not near {0, 1} (two unimodal clusters elsewhere, or one broad mode with τ̂ ≥ 0.35); *failed* = powered, U not rejected and τ̂ upper CI < 0.35; *descriptive* = underpowered.

Prior credences (Claude, 2026-10-04): P1 0.15, P2 0.2, P3 0.8, P4 0.35, P5 0.5, N-G51 0.15, N-NE42 0.35.

## Synthetic validation (axis F; run 2026-10-04 ~19:40–21:05 UTC, before any per-agent statistic on real data)
`analysis/synthetic.py`; outputs in `data/processed/H68-dilution-mixture/synthetic/` (`period_worlds.parquet`, `summary.json`, `lab_worlds.json`). Real unit skeletons of all 17 periods (real k, n_j, mentions, agent-days); responses simulated at each agent's real response rate (a nuisance level), day effects N(0, 0.4²), mention factor 2.2; 20 replicates per world and period; mixture bootstrap B = 60.

| World | P1 passes | LR rejects U | τ̂ upper CI < 0.35 | per-agent β̂ |
| --- | --- | --- | --- | --- |
| W0 one exponent (0.65) | 0 in every period | 0–0.10 | 0.9–1.0 where ≥ 9 agents | bias ≤ 0.02; z SD 0.73–1.0; coverage 0.93–0.99 |
| W1 unimodal, SD 0.15 | 0–0.05 | 0–0.15 | 0.4–1.0 | unbiased |
| W2 H68 {0, 1}, π = 0.65 | **≥ 0.85 in G25, G26, G30, G31, G36, G38, G41, G44, G51**; 0.7 G24, G27, G40; 0.55 G35; ≤ 0.2 G10, G37, G39, G42 | 0.65–1.0 | 0–0.1 | unbiased |
| W3 soft {0.35, 0.95} | 0–0.35 (modes miss {0, 1} by design) | ≥ 0.85 in G25–G31, G41, G51 | 0–0.05 | unbiased |

Pooled family and trait worlds (all periods, 12 replicates): **L0** (agent traits, SD 0.15, no lab effect): lab permutation p < 0.05 in 1/12; η² 0.11–0.45 (median 0.24). **L1** (lab sets β ∈ {0, 1}): p < 0.05 in 11/12, η² ≥ 0.97. The trait ICC estimator is noisy (L0 truth 0.69: estimates 0.46–1.13) and unstable when the true spread is small (two L1 replicates negative).

Readings:
- The per-agent estimator is unbiased with calibrated SEs at village counts, so the spread of β̂_i can be deconvolved.
- Nine periods are powered for P1; in them, a true H68 world is never mistaken for a tight unimodal one (τ̂ upper < 0.35 in ≤ 0.1 of W2 runs), and a one-exponent world never passes P1.
- The LR alone is slightly anti-conservative (up to 0.15 under W1); P1 also needs modes near {0, 1}, which keeps its false-pass rate ≤ 0.05.

## Amendments (2026-10-04 ~21:10 UTC, after the synthetic validation, before any per-agent statistic on real data)
- **B1 · P2 family test.** η² is inflated under the no-lab null (median 0.24, up to 0.45), so P2's lab part needs η² ≥ 0.4 **and** permutation p < 0.05 (size 0.08, power 0.92). The trait ICC is reported with its bootstrap CI as descriptive.
- **B2 · Powered periods** (W2 power ≥ 0.8 and ≥ 6 eligible agents): G25, G26, G30, G31, G36, G38, G41, G44, G51. The other eight periods are descriptive.
- **B3 · Bootstrap size.** Real-data mixture tests use B = 200.
- **B4 · Workers.** All runs use ≤ 2 worker processes (coordinator, 2026-10-04: machine load).

## Results by goal period
*Exploratory, non-holdout. μ̂ and τ̂: heteroscedastic random-effects mean and between-agent SD of the per-agent exponents (profile 95% CI). LR p: parametric bootstrap (B = 200) of two components vs one. Power: synthetic P1 pass rate in the H68 world (W2).*

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G10](goalperiod-subhypotheses/G10/README.md) | replication | descriptive | 3 eligible agents |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | descriptive | 9 agents; μ̂ 0.64, τ̂ 0.14 [0.04, 0.30]; p 0.08; power 0.7 |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | failed | 10 agents; μ̂ 0.69, τ̂ 0.17 [0.10, 0.31]; p 0.46 |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication | failed | 10; μ̂ 0.61, τ̂ 0.15 [0.08, 0.30]; p 0.20 |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | descriptive | 9; μ̂ 0.74, τ̂ 0.19 [0.11, 0.35]; power 0.7 |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | mixed | 10; μ̂ 0.71, τ̂ 0.20 [0.07, 0.44]; p 0.72 (per-message variant 0.02: one agent at 1.8) |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | failed | 11; μ̂ 0.54, τ̂ 0.09 [0.02, 0.19]; p 0.38 |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | descriptive | 10; μ̂ 0.77, τ̂ 0.19 [0.08, 0.38]; power 0.55 |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | failed | 11; μ̂ 0.86, τ̂ 0.14 [0.00, 0.30]; p 0.28 |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | descriptive | 2 eligible agents |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | mixed | 11; μ̂ 0.75, τ̂ 0.20 [0.11, 0.37]; p 0.59 |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | descriptive | 5 agents; power 0 |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | descriptive | 11; μ̂ 0.61, τ̂ 0.00 [0.00, 0.14]; power 0.7 |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | failed | 11; μ̂ 0.70, τ̂ 0.14 [0.04, 0.29]; p 0.86 |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | descriptive | 6; power 0.2 |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | failed | 9; μ̂ 0.83, τ̂ 0.13 [0.04, 0.29]; p 0.52 |
| [G51](goalperiod-subhypotheses/G51/README.md) | native | failed | 32 agents, 8 labs; μ̂ 0.87, τ̂ 0.15 [0.11, 0.21]; p 0.20; lab p 0.12; ρ(β^D2, β) 0.15 |
| [NE42](goalperiod-subhypotheses/NE42/README.md) | native | descriptive | 5 agents in all three weeks; ρ 0.40 (p 0.50); Δβ −0.11 ± 0.08 |

## Results
*All numbers: `data/processed/H68-dilution-mixture/results.json` (`analysis/run_periods.py`), per-period `G<NN>/{agents.parquet, period.json}`, `agents_all.parquet`, `posthoc_permsg.json`. Figures: `figures/summary_obs.pdf` (per-agent exponents), `figures/summary_obs2.pdf` (synthetic).*

### Outcome vs prediction
| # | Prediction | Observed | Outcome |
| --- | --- | --- | --- |
| P1 | bimodal β_i in ≥ 50% of powered periods | **0/9 powered** (0/17 any); τ̂ upper bound < 0.35 in 7/9 powered (G30 0.44, G38 0.37); H68-literal fit 1.3–29 log-lik units below U everywhere | **failed** (refuted by the pre-registered "against" clause) |
| P2 | lab η² ≥ 0.4 with p < 0.05; trait ρ ≥ 0.5 | all periods: η² 0.16, p 0.37 (35 agents, 8 labs, 170 agent-periods); G51: η² 0.43, p 0.12; trait ICC 0.23 [−0.10, 0.50] (16 agents in ≥ 2 periods) | **failed** |
| P3 | weighted mean of β_i within ±0.1 of the pooled β in ≥ 80% | 15/15 (largest gap 0.035) | passed (consistency check) |
| P4 | ρ(β_i, C_i) < −0.3 | **+0.36** (p 1e-6, n 170) | **failed, reversed** |
| P5 | ρ(β_mention, β_reply) ≥ 0.3 | 0.52 (n 156) | passed (the ranking is not a naming habit) |
| N-G51 | (a) P1; (b) lab η² ≥ 0.4, p < 0.05; (c) ρ(β^D2, β) ≥ 0.4; (d) ≤ 20% in [0.3, 0.7] | (a) fails, τ̂ 0.15 [0.11, 0.21]; (b) η² 0.43, p 0.12; (c) 0.15 (n 24); (d) 0.13 by the letter, but 31/32 agents sit in one mode at 0.85 (per-message variant: 0.69 in [0.3, 0.7]) | **failed** |
| N-NE42 | ρ ≥ 0.4 and \|Δβ\| ≤ 0.15 | n 5; ρ 0.40 (p 0.50), Δβ −0.11 ± 0.08; ρ(β_39, β_41) −0.50 | **descriptive** (no power) |

### Findings
1. **One exponent per period, narrow spread.** Within a period, agents' dilution exponents scatter by τ̂ ≈ 0.09–0.20 around the period mean. The two-strategy world needs τ ≈ 0.45 and modes at 0 and 1. Of 170 agent-periods, none has β̂ below 0.25, and 3% lie below 0.3. Every agent dilutes.
2. **Not family, barely a trait.** Lab explains no detectable share of the between-agent variance (p 0.37). The same agent's exponent in two periods correlates weakly (ICC 0.23, CI to 0.50). The residual spread is mostly agent × period: a state, not a fixed attention style.
3. **Concentration goes with steeper dilution.** Agents whose addressing concentrates on few senders have *higher* β (ρ +0.36). An agent that follows a thread ignores the rest of the backlog more as it grows, which is what a steep exponent means at the sender level. HH258's "thread follower = k⁰" picture had the sign wrong.
4. **The population law stands.** The precision-weighted mean of the per-agent exponents reproduces the pooled exponent in 15/15 periods, so H18's k^−0.66 is an agent-level constant, not a composition average. For mean-field use, one β per period is enough; the roster's family mix does not set it.
5. **Convention note (post hoc).** H68 applied the mention factor once per (talk, sender) unit, as pre-registered. H18 applies it per pending message. With H18's convention the pooled exponents reproduce H18 exactly (G51 0.609, G38 0.685), μ̂ falls in G51 (0.87 → 0.63), and every verdict stays (`posthoc_permsg.json`).

### Caveats
- The response is the mention proxy (H18). The reply response has a one-parent budget (Known issues), so only its ranking of agents is used.
- Per-agent eligibility drops low-volume agents (53 of 223 agent-periods); a thread-following agent that rarely talks could hide there.
- The per-agent timer-wake check (G51) has 24 agents and wide SEs; it does not exclude reactive timing per agent.
- The trait ICC estimator is noisy (synthetic L0: 0.46–1.13 for a truth of 0.69).
- Multiplicity: 17 periods × 5 statistics; the refutation holds in every powered period, so no correction changes it.

## Confirmatory design (written 2026-10-04 after round 1, before any holdout use; `analysis/confirm.py`, dry-run only, NOT run)
Frozen C1–C4 (one exponent family: τ̂ upper < 0.35 in ≥ 75% of scored targets; P1 fails everywhere; < 5% thread followers; lab p > 0.05) on #28, #29, #45–#47, #49, #50 and the #51 tail. The dry run on G38, G41, G44, G51 reproduces round 1's τ̂ exactly. The run needs held-out pending sets that H18's builder does not make (it drops the holdout): the builder should move to `infra/shared/` with an `--include-holdout` switch first. Reuse: H18's own confirm script targets the same periods with the population exponent (a different statistic); H02 used #45, H04 used #46–#50.

## Notes
- 2026-10-04 19:15 UTC: card, predictions and nulls written before any per-agent statistic.
- 2026-10-04 ~19:40–21:05 UTC: synthetic validation; amendments B1–B4.
- 2026-10-04 ~21:15 UTC: real-data run (`run_periods.py`), period READMEs, figures, estimates rows (45). Post hoc: per-message mention factor (`posthoc_permsg.py`), labelled as such.
- Code map: `scheme/build.py`; `analysis/h68lib.py` (cloglog fits, mixture tests, family and trait), `synthetic.py`, `run_periods.py`, `posthoc_permsg.py`, `write_period_cards.py`, `figures.py`, `estimates_rows.py`, `confirm.py`.

## Round 2 redirects (2026-10-04)
- **H68-R1.** The residual spread (τ̂ ≈ 0.15) is agent × period. Test whether it tracks load or role (G51 segments, per-agent β by week) rather than identity.
- **H68-R2.** Fix one mention-factor convention across H18 and H68 (per message) in the shared pending-set builder.
- **H68-R3.** Use one β per period as the mean-field normalization in H03/H05; no composition correction is needed.
