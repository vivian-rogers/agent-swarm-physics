# H146: Ideology egregores in #51 recruit by being read, survive their hosts' amnesia, and carry functional behaviors

**Status:** round 1 done (2026-10-09): mixed. Memeplexes survive host wipes (median HR 0.90) and re-expression is read-gated, but both are generic (matched by pseudo-patterns); recruitment unpowered as a negative; no repair; specialization at pseudo level. Card written 2026-10-09 from HH394 and HH395 after Vivian's clarification and the qualitative reading of #51. No H146 estimate on real data has been computed. Runs on H145's memeplexes (`memeplexes.json`) once H145 writes `scratchpad/H145.READY`; until then it builds its event tables and synthetic validation on the qualitative candidates, labelled post hoc.
**Fields:** sociophysics, epidemics, info theory
**Literature:** [Krakauer et al. 2020](../../literature/krakauer-2020-information-theory-of-individuality.md); [Heylighen 2016](../../literature/heylighen-2016-stigmergy-universal-coordination-mechanism.md); [Centola & Baronchelli 2015](../../literature/centola-2015-spontaneous-emergence-of-conventions.md); [Rosas et al. 2019](../../literature/rosas-2019-o-information-high-order-interdependencies.md); [Vivian's essay](../../literature/jazzloaf-2026-agent-ecologies-essay.md)
**Definitions used:** *egregore (ideology)*, conditions 2–4; *in-flight placebo (matched-lag)* (H67); *named message*; *interaction (reply, DQ2 parent)*; *O-information (field-removed)* (model 12).
**Question served:** Q1 (what couples agents), Q3, `GOALS.md`. Paper 2.

## Question
Do the ideologies of #51 behave as agents of their own: do they recruit new carriers through what those carriers read, re-occupy carriers that forgot them, and show coordinated behaviors across carriers (recruitment, repair, division of labor) that keep the pattern going?

## Model
**From:** `physics-models/03-contagion/` (adoption hazards with a read channel), `physics-models/12-information-dynamics/` (synergy across hosts), `physics-models/13-cultural-evolution-conventions/`.
- **Adoption:** agent i adopts K at bin b if it expresses K (≥ m elements) after ≥ 2 active days without expressing it. Hazard h_i,K(b) = f(R_i,K(b), U_i,K(b), N_i,K(b), Z) with R = items carrying K that i read at its read-out calls in the last 2 h (from hosts), N = the subset that name i, U = items carrying K posted in i's room but in flight at matched lag (the placebo), Z = agent × day strata, i's own past expression of K, and E (H145's bundle).
- **Re-expression after a wipe:** for a host i with a forced erasure F (or a placebo call P at call 20 of a segment), the time to i's next expression of K; split by whether i read K-carrying items or re-read a K artifact in calls 1–10.
- **Functional behaviors:**
  - *recruitment acts:* named messages from hosts of K to non-hosts that carry K; their effect on the target's adoption vs unnamed reads;
  - *repair:* named messages carrying K from other hosts to host i in the 2 h after i's forced erasure, a challenge (an opposing DQ2 reply to i's K statement), or a lapse (i drops K for ≥ 1 day), vs matched placebo times;
  - *division of labor:* element specialization (hosts' element-expression profiles within K more distinct than a within-K permutation of elements across hosts) and O-information Ω/(n−2) across hosts on K's elements, after regression on e1–e3 and leave-one-out means.

## Data scheme (`scheme/`)
- **Inputs:** H145's `elements.parquet`, `expr/`, `memeplexes.json` (or the qualitative candidates as element lists fixed in `candidates_story.json` before any statistic); `context_ledger_items` (read-out items; `uncertain` with and without), `context_ledger_turns` (`reset_forced`, call index, room), `chat_core`, `chat_mentions_clean` (named), `reply_pairs` / `reply_stance_v2` (opposes), `project_calls.proj` (touch-based; never `label`), `work_commits` (cleaned as H145), `roster`, `rooms_timeline`.
- **Item coding:** each chat item is coded with the K elements its statement and markers carry (H145's element map), in memory; only codes are stored.
- **Events:** adoptions; forced erasures F and placebo calls P of hosts (agent × unit strata); challenges; lapses; newcomer arrivals (07-09 GPT-5.6 trio, 07-10 Grok 4.5, 07-17 Kimi K3, 07-24 Claude Opus 5, 08-28 GLM-5.3 Flash, 09-01 Claude Fable 5.1, 09-03/04 NE33).
- **Output:** `data/processed/H146-egregore-recruitment-behaviors-51/` (`events/`, `results/`, `synthetic/`, `_provenance.json`).
- **Span:** 07-06 → 09-04; 51m masked; frozen `analysis/confirm.py`, dry-run only.

## Observables
O1 read-gated adoption: log-OR of adoption per K-carrying read vs per in-flight K item at matched lag (stratified on after-lag × before-message age, H54 trap), and per named vs unnamed read. O2 newcomers: the share of a newcomer's first-2-day expression on each K, against what it read, read vs in-flight. O3 re-expression after a wipe: hazard ratio F vs P; read-gated vs not. O4 recruitment acts: the target's adoption hazard after a named K message from a host vs an unnamed K read. O5 repair: the rate of named K messages from other hosts to host i after a wipe, challenge or lapse vs placebo times; the time to i's re-expression with vs without repair. O6 specialization and Ω across hosts per K.

## Null / baseline
In-flight items at matched lag (convergence); frequency-matched pseudo-patterns from H145 (every statistic is also computed on them; an egregore must beat them); placebo calls and placebo times at matched segment position or time of day; within-K element permutations (specialization); constraint-preserving surrogates for Ω (keep each host's marginals and per-bin counts); the agent-day cluster bootstrap with 1-h blocks.

## Faithfulness scorecard
Scored per model, mapping and window; 0/1/2. Thresholds: `writeup/papers/thermodynamics/sections/method.tex`.
**Rival models:** W_convergence (agents reach the same ideas from shared inputs: read = in-flight), W_field (adoption follows role texts and operator topics), W_hub (adoption is replying to one prolific agent: effect only for its items), W_egregore (read-gated adoption, repair and specialization beyond pseudo-patterns).
**Reserved data:** 51m.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | adoption, read-out items, wipes and replies from the ledgers | 1 | Round 1: ledger reads, wipes, replies direct; hosts from H145's panel; candidates post hoc regex |
| B assumptions | hazard proportionality; matched lag and before-age; one adoption per agent-pattern-lapse | 1 | Round 1: matched lag and before-age bins; proportionality untested |
| C adequacy | read > in-flight beyond pseudo-patterns | 0 | Round 1: no pattern beats its pseudo-patterns (P1b, P4, P5) |
| D unfitted predictions | repair and specialization are not used to define memeplexes | 1 | Round 1: repair and specialization computed, both at pseudo level |
| E interventional | NE41 wipes; newcomer arrivals (NE33 and earlier joins) | 1 | Round 1: NE41 wipes used; NE33 untestable |
| F identifiability | synthetic contagion, convergence and hub worlds on the real ledger; size ≤ 0.10 | 1 | Round 1: size ≤ 0.06 on each skeleton; P1b power ≤ 0.53 |
| G ground truth | named reads stronger than unnamed (paper 1: ×19 for talk) | 1 | Round 1: named > unnamed in 7/15, also at pseudo level |
| H comparative | W_egregore vs W_convergence vs W_hub vs W_field | 1 | Round 1: convergence and hub rejected for the read effect; egregore not separated from generic vocabulary |
| I transfer | 51m (not run) | 0 | Round 1: 51m not run (confirm.py dry-run) |

## Prediction
*Written 2026-10-09, before running the analysis on real data.*

| | Card's prediction (operational) | Falsified if | My prior |
| --- | --- | --- | --- |
| **P1** read-gated adoption | log-OR(read − in-flight) > 0 (CI above 0) for ≥ 2 memeplexes, and larger than for their pseudo-patterns | CI includes 0 for all, or pseudo-patterns as large | 0.55 |
| **P2** names recruit | the named-read effect exceeds the unnamed-read effect (ratio ≥ 3) for patterns that pass P1 | ratio ≤ 1 | 0.6 |
| **P3** newcomers are recruited | newcomers' first-2-day expression follows what they read (read > in-flight) for ≥ 1 pattern; the byte game and onboarding patterns absorb newcomers first | newcomers adopt patterns at their in-flight rate | 0.5 |
| **P4** survives amnesia | after a host's forced wipe, its re-expression hazard is ≥ 0.8 of the placebo hazard, and read-gated re-expression is faster than not | ratio < 0.5 (the pattern lived in the host's context) | 0.65 |
| **P5** repair | named K messages to a host rise after its wipe, challenge or lapse vs placebo (rate ratio > 1.2, CI above 1) for ≥ 1 pattern | ratio ≤ 1 for all | 0.3 |
| **P6** division of labor | element specialization above the permutation null (z ≥ 2) for ≥ 2 patterns; Ω/(n−2) < 0 after field removal for ≥ 1 | no specialization beyond permutation | 0.5 (specialization), 0.25 (Ω < 0) |

**Kill rules.** (K1) If P1 fails with power ≥ 0.8 at a planted log-OR of 0.3, the ideologies spread by convergence, not by reading: they are fields. (K2) If P4's ratio is < 0.5, the pattern is held in hosts' contexts, not above them: it fails condition 2. (K3) If no functional behavior (P5, P6) beats pseudo-patterns, the patterns are passive memes, not egregores.

**Overall prior.** I expect read-gated recruitment for a few patterns, carried mostly by named messages (paper 1's strongest result), survival of amnesia (artifacts and other hosts re-supply the pattern), some specialization, and little evidence of repair. The likely verdict is "recruiting memes with a division of labor, no measured homeostasis".

**Synthetic validation (axis F), before real data.** On the real #51 ledger (who read what, when): W_convergence (adoption from a shared field timed with the items, no read effect), W_contagion (read K items raise adoption, log-OR 0.3 and 0.6, named ×3), W_hub (only one agent's items act), W_repair (hosts address a lapsed host with probability r). Size ≤ 0.10 and power reported for each test.

## Impostors
| Impostor | How handled | Status (planned) |
| --- | --- | --- |
| Scheduler field | agent × day strata; matched lag; placebo times at matched time of day | removed |
| Exogenous field | E in every model; operator and relayed human items coded as exogenous, not as host items | removed |
| Shared model priors | agent strata; cross-lab adoption reported separately | partly |
| Contemporaneous convergence | in-flight items at matched lag with before-age strata (the primary contrast) | removed |

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G51](goalperiod-subhypotheses/G51/README.md) | exploratory | mixed | P1b CI > 0 in 2/15 memeplexes, 0 beyond pseudo (power ≤ 0.53); P5 RR ≤ 1.07; z_spec at pseudo level |
| [NE41](goalperiod-subhypotheses/NE41/README.md) (host wipes) | native | mixed | wipe HR median 0.90 (0.78–1.11), read-gate HR 1.2–2.3, both at pseudo level; repair RR 0.95–1.07 |
| [NE33](goalperiod-subhypotheses/NE33/README.md) (newcomers 09-03/04, plus earlier joins) | native | descriptive | untestable (power ≤ 0.15); first pattern K09 for 5/11 |
| 51m (reserved) | confirmatory | not run | |

## Results
See "Round 1 (2026-10-09)" below: survival of amnesia supported but generic; recruitment inconclusive; no repair; specialization at pseudo level.

## Round 1 (2026-10-09)
*Written by the H146 agent. Everything in this section above "Real data" was written and committed before any H146 estimate on real data. The per-pattern power checks use each pattern's real skeleton (item coding, exposures, at-risk rows, event counts, wipe and placebo events) with planted outcomes; they compute no estimate of a real effect.*

### Inputs and instruments
- **Event tables** (`scheme/build.py`, commit e57574f): 41,844 chat items, 928,207 calls, 69,048 statements, 40,956 talk rows with ≥ 1 own chat item, 26,733 matched-lag window items (mirror read / in flight), 930,398 read-out items, 129,499 project touches (`proj`, never `label`), 14,547 forced erasures F and 19,466 placebo calls P (ctx_pos 20, no reset in the next 10 calls, not first of day), 22,496 DQ2 parent replies (1,742 DQ2 opposes, 183 DQ10 validated disagreements), 11 newcomers (07-09 GPT-5.6 trio … 09-03/04 NE33). 51m is absent by construction (asserted). The tables use no commits, so the `clean_commits` fix (4f6ab2e) does not touch them.
- **Pattern sets.** Primary: H145's memeplexes (`memeplexes.json`), coded through H145's frozen element map (`analysis/coding_h145.py`: H145's own agent × 2-h expression panel for hosts; cluster, marker and repo/project elements on chat items and statements). Comparison, **post hoc**: the eight qualitative candidates fixed in `scheme/candidates_story.json` before any statistic (regex terms on text in memory, plus practice repos; all-hours 2-h bins, no presence trim).
- **Pseudo-patterns** (both sets): random element sets from H145's element pool, each element matched in agent-bin count (±25%) and agent count (±1), widened in recorded steps when no match is free.

### Amendment A1 (2026-10-09, before real data; from the synthetic checks below, not post hoc)
- **A1.1 Adoption rule.** Agent i adopts K in 2-h bin b if it is a host of K in b (≥ m = 2 elements) after ≥ 2 active days with no host bin. The adoption call is the first talk row in b whose own chat carries ≥ 1 K element. Rows of i are at risk during the spell, up to and including the adoption call. Adoption bins without such a row are dropped and counted.
- **A1.2 P1b, expression response (amended P1).** The adoption design has power ≤ 0.28 at log-OR 0.3 even with 400 adoptions (table S1). P1b keeps the same contrast on more events: risk set = talk rows of agents with no host bin of K earlier that PT day; outcome = the row's own chat carries ≥ 1 K element. Same fit: conditional Poisson with agent × day strata, exposures read in the mirror window (Rm), in flight at matched lag (P), read at the call before the mirror (Rc_rest), read at earlier calls in 2 h (R2h); controls log density, all-item read and in-flight counts, lag and before-age bins; ridge 0.5; 1-h-block cluster sandwich. δ = β_Rm − β_P. P1 (adoption) and P1b are both reported; the verdict table names which one is used.
- **A1.3 Untestability rule, per pattern.** Before its estimate, each pattern's own skeleton is run with planted outcomes (`analysis/power146.py`). A kill rule applies to a pattern only where that power is ≥ 0.8 at the card's effect size: P1/P1b and P3 at log-OR 0.3; P4 read-gating at a hazard ratio 2 after call 10; each P5 subtest at a rate ratio 1.5. Below 0.8, a null result is "inconclusive" and only a positive can count. P1/P1b positives need size ≤ 0.10 on the same skeleton (100 null replicates).
- **A1.4 Relayed human input.** No message-level relay classifier exists (H143's A0.2 rule was never built). Robustness fit P1b_nofable drops every Claude Fable 5 item from host exposures (conservative).
- **A1.5 Pseudo-pattern rule.** 30 pseudo-patterns per pattern (not 200, for cost). "Beats its pseudo-patterns" = p_pseudo = (1 + #{pseudo ≥ K}) / 31 ≤ 0.05 on the point estimate (for Ω: ≤). Pseudo-patterns get point estimates only (no bootstraps).
- **A1.6 P2 ratio.** Excess-rate ratio (e^δ_named − 1)/(e^δ_unnamed − 1), with δ = read − in flight. Pass: ratio ≥ 3 and z(δ_named − δ_unnamed) ≥ 1.96 (or δ_unnamed ≤ 0 < δ_named with δ_named's CI above 0). Falsified: δ_named ≤ δ_unnamed. Only for patterns that pass P1 or P1b.
- **A1.7 P4.** HR = Mantel–Haenszel rate ratio (agent × unit strata) of the host's first K statement per follow-up call, calls 1–20 after the event (truncated at the next reset or day end), F vs P; agent-day cluster bootstrap, B = 300. Hosts = host of K in a bin before the event within its previous 2 active days. Read-gating: landmark at call 10, events without re-expression by call 10; R+ = read ≥ 1 K-carrying item at calls 1–10 or touched a K practice project; HR(R+ vs R−) with the CI above 1 = "read-gated re-expression is faster".
- **A1.8 P5.** Count of named K-carrying messages from other hosts to host i in the 2 h after the event. Subtests: wipe (F vs P host events); challenge (DQ10 validated disagreement, and DQ2 opposes) vs neutral replies to i's K-carrying message (the reply itself not counted); lapse (host on active day k, not on k + 1; window = first 2 h of day k + 2) vs continuing hosts, strata agent × activity tercile. Pass per subtest: RR > 1.2 and CI above 1; K3 also needs p_pseudo ≤ 0.05.
- **A1.9 P6 O-information.** The card's sign rule (Ω/(n−2) < 0 after field removal) has size 0.67–1.0 in no-coupling and field worlds (table S3): Gaussian Ω on binary host indicators, and the plug-in discrete Ω, are negative under independence. Amended rule: discrete Ω/(n−2) (Miller–Madow) < 0 **and** below the 5th percentile of 100 curveball surrogates (each host's host-bin count and each bin's host count kept). The Gaussian field-removed Ω is reported only. Hosts: the ≤ 8 most frequent hosts with ≥ 10 host bins; bins where all are present.
- **A1.10 P6 specialization.** I(host; element) over host-element triples in bins with ≥ 2 hosts; null = within-bin permutation of the hosts' element sets (keeps each bin's sets and each host's bins); Besag–Clifford stop at 10 exceedances or 200 draws; pass z ≥ 2.

### Synthetic validation (axis F)
Real skeletons, planted truth. Scripts: `analysis/synthetic_p1.py`, `analysis/synthetic_p456.py`; output `data/processed/H146-…/synthetic/`. Seeds fixed.

**S1. P1 read vs in flight** (all 40,956 talk rows; 100 null and 60 power replicates per cell; "rej" = z(δ) > 1.96; q0 = share of items carrying K):

| Design | World | Events | rej, q0 0.04 | rej, q0 0.12 |
| --- | --- | --- | --- | --- |
| adoption | convergence, slow field (5–60 min) | 150 / 400 | 0.02 / 0.02 | 0.01 / 0.02 |
| adoption | convergence, fast field (0.5–3 min) | 150 / 400 | 0.00 / 0.05 | 0.02 / 0.04 |
| adoption | contagion β 0.3 | 150 / 400 | 0.08 / 0.08 | 0.12 / 0.28 |
| adoption | contagion β 0.6 | 150 / 400 | 0.23 / 0.23 | 0.20 / 0.50 |
| expression | convergence slow / fast | 1,500 | 0.02 / 0.03 | 0.00 / 0.02 |
| expression | no effect (β 0) | 1,500 | 0.04 | 0.01 |
| expression | contagion β 0.3 | 500 / 1,500 / 4,000 | 0.08 / 0.10 / 0.38 | 0.20 / 0.35 / 0.78 |
| expression | contagion β 0.6 | 500 / 1,500 / 4,000 | 0.22 / 0.62 / 0.92 | 0.48 / 0.78 / 0.97 |
| expression | hub only (β 0.6); no-hub refit | 1,500 | 0.13; no-hub δ 0.02, rej 0.03 | 0.17; no-hub δ −0.05, rej 0.00 |
| expression | named ×3 on β 0.3: P2 ratio ≥ 3 | 1,500 | 0.83 of replicates (ratio ≤ 1: 0.00) | 0.97 (0.00) |

Size of the read − in-flight contrast is ≤ 0.05 in every convergence world with ≥ 150 events (0.08–0.11 at 50 events, where < 16% of replicates are estimable). Bias is toward 0 (−0.05 to −0.29 at β 0.6): read exposures at the call outside the mirror window absorb part of the planted effect. The no-hub refit separates W_hub from contagion. **The adoption design cannot reach power 0.8 at log-OR 0.3 at any event count a pattern can supply.**

**S2. P4 and P5** (real F/P skeleton; 100 replicates):

| Test | Planted | n events | Result |
| --- | --- | --- | --- |
| P4 HR F vs P | r = 1 | 300 / 1,500 | HR 1.06 / 0.99; 95% coverage 0.95 / 0.94; share HR ≥ 0.8: 0.87 / 1.00; share HR < 0.5: 0.00 / 0.00 |
| P4 HR F vs P | r = 0.8 | 300 / 1,500 | HR 0.85 / 0.81; coverage 0.96 / 0.96; share HR < 0.5: 0.03 / 0.00 |
| P4 HR F vs P | r = 0.5 (K2 world) | 300 / 1,500 | HR 0.54 / 0.50; share HR < 0.5: 0.46 / 0.48 |
| P4 read-gating, CI above 1 | g = 1 / g = 2 | 1,500 | 0.05 / 0.85 (at 300: 0.05 / 0.07) |
| P5 rule (RR > 1.2, CI above 1) | RR 1 / 1.5 / 2 | 300 + 300 | 0.01 / 0.48 / 0.87 |
| P5 rule | RR 1 / 1.5 / 2 | 1,500 + 1,500 | 0.04 / 1.00 / 1.00 |
| P5 rule | RR 1 / 1.5 / 2 | 20 + 200 | 0.06 / 0.08 / 0.11 |

K2 (HR < 0.5) is a point-estimate rule: it fires in about half of the K2-world replicates and in ≤ 3% of replicates with r ≥ 0.8.

**S3. P6** (real presence of the 8 most active agents; specialization 100/50 replicates, Ω 60 replicates on 172 all-present bins of 6 hosts):

| Test | World | Result |
| --- | --- | --- |
| specialization z ≥ 2 | no coupling / shared field | 0.04 / 0.05 |
| specialization z ≥ 2 | host-specific element mix λ 0.2 / 0.5 | 0.80 / 0.98 |
| Ω card rule (Gaussian, field-removed, < 0) | no coupling / field / fixed budget / XOR | 0.67 / 1.00 / 0.00 / 0.60 |
| Ω discrete < 0 | all four worlds | 0.95–1.00 |
| Ω amended rule (A1.9) | no coupling / field / fixed budget / XOR triplet | 0.08 / 0.05 / 0.08 / 1.00 |

**S4. Per-pattern power on the real skeletons** (`results/power_candidates.json`; the post hoc candidates; H145's memeplexes get the same check when `memeplexes.json` is final):

| Candidate | Hosts (host bins) | Adoptions; P1 power β 0.3 | P1b events; read-exposed rows; power β 0.3 / 0.6; size | P3 events; power β 0.3 | P4 F; read-gate power | P5 power at RR 1.5: wipe / DQ2 / DQ10 / lapse |
| --- | --- | --- | --- | --- | --- | --- |
| verification | 28 (990) | 61; 0.02 | 5,190; 1,200; 0.20 / 0.50; 0.04 | 312; 0.03 | 7,231; 1.00 | 1.00 / 1.00 / 0.87 / 0.63 |
| protections | 24 (378) | 66; 0.07 | 1,950; 566; 0.40 / 0.40; 0.02 | 64; 0.00 | 4,991; 1.00 | 1.00 / 0.97 / 0.27 / 0.25 |
| welfare | 25 (745) | 50; 0.17 | 2,941; 1,123; 0.07 / 0.03; 0.06 | 64; 0.00 | 5,249; 1.00 | 1.00 / 1.00 / 0.27 / 0.48 |
| governance | 20 (452) | 41; 0.00 | 1,584; 624; 0.23 / 0.73; 0.06 | 15; 0.00 | 4,317; 1.00 | 1.00 / 0.97 / 0.25 / 0.38 |
| onboarding | 27 (342) | 49; 0.00 | 886; 188; 0.12 / 0.23; 0.00 | 105; 0.00 | 3,058; 0.85 | 1.00 / 0.50 / 0.08 / 0.13 |
| relay | 27 (306) | 56; 0.05 | 1,877; 449; 0.08 / 0.13; 0.03 | 108; 0.03 | 4,153; 0.98 | 1.00 / 0.98 / 0.35 / 0.27 |
| byte game | 19 (152) | 27; 0.00 | 710; 234; 0.15 / 0.87; 0.00 | 122; 0.00 | 1,611; 0.60 | 1.00 / 0.50 / 0.08 / 0.18 |
| Echoes | 25 (871) | 35; 0.02 | 2,496; 1,209; 0.57 / 0.67; 0.05 | 86; 0.12 | 5,823; 1.00 | 1.00 / 1.00 / 0.30 / 0.43 |

**S5. Per-pattern power on H145's 15 frozen memeplexes** (`results/power_h145.json`; `memeplexes.json` md5 9b899c34, frozen 2026-10-09 18:12 UTC; H145 coding):

| Memeplex (H145 label) | Elements | Hosts (host bins) | Adoptions; P1 power β 0.3 | P1b events; read-exposed rows; power β 0.3 / 0.6; size | P3 events; power β 0.3 | P4 F; read-gate power | P5 power at RR 1.5: wipe / DQ2 / DQ10 / lapse |
| --- | --- | --- | --- | --- | --- | --- | --- |
| K01 (verify) | 68 | 31 (1,189) | 61; 0.00 | 2,613; 824; 0.53 / 0.97; 0.04 | 170; 0.10 | 10,372; 1.00 | 1.00 / 1.00 / 0.42 / 0.73 |
| K02 (verify) | 37 | 26 (359) | 62; 0.00 | 1,395; 363; 0.08 / 0.03; 0.03 | 53; 0.00 | 4,476; 0.98 | 1.00 / 0.80 / 0.28 / 0.30 |
| K03 (governance) | 187 | 31 (1,299) | 55; 0.13 | 3,244; 1158; 0.43 / 0.57; 0.03 | 141; 0.00 | 11,173; 1.00 | 1.00 / 1.00 / 0.70 / 0.82 |
| K04 (unlabelled) | 64 | 31 (1,020) | 57; 0.00 | 2,620; 819; 0.20 / 0.13; 0.05 | 102; 0.00 | 10,072; 1.00 | 1.00 / 1.00 / 0.50 / 0.77 |
| K05 (echoes) | 41 | 22 (307) | 46; 0.00 | 1,743; 366; 0.17 / 0.57; 0.04 | 50; 0.15 | 3,481; 0.88 | 1.00 / 0.68 / 0.10 / 0.28 |
| K06 (frameworks) | 70 | 27 (608) | 55; 0.00 | 2,255; 677; 0.02 / 0.07; 0.00 | 166; 0.00 | 6,027; 1.00 | 1.00 / 0.97 / 0.28 / 0.43 |
| K07 (frameworks) | 82 | 31 (655) | 68; 0.00 | 1,935; 501; 0.17 / 0.23; 0.01 | 72; 0.00 | 7,108; 1.00 | 1.00 / 1.00 / 0.25 / 0.68 |
| K08 (unlabelled) | 129 | 27 (679) | 62; 0.05 | 2,008; 624; 0.35 / 0.50; 0.01 | 55; 0.02 | 7,312; 1.00 | 1.00 / 1.00 / 0.32 / 0.48 |
| K09 (unlabelled) | 116 | 32 (1,399) | 64; 0.10 | 3,481; 1278; 0.32 / 0.53; 0.04 | 317; 0.00 | 10,026; 1.00 | 1.00 / 1.00 / 0.53 / 0.67 |
| K10 (unlabelled) | 31 | 23 (226) | 49; 0.00 | 1,052; 292; 0.05 / 0.00; 0.01 | 38; 0.00 | 3,780; 0.97 | 1.00 / 0.82 / 0.08 / 0.20 |
| K11 (frameworks) | 51 | 24 (470) | 66; 0.00 | 2,631; 659; 0.32 / 0.67; 0.05 | 46; 0.00 | 5,819; 1.00 | 1.00 / 1.00 / 0.17 / 0.63 |
| K12 (welfare) | 153 | 32 (2,352) | 38; 0.00 | 4,869; 1871; 0.30 / 0.60; 0.01 | 268; 0.10 | 13,049; 1.00 | 1.00 / 1.00 / 0.72 / 0.62 |
| K13 (unlabelled) | 140 | 32 (1,747) | 37; 0.03 | 4,307; 1518; 0.33 / 0.43; 0.06 | 164; 0.00 | 12,436; 1.00 | 1.00 / 1.00 / 0.77 / 0.83 |
| K14 (unlabelled) | 4 | 5 (15) | 10; 0.00 | 78; 17; 0.00 / 0.00; 0.00 | 2; 0.00 | 427; 0.08 | 0.30 / 0.08 / – / 0.00 |
| K15 (frameworks) | 45 | 18 (179) | 47; 0.00 | 1,252; 172; 0.28 / 0.43; 0.01 | 32; 0.00 | 2,648; 0.78 | 1.00 / 0.70 / 0.22 / 0.22 |

K14 (4 markers, 5 hosts in H146's coding, 15 host bins) is too small for every test.

### Declared before any estimate (untestability rule, A1.3)
- **P1 (adoption) and P1b: K1 cannot fire** for any candidate or memeplex. Memeplexes: power at log-OR 0.3 ≤ 0.13 (adoption) and ≤ 0.53 (P1b; K01 0.53, K03 0.43, all others ≤ 0.35); size ≤ 0.06. Candidates: Power at log-OR 0.3 is ≤ 0.17 (adoption) and ≤ 0.57 (P1b), because only 102–1,209 at-risk rows per pattern hold a K item in the mirror window. Only a positive can count; a null is "inconclusive". Size on the same skeletons is ≤ 0.06.
- **P3 (newcomers): untestable** (power ≤ 0.15; 2–317 events in newcomers' first two active days). Reported as descriptive only.
- **P2:** conditional on P1/P1b; computed only for patterns that pass.
- **P4:** the HR is identified for every candidate (1,611–7,231 host wipes; in the survival world the share with HR ≥ 0.8 is ≥ 0.98, in the K2 world about half fall below 0.5). Read-gating is powered (≥ 0.85) for all candidates except the byte game (0.60).
- **P5 (memeplexes):** wipe powered for all but K14 (1.00); DQ2 challenge powered for 12 of 15 (not K05, K15, K14); DQ10 challenge unpowered for all (≤ 0.77); lapse powered for K03 and K13 only (0.82, 0.83). **P4 (memeplexes):** read-gating powered for all but K15 (0.78) and K14.
- **P5 (candidates):** the wipe subtest is powered for all candidates (1.00). The DQ2-challenge subtest is powered for 6 of 8 (not onboarding, byte game: 0.50). The DQ10-challenge subtest is powered only for verification (0.87). The lapse subtest is unpowered for all (≤ 0.63).
- **P6:** specialization power 0.80 at λ 0.2 (generic skeleton); Ω uses the amended rule A1.9.

### Cost (measured)
- Event tables load in 0.7 s; the H145 coding builds in 9 s; the candidate coding in about 20 s.
- One P1/P1b fit: 0.03–0.04 s (41k rows, conditional Poisson, closed-form Newton steps). Per-pattern power stage: 45–60 s.
- The estimate stage runs the full statistics once per pattern (bootstraps B = 300, 200 permutations, 100 surrogates) and point estimates on 30 pseudo-patterns.
- Measured afterwards: the estimate stage takes about 1 s per pattern and 7–9 s for its 30 pseudo-patterns (15 memeplexes: 138 s in all).

### Real data (exploration, #51 07-06 → 09-04; 51m and #45–#50 not read)
Results: `data/processed/H146-…/results/real_h145.json`, `real_candidates.json`, `verdicts_*.json` (rules applied by `analysis/evaluate.py`). The candidate estimates were run after commit 6081c11 (their power declarations) and before H145.READY; their pseudo-patterns and all memeplex estimates after H145.READY and after commit 11e1bcf. Figure: `figures/r1_obs.pdf`.

**Per memeplex (H145, K14 omitted from the table: 4 elements, 15 host bins).** δ = read − in-flight log rate ratio (P1b, 95% CI); p_ps = p against 30 pseudo-patterns; HR = re-expression after a forced wipe vs placebo (calls 1–20); read-gate = HR of re-expression after call 10, read-supplied vs not (F events); RR = named K messages from other hosts in 2 h after a wipe vs placebo; z_spec = host-element specialization vs within-bin permutation.

| K (H145 label) | P1b δ [CI]; p_ps | P4 HR [CI] | read-gate HR [CI] | P5 wipe RR [CI] | z_spec; p_ps | Ω/(n−2) vs surrogate p05 |
| --- | --- | --- | --- | --- | --- | --- |
| K01 verify | 0.18 [−0.07, 0.42]; 0.19 | 0.89 [0.81, 0.96] | 1.58 [1.27, 1.90] | 0.98 [0.97, 1.00] | 63; 0.32 | −0.185 vs −0.255 |
| K02 verify | 0.59 [0.12, 1.05]; 0.06 | 0.89 [0.79, 1.04] | 1.39 [0.96, 2.06] | 0.98 [0.93, 1.01] | 15; 0.45 | −0.033 vs −0.105 |
| K03 governance | 0.01 [−0.15, 0.16]; 0.77 | 0.94 [0.87, 1.02] | 1.63 [1.25, 2.10] | 0.99 [0.97, 1.00] | 49; 1.00 | −0.164 vs −0.209 |
| K04 – | −0.05 [−0.23, 0.13]; 0.81 | 0.93 [0.86, 1.02] | 1.25 [1.02, 1.55] | 0.97 [0.96, 1.00] | 34; 0.65 | −0.242 vs −0.246 |
| K05 echoes | 0.34 [0.15, 0.52]; 0.35 | 0.91 [0.76, 1.12] | 0.99 [0.45, 2.04] | 1.00 [0.96, 1.05] | 17; **0.03** | −0.056 vs −0.094 |
| K06 frameworks | 0.00 [−0.22, 0.23]; 0.81 | 0.78 [0.67, 0.92] | 1.21 [0.70, 1.91] | 0.95 [0.91, 0.99] | 35; 0.13 | −0.085 vs −0.162 |
| K07 frameworks | 0.20 [−0.01, 0.42]; 0.39 | 0.82 [0.72, 0.93] | 1.41 [0.98, 1.99] | 1.00 [0.96, 1.03] | 28; 0.94 | −0.111 vs −0.170 |
| K08 – | 0.09 [−0.11, 0.30]; 0.55 | 0.87 [0.78, 0.96] | 1.69 [1.25, 2.15] | 0.98 [0.96, 1.00] | 30; 1.00 | −0.034 vs −0.139 |
| K09 – | 0.08 [−0.06, 0.23]; 0.42 | 0.83 [0.77, 0.90] | 1.45 [1.10, 1.89] | 0.99 [0.98, 1.01] | 88; 0.13 | −0.057 vs −0.127 |
| K10 – | −0.04 [−0.44, 0.37]; 0.68 | 0.81 [0.66, 1.00] | 2.32 [1.18, 4.45] | 1.05 [0.97, 1.13] | 9; 0.58 | −0.027 vs −0.038 |
| K11 frameworks (field-seeded) | 0.16 [−0.03, 0.35]; 0.42 | 0.95 [0.84, 1.08] | 1.58 [1.08, 2.30] | 1.00 [0.97, 1.03] | 21; 0.45 | −0.089 vs −0.142 |
| K12 welfare | 0.04 [−0.05, 0.13]; 0.55 | 0.95 [0.89, 1.00] | 1.35 [1.03, 1.77] | 1.00 [0.99, 1.01] | 153; 0.94 | −0.042 vs −0.052 |
| K13 – | −0.00 [−0.11, 0.10]; 0.97 | 0.92 [0.87, 0.99] | 1.46 [1.19, 1.83] | 0.99 [0.98, 1.01] | 83; 0.71 | −0.139 vs −0.178 |
| K15 frameworks | 0.42 [−0.30, 1.14]; 0.42 | 1.11 [0.84, 1.38] | 2.34 [1.25, 3.97] | 1.07 [0.97, 1.12] | 12.5; **0.03** | −0.003 vs −0.035 |

**Pseudo-patterns (the null), pooled over all memeplexes (450 sets):** P1b δ median 0.09 (IQR 0.00–0.20; 75% > 0); wipe HR median 0.89 (5–95%: 0.77–1.01); specialization z median 34 (100% ≥ 2); wipe RR median 0.99. **Post hoc** (`analysis/posthoc_r1.py`, 30 new pseudo-patterns per pattern): read-gate HR median 1.39 over 422 pseudo-patterns (98% > 1); no memeplex beyond its pseudo-patterns (p_ps 0.07–1.0).

**Candidates (POST HOC, regex coding):** P1b CI above 0 for verification 0.27 [0.13, 0.41], protections 0.29 [0.07, 0.51], governance 0.24 [0.04, 0.44], onboarding 0.79 [0.28, 1.29], relay 0.33 [0.05, 0.61]; none beyond pseudo (p_ps 0.13–0.52; candidate pseudo median 0.19). Named > unnamed (z ≥ 1.96) with ratio ≥ 3 for protections (6.2) and governance (8.0). HR 0.81–1.19; read-gate CI above 1 for protections, governance, relay, Echoes (post hoc pseudo: relay alone p_ps 0.03). Wipe RR 0.93–1.03; DQ2-challenge RR 0.56–1.38, none passing. z_spec beyond pseudo for onboarding and the byte game only. Ω rule met for none. Newcomers: 9 of 11 express onboarding first.

### Prediction vs result
| # | Prediction (rule) | Result | Verdict |
| --- | --- | --- | --- |
| P1 | read − in-flight > 0 (CI above 0) for ≥ 2 patterns, beyond pseudo | Adoption design: estimable for 3 of 15 memeplexes, CI above 0 for none. P1b: CI above 0 for K02 (0.59 [0.12, 1.05]) and K05 (0.34 [0.15, 0.52]); neither beyond pseudo (p_ps 0.06, 0.35); K02 loses its CI in the no-hub refit (0.47 [−0.13, 1.07]); K05 keeps it (0.35 [0.15, 0.55]). Pseudo-patterns show the same effect (median 0.09). | **not supported; inconclusive** (power ≤ 0.53 at log-OR 0.3: K1 cannot fire) |
| P2 | named ≥ 3× unnamed, for P1 passes | No pattern passes P1. Descriptive: named − unnamed CI above 0 in 7 of 15 memeplexes; pseudo-patterns show it too | **n/a** |
| P3 | newcomers follow reads | 2–317 events; estimable for 3 memeplexes, all CIs include 0. Descriptive: first pattern expressed is K09 for 5 of 11 newcomers; onboarding (post hoc) for 9 of 11 | **untestable** (descriptive) |
| P4 | wipe HR ≥ 0.8; read-gated faster; K2 if HR < 0.5 | HR median 0.90 over 14 memeplexes (range 0.78–1.11; K06 0.78 [0.67, 0.92] the only one < 0.8); K2 fires for none. Read-gate CI above 1 for 10 of 15 (HR 1.21–2.34). Both are at pseudo level (post hoc for read-gating) | **supported as written; not pattern-specific** |
| P5 | repair RR > 1.2, CI above 1, for ≥ 1 pattern | Wipe RR 0.95–1.07 (powered for 14): 0 pass. DQ2-challenge RR 0.64–0.97 (powered for 12): 0 pass. Lapse RR 0.14–0.88 (powered for K03, K13: 0.45, 0.59): 0 pass | **failed** (ratio ≤ 1.07 for all) |
| P6 | specialization z ≥ 2 for ≥ 2; Ω rule for ≥ 1 | z 9–153 for all 14 vs permutation, but pseudo-patterns give z 34 (median): only K05 and K15 beyond pseudo, each at the minimum attainable p_ps 0.032 (2 of 14 by chance: P ≈ 0.07). Ω amended rule met for 0 of 14 | **specialization: met literally, at pseudo level; Ω: failed** |

**Kill rules.** K1 cannot fire (unpowered; A1.3). K2 does not fire (no HR < 0.5). K3 does not fire literally: K05 and K15 beat their pseudo-patterns on specialization. Two hits in 14 at the minimum attainable p are consistent with chance (P ≈ 0.07), so K3 is read as **not resolved**: no functional behavior is resolved beyond pseudo-patterns.

### Impostors (filled in)
| Impostor | How handled | Status |
| --- | --- | --- |
| Scheduler field | agent × day strata; matched lag; 1-h blocks; placebo calls at ctx_pos 20 | removed |
| Exogenous field | only agent-kind items are exposures; Claude Fable 5 items dropped in P1b_nofable (K05 lower CI 0.16; K02 0.12) | partly (no relay classifier) |
| Shared model priors | agent strata; specialization equals the pseudo-pattern level (agents keep their own vocabulary) | not removed for P6; this impostor explains the specialization |
| Contemporaneous convergence | in-flight items at matched lag; synthetic size ≤ 0.05 in fast and slow field worlds | removed for P1b; the residual read effect is generic (pseudo median 0.09) |
| Hub (W_hub) | no-hub refit | K02 explained by the hub; K05 not |

### Faithfulness scorecard (round 1)
| Axis | Score | Evidence |
| --- | --- | --- |
| A mapping | 1 | ledger reads, wipes and replies are direct; hosts from H145's panel; candidates are post hoc regex |
| B assumptions | 1 | matched lag and before-age bins in place; hazard proportionality not tested |
| C adequacy | 0 | no pattern beats its pseudo-patterns on P1b, P4 or P5 |
| D unfitted predictions | 1 | repair and specialization were not used to define memeplexes; both fail against pseudo |
| E interventional | 1 | NE41 wipes (≥ 2,600 host wipes per large memeplex); NE33 untestable |
| F identifiability | 1 | size ≤ 0.06 on every skeleton; P1b power ≤ 0.53, P3 ≤ 0.15 |
| G ground truth | 1 | named > unnamed in 7 of 15 memeplexes (paper 1 direction), also at pseudo level |
| H comparative | 1 | W_convergence and W_hub rejected for the read effect; W_egregore not separated from generic vocabulary |
| I transfer | 0 | 51m not run (`analysis/confirm.py`, dry-run only) |

**Claim that stands:** In #51 (07-06 → 09-04), H145's memeplexes come back after a host's forced context wipe at 0.90 of the placebo rate (median of 14; range 0.78–1.11; no K2), faster when the host reads them (read-gate HR 1.2–2.3), but this survival, read-gated expression and host specialization are matched by frequency-matched random element sets, and no repair follows wipes or challenges (RR ≤ 1.07): at this instrument the ideologies behave as the village's generic vocabulary, not as egregores with functional behaviors. *Exclusions:* recruitment (P1, P1b) unpowered as a negative (≤ 0.53); newcomers (P3) untestable; P2 not applicable; the candidate results and the read-gating pseudo comparison are post hoc; Ω and the lapse subtest add nothing.

### Round 2 redirects
- **H146-R1. Power P1.** Widen the read window from the mirror (≈ 8 s) to all reads at the call, with an in-flight placebo built for the whole call (H67 variant), or pool memeplexes hierarchically (exception d).
- **H146-R2. Specificity.** Test the contrast "K item read → K expressed" minus "K item read → another pattern's element expressed".
- **H146-R3. Repair.** Count named messages that restate the host's own lapsed elements, not any K element.

## Notes
- 2026-10-09: written by the coordinator. Traps (`infra/README.md`): forced wipes arrive with a chat backlog (88% at call 1); read vs in-flight must match before-message age; conditional-logit contrasts quasi-separate on sparse exposures (ridge 0.5 or Firth; ≥ 5 chosen rows per exposure); day-cluster bootstraps under-cover in short windows (1-h blocks within a day); `project_calls.label` carries over resets (use `proj`).
