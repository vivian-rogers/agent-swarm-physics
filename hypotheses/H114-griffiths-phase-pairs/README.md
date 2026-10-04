# H114: A Griffiths phase: rare strong pairs give a subcritical swarm heavy-tailed talk

**Status:** exploratory round 1 done (2026-10-04; non-holdout only). **The Griffiths-pair reading fails: reply chains are heavier than geometric, but the excess is first-order thread momentum, not rare strong pairs.**
- **Heavier than geometric at the mean:** the tail continuation hazard exceeds the reply branching ratio (Δh = h_tail − g_rep > 0) in 52/54 usable units, with CI excluding 0 in 33/54 (61%; P1 missed its 2/3 bar). Regime medians Δh 0.27 (I) and 0.17 (III).
- **The excess sits at depth 1, not in the tail:** a reply's parent is itself a reply far more often than g_rep allows (h(1) > g_rep in 54/54, median +0.16), and the hazard rises little beyond depth 1 (median δh +0.05; CI > 0 in 10/54). Synthetic: that is the thread-momentum signature; strong pairs give a clear rise.
- **Strong pairs are rare and do not carry the tail:** 37 strong directed pairs (lower bound of g_ij > 0.5) in 18/66 units, half of them readers answering three hub authors (4 ping-pong dyads); cutting them carries the excess in 1/16 units; Δh does not track their share (ρ −0.14).
- **Agents and pairs explain little:** rank-1 agent heterogeneity (M1) and the pair Markov chain (M2) both sit near g_rep (M2 − M1 median +0.003); the observed tail is above M2 in 31/54.
- Natives: G51 mixed (assigned rival/opposed pairs reply to each other more, MW p 0.0003, but none is strong), NE42 descriptive (no strong pair in #39–#41). The tail exponent is not identifiable (synthetic and real).
- Scorecard A1 B1 C1 D1 E0 F1 G1 H1 I0. `analysis/confirm.py` frozen, guarded and dry-run; **not run**.
**Question (GOALS.md):** **Q3** (is there collective order beyond fields?): do rare, locally strong agent pairs make reply chains heavy-tailed in a swarm that is subcritical on average? **Q1** second (what couples agents: are couplings pair-specific beyond agent-level propensities?).
**Fields:** stat mech (disordered systems, Griffiths phases), branching processes, sociophysics
**Literature:** no note in `literature/` covers Griffiths phases. Cited from memory (†, not in `literature/`): Griffiths, *PRL* 23, 17 (1969)†; Vojta, *J. Phys. A* 39, R143 (2006)† (rare regions, power-law tails with non-universal exponents); Muñoz, Juhász, Castellano & Ódor, *PRL* 105, 128701 (2010)† (Griffiths phases on networks); Clauset, Shalizi & Newman, *SIAM Rev.* 51, 661 (2009)† (power-law vs exponential tests). Model references: [`physics-models/09-hawkes/README.md`](../../physics-models/09-hawkes/README.md), [`physics-models/03-contagion/README.md`](../../physics-models/03-contagion/README.md), [`physics-models/01-inverse-ising/README.md`](../../physics-models/01-inverse-ising/README.md).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Population N(t); Regime; Driving / external field; Interaction (reply) in DQ2's ledger form; **Exposure (turn read-out)** (H08; implemented by the context ledger); **Read-out loop gain g_lag** (H67, comparison only); **Branching ratio (content)** (H34, comparison only). **New named variants proposed for DEFINITIONS.md** (not edited here), defined under Model: *reply depth D*, *continuation hazard h(d)*, *reply branching ratio g_rep*, *pair reply gain g_ij*, *strong pair*.
**From:** HH346 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/09-hawkes/` (branching ratio), `physics-models/03-contagion/` (heterogeneous branching, outbreak tails), `physics-models/01-inverse-ising/` (pair couplings J_ij)
**Data inputs (shared tables first):** DQ2 `reply_pairs` (`parent`, `pair_set == cand`, ledger-visible candidates), `reply_graph` (cross-check); `pair_day_reads` (ledger reads per pair-day; H05/H18 consolidated); `chat_core`, `chat_mentions_clean`; DQ1 `call_windows` (all-present window); `ground_truth_labels` (#51 rival and opposed pairs); `roster` (families); `calendar`, `period_units`.

## Source HH (verbatim from the HH list, including refinements)
- **HH346 · A Griffiths phase: rare strong pairs give a subcritical swarm heavy-tailed talk.** Every unit is subcritical on average (g_lag ≤ 0.39). In a disordered system, rare strongly coupled regions can still be locally supercritical. That gives power-law tails with exponents that vary from period to period (a Griffiths phase), not the geometric tail of a uniform subcritical process. Ping-pong dyads that name each other are the candidate regions.
  - *Prediction:* reply-chain lengths have tails heavier than the geometric law with the unit's mean g. Pairs with pair gain g_ij > 0.5 carry the tail. Removing those pairs restores a geometric tail, and the tail exponent across units tracks the share of strong pairs.
  - *Check:* chains from `reply_pairs` (ledger-visible replies only), per-pair gains from named replies; trimmed at day edges; KS test against the fitted geometric; leave-strong-pairs-out refit.
  - *Kill:* tails are geometric at the mean g, or no pair has g_ij reliably > 0.5.
  - *Impostors:* scheduler: day-edge trim. Exogenous: human-initiated chains are split out. Convergence: ledger-read replies only. Priors: pair strength checked across periods (is it a family pairing?).
  - *Models:* 09, 03, 01 · *Builds on:* H67, H34, H18, H62

## Question
Are reply chains longer than a uniform subcritical branching process allows, and is the excess carried by a few strongly coupled agent pairs (a Griffiths phase), rather than by agent-level heterogeneity or by thread momentum that is not pair-specific?

## Design: two layers (STANDARDS §4)
- **Replication (layer 1, role `replication`).** The common estimators (below) on every non-holdout period unit with ≥ 300 agent messages and ≥ 100 agent-to-agent parent links (DQ2). One README per goal period. Units of a split period are reported separately and pooled by a random-effects mean (CLAUDE.md exception (d), named).
- **Natives (layer 2, role `native`),** each with its own dated prediction in its folder:
  - **NE42** (#39 → #40 → #41, room merge and split at a fixed roster): one shared room of 14 agents dilutes reading (H67: read-out coupling vanishes in #40). Strong pairs and the tail excess should fall in #40 and return in #41.
  - **G51 (rival and opposed pairs):** DQ6 lists 9 assigned rival pairs and 2 opposed pairs in #51. Known pair structure: are the strong pairs the detector finds enriched for assigned pairs (ground truth, axis G)?

## Model
**From:** `physics-models/09-hawkes` (branching ratio), `physics-models/03-contagion` (heterogeneous branching), `physics-models/01-inverse-ising` (pair-specific couplings).

**H114 variant: a reply forest with pair-specific continuation.** Every agent message m has at most one agent parent a(m) (DQ2 keeps one parent: the best ledger-visible candidate with p_reply ≥ 0.5). Following parents back gives m's **reply depth D(m)** (proposed named variant): the number of agent → agent parent links to the chain's root. Depth is the chain length the HH means; one parent per message makes the ancestry a single path.
- **Reply branching ratio g_rep** (proposed named variant) = agent parent links ÷ agent messages = the mean number of agent replies per message = P(a message has an agent parent). Subcritical: g_rep < 1.
- **Continuation hazard h(d)** (proposed named variant) = S(d + 1)/S(d), with S(d) = P(D ≥ d) over messages. h(0) = g_rep.
- **Uniform subcritical process (the HH's null):** each message has a parent independently with probability g_rep. Then S(d) = g_rep^d, a geometric law, and h(d) = g_rep at every depth.
- **Griffiths reading:** the continuation probability varies by region. A chain that sits in a strong pair continues with probability p_ij close to 1. The depth law is then a mixture of geometrics, and h(d) rises with d toward the strongest local continuation; with a broad distribution of p near 1, S(d) approaches a power law d^(−α) with a period-specific α.
- **Pair reply gain g_ij** (proposed named variant) = L_ij / R_ij: the number of i's messages whose parent is a j message (L_ij), per j message read by i at a ledger call (R_ij, from `pair_day_reads`). **Strong pair:** a directed pair with R_ij ≥ 10 and the 95% lower bound of g_ij (Gamma/Jeffreys, Poisson L) > 0.5. **Ping-pong dyad:** both directions with point g > 0.5.

**Model ladder for the depth law** (each gives S(d) exactly by matrix powers, no simulation):
- **M0 geometric:** h(d) = g_rep.
- **M1 agent heterogeneity, rank 1 (the matched-heterogeneity null):** a first-order Markov chain over authors. A message by k has a parent with probability p_k (k's own parent share). The parent's author k′ is drawn with P(k′ | k) ∝ R_{k k′} · b_{k′}: reads times an author attractiveness b fitted by a Poisson model L_{k k′} ~ R_{k k′} a_k b_{k′}. No pair-specific term.
- **M2 pair Markov (the Griffiths-pair model):** the same chain with the empirical P(k′ | k) = L_{k k′}/Σ L_{k ·}. Ping-pong (A → B → A) is in M2 and not in M1.
- **M3 thread memory (rival):** continuation depends on the chain's history beyond the current pair (a conversation's momentum). Shows as observed h(d) above M2.

**Rivals (named).**
- **R1 uniform subcritical** (M0): the HH null.
- **R2 agent heterogeneity** (M1): a few chatty agents and a few attractive authors make the depth law a mixture without any pair structure.
- **R3 thread field** (M3; H62: a thread field alone gives a reply premium of about 3): chains continue because a conversation is running, whoever the pair is.
- **R4 parent-selection artifact:** DQ2's candidate score adds +0.20 when B names A's author, and parents are partly content-selected. Named partners are favored as parents, which can manufacture ping-pong links.

## Data scheme (`scheme/`)
`scheme/build.py` reads shared tables only and asserts the holdout twice (`calendar.holdout` and `common.holdout_mask`). Codes and message indices only (no text).
- **Messages:** `chat_core` agent messages (`speaker_kind == agent`) on the unit's non-holdout days; author, room, time, PT date; names from `chat_mentions_clean.mentions_roster`.
- **Links:** `reply_pairs` rows with `parent == True`, `pair_set == "cand"`, non-holdout. Agent parent: `a_kind` = agent. A human or automated parent makes the message a root, flagged `root_kind` = human / automated (exogenous chains).
- **Day-edge trim (scheduler):** links whose parent is on another PT date are cut (the child becomes a root). Depth is counted for messages posted inside the day's DQ8 all-present window (H67's rule from `call_windows`); ancestors may lie anywhere earlier that day. Variant: all messages of the day.
- **Reads:** R_ij summed over the unit's days from `pair_day_reads` (kind `agent` ledger items; self-reads dropped).
- **Output:** `data/processed/H114-griffiths-phase-pairs/` (`msgs/<unit>.parquet`: message index, author, room, time, parent index, depth, root kind, link flags; `pairs/<unit>.parquet`: L_ij, R_ij, g_ij with bounds, names share, same family; `unit_meta.parquet`, `results/`, `synthetic/`, `_provenance.json`). Budget ≤ 50 MB.
- **Regimes covered:** I, II, III (non-holdout units).

## Observables
Per unit (period pooled by random effects):
1. **g_rep**, **S(d)** and **h(d)** for d = 0…15; the **tail hazard h_tail** = Σ_{d ≥ 4} S(d + 1) / Σ_{d ≥ 4} S(d) (pooled continuation from depth 4 on), and **h_1** = h(1).
2. **Tail excess over geometric** Δh = h_tail − g_rep; **Griffiths rise** δh = h_tail − h_1. CI: day-block bootstrap of chains (resample days; hour blocks when the unit has ≤ 5 days), 500 draws.
3. **KS distance** between the depth distribution and the fitted geometric, with a parametric-bootstrap p-value that resamples whole chains (the HH's check).
4. **Model ladder:** h_tail under M1 and M2 (exact), and the observed minus each.
5. **Pair gains:** g_ij with 95% bounds; the number of strong pairs; the **strong-link share** (share of agent links that lie in strong pairs); ping-pong dyads; the share of strong-pair links whose child names the parent's author vs other links; same-family share vs the pair-count expectation.
6. **Leave-strong-pairs-out:** cut every link of a strong pair (the child becomes a root), recompute g_rep′, h_tail′ and Δh′. **Matched control:** cut the same number of links drawn at random from non-strong pairs (200 draws). The strong cut "carries the tail" if Δh′ CI includes 0 and Δh′ is below the 5th percentile of the random cuts.
7. **Tail exponent:** discrete power-law MLE α̂ on D ≥ 3 and the likelihood ratio against a discrete exponential (geometric) on the same range (Vuong test). Reported only if the synthetic validation shows α is identifiable at the unit's counts.
8. **Cross-unit:** Spearman ρ(Δh, strong-link share) and ρ(α̂, strong-link share); heterogeneity of α̂ across units (Cochran Q with bootstrap SEs).
9. **Comparison:** H67's g_lag for the same unit (a talk-call gain, not a reply gain).

## Null / baseline
- **M0 geometric at g_rep** (the HH's null) and **M1 rank-1 heterogeneity** (the uniform-subcritical null with matched heterogeneity), both exact.
- **Matched random cuts** for the leave-strong-pairs-out test (a partition contrast: strong vs other pairs, STANDARDS §3).
- **Synthetic worlds on the real message skeleton** (axis F): real message times, authors and rooms; parents planted by a known rule (below).
- **Strong-pair false-positive rate:** strong pairs detected in the M1 synthetic world, where no pair is strong by construction.

## Impostors (STANDARDS §1)
| Impostor | How H114 removes it | Status |
| --- | --- | --- |
| **Scheduler field** | Links across PT dates are cut; depth is counted inside the DQ8 all-present window; day-block bootstrap | removed |
| **Exogenous field** (kickoff, goal, operator) | Chains with a human or automated root are flagged and reported apart (variant: dropped); g_rep and h(d) are within-unit, so the goal is fixed | partly (kickoff-day chains kept; variant drops the kickoff day) |
| **Shared model priors** | Same-family enrichment of strong pairs vs the pair-count expectation; persistence of strong pairs across units (does the same pair recur in other periods?); M1 absorbs agent-level (family) propensities | partly |
| **Contemporaneous convergence** | Parents are ledger-visible candidates only (DQ2 `pair_set == cand`: posted before the author's call read them); p_reply ≥ 0.8 variant (93% blind precision) | partly (DQ2 p_reply keeps a thread-membership component; R4) |

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R1 uniform subcritical (M0); R2 agent heterogeneity (M1); R3 thread field (M3); R4 parent-selection artifact.
**Locked holdout used for confirmation:** none yet. `analysis/confirm.py` (frozen 2026-10-04, guarded, dry-run on stand-ins 27, 41, 51h; **not run**) targets #28 (regime I), #43 and the #51 tail (regime III). Frozen C1 (pooled Δh > 0 per target period), C2 (h(1) > g_rep in every unit and pooled δh < 0.08 or CI including 0: momentum, no Griffiths rise), C3 (strong-pair cut carries the tail in < half of units with strong pairs), C4 (observed tail above M1 in ≥ half).
**Scorecard plan:** A mapping (depth and pair gains from DQ2 and the ledger); B (Markov order of the depth chain: M2 vs M3); C (M0/M1 rejection with chain-resampling bootstrap); D (the strong-pair cut and the cross-unit slope are not fitted); E (NE42); F (synthetic recovery of planted strong pairs and tails on real skeletons); G (#51 assigned pairs); H (M2 vs M1 vs M3); I (holdout, not run).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Depth from DQ2 parents (ledger-visible candidates, one parent, cross-day links cut); g_ij from links per ledger read. Known distortions listed: DQ2's score favors named partners and p_reply carries thread membership (R4); a reader can reply to one message more than once (g_ij > 1 in 5 pairs). Qualitatively invariant across regimes. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Markov order checked: a first-order chain over the "is a reply" state (h(1) ≫ g_rep, flat h(d) beyond) fits; author-level first-order chains (M1, M2) do not. Parents precede children (asserted). |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | M0 (geometric) rejected one-sided in 33/54 units (synthetic size 0/80); M1 rejected in 31/54. Day/hour-block bootstrap. No held-out run. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | The Griffiths signatures (rise with depth, strong-pair cut, cross-unit tracking) were predicted and failed (P2 10/54, P4 1/16, P7 ρ −0.14); the momentum signature (h(1) jump, flat tail) was a synthetic world and appears in 54/54. |
| E interventional | predicts the change across a natural experiment | 0 | NE42 descriptive (no strong pairs to dilute; Δh 0.18 in the merged room). No other intervention used. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Real skeletons: null size 0/80; thread momentum identified in 100%; strong pairs at g ≈ 0.8 detected in 30–81% and their tail in 90–100%, but at g ≈ 0.5 detected in 15–40%; the exponent is unidentifiable. Variants (untrimmed, p_reply ≥ 0.8, human-rooted chains dropped) keep P1's direction and P2's failure. |
| G ground truth | agrees with known structure | 1 | #51 assigned rival/opposed pairs answer each other more than other pairs (MW p 0.0003) but none is strong (0/176 rows vs 21/6,410). |
| H comparative | beats the named rivals | 1 | R3 (thread momentum) beats the Griffiths reading and R2 (agent heterogeneity) on the rise and model-ladder tests; R4 (parent-selection artifact) is not excluded. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | The momentum pattern holds in every regime (h(1) > g_rep in 54/54); no holdout run. |

## Prediction
*Written 2026-10-04 21:29 UTC, before any real-data statistic. Seen beforehand: table schemas; the period-unit list; DQ2's published coverage (parents for 37% / 48% / 54% of messages in regimes I / II / III; 70% of parents named by the child) and validation; H67's, H62's, H34's and H104's published results; DQ6's count of #51 rival pairs (9) and opposed pairs (2). Not seen: any chain depth, pair gain or tail statistic.*

**Synthetic (axis F), before real data.** Parents planted on the real message skeletons of four units (one regime I, one regime II, two regime III): each message picks a parent among same-room agent messages of the previous 30 min with a recency kernel. Worlds: **W0** homogeneous (parent share g = 0.45); **W1** agent heterogeneity (agent-specific parent shares and author attractiveness, lognormal σ = 0.7); **W2** W1 plus 3–5 planted strong dyads (g_ij ≈ 0.6–0.8 both ways); **W3** W1 plus thread momentum (a message is likelier to have a parent when its newest candidate has one), no pair structure. 10 replicates per world and unit.
- **S1 null calibration:** in W0, Δh CI excludes 0 in ≤ 10% of replicates; in W1, the observed h_tail lies inside M1's bootstrap band in ≥ 85%. [0.65]
- **S2 strong-pair detection:** in W2, ≥ 70% of planted directed strong pairs are detected; in W1, ≤ 1 false strong pair per unit on average. [0.55]
- **S3 the cut:** in W2, cutting strong pairs brings Δh′ to within CI of 0 and below the 5th percentile of random cuts in ≥ 70% of replicates; in W3 it does not (≤ 20%). [0.5]
- **S4 ladder:** W2 is fit by M2 and not by M1 (M1 rejected in ≥ 70%); W3 is rejected by both M1 and M2 in ≥ 70%. [0.5]
- **S5 exponent:** α̂ is reported only if, in W2, the Vuong test prefers the power law in ≥ 70% and α̂'s bootstrap SE is ≤ 0.3; otherwise P7 is scored inconclusive (H104: tails were unidentifiable at its counts).

**Real data (exploratory, non-holdout).**

| # | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| P1 | **Heavier than geometric (HH).** h_tail > g_rep (Δh CI excluding 0) in ≥ 2/3 of eligible units. | Δh ≤ 0 or CI including 0 in ≥ 1/2 (kill: tails geometric at the mean) | 0.75 |
| P2 | **Griffiths rise.** h(d) rises with depth: δh = h_tail − h_1 > 0 (CI excluding 0) in ≥ 1/2 of units. | δh ≤ 0 in ≥ 1/2 | 0.45 |
| P3 | **Strong pairs exist (HH).** ≥ 1 strong directed pair (lower bound of g_ij > 0.5, R_ij ≥ 10) in ≥ 1/2 of units. | none in ≥ 1/2 of units (kill: no pair reliably > 0.5) | 0.35 |
| P4 | **Strong pairs carry the tail (HH).** In units with strong pairs, the leave-strong-pairs-out cut brings Δh′ within CI of 0 and below the 5th percentile of matched random cuts in ≥ 1/2 of them. | the cut beats random cuts in < 1/3 | 0.3 |
| P5 | **Pair structure beyond agents.** M1 underpredicts h_tail (observed above M1's 97.5% band) in ≥ 1/2 of units, and M2 is closer to the observed h_tail than M1 in ≥ 2/3. | M1 fits in ≥ 1/2 | 0.45 |
| P6 | **Thread memory beyond pairs (R3).** The observed h_tail exceeds M2's 97.5% band in ≥ 1/2 of units. (Supports R3, not the HH.) | — | 0.5 |
| P7 | **Cross-unit tracking (HH).** Spearman ρ(Δh, strong-link share) ≥ 0.4 across units; if S5 passes, α̂ varies across units beyond bootstrap error (Q-test p < 0.05) and ρ(α̂, strong-link share) ≤ −0.4. | ρ(Δh, share) < 0.2 | 0.35 |
| P8 | **Naming and priors.** Strong-pair links name the partner more often than other links (ratio ≥ 1.2), and strong pairs are not same-family enriched (odds ratio < 2 vs the pair-count expectation). | naming ratio < 1; family OR ≥ 2 | 0.5 |

**Amendment A1 (2026-10-04 21:50 UTC, after the synthetic validation, before any real-data statistic).** Seen: only synthetic forests planted on the real message skeletons and real reads of units 27, 35, 41 and 51c (worlds W0–W3 plus a stronger pair world W2s, 10 replicates each; `synthetic/summary.json`). The skeleton build counted messages and links per unit for eligibility (66 of 71 units eligible); no depth, pair gain or tail statistic of real data was computed. No estimator change; the following are stated before real data.
- **Null calibration (S1 passed for the one-sided test).** In W0 and W1, Δh > 0 with CI excluding 0 in 0% of 80 replicates. The finite skeleton makes null tails slightly *lighter* than geometric (Δh −0.08 to 0.00), so the two-sided CI is anti-conservative on the negative side (excludes 0 in up to 40%). P1 is scored one-sided (Δh > 0). M1 contains the observed h_tail in 60–100% (W0) and 80–100% (W1).
- **Strong pairs at g ≈ 0.5 are not detectable (S2, S3, S4 failed in W2).** Planted dyads with realized g ≈ 0.31–0.58 are detected in 15–40%; Δh > 0 in 0–40%; M1 is rejected in 0–10%; the cut test passes in 10–20%. **At g ≈ 0.7–1.0 (W2s)** detection is 30–81%, Δh > 0 in 90–100%, the Griffiths rise δh > 0 in 60–80% (3 of 4 units), M1 rejected in 100% (3 of 4), the cut test passes in 50–70%. Consequence: a P3/P4 negative rules out only strong pairs of g ≳ 0.7; weaker pair structure would go unseen ("inconclusive" for g ≈ 0.5).
- **Momentum vs pairs.** Thread momentum (W3) gives Δh ≈ +0.19 (100% significant) and rejects M1 and M2 in 100%, but gives no rise (δh > 0 in 0%). Strong pairs give a rise. **P2 (δh) is therefore the discriminating statistic** between R3 (thread momentum: Δh > 0, δh ≈ 0) and the Griffiths reading (Δh > 0, δh > 0). P6 alone does not separate them: under strong pairs the observed h_tail also exceeds M2 in 20–70% of replicates.
- **Tail exponent not identifiable (S5 failed).** The Vuong test prefers a power law in 0% of replicates in every world, including W2s and W3; P7's exponent clause is scored inconclusive and the cross-unit test uses Δh only (H104's lesson holds here).

**Per-period verdict rule (replication):** on the period pool: **supported** if Δh > 0 (CI excluding 0), the period has ≥ 1 strong pair, and the strong cut brings Δh′ within CI of 0 and below the 5th percentile of random cuts; **failed** if Δh's CI includes 0 (geometric at the mean), or if the period has no strong pair while Δh > 0 is carried elsewhere (the HH's kill); **mixed** otherwise (strong pairs exist but do not carry the excess); **descriptive** if the period has fewer than 100 agent links or fewer than 30 messages at depth ≥ 4.

Native predictions are in `goalperiod-subhypotheses/NE42/` and `G51/` (written before those runs).

## Results by goal period
Per-period rule (card). **0 supported, 6 mixed, 26 failed, 2 descriptive** (34 periods, 66 units). Most periods fail by the HH's own kill clause: their tail is heavier than geometric but no strong pair exists to carry it. The 6 mixed periods have strong pairs that do not carry the excess.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G02](goalperiod-subhypotheses/G02/README.md) | replication | failed | I: g_rep 0.64 · Δh -0.01 [-0.18, 0.16] · δh -0.14 · 3 strong pairs in 1 unit(s), carried in 0 |
| [G03](goalperiod-subhypotheses/G03/README.md) | replication | failed | I: g_rep 0.47 · Δh 0.23 [0.02, 0.44] · δh 0.18 · 0 strong pairs in 0 unit(s), carried in 0 |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | mixed | I: g_rep 0.40 · Δh 0.29 [0.24, 0.35] · δh 0.04 · 2 strong pairs in 1 unit(s), carried in 0 |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | failed | I: g_rep 0.37 · Δh 0.50 [0.19, 0.81] · δh 0.18 · 0 strong pairs in 0 unit(s), carried in 0 |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | failed | I: g_rep 0.25 · Δh 0.14 [-0.00, 0.28] · δh -0.12 · 0 strong pairs in 0 unit(s), carried in 0 |
| [G07](goalperiod-subhypotheses/G07/README.md) | replication | failed | I: g_rep 0.36 · Δh 0.34 [0.09, 0.59] · δh 0.05 · 0 strong pairs in 0 unit(s), carried in 0 |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | failed | I: g_rep 0.20 · Δh 0.35 [0.20, 0.50] · δh -0.04 · 0 strong pairs in 0 unit(s), carried in 0 |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | failed | I: g_rep 0.25 · Δh 0.40 [0.29, 0.50] · δh 0.11 · 0 strong pairs in 0 unit(s), carried in 0 |
| [G12](goalperiod-subhypotheses/G12/README.md) | replication | failed | I: g_rep 0.38 · Δh 0.22 [0.08, 0.36] · δh 0.04 · 0 strong pairs in 0 unit(s), carried in 0 |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | failed | I: g_rep 0.31 · Δh 0.34 [0.25, 0.43] · δh 0.02 · 0 strong pairs in 0 unit(s), carried in 0 |
| [G16](goalperiod-subhypotheses/G16/README.md) | replication | failed | I: g_rep 0.21 · Δh 0.49 [0.33, 0.66] · δh 0.20 · 0 strong pairs in 0 unit(s), carried in 0 |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | failed | I: g_rep 0.23 · Δh 0.27 [0.16, 0.38] · δh 0.09 · 0 strong pairs in 0 unit(s), carried in 0 |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | mixed | I: g_rep 0.46 · Δh 0.17 [0.02, 0.32] · δh 0.06 · 2 strong pairs in 2 unit(s), carried in 0 |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | mixed | I: g_rep 0.45 · Δh 0.29 [0.09, 0.50] · δh 0.17 · 1 strong pairs in 1 unit(s), carried in 0 |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | failed | I: g_rep 0.34 · Δh 0.26 [0.13, 0.38] · δh 0.09 · 0 strong pairs in 0 unit(s), carried in 0 |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | descriptive | I: g_rep 0.25 · Δh – [–, –] · δh – · 2 strong pairs in 0 unit(s), carried in 0 |
| [G23](goalperiod-subhypotheses/G23/README.md) | replication | failed | I: g_rep 0.21 · Δh 0.58 [0.34, 0.82] · δh 0.29 · 0 strong pairs in 0 unit(s), carried in 0 |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | failed | I: g_rep 0.22 · Δh 0.45 [0.30, 0.59] · δh 0.17 · 0 strong pairs in 0 unit(s), carried in 0 |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | failed | I: g_rep 0.49 · Δh 0.16 [0.02, 0.30] · δh 0.08 · 0 strong pairs in 0 unit(s), carried in 0 |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication | failed | I: g_rep 0.49 · Δh 0.15 [0.02, 0.29] · δh 0.13 · 0 strong pairs in 0 unit(s), carried in 0 |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | failed | I: g_rep 0.35 · Δh 0.26 [0.16, 0.36] · δh 0.14 · 0 strong pairs in 0 unit(s), carried in 0 |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | failed | I: g_rep 0.32 · Δh 0.07 [-0.08, 0.22] · δh -0.08 · 0 strong pairs in 0 unit(s), carried in 0 |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | failed | I: g_rep 0.31 · Δh 0.19 [0.08, 0.29] · δh 0.04 · 0 strong pairs in 0 unit(s), carried in 0 |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication | failed | II: g_rep 0.40 · Δh 0.16 [0.06, 0.26] · δh -0.01 · 0 strong pairs in 0 unit(s), carried in 0 |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | failed | II: g_rep 0.45 · Δh 0.02 [-0.09, 0.13] · δh -0.14 · 0 strong pairs in 0 unit(s), carried in 0 |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | failed | II: g_rep 0.39 · Δh 0.14 [0.06, 0.21] · δh -0.08 · 0 strong pairs in 0 unit(s), carried in 0 |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | failed | III: g_rep 0.72 · Δh 0.01 [-0.10, 0.12] · δh -0.05 · 2 strong pairs in 1 unit(s), carried in 0 |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | mixed | III: g_rep 0.46 · Δh 0.18 [0.11, 0.24] · δh 0.02 · 2 strong pairs in 1 unit(s), carried in 0 |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication + NE42 | descriptive | III: g_rep 0.20 · Δh – [–, –] · δh – · 0 strong pairs in 0 unit(s), carried in 0 |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication + NE42 | failed | III: g_rep 0.34 · Δh 0.18 [0.08, 0.28] · δh 0.01 · 0 strong pairs in 0 unit(s), carried in 0 |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication + NE42 | failed | III: g_rep 0.53 · Δh 0.08 [-0.03, 0.18] · δh -0.01 · 0 strong pairs in 0 unit(s), carried in 0 |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | mixed | III: g_rep 0.49 · Δh 0.26 [0.14, 0.39] · δh 0.04 · 1 strong pairs in 1 unit(s), carried in 0 |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | failed | III: g_rep 0.77 · Δh 0.01 [-0.05, 0.07] · δh -0.01 · 1 strong pairs in 1 unit(s), carried in 0 |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication + native (assigned pairs) | mixed | III: g_rep 0.54 · Δh 0.22 [0.17, 0.26] · δh 0.07 · 21 strong pairs in 7 unit(s), carried in 1 |
| [NE42](goalperiod-subhypotheses/NE42/README.md) | native | descriptive | no strong pair in #39, #40, #41 (max g 0.27–0.36); Δh #40 0.18 [0.07, 0.27] |

## Results
*Exploratory round 1, 2026-10-04: 66 eligible non-holdout units in 34 periods; 54 usable (≥ 100 links, ≥ 30 messages at depth ≥ 4). Numbers from `data/processed/H114-griffiths-phase-pairs/results/{units,pairs,periods}.parquet`, variants `units_{untrim,p08,nohuman}.parquet`, `summary.json`; synthetic from `synthetic/summary.json`. Code: `scheme/build.py`, `analysis/h114lib.py`, `synthetic.py`, `run_units.py`, `summarize.py`, `write_period_folders.py`, `confirm.py`.*

### Headline
Reply chains in the village are longer than a uniform subcritical branching process allows, but not for the HH's reason. The continuation hazard jumps at depth 1: a message that answers a reply is itself answered far more often than the mean (h(1) − g_rep = +0.16, 54/54 units). Beyond depth 1 the hazard rises little (median δh +0.05; no significant rise in 44/54). That is a conversation's momentum, a first-order memory in the "this is a thread" state, not rare locally supercritical pairs. Strong pairs exist in a quarter of units, are hub-like, and do not carry the tail.

### Outcome vs prediction
| # | Prediction | Observed | Outcome |
| --- | --- | --- | --- |
| S1 | null size: Δh > 0 false positives ≤ 10%; M1 contains W1 | 0/80; M1 inside 80–100% | passed (one-sided) |
| S2 | planted strong pairs detected ≥ 70%; ≤ 1 false per unit | g ≈ 0.5: 15–40%; g ≈ 0.8: 30–81%; false 0–0.2 | **failed** at g ≈ 0.5 (A1) |
| S3 | the cut carries planted tails in ≥ 70%; momentum ≤ 20% | g ≈ 0.5: 10–20%; g ≈ 0.8: 50–70% | **failed** (A1) |
| S4 | W2 fit by M2 not M1; W3 rejected by both | W2 M1 rejected 0–10% (W2s 75–100%); W3 100% | partly passed |
| S5 | exponent identifiable | Vuong prefers a power law in 0% | **failed**: P7 exponent inconclusive |
| P1 | Δh > 0 (CI) in ≥ 2/3 | 33/54 (61%); point estimate 52/54 | **failed narrowly** (direction holds) |
| P2 | Griffiths rise δh > 0 in ≥ 1/2 | 10/54 (19%) | **failed** |
| P3 | ≥ 1 strong pair in ≥ 1/2 of units | 18/66 (27%); 37 directed pairs; 4 ping-pong dyads | **failed** (HH kill clause "no pair reliably > 0.5" not met) |
| P4 | strong cut carries the tail in ≥ 1/2 of units with pairs | 1/16 | **failed** |
| P5 | M1 underpredicts in ≥ 1/2; M2 closer in ≥ 2/3 | 31/54; 39/54, but M2 − M1 median +0.003 | supported on its letter, null in size |
| P6 | observed above M2 in ≥ 1/2 (R3) | 31/54 (57%) | **supported** (with P2's failure: thread momentum) |
| P7 | ρ(Δh, strong-link share) ≥ 0.4 | −0.14 (p 0.32); exponent unidentifiable | **failed** |
| P8 | naming ratio ≥ 1.2; family OR < 2 | 0.73 (strong-pair links name the partner *less*); OR 0.31 (p 0.045) | **mixed** |
| G51a/b | assigned pairs enriched among strong pairs; higher g | 0/176 strong (OR 0); MW p 0.0003 | failed / supported |
| N42a/b | strong pairs and Δh fall in #40 | no strong pairs anywhere; Δh nominal | descriptive |

### Findings
1. **Thread momentum.** In every usable unit the chance that a reply's parent is itself a reply (h(1)) exceeds the base reply share g_rep: medians 0.56 vs 0.36 (regime I) and 0.68 vs 0.53 (regime III). Deeper links continue at about h(1) or slightly above (median δh +0.05). A first-order memory in thread state gives exactly this; synthetic thread momentum gave Δh ≈ +0.19 with no rise.
2. **Little Griffiths rise; the data sit with the momentum world.** The hazard does not climb significantly with depth in 44/54 units (regime medians δh +0.08 and +0.02). The point estimate is positive in 40/54, so a small rise exists. Against the synthetic worlds on the same skeletons, three signatures place the data with thread momentum: pair-specific transitions add nothing (M2 − M1 median +0.003; W3 0.000, planted pairs W2 +0.014, W2s +0.054); the rise is significant in 19% of units (W3 0%, W2s 55%); and the depth-1 jump is +0.16 (W3 +0.19, W2s +0.12). Strong pairs appear in 27% of units (W3 0%, W2 95%), so a weak pair component cannot be excluded. Planted strong pairs at g ≈ 0.8 produced a rise in 60–80% of synthetic replicates; the real data look like the momentum world, not the pair world.
3. **Strong pairs are hubs, not dyads.** 19 of the 37 strong directed pairs are readers answering three hub authors; only 4 dyads are mutual. Their links name the partner less often than other links (56% vs 77%), and they are under-represented within a lab (OR 0.31): not a family pairing. 6 of 17 distinct strong pairs recur in a second period.
4. **Agent heterogeneity is small.** Rank-1 agent propensities (M1) put h_tail near g_rep; pair-specific transitions (M2) add +0.003. The tail needs history, not identities.
5. **Assigned rivals talk more but not strongly** (#51): assigned pairs have higher pair gains (p 0.0003) and none crosses 0.5.

### Caveats
- DQ2's parent rule adds +0.20 to the candidate score when the child names the parent's author, and p_reply keeps ~75% of its value for strictly invisible pairs (thread membership). Both can manufacture momentum; a label-free reply proxy is needed (round 2).
- Pairs of g ≈ 0.5 are not detectable at village counts (A1); the negative covers g ≳ 0.7.
- One parent per message: the forest is a projection of a reply graph with multiple parents.
- P1 at 61% (CI) is below its bar, though the point estimate is positive in 52/54; the finite skeleton biases Δh down (synthetic −0.08 to 0).
- Predictions were written knowing DQ2's coverage, H62's thread-field result and H104's identifiability lesson.

**Claim that stands:** DQ2 reply chains are heavier than a uniform subcritical branching process at the mean (Δh median 0.27 in regime I and 0.17 in regime III; CI > 0 in 33/54 units) because of first-order thread momentum (h(1) − g_rep = +0.16, 54/54 units; no significant rise with depth in 44/54, median δh +0.05), not rare strong pairs (present in 18/66 units, carrying the tail in 1/16). *Excluded:* pair structure weaker than g ≈ 0.7 (undetectable, A1), the tail exponent (unidentifiable), G51a (no strong assigned pair, OR undefined), NE42 (no pairs to test), any label-free claim (R4 open).

## Round 2 redirects
- **What the direction is really after:** whether swarm talk has a disordered, locally near-critical structure an operator could target, or only conversation-level memory.
- **H114-R1. Label-free momentum.** Rebuild chains from ledger timing alone (reply = the recipient's next talk call after reading a message that names it) and test whether h(1) > g_rep survives without DQ2 labels.
- **H114-R2. Momentum as a field or a coupling.** Compare h(1) for children whose parent was read at the producing call vs posted in flight (H67's placebo) to tell a conversation field from reading.
- **H114-R3. Hubs.** Model the strong-pair hubs as author fields (M1 with hub-specific attractiveness by period) and test whether hub replies end chains or extend them.
- **H114-R4. Holdout.** Run `confirm.py` (C1–C4) on #28, #43 and the #51 tail.


## Notes
- 2026-10-04 21:29 UTC: round 1 started; card filled before any real-data statistic. Compute: local, ≤ 2 workers, one heavy job at a time.
- 2026-10-04 21:45–21:50 UTC: scheme built (71 units, 66 eligible, 2 MB); synthetic validation on real skeletons; Amendment A1.
- 2026-10-04 21:51 UTC: period predictions written (33 folders; G51, NE42 earlier); ~21:52 replication and variants run (≈ 15 s). The period-level carry rule was first coded as "any unit"; changed to "at least half of the units with strong pairs", the card's pooled reading, before any verdict was written (it moved #51 from supported to mixed).
- Data: `data/processed/H114-griffiths-phase-pairs/` (≈ 3 MB). Estimates: 258 rows in `per_period_estimates` (`reply_tail_excess`, `reply_griffiths_rise`, `reply_branching_ratio`, `strong_pair_count` on channel `reply_dq2`; 2 native rows).
- Proposed for `physics-models/DEFINITIONS.md` (not edited): *reply depth D*, *continuation hazard h(d)*, *reply branching ratio g_rep*, *pair reply gain g_ij*, *strong pair*, *thread momentum h(1) − g_rep*.
- Not computed as listed under Observables: the KS parametric-bootstrap p-value (item 3). Depths within one chain are dependent, so the KS distance is stored (`ks`) but the decision statistic is Δh with the day/hour-block bootstrap.
