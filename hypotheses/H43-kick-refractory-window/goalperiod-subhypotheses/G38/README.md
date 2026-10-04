# H43 × G38: Choose a charity and raise money (2026-04-02 → 2026-04-24)

**Verdict:** descriptive
**Role:** native (also carries the replication-layer row)
**Period:** regime III · mode C · 12–14 agents · #best / #rest · 17 non-holdout days · units 38a–38e (NE17 approval system 04-14, NE18 04-20, two roster joins).

## Why this period
In regime III an agent reads chat only when its own PAUSE timer expires (DQ1: wakes are at the timer in 99.8% of cases), so every kick read while idle is read at a *gate*. Two consequences make G38 the cleanest refractory test for idle agents:
- **Batched dose:** two kicks that arrive during one pause are read together at the same gate. H16 found a directed kick at a gate raises the escape odds ×2.9; the marginal effect of a second kick in the same read is the δ = 0 limit.
- **Re-kicks at a later gate:** a directed kick (class D: nudge, named human message or @-mention; 2,600 directed receiving calls in G38) read at a gate after an earlier effective directed kick, whose launched episode has ended (A3: an agent at a gate is idle, so its episode is over), against fresh gates (no directed kick in the previous 30 min). This asks whether refractoriness outlasts the episode, i.e. the R-time vs R-episode contrast at the read-out point.
G38 is the longest four-hour regime-III period, with the most gates (1,600 pause gates in H16).

## Prediction
*Written 2026-10-04, before running on this period (card P8, as operationalized in A3).*
- **P8a:** directed kicks at gates after an effective directed primer whose episode has ended (status `post`, δ ≤ 120 min) have R ≤ 0.5 against fresh gates (E1 > 0 required). Under R-episode (H43's claim) this R should instead be ≈ 1; the prediction as written (R ≤ 0.5) is the R-time reading. **Pre-stated interpretation:** R_post ≈ 1 supports episode-locked refractoriness; R_post ≤ 0.5 supports a clock that outlasts the episode.
- **P8b:** a second directed kick read at the same gate (batched, dose ≥ 2 vs 1) adds ≤ 0.3 × E1.
- **Replication row (templated):** as for every period (see the card).
- **Power:** H16's kicked gates by dose were [133, 23, 8], so P8a rests on a few dozen re-kicked gates; expect wide intervals.

## Result
Run 2026-10-04 with `analysis/run_native.py --test G38` and `analysis/run_period.py --period G38` (B = 300); numbers in `data/processed/H43-kick-refractory-window/native/G38.json` and `G38/results.json`.

**Native (P8), directed kicks at gates (class D):** 2,581 directed receiving calls, 369 primers (101 idle at read), 301 second kicks.
- In G38 nearly every idle-at-read call escapes within 15 min (F_ctrl ≈ 0.95), so only hazard speed-up is informative.
- Only 49% of idle-at-read calls follow a PAUSE; the rest follow ≥ 180-s gaps (long tool calls).

| Prediction | Observed | Verdict |
| --- | --- | --- |
| P8a re-kick after an ended episode: R ≤ 0.5 vs fresh gates | E1 at fresh gates = 0.28 [−0.12, 0.66] (O1; n.s.). Only **8** re-kicked gates after an ended episode (R 0.18 [−13.7, 39.1]). O1a: E1 = 0.15 [0.04, 0.23], R = 0.66 [0.00, 4.68] | **untestable** (no first-kick effect; 8 cases) |
| P8b batched dose 2+ adds ≤ 0.3 × E1 | 12 batched gates; uninformative | **untestable** |

Nudges alone at gates have E1 = 1.04 [0.60, 1.63] (O1, 23 primers; H16's directed gate effect), but only 6–8 second nudges. Mentions dominate class D and have no gate effect (E1 = 0.06).

**Replication row (templated, 30-min quiet rule):**

| Class | outcome | primers / second kicks | E1 (lnHR) | R (0–15 min] | R (15–60] | R (60–240] | δ½ (min) vs L̃ | test |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| N | O1 | 23 / 8 | 1.04 [0.65, 1.46] | – | 0.61 [0.16, 2.08] | – | – vs L̃ 9 | underpowered |
| H | O2 | 13 / 9 | 0.58 [−0.00, 0.85] | 0.69 [−3.45, 7.86] | – | – | – vs L̃ 72 | underpowered |
| A | O2 | 249 / 210 | 0.34 [0.04, 0.62] | 1.80 [0.46, 13.69] | 1.65 [−1.15, 9.69] | 0.19 [−5.58, 3.23] | 0.0 [0.0, 7.9] vs L̃ 28 | fail (no window) |

Verdict: **descriptive**. The native test is untestable at G38's size (the synthetic validation already found nothing resolvable at G38 scale). The replication row shows no mention window (R(0–15) ≥ 1).
