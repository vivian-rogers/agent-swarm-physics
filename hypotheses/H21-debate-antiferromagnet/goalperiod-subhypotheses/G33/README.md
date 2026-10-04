# H21 × G33: Pentagon–AI news: discuss, debate, act (2026-03-02 → 03-04)

**Verdict:** failed
**Role:** native (round 1b, non-holdout)
**Period:** regime II · one room (#general) · 11 agents · 3 days (one unit) · a shared claims database with a strict sourcing norm; 22 nudges, 1 human message. No sides were assigned and no stance ground truth exists.

## Why this period
DQ9 lists #33 as the period for stance polarization on an external political topic. It is the natural control for #12: a period framed as "debate" in which nobody assigns teams. H21's round-2 redirect (H21-R2) says agreement is the default and disagreement appears only when assigned; if so, the reply-stance graph here should be ferromagnetic with no two-camp structure beyond what agent fields produce.

## Prediction
*Written 2026-10-04 07:14 UTC, before computing any #33 statistic.* Seen before: DQ9's description; the calibrated-null sizes from H37 (size 0.04 for the camp test at #40's and #51's structures).

- **Stance graph.** DQ2 `reply_pairs` (cand, labelled), agent → agent; soft stance per reply s = p_supports − p_opposes, weighted by p_reply. Pair coupling J_ij = mean s over replies in both directions (n_ij ≥ 3).
- **Statistics.** (i) mean soft stance s̄; (ii) the camp score: satisfied |J| weight of the ground-state two-camp split of the double-centred J (exact enumeration, N ≤ 11); (iii) the number of pairs with residual stance significantly negative (per-pair z < −2 on double-centred reply residuals).
- **Null.** The calibrated agent-field null (ordered logit with speaker and target fields on the hard labels, 300 simulations on the real reply structure; `infra/shared/nulls.py: agent_field_null`). Sign-shuffle values are reported but not used.
- **Prediction.** s̄ > 0 (ferromagnetic; credence 0.9); camp score within the null (calibrated p > 0.05; credence 0.75); negative-pair count within the null's 95% range (credence 0.7).
- **Content channel (descriptive).** If a stance split exists, H21's within-minus-cross content cosine Δ for that split (bge and gte); otherwise the content-graph ground-state split and its agreement with lab (family confound).

## Result
*Run 2026-10-04 (round 1b), after the prediction above. Code: `analysis/r1b.py` (`native_g33`); data: `r1b/r1b.json` → `native_G33`.* 12 agents, 2,540 labelled replies, 60 pairs with ≥ 3 replies.

| Prediction | Observed | Null | Verdict |
| --- | --- | --- | --- |
| s̄ > 0 (ferromagnetic) | mean soft stance +0.50; supports 44%, opposes 6.3% (at DQ2's label-noise floor) | — | pass |
| no camps beyond agent fields | camp score 0.815 (hard labels) | agent-field null mean 0.776, 95th percentile 0.835; p = 0.10 | pass (no camps) |
| negative pairs within the null | 1 pair | null mean 1.2, 95th percentile 3 | pass |
| content for the best stance split (descriptive) | within − cross cosine −0.066 (bge), −0.028 (gte); the split is not lab-sorted | — | — |

**Native verdict: failed for H21 (no spontaneous two-sublattice order), as predicted.** A period framed as "debate" but with no assigned sides is ferromagnetic in stance, with no factions beyond agent fields. Together with #12 and #26 this supports H21-R2: disagreement appears where a protocol assigns it.

**Round 1c (stance v2.1, 2026-10-04; prediction in the card, 22:10 UTC):** the true disagreement rate between agents is 0.019 [0, 0.049] (14 flags in 938 agent-to-agent replies), against 0.75 [0.50, 1.0] for #12 opponents. The flag graph forms no camps beyond the noise-aware agent-field null (camp score 0.79, null 95th percentile 0.82, p 0.32). Verdict unchanged: failed, as predicted.
