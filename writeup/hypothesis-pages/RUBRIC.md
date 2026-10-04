# Hypothesis summary pages: rubric and content rules

Every hypothesis gets a **two-page** RevTeX summary at `hypotheses/H<NN>-<slug>/summary/summary.pdf`. All of them are appended, behind a color-coded table of contents, into `writeup/hypotheses-compendium.pdf`. This is a living status document, **not** the paper.

Build everything (or one hypothesis) with:

```
uv run python infra/summaries/build_summaries.py            # all pages + compendium
uv run python infra/summaries/build_summaries.py --only H05 # one page (skip the compendium)
```

## Files a hypothesis owner writes (in `hypotheses/H<NN>-<slug>/summary/`)

- **`content.tex`**: the prose and math, through these macros, each called once:
  - `\hwhat{...}` **What happened**, ≤ 150 words. What was tested, on which goal periods, what came out, including failures and holdout results. Plain language with numbers.
  - `\hmodel{...}` **Physical model**, ≤ 80 words. Which model from `physics-models/`, what the spins, states, fields and couplings are in village terms.
  - `\hmath{...}` **Math**, ≤ 6 display lines. The model's defining equations (e.g. the Hamiltonian, the kinetic rule, the estimator, the key mean-field relation), in LaTeX math. Define the symbols in `\hmodel`.
  - `\hobs{<figure path relative to summary/>}{<note>}` **Observables figure** and a note of ≤ 80 words. Show the observable that best shows how the strongest sub-hypotheses or periods went. One focused figure, ideally one or two panels, readable at about 4 in wide. Make a new one in `figures/` if the existing ones are full-page summaries.
  - `\htelos{...}` **So what?**, ≤ 130 words. Scope it to the project's purpose: *practically* understanding the dynamics of agent swarms. Be candid, even cynical. Would someone running, steering or aligning a swarm of LLM agents do anything differently because of this? Or is it a curiosity, a measurement artifact, or a restatement of something obvious? Say which.
  - `\hbottom{...}` **Bottom line**, one sentence.
- **Page 2 (added 2026-10-04 at Vivian's request), also in `content.tex`:**
  - `\hresults{...}` **Results vs predictions**, ≤ 150 words or a compact `tabular` sized to `\columnwidth` (≤ 10 rows): each main prediction, what was observed (with numbers), and the verdict.
  - `\hobsb{<figure path>}{<note>}` **Second figure** and a note of ≤ 60 words: synthetic validation, or a second observable that matters (≤ 2.1 in tall at column width). Optional but encouraged.
  - `\hcaveats{...}` **Caveats**, ≤ 120 words: the limits that would change the reading.
  - `\hnext{...}` (optional, ≤ 60 words) next steps beyond the card's round-2 redirects.
  - Generated automatically (don't write them): the goal-period table (from the period folders), the A–I scorecard (from the card) and the round-2 list (from the card's "Round 2 redirects" section).
- **`meta.json`**: suggested ratings (the coordinator calibrates them across hypotheses):
  ```json
  {"complete": 45, "faithfulness": 2.0, "usefulness": 1.5,
   "rationale": {"complete": "...", "faithfulness": "...", "usefulness": "..."},
   "rated_by": "H05 agent (suggested)", "updated": "2026-10-04"}
  ```

The goal-period diagram (`periods.pdf`) and the page header are generated from the `G<NN>/` / `NE<NN>/` folders and the card. Don't edit `summary.tex`; it is regenerated. The summary must be **exactly two pages**: page 1 is the overview, page 2 the details. The build warns otherwise. LaTeX special characters (`# & % _ $`) must be escaped in content. Never quote agent message text (gated data).

## Writing style (Vivian, 2026-10-04): physicist voice, ASD-STE100 leaning
Applies to every `content.tex` and to all dashboard text. The reader is a physicist who wants the model, the measurement and the result, and an operator who wants to know what to do.

**Physicist content, in this order where it fits:**
1. The system and the degrees of freedom: what a spin, state, field or coupling is in village terms.
2. The model: the Hamiltonian, master equation or estimator, and the control and order parameters.
3. The measurement: the observable, the estimator, the null, and the error bars or CI.
4. The result: numbers with uncertainty and the number of units, plus what is ruled out.
5. The impostors removed: scheduler field, kickoff/goal field, shared model priors, contemporaneous convergence.

Separate a field (an external drive) from a coupling (an interaction). Report scaling exponents and timescales with units. Say "consistent with" when a test cannot reject a rival.

**Language (ASD-STE100 leaning):**
- One idea per sentence. At most 20 words for an instruction and 25 for a description. At most 6 sentences per paragraph.
- Active voice and present tense. Name the agent of the verb: "the nudge raises", not "a raise is observed".
- One word for one meaning, used the same way on every page (e.g. "read-out call", "field", "coupling", "unit", "period"). Use the DEFINITIONS.md terms.
- Use specific numbers, not adjectives. "×1.5 [1.3, 1.7]", not "a large effect".
- No filler or hype. Banned: notably, remarkably, crucially, striking, intriguing, interestingly, delve, landscape, rich, nuanced, robust (unless you mean "survives the stated variants"), compelling, powerful, key insight, sheds light, paves the way, "it is worth noting".
- No rhetorical triplets, no em-dash asides, no rhetorical questions, no closing summary sentence that repeats the paragraph.
- Use articles. Avoid phrasal verbs ("set up" → "build"; "find out" → "measure"). Avoid -ing nouns where a plain noun exists.

**Practical value (`\htelos`):** say what an operator, a scaffold builder or a monitor can do with this result, in one or two instructions with a number. If nothing changes in practice, say that in one sentence.

**`meta.json` field `models`** (for the dashboard's physics-model × hypothesis matrix):
`"models": [{"model": "03-contagion", "role": "primary|secondary|rival|null|tool", "outcome": "supported|refuted|mixed|untested|n/a", "note": "≤ 12 words"}]`.
- *primary:* the card's model.
- *secondary:* a second model fitted.
- *rival:* the model the card tests against.
- *null:* the model serves as the null.
- *tool:* only its estimator is used, e.g. Aguilera EP.
- *outcome:* whether that model held for this hypothesis's claim after round 1b.

## Scoring v2 (2026-10-04): replaces the 0–5 faithfulness/usefulness ratings below
Rationale and worked examples: `writeup/scoring/scoring-v2.pdf`. The v1 numbers stay in `meta.json` for history; the dashboard and compendium show v2 when present.

**What is scored:** one stated, scoped claim per hypothesis (the result that currently stands, positive or negative), with the original hypothesis verdict recorded separately.

**Credence** `p` = probability the claim survives an independent confirmatory test at its stated scope. Start from the base rate and multiply the odds p/(1−p) by each factor that applies; cap 0.95 before a holdout run (0.98 after).

| Evidence | Factor |
| --- | --- |
| Base: pre-registered primary / secondary / post hoc | p₀ = 0.40 / 0.30 / 0.20 |
| Calibrated null passed (DQ8 sizes or own synthetic) | ×2 (mis-sized or unchecked ×0.7) |
| Replication: same sign in ≥ 2/3 of ≥ 6 independent units | ×2 (single powered unit ×0.6) |
| Robust to data versions and instruments (survived round 1b; both embedding models; estimator variants) | ×2 (changed under a data fix ×0.3) |
| Identified: synthetic recovery at real counts | ×1.5 (not identifiable ×0.5) |
| Intervention consistent (natural experiment / quasi-random) | ×2 |
| Rival beaten on held-out data | ×1.5 |
| Ground truth agrees (DQ6, known structure) | ×1.5 |
| Holdout passed / failed | ×5 / ×0.15 |
| Penalties: unvalidated LLM labels, known-problem inputs, uncorrected multiplicity | ×0.5–0.8 each |

Negative claims ("X does not happen") need synthetic power ≥ 0.8 at the effect size that would matter; otherwise the claim is "inconclusive" and credence stays near its base.

**Mechanism level:** M0 reproducible pattern; M1 mechanism-consistent (signature predicted, rival rejected); M2 mechanism identified (intervention + rival + synthetic).
**Fragile:** true if the headline changed sign or significance between data versions or across reasonable analytic variants (kept on the record after repair).

**Value if true** `V` (0–5): name the decision (operator, scaffold builder, alignment/safety, detection, science model choice; none → V ≤ 1); magnitude in the decision's units (negligible < 1% caps V at 2; small 1–5%; material 5–25%; large > 25%); generality (scaffold-specific −1; any read-out-gated LLM swarm 0; any multi-agent LLM system +0.5); readiness (rule written and computable from standard logs +0.5).
**Expected usefulness** `EU = p × V`. **Scientific value** `S` (0–5): rules out a model class, corrects earlier results, builds an instrument, unifies phenomena (refutations and data-bug discoveries score here).

**Process:** an independent rater (not the hypothesis agent) scores from the card and evidence; anchors are double-scored by the coordinator to measure agreement; disagreements beyond Δp > 0.25 or ΔV > 1 are adjudicated.

**Clarifications after the first rater check (2026-10-04).** A blind rater scored six anchors (H08, H12, H54, H44, H04, H29). Mean |Δp| was 0.105 against the coordinator, and the largest gap was 0.23 (H29), so none crossed the thresholds. Rank agreement was Spearman 0.75 on p and 0.99 on EU. Where two raters exist, credence is the log-odds mean and V the mean; both records are kept under `v2.raters`. The rater's ambiguity notes became these rules:
- **Base provenance.** *Primary*: the prediction and estimator were both fixed before the run. *Secondary*: the prediction was pre-registered, but the estimator or outcome was redesigned after seeing data (e.g. a round-1b redesign). *Post hoc*: the claim was formed after seeing the result.
- **Partial factors.** "Partly robust" (one instrument family only, or estimator variants without a second embedding model) and "partial replication" (scattered or < 6 units) each get ×1.5. Interventions that are only partly consistent also get ×1.5.
- **One design counts once.** When a natural experiment, a synthetic check and a null are one piece of work, credit the strongest factor among them, not all three. In particular, don't stack ×2 for intervention and ×2 for a calibrated null that is the same NE placebo.
- **Fragile** refers to the scored claim's *headline* in the previous data version, not to sub-findings. A withdrawn secondary result (e.g. H08's ~3-min post-read-out lag) does not set it; a collapsed headline that the claim replaces (H12's activity market mode) does.
- **V before adjustments.** Negligible 1–2 (cap 2), small ≈ 2, material ≈ 3, large ≈ 4; then apply generality (−1 / 0 / +0.5) and readiness (+0.5).
- **Null mis-sized** also applies when a known issue says the test is dominated by something other than its target (e.g. co-response in seen/unseen content tests).

**`meta.json` schema v2** (added under a `"v2"` key; v1 keys untouched):
```json
"v2": {"claim": "...", "scope": "...", "direction": "positive|negative", "original_verdict": "supported|refuted|mixed|inconclusive",
       "credence": 0.72, "ladder": [{"factor": "calibrated null", "x": 2, "evidence": "card §Round 1b"}],
       "mechanism_level": "M1", "fragile": false, "value_if_true": 2.5, "decision": "...", "magnitude": "small",
       "generality": "read-out-gated swarms", "expected_usefulness": 1.8, "scientific_value": 3,
       "rater": "rater-v2 (independent)", "rated_at": "2026-10-04"}
```

## Ratings (v1, kept for history)

### Estimated completion of the research direction (0–100 %)
How far along the *direction* is, not just round 1.

| % | Stage |
| --- | --- |
| 5 | idea or parked |
| 10–15 | specified: card, model, candidate periods |
| 20–30 | round 1 running: predictions written, synthetic validation under way |
| 35–50 | round 1 done: per-period verdicts and scorecard |
| 55–65 | confirmatory holdout run done |
| 70–85 | round 2: robustness (embedding swap, causal designs), rivals compared, mechanism isolated |
| 90–100 | settled: faithful or refuted, written up |

### Scoped faithfulness (0–5, halves allowed)
How well the hypothesis' model holds *for what it claims*, given the evidence. Anchored to the A–I scorecard and the holdout.

| Score | Meaning |
| --- | --- |
| 0 | untested, or the core prediction was refuted outright |
| 1 | fits something but does not beat the nulls; main predictions failed |
| 2 | beats some nulls (C = 1); mixed per-period verdicts; or a clear but partial result |
| 3 | descriptive level (C = 2, D ≥ 1), or the primary holdout test passed |
| 4 | supported (`writeup/paper.tex` promotion rules), confirmed on the holdout |
| 5 | faithful and mechanistic: interventional, identifiable, beats rivals, transfers |

A cleanly *refuted* hypothesis can still have a well-understood result. Faithfulness scores the hypothesis, not the work.

### Unscoped usefulness for controlling, steering or aligning agent swarms (0–5, halves allowed)
Ignore whether the hypothesis came out true. Ask what an operator or alignment researcher can *do* with what we now know.

| Score | Meaning |
| --- | --- |
| 0 | pure curiosity; no handle on any real swarm |
| 1 | an interesting framing or vocabulary, but nothing to compute or act on |
| 2 | a diagnostic someone could compute on their own swarm logs, with unclear payoff |
| 3 | a validated monitor or design rule with modest evidence (e.g. "rooms decouple chat") |
| 4 | a lever: predicts the effect of an intervention (steering) with evidence |
| 5 | a validated, transferable control knob or alignment-relevant guarantee |

## Color coding (TOC and page header)
- **Completion:** single-hue blue ramp, light (early) to dark (done).
- **Faithfulness and usefulness:** diverging red ↔ neutral gray (2.5) ↔ blue; red = low, blue = high. The number is always printed, so color never carries the value alone.
