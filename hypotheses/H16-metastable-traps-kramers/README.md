# H16: Agents get stuck in metastable traps and escape by Kramers kinetics; nudges lower the barrier

**Status:** exploratory round 1 done (2026-10-03; 11 non-holdout goal periods). **The trap picture holds and the Kramers picture does not.**
- **Aging, not memoryless escape:** wherever power suffices (G51, G38, G37), the escape hazard falls with time in the trap. The same holds per timer gate (TS2r) and in error loops.
- **Kicks are saturating, not exponential:** a directed message during a pause raises the odds of acting at the gate ×1.5–2.9.
- **The Boltzmann barrier is not identifiable at 1-min resolution.**
- **No collective bistability**, as mean field predicts (βJ₀ < 1).

**Round 1b (2026-10-04, improved data):** on real failures (not stderr) error loops age only in #51; Jev blocked and repeated-action spells age in #51, #27 (and #38 for loops) but are timer-like in short periods; kick results survive the leading-@ target fix; with the nudger off (NE43) aging is unchanged, so it is intrinsic.

Confirmatory script for #32/#45 is written and dry-run on stand-ins; **not run**.
**Fields:** stat mech, dynamics, thermodynamics
**Origin:** HH53 + HH86 (shortlist 2, item 10) (`../hypohypotheses/HYPOHYPOTHESES.md`; `../promotion-shortlist.md`); HH47 for the landscape.
**Definitions used:** Agent; Regime; Action; Population N(t) (active-population variant: agents with ≥ 1 active row that day); Interaction (broadcast) for undirected kicks and Interaction (addressed) for directed kicks; Driving / external field (human messages; nudges). New operational terms (trap states TS1–TS4, reaction coordinate x, kick classes) are defined below; proposed as named variants for `physics-models/DEFINITIONS.md` in the round-1 report (not edited here).

## Standards (2026-10-04)
**Question served:** Q6 (trap kinetics) and Q5 (what gets a stuck agent out).

| Impostor | Relevant? | How it was handled | Status |
| --- | --- | --- | --- |
| Scheduler field | partly | Agent fixed effects against frailty; day-swap kick-timeline null (Null / baseline). The swarm block (d) was not re-run on fixed or trimmed data. | partly |
| Exogenous field (kickoff/goal/operator) | yes | Past-only kick look-backs and the day-swap null (Round 1b, Lever controls); NE43 shows aging persists with the nudger off. | removed |
| Shared model priors | no | Agent fixed effects absorb per-agent frailty; no family claim. | n/a |
| Contemporaneous convergence | partly | Kicks are counted by posting time in 2- and 15-min look-backs, not by ledger receipt. Close with the in-flight placebo at the gate call (§1). | open |

**Inputs:** round 1b uses `turn_outcomes.failed`, `error_class`, leading-@ targets and Jev v3.1. Still old: kick exposure is by time window, not the context ledger; the landscape (b) and swarm (d) blocks were not re-run.

**Two layers:** 11 replication folders. Natives: 3 in the card (NE43, NE44, #27), all mixed; the G27 folder is tagged exploratory, so 2 carry `**Role:** native`.

**Confirm script:** `confirm.py` (#32, #45), written and dry-run, not run. Re-freeze: yes; TS3 counts `actions.error` and N_tgt counts every named agent. #32 and #45 collide with H05's and H02/H04's executed runs (holdout item 2).

## Question
Idle loops, repeated-error debugging loops and theory spirals look like local free-energy minima. Do dwell times in these trap states follow Kramers escape, with the rate set by a barrier from Boltzmann inversion of occupancies? Do kicks (nudges, @-mentions, human messages) lower the barrier, with escape hazard rising exponentially in kick strength? At swarm level, does mean-field theory (βJ₀ < 1, as measured) correctly predict *no* collective bistability, so that traps are individual? Practical payoff: predicting when agents get stuck and what gets them out.

## Model
**From:** `physics-models/02-nonequilibrium-ising` and `01-inverse-ising` (mean-field double well f(m) = −J₀m²/2 − hm − T·s(m); bistable only when βJ₀ > 1), with Kramers escape along a reaction coordinate, and `11-vector-spins` for content-level spirals (not run in round 1).

**H16 variant (single agent).** Each agent's activity is an overdamped coordinate in a double well, U(x) with an idle well and an active well, at effective temperature T_eff:
- **Kramers:** escape from the idle well is memoryless after intra-well relaxation, with rate k = ν exp(−ΔU/T_eff). The Boltzmann inversion G(x) = −ln P(x) of the occupancy gives ΔG = ΔU/T_eff directly (in units of T_eff).
- **Kicks** add a transient force f, which lowers the barrier by about f, so ln k rises by about f/T_eff per concurrent kick. The hazard is then *exponential in dose* (ln HR_n = n·b).
- **Rivals:**
  - **R1 aging / trap deepening:** the hazard falls with time in the trap (Bouchaud-type trap models; self-reinforcing waiting).
  - **R2 timer gate:** escape happens at self-scheduled expiry times (H09 regime III), so the real-time hazard is peaked and the per-gate escape probability is the object.
  - **R3 independent triggers:** each kick independently triggers escape, so the hazard is *additive* in dose (HR_n = 1 + c n). The saturating variant is HR_n = 1 + c(1 − e^{−n/n₀}).
  - **R4 collective bistability:** βJ₀ > 1 gives a swarm-level double well.

**Swarm level (HH86).** Curie–Weiss with a time-varying field: the swarm is bistable only if βJ₀(1 − m²) > 1. With βJ₀ < 1, m(t) is unimodal around the field-driven mean, and any bimodality must come from the field (the schedule) or from common outages ("stalls"), not from coupling.

## Definitions (operational; all from shared tables)
- **Active row:** any agent event in `events_core` except WAIT and PAUSE, or any computer-use turn in `actions` except the `pause` tool call. The `pause` turn mirrors the PAUSE event (H09). This is the same rule as H09's `idle_runs`.
- **Active minute** a_i(m) = 1 if agent i has ≥ 1 active row in minute m of the day's window (`calendar.win_start`).
  - Present agents: those with ≥ 1 active row that day.
  - The Claude Code agent is excluded.
- **TS1 inactive spell (strict):** a gap ≥ 180 s between consecutive active rows of one agent, within one day's window.
  - It starts at the last active row and ends at the next one (escape), or at the window end (right-censored).
  - The gap before the agent's first active row of the day is the cold start; it is excluded.
- **TS1r (robust, core-set):** TS1 computed after dropping *isolated* active rows (no other active row within ±120 s). An escape therefore needs a burst of activity; a single sporadic action inside a trap counts as a failed escape attempt (a recrossing).
- **TS2 pause-chain gate (regime III):**
  - *Chain:* a maximal run of PAUSE events with no active row in between.
  - *Gate k:* the expiry decision after the k-th PAUSE. It is a re-pause if the next PAUSE comes before any active row; otherwise an escape. An "early" escape is an active row more than 30 s before the declared expiry.
  - *Censored:* the window ends first.
  - *Covariates:* declared duration, and kicks received during that pause.
- **TS3 error loop:** a run of consecutive `actions` turns with `error = true`, per agent-day.
  - Per-turn escape means the next turn has no error.
  - A *trap* is a run reaching 3 turns.
- **TS4 identical-command loop:** a run of consecutive bash turns with an identical command, matched exactly through `artifact_commands_text.cmd` on (t, agent).
  - The text is hashed in memory and never stored. Bash turns with no recorded command break a run.
  - At most 10 min between turns.
  - Rows start at the first repeat; a *trap* is a run reaching 3 turns.
- **Reaction coordinate** x_i(m) = EWMA of a_i(m) with τ = 5 min (robustness: 3 and 10 min); the first 15 min of each day are dropped (burn-in).
  - Landscape: G(x) = −ln P(x) on 20 bins of [0, 1], smoothed over 3 bins.
  - *Double well:* a low-x minimum (x ≤ 0.5) and a second minimum ≥ 0.2 away, with the barrier ≥ 0.3 above both and ≥ 2% of the mass near each.
  - ΔG = G(x‡) − G(x_a).
  - Passage: from the trap core (x ≤ the upper edge of the trap-minimum bin) to just past the barrier top.
- **Kick classes:** chat messages that reach the agent (`exposure`), classified with `chat_mentions_clean.mentions_roster` (the polluted `chat_core.mentions` is never used).
  - A_und / A_men: an agent speaker, not mentioning / mentioning the agent.
  - H_und / H_men: the same for a human speaker.
  - N_tgt: an automated message that names the agent (a nudge to it).
  - N_by: an automated message that names others.
  - An automated message with no valid mention is the daily pause/resume bookend; it is dropped.
  - *Directed* = A_men + H_men + N_tgt. *Undirected* = A_und + H_und.
  - *Dose* = the number of kicks in the 2 min before the hazard bin (fast window). The slow window for N_tgt is 15 min (H04: a delayed response that plateaus around 15 min).

## Data scheme (`scheme/`)
- **Inputs:** `scheme/build.py` reads `events_core`, `actions`, `artifact_commands_text` (cmd hashed only), `chat_core`, `chat_mentions_clean`, `exposure`, `calendar` and `roster`. Library: `analysis/h16lib.py`.
- **Output:** `data/processed/H16-metastable-traps-kramers/G<NN>/`, holding `ts1`, `ts1r`, `ts2`, `ts3`, `ts4`, `minutes`, `kicks` (parquet, no text) and `_provenance.json`.
- **Synthetic outputs:** `synthetic/`.
- **Confirmatory outputs** (when run): `confirm/`.
- H09's `idle_runs` is the reference for TS1/TS2 semantics. H16 rebuilds its own spells so that the robust variant, the gate structure and clean mentions are all available.

## Candidate goal periods (unit of analysis: one goal period)
| Period | Window used | Regime | Notes |
| --- | --- | --- | --- |
| G27 | 01-12 → 01-23 (10 d) | I | before the nudger; regime-I comparison |
| G30 | 02-09 → 02-13 (5 d) | I | NE10: first nudges on 02-13 |
| G31 | 02-16 → 02-19 (4 d) | I | 02-20 excluded (NE11, 100-turn session cap) |
| G37 | 03-30 → 04-01 (3 d) | III | first regime-III goal; low power |
| G38 | 04-02 → 04-24 (17 d) | III | NE17 (04-14) split as a sensitivity check |
| G39–G42 | 5 d each | III | |
| G44 | 05-26 → 05-29 (4 d) | III | |
| G51 | 07-06 → 09-02 (non-holdout, pre-NE33) | III | 8 h days, up to 32 agents; most power |
| 🔒 G32, G45 | | I, III | loop-heavy; confirmation only (`analysis/confirm.py`, not run) |

#43 and #46–#50 are held out and not used. Regime II is skipped (9 non-holdout days, mixed scaffold).

## Links to other hypotheses
- **H09:** idle-escape observables (E6); H16's TS1/TS2 extend them with robust spells, gates and clean mentions.
- **H04:** the kick mapping and the delayed nudge response.
- **H02 / H05:** βJ₀ and joint silences.
- **Ideas:** HH53, HH86, HH47.

## Observables
**(a) Dwell law** (per period; trap types TS1r [primary], TS1, TS2, TS3, TS4).
- **TS1r/TS1:**
  - Discrete-time hazard per 30-s bin with a complementary log-log link (grouped proportional hazards).
  - Agent fixed effects (frailty) and a slope β on ln(elapsed). β = 0 is memoryless (exponential dwell, Kramers); β < 0 is aging; β > 0 is timer-like.
  - **Primary window: elapsed ≥ 10 min** (the trap regime). [3, 10) min is reported too.
  - 95% CI from a day-block bootstrap (resampling days).
  - Verdict band: |β| ≤ 0.3 is memoryless.
  - Also reported: KM median, censoring-aware exponential MLE vs. the naive completed-spell mean, and spells with vs. without a declared idle event.
- **TS2:** logit of P(escape at gate) on ln k, controlling for ln(declared duration), with agent FE and a day bootstrap. Trap deepening: the next declared duration vs. the current one in re-pauses.
- **TS3/TS4:** the per-turn break hazard (cloglog) on ln k for k ≥ 3, with agent FE.
- **(a2):** the TS1 deep-window slope with and without the kick covariates (does conditioning on kicks remove aging?).

**(b) Landscape and Kramers closure** (per agent with ≥ 1500 min after burn-in, plus period-pooled):
- **b0:** the fraction of agents with a double well in G(x).
- **b1:** Arrhenius across agents: the slope of ln k_TS1r,deep (deep-window escape rate) on ΔG.
- **b2:** the 2D Markov-embedding closure, i.e. a Markov chain on (x bin, current-minute activity a). Statistic: median |ln(k_obs/k_MSM2)| over agents with ≥ 15 passages.
- **b3:** the 1D Kramers closure: mean first-passage time from the occupancy plus the Kramers–Moyal diffusion D(x), and the saddle-point Kramers formula.
- **T_eff ≡ D(x) in the trap well:** the KM second coefficient, estimated independently of the occupancy. With a binary readout it measures readout noise, not a temperature (see F).
- **b4:** across periods, the period-pooled ΔG vs. the period's deep escape rate.
- Robustness: τ = 3 and 10 min.

**(c) Kicks** (TS1 strict primary; TS1r secondary; TS2 gates; TS3/TS4 turns):
- Per-class ln HR for "any kick of class c in the prior 2 min", with agent FE and ln elapsed.
- Directed and undirected dose (0, 1, 2, 3+) and their dose laws, compared by minimum distance on the dose-specific ln HRs:
  - Kramers: ln HR_n = b n;
  - additive: HR_n = 1 + c n;
  - saturating: 2 parameters.
  - A dose law is scored only if powered: ≥ 30 escapes at dose ≥ 2, and ≥ 5 escapes per dose level used.
- The slow 15-min window for N_tgt.

**(d) Swarm** (per period):
- m(t) = fraction of present agents active per minute, over minutes 15 → end − 10.
- **Null:** agent-wise day swap with ±15 min jitter. This keeps each agent's schedule profile and autocorrelation and destroys within-day cross-agent timing.
- **VR** = Σ(K − E_null K)² / Σ Var_null K, bias-corrected by the median VR of the null (the leave-own-day-out bias).
- **βJ₀** = (1 − 1/VR)/⟨1 − m_i²⟩.
- **Bimodality:** valley depth of the smoothed histogram [primary], number of modes, and the bimodality coefficient [unreliable in synthetic data; reported only]. Each is compared with the null.
- **Branch memory:** residual ACF at 30 min vs. the null.
- Everything is reported with and without **joint-silence minutes** (K = 0; possible platform stalls).

## Null / baseline
1. **Memoryless null for (a):** constant hazard within agent (β = 0, Kramers itself). It is the null that aging (R1) or timers (R2) must beat, *after* agent frailty. Pooled slopes without FE are reported but never interpreted: synthetic agent frailty fakes aging of −0.25 to −0.33.
2. **Kick nulls for (c):** the day-swap kick timeline, i.e. each agent-day's kicks come from the same agent on another day of the same period, at the same window offset (40 draws). This keeps kick density and schedule and destroys within-day alignment. Plus HR = 1.
3. **Dose-law rivals for (c):** Kramers (exponential), additive (independent triggers) and saturating.
4. **Swarm null for (d):** the jittered day swap (independent agents with their own schedule and autocorrelation) and Curie–Weiss with the fitted βJ₀ < 1 (unimodal).
5. **(b) nulls:** the x-only Markov chain and the 1D diffusion closure. These are the "landscape-only" predictors, and both fail even on true Kramers agents (F). The 2D Markov embedding is the baseline for "memoryless given the coarse state".

## Synthetic validation (axis F; done 2026-10-03, before any real-data run)
`analysis/synthetic.py` runs the same estimators (h16lib) on simulated data. Results: `data/processed/H16-metastable-traps-kramers/synthetic/synthetic_results.json`; figure: `figures/synthetic_validation.pdf`.

**Simulated data.** Overdamped Langevin agents in a double well U = (x²−1)² + cx, observed only through event times:
- Poisson readout of 3/min in the active well (or a sparse 0.8/min) and 0.01/min in the idle well;
- 4 h days with a cold start in the active well;
- 12 agents × 20 days per scenario;
- kicks as force pulses or as triggers.

The gate model and a Glauber swarm are simulated too.

| Check | Result | Consequence for the design |
| --- | --- | --- |
| Dwell slope, exponential truth | TS1r, agent FE, ≥ 10 min: **+0.05 ± 0.07** (truth +0.02) | estimator unbiased |
| Deepening trap (γ = 1, 2) | **−0.58 ± 0.08 / −1.08 ± 0.17** (truth −0.54 / −1.18) | aging is recovered |
| Same with TS1 strict | −0.16 / −0.13 | sporadic in-trap actions wash out aging → **TS1r primary for (a)** |
| Agent frailty, pooled (no FE) | −0.25 (spurious aging); agent FE −0.07 | **agent FE required**; pooled never interpreted |
| Agent-day FE | +0.24 to +0.34 bias (incidental parameters) | not used |
| Sparse readout (silences inside the active well) | ≥ 10 min: −0.19 ± 0.06 (truth +0.05); [3, 10) min: −1.06 | **primary window ≥ 10 min; band \|β\| ≤ 0.3** |
| Gate model, frailty, true θ_age = 0 / −0.5 | pooled −0.33 / −0.77; agent FE **−0.03 / −0.47**; mention effect 0.51 (truth 0.5) | agent FE on gates |
| Day-boundary censoring (TS1r) | naive completed mean is biased once the mean dwell is ≳ 0.4 × day: 58 vs. 97, 70 vs. 264 min. Censoring-aware exponential MLE: 98 vs. 97, 244 vs. 264; it fails at a 717-min mean (305; 69% censored) | use censoring-aware estimators; **dwell scales beyond ~1 day length are not identifiable** (cold starts) |
| Landscape: double-well detection | 94% of true double wells; 0/6 false positives on single wells | b0 is usable |
| Boltzmann ΔG vs. latent barrier | slope 0.92, r = 0.72 | tracks it, but the location of the apparent barrier (x ≈ 0.125) is set by the EWMA step, and its height by deep-idle time per idle entry (found in round 1). **Not a barrier measurement** |
| **1D Kramers closure** (occupancy + KM diffusion) | median \|ln(obs/pred)\| = **0.86**; saddle formula r = 0.14 | **fails on true Kramers agents.** The barrier region is crossed in seconds and is unpopulated at 1-min sampling, and x alone is not Markov. b3 is reported but **not diagnostic** |
| x-only Markov chain | 0.80 | not diagnostic |
| 2D Markov embedding (x, a) | median \|ln ratio\| 0.09, slope 0.97 | *Corrected after round 1:* this agreement is **tautological**. From the trap core, one active minute (α ≈ 0.18) jumps past the apparent barrier at x ≈ 0.125, so passage is a single step that any Markov chain fitted to the same minutes reproduces. **b2 is not diagnostic** |
| Arrhenius, ln k_TS1r,deep on ΔG | slope **−0.62** (r = −0.80); ln k_TS1r,deep vs. latent rate: slope 0.78, r = 0.94 | b1 calibration for a true Kramers population |
| Dose law, high kick rates | barrier pulses → Kramers chosen (2/2 bin widths); triggers → additive (2/2). Per-kick ln HR attenuated ~50% (0.38 vs. 0.875) by timing | the test discriminates when powered |
| Dose law, village kick rates | ≤ 5 escapes at dose 3+ → underpowered or arbitrary | **powered-only rule** (≥ 30 escapes at dose ≥ 2) |
| Swarm: βJ₀ recovery | 0.08 / 0.31 / 0.58 / 1.26 for truth 0 / 0.3 / 0.6 / 1.3 (4 h, N = 15, 5 d); 0.04 / 0.24 / 0.49 / 1.44 (8 h, N = 25, 20 d) | usable for βJ₀ ≲ 1.3 |
| Swarm: bimodality (valley) | p ≤ 0.007 at βJ₀ ≥ 1.3; p = 1.0 at ≤ 0.6 (0/6 false positives). The BC statistic has false positives | valley is primary |
| Common stalls (βJ₀ = 0, 4% stall minutes) | valley p = 0.007 (false positive) → p = 1.0 with stall minutes excluded | stall exclusion pre-registered |

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness". Filled in after round 1 (below).
**Rival models:** R1 aging / trap deepening; R2 timer gate; R3 independent-trigger kicks (additive or saturating); R4 collective bistability (βJ₀ > 1).
**Locked holdout used for confirmation:** none. #32 and #45 are planned (`analysis/confirm.py`, written, dry-run on stand-ins, not run).
**Scored after round 1** (2026-10-03). Faithfulness of the *Kramers* model is low: its core signatures failed. The mean-field "no collective bistability" part holds.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Trap states, the coordinate and kick classes are defined from fields, with assumptions listed (clean mentions; pause-mirror rule; bookends dropped). Not invariant across regimes: TS2 exists only in III, and TS1 mixes silent stalls with pauses differently in I and III. The EWMA coordinate turned out to manufacture an apparent barrier |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Memorylessness, the Kramers order-0 assumption, was tested directly and fails (aging). NE17 split in G38: same sign on both sides. Within-period stationarity is otherwise untested; no update-order audit |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Kick effects beat the day-swap null in some periods: undirected in 5/8 regime-III periods; directed at gates 5/7. Aging beats the memoryless null within agent where powered. The *Kramers* model itself loses to these nulls and rivals. No held-out-day prediction |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | Mean-field forward prediction holds: βJ₀ < 1 → unimodal swarm activity in 10/11 periods (11/11 with the minimum-mass rule). The Kramers signatures (memoryless dwell; exponential dose law) are absent |
| E interventional | predicts the change across a natural experiment | 1 | *Round 1b (2026-10-04; was 0):* NE43 tested: aging unchanged with the nudger off, as predicted; the predicted drop in gate escape failed, and the NE44 interaction failed as operationalized (the H35 pattern holds in probabilities). Round 1: no NE tested; NE17 was only a stability check |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | (a), the TS2 gate model and (d) are recovered on synthetic data. The dose law is identifiable only at high kick rates. **(b) is not identifiable** (1D closure fails; MSM closure tautological; barrier location is an EWMA artifact). τ = 3/10 min gives the same landscapes. Outage censoring and alternative nulls (A3–A5) do not change (a) or (d) |
| G ground truth | agrees with known structure | 1 | Regime-III timer gates respond to directed messages (H09's mention effect at the gate, reproduced and quantified per dose). H09's regime-I message triggering does *not* extend to silences ≥ 3 min |
| H comparative | beats the named rivals | 0 | Kramers loses to R1 (aging) in the dwell law and to R3 (saturating/additive) in the dose law (14/16 powered cells). R4 (collective bistability) is rejected in its favour only on the mean-field part |
| I transfer | holds in other same-mode periods, including the holdout | 1 | The direction (aging; gate kicks) is consistent across regime-III periods (6/8 TS1r point estimates negative; 6/7 TS2r). Holdout not used |

## Prediction
*Written 2026-10-03, after the synthetic validation and before any H16 statistic was computed on real data.*

**What had been seen first:**
- H09 E1/E6, H04, H02 and the LOG entries (βJ₀ 0.06–0.4; joint silences; message-triggered vs. timer-gated idling; delayed nudge response).
- Structural checks only:
  - row counts and column coverage;
  - action-type counts and error-flag rates by regime: errors on I 4.1%, II 10.8%, III 6.4% of turns; 14% of bash turns;
  - the command sidecar's exact join to `actions` (700k bash turns);
  - `activity_bins` state fractions by regime: III is 50% silent, 11% idle, 36% act, 3% talk; I is 42 / 1 / 44 / 12;
  - kick counts per period by kind; agent and agent-minute counts per period;
  - the alignment of `chat_mentions_clean`.

No H16 dwell, hazard, kick-effect, landscape or swarm statistic had been computed on real data.

**Decision rules apply per period.** A card-level claim needs the stated count of periods. With 11 periods and ~15 statistics each, single-period hits are not evidence: about one in twenty is expected by chance per statistic. All statistics are reported.

**(a) Dwell law: Kramers memorylessness is predicted to FAIL for most trap types (aging wins).**
- **P-a1 (TS1r, regime III):** the deep-window slope β < −0.3 with CI below −0.3 (aging) in ≥ 5 of 8 regime-III periods. Reason: long pause chains and silent stalls, plus agents "waiting for others or for the day to end".
- **P-a2 (TS1r, regime I):** aging (β < −0.3) in ≥ 2 of 3 regime-I periods. Reason: escape is message-triggered, and messages are bursty (Hawkes n ≈ 0.6).
- **P-a3 (a2, regime I):** adding the kick covariates moves the TS1 deep slope toward 0 (|β_with| < |β_without|) in ≥ 2 of 3 regime-I periods. That would make it "driven Kramers": memoryless given the kick field.
- **P-a4 (TS2):** per-gate escape probability falls with gate index, after declared duration and agent FE: β_lnk < 0 with CI excluding 0 in ≥ 5 of 8 regime-III periods. Re-pauses keep or lengthen the declared duration: the median log ratio of next to current ≥ 0 in ≥ 5 of 8.
- **P-a5 (TS3 error loops):** aging (β < −0.3) in the majority of periods with ≥ 15 deep escapes.
- **P-a6 (TS4 command loops):** aging (β < −0.3) in the majority of periods with ≥ 15 deep escapes.
- **What would count for Kramers:** |β| ≤ 0.3 with CI inside the band, in the majority of periods for a trap type.

**(b) Landscape.**
- **P-b0:** individual double wells. ≥ 50% of agent cells show a double well in G(x), in ≥ 8 of 11 periods (idle and active basins: HH53's "local minima").
- **P-b1:** Arrhenius across agents within a period (periods with ≥ 6 eligible double-well agents). The slope of ln k_TS1r,deep on ΔG is negative in ≥ 70% of eligible periods. Its magnitude is between 0.2 and 1.2 (the synthetic Kramers calibration is −0.62). This is a weak test: any process in which longer idle spells add idle occupancy gives a negative sign.
- **P-b2 (Markov-embedding closure):** median |ln(k_obs/k_MSM2)| ≤ 0.3 in regime I (memoryless given the coarse state), and > 0.3 in regime III with k_obs < k_pred (memory from timers and aging) in ≥ 5 of 8 regime-III periods.
- **P-b3:** the 1D Kramers closure misses by more than a factor 2 (median |ln ratio| > 0.7) almost everywhere. Not diagnostic (F).
- **P-b4:** across periods, the Spearman correlation between pooled ΔG and the deep escape rate is < 0. Descriptive.

**(c) Kicks: they raise escape, but not as exponential barrier lowering.**
- **P-c1 (regime I, TS1):** undirected kicks raise the hazard, with HR ≥ 1.5 and ln HR above the day-swap null p95, in ≥ 2 of 3 periods. Directed kicks have HR ≥ 1.5 as well.
  - Ordering: H04 found mentioned agents responding 4.7× more than unmentioned ones; H09 found mention HR ≈ 1 in regime I. These conflict, so I predict directed ≥ undirected with low confidence.
- **P-c2 (regime III, TS1):** undirected HR within [0.8, 1.25] or with a CI including 1; directed HR ≥ 1.3 and above the null p95. Each in ≥ 5 of 8 regime-III periods (H09: room messages never interrupt a pause).
- **P-c3 (regime III, TS2):** directed kicks during a pause raise the gate escape odds (OR ≥ 1.5, CI excluding 1) in ≥ 5 of 8 periods. Undirected OR has a CI including 1.
- **P-c4 (dose law):** where powered, the Kramers exponential law is **not** preferred: additive or saturating wins by AIC (κ = ln HR₂/ln HR₁ < 2) in the majority of powered (period × trap × group) cells. Reasons: H09's linear k = k₀ + c·r in regime I; H04's hidden-context reading (a message is read at the next turn, so a second message adds little).
- **P-c5:** in the slow window (15 min), N_tgt has ln HR > 0 in ≥ 5 of 8 regime-III periods (H04's delayed response).
- **P-c6 (loops):** directed kicks raise the per-turn break hazard of error loops (HR > 1) in the majority of periods with ≥ 30 kicked rows. Low power expected.

**(d) Swarm: mean field is right, with no collective bistability.**
- **P-d1:** the bias-corrected βJ₀ < 1 in 11 of 11 periods, with values in [0, 0.6].
- **P-d2:** valley-depth bimodality is not above the null (p > 0.05) with joint-silence minutes excluded, in ≥ 9 of 11 periods. With them included, false positives are possible; any such case is attributed to stalls only if the exclusion removes it.
- **P-d3:** the branch-memory excess (residual ACF at 30 min above the null p95) appears in ≤ 3 of 11 periods.
- **Falsifier of the mean-field claim:** a period with βJ₀ < 1 *and* significant valley bimodality after excluding stalls.

**Amendment A1 (2026-10-03): written after building the trap tables, before any analysis statistic was computed.**
- **What I had seen:** a sanity check of G40. It has 207 PAUSE events (the same count as H09's idle_runs), and under the strict TS2 rule 204 of them end in an active row, 1 is a re-pause and 2 are censored. Per-period gate counts are in the build log.
- **The problem:** strict chains barely exist, because any action at expiry counts as escape (e.g., one glance at the screen).
- **New variant, TS2r (glance-robust):** a gate is a re-pause if the next PAUSE comes within 120 s of waking. Waking is the first active row after the pause, or the expiry. Chains and k follow these re-pauses. A gate is censored if the window ends within 120 s of waking.
- **How it is scored:**
  - P-a4 and P-c3 are scored on strict TS2, as pre-registered, wherever strict TS2 has ≥ 10 re-pauses; otherwise they are "n/a (no strict chains)".
  - They are scored again on TS2r, labelled "amended".
  - Thresholds and directions are unchanged.

**Amendments A2–A4 (2026-10-03): POST HOC, made after seeing first-pass round-1 results. They are sensitivity analyses only; scored verdicts stay with the pre-registered estimators.**
- **A2, exact-time kick model.**
  - *What I had seen:* the first-pass TS1 kick estimates (30-s bins) for the ten 4-h periods, G51 excluded. Undirected and directed ln HR were small in regime I (−0.4 to +0.3), contrary to H09's ×3.06.
  - *Why:* a 30-s bin evaluates kicks at the bin start. A reply that comes about 20 s after a message usually falls inside the escape bin, so its trigger is not counted.
  - *What it is:* each TS1 spell is split at kick arrivals and at the moments kicks leave the 2-min window (a counting process; cloglog with offset ln Δt), with 20 day-swap null draws.
  - *Synthetic check:* for a fast trigger acting within ~20 s, ln HR(dose 1) is 1.73 with 30-s bins, 2.23 with 10-s bins and 2.68 with exact time. So 30-s bins attenuate fast effects but do not hide them.
- **A3, outage censoring.**
  - *What I had seen:* the first-pass swarm results, and a per-day diagnostic of G37. Its 03-31 window is 755 min long and contains a 513-min period in which every agent is silent.
  - *Scan:* village-off runs (all present agents silent ≥ 10 min) occur in G37 (one, 513 min), G38 (one, 213 min) and G51 (6 days, up to 492 min).
  - *Rule:* TS1/TS1r spells that overlap an outage are censored at its start; spells starting inside one are dropped. The landscape is recomputed without outage days.
  - *Already seen:* the first-pass G37/G38 TS1r slopes.
- **A4, within-day circular-shift null for swarm bimodality.**
  - *What I had seen:* G44's valley p = 0.005 with stalls excluded (βJ₀ ≈ 0.33), and a per-day / per-room diagnostic. The pooled bimodality tracks day-to-day shifts in #rest's activity level, which the day-swap null destroys by construction.
  - *What it is:* each agent's series is circularly shifted within its own day (by ≥ 30 min). This keeps each agent's activity level that day, so day-level common fields survive in the null.
- **Bug fixes, not amendments; first-pass numbers were never scored.**
  - The GLM silently returned β ≈ 0 when the line search stalled. Fits are now marked failed (NaN).
  - Coefficients with complete separation (|β| > 8 or SE > 4, e.g., a dose level with zero escapes) are now blanked individually, not left at ±13 or ±17.
- **Inference caveat found in round 1.** With 3–5 days, the day-block bootstrap has at most 35 distinct resamples (for 4 days), and the full-sample estimate can sit at the edge of its own bootstrap distribution (G44). Verdicts use the pre-registered bootstrap CI. Wald-CI verdicts (agent-FE model SE) are reported alongside, and any ≤ 5-day verdict is flagged.

## Confirmatory predictions (C-*): for the locked holdout, written 2026-10-03 after round 1, not run
Script: `analysis/confirm.py`. It refuses without `--confirm --i-understand-this-uses-the-locked-holdout`. `--dry-run` runs the same code on stand-ins (G31 for #32, G44 for #45) and wrote `data/processed/H16-metastable-traps-kramers/confirm_dryrun/` (stand-in results only, no holdout rows).
- **Rules use Wald CIs from the agent-FE model** (the day bootstrap is unreliable with 5 days; see the round-1 caveat).
- **Overall verdict:** supported if no primary prediction fails and ≥ 1 passes; failed if none passes; otherwise mixed.
- **Swarm block (d):** reported descriptively and not scored. βJ₀ and the activity distribution overlap with what H02 (#45) and H05 (NE12 ⊃ #32) computed.
- **Before a real run:** the card and the script must be committed (holdout reuse policy).

| ID | Target | Statement | Primary |
| --- | --- | --- | --- |
| C45-1 | #45 (III) | TS1r deep-window hazard ages within agent: β < −0.3 and Wald CI below 0 | yes |
| C45-2 | #45 | TS2r per-gate escape falls with re-pause count (agent FE, ln declared duration controlled): Wald CI below 0 | yes |
| C45-3 | #45 | a directed kick during a pause raises the gate escape odds: TS2r OR(dose 1) ≥ 1.5, CI excluding 1 | yes |
| C45-4 | #45 | TS3 error loops age: β < −0.3 and Wald CI below 0 | no |
| C45-5 | #45 | where powered, the dose law is additive or saturating in the majority of cells | no |
| C45-6 | #45 | undirected room messages raise TS1 escape above the day-swap null p95 (reverses P-c2, from exploration) | no |
| C32-1 | #32 (I) | TS3 error loops age: β < −0.3 and Wald CI below 0 | yes |
| C32-2 | #32 | regime I: undirected kicks do **not** raise escape from silences ≥ 3 min above the day-swap null p95 | yes |
| C32-3 | #32 | TS4 identical-command loops age: β < −0.3 and Wald CI below 0 | no |
| C32-4 | #32 | where powered, the dose law is additive or saturating | no |

- **Dry run (stand-ins, not evidence).** G31 as #32: C32-1 pass, C32-2 pass, C32-3 n/a, C32-4 fail. G44 as #45: C45-1 pass, C45-2 fail, C45-3 pass, C45-4 fail, C45-5 pass, C45-6 pass.
- **Expectations and power.**
  - #45: the C45-2 power is modest at 4–5 days (G44's Wald CI reached +0.08).
  - #32: it differs from every exploratory regime-I period by the 100-turn session cap (NE11) and by the rooms split on 02-25 (NE12/NE35), so C32 tests transfer across a scaffold change. The 02-25 split is a sensitivity check only.

## Results by goal period
Verdict rule: the core predictions (P-a1/a2, P-a4, P-c1/c2/c3, P-d1, P-d2) all supported → supported; none supported → failed; otherwise mixed. Every period is **mixed**, because aging and gate kicks (supported) sit next to the failed predictions on kicks in silent spells. Details are in each `G<NN>/README.md`.

| Period | Role | Verdict | Key numbers (TS1r deep β; TS2r β; TS3 β; undirected HR vs null p95; gate OR for directed kicks; βJ₀ stalls excl.) |
| --- | --- | --- | --- |
| [G27](goalperiod-subhypotheses/G27/README.md) | exploratory, regime I | mixed | −0.66 (52 escapes, CI spans band); –; −0.69; 1.12 vs 1.18; –; 0.26 |
| [G30](goalperiod-subhypotheses/G30/README.md) | exploratory, regime I | mixed | **+2.61** (24 escapes, timer-like); –; −1.05; 0.66 vs 1.12; –; 0.23 |
| [G31](goalperiod-subhypotheses/G31/README.md) | exploratory, regime I | mixed | too few (6); –; −0.68; 0.92 vs 1.08; –; 0.09 |
| [G37](goalperiod-subhypotheses/G37/README.md) | exploratory, regime III | mixed | **−1.56**; −0.36; −0.39; 1.16 vs 1.71; 0.91; **1.10** (outage day; 0.35 vs the within-day null) |
| [G38](goalperiod-subhypotheses/G38/README.md) | exploratory, regime III | mixed | **−1.71**; **−0.44**; −0.41; 1.22 vs 1.12; **2.90**; 0.09 |
| [G39](goalperiod-subhypotheses/G39/README.md) | exploratory, regime III | mixed | −1.97 (26 escapes; Wald below band); n/a; +0.20; 1.22 vs 1.16; n/a; 0.15 |
| [G40](goalperiod-subhypotheses/G40/README.md) | exploratory, regime III | mixed | +0.12 (28 escapes); −0.04; **−0.89**; 2.43 vs 2.52; 1.84 (13 gates); 0.12 |
| [G41](goalperiod-subhypotheses/G41/README.md) | exploratory, regime III | mixed | −0.62; −0.44 (Wald below 0); −0.72; **1.70 vs 1.35**; **2.35**; 0.35 |
| [G42](goalperiod-subhypotheses/G42/README.md) | exploratory, regime III | mixed | +0.21 (22 escapes); +0.32; −0.31; 1.01 vs 1.21; 8.1 (20 gates); 0.09 |
| [G44](goalperiod-subhypotheses/G44/README.md) | exploratory, regime III | mixed | −0.77 (Wald [−1.32, −0.22]); −0.23; +0.53; 1.31 vs 1.21; **2.17**; 0.33; pre-registered bimodality test **failed** (tiny-mode artifact, A5) |
| [G51](goalperiod-subhypotheses/G51/README.md) | exploratory, regime III | mixed | **−0.77** [−0.81, −0.73] (4,321); **−0.38**; **−0.72**; **1.48 vs 1.28**; **1.54**; 0.41 |
| [NE44](goalperiod-subhypotheses/NE44/README.md) | native (round 1b) | mixed | kick × ln k +0.57 before, +0.06 after (predicted 0 then < 0); declared pauses 90 → 180 s; escape at k = 1 0.58 → 0.49 |
| [NE43](goalperiod-subhypotheses/NE43/README.md) | native (round 1b) | mixed | aging unchanged with the nudger off (TS1r −0.59 → −0.53); gate escape unchanged (+0.006 [−0.09, 0.10]) |

*Round 1b (2026-10-04):* every G folder has a `Verdict (1b)` line (unchanged under the round-1 rule) and a Round 1b section; G27 carries the native long-debugging test (holds: blocked spells age, β −1.24).

## Results
### Exploratory round 1 (2026-10-03; non-holdout; 3 regime-I and 8 regime-III goal periods)
- **Scripts:** `scheme/build.py`, `analysis/run_period.py --period G<NN>`, `analysis/write_period_folders.py`, `analysis/summarize.py`, `analysis/summary_obs.py`, `analysis/synthetic.py`, `analysis/confirm.py`.
- **Numbers:** `data/processed/H16-metastable-traps-kramers/<period>/results.json`, `summary.json`, `period_scores.json`, `A5_valley_minmass.json`, `synthetic/`.
- **Figures:**
  - `figures/H16_summary.pdf` (one page);
  - `figures/cross_period.pdf`;
  - `figures/synthetic_validation.pdf`;
  - `figures/summary_obs.pdf`;
  - `G<NN>/figures/period.pdf`.

**Outcome vs. prediction.** Counts are periods (or powered cells for P-c4). "boot" and "Wald" are the two CI versions; the pre-registered verdict uses boot.

| Prediction | Predicted | Outcome | Verdict |
| --- | --- | --- | --- |
| P-a1 TS1r aging, regime III | ≥ 5/8 with CI below −0.3 | boot 3/8 (G37, G38, G51), Wald 4/8 (+G39). Point β < −0.3 in 6/8. None memoryless with a CI inside the band | **direction supported, count not met** (underpowered 4–5-day periods) |
| P-a2 TS1r aging, regime I | ≥ 2/3 | G27 −0.66 (inconclusive); G30 +2.61 (timer-like, 24 escapes); G31 n/a | **failed / underpowered** |
| P-a3 kicks remove aging (I) | ≥ 2/3 | only G27 testable; the slope does not shrink | **failed (1 period)** |
| P-a4 gate escape falls with k | ≥ 5/8 | strict: 3 supported (G37 −1.20, G38 −1.89, G51 −0.94), 3 with no strict chains. TS2r (amended): boot 2/7, Wald 3/7 (G38, G41, G51); negative in 6/7 | **direction supported; count not met** |
| P-a4b re-pause keeps/lengthens duration | ≥ 5/8 | 7/7 (median log ratio 0; longer 18–53% > shorter 13–27% in every period) | supported (weak: most re-pauses repeat the same duration) |
| P-a5 error-loop aging | majority | boot 1/11, Wald 3/11; point β < −0.3 in 8/11; G51 −0.72 [−0.87, −0.58] | **direction supported; CI rule met in 1–3** |
| P-a6 command-loop aging | majority | Wald 1/8 (G27), G51 −0.29, timer-like G44 | **not supported** |
| P-b0/b1/b2/b3 landscape | | b0 2/3 eligible periods; b1 slope −0.40 (G38), −0.66 (G51); b2 tautological; b3 G51 0.44 | **not diagnostic** (coordinate artifact; F fails for (b)) |
| P-c1 undirected kicks, regime I | HR ≥ 1.5 > null, ≥ 2/3 | 0/3 (HR 0.66–1.12); exact-time A2 also null | **failed** |
| P-c2 undirected ≈ 1, regime III | ≥ 5/8 | 4/8 within the band. **Above the day-swap null in 5/8** (G38, G39, G41, G44, G51; HR 1.2–1.7) | **failed** (undirected messages do raise escape from long silences) |
| P-c2b directed ≥ 1.3 > null (TS1) | ≥ 5/8 | 1/8; G51 HR 1.20 is above the null but below 1.3 | **failed** |
| P-c3 directed kick at the gate, OR ≥ 1.5 | ≥ 5/8 | TS2r: 5/7 (OR 1.5–2.9 in G38, G41, G44, G51; G42 8.1 on 20 gates). Strict TS2: separation-limited | **supported (amended definition)** |
| P-c4 dose law not Kramers | majority of powered cells | 14/16 additive or saturating. G51: undirected ln HR 0.36 / 0.39 / 0.41 for 1 / 2 / 3+ kicks | **supported**, with the caveat that synthetic timing attenuation also flattens the dose curve |
| P-c5 nudge, 15-min window | ≥ 5/8 | 1/8 (G51 +0.36 ± 0.08; few nudges elsewhere) | **failed / underpowered** |
| P-c6 kicks break error loops | majority | 0/10 (ln HR −0.54 to +0.12) | **failed**: messages do not break error loops |
| P-d1 βJ₀ < 1 | 11/11 | 10/11 (0.09–0.41). G37 1.10, an outage-day artifact: 0.35 against the A4 null | supported, 1 exception explained post hoc |
| P-d2 no bimodality (stalls excl.) | ≥ 9/11 | 10/11; G44 fails (tiny-mode artifact, A5: 11/11 unimodal) | **supported**; falsifier triggered once by the pre-registered statistic |
| P-d3 no branch memory | ≤ 3/11 | excess in 5/11 (G27, G37, G38, G41, G51) | **failed**: slow collective persistence without bistability |

**Reading.**
1. **Traps age.**
   - Within agent and in the deep window, the escape hazard from long inactivity falls roughly as t^−0.8 (G51 β = −0.77 [−0.81, −0.73]; G38 −1.71; G37 −1.56).
   - The older a pause chain, the less likely the agent acts at the next expiry (G51 −0.38, G38 −0.44).
   - Error loops age too (G51 −0.72).
   - Pooled slopes are steeper (G51 −0.95), so part of the aging is between agents, but most survives agent fixed effects.
   - This is rival R1 (trap deepening / disorder), not Kramers. Cold starts cap every trap at one day: dwell scales beyond a day are not identifiable (synthetic S1b).
2. **What ends a trap.**
   - *Regime III:* a directed message during a pause raises the chance of acting at the timer gate (OR 1.5–2.9). An undirected room message raises escape from long silences modestly (HR 1.2–1.7) above a null that keeps kick density and schedule.
   - *Regime I:* messages do not shorten silences ≥ 3 min (0/3). H09's ×3.06 came from turn-scale gaps.
   - *Dose:* one kick is what matters; a second or third adds little (saturating; κ ≈ 1.1–1.6). That fits H04's hidden-context reading (a message is read at the next turn) better than barrier lowering.
   - *Error loops:* messages never helped (0/10).
3. **Swarm.**
   - Mean field is right: βJ₀ ≈ 0.1–0.4 and swarm activity is unimodal once common stalls and outages are removed. Traps are individual.
   - Collective persistence at 30 min exists in 5/11 periods without bimodality: a slow shared field or weak coupling, not bistability.
4. **Landscape.** Boltzmann inversion of a smoothed 1-min activity coordinate does not measure a barrier: the apparent barrier is where one active minute jumps the EWMA. The test needs a graded, sub-minute observable (turn intensity, tokens, content drift) to mean anything.

**Caveats.**
- *Inference and data.*
  - Per-period power is low in 3–5-day periods. The day bootstrap is coarse there (Wald CIs are reported next to it).
  - Kick labels are temporal coincidences. The day-swap null keeps schedule and density but not within-day bursts, so part of the undirected-message effect may be shared burstiness.
  - TS1 in regime III mixes silent stalls (long model calls?) with pauses. The deep slope is negative in both subsets (G51: declared-idle −0.60, silent −1.04).
  - 11 periods × ~20 statistics: single-period hits are expected by chance. Only cross-period counts and the high-power G51 carry weight.
- *Amendments and fixes.*
  - TS2r (A1) was defined after seeing that strict pause chains barely exist.
  - A2–A5 are post hoc, with what I had seen listed above.
  - The GLM fixes (silent β ≈ 0 on stalled fits; separation) changed first-pass numbers, which were never scored.
  - **The b2 "pass" in synthetic was a tautology**; I caught it in round 1 and reclassified it as not diagnostic.
- *Not done.*
  - TS5 content-level spirals (embeddings) were not run.
  - No natural experiment (E = 0).
  - The H04 nudge mapping was reimplemented, not imported (same rules, plus clean mentions).

## Notes
- 2026-10-03: promoted from shortlist 2 (HH53 + HH86, shortlist 2, item 10).
- 2026-10-03: exploratory round 1 done (see Results). Compute: local, 1 process (≤ 2 threads); about 15 min of CPU in total. Disk: `data/processed/H16-metastable-traps-kramers/` ≈ 7 MB.
- 2026-10-03: the coordinator's data fix arrived before any kick was computed. `chat_core.mentions` carries a spurious `o1` on 175k messages; H16 uses `chat_mentions_clean.mentions_roster` throughout. H09's idle-agent mention flags are not reused.
- 2026-10-03: holdout reuse policy (`../holdout.md`).
  - #45 was used for confirmation by H02 (activity-timing couplings and its Curie–Weiss βJ₀ = 0.41). #32 lies inside H05's NE12 confirmatory window (room couplings on activity and talk spins).
  - H16's confirmatory statistics on these periods differ from those runs: dwell hazards, pause gates, loop hazards, kick dose laws and swarm bimodality. βJ₀ on #45 is **not** a confirmatory statistic for H16, because H02 computed it.
  - The H16 confirmatory script and predictions must be committed before the run.

## Round 1b (improved data, 2026-10-04)
*Re-evaluation on the improved data (Vivian's priority 2; two-layer design, `infra/data-quality/QUEUE.md`). Holdout untouched; no confirmatory run. Code: `scheme/build.py --r1b`, `analysis/r1blib.py`, `analysis/run_period.py --r1b`, `analysis/native_r1b.py`; the round-1 path (`build.py`, `run_period.py` without the flag) is unchanged. Numbers: `data/processed/H16-metastable-traps-kramers/r1b/`.*

### What changed in the inputs
- **Real failures for error loops (TS3r).** Round 1's TS3 used `actions.error`, which is "stderr non-empty": 58% of stderr-flagged bash turns are not failures (git and curl progress), and 15% of real failures have empty stderr. TS3r uses `turn_outcomes.failed` for bash/type turns and, for other computer-use turns, a platform failure (`error_class` in timeout, vm, resource, network, tool_use, other).
- **Nudge target = the leading @ (H35).** 29% of nudges also name other agents; round 1's N_tgt counted every named agent. N_tgt is now the nudge's leading-@ agent; every other exposure to a nudge (including being named second) is N_by. Text is read in memory only.
- **New trap types from Jev v3.1 windows:** **TS5 blocked spell** = a run of consecutive labelled windows with `p_blocked` ≥ 0.5 (escape: the next window has p_blocked < 0.5; censored at an unlabelled/absent window or the end of the span); **TS6 loop spell** = a run of windows with `longest_run` ≥ 5 (identical action+command repeats inside the window). Hazard per window, cloglog, agent FE, slope on ln(windows elapsed) for spells that reached 2 windows.
- **Lever controls.** H16's kick effects are hazards on *past* kicks (2-min and 15-min look-backs) inside the agent's own spell (presence-masked by construction), with a day-swap null; they never condition on future kicks, so the H30/H39 bias does not apply. Unchanged.
- **Unchanged inputs:** TS1/TS1r/TS2 come from `events_core` + `actions` active rows (not `activity_bins`), the swarm block (d) and the outage scan (A3) from H16's own minute grid. Their dwell numbers are recomputed as a check; kick models change only through N_tgt/N_by.

### Predictions (round 1b; written 2026-10-04 before running)
*What I had seen first:* H35's card (nudge target = leading @; before NE44 a nudge wakes a pausing agent at any trap age, escape 0.86–1.0; after it only early re-pauses respond), H39's nudger-off note (idle escape −13%, post hoc), DQ3's documentation and a structural check (per-period window counts, mean `p_blocked`, real-failure shares; the distribution of `longest_run` pooled over all windows, used to set the TS6 threshold at 5 ≈ its 90th percentile). No round-1b hazard or kick estimate.
- **P-a5r (error loops on real failures).** TS3r ages (β < −0.3, agent FE, k ≥ 3) in the majority of periods with ≥ 15 deep escapes; in G51, β < −0.3 with the bootstrap CI below −0.3. Credence 0.6. TS3r has ≥ 40% fewer loop rows than TS3 in regime III (descriptive). Credence 0.8.
- **P-c6r.** Directed kicks do not raise the break hazard of real-failure loops (ln HR ≤ 0 or CI including 0) in the majority of periods with ≥ 30 kicked rows. Credence 0.7.
- **P-a7 (TS5 blocked spells).** Aging (β < −0.3) in G51 and G38 and in ≥ 50% of powered periods (≥ 15 escapes after ≥ 2 windows). Credence 0.55. Memoryless (|β| ≤ 0.3 with CI inside the band): credence 0.3.
- **P-a8 (TS6 loop spells).** Aging in G51. Credence 0.5.
- **P-c3r (leading-@ targets).** A directed kick during a pause raises the TS2r gate escape odds (OR ≥ 1.5, CI excluding 1) in ≥ 5 of 7 regime-III periods. Credence 0.5 (round 1: 5/7 with every named agent as a target).
- **P-c2r.** Undirected kicks raise TS1 escape above the day-swap null's 95th percentile in ≥ 5/8 regime-III periods (replication; the definition is unchanged). Credence 0.6.
- **P-c5r.** N_tgt (leading @) raises the TS1 hazard in the 15-min window in G51 (ln HR > 0, Wald CI above 0). Credence 0.7.

### Native tests (layer 2; predictions written 2026-10-04 before running; `analysis/native_r1b.py`)
- **N1, NE44: the gate model across the pause-default change (12 h → 5 min on 06-11).** Pre = the regime-III periods G37–G44 (03-30 → 05-29) pooled with period fixed effects; post = G51 07-06 → 08-20 (nudger on, before NE43). TS2r gates, logit with agent FE, ln k and ln declared duration. (a) The directed-kick × ln k interaction is ≈ 0 before (CI includes 0) and negative after (CI below 0): a kick wakes an agent at any depth under long sleeps, only early re-pauses under short timers. Credence 0.5 (H35's version seen). (b) The median declared pause duration falls ≥ 5× from pre to post. Credence 0.8. (c) Gate escape at k = 1 is more likely before than after. Credence 0.5. The NE21+NE23 holdout window (06-08 → 07-06) contains the change itself and is not used, so this is a between-period contrast (confounded with goals and roster), not an event study.
- **N2, NE43: escape with no kicks (#51).** B = 08-07 → 08-20 (nudges on, bookends gone) vs C = 08-21 → 09-02 (no nudges). (a) Aging persists on both sides (TS1r deep β < −0.3 and TS2r β_lnk < 0 in each). Credence 0.7. (b) Gate escape is lower without nudges: the C indicator in the TS2r gate logit (agent FE, ln k, ln declared duration) is negative with its Wald CI below 0. Credence 0.4.
- **N3, #27 long debugging traps (regime I, 10 days, 55k model calls).** TS3r or TS5 ages in G27 (β < −0.3, Wald CI below 0, for at least one of the two). Credence 0.5. Directed messages do not break TS3r loops in G27 (P-c6r). Credence 0.7.
- **Not run:** #16 (operator rules against two named trap behaviors) needs content labels for spreadsheet and bug-report loops; queued for round 2.

### Results (round 1b, run 2026-10-04)
*Numbers: `r1b/<period>/results.json`, `r1b/summary_r1b.json`, `r1b/native_r1b.json`. Figure: `figures/r1b_summary.pdf`. Compute: ≈ 10 min, one local process. TS1/TS1r/TS2 dwell numbers reproduce round 1 exactly (same inputs); the landscape (b) and swarm (d) blocks were not re-run (inputs unchanged).*

**Old vs new per period** (agent-FE cloglog slopes on ln k or ln elapsed; boot = day-bootstrap 95% CI; TS5/TS6 have no round-1 counterpart):

| Period | TS3 error loops, stderr (r1): β [boot], deep escapes | TS3r real failures (1b): β [boot], escapes | TS5 blocked spells (1b): β [Wald], spells | TS6 loop spells (1b): β [Wald] | gate OR, directed kick (r1 → 1b) | N_tgt kicks (r1 → 1b) |
| --- | --- | --- | --- | --- | --- | --- |
| G27 (I) | −0.69 [−0.93, 0.40], 186 | −0.19 [−0.93, 3.3], 57 | **−1.24 [−1.93, −0.54]**, 335 | +0.25 [−0.82, 1.31] | – | 0 → 0 |
| G30 (I) | −1.06 [−1.30, 0.19], 111 | +1.27 [−0.39, 5.6], 25 | +0.43 [−1.18, 2.05], 155 | +0.02 | – | 20 → 12 |
| G31 (I) | −0.68 [−1.25, 3.0], 127 | −0.77 [−0.86, 1.38], 43 | +0.55, 123 | −0.88 | – | 40 → 20 |
| G37 | −0.39 [−1.22, 0.79], 53 | −0.53 (14) | +1.10 [−0.64, 2.84], 85 | +0.91 [0.01, 1.81] | 0.91 → 0.83 | 24 → 20 |
| G38 | −0.41 [−0.59, 0.64], 218 | −0.07 [−0.31, 2.75], 77 | −0.17 [−0.68, 0.34], 414 | **−0.77 [−1.17, −0.37]** | 2.90 → 2.92 | 120 → 110 |
| G39 | +0.21 [−0.13, 1.62], 71 | −0.09 (23) | n/a (12 escapes) | +0.81 | n/a | 8 → 7 |
| G40 | **−0.89 [−1.30, −0.15]**, 432 | +0.09 [−0.10, 5.3], 27 | +2.95 [0.61, 5.28], 113 | −0.94 [−2.14, 0.26] | 1.84 → 1.84 | 11 → 11 |
| G41 | −0.72 [−0.91, −0.09], 223 | −0.36 [−0.75, 4.0], 42 | −0.76 [−1.69, 0.18], 121 | +4.0 | 2.35 → 2.27 | 72 → 59 |
| G42 | −0.31 [−0.65, 1.36], 91 | +0.16 (25) | +0.09, 145 | −0.08 | 8.1 → 17.4 (20 gates) | 28 → 25 |
| G44 | +0.54 [0.24, 1.72], 117 | +1.63 [−0.11, 5.9], 29 | +0.91 [−0.07, 1.89], 145 | −0.29 | 2.17 → 2.57 | 32 → 27 |
| G51 | **−0.72 [−0.89, −0.37]**, 2,253 | **−0.57 [−0.69, −0.06]**, 984 | **−0.39 [−0.56, −0.22]**, 3,417 | **−0.46 [−0.63, −0.29]** | 1.54 → 1.52 | 970 → 729 |

**Outcome vs prediction (round 1b):**

| Prediction | Outcome | Verdict |
| --- | --- | --- |
| P-a5r: real-failure loops age in the majority of powered periods; G51 boot CI below −0.3 | point β < −0.3 in 3/10 powered periods (G31, G41, G51); boot CI below −0.3 in 0/10 (Wald: G51 only). G51 −0.57 [−0.69, −0.06] | **failed** (round 1 on stderr: 8/11 point estimates) |
| TS3r has ≥ 40% fewer loop rows (regime III) | −51% overall (−34% to −80% per period) | holds |
| P-c6r: directed kicks do not break real-failure loops | 9/9 powered periods; ln HR −0.53 to +0.11 (G38 −0.53 ± 0.17, G27 −0.51 ± 0.13) | **holds** |
| P-a7: blocked spells age in G51, G38 and ≥ 50% of powered periods | G51 −0.39 [−0.50, −0.12] boot; G38 −0.17 (CI spans 0); point aging 3/10; timer-like in G37, G40, G44; memoryless in 0/10 | **failed** (aging only in the long #51 window and #27) |
| P-a8: loop spells age in G51 | −0.46, boot [−0.55, −0.18], Wald [−0.63, −0.29] | partial (β < −0.3, CI below 0 but overlaps the band) |
| P-c3r: directed kick at the gate, OR ≥ 1.5, CI excluding 1, in ≥ 5/7 | 5/7 (G38, G41, G42, G44, G51); ORs barely move under leading-@ targets | **holds** (as round 1) |
| P-c2r: undirected kicks above the day-swap null in ≥ 5/8 | 6/8 | holds |
| P-c5r: N_tgt slow-window ln HR > 0 in G51 | +0.35 ± 0.045 (round 1 +0.36 ± 0.08) | holds |
| N1 NE44 (a): kick × ln k ≈ 0 before, < 0 after | before **+0.57 [0.27, 0.87]**, after +0.06 [−0.04, 0.16] | **failed as stated** (see reading) |
| N1 NE44 (b): median declared pause falls ≥ 5× | 90 s before vs 180 s after (90th pct 600 vs 840 s) | **failed** |
| N1 NE44 (c): escape at k = 1 higher before | 0.58 vs 0.49 | holds |
| N2 NE43 (a): aging persists without kicks | TS1r deep β B −0.59 [−0.68, −0.39], C −0.53 [−0.56, −0.41]; TS2r β_lnk −0.31 and −0.26 (CIs below 0) | **holds** |
| N2 NE43 (b): gate escape lower without nudges | C indicator +0.006 [−0.09, 0.10] (directed kick +0.42 [0.28, 0.56]) | **failed** |
| N3 #27: TS3r or TS5 ages; messages do not break TS3r | TS5 −1.24, Wald [−1.93, −0.54] ✓; TS3r −0.19 (flat); directed ln HR on TS3r −0.51 ± 0.13 ✓ | **holds** |

**Reading.**
1. **"Error loops age" was largely a stderr artifact.** Round 1's TS3 counted runs of turns with non-empty stderr, so a chain of git or curl progress messages looked like a deepening error loop. On real failures half the loop rows disappear, and aging survives only in the long #51 window (β −0.57, weaker than −0.72). In the 4-h periods real-failure loops are short and flat or timer-like.
2. **Semantic traps age where there is power.** Blocked spells (Jev `p_blocked` ≥ 0.5) and repeated-action spells age in #51 (β −0.39, −0.46) and in #27's long debugging (blocked β −1.24); repeated-action spells age in #38 (−0.77). In short periods several are timer-like, so aging is not universal across trap types.
3. **Kick results are robust to the nudge-target fix.** The leading-@ rule removes 25% of #51's N_tgt rows, and every kick estimate moves by less than its SE. Messages still never break failure loops; if anything they arrive during longer ones.
4. **NE43: aging is intrinsic, not kick-made.** With the nudger off, the dwell and gate aging slopes are unchanged and gate escape is as likely as before. The trap deepens by itself.
5. **NE44: H35's pattern holds in probabilities, not in my logit interaction.** Before the pause-default change, a directed kick lifts escape at deep gates (k ≥ 3) from 0.21 to 0.56; after it, from 0.17 to 0.25. On the logit scale that is a positive interaction before and none after. Declared pause durations did not shrink (90 → 180 s median): agents almost always declare a duration, so the 12-h default rarely applied in these periods. NE44 changed the response to kicks without changing the declared timers.

**Verdict changes.** Per period: none under the round-1 rule (its core predictions, aging on TS1r/TS2r and the gate and room kicks, did not change); `Verdict (1b)` lines note the error-loop and window-trap results. Card level: the claim "error loops age too" is withdrawn outside #51; "traps age" now rests on silences, pause chains and #51's semantic spells; "aging is intrinsic" gains support from NE43.

**Scorecard (round 1b; round 1 in brackets).** A 1 [1]: real failures, leading-@ targets and v3 window traps defined from fields; `p_blocked` is regime-dependent. B 1 [1]. C 1 [1]. D 1 [1]. **E 1 [0]**: NE43 tested; aging unchanged with the nudger off, as predicted; the predicted drop in gate escape and the NE44 interaction failed. F 1 [1]. G 1 [1]: the gate response follows the known scaffold change (NE44) in probabilities. H 0 [0]: Kramers still loses to aging. I 1 [1].

**Shared-file suggestions** (not made): `infra/README.md` known issue: *"Error-loop statistics built on `actions.error` are mostly stderr loops (git/curl progress): H16's TS3 loses 51% of rows and most of its aging on `turn_outcomes.failed`."* `kicks_classified`: the queued `primary_target` column (H16 now computes it in `r1blib.nudge_targets`, same rule as H35). NE44 row in `natural-experiments.md`: "declared pause durations did not shrink across 06-11 in non-holdout regime-III periods (median 90 → 180 s); the change shows in the kick response, not the timers (H16 round 1b)."

## Round 2 redirects (2026-10-04)
*From the round-1 reflection (`writeup/round1-reflection/round1-reflection.pdf`).*
- **Where round 1 went sideways:** The Kramers barrier on a smoothed activity coordinate was an artifact; the aging was real.
- **What the direction is really after:** Traps deepen by self-reinforcement as the context fills with the agent's own output.
- **H16-R1.** Pólya urn: P(repeat) ∝ the share of the context that is own repeats. This predicts the aging exponent (about −0.8 in #51) from the measured context composition (E2).
- **H16-R2.** One directed message works because it dilutes the urn; repeated messages add little once the context is diluted.
- **H16-R3.** Trap depth is a model trait: some models loop more.

## Round 2 (2026-10-05): Pólya urn, dilution, trap depth as a trait, and the mixture rival
*Predictions, nulls and kill rules written 2026-10-05 ~03:30 UTC, before any round-2 outcome statistic on real data. Exploratory; non-reserved days only (`holdout_mask`; the ledger's `holdout` flag; #51 before 09-03 as in round 1). Serves Q5 (what gets a stuck agent out) and Q6 (trap kinetics). Code: `scheme/build_r2.py`, `analysis/r2lib.py`, `analysis/predict_r2.py`, `analysis/synthetic_r2.py`, `analysis/run_r2.py`. Numbers: `data/processed/H16-metastable-traps-kramers/r2/`. Rounds 1 and 1b reproduce unchanged (their code paths are not touched).*

**What I had seen first.**
- Rounds 1/1b of this card; H72 round 1 (gate aging −0.48 on the call clock survives starvation control; recent input *lowers* escape, β_s +0.23); RE-R1 (unaddressed chatter holds agents at the timer gate; a mention restores the no-news rate, OR 3.1); H69 round 2 (own tool tokens do not trigger restatement loops; an erasure ends loops as a step, not a dose); H44 (after a forced erasure agents re-read and pause less); H45 (room share follows inflow passively; the token ruler).
- Structural counts with no outcome: the token ruler (an own idle call adds ≈ 320–370 prompt tokens, an active call 560–1,180, the prompt at a reset is 13–20k); composition at regime-III gates (G51 medians: token share of own repeats f_tok 0.021, call share f_call 0.19, entry share 0.058, recency share 0.10); 774 gates in G51 follow a context reset inside the trap (289 forced at the 41-call cap), 43 in G38 (41 forced); 3,875 G51 gates read a directed item at the gate.
- **A structural fact about TS1r:** in regime III, 45–58% of TS1r spells end within 60 s of a CONSOLIDATE event, and 48% of G51 spells start with a consolidation call within 60 s of the last active row (median dwell 5.5 min). A consolidation is logged ≈ 3 min after the previous turn and counts as an active row, so these "spells" are the consolidation's own latency, not traps. Spell kinds at start in G51: consolidation 10,630; pause 7,133; silent 7,122.
- **The urn-predicted exponents** (below, from `predict_r2.py`): computed from composition on the real skeleton with simulated outcomes. No observed escape entered.

### Degrees of freedom and model
- **State at a gate** (call clock, H72's shared `idle_gates`): the composition of the context segment (calls since the last reset; regime III). n_rep = own idle calls earlier in the segment; n_act = own active calls; k = room items in context; B = the prompt at a reset (system prompt, memory, room snapshot).
- **Pólya urn (H16-R1).** P(escape at gate) = c_i (1 − f), with f the own-repeat share of the context. On the wall clock (TS1r, 30-s bins): cloglog h = α_i + ln(1 − f). Four rulers for "share of the context", fixed before data:
  - **U-tok (primary):** f = n_rep τ_I / (B_L + n_rep τ_I + n_act τ_A + R), the token share (H45 room ruler for R; lab medians for τ_I, τ_A, B_L; `r2/ruler.json`).
  - **U-call:** f = n_rep / (n_rep + n_act), the share of own calls in the segment that are idle.
  - **U-entry:** f = n_rep / (n_rep + n_act + k), the share of context entries.
  - **U-rec:** idle calls among the last 10 entries (recency urn).
- **Rivals.** R1-intrinsic: aging with trap age at fixed composition (H72). **Mixture:** within-agent mixtures of spell kinds (consolidation latency, pause chains, silent spells; after work, talk or a failure) produce apparent aging with no aging inside any kind. **Context step:** a reset raises escape by a fixed step regardless of how much repeat content it removes (H69's finding for loops). **Address:** a message works because it names the agent, not because it dilutes.

### R1 · The urn's exponent from composition (pre-registered numbers)
Urn-predicted slopes on the real skeleton (100 simulated outcome sets; band = 2.5–97.5%). Gate: agent-FE logit of sustained escape on ln(trap age), with ln previous pause, hours into the day, others' activity and ln last-run length; the level c makes the mean escape 0.5 (0.3 / 0.7 in brackets). TS1r: agent-FE cloglog slope on ln elapsed in the deep window (≥ 10 min).

| Urn | G51 gate β_pred [band] (level 0.3 / 0.7) | G38 gate β_pred | G51 TS1r β_pred [band] | G38 TS1r β_pred |
| --- | --- | --- | --- | --- |
| **U-tok (primary)** | **−0.02 [−0.05, 0.01]** (−0.02 / −0.03) | −0.02 [−0.15, 0.11] | **0.00 [−0.03, 0.04]** | 0.00 [−0.30, 0.39] |
| U-call | −0.37 [−0.40, −0.34] (−0.28 / −0.56) | −0.17 [−0.33, −0.05] | −0.08 [−0.12, −0.04] | +0.01 [−0.49, 0.49] |
| U-entry | −0.03 [−0.06, 0.00] | −0.09 [−0.19, 0.02] | +0.01 [−0.02, 0.04] | −0.01 |
| U-rec | −0.04 [−0.07, 0.00] | −0.17 [−0.30, −0.06] | +0.01 [−0.03, 0.03] | −0.03 |

The level c is set to the observed overall escape fraction when the observed slope is compared (interpolating the 0.3/0.5/0.7 values); that is a single level, not a slope.

| # | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| R1-P1 | **U-tok does not predict the exponent.** In G51 the observed gate slope and the observed TS1r slope each lie outside the U-tok band, with \|β_obs − β_pred\| > 0.2 | the observed slope's CI overlaps the band and \|Δ\| ≤ 0.2 (the urn predicts it) | 0.9 |
| R1-P1b | U-call comes closest at the gate (\|Δ\| ≤ 0.2 in G51) but not on TS1r | — | 0.35 |
| R1-P2 | **Composition does not absorb aging.** Adding ln(1 − f) to the gate model leaves ρ = 1 − β_a/β_a0 < 0.25 for every ruler (G51) | ρ ≥ 0.5 with β_f > 0, CI > 0 (urn absorbs aging) | 0.75 |
| R1-P3 | **A forced reset inside a trap raises escape as a step** (NE41; exception (c), the transition is the object). G51: forced-reset OR > 1 with CI > 1 | OR CI includes 1 at power ≥ 0.8 | 0.6 |
| R1-P4 | **The step is not a dose.** The interaction of the forced reset with the removed repeat content Δ_u = −ln(1 − f_pre) (U-call; U-tok variant) has a CI including 0 | CI > 0 (urn dose) | 0.6 |

**Kill rule (R1).** If R1-P1 holds for U-tok and R1-P2 holds, the card states "the own-repeat share of the context does not set the aging exponent". If an urn ruler passes both P1 (gate and TS1r) and P2, "traps deepen by self-reinforcement as the context fills with the agent's own output" is adopted for that ruler. R1-P3/P4 are read only where the synthetic power is ≥ 0.8; otherwise inconclusive.

### R2 · Does a directed message work by diluting the urn?
Gate model as in R1 plus current reads at the gate: 1[≥ 1 directed item], 1[only undirected items], and Δ_k = ln(1 − f_with) − ln(1 − f_without), the urn-implied effect of the items read at the gate (U-tok primary, U-entry, U-rec).

| # | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| R2-P1 | **Address, not dilution.** Directed current reads raise escape more than undirected ones: the difference of the two log ORs has CI > 0 (G51). The urn predicts equal effects per item | difference CI includes 0 or < 0 | 0.75 |
| R2-P2 | **The urn-implied kick is far too small.** The mean Δ_k at directed gates (U-tok, U-entry) is < 0.2 × the observed directed log OR | ratio ≥ 0.5 | 0.85 |
| R2-P3 | **No dilution scaling.** The Δ_k coefficient's CI includes 0 (read only at power ≥ 0.8 for a coefficient of 1) | CI > 0 | 0.6 |
| R2-P4 | **Saturation.** Two or more directed items add less than half the first item's log OR (G51) | ≥ 2 items' log OR ≥ 1.5 × the first's | 0.6 |

### R3 · Trap depth as a model trait (CLAUDE.md exception (b))
Every agent runs one model (one shared fine-tuned model string aside), so "model" = agent; lab is the coarser group.
- **Depth:** D_{a,p} = −ln k_deep, with k_deep the censoring-aware exponential escape rate (escapes per minute of exposure) of agent a's TS1r spells after 10 min in period p. Cells with ≥ 5 deep escapes. Sampling variance 1/escapes.
- **Invariance first (R3-P1):** for agents in ≥ 2 periods, the correlation of D_{a,p} with the agent's mean in the other periods (period-centred), pooled over periods; agent bootstrap CI. **Pass:** r > 0 with CI > 0. Credence 0.6. If it fails, no pooled per-model depth is reported (only per-period values).
- **Partial pooling (R3-P2):** D_{a,p} = μ_p + u_agent + e, method-of-moments variance components with the sampling variance known; per-agent shrunk depth with intervals. Agent share of the non-sampling variance ≥ 0.2, permutation p < 0.05 (agent labels permuted within period). Credence 0.5. Lab share (same test with lab labels): credence 0.3 (shared-priors check).
- **R3-P3 (G51, aging per model):** agent-specific deep TS1r slopes differ (Cochran Q p < 0.05). Credence 0.5.

### Mixture rival (within-agent mixtures of spell kinds)
Kinds fixed at spell start (never from the spell's future):
- TS1r: **kind_start** (consol: a consolidation call starts within 60 s; else the first declared idle in the first 180 s: pause, wait, silent) × **last_kind** (the last active row is a real failure, a talk event, or other work).
- Gates: **trap_kind** = the last active call before the trap failed / talked / worked.

| # | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| M-P1 | **Aging survives within kinds.** The deep TS1r slope within pause-start spells (agent × kind FE) is < −0.3 with day-bootstrap CI below 0 in G51 | CI includes 0 or β ≥ −0.3 | 0.7 |
| M-P1b | Same in G38 | — | 0.5 |
| M-P2 | **The pure-mixture null fails.** On the real skeleton, constant hazards per agent × kind_start × last_kind cell (no aging inside any cell) give pooled agent-FE slopes whose 2.5th percentile lies above the observed G51 slope | observed slope inside the null's 95% range | 0.75 |
| M-P3 | **Gate aging survives within trap kind:** after-work traps in G51, slope < −0.2 with CI below 0 | — | 0.75 |
| M-P4 | Descriptive: the share of the pooled G51 TS1r slope explained by kind mixing, 1 − β_within/β_pooled | — | — |

**Kill rule (mixture).** If M-P1 fails and M-P2 fails, the claim "traps age" is withdrawn as a mixture artifact for TS1r and stated only for gates (if M-P3 holds). Per-spell frailty (unobserved depth) is not separable from aging with single spells; the forced reset (R1-P3) is the one design that separates them (a frailty world gives no step; synthetic check).

### Nulls and validation plan (before any real-data round-2 statistic)
`analysis/synthetic_r2.py` on the real G51 and G38 skeletons. Gate worlds simulated **sequentially within traps** (stop at the first escape; censor at the real trap end): W0 null; W1 intrinsic aging (−0.5 per ln a); W2 urn (U-call, the strongest ruler); W3 per-trap frailty (SD 1.5), no conditional aging; W4 W1 + a forced-reset step (+0.7, no dose); W5 W1 + an address kick (+0.7 for a directed read, undirected 0). TS1r worlds: per-row draws on the deep skeleton with cell hazards (pure mixture) or within-cell aging (−0.5). R3: planted agent depths (SD 0.5 or 0) on the real agent × period skeleton.
Pass: size ≤ 0.10 and power ≥ 0.8 at real counts; otherwise the statistic is reported as inconclusive (dated amendment).

### Round-2 synthetic validation (run 2026-10-05 ~03:40–04:20 UTC, before any round-2 outcome statistic)
`analysis/synthetic_r2.py`; outputs `r2/synthetic/{gates,ts1r,r3}.json`. Gate worlds: 30 runs (G51), 60 (G38); sequential within traps. TS1r: 8 runs (G51), 16 (G38), 40 null draws each. R3: 40 runs. Rates are Wald-test rejections at 5% (two-sided).

| Statistic | Null world (size) | Planted world (power) | Notes |
| --- | --- | --- | --- |
| Gate aging β_a0 | W0: 0.03 (G51), 0.05 (G38) | W1 −0.49 (truth −0.5): 1.00 / 0.95 | unbiased |
| Absorption (U-call): β_f > 0 and ρ | W1: β_f 0.00, ρ 0.00 | W2 urn: β_f 1.70, power 1.00; ρ 1.02 (G51) | separates intrinsic aging from the urn |
| Absorption (U-tok) | β_f erratic (W0 −0.34, W3 +4.7) | — | f_tok varies too little: β_f is weakly identified; ρ is read, β_f is descriptive |
| Per-trap frailty (W3) | marginal aging −0.44 with no conditional aging | — | **frailty fakes aging on the gate clock**; forced-reset step **+0.47 (rejection 0.87)** in the pre-registered reset model |
| Forced-reset step (with ln k, A1) | W1 0.00; **W3 0.01 (0.00)** | W4 +0.74: 1.00 (G51), 0.33 (G38); W2 urn +0.58: 0.83 | G51 powered; G38 not |
| Reset × removed repeat share (dose) | W4: −0.55 (0.10) | W2: power 0.30 | **not powered** |
| Directed vs undirected (diff) | W1: 0.00–0.07 | W5 +0.69: 1.00 (G51), 0.92 (G38) | — |
| Dilution coefficient on Δ_k (U-entry) | W5: 0.07 | W6 1.27 (truth 1): 0.97 (G51); G38 0.14, not powered | U-tok Δ_k separates (too little variance): not estimable |
| Dose 2+ directed items | — | W5: 1.00 (G51), 0.42 (G38) | — |
| TS1r pure mixture (cell SD 1) | pooled slope −0.02 (G51), +0.01 (G38); M-P1 size 0.00; M-P2 size 0.13 (1/8) | WA −0.50: M-P1 1.00 / 0.25; M-P2 1.00 / 0.50 | the real deep skeleton shifts little between kinds; G38 underpowered |
| R3 invariance r > 0 | u SD 0: 0.025 | u SD 0.5: 0.80 | — |
| R3 agent share (permutation) | 0.05 | 0.73 (share 0.65) | — |

### Round-2 amendments (2026-10-05 ~04:20 UTC, after the synthetic validation, before any round-2 outcome statistic)
- **R2-A1 · ln(gate index) in the reset and kick models.** The pre-registered reset model gives a frailty world (W3) a spurious forced-reset step of +0.47 (rejection 0.87): forced resets fall at k = 1 after long work runs (53% at k = 1, trap age 11 vs 6 min), where survivor selection has not yet acted. Adding ln k_sus removes it (W3: 0.01, size 0.00) and keeps power (W4: 1.00). The kick models get the same term. The aging and absorption models are unchanged.
- **R2-A2 · R1-P4 (reset dose) is descriptive** (power 0.30). **R1-P3 and R1-P4 are read in G51 only** (G38 power 0.33).
- **R2-A3 · U-tok β_f is descriptive;** R1-P2 is decided on ρ (with β_f for U-call, U-entry, U-rec). **R2-P3 is read on Δ_k (U-entry) in G51 only;** Δ_k (U-tok) separates.
- **R2-A4 · M-P1b (G38) is inconclusive by design** (power 0.25); G38 within-kind slopes are descriptive.
- **R2-A5 · Frailty caveat made explicit.** A per-trap frailty world reproduces gate-clock aging (−0.44). Gate aging alone therefore cannot separate aging from unobserved trap depth; only the forced reset (A1 model) can, and only in G51.
