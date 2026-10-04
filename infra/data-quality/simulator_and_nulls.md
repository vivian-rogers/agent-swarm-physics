# Village-skeleton simulator and null library (DQ8)

**Code:**
- `infra/shared/simulate.py`: skeletons and dynamics.
- `infra/shared/nulls.py`: surrogates, placebo designs, parametric nulls, statistics and the size calibration.
- `infra/shared/activity_bins_fixed.py`: the corrected minute grid the skeleton reads.

**Tests:** `infra/shared/tests/test_simulate.py` (15) and `test_nulls.py` (6).

**Size table:**
- `infra/data-quality/null_sizes.json` (in git, numbers only);
- `data/processed/shared/null_sizes.parquet` (with provenance).

**Why.** About a dozen hypotheses built their own "synthetic worlds on real schedules" and their own surrogate nulls, and several fell into the same traps independently:
- shared fields read as coupling or branching (H25, H34);
- day edges and stalls fake co-activation (H38);
- lull filters bias variance ratios (H25);
- sign-shuffle and FDR nulls are anti-conservative (H37);
- kick-free-future controls manufacture effects (H39);
- whole-graph λ₂ is a weakest-link statistic (H31);
- drives saturate H01's estimator (H26).

One tested simulator and one calibrated null library make axis-F validations comparable and catch these traps by default.

## 1. Skeletons

`extract_skeleton(unit_id)` reads one `period_units` unit. It reads structure, not outcomes, and no text:

| Element | Source |
| --- | --- |
| roster, presence (agent on the roster that day) | `activity_bins_fixed` rows |
| per-agent span (first..last record of the day) | `states_min.in_span` |
| rate profiles: activity, P(talk \| active), messages per minute, switching rate | `activity_bins_fixed` states, `chat_core`; 121-min moving average within the span |
| rooms over time | `rooms_timeline` (minute midpoints) |
| kicks: time, kind, subkind, targets | `kicks_classified` |
| operator schedule; real stalls; silence reasons | `stall_minutes.scheduled` / `.explained`; `reasons` |
| statement counts per agent × 30-min window | `embeddings/statements` (chat) |
| project-label coverage | `project_states` (W = 30, sources all) |
| call windows (turn call start / end, talk flag) | `call_windows` (DQ1) |

- **Holdout.** A held-out unit raises `HoldoutError` unless `allow_holdout=True`, which is for confirmatory designs only.
- **Toy skeletons.** `toy_skeleton(...)` builds the same structure without data, on consecutive weekdays from a Monday, for tests and long event-study timelines.
- **Speed.** Extraction takes about 0.2 s per unit. Simulation takes 0.05–0.5 s per unit (a 25-agent, 5-day unit is about 0.3 s).

**The skeleton reads `activity_bins_fixed`, not `activity_bins`** (see the data-quality finding below). Real stall and reason replay (`StallModel(source="real")`) still inherits that bug until `outages.py` is rebuilt on the fixed grid.

## 2. Dynamics

Every model is optional and plugs into one channel. `simulate(sk, seed, activity=, edge=, stalls=, talk=, content=, projects=, kicks=)` runs them. `preset(name, **overrides)` gives the named dynamics below.

| Preset / model | What it plants | Truth recorded |
| --- | --- | --- |
| `independent` (`ActivityModel()`) | Each agent is a two-state Glauber chain whose occupancy follows its real smoothed profile and whose switching rate matches its real one: P(+\|+) = 1 − c/2p, P(+\|−) = c/2(1−p), so h = (logit a + logit b)/4 and K = (logit a − logit b)/4 (exact rate matching). `profile="flat"` uses agent-day means, which removes the real shared schedule. | — |
| `global_field`, `room_field`, `tod_field` (`Fields`) | Shared OU field (sd, τ), per-room OU fields, time-of-day cosine, day field, weekday field (Monday effect), agent-day heterogeneity. | field parameters |
| `day_edge` (`EdgeDrive`) | Spans start within `jitter` min of the operator's first on-minute and end within `jitter` of the last, plus a start-up burst (H38's regime-III scaffold). | jitter, burst |
| `ising`, `ising_readout` (`ActivityModel(J, scope, delay)`) | Parallel kinetic Ising with mean-field coupling J/n to the others' deviations from their expected spin (rates stay matched to first order), village or room scope. Delay: `none`, `lag` (L_i min), or `readout`, where the others are seen as they were at the agent's last call start (H08's rule, from `call_windows`). | J, g_true = J q̄ (N−1)/N (H25's formula), median read-out lag |
| `hawkes` (`TalkModel(kind="hawkes")`) | Multivariate Hawkes talk, exponential kernel, self n_s, cross n_x. Each event's cross offspring go to recipients drawn in proportion to their own rates, village or room scope. Simulated exactly by the cluster construction, with baseline μ = r − n_s r − A r so that stationary message rates match the real ones. Children mention their parent's author with probability p. | n_x, n_s, τ, realized branching, parent of every message (`msg_truth`) |
| `vector_spin` (`ContentModel(kind="ou")`) | O(32) latent content per 30-min window with anisotropic noise (PR ≈ 8), persistence φ, room or village mean-field J, and drives: global day, room day, kickoff relaxation, time of day. Statements u = unit(static + 0.6 goal + z + ε), emitted with the real statement counts, float16 unit vectors like the shared white32 vectors. | J, g_true = J (n−1)/n, latent z |
| `degroot` (`ContentModel(kind="degroot")`) | Read-out DeGroot: an agent active in window w moves toward the previous window's statements by others (room or village) with weight α. | α, latent z |
| `potts_waves` (`ProjectModel`) | Kinetic Potts project choice per 30-min window (P ∝ exp(h_a + J frac_a)), reconsider probability p, herding waves in which a random project recruits each agent with probability `wave_p`. Observed only where the real labels exist. | J, p, waves |
| `stalls` (`StallModel`) | Planted platform stalls: rate from π, geometric lengths (mean 8, ≥ 2 min), everyone silent except an optional free agent, infra reasons with probability r; or `source="real"` to replay real stalls and scheduled-off minutes. | stall minutes |
| `kick_field` (`KickModel`) | Field (or catalytic, at fixed occupancy) responses to skeleton kicks; or `source="idle"`, a synthetic nudger that targets agents idle ≥ 10 min, as the real nudger does. | kick truth table |

**Outputs.** `Sim.tables()` returns frames in the shared schemas:
- `activity_bins`, `chat_core`, `chat_mentions_clean`;
- `statements`, with `Sim.statement_vectors` (n × 32 float16, unit);
- `agent_win30`, with vectors;
- `project_states`, `kicks_classified`;
- `stall_minutes` (its counting columns, plus `planted_stall`), `reasons`;
- `call_windows` (lite: the skeleton's turns);
- truth frames `kick_truth` and `msg_truth`.

Column names and dtypes match the real tables, which is checked in the tests. `Sim.spins(channel)` gives per-day (T × N) ±1 arrays; `Sim.content_panel()` gives N × W × 32 agent-window means.

**Hook (DQ1).** `delay="readout"` uses call starts. A finer read-out (the visible message set at each turn) can take `context_ledger_items` per turn once a content model needs it. `_readout_index` is the place to plug it in.

## 3. Planted-parameter recovery (tests)

All 15 `test_simulate.py` tests pass (~6 s):

| Check | Result |
| --- | --- |
| independent: occupancy vs profile; switching vs real rate | within 0.05 per agent; within 25% |
| independent: equal-time gain on the all-present window | \|g\| < 0.04; on the whole-day grid, staggered edges fake g ≈ 0.3 |
| kinetic Ising J = 0 and 0.8 | pseudo-likelihood with the engine's exact offsets recovers J within 0.15 |
| read-out delay J = 0.8 | recovered with the read-out regressor; a no-delay regressor attenuates it |
| shared field, no coupling | raises the gain by > 0.1 (fields are not coupling) |
| day edge | all spans start and end within 2 min |
| stalls π = 0.10 | realized 0.10 ± 0.03 over 30 days; nobody active in stall minutes; infra reasons |
| Hawkes n_x + n_s = 0.5 | realized branching within 0.07; message rate within 15%; EM estimate within 0.12; parent mentions at the configured rate |
| vector spin J = 0.6 | least squares on the latent state recovers J within 0.15; real statement counts reproduced; unit float16 vectors |
| DeGroot α = 0.4 | regression on read-out targets recovers α within 0.1 |
| Potts J = 2, p = 0.4 (with waves) | MLE recovers p within 0.08 and J within 0.6 |
| kick field h = 1.5 vs 0 | ITT episode − control > 0.1 vs \|·\| < 0.05 |
| tables | schemas equal to the real tables; no string longer than 40 characters (no text) |
| real unit 41 | rate-matched activity within 5%; a held-out unit raises `HoldoutError` |

On real units, the independent model matches activity minutes, talk minutes and message counts within about 1–3% (units 12a, 41, 51c).

## 4. Null library

| Null | Function | Keeps | Breaks |
| --- | --- | --- | --- |
| cross-day surrogate | `crossday` | daily profiles, operator schedule and edges (aligned by minute), autocorrelation | same-day co-movement |
| within-day circular shift | `circshift` | per-day marginals, autocorrelation | daily-profile alignment and same-day co-movement |
| block shift (30 min) | `block_shift` | per-agent block means | within-block alignment |
| room relabeling | `room_relabel` | room sizes at every time | agent–room assignment |
| placebo dates | `placebo_dates`, `placebo_test` | weekday (Monday effect), timeline position | the event |
| lever controls | `lever_design`, `cluster_boot_test` | agent, state, inactivity-age bin, past-only eligibility, presence | the kick |
| agent-field null (signed graphs) | `fit_ordinal`, `agent_field_null` (from H37) | speaker and target fields, ordinal non-additivity | pair structure |
| sign shuffle (H37) / label permutation | `sign_shuffle`, `label_permutation` | edge magnitudes / label counts | fields and signs |
| cross-day message placebo (H29) | `crossday_message_placebo` | sender, time of day | the day |

Stall and edge handling: `all_present_window` (H38's operator rule), `explained_silence_mask` (H38's stall rule), `stall_mask` (H25's null-calibrated stall runs).

**Joint shifting.** All three surrogates take `joint=[...]` to shift reasons or talk spins with the same offsets. Masks are applied **before** surrogates are drawn.

**Statistics:** `stat_cw_gain` (pooled 1 − 1/VR in 30-min blocks), `stat_lambda1`, `stat_room_excess`, `stat_event_step`, `stat_signed` (faction score 1 − 2f and BH-significant negative pairs), `message_pull_rows`.

## 5. Size table

**Calibration setup:**
- Nominal α = 0.05.
- **100 replicates per cell (50 for power cells), each with 49 surrogates.** One-sided p = (1 + #{null ≥ obs}) / 50, except for the design-based tests, which use two-sided cluster-bootstrap or t prediction p.
- Activity cells run on 10 real non-holdout skeletons (12a, 13, 20c, 26, 35, 38a, 40, 41, 42b, 51c), cycled over replicates. The other families run on toy skeletons.
- "Calibrated" means a size ≤ 0.10, the binomial 97.5% quantile at 100 replicates.
- About 2,000 jobs, 4 min on 2 processes.

**Activity preprocessing variants:**
- `raw`: the whole-day grid.
- `trim`: the all-present window.
- `trim_h38mask`: trim, plus explained joint silences removed.

**Scenarios** (J = 0 unless the column is a power column):
- `indep`: rate-matched on real schedules.
- `indep_flat`: flat profiles.
- `slow_field`: OU τ = 120 min plus time of day.
- `fast_field`: OU τ = 10 min.
- `day_edge`: synchronized starts plus a burst.
- `stalls`: π = 0.05, 30% with a free agent.

**Activity statistics** (size per scenario; **bold** = anti-conservative (> 0.10); † = a documented trap, reproduced; ‡ = a documented trap, not reproduced in this design; last column = power at J = 0.5):

| statistic | null | indep | indep_flat | slow_field | fast_field | day_edge | stalls | power_J0.5 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cw_gain_raw | crossday | 0.06 | 0.10 | **0.93** | **1.00** | **0.22** | **1.00** | 0.92 |
| cw_gain_raw | circshift | **0.30**† | **0.33** | **0.97** | **1.00** | **1.00** | **1.00** | 0.96 |
| cw_gain_raw | block_shift | **0.28**† | **0.34** | **0.95** | **1.00** | **1.00** | **1.00** | 0.94 |
| cw_gain_trim | crossday | 0.03 | 0.05 | **0.90** | **1.00**† | **0.15** | **0.99**† | 0.92 |
| cw_gain_trim | circshift | 0.02 | 0.02 | **0.94**† | **1.00** | **0.44** | **1.00** | 0.90 |
| cw_gain_trim | block_shift | 0.04 | 0.03 | **0.94** | **1.00**† | **0.51**† | **1.00**† | 0.88 |
| cw_gain_trim_h38mask | crossday | 0.05 | 0.05 | **0.88** | **1.00** | **0.13** | **0.13** | 0.90 |
| cw_gain_trim_h38mask | circshift | 0.00 | 0.02 | **0.92** | **1.00** | **0.49** | 0.09 | 0.94 |
| cw_gain_trim_h38mask | block_shift | 0.02 | 0.03 | **0.93** | **1.00** | **0.52** | **0.12** | 0.92 |
| lambda1_raw | crossday | **0.62** | **0.53** | **1.00** | **1.00** | **0.68** | **0.99** | 0.92 |
| lambda1_raw | circshift | **0.67** | **0.56** | **1.00** | **1.00** | **1.00** | **0.98** | 0.94 |
| lambda1_raw | block_shift | **0.35** | **0.40** | **0.95** | **1.00** | **1.00** | **0.98** | 0.94 |
| lambda1_trim | crossday | **0.19**† | **0.11** | **1.00** | **1.00** | **0.27** | **0.97** | 0.70 |
| lambda1_trim | circshift | **0.17** | 0.03 | **1.00** | **1.00** | **0.36** | **0.99** | 0.80 |
| lambda1_trim | block_shift | 0.05 | 0.05 | **0.94** | **1.00** | **0.20** | **0.99** | 0.74 |

**Design-based and other nulls:**

| statistic | null | scenario: size | power |
| --- | --- | --- | --- |
| room_excess | room_relabel | indep 0.05; global_drive 0.04; room_drive **0.82**† | 0.18 |
| event_step_k1 | placebo_dates_weekday | indep 0.07; monday 0.09 | 0.06 |
| event_step_k1 | placebo_dates_any | indep 0.05; monday 0.08‡ | 0.06 |
| event_step_k3 | placebo_dates_weekday | indep 0.07; monday 0.06 | 0.22 |
| event_step_k3 | placebo_dates_any | indep 0.07; monday 0.05 | 0.28 |
| lever_effect | lever_controls_past | indep 0.08 | 1.00 |
| lever_effect | lever_controls_future | indep **0.15**† | 1.00 |
| lever_effect | lever_controls_past_cut | indep **0.43**† | 1.00 |
| lever_effect | lever_controls_past_nopresence | indep **0.13**† | 1.00 |
| signed_faction | agent_field | indep 0.03; sparse 0.08 | 0.82 |
| signed_faction | sign_shuffle | indep 0.04; sparse 0.06‡ | 0.86 |
| signed_faction | label_permutation | indep 0.03; sparse 0.02 | 0.84 |
| signed_negpairs | agent_field | indep 0.01; sparse 0.03 | 0.50 |
| signed_negpairs | fdr_direct | indep 0.09‡; sparse **0.30**† | 0.60 |
| signed_negpairs | label_permutation | indep 0.03; sparse 0.01 | 0.50 |
| message_pull | crossday_message_placebo | indep 0.02; ou_drift 0.04; day_drive **1.00**† | 0.92 |
| message_pull | sameday_message_placebo | indep 0.07; ou_drift 0.09‡; day_drive 0.06 | 0.44 |

Run: 100 replicates per size cell (power cells: 50), 49 surrogates, seed 20261004, 224 s, built 2026-10-04T06:07 UTC.

**How to read it:**
1. **Trim before any synchrony statistic.** On the whole-day grid, block-shift and circular-shift nulls reject 28–34% of independent swarms: staggered day edges and absent minutes look like co-activation (H38, H17). Only the cross-day null survives this, because it keeps the edges aligned. On the all-present window, all three nulls are calibrated for the gain.
2. **No surrogate removes a same-day shared field.** Fast or slow fields give 88–100% rejections with every null, trimmed or not. A significant gain or λ₁ against any of these nulls means "co-movement beyond each agent's own schedule", not coupling (H25, H34). Separating field from coupling needs a design: room-excess with room relabeling, natural experiments, or read-out timing.
3. **Day edges and start-up bursts survive trimming** (block shift 0.51; cross-day 0.13–0.15). Stalls give about 100% rejections unless masked; H38's explained-silence mask brings them to 0.09–0.13, borderline, because stalls with one free agent still leak.
4. **λ₁ against the cross-day edge picks up the real shared schedule** even for independent agents on the trimmed window (0.19; 0.11 with flat profiles). Use the block shift (0.05) for λ₁, or report the schedule share. This bears on H12's "one market mode in 22/24 units".
5. **Room relabeling is calibrated against global drives but not against room-specific drives** (0.82). Within-room excess is coupling or a room field (H26).
6. **Lever designs:**
   - past-only eligibility, presence-masked, uncut ITT windows, agent-day clusters: 0.08;
   - future-kick-free controls: 0.15 (H39);
   - presence ignored: 0.13 (H17's grid idle);
   - window means cut at the next kick: 0.43, state-dependent censoring. Cutting is right for hazard estimators only.
7. **Signed graphs.** The ordered-logit agent-field null is calibrated (0.01–0.08). The direct per-pair BH FDR is anti-conservative (0.09 dense, 0.30 sparse; H37). H37's sign-shuffle anti-conservativeness (10–28% at its real reply structures) is **not** reproduced at our synthetic structures (0.04–0.06). Use the agent-field null anyway.
8. **Message pull.** The cross-day placebo is calibrated without shared drives, but a day-level shared content drive passes it 100% of the time (H29: use matched-age visible-vs-invisible comparisons). Use day clusters with a t reference: recipient-day clusters gave 0.12 under the null, because recipients on a day share the same sender messages. The same-day placebo's recency confound (H29: similarity falls 5–23× with message age) is not reproduced at this OU drift (0.09). Real recency decay is far stronger than the simulator's, so keep H29's matched-age design.
9. **Placebo dates.** The weekday-matched placebo is calibrated under a strong Monday effect. Unmatched placebos were *not* anti-conservative in this design (0.08): the Monday effect inflates the placebo variance as much as it shifts the mean. They give a biased effect estimate (obs − placebo mean is about the Monday effect) and lose power.

## 6. Data-quality finding: `activity_bins` drops events (fixed in a sidecar)

`build_derived.build_activity_bins` bins events with `active_min = (active_offset_s + (t − win_start)) // 60`. The grid uses `active_offset_s // 60 + minute`, and the two are joined on `(pt_date, minute, active_min, agent)`. With a = `active_offset_s` mod 60, every event whose second-of-minute b satisfies a + b ≥ 60 is dropped, so a share of about a/60 of each day's events is lost.

**Scale of the loss:**
- per-day talk counts correlate with a at −0.99 (turns at −0.999);
- 305 of 389 days keep less than 80% of their talk events;
- the median day keeps 53%;
- days with a = 59 s keep 1–2%.

**Every event-derived column is affected** (talk, idle, consolidate, other_event, turns, paused), and so is `state`:
- 24% of agent-minute states change;
- the non-holdout active share goes from 0.43 to 0.58;
- the talk share goes from 0.056 to 0.103.

The loss depends only on an event's second, so it is random within a day. It thins activity at a day-specific rate: rates and co-activation are understated and vary from day to day for no behavioral reason.

**Downstream:**
- `outages` / `stall_minutes` / `reasons` (they read `state`). Joint silences are over-counted on high-a days.
- Hypothesis spins built from `activity_bins`: H02, H04, H05, H08, H09, H12, H13, H15, H19, H22, H25, H26, H30, H33, H36, H38, H49.

**Fix:** `activity_bins_fixed.py` uses identical code but joins on `(pt_date, minute, agent)` and takes `active_min` from the grid. Its `--verify` shows every eligible event recovered: 170,870 of 170,870 roster-agent talk events (the remaining 2,623 are the Claude Code agent's, excluded by design), and median per-day turn recovery of 1.000. It writes `activity_bins_fixed.parquet`, the same schema and rows. DQ7 should apply the same fix in `build_derived.py`, then rebuild `outages`.

## 7. Limits

- **Coupling truth is model-specific.** `g_true` follows H25's equilibrium Curie–Weiss formula. Parallel kinetic dynamics with persistence and delays map onto equal-time gains through a model-dependent curve, so calibrate the estimator against the planted J. Tests recover J by pseudo-likelihood, not by equal-time g.
- **Rate matching is approximate under coupling and fields.** Compensation is first-order and fields are zero-mean in the logit, so marginal activity drifts by a few percent at J ≈ 1. Hawkes room scope matches rates only approximately.
- **The independent baseline carries the real schedule.** Its 2-h smoothed own-activity profiles include genuine shared slow variation, which could itself be slow coupling. `profile="flat"` removes it.
- **Content is a stylized O(32) Gaussian world** (anisotropic, PR ≈ 8, statement noise calibrated to H26), not real embedding geometry. There is no self-repetition or templating (H12) and no style field (H13).
- **No consolidation, error-turn or context-erasure dynamics.** Reason codes are only pre, post, infra and pause; consolidation is not simulated.
- **Kicks** are field or catalytic pulses on activity only. There are no content responses to kicks yet, and no human agents.
- **Projects** have no artifact-mention process: a label is observed wherever real labels exist.
- **Signed graphs** come from a separate generator (ordered logit on synthetic reply structures), not the skeleton's replies; DQ2's `reply_pairs` would be the natural skeleton.
- **Size table.** 100 replicates leave ±0.04 binomial error at α = 0.05. Toy skeletons are used outside the activity family. Statistics are representative implementations, not each hypothesis's exact estimator: re-run `calibrate` on your own estimator via the `FAMILIES` hooks.
