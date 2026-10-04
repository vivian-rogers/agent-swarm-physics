# H85: Scaling of outputs with N

**Status:** **exploratory round 1 done (2026-10-04, non-holdout only). Mixed: talk scales sublinearly with N (messages β 0.33 [−0.18, 0.64]; regime I 0.09), while addressing per message rises as fast as H18's dilution predicts or faster (0.79 [0.41, 1.39] vs 0.44); reply parents do not aggregate (HH kill fires); work exponents are unidentified.**
- **Talk budget:** in regime I each agent keeps its call clock but its share of talking calls falls as N^−0.89, so room talk volume is nearly fixed.
- **Pending set** grows with N (γ_k 1.29 across units, 1.02 across rooms on the same day).
- **Reply parents per message** are flat in N (0.02 vs predicted 0.32).
- **Precision:** the across-unit SD of a level exponent is 0.25 (synthetic), not 0.10; 1.15 vs 1 is unresolvable.
- Card and predictions written 2026-10-04 20:04 UTC before any real-data statistic. `analysis/confirm.py` written and dry-run, **not run**.
**Question (GOALS.md):** **Q3** (is there collective order beyond fields?): a superlinear output exponent would be the first collective benefit; extensive exponents say the swarm is a sum of agents. It also serves **Q1** (does H18's per-pair dilution aggregate to a swarm-level size law?).
**Fields:** stat mech, complex systems (urban scaling)
**Literature:** none in `literature/`; Bettencourt et al. 2007 and Bettencourt 2013 are quoted from memory in `physics-models/14-scaling-and-fluctuations/README.md` (marked †).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; **Population N(t)**, variant *active population* (agents with ≥ 1 record on the day, hour-weighted over the unit; see Observables); Regime; Driving / external field (goal type); Interaction, variants *addressed* (mention) and *reply* (here the DQ2 reply parent, named variant **interaction (reply parent)** below); H18's pending set k (`context_ledger_turns.k_since_talk` at talk calls, RE-V1's ledger k). Proposed named variants for DEFINITIONS.md: **output rate Y/T** (unit total per scheduled village hour) and **scaling exponent β (unit level)** (definitions under Observables).
**From:** HH309 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/14-scaling-and-fluctuations/` (primary: allometric scaling), `physics-models/02-nonequilibrium-ising/` (the per-call response kernel whose dilution is aggregated; secondary)
**Data inputs (shared tables first):** `period_units`, `period_affordances` (`mode`, `git_dense`), `calendar` (windows), `activity_bins_fixed` (active population), `chat_core` + `chat_mentions_clean` (messages, addressed pairs), DQ2 `reply_pairs` (`parent`, `pair_set = cand`), DQ4 `work_commits` (default agent-work filter), `context_ledger_turns` (`k_since_talk`, `talk`), `rooms_timeline` (room membership for natives), `roster`.

## Source HH (verbatim from the HH list, including literature refinements)
Urban-style scaling of swarm outputs with N, with exponents derived from H18 and H58. Fit Y = Y₀ N^β across the 71 units, with regime and goal-type covariates.
  - *Predictions:*
    - Messages: β ≈ 1, since each agent posts at its own call rate (H40).
    - Replies: β ≈ 1.34. Per-recipient replies scale as k · k^{−0.66} = k^{0.34} with k ∝ N, so N · N^{0.34}.
    - Committed work: β = 1.0 ± 0.1, the independent agent + own artifact unit (H58). Superlinear β > 1.1 (Bettencourt's 1.15) would be a collective benefit and an egregore-positive result; β < 0.9 would be coordination overhead.
    - Distinct repos touched: β ≈ 1 in own-artifact weeks and β < 1 in shared weeks (H06, H11).
  - *Kill for the consistency check:* reply β outside [1.15, 1.55] means H18's dilution law doesn't aggregate.
  - *Models:* 02, 05 · *Builds on:* H18, H40, H58, H06

## Question
Do the swarm's outputs scale with the active population as an independent-agent sum (β = 1), and does H18's per-pair dilution (k^−0.66) aggregate into the predicted superlinear exponent for addressed interactions (β ≈ 1.34)?

## Design: two layers (Vivian, 2026-10-04)
- **Replication:** one point per eligible non-holdout period unit (`period_units`, 71 units). Y and N are per-unit statistics. The exponent is a comparison of units as points on a phase diagram (CLAUDE.md: periods compared by their parameters), not a model fitted to pooled events. Each goal period's README reports its units' points and residuals. Role `replication`.
- **Natives (3):** NE42 (G40; #best and #rest merged for one week: room N doubles with the same agents), G51 (#51 roster growth from about 20 to 31 agents in one room: a within-period N sweep), G38 (two rooms of unequal and changing size on the same days: a within-day room-size contrast). Role `native`.

## Model
**From:** `physics-models/14-scaling-and-fluctuations/` (1. allometric scaling), with the mean-field derivation from per-pair dilution.

**H85 variant: unit-level allometry with a mechanism decomposition.** For output Y in unit u with active population N_u and scheduled hours T_u:

  ln(Y_u / T_u) = α_{regime(u)} [+ δ_{mode(u)}] + β_Y ln N_u + ε_u,   ε_u = ζ_{goal(u)} + e_u

- β_Y = 1: extensive (each agent adds a fixed rate). β > 1: interaction adds output. β < 1: shared overhead or saturation.
- The regime intercept α absorbs the scaffold (chat sessions in I, rooms in II, computer use in III). N is not exogenous: the operators grew the roster over time, so N rises with regime.
- ζ_goal is a goal-period effect shared by the units of one goal (the units of #51 are not independent points).

**Mechanism decomposition (from H18 and H40).** Total addressed responses per hour = N · r_talk · c · k^{1−β_d}, with r_talk the talk calls per agent-hour, k the pending set at a talk call and β_d = 0.66 (H18, mention-based, ledger k). With k ∝ N^{γ_k} and r_talk ∝ N^{ρ}:
- messages: β_msg = 1 + ρ (+ the scaling of messages per talk call, ≈ 0);
- addressed pairs: β_ment = 1 + ρ + (1 − β_d) γ_k, so **β_ment − β_msg = 0.34 γ_k**. If k ∝ N (γ_k = 1) and ρ = 0, β_ment = 1.34 (the HH).
- **One-parent budget (DQ2 reply parents).** DQ2 keeps at most one parent per message (`infra/README.md` Known issues). If a message's addressed responses are Poisson with mean λ ∝ k^{0.34}, the chance that it has a parent is f = 1 − e^{−λ}, and its elasticity in k is 0.34 · λ(1 − f)/f. At the documented parent fractions f = 0.37 (regime I) to 0.54 (regime III) this factor is 0.79 to 0.66, so **β_reply ≈ β_msg + (0.22–0.27) γ_k ≈ 1.25** under H18, not 1.34.

**Rivals.**
- **R1 extensive everything (independent agents):** β = 1 for every output, including addressed pairs; H18's dilution does not aggregate because k does not grow with N (agents read a fixed window) or because addressing saturates.
- **R2 conversation saturation:** addressed pairs per message are fixed by convention (agents name one or two others per message), so β_ment = β_msg.
- **R3 coordination overhead:** committed work β < 0.9 (agents spend calls on talk as N grows).
- **R4 collective benefit (egregore-positive):** committed work β > 1.1.
- **R5 regime confound:** an apparent β from N rising with regime; removed by α_regime and by within-regime slopes.

## Data scheme (`scheme/`)
Script: `scheme/build.py` (shared tables only; no text read; holdout rows removed by `period_units.holdout` and by `common.holdout_mask` on (pt_date, goal_no), asserted).
- **Inputs:** listed above.
- **Transform:**
  1. **Units:** the 71 non-holdout `period_units` rows. Every record is assigned to the unit whose [start, end) contains its timestamp.
  2. **Clock T_u:** scheduled village hours, the overlap of each day's `calendar` window [win_start, win_end) with the unit's [start, end). Sensitivity: `period_affordances.active_hours`.
  3. **Active population N_u:** for each day d in the unit, n_d = agents (Claude Code agent excluded, as in `activity_bins_fixed`) with ≥ 1 record (turn, talk, idle, consolidate or other event) inside the unit's part of the day's window. N_u = Σ_d n_d h_d / Σ_d h_d (h_d = the day's hours in the unit). Sensitivities: roster count (`period_units.n_roster`) and span population (agent first-to-last-record minutes / window minutes).
  4. **Outputs Y_u** (all agent-authored, Claude Code agent excluded):
     - `msg`: agent chat messages (`chat_core`, `speaker_kind = agent`).
     - `ment`: addressed pairs, Σ over agent messages of |`mentions_roster` \ {sender}| (`chat_mentions_clean`).
     - `reply`: DQ2 reply parents with an agent parent (`parent & pair_set = cand & a_kind = 0`); variant `reply_any` with any parent.
     - `commit`: DQ4 agent work commits (`canonical & ~imported & author_kind = agent & ~automated`), by commit time `t`.
     - `repos_day`: distinct repos with ≥ 1 agent work commit per day, averaged over the unit's days (a per-day count, not a rate).
     - mechanism: `talk_calls` (`context_ledger_turns` rows with `talk`), `k_talk` = mean `k_since_talk` at talk calls.
  5. **Covariates:** regime (`period_units`), mode (`period_affordances`: C shared objective, M teams = **shared**; I, F, K, I/K = **own-artifact**), goal number (cluster).
  6. **Room level (natives):** per (unit, day, room) the same outputs by `chat_core.room`, and the room's active population (active agents whose `rooms_timeline` interval covers that day's window midpoint).
- **Output:** `data/processed/H85-output-scaling-with-n/` (`units.parquet`, `room_days.parquet`, `days.parquet` (#51 sweep), `synthetic/`, `replication/`, `natives/`, `_provenance.json`).
- **Regimes covered:** I, II, III (non-holdout units). Regime II has 3 units (33, 35, 36a) and gets no separate slope.

## Eligible units
- `msg`, `ment`, `reply`, `talk_calls`, `k_talk`: all 71 units with T_u ≥ 1 h and ≥ 20 agent messages (`k_talk` needs ledger talk calls).
- `commit`, `repos_day`: units with `period_affordances.git_dense` (agent work is recorded in git there; 36 units), with Y > 0.

## Observables
*Written 2026-10-04 20:04 UTC. Sampling facts already seen: the unit list (ids, dates, regime, roster sizes, mode, git_dense: 36 units), the documented DQ2 parent fractions (37% / 48% / 54% of agent messages in regimes I / II / III, `infra/data-quality/reply_threading.md`), H18's per-period dilution exponents. No output count or N_u has been computed.*

- **O1 exponents β_Y** for Y ∈ {msg, ment, reply, commit} from M1: ln(Y/T) = α_regime + β ln N (OLS over units). Also M0 (no covariates), M2 (+ mode: shared vs own-artifact), within-regime slopes (I and III), and the sensitivities (N_roster, N_span; active hours).
  - **CI (primary):** goal-period cluster bootstrap (resample goal periods with their units; 2,000 draws; percentile). Secondary: unit bootstrap and HC1.
  - **WLS check:** weights ∝ min(T_u, 40 h) (long units are less noisy), reported next to OLS.
- **O2 mechanism:** γ_k (scaling of k_talk with N, M1) and ρ (scaling of talk calls per agent-hour with N). Unfitted prediction: Δβ = β_ment − β_msg = 0.34 γ_k; β_reply − β_msg = 0.25 γ_k (budget-corrected).
- **O3 repos:** ln(repos_day) = α_regime + β ln N + θ ln(h_day) by mode class (own-artifact vs shared), and the interaction β_shared − β_own.
- **O4 residuals:** per unit, the M1 residual for each output (reported in the period READMEs as the unit's distance from the scaling line).

## Null / baseline
*Written 2026-10-04 20:04 UTC.*
- **Independent-parts reference:** β = 1 for every output (a reference, not a null: the regime field and the goal effect are the real nuisances).
- **Calibration on synthetic units** at the real (N_u, T_u, regime, goal) layout with planted β (`analysis/synthetic.py`): bias, CI coverage and power of the cluster bootstrap, and the regime-confound scenario.
- **Within-regime slopes** as the check against R5.
- **Natives:** placebo boundaries (NE42: the #39 → #41 contrast without a room change; G51: calendar splits without roster joins; G38: rooms without size change).

## Impostor table (STANDARDS.md §1)
| Impostor | How it could fake this result | How H85 removes it | Status |
| --- | --- | --- | --- |
| Scheduler field | Longer scheduled days or always-on running raise totals and correlate with N (later regimes run longer and have more agents) | Y is per scheduled hour; regime intercepts; within-regime slopes; active-hour sensitivity | partly (hours per day still differ inside regime I) |
| Exogenous field (goal, kickoff, operator) | Goals that demand talk or coding (debates, competitions) sit at particular N; operator nudges add messages | mode covariate (M2); goal-period cluster bootstrap; natives hold the goal fixed (G51) or the agents fixed (NE42) | partly (NE42 coincides with goal #40) |
| Shared model priors (family, style) | Larger rosters add chattier families (regime III newcomers), so per-agent rates rise with N through composition, not interaction | regime intercepts; NE42 keeps the same agents; G51 sweep adds agents one at a time (composition is stated); per-agent rate check by family left for round 2 | partly |
| Contemporaneous convergence | Not a copying claim. Addressed pairs could rise because agents name everyone in a crowded room without reading (co-addressing) | H18's dilution is measured on ledger-visible pending sets; the decomposition uses the same k; mention pairs are reported with reply parents (content-labelled) | n/a for β; partly for the mechanism |

## Prediction
*Written 2026-10-04 20:04 UTC, before running the analysis on real data.*

Design SE (model 14): ≈ 0.10 per exponent across 71 units, wider with covariates and goal clustering. So 1.34 vs 1 is resolvable; 1.15 vs 1 is not.

**Replication (card level).**
- **P1 messages:** β_msg ∈ [0.85, 1.15] and its 95% cluster CI includes 1. *Against:* CI excludes 1 (per-agent posting rate changes with N). Prior 0.6.
- **P2 replies (HH kill, DQ2 parents agent→agent):** β_reply ∈ [1.15, 1.55]. Budget-corrected expectation ≈ 1.25 (Model). *Against:* β_reply < 1.15 or > 1.55 (the HH's kill: dilution does not aggregate). Prior 0.45.
- **P3 addressed pairs (budget-free form of the HH, primary for the mechanism):** β_ment ∈ [1.15, 1.55], and Δβ = β_ment − β_msg within ± 0.15 of 0.34 γ̂_k. *Against:* Δβ CI includes 0 (R2: addressing saturates) or Δβ deviates from 0.34 γ̂_k by > 0.15. Prior 0.45.
- **P4 pending set:** γ_k ∈ [0.7, 1.3] (k ∝ N). *Against:* γ_k < 0.5 (agents read a fixed window: R1's mechanism).
- **P5 committed work:** β_commit ∈ [0.9, 1.1] with the CI including 1 (H58: agent + own artifact). *Against:* CI entirely above 1.1 (R4, egregore-positive) or entirely below 0.9 (R3). At SE ≈ 0.10–0.15 a pass is "consistent with extensive", not a rejection of 1.15.
- **P6 distinct repos per day:** own-artifact units β_own CI includes 1; shared units β_shared < 0.85, and β_shared < β_own (one-sided cluster-bootstrap p < 0.1). *Against:* β_shared ≥ β_own. Prior 0.35 (few units per class).

**Natives (dated predictions also in each folder).**
- **N1 NE42 (G40 vs G39, G41; the same ≈ 15 agents, room population doubled):** per-agent message rate ratio (merged / split) ∈ [0.8, 1.25]; k_talk ratio ≥ 1.5; per-agent addressed-pair rate ratio = (k ratio)^{0.34} ± 0.15 and > 1. Placebo: #39 → #41 (no room change) ratios within [0.8, 1.25]. *Against:* k ratio < 1.3 (merging did not enlarge the pending set) or addressed-pair ratio ≤ 1 with k ratio ≥ 1.5.
- **N2 G51 sweep (non-holdout days 07-06 → 09-04, day-level points, step dummies for NE43 at 08-05 and 08-21):** β_msg ∈ [0.7, 1.3]; β_ment − β_msg > 0; β_commit CI includes 1. *Against:* β_ment − β_msg ≤ 0 with CI below 0. Sensitivity: a linear day trend (roster growth is confounded with time since kickoff).
- **N3 G38 room contrast (rooms #best and #rest, day fixed effects, room-day points):** β_room,msg ∈ [0.7, 1.3] and β_room,ment > β_room,msg. Descriptive if the SD of the within-day log room-size ratio is < 0.1.

**Overall reading (fixed now).** **Supported** if P1 and P5 pass and P2 or P3 passes (dilution aggregates, work is extensive). **Mixed** if P1 and P5 pass but P2 and P3 both fail, or if exactly one of P1 and P5 fails. **Failed** if both P1 and P5 fail. P5's direction decides the egregore reading: CI above 1.1 is a collective-benefit lead and goes to the holdout first.

## Synthetic validation (axis F; run 2026-10-04 20:06–20:09 UTC, before any real-data exponent)
`analysis/synthetic.py` → `data/processed/H85-output-scaling-with-n/synthetic/synthetic.json`. Real layout: 71 units, 35 goal clusters, N_u and T_u as built (SD ln N 0.59; within regime I 0.38, II 0.04, III 0.35). Poisson counts with a goal effect (SD 0.3) and a unit residual (SD 0.4). 200 replicates, 300 cluster-bootstrap draws each.

| Check | Result |
| --- | --- |
| β (M1) bias, planted 0.85 / 1.00 / 1.15 / 1.34 | −0.02 / +0.02 / +0.02 / +0.02 |
| β SD and mean 95% CI width | 0.23–0.26; 0.86–0.88 (**not** the design 0.10: regime intercepts leave SD ln N ≈ 0.37, and 35 goal clusters, 12 units in #51) |
| Cluster-CI coverage | 0.90–0.93 (slightly anti-conservative) |
| Power to reject β = 1 at 1.15 / 1.34 | 0.20 / 0.38 |
| Power to reject 1.34 at β = 1 | 0.31 |
| Regime confound (β = 1, regime III +0.7) | M0 1.43, M1 0.98: regime intercepts are required |
| Commits on the 36 git-dense units (β 1.0 / 1.15) | SD 0.51; CI width 3.5; power vs 1 ≈ 0.05 |
| Repos interaction (own 1.0, shared 0.7) | power 0.00, size 0.02 |
| Mechanism (H18 dilution, k ∝ N): β_msg / β_parent (DQ2 budget) / β_ment | 1.00 / 1.26 / 1.35 |
| Δβ_ment = slope of ln(ment/msg), extra ratio noise (goal 0.15, unit 0.25), planted 0 / 0.17 / 0.34 | mean 0.01 / 0.18 / 0.35; SD 0.13–0.15; coverage 0.92–0.94; reject 0: 0.06 / 0.32 / 0.79; reject 0.34 when 0: 0.73 |

Readings: (1) The level exponents across units cannot separate 1.15 from 1, and separate 1.34 from 1 only 38% of the time. (2) The per-message addressing slope Δβ shares the units' chattiness noise with messages, so it is the powered form of the consistency check. (3) Commit and repo exponents across units are unidentified at this layout; the within-period natives carry the work claim.

## Amendments (2026-10-04 20:09 UTC, after the synthetic validation, before any real-data exponent)
- **A1 (level tests are wide).** P1–P3 level clauses and the HH kill are judged on the cluster CI: a level is *consistent* if its CI contains the predicted value and *against* if the CI excludes it. The HH kill fires only if the β_reply CI lies entirely below 1.15 or entirely above 1.55. The CR1 t(G − 1) interval is reported too; verdicts use the wider of the two.
- **A2 (primary consistency test).** P3 is judged on Δβ_ment, the M1 slope of ln(ment/msg) on ln N (goal-cluster CI): pass if its CI excludes 0 and contains 0.34 γ̂_k. The same for replies: Δβ_reply (slope of ln(reply/msg)) against 0.25 γ̂_k (budget-corrected; synthetic 0.26).
- **A3 (work is descriptive across units).** P5 and P6 are reported without verdict weight across units. The work claim moves to the natives (G51 sweep, NE42). **Overall reading restated:** **supported** if P1 is consistent and A2's Δβ_ment passes; **mixed** if exactly one of them holds; **failed** if neither. A G51 or NE42 commit exponent with CI above 1.1 is flagged as an egregore lead.

## Results by goal period
Roles: `replication` = the period's units as points on the cross-unit lines (descriptive: one period cannot test a slope); `native` = a period-specific design. NE42 spans G39–G41.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G02](goalperiod-subhypotheses/G02/README.md) | replication | descriptive | N 3.5–3.5; msg/agent-h 42.34; addressed/msg 1.22; reply share 0.65 |
| [G03](goalperiod-subhypotheses/G03/README.md) | replication | descriptive | N 4.0–4.0; msg/agent-h 68.55; addressed/msg 0.86; reply share 0.45 |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | descriptive | N 4.0–4.0; msg/agent-h 31.31; addressed/msg 0.56; reply share 0.42 |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | descriptive | N 4.0–4.0; msg/agent-h 28.09; addressed/msg 0.48; reply share 0.36 |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | descriptive | N 4.0–4.0; msg/agent-h 12.74; addressed/msg 0.23; reply share 0.24 |
| [G07](goalperiod-subhypotheses/G07/README.md) | replication | descriptive | N 4.0–4.0; msg/agent-h 23.89; addressed/msg 0.21; reply share 0.36 |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | descriptive | N 4.0–4.0; msg/agent-h 15.16; addressed/msg 0.25; reply share 0.19 |
| [G10](goalperiod-subhypotheses/G10/README.md) | replication | descriptive | N 7.0–7.0; msg/agent-h 12.60; addressed/msg 0.15; reply share 0.07 |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | descriptive | N 7.0–7.0; msg/agent-h 22.96; addressed/msg 0.86; reply share 0.24 |
| [G12](goalperiod-subhypotheses/G12/README.md) | replication | descriptive | N 7.0–7.0; msg/agent-h 34.49; addressed/msg 1.14; reply share 0.34 |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | descriptive | N 6.0–6.0; msg/agent-h 25.46; addressed/msg 0.57; reply share 0.30 |
| [G16](goalperiod-subhypotheses/G16/README.md) | replication | descriptive | N 7.0–7.0; msg/agent-h 18.37; addressed/msg 0.73; reply share 0.21 |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | descriptive | N 7.0–7.0; msg/agent-h 18.99; addressed/msg 1.02; reply share 0.22 |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | descriptive | N 7.0–8.0; msg/agent-h 24.65; addressed/msg 1.34; reply share 0.45 |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | descriptive | N 7.0–8.0; msg/agent-h 18.86; addressed/msg 1.27; reply share 0.43 |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | descriptive | N 8.0–10.0; msg/agent-h 12.30; addressed/msg 1.28; reply share 0.33 |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | descriptive | N 8.0–9.0; msg/agent-h 14.50; addressed/msg 1.45; reply share 0.25 |
| [G23](goalperiod-subhypotheses/G23/README.md) | replication | descriptive | N 10.0–10.0; msg/agent-h 8.85; addressed/msg 0.68; reply share 0.21 |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | descriptive | N 10.0–10.0; msg/agent-h 8.31; addressed/msg 0.55; reply share 0.23 |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | descriptive | N 9.8–9.8; msg/agent-h 13.29; addressed/msg 1.83; reply share 0.48 |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication | descriptive | N 10.0–10.0; msg/agent-h 13.33; addressed/msg 1.62; reply share 0.46 |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | descriptive | N 10.0–10.0; msg/agent-h 9.32; addressed/msg 0.91; reply share 0.34 |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | descriptive | N 11.0–11.0; msg/agent-h 10.79; addressed/msg 0.90; reply share 0.37 |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | descriptive | N 11.0–12.0; msg/agent-h 12.43; addressed/msg 1.11; reply share 0.35 |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication | descriptive | N 11.0–11.0; msg/agent-h 13.41; addressed/msg 1.40; reply share 0.45 |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | descriptive | N 12.0–12.0; msg/agent-h 8.72; addressed/msg 0.61; reply share 0.48 |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | descriptive | N 12.0–12.0; msg/agent-h 6.53; addressed/msg 0.83; reply share 0.42 |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | descriptive | N 12.0–12.0; msg/agent-h 2.82; addressed/msg 0.81; reply share 0.69 |
| [G38](goalperiod-subhypotheses/G38/README.md) | native | mixed | room contrast: β_msg 0.36 [0.02, 0.82], β_ment 1.12 [0.31, 2.04], β_k 1.11. N 12.0–13.7; msg/agent-h 5.09; addressed/msg 0.62; reply share 0.45 |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | descriptive | N 14.8–14.8; msg/agent-h 2.90; addressed/msg 0.55; reply share 0.18 |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | descriptive | N 15.0–15.0; msg/agent-h 5.69; addressed/msg 0.87; reply share 0.34 |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | descriptive | N 15.0–15.0; msg/agent-h 7.10; addressed/msg 1.33; reply share 0.53 |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | descriptive | N 15.0–16.0; msg/agent-h 3.87; addressed/msg 1.00; reply share 0.49 |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | descriptive | N 16.0–17.5; msg/agent-h 6.41; addressed/msg 1.20; reply share 0.73 |
| [G51](goalperiod-subhypotheses/G51/README.md) | native | descriptive | day sweep unidentified (SD ln n 0.08; β_msg −0.02 [−0.76, 2.08]). N 21.0–32.0; msg/agent-h 4.09; addressed/msg 1.00; reply share 0.55 |
| [NE42](goalperiod-subhypotheses/NE42/README.md) | native | failed | placebo #41/#39 ×2.5–7.5; k ratio 1.34 [0.89, 2.01]; addressed ratio 0.90 (pred 1.10); commits ×1.45 |

## Outcome vs prediction
*Run 2026-10-04 20:13–20:16 UTC (`analysis/replication.py`, `analysis/natives.py`). 71 non-holdout units, 35 goal clusters; M1 = regime intercepts; 95% goal-cluster bootstrap CI (CR1 t interval in brackets where it is wider).*

| Prediction | Observed | Verdict |
| --- | --- | --- |
| P1 messages β ∈ [0.85, 1.15], CI includes 1 | β_msg 0.33 [−0.18, 0.64] (CR1 [−0.02, 0.68]); regime I 0.09, regime III 0.77; WLS 0.52, roster N 0.34, active hours 0.26 | **fail** (sublinear) |
| P2 reply parents β ∈ [1.15, 1.55] (HH kill if the CI lies outside) | β_reply 0.36 [−0.46, 0.87]; parents per message vs N 0.02 [−0.35, 0.30] against a budget-corrected 0.32 | **fail: the HH kill fires** |
| P3 / A2 addressing per message Δβ_ment: CI excludes 0 and contains 0.34 γ̂_k | Δβ_ment 0.79 [0.41, 1.39] vs predicted 0.44 [0.31, 0.52]; difference 0.36 [−0.06, 1.05]. β_ment 1.13 [0.42, 1.83] (contains 1.34) | **pass** (point about twice the prediction) |
| P4 pending set γ_k ∈ [0.7, 1.3] | γ_k 1.29 [0.91, 1.52]; within-day room contrast 1.02 [0.88, 1.15] | **pass** |
| P5 committed work β = 1.0 ± 0.1 (descriptive after A3) | β_commit 1.89 [0.55, 7.76] on 36 git-dense units (CR1 [0.96, 2.82]) | descriptive (unidentified) |
| P6 repos per day, own vs shared (descriptive after A3) | own 1.30 [−4.0, 1.4]; shared 3.2 [−7.3, 9.6] | descriptive (unidentified) |
| N1 NE42 merge: msg ratio ∈ [0.8, 1.25]; k ratio ≥ 1.5; addressed ratio = k^0.34 | msg 1.14 [0.90, 1.41]; k 1.34 [0.89, 2.01]; addressed 0.90 [0.42, 1.59] (pred 1.10); placebo #41/#39 ×2.5 (msg) to ×7.5 (replies) | **failed** (placebo invalid) |
| N2 G51 sweep: β_msg ∈ [0.7, 1.3]; Δβ_ment > 0 | β_msg −0.02 [−0.76, 2.08]; Δβ_ment 0.62 [−0.22, 4.06]; SD ln n_d 0.08 | descriptive (unidentified) |
| N3 G38 room contrast: β_room,msg ∈ [0.7, 1.3]; β_ment > β_msg | β_msg 0.36 [0.02, 0.82]; β_ment 1.12 [0.31, 2.04]; Δ 0.76 [−0.15, 1.62] | **mixed** |

**Overall (pre-registered reading, A3):** P1 fails and the A2 consistency test passes, so H85 is **mixed**. Addressing per message rises with N about as H18's dilution predicts (or faster). But it rides on a sublinear message base: the swarm's talk volume grows much more slowly than its population, and reply parents per message do not rise at all.

## Results
**1. Talk is sublinear: agents talk less as the room fills.** Messages per scheduled hour scale as N^0.33 [−0.18, 0.64] across units with regime intercepts. In regime I the room's talk throughput is nearly fixed (β 0.09). Every agent keeps its call clock (all calls per agent-hour vs N: −0.02 in regime I, post hoc PH2). Each agent's share of talking calls falls as N^−0.89, so the total is conserved. In regime III talk is closer to extensive (β 0.77) and agents make fewer calls per hour as N grows (−0.47). Messages per talk call do not change with N (−0.015). So the sublinearity is a choice to talk, not a scaffold cap on calls. Within-day room contrasts (same day, two rooms of different size) give the same sign: G38 0.36 [0.02, 0.82]; random-effects mean over the four identified rooms-era periods 0.85 [0.17, 1.53] (exception (d)).

**2. Addressing per message rises with N, as dilution predicts or faster.** The pending set at a talk call grows as k ∝ N^1.29 [0.91, 1.52] across units and as N^1.02 [0.88, 1.15] across rooms on the same day. H18's dilution then predicts an addressing slope of 0.34 γ_k = 0.44. Observed: 0.79 [0.41, 1.39] across units and 0.65 [0.21, 1.09] across rooms (random effects). Post hoc (PH1): about two thirds of the slope is the share of messages that name anyone (N^0.55 [0.23, 0.90]); the rest is names per naming message (N^0.25), all in regime I (0.44; regime III −0.09). So regime-I co-addressing inflates the count. Regime III is close to the dilution prediction (0.42 vs 0.34 × 1.81 = 0.62).

**3. Reply parents do not aggregate.** DQ2 parents per message are flat in N (0.02 [−0.35, 0.30]) against a budget-corrected 0.32 [0.23, 0.38] (difference CI excludes 0). With the sublinear message base, β_reply = 0.36, and the HH's kill fires. The one-parent budget explains part of it (synthetic β_parent 1.26 vs β_ment 1.35 under H18), not a flat share. Either the reply labeller's parent rate is set by thread structure rather than by pending load, or responses to a larger pending set go to more targets per message without raising the chance that a message has a parent at all.

**4. Work exponents are unidentified across units.** Committed work gives β 1.89 [0.55, 7.76] on 36 git-dense units: superlinear at the point, but the synthetic SD at this layout is 0.51 and the git-dense units sit in a few goal clusters (12 of 36 are #51). Distinct repos per day are unidentified. The within-period designs that should carry the work claim failed: the G51 sweep has too little day-level N variation once the NE43 steps are absorbed (SD ln n 0.08), and NE42's placebo shows goal effects of ×2.5–7.5 between adjacent weeks.

**5. Precision.** The design SE from model 14 (0.10) was optimistic by 2.5×: regime intercepts leave SD ln N ≈ 0.37 and the 71 units form 35 goal clusters. A level exponent across units cannot separate 1.15 from 1 (power 0.20). Ratio slopes (per-message quantities) cancel the units' shared chattiness and have SD ≈ 0.13.

Figures: `figures/summary_obs.pdf` (messages per hour and addressing per message against N, by regime), `figures/summary_obsb.pdf` (exponents against predictions; within-day room contrasts). Data: `data/processed/H85-output-scaling-with-n/` (`units.parquet`, `days.parquet`, `agent_units.parquet`, `room_days.parquet`, `replication/`, `natives/`, `posthoc/`, `synthetic/`, `confirm/confirm_dryrun.json`). Estimates: 571 rows in `per_period_estimates` (hypothesis H85: per-unit rates, addressing per message, reply share, k; native room exponents for G36/G38/G42/G44 and the G51 sweep). The cross-unit exponents are phase-diagram slopes, not per-period fits, so they are not in that table.

## Faithfulness scorecard
*Round 1, 2026-10-04.* Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed.
**Rival models:** R1 extensive everything; R2 conversation saturation; R3 coordination overhead; R4 collective benefit; R5 regime confound.
**Locked holdout used for confirmation:** none yet (`analysis/confirm.py`, dry-run only).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | N, T, every output and k come from shared tables with stated filters. The mapping is not regime-invariant: regime I talk is a per-agent share of a fixed clock, regime III is not; "addressed pairs" mixes responses with co-addressing in regime I. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | A single power law per output fails across regimes (messages 0.09 vs 0.77). N is endogenous (roster grew over time); regime intercepts are required (synthetic M0 bias +0.43). |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Regime intercepts and goal clusters handled; exponents robust to WLS, roster N, span N and active hours (messages 0.26–0.52). No held-out-day prediction. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | Addressing slope predicted from the measured k scaling (unfitted): consistent (0.79 vs 0.44, CI includes it). Reply prediction fails. |
| E interventional | predicts the change across a natural experiment | 0 | NE42's placebo fails (goal effects ×2.5–7.5); the G51 sweep is unidentified. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 2 | Synthetic at the real layout: bias ≤ 0.02, coverage 0.90–0.93, the true SD (0.25) and power; regime-confound scenario; the powered ratio form found and adopted before real data (A2); work and repo exponents declared unidentified (A3). |
| G ground truth | agrees with known structure | 1 | k ∝ N in rooms on the same day (1.02 [0.88, 1.15]); the per-agent call clock is fixed in regime I (−0.02), as the ledger documents scheduled chat calls. |
| H comparative | beats the named rivals | 1 | R1 (extensive) fails for talk (sublinear) and for addressing (Δβ > 0); R2 (saturation) loses for addressing but wins for reply parents; R5 handled by intercepts and within-regime slopes; R3/R4 untestable here. |
| I transfer | holds in other same-mode periods, including the holdout | 1 | Within-day room contrasts in 4 rooms-era periods reproduce sublinear talk and rising addressing; holdout not run. |

## Confirmatory predictions (written 2026-10-04 20:20 UTC after round 1, before any holdout use; `analysis/confirm.py`, dry-run only, **not run**)
Targets: held-out period units (held-out goal periods and NE-window units), fitted on their own.
- **C1:** β_msg < 0.85 with CI upper bound < 1.10.
- **C2:** Δβ_ment CI excludes 0, and the CI of Δβ_ment − 0.34 γ_k contains 0.
- **C3:** reply parents per message: slope < 0.20 with CI containing 0.
- **C4:** regime-I held-out units: talk share of calls falls faster than N^−0.5.
- **Overall:** confirmed if C1 and C2 pass. Dry run on the 71 non-holdout units: C1–C4 pass (C4 slope −0.82).
- **Reuse disclosure:** family `dilution_addressing` overlaps H18's confirm script on the same held-out periods; disclose in both cards and LOG.md if both run.

## Caveats
- **Regime I chat mode** rebuilt the prompt from recent chat with an unknown message limit (2025-08-20); a fixed visible window could make agents talk less when the room is busy. The talk budget may be partly a scaffold property of chat mode.
- **N is the active population**, hour-weighted. Roster growth is confounded with calendar time (model generations, operator practice); regime intercepts remove only the largest steps.
- **Addressed pairs** count names, not responses: in regime I, names per naming message rise with N (co-addressing). A pending-sender restriction (names of agents whose messages were pending at that call) would be the clean aggregate of H18.
- **Reply parents** carry the one-parent budget and the labeller's thread-membership bias (Known issues).
- **Room contrasts** have no room fixed effect (pre-registered); rooms with fixed size ratios identify β only through the between-room difference.
- **Post hoc:** PH1 (naming share vs names per message) and PH2 (call clock and talk share) were added after the pre-registered results.

## Round 2 redirects (2026-10-04)
*Proposed by the round-1 agent; the coordinator may revise.*
- **Where round 1 went sideways:** the HH treated output volume as N × a fixed per-agent rate. Talk is not like that: the room's talk volume is nearly conserved in regime I, so every interaction count inherits a sublinear base. The cross-unit design also had 2.5× less power than the design note claimed.
- **What the direction is really after:** whether the swarm produces more per agent as it grows (a collective benefit), and how much of its talk is a shared, capacity-limited channel.
- **H85-R1. Talk budget model.** Fit each agent's talk probability per call against the room's traffic (messages received at that call, ledger) within periods. Test whether room talk throughput stays constant across roster joins inside a day (regime I) and across the #38 room-size changes.
- **H85-R2. Pending-sender addressing.** Count only names of agents with a pending message at the talk call (context ledger). Its N slope is the clean aggregate of H18's dilution; co-addressing drops out.
- **H85-R3. Work per agent across joins.** Commits per agent-hour of incumbents before and after each roster join (agent fixed effects, #18–#51), the within-agent design that the cross-unit fit cannot give.
- **H85-R4. Uncapped replies.** A multi-label reply sample of pending candidates (DQ2 follow-up) to test reply aggregation without the one-parent budget.


## Notes
- 2026-10-04: the first draft of this card carried hand-written timestamps (20:10, 20:33–20:40 UTC) that ran ahead of the clock. They were corrected from file modification times at 20:25 UTC: card 20:04, synthetic.json 20:08:46, amendments 20:09, units.parquet rebuilt and replication.json 20:13:22, natives.json 20:14:59. The order (card → synthetic → amendments → real runs) is unchanged.
- 2026-10-04: `ment_msgs` (messages naming ≥ 1 agent) was added to the build after the main run, for PH1 only; the rebuild leaves every other column unchanged.
- 2026-10-04: runs used one process at a time (≤ 2 threads); outputs ≈ 0.3 MB with `_provenance.json`. No code is imported from another hypothesis; H54's and H86's processed tables are not used by H85's pre-registered tests.
- 2026-10-04 20:04 UTC: card written by the round-1 agent before any real-data statistic. Kickoff specificity (H54) is used only by H86. Model 05 (replicator dissipation) is listed on the HH but has no role in a unit-level size law; it is not used.
