# H14 × NE14: The regime boundary inside #36 (03-23 regime II vs 03-24 → 03-27 regime III)

**Verdict:** mixed
**Role:** native
**Period:** #36 (interact with outside agents), same goal and roster across the boundary. 36a = 03-23 (regime II, one day), 36b/36c = 03-24 → 03-27 (perma-computer-use, forced erasures from 03-24; NE16 memory fix on 03-26). 12 agents, two rooms.

## Why this period
Round 1's regime contrast (regime I 7–29× more irreversible per transition) compared periods two months apart. #36 is the only goal that straddles the regime II → III change, so the contrast can be tested at a fixed goal (DQ9 cross-index: NE14 for H14).

## Prediction
*Written 2026-10-04, before running (card, "Round 1b", N2).* Pooled per-transition EP (all agents, agent folds) drops by ≥ 30% from 03-23 to 03-24 → 03-27 on the coarse and act_sh chains (credence 0.6), and the v3 semantic EP drops less in relative terms than the coarse EP (after/before ratio v3 > coarse; credence 0.5).

## Result
*Run 2026-10-04 (`analysis/native_r1b.py`; `r1b/native_r1b.json`). Ratios after/before with agent-bootstrap 95% CIs.*

| Chain | before (03-23) | after (03-24 → 03-27) | ratio [95% CI] | prediction |
| --- | --- | --- | --- | --- |
| coarse (turns) | 0.0217 | 0.0055 | 0.25 [0.04, 6.6] | drop ≥ 30%: ✓ (point) |
| act_sh (turns) | 0.0667 | 0.0476 | 0.71 [0.22, 1.51] | drop ≥ 30%: ✗ (−29%) |
| v3 soft (5-min windows) | 0.0153 | 0.0111 | 0.72 [0.07, 1.06] | ratio > coarse: ✓ (point) |
| v3 − coarse ratio | | | CI [−6.5, 0.8] | not significant |

**Mixed and underpowered.** The coarse arrow falls by three quarters across the boundary while the fine and semantic arrows fall by about 30%, the pattern expected if the regime contrast is mostly scaffold structure in the coarse chain. With one day before the change, none of the ratios is distinguishable from 1.

## Scorecard (period-specific axes)
E 0 (no significant change). G 1 (the coarse chain moves most where the scaffold changed).

## Notes
- The forced-erasure regime (NE41) and perma-computer-use (NE14b) start on the same day, so this is a bundle.
