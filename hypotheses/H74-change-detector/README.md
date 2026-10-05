# H74: An operator-grade change detector

**Status:** **Round 2 (2026-10-05): mixed.** A leave-one-period-out calibrated monitor (schema diff ∪ operator counters ∪ H36's topic rule) has out-of-sample per-day FAR 0.085 [0.04, 0.17] (0.051 with round-1 provider dates catalogued, post hoc), goal hit 0.57 (p 0.003), all three undocumented drive steps dated by the counters at FAR 1/82; scaffold-tool hits at chance; NE40 dated by format presence rules (recovery); provider DiD unpowered (see Round 2). Round 1 (2026-10-04): **mixed.** Card, channels, rule and predictions written 19:25 UTC before any real-data score; Amendment 1 (~20:25 UTC) after the synthetic study, before real data. `analysis/confirm.py` frozen, guarded and dry-run (PARTIAL on stand-ins); **not run**.
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
| [NE14](goalperiod-subhypotheses/NE14/README.md) | native | supported (r2: supported, through C3 only) | 03-24: S = 16 (new pause and search tool schemas, CONSOLIDATE events; WAIT retires); M 2.6 (missed); C 1.8 |
| [NE40](goalperiod-subhypotheses/NE40/README.md) | native | failed (r2: mixed, presence rules) | O ≤ 2.8 at 04-20; fused alarm only through an unrelated M cache-share jump on 04-21; 03-31 outage caught (D 102.8, O 4.3) |
| [NE43](goalperiod-subhypotheses/NE43/README.md) | native | mixed (r2: supported, D3) | 08-05 D = 8 (bookends 2 → 0); 08-21 D = 6.9 (nudges → 0); quiet-day alarms 2/7 (O) |
| [NE45](goalperiod-subhypotheses/NE45/README.md) | native | supported (r2: mixed, S blinded by provider days) | 07-29 S = 12 (startDay/endDay int → startDate/endDate str); S at 1/8 #51 join windows |
| G02–G51 (35 folders) | replication | 17 supported · 6 mixed · 4 failed · 8 descriptive | per-period hits on scaffold/operator/undocumented events and placebo FAR; see each `G<NN>/README.md`. With 30% of days in alarm, a 3-day window hits by chance about half the time, so period "supported" verdicts are weak evidence. |
| G02–G51, round 2 | replication | 11 supported · 11 mixed · 13 failed (`Verdict (r2)`) | round-2 monitor per period: target hits and P2 false alarms; see each `G<NN>/README.md` Round 2 block |
| [NE39](goalperiod-subhypotheses/NE39/README.md) | native (round 2) | supported | 07-02: D3 4.5 > threshold 2.76 (human messages 100–167 → 4, 1, 1); Q and G miss |

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

## Round 2 (2026-10-05)
*Scope: redirects H74-R1 (precision monitor, calibrated on non-reserved placebo days only), H74-R3 (heavy-tailed baselines), H74-R2 (presence/retirement rule for formats) and H74-R4 (provider API changes as family-targeted DiD). H74-R5 (reserved data) is not run. Exploratory data only (`holdout_mask`); no `confirm.py` run.*

### Pre-registration (written 2026-10-05 03:50 UTC, before any round-2 statistic on real data)
**Disclosure.** I have read the round-1 results above and H36's round-2 results: the frozen topic rule C3 (alarm if R1 ≥ 3 or Z_cont ≥ 2) hits 0.55–0.64 of kickoffs at window FAR 0.02–0.07; the intraday rule fires in the first 30 min on 82–85% of kickoffs at a 7–9% placebo day-start rate; within-agent daily action mixes are overdispersed ~28× over multinomial; gte's Z_cont FAR is seed-fragile. Design facts computed for this plan (no detector score): the non-reserved placebo pool at ≥ 2 active days from every catalogued event has 82 days in 22 goal periods (34 days in 6 periods at round 1's ≥ 3 rule); search answers exist on 162 days from 2025-09-19; NE39 (07-01) is day index 39, so it has a full baseline. `natural-experiments.md` already says the Gemini bullet marker is present on 55/61 days before 04-17 and in 0/68 answers from 04-20. **NE40 is therefore a recovery test of the presence rule, not a discovery.** The prospective parts are the false-alarm rates, the other undocumented events and the class hit rates.

**Common evaluation.**
- Days: the 282 non-reserved active days; catalog: round 1's `events.parquet` (217 events; undocumented class scored separately, as round 1).
- **Placebo pool P2** (primary): days with a baseline (index ≥ 10), not a return from a reserved gap, and ≥ 2 active days from every catalogued event (82 days). A day ≥ 2 days from every event cannot be inside any event's hit window, so an alarm on it is a false alarm by the hit definition. Round 1's ≥ 3 pool (34 days) is reported for comparison, with window FARs.
- **Leave-one-period-out (LOPO) calibration.** For each goal period g and channel k, the threshold θ_k(g) is the conformal quantile of channel k's scores on the P2 days of all *other* periods: the ⌈(1 − α)(n + 1)⌉-th smallest of the n training scores, with α = 0.02 (if that rank exceeds n, the channel is off in that fold). Alarm on day d of period g if score_k(d) > θ_k(g). Every reported FAR is out-of-sample: each placebo day is judged by thresholds that never saw its period. With n ≈ 60–81 training days the rank equals n, so the rule is "above every training placebo day of the other periods"; its expected per-day FAR is ≈ 1/(n + 1) ≈ 0.013–0.016 per channel.
- Hit = an alarm on day −1, 0 or +1 (active-day offsets), as round 1. Classes: scaffold_tool (23), scaffold_prompt (17), scaffold_family (9), drive = operator ∪ operator_schedule (7), goal (35), goal_prompt (5), roster (27), room (6), undocumented (6). Random-date null per class: 2,000 draws of same-regime eligible days. AUCs are not the target here; hit at a fixed FAR is.

**R1: precision monitor (S + D counters + C).**
- **S:** round 1's schema diff (shared `schema_diff_daily` z_S = 4 × new + retired signatures), LOPO-calibrated (round 1 had 0 placebo alarms, so I expect θ_S = 0: alarm at ≥ 1 platform-wide signature change).
- **D counters:** n_bookends, n_nudges, n_human, documented_hours, window_min, js_share (start time, start spread and n_present are dropped: they fired on roster changes and gave round 1's largest unexplained alarm). Each feature is scored by R3's primary baseline (below); channel score D = max over the six; LOPO-calibrated.
- **C (topic):** H36's frozen C3 per-day score (bge-small, restate dedupe; `fmax(R1 − 1, Z_cont)`, alarm at ≥ 2; read as data from `data/processed/H36-reorganization-alarm/r2/rob_bge_restate/scores.parquet`). C3 is used **frozen** (its thresholds were set by H36 before this round), so its FAR is out-of-sample by construction; a LOPO-recalibrated C3 score is reported as secondary. Seed spread: the monitor is recomputed with each of H36's stored bge seed variants (base + s1…s8 = 9 surrogate seeds) and the range is reported. Intraday rule (max r1w over windows 0–1 of the day, H36 `intraday_bge`) is a secondary C channel, LOPO-calibrated.
- **Monitor alarm** = S ∪ D ∪ C.
- Predictions [credence]:
  - **P1a** per-channel OOS per-day FAR on P2 ≤ 0.03 for S, D and C [0.7]; union FAR ≤ 0.06 [0.55].
  - **P1b** hit rates: goal 0.45–0.70 [0.6]; scaffold_tool 0.20–0.40 [0.6]; scaffold_prompt ≤ 0.25 [0.7]; drive ≥ 0.5 [0.5]; room ≥ 0.5 [0.5]; roster ≤ 0.40 [0.6]; undocumented ≥ 3/6 [0.5].
  - **P1c** random-date p < 0.05 for goal and drive [0.5]; scaffold_tool p < 0.10 [0.4].
  - **P1d** vs round 1's fused alarm: per-day FAR falls from 0.18 to ≤ 0.06, and the scaffold_tool hit falls from 0.78 to ≤ 0.40, because most round-1 hits were chance at 30% alarm days [0.6].
  - **P1e** rival R1 (topic alone, frozen C3): the monitor adds ≥ 0.15 hit on the pooled platform + drive + undocumented events (scaffold_tool, scaffold_family, drive, undocumented) at a union FAR cost ≤ +0.04 [0.6].
- **Period rule (round 2, `**Verdict (r2):**` line in each G folder; added 04:05 UTC, still before any round-2 statistic).** Target events: scaffold_tool, scaffold_family, drive, undocumented and goal. *Supported* if every non-reserved target event in the period is hit by the monitor and no P2 day of the period alarms; *failed* if no target event is hit; *mixed* otherwise; *descriptive* if the period has no target event (its P2 false alarms are reported).
- **Kill rule.** The monitor is **operator-grade** if the union OOS per-day FAR ≤ 0.05 (Wilson upper ≤ 0.12), goal hit ≥ 0.45, drive hit ≥ 0.5 and scaffold_tool hit ≥ 0.20 with random-date p < 0.10. **Failed** if the union FAR > 0.10 or goal hit < 0.40. Mixed otherwise.

**R3: heavy-tailed baselines.**
- Transforms: log1p for counts (bookends, nudges, human messages) and log for minutes (window_min); documented_hours and js_share raw.
- Scores per feature:
  - **G** (round 1): raw value, Gaussian trailing z, B = 10, round-1 floors.
  - **L**: transformed value, Gaussian trailing z, B = 10 (floor 0.1 on log scales).
  - **Q (primary)**: transformed value, empirical-quantile exceedance over the previous B = 30 scored days (≥ 10 needed): e = (x − Q50)/(Q90 − Q50) above the median and (Q50 − x)/(Q50 − Q10) below it; denominators floored at 0.1 on log scales, 0.5 h for documented_hours and 0.01 for js_share. Score = |e|.
- Readouts: per-day exceedance on P2 at the nominal thresholds (G, L: |z| ≥ 4; Q: |e| ≥ 4); the LOPO-calibrated thresholds; NE39's n_human score and whether it alarms at the calibrated D threshold.
- Synthetic (100 worlds on the real skeleton): the real 282-day sequence (index, period, regime, reserved gaps); each D feature follows a level path with steps at the real documented changes, and day noise drawn by block bootstrap (blocks of 5) from the feature's real residuals on non-event days (residual = transformed value − rolling median of 9), which keeps the real tails. Planted on 12 random non-event days per world: bookends 2 → 0, nudges → 0, human messages × 0.03, window length × 0.75, js_share + 0.3. LOPO calibration on the synthetic values of the real P2 days.
  - **P3.0** G at |z| ≥ 4 has per-day FAR ≥ 0.04 on synthetic P2 (the round-1 failure reproduces) [0.6]; Q with LOPO thresholds has OOS FAR ≤ 0.03 [0.7]; planted-step hit ≥ 0.8 for the three count steps and ≥ 0.5 for the window and silence steps [0.6]. If Q's count-step hit is < 0.6, a real miss is uninformative.
  - **P3.1** NE39: Q alarms on n_human within day −1..+1 of 07-01 at the calibrated D threshold [0.75]; G does not (as round 1) [0.8].
  - **P3.2** real P2 exceedance at nominal thresholds: G ≥ 0.05, Q ≤ 0.04 [0.5]; the calibrated Q threshold is ≤ 10 [0.5].
  - **P3.3** NE43a and NE43b alarm under Q in the D channel at calibrated thresholds [0.7].
- **Kill rule.** R3 succeeds if NE39 alarms at a D-channel OOS per-day FAR ≤ 0.03. Failed if NE39 does not alarm under Q or L at the calibrated threshold.
- Secondary (descriptive): channels M and O rescored with Q baselines (log features as they are; shares via logit), LOPO-calibrated; do they add hits to the monitor at ≤ +0.01 union FAR?

**R2: presence/retirement rule for format markers.**
- Markers (per search answer, from `search_format.parquet`): presence (count > 0) of h1, h2, h3, bold, each bullet style (`*` with 3 spaces, `*`, `-`, `•`, numbered), em dash, en dash, non-ASCII, and each opening-phrase class (4 classes). A day is scored if it has ≥ 3 answers.
- **Retirement alarm** on day d for marker m: m was present on ≥ 8 of the previous 10 scored days, m is absent from every answer on d, and the binomial probability of zero answers with m, given the pooled baseline share s over those 10 days and today's n answers, is ≤ 0.01. Only the first day of an absence counts. Channel score P = number of markers retiring on d; alarm at P ≥ 1 (fixed in advance; the LOPO threshold is reported).
- Secondary: an **appearance alarm** (m present on ≤ 2 of the previous 10 scored days, present today in ≥ 3 answers from ≥ 2 agents).
- Synthetic (100 worlds): the real search-day skeleton (real answers per day and agents), 12 markers with baseline shares 0.05–0.9, day-level beta-binomial overdispersion set to the real day-to-day dispersion of presence shares; 6 planted retirements (share → 0) and 6 nuisance halvings per world. **P2.0** retirement hit ≥ 0.8 within ±1 day, per-day FAR ≤ 0.02, halvings alarm ≤ 0.1 [0.6].
- **P2.1** NE40: a retirement alarm within day −1..+1 of 04-20 [0.85; a recovery]. **P2.2** the 03-31 near-empty-answer outage alarms [0.7]. **P2.3** OOS per-day FAR on P2 search days ≤ 0.03 [0.5]; ≤ 10 retirement alarm days in all 162 search days [0.5]. **P2.4** NE45 (a tool-schema change, not an answer change) does not alarm [0.6].
- **Kill rule.** Failed if NE40 is not alarmed or the P2 FAR > 0.05.

**R4: provider API response changes as family-targeted DiD.**
- Events (round 1's S finds): 2025-12-19 Google, 2026-02-09 Anthropic, 2026-04-01 Anthropic (adjacent to the 03-31 search outage; disclosed confound), 2026-05-06 Google, 2026-07-13 OpenAI.
- Outcomes per agent-day (`agent_day_features`): log_out, log_turnaround, infra_err_share, rec_per_call, cache_share (cache_share is accounting-sensitive: a shift there is a measurement change, not behavior).
- Estimator: DiD = [mean over target-family agents of (post − pre)] − [same over other agents], pre = 5 active days before day 0, post = days 0…+4; agents need ≥ 3 days on each side; no reserved gap inside the window. Null: the same DiD for the same target family at every eligible non-event day of the same regime; two-sided p = rank of |DiD|. Holm over 5 events × 5 outcomes.
- **P4.1** at most 1 of the 25 tests survives Holm [0.7]: response-envelope changes are format changes, not behavior changes. **P4.2** if one survives, it is cache_share or infra_err_share (accounting or errors), not log_out or rec_per_call [0.6].

### Amendment R2-A1 (2026-10-05 ~04:30 UTC; after the synthetic study, before any round-2 statistic on real data)
*Synthetic: `analysis/r2_synthetic.py`, 100 worlds each; `data/processed/H74-change-detector/r2/synthetic_D.json`, `synthetic_presence.json`.*
1. **The pre-registered D channel is unpowered at FAR 0.02.** With real residual tails, D = max over six one-day feature scores needs LOPO thresholds of 21 (Q), 38 (L) and 84 (G). At those thresholds planted-step hits are 0.02–0.38 for every step type (OOS FAR 0.013–0.015, as designed). Nominal |score| ≥ 4 gives per-day FAR 0.12 (Q), 0.15 (L) and 0.14 (G): the round-1 failure reproduces, and Q alone does not cure it (P3.0: G part held; Q's power part failed).
2. **Amended D channel (primary from now on): D3-L-p2.** Only the three operator counters (bookends, nudges, human messages); log1p transform with a Gaussian trailing z (B = 10, floor 0.1; variant L); a **two-day persistence score**, p_f(t) = min(|z_f(t − 1)|, |z_f(t)|), dated on day t; D = max over the three; LOPO conformal threshold. Synthetic: OOS FAR 0.015, LOPO threshold ≈ 2.7, planted-step hit 0.62 (bookends), 0.55 (nudges), 0.38 (human × 0.03 or × 30). Persistence removes one-day spikes. It costs one day of delay, which the −1..+1 hit window allows. **A real miss of a count step is therefore only weakly informative (power 0.4–0.6).**
3. Hours, window length and joint silence leave the monitor. They become a descriptive **schedule/stall flag** (Q scores, nominal |e| ≥ 4), reported but not counted in the union FAR.
4. The pre-registered D (six features, one day) under G, L and Q is still computed and reported, as is Q with D3 and/or persistence. P3.1–P3.3 are read on the amended channel and on Q.
5. **Presence rule.** The pre-registered one-day retirement rule has synthetic per-day FAR 0.049 (p95 0.11) and hit 0.70: P2.0 failed. Real presence is overdispersed (median intra-day correlation ρ = 0.07 from day-to-day differences), so one absent day of a minority marker is weak evidence. **Amended rule (primary): evidence accumulates** over consecutive absent scored days, each adding log P(0) under a beta-binomial with the frozen baseline share and ρ = 0.07; alarm when the sum ≤ log 10⁻³ (`r2lib.presence_retire_acc`). Synthetic: FAR 0.017 (p95 0.037), hit within ±1 day 0.71, within 5 scored days 0.87 (0.99 for markers with share ≥ 0.4), halvings alarm 0.025. The detection delay is reported per event. The pre-registered rule is reported as secondary. P2.1–P2.4 and the kill rule apply to the amended rule; a hit within 5 scored days is reported next to the ±1 hit.

**Impostors in round 2.** Scheduler field: D tracks the schedule as a target; Monday placebo FAR is reported. Exogenous field: goal changes are their own class, and the C channel is H36's rule. Shared priors: within-agent baselines (M), family-targeted DiD with other families as control (R4). Convergence: n/a (no influence claim). No coupling claim, so the partition-contrast rule does not apply.

### Results (2026-10-05)
*Non-reserved data only: 282 active days, 217 catalogued events, P2 = 82 placebo days in 22 periods (P3 = 34). Scripts: `analysis/r2lib.py`, `r2_common.py`, `r2_synthetic.py`, `r2_monitor.py` (`--catalog prereg|ext`), `r2_presence.py`, `r2_did.py`, `r2_periods.py`, `r2_figures.py`. Outputs: `data/processed/H74-change-detector/r2/` (`monitor.json`, `monitor_ext.json`, `monitor_days.parquet`, `presence.json`, `did.json`, `synthetic_*.json`). Figure: `figures/r2_summary.pdf`. Wilson 95% intervals; random-date p from 2,000 same-regime draws; "chance" is the mean random-date hit.*

**Finding outside the plan: the pre-registered placebo pool contains two of round 1's own finds.** Two P2 days carry platform-wide schema changes: the Gemini (05-06) and OpenAI (07-14) provider response-format changes that round 1 listed under Notes, not in the catalog. Under the pre-registered catalog they count as S false alarms, and they push S's LOPO threshold to 8 or 20. S then misses NE14 (S = 16) and NE45 (S = 12). I report the pre-registered result as primary. A **post hoc catalog completion** (`--catalog ext`) adds round 1's five provider dates as a "provider" class; its results are labelled post hoc. The provider class hit (5/5) is circular (S found those dates) and is not evidence.

**R1: precision monitor S ∪ D3 ∪ C3 (LOPO, α = 0.02).**

| Readout | Pre-registered catalog (primary) | + provider dates (post hoc) |
| --- | --- | --- |
| LOPO thresholds | S 8 / 20 (provider days in P2); D3 2.1–2.8 | S 0 (alarm at ≥ 1 change); D3 2.1–2.8 |
| per-day FAR on P2, per channel: S · D3 · C3 (frozen) | 1/82 · 1/82 · 5/82 (0.061 [0.026, 0.135]) | 0/78 · 1/78 · 3/78 |
| **union per-day FAR on P2** | **7/82 = 0.085 [0.042, 0.166]** (Mondays 0/12) | **4/78 = 0.051 [0.020, 0.125]** |
| window FAR on P3 (round 1's 34 days) | 0/34 | 0/34 |
| alarm days (of 282) | 40 | 55 |
| goal kickoffs (35): hit · p (chance) | **0.57 · 0.003** (0.33) | 0.71 · < 0.001 (0.42) |
| drive = operator ∪ schedule (7) | 0.57 · 0.13 (0.31) | **1.00 · 0.002** (0.41) |
| undocumented (6) | 0.50 · 0.34 | 0.83 · 0.10 |
| scaffold tool (23) | 0.35 · 0.55 (0.34) | 0.52 · 0.23 (0.43) |
| scaffold prompt (17) · family (9) | 0.24 · 0.22 | 0.35 · 0.44 |
| roster (27) · room (6) | 0.26 · **1.00 (p 0.008)** | 0.41 · 1.00 (p 0.035) |
| pooled platform + drive + undocumented (45) | 0.38 [0.25, 0.52] · p 0.32 | 0.62 [0.48, 0.75] · **p 0.012** |

- **Channel by channel.** D3 (log counts, two-day persistence) alarms on 8 days: NE39 (07-02), NE43a (08-06), NE43b (08-21), four days within a day of other catalogued events (02-16, 05-22, 05-29, 08-24) and one P2 day (04-29, nudges). On the undocumented class alone it scores 3/6, p 0.034. S alone (post hoc catalog) hits the pooled 45 events at 0.33 (p 0.012), scaffold tool 0.26 (p 0.15) at 0/78 false alarms. C3 alone hits goals at 0.51 (p < 0.001) and fires on 5 P2 days (#11 twice, #19, #40, #51).
- **C3 seed spread** (H36's nine bge surrogate seeds): C3's P2 FAR 0.049–0.061, goal hit 0.51–0.54; the monitor's union FAR 0.073–0.085 (primary) and 0.051 in all nine seeds (post hoc catalog). The gte variant gives the same union FAR (0.085) with goal hit 0.63.
- **Round 1's fused alarm on the same pools:** FAR 17/82 = 0.21 [0.13, 0.31], 86 alarm days, pooled hit 0.84 against a chance level of 0.62. With a LOPO threshold it fires on 1 day and hits nothing: its heavy-tailed max has no operating point at FAR 0.02.
- **C variants.** A LOPO-recalibrated C3 (thresholds 3.0–4.0 on the encoded score) drops the union FAR to 3/82 (0.037) and goal hit to 0.40 (post hoc catalog: 2/78, goal 0.57, drive 7/7, scaffold tool 0.43, p 0.17). The intraday rule frozen at r1w ≥ 3 has P2 per-day FAR 0.061 and goal hit 0.80; LOPO-calibrated (threshold 5.7–11) it keeps goal hit 0.26.
- **Add-ons (R3 secondary).** M with quantile baselines (logit shares): LOPO FAR 1/82; it hits scaffold tool 4/23 (p 0.016, post hoc lead) and adds one P2 alarm to the monitor (FAR 0.085 → 0.098). O with quantile baselines never alarms at its LOPO threshold. Neither meets the "≤ +0.01 FAR" add-on rule cleanly; M is a lead for scaffold changes.

**R3: heavy-tailed baselines.**

| D variant | P2 exceedance at nominal 4 | LOPO threshold | D FAR (P2) | NE39 window max (alarm?) | NE43a · NE43b |
| --- | --- | --- | --- | --- | --- |
| G, 6 features, 1 day (round 1) | 0.085 | 83.5 | 1/82 | 8.0 (no) | no · no |
| L, 6 features, 1 day | 0.085 | 82.4 | 1/82 | 11.0 (no) | no · no |
| **Q, 6 features, 1 day (pre-registered primary)** | 0.073 | 20.8 | 1/82 | 11.0 (no) | no · yes |
| Q, D3, 1 day | 0.037 | 11.0 | 2/82 | 11.0 (no: tie with the threshold) | yes · yes |
| **L, D3, 2-day persistence (amended primary)** | 0.000 | **2.76** | **1/82** | **4.5 (yes, 07-02)** | **yes · yes** |
| G, D3, 2-day persistence | 0.000 | 2.97 | 1/82 | 2.0 (no) | yes · yes |

- The heavy tail of the day-level drive features is **joint silence** (stall days): js_share exceeds |z| 4 on 8.5% of P2 days. Hours and window length add 2.4%. The counters themselves (bookends, nudges, human messages) never exceed 4 on a P2 day once logged and required to persist for two days.
- **NE39** (human messages 100–167/day → 4, 1, 1, 2 from 07-01) alarms on 07-02 under the amended channel at a D FAR of 1/82. Under the pre-registered Q it does not: the Q threshold is set by silence and hours features.
- The **stall flag** (Q on hours, window, joint silence; nominal |e| ≥ 4, descriptive) fires on 17 days, 4 of them P2 days (0.049). It catches the 03-31 search-outage day (52.8), 04-16, 07-07, the January stall pair and 07-28.

**R2: presence/retirement rule for answer-format markers (16 markers, 129 scored search days, 37 P2 search days).**

| Rule | P2 false alarms | alarm days | NE40 (04-20) | 03-31 outage | NE45 (should stay silent) |
| --- | --- | --- | --- | --- | --- |
| **accumulating retirement (amended primary)** | 0/37 | 2 | **04-22: 2 scored days late** (both `*` bullet styles) | no | silent |
| one-day retirement (pre-registered) | 1/37 | 10 | **04-20** (same markers) | no | fires (h1) |
| appearance (secondary) | 0/37 | 3 | **04-20** (h2, `-` bullets, an opening-phrase class) | no | silent |

- NE40 is a recovery (disclosed). The prospective part holds: 0–1 false alarms on 37 placebo search days, 2–10 alarm days in 129. The one other primary alarm (05-12, em dash and non-ASCII) sits within a day of a catalogued event.
- Retirement plus appearance together date the oracle swap to the day: the old model's bullet styles vanish and the new model's headers and dash bullets appear on 04-20.

**R4: provider response changes as family DiD.** 12-19 and 02-09 are not estimable (the windows cross reserved days or lack two target agents with data). For 04-01, 05-06 and 07-13, no DiD survives Holm (0 of 25). **The design was unpowered by construction:** with 30–31 null windows per regime, the smallest rank p is 0.031, and Holm over 25 tests needs p < 0.002. *Post hoc lead:* the infrastructure-error share rises in the target family beyond all 31 null windows at 04-01 (Anthropic, +0.011; confounded with the 03-31 search outage) and 07-13 (OpenAI, +0.018).

**Outcome vs prediction (round 2).**

| Prediction | Outcome | Verdict |
| --- | --- | --- |
| P1a per-channel FAR ≤ 0.03; union ≤ 0.06 | S 0.012, D3 0.012, C3 0.061; union 0.085 (post hoc catalog 0.051) | partly (C3 fails) |
| P1b hits: goal 0.45–0.70; scaffold tool 0.20–0.40; prompt ≤ 0.25; drive ≥ 0.5; room ≥ 0.5; roster ≤ 0.40; undocumented ≥ 3/6 | 0.57; 0.35; 0.24; 0.57; 1.00; 0.26; 3/6 | held (all seven) |
| P1c random-date p < 0.05 for goal and drive; scaffold tool p < 0.10 | goal 0.003; drive 0.13 (post hoc 0.002); scaffold tool 0.55 | partly |
| P1d FAR 0.18 → ≤ 0.06 and scaffold-tool hit 0.78 → ≤ 0.40 | 0.21 → 0.085; 0.78 → 0.35 (round-1 hits were chance: 0.60) | partly |
| P1e monitor beats C3 alone by ≥ 0.15 pooled hit at ≤ +0.04 FAR | 0.22 → 0.38 at +0.024 | held |
| **R1 kill rule** (operator-grade: union FAR ≤ 0.05, goal ≥ 0.45, drive ≥ 0.5, scaffold tool ≥ 0.20 with p < 0.10) | FAR 0.085; scaffold-tool p 0.55 | **mixed** (post hoc catalog: FAR 0.051, scaffold-tool p 0.23: still mixed) |
| P3.0 synthetic: G nominal FAR ≥ 0.04; Q LOPO FAR ≤ 0.03; count-step hit ≥ 0.8 | 0.136; 0.015; 0.02–0.38 | partly (power failed; Amendment R2-A1) |
| P3.1 NE39 alarms under Q; not under G | Q no (11.0 < 20.8); G no; amended D3 yes (4.5 > 2.76) | failed for Q; held for G; held on the amended channel |
| P3.2 G exceedance ≥ 0.05, Q ≤ 0.04; Q threshold ≤ 10 | 0.085; 0.073; 20.8 | partly |
| P3.3 NE43a and NE43b alarm (Q) | Q: NE43b only; amended: both | partly; held on the amended channel |
| **R3 kill rule** (NE39 alarms at D FAR ≤ 0.03) | amended channel: yes at 1/82; pre-registered Q: no | **supported on the amended channel** (amendment before real data); failed for Q |
| P2.0 synthetic: hit ≥ 0.8, FAR ≤ 0.02 | one-day rule 0.70, 0.049; accumulating rule 0.71 (0.87 within 5 days), 0.017 | failed; held for FAR after the amendment |
| P2.1 NE40 alarm within ±1 day | accumulating: 2 days late; one-day and appearance: on the day | mixed |
| P2.2 03-31 outage alarms · P2.3 FAR ≤ 0.03 and ≤ 10 alarm days · P2.4 NE45 silent | no · 0/37 and 2 · silent (one-day rule fires) | failed · held · held |
| **R2 kill rule** (NE40 alarmed, FAR ≤ 0.05) | alarmed (2 days late), 0/37 | **passes** (recovery, not blind) |
| P4.1 ≤ 1 of 25 DiD tests survives Holm · P4.2 | 0 of 25; leads are infra errors | held as counted, but **unpowered** (minimum p 0.031) |

**Old → new.**

| Quantity | Round 1 | Round 2 |
| --- | --- | --- |
| fused per-day FAR | 0.18 (34 days, in-sample τ) | monitor 0.085 [0.04, 0.17] out-of-sample on 82 days (0.051 post hoc catalog) |
| schema diff S | 0/34 placebo alarms | 2/82 on the wider pool, both provider format changes found in round 1; 0/78 once they are catalogued |
| drive steps (NE39, NE43a, NE43b) | NE43a/b dated, NE39 missed (raw z) | all three dated by D3 at FAR 1/82 |
| NE40 oracle swap | missed (O channel) | dated on the day (one-day retirement and appearance rules) or 2 days late (accumulating rule), 0–1/37 FAR |
| scaffold tool changes | hit 0.78 at 30% alarm days (chance 0.60) | 0.35 at chance 0.34; not detectable at FAR ≤ 0.1 |
| goal kickoffs | C AUC 0.89 | C3 in the monitor: hit 0.57, p 0.003 |

**Scorecard after round 2.**
- A 1 (unchanged).
- **B 1 → 2**: Gaussian thresholds are replaced by distribution-free conformal thresholds, calibrated leave-one-period-out; the joint-silence tail is named.
- C 1: the monitor beats random dates for goals (p 0.003) and rooms, D3 for undocumented drive steps (p 0.034), but not for scaffold changes.
- D 1 (channel specificity holds: S for formats, D3 for drive, C3 for goals).
- E 1: NE39 and NE43a/b dated; NE14 only through C3; NE45 and NE40 only with post hoc catalog or a late or secondary rule.
- **F 1 → 2**: synthetic worlds on the real skeleton with bootstrapped real tails reproduce the round-1 FAR failure, show the pre-registered D was unpowered, and predict the real OOS FAR (0.013–0.015 synthetic vs 0.012 real per channel).
- G 2.
- H 1: beats round 1's fused alarm at matched FAR (which has no operating point) and C3 alone on pooled platform hits (+0.16); loses nothing on goals.
- I 1 (reserved data not run).

**Faithfulness lever.** B and F: out-of-sample calibration replaced in-sample Gaussian thresholds, and the synthetic study reproduced the real failure before the real run.

### Operator rule (one page)
**Purpose.** Tell an operator, the day after, that the platform, the drive or the goal changed, at about one false alarm per 12–20 quiet days.

| Channel | What it reads (per active day) | Score | Alarm | Out-of-sample per-day FAR | What it catches |
| --- | --- | --- | --- | --- | --- |
| **S, schema diff** | field names and JSON types of every log record (`infra/shared/schema_diff.py`) | platform-wide new or retired signatures (≥ 2 agents; newcomers' first 3 days excluded) | ≥ 1 change. Report provider-envelope signatures (`turn_api`) as a separate "provider" alert | 0/78 (Wilson upper 0.047) with provider changes catalogued; 2/82 if they are not | tool-schema and record-format changes to the day, with the fields named; provider API format changes. Scaffold tool hit 0.26 |
| **D3, operator counters** | daily counts of pause/resume bookends, nudges, human messages | log1p count; robust trailing z (10 days, trimmed SD / 0.70, floor 0.1); persistence p(t) = min(\|z(t−1)\|, \|z(t)\|); max over the three | p > 2.8 | 1/82 = 0.012 [0.002, 0.066] | operator wind-downs and chat closure (NE39, NE43a, NE43b; undocumented class 3/6, p 0.034); one day of delay |
| **C3, topic shift** (H36) | agent-day embedding centroids, bge-small, restatements removed | R1 trailing z and Z_cont (≥ 100 surrogates) | R1 ≥ 3 or Z_cont ≥ 2 | 5/82 = 0.061 [0.026, 0.135] (0.049–0.061 over 9 seeds) | goal kickoffs (0.51 alone; 0.57 in the monitor, p 0.003), room changes |
| *add-on:* format presence | per search answer: bullet styles, headers, dashes, opening class | first-absence evidence (beta-binomial, ρ = 0.07) and appearance | Σ log P(0) ≤ log 10⁻³, or a marker on ≤ 2 of 10 days appears in ≥ 3 answers from ≥ 2 agents | 0/37 | answer-model swaps (NE40) on the day (appearance) or 2 days late (retirement) |
| *flag only:* stall | joint silence, window length, documented hours | empirical-quantile exceedance (30 days) | \|e\| ≥ 4 | 4/82 (not counted) | stall and outage days (03-31, 01-07/08, 07-07, 07-28) |

- **Expected performance (S ∪ D3 ∪ C3):** per-day FAR 0.05–0.085 on quiet days; drive changes 4/7 to 7/7; goal kickoffs 0.57–0.71; room changes 6/6; undocumented steps 3–5 of 6.
- **What it cannot do:** scaffold-tool changes are hit at chance (0.35 vs 0.34); prompt-only changes are invisible (0.24). Behavioral mixes vary by ~28 SD over multinomial day to day (H36), so no action-mix channel reaches FAR 0.02.
- **Calibration:** recalibrate each threshold as the maximum of the channel's score on your own quiet days (≥ 50 days ≥ 2 days from any known change; conformal rank ⌈0.98(n + 1)⌉). Catalog provider format changes before calibrating S, or they set its threshold.

### Round 3 redirects
- **H74-R5 (unchanged).** Run `confirm.py` on the reserved data after sign-off. Re-freeze it first on the round-2 monitor (S at ≥ 1 change with provider dates catalogued, D3 at 2.8, C3 frozen) and on the presence rules.
- **H74-R6. Split S into platform and provider streams.** Provider-envelope signatures change with the model vendor, not the village; alert on them separately.
- **H74-R7. Scaffold changes need a new observable.** Neither schema, counters, topic nor action mix sees them beyond chance. Candidates: M with quantile baselines (post hoc lead, p 0.016), bash-grammar presence (H36-R7).
- **H74-R8. Powered provider DiD.** Use agent-day block permutations instead of ~30 null windows, so that Holm over the tests can reject; test the infrastructure-error lead first.

**Claim that stands:** On 282 non-reserved days, a three-channel monitor with leave-one-period-out thresholds (schema diff ∪ log-count operator counters with two-day persistence ∪ H36's topic rule) has an out-of-sample per-day FAR of 0.085 [0.04, 0.17] and hits goal kickoffs at 0.57 (p 0.003) and room changes at 6/6; its counter channel alone dates all three undocumented drive steps (NE39, NE43a, NE43b) at FAR 1/82. *Exclusions:* the post hoc catalog completion (FAR 0.051, drive 7/7); the NE40 presence recovery (not blind, 2 days late under the primary rule); the M-channel scaffold lead; R4 (unpowered); scaffold-tool hits are at chance (0.35 vs 0.34).

## Notes
- 2026-10-04 19:25 UTC: card written before any detector score (see disclosure).
- ~19:40–20:25: synthetic study (3 passes; generator drift bug and floor design fixed; Amendment 1).
- ~20:30: native predictions written in NE14, NE40, NE43, NE45 before the real-data run.
- ~20:40–21:10: scan (4 min, 2 processes), build, detector, natives, period folders, estimates, confirm dry run. A start-time Int8 overflow in `build.py` was fixed and rerun; results unchanged to 2 decimals.
- Compute and disk: local, ≤ 2 processes; ≈ 10 CPU-min; `data/processed/H74-change-detector/` ≈ 3 MB. No text stored (field names and type names only).
- **Data findings for the shared catalog** (not edited): undocumented provider API response-format changes on 2025-12-19 (Gemini: `responseId`, `sdkHttpResponse` added), 2026-02-09 (Anthropic usage subfields), 2026-04-01 (Anthropic `stop_details` added), 2026-05-06 (Gemini `usageMetadata` subfields), 2026-07-13/14 (OpenAI response items: `phase`, `encrypted_content`); the first SEARCH_HISTORY event in the (non-holdout, unbroken) record is on 2025-09-19, two weeks after NE04's 09-05 date, the same day as a CHANGELOG tool entry: either the tool deployed later than NE04 says or it went unused; a field-less variant appears once on 2026-02-19 and the `roomId` field is added on 2026-03-16; stall days flagged by joint silence on 2025-07-25, 2025-10-16, 2026-01-07/08, 2026-07-28.
- **Proposed shared-file changes** (not made): DEFINITIONS.md named variants *record signature* and *synchronous within-agent shift*; a shared `infra/shared/` schema-diff builder (scan_signatures logic) with `--verify`, since it is the cheapest platform monitor found so far; infra Known issue: H56's `event_catalog.parquet` is now an input to H74 and should move to `infra/shared/`.
