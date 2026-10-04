# DQ5: embedding robustness pack

Built 2026-10-04. Shared tables that let every content-based hypothesis check its result against three known
contaminations of the single-model pipeline:
- **one model:** bge-small-en-v1.5 (384-d) handles negation poorly (H21), and some results move when the
  representation changes (H29: driver rankings ρ 0.15–0.99 with raw 384-d vectors; H24: the coupling step depends on
  the dimension);
- **style:** H13's family field is writing style;
- **self-repetition:** 16–60% of an agent's daily chat in #38–#40 copies its own text (H12).

No text in any output: numbers, vectors and booleans only. Text is read in memory for lengths, token counts,
style features and exact-match checks. Every fit (whitening, style regression, the gte threshold) uses non-holdout
statements only. Agreement and flag summaries are reported on non-holdout statements only. Holdout rows are present
in every per-row table, flagged through `statements.holdout`, as in the existing tables.

## What was built

| Script (`infra/shared/`) | Outputs (`data/processed/shared/`) | Runtime |
| --- | --- | --- |
| `embed_models.py` | none: model registry and loaders (`statement_embeddings`, `load_whitener(regime, dim, model)`, `agent_vectors(level, model, variant)`, `statement_vectors`, `goal_vectors`, `group_ids`) | – |
| `build_embeddings_v2.py [embed\|vectors\|goals\|all]` | `embeddings/chat_gte_modernbert.npy` (183,485 × 768), `intentions_gte_modernbert.npy` (78,299 × 768), `agent_day_vec_gte_modernbert.npy`, `agent_win30_vec_gte_modernbert.npy`, `whitening_gte_modernbert_{I,II,III}.npz`, `goal_vectors_gte_modernbert.npy` (249 × 768) | embed 46 min on MPS under load 120–180 (chat 38 min, intentions 8 min); vectors 4 s; goals 10 s |
| `style_resid.py [build\|check\|all]` | `embeddings/statements_{white32,style_resid32,style_resid_period32}_<model>.npy` (251,792 × 32), `agent_{day,win30}_{white32,style_resid,style_resid_period}_<model>.npy`, `style_resid_fit.json`; check: `style_resid_check.{parquet,json}` | build 14 s (both models); check ~2 min |
| `statement_flags.py` | `statement_flags.parquet` (251,792 rows, 31 columns), `statement_flags_meta.json`, `statement_flags_by_period.parquet` | 2.7 min |
| `embedding_agreement.py` | `embeddings/agreement_gte_modernbert.{parquet,json}` | 35 s |

Sizes: 38 new files, 598 MB in total. The gte statement arrays are 402 MB, the gte agent vectors 71 MB, and the
32-d statement and agent arrays for both models 114 MB. Everything is fp16.
- **Alignment.** Arrays are aligned to the existing index tables: `chat_index`, `intentions_index`, `statements`,
  `agent_day`, `agent_win30`, `goals`.
- **Regrouping.** The agent grouping is recomputed and asserted identical to the existing tables. The original bge
  `agent_day_vec` / `agent_win30_vec` reproduce bit for bit under an order-safe join (`maintain_order="left"`).
- **Resumable.** The embedding run writes length-sorted 4,096-row chunks to `embeddings/_dq5_work/` and skips
  finished chunks on restart. The folder is removed after assembly.
- **Threads.** CPU is capped at 2 threads everywhere (torch, BLAS, polars, tokenizers).

### Model: `Alibaba-NLP/gte-modernbert-base` (revision e7f32e3c), 768-d, CLS pooling, no prefix
Why this model rather than e5-base-v2 or gte-base:
- **Different lineage at every level that can share a blind spot with bge-small.**
  - Backbone: ModernBERT (22 layers, RoPE, trained on 2T tokens of web and code), not a BERT.
  - Tokenizer: cased BPE (50k), not bge's uncased BERT WordPiece. e5-base-v2 and gte-base both share that
    WordPiece vocabulary with bge.
  - Lab and training data: Alibaba GTE, not BAAI.
  - Casing, code, URLs and hashes are common in agent chat, and an uncased WordPiece model cannot see them.
- **Strong.** MTEB-en 64.4, against 62.2 for bge-small and 61.5 for e5-base-v2. Clustering 46.5, STS 81.6; CoIR (code)
  79.3.
- **Symmetric, no prefix convention to get wrong.** e5 needs "query: " on both sides for symmetric tasks, and its
  cosines are compressed into ~0.7–1.0, which makes a 0.95 rule meaningless.
- **Practical.** Runs on MPS at the projected ~45 min. fp16 and fp32 outputs agree to cos ≥ 0.999; it was computed in
  fp32 and stored in fp16.

Inputs are identical to the bge run: the same rows, text cut at 2,000 characters, max 256 tokens. That isolates the
model from truncation. The truncated share is in `statement_flags` (`n_tok_bge`, `n_tok_gte`): 6% of #51 chat and
up to 32–33% of regime-III chat (#39, #41) exceed 256 tokens.

**Negation is not fixed.** In an ad hoc synthetic probe (5 negated pairs and 5 paraphrase pairs, no dataset text),
mean cosines were:

| | negated pairs | paraphrase pairs |
| --- | --- | --- |
| gte | 0.83 | 0.87 |
| bge | 0.82 | 0.86 |

In both models, several negations score above the weakest paraphrase. Neither embedding can test H21's stance
claims. That needs stance labels (DQ2).

## Agreement between the models (non-holdout, 33–35 goal periods)

| Level | Statistic | Median (min–max over periods) |
| --- | --- | --- |
| statements, chat | linear CKA, raw | 0.82 (0.73–0.90) |
| | linear CKA, regime-whitened 32-d | 0.70 (0.46–0.81) |
| | Spearman of pairwise cosines (sample of 1,500), whitened | 0.69 (0.46–0.85) |
| | 10-NN overlap (Jaccard), whitened | 0.26 (0.18–0.47) |
| statements, intentions | CKA whitened / pairwise ρ / 10-NN | 0.72 / 0.70 / 0.31 |
| agent-day (standard pipeline: `agent_day_vec` → whitener 32 → unit) | CKA | 0.91 (0.78–0.97) |
| | same-day agent-pair cosines, Spearman / Pearson | 0.91 (0.71–0.96) / 0.91 |
| | same, after day-demeaning (H13 δ) | 0.86 (0.46–0.97) |
| | agent × agent similarity of period-mean δ (H01/H13 agent fields) | 0.90 (0.09–0.99; the low values are 4-agent periods #5 and #6) |
| agent × 30-min window | same-window agent-pair cosines | 0.88 (0.63–0.95) |
| across periods (phase-diagram ordering) | mean agent-day alignment, bge vs gte | ρ = 0.95 (medians 0.485 vs 0.483) |
| | mean window alignment | ρ = 0.96 |
| | agent-day participation ratio | ρ = 0.89 (medians 8.7 vs 8.2) |
| | statement-cloud participation ratio | ρ = 0.94 chat, 0.84 intentions |

How to read the table:
- **Aggregates are robust.** Agent-day and window states, their alignment, and the cross-period ordering of alignment
  and effective dimension all survive the swap. Day-demeaned mean alignment is not listed: it is fixed by the number of
  agents (≈ −1/(n−1)).
- **Fine structure is not.** Statement-level geometry agrees much less. Nearest neighbours are mostly different
  (10-NN overlap 0.26), so clusters, kNN graphs, copy chains and per-statement projections are model-dependent.
- **#51 is the least robust period at every level.** It is the largest and most diverse (31 agents, private roles):
  agent-day pair ρ 0.71, window ρ 0.63, statement pair ρ 0.52, CKA-w32 0.57.
- **#36** has the lowest whitened statement CKA (0.46).

Per-period values: `embeddings/agreement_gte_modernbert.parquet`.

## Style-residualized vectors

Method (`style_resid.py`; numbers in `style_resid_fit.json`):
1. Each statement is whitened with its model's regime whitener (d = 32) and unit-normalized (`statements_white32`).
2. The 32 coordinates are regressed (OLS) on an intercept plus H13's 20 standardized style features:
   - chat features from `text_features.parquet`;
   - intention features computed in memory with `text_features.text_features`.
3. The fit is on non-holdout statements and applied to all rows.
4. Only the style-explained deviation (slopes × standardized features) is subtracted. The intercept, i.e. the group's
   mean direction, is kept.
5. Residuals are re-normalized.

Two fit groupings:
- **`style_resid`:** within (regime, kind). Style R² is 0.08–0.12 for chat and 0.06–0.11 for intentions.
- **`style_resid_period`:** within (goal period, regime, kind), the unit-of-analysis rule. Groups need at least 300
  non-holdout statements. Held-out periods (56,628 statements) fall back to the regime fit. For a confirmatory run on a
  held-out period, refit with `style_resid.fit_style` / `apply_style` on that period.

Agent vectors are plain means of the unit vectors over each existing `agent_day` / `agent_win30` row (chat +
intentions). They are not re-normalized and are already whitened. For chat-only aggregates, average the statement
arrays over chat rows.

**Check: H13's family-field test.** The test is a1/a2: T = same-family minus cross-family cosine of agent mean
day-demeaned chat vectors, with lab permutation (2,000) and agent jackknife. It was run on H13's 16 exploratory units
with both models. H13 itself reported raw 9/15 units at p < 0.05 (RE 0.080) and, after within-unit residualization,
0/15 (RE −0.001).

| | units p < 0.05 | RE T [95% CI] | median retention (raw-significant units) | regime-III goal classification (balanced acc., chance 0.11) | between-goal share |
| --- | --- | --- | --- | --- | --- |
| bge raw (white32) | 8/16 | 0.068 [0.018, 0.118] | – | 0.75 | 0.13 |
| bge `style_resid` | 4/16 | 0.022 [−0.015, 0.059] | 0.44 | 0.73 | 0.11 |
| bge `style_resid_period` | 1/16 | 0.007 [−0.029, 0.043] | 0.08 | 0.90 | 0.19 |
| gte raw | 8/16 | 0.064 [0.018, 0.109] | – | 0.76 | 0.14 |
| gte `style_resid` | 3/16 | 0.037 [0.002, 0.071] | 0.56 | 0.73 | 0.12 |
| gte `style_resid_period` | 1/16 (0 of the raw-significant) | 0.010 [−0.023, 0.042] | 0.07 | 0.89 | 0.19 |

Goal classification is leave-one-day-out nearest centroid on agent-day vectors.

What the check shows:
- **H13 replicates in both models.** The family field is writing style.
- **Only the period-level fit removes it.** The regime-level fit removes about half; the style→content map varies
  across periods.
- **Topic structure stays and sharpens.** Under the period-level fit, goal-period classification rises from 0.75 to
  0.90, and the day-field share within a unit rises from 0.073 to 0.088–0.092.
- **Agent identity is partly style.** The between-agent share of agent-day vectors drops from 0.64 to 0.55.
- **Pairwise agent-day geometry changes.** Spearman between raw and residualized pair cosines is 0.90 for the regime
  fit and 0.75–0.76 for the period fit.
- **Recommendation:** use `style_resid_period` for any claim about agent or family identity, roles or couplings.

## Statement flags (`statement_flags.parquet`, rows = `statements.parquet`, key `srow`)

Columns:
- **Keys and length:** `kind`, `src_row`, `n_chars`, `n_words`, `n_tok_bge`, `n_tok_gte`.
- **Model-free exact flags:** `exact_self_repeat` and `exact_cross_echo`. Exact means identical text after lower-casing
  and collapsing whitespace.
- **Per model** (`_bge`, `_gte`):
  - `self_repeat_cos` and `self_repeat_src`: the max cosine to the same agent's earlier same-kind statement that PT day,
    and that statement's row;
  - `self_repeat`;
  - `cross_echo_cos` and `cross_echo_src`: the max cosine to another agent's same-kind statement in [t − 2 h, t), any
    room, and that statement's row;
  - `cross_echo`;
  - `n_dup_agents`: distinct other agents with a same-kind statement above the threshold anywhere in the goal period;
  - `templated`: `n_dup_agents` ≥ 2, i.e. at least 3 agents use the form.
- **Primary flags:** `self_repeat`, `cross_echo` and `templated` are the bge versions (H12's rule).
- **Consensus flags:** `self_repeat_both`, `cross_echo_both` and `templated_both`.

Thresholds:
- **bge:** 0.95.
- **gte: 0.938.** gte cosines run lower, so its threshold is rate-matched to bge's non-holdout self-repeat rate
  (12.99%). Agreement at gte 0.95 is also in `statement_flags_meta.json`.

**Agreement (non-holdout).**

| Flag | Kind | Rate bge / gte | Cohen κ | Jaccard |
| --- | --- | --- | --- | --- |
| self_repeat | chat | 12.3% / 12.2% | 0.77 | 0.67 |
| self_repeat | intentions | 14.5% / 14.7% | 0.80 | 0.70 |
| cross_echo | chat | 2.0% / 1.7% | 0.60 | 0.44 |
| cross_echo | intentions | 0.44% / 0.46% | 0.75 | 0.61 |
| templated | chat | 1.0% / 0.8% | 0.61 | 0.44 |
| templated | intentions | 0.25% / 0.29% | 0.85 | 0.74 |

**Agreement against the model-free anchors.**
- **Exact repeats:** both models flag 100% of exact repeats. Exact repeats are 2.7% of chat and 4.2% of intentions,
  and only 22% (chat) / 29% (intentions) of the model flags.
- **Surface overlap** is measured as the character 5-gram Jaccard with the matched statement (in memory, sample of
  ≤ 3,000 per cell):

| Flag | Kind | Median Jaccard: flagged by both | flagged by one model only | flagged by neither |
| --- | --- | --- | --- | --- |
| self_repeat | chat | 0.57 | 0.27–0.31 | 0.12 |
| self_repeat | intentions | 0.78 | 0.38–0.43 | 0.17 |
| cross_echo | chat | 0.32 | 0.22–0.23 | 0.07 |

What the anchors show:
- **Consensus flags are near-copies.** When both models flag a statement, it shares most of its surface text with the
  match.
- **Single-model flags are restatements.** They say the same thing in other words, and neither model's single flags are
  closer to copies than the other's.
- **Cross-agent echoes are mostly semantic,** not copied text: even consensus chat echoes have a median Jaccard of
  0.32.

**Rates per goal period** are in `statement_flags_by_period.parquet` (chat, non-holdout):
- **self_repeat (bge):**
  - #2 43%, #3 26%, #10–#11 28%;
  - #18–#21 16–34%;
  - #24–#37 0.6–18%, falling to ≤ 6.4% from #27;
  - #38 20%, #39 22%, #40 10%, #41 7%, #42–#44 ≤ 2%;
  - #51 2.9%.
- **cross_echo (bge):**
  - ≤ 1% in most periods;
  - highest in #18 (13%), #21 (11%), #11 (6%), #19 (6%) and #25 (4%).
- **templated** is rare except #18 (9%) and #21 (9%).
- **Exact self-repeats** are 0–0.3% in regime III: none of the regime-III repetition is literal copying.

**H12's self-repetition depends on the model in exactly its periods.** In #38 bge flags 20% of chat and gte 10%; in
#40, 10% and 6%. #39 agrees (22% and 23%).
- **Agent-days with ≥ 5 messages:**

  | Period | bge q75 / q90 | gte q75 / q90 |
  | --- | --- | --- |
  | #38 | 33% / 71% | 15% / 26% |
  | #40 | 17% / 29% | 9% / 21% |

  Spearman between the models' agent-day shares is 0.79.
- **Two #38 agents** go from 67% and 54% (bge) to 19% and 23% (gte).
- **Likely why:** their messages are formulaic status updates with varying details. bge-small (uncased WordPiece)
  scores them as near-identical and gte does not; their surface overlap is low (see the anchors above).
- **Implication:** the "16–60% copies" figure is mostly restatement, not copying. Dedupe with `self_repeat_both` to
  remove copies; use either model's flag to remove restatements.

## How to use
```python
from embed_models import statement_embeddings, load_whitener, agent_vectors, statement_vectors, goal_vectors
E = statement_embeddings("gte_modernbert")                  # rows of statements.parquet, float32
W = load_whitener("III", 32, model="gte_modernbert")         # same contract as common.load_whitener
V = agent_vectors("day", "gte_modernbert")                   # rows of agent_day.parquet (raw; whiten downstream)
S = agent_vectors("day", "bge_small", "style_resid_period")  # already whitened 32-d; do not whiten again
F = pl.read_parquet(OUT / "statement_flags.parquet")         # filter ~F["self_repeat_both"] before content stats
```

## Limits
- **One second model.** Agreement bounds model-specific artefacts but not shared ones: both models are contrastive
  sentence encoders, neither handles negation, and both truncate at 256 tokens. Long regime-III messages (6–33% of
  chat truncated per period) are judged on their first 256 tokens in both.
- **Thresholds.** The gte threshold is rate-matched to bge, so flag rates agree by construction for self-repeat.
  Agreement is about *which* statements are flagged. The 0.95 rule itself is not validated against human judgement.
  The surface-overlap check only says consensus flags are near-copies.
- **The style regression is linear** in 20 hand-made features. Style that the features miss (word choice, markers)
  stays. The period fit also removes any position that correlates with style (H13's caveat).
- **Held-out periods** use the regime-level fit in `style_resid_period`, so they are residualized less aggressively than
  explored periods. Refit at confirmation time.
- **Whitened at d = 32 only** for the style variants. H24 found results that change between 32 and 64; refit at 64 from
  the statement embeddings if needed (OLS is column-wise, so the first 32 columns are unchanged).
- **cross_echo** ignores rooms (an echo across rooms may be coincidence) and human messages. **templated** uses whole
  goal periods, so long periods have more chances to match.
- **The negation probe is 10 synthetic pairs.** It is indicative, not a benchmark.

## Which content results to re-check first
| Priority | Hypothesis | Why exposed | Variant to use |
| --- | --- | --- | --- |
| 1 | H12 groupthink / dimensional collapse | the self-repetition fact halves in #38/#40 under gte; statement-level effective dimension | gte whitened statements (`load_whitener(r, 64, "gte_modernbert")`); dedupe with `self_repeat_both` (copies) and with `self_repeat_bge \| self_repeat_gte` (restatements) as brackets; `cross_echo` for echo-driven collapse |
| 2 | H26 content near-critical | heavy dedupe; cluster and avalanche statistics are statement-level (10-NN overlap 0.26) | flags-based dedupe (`self_repeat_both`, `templated`); gte statements |
| 3 | H20 content aging | self-repeats inflate short-lag two-time overlap; null shape is model-specific | `agent_day_vec_gte_modernbert` + gte whitener at 64; rebuild agent vectors without `self_repeat_both` rows from `statement_vectors(..., "white32")`; re-estimate the anisotropic null per model |
| 4 | H29 driver nodes | rankings already unstable; #51 is the least robust period (window ρ 0.63) | gte whitened 32-d statements; compare driver rankings per unit, G51b first |
| 5 | H22 private-goals spin glass | #51 overlaps; style offsets act as frozen (quenched) fields | `statements_style_resid_period32_*` and gte, #51 units |
| 6 | H24 forecast-coupling switch | instrument-sensitive step; single-direction goal removal leaks | gte + `goal_vectors("gte_modernbert")`; `style_resid_period` (style offsets can pose as coupling) |
| 7 | H01 emergent superagents | agent identity and role fields; agent share drops 0.64 → 0.55 under style removal; #51 weakest | `agent_day_style_resid_period_*` with both models; gte goal vectors |
| 8 | H36 reorganization alarm | uses `agent_win30_vec`; window agreement 0.88 overall but 0.63 in #51 | `agent_win30_vec_gte_modernbert`; `agent_win30_style_resid_period_*` |
| 9 | H10 goals as Legendre pushes | day- and agent-day-level projections (robust level), but on bge goal vectors | gte goal vectors + gte whitener |
| 10 | H13 family fields | done here: the style verdict replicates in gte | cite `style_resid_check.json`; adopt `style_resid_period` as the shared S-a |
| – | H21 debate antiferromagnet | negation is not fixed by the swap | stance labels (DQ2) instead; run gte only as a sanity check |
