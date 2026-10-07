# H127: Content trails a moving goal like an overdamped particle: agents that call more catch up faster

**Status:** exploratory round 1 **done (2026-10-04): not supported. There is no rise to time: at a kickoff an agent's alignment with the new goal jumps at its read-out call and then decays. The call-rate slope is inconclusive by the amended rule; the read-out-jump rival fits.**
- **Read-out jump (P4, failed for HH368; rival R_L favoured).** 74% of 152 rising agents (bge; 75% gte) reach their day-1 plateau within the read-out call itself (synthetic relaxation worlds ≤ 0.20, read-out jump 0.42–0.47). Median half time < 1 s after the read-out (grid floor); median read-out delay 75 s after t₀.
- **Spike then decay (descriptive, post hoc).** Normalized alignment is 2.4× the late day-1 plateau at the read-out call, 1.5–1.8× over calls 8–63, and 1× after 64 calls (about 1 h).
- **Slope (P1 pooled, not supported):** +0.59 [−0.45, +1.75] (bge), +0.42 [−0.96, +1.45] (gte); the kill clause does not apply (median rise 0.15–0.19 < 0.4, power ≈ 0.35). **Clock test (P3, read-out origin):** ΔSSE_ro −0.0009 [−0.0019, +0.0001] / −0.0000 [−0.0005, +0.0004].
- **Natives:** G51 failed (21 agents, 5× cadence spread, all half times at the floor); NE38 descriptive (Opus 5's mid-day reassignment gives a resolved rise, T½ 0.20–0.24 h ≈ 16–19 calls).
- Card and predictions written 22:18 UTC; Amendment 1 (22:58 UTC) after the synthetic, before real data. `analysis/confirm.py` frozen and dry-run (reproduces the stand-ins); **not run**. Scorecard A1 B1 C1 D0 E1 F2 G1 H1 I1.
**Question (GOALS.md):** **Q1** (what couples agents, and on which clock): does an agent's content relax toward a new goal per model call (the call clock H40 found for replies) or per hour? Second: **Q5** (cadence as a lever: does doubling an agent's call rate halve its catch-up time?).
**Fields:** stat mech (overdamped Langevin relaxation in a moving well), dynamics (time-rescaling, data collapse)
**Literature:** none in `literature/` covers this. Background from memory: Brown, Barbieri, Ventura, Kass & Frank, *Neural Comput.* 14, 325 (2002)† (time-rescaling: a process is simple in its own intensity clock); Glauber, *J. Math. Phys.* 4, 294 (1963)† (attempt rate sets the relaxation time). Project cards: H40 (call clock for replies in regimes II–III, not I; per-hour coupling ∝ call rate, slope 1.00 in G51), H103 (remanence decays on active work, not nights; an agent's own idle hour does not age its content), H97 (kickoff restoring force, overshoot), H54 (kickoff target), H48 (coverage 0.24 active h, settling τ ≈ 4.5 active h), H75 (named-target kickoffs freeze within 0.5 active h), H100 (agent constants â_i), H08 (read-out gating at the recipient's next call).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent (19, 28, 30 excluded); Regime (whitening per regime; every kickoff inside one regime); Driving / external field (the kickoff; #51 `agent_goal` for the natives); **Exposure (turn read-out)** (H08) via the shared context ledger; H40's **call clock** and **per-call / per-hour** distinction; Activity time, in H103's **active-hour clock H**; Agent state, variant *vector* (unit regime-whitened statement vectors, d = 32); H125's **kickoff excess alignment a(h)** (proposed). New named variants proposed (defined under Observables; DEFINITIONS.md not edited): **half-alignment time T½**, **call rate r_i (day 1, leave-period-out)**, **collapse ratio CR**, **within-agent clock gain ΔSSE_c**, **read-out half time T½^ro**.
**From:** HH368 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/11-vector-spins/` (primary: content spin relaxing toward the field direction), `physics-models/02-nonequilibrium-ising/` (secondary: Glauber attempt rate = call rate)
**Model folder:** `physics-models/16-langevin-relaxation/` (added 2026-10-07)

## Source HH (verbatim from the HH list, including refinements)
- **HH368 · Content trails a moving goal like an overdamped particle: agents that call more catch up faster.** Model content as a particle in a potential well that moves when the goal moves (Langevin: ẋ = −k(x − g(t)) + noise). H103 says the clock is active work. So each agent's lag behind the goal should scale with its own call rate.
  - *Prediction:* per agent, the time to reach half of its settled alignment after a kickoff falls with its calls per active hour (log-log slope near −1); measured in calls, it is the same for all agents (data collapse).
  - *Check:* per-agent half-alignment times across non-holdout kickoffs; regress on call rate; compare the collapse on calls vs hours.
  - *Kill:* slope near 0, or no improvement in the collapse when time is measured in calls.
  - *Impostors:* busy agents may also be more on-task (a field); control for agent constant (H100 â_i) and lab.
  - *Models:* 11, 02 · *Builds on:* H97, H103, H40, HH344

## Standards (2026-10-04)
**Question served:** Q1 (the clock of content relaxation), Q5 (cadence as a lever).

| Impostor | Relevant? | How it is handled | Status |
| --- | --- | --- | --- |
| Scheduler field | partly | Day-1 times after t₀ only (no night inside a fit). The within-agent clock test uses each agent's own pauses: during a pause hours run and calls stop, so a common scheduler profile does not favour either clock. | removed |
| Exogenous field (kickoff/goal/operator) | yes | The kickoff is the field; the question is each agent's speed toward it. Busy agents may be more on-task (HH368's impostor): controls are the agent's on-task trait â_i^on (leave-kickoff-out settled excess alignment, an H100-style agent constant) and lab fixed effects in the pooled model. The leave-period-out call rate removes "busy today because on-task today". | partly |
| Shared model priors | yes | Lab fixed effects; â_i^on absorbs a family's prior affinity for goal text; style variant `statements_style_resid_period32`; both embedding models. | partly |
| Contemporaneous convergence | no | No agent-to-agent influence claim. Each agent relaxes toward a common field; read-out gating (rival R_L) is a field-delivery delay, tested directly. | n/a |

**Inputs:** H125's processed statement table (`data/processed/H125-kickoff-damped-oscillator/stmt.parquet`, `kickoffs.parquet`, `vectors.npz`; read-only, same holdout mask); DQ1 `call_windows` (agent call times), `context_ledger_items` (read-out call of the kickoff message); `kicks_classified` (kickoff message ids); `roster` (lab); DQ5 statement vectors (both models, white32 and style variants); `holdout_mask`. No text is read.

**Two layers:** replication on every eligible kickoff (role `replication`); natives G51 (own-role alignment of ~21 agents with a 7× spread of call rates) and NE38 (one-agent reassignment: an out-of-sample prediction of Opus 5's half time from its call rate), role `native`.

**Confirm script:** `analysis/confirm.py`, frozen and guarded, not run.

## Question
After a kickoff, does each agent's content approach its settled alignment with the new goal at a rate set by its own model calls, so that the half-alignment time in hours scales as 1/(call rate) and the curves collapse when time is counted in calls?

**Practical payoff:** if content relaxes per call, an operator who doubles an agent's cadence halves the time it trails a new goal, and the catch-up time of any agent is predictable from one constant (calls to half alignment).

## Model
**From:** `physics-models/11-vector-spins` (content state along the field direction k̂) with Glauber kinetics (`physics-models/02-nonequilibrium-ising`: the attempt rate sets the time unit).

**H127 variant: overdamped relaxation in a well that jumps at t₀, on a clock c.** For agent i, the excess alignment a_i(t) (H125) obeys
  da_i/dc = −k (a_i − S_i) + noise,  c ∈ {H (active hours since t₀), C (own calls since t₀)},
with S_i the settled level (days 2–5) and P_i the pre-kickoff level. The mean response is
  E[a_i(t)] = P_i + Δ_i (1 − e^{−c_i(t)/τ_c}),  Δ_i = S_i − P_i,  T½ = τ_c ln 2.
- **Call clock (HH368):** τ_C is one constant for all agents. In hours, τ_H,i = τ_C / r_i, so log T½,i^H = const − log r_i (slope −1).
- **Wall/active-hour clock (rival R_W):** τ_H is one constant; slope 0.

**Rivals:**
- **R_W hour clock:** slope 0; the collapse is worse in calls.
- **R_L read-out jump (H08 gating):** content jumps at the agent's first read-out call of the kickoff and does not relax further. The half time from t₀ is the read-out delay, which also scales as ≈ 1/r_i (slope ≈ −1). Measured from the read-out call, T½^ro ≈ 0 and does not depend on r_i. This rival reproduces HH368's headline without per-call relaxation.
- **R_F on-task field:** agents with a strong affinity for goal content both call more and move faster; the slope vanishes with â_i^on and lab controls.
- **R_S sampling:** fast agents emit more statements per hour, so their fitted rise is resolved earlier; synthetic worlds at the real statement and call times size this.

## Data scheme (`scheme/`)
`scheme/build.py` builds `data/processed/H127-content-trails-goal-call-clock/` from H125's statement table and shared call tables. No text is read.
- **Kickoffs:** H125's eligible kickoffs (27; #4, 5, 6, 8, 10–13, 16–21, 24–27, 30, 31, 35, 38–42, 51). Counts seen before writing: 4–21 incumbents per kickoff.
- **Agents per kickoff:** H125 incumbents with ≥ 4 `pre` statements (previous non-holdout active day plus day 1 before t₀), ≥ 8 day-1 statements after t₀, ≥ 4 statements on days 2–5, and ≥ 3 calls on day 1 after t₀.
- **Read-out call:** the agent's first call (`call_windows.t_call`) whose context ledger holds a kickoff message of period p (`kicks_classified` kind `human_message`, subkind `kickoff`, or kind `goal_kickoff`, matched by `message_id`, `omitted` false). Fallback: the first call after t₀ (flagged).
- **Per statement (day 1 after t₀):** hours since t₀, own calls with t_call in (t₀, t_s], hours and calls since the read-out call.
- **Per agent:** day-1 call rate r_i = calls on day 1 after t₀ / active hours from t₀ to the day's window end; leave-period-out cadence r_i^LPO = the agent's calls per active hour over all other non-holdout periods of the same regime; lab.
- **Output:** `agents.parquet` (kickoff, agent, P_i, S_i, Δ_i and SE, r_i, r_i^LPO, t_ro, fallback flag, lab, counts), `day1.parquet` (statement row, kickoff, agent, clocks), `_provenance.json`. Analysis outputs in `G<NN>/`, `NE34/` (cross-kickoff), `natives/`, `synthetic/`.
- **Regimes covered:** I, II (#35), III.

## Observables
*Specified 2026-10-04 22:18 UTC, before any real-data statistic along a kickoff direction.*
- **Excess alignment a_s:** H125's per-statement genericness-corrected projection on k̂_p (linear; no renormalized windows).
- **Levels:** P_i = mean a_s over `pre`; S_i = mean a_s over days 2–5; Δ_i = S_i − P_i with SE from the statement variances. **Rising agents:** Δ_i / SE > 2. Agents that do not rise are counted and excluded from T½.
- **Per-agent half time T½,i^c:** least-squares fit of a_s = P_i + Δ_i (1 − e^{−c_s/τ}) over the agent's day-1 statements after t₀, one free parameter τ on a log grid (hours 0.005–50; calls 0.1–5,000). T½ = τ ln 2. A fit at the grid floor is "immediate", at the ceiling "not reached"; both enter rank-based statistics at the bound.
- **P1 slope s:** per kickoff, Theil–Sen slope of log T½,i^H on log r_i (agent bootstrap SE, 500 draws). Across kickoffs, a DerSimonian–Laird mean of s and a sign test. **Pooled companion** (exception (d), next to the per-kickoff values): log T½,i^H = α_p + s log r_i + b â_i^on + lab + ε (kickoff fixed effects, agent-clustered bootstrap).
- **P2 collapse ratio:** CR = var_i(log T½^C) / var_i(log T½^H) per kickoff (robust variance: MAD²). CR < 1: calls collapse the curves. Card level: median CR and the share of kickoffs with CR < 1. CR and s share one design (CR < 1 roughly when s < −½); they count once.
- **P3 within-agent clock gain:** per kickoff, a common-τ fit on each clock (one τ_c for all agents, each agent weighted 1/n_i). ΔSSE = (SSE_H − SSE_C)/(SSE_0 − min(SSE_H, SSE_C)), SSE_0 = a step at t₀ (F ≡ 1). It uses the within-agent irregularity of calls (pauses), not only the between-agent rate spread. ΔSSE > 0 favours calls.
- **P4 read-out test (R_L):** the same per-agent fits with time from the read-out call: T½^ro,H (hours) and its slope s^ro on log r_i. HH368's relaxation predicts s^ro ≈ −1; R_L predicts T½^ro at the grid floor (immediate) and s^ro ≈ 0.
- **â_i^on (on-task trait):** the agent's mean S_i (settled excess alignment) over its other eligible kickoffs (leave-kickoff-out), ≥ 2 kickoffs.

## Null / baseline
- **N0 slope 0 (R_W):** synthetic hour-clock worlds at the real statement and call times give the null distribution of s, CR and ΔSSE, including sampling artifacts (R_S).
- **N1 agent bootstrap** within kickoff for every per-kickoff CI; DL random-effects mean and sign test across kickoffs. Periods are never pooled into one fit except the named exception (d) companion.
- **N2 synthetic worlds** (axis F): W (hour clock), C (call clock from t₀), L (read-out jump), L+W (read-out gate, then hour relaxation), each at two time constants, at the real skeleton, with noise calibrated on decoy-direction projections (no k̂ statistic).

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R_W hour clock; R_L read-out jump; R_F on-task field; R_S sampling artifact.
**Locked holdout used for confirmation:** none yet. Planned: held-out kickoffs, and NE44 (2026-06-11, pause default 12 h → 5 min, a village-wide cadence step inside the held-out NE21+NE23 window) (`analysis/confirm.py`, frozen, not run).

*Scorecard plan (filled after round 1):* A from the mapping (ledger read-out, call clock); B from the time-rescaling audit (P3); C from s and CR against the synthetic hour-clock null; D from the collapse (an unfitted consequence of slope −1) and the NE38 out-of-sample prediction; E from NE38; F from the synthetic worlds; G from the ledger read-out times; H from R_L and R_F; I from regime transfer and the holdout.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Read-out call from the context ledger, call counts from `call_windows`, linear excess alignment (both models, style variant). The first statements after read-out likely restate the kickoff, which the mapping cannot separate from re-orientation. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Time-rescaling tested from the read-out origin: no clock preference (ΔSSE_ro CI contains 0). Overdamped single-exponential rise rejected in form: the day-1 path is a spike and a decay. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | The immediate share (0.74) is beyond every synthetic relaxation world (≤ 0.20) and above the read-out-jump world (0.42–0.47). |
| D unfitted predictions | unfitted statistics and the model's signature | 0 | The collapse (CR) is non-diagnostic and the NE38 out-of-sample prediction is untestable (both predictions at the floor). |
| E interventional | predicts the change across a natural experiment | 1 | NE38: a single-agent mid-day reassignment gives a resolved rise (0.2 h), unlike kickoffs; one agent. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 2 | 6 worlds × 3 amplitudes on the real skeleton before real data; the per-kickoff design's lack of power, CR's and the t₀-origin ΔSSE's bias under read-out gating were found and replaced (Amendment 1). |
| G ground truth | agrees with known structure | 1 | Read-out times agree with H08/H48 (median 75 s after t₀; coverage within minutes). |
| H comparative | beats the named rivals | 1 | R_L (read-out jump) fits better than HH368's relaxation; R_W vs the call clock is not separable at this resolution. |
| I transfer | holds in other same-mode periods, including the holdout | 1 | Immediate rises in regimes I, II and III (share 0.66–0.75 across configurations); holdout not run. |

## Prediction
*Written 2026-10-04 22:18 UTC, before running the analysis on real data.*

**What I had seen when writing this:** the round-1 cards of H40 (call clock in II–III, η ≈ 0; neither clock in regime I, η +0.51; G51 call rates 25–184 per hour; per-hour reply coupling ∝ call rate), H103 (active-work clock for remanence), H48 (coverage within 0.24 active h; settling τ ≈ 4.5 h), H75 (freeze within 0.5 active h), H97/H54 (day-1 overshoot; 0.24 → 0.11), H08 (read-out gating). Counts only for H127: eligible kickoffs and incumbents (H125/H103). No alignment, half-time or call-rate statistic computed.

**Primary predictions** (combined across kickoffs; per-kickoff values are descriptive):

| ID | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| **P1** slope (HH368) | DL mean s < 0 with 90% CI below 0, and the CI overlaps [−1.5, −0.5] ("near −1"), bge white32; same sign in gte | Kill: \|s\| < 0.25 with CI containing 0 (slope near 0) | 0.35 |
| **P2** collapse | median CR < 1 and CR < 1 in ≥ 2/3 of kickoffs (sign test p < 0.05) | Kill: median CR ≥ 1 (no improvement in calls) | 0.35 |
| **P3** within-agent time-rescaling | DL mean ΔSSE > 0 with 90% CI above 0 | ΔSSE ≤ 0 | 0.3 |
| **P4** relaxation beyond read-out (vs R_L) | from the read-out call, T½^ro is resolved (not at the grid floor) for ≥ half of rising agents and s^ro < 0 with 90% CI below 0 | T½^ro at the floor for most agents, or s^ro CI containing 0 | 0.2 |

**Secondary:**

| ID | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| S1 | Regime contrast (H40): s is more negative in regimes II–III than in regime I (Mann–Whitney on per-kickoff s, one-sided p < 0.1) | reversed or equal | 0.45 |
| S2 | R_F control: in the pooled model, s stays < 0 (CI below 0) with â_i^on and lab fixed effects, and with r_i^LPO in place of r_i | s CI contains 0 after controls | 0.5 (conditional on P1) |
| S3 | Both models and the style variant give the same sign of s | sign flips in ≥ 1 of 3 | 0.6 |
| S4 | The share of rising agents (Δ_i/SE > 2) is ≥ 0.5 of eligible agents (setup check: there is a rise to time) | < 0.3 | 0.75 |

**Native predictions** (each also in its folder README):

| ID | Unit | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| N1 | G51 (#51 kickoff 2026-07-06; ~21 agents with private roles; call rates spread ~7×) | Own-role half-alignment time (decoys = other agents' roles) falls with call rate: Theil–Sen s < 0 with 90% CI below 0, both models | s CI contains 0 | 0.4 |
| N2 | NE38 (Opus 5 reassigned 2026-07-29 16:51 UTC) | Out-of-sample: Opus 5's measured T½^H (own new role) is closer (in \|log ratio\|) to the call-clock prediction T½^C(regime III replication median) / r_Opus5 than to the hour-clock prediction (regime III median T½^H), both models | hour-clock prediction closer | 0.5 |

**Overall verdict rule:** **supported** if P1 and P2 hold; **failed** if either kill clause holds (slope near 0, or no collapse improvement in calls); **mixed** otherwise. P4 decides between HH368's per-call relaxation and the read-out-jump rival R_L and gets its own line: if P1–P2 hold but P4 fails, the call-clock law stands as read-out latency, not relaxation.

**Per-kickoff replication rule (templated):** supported if s < 0 with bootstrap 90% CI below 0 and CR < 1; failed if s ≥ 0; mixed otherwise; descriptive if fewer than 5 rising agents with a fitted T½.

**Multiplicity and power.** P1–P2 are one design (count once); P3 and P4 use different contrasts. The synthetic run states the size of P1–P3 under R_W and the power under C before the real run; if power at the real counts is below 0.8, a miss is "inconclusive".

**Amendment 1** (2026-10-04 22:58 UTC, after the synthetic runs, before any real-data statistic along a kickoff direction; noise from H125's decoy-direction calibration). `analysis/synthetic.py` on the real skeleton (27 kickoffs, real statement times, call times, read-out calls; 30 replicates for the card's original estimators, then 12 replicates × 6 worlds × 3 rise amplitudes Δ ∈ {0.1, 0.2, 0.4} for the amended ones; `synthetic/results_bge_white*.json`).
1. **The per-kickoff design has almost no power.** At Δ = 0.10 the card's P1 (DL meta of per-kickoff Theil–Sen slopes) passes in 17–23% of call-clock worlds (median slope −0.37 for a planted −1) and 0–7% of hour-clock worlds; P2 (CR) passes in 0–3%. Noise-free, the estimator recovers −0.87; the loss comes from statement noise (SD 0.09 per statement against Δ ≈ 0.1) during rises that last minutes to an hour, plus only a 2–3× call-rate spread inside a kickoff.
2. **Per-agent fit: day-1 amplitude free** (`AMP_FREE`; the fixed-Δ form stays behind the switch). T½ is the half time of the agent's own day-1 plateau; Δ (settled) still selects rising agents. Reason: the day-1 agent-day offset (SD ≈ 0.035) otherwise biases τ toward the grid floor or ceiling. The hour grid floor moves from 18 s to 0.36 s, so a step at the read-out call can be fitted on both clocks.
3. **P1 becomes the pooled within-kickoff slope** (exception (d): kickoff fixed effects, common slope, bootstrap over kickoffs), reported next to the per-kickoff meta. Rule unchanged (90% CI below 0 and overlapping [−1.5, −0.5]). Power: 0.17 (Δ 0.1), 0.33–0.42 (Δ 0.2), 0.67–0.92 (Δ 0.4); size 0–0.08 at Δ ≤ 0.2, up to 0.33 for fast hour-clock rises at Δ 0.4. **The kill clause "slope near 0" applies only if the observed median Δ of rising agents is ≥ 0.4**; below that a miss is "inconclusive".
4. **P2 (CR collapse) is demoted to descriptive.** It passes in 92% of read-out-jump worlds (R_L) at every amplitude and in at most 42% of call-clock worlds: the call clock captures the read-out step, so a collapse in calls does not distinguish per-call relaxation from read-out gating. HH368's second kill clause ("no improvement in the collapse") cannot be applied with this instrument and is not used.
5. **P3 changes origin.** ΔSSE from t₀ passes in 50–100% of R_L worlds (the step sits at call 1 but at an agent-specific hour). **P3 now uses clocks from the read-out call** (ΔSSE_ro, two-sided): size 0.00 under W, L and LW; power 0.25 (Δ 0.1), 0.58–0.92 (Δ 0.2), 0.92–1.00 (Δ 0.4). ΔSSE_ro significantly below 0 (hour clock) occurs in 42–100% of hour-clock worlds at Δ ≥ 0.2 and in 0% of call-clock worlds. It is the best-powered clock test here.
6. **P4** (read-out rival): the share of immediate fits from the read-out call is 0.42–0.47 under R_L and ≤ 0.20 elsewhere; power of the full P4 rule 0.25 (Δ 0.2) to 0.58–0.67 (Δ 0.4), size ≤ 0.17.
7. **Amended verdict rule:** **supported** if P1 (pooled) holds and ΔSSE_ro > 0 (90% CI above 0); **failed** if ΔSSE_ro < 0 (90% CI below 0: the hour clock fits better from the read-out call), or the pooled kill holds at median Δ ≥ 0.4; **inconclusive** if neither holds and the power at the observed Δ is below 0.8; **mixed** otherwise. Agents without a previous non-holdout day (#10, #16, #30, #35, #51) use P_i = 0 (flagged; checked by dropping them).

## Results by goal period
Replication rule (templated, as written before the run): supported if s < 0 with bootstrap 90% CI below 0 and CR < 1; failed if s ≥ 0; mixed otherwise; descriptive if fewer than 5 rising agents. Most "failed" rows have s = 0 because every half time sits at the grid floor (a tie).

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| NE34 (27 kickoffs) | replication (cross-kickoff) | inconclusive (slope); read-out jump favoured | 152 rising agents (bge); 74% reach the day-1 plateau within the read-out call; pooled slope +0.59 [−0.45, +1.75] (gte +0.42 [−0.96, +1.45]); ΔSSE_ro −0.0009 [−0.0019, +0.0001] |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | descriptive | rising 3/4; immediate from read-out 0.33; s – |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | descriptive | rising 1/4; immediate from read-out 1.00; s – |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | descriptive | rising 3/4; immediate from read-out 0.00; s – |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | descriptive | rising 3/4; immediate from read-out 1.00; s – |
| [G10](goalperiod-subhypotheses/G10/README.md) | replication | failed | rising 7/7; immediate from read-out 0.43; s +2.72 |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | descriptive | rising 0/7; immediate from read-out –; s – |
| [G12](goalperiod-subhypotheses/G12/README.md) | replication | failed | rising 7/7; immediate from read-out 0.71; s +0.00 |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | descriptive | rising 3/6; immediate from read-out 1.00; s – |
| [G16](goalperiod-subhypotheses/G16/README.md) | replication | descriptive | rising 4/7; immediate from read-out 1.00; s +0.00 |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | failed | rising 5/7; immediate from read-out 1.00; s +0.00 |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | descriptive | rising 3/7; immediate from read-out 1.00; s – |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | descriptive | rising 2/7; immediate from read-out 1.00; s – |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | descriptive | rising 1/8; immediate from read-out 0.00; s – |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | descriptive | rising 3/8; immediate from read-out 0.67; s – |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | failed | rising 8/10; immediate from read-out 0.62; s -0.00 |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | failed | rising 10/10; immediate from read-out 0.70; s +0.00 |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication | failed | rising 8/10; immediate from read-out 1.00; s -0.00 |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | failed | rising 10/10; immediate from read-out 0.80; s +0.00 |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | failed | rising 11/11; immediate from read-out 1.00; s -0.00 |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | descriptive | rising 1/11; immediate from read-out 1.00; s – |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | failed | rising 7/12; immediate from read-out 0.71; s +0.00 |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | descriptive | rising 4/12; immediate from read-out 1.00; s -0.00 |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | failed | rising 12/14; immediate from read-out 0.83; s -0.00 |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | failed | rising 11/15; immediate from read-out 0.55; s +0.00 |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | descriptive | rising 3/15; immediate from read-out 0.67; s – |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | failed | rising 14/15; immediate from read-out 0.57; s +0.00 |
| [G51](goalperiod-subhypotheses/G51/README.md) | native (+ replication) | failed | rising 8/21; immediate from read-out 0.75; s +0.00; N1 own roles: 18/21 rising, all half times at the floor (failed) |
| [NE38](goalperiod-subhypotheses/NE38/README.md) | native | descriptive | Opus 5 T½ 0.20 / 0.24 h (16–19 calls), resolved; both clock predictions at the floor |

## Results
**Headline.** HH368 pictures content trailing a moved goal, catching up at a rate set by each agent's calls. The data show no trailing to time. At a kickoff, an agent's alignment with the new goal is already at or above its day-1 plateau in the first statement after its read-out call (74% of 152 rising agents). It then decays from about 2.4× the plateau to the plateau over roughly 64 calls (about an hour). With the rise inside one call, there is no per-agent half time for the call rate to set, and the slope test cannot work (pooled slope +0.59 [−0.45, +1.75]).

**Outcome vs prediction** (after Amendment 1)

| Prediction | Credence | Outcome | Verdict |
| --- | --- | --- | --- |
| P1 pooled slope < 0, near −1 | 0.35 | bge +0.59 [−0.45, +1.75]; gte +0.42 [−0.96, +1.45]; per-kickoff meta +0.11 [−0.99, +1.22] (k 10) | not supported; kill not applicable (median Δ 0.15 / 0.19 < 0.4; power ≈ 0.35) → inconclusive |
| P2 collapse CR < 1 (descriptive after Amendment 1) | 0.35 | median CR 0.65 / 0.19; ties at the floor | non-diagnostic |
| P3 ΔSSE_ro (read-out origin) | 0.3 | −0.0009 [−0.0019, +0.0001] (bge); −0.0000 [−0.0005, +0.0004] (gte) | not supported (no clock preference) |
| P4 relaxation beyond read-out | 0.2 | immediate share 0.74 / 0.75 (≥ 0.5); s^ro ≈ 0 | failed: read-out jump (R_L) |
| S1 slope more negative in II–III than I | 0.45 | pooled I +0.34, II–III +1.00 (bge); MW on per-kickoff s p 0.25 | not supported |
| S2 slope survives â_i^on + lab, r^LPO | 0.5 (cond.) | +0.37 [−1.20, +1.74]; r^LPO +0.13 [−0.95, +1.07] | moot (no slope) |
| S3 same sign across models and style | 0.6 | pooled s > 0 in all 4 configurations | sign agrees (positive, CIs contain 0) |
| S4 rising share ≥ 0.5 | 0.75 | 0.60 / 0.57 (median Δ 0.15 / 0.19) | supported |
| N1 G51 slope < 0 | 0.4 | 18/21 rising; all half times at the floor | failed |
| N2 NE38 call-clock prediction closer | 0.5 | Opus 5 T½ 0.20 / 0.24 h; both predictions at the floor | uninformative (descriptive) |
| **Overall (amended rule)** | | P1 not supported, P3 not significant, kill not applicable; P4: R_L | **inconclusive on the slope; HH368's relaxation picture not supported** |

**Synthesis**
1. **The kickoff field is delivered in one call.** The median read-out call comes 75 s after t₀, and the first statement that follows already carries the new alignment. This is H08's read-out gating applied to content: the field acts at the receiving call.
2. **What relaxes is the spike, not the agent.** After the jump, alignment falls back toward a plateau over tens of calls and about an hour (post hoc rise curve, `NE34/rise_curve.json`). Slow and fast agents (split at the median call rate) follow the same path in hours within the CIs, and in calls the slow half is not slower. This decay is H125's day-1 overshoot seen at call resolution, and its clock is the round-2 question.
3. **A single-agent step is different.** Opus 5's reassignment by a mid-day human message (NE38) gives a resolved rise with T½ ≈ 0.2 h (16–19 of its calls). A kickoff to everyone does not. Candidate reasons: the kickoff is in the prompt (NE08/NE13) and every agent reads it at once; the reassignment arrives in a busy context.
4. **Instrument lessons.** In the synthetic, a collapse in calls (CR < 1) and a t₀-origin clock comparison both favour calls under pure read-out gating (92% and 50–100% of worlds), because the read-out sits at call 1 but at an agent-specific hour. Clock tests for message-delivered fields must start at the read-out call.

**Caveats.** The first statements after read-out likely restate the kickoff, so part of the spike is copying the text, not re-orientation. Half times below the 0.36-s grid floor are ties, which make per-kickoff slopes 0 and per-period verdicts "failed" by the templated rule. Five kickoffs lack a previous non-holdout day (P_i = 0 fallback). The pooled slope assumes one slope across kickoffs (exception (d)); per-kickoff values are reported beside it.

**Code.** `scheme/build.py` (reads H125's statement table); `analysis/h127lib.py`, `synthetic.py`, `run.py`, `natives.py`, `rise_curve.py` (post hoc), `figures.py`, `period_folders.py`, `write_rows.py`, `confirm.py` (not run). **Data:** `data/processed/H127-content-trails-goal-call-clock/` (≈ 0.5 MB). **Figures:** `figures/summary_obs.pdf`, `figures/synthetic_compact.pdf`.

**Per-period estimates:** rows written with `write_estimates` (`halftime_callrate_slope_s`, `readout_immediate_share`, `clock_gain_dsse_readout`; natives `ne38_opus5_halftime_h`, `g51_own_role_readout_immediate_share`).

**Claim that stands:** At a goal kickoff an agent's excess alignment with the new goal jumps within its read-out call (74% of 152 rising agents over 27 kickoffs, both models; synthetic relaxation worlds ≤ 0.20) and then decays from about 2.4× to 1× its day-1 plateau over about 64 calls, so no per-agent catch-up time exists for the call rate to set. Excluded: the call-rate slope (inconclusive, power ≈ 0.35), the CR collapse (non-diagnostic), the decay's clock (post hoc, untested).

## Confirmatory test (written 2026-10-04 after exploration; NOT run)
`analysis/confirm.py` refuses to run without `--confirm --i-understand-this-uses-the-locked-holdout`, a clean git state for its files and a holdout-ledger check. `--dry-run` on the stand-ins #11–#13, #38–#42 reproduces the exploratory counts (54 rising agents; C1 0.74 pass, C2 1.53 pass, C3 pass). Frozen predictions on the held-out kickoffs with ≥ 5 days (from #1, #9, #14, #15, #28, #29, #34, #43, #45–#50):
- **C1** read-out jump: immediate share ≥ 0.5 (credence 0.8).
- **C2** spike then decay: mean normalized alignment over calls 1–3 after read-out ≥ 1.5× the late plateau (credence 0.7).
- **C3** no call-clock law: pooled slope CI contains 0 or lies above −0.5 (credence 0.75).
- Planned separately: NE44 (pause default 12 h → 5 min, held-out window) as a cadence step for the spike's decay, after a round-2 card section. Reuse: H125, H97, H54 plan the same held-out kickoffs; disclose in all cards and LOG.md.

## Round 2 redirects (2026-10-04)
- **H127-R1. The clock of the spike's decay.** Fit the decay from each agent's read-out call on calls vs hours (ΔSSE from the read-out origin, slow vs fast halves). The spike is ≈ 2.4× the plateau, so this test has the power the rise test lacked.
- **H127-R2. Resolved rises.** Collect the other single-agent role changes in #51 (DQ6: agents 41–45, 08-31 → 09-04, non-holdout part) and measure T½ against call rate, as NE38 did.
- **H127-R3. Restatement.** Remove statements that copy the kickoff text and re-measure the immediate share.

## Notes
- 2026-10-04 23:20 UTC: round 1 done (synthetic → Amendment 1 → replication on 27 kickoffs × 4 configurations → natives → estimates → confirm.py frozen and dry-run). Post hoc (labelled): the rise curve (`rise_curve.py`).
- 2026-10-04 22:18 UTC: card, observables and predictions written from HH368 (approved by Vivian in the dashboard), before any real-data statistic along a kickoff direction.
- The scheme reads H125's processed statement table (data, read-only); no code is imported across hypothesis folders. Candidate for `infra/shared/`: a per-statement kickoff-projection table on the active-hour clock (H103, H125, H127 and H96 each build a variant).
- Proposed DEFINITIONS.md variants (H127): **half-alignment time T½^c** = τ_c ln 2 from a one-parameter fit of a_s = P_i + Δ_i(1 − e^{−c/τ_c}) on the agent's day-1 statements after t₀, clock c ∈ {active hours, own calls}, from t₀ or from the read-out call (T½^ro); **call rate r_i** = the agent's calls per active hour on day 1 after t₀ (variant r_i^LPO: other periods of the regime); **collapse ratio CR** = MAD²(log T½^C)/MAD²(log T½^H) across a kickoff's agents; **within-agent clock gain ΔSSE** = (SSE_H − SSE_C)/(SSE_0 − min SSE) for a common-τ fit.
