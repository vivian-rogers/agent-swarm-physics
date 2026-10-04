# H55 × G38: charity fundraiser, year 2 (2026-04-02 → 2026-04-24)

**Verdict:** failed
**Role:** native
**Period:** regime III · mode O/C · 12 → 14 agents · two rooms (#best, #rest) · 17 days; units 38a–38e (NE36 on day 1, NE17, NE18, two joins).

## Why this period
The loop-densest regime-III week with enough directed messages to test the rivals of the immune reading: 20% of chat statements are restatements under bge (10% under gte; DQ5's largest model dependence) and 538 restatement at-risk steps, 261 of them with a directed read. The two rooms are two parallel sub-swarms (replicates), and copies vs restatements can be compared where they differ most. The Jev correction sensor flags almost nothing here, so this period tests *what* breaks loops (address, novelty, sender kind) rather than corrections as such.

## Prediction
*Written 2026-10-04 06:41 UTC, before any H55 statistic on this period* (seen: the count of at-risk steps with directed and with Jev-correction reads, no outcomes).
- **N38a (R-address):** a directed read raises restatement-loop escape relative to matched steps without one (address Δ > 0, p < 0.05), with the same sign in #best and #rest. [0.6]
- **N38b (R-novelty):** among steps with a directed read, a novel first directed message (top novelty tercile) raises escape relative to the bottom tercile (Δ_nov > 0). [0.5]
- **N38c (HH210):** fewer than 5% of G38's restatement loop episodes receive any Jev correction. [0.85]
- **N38d:** N38a holds with the same sign for copy loops (both models). [0.6]
- *Against:* directed reads do not change loop escape (loops end on their own clock, R0).

## Result
*Run 2026-10-04 (`analysis/native.py`; data `data/processed/H55-norm-enforcer-immunity/G38/native.json`).* Restatement loops: 538 at-risk steps (escape 0.24), 261 with a directed read, 1 with a Jev correction read; almost all in #rest (239 of 245 matched steps). Copy loops: 124 steps, 30 with a directed read.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| N38a directed read raises escape, both rooms | Δ +0.012 [−0.054, +0.091] (245 steps); #rest +0.009; #best not scorable (no matched steps) | matched no-read steps, agent-demeaned | **fail** |
| N38b novel directed message raises escape | top − bottom novelty tercile +0.02 [−0.11, +0.17] | cluster bootstrap | **fail** |
| N38c < 5% of loop episodes get a correction | 1 of 154 (0.6%); 62% get some directed read | | **pass** |
| N38d copy loops, address | Δ −0.04 [−0.24, +0.21] (30 steps) | | **fail** |

**Reading.** In the loop-densest regime-III week, restatement loops are not shortened by being addressed or by novel input: 62% of loop episodes receive a directed message and escape does not change. Corrections almost never reach a looping agent. The pooled address effect (card P6, +0.05) comes from regime I, above all the #12 debates (+0.24).

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 0 | no lever beats the matched null here |
| D unfitted predictions | 1 | HH210's coverage prediction holds (0.6%) |
