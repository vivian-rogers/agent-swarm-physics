# H104 × NE38: a local field step on one agent (2026-07-29)

**Verdict:** supported
**Role:** native (exploratory)
**Period:** regime III · #51 private roles · unit 51f starts at NE38 (07-29). A human reassigns Claude Opus 5's role (game dev → mathematician) by message.

## Why this period
NE38 is the cleanest local field step in the data: a human message changes one agent's random field. In the zero-temperature RFIM the target flips; with weak coupling (H22, H98) the flip does not propagate, so the avalanche is the target alone. A near-critical swarm would carry it to others.

## Prediction
*Written 2026-10-04 20:25 UTC, before running.* Step = the reassigning human session on 07-29 (first human message to the target after 16:40 UTC; W = 120 min).
- **NE38-a (target flips).** Agent 40 has a switch (work or attention channel) in (t_k, t_k + 120 min]. Credence 0.6.
- **NE38-b (no avalanche beyond the target).** The number of other at-risk agents with a switch in (t_k, t_k + 120 min] lies inside the time-shuffle null's central 90% band, in both channels. Credence 0.7.
- Counts against the RFIM-with-weak-coupling reading: others' switches above the null's 95th percentile.

## Result
*Run 2026-10-04 21:05 UTC. Data: `results/natives.json`.*
- Step: the human session at 2026-07-29 16:50 UTC (1 message); agent 40 read it.
- **NE38-a passes:** agent 40 switches in the attention channel within 120 min (no work switch).
- **NE38-b passes:** other at-risk agents switching: 2 of 26 (work; null band 1–5, mean 2.8) and 10 of 26 (attention; null band 10–15, mean 12.5, at the low edge).
- A one-agent field step stays local, as the weak-coupling RFIM predicts.
