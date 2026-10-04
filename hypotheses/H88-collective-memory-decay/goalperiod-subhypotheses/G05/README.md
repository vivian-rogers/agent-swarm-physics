# H88 × G05: the afterlife of goal period #5 (2025-06-19 → 2025-06-25)

**Verdict:** mixed
**Role:** native (exploratory)
**Period:** regime I · items: 1 artifacts, 69 terms · follow-up 120 village days after 2025-06-25 (held-out days censored). Channels eligible: terms.

## Why this period
from 2025-05-23 (Claude Opus 4 joins) to 2025-08-15 the roster is fixed at four agents (Claude 3.7 Sonnet, o3, Gemini 2.5 Pro, Claude Opus 4). No departure and no newcomer can shape the decay of attention to #4–#7's items.

## Prediction
*Written 2026-10-04 21:04 UTC, before running (native N1).*
- **Why native:** from 2025-05-23 (Claude Opus 4 joins) to 2025-08-15 the roster is fixed at four agents (Claude 3.7 Sonnet, o3, Gemini 2.5 Pro, Claude Opus 4). No departure and no newcomer can shape the decay of attention to #4–#7's items.
- **N1 prediction:** with the follow-up truncated at 2025-08-15, M2 beats M1 (best by QAIC and ΔQAIC ≥ 2) for at least 2 of #4, #5, #6, #7 on artifacts or terms.
- *Counts against:* M1 best in ≥ 3 of 4, or no decay (decay needs carrier turnover).

The templated replication prediction also applies to this period:
*Written 2026-10-04 21:04 UTC, before running on this period. Templated replication prediction (layer 1).*
- **Observable:** the veterans' attention share to this period's items over the 120 village days after its last day (artifacts: repos, sites, files first seen here; terms: H34 N-class coinages first seen here). Fits M1 (single exponential), M2 (biexponential), M1c (exponential + floor), MP (power law) by quasi-likelihood; QAIC.
- **Prediction:** M2 is the best model and beats M1 by ≥ 2 QAIC (a fast τ₁ of 0.5–5 village days and a slow τ₂ of 10–120); the present veterans' share at k 21–40 is below the share at k 1–3.
- **Verdict rule (templated, per channel; artifacts primary where eligible):** supported if M2 is best with ΔQAIC(M1−M2) ≥ 2; failed if M1 is best; mixed if M1c or MP is best. Per-period power for the call is 0.4–0.6 (artifacts) and 0.6–0.97 (terms) at the synthetic biexponential.
- *Counts against:* M1 best (kill 1), or no decay of the present veterans' share (kill 2).

## Result
*Run 2026-10-04 21:09 UTC (`analysis/replication.py`, `analysis/natives.py`) → `data/processed/H88-collective-memory-decay/replication/replication.json`, `natives/natives.json`.*

- **Artifacts (veterans):** not eligible (design) or fewer than 50 post-period veteran uses.
- **Terms (veterans):** not eligible (design) or fewer than 50 post-period veteran uses.
- **Templated verdict:** n/a (terms channel).

**N1 (closed village, follow-up truncated at 2025-08-15).**

| Items | Veteran uses | Best | ΔQAIC(M1−M2) | M1c τ (days) | floor c/A |
| --- | --- | --- | --- | --- | --- |
| #4 art | 7 | too few uses | | | |
| #4 term | 471 | MP | -2.0 | 6.8 | 0.356 |
| #5 art | 0 | too few uses | | | |
| #5 term | 35 | MP | +2.0 | 1.0 | 0.002 |
| #6 art | 0 | too few uses | | | |
| #6 term | 218 | M1c | +8.8 | 1.1 | 0.037 |
| #7 art | 0 | too few uses | | | |
| #7 term | 0 | too few uses | | | |

- **Verdict: mixed.** No period is biexponential (0 of 3 fitted); none is a single exponential either. Attention to #4–#6's terms decays with the roster fixed, as a power law (#4, #5) or to a floor (#6). So decay does not need carrier turnover (kill 2 fails here), but its form is not Candia's. Artifacts of #4–#7 are almost never used after their period (7 uses).

## Scorecard (period-specific axes)
- E (interventional): 1. Decay with a closed roster rules out departure-driven decay for #4–#6; it does not pick Candia's form.
- D: 1.
