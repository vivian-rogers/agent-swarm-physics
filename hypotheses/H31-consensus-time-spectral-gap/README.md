# H31: Consensus time scales with the interaction graph's spectral gap

**Status:** exploratory round 1 done (2026-10-03). **The 1/λ₂ law is not supported as posed.**
- Gradual project consensus scales *sub-linearly*, τ ∝ λ₂^−0.37 [0.08, 0.55], and the slope-1 rule loses to a constant forecast out of sample.
- A pure field model is rejected for these events; the data cannot tell diffusion, voter and herding apart.
- About half of all consensus events are not gradual: they are frozen at the kickoff or happen as one-window waves.
- Content never converges; it diverges after every kickoff where anything is detected.
- The operator rule that survives is a constant: ≈ 4 active h, with an 80% interval of ≈ 1–18 h.
- The confirmatory script is written, not run. Predictions were written 2026-10-03, before any real-data run.
**Fields:** stat mech, sociophysics, info theory
**Origin:** HH115, with HH68 (`../hypohypotheses/HYPOHYPOTHESES.md`; `../promotion-shortlist.md`)
**Definitions used:**
- "Interaction (broadcast)", with a proposed named variant **interaction (seen, weighted)**: W_ij is the number of agent j's messages first seen by agent i, per active hour. "Seen" follows H18's call-start visibility rule; recipients come from `exposure`.
- "Agent state (categorical)", using H11's named variant **project/artifact strict**: H11's labels are imported unchanged.
- "Agent state (vector)", using H01's named variant **whitened statement mean**: per 30-min window, from `embeddings/agent_win30`, whitened per regime with d = 32.
- "Population N(t)": roster agents in the room.
- "Regime": each period sits in one regime, except #36.
- Active time: the shared-table convention in `infra/README.md`.
- New terms, proposed for DEFINITIONS.md: **consensus event**, **consensus time**, **exposure spectral gap λ₂** (variants below), **time-respecting DeGroot gap γ_tr**.

## Question
Does the time a swarm takes to reach consensus scale as 1/λ₂, where λ₂ is the algebraic connectivity of its exposure graph (HH68)? Rival scalings:
- N^a, the voter-model scaling (a ≈ 1 on a complete graph);
- the turn interval (herding waves);
- nothing at all: kickoffs or prompts set the time (field-driven).

The *check* is consensus times across goal periods and rooms, regressed against λ₂ and N, then prediction of held-out periods.

**Practical aim (usefulness-first batch):** a forecast rule. From the first day's communication logs, predict how long the swarm will take to coordinate, with an interval.

## Model
**From:** `physics-models/10-potts` (voter-model and Potts coarsening, with their consensus-time scalings) and graph diffusion (HH68). We use no separate graph-diffusion folder; general results go back to model 10.

**H31 variant.** Agents sit on a directed, weighted, time-varying exposure graph W_ij(t). Agent i's state changes only at its own turns, using the agent messages it has newly seen at that call start. Four dynamics are compared on the *same* real schedule:

| Model | Update at a reading turn of i (batch B of newly seen agent messages) | Consensus-time scaling |
| --- | --- | --- |
| **D (H31): diffusion / DeGroot, count-weighted** | dx_i/dt = Σ_j W_ij (x_j − x_i); continuous opinions, or adoption pressure ∝ the number of messages from adopters | τ ∝ 1/λ₂(L_w), with L_w = D − (W + Wᵀ)/2 |
| **A: DeGroot averaging at turns** | x_i ← (1 − α) x_i + α · mean_{m ∈ B} x_{s(m)}(t_m), with α = 0.5 | τ ∝ 1/γ_tr, the time-respecting gap. On a complete graph that is ≈ the turn interval, independent of N |
| **V: voter** | i copies the state carried by one random m ∈ B | τ ∝ N_eff / u (u = turn rate): ∝ N on a complete graph |
| **H: Potts herding wave** | i takes the batch's majority state with logit weight βJ (complex contagion) | τ ≈ the time for half the room to read the announcement, τ_wave. Abrupt rise |
| **F: field** | agents adopt at exogenous times (kickoff, human or operator message), with independent delays | τ independent of the graph; consensus locks to kicks |

In a broadcast room, W_ij ≈ r_j (j's message rate). So λ₂(L_w) grows with N × the message rate, and model D predicts that *bigger, chattier rooms converge faster*. V predicts the opposite (∝ N), and A and H predict no N dependence. This three-way split on the N axis is the rival design.

## Data scheme (`scheme/`)
`scheme/build.py` builds `data/processed/H31-consensus-time-spectral-gap/G<NN>/` for every non-holdout goal period that has H11 labels or embedding windows. It reuses shared tables and imports H11's and H18's code without modifying it. Holdout days are dropped with `calendar.holdout` and `common.holdout_mask` before anything is computed. `--allow-holdout` exists only for `analysis/confirm_holdout.py`.
- **Reading schedule** (`reads.parquet`).
  - For each `exposure` row (agent message m, recipient i ≠ sender, both roster agents), t_seen is i's first logged turn strictly after t_m. Turns are `actions` minus `pause` mirrors, plus `events_core` agent events, as in H18's `turn_times`.
  - t_upd is i's first turn after t_seen + 1 s: the output of the call that saw m.
  - Messages carry the sender's state at t_m.
  - Human and automated messages are fields (kicks), not graph edges.
- **Messages** (`msgs.parquet`): agent chat messages with time, sender, room, active time and mentions (`mentions_roster`).
- **Blocks:** a block is the agents in one room (room at the window midpoint, from `rooms_timeline`). Regime I is a single block (#general). Blocks need ≥ 3 roster agents.
- **Project states** (`states_project.parquet`): H11's `labels_project_w30` (and w15, w60 for robustness), imported. Carried forward per agent for up to L = 4 windows of active time.
- **Content alignment** (`alignment.parquet`): per block and 30-min window, A_b(w) = the mean pairwise cosine of whitened, unit-normalized agent vectors (`agent_win30`, regime whitener, d = 32). Needs ≥ 3 agents.
- **Active time:** active_offset_s + (t − win_start), from `calendar`.
- **Output size:** under 200 MB. No text anywhere.

## Candidate goal periods
- **Card candidates:** #19, #26, #31, #40 (consensus events named by HH115 and H11).
- **E-P (project) events:** all non-holdout periods where ≥ 50% of the H11 room-windows have ≥ 3 labeled agents. That is #17–#21, #24–#26, #30, #31, #33, #35–#42 and #44: 20 periods, 27 room blocks once the two rooms are counted.
- **E-C (content) events:** non-holdout periods #10–#44 (minus holdout) with embedding windows.
- **Within-period room contrast:** the two-room periods #35, #36, #37, #38, #39, #41, #42 and #44. Same goal and kickoff in both rooms, so this design controls the field.
- **#51:** not used in round 1. It is the private-role era, and H11 has no labels for it.

Per-period folders go in `goalperiod-subhypotheses/G<NN>/`.

## Observables
**Consensus events (defined by rule, before any outcome was looked at):**
- **E-P, project-share consensus** (W = 30 min; H11 merged labels, where 0 = "other" never counts).
  - **Carry-forward state:** σ_i(w) is i's most recent real label within the last 4 windows. N_lab(w) is the number of carried-forward labeled agents in the block; N_b(w) is the number of roster agents in the room.
  - **Consensus at w for project a:** n_a(w) ≥ max(3, ⌈N_b/3⌉) and x_a = n_a/N_lab ≥ 0.5, in w and in w + 1.
  - **Onset t₀:** the first window in which any agent in the block holds a.
  - **τ_P** = active time from t₀ to the consensus window (window midpoints), floored at W/2 = 0.25 h.
  - **Left-censored ("frozen"):** the criterion already holds at t₀, or in the block's first window with N_lab ≥ 3. Frozen events are counted but excluded from the τ fits.
  - **No consensus:** a project held by ≥ 2 agents that never meets the criterion. Counted only.
  - One event per (block, project). Bootstraps resample periods.
- **E-V, vote consensus.** #26 only, from H11's `votes.parquet`: first-person single-candidate declarations, carried forward.
  - **Onset:** the first runoff-word message.
  - **Consensus:** the eventual winner's declared share ≥ 0.5 among ≥ 3 declared agents.
  - **τ_V** = consensus − onset. The approval round, which ended in a tie, is right-censored.
  - n = 1, so this is descriptive.
- **E-C, content-alignment convergence**, per block and period.
  - **Fit:** A(t) = A∞ − ΔA·e^(−t/τ_C) over active hours from the block-period start. τ_C is on a log grid [0.25 h, 2T], weighted by pair count.
  - **"Convergence" event:** ΔA > 0, ΔBIC(exponential vs constant) ≥ 6, τ_C ≤ T, and ≥ 12 windows with ≥ 3 agents.
  - **"Divergence":** ΔA < 0 with ΔBIC ≥ 6. Counted, not a consensus.

**Predictors per block.** Computed on (i) the whole non-holdout block-period, the **primary** forecast input, and (ii) the 4 active hours starting at the event onset (event window, secondary). Units are 1/active hour unless stated.
- **λ₂^w,sym (primary):** the second eigenvalue of L = D − (W + Wᵀ)/2, with W the seen-weighted graph per active hour.
- **λ₂^w,dir:** the smallest nonzero Re λ of L_in = diag(W·1) − W.
- **λ₂^bin:** the normalized Laplacian of the binary symmetrized graph (dimensionless).
- **u·λ₂^rw:** the random-walk Laplacian I − D_in⁻¹W, times the median reading-turn rate u.
- **γ_tr (time-respecting):** the decay rate of disagreement under model A, simulated on the real reading sequence (α = 0.5; 8 random initial vectors; renormalized, so it is exact for the linear system with delays).
- **λ₂^ment:** λ₂^w,sym of the mention graph (j's message names i, so the edge runs j → i), the "addressed" variant.
- **N_b:** the median roster agents in the block.
- **u:** the median per-agent rate of reading turns (turns that see ≥ 1 new agent message).
- **τ_wave:** the median over agents of (t_seen − t) for a broadcast at time t, averaged over the block-period. This is the herding-wave timescale.
- **τ_Vsim:** the voter conditional time from one seed to 50%, by Monte Carlo on the real schedule (copy at every reading turn).

**Tests (per event class):**
- **T1 slope:** OLS of log τ on log(1/λ₂^w,sym), with a 95% cluster bootstrap over periods. The same is done for each secondary predictor.
- **T2 rival N^a:** log τ on log N_b.
- **T3 model comparison:** leave-one-period-out RMSE of log τ for:
  - M0, constant (field);
  - M_λ, log τ = c − log λ₂^w,sym with slope fixed at 1 (the H31 rule);
  - M_λfree, the same with slope free;
  - M_N, slope free on log N_b;
  - M_tr, slope 1 on 1/γ_tr;
  - M_V, slope 1 on τ_Vsim;
  - M_wave, slope 1 on τ_wave.
- **T4 kick locking (field rival):**
  - K = the fraction of E-P consensus windows within ≤ 2 windows (1 h) after a kick: the goal kickoff (the period's first window), or a human message in the block;
  - the placebo is 2000 random windows of the same block and day;
  - ratio K/K_placebo with a permutation p.
- **T5 abruptness (herding-wave rival):** the rise ρ, in windows from the last window with x_a < 0.25 to the first with x_a ≥ 0.5. Model H predicts ρ ≤ 1 in most events; D, A and V predict gradual rises that scale with their timescales.
- **T6 within-period room contrast:** sign of log(τ_small/τ_large) for two-room periods with events in both rooms.
  - D predicts sign(log(λ₂,large/λ₂,small));
  - V predicts τ_small < τ_large;
  - F predicts no difference.
- **T7 E-V:** #26 runoff τ_V against the E-P-calibrated M_λ prediction. Descriptive.

## Null / baseline
- **N0, field / constant:** τ independent of the graph (M0). This is the strongest practical null: "consensus takes about X hours, whatever the graph".
- **N1, placebo kicks:** random windows matched by block and day (T4).
- **N2, permutation of λ₂ across periods:** for the slope test, as a check on the bootstrap.
- **N3, synthetic truth models:** D, A, V, H and F run on the real schedules through the same observation model (label coverage, W = 30, carry-forward, detection rules). They give the expected slope pattern under each truth, and the power at the realized number of events.
- **Known confounds:**
  - λ₂^w,sym ∝ message volume, and volume co-varies with goal type;
  - N co-varies with regime and date;
  - τ is bounded by period length (3–17 days);
  - project labels measure attention, not work (H11);
  - mention-based edges are contaminated (H18 placebo);
  - the call-start visibility rule is doubtful in regime I (H18) and before NE09 (2025-12-20).

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** V (voter, τ ∝ N), A (DeGroot averaging, τ ∝ turn interval), H (Potts herding wave, τ ≈ τ_wave, abrupt), F (field: kick-locked, graph-independent).
**Locked holdout used for confirmation:** none yet. Targets: #29, #46, #47, #50 (E-P), plus #49 (E-C only). These avoid H11's confirmation targets (#22, #28, #45), whose dominant-share trajectories H11's confirm script will examine. `analysis/confirm_holdout.py` is written and dry-run, not run.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Exposure (`exposure` recipients plus H18 call-start visibility), turns, H11 project labels and whitened embeddings are all defined from fields; assumptions are listed. Not invariant: the visibility rule is doubtful in regime I and before NE09, labels measure attention rather than work, and λ₂^bin is ≈ N/(N−1) everywhere (rooms are complete broadcast graphs). |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Time-rescaling: W = 15 / 30 / 60 give slopes 0.60 / 0.37 / 0.42. Update order is taken from the real reading schedule (time-respecting variants). Stationarity of the graph within a period is not established: the event-window λ₂ slope is n.s. (0.25 [−0.25, 0.48]) while the period-level one is significant. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | The H31 rule (slope fixed at 1) loses to the constant in leave-one-period-out RMSE (1.25 vs 1.08). A free sub-linear slope beats it modestly (0.99, −8%; also −6% at W = 15 and −12% at W = 60). Gradual events are not kick-locked beyond placebo (0.27 vs 0.25), so they are not purely field-timed. |
| D unfitted predictions | unfitted statistics and the model's signature | 0 | The model's signatures failed: the slope is 0.37, not 1; content diverges instead of converging (0/35 blocks converge); rises are gradual rather than diffusive-exponential or abrupt in the predicted mix. The two-room sign agrees with D in 3/4 periods, which is too few to count. |
| E interventional | predicts the change across a natural experiment | 0 | No natural experiment was used. NE15's pre-split side is held out (#34). The #39 → #40 → #41 merge A-B-A is not tested. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Synthetic recovery on the real schedules: the primary λ₂^w,sym slope is attenuated (≈ 0.5 under the true diffusion model) and underpowered (P1 pass rate 0.13). Bulk predictors (core λ₂, reading rate) recover a slope near 1 with power 0.7–0.85. The field null is calibrated (5–10% false positives). The real-data result is not robust to the core-agent variant (0.25 [−0.40, 0.52]). |
| G ground truth | agrees with known structure | 1 | The #26 winner (DeepSeek-V3.2) and the runoff step (0.22 → ≥ 0.5 in 0.76 h, post hoc) match the dataset's summary and H11. #19 is frozen at the start, as H11 found. All 13 kickoff-frozen events sit on goal kickoffs. There is no ground truth for consensus timing. |
| H comparative | beats the named rivals | 1 | λ₂-based models beat the voter-on-schedule, herding-wave and fixed-slope γ_tr models by large margins (RMSE 2.06–2.84). The free-slope λ₂ is marginally best, but it ties N^a (1.09) and the constant (1.08) within noise. The rivals are not decisively beaten. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Holdout not run. Within-regime slopes have CIs that include 0 (regime I 0.99 [−0.05, 3.04], 8 periods; regime II/III 0.41 [−0.18, 1.03], 6 periods). |

## Prediction
*Written 2026-10-03, before running any analysis on real data.*

**What I had seen when writing this:**
- H11's label structure per period: windows, days, agents, rooms, labeled agent-windows, q, and the share of room-windows with ≥ 3 labeled agents. No shares, trajectories or timings.
- Message and action counts per goal period, including holdout periods (counts only).
- The round-1 results of H11, H12, H18, H05 and H24 as summarized in LOG.md. These include #26's runoff jump within one 30-min window, #19's frozen consensus, #31's herding waves, and that kickoffs raise content diversity (H12). They inform the priors below.

**Primary (P1, E-P, the H31 law):**
- **Supported** if the slope of log τ_P on log(1/λ₂^w,sym) (whole block-period graph) has a 95% cluster-bootstrap CI that excludes 0 and includes 1, *and* M_λ's leave-one-period-out RMSE is ≥ 5% below M0's.
- **Failed** if the slope is ≤ 0, or its CI excludes 1, or M_λ does no better than M0.
- **Inconclusive** otherwise, or if the synthetic power (P8) is < 0.5.
- **Credence:** 0.15 supported, 0.45 failed, 0.40 inconclusive.

**Secondary predictions:**

| ID | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| P2 | T2: the slope on log N_b has a CI that includes 0 (no voter-like ∝ N growth) | a > 0 with CI excluding 0 means voter-like; a < 0 with CI excluding 0 means D-like (bigger rooms faster) | 0.45 null; 0.35 a > 0; 0.20 a < 0 |
| P3 | T4: consensus locks to kicks, with K/K_placebo ≥ 1.5 and p < 0.05 (field rival partly right) | ratio ≈ 1 | 0.5 |
| P4 | T5: E-P consensus is mostly abrupt (ρ ≤ 1 window in ≥ 60% of uncensored events). That is the herding-wave signature | most rises gradual (≥ 2 windows) | 0.55 |
| P5 | E-C: the slope of log τ_C on log(1/γ_tr) has a CI that excludes 0 and includes 1, and M_tr beats M0 in leave-one-period-out RMSE | as for P1 | 0.15 |
| P6 | T6: in two-room periods with events in both rooms, the sign of log(τ_small/τ_large) agrees with model D in ≥ 75% of pairs | ≤ 50% agreement; V's sign wins | 0.30 |
| P7 | Counts: ≥ 15 uncensored E-P events, ≥ 5 frozen, ≥ 8 E-C convergence events | fewer, which leaves the test underpowered | 0.6 / 0.5 / 0.5 |
| P8 | Synthetic (axis F): with the realized events and predictor spread, the power to detect slope 1 vs 0 under truth D is ≥ 0.5 for E-P | power < 0.5 means P1 cannot pass | 0.4 |
| P9 | Magnitudes: median τ_P is 0.5–4 active h (herding-wave speed); median τ_C is 2–15 active h (days, per H12 and H20) | — | 0.6 / 0.5 |
| P10 | #26 votes: τ_V ≤ 1 h after the runoff onset, faster than the M_λ prediction calibrated on E-P (a decision field, not diffusion) | τ_V within the M_λ 80% interval | 0.6 |

**Prior, stated plainly:** consensus timing in the village is mostly set by task structure and announcements: shared repos created, deadlines, kickoffs (H11's herding waves; #18's last-day convergence). Rooms are near-complete broadcast graphs, so λ₂ varies across blocks mainly through message volume and N. I expect the spectral gap to carry little information beyond a constant, and the forecast rule to end up close to "constant ± spread". The synthetic run will say whether a scaling could have been detected at all.

**Multiplicity:** one primary test (P1). The five secondary predictors are reported with Holm correction across predictors within each event class. Per-period verdicts are descriptive.

**Forecast-rule protocol (frozen after round 1):** choose the model with the lowest exploration leave-one-period-out RMSE among M0, M_λ, M_tr, M_V, M_wave and M_N. Its intercept is calibrated on all exploration events. The prediction interval comes from the leave-one-period-out residual quantiles (10% and 90%). Confirmation (`analysis/confirm_holdout.py`):
- **Primary:** on the targets' uncensored events, the frozen rule's log-RMSE beats the frozen constant rule's.
- **Secondary:** ≥ 70% of target events fall inside the 80% interval.

### Synthetic validation (axis F)
*Run 2026-10-03, after the predictions above and before any real-data event detection.* Script: `analysis/synthetic.py`; output: `data/processed/H31-consensus-time-spectral-gap/synthetic/`. It used label *coverage* per block (structure) but no label timing or alignment values.

- **S0, generic two- and three-cluster graphs with Poisson schedules.**
  - The time-respecting gap tracks the random-walk spectral gap × reading rate: corr(log γ_tr, log u·λ₂^rw) = 0.97.
  - Count-contagion consensus time scales as λ₂^w,sym to the power −0.62 (50%) or −0.65 (90%), not −1. The bridge only limits the rate once it is weak.
- **S2, five truth models on the 28 real E-P block schedules** (period label coverage, W = 30, carry-forward, the card's rule; one uncensored event per block; 150 synthetic datasets).

  | Truth | Slope on log(1/λ₂^w,sym) (median) | P1 passes | Slope, core λ₂ | Slope, u·λ₂^rw | Slope, γ_tr | Slope, log N | Best LOPO model (share) |
  | --- | --- | --- | --- | --- | --- | --- | --- |
  | D count contagion | 0.52 | 0.13 | 0.75 (P1-type pass 0.68) | 0.85 (0.85) | 0.12 | −0.90 | u·λ₂^rw 0.53, core λ₂ 0.34, M0 0.01 |
  | A fraction contagion | 0.52 | 0.13 | 0.65 | 0.75 (0.72) | 0.13 | −0.84 | u·λ₂^rw 0.57; M0 0.09 |
  | V voter | 0.29 | 0.00 | 0.52 | 0.57 | 0.10 | −0.49 | u·λ₂^rw 0.49; M0 0.31 |
  | H herding wave (55% frozen) | 0.40 | 0.09 | 0.35 | 0.45 | 0.17 | −0.41 | M0 0.47; λ₂ 0.25 |
  | F field | 0.03 (CI excludes 0 in 5%) | 0.00 | 0.06 | 0.10 | 0.03 | −0.22 | M0 0.6–0.7, M_N 0.2–0.4 |

  - **Reading of S2.** λ₂^w,sym is a weakest-link statistic: one barely active agent sets it. 50% consensus is a bulk property, so even under the true diffusion model the primary slope comes out attenuated (≈ 0.5), and P1's pass rate is 0.13. **P8 fails, so by the card rule P1 cannot pass.** The bulk predictors (core-agent λ₂, u·λ₂^rw ≈ the reading rate) recover a slope near 1 with power 0.7–0.85 under D and A. The time-respecting gap γ_tr (α = 0.5) does not: it is set by the slowest agent too.
  - **Leave-one-period-out model choice discriminates well:** a graph model wins in ≥ 90% of datasets under D and A, and M0 wins 60–70% under F.
  - **The N slope is negative under every truth,** including the voter, because N is confounded with reading rate across regimes (regime-I rooms are bigger and read faster). **T2 cannot identify the voter scaling.**
  - The bootstrap's false-positive rate under F is 5–10% (slightly anti-conservative).
- **S3, content:** DeGroot vectors on the real schedules (α_true = 0.0056), with measurement noise σ.
  - At σ = 0.5, convergence is detected in 81% of block runs. The slope of log τ_C on log(1/γ_tr) is ≈ 0.30 (CI excludes 0 in 85%, includes 1 in 0%).
  - At σ = 1.0, convergence is detected in only 9%.
  - **P5's "CI includes 1" clause cannot pass even under true DeGroot.** The calibrated benchmark is a positive slope of about 0.3.

**Amendments (all before any real-data event detection):**
1. *2026-10-03, before outcomes.* A **core-agent** robustness variant of every predictor: agents present in the room in ≥ 50% of the block-period's windows (`h31lib.core_agents`).
2. *2026-10-03, after the synthetic run.*
   - Added **M_ul2_rw** (slope 1 on 1/(u·λ₂^rw)) and **M_λcore** (slope 1 on 1/λ₂^w,sym, core) to the leave-one-period-out comparison and to the forecast-rule candidates.
   - P1 and P5 are reported literally *and* against the calibrated synthetic benchmarks (slope ≈ 0.5 for λ₂^w,sym under D; ≈ 0.3 for γ_tr under DeGroot content).
   - T2 is reported as descriptive only.

## Results by goal period
Per-period verdicts are descriptive. "Supported" or "failed" says whether the H31 rule, fitted on the *other* periods, beat the constant forecast for this period's gradual events (or, for #26, whether τ_V fell inside its 80% interval). Notation: E-P events are counted as frozen at kickoff / instant / gradual; τ is in active hours; E-C gives the content kind.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G10](goalperiod-subhypotheses/G10/README.md), [G12](goalperiod-subhypotheses/G12/README.md) | E-C only | descriptive | content divergence (τ 1.0 h, 4.6 h) |
| [G11](goalperiod-subhypotheses/G11/README.md), [G13](goalperiod-subhypotheses/G13/README.md), [G16](goalperiod-subhypotheses/G16/README.md), [G23](goalperiod-subhypotheses/G23/README.md), [G27](goalperiod-subhypotheses/G27/README.md) | E-C only | descriptive | content: no trend |
| [G17](goalperiod-subhypotheses/G17/README.md) | E-P + E-C | failed | 0/2/1; τ 2.5 |
| [G18](goalperiod-subhypotheses/G18/README.md) | E-P + E-C | supported | 1/5/1; τ 1.0. Five one-window waves |
| [G19](goalperiod-subhypotheses/G19/README.md) | card candidate | supported | 1/1/1; τ 18.5 (lowest-λ₂ regime-I room); frozen build repo as predicted; content divergence 23 h |
| [G20](goalperiod-subhypotheses/G20/README.md) | E-P + E-C | failed | 0/0/2; τ 4.5, 8.0 |
| [G21](goalperiod-subhypotheses/G21/README.md) | E-P + E-C | failed | 0/1/2; τ 2.0, 3.0; content divergence 0.7 h |
| [G24](goalperiod-subhypotheses/G24/README.md) | E-P + E-C | descriptive | no consensus |
| [G25](goalperiod-subhypotheses/G25/README.md) | E-P + E-C | failed | 0/1/2; τ 1.0, 6.0 |
| [G26](goalperiod-subhypotheses/G26/README.md) | card candidate (E-V) | failed | 1/6/0. E-V τ_V = 12.5 h by rule (onset fired at the period start), outside the M_λ 80% interval [0.19, 5.4]; post hoc runoff rise 0.76 h |
| [G30](goalperiod-subhypotheses/G30/README.md) | E-P + E-C | failed | 1/0/1; τ 5.0; content divergence 0.4 h |
| [G31](goalperiod-subhypotheses/G31/README.md) | card candidate | failed | 0/0/5; τ 1.0, 1.0, 3.0, 3.5, 13.5 (successive waves, gradual by the rule) |
| [G33](goalperiod-subhypotheses/G33/README.md) | E-P + E-C | descriptive | 1/1/0 |
| [G35](goalperiod-subhypotheses/G35/README.md) | two rooms | descriptive | both rooms frozen at kickoff |
| [G36](goalperiod-subhypotheses/G36/README.md) | two rooms | failed | #best 1/0/2 (τ 6.0, 8.6); #rest 0/0/1 (τ 0.5). T6 agrees with D |
| [G37](goalperiod-subhypotheses/G37/README.md) | two rooms | failed | #best τ 10.1; #rest τ 2.0, 3.5, 18.1, 20.1. T6 agrees with D |
| [G38](goalperiod-subhypotheses/G38/README.md) | two rooms | supported | #best τ 19.6 (λ₂ 1.6); #rest τ 1.0–10.1. T6 agrees with D (ratio 4.6 vs 10.8 predicted) |
| [G39](goalperiod-subhypotheses/G39/README.md) | two rooms | descriptive | no consensus (own worlds); content divergence |
| [G40](goalperiod-subhypotheses/G40/README.md) | card candidate | descriptive | hub frozen at kickoff, as predicted; content divergence 13.6 h |
| [G41](goalperiod-subhypotheses/G41/README.md) | two rooms | failed | #rest τ 4.0, 13.5 |
| [G42](goalperiod-subhypotheses/G42/README.md) | two rooms | supported | #best τ 8.0; content divergence in both rooms |
| [G44](goalperiod-subhypotheses/G44/README.md) | two rooms | failed | #best τ 0.5, #rest τ 4.6. T6 agrees with V, not D |

## Results
*Exploratory round 1, 2026-10-03; non-holdout periods #10–#44 only.*
- **Code:** `scheme/build.py`; `analysis/h31lib.py`, `predictors.py`, `synthetic.py`, `explore.py`, `robustness.py` (post hoc), `period_folders.py`, `figures.py`, `confirm_holdout.py`.
- **Data:** `data/processed/H31-consensus-time-spectral-gap/`: `predictors_period.parquet`, `events_ep_w{15,30,60}.parquet`, `events_ec.parquet`, `ev26.json`, `cross_period_w*.json`, `robustness_w30.json`, `frozen_rule.json`, `synthetic/`.
- **One-page figure summary:** [`figures/H31_round1_summary.pdf`](figures/H31_round1_summary.pdf). Also [`figures/summary_obs.pdf`](figures/summary_obs.pdf) and [`figures/synthetic_validation.pdf`](figures/synthetic_validation.pdf).

**Events.**
- **E-P:** 144 projects in 28 eligible room blocks (20 periods). 63 reached consensus:
  - 13 were **frozen at the kickoff**: already shared in the first window, so all are kick-locked by construction;
  - 17 were **instant**: the criterion was met in the very window the project first appeared, mid-period. These are one-window herding waves, and only 4/17 are kick-locked;
  - 33 were **gradual** (14 periods, 18 blocks), with median τ_P = 4.5 active h (80%: 1.0–17 h) and a median rise of 3 windows.

  The card's rule counts frozen and instant events together as left-censored (30). 81 projects held by ≥ 2 agents never reached consensus.
- **E-C:** 35 blocks. **0 convergence**, 12 divergence, 23 no trend. Where content moves, alignment is highest at the kickoff (median A₀ 0.64) and relaxes to A∞ ≈ 0.29 with τ ≈ 4.4 h (80%: 0.8–22 h).
- **E-V (#26):**
  - The pre-registered onset (the first runoff-word message) fired at the period start, so τ_V = 12.5 h.
  - Post hoc, the winner's declared share rose from 0.22 to ≥ 0.5 within 0.76 h, then to 0.8.
  - The winner was DeepSeek-V3.2.

**Outcome vs prediction**

| Prediction | Outcome | Verdict |
| --- | --- | --- |
| P1 (primary): slope of log τ_P on log(1/λ₂^w,sym) has a CI that includes 1 and excludes 0, and M_λ beats M0 by ≥ 5% (leave-one-period-out) | slope 0.37 [0.08, 0.55], permutation p = 0.039; M_λ RMSE 1.25 vs M0 1.08 (−16%) | **Failed** (literal). *Calibrated:* the slope lies inside the synthetic range of every coupled truth (D, A 0.34–0.69; H 0.18–0.67; V 0.12–0.51) and outside the field truth's (−0.09 to 0.16). P8 had already ruled out a pass |
| P2: N slope CI includes 0 | −0.51 [−1.38, 0.72] | Holds; descriptive only, since the synthetic shows T2 is not identifiable |
| P3: kick-locking ratio ≥ 1.5, p < 0.05 | K 0.41 vs placebo 0.25, ratio 1.67, p = 0.002. But kickoff-frozen events are 13/13 locked, gradual events 0.27 and instant events 0.24 (≈ placebo) | **Supported literally; trivial.** The field sets the *initial* consensus; mid-period consensus is not timed by human messages |
| P4: ≥ 60% of gradual events abrupt (ρ ≤ 1) | 13% (median ρ = 3); 45% if instant events count as abrupt | **Failed.** The mix is bimodal: one-window waves plus multi-hour gradual approaches |
| P5: content slope on 1/γ_tr | no convergence events at all | **Untestable**; content does the opposite of consensus |
| P6: two-room sign agrees with D in ≥ 75% | 3/4 (#36, #37, #38 agree; #44 agrees with V). At W = 15 and W = 60: 2/3 | **Met at the threshold;** weak (n = 4) |
| P7: ≥ 15 gradual E-P, ≥ 5 frozen, ≥ 8 E-C convergence | 33 / 30 / 0 | Two of three met |
| P8: synthetic power ≥ 0.5 | 0.13 for the primary statistic | **Failed** (the primary statistic is a weakest-link quantity) |
| P9: median τ_P in 0.5–4 h; τ_C in 2–15 h | 4.5 h; no τ_C (divergence τ 4.4 h) | Failed narrowly / n/a |
| P10: τ_V ≤ 1 h after the runoff onset | 12.5 h by rule; 0.76 h rise post hoc | **Failed** (literal); the post hoc step fits the spirit |

**Secondary predictors** (period-level slopes on log(1/x); Holm across the five):
- λ₂^w,dir: 0.36 [0.01, 0.56], p_Holm 0.15.
- γ_tr: 0.41 [0.02, 0.69], p_Holm 0.05.
- u·λ₂^rw: 0.40 [−0.35, 0.70], p_Holm 0.42.
- λ₂^ment: 0.17 [−0.11, 0.28], p_Holm 0.42.
- λ₂^bin: −0.8, uninformative (≈ N/(N−1) everywhere).
- Event-window λ₂^w,sym: 0.25 [−0.25, 0.48].
- Core-agent λ₂^w,sym: 0.25 [−0.40, 0.52].

**Robustness of the sub-linear slope** (post hoc, `robustness_w30.json`):

| Variant | Slope [95% CI] |
| --- | --- |
| + regime fixed effect | 0.53 [0.05, 1.09] |
| + log period length | 0.35 [0.03, 0.57] |
| + log N | 0.55 [0.14, 1.04] |
| + onset position | 0.32 [0.09, 0.54] |
| one point per block | 0.39 [0.03, 0.61] |
| leave-one-period-out range | 0.34–0.42 |
| excluding pre-NE09 periods (#17–#21) | 0.34 [−0.04, 0.52] |
| regime I only | 0.99 [−0.05, 3.04] |
| regime II/III only | 0.41 [−0.18, 1.03] |
| W = 15 | 0.60 [0.23, 1.14] |
| W = 60 | 0.42 [0.23, 0.73] |

**Synthesis**
1. **What the spectral gap measures here.** Rooms are complete broadcast graphs, so the binary λ₂ carries nothing. The weighted λ₂^w,sym tracks message volume (corr 0.87 with log message rate across blocks) and is pulled down by peripheral agents.
   - Post hoc, the activity clock alone does not predict τ: log(1/message rate) gives 0.32 [−0.29, 0.59].
   - The *structural* part, log(message rate / λ₂), does: 0.74 [0.16, 1.19], fitted jointly with the clock (0.17, n.s.).
   - Gradual consensus is slower in rooms whose exposure is uneven (one or more poorly connected agents: #19, #38 #best, #37 #best). The effect is sub-linear and post hoc.
2. **Three kinds of consensus, not one.**
   - About a fifth of consensus is **set by the kickoff**: field-frozen.
   - About a quarter arrives as **one-window waves** with no human trigger. Their share is higher in better-connected rooms (r = 0.49 across 24 blocks, confounded with regime I).
   - About half are **gradual over hours**, with τ ∝ λ₂^−0.37.

   No single 1/λ₂ law covers them. The herding-wave and voter models run on the real schedule miss τ by an order of magnitude: they predict minutes, while the gradual events take hours.
3. **Content never forms a consensus.** By raw 30-min mean pairwise cosine, the kickoff imposes alignment and the swarm dissolves it within hours.
   - It fits H24's "aligned from the first hour".
   - It is not directly comparable with H12's participation ratio (kickoffs raise diversity) or with H24's residual-alignment ramp in #21 (here #21 decays within 0.7 h). Those are different statistics (dimensionality; goal-field-removed alignment), and reconciling them is open.
4. **Forecast rule (frozen for confirmation; `analysis/frozen_rule.json`).**
   - Leave-one-period-out picks the **constant**: from a project's first appearance to majority, ≈ 4.1 active h, 80% interval ≈ 0.9–18 h (×/÷ 4.4).
   - It should be read together with two base rates: about 20% of consensus is already in place at the kickoff, and about 25% arrives within one 30-min window.
   - A post hoc modulation, τ ≈ 14 h · (λ₂^w,sym)^−0.37 (λ₂ per active hour), cuts the leave-one-period-out error by 8%. Across the observed λ₂ range (1.6–98/h) it shifts the forecast by a factor of about 4.6.
   - Both are frozen for the holdout: C1, the pre-registered slope-1 rule; C1b, the post hoc free slope.
5. **Heterogeneity.**
   - Regime I periods (#17–#31): higher λ₂, more instant waves, shorter gradual τ (median ≈ 3 h).
   - Regime II/III two-room periods: the small #best rooms often have one low-connectivity agent and the slowest consensus (#38 #best 19.6 h; #37 #best 10.1 h). That is the D sign in the room contrast, opposite to the voter's.

**Caveats**
- **Power and multiplicity.** 33 gradual events from 14 periods; the effective n is the 18 blocks. Seven predictors × three event classes × three window sizes were examined, with one primary test (P1), and it failed literally. The positive sub-linear slope is p ≈ 0.04 by permutation and survives the covariates above, but not the core-agent variant, the event-window variant, the pre-NE09 exclusion or the within-regime splits. Treat it as a lead, not a finding.
- **Confounds.** λ₂, message volume, N and regime co-vary. The "structure" decomposition is post hoc. τ is bounded by period length, though including it changes little.
- **Event definitions.**
  - Consensus is "≥ 50% of labeled agents on the same project for 2 windows"; labels are attention (artifact mentions), not work.
  - The left-censoring rule lumps kickoff-frozen and instant events together. The split is post hoc.
  - The #26 onset rule fired at the period start, as H11's did; it was not amended.
- **Visibility.** The call-start rule is doubtful in regime I and before NE09 (H18 placebo). Mention edges are contaminated (H18).
- **Content.** The whitened 32-d statement mean at 30-min resolution is noisy (S3: detection needs σ ≲ 0.5). A one-embedding-model result.
- **Synthetic truths are stylized.** The parameters were set to give τ of a few hours; a voter with a different copy rate would scale differently.

**Amendments made after seeing results (all flagged; the pre-registered rules were not changed):**
- the instant/frozen split;
- the activity-clock decomposition;
- the regime, period-length, N, onset-position and block-level controls;
- the E-V post hoc rise;
- the post hoc free-slope forecast rule (C1b);
- the "E-C divergence" description.

**Next steps**
1. Run `analysis/confirm_holdout.py` on #29, #46, #47, #49 and #50 after sign-off. C1 and C1b go against the constant; C2 checks interval calibration.
2. A pair-level test of the "uneven exposure" lead: within a room, do poorly connected agents adopt later (agent-level time-to-adopt vs in-strength)? This tests the mechanism directly and has far more data than period-level slopes.
3. Instant waves: what triggers them (a message carrying the project's link, seen by ≥ 3 agents in one call cycle?). Use `artifact_mentions` with chat as the source.
4. Use the #39 → #40 → #41 merge A-B-A (λ₂ jumps when rooms merge) as an interventional test (axis E).
5. Content: replace the 30-min statement mean with day-level or topic-cluster states, and test whether the post-kickoff decay time tracks λ₂ (post hoc slope +0.86 [−0.10, 1.49], 12 events).

## Notes
- **From H53 (2026-10-04):** the #40 "kickoff-frozen" hub was link-seeded 2.4 min into the kickoff and drew an 8-agent wave (0.5 predicted, p = 0.0004). Some "frozen" events are first-link waves inside the first window.
- **From DQ6 (2026-10-04): E-V measured the 01-09 re-election, not the runoff.** The keyword onset fired at 18:02 on 01-05 and the consensus time landed on 01-09 at 18:46. The actual runoff opened at 19:32:19 UTC on 01-05 and ended 7–1–0 within about 100 s. That agrees with the post-hoc 0.76-h rise being an upper bound. Redo E-V per election round with `ground_truth_labels`.
- 2026-10-03: promoted from HH115 by Vivian (usefulness-first batch, wave 1). Round 1 started; card predictions written before any real-data run.
- 2026-10-03: synthetic validation run and Amendments 1–2 recorded before any real-data event detection. Per-period predictions (`G<NN>/README.md`) written before the real-data run, using only outcome-free predictors.
- 2026-10-03: round 1 run (W = 30 primary; W = 15 and 60 robustness), post hoc analyses flagged, forecast rule frozen (`analysis/frozen_rule.json`), confirmatory script dry-run on stand-ins #30, #39, #41, #42 and #44.
- 2026-10-03, **data quirk for H11's owner:** H11's `modal()` breaks ties with `group_by` without `maintain_order`. Rebuilding #30's labels reproduced 99.1% of them; 4 of 439 agent-windows flipped between two tied projects. H31's confirm script rebuilds labels with the same code, so this noise also applies there.
