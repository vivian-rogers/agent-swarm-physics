# H07: The RPG forks diverge from a common ancestor at a measurable rate

**Status:** running; round 1b done 2026-10-04 (no verdict changes; natives: leakage is read-bounded, a second fork family re-converges through its upstream, nucleation is a trait not a role). Results are organized by goal period (see "Results by goal period"). Exploratory round 1 (non-holdout: #35 onward) done 2026-10-03: divergence is **gradual and measurable** at file and function level, **punctuated** for content (names, numbers), the two forks mutate content at very different team-specific rates, and the few shared innovations look like **convergent repair of inherited defects, not leakage**. Confirmatory test on the held-out #34 lineage written (`analysis/confirm_h34.py`), dry-run on non-holdout stand-ins, **not run**.
**Fields:** info theory, dynamics, sociophysics
**Literature:** Kolchinsky & Corominas-Murtra 2020 (copy vs. transformation; PDF not in `literature/`, see the caveat under Observables); Eigen 1971 (error threshold); Griffiths & Kalish 2007 (iterated learning). All cited via `physics-models/08-copying-vs-transformation/README.md`.
**Origin:** shortlist S7 ([`../promotion-shortlist.md`](../promotion-shortlist.md)); idea HH38; goal periods #34 (held out) and #35; NE15 (the split).
**Definitions used** (`physics-models/DEFINITIONS.md`): Regime; Population; Activity time. Proposed here, to be added to DEFINITIONS.md by whoever owns that file: **"copy information (fork variant)"** (Observables 2) and **"lineage"** (Data scheme).

## Question
On 2026-03-16 the village was split into #best (GPT-5.4, Claude Opus 4.6, Gemini 3.1 Pro) and #rest (everyone else), and each room took its own copy of the RPG that all twelve agents had built during #34. Two isolated subpopulations then evolved two copies of one artifact. How fast, and in which features, do the copies diverge from the common ancestor and from each other? Is the divergence gradual (an inheritance curve with a measurable mutation rate), and does anything cross between the rooms?

## Model
**From:** `physics-models/08-copying-vs-transformation/` (primary); `10-potts` (rooms as domains) and `09-hawkes` (per-fork commit kernels) as secondary (not fitted in round 1).
- **Channel.** A keyed feature (a file path, a numeric parameter at a code path, a named game entity) has value x in the ancestor and value y in a descendant snapshot. The ensemble of keys defines p(x, y). Two channels: **vertical** (ancestor → lineage k at time t) and **horizontal** (#best(t) ↔ #rest(t), same key).
- **Decomposition.** I(X;Y) = I_copy + I_transform. Copy information counts y = x beyond chance; transformation information counts systematic rewriting (e.g. every `hp: 100` becoming `hp: 120`).
- **Mutation-clock variant (this card).** Each key mutates independently with a hazard μ per unit of a clock (active hour, commit, or file-touch). Ancestor → fork copy fraction c_k(t) = exp(−μ_k τ_k(t)) for a homogeneous key population, or a two-class mixture (a "hot" fraction that mutates, a "frozen core" that is never touched). With **no leakage and no convergent edits**, a key is identical across the forks only if both kept the ancestor value, so horizontal identity is bounded by P(both unchanged), and identical *new* values in both forks should be ≈ 0.

## Data scheme (`scheme/`)
- **Inputs:**
  - shared tables: `rooms_timeline`, `roster`, `calendar`, `chat_core`, `rooms`; the new shared **`artifacts`** / **`artifact_mentions`** tables (built for this card by `infra/shared/build_artifacts.py`; schema in the final report of 2026-10-03 and the module docstring);
  - the public GitHub repositories of the RPG and its forks (fetched read-only, approved 2026-10-03), as bare partial clones in `data/raw/repos/` (5.8 MB, gitignored; see `data/raw/repos/_source.md`);
  - raw `events` (SEARCH_HISTORY between T0 and 2026-05-01 only), for leakage.
- **Lineages.** Identified from the artifacts table (chat URLs during #35): `ai-village-agents/rpg-game` (the ancestor repo, lineage `origin` after T0), `rpg-game-best`, `rpg-game-rest`, `rpg-game-rest-week` (a second #rest copy that received one README commit). A *lineage* is one repository's default-branch history restricted to commits after the fork point A (`A..main`).
- **Fork instant and ancestor.** T0 = 2026-03-16 16:20:05 UTC (#35 kickoff). A = `abc7c37` = the newest `rpg-game/main` commit contained in every fork's main (found from commit-ID sets only) = `rpg-game/main` at T0 (last commit 2026-03-13 20:29 UTC, end of the last pre-split session). The #best lineage additionally contains 7 commits the three #best agents made on `rpg-game` itself on 03-16 (17:12–18:34 UTC) before moving to `rpg-game-best`. **No commit, author or message before T0 is analyzed**: every git call is restricted to `A..main`; 0 commits in `A..main` predate T0; 0 fall on held-out days.
- **Transform:**
  - `scheme/build_lineages.py`: commits (author → agent via the `<agent-slug>@agentvillage.org` email; room at commit time), files touched (non-merge), the tree at A and at every first-parent commit (with cumulative non-merge commits, file-touches by exact ancestry, and active hours from `calendar` windows), main state at the end of each PT day.
  - `scheme/extract_features.py` (tree-sitter JavaScript; 1,345 `src/**/*.js` blobs, 6 with recoverable parse errors): per blob, **numbers** keyed by code path (declarator / class / function / object keys / array element labelled `[id=..]` or `[name=..]` when available, else index; occurrence index), flagged `data` when the literal sits directly in a pair, array or declarator (= "numeric parameters"); **function bodies** keyed by qualified name (value = hash of whitespace-collapsed body); declared **identifiers** (set); **content names** (`name`/`title`/`displayName`/`label` string values; keyed by object path, and as a set); **entities** (objects with both `id`/`key` and `name`: id → name). Files: key = path, value = blob id (all files; also src and tests separately).
  - `scheme/search_history.py`: the 633 history searches between T0 and 05-01 (query ≤ 300 chars; flags for mentions of the RPG and of either fork in query or answer).
- **Output:** `data/processed/H07-rpg-forks/` (1.1 MB): `commits`, `commit_files`, `fp_trees`, `day_snapshots`, `blob_{numbers,functions,idents,names,entities,meta}`, `search_history_text`, and from `analysis/`: `curves_commit`, `curves_day`, `horizontal_day`, `clock_fits`, `shared_innovations`, `leakage`, `results.json`, `leakage_summary.json`, `_provenance.json`. Figures: `NE15/figures/`, `G35/figures/`.
- **Regimes covered:** regime II (#35, 03-16 → 03-23) and regime III (#36 → last fork commit 05-28; non-holdout days only). Nearly all activity (357 of 405 non-merge fork commits) is in #35, so results are effectively regime II.

## Observables
1. **Copy fraction** c(t) = P(Y = X) over ancestor keys, per lineage and feature type; chance-corrected version κ = (c − Σ_x p_X(x) p_Y(x)) / (1 − Σ_x p_X(x) p_Y(x)). For set-valued features (identifiers, distinct names): survival = |S_A ∩ S_t| / |S_A|.
2. **Copy and transformation information** per feature type vs. days (active hours, commits) since the split. Our reading of Kolchinsky & Corominas-Murtra: I_copy = Σ_x p(x) · d(p(Y=x|X=x) ‖ p_Y(x)) · 1[p(Y=x|X=x) > p_Y(x)], with d the binary KL divergence; I_transform = I(X;Y) − I_copy ≥ 0 (data processing). **Caveat:** this definition could not be checked against the paper (PDF not available); it is used as a documented proxy, alongside κ, which does not depend on it. Plug-in estimates are biased for large alphabets, so every I is reported minus a shuffle null (Y permuted across keys; 100 draws). *Added during round 1:* a **conditional null** for I_transform (copied pairs kept, outputs permuted among changed keys present in both), because under strong copying the plain shuffle null over-corrects and makes I_transform negative; plus the share of changed values that follow an (x → y) mapping shared with another key.
3. **Mutation rates** μ per lineage and feature type, against three clocks: active hours, commits, file-touches; the frozen-core fraction from a two-class fit.
4. **Horizontal identity** between #best and #rest: P(same value at key), compared with P(both unchanged); count of **shared innovations** (identical new values or new names in both forks that are absent from the ancestor).
5. **Leakage events:** agents moving between rooms (`rooms_timeline`), commits or pushes to the other room's repository (git authorship, and git commands in the artifacts table), history searches mentioning the other fork, chat mentions of the other fork's URL.

## Null / baseline
- **No divergence:** forks identical to the ancestor (c = 1).
- **Total divergence at once:** a rewrite or reset (c drops to ≈ 0 in one commit).
- **Shuffle null** for information estimates (Y permuted across keys); **conditional null** for transformation (see Observables 2).
- **Independent lineages:** horizontal identity = P(both unchanged), no shared innovations beyond convergent edits; convergent edits estimated from shared innovations between the two #rest copies vs. between #best and #rest (not usable: rest-week never evolved).
- **Clock null:** divergence tracks active time equally well as it tracks commits.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** model-08 seed "numbers are copied, ideas are transformed" (rival to P2); wall-clock divergence (rival to P3); leakage-driven convergence (rival to P5).
**Locked holdout used for confirmation:** #34 (the ancestor's own build lineage, 2026-03-05 → 03-16) and the NE30 window that covers it. Script: `analysis/confirm_h34.py` (written, dry-run on stand-ins, not run).

Scored for round 1 (exploratory, non-holdout), mapping = git trees + tree-sitter keyed features, #35 onward.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Lineages, authorship (99% email → agent) and keyed features defined from git objects; assumptions and key-alignment failure modes listed (Caveats). Keyed features break on restructuring (best `items.js`, 03-19), bounded by set-level measures. Not tested across model families. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Homogeneous-hazard assumption audited and **rejected**: 66 inherited files changed in both forks vs. 27.6 expected under independence (2.4×), i.e. persistent hot spots. Content mutation is punctuated (59–77% of name/number divergence in one commit), not a constant hazard. No stationarity test across days. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Copy information far above the shuffle null for every feature (e.g. horizontal files 4.75 bits at end of #35); horizontal identity on ancestor keys equals P(both unchanged) exactly (independent-lineage null holds). No day-blocked held-out prediction. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | P1, P4 (monotone decline), P7 and the independent-lineage identity held; P3a (per-commit clock) and P6 failed. The touch clock collapsing the forks (μ ratio 1.0–1.2) is post hoc. |
| E interventional | predicts the change across a natural experiment | 1 | Sign and rough size of the post-split divergence predicted (P1); no model fitted before the split (that needs #34, held out). |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 0 | No synthetic recovery. Partial robustness only (keyed vs. set measures; plain vs. conditional null). |
| G ground truth | agrees with known structure | 1 | Commits match the room assignment (best 193/196, rest 241/242 by own-team agents); the lineages' common history ends at the last pre-split session. This validates the mapping, not the copy model. Round 1b: 99.4% / 100% on DQ6 `room_assignment` in #35; every cross-fork commit followed a ledger read of the target fork; DQ6 lead designers do not predict who nucleates content. |
| H comparative | beats the named rivals | 1 | Model-08 seed rival (numbers most conserved) not supported; wall clock not beaten by commit clock (beaten by touch clock, post hoc); leakage rival not supported (shared innovations precede any channel). No likelihood comparison. |
| I transfer | holds in other same-mode periods, including the holdout | 1 | Round 1: not tested (one split; NE32 involves no shared artifact; #34 confirmation not run). **Round 1b (0 → 1):** the independent-lineage test transferred to a second fork family (`agent-papers`, #36) and flagged its channel (upstream syncs: identity excess 0.30, 29/29 shared files upstream-first). One event; holdout not run. |

## Prediction
*Written 2026-10-03, before any repository history was fetched or any fork feature computed. Known at this point: the four repository names (from #35 chat URLs), their GitHub creation and last-push dates (API metadata: forks created 03-16 17:02–17:03 UTC; last pushes 04-03 for best and rest-week, 05-28 for rest, 04-03 for the ancestor repo), and room membership from `rooms_timeline` (#best = GPT-5.4, Opus 4.6, Gemini 3.1 Pro; Haiku 4.5 appears in #best from 03-19 20:46 to 03-20 17:14 UTC; most agents show short #general intervals near the end of 03-19 and 03-20).*

"End of #35" = the last snapshot before 2026-03-23 11:17 UTC. "Main forks" = rpg-game-best and rpg-game-rest.

- **P1 (gradual divergence, neither extreme).** At the end of #35, each main fork's file copy fraction is in [0.2, 0.9]; identifier survival ≥ 0.8; content-name survival ≥ 0.85; numeric-parameter copy fraction ≥ 0.7. No single commit accounts for more than half of a fork's file-level divergence at the end of #35. *Falsifier:* c_files > 0.97 (no divergence) or < 0.1, or one commit carrying > 50% of the divergence (total divergence at once).
- **P2 (feature hierarchy).** Chance-corrected copy fraction at the end of #35: content names ≥ identifiers ≥ numeric parameters > file contents, in both main forks. This is the rival of the model-08 seed ("numbers are copied"): the goal ("make it fun and functional") invites balance tuning, so numbers should be *less* conserved than names. *Falsifier:* numeric parameters more conserved than identifiers in both forks.
- **P3 (commit clock and frozen core).** (a) Divergence is better described against cumulative commits (or file-touches) than against active hours: the per-commit mutation rates of the two main forks agree within a factor of 2, and agree more closely than their per-active-hour rates. (b) The file copy curve saturates: a frozen core of ≥ 30% of ancestor files is untouched in both main forks at the end of #35, and a two-class (hot + frozen) fit beats a single exponential.
- **P4 (horizontal decay, then freeze).** Horizontal copy information I_copy(best; rest), shuffle-corrected, falls monotonically (day by day) through #35, and changes by < 10% of its #35 drop over all later periods combined, because commit activity collapses (≥ 80% fewer commits per active day) once the goal changes on 03-23.
- **P5 (leakage is rare and channel-attributable).** ≤ 5 shared innovations between #best and #rest (identical new file contents or new content names in both forks), each traceable to a cross-room channel: a room move (Haiku 4.5 in #best on 03-19/20; the #general intervals), a cross-room push, a history search or a chat link. ≤ 2 post-split commits on either main fork by an agent of the other room. Shared innovations between #best and #rest are fewer than between the two #rest copies (rest vs. rest-week).
- **P6 (population size).** #rest makes ≥ 1.5× as many commits as #best during #35, and diverges further from the ancestor by the end of #35 (lower file copy fraction).
- **P7 (copying, not transformation).** For every keyed feature type, shuffle-corrected I_transform ≤ 0.1 × I_copy in each main fork at the end of #35: changes are idiosyncratic, not systematic re-mappings. The possible exception is numeric parameters, if a fork rescaled stats globally.
- **P8 (ground truth, axis G).** ≥ 90% of post-split commits on each main fork are by agents of the matching room, and the forks' common history ends within 2 h of T0.

## Confirmatory predictions (held-out #34)
*Written 2026-10-03, after exploratory round 1 and before any #34 commit, author, message or file list was read. Script: `analysis/confirm_h34.py --i-am-confirming` (not run; the default mode is a dry run on #35 stand-ins).*
- **C1 (persistent hot spots).** Per-file touch counts on `rpg-game/main` during #34 (non-merge commits; files present in A) predict which ancestor files were changed in **both** forks by the end of #35: AUC ≥ 0.65; the top quartile of #34 touches (tie-averaged ranks) has ≥ 2× the both-changed rate of the bottom half; the co-change excess (2.4× for all files in exploration) falls to ≤ 1.5 when the independence expectation is computed within #34-touch quartiles. *Falsifier:* AUC < 0.55 or stratified excess ≥ 2.
- **C2 (touch clock transfers).** In the second half of #34, the src-file copy fraction relative to the snapshot at the end of 2026-03-10 PT, against cumulative touches to those reference files, has a single-exponential rate within a factor of 1.5 of the #35 value from the same function (pooled best+rest = 0.00194 per touch; best 0.00211, rest 0.00176). *Falsifier:* ratio outside [0.5, 2].

## Results
*Exploratory, non-holdout (#35 onward), 2026-10-03. Per-period findings are in the period folders. Code: `analysis/curves.py`, `analysis/leakage.py`, `analysis/figures.py`. Numbers: `data/processed/H07-rpg-forks/results.json` and the parquet outputs.*

### Results by goal period

| Folder | Period | Role | Verdict | Headline |
| --- | --- | --- | --- | --- |
| [`G34/`](goalperiod-subhypotheses/G34/README.md) | #34 RPG build (held out) | confirmatory | pending | C1 (hot spots persist from #34) and C2 (touch clock transfers) written; `confirm_h34.py` not run |
| [`NE15/`](goalperiod-subhypotheses/NE15/README.md) | the 03-16 split → 05-28 (spans #35–#44) | exploratory | mixed | Horizontal copy information falls monotonically through #35; the independent-lineage identity holds exactly. The freeze afterwards holds for files and names, not for numbers and functions (#37 revival). 3 shared innovations, all convergent repairs of inherited defects, none channel-borne |
| [`G35/`](goalperiod-subhypotheses/G35/README.md) | #35 Test your game | exploratory | mixed | Gradual divergence (files 0.69 / 0.81 identical to the ancestor). Content divergence is punctuated, and nearly all of it is in #best (re-theming, rebalancing). The touch clock collapses code-level rates; the commit clock and population size do not explain them |
| [`G36/`](goalperiod-subhypotheses/G36/README.md) | #36 Interact with outside agents | exploratory | supported | Freeze and activity collapse as predicted; the only fork commits are README cross-links (2 on #best's repo by #rest agents) |
| [`G37/`](goalperiod-subhypotheses/G37/README.md) | #37 Pick your own goal | exploratory | mixed | One agent (Gemini 3.1 Pro) returned to the game: 27 #best commits, inherited content stable, fork grew (378 new numeric keys) |
| — | #38–#44 | — | n/a | 16 fork commits in 41 active days: README and data notes, 6 #rest code fixes (GPT-5.2), 4 playthrough-milestone logs (Opus 4.5); covered in NE15 |

### Prediction verdicts (where evaluated)
- **P1** gradual divergence: supported ([G35](goalperiod-subhypotheses/G35/README.md)).
- **P2** feature hierarchy: failed in #best, held in #rest; the model-08 "numbers are copied" rival is not supported either ([G35](goalperiod-subhypotheses/G35/README.md)).
- **P3a** commit clock: failed; the file-touch clock works for code (post hoc, tested by C2) ([G35](goalperiod-subhypotheses/G35/README.md)).
- **P3b** frozen core: mixed ([G35](goalperiod-subhypotheses/G35/README.md)).
- **P4** decay then freeze: mixed ([NE15](goalperiod-subhypotheses/NE15/README.md), [G36](goalperiod-subhypotheses/G36/README.md), [G37](goalperiod-subhypotheses/G37/README.md)).
- **P5** rare, channel-borne leakage: mixed. Leakage is rare, but the shared innovations are convergent, and #best received 3 cross-fork commits ([NE15](goalperiod-subhypotheses/NE15/README.md)).
- **P6** population size: failed ([G35](goalperiod-subhypotheses/G35/README.md)).
- **P7** copying, not transformation: supported, with a small significant numeric rebalance in #best ([G35](goalperiod-subhypotheses/G35/README.md)).
- **P8** ground truth: supported ([G35](goalperiod-subhypotheses/G35/README.md)).

### Main findings
1. **A measurable inheritance curve.** Copy fractions decline gradually after the split and level off when work stops. The independent-lineage bound holds exactly: no inherited file was changed to identical content in both forks after day 2.
2. **Two kinds of change.** Code-level divergence is gradual, with a common per-edit rate in both forks (μ ≈ 0.0013 per file-touch for src files). Content divergence (names, numbers) is punctuated and team-specific: two Gemini 3.1 Pro commits in #best carry 59–77% of it, while #rest barely touched content.
3. **Persistent hot spots.** Both forks edited the same inherited files 2.4× more often than independence predicts (C1 tests whether #34 already predicts which files).
4. **Convergence without contact.** Shared innovations are repairs of the same inherited defects, found independently. Real cross-room contact left no shared content: one #35 room visit, and 5 cross-fork commits of which 1 is game code.
5. **Not population size.** 3 #best agents out-produced 10 #rest agents per capita (≈54 vs. ≈20 commits) and diverged further on every feature.

### Caveats
- **Key alignment.** Keyed features treat moved or restructured code as deletion plus insertion: index-labelled array elements, renamed containers, moved functions. Set-level measures bound the effect (#best names: keyed 0.896, set 0.951).
- **Union-key horizontal statistics** fall when one fork grows. Read them alongside the ancestor-key identity, which isolates mutation of inherited content.
- **Copy information** uses our unverified reading of Kolchinsky & Corominas-Murtra; κ and copy fractions are reported alongside and carry the same conclusions. Shuffle nulls have about 0.002 bits of run-to-run Monte Carlo noise.
- Commit times are committer dates (local), not push times; first-parent snapshots stand in for "main over time"; merges bring branch changes at once.
- **Claude Code agent.** Its actions are in a separate stream, so the artifact-based leakage check cannot see its fetches; its commits are visible through git.
- **Leakage is a lower bound.** Identical-content matching cannot see a feature re-implemented after viewing the other fork.
- **Sample size.** n = 2 forks and one split; the clock comparison rests on two curves over 5 active days; rest-week never evolved, so there is no within-room baseline.

## Notes
- 2026-10-03: card opened; predictions written before fetching repository histories.
- 2026-10-03: fork point found from commit-ID sets: A = `abc7c37` for all forks. The #best fork also contains 7 post-T0 commits its agents made on the original repo on day 1 (treated as part of the #best lineage). `rpg-game-rest-week` was created by #rest agents at 17:02–17:03 UTC (GPT-5.2 and DeepSeek-V3.2 both ran `gh repo create` for it) and abandoned when #rest settled on `rpg-game-rest`; its only commit is a README note by GPT-5.4 (04-03). It is not a usable second #rest lineage.
- 2026-10-03: added the conditional null for I_transform after seeing that the plain shuffle null gives negative transformation information under strong copying (an analysis change made after data; both are reported).
- 2026-10-03: the touch-clock result is post hoc (P3a named commits). C2 tests it on #34.
- 2026-10-03: shared artifacts table built (`infra/shared/build_artifacts.py`). Directory-based repo resolution precision, checked against git-printed remotes: 0.89 (`cwd`) and 0.81 (`session_cwd`). Strict uses should keep `how ∈ {url, output, bare}`.
- Next: run `confirm_h34.py --i-am-confirming` once the holdout is opened; add memories as a fourth artifact source; check NE32 and #40 (`the-universe` repo) for other shared-artifact forks; a paraphrase-level leakage detector (embedding similarity of new functions across forks).

## Round 1b (improved data, 2026-10-04)

### What changes in the inputs
- **Copy information:** the shared `infra/shared/copy_info.py` (moved out of `h07lib`, tests claim equivalence) replaces `h07lib` for the end-of-#35 decompositions; reproduced, not re-derived.
- **Commits (DQ4):** each fork commit is matched to the shared `work_commits` ledger; round 1 counted every commit under an agent identity, DQ4 separates agent work from `automated` commits (scripts, CI, cron).
- **Room membership (DQ6):** P8 and the team assignment are re-scored on `ground_truth_labels` `room_assignment` (preferred, non-holdout) instead of `rooms_timeline`.
- **Visibility (DQ1 context ledger):** leakage is re-counted as what each agent could have *read* (`context_ledger_items` joined to `call_windows`), not what was posted. Round 1's chat channel counted posts.
- **Copying vs convergence (H57):** the three shared innovations are checked against the ledger: was any message naming the innovated item, from the other team, in the later adopter team's context before the later commit?
- **Ground truth (DQ6):** #35 lead designers per room and day (03-16/17/18) for a native test.
- **Not used by H07, unchanged:** `activity_bins` (the clocks use calendar active hours, which the event-drop bug did not touch), embeddings and `statement_flags` (H07's features are code and content keys, not text embeddings).
- **Code:** `analysis/round1b.py` (runs only with `H07_DATA=r1b`; round-1 scripts unchanged), outputs in `data/processed/H07-rpg-forks/r1b/`.

### Predictions for round 1b
*Written 2026-10-04, before running anything on the round-1b inputs.* The round-1 predictions are unchanged and re-scored as written.

**What I had seen when writing this:** H07's round-1 results; the DQ6 #35 lead-designer rows (#best: GPT-5.4 on 03-16, Opus 4.6 on 03-17, Gemini 3.1 Pro on 03-18; #rest: three different agents); a root-commit scan of the 633 on-disk clones (structural only: which repos share a root commit, their first/last commit dates and commit counts). Not seen: any DQ4 flag on the fork commits, any ledger count, the dates of the two Gemini 3.1 Pro content commits, or any divergence statistic on another fork family.

- **R1b-1 (shared copy_info).** Every end-of-#35 copy fraction, κ and plug-in information value reproduces to 3 decimals. Credence 0.95.
- **R1b-2 (DQ4 commits).** ≥ 95% of the post-split non-merge commits on the two main forks are DQ4 agent work (not `automated`); P6 stays failed (#best out-produces #rest per capita). Credence 0.85.
- **R1b-3 (P8 on DQ6 rooms).** ≥ 90% of each main fork's post-split commits are by agents DQ6 assigns to the matching room. Credence 0.9.
- **R1b-4 (visibility; NE15 native).** Predictions in [`NE15/README.md`](goalperiod-subhypotheses/NE15/README.md) (Round 1b section).
- **Natives:** [`G35/`](goalperiod-subhypotheses/G35/README.md) (content nucleation by the day's lead designer, DQ6), [`NE15/`](goalperiod-subhypotheses/NE15/README.md) (ledger light cone), [`G36/`](goalperiod-subhypotheses/G36/README.md) (a second fork event: the `agent-papers` fork family of 03-26/27, forked from an outside agent's repo by three village agents in two rooms).

### Results (round 1b, run 2026-10-04)
Code: `analysis/round1b.py` (parts `copyinfo`, `dq4`, `p8`, `ledger`, `lead`, `papers`). Data: `data/processed/H07-rpg-forks/r1b/results_r1b.json` (+ `_provenance.json`). Estimates: `per_period_estimates` (H07, round 1b rows). Runtime ≈ 2 min, one process; no network (the `agent-papers` clones were already on disk from DQ4).

**Old → new.**

| Quantity | Round 1 | Round 1b |
| --- | --- | --- |
| End-of-#35 copy fractions, κ, I, I_copy (8 features × 2 forks + horizontal) | h07lib | shared `copy_info`: identical (max abs diff 0) |
| Post-split non-merge fork commits that are DQ4 agent work | all counted (405) | 398 / 405 agent work; 0 automated; the 7 others are #best's day-1 commits whose canonical copy is `rpg-game` |
| P6 commits per capita in #35, #best vs #rest | 53.7 vs 19.6 | 51.3 vs 19.6 (agent work, DQ6 team sizes 3 / 10): **P6 still failed** |
| P8 own-team commits (rooms) | 98.5% / 99.6% (`rooms_timeline`) | #35: 99.4% / 100% (DQ6 `room_assignment`); all post-split 98.5% / 99.2%: **supported** |
| Cross-team chat in #35 | posts: 3 chat links, 2 #general co-presence days | **reads (ledger):** 288 of 14,572 items (1.98%); #36 3.0%, #37 1.4% |
| Shared innovations with a channel | 0 / 3 (posts, visits, searches) | 0 / 3 with a cross-team read naming the item before the later commit |
| Cross-fork commits preceded by a read of the target fork's address | not measured | 5 / 5 |

**Verdict changes.** None at the card level or per period. R1b-1, R1b-2 (P6 unchanged), R1b-3 supported. P5's mechanism verdict (convergent, not channel-borne) now rests on what agents could read, not on what was posted (H57's correction applied: identical new content with no readable channel is convergence).

**Natives.**
- **G35, lead designers (DQ6): failed, informatively.** The lead designer of the room-day made 0% of #best's content changes on 03-16 → 03-18 (C = 22% of commits); 0/5 room-days have their largest content commit by the lead. Gemini 3.1 Pro carries 86% of #best's #35 content changes whatever its role that day: nucleation looks like a trait (H07-R1), n = 1.
- **NE15, ledger light cone: supported** (V2, V3; V1 mixed). Cross-team reads are 2% and come only from co-presence episodes, including an unpredicted one: the split hour on 03-16, when #rest still read #best's last #general messages. Every cross-fork commit followed such a read; no shared innovation did.
- **G36, a second fork event (`agent-papers`, 03-26): supported** (2/3; 1 n/a). Contribution forks of an outside agent's repo: the two #best copies never moved on `main`; the #rest and org copies re-converged by syncing the upstream (identity on ancestor files 0.97 vs P(both unchanged) 0.67; 29 shared new files, all upstream-first). The independent-lineage bound fails exactly when a channel exists, the negative case the RPG lacked.

**Scorecard changes (round 1b).** I 0 → 1: the independent-lineage test transferred to a second fork family and correctly flagged its channel (one event; the #34 confirmation is still not run). G stays 1 (DQ6 rooms and ledger reads validate the mapping; DQ6 leaders did not predict nucleators). H stays 1 (the leakage rival is now tested on reads and still loses). Others unchanged.

**Model- and data-dependence.** Nothing here depends on an embedding model or on `activity_bins`. The copy-information decomposition is still our unverified reading of Kolchinsky & Corominas-Murtra. The ledger excludes the Claude Code agent as a recipient, which made the second tavern-dice fix, so V2 relies on round 1's fetch check for that commit. The second fork event is file-level only (trees, no contents), and only two of its four copies evolved.

**Claim that stands.** Two isolated copies of one artifact diverge gradually and independently, with identical new content arising only by convergent repair (no readable channel). A second fork family with a shared upstream breaks the independent-lineage bound as expected. Content change is nucleated by one agent rather than by the designated leader.

## Round 2 redirects (2026-10-04)
*From the round-1 reflection (`writeup/round1-reflection/round1-reflection.pdf`).*
- **Where round 1 went sideways:** Forks were treated as passive copying; the interesting signal was nucleation by a single agent.
- **What the direction is really after:** Does culture in shared artifacts change by gradual drift or by rare rewrites from a few agents?
- **H07-R1.** Content change in every shared artifact is heavy-tailed, dominated by a few nucleator agents, and nucleators are consistent across artifacts (a trait; HH96).
- **H07-R2.** Mutation per file-touch is universal across artifacts and agents (HH95).
- **H07-R3.** Forks re-converge when the same models meet the same bugs: the rate of convergent evolution is set by the shared prior (E4).
