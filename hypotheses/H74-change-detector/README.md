# H74: An operator-grade change detector

**Status:** exploratory round 1 done (2026-10-04): **mixed.** Card, channels, rule and predictions written 19:25 UTC before any real-data score; Amendment 1 (~20:25 UTC) after the synthetic study, before real data. `analysis/confirm.py` frozen, guarded and dry-run (PARTIAL on stand-ins); **not run**.
- **Primary (documented scaffold_tool changes, 23 events):** fused AUC 0.68 [0.54, 0.82], hit 0.78, random-date p 0.059 (Holm 0.59): mixed by the card's rule.
- **The fused max-rule alarms too often:** per-day placebo FAR 0.18 (34 placebo days; predicted ≤ 0.10), 86/282 days in alarm. Real day-to-day noise in the mix (M), oracle-format (O) and drive (D) channels is heavier-tailed than in the synthetic streams.
- **The schema channel S is the operator-grade part:** 0/34 placebo false alarms, and it dates format changes to the day with the changed fields named: NE14 (03-24), NE17 (04-14), the undocumented NE45 (07-29), and six provider API response-format changes that no catalog lists.
- **Undocumented steps:** 6/6 are inside a fused alarm window (random-date p 0.13); 4/6 are attributable to the channel built for them (NE45 S; NE43a, NE43b D; the 03-31 outage D + O). NE40 and NE39 are not.
- **Rival R1 (topic shift):** the fused score beats it on undocumented steps (ΔAUC +0.30 [0.01, 0.59]) and loses on goal changes (−0.16 [−0.29, −0.04]); content alone stays the goal detector (AUC 0.89).
**Question served:** **Q5** (what can an operator do?: a monitor with measured hit and false-alarm rates). Secondary: Q7 (a detector computable from public logs) and Q2 (separating platform steps from goal fields).
**Fields:** stat mech, info theory, sociophysics
**Literature:** none of the notes in `literature/` covers change-point detection. Cited from memory (†): Page, *Biometrika* 41, 100 (1954)† (CUSUM); Basseville & Nikiforov, *Detection of Abrupt Changes* (1993)†; Lin, *IEEE Trans. Inf. Theory* 37, 145 (1991)† (Jensen–Shannon divergence).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Population N(t), **day-present variant** (H36); Regime (the detector crosses regime boundaries on purpose: the transition is the object, exception (c)); Driving / external field; **Content centroid shift (R1)** (H36 named variant); H38's *joint silence*; Action (turn-merged) via the ledger's calls. **New named variants proposed** (not edited into DEFINITIONS.md): *record signature*, *synchronous within-agent shift*, *change-point alarm (multi-channel)*, defined under Model.
**From:** HH268 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` ("Making the faithful ones better") · **Models:** `physics-models/02-nonequilibrium-ising/` (a step in the drive or the rules of a kinetic system; synchronous response as the platform signature), `physics-models/11-vector-spins/` (content centroid as the order parameter of a field step)
**Data inputs (shared tables first):** `call_windows`, `actions` + `actions_bash_head_fixed` (error_class), `kicks_classified`, `outages_fixed/stall_minutes`, `calendar`, `roster`, `embeddings/agent_day*` (bge and gte), H56's `event_catalog.parquet` (the CHANGELOG-derived catalog, read as data), and one numbers-only pass over raw `events` and `computer_use_turns` for record signatures and search-answer format counts (no text kept).

## Question
Does a multi-channel change-point monitor, combining H36's topic shift, H56's log features (event mix, tool schemas, answer stylometry) and the schedule/outage signals, recover documented NEs and find undocumented ones (NE40, NE45, NE43's two steps) at a low false-alarm rate?

**Faithfulness lever (HH268):** axis G (dated platform changes as ground truth) and axis I (one rule across all regimes). The scorecard says whether it moved them.

## Design: two layers (Vivian, 2026-10-04)
- **Replication (role `replication`):** the same daily detector on every non-holdout active day (all regimes; 51 goal periods, of which 35 have non-holdout days). Per goal period: hits on the period's catalogued events and the per-day false-alarm rate on its placebo days. One `G<NN>/` folder per period.
- **Period-native tests (role `native`), each with its own dated prediction in its folder:**
  - **NE43** (#51; bookends stop after 2026-08-04, nudges after 08-20): two undocumented operator steps in one period with a dense, stable baseline. Does the drive channel date both steps blind, and nothing else in #51?
  - **NE45** (#51, 2026-07-29): an undocumented tool-schema change. Does the schema channel date it, and does it stay silent at #51's eleven roster joins?
  - **NE40** (#38, 2026-04-20): the undocumented search-oracle swap, shipped with the documented NE18. Does the generic answer-format channel date it?
  - **NE14** (#36, 2026-03-24): the regime II → III boundary, the largest documented platform change in the non-holdout data. A positive control: platform channels should fire and the content channel need not.

## Model
**From:** `physics-models/02-nonequilibrium-ising` (a kinetic system whose drive or update rules change in one step) and `physics-models/11-vector-spins` (the content order parameter).

**Degrees of freedom.** One active day d is one time step. Each day gives five channel vectors:
- **S, schema (platform rules).** A *record signature* is the record type plus its sorted field names and value types: for `events` the action type and the keys and JSON types of `data` (excluding the provider-shaped `output`); for `computer_use_turns` the keys and types of `agent_action` and the non-null status of `output`, `error` and `system`. A platform change that adds, renames or retypes a field creates a new signature or retires an old one.
- **M, mix and per-call numbers (agent behavior under the rules).** Per agent-day: shares of call kinds (cu_action, talk, pause, wait, consolidate, search, session start/stop, room move), records per call, log medians of call turnaround, prompt tokens (`tok_in + tok_cache_read`), output tokens, reasoning characters, the cache-read share, and the share of turns with an infrastructure `error_class`.
- **O, oracle output format.** Per history-search answer, generic format counts: length, lines, blank lines, markdown headers by level, bold markers, bullets by marker (`*`, `-`, `•`), numbered items, em dashes, non-ASCII share, and an opening-phrase class. No text is kept.
- **D, drive and schedule (operator).** Window start time of day and length, documented hours, counts of pause/resume bookends, nudges and human messages, the joint-silence share (`outages_fixed`), the spread of agents' first-call times and the number of day-present agents.
- **C, content.** H36's R1 (centroid shift of the raw agent-day embedding means between consecutive active days), computed with bge and with gte.

**Change model.** Each channel x_k(d) is stationary with slow drift except at steps. A platform step changes the rules for every agent at once, so per-agent behavior features shift **synchronously** (the platform signature; H56's post hoc lead). A goal step is a field step on content (H36, H54). An operator step changes the drive features. A roster step changes composition but not each incumbent's behavior.

**Scores.** For each scalar feature, the robust trailing z against the previous B = 10 non-holdout active days: z = (x(d) − median) / (trimmed SD × 1/0.70), the consistency factor from the Known issues (H36), with an SD floor of 0.05 × |median| + 10⁻⁶ to avoid zero scales. Channel scores:
- **z_S** = 4 × the number of *platform-wide* signature changes on d: a new signature (≥ 5 records on d, ≥ 2 distinct agents or a non-agent record type, absent from the previous 10 active days) or a retired one (≥ 2% of its record type and ≥ 2 agents in the baseline, expected count on d ≥ 10, zero on d). Signatures carried by an agent in its first 3 active days are attributed to the roster and not counted.
- **z_M** = max over M features of |median across day-present agents of the within-agent z| (agent's own trailing baseline; ≥ 3 agents with a baseline). The median across agents is the synchronous-shift statistic.
- **z_O** = max over O features of |z| of the day's median answer (days with ≥ 3 searches; otherwise missing).
- **z_D** = max over D features of |z|.
- **z_C** = mean of the one-sided R1 z over the two embedding models.
- **Fused score** Z(d) = max(z_S, z_M, z_O, z_D, z_C). **Alarm rule (pre-registered):** Z(d) ≥ τ = 4. Hit = an alarm on day −1, 0 or +1 of an event's day 0 (offsets in non-holdout active days).

**Rivals.**
- **R1 topic shift alone** (H36's R1, the best single detector so far): the fused monitor adds nothing beyond z_C.
- **R2 EP and fluctuation alarms** (H56, H36): reported from their cards; they missed the platform steps.
- **R3 calendar:** Mondays and returns from gaps fire every channel (H36); weekday-matched placebos test this.
- **R4 composition:** roster changes fire the mix channel; within-agent baselines and the first-3-days rule test this.

## Data scheme (`scheme/`)
- `scheme/scan_signatures.py`: one pass over raw `events` and `computer_use_turns` (orjson, ≤ 2 processes). Keeps, per record: PT date, agent code, record type, signature hash (and the signature string, which holds field names and JSON type names only), and for `SEARCH_HISTORY` the O-channel counts. **No text is stored.** Held-out days are scanned (the raw files are not split by day) but dropped before writing; an assertion checks that no held-out day is written.
- `scheme/build.py`: daily channel features from the shared tables and the scan, non-holdout days only, with `_provenance.json`.
- **Output:** `data/processed/H74-change-detector/` with `signatures_daily.parquet` (day × record type × signature: counts, distinct agents), `signature_dict.parquet` (hash → field-name/type string), `search_format.parquet`, `agent_day_features.parquet`, `day_features.parquet`, `scores.parquet` (day × channel score, fused score, alarm), `events.parquet` (the evaluation catalog), results in `replication/`, `native/`, `synthetic/`, `confirm_dryrun/`. Budget ≤ 50 MB.
- **Evaluation catalog.** H56's CHANGELOG-derived `event_catalog.parquet` (classes scaffold_tool, scaffold_prompt, scaffold_family, goal, goal_prompt, roster, room, operator, operator_schedule; infra_invisible and excluded rows dropped), plus an **undocumented** class: NE39 (2025-07-01), the history-search outage (2026-03-31), NE40 (04-20), NE45 (07-29), NE43a (08-05) and NE43b (08-21). The blind scoring runs on the CHANGELOG + roster + goal + room catalog only; the undocumented dates are scored afterwards.
- **Regimes covered:** all non-holdout active days, I → III, in time order. Trailing baselines skip held-out days.

## Observables
1. **Per class** (scaffold_tool, scaffold_prompt, scaffold_family, operator, operator_schedule, goal, roster, room, undocumented): hit rate at τ; AUC of max Z over days −1..+1 vs placebo days (bootstrap CI); the same for each channel; best channel per class.
2. **False alarms:** per-day FAR on placebo days (non-holdout active days ≥ 3 active days from every catalogued event); window FAR on 3-day placebo windows; Monday-placebo FAR.
3. **Random-date null:** per class, event days replaced by random eligible days of the same regime (2,000 draws); p for the hit rate and for mean max Z.
4. **Blind change-points:** alarm days with no catalogued event within ±1 day, ranked by Z, with their channel; the rank and channel of NE39, NE40, NE43a/b, NE45 and the 03-31 outage among them; matches to the DQ9 candidate list.
5. **Rival comparison:** AUC(Z) vs AUC(z_C alone) per class (paired bootstrap); hit gain of the fused alarm over z_C ≥ τ at matched window FAR.

## Null / baseline
- **N1 placebo days** (the false-alarm rate) and **weekday-matched placebos** (R3).
- **N2 random dates** per class (as H36 and H56).
- **N3 synthetic streams** at real counts (below): planted steps of each kind, plus nuisance changes (roster joins with a new provider, goal steps with a mix change, Mondays).

## Impostor table (STANDARDS §1)
| Impostor | How H74 handles it |
| --- | --- |
| Scheduler field | A schedule change is a target (channel D), not a confound. Within-day synchrony is not used. Day-length and roster changes that move other channels are reported as such, and weekday placebos check the calendar. |
| Exogenous field (kickoff, goal, operator) | Goal kickoffs are their own class. Channel-specificity (content for goals, schema and synchronous mix for platform steps) is the test; a platform alarm that fires on kickoffs counts as a false attribution in the class table. |
| Shared model priors (family, style) | Within-agent baselines remove family levels. A family-targeted change (scaffold_family) is scored separately; a platform-wide signature needs ≥ 2 agents. |
| Contemporaneous convergence | Not applicable: no influence or copying claim is made. The detector reports dated changes, not who caused them. |

## Synthetic validation (axis F; `analysis/synthetic.py`; before any real-data score)
Daily feature streams at real counts: 200 active days, N from 4 to 27 agents (the real roster path), calls per agent-day and searches per day drawn from the real non-holdout marginals (counts only). Each agent has its own baseline mix (Dirichlet) and per-call numbers (lognormal), with day-to-day noise and a slow drift. Signature streams have 20–60 stable signatures plus rare (≤ 1%) one-agent signatures. Planted steps (10 of each per run, 20 runs): **schema** (one signature renamed for all agents), **mix** (a synchronous +30% shift of one call-kind share for all agents), **oracle** (bullet marker swap in search answers), **drive** (bookend count to zero; start time +30 min), **content** (a new goal direction). Nuisances: **roster** (+3 agents of a new provider with their own signatures and mix), **goal + mix** (a task change that moves the mix of half the agents), Monday jumps.
Checks: per-channel hit rate at τ ≥ 0.8 on its own step type; per-day FAR of the fused alarm ≤ 0.10 on clean days; schema alarms on ≤ 0.2 of roster joins; mix alarms on ≤ 0.3 of goal + mix steps.

## Amendment 1 (2026-10-04 ~20:25 UTC; after the synthetic study, before any real-data score)
1. **Floors.** The relative floor (5% of |median|) is dropped: on log-scale features it exceeded the real day-to-day noise by 5× (log prompt ≈ 10.5 → floor 0.53) and blinded channel M. Only absolute floors remain (shares 0.01; logs and records per call 0.05; bookends 0.25 because the baseline is exactly 2 per day; search-format counts 1.0 because day medians of small counts are integer-valued).
2. **Synthetic noise calibrated** to the real non-holdout within-agent day-to-day dispersion (median over agents of 1.4826·MAD(Δx)/√2: log turnaround 0.13, log prompt 0.10, log output 0.11, records per call 0.02, at its floor 0.05). Only the generator changed. Mix steps are now planted at 3 and 5 SD.
3. **Synthetic result** (20 runs × 24 planted steps; `synthetic/summary.json`). Own-channel hit rate at τ = 4: schema S 1.00, oracle O 0.80, drive D 0.97, content C 0.98, mix M 0.90 at 5 SD and **0.05 at 3 SD**. Fused hit: 1.00 / 0.80 / 0.97 / 0.98 / 0.93 / 0.25. Fused per-day FAR on clean days 0.051 (S 0, M 0, O 0.022, D 0.025, C 0.005). Nuisances: schema alarms at new-provider roster joins 0.00 (newcomer rule), M alarms at goal + mix steps 0.00, fused alarms at roster joins 0.32 (through n_present in D). P0 passes, with one limit: **the mix channel sees only synchronous shifts of ≳ 4 within-agent SD**. A real miss on a smaller platform change is uninformative.

## What I had seen (disclosure)
I have read the H36 and H56 cards in full. They report that NE40 is datable by answer stylometry (bullet markers) and NE45 by the renamed search-date fields, that NE43's bookends stop on 08-04 and nudges on 08-20, that R1 detects goal changes at AUC 0.95, and that neither EP nor the fluctuation alarm detects documented scaffold changes. Channels S and O are generic versions of what H56 found by hand: **NE40 and NE45 are therefore not blind tests of channels O and S**, and they are scored as recoveries, not discoveries. The prospective tests are the documented CHANGELOG scaffold events (no detector has found them so far) and the unexplained alarms. I have computed no detector score on real data.

## Prediction
*Written 2026-10-04 19:25 UTC, before the synthetic study and before any real-data score. Credences in brackets.*
- **P0 (synthetic, F).** All checks above pass [0.6]. If a channel misses its own step type (< 0.8), its real-data misses are uninformative.
- **P1 (primary: documented scaffold_tool changes).** AUC of Z (max over −1..+1) vs placebo ≥ 0.70 with CI above 0.5 [0.4], hit rate ≥ 0.4 [0.35], random-date p < 0.05 [0.4]. **Supported** if AUC CI > 0.5 and p < 0.05; **failed** if AUC ≤ 0.60 or p > 0.10; mixed otherwise. The best channel for scaffold_tool is S or M [0.6].
- **P2 (undocumented).** An alarm within ±1 day of NE45 [0.8], NE40 [0.6], NE43a [0.6], NE43b [0.7], NE39 [0.4] and the 03-31 search outage [0.5]; ≥ 4 of 6 [0.5].
- **P3 (goal changes, specificity).** z_C AUC ≥ 0.9 [0.8]; z_S AUC ≤ 0.6 [0.7]; fused hit ≥ 0.6 [0.6].
- **P4 (false alarms).** Per-day placebo FAR of the fused alarm ≤ 0.10 [0.5]; the Monday FAR is no more than 2× the other placebos [0.5].
- **P5 (rival R1).** The fused monitor beats z_C alone on scaffold and operator classes (AUC gain ≥ 0.1) [0.6] and loses ≤ 0.05 AUC on goal changes [0.7].
- **P6 (roster, R4).** Roster joins hit ≥ 0.3 (composition moves M) [0.5], but platform-wide schema alarms at roster joins ≤ 0.2 [0.6].
- **P7 (unexplained alarms).** ≥ 3 unexplained alarm days, of which ≥ 1 matches a DQ9 candidate or a known data anomaly [0.5]. Each is listed for the shared catalog.
- **Multiplicity.** Primary tests: P1 (scaffold_tool, AUC and random-date p) and P2 (count of undocumented recoveries). Everything else is descriptive; Holm over the class tests is reported.
- **Replication rule for a period README:** *supported* if every non-holdout scaffold, operator or undocumented event in the period is hit and the period's per-day placebo FAR ≤ 0.10; *failed* if no such event is hit; *mixed* otherwise; *descriptive* if the period has no such event (FAR and goal-change hits reported).

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [NE14](goalperiod-subhypotheses/NE14/README.md) | native | supported | 03-24: S = 16 (new pause and search tool schemas, CONSOLIDATE events; WAIT retires); M 2.6 (missed); C 1.8 |
| [NE40](goalperiod-subhypotheses/NE40/README.md) | native | failed | O ≤ 2.8 at 04-20; fused alarm only through an unrelated M cache-share jump on 04-21; 03-31 outage caught (D 102.8, O 4.3) |
| [NE43](goalperiod-subhypotheses/NE43/README.md) | native | mixed | 08-05 D = 8 (bookends 2 → 0); 08-21 D = 6.9 (nudges → 0); quiet-day alarms 2/7 (O) |
| [NE45](goalperiod-subhypotheses/NE45/README.md) | native | supported | 07-29 S = 12 (startDay/endDay int → startDate/endDate str); S at 1/8 #51 join windows |
| G02–G51 (35 folders) | replication | 17 supported · 6 mixed · 4 failed · 8 descriptive | per-period hits on scaffold/operator/undocumented events and placebo FAR; see each `G<NN>/README.md`. With 30% of days in alarm, a 3-day window hits by chance about half the time, so period "supported" verdicts are weak evidence. |

## Results
*Round 1, 2026-10-04; non-holdout only: 282 active days, 217 catalogued events (H56's CHANGELOG catalog + 6 undocumented), 34 placebo days (7 Mondays). Scripts: `scheme/scan_signatures.py`, `scheme/build.py`, `analysis/h74lib.py`, `synthetic.py`, `run_detector.py`, `natives.py`, `write_period_folders.py`, `confirm.py`. Numbers: `data/processed/H74-change-detector/{replication/results.json, scores.parquet, replication/changepoints.parquet, native/results.json, synthetic/summary.json}`. Figures: `figures/summary_obs.pdf`, `figures/synthetic.pdf`.*

**Operating characteristics (window = days −1..+1; AUC vs placebo windows, 1,000-draw bootstrap; random-date null 2,000 draws, same regime).**
| Class (n) | fused hit · AUC [CI] · p | best channel (AUC) | S hit · AUC |
| --- | --- | --- | --- |
| scaffold_tool (23) | 0.78 · 0.68 [0.54, 0.82] · 0.059 | fused 0.68; C 0.65; S 0.63; D 0.63 | 0.26 · 0.63 |
| scaffold_prompt (17) | 0.53 · 0.51 · 0.77 | D 0.61 | 0.18 · 0.59 |
| scaffold_family (9) | 0.78 · 0.62 · 0.27 | C 0.69; S 0.67 | 0.33 · 0.67 |
| operator (4) | 1.00 · 0.81 · 0.21 | D 0.88 | 0.50 · 0.75 |
| operator_schedule (3) | 1.00 · 0.76 · 0.15 | D 0.91 | 0.67 · 0.83 |
| goal kickoff (35) | 0.69 · 0.68 · 0.16 | **C 0.89 [0.80, 0.96]** (p 0.007) | 0.31 · 0.66 |
| roster (27) | 0.63 · 0.58 · 0.63 | D 0.66 | 0.26 · 0.63 |
| room (6) | 0.83 · 0.81 · 0.44 | C 0.97 | 0.50 · 0.75 |
| undocumented (6) | 1.00 · 0.86 [0.73, 0.96] · 0.13 | **D 0.89 [0.74, 0.99]** (p 0.031) | 0.33 · 0.67 |

Per-day placebo FAR: S 0.00, C 0.00, O 0.06, M 0.09, D 0.09, fused 0.18 (window 0.44; Mondays 0.29 vs 0.15 otherwise).

**Outcome vs prediction.**
| Prediction | Observed | Verdict |
| --- | --- | --- |
| P0 synthetic: own-channel hit ≥ 0.8; fused FAR ≤ 0.10; nuisance alarms low | S 1.00, D 0.97, C 0.98, O 0.80, M 0.90 at 5 SD (0.05 at 3 SD); FAR 0.051; schema at roster 0.00 | held (M sees only ≳ 4 SD shifts) |
| P1 scaffold_tool AUC ≥ 0.70, hit ≥ 0.4, p < 0.05 | AUC 0.68 [0.54, 0.82], hit 0.78, p 0.059 | **mixed** (rule: AUC > 0.60 and p ≤ 0.10) |
| P2 undocumented ≥ 4/6 | 6/6 in window (p 0.13); attributable 4/6 | held as counted; weak beyond chance |
| P3 C AUC ≥ 0.9; S AUC ≤ 0.6 on goals; fused hit ≥ 0.6 | 0.89; 0.66; 0.69 | mostly failed (S fires near kickoffs: new periods bring new tools) |
| P4 fused per-day FAR ≤ 0.10; Monday ≤ 2× others | 0.18; 0.29 vs 0.15 (1.9×) | failed; held |
| P5 fused beats C on scaffold/operator by ≥ 0.1; loses ≤ 0.05 on goals | scaffold_tool +0.04 [−0.15, 0.22]; operator +0.12 [−0.29, 0.63]; undocumented +0.30 [0.01, 0.59]; goals −0.16 | failed |
| P6 roster hit ≥ 0.3; S at roster ≤ 0.2 | 0.63; 0.26 | held; failed (marginal) |
| P7 ≥ 3 unexplained alarms, ≥ 1 matching a known anomaly | 17 unexplained: 4 joint-silence (stall) days, 2 schedule anomalies, 5 oracle-format, 2 mix, 1 content, 2 provider API format changes (S), 1 presence | held |
| Natives | NE14 supported; NE45 supported; NE43 mixed; NE40 failed | 2 / 1 / 1 |

**What it means.**
1. **A schema diff is a nearly free, precise platform monitor.** Hashing field names and value types of every log record and alarming on platform-wide new or retired signatures gave 0 false alarms on 34 placebo days. It dated NE14, NE17 and NE45 to the day and named the changed fields. It also found undocumented provider API format changes: Anthropic usage fields (2026-02-09) and a `stop_details` field (2026-04-01); Gemini response envelopes (2025-12-19, 2026-05-06); OpenAI response items (2026-07-13/14). Prompt-only and behavioral changes leave no schema trace, so S cannot see them (scaffold_prompt hit 0.18).
2. **Operator steps are visible in plain counters.** Bookend and nudge counts dated both NE43 steps; schedule and joint-silence features flagged the 03-31 stall day and three other stall days.
3. **Goal changes remain a content problem** (C AUC 0.89; H36 replicated with both embedding models).
4. **The fused max-rule is not operator-grade as tuned.** Heavy-tailed mix and format statistics fire on 6–9% of quiet days each. The synthetic streams were too Gaussian.
5. **The oracle swap (NE40) needs a presence rule, not a z-score.** The marker H56 used appears in a minority of answers on 55/61 days, then never. Day medians and means of counts do not move far enough.

**Caveats.**
- Only 34 placebo days survive the dense catalog, so FARs have wide intervals (Wilson 95% for 6/34: 0.08–0.33).
- NE40 and NE45 are not blind tests (H56 found them by hand; disclosed before the run).
- The catalog's merge dates can miss deploy dates by a day.
- S signatures from provider responses change when providers change, which is a real change but not a village platform change.
- One trailing baseline length (10 days) and one threshold (τ = 4) were tested. The holdout is not run.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R1 topic shift alone (H36); R2 EP and fluctuation alarms (H56, H36; from their cards); R3 calendar; R4 composition.
**Locked holdout used for confirmation:** none yet (`analysis/confirm.py` frozen; dry run on non-holdout stand-ins gives PARTIAL: C1 fails on S's hit rate 0.26 < 1/3, C2–C4 pass).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | All channels are counts, field names, format counts and embedding means from logs; one rule across regimes I–III. Provider-shaped responses make S partly provider-specific. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Trailing robust z assumes near-Gaussian day noise; the real tails broke the FAR (0.18 vs 0.05 synthetic). |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | AUC CIs above 0.5 for scaffold_tool, goal, undocumented; random-date p < 0.05 only for C on goals and D on undocumented; fused p 0.059. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | Channel specificity largely as designed (S for schema, D for operator, C for goals); M rarely fires at platform steps. |
| E interventional | predicts the change across a natural experiment | 1 | NE14 and NE45 dated by S, NE43a/b by D; NE40 missed. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Synthetic own-channel recovery 0.80–1.00 at FAR 0.05, but the synthetic noise model was too light-tailed; one data bug (Int8 start time) found and fixed with no effect on results. |
| G ground truth | agrees with known structure | 2 | Dated documented and undocumented changes as the answer key; S names the exact changed fields at NE14, NE17 and NE45. |
| H comparative | beats the named rivals | 1 | Beats R1 on undocumented steps (+0.30); loses on goals (−0.16); beats H56/H36, which detected no scaffold change. |
| I transfer | holds in other same-mode periods, including the holdout | 1 | Same rule over 16 months and three regimes; holdout not run. |

**Faithfulness lever (HH268):** G moved (dated changes, with S naming the fields); I partly (one rule over all regimes, but the fused FAR does not transfer from synthetic to real).

## Round 2 redirects
**What the direction is really after:** a cheap monitor that tells an operator, on the day, that the platform, the drive or the goal changed, with a known false-alarm rate.
- **H74-R1. Precision monitor.** S (schema diff) + D's counters (bookends, nudges, hours, joint silence) + C (topic) only; calibrate each channel's threshold on placebo days to a per-day FAR of 0.02 and test on the holdout.
- **H74-R2. Presence/retirement rule for formats.** Treat format markers (bullet styles, headers) like signatures: alarm when a marker present on ≥ 8 of the last 10 days disappears. Retest NE40.
- **H74-R3. Heavy-tailed baselines.** Replace the Gaussian trailing z with empirical quantiles over 20–30 days, or with log transforms for counts (human messages fall from ~150 to ~4 at NE39 without an alarm).
- **H74-R4. Provider API changes as natural experiments.** The six dated format changes are candidates for family-targeted DiD (H56-R2's sign synchrony).
- **H74-R5. Holdout.** Run `confirm.py` after sign-off.

## Notes
- 2026-10-04 19:25 UTC: card written before any detector score (see disclosure).
- ~19:40–20:25: synthetic study (3 passes; generator drift bug and floor design fixed; Amendment 1).
- ~20:30: native predictions written in NE14, NE40, NE43, NE45 before the real-data run.
- ~20:40–21:10: scan (4 min, 2 processes), build, detector, natives, period folders, estimates, confirm dry run. A start-time Int8 overflow in `build.py` was fixed and rerun; results unchanged to 2 decimals.
- Compute and disk: local, ≤ 2 processes; ≈ 10 CPU-min; `data/processed/H74-change-detector/` ≈ 3 MB. No text stored (field names and type names only).
- **Data findings for the shared catalog** (not edited): undocumented provider API response-format changes on 2025-12-19 (Gemini: `responseId`, `sdkHttpResponse` added), 2026-02-09 (Anthropic usage subfields), 2026-04-01 (Anthropic `stop_details` added), 2026-05-06 (Gemini `usageMetadata` subfields), 2026-07-13/14 (OpenAI response items: `phase`, `encrypted_content`); the first SEARCH_HISTORY event in the (non-holdout, unbroken) record is on 2025-09-19, two weeks after NE04's 09-05 date, the same day as a CHANGELOG tool entry: either the tool deployed later than NE04 says or it went unused; a field-less variant appears once on 2026-02-19 and the `roomId` field is added on 2026-03-16; stall days flagged by joint silence on 2025-07-25, 2025-10-16, 2026-01-07/08, 2026-07-28.
- **Proposed shared-file changes** (not made): DEFINITIONS.md named variants *record signature* and *synchronous within-agent shift*; a shared `infra/shared/` schema-diff builder (scan_signatures logic) with `--verify`, since it is the cheapest platform monitor found so far; infra Known issue: H56's `event_catalog.parquet` is now an input to H74 and should move to `infra/shared/`.
