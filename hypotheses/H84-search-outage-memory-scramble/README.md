# H84: History-search outage as a collective-memory scramble

**Status:** **exploratory round 1 done (2026-10-04, non-holdout only). Failed (scoped): the history-search outage cost no continuity.** The outage fully reached one agent (answers 2,880 → 42 characters; 128 retries). Continuity rose with dose instead of falling (β_V1 = +0.12 per search per 100 calls, placebo rank p for a dip 0.87), earlier-goal references rose (largest of 38 placebos), commits per 20 calls did not move (+0.03 ± 0.51). A dose-proportional continuity dip ≥ 0.30 at the mean searcher dose is excluded (power 0.85–0.91); 0.20 is not (power 0.63–0.74). The search answers carry 0.012 bits [−0.011, +0.035] of allocation information (pooled over 7 periods; I_Q > 0 in 2/7). NE18 had no first stage; G51 failed answers cost nothing. `confirm.py` written, **not run**. (Approved by Vivian 2026-10-04 from HH294; card filled ~20:05 UTC before any outcome.)
**Question (GOALS.md):** **Q4**, where does the swarm's information live, and what is it worth? H84 measures what the village's history-search channel is worth by its one natural scramble: the 2026-03-31/04-01 malfunction. It delivers the ΔV of the **search row** of the H87 κ table.
**Fields:** information theory (Kolchinsky–Wolpert semantic information, natural-scramble variant), causal inference (dose-weighted difference-in-differences, placebo dates), physics of life (collective memory, viability)
**Literature:** [Kolchinsky & Wolpert 2018](../../literature/kolchinsky-2018-semantic-information-autonomous-agency.md) (value of information ΔV under a scramble of system–environment correlations; κ = ΔV/I); [Sowinski et al. 2023](../../literature/sowinski-2023-semantic-information-resource-gathering-agents.md) (viability flat until the channel degrades past a threshold; the history oracle as a "sensor" whose fidelity the outage removes).
**Definitions used** (`physics-models/DEFINITIONS.md`): Regime; Semantic information (Kolchinsky–Wolpert); **Semantic information (natural-scramble variant)** (H15); Unit macro-state (allocation) (H58). Named variants defined here and proposed for DEFINITIONS.md: **search dose**, **continuity (repo-age variant)**, **duplicate creation (name-overlap variant)**, **earlier-goal reference share**.
**From:** HH294 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/04-semantic-information/`
**Data inputs (shared tables first):** DQ1 context ledger (`context_ledger_turns`: calls and `kind == "search"`), DQ4 work ledger (`work_commits`, agent work only; `work_repos.first_commit_t`), `artifact_mentions` + `artifacts` (strict mentions), raw `events` SEARCH_HISTORY rows (answer and query **lengths and repo ids only**, no text stored), `calendar`, `period_units`, `roster`. Not used: `activity_bins`, `actions.error`.

## Source HH (verbatim from the HH list, including literature refinements)
The history-search outage is a natural scramble of collective memory. On 2026-03-31 and 04-01, history search returned near-empty answers (agents retried 85–98 times a day; infra Known issues). Search token logging also starts on 03-24. This is a Kolchinsky intervention on the village's access to its own past. Viability: project continuity, meaning the share of DQ4 work on pre-existing repos, the re-creation of artifacts that already exist, and references to earlier goals. Prediction: continuity dips on outage days relative to placebo weekdays, in proportion to each agent's pre-outage reliance on search, and recovers immediately afterwards. *Check:* agent-day continuity vs pre-outage search dose; duplicate creation; placebo days. *Kill:* no dip, so the history channel carries ≈ 0 semantic information, like memory in H15.
  *Models:* 04 · *Builds on:* H15, HH261 (H70) · *Periods:* 03-24 → 04-03 window

## Question
When the history-search oracle returned near-empty answers for two days, did agents that relied on it lose project continuity in proportion to their reliance, and did they recover at once when it came back?

## Design: two layers (Vivian, 2026-10-04)
- **Replication** (role `replication`): the search channel's allocation information I_Q at search calls (bits), on every regime-III non-holdout period with ≥ 30 search calls. It is the I side of κ_Q; the outage is the only place ΔV_Q is identified.
- **Natives** (role `native`, each with its own dated prediction):
  - **N1, G37 outage** (03-31, 04-01): the HH test. Dose-weighted DiD with placebo dates and recovery days. Folder `goalperiod-subhypotheses/G37/`.
  - **N2, NE18** (2026-04-20, inside #38): the opposite intervention. Search answers became verbatim segments over a 10-day window, and the answerer changed (NE40, same day). Folder `goalperiod-subhypotheses/NE18/`.
  - **N3, G51 failed answers** (call scale, #51 non-holdout head): single searches that return a near-empty answer, against normal answers from the same agent. Not exogenous, so role native with a descriptive verdict rule. Folder `goalperiod-subhypotheses/G51/`.

## Model
**From:** `physics-models/04-semantic-information/` (Kolchinsky–Wolpert, natural-scramble variant).
- **System X:** one agent. Its state on an agent-day is its **allocation**: the repos its work commits go to (DQ4), coarse-grained to "pre-existing" vs "new", plus its artifact references.
- **Environment Y:** the village's logged past, reachable through the history-search oracle (Y → X channel Q).
- **Scramble:** the outage. Answers collapse from a median of 1.4–3 k characters to 383 (03-31) and 42 (04-01) characters (H56). The channel stays nominally open, so agents retry. It is a degradation of the channel, not a marginal-preserving shuffle.
- **Dose:** each agent's **search dose** d_a = search calls per 100 ledger calls on 03-24 → 03-30 (the five regime-III days before the outage; 12 agents). The dose is concentrated: three agents have d = 1.95, 0.81, 0.31; nine have d ≤ 0.13 (four have 0).
- **Value:** ΔV_Q(d) = β·d, from

  y_{a,t} = α_a + γ_t + β · d_a · O_t + β_rec · d_a · R_t + ε_{a,t},

  with O_t = 1 on 03-31 and 04-01, R_t = 1 on 04-02 and 04-03 (recovery), agent and day fixed effects. The day effects absorb everything common to a day: #37's goal structure, 03-31's 12.6-hour window, the kickoff on 04-02.
- **κ link (for H87):** ΔV_Q in commits per 20 calls at the mean searcher dose, divided by I_Q (bits) from the replication layer.
- **Departures from KW** (axis A): degradation instead of a shuffle; dose is chosen by the agents (pre-outage, so not affected by the outage); one event (two days), so the "ensemble" is 12 agents.

### Rivals
- **R0, search is decorative (≈ 0 semantic information):** β = 0 for every viability component; continuity is carried by artifacts and context (H70, H44).
- **R1, substitution:** searchers lose search but re-read their own artifacts (the H44/H58 path); continuity is unchanged while artifact re-reads rise.
- **R2, goal-structure confound:** heavy searchers behave differently on days 2–3 of any goal; the "dip" appears equally at kickoff-matched placebo days.
- **R3, retry cost (attention, not memory):** the outage costs work through wasted retries (commits per call fall), not through lost continuity (continuity share unchanged).

## Data scheme (`scheme/`)
- **`scheme/search_events.py`:** one pass over raw `events.jsonl.gz` (substring prefilter on SEARCH_HISTORY). Per search: t, pt_date, agent, event_index, answer chars, query chars, and the repo ids named in the answer and in the query (`infra/shared/build_artifacts.canon` + `refs_in_text`, mapped to `work_repos`). No text is stored. Holdout days dropped at scan time. Output `search_events.parquet` (shared with H87).
- **`scheme/build.py`:** the agent-day panel.
  - Days: regime-III non-holdout active days 03-24 → 05-29 (#36b–#42, #44; #43 is held out), weekdays only.
  - Agents: the 12 roster agents active on 03-24 → 03-30 (the dose window). Later joiners have no dose and are excluded.
  - Per agent-day: ledger calls, search calls, failed searches (answer < 150 chars), work commits (DQ4 agent work), commits on pre-existing repos, new repos, duplicate new repos, strict artifact mentions and earlier-goal mentions, own-artifact re-reads.
- **Output:** `data/processed/H84-search-outage-memory-scramble/` with `search_events.parquet`, `panel.parquet` (codes and counts only), `_provenance.json`; results in `results/`.
- **Regimes covered:** regime III only (the ledger's call counts and the outage are regime-III facts).

### Viability components (fixed before any outcome)
- **V1 continuity (repo-age variant), primary:** the share of the agent's work commits that day that go to repos whose first commit (`work_repos.first_commit_t`, any author) is before that PT day's window start. Defined on agent-days with ≥ 1 work commit.
- **V2 duplicate creation (name-overlap variant):** the number of new repos that day (first commit on that day, first committer = the agent) whose name token set (split on `-_./`, lowercase, tokens ≥ 3 chars) has Jaccard ≥ 0.5 with a repo that existed before the day.
- **V3 earlier-goal reference share:** the share of the agent's strict artifact mentions that day (`how ∈ {url, output, bare}`; sources action, chat, intention) that name artifacts first seen before the current goal period's first day. Defined on agent-days with ≥ 5 strict mentions.
- **V4 work rate:** work commits per 20 ledger calls (for κ, and for rival R3).
- **First stage and substitution:** search calls per 100 calls; failed-answer share; own-artifact re-reads (action mentions of pre-existing repos the agent committed to before) per 100 calls.

## Observables
- **O1** β for V1–V4 (per unit dose; also reported at the top dose and at the mean dose of the three searchers).
- **O2** β_rec for V1–V4.
- **O3** placebo rank of β among all other consecutive weekday pairs in the panel (excluding the dose window, outage and recovery days), and among **kickoff-matched** pairs (days 2–3 of #38, #39, #40, #41, #42, #44).
- **O4** dose-permutation p (2,000 permutations of d across the 12 agents) and leave-one-agent-out β.
- **O5** first stage: answer length and retries for each searcher, outage vs pre-outage days.
- **O6** I_Q per period (replication; bits, Miller–Madow, within-agent permutation floor; `infra/shared/semantic_kappa.mi_corrected`).

## Null / baseline
- **Placebo dates** (main inference): the same regression with O_t moved to every other consecutive weekday pair; one-sided rank p.
- **Kickoff-matched placebo dates:** only pairs that are days 2–3 of a goal period (the outage is days 2–3 of #37).
- **Dose permutation:** shuffles which agent had which dose.
- **Synthetic power at real counts** (axis F, `analysis/synthetic.py`, before real outcomes): keep the real panel (agents, days, commit and mention counts), draw outcomes from agent and day base rates with no effect, and plant a dose-proportional dip. Report size and power for the placebo-rank test at planted dips of 0.10, 0.20, 0.30 and 0.50 in V1 at the mean searcher dose.
- **The effect that matters:** a 0.20 drop in V1 at the mean searcher dose (about half the forced-erasure cost on output, H15/H70). A negative verdict needs power ≥ 0.8 there; otherwise "inconclusive".

## Impostors (STANDARDS §1)
| Impostor | How it could fake a dip | How H84 removes it | Status |
| --- | --- | --- | --- |
| Scheduler field | The outage days are days 2–3 of #37; 03-31 ran a 12.6-hour window | Day fixed effects absorb every common-day shock; β is identified only by between-agent dose differences; outcomes are shares and per-call rates; placebo pairs | removed |
| Exogenous field (goal, kickoff) | #37's goal may favor new repos on days 2–3, and heavy searchers may respond more to such goals | Day fixed effects; kickoff-matched placebo pairs (days 2–3 of six other goals); recovery days 04-02/03 include #38's kickoff and are reported separately | partly |
| Shared model priors | The three searchers are three particular models; family habits could interact with day 2–3 of a goal | Agent fixed effects; placebo dates remove any stable dose × day-of-goal pattern; leave-one-agent-out β | partly |
| Contemporaneous convergence | n/a: no peer-influence claim | — | n/a |

## Scorecard scheme, rivals and holdout
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R0 decorative search; R1 substitution through artifacts; R2 goal-structure confound; R3 retry cost.
**Locked holdout used for confirmation:** none yet. Planned in `analysis/confirm.py` (frozen, guarded, **not run**): NE25 (2026-07-01, search scoped to the agent's own village, inside the held-out NE21+NE23 window) as a second dose-weighted scramble, and I_Q on held-out regime-III periods (#43, #45–#50, #51 tail).

*(Round 1 scores in "Faithfulness scorecard" below.)*


## Prediction
*Written 2026-10-04 ~20:05 UTC, before any outcome statistic (V1–V4, re-reads) was computed. Looked at before: the daily search counts, answer lengths and searcher sets (H56's numbers-only table), the pre-outage dose of each agent, the calendar and the period units. Prior knowledge: H15 (memory carries ≈ 0 day-scale value), H44/H58 (agents recover through their own artifacts; re-read raises P(return) 0.96 vs 0.85), H70 (artifact pointer 0.14 bits per erasure with no measurable value; context row κ_C = 5.2 commits per 20 calls per bit).*

| # | Prediction (HH294) | Counts against |
| --- | --- | --- |
| P1 | **Continuity dips in proportion to dose.** β_V1 < 0, placebo rank p ≤ 0.10 (one-sided) among all pairs and among kickoff-matched pairs; a drop of ≥ 0.10 in V1 at the mean searcher dose. | β_V1 ≥ 0, or within the central 80% of placebo β |
| P2 | **Immediate recovery.** β_rec(V1) inside the central 80% of placebo β. | β_rec below the placebo 10th percentile |
| P3 | **Duplicates up, earlier-goal references down.** β_V2 > 0 and β_V3 < 0, each beyond the placebo 80th / 20th percentile. | opposite signs |
| P4 | **First stage.** For each searcher with ≥ 5 searches on outage days, the median answer length is < 25% of its pre-outage median and searches per 100 calls rise. | answers not degraded for a searcher (the scramble did not reach it) |
| P5 | **Substitution (R1 marker).** Own-artifact re-reads per 100 calls rise with dose on outage days (β > 0). | β ≤ 0 |
| N1 | see `goalperiod-subhypotheses/G37/README.md` (P1–P5 are N1's predictions) | |
| N2 | see `goalperiod-subhypotheses/NE18/README.md` | |
| N3 | see `goalperiod-subhypotheses/G51/README.md` | |
| R | **Replication:** I_Q > 0 (permutation p < 0.05) in ≥ 2/3 of eligible periods; pooled I_Q ≤ 0.3 bits | I_Q not significant in > 1/2 of periods |

**Analyst's expectation (stated, not tested):** with three effective searchers and two days, power at the effect that matters may be below 0.8. If so, a null on P1 is "inconclusive", not R0.

**Verdict rule (N1):** *supported* if P1 holds and P2 holds; *failed* if β_V1 ≥ 0 or inside the central 80% of placebos **and** synthetic power at a 0.20 dip is ≥ 0.8 (R0); *inconclusive* if P1 fails with power < 0.8; *mixed* otherwise.

## Synthetic validation (axis F; run 2026-10-04 20:11–20:16 UTC, before any real outcome statistic)
`analysis/synthetic.py` → `data/processed/H84-search-outage-memory-scramble/synthetic/synthetic.json`. Real skeleton: the 12 dose-window agents, 48 panel days, real commit and mention counts per agent-day, real doses. Outcome drawn as Binomial(count, p) with logit p = agent + day + agent-day jitter (s_e ∈ {0.3, 0.6, 1.0}), with an absolute shift δ·d_a/d̄_s planted on the treated days. Test: one-sided placebo rank p ≤ 0.10. 200 replicates per cell.

| Test | Placebos | Size (δ = 0) | Power at 0.10 | at 0.20 | at 0.30 | at 0.50 |
| --- | --- | --- | --- | --- | --- | --- |
| G37 V1 continuity | 38 pairs | 0.05–0.12 | 0.34–0.43 | 0.63–0.74 | 0.85–0.91 | 0.99–1.00 |
| G37 V3 earlier-goal refs | 38 pairs | 0.04–0.08 | 0.43–0.94 | 0.91–1.00 | 1.00 | 1.00 |
| NE18 V1 (shift +δ) | 17 boundaries | 0.12–0.22 | 0.31–0.46 | 0.46–0.65 | 0.53–0.71 | — |

- **G37 V1 is underpowered at the effect that matters** (a 0.20 drop at the mean searcher dose: power 0.63–0.74). Power reaches 0.85 at a 0.30 drop. V3 is powered at 0.20, although the binomial draw ignores overdispersion of mentions, so its power is an upper bound.
- **The NE18 test is oversized** (0.12–0.22 at nominal 0.10) and has low power.
- **Correction (2026-10-04, blind-rater check): one reached agent.** The power above assumes the dip reaches every dose-window agent in proportion to dose. The first stage (P4) shows that the outage fully reached only the top-dose searcher (dose 2.00 and d̄_s = 1.05 in `h84lib.dose_table`). `analysis/synthetic_one_reached.py` (run 2026-10-04, after round 1, one process; `data/processed/H84-search-outage-memory-scramble/synthetic/synthetic_one_reached.json`) plants the same per-agent dip δ·d_a/d̄_s in that agent only and uses the card's test unchanged (38 placebo pairs, 200 replicates per cell, s_e 0.3 / 0.6 / 1.0). Results: size 0.075–0.12. Power is 0.58–0.68 at δ = 0.20 (was 0.63–0.74) and 0.85–0.94 at δ = 0.30 (was 0.85–0.91); Monte Carlo SE ≈ 0.03. The dose-weighted β is dominated by the top-dose agent, so losing the other searchers costs little power. The A1 scope (no dip ≥ 0.30 at d̄_s) still holds. But δ = 0.30 at d̄_s means a 0.57 continuity dip in the one reached agent. A 0.20 dip in the reached agent itself (δ = 0.105) has power only 0.31–0.43 and is not excluded. Read the negative as: "no large dip in the one scrambled heavy searcher".

## Amendments (2026-10-04 20:18 UTC, after the synthetic, before any real outcome statistic)
- **A0 (structural, written into the scheme before any outcome):** V3 counts only repo, site and file artifacts (not URL domains, whose first-seen dates are mostly ancient), and "searchers" are agents with dose ≥ 0.25 searches per 100 calls; d̄_s is their mean dose.
- **A1 (power scope, adjudication rule 2):** a negative V1 verdict is scoped to a **0.30** drop at d̄_s (power 0.85–0.91), not to 0.20. If β_V1 is null, the claim reads "no V1 dip ≥ 0.30 at the mean searcher dose", and the 0.20 effect stays inconclusive. V3 negatives are scoped at 0.20.
- **A2 (kickoff-matched placebos):** only six kickoff-matched pairs exist, so their rank p cannot go below 1/7 = 0.14. P1's kickoff-matched clause now reads "β_V1 below all six kickoff-matched placebo β (p = 0.14)" and is a secondary check, not a gate.
- **A3 (NE18):** because the test is oversized, NE18's Q1 needs placebo rank p ≤ 0.05, and its verdict is at most *mixed* unless G37 also shows a dip.

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | supported | I_Q 0.26 bits [−0.04, 0.60], p 0.005, n 50 |
| [G37](goalperiod-subhypotheses/G37/README.md) | native (N1, outage) | failed | β_V1 +0.12 (rank p dip 0.87); β_V3 +0.16 (max of 38); β_V4 +0.03; one agent reached |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | failed | I_Q 0.031 [−0.024, 0.107], p 0.07, n 219 |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | descriptive | I_Q −0.025, p 1.0, n 50 |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | descriptive | I_Q 0.053 [−0.003, 0.205], p 0.20, n 51 |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | failed | I_Q −0.022, p 0.85, n 283 |
| [G51](goalperiod-subhypotheses/G51/README.md) | native (N3) + replication | descriptive | failed answers RR 1.25 [0.52, 2.42]; I_Q 0.028 [0.004, 0.057], p 0.005 |
| [NE18](goalperiod-subhypotheses/NE18/README.md) | native (N2) | mixed (inconclusive) | no first stage; β_V1 +0.055, rank p 0.11 |

## Outcome vs prediction
| # | Prediction | Observed | Verdict |
| --- | --- | --- | --- |
| P1 | V1 dips ∝ dose; rank p ≤ 0.10 | β_V1 +0.12 (+0.13 at d̄_s = 1.05); rank p (dip) 0.87; above all 5 kickoff-matched pairs | **fail**; dip ≥ 0.30 excluded (A1) |
| P2 | immediate recovery | β_rec +0.24, above the placebo 90th percentile (searchers stay high on 04-02/03) | fail (not a recovery pattern; level shift) |
| P3 | duplicates up, old refs down | V2 β −0.004 (13 duplicates in the panel; unpowered); V3 β +0.16 (largest of 38) | fail (V3 opposite) |
| P4 | first stage in every searcher | 1 of 3 searchers degraded (2,880 → 42 chars, rate 2.0 → 8.8 per 100 calls); 1 halved; 1 did not search | partial |
| P5 | re-reads rise with dose (R1) | β +6.4 per 100 calls (dose perm p 0.048; placebo rank 0.23); driven by agent 17 | partial |
| R | I_Q > 0 in ≥ 2/3 periods; pooled ≤ 0.3 bits | 2/7 periods; pooled 0.012 [−0.011, 0.035] bits | fail (first clause); pass (second) |
| N2 | NE18: V1 up with dose | no first stage (answers shorter, top searcher stopped); β +0.055, p 0.11 | inconclusive |
| N3 | G51: failed answers cost output | RR 1.25 [0.52, 2.42]; return +0.06 [−0.02, +0.13] | not consistent |

## Results
- **The outage was a one-agent scramble.** The search channel is used by few agents in regime III (three of twelve had a dose ≥ 0.25 per 100 calls). Only the top-dose agent kept searching through the outage; its answers collapsed and it retried 128 times.
- **No continuity cost.** Across agents, continuity and earlier-goal references rose with dose on the outage days, and stayed high on the recovery days. The single-agent residuals (post hoc) agree: the scrambled agent's continuity was +0.19 above its fitted level (placebo 10–90% [−0.22, +0.16]) and its commits per 20 calls +0.10 (p 0.77). Re-reads and earlier-goal references rose for that agent on the outage and recovery days alike, so they are not an outage response.
- **The channel carries little allocation information.** Pooled over 7 periods, a search answer carries 0.012 bits about the next repo. Only G36 (n 50) and G51 (n 3,954) beat the permutation floor. In G51, an answer that names the agent's own artifact precedes a return 99% of the time (vs 92%), which is query selection, not value.
- **κ input for H87:** ΔV_Q = −0.03 ± 0.51 commits per 20 calls at the mean searcher dose; I_Q = 0.012 [−0.011, 0.035] bits. κ_Q is not identified (I_Q's CI includes 0).
- **What this means.** History search is a channel agents reach for when it exists, not one they depend on. When it broke, the scrambled agent retried and then kept working from its own artifacts (H44, H58, H70). This fits R0/R1 and the HH's kill clause ("the history channel carries ≈ 0 semantic information, like memory in H15"), within the stated power.

## Faithfulness scorecard
*Round 1, 2026-10-04.*
| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Dose, continuity, duplicates, earlier-goal references and re-reads come from the ledger, DQ4 and `artifact_mentions`; KW departures listed. Regime III only; V1 depends on the repo-age rule. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Parallel trends checked through 38 placebo pairs; the dose is fixed before the outage. The searchers' level stays high on recovery days, so a dose × goal interaction is not ruled out. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Placebo pairs, kickoff-matched pairs and dose permutation sized on synthetic data; the predicted dip does not beat them, and the opposite-sign V3 rise is a level shift. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | The first-stage signature (collapsed answers, retries) appears in the logs as predicted for the reached agent; the continuity signature does not. |
| E interventional | predicts the change across a natural experiment | 1 | The outage is an involuntary scramble with a pre-set dose; the predicted dip fails. NE18 had no first stage. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Power at real counts: V1 0.85–0.91 at 0.30, 0.63–0.74 at 0.20; V3 ≥ 0.9 at 0.20; NE18 oversized (0.12–0.22). Weighted, binary-dose and leave-one-agent-out variants agree in sign. |
| G ground truth | agrees with known structure | 1 | The malfunction is documented (H56); the first stage reproduces it per agent. |
| H comparative | beats the named rivals | 1 | R0/R1 fit better than the HH model; R3 (retry cost) is rejected (no output change); R2 cannot be separated from the level shift. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | One event; NE18 is not a usable replication; NE25 (holdout) is planned, not run. |

## Confirmatory predictions (written 2026-10-04 ~20:35 UTC after round 1, before any holdout use; `analysis/confirm.py`, **not run**)
- **C1 (NE25, 2026-07-01, inside the held-out NE21+NE23 window):** search scoped to the agent's own village removes other villages' history. Dose = search calls per 100 calls on the five held-out active days before 07-01. Prediction (round-1 picture): β_V1 within the central 80% of placebo pairs on the same panel, and β_V4 within the central 80% (no continuity or output cost).
- **C2 (held-out regime-III periods #43, #45–#50, #51 tail):** pooled I_Q ≤ 0.05 bits, with I_Q > 0 (p < 0.05) in ≤ 1/2 of periods with ≥ 30 search calls.
- Overall: the round-1 picture is CONFIRMED if C1 and C2 pass.

## Caveats
- One agent was fully scrambled, for two days. The result bounds the value of search for a heavy searcher, not for the village.
- The searchers' continuity and earlier-goal references are high on the recovery days too. A dose × goal-structure interaction (#37 → #38) could mask a small dip.
- V2 (duplicates) has 13 events in the whole panel; it cannot speak.
- Search answers name repos in 27% of #51 searches and far fewer elsewhere, so I_Q measures only the repo-naming part of what search carries.
- Search failures in #51 are not exogenous (empty answers follow queries about absent things).

## Round 2 redirects (2026-10-04)
*Proposed by the round-1 agent; the coordinator may revise.*
- **Where round 1 went sideways:** the outage reached one agent fully, so the dose design had one effective treated unit.
- **H84-R1.** NE45 (2026-07-29, #51): check the search-tool schema change for a failure burst across 32 agents; if present, rerun the dose design there.
- **H84-R2.** Call-scale event study in #51: runs of failed answers per agent as dose; commits and return in the next 40 calls; agent-day placebos.
- **H84-R3.** Run `confirm.py` on NE25 after Vivian's sign-off (re-freeze if inputs change).
- **H84-R4.** Search content beyond repos: discretize answers by the goal period they cite, to measure I_Q beyond repo naming.

## Notes
- 2026-10-04 ~20:05 UTC: card written before any outcome statistic. Holdout masked with `holdout_mask` and the ledger's `holdout` flag in every script; held-out counts never printed.
- 2026-10-04 ~20:05 UTC: coordinator message received before the predictions were fixed: H70's κ_C = 5.2 [3.8, 8.4], κ_A ≈ 0, I_A = 0.14 bits; Poisson DiD and original-stratum bootstrap rules. Cited above as prior knowledge.
- 2026-10-04 20:16 UTC: **correction found after the run:** only five kickoff-matched pairs exist (#38's days 2–3 include a recovery day), so A2's minimum rank p is 1/6 = 0.17, not 1/7.
- 2026-10-04 20:25 UTC: **post hoc** single-agent ITS for agent 17 (`analysis/posthoc_single_agent.py`), added after the first stage showed only one agent was reached. Labelled post hoc wherever cited.
- 2026-10-04: NE18's verdict reads "mixed (inconclusive)" because the period verdict list has no "inconclusive".
