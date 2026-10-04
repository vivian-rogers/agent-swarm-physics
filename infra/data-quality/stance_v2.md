# DQ10: reply stance v2 (disagreement on substance vs correction, decline, coordination)

**Code:** `infra/shared/stance_v2.py` (sample, blind sheet, Jev labelling, validation, compile).
**Table:** `data/processed/shared/reply_stance_v2.parquet` (codes only); working files in `data/processed/shared/stance_v2/` (label JSONL with codes only; gated blind sheets and keys).
**Status:** pre-registered 2026-10-04 (UTC), before any v2 sample was drawn or any v2 label requested. Results go below the line, dated.
**Outcome (2026-10-04):** v2.0 and v2.1 failed the gate on the draft and on the first fresh sheet. **v2.1 passed on the second, Vivian-authorized confirmation sheet (Amendment 2).** The validated observable is `disagree` with confidence ≥ 0.6: precision 0.67 [0.54, 0.80], n = 44. `reply_stance_v2.parquet` covers 55,428 of 61,533 non-holdout pairs.
**Downstream:** H21, H22, H37, H55, H64.

## Why
DQ2's stance labels (`reply_pairs.stance`, 4 classes) are usable only in aggregate: 4-class κ 0.44 against a blind labeler, pair-level `opposes` precision 0.08 (H37's prompt: 0.30). The misses are known. Most Jev "opposes" are task corrections ("the link is broken", "that's already merged"), polite declines, or a different status report. DQ2's second-pass subtype (`opp_type`) runs only inside Jev's opposes, so it cannot recover precision lost upstream (subtype κ 0.11; position precision 1/3). `supports` (precision 0.44) also absorbs friendly acknowledgments and status replies.

The physics needs one clean class: **a dispute on the merits** (the antiferromagnetic bond of H21, H37, H64; the friction of H55). Corrections and declines are other observables (H55's immune signal), not conflict. Stance v2 asks one question with classes that keep these apart.

## Taxonomy `stance-v2.0` (one Jev choice question per (A, B) pair)
**Instruction:** "Message B was posted after message A in the same group chat. Which class best describes what B does with respect to A? Judge B's substance toward A and ignore courtesy openers and sign-offs (e.g. 'great point, but …' is judged by what follows). Use 'disagree' only for a dispute on the merits of something A claims, proposes, decides or argues. Fixing a detail, declining a request, or reporting something different without contesting A is not 'disagree'."

| Class | Definition sent to Jev | Sign |
| --- | --- | --- |
| `agree` | B endorses A on the merits: agrees with A's claim, argument or opinion, supports or votes for A's proposal or decision, or says A is right. Thanks or praise alone is not agree. | + |
| `disagree` | B disputes A on the merits: contests A's claim, argument, opinion, plan, proposal, decision or vote, argues for an alternative instead of A's, or says A or A's work is wrong or bad. A dispute about what A said or wants, not a small factual fix. | − |
| `correct` | B fixes a detail in A without contesting A's overall point or plan: a fact, number, name, date, status, link, file or technical detail, or reports a bug or error in A's work. | 0 (pushback) |
| `decline` | B declines, refuses, postpones or redirects a request, task, invitation or offer made in A, or says it cannot do it. | 0 (pushback) |
| `coordinate` | B handles task logistics with A: accepts or confirms a request or assignment, claims or hands off work, reports doing what A asked, divides tasks, schedules, or sets next steps. | 0 |
| `ask` | B asks A's author a question about A, or asks for clarification, details or confirmation. | 0 |
| `acknowledge` | B only acknowledges, thanks, praises, congratulates or welcomes A, without taking a position on A's content. | 0 |
| `inform` | B gives information or a status update that takes no side on A, or B does not respond to A at all. | 0 |

Derived columns: `s2_sign` (+1 agree, −1 disagree, else 0), `s2_soft` = p_agree − p_disagree, `p_pushback` = p_disagree + p_correct + p_decline.
Mapping to DQ2's classes (for comparison only): agree → supports; disagree, correct, decline → opposes; ask → asks; coordinate, acknowledge, inform → neutral (DQ2 put some of these in supports).

State sent to Jev: exactly DQ2's (`reply_threading.make_states`): the two messages with speaker labels, A cut to 700 characters, B to 900 characters around its first mention of A's author. No time, room, period, team or role. Zero-shot; no training.

## Population
Non-holdout DQ2 reply pairs: `reply_pairs` rows with `pair_set = cand`, a DQ2 label (`p_reply` not null) and **p_reply ≥ 0.5**, and not in the locked holdout (`holdout` flag and `holdout_mask` both re-applied). 61,533 pairs (regime I 27,860; II 2,265; III 31,408). Held-out pairs are never sent, sampled or labelled.

## Validation (before any full run)
**Sample (200 pairs, stratified, drawn before any v2 label exists).** Strata partition the population (first match wins):
| Stratum | Rule | n |
| --- | --- | --- |
| G12 | goal #12 (debate weeks) | 30 |
| OPP | DQ2 stance `opposes` | 50 |
| ASK | DQ2 `asks` | 20 |
| NEU | DQ2 `neutral` | 20 |
| SUP-I / SUP-II / SUP-III | DQ2 `supports`, by regime | 26 / 20 / 34 |

Pairs in DQ2's earlier blind sheets are excluded. Weights for population estimates: N_stratum / n_stratum.

**Blind reference.** A separate Claude subagent labels all 200 pairs on the definitions above. It sees the same text Jev sees, shuffled, without strata, DQ2 labels or any Jev output. It also marks items it finds ambiguous. Jev is run on the same 200 pairs; its output is not shown to the labeler.

**Report:** 8-class κ (raw and reweighted); sign κ (− / 0 / +); 4-group κ (agree / disagree / correct+decline / rest); per-class precision and recall (raw and reweighted, Wilson or stratified-bootstrap CIs); agreement by Jev confidence; what the blind labeler calls DQ2's `opposes` pairs (how many are disagreement); DQ2's 4-class κ on the same items, as a baseline.

**Gate (pre-registered).** The full run goes ahead only if
- (a) Jev's hard `disagree` class has a **population-reweighted precision ≥ 0.6**; or
- (b) the pre-specified flag `disagree` with confidence ≥ 0.8 reaches reweighted precision ≥ 0.6 with ≥ 15 flagged items in the sample. Then the flag, not the class, is the validated conflict observable.

If both fail, one revision (`stance-v2.1`) is allowed. It must pass the same gate on a **fresh** 100-pair sheet (same strata proportions), blind-labelled before any v2.1 output is read. Otherwise no full run; the draft and the failure are reported.

## Full run (only if the gate passes)
All population pairs, in this order: regime III; goal #12; regime II; regime I. Random order within each (seed 20261004). Resumable JSONL.

**Spend.** Hard cap $6.00 for DQ10 in total (stance v2 and anything else); the script stops at $5.90 summed over every `stance_v2/labels/*.jsonl` and prints the running total before each batch. DQ2 measured ~$0.00004 per pair, so the full population is ~$2.5–3.5.

## Known limits (before results)
- One blind labeler, same model family as the designer. The labeler is a separate agent with no access to Jev output.
- Truncated text (700 / 900 characters), as in DQ2.
- The class is a property of the (A, B) pair; it inherits DQ2's visibility rule and p_reply threshold (p_reply is direction-blind; direction comes from the candidate rule).

### Amendment 1 (2026-10-04, after the draft failed the gate; written before the fresh sheet was drawn)
**Draft result (v2.0, 200 pairs):** the gate failed. The hard `disagree` class has reweighted precision 0.45 (raw 11/23). The confidence-0.8 flag is precise (7/8) but too rare (n = 8 < 15). Full numbers are under Results.

**What the draft showed (Jev's 12 false `disagree`, by the reference):**
- inform 5: B reports a different status or observation without saying A is wrong;
- coordinate 3: B takes over or redirects work;
- agree 2: B joins A's criticism of a third party;
- correct 2.

Precision rises steeply with Jev's confidence: 1/9 below 0.5 and 10/13 at 0.6 or above.

**Revision `stance-v2.1` (prompt only; same 8 classes, state and population):**
- The instruction adds: "Judge B's stance toward A itself, not toward third parties that A or B mention: if A criticizes something and B joins in, B agrees with A."
- `disagree` must make the opposition to A explicit: "B explicitly rejects or contests something A said or wants: says that A's claim, argument, plan, proposal, decision or vote is wrong, should not be done, or should give way to B's alternative. A different report, B's own new plan, or a next step that does not reject A is not disagree. A dispute about the merits, not a small factual fix."
- `inform` adds: "including an observation or result that differs from A's without saying A is wrong."
- `coordinate` adds: "or takes over or redirects the work."
- `correct` adds: "B says a specific detail in A is wrong or out of date while A's overall point stands."
- The v2.0 wording stays in the code (`--taxonomy stance-v2.0`), so the draft reproduces.

**Fresh confirmation sheet (deviation from the 100-pair, same-proportion plan, declared before drawing).** A 100-pair sheet in draft proportions would hold about 12 Jev-`disagree` items and about 4 confident flags, so the flag rules could never reach n ≥ 15. The fresh sheet is therefore **150 pairs**, enriched where disagreement lives:

| Stratum | n |
| --- | --- |
| OPP | 60 |
| G12 | 30 |
| ASK | 8 |
| NEU | 10 |
| SUP-I | 14 |
| SUP-II | 8 |
| SUP-III | 20 |

It excludes every draft and DQ2 sheet pair. Stratum weights keep the estimates population-valid. A **new** blind subagent labels it on the v2.1 definitions before any v2.1 output on those pairs is read.

**v2.1 gate (on the fresh sheet only):** reweighted precision ≥ 0.6 for one of three pre-specified observables. The full run then ships that observable as the validated conflict flag.
- (a) the hard `disagree` class;
- (b) `disagree` with confidence ≥ 0.8 and ≥ 15 flagged;
- (c) `disagree` with confidence ≥ 0.6 and ≥ 15 flagged.

Rule (c) was chosen after seeing the draft; testing it on fresh pairs is what makes it admissible. With three rules the chance of a lucky pass is higher, so the bootstrap CI is reported with every pass. If none passes, there is no full run and the failure is recorded.

---

## Results

### Verdict (2026-10-04): the gate failed twice; no full run, no `reply_stance_v2` table
All numbers are in `data/processed/shared/stance_v2/validation/results_*.json`. Every pair is non-holdout.
- **Spend:** $0.0259 of the $6.00 cap. That paid for 550 label calls: v2.0 on the draft (200), v2.1 on the draft (200) and v2.1 on the fresh sheet (150). There were 0 errors.
- **Coverage:** 350 unique pairs of 61,533 labelled, all validation pairs. The full pass (about $2.9) was not run.
- **Code guard:** `stance_v2.py label --phase full` and `compile` both refuse to run without a passed fresh-sheet gate.

| | v2.0, draft (n = 200) | v2.1, draft (development, in-sample) | **v2.1, fresh (n = 150, confirmatory)** |
| --- | --- | --- | --- |
| 8-class κ, raw / reweighted | 0.49 / 0.45 | 0.55 / 0.46 | **0.54 / 0.52** |
| sign κ (− / 0 / +), raw / reweighted | 0.53 / 0.48 | 0.63 / 0.47 | **0.61 / 0.59** |
| DQ2's 4-class labels on the same items vs reference (mapped), raw / reweighted | 0.31 / 0.13 | — | 0.26 / 0.14 |
| v2 mapped to DQ2's classes vs reference (mapped) | 0.57 | 0.62 | 0.64 |
| agreement at Jev confidence ≥ 0.8 | 73% (n = 89) | — | **94% (n = 52; κ 0.92)** |
| **`disagree`, hard class**: correct / predicted; precision raw [Wilson]; reweighted [stratified bootstrap]; recall | 11/23; 0.48 [0.29, 0.67]; 0.45 [0.25, 0.65]; 0.85 | 13/16; 0.81; 0.80 [0.56, 1.0]; 1.0 | **7/13; 0.54 [0.29, 0.77]; 0.48 [0.21, 0.76]; 0.88** |
| `disagree` & confidence ≥ 0.8 | 7/8; 0.87 | 6/6 | 3/3 (n < 15) |
| `disagree` & confidence ≥ 0.6 | 10/13 (post hoc) | 7/9 | **7/7; 1.0 [0.65, 1.0]; recall 0.88 (n = 7 < 15)** |
| gate | fail (a: 0.45; b: n = 8) | — (not a test) | **fail (a: 0.48; b: n = 3; c: n = 7)** |

**What the numbers say**
- **v2 is a better stance labeller than DQ2 on the same items:** κ 0.26 rises to 0.64 in DQ2's own 4 classes.
- **Confident v2.1 labels are reliable across classes:** 94% agreement at confidence ≥ 0.8.
- **The hard `disagree` class is not precise enough.** On the fresh sheet the 6 false positives were inform 4, coordinate 1 and correct 1, all at confidence < 0.6.
- **The confident flag looked precise but could not be validated.** It was right 7 of 7 times on the fresh sheet and 14 of 16 over both sheets, the draft being in-sample. True disagreement is too rare to reach 15 flags in a sheet of this size: the reference found 8 in 150 enriched pairs.
- **Rule (c) is promising but unvalidated.** Testing it needs a larger fresh sheet. That would be a new, disclosed confirmation attempt of a pre-specified rule, so it is a decision for Vivian.

**Other classes (fresh sheet, v2.1)**
- **`decline`:** 9/10 precise (recall 0.90).
- **`agree`:** 7/8 (recall 0.50). `ask`: 5/6. `coordinate`: 0.67. `inform`: 0.63 (recall 0.40).
- **`correct` is over-called:** 11/28 precise, reweighted 0.20. Jev called 28 pairs correct where the reference found 12.
- **`acknowledge` is under-called:** recall 0.20.

**What DQ2's `opposes` contains** (fresh sheet, 65 DQ2-opposes pairs, by the blind reference):
- inform 21, coordinate 14, correct 12, decline 9, **disagree 8 (12%)**, ask 1;
- DQ2 `opp_type = position` (19 pairs) is disagreement in 6 of them.

This confirms the Limits of `reply_threading.md`. Most DQ2 opposes are not conflict.

**Reference noise ceiling.** The draft was blind-labelled twice, by two independent subagent runs with v2.0 definitions.
- They agree at κ 0.71 (77.5%) and sign κ 0.78.
- On `disagree` they found 13 and 12 pairs, 10 of them shared. One reference is 0.83 precise against the other.
- Precision of about 0.8 is therefore the most any labeller can reach against a single Claude reference.

**Process notes**
- **First launch.** The first blind-labeller launch did not deliver output in time. The retry labellers' per-chunk files are the reference (`ref_labels_*.json`).
- **Late output.** The first launch's draft labels arrived later. They were kept only as the second reference (`ref2_labels_draft_original.json`).
- **Fresh-sheet labeller.** It wrote 15 labels before reading their text, noticed, deleted them, and relabelled them from the text.
- **What I saw.** I saw Jev's v2.0 draft class counts before any reference existed, never the reference before Jev ran. I designed v2.1 after reading the v2.0 confusion matrix and the reference's one-line notes. v2.1 was then judged only on the fresh sheet.

**For downstream users (H21, H22, H37, H55, H64)**
- Nothing is unblocked. Keep DQ2's aggregate stance with its Limits.
- **H55 and H64:** v2.1's `decline` (0.90) and confident labels (94%) are the best evidence so far that a zero-shot labeller can separate declines from conflict. They are still not a shipped table.

### Amendment 2: second confirmation attempt, authorized by Vivian 2026-10-04 (written before the pool or sheet was drawn)
**Why.** On the fresh sheet the confident flag (`disagree`, confidence ≥ 0.6) was right 7 of 7 times, but n = 7 is below the gate's 15. True disagreement is rare, so an enriched random sheet would need about 300 pairs to reach 15 flags. Vivian authorized one more confirmation attempt. The earlier results above stay in full.

**Design (two-phase, enrichment by Jev's v2.1 prediction; the labeller stays blind):**
1. **Phase 1 pool.** These are non-holdout population pairs whose B message is in none of the 350 earlier sheet pairs:
   - every OPP and G12 pair;
   - a uniform random 4,000 of the rest (ASK, NEU, SUP-I/II/III; seed 20261004).

   Jev v2.1 labels the pool. The labels count toward the full run if one follows. Code reads them only to select phase 2; no Jev output on the pool is printed or inspected before the blind labels exist.
2. **Phase 2 sheet (about 130 pairs).** Phase-1 strata s ∈ {OPP, G12, REST} are crossed with Jev cells:
   - F = `disagree` with confidence ≥ 0.6: all of them if ≤ 45, else 45 allocated in proportion to estimated population counts, with at least 5 per s where available;
   - H = `disagree` with confidence < 0.6: up to 25, allocated the same way;
   - O = any other class: 20 per s.
3. **Weights.** Each sheet cell (s, c) has weight N_{s,c} / n2_{s,c}, where N_{s,c} = N_s · n1_{s,c} / n1_s (exact for OPP and G12, whose pools are complete). Precision of a rule is the weighted share of its sheet items the reference calls `disagree`. Cells are the strata of the bootstrap.
4. **Blind reference.** A new Claude subagent labels the sheet on the v2.1 definitions. It sees the text only: shuffled, with no cells, strata, DQ2 labels or Jev output.

**Gate.** Unchanged (rules a, b, c with reweighted precision ≥ 0.6 and ≥ 15 flagged items for b and c), judged on this sheet only. The combined results over the first and second fresh sheets are reported as secondary.
- **Multiple testing.** This is the second attempt and has three rules, so the bootstrap CI and the lower bound are reported with any pass. A pass whose lower bound is below 0.5 is flagged as weak in the verdict.

**If it passes.** Full v2.1 pass over the rest of the population, in the order regime III, #12, regime II, then regime I.
- **Spend:** these labels share a $3.00 cap with the held-out passes. Remaining regime-I pairs may stay unlabelled at the cap; they are marked `labelled = false`.
- **Validated observable:** the observable of the passing rule (the least restrictive one if several pass) is shipped as `disagree_validated`.

**If it fails.** Recorded; no full run, no table.

### Amendment 2 result (2026-10-04): gate passed; full run; `reply_stance_v2` shipped
Results file: `results_confirm2__stance-v2.1.json`.
- **Sheet:** 129 pairs, two-phase. The phase-1 pool was 10,576 pairs labelled with v2.1. Sheet cells: OPP F 36, H 13, O 20; G12 F 7, H 5, O 20; REST F 1, H 7, O 20.
- **Blind reference:** a new subagent; it flagged 73 of 129 items ambiguous.

| Rule | Correct / flagged | Precision raw [Wilson] | Reweighted [stratified bootstrap] | Recall (raw / reweighted) | Gate |
| --- | --- | --- | --- | --- | --- |
| (a) hard `disagree` | 41 / 69 | 0.59 [0.48, 0.70] | 0.56 [0.43, 0.70] | 1.0 / 1.0 | fail |
| (b) `disagree` & conf ≥ 0.8 | 22 / 26 | 0.85 [0.67, 0.94] | **0.81 [0.64, 0.96]** | 0.54 / 0.40 | pass |
| **(c) `disagree` & conf ≥ 0.6** | **31 / 44** | 0.70 [0.56, 0.82] | **0.67 [0.54, 0.80]** | 0.76 / 0.61 | **pass (shipped)** |

**Gate: pass.**
- Rules (b) and (c) pass, and the pre-registered choice is the least restrictive passing rule, so (c) is shipped as `disagree_validated`.
- The lower bound of (c) is 0.54, which is ≥ 0.5, so the pass is not flagged weak.
- This is the second attempt, with three rules per attempt. Read the pass with that in mind.

**Other numbers on this sheet**
- 8-class κ 0.45 raw, 0.31 reweighted. The sheet is built around `disagree`; agreement on the other classes is not its purpose.
- Agreement at confidence ≥ 0.8: 88% (n = 50).
- None of the 60 sampled O-cell pairs is a reference `disagree`, so the reweighted recall rests on that.
- Jev's false `disagree` calls (28) were inform 11, correct 10, coordinate 3, agree 2, acknowledge 1, ask 1.

**Sensitivity (post hoc, disclosed).** Nine sheet pairs reply to automated messages, mostly the idling nudge. The reference labelled the agents' objections to the nudge `disagree`.
- Without those pairs, rule (c) scores 0.61 (n = 38) and rule (b) 0.78 (n = 23).
- Counting them as false positives instead gives 0.52 and 0.67.
- Hence the convenience column `disagree_validated_agent` (validated flag, parent by an agent or a human). **Use it for agent–agent conflict analyses.**

**Combined record over all three test sheets** (secondary, not a gate): the confidence ≥ 0.6 flag was right 7 of 7 times on fresh sheet 1 and 31 of 44 on confirm2.

**Full run and spend.** The $3.00 cap was shared with the held-out passes; the round spent **$2.9512**.

| Item | Cost |
| --- | --- |
| held-out behavior | $0.2103 |
| H55 opposes-subtype | $0.0661 |
| phase-1 pool | $0.5136 |
| priorities III, #12, II | $1.3778 |
| regime I, up to the cap | $0.7834 |

The DQ10 total including the first round is $2.98: DQ10 round 1 spent $0.0259 of its $6 cap, and the second round $2.95 of its $3.

**`data/processed/shared/reply_stance_v2.parquet`** (3.2 MB, non-holdout only, `holdout = false` on every row).
- One row per population pair: 61,533 rows; **labelled 55,428 (90.1%)**:
  - regime III 31,404 / 31,408 (4 call errors);
  - regime II 2,265 / 2,265;
  - #12 1,325 / 1,325;
  - regime I 21,759 / 27,860. The regime-I remainder was cut at the cap; its order was random, so the labelled part is a random 78% of regime I.
- Columns:
  - keys `B_message_id`, `A_message_id` (join to `reply_pairs`), context, and DQ2's `p_reply`, `dq2_stance` and `dq2_opp_type`;
  - `stance2`, `stance2_conf` and the eight `p_*` probabilities;
  - `s2_sign`, `s2_soft`, `p_pushback`;
  - `disagree_conf` (confidence ≥ 0.8), **`disagree_validated`** (confidence ≥ 0.6, the gate-passing rule), **`disagree_validated_agent`**;
  - `labelled`, `phase`, `cost`.
- 707 labelled pairs carry `disagree_validated` (1.3%).
- Rebuild: `build_all.py --only stance_v2_validate_confirm2,stance_v2_compile`. No API calls.

**How to use it**
- **Conflict:** count or sum `disagree_validated_agent` per group. Precision is about 0.6–0.67 and recall about 0.6, so build the labeller's confusion into any null (H37's ordered-logit agent-field null).
- **Soft sums:** `p_disagree`; `s2_soft` for sign.
- **Corrections and declines:** `p_correct` is over-called (precision 0.26–0.55). `decline` was 0.90 on fresh sheet 1 and 0.50–0.61 on confirm2.
- **Not validated:** the hard class and the other classes, beyond the κ above.

**Held-out stance labels (pass c): not run.** Labelling the 18,621 held-out pairs would cost about $0.91, which did not fit under the $3 cap after the non-holdout pass. Vivian set the non-holdout pass first. To run it later: `uv run --with httpx python infra/shared/holdout_labels.py stance2 --cap <cap>`. The script refuses unless the confirm2 gate has passed, and writes to `data/processed/holdout_labels/stance_v2_holdout.jsonl` and `reply_stance_v2_holdout.parquet`.
