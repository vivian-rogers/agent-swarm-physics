# H13: Model families carry their own fields, and couple by family

**Status:** **exploratory round 1 done (2026-10-04).**
- **Families carry a stable content field, but it is writing style.** The field shows in 9/15 periods and is invariant across periods. It does not survive style residualization in any period.
- **Families do not couple by family.** Talk-timing and content co-movement show no family homophily.
- **Coupling follows rooms.**
- **Round 1b (2026-10-04, section below):** all of this replicates with the second embedding model, both style rivals, dedupe and the corrected talk table (talk CI 2.3× narrower). The behavioral family test (HH267) **failed** by its rule (3/15 units; RE 0.075 [0.030, 0.121]): families leave only a weak, work-habit-shaped trace in behavior. Natives: NE06 uninformative (the change was village-wide), NE32 failed, G35 mixed.

Confirmatory script written, not run. Predictions were written 2026-10-03 23:50 UTC, before any real-data run (below).
**Fields:** stat mech, sociophysics, info theory
**Origin:** HH10 + HH75 + HH89 (shortlist 2, item 4) (`../hypohypotheses/HYPOHYPOTHESES.md`; `../promotion-shortlist.md`)
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Population; Regime; Driving / external field (the goal field, here estimated as the day field, see Observables); Agent state, **variant vector** (named sub-variant proposed here: *agent state (vector, chat agent-day, whitened)*, defined under Observables); Interaction (broadcast: co-located = same room). Two terms not in DEFINITIONS.md are used with the operational meaning given here and proposed for the shared file: **model family** = `roster.lab`, and **talk spin** = H05's spin (+1 in a 1-min bin where `activity_bins.state == 4`, else −1).

## Standards (2026-10-04)
**Question served:** Q2 (family fields are writing style, not coupling).

| Impostor | Relevant? | How it was handled | Status |
| --- | --- | --- | --- |
| Scheduler field | partly | Cross-day surrogate for talk spins (b1, Null / baseline), on `activity_bins_fixed` but untrimmed. Close with trim-then-block-shift (§1, §3). | partly |
| Exogenous field (kickoff/goal/operator) | yes | Day- or window-mean removal on every a, b and c observable (goal-field null, Null / baseline). | removed |
| Shared model priors | yes | The object of the card: style rivals S-a, S-b and `style_resid_period` in both models remove the family field (P2, Round 1b). | removed |
| Contemporaneous convergence | partly | Not handled for P7's "rooms carry coupling" (co-movement, not reads). Close with ledger reads or the in-flight placebo (§1). | open |

**Inputs:** round 1b uses both embedding models, `style_resid_period`, DQ5 dedupe, `activity_bins_fixed`, Jev v3.1 and `n_errors`. Still old: talk coupling is minute-bin co-movement, not ledger read-outs; the card does not name DQ4 as the source of commit rates.

**Two layers:** 10 replication folders. Natives: 3 in the card (NE06 uninformative, NE32 failed, G35 mixed); the G35 folder is tagged exploratory, so 2 carry `**Role:** native`.

**Confirm script:** `confirm.py` (C1–C6), written and dry-run, not run. Re-freeze: yes; C5's talk test was frozen before the switch to `activity_bins_fixed`.

## Question
Does each lab's models share a direction in content space (a family field h_f, e.g. the 'genuinely' magnetization), beyond the goal field? Is coupling homophilous by family: a K×K family coupling matrix with J_within > J_across? Does family identity persist across room boundaries, or does room identity dominate (H01 D9.2)? Practical payoff: vendor bias and homophily in mixed-model swarms, with about 9 parameters instead of N×N.

## Model
**From:** `physics-models/11-vector-spins` (fields), `physics-models/10-potts`, and `physics-models/01-inverse-ising` / `02-nonequilibrium-ising` in K-population mean-field form (family blocks, like H05's two-block mean field). Lexical magnetizations, such as per-family rates of marker words, come from derived counts only.

**H13 variant (vector spins with family fields and family-block couplings).** For agent i of family f(i), on day d of goal-period unit u, in the regime-whitened embedding space:

  v_{i,d} = g_{u,d} + h_{f(i),u} + a_i + x_{i,d} + ε_{i,d}

- g_{u,d}: the day field, common to every agent present (goal, kickoff, the day's events);
- h_{f,u}: the **family field** (what H13 is about);
- a_i: an idiosyncratic agent offset (its own style, its assigned role in #51);
- x_{i,d}: fluctuations, coupled across agents with a K×K block matrix, J_ij = J_{f(i)f(j)};
- ε: statement-sampling noise.

Two decompositions of h_f are rivals:
- **position** (h_f depends on the period: the family takes its own stance on the period's material);
- **style** (h_f is a fixed writing-style offset, the same in every period and removable by style features).

Talk spins follow the same block structure in H05's mean-field form (`../H05-rooms-cut/analysis/mf_blocks.py`, `block_J`, which already handles K blocks).

## Data scheme (`scheme/`)
Script: `scheme/build.py` (reads shared tables only; asserts no holdout day unless called by the confirmatory script). Inputs:
- `embeddings/statements.parquet` + `chat_bge_small.npy`;
- `common.load_whitener(regime, 32)`;
- `chat_text` (for derived style features and marker counts; text never written out);
- `activity_bins` (talk spins), `roster` (lab), `calendar`, `agent_goals` (raw; #51 roles).

**Output:** `data/processed/H13-family-fields/G<NN>/` (one subfolder per goal period; sub-units inside), with `_provenance.json`:
- agent-day and agent-window (30 min) content vectors: raw and style-residualized;
- per agent-day marker counts and style features (numbers only);
- talk-spin pair-day correlations with a cross-day surrogate;
- agent room labels.

**Units** (goal periods split at step changes, the same units as H01): 35 (regime II), 36b (03-24 → 03-27; regime III part of #36; 03-23 dropped), 37, 38a (04-02 → 04-13), 38b (04-14 → 04-17), 38c (04-20 → 04-24), 39, 40, 41, 42, 44, 51a (07-06 → 07-08), 51b (07-09 → 08-04), 51c (#focus, 08-05 → 08-24), 51d (08-25 → 09-02), 51e (09-03 → 09-04). Non-holdout days only (#43 and the #51 tail are held out). Units with ≥ 3 days count toward verdicts; 51e (2 days) is descriptive.

## Candidate goal periods
#51 (most families; non-holdout days only), regime III (#35–#44), #35 rooms (family vs room).

## Links to other hypotheses
H01 D1.1.b, D6.4 (families as units), D9.2; H05 two-block machinery; HH90 (attention) not in scope.

## Observables
*Written 2026-10-03, before any real-data run.*

**Content state.** *Agent state (vector, chat agent-day, whitened):*
- Statements are the agent's own chat messages (`statements.kind == chat`); intentions are excluded, since their genre share differs by agent.
- Each statement embedding is whitened with its regime's whitener at n = 32 (`load_whitener`) and unit-normalized.
- v_{i,d} is the mean of these unit vectors over the agent's statements on day d. Agent-days need ≥ 3 statements.
- Window version v_{i,w}: the same over 30-min windows of the day's active window (`win30`), ≥ 2 statements.

**Goal field removed.** δ_{i,d} = v_{i,d} − m_d, where m_d is the equal-weight mean over agents present that day. This removes the day field g_{u,d}. It is stronger than projecting out the goal text, since it also removes kickoffs and the day's shared events.

### (a) Family field
- **a1. Family alignment.** H_i = mean_d δ_{i,d} over the agent's eligible days in the unit (≥ 2 days).
  - T_field = mean cos(H_i, H_j) over same-family pairs − mean over cross-family pairs.
  - "Same family" only for labs with ≥ 2 eligible agents in the unit (up to the 5 largest). All other agents are singletons: they enter cross pairs and the day mean.
  - In #51 units, pairs sharing an assigned role (`agent_goals.short_name`) are dropped from both sets, so a shared role can't pose as a family.
  - Also reported: R²_fam, the share of between-agent sum of squares of H explained by family means (multi-member labs only), and |h_f| for h_f = mean of members' H_i.
- **a2. Style-residualized field (style rival S-a).** Per message, 20 numeric style features from the text: log length, lines, bullet-line share, headers, bold markers, emoji, ! and ? per 100 chars, URLs, backticks, digit share, uppercase share, @ signs, em-dashes, 1st-person-singular / 1st-person-plural / 2nd-person rates, colons, mean word length, parentheses.
  - Within each unit, the whitened unit statement vectors are regressed on the standardized features (OLS, all agents' statements). The residuals are renormalized and pass through the same pipeline.
  - Retention = T_field(residualized) / T_field(raw).
  - This is the maximal linear version of "family = writing style": it also removes any position that correlates with style.
- **a3. Invariance check (exception (b) of the unit-of-analysis rule).** Run before any family field is treated as a family constant. Regime III units only, since the whitening basis is per regime.
  - **Family level:** split the counted regime III units alternately into two disjoint sets; h_f^A and h_f^B are the means of the unit-normalized per-unit family fields. Statistic: cos(h_f^A, h_f^B) for Anthropic, OpenAI and Google, against the cross-family baseline cos(h_f^A, h_g^B), f ≠ g.
  - **Agent level:** cos(H_i^A, H_i^B) for agents with units in both sets. This is the H01 check, on day-demeaned vectors.
  - Also: all pairs of units (mean cos of h_{f,u}, h_{f,u'} same-family vs cross-family, family-label permutation within units).
  - **Pass rule (H01's):** median cos ≥ 0.5 and above the cross-family baseline.
- **a4. Fixed-offset rival (S-b, "remove per-agent means").** H_i' = H_i − S_i, where S_i is the agent's mean H over *other* regime III units (cross-fitted). Then T_field is recomputed on agents that have an S_i. If the family field is only a fixed per-agent offset (style or stable prior), T' ≈ 0. If it has a period-specific (position) part, T' > 0.
- **a5. Lexical magnetization (HH10).** Marker counts per message from a list fixed now, before any count (word-boundary, case-insensitive):
  - **a priori "Claude-like":** genuinely, honestly, appreciate, "you're right", wonderful, beautiful, fascinating, "I think";
  - **"GPT-like":** per, ETA, ack, FYI, noted, confirmed, verified, blocked, "next step", "will do", "on it", "standing by";
  - **"Gemini-like":** delve, crucial, robust, comprehensive, seamless(ly), leverage, indeed, "I will", "I am";
  - **general:** absolutely, perfect, excellent, great, amazing, awesome, thanks / thank you, sorry / apolog*.

  The a priori assignments are guesses and are not tested. Statistics:
  - the "genuinely" rate per 1,000 words, Anthropic vs other agents (rate ratio; lab-permutation p);
  - T_lex, the within- minus cross-family mean correlation of agents' standardized log-rate profiles (lab permutation).

### (b) Family coupling matrix (K×K, K = 2–5 multi-member labs)
- **b1. Talk spins.** Per day, the equal-time correlation c0_ij of talk spins (1-min bins of the active window; agents with ≥ 4 flips), minus the **cross-day surrogate** within the unit (i's day d against j's day e ≠ d, aligned by minute; removes the shared schedule). r_ij = mean over days.
  - H05's `block_J` (naive mean-field inversion of the block-homogeneous correlation matrix) gives the K×K J, J_within (pair-weighted diagonal blocks) and J_across, Δ = J_in − J_out, and the loop gain.
  - Uncertainty: day bootstrap (500).
- **b2. Content co-movement.** x_{i,w} = v_{i,w} − m_w − H̄_i, where m_w is the window mean over agents and H̄_i the agent's unit mean of (v − m). This removes the day/window field and every static field, family and style included.
  - r_ij = Σ_w ⟨x_iw, x_jw⟩ / √(Σ|x_iw|² Σ|x_jw|²) over shared windows (≥ 5).
  - `block_J` with unit variances gives K×K J and Δ_content.

### (c) Family vs room (two-room units: 35, 36b, 37, 38a–c, 39, 41, 42, 44)
- Agent room = modal room of its chat over the unit's days (stable across days, purity ≥ 0.9; others dropped).
- Pair outcomes:
  - y1 = talk r_ij (b1);
  - y2 = content field alignment cos(H_i, H_j) (a1; day mean only, so room fields stay in);
  - y3 = content co-movement r_ij (b2);
  - y4 = lexical profile correlation (a5).
- OLS over pairs, y = c + b_lab·same_lab + b_room·same_room.
- Node-level permutations: lab labels permuted with rooms fixed (null of b_lab); room labels permuted with labs fixed (null of b_room); 2,000 each.

### (d) Unfitted and transfer checks
- **d1. Leave-one-agent-out family classification.** An agent's H_i goes to the nearest multi-member family centroid (cosine), with centroids built without that agent. Accuracy vs the lab-permutation null. The family field is never fitted on the agent being classified.
- **d2. Newcomers (#51).** Agents with no earlier exploration data are classified from their first ≤ 3 eligible days by the *regime III family fields of earlier units* (incumbents only):
  - GPT-5.6 ×3, Kimi K3, Opus 5, GLM-5.3 Flash, Fable 5.1, Gemini 3.8 Flash, GPT-6 Astra;
  - plus the agents whose only earlier days are held out: Fable 5, Sonnet 5, DeepSeek-V4-Pro, GLM-5.2.

  Counted only if a3 passes; descriptive otherwise.
- **d3. NE32 (07-09).** The GPT-5.6 triplet, isolated and unexposed on their first day: alignment of their day-demeaned vectors with the OpenAI field vs other families' fields (incumbents, same day and unit). n = 3, descriptive.
- **B-axis stationarity.** Within-unit split-half (first vs second half of days) stability of h_f.

**Multiplicity.** The verdicts are P1–P8 below. Each is a count over counted units plus a random-effects (DerSimonian–Laird) summary across units, with heterogeneity (τ², I²). Per-unit p-values, variants and nulls are descriptive. Units are fitted separately; cross-unit pooling happens only in a3 / d2 (exception (b), after the invariance check) and in the meta-analytic summaries of per-unit estimates.

## Null / baseline
*Written 2026-10-03, before any real-data run.*
- **Lab-label permutation within unit** (primary for a1, a2, a5, b, d1): agents' lab labels are shuffled, preserving family sizes; 5,000 permutations (2,000 for b). This holds every agent's own vectors and spins fixed and tests only whether *family* organizes them.
- **Rotation null** (per agent, an independent random rotation of its vectors): destroys all cross-agent alignment while keeping each agent's own trajectory. Used for b2 (is there content co-movement at all) and as a sanity floor for a1.
- **Style-only rival:** S-a (style-feature residualization, a2) and S-b (cross-fitted per-agent offsets removed, a4). If a family field disappears under S-a, it is writing style. If it disappears under S-b but not S-a, it is a fixed per-agent prior (style or stance) with no period-specific family part.
- **Shared-schedule null for talk:** the cross-day surrogate (b1). H05 showed the within-day circular shift is not a valid null on this data.
- **Room rival (c):** room membership, not family, organizes coupling and content.
- **Goal-field null:** day-mean removal (all a, b, c observables are computed on day- or window-demeaned vectors).

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** style-only family offset (S-a, S-b); room blocks (H05) for coupling; no family structure (lab permutation).
**Locked holdout used for confirmation:** none yet. Script `analysis/confirm.py` (C1–C6) is written and dry-run on stand-ins, not run.
Scored for exploratory round 1 (non-holdout; 15 counted units plus 51e). Mapping: chat agent-day vectors (regime-whitened, n = 32), 1-min talk spins, lab labels.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Lab from `roster.lab`, content from regime-whitened chat embeddings, talk spins from `activity_bins`; assumptions listed under Model and Observables. **Not family-invariant by construction:** the content state carries each family's writing style (style features alone separate families in 14/15 units). Regime II and III bases differ, so #35 is outside the cross-period checks. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Within-unit split-half stability of family fields: cos 0.31–0.85 (most > 0.5). The equal-time mean-field inversion assumes quasi-equilibrium; no Markov-order or update-order audit for talk spins. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | The family field beats the lab-permutation null in 9/15 units (RE T = 0.080 [0.024, 0.137]). It does **not** beat the strongest relevant null, the style field (S-a: 0/15). Family coupling never beats its null (as predicted). No held-out-day likelihood comparison. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | Leave-one-agent-out family classification beats chance in 7/15 units. Newcomers classified by earlier units' family fields: 4/11 vs 14% chance (p = 0.06). NE32 triplet: 1/3 aligns with the OpenAI field (descriptive). Round 1b: by behavior, newcomers 3/9 (chance 0.15, p 0.14). |
| E interventional | predicts the change across a natural experiment | 0 | Round 1: none used. **Round 1b:** NE06 (Google-only scaffold change, #20) attempted on behavior and content: no Google-specific shift, and the manipulation itself is village-wide in the logs (actions per turn halved for every agent), so no family-specific intervention exists outside the holdout (NE20). |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 2 (1b; round 1: 1) | `analysis/synthetic.py` F1–F5. All tests have nominal size; power is reported at village N and sampling. The synthetic run exposed and fixed two estimator flaws before real data (invariance baseline; window-demeaned co-movement). **Round 1b:** every content result replicates with gte-modernbert (a different lineage), with DQ5's shared style residuals and after removing restatements or copies. Not done: whitening dimension. |
| G ground truth | agrees with known structure | 1 | Families are recoverable from content (7/15) and from style features (10/15). Rooms come out as the coupling blocks (co-movement b_room > b_lab 9/10; talk b_room p < 0.05 5/10), consistent with H05. |
| H comparative | beats the named rivals | 0 | For H13 as stated (a family *position* field, family coupling), the rivals win: the style rival absorbs the field (S-a 0/15; S-b leaves a period-specific part in only 3/14), and the room rival carries the coupling. The reframed reading (a stable, style-borne family field) is consistent with every rival comparison. |
| I transfer | holds in other same-mode periods, including the holdout | 1 | The family field is invariant across regime III periods (split-half cos 0.84 / 0.93 / 0.88 vs a regrouping null of 0.76, p = 0.008). Holdout transfer (C3) written, not run. |

## Prediction
*Written 2026-10-03 23:50 UTC, before any real-data run.*

**What I had seen when writing this** (sampling design only):
- the family composition of each unit: Anthropic 5–11, OpenAI 3–9, Google 1–4, others mostly singletons; #51 has Moonshot, DeepSeek and Zhipu pairs;
- chat statements per agent-day (median 9–37 by period; 10th percentile 1–8);
- the lab × room cross-tab of the two-room periods: #best holds about one agent per lab, so lab and room are well crossed;
- the #51 role assignments: shared roles are mostly cross-family; one same-family pair, the YouTubers GPT-5.2 and GPT-5.6 Terra.

I have not computed any alignment, field, coupling, lexical or correlation statistic, and I have not read H01's real-data outputs.

**Also known going in** (from other cards):
- H02: pairwise activity couplings are noise; same-lab enrichment 1.11;
- H05: talk coupling is room-structured;
- H09 E3: family explains 41–77% of between-agent variance in action statistics;
- H01 Amendment 3: the regime III agent field h_i failed its invariance check (median cos 0.31 vs a −0.02 baseline).

**My prior** is that families carry fields and rooms carry couplings. Family identity is a strong static content offset, part writing style and part stance. Dynamic coupling (talk timing, content co-movement) is organized by room, not by family.

- **P1 (a1, family field exists beyond the goal field).** T_field > 0 with lab-permutation p < 0.05 in ≥ 2/3 of counted units, and the random-effects summary of T_field > 0 (95% CI excludes 0). *Falsifier:* p ≥ 0.05 in more than 1/3 of units.
- **P2 (a2, the field is not only writing style).** After style-feature residualization, T_field stays > 0 with p < 0.05 in ≥ 2/3 of the units where P1 passed, and median retention ≥ 0.5. *Falsifier:* median retention < 0.25, or survival in < 1/3. Then the family field is writing style.
- **P3 (a3, invariance).** The family-level split-half cos has median ≥ 0.5 over {Anthropic, OpenAI, Google}, above the cross-family baseline: **passes**. The agent-level median is < 0.5 (consistent with H01): **fails**. So the family field may be treated as a regime III family constant, and agent fields may not. *Falsifier:* family-level median < 0.5.
- **P4 (a4, a period-specific part).** After removing cross-fitted per-agent offsets, T' > 0 with p < 0.05 in ≥ 1/3 of the regime III units where it is computable, with T'/T_field median between 0.2 and 0.7. That is, mostly a fixed offset, plus a smaller position part. *Falsifiers:* T' ≈ 0 everywhere, meaning a fixed offset only; or T' ≈ T, meaning nothing fixed.
- **P5 (b1, no family homophily in talk timing).**
  - In one-room units (40, 51a–e), Δ_talk = J_in − J_out has lab-permutation p ≥ 0.05 in ≥ 2/3, and the RE summary of the enrichment J_in/J_out is < 1.3 (H02: 1.11).
  - In two-room units, the room-adjusted b_lab (talk, c) has p ≥ 0.05 in ≥ 2/3.
  - *Falsifier (for this "no" prediction):* Δ_talk > 0 at p < 0.05 in ≥ 1/2 of one-room units, or a room-adjusted b_lab significant in ≥ 1/2 of two-room units. Either would support HH89's homophilous coupling.
- **P6 (b2, content co-movement is not family-structured).** Δ_content > 0 at p < 0.05 in < 1/2 of counted units, and the RE summary of Δ_content is < 0.02 (in J units).
  - Overall co-movement (mean r) beats the rotation null in two-room units (room-driven).
  - *Falsifier:* Δ_content > 0 at p < 0.05 in ≥ 1/2 of units. That would be family coupling in content (H13(b) supported).
- **P7 (c, family vs room; D9.2 for fields, D9.2′ for couplings).** In two-room units:
  - **talk (y1):** b_room > b_lab in ≥ 2/3; b_room p < 0.05 in ≥ 1/2; b_lab p ≥ 0.05 in ≥ 2/3;
  - **content field (y2):** b_lab > 0 at p < 0.05 in ≥ 2/3 (family identity persists across rooms), and b_room > 0 at p < 0.05 in ≥ 1/2 (room-specific tasks in #35, #41, #44);
  - **content co-movement (y3):** b_room > b_lab in ≥ 2/3;
  - **lexical (y4, HH10):** b_lab > b_room in ≥ 2/3, with b_room > 0 (vocabulary converging within a room) in ≥ 1/2. Direction only.
  - *Falsifiers:* y2 b_lab significant in < 1/3, meaning room erases family; or y1 b_lab > b_room in ≥ 1/2.
- **P8 (a5 + d, HH10 lexical magnetization and unfitted classification).**
  - The Anthropic "genuinely" rate is ≥ 2× the other agents' rate, with lab-permutation p < 0.05, in ≥ 2/3 of counted units.
  - T_lex > 0 at p < 0.05 in ≥ 2/3.
  - Leave-one-agent-out family classification (d1) beats the permutation null (p < 0.05) in ≥ 2/3.
  - If P3 passes: newcomers (d2) are classified into their own family at ≥ 60% (chance ≈ 1/K) and above the permutation null.
  - *Falsifiers:* rate ratio < 1.5 in most units; d1 at chance in ≥ 1/2.
- **Descriptive (no verdict):** d3 (NE32 triplet), within-unit stationarity of h_f, K×K matrices and loop gains, R²_fam, |h_f|.

**Overall reading (fixed in advance):**
- "**Families carry fields**" is supported if P1, P2 and P3 pass.
- "**Families couple by family**" (HH89) is supported if P5 or P6 is falsified in the family direction. It is refuted for this sampling if both P5 and P6 hold.
- "**Family persists across rooms**" (D9.2) is supported if P7-y2 passes. "**Room dominates coupling**" (D9.2′) is supported if P7-y1 and P7-y3 pass.

### Amendment 1 (2026-10-04 ~00:15 UTC, after the synthetic validation, before any real-data run)
**What I had seen:**
- the synthetic validation (`analysis/synthetic.py`, fast and full runs);
- generic instrument statistics of the real data, used to calibrate the synthetic world. These are agent-day resultant length (0.46–0.79), day-field norm (0.2–0.53), |δ| (0.36–0.62), agent day-to-day consistency of δ (0.31–0.82), and the share of statement-vector variance explained by style features per unit (0.13–0.37).

None of these contrasts families or rooms. Changes:
1. **a3 null and pass rule.** The cross-family baseline is negative by construction: day-demeaned family fields sum to about 0, giving −0.2 to −0.4 in the synthetic. With a persistent roster, stable *agent* offsets alone make a family's mean look invariant: split-half cos ≈ 0.75 with **no** family field. The baseline is now a **fixed random regrouping** of the agent pool (one global permutation of agent → lab, applied in every unit). **Pass rule:** family median cos ≥ 0.5 **and** above the regrouping null (p < 0.05). In the synthetic, a static family field passes (0.93 vs null 0.81) and a period-specific one fails (0.52 < 0.69).
2. **a4 / P4.** T'/T is not a share. It depends on how stable the agent offsets are: in the synthetic it is ≈ 0 for a static family field, ≈ 1.1 for half static, and ≈ 1.3 for period-specific. **P4 becomes:** T' > 0 at p < 0.05 in ≥ 1/3 of the units where computable, meaning a period-specific family part exists. The ratio is descriptive. Projection removal is primary; subtraction is a variant.
3. **b2.** x = v − the agent's unit mean, **without** removing the window mean. Window-demeaning with ~8 agents per window gives every pair r ≈ −1/(n−1) and makes the naive mean-field inversion singular (synthetic Δ̂ in the thousands). The common window field now adds a uniform positive correlation, which cancels in J_in − J_out. The window-demeaned within − across contrast is reported as a variant. P6's rotation-null clause is **dropped**: it is trivially rejected once the common field is kept. Room-driven co-movement is tested by P7-y3 only.
4. **Power** (synthetic, village sampling; full numbers in Results):
   - the family-field test at a family share of 10% of the agent-offset variance has power 0.24 / 0.53 / 0.90 (units 37 / 41 / 51b), and 0.57 / 0.91 / 1.0 at 20%;
   - content co-movement Δ has power 0.22 at a true J_in − J_out = 0.04 and 0.73 at 0.08;
   - talk Δ has power 0.44 at J_in / J_out = 0.08 / 0.02 and 1.0 at 0.15 / 0.02.

   So "no family coupling" verdicts (P5, P6) exclude only couplings of roughly that size.

### Confirmatory predictions for the locked holdout (C1–C6)
*Written 2026-10-04 ~00:45 UTC, after exploratory round 1 and its post hoc diagnostics, before any holdout data was built or read. They are applied mechanically by `analysis/confirm.py` (`PREDICTIONS`), which stores a hash of this section with its output. Not run: needs Vivian's sign-off and `--confirm --i-understand-this-uses-the-locked-holdout`.*

**Held-out units** (goal periods split at catalogued step changes):
- 45a 06-01 → 06-02 (NE19), descriptive (2 days);
- 45b 06-03 → 06-05 (NE20: Anthropic one tool call per turn);
- 46a 06-08 → 06-10;
- 46b 06-11 → 06-13 (NE22; 06-13 is the #best-only Saturday);
- 47 06-15 → 06-19;
- 49 06-23 → 06-26;
- 50a 06-29 → 06-30, descriptive (2 days);
- 50b 07-01 → 07-03 (NE25);
- 51t 09-07 → 09-18 (#51 tail).

#43 and #48 (one day each) are excluded: H_i needs ≥ 2 days. Counted: units with ≥ 3 days. A unit is "two-room" if ≥ 2 rooms each hold ≥ 2 room-stable agents (rule applied from room data). All estimators, thresholds and nulls are as in exploration (`explore.run_unit`).

- **C1 (a family field exists).** The RE summary of T_field over counted held-out units is > 0 (95% CI excludes 0), and p < 0.05 in ≥ 1/2 of them. Exploration: 9/15, RE 0.080 [0.024, 0.137].
- **C2 (it is writing style).**
  - The RE summary of the style-residualized (S-a) T_field has a 95% CI that includes 0, with a point estimate ≤ 0.25 × the raw RE.
  - In two-room held-out units, S-a keeps the room field and removes the family term: y2 b_room on residualized vectors at p < 0.05 in ≥ 1/2, and y2 b_lab at p < 0.05 in ≤ 1/3. Exploration: 8/10 and 0/10.
- **C3 (the family field transfers).** Family fields estimated on exploration regime III units predict those on held-out regime III units: median over {Anthropic, OpenAI, Google} of cos(h_f^explore, h_f^holdout) ≥ 0.5, and above the fixed random-regrouping null (p < 0.05). Exploration split-half: 0.88 vs a 0.76 null.
- **C4 (style features alone carry family identity).** T_field computed on agents' mean style-feature vectors has p < 0.05 in ≥ 2/3 of counted held-out units. Exploration, post hoc: 14/15. The confirmatory version uses agent-day feature means weighted by statement counts, standardized across agents.
- **C5 (no family coupling).**
  - The RE of Δ_talk has a 95% CI that includes 0 and |μ| < 0.05.
  - The RE of Δ_content has a 95% CI that includes 0 and |μ| < 0.03.
  - The room-adjusted talk b_lab is n.s. in all but at most one two-room held-out unit.
- **C6 (rooms carry coupling).** In two-room held-out units, b_room > b_lab for content co-movement (y3) in ≥ 2/3, and the RE of b_room(y3) is > 0 (CI excludes 0).
- **Overall:**
  - **Confirmed** ("model families carry a stable, style-borne field and do not couple by family") if C1, C2, C3 and C5 pass.
  - **Refuted** if any of these happens: C1's RE CI includes 0; the S-a RE is > 0 with its CI excluding 0 (a non-style family field); C5 shows family coupling with a CI excluding 0 in the positive direction.
  - Otherwise **inconclusive**. C4 and C6 are secondary.
- **Power caveats.** Only 3–4 two-room held-out units, so C2-room and C6 rest on few units. The one-room held-out units (49, 50b, 51t) carry most of the C5 talk test.

### Amendment 2: round-1b pre-registration of the behavioral family test (HH267) (2026-10-04 07:12 UTC, before any behavioral statistic was computed)
**What I had seen:** the round-1 results above; DQ5's style check (`style_resid_check.json`: shared `style_resid_period` leaves 1/16 units significant in both models); H46 (style drifts with context and resets at erasure; style shifts under assigned registers); H09 E3 (family explains 41–77% of between-agent variance in *action statistics*, a prior for this test); H56 (family differences in turn-level statistics survive scaffold removal, η² 0.40); the `behavior_states_v3` schema and validation notes. I have not computed any behavioral statistic by agent or family.

**Behavior state of an agent-day** (*agent state (behavior, agent-day)*, proposed as a named variant): from `behavior_states_v3` windows that are active and labelled, the mean of the 11 state probabilities `p_*` (Jev v3.1; probability vectors, not argmax), plus four rates: log(1 + actions per active window), real failure rate n_errors / n_actions (smoothed with 1 pseudo-failure in 15 actions, the village mean), log(1 + successful commits per window), log(1 + file writes per window). Agent-days need ≥ 6 active labelled windows (30 min). Each of the 15 features is z-scored within the unit; the agent-day vector is day-demeaned exactly like the content state (a1), and H_i^B is the agent's mean over ≥ 2 days. Variant *B+tools*: three more features, the agent-day shares of bash, GUI (click/key/scroll/type/mouse) and other tool calls (`actions.action`).

**Predictions (applied to the same 15 counted units; replication, templated):**
- **B1 (behavioral family field exists).** T_field^B > 0 with lab-permutation p < 0.05 in ≥ 2/3 of counted units, and its RE summary CI excludes 0. Credence 0.65.
- **B2 (it is not style).** In a pair regression of behavior-field alignment cos(H_i^B, H_j^B) on same-lab with the agents' style-feature similarity (cosine of mean standardized 20-feature vectors) as a covariate, b_lab > 0 at node-permutation p < 0.05 in ≥ 1/2 of counted units and the RE of b_lab excludes 0. Credence 0.5.
- **B3 (invariance).** Family-level split-half cos of behavioral family fields over regime III units ≥ 0.5 and above the fixed random-regrouping null (p < 0.05). Credence 0.5.
- **B4 (behavior carries family better than style-free words).** Leave-one-agent-out family classification from H^B beats the lab-permutation null in ≥ 1/2 of units, and beats the classification from style-residualized content (shared `style_resid_period`, bge) in more units than it loses. Credence 0.5.
- **Descriptive:** per-feature family η² (which behaviors carry the field); failure-rate family contrast; behavior vs room in two-room units (b_lab vs b_room, as P7).
- **Overall reading (fixed now):** HH267 "family fields live in behavior, not words" is **supported** if B1 and B2 pass, **failed** if B1 fails, otherwise mixed. Natives (NE06, NE32, G35) are written in their folders.
- **Caveats stated in advance:** Jev reads window evidence that can include the agent's own narration, so family writing style could leak into state labels; family-specific harness behavior (e.g. NE20's Anthropic one-call-per-turn change, held out) would appear as a behavioral family field without any model disposition; in #51, roles shape behavior (same-role pairs are dropped, as in a1).

## Results by goal period
One folder per goal period (round-1b `Verdict (1b)` lines in each; unchanged); verdict rule in `analysis/period_results.py` (failed = no unit detects a family field; mixed = a style-borne field is detected and the no-family-coupling predictions hold; no period can be 'supported' because P2 failed everywhere). T = T_field (a1), S-a = style-residualized T_field, talk/content Δ = J_in − J_out (lab-permutation p), y2 = room-adjusted content-field regression (two-room units).

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G35](goalperiod-subhypotheses/G35/README.md) | exploratory; native (1b) | mixed; 1b mixed (native: style-free words follow rooms, behavior b_lab +0.125 n.s.) | 35: T 0.32 (p 0.000), S-a 0.06 (p 0.16); talk Δ 0.029 (p 0.24); content Δ -0.028 (p 0.49); y2 b_lab/b_room 0.31/0.25 |
| [G36](goalperiod-subhypotheses/G36/README.md) | exploratory | mixed | 36b: T 0.38 (p 0.005), S-a 0.01 (p 0.41); talk Δ 0.049 (p 0.28); content Δ -0.027 (p 0.62); y2 b_lab/b_room 0.43/0.19 |
| [G37](goalperiod-subhypotheses/G37/README.md) | exploratory | failed | 37: T -0.08 (p 0.784), S-a 0.03 (p 0.31); talk Δ -0.029 (p 0.41); content Δ -0.655 (p 0.75); y2 b_lab/b_room -0.08/0.35 |
| [G38](goalperiod-subhypotheses/G38/README.md) | exploratory | mixed | 38a: T 0.11 (p 0.179), S-a -0.01 (p 0.43); talk Δ -0.035 (p 0.72); content Δ -0.060 (p 0.58); y2 b_lab/b_room 0.18/0.89<br>38b: T -0.03 (p 0.455), S-a -0.08 (p 0.77); talk Δ -0.486 (p 0.99); content Δ -0.001 (p 0.30); y2 b_lab/b_room 0.08/0.89<br>38c: T 0.12 (p 0.156), S-a 0.01 (p 0.38); talk Δ -0.041 (p 0.56); content Δ -0.047 (p 0.61); y2 b_lab/b_room 0.14/0.86 |
| [G39](goalperiod-subhypotheses/G39/README.md) | exploratory | mixed | 39: T 0.17 (p 0.040), S-a -0.13 (p 0.99); talk Δ -0.119 (p 0.77); content Δ 0.081 (p 0.03); y2 b_lab/b_room 0.17/0.04 |
| [G40](goalperiod-subhypotheses/G40/README.md) | exploratory | mixed | 40: T 0.32 (p 0.007), S-a -0.05 (p 0.74); talk Δ 0.040 (p 0.21); content Δ 0.017 (p 0.15) |
| [G41](goalperiod-subhypotheses/G41/README.md) | exploratory | mixed | 41: T 0.28 (p 0.011), S-a -0.09 (p 0.91); talk Δ 0.002 (p 0.41); content Δ 0.032 (p 0.07); y2 b_lab/b_room 0.26/0.47 |
| [G42](goalperiod-subhypotheses/G42/README.md) | exploratory | mixed | 42: T 0.22 (p 0.009), S-a 0.06 (p 0.18); talk Δ -0.307 (p 0.90); content Δ -0.033 (p 0.50); y2 b_lab/b_room 0.16/0.33 |
| [G44](goalperiod-subhypotheses/G44/README.md) | exploratory | failed | 44: T 0.06 (p 0.185), S-a 0.05 (p 0.23); talk Δ -0.008 (p 0.50); content Δ -0.028 (p 0.34); y2 b_lab/b_room 0.06/0.72 |
| [G51](goalperiod-subhypotheses/G51/README.md) | exploratory | mixed | 51a: T 0.06 (p 0.047), S-a 0.02 (p 0.21); talk Δ 0.084 (p 0.01); content Δ -0.005 (p 0.40)<br>51b: T 0.07 (p 0.009), S-a -0.01 (p 0.61); talk Δ 0.026 (p 0.23); content Δ -0.002 (p 0.29)<br>51c: T 0.09 (p 0.002), S-a 0.04 (p 0.06); talk Δ -0.010 (p 0.51); content Δ -0.001 (p 0.17)<br>51d: T 0.01 (p 0.379), S-a -0.03 (p 0.86); talk Δ -0.053 (p 0.68); content Δ -0.008 (p 0.40)<br>51e: T 0.01 (p 0.341), S-a -0.03 (p 0.79); talk Δ -0.116 (p 0.86); content Δ -0.049 (p 0.76) |
| [NE06](goalperiod-subhypotheses/NE06/README.md) (#20) | native (1b) | failed | Google behavior DiD percentile 0.69 (36 relabelings); manipulation absent: actions per turn halved for all agents on 11-20 |
| [NE32](goalperiod-subhypotheses/NE32/README.md) (#51 newcomers) | native (1b) | failed | behavior classifies 3/9 newcomers (chance 0.15, p 0.14); style-free words 2/9 |

## Results

### Exploratory round 1 (2026-10-04; non-holdout only, asserted in every script)
**Scope.** 16 units (15 counted, 51e descriptive), 57,403 agent chat statements, N = 10–27 agents per unit, K = 2–5 multi-member labs. Labeled exploratory: eight predictions, several statistics each. Per-unit p-values are descriptive; the verdicts are the pre-registered count rules plus random-effects (RE) summaries.

**Scripts:**
- `scheme/build.py`;
- `analysis/{h13lib,synthetic,explore,posthoc,figures,period_folders,period_results,confirm}.py`.

**Numbers:** `data/processed/H13-family-fields/{synthetic_validation,explore,posthoc}.json` and `G<NN>/results_u<unit>.json`.

**Figures:**
- `figures/summary_round1.pdf` (one-page summary);
- `figures/synthetic_validation.pdf`;
- `G<NN>/figures/H13_G<NN>.pdf` (per period: family-ordered alignment heatmaps and K×K matrices).

**Synthetic validation (axis F)** (village N, family compositions and statement counts; `synthetic.py`):
- **F1, family-field test.**
  - Size: 0.01–0.035.
  - Power at a family share of 10% / 20% of the agent-offset variance: 0.24 / 0.57 (unit 37 design, N = 10, 3 days), 0.53 / 0.91 (#41, N = 14, 5 days), 0.90 / 1.0 (#51b, N = 27, 19 days).
  - Leave-one-out classification is less powerful (0.34 / 0.63 for #41).
- **F2, invariance and the fixed-offset rival.**
  - With a fixed roster, stable agent offsets alone give a family split-half cos of 0.77 with no family field, which is why the regrouping null was adopted (Amendment 1).
  - A static family field passes (0.91 vs 0.81; power 1.0); a period-specific one fails (0.53 vs 0.68).
  - S-b detects a period-specific part with power 0.96–1.0 at size 0.04.
- **F3, content K×K.** Size 0.05. Power 0.22 / 0.73 / 1.0 at a true J_in − J_out of 0.04 / 0.08 / 0.13. Δ̂ is attenuated (0.3–0.8 of the true value).
- **F4, talk K×K (kinetic Ising, ~10% talk activity).**
  - Size 0.06; power 0.44 / 1.0 at J_in / J_out = 0.08 / 0.02 and 0.15 / 0.02.
  - A room-only coupling world does **not** trigger the family test (0.06; room-adjusted b_lab 0.04).
- **F5, family vs room (content field, #41 design).** b_lab and b_room separate cleanly (power ≥ 0.975, cross-talk ≤ 0.075).

**Outcome vs prediction**

| | Prediction | Outcome | Verdict |
| --- | --- | --- | --- |
| P1 | family field beyond the day field: p < 0.05 in ≥ 2/3 units; RE > 0 | p < 0.05 in **9/15** (35, 36b, 39, 40, 41, 42, 51a, 51b, 51c; needed 10). RE T = **0.080 [0.024, 0.137]**, I² = 0.20. R²_fam 0.10–0.48. Fails in 37 (free week, K = 2), 38a–c (K = 2; a large room field adds variance), 44, 51d | **mixed**: count rule fails by one unit; RE passes |
| P2 | survives style residualization in ≥ 2/3 of P1 units; median retention ≥ 0.5 | **0/9**; median retention 0.03; RE T(S-a) = **−0.001 [−0.037, 0.035]** | **falsified**: the family field is writing style |
| P3 | family-level invariance passes; agent-level fails | family split-half cos Anthropic 0.84, OpenAI 0.93, Google 0.88 (median 0.88) vs regrouping null 0.76, **p = 0.008**; all-pairs 0.41 vs 0.22 (p = 0.004). Agent level: median **0.81** (27 agents). After S-a: 0.75 vs 0.67 (p = 0.11) | family part **passed**; agent part **wrong** (agent offsets are stable too) |
| P4 (amended) | period-specific family part (S-b T′ p < 0.05) in ≥ 1/3 | **3/14** (36b, 40, 51a) | **failed**: the family field is a fixed per-agent offset |
| P5 | no family homophily in talk timing | one-room units: Δ_talk n.s. in **4/5** (exception: 51a, Δ = 0.084, p = 0.005). Two-room units: room-adjusted talk b_lab n.s. in **10/10**, RE −0.004 [−0.017, 0.009]. RE Δ_talk 0.002 [−0.040, 0.045]; one-room RE 0.029 [−0.032, 0.089]. The enrichment ratio J_in/J_out was not computable as specified (J_out ≈ 0.005–0.04 makes it explode: 6.7, 17, 1.25, 0.76, −6.2) | **supported** (excludes couplings ≳ 0.1–0.15; F4) |
| P6 | content co-movement not family-structured | Δ_content p < 0.05 in **1/15** (39); RE **−0.002 [−0.019, 0.015]**. Window-demeaned variant agrees | **supported** (excludes Δ ≳ 0.08; F3) |
| P7-y1 | talk: room > lab ≥ 2/3; b_room sig ≥ 1/2; b_lab n.s. ≥ 2/3 | room > lab **8/10**; b_room p < 0.05 **5/10**; b_lab n.s. **10/10**. RE b_room 0.016 [0.005, 0.027] | **supported** (D9.2′ for coupling) |
| P7-y2 | content field: b_lab sig ≥ 2/3; b_room sig ≥ 1/2 | b_lab p < 0.05 **7/10**, RE 0.137 [0.043, 0.230]; b_room p < 0.05 **9/10**, RE 0.489 [0.286, 0.692] (I² = 0.77; largest in #38 and #44) | **supported** (D9.2 for the field), but see post hoc: the cross-room family term is style |
| P7-y3 | co-movement: room > lab ≥ 2/3 | **9/10**; RE b_room 0.217 [0.163, 0.271] vs b_lab 0.013 [−0.013, 0.038] | **supported** |
| P7-y4 | lexical: lab > room ≥ 2/3; b_room > 0 ≥ 1/2 | lab > room **5/10**; b_room > 0 **9/10** (p < 0.05 in 7/10). RE b_lab 0.110 ≈ b_room 0.102 | **mixed**: vocabulary has a family part *and* converges within rooms (HH10's convergence check: yes) |
| P8 | 'genuinely' ratio ≥ 2 and p < 0.05 in ≥ 2/3; T_lex ≥ 2/3; LOO ≥ 2/3; newcomers ≥ 60% | 'genuinely' **3/15** (37, 38a, 42; ratio ≥ 2 in 7/15, e.g. 13× in 38a, but the word is rare, 0–0.8 per 1k words, and Anthropic is *not* enriched in 35, 36b, 40, 41). T_lex **9/15**. LOO **7/15**. Newcomers **4/11** (36%; chance 14%, p = 0.06): correct for GPT-5.6 Terra and Luna, Kimi K3, Gemini 3.8 Flash; all four new Anthropic models missed | **failed** |
| d3 | NE32 triplet (descriptive) | 07-09: only Luna (72 statements) aligns with the OpenAI field (0.33); Sol (4 statements) and Terra (8) are noise. Triplet mutual cos 0.33 vs triplet–incumbent −0.06 (shared onboarding situation and family are confounded) | descriptive |

**Post hoc diagnostics** (`analysis/posthoc.py`, written after seeing the P2 result; labeled post hoc). The worry was that S-a over-removes: 20 features against 10–27 agents could absorb any agent-level offset.
- **S-a is selective.** On the residualized vectors the room field survives (y2 b_room p < 0.05 in 8/10; median 0.32 vs 0.41 raw), while the cross-room family term vanishes (b_lab 0/10). Style residualization removes family, not agent-level structure in general.
- **S-a′, a gentler rival** (the style→embedding map estimated from within-agent variation only), leaves about a third of the field. Median T 0.042 vs 0.114 raw; significant in 4/15 (35, 40, 42, 51c); y2 b_lab 2/10. So "mostly style" is robust; "only style" is not established.
- **The 20 style features alone** (agent means, no embeddings) carry family identity more reliably than the embeddings: T p < 0.05 in **14/15**, leave-one-out in **10/15**.
- **Per family:** the embedding field is carried by **OpenAI** (median within − across cos +0.26) and **Google** (+0.31), not **Anthropic** (+0.03). Caveat 2 applies.

**What this means.**
1. **Model families do carry their own field in content space:** a direction shared by a lab's agents beyond the day's goal field. It is stable across periods and families (exception (b) holds at the family level), but most of it is **writing style**: formatting, punctuation and function-word rates. A fixed per-agent offset explains it; no period-specific "family stance" is detectable (S-b 3/14). HH10's "genuinely" magnetization is real but rare and intermittent.
2. **Families do not couple by family.**
   - The K×K family coupling matrix is flat in talk timing (RE Δ ≈ 0, matching H02's 1.11) and in 30-min content co-movement.
   - The ~9-parameter K×K matrix has no homophily to report at this sampling, down to couplings of about 0.1 (talk) and 0.08 (content).
   - HH89 / HH75 (homophilous coupling) is **not supported**; D1.1.b (family members more coupled once the shared prior is removed) is **not supported**.
3. **Rooms carry the coupling** (D9.2′ for dynamics), for talk timing (consistent with H05), content co-movement and vocabulary convergence. Family identity persists across rooms (D9.2 for the field), but only as style.
4. **Model reading** (vector spins, model 11): the family enters as a static, style-borne field h_f (the "shared pretraining prior" of the paper's null hierarchy), not as a coupling. Mixed-family swarms show vendor *style* bias with no measurable vendor *homophily* in who co-moves with whom.

**Deviations and amendments after seeing data** (all labeled):
1. P5's "RE of J_in/J_out < 1.3" was not computable: J_out ≈ 0 makes the ratio explode. The RE of Δ is reported instead, a deviation decided after seeing the ratios.
2. `posthoc.py` (S-a′, the S-a room check, style features alone, per-family breakdown) was written after seeing P2.
3. The period verdict rule (`period_results.py`) was fixed after seeing the data. Counting a significant room-adjusted y2 b_lab as "detects a family field" moved **G38 from failed to mixed**: a1 failed in 38a–c, while y2 b_lab passed in 38a and 38c. Under an a1-only rule G38 would be "failed".

**Caveats.**
1. **S-a is the maximal style rival.** It removes any family position that co-varies with style. The post hoc S-a′ keeps about a third of the field in 4/15 units, so a small non-style family field cannot be excluded.
2. **Day-mean removal attenuates the largest family.** Anthropic is ~40% of agents, so its own field is partly absorbed into the day mean. The per-family numbers are biased against Anthropic; the permutation tests stay valid. A leave-family-out day mean is the fix (next steps).
3. **a1 is conservative in two-room periods.** The large room field (y2 b_room up to 0.89) inflates the variance of T_field. #38 shows a family term only once the room field is controlled.
4. **Power.** The "no family coupling" results exclude only couplings of about F3/F4 size (Δ ≳ 0.08 content, ≳ 0.1–0.15 talk). Talk Δ CIs are wide in 4-hour units (e.g. 38b [−2.35, −0.10]).
5. **#51 roles** are agent-specific fields. Same-role pairs were dropped, but a correlation between role topics and labs cannot be fully excluded (role directions were not projected out).
6. **One embedding model** (bge-small) and one whitening dimension (32). No embedding swap yet.
7. Content vectors embed what agents *say* (narration is a claim, not ground truth). Talk spins were not cleaned of scheduler artifacts beyond the cross-day surrogate.
8. **Newcomer candidates** included single-agent "families", per the card (e.g. the fine-tuned Kimi leader, which attracted two wrong guesses). Chance is 14%.
9. **Data quirks.**
   - 2026-04-22 (38c) had only 9 talk-minutes in the whole village.
   - GPT-5 (alone in #rest in #40) and the #focus pair (51c) are excluded from the K×K fits.
   - #36's regime II day (03-23) was dropped.
   - The "Fine-tuned (Kimi)" lab label is kept separate from Moonshot.

**Disk and compute.** `data/processed/H13-family-fields/` is 3.8 MB (including the dry-run). Scheme build ~5 s; synthetic 217 s; explore 90 s; post hoc ~60 s; dry run ~40 s. Single process, ≤ 2 BLAS threads. No network; mentions not used.

**Next steps.**
1. Sign-off, then `confirm.py --confirm --i-understand-this-uses-the-locked-holdout` (C1–C6).
2. Robustness: embedding-model swap; whitening n = 16 / 64; leave-family-out and room-day means for a1.
3. A family **style fingerprint**: which features and markers carry each lab's field (a lexical/format decomposition). Usable as a style control in every content-alignment hypothesis (H01 P2, H12).
4. Family-specific natural experiments as interventions on the field: NE20 (Anthropic one tool call per turn, 06-03, holdout); NE05/NE06 in regime I. Does the style field move?
5. Family *susceptibility*: response to the goal field at kickoffs by family (H01 D6.1.a). This is a dynamic field response, which a static-field analysis cannot see.
6. Event-time (reply / Hawkes) family-block coupling for more power than 1-min spins.

## Round 1b (improved data, 2026-10-04)
*Re-run of round 1's pre-registered statistics (P1–P8 unchanged) on the corrected inputs, plus the behavioral family test (HH267; Amendment 2, written 07:12 UTC before any behavioral statistic) and three period-native tests (NE06, NE32, G35; predictions written 07:13 UTC in their folders before running). Non-holdout only, asserted in every script; `confirm.py` not run.*

**What changed in the inputs.**
- **Embeddings (DQ5):** statement vectors now come from the shared statement-level files (`statements_white32_<model>`), for bge-small (identical to round 1's own whitening: agent-day cosine 1.000) and the second model gte-modernbert. Style rivals: H13's own within-unit S-a (pre-registered) and DQ5's shared `style_resid_period` vectors. Dedupe: DQ5 restatement flags (either model) and copy flags (both models).
- **Talk spins** from `activity_bins_fixed` (DQ8): 13–40% more pair-days pass the ≥ 4-flip rule.
- **Behavior (DQ3):** Jev v3.1 state probabilities and real failure rates (`n_errors`, not stderr) per agent-day, plus commit and file-write rates; tool mix from `actions`.
- Code (old paths unchanged): `scheme/build.py --r1b --model … --dedupe …`, `analysis/explore.py --base … --style own|period`, new `analysis/r1b_behavior.py`, `r1b_summary.py`, `r1b_periods.py`, `r1b_figures.py`. Outputs: `data/processed/H13-family-fields/r1b/` (14 MB). DQ5's own check of H13's estimator on its agent-day table (`embeddings/style_resid_check.json`: 8/16 units → 1/16 under `style_resid_period`, both models) agrees with the numbers below.

**Old vs new (content and talk channels).**

| Prediction | Round 1 (bge, own S-a, old talk table) | Round 1b bge | Round 1b gte | Notes |
| --- | --- | --- | --- | --- |
| P1 family field (count; RE T) | 9/15; 0.080 [0.024, 0.137] | 9/15; 0.080 [0.024, 0.137] | 8/15; 0.085 [0.040, 0.131] | restatements removed: 9/15, 0.084 (bge); 8/15, 0.088 (gte) |
| P2 survives own S-a (count in P1 units; RE) | 0/9; −0.001 [−0.037, 0.035] | 0/9; −0.001 | 0/8; −0.001 | — |
| P2 survives shared `style_resid_period` | – | 1/9 (51c); 0.009 [−0.030, 0.047]; retention 0.09 | 0/8; 0.015 [−0.022, 0.052]; retention 0.07 | DQ5 check: 1/16 in both models |
| P3 family invariance (median cos vs regrouping null) | 0.88 vs 0.76, p 0.008 | 0.88 vs 0.76, p 0.006 | 0.90 vs 0.74, p 0.001 | agent level 0.81 / 0.80 |
| P4 period-specific family part | 3/14 | 3/14 | 1/14 | — |
| P5 talk homophily, one-room (n.s. count; RE Δ) | 4/5; 0.029 [−0.032, 0.089] | 4/5; 0.008 [−0.025, 0.041] | (same spins) | 51a still Δ = 0.080, p 0.008 |
| P5 talk, all units RE Δ; two-room b_lab n.s. | 0.002 [−0.040, 0.045]; 10/10 | −0.003 [−0.021, 0.016]; 10/10 | — | CI 2.3× narrower |
| P6 content co-movement | 1/15; −0.002 | 1/15; −0.002 | 1/15; +0.005 | — |
| P7 y1 talk room > lab | 8/10 | 10/10 | — | — |
| P7 y2 field b_lab / b_room p < 0.05 | 7/10 / 9/10 | 7/10 / 9/10 | 6/10 / 9/10 | — |
| P7 y3 co-movement room > lab | 9/10 | 9/10 | 10/10 | — |
| P8 LOO; newcomers (d2) | 7/15; 4/11 | 7/15; 4/11 | 7/15; 4/11 | lexical tests unchanged (no embeddings) |

**Behavioral family test (HH267, Amendment 2).** Fifteen behavior features per agent-day (11 Jev v3.1 state probabilities, actions, real failures, commits and file writes per window), z-scored within the unit, day-demeaned, agent means over ≥ 2 days; same estimators and nulls as a1.

| Prediction | Observed | Verdict |
| --- | --- | --- |
| B1 behavioral field: p < 0.05 in ≥ 2/3 of units and RE CI > 0 | **3/15** (36b at p = 0.050, 39, 40; 44 and 51a at 0.052–0.057); RE T_B = 0.075 [0.030, 0.121], I² = 0. With tool mix: 3/15, RE 0.088 [0.039, 0.137] | **fail** (count); RE positive |
| B2 not style: b_lab given style similarity, p < 0.05 in ≥ 1/2; RE > 0 | 4/15 (39, 40, 42, 44); RE 0.038 [−0.009, 0.085] | **fail** |
| B3 invariance across regime III units | family median 0.89 vs regrouping null 0.80, p = 0.047; agent level 0.91 | pass (marginal) |
| B4 LOO beats null in ≥ 1/2; beats style-free words in more units than it loses | LOO 4/15 (38c, 39, 40, 41); behavior > style-free words (bge) in 12/15 units, < in 2 | mixed |
| descriptive: family vs room (two-room units) | behavior b_lab RE 0.14 [0.06, 0.22] vs b_room 0.03 [−0.05, 0.11]; lab > room 7/10; style-free words: b_lab ≈ 0, b_room 9/10 (round 1 post hoc) | — |
| descriptive: which behaviors | the field is concentrated in #39/#40 (worlds and their merge): file writes per window (η² 0.84 / 0.73), execute-task, verify-report and monitor-wait occupancy, commits; in #35 failure rate and debug-recover (η² 0.62 / 0.60); nothing in #51 (roles dominate) | — |

**HH267 verdict (rule fixed in Amendment 2): failed** (B1 fails). Families do not carry a strong behavioral field either; there is a weak one (RE ≈ 0.08, stable across periods, room-independent, beats style-free words in classification) that lives mostly in work habits such as file-write and commit cadence in build weeks. That is plausibly partly harness (tool conventions per provider) rather than model disposition, which NE06 could not separate (below).

**Native tests.**
- **NE06 (Google-only scaffold change in #20): failed / uninformative.** Google's behavior change across step 1 is ordinary (percentile 0.69 of 36 relabelings), and the manipulation check fails: actions per turn halved for *every* agent on 11-20 (others 3.63 → 1.80; Gemini 3.56/2.85 → 1.82/1.86). In the logs NE06 is a village-wide turn-structure change (DQ9's confound), so it is no family-specific intervention.
- **NE32 (newcomers to #51 classified by incumbents' behavioral family fields): failed.** 3/9 classifiable newcomers (chance 0.15, p 0.14); style-free words 2/9 (bge), 1/9 (gte). The GPT-5.6 triplet is not recognised as OpenAI by behavior; on its isolated day Terra matches both the OpenAI field and its same-family role-mate, Luna matches its role-mate (DeepSeek) better than the OpenAI field.
- **G35 (#35, room × lab crossed): mixed.** Style-free words follow rooms (b_room 0.21/0.24, p 0.018/0.009) with no lab term (as predicted); behavior has b_lab +0.125 > b_room −0.046 but n.s. (p 0.21; 5 same-lab cross-room pairs).

**Which verdicts change.** None of the round-1 period verdicts change (`**Verdict (1b):**` lines added in G35–G51: same rule, same counts in both models). The card-level readings hold and are now model-robust: a stable family content field (P1 RE, P3) that is writing style (P2 fails under both style rivals and both models), no family coupling (P5 tighter on the fixed table, P6), rooms carry coupling (P7). New: HH267 fails; a weak behavioral family field exists.

**Scorecard after 1b.** F 1 → 2 (content results replicate across two embedding lineages, two style rivals and two dedupe rules, on top of the synthetic F1–F5). E stays 0 (NE06 attempted; not family-specific in the data). D stays 1 (behavioral newcomer test 3/9, n.s.). C, G, H, I unchanged (behavior adds a positive RE but no count pass; the style rival still wins for a family *position* field).
**Figure:** `figures/r1b_behavior_vs_words.pdf`. **Estimates:** 131 rows in `per_period_estimates` (content T and style-residualized T in both models, talk Δ on the fixed table, behavioral T_B, natives).

## Notes
- 2026-10-03: promoted from shortlist 2 (HH10 + HH75 + HH89 (shortlist 2, item 4)).
- 2026-10-03: `chat_core.mentions` is polluted (coordinator note). H13 round 1 does not use mentions at all. Any exposure variant would use `chat_mentions_clean.mentions_roster`.

## Round 2 redirects (2026-10-04)
*From the round-1 reflection (`writeup/round1-reflection/round1-reflection.pdf`).*
- **Where round 1 went sideways:** Family alignment in embeddings turned out to be writing style, which was close to trivial.
- **What the direction is really after:** Do vendors differ in decisions, not prose?
- **H13-R1.** Policy fingerprint: P(next behavior state | current state, context features) differs by family beyond agent identity.
- **H13-R2.** Families differ in susceptibility: who listens to whom (HH98).
- **H13-R3.** Mixed-vendor periods out-produce single-vendor ones (descriptive, confounded; work ledger).

## Round 2 (2026-10-05): graded style rival, newcomer enculturation, family coupling at the read-out call
*Scope: the coordinator's round-2 brief (graded style rival; enculturation of newcomers; power for the no-coupling result) plus H13-R2 (who listens to whom) as a descriptive K×K matrix of the read-out design. H13-R1 (policy fingerprint) and H13-R3 (mixed-vendor output) are not run. Non-reserved data only (`holdout_mask` asserted in every script); `confirm.py` not run; no paid labels.*

### Pre-registration (written 2026-10-05 03:25 UTC, committed before any round-2 statistic on real data)
*Facts seen before writing (sampling design only): the joiner list from `roster` with each joiner's chat-statement counts on its first five days and the reserved flags of those days; the schemas of `text_features`, `reply_pairs`, `behavior_states_v3`, `context_ledger_items`, `call_windows`, `producing_calls`; H46's round-2 card (genre control, per-segment style offset ≈ 5% of per-message style variance, function words identify agents at 0.79); H50's round-2 content read-out estimator and its pooled regime-III J^c_1 = 0.033 [0.027, 0.039]. No family, style-ladder, enculturation or read-out statistic split by lab has been computed.*

**Code (new, behind a switch; round-1 and 1b scripts are untouched):** `analysis/r2lib.py`, `r2_synthetic.py`, `r2_ladder.py`, `r2_encult.py`, `r2_readout.py`, `r2_write.py`. Data: `data/processed/H13-family-fields/r2/`.

#### R2-A. Graded style rival (settles "only style" vs "mostly style")
**Population.** Round-1b units (15 counted plus 51e descriptive), agent chat statements with DQ5 `statements_white32` vectors (bge-small primary, gte-modernbert second) and a `text_features` row. Agent-day means (≥ 3 statements), day-demeaning, agent means (≥ 2 days), T_field, lab permutation (2,000), #51 same-role pairs dropped, delete-one-agent jackknife SE and DerSimonian–Laird RE exactly as round 1 (a1).

**Feature blocks (per statement, standardized within unit).**
- `S20`: H13's 20 style features (`text_features` f_*).
- `core14`: `S20` without the length/markup-count features (log_chars, urls, backticks) and the topic-adjacent ones (digit_share, upper_share, colon; H46).
- `FW50`: the 50 most frequent of H46's 128 closed-class words (list copied, not imported) in non-reserved H13-unit statements with ≥ 10 word tokens; sqrt relative frequency, winsorized at 0.1/99.9%, z-scored; statements with < 10 tokens get 0 plus a short-statement flag.
- `G` (speech-act genre, H46's block): is-reply, parent human, parent automated, parent-pair p_supports / p_opposes / p_asks, max candidate p_reply, has-mention, log(1 + mentions), leading @, 12 DQ3 window probabilities (execute_task is the reference) and a DQ3-missing flag.
- **Genre control (suffix g):** each block is residualized on G within the unit with agent fixed effects; only (G − Ḡ)B̂ is removed, the agent constant is kept (H46's method). So a family difference in speech-act mix stays in the content.

**Maps.** **W** (within-agent): B̂ is fitted on agent-demeaned statements and features, then applied to the full features (round 1's S-a′ form). **P** (pooled): OLS with intercept on all statements (round 1's S-a form). The residual statement vectors are renormalized and pass through the a1 pipeline.

**Ladder (nested within a map).** L0 raw; W1 = W(core14g); W2 = W(S20g); **W3 = W(S20g + FW50g)**; Wf = W(FW50g); P1, P2, P3, Pf likewise. Bridges: S-a (P, raw S20; round 1) and S-a′ (W, raw S20). Speech-act rival PG = P(G) alone. Strength axis: the share of statement-vector variance each map removes (R²_map).

**Why W3 is decisive.** The W map removes only the embedding signature that style features carry within an agent. It cannot remove a family position that merely correlates with family style across agents. P can, so P over-removes by construction. W3 is the gentlest complete linear style control (formatting plus function words, genre kept).

**Predictions.**
- **A-P1 (monotone ladder).** RE T falls as blocks are added (L0 ≥ W1 ≥ W2 ≥ W3; L0 ≥ P1 ≥ P2 ≥ P3), and each P level ≤ the W level with the same block. Credence 0.7.
- **A-P2 (mostly style).** Retention ρ_W3 = RE T(W3) / RE T(L0) lies in (0.10, 0.50]; W3 p < 0.05 in ≤ 4/15 units. Credence 0.5.
- **A-P3 (function words carry part of the field beyond formatting).** ρ_W3 ≤ 0.75 ρ_W2. Credence 0.5.
- **A-P4 (the field is not speech-act mix).** ρ_PG ≥ 0.75, and T on agents' mean G vectors has p < 0.05 in ≤ 5/15 units. Credence 0.6.
- **Reading (fixed now).** *Only style* (at linear resolution): W3 RE CI includes 0, ρ_W3 ≤ 0.25, and synthetic power ≥ 0.8 to detect a non-style family field of one third of the raw field at W3. *Mostly style, with a non-style residual:* W3 RE CI excludes 0 and ρ_W3 ≤ 0.5. *Not mainly style:* ρ_W3 > 0.5. Any other outcome: *mostly style, residual unresolved*.
- **Kill.** ρ_W3 > 0.5 with the W3 RE CI above 0: round 1's "the family field is writing style" is withdrawn as stated.
- **Descriptive.** gte ladder; leave-family-out day mean at L0 and W3 (round-1 caveat 2); T on agents' mean FW50g vectors.

#### R2-B. Enculturation of newcomers
**Joiners.** Agents whose roster join day is a non-reserved day with ≥ 5 chat statements. The joiner's window is its join goal period's non-reserved days from the join day, at most 10 PT days and one regime. Day index d = the d-th window day with ≥ 5 joiner statements, d ≤ 6. *Incumbents* are agents present in the window before the join day. The candidate labs are the labs with ≥ 1 incumbent with ≥ 2 eligible days in the window; the joiner needs its own lab and ≥ 1 other lab among them. From the roster this gives about 20 joiners (regimes I–III); the exact list is fixed by the rule in code.

**Vectors.** DQ5 `statements_white32` (bge primary; gte second), regime-whitened, unit-normalized. Style-free variant: shared `statements_style_resid_period32`. Day mean m_d = incumbents' equal-weight agent-day mean (joiner excluded). Lab field h_g = mean over g's incumbents of their day-demeaned agent means over the window. **Statement-count matching:** every joiner and incumbent agent-day vector entering a cosine statistic is the mean of 5 random statements; statistics are averaged over 20 draws (fewer statements give noisier means and smaller cosines).

**Observables.**
- Lab alignment a(d) = cos(v_{j,d} − m_d, h_own) − mean over other candidate labs g of cos(v_{j,d} − m_d, h_g).
- Room outsiderness r(d) = cos(v_{j,d}, m^room_d) − mean over incumbents i in the room of cos(v_{i,d}, m^room_{d,−i}), with m^room_d the incumbents' mean in the joiner's modal room that day (≥ 2 incumbents).
- Null for a(1): own-lab relabelling (each joiner's own lab replaced by a random candidate lab; 10,000 draws). Slopes: per-joiner OLS over d (joiners with ≥ 3 days), mean slope, joiner bootstrap CI (5,000). Lab-alignment drift is also compared with incumbents' leave-self-out a(d) on the same days (difference in slopes).

**Predictions (direction fixed now).**
- **B-P1 (start at the lab, raw content).** Mean a(1) > 0 with relabelling p < 0.05. Credence 0.6.
- **B-P2 (the lab alignment does not fade).** The mean slope of a(d) is not negative: joiner-bootstrap CI includes 0 or lies above 0. Credence 0.65.
- **B-P3 (style-free content starts neutral).** With `style_resid_period`, a(1) has p ≥ 0.05 and a point estimate ≤ 0.5 × the raw a(1). Credence 0.6.
- **B-P4 (convergence on the room).** Mean r(1) < 0 (CI below 0) and the mean slope of r(d) > 0 (CI above 0). Credence 0.45.
- **Reading.** "Newcomers arrive carrying their lab's style and converge on the room's content" if B-P1, B-P2 and B-P4 pass. "Newcomers start neutral" if B-P1 fails with synthetic power ≥ 0.8 at the planted lab field. **Kill for "the family field is a fixed charge":** slope of a(d) < 0 with CI below 0 (newcomers lose their lab position as they settle).

#### R2-C. Family coupling at the read-out call (power for the no-coupling result)
**Round-1 sensitivity (analytic, stated now).** The minimum detectable effect at 80% power is about 2.8 × the RE SE: Δ_talk 2.8 × 0.0094 ≈ 0.026 and Δ_content 2.8 × 0.0087 ≈ 0.024 in estimator units. F3 attenuation (0.3–0.8) puts the content bound at a true J_in − J_out of roughly 0.03–0.08.

**New design (H50's content read-out estimator, reimplemented here from shared tables).**
- Source m = an agent chat message with a statement vector. Recipient j = a ledger receiver (`context_ledger_items`, kind agent; receiving call r).
- Response B = one of j's next 8 statements after t_m, same PT day, within 30 min.
- Hop h = pos(prod(B)) − pos(r) + 1 in j's non-summary call sequence (`call_windows`, ordered by t_call; `producing_calls`). h = 1 is the read-out call; h = 0 is the call in flight at t_m (posted after m, could not read it).
- y = cos(z_B, z_m) − mean cos(z_B, z_m′), with m′ two seeded random statements of the same sender ≥ 2 h away in the unit.
- J^c_1 = Σ_b w_b [ȳ(1, b) − ȳ(0, b)] over 10-s age bins in [0, 60) s, w_b ∝ n_1b n_0b / (n_1b + n_0b).
- Units: round-1b units with ≥ 200 hop-1 and ≥ 200 hop-0 rows; block bootstrap (days if ≥ 3 days, else 1-h blocks), 400 draws; inverse-variance pooling over regime-III units; #35 (regime II) reported separately.
- **Family partition:** same-lab (sender lab = recipient lab) vs cross-lab rows. Δ_J = J_same − J_cross with paired bootstrap draws. **Primary:** the named-stratified contrast Δ_J^adj = Σ_s w_s (J_same,s − J_cross,s) over s ∈ {named, unnamed} (ledger `ment`), w_s = the unit's share of hop-1 rows in s. Naming is address-gated coupling (×5, H50) and may differ by lab pair.
- This is a partition contrast twice over: read vs in-flight at matched age (contemporaneous convergence and common drives cancel), and same vs cross lab. Reads happen within a room, so rooms are held fixed.
- **Talk (secondary).** For each non-summary call c: talk_c (`call_windows.talk`) on the counts of agent items newly read at c, split same-lab / cross-lab × named / unnamed, with agent-day fixed effects (linear probability). Δβ_talk = named-stratified β_same − β_cross; block bootstrap; pooled.
- **Smallest effect of interest:** Δ_J = 0.5 × the pooled J^c_1 (all rows); Δβ_talk = 0.5 × the pooled β (all reads).
- **Descriptive (H13-R2, who listens to whom):** pooled J^c_1 by sender lab × receiver lab over {Anthropic, OpenAI, Google, other}, and by receiver lab (susceptibility).

**Predictions.**
- **C-P1 (no family coupling in content at the read-out).** Pooled Δ_J^adj CI includes 0 and its upper bound < 0.5 J̄. Credence 0.55.
- **C-P2 (no family coupling in talk at the read-out).** Pooled Δβ_talk CI includes 0 and its upper bound < 0.5 β̄. Credence 0.55.
- **C-P3 (replication of H50).** Pooled regime-III J^c_1 > 0 with CI above 0 and inside [0.018, 0.048].
- **Kill.** Δ_J^adj CI above 0: family coupling exists at the read-out, and round 1's "no family coupling" is withdrawn for content. CI including 0 with an upper bound ≥ 0.5 J̄, or synthetic power < 0.8 at Δ = 0.5 J̄: inconclusive.

#### Synthetic validation first (axis F; `analysis/r2_synthetic.py`, real skeletons, before any real round-2 statistic)
- **A.** Real statements, features, agents and days of every unit. Synthetic U = (real features) × (real within-agent map) + agent offsets permuted across agents (no family link) + real day means + real within-agent residuals permuted across statements. Worlds: S0 style only; S1 = S0 + a random non-style family direction sized to one third of the raw field; S2 = S0 + a family position aligned with family mean style through a different map; NL = S0 + squared style terms (nonlinear style); SG = S0 + a speech-act signature (real family G differences). Required: W3 size ≤ 0.1 per unit and RE CI > 0 in ≤ 10% of replicates in S0; report leakage under NL; W3 power in S1; S2 kept by W and removed by P; SG kept by g levels.
- **B.** Real joiners' and incumbents' statement schedules and incumbents' real vectors; joiner statements replaced. Worlds: J0 neutral; J1 at the lab from day 1; J2 neutral then converging to the lab; J3 a room outsider converging. Required: J0 size ≤ 0.07 for a(1); power at J1.
- **C.** Real rows (hop, age, naming, lab pair, blocks); outcomes replaced. Worlds: N0 no pull; N1 equal pull for all lab pairs; N2 family pull Δ = 0.5 J̄; N3 a family-common drive at both hops (no coupling); N4 only named rows couple and naming is more frequent within labs. Required: size ≤ 0.07 in N0, N1, N3, N4 for Δ_J^adj (N4 tests the stratification); power at N2. Talk: the same with Bernoulli outcomes.

**Estimates.** Per-unit rows to `per_period_estimates` (hypothesis H13, round 2): T at each ladder level (bge), J_same, J_cross, Δ_J^adj and Δβ_talk per unit; enculturation statistics per joiner unit. Period READMEs G35–G51 and NE32 get round-2 blocks.

### Synthetic validation (run 2026-10-05 03:40–04:20 UTC, before any round-2 statistic on real data)
Outputs: `data/processed/H13-family-fields/r2/synthetic_{A,B,C}.json`. Values are means over replicates.

**A (graded ladder; 15 units, 20 replicates per world).** Entries: RE T / share of replicates with RE CI > 0.

| World | L0 | W1 | W2 | **W3** | P3 | S-a | S-a′ | PG |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S0 style only | 0.034 / 0.60 | 0.011 / 0 | 0.005 / 0 | **−0.004 / 0** | −0.070 / 0 | −0.046 / 0 | 0.005 / 0 | 0.011 / 0 |
| NL (+ squared style) | 0.032 / 0.40 | 0.012 / 0.10 | 0.004 / 0.10 | **−0.001 / 0** | −0.068 / 0 | −0.043 / 0 | 0.005 / 0.10 | 0.009 / 0.10 |
| SG (+ speech-act signature) | 0.039 / 0.50 | 0.016 / 0.05 | 0.009 / 0 | **0.002 / 0** | −0.065 / 0 | −0.043 / 0 | 0.007 / 0 | 0.014 / 0 |
| S1 non-style field, c 0.10 | 0.043 / 0.75 | 0.022 / 0.20 | 0.014 / 0.05 | **0.009 / 0.05** | −0.062 / 0 | −0.036 / 0 | 0.014 / 0.05 | 0.020 / 0.20 |
| S1, c 0.15 | 0.059 / 1.0 | 0.041 / 0.75 | 0.033 / 0.50 | **0.027 / 0.30** | −0.055 / 0 | −0.027 / 0 | 0.033 / 0.60 | 0.030 / 0.50 |
| S1, c 0.20 | 0.065 / 1.0 | 0.047 / 0.90 | 0.044 / 0.80 | **0.040 / 0.75** | −0.048 / 0 | −0.019 / 0 | 0.044 / 0.80 | 0.038 / 0.70 |
| S1, c 0.30 | 0.124 / 1.0 | 0.108 / 1.0 | 0.107 / 1.0 | **0.103 / 1.0** | −0.021 / 0 | 0.019 / 0.20 | 0.106 / 1.0 | 0.088 / 1.0 |
| S2 style-aligned position, c 0.15 | 0.053 / 0.95 | 0.032 / 0.50 | 0.027 / 0.25 | **0.022 / 0.25** | −0.054 / 0 | −0.028 / 0 | 0.027 / 0.25 | 0.028 / 0.25 |

Readings. (1) W3 holds size (RE CI > 0 in 0/20 replicates in S0, NL and SG; per-unit rate 0.06–0.10). Squared style terms do not leak into W3. (2) **Every pooled map is biased downward under the style-only world** (P3 −0.070, S-a −0.046, P1 −0.030): a pooled map fits agent offsets through the agents' mean features, which makes same-family residuals anti-aligned. Round 1's S-a value is therefore not centred at 0 when the field is style only. (3) The W3 test has power 0.30 at a non-style field of one third of the raw field (W3 ≈ 0.027) and 0.75 at one half (W3 ≈ 0.040). (4) With agent offsets permuted, the within-agent linear style signature alone gives a raw field of 0.034, about 40% of the real raw RE (0.080). (5) The S2 world (family position aligned with family style) is kept by W and removed by P, as designed.

**B (enculturation; 20 joiners, 200 replicates).** J0 neutral: a(1) relabelling p < 0.05 in 0.07; a-slope CI > 0 in 0.035. J0 places a synthetic joiner nearer the room mean than real incumbents (r(1) +0.07), so the r statistic has no generative null. J0c (an exchangeable pseudo-joiner: a real incumbent of another lab in the same room, removed from the incumbent set): r(1) CI < 0 in 0.03, r-slope CI > 0 in 0.025. Power: J1 (half the lab field, from day 1) a(1) 1.0; J2 (converging to the lab) slope 1.0; J3 (room outsider converging) r(1) CI < 0 in 0.87, r-slope CI > 0 in 1.0.

**C (read-out; 8 eligible regime-III units: 38a, 40, 41, 44, 51a–d; 40 replicates).** Pre-registered day blocks with inverse-variance pooling gave false positives in 0.40 of N0 replicates (unit SEs from 3–8 day blocks are too small and noisy). After Amendment C-A1: N0 size 0.075, N1 0.05, N3 (family-common drive) 0.025, N4 (only named rows couple) 0.0 for Δ_J^adj; the unstratified Δ_J is biased in N4 (−0.010). Power at Δ = 0.5 J̄: **0.55**. Pooling hops 1–2, or using all regime-III units, does not raise it (0.15–0.40). The replicate SD of pooled Δ_J^adj is ≈ 0.011, so the 80%-power MDE is ≈ 0.031, about J̄. With a true Δ = 0 the "supported" rule (upper bound < 0.5 J̄) is met in 0.30 of replicates. Talk: T0 size 0.05; T1 (equal couplings) 0.10, a linear-probability bias of 20% of β̄; power at Δβ = 0.5 β̄ 0.90.

### Amendments (2026-10-05 04:22 UTC, after the synthetic validation, before any round-2 statistic on real data)
- **A-A1 (pooled-map bias).** P-level and PG values are reported next to their S0 reference value. A-P1's clause "each P level ≤ the W level" is dropped as uninformative. A-P4's ρ_PG clause is dropped: S0 gives ρ_PG = 0.32 with no speech-act field. A-P4 is judged on T over agents' mean G vectors alone.
- **A-A2 (the "only style" reading cannot be reached).** It needs W3 power ≥ 0.8 at one third of the raw field, and the synthetic gives 0.30. A W3 RE CI that includes 0 therefore reads "mostly style; a non-style residual below ≈ half of the raw field is not resolved". The stated exclusion bound is the W3 value with 0.8 power (≈ 0.045).
- **A-A3 (calibrated location, descriptive, fixed now).** The real RE values of W3, S-a and P3 are placed on the synthetic S0/S1 curves (c grid) to give an implied non-style field size c*. Model-based; no verdict.
- **B-A1.** No estimator change. The size of the r statistic rests on the J0c world.
- **C-A1 (blocks and pooling).** 1-h blocks in every unit, and fixed-weight pooling of the units' bootstrap draws (weights n₁n₀/(n₁ + n₀) for content, read items for talk). This replaces day blocks with inverse-variance pooling.
- **C-A2 (power).** C-P1 keeps its rule, but it is now known to be reachable in only 30% of true-null worlds. The design excludes a family pull that doubles J̄ (Δ ≥ ≈ 0.031) with 80% power, not one of half that size. A C-P1 outcome with CI ∋ 0 and upper bound ≥ 0.5 J̄ reads "inconclusive at 0.5 J̄; Δ ≥ J̄ excluded" if the upper bound is < J̄.
