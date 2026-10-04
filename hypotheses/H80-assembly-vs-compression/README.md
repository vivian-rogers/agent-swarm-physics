# H80: Assembly index vs compression as an agent signature

**Status:** **exploratory round 1 done (2026-10-04, non-holdout only): the assembly index adds nothing over compression (ΔAUC −0.007 to +0.001; kill not near), but compression does not identify automation either.** The timing (scheduler) baseline separates automated from agent commit windows (AUC 0.92–1.00); compression reaches 0.96 only for the one in-period cron stream that replays identical commits, and falls to 0.25 across the 28 post-period scripts, whose commits look like agent work. High-index, high-copy command motifs are one agent's habits (median 1 agent at a = 7), not a cross-family prior (7.8% on a joiner's first day and in ≥ 2 labs; P5 failed) and not selection across agents. Confirm script frozen, not run.
**Fields:** algorithmic information theory, assembly theory, statistical inference (classification)
**Literature:** [`literature/sharma-2023-assembly-theory-selection-evolution.md`](../../literature/sharma-2023-assembly-theory-selection-evolution.md) (assembly index, copy number, selection claim); [`literature/abrahao-2024-assembly-theory-lz-compression-critique.md`](../../literature/abrahao-2024-assembly-theory-lz-compression-critique.md) (assembly index = grammar size, LZ bound); [`literature/oolen-2026-origins-of-life-review-part2-theory.md`](../../literature/oolen-2026-origins-of-life-review-part2-theory.md) (candidate 4)
**Definitions used:** Agent, Regime, Entropy (of behavior; entropy-rate variant), Driving / external field (DEFINITIONS.md). New named variants proposed in the report: *commit window*, *command motif*, *assembly proxy (Re-Pair grammar size)*, *scheduler baseline*.
**From:** HH328 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` ("From the thermodynamics and origins-of-life notes") · **Models:** `physics-models/04-semantic-information/` (tool: compression and grammar estimators)

## Source HH (verbatim from the HH list)
Assembly index vs compression as an agent-vs-script signature. Classify DQ4 automated vs agent commits from sequence features only, with timing-only results reported as the scheduler baseline.
  - *Prediction:* compression reaches AUC ≥ 0.9 and assembly index adds < 0.02. Also, ≥ 70% of high-index, high-copy command motifs appear on an agent's first day and across model families. Assembly theory's "high index × high copy number = selection" would then be read as the shared-prior impostor.
  - *Kill:* assembly index adds ≥ 0.05 AUC over compression.
  - *Models:* 04 · *Builds on:* HH191–HH210, HH244, DQ4 · *Literature:* OoLEN 2026 (assembly theory background; primary papers to grab)

## Question
Does the assembly index of a commit or command sequence carry information about who made it (an agent or a script) beyond plain compression? And are the high-index, high-copy command motifs that assembly theory reads as "selection" already present on an agent's first day, across model families (the shared model prior)?

## Model
**From:** `physics-models/04-semantic-information/`, used as a tool family (compression estimators of structure). Assembly theory (Sharma et al. 2023) is the claim under test.

- **Object:** a token string x of length L. For commits, one token per commit; for commands, one token per action.
- **Commit token:** a hash of (n_files, msg_len, insertions, deletions bucket, merge, pages-branch, deploy-message flags) from DQ4 `work_commits`. No text.
- **Command token:** the action type, or the bash head (`actions_bash_head_fixed`) for bash actions, hashed.
- **Assembly index a(x):** the minimal number of joins that builds x from single tokens, with reuse of built pieces. By Abrahão et al. (Cor. 8) it equals the non-basis size of the minimal grammar. **Proxy:** a_RP = (#Re-Pair rules) + (length of the final Re-Pair string − 1), an upper bound. Exact a by iterative-deepening search for L ≤ 12 (validation only). Lower bound ⌈log₂ L⌉.
- **Compression family (the rivals that AT must beat):** empirical entropy rate (block entropy h₂ = H₂ − H₁), LZ76 complexity, LZ78 factor count, gzip ratio, zstd ratio (CLI).
- **Copy number** n_i: number of distinct sessions that contain motif i. **Ensemble assembly** A = Σ e^{a_i}(n_i − 1)/N_T.

## Data scheme (`scheme/`)
- **Inputs:** shared `work_commits` (DQ4), `actions` + `actions_bash_head_fixed` (row-aligned), `sessions`, `calendar`, `roster`, `period_units`.
- **Transform** (`scheme/build.py`):
  1. *Commit windows:* agent-identity, non-imported commits (canonical or not: the DQ4 fork caveat does not change who authored a commit; duplicate hashes keep one row). Sorted per (repo, author identity) stream; cut into windows of L = 16 consecutive commits; label = majority `automated`; purity kept. At most 20 windows per stream-day (a dominant cron stream cannot fill the sample).
  2. *Features per window:* timing-only (log inter-commit gaps: median, IQR, min, max; share of gaps within 2 s of the median gap; share of commits at second < 5; hour-of-day sine and cosine (PT); share in the village window); compression family; assembly proxy. `turn_gap_s`, `turn_backed` and `clockwork` define the label and are never features.
  3. *Command motifs:* per session, the token string of actions (regime III, non-holdout). Motifs = contiguous n-grams, n = 4…8. Per motif: exact a (n ≤ 8), session copy number, agents, labs, first-day presence.
- **Output:** `data/processed/H80-assembly-vs-compression/` `windows.parquet` (window id, period, stream hash, label, purity, features), `motifs.parquet` (motif hash, n, a, copies, agents, labs, first-day flags), `_provenance.json`. Hashes and numbers only.
- **Regimes covered:** #31 (regime I), #41, #51 (regime III) for the classifier; regime III for motifs; #38 as a no-automation check.

## Observables
- **AUC** of an L2 logistic classifier, automated vs agent windows, out of fold. Folds are blocked by repo (no stream in both train and test); a day-blocked variant is reported too. Feature sets: T (timing only, the scheduler baseline), C (compression family), C + A (adds the assembly proxy), A (assembly only), T + C.
- **ΔAUC_A = AUC(C + A) − AUC(C)**, with a 95% interval from a bootstrap over repos.
- **Rank correlation** ρ(a_RP, LZ78 factors) over windows.
- **Prior share:** among high-index, high-copy motifs (a ≥ 6 and session copies ≥ 20), the share present on ≥ 1 agent's first regime-III day **and** used by ≥ 2 labs. Contrast: first-day vs random-later-day presence ratio per motif, and copy-matched low-index motifs.
- **NCD drift:** per agent-day, the normalized compression distance (gzip) between a 400-token sample of the day's command string and the pooled first-day reference of the other agents. A falling NCD would be village-specific structure beyond the prior.

## Null / baseline
- The **scheduler baseline** T is the first rival: if T alone reaches AUC ≈ 1, sequence features can only add a little.
- **Label-permutation null** for AUC (within period, 200 draws) and a stream-shuffled null for ΔAUC.
- **Shared-prior impostor:** first-day and cross-lab presence; NE32 isolated newcomers.
- **Kickoff field:** commands carry no kickoff text tokens (heads only), so templated kickoff strings cannot enter.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** (R1) assembly theory's claim that a measures selection beyond compression; (R2) the scheduler (timing alone); (R3) compression family (LZ, entropy, gzip, zstd), which is the hypothesis's own expected winner.
**Locked holdout used for confirmation:** none yet; `analysis/confirm.py` targets #47 and #49 (automation-dense, held out) and the #51 tail; frozen, not run.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Commit tokens hash DQ4 numeric fields (no text); command tokens are action types and bash heads. The label `automated` is defined by turn timing, so the timing family has an advantage by construction (stated). Same mapping in regimes I and III. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Fixed-length windows (L = 16) remove length effects on compression; cap of 20 windows per stream-day limits the cron stream's weight. Within-period stationarity assumed. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | All families beat label permutation in-period (p < 0.005). Day- and repo-blocked folds; compression fails the repo-blocked transfer (0.25). |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | P2 (no assembly gain) holds in 4/4 units and P6 (no NCD fall) holds; P1, P3 (ρ 0.82 in G51), P4b, P5 fail. |
| E interventional | predicts the change across a natural experiment | 1 | NE32: isolated newcomers use high-index motifs on day 1 at 1.65× the incumbents' rate, consistent with agent-carried habits; the NE33 arm is uninformative (selection artifact). |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 2 | Exact assembly index verified against brute force (600 strings); Re-Pair proxy never below exact, exact in 97.6%, within +1 in 99.6%, Spearman 0.99; s^k known values recovered. Pipeline size 0/20, power 20/20 for an assembly-only signal. |
| G ground truth | agrees with known structure | 0 | G38 (no automation): sequence classifiers trained on G51+post flag 97% of agent windows; timing flags 0% (with the village-window feature). |
| H comparative | beats the named rivals | 1 | AT (R1) rejected: assembly adds ≤ 0.001 AUC. Compression (R3) loses to the scheduler (R2) in every unit. |
| I transfer | holds in other same-mode periods, including the holdout | 1 | ΔAUC ≈ 0 in G31, G41, G51; compression transfer across streams and to G38 fails. Holdout not used. |

## Prediction
*Written 2026-10-04, before running the analysis on real data (the coordinator's 2026-10-04 literature points were folded in before any run).*
- **P1 (compression suffices):** C reaches AUC ≥ 0.90 (repo-blocked) in G51, and ≥ 0.85 in G31 and G41.
- **P2 (assembly adds nothing):** ΔAUC_A < 0.02 in every period. **Kill:** ΔAUC_A ≥ 0.05 in any powered period (≥ 50 windows per class).
- **P3 (AT ≈ LZ):** Spearman ρ(a_RP, LZ78 factors) ≥ 0.9 over windows in each period.
- **P4 (scheduler baseline):** T alone reaches AUC ≥ 0.85 in G51. T + C adds ≥ 0.02 over T, so sequence structure is not only the cron schedule. *Against:* T + C adds < 0.01.
- **P5 (prior impostor):** ≥ 70% of high-index, high-copy command motifs are present on some agent's first regime-III day and used by ≥ 2 labs. The median first-day / later-day presence ratio is ≥ 0.8. *Against:* < 50%, or a ratio < 0.5 (motifs learned in the village).
- **P6 (no village-specific accumulation):** the NCD to the first-day reference does not fall: median NCD on days ≥ 5 of an agent's tenure is within 0.02 of its day-1 to day-2 value. *Against:* a fall ≥ 0.05.
- **Synthetic (S1):** a_RP is within +1 join of the exact a on ≥ 80% of random strings with L ≤ 12, never below it, and exact on s^k (a = |s| − 1 + l(k), l = shortest addition chain); Spearman(a_RP, exact) ≥ 0.9. A planted generator difference that only a carries (same LZ78 count, different grammar size) is detected at ΔAUC ≥ 0.05 by the pipeline (power check).

### Amendment A1 (2026-10-04, after building windows, before any classifier run)
- **Finding while building:** inside each period's calendar days there is **one** automated stream (one repo × identity) with ≥ 16 commits: G51 the GPT-5 cron stream, G31 one stream, G41 one stream, G38 none. The other 27 G51 streams with ≥ 16 automated commits run on 2026-09-21 → 10-03, after the village's last day. They are DQ4 goal 51 and outside every holdout window (#51 tail ends 09-21, exclusive).
- **Consequence:** with one positive stream, repo-blocked folds are undefined, and any classifier separates one script from the agents (n_eff = 1 positive unit).
- **Change:** (i) in-period units (G31, G41, G51) use day-blocked folds and are labelled "one positive stream"; P1/P2 are read there with that caveat. (ii) A new unit **G51+post** adds the post-period automated windows (28 streams) to G51's in-period agent windows, with repo-blocked folds. It is the powered test of P1–P3. The timing family includes `in_window`, which separates post-period commits trivially, so T is reported with and without `in_window` there.
- Predictions P1–P6 are unchanged; P1/P2 for G51+post use the G51 thresholds.

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication | mixed | C 0.965 (1 stream) / 0.254 (G51+post, 28 streams); ΔAUC_A +0.001 / −0.007; T 0.999 / 0.915; ρ 0.82; prior share 7.8% |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | mixed | C 0.69; ΔAUC_A 0.000; T 0.955; ρ 0.98 |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | supported | C 0.958 (1 stream, window folds); ΔAUC_A −0.001; ρ 0.95 |
| [NE32](goalperiod-subhypotheses/NE32/README.md) | native | mixed | isolated newcomers' day-1 high-index motif share 1.65× incumbents'; NE33 arm uninformative |
| [G38](goalperiod-subhypotheses/G38/README.md) | native | failed | no-automation period: C flags 97% of agent windows; T 0% |

## Results
Pipeline: `scheme/build.py` → `analysis/synthetic.py` → `analysis/run.py --part cls|motifs|ncd|natives` → `analysis/figures.py`, `analysis/estimates_rows.py`. Data: `data/processed/H80-assembly-vs-compression/` (9 MB).

1. **Assembly index = compression, here.** Adding the Re-Pair assembly proxy to the compression family changes AUC by +0.0009 [−0.0003, 0.0019] (G51), 0.000 (G31), −0.001 (G41) and −0.007 [−0.018, −0.001] (G51+post). The kill (≥ 0.05) is far. Synthetic: an assembly-only signal would show (ΔAUC median 0.37), so this is a power-backed null. The rank correlation with LZ78 is 0.82–0.98 (P3's 0.9 fails in G51): the proxy is not identical to LZ, but its extra variance carries no label information.
2. **The scheduler wins.** Timing alone gives AUC 0.999 (G51), 0.955 (G31), 0.948 (G41), 0.915 (G51+post, repo-blocked). Adding compression adds ≤ 0.005. This is partly by construction: the label is defined by time to the nearest agent turn.
3. **Compression detects replay, not automation.** The in-period cron streams write near-identical commits (1.0–1.3 distinct tokens per 16), so C separates them (0.96–0.97, one stream each). The 28 scripts committing after the village's last day write commits as varied as agent work (12.5 distinct tokens), and C falls to 0.25 under repo-blocked folds (0.60 day-blocked). A classifier trained there flags 97% of G38's pure agent windows.
4. **High a × high copy is a per-agent habit.** Among 12,869 command motifs (n = 4–8, ≥ 20 session copies, G51), the median number of agents using a motif falls from 7 (a = 2) to 1 (a = 7); the top agent holds 70% of a high-index motif's agent-days. Only 7.8% of the 562 high-index, high-copy motifs appear on a joiner's first day and in ≥ 2 labs (P5 failed), below copy-matched low-index motifs (14.8%). AT's selection reading is fooled here by within-agent repetition, a third impostor next to the shared prior and the scheduler.
5. **No village-specific accumulation.** Joiners' command strings do not move toward or away from the first-day reference over their tenure (NCD change +0.005; P6 supported).

## Round 2 redirects (2026-10-04)
**What the direction is really after:** a log-only detector of "who did this, an agent or its script", and whether assembly theory's selection index measures anything in agent swarms beyond repetition.
- **H80-R1. Copies per independent producer.** Recompute ensemble assembly A with copy number counted per agent (Sharma's caveat), and test it against plain motif counts and gzip across periods (phase-diagram ranking).
- **H80-R2. Content tokens for commits.** Hash file paths from the bare clones (read-only `git log --name-only`); scripts that write the same file set should separate from agents where size fields do not.
- **H80-R3. A timing-free label.** Build a label from process evidence (cron or CI config files, runner identity) so that timing is not favoured by construction.
- **H80-R4. Run `confirm.py`** on #46–#50 and the #51 tail.

## Confirmatory design (frozen 2026-10-04, not run)
`analysis/confirm.py` (guarded; `--dry-run` passes on G31/G41/G51 stand-ins). C1 ΔAUC_A < 0.02 in every unit with ≥ 50 windows per class (kill ≥ 0.05); C2 ρ(a_RP, LZ78) ≥ 0.8; C3 T ≥ 0.9 and T + C adds < 0.01 in ≥ 2/3; C4 Spearman(a, agents per motif) < 0 and median agents at a ≥ 6 ≤ 3. Targets #46–#50 and the #51 tail; uses not yet in `holdout_ledger.json`.

## Notes
- 2026-10-04: Round 1 done. zstd via the CLI (no Python binding offline); gzip via zlib. The LZ78 count of a 16-token window ranges 6–16, so ranks tie often.
- 2026-10-04: Round 1 started. Unit: goal period (classifier fitted within a period). The label `automated` is itself defined by timing (no logged turn within 5 min, or clockwork streams), so the timing-only baseline has an advantage by construction; the turn-gap columns are never used as features.
