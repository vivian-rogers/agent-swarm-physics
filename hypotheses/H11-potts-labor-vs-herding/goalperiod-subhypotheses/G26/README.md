# H11 × G26: Elect a village leader. They choose this week's goal! (2026-01-05 → 2026-01-12)

**Verdict:** P1 supported; P2 supported; HH22: jump supported, mechanism inconclusive
**Verdict (1b):** mixed (native: jump on the right vote; cascade, not field)
**Role:** native (round 1b: #26 per election round on DQ6 ballots; round 1: exploratory candidate)
**Period:** regime I · mode C · N = 10 at start · one room (#general) · 5 active days. Class for H11: **FM-consensus**.

## Why this period
HH22 (folded into H11 on 2026-10-03 by Vivian) and HH84: approval voting over six candidates, a three-way tie, then a runoff. Two state variants: project labels (the shared ballot documents) for P1/P2, and **chat-declared votes** for the HH22 tests.

## Prediction
*Written 2026-10-03, before running on this period.*
- **Class prediction:** ferromagnetic (consensus on a shared choice): βJ_CW > 0 (P1), βJ_PL z_N2 ≥ +2 (P2), and a first-order jump in the dominant share (P3). Per-period verdict on P1: **supported** if the sign is right and |t| > t_(D−1, 0.975) (leave-one-day-out jackknife); **weak** if the sign is right but not significant; **failed** if the sign is wrong.
- **P3 (consensus jump):** the share x₁ of the final-day dominant project shows an O4 'jump' (Δ ≥ 0.3, τ ≤ 2 windows, persistence ≤ 0.15), and βJ_CW ≥ βJ_s(q_eff) (first-order region). A jump with βJ_CW < βJ_s is scored as a field-driven step; a gradual rise counts against P3.
- **P4 (control):** the action-class βJ_CW is positive or ≈ 0 whatever the class.
- **P7 (prior):** |βJ_CW| < 2, below βJ_s(q), so no spontaneous first-order transition.
- **Minimum data:** ≥ 15 room blocks with N_b ≥ 3 at W = 30; otherwise n/a.
- **What would count against it:** the opposite sign of βJ_CW (P1), or, for an FM class, a positive βJ_CW that disappears under the within-agent permutation null N1 (spread carried entirely by agent fields, R1).

**HH22 vote tests (G26 only; chat-declared votes, structural labels, no text).**
- *States.* A vote declaration is an agent chat message in #26 containing a vote word that names ≥ 1 roster agent (`chat_mentions_clean.mentions_roster`).
  - The primary set is first-person declarations ("I vote / my vote / I approve …"); any vote-word message is the robustness variant.
  - A single named candidate is a categorical state. Several named candidates form an approval set, weighted 1/k per candidate.
  - Each voter's latest declaration is carried forward.
  - Candidates are the agents named in ≥ 1 first-person declaration; HH22 expects q = 6.
  - Runoff onset is the first 30-min window with ≥ 2 agent messages containing "runoff", a structural keyword timing.
- **P-G26a (symmetric point).** At runoff onset, the latest declarations put the top three candidates level: a multinomial equality test on their approval weight gives p > 0.05, and the perplexity of the declared distribution over the candidates is q_eff ≥ 3. Fails if one candidate already leads significantly.
- **P-G26b (first-order jump).** The eventual winner's declared share shows an O4 "jump" at or after runoff onset: Δ ≥ 0.3, τ ≤ 2 windows, rising from ≈ 1/3 to ≥ 0.75, with persistence ≤ 0.15. Fails if the rise is gradual (R3) or absent.
- **P-G26c (Potts mechanism, mean field).** Take the runoff snapshot (each voter's last single-candidate declaration after onset) under symmetric fields (HH22's symmetric point). The profile-likelihood βJ_snap of the Curie–Weiss Potts with q = q_runoff is ≥ βJ_s(q_runoff), i.e. the first-order region (βJ_s(3) = 2.75). If the runoff count vector is concentrated but βJ_snap < βJ_s, or symmetric fields are rejected, the step is field-driven (institutional), not a Potts transition.
- My credences: P-G26a 0.5; P-G26b 0.5; P-G26c 0.15. The runoff is a protocol change that narrows q from 6 to the tied set; that is a field, not spontaneous ordering.

## Result
| Test | Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- | --- |
| P1 βJ_CW (primary) | > 0 | +6.13 (jackknife SE 0.87, t = +7.03, t_crit 2.78) | βJ = 0; N1 (within-agent permutation) mean -1.09, z_N1 = +4.0 | **supported** |
| P2 βJ_PL (agent fields) | z ≥ +2 | +7.49; z_N2 = +6.44, z_N1d = +5.29, z_N1 = +4.99 | N2 (circular shift) mean +4.14 | **supported** |
| O3 agreement ratio R | – | 9.35 | 1 = interchangeable agents | descriptive |
| P3 consensus jump (project labels) | jump, Δ ≥ 0.3, τ ≤ 2, persistence ≤ 0.15; βJ_CW ≥ βJ_s(q_eff) | gradual (Δ = +0.18, τ = 0.03 win, persistence +0.50); q_eff = 4.7, βJ_s = 3.56, first-order region: yes | constant / linear fits | **failed** |
| P4 control: action-class βJ_CW | ≥ 0 or ≈ 0, any class | +1.27 (t = +2.81); action βJ_PL z_N2 = +3.97 | – | consistent |
| P5 held-out PL (coupled vs fields-only) | gain in ≥ 4/5 folds where abs(z_N2) ≥ 2 | 5/5 day folds improve | fields only | consistent |
| P6 plmDCA diagonal (secondary) | same sign as βJ_PL | z_N1 = +38.9 | N1 (9 draws) | agrees |
| P7 prior: abs(βJ) < 2 | – | βJ_CW +6.13; drift-corrected excess βJ_PL − N2 mean = +3.36 | – | fails (βJ_CW) |

**Robustness (O9; βJ_CW):** raw labels +5.54, q ≤ 4 +6.78, W = 15 min +5.93, W = 60 min +6.24, computer-use actions only (post hoc) +5.68, day fields +3.77.

**Post hoc** (added after the round-1 run, not pre-registered):
- z of βJ_PL vs a ±1-window local shift: +3.43. This tests alignment at the 30-min scale.
- Ownership index (share of agent-windows on projects one agent dominates): 0.17.
- Persistence P(same project next window): 0.61.

**HH22 vote tests (chat-declared votes; candidate codes only, no text):**
| Test | Prediction | Observed | Verdict |
| --- | --- | --- | --- |
| P-G26a symmetric point at runoff onset | top-3 level (p > 0.05), q_eff ≥ 3 | onset rule fired at window 2 (day 1). Top-3 approvals [8.0, 3.0, 2.0], χ² p = 0.09, q_eff = 3.66, 9 voters | passes the test as written (p > 0.05, q_eff ≥ 3) but is uninformative: the onset rule fired on a day-1 mention of a runoff, the test has little power, and the proxy does not reproduce the reported three-way tie |
| P-G26b runoff is a first-order jump | jump, Δ ≥ 0.3, τ ≤ 2, ≈ 1/3 → ≥ 0.75, persistence ≤ 0.15 | jump at window 27.2 of 36: 0.18 → 0.80 (Δ = 0.62, τ = 0.15 win, ΔBIC step vs linear 40), persistence 0.00 | **supported** (the pre-jump level is 0.18, below ≈ 1/3; any-vote-word variant: Δ = 0.48, end level 0.69) |
| P-G26c Potts mechanism (runoff snapshot, symmetric fields) | βJ_snap ≥ βJ_s(q) | counts [8, 1, 1] (q = 3); βJ_snap = 2.80 [0.65, 4.65] vs βJ_s = 2.75; P(max ≥ 8 under independent symmetric voters) = 0.010 | **at threshold, inconclusive** |

Winner (most single-candidate declarations, from structural codes) = agent 17, DeepSeek-V3.2, matching the dataset's goal summary. The declared-vote universe is 10 named agents, not 6: vote messages also name non-candidates, e.g. ballot organizers.

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 2 | z_N2 = +6.4; held-out gain 5/5 folds |
| D unfitted predictions | 1 | sign by goal mode: supported (not diagnostic on its own: βJ_CW > 0 in 11/14 tested weeks, whatever the mode); vote jump predicted and observed |
| G ground truth | 1 | vote winner and runoff jump match the dataset's goal summary |

## Notes
- 2026-10-03 (round 1): the project labels (mostly ballot Google Docs) are not the consensus variable. The declared votes are. The pre-registered runoff-onset rule (≥ 2 'runoff' messages in a window) fired on day 1, long before the decisive vote at window ≈ 27, so P-G26a measured an early state.

## Round 1b: per election round (native; DQ6 ballots)
*Design and predictions written 2026-10-04 07:15 UTC, before computing any of the statistics below.* DQ9 names #26 per election round as H11's (and H31's) mandatory native test: three vote events at known instants with known ballots.

**What I had seen:** the DQ6 tallies and ballot timestamps (approval 01-05: first ballot 19:25:09 UTC, recorded opening 19:26:03, close 19:30; 47 approvals by 9 voters, with Claude 3.7 Sonnet, Gemini 2.5 Pro and DeepSeek-V3.2 each approved by all 9; runoff: opening 19:32:19, 8 ballots 19:32:36 → 19:33:59, 7–1–0 for DeepSeek-V3.2; confirmatory 01-09: scheduled 18:45, 9 ballots 18:45:29 → 18:46:54, 9–0); H53's finding that 14/17 runoff and confirmatory ballots were cast by the call that read the round's opening message. I had not looked at any ballot's context (which earlier ballots or candidate mentions a voter had seen).

**States.** Ballot rows from `ground_truth_labels` (`label_kind = ballot`, preferred), by round (approval, runoff, confirmatory): voter, candidate, time. Codes only.

- **N26-a (symmetric point, approval round).** Ground truth, not a prediction: each of the three tied candidates was approved by all 9 voters, so the runoff starts from an exact symmetric point among q = 3 (x = 1/3 each). Round 1's P-G26a (chat proxy, onset on day 1) is replaced by this fact.
- **N26-b (runoff jump).** Also known from DQ6 before writing: the winner's share goes from 1/3 to 7/8 within ≈ 100 s (Δ ≈ 0.54, far inside one 30-min window) and is confirmed 9–0 four days later (persistence 0). Scored as a ground-truth check of P-G26b on the right election, not as a blind prediction.
- **N26-c (mean-field mechanism, per round).** Profile-likelihood βJ_snap of the symmetric-field Curie–Weiss Potts on each round's final ballots: runoff (7, 1, 0) with q = 3; confirmatory (9, 0) with q = 2.
  - Prediction: runoff βJ_snap MLE ≥ βJ_s(3) = 2.75, but the 95% profile interval includes βJ_s (inconclusive with N = 8). P(max ≥ 7 of 8 | independent symmetric voters) < 0.05 (my hand estimate before running: ≈ 0.008).
  - Confirmatory: unanimous, so the MLE sits at the grid bound and the test is uninformative by construction; P(9 of 9 | independent symmetric, q = 2) ≈ 0.004.
- **N26-d (coupling needs visibility: ballots vs a pre-set field).** Potts coupling acts through what voters see. For each runoff and confirmatory ballot, find the voter's call that cast it (`call_windows`, talk call containing the ballot message) and count the same round's earlier ballots that had entered the voter's context by that call (`context_ledger_items`). Also count, in the voter's context between the approval tally and the ballot call, the messages naming each runoff candidate (`chat_mentions_clean.mentions_roster`): the visible "field".
  - Prediction: ≥ 5 of 8 runoff ballots are cast having seen ≤ 1 earlier runoff ballot, and DeepSeek-V3.2's share among ballots cast with no earlier ballot visible is ≥ 0.6. So the runoff consensus does not need ballot-to-ballot coupling: it was set before the runoff opened.
  - Prediction: DeepSeek-V3.2 leads the visible candidate mentions (ties count as not leading) for ≥ 5 of 8 runoff voters.
  - **Coupling reading** (counts against my prediction): DeepSeek's share rises with the number of earlier DeepSeek ballots seen, and voters who saw none split near 1/3.

### Result (round 1b, run 2026-10-04)
`analysis/round1b.py g26` → `data/processed/H11-potts-labor-vs-herding/r1b/g26_rounds_r1b.json`. Ballot-to-call matching: the voter's talk call whose logged span contains the ballot message (`call_windows`); visibility: items received by that call or earlier (`context_ledger_items`).

| Test | Prediction | Observed | Verdict |
| --- | --- | --- | --- |
| N26-a symmetric point (approval) | ground truth | 9/9 voters approved all three tied candidates (0, 6, 17); approvals {17: 9, 0: 9, 6: 9, 16: 7, 12: 7, 15: 4, 13: 2} | exact symmetric start (fact, not a test) |
| N26-b runoff jump | ground truth check | winner's share 1/3 → 7/8 (Δ = 0.54) over 83 s (first ballot 17 s after the opening); 9/9 on 01-09 | **holds on the correct election** (round 1's 0.18 → 0.80 was the 01-09 vote) |
| N26-c coupling, runoff (7, 1, 0), q = 3 | MLE ≥ 2.75, CI includes it; P(indep) < 0.05 | βJ_snap 3.2 [1.05, 6.0]; P(≥ 7 of 8 \| independent symmetric) = 0.008 | **as predicted: inconclusive mechanism, independence rejected** |
| N26-c confirmatory (9, 0), q = 2 | at bound, uninformative | MLE at the bound (CI [1.85, ∞)); P = 0.004 | as predicted |
| N26-d earlier ballots seen | ≥ 5/8 runoff ballots with ≤ 1 seen | 3/8 (seen: 0, 1, 1, 2, 3, 4, 4, 6; mean 2.6) | **failed** |
| N26-d winner share, nothing seen | ≥ 0.6 | 1/1 (only the first ballot was cast blind) | met, n = 1 |
| N26-d visible mention field | DeepSeek leads for ≥ 5/8 voters | 0/8. From the first approval ballot on, Gemini 2.5 Pro led the visible candidate mentions for 7/8 runoff voters (Claude 3.7 Sonnet for the first); in the 16-s window from the tally on, mentions were tied or led by Gemini | **failed** |

**Reading.** The runoff was not decided by a field visible in chat before it opened: the mention field favoured Gemini 2.5 Pro, yet DeepSeek-V3.2 won 7–1. The first ballot came from one of the three candidates (Claude 3.7 Sonnet), for a rival (DeepSeek-V3.2); the next voter, having seen that one ballot, voted for Gemini 2.5 Pro; then Gemini 2.5 Pro itself, having seen one DeepSeek ballot, voted for DeepSeek, and every later voter, having seen 2–6 earlier ballots, did the same. That is the order of a ballot cascade (sequential, visible, majority-following), which is the Potts-coupling reading, with a courtesy twist (2 of 3 candidates voted for a rival). n = 8 cannot tell a cascade from a shared norm ("vote for the proposer of the runoff"); text would be needed and is out of scope. The confirmatory vote is the clean field case: 6/9 ballots were cast before any earlier ballot was visible, all for the incumbent.

**Scorecard (round 1b, native):** D 1 (jump holds on the correct election; mechanism inconclusive); G 1 (DQ6 tallies are the ground truth); B (update-order audit) partial: ballots are cast by calls that read 0–6 earlier ballots.
