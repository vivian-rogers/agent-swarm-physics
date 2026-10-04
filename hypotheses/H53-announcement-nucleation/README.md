# H53: Herding is announcement-seeded nucleation

**Status:** exploratory round 1 done (2026-10-04). **Failed as posed: herding is announcement-seeded, but the call clock does not set wave size.** Adoptions of a project jump about 20-fold at its first chat link (F1 22.5; 33 for new projects, 3.8 for carried-over ones), stay in the poster's room (other-room ratio 0.12) and almost never happen without the link in context (1.5%). But agents who read the link within one call cycle adopt no more often than later readers (RR_timely 1.06 [0.93, 1.22]; 726 adoptions, 928 seeds, 23 periods), the receptive count adds nothing to held-out wave-size prediction (M_R − M0 −1.7 nats), and the project's current share is the only rival that predicts herding (AUC 0.72 vs 0.46 for R). Poster status adds nothing once period intercepts are partially pooled. The call clock sets wave size only for deadline-bound calls: in the #26 runoff (100-s window) ballots = readers within the window (8 = 8), and 14/17 ballots in two rounds were cast by the reading call itself. Synthetic validation on the real schedules: the agent-level test recovers a planted ×4 receptive effect in 95–100% of runs with 0–10% false positives; the seed-level comparison has no power. Predictions were written 2026-10-04 before any outcome was computed; `analysis/confirm.py` is written and dry-run, not run.
**Fields:** stat mech, sociophysics, info theory
**Literature:** no paper in `literature/` covers announcement-triggered adoption directly; the nearest is `literature/pinero-2025-neutral-theory-cooperative-dynamics.md` (frequency-dependent joining). Classical background named, not filed: nucleation (a critical nucleus seeded by a local field pulse), Bass diffusion (innovation vs imitation), threshold and cascade models (Granovetter; Watts).
**Definitions used (physics-models/DEFINITIONS.md):** "Agent state (categorical, project/artifact strict)" (H11 variant, from shared `project_states`); "Exposure (turn read-out)" (H08) as implemented by the context ledger; "Herding onset (project-share step)" (H27) and "Consensus event (project share)" (H31), read-only, for ground truth; "Population N(t)"; "Regime". New named variants proposed for DEFINITIONS.md (not edited here; outside H53's scope): **seed (first chat link)**, **adoption (project label, H53)**, **wave size (H53, 2 h)**, **call cycle (agent median)**, **receptive count (H53)**, all defined under Data scheme and Observables.
**From:** HH168 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/10-potts/` (kinetic Potts with read-out-gated updates), `physics-models/03-contagion/` (field vs imitation; the shared-field pitfall)
**Data inputs (shared tables first):** DQ1 `call_windows`, `context_ledger_items`, `context_ledger_turns`; `project_states` (deterministic H11 labels); `artifacts`, `artifact_mentions` (link messages, codes only); DQ2 `reply_graph`; DQ4 `work_commits`; DQ6 `ground_truth_labels` (#26 rounds); `kicks_classified`, `period_units`, `rooms_timeline`, `calendar`, `roster`. Read-only cross-checks: H27 `onsets_round1.parquet`, H31 `events_ep_w30.parquet`.

## Standards (2026-10-04)
*Documentation pass against `STANDARDS.md`. No analysis was re-run. H53 has no round-1b section; round 1 already ran on the corrected inputs.*

**Question served:** Q5. The card tests whether an operator can size a pile-on by timing an announcement to the call clock. Q1 second: adoption is gated by reading the link.

| Impostor | Relevant? | How it was handled | Status |
| --- | --- | --- | --- |
| Scheduler field | partly | Active-time horizons; RR_timely is seed-stratified with pre-seed call and talk controls and an agent fixed-effect variant (O4). The activity null W0 runs on the real call schedules. Late readers' deficit is explained by prior inactivity. | removed |
| Exogenous field (kickoff/goal/operator) | yes | Seed-locked and pre-ramp field worlds simulated (WF0, WFpre); F1 step 22.5; F2 other-room ratio 0.12 on 301 multi-room seeds; `kick_near` flag. One-room periods cannot separate a seed-locked field from read-out triggering (Caveats). | partly |
| Shared model priors | no | Project adoption with a status rival; no family or content claim. | n/a |
| Contemporaneous convergence | yes | F3: 1.5% of adopters had no link to the project in context before adopting; F2 other-room agents adopt at 0.12×. Adoption without reading is rare. | removed |

**Inputs:** round 1 uses the context ledger, shared deterministic `project_states`, DQ2 `reply_graph`, the DQ4 work ledger and DQ6 #26 rounds. It never reads `activity_bins` or `outages`. Still old: none of the listed inputs. Embeddings and failures are not inputs.

**Two layers:** 26 replication folders (15 descriptive). Native tests: 4 (`G26` and `G31` mixed; `G30` and `G40` failed).

**Confirm script:** `analysis/confirm.py` exists, frozen and dry-run, built on the corrected inputs (C1–C5). No re-freeze needed.

## Question
Is the size of a herding wave set by the receptive fraction: the number of agents whose next model call falls within one cycle after the seeding link, rather than network position or the poster's status?

Context (cross-hypothesis; H28 is cited throughout). Pile-ons follow a chat link to the project (H27, post hoc: 11/21 onsets within 30 min, OR 11.6); about a quarter of consensus events are one-window waves (H31: 17 instant events); herding onto shared artifacts is the default (H11, 11/14 weeks); responses wait for the recipient's next model call (H08). But H28 found that links mark attention bursts (future links predict switches better than past ones; naive agents switch at 3.3× baseline in the hour before their first visible link), H06 found free-week projects mostly private, and H34 found that a shared field looks like branching. H53 asks whether the *timing* of each agent's read-out of the seed, relative to its commitments, sets the wave.

**Operator lever if true:** time announcements to the call clock (post when many uncommitted agents are about to start a call).

## Design: two layers (Vivian, 2026-10-04; see `infra/data-quality/QUEUE.md`)
- **Replication:** the common estimator on every eligible goal period (comparable phase-diagram points). Period README role: `replication`.
- **Period-native tests:** 4 goal periods whose setup gives special leverage, each with its own observable, null and dated prediction. Period README role: `native`.
  - **#26** (election; DQ6 ballots): the three voting rounds are seeds with a known, timestamped response (ballots). Tests read-out gating of the wave directly, and a *scheduled* round (01-09) gives a clock-driven shared-field rival.
  - **#31** (free week; H11's waves vs H06's private projects): which seeds herd in a week where most projects stay private.
  - **#30** (one shared park repo re-linked many times; H27's four "returns"): re-announcements of the *same* project, so project attractiveness is held fixed.
  - **#40** (a hub set by the goal, frozen at the kickoff per H31): the negative control, herding that is field-frozen, not nucleated.

## Model
**From:** `physics-models/10-potts/` (kinetic Potts, read-out-gated updates) and `physics-models/03-contagion/` (field vs imitation).

**H53 variant: nucleation by a decaying read-out pulse.** σ_i ∈ {0 (other / no project), 1..q (projects)}; agents update only at their own model calls (H08). A seed is the first chat link to project X; it is a local field pulse on X for the agents in the poster's room. At agent i's reading call (the first call whose context contains the seed; DQ1 ledger), with message age a_i = t_call − t_seed,

P(σ_i → X at its reading call) = 1 − exp(−A_X · u_i · g(a_i / c_i) · e^{βJ k_X/(N−1)}),

where A_X is the project's attractiveness, u_i = 1 if i is uncommitted (no strict mention of another project in the last 30 active min) and u_c < 1 otherwise, c_i is i's call cycle (median start-to-start interval), g is a decreasing gate (g = 1 for a ≤ c, g_late < 1 after: the seed is buried in a backlog and the agent has started something else), and βJ k_X is the ordinary Potts occupancy coupling. Summing over the room, the expected wave is

E[S | seed] ≈ A_X [ p_hi R + p_lo (N_sus − R) ],  R = #{i susceptible: u_i = 1, a_i ≤ c_i},

so with p_hi ≫ p_lo the wave scales with the **receptive count R**, not with room size N_sus, the poster's status or the network.

**Rivals (each also simulated on the real call schedules, below):**
- **R-status:** every reader adopts with probability set by the poster's status (reply in-strength, centrality, human vs agent), whatever its read-out time.
- **R-field (shared field):** adoption is driven by a field common to the period or room (goal, kickoff, human prompt, an attention burst that starts before the link), so agents adopt whether or not they read the seed (H34's lesson; H28's lead > lag). Variants: a pulse beginning before the seed (pre-ramp), and one beginning at the seed but reaching every room.
- **R-size:** waves scale with the number of susceptible agents in the room (room size), with no timing effect.
- **R-activity (null):** a constant per-call adoption hazard; agents who happen to be active adopt more of everything.
- **R-share / R-time:** the project's current share, or time of day, sets the wave.

## Data scheme (`scheme/`)
`scheme/build.py` builds `data/processed/H53-announcement-nucleation/` from shared tables only (imports, read-only: `infra/shared/project_states.py: project_map, load_calendar`, `infra/shared/common.py: holdout_mask`). Holdout days are dropped with `holdout_mask` before anything is computed; ledger calls on holdout days count as unobserved. `--allow-holdout` exists only for `analysis/confirm.py`.
- **Inputs:** `artifact_mentions` (strict: `how ∈ {url, output, bare}`; chat links: `source = chat`, `how ∈ {url, bare}`), `artifacts` (project map: files and sites → parent repo, as in `project_states`), `context_ledger_items` + `call_windows` (read-out calls, ages, call cycles), `rooms_timeline`, `roster` (Claude Code agent excluded as a recipient, as in the ledger), `calendar` (active time), `reply_graph` (poster status), `work_commits` (agent work commits), `kicks_classified` (human messages, kickoffs), `period_units` (step changes), `project_states` (W = 30, sources = all, for the herded / never-herded classification).
- **Active time:** a(t) = `active_offset_s` + clip(t − `win_start`, 0, `window_s`) from `calendar`; all horizons and look-backs are in active time (overnight and weekend gaps removed).
- **Seed (first chat link):** the first chat message in the goal period with a strict link to project X, by an agent or a human. Flags: `carried` (X was first seen in the dataset before the period), `human`, `kick_near` (a human message or goal kickoff in the poster's room within 30 active min before), `censored` (the 2-h horizon runs past the period's last non-holdout day).
- **Recipients:** every roster agent (Claude Code excluded) in the seed's room at t_seed, minus the poster; also the agents in other rooms (for the room placebo).
  - **Read-out:** the ledger's receiving call of the seed message (`context_ledger_items.message_id`): t_read, age a_i = `age_s`, batch size `k_new`, rank, `gap_kind`. No item → not read (absent or out of room).
  - **Call cycle c_i:** agent i's median start-to-start `t_call` interval in the period (non-holdout calls, intervals < 1 h).
  - **Susceptible:** i has never had X as its modal project (`project_states`-style W = 15 window label, computed here from strict mentions with the same rule) before t_seed in the period. Mention-level variant: never mentioned X.
  - **Uncommitted u_i:** no strict mention of any project ≠ X in the 30 active min before t_seed. Variant u2: ≤ 2 such mentions.
  - **Pre-seed activity:** calls in the 30 active min before t_seed; any talk call in that window.
- **Adoption (project label, H53):** the time of i's first strict mention of X inside the first W = 15 window (from the day's `win_start`) in which X is i's modal project (H11 rule, ties to the most recent mention), if after t_seed. Variants: *action-only* (sources = action, computer-use touches only), *mention-level* (first strict mention of X, any source), *work commit* (first agent-work commit by i to repo X: `canonical & ~imported & author_kind == agent & ~automated`; periods ≥ #30 only, where git is dense).
- **Output (`data/processed/H53-announcement-nucleation/`):** `seeds.parquet` (one row per seed: goal, unit, project code, poster, human, t_seed, active time, room, flags, poster status, current share, herded k_max, room size), `recipients.parquet` (one row per seed × roster agent present that day, in-room and other-room: read-out call and age, call cycle, batch size, commitment count, pre-seed activity, adoption times per variant, calls from read-out to adoption, follow-up call count, shifted pseudo-seed ages), `adoptions.parquet` (goal, agent, project code: first label / action / mention / commit times), `projects.parquet` (project code → canonical name; data folder only, gitignored), `calls_cache.parquet` (per-call times for the synthetic and natives), `round1/`, `natives/`, `synthetic/`, `confirm_dryrun.json`, `_provenance.json`. Wave sizes and the event study are derived in `analysis/h53core.py: prep` and `analysis/fig_real.py`. No message text anywhere. 30 MB.
- **Regimes covered:** every non-holdout goal period with seeds (regimes I–III); no period crosses 2026-03-24 except #36, which is split by `period_units`.

## Observables
Per seed s (horizon H = 2 h active time, pre-registered; H = 1 h and 4 h as robustness):
- **O1, wave size S_H(s)** = susceptible in-room agents (not the poster) adopting X in (t_seed, t_seed + H] (project-label adoption primary; action-only, mention-level and work-commit variants).
- **O2, receptive count R(s)** = susceptible, uncommitted in-room agents whose read-out age a_i ≤ c_i (one call cycle). **Sensitivity grid:** c ∈ {0.5, 1, 2, 4} × c_i and fixed {1, 2, 5, 10, 30} min; uncommitted variants u, u2, none. Receptive fraction f_R = R / N_sus.
- **O3, rival covariates:** N_sus (susceptible in-room roster agents: room size); U (uncommitted susceptibles, no timing); poster status (log(1 + period reply in-strength) from `reply_graph`, scale = period, soft; PageRank on the period reply graph; human flag); current share of X (pre-seed adopters / labelled in-room agents in the last 30 active min); time of day (fraction of the day's active window elapsed; first-30-min flag).
- **O4, agent-level read-out effect.** For every susceptible in-room recipient whose read-out comes within H: y_is = adopts X within 60 active min after its *own* read-out call (equal follow-up for early and late readers). Timely_is = 1[a_i ≤ c_i]. Seed-stratified (conditional) Poisson / logit with controls (u_i, log(1 + pre-seed calls), talk in last 30 min); rate ratio RR_timely. Variants: agent fixed effects; prior adopters before i's read-out; the grid of c.
- **O5, seed-level model comparison.** Negative binomial (NB2) with period intercepts (exception (d): too few seeds per period; common slopes, partial pooling; per-period slopes and a random-effects meta-analysis alongside):
  - M0 period intercept; M_N log(1+N_sus); M_U log(1+U); **M_R log(1+R)**; M_status (log in-strength + human); M_share; M_tod; M_full (N, U, status, share, tod); M_full+R.
  - Scored by **day-blocked cross-validated log score** (leave one active day out within each period), with a period-cluster bootstrap of score differences.
- **O6, placebo (never-herded seeds).** Herded = X reaches k_X(w) ≥ max(3, ⌈N_room/3⌉) labelled agents in some W = 30 window after the seed (shared `project_states`); never-herded = max k_X(w) ≤ 1. Within-period AUC of R (and of each rival) for herded vs never-herded seeds.
- **O7, phase placebo.** R recomputed at a pseudo-seed time t_seed − 60 active min (same room, same susceptible set) from `call_windows`; its slope in M_R is compared with the real R's. A receptive effect at the call-cycle scale is a phase effect and must not transfer to a time an hour earlier.
- **O8, shared-field diagnostics (H34's lesson).**
  - F1 *step:* naive-agent adoptions of X in (0, 30] vs [−30, 0) active min around t_seed (poster excluded), pooled ratio.
  - F2 *room placebo* (multi-room periods): adoption probability within H for susceptible agents in other rooms (who cannot read the seed) vs the same room.
  - F3 *unexposed adopters:* share of within-H adopters whose ledger context held no link to X before their adoption time.
  - F4 *read-locking for late readers* (a > 10 min): share of their adoptions within 60 min of read-out that fall in the first 3 calls after read-out, vs the share expected if adoption were uniform over their calls in that hour.
- **O9, placebo outcome (activity artifact):** RR_timely for adopting *any other new project* (first linked in the period within ±2 h of the seed) within 60 min of read-out. H53 needs RR_timely(X) > RR_timely(other).
- **O10, operator rule:** predicted wave size from M_R (or the best model) at the 90th vs 50th percentile of R in each period, and the share of a period's seeds posted at a low-R moment.

## Null / baseline
- **N0, activity null** (R-activity): constant per-call hazard; simulated on the real call schedules (synthetic W0). RR_timely ≈ 1 with equal follow-up; seed-level R predicts only through N_sus.
- **N1, room size:** M_N; R must beat it.
- **N2, uncommitted count without timing:** M_U; R must beat it, or the call clock adds nothing beyond "agents are free".
- **N3, poster status:** M_status.
- **N4, shared field:** F1–F4 and the synthetic field worlds; phase placebo (O7); placebo outcome (O9).
- **N5, never-herded seeds** (O6): AUC 0.5.

## Synthetic validation plan (axis F; run before any real data)
`analysis/synthetic.py`: on the **real** call schedules (`call_windows`), rooms, seeds (times, rooms, posters, real susceptible / uncommitted flags and ages), simulate adoptions only, in every replication-eligible period (so event counts are real), 20 replicates per world:
- **W0 activity null:** per-call hazard h·A_X at every call within H, A_X ~ Gamma(shape 0.3, mean 1) (most projects private, a few attractive).
- **WN receptive nucleation:** at the read-out call, P = p·A_X·(m if timely and uncommitted else 1), m ∈ {2, 4}; background W0 at half rate.
- **WS status:** at the read-out call, P = p·A_X·exp(0.7 z_status(poster)), no timing effect.
- **WF0 shared field at the seed:** every susceptible agent in *all rooms* adopts at per-call hazard h_F·A_X·exp(−Δa/30 min) from t_seed, whether or not it read the seed.
- **WFpre attention burst:** the same pulse starting U(0, 60) active min *before* t_seed.
- Base rates set so the mean wave size is 0.3 or 1.0 (two levels; chosen without looking at real adoption).

The full estimator suite (O4, O5, O7, O8, O9) runs on each synthetic data set; recovery rates and a world-classification table are reported. **Decision rule (frozen with the synthetic results, before real data):** "nucleation" = RR_timely CI > 1 *and* M_R beats M_N and M_U *and* no field flag (F1 ratio ≥ 3, F2 ratio ≤ 0.3 where available, F3 ≤ 0.2, placebo outcome RR below RR_timely); "status" = status slope CI > 0 with RR_timely CI including 1; "field" = any field flag; else "null".

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R-status, R-field (pre-ramp; seed-locked all-room pulse), R-size, R-activity, R-share, R-time (Model section).
**Locked holdout used for confirmation:** none yet. Targets #22, #29, #32, #45, #46, #47, #49, #50 and the #51 tail; frozen rule C1–C5 under Results; `analysis/confirm.py` written and dry-run, not run.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Seeds, read-out (DQ1 ledger), adoption (H11 labels via shared `project_states`), commitment and activity all come from shared tables, with one mapping in regimes I–III. Weak points: adoption is attention (strict mentions, chat included; action-only gives the same answers); "uncommitted" is a mention-based proxy whose 30-min active-time look-back reaches into the previous day at day starts; the 10 human seeds are too few. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Read-out gating (updates only at calls) holds: #26 ballots are cast by the reading call (14/17), F4 late-reader locking 7.0 (n = 12 only). The model's gate assumption (adoption probability falls with read-out age at the call-cycle scale) fails: RR flat from ½ cycle to 4 cycles (0.92–1.08). Stationarity and Markov order not audited. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 0 | M_R does not beat M0, M_N or M_U on leave-one-day-out log score (−1.7, −0.8, −1.0 nats; 90% CIs include 0); adding R to M_full gives −0.8. RR_timely CI includes 1; the period random-effects mean is 0.91 [0.69, 1.21]. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | Signatures of announcement seeding hold and match the synthetic read-out worlds: step at the link (F1 22.5 vs ≈ 1 for field worlds), room-bounded adoption (F2 0.12), 1.5% unexposed adopters, and wave = receptive count in the #26 runoff. The nucleation signature itself (early readers adopt more) is absent. The step is partly mechanical for brand-new projects (3.8 for carried-over ones). |
| E interventional | predicts the change across a natural experiment | 1 | No NE study. One quasi-intervention: the 01-09 #26 vote was scheduled in advance, so a clock-driven field and the opening message compete; all 9 ballots followed the message's read-out, none came by the clock. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | 240 synthetic runs on the real schedules of all 23 periods (994 seeds): a planted ×4 receptive effect is recovered in 95–100% of runs (rule v2: 19–20/20), status 20/20, no false "nucleation" in 120 null and field runs; a ×2 effect only at the higher base rate (19/20 vs 4/20). The pre-registered seed-level comparison (P2) has 0–20% power even at ×4. Real results are stable across 9 receptive windows × 3 commitment rules × 3 adoption variants. |
| G ground truth | agrees with known structure | 1 | #26 (DQ6): read-out gating and wave = receptive count in the two rounds with a correctly placed seed; the recorded approval-round opening came after 6/9 ballots (post hoc, the first ballot seeded that wave). #31: H11's waves appear as 10 herded seeds. #40: H31's kickoff-frozen hub turns out to be a link posted 2 min into the kickoff. |
| H comparative | beats the named rivals | 0 | Current share beats R (CV +61.8 nats vs M0, 18/23 periods; AUC 0.72 vs 0.46). R ties room size, uncommitted count, time of day and status. Status's apparent advantage under plain period fixed effects (+141 nats) was a fold artifact (Amendment 2). |
| I transfer | holds in other same-mode periods, including the holdout | 0 | RR_timely CI > 1 in 3 of the 14 periods with ≥ 15 adoptions (#13 1.92, #18 1.38, #38 1.38) and < 1 in none; replication verdicts 1 supported, 2 mixed, 8 failed, 15 descriptive; natives 2 mixed, 2 failed. No regime pattern (I 1.06, III 1.08). Holdout not run. |

## Prediction
*Written 2026-10-04, before the synthetic validation and before any real-data outcome (wave sizes, adoptions, AUCs) was computed.*

**What I had seen when writing this:** the round-1 cards of H27, H31, H11, H06, H28, H08 and H34 (summaries above); structural counts only: seeds per period (5–62 per non-holdout period, 252 in #51; 34 human-posted links in all, ≈ 17 human seeds, nearly all in early regime I); call cycles (median 11–19 s per period, busy loops); read-out ages of seed recipients (median 8–23 s; 40–60% within one cycle, 75–95% within 2 min, ≥ 87% within 10 min; #51 slower: median 47 s); the share of recipients with no other-project mention in the previous 30 min (15–30% in regime III and #30/#31, 40–90% in early regime I). No adoption or wave statistic.

**Prior.** With 15-s cycles, "within one cycle" mostly separates agents in a busy loop from agents in a pause, a long tool call or a consolidation; the phase of a busy loop is close to random. I doubt a 15-s phase changes adoption. A minutes-scale effect (awake vs paused or away) is plausible but hard to separate from activity and from attention bursts that precede the link (H28). Uncommitted agents adopting more is likely and uninteresting. I expect the seed-level wave to track room size and the project's current share, and the call clock to add little.

| # | Prediction | Counts against | My call (credence H53 passes) |
| --- | --- | --- | --- |
| **P1 (primary, mechanism)** | Pooled RR_timely (one cycle) ≥ 1.5 with 95% CI > 1 and random-effects period mean > 1 | CI includes 1, or RR < 1.2 | failed at one cycle (RR 0.9–1.3); 0.2 |
| **P1b (minutes scale)** | RR_timely at c = 10 min ≥ 1.5, CI > 1, and larger than the placebo-outcome RR (O9) | equal to the placebo RR | RR ≈ 1.5–2 but mostly shared with the placebo outcome; 0.3 |
| **P2 (primary, wave size)** | M_R beats M_N, M_U, M_status, M_share and M_tod on day-blocked CV log score (period-bootstrap 90% CI of each difference > 0), and β_R > 0 (CI > 0) in M_full+R | M_R loses to M_N or M_U, or β_R CI includes 0 | failed: M_share or M_N best; 0.2 |
| P3 (status matters little) | M_status adds < 1 nat per 100 seeds over M0 and β_status CI includes 0 | status slope CI > 0 | supported; 0.6 |
| P4 (placebo, never herded) | AUC of R for herded vs never-herded seeds ≥ 0.65 and above the AUC of N_sus | AUC ≤ 0.55 | 0.50–0.60; 0.25 |
| P5 (phase placebo) | the real-R slope exceeds the pseudo-R (t − 60 min) slope, the latter CI including 0 | pseudo-R predicts as well | if R predicts at all, pseudo-R does too (persistent activity); 0.3 |
| P6 (shared field) | F1 step ratio ≥ 3; F2 other-room ratio ≤ 0.3; F3 unexposed share ≤ 0.2; F4 HR ≥ 2 | any of F1–F3 failing flags a field | F1 ≈ 1.5–3 (pre-ramp, as H28), F2 and F3 pass, F4 unclear; 0.3 |
| P7 (work commits) | same sign as P1 on commit adoption (periods ≥ #30), smaller and noisier | opposite sign | attention ≠ work; commit waves mostly 0; descriptive |
| P8 (synthetic, axis F) | at real event counts the decision rule recovers WN (m = 4) in ≥ 80% of runs and W0 / WS in ≥ 80%; WF0 is flagged as a field only where rooms exist (multi-room periods) and is mistaken for nucleation by RR_timely alone in ≥ 50% of runs | WN not recoverable (power < 50% at m = 4) | power adequate for m = 4, marginal for m = 2 |
| P9 (operator rule) | if P1 or P1b holds: posting at the 90th vs 50th percentile of R raises the predicted wave by ≥ 30% | < 10% | no usable timing rule; 0.25 |

**Amendment 0 (2026-10-04, after the coordinator relayed H28's final results, before any synthetic or real-data run; P1–P9 unchanged).** H28 (finished): link exposure goes with HR 2.3 switch-in, but in herding weeks links in the *next* hour predict switches better than links seen in the last hour (10/11 weeks), agents new to X switch at 3.3× baseline in the hour before their first visible link, and the 60-min effect beats a ±30–120 min shift null in only 3/11 periods; a lead placebo is diagnostic only against a synthetic calibration, because cascades make future links positive too. Added controls:
- **O7 extended to a lead/lag placebo:** R recomputed at shifted pseudo-seed times t_seed + δ, δ ∈ {−120, −60, −30, +30, +60, +120} active min (same room and susceptible set); the real-R slope must exceed the shifted ones. Both this and F1 are calibrated on the synthetic worlds (WN must show real > shifted; WFpre shows the H28 pattern).
- **F1 extended to a full pre-trend** (event study −2 h … +2 h), reported against the synthetic WN and WFpre curves.
- **Burst-onset fallback (secondary, labelled post hoc if used):** if adoptions start before seeds become visible (F1 ratio < 2 or a pre-seed excess over the synthetic WN curve), H53's trigger claim fails and I report what precedes the burst instead: the burst onset is the first time ≥ 2 non-poster agents make strict mentions of X within 30 active min; candidates are the seed link, an earlier action-only touch by the creator, a human message or kickoff in the room, and the day start.
- **P10 (added now):** the real-R slope exceeds every shifted-R slope (|δ| ≥ 30 min) and the shifted slopes' CIs include 0. Counts against: shifted R predicts as well (activity / burst state). My call: fails if R predicts at all; credence 0.25.

**Calibration notes from the synthetic validation and Amendment 1** (appended 2026-10-04 after `analysis/synthetic.py` finished, before any real-data outcome; P1–P10 unchanged). 6 worlds × 2 base rates × 20 replicates on the real schedules of the 23 replication-eligible periods (994 seeds, 12,177 susceptible recipient pairs, 6.7M calls). Summary: `data/processed/H53-announcement-nucleation/synthetic/synthetic_summary.json`; figure `figures/synthetic_validation.pdf`.
- **Agent-level RR_timely (P1) is calibrated and powered for strong nucleation only.** CI > 1 in 0–10% of runs under W0, WF0 and WS, 20% under the pre-ramp burst WFpre (RR median 1.09–1.10). Under WN4: positive in 95–100%, median RR 1.56–1.68, P1's full rule (RR ≥ 1.5, CI > 1) passes 80%. Under WN2: median RR 1.19–1.24, positive 25% (mean wave 0.3) / 95% (mean wave 1.0), P1's rule passes ≤ 10%. So **P1's 1.5 threshold corresponds to a planted ×4 receptive multiplier**; the timely main effect is diluted because committed agents carry no effect.
- **The seed-level comparison (P2) has no power.** M_R beats M_N in 0–20% and M_U in 0–10% of WN4 runs; adding R to M_full helps in ≤ 10%. Project attractiveness (overdispersed) and room size swamp the binomial "phase" variation of R given U. **A P2 failure is therefore not evidence against H53** (as H27's P1). P2 is kept as written and reported; it no longer enters the classification.
- **Receptive interaction (added as P1-int, secondary):** the RR of timely × uncommitted, with both main effects in the model, is 0.93–1.07 in the non-nucleation worlds (positive ≤ 5%) and 1.7 (WN2) / 2.9–3.6 (WN4), positive 60–100%. It is the literal H53 contrast and has more power than P1.
- **Shared-field diagnostics discriminate:** F1 step ratio ≈ 1 (W0), 0.6–0.7 (WFpre), ∞ (WF0, no pre-seed adoption), 11–16 (WN, WS). F4 read-locking ≈ 0–1.6 (W0, WF0), 1.6–2.2 (WFpre), 3.1–4.0 (WN, WS). F2 other-room ratio ≈ 1.0–1.2 under every field world but **0.28–0.30 under WN** (background adoption reaches other rooms), so the card's 0.3 threshold sits on the WN median. **Amendment 1: the F2 field flag is moved to > 0.6** (midway); F3 cannot be simulated (no link reads outside the seed) and is reported on real data only.
- **Lead/lag placebo (P10) is weak, as H28 warned:** under WN4 the real-R slope is positive in 50–65% of runs but at least one shifted slope is positive in 45–60%, because busy states persist for an hour. Read P10 as descriptive.
- **Decision rule v2 (frozen now):** *nucleation* = RR_timely CI > 1, F1 ≥ 3, F4 ≥ 2 and F2 ≤ 0.6 where rooms exist; *status* = status slope CI > 0 with RR_timely CI including 1; *field* = F1 < 3 or F2 > 0.6; *seed-locked field* = F1 ≥ 3 but F4 < 2; *read-out-triggered, no timing* = F1 ≥ 3, F4 ≥ 2, RR_timely CI including 1, no status. Recovery: WN4 19/20 and 20/20 nucleation; WN2 19/20 at mean wave 1.0 but 4/20 at 0.3 (13/20 "read-out, no timing"); WS 20/20 status; W0, WF0, WFpre 19–20/20 field. **No false "nucleation" call in 120 non-nucleation runs.**
- **Data notice (2026-10-04):** the shared `activity_bins` join bug does not affect H53 (no use of `activity_bins` or `outages`; activity and commitment come from `call_windows` and `artifact_mentions`).

**Card-level verdict rule.** Supported = P1 and P2 pass, and no field flag in P6. Failed = P1 fails at one cycle *and* at 2 min, and P2 fails. Mixed = anything else (e.g. only P1b passes: an "awake fraction" version, reported as such). *Amendment 1:* the decision-rule-v2 label is reported alongside; because P2 has no power, a P1 pass with a v2 "nucleation" label and a P2 failure reads as "mixed (P2 underpowered)".

**Multiplicity.** Primary tests: P1 and P2 (Holm over the two). Everything else is secondary; the sensitivity grid (9 values of c × 3 commitment variants × 4 adoption variants × 3 horizons) is reported as a curve, not as tests.

**Period roles.** Replication on every eligible period (≥ 10 eligible seeds: ≥ 3 susceptible in-room roster recipients and an uncensored 2-h horizon); periods with 3–9 eligible seeds are descriptive. Per-period predictions are in each `goalperiod-subhypotheses/G<NN>/README.md`, written before that period's run. Native tests (#26, #31, #30, #40) have their own predictions there.

**Holdout confirmation targets** (chosen now from `holdout.json`, before any real-data run): #22 (free week, regime I, like #31), #29 and #32 (regime I), #45 (regime III, two rooms: room placebo), #46, #47, #49, #50 (regime III), and the #51 tail. #28, #34 and #43 have ≤ 4 seeds and are reported but not scored. **Reuse disclosure:** H11 (#22, #28, #45), H28 (#22, #28, #45), H27 (#22, #28, #29, #32, #34, #45–#50, #51 tail), H31 (#29, #46, #47, #49, #50) and H06 (#22) target overlapping periods with project-label statistics (Potts coupling, link hazards, onset timing, consensus times, abundance). H53's statistics (read-out timing of seed recipients → wave size; RR_timely) are different and unexamined; the reuse policy in `../holdout.md` applies (committed predictions and script, disclosure in both cards and `LOG.md`).

## Results by goal period
All periods run 2026-10-04 after their `G<NN>/README.md` prediction was written. Key numbers: RR_timely (one cycle, 95% CI), F1 step ratio, mean wave S (2 h), mean receptive count R. Replication verdicts use Amendment 2's mapping (F4 is untestable per period). 15 descriptive rows are underpowered (< 15 adoptions, a non-estimable SE, or 3–9 seeds); they count as 15 phase-diagram points, not as tests.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | failed | RR 0.69 [0.47, 1.01]; F1 ∞ (no pre-seed adoption); mean S 0.91; R 0.43 |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | descriptive | 6 seeds; mean S 0.67 |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | descriptive | 7 seeds; mean S 0.43 |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | descriptive | RR 0.32 [0.03, 2.88]; F1 ∞ (no pre-seed adoption); mean S 0.13; R 1.52 |
| [G12](goalperiod-subhypotheses/G12/README.md) | replication | failed | RR 1.39 [0.80, 2.43]; F1 ∞ (no pre-seed adoption); mean S 0.92; R 2.12 |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | supported | RR 1.92 [1.15, 3.23]; F1 11.50; mean S 0.82; R 1.48 |
| [G16](goalperiod-subhypotheses/G16/README.md) | replication | descriptive | 8 seeds; mean S 0.50 |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | descriptive | RR 1.26 [0.37, 4.23]; F1 ∞ (no pre-seed adoption); mean S 0.64; R 1.80 |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | mixed | RR 1.38 [1.03, 1.83]; F1 101.00; mean S 2.21; R 1.44 |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | failed | RR 1.39 [0.76, 2.54]; F1 30.00; mean S 0.71; R 1.10 |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | descriptive | RR 0.56 [0.54, 0.57]; F1 ∞ (no pre-seed adoption); mean S 0.38; R 2.10 |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | failed | RR 0.76 [0.42, 1.36]; F1 ∞ (no pre-seed adoption); mean S 0.70; R 2.32 |
| [G23](goalperiod-subhypotheses/G23/README.md) | replication | descriptive | 5 seeds; mean S 2.20 |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | descriptive | RR 0.56 [0.56, 0.56]; F1 ∞ (no pre-seed adoption); mean S 0.95; R 2.90 |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | failed | RR 0.88 [0.45, 1.72]; F1 ∞ (no pre-seed adoption); mean S 1.71; R 2.38 |
| [G26](goalperiod-subhypotheses/G26/README.md) | native | mixed | runoff 8/8 ballots = readers in window; 17/17 ballots after read-out in runoff + confirmatory; ρ fails |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | descriptive | 5 seeds; mean S 2.60 |
| [G30](goalperiod-subhypotheses/G30/README.md) | native | failed | RR 0.80 [0.53, 1.18]; re-link step 1.29; 8 re-seeds |
| [G31](goalperiod-subhypotheses/G31/README.md) | native | mixed | AUC(R) 0.70 vs share 0.76; largest waves at R = 1; F1 5.8 |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication | descriptive | 8 seeds; mean S 2.38 |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | descriptive | 4 seeds; mean S 2.00 |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | descriptive | RR 0.53 [0.35, 0.78]; F1 3.67; mean S 0.53; R 0.39 |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | descriptive | RR 1.10 [0.44, 2.75]; F1 ∞ (no pre-seed adoption); mean S 1.64; R 0.82 |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | mixed | RR 1.38 [1.01, 1.90]; F1 6.00; mean S 0.55; R 0.31 |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | descriptive | RR 0.00 [0.00, 0.00]; F1 n/a; mean S 0.31; R 0.19 |
| [G40](goalperiod-subhypotheses/G40/README.md) | native | failed | hub wave 8 (pred. 0.5) at R = 0; 14% pre/unexposed; 71% in hour 1 |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | failed | RR 1.36 [0.72, 2.57]; F1 6.67; mean S 1.16; R 0.56 |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | descriptive | RR 0.00 [0.00, 0.86]; F1 ∞ (no pre-seed adoption); mean S 0.38; R 0.85 |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | failed | RR 1.18 [0.86, 1.60]; F1 13.67; mean S 1.20; R 1.24 |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication | failed | RR 1.05 [0.77, 1.43]; F1 18.00; mean S 0.77; R 2.36 |

## Results
*Exploratory round 1, 2026-10-04. Non-holdout days only.*
- **Code:** `scheme/build.py` (+ `scheme/h53lib.py`); `analysis/h53core.py` (estimators), `analysis/synthetic.py`, `synth_summary.py`, `fig_synth.py`, `run_round1.py`, `natives.py`, `natives_text.py`, `period_folders.py`, `fig_real.py`, `confirm.py` (frozen, dry-run only).
- **Data:** `data/processed/H53-announcement-nucleation/` (`seeds`, `recipients`, `adoptions`, `projects`, `calls_cache`; `round1/round1.json`, `period_G<NN>.json`, `agent_table`, `seed_table`, `readout_spread.json`; `natives/`; `synthetic/`; `confirm_dryrun.json`; `_provenance.json`). 30 MB (27 MB is the call cache).
- **Figures:** [`figures/round1_overview.pdf`](figures/round1_overview.pdf) (six panels), [`figures/synthetic_validation.pdf`](figures/synthetic_validation.pdf), [`figures/summary_obs.pdf`](figures/summary_obs.pdf), [`figures/summary_synth.pdf`](figures/summary_synth.pdf).

**Outcome vs prediction** (pooled over the 23 replication-eligible periods: 928 seeds, 10,261 susceptible readers, 726 adoptions)

| Prediction | Outcome | Verdict |
| --- | --- | --- |
| **P1** RR_timely (one cycle) ≥ 1.5, CI > 1, RE mean > 1 | 1.06 [0.93, 1.22]; RE mean 0.91 [0.69, 1.21] (21 periods); agent FE 1.09; no controls 1.13 [0.98, 1.30]; action-only 1.07; mention-level 1.04 | **Failed** (as I predicted) |
| P1-int (Amendment 1) RR of timely × uncommitted | 1.12 [0.85, 1.49] | failed |
| **P1b** RR_timely at 10 min, CI > 1 and above the placebo outcome | 1.35 [0.79, 2.29]; placebo outcome 1.00 [0.70, 1.44]. At 5 min 1.61 [1.05, 2.48] (1 of 27 grid cells; not significant after multiplicity) | **Failed** |
| **P2** M_R beats every rival on held-out log score; β_R > 0 | M_R − M0 −1.7 [−4.8, 1.0]; vs M_N −0.8; vs M_U −1.0; vs M_share −63.5; β_R in M_full+R 0.16 [−0.07, 0.40] | **Failed** (and unpowered: Amendment 1) |
| P3 status matters little | M_status − M0 −1.4 [−4.9, 1.8]; β_status 0.07 ± 0.07; 6 eligible human seeds (mean wave 1.2 vs 0.9 for agents) | **Supported** |
| P4 AUC(R), herded vs never-herded ≥ 0.65 | 0.46 (109 herded vs 637 never); current share 0.72, status 0.55, U 0.46, room size 0.42 | **Failed** |
| P5/P10 real-R slope beats shifted-R slopes | real 0.13 [−0.09, 0.34]; shifted −0.20 … 0.11 (−120 min: −0.20 [−0.40, −0.00]) | **Failed** (nothing to beat; weakly diagnostic per the synthetic) |
| **P6** no shared field: F1 ≥ 3, F2 ≤ 0.3, F3 ≤ 0.2, F4 ≥ 2 | F1 22.5 (28 → 630); F2 0.12 (301 multi-room seeds); F3 0.015; F4 7.0 (n = 12) | **Passed** (my call was a pre-ramp: wrong for first links; carried-over projects 3.8) |
| P7 commits: same sign as P1, weaker | RR 0.95 [0.70, 1.29]; 128 commit adoptions; 85% of commit waves are 0 | as predicted (descriptive) |
| P8 synthetic recovery | ×4 recovered 19–20/20; status 20/20; nulls/fields 0 false nucleation; ×2 19/20 at mean wave 1.0, 4/20 at 0.3; seed-level P2 0–20% power | **Mostly passed**; the "field mistaken for nucleation by RR alone" clause failed (RR positive in only 5–10% of field runs): good news for the agent-level test |
| P9 operator timing gain ≥ 30% | posting at the 90th vs 50th percentile of R: ×1.09 predicted wave | **Failed** (as I predicted) |
| Card-level rule | P1 fails at one cycle and at 2 min (1.21 [0.95, 1.53]); P2 fails | **Failed**. Rule-v2 label: "read-out-triggered, no timing" |

**Synthesis.**
1. **Waves are seeded by announcements.** For brand-new projects almost no one adopts before the first link (18 adoptions in the 30 active min before vs 592 after). Even for projects already known in the dataset the rate rises 3.8× at the period's first link. Adoption stays in the poster's room (other-room agents adopt at 0.12× the rate) and requires the link in context (1.5% of adopters had none). This differs from H28's pre-trend because H53 uses *first* links: H28's agents were switching to projects they already knew, inside an attention burst.
2. **…but the call clock does not set the wave.** Read-out within ½–4 call cycles (8–60 s) makes no difference (RR 0.92–1.08). Minutes-scale windows show at most a weak, non-robust effect (5 min: 1.61 [1.05, 2.48]; 10 min: 1.35; 30 min: 1.57 [0.63, 3.9]). Late readers (> 10 min) do adopt much less (15 of 914, 1.6% vs 7%), but that gap is explained by their being inactive before the seed (calls, talk in the previous 30 min). It is the awake/active state, not the phase of the call loop.
3. **Who adopts instead (post hoc, labelled).** Agents who talked in the 30 min before the seed adopt 3.1× [2.2, 4.4] more (they are in the conversation), and agents with *no* other-project mention adopt *less* (0.77 [0.65, 0.91]): artifact-active agents take up new projects; idle ones don't. H53's premise that uncommitted readers are the receptive ones is reversed. Read-out delay as a continuous dose: RR 0.88 [0.78, 0.997] per log-minute, marginal and post hoc. A "prior adopters before read-out" covariate looked strongly negative (0.67) but is mechanically biased (an agent's own adoption is excluded from its own count) and is not interpreted.
4. **What predicts wave size: the project's current share.** Projects already held by some of the room at the moment of the link herd later (AUC 0.72; CV +62 nats, 18/23 periods). The receptive count, room size, the uncommitted count, time of day and poster status add nothing out of sample.
5. **Where the call clock does matter: deadline-bound calls.** In #26, ballots are cast by the agent's reading call of the round's opening message (14/17 in the runoff and confirmatory rounds), and the runoff's 100-s window made the wave equal to the readers within it (8 = 8; the only non-voter read at 115 s). The scheduled 01-09 round followed the message, not the clock. Post hoc, the approval round was seeded by the first ballot: the next five ballots came within 40 s, each from the voter's reading call or the next one.
6. **Natives in brief.** #31 (mixed): herded seeds had higher R (AUC 0.70), but the largest waves came from seeds with R = 1. #30 (failed): re-announcing the shared repo brings agents back (62% of at-risk readers), but timing does not predict who, and returns do not step up at re-links (1.29). #40 (failed as a negative control): the kickoff-frozen hub was link-seeded 2.4 min into the kickoff; 8 agents adopted within 2 h (predicted 0.5; p = 0.0004) although R = 0.

**Operator rules (deliverable).**
- *Project announcements:* timing them to the call clock buys nothing (≈ +9% at best). Post into an active conversation (agents who just talked are 3× likelier to take it up). The share of the room already on the project is the best predictor of a pile-on. Duplicate pile-ons are prevented by not linking, not by timing: no link, almost no wave.
- *Deadline-bound calls (votes, polls, sign-ups):* the wave equals the agents whose next call falls inside the window. Read-out delays of present agents: median 25 s; 88% within 2 min in regimes I/II but only 67% in regime III (90% within ≈ 12 min; 95% within ≈ 29 min). A 2-min window disenfranchises about a third of a regime-III swarm; ≥ 15 min reaches about 90%.

**Caveats.**
- **Adoption is attention.** Labels come from strict mentions, including chat; the action-only variant gives the same answers; commit adoptions are rare (128).
- **The step at the first link is partly mechanical** for projects nobody knew; carried-over projects (step 3.8) are the cleaner test.
- **The "uncommitted" proxy is crude** (mention-based; its active-time look-back crosses day boundaries).
- **Power.** The agent-level test detects a ×4 receptive effect, not reliably a ×2 one at low adoption rates. The seed-level comparison has no power at all (Amendment 1). Per-period tests are mostly underpowered (15 descriptive).
- **Multiplicity.** The grid has 27 cells; the one with CI > 1 (5 min) is reported as such.
- **Fold artifact.** Plain period fixed effects made the held-out comparison degenerate (Amendment 2); partial pooling with τ = 1 was fixed without tuning, and the FE numbers are in `round1.json` (`P2_models_fe`).
- **#26.** The approval round's recorded opening message postdates most ballots; the effective seed is post hoc (DQ2 replies are low-confidence, p_reply 0.11–0.48).
- **One-room periods** cannot separate a seed-locked shared field from read-out triggering (synthetic WF0); F2 rests on the 301 multi-room seeds (#36–#51).

**Amendments, with what I had seen when making them.**
- *Amendment 0* (after the coordinator relayed H28's final results; before any synthetic or real run): lead/lag placebo, full pre-trend, burst-onset fallback, P10.
- *Amendment 1* (after the synthetic validation; before any real outcome): P2 declared unpowered and dropped from classification; P1-int added; F2 flag moved from 0.3 to 0.6; decision rule v2 frozen.
- *Amendment 2* (post hoc, after the first real run): (a) the seed-level models use partial pooling of period intercepts (τ = 1, fixed, not tuned). The card already named exception (d), but plain fixed effects were run first; leave-one-day-out folds whose training days had zero adoptions (#24, #39) gave −∞ intercepts and handed any covariate model spurious gains (status +141 nats, R −62). FE results are kept as `P2_models_fe`. (b) Per-period verdict mapping: F4 has < 10 late-reader adoptions in every period, so per-period verdicts use RR_timely and F1 only (supported = RR ≥ 1.5, CI > 1, F1 ≥ 3; failed = CI includes 1 or RR < 1; mixed = CI > 1 but RR < 1.5; descriptive = < 15 adoptions or non-estimable SE). (c) Post hoc analyses: activity/talk/commitment effects, read-out-delay dose, rank in batch, new vs carried projects, by regime, the #26 effective seed.
- *Not amended:* seed, adoption, receptive and susceptible definitions; horizons; P1–P10 thresholds; the card-level rule.

**Confirmatory prediction** (frozen 2026-10-04 after round 1, before any holdout data was read; `analysis/confirm.py`).
- **Targets:** #22, #29, #32, #45, #46, #47, #49, #50 and the #51 tail. #28, #34, #43 are reported but not scored.
- **C1 (H53 as hypothesized):** RR_timely ≥ 1.5 with CI > 1. *Round 1 predicts: not confirmed.*
- **C2 (round-1 negative replicates):** CI includes 1, or RR < 1.2.
- **C3 (announcement-seeded, room-bounded):** F1 ≥ 3, F3 ≤ 0.2, and F2 ≤ 0.3 where ≥ 20 multi-room seeds exist.
- **C4:** AUC(share) > AUC(R) and AUC(R) ≤ 0.6.
- **C5:** M_R − M0 held-out score ≤ 0 or its CI includes 0.
- **Power rules:** C1/C2 need ≥ 100 adoptions; C4 ≥ 10 herded seeds.
- **Dry run** on non-holdout stand-ins #18, #31, #44: C1 not confirmed; C2–C5 confirmed (a pipeline check, not evidence).
- **Safety:** needs `--confirm --i-understand-this-uses-the-locked-holdout` and a committed H53 folder. Reuse disclosure under Prediction.

## Round 2 redirects (proposed by the round-1 agent, 2026-10-04)
- **What the direction is really after:** When does announcing something produce a pile-on, and can an operator shape the size by when and how it announces?
- **H53-R1. Deadline-bound calls as the regime where the clock binds.** Collect every time-limited call to action (votes, polls, sign-ups, checkpoint calls in #44, #12 verdicts). Test wave = readers inside the window, and window length against regime read-out spread (a disenfranchisement curve).
- **H53-R2. Conversation-gated uptake.** Model take-up as current share × conversation participation (talk in the last 30 min, RR 3.1): a kinetic Potts with a coupling switched on by being in the thread (DQ2 reply graph), against H28's attention-burst rival.
- **H53-R3. Within-project designs at scale.** Use every re-link after a lull in all periods (not only #30) with project fixed effects, which removes attractiveness, the dominant confound.
- **H53-R4. A better commitment measure.** Behavior states or context backlog instead of mention counts, with day starts handled. Test why artifact-active agents adopt more.

## Notes
- 2026-10-04: promoted from HH168 by Vivian (wave B; DQ1 context ledger available). Round-1 agent: card, model, scheme, observables, nulls and predictions written before the synthetic validation and before any real-data outcome.
- 2026-10-04: Amendment 0 after the coordinator relayed H28's results (before any run). Synthetic validation run; Amendment 1 appended before real data. Per-period predictions written (30 folders), then round 1 run; Amendment 2 (post hoc) disclosed above. `analysis/confirm.py` frozen and dry-run on stand-ins only.
- 2026-10-04: the shared `activity_bins` join bug (coordinator notice) does not touch H53.
