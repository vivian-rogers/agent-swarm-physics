# DQ2: reply threading and stance labels

**Code:** `infra/shared/reply_threading.py` (candidates, Jev labelling, compile) and `infra/shared/reply_threading_validate.py` (blind sample, κ, placebo, ground truth).
**Tables:** `data/processed/shared/reply_pairs.parquet`, `data/processed/shared/reply_graph.parquet`; working files in `data/processed/shared/reply_threading/` (candidates, label JSONLs with codes only, and the gated validation sheet).
**Status:** pre-registered 2026-10-04 (UTC), before any Jev label was requested. Results are added below the line, dated.

## Why
Round 1 used @-mentions as the proxy for "B responds to A". H18's placebo showed it is contaminated: agents name senders whose messages they could not yet have seen 3–10× more often than chance. Reply structure is the swarm's coupling graph. Stance (support vs oppose) is where conflict lives; H22 showed that topic co-movement can't see it.

## Pre-registration (written before any label)

### Candidate parents (visibility + ranking)
For every agent chat message B (author a, time t_B):
- **Call start s(B)** (H18 rule): a's latest logged turn (any `actions` row except `pause` mirrors, or any `events_core` event of a) strictly before t_B − 1 s. If a has no logged turn that day (more than 1 h before the day's window), s(B) = t_B − 1 s (flag `s_fallback`; 1,184 messages).
- **Visible pool:** messages A by anyone other than a (agent, human or automated) that were posted in a's room (`exposure` rows of a), on the same PT day, with s(B) − 60 min ≤ t_A < s(B); at most the 40 most recent.
- **Features:** `cos` = cosine of the bge-small embeddings of A and B; `b_names_a` = B's `mentions_roster` contains A's author; `a_names_b` = A's `mentions_roster` contains a; `new` = A arrived after the call start of a's previous message that day (it is new to a since a last spoke); `pos` = recency position (1 = newest visible).
- **Ranking rule (fixed, not fitted):** score = cos + 0.20·b_names_a + 0.10·a_names_b + 0.05·new − 0.03·ln(pos). Candidates sorted by score; **K = 3** kept per B in `reply_pairs`.
- **Placebo sets** (same features and score):
  - *invisible:* the best-scoring message that arrived in a's room during B's own model call (s(B) ≤ t_A < t_B), so a could not have seen it;
  - *reversed:* the best-scoring message by another speaker in B's room in the 30 min *after* B (it often replies to B, so it tests direction confusion).
- **Visibility source:** H18's call-start rule now. When DQ1's `context_ledger_items.parquet` exists, `candidates --visibility ledger` rebuilds the pools from the ledger; everything downstream is unchanged.

### Jev question (one call per pair, zero-shot)
Model `typesafe/jev-1.13` via the OpenRouter Decisions API (`label_windows.load_key()`; key never printed or written). State: the two messages with speaker labels (agent display name; "a human viewer"; "the village's automated system"). A's text is cut to 700 characters (head); B's to 900 characters (a window around its first mention of A's author, else the head). No time, room, rank, period, team or role information is sent.
- `reply` (noul): "Is B a direct reply or response to message A? Count it only if B takes up A specifically: answers its question, acts on its request, comments on or reacts to its content, or addresses its author about it. Being on the same general topic, or addressing A's author about something else, does not count."
- `stance` (choice): **supports** (agrees, endorses, accepts, confirms, thanks, praises, builds on, or does what A asked) · **opposes** (explicitly disagrees, rejects, corrects, disputes, criticizes, or refuses; reporting other facts without disputing A does not count) · **asks** (asks A's author about A, or for clarification) · **neutral** (no side: information, status, acknowledgment, logistics, or unrelated). "If B does not respond to A at all, choose neutral; ignore courtesy openers when B goes on to disagree." The opposes wording is narrower than H37's because H37 measured a precision of 0.30 for Jev's negative class.

### Labelling order and budget (hard cap $8.00; script cap $7.90 summed over every run)
1. `smoke`: 20 random non-holdout top-1 pairs (format and cost).
2. `top1`: the top candidate of every message with a pool (170,511; non-holdout first, then holdout; random order within each).
3. `audit`: whole pools (up to 40) of 300 random non-holdout messages with ≥ 4 candidates, from a 2% subset drawn before labelling. Measures recall@K of the ranking.
4. `placebo`: 2,000 *invisible* and 1,000 *reversed* pairs (non-holdout).
5. `extras`: ranks 2–3 for messages whose top-1 p_reply < 0.8, most ambiguous (|p − 0.5| smallest) first, non-holdout first, until the cap.
Holdout days are labelled (labels are a measurement, as for behavior states) and flagged; every validation and diagnostic below uses non-holdout pairs only.

### Validation (blind second labeler)
- **Sample:** 150 non-holdout labelled pairs, excluding smoke pairs: 100 drawn at random from `top1` (stratified by regime, ∝ size) and 50 enriched (drawn equally from Jev's predicted opposes, asks, and p_reply in [0.3, 0.7]), shuffled together; the labeler (Claude, this agent) sees text only, never Jev's answers or the item's stratum. Labels: reply yes/no, stance (4 classes).
- **Report:** Cohen's κ for reply (Jev p_reply ≥ 0.5) and for stance (4 classes and the sign − / 0 / +, where asks counts as 0), on the random 100 and on all 150 reweighted to population shares; agreement by Jev confidence bin (stance confidence; reply |p − 0.5|); per-class precision.
- **Pre-registered expectations:** reply κ ≥ 0.5; stance κ ≥ 0.5 on the random set; agreement ≥ 85% when Jev's stance confidence ≥ 0.8; opposes precision ≥ 0.5 (the H37 prompt got 0.30).

### Placebo predictions (H18 logic)
- **P-inv:** mean p_reply of *invisible* pairs < 0.5 × that of top-1 visible pairs, and lower than visible pairs matched on b_names_a and cos decile. If invisible pairs score like visible ones, Jev's "reply" reads thread membership, not uptake of a specific message.
- **P-rev:** mean p_reply of *reversed* pairs < 0.5 × top-1 visible. A high value means Jev ignores direction.
- **P-mention:** among top-1 pairs, p_reply is higher when B names A's author, but a large share of mention pairs (> 20%) get p_reply < 0.5 (mentions ≠ replies).

### Ground-truth checks (descriptive, not H37's analysis)
- **#12 debates (H21 teams):** among debater-to-debater top-1 replies during debate windows, opposes share is higher for opposite-team than same-team pairs.
- **#51 roles (H22 classes):** mean stance by role class (U, SR, OP, SY, NC), descriptive only.
- **Agreement with H37's Jev labels** on pairs both pipelines labelled (different prompts): sign agreement and κ.

### Amendment 1 (2026-10-04, before any outcome statistic; only 20 smoke labels and the cost log seen)
1. **Order.** `placebo` and `audit` ran before `top1` so that they are guaranteed budget; `extras` still runs last.
2. **Blind sample design.** Sheet 1 = 100 random non-holdout top-1 pairs, drawn from the candidates without any Jev output, labelled first (done before any Jev answer was looked at). Sheet 2 = 50 enriched pairs (17 Jev-opposes, 17 Jev-asks, 16 with p_reply in [0.3, 0.7]) mixed with 25 more random pairs and shuffled, so the labeler cannot tell which items are enriched. Total 175.
3. **H37 labels (coordinator request).** H37 labelled 30,461 reply pairs with its own prompt (5 stance classes, a looser "responds" question). They are attached to `reply_pairs` as separate columns (`h37_stance`, `h37_s_soft`, `h37_responds`), with `label_source` ∈ {dq2, dq2+h37, h37, none}; they are never copied into `p_reply` or the stance probabilities, so the shared columns keep one taxonomy. The `extras` phase skips pairs H37 already labelled (those rows carry `label_source = h37`). Agreement between the two prompts on the overlap is reported.
4. **Opposition subtype (coordinator request; H37 measured an oppose precision of 0.30, mostly task corrections and polite declines).** A second Jev call (`opptype`, choice) for every visible candidate Jev labelled `opposes`: **position** (disagrees with A's position, argument, plan, proposal or decision, or criticizes its author) · **correction** (corrects a fact, number, status, link or technical detail, or points out an error, without disputing A's overall position) · **decline** (declines, refuses or defers a request, task or offer) · **none** (no pushback). Runs after `top1`, before `extras`. The blind labeler gives the same subtype for every item it labels `opposes`. Reported: subtype κ, precision of position-oppose, and the label-noise floor of the raw opposes share (population share of Jev-opposes that the blind labeler does not call opposes; H37's was 0.065).
5. **Graph-level nulls.** `reply_graph` ships counts only. Any graph-level statistic built on it (faction score, frustration, per-pair significance) must use H37's calibrated ordered-logit agent-field null (`hypotheses/H37-stance-spins/analysis/calibrate.py`); the sign-shuffle null and per-pair FDR were anti-conservative there (10–28% false alarms; 100% at #51's structure).

## Schema

### `reply_pairs.parquet` (one row per (A, B) pair; codes only, no text)
| Column | Meaning |
| --- | --- |
| `B_message_id`, `A_message_id` | chat message ids (stable across rebuilds); `b_msg`, `a_msg` = chat_core row index at build time (pinned in `reply_threading/msg_index.parquet`) |
| `pair_set` | `cand` (visible candidate), `invisible` (A arrived during B's own model call; placebo), `reversed` (A came after B; placebo) |
| `cand_rank` | rank by the pre-registered score (1 = best); every B has ranks 1–3 (K = 3); audit messages carry their whole pool |
| `score`, `cos`, `b_names_a`, `a_names_b`, `new`, `pos`, `lag_s` | ranking features (see pre-registration); `lag_s` = t_B − t_A (negative for `reversed`) |
| `n_pool`, `n_invisible` | size of B's visible pool and of its invisible set |
| `b_agent`, `a_kind` (0 agent, 1 human, 2 automated), `a_agent` | authors (int8 codes; humans not identified) |
| `room`, `pt_date`, `goal_no`, `regime`, `holdout` | B's context; `holdout` = locked holdout (calendar flag or `holdout_mask`) |
| `labelled`, `phase` | whether Jev (this prompt) labelled the pair, and in which phase (smoke, top1, audit, placebo, extras) |
| `p_reply` | Jev's probability that B is a direct reply to A |
| `p_supports`, `p_opposes`, `p_asks`, `p_neutral`, `stance`, `stance_conf` | Jev stance probabilities, hard choice and confidence |
| `opp_type`, `p_opp_position`, `p_opp_correction`, `p_opp_decline`, `p_opp_none` | subtype of Jev-opposes pairs (second pass) |
| `parent` | B's best labelled visible candidate (highest p_reply, ties to the better rank) when its p_reply ≥ 0.5 |
| `cost` | Jev cost of this pair's label (USD) |
| `label_source` | dq2, dq2+h37, h37 (H37 label only), none |
| `h37_stance`, `h37_s_soft`, `h37_responds` | H37's labels of the same pair (its prompt: 5 classes, looser "responds") |

### `reply_graph.parquet` (replier = B's author → target = A's author; −1 human, −2 automated)
`scale` ∈ {day, period}; `pt_date` (null for period rows), `goal_no`, `regime`, `holdout` (period rows are split by holdout so a period cut by an NE window has two rows); counts over labelled visible candidates:
`n_pairs_labelled`, `n_top1`, `reply_soft` (Σ p_reply), `reply_hard` (# B whose `parent` is by the target), `<stance>_soft` (Σ p_reply · p_stance), `<stance>_hard` (# parent pairs with that hard stance), `opp_position_soft`, `opp_position_hard`, and `n_mention_msgs` (# B messages by replier naming target, from `chat_mentions_clean.mentions_roster`, for comparison with the old proxy).

### Amendment 2 (2026-10-04, after an API-session outage; written before the calls it describes)
- **State at resume:** placebo (3,000), audit (10,891 pairs, 300 messages), smoke (20) and top1 (170,186 + 5 errors) done; $7.2364 spent; 184,097 unique labelled pairs, none twice. Blind sheet 1 (random 100) labelled before the outage, with no Jev answer seen.
- **The DQ1 context ledger now exists**, and its validation shows H18's naive call-start rule misplaces visibility: 65–70% of messages that rule calls invisible to a talk call were in fact in its context (mostly PAUSE windows and scheduled chat-mode calls), and prompt-token growth tracks the ledger (r 0.30) rather than the naive rule (r 0.03) where they disagree. Candidates were therefore rebuilt with `--visibility ledger` (`candidates_ledger.parquet`, `b_meta_ledger.parquet`): the pool cutoff is the ledger's `t_call` of the call that produced B (matched through B's AGENT_TALK event; chat timestamps sit ~60 ms earlier), with its bounds kept for an `uncertain` flag. Same window, cap, score and K. 2,623 messages without a ledger call (the Claude Code agent, unmatched) keep the H18 cutoff (`s_fallback`). **The ledger version is the primary one; `reply_pairs` and `reply_graph` are built from it.** Labels are properties of the (A, B) pair, so all existing labels are reused.
- **Effect:** the ledger top-1 differs from the H18 top-1 for 19% of messages (30% in regime I, 6% in regime III). 29,165 ledger top-1 pairs were unlabelled (22,387 non-holdout), about $1.15, more than the $0.66 left under the script cap.
- **Revised order for the remaining budget** (script cap unchanged at $7.90):
  1. `top1_ledger`: non-holdout unlabelled ledger top-1, regimes II and III first (3,018 pairs);
  2. `opptype`: restricted to non-holdout visible candidates Jev called `opposes` with p_reply ≥ 0.5 (5,072 pairs), the ones that enter parent stance counts;
  3. `top1_ledger` continued: non-holdout regime-I pairs in random order (seed 20261004) until the cap.
  `extras` (ranks 2–3) and holdout ledger top-1 are dropped. Unlabelled ledger top-1 pairs stay in `reply_pairs` with `labelled = false`; a B whose ledger top-1 is unlabelled still has its H18 top-1 labelled (now usually ledger rank ≥ 2).
- **Placebo is re-scored with ledger visibility** (pairs within the ledger's start bounds are reported separately as uncertain). The H18-based placebo is kept for comparison.
- **The audit's recall** refers to the H18 pools (whole pools labelled); ledger pools are supersets for those messages and are not re-audited.

---

## Results (2026-10-04)
All numbers are in `data/processed/shared/reply_threading/validation/results.json` (non-holdout only).

### What was labelled and spent
- **197,099 unique (A, B) pairs** labelled once each: 170,186 H18 top-1, 13,002 ledger top-1 (all of regimes II and III non-holdout, then 9,984 random regime-I non-holdout), 10,891 audit (whole pools of 300 messages), 3,000 placebo, 20 smoke. Plus 5,088 opposition-subtype labels. 5 top-1 calls errored (not retried).
- **Spend $7.9006** of the $8.00 cap (script cap $7.90; ~$0.000039 per pair call, ~$0.000033 per subtype call). No pair was sent twice; pairs H37 had labelled were not re-sent in the ledger phases.
- **Coverage:** 170,511 of 173,493 agent messages have a visible pool. 152,551 (89%) have their ledger top-1 labelled. Unlabelled ledger top-1: about 9,400 regime-I non-holdout, 6,778 holdout, 1,797 with an H37 label only; all of these B's still have their H18 top-1 labelled. 170,201 B's have at least one labelled pair in the graph set. **75,266 B's (44%) have a parent** (p_reply ≥ 0.5): non-holdout 37% in regime I, 48% in II, 54% in III. Parents: 76% supports, 11% neutral, 9% opposes, 4% asks; 96% agent, 3% human, 1% automated; 70% are named by B.

### Blind second labeler (175 pairs: 125 random, 50 enriched, shuffled)
| | Random (n = 125) | All, reweighted (n = 175) | Pre-registered |
| --- | --- | --- | --- |
| reply κ (p ≥ 0.5) | **0.56** (80%) | **0.61** (82%) | ≥ 0.5: **pass** |
| stance κ, 4 classes | 0.44 (71%) | 0.45 (71%) | ≥ 0.5: **fail** |
| stance κ, sign | 0.43 (72%) | 0.44 (72%) | |
- **Reply calibration:** p_reply ≥ 0.8 → 93% replies by the blind labeler; 0.5–0.8 → 49%; 0.2–0.5 → 22%; < 0.2 → 9%. Agreement 100% when |2p − 1| ≥ 0.8, 82% for 0.4–0.8, 59% below. Jev's "yes" precision 0.73, "no" 0.86.
- **Stance by Jev confidence:** agreement 81% at confidence ≥ 0.8 (n = 80; pre-registered ≥ 85%: **fail**), 48% at 0.5–0.8, 42% below 0.5.
- **Per-class precision:** neutral 0.99 (n = 71); supports 0.44 (n = 61; 34 of the misses are neutral: friendly acknowledgments and status replies read as support); asks 0.47 (n = 19); **opposes 0.08** (n = 24; 20 of them neutral; pre-registered ≥ 0.5: **fail**).
- **Noise floor of the raw opposes share:** Jev calls 5.7% of top-1 pairs opposes; the blind labeler 0.5%. At least 5.2 points of the 5.7% are false positives (H37's floor was 6.5 points). **The pair-level opposes label is mostly noise in ordinary village chat**, where true opposition is rare.
- **Opposition subtype:** in the blind set, 16 Jev-opposes items had a subtype (correction 11, position 3, decline 2); the blind labeler called 14 of them no pushback. Subtype κ 0.11; position precision 1/3 (n = 3). Among all parent opposes, subtypes are correction 2,683, position 1,312, decline 572, none 24, and 2,380 without a subtype (holdout, or labelled after the subtype pass ran). Treat `opp_type = position` as the best available conflict flag, not a validated one.

### Ground truth (does aggregated stance see conflict where it is assigned?)
- **#12 debates (H21 teams), debater-to-debater top-1 replies inside debate windows:** opposes 33% for opposite-team pairs (n = 165) vs 6% same-team (n = 226); soft sign −0.18 vs +0.31; within-debate permutation p = 0.0005. Aggregated stance does see assigned conflict, despite the low pair-level precision.
- **#51 roles (H22 classes), descriptive:** opposes share OP 3.9% (n = 181), U 5.6%, SY 4.1%, NC 7.7%, SR 10% (n = 660). No signal for the opposed-objective pairs.
- **Agreement with H37's Jev labels** (8,734 shared pairs, different prompt): sign κ 0.75 (86%), soft-sign correlation 0.93. Negative share 9.6% (H37) vs 6.9% (DQ2), so the narrower opposes wording removed about 28% of negatives. H37's "responds" is ≥ 0.5 for 96% of pairs, DQ2's p_reply for 68%: the stricter reply question discriminates.
- **H37's own pairs under the ledger:** 8.3% invisible (A arrived during B's call), 9.9% uncertain. The H18 rule had called 26.5% invisible.

### Placebo (H18 logic)
- **With H18's call-start rule** the placebo fails exactly as H18's mention placebo did: "invisible" pairs p_reply 0.34 vs 0.35 for visible pairs matched on mention × cosine decile.
- **But the rule, not the labels, is the main cause.** Re-scored with the ledger, 30% of those 2,000 pairs were in fact visible (p 0.44, like visible top-1 at 0.45), 43% are within the start bounds (p 0.32), and the strictly invisible 27% score 0.25.
- **All 929 strictly ledger-invisible labelled pairs:** p 0.24 vs 0.32 for matched visible pairs (≥ 0.5 rate 0.18 vs 0.26; ratio ≈ 0.75). When B names A's author: 0.48 vs 0.60; otherwise 0.20 vs 0.27. In regime III: 0.21 invisible vs 0.59 visible.
- **P-inv (pre-registered: < 0.5 × visible top-1 = 0.227):** 0.239, a **narrow fail**; the matched direction holds. p_reply still carries a thread-membership component: a message from the same exchange that B could not have seen gets about three quarters of the score.
- **P-rev: fail.** Reversed pairs (A posted after B, often a reply *to* B) get 0.38 (matched visible 0.46). Jev ignores direction; direction comes only from the candidate rule (A always precedes B's call).
- **P-mention: pass.** Top-1 pairs where B names A's author average 0.62 (others 0.29), but 35% of them get p < 0.5: a mention is not a reply.

### Ranking rule (audit of 300 whole H18 pools, 10,891 pairs)
- 64% of messages have at least one candidate with p ≥ 0.5, and they have 3.4 such candidates on average: many village messages answer several earlier messages, or summarize a thread.
- The best-scoring candidate (highest p_reply) is ranked 1st in 32% of messages, top-3 in 54%, top-10 in 76%. The pre-registered score beats recency alone (19%) and cosine alone (18%) as a top-1 ranker.
- Mean p_reply by feature: neither name 0.12; A names B's author 0.25; B names A's author 0.37; both 0.54. Cosine bottom quintile 0.08, top 0.31. `new` adds nothing (0.17 vs 0.17).
- Ranks 1–3 hold only 28% of all p ≥ 0.5 links. **`reply_graph` is a primary-parent graph** (at most one parent per B); it undercounts multi-target replies.

### Ledger vs H18 visibility
- The ledger top-1 differs from the H18 top-1 for 19% of messages (30% in regime I, 6% in regime III).
- 6.7% of parents (11% in regime I) are messages the H18 rule had hidden.
- 388 labelled H18 candidates turn out to be ledger-invisible; they are excluded from the graph set.

### Graph
- 34,548 rows (day and period scales).
- At period level (non-holdout agent pairs, n = 3,328), parent counts correlate 0.81 with mention counts. 508 pairs have mentions but no parent edge; 104 have parent edges but no mention.
- Parent edges total 75,266, against 162,583 mention messages.

## Limits
1. **Stance is reliable only in aggregate.** The 4-class κ is 0.44, opposes precision 0.08 and supports precision 0.44. Use soft sums (`*_soft`), contrasts between groups, and confidence ≥ 0.8. Never read an individual `opposes` label as conflict. `opp_type = position` is the closest flag, unvalidated (n = 3).
2. **p_reply is direction-blind and partly thread-based** (invisible pairs keep ~75% of the score; reversed pairs ~80%). Direction and visibility come from the candidate rule, so always use pairs with `pair_set = cand`.
3. **It is a primary-parent graph** (top-3 holds 28% of reply links; recall@3 is 54% for the single best link). Multi-target replies and long-range replies (> 60 min or beyond 40 messages) are missed.
4. **Coverage gaps:** about 18k ledger top-1 pairs are unlabelled (mostly regime-I non-holdout and holdout); ranks 2–3 are labelled only incidentally; the `extras` phase was dropped for budget.
5. **Visibility uncertainty:** regime-I/II ledger starts are latency-placed (low confidence); `vis_uncertain` flags A within the start bounds. The Claude Code agent's 2,623 messages use the H18 cutoff (`s_fallback`).
6. **One blind labeler** (Claude, n = 175), conservative on opposes by its rule ("reporting a different status is not opposition"). H37's rater, with a broader prompt, found opposes precision 0.30.
7. **Truncation:** A ≤ 700 characters, B ≤ 900 characters around the first mention of A's author.
8. **Holdout:** labelled and flagged (`holdout`); every number above is non-holdout. Exploratory users must drop `holdout = true`.
9. **Graph-level nulls:** sign-shuffle and per-pair FDR are anti-conservative on these graphs (H37). Use H37's calibrated ordered-logit agent-field null (`hypotheses/H37-stance-spins/analysis/calibrate.py`, import only).
10. **Label JSONLs key pairs by chat_core row index**, pinned in `reply_threading/msg_index.parquet`. `reply_pairs` carries message ids, so it survives a chat_core rebuild (DQ7). Re-running `compile` after a rebuild needs `msg_index.parquet` (kept).

## Rebuild
```
uv run python infra/shared/reply_threading.py candidates                       # H18 pools (labels were drawn from these)
uv run python infra/shared/reply_threading.py candidates --visibility ledger   # ledger pools (primary; needs call_windows)
uv run python infra/shared/reply_threading.py validate                         # needs the blind label JSONs in validation/
uv run python infra/shared/reply_threading.py compile                          # reply_pairs + reply_graph + provenance
```
The labelling commands (`label --phase ...`) are not part of a rebuild: they call the Jev API and are capped by the spend in `labels/*.jsonl`.
