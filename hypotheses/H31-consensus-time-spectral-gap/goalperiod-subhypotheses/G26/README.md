# H31 × G26: Elect a village leader. They choose this week’s goal! (2026-01-05 → 2026-01-12)

**Verdict:** failed
**Verdict (1b):** supported (native: votes settle in 57 s / 39 s)
**Role:** native (round 1b: E-V per election round on DQ6 ballots; round 1: exploratory card candidate, E-P + E-C)
**Period:** regime I · mode C · 10 agents · #general · 5 non-holdout days (15.8 active h).

## Why this period
Named by HH115 and H11 as a consensus period. H11 project labels are dense enough for E-P (≥ 50% of room-windows have ≥ 3 labeled agents).

**Predictors** (whole block-period; computed before any outcome):

| Block | N_b | msgs/h | u (reads/h) | λ₂^w,sym (1/h) | λ₂^w,dir | u·λ₂^rw | γ_tr | τ_wave (min) | τ_Vsim (h) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| #general | 10 | 133 | 53.0 | 89.10 | 131.56 | 54.8 | 14.81 | 1.0 | 0.044 |

## Prediction
*Written 2026-10-03, before running on this period.*

- **Card rules apply unchanged** (E-P, E-V, E-C definitions; tests T1–T7). Per-period verdicts are descriptive; the scaling test (P1, P5) is cross-period.
- **H31 (model D):** if this block's events are uncensored, their τ should sit on the cross-period line τ = c/λ₂^w,sym. Blocks with a larger λ₂^w,sym should be faster.
- **My prior (card):** the timing is set by task structure and announcements, so this period's τ will not track λ₂ beyond noise. E-P rises will be mostly abrupt (ρ ≤ 1 window), and E-C, if present, will be a convergence over days (τ_C 2–15 h).
- **Period-specific:** Election week. E-P project events should be gradual or absent (H11: project labels gradual). **E-V:** the runoff consensus should come within ≤ 1 h of the first runoff message (P10), faster than the E-P-calibrated M_λ forecast. That would make it a decision field, not diffusion.
- **Counts against H31 here:** uncensored events whose τ is far off the calibrated line (outside the 80% LOPO interval), or a room contrast with the opposite sign to D.

## Result
| Block | E-P projects | consensus (frozen at start / instant / uncensored) | τ_P (h), uncensored | rise (windows) | kick-locked | M_λ forecast (h) | M0 forecast (h) | E-C kind | E-C τ (h) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| #general | 8 | 7 (1 / 6 / 0) | – | – | 2/7 | – | – | none | – |
- **E-V (runoff):** onset at 0.0 active h. The winner's declared share reached ≥ 0.5 (≥ 3 declared) after τ_V = 12.55 h. The M_λ forecast was 1.22 h (80%: 0.19–5.36). Before the runoff, the top candidate's declared share was 1.00 (n = 1).
- **E-V post hoc:** the pre-registered onset (first runoff-word message) fired at the period start, as H11's onset rule did. The winner's share rose from 0.22 to ≥ 0.5 within 0.76 h (last window below 0.25 → first ≥ 0.5): an abrupt decision step.
- No uncensored E-P event: 1 frozen at the period start (kick-locked by construction) and 6 *instant* (criterion met in the onset window mid-period: a one-window herding wave). By the card's rule both are left-censored, so there is no τ to test.

Data: `data/processed/H31-consensus-time-spectral-gap/G26/`, `events_ep_w30.parquet`, `events_ec.parquet`.

## Scorecard (period-specific axes)
- **C (period level):** the per-event leave-one-period-out comparison of M_λ (or M_tr) vs the constant is listed above.
- **G:** the #26 runoff winner matches the dataset's summary (DeepSeek-V3.2).

## Notes
- 2026-10-03: folder and prediction written before the real-data run on this period.
- 2026-10-03: results filled from `analysis/explore.py` (round 1).

## Round 1b: consensus time per election round (native; DQ6 ballots)
*Design and predictions written 2026-10-04 07:24 UTC, before computing any per-round statistic.* DQ9: #26 offers three consensus events with exact instants (approval tie, runoff, confirmatory vote), the only consensus times in the village with ground truth.

**What I had seen:** the DQ6 phase and ballot times (listed in the card's round-1b section); H53's finding that 14/17 runoff and confirmatory ballots came from the call that read the round's opening message, and that the approval round's recorded opening (19:26:03) postdates 6/9 ballots (first ballot 19:25:09). I had not computed read-out times, M_λ forecasts on the new data, or any τ_V.

**Definitions (fixed now).** Per round r: onset t₀ = the round's opening (runoff: the phase message, 19:32:19; confirmatory: the scheduled opening, 18:45:00; approval: the first ballot, 19:25:09, since the recorded opening comes later). Ballots are carried to the end of the round. Consensus t_c = the first ballot after which one candidate holds ≥ 50% of ballots cast so far with ≥ 3 ballots (the card's E-V rule, on ballots). τ_V = t_c − t₀ in active hours. The approval round has approval sets, so a candidate's share is its approvals / ballots; a tie at the close is right-censored. Read-out: τ_read(k) = time from t₀ until the k-th roster agent's first receiving call that has the opening message in context (`context_ledger_items`; approval: the first ballot message).

- **V26-a (approval):** no consensus (the three leaders end level): right-censored at the 19:30 close.
- **V26-b (runoff) and V26-c (confirmatory):** τ_V ≤ 0.05 h (3 min) after the opening, below the lower end of the round-1b M_λ 80% interval for the #26 block (P10 per round: supported).
- **V26-d (the clock that sets τ_V):** model H (herding wave = read-out of the announcement) predicts τ_V ≈ τ_read(3), the time for the third agent to read the opening, since consensus needs 3 ballots. Prediction: τ_V / τ_read(3) ∈ [0.5, 2] in both decided rounds. Model D's diffusion time 1/λ₂ (hours) misses by ≥ 1 order of magnitude.
- **What would count against:** τ_V of tens of minutes or more, or consensus forming only after many voters had read several ballots (a gradual, diffusive approach).

### Result (round 1b, run 2026-10-04)
`analysis/ev26_dq6.py` (via `explore.py` with `H31_EV26=dq6`) → `data/processed/H31-consensus-time-spectral-gap/r1b/ev26.json`. Read-out from `context_ledger_items` (first receiving call of each roster agent with the opening message in context).

| Round | Onset t₀ (UTC) | Ballots | Consensus | τ_V | τ_read(1/3/5) | τ_V / τ_read(3) |
| --- | --- | --- | --- | --- | --- | --- |
| Approval (01-05) | 19:25:09 (first ballot) | 9 voters, approval sets | none: 9–9–9 tie of three leaders at the close | right-censored | 0.3 / 9.5 / 15.3 s | – |
| Runoff (01-05) | 19:32:19 (opening message) | 8; 7–1–0 | after the third ballot (2 of 3 for DeepSeek-V3.2) | **57 s** (0.016 h) | 5.5 / 33.1 / 47.8 s | **1.7** |
| Confirmatory (01-09) | 18:45:00 (scheduled) | 9; 9–0 | after the third ballot | **39 s** (0.011 h) | 10.9 / 13.4 / 20.1 s | **2.9** |

Round-1b M_λ forecast for the #26 block (fitted on all E-P gradual events): 1.14 h, 80% interval 0.22–5.2 h.

| Test | Prediction | Observed | Verdict |
| --- | --- | --- | --- |
| V26-a approval | censored (tie) | tie of three leaders at the close | **supported** |
| V26-b runoff | τ_V ≤ 0.05 h, below the M_λ interval | 0.016 h; interval starts at 0.22 h | **supported** |
| V26-c confirmatory | same | 0.011 h | **supported** |
| V26-d read-out clock | τ_V / τ_read(3) in [0.5, 2] in both rounds | 1.7 (runoff), 2.9 (confirmatory) | **partly** (1 of 2) |

**Reading.** Deadline-bound votes reach consensus at the speed of read-out: tens of seconds, set by how fast the opening message reaches the third reader plus one reply cycle, not by the exposure graph's spectral gap (whose forecast is 70–100× too slow). The confirmatory round's ratio is higher because its scheduled opening preceded the actual call-to-vote message (posted 18:45:10) and agents read in a tight cluster at 11–20 s, then took one more call to vote. The round-1 E-V (12.5 h, keyword onset on day 1, consensus on 01-09) is superseded.

**Scorecard (round 1b, native):** G 2 for E-V (ground-truth instants and ballots); D 1 (the herding-wave/read-out model's timescale predicted, the λ₂ law's not).
