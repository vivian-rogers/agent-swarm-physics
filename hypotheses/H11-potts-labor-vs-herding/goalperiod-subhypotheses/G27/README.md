# H11 × G27: Hack the OWASP Juice Shop; compete on challenges completed (2026-01-12 → 2026-01-23)

**Verdict:** descriptive (first tested in round 2)
**Verdict (r2):** R1 attachment G27 att: supported; R2 stigmergy G27 att: failed
**Role:** replication (round 2 common estimators)
**Period:** regime I · whole goal period used as the round-2 unit (named exception (d), card Round 2).

## Why this period
It has ≥ 25 recruit joins with ≥ 2 choices in at least one channel, so the round-2 choice models are testable here. It was not a round-1 candidate or transfer period.

## Round 2 (2026-10-05)
*Predictions: the card's Round 2 block (written 2026-10-05 03:30 UTC, before any round-2 statistic; amendment A1 after the synthetic validation, before real data). Units: whole period (#51: period units). Data: `data/processed/H11-potts-labor-vs-herding/r2/` (`results/real_r2.json`, `score_r2.json`).*

| Unit · channel | α [95% CI] (R1a) | α_FE | lag − lead (R1d) | replay inside: top share / exp(H) (fit · Yule · uniform) | ΔLL artifact − chat (R2a) | OR chat-read \| act · OR commits \| chat (R2b) | read − lead, chat · commits (R2c) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| G27 · att (n = 25) | +1.39 [+0.62, +2.16] | +1.12 [+0.38, +1.86] | +0.35 [-1.71, +2.41] | ✓/✓ · ✓/✗ · ✗/✗ | -0.618 [-1.225, -0.011] | 1.44 · – | -1.48 [-2.95, -0.00] · +0.42 [-0.81, +1.66] |

Reading rules (card): R1a counts α with CI > 0; causal attachment needs α_FE > 0 and lag − lead > 0 together (A1); R2a counts ΔLL > 0 (artifact beats chat), with the CI-based count next to it; R3a counts log RR > 0. n.e. = not estimable (A1: < 5 chosen exposed rows), n.s. = CI includes 0.
