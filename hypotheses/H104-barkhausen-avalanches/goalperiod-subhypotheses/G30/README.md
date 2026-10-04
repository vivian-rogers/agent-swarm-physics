# H104 × G30: #30

**Verdict:** descriptive
**Role:** exploratory (replication)
**Period:** regime I · 11 agents · 5 days · attention channel only (4 isolated steps).

## Why this period
It passes the eligibility rule (≥ 3 isolated human steps with ≥ 3 agents at risk, ≥ 30 switches in at-risk spans). Amendment A1: with 3–4 steps the period has no tail power and BR is invalid, so it is a descriptive point.

## Prediction
*Written 2026-10-04 21:04 UTC, before running on this period.* Card P1, P3–P5 as they apply: X > 1 (credence 0.45 attention, 0.3 work); quiet-window D > 1.25 (endogenous clustering; the card's prior); tail inconclusive (A1). Verdict: descriptive by A1 (power < 0.5).

## Result
*Run 2026-10-04 21:04 UTC. Data: `data/processed/H104-barkhausen-avalanches/results/periods.parquet` (primary variant).*

| Channel | Isolated steps | X [95% CI] | V | D (quiet) | K (kickoff) |
| --- | --- | --- | --- | --- | --- |
| attention | 4 | 1.04 [0.78, 1.42] (p 0.46) | 0.08 | – | 1.16 |

- No step response; too few steps for the tail or BR (Amendment A1). The kickoff ratio K is the informative number here.
