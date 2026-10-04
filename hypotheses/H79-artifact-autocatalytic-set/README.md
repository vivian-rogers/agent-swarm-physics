# H79: An artifact-only autocatalytic set

**Status:** **exploratory round 1 done (2026-10-04, non-holdout only): no artifact-only autocatalytic set beyond first order.** Self-catalysis carries 85–99% of maxRAF commits; no catalytic cycle of length ≥ 3 with ≥ 3 events per edge in any of 5 periods (G51 has fewer cross-cycles than the rewired null, p = 0.01); a departed agent's repos catalyse 0% of later work (NE29). But the maxRAF covers 21–40% of agent work commits (P1 failed; 0.3–14% without python heads, a post hoc variant), that coverage is only the share of write sessions with executed repo code (rewired null identical), and executions follow writes more often than precede them (ratio 0.74–0.90; P4 failed in reverse). Confirm script frozen, not run.
**Fields:** origins-of-life theory (reaction networks, autocatalysis), stat mech of open systems, sociophysics (stigmergy)
**Literature:** [`literature/oolen-2026-origins-of-life-review-part2-theory.md`](../../literature/oolen-2026-origins-of-life-review-part2-theory.md) (RAF definition, mapping, candidate 1); [`literature/heylighen-2016-stigmergy-universal-coordination-mechanism.md`](../../literature/heylighen-2016-stigmergy-universal-coordination-mechanism.md) (agentless traces, medium). Hordijk–Steel primary papers are not in `literature/` (to grab).
**Definitions used:** Agent, Regime, Driving / external field, Lineage (DEFINITIONS.md); new named variants proposed in the report (not yet in DEFINITIONS.md): *artifact reaction (session × repo)*, *executed catalyst*, *operator food set*, *artifact-only RAF*.
**From:** HH327 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` ("From the thermodynamics and origins-of-life notes") · **Models:** `physics-models/05-replicator-dissipation/`

## Source HH (verbatim from the HH list)
Is there an artifact-only autocatalytic set? Build session × repo reactions from `work_commits`, `artifact_mentions` and `artifact_commands_text`.
  - Catalysts are executed artifacts and automated streams.
  - The food set is platforms plus kickoff-named and pre-period artifacts.
  - Agents are excluded as catalysts, because they are operator-supplied.
  - Nulls: rewired and time-reversed catalysis.

  *Prediction:* the largest RAF covers ≤ 20% of work commits, and minimal sets of size ≥ 3 occur in ≤ 1/3 of periods. That would make HH244's automata mostly single cron jobs feeding their own repo, not a self-sustaining artifact layer.
  *Egregore-positive:* a RAF beyond the nulls that persists across member turnover.
  *Models:* 05 · *Builds on:* HH244, HH301, HH302 · *Literature:* OoLEN 2026 (RAF background; Hordijk–Steel to grab)

## Question
Do the village's artifacts form a self-sustaining catalytic set on their own, once agents are excluded as catalysts? Or is artifact catalysis first-order: single scripts and repos that run to rewrite themselves, plus pre-existing tools?

## Model
**From:** `physics-models/05-replicator-dissipation/` (replicators and self-maintenance), RAF variant (Hordijk–Steel; background in the OoLEN notes).

- **Species:** repos. Files and sites collapse onto their parent repo; registrable domains and hosting platforms are platforms (food).
- **Reaction** r = (X, Y): "repo X is written while artifact Y's code runs". One reaction per (product, catalyst) pair per period, aggregated over its *events*. An event is one agent session (context segment, `sessions`) × one product repo with ≥ 1 agent work commit to X in that session.
- **Reactants** of r: repos read (strict mentions, `how ∈ {url, output, bare}`, read verbs) in r's first event before the write, excluding X and Y. Writes do not consume X (a write re-makes X from its inputs), so the network can hold cycles.
- **Catalysts** (agents excluded): (i) an *executed catalyst*: a repo Y in whose working directory the agent runs code (bash head ∈ {python, node, npm, npx, make, bash/sh, pytest, ./…, …}, cwd resolved from `artifact_mentions` `how ∈ {cwd, session_cwd}`) in the same session before the last write to X; (ii) an *automated stream*: DQ4 `automated` commits to X catalyse a self-reaction (X, X). Y = X is **self-catalysis** (first-order).
- **Food set F:** platforms; artifacts whose `first_t` precedes the period start (pre-period); artifacts named in chat by humans or the operator during the period (kickoff / operator naming).
- **RAF:** R' ⊆ R is a RAF if every reactant of every r ∈ R' lies in cl_R'(F) and every r ∈ R' has ≥ 1 catalyst in cl_R'(F). The maxRAF comes from polynomial pruning; irrRAFs are the RAFs with no proper sub-RAF.
- **Expected structure** under "mostly first-order": the maxRAF is a union of singletons. Each singleton is a reaction catalysed by food (a pre-period tool) or by its own product (a cron job or a repo's own build script). Cross-catalytic cycles (A's code builds B, B's code updates A) are absent.

## Data scheme (`scheme/`)
- **Inputs:** shared `work_commits` (DQ4), `sessions`, `artifacts`, `artifact_mentions`, `actions` + `actions_bash_head_fixed` (row-aligned), `period_units`, `calendar`, `roster`.
- **Transform** (`scheme/build.py`):
  1. Agent work commits: `~imported & author_kind == agent & ~automated`, canonical rows. DQ4 caveat: `canonical == False` also marks fork commits whose hash first appeared in the parent repo, so non-canonical rows count when the same agent pushed to that repo in the session (push-confirmed fork rows).
  2. Commits → sessions by an as-of join on (agent, t) to the session interval, ±5 min.
  3. Executions: `actions` rows with an execution head; cwd = the agent's last cwd mention within 30 min, same session.
  4. Reads: strict artifact mentions in the session before the event's last commit.
  5. Automated commits: one self-reaction per (repo, author identity, day) stream-day.
  6. Time-reversed catalysis: the same rule with executions **after** the event's last commit (same session, or the agent's next session).
- **Output:** `data/processed/H79-artifact-autocatalytic-set/` `events.parquet` (period, event id, agent, session, product, n commits, catalyst ids, reversed-catalyst ids, read ids; ids only), `species.parquet` (artifact id, kind, creation time, creator agent, food flags per period), `_provenance.json`. No text.
- **Regimes covered:** #31 (regime I), #38, #40, #41, #51 (regime III); holdout masked.

## Observables
- **O1 coverage:** share of agent work commits in events whose reactions are in the maxRAF. The same share of all agent-identity commits (automated included) is reported separately.
- **O2 decomposition** of O1 by catalyst class: self (Y = X), food tool (Y ∈ F, Y ≠ X), in-period tool (Y made in the period, Y ≠ X). The last class is the "artifact layer".
- **O3 irrRAF structure:** sizes of irrRAFs, sampled by random-order pruning from the maxRAF (200 orders), plus an exact search for irrRAFs of size ≥ 3 inside the cross-catalysed core (self-catalysis removed); `S3` = 1 if one exists.
- **O4 time arrow:** real catalysed coverage / time-reversed catalysed coverage.
- **O5 persistence** (egregore-positive): reactions by other agents catalysed by repos that a departed or inactive creator made, after the creator's last action.

## Null / baseline
- **Rewired catalysis:** permute catalysis edges across reactions within the period, keeping each reaction's number of catalysts and each catalyst's number of uses (bipartite edge swap; reads untouched). 200 draws.
- **Time-reversed catalysis:** catalysts from executions after the write (above).
- **Impostors:** the kickoff/goal field (operator-named artifacts are food); the scheduler (automated self-loops reported separately); shared tooling priors (pre-period tools are food, so a used tool is a singleton, not a set).

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** (R1) a collective artifact layer: cross-catalytic cycles, the "egregore" reading of HH290–HH306; (R2) model 06 neutral use (catalysts chosen at random by popularity, no structure: the rewired null).
**Locked holdout used for confirmation:** none yet; `analysis/confirm.py` targets #46–#50 (NE21+NE23 window, automation-dense) and the #51 tail; frozen, not run.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Reactions, catalysts, reads and food come from logged fields (DQ4 commits, sessions, cwd mentions, bash heads). Weak points: execution is head-only (python3 heredocs count as running the repo), cwd precision 0.89, and `artifacts.first_t` is first mention, not creation. Same mapping in regimes I and III. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Time order audited directly (P4): executions after the write are 1.1–1.3× as common as before it, so the static catalysis edge is not causally ordered. Static RAF assumes a period-stationary network. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | The cycle statistic sits at or below the rewired null in all periods (G51 below, p_low 0.01). Coverage equals the rewired null to within 0.01 everywhere: the topology adds nothing beyond the execution share. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | P2 (no ≥ 3 cycles) and P3a (self ≥ 50%) hold in 5/5; P3b in 4/5; P1 fails 5/5; P4 fails 5/5 (reversed); P5 holds in 2/5. |
| E interventional | predicts the change across a natural experiment | 1 | NE29: the retiree's 120 repos catalyse 0 commits of others after the exit (predicted ≤ 1%). G40 (a goal that asks for cross-artifact wiring): no cross-catalysis. Low material in both. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Structure (self ≥ 0.99, 0 cycles) survives dropping python heads; coverage does not (0.3–14%). maxRAF and irrRAF code exact against brute force (300 networks, both reactant rules). Planted 3-cycles with ≥ 3 events per edge: power 30/30, size 0/30 (after A2; unweighted cycles had size 0.77 and power ≤ 0.17). Synthetic background is parametric, not real schedules. |
| G ground truth | agrees with known structure | 1 | The HH244 cron streams appear as single self-catalysed reactions (G51: 54,892 commits; G41: 858; G31: 1,345). |
| H comparative | beats the named rivals | 1 | R1 (collective layer) rejected by P2 and NE29; R2 (neutral, rewired) not rejected for coverage or in-period share, and the real cycle count is lower than R2's. |
| I transfer | holds in other same-mode periods, including the holdout | 1 | Same picture in regimes I and III and in 5 periods; holdout not used. |

## Prediction
*Written 2026-10-04, before running the analysis on real data.*
- **P1 (coverage):** the maxRAF covers ≤ 20% of agent work commits in each replication period (G51, G31, G38, G41). *Against:* > 20% in ≥ 2 of 4.
- **P2 (no collective set):** irrRAFs of size ≥ 3 exist in ≤ 1/3 of tested periods, and where one exists the rewired null produces one at least as often (p ≥ 0.05). *Against:* S3 = 1 in ≥ 2 of 4 periods with rewired p < 0.05 (that would be the egregore-positive reading).
- **P3 (first order):** self-catalysed reactions carry ≥ 50% of maxRAF commits when automated commits are counted; in-period tools catalysing other repos carry ≤ 5% of agent work commits.
- **P4 (time arrow):** real catalysed coverage exceeds time-reversed coverage (ratio > 1, bootstrap over days excludes 1) in ≥ 3 of 4 periods: agents run code, then commit. *Against:* ratio ≤ 1, which would make execution incidental to writes.
- **Synthetic (S1):** the pipeline recovers planted maxRAFs exactly; planted 3-cycles of cross-catalysis at real event counts are detected with power ≥ 0.8 when ≥ 3 events support each edge; the rewired null has size ≤ 0.05 on networks without planted cycles.

### Amendment A1 (2026-10-04, after the coordinator's literature notes; still before any real-data run)
Sources: `literature/hordijk-2023-raf-sets-formal-definition-algorithm.md`, `literature/sharma-2023-assembly-theory-selection-evolution.md`.
- **Agent work is the uncatalyzed background.** Products of agent-only (uncatalyzed) events count as available *reactants* inside the closure. A reaction still enters a RAF only if an artifact catalyst is in cl_R'(F); closure ignores catalysis (Hordijk–Steel), so a catalyst counts if food or the product of a reaction in R'. The strict variant (no background reactants) is reported as a sensitivity.
- **Consequence for O3 (derived, not fitted).** With background reactants, reactants never bind. A self-catalysed reaction (X, X) and a food-catalysed reaction are one-member irrRAFs. Every larger irrRAF is a simple directed cycle in the catalysis graph on non-food artifacts (Y → X for each reaction (X, Y), Y ∉ F, Y ≠ X). S3 is therefore computed exactly by cycle enumeration, not by random pruning.
- **maxCAF beside maxRAF.** maxCAF (Mossel–Steel, constructive) is built in event time order: a reaction fires at an event only if a catalyst is food or was produced by an earlier CAF event. A RAF reaction outside the CAF needs a bootstrap, here an agent action. Report |maxCAF| / |maxRAF| in commits.
- **Time-respecting edges** (already the rule): the catalyst executes in the session before the write. The time-reversed null keeps executions after the write.
- **Common tools are food, not catalysts.** Package managers and platform CLIs (npm, npx, yarn, pnpm, pip, uv, gh, glab, git, deploy CLIs) never make a repo a catalyst. A repo catalyses only when its own code runs in its working directory (python, node, bash/sh scripts, ./x, make, pytest, deno, bun, ruby, perl, php, go run, cargo run).
- **P1–P4 are unchanged.** Added P5: maxCAF covers ≥ 90% of maxRAF commits (artifact catalysis needs no agent bootstrap beyond creating the catalyst). *Against:* < 70%.

### Amendment A2 (2026-10-04, from the synthetic check, before any real-data analysis)
- **Rewired null holds self-catalysis fixed.** Rewiring every catalysis edge turns self-loops into cross edges and fills the null with cycles (the synthetic background went from 1 cycle to thousands), which would make P2 pass by construction. The null now permutes only cross-catalysis edges (catalyst ≠ product), keeping each event's number of cross edges and each catalyst's number of cross uses. Automated self-reactions stay fixed.
- **Cycle enumeration** is capped at length 6 and 2,000 cycles per network (flagged `truncated`).
- **S3 test statistic (primary):** the number of simple cycles of length ≥ 3 in the catalysis graph restricted to reactions backed by ≥ 3 events (`cycles_support3`); p = share of rewired draws with at least as many (100 draws per period). The unweighted S3 (any support) is reported too.
- **Why (synthetic, 2026-10-04):** in a neutral village-sized network (3,000 events; 10% of catalysed events use a new in-period tool), unweighted 3-cycles appear in 77% of networks with nothing planted, and a planted 3-cycle is detected (S3 and p < 0.05) in only 0–17% of runs. With the support ≥ 3 rule, size is 0/30 and power is 30/30 for planted cycles with ≥ 3 events per edge (`data/processed/H79-artifact-autocatalytic-set/synthetic.json`).

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication | mixed | coverage 0.21 [0.19, 0.24]; self 0.97; ≥3-cycles 0 (null 27, p_low 0.01); arrow 0.86 [0.84, 0.88]; CAF/RAF 0.09 |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | mixed | coverage 0.40; self 0.85; in-period tools 0.21 (null 0.20); arrow 0.85 [0.64, 1.00] |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | mixed | coverage 0.22 [0.14, 0.31]; self 0.92; arrow 0.74 [0.56, 0.90] |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | mixed | coverage 0.35; self 0.99; arrow 0.88 [0.77, 0.99] |
| [G40](goalperiod-subhypotheses/G40/README.md) | native | mixed | 11 reactions, 0 cycles; self 0.98; food-tool share 0.003 (N1c failed) |
| [NE29](goalperiod-subhypotheses/NE29/README.md) | native | supported | retiree repos catalyse 0% of others' later work in 12 follow-up periods |

## Results
Pipeline: `scheme/build.py` → `analysis/synthetic.py` → `analysis/run.py` (per period; `--natives`) → `analysis/figures.py`, `analysis/estimates_rows.py`. Data: `data/processed/H79-artifact-autocatalytic-set/` (events 0.4 MB; results/*.json).

1. **The artifact network is first order.** In every period, self-catalysis (a repo whose own code runs before it is written, plus cron streams writing their own repo) carries 85–99% of maxRAF commits. Pre-period tools carry 0.3–2.2% of agent work commits and in-period tools 0.3–3.7%, except G31 (21%, equal to the rewired null and likely cwd mixing in a herding wave).
2. **No collective set.** No period has a catalytic cycle of length ≥ 3 with ≥ 3 events per edge. G51 has 2 supported 2-cycles (each across two makers) and 0 longer ones, against 27 in the rewired null (p_low 0.01): real cross-catalysis is more tree-like than random pairing.
3. **Coverage is the execution share, not topology.** maxRAF coverage (21–40%) equals the share of agent work commits whose session ran repo code, and the rewired null reproduces it to 0.01. With agent work as the background (A1), closure never binds; with strict reactants G51 drops to 0.13 and the others barely move.
4. **Executions follow writes.** Catalysed coverage from executions after the write exceeds that from executions before it in 5/5 periods (ratio 0.74–0.90; CI below 1 in G51, G38, G40). The likely mechanism is commit-then-run (deploy, test, verify). The "catalysis" edge is as much a consequence of the write as a cause.
4b. **Coverage depends on what counts as execution (post hoc variant).** Python heads are 81% of execution actions, and many are heredocs, not the repo's own scripts. Without python and python3, coverage falls to 0.003 (G51), 0.015 (G31), 0.024 (G38), 0.030 (G41) and 0.14 (G40, node builds of the 3D universe), all ≤ 20%. Self share stays ≥ 0.99, supported ≥ 3 cycles stay at 0, and the time ratio is 0.83–1.0 except G31 (2.9 on few events). `results/variant_no_python.json`. So P1's failure rests on the head-only execution rule; the structural results (P2, P3) do not.
5. **RAF needs agent bootstraps.** maxCAF/maxRAF in commits is 0.09 in G51 (the cron repo was made by an agent in the period), 0.75–0.99 elsewhere.
6. **Turnover:** the retiree's repos never catalyse later work (NE29). An egregore-positive result would have needed > 5%.

**Mode and regime dependence:** none detected; regime I (G31) and regime III look alike apart from G31's in-period-tool share, which the null matches.

## Round 2 redirects (2026-10-04)
**What the direction is really after:** whether artifacts carry work forward without an agent in the loop. Round 1 says they do so only as single self-maintaining scripts; the open question is causal: does running an artifact make the next write happen, or only follow it?
- **H79-R1. Content-dependent catalysis.** Replace session co-occurrence with a content edge: the executed script's output (files it writes, URLs it prints) is read or committed in the product. The bare clones give file-level diffs; a script that writes the committed file is a real catalyst.
- **H79-R2. Full command text for execution.** Distinguish `python3 script.py` in repo Y from heredocs; the raw computer-use turns hold it. This removes the head-only execution caveat.
- **H79-R3. The automata as replicators (with H77/H78).** Fit the cron streams' growth and death (model 05): which streams outlive their makers, and do any spawn others?
- **H79-R4. Run `confirm.py`** on #46–#50 and the #51 tail (automation-dense, held out).

## Confirmatory design (frozen 2026-10-04, not run)
`analysis/confirm.py` (guarded; `--dry-run` passes on G41/G51 stand-ins). C1 no supported ≥ 3 cycles above the rewired null in every unit with ≥ 1,000 work commits; C2 self share ≥ 0.80; C3 time ratio < 1 in ≥ 2/3; C4 in-period tools ≤ 5% in ≥ 2/3; C5 |coverage − rewired coverage| ≤ 0.01. Targets #46–#50 and the #51 tail; uses not yet in `holdout_ledger.json`.

## Notes
- 2026-10-04: Round 1 done. Execution detection is head-only (`bash_head_fixed`), so `python3 - <<EOF` counts as running the cwd repo's code; a variant without python would test this (R2).
- 2026-10-04: Round 1 started. Unit of analysis is the goal period (RAFs are period-level objects). A static RAF ignores time; a time-respecting construction makes every irrRAF a singleton by construction (the earliest reaction of any set has only earlier inputs), so the static, type-level network is the right object for "self-sustaining", and the time arrow is tested separately (O4).
