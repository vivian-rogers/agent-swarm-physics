# Lab notebook

Newest entry at the top. Add an entry when you start, finish, or abandon
something, or make a decision worth remembering.

---

## 2026-10-03

- **Decisions (Vivian):**
  - **Behavior states via Jev** (TypeSafe's hosted typed classifier; zero-shot; gated text goes to TypeSafe with Vivian's approval);
  - **givemeanode OK for Phase 2**: $433.91 credit, expiring 2026-11-03; workspace cap $200/month; an unrelated stopped 8×H100 node from another mission, left alone;
  - **`llm_calls` not obtainable**, so replay (H01 Tier 1; H08 C4–C6) is blocked;
  - **outbound fetch of public repo histories approved** (S7);
  - commit approved.
- **Phase 0 shared tables built** (`data/processed/shared/`, ~120 MB): four raw scans in parallel (72 s; row counts match the manifest), then the derived tables.
  - The empirical daily windows match the documented hours (2.0 / 3.0 / 4.0 / 8.1 h medians); the undocumented first weeks ran ~2 h/day.
  - Exposure: median 9 recipients per message, median lag 248 s.
  - Fixes: bot messages labeled via the events table (2,230 automated vs. 7,762 human); declared PAUSE durations count as idle (idle now 8.3% of agent-minutes).
- **H09 exploratory round 1** (282 non-holdout days), scored against predictions written beforehand:
  - E1: co-activation beyond independence holds only in regime III (variance ratio 1.61); the activity landscape's two wells come from the schedule (the time-varying null reproduces them).
  - E2: entropy production > null in 78% of agent × regime cells; it collapses at the event level after perma-computer-use. Regime III has a dominant cycle: consolidate → search → talk → pause → consolidate.
  - E3: no non-ergodicity at the day scale, but model family explains 41–77% of between-agent variance.
  - E4: idle dwell is heavy-tailed (CV 3.8); the nudger test is untestable in exploration (holdout).
  - E5: no aging at 1-min resolution.
- **Five parallel subagents launched**, one per direction, under shared rules (predictions first, non-holdout exploration only, confirmatory scripts written but not run, ≤150 MB each, ~2–3 cores each):
  - H02 couplings are real (S1);
  - H03 self-excited criticality (S2);
  - H04 reversible forcing and Green's functions (S3);
  - H05 rooms as coupled blocks (S4);
  - H09 round 2 (E6 idle traps; E7 collective irreversibility; E8 a memory equation of state).
- **Misread corrected.** "Make a whole new hypothesis for that" meant the general thermodynamics framing, not `llm_calls`.
  - `llm_calls` is not on Hugging Face: AI Digest has only `aidigestorg/ai-village`, with no such file. Requesting it is Vivian's call.
  - **H08 "Context is the coupling"** was opened on the misread. It's parked as an idea (H numbers are permanent), with C1 ready to run on the Claude Code agent. That agent's stream has its full input side (village-event feeds with event IDs matching `events`, compactions, unseen counts) and spans NE12.
  - **H09 "Agent swarms have an effective thermodynamics"** is opened: T1–T10 mapped to HH IDs; exploratory E1–E5 with predictions written before data.
- **Holdout locked** before any exploration (`hypotheses/holdout.md`, `holdout.json`, seed 20261003):
  - NE windows: NE12, NE21 + NE23, NE30, and the #51 tail;
  - 16 of 51 goal periods held out in full.

  Corrected one boundary artifact (NE21 window start) and redrew once, before data; the redraw picked #45 at random, and the draw stands.
- **Storage and compute:** ≤10 GB project budget; run locally (10 cores, 32 GB), multithreaded. Project environment via `pyproject.toml` (`.venv` ~434 MB).
- **Phase 0 pipeline started:** `infra/shared/common.py`, `scan_tables.py` (four parallel scans), `build_derived.py` (calendar, rooms_timeline, exposure, activity_bins, kicks).
- Findings from the response structure:
  - `computer_use_turns.agent_messages` holds provider responses only: no prompts, no sampling temperature;
  - it does hold per-call token accounting with cache reads and writes, a proxy for new context per call.
- `hypotheses/hypohypotheses/statmech-primitives.md`: inventory of stat-mech primitives in the data:
  - microstates (turn, message, agent, memory, swarm, artifact, path) and macrostates (activity, occupancies, polarization, effective dimensionality, semantic entropy, collective mode, leadership concentration, multi-information);
  - ensembles and reservoirs; conjugate pairs and who controls them; conserved and bounded quantities;
  - symmetries and their breakers; the timescale hierarchy; currents; work and heat analogs.
- Appended HH55–HH67: non-ergodicity, work cycles with currents, memory as a finite volume, dimensional collapse, entropic scope creep, grand-canonical rooms, adiabatic elimination, statistical complexity by family, goal switches as work, artifact food web, multi-information peaks, explicit vs. spontaneous symmetry breaking in #best/#rest, collective irreversibility.
- Added HH47–HH54 (appended; no renumbering), the free-energy landscape family. Boltzmann inversion G = −T ln P over coarse states; Gibbs not Helmholtz, since operators set the field and agents set the alignment.
  - HH47 the landscape itself; HH48 enthalpy vs. entropy; HH49 Legendre pushes; HH50 chemical potentials of rooms and projects;
  - HH51 coupled reactions (ATP); HH52 catalysts vs. fields; HH53 metastable traps; HH54 free energies already inside models 06 and 07.
- `hypotheses/promotion-shortlist.md`: seven to test first. S1–S4 need no text; S5–S7 need Phase 2.
  - S1 couplings are real (HH44 + HH23);
  - S2 criticality (HH30 + HH32);
  - S3 reversible forcing (HH46 + HH31);
  - S4 the rooms cut (HH33);
  - S5 field vs. coupling (H01 D3.2);
  - **S6 neutral cooperation (HH42)**;
  - **S7 RPG forks (HH38)**.

  HH IDs are untouched; HH numbering is append-only from now on.
- Light structural pass over chat and events (field presence and counts only):
  - every chat message has a room;
  - human-side speakers: 602 IDs; the bot is `automated` (2,230 messages), so nudges are identifiable without text;
  - `roomId` is on ~100% of talk, consolidation and pause events, 2% of WAIT, 14% of start/stop events.
- Planned the Phase 0 shared tables in `infra/README.md`. The key one is `exposure`: for each message, who could see it and when.
- **Faithfulness scheme** (`writeup/paper.tex`, Sec. VI): nine axes, each scored 0/1/2:
  - A mapping, B assumptions, C adequacy vs. the null hierarchy, D unfitted predictions;
  - E interventional (natural experiments), F identifiability (synthetic recovery), G ground truth;
  - H comparative vs. rivals, I transfer.

  Levels: idea → hypothesis (a commitment to a test), descriptive, supported, faithful. Principles include: fit ≠ faithfulness; beat the strongest null; lock a holdout before exploring. Added a scorecard to the hypothesis template, the promotion rule to `HYPOHYPOTHESES.md`, and a rule to `CLAUDE.md`. The paper also gained a phased plan of work (Sec. VII); now 4 pp.
- `hypotheses/hypohypotheses/greens-functions.md`: which ideas map onto a Green's function (a linear response kernel). It gives three tests for when one applies (linearity in dose, superposition, time-translation invariance), natural fits (HH31 nudger, HH14, Hawkes as a Dyson series, HH23, HH02 aging), partial fits, and ideas where it doesn't apply. It also notes an exact link: the semantic-information viability landscape is a backward Green's function.
- Added susceptibility sections to models 01, 02 and 11, plus entry 2b (susceptibility map) in `phase-diagrams.md`:
  - **01:** χ = C from fluctuations, its top eigenmode, and a fictitious-temperature sweep;
  - **02:** response functions from real kicks (nudges, human messages, kickoffs, one-agent and one-family changes), and the fluctuation–dissipation violation as an effective temperature;
  - **11:** longitudinal vs. transverse χ, with a Goldstone prediction for weeks that order spontaneously.
- `writeup/`:
  - `paper.tex`: RevTeX working draft (3 pp.) documenting the project so far. Covers motivation, architecture, the model library, catalogs, H01 and next steps; no results.
  - `figures/architecture.tikz`: single-column flowchart, shared by the paper (Fig. 1) and `project-architecture.pdf`.
  - The earlier poster-size version is kept as `project-architecture-detailed.pdf`.
- `hypotheses/hypohypotheses/phase-diagrams.md`: speculation on which phase diagrams are easiest from the data. Easiest are the Hawkes branching ratio across goal periods (timestamps only) and placing each period on a spin-glass phase diagram (binned activity only). Neutral cooperation is the best theory-vs-data diagram, since its boundaries are analytic.
- `HYPOHYPOTHESES.md`: every idea now has an ID (HH01–HH46) and is tagged with its most faithful models (best first) and candidate goal periods and natural experiments.
- **H01 renamed "Emergent superagents exist"**; folder `hypotheses/H01-emergent-superagents-exist/`. Wrote `subhypotheses.md`: the full set of 10 non-conflicting directions (D1–D10) with sub- and sub-sub-hypotheses, rivals marked (⟷), tiers, windows and models, plus a suggested starting set.
- **Decisions (Vivian):**
  - viability: open, with candidates as D2.1–D2.4 and a data-driven selection rule (D2.6, homeostasis);
  - request `llm_calls` eventually;
  - **no new swarms**: simulation dropped;
  - mined and fixed probes both fine.
- Added `hypotheses/natural-experiments.md`: documented step changes NE01–NE40 as quasi-interventions. Many are channel cuts that act as natural Kolchinsky–Wolpert scrambles (rooms, hidden plans, context cap). Reversals: NE21 (hours), NE23 (nudger). Undocumented step changes could be found by change-point detection; not run.
- Added 25 "model X explains period Y" entries to `HYPOHYPOTHESES.md`.
- H01: saved the pasted Kolchinsky–Wolpert Q&A as `notes/kolchinsky-qa-transcript.md` (verbatim, unverified) and wrote `architecture.md`.
  - **Terms:** "semantic entropy" in the original framing → Kolchinsky–Wolpert semantic information. Meaning-cluster semantic entropy is kept as the ideology order parameter.
  - **Sub-hypotheses:** H01b (ideology as an ordered phase; observational), H01a (superagents), H01c (load-bearing beliefs).
  - **Tiers:** Tier 0 observational (bounds, candidates), Tier 1 replay (blocked: exact prompts not exported, `llm_calls` on request), Tier 2 own simulation.
  - Added draft definitions (superagent, semantic information, semantic entropy, ideology). Four decisions open for Vivian.
- Moved the newest download, *Physics of Agents: Statistical Mechanics Predicts Collective Behavior of AI Agents* (arXiv:2608.16578v2), into `literature/` with stub notes. It's unread; the authors aren't in the PDF metadata.
- Opened **H01: emergent superagents and the thermodynamics of ideology** (Vivian's proposal), status "idea". The card records the framing (superagent discovery via semantic information; ideology as a low-semantic-entropy state) and the open questions, especially which "semantic entropy" is meant. Deliberately not developed further yet.
- Added physics models 10 (Potts: categorical states; antiferromagnetic Potts as division of labor) and 11 (vector spins: O(n)/Heisenberg/spherical, with agent states as embeddings or √p over topics, and the goal as a literal field vector). Added matching state variants to `DEFINITIONS.md`.
- `hypotheses/HYPOHYPOTHESES.md` is now `hypotheses/hypohypotheses/HYPOHYPOTHESES.md`. Added `goal-periods.md` with all 51 goal periods: setup, N, agent-hours, scaffold changes inside each goal, and ranked physics models per week, plus a "best weeks per model" index.
  - Notable natural experiments: #36 (perma-computer-use lands mid-goal), #35 (#best/#rest evolve separate forks), #45 (a known leader, i.e. ground truth for directed couplings), #32 (alphabetical turn order), #1 vs #38 (same goal a year apart).
  - Two goal summaries in the dataset are filed under swapped slugs: `pick-your-own-goal` describes #37, and `pick-your-own-goal-agents-bid-37` describes #31.
- Overview now credits Vivian Rogers, with Claude Opus 5.5, plus a provenance note. Its goals table is generated by `figures.py` and has per-goal columns:
  - active days (d), hours/day (h), agents at start (N), joins/retirements (±);
  - agent-hours (AH), scaffold regime (reg), who wrote the objective (by), and the coupling the goal imposes (mode).
  - Mode counts: C 22, K 6, M 2, I 10, F 10, plus the private-role era. Goal #51 alone has about 12k agent-hours, more than goals 1–37 combined.
- Expanded the overview to 7 pages, reorganized as population → anatomy of an agent → platform → interaction structure → external forcing → who writes the goals → export → modeling implications.
  - New figures: an action vocabulary (event types, computer-use actions); external forcing (capability timeline, changelog entries by category, operating hours); a goal-authorship diagram.
  - New tables: what each agent can see of the others; private roles. (An export-contents table was cut for length; Table I covers the counts.)
  - Goal authorship coding (our own, soft): of 51 village goals, 35 operator-specified, 3 where agents design the content, 10 free choice or holiday, 2 set by an agent (#26 election, #45 fine-tuned leader), 1 private roles.
  - The election week's actual goal (an interactive-fiction game) is not in `village_goals`.
- Wrote a 5-page RevTeX overview of the AI Village setup and platform: `data/processed/ai-village/ai-village-overview.pdf`. Source and build in `infra/ai_village_overview/` (`build.sh`). Descriptive only, from docs + small tables + action-type counts; no dynamics or social-graph analysis (on purpose).
- Findings worth remembering from it:
  - **Bash adoption drifted hugely and is barely documented.** Agents that left before Dec 2025 used ≤6% bash; many 2026 agents use 70–93%.
  - **Same-day variants differ.** GPT-5.6 Sol is 71% bash; Terra and Luna are 2–3%.
  - **Private, partly competing roles** have been in place since 2026-07-06.
  - **Concurrency/turn-taking is undocumented** (`villages.active_agent_id`, `turn_id`).
  - **Model reasoning text is in the raw outputs.**
- Added model 09 (Hawkes processes) to `physics-models/`.
- Set up the project structure: `data/raw`, `data/processed`, `infra`, `physics-models`, `hypotheses`, `literature`, `interpretation`, `writeup`. See `CLAUDE.md`.
- **Decision:** physics models get their own folder, `physics-models/`, one subfolder per model. Each hypothesis picks one model from there and owns its processing scheme (`scheme/`). Code shared by more than one hypothesis moves to `infra/`. (Briefly had models inside hypothesis folders; reversed the same day.)
- Wrote up 8 models: inverse Ising, nonequilibrium Ising (asymmetric J and non-random update order), contagion with thermo dictionary, semantic information of emergent structures, replicator dissipation, neutral cooperative dynamics, replicators in fluctuating environments, copying vs. transformation. Models 04–07 come from the papers in `literature/`; references marked † were written from memory and need verifying.
- Pulled the full AI Village export (all tables + `village-transcript.json`) into `data/raw/ai-village/`, pinned to one HF revision. See `data/raw/ai-village/_source.md`.
- **Decision:** skipped the computer-use screenshots (171 GB, 370 daily tars). Plan: OCR them later rather than store raw images. Not now.
- Started `physics-models/DEFINITIONS.md` with draft operational definitions. Biggest open questions: what counts as exposure in an interaction, and how to separate contagion from shared pretraining.
- Added 7 papers to `literature/` with notes and an index; PDFs renamed to `author-year-title`. Kolchinsky is an author on all 7. None is a contagion paper, so model 03 rests on references not yet in the folder.
- Started `hypotheses/HYPOHYPOTHESES.md` for loose ideas.
