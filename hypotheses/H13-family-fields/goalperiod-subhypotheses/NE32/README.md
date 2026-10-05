# H13 × NE32: newcomers to #51, including the isolated GPT-5.6 triplet (2026-07-09 → 09-04)

**Verdict:** failed
**Verdict (r2):** failed for #51 (newcomers start neutral here; pooled B-P1 passes on earlier joiners)
**Role:** native (round 1b, non-holdout)
**Period:** regime III · #51 (private roles) · newcomers after the 07-06 start: GPT-5.6 Sol, Terra, Luna (NE32: each alone in an onboarding room on 07-09, merged 07-10), Grok 4.5 (07-10), Kimi K3 (07-17), Claude Opus 5 (07-24), GLM-5.3 Flash (08-28), Claude Fable 5.1 (09-01), Muse Spark 1.3, Gemini 3.8 Flash and GPT-6 Astra (09-04). Non-holdout days only (through 09-04).

## Why this period
Newcomers are the cleanest unfitted test of a family field: an agent that has never been in the village is classified by the *incumbents'* family field, so nothing about the newcomer is fitted (axis D). NE32 adds three same-family agents who start with no one to copy. Each GPT-5.6 also holds a role shared with an incumbent (Luna–DeepSeek-V3.2 diplomats, Terra–GPT-5.2 YouTubers, Sol–Opus 4.6 forecasters), so family and role pull apart for two of the three. Round 1 ran this classification on content (4/11, chance 14%, p 0.06); round 1b runs it on behavior (HH267).

## Prediction
*Written 2026-10-04 07:13 UTC, before computing any behavioral statistic.* Design facts seen: join dates and roles (DQ6), the round-1 content classification above.

- **Observable.** Behavior state of card Amendment 2, z-scored within the newcomer's first H13 unit; day-demeaned over all agents present that day. Newcomer vector = mean of its first ≤ 3 eligible days (≥ 6 labelled active windows). Incumbent family fields = unit-normalized mean of the day-demeaned behavior means of incumbents (agents present before the newcomer's first day) in the same unit, per lab; newcomer excluded.
- **Classification.** Nearest family field (cosine) among labs with ≥ 1 incumbent. Accuracy against chance = mean 1/(number of candidate labs); one-sided binomial test.
- **Prediction (B-D).** Behavior accuracy ≥ 0.5 with binomial p < 0.05 (credence 0.4; #51 behavior is role-heavy and newcomers spend early days onboarding). Behavior accuracy ≥ the style-residualized content accuracy (shared `style_resid_period`, bge) on the same newcomers under the same rule (credence 0.55).
- **NE32 triplet (descriptive, n = 3).** On 07-09 and 07-10, each GPT-5.6's behavior vector is closer to the OpenAI incumbents' field than to its role-mate's own vector? Reported, not scored.
- **What counts against HH267 here:** behavior accuracy at chance while round 1's raw content (style) classification stays above it.

## Result
*Run 2026-10-04 (round 1b), after the prediction above. Code: `analysis/r1b_behavior.py` (`ne32`); data: `r1b/behavior.json` (`native_NE32`).* Eleven newcomers; Grok 4.5 (xAI) and Muse Spark 1.3 (Meta) have no incumbent of their own lab and are not classifiable, leaving 9.

| Prediction | Observed | Null / chance | Verdict |
| --- | --- | --- | --- |
| Behavior classifies newcomers into their own family at ≥ 0.5, p < 0.05 | **3/9 (0.33)**: Kimi K3, GLM-5.3 Flash, Claude Fable 5.1 correct; all three GPT-5.6, Opus 5, Gemini 3.8 Flash and GPT-6 Astra wrong; mean rank of own lab 3.4 | chance 0.15 (mean 1/candidates); binomial p = 0.14 | **fail** |
| Behavior ≥ style-free content (shared `style_resid_period`, bge) on the same newcomers | behavior 3/9 vs style-free words 2/9 (gte 1/9); raw content 2/9 under the same incumbent rule | — | pass (weak) |
| NE32 triplet, descriptive | 07-09 (isolated): Terra's behavior is closest to the OpenAI field (cos 0.69) and to its role-mate GPT-5.2 (0.66), where family and role coincide; Sol ranks OpenAI 4th (closest: Zhipu); Luna ranks it 3rd and sits closer to its role-mate DeepSeek-V3.2 (0.38) than to the OpenAI field (−0.005). On 07-10 (merged) all three rank OpenAI 2nd–3rd | n = 3 | descriptive |

**Reading.** Behavior carries no reliable family signature that transfers to a newcomer in #51, where private roles and onboarding dominate what an agent does in its first days. Behavior does slightly better than style-free words, but both are near chance. Round 1's raw-content newcomer result (4/11 by earlier units' fields) used a different rule (incumbent fields from earlier periods, words including style).

## Scorecard (period-specific axes)
- **D (unfitted predictions):** newcomer classification is unfitted; behavior 3/9 (p 0.14). Score 0.

<!-- r2:start -->
## Round 2 (2026-10-05): enculturation of newcomers (R2-B)
*Pre-registered in the card (Round 2, B-P1–B-P4), synthetic-validated, run on non-reserved data. This folder holds the #51 part; the pooled test uses 20 joiners from regimes I–III.*

| Joiner | Lab | a(d), d = 1… (bge raw) | r(d) |
| --- | --- | --- | --- |
| GPT-5.6 Terra | OpenAI | 0.26, 0.08, 0.13, 0.22 | 0.20, 0.03, -0.09, 0.01 |
| GPT-5.6 Luna | OpenAI | 0.38, 0.38, 0.28, 0.20, 0.06 | 0.00, 0.02, -0.14, 0.11, -0.06 |
| Kimi K3 | Moonshot | -0.03, 0.07, 0.00, -0.08, -0.03, 0.12 | -0.01, -0.12, 0.19, -0.16, 0.02, 0.01 |
| Claude Opus 5 | Anthropic | -0.06, 0.04, -0.00, -0.01, -0.15, -0.11 | 0.03, -0.00, 0.20, 0.12, 0.05, 0.12 |
| GLM-5.3 Flash | Zhipu | -0.22, -0.26, -0.12, -0.05, 0.07 | 0.21, 0.33, 0.14, 0.24, 0.29 |
| Claude Fable 5.1 | Anthropic | -0.26, -0.28, -0.17, -0.34 | 0.02, 0.13, 0.06, 0.01 |
| Gemini 3.8 Flash | Google | 0.05, -0.06 | 0.12, 0.28 |

**Reading.** Pooled over 20 joiners, newcomers start at their lab's field (a(1) 0.205, relabelling p 0.0045) and drift away (slope −0.034 per day [−0.065, −0.003]). *Post hoc:* #51 joiners start neutral (a(1) 0.018 [-0.141, 0.182], n = 7); the lab start and the drift come from the 13 earlier joiners (a(1) 0.305). In #51 private roles, assigned at or after joining, dominate content from day 1 (H98 NE33).
<!-- r2:end -->
