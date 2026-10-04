# H07 × G36: Interact with other AI agents outside the Village! (2026-03-23 → 2026-03-30)

**Verdict:** supported
**Verdict (1b):** supported (unchanged); native second fork supported
**Role:** exploratory; native (round 1b: second fork event)
**Period:** regime II → III (F perma-computer-use lands 03-24) · mode C · 13 agents · rooms #best / #rest (split continues) · 5 active days × 4 h. Split inside: the regime boundary on 03-24 (no fork content changed on either side of it).

## Why this period
The first period after #35, with a goal unrelated to the game: the test of P4's "freeze" (horizontal copy information stops changing once commit activity collapses).

## Prediction
*Written 2026-10-03, before any repository history was fetched (main card, P4):* after the goal change on 03-23, commits per active day fall ≥ 80%, and horizontal copy information changes by < 10% of its #35 drop.

## Result
| Test | Observed | Verdict |
| --- | --- | --- |
| activity collapse | 3 fork commits in 5 active days (0.6/day vs. 71.4 in #35; −99%) | supported |
| horizontal freeze | I_copy(best; rest) − shuffle null unchanged (0.000 bits) for every feature type. The 03-23 README edits touched a file that already differed between the forks | supported |

All three #36 fork commits are README "for autonomous agents" cross-links, made by #rest agents in the spirit of the #36 goal:
- GPT-5.2 on #rest's repo;
- Haiku 4.5 and Sonnet 4.5 on **#best's** repo (cross-fork commits, no game content).

Other cross-room contact: room visits by Claude Code (03-23) and DeepSeek-V3.2 (03-26/27) to #best, and 12 explicit references by #rest agents to `rpg-game-best`, mostly on 03-23. None changed game content. Data: `data/processed/H07-rpg-forks/horizontal_day.parquet`, `leakage.parquet`.

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| D unfitted predictions | 2 | Freeze and activity collapse as predicted, before the data were seen. |

## Notes
- 2026-10-03: the F boundary (03-24) leaves no trace in the forks because nothing game-related was committed after 03-23.
- Shuffle-null estimates carry Monte Carlo noise of about 0.002 bits between runs (100 draws; key order follows Python's per-process hash seed), so differences below about 0.01 bits are not meaningful.

## Round 1b native: a second fork event (`agent-papers`, 03-26/27)
**Role (round 1b):** native. *Prediction written 2026-10-04 from a structural scan only:* five on-disk clones share one root commit (2026-03-26 04:36 UTC): an outside agent's repo (`terminator2-agent/agent-papers`, 214 commits to 05-18) and copies under `gpt-5-4` (#best), `gemini-3-1-pro` (#best), `deepseek-v32` (#rest) and `ai-village-agents` (91–97 commits each, last commits 03-27 → 04-03). I have not read any commit, author, file list or tree in them.

**Design.** H07's estimator on file features (path → blob id; trees only, no blob contents): ancestor A = the newest commit contained in every village copy's default branch (H07's rule); lineage = `A..HEAD` first-parent, commits up to 2026-04-03 (non-holdout). Vertical copy fraction per lineage; horizontal identity on A's keys vs P(both unchanged) per pair; shared innovations (same path, same new blob in two copies, absent from A), each checked for presence in the upstream repo before both adoptions.
- **N36-1.** Unlike the RPG forks, the independent-lineage bound is violated for at least one pair: horizontal identity on ancestor keys exceeds P(both unchanged) by ≥ 0.02. Credence 0.6.
- **N36-2.** Shared innovations exist (≥ 5 for at least one pair), and ≥ 80% of them are present upstream before both copies adopt them: channel-borne (upstream syncs), not convergent. Credence 0.55.
- **N36-3 (H57 control).** Within-room pairs (the two #best copies) share at least as many innovations as cross-room pairs involving the #rest copy. Credence 0.5.
- If the copies have < 5 post-A commits each, the test is n/a (no divergence to measure).

### Result (round 1b, run 2026-10-04)
Data: `data/processed/H07-rpg-forks/r1b/results_r1b.json` (`papers`). Ancestor A = `5720e26` (2026-03-26 18:32 UTC, 30 files), the newest commit in all four village copies' `main`.

| Test | Observed | Verdict |
| --- | --- | --- |
| Divergence exists | The two #best copies (GPT-5.4, Gemini 3.1 Pro) have **0** first-parent commits on `main` after A: their work went into branches and pull requests to the upstream. The #rest copy (DeepSeek-V3.2) and the org copy have 52 and 54, all synced from the upstream (authors: the outside agent, a second outside agent, GPT-5.4 and Gemini 3.1 Pro via merged PRs) | lineages exist for 2 of 4 copies |
| N36-1 bound violated (≥ 0.02) | #rest copy vs org copy: identity on A's files 0.97 vs P(both unchanged) 0.67 (excess 0.30); every pair involving a frozen #best copy: excess 0 | **supported** |
| N36-2 ≥ 5 shared innovations, ≥ 80% upstream-first | 29 shared new files (#rest ~ org), 29/29 present upstream before both adoptions | **supported** |
| N36-3 within-room ≥ cross-room | the #best–#best pair has nothing to share (both frozen) | **n/a** |

**Reading.** A second fork event with the opposite mechanism: these are contribution forks, and the copies re-converge by pulling the shared upstream, so the independent-lineage bound fails exactly as a channel predicts. Together with the RPG (no channel, bound held exactly), this gives the bound both a positive and a negative case. File level only (trees, no blob contents).
