# H11 × G36: Interact with other AI agents outside the Village (2026-03-23 → 2026-03-27)

**Verdict:** descriptive (first tested in round 2)
**Verdict (r2):** R1 attachment G36 work: supported; R2 stigmergy G36 work: n.s. (−); R3 herding raises output G36: n.s. (+); θ < 1 G36: yes
**Role:** replication (round 2 common estimators)
**Period:** regime II → III (units 36a-c) · whole goal period used as the round-2 unit (named exception (d), card Round 2).

## Why this period
It has ≥ 25 recruit joins with ≥ 2 choices in at least one channel, so the round-2 choice models are testable here. It was not a round-1 candidate or transfer period.

## Round 2 (2026-10-05)
*Predictions: the card's Round 2 block (written 2026-10-05 03:30 UTC, before any round-2 statistic; amendment A1 after the synthetic validation, before real data). Units: whole period (#51: period units). Data: `data/processed/H11-potts-labor-vs-herding/r2/` (`results/real_r2.json`, `score_r2.json`).*

| Unit · channel | α [95% CI] (R1a) | α_FE | lag − lead (R1d) | replay inside: top share / exp(H) (fit · Yule · uniform) | ΔLL artifact − chat (R2a) | OR chat-read \| act · OR commits \| chat (R2b) | read − lead, chat · commits (R2c) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| G36 · work (n = 43) | +1.07 [+0.65, +1.49] | +0.73 [+0.37, +1.09] | -0.54 [-1.77, +0.68] | ✓/✗ · ✓/✓ · ✗/✗ | -0.042 [-0.253, +0.170] | 2.38 · 6.96 | +0.98 [+0.16, +1.79] · -1.49 [-2.84, -0.13] |
| G36 · att (n = 167) | +0.59 [+0.31, +0.88] | +0.01 [-0.35, +0.36] | -0.14 [-0.60, +0.32] | ✗/✗ · ✗/✗ · ✗/✗ | -0.028 [-0.109, +0.053] | 3.38 · 1.97 | +0.18 [-0.49, +0.85] · -0.06 [-0.57, +0.45] |

| Unit | log RR herd vs solo, commits (R3a) | landed | matched pairs (mean log ratio) | θ crowding (R3b) | herd / solo windows |
| --- | --- | --- | --- | --- | --- |
| G36 (shared) | +0.29 [-0.08, +0.65] | +0.35 [-0.07, +0.76] | +0.21 ± 0.09 | +0.44 [+0.19, +0.68] | 168/83 |

Reading rules (card): R1a counts α with CI > 0; causal attachment needs α_FE > 0 and lag − lead > 0 together (A1); R2a counts ΔLL > 0 (artifact beats chat), with the CI-based count next to it; R3a counts log RR > 0. n.e. = not estimable (A1: < 5 chosen exposed rows), n.s. = CI includes 0.
