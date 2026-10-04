# H116: The election as a coupling step: influence should flow toward the winner after the result (#26)

**Status:** exploratory round 1 **done (2026-10-04): failed. The election result does not step the winner's per-call out-coupling (power only for steps ≳ 0.75 Ising units); designations in #12 and #35 carry no out-coupling either. Post hoc, the 01-09 re-election does show a step.** Card and predictions written 2026-10-04 22:05 UTC; Amendments A0 (22:12, skeleton) and A1 (22:25, synthetic) before any real-data H116 statistic.
- **N1 (primary):** ΔJ_out(17, T*) = +0.035 (λ = 4; magnitude +0.09 ± 0.33): percentile 0.56 of 16 time placebos and 0.71 of the event-day skeleton null. Not detected; excludes Δ ≥ 0.75, silent on HH354's 0.05 (synthetic power 0.14 there).
- **N1b** in-coupling flat (consistent); **N1c** the winner does not stand out among 9 agent placebos; **N3** no read-over-in-flight step; **N4** EP below resolution.
- **N2 (negative control) failed:** at the 01-09 re-election ΔJ_out = +0.31 ± 0.21 (magnitude +1.03 ± 0.47), above all event-offset, re-election-offset (post hoc) and skeleton placebos, with read > in-flight.
- **Replication:** judges (#12) Δout −0.04 ± 0.10 (p 0.76); lead designers (#35) −0.02 ± 0.11 (p 0.83).
- Scorecard A1 B1 C1 D1 E1 F2 G1 H1 I0. `analysis/confirm.py` (NE37 / #48 focal agent) frozen, guarded, dry-run; **not run**.
**Fields:** stat mech (kinetic Ising, broken detailed balance, entropy production), sociophysics (leadership, elections)
**Literature:** [Aguilera, Ito & Kolchinsky 2026](../../literature/aguilera-2026-entropy-production-nonequilibrium-maxent.md) (kinetic Ising; maximum-entropy lower bound on entropy production from antisymmetric observables). Cited from memory (†, not in `literature/`): Roudi & Hertz, *PRL* 106, 048702 (2011)†; Glauber, *J. Math. Phys.* 4, 294 (1963)†.
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime; Driving / external field (the goal the leader sets; the election itself); Exposure (turn read-out) via the context ledger's visibility rule; **Call clock**, **per-call coupling** (H40); **In-flight placebo (matched-lag)** (H67); **Entropy production (pairwise AIK bound)** in a call-clock multipartite variant (defined below); **Taylor field gauge c_×** (H86). New named variants proposed for DEFINITIONS.md (not edited here): *talk spin (per call)*, *read-gated sender input*, *out-coupling step ΔJ̄_out*, *multipartite call-clock EP bound Σ_mp*.
**From:** HH354 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/02-nonequilibrium-ising/`
**Data inputs (shared tables first):** `call_windows`, `context_ledger_turns` (room per call), `context_ledger_items` (read-rule validation only), `chat_core`, `calendar`, `period_units`, `per_period_estimates` (H86 c_×), `ground_truth_labels` (#26 `phase`, `tally`, `leader` rows; #12 `judge` rows after H115's freeze; #35 `leader` rows). No text is read.

## Source HH (verbatim from the HH list, including refinements)
- **HH354 · The election as a coupling step: influence should flow toward the winner after the result (#26).** Before the result every agent is a peer; after it, one agent sets the week's goal.
  - *Prediction:* the winner's out-coupling (Σ_j J_ji) jumps at the result time while the in-coupling does not; the swarm's EP rises with the new asymmetry. H65 found the elected leader gets attention but no extra broadcast reach in regime II, so in regime I a step of ≥ 0.05 is the test.
  - *Check:* date the result from chat (one timestamp); event study with windows on both sides, matched placebo times on other days.
  - *Kill:* no step in out-coupling beyond placebo times.
  - *Impostors:* the goal change that follows the election is a field step; separate coupling (responses to the leader's messages at read-out) from the new goal direction.
  - *Models:* 02 · *Builds on:* H65, H29, HH83

## Standards (2026-10-04)
**Question served:** **Q1** (what couples agents?): does a designation change who couples to whom, on the per-call clock? **Q5** second: does electing a leader buy broadcast reach, and how large is it?

| Impostor | Relevant? | How it is removed | Status (planned) |
| --- | --- | --- | --- |
| Scheduler field | yes | Per-call clock; calls trimmed to the all-present window; agent × call-mode × side (pre/post) intercepts; the same clock-time and kickoff-offset windows on placebo days; H86 c_× reported. | removed (planned) |
| Exogenous field (the election, the new goal, the kickoff) | yes (central) | Side-specific intercepts absorb any talk-level step at the result (the new goal as a field). The statistic is the step in the *response to the winner's read messages*, not in talk level. Kickoff-matched placebos: the first days of #24, #25, #27 at the same offset from the day start, because 01-05 is #26's kickoff day. A guard band drops the vote itself (first ballot 19:25:09 → result 19:35:22 UTC). | removed (planned) |
| Shared model priors | partly | The winner's family is fixed across the event; agent placebos (the same event time with each other agent as "winner") show whether any agent steps. | partly (planned) |
| Contemporaneous convergence | yes | In-flight placebo: the winner's messages posted during a recipient's call; the read-gated step must exceed the in-flight step (partition contrast, STANDARDS §3). | removed (planned) |

**Inputs:** ledger call clock and visibility rule (my read rule checked against `context_ledger_items`), `chat_core`, DQ6 labels. Not `activity_bins`.
**Two layers:** natives on G26 (N1 the runoff result step, primary; N2 the 01-09 re-election as a null event; N3 read vs in-flight; N4 EP); replication on G12 (judges: in-role vs out-of-role out-coupling) and G35 (daily lead designers). G44 is not eligible: its leader arrives with the role, so there is no pre window.
**Confirm script:** `analysis/confirm.py` (NE37: the step from the focal agent's last #47 day to #48; C1–C2), frozen 2026-10-04 22:35 UTC (SHA-256 `64f36b1c…812c`), guarded (`--confirm` + `H116_CONFIRM=1` + ledger check on G47 and G48 + coordinator-supplied `--focal`), dry-run on a non-holdout stand-in (#26 01-07 → 01-08, agent 17); **not run**. NE31 (#45) was the first choice but is blocked: H02 ran the same family on #45.

## Question
Before 2026-01-05 19:35:22 UTC agent 17 (DeepSeek-V3.2) was one of ten peers. At that moment it won the runoff (7–1–0 after a 9–9–9 approval tie) and gained the right to set the week's goal. Does the swarm's per-call talk response to agent 17's messages step up at that moment, while agent 17's response to others stays the same? A yes means a designation changes the coupling matrix, not only the field. A no (with power) means an elected leader in this scaffold is a field-setter, not a node others answer more.

## Design: two layers (STANDARDS §4)
- **Natives (G26, role `native`):** N1 the result step in the winner's out-coupling (primary); N2 the confirmatory re-election (01-09 19:00:43 UTC, 9–0) as a negative control, where no new step is expected; N3 read-gated vs in-flight step; N4 EP step.
- **Replication (role `replication`):** the same role-step estimator wherever DQ6 names a designated agent with out-of-role data in the same unit: G12 (each debate's judge: out-coupling in its judged debate vs in the debates it did not judge, after H115's freeze) and G35 (each lead designer: out-coupling on its leader day vs its other days in the same room).

## Model
**From:** `physics-models/02-nonequilibrium-ising/` (kinetic Ising on the call clock; HH83's leader–follower mean field as the reading).

**Spins and inputs** (identical to H115; `scheme/callspins.py`): talk spin s_i(c) = ±1 per non-summary call; read-gated input x_ij(c) = 1 if j posted in i's room since i's previous call's t_call; in-flight input x^P_ij(c) = 1 if j posted during c's model call (t_call, t_first).

**Winner-focused event model (primary).** For an event at time T with designated agent w, windows pre = [t₀, T_g) and post = [T, T + L), with the guard band [T_g, T) dropped and L = T_g − t₀ (equal lengths). For every recipient j ≠ w and call c:
H_j(c) = h_{j,κ,side} + J_jj s_j(c⁻) + J_out x_jw(c) + ΔJ_out x_jw(c)·post + J_oth X_j,−w(c) + ΔJ_oth X_j,−w(c)·post + (the same four terms on in-flight inputs) + γ·wake,
with X_j,−w the number of senders other than w read at c. For the winner's own calls:
H_w(c) = h_{w,κ,side} + J_ww s_w(c⁻) + J_in X_w(c) + ΔJ_in X_w(c)·post + (in-flight terms) + γ·wake.
P(s = +1) = e^H / 2cosh H, fitted by penalized maximum likelihood (ridge 0.1 on intercepts, λ on coupling terms, chosen in the synthetic). Coefficients are in Ising units (half-logits).
- **ΔJ̄_out** = ΔJ_out: the step in the mean coupling J_jw from the winner to a reader, per read. HH354's Σ_j J_jw is (N − 1)·J_out; the threshold 0.05 applies to the per-reader step ΔJ_out.
- **ΔJ_in:** the step in the winner's per-sender response.
- **DiD:** ΔJ_out − ΔJ_oth removes a global coupling step (everyone answering more after the result).
- **Variant:** the additive in/out model (J_ij = α_i + β_j with a post-step on every α and β), mean ΔJ_jw.

**Entropy production (call-clock multipartite bound).** Calls are ordered in time; at each call c of agent i the system state changes only in s_i (s_i(c⁻) → s_i(c)); the others' states s_j are their latest call spins. Antisymmetric observables g_ij(c) = (s_i(c) − s_i(c⁻))·s_j(c) (model 02's multipartite form). Σ_mp = the held-out Newton bound of `infra/shared/ep_newton.py` (`ep_newton_heldout`, folds = 10-min blocks) on these g, in nats per call. Two sets: winner pairs (g_wj and g_jw, 18 observables) and all ordered pairs (90). ΔΣ = post − pre.

**What each picture predicts.**
| Picture | ΔJ_out | ΔJ_in | ΔJ_out − ΔJ^P_out | re-election (N2) | ΔΣ |
| --- | --- | --- | --- | --- | --- |
| **H116 (coupling step)** | > 0, beyond time placebos | ≈ 0 | > 0 | no step | > 0 |
| **R-field (leader sets a goal field only)** | ≈ 0 | ≈ 0 | — | no step | ≈ 0 |
| **R-attention (talk about the winner, H65)**: others mention and reply to the winner, but the reply is a co-response to the new goal | > 0 | ≈ 0 | ≈ 0 (in-flight steps as much) | no step | — |
| **R-global (the result energizes everyone)** | > 0 | > 0 | — | — | DiD ≈ 0 |

## Data scheme (`scheme/`)
- **`scheme/callspins.py`**: byte-identical copy of H115's (see H115 Notes).
- **`scheme/build.py`** → `data/processed/H116-election-coupling-step/<unit>/`: per-day call tables, X_R, X_P for G26 and the placebo days of #24, #25, #27 (regime I), G12 (debate windows) and G35 (room-days), `_provenance.json`. Codes only.
- **Event times (from DQ6, one timestamp each):** T* = 2026-01-05 19:35:22.59 UTC (`phase` = result, round 1); guard start T_g = 19:25:00 (the first ballot was 19:25:09, Known issue); T₂ = 2026-01-09 19:00:43.08 UTC (round-2 result), guard start 18:45:00 (DQ6 `t_valid_from` of the confirmatory vote).
- **Regimes covered:** I (G26, G24, G25, G27 placebos; G12), II (G35).

## Observables
*Written 2026-10-04 22:05 UTC.*
- **O1** ΔJ_out(17, T*) with a 10-min-block bootstrap SE; ΔJ_oth; DiD.
- **O2** ΔJ_in(17, T*).
- **O3** ΔJ^P_out (in-flight) and ΔJ_out − ΔJ^P_out.
- **O4** ΔΣ_mp (winner pairs; all pairs).
- **O5** ΔJ_out(17, T₂) (re-election).
- **O6 (replication)** role steps: G12 Δout_judge = J_out as judge − J_out as debater (same agent; per debate, pooled); G35 Δout_lead = J_out on leader day − J_out on the same agent's other days in the same room. DiD against the same contrast for non-designated agents.
- **Gauge:** H86 c_× (`taylor_c_shared`, `activity_trim`) for units 26, 12a, 35.

## Null / baseline
*Written 2026-10-04 22:05 UTC.*
- **N-time (primary placebo):** the same estimator with w = 17 at the same offset from the day start (the event is 93.8 min after the 01-05 start) on every other non-holdout regime-I day of #24–#27 where agent 17 has ≥ 30 calls in each window and the windows fit in the day's all-present span. The first days of #24, #25 and #27 are the kickoff-matched subset. One placebo per day.
- **N-agent:** the same T* with each other agent as w (9 placebos).
- **N-inflight:** the in-flight step ΔJ^P_out.
- **Synthetic (axis F, before real data):** kinetic Ising on the real 01-05 skeleton and update order with a planted step ΔJ_out ∈ {0, 0.05, 0.1, 0.25, 0.5, 1.0} at T*; power of the kill rule against the real time-placebo distribution; size at Δ = 0.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R-field (leader as field-setter only), R-attention (co-response to the new goal), R-global (everyone steps).
**Locked holdout used for confirmation:** none yet. Planned: NE37 (#47 → #48, held out: an operator designation of one focal agent). NE31 (#45) is blocked by H02's same-family run.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Ledger call-clock spins and reads (≥ 99.9% agreement); one DQ6 result timestamp; regime-I clock contested (H67). |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Real call order; stationarity within 83-min windows; untrimmed re-election windows (A0). |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | N1 inside time and skeleton nulls; time placebos alone anti-conservative (synthetic size 0.22), fixed by the skeleton null (0.06). |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | In-coupling flat as predicted; EP below resolution; the re-election control fails. |
| E interventional | predicts the change across a natural experiment | 1 | No coupling step at the election; a step at the re-election (not a designation). |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 2 | Synthetic on real skeletons: size 0.06 with both nulls; power 0.68 at Δ = 0.5, 0.96 at 1.0; ridge shrinkage quantified. |
| G ground truth | agrees with known structure | 1 | DQ6 event time and winner used; no signature at the designation. |
| H comparative | beats the named rivals | 1 | R-field fits the result; the re-election step is not R-global (others' step −0.06 ± 0.12). |
| I transfer | holds in other same-mode periods, including the holdout | 0 | No role step in G12 or G35; holdout not run. |

## Prediction
*Written 2026-10-04 22:05 UTC, before running any H116 statistic on real data.*

**What I had seen.** Cards H65, H29, H67, H40, H86 (headlines). H65: the elected leader (#26) is a content source (outflow percentile 0.89–1.00) and ranks 0.89 in replies received; H29: #26's leader's broadcast pull rose more than anyone's (regime I); H67: regime-I per-call read-out jump ≈ 0 (26: J₁\* 0.001 [−0.006, 0.009]). Structural facts only for H116: DQ6 event times and tallies (above); per-agent call counts and talk shares for #26 over the whole week (agent 17: 1,683 calls, talk share 0.11). No coupling, response or EP statistic.

**Power context (before the synthetic).** About 12 winner messages in an 83-min pre window, each read once by 9 agents, give ~110 exposed reader-calls per side. At a base talk probability of ~0.15 the SE of a per-side Ising coupling is ~0.13, so the step's SE is ~0.2. HH354's 0.05 is far below what one event can resolve. The synthetic gives the detectable step; a null result below it is "inconclusive", not "failed".

| ID | Prediction | Against (kill) | Credence |
| --- | --- | --- | --- |
| **N1 (primary)** | ΔJ_out(17, T*) ≥ 0.05 **and** above the 95th percentile of the time placebos (N-time). | **Kill (HH):** ΔJ_out(17, T*) not above the time-placebo 95th percentile, provided synthetic power at the observed-scale step is ≥ 0.8; otherwise inconclusive. | 0.3 |
| N1b | ΔJ_in(17, T*) inside the central 90% of time placebos (the in-coupling does not step). | outside | 0.7 |
| N1c | ΔJ_out(17, T*) above the 90th percentile of agent placebos (the winner, not everyone). | inside | 0.3 |
| N2 (negative control) | ΔJ_out(17, T₂) inside the central 90% of time placebos. | outside (a step at a re-confirmation would point to election excitement, not designation) | 0.75 |
| N3 (coupling, not field) | ΔJ_out − ΔJ^P_out > 0 (bootstrap 90% CI above 0). | ≤ 0 (R-attention / co-response) | 0.3 |
| N4 (EP) | ΔΣ_mp (winner pairs) above the 95th percentile of time placebos. | inside | 0.2 |
| **R (replication)** | Role steps are positive: G12 Δout_judge > 0 and G35 Δout_lead > 0, each with label-permutation p < 0.05. | ≤ 0 or p ≥ 0.05 in both (no designation coupling anywhere) | 0.35 |

**What would count against H116 as a whole:** N1's kill with power, together with no replication role step: designation in this village changes the field (what agents talk about), not who answers whom per call.

### Amendment A0 (2026-10-04 22:12 UTC, skeleton only, before any statistic)
On 01-09 one agent starts late, so the all-present span begins at 18:32 UTC and the pre window before the 18:45 guard would be 13 min. N2 therefore uses untrimmed windows from the calendar start: pre = [18:01:08, 18:45:00), post = [19:00:43, 19:44:35) (502 and 557 calls). Not post hoc: no outcome was computed.

### Synthetic result (axis F) and Amendment A1 (2026-10-04 22:25 UTC, after the synthetic, before any real-data H116 statistic)
Kinetic Ising on the real call skeletons of #24, #25, #26 and #27 (117,860 calls; real t_call, t_first, call modes; one room). Field = each agent's real week-level talk logit per call mode; J₀ = 0.02; self coupling 0.3; in #26 the couplings J_j,17 gain a step Δ at T*. 16 eligible time-placebo days (#24: 12-22, 23, 24, 26; #25: 12-29, 30; #27: 10 days). 50 worlds (`analysis/synthetic.py`; `data/processed/H116-election-coupling-step/synthetic/synthetic.json`).

| Planted Δ (Ising) | mean estimate (λ = 4) | SE | time-placebo rule alone | rule with the skeleton null (A1) |
| --- | --- | --- | --- | --- |
| 0 | 0.02 | 0.21 | 0.22 (anti-conservative) | 0.06 |
| 0.05 (HH354's test size) | 0.03 | 0.20 | 0.28 | 0.14 |
| 0.25 | 0.07 | 0.20 | 0.32 | 0.24 |
| 0.5 | 0.20 | 0.20 | 0.74 | 0.68 |
| 1.0 | 0.41 | 0.19 | 1.00 | 0.96 |

- **Power:** one event cannot resolve HH354's 0.05: power 0.14 at Δ = 0.05, 0.68 at 0.5, 0.96 at 1.0. A non-detection is "inconclusive" for Δ ≲ 0.6 Ising units.
- **Size:** the time-placebo rule alone fires in 22% of null worlds. With 16 placebos and an event day whose skeleton differs from theirs (01-05 is a kickoff day with more calls), the empirical 95th percentile is anti-conservative. An event-day field-only skeleton null restores the size (0.06).
- **Shrinkage:** the ridge attenuates the step (λ = 4: Δ = 1 → 0.41; λ = 1: → 0.65). Tests compare like with like, so this does not bias the rule, but magnitudes must come from a near-unpenalized fit.

**Amendment A1 (not post hoc):** (1) λ = 4 on coupling terms for all test statistics (SE 0.20 vs 0.31 at λ = 1). (2) N1's detection rule adds a second null: ΔJ_out must also exceed the 95th percentile of 200 field-only skeleton worlds on the real event day (each agent's real talk rate per call mode × side, J = 0). (3) Magnitudes are reported from a λ = 0.01 fit with Wald SEs. (4) N1's kill clause is read with the synthetic's power: no detection excludes Δ ≳ 0.75 (power ≥ 0.8 near Δ ≈ 0.7); smaller steps stay inconclusive. Predictions unchanged.

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G26](goalperiod-subhypotheses/G26/README.md) | native | failed | ΔJ_out(T*) +0.035 (pct 0.56 time, 0.71 skeleton); re-election +0.31 ± 0.21 (above all placebos) |
| [G12](goalperiod-subhypotheses/G12/README.md) | replication | failed | judge Δout −0.04 ± 0.10 (p 0.76) |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | failed | lead Δout −0.02 ± 0.11 (p 0.83) |

## Results
### Round 1 (2026-10-04): exploratory, non-holdout
Read rule vs ledger: 99.94–99.98% of calls agree (#24–#27, #12, #35). Code: `scheme/callspins.py`, `scheme/build.py`, `analysis/synthetic.py`, `run_g26.py`, `posthoc_n2.py`, `run_replication.py`; data `data/processed/H116-election-coupling-step/`. H86 gauge: c_× (activity_trim) 0.032 [0.005, 0.062] in unit 26 (φ_sh 0.17); the side-specific intercepts and the field-only skeleton null carry that field.

**Predictions scored (as written, read through A1):**
| ID | Prediction | Observed | Verdict |
| --- | --- | --- | --- |
| N1 | ΔJ_out ≥ 0.05 beyond time placebos (and skeleton, A1) | +0.035; pct 0.56 (time), 0.71 (skeleton); magnitude +0.09 ± 0.33 | not detected: kill fires at the powered scale (Δ ≳ 0.75); inconclusive at 0.05 |
| N1b | ΔJ_in inside the placebo band | −0.004 in [−0.15, +0.18] | consistent |
| N1c | winner above agent placebos (q90) | pct 0.56 | failed |
| N2 | no step at the re-election | +0.31 ± 0.21, above all 16 placebos | **failed** |
| N3 | read step > in-flight step | −0.02 ± 0.28 | failed |
| N4 | EP rises | ΔΣ_mp +0.002 nats/call, pct 0.69; bound ≤ 0 in both windows | failed (below resolution) |
| R | role steps in #12 and #35 | −0.04 ± 0.10 (p 0.76); −0.02 ± 0.11 (p 0.83) | failed |

**Reading.**
1. **The designation itself is not a coupling step.** In the 83 min after agent 17 won, the other nine agents did not talk more often after reading it. The interval excludes a step of 0.75 Ising units; it cannot exclude HH354's 0.05, which one event cannot resolve (synthetic power 0.14). Debate judges and daily lead designers, which are designations repeated 10 and 5 times, show no out-coupling step either (pooled SE 0.10).
2. **Influence followed the leader later, and around its activity.** H115's G26 replication ranks agent 17 the top talk source on 01-06, 01-07 and 01-09, and the 01-09 re-election window shows a step of +0.31 ± 0.21 (post hoc checks: above re-election-offset placebos and a skeleton null; read-gated). A re-confirmation is not a new designation, so the designation itself does not explain the step; what the leader's messages in that window did is open (H116-R1; no text was read). With 44 / 54 exposed reader-calls this is one thin window.
3. **Placebo calibration matters.** With 16 time placebos and an event on a kickoff day, the time-placebo rule alone has size 0.22 in the synthetic; the event-day skeleton null restores 0.06. Any single-event coupling-step claim needs both.
4. **EP at this scale is not measurable.** The held-out Newton bound on call-clock multipartite observables is ≤ 0 for 10 agents and ~1,500 calls per window.

**Scorecard (round 1).**
| Axis | Score | Evidence |
| --- | --- | --- |
| A mapping | 1 | Spins and reads from the ledger call clock (≥ 99.9% agreement); one result timestamp from DQ6; regime-I clock contested (H67). |
| B assumptions | 1 | Real call order and windows; stationarity within each 83-min window assumed; the re-election window needed untrimmed bounds (A0). |
| C adequacy | 1 | N1 inside both nulls; the time-placebo null alone is anti-conservative (synthetic size 0.22), fixed by the skeleton null (0.06). |
| D unfitted predictions | 1 | In-coupling flat as predicted; EP and the re-election control fail. |
| E interventional | 1 | The election is a dated intervention; no step at it; the re-election (not a designation) steps. |
| F identifiability | 2 | Synthetic on the real skeletons: size 0.06 with both nulls, power 0.68 at Δ = 0.5 and 0.96 at 1.0; shrinkage quantified. |
| G ground truth | 1 | DQ6 event times and winner; no coupling signature at the designation. |
| H comparative | 1 | R-field fits the first result (no coupling step); the re-election step is not R-global (others' step −0.06 ± 0.12 unpenalized). |
| I transfer | 0 | No role step in #12 or #35; holdout not run. |

**Claim that stands:** Winning the #26 election did not raise the per-call talk response to the winner within the same day (ΔJ_out = +0.09 ± 0.33 Ising units; a step ≥ 0.75 excluded), and debate judges and daily lead designers carry no role step in out-coupling (−0.04 ± 0.10, −0.02 ± 0.11). **Exclusions:** the 01-09 re-election step (pre-registered control failed; magnitude and robustness checks post hoc); EP (below resolution); HH354's 0.05 threshold (unpowered).

## Confirmatory (planned, not run)
`analysis/confirm.py`, frozen 2026-10-04 22:35 UTC after round 1 (SHA-256 `64f36b1cf7cf8e6f7dfa07415157232b9050d3b4a5d6306afd744510de06812c`).
- **Target:** NE37: pre = the focal agent's last active day of #47, post = #48 (2026-06-22), both held out. The focal agent's code comes from the coordinator; no held-out text is read.
- **C1 (the claim that stands):** the A1 detection rule does not fire and the unpenalized ΔJ_out < 0.75 Ising units. **C2:** ΔJ_in inside the central 90% of time placebos (consecutive non-holdout regime-III day pairs of #38–#42 and #44 with the same agent).
- **Reuse:** G47 and G48 were both run by H04 (Curie–Weiss, Hawkes and kick-response families; activity timing), with no kinetic-Ising-coupling run; H115's confirm uses #48 with a different statistic. Ledger family `kinetic_ising_couplings`, modality talk timing.

## Round 2 redirects
- **H116-R1. Activity, not title.** Model the leader's out-coupling as a function of its own announcement messages (directive vs ordinary, by DQ2 / stance labels) rather than of the designation time; test on G26 term days and the re-election window.
- **H116-R2. Pool designations.** A hierarchical role-step model over all non-holdout designations (G12 judges, G26, G35, G44 checkpoints) for a pooled Δ with an SE near 0.05, the size HH354 asked about.
- **H116-R3. Day-scale step.** Pre-register the step from the pre-result window of 01-05 to the term days 01-06..01-08, with kickoff-matched placebo weeks.
- **H116-R4. EP instrument.** The multipartite call-clock bound needs ≳ 10⁴ calls per window or fewer observables; size it on synthetic first.

## Notes
- 2026-10-04 22:05 UTC: `scheme/callspins.py` is a byte-identical copy of H115's (STANDARDS §8 asks for `infra/shared/`; shared files are out of scope this round; suggested in the report).
- 2026-10-04 22:40 UTC: `confirm.py` imports `scheme/callspins.py` (SHA-256 prefix `c40dbe842340a79a`, identical in H115 and H116) and `analysis/h116lib.py` (`cb06f29c3f79be52`); these are frozen with it. The confirm-only switch `callspins.ALLOW_HOLDOUT` is set in memory only after the guard passes.
