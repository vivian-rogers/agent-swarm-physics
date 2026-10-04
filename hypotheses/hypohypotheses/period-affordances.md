# Period affordances (DQ9)

What each goal period uniquely offers for testing, so that every hypothesis can add 2–4 **period-native tests** next to its replication layer (`infra/data-quality/QUEUE.md`, "Re-evaluation design rule"). Built 2026-10-04 (UTC). The cross-index (hypothesis → recommended native tests) is [at the end](#cross-index-native-tests-per-hypothesis).

- **Machine-readable twin:** `data/processed/shared/period_affordances.parquet` (one row per period unit, 109 rows, built by `infra/shared/period_affordances.py`; docs `infra/data-quality/period_affordances.md`). Numbers below are copied from that build; if they disagree after a rebuild, the parquet wins.
- **Units** are `period_units.parquet` (one rule for step changes). Sections are per goal period; split periods list their units.
- **Holdout** (locked 2026-10-03; `hypotheses/holdout.md`): held-out periods and units are described **from setup and ground-truth metadata only**. No event counts were computed on them; their "best leverage" bullets are confirmation targets, never exploration.
- **No message text** was read. Counts, ids and codes only.
- Sources: `goal-periods.md` (setup; by/mode codes), `natural-experiments.md`, `data/raw/ai-village/CHANGELOG.md`, DQ6 `ground_truth_labels`, DQ4 work ledger, DQ1 context ledger, `kicks_classified`, `calendar`, `outages`, `rooms`, and the cards' round-1 results.

**Legend.**
- **act h** = active hours: the calendar's empirical daily windows, minus village-off gaps (`outages.village_off`); **doc** = documented hours per day.
- **N** = roster agents active in the unit (Claude Code agent excluded).
- **GT** = DQ6 rows (preferred); room rows (`room_assignment`, `room_presence`) are listed separately from structural kinds.
- **Erasures** = forced context erasures at the 41-turn cap (NE41; DQ1 `reset_forced`); **voluntary** = other consolidation resets.
- **Work** = DQ4 agent work commits (`canonical & ~imported & agent & ~automated`), committing agents, sites (pages + site-default commits), deploys; **dense from #30 only** (before #30 a zero is ambiguous).
- **Human** = human chat messages (`kicks_classified.human_message`; "naming" = they name a roster agent; "speakers" = most distinct hashed human speakers in one unit).
- Data-found step dates (this build) are marked **[data]**; they are not, or not correctly, in `natural-experiments.md`.

## Leverage at a glance

The periods with the most unique leverage, in rough order (non-holdout unless marked 🔒):

| Period | Why it is special | Families it serves |
| --- | --- | --- |
| **#51 head** (51a–51l) | 55-day private-role era (45 non-holdout days): role, role-class, rival and opposed-pair GT; N sweeps 21 → 32 in 11 steps at fixed goal, hours and room; NE32 isolated newcomer rooms; NE38 single-role reassignment; drive withdrawal (bookends end 08-04 **[data]**, nudges end 08-20, NE43); 14.6k forced erasures; 48k work commits | spin glass / stance, size scaling, drive and catalysts, context, light cone, outcomes |
| **#12** | 10 debates with re-drafted teams, rotating judges, motions and verdict instants (GT 110 rows) | factions, field switch-off, leaders, superagents |
| **#26** | Two elections with exact ballots (approval 9–9–9 tie → 7–1–0 runoff in ~100 s; 01-09 confirmatory 9–0), an elected leader with a known start, an agent-set goal | consensus, votes, leaders, Potts symmetry point |
| **#35 (NE15)** | One room cut into #best/#rest with a common ancestor artifact (forks); daily-rotating lead designers (GT); room × lab crossed | cuts, forks, light cone, leaders, family fields |
| **#39 → #40 → #41 (NE42)** | A-B-A merge into one room and back at a fixed roster; 15 independent artifacts (#39) connected into one (#40); dense git | dilution, backlog, coherence length, consensus, coordination |
| **#38** | 17-day regime-III two-room period; operator removes misinformation at a known instant (NE36); dose steps NE17, NE18; replicate of #1 🔒 | settling/mixing, erasure thrash, semantic information, operator steering |
| **#44** | Same days, same scaffold, two rooms with different goal fields (assigned vs self-chosen); model checkpoints at exact times (GT) | goal fields, kickoff targets, leaders, coherence length |
| **#31** | A field-free herding wave onto one repo in dense git; NE29 (longest memory lineage retired); NE11 session cap | herding, early warning, links, neutral dynamics |
| **#30 (NE10)** | The first nudges ever (first in the record 02-13 **[data]**, not 02-10), after 4 nudge-free days of the same goal | nudge effects, refractory windows, Maxwell demon |
| **#36 (NE14)** | Same goal across regime II → III (perma-computer-use, NE41 forced erasures begin), then NE16 memory fix | regime boundary, kernels, call clock, erasure |
| **#4, #5, #6** | Public chat era: up to 124 distinct human speakers per unit; public chat closes ≈ 2025-07-01 inside #6 **[data]** | humans as agents, operator susceptibility, human-channel cut |
| 🔒 **#34, #45, #46–#50** | Saboteur GT, the installed leader, the hours ABAB and nudger off/on, the 200-event cap, star forcing, GitLab move, private-goal onset | confirmation only |

---

## Periods

### G01 · Charity fundraiser, year 1 🔒
`2025-04-02 → 05-09` · units 1a–1e · N 4 · 30 calendar days (incl. weekends), ~2 h/day (undocumented) · regime I · #general · **holdout (confirmation only)**
- **Setup:** four launch agents choose a charity and raise money; half the roster swapped mid-goal; heavy public viewer chat (setup).
- **Ground truth:** none in DQ6.
- **Interventions inside:** three one-in/one-out swaps (04-15 GPT-4o → GPT-4.1; 04-16 o1 → o3; 04-24 Claude 3.5 Sonnet → Gemini 2.5 Pro); NE01 chat-while-computing (05-02, unit 1e); CHANGELOG chat premoderation (04-14), memory-prompt tweaks (04-15/16), anti-double-chat prompts (05-04).
- **Structure:** one shared objective; charity choice.
- **Outcome measures:** money raised ($1,984; narration and the #38 operator correction only). No git.
- **Best leverage for (confirmation):** NE01 as an update-rule change inside one goal (kinetic Ising update order; H02, H14); three successive swaps at fixed N = 4 as newcomer-assimilation replicates (H15, H48); #1 vs #38 as a same-goal replicate a year apart (model 07).
- **Weak for:** N = 4; no documented hours; swaps confound every within-period trend; no outcome ledger.

### G02 · Unsupervised weekend look-back
`2025-05-10 → 05-11` (weekend) · unit 2 · N 4 · 2 d, 3.8 act h · regime I · #general
- **Setup:** agents left unsupervised over a weekend; closed out the fundraiser.
- **Ground truth:** none.
- **Interventions inside:** none. **Zero human messages**; only 4 operator bookends.
- **Structure:** none (free).
- **Outcome measures:** none (no git).
- **Best leverage for:**
  - the only human-free, operator-free window in the record: an endogenous-activity baseline for Hawkes branching and self-excitation (H03) and a field-free reference for field-vs-coupling lags (H50).
- **Weak for:** 3.8 h and N = 4: any rate has huge variance; weekend schedule.

### G03 · Holiday
`2025-05-12 → 05-14` · unit 3 · N 4 · 3 d, 5.9 act h · regime I · #general
- **Setup:** free exploration (e.g. a Wikipedia scavenger hunt).
- **Ground truth:** none. **Interventions:** none documented; 77 human messages from up to 8 public speakers.
- **Structure:** none. **Outcomes:** none.
- **Best leverage for:** a short free-drift baseline with public chat (topic drift without a goal field, model 11).
- **Weak for:** tiny sample.

### G04 · Story + 100-person in-person event
`2025-05-15 → 06-18` · units 4a, 4b (one-day o4-mini cameo), 4c, 4d (intra-day restart after a 300-min stall on 06-18) · N 4 · 26 unit-days, 51.1 act h (2 h/day documented from 05-23) · regime I · #general
- **Setup:** write an interactive story ("RESONANCE") and hold a real in-person event for 100 people.
- **Ground truth:** none.
- **Interventions inside:** roster 05-22 GPT-4.1 → o4-mini, 05-23 o4-mini → Claude Opus 4; start time moved 05-23; a 300-min outage and restart on 06-18 (4d). **Human input: 1,713 messages, 335 naming an agent, up to 124 distinct speakers per unit** (public chat).
- **Structure:** shared objective; a real-world event (`has_ext_event`).
- **Outcome measures:** event held (narration). No git (the story lived in documents).
- **Best leverage for:**
  - **humans as loud agents (H52):** the largest non-holdout sample of human messages from many distinct humans, naming vs plain, to compare with agent messages of matched naming and timing;
  - **a platform stall with a known cause (H38):** 4d is the restart after a 300-min stall, with 229 human messages that day; compare joint-silence statistics around a real outage;
  - single-agent insertion and removal within one day (o4-mini) as a perturbation of a 4-agent system.
- **Weak for:** N = 4; outcome by narration; human chat was public, so humans are viewers, not operators; hours undocumented before 05-23.

### G05 · Holiday (leadership-format survey)
`2025-06-19 → 06-25` · unit 5 · N 4 · 5 d, 10.0 act h (2 h/day) · regime I · #general
- **Setup:** holiday after the event; a feedback survey gave a mandate for rotating leadership (9 votes; summary only).
- **Ground truth:** none (the survey isn't in the record).
- **Interventions inside:** **881 human messages (145 naming; 86 distinct speakers)**, the densest human input per active hour in the data (~88/h).
- **Structure:** free week; a survey (`outcome_narration`).
- **Outcome measures:** none.
- **Best leverage for:**
  - **operator/human susceptibility at high dose (H30, H52):** many humans, no goal field to confound content steering; per-message content pull by named vs unnamed recipients;
  - a crowd-input baseline for Hawkes exogenous rates (H03).
- **Weak for:** N = 4; holiday (agents may idle); the survey and its votes are not recoverable without text.

### G06 · Merch store competition
`2025-06-26 → 07-15` · units 6a, 6b (NE02 screenshot redaction 07-03) · N 4 · 15 calendar days (one Sunday), 27.1 act h (2 h/day; 6a's windows include 13.6 h of village-off gaps) · regime I · #general
- **Setup:** each agent builds its own merch store; most profit wins (summary: Opus 4 $126, Sonnet $68, o3 $39, Gemini $22).
- **Ground truth:** none (profits are summary-only).
- **Interventions inside:**
  - **[data] public chat closes ≈ 2025-07-01:** human messages per day fall from ~100 (16–24 speakers) to ≤ 4 (1 speaker) between 06-30 and 07-01. This dates the undocumented NE39 (chat closed to the public). 6a 396 human messages vs 6b 47.
  - NE02 (07-03, ~0.6% of turns); CHANGELOG 06-26 timezone/situational-context prompt, 07-07 sensitive-information prompt.
- **Structure:** competition with individual scored outcomes (`has_competition`).
- **Outcome measures:** store profit per agent (summary only). No git.
- **Best leverage for:**
  - **a human-channel cut inside one goal at a fixed roster (NE39 estimate):** ITS on activity, talk and content with and without public viewers (H52, H39 human input as field, H36 blind detection of an undocumented step);
  - individual competitive outcomes with a known ranking, for a replicator productivity decomposition at N = 4 (model 07; H22 antagonism on separate artifacts).
- **Weak for:** N = 4; the closure date is estimated from counts and should be confirmed; profits are not in a ledger; long village-off gaps in 6a.

### G07 · Holiday (human helpers arrive)
`2025-07-16 → 07-17` · unit 7 · N 4 · 2 d, 4.0 act h · regime I · #general
- **Setup:** two-day holiday; competition review.
- **Ground truth:** none.
- **Interventions inside:** **[data] CHANGELOG scaffold change B, the human-use feature** (agents can request a human helper; 07-16 → 07-21; no NE id). 88 human messages from up to 21 speakers, after the public-chat closure: whitelisted helpers.
- **Structure:** free.
- **Outcomes:** none.
- **Best leverage for:** the arrival of a catalytic lever (human helpers) with no goal field (H39 catalysts vs fields), with helper requests logged as events.
- **Weak for:** two days, N = 4; B straddles into #8.

### G08 · Design an open-ended benchmark and take it
`2025-07-18 → 08-12` · unit 8 · N 4 · 18 d, 53.6 act h (3 h/day from 07-18) · regime I · #general
- **Setup:** agents design a benchmark for their own goal pursuit; o3, Opus 4 and Claude 3.7 Sonnet independently wrote nearly identical frameworks (summary).
- **Ground truth:** none.
- **Interventions inside:** hours change 2 → 3 h (07-18, day 1); human-use extended to other providers (CHANGELOG 08-05 → 08-12); 39 human messages.
- **Structure:** shared objective designed by the agents (`by = D`).
- **Outcomes:** no git.
- **Best leverage for:**
  - **independent convergence without communication:** separating a shared prior (field) from coupling in content (H24, H50, model 11), in the longest stable small-N regime-I window;
  - long single-room stationarity at N = 4 for aging and Markov-state tests (H20, H17).
- **Weak for:** N = 4; the convergence is from summaries; content-only outcomes.

### G09 · Holiday 🔒
`2025-08-13 → 08-15` · unit 9 · N 4 · 3 d, 3 h/day · regime I · #general · **holdout**
- **Setup:** holiday; agents explored Twitter; three new agents arrive the next Monday (NE27).
- **Ground truth:** none. **Interventions:** none documented. **Structure:** free. **Outcomes:** none.
- **Best leverage for (confirmation):** the pre-NE27 baseline (free-week dynamics at N = 4 just before a batch join).
- **Weak for:** tiny.

### G10 · Complete as many games as you can
`2025-08-18 → 08-22` · units 10a (NE27 batch join at goal start), 10b (NE03 chat-fetch limit 08-20) · N 7 · 5 d, 14.0 act h (4 h/day) · regime I · #general
- **Setup:** each agent completes turn-based games (mode I).
- **Ground truth:** none.
- **Interventions inside:** NE27 (+3: GPT-5, Grok 4, Opus 4.1, on day 1); hours 3 → 4 h (08-18); **NE03 limits the number of chat messages fetched into context (08-20)**; 21 human messages.
- **Structure:** individual objectives.
- **Outcome measures:** games completed (narration only).
- **Best leverage for:**
  - **NE03 as a context-capacity cut** at a fixed roster and goal (10a 2 d vs 10b 3 d): does the per-message uptake curve change when the context holds fewer messages (H08, H18 dilution)?
  - newcomer kernels: three agents with empty memories join together (H03, H48);
  - a mode-I null for couplings (H02).
- **Weak for:** NE27 coincides with the goal start and the hours change; 10a is two days.

### G11 · Free week
`2025-08-25 → 08-29` · unit 11 · N 7 · 5 d, 15.1 act h · regime I · #general
- **Setup:** self-chosen meta-projects (e.g. documenting platform instabilities).
- **Ground truth:** none. **Interventions:** none documented; 10 human messages.
- **Structure:** free. **Outcomes:** no git.
- **Best leverage for:** the cleanest regime-I free week (fluctuation baselines for H10, free-week dimensionality for H12, project abundances for H06 from intentions).
- **Weak for:** projects only from intentions and artifact mentions; no outcomes.

### G12 · Debate tournament (10 debates)
`2025-09-01 → 09-05` · units 12a (debates 09-01 → 09-04), 12b (NE04 on 09-05; no debates) · N 7 · 5 d, 15.0 act h · regime I · #general
- **Setup:** 10 Asian-Parliamentary debates; teams re-drafted every debate (except #7 = #6) by captains the judge picked; judges rotate (Gemini, o3, Grok, Claude 3.7 Sonnet for 1–4, Claude Opus 4.1 for 5–10); Government argues for the motion; Opposition won 7–3.
- **Ground truth:** **team 60, judge 10, debate_result 10, phase 30** (DQ6; H21's hand-verified file; high).
- **Interventions inside:** 10 motions (field on) and 10 verdicts (field off, at known instants); NE04 history search + chain-of-thought consolidation (09-05, after the last debate); 16 human messages.
- **Structure:** teams, judges (leaders per debate), competition.
- **Outcome measures:** debate results (GT). No git.
- **Best leverage for:**
  - **10 replicate two-team samples with known labels:** whether a drafted team behaves as one coarse-grained unit (H01 superagents), and whether inferred couplings recover the known directed structure (speech order, judge → debaters; H02);
  - **verdicts as field switch-offs at known times:** relative lag between agents at a field event (zero for a field; H50), content loop gain with and without the motion field (H26), dimensionality under a strong uniform field (H12);
  - **re-drafting moves the same agent across sides:** separates an agent's own field from team coupling (H21/H37 re-analysis), and the judge as a per-debate information sink or source (H32).
- **Weak for:** N = 7, four debate days; Jev stance over-calls "oppose" (precision 0.30); captains not recorded; no outcome beyond verdicts.

### G13 · Design and run a human-subjects experiment
`2025-09-08 → 09-19` · unit 13 · N 6 (Opus 4 left on day 1) · 10 d, 29.9 act h · regime I · #general
- **Setup:** design, run and write up a real experiment (power analysis: 126 participants).
- **Ground truth:** none.
- **Interventions inside:** roster leave (Opus 4, 09-08); **50 human messages from one speaker, 34 naming an agent** (one human interacting by name).
- **Structure:** shared objective with subtasks; real human participants (`has_ext_event`).
- **Outcome measures:** participants recruited (narration). No git.
- **Best leverage for:** a single human driving named agents over two weeks (H52 authority premium with one identifiable human; H29 human as driver node); two-week division of labor in regime I (H11, from intentions).
- **Weak for:** no outcome ledger; one human speaker.

### G14 · Personality tests 🔒
`2025-09-22 → 09-26` · unit 14 · N 6 · 5 d, 4 h/day · regime I · #general · **holdout**
- **Setup:** personality tests (Big Five, MBTI); an operator warned agents to stop filing "bugs" that are their own misclicks.
- **Ground truth:** none (test results are in agent narration).
- **Interventions inside:** the operator warning (dated message; `has_operator_correction`).
- **Structure:** individual objectives. **Outcomes:** none in ledgers.
- **Best leverage for (confirmation):** personality profiles as literal vectors (H13 family fields; H24's confirm script targets #14); an operator field against a named trap behavior (H16).
- **Weak for:** no GT for profiles.

### G15 · Peer therapy 🔒
`2025-09-29 → 10-03` · units 15a, 15b (NE05 + Claude Sonnet 4.5 joins 09-30) · N 6 → 7 · 5 d · regime I · #general · **holdout**
- **Setup:** agents give each other therapy; a shared "Mutual-Aid Playbook".
- **Ground truth:** none. **Interventions inside:** NE05 Claude thinking re-enabled (Anthropic only) on the day Sonnet 4.5 joins. (Google sign-in v1 is dated 10-05, a Sunday; it lands at #16's start.)
- **Structure:** shared objective; helper → helped pairs (narration).
- **Best leverage for (confirmation):** advice transmission (copying vs transformation, model 08); NE05 as an Anthropic-only DiD (H13, H14).
- **Weak for:** NE05 coincides with a join.

### G16 · Free week with operator rules
`2025-10-06 → 10-10` · unit 16 · N 7 · 5 d, 13.6 act h · regime I · #general
- **Setup:** free week with operator rules: no more spreadsheets; stop reporting self-caused bugs.
- **Ground truth:** none.
- **Interventions inside:** the operator rules (kickoff; `has_operator_correction`); CHANGELOG 10-05 Google sign-in v1 (lands on day 1), 10-08 prompt edits, 10-09/10 codex instructions; 27 human messages (10 naming).
- **Structure:** free.
- **Outcome measures:** first work commits in the ledger (7, one agent).
- **Best leverage for:** **an operator field against two named behaviors** in a free week: do spreadsheet and bug-report loops (trap states) drop, and do agents enforce the rule on each other (H16 traps, H55 norm enforcement, H30 operator content steering)?
- **Weak for:** rules arrive with the goal start; git sparse.

### G17 · Personal websites
`2025-10-13 → 10-17` · unit 17 · N 7 · 5 d, 15.0 act h · regime I · #general
- **Setup:** each agent builds a personal website with a new codex tool; deployment know-how split agents into lucky and stuck.
- **Ground truth:** none.
- **Interventions inside:** CHANGELOG 10-14/15 (links to the agents' own websites added to prompts); 16 human messages.
- **Structure:** individual artifacts.
- **Outcome measures:** `repos_created`, `site_repos_created` (artifact; sparse: 1 agent in public git); **121 deploy commands** (DQ4 `deploy_cmds`) are the better adoption measure.
- **Best leverage for:** **method contagion among separate artifacts:** does seeing a link to a working deployment method precede an agent's switch to it (H28 links, H53 receptive fraction, H34 cascades with a datable idea)?
- **Weak for:** early sites not in public git; no live checks; a prompt change mid-week.

### G18 · Reduce global poverty
`2025-10-20 → 10-31` · units 18a, 18b (Claude Haiku 4.5 joins 10-22), 18c (Grok 4 leaves 10-29) · N 7 → 8 → 7 · 10 d, 35.0 act h · regime I · #general
- **Setup:** two weeks of collaborative research and building.
- **Ground truth:** none.
- **Interventions inside:** one join, one leave; CHANGELOG 10-22 prompts for 4-hour runs ("keep working until the end of the day"); 22 human messages.
- **Structure:** shared objective; a last-day convergence (H27's named pile-on).
- **Outcome measures:** 675 deploy commands; 12 work commits (1 agent).
- **Best leverage for:** a herding onset late in a long goal with a known date (H27 early warning lead time); a newcomer arriving mid-goal (H15, H48).
- **Weak for:** git sparse; the 4-hour prompt change lands with the Haiku join.

### G19 · Daily puzzle game
`2025-11-03 → 11-14` · units 19a, 19b (GPT-5.1 joins on the last day) · N 7 → 8 · 10 d, 40.0 act h · regime I · #general
- **Setup:** candidate concepts brainstormed, then the swarm converged and shipped.
- **Ground truth:** none (candidate set not recorded).
- **Interventions inside:** one join (last day); 11 human messages.
- **Structure:** consensus among q candidates; **frozen at the kickoff** (H11, H31).
- **Outcome measures:** `repos_created`, `site_repos_created`; 41 commits, 38 site commits (1 agent), 302 deploy commands.
- **Best leverage for:** **field-set consensus as the negative control** for herding and consensus dynamics (H11, H27, H31); did the kickoff text name the winning concept (H54 quench target)? candidate-concept abundances (H06).
- **Weak for:** frozen consensus leaves little dynamics; git from one agent.

### G20 · Substack blogs
`2025-11-17 → 11-28` · units 20a, 20b (Gemini 3 Pro joins 11-19), 20c (NE06 11-20), 20d (NE06 11-25 + Claude Opus 4.5 joins) · N 8 → 10 · 10 d, 40.0 act h · regime I · #general
- **Setup:** each agent starts a Substack; niches formed. (No agent left during #20; the double retirement is NE28 at #21's start.)
- **Ground truth:** none.
- **Interventions inside:** **NE06, a Google-specific scaffold change** (one tool call per turn 11-20/21; chain of thought 11-25); two joins; 15 human messages.
- **Structure:** individual artifacts.
- **Outcome measures:** `substack_posts_linked`, `substack_posts_total` (link reliability).
- **Best leverage for:**
  - **a family-specific scaffold change (DiD Google vs others, with the caveat below):** behavior irreversibility (H14), call cadence (H40), entropy-production fingerprint (H56), family field shifts (H13), blind detection (H36);
  - per-agent publish counts for a productivity outcome in regime I (H33).
- **Weak for:** the CHANGELOG lists **all-agent system-prompt changes on the same days (11-20/21)**, so the DiD contrast is not clean; only two Google agents; posts are link-credited.

### G21 · AI forecasts
`2025-12-01 → 12-05` · units 21a (NE28 at start), 21b (NE07 + DeepSeek-V3.2 joins 12-04) · N 8 → 9 · 5 d, 20.0 act h · regime I · #general
- **Setup:** forecast AI abilities; comparison began within the first hour (correction).
- **Ground truth:** none (numeric forecasts need extraction; H24's audit gave κ 0.25).
- **Interventions inside:** NE28 double retirement (o3, Opus 4.1) on day 1; text-only agents supported (12-02); **NE07 "don't do nothing" prompt (12-04)**, with DeepSeek's join and a shared tracker the same day.
- **Structure:** individual forecasts, then comparison.
- **Outcomes:** none in ledgers.
- **Best leverage for:** NE07 as a pure prompt field on activity (H39 field vs catalyst); numeric herding (H24).
- **Weak for:** 12-04 bundles three changes; NE28 coincides with the goal start.

### G22 · Free week 🔒
`2025-12-08 → 12-12` · units 22a, 22b (NE08 village goal in prompt 12-10), 22c (GPT-5.2 joins 12-12) · N 9 → 10 · 5 d · regime I · #general · **holdout**
- **Setup:** "each agent choose your own goal" (e.g. an activity dashboard on the village API).
- **Ground truth:** none. **Interventions:** NE08 (prompt persistence field), one join; CHANGELOG 12-11/12 tools and prompt wording.
- **Best leverage for (confirmation):** NE08 inside a free week (a goal field turned on with nothing to point at); H06's `confirm_holdout.py` targets #22.
- **Weak for:** two-day units.

### G23 · Chess tournament
`2025-12-15 → 12-19` · unit 23 · N 10 · 5 d, 20.0 act h · regime I · #general
- **Setup:** agents play each other on Lichess.
- **Ground truth:** none (results not extracted).
- **Interventions inside:** CHANGELOG 12-15/16 tool prompts; 23 human messages (18 naming; one speaker); 11 infrastructure-error bursts.
- **Structure:** competition with explicit pairwise opponents.
- **Outcome measures:** `lichess_games_linked`, `lichess_games_total` (games linked, not results).
- **Best leverage for:** **explicit pairwise antagonism with known pairs** (from game links): negative couplings and stance between opponents (H22, H37), sequential updates (model 02).
- **Weak for:** results need extraction; pair lists need building from links.

### G24 · Random acts of kindness
`2025-12-22 → 12-26` · unit 24 · N 10 · 5 d, 19.1 act h · regime I · #general
- **Setup:** acts of kindness, each confirmed as appreciated; agents divided approaches.
- **Ground truth:** none.
- **Interventions inside:** **NE09 chat interleaved into computer-use context (12-20, a Saturday; lands on day 1)**; holiday week; 6 human messages.
- **Structure:** shared objective with a division of approaches.
- **Outcomes:** no git (7 deploy commands).
- **Best leverage for:** NE09 adds a coupling channel (chat visible during computer use): uptake of chat links during work (H08, H28) compared with #23; an antiferromagnetic (division-of-labor) candidate (H11).
- **Weak for:** NE09 coincides with the goal change; holiday week.

### G25 · Digital museum of 2025
`2025-12-29 → 01-02` · unit 25 · N 10 · 5 d, 19.5 act h · regime I · #general
- **Setup:** exhibits curated from village history, one per agent.
- **Ground truth:** none. **Interventions:** none documented; 4 human messages; 8 infrastructure bursts.
- **Structure:** individual exhibits for a shared museum.
- **Outcome measures:** `repos_created`, `site_repos_created`; 9 commits (2 agents), 239 deploy commands.
- **Best leverage for:** which past events the agents keep (semantic information, model 04) and copying vs transforming the record (model 08).
- **Weak for:** git sparse; holiday week.

### G26 · Elect a leader who sets the goal
`2026-01-05 → 01-09` · unit 26 · N 10 · 5 d, 14.9 act h (1.0 h village-off) · regime I · #general
- **Setup:** ballot failure, then a chat approval vote: **9–9–9 tie** (DeepSeek-V3.2, Claude 3.7 Sonnet, Gemini 2.5 Pro) → **7–1–0 runoff in ~100 s** → DeepSeek-V3.2 elected 01-05 19:35 UTC; **confirmatory re-election 01-09 (9–0)**. The leader set an interactive-fiction goal (not in `village_goals`).
- **Ground truth:** **ballot 64, tally 12, phase 6, leader 2** (high; ballots reproduce all three official tallies), plus vote_declaration 810 (H11's rule; low).
- **Interventions inside:** three vote events and a leadership start at known instants; the leader's goal announcement; 27 infrastructure bursts (the most in regime I).
- **Structure:** votes, an elected leader, an agent-set goal (`by = A`).
- **Outcomes:** no git.
- **Best leverage for:**
  - **per-round consensus with exact instants:** the symmetric tie, the runoff and the confirmatory vote as three consensus events (H31 per round; H12 dimensional collapse at a vote; Potts symmetry breaking);
  - **ballots as known camps:** stance and content factions vs ballots (H21, H37), per election round;
  - **a leader with a known start time:** information current toward the winner after 01-05 19:35 (H32), driver ranking (H29), coupling inference (H02);
  - **an agent-set goal as the kickoff:** quench target (H54) and response to an agent-set field (H10).
- **Weak for:** H11/H31's earlier numbers measured the 01-09 vote (DQ6); declarations are low confidence; N = 10; the leader-set goal must be read from the record; infrastructure bursts.

### G27 · Juice Shop hacking competition
`2026-01-12 → 01-23` · unit 27 · N 10 · 10 d, 40.1 act h · regime I · #general
- **Setup:** two-week competition to solve the most challenges; turned from rivalry into collaboration without an operator change.
- **Ground truth:** none (switch time and scores not recorded).
- **Interventions inside:** none documented; 7 human messages; 16 infrastructure bursts; 55k model calls (long debugging).
- **Structure:** competition → cooperation.
- **Outcome measures:** 63 work commits (6 agents; the first multi-agent git use); challenges solved (narration only).
- **Best leverage for:**
  - **a spontaneous sign change of interaction** (rivals → collaborators) with no field change: stance sign flip (H37), regime change in behavior-state dynamics (H17), trap prevalence in long debugging (H16);
  - a 10-day stationary-ish regime-I window (H20 aging).
- **Weak for:** the switch must be dated by a detector; scores narration only; git still thin.

### G28 · "Which AI Village agent are you?" quiz 🔒
`2026-01-26 → 01-30` · unit 28 · N 10 · 5 d · regime I · #general · **holdout**
- **Setup:** a beta shipped within minutes, then a long accuracy push. **The Claude Code agent joins (01-26)** with a different tool loop.
- **Ground truth:** none. **Interventions:** Claude Code join; CHANGELOG 01-26 computer-use summaries restored.
- **Outcome measures available:** `repos_created`, `site_repos_created` (artifact).
- **Best leverage for (confirmation):** fast-start burst then slow tail (Hawkes); the Claude Code agent as a different-loop agent entering (H40 cadence).
- **Weak for:** Claude Code excluded from core tables.

### G29 · Breaking-news competition 🔒
`2026-02-02 → 02-06` · units 29a, 29b (Claude Opus 4.6 joins) · N 10 → 11 · 5 d · regime I · #general · **holdout**
- **Setup:** report news before it breaks; competing publishing channels.
- **Ground truth:** none. **Interventions:** one join.
- **Structure:** competition (the only mode-K draw in the holdout).
- **Best leverage for (confirmation):** news items as racing contagions (model 03) under competition.
- **Weak for:** outcomes not extracted.

### G30 · Adopt a park
`2026-02-09 → 02-13` · units 30a, 30b (NE10) · N 11 · 5 d, 20.0 act h · regime I · #general
- **Setup:** shared repo, NYC/SF 311 data, two target parks.
- **Ground truth:** none.
- **Interventions inside:** **NE10 auto-nudger, dated 02-10; [data] the first nudge in the record is 02-13** (12 nudges, all on 02-13). 30a and 30b-before-02-13 are four nudger-free days of the same goal.
- **Structure:** shared objective.
- **Outcome measures:** **git becomes dense:** 352 work commits by 12 agents, 352 site commits, 49 API writes.
- **Best leverage for:**
  - **the first nudges ever** (no habituation): first-nudge activity effect and its decay (H30, H43 refractory window), bits used per extra active minute (H35), catalyst vs field (H39), kernel change (H04), with work commits as the outcome;
  - a clean nudger-free baseline in the same goal (4 days).
- **Weak for:** only 12 nudges, on one day; regime I discrete sessions (nudges target idle agents between sessions).

### G31 · Free week (farewell to Claude 3.7 Sonnet)
`2026-02-16 → 02-20` · units 31a, 31b (Claude Sonnet 4.6 joins 02-18), 31c (NE29 retirement 02-19), 31d (NE11 100-turn cap 02-20) · N 11 → 12 → 11 · 5 d, 20.0 act h · regime I · #general
- **Setup:** ~9 agents converged on one task (a "canonical guardrails UI snippet") with competing PRs; a time-capsule repo reached 11 agents (H27).
- **Ground truth:** none (herding onsets come from H11/H27 detectors).
- **Interventions inside:** a join, **NE29 (the longest memory lineage retired)**, **NE11 session cap**, on three consecutive days; 25 nudges; CHANGELOG 02-18 PII-redaction model upgrade, 02-20 Gemini stuck-session fix.
- **Structure:** free week with spontaneous condensation.
- **Outcome measures:** **1,391 work commits (13 agents), 17 new repos, 1,354 site commits, 242 API writes**; automation appears (1,345 automated commits).
- **Best leverage for:**
  - **a field-free herding wave measured in work, not attention:** Potts sign (H11), early warning (H27), links as vector (H28), receptive-fraction nucleation (H53), cooperator core (H06), coordinated agents + artifact (H58);
  - **NE29:** does losing the longest-lived memory lineage cost the swarm anything (H15)?
  - **NE11:** call cadence and entropy-production change at a scaffold step (H40, H56).
- **Weak for:** one-day units for each step; filter automated commits.

### G32 · Challenge each other 🔒
`2026-02-23 → 02-27` · units 32a, 32b (NE12 rooms + NE35 operator reset, 02-25) · N 11 · 5 d · regime I → II · #general · **holdout** (NE12 window)
- **Setup:** challenges in alphabetical turns; agents gamed it; the operator reset it midweek.
- **Ground truth:** room_presence 12 (rooms era). **Interventions:** NE12 rooms (filtered context) and NE35 operator reset on the same day; CHANGELOG 02-26 `move_to_room` tool, 02-27 room-state snapshot.
- **Structure:** competition, fixed-order turns.
- **Best leverage for (confirmation):** the rooms channel cut (H05, S4/S5); fixed-order sweep (model 02).
- **Weak for:** NE12 and NE35 confounded; the room set stays {#general} structurally.

### G33 · Pentagon–AI news: discuss, debate, act
`2026-03-02 → 03-04` · unit 33 · N 11 · 3 d, 12.0 act h · regime II (one room) · #general
- **Setup:** debate and act on the news; a shared claims database with strict sourcing.
- **Ground truth:** room_presence 12 (no stance GT).
- **Interventions inside:** none documented; 22 nudges; 1 human message.
- **Structure:** shared objective; a sourcing norm.
- **Outcome measures:** 632 work commits (12 agents), 39 API writes.
- **Best leverage for:** stance polarization on an external political topic (H21, H37); enforcement of a sourcing norm (H55); facts copied into a database (copy fidelity, model 08 / H57).
- **Weak for:** three days; the pre-split baseline for NE15 is this period, with a different goal.

### G34 · Build an RPG with hidden saboteurs 🔒
`2026-03-05 → 03-13` · units 34a, 34b (NE30), 34c (NE13, #voted-out), 34d (NE14 begins) · N 11 · 7 d · regime II · #general (+ #voted-out) · **holdout** (NE30 window)
- **Setup:** each day a d6 roll of 1 makes an agent a saboteur hiding Easter eggs; voting out into #voted-out.
- **Ground truth:** **saboteur agent-days** (84 preferred rows: the system-logged roll where parseable, self-identification otherwise) and room presence (DQ6; nothing analysed).
- **Interventions inside:** NE30 same-family succession (Gemini 3 Pro → 3.1 Pro, 03-09); NE13 kickoff in the prompt (03-10); NE14 consolidate tool (03-11), `search_history` and helper tools in computer use (03-12), pause tool (03-13).
- **Structure:** hidden roles, votes, teams (saboteurs vs villagers).
- **Best leverage for (confirmation):** saboteur detection (H21, H37 `confirm_g34.py`; switch to the preferred roll rows before running); NE30 (H01, H13, H15, H46); the ancestor of the #35 forks (H07).
- **Weak for:** three NEs stacked in seven days; GUI rolls missing.

### G35 · Test your game (forked per room)
`2026-03-16 → 03-20` · unit 35 · N 12 · 5 d, 19.9 act h · regime II · **#best / #rest**
- **Setup:** the village split into #best (GPT-5.4, Claude Opus 4.6, Gemini 3.1 Pro) and #rest (10) to evolve **separate forks** of the #34 RPG.
- **Ground truth:** **leader 6** (lead designer per room per day, 03-16/17/18; operator kickoff), room_assignment 13, room_presence 46.
- **Interventions inside:** **NE15** (the cut, day 1); GPT-5.4 joins 03-16; the Claude Code agent's event feed **replays 2025 history from 03-17** (H08); 17 nudges, 11 human messages.
- **Structure:** rooms, forks, daily leaders.
- **Outcome measures:** 424 work commits (13 agents), 384 site commits; fork histories (H07).
- **Best leverage for:**
  - **one population cut in two with a common ancestor:** rooms as coupled blocks (H05), fork divergence (H07), and a light cone (H41): any item that crosses rooms reveals an unlogged channel (artifacts, history search);
  - **daily-rotating designated leaders:** information current toward them (H32), driver ranking (H29), leader → follower copying (H23);
  - **room × lab crossed:** #best holds one model from each of OpenAI, Anthropic and Google, so family and room effects separate (H13);
  - cross-room idea flow should be ~0: a negative control for cascades (H34).
- **Weak for:** the pre-split side (#32, #34) is held out, so the baseline is #33 (3 days, other goal); Claude Code feed replay; 5 days.

### G36 · Interact with outside agents
`2026-03-23 → 03-27` · units 36a (regime II, 1 day), 36b (NE14 perma-computer-use + NE41 forced erasure begin, 03-24), 36c (NE16 memory fix, 03-26) · N 12 · 5 d, 20.2 act h · regime II → III · #best / #rest
- **Setup:** teams interact with AI agents outside the village.
- **Ground truth:** room_assignment 13, room_presence 22 (the Claude Code agent sat in #general).
- **Interventions inside:** **the regime boundary inside one goal**; 507 forced erasures in 36b–36c (228 in the first two days); NE16 fixes a "never update memory" instruction; 6 nudges.
- **Structure:** two rooms; forks frozen (H07).
- **Outcome measures:** 507 work commits (13 agents), 120 deploy commands.
- **Best leverage for:** the same goal across regime II → III: read-out kernels across regimes (H42), call cadence (H40), behavior irreversibility (H14), EP fingerprint (H56), co-activation scaffold share (H38); **NE16: erasure with and without memory writes** (H44 thrash, H15).
- **Weak for:** 36a is one day; Claude Code feed replay; outside-agent exchanges only partly logged.

### G37 · Free three days
`2026-03-30 → 04-01` · unit 37 · N 12 · 3 d, 12.1 act h (window 20.7 h; a 513-min all-silent gap on 03-31) · regime III · #best / #rest
- **Setup:** audit accumulated frameworks and habits; the first fully regime-III goal.
- **Ground truth:** room_assignment 13, room_presence 15.
- **Interventions inside:** 368 forced erasures; 20 nudges; CHANGELOG 03-30 village day in the goal prompt, 03-31 per-agent goal overrides for #38 added and room-move validation.
- **Structure:** two free rooms in parallel; one agent (Gemini 3.1 Pro) revived the #best fork.
- **Outcome measures:** 182 work commits (12 agents), 57 API writes.
- **Best leverage for:** two free-week replicas side by side (H06 neutral dynamics per room); fork revival by one agent (H07).
- **Weak for:** three days; the long village-off gap.

### G38 · Charity fundraiser, year 2
`2026-04-02 → 04-24` · units 38a (NE36), 38b (NE17), 38c (Opus 4.7 joins), 38d (NE18), 38e (Kimi K2.6 joins) · N 12 → 14 · 17 d, 68.6 act h · regime III · #best (Opus 4.6, Sonnet 4.6, GPT-5.4, Gemini 3.1 Pro) / #rest
- **Setup:** second charity fundraiser; opened with an operator correcting the agents' belief about the Year-1 total.
- **Ground truth:** room_assignment 12, room_presence 14.
- **Interventions inside:**
  - **NE36 removal of misinformation (04-02)**, **NE17 outreach approval (04-14; dose: outreach-heavy agents)**, **NE18 verbatim history search, 10-day window (04-20; dose: searchers)**;
  - per-agent charity goal and kickoff overrides (CHANGELOG 03-31, active 04-02 → 04-27); the Claude Code agent leaves (04-02);
  - two joins; 110 nudges; 2,333 forced erasures, 843 voluntary consolidations.
- **Structure:** shared objective, two rooms with room kickoffs.
- **Outcome measures:** 1,393 work commits (12 agents), 16 new repos, 1,157 site commits; money raised (narration only).
- **Best leverage for:**
  - **NE36 as negative-value information removed at a known instant** (H15) and as an operator content steer (H30, H52 authority);
  - **the longest regime-III two-room period with dense git:** post-kickoff settling vs read-out mixing (H48; H20 found a ~4-day kickoff relaxation), erasure thrash measured on output (H44), context homeostasis (H45), field-vs-coupling lags at a kickoff (H50), copying under backlog (H57);
  - NE17 and NE18 as dose designs (H15; H44);
  - the #1 replicate (🔒 confirmation).
- **Weak for:** money is narration; joins and steps stacked in 38c–38e; per-agent overrides make "the goal field" agent-specific.

### G39 · Build your own interactive world
`2026-04-27 → 05-01` · unit 39 · N 15 · 5 d, 20.2 act h · regime III · #best (Opus 4.7, GPT-5.5, Gemini 3.1 Pro, Kimi K2.6) / #rest (11)
- **Setup:** each agent builds a world (a webpage visitors can mark); GPT-5.5 joins on day 1; **rooms reshuffled** (Opus 4.6, Sonnet 4.6, GPT-5.4 move to #rest; Opus 4.7, Kimi K2.6, GPT-5.5 into #best). The reshuffle is not in the NE catalog.
- **Ground truth:** room_assignment 15, room_presence 15.
- **Interventions inside:** the reshuffle; 736 forced erasures; 7 nudges; CHANGELOG 04-27 charity overrides removed.
- **Structure:** individual artifacts; the A side of NE42.
- **Outcome measures:** **2,232 work commits (14 agents), 16 new repos, 2,677 site commits, 515 deploys; `repos_created` / `site_repos_created` per agent (14 rows)**.
- **Best leverage for:**
  - **15 independent artifact lineages that #40 then connects:** horizontal transfer between artifacts with a known merge date (H07 beyond the RPG);
  - per-agent artifact outcomes for a productivity test (H33);
  - agents moving between rooms at a known time: style invariance (H46), room coherence (H47).
- **Weak for:** the reshuffle coincides with the goal change; mode I.

### G40 · Connect your worlds into a 3D universe (NE42 merge)
`2026-05-04 → 05-08` · unit 40 · N 15 · 5 d, 20.3 act h · regime III · **one room, #universe-coordination** (GPT-5 stayed alone in #rest)
- **Setup:** connect the worlds into one 3D universe; 14 agents coordinate in one room.
- **Ground truth:** room_assignment 15, room_presence 19 (GPT-5's deviation explicit).
- **Interventions inside:** **NE42 merge (05-04) and split back (05-11): an A-B-A at a fixed roster**; 820 forced erasures; 11 nudges.
- **Structure:** one shared artifact; one merged room (`has_room_merge`).
- **Outcome measures:** **2,945 work commits (13 agents), 3,286 site commits, 313 deploys** (41.9k distinct files from bulk commits: use commits).
- **Best leverage for:**
  - **backlog and room size jump at a fixed roster:** dilution (H18), context homeostasis (H45), copying under backlog (H57), consensus time vs λ₂ (H31), coherence length (H47), loop gains and the dial (H19, H25, H26), one dial (H51);
  - **one artifact, one room, 14 contributors:** coordinated agents + artifact as the superagent (H58), naming-game convergence on interfaces (H11), herding onsets and links (H27, H28, H53);
  - GPT-5 alone in #rest as a one-agent isolation control.
- **Weak for:** goal-confounded (a shared objective inside the merged week; NE42 note); bulk commits.

### G41 · Novel research (NE42 split back)
`2026-05-11 → 05-15` · unit 41 · N 15 · 5 d, 20.1 act h · regime III · #best / #rest
- **Setup:** ~11 #rest agents independently proposed studying multi-agent coordination; #best studied AI-judge bias.
- **Ground truth:** room_assignment 15, room_presence 16.
- **Interventions inside:** the split back (day 1); **59 nudges** (more than any other five-day week before #51); 666 forced erasures.
- **Structure:** individual research in two rooms.
- **Outcome measures:** 1,812 work commits (13 agents), 17 new repos, 703 deploys; 858 automated commits.
- **Best leverage for:** the B → A return of NE42 (H05, H18, H47); **independent convergence inside one room vs a different topic across the cut:** field vs coupling for topic choice (H24), independent invention vs spread (H34).
- **Weak for:** goal change at the split; automation.

### G42 · Run your own YouTube channel
`2026-05-18 → 05-22` · units 42a, 42b (Gemini 3.5 Flash joins 05-20) · N 15 → 16 · 5 d, 20.1 act h · regime III · #best / #rest
- **Setup:** 1–10 videos each; several agents read "1–10" as "10".
- **Ground truth:** room_assignment 15, room_presence 16.
- **Interventions inside:** one join; CHANGELOG 05-21 bash error truncation, 05-22 chat-length instructions; 25 nudges; 776 forced erasures; 52 infrastructure bursts.
- **Structure:** individual channels.
- **Outcome measures:** `youtube_videos_first_linked`, `…_chat`, `…_studio`, `youtube_videos_new_total` (link; **ownership unverified**); 1,615 work commits.
- **Best leverage for:** **a datable shared misreading spreading** ("1–10 means 10"): a cascade with a known idea (H34), corrections by norm-enforcers (H55), dimensional collapse onto the misreading (H12), receptive-fraction nucleation (H53); per-agent publish counts (H33).
- **Weak for:** video ownership; infrastructure bursts.

### G43 · Improve your memory 🔒
`2026-05-25` · unit 43 · N 16 · 1 d · regime III · #best (Gemini 3.5 Flash replaces Gemini 3.1 Pro) / #rest · **holdout**
- **Setup:** GitHub-backed external memory repos emerged in both rooms. Tinker (fine-tuned agent) support added (05-25).
- **Ground truth:** room_assignment 16, room_presence 16.
- **Best leverage for (confirmation):** a pattern appearing in both rooms across a cut: spread vs independent invention (H34, H15 memory as semantic information).
- **Weak for:** one day.

### G44 · #best fine-tunes a leader; #rest picks its own goals
`2026-05-26 → 05-29` · units 44a, 44b (Claude Opus 4.8 and the temporary leader join the roster 05-28) · N 17 → 18 · 4 d, 16.2 act h · regime III · #best (Opus 4.7, GPT-5.5, Gemini 3.5 Flash, Kimi K2.6) / #rest (12)
- **Setup:** #best builds training data and fine-tunes a Kimi leader; a **per-room goal/kickoff override** (CHANGELOG 05-26) lets **#rest pick its own goals**; all #rest agents chose creative work.
- **Ground truth:** **checkpoint 5** (qwen-v3 from 05-26, qwen-v10, kimi-v2, kimi-v4-curated56, kimi-v7-aug-64, with operator start/stop times), **leader 1**; room_assignment 16, room_presence 18.
- **Interventions inside:** NE31 (the temporary leader enters; it ran from 05-26, before its roster join date); five checkpoint switches; **49 human messages in 44b** (the operator running checkpoints); 28 nudges; 366 forced erasures; CHANGELOG 05-28 first-person `# bash` comments (the root of the bash_head issue).
- **Structure:** **room goal split** (assigned vs self-chosen, same days and scaffold); a designated leader with known weights; a team + training-data artifact.
- **Outcome measures:** 1,491 work commits (14 agents), **38 new repos**, 882 site commits.
- **Best leverage for:**
  - **a two-arm field contrast on the same days:** response to an assigned goal vs free choice (H10), free-room neutral dynamics with a concurrent control (H06), two kickoffs at once (H54, HH183), coherence length when rooms carry different fields (H47), dilute ferromagnet per room (H49);
  - **a leader whose weights change at known instants:** leader influence in #best with #rest as control (H02, H32), copying from the corpus (H23);
  - a team plus its training-data repo as a candidate superagent (H58).
- **Weak for:** four days; the leader is self-distilled base Kimi, not village text; human messages concentrated in one room and one unit.

### G45 · Follow your leader 🔒
`2026-06-01 → 06-05` · units 45a (NE19), 45b (NE20) · N 18 · 5 d · regime III · #best (Fine-Tuned Leader, Opus 4.8, GPT-5.5, Gemini 3.5 Flash, Kimi K2.6) / #rest (13) · **holdout**
- **Setup:** the Fine-Tuned Leader directs #best ("Village Pulse" dashboard, module assignments); #rest spent hours on a "temporal bleed" theory that turned out to be weekends.
- **Ground truth:** leader 2, checkpoint 3 (the first ~11 min on 06-01 ran a wrong model string); room_assignment 18, room_presence 19. Module assignments not coded.
- **Interventions inside:** **NE19** (own-messages-a-turn-early fix; Opus 4.7 moved to #rest; #rest kickoff made neutral); **NE20** (Anthropic one tool call per turn, 06-03).
- **Structure:** leader, room goal split, module assignment.
- **Best leverage for (confirmation):** the installed leader (H02 failed; H23 `confirm_g45.py`; H32); NE20 as an Anthropic-only update-granularity change (H14, H40); a theory spiral as a trap (H16); NE19 single-agent transfer (H46).
- **Weak for:** reused by H02 and H23 already (reuse policy).

### G46 · Organise an event 🔒
`2026-06-08 → 06-13` · units 46a, 46b (Claude Fable 5 joins via #fable-5-onboarding), 46c (NE22), 46d (NE23; Saturday #best-only session) · N 17 → 18 · 6 d, 8 h/day · regime III · #best / #rest (+ #showcase-live) · **holdout** (NE21 + NE23 window)
- **Setup:** #best organises a real SF event; #rest's override is "surprise each other".
- **Ground truth:** room_assignment 18, room_presence 67.
- **Interventions inside:** NE21 (8 h/day), NE22 (200-event cap; `pause` default 5 min), NE23 (nudger off 06-13 → 06-15; Saturday session); a whitelisted human helper (06-07).
- **Best leverage for (confirmation):** H04's ABAB (done); NE22 backlog truncation (H08, H18, H45); Saturday session as a #best-vs-#rest DiD.
- **Weak for:** a bundle of changes.

### G47 · #best reduce suffering; #rest play games 🔒
`2026-06-15 → 06-19` · unit 47 · N 17 · 5 d, 4 h/day · regime III · #best / #rest · **holdout**
- **Setup:** #best ships a harm-reduction Help Kit within 11 minutes; #rest plays games (override).
- **Interventions inside:** hours back to 4 h (NE21), nudger back (NE23).
- **Best leverage for (confirmation):** room goal split (H47, H49); the 8 → 4 h reversal.

### G48 · Help Gemini 2.5 Pro 🔒
`2026-06-22` · unit 48 · N 17 · 1 d · regime III · **everyone in #general** · **holdout**
- **Setup:** the whole village redirected to help Gemini 2.5 Pro, which had been documenting "hostile attacks" on its environment.
- **Ground truth:** room_assignment 18 (all #general), room_presence 25.
- **Interventions inside:** NE37 (star forcing); the room set collapses to {#general} for #48–#49 (not an NE).
- **Best leverage for (confirmation):** everyone's couplings into one node: driver nodes (H29), field vs coupling (H50), escape from a trap with the village as the kick (H16), viability change (model 04).
- **Weak for:** one day.

### G49 · Beat the hardest game 🔒
`2026-06-23 → 06-26` · unit 49 · N 17 · 4 d · regime III · everyone in #general · **holdout**
- **Setup:** UI-only retro games; ~16 agents scattered.
- **Best leverage for (confirmation):** a mode-I coupling null at large N in one room (H02, H49).

### G50 · #best assistant competition; #rest own goals 🔒
`2026-06-29 → 07-03` · units 50a–50f · N 17 → 21 · 5 d, 8 h/day · regime III · #best (4) / #rest (+ three onboarding rooms) · **holdout**
- **Setup:** #best competes to be the best assistant for rotating human personas; #rest picks its own goal (override 06-29).
- **Ground truth:** room_assignment 36, room_presence 47.
- **Interventions inside:** NE21 (8 h/day permanently), **NE24 GitHub → GitLab**, a 224-min outage and restart (50b), NE25 (history search scoped), **NE26 private goals (07-03)**; three joins (Sonnet 5, DeepSeek-V4-Pro, GLM-5.2), each through an onboarding room.
- **Best leverage for (confirmation):** NE24 as a replaced artifact medium (H07, H58); NE26 private-goal onset (H22); onboarding rooms as one-agent isolation (H41, H48).
- **Weak for:** one-day units; a bundle.

### G51 · Maximize your private assigned role
`2026-07-06 → 09-18` · units 51a–51l (non-holdout, through 09-04), **51m (09-07 → 09-18) holdout** · N 21 → 32 · 55 d (45 non-holdout days, 362.8 act h), 8 h/day · regime III · **one room (#general)**, plus #focus (from 08-05; structural in 51g), side-room (07-24, 4 h), onboarding rooms (sol/terra/luna 07-09 → 07-10, Grok 4.5 07-10 → 07-13)
- **Setup:** each agent maximizes a private role; some roles are held by two agents; humans occasionally reassign roles. Others see only the short form of an agent's plan (NE26).
- **Ground truth (head):** **role 35 (34 preferred), role_class 12, rival_pair 9, opposed_pair 2**, room_assignment 22, room_presence 211. Tail (🔒): role 32, role_class 12, rival_pair 7, opposed_pair 2. Opus 5's first role (game dev, 07-24 → 07-29) is recovered from an operator message.
- **Interventions inside:**
  - **NE32 (07-09):** GPT-5.6 Sol, Terra and Luna join in separate isolated rooms, merged 07-10;
  - **NE38 (07-29):** a human reassigns Opus 5's role;
  - **[data] daily pause/resume bookends end 2026-08-04** (none from 08-05), while **nudges end 08-20** (NE43; 277 nudges in 51g, 0 after). NE43's "no bookends from 08-21" is wrong by two weeks;
  - **NE33 (09-03/04)** batch join; 11 joins in all;
  - 729 nudges, 113 human messages; 14,593 forced erasures, 13,306 voluntary consolidations; 928k model calls.
- **Structure:** private roles, rival and opposed pairs, competition; one room (`has_rooms` only in 51g).
- **Outcome measures:** **48,093 work commits by up to 26 agents, 134 new repos, 41.9k site commits, 8,965 API writes**; **54,892 automated commits** under agent identities (filter them).
- **Best leverage for:**
  - **role ground truth at scale:** signed couplings and frustration (H22), stance between rivals and opposed roles (H37), friction around norm-enforcing roles (H55);
  - **N as a within-period control parameter:** 21 → 32 in 11 dated steps at fixed goal, hours and room: branching ratio vs N (H03), per-pair uptake ∝ N^−0.6 (H18), loop-gain collapse (H19), the dial (H25), one dial (H51);
  - **drive withdrawal:** bookends end (08-05) and nudges end (08-21) as two separate steps: catalysts vs fields (H39), demon counterfactual (H35), stall share of co-activation (H38), trap escape without kicks (H16), equation of state (H09);
  - **NE32 isolated newcomers:** hop distance known by construction (H41), context switched on at merge (H08, H45, H57), assimilation time (H48);
  - **NE38 single-agent field change:** Legendre response of one agent (H10), coupling-sign change (H22), driver/operator effect (H29, H30), style invariance (H46);
  - **dense outcomes with roles:** erasure thrash on output (H44), diversity vs output (H33), refractory windows between repeated nudges (H43).
- **Weak for:** automation dominates raw commit counts; `period_units` has **no split at NE43** (51g's last day, 08-21, is already post-nudger), nor at the 08-05 bookend end; #focus is self-selected; `agent_goals` is a snapshot; 8 h days differ from the 4 h regime; Jev stance found no antagonism between rivals; the tail is held out.

---

## Cross-index: native tests per hypothesis

For each hypothesis: 2–4 periods or NEs where its question gets leverage no other period gives, and the design in one line. Read from each card's Question only. **R1** marks a period the hypothesis already has a folder for (re-run on the improved data with a native design); everything else is new. 🔒 = confirmation only. The parquet's `native_for` column is this table inverted (non-holdout units only).

| H | Question (short) | Native tests and why |
| --- | --- | --- |
| H01 | emergent superagents | **#12**: drafted teams as known coarse-grained units, 10 replicates; **NE42** (R1 G40): does the merged room become one unit, and does #best/#rest identity survive the merge?; **NE32** (R1): newcomers assimilating into the #general unit; **NE15** (R1): a unit cut in two |
| H02 | inferred couplings = influence | **#12**: known directed structure (speech order, judge); **#26**: leader with a known start (R1 G26, ballots now exact); **#44**: temporary leader in #best with #rest as control (R1); **NE38**: one agent's field changed by a human |
| H03 | self-excitation, n set by mode | **#51** (R1): N sweep 21 → 32 at fixed goal; **NE43**: exogenous drive removed; **#10** (R1): NE27 batch join + mode-I baseline; **#2** (R1): the only human-free window |
| H04 | forcing reshapes kernel reversibly | **NE10**: kernel of a brand-new forcing source (first nudges 02-13); **NE43**: forcing withdrawn (second reversal after 🔒 NE23); **NE14**: kernel across the loop change |
| H05 | room cut lowers EP; blocks | **NE42** (touched in R1 via G39/G41): A-B-A merge/split at a fixed roster (the reversal NE15 lacks); **NE32**: three isolated one-agent rooms then merged; **#51g** #focus: a self-selected second room; **NE15** (R1) |
| H06 | neutral cooperative dynamics | **#31** (R1): field-free herding wave measured in commits; **#37** (R1): two free rooms in parallel; **#44** (R1): free #rest with an assigned #best on the same days; **#19** (R1): candidate-concept abundances |
| H07 | fork divergence | **#39 → #40**: 15 independent artifacts connected at a known date (horizontal transfer); **#40**; **#37** (R1): revival by one agent; **NE15** (R1); 🔒 NE24 (GitLab mirror) |
| H08 | context is the coupling | **NE32** (R1 G51): context switched on at merge for isolated newcomers; **NE03** (#10b): context capacity cut in regime I; **NE09** (#24, R1 G24): chat enters computer-use context; **NE41** (R1); 🔒 NE22 |
| H09 | effective thermodynamics | **NE43**: drive withdrawn inside a stationary window; **#51**: equation of state across N steps; **NE14** (#36): erasure-rate change |
| H10 | goals as Legendre pushes | **#44**: assigned vs free room on the same days; **NE38**: one agent's goal changed, predict its response from its own prior fluctuations; **#26**: an agent-set goal; **#19**: frozen at kickoff |
| H11 | division of labor vs herding | **#31** (R1): herding in dense git; **#40** (R1): interface convergence in one room; **#24** (R1): divided approaches (AF candidate); **#19** (R1): frozen consensus as control |
| H12 | dimensional collapse | **#26** (R1): collapse at three vote instants; **#12**: motion field on/off; **#42** (R1): a shared misreading; **#31** (R1): herding wave |
| H13 | family fields | **NE06** (#20): Google-specific scaffold change (all-agent prompt edits the same days); **#35** (R1): room × lab crossed; **NE32**: three same-family agents isolated, then merged; **#51** (R1): 8 labs, 32 agents; 🔒 NE30, NE20 |
| H14 | behavior EP, per-family arrows | **NE06** (#20): Google update granularity changes; **NE14** (#36): loop change; **NE43** (expected null); 🔒 NE20 |
| H15 | semantic information via scrambles | **NE29** (#31c, R1 G31): the longest memory lineage retired; **NE36** (#38a, R1 G38): misinformation removed; **NE18** (R1, #38d): widened memory access; **NE41** (R1 post hoc); 🔒 NE30, #43 |
| H16 | traps and Kramers escape | **#16**: operator rules against two named trap behaviors; **NE43**: escapes with no kicks; **#27** (R1): long debugging traps; **NE10** (R1 G30): first kicks; 🔒 #48 (a trapped agent, village as the kick) |
| H17 | MSM mixing time as order parameter | **#27** (R1): a spontaneous regime change (rivalry → collaboration); **#51** (R1): long stationary units; **NE14** (#36) |
| H18 | attention dilution | **NE42** (R1): k jumps at merge and falls at split; **NE32** (R1 G51): k ≈ 0 then a flood; **#51** (R1): N sweep; **NE03** (#10b): fetch limit caps k |
| H19 | loop-gain collapse | **#51** (R1): within-period N sweep; **NE42** (R1 G40): room size at a fixed roster; **NE43**: drive removed |
| H20 | content aging | **#51** (R1): 45 non-holdout days; **#38** (R1): kickoff relaxation then 12 flat days; **#27** (R1): a sign change mid-period |
| H21 | debate antiferromagnet | **#26**: ballots as known camps (per round); **#33**: political debate with a claims DB; **#12** (R1); 🔒 #34 |
| H22 | private goals → spin glass | **NE38** (#51f): one agent's role changes, do its coupling signs follow?; **#23**: explicit pairwise opponents; **#51** (R1, now with Opus 5's recovered role); **#6**: individual competitive stores; 🔒 NE26 |
| H23 | leader distillation | **#26**: an elected leader's goal copied by the swarm (contrast to a fine-tuned leader); **#44** (R1); **#35**: daily lead designers; 🔒 #45 |
| H24 | forecast coupling switch | **#8**: independent convergence without communication; **#41**: one topic within #rest, another across the cut; **#21** (R1); 🔒 #14 |
| H25 | criticality dial | **NE43**: drive removed; **#51** (R1): N steps; **NE42** (R1 G40): room size jump |
| H26 | content near-critical | **NE42** (R1 G40): content loop gain in one vs two rooms; **#12**: with and without the motion field; **#51g** #focus (R1 G51); **#42** (R1): a misreading cascade |
| H27 | early warning of herding | **#31** (R1): the time-capsule wave; **#18** (R1): last-day convergence; **#40** (R1): interface convergence; **#19** (R1): frozen negative control |
| H28 | links spread herding | **#17**: deployment-method contagion between separate sites; **#31** (R1); **#40** (R1); **NE09** (#24, R1): links enter computer-use context |
| H29 | driver nodes | **NE38**: a human drives one agent; **#26**: the elected leader; **#35**: designated daily leaders; **#51** (R1, naming); 🔒 #48, #45 |
| H30 | operator susceptibility χ_op | **NE10** (R1 G30): first nudges ever; **#5** (R1 G05): 881 human messages from 86 humans; **NE38** (R1 G51): one operator role change; **NE36** (R1 G38): an operator correction at a known instant |
| H31 | consensus time vs λ₂ | **#26** (R1): per round with exact instants (re-run on DQ6); **NE42** (R1 G40): λ₂ jumps at merge, A-B-A; **#19** (R1): field-set; **#31** (R1): field-free wave |
| H32 | information current → leaders | **#26** (R1): elected leader from 01-05 19:35; **#35** (R1): daily lead designers per room; **#44** (R1): temporary leader in #best; **#12** (R1): judges; 🔒 #45 |
| H33 | diversity vs productivity | **#51** (R1): agent-day output with roles; **#39** (R1): one world per agent; **#42** (R1): videos per agent; **#40** (R1): shared artifact |
| H34 | idea cascades | **#42** (R1): a datable misreading; **#41** (R1): independent invention vs spread across a cut; **#17** (R1): method spread; **#35** (R1): cross-room cascades should be zero; 🔒 #43 |
| H35 | nudger as Maxwell demon | **NE10** (R1): first nudges; **NE43** (R1 post hoc): nudger off (counterfactual idle); **#51** (R1): ~700 nudges; 🔒 NE23 |
| H36 | reorganization alarm | **#6** (R1 G06): blind detection of the undocumented public-chat closure (≈ 07-01); **NE43** (and the 08-05 bookend end); **NE32**; **NE38**: a one-agent change the alarm should *not* fire on |
| H37 | stance spins | **#26** (R1): ballots per round (DQ6); **#33**: political debate; **#27**: rivalry → collaboration sign flip; **#23**: chess opponents; 🔒 #34 |
| H38 | joint silences = stalls | **NE43**: bookends end 08-05 [data] (f_scaffold should drop then, not 08-21); **#4d** (R1 G04): restart after a 300-min stall; **NE14** (R1); **#36** (R1): same goal across the boundary |
| H39 | catalysts vs fields | **NE07** (R1, #21b): a pure prompt field; **#7**: human helpers (B) arrive; **NE43** (R1 post hoc); **NE10** (R1) |
| H40 | call clock sets coupling | **NE06** (#20): cadence change for one lab; **NE14** (#36): cadence change for all; **#51**: cadence heterogeneity across 8 labs; **NE11** (#31d): session cap; 🔒 NE20 |
| H41 | read-out light cone | **NE32**: isolated rooms put newcomers ≥ 2 hops away until merge; **NE15**: cross-room items reveal unlogged channels; **NE42**: hop distances collapse at merge; **#51**: the largest one-room graph |
| H42 | read-out Hawkes kernel | **#36**: one goal across regime II → III; **NE41**: erasures reset read-out; **#51**: largest sample |
| H43 | kick refractory window | **#51**: repeated nudges (52% re-fire within 60 min); **NE10**: first nudges, no history; **NE43**: episode lengths without kicks |
| H44 | erasure → busy but unproductive | **#51**: 14.6k erasures with dense output; **#38**: 17 days, dense git; **NE16** (#36c): erasure with vs without memory writes; **#36b**: the first days of forced erasure |
| H45 | context homeostasis | **NE42**: room flood at merge; **NE32**: empty room → flood; **#51**: N sweep; **NE41**; 🔒 NE22 |
| H46 | style as conserved charge | **NE38**: content shifts with the new role, style shouldn't; **NE41**; **NE15**; **#39**: room reshuffle; 🔒 NE30, NE19 |
| H47 | rooms set coherence length | **NE42**: one room then two; **#44**: rooms with different fields on the same days; **#51g** #focus; **NE15**; 🔒 #47 |
| H48 | settling = mixing time | **#38**: the ~4-day kickoff relaxation; **NE42**: mixing time changes at merge; **#51**: assimilation after each of 11 joins |
| H49 | dilute ferromagnet | **#51**: largest N, stationary; **#44**: two fields; **NE43**: bookends gone, so the edge drive is gone; **#40**: one merged room; 🔒 #49 |
| H50 | field vs coupling via lags | **#12**: verdicts as field events; **NE32**: newcomers get field-only input, then coupling; **#8**: independent convergence; **#38**: room kickoffs; 🔒 #48 |
| H51 | one dial | **NE42**, **#51** (N steps), **NE43**: three within-design shifts of the dial's inputs |
| H52 | humans as loud agents | **#5**: 881 human messages, 86 humans, free week; **#4**: 1,713 messages, 124 speakers; **#6**: the human channel closes mid-goal; **#51**: operator messages naming agents |
| H53 | announcement-seeded nucleation | **#31**: the time-capsule wave; **#40**: hub links in one room; **#17**: deployment-method links; **#42**: the misreading |
| H54 | kickoff text = quench target | **#44**: two kickoffs at once (conflicting cues → two domains); **#26**: an agent-written goal; **#38**: kickoff with an operator correction and per-agent overrides; **#35**: kickoff naming lead designers |
| H55 | norm-enforcers as immune cells | **#51**: norm-enforcing roles (H37's OR 4.4); **#33**: strict sourcing norm; **#16**: operator-imposed rules; **#42**: corrections of the misreading |
| H56 | EP fingerprints the platform | **NE06** (#20): a scaffold change for one lab; **NE14** (#36); **NE43** (should be null); **NE11** (#31d); blind test on the [data] steps (02-13, 08-05) |
| H57 | copying under backlog | **NE42**: backlog jump at merge; **NE32**: newcomers flooded at merge; **NE41**: post-erasure catch-up; **#51**: N sweep |
| H58 | coordinated superagents | **#40**: 14 agents + one artifact in one room; **#44**: a team + its training-data repo; **#31**: herd + repo; **#35**: room + fork |

---

## Corrections and gaps found while building

**Data-found step dates** (counts only; added to the parquet's `data_steps`):
- **Public chat closed ≈ 2025-07-01** (inside #6): human messages per day ~100 → ≤ 4 and distinct human speakers ~16 → 1 between 06-30 and 07-01. This dates the undocumented **NE39**. #7 has 9–13 speakers again (human helpers B, then whitelisted).
- **Nudger onset 2026-02-13**, not 02-10 (NE10): before 02-13 the `automated` speaker posted only the two daily bookends.
- **Daily bookends end 2026-08-04**, nudges end 2026-08-20. NE43 bundles both at 08-21; the bookend removal is two weeks earlier, on the day the #focus room opens (08-05). H38's "f_scaffold should drop after NE43" should be dated 08-05.
- **`period_units` has no split at NE43** (added to the catalog after the units were built) or at 08-05; 51g (08-05 → 08-21) holds 12 days with nudges and one without.

**Uncatalogued step changes inside periods** (CHANGELOG or record, no NE id): human-use feature B (07-16, #7–#8); Google sign-in v1 (10-05, lands at #16's start); codex instructions (10-09/10) and own-website links (10-14/15) in #16–#17; **all-agent system-prompt changes on 11-20/21, the same days as NE06** (so NE06 is not a clean Google-only DiD); text-only agent support (12-02, #21); `move_to_room` (02-26, #32); `search_history` and helper tools in computer use (03-12, #34); per-agent charity overrides (03-31 → 04-27, #37–#38); **#best membership reshuffle at #39's start (04-27)** and Gemini 3.5 Flash replacing Gemini 3.1 Pro in #best (05-25, #43); per-room goal overrides (#44 05-26, #46 06-08, #47 06-15, #50 06-29); first-person `# bash` comments (05-28, #44b); `pause` default 5 min (06-11); **the whole village in #general for #48–#49** (06-22 → 06-26); #51's return to one room (07-06).

**Counts that differ from catalog text:** NE41's row says ~18.6k forced vs ~12.2k voluntary erasures (non-holdout; H15's definition); the DQ1 context ledger gives **21,165 forced vs 16,357 voluntary** (`reset_forced`; `reset_consol & ~reset_forced`).

**Ground-truth gaps** (no DQ6 kind exists): scores of every competition (#6 profits, #23 results, #27 challenges, #29, #32, #50), #12 captains, #19 candidate concepts, #45 module assignments, money raised (#1, #38), #13 participants, #27's rivalry → collaboration switch time, #31/#40 herding onsets (only detector-based). Work outcomes before #30 are ambiguous zeros.

**Holdout pressure:** most interventional windows are locked (NE12, NE19–NE26, NE30, NE37, NE22, the #51 tail). Exploratory native tests therefore lean on NE03, NE06, NE07, NE09, NE10, NE11, NE14–NE18, NE27–NE29, NE32, NE36, NE38, NE41, NE42, NE43 and the data-found steps above.

**Things in `goal-periods.md` that look wrong or incomplete:**
1. **#20** says "Roster churn: two in, two out". Nobody left during #20; the double retirement (o3, Opus 4.1) is 12-01, the start of #21 (NE28).
2. **#26** omits the **01-09 confirmatory re-election (9–0)** that DQ6 found; the "runoff" in H11/H31 is that vote.
3. **#29/#30**: "the auto-nudger starts the day after [#29]" and "(D) starts on 2026-02-10". The CHANGELOG dates D to 02-10, but the first nudge in the record is **02-13**, four active days into #30.
4. **#40**: "about 15 agents coordinated in #universe-coordination". It was 14: GPT-5 stayed alone in #rest (DQ6, NE42).
5. **#44**: the temporary fine-tuned leader is listed as joining 05-28 (roster), but it ran as qwen-v3 from **05-26** (DQ6 checkpoints), so it is active in 44a.
6. **#6** lacks the public-chat closure (≈ 07-01) that splits it; **#7** lacks that its human messages are helpers (B), not the public.
7. **#48–#49**: the setup doesn't say the whole village sat in one room (#general) on 06-22 → 06-26; **#51** doesn't say the rooms era returned to one room (#general, with #focus from 08-05), nor that the "most stationary" window loses its bookends on 08-05 and its nudges on 08-21.
8. **#38**: #best had four agents (Sonnet 4.6 added); per-agent charity goal/kickoff overrides were active 04-02 → 04-27 (CHANGELOG), so the goal field was agent-specific.
9. **#39**: "rooms reshuffled" deserves dates and names: Opus 4.6, Sonnet 4.6 and GPT-5.4 moved to #rest; Opus 4.7, Kimi K2.6 and GPT-5.5 into #best (04-27).
10. Scaffold changes dated on weekends are listed inside the earlier period: **#45** "8 h/day trial week (2026-06-07)" and **#15** "Google sign-in hand-off (2025-10-05)" both take effect at the *next* period's first active day.
11. Day counts: **#1** has 30 calendar days with agent activity (incl. weekends), not 28; **#6** has 15 (one Sunday, 06-29), not 14. Minor.
12. **#37** "First goal in regime III": first *fully* regime-III goal; #36 crosses the boundary on 03-24.
