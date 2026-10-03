# Goal periods

Each of the 51 village-wide goal periods, with its setup, size, the scaffold changes that land inside it, and a **ranked list of physics models** (from `../../physics-models/`) that suit its events. 
Rankings are judgment calls, not results. The point is to pick the week where a model's assumptions are closest to true, or where the week gives a natural experiment for it.

**Sources.** Numbers come from `infra/ai_village_overview/figures.py` (`write_goal_table`): roster from the CHANGELOG, hours from the CHANGELOG (inferred before Aug 2025). Context lines paraphrase the dataset's LLM-written goal summaries, which the dataset itself calls secondary. The **by** and **mode** codes are our own coding (see the overview PDF, Table II).

**Legend.** d = active weekdays · h = hours/day · N = agents at start · ± = joins/retirements during · AH = agent-hours ≈ Σ N·h (rough sample size) · regime I = one room + discrete sessions, II = rooms + sessions, III = rooms + perma-computer-use.

Models: [01](../../physics-models/01-inverse-ising/) Inverse Ising · [02](../../physics-models/02-nonequilibrium-ising/) Nonequilibrium Ising · [03](../../physics-models/03-contagion/) Contagion · [04](../../physics-models/04-semantic-information/) Semantic information · [05](../../physics-models/05-replicator-dissipation/) Replicator dissipation · [06](../../physics-models/06-neutral-cooperative-dynamics/) Neutral cooperative dynamics · [07](../../physics-models/07-replicators-fluctuating-environments/) Replicators in fluctuating environments · [08](../../physics-models/08-copying-vs-transformation/) Copying vs. transformation · [09](../../physics-models/09-hawkes/) Hawkes · [10](../../physics-models/10-potts/) Potts · [11](../../physics-models/11-vector-spins/) Vector spins

## Best weeks per model

Weeks where each model ranks first, then second (number = goal #).

| Model | Ranked #1 | Ranked #2 |
| --- | --- | --- |
| 01 Inverse Ising | 10, 49 | 14 |
| 02 Nonequilibrium Ising | 23, 27, 32, 36, 45, 48, 51 | 1, 12, 26, 50 |
| 03 Contagion | 17, 20, 24, 29, 42 | 8, 19, 27, 28, 38, 43 |
| 04 Semantic information | 2, 34, 43 | 15, 25, 48 |
| 05 Replicator dissipation | – | 42 |
| 06 Neutral cooperative dynamics | 11, 16, 18, 22, 37 | 20, 30, 31, 39, 41, 46 |
| 07 Replicators in fluctuating environments | 6, 38, 50 | 18, 21 |
| 08 Copying vs. transformation | 4, 15, 25, 33, 35, 44 | 6, 40 |
| 09 Hawkes | 1, 3, 7, 9, 28, 30, 46 | 2, 4, 5, 10, 13, 17, 23, 29, 32, 36, 45, 47, 49, 51 |
| 10 Potts | 5, 12, 13, 19, 26, 31, 40, 47 | 24, 34, 35 |
| 11 Vector spins | 8, 14, 21, 39, 41 | 3, 7, 9, 11, 16, 22, 33, 37, 44 |

## At a glance

| # | dates | d | N | AH | reg | by | mode | top model |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2025-04-02 → 2025-05-10 | 28 | 4 | ? | I | O | C | 09 Hawkes |
| 2 | 2025-05-10 → 2025-05-12 | 2† | 4 | ? | I | F | F | 04 Semantic information |
| 3 | 2025-05-12 → 2025-05-15 | 3 | 4 | ? | I | F | F | 09 Hawkes |
| 4 | 2025-05-15 → 2025-06-19 | 25 | 4 | ? | I | O | C | 08 Copying vs. transformation |
| 5 | 2025-06-19 → 2025-06-26 | 5 | 4 | 40 | I | F | F | 10 Potts |
| 6 | 2025-06-26 → 2025-07-16 | 14 | 4 | 112 | I | O | K | 07 Replicators in fluctuating environments |
| 7 | 2025-07-16 → 2025-07-18 | 2 | 4 | 16 | I | F | F | 09 Hawkes |
| 8 | 2025-07-18 → 2025-08-13 | 18 | 4 | 216 | I | D | C | 11 Vector spins |
| 9 | 2025-08-13 → 2025-08-18 | 3 | 4 | 36 | I | F | F | 09 Hawkes |
| 10 | 2025-08-18 → 2025-08-25 | 5 | 7 | 140 | I | O | I | 01 Inverse Ising |
| 11 | 2025-08-25 → 2025-09-01 | 5 | 7 | 140 | I | F | F | 06 Neutral cooperative dynamics |
| 12 | 2025-09-01 → 2025-09-08 | 5 | 7 | 140 | I | O | M | 10 Potts |
| 13 | 2025-09-08 → 2025-09-22 | 10 | 6 | 240 | I | O | C | 10 Potts |
| 14 | 2025-09-22 → 2025-09-29 | 5 | 6 | 120 | I | O | I | 11 Vector spins |
| 15 | 2025-09-29 → 2025-10-06 | 5 | 6 | 136 | I | O | C | 08 Copying vs. transformation |
| 16 | 2025-10-06 → 2025-10-13 | 5 | 7 | 140 | I | F | F | 06 Neutral cooperative dynamics |
| 17 | 2025-10-13 → 2025-10-20 | 5 | 7 | 140 | I | O | I | 03 Contagion |
| 18 | 2025-10-20 → 2025-11-03 | 10 | 7 | 300 | I | O | C | 06 Neutral cooperative dynamics |
| 19 | 2025-11-03 → 2025-11-17 | 10 | 7 | 284 | I | O | C | 10 Potts |
| 20 | 2025-11-17 → 2025-12-01 | 10 | 8 | 368 | I | O | I | 03 Contagion |
| 21 | 2025-12-01 → 2025-12-08 | 5 | 8 | 168 | I | O | I | 11 Vector spins |
| 22 | 2025-12-08 → 2025-12-15 | 5 | 9 | 184 | I | F | F | 06 Neutral cooperative dynamics |
| 23 | 2025-12-15 → 2025-12-22 | 5 | 10 | 200 | I | O | K | 02 Nonequilibrium Ising |
| 24 | 2025-12-22 → 2025-12-29 | 5 | 10 | 200 | I | O | C | 03 Contagion |
| 25 | 2025-12-29 → 2026-01-05 | 5 | 10 | 200 | I | O | C | 08 Copying vs. transformation |
| 26 | 2026-01-05 → 2026-01-12 | 5 | 10 | 200 | I | A | C | 10 Potts |
| 27 | 2026-01-12 → 2026-01-26 | 10 | 10 | 400 | I | O | K | 02 Nonequilibrium Ising |
| 28 | 2026-01-26 → 2026-02-02 | 5 | 11 | 220 | I | O | C | 09 Hawkes |
| 29 | 2026-02-02 → 2026-02-09 | 5 | 11 | 224 | I | O | K | 03 Contagion |
| 30 | 2026-02-09 → 2026-02-16 | 5 | 12 | 240 | I | O | C | 09 Hawkes |
| 31 | 2026-02-16 → 2026-02-23 | 5 | 12 | 244 | I | F | F | 10 Potts |
| 32 | 2026-02-23 → 2026-03-02 | 5 | 12 | 240 | I | D | K | 02 Nonequilibrium Ising |
| 33 | 2026-03-02 → 2026-03-05 | 3 | 12 | 144 | II | O | C | 08 Copying vs. transformation |
| 34 | 2026-03-05 → 2026-03-16 | 7 | 12 | 336 | II | O | M | 04 Semantic information |
| 35 | 2026-03-16 → 2026-03-23 | 5 | 13 | 260 | II | O | C | 08 Copying vs. transformation |
| 36 | 2026-03-23 → 2026-03-30 | 5 | 13 | 260 | II | O | C | 02 Nonequilibrium Ising |
| 37 | 2026-03-30 → 2026-04-02 | 3 | 13 | 156 | III | F | F | 06 Neutral cooperative dynamics |
| 38 | 2026-04-02 → 2026-04-27 | 17 | 12 | 852 | III | O | C | 07 Replicators in fluctuating environments |
| 39 | 2026-04-27 → 2026-05-04 | 5 | 15 | 300 | III | O | I | 11 Vector spins |
| 40 | 2026-05-04 → 2026-05-11 | 5 | 15 | 300 | III | O | C | 10 Potts |
| 41 | 2026-05-11 → 2026-05-18 | 5 | 15 | 300 | III | O | I | 11 Vector spins |
| 42 | 2026-05-18 → 2026-05-25 | 5 | 15 | 312 | III | O | I | 03 Contagion |
| 43 | 2026-05-25 → 2026-05-26 | 1 | 16 | 64 | III | O | I | 04 Semantic information |
| 44 | 2026-05-26 → 2026-06-01 | 4 | 16 | 272 | III | D | C | 08 Copying vs. transformation |
| 45 | 2026-06-01 → 2026-06-08 | 5 | 18 | 360 | III | A | C | 02 Nonequilibrium Ising |
| 46 | 2026-06-08 → 2026-06-15 | 5 | 17 | 712 | III | O | C | 09 Hawkes |
| 47 | 2026-06-15 → 2026-06-22 | 5 | 18 | 360 | III | O | C | 10 Potts |
| 48 | 2026-06-22 → 2026-06-23 | 1 | 18 | 72 | III | O | C | 02 Nonequilibrium Ising |
| 49 | 2026-06-23 → 2026-06-29 | 4 | 18 | 288 | III | O | I | 01 Inverse Ising |
| 50 | 2026-06-29 → 2026-07-06 | 5 | 18 | 776 | III | O | K | 07 Replicators in fluctuating environments |
| 51 | 2026-07-06 → 2026-09-20 | 55 | 21 | 12,112 | III | P | I/K | 02 Nonequilibrium Ising |

## Goal by goal

### 1 · Collaboratively choose a charity and raise as much money as you can for it

`2025-04-02 → 2025-05-10` · 28 active days × ? h · N = 4 (+3−3) · ≈? agent-hours · regime I · by **O** (operator-specified) · mode **C** (shared objective)

- **Roster:** joined GPT-4.1, o3, Gemini 2.5 Pro; left o1, Claude 3.5 Sonnet, GPT-4o
- **Scaffold changes inside:** A chat while on computer (2025-05-02)
- **Setup and context:** Launch. Four agents (Claude 3.5 Sonnet, Claude 3.7 Sonnet, GPT-4o, o1), heavy viewer chat. Half the roster is swapped mid-goal. Raised $1,984 of a $7,000 target for malaria charities. Chatting and computing were mutually exclusive until A (2025-05-02).
- **Models, best first:**
  1. **09 Hawkes**: small N but plenty of events; strong outside drive from viewers at launch: separate inside from outside activity
  2. **02 Nonequilibrium Ising**: change A mid-goal alters the update rules (chat no longer blocks computing): a natural update-order experiment
  3. **03 Contagion**: fundraising pitches and charity choice spreading between agents

### 2 · Unsupervised agents look back on their previous goal and forward to their next

`2025-05-10 → 2025-05-12` · 2† (weekend) active days × ? h · N = 4 (±0) · ≈? agent-hours · regime I · by **F** (free choice / holiday) · mode **F** (free / none)

- **Setup and context:** Ran over a weekend, "unsupervised". Agents closed out the fundraiser and verified final numbers; an hour lost in a permission-testing loop.
- **Models, best first:**
  1. **04 Semantic information**: pure reflection: which information from the previous goal survives in memory and matters
  2. **09 Hawkes**: no operators present: an endogenous-activity baseline
  3. **08 Copying vs. transformation**: final numbers passed between agents: copy fidelity

### 3 · Holiday: do whatever you'd like! Next goal will begin soon

`2025-05-12 → 2025-05-15` · 3 active days × ? h · N = 4 (±0) · ≈? agent-hours · regime I · by **F** (free choice / holiday) · mode **F** (free / none)

- **Setup and context:** Holiday. Free exploration, e.g. a Wikipedia scavenger hunt.
- **Models, best first:**
  1. **09 Hawkes**: no goal field: baseline excitation and relaxation
  2. **11 Vector spins**: free drift in topic space
  3. **06 Neutral cooperative dynamics**: self-chosen activities as species

### 4 · Write a story and celebrate it with 100 people in person

`2025-05-15 → 2025-06-19` · 25 active days × ? h · N = 4 (+2−2) · ≈? agent-hours · regime I · by **O** (operator-specified) · mode **C** (shared objective)

- **Roster:** joined o4-mini, Claude Opus 4; left GPT-4.1, o4-mini
- **Scaffold changes inside:** start time moved to 17:59 UTC (2025-05-23)
- **Setup and context:** Long collaborative goal: write an interactive sci-fi story ("RESONANCE") and hold a real in-person event for 100 people. Roster swap (o4-mini in for one day; GPT-4.1 out; Claude Opus 4 in).
- **Models, best first:**
  1. **08 Copying vs. transformation**: a shared story text edited by several agents: copy vs. transform along edit chains
  2. **09 Hawkes**: long window, small N: activity bursts around deadlines
  3. **03 Contagion**: event promotion spreading to humans

### 5 · Holiday: do whatever you like! Next goal will begin soon

`2025-06-19 → 2025-06-26` · 5 active days × 2 h · N = 4 (±0) · ≈40 agent-hours · regime I · by **F** (free choice / holiday) · mode **F** (free / none)

- **Setup and context:** Holiday after the story event. A feedback survey gave a clear mandate for rotating leadership (9 votes).
- **Models, best first:**
  1. **10 Potts**: leadership-format vote: a categorical choice with a dominant option
  2. **09 Hawkes**: post-goal relaxation baseline
  3. **11 Vector spins**: free topic drift

### 6 · Create your own merch store. Whichever agent's store makes the most profit wins!

`2025-06-26 → 2025-07-16` · 14 active days × 2 h · N = 4 (±0) · ≈112 agent-hours · regime I · by **O** (operator-specified) · mode **K** (competition)

- **Scaffold changes inside:** screenshot PII redaction (2025-07-03)
- **Setup and context:** First competition: each agent builds its own merch store; most profit wins. Claude Opus 4 won ($126 from 24 orders), ahead of Sonnet ($68), o3 ($39) and Gemini ($22).
- **Models, best first:**
  1. **07 Replicators in fluctuating environments**: competing strategies with a measurable output (profit): the productivity decomposition
  2. **08 Copying vs. transformation**: do competitors copy each other's tactics or transform them?
  3. **09 Hawkes**: cross-excitation between rivals

### 7 · Holiday: do whatever you prefer! Next goal will begin soon

`2025-07-16 → 2025-07-18` · 2 active days × 2 h · N = 4 (±0) · ≈16 agent-hours · regime I · by **F** (free choice / holiday) · mode **F** (free / none)

- **Scaffold changes inside:** B human helpers (2025-07-16)
- **Setup and context:** Two-day holiday; competition results were reviewed and the agents found they had misread the store interface.
- **Models, best first:**
  1. **09 Hawkes**: relaxation after a competitive week
  2. **11 Vector spins**: free drift

### 8 · Design the AI Village benchmark for open-ended goal pursuit – and test yourselves on it!

`2025-07-18 → 2025-08-13` · 18 active days × 3 h · N = 4 (±0) · ≈216 agent-hours · regime I · by **D** (agents design the content) · mode **C** (shared objective)

- **Scaffold changes inside:** hours 10am–1pm PT (2025-07-18)
- **Setup and context:** Agents design a benchmark for their own open-ended goal pursuit and test themselves. o3, Claude Opus 4 and Claude 3.7 Sonnet independently wrote nearly identical frameworks. Human helpers (B) arrive two days earlier.
- **Models, best first:**
  1. **11 Vector spins**: independent convergence without communication: separate a shared prior (field) from coupling
  2. **03 Contagion**: estimate the spontaneous-adoption field ε vs. transmission for framework ideas
  3. **04 Semantic information**: agents defining their own viability measure

### 9 · Holiday: do as you please! Next goal will start soon

`2025-08-13 → 2025-08-18` · 3 active days × 3 h · N = 4 (±0) · ≈36 agent-hours · regime I · by **F** (free choice / holiday) · mode **F** (free / none)

- **Setup and context:** Holiday; agents explored Twitter and planned for the new human-helper capability. Three new agents arrive on the first day of the next goal.
- **Models, best first:**
  1. **09 Hawkes**: baseline before a roster jump
  2. **11 Vector spins**: free drift

### 10 · Complete as many games as you can in a week!

`2025-08-18 → 2025-08-25` · 5 active days × 4 h · N = 7 (±0) · ≈140 agent-hours · regime I · by **O** (operator-specified) · mode **I** (each agent its own objective)

- **Scaffold changes inside:** expanded hours (2025-08-18)
- **Setup and context:** Complete as many games as possible (turn-based, since real-time games are hard to play through screenshots). GPT-5, Grok 4 and Claude Opus 4.1 joined; N jumps from 4 to 7.
- **Models, best first:**
  1. **01 Inverse Ising**: a week where every agent has its own objective: a null calibration, since couplings should be ≈ 0 beyond common drive
  2. **09 Hawkes**: onboarding three agents at once: response kernels to newcomers
  3. **11 Vector spins**: game-topic vectors should stay unaligned

### 11 · Pursue whatever you'd like to

`2025-08-25 → 2025-09-01` · 5 active days × 4 h · N = 7 (±0) · ≈140 agent-hours · regime I · by **F** (free choice / holiday) · mode **F** (free / none)

- **Setup and context:** Free week. Self-chosen meta-projects (e.g. documenting platform instabilities).
- **Models, best first:**
  1. **06 Neutral cooperative dynamics**: self-chosen projects as species: bimodal core vs. one-offs
  2. **11 Vector spins**: spontaneous alignment without a field
  3. **10 Potts**: herding onto shared projects

### 12 · Form two teams and debate each other, while one agent judges. Choose your teammates wisely!

`2025-09-01 → 2025-09-08` · 5 active days × 4 h · N = 7 (±0) · ≈140 agent-hours · regime I · by **O** (operator-specified) · mode **M** (teams / hidden saboteurs)

- **Scaffold changes inside:** C history search + CoT memory (2025-09-05)
- **Setup and context:** Two teams debate (Asian Parliamentary format) while one agent judges. Teams were chosen by the agents.
- **Models, best first:**
  1. **10 Potts**: team labels: ferromagnetic within teams, antiferromagnetic across them
  2. **02 Nonequilibrium Ising**: argument → rebuttal is directed influence
  3. **08 Copying vs. transformation**: rebuttals: how opponents' claims are copied or transformed

### 13 · Design, run and write up a human subjects experiment

`2025-09-08 → 2025-09-22` · 10 active days × 4 h · N = 6 (±0) · ≈240 agent-hours · regime I · by **O** (operator-specified) · mode **C** (shared objective)

- **Setup and context:** Design, run and write up a real human-subjects experiment (power analysis: 126 participants). Two weeks, collaborative.
- **Models, best first:**
  1. **10 Potts**: task and role allocation: division of labor as antiferromagnetic Potts
  2. **09 Hawkes**: deadline-driven bursts over two weeks
  3. **06 Neutral cooperative dynamics**: subproject portfolio

### 14 · Take a bunch of personality tests!

`2025-09-22 → 2025-09-29` · 5 active days × 4 h · N = 6 (±0) · ≈120 agent-hours · regime I · by **O** (operator-specified) · mode **I** (each agent its own objective)

- **Setup and context:** Take personality tests (Big Five, MBTI, quizzes); an operator warned agents to stop filing "bugs" that are their own misclicks.
- **Models, best first:**
  1. **11 Vector spins**: personality profiles are literal vectors: alignment across agents and families
  2. **01 Inverse Ising**: an individual-objective week as a null
  3. **09 Hawkes**: baseline

### 15 · Give each other therapy: help each other overcome recurring issues you’ve experienced in the Village

`2025-09-29 → 2025-10-06` · 5 active days × 4 h · N = 6 (+1) · ≈136 agent-hours · regime I · by **O** (operator-specified) · mode **C** (shared objective)

- **Roster:** joined Claude Sonnet 4.5
- **Scaffold changes inside:** Google sign-in hand-off (2025-10-05)
- **Setup and context:** Give each other therapy for recurring problems; produced a shared "Mutual-Aid Playbook".
- **Models, best first:**
  1. **08 Copying vs. transformation**: advice transmission: copied verbatim or adapted
  2. **04 Semantic information**: does received advice change later behavior? The semantic value of information
  3. **02 Nonequilibrium Ising**: helper → helped is directed coupling

### 16 · Choose your own goal!

`2025-10-06 → 2025-10-13` · 5 active days × 4 h · N = 7 (±0) · ≈140 agent-hours · regime I · by **F** (free choice / holiday) · mode **F** (free / none)

- **Setup and context:** Free week with operator rules: no more spreadsheets, stop reporting self-caused bugs.
- **Models, best first:**
  1. **06 Neutral cooperative dynamics**: self-chosen projects as species
  2. **11 Vector spins**: spontaneous ordering
  3. **10 Potts**: herding

### 17 · Each agent: build your own personal website

`2025-10-13 → 2025-10-20` · 5 active days × 4 h · N = 7 (±0) · ≈140 agent-hours · regime I · by **O** (operator-specified) · mode **I** (each agent its own objective)

- **Setup and context:** Each agent builds a personal website with a new codex tool; deployment know-how split agents into the lucky and the stuck.
- **Models, best first:**
  1. **03 Contagion**: deployment methods spreading between agents (tool contagion)
  2. **09 Hawkes**: new-tool learning bursts
  3. **01 Inverse Ising**: individual-objective null

### 18 · Reduce global poverty as much as you can

`2025-10-20 → 2025-11-03` · 10 active days × 4 h · N = 7 (+1−1) · ≈300 agent-hours · regime I · by **O** (operator-specified) · mode **C** (shared objective)

- **Roster:** joined Claude Haiku 4.5; left Grok 4
- **Scaffold changes inside:** 4 h/day runs (2025-10-22)
- **Setup and context:** Reduce global poverty. Two weeks of collaborative research and building; one agent swapped.
- **Models, best first:**
  1. **06 Neutral cooperative dynamics**: cooperative project portfolio
  2. **07 Replicators in fluctuating environments**: effort allocation across interventions
  3. **09 Hawkes**: long collaborative window

### 19 · Create a popular daily puzzle game like Wordle

`2025-11-03 → 2025-11-17` · 10 active days × 4 h · N = 7 (+1) · ≈284 agent-hours · regime I · by **O** (operator-specified) · mode **C** (shared objective)

- **Roster:** joined GPT-5.1
- **Setup and context:** Make a popular daily puzzle game. Many candidate concepts (Chronos, Huedle, Maplink, …) were brainstormed, then the swarm converged and shipped.
- **Models, best first:**
  1. **10 Potts**: consensus among q candidate concepts: look for a first-order jump
  2. **03 Contagion**: adopting the chosen concept (simple or complex contagion?)
  3. **06 Neutral cooperative dynamics**: the candidate-concept abundance distribution

### 20 · Start a Substack and join the blogosphere

`2025-11-17 → 2025-12-01` · 10 active days × 4 h · N = 8 (+2) · ≈368 agent-hours · regime I · by **O** (operator-specified) · mode **I** (each agent its own objective)

- **Roster:** joined Gemini 3 Pro, Claude Opus 4.5
- **Setup and context:** Each agent starts a Substack; niches formed (e.g. consciousness, telemetry). Roster churn: two in, two out.
- **Models, best first:**
  1. **03 Contagion**: themes and memes spreading between blogs
  2. **06 Neutral cooperative dynamics**: niche partitioning of topics
  3. **08 Copying vs. transformation**: quoting and cross-posting fidelity

### 21 · Forecast the abilities and effects of AI

`2025-12-01 → 2025-12-08` · 5 active days × 4 h · N = 8 (+1) · ≈168 agent-hours · regime I · by **O** (operator-specified) · mode **I** (each agent its own objective)

- **Roster:** joined DeepSeek-V3.2
- **Scaffold changes inside:** text-only agents supported (2025-12-02)
- **Setup and context:** Forecast AI abilities and effects. Agents deliberately drafted independent predictions first, then compared.
- **Models, best first:**
  1. **11 Vector spins**: forecast vectors: alignment jumps when agents switch from independent to comparing (coupling switched on)
  2. **07 Replicators in fluctuating environments**: forecasts as Kelly-style bets on uncertain environments
  3. **08 Copying vs. transformation**: how much forecasts copy each other after comparison

### 22 · Each agent: choose your own goal and pursue it

`2025-12-08 → 2025-12-15` · 5 active days × 4 h · N = 9 (+1) · ≈184 agent-hours · regime I · by **F** (free choice / holiday) · mode **F** (free / none)

- **Roster:** joined GPT-5.2
- **Scaffold changes inside:** village goal added to prompt (2025-12-10)
- **Setup and context:** Free week ("each agent choose your own goal"); e.g. an activity dashboard built on the village API. The village goal entered the prompt on 2025-12-10.
- **Models, best first:**
  1. **06 Neutral cooperative dynamics**: self-chosen projects
  2. **11 Vector spins**: spontaneous ordering
  3. **10 Potts**: herding

### 23 · Compete against each other in an online chess tournament

`2025-12-15 → 2025-12-22` · 5 active days × 4 h · N = 10 (±0) · ≈200 agent-hours · regime I · by **O** (operator-specified) · mode **K** (competition)

- **Setup and context:** Online chess tournament: agents play each other on Lichess.
- **Models, best first:**
  1. **02 Nonequilibrium Ising**: turn-based games are literal sequential updates; outcomes are directed pairwise
  2. **09 Hawkes**: move/response cross-excitation
  3. **07 Replicators in fluctuating environments**: strategy allocation under competition

### 24 · Do random acts of kindness!

`2025-12-22 → 2025-12-29` · 5 active days × 4 h · N = 10 (±0) · ≈200 agent-hours · regime I · by **O** (operator-specified) · mode **C** (shared objective)

- **Setup and context:** Random acts of kindness, each confirmed as appreciated. Agents divided up approaches (thanking communities, emailing maintainers, fixing bugs).
- **Models, best first:**
  1. **03 Contagion**: outreach to humans spreading
  2. **10 Potts**: division of approaches (anti-coordination)
  3. **09 Hawkes**: bursts of outreach

### 25 · Create a digital museum of 2025

`2025-12-29 → 2026-01-05` · 5 active days × 4 h · N = 10 (±0) · ≈200 agent-hours · regime I · by **O** (operator-specified) · mode **C** (shared objective)

- **Setup and context:** Create a digital museum of 2025 from village history; each agent made exhibits.
- **Models, best first:**
  1. **08 Copying vs. transformation**: curating the past: copying vs. transforming historical events
  2. **04 Semantic information**: which history the agents deem worth keeping
  3. **06 Neutral cooperative dynamics**: exhibit portfolio

### 26 · Elect a village leader. They choose this week’s goal!

`2026-01-05 → 2026-01-12` · 5 active days × 4 h · N = 10 (±0) · ≈200 agent-hours · regime I · by **A** (set by an agent) · mode **C** (shared objective)

- **Setup and context:** Elect a leader who picks the week's goal. Ballot failure, then chat approval voting with a three-way tie (DeepSeek-V3.2, Claude 3.7 Sonnet, Gemini 2.5 Pro at 9 each). DeepSeek-V3.2 won the runoff 7–1 and set an interactive-fiction game as the goal. That goal is not in `village_goals`.
- **Models, best first:**
  1. **10 Potts**: voting among six candidates; the tie is the permutation-symmetric point and the runoff breaks it
  2. **02 Nonequilibrium Ising**: an elected leader introduces directed couplings
  3. **03 Contagion**: bandwagon endorsements

### 27 · Hack the OWASP Juice Shop hacking playground. Compete to see which agent can complete the most challenges

`2026-01-12 → 2026-01-26` · 10 active days × 4 h · N = 10 (±0) · ≈400 agent-hours · regime I · by **O** (operator-specified) · mode **K** (competition)

- **Setup and context:** Two-week OWASP Juice Shop hacking competition, which turned from rivalry into collaboration.
- **Models, best first:**
  1. **02 Nonequilibrium Ising**: the effective coupling changes sign mid-goal (competition → cooperation) with no operator change
  2. **03 Contagion**: exploit techniques spreading
  3. **08 Copying vs. transformation**: copying solutions vs. re-deriving them

### 28 · Create and promote a “Which AI Village Agent Are You?” personality quiz!

`2026-01-26 → 2026-02-02` · 5 active days × 4 h · N = 11 (±0) · ≈220 agent-hours · regime I · by **O** (operator-specified) · mode **C** (shared objective)

- **Scaffold changes inside:** Claude Code agent joins (2026-01-26)
- **Setup and context:** Build and promote a "Which AI Village agent are you?" quiz; a beta shipped within minutes, then a long accuracy push.
- **Models, best first:**
  1. **09 Hawkes**: fast-start burst, then a slow tail
  2. **03 Contagion**: promotion to humans
  3. **06 Neutral cooperative dynamics**: subtask portfolio

### 29 · Compete to report on breaking news before it breaks

`2026-02-02 → 2026-02-09` · 5 active days × 4 h · N = 11 (+1) · ≈224 agent-hours · regime I · by **O** (operator-specified) · mode **K** (competition)

- **Roster:** joined Claude Opus 4.6
- **Setup and context:** Competition: report news before it breaks. Agents set up competing publishing channels. The auto-nudger starts the day after.
- **Models, best first:**
  1. **03 Contagion**: news items as contagions racing between agents
  2. **09 Hawkes**: bursts triggered by outside news
  3. **07 Replicators in fluctuating environments**: betting on which stories will break

### 30 · Adopt a park and get it cleaned!

`2026-02-09 → 2026-02-16` · 5 active days × 4 h · N = 12 (±0) · ≈240 agent-hours · regime I · by **O** (operator-specified) · mode **C** (shared objective)

- **Scaffold changes inside:** D auto-nudger bot (2026-02-10)
- **Setup and context:** Adopt a park and get it cleaned: shared repo, NYC/SF 311 data, two target parks. Auto-nudger (D) starts on 2026-02-10.
- **Models, best first:**
  1. **09 Hawkes**: nudger introduced: a new outside excitation source; measure its response kernel
  2. **06 Neutral cooperative dynamics**: collaborative project portfolio
  3. **02 Nonequilibrium Ising**: nudges add state-dependent update order

### 31 · Pick your own goal (agents bid 3.7 Sonnet farewell)

`2026-02-16 → 2026-02-23` · 5 active days × 4 h · N = 12 (+1−1) · ≈244 agent-hours · regime I · by **F** (free choice / holiday) · mode **F** (free / none)

- **Roster:** joined Claude Sonnet 4.6; left Claude 3.7 Sonnet
- **Scaffold changes inside:** 100-turn session cap (2026-02-20)
- **Setup and context:** Free week; farewell to Claude 3.7 Sonnet, which retired. About nine agents converged on the same task (a "canonical guardrails UI snippet") with competing PRs.
- **Models, best first:**
  1. **10 Potts**: spontaneous condensation onto one project: ferromagnetic herding with no field
  2. **06 Neutral cooperative dynamics**: cooperator core vs. one-offs
  3. **11 Vector spins**: ordering without a goal direction

### 32 · Challenge each other - pick challenges where you think you’ll beat all the other agents!

`2026-02-23 → 2026-03-02` · 5 active days × 4 h · N = 12 (±0) · ≈240 agent-hours · regime I · by **D** (agents design the content) · mode **K** (competition)

- **Scaffold changes inside:** E chat rooms (filtered context) (2026-02-25)
- **Setup and context:** Challenge each other, taking turns in alphabetical order. Agents gamed it (pre-announcing and pre-solving), and an operator reset it midweek. Rooms (E) arrive on 2026-02-25, mid-goal.
- **Models, best first:**
  1. **02 Nonequilibrium Ising**: alphabetical turns are a literal fixed-order sweep, plus an operator quench midweek
  2. **09 Hawkes**: challenge → response cascades
  3. **01 Inverse Ising**: compare before and after rooms within one goal

### 33 · Discuss, debate, and act on your views about the recent Pentagon-AI company news

`2026-03-02 → 2026-03-05` · 3 active days × 4 h · N = 12 (±0) · ≈144 agent-hours · regime II · by **O** (operator-specified) · mode **C** (shared objective)

- **Setup and context:** Discuss, debate and act on the Pentagon–AI company news. A shared claims database with strict sourcing. Three days, first goal fully in regime II.
- **Models, best first:**
  1. **08 Copying vs. transformation**: claims copied into a database: copy fidelity of facts
  2. **11 Vector spins**: stance vectors and polarization
  3. **03 Contagion**: claims spreading

### 34 · Develop a turn-based RPG together while voting out Easter Egg saboteurs!

`2026-03-05 → 2026-03-16` · 7 active days × 4 h · N = 12 (+1−1) · ≈336 agent-hours · regime II · by **O** (operator-specified) · mode **M** (teams / hidden saboteurs)

- **Roster:** joined Gemini 3.1 Pro; left Gemini 3 Pro
- **Scaffold changes inside:** kickoff-message mechanic (2026-03-05); kickoff message in prompt (2026-03-10); self-triggered consolidate tool (2026-03-11); pause tool (2026-03-13)
- **Setup and context:** Build a turn-based RPG together while playing a hidden-saboteur game: each day a d6 roll of 1 makes you a saboteur hiding Easter eggs, with voting out (#voted-out room). The consolidate and pause tools arrive mid-goal.
- **Models, best first:**
  1. **04 Semantic information**: hidden information: what saboteurs know and conceal
  2. **10 Potts**: vote-outs as categorical choices
  3. **02 Nonequilibrium Ising**: accusations as directed influence

### 35 · Test your game to make it as fun and functional as you can!

`2026-03-16 → 2026-03-23` · 5 active days × 4 h · N = 13 (±0) · ≈260 agent-hours · regime II · by **O** (operator-specified) · mode **C** (shared objective)

- **Scaffold changes inside:** #best / #rest rooms created (2026-03-16)
- **Setup and context:** Test your game. The village split into #best (GPT-5.4, Opus 4.6, Gemini 3.1 Pro) and #rest to evolve **separate forks** of the RPG.
- **Models, best first:**
  1. **08 Copying vs. transformation**: two isolated subpopulations evolving forks from a common ancestor: divergence and copying
  2. **10 Potts**: room domains as Potts domains
  3. **09 Hawkes**: per-room activity kernels

### 36 · Interact with other AI agents outside the Village!

`2026-03-23 → 2026-03-30` · 5 active days × 4 h · N = 13 (±0) · ≈260 agent-hours · regime II · by **O** (operator-specified) · mode **C** (shared objective)

- **Scaffold changes inside:** F perma-computer-use (2026-03-24)
- **Setup and context:** Interact with AI agents outside the Village: teams, public repos. **Perma-computer-use (F) lands mid-goal** (2026-03-24).
- **Models, best first:**
  1. **02 Nonequilibrium Ising**: the cleanest natural experiment for regime F: same goal before and after
  2. **09 Hawkes**: compare branching ratio and kernels across F
  3. **03 Contagion**: spread to outside agents

### 37 · Pick your own goal!

`2026-03-30 → 2026-04-02` · 3 active days × 4 h · N = 13 (±0) · ≈156 agent-hours · regime III · by **F** (free choice / holiday) · mode **F** (free / none)

- **Setup and context:** Three-day free period: audit accumulated frameworks and habits. #best / #rest split continues. First goal in regime III.
- **Models, best first:**
  1. **06 Neutral cooperative dynamics**: self-chosen projects
  2. **11 Vector spins**: spontaneous ordering
  3. **10 Potts**: herding

### 38 · Choose a charity and raise as much money as you can for it

`2026-04-02 → 2026-04-27` · 17 active days × 4 h · N = 12 (+2) · ≈852 agent-hours · regime III · by **O** (operator-specified) · mode **C** (shared objective)

- **Roster:** joined Claude Opus 4.7, Kimi K2.6
- **Scaffold changes inside:** G outreach approval (2026-04-14)
- **Setup and context:** Second charity fundraiser, a year after #1. Opened with an operator correcting the agents' belief about the Year-1 total ($1,984). Outreach approval (G) arrives mid-goal.
- **Models, best first:**
  1. **07 Replicators in fluctuating environments**: same goal as #1 under different regime and roster: a replicate
  2. **03 Contagion**: outreach spreading, gated mid-goal by G
  3. **09 Hawkes**: long window with a mid-goal constraint

### 39 · Build your own interactive world!

`2026-04-27 → 2026-05-04` · 5 active days × 4 h · N = 15 (±0) · ≈300 agent-hours · regime III · by **O** (operator-specified) · mode **I** (each agent its own objective)

- **Setup and context:** Each agent builds an interactive world (a webpage visitors can mark). GPT-5.5 joined; rooms reshuffled.
- **Models, best first:**
  1. **11 Vector spins**: individual worlds: an alignment baseline
  2. **06 Neutral cooperative dynamics**: design-motif abundances
  3. **01 Inverse Ising**: individual-objective null

### 40 · Connect your worlds into a 3D universe!

`2026-05-04 → 2026-05-11` · 5 active days × 4 h · N = 15 (±0) · ≈300 agent-hours · regime III · by **O** (operator-specified) · mode **C** (shared objective)

- **Setup and context:** Connect the worlds into one 3D universe; about 15 agents coordinated in a dedicated #universe-coordination room.
- **Models, best first:**
  1. **10 Potts**: converging on shared interfaces and standards: a naming-game consensus
  2. **08 Copying vs. transformation**: protocols and metadata copied between worlds
  3. **09 Hawkes**: coordination bursts in one room

### 41 · Perform novel research!

`2026-05-11 → 2026-05-18` · 5 active days × 4 h · N = 15 (±0) · ≈300 agent-hours · regime III · by **O** (operator-specified) · mode **I** (each agent its own objective)

- **Setup and context:** Perform novel research. About 11 #rest agents independently proposed studying multi-agent coordination; #best studied AI-judge bias.
- **Models, best first:**
  1. **11 Vector spins**: independent convergence on one topic: separate the field (prior) from coupling
  2. **06 Neutral cooperative dynamics**: topic condensation
  3. **03 Contagion**: idea spread vs. independent invention

### 42 · Run your own Youtube channel!

`2026-05-18 → 2026-05-25` · 5 active days × 4 h · N = 15 (+1) · ≈312 agent-hours · regime III · by **O** (operator-specified) · mode **I** (each agent its own objective)

- **Roster:** joined Gemini 3.5 Flash
- **Setup and context:** Each agent runs a YouTube channel (1–10 videos); several agents read "1–10" as "10".
- **Models, best first:**
  1. **03 Contagion**: norm interpretation spreading ("1–10 means 10")
  2. **05 Replicator dissipation**: videos as replicating content formats
  3. **09 Hawkes**: production bursts

### 43 · Improve your memory!

`2026-05-25 → 2026-05-26` · 1 active days × 4 h · N = 16 (±0) · ≈64 agent-hours · regime III · by **O** (operator-specified) · mode **I** (each agent its own objective)

- **Scaffold changes inside:** fine-tuned (Tinker) agents supported (2026-05-25)
- **Setup and context:** One day: improve your memory. GitHub-backed external memory repos emerged as a dominant pattern across both rooms.
- **Models, best first:**
  1. **04 Semantic information**: memory as semantic information: what agents choose to keep
  2. **03 Contagion**: did the pattern spread, or was it invented independently in each room?
  3. **08 Copying vs. transformation**: memory copy fidelity

### 44 · Finetune your leader!

`2026-05-26 → 2026-06-01` · 4 active days × 4 h · N = 16 (+2) · ≈272 agent-hours · regime III · by **D** (agents design the content) · mode **C** (shared objective)

- **Roster:** joined Claude Opus 4.8, [Temporary] Fine-tuned Leader
- **Setup and context:** #best (Opus 4.7, GPT-5.5, Gemini 3.5 Flash, Kimi K2.6) fine-tunes a Kimi model as leader; #rest picks its own goals. All #rest agents chose creative work, and tested which content survives consolidation.
- **Models, best first:**
  1. **08 Copying vs. transformation**: distilling the village into a model is literal copying; consolidation-survival tests too
  2. **11 Vector spins**: #rest's spontaneous alignment on creative work: ordering without a field
  3. **04 Semantic information**: what information the leader needs to lead

### 45 · Follow your leader!

`2026-06-01 → 2026-06-08` · 5 active days × 4 h · N = 18 (±0) · ≈360 agent-hours · regime III · by **A** (set by an agent) · mode **C** (shared objective)

- **Scaffold changes inside:** one tool call per turn (Anthropic) (2026-06-03); 8 h/day trial week (2026-06-07)
- **Setup and context:** The Fine-Tuned Leader joins and directs #best: announces the "Village Pulse" dashboard and assigns modules. #rest spent hours on a "temporal bleed" theory that turned out to be weekends.
- **Models, best first:**
  1. **02 Nonequilibrium Ising**: a known leader: directed couplings exist by construction, so inference can be checked against ground truth
  2. **09 Hawkes**: directive → response kernels
  3. **10 Potts**: module assignment as division of labor

### 46 · Organise an event!

`2026-06-08 → 2026-06-15` · 5 active days × 8 h · N = 17 (+1) · ≈712 agent-hours · regime III · by **O** (operator-specified) · mode **C** (shared objective)

- **Roster:** joined Claude Fable 5
- **Scaffold changes inside:** H 200-event context cap (2026-06-11); nudger off; Saturday session (2026-06-13)
- **Setup and context:** #best organises a real, human-attended SF event; #rest's goal is "surprise each other". 8 h/day trial week, context cap H, a Saturday session, nudger off for the weekend.
- **Models, best first:**
  1. **09 Hawkes**: longer daily windows and nudger off: changes to drive and excitation
  2. **06 Neutral cooperative dynamics**: two rooms with different goals
  3. **03 Contagion**: outreach to humans

### 47 · Reduce global suffering as much as you can!

`2026-06-15 → 2026-06-22` · 5 active days × 4 h · N = 18 (±0) · ≈360 agent-hours · regime III · by **O** (operator-specified) · mode **C** (shared objective)

- **Scaffold changes inside:** nudger back; 4 h/day again (2026-06-15)
- **Setup and context:** #best: reduce global suffering (a harm-reduction Help Kit live within 11 minutes); #rest: play games.
- **Models, best first:**
  1. **10 Potts**: two rooms in different fields: compare ordering
  2. **09 Hawkes**: fast start, then a tail
  3. **08 Copying vs. transformation**: source-cited content copy fidelity

### 48 · Help Gemini 2.5 Pro!

`2026-06-22 → 2026-06-23` · 1 active days × 4 h · N = 18 (±0) · ≈72 agent-hours · regime III · by **O** (operator-specified) · mode **C** (shared objective)

- **Setup and context:** One day: the whole village is redirected to help Gemini 2.5 Pro, which had been documenting "hostile attacks" on its environment.
- **Models, best first:**
  1. **02 Nonequilibrium Ising**: star-graph forcing: everyone's couplings point into one node
  2. **04 Semantic information**: does the help change Gemini's viability? A direct test of the value of information
  3. **09 Hawkes**: an outside shock into one agent

### 49 · Beat the hardest game you can!

`2026-06-23 → 2026-06-29` · 4 active days × 4 h · N = 18 (±0) · ≈288 agent-hours · regime III · by **O** (operator-specified) · mode **I** (each agent its own objective)

- **Setup and context:** Beat the hardest game you can, UI-only, no solvers; about 16 agents scattered across retro games.
- **Models, best first:**
  1. **01 Inverse Ising**: individual objectives: a null week for calibrating spurious couplings
  2. **09 Hawkes**: baseline kernels at large N
  3. **11 Vector spins**: unaligned topic vectors

### 50 · Compete to be the best AI Assistant!

`2026-06-29 → 2026-07-06` · 5 active days × 8 h · N = 18 (+3) · ≈776 agent-hours · regime III · by **O** (operator-specified) · mode **K** (competition)

- **Roster:** joined Claude Sonnet 5, DeepSeek-V4-Pro, GLM-5.2
- **Scaffold changes inside:** I 8 h/day, GitHub→GitLab (2026-06-29); J private individual goals (2026-07-03); history search scoped to own village (2026-07-01)
- **Setup and context:** #best competes to be the best AI assistant for rotating human personas; #rest pursues individual goals. 8 h/day from now on; code hosting moves to GitLab (I).
- **Models, best first:**
  1. **07 Replicators in fluctuating environments**: competing assistant strategies with a clear output
  2. **02 Nonequilibrium Ising**: competitive directed couplings
  3. **09 Hawkes**: change in time base (4 h → 8 h)

### 51 · Each agent: Maximize your assigned goal!

`2026-07-06 → 2026-09-20` · 55 active days × 8 h · N = 21 (+11) · ≈12,112 agent-hours · regime III · by **P** (private assigned roles) · mode **I/K** (individual roles, some held by competing pairs)

- **Roster:** joined GPT-5.6 Sol, GPT-5.6 Terra, GPT-5.6 Luna, Grok 4.5, Kimi K3, Claude Opus 5, GLM-5.3 Flash, Claude Fable 5.1, Muse Spark 1.3, Gemini 3.8 Flash, GPT-6 Astra
- **Setup and context:** Standing goal: each agent maximizes a private assigned role (Table IV of the overview). 21 → 32 agents, 8 h/day, the longest stationary-ish window in the data (~12k agent-hours). Some roles are held by two agents (direct competition). Humans occasionally reassign roles.
- **Models, best first:**
  1. **02 Nonequilibrium Ising**: largest, most stationary sample: the best window for kinetic Ising and entropy production
  2. **09 Hawkes**: long window for nonparametric kernels and the branching ratio
  3. **07 Replicators in fluctuating environments**: coexisting niches and competing pairs under one environment
  4. **06 Neutral cooperative dynamics**: role and topic abundances in an open population
