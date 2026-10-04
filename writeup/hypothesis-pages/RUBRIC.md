# Hypothesis summary pages: rubric and content rules

Every hypothesis gets a one-page PDF summary at `hypotheses/H<NN>-<slug>/summary/summary.pdf`. All of them are appended, behind a color-coded table of contents, into `writeup/hypotheses-compendium.pdf`. This is a living status document, **not** the paper.

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
- **`meta.json`**: suggested ratings (the coordinator calibrates them across hypotheses):
  ```json
  {"complete": 45, "faithfulness": 2.0, "usefulness": 1.5,
   "rationale": {"complete": "...", "faithfulness": "...", "usefulness": "..."},
   "rated_by": "H05 agent (suggested)", "updated": "2026-10-04"}
  ```

The goal-period diagram (`periods.pdf`) and the page header are generated from the `G<NN>/` / `NE<NN>/` folders and the card. Don't edit `summary.tex`; it is regenerated. The page must fit on **one** page; the build warns otherwise. LaTeX special characters (`# & % _ $`) must be escaped in content. Never quote agent message text (gated data).

## Ratings

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
