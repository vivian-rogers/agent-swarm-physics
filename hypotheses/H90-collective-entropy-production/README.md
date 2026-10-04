# H90: Collective entropy production beyond the parts

**Status:** exploratory round 1 **done (2026-10-04): the swarm's only measurable collective arrow of time is talk following the agents who name you, and only G51 has enough data to see it.** Card, observables and predictions written ~20:15 UTC before any real-data statistic; amendments A1 (after the synthetic), A2 (post hoc estimator fix) and A3 (post hoc power reading) dated below. Approved by Vivian 2026-10-04 from HH311.
- **G51 (supported):** talk collective EP sits entirely on named partners: σ_nam = 7.6 [4.3, 11.2]×10⁻³ nats/min (0.017 nats per agent-hour), σ_un = −0.4 [−1.7, 0.5]×10⁻³, address contrast Δ_addr = 8.0 [5.1, 12.1]×10⁻³ (block-shift p = 0.01). Single-agent talk irreversibility is ≈ 0, so the talk arrow is ~100% collective. Behavior: Σ̂₁ = 0.078 [0.051, 0.101] nats per 5 min, σ_coll 0.0002 (ρ_coll = 0.003). Activity ≈ 0.
- **Seven smaller periods (mixed, underpowered):** nothing beats the shift null in talk; power at G51's effect size is ≤ 0.05 in 5-day periods and 0.45 in G38 (A3).
- **Synthetic (axis F):** the HH's kill null (block shift) is passed by a lagged common field in 63–100% of G38/G51-size worlds; the address contrast is the field-robust test (size 0.00–0.10, power 1.00 at J = 1).
- **Natives:** N1 G38 rooms supported (weak; same-room talk lead–lag p 0.03, cross-room at null); N2 G51 pairwise failed (per-pair θ signs do not follow the naming direction: agreement 0.52 vs null q95 0.55); N3 NE43 mixed (σ_coll(all) within placebo range; σ_nam dips ×0.80 but stays at 0.021 nats per agent-hour).
- **H50 match (P4) failed:** across periods, talk σ per agent-hour does not rank with H50's J₁ (Spearman −0.29 named, −0.50 all; n = 8, mostly noise). Scorecard A1 B1 C1 D1 E1 F1 G1 H1 I1. `confirm.py` (#51 tail, #45, #47) written and frozen; **not run**.
**Fields:** thermodynamics (stochastic), stat mech, info theory, sociophysics
**Literature:** [Aguilera, Ito & Kolchinsky 2026](../../literature/aguilera-2026-entropy-production-nonequilibrium-maxent.md) (nonequilibrium max-ent bound Σ_g, hierarchy Σ₁ ≤ Σ₂ ≤ Σ, Newton-step bound, θ_ij − θ_ji ≈ β(w_ij − w_ji)); [Kolchinsky, Dechant, Yoshimura & Ito 2026](../../literature/kolchinsky-2026-generalized-free-energy-excess-housekeeping.md) (σ as statistical irreversibility; excess vs housekeeping, used only to read the single-agent part).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Population N(t) (variant *day-present*, H36); Regime; Driving / external field; Interaction (broadcast) with **Exposure (turn read-out)** (H08) for the naming partition; Agent state, variant *categorical* (v3 behavior state, coarse 5 groups as in H76) and variant *binary spin* (1-min talk, 1-min activity); Entropy production / irreversibility, in the named variant **"entropy production (AIK cross-agent bound on categorical states)"** introduced by H14, here on DQ8-trimmed windows. New named variants proposed for DEFINITIONS.md (not edited there; defined under "Operational definitions"): **collective EP σ_coll**, **collective share ρ_coll**, **address-split collective EP σ_nam / σ_un**.
**Question served:** Q6 (thermodynamics and selection), with Q3 (is there collective order beyond fields?) second.
**From:** HH311 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/15-stochastic-thermodynamics-selection/` (Aguilera EP inference, item 1), `physics-models/02-nonequilibrium-ising/` (kinetic spins with asymmetric couplings)
**Data inputs (shared tables first):** DQ3 `behavior_states_v3` (soft `p_*`, `active`, `labeled`, `in_span`), `activity_bins_fixed` (1-min talk and activity; never the old `activity_bins`), `chat_core` + `chat_mentions_clean.mentions_roster` (who names whom; agent speakers only), `rooms_timeline` (G38 native), `calendar`, `period_units`, `kicks_classified` (NE43 dates, check only), `per_period_estimates` (H50 J₁, read-only). No text.

## Source HH (verbatim from the HH list, including literature refinements)
Collective entropy production beyond the parts. Use the Aguilera–Ito–Kolchinsky nonequilibrium max-ent lower bound on σ for the joint process of agents' behavior states (v3, trimmed windows), and compare with Σ_i σ_i of the marginal processes. σ_coll = σ_joint − Σ σ_i > 0 requires directed couplings.
  - *Prediction:* σ_coll / σ_joint < 0.1 in activity and behavior. It is concentrated in the talk channel at named-message read-outs, with its asymmetric couplings matching H50's J₁ (named 0.17 vs unnamed 0.004).
  - *Egregore reading:* a collective arrow of time that individuals don't have. This revamps HH67 with the corrected data.
  - *Kill:* σ_coll indistinguishable from a block-shift null in all channels.
  - *Models:* 02, 04 · *Builds on:* H14, H50, Aguilera 2026

## Standards (2026-10-04)
**Question served:** Q6, then Q3.

| Impostor | Relevant? | How it is handled | Status |
| --- | --- | --- | --- |
| Scheduler field | yes | Every statistic runs on the DQ8 all-present window of each day (no day edges, H76: the edges carry 80–100% of the excess). Floor = per-agent block flips (H76 A1). **A1:** the synthetic shows a within-day drive with agent-specific lags beats the per-agent block-shift null (70–100% at G38/G51 scale), so the shift null alone does not remove it. The coupling claim rests on the address contrast Δ_addr (size ≤ 0.08 under the lagged field). | removed for the coupling claim (Δ_addr); open for σ_coll itself |
| Exogenous field (kickoff, goal, operator) | yes | Same as above: a common drive with per-agent response lags fakes lead–lag and passes the shift null; the **address split** (σ_nam vs σ_un, both with N observables) removes a field that acts on every pair alike. The first active day is dropped as a sensitivity. NE43 native: the nudger (an operator field) stops. | removed for the coupling claim (Δ_addr); open for σ_coll itself |
| Shared model priors | partly | A family prior can give two agents the same intrinsic arrow, not a lagged cross-agent asymmetry. Same-lab pairs are reported separately in the pairwise native (N2). | n/a for the joint term; partly for N2 |
| Contemporaneous convergence | yes | Equal-time co-movement is time-symmetric and gives no σ_coll by construction (antisymmetric observables). A read-out lag shorter than the bin moves the effect into equal-time correlation (lost, not faked). The address split tests the gate (named partners) rather than co-movement. No read vs posted-but-unread placebo at the message level (bins are 1–5 min). | partly |

**Inputs:** `activity_bins_fixed` (never the old `activity_bins`), DQ3 v3, `chat_mentions_clean`. Still old: naming uses `mentions_roster` (any naming), not the leading-@ target (H90-R3).

**Two layers:** 8 replication periods; natives N1 (G38 rooms), N2 (G51 pairwise), N3 (NE43).

**Confirm script:** `analysis/confirm.py`, frozen and guarded, built on current inputs; not run.

## Question
Is the swarm's joint behavior more irreversible than the sum of its agents' own behavior? If it is, does the extra arrow of time sit in the talk channel, between agents that name each other, as H50's gated coupling predicts?

## Design: two layers (Vivian, 2026-10-04)
- **Replication:** the common estimator on every non-holdout regime-III goal period with ≥ 3 non-holdout days and N ≥ 12: G37, G38, G39, G40, G41, G42, G44, G51 (head, 45 non-holdout days). Three channels per period (behavior, talk, activity). Period README role: `replication`. Each period is fitted on its own; G38 and G51 are fitted per period with a day-varying agent set (agents absent on a day contribute zero observables), because many of their shared units are 1–3 days (exception (d) for the unit split; no pooling across periods).
- **Natives (3):** N1 G38 rooms (within-room vs cross-room pairs: reading-routed coupling); N2 G51 full pairwise talk asymmetry vs naming direction (largest N × days); N3 NE43 (G51: the nudger stops after 2026-08-20). Role: `native`.
- **Confirmation:** `analysis/confirm.py` (transfer to #45, #47 and the #51 tail), frozen, guarded, **not run**.

## Model
**From:** `physics-models/15-stochastic-thermodynamics-selection` (item 1, EP inference) and `physics-models/02-nonequilibrium-ising` (kinetic spins with asymmetric couplings).

**H90 variant: the AIK max-ent bound with nested observable sets.** For a trajectory window x of the joint process (all agents present in the trimmed window of one day, one step t → t+1, or t → t+2 for the binary channels' single-agent patterns) and a vector g of antisymmetric observables (g(x̃) = −g(x)),

  Σ ≥ Σ_g = max_θ [ θᵀ⟨g⟩ − ln⟨e^{−θᵀg}⟩ ]   (stationary, antisymmetric g: only forward samples needed)

and, to second order (Aguilera's Newton-step bound), Σ_g ≈ 2⟨g⟩ᵀK⁻¹⟨g⟩, K the covariance of g. Nested observable sets give a hierarchy:
- **Σ₁:** single-agent observables only (each agent's own transition asymmetries), fitted jointly.
- **Σ₁₊C:** single-agent plus cross-agent lagged observables C.
- **σ_coll = Σ₁₊C − Σ₁ ≥ 0** at the population level (nested sets). It is > 0 only if a lagged cross-agent asymmetry exists: a directed coupling, or a field that reaches agents with different lags.
- **Σσ_i:** the HH's marginal sum, each agent fitted alone. Σ₁ = Σσ_i for independent agents; both are reported.

The optimal θ on a cross-agent observable g_ij is the antisymmetric coupling (θ_ij − θ_ji ≈ β(w_ij − w_ji) in Aguilera's kinetic Ising). In village terms a positive θ on "i's state at t+1 × j's state at t" means i follows j.

**What each rival predicts.**
- **R0 independent agents (H14's HH67 result):** σ_coll at the floor in every channel.
- **R1 scheduler/field lead–lag:** σ_coll > 0 on untrimmed days, gone under trimming and the block-shift null; σ_nam ≈ σ_un.
- **R2 ungated broadcast coupling:** σ_coll > 0 with σ_nam ≈ σ_un (everyone follows everyone).
- **H90 (gated coupling):** σ_coll > 0 in talk, σ_nam > σ_un, ρ_coll = σ_coll/Σ₁₊C < 0.1 in behavior and activity.

## Data scheme (`scheme/build.py`)
- **Inputs:** `behavior_states_v3` (non-holdout rows), `activity_bins_fixed`, `chat_core` (agent speakers) + `chat_mentions_clean`, `calendar`, `period_units`, `roster`, `rooms_timeline`. Every row passes `holdout_mask` and `~holdout`.
- **Transform:**
  1. **Behavior grid (5 min).** H76's coarse 5-state soft vectors (absent · work · explore · coord · wait; absent = one-hot when not `active & labeled`). Day-present agents = agents with any `in_span` window that day. Trim = windows where every day-present agent is `in_span` (DQ8 all-present rule; H76 `trim_mask`). Transitions w → w+1 inside the trimmed window only.
  2. **Talk and activity grids (1 min).** From `activity_bins_fixed`: talk spin s = 1[talk > 0]; activity spin s = 1[state ≥ 3] (act or talk). Day-present agents = agents with any record (state ≥ 2) that day; per agent the span is [first, last] record minute; trim = minutes where every day-present agent is inside its span (`nulls.all_present_window`).
  3. **Naming weights.** w_ji = number of agent messages by j whose `mentions_roster` contains i, on the period's non-holdout days (agents only; humans and `automated` excluded).
  4. **Rooms (N1).** G38 room of each agent per day from `rooms_timeline` (open rooms' null `t_end` filled with +∞, Known issues), majority room over the trimmed window.
- **Output:** `data/processed/H90-collective-entropy-production/<G..>/` with `grid_<channel>.npz` (per-day state arrays, agent ids, trimmed masks; float16/uint8), `weights.parquet` (j, i, w_ji), `results.json`; `synthetic/`; `results/`; `_provenance.json`. Expected < 30 MB.
- **Regimes covered:** regime III only (G37 → G51 head).

## Operational definitions (written 2026-10-04 ~20:15 UTC, before any real-data run)
- **Single-agent observables.** Behavior: for each agent i and state pair a < b, u_i^{ab}(t) = x_i^a(t) x_i^b(t+1) − x_i^b(t) x_i^a(t+1) (10 per agent; soft vectors). Talk and activity (binary; a one-step binary chain is reversible in steady state): the two antisymmetric 3-step patterns s(t)(1−s(t+1))... written as 1[001] − 1[100] and 1[011] − 1[110] over (t, t+1, t+2), soft-free (2 per agent).
- **Coupling observables (structured, N per set).** For agent i and a partner field h_i: g_i(t) = s_i(t+1) h_i(t) − s_i(t) h_i(t+1). Behavior uses s = x^a for a ∈ {work, explore, coord, wait} (4 per agent per set); binary channels use the spin (1 per agent per set). Partner fields:
  - **all:** h_i = mean of s_j over the other day-present agents (mean field);
  - **named:** h_i = Σ_j w_ji s_j / Σ_j w_ji over j that named i (agents never named: 0);
  - **unnamed:** h_i = mean of s_j over j with w_ji = w_ij = 0.
- **Estimator (primary).** H05/H14's cross-fitted Newton bound, re-implemented: day folds k = min(10, days); K = covariance of g over all trimmed steps (ridge 10⁻³ tr(K)/d); Σ̂ = 2 · mean over fold pairs a ≠ b of ḡ_aᵀ K⁻¹ ḡ_b (unbiased at Σ = 0). **Companion:** the exact dual with θ fitted on training folds (θ = 2K_tr⁻¹ḡ_tr) and evaluated on the held-out fold, θᵀḡ_te − ln mean_te e^{−θᵀg}.
- **σ_coll** = Σ̂(single ∪ all) − Σ̂(single). **σ_nam**, **σ_un** = the same with the named or unnamed set. **Σσ_i** = sum over agents of Σ̂(single_i) fitted alone. **ρ_coll** = σ_coll / Σ̂(single ∪ all) (a ratio of point estimates; reported only where the denominator's CI excludes 0).
- **Units.** Nats per system step; per agent-hour = Σ̂ × steps per hour / N̄ (N̄ = mean day-present agents).
- **Block flip (floor).** In each trimmed day, cut the steps into 30-min blocks (6 behavior steps, 30 minutes); each agent's segment is time-reversed with probability ½, independently per agent and block. Kills single and cross arrows. 20 replicates.
- **Block shift (kill null, HH).** Each agent's trimmed-day sequence is circularly shifted by a random whole number of 30-min blocks (≥ 1), independently per agent and day. Keeps each agent's own arrow; destroys same-day cross-agent timing. 50 replicates (100 for talk). p = (1 + #{null ≥ obs})/(R + 1).
- **CI.** Day bootstrap (B = 200): days resampled with replacement, copies of one day kept in one fold (so duplicates cannot cross-fit against themselves); percentile 95%.
- **Address contrast.** Δ_addr = σ_nam − σ_un, with the day-bootstrap CI and a shift-null p-value.
- **H50 match.** Across replication periods: Spearman of σ_coll(talk) per agent-hour vs H50's per-period J₁ (from `per_period_estimates`, read-only), and the ratio σ_nam/σ_un vs H29's J₁ ratio (0.17/0.004).

## Observables
1. Per period × channel: Σ̂₁, Σσ_i, Σ̂₁₊all, σ_coll, ρ_coll, σ_nam, σ_un, Δ_addr; floor and shift-null distributions; per agent-hour versions.
2. Cross-period: σ_coll(talk) vs H50 J₁; channel ordering of ρ_coll.
3. Natives (below).

## Null / baseline
- **Floor:** per-agent block flips (above).
- **Kill null (HH):** per-agent block shifts inside the trimmed window (above).
- **Size-matched comparison** (STANDARDS §3): σ_coll grows with N (more observables carry more signal and more noise). Across periods, σ_coll is also reported for random subsets of 12 agents (20 draws; the smallest replication N).
- **Synthetic calibration** (axis F, below).

## Native tests (each with its own prediction, below)
- **N1 · G38 rooms (two rooms on the same days, 17 days).** Rooms route reading (H05: co-location effects vanish once reads are controlled). Pairs in the same room can read each other's talk at the next call; cross-room pairs mostly cannot. Observable: σ_coll with the partner field restricted to same-room partners (σ_same) vs other-room partners (σ_cross), N observables each, talk and behavior.
- **N2 · G51 full pairwise talk.** With N = 27 and 45 days, the pairwise observables g_ij = s_i(t+1)s_j(t) − s_i(t)s_j(t+1) (351 pairs) are estimable. Observables: Σ̂(single ∪ pairs) − Σ̂(single); per pair the fitted θ_ij (training on all days, ridge); the sign agreement of θ_ij with the naming direction sign(w_ji − w_ij) over pairs with |w_ji − w_ij| ≥ 3; the Spearman of |θ_ij| with w_ij + w_ji. Null: the same statistics under 20 block shifts.
- **N3 · NE43 (G51; nudges end after 2026-08-20).** The nudger is an operator field aimed at idle agents. If σ_coll(talk) were made by the nudger, it would fall after the nudger stops. Observable: σ_coll(talk) per agent-hour on the 10 non-holdout active days after 08-21 vs the 10 before; placebo boundaries at 07-20, 07-27, 08-04 and 08-28 (same windows).
- **Considered and not used:** G44 rooms (#best has 4 agents; trimmed window 9 steps per day at 5 min); NE32 isolated newcomer rooms (three agents for one to two days); NE21/NE23 (holdout).

## Synthetic validation plan (axis F; `analysis/synthetic.py`)
A kinetic model sampled like the village, at three sizes taken from the real trimmed counts (structure only): **S40** N 15, 5 days × 40 steps (5-min) / × 200 steps (1-min); **S38** N 13, 16 days × 44 / × 220; **S51** N 27, 33 days × 69 / × 345.
- **Behavior (4 trimmed states + soft labels):** each agent is a Markov chain with a driven cycle work → explore → coord → work (single-agent irreversibility). Directed coupling: agent i's rate into coord at t+1 is multiplied by e^{J·n_i(t)}, n_i = number of i's namers in coord at t; each agent has 2–3 namers (sparse directed graph A). Soft labels as in H76 (true-state confidence with median 0.75, rest spread).
- **Talk (binary, 1-min):** P(s_i(t+1) = 1) = logistic(b_i + a s_i(t) + J Σ_j A_ji s_j(t) + f(t − ℓ_i)), with burst persistence a.
- **Scenarios:** (0) independent (J = 0, f = 0); (F) field only: a common slow drive f with agent-specific lags ℓ_i ∈ {0, 1, 2} steps, J = 0, naming weights ∝ agents' talk rates (to mimic talkative partners); (C) gated coupling at J ∈ {0.5, 1.0} (talk: Δp of the target's next-step talk ≈ 0.03–0.10, below H29's 0.17 per read-out).
- **Pass criteria:** (i) size: σ_coll exceeds its shift-null 95th percentile in ≤ 10% of scenario-0 replicates; (ii) the field world: σ_coll over the shift null in ≤ 10% (trimmed windows remove nothing here, so this is the lead–lag test), and Δ_addr > 0 at p < 0.05 in ≤ 10%; (iii) power: under C, σ_coll over the null and Δ_addr > 0, both reported per size and J; (iv) the floor mean of σ_coll under block flips is within ±1 SE of 0.
- If power at J = 1 is < 0.8 at a size, a null result at that size is "inconclusive", not "no collective EP" (STANDARDS §3).

## Synthetic validation results (2026-10-04 ~20:55 UTC, re-run ~21:20 UTC under A2; `analysis/synthetic.py`, `analysis/synthetic_size.py`, `data/processed/H90-collective-entropy-production/synthetic/`)
Held-out Newton bound with the block-floored per-column ridge (A1 + A2; the A1-only run is kept as `summary_A1.parquet` and gave the same picture). Rates are the share of replicates with p < 0.05 against 30 (talk) or 20 (behavior) block shifts. Replicates: S40 25, S38 20 (talk) / 12 (behavior), S51 12 / 6; size check 40 per cell.

| Size | Channel | Scenario | σ_coll(all) > shift | σ_nam > shift | **Δ_addr > shift** | mean σ_nam | mean σ_un |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S40 (N 15 × 5 d) | talk | 0 independent | 0.00 | 0.08 | 0.08 | −0.002 | −0.001 |
| | | F lagged field | 0.04 | 0.00 | **0.00** | −0.001 | −0.001 |
| | | C0.5 | 0.00 | 0.36 | 0.16 | 0.007 | −0.002 |
| | | C1 | 0.32 | 1.00 | **1.00** | 0.073 | −0.003 |
| S38 (N 13 × 16 d) | talk | 0 (40 reps) | 0.00 | 0.03 | 0.03 | −0.001 | −0.001 |
| | | F (40 reps) | **0.63** | 0.28 | **0.10** | 0.001 | 0.001 |
| | | C0.5 | 0.20 | 0.95 | 1.00 | 0.010 | −0.001 |
| | | C1 | 0.95 | 1.00 | **1.00** | 0.059 | 0.000 |
| S51 (N 27 × 33 d) | talk | 0 (40 reps) | 0.05 | 0.08 | 0.00 | −0.001 | −0.000 |
| | | F (40 reps) | **1.00** | **0.98** | **0.03** | 0.002 | 0.002 |
| | | C0.5 | 0.50 | 1.00 | 1.00 | 0.028 | −0.000 |
| | | C1 | 1.00 | 1.00 | **1.00** | 0.154 | −0.000 |
| S40 | behavior | 0 / F / C0.5 / C1 | 0.12 / 0.08 / 0.04 / 0.04 | 0.08 / 0.08 / 0.36 / 0.48 | 0.12 / 0.04 / 0.20 / 0.40 | | |
| S38 | behavior | 0 / F / C0.5 / C1 | 0.00 / 0.17 / 0.08 / 0.17 | 0.00 / 0.17 / 0.67 / 0.83 | 0.00 / 0.17 / 0.50 / 0.83 | | |
| S51 | behavior | 0 / F / C0.5 / C1 | 0.00 / **1.00** / 0.33 / 0.33 | 0.17 / 1.00 / 1.00 / 1.00 | 0.00 / 0.00 / 1.00 / 1.00 | | |

- **Estimator.** The cross-product Newton form (H05/H14) diverged when the observable count approached the sample count (behavior, 5-day periods: single-agent Σ̂ ≈ 2 nats per step in independent worlds, floor 0.39). The held-out form never inflates: in independent worlds σ_coll ≤ 0 on average at every size. Σ̂₁ and Σσ_i agree within 0.04 everywhere (P5's premise).
- **The block-shift null does not separate a lagged field from coupling.** A common drive that reaches agents with 0–2-step lags beats the shift null in 70% (S38) and 100% (S51) of talk worlds, and in 100% of S51 behavior worlds. Shifting destroys the field's alignment along with the coupling. The HH's kill null therefore tests "any cross-agent lead–lag", not coupling.
- **The address contrast is the field-robust coupling statistic.** Δ_addr = σ_nam − σ_un has size 0.00–0.08 under the lagged field and under independence, and power 1.00 at J = 1 in talk at every size (C0.5: 0.20 / 1.00 / 1.00).
- **The mean field over all agents dilutes gated coupling.** σ_coll(all) detects C1 talk in only 32% of S40 worlds; σ_nam detects it in 100%.
- **Behavior at 5 min is underpowered in 5-day periods** (Δ_addr power at J = 1: 0.40 at S40, 0.83 at S38, 1.00 at S51).
- **Floor.** Block-flip means of Σ̂₁ are negative (−0.18 at S40 behavior, ≈ 0 in talk): the held-out estimator sits below 0 without irreversibility, as intended.

## Amendments (dated; what had been seen)
- **A1 (2026-10-04 ~20:55 UTC, after the synthetic run, before any real-data statistic).**
  1. **Estimator.** The primary estimator is the *held-out* Newton bound: on each day fold f, θ_f = 2(K₋f + c·diag K₋f)⁻¹ μ₋f from the other folds, and L_f = 2θ_fᵀμ_f − ½θ_fᵀK_fθ_f on fold f; Σ̂ = n-weighted mean of L_f. The ridge is per column (λ_k = c K_kk, c = 1), so nested sets shrink shared columns alike; a common scalar ridge faked σ_coll ≈ +0.04 in independent S51 behavior worlds. The cross-product form is kept only as a companion in the code.
  2. **What the shift null tests.** σ_coll above the shift null means cross-agent lead–lag (field with lags or coupling). **The coupling test is Δ_addr > 0 against the shift null** (calibrated under the lagged field). P2 is read as "lead–lag exists"; P3 becomes the primary coupling test and is evaluated in every replication period (talk power at J = 1 is 1.00 at all three sizes), not only where P2 holds.
  3. **Verdict rule (replaces the one under Prediction).** *Supported:* Δ_addr(talk) > 0 with shift p < 0.05, and ρ_coll < 0.1 in behavior and activity (or their σ_coll and Δ_addr inside the shift null). *Failed:* Δ_addr(talk) inside the shift null and σ_coll inside it in every channel (talk power ≥ 0.8 at all sizes). *Mixed:* otherwise. Behavior results in 5-day periods are marked "underpowered".
  4. **Block flips** are the floor (reported as the null mean); p-values against 20 flips are not used (minimum p 1/21).
  5. The impostor table's scheduler/exogenous rows change from "removed by the shift null" to "removed only by the address contrast" (below).
- **A2 (2026-10-04 ~21:15 UTC, post hoc to an estimator failure on real data; disclosed).** The first real-data pass on G40 (behavior) returned Σ̂₁ = −17.9 nats per step: v3 soft labels are confident, so many state-pair columns have near-zero variance on some days, and a ridge proportional to each column's own variance gave them huge θ that the held-out folds then penalized. **Fix:** λ_k = c (K_kk + mean diagonal of k's observable block), blocks = single / each partner set / pairs (still identical for shared columns across nested sets). What I had seen before the fix: G40's three-channel output under A1 (behavior absurd; talk and activity at the floor, shift p 0.36–0.77). The synthetic was re-run under A2 (table above) and the size of Δ_addr re-checked with 40 replicates per cell. No prediction or verdict rule changed.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R0 independent agents (H14 HH67); R1 scheduler/field lead–lag; R2 ungated broadcast coupling.
**Locked holdout used for confirmation:** none yet. `analysis/confirm.py` (#51 tail, #45, #47) written and frozen; not run.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | States from DQ3 v3 (soft, coarse 5) and `activity_bins_fixed`; naming from `mentions_roster` (any naming, not the leading-@ target); DQ8 all-present trim per day. Regime III only. Assumptions listed (stationarity within the trimmed window, even variables). |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | One-step pair observables plus 3-step single-agent patterns for binary spins. Day-to-day nonstationarity is penalized by the held-out estimator (it broke the first behavior fit: A2). No Markov-order audit beyond 3 steps; parallel update assumed at 1–5 min. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | The estimator is held out by day fold by construction. G51 talk beats the block-shift null and the field-robust address contrast (p 0.01). 7/8 periods at the floor (underpowered). |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | G51 shows the predicted signature unfitted (talk only, named > unnamed, ρ_coll ≈ 0 in behavior). N2 (pair direction) and P4 (H50 J₁ ranking) failed. |
| E interventional | predicts the change across a natural experiment | 1 | NE43 (nudger off): σ_coll(all) inside placebo range; the gated term persists (×0.80, against rising placebos). No holdout run. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Synthetic at the three real sizes with soft labels: size ≤ 0.10, power curves vs J, the shift null's failure under lagged fields. A2 was a post-hoc estimator fix found on real data, then re-validated. Not tested: alternative trims and bin widths. |
| G ground truth | agrees with known structure | 1 | Agrees with H50/H29 address gating and H05 (rooms route reading): N1 same-room > cross-room (weak). |
| H comparative | beats the named rivals | 1 | In G51 talk, R0 (independent), R1 (lagged field: address contrast size 0.03) and R2 (ungated broadcast: σ_un ≤ 0) are rejected. Not separable elsewhere. |
| I transfer | holds in other same-mode periods, including the holdout | 1 | One powered unit (G51). Holdout (#51 tail) not run. |

## Prediction
*Written 2026-10-04 ~20:15 UTC, before running the analysis on real data. What I had seen: the H14 card (HH67 collective term null in 8/8 regime-III periods, blind below ~0.3–0.5 nats/min in 5-day periods, on untrimmed 1-min grids with a cross-day null); H50 (talk J₁ > 0 in 45/71 units; named 0.17 vs unnamed 0.004 from H29); H76 (edge excess, soft-label attenuation ×0.19); structural counts of trimmed 5-min windows per period (G37 122 … G51 2,416; G44 47). No EP, flux, naming-weight or coupling statistic.*
- **P1 (small collective share, primary).** In behavior and activity, ρ_coll < 0.1 in every replication period where Σ̂₁₊all's CI excludes 0. *Against:* ρ_coll ≥ 0.3 with σ_coll above the shift null in any period. Credence 0.7.
- **P2 (talk carries it, primary).** σ_coll(talk) exceeds the block-shift null's 95th percentile in ≥ 1/2 of the replication periods where the synthetic power at J = 1 is ≥ 0.8, and in at most 1 period in behavior or activity. *Against (HH kill):* σ_coll inside the shift null in every channel and period. Credence 0.4 (H14 found no collective term; trimming and the talk spin are the changes).
- **P3 (address gating).** In the periods where P2 holds, Δ_addr = σ_nam − σ_un > 0 with its CI excluding 0, in ≥ 2/3 of them. *Against:* σ_un ≥ σ_nam (R2 ungated). Credence 0.45.
- **P4 (H50 match).** Spearman(σ_coll(talk) per agent-hour, H50 J₁) > 0 across the replication periods (n ≈ 8; descriptive, no significance claim). Credence 0.5.
- **P5 (marginal sum).** Σ̂₁ and Σσ_i agree within their CIs in every period and channel (agents nearly independent at the single-agent level). Credence 0.7.
- **N1 (G38 rooms).** σ_same(talk) > σ_cross(talk), and σ_cross inside its shift null. Credence 0.45.
- **N2 (G51 pairwise).** Sign agreement of θ_ij with the naming direction ≥ 0.6 over pairs with |w_ji − w_ij| ≥ 3, above the shift-null 95th percentile; Spearman(|θ_ij|, w_ij + w_ji) > 0.1. Credence 0.4.
- **N3 (NE43).** The after/before ratio of σ_coll(talk) lies inside the placebo range (the nudger is a field, not the coupling; H50 found peer J₁ ×0.69 across NE43). *Against:* the ratio falls below the placebo minimum. Credence 0.5 (power expected to be low: 10 days a side).
- **Per-period verdict rule (replication):** *supported* if σ_coll(talk) > shift null (p < 0.05) and ρ_coll < 0.1 in behavior and activity (or their σ_coll at the floor); *failed* if σ_coll is inside the shift null in every channel and the synthetic power at that size is ≥ 0.8; *mixed* if one of the two parts holds; *inconclusive → mixed with the note "underpowered"* if power < 0.8 and nothing exceeds the null; *n/a* if fewer than 3 days or no trimmed steps.

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | mixed | 3 days, N 12; talk Δ_addr +4.9×10⁻³ (p 0.26); behavior Σ̂₁ < 0 (floor); underpowered |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication + native | mixed (N1 supported, weak) | 17 days, N 14; talk Δ_addr +2.2×10⁻³ (p 0.08), power 0.45; N1 σ_same +1.6×10⁻³ (p 0.03) vs σ_cross −0.7×10⁻³ (p 0.66) |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | mixed | talk Δ_addr +0.6×10⁻³ (p 0.37); all channels at the floor; underpowered |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | mixed | talk Δ_addr +5.3×10⁻³ (p 0.16); behavior σ_nam p 0.02 (single exceedance) |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | mixed | talk Δ_addr −2.9×10⁻³ (p 0.58); behavior σ_coll(all) p 0.02 (single exceedance) |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | mixed | talk Δ_addr −1.1×10⁻³ (p 0.63); all channels at the floor; underpowered |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | mixed | 3 days, 9 trimmed behavior steps a day; talk Δ_addr +23×10⁻³ (p 0.13); underpowered |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication + native | supported (N2 failed) | talk σ_nam 7.6 [4.3, 11.2]×10⁻³, σ_un −0.4, Δ_addr 8.0 [5.1, 12.1]×10⁻³ (p 0.01); behavior ρ_coll 0.003; N2 sign agreement 0.52 |
| [NE43](goalperiod-subhypotheses/NE43/README.md) | native | mixed | σ_coll(all) Δ −1.5×10⁻³/agent-h inside placebos [−3.4, +2.9]; σ_nam 0.026 → 0.021 nats/agent-h, below placebo steps (+4.6 … +12.8×10⁻³) |

## Results
### Exploratory round 1 (2026-10-04; `scheme/build.py`, `analysis/run.py`, `analysis/synthetic*.py`, `analysis/figures.py`)
Numbers: `data/processed/H90-collective-entropy-production/results/{summary,natives}.json`, `G<NN>/results.json`, `synthetic/`. Figures: `figures/summary_obs.pdf` (talk σ_nam vs σ_un per period with the shift-null 95th percentile; behavior Σ̂₁ vs σ_coll), `figures/synthetic_compact.pdf` (Δ_addr power vs J; false positives under a lagged field). Estimates: `per_period_estimates` (H90, `coll_ep_*`; 120 replication rows (8 periods × 3 channels × 5 statistics), 3 native rows). Run time ≈ 4 min.

**Outcome vs prediction**
| Prediction | Observed | Verdict |
| --- | --- | --- |
| P1 ρ_coll < 0.1 in behavior and activity (where Σ̂₁₊all's CI excludes 0) | only G51 behavior qualifies: ρ_coll 0.003 (Σ̂₁ 0.078 nats/5 min); activity Σ̂ ≈ 10⁻⁴ everywhere | supported (1/1 measurable) |
| P2 σ_coll(talk) over the shift null (read as lead–lag after A1) | G51 only (σ_coll(all) 0.97 [0.24, 1.70]×10⁻³, p 0.01); 0/7 elsewhere | supported in G51; kill not met |
| P3 Δ_addr > 0 against the shift null (the coupling test after A1) | G51 p 0.01; G38 p 0.08; 5-day periods p 0.13–0.65 | supported where powered (1/1 at power ≥ 0.8) |
| P4 Spearman(σ_coll(talk)/agent-h, H50 J₁) > 0 | −0.29 (σ_nam), −0.50 (σ_all), n = 8 | failed (noise-dominated) |
| P5 Σ̂₁ ≈ Σσ_i | largest gap 0.033 nats/step (G37 behavior, both below the floor); G51 behavior 0.078 vs 0.079; talk and activity within 10⁻⁴ | supported |
| N1 G38 σ_same > σ_cross, σ_cross at null | talk +1.6 (p 0.03) vs −0.7 (p 0.66)×10⁻³; CI of σ_same spans 0 | supported (weak) |
| N2 G51 θ_ij sign follows naming direction | agreement 0.52 (null q95 0.55); Spearman 0.08 (null q95 0.16) | failed |
| N3 NE43 σ_coll(talk) inside placebo range | σ_coll(all) yes; σ_nam dips ×0.80 against rising placebos | mixed |

**What it means.**
1. *The individual arrows are in behavior; the collective arrow is in talk.* In G51, the 5-min behavior mix of each agent is irreversible (Σ̂₁ = 0.078 nats per step, ≈ 0.035 nats per agent-hour), and no measurable part of it is collective (ρ_coll = 0.003). The 1-min talk spins are reversible one agent at a time (Σ̂₁ ≈ 0) and irreversible jointly: the whole talk arrow is collective.
2. *The collective talk arrow is address-gated.* It sits on the partner field built from agents who named the recipient (σ_nam 0.0076 nats/min) and is absent from never-named partners (σ_un ≤ 0). This is H50's read-out gate (H29: named J₁ 0.17 vs unnamed 0.004) seen as entropy production: agents start talking in the minute after the agents who name them talked.
3. *The block-shift null is not a coupling test.* A common within-day drive that reaches agents with different lags passes it (synthetic). H14's HH67 null and HH311's kill both used shift- or cross-day surrogates; only the address split separates gated coupling from lagged fields.
4. *Per-pair direction is not stable.* The gated term is "i follows the agents who name it", summed over partners. Pairwise θ signs do not follow which partner named the other more (naming is mostly reciprocal), so there is no leader–follower hierarchy in this channel.
5. *Five-day periods cannot see it.* At G51's effect size (J ≈ 0.28 in synthetic units), power is ≤ 0.05 in 5-day periods and 0.45 in G38. The seven null periods are inconclusive, not evidence against the coupling. A size-matched (12-agent) G51 estimate is also at the floor (−0.05×10⁻³): the effect needs the full roster and 40+ days.

**Egregore reading (HH311).** The swarm has a collective arrow of time that individuals lack, but only in the talk channel and only as a sum of pairwise read-out responses to being named. It is coupling, not a new collective variable: removing the naming partition removes it.

## Amendment A3 (2026-10-04 ~21:40 UTC, post hoc; labelled)
After the first full run, the A1 verdict rule called G37, G38, G39, G42 and G44 "failed" because talk power at J = 1 is 1.00. J = 1 is about 4× G51's measured coupling. `analysis/synthetic_effect.py` measured power at J = 0.25 and 0.35 (G51's σ_nam corresponds to J ≈ 0.28): 0.05 / 0.00 (S40), 0.45 / 0.55 (S38), 1.00 / 1.00 (S51). Following STANDARDS §3 (a negative needs power ≥ 0.8 at the effect that matters), these periods are **mixed (underpowered)**, with "failed under the A1 rule" kept in their READMEs. The A3 numbers are post hoc because the effect size came from the data.

## Confirmatory predictions (C-*): for the locked holdout, frozen 2026-10-04 after round 1, not run (`analysis/confirm.py`)
- **C1 (#51 tail, 09-07 → 09-18):** talk Δ_addr > 0 with p < 0.05 against 100 block shifts. Power at G51's effect: between 0.45 (16 days) and 1.00 (33 days); the tail has 10 days at N ≈ 32.
- **C2 (#51 tail):** σ_un(talk) inside the shift null (p ≥ 0.05).
- **C3 (#51 tail):** behavior and activity ρ_coll < 0.1, or σ_coll and Δ_addr inside the shift null.
- **C4 (#45, #47):** σ_coll(all) inside the shift null in behavior and activity (expected null; talk reported, not scored).
- Reuse: these targets are planned by many hypotheses (H02, H04, H14 EP on v3, H41, H76). The script calls `holdout_ledger.check` with family `entropy_production` and stops on a same-family conflict. H90 is not yet registered in the ledger (shared file; see the report).

## Round 2 redirects
**What the direction is really after:** whether the swarm has collective order that no agent carries alone, measured as irreversibility, with the fields removed.
- **H90-R1. Call-clock talk spins.** Rebuild the talk channel on each agent's call clock (H40) instead of 1-min bins, and use the ledger's read-out call as the time origin. That should raise the per-pair signal several-fold and make 5-day periods testable.
- **H90-R2. Read vs posted-but-unread partner fields.** Split σ_nam by whether the naming message had been read at the recipient's next call (context ledger); the in-flight half is the contemporaneous-convergence control.
- **H90-R3. Leading-@ targets.** Replace `mentions_roster` (any naming) with the leading-@ target (STANDARDS §2) and compare σ_nam.
- **H90-R4. Hierarchical pooling across 5-day periods** (exception (d)): a shrinkage estimate of Δ_addr per period, reported next to the per-period values.
- **H90-R5. Run confirm.py** after registering H90 in the holdout ledger.

## Notes
- 2026-10-04: compute limits (STANDARDS §9): ≤ 2 threads, no process pools, one job at a time, no sub-agents.
- 2026-10-04: G44's trimmed behavior window is 9 five-minute steps a day (one late or early agent empties it): behavior results there are not interpretable.
- 2026-10-04: processed data ≈ 1 MB (`du -sh data/processed/H90-collective-entropy-production`).
- 2026-10-04: the estimator is a re-implementation of H05/H14's `ep_gauss_crossfit` (cross-fitted Newton bound) and H76's block-flip surrogate, copied with attribution into `analysis/h90lib.py`; nothing is imported across hypothesis folders.
- 2026-10-04: **Correction (2026-10-04, blind-rater check): G51 day counts.** G51 has 45 non-holdout days. The DQ8 all-present trim leaves 43 talk and activity days and 34 behavior days (`data/processed/H90-collective-entropy-production/G51/results.json`). The replication fit and native N2 (`run.py: native_g51_pairwise`, talk) use the 43 talk days. "33 days" is the synthetic size class S51 (N 27 × 33 days, `synthetic.py: SIZES`), fixed before the real run and smaller than G51's talk grid, so its talk power is conservative for G51. C1's "16–33 days" are the S38 and S51 size classes, not G51 day counts.
